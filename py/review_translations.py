"""
Dota2 API 翻译审核与自动修复脚本 (增强版)
- 使用AI检查翻译是否符合Dota2术语
- 自动修复不准确的翻译
- 分批处理大文件
- 断点续传支持
- 详细进度追踪
- 成功/失败记录分别保存
- 支持长时间无人值守运行
- 自动重试机制
"""
import json
import os
import sys
import time
import random
import logging
import threading
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# 添加当前目录到 path
sys.path.insert(0, os.path.dirname(__file__))

import urllib.request
import urllib.error

# ==================== 配置 ====================

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"

# 需要审核的文件列表（减小批次大小避免超出API限制）
REVIEW_FILES = [
    {
        "path": "gameevents/events_cn.json",
        "type": "game_event",
        "item_key": "items",
        "batch_size": 8,  # 有parameters嵌套，减小批次
    },
    {
        "path": "luaapi/classes_cn.json",
        "type": "class",
        "item_key": "items",
        "batch_size": 2,  # 类有很多methods，必须很小
    },
    {
        "path": "luaapi/functions_cn.json",
        "type": "function",
        "item_key": "items",
        "batch_size": 5,  # 有parameters嵌套
    },
    {
        "path": "luaapi/enums_cn.json",
        "type": "enum",
        "item_key": "items",
        "batch_size": 3,  # 有members嵌套
    },
    {
        "path": "luaapi/constants.json",
        "type": "constant",
        "item_key": "items",
        "batch_size": 10,  # 简单结构，可以大一点
    },
    {
        "path": "panoramaapi/enums.json",
        "type": "panorama_enum",
        "item_key": "items",
        "batch_size": 3,  # 有members嵌套
    },
    {
        "path": "panoramaevents/events.json",
        "type": "panorama_event",
        "item_key": "items",
        "batch_size": 8,  # 有parameters嵌套
    },
]

# 进度文件
PROGRESS_FILE = Path(__file__).parent.parent / "review_progress.json"

# 成功记录文件
SUCCESS_FILE = Path(__file__).parent.parent / "review_success.json"

# 失败记录文件
FAILED_FILE = Path(__file__).parent.parent / "review_failed.json"

# 日志文件
LOG_FILE = Path(__file__).parent.parent / "review.log"

# API 配置
API_BASE_URL = "https://siliconflow-manager.ypyt147.workers.dev/v1"
API_KEY = "apikeyliam"
MODEL = "zai-org/GLM-4.6"

# 重试配置
MAX_RETRIES = 3  # 单个批次最大重试次数
RETRY_DELAY = 5  # 重试延迟（秒）
MAX_CONSECUTIVE_FAILURES = 10  # 连续失败多少次后暂停

# 线程锁
progress_lock = threading.Lock()
log_lock = threading.Lock()
success_lock = threading.Lock()
failed_lock = threading.Lock()

# ==================== 日志配置 ====================

logger = logging.getLogger("review")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(message)s',
    datefmt='%H:%M:%S'
))

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log(msg, level="info"):
    """统一日志输出"""
    with log_lock:
        if level == "debug":
            logger.debug(msg)
        elif level == "warning":
            logger.warning(msg)
        elif level == "error":
            logger.error(msg)
        else:
            logger.info(msg)


# ==================== Dota2 术语对照表 ====================

DOTA2_TERMINOLOGY = """
## Dota2 专业术语对照表

### 常见错误翻译 → 正确翻译
| 错误 | 正确 | 备注 |
|------|------|------|
| 溅射 | 分裂攻击 | Cleave的官方译名 |
| 思考者 | Thinker实体 | 保留英文专业术语 |
| 修改器 | Modifier/效果 | 技术术语，可保留英文 |
| 中立物品等级 | 中立物品品阶 | 官方用语是"品阶" |
| 中立生物 | 野怪 | 玩家习惯用语 |
| 播报员 | 播音员 | 统一用语 |
| 矢量 | 向量 | 统一数学术语 |
| Roshan | 肉山 | 玩家常用称呼 |

### 游戏机制术语
| 英文 | 中文 |
|------|------|
| Cleave | 分裂攻击 |
| Critical Strike | 暴击 |
| Bash | 重击 |
| Lifesteal | 吸血 |
| Spell Immunity | 技能免疫 |
| Magic Resistance | 魔法抗性 |
| Evasion | 闪避 |
| True Strike | 必中 |
| Break | 破坏 |
| Dispel | 驱散 |
| Purge | 净化 |
| Silence | 沉默 |
| Stun | 眩晕 |
| Root | 缠绕/禁锢 |
| Hex | 妖术 |

### 游戏对象术语
| 英文 | 中文 |
|------|------|
| Hero | 英雄 |
| Creep | 小兵 |
| Neutral Creep | 野怪 |
| Ancient Creep | 远古野怪 |
| Roshan | 肉山 |
| Tower | 防御塔 |
| Barracks | 兵营 |
| Ancient | 遗迹 |
| Fountain | 泉水 |
| Outpost | 前哨 |
| Ward | 眼/守卫 |
| Courier | 信使 |
| Illusion | 幻象 |
| Summon | 召唤物 |

### 保留英文的术语
- Thinker（Thinker实体）
- Modifier（Modifier/效果）
- NPC（NPC单位）
- Vector（向量）
- Handle（句柄）
- Quaternion（四元数）
"""


