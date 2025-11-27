# Dota2 Lua API 页面结构分析

## 数据来源
- **网站**: https://moddota.com/api/#!/vscripts/

---

## 一、页面整体结构

### 1. 顶层容器
```html
<main class="Content__ContentWrapper-hreHLK ikDLQi">
  <div class="Search__SearchBoxWrapper-fAhBrj">...</div>  <!-- 搜索框 -->
  <div style="flex: 1 1 0%; overflow: hidden scroll;">    <!-- 内容区域 -->
    <div class="Content__ListItem-cTVUVP cGougT">         <!-- 列表项容器 -->
      ...
    </div>
  </div>
</main>
```

---

## 二、类/接口声明结构 (Class Declaration)

### 关键CSS类
| CSS类名 | 用途 |
|---------|------|
| `ClassDeclaration__ClassWrapper-jdNVGi` | 类的外层包装器 |
| `ClassDeclaration__ClassName-dQXDbO gNJGnf` | **类名** (如 `CDOTA_BaseNPC`, `Vector`) |
| `ClassDeclaration__ClassExtendsWrapper-fDQCJr` | 继承关系包装器 |
| `ClassDeclaration__ClassMembers-gBDXje` | 类成员列表容器 |

### 结构示例
```html
<div class="styles__CommonGroupWrapper-hQAAsg ClassDeclaration__ClassWrapper-jdNVGi kXIowE">
  <div class="styles__CommonGroupHeader-dUnrnU ClassDeclaration__ClassHeader-gebJti">
    <div class="styles__CommonGroupSignature-gODApT flitrE">
      <svg>...</svg>  <!-- 图标 -->
      <span class="ClassDeclaration__ClassName-dQXDbO gNJGnf">类名</span>
      <span class="ClassDeclaration__ClassExtendsWrapper-fDQCJr">
        extends <a class="types__TypeReferenceLink-bpPxLF kDAZjj" href="#!/vscripts/父类">父类</a>
      </span>
    </div>
    <div class="styles__ElementBadges-frIvDt">...</div>  <!-- 徽章区域 -->
  </div>
  <div class="styles__Description-enGWpD">类描述</div>
  <div class="ClassDeclaration__ClassMembers-gBDXje">
    <!-- 类成员(方法/字段)列表 -->
  </div>
</div>
```

---

## 三、方法/函数声明结构 (Function Declaration)

### 关键CSS类
| CSS类名 | 用途 |
|---------|------|
| `FunctionDeclaration__FunctionWrapper-gYcoXK` | 函数外层包装器，**id属性=方法名** |
| `FunctionDeclaration__FunctionSignature-eAuxgh` | 函数签名区域 |
| `styles__CommonGroupSignature-gODApT` | 通用签名容器 |

### 结构示例
```html
<div class="styles__CommonGroupWrapper-hQAAsg FunctionDeclaration__FunctionWrapper-gYcoXK" id="方法名">
  <div class="styles__CommonGroupHeader-dUnrnU">
    <div class="styles__CommonGroupSignature-gODApT FunctionDeclaration__FunctionSignature-eAuxgh">
      <svg>...</svg>  <!-- 图标 -->
      方法名(参数列表): 返回值类型
    </div>
    <div class="styles__ElementBadges-frIvDt">
      <div class="AvailabilityBadge__AvailabilityBadgeBox-jsLhaU" title="Available on server-side Lua">s</div>
      <div class="AvailabilityBadge__AvailabilityBadgeBox-jsLhaU" title="Available on client-side Lua">c</div>
      <!-- GitHub搜索链接等 -->
    </div>
  </div>
  <div class="styles__Description-enGWpD">方法描述</div>
</div>
```

### 参数结构
```html
<span class="types__FunctionParameterWrapper-bUssSi fapRVj">
  <span style="color: rgb(11, 88, 114);">参数名</span>:&nbsp;
  <span class="types__TypeSpan-bcJynW fAGQXw">
    <span style="color: rgb(17, 110, 81);">参数类型</span>
  </span>
</span>
```

### 返回值结构
**普通类型:**
```html
<span class="types__TypeSpan-bcJynW fAGQXw">
  <span style="color: rgb(117, 42, 126);">nil</span>
</span>
```

