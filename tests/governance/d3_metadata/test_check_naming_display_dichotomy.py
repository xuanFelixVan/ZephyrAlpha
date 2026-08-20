# [BLUEPRINT] MOD-INF-005 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""main() 显示二元化测试——真阻断 vs warn-only 计数分离。

背景（Task 3，#ARCH-PRECOMMIT-INCREMENTAL，2026-08-06）：
    全仓 --warn-only --scan 曾输出"369 阻断性命名违规"但实际 exit 0（不阻断 commit），
    显示与 exit code 矛盾，误导开发者以为 commit 被卡。治本：将计数拆为
      actual_blocking（真阻断，exit 1）
      warn_only_count（警告级，exit 0，走 gate-naming-audit 清零）
    保证显示语义与 exit code 一致。

    本测试锁定二元化行为，防回归到"显示阻断但 exit 0"的误导状态。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


def _make_bad_name_file(tmp_path: Path) -> Path:
    """构造 N-01/N-13 违规文件（含大写字母的 .md 文件名，在 repo 外避免 N-16 干扰）。"""
    bad = tmp_path / "BadName.md"
    bad.write_text("# test", encoding="utf-8")
    return bad


def test_warn_only_shows_warn_only_count_and_exits_zero(tmp_path):
    """warn-only 模式 + other 违规（N-01/N-13）→ 输出 warn-only 提示 + exit 0。

    Task 3 核心：warn-only 模式下 other 违规不卡 commit，显示须明示"不阻断"。
    """
    bad = _make_bad_name_file(tmp_path)
    r = _run(["--warn-only", str(bad)])
    assert r.returncode == 0, (
        f"warn-only 模式 other 违规应 exit 0（不阻断），实际 {r.returncode}。stdout={r.stdout} stderr={r.stderr}"
    )
    assert "warn-only 命名违规" in r.stdout, f"应输出 warn-only 计数提示。stdout={r.stdout}"
    assert "不阻断 commit" in r.stdout, f"应明示不阻断 commit。stdout={r.stdout}"
    assert "阻断性命名违规" not in r.stdout, f"warn-only 模式不应显示'阻断性命名违规'（误导）。stdout={r.stdout}"


def test_blocking_mode_shows_actual_blocking_and_exits_nonzero(tmp_path):
    """非 warn-only 模式 + other 违规 → 输出阻断性计数 + exit 1。

    Task 3 核心：非 warn-only 模式下 other 违规真阻断，显示须与 exit code 一致。
    """
    bad = _make_bad_name_file(tmp_path)
    r = _run([str(bad)])
    assert r.returncode != 0, (
        f"非 warn-only 模式 other 违规应 exit 非零（阻断），实际 {r.returncode}。stdout={r.stdout} stderr={r.stderr}"
    )
    assert "阻断性命名违规" in r.stdout, f"应输出阻断性计数提示。stdout={r.stdout}"
    assert "不阻断 commit" not in r.stdout, (
        f"非 warn-only 模式不应显示'不阻断 commit'（与 exit 1 矛盾）。stdout={r.stdout}"
    )
