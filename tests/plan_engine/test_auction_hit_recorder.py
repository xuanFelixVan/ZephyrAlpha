# [A_test] module_id: MOD-PLAN-015 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-015 | 待统筹登记 | 缺口总账 GAP-F-08 + 45号 §4 W3
# [MODULE] tests.plan_engine.test_auction_hit_recorder
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""AuctionHitRecorder (MOD-PLAN-015) 施工验证测试。

覆盖：
- 盘中命中判定：mock 指数日线（开盘桶）+ ETF 分钟窗（走势桶）→ 9 格命中格；
  命中判定复用 MOD-PLAN-008 determine_actual_scenario 口径。
- 竞价三细节透传：注入 AuctionVerification → payload 携 D1/D2/D3/昨涨停溢价；
  fake_ratio>0.6 → direction_void=True 红色留痕；未注入 → auction=None 不炸。
- 落库：prediction_type="auction_hit" 幂等保首条；hit=（命中格==预案 final_scenario）；
  无预案行 → hit=None 仍落库（W3 观察哨只看命中格）；落库失败 fail-open。
- 降级路径：无开盘数据 skipped:no_open_data；分钟缺失走 daily_proxy 留痕；
  代理禁用 skipped:no_trend_data；CH 异常 fail-open。
- 契约：trade_date 非法 fail-closed；to_dict JSON 可序列化。
全 mock CH + tmp 库隔离，不触真 governance.db 与真 ClickHouse。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.plan_engine.auction_hit_recorder import (
    MODULE_LOG_NAME,
    PREDICTION_TYPE_AUCTION_HIT,
    AuctionHitConfig,
    record_auction_hit,
)
from zephyr.plan_engine.scenario_planner import AuctionVerification
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
    query_predictions,
)

TRADE_DATE = "2026-08-21"
PREV_DATE = "2026-08-20"


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    db = tmp_path / "governance.db"
    ensure_prediction_log_table(db)
    return db


def _index_tsv(today_open: float = 3910.0, today_close: float = 3920.0, prev_close: float = 3900.0) -> str:
    return f"{TRADE_DATE}\t{today_open}\t{today_close}\n{PREV_DATE}\t3895.0\t{prev_close}"


def _etf_tsv(vwap: float = 4.05, last_close: float = 4.10, n: int = 30) -> str:
    vol = n * 10000.0
    return f"{vol * vwap}\t{vol}\t{last_close}\t{n}"


def _make_ch(index_tsv: str = "", etf_tsv: str = "", raise_on: str | None = None):
    def _ch(sql: str) -> str:
        if "kline_etf_1min" in sql:
            if raise_on == "etf":
                raise RuntimeError("etf boom")
            return etf_tsv
        if "kline_index" in sql:
            if raise_on == "index":
                raise RuntimeError("index boom")
            return index_tsv
        return ""

    return _ch


def _seed_plan(db: Path, final_scenario: str = "FLAT_OPEN_REAL_UP") -> None:
    log_prediction(
        trade_date=TRADE_DATE,
        module="plan_engine.scenario_planner",
        prediction_type="scenario_plan",
        payload={"final_scenario": final_scenario, "confidence_scale": 1.0},
        db_path=db,
    )


def _auction(fake_ratio: float | None = 0.3) -> AuctionVerification:
    return AuctionVerification(
        deviation=0.004,
        volume_ratio=1.35,
        fake_ratio=fake_ratio,
        yesterday_limit_premium=0.021,
        direction="UP",
        direction_consistent=True,
        confirmed=True,
        volume_shrink=False,
        direction_void=(fake_ratio or 0.0) > 0.6,
        status="ok",
        detail={"n_symbols": 5213},
    )


# ── 输入校验 ──


def test_trade_date_invalid() -> None:
    with pytest.raises(ValueError):
        record_auction_hit("2026/08/21", ch_client=_make_ch(), db_path=None)
    with pytest.raises(ValueError):
        record_auction_hit("20260821", ch_client=_make_ch(), db_path=None)


def test_config_invalid() -> None:
    with pytest.raises(ValueError):
        AuctionHitConfig(open_threshold=0.0)


# ── 命中判定主链路 ──


def test_hit_flat_up_match_plan(tmp_db: Path) -> None:
    # 开盘 +0.26%（平开）+ 走势 +1.2%（高走）→ FLAT_OPEN_REAL_UP；预案同格 → hit=True
    _seed_plan(tmp_db, "FLAT_OPEN_REAL_UP")
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(_index_tsv(), _etf_tsv()),
        db_path=tmp_db,
        auction=_auction(),
    )
    assert verdict.status == "ok"
    assert verdict.actual_scenario == "FLAT_OPEN_REAL_UP"
    assert verdict.hit is True
    assert verdict.matched_plan_scenario == "FLAT_OPEN_REAL_UP"
    assert verdict.direction_void is False
    assert verdict.row_id is not None and verdict.row_id > 0
    rows = query_predictions(
        trade_date=TRADE_DATE,
        module=MODULE_LOG_NAME,
        prediction_type=PREDICTION_TYPE_AUCTION_HIT,
        db_path=tmp_db,
    )
    assert len(rows) == 1
    payload = json.loads(rows[0]["payload_json"])
    assert payload["phase"] == "intraday_1000"
    assert payload["auction"]["fake_ratio"] == pytest.approx(0.3)
    assert payload["auction"]["volume_ratio"] == pytest.approx(1.35)


