# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/env_check.py | §
# [MODULE] scripts.governance.meta.env_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""env_check.py — 环境就绪检查门禁 (Environment Readiness Gate)

对标：12-Factor App §Dependencies（显式声明 + 隔离验证）

功能：
1. 检查 Python 版本（>= 3.12，SSoT=pyproject.toml requires-python，对齐 AGENTS.md RULE-ENV）
2. PATH 影子运行时检测：首位 python 非项目 Python（Python312）时告警——advisory 不阻断 CI，JSON 带 path 字段供消费
3. 解析 requirements.txt，检查每个依赖是否可 import
4. 列出缺失项（清晰、可操作）
5. --install：自动 pip install 缺失依赖
6. --json：结构化输出供 CI 消费

集成：
- 被 smoke_test.py 调用（冒烟测试前自动跑）
- 可独立运行：python scripts/governance/env_check.py --install

exit codes: 0=环境就绪, 1=依赖缺失, 2=运行错误
"""

from __future__ import annotations

__manifest__ = """
args:
- --install
description: 环境就绪检查门禁（Python版本 + requirements.txt三方依赖验证 + 自动安装）
dimensions:
- D1
priority: P0
timeout_seconds: 120
warn_only: false
"""

import importlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

REQUIREMENTS_FILE = REPO_ROOT / "requirements.txt"
# P2-3（2026-09-14 外审遗留批）：SSoT=pyproject.toml requires-python>=3.12；旧值 3.10 会放行
# 3.11 环境（系统 PATH 实存 3.11/3.12 并存，AGENTS.md RULE-ENV 明示 3.10 注入会崩 datetime.UTC）。
MIN_PYTHON = (3, 12)
# 项目 Python 安装前缀（AGENTS.md RULE-ENV 惯例路径）。PATH 首位非此前缀 → 告警（advisory）。
_PROJECT_PYTHON_PREFIX = "programs\\python\\python312"
_PACKAGE_IMPORT_MAP: dict[str, str] = {
    "pydantic": "pydantic",
    "pyyaml": "yaml",
    "pandas": "pandas",
    "chromadb": "chromadb",
}


@dataclass
class DependencyStatus:
    pip_name: str
    import_name: str
    version_spec: str
    installed: bool = False
    error: str | None = None


@dataclass
class EnvReport:
    python_ok: bool = False
    python_version: str = ""
    python_path_ok: bool = True
    python_path_first: str = ""
    python_path_warning: str = ""
    dependencies: list[DependencyStatus] = field(default_factory=list)
    all_ok: bool = False

    @property
    def missing(self) -> list[DependencyStatus]:
        """缺失标记"""
        return [d for d in self.dependencies if not d.installed]
        "缺失标记."

    @property
    def ok(self) -> list[DependencyStatus]:
        """缺失标记."""
        return [d for d in self.dependencies if d.installed]

    "成功标记."


def _parse_requirements() -> list[tuple[str, str]]:
    """_parse_requirements implementation."""
    entries: list[tuple[str, str]] = []
    if not REQUIREMENTS_FILE.exists():
        return entries
    line_pattern = re.compile("^([a-zA-Z0-9_-]+)\\s*([><=!]+\\s*[\\d.]+(?:\\s*,\\s*[><=!]+\\s*[\\d.]+)*)?")
    for line in REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        m = line_pattern.match(line)
        if m:
            entries.append((m.group(1).lower(), (m.group(2) or "").strip()))
    return entries


def _check_python() -> tuple[bool, str]:
    """_check_python implementation."""
    current = sys.version_info[:2]
    version_str = f"{current[0]}.{current[1]}.{sys.version_info[2]}"
    return (current >= MIN_PYTHON, version_str)


def _check_python_path() -> tuple[bool, str, str]:
    """P2-3（2026-09-14）：PATH 影子运行时检测（advisory，不阻断）。

    规则：shutil.which("python") 首位非项目 Python（Python312 用户安装）→ 不合格；
    未检出 python → 放行（非 Windows 布局或极端环境，advisory 层不误报）。
    3.11/3.10 残留 PATH 的风险同样落在“首位是否项目 Python”上：首位正确时，
    3.11 在后不会被实际解析到（won't shadow）。

    Returns:
        (path_ok, first_python_abs_path, warning_text)
    """
    import shutil as _shutil

    first = _shutil.which("python") or ""
    if not first:
        return (True, "", "")
    norm = first.replace("/", "\\").lower()
    if _PROJECT_PYTHON_PREFIX in norm:
        return (True, first, "")
    warning = (
        f"PATH 首位 python 非项目 Python：{first}\n"
        f"  项目约定（AGENTS.md RULE-ENV）：会话内先执行\n"
        f"  $env:PATH = \"$env:LOCALAPPDATA\\Programs\\Python\\Python312;$env:LOCALAPPDATA\\Programs\\Python\\Python312\\Scripts;\" + $env:PATH"
    )
    return (False, first, warning)


def _check_package(pip_name: str, import_name: str) -> tuple[bool, str | None]:
    """_check_package implementation."""
    try:
        importlib.import_module(import_name)
        return (True, None)
    except ImportError as e:
        return (False, str(e))


def run_check() -> EnvReport:
    """执行检查"""
    report = EnvReport()
    "执行检查."
    py_ok, py_ver = _check_python()
    report.python_ok = py_ok
    report.python_version = py_ver
    path_ok, path_first, path_warn = _check_python_path()
    report.python_path_ok = path_ok
    report.python_path_first = path_first
    report.python_path_warning = path_warn
    entries = _parse_requirements()
    for pip_name, version_spec in entries:
        import_name = _PACKAGE_IMPORT_MAP.get(pip_name, pip_name)
        installed, error = _check_package(pip_name, import_name)
        report.dependencies.append(
            DependencyStatus(
                pip_name=pip_name, import_name=import_name, version_spec=version_spec, installed=installed, error=error
            )
        )
    report.all_ok = report.python_ok and all(d.installed for d in report.dependencies)
    return report
    "执行检查."


def _install_missing(missing: list[DependencyStatus]) -> bool:
    """_install_missing implementation."""
    install_targets = [f"{d.pip_name}{d.version_spec}" if d.version_spec else d.pip_name for d in missing]
    if not install_targets:
        return True
    print(f"\n[ENV-INSTALL] 安装缺失依赖: {', '.join(install_targets)}\n", file=sys.stderr)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", *install_targets], capture_output=False, cwd=str(REPO_ROOT)
        )
        if result.returncode != 0:
            print("\n[ENV-ERROR] pip install 失败，请手动运行: pip install -r requirements.txt", file=sys.stderr)
            return False
        return True
    except (subprocess.SubprocessError, OSError) as e:
        print(f"\n[ENV-ERROR] pip install 异常: {e}", file=sys.stderr)
        return False


def _print_report(report: EnvReport) -> None:
    """_print_report implementation."""
    py_label = "✅" if report.python_ok else f"❌（需要 >={MIN_PYTHON[0]}.{MIN_PYTHON[1]}，SSoT=pyproject requires-python）"
    print(f"\nPython:  {report.python_version} {py_label}", file=sys.stderr)
    if report.python_path_warning:
        print(f"⚠️  PATH 影子运行时告警：{report.python_path_warning}", file=sys.stderr)
    print(f"依赖包:  {len(report.ok)}/{len(report.dependencies)} 就绪\n", file=sys.stderr)
    if report.missing:
        print("缺失依赖:", file=sys.stderr)
        for d in report.missing:
            hint = _PACKAGE_IMPORT_MAP.get(d.pip_name, d.pip_name)
            install_cmd = f"pip install {d.pip_name}{d.version_spec}"
            print(f"  ❌ {d.pip_name}{d.version_spec}  →  import '{hint}' 失败", file=sys.stderr)
            print(f"     修复: {install_cmd}", file=sys.stderr)
        print(file=sys.stderr)
    if report.all_ok:
        print("✅ 环境就绪 — 所有依赖齐全\n", file=sys.stderr)


def _print_json(report: EnvReport) -> None:
    """_print_json implementation."""
    data = {
        "ready": report.all_ok,
        "python": {
            "ok": report.python_ok,
            "version": report.python_version,
            "required": f">={MIN_PYTHON[0]}.{MIN_PYTHON[1]}",
            "path_ok": report.python_path_ok,
            "path_first": report.python_path_first,
        },
        "dependencies": {
            "total": len(report.dependencies),
            "ok": len(report.ok),
            "missing": [
                {"name": d.pip_name, "import_name": d.import_name, "spec": d.version_spec} for d in report.missing
            ],
        },
    }
    print(json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr)


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="环境就绪检查门禁")
    parser.add_argument("--install", action="store_true", help="自动安装缺失依赖")
    parser.add_argument("--json", action="store_true", help="结构化 JSON 输出（CI 消费）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式：环境未就绪不阻塞（exit 0）")
    args = parser.parse_args()
    report = run_check()
    if args.json:
        _print_json(report)
    else:
        _print_report(report)
    if not report.all_ok:
        if args.install and report.missing:
            print("[ENV-INSTALL] 正在自动安装...", file=sys.stderr)
            if _install_missing(report.missing):
                report2 = run_check()
                if args.json:
                    _print_json(report2)
                else:
                    _print_report(report2)
                if report2.all_ok:
                    print("✅ 安装完成，环境就绪", file=sys.stderr)
                    sys.exit(EXIT_PASS)
                else:
                    print("❌ 安装后仍有依赖缺失，请手动排查", file=sys.stderr)
                    if args.warn_only:
                        sys.exit(EXIT_PASS)
                    sys.exit(EXIT_FINDINGS)
            else:
                if args.warn_only:
                    sys.exit(EXIT_PASS)
                sys.exit(EXIT_FINDINGS)
        else:
            if not args.json:
                print("💡 提示: 运行 `python scripts/governance/env_check.py --install` 自动安装", file=sys.stderr)
            if args.warn_only:
                sys.exit(EXIT_PASS)
            sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
