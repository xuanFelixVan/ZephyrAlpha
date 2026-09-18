# [BLUEPRINT] MOD-AUTO-L1-001 | docs/_working/automation/campaign/blueprints/onboard_source_blueprint.md | §巡检测试（WO-③-04）
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] tests.data.test_source_health_patrol
# [DOMAIN] D_DATA
# [INVARIANTS] 零网络零 CH——verify_fn/alert_fn 全注入 fake；报告输出 tmp_path（宪法 §9.6）
# [TTL] permanent
"""源健康度周期巡检器测试：状态判定/degraded 不炸/告警路由/报告落盘。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
for p in ("scripts", "scripts/data"):
    if str(REPO_ROOT / p) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / p))

import source_health_patrol as shp  # noqa: E402


def _card_dir(tmp_path, names=("a.yaml", "b.yaml")):
    card = {
        "source_id": "s", "schema_module": "schemas.categories.market.market_alt_fx_rate_ecb",
        "table": "c1_market.alt_fx_rate_ecb", "ingest_script": "scripts/data/fx_ecb_ingest.py",
        "task_name": "T", "schedule": {"type": "weekly", "days": ["MON"], "time": "23:30"},
    }
    d = tmp_path / "cards"
    d.mkdir()
    for n in names:
        (d / n).write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return d


def _ok_verify(card):
    return {"table": card["table"], "rows": 9, "latest_date": "2026-09-17", "task_state": "Ready"}


def test_patrol_all_pass_and_report(tmp_path):
    d = _card_dir(tmp_path)
    report = shp.patrol(d, verify_fn=_ok_verify)
    assert report["overall"] == "pass"
    assert report["pass"] == 2 and report["fail"] == 0
    path = shp.write_report(report, tmp_path / "reports")
    assert re.fullmatch(r"\d{8}\.json", path.name)  # <YYYYMMDD>.json
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["overall"] == "pass" and loaded["total"] == 2


def test_patrol_empty_table_is_fail_with_alert(tmp_path):
    d = _card_dir(tmp_path, names=("only.yaml",))
    calls = []
    report = shp.patrol(d, verify_fn=lambda c: {"table": c["table"], "rows": 0,
                                                "latest_date": None, "task_state": "Ready"},
                        alert_fn=lambda *a, **k: calls.append(a))
    assert report["overall"] == "fail"
    assert report["cards"][0]["status"] == "fail"
    shp.alert(report, alert_fn=lambda *a, **k: calls.append(a))
    assert calls and calls[0][2] == "ERROR"  # (task_id, error, level, ...)


def test_patrol_ch_down_all_cards_degraded_no_alert_spam(tmp_path):
    """CH 断连：全卡 error→整体 degraded，单条 WARN，不炸批。"""
    d = _card_dir(tmp_path)
    calls = []
    report = shp.patrol(
        d, verify_fn=lambda c: {"table": c["table"], "error": "CH 查询失败: connection refused"},
        alert_fn=lambda *a, **k: calls.append(a))
    assert report["overall"] == "degraded"
    assert report["degraded_cards"] == 2
    shp.alert(report, alert_fn=lambda *a, **k: calls.append(a))
    assert len(calls) == 1 and calls[0][2] == "WARN"


def test_patrol_single_card_error_is_fail_family(tmp_path):
    """个别卡 error（非全卡）→该卡连接级故障，整体 fail。"""
    d = _card_dir(tmp_path)
    seq = {"n": 0}

    def verify(card):
        seq["n"] += 1
        if seq["n"] == 1:  # 第一张卡（排序后 a.yaml）连接故障
            return {"table": card["table"], "error": "CH 查询失败: timeout"}
        return _ok_verify(card)

    report = shp.patrol(d, verify_fn=verify)
    assert report["overall"] == "fail"
    statuses = [c["status"] for c in report["cards"]]
    assert statuses == ["error", "pass"]


def test_patrol_bad_card_file_fail_not_crash(tmp_path):
    d = tmp_path / "cards"
    d.mkdir()
    (d / "bad.yaml").write_text("source_id: x\n", encoding="utf-8")  # 缺必备字段
    calls = []
    report = shp.patrol(d, verify_fn=_ok_verify)
    assert report["overall"] == "fail"
    assert report["cards"][0]["status"] == "fail"
    shp.alert(report, alert_fn=lambda *a, **k: calls.append(a))
    assert calls and calls[0][2] == "ERROR"


def test_patrol_verify_raises_counts_as_error(tmp_path):
    d = _card_dir(tmp_path, names=("x.yaml",))

    def boom(card):
        raise RuntimeError("boom")

    report = shp.patrol(d, verify_fn=boom)
    assert report["overall"] == "degraded"  # 全卡 error → degraded 语义
    assert "boom" in report["cards"][0]["detail"]["error"]


def test_main_exit_codes_and_no_alert(tmp_path, monkeypatch, capsys):
    d = _card_dir(tmp_path)
    monkeypatch.setattr(shp.ob, "verify", _ok_verify)
    monkeypatch.setattr(sys, "argv", ["source_health_patrol.py", "--cards-dir", str(d),
                                      "--report-dir", str(tmp_path / "r"), "--no-alert"])
    assert shp.main() == 0
    out = capsys.readouterr().out
    assert "overall=pass" in out
    assert list((tmp_path / "r").glob("*.json"))

    monkeypatch.setattr(shp.ob, "verify",
                        lambda c: {"table": c["table"], "error": "CH 查询失败: x"})
    monkeypatch.setattr(sys, "argv", ["source_health_patrol.py", "--cards-dir", str(d),
                                      "--report-dir", str(tmp_path / "r"), "--no-alert"])
    assert shp.main() == 0  # 全卡 error=degraded → exit 0 不炸
    out = capsys.readouterr().out
    assert "overall=degraded" in out


def test_main_fail_exit_nonzero(tmp_path, monkeypatch, capsys):
    d = _card_dir(tmp_path, names=("only.yaml",))
    monkeypatch.setattr(shp.ob, "verify",
                        lambda c: {"table": c["table"], "rows": 0, "latest_date": None,
                                   "task_state": "Ready"})
    monkeypatch.setattr(sys, "argv", ["source_health_patrol.py", "--cards-dir", str(d),
                                      "--report-dir", str(tmp_path / "r"), "--no-alert"])
    assert shp.main() == shp.EXIT_FAIL
    capsys.readouterr()


def test_alert_no_alert_fn_default_uses_alerter(tmp_path, monkeypatch):
    """默认告警走 Alerter 正门（不抛契约：WARN 级只 log）。"""
    d = _card_dir(tmp_path)
    report = shp.patrol(d, verify_fn=lambda c: {"table": c["table"],
                                                "error": "CH 查询失败: refused"})
    sent = []
    import zephyr.data.alerter as al

    monkeypatch.setattr(al.Alerter, "notify",
                        lambda self, task_id, error, **kw: sent.append((task_id, kw.get("level"))))
    shp.alert(report)  # 不注入 alert_fn → 走 Alerter 正门
    assert sent == [(shp.TASK_ID, "WARN")]
