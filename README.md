# AI Context Manager

> Stop reverse-engineering your codebase on every AI task. Module contracts cut token consumption by 60-90%.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange)](https://github.com/KaiDev-dev/ai-context)
[![Lang](https://img.shields.io/badge/README-中_文-red)](README_CN.md)
[![Website](https://img.shields.io/badge/website-aicodingdir.com-blue)](https://aicodingdir.com/tools/ai-context/)

---

> **Featured on [AICoding](https://aicodingdir.com) — [Product Page](https://aicodingdir.com/tools/ai-context/) · [Deep Dive: Module Contract Pattern](https://aicodingdir.com/blog/module-contract-pattern-ai-coding-2026/)**

## The Problem

Every developer using AI coding tools hits the same wall:

- **Early project** (< 10 files): AI reads 3-5 files, 2K-5K tokens. Fast, accurate. "This is amazing!"
- **Mid-size** (10-50 files): AI scans 10-15 files trying to understand dependencies, 10K-30K tokens. Mixed results.
- **Large** (50+ files): AI reads 20+ files, traces imports, burns 30K-80K tokens. Constantly wrong about architecture. Context compression causes amnesia between sessions.

**The model isn't the problem. The project structure isn't designed for AI.**

---

## The Solution: Module Contract Pattern

Same principle you use every day as a developer:

| In Programming | For AI |
|----------------|--------|
| Call `pay(100, "USD")` without reading 200 lines of implementation | Modify payment module without reading 200 lines of source |
| `.h` header files declare interfaces | `.contract.md` files declare module APIs |
| `pip install` requires only package name | `Dependencies` section declares module relationships |

**Each module gets a `.contract.md` — a human and AI-readable interface definition. AI reads the contract, not the implementation.**

```
Traditional: Scan 20+ source files → Understand project → Code
             (15K-50K tokens)

Contract:    Read PROJECT.md → Read 1 contract → Read 1 source file → Code
             (2K-5K tokens)

Savings: 60-90%
```

---

## Quick Start

```bash
# Install from GitHub
pip install git+https://github.com/KaiDev-dev/ai-context.git

# Initialize in your project (English by default)
cd your-project
ai-context init           # English mode
ai-context init --lang zh # Chinese mode
ai-context scan           # Scans code, generates all contracts
ai-context status         # See token savings report
```

### Generated Structure

```
your-project/
├── .ai/                            # AI context layer (commit to Git)
│   ├── PROJECT.md                  # Project map — AI reads this first
│   ├── GUIDE.md                    # AI development rules
│   └── contracts/                  # Module contracts
│       ├── auth.contract.md        # Auth module API
│       ├── payment.contract.md     # Payment module API
│       └── database.contract.md    # Database module API
├── src/                            # Your code (unchanged)
└── ...
```

### What a Contract Looks Like

```markdown
# Module: payment
> Payment processing — orders, refunds, billing
> Last updated: 2026-07-24 16:00

## Public API

### Functions

`async create_order(amount, currency) -> Order`
  Create a new payment order. Returns Order in "pending" state.

`refund(order_id, reason, partial=False) -> RefundResult`
  Process a refund. Set partial=True for partial refunds.

### Classes

- **Order**
  - `mark_paid() -> None`
  - `cancel() -> None`

## Dependencies
- `database` — order and refund persistence
- `gateway` — payment gateway (Stripe / WeChat Pay)

## Side Effects
- [x] Database writes (orders, refunds)
- [x] Network requests (payment gateway API)

## Files
- `src/payment/service.py` — core payment logic
- `src/payment/models.py` — Order, RefundResult dataclasses
```

**500 tokens. AI reads this and fully understands the payment module's capabilities and boundaries. No need to read 300 lines of implementation.**

---

## Configure Your AI Tool

Contracts are generated, but your AI tool needs to know where to find them. Add this to your tool's context file:

### Cursor
> `.cursorrules`
```
## Context Rules
Always read `.ai/PROJECT.md` first to understand the project.
Before modifying any module, read its contract at `.ai/contracts/<module>.contract.md`.
Use the `Files` section in contracts to locate source files — do not scan directories.
After changing a module's public API, remind the user to run `ai-context scan`.
```

### Claude Code
> `CLAUDE.md`
```
## Project Context
- Read .ai/PROJECT.md first for the module map
- Read .ai/contracts/*.contract.md for module APIs before any changes
- Contracts define the interface; source code is the implementation
- After modifying a public API, remind the user to run `ai-context scan`
```

### WorkBuddy / CodeBuddy
> `.workbuddy/memory/MEMORY.md`
```markdown
## AI Development Rules
- Read .ai/PROJECT.md first to understand project structure
- Read the relevant .contract.md before modifying any module
- Do not scan src/ directory to find files
- After changing a public API, remind the user to run ai-context scan
```

### GitHub Copilot
> `.github/copilot-instructions.md` — same content as above.

> **Auto-configuration is planned for a future release.** For now, copy-paste the snippet for your tool.

---

## Commands

| Command | What it does |
|---------|-------------|
| `ai-context init` | Initialize `.ai/` directory |
| `ai-context init --lang zh` | Initialize with Chinese output |
| `ai-context scan` | Scan project, auto-generate all contracts |
| `ai-context gen <name>` | Create a contract skeleton for a new module |
| `ai-context map` | Update PROJECT.md project map |
| `ai-context check` | Check if contracts are in sync with code |
| `ai-context status` | Show token savings comparison |
| `ai-context scan --force` | Force overwrite PROJECT.md and GUIDE.md |

### How Updates Work

`ai-context scan` uses **smart partial updates** to avoid destroying your manual work:

| File | Behavior |
|------|----------|
| **PROJECT.md** | Only updates auto-generated sections (module table + dev rules). Your Architecture Overview, Tech Stack, and custom sections are preserved. |
| **GUIDE.md** | Never overwritten after first generation. Customize it freely — it's yours. |
| **.contract.md** | Always regenerated — code is the source of truth. |

Use `--force` to fully regenerate PROJECT.md and GUIDE.md from templates.

> **Tip**: PROJECT.md markers (`<!-- AUTO_BEGIN -->` / `<!-- AUTO_END -->`) define which sections are auto-updated. Keep your manual content outside these markers.

---

## Measured Results

On the `ai-context` project itself (3 Python files):

```
Project: ai-context

PROJECT.md: OK
GUIDE.md:   OK
Contracts:  1

Token comparison:
  Traditional (full scan): ~9,000 tokens
  Contract mode (on demand): ~548 tokens
  Savings: 94%
```

**A 50-file FastAPI project typically saves 75-85% per AI task.**

---

## Use Cases

- Any project with **10+ files** using AI coding assistants
- Team projects — commit `.ai/` to Git for shared AI context
- Frequent session switching — contracts persist across sessions, no context amnesia

## Compatible With All AI Coding Tools

ai-context generates plain Markdown files — works everywhere:

- **Cursor** — reference contracts in `.cursorrules`
- **Windsurf** — add to `.windsurfrules`
- **Claude Code** — declare in `CLAUDE.md`
- **GitHub Copilot** — add to custom instructions
- **WorkBuddy / CodeBuddy** — native Skill support
- **Cline, Aider, and any tool that reads project files**

---

## How It Works

```
                 ┌─────────────────┐
  You            │   ai-context    │
  "add refund" → │   scans code    │
                 │   generates     │
                 │   contracts     │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │   .ai/          │
                 │   PROJECT.md    │── Step 1: AI reads project map
                 │   contracts/    │
                 │   ├─ auth.md    │── Step 2: AI reads module contract
                 │   ├─ pay.md     │
                 │   └─ ...        │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
       AI tool   │ contract → file │
       (Cursor)  │ → implement     │  2K-5K tokens per task
                 └─────────────────┘
```

---

## FAQ

**Do I need to manually maintain contracts?**
Mostly no. `ai-context scan` auto-extracts function signatures and classes from code. Re-run after API changes. The Side Effects section is the only part worth filling in manually.

**Should contracts be committed to Git?**
Yes. `.ai/` should be version-controlled so every team member's AI tool shares the same project understanding.

**How do I switch languages?**
Run `ai-context init --lang zh` for Chinese, or omit `--lang` for English (default). The setting is saved in `.ai/.contractconfig` and used by all subsequent commands. To change later, edit `.contractconfig` and re-run `ai-context scan`.

**Which languages are supported?**
Python (full AST parsing) and TypeScript/JavaScript (regex-based export detection). Go, Rust, and Java support planned.

**How is this different from .cursorrules?**
`.cursorrules` tells AI **how** to write code (conventions, style). Contracts tell AI **what** the code does (module APIs, dependencies). They're complementary — use both.

---

## License

MIT — free forever, no strings attached.
