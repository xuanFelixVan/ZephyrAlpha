# [BLUEPRINT] MOD-L00-004 | tests/zephyr/data/test_data_service.py
# [MODULE] tests.zephyr.data.test_data_service
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.data_service; zephyr.data.pit_query; zephyr.shared.contracts.selection_result
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-004 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DataService 单元测试——统一数据服务门面（CAND-DAT-008 / B13-04033）。

覆盖四能力一口径 + SLA：
    1. 实时查询：Redis 读端 <5ms SLA 判定、缺后端 fail-closed、键缺失合法 miss
    2. PIT 回测：AS OF JOIN 委派 + 双时态（认知截止 × 业务时点过滤）
    3. 决策输入打包：因子+信号 → L3 SignalInput 契约（无效信号剔除、universe 派生）
    4. 审计追溯：血缘上下游 + 事件 → 合规报告
    5. sla_report：各能力调用计数/违约计数/最坏延迟
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from zephyr.data.data_service import (
    SLA_TARGETS,
    DataService,
    DataServiceError,
)
from zephyr.shared.contracts.factor_signal import FactorSignal
from zephyr.shared.contracts.selection_result import SignalInput

UTC = timezone.utc


# ── 测试替身 ──


class _FakeClock:
    """每次调用前进 step 秒的假 perf_counter。"""

    def __init__(self, step: float = 0.001):
        self.t = 0.0
        self.step = step

    def __call__(self) -> float:
        self.t += self.step
        return self.t


class _FakeRedis:
    def __init__(self, data: dict[str, dict] | None = None):
        self.data = data or {}

    def hgetall(self, key: str) -> dict:
        return self.data.get(key, {})


class _FakePIT:
    """FinancialPITQuery 替身：返回固定 TSV。"""

    def __init__(self, tsv: str):
        self.tsv = tsv
        self.calls: list[tuple] = []

    def as_of(self, table: str, symbol: str, query_time, columns: str = "*") -> str:
        self.calls.append((table, symbol, str(query_time), columns))
        return self.tsv


class _FakeLineage:
    def __init__(self):
        self.up = {"signal.x": ["factor.y", "market.kline"]}
        self.down = {"signal.x": ["portfolio.z"]}

    def get_upstream(self, node: str) -> list[str]:
        return self.up.get(node, [])

    def get_downstream(self, node: str) -> list[str]:
        return self.down.get(node, [])


def _factor_signal(symbol: str = "000001.SZ", valid: bool = True) -> FactorSignal:
    return FactorSignal(
        as_of_date=datetime(2026, 8, 25, tzinfo=UTC),
        factor_id="momentum_20d",
        idempotency_key=f"k-{symbol}",
        raw_value=0.83,
        symbol=symbol,
        is_valid=valid,
    )


# ── 1. 实时查询（Redis GET <5ms）──


class TestRealtimeQuery:
    def test_hit_within_sla(self):
        svc = DataService(redis_client=_FakeRedis({"tick:000001.SZ:latest": {"price": "12.5"}}), clock=_FakeClock(0.001))
        result = svc.get_realtime("000001.SZ")
        assert result.ok is True
        assert result.value == {"price": "12.5"}
        assert result.sla_met is True
        assert result.latency_ms < SLA_TARGETS["realtime"]

    def test_sla_violation_when_slow(self):
        svc = DataService(redis_client=_FakeRedis({"tick:000001.SZ:latest": {"price": "12.5"}}), clock=_FakeClock(0.010))
        result = svc.get_realtime("000001.SZ")
        assert result.ok is True
        assert result.sla_met is False  # 10ms > 5ms SLA

    def test_missing_key_is_legit_miss(self):
        svc = DataService(redis_client=_FakeRedis({}), clock=_FakeClock())
        result = svc.get_realtime("000001.SZ")
        assert result.ok is False and result.value is None

    def test_no_backend_fail_closed(self):
        svc = DataService(clock=_FakeClock())
        with pytest.raises(DataServiceError):
            svc.get_realtime("000001.SZ")


# ── 2. PIT 回测（AS OF JOIN + 双时态）──

_TSV = "000001.SZ\t2026-03-31\t2026-04-15\t100\n000001.SZ\t2026-06-30\t2026-08-20\t120"
_COLS = ["symbol", "report_period", "announce_date", "net_profit"]