# ==================== 进度管理 ====================

def load_progress() -> dict:
    """加载进度"""
    with progress_lock:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "started_at": datetime.now().isoformat(),
            "files": {},
            "stats": {
                "total_items_reviewed": 0,
                "total_issues_found": 0,
                "total_issues_fixed": 0,
            }
        }


def save_progress(progress: dict):
    """保存进度"""
    progress["updated_at"] = datetime.now().isoformat()
    with progress_lock:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)


def get_file_progress(progress: dict, file_path: str) -> dict:
    """获取单个文件的进度"""
    if file_path not in progress["files"]:
        progress["files"][file_path] = {
            "status": "pending",
            "current_batch": 0,
            "total_batches": 0,
            "items_reviewed": 0,
            "issues_found": 0,
            "issues_fixed": 0,
            "modifications": [],
        }
    return progress["files"][file_path]


# ==================== API 调用 ====================

def call_ai_api(messages: List[dict], timeout: int = 120) -> Optional[str]:
    """
    调用AI API
    Returns: 响应内容或None（失败时）
    """
    url = f"{API_BASE_URL}/chat/completions"
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 4096,
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                log(f"   ⚠️ API响应格式异常: {str(result)[:100]}", "warning")
                return None
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ""
        log(f"   ❌ API HTTP错误 {e.code}: {error_body[:200]}", "error")
        return None
    except urllib.error.URLError as e:
        log(f"   ❌ API连接错误: {e.reason}", "error")
        return None
    except Exception as e:
        log(f"   ❌ API调用异常: {e}", "error")
        return None


# ==================== 成功/失败记录管理 ====================

def load_success_records() -> dict:
    """加载成功记录"""
    with success_lock:
        if SUCCESS_FILE.exists():
            try:
                with open(SUCCESS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "updated_at": datetime.now().isoformat(),
            "total_fixed": 0,
            "records": []
        }


def save_success_records(records: dict):
    """保存成功记录"""
    records["updated_at"] = datetime.now().isoformat()
    with success_lock:
        with open(SUCCESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)


def add_success_record(file_path: str, item_name: str, field: str, 
                       original: str, corrected: str, reason: str):
    """添加一条成功修复记录"""
    records = load_success_records()
    records["total_fixed"] += 1
    records["records"].append({
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "item": item_name,
        "field": field,
        "original": original[:200] if original else "",  # 限制长度
        "corrected": corrected[:200] if corrected else "",
        "reason": reason
    })
    save_success_records(records)
    log(f"  📝 成功记录已保存: {item_name}.{field}")


def load_failed_records() -> dict:
    """加载失败记录"""
    with failed_lock:
        if FAILED_FILE.exists():
            try:
                with open(FAILED_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "updated_at": datetime.now().isoformat(),
            "total_failed": 0,
            "records": []
        }


def save_failed_records(records: dict):
    """保存失败记录"""
    records["updated_at"] = datetime.now().isoformat()
    with failed_lock:
        with open(FAILED_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)


def add_failed_record(file_path: str, batch_idx: int, items: List[dict], 
                      error_type: str, error_msg: str):
    """添加一条失败记录"""
    records = load_failed_records()
    records["total_failed"] += 1
    
    # 提取条目名称
    item_names = [item.get("name", item.get("eventName", "unknown")) for item in items[:5]]
    if len(items) > 5:
        item_names.append(f"...及其他{len(items)-5}个")
    
    records["records"].append({
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "batch_idx": batch_idx,
        "items": item_names,
        "error_type": error_type,
        "error_msg": str(error_msg)[:500],  # 限制长度
        "retry_count": 0
    })
    save_failed_records(records)
    log(f"  📝 失败记录已保存: {file_path} 批次{batch_idx}")


