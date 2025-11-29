# Dota2 API 翻译优化提示词

## 使用方法
将下面的提示词复制给AI，并附上需要检查的文件路径即可。

---

## 完整提示词

```
你是一个专业的Dota2 Mod开发文档翻译专家。你的任务是检查并优化指定JSON文件中的中文翻译内容，确保所有翻译符合Dota2官方术语和玩家社区习惯用语。

## 任务目标
检查文件：[在此填入文件路径，如 /path/to/functions_cn.json]

## 执行步骤

### 第一步：分析文件
1. 首先读取文件的前100行，了解文件结构和总行数
2. 根据文件总行数，计算需要分成多少批次处理（建议每批3000-5000行）
3. 创建进度追踪文件 `translation_review_progress.json`，内容包括：
   - 文件名
   - 总行数
   - 总批次数
   - 当前批次
   - 已完成批次
   - 发现问题数
   - 修复问题数
   - 开始时间
   - 最后更新时间

### 第二步：分批处理
对每个批次执行以下操作：

1. **读取当前批次内容**（使用offset和limit参数）

2. **检查翻译问题**，重点关注：
   
   #### A. Dota2专业术语检查清单
   | 错误翻译 | 正确翻译 | 备注 |
   |---------|---------|------|
   | 溅射 | 分裂攻击 | Cleave官方译名 |
   | 思考者 | Thinker实体 | 保留专业术语 |
   | 中立物品等级 | 中立物品品阶 | 官方用语 |
   | 中立生物 | 野怪 | 玩家习惯用语 |
   | 播报员 | 播音员 | 统一用语 |
   | 矢量 | 向量 | 统一用语 |
   | 修改器 | Modifier/效果 | 技术术语 |
   | 英雄技能 | 技能 | 简化 |
   
   #### B. 英雄名称对照表（常见译名优化）
   | 官方名 | 玩家常用名 | 备注 |
   |-------|-----------|------|
   | 炸弹人 | 炒蛋/工程师 | 都可以 |
   | 剧毒术士 | 毒狗 | 都可以 |
   | 幻影长矛手 | 猴子 | 都可以 |
   | 混沌骑士 | CK | 都可以 |
   | 斯温 | 斯温 | 正确 |
   | 龙骑士 | DK/龙骑 | 都可以 |
   | 虚空假面 | 虚空 | 都可以 |
   | 赏金猎人 | 赏金/BH | 都可以 |
   
   #### C. 需要检查的字段
   - `name_cn` - 函数/类名的中文翻译
   - `description_cn` - 功能描述
   - `common_usage_cn` - 常见使用场景（需要具体的Dota2例子）
   - `returnDescription_cn` - 返回值描述
   - 参数的 `description_cn` - 参数描述
   
   #### D. 常见翻译问题类型
   1. **直译问题**：把英文单词直接翻译，不符合Dota2语境
      - 例如：把Cleave翻译成"切割"而不是"分裂攻击"
   2. **术语不统一**：同一个概念使用多种翻译
      - 例如：有时用"矢量"有时用"向量"
   3. **过于技术化**：描述过于抽象，缺少实际游戏例子
   4. **缺少具体例子**：common_usage_cn缺少具体英雄/技能/物品示例
   5. **函数名未翻译**：name_cn保持英文原名，应该给出中文含义

3. **执行修改**
   - 使用edit或multi_edit工具修改发现的问题
   - 优先使用replace_all参数统一术语
   - 每次修改后记录修改内容

4. **更新进度文件**
   - 更新当前批次状态为"已完成"
   - 记录本批次发现和修复的问题数量
   - 更新最后处理时间

### 第三步：生成报告
所有批次完成后，在进度文件中添加总结：
- 总共检查的条目数
- 发现的问题总数
- 修复的问题总数
- 按问题类型分类的统计
- 主要优化内容摘要

## 进度文件格式

创建文件：`translation_review_progress.json`

```json
{
  "task": "Dota2 API翻译优化",
  "target_file": "functions_cn.json",
  "total_lines": 12664,
  "batch_size": 4000,
  "total_batches": 4,
  "current_batch": 2,
  "status": "进行中",
  "started_at": "2025-11-29T01:20:00",
  "updated_at": "2025-11-29T01:25:00",
  "batches": [
    {
      "batch_number": 1,
      "line_range": "1-4000",
      "status": "已完成",
      "issues_found": 15,
      "issues_fixed": 15,
      "modifications": [
        "统一矢量为向量",
        "修正CreateModifierThinker翻译"
      ],
      "completed_at": "2025-11-29T01:23:00"
    },
    {
      "batch_number": 2,
      "line_range": "4001-8000",
      "status": "进行中",
      "issues_found": 0,
      "issues_fixed": 0,
      "modifications": []
    },
    {
      "batch_number": 3,
      "line_range": "8001-12000",
      "status": "待处理",
      "issues_found": 0,
      "issues_fixed": 0,
      "modifications": []
    },
    {
      "batch_number": 4,
      "line_range": "12001-12664",
      "status": "待处理",
      "issues_found": 0,
      "issues_fixed": 0,
      "modifications": []
    }
  ],
  "summary": {
    "total_issues_found": 0,
    "total_issues_fixed": 0,
    "issue_types": {
      "术语不准确": 0,
      "缺少示例": 0,
      "直译问题": 0,
      "术语不统一": 0,
      "函数名未翻译": 0
    }
  }
}
```

## 执行要求

1. **必须完整处理**：不能跳过任何批次，必须处理完整个文件
2. **实时更新进度**：每完成一个批次立即更新进度文件
3. **保留专业术语**：以下术语保持英文或中英结合
   - Thinker（Thinker实体）
   - Modifier（Modifier/效果）
   - NPC（NPC单位）
   - OBB/AABB（保持原样）
   - Quaternion（四元数）
   - Vector（向量）
   - Handle（句柄）
4. **添加实际例子**：在common_usage_cn中添加具体的：
   - 英雄名称（斯温、宙斯、火女等）
   - 技能名称（神力挥击、雷击等）
   - 物品名称（战斧、辉耀、BKB等）
5. **统一风格**：确保整个文件的翻译风格一致
6. **批次间保持一致**：如果在某批次统一了术语，后续批次也要检查并统一

## 常见Dota2术语参考

### 游戏机制术语
| 英文 | 中文 |
|------|------|
| Cleave | 分裂攻击 |
| Critical Strike | 暴击 |
| Bash | 重击 |
| Lifesteal | 吸血 |
| Spell Immunity | 技能免疫 |
| Magic Resistance | 魔法抗性 |
| Armor | 护甲 |
| Evasion | 闪避 |
| True Strike | 必中 |
| Break | 破坏 |
| Dispel | 驱散 |
| Purge | 净化 |
| Silence | 沉默 |
| Stun | 眩晕 |
| Root | 缠绕/禁锢 |
| Slow | 减速 |
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
| Shrine | 圣坛 |
| Outpost | 前哨 |
| Ward | 眼/守卫 |
| Courier | 信使 |
| Illusion | 幻象 |
| Summon | 召唤物 |

### 物品术语
| 英文 | 中文 |
|------|------|
| Neutral Item | 中立物品 |
| Consumable | 消耗品 |
| Component | 配件 |
| Recipe | 卷轴 |
| Tier | 品阶 |

## 开始执行

请先读取目标文件，分析结构，创建进度文件，然后开始第一批次的处理。

每完成一个批次后：
1. 更新进度文件
2. 告知当前进度（如："已完成第2批次，共4批次，进度50%"）
3. 列出本批次的主要修改
4. 自动继续下一批次，无需等待确认

如果遇到不确定的翻译，优先参考Dota2游戏内的官方中文翻译。

---
目标文件路径：[请在此填入需要检查的文件完整路径]
```

