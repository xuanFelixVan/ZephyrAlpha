# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/pre_op_check.py | §
# [MODULE] scripts.governance.meta.pre_op_check
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
# [TTL] task_bound
"""AI操作前准入控制器 — 写/删文件前的机械门禁检查.

本脚本是 RULE-ZERO~EIGHT 的代码级强制执行层。
对标: K8s Admission Webhook — 操作前硬拦截，不放行就不创建。

Usage:
    python scripts/governance/pre_op_check.py --check-write <filepath> [--session-id <id>]
    python scripts/governance/pre_op_check.py --check-delete <filepath>
    python scripts/governance/pre_op_check.py --check-create <filepath> [--session-id <id>]
    python scripts/governance/pre_op_check.py --check-all <filepath> [--session-id <id>]
    python scripts/governance/pre_op_check.py --json  # JSON output

Exit codes:
    0 = ALLOW (所有检查 GREEN)
    1 = DENY  (至少一个 RED 阻断)
    2 = WARN  (至少一个 YELLOW 警告，无 RED)
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_PASS, REPO_ROOT

__manifest__ = """
args: [--check-write, --check-delete, --check-create, --check-all, --session-id, --json]
description: >
    AI操作前准入控制器——在任何 Write/SearchReplace/DeleteFile 操作前执行机械门禁检查。
    对标 K8s Admission Webhook：不放行就不创建。
dimensions:
- D1
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import json
import logging
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_PROJECT_ROOT = REPO_ROOT
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts"
_LOCK_SCRIPT = _SCRIPTS_DIR / "lock_files.py"
_SCAFFOLD_SCRIPT = _SCRIPTS_DIR / "scaffold.py"
_AUDIT_SCRIPT = _SCRIPTS_DIR / "governance" / "audit_registration.py"
_REGISTRY_OF_REGISTRIES = _PROJECT_ROOT / "docs" / "registry_of_registries.yaml"
_SCRIPT_MANIFEST = _SCRIPTS_DIR / "script_manifest.yaml"

_LEGAL_DIRS = {
    _PROJECT_ROOT / "src" / "zephyr",
    _PROJECT_ROOT / "scripts",
    _PROJECT_ROOT / "tests",
    _PROJECT_ROOT / "docs",
    _PROJECT_ROOT / "config",
    _PROJECT_ROOT / "data",
}

_MAX_WORKERS = 8


@dataclass
class CheckItem:
    check_id: str
    name: str
    status: str  # GREEN / YELLOW / RED
    message: str
    detail: str = ""


@dataclass
class AdmissionResult:
    filepath: str
    operation: str  # write / delete / create
    allowed: bool
    checks: list[CheckItem] = field(default_factory=list)
    recommendation: str = ""

    @property
    def red_checks(self) -> list[CheckItem]:
        """red_checks implementation."""
        return [c for c in self.checks if c.status == "RED"]

    @property
    def yellow_checks(self) -> list[CheckItem]:
        """yellow_checks implementation."""
        return [c for c in self.checks if c.status == "YELLOW"]

    def to_dict(self) -> dict[str, Any]:
        """to_dict implementation."""
        return {
            "filepath": self.filepath,
            "operation": self.operation,
            "allowed": self.allowed,
            "exit_code": 0 if self.allowed else (2 if not self.red_checks else 1),
            "summary": f"{len(self.red_checks)} RED, {len(self.yellow_checks)} YELLOW, "
            f"{len(self.checks) - len(self.red_checks) - len(self.yellow_checks)} GREEN",
            "checks": [
                {"check_id": c.check_id, "name": c.name, "status": c.status, "message": c.message, "detail": c.detail}
                for c in self.checks
            ],
            "recommendation": self.recommendation,
        }


def _run_lock_check(filepath: str, session_id: str | None) -> tuple[int, str]:
    """_run_lock_check implementation."""
    args = [sys.executable, str(_LOCK_SCRIPT), "check", filepath]
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15, cwd=str(_PROJECT_ROOT)
        )
        combined = (result.stdout + result.stderr).strip()
        return result.returncode, combined
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, f"ERROR: {e}"


