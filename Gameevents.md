# Game Events 爬取流程

## 数据来源
- **网站**: https://moddota.com/api/#!/events

---

## 步骤一：拼接地址

根路径为 `https://moddota.com/api/#!/events`，通过选择器 `a.Sidebar__SidebarLink-kKnkkd` 找到所有侧边栏链接，提取其 `href` 属性（如 `#!/events/dota_player_kill`），然后拼接根路径得到完整地址。

**示例**：
- href: `#!/events/dota_illusions_created`
- 完整地址: `https://moddota.com/api/#!/events/dota_illusions_created`

**注意**：部分事件带有 ⭐ 标记，表示该事件对自定义游戏有用，需要提取这个标记。

---

## 步骤二：提取页面信息

### 页面结构

Game Events 页面结构比较简单，每个事件页面只有一种类型。

---

### 事件提取规则

**事件容器**：`div[class*="FunctionDeclaration__FunctionWrapper"]`，事件名从 `id` 属性获取

**事件签名**：`div[class*="FunctionDeclaration__FunctionSignature"]`

**参数提取**：`span[class*="types__FunctionParameterWrapper"]`
- 参数名：第一个 `span` 的文本（去掉 `:` 后缀）
- 参数类型：`span[class*="types__TypeSpan"]` 的文本
- 常见类型：`EntityIndex`, `PlayerID`, `short`, `long`, `int`, `byte`, `bool`, `string`, `float`

**参数描述（有的事件有有的事件没有）**：`li[class*="FunctionDeclaration__ParameterDescription"]`
- 参数名：`span[class*="FunctionDeclaration__ParameterDescriptionName"]` 的文本
- 描述：`: ` 后面的文本

**事件描述（有的事件有有的事件没有）**：`div[class*="styles__Description"]` 内除了参数描述列表外的文本

**返回值**：通常为 `void`

**是否推荐（有的事件有有的事件没有）**：侧边栏链接中的 `span[title="This event is useful for custom games"]` 带有 ⭐

**GitHub链接**：`a[title="Search on GitHub"]`

**Google链接**：`a[title="Search on Google"]`

**锚点链接**：`a[class*="ElementLink__StyledElementLink"]`

---

### 三种页面结构示例

| 事件 | 参数描述 | 事件描述 |
|------|---------|---------|
| `player_chat` | ✅ 有 | ✅ 有 "A public player chat." |
| `chat_members_changed` | ❌ 无 | ✅ 有 "The specified channel has had..." |
| `dota_npc_goal_reached` | ✅ 有 | ❌ 无 |

---

## JSON 输出格式

```json
{
  "metadata": {
    "type": "gameevents",
    "source": "https://moddota.com/api/#!/events",
    "crawledAt": "2024-11-28T00:00:00Z",
    "count": 0
  },
  "items": [
    {
      // ========== 原始字段 ==========
      "name": "player_chat",
      "signature": "player_chat(teamonly: bool, userid: EntityIndex, playerid: PlayerID, text: string): void",
      "description": "A public player chat.",
      "parameters": [
        {
          "name": "teamonly",
          "type": "bool",
          "description": "True if team only chat.",
          // 中文化字段
          "description_cn": "",
          "type_description_cn": ""
        },
        {
          "name": "userid",
          "type": "EntityIndex",
          "description": "Chatting player.",
          "description_cn": "",
          "type_description_cn": ""
        },
        {
          "name": "playerid",
          "type": "PlayerID",
          "description": "Chatting player ID.",
          "description_cn": "",
          "type_description_cn": ""
        },
        {
          "name": "text",
          "type": "string",
          "description": "Chat text.",
          "description_cn": "",
          "type_description_cn": ""
        }
      ],
      "returnType": "void",
      "isRecommended": true,
      "githubLink": "https://github.com/search?l=Lua&q=player_chat...",
      "googleLink": "https://www.google.com/search?q=...",
      "link": "#!/events/player_chat",
      
      // ========== 中文化字段 ==========
      "name_cn": "",
      "description_cn": "",
      "example_ts": "",
      "notes_cn": "",
      "common_usage_cn": "",
      "related": [],
      "see_also": [],
      "tags": []
    }
  ]
}
```

**字段说明：**
- `description`: 事件描述（有的事件有有的事件没有）
- `parameters[].description`: 参数描述（有的事件有有的事件没有）
- `isRecommended`: 是否带 ⭐ 标记

---

## CSS 选择器速查表

```css
/* === 侧边栏链接 === */
a.Sidebar__SidebarLink-kKnkkd                          /* 事件链接 */
span[title="This event is useful for custom games"]    /* 推荐标记 ⭐ */

/* === 事件容器 === */
div[class*="FunctionDeclaration__FunctionWrapper"]     /* 事件容器, id=事件名 */
div[class*="FunctionDeclaration__FunctionSignature"]   /* 签名容器 */

/* === 参数相关 === */
span[class*="types__FunctionParameterWrapper"]         /* 参数包装 */
span[class*="types__TypeSpan"]                         /* 参数类型 */

/* === 描述相关 === */
div[class*="styles__Description"]                      /* 描述区域 */
li[class*="FunctionDeclaration__ParameterDescription"] /* 参数描述 */
span[class*="FunctionDeclaration__ParameterDescriptionName"]  /* 参数描述名 */

/* === 链接 === */
a[title="Search on GitHub"]                            /* GitHub 搜索 */
a[title="Search on Google"]                            /* Google 搜索 */
a[class*="ElementLink__StyledElementLink"]             /* 锚点链接 */
```

---

## 输出文件

```
data/gameevents/
└── events.json    # 所有游戏事件
```