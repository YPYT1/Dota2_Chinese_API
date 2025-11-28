"""
Dota2 API 文档批量翻译脚本
- 支持无人值守长时间运行
- 断点续传
- 自动保存进度
- 翻译后文件保存为 xxx_cn.json
- 详细日志输出 + 日志文件
- 支持多线程并行翻译不同目录
"""
import json
import os
import sys
import time
import random
import logging
import threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加当前目录到 path
sys.path.insert(0, os.path.dirname(__file__))
from smart_api_pool import SmartAPIPool

# ==================== 日志配置 ====================

LOG_FILE = Path(__file__).parent.parent / "translate.log"

# 创建 logger
logger = logging.getLogger("translate")
logger.setLevel(logging.INFO)

# 文件处理器（详细日志）
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))

# 控制台处理器（简洁输出）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(message)s',
    datefmt='%H:%M:%S'
))

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log(msg, level="info", worker_id=None):
    """统一日志输出（线程安全）"""
    # 添加 worker 标识
    if worker_id is not None:
        msg = f"[W{worker_id}] {msg}"
    
    with log_lock:
        if level == "debug":
            logger.debug(msg)
        elif level == "warning":
            logger.warning(msg)
        elif level == "error":
            logger.error(msg)
        else:
            logger.info(msg)

# ==================== 配置 ====================

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"

# 翻译任务配置
TRANSLATE_TASKS = [
    {
        "source": "gameevents/events.json",
        "output": "gameevents/events_cn.json",
        "type": "game_event",
        "item_key": "items"
    },
    {
        "source": "luaapi/classes.json",
        "output": "luaapi/classes_cn.json",
        "type": "class",
        "item_key": "items"
    },
    {
        "source": "luaapi/functions.json",
        "output": "luaapi/functions_cn.json",
        "type": "function",
        "item_key": "items"
    },
    {
        "source": "luaapi/enums.json",
        "output": "luaapi/enums_cn.json",
        "type": "enum",
        "item_key": "items"
    },
    {
        "source": "luaapi/constants.json",
        "output": "luaapi/constants_cn.json",
        "type": "constant",
        "item_key": "items"
    },
    {
        "source": "panoramaapi/enums.json",
        "output": "panoramaapi/enums_cn.json",
        "type": "panorama_enum",
        "item_key": "items"
    },
    {
        "source": "panoramaevents/events.json",
        "output": "panoramaevents/events_cn.json",
        "type": "panorama_event",
        "item_key": "items"
    },
]

# 进度文件
PROGRESS_FILE = Path(__file__).parent.parent / "translate_progress.json"

# 失败记录文件
FAILED_FILE = Path(__file__).parent.parent / "translate_failed.json"

# 翻译模型
MODEL = "deepseek-ai/DeepSeek-V3"

# 线程锁（用于保护共享资源）
progress_lock = threading.Lock()
failed_lock = threading.Lock()
log_lock = threading.Lock()

# 任务分组（用于并行翻译）
TASK_GROUPS = [
    # 组1: gameevents
    [{"source": "gameevents/events.json", "output": "gameevents/events_cn.json", "type": "game_event", "item_key": "items"}],
    # 组2: luaapi (classes + functions)
    [
        {"source": "luaapi/classes.json", "output": "luaapi/classes_cn.json", "type": "class", "item_key": "items"},
        {"source": "luaapi/functions.json", "output": "luaapi/functions_cn.json", "type": "function", "item_key": "items"},
    ],
    # 组3: luaapi (enums + constants)
    [
        {"source": "luaapi/enums.json", "output": "luaapi/enums_cn.json", "type": "enum", "item_key": "items"},
        {"source": "luaapi/constants.json", "output": "luaapi/constants_cn.json", "type": "constant", "item_key": "items"},
    ],
    # 组4: panorama
    [
        {"source": "panoramaapi/enums.json", "output": "panoramaapi/enums_cn.json", "type": "panorama_enum", "item_key": "items"},
        {"source": "panoramaevents/events.json", "output": "panoramaevents/events_cn.json", "type": "panorama_event", "item_key": "items"},
    ],
]


# ==================== Prompt 模板 ====================

