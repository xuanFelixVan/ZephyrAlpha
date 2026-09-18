# [BLUEPRINT] MOD-AUTO-L1-001 | docs/_working/automation/campaign/blueprints/onboard_source_blueprint.md | §测试
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] tests.data.test_onboard_source
# [DOMAIN] D_DATA
# [INVARIANTS] 零网络零 CH——解析/渲染/校验纯函数直喷；临时目录隔离（宪法 §9.6）
# [TTL] permanent
"""上架流水线 v0 测试：源卡片校验/DDL 规则/frankfurter 解析/schtasks 命令渲染。"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
for p in ("scripts", "scripts/data"):
    if str(REPO_ROOT / p) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / p))

import onboard_source as ob  # noqa: E402
import fx_ecb_ingest as fx  # noqa: E402


def _card(**over):
    base = yaml.safe_load((REPO_ROOT / "config" / "source_cards" / "fx_ecb.yaml").read_text(encoding="utf-8"))
    base.update(over)
    return base


def test_load_card_real_card_passes():
    card = ob.load_card(REPO_ROOT / "config" / "source_cards" / "fx_ecb.yaml")
    assert card["table"] == "c1_market.alt_fx_rate_ecb"


def test_load_card_missing_field_raises(tmp_path):
    bad = _card()
    bad.pop("task_name")
    p = tmp_path / "bad.yaml"
    p.write_text(yaml.safe_dump(bad, allow_unicode=True), encoding="utf-8")
    with pytest.raises(KeyError):
        ob.load_card(p)


def test_ddl_rules():
    """库规三铁：ReplacingMergeTree/DateTime64(3) 时区/PARTITION toYYYYMM+自然键。"""
    mod = importlib.import_module("schemas.categories.market.market_alt_fx_rate_ecb")
    ddl = mod.FX_RATE_ECB_DDL
    assert "ReplacingMergeTree" in ddl
    assert "DateTime64(3, 'UTC')" in ddl
    assert "PARTITION BY toYYYYMM(trade_date)" in ddl
    assert "ORDER BY (trade_date, base, quote)" in ddl
    assert mod.TABLE_NAME == "c1_market.alt_fx_rate_ecb"
    assert mod.INSERT_COLUMNS == ("trade_date", "base", "quote", "rate")


def test_parse_series_holiday_and_sort():
    payload = {"rates": {
        "2026-09-15": {"CNY": 7.10, "JPY": 146.0},
        "2026-09-14": {"CNY": 7.12},  # JPY 缺价=假日，应跳过
    }}
    rows = fx.parse_series(payload, [("USD", "CNY"), ("USD", "JPY")])
    assert rows == [
        ("2026-09-14", "USD", "CNY", 7.12),
        ("2026-09-15", "USD", "CNY", 7.10),
        ("2026-09-15", "USD", "JPY", 146.0),
    ]


def test_parse_series_empty_payload():
    assert fx.parse_series({}, [("USD", "CNY")]) == []


def test_build_task_cmd_shape():
    cmd = ob.build_task_cmd(_card())
    assert cmd[0] == "schtasks" and "/tn" in cmd and "ZephyrAlpha_AltFxECB" in cmd
    assert "/sc" in cmd and "weekly" in cmd
    assert "MON,TUE,WED,THU,FRI" in cmd and "23:30" in cmd
    assert "fx_ecb_ingest.py" in " ".join(cmd)


# ---- 批量模式（WO-③-03：--cards-dir 单卡失败不炸批+末尾汇总表）----

def _write_card(tmp_path, name, **over):
    p = tmp_path / name
    p.write_text(yaml.safe_dump(_card(**over), allow_unicode=True), encoding="utf-8")
    return p


def test_batch_verify_all_ok(tmp_path, monkeypatch, capsys):
    _write_card(tmp_path, "a.yaml")
    _write_card(tmp_path, "b.yaml")
    monkeypatch.setattr(ob, "verify",
                        lambda card: {"table": card["table"], "rows": 5,
                                      "latest_date": "2026-09-17", "task_state": "Ready"})
    rc = ob.run_batch(tmp_path, "verify")
    out = capsys.readouterr().out
    assert rc == 0
    assert "a.yaml" in out and "b.yaml" in out
    assert '"fail": 0' in out
    assert "rows=5" in out


def test_batch_single_card_failure_continues(tmp_path, monkeypatch, capsys):
    _write_card(tmp_path, "good.yaml")
    bad = _card()
    bad.pop("task_name")  # 缺必备字段 → load_card KeyError
    (tmp_path / "bad.yaml").write_text(yaml.safe_dump(bad, allow_unicode=True), encoding="utf-8")
    monkeypatch.setattr(ob, "verify",
                        lambda card: {"table": card["table"], "rows": 1,
                                      "latest_date": "2026-09-17", "task_state": "Ready"})
    rc = ob.run_batch(tmp_path, "verify")
    out = capsys.readouterr().out
    assert rc == 1  # 单卡失败→批非零退出，但不炸批
    lines = [ln for ln in out.splitlines() if ln.startswith(("good.yaml", "bad.yaml"))]
    assert any("ok" in ln.split() for ln in lines if ln.startswith("good.yaml"))
    assert any("fail" in ln.split() and "KeyError" in ln for ln in lines if ln.startswith("bad.yaml"))
    assert '"fail": 1' in out and '"ok": 1' in out


def test_batch_verify_error_payload_counts_fail(tmp_path, monkeypatch):
    """fail-visible：verify 载荷带 error（CH 故障）不得伪装成 ok。"""
    _write_card(tmp_path, "a.yaml")
    monkeypatch.setattr(ob, "verify", lambda card: {"table": card["table"],
                                                    "error": "CH 查询失败: connection refused"})
    rc = ob.run_batch(tmp_path, "verify")
    assert rc == 1


def test_batch_empty_dir_returns_2(tmp_path, capsys):
    rc = ob.run_batch(tmp_path, "verify")
    out = capsys.readouterr().out
    assert rc == 2 and "batch_error" in out


def test_cli_card_and_cards_dir_mutually_exclusive(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["onboard_source.py", "--card", "x.yaml",
                                      "--cards-dir", "d", "--mode", "verify"])
    with pytest.raises(SystemExit) as ei:
        ob.main()
    assert ei.value.code == 2  # argparse 互斥组冲突
    capsys.readouterr()