**引用类型(带链接):**
```html
<a class="types__TypeReferenceLink-bpPxLF kDAZjj" href="#!/vscripts/Vector">
  <span style="color: rgb(17, 110, 81);">Vector</span>
</a>
```

---

## 四、字段声明结构 (Field Declaration)

### 关键CSS类
| CSS类名 | 用途 |
|---------|------|
| `Field__FieldWrapper-TgvHu` | 字段外层包装器，**id属性=字段名** |
| `Field__FieldSignature-septJ` | 字段签名区域 |

### 结构示例
```html
<div class="styles__CommonGroupWrapper-hQAAsg Field__FieldWrapper-TgvHu" id="x">
  <div class="styles__CommonGroupHeader-dUnrnU">
    <div class="styles__CommonGroupSignature-gODApT Field__FieldSignature-septJ">
      <svg>...</svg>
      x: <span class="types__TypeSpan-bcJynW">float</span>
    </div>
  </div>
</div>
```

---

## 五、枚举常量结构 (Enum Declaration)

### 关键CSS类
| CSS类名 | 用途 |
|---------|------|
| `Enum__EnumHeader-eIZJUS` | 枚举头部 |
| `Enum__EnumMemberWrapper-gHjqxK` | 枚举成员包装器，**id属性=枚举值名** |
| `Enum__EnumMemberSignature-hsNgBm` | 枚举成员签名 |

### 结构示例
```html
<div class="styles__CommonGroupWrapper-hQAAsg kXIowE">
  <div class="styles__CommonGroupHeader-dUnrnU Enum__EnumHeader-eIZJUS">
    <div class="styles__CommonGroupSignature-gODApT flitrE">
      <svg>...</svg>
      EDOTA_ModifyGold_Reason  <!-- 枚举类型名 -->
    </div>
  </div>
  <div class="styles__CommonGroupMembers-gMkGvA">
    <div class="Enum__EnumMemberWrapper-gHjqxK" id="DOTA_ModifyGold_Unspecified">
      <div class="Enum__EnumMemberSignature-hsNgBm">
        DOTA_ModifyGold_Unspecified = 0  <!-- 枚举值 -->
      </div>
    </div>
    <!-- 更多枚举成员 -->
  </div>
</div>
```

---

## 六、通用元素

### 徽章区域 (Badges)
```html
<div class="styles__ElementBadges-frIvDt dJwWYO">
  <!-- 服务端可用标记 -->
  <div class="AvailabilityBadge__AvailabilityBadgeBox-jsLhaU cNUzWe" title="Available on server-side Lua">s</div>
  <!-- 客户端可用标记 -->
  <div class="AvailabilityBadge__AvailabilityBadgeBox-jsLhaU cXPKXg" title="Available on client-side Lua">c</div>
  <!-- 引用计数链接 -->
  <a class="ReferencesLink__StyledReferencesLink-jKYjcG" href="#!/vscripts?search=...">N references</a>
  <!-- 锚点链接 -->
  <a class="ElementLink__StyledElementLink-fBvRBm" href="#!/vscripts/XXX">#</a>
  <!-- GitHub搜索链接 -->
  <a class="components__SearchWrapper-fJLHg" href="https://github.com/search?...">...</a>
</div>
```

### 描述区域
```html
<div class="styles__Description-enGWpD iGrEG">描述文本</div>
```

---

## 七、类型系统总结

| CSS类 | 说明 | 示例 |
|-------|------|------|
| `types__TypeSpan-bcJynW fAGQXw` | 基础类型 | `int`, `float`, `nil`, `bool`, `string` |
| `types__TypeReferenceLink-bpPxLF kDAZjj` | 引用类型(带链接) | `Vector`, `CBaseEntity`, `handle` |
| `types__FunctionParameterWrapper-bUssSi` | 参数包装器 | 包含参数名和类型 |

---

## 八、数据提取要点

### 需要提取的字段

#### 类(Class)
- **类名**: `ClassDeclaration__ClassName-dQXDbO`
- **父类**: `ClassDeclaration__ClassExtendsWrapper-fDQCJr` 下的 `types__TypeReferenceLink-bpPxLF`
- **描述**: `styles__Description-enGWpD`
- **成员列表**: `ClassDeclaration__ClassMembers-gBDXje`