def get_translate_prompt(item_type: str, item: dict) -> str:
    """根据类型生成翻译 prompt"""
    
    base_prompt = """你是 Dota2 Mod 开发专家和技术文档翻译专家。请为以下 API 内容生成中文文档。

要求：
1. 翻译要准确、专业，符合 Dota2 游戏术语
2. 代码标识符（函数名、变量名、类型名）保持英文不翻译
3. 返回标准 JSON 格式，只返回 JSON，不要其他内容
4. 对于每个需要翻译的 _cn 字段，填入对应的中文翻译

Dota2 常用术语参考：
- hero = 英雄
- ability = 技能
- modifier = 修改器/buff
- item = 物品
- unit = 单位
- entity = 实体
- damage = 伤害
- cooldown = 冷却时间
- mana = 魔法值
- health = 生命值
- armor = 护甲
- attack = 攻击

"""
    
    if item_type == "game_event":
        # 只提取必要信息，减少 token 消耗
        params_info = []
        for p in item.get("parameters", []):
            params_info.append({"name": p.get("name"), "type": p.get("type")})
        
        simplified = {
            "name": item.get("name"),
            "signature": item.get("signature"),
            "parameters": params_info
        }
        
        return base_prompt + f"""
这是一个 Dota2 Game Event（游戏事件）：
{json.dumps(simplified, ensure_ascii=False)}

请只返回翻译结果的 JSON，格式如下：
{{
  "name_cn": "事件名称中文",
  "description_cn": "事件描述（什么时候触发、有什么用）",
  "parameters_cn": [
    {{"name": "参数名", "description_cn": "参数说明", "type_description_cn": "类型说明"}}
  ]
}}

只返回上述格式的 JSON，不要返回原始数据。
"""
    
    elif item_type == "class":
        # 只提取类级别信息，方法太多会导致 token 超限
        # 只取前5个方法名作为参考
        method_names = [m.get("name") for m in item.get("methods", [])[:5]]
        
        simplified = {
            "name": item.get("name"),
            "extends": item.get("extends"),
            "description": item.get("description"),
            "method_count": len(item.get("methods", [])),
            "sample_methods": method_names
        }
        
        return base_prompt + f"""
这是一个 Dota2 Lua API 类：
{json.dumps(simplified, ensure_ascii=False, indent=2)}

请只返回类级别的翻译（不要翻译方法），格式如下：
{{
  "name_cn": "类名中文说明（简短）",
  "description_cn": "这个类的作用、什么时候使用（1-2句话）",
  "common_usage_cn": "常见使用场景"
}}

只返回上述格式的 JSON，不要返回原始数据，不要翻译方法。
"""
    
    elif item_type == "function":
        # 简化函数信息
        params_info = [{"name": p.get("name"), "type": p.get("type"), "isOptional": p.get("isOptional", False)} for p in item.get("parameters", [])]
        
        simplified = {
            "name": item.get("name"),
            "signature": item.get("signature"),
            "description": item.get("description"),
            "returnType": item.get("returnType"),
            "parameters": params_info
        }
        
        return base_prompt + f"""
这是一个 Dota2 Lua API 全局函数：
{json.dumps(simplified, ensure_ascii=False, indent=2)}

请只返回翻译结果的 JSON，格式如下：
{{
  "name_cn": "函数中文名",
  "description_cn": "函数功能详细说明（做什么、什么时候用）",
  "common_usage_cn": "常见使用场景",
  "returnType_cn": "返回值类型说明",
  "returnDescription_cn": "返回值含义说明",
  "parameters_cn": [
    {{"name": "参数名", "description_cn": "参数说明", "type_description_cn": "类型说明"}}
  ]
}}

只返回上述格式的 JSON，不要返回原始数据。
"""
    
    elif item_type in ["enum", "panorama_enum"]:
        # 简化枚举信息
        members_info = [{"name": m.get("name"), "value": m.get("value")} for m in item.get("members", [])]
        
        simplified = {
            "name": item.get("name"),
            "description": item.get("description"),
            "members": members_info
        }
        
        return base_prompt + f"""
这是一个 Dota2 枚举定义：
{json.dumps(simplified, ensure_ascii=False, indent=2)}

请只返回翻译结果的 JSON，格式如下：
{{
  "name_cn": "枚举中文名",
  "description_cn": "枚举用途说明（什么时候用、有哪些值）",
  "common_usage_cn": "常见使用场景",
  "members_cn": [
    {{"name": "成员名", "description_cn": "该值的含义说明"}}
  ]
}}

只返回上述格式的 JSON，不要返回原始数据。
"""
    
    elif item_type in ["panorama_event"]:
        return base_prompt + f"""
这是一个 Dota2 Panorama UI 事件：

{json.dumps(item, ensure_ascii=False, indent=2)}

请填充以下中文字段并返回完整 JSON：
- name_cn: 事件名的中文翻译
- description_cn: 事件的详细中文描述
- 每个 parameter 的 description_cn: 参数说明

只返回 JSON，不要其他内容。
"""
    
    elif item_type == "constant":
        simplified = {
            "name": item.get("name"),
            "value": item.get("value"),
            "valueType": item.get("valueType")
        }
        
        return base_prompt + f"""
这是一个 Dota2 常量定义：
{json.dumps(simplified, ensure_ascii=False, indent=2)}

请只返回翻译结果的 JSON，格式如下：
{{
  "name_cn": "常量中文名",
  "description_cn": "常量用途说明（这个值代表什么、什么时候用）",
  "common_usage_cn": "常见使用场景"
}}

只返回上述格式的 JSON，不要返回原始数据。
"""
    
    return base_prompt + f"""
请翻译以下内容的 _cn 字段：

{json.dumps(item, ensure_ascii=False, indent=2)}

只返回 JSON，不要其他内容。
"""


# ==================== 翻译逻辑 ====================

def load_progress() -> dict:
    """加载进度（线程安全）"""
    with progress_lock:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


def save_progress(progress: dict):
    """保存进度（线程安全）"""
    with progress_lock:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)


