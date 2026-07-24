# AI Context Manager

> 让 AI 编程助手"像调用函数一样使用模块"——不再每次逆向工程整个代码库

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange)](https://github.com/KaiDev-dev/ai-context)
[![Lang](https://img.shields.io/badge/README-EN-blue)](README.md)
[![Website](https://img.shields.io/badge/website-aicodingdir.com-blue)](https://aicodingdir.com/tools/ai-context/)

---

> **已被 [AICoding](https://aicodingdir.com) 收录 — [产品页面](https://aicodingdir.com/tools/ai-context/) · [深度文章：模块契约模式](https://aicodingdir.com/blog/module-contract-pattern-ai-coding-2026/)**

## 问题

用 AI 写项目的人都有这个体验：

- **前期**：爽，改一个文件就搞定，token 消耗几百
- **中期**：还行，每次读 5-10 个文件，token 消耗 5K 左右
- **后期**：崩溃，改个支付功能，AI 要扫描 20+ 个文件来"理解项目"，token 消耗 30K+，新会话完全断片

**这不是模型不够强，是项目结构没有为 AI 设计。**

---

## 方案：模块契约模式

编程中早就有的原则：

| 编程中 | AI 开发中 |
|--------|-----------|
| 调用 `pay(100, "CNY")` 不需要读 200 行实现 | 改支付功能不需要读 200 行 service.py |
| `.h` 头文件声明接口 | `.contract.md` 声明模块 API |
| `pip install` 看包名版本即可 | Dependencies 字段声明依赖关系 |

**每个模块生成一份 `.contract.md`，只描述公开 API 和依赖。AI 读契约而非实现。**

```
传统方式：扫描 20+ 源文件 → 理解项目 → 开发
          (15K-50K tokens)

契约模式：读 PROJECT.md → 读 1 个契约 → 读 1 个源文件 → 开发
          (2K-5K tokens)

节省：60%-90%
```

---

## 快速开始

```bash
# 从 GitHub 安装
pip install git+https://github.com/KaiDev-dev/ai-context.git

# 在项目中初始化（默认英文）
cd your-project
ai-context init           # 英文模式
ai-context init --lang zh # 中文模式
ai-context scan           # 扫描代码，生成契约
ai-context status         # 查看 token 节省报告
```

### 生成的项目结构

```
your-project/
├── .ai/                            # AI 上下文层（提交到 Git）
│   ├── PROJECT.md                  # 项目地图，AI 第一个读
│   ├── GUIDE.md                    # AI 开发规范
│   └── contracts/                  # 模块契约
│       ├── auth.contract.md        # 认证模块 API
│       ├── payment.contract.md     # 支付模块 API
│       └── database.contract.md    # 数据库模块 API
├── src/                            # 你的代码（不变）
└── ...
```

### 契约文件长这样

```markdown
# Module: payment
> 支付模块，处理订单创建、退款、账单查询

## Public API

### Functions

`async create_order(amount, currency) -> Order`
  创建支付订单，返回 Order 对象

`refund(order_id, reason, partial=False) -> RefundResult`
  处理退款，partial=True 支持部分退款

### Classes

- **Order**
  - `mark_paid() -> None`
  - `cancel() -> None`

## Dependencies
- `database` — 订单和退款持久化
- `gateway` — 支付网关（微信/支付宝/Stripe）

## Side Effects
- [x] 数据库写入（orders, refunds）
- [x] 网络请求（支付网关 API）

## Files
- `src/payment/service.py`
- `src/payment/models.py`
```

**500 tokens。AI 读这个就完全理解支付模块的能力和边界，不需要读 300 行实现代码。**

---

## 配置 AI 工具

契约生成了，但你的 AI 工具得知道去哪找。在工具的规则文件里加上这一段：

### Cursor
> `.cursorrules`
```
## 上下文规则
先读 .ai/PROJECT.md 了解项目结构。
修改任何模块前，先读 .ai/contracts/<模块名>.contract.md。
用契约中的 Files 字段定位源文件——不要扫描目录。
修改公开 API 后，提醒用户运行 ai-context scan 更新契约。
```

### Claude Code
> `CLAUDE.md`
```
## 项目上下文
- 先读 .ai/PROJECT.md 了解模块地图
- 改动任何模块前读 .ai/contracts/*.contract.md
- 契约是接口定义，源码是实现细节
- 修改公开 API 后，提醒用户运行 ai-context scan
```

### WorkBuddy / CodeBuddy
> `.workbuddy/memory/MEMORY.md`
```markdown
## AI 开发规则
- 先读 .ai/PROJECT.md 了解项目结构
- 修改模块前读 .ai/contracts/ 下对应的契约文件
- 禁止扫描 src/ 目录找文件
- 修改公开 API 后，提醒用户运行 ai-context scan 更新契约
```

### GitHub Copilot
> `.github/copilot-instructions.md` — 同上

> **后期会做自动配置，目前需要手动复制粘贴一下。**

---

## 命令

| 命令 | 作用 |
|------|------|
| `ai-context init` | 初始化 `.ai/` 目录（英文） |
| `ai-context init --lang zh` | 初始化 `.ai/` 目录（中文） |
| `ai-context scan` | 扫描项目，自动生成所有契约 |
| `ai-context gen <name>` | 为新模块创建契约骨架 |
| `ai-context map` | 更新项目地图 PROJECT.md |
| `ai-context check` | 检查契约是否与代码同步 |
| `ai-context status` | 查看 token 消耗对比 |

---

## 效果实测

以 `ai-context` 自身项目（3 个 Python 文件）为例：

```
项目: ai-context

PROJECT.md: OK
GUIDE.md:   OK
契约文件:   1 个

Token 对比:
  传统方式（全量扫描）: ~9,000 tokens
  契约模式（按需读取）: ~548 tokens
  节省: 94%
```

**50 个文件的 FastAPI 项目预计节省 75%-85%。**

---

## 适用场景

- 用 AI 编程助手开发的**中大型项目**（>10 个文件）
- 团队协作（`.ai/` 提交到 Git，全员 AI 上下文一致）
- 频繁切换会话/工具的开发者（契约持久化，不会断片）

## 兼容所有 AI 编程工具

生成的是标准 Markdown 文件，通用：

- **Cursor** — `.cursorrules` 中引用
- **Windsurf** — `.windsurfrules` 中引用
- **Claude Code** — `CLAUDE.md` 中声明
- **GitHub Copilot** — 自定义指令中使用
- **WorkBuddy / CodeBuddy** — 原生 Skill 支持
- **Cline、Aider 及任何读项目文件的工具**

---

## 原理

```
                 ┌─────────────────┐
  你              │   ai-context    │
  "加退款功能" →  │   扫描代码       │
                 │   生成契约       │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │   .ai/          │
                 │   PROJECT.md    │── 第一步：AI 读项目地图
                 │   contracts/    │
                 │   ├─ auth.md    │── 第二步：AI 读模块契约
                 │   ├─ pay.md     │
                 │   └─ ...        │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
       AI 工具   │ 契约 → 文件     │
       (Cursor)  │ → 精准实现      │  2K-5K tokens / 任务
                 └─────────────────┘
```

---

## 常见问题

**需要手动维护契约吗？**
基本不需要。`ai-context scan` 自动从代码提取 API。改了接口跑一次 scan 就行。Side Effects 部分建议手动补充。

**契约文件应该提交 Git 吗？**
应该。`.ai/` 目录应纳入版本控制，团队共享才能保证 AI 上下文一致。

**怎么切换语言？**
`ai-context init --lang zh` 中文，不加参数默认英文。语言设置保存在 `.ai/.contractconfig`，后续命令自动读取。要改语言就编辑 `.contractconfig` 然后重新 `ai-context scan`。

**支持哪些语言？**
当前 Python（AST 解析）和 TypeScript/JavaScript。Go、Rust、Java 计划中。

**和 .cursorrules 有什么区别？**
`.cursorrules` 告诉 AI **怎么写**（规范、风格）。契约文件告诉 AI **代码做了什么**（API、依赖、副作用）。两者互补，搭配使用。

---

## License

MIT — 永久免费，无附加条件。
