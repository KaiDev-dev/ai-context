# Project: ai-context
> AI 上下文入口 — 开发前先读此文件
> 生成时间: 2026-07-24 18:58

## 架构概览

## 模块目录

| 模块 | 路径 | 公开 API 数 | 契约文件 |
|------|------|------------|----------|
| ai_context | `ai_context` | 21 | `.ai/contracts/ai_context.contract.md` |

**总计**: 1 个模块, 21 个公开 API

## AI 开发规则

1. **开发前先读契约 — 找到目标模块的 `.contract.md`，不要直接读源码**
2. **改完更新契约 — 每次修改 API 后，运行 `ai-context scan` 更新契约**
3. **新增模块先建契约 — `ai-context gen <module>` 生成契约骨架**
4. **跨模块调用查契约 — 需要调用其他模块时，读它的 `.contract.md` 而非源码**
5. **依赖关系维护在契约中 — Dependencies 字段是 AI 理解模块关系的关键**

## 技术栈

_请手动填写_
