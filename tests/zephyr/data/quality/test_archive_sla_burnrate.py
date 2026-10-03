# [BLUEPRINT] MOD-DATENG-003 | docs/03_modules/_domain_data_eng/quality_sla_breach_predictor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATENG-003 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.zephyr.data.quality.test_archive_sla_burnrate
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] src/zephyr/data/quality/archive_sla_burnrate.py
"""archive_sla_burnrate 单元测试：F08 归档链 SLA burn-rate 消费面。

验收（T1-B1 融合接线 2026-09-30）：
- manifest 路径镜像常量与 scripts/ch/archiver.py 真源同源（防漂移断言）
- manifest 缺失/观测不足=not_run 不冒绿；损坏行跳过计数
- 窗口归属确定性；ran 态全量透出；告警只回调；同输入必同输出
全部输出走 tmp_path fixture（测试隔离铁律），不触生产路径。
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

import pytest

pytest.importorskip(
    "zephyr.data.quality.archive_sla_burnrate",
    reason="archive_sla_burnrate not importable",
)

from zephyr.data.quality.archive_sla_burnrate import (  # noqa: E402
    DEFAULT_MANIFEST_PATH,
    build_weekly_attainment,
    load_manifest_records,
    run_archive_sla_burnrate,
)

_T0 = datetime.datetime(2026, 9, 30, 12, 0, 0, tzinfo=datetime.UTC)


def _write_manifest(tmp_path: Path, archived_ats: list[str], *, verified: bool = True) -> Path:
    p = tmp_path / "archive_manifest.jsonl"
    lines = [
        json.dumps(
            {"table": "c1_market.kline_1min", "partition": f"2026{i:02d}", "verified": verified, "archived_at": ts},
            ensure_ascii=False,
        )
        for i, ts in enumerate(archived_ats, start=1)
    ]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


# ── SSOT 防漂移 ───────────────────────────────────────────────────────────


def test_manifest_path_mirror_matches_archiver_source():
    """镜像常量必须与 scripts/ch/archiver.py 真源一致（scripts 不可 import 的机械同源闸）。"""
    src = (Path(__file__).resolve().parents[4] / "scripts" / "ch" / "archiver.py").read_text(encoding="utf-8")
    root_m = re.search(r"ARCHIVE_ROOT = pathlib\.Path\(\s*\n?\s*\"([^\"]+)\"", src)
    manifest_m = re.search(r"MANIFEST_PATH = ARCHIVE_ROOT / \"([^\"]+)\"", src)
    assert root_m and manifest_m, "archiver.py 真源常量解析失败（脚本被改须同步本闸）"
    assert Path(root_m.group(1)) / manifest_m.group(1) == DEFAULT_MANIFEST_PATH


# ── load_manifest_records ────────────────────────────────────────────────


def test_load_manifest_missing_returns_empty(tmp_path):
    records, corrupt = load_manifest_records(tmp_path / "nope.jsonl")
    assert records == []
    assert corrupt == 0


def test_load_manifest_skips_corrupt_lines(tmp_path):
    p = tmp_path / "archive_manifest.jsonl"
    good = json.dumps({"verified": True, "archived_at": "2026-09-30T00:00:00+00:00"})
    p.write_text(good + "\n{broken json\n\nnot json\n", encoding="utf-8")
    records, corrupt = load_manifest_records(p)
    assert len(records) == 1
    assert corrupt == 2


# ── build_weekly_attainment ──────────────────────────────────────────────


def test_build_weekly_attainment_window_membership_deterministic():
    # 两个窗口内有 verified 记录，其余空
    ats = [
        "2026-09-29T00:00:00+00:00",  # 末窗（-7d..now）
        "2026-09-15T00:00:00+00:00",  # 第三窗（-21d..-14d）
    ]
    records = [{"verified": True, "archived_at": a} for a in ats]
    points = build_weekly_attainment(records, now_utc=_T0, window_days=7, windows=4)
    assert [p.attainment for p in points] == [0.0, 1.0, 0.0, 1.0]
    assert points[-1].observed_at == _T0


def test_build_weekly_attainment_ignores_unverified_and_bad_ts():
    records = [
        {"verified": False, "archived_at": "2026-09-29T00:00:00+00:00"},
        {"verified": True, "archived_at": "garbage"},
        {"verified": True},
    ]
    points = build_weekly_attainment(records, now_utc=_T0, window_days=7, windows=3)
    assert all(p.attainment == 0.0 for p in points)


def test_build_weekly_attainment_rejects_bad_params():
    with pytest.raises(Exception, match="windows"):
        build_weekly_attainment([], now_utc=_T0, windows=1)
    with pytest.raises(Exception, match="window_days"):
        build_weekly_attainment([], now_utc=_T0, window_days=0)


# ── run_archive_sla_burnrate 诚实四态 ────────────────────────────────────


def test_run_not_run_when_manifest_missing(tmp_path):
    summary = run_archive_sla_burnrate(tmp_path / "nope.jsonl", clock=lambda: _T0)
    assert summary["status"] == "not_run"
    assert "缺失" in summary["reason"]


def test_run_not_run_when_fewer_than_two_observed_windows(tmp_path):
    p = _write_manifest(tmp_path, ["2026-09-29T00:00:00+00:00"])
    summary = run_archive_sla_burnrate(p, clock=lambda: _T0)
    assert summary["status"] == "not_run"
    assert summary["observed_windows"] == 1


def test_run_ran_healthy_when_all_windows_covered(tmp_path):
    # 8 窗全覆盖（每周一档）：attainment 恒 1.0 → 零消耗零 burn → HEALTHY
    ats = [
        "2026-09-29T00:00:00+00:00",
        "2026-09-22T00:00:00+00:00",
        "2026-09-15T00:00:00+00:00",
        "2026-09-08T00:00:00+00:00",
        "2026-09-01T00:00:00+00:00",
        "2026-08-25T00:00:00+00:00",
        "2026-08-18T00:00:00+00:00",
        "2026-08-11T00:00:00+00:00",
    ]
    p = _write_manifest(tmp_path, ats)
    summary = run_archive_sla_burnrate(p, clock=lambda: _T0)
    assert summary["status"] == "ran"
    assert summary["level"] == "healthy"
    assert summary["burn_rate"] == 0.0


def test_run_ran_critical_alerts_when_recent_windows_empty(tmp_path):
    alerts: list = []
    # 记录落在 k3/k4 两窗（注意 _T0 带 12:00 时刻，窗口按 12:00 对齐）：
    # 近两窗断供 → 末点 attainment=0 → burn_rate=10 > critical
    ats = ["2026-09-10T18:00:00+00:00", "2026-09-16T18:00:00+00:00"]
    p = _write_manifest(tmp_path, ats)
    summary = run_archive_sla_burnrate(p, clock=lambda: _T0, alert_sink=alerts.append)
    assert summary["status"] == "ran"
    assert summary["level"] in ("critical", "exhausted")
    assert len(alerts) == 1


def test_run_counts_corrupt_lines(tmp_path):
    p = _write_manifest(tmp_path, ["2026-09-29T00:00:00+00:00", "2026-09-22T00:00:00+00:00"])
    with open(p, "a", encoding="utf-8") as f:
        f.write("{broken\n")
    summary = run_archive_sla_burnrate(p, clock=lambda: _T0)
    assert summary["corrupt_lines"] == 1
    assert summary["status"] == "ran"


# ── 确定性 ───────────────────────────────────────────────────────────────


def test_run_same_input_same_output(tmp_path):
    ats = ["2026-09-29T00:00:00+00:00", "2026-09-20T00:00:00+00:00", "2026-09-13T00:00:00+00:00"]
    p = _write_manifest(tmp_path, ats)
    a = run_archive_sla_burnrate(p, clock=lambda: _T0)
    b = run_archive_sla_burnrate(p, clock=lambda: _T0)
    assert a == b
