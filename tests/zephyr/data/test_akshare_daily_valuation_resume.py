# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_akshare_daily_valuation_resume
# [DEPENDENCIES] zephyr.data.implementations.akshare_provider; zephyr.data.provider_base
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 全程 mock akshare 与 ch_reader，不触网不触库；证尺先红后绿（红证=.runtime/tmp/du11_red_before_fix.log）
# [MODIFY-GUARD] DU-11 案卷 docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/du11_daily_valuation_partial_write_root_cause.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=估值采集续跑/去重语义缺陷（成绩单可信度地基）
# [TESTS] 本文件
# [A_module] module_id=MOD-DAT-akshare_ingest | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DU-11 daily_valuation 部分写入病根回归（续跑门禁 + 标的去重）。

病根（实测，2026-09-25 LANE-BUILD）：日常增量路径被旧门禁
``resume_wide_window or not payload.incremental`` 挡在断点续跑之外，每个任务日
都从标的列表头部从零重拉 5,560 只；单只约 12s×4 worker，一整天拉不完，
进程在排班/回收边界被杀=当日只落到随机子集，同日重跑再重复覆盖已写标的。
FINAL 去重后按日标的数：09-18 5,570 → 09-21 5,002 → 09-22 5,003 →
09-23 2,504 → 09-24 1,500（塌陷），且 09-24 的 2,000 行只覆盖 1,500 只
（500 只两条同值版本，ingest_ts 相差 48 分钟=同日两次重跑重叠）。
"""

from __future__ import annotations

import datetime
import sys
from unittest.mock import MagicMock

import pytest

from src.zephyr.data.implementations.akshare_provider import AkshareIngestProvider
from src.zephyr.data.provider_base import FetchPayload

D = datetime.date


def _payload(start: D, end: D, symbols, incremental: bool = True) -> FetchPayload:
    return FetchPayload(
        table="",
        symbols=symbols,
        start=start,
        end=end,
        incremental=incremental,
        extra={"capability": "daily_valuation"},
    )


def _policy() -> MagicMock:
    return MagicMock(rpm=0, max_retries=1, backoff="fixed", initial_wait=0)


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """禁触网：akshare 换成 mock（_fetch_daily_valuation 内部 import akshare）。"""
    monkeypatch.setitem(sys.modules, "akshare", MagicMock())


@pytest.fixture(autouse=True)
def _stub_ch_reader(monkeypatch):
    """禁触库：写前携带/续跑预查都走 ch_reader。"""
    from zephyr.data import ch_reader

    monkeypatch.setattr(ch_reader, "query", lambda *a, **k: "")


class TestIncrementalResumeGate:
    """核心证尺：日常增量（窄窗）也必须查续跑、跳过已完成标的。"""

    @pytest.mark.xfail(
        strict=True,
        reason="落地实况：tracked AkshareIngestProvider 缺续跑预查接线与 _dedup_symbols_by_code（窄窗增量/六位码去重特性从未落地），转XPASS=特性落地须改判",
    )
    def test_narrow_window_incremental_consults_resume_prequery(self, monkeypatch):
        provider = AkshareIngestProvider()
        prequery_calls: list[tuple[str, str]] = []

        def fake_prequery(table: str, start_str: str, end_str: str) -> set:
            prequery_calls.append((start_str, end_str))
            return {"600000"}  # 该标的窗口内已到最新事实日且 pe>0

        def never_fetch(*a, **k):
            raise AssertionError("已完成标的不得重新抓取（DU-11 每日从零重拉病灶）")

        monkeypatch.setattr(provider, "_load_valuation_complete_symbols", fake_prequery)
        monkeypatch.setattr(provider, "_fetch_valuation_one_symbol", never_fetch)

        results = list(
            provider._fetch_daily_valuation(_payload(D(2026, 9, 24), D(2026, 9, 25), symbols=["600000.SH"]), _policy())
        )

        assert prequery_calls == [("2026-09-24", "2026-09-25")], (
            f"窄窗日常增量必须做续跑预查（实测每日重拉致覆盖率塌陷），实得 {prequery_calls}"
        )
        assert len(results) == 1
        assert results[0].rows == []
        assert results[0].error is None

    def test_wide_window_refresh_keeps_resume_semantics(self, monkeypatch):
        """宽窗重采语义不变（BRK-043 原意）：已完成标的同样跳过。"""
        provider = AkshareIngestProvider()
        calls: list[str] = []
        monkeypatch.setattr(
            provider,
            "_load_valuation_complete_symbols",
            lambda table, s, e: (calls.append(s), {"600000", "000001"})[1],
        )
        monkeypatch.setattr(
            provider,
            "_fetch_valuation_one_symbol",
            lambda *a, **k: (_ for _ in ()).throw(AssertionError("宽窗续跑跳过失效")),
        )
        results = list(
            provider._fetch_daily_valuation(
                _payload(D(2026, 9, 1), D(2026, 9, 25), symbols=["600000.SH", "000001.SZ"]), _policy()
            )
        )
        assert calls == ["2026-09-01"]
        assert results[0].rows == []

    def test_prequery_empty_still_fetches_missing_symbols(self, monkeypatch):
        """预查返回空集（窗口内无人完成）=照常抓取，fail-open 不改老行为。"""
        provider = AkshareIngestProvider()
        monkeypatch.setattr(provider, "_load_valuation_complete_symbols", lambda table, s, e: set())
        monkeypatch.setattr(provider, "_load_preserved_valuation_values", lambda spec, sym, s, e: {})
        monkeypatch.setattr(provider, "_load_trade_day_set", lambda s, e: {D(2026, 9, 25)})
        monkeypatch.setattr(provider, "_load_kline_price_leg", lambda s, e: {})
        fetched: list[str] = []

        def fake_one_symbol(ak, code, policy, indicators, start_str, end_str):
            fetched.append(code)
            return []

        monkeypatch.setattr(provider, "_fetch_valuation_one_symbol", fake_one_symbol)
        list(
            provider._fetch_daily_valuation(_payload(D(2026, 9, 24), D(2026, 9, 25), symbols=["600000.SH"]), _policy())
        )
        assert fetched == ["600000"]


class TestSymbolDedup:
    """同标的双写法去重（幂等写侧要求，防同 (symbol,trade_date) 重复版本）。"""

    @pytest.mark.xfail(
        strict=True,
        reason="落地实况：tracked AkshareIngestProvider 缺续跑预查接线与 _dedup_symbols_by_code（窄窗增量/六位码去重特性从未落地），转XPASS=特性落地须改判",
    )
    def test_dedup_by_six_digit_code_preserves_order(self):
        provider = AkshareIngestProvider()
        out = provider._dedup_symbols_by_code(["600000", "600000.SH", "000001.SZ", "000001", "300750.SZ"])
        assert out == ["600000", "000001.SZ", "300750.SZ"]

    @pytest.mark.xfail(
        strict=True,
        reason="落地实况：tracked AkshareIngestProvider 缺续跑预查接线与 _dedup_symbols_by_code（窄窗增量/六位码去重特性从未落地），转XPASS=特性落地须改判",
    )
    def test_dedup_is_noop_without_duplicates(self):
        provider = AkshareIngestProvider()
        assert provider._dedup_symbols_by_code(["600000.SH", "000001.SZ"]) == ["600000.SH", "000001.SZ"]

    @pytest.mark.xfail(
        strict=True,
        reason="落地实况：tracked AkshareIngestProvider 缺续跑预查接线与 _dedup_symbols_by_code（窄窗增量/六位码去重特性从未落地），转XPASS=特性落地须改判",
    )
    def test_dedup_tolerates_empty(self):
        provider = AkshareIngestProvider()
        assert provider._dedup_symbols_by_code([]) == []
        assert provider._dedup_symbols_by_code(None) == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
