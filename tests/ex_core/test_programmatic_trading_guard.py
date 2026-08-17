# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TESTS] tests/ex_core/test_programmatic_trading_guard.py
# [TTL] task_bound
"""ProgrammaticTradingGuard 测试（gap 18 程序化报备开关）。

覆盖矩阵：
  - 模式豁免：PAPER / SIMULATION 直接放行
  - 实盘未报备：启动/下单抛异常
  - 实盘已报备：放行
  - 报备信息漂移：阻断（默认严格）/ 仅告警（allow_drift_warning_only=True）
  - 未识别 broker：保守拒绝
  - enforce_on_start=False / enforce_on_submit=False 宽松模式
  - hash_risk_config 稳定性
  - 报备历史审计
  - 报备参数校验（空 registration_id / 空 strategy_id 等）
"""

from __future__ import annotations

import pytest

from zephyr.ex_core.programmatic_trading_guard import (
    CheckOutcome,
    ProgrammaticTradingGuard,
    ProgrammaticTradingGuardConfig,
    ProgrammaticTradingGuardError,
    RegistrationInfo,
    TradingMode,
    hash_risk_config,
)

# ──────────────────────────────────────────────────────────────────────────────
# 辅助：构造报备信息
# ──────────────────────────────────────────────────────────────────────────────


_VALID_RISK_HASH = hash_risk_config(
    max_single_order_pct=0.04,
    max_symbol_orders_per_day=10,
    max_total_orders_per_day=50,
    cancel_rate_limit=0.15,
)


def _make_registered_guard(
    mode: TradingMode = TradingMode.LIVE,
    live_broker_ids: set[str] | None = None,
    risk_config_provider=None,
    allow_drift_warning_only: bool = False,
    registration_id: str = "PTR-2026-0001",
    risk_hash: str = _VALID_RISK_HASH,
) -> ProgrammaticTradingGuard:
    guard = ProgrammaticTradingGuard(
        config=ProgrammaticTradingGuardConfig(
            mode=mode,
            live_broker_ids=live_broker_ids if live_broker_ids is not None else {"miniqmt"},
            allow_drift_warning_only=allow_drift_warning_only,
        ),
        risk_config_provider=risk_config_provider,
    )
    guard.record_registration(
        registration_id=registration_id,
        strategy_id="daban_v1",
        algorithm_types=("TWAP", "VWAP"),
        server_location="上海券商机房",
        risk_config_hash=risk_hash,
        max_total_orders_per_day=50,
        cancel_rate_limit=0.15,
    )
    return guard


def _matching_risk_provider():
    """返回与 _VALID_RISK_HASH 一致的风控配置查询函数。"""
    return lambda: {
        "max_single_order_pct": 0.04,
        "max_symbol_orders_per_day": 10,
        "max_total_orders_per_day": 50,
        "cancel_rate_limit": 0.15,
    }


def _drifted_risk_provider():
    """返回与 _VALID_RISK_HASH 不一致的风控配置（max_total_orders_per_day 改了）。"""
    return lambda: {
        "max_single_order_pct": 0.04,
        "max_symbol_orders_per_day": 10,
        "max_total_orders_per_day": 100,  # 改了：50→100
        "cancel_rate_limit": 0.15,
    }


# ──────────────────────────────────────────────────────────────────────────────
# hash_risk_config
# ──────────────────────────────────────────────────────────────────────────────