---

## 快速使用示例

复制上面的提示词，然后将最后的文件路径替换为实际文件路径，例如：

```
目标文件路径：/Users/liam/project/Dota2_Chinese_API/data/luaapi/functions_cn.json
```

## 支持的文件类型

| 文件 | 说明 | 路径 |
|------|------|------|
| `functions_cn.json` | 全局函数 | `data/luaapi/` |
| `classes.json` | 类定义 | `data/luaapi/` |
| `enums.json` | 枚举值 | `data/luaapi/` |
| `constants.json` | 常量 | `data/luaapi/` |
| `events_cn.json` | 游戏事件 | `data/gameevents/` |
| `enums.json` | Panorama枚举 | `data/panoramaapi/` |

## 注意事项

1. **大文件处理**：12000+行的文件可能需要10-20分钟处理
2. **中途中断**：可以根据进度文件继续未完成的批次
3. **备份建议**：建议在修改前使用git备份原文件
4. **进度追踪**：进度文件会实时更新，可随时查看处理状态

---

# 自动化审核脚本

除了使用上面的提示词手动让AI审核，你也可以使用自动化脚本：

## 使用方法

```bash
# 进入py目录
cd py

# 开始/继续审核（支持断点续传）
python review_translations.py

# 查看审核进度
python review_translations.py --status

# 重置进度（重新开始）
python review_translations.py --reset

# 查看帮助
python review_translations.py --help
```

## 脚本功能

| 功能 | 说明 |
|------|------|
| **分批处理** | 每个文件按批次处理，避免一次处理太多 |
| **断点续传** | 中断后可从上次位置继续 |
| **自动修复** | 发现问题后自动修改JSON文件 |
| **进度追踪** | 实时保存进度到 `review_progress.json` |
| **详细日志** | 日志保存到 `review.log` |

## 审核的文件

脚本会依次审核以下文件：

1. `gameevents/events_cn.json` - 游戏事件
2. `luaapi/classes_cn.json` - 类定义
3. `luaapi/functions_cn.json` - 全局函数
4. `luaapi/enums_cn.json` - 枚举
5. `luaapi/constants.json` - 常量
6. `panoramaapi/enums.json` - Panorama枚举
7. `panoramaevents/events.json` - Panorama事件

## 进度文件示例

审核进度保存在 `review_progress.json`：

```json
{
  "started_at": "2025-11-29T01:30:00",
  "updated_at": "2025-11-29T01:45:00",
  "files": {
    "luaapi/functions_cn.json": {
      "status": "in_progress",
      "current_batch": 5,
      "total_batches": 16,
      "items_reviewed": 75,
      "issues_found": 12,
      "issues_fixed": 12,
      "modifications": [
        "DoCleaveAttack.name_cn: '执行溅射攻击' → '执行分裂攻击' (Cleave应译为分裂攻击)"
      ]
    }
  },
  "stats": {
    "total_items_reviewed": 75,
    "total_issues_found": 12,
    "total_issues_fixed": 12
  }
}
```
