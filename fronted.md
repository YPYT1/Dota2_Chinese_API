# Dota2 中文 API 文档网站 - 前端开发规范

## 项目概述

构建一个现代化的 Dota2 中文 API 文档网站，提供 Lua API 和 Panorama API 的完整中文文档查询功能。


我想要苹果的风格:
好的，我给你 **“苹果官网 Apple.com 风格”** 的 **高级极简配色方案 + 设计语言（Design System）**。
这是目前最干净、最高级、最有质感的风格之一，非常适合你的“简约 API 网站”。

---

# 🍎 **Apple 官网风格高级配色方案（Apple Design System）**

苹果的设计关键不是颜色多，而是：

### **① 大量留白（White Space）**

### **② 极轻边框（0.5px hairline）**

### **③ 高级灰（不使用纯黑/纯白）**

### **④ 跨设备统一的中性色**

以下是 *高度复刻 Apple 风格* 的配色表：

---

# 🎨 **Apple-style 色板（Light Theme）**

### **主背景 Background**

* **#F5F5F7**（Apple Light Grey — 苹果官网底色）
* **#FFFFFF**（内容区卡片）

### **主文本 Primary Text**

* **#1D1D1F**（Apple Graphite 黑灰，不刺眼）

### **副文本 Secondary Text**

* **#6E6E73**（苹果网页常用的次级文字颜色）

### **边框 Border（极轻）**

* **#D2D2D7**（Apple Hairline Border）

### **主色 Primary（蓝色按钮、链接）**

* **#0071E3**（Apple 蓝）

### **强调色 Accent**

* 成功：**#34C759**（Apple Green）
* 警告：**#FF9500**
* 错误：**#FF3B30**

---

# 🌑 **Apple Dark Theme（可选深色）**

### 背景

* **#000000**
* **#1C1C1E**

### 文字

* 主文字：**#FFFFFF**
* 次文字：**#8E8E93**

### 边框

* **#2C2C2E**

### 蓝色主色

* **#0A84FF**

---

# 🍎 **Apple 风格的 UI 特征（你做网站必须遵守这些）**

### ✔ 1. 大量留白

* Apple 网站通常左右留白 **24–80px**
* 组件间距大、呼吸感强

### ✔ 2. 字体非常重要

使用系统字体栈：

```
font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", sans-serif;
```

### ✔ 3. 轻边框 vs 无边框

* 卡片基本不加边框
* 若必须加边框 → **只有 0.5px 的超轻边**

### ✔ 4. 微妙阴影（不明显）

Apple 不用浓阴影，示例：

```
box-shadow: 0 2px 6px rgba(0,0,0,0.04);
```

### ✔ 5. 按钮用 Apple 蓝

按钮圆角小、简洁：

```
background: #0071E3;
border-radius: 8px;
padding: 12px 22px;
font-weight: 500;
color: white;
```

---

# 🧱 **完整 Tailwind 配色（可直接复制到项目）**

```js
theme: {
  extend: {
    colors: {
      apple: {
        bg: '#F5F5F7',
        card: '#FFFFFF',
        text: '#1D1D1F',
        textSecondary: '#6E6E73',
        border: '#D2D2D7',
        blue: '#0071E3',
        green: '#34C759',
        orange: '#FF9500',
        red: '#FF3B30',
      }
    }
  }
}
```


## 技术栈

- **框架**: Next.js 16.0.5 (App Router)
- **UI 组件库**: shadcn/ui
- **样式**: Tailwind CSS 4
- **动画**: Motion (framer-motion)
- **国际化**: next-intl
- **部署**: Cloudflare Pages
- **包管理**: pnpm

## 数据源文件

```
data/
├── gameevents/
│   └── events_cn.json          # 游戏事件数据
├── luaapi/
│   ├── classes_cn.json         # Lua 类数据
│   ├── constants.json          # Lua 常量数据
│   ├── enums_cn.json           # Lua 枚举数据
│   └── functions_cn.json       # Lua 函数数据
├── panoramaapi/
│   └── enums.json              # Panorama 枚举数据
└── panoramaevents/
    └── events.json             # Panorama 事件数据
```

## 页面结构

### 顶部导航 (4个主要模块)

1. **Lua API** (`/lua-api`)
   - 子分类:
     - Classes (类) - 数据源: `classes_cn.json`
     - Functions (函数) - 数据源: `functions_cn.json`
     - Constants (常量) - 数据源: `constants.json`
     - Enums (枚举) - 数据源: `enums_cn.json`

2. **Game Events** (`/game-events`)
   - 数据源: `events_cn.json`

3. **Panorama API** (`/panorama-api`)
   - 数据源: `enums.json`

4. **Panorama Events** (`/panorama-events`)
   - 数据源: `events.json`

## 设计规范

### 整体风格