class TestHashRiskConfig:
    def test_stable_for_same_input(self):
        h1 = hash_risk_config(0.04, 10, 50, 0.15)
        h2 = hash_risk_config(0.04, 10, 50, 0.15)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_different_input_different_hash(self):
        h1 = hash_risk_config(0.04, 10, 50, 0.15)
        h2 = hash_risk_config(0.04, 10, 100, 0.15)  # orders 改了
        assert h1 != h2

    def test_extra_fields_included(self):
        h1 = hash_risk_config(0.04, 10, 50, 0.15)
        h2 = hash_risk_config(0.04, 10, 50, 0.15, extra={"max_position_pct": "0.30"})
        assert h1 != h2

    def test_extra_order_independent(self):
        """extra dict 顺序不影响 hash（按 key 排序）。"""
        h1 = hash_risk_config(
            0.04, 10, 50, 0.15,
            extra={"a": "1", "b": "2"},
        )
        h2 = hash_risk_config(
            0.04, 10, 50, 0.15,
            extra={"b": "2", "a": "1"},
        )
        assert h1 == h2

    def test_float_precision_normalized(self):
        """0.04 与 0.04000 应生成相同 hash。"""
        h1 = hash_risk_config(0.04, 10, 50, 0.15)
        h2 = hash_risk_config(0.04000, 10, 50, 0.15000)
        assert h1 == h2


# ──────────────────────────────────────────────────────────────────────────────
# 模式豁免
# ──────────────────────────────────────────────────────────────────────────────


class TestModeExemption:
    def test_paper_mode_allowed_without_registration(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(mode=TradingMode.PAPER),
        )
        result = guard.check_can_trade("miniqmt")
        assert result.outcome is CheckOutcome.ALLOWED
        assert result.mode is TradingMode.PAPER
        assert "豁免" in result.reason

    def test_simulation_mode_allowed_without_registration(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(mode=TradingMode.SIMULATION),
        )
        result = guard.check_can_trade("any_broker")
        assert result.outcome is CheckOutcome.ALLOWED

    def test_paper_assert_can_start_no_raise(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(mode=TradingMode.PAPER),
        )
        # 未报备也不抛
        guard.assert_can_start("miniqmt")

    def test_paper_assert_can_submit_no_raise(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(mode=TradingMode.PAPER),
        )
        guard.assert_can_submit("miniqmt")


# ──────────────────────────────────────────────────────────────────────────────
# 实盘未报备
# ──────────────────────────────────────────────────────────────────────────────


class TestLiveUnregistered:
    def test_live_unregistered_blocked(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE,
                live_broker_ids={"miniqmt"},
            ),
        )
        result = guard.check_can_trade("miniqmt")
        assert result.outcome is CheckOutcome.BLOCKED_UNREGISTERED
        assert result.is_blocked
        assert "未完成" in result.reason

    def test_live_unregistered_assert_can_start_raises(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE,
                live_broker_ids={"miniqmt"},
            ),
        )
        with pytest.raises(ProgrammaticTradingGuardError, match="启动校验"):
            guard.assert_can_start("miniqmt")

    def test_live_unregistered_assert_can_submit_raises(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE,
                live_broker_ids={"miniqmt"},
            ),
        )
        with pytest.raises(ProgrammaticTradingGuardError, match="下单校验"):
            guard.assert_can_submit("miniqmt")

    def test_live_broker_ids_none_treats_all_as_live(self):
        """live_broker_ids=None 时所有 broker 视为实盘。"""
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE,
                live_broker_ids=None,
            ),
        )
        # 未报备，任何 broker_id 都拒绝
        result = guard.check_can_trade("unknown_broker")
        assert result.outcome is CheckOutcome.BLOCKED_UNREGISTERED


# ──────────────────────────────────────────────────────────────────────────────
# 实盘已报备
# ──────────────────────────────────────────────────────────────────────────────