def mark_failed_as_retried(file_path: str, batch_idx: int):
    """标记失败记录为已重试"""
    records = load_failed_records()
    for record in records["records"]:
        if record["file"] == file_path and record["batch_idx"] == batch_idx:
            record["retry_count"] = record.get("retry_count", 0) + 1
            record["last_retry"] = datetime.now().isoformat()
    save_failed_records(records)


# ==================== AI 审核 Prompt ====================

def extract_translations(item: dict, item_type: str) -> dict:
    """
    提取一个条目的所有翻译字段（包括嵌套）
    返回扁平化的结构，便于AI审核
    
    完整字段列表:
    - 顶层: name_cn, description_cn, common_usage_cn, returnType_cn, 
            returnDescription_cn, notes_cn, warnings_cn, usage_cn
    - parameters[]: description_cn, type_description_cn
    - members[]: description_cn, methodName_cn
    - methods[]: name_cn, description_cn, returnType_cn, returnDescription_cn,
                 notes_cn, warnings_cn, common_usage_cn
    - methods[].parameters[]: description_cn, type_description_cn
    """
    name = item.get("name", item.get("eventName", "unknown"))
    result = {"_name": name}  # 用于标识
    
    # 顶层翻译字段（完整列表）
    top_fields = [
        "name_cn", "description_cn", "common_usage_cn", 
        "returnType_cn", "returnDescription_cn", 
        "notes_cn", "warnings_cn", "usage_cn"
    ]
    for field in top_fields:
        if field in item and item[field]:
            # 限制长度避免超出API限制
            val = item[field]
            result[field] = val[:150] if len(val) > 150 else val
    
    # 提取 parameters 嵌套翻译（限制数量）
    params = item.get("parameters", [])[:4]  # 最多4个参数
    if params:
        params_cn = []
        for p in params:
            p_info = {"name": p.get("name", "")}
            if p.get("description_cn"):
                p_info["description_cn"] = p["description_cn"][:80]
            if p.get("type_description_cn"):
                p_info["type_description_cn"] = p["type_description_cn"][:50]
            if len(p_info) > 1:
                params_cn.append(p_info)
        if params_cn:
            result["parameters"] = params_cn
    
    # 提取 members 嵌套翻译（枚举类型）
    if item_type in ["enum", "panorama_enum"]:
        members = item.get("members", [])[:6]  # 最多6个成员
        if members:
            members_cn = []
            for m in members:
                m_info = {"name": m.get("name", "")}
                if m.get("description_cn"):
                    m_info["description_cn"] = m["description_cn"][:80]
                # panoramaapi特有的 methodName_cn
                if m.get("methodName_cn"):
                    m_info["methodName_cn"] = m["methodName_cn"]
                if len(m_info) > 1:
                    members_cn.append(m_info)
            if members_cn:
                result["members"] = members_cn
    
    # 提取 methods 嵌套翻译（类类型）- 完整字段
    if item_type == "class":
        methods = item.get("methods", [])[:2]  # 最多2个方法（方法内容多）
        if methods:
            methods_cn = []
            for m in methods:
                m_info = {"name": m.get("name", "")}
                
                # 方法的所有翻译字段（完整列表！）
                method_fields = [
                    "name_cn", "description_cn", "returnType_cn", 
                    "returnDescription_cn", "common_usage_cn",
                    "notes_cn", "warnings_cn"  # 补充遗漏的字段
                ]
                for mf in method_fields:
                    if m.get(mf):
                        val = m[mf]
                        m_info[mf] = val[:80] if len(val) > 80 else val
                
                # 方法的参数翻译（最多2个）
                m_params = m.get("parameters", [])[:2]
                if m_params:
                    m_params_cn = []
                    for mp in m_params:
                        mp_info = {"name": mp.get("name", "")}
                        if mp.get("description_cn"):
                            mp_info["description_cn"] = mp["description_cn"][:60]
                        if mp.get("type_description_cn"):
                            mp_info["type_description_cn"] = mp["type_description_cn"][:40]
                        if len(mp_info) > 1:
                            m_params_cn.append(mp_info)
                    if m_params_cn:
                        m_info["parameters"] = m_params_cn
                
                if len(m_info) > 1:
                    methods_cn.append(m_info)
            if methods_cn:
                result["methods"] = methods_cn
    
    return result


