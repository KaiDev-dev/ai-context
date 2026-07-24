"""
AI Context Manager CLI — 为 AI 辅助开发生成和管理模块契约文件

用法:
    ai-context init           初始化 .ai/ 目录结构
    ai-context scan           扫描项目并生成/更新所有契约文件
    ai-context gen <module>   为指定模块生成契约
    ai-context map            生成/更新项目地图 PROJECT.md
    ai-context check          检查契约文件是否与代码同步
    ai-context status         查看当前上下文状态
"""

import argparse
import sys
from pathlib import Path

from .scanner import scan_project
from .generator import generate_all, generate_project_map
from . import __version__


def cmd_init(args):
    """初始化 AI 上下文目录结构"""
    project_root = Path(args.dir or ".").resolve()
    ai_dir = project_root / ".ai"

    if ai_dir.exists():
        print(f"[!] .ai/ 目录已存在于 {project_root}")
        print(f"    运行 'ai-context scan' 来更新契约文件")
        return

    ai_dir.mkdir(parents=True)
    (ai_dir / "contracts").mkdir()

    # 创建初始文件
    (ai_dir / "PROJECT.md").write_text(
        f"# Project: {project_root.name}\n\n"
        "> AI 上下文入口 — 开发前先读此文件\n\n"
        "运行 `ai-context scan` 来生成模块契约\n",
        encoding="utf-8",
    )
    (ai_dir / "GUIDE.md").write_text(
        "# AI 开发指南\n\n"
        "运行 `ai-context scan` 来生成完整的开发指南\n",
        encoding="utf-8",
    )

    print(f"[+] AI 上下文目录已初始化: {ai_dir}")
    print(f"    {ai_dir / 'PROJECT.md'}")
    print(f"    {ai_dir / 'GUIDE.md'}")
    print(f"    {ai_dir / 'contracts/'}")
    print()
    print(f"    下一步: ai-context scan")


def cmd_scan(args):
    """扫描项目，生成所有契约文件"""
    project_root = Path(args.dir or ".").resolve()
    ai_dir = project_root / ".ai"

    if not ai_dir.exists():
        print("[!] 请先运行 'ai-context init' 初始化")
        return

    print(f"[*] 扫描项目: {project_root}")
    result = scan_project(str(project_root))

    print(f"[*] 发现 {result['total_files']} 个源文件, {len(result['packages'])} 个模块")
    output = generate_all(str(ai_dir), result)

    print(f"[+] PROJECT.md → {output['project']}")
    print(f"[+] GUIDE.md → {output['guide']}")
    print(f"[+] 契约文件 ({output['contract_count']} 个) → {output['contracts_dir']}")
    print()

    # 列出生成的所有契约
    contracts = sorted(Path(output["contracts_dir"]).glob("*.contract.md"))
    for c in contracts:
        size = c.stat().st_size
        print(f"    {c.name} ({size}B)")


def cmd_map(args):
    """生成/更新项目地图"""
    project_root = Path(args.dir or ".").resolve()
    ai_dir = project_root / ".ai"

    if not ai_dir.exists():
        print("[!] 请先运行 'ai-context init' 初始化")
        return

    print(f"[*] 扫描项目: {project_root}")
    result = scan_project(str(project_root))

    project_map = generate_project_map(result)
    (ai_dir / "PROJECT.md").write_text(project_map, encoding="utf-8")

    print(f"[+] PROJECT.md 已更新")
    print(f"    模块数: {len(result['packages'])}")
    print(f"    源文件: {result['total_files']}")


def cmd_gen(args):
    """为指定模块生成契约"""
    project_root = Path(args.dir or ".").resolve()
    ai_dir = project_root / ".ai"

    if not ai_dir.exists():
        print("[!] 请先运行 'ai-context init' 初始化")
        return

    module_name = args.module
    contract_path = ai_dir / "contracts" / f"{module_name}.contract.md"

    # 生成契约骨架
    content = f"""# Module: {module_name}
> _请填写模块描述_
> Last updated: (auto-generated)

## Public API

### Functions
- `example_function(params) -> ReturnType`
  _请填写函数描述_

### Classes
- **ExampleClass**
  - `method(params) -> ReturnType`

## Dependencies
- `dependency_name` — 用途

## Side Effects
- [ ] Database reads/writes
- [ ] File I/O
- [ ] Network/HTTP requests

## Files
- `path/to/{module_name}.py` — 用途
"""
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(content, encoding="utf-8")

    print(f"[+] 契约骨架已生成: {contract_path}")
    print(f"    请手动填写模块的 API 描述和依赖关系")