def _file_is_registered(filepath: str) -> tuple[bool, str]:
    """_file_is_registered implementation."""
    rel = str(Path(filepath).resolve().relative_to(_PROJECT_ROOT)).replace("\\", "/")
    checks: list[tuple[bool, str]] = []

    if _SCRIPT_MANIFEST.exists():
        try:
            content = _SCRIPT_MANIFEST.read_text(encoding="utf-8")
            if rel in content:
                checks.append((True, "script_manifest.yaml"))
        except Exception:
            pass

    if _REGISTRY_OF_REGISTRIES.exists():
        try:
            content = _REGISTRY_OF_REGISTRIES.read_text(encoding="utf-8")
            if rel in content:
                checks.append((True, "registry_of_registries.yaml"))
        except Exception:
            pass

    init_dir = Path(filepath).resolve().parent
    init_file = init_dir / "__init__.py"
    if init_file.exists():
        try:
            content = init_file.read_text(encoding="utf-8")
            basename = Path(filepath).stem
            if basename in content:
                checks.append((True, "__init__.py"))
        except Exception:
            pass

    if checks:
        locations = ", ".join(loc for _, loc in checks)
        return True, locations
    return False, "未在任何注册表中发现"


def _check_legal_directory(filepath: str) -> bool:
    """_check_legal_directory implementation."""
    resolved = Path(filepath).resolve()
    for legal_dir in _LEGAL_DIRS:
        try:
            resolved.relative_to(legal_dir)
            return True
        except ValueError:
            pass
    return False