def get_review_prompt(items: List[dict], item_type: str) -> str:
    """生成审核 prompt"""
    
    # 提取所有翻译字段（包括嵌套）
    items_to_review = []
    for item in items:
        extracted = extract_translations(item, item_type)
        items_to_review.append(extracted)
    
    prompt = f"""你是Dota2 Mod开发文档翻译审核专家。

## 任务
检查以下API文档的中文翻译是否准确、是否符合Dota2术语。

## ⚠️ 规则
1. 只能修正 `_cn` 结尾的字段
2. 不能修改 `_name`、`name` 等非翻译字段
3. 只报告有问题的，正确的不报告

{DOTA2_TERMINOLOGY}

## 待检查内容

```json
{json.dumps(items_to_review, ensure_ascii=False, indent=2)}
```

## 检查要点
- 术语是否正确（Cleave=分裂攻击，不是溅射）
- 是否直译（要符合游戏语境）
- name_cn是否表达了功能含义

## 返回格式

顶层字段问题：
`{{"name": "函数名", "field": "name_cn", "original": "原", "corrected": "修", "reason": "因"}}`

一级嵌套（parameters/members/methods）：
`{{"name": "函数名", "nested": "parameters", "nested_name": "参数名", "field": "description_cn", "original": "原", "corrected": "修", "reason": "因"}}`

二级嵌套（methods内的parameters）：
`{{"name": "类名", "nested": "methods", "nested_name": "方法名", "nested2": "parameters", "nested2_name": "参数名", "field": "description_cn", "original": "原", "corrected": "修", "reason": "因"}}`

完整返回：`{{"issues": [...], "summary": "总结"}}`
无问题：`{{"issues": [], "summary": "OK"}}`

只返回JSON。
"""
    return prompt


def parse_review_response(response: str) -> dict:
    """解析AI返回的审核结果"""
    import re
    
    response = response.strip()
    
    # 移除markdown代码块
    if response.startswith('```'):
        response = re.sub(r'^```(?:json)?\s*', '', response)
        response = re.sub(r'\s*```$', '', response)
    
    # 找到JSON开始
    start = response.find('{')
    if start == -1:
        return {"issues": [], "summary": "无法解析响应"}
    
    json_str = response[start:]
    
    # 尝试找到完整的JSON
    brace_count = 0
    end = 0
    for i, c in enumerate(json_str):
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if brace_count == 0:
                end = i + 1
                break
    
    if end > 0:
        json_str = json_str[:end]
    
    try:
        return json.loads(json_str)
    except:
        return {"issues": [], "summary": "JSON解析失败"}


# ==================== 修复逻辑 ====================

# 允许修改的字段白名单（只能修改翻译相关的 _cn 字段）
ALLOWED_FIELDS = {
    "name_cn",
    "description_cn", 
    "common_usage_cn",
    "returnType_cn",
    "returnDescription_cn",
    "notes_cn",
    "warnings_cn",
    "usage_cn",
    "type_description_cn",
    "methodName_cn",  # panorama enums
}

# 允许的嵌套类型
ALLOWED_NESTED = {"parameters", "members", "methods"}


