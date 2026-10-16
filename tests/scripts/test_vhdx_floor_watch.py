# [MODULE] tests.scripts.test_vhdx_floor_watch
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] scripts.ops.vhdx_floor_watch (采样/告警面), pytest.MonkeyPatch
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 全部落 tmp 目录（测试禁写生产路径 data/ 与 .runtime/）；假 vhdx 文件实测采样行；
#              红线两侧/节流/告警双落点/格式与既有序列字段对齐/dry-run 零副作用
# [STABILITY] volatile
# [SAFETY] L
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_vhdx_floor_watch.py — D2 VHDX 采样+红线告警单测（st-diskp0-20261015）。

测试组:
- test_sample_row_format_alignment: 假 vhdx 实测采样行，字段与既有 3 行序列逐字段对齐
- test_below_red_line_alerts_dual_sink: 红线下 → workspace_alerts 件 + audit jsonl 行双落点
- test_above_red_line_no_alert: 红线上 → 零告警
- test_throttle_then_force: 60min 节流 + --force 立即采样
- test_flag_disabled_no_alert: flags.disk_floor.enabled=false → 只采样不告警
- test_dry_run_no_side_effect: dry-run 零写
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ops" / "vhdx_floor_watch.py"

#: 既有序列（data/audit-trail/vhdx_growth_series.jsonl）的字段集——格式对齐判据
_EXPECTED_FIELDS = {
    "ts",
    "vhdx_gb",
    "d_free_gb",
    "delta_vs_prev_gb",
    "d_red_line_gb",
    "d_below_red_line",
    "d_red_line_reason",
}