class TestLiveRegistered:
    def test_registered_allowed(self):
        guard = _make_registered_guard()
        result = guard.check_can_trade("miniqmt")
        assert result.outcome is CheckOutcome.ALLOWED
        assert result.registration_id == "PTR-2026-0001"
        assert result.is_allowed

    def test_registered_assert_can_start_passes(self):
        guard = _make_registered_guard()
        # 不抛即通过
        result = guard.assert_can_start("miniqmt")
        assert result.is_allowed

    def test_registered_assert_can_submit_passes(self):
        guard = _make_registered_guard()
        result = guard.assert_can_submit("miniqmt")
        assert result.is_allowed

    def test_registration_property_returns_info(self):
        guard = _make_registered_guard()
        info = guard.registration
        assert isinstance(info, RegistrationInfo)
        assert info.registration_id == "PTR-2026-0001"
        assert info.strategy_id == "daban_v1"
        assert info.algorithm_types == ("TWAP", "VWAP")
        assert info.max_total_orders_per_day == 50

    def test_is_live_broker_true_for_live_mode(self):
        guard = _make_registered_guard(live_broker_ids={"miniqmt"})
        assert guard.is_live_broker("miniqmt") is True
        assert guard.is_live_broker("other") is False

    def test_is_live_broker_false_for_simulation_mode(self):
        guard = _make_registered_guard(mode=TradingMode.SIMULATION)
        assert guard.is_live_broker("miniqmt") is False


# ──────────────────────────────────────────────────────────────────────────────
# 报备信息漂移
# ──────────────────────────────────────────────────────────────────────────────


class TestConfigDrift:
    def test_drift_blocked_by_default(self):
        guard = _make_registered_guard(
            risk_config_provider=_drifted_risk_provider(),
        )
        result = guard.check_can_trade("miniqmt")
        assert result.outcome is CheckOutcome.BLOCKED_CONFIG_DRIFT
        assert result.config_hash_drift is True
        assert "漂移" in result.reason

    def test_drift_assert_can_start_raises(self):
        guard = _make_registered_guard(
            risk_config_provider=_drifted_risk_provider(),
        )
        with pytest.raises(ProgrammaticTradingGuardError, match="漂移"):
            guard.assert_can_start("miniqmt")

    def test_drift_warning_only_allows(self):
        guard = _make_registered_guard(
            risk_config_provider=_drifted_risk_provider(),
            allow_drift_warning_only=True,
        )
        result = guard.check_can_trade("miniqmt")
        assert result.outcome is CheckOutcome.ALLOWED
        assert result.config_hash_drift is True  # 标记漂移但放行

    def test_no_drift_when_provider_returns_matching_hash(self):
        guard = _make_registered_guard(
            risk_config_provider=_matching_risk_provider(),
        )
        result = guard.check_can_trade("miniqmt")
        assert result.outcome is CheckOutcome.ALLOWED
        assert result.config_hash_drift is False

    def test_no_drift_when_provider_none(self):
        """未配置 risk_config_provider 时不做漂移检测。"""
        guard = _make_registered_guard(risk_config_provider=None)
        result = guard.check_can_trade("miniqmt")
        assert result.outcome is CheckOutcome.ALLOWED
        assert result.config_hash_drift is False

    def test_drift_provider_exception_does_not_block(self):
        """risk_config_provider 抛异常时保守放行（不阻断交易）。"""
        def bad_provider():
            raise RuntimeError("风控配置查询失败")

        guard = _make_registered_guard(risk_config_provider=bad_provider)
        result = guard.check_can_trade("miniqmt")
        assert result.outcome is CheckOutcome.ALLOWED
        assert result.config_hash_drift is False


# ──────────────────────────────────────────────────────────────────────────────
# 未识别 broker
# ──────────────────────────────────────────────────────────────────────────────


class TestUnrecognizedBroker:
    def test_unrecognized_broker_blocked_in_live_mode(self):
        guard = _make_registered_guard(live_broker_ids={"miniqmt"})
        result = guard.check_can_trade("unknown_broker")
        assert result.outcome is CheckOutcome.BLOCKED_LIVE_BROKER
        assert "不在已识别" in result.reason

    def test_unrecognized_broker_assert_can_start_raises(self):
        guard = _make_registered_guard(live_broker_ids={"miniqmt"})
        with pytest.raises(ProgrammaticTradingGuardError, match="未识别"):
            guard.assert_can_start("unknown_broker")

    def test_multiple_live_brokers_all_recognized(self):
        guard = _make_registered_guard(live_broker_ids={"miniqmt", "bigqmt"})
        assert guard.check_can_trade("miniqmt").is_allowed
        assert guard.check_can_trade("bigqmt").is_allowed