def apply_fixes(data: dict, item_key: str, issues: List[dict], file_path: str) -> Tuple[int, List[str]]:
    """
    应用修复到数据中，并记录成功修复
    ⚠️ 安全机制：
    1. 只修改白名单内的 _cn 字段
    2. 只修改已存在的字段
    3. 不会添加新字段
    4. 不会删除任何字段
    5. 不会修改非翻译字段
    6. 支持嵌套字段修改（parameters/members/methods）
    Returns: (修复数量, 修复描述列表)
    """
    fixed_count = 0
    modifications = []
    
    items = data.get(item_key, [])
    
    # 建立名称到索引的映射
    name_to_index = {}
    for i, item in enumerate(items):
        name = item.get("name", item.get("eventName", ""))
        if name:
            name_to_index[name] = i
    
    for issue in issues:
        name = issue.get("name")
        field = issue.get("field")
        corrected = issue.get("corrected")
        original = issue.get("original", "")
        reason = issue.get("reason", "")
        nested = issue.get("nested")  # 嵌套类型：parameters/members/methods
        nested_name = issue.get("nested_name")  # 嵌套项名称
        
        # 安全检查1: 名称必须存在
        if name not in name_to_index:
            log(f"  ⚠️ 跳过: 找不到 {name}", "warning")
            continue
        
        # 安全检查2: 字段必须在白名单内
        if field not in ALLOWED_FIELDS:
            log(f"  ⚠️ 跳过: {field} 不在允许修改的字段列表内", "warning")
            continue
        
        idx = name_to_index[name]
        item = items[idx]
        
        # 安全检查3: 新值不能为空
        if not corrected or not corrected.strip():
            log(f"  ⚠️ 跳过: 修正值为空", "warning")
            continue
        
        # 处理嵌套字段
        nested2 = issue.get("nested2")  # 二级嵌套类型
        nested2_name = issue.get("nested2_name")  # 二级嵌套项名称
        
        if nested and nested_name:
            # 安全检查：嵌套类型必须在允许列表内
            if nested not in ALLOWED_NESTED:
                log(f"  ⚠️ 跳过: 不允许的嵌套类型 {nested}", "warning")
                continue
            
            nested_list = item.get(nested, [])
            if not nested_list:
                log(f"  ⚠️ 跳过: {name} 没有 {nested}", "warning")
                continue
            
            # 查找一级嵌套项
            target = None
            for nested_item in nested_list:
                if nested_item.get("name") == nested_name:
                    target = nested_item
                    break
            
            if not target:
                log(f"  ⚠️ 跳过: 找不到 {name}.{nested}.{nested_name}", "warning")
                continue
            
            # 处理二级嵌套（如 methods[].parameters[]）
            if nested2 and nested2_name:
                if nested2 not in ALLOWED_NESTED:
                    log(f"  ⚠️ 跳过: 不允许的二级嵌套类型 {nested2}", "warning")
                    continue
                
                nested2_list = target.get(nested2, [])
                if not nested2_list:
                    log(f"  ⚠️ 跳过: {name}.{nested}.{nested_name} 没有 {nested2}", "warning")
                    continue
                
                # 查找二级嵌套项
                target2 = None
                for n2_item in nested2_list:
                    if n2_item.get("name") == nested2_name:
                        target2 = n2_item
                        break
                
                if not target2:
                    log(f"  ⚠️ 跳过: 找不到二级嵌套 {nested2_name}", "warning")
                    continue
                
                if field not in target2:
                    log(f"  ⚠️ 跳过: 二级嵌套没有 {field}", "warning")
                    continue
                
                old_value = target2.get(field, "")
                if old_value == corrected:
                    continue
                
                # 执行二级嵌套修改
                target2[field] = corrected
                fixed_count += 1
                
                path = f"{name}.{nested}[{nested_name}].{nested2}[{nested2_name}].{field}"
                old_display = old_value[:20] + "..." if len(old_value) > 20 else old_value
                new_display = corrected[:20] + "..." if len(corrected) > 20 else corrected
                modifications.append(f"{path}: '{old_display}' → '{new_display}'")
                log(f"  ✏️ 修复二级嵌套: {path}")
                
                add_success_record(file_path=file_path, item_name=path, field=field,
                                   original=old_value or original, corrected=corrected, reason=reason)
                continue
            
            # 一级嵌套修改
            if field not in target:
                log(f"  ⚠️ 跳过: {name}.{nested}.{nested_name} 没有 {field}", "warning")
                continue
            
            old_value = target.get(field, "")
            if old_value == corrected:
                continue
            
            target[field] = corrected
            fixed_count += 1
            
            path = f"{name}.{nested}[{nested_name}].{field}"
            old_display = old_value[:25] + "..." if len(old_value) > 25 else old_value
            new_display = corrected[:25] + "..." if len(corrected) > 25 else corrected
            modifications.append(f"{path}: '{old_display}' → '{new_display}'")
            log(f"  ✏️ 修复嵌套: {path} - {reason}")
            
            add_success_record(file_path=file_path, item_name=path, field=field,
                               original=old_value or original, corrected=corrected, reason=reason)
        else:
            # 处理顶层字段
            if field not in item:
                log(f"  ⚠️ 跳过: {name} 没有 {field} 字段", "warning")
                continue
            
            old_value = item.get(field, "")
            if old_value == corrected:
                continue
            
            # 执行修改
            item[field] = corrected
            fixed_count += 1
            
            old_display = old_value[:25] + "..." if len(old_value) > 25 else old_value
            new_display = corrected[:25] + "..." if len(corrected) > 25 else corrected
            modifications.append(f"{name}.{field}: '{old_display}' → '{new_display}'")
            log(f"  ✏️ 修复: {name}.{field} - {reason}")
            
            add_success_record(
                file_path=file_path,
                item_name=name,
                field=field,
                original=old_value or original,
                corrected=corrected,
                reason=reason
            )
    
    return fixed_count, modifications


# ==================== 主审核逻辑 ====================

