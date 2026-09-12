# [BLUEPRINT] MOD-INF-072 | docs/03_modules/_domain_infrastructure_operations/strategy_canary_release/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-072 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.infrastructure.test_strategy_canary_release
# [TESTS] src/zephyr/infrastructure/strategy_canary_release.py
"""MOD-INF-072 单元测试：strategy_canary_release 策略灰度发布。

蓝图验收（B14-04678/CAND-INFRAOPS-002，A9 §8.3.6）：
三阶段阶梯推进 + 6 维验证 + 失败自动回滚（<10s 配置回滚语义）+
交易时段禁启动（HC-05）。全部内存状态机，不触网不触库不切真实流量。
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

pytest.importorskip(
    "zephyr.infrastructure.strategy_canary_release",
    reason="strategy_canary_release not importable",
)

from zephyr.infrastructure.strategy_canary_release import (  # noqa: E402
    DEFAULT_STAGES,
    CanaryStatus,
    StrategyCanaryConfig,
    StrategyCanaryError,
    StrategyCanaryRelease,
    ValidationDimension,
    config_from_dict,
)

_NOW = datetime(2026, 8, 25, 12, 0, 0, tzinfo=timezone.utc)

_ALL_DIMS = tuple(ValidationDimension)


def _config(**kw) -> StrategyCanaryConfig:
    return StrategyCanaryConfig(strategy_id="strat_alpha", **kw)


def _pass_metrics(config: StrategyCanaryConfig) -> dict:
    return {d: config.validation_thresholds[d] for d in _ALL_DIMS}


class TestStart:
    def test_start_enters_stage1_floor_ratio(self) -> None:
        rel = StrategyCanaryRelease()
        st = rel.start(_config(), now_utc=_NOW, is_trading_session=False)
        assert st.status == CanaryStatus.RUNNING
        assert st.stage_index == 0
        assert st.current_ratio == pytest.approx(DEFAULT_STAGES[0].min_ratio)  # 0.01

    def test_trading_session_start_blocked_hc05(self) -> None:
        rel = StrategyCanaryRelease()
        with pytest.raises(StrategyCanaryError, match="HC-05|交易时段"):
            rel.start(_config(), now_utc=_NOW, is_trading_session=True)

    def test_duplicate_start_rejected(self) -> None:
        rel = StrategyCanaryRelease()
        rel.start(_config(), now_utc=_NOW, is_trading_session=False)
        with pytest.raises(StrategyCanaryError):
            rel.start(_config(), now_utc=_NOW, is_trading_session=False)


class TestAdvance:
    def _running(self) -> tuple[StrategyCanaryRelease, StrategyCanaryConfig]:
        rel = StrategyCanaryRelease()
        cfg = _config()
        rel.start(cfg, now_utc=_NOW, is_trading_session=False)
        return rel, cfg

    def test_full_ladder_to_completed(self) -> None:
        rel, cfg = self._running()
        st = rel.advance("strat_alpha", _pass_metrics(cfg), now_utc=_NOW)
        assert st.stage_index == 1
        assert st.current_ratio == pytest.approx(DEFAULT_STAGES[1].min_ratio)  # 0.25
        st = rel.advance("strat_alpha", _pass_metrics(cfg), now_utc=_NOW)
        assert st.stage_index == 2
        assert st.current_ratio == pytest.approx(1.0)
        st = rel.advance("strat_alpha", _pass_metrics(cfg), now_utc=_NOW)
        assert st.status == CanaryStatus.COMPLETED
        assert st.current_ratio == pytest.approx(1.0)

    def test_failing_dimension_auto_rollback(self) -> None:
        rel, cfg = self._running()
        metrics = _pass_metrics(cfg)
        metrics[ValidationDimension.ERROR_RATE] = cfg.validation_thresholds[ValidationDimension.ERROR_RATE] + 1.0
        st = rel.advance("strat_alpha", metrics, now_utc=_NOW)
        assert st.status == CanaryStatus.ROLLED_BACK
        assert st.current_ratio == pytest.approx(0.0)
        assert any("ERROR_RATE" in h or "error_rate" in h for h in st.history)

    def test_missing_dimension_fail_closed(self) -> None:
        rel, cfg = self._running()
        metrics = _pass_metrics(cfg)
        del metrics[ValidationDimension.RESOURCE]
        with pytest.raises(StrategyCanaryError):
            rel.advance("strat_alpha", metrics, now_utc=_NOW)

    def test_advance_without_start_rejected(self) -> None:
        rel = StrategyCanaryRelease()
        with pytest.raises(StrategyCanaryError):
            rel.advance("strat_alpha", {}, now_utc=_NOW)

    def test_rolled_back_can_restart_off_session(self) -> None:
        rel, cfg = self._running()
        rel.rollback("strat_alpha", "手动回滚", now_utc=_NOW)
        st = rel.start(cfg, now_utc=_NOW, is_trading_session=False)
        assert st.status == CanaryStatus.RUNNING
        assert st.stage_index == 0
        with pytest.raises(StrategyCanaryError, match="HC-05|交易时段"):
            rel.start(cfg, now_utc=_NOW, is_trading_session=True)


class TestRollback:
    def test_manual_rollback_zeroes_ratio_and_traces(self) -> None:
        rel = StrategyCanaryRelease()
        cfg = _config()
        rel.start(cfg, now_utc=_NOW, is_trading_session=False)
        st = rel.rollback("strat_alpha", "错误率超标", now_utc=_NOW)
        assert st.status == CanaryStatus.ROLLED_BACK
        assert st.current_ratio == pytest.approx(0.0)
        assert any("错误率超标" in h for h in st.history)

    def test_rollback_timeout_config_semantics(self) -> None:
        cfg = _config()
        assert cfg.rollback_timeout_sec == 10  # <10s 配置回滚声明
        with pytest.raises(StrategyCanaryError):
            _config(rollback_timeout_sec=0)


class TestConfig:
    def test_default_thresholds_cover_six_dimensions(self) -> None:
        cfg = _config()
        assert set(cfg.validation_thresholds) == set(_ALL_DIMS)

    def test_from_dict(self) -> None:
        cfg = config_from_dict(
            "strat_beta",
            {
                "stages": [
                    {"name": "s1", "min_ratio": 0.02, "max_ratio": 0.05},
                    {"name": "s2", "min_ratio": 0.3, "max_ratio": 0.5},
                    {"name": "s3", "min_ratio": 1.0, "max_ratio": 1.0},
                ],
                "validation_thresholds": {d.value: 1.0 for d in _ALL_DIMS},
            },
        )
        assert cfg.strategy_id == "strat_beta"
        assert cfg.stages[0].min_ratio == pytest.approx(0.02)

    def test_invalid_stages_rejected(self) -> None:
        with pytest.raises(StrategyCanaryError):
            config_from_dict("s", {"stages": [{"name": "x", "min_ratio": 0.5, "max_ratio": 0.1}]})
        with pytest.raises(StrategyCanaryError):
            config_from_dict("s", {"stages": [{"name": "x", "min_ratio": 0.0, "max_ratio": 0.1}]})
        with pytest.raises(StrategyCanaryError):
            config_from_dict("s", {"stages": []})