def load_failed() -> dict:
    """加载失败记录（线程安全）"""
    with failed_lock:
        if FAILED_FILE.exists():
            with open(FAILED_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


def save_failed(failed: dict):
    """保存失败记录（线程安全）"""
    with failed_lock:
        with open(FAILED_FILE, 'w', encoding='utf-8') as f:
            json.dump(failed, f, ensure_ascii=False, indent=2)


def add_failed(failed: dict, file_key: str, index: int, name: str):
    """添加失败记录"""
    if file_key not in failed:
        failed[file_key] = []
    # 避免重复
    if index not in failed[file_key]:
        failed[file_key].append(index)
        failed[file_key].sort()  # 保持顺序
    save_failed(failed)


def remove_failed(failed: dict, file_key: str, index: int):
    """移除失败记录（重试成功后）"""
    if file_key in failed and index in failed[file_key]:
        failed[file_key].remove(index)
        if not failed[file_key]:
            del failed[file_key]
        save_failed(failed)


def fix_truncated_json(json_str: str) -> str:
    """修复截断的 JSON 字符串"""
    # 检查是否在字符串中间
    in_string = False
    escape = False
    last_quote_pos = -1
    
    for i, c in enumerate(json_str):
        if escape:
            escape = False
            continue
        if c == '\\':
            escape = True
            continue
        if c == '"':
            in_string = not in_string
            if in_string:
                last_quote_pos = i
    
    fixed = json_str.rstrip()
    
    # 如果在字符串中间截断，添加引号
    if in_string:
        fixed += '"'
    
    # 循环移除尾部不完整的部分
    max_iterations = 10
    for _ in range(max_iterations):
        fixed = fixed.rstrip()
        if not fixed:
            break
            
        last_char = fixed[-1]
        
        # 如果以逗号结尾，移除
        if last_char == ',':
            fixed = fixed[:-1]
            continue
        
        # 如果以冒号结尾，添加空值
        if last_char == ':':
            fixed += '""'
            continue
        
        # 如果以 { 开头但没内容
        if last_char == '{':
            fixed += '}'
            continue
            
        # 如果以 [ 开头但没内容
        if last_char == '[':
            fixed += ']'
            continue
        
        # 如果以引号结尾，检查是否是完整的键值对
        if last_char == '"':
            # 检查前面是否是 : 或 , 或 { 或 [
            # 如果是 "key": "value" 形式，是完整的
            break
            
        break
    
    # 计算并添加缺少的闭合括号
    # 需要按正确顺序闭合：先 }，再 ]，交替进行
    open_braces = fixed.count('{') - fixed.count('}')
    open_brackets = fixed.count('[') - fixed.count(']')
    
    # 分析结构，按正确顺序闭合
    # 简单策略：交替添加 } 和 ]
    while open_braces > 0 or open_brackets > 0:
        # 先闭合最内层的 {
        if open_braces > 0:
            fixed += '}'
            open_braces -= 1
        # 再闭合 [
        if open_brackets > 0:
            fixed += ']'
            open_brackets -= 1
    
    return fixed


def parse_json_response(response: str) -> dict:
    """解析 AI 返回的 JSON，能处理截断和格式错误的情况"""
    import re
    
    # 清理响应
    response = response.strip()
    
    # 移除 markdown 代码块标记
    if response.startswith('```'):
        response = re.sub(r'^```(?:json)?\s*', '', response)
        response = re.sub(r'\s*```$', '', response)
    
    # 修复常见的 JSON 格式错误
    # 1. 修复缺少引号的键名，如: description": → "description":
    response = re.sub(r'(\s)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:\s*)', r'\1"\2"\3', response)
    # 2. 修复重复的引号
    response = re.sub(r'""([a-zA-Z_][a-zA-Z0-9_]*)""', r'"\1"', response)
    
    # 1. 尝试直接解析
    try:
        return json.loads(response)
    except:
        pass
    
    # 2. 找到 JSON 开始位置
    start = response.find('{')
    if start == -1:
        raise ValueError(f"无法找到 JSON 开始: {response[:100]}")
    
    json_str = response[start:]
    
    # 3. 尝试直接解析
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # 4. 尝试修复截断的 JSON
    fixed = fix_truncated_json(json_str)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass
    
    # 5. 更激进的修复：找到最后一个完整的键值对
    # 尝试在不同位置截断并修复
    for end_marker in ['},', '},\n', '",', '"\n', '],', ']\n']:
        last_pos = json_str.rfind(end_marker)
        if last_pos > 0:
            truncated = json_str[:last_pos + len(end_marker) - 1]  # 不包含逗号
            fixed = fix_truncated_json(truncated)
            try:
                return json.loads(fixed)
            except:
                continue
    
    # 6. 最后尝试：从后往前找完整的 }
    for i in range(len(json_str) - 1, 0, -1):
        if json_str[i] == '}':
            test_str = json_str[:i+1]
            fixed = fix_truncated_json(test_str)
            try:
                return json.loads(fixed)
            except:
                continue
    
    raise ValueError(f"无法解析 JSON: {response[:200]}")


def merge_translation(original: dict, translation: dict, item_type: str) -> dict:
    """将翻译结果合并到原始数据中"""
    import copy
    result = copy.deepcopy(original)  # 深拷贝避免修改原始数据
    
    # 合并顶层字段
    top_level_keys = [
        "name_cn", "description_cn", "example_ts", "notes_cn", "common_usage_cn", 
        "usage_cn", "returnType_cn", "returnDescription_cn", "warnings_cn"
    ]
    for key in top_level_keys:
        if key in translation and translation[key]:
            result[key] = translation[key]
    
    # 合并参数翻译 (game_event, function, panorama_event)
    if "parameters_cn" in translation:
        params_cn = {p["name"]: p for p in translation["parameters_cn"] if "name" in p}
        for param in result.get("parameters", []):
            pname = param.get("name")
            if pname in params_cn:
                param["description_cn"] = params_cn[pname].get("description_cn", "")
                param["type_description_cn"] = params_cn[pname].get("type_description_cn", "")
    
    # 合并方法翻译 (class)
    if item_type == "class" and "methods_cn" in translation:
        methods_cn = {m["name"]: m for m in translation["methods_cn"] if "name" in m}
        for method in result.get("methods", []):
            mname = method.get("name")
            if mname in methods_cn:
                m_trans = methods_cn[mname]
                method["name_cn"] = m_trans.get("name_cn", "")
                method["description_cn"] = m_trans.get("description_cn", "")
                method["returnType_cn"] = m_trans.get("returnType_cn", "")
                method["returnDescription_cn"] = m_trans.get("returnDescription_cn", "")
                method["notes_cn"] = m_trans.get("notes_cn", "")
                method["warnings_cn"] = m_trans.get("warnings_cn", "")
                method["common_usage_cn"] = m_trans.get("common_usage_cn", "")
                
                # 合并方法的参数翻译
                if "parameters_cn" in m_trans:
                    m_params_cn = {p["name"]: p for p in m_trans["parameters_cn"] if "name" in p}
                    for param in method.get("parameters", []):
                        pname = param.get("name")
                        if pname in m_params_cn:
                            param["description_cn"] = m_params_cn[pname].get("description_cn", "")
                            param["type_description_cn"] = m_params_cn[pname].get("type_description_cn", "")
    
    # 合并类字段翻译 (class fields)
    if item_type == "class" and "fields_cn" in translation:
        fields_cn = {f["name"]: f for f in translation["fields_cn"] if "name" in f}
        for field in result.get("fields", []):
            fname = field.get("name")
            if fname in fields_cn:
                field["description_cn"] = fields_cn[fname].get("description_cn", "")
                field["type_description_cn"] = fields_cn[fname].get("type_description_cn", "")
                field["notes_cn"] = fields_cn[fname].get("notes_cn", "")
    
    # 合并枚举成员翻译 (enum)
    if item_type in ["enum", "panorama_enum"] and "members_cn" in translation:
        members_cn = {m["name"]: m for m in translation["members_cn"] if "name" in m}
        for member in result.get("members", []):
            mname = member.get("name")
            if mname in members_cn:
                member["description_cn"] = members_cn[mname].get("description_cn", "")
    
    # ==================== 确保所有翻译字段存在 ====================
    
    # 顶层字段
    result.setdefault("name_cn", "")
    result.setdefault("description_cn", "")
    result.setdefault("example_ts", "")
    result.setdefault("notes_cn", "")
    result.setdefault("warnings_cn", "")
    result.setdefault("common_usage_cn", "")
    result.setdefault("related", [])
    result.setdefault("see_also", [])
    result.setdefault("tags", [])
    
    # function/class 顶层的返回值字段
    if item_type in ["function"]:
        result.setdefault("returnType_cn", "")
        result.setdefault("returnDescription_cn", "")
    
    # 参数字段 (function, panorama_event)
    for param in result.get("parameters", []):
        param.setdefault("description_cn", "")
        param.setdefault("type_description_cn", "")
    
    # 方法字段 (class)
    for method in result.get("methods", []):
        method.setdefault("name_cn", "")
        method.setdefault("description_cn", "")
        method.setdefault("returnType_cn", "")
        method.setdefault("returnDescription_cn", "")
        method.setdefault("notes_cn", "")
        method.setdefault("warnings_cn", "")
        method.setdefault("common_usage_cn", "")
        for param in method.get("parameters", []):
            param.setdefault("description_cn", "")
            param.setdefault("type_description_cn", "")
    
    # 类字段 (class fields)
    for field in result.get("fields", []):
        field.setdefault("description_cn", "")
        field.setdefault("type_description_cn", "")
        field.setdefault("notes_cn", "")
    
    # 枚举成员字段 (enum)
    for member in result.get("members", []):
        member.setdefault("description_cn", "")
    
    return result


def translate_methods_batch(pool: SmartAPIPool, class_name: str, methods: list, batch_size: int = 5) -> dict:
    """
    分批翻译类的方法
    Returns: {method_name: translation_dict}
    """
    all_translations = {}
    total_batches = (len(methods) + batch_size - 1) // batch_size
    
    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(methods))
        batch = methods[start:end]
        
        # 极简方法信息
        batch_info = []
        for m in batch:
            params = [p.get("name") for p in m.get("parameters", [])]
            batch_info.append({
                "n": m.get("name"),
                "d": (m.get("description") or "")[:100],  # 限制描述长度
                "p": params
            })
        
        # 极简 prompt
        prompt = f"""翻译Dota2方法:
{json.dumps(batch_info, ensure_ascii=False)}
返回JSON:{{"m":[{{"n":"方法名","c":"中文名","d":"说明","p":[{{"n":"参数名","d":"说明"}}]}}]}}"""
        
        response = pool.chat_safe([
            {"role": "system", "content": "只返回JSON。字段名name必须保持英文原样。"},
            {"role": "user", "content": prompt}
        ], model=MODEL)
        
        if response:
            try:
                result = parse_json_response(response)
                # 支持多种格式
                methods_list = result.get("methods_cn", result.get("m", []))
                success_count = 0
                for m in methods_list:
                    # 支持 name 或 n 作为方法名
                    mname = m.get("name", m.get("n"))
                    if mname:
                        # 转换简化格式到标准格式
                        all_translations[mname] = {
                            "name": mname,
                            "name_cn": m.get("name_cn", m.get("c", m.get("n_cn", ""))),
                            "description_cn": m.get("description_cn", m.get("d", "")),
                            "returnType_cn": m.get("returnType_cn", m.get("r", "")),
                            "returnDescription_cn": m.get("returnDescription_cn", ""),
                            "parameters_cn": []
                        }
                        # 处理参数
                        params = m.get("parameters_cn", m.get("p", []))
                        for p in params:
                            pname = p.get("name", p.get("n")) if isinstance(p, dict) else None
                            if pname:
                                all_translations[mname]["parameters_cn"].append({
                                    "name": pname,
                                    "description_cn": p.get("description_cn", p.get("d", "")),
                                    "type_description_cn": p.get("type_description_cn", p.get("t", ""))
                                })
                        success_count += 1
                log(f"      方法批次 {batch_idx+1}/{total_batches}: ✅ {success_count} 个")
            except Exception as e:
                log(f"      方法批次 {batch_idx+1}/{total_batches}: ❌ {str(e)[:60]}")
        else:
            log(f"      方法批次 {batch_idx+1}/{total_batches}: ❌ 请求失败")
        
        time.sleep(0.5)  # 避免请求过快
    
    return all_translations