def review_batch_with_retry(batch_items: List[dict], item_type: str,
                            data: dict, item_key: str, file_config: dict, 
                            batch_idx: int) -> Tuple[bool, int, int, List[str]]:
    """
    审核单个批次，带重试机制
    Returns: (success, issues_count, fixed_count, modifications)
    """
    file_path_str = file_config["path"]
    file_path = DATA_DIR / file_path_str
    
    for retry in range(MAX_RETRIES):
        try:
            if retry > 0:
                log(f"   🔄 重试 {retry}/{MAX_RETRIES}...")
                time.sleep(RETRY_DELAY)
            
            # 生成审核prompt
            prompt = get_review_prompt(batch_items, item_type)
            
            # 调用AI审核
            response = call_ai_api([
                {"role": "system", "content": "你是Dota2翻译专家。只返回JSON格式的审核结果。"},
                {"role": "user", "content": prompt}
            ])
            
            if not response:
                log(f"   ⚠️ API响应为空", "warning")
                continue
            
            result = parse_review_response(response)
            issues = result.get("issues", [])
            summary = result.get("summary", "")
            
            log(f"   发现问题: {len(issues)} 个")
            if summary:
                log(f"   摘要: {summary[:100]}")
            
            # 应用修复
            modifications = []
            fixed_count = 0
            if issues:
                fixed_count, modifications = apply_fixes(data, item_key, issues, file_path_str)
                
                # 保存修复后的文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                log(f"   ✅ 已修复 {fixed_count} 个问题")
            else:
                log(f"   ✅ 该批次翻译正确")
            
            return True, len(issues), fixed_count, modifications
            
        except Exception as e:
            log(f"   ❌ 处理异常: {e}", "error")
            if retry == MAX_RETRIES - 1:
                # 最后一次重试失败，记录到失败文件
                add_failed_record(
                    file_path=file_path_str,
                    batch_idx=batch_idx,
                    items=batch_items,
                    error_type="ProcessingError",
                    error_msg=str(e)
                )
    
    return False, 0, 0, []


def review_file(file_config: dict, progress: dict):
    """审核单个文件（增强版：支持重试和失败记录）"""
    file_path = DATA_DIR / file_config["path"]
    item_type = file_config["type"]
    item_key = file_config["item_key"]
    batch_size = file_config["batch_size"]
    
    if not file_path.exists():
        log(f"⚠️ 文件不存在: {file_config['path']}", "warning")
        return
    
    log("=" * 60)
    log(f"📁 开始审核: {file_config['path']}")
    log(f"   类型: {item_type}, 批次大小: {batch_size}")
    log("=" * 60)
    
    # 加载数据
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data.get(item_key, [])
    total = len(items)
    total_batches = (total + batch_size - 1) // batch_size
    
    # 获取文件进度
    file_progress = get_file_progress(progress, file_config["path"])
    start_batch = file_progress["current_batch"]
    file_progress["total_batches"] = total_batches
    file_progress["status"] = "in_progress"
    
    log(f"📊 总条目: {total}, 总批次: {total_batches}")
    if start_batch > 0:
        log(f"   从批次 {start_batch + 1} 继续...")
    
    file_start_time = time.time()
    total_issues = 0
    total_fixed = 0
    consecutive_failures = 0
    
    for batch_idx in range(start_batch, total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, total)
        batch_items = items[start:end]
        
        log(f"\n📦 批次 {batch_idx + 1}/{total_batches} (条目 {start+1}-{end})")
        
        # 调用带重试的审核
        success, issues_count, fixed_count, modifications = review_batch_with_retry(
            batch_items, item_type, data, item_key, file_config, batch_idx
        )
        
        if success:
            consecutive_failures = 0
            total_issues += issues_count
            total_fixed += fixed_count
            file_progress["modifications"].extend(modifications)
        else:
            consecutive_failures += 1
            log(f"   ⚠️ 批次处理失败，已记录到失败文件", "warning")
            
            # 连续失败太多，暂停一会儿
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                log(f"⚠️ 连续 {consecutive_failures} 次失败，暂停 60 秒...", "warning")
                time.sleep(60)
                consecutive_failures = 0
        
        # 更新进度
        file_progress["current_batch"] = batch_idx + 1
        file_progress["items_reviewed"] = end
        file_progress["issues_found"] = total_issues
        file_progress["issues_fixed"] = total_fixed
        progress["stats"]["total_items_reviewed"] += len(batch_items)
        save_progress(progress)
        
        # 打印进度
        pct = (batch_idx + 1) * 100 // total_batches
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        elapsed = time.time() - file_start_time
        eta = (elapsed / (batch_idx + 1 - start_batch)) * (total_batches - batch_idx - 1) if batch_idx > start_batch else 0
        log(f"   进度: [{bar}] {pct}% | 预计剩余: {eta/60:.1f}分钟")
        
        # 延迟避免请求过快
        time.sleep(1.0 + random.random() * 0.5)
    
    # 完成
    elapsed = time.time() - file_start_time
    file_progress["status"] = "completed"
    file_progress["completed_at"] = datetime.now().isoformat()
    progress["stats"]["total_issues_found"] += total_issues
    progress["stats"]["total_issues_fixed"] += total_fixed
    save_progress(progress)
    
    log(f"\n🎉 完成: {file_config['path']}")
    log(f"   耗时: {elapsed/60:.1f} 分钟")
    log(f"   发现问题: {total_issues}, 已修复: {total_fixed}")
    log(f"   成功记录: {SUCCESS_FILE}")
    log(f"   失败记录: {FAILED_FILE}")


