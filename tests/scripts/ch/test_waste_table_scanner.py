"""waste_table_scanner 纯逻辑单测（名字族匹配+登记册对账，零 CH 依赖）。"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "ch"))
import waste_table_scanner as ws  # noqa: E402


def test_patterns_match_all_17_families():
    samples = [
        "kline_etf_1min_tz_bak_20260918",
        "kline_1min_tzbak_20260914",
        "kline_daily_bak_256",
        "kline_daily_hfq_bak_20260915dup",
        "news_data_corrupt_20260828",
        "news_data_pre_tz2_20260828",
        "balance_sheet_bak_1970clean_20260914",
        "tick_data_tzbak_20260914",
        "auction_book_limit_bak_20260908",
    ]
    for name in samples:
        assert any(p.match(name) for p in ws.WASTE_PATTERNS), f"漏报: {name}"
    # 正常表禁误报
    for clean in ("kline_daily", "news_data", "tick_data", "balance_sheet", "macro_data"):
        assert not any(p.match(clean) for p in ws.WASTE_PATTERNS), f"误报: {clean}"


def test_registry_new_registration_and_no_delete(tmp_path, monkeypatch):
    reg = tmp_path / "waste_table_registry.yaml"
    monkeypatch.setattr(ws, "REGISTRY_FILE", reg)
    found = [
        {"table": "c1_market.foo_bak_20260101", "total_rows": 10},
        {"table": "c1_market.bar_corrupt", "total_rows": 20},
    ]
    res = ws.update_registry(found, discovered_by="test")
    assert len(res["new"]) == 2
    saved = yaml.safe_load(reg.read_text(encoding="utf-8"))
    assert len(saved["entries"]) == 2
    assert all(e["status"] == "待人工盘点" for e in saved["entries"])
    # 第二轮：已知表只刷 last_seen 不新增；且永不删除条目
    res2 = ws.update_registry(found[:1], discovered_by="test")
    assert res2["new"] == []
    saved2 = yaml.safe_load(reg.read_text(encoding="utf-8"))
    assert len(saved2["entries"]) == 2  # bar_corrupt 仍保留
    assert saved2["entries"][1]["last_seen"] == saved2["entries"][0]["last_seen"]