def translate_class_item(pool: SmartAPIPool, item: dict, index: int, total: int) -> tuple:
    """
    翻译单个 class 条目（包括分批翻译方法）
    Returns: (translated_item, success: bool)
    """
    import copy
    name = item.get("name", f"class_{index}")
    start_time = time.time()
    
    log(f"[{index+1}/{total}] 开始翻译类: {name}")
    
    methods = item.get("methods", [])
    log(f"      包含 {len(methods)} 个方法")
    
    # 第一步：翻译类本身
    prompt = get_translate_prompt("class", item)
    
    response = pool.chat_safe([
        {"role": "system", "content": "只返回纯 JSON，不要 markdown。直接以 { 开头。"},
        {"role": "user", "content": prompt}
    ], model=MODEL)
    
    result = copy.deepcopy(item)
    class_success = False
    
    if response:
        try:
            translation = parse_json_response(response)
            # 合并类级别翻译
            for key in ["name_cn", "description_cn", "common_usage_cn", "notes_cn"]:
                if key in translation and translation[key]:
                    result[key] = translation[key]
            class_success = True
            log(f"      类信息: ✅")
        except Exception as e:
            log(f"      类信息: ❌ {e}")
    
    # 第二步：分批翻译方法（如果有方法）
    if methods:
        # 每批3个方法，避免 token 超限导致 JSON 截断
        methods_translations = translate_methods_batch(pool, name, methods, batch_size=3)
        
        # 合并方法翻译
        for method in result.get("methods", []):
            mname = method.get("name")
            if mname in methods_translations:
                m_trans = methods_translations[mname]
                method["name_cn"] = m_trans.get("name_cn", "")
                method["description_cn"] = m_trans.get("description_cn", "")
                method["returnType_cn"] = m_trans.get("returnType_cn", "")
                method["returnDescription_cn"] = m_trans.get("returnDescription_cn", "")
                
                # 合并参数翻译
                if "parameters_cn" in m_trans:
                    params_cn = {p["name"]: p for p in m_trans["parameters_cn"] if "name" in p}
                    for param in method.get("parameters", []):
                        pname = param.get("name")
                        if pname in params_cn:
                            param["description_cn"] = params_cn[pname].get("description_cn", "")
                            param["type_description_cn"] = params_cn[pname].get("type_description_cn", "")
        
        translated_methods = sum(1 for m in result.get("methods", []) if m.get("name_cn"))
        log(f"      方法翻译: {translated_methods}/{len(methods)}")
    
    # 确保所有字段有默认值
    result = merge_translation(result, {}, "class")
    
    elapsed = time.time() - start_time
    log(f"[{index+1}/{total}] {'✅' if class_success else '⚠️'} 完成: {name} (耗时 {elapsed:.1f}s)")
    
    return result, class_success