#### 方法(Function)
- **方法名**: `FunctionDeclaration__FunctionWrapper-gYcoXK` 的 `id` 属性
- **参数**: `types__FunctionParameterWrapper-bUssSi` 内
  - 参数名: 第一个 `span`
  - 参数类型: `types__TypeSpan-bcJynW` 或 `types__TypeReferenceLink-bpPxLF`
- **返回值类型**: 签名末尾的 `types__TypeSpan-bcJynW` 或 `types__TypeReferenceLink-bpPxLF`
- **可用性**: `AvailabilityBadge__AvailabilityBadgeBox-jsLhaU` (s=服务端, c=客户端)
- **描述**: `styles__Description-enGWpD`

#### 字段(Field)
- **字段名**: `Field__FieldWrapper-TgvHu` 的 `id` 属性
- **字段类型**: `types__TypeSpan-bcJynW`

#### 枚举(Enum)
- **枚举类型名**: `Enum__EnumHeader-eIZJUS` 下的签名文本
- **枚举成员**: `Enum__EnumMemberWrapper-gHjqxK` 的 `id` 属性
- **枚举值**: `Enum__EnumMemberSignature-hsNgBm` 内文本

---

## 九、现有文件对应关系

| 文件 | 内容类型 |
|------|----------|
| `luaapi.html` | 类和方法 (如 `CDOTA_BaseNPC`) |
| `其他.html` | 特殊类型类 (如 `Vector`) |
| `常量.html` | 枚举常量第一部分 |
| `常量2.html` | 枚举常量第二部分 |

---

## 十、完整爬取规范

### 10.1 需要爬取的完整字段清单

#### 类(Class)
| 字段 | 必须 | 说明 |
|------|------|------|
| name | ✅ | 类名 |
| extends | ❌ | 父类名 |
| extendsLink | ❌ | 父类链接 |
| description | ❌ | 类描述 |
| references | ✅ | 引用数量 |
| server | ✅ | 服务端是否可用 |
| client | ✅ | 客户端是否可用 |
| link | ✅ | 锚点链接 |
| methods | ✅ | 方法列表 |
| fields | ❌ | 字段列表 |

#### 方法(Method)
| 字段 | 必须 | 说明 |
|------|------|------|
| name | ✅ | 方法名 (从id属性获取) |
| parameters | ✅ | 参数列表 |
| returnType | ✅ | 返回值类型 |
| returnTypeLink | ❌ | 返回值类型链接 |
| description | ❌ | 方法描述 |
| server | ✅ | 服务端是否可用 |
| client | ✅ | 客户端是否可用 |

#### 参数(Parameter)
| 字段 | 必须 | 说明 |
|------|------|------|
| name | ✅ | 参数名 |
| type | ✅ | 参数类型 |
| typeLink | ❌ | 类型链接(引用类型) |

#### 枚举(Enum)
| 字段 | 必须 | 说明 |
|------|------|------|
| name | ✅ | 枚举类型名 |
| description | ❌ | 枚举描述 |
| references | ✅ | 引用数量 |
| link | ✅ | 锚点链接 |
| members | ✅ | 成员列表 |

#### 枚举成员(EnumMember)
| 字段 | 必须 | 说明 |
|------|------|------|
| name | ✅ | 成员名 |
| value | ✅ | 成员值 |
| description | ❌ | 成员描述 |

---

### 10.2 CSS选择器速查表