class TestPITQuery:
    def test_as_of_delegates_and_parses(self):
        pit = _FakePIT(_TSV)
        svc = DataService(pit=pit, clock=_FakeClock())
        records = svc.query_pit(
            "balance_sheet", "000001.SZ", date(2026, 8, 25), columns=",".join(_COLS)
        )
        assert pit.calls[0][0] == "balance_sheet"
        assert len(records) == 2
        # 双时态字段齐备：业务时点 report_period + 认知时点 announce_date
        assert records[0]["report_period"] == "2026-03-31"
        assert records[0]["announce_date"] == "2026-04-15"

    def test_bitemporal_filter(self):
        pit = _FakePIT(_TSV)
        svc = DataService(pit=pit, clock=_FakeClock())
        # 认知截止 2026-08-25（两期均已公告），业务时点 2026-05-01 → 仅 Q1 可见
        records = svc.query_pit_bitemporal(
            "balance_sheet",
            "000001.SZ",
            valid_time=date(2026, 5, 1),
            knowledge_time=date(2026, 8, 25),
            columns=",".join(_COLS),
        )
        assert [r["report_period"] for r in records] == ["2026-03-31"]

    def test_no_pit_backend_fail_closed(self):
        svc = DataService(clock=_FakeClock())
        with pytest.raises(DataServiceError):
            svc.query_pit("balance_sheet", "000001.SZ", date(2026, 8, 25))


# ── 3. 决策输入打包（因子+信号 → L3 契约）──


class TestPackDecisionInput:
    def test_pack_filters_invalid_and_derives_universe(self):
        svc = DataService(clock=_FakeClock())
        signals = [_factor_signal("000001.SZ"), _factor_signal("600000.SH"), _factor_signal("bad.X", valid=False)]
        packed = svc.pack_decision_input(
            signals=signals,
            as_of_date=date(2026, 8, 25),
            regime_budget=0.6,
        )
        assert isinstance(packed, SignalInput)
        assert packed.as_of_date == date(2026, 8, 25)
        assert packed.regime_budget == 0.6
        assert packed.universe == ["000001.SZ", "600000.SH"]  # 无效信号剔除后派生
        assert len(packed.signals) == 2

    def test_explicit_universe_respected(self):
        svc = DataService(clock=_FakeClock())
        packed = svc.pack_decision_input(
            signals=[_factor_signal()],
            as_of_date=date(2026, 8, 25),
            universe=["000001.SZ", "300750.SZ"],
            regime_budget=1.0,
        )
        assert packed.universe == ["000001.SZ", "300750.SZ"]


# ── 4. 审计追溯（血缘+事件 → 合规报告）──


class TestAuditTrail:
    def test_lineage_and_events_aggregated(self):
        svc = DataService(
            lineage_tracker=_FakeLineage(),
            event_reader=lambda node: [{"event": "read", "node": node, "at": "2026-08-25T10:00:00"}],
            clock=_FakeClock(),
        )
        report = svc.audit_trail("signal.x")
        assert report["node"] == "signal.x"
        assert report["upstream"] == ["factor.y", "market.kline"]
        assert report["downstream"] == ["portfolio.z"]
        assert len(report["events"]) == 1
        assert "generated_at" in report

    def test_no_backends_returns_empty_trail(self):
        svc = DataService(clock=_FakeClock())
        report = svc.audit_trail("signal.x")
        assert report["upstream"] == [] and report["downstream"] == [] and report["events"] == []


# ── 5. SLA 汇总 ──


class TestSLAReport:
    def test_sla_report_counts(self):
        svc = DataService(redis_client=_FakeRedis({"tick:000001.SZ:latest": {"p": "1"}}), clock=_FakeClock(0.001))
        svc.get_realtime("000001.SZ")
        svc.get_realtime("000001.SZ")
        report = svc.sla_report()
        assert report["realtime"]["calls"] == 2
        assert report["realtime"]["violations"] == 0
        assert report["realtime"]["sla_ms"] == SLA_TARGETS["realtime"]

    def test_sla_violation_counted(self):
        svc = DataService(redis_client=_FakeRedis({"tick:000001.SZ:latest": {"p": "1"}}), clock=_FakeClock(0.010))
        svc.get_realtime("000001.SZ")
        assert svc.sla_report()["realtime"]["violations"] == 1