def main():
    """主函数（支持无人值守长时间运行）"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║        Dota2 API 翻译审核与自动修复工具 (增强版)              ║
╠══════════════════════════════════════════════════════════════╣
║  功能:                                                       ║
║  - 使用AI检查翻译是否符合Dota2术语                            ║
║  - 自动修复不准确的翻译                                       ║
║  - 支持断点续传                                              ║
║  - 成功/失败分别记录到文件                                    ║
║  - 自动重试机制，支持无人值守运行                              ║
╠══════════════════════════════════════════════════════════════╣
║  输出文件:                                                   ║
║  - review_progress.json  : 进度追踪                          ║
║  - review_success.json   : 成功修复记录                       ║
║  - review_failed.json    : 失败记录（方便后续重试）            ║
║  - review.log            : 详细日志                          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 显示API配置
    log(f"🔑 API配置:")
    log(f"   Base URL: {API_BASE_URL}")
    log(f"   Model: {MODEL}")
    
    # 测试API连接
    log("🔄 测试API连接...")
    test_response = call_ai_api([{"role": "user", "content": "你好，回复OK即可"}])
    if test_response:
        log(f"✅ API连接正常")
    else:
        log("❌ API连接失败，请检查配置!", "error")
        return
    
    # 加载进度
    progress = load_progress()
    
    # 显示当前进度
    log("\n📊 当前进度:")
    for file_config in REVIEW_FILES:
        fp = progress.get("files", {}).get(file_config["path"], {})
        status_icon = "✅" if fp.get("status") == "completed" else "⏳" if fp.get("status") == "in_progress" else "⬜"
        batch_info = f"{fp.get('current_batch', 0)}/{fp.get('total_batches', '?')}" if fp.get("total_batches") else "未开始"
        log(f"  {status_icon} {file_config['path']}: {batch_info}")
    
    log("\n" + "=" * 60)
    log("开始审核...")
    log("=" * 60)
    
    start_time = time.time()
    
    # 依次审核每个文件
    for file_config in REVIEW_FILES:
        # 检查是否已完成
        fp = progress.get("files", {}).get(file_config["path"], {})
        if fp.get("status") == "completed":
            log(f"⏭️ 跳过已完成: {file_config['path']}")
            continue
        
        try:
            review_file(file_config, progress)
        except Exception as e:
            log(f"❌ 文件处理异常: {file_config['path']} - {e}", "error")
            continue
    
    # 总结
    elapsed = time.time() - start_time
    stats = progress.get("stats", {})
    
    log("\n" + "=" * 60)
    log("📊 审核完成总结")
    log("=" * 60)
    log(f"总耗时: {elapsed/60:.1f} 分钟")
    log(f"审核条目: {stats.get('total_items_reviewed', 0)}")
    log(f"发现问题: {stats.get('total_issues_found', 0)}")
    log(f"修复问题: {stats.get('total_issues_fixed', 0)}")
    log(f"\n进度文件: {PROGRESS_FILE}")


def reset_progress():
    """重置进度"""
    files_to_remove = [PROGRESS_FILE, SUCCESS_FILE, FAILED_FILE]
    for f in files_to_remove:
        if f.exists():
            os.remove(f)
            print(f"  已删除: {f.name}")
    print("✅ 所有进度和记录已重置")


def show_status():
    """显示当前状态"""
    progress = load_progress()
    success_records = load_success_records()
    failed_records = load_failed_records()
    
    print("\n" + "=" * 60)
    print("📊 审核进度状态")
    print("=" * 60)
    
    stats = progress.get("stats", {})
    print(f"开始时间: {progress.get('started_at', 'N/A')}")
    print(f"最后更新: {progress.get('updated_at', 'N/A')}")
    print(f"总审核条目: {stats.get('total_items_reviewed', 0)}")
    print(f"总发现问题: {stats.get('total_issues_found', 0)}")
    print(f"总修复问题: {stats.get('total_issues_fixed', 0)}")
    
    print("\n📁 文件进度:")
    for file_config in REVIEW_FILES:
        fp = progress.get("files", {}).get(file_config["path"], {})
        status = fp.get("status", "pending")
        status_icon = "✅" if status == "completed" else "⏳" if status == "in_progress" else "⬜"
        
        batch_current = fp.get("current_batch", 0)
        batch_total = fp.get("total_batches", 0)
        pct = batch_current * 100 // batch_total if batch_total > 0 else 0
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        
        issues = fp.get("issues_found", 0)
        fixed = fp.get("issues_fixed", 0)
        issue_str = f" 问题:{issues}/修复:{fixed}" if issues > 0 else ""
        
        print(f"  {status_icon} {file_config['path']}")
        print(f"     [{bar}] {batch_current}/{batch_total} ({pct}%){issue_str}")
    
    # 显示成功/失败记录摘要
    print("\n" + "-" * 60)
    print("📝 记录摘要:")
    print(f"  ✅ 成功修复: {success_records.get('total_fixed', 0)} 条")
    print(f"  ❌ 失败记录: {failed_records.get('total_failed', 0)} 条")
    
    if failed_records.get('records'):
        print("\n  最近失败:")
        for record in failed_records['records'][-3:]:
            print(f"    - {record['file']} 批次{record['batch_idx']}: {record['error_type']}")


def show_success():
    """显示成功修复记录"""
    records = load_success_records()
    
    print("\n" + "=" * 60)
    print("✅ 成功修复记录")
    print("=" * 60)
    print(f"总修复数: {records.get('total_fixed', 0)}")
    print(f"更新时间: {records.get('updated_at', 'N/A')}")
    
    if records.get('records'):
        print("\n最近 20 条修复:")
        for record in records['records'][-20:]:
            print(f"\n  📍 {record['file']} - {record['item']}.{record['field']}")
            print(f"     原文: {record['original'][:50]}...")
            print(f"     修正: {record['corrected'][:50]}...")
            print(f"     原因: {record['reason']}")
    else:
        print("\n暂无修复记录")


def show_failed():
    """显示失败记录"""
    records = load_failed_records()
    
    print("\n" + "=" * 60)
    print("❌ 失败记录")
    print("=" * 60)
    print(f"总失败数: {records.get('total_failed', 0)}")
    print(f"更新时间: {records.get('updated_at', 'N/A')}")
    
    if records.get('records'):
        print("\n所有失败记录:")
        for record in records['records']:
            print(f"\n  📍 {record['file']} - 批次 {record['batch_idx']}")
            print(f"     条目: {', '.join(record['items'][:3])}...")
            print(f"     错误类型: {record['error_type']}")
            print(f"     错误信息: {record['error_msg'][:100]}...")
            print(f"     重试次数: {record.get('retry_count', 0)}")
    else:
        print("\n暂无失败记录 🎉")


def print_help():
    """打印帮助信息"""
    print("""