def _run_audit_scan() -> tuple[int, str]:
    """_run_audit_scan implementation."""
    if not _AUDIT_SCRIPT.exists():
        return -1, f"SCRIPT_NOT_FOUND: {_AUDIT_SCRIPT}"
    try:
        result = subprocess.run(
            [sys.executable, str(_AUDIT_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(_PROJECT_ROOT),
        )
        return result.returncode, result.stdout.strip()[:3000]
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, f"ERROR: {e}"


def _check_file_exists_for_duplicate(filepath: str) -> bool:
    """_check_file_exists_for_duplicate implementation."""
    return Path(filepath).resolve().exists()


def check_write(filepath: str, session_id: str | None = None) -> AdmissionResult:
    """Check compliance and report findings."""
    checks: list[CheckItem] = []
    resolved = Path(filepath).resolve()
    file_exists = resolved.exists()
    is_new_file = not file_exists

    def _lock_check() -> CheckItem:
        """_lock_check implementation."""
        if file_exists:
            exit_code, output = _run_lock_check(filepath, session_id)
            if "FREE" in output:
                return CheckItem("PRE-OP-001", "文件锁检查", "GREEN", f"文件未被锁定: {filepath}")
            elif "LOCKED" in output:
                holder = output.split("持有者:")[-1].strip() if "持有者:" in output else "unknown"
                return CheckItem("PRE-OP-001", "文件锁检查", "RED", f"文件已被锁定: {filepath}", f"持有者: {holder}")
            return CheckItem("PRE-OP-001", "文件锁检查", "YELLOW", f"锁检查异常: {output[:200]}")
        return CheckItem("PRE-OP-001", "文件锁检查", "GREEN", f"新文件无需锁检查: {filepath}")

    def _new_file_check() -> CheckItem:
        """_new_file_check implementation."""
        if is_new_file:
            if not _check_legal_directory(filepath):
                return CheckItem(
                    "PRE-OP-002",
                    "新建文件目录合法性",
                    "RED",
                    f"文件不在合法目录中: {filepath}",
                    f"合法目录: {[str(d.relative_to(_PROJECT_ROOT)) for d in _LEGAL_DIRS]}",
                )
            registered, locations = _file_is_registered(filepath)
            if registered:
                return CheckItem("PRE-OP-003", "新建文件注册检查", "GREEN", f"文件已在注册表中: {locations}")
            else:
                return CheckItem(
                    "PRE-OP-003",
                    "新建文件注册检查",
                    "RED",
                    "新文件未注册! 必须通过 scaffold.py 创建",
                    "运行: python scripts/scaffold.py script/module/gate ...",
                )
        return CheckItem("PRE-OP-002", "新建文件检查", "GREEN", "文件已存在，无需 scaffold")

    def _func_duplicate_check() -> CheckItem:
        """_func_duplicate_check implementation."""
        if is_new_file:
            return CheckItem(
                "PRE-OP-004",
                "功能重复检查",
                "YELLOW",
                "新文件应通过 scaffold.py 自动查重",
                "scaffold.py 内置 BlueprintSearchServer 功能重复检测",
            )
        return CheckItem("PRE-OP-004", "功能重复检查", "GREEN", "修改已有文件，不查功能重复")

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {
            executor.submit(_lock_check): "lock",
            executor.submit(_new_file_check): "new_file",
            executor.submit(_func_duplicate_check): "duplicate",
        }
        for future in as_completed(futures):
            checks.append(future.result())

    reds = [c for c in checks if c.status == "RED"]
    allowed = len(reds) == 0
    recommendation = ""
    if not allowed:
        for c in reds:
            recommendation += f"[{c.check_id}] {c.message}\n"
        if any("PRE-OP-003" in c.check_id for c in reds):
            recommendation += "\n→ 请用 scaffold.py 创建文件，不要用 Write 直接写入新文件。"

    return AdmissionResult(
        filepath=filepath,
        operation="write",
        allowed=allowed,
        checks=checks,
        recommendation=recommendation.strip(),
    )


def check_delete(filepath: str) -> AdmissionResult:
    """Check compliance and report findings."""
    checks: list[CheckItem] = []
    resolved = Path(filepath).resolve()

    def _exists_check() -> CheckItem:
        """_exists_check implementation."""
        if not resolved.exists():
            return CheckItem("DEL-001", "文件存在性", "RED", f"文件不存在，无需删除: {filepath}")
        return CheckItem("DEL-001", "文件存在性", "GREEN", "文件存在")

    def _registration_check() -> CheckItem:
        """_registration_check implementation."""
        registered, locations = _file_is_registered(filepath)
        if registered:
            return CheckItem(
                "DEL-002",
                "RULE-THREE STEP 1: 登记检查",
                "RED",
                f"文件已在注册表中登记 ({locations})! 不能删除，只能重构/重安置。",
                "如确需删除，先从所有注册表中移除引用。",
            )
        return CheckItem("DEL-002", "RULE-THREE STEP 1: 登记检查", "GREEN", "文件未在任何注册表中登记")

    def _git_check() -> CheckItem:
        """_git_check implementation."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-1", "--", filepath],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                cwd=str(_PROJECT_ROOT),
            )
            if result.stdout.strip():
                return CheckItem(
                    "DEL-003",
                    "RULE-THREE STEP 1: git历史检查",
                    "RED",
                    f"文件有 git 提交历史: {result.stdout.strip()[:100]}",
                    "已提交的文件有持续价值。只能重构/重安置，不能删除。",
                )
        except Exception:
            pass
        return CheckItem("DEL-003", "RULE-THREE STEP 1: git历史检查", "GREEN", "文件无 git 提交历史")

    def _content_value_check() -> CheckItem:
        """_content_value_check implementation."""
        if not resolved.exists() or not resolved.is_file():
            return CheckItem("DEL-004", "RULE-THREE STEP 3: 内容价值检查", "GREEN", "文件不存在，跳过内容检查")
        try:
            content = resolved.read_text(encoding="utf-8", errors="replace")
            if len(content.strip()) == 0:
                return CheckItem("DEL-004", "RULE-THREE STEP 3: 内容价值检查", "GREEN", "空文件——无内容价值")
            unique_indicators = [  # noqa: gate-vocab  内容检测子串，非 file_category
                "class ",
                "def ",
                "yaml",
                "registry",
                "contract",
                "check",
                "validate",
                "manifest",
                "gate",
                "pipeline",
                "schema",
                "threshold",
            ]
            content_lower = content.lower()
            found = [ind for ind in unique_indicators if ind in content_lower]
            if found:
                return CheckItem(
                    "DEL-004",
                    "RULE-THREE STEP 3: 内容价值检查",
                    "YELLOW",
                    f"文件包含潜在有价值内容: {found[:5]}",
                    "请在删除前逐行确认这些内容在其他文件中也有备份。",
                )
            return CheckItem("DEL-004", "RULE-THREE STEP 3: 内容价值检查", "GREEN", "未检测到明显的独特内容指标")
        except Exception as e:
            return CheckItem("DEL-004", "RULE-THREE STEP 3: 内容价值检查", "YELLOW", f"内容读取异常: {e}")

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {
            executor.submit(_exists_check): "exists",
            executor.submit(_registration_check): "registration",
            executor.submit(_git_check): "git",
            executor.submit(_content_value_check): "content",
        }
        for future in as_completed(futures):
            checks.append(future.result())

    reds = [c for c in checks if c.status == "RED"]
    yellows = [c for c in checks if c.status == "YELLOW"]
    allowed = len(reds) == 0
    recommendation = ""
    if reds:
        for c in reds:
            recommendation += f"[{c.check_id}] {c.message}\n"
        recommendation += "\n→ RULE-THREE 三步审判未通过。不能删除。"
    elif yellows:
        recommendation = f"⚠ {len(yellows)} 个警告。请确认每行内容在别处有备份后再删。"

    return AdmissionResult(
        filepath=filepath,
        operation="delete",
        allowed=allowed,
        checks=checks,
        recommendation=recommendation.strip(),
    )


def check_create(filepath: str, session_id: str | None = None) -> AdmissionResult:
    """Check compliance and report findings."""
    result = check_write(filepath, session_id)
    result.operation = "create"
    return result


def check_all(filepath: str, session_id: str | None = None) -> AdmissionResult:
    """Check compliance and report findings."""
    resolved = Path(filepath).resolve()
    if resolved.exists():
        return check_write(filepath, session_id)
    return check_create(filepath, session_id)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="AI操作前准入控制器 — K8s Admission Webhook 模式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python scripts/governance/pre_op_check.py --check-write src/zephyr/core/models.py
    python scripts/governance/pre_op_check.py --check-delete _temp_old_script.py
    python scripts/governance/pre_op_check.py --check-create scripts/new_tool.py --session-id session-20260508-001
    python scripts/governance/pre_op_check.py --check-all scripts/my_script.py --json
        """,
    )
    parser.add_argument("--check-write", metavar="FILEPATH", help="写文件前准入检查")
    parser.add_argument("--check-delete", metavar="FILEPATH", help="删除文件前准入检查")
    parser.add_argument("--check-create", metavar="FILEPATH", help="创建新文件前准入检查")
    parser.add_argument("--check-all", metavar="FILEPATH", help="全量检查（自动判断操作类型）")
    parser.add_argument("--session-id", default=None, help="AI session ID（用于锁检查）")
    parser.add_argument("--json", action="store_true", help="JSON 输出（AI 消费格式）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式——RED 也不阻断 exit code")

    args = parser.parse_args()

    if args.check_write:
        result = check_write(args.check_write, args.session_id)
    elif args.check_delete:
        result = check_delete(args.check_delete)
    elif args.check_create:
        result = check_create(args.check_create, args.session_id)
    elif args.check_all:
        result = check_all(args.check_all, args.session_id)
    else:
        parser.print_help()
        sys.exit(EXIT_PASS)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"[PRE-OP] {result.filepath} | operation={result.operation}")
        for c in result.checks:
            icon = {"GREEN": "✅", "YELLOW": "⚠️", "RED": "🔴"}.get(c.status, "?")
            print(f"  {icon} [{c.check_id}] {c.name}: {c.message}")
        if result.recommendation:
            print(f"\n{result.recommendation}")
        print(f"\n→ {'ALLOW' if result.allowed else 'DENY'}")

    if args.warn_only:
        sys.exit(EXIT_PASS)
    if not result.allowed:
        red_count = len(result.red_checks)
        sys.exit(1 if red_count > 0 else 2)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