# ──────────────────────────────────────────────────────────────────────────────
# 宽松模式（enforce=False）
# ──────────────────────────────────────────────────────────────────────────────


class TestLooseEnforcement:
    def test_enforce_on_start_false_skips_block(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE,
                live_broker_ids={"miniqmt"},
                enforce_on_start=False,
            ),
        )
        # 未报备但不抛（宽松模式）
        result = guard.assert_can_start("miniqmt")
        assert result.is_blocked  # 返回结果仍标记 blocked，但不抛异常

    def test_enforce_on_submit_false_skips_block(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE,
                live_broker_ids={"miniqmt"},
                enforce_on_submit=False,
            ),
        )
        result = guard.assert_can_submit("miniqmt")
        assert result.is_blocked  # 标记 blocked 但不抛


# ──────────────────────────────────────────────────────────────────────────────
# 报备参数校验
# ──────────────────────────────────────────────────────────────────────────────


class TestRegistrationValidation:
    def test_empty_registration_id_raises(self):
        guard = ProgrammaticTradingGuard()
        with pytest.raises(ProgrammaticTradingGuardError, match="registration_id"):
            guard.record_registration(
                registration_id="",
                strategy_id="daban_v1",
                algorithm_types=("TWAP",),
                server_location="上海",
                risk_config_hash=_VALID_RISK_HASH,
                max_total_orders_per_day=50,
                cancel_rate_limit=0.15,
            )

    def test_empty_strategy_id_raises(self):
        guard = ProgrammaticTradingGuard()
        with pytest.raises(ProgrammaticTradingGuardError, match="strategy_id"):
            guard.record_registration(
                registration_id="PTR-001",
                strategy_id="",
                algorithm_types=("TWAP",),
                server_location="上海",
                risk_config_hash=_VALID_RISK_HASH,
                max_total_orders_per_day=50,
                cancel_rate_limit=0.15,
            )

    def test_empty_algorithm_types_raises(self):
        guard = ProgrammaticTradingGuard()
        with pytest.raises(ProgrammaticTradingGuardError, match="algorithm_types"):
            guard.record_registration(
                registration_id="PTR-001",
                strategy_id="daban_v1",
                algorithm_types=(),
                server_location="上海",
                risk_config_hash=_VALID_RISK_HASH,
                max_total_orders_per_day=50,
                cancel_rate_limit=0.15,
            )

    def test_zero_max_orders_raises(self):
        guard = ProgrammaticTradingGuard()
        with pytest.raises(ProgrammaticTradingGuardError, match="max_total_orders_per_day"):
            guard.record_registration(
                registration_id="PTR-001",
                strategy_id="daban_v1",
                algorithm_types=("TWAP",),
                server_location="上海",
                risk_config_hash=_VALID_RISK_HASH,
                max_total_orders_per_day=0,
                cancel_rate_limit=0.15,
            )

    def test_cancel_rate_out_of_range_raises(self):
        guard = ProgrammaticTradingGuard()
        with pytest.raises(ProgrammaticTradingGuardError, match="cancel_rate_limit"):
            guard.record_registration(
                registration_id="PTR-001",
                strategy_id="daban_v1",
                algorithm_types=("TWAP",),
                server_location="上海",
                risk_config_hash=_VALID_RISK_HASH,
                max_total_orders_per_day=50,
                cancel_rate_limit=0.0,  # 必须 > 0
            )

    def test_cancel_rate_above_one_raises(self):
        guard = ProgrammaticTradingGuard()
        with pytest.raises(ProgrammaticTradingGuardError, match="cancel_rate_limit"):
            guard.record_registration(
                registration_id="PTR-001",
                strategy_id="daban_v1",
                algorithm_types=("TWAP",),
                server_location="上海",
                risk_config_hash=_VALID_RISK_HASH,
                max_total_orders_per_day=50,
                cancel_rate_limit=1.5,  # 必须 ≤ 1
            )

    def test_list_algorithm_types_accepted(self):
        """list 形式的 algorithm_types 也应接受（自动转 tuple）。"""
        guard = ProgrammaticTradingGuard()
        info = guard.record_registration(
            registration_id="PTR-001",
            strategy_id="daban_v1",
            algorithm_types=["TWAP", "VWAP"],  # list
            server_location="上海",
            risk_config_hash=_VALID_RISK_HASH,
            max_total_orders_per_day=50,
            cancel_rate_limit=0.15,
        )
        assert info.algorithm_types == ("TWAP", "VWAP")
        assert isinstance(info.algorithm_types, tuple)


