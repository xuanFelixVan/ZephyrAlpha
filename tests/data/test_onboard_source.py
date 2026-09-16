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