Dota2 API 翻译审核工具 (增强版)

用法:
    python review_translations.py            # 开始/继续审核（支持无人值守）
    python review_translations.py --status   # 查看进度
    python review_translations.py --success  # 查看成功修复记录
    python review_translations.py --failed   # 查看失败记录
    python review_translations.py --reset    # 重置所有进度和记录
    python review_translations.py --help     # 显示帮助

说明:
    此脚本会依次检查以下文件的翻译质量:
    - gameevents/events_cn.json
    - luaapi/classes_cn.json
    - luaapi/functions_cn.json
    - luaapi/enums_cn.json
    - luaapi/constants.json
    - panoramaapi/enums.json
    - panoramaevents/events.json

特性:
    1. 分批读取每个文件的条目
    2. 使用AI检查翻译是否符合Dota2术语
    3. 自动修复发现的问题
    4. 断点续传 - 中断后可继续
    5. 自动重试 - 失败会重试3次
    6. 成功/失败分别记录到文件
    7. 支持无人值守长时间运行

输出文件:
    - review_progress.json : 进度追踪
    - review_success.json  : 成功修复记录
    - review_failed.json   : 失败记录
    - review.log           : 详细日志
    """)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
    elif "--reset" in sys.argv:
        confirm = input("⚠️ 确定要重置所有进度和记录吗？(输入 yes 确认): ")
        if confirm.lower() == "yes":
            reset_progress()
        else:
            print("已取消")
    elif "--status" in sys.argv:
        show_status()
    elif "--success" in sys.argv:
        show_success()
    elif "--failed" in sys.argv:
        show_failed()
    else:
        main()
