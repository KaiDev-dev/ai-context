"""
契约文件生成器 — 根据扫描结果生成 .contract.md 文件

契约文件格式：
    # Module: [Name]
    > 一句话描述

    ## Public API
    ### Functions
    - `name(params) -> ReturnType`
      描述

    ### Classes
    - `ClassName(BaseClass)`
      - `method(params) -> ReturnType`

    ## Dependencies
    - `module_name` — 用途

    ## Side Effects
    - 数据库读写 / 文件 I/O / 网络请求

    ## Files
    - `path/to/file.py` — 用途
"""

import os
from pathlib import Path
from datetime import datetime
from .scanner import ModuleInfo, FunctionInfo, ClassInfo, scan_project


def generate_contract_for_module(module_info: ModuleInfo, project_root: str = "") -> str:
    """为单个模块生成契约内容"""
    name = module_info.name
    doc = module_info.docstring or f"{name} 模块"

    lines = [
        f"# Module: {name}",
        f"> {doc.split(chr(10))[0] if doc else 'No description'}",
        f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    # Public API
    has_api = False
    api_lines = ["## Public API", ""]

    if module_info.functions:
        has_api = True
        api_lines.append("### Functions")
        api_lines.append("")
        for func in module_info.functions:
            if not func.is_public:
                continue
            params_str = ", ".join(func.params)
            ret = f" -> {func.return_type}" if func.return_type else ""
            async_prefix = "async " if func.is_async else ""
            dec_str = ""
            if func.decorators:
                dec_str = " ".join(f"@{d}" for d in func.decorators) + " "
            api_lines.append(f"`{dec_str}{async_prefix}{func.name}({params_str}){ret}`")
            if func.docstring:
                summary = func.docstring.split("\n")[0].strip()
                api_lines.append(f"  {summary}")
            api_lines.append("")

    if module_info.classes:
        has_api = True
        api_lines.append("### Classes")
        api_lines.append("")
        for cls in module_info.classes:
            bases = f"({', '.join(cls.base_classes)})" if cls.base_classes else ""
            api_lines.append(f"- **{cls.name}**{bases}")
            if cls.docstring:
                api_lines.append(f"  {cls.docstring.split(chr(10))[0].strip()}")
            for method in cls.methods:
                params_str = ", ".join(method.params)
                ret = f" -> {method.return_type}" if method.return_type else ""
                async_prefix = "async " if method.is_async else ""
                api_lines.append(f"  - `{async_prefix}{method.name}({params_str}){ret}`")
            api_lines.append("")

    if has_api:
        lines.extend(api_lines)
    else:
        lines.append("## Public API")
        lines.append("")
        lines.append("_No public API detected_")
        lines.append("")

    # Dependencies
    lines.append("## Dependencies")
    lines.append("")
    if module_info.imports:
        # 去重并过滤标准库
        unique_imports = sorted(set(
            imp.split(".")[0] for imp in module_info.imports
            if not imp.startswith("_")
        ))
        for imp in unique_imports[:15]:
            lines.append(f"- `{imp}`")
    else:
        lines.append("_No external dependencies detected_")
    lines.append("")

    # Side Effects
    lines.append("## Side Effects")
    lines.append("")
    lines.append("_Auto-detection limited — please document manually:_")
    lines.append("- [ ] Database reads/writes")
    lines.append("- [ ] File I/O")
    lines.append("- [ ] Network/HTTP requests")
    lines.append("- [ ] Cache operations")
    lines.append("")

    # Files
    lines.append("## Files")
    lines.append("")
    root = Path(project_root) if project_root else Path(".")
    for f in module_info.files:
        try:
            rel_path = Path(f).relative_to(root)
        except ValueError:
            rel_path = Path(f)
        lines.append(f"- `{rel_path}`")
    lines.append("")

    return "\n".join(lines)


def generate_project_map(scan_result: dict) -> str:
    """生成项目地图 PROJECT.md"""
    root = scan_result["root"]
    project_name = Path(root).name
    packages = scan_result["packages"]

    lines = [
        f"# Project: {project_name}",
        f"> AI 上下文入口 — 开发前先读此文件",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 架构概览",
        "",
    ]

    # 模块列表
    lines.append("## 模块目录")
    lines.append("")
    lines.append("| 模块 | 路径 | 公开 API 数 | 契约文件 |")
    lines.append("|------|------|------------|----------|")

    total_funcs = 0
    for pkg_name, pkg_data in sorted(packages.items()):
        modules = pkg_data["modules"]
        func_count = sum(len(m.functions) + len(m.classes) for m in modules)
        total_funcs += func_count
        contract = f".ai/contracts/{pkg_name}.contract.md"
        display_name = pkg_name.replace("__root__", "(root)")
        try:
            pkg_rel = Path(pkg_data["path"]).relative_to(root)
        except ValueError:
            pkg_rel = Path(pkg_data["path"])
        lines.append(f"| {display_name} | `{pkg_rel}` | {func_count} | `{contract}` |")

    lines.append("")
    lines.append(f"**总计**: {len(packages)} 个模块, {total_funcs} 个公开 API")
    lines.append("")

    # 开发规则
    lines.append("## AI 开发规则")
    lines.append("")
    lines.append("1. **开发前先读契约** — 找到目标模块的 `.contract.md`，不要直接读源码")
    lines.append("2. **改完更新契约** — 每次修改 API 后，运行 `ai-context scan` 更新契约")
    lines.append("3. **新增模块先建契约** — `ai-context gen <module>` 生成契约骨架")
    lines.append("4. **跨模块调用查契约** — 需要调用其他模块时，读它的 `.contract.md` 而非源码")
    lines.append("5. **依赖关系维护在契约中** — Dependencies 字段是 AI 理解模块关系的关键")
    lines.append("")

    # 技术栈
    lines.append("## 技术栈")
    lines.append("")
    lines.append("_请手动填写_")
    lines.append("")

    return "\n".join(lines)


def generate_guide() -> str:
    """生成 AI 开发指南 GUIDE.md"""
    return """# AI 开发指南

## 核心原则

本项目采用 **模块契约模式 (Module Contract Pattern)** 来管理 AI 上下文。

### AI 应该怎么做

1. **接到开发任务** → 先读 `.ai/PROJECT.md`（本指南）
2. **定位目标模块** → 查看 PROJECT.md 中的模块目录
3. **读取模块契约** → 打开 `.ai/contracts/<module>.contract.md`
4. **理解接口** → 从 Public API 了解该模块提供什么能力
5. **编码实现** → 只读相关实现文件，不扫描无关代码
6. **更新契约** → 如果修改了 API，同时更新 `.contract.md`

### AI 不应该做

- 不要扫描整个项目目录来找文件
- 不要读不在契约 Dependencies 中的无关模块
- 不要在一个文件里塞入过多功能（超过 300 行考虑拆分）
- 不要跳过契约直接读源码（契约是设计文档，源码是实现细节）

## 文件职责

| 文件 | 职责 |
|------|------|
| `.ai/PROJECT.md` | 项目总览，模块目录 |
| `.ai/GUIDE.md` | 本文件，AI 开发规范 |
| `.ai/contracts/*.contract.md` | 各模块的接口契约 |
| `src/` 等源码目录 | 实际代码实现 |

## 模块拆分原则

- **单一职责** — 一个模块只做一件事
- **接口稳定** — 公开 API 的签名不应频繁变动
- **高内聚低耦合** — 通过 Dependencies 字段声明依赖，而非隐式 import
- **文件大小** — 单个文件建议不超过 300 行，超过考虑拆子模块

## Token 优化效果

以典型 Flask/FastAPI 项目为例：
- 传统方式：每次任务 15K-50K tokens（扫描 20+ 文件）
- 契约模式：每次任务 3K-8K tokens（读 1-2 个契约 + 1-2 个文件）

Token 节省约 60%-80%。
"""


def generate_all(output_dir: str, scan_result: dict):
    """生成所有 AI 上下文文件"""
    base = Path(output_dir)
    contracts_dir = base / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)
    project_root = scan_result["root"]

    # 生成 PROJECT.md
    project_map = generate_project_map(scan_result)
    (base / "PROJECT.md").write_text(project_map, encoding="utf-8")

    # 生成 GUIDE.md
    guide = generate_guide()
    (base / "GUIDE.md").write_text(guide, encoding="utf-8")

    # 生成各模块契约
    packages = scan_result["packages"]
    for pkg_name, pkg_data in packages.items():
        modules = pkg_data["modules"]
        # 合并同包下的所有模块
        combined = ModuleInfo(
            name=pkg_name,
            path=pkg_data["path"],
            files=[],
        )
        for mod in modules:
            combined.functions.extend(mod.functions)
            combined.classes.extend(mod.classes)
            combined.imports.extend(mod.imports)
            combined.files.extend(mod.files)
            if mod.docstring:
                combined.docstring = mod.docstring

        contract_content = generate_contract_for_module(combined, project_root)
        safe_name = pkg_name.replace("__root__", "root").replace("\\", "_").replace("/", "_")
        contract_file = contracts_dir / f"{safe_name}.contract.md"
        contract_file.write_text(contract_content, encoding="utf-8")

    return {
        "project": str(base / "PROJECT.md"),
        "guide": str(base / "GUIDE.md"),
        "contracts_dir": str(contracts_dir),
        "contract_count": len(packages),
    }
