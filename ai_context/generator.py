"""
Contract file generator — generates .contract.md files from scan results

Supports English (en) and Chinese (zh) output.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from .scanner import ModuleInfo, FunctionInfo, ClassInfo, scan_project


# ─── Markers for partial updates ──────────────────────────────

MARKER_BEGIN = "<!-- AUTO_BEGIN: {key} -->"
MARKER_END = "<!-- AUTO_END: {key} -->"

def replace_auto_section(content: str, key: str, new_text: str, section_header: str = "") -> str:
    """Replace the auto-generated section between markers, or handle legacy files.

    - If markers found: replace content between them.
    - If no markers + section_header given: find legacy section by header and replace it.
    - Fallback: append marked section at end.
    """
    begin = MARKER_BEGIN.format(key=key)
    end = MARKER_END.format(key=key)
    pattern = re.escape(begin) + r".*?" + re.escape(end)
    replacement = begin + "\n" + new_text.strip() + "\n" + end
    if re.search(pattern, content, re.DOTALL):
        return re.sub(pattern, lambda m: replacement, content, flags=re.DOTALL)

    # Legacy file: try to find and replace the old section by its header
    if section_header:
        escaped_header = re.escape(section_header)
        legacy_pattern = escaped_header + r"\n\n(?:(?!\n## ).)+"
        legacy_match = re.search(legacy_pattern, content, re.DOTALL)
        if legacy_match:
            return content[:legacy_match.start()] + replacement + "\n\n" + content[legacy_match.end():].lstrip()

    # Fallback: append at end
    return content.rstrip() + "\n\n" + replacement + "\n"


def extract_auto_section(content: str, key: str) -> str | None:
    """Extract the auto-generated section between markers."""
    begin = MARKER_BEGIN.format(key=key)
    end = MARKER_END.format(key=key)
    pattern = re.escape(begin) + r"\n(.*?)\n" + re.escape(end)
    m = re.search(pattern, content, re.DOTALL)
    return m.group(1).strip() if m else None


# ─── Language strings ──────────────────────────────────────────

STRINGS = {
    "en": {
        "project_subtitle": "AI context entry point — read this file first",
        "generated": "Generated",
        "overview": "Architecture Overview",
        "module_dir": "Module Directory",
        "module_col": "Module",
        "path_col": "Path",
        "api_count_col": "Public APIs",
        "contract_col": "Contract File",
        "total": "Total",
        "modules_unit": "modules",
        "public_apis": "public APIs",
        "dev_rules": "AI Development Rules",
        "rule_1": "Read contracts first — find the target module's `.contract.md`, don't read source directly",
        "rule_2": "Update contracts after changes — run `ai-context scan` after modifying APIs",
        "rule_3": "Create contracts for new modules — `ai-context gen <module>` generates a skeleton",
        "rule_4": "Check contracts for cross-module calls — read `.contract.md` instead of source",
        "rule_5": "Maintain dependencies in contracts — the Dependencies field is key for AI to understand module relationships",
        "rule_6": "Write docstrings for all public functions — contracts extract descriptions from docstrings; without them, the AI only sees function names",
        "tech_stack": "Tech Stack",
        "fill_manually": "Please fill in manually",
        "no_api": "No public API detected",
        "no_deps": "No external dependencies detected",
        "side_effects_hint": "Auto-detection limited — please document manually:",
        "side_db": "Database reads/writes",
        "side_io": "File I/O",
        "side_net": "Network/HTTP requests",
        "side_cache": "Cache operations",
        "guide_title": "AI Development Guide",
        "guide_core": "Core Principle",
        "guide_core_text": "This project uses the **Module Contract Pattern** to manage AI context.",
        "guide_do": "What AI Should Do",
        "guide_do_1": "Receive task → Read `.ai/PROJECT.md` first",
        "guide_do_2": "Locate target module → Check the module directory in PROJECT.md",
        "guide_do_3": "Read module contract → Open `.ai/contracts/<module>.contract.md`",
        "guide_do_4": "Understand interface → Learn module capabilities from Public API",
        "guide_do_5": "Implement → Only read relevant source files, don't scan unrelated code",
        "guide_do_6": "Update contract → If API changed, update `.contract.md`",
        "guide_dont": "What AI Should NOT Do",
        "guide_dont_1": "Don't scan the entire project directory to find files",
        "guide_dont_2": "Don't read unrelated modules not in contract Dependencies",
        "guide_dont_3": "Don't cram too much into one file (consider splitting at 300+ lines)",
        "guide_dont_4": "Don't skip contracts to read source directly (contracts are design docs, source is implementation)",
        "guide_file_role": "File Responsibilities",
        "guide_file_role_table": [
            ("`.ai/PROJECT.md`", "Project overview, module directory"),
            ("`.ai/GUIDE.md`", "This file, AI development conventions"),
            ("`.ai/contracts/*.contract.md`", "Module interface contracts"),
            ("`src/` and other source dirs", "Actual code implementation"),
        ],
        "guide_split": "Module Splitting Principles",
        "guide_split_1": "Single responsibility — one module does one thing",
        "guide_split_2": "Stable interfaces — public API signatures should not change frequently",
        "guide_split_3": "High cohesion, low coupling — declare dependencies via Dependencies field, not implicit imports",
        "guide_split_4": "File size — prefer <300 lines per file, consider splitting beyond that",
        "guide_token": "Token Optimization Effect",
        "guide_token_text_1": "For a typical Flask/FastAPI project:",
        "guide_token_text_2": "Traditional: 15K-50K tokens per task (scanning 20+ files)",
        "guide_token_text_3": "Contract mode: 3K-8K tokens per task (reading 1-2 contracts + 1-2 files)",
        "guide_token_text_4": "Token savings: approximately 60%-80%.",
    },
    "zh": {
        "project_subtitle": "AI 上下文入口 — 开发前先读此文件",
        "generated": "生成时间",
        "overview": "架构概览",
        "module_dir": "模块目录",
        "module_col": "模块",
        "path_col": "路径",
        "api_count_col": "公开 API 数",
        "contract_col": "契约文件",
        "total": "总计",
        "modules_unit": "个模块",
        "public_apis": "个公开 API",
        "dev_rules": "AI 开发规则",
        "rule_1": "开发前先读契约 — 找到目标模块的 `.contract.md`，不要直接读源码",
        "rule_2": "改完更新契约 — 每次修改 API 后，运行 `ai-context scan` 更新契约",
        "rule_3": "新增模块先建契约 — `ai-context gen <module>` 生成契约骨架",
        "rule_4": "跨模块调用查契约 — 需要调用其他模块时，读它的 `.contract.md` 而非源码",
        "rule_5": "依赖关系维护在契约中 — Dependencies 字段是 AI 理解模块关系的关键",
        "rule_6": "公开函数必须写 docstring — 契约文件从 docstring 提取描述；没有 docstring，AI 只能看到函数名",
        "tech_stack": "技术栈",
        "fill_manually": "请手动填写",
        "no_api": "未检测到公开 API",
        "no_deps": "未检测到外部依赖",
        "side_effects_hint": "自动检测有限 — 请手动补充：",
        "side_db": "数据库读写",
        "side_io": "文件 I/O",
        "side_net": "网络/HTTP 请求",
        "side_cache": "缓存操作",
        "guide_title": "AI 开发指南",
        "guide_core": "核心原则",
        "guide_core_text": "本项目采用 **模块契约模式 (Module Contract Pattern)** 来管理 AI 上下文。",
        "guide_do": "AI 应该怎么做",
        "guide_do_1": "接到开发任务 → 先读 `.ai/PROJECT.md`",
        "guide_do_2": "定位目标模块 → 查看 PROJECT.md 中的模块目录",
        "guide_do_3": "读取模块契约 → 打开 `.ai/contracts/<module>.contract.md`",
        "guide_do_4": "理解接口 → 从 Public API 了解该模块提供什么能力",
        "guide_do_5": "编码实现 → 只读相关实现文件，不扫描无关代码",
        "guide_do_6": "更新契约 → 如果修改了 API，运行 `ai-context scan` 更新契约",
        "guide_dont": "AI 不应该做",
        "guide_dont_1": "不要扫描整个项目目录来找文件",
        "guide_dont_2": "不要读不在契约 Dependencies 中的无关模块",
        "guide_dont_3": "不要在一个文件里塞入过多功能（超过 300 行考虑拆分）",
        "guide_dont_4": "不要跳过契约直接读源码（契约是设计文档，源码是实现细节）",
        "guide_file_role": "文件职责",
        "guide_file_role_table": [
            ("`.ai/PROJECT.md`", "项目总览，模块目录"),
            ("`.ai/GUIDE.md`", "本文件，AI 开发规范"),
            ("`.ai/contracts/*.contract.md`", "各模块的接口契约"),
            ("`src/` 等源码目录", "实际代码实现"),
        ],
        "guide_split": "模块拆分原则",
        "guide_split_1": "单一职责 — 一个模块只做一件事",
        "guide_split_2": "接口稳定 — 公开 API 的签名不应频繁变动",
        "guide_split_3": "高内聚低耦合 — 通过 Dependencies 字段声明依赖，而非隐式 import",
        "guide_split_4": "文件大小 — 单个文件建议不超过 300 行，超过考虑拆子模块",
        "guide_token": "Token 优化效果",
        "guide_token_text_1": "以典型 Flask/FastAPI 项目为例：",
        "guide_token_text_2": "传统方式：每次任务 15K-50K tokens（扫描 20+ 文件）",
        "guide_token_text_3": "契约模式：每次任务 3K-8K tokens（读 1-2 个契约 + 1-2 个文件）",
        "guide_token_text_4": "Token 节省约 60%-80%。",
    },
}


def t(lang: str, key: str) -> str:
    """Get a translated string, falling back to English."""
    return STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))


# ─── Contract generator ────────────────────────────────────────


def generate_contract_for_module(module_info: ModuleInfo, project_root: str = "") -> str:
    """Generate contract content for a single module (language-neutral headers)."""
    name = module_info.name
    doc = module_info.docstring or f"{name} module"

    lines = [
        f"# Module: {name}",
        f"> {doc.split(chr(10))[0] if doc else 'No description'}",
        f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

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


# ─── PROJECT.md generator ──────────────────────────────────────


def generate_project_map(scan_result: dict, lang: str = "en") -> str:
    """Generate PROJECT.md in the specified language."""
    root = scan_result["root"]
    project_name = Path(root).name
    packages = scan_result["packages"]

    lines = [
        f"# Project: {project_name}",
        f"> {t(lang, 'project_subtitle')}",
        f"> {t(lang, 'generated')}: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"## {t(lang, 'overview')}",
        "",
    ]

    # Module table (auto-generated, wrapped in markers)
    lines.append(MARKER_BEGIN.format(key="module_table"))
    lines.append("")
    lines.append(f"## {t(lang, 'module_dir')}")
    lines.append("")
    lines.append(f"| {t(lang, 'module_col')} | {t(lang, 'path_col')} | {t(lang, 'api_count_col')} | {t(lang, 'contract_col')} |")
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
    lines.append(f"**{t(lang, 'total')}**: {len(packages)} {t(lang, 'modules_unit')}, {total_funcs} {t(lang, 'public_apis')}")
    lines.append("")
    lines.append(MARKER_END.format(key="module_table"))
    lines.append("")

    # Dev rules (auto-generated, wrapped in markers)
    lines.append(MARKER_BEGIN.format(key="dev_rules"))
    lines.append("")
    lines.append(f"## {t(lang, 'dev_rules')}")
    lines.append("")
    lines.append(f"1. **{t(lang, 'rule_1')}**")
    lines.append(f"2. **{t(lang, 'rule_2')}**")
    lines.append(f"3. **{t(lang, 'rule_3')}**")
    lines.append(f"4. **{t(lang, 'rule_4')}**")
    lines.append(f"5. **{t(lang, 'rule_5')}**")
    lines.append(f"6. **{t(lang, 'rule_6')}**")
    lines.append("")
    lines.append(MARKER_END.format(key="dev_rules"))
    lines.append("")

    lines.append(f"## {t(lang, 'tech_stack')}")
    lines.append("")
    lines.append(f"_{t(lang, 'fill_manually')}_")
    lines.append("")

    return "\n".join(lines)


# ─── GUIDE.md generator ───────────────────────────────────────


def generate_guide(lang: str = "en") -> str:
    """Generate AI Development Guide in the specified language."""
    s = lambda k: t(lang, k)

    lines = [
        f"# {s('guide_title')}",
        "",
        f"## {s('guide_core')}",
        "",
        s("guide_core_text"),
        "",
        f"### {s('guide_do')}",
        "",
        f"1. **{s('guide_do_1')}**",
        f"2. **{s('guide_do_2')}**",
        f"3. **{s('guide_do_3')}**",
        f"4. **{s('guide_do_4')}**",
        f"5. **{s('guide_do_5')}**",
        f"6. **{s('guide_do_6')}**",
        "",
        f"### {s('guide_dont')}",
        "",
        f"- {s('guide_dont_1')}",
        f"- {s('guide_dont_2')}",
        f"- {s('guide_dont_3')}",
        f"- {s('guide_dont_4')}",
        "",
        f"## {s('guide_file_role')}",
        "",
        "| 文件 | 职责 |",
        "|------|------|",
    ]
    rows = s("guide_file_role_table")
    if isinstance(rows, list):
        for file, role in rows:
            lines.append(f"| {file} | {role} |")
    lines.append("")

    lines.append(f"## {s('guide_split')}")
    lines.append("")
    lines.append(f"- **{s('guide_split_1')}**")
    lines.append(f"- **{s('guide_split_2')}**")
    lines.append(f"- **{s('guide_split_3')}**")
    lines.append(f"- **{s('guide_split_4')}**")
    lines.append("")

    lines.append(f"## {s('guide_token')}")
    lines.append("")
    lines.append(s("guide_token_text_1"))
    lines.append(f"- {s('guide_token_text_2')}")
    lines.append(f"- {s('guide_token_text_3')}")
    lines.append("")
    lines.append(s("guide_token_text_4"))
    lines.append("")

    return "\n".join(lines)


# ─── Bulk generator ────────────────────────────────────────────


def generate_all(output_dir: str, scan_result: dict, lang: str = "en", force: bool = False):
    """Generate all AI context files in the specified language.

    Preservation rules:
    - PROJECT.md: partial update (module table + dev rules), preserves manual sections
    - GUIDE.md: never overwritten unless --force
    - .contract.md: always regenerated (code is truth)
    """
    base = Path(output_dir)
    contracts_dir = base / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)
    project_root = scan_result["root"]

    project_file = base / "PROJECT.md"
    guide_file = base / "GUIDE.md"

    # Generate fresh content
    full_project = generate_project_map(scan_result, lang)
    fresh_guide = generate_guide(lang)

    # ─── PROJECT.md: partial update ───
    if project_file.exists() and not force:
        existing = project_file.read_text(encoding="utf-8")
        # Extract auto-generated sections from fresh content
        module_table = extract_auto_section(full_project, "module_table")
        dev_rules = extract_auto_section(full_project, "dev_rules")
        if module_table:
            existing = replace_auto_section(existing, "module_table", module_table,
                                           section_header=f"## {t(lang, 'module_dir')}")
        if dev_rules:
            existing = replace_auto_section(existing, "dev_rules", dev_rules,
                                           section_header=f"## {t(lang, 'dev_rules')}")
        project_file.write_text(existing, encoding="utf-8")
        print("    PROJECT.md — 模块表已更新 (手动内容已保留)")
    else:
        project_file.write_text(full_project, encoding="utf-8")
        if force:
            print("    PROJECT.md — 已强制覆盖")
        else:
            print("    PROJECT.md — 已创建")

    # ─── GUIDE.md: preserve ───
    if guide_file.exists() and not force:
        print("    GUIDE.md — 已跳过 (手动内容已保留，用 --force 可覆盖)")
    else:
        guide_file.write_text(fresh_guide, encoding="utf-8")
        if force:
            print("    GUIDE.md — 已强制覆盖")
        else:
            print("    GUIDE.md — 已创建")

    packages = scan_result["packages"]
    for pkg_name, pkg_data in packages.items():
        modules = pkg_data["modules"]
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