```css
/* === 类相关 === */
.ClassDeclaration__ClassWrapper-jdNVGi          /* 类容器 */
.ClassDeclaration__ClassName-dQXDbO             /* 类名 */
.ClassDeclaration__ClassExtendsWrapper-fDQCJr   /* 继承关系 */
.ClassDeclaration__ClassMembers-gBDXje          /* 成员列表 */

/* === 方法相关 === */
.FunctionDeclaration__FunctionWrapper-gYcoXK    /* 方法容器, id=方法名 */
.FunctionDeclaration__FunctionSignature-eAuxgh  /* 方法签名 */

/* === 字段相关 === */
.Field__FieldWrapper-TgvHu                      /* 字段容器, id=字段名 */
.Field__FieldSignature-septJ                    /* 字段签名 */

/* === 枚举相关 === */
.Enum__EnumHeader-eIZJUS                        /* 枚举头部 */
.Enum__EnumMembers-jEmcJm                       /* 枚举成员列表 */
.Enum__EnumMemberWrapper-kSZNPe                 /* 枚举成员容器 */

/* === 类型相关 === */
.types__FunctionParameterWrapper-bUssSi         /* 参数包装 */
.types__TypeSpan-bcJynW                         /* 基础类型 */
a.types__TypeReferenceLink-bpPxLF               /* 引用类型(带链接) */

/* === 通用元素 === */
.styles__CommonGroupWrapper-hQAAsg              /* 通用包装器 */
.styles__CommonGroupSignature-gODApT            /* 通用签名 */
.styles__Description-enGWpD                     /* 描述文本 */
.styles__ElementBadges-frIvDt                   /* 徽章区域 */

/* === 可用性标记 === */
.AvailabilityBadge__AvailabilityBadgeBox-jsLhaU.cNUzWe  /* 服务端可用 */
.AvailabilityBadge__AvailabilityBadgeBox-jsLhaU.UnwH    /* 服务端不可用 */
.AvailabilityBadge__AvailabilityBadgeBox-jsLhaU.cXPKXg  /* 客户端可用 */
.AvailabilityBadge__AvailabilityBadgeBox-jsLhaU.tpxgF   /* 客户端不可用 */

/* === 链接相关 === */
.ReferencesLink__StyledReferencesLink-jKYjcG    /* 引用数链接 */
.ElementLink__StyledElementLink-fBvRBm          /* 锚点链接 */
a.components__SearchWrapper-fJLHg               /* 搜索链接 */
```

---

### 10.3 JSON输出格式示例

```json
{
  "classes": [{
    "name": "CDOTAPlayerController",
    "extends": "CBaseAnimatingActivity",
    "extendsLink": "#!/vscripts/CBaseAnimatingActivity",
    "description": "",
    "references": 9,
    "server": true,
    "client": true,
    "link": "#!/vscripts/CDOTAPlayerController",
    "methods": [{
      "name": "GetAssignedHero",
      "parameters": [],
      "returnType": "CDOTA_BaseNPC_Hero",
      "returnTypeLink": "#!/vscripts/CDOTA_BaseNPC_Hero",
      "description": "Get the player's hero.",
      "server": true,
      "client": false
    }]
  }],
  "enums": [{
    "name": "DOTALimits_t",
    "description": "",
    "references": 0,
    "link": "#!/vscripts/DOTALimits_t",
    "members": [{
      "name": "DOTA_DEFAULT_MAX_TEAM",
      "value": 5,
      "description": "Default number of players per team."
    }]
  }]
}
```

---

### 10.4 可用性判断规则

| 徽章类名 | title属性 | 含义 |
|----------|-----------|------|
| `cNUzWe` | "Available on server-side Lua" | 服务端✅可用 |
| `UnwH` | "Unavailable on server-side Lua" | 服务端❌不可用 |
| `cXPKXg` | "Available on client-side Lua" | 客户端✅可用 |
| `tpxgF` | "Unavailable on client-side Lua" | 客户端❌不可用 |

---

### 10.5 特殊情况处理

1. **枚举成员描述**: 可能有也可能没有(如 `DOTALimits_t` 有, `SourceEngineAnimationEvent` 无)
2. **枚举类型描述**: 可能是链接文本(如 `https://developer.valvesoftware.com/wiki/...`)
3. **返回值类型**: 签名中 `):` 后面的部分
4. **多参数**: 用逗号 `, ` 分隔

---

## 十一、缺失内容 (待补充)

1. **全局函数** - 不属于任何类的独立函数
2. **完整的类型定义** - 如 `QAngle`, `Quaternion` 等
3. **接口定义** - 如果有的话
4. **事件/回调定义** - 游戏事件相关


luaapi
类名:
类名:
class="ClassDeclaration__ClassName-dQXDbO gNJGnf"
完整的标签:<span class="ClassDeclaration__ClassName-dQXDbO gNJGnf">CDOTA_Ability_Aghanim_Spear</span>

