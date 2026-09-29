# [TTL] permanent
"""证尺：gate 执行统计落盘不得有 1ms 观测盲区（st-commitspeed-tbl-20260924-p13）。

病灶：commit_gate_registry._stat_flush 落盘 rec["ms"] 曾用 `>= 1.0` 过滤，
凡耗时 <1ms 的门从统计里整个消失（实测约 42-44% 盲区），导致
"零触发零消费→可退役"判据对近半门无法证。
本测塞入 ms=0.4 的门，断言落盘 jsonl 仍含该门（未修＝红，修后＝绿）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.gov_enforcement.rule_bridge import commit_gate_registry as cgr  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[2]


class _FakeGateway:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root


def _last_rec(root: Path) -> dict:
    lines = (root / ".runtime" / "audit" / "gate_execution_stats.jsonl").read_text(encoding="utf-8").splitlines()
    assert lines, "flush 未落任何行"
    return json.loads(lines[-1])


def test_stat_flush_records_sub_ms_gates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # 防假绿：确认加载的是本仓树（本测试所在 checkout/worktree）的源码，
    # 而非 pip editable .pth 指向的外来 checkout——原版曾绑作者 worktree 绝对路径
    # 子串 "csx-p13"，任何其他 worktree/主区恒红（st-nightsweep-sw12 改相对判据，
    # 语义零放宽：跨仓加载仍必红）
    assert Path(cgr.__file__).resolve().is_relative_to(_REPO_ROOT), (
        f"commit_gate_registry 加载自外来源码: {cgr.__file__} (本仓根={_REPO_ROOT})"
    )
    monkeypatch.setattr(
        cgr,
        "_STAT_ACC",
        {
            "fast_gate": {"ms": 0.4, "passed": True, "state": "ran"},
            "slow_gate": {"ms": 9.9, "passed": True, "state": "ran"},
        },
    )
    cgr._stat_flush(_FakeGateway(tmp_path))
    rec = _last_rec(tmp_path)
    assert "fast_gate" in rec["ms"], f"亚毫秒门被 1ms 门槛吞掉: {rec['ms']}"
    assert rec["ms"]["fast_gate"] == 0.4
    assert rec["ms"]["slow_gate"] == 9.9
    assert rec["n_specs"] == 2