def translate_item(pool: SmartAPIPool, item: dict, item_type: str, index: int, total: int) -> tuple:
    """
    翻译单个条目
    Returns: (translated_item, success: bool)
    """
    # class 类型使用专门的翻译函数
    if item_type == "class":
        return translate_class_item(pool, item, index, total)
    
    name = item.get("name", item.get("eventName", f"item_{index}"))
    start_time = time.time()
    
    log(f"[{index+1}/{total}] 开始翻译: {name}")
    
    prompt = get_translate_prompt(item_type, item)
    
    response = pool.chat_safe([
        {"role": "system", "content": "你是 Dota2 Mod 开发专家和技术文档翻译专家。\n\n重要规则：\n1. 只返回纯 JSON，不要 markdown 代码块\n2. 不要返回 ```json 或 ```\n3. 直接以 { 开头，以 } 结尾\n4. 确保 JSON 完整，不要截断\n5. 只返回翻译字段，不要返回原始数据"},
        {"role": "user", "content": prompt}
    ], model=MODEL)
    
    elapsed = time.time() - start_time
    
    if response is None:
        log(f"[{index+1}/{total}] ❌ 翻译失败: {name} (耗时 {elapsed:.1f}s)", "error")
        return item, False
    
    try:
        translation = parse_json_response(response)
        # 合并翻译结果到原始数据
        result = merge_translation(item, translation, item_type)
        log(f"[{index+1}/{total}] ✅ 完成: {name} (耗时 {elapsed:.1f}s)")
        return result, True
    except Exception as e:
        log(f"[{index+1}/{total}] ❌ JSON解析失败: {name} - {e}", "error")
        return item, False


