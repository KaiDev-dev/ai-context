"""
代码扫描器 — 分析项目结构，提取模块信息

支持的检测模式：
    - Python: 函数/类定义、import 语句、装饰器路由
    - TypeScript/JavaScript: export 语句、函数签名、接口定义
    - 目录结构: 基于文件夹的模块识别
"""

import os
import re
import ast
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class FunctionInfo:
    name: str
    params: list[str]
    return_type: str = ""
    docstring: str = ""
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False
    is_public: bool = True


@dataclass
class ClassInfo:
    name: str
    methods: list[FunctionInfo] = field(default_factory=list)
    base_classes: list[str] = field(default_factory=list)
    docstring: str = ""
    is_public: bool = True


@dataclass
class ModuleInfo:
    name: str
    path: str
    files: list[str] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    docstring: str = ""


def should_skip_dir(dirname: str) -> bool:
    """判断是否应该跳过该目录"""
    skip = {
        "__pycache__", ".git", ".ai", "node_modules", "venv", ".venv",
        "env", ".env", "dist", "build", ".next", ".nuxt", "coverage",
        ".pytest_cache", ".mypy_cache", ".tox", "egg-info",
    }
    return dirname in skip or dirname.startswith(".")


def should_skip_file(filename: str) -> bool:
    """判断是否应该跳过该文件"""
    skip_prefixes = ("__", ".")
    skip_suffixes = (".pyc", ".pyo", ".spec.ts", ".test.ts", ".spec.js", ".test.js")
    skip_names = {"setup.py", "conftest.py"}
    if filename in skip_names:
        return True
    if filename.startswith(skip_prefixes):
        return True
    if any(filename.endswith(s) for s in skip_suffixes):
        return True
    return False


# ─── Python 扫描器 ───────────────────────────────────────────


class PythonScanner:
    """扫描 Python 文件，提取公开 API"""

    def scan_file(self, filepath: str) -> ModuleInfo:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return ModuleInfo(name="", path=filepath)

        info = ModuleInfo(
            name=Path(filepath).stem,
            path=filepath,
            files=[filepath],
            docstring=ast.get_docstring(tree) or "",
        )

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    info.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    info.imports.append(node.module)

            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith("_"):
                    continue
                func = self._extract_function(node)
                info.functions.append(func)

            elif isinstance(node, ast.AsyncFunctionDef):
                if node.name.startswith("_"):
                    continue
                func = self._extract_function(node)
                func.is_async = True
                info.functions.append(func)

            elif isinstance(node, ast.ClassDef):
                if node.name.startswith("_"):
                    continue
                cls = self._extract_class(node)
                info.classes.append(cls)

        return info

    def _extract_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
        params = []
        # Build parameter list with type annotations and defaults
        args = node.args
        defaults_offset = len(args.args) - len(args.defaults)
        for i, arg in enumerate(args.args):
            p = arg.arg
            if arg.annotation:
                p += f": {ast.unparse(arg.annotation)}"
            # Add default value if present
            default_idx = i - defaults_offset
            if default_idx >= 0:
                default_val = ast.unparse(args.defaults[default_idx])
                p += f" = {default_val}"
            params.append(p)
        if args.vararg:
            params.append(f"*{args.vararg.arg}")
        if args.kwarg:
            params.append(f"**{args.kwarg.arg}")

        return_type = ""
        if node.returns:
            return_type = ast.unparse(node.returns)

        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(ast.unparse(dec))

        return FunctionInfo(
            name=node.name,
            params=params,
            return_type=return_type,
            docstring=ast.get_docstring(node) or "",
            decorators=decorators,
            is_public=True,
        )

    def _extract_class(self, node: ast.ClassDef) -> ClassInfo:
        bases = [ast.unparse(b) for b in node.bases]
        methods = []

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name.startswith("_") and child.name != "__init__":
                    continue
                func = self._extract_function(child)
                if isinstance(child, ast.AsyncFunctionDef):
                    func.is_async = True
                methods.append(func)

        return ClassInfo(
            name=node.name,
            methods=methods,
            base_classes=bases,
            docstring=ast.get_docstring(node) or "",
        )


