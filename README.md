# AI Context Manager

> 让 AI 编程助手"像调用函数一样使用模块"——不再每次逆向工程整个代码库

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange)](https://github.com)

---

## 问题

用 AI 写项目的人都有这个体验：

- **前期**：爽，改一个文件就搞定，token 消耗几百
- **中期**：还行，每次读 5-10 个文件，token 消耗 5K 左右  
- **后期**：崩溃，改个支付功能，AI 要扫描 20+ 个文件来"理解项目"，token 消耗 30K+，新会话完全断片

**这不是模型不够强，是项目结构没有为 AI 设计。**

---

## 方案

类比编程世界：

| 编程中 | AI 开发中 |
|--------|-----------|
| 调用 `pay(100, "CNY")` 不需要读 200 行实现 | 改支付功能不需要读 200 行 service.py |
| `.h` 头文件声明接口 | `.contract.md` 声明模块 API |
| `pip install` 看包名版本即可 | Dependencies 字段声明依赖关系 |

**核心思路：每个模块生成一份 `.contract.md`，只描述公开 API 和依赖关系。AI 接到任务 → 读契约 → 精准改代码，不需要理解全部实现。**

```
传统方式：读 20+ 源文件 → 理解项目 → 开发
          (15K-50K tokens)

契约模式：读 PROJECT.md → 读 1 个 .contract.md → 读 1 个源文件 → 开发
          (2K-5K tokens)

节省: 60%-90%
```

---

## 快速开始

```bash
# 安装
pip install ai-context

# 在项目中初始化
cd your-project
ai-context init      # 创建 .ai/ 目录结构
ai-context scan      # 扫描代码生成契约文件
ai-context status    # 查看 token 节省效果
```

### 生成的目录结构

```
your-project/
├── .ai/                            # AI 上下文管理层（提交到 Git）
│   ├── PROJECT.md                  # 项目总览，AI 第一个读的文件
│   ├── GUIDE.md                    # AI 开发规范
│   └── contracts/                  # 模块契约
│       ├── auth.contract.md        # 认证模块的接口定义
│       ├── payment.contract.md     # 支付模块的接口定义
│       └── database.contract.md    # 数据库模块的接口定义
├── src/                            # 你的代码（不变）
└── ...
```

### 契约文件长这样

```markdown
# Module: payment
> 支付模块，处理订单创建、退款、账单查询
> Last updated: 2026-07-24 16:00

## Public API

### Functions

`async create_order(amount, currency) -> Order`
  创建支付订单，返回 Order 对象

`refund(order_id, reason, partial) -> RefundResult`
  创建退款，partial=True 时支持部分退款

### Classes

- **Order**
  - `mark_paid() -> None`
  - `cancel() -> None`

## Dependencies
- `database` — 订单和退款记录持久化
- `gateway` — 支付网关接口（微信/支付宝）

## Side Effects
- [x] Database writes (orders, refunds)
- [x] Network requests (支付网关 API)

## Files
- `src/payment/service.py`
- `src/payment/models.py`
```

**关键：AI 看到这个 500 tokens 的契约文件，就完全理解支付模块的能力和边界，不需要去读 200 行 service.py 和 100 行 models.py。**

---

## 命令

| 命令 | 作用 |
|------|------|
| `ai-context init` | 初始化 `.ai/` 目录 |
| `ai-context scan` | 扫描项目，自动生成所有契约文件 |
| `ai-context gen <name>` | 为新模块创建契约骨架 |
| `ai-context map` | 更新项目地图 PROJECT.md |
| `ai-context check` | 检查契约是否与代码同步 |
| `ai-context status` | 查看 token 消耗对比 |

---

## 效果实测

以 `ai-context` 自身项目（3 个 Python 文件）为例：

```
项目根目录: ai-context

PROJECT.md: OK
GUIDE.md:   OK  
契约文件:   1 个

Token 节省对比:
  传统方式 (全量扫描): ~9,000 tokens
  契约模式 (按需读取): ~548 tokens
  节省比例:           94%
```

**中型 FastAPI 项目（15 个模块，50+ 文件）预计节省 75%-85%。**

---

## 适用场景

- 任何用 AI 编程助手开发的**中大型项目**（>10 个文件）
- 团队协作项目（契约文件提交到 Git，团队成员共享 AI 上下文）
- 需要频繁切换会话/工具的开发者（契约保留下下文，不会断片）

## 兼容的 AI 工具

ai-context 生成的是标准 Markdown 文件，适用于所有 AI 编程助手：

- WorkBuddy / CodeBuddy（配合 Skill 自动遵循契约模式）
- Cursor（配合 `.cursorrules` 引用契约）
- Claude Code（CLAUDE.md 中声明契约目录）
- GitHub Copilot（配合自定义指令）
- Windsurf、Cline、Aider 等

---

## 原理

```
                     ┌─────────────────┐
  用户/开发者         │   ai-context    │
  "加退款功能"  ───→ │   自动扫描项目   │
                     │   生成契约文件    │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │   .ai/          │
                     │   PROJECT.md    │── 项目地图（AI 第一步读取）
                     │   contracts/    │
                     │   ├─ auth.md    │── 模块接口（AI 第二步读取）
                     │   ├─ payment.md │
                     │   └─ ...        │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
           AI 编程助手 │   读契约 → 精准定位 → 修改代码   │
           (WorkBuddy │   2K-5K tokens / 任务             │
            Cursor等)  └──────────────────────────────────┘
```

---

## 常见问题

**Q: 需要手动维护契约文件吗？**
A: 基本不需要。`ai-context scan` 自动从代码提取 API。如果改了接口签名，重新 scan 即可。Side Effects 等少数字段建议手动补充。

**Q: 契约文件应该提交到 Git 吗？**
A: 应该。`.ai/` 目录是 AI 上下文，团队共享才能保证所有人的 AI 助手理解一致。

**Q: 支持哪些语言？**
A: 当前支持 Python（AST 解析）和 TypeScript/JavaScript（正则匹配）。Go、Rust 等语言计划中。

---

## License

MIT