def translate_file(pool: SmartAPIPool, task: dict, progress: dict, failed: dict, global_stats: dict, worker_id: int = 0):
    """翻译单个文件"""
    source_path = DATA_DIR / task["source"]
    output_path = DATA_DIR / task["output"]
    item_type = task["type"]
    item_key = task["item_key"]
    progress_key = task["source"]
    
    # 获取目录名作为标识
    dir_name = task["source"].split("/")[0]
    
    log("=" * 60, worker_id=worker_id)
    log(f"📁 [{dir_name}] 开始翻译: {task['source']}", worker_id=worker_id)
    log(f"   输出: {task['output']}", worker_id=worker_id)
    log(f"   类型: {item_type}", worker_id=worker_id)
    log("=" * 60, worker_id=worker_id)
    
    # 加载源数据
    with open(source_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data.get(item_key, [])
    total = len(items)
    
    # 检查是否有已翻译的输出文件
    translated_data = None
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            translated_data = json.load(f)
    else:
        translated_data = {
            "metadata": data.get("metadata", {}),
            item_key: []
        }
        translated_data["metadata"]["translated_at"] = datetime.now().isoformat()
        translated_data["metadata"]["model"] = MODEL
    
    # 获取已翻译的索引
    start_index = progress.get(progress_key, 0)
    
    # 获取之前失败的条目
    failed_indices = failed.get(progress_key, [])
    
    log(f"📊 [{dir_name}] 进度: {start_index}/{total} ({start_index*100//total if total > 0 else 0}%)", worker_id=worker_id)
    log(f"   待翻译: {total - start_index} 条", worker_id=worker_id)
    if failed_indices:
        log(f"   ⚠️ 之前失败需重试: {len(failed_indices)} 条", worker_id=worker_id)
    
    # 确保已翻译的数据列表长度正确
    while len(translated_data[item_key]) < start_index:
        translated_data[item_key].append(items[len(translated_data[item_key])])
    
    file_start_time = time.time()
    
    # ========== 第一阶段：重试之前失败的条目 ==========
    if failed_indices:
        log(f"🔄 [{dir_name}] 重试 {len(failed_indices)} 个失败条目...", worker_id=worker_id)
        retry_success = 0
        retry_failed = 0
        
        for idx in failed_indices[:]:  # 用切片复制，避免修改时出错
            if idx >= total:
                continue
            
            item = items[idx]
            name = item.get("name", item.get("eventName", f"item_{idx}"))
            log(f"  🔄 [{dir_name}] 重试 [{idx+1}/{total}]: {name}", worker_id=worker_id)
            
            translated_item, success = translate_item(pool, item, item_type, idx, total)
            
            if success:
                # 更新翻译结果
                while len(translated_data[item_key]) <= idx:
                    translated_data[item_key].append(items[len(translated_data[item_key])])
                translated_data[item_key][idx] = translated_item
                
                # 从失败列表移除
                remove_failed(failed, progress_key, idx)
                retry_success += 1
                log(f"  ✅ [{dir_name}] 重试成功: {name}", worker_id=worker_id)
            else:
                retry_failed += 1
                log(f"  ❌ [{dir_name}] 重试失败: {name}", worker_id=worker_id)
            
            time.sleep(0.5)
        
        # 保存重试后的结果
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
        log(f"  📊 [{dir_name}] 重试结果: 成功 {retry_success}, 失败 {retry_failed}", worker_id=worker_id)
    
    # ========== 第二阶段：继续翻译新条目 ==========
    if start_index < total:
        log(f"📝 [{dir_name}] 继续翻译 (从 {start_index + 1} 开始)...", worker_id=worker_id)
    
    consecutive_failures = 0  # 连续失败计数
    MAX_CONSECUTIVE_FAILURES = 20  # 连续失败超过这个数就暂停
    
    for i in range(start_index, total):
        item = items[i]
        name = item.get("name", item.get("eventName", f"item_{i}"))
        
        # 检查 API 池状态
        pool_status = pool.get_status()
        if pool_status['available'] == 0:
            log(f"❌ [{dir_name}] API Key 都已失效！进度: {i}/{total}", "error", worker_id=worker_id)
            # 保存当前文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
            raise Exception(f"[{dir_name}] 所有 API Key 都已失效")
        
        # 翻译
        log(f"[{dir_name}] [{i+1}/{total}] 翻译: {name}", worker_id=worker_id)
        translated_item, success = translate_item(pool, item, item_type, i, total)
        
        # 添加到结果
        if len(translated_data[item_key]) > i:
            translated_data[item_key][i] = translated_item
        else:
            translated_data[item_key].append(translated_item)
        
        # 记录失败
        if not success:
            add_failed(failed, progress_key, i, name)
            consecutive_failures += 1
            log(f"  ❌ [{dir_name}] 失败: {name}", worker_id=worker_id)
            
            # 连续失败太多，可能是 API 问题
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                log(f"⚠️ [{dir_name}] 连续 {consecutive_failures} 次失败，暂停", "warning", worker_id=worker_id)
                # 保存当前文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(translated_data, f, ensure_ascii=False, indent=2)
                progress[progress_key] = i + 1
                save_progress(progress)
                return  # 退出当前文件，继续下一个文件
        else:
            consecutive_failures = 0  # 成功则重置
            log(f"  ✅ [{dir_name}] 完成: {name}", worker_id=worker_id)
        
        # 保存进度（每条都保存）
        progress[progress_key] = i + 1
        save_progress(progress)
        
        # 更新全局统计（线程安全）
        with progress_lock:
            global_stats["completed"] += 1
        
        # 每条都保存文件（确保不丢失）
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
        # 每 5 条打印一次状态
        if (i + 1) % 5 == 0 or i == total - 1:
            elapsed = time.time() - file_start_time
            items_done = i + 1 - start_index
            avg_time = elapsed / items_done if items_done > 0 else 0
            remaining = (total - i - 1) * avg_time
            
            current_failed = len(failed.get(progress_key, []))
            log(f"💾 [{dir_name}] {i+1}/{total} | 失败:{current_failed} | {avg_time:.1f}s/条 | 剩余:{remaining/60:.1f}分钟", worker_id=worker_id)
        
        # 短暂休息，避免请求过快（增加随机抖动避免多线程同时请求）
        time.sleep(1.0 + random.random() * 0.5)  # 1.0-1.5 秒随机延迟
    
    elapsed = time.time() - file_start_time
    final_failed = len(failed.get(progress_key, []))
    log(f"🎉 [{dir_name}] 完成: {task['source']} | 耗时: {elapsed/60:.1f}分钟 | 失败: {final_failed} 条", worker_id=worker_id)


def worker_translate_group(worker_id: int, api_keys: list, tasks: list, progress: dict, failed: dict, global_stats: dict, all_tasks: list = None):
    """
    Worker 线程：翻译一组任务
    每个 worker 使用多个 API Key（轮换使用）
    完成自己的任务后，会尝试帮助其他未完成的任务
    """
    # 创建独立的 API 池，使用分配的多个 Key
    pool = SmartAPIPool(max_rpm=60, max_rpm_per_key=10)  # 降低单 Key 速率
    # 清空默认 keys
    pool.keys_info = {}
    pool.key_order = api_keys
    pool.current_key_index = 0
    
    # 添加分配的所有 keys
    from smart_api_pool import APIKeyInfo
    for key in api_keys:
        pool.keys_info[key] = APIKeyInfo(key=key)
    
    log(f"🚀 Worker {worker_id} 启动，负责 {len(tasks)} 个任务", worker_id=worker_id)
    log(f"   分配 {len(api_keys)} 个 API Keys", worker_id=worker_id)
    
    def process_task(task):
        """处理单个任务，返回是否有工作可做"""
        source_path = DATA_DIR / task["source"]
        if not source_path.exists():
            log(f"⚠️ 跳过不存在: {task['source']}", "warning", worker_id=worker_id)
            return False
        
        # 检查是否已完成
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total = len(data.get(task["item_key"], []))
        done = progress.get(task["source"], 0)
        has_failed = len(failed.get(task["source"], [])) > 0
        
        if done >= total and not has_failed:
            return False  # 已完成，无需处理
        
        try:
            translate_file(pool, task, progress, failed, global_stats, worker_id)
            return True
        except Exception as e:
            log(f"❌ 任务异常: {task['source']} - {e}", "error", worker_id=worker_id)
            return False
    
    # 第一阶段：处理自己负责的任务
    for task in tasks:
        process_task(task)
    
    log(f"✅ Worker {worker_id} 完成自己的任务", worker_id=worker_id)
    
    # 第二阶段：帮助其他未完成的任务
    if all_tasks:
        log(f"🔍 Worker {worker_id} 检查是否有其他任务需要帮助...", worker_id=worker_id)
        helped = False
        for task in all_tasks:
            # 跳过自己已经处理过的
            if task in tasks:
                continue
            
            source_path = DATA_DIR / task["source"]
            if not source_path.exists():
                continue
            
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            total = len(data.get(task["item_key"], []))
            done = progress.get(task["source"], 0)
            has_failed = len(failed.get(task["source"], [])) > 0
            
            # 如果还有未完成的工作
            if done < total or has_failed:
                log(f"🤝 Worker {worker_id} 帮助翻译: {task['source']} ({done}/{total})", worker_id=worker_id)
                if process_task(task):
                    helped = True
        
        if not helped:
            log(f"👍 Worker {worker_id} 没有需要帮助的任务", worker_id=worker_id)
    
    log(f"🏁 Worker {worker_id} 完成所有工作", worker_id=worker_id)


def main(parallel: int = 1):
    """
    主函数
    parallel: 并行线程数（1=串行，>1=并行）
    """
    log("=" * 60)
    log("🚀 Dota2 API 文档批量翻译")
    log(f"   模型: {MODEL}")
    log(f"   模式: {'并行 ' + str(parallel) + ' 线程' if parallel > 1 else '串行'}")
    log(f"   时间: {datetime.now().isoformat()}")
    log(f"   日志: {LOG_FILE}")
    log("=" * 60)
    
    # 加载 API Keys
    keys_file = Path(__file__).parent.parent / "valid_api_keys.json"
    with open(keys_file, 'r') as f:
        all_keys = json.load(f)["keys"]
    
    log(f"\n🔑 可用 API Keys: {len(all_keys)} 个")
    
    # 加载进度和失败记录
    progress = load_progress()
    failed = load_failed()
    
    # 统计
    total_items = 0
    completed_items = 0
    total_failed = 0
    
    log("\n📋 任务列表:")
    for task in TRANSLATE_TASKS:
        source_path = DATA_DIR / task["source"]
        if source_path.exists():
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            count = len(data.get(task["item_key"], []))
            done = progress.get(task["source"], 0)
            failed_count = len(failed.get(task["source"], []))
            total_items += count
            completed_items += done
            total_failed += failed_count
            status = "✅" if done >= count else "⏳"
            failed_str = f" (❌失败: {failed_count})" if failed_count > 0 else ""
            log(f"   {status} {task['source']}: {done}/{count}{failed_str}")
    
    log(f"\n📊 总进度: {completed_items}/{total_items} ({completed_items*100//total_items if total_items > 0 else 0}%)")
    if total_failed > 0:
        log(f"   ⚠️ 待重试: {total_failed} 条失败记录")
    
    # 全局统计
    global_stats = {
        "total": total_items,
        "completed": completed_items,
        "start_time": time.time()
    }
    
    # 开始翻译
    if parallel > 1:
        log(f"\n🔀 并行模式: {parallel} 个线程同时工作")
        log(f"   每个线程使用独立的 API Key")
        for i, group in enumerate(TASK_GROUPS[:parallel]):
            tasks_str = ", ".join([t["source"].split("/")[0] for t in group])
            log(f"   线程 {i+1}: {tasks_str}")
    
    input("\n按 Enter 开始翻译（Ctrl+C 可随时中断，进度会自动保存）...")
    
    log("\n🏃 开始翻译任务...")
    
    try:
        if parallel > 1:
            # 并行模式
            num_workers = min(parallel, len(TASK_GROUPS))
            threads = []
            
            # 将 API Keys 平均分配给各个 Worker
            # 每个 Worker 获得多个 Key，可以在限流时切换
            keys_per_worker = max(1, len(all_keys) // num_workers)
            
            log(f"\n🔑 Key 分配策略: {len(all_keys)} 个 Key / {num_workers} 个 Worker = 每个 Worker {keys_per_worker} 个 Key")
            
            # 收集所有任务（用于完成后帮助其他线程）
            all_tasks_flat = [task for group in TASK_GROUPS for task in group]
            
            for i in range(num_workers):
                # 分配 Keys: Worker i 获得 keys[i*n : (i+1)*n]
                start_idx = i * keys_per_worker
                end_idx = start_idx + keys_per_worker if i < num_workers - 1 else len(all_keys)
                worker_keys = all_keys[start_idx:end_idx]
                
                tasks = TASK_GROUPS[i]
                
                t = threading.Thread(
                    target=worker_translate_group,
                    args=(i + 1, worker_keys, tasks, progress, failed, global_stats, all_tasks_flat),
                    daemon=True
                )
                threads.append(t)
                t.start()
                # 错开启动时间，避免同时请求触发 IP 限流
                if i < num_workers - 1:
                    log(f"⏳ 等待 5 秒后启动下一个线程...")
                    time.sleep(5)
            
            # 等待所有线程完成
            for t in threads:
                t.join()
        else:
            # 串行模式（原有逻辑）
            pool = SmartAPIPool(max_rpm=200, max_rpm_per_key=3)
            
            for task in TRANSLATE_TASKS:
                source_path = DATA_DIR / task["source"]
                if not source_path.exists():
                    log(f"⚠️ 跳过不存在的文件: {task['source']}", "warning")
                    continue
                
                # 检查是否已完成（但如果有失败记录，仍需处理）
                with open(source_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                total = len(data.get(task["item_key"], []))
                done = progress.get(task["source"], 0)
                has_failed = len(failed.get(task["source"], [])) > 0
                
                if done >= total and not has_failed:
                    log(f"✅ 跳过已完成: {task['source']}")
                    continue
                
                translate_file(pool, task, progress, failed, global_stats, worker_id=0)
            
    except KeyboardInterrupt:
        log("\n⚠️ 用户中断，进度已保存", "warning")
        log(f"   进度文件: {PROGRESS_FILE}")
        log(f"   失败记录: {FAILED_FILE}")
    
    # 最终统计
    total_time = time.time() - global_stats["start_time"]
    final_failed = sum(len(v) for v in failed.values())
    log("\n" + "=" * 60)
    log("🏁 翻译任务结束")
    log(f"   完成: {global_stats['completed']}/{global_stats['total']}")
    log(f"   失败: {final_failed} 条（下次运行会自动重试）")
    log(f"   耗时: {total_time/60:.1f} 分钟")
    log("=" * 60)


def reset_progress():
    """重置所有进度"""
    import shutil
    
    log("🗑️ 重置翻译进度...")
    
    # 删除进度文件
    if PROGRESS_FILE.exists():
        os.remove(PROGRESS_FILE)
        log(f"   删除: {PROGRESS_FILE.name}")
    
    # 删除失败记录
    if FAILED_FILE.exists():
        os.remove(FAILED_FILE)
        log(f"   删除: {FAILED_FILE.name}")
    
    # 删除所有 *_cn.json 文件
    for task in TRANSLATE_TASKS:
        output_path = DATA_DIR / task["output"]
        if output_path.exists():
            os.remove(output_path)
            log(f"   删除: {task['output']}")
    
    # 删除 API 池状态
    state_file = Path(__file__).parent.parent / "api_pool_state.json"
    if state_file.exists():
        os.remove(state_file)
        log(f"   删除: api_pool_state.json")
    
    log("✅ 进度已重置，可以从头开始翻译")


def print_help():
    """打印帮助信息"""
    print("""
Dota2 API 文档批量翻译工具

用法:
  python translate_all.py [选项]

选项:
  (无参数)     串行模式，断点续传
  -p N         并行模式，N 个线程同时翻译（最多 4 个）
  --reset      重置所有进度，从头开始
  --status     只显示当前进度，不翻译
  --help       显示此帮助信息

示例:
  python translate_all.py           # 串行翻译
  python translate_all.py -p 4      # 4 线程并行翻译
  python translate_all.py --reset   # 从头开始
  python translate_all.py --status  # 查看进度

并行模式说明:
  - 每个线程使用独立的 API Key
  - 线程 1: gameevents
  - 线程 2: luaapi/classes + functions
  - 线程 3: luaapi/enums + constants
  - 线程 4: panoramaapi + panoramaevents
""")


def show_status():
    """只显示进度状态"""
    progress = load_progress()
    failed = load_failed()
    
    print("\n📋 翻译进度:")
    print("-" * 60)
    
    total_items = 0
    completed_items = 0
    total_failed = 0
    
    for task in TRANSLATE_TASKS:
        source_path = DATA_DIR / task["source"]
        if source_path.exists():
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            count = len(data.get(task["item_key"], []))
            done = progress.get(task["source"], 0)
            failed_count = len(failed.get(task["source"], []))
            total_items += count
            completed_items += done
            total_failed += failed_count
            
            pct = done * 100 // count if count > 0 else 0
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            status = "✅" if done >= count else "⏳"
            failed_str = f" ❌{failed_count}" if failed_count > 0 else ""
            
            print(f"{status} {task['source']}")
            print(f"   [{bar}] {done}/{count} ({pct}%){failed_str}")
    
    print("-" * 60)
    total_pct = completed_items * 100 // total_items if total_items > 0 else 0
    print(f"📊 总进度: {completed_items}/{total_items} ({total_pct}%)")
    if total_failed > 0:
        print(f"⚠️  待重试: {total_failed} 条")
    print()


if __name__ == "__main__":
    import sys
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
    elif "--reset" in sys.argv:
        confirm = input("⚠️ 确定要重置所有进度吗？这将删除所有翻译结果！(输入 yes 确认): ")
        if confirm.lower() == "yes":
            reset_progress()
        else:
            print("已取消")
    elif "--status" in sys.argv:
        show_status()
    elif "-p" in sys.argv:
        # 并行模式
        try:
            idx = sys.argv.index("-p")
            parallel = int(sys.argv[idx + 1])
            parallel = max(1, min(parallel, 4))  # 限制 1-4
            main(parallel=parallel)
        except (IndexError, ValueError):
            print("错误: -p 后面需要指定线程数，如 -p 4")
            print_help()
    else:
        main(parallel=1)