def test_hit_miss_when_plan_diverges(tmp_db: Path) -> None:
    _seed_plan(tmp_db, "HIGH_OPEN_REAL_UP")
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(_index_tsv(), _etf_tsv()),
        db_path=tmp_db,
    )
    assert verdict.status == "ok"
    assert verdict.hit is False
    assert verdict.matched_plan_scenario == "HIGH_OPEN_REAL_UP"


def test_no_plan_row_still_persists(tmp_db: Path) -> None:
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(_index_tsv(), _etf_tsv()),
        db_path=tmp_db,
    )
    assert verdict.status == "ok"
    assert verdict.hit is None
    assert verdict.matched_plan_scenario is None
    assert verdict.row_id is not None and verdict.row_id > 0


def test_direction_void_on_high_fake_ratio(tmp_db: Path) -> None:
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(_index_tsv(), _etf_tsv()),
        db_path=tmp_db,
        auction=_auction(fake_ratio=0.75),
    )
    assert verdict.direction_void is True
    assert any("虚假申报" in a or "作废" in a for a in verdict.annotations)
    rows = query_predictions(
        trade_date=TRADE_DATE,
        module=MODULE_LOG_NAME,
        prediction_type=PREDICTION_TYPE_AUCTION_HIT,
        db_path=tmp_db,
    )
    payload = json.loads(rows[0]["payload_json"])
    assert payload["direction_void"] is True


def test_auction_none_ok(tmp_db: Path) -> None:
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(_index_tsv(), _etf_tsv()),
        db_path=tmp_db,
        auction=None,
    )
    assert verdict.status == "ok"
    rows = query_predictions(
        trade_date=TRADE_DATE,
        module=MODULE_LOG_NAME,
        prediction_type=PREDICTION_TYPE_AUCTION_HIT,
        db_path=tmp_db,
    )
    payload = json.loads(rows[0]["payload_json"])
    assert payload["auction"] is None


def test_idempotent_rerun(tmp_db: Path) -> None:
    ch = _make_ch(_index_tsv(), _etf_tsv())
    v1 = record_auction_hit(TRADE_DATE, ch_client=ch, db_path=tmp_db)
    v2 = record_auction_hit(TRADE_DATE, ch_client=ch, db_path=tmp_db)
    assert v1.row_id == v2.row_id  # 幂等保首条
    rows = query_predictions(
        trade_date=TRADE_DATE,
        module=MODULE_LOG_NAME,
        prediction_type=PREDICTION_TYPE_AUCTION_HIT,
        db_path=tmp_db,
    )
    assert len(rows) == 1


# ── 降级路径 ──


def test_skip_no_open_data(tmp_db: Path) -> None:
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(index_tsv="", etf_tsv=_etf_tsv()),
        db_path=tmp_db,
    )
    assert verdict.status == "skipped:no_open_data"
    assert verdict.row_id is None


def test_daily_proxy_fallback(tmp_db: Path) -> None:
    # 分钟缺失 → 日线代理（close-open)/open=+0.26% 高走；trend_source 留痕
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(_index_tsv(today_open=3910.0, today_close=3920.0), etf_tsv=""),
        db_path=tmp_db,
    )
    assert verdict.status == "ok"
    assert verdict.trend_source == "daily_proxy"
    assert verdict.actual_scenario == "FLAT_OPEN_REAL_UP"


def test_proxy_disabled_skips(tmp_db: Path) -> None:
    cfg = AuctionHitConfig(allow_daily_proxy=False)
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(_index_tsv(), etf_tsv=""),
        db_path=tmp_db,
        config=cfg,
    )
    assert verdict.status == "skipped:no_trend_data"
    assert verdict.row_id is None


def test_ch_exception_fail_open(tmp_db: Path) -> None:
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(raise_on="index"),
        db_path=tmp_db,
    )
    assert verdict.status == "skipped:no_open_data"  # 通道异常按缺数据降级，不炸


def test_high_open_down_trend_cell(tmp_db: Path) -> None:
    # 高开 +2.6% + 低走 -1.2% → HIGH_OPEN_FAKE_UP（假突破格）
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(
            _index_tsv(today_open=4001.0, prev_close=3900.0),
            _etf_tsv(vwap=4.05, last_close=4.00),
        ),
        db_path=tmp_db,
    )
    assert verdict.status == "ok"
    assert verdict.actual_scenario == "HIGH_OPEN_FAKE_UP"


def test_to_dict_json_serializable(tmp_db: Path) -> None:
    verdict = record_auction_hit(
        TRADE_DATE,
        ch_client=_make_ch(_index_tsv(), _etf_tsv()),
        db_path=tmp_db,
        auction=_auction(),
    )
    payload = verdict.to_dict()
    json.dumps(payload, ensure_ascii=False)
    assert payload["trade_date"] == TRADE_DATE
    assert payload["actual_scenario"] == "FLAT_OPEN_REAL_UP"