# ──────────────────────────────────────────────────────────────────────────────
# 报备历史与重新报备
# ──────────────────────────────────────────────────────────────────────────────


class TestRegistrationHistory:
    def test_re_registration_keeps_history(self):
        guard = _make_registered_guard(registration_id="PTR-001")
        # 重新报备
        guard.record_registration(
            registration_id="PTR-002",
            strategy_id="daban_v2",
            algorithm_types=("IS",),
            server_location="北京机房",
            risk_config_hash=_VALID_RISK_HASH,
            max_total_orders_per_day=80,
            cancel_rate_limit=0.12,
        )
        # 当前指向新报备
        assert guard.registration.registration_id == "PTR-002"
        # 旧的进历史
        history = guard.registration_history
        assert "PTR-001" in history
        assert history["PTR-001"].strategy_id == "daban_v1"

    def test_registration_history_empty_initially(self):
        guard = ProgrammaticTradingGuard()
        assert guard.registration_history == {}
        assert guard.registration is None

    def test_registration_info_is_frozen(self):
        """RegistrationInfo 是 frozen dataclass，不可修改。"""
        guard = _make_registered_guard()
        info = guard.registration
        with pytest.raises(Exception):  # FrozenInstanceError
            info.registration_id = "hacked"  # type: ignore[misc]

    def test_check_result_is_frozen(self):
        """CheckResult 是 frozen dataclass，不可修改。"""
        guard = _make_registered_guard()
        result = guard.check_can_trade("miniqmt")
        with pytest.raises(Exception):  # FrozenInstanceError
            result.outcome = CheckOutcome.BLOCKED_UNREGISTERED  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────────────────────
# CheckResult 属性
# ──────────────────────────────────────────────────────────────────────────────


class TestCheckResultProperties:
    def test_allowed_is_blocked_false(self):
        guard = _make_registered_guard()
        result = guard.check_can_trade("miniqmt")
        assert result.is_allowed is True
        assert result.is_blocked is False

    def test_blocked_is_allowed_false(self):
        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE,
                live_broker_ids={"miniqmt"},
            ),
        )
        result = guard.check_can_trade("miniqmt")
        assert result.is_allowed is False
        assert result.is_blocked is True

    def test_blocked_outcomes_distinct(self):
        """三种 BLOCKED outcome 互不相同。"""
        # UNREGISTERED
        guard1 = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE, live_broker_ids={"miniqmt"},
            ),
        )
        assert guard1.check_can_trade("miniqmt").outcome is CheckOutcome.BLOCKED_UNREGISTERED

        # LIVE_BROKER
        guard2 = _make_registered_guard(live_broker_ids={"miniqmt"})
        assert guard2.check_can_trade("unknown").outcome is CheckOutcome.BLOCKED_LIVE_BROKER

        # CONFIG_DRIFT
        guard3 = _make_registered_guard(risk_config_provider=_drifted_risk_provider())
        assert guard3.check_can_trade("miniqmt").outcome is CheckOutcome.BLOCKED_CONFIG_DRIFT