def cmd_check(args):
    """检查契约文件是否与代码同步"""
    import os
    project_root = Path(args.dir or ".").resolve()
    ai_dir = project_root / ".ai"
    contracts_dir = ai_dir / "contracts"

    if not contracts_dir.exists():
        print("[!] 未找到契约文件，请先运行 'ai-context scan'")
        return

    result = scan_project(str(project_root))

    # 检查是否有模块没有契约文件
    packages = result["packages"]
    contracts = {c.stem.replace(".contract", "") for c in contracts_dir.glob("*.contract.md")}

    missing = []
    for pkg_name in packages:
        safe_name = pkg_name.replace("__root__", "root")
        if safe_name not in contracts:
            missing.append(pkg_name)

    # 检查是否有孤立的契约文件（对应模块已删除）
    all_pkg_names = {p.replace("__root__", "root") for p in packages}
    orphan = contracts - all_pkg_names - {"root"}  # root always exists

    if not missing and not orphan:
        print("[+] 所有契约文件与代码同步")
    else:
        if missing:
            print(f"[!] 缺少契约文件的模块: {', '.join(missing)}")
        if orphan:
            print(f"[!] 孤立的契约文件(对应代码已删除): {', '.join(orphan)}")
        if missing:
            print()
            print("    运行 'ai-context scan' 来更新")


def cmd_status(args):
    """查看 AI 上下文状态"""
    project_root = Path(args.dir or ".").resolve()
    ai_dir = project_root / ".ai"

    print(f"项目根目录: {project_root}")
    print()

    if not ai_dir.exists():
        print("[!] 未初始化 — 运行 'ai-context init'")
        return

    contracts_dir = ai_dir / "contracts"
    project_md = ai_dir / "PROJECT.md"
    guide_md = ai_dir / "GUIDE.md"

    print(f"PROJECT.md: {'OK' if project_md.exists() else 'MISSING'}")
    print(f"GUIDE.md:   {'OK' if guide_md.exists() else 'MISSING'}")

    if contracts_dir.exists():
        contracts = list(contracts_dir.glob("*.contract.md"))
        print(f"契约文件:   {len(contracts)} 个")
        total_size = sum(c.stat().st_size for c in contracts)
        print(f"契约总大小: {total_size}B (~{total_size // 4} tokens)")
        print()
        for c in sorted(contracts):
            print(f"  - {c.name}")

        print()
        print(f"预估 AI 上下文消耗:")
        print(f"  项目地图:    ~{(project_md.stat().st_size if project_md.exists() else 0) // 4} tokens")
        print(f"  全部契约:    ~{total_size // 4} tokens")
        print(f"  首次会话:    ~{(project_md.stat().st_size if project_md.exists() else 0) // 4 + total_size // 4} tokens")
        print(f"  后续任务:    ~{(total_size // len(contracts)) if contracts else 0} tokens (单模块 + PROJECT.md)")
    else:
        print("契约文件:   无")

    print()
    print("Token 节省对比:")
    result = scan_project(str(project_root))
    total_files = result["total_files"]
    # 粗略估算：每个源文件平均 3K tokens
    traditional_tokens = total_files * 3000
    contract_tokens = total_size // 4 if contracts_dir.exists() else 0
    print(f"  传统方式 (全量扫描): ~{traditional_tokens:,} tokens")
    print(f"  契约模式 (按需读取): ~{contract_tokens:,} tokens")
    if traditional_tokens > 0:
        saving = (1 - contract_tokens / traditional_tokens) * 100
        print(f"  节省比例:           {saving:.0f}%")


def main():
    parser = argparse.ArgumentParser(
        description="AI Context Manager — 为 AI 辅助开发生成模块契约文件",
        prog="ai-context",
    )
    parser.add_argument(
        "--version", action="version", version=f"ai-context {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # init
    p_init = subparsers.add_parser("init", help="初始化 .ai/ 目录结构")
    p_init.add_argument("--dir", default=".", help="项目根目录")

    # scan
    p_scan = subparsers.add_parser("scan", help="扫描项目并生成所有契约文件")
    p_scan.add_argument("--dir", default=".", help="项目根目录")

    # map
    p_map = subparsers.add_parser("map", help="生成/更新项目地图")
    p_map.add_argument("--dir", default=".", help="项目根目录")

    # gen
    p_gen = subparsers.add_parser("gen", help="为指定模块生成契约骨架")
    p_gen.add_argument("module", help="模块名称")
    p_gen.add_argument("--dir", default=".", help="项目根目录")

    # check
    p_check = subparsers.add_parser("check", help="检查契约文件同步状态")
    p_check.add_argument("--dir", default=".", help="项目根目录")

    # status
    p_status = subparsers.add_parser("status", help="查看 AI 上下文状态")
    p_status.add_argument("--dir", default=".", help="项目根目录")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "scan":
        cmd_scan(args)
    elif args.command == "map":
        cmd_map(args)
    elif args.command == "gen":
        cmd_gen(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