def _load_module(monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("vhdx_floor_watch_under_test", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """tmp 全套环境：假 vhdx + 空 series + flags（min_free_gib 可按用例覆写）。"""
    mod = _load_module(monkeypatch)
    root = tmp_path / "repo"
    vhdx = tmp_path / "fake.vhdx"
    vhdx.write_bytes(b"x" * 4096)
    series = root / "data" / "audit-trail" / "vhdx_growth_series.jsonl"
    series.parent.mkdir(parents=True, exist_ok=True)
    flags = root / "config" / "flags.yaml"
    flags.parent.mkdir(parents=True, exist_ok=True)
    flags.write_text("flags:\n  disk_floor:\n    enabled: true\n    min_free_gib: 15\n", encoding="utf-8")

    def _set_floor(enabled: bool = True, gib: float = 15.0) -> None:
        flags.write_text(
            f"flags:\n  disk_floor:\n    enabled: {str(enabled).lower()}\n    min_free_gib: {gib}\n",
            encoding="utf-8",
        )

    return {"mod": mod, "root": root, "vhdx": vhdx, "series": series, "set_floor": _set_floor}


def test_sample_row_format_alignment(env, monkeypatch):
    """假 vhdx 实测：采样行落盘且字段与既有序列逐字段对齐。"""
    e = env
    import shutil as _sh

    real_free = _sh.disk_usage(str(e["root"])).free
    r = e["mod"].sample_once(
        repo_root=e["root"],
        vhdx_path=e["vhdx"],
        series_path=e["series"],
        alert_dir=e["root"] / ".runtime" / "workspace_alerts",
        audit_dir=e["root"] / ".runtime" / "audit",
        force=True,
    )
    assert r["action"] == "sampled", r
    row = r["row"]
    assert set(row) >= _EXPECTED_FIELDS, f"字段不对齐: {sorted(row)}"
    assert row["vhdx_gb"] == round(4096 / e["mod"].GIB, 1) or row["vhdx_gb"] == 0.0, row
    # D 盘是活盘（他会话在写）——采样与断言之间 free 会漂移，用 2GiB 松带
    now_free = _sh.disk_usage(str(e["root"])).free / e["mod"].GIB
    assert abs(row["d_free_gb"] - now_free) < 2.0, (row["d_free_gb"], now_free)
    lines = e["series"].read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert set(json.loads(lines[0])) >= _EXPECTED_FIELDS, "落盘行字段不对齐"


def test_below_red_line_alerts_dual_sink(env, monkeypatch):
    """红线下：workspace_alerts 告警件 + disk_floor_alerts.jsonl 审计行双落点。"""
    e = env
    e["set_floor"](gib=10**9)  # 巨大地板=必破线
    alert_dir = e["root"] / ".runtime" / "workspace_alerts"
    audit_dir = e["root"] / ".runtime" / "audit"
    r = e["mod"].sample_once(
        repo_root=e["root"],
        vhdx_path=e["vhdx"],
        series_path=e["series"],
        alert_dir=alert_dir,
        audit_dir=audit_dir,
        force=True,
    )
    assert r["below"] is True
    assert r["alert"] and r["alert"]["alert_file"], "告警件未落"
    assert Path(r["alert"]["alert_file"]).exists()
    body = json.loads(Path(r["alert"]["alert_file"]).read_text(encoding="utf-8"))
    assert body["event"] == "disk_floor_breach" and body["severity"] == "escalated"
    assert body["note"] and "零自动删停" in body["note"], "告警必须声明零删停"
    audit_lines = (audit_dir / e["mod"].ALERT_AUDIT_FILENAME).read_text(encoding="utf-8").strip().splitlines()
    assert len(audit_lines) == 1 and json.loads(audit_lines[0])["event"] == "disk_floor_breach"


def test_above_red_line_no_alert(env):
    """红线上（剩余远大于地板）：零告警双落点。"""
    e = env
    e["set_floor"](gib=0.0000001)
    alert_dir = e["root"] / ".runtime" / "workspace_alerts"
    audit_dir = e["root"] / ".runtime" / "audit"
    r = e["mod"].sample_once(
        repo_root=e["root"],
        vhdx_path=e["vhdx"],
        series_path=e["series"],
        alert_dir=alert_dir,
        audit_dir=audit_dir,
        force=True,
    )
    assert r["below"] is False and r["alert"] is None
    assert not any(alert_dir.iterdir()) if alert_dir.exists() else True


def test_throttle_then_force(env):
    """60min 节流（读序列末行判距）+ force 立即采样。"""
    e = env
    kw = dict(
        repo_root=e["root"],
        vhdx_path=e["vhdx"],
        series_path=e["series"],
        alert_dir=e["root"] / ".runtime" / "workspace_alerts",
        audit_dir=e["root"] / ".runtime" / "audit",
    )
    r1 = e["mod"].sample_once(**kw, force=True)
    assert r1["action"] == "sampled"
    r2 = e["mod"].sample_once(**kw, min_interval_min=60)
    assert r2["action"] == "throttled", "fresh 末行应被节流"
    r3 = e["mod"].sample_once(**kw, min_interval_min=60, force=True)
    assert r3["action"] == "sampled"
    assert r3["row"]["delta_vs_prev_gb"] == 0.0, "同 vhdx 二采 delta 应为 0"


def test_flag_disabled_no_alert(env):
    """flags.disk_floor.enabled=false → 采样行 reason=disabled 且零告警。"""
    e = env
    e["set_floor"](enabled=False, gib=10**9)
    alert_dir = e["root"] / ".runtime" / "workspace_alerts"
    r = e["mod"].sample_once(
        repo_root=e["root"],
        vhdx_path=e["vhdx"],
        series_path=e["series"],
        alert_dir=alert_dir,
        audit_dir=e["root"] / ".runtime" / "audit",
        force=True,
    )
    assert r["below"] is False and r["alert"] is None
    assert r["row"]["d_red_line_reason"] == "disabled"


def test_dry_run_no_side_effect(env):
    """dry-run：返回行但零写盘。"""
    e = env
    r = e["mod"].sample_once(
        repo_root=e["root"],
        vhdx_path=e["vhdx"],
        series_path=e["series"],
        alert_dir=e["root"] / ".runtime" / "workspace_alerts",
        audit_dir=e["root"] / ".runtime" / "audit",
        force=True,
        dry_run=True,
    )
    assert r.get("dry_run") is True and r["row"] is not None
    assert not e["series"].exists(), "dry-run 不得写序列"
