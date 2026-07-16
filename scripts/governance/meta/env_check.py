# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/env_check.py | §
# [MODULE] scripts.governance.meta.env_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""env_check.py — 环境就绪检查门禁 (Environment Readiness Gate)

对标：12-Factor App §Dependencies（显式声明 + 隔离验证）

功能：
1. 检查 Python 版本（>= 3.10）
2. 解析 requirements.txt，检查每个依赖是否可 import
3. 列出缺失项（清晰、可操作）
4. --install：自动 pip install 缺失依赖
5. --json：结构化输出供 CI 消费

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
MIN_PYTHON = (3, 10)
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
    print(f"\nPython:  {report.python_version} {('✅' if report.python_ok else '❌（需要 >=3.10）')}", file=sys.stderr)
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
