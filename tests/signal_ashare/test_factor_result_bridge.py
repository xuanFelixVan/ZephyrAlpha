# [BLUEPRINT] MOD-SIG-087 | docs/03_modules/_domain_signal/factor_result_bridge/blueprint.md
# [MODULE] tests.signal_ashare.test_factor_result_bridge
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.factor_result_bridge
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 纯内存判定核心测试，provider/audit_sink 注入式，不触网不触库
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=版本裁定/降级透传/消费审计逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""FactorResultBridge 单元测试（CAND-TESTB-027 / B13-04307，D-SIGNAL-158）。

覆盖（min_build_spec）：
- 经 provider 注入取因子结果（CTR-002 适配器前瞻兼容，信号侧不直连因子存储）
- 版本兼容三态裁定：exact / compatible / unsupported（fail-closed 拒收）
- is_degraded 透传（上游降级标记原样带出，桥接器不制造降级）
- 消费审计：每次消费产不可变审计记录，audit_sink 异常不阻断
"""

from __future__ import annotations

import datetime

import pytest

from zephyr.signal_ashare.factor_result_bridge import (
    ConsumptionVerdict,
    FactorResultBatch,
    FactorResultBridge,
    FactorResultBridgeError,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, tzinfo=datetime.timezone.utc)


def _batch(version: str = "1.0", degraded: bool = False, n: int = 3) -> FactorResultBatch:
    return FactorResultBatch(
        schema_version=version,
        factor_values=(("momentum_20d", "000001.SZ", 0.42),) * n,
        as_of=_T0,
        is_degraded=degraded,
        metadata={"source": "ctr002_stub"},
    )


class TestVersionAdjudication:
    """版本兼容三态裁定。"""

    def test_exact_version_accepted(self) -> None:
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("1.0"))
        verdict = bridge.consume()
        assert verdict.accepted is True
        assert verdict.version_action == "exact"
        assert verdict.degraded is False
        assert verdict.batch is not None
        assert len(verdict.batch.factor_values) == 3

    def test_compatible_minor_version_passthrough(self) -> None:
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("1.3"))
        verdict = bridge.consume()
        assert verdict.accepted is True
        assert verdict.version_action == "compatible"

    def test_unsupported_major_version_rejected_fail_closed(self) -> None:
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("2.0"))
        verdict = bridge.consume()
        assert verdict.accepted is False
        assert verdict.version_action == "unsupported"
        assert "2.0" in verdict.reason
        # fail-closed：拒收时产空批次且标降级，绝不静默按错版本解析
        assert verdict.batch is not None
        assert verdict.batch.factor_values == ()
        assert verdict.degraded is True

    def test_custom_supported_versions(self) -> None:
        bridge = FactorResultBridge(
            provider=lambda as_of=None: _batch("2.1"),
            supported_versions=("2.0", "2.1"),
        )
        verdict = bridge.consume()
        assert verdict.accepted is True
        assert verdict.version_action == "exact"

    def test_malformed_version_rejected(self) -> None:
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("v1"))
        verdict = bridge.consume()
        assert verdict.accepted is False
        assert verdict.version_action == "unsupported"


class TestDegradedPassthrough:
    """is_degraded 透传。"""

    def test_upstream_degraded_passthrough(self) -> None:
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("1.0", degraded=True))
        verdict = bridge.consume()
        assert verdict.accepted is True
        assert verdict.degraded is True
        assert verdict.batch is not None and verdict.batch.is_degraded is True

    def test_bridge_does_not_manufacture_degradation(self) -> None:
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("1.0", degraded=False))
        verdict = bridge.consume()
        assert verdict.degraded is False


class TestConsumptionAudit:
    """消费审计。"""

    def test_audit_record_written_per_consume(self) -> None:
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("1.0"))
        bridge.consume()
        bridge.consume()
        log = bridge.audit_log
        assert len(log) == 2
        rec = log[0]
        assert rec["schema_version"] == "1.0"
        assert rec["accepted"] is True
        assert rec["value_count"] == 3
        assert rec["degraded"] is False
        assert "consumed_at" in rec and "as_of" in rec

    def test_audit_sink_receives_record(self) -> None:
        sink: list[dict] = []
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("1.0"), audit_sink=sink.append)
        bridge.consume()
        assert len(sink) == 1
        assert sink[0]["accepted"] is True

    def test_audit_sink_failure_does_not_block_consumption(self) -> None:
        def _boom(_rec: dict) -> None:
            raise RuntimeError("sink down")

        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("1.0"), audit_sink=_boom)
        verdict = bridge.consume()
        assert verdict.accepted is True
        assert len(bridge.audit_log) == 1  # 内存审计仍在

    def test_rejected_consumption_also_audited(self) -> None:
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("9.9"))
        bridge.consume()
        assert bridge.audit_log[0]["accepted"] is False
        assert bridge.audit_log[0]["version_action"] == "unsupported"


class TestProviderContract:
    """provider 注入契约。"""

    def test_provider_receives_as_of(self) -> None:
        seen: list[object] = []

        def _provider(as_of: object = None) -> FactorResultBatch:
            seen.append(as_of)
            return _batch("1.0")

        bridge = FactorResultBridge(provider=_provider)
        bridge.consume(as_of=_T0)
        assert seen == [_T0]

    def test_provider_failure_raises_bridge_error(self) -> None:
        def _boom(as_of: object = None) -> FactorResultBatch:
            raise ConnectionError("store down")

        bridge = FactorResultBridge(provider=_boom)
        with pytest.raises(FactorResultBridgeError, match="store down"):
            bridge.consume()

    def test_batch_is_frozen(self) -> None:
        with pytest.raises(AttributeError):
            _batch("1.0").is_degraded = True  # type: ignore[misc]

    def test_verdict_is_frozen(self) -> None:
        bridge = FactorResultBridge(provider=lambda as_of=None: _batch("1.0"))
        verdict = bridge.consume()
        assert isinstance(verdict, ConsumptionVerdict)
        with pytest.raises(AttributeError):
            verdict.accepted = False  # type: ignore[misc]