- **设计理念**: 简洁、现代、高级感
- **配色方案**: 
  - 避免过重的颜色
  - 使用柔和的渐变和中性色调
  - 主色调建议: 深蓝灰 (#1e293b) / 浅灰白 (#f8fafc)
  - 强调色: 柔和的蓝色 (#3b82f6) 或紫色 (#8b5cf6)

### 主题模式

- 支持 **亮色模式** (Light Mode)
- 支持 **暗色模式** (Dark Mode)
- 使用 `next-themes` 实现主题切换
- 默认跟随系统设置

### 布局结构

```
┌─────────────────────────────────────────────────────────┐
│  Logo    [Lua API] [Game Events] [Panorama API] [Panorama Events]   [Global Seach]│  ← 顶部导航
│                                        🌙/☀️  🌐 i18n   │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌─────────────────────────────────────┐  │
│  │          │  │                                     │  │
│  │  侧边栏   │  │           主内容区域                 │  │
│  │  (分类)   │  │                                     │  │
│  │          │  │                                     │  │
│  └──────────┘  └─────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│              Design by LiamWang © 2025                  │  ← 页脚
└─────────────────────────────────────────────────────────┘
```

### 类型图标 SVG 设计

为不同类型的 API 元素设计统一风格的 SVG 图标:

#### 1. Class (类) 图标
```svg
你自己设计
```
- 含义: 矩形框代表类的封装性，内部线条代表属性和方法

#### 2. Function (函数) 图标
```svg
你自己设计
```
- 含义: 花括号形状，代表函数定义

#### 3. Constant (常量) 图标
```svg
你自己设计
```
- 含义: 圆形代表固定不变，指针代表固定值

#### 4. Enum (枚举) 图标
```svg
你自己设计
```
- 含义: 多个方块代表枚举的多个选项

#### 5. Event (事件) 图标
```svg
你自己设计
```
- 含义: 闪电形状，代表事件触发

### 动画效果

使用 Motion 库实现以下动画:

1. **页面切换**: 淡入淡出 + 轻微位移
2. **列表项**: 交错进入动画 (stagger)
3. **卡片悬停**: 轻微上浮 + 阴影增强
4. **侧边栏展开/收起**: 平滑过渡
5. **搜索结果**: 淡入动画

```tsx
// 示例动画配置
你自己设计
```

### 页脚设计

```tsx
// 页脚样式参考
你自己设计
```

## 功能需求

### 核心功能

1. **搜索功能**
   - 全局搜索 (Cmd/Ctrl + K)（方法名，函数名，类名，常量名，值等所有的都要支持可以搜索到，在各个页面下，在各个页面下只能搜索到各个页面下的，但是在global可以搜索到全部的，)
   - 支持模糊匹配
   - 搜索结果高亮
   - 搜索历史记录

2. **侧边栏导航**
   - 分类列表
   - 可折叠/展开
   - 当前位置高亮
   - 滚动时固定

3. **内容展示**
   - 代码语法高亮 (使用 shiki 或 prism)
   - 参数表格展示
   - 返回值说明
   - 相关链接 (GitHub/Google 搜索)


### 数据展示格式

#### 类 (Class) 展示
```
┌─────────────────────────────────────────┐
│ 🔷 CDOTA_BaseNPC                        │
│ 基础NPC类                                │
├─────────────────────────────────────────┤
│ 方法列表:                                │
│ ├─ GetHealth() → int                    │
│ │  获取当前生命值                         │
│ ├─ SetHealth(health: int) → void        │
│ │  设置生命值                            │
│ └─ ...                                  │
└─────────────────────────────────────────┘
```

#### 函数 (Function) 展示
```
┌─────────────────────────────────────────┐
│ ⚡ CreateUnitByName                      │
│ 通过名称创建单位                          │
├─────────────────────────────────────────┤
│ 参数:                                    │
│ ┌────────────┬────────┬───────────────┐ │
│ │ 参数名      │ 类型    │ 说明          │ │
│ ├────────────┼────────┼───────────────┤ │
│ │ unitName   │ string │ 单位名称       │ │
│ │ location   │ Vector │ 生成位置       │ │
│ └────────────┴────────┴───────────────┘ │
│ 返回值: handle (单位句柄)                 │
└─────────────────────────────────────────┘
```

#### 枚举 (Enum) 展示
```
┌─────────────────────────────────────────┐
│ 📦 DOTA_TEAM                            │
│ 队伍类型                                 │
├─────────────────────────────────────────┤
│ 成员:                                    │
│ ├─ DOTA_TEAM_GOODGUYS = 2  // 天辉      │
│ ├─ DOTA_TEAM_BADGUYS = 3   // 夜魇      │
│ └─ DOTA_TEAM_NEUTRALS = 4  // 野怪      │
└─────────────────────────────────────────┘
```

## 项目结构
你自己进行设计这个项目data目录就在那里

## Cloudflare Pages 部署配置

### next.config.js
```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // 静态导出
  images: {
    unoptimized: true
  },
  trailingSlash: true
}

module.exports = nextConfig
```

### 部署步骤
1. 推送代码到 GitHub
2. 在 Cloudflare Pages 创建新项目
3. 连接 GitHub 仓库
4. 构建设置:
   - 构建命令: `pnpm build`
   - 输出目录: `out`
   - Node 版本: 18+

## 响应式设计

- **桌面端** (>= 1024px): 完整侧边栏 + 主内容
- **平板端** (768px - 1023px): 可收起侧边栏
- **移动端** (< 768px): 汉堡菜单 + 全屏导航

## 性能优化

1. **静态生成**: 所有页面预渲染
2. **代码分割**: 按路由自动分割
3. **图片优化**: 使用 Next.js Image 组件
4. **字体优化**: 使用 next/font 加载字体
5. **缓存策略**: 利用 Cloudflare CDN

## SEO 优化

1. 每个页面设置独立的 title 和 description
2. 生成 sitemap.xml
3. 添加 robots.txt
4. 使用语义化 HTML 标签
5. 添加 Open Graph 标签

## 开发命令

```bash
# 安装依赖
pnpm install

# 开发模式
pnpm dev

# 构建
pnpm build

# 预览构建结果
pnpm start

# 代码检查
pnpm lint
```

## 颜色变量参考

```css
/* 亮色主题 */
你自己设计两个主题

---

## 注意事项

1. 所有数据从 `data/` 目录的 JSON 文件读取
2. 确保 JSON 文件在构建时被正确引入
3. 搜索功能需要在客户端实现 (use client)
4. 主题切换需要处理 hydration 问题
5. i18n 路由使用 `[locale]` 动态段

---

*文档版本: 1.0*
*最后更新: 2025-11-29*
