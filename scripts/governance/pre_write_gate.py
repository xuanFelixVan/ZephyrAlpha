"""AI写入前强制门禁钩子: lock协议检查+GateEngine Phase评估+注册完整性验证

RULE-ZERO 硬执行器——AI 在调用 Write/SearchReplace 之前 MUST 先通过此门禁。
exit 0 = CLEAN（允许写入）, exit 1 = BLOCKED（拒绝写入）。

用法:
    python scripts/governance/pre_write_gate.py <file_path> [--create]

设计原则:
    - 零副作用: 只读检查，不修改任何文件
    - 硬阻断: RED → exit 1，AI 无法绕过
    - 快速: 目标 <3s，不阻塞 AI 工作流
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts"
_LOCK_SCRIPT = _SCRIPTS_DIR / "lock_files.py"

_ILLEGAL_ROOT_PATTERNS = [
    r"^_temp",
    r"^_check",
    r"^_fix",
    r"^_phase_",
    r"^_deep",
    r"^_construction",
    r"^_rebuild",
    r"^_audit",
]


def _check_lock(file_path: str) -> tuple[bool, str]:
    """_check_lock implementation."""
    result = subprocess.run(
        [sys.executable, str(_LOCK_SCRIPT), "check", file_path],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=10,
        cwd=str(_PROJECT_ROOT),
    )
    output = result.stdout.strip()
    if "FREE" in output:
        return True, "OK"
    if "LOCKED" in output:
        return False, output
    return True, f"LOCK_CHECK_WARN: {output[:200]}"


def _check_root_pollution(file_path: str) -> tuple[bool, str]:
    """_check_root_pollution implementation."""
    rel = Path(file_path)
    try:
        rel = rel.resolve().relative_to(_PROJECT_ROOT.resolve())
    except ValueError:
        return True, "OK"

    parts = rel.parts
    if len(parts) == 1:
        for pat in _ILLEGAL_ROOT_PATTERNS:
            if re.match(pat, parts[0]):
                return False, f"ILLEGAL_ROOT: {file_path} 匹配禁止前缀 {pat!r}——临时文件不得落盘到根目录（RULE-FIVE）"
    return True, "OK"


def _check_phase_health() -> tuple[bool, str]:
    """_check_phase_health implementation."""
    try:
        from zephyr.governance.phase_manager import GateResult, session_startup
        result = session_startup(quick=True)
        if result["ready"]:
            return True, f"PHASE_OK: {result['green']}G/{result['yellow']}Y/{result['red']}R"
        return False, f"PHASE_BLOCKED: {result['next_action']}"
    except ImportError as e:
        return True, f"PHASE_WARN: 无法加载 phase_manager ({e})——降级通过"
    except Exception as e:
        return True, f"PHASE_WARN: phase_manager 异常 ({e})——降级通过"


def _check_registered(file_path: str, is_create: bool) -> tuple[bool, str]:
    """_check_registered implementation."""
    if not is_create:
        return True, "OK"
    rel = Path(file_path)
    try:
        rel = rel.resolve().relative_to(_PROJECT_ROOT.resolve())
    except ValueError:
        return True, "OK"
    parts = rel.parts
    allowed_dirs = {"src", "scripts", "tests", "docs", "config", "data", ".trae"}
    if parts and parts[0] not in allowed_dirs:
        return False, f"UNREGISTERED_DIR: {parts[0]!r} 不在允许目录 {allowed_dirs}——新建文件 MUST 走 scaffold.py（RULE-FOUR）"
    return True, "OK"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="AI 写入前强制门禁——不通过则拒绝写入",
    )
    parser.add_argument("file_path", help="要写入的文件路径（相对或绝对）")
    parser.add_argument("--create", action="store_true", help="是否创建新文件")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    checks: list[dict] = []

    ok, msg = _check_phase_health()
    checks.append({"check": "phase_health", "pass": ok, "message": msg})

    ok, msg = _check_lock(args.file_path)
    checks.append({"check": "lock_protocol", "pass": ok, "message": msg})

    ok, msg = _check_root_pollution(args.file_path)
    checks.append({"check": "root_pollution", "pass": ok, "message": msg})

    ok, msg = _check_registered(args.file_path, args.create)
    checks.append({"check": "registration", "pass": ok, "message": msg})

    blocked = [c for c in checks if not c["pass"]]

    if args.json:
        import json
        print(json.dumps({
            "allowed": len(blocked) == 0,
            "checks": checks,
            "file": args.file_path,
        }, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            icon = "  PASS" if c["pass"] else "  BLOCK"
            print(f"{icon}  {c['check']}: {c['message']}")

        if blocked:
            print(f"\n  BLOCKED ({len(blocked)}/{len(checks)} checks failed)")
            print(f"  File: {args.file_path}")
            print(f"  Action required: 修复以上 BLOCK 项后重试")
        else:
            print(f"\n  ALL CLEAR ({len(checks)}/{len(checks)}) — 允许写入 {args.file_path}")

    return 0 if len(blocked) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
