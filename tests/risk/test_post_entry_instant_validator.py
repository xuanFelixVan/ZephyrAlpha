# [BLUEPRINT] MOD-RK-40 | docs/03_modules/_domain_risk/post_entry_instant_validator/blueprint.md | §test
# [MODULE] tests.risk.test_post_entry_instant_validator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.post_entry_instant_validator
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_post_entry_instant_validator.py
# [A_test] module_id: MOD-RK-40 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-40 单元测试: PostEntryInstantValidator — 买入后即时验证与快速纠错。

覆盖: T+5/15/30min 三档规则命中/边界（1% 严格大于、量比阈值、vwap 严格小于、
0.5ATR 反弹无力、2ATR 严格大于）、档位必填缺失拒绝、配置非法拒绝、audit_sink
仅非 PASS 触发、verdict frozen。
"""

from __future__ import annotations

import pytest

from zephyr.risk.post_entry_instant_validator import (
    CorrectionAction,
    InvalidPostEntryInputError,
    PostEntryCheckpoint,
    PostEntryInstantValidator,
    PostEntryValidatorConfig,
    PostEntryVerdict,
)


@pytest.fixture
def validator() -> PostEntryInstantValidator:
    return PostEntryInstantValidator()


class TestCheckpoint5Min:
    def test_watch_on_drawdown_with_volume(self, validator):
        v = validator.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_5,
            current_price=9.89,  # 跌 1.1% > 1%
            volume_ratio=2.0,  # ≥1.5 放量
        )
        assert v.action is CorrectionAction.WATCH
        assert v.checkpoint is PostEntryCheckpoint.MIN_5

    def test_pass_when_no_volume_confirmation(self, validator):
        v = validator.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_5,
            current_price=9.89,
            volume_ratio=1.2,  # 未放量
        )
        assert v.action is CorrectionAction.PASS

    def test_pass_when_drawdown_not_beyond_1pct(self, validator):
        v = validator.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_5,
            current_price=9.90,  # 恰好 1%，严格大于不命中
            volume_ratio=3.0,
        )
        assert v.action is CorrectionAction.PASS

    def test_missing_volume_ratio_rejected(self, validator):
        with pytest.raises(InvalidPostEntryInputError):
            validator.validate("S1", entry_price=10.0, checkpoint=PostEntryCheckpoint.MIN_5, current_price=9.8)


class TestCheckpoint15Min:
    def test_reduce_half_on_below_vwap_weak_rebound(self, validator):
        v = validator.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_15,
            current_price=9.80,
            vwap=9.90,  # current < vwap
            session_low=9.70,  # 反弹 0.10 < 0.5×ATR=0.15 → 无力
            atr14=0.30,
        )
        assert v.action is CorrectionAction.REDUCE_HALF

    def test_pass_when_rebound_strong(self, validator):
        v = validator.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_15,
            current_price=9.85,
            vwap=9.90,
            session_low=9.60,  # 反弹 0.25 ≥ 0.15 → 有力
            atr14=0.30,
        )
        assert v.action is CorrectionAction.PASS

    def test_pass_when_above_vwap(self, validator):
        v = validator.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_15,
            current_price=9.95,
            vwap=9.90,
            session_low=9.60,
            atr14=0.30,
        )
        assert v.action is CorrectionAction.PASS

    def test_missing_vwap_rejected(self, validator):
        with pytest.raises(InvalidPostEntryInputError):
            validator.validate(
                "S1",
                entry_price=10.0,
                checkpoint=PostEntryCheckpoint.MIN_15,
                current_price=9.8,
                session_low=9.7,
                atr14=0.3,
            )


class TestCheckpoint30Min:
    def test_exit_all_on_adverse_beyond_2atr(self, validator):
        v = validator.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_30,
            current_price=9.35,  # 反向 0.65 > 2×0.30
            atr14=0.30,
        )
        assert v.action is CorrectionAction.EXIT_ALL

    def test_pass_at_exactly_2atr(self, validator):
        v = validator.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_30,
            current_price=9.40,  # 恰好 2ATR，严格大于不命中
            atr14=0.30,
        )
        assert v.action is CorrectionAction.PASS

    def test_missing_atr_rejected(self, validator):
        with pytest.raises(InvalidPostEntryInputError):
            validator.validate("S1", entry_price=10.0, checkpoint=PostEntryCheckpoint.MIN_30, current_price=9.0)


class TestAuditAndImmutability:
    def test_audit_sink_only_on_non_pass(self):
        seen: list[PostEntryVerdict] = []
        v = PostEntryInstantValidator(audit_sink=seen.append)
        v.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_5,
            current_price=10.05,  # PASS
            volume_ratio=2.0,
        )
        assert seen == []
        v.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_30,
            current_price=9.0,  # EXIT_ALL
            atr14=0.3,
        )
        assert len(seen) == 1
        assert seen[0].action is CorrectionAction.EXIT_ALL

    def test_verdict_frozen_and_reason_recorded(self, validator):
        v = validator.validate(
            "S1",
            entry_price=10.0,
            checkpoint=PostEntryCheckpoint.MIN_30,
            current_price=9.0,
            atr14=0.3,
        )
        assert isinstance(v, PostEntryVerdict)
        assert "2" in v.reason and "ATR" in v.reason
        with pytest.raises(AttributeError):
            v.action = CorrectionAction.PASS  # type: ignore[misc]


class TestFailClosed:
    def test_bad_entry_price_rejected(self, validator):
        with pytest.raises(InvalidPostEntryInputError):
            validator.validate(
                "S1",
                entry_price=0.0,
                checkpoint=PostEntryCheckpoint.MIN_5,
                current_price=9.9,
                volume_ratio=1.0,
            )

    def test_bad_current_price_rejected(self, validator):
        with pytest.raises(InvalidPostEntryInputError):
            validator.validate(
                "S1",
                entry_price=10.0,
                checkpoint=PostEntryCheckpoint.MIN_5,
                current_price=float("nan"),
                volume_ratio=1.0,
            )

    def test_empty_symbol_rejected(self, validator):
        with pytest.raises(InvalidPostEntryInputError):
            validator.validate(
                "",
                entry_price=10.0,
                checkpoint=PostEntryCheckpoint.MIN_5,
                current_price=9.9,
                volume_ratio=1.0,
            )

    def test_bad_checkpoint_type_rejected(self, validator):
        with pytest.raises(InvalidPostEntryInputError):
            validator.validate(
                "S1",
                entry_price=10.0,
                checkpoint="5min",  # type: ignore[arg-type]
                current_price=9.9,
                volume_ratio=1.0,
            )

    def test_bad_config_rejected(self):
        with pytest.raises(InvalidPostEntryInputError):
            PostEntryValidatorConfig(drawdown_pct_5m=0.0)
        with pytest.raises(InvalidPostEntryInputError):
            PostEntryValidatorConfig(volume_ratio_min=-1.0)
        with pytest.raises(InvalidPostEntryInputError):
            PostEntryValidatorConfig(adverse_atr_mult=0.0)
