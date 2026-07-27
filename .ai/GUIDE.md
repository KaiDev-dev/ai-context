# AI Development Guide

## Core Principle

This project uses the **Module Contract Pattern** to manage AI context.

### What AI Should Do

1. **Receive task → Read `.ai/PROJECT.md` first**
2. **Locate target module → Check the module directory in PROJECT.md**
3. **Read module contract → Open `.ai/contracts/<module>.contract.md`**
4. **Understand interface → Learn module capabilities from Public API**
5. **Implement → Only read relevant source files, don't scan unrelated code**
6. **Update contract → If API changed, update `.contract.md`**

### What AI Should NOT Do

- Don't scan the entire project directory to find files
- Don't read unrelated modules not in contract Dependencies
- Don't cram too much into one file (consider splitting at 300+ lines)
- Don't skip contracts to read source directly (contracts are design docs, source is implementation)

## File Responsibilities

| 文件 | 职责 |
|------|------|
| `.ai/PROJECT.md` | Project overview, module directory |
| `.ai/GUIDE.md` | This file, AI development conventions |
| `.ai/contracts/*.contract.md` | Module interface contracts |
| `src/` and other source dirs | Actual code implementation |

## Module Splitting Principles

- **Single responsibility — one module does one thing**
- **Stable interfaces — public API signatures should not change frequently**
- **High cohesion, low coupling — declare dependencies via Dependencies field, not implicit imports**
- **File size — prefer <300 lines per file, consider splitting beyond that**

## Token Optimization Effect

For a typical Flask/FastAPI project:
- Traditional: 15K-50K tokens per task (scanning 20+ files)
- Contract mode: 3K-8K tokens per task (reading 1-2 contracts + 1-2 files)

Token savings: approximately 60%-80%.