# ─── TypeScript/JavaScript 扫描器 ────────────────────────────


class TypeScriptScanner:
    """扫描 TS/JS 文件，提取 export 语句和函数签名"""

    EXPORT_RE = re.compile(
        r"export\s+(?:async\s+)?(?:function|class|const|let|var|interface|type|enum)\s+(\w+)",
        re.MULTILINE,
    )
    FUNC_SIG_RE = re.compile(
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*(\S+))?",
        re.MULTILINE,
    )

    def scan_file(self, filepath: str) -> ModuleInfo:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        info = ModuleInfo(
            name=Path(filepath).stem,
            path=filepath,
            files=[filepath],
        )

        for m in self.EXPORT_RE.finditer(source):
            info.exports.append(m.group(1))

        for m in self.FUNC_SIG_RE.finditer(source):
            name = m.group(1)
            if name.startswith("_"):
                continue
            params_str = m.group(2).strip()
            params = [p.strip().split(":")[0].strip() for p in params_str.split(",") if p.strip()]
            return_type = m.group(3) or ""
            info.functions.append(FunctionInfo(
                name=name, params=params, return_type=return_type, is_public=True
            ))

        return info


# ─── 统一扫描入口 ────────────────────────────────────────────


class ProjectScanner:
    """扫描整个项目，按目录/包识别模块"""

    def __init__(self, root: str):
        self.root = Path(root).resolve()

    def scan(self) -> list[ModuleInfo]:
        modules: list[ModuleInfo] = []
        self._walk(self.root, modules)
        return modules

    def _walk(self, directory: Path, modules: list[ModuleInfo]):
        try:
            entries = sorted(directory.iterdir())
        except PermissionError:
            return

        py_files = []
        ts_files = []
        subdirs = []

        for entry in entries:
            if entry.is_dir():
                if not should_skip_dir(entry.name):
                    subdirs.append(entry)
            elif entry.is_file():
                if should_skip_file(entry.name):
                    continue
                if entry.suffix == ".py" and entry.name != "__init__.py":
                    py_files.append(entry)
                elif entry.suffix in (".ts", ".tsx", ".js", ".jsx"):
                    ts_files.append(entry)

        py_scanner = PythonScanner()
        ts_scanner = TypeScriptScanner()

        for f in py_files:
            info = py_scanner.scan_file(str(f))
            if info.functions or info.classes:
                modules.append(info)

        for f in ts_files:
            info = ts_scanner.scan_file(str(f))
            if info.exports or info.functions:
                modules.append(info)

        for subdir in subdirs:
            self._walk(subdir, modules)

    def group_by_package(self, modules: list[ModuleInfo]) -> dict[str, list[ModuleInfo]]:
        """将模块按父目录分组"""
        groups: dict[str, list[ModuleInfo]] = {}
        for mod in modules:
            rel = Path(mod.path).relative_to(self.root)
            parent = str(rel.parent) if str(rel.parent) != "." else "__root__"
            groups.setdefault(parent, []).append(mod)
        return groups

    def detect_modules(self, modules: list[ModuleInfo]) -> dict[str, dict]:
        """
        智能识别模块边界：
        - 如果有 __init__.py 的目录 → Python package
        - 如果有 index.ts 的目录 → TS 模块
        - 孤立的文件 → 独立模块
        """
        packages = {}
        for mod in modules:
            pkg_dir = Path(mod.path).parent
            package_name = pkg_dir.name if pkg_dir != self.root else "__root__"

            init_files = list(pkg_dir.glob("__init__.py")) + list(pkg_dir.glob("index.ts"))
            if init_files or package_name not in ("__root__", ""):
                packages.setdefault(package_name, {"modules": [], "path": str(pkg_dir)})
                packages[package_name]["modules"].append(mod)
            else:
                packages.setdefault(mod.name, {"modules": [mod], "path": str(pkg_dir)})

        return packages


def scan_project(root: str) -> dict:
    """便捷函数：扫描项目并返回结构化结果"""
    scanner = ProjectScanner(root)
    modules = scanner.scan()
    detected = scanner.detect_modules(modules)

    result = {
        "root": str(scanner.root),
        "total_files": len(modules),
        "packages": detected,
    }
    return result
