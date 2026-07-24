# Module: ai_context
> 代码扫描器 — 分析项目结构，提取模块信息
> Last updated: 2026-07-24 18:58

## Public API

### Functions

`cmd_init(args)`
  初始化 AI 上下文目录结构

`cmd_scan(args)`
  扫描项目，生成所有契约文件

`cmd_map(args)`
  生成/更新项目地图

`cmd_gen(args)`
  为指定模块生成契约

`cmd_check(args)`
  检查契约文件是否与代码同步

`cmd_status(args)`
  查看 AI 上下文状态

`main()`

`t(lang, key) -> str`
  Get a translated string, falling back to English.

`generate_contract_for_module(module_info, project_root) -> str`
  Generate contract content for a single module (language-neutral headers).

`generate_project_map(scan_result, lang) -> str`
  Generate PROJECT.md in the specified language.

`generate_guide(lang) -> str`
  Generate AI Development Guide in the specified language.

`generate_all(output_dir, scan_result, lang)`
  Generate all AI context files in the specified language.

`should_skip_dir(dirname) -> bool`
  判断是否应该跳过该目录

`should_skip_file(filename) -> bool`
  判断是否应该跳过该文件

`scan_project(root) -> dict`
  便捷函数：扫描项目并返回结构化结果

### Classes

- **FunctionInfo**

- **ClassInfo**

- **ModuleInfo**

- **PythonScanner**
  扫描 Python 文件，提取公开 API
  - `scan_file(self, filepath) -> ModuleInfo`

- **TypeScriptScanner**
  扫描 TS/JS 文件，提取 export 语句和函数签名
  - `scan_file(self, filepath) -> ModuleInfo`

- **ProjectScanner**
  扫描整个项目，按目录/包识别模块
  - `__init__(self, root)`
  - `scan(self) -> list[ModuleInfo]`
  - `group_by_package(self, modules) -> dict[str, list[ModuleInfo]]`
  - `detect_modules(self, modules) -> dict[str, dict]`

## Dependencies

- `argparse`
- `ast`
- `dataclasses`
- `datetime`
- `generator`
- `os`
- `pathlib`
- `re`
- `scanner`
- `sys`
- `typing`

## Side Effects

_Auto-detection limited — please document manually:_
- [ ] Database reads/writes
- [ ] File I/O
- [ ] Network/HTTP requests
- [ ] Cache operations

## Files

- `ai_context\cli.py`
- `ai_context\generator.py`
- `ai_context\scanner.py`
