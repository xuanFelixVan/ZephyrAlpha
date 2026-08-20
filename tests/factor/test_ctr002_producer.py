# [A_test] module_id: MOD-GOV_ctr002_producer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_ctr002_producer
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_ctr002_producer.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""CTR-002 FactorSignal 生产者测试——to_signals。

覆盖：
- 空输入 / 单条 / 多条
- z-score 标准化 / rank_pct 排名
- NaN → is_valid=False
- confidence 计算
- idempotency_key 格式
- factor_version / prefix 传递
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

converter = pytest.importorskip("zephyr.factor.core.ctr002_producer.converter")
from zephyr.shared.contracts.factor_signal import FactorSignal  # noqa: E402

to_signals = converter.to_signals

_AS_OF = datetime(2026, 6, 15, tzinfo=timezone.utc)


class TestToSignalsEmpty:
    def test_none_input(self):
        assert to_signals(None, "f1", _AS_OF) == []

    def test_empty_series(self):
        assert to_signals(pd.Series([], dtype=float), "f1", _AS_OF) == []


class TestToSignalsBasic:
    def test_single_value(self):
        s = pd.Series([1.0], index=["A.SH"])
        signals = to_signals(s, "mom_20d", _AS_OF)
        assert len(signals) == 1
        assert signals[0].symbol == "A.SH"
        assert signals[0].factor_id == "mom_20d"
        assert signals[0].raw_value == 1.0
        assert signals[0].is_valid is True

    def test_multiple_values(self):
        s = pd.Series([1.0, 2.0, 3.0], index=["A.SH", "B.SH", "C.SH"])
        signals = to_signals(s, "f1", _AS_OF)
        assert len(signals) == 3
        syms = {sig.symbol for sig in signals}
        assert syms == {"A.SH", "B.SH", "C.SH"}

    def test_returns_factor_signal_type(self):
        s = pd.Series([1.0], index=["A.SH"])
        signals = to_signals(s, "f1", _AS_OF)
        assert isinstance(signals[0], FactorSignal)

    def test_as_of_date_propagated(self):
        s = pd.Series([1.0], index=["A.SH"])
        signals = to_signals(s, "f1", _AS_OF)
        assert signals[0].as_of_date == _AS_OF


class TestToSignalsNormalization:
    def test_zscore_mean_zero(self):
        s = pd.Series([1.0, 2.0, 3.0], index=["A", "B", "C"])
        signals = to_signals(s, "f1", _AS_OF)
        norms = [sig.normalized_value for sig in signals if sig.normalized_value is not None]
        assert abs(sum(norms)) < 1e-10

    def test_zscore_std_one(self):
        s = pd.Series([1.0, 2.0, 3.0], index=["A", "B", "C"])
        signals = to_signals(s, "f1", _AS_OF)
        norms = [sig.normalized_value for sig in signals if sig.normalized_value is not None]
        assert abs(np.std(norms, ddof=0) - 1.0) < 1e-10

    def test_rank_pct_in_range(self):
        s = pd.Series([10.0, 20.0, 30.0], index=["A", "B", "C"])
        signals = to_signals(s, "f1", _AS_OF)
        for sig in signals:
            assert sig.rank_pct is not None
            assert 0.0 < sig.rank_pct <= 1.0

    def test_rank_pct_highest_for_max(self):
        s = pd.Series([1.0, 5.0, 3.0], index=["A", "B", "C"])
        signals = to_signals(s, "f1", _AS_OF)
        by_sym = {sig.symbol: sig.rank_pct for sig in signals}
        # B(5.0) 应该有最高排名
        assert by_sym["B"] > by_sym["A"]
        assert by_sym["B"] > by_sym["C"]


class TestToSignalsNan:
    def test_nan_invalid(self):
        s = pd.Series([1.0, float("nan"), 3.0], index=["A", "B", "C"])
        signals = to_signals(s, "f1", _AS_OF)
        by_sym = {sig.symbol: sig.is_valid for sig in signals}
        assert by_sym["A"] is True
        assert by_sym["B"] is False
        assert by_sym["C"] is True

    def test_nan_raw_value_zero(self):
        s = pd.Series([1.0, float("nan")], index=["A", "B"])
        signals = to_signals(s, "f1", _AS_OF)
        by_sym = {sig.symbol: sig for sig in signals}
        assert by_sym["B"].raw_value == 0.0

    def test_confidence_ratio(self):
        s = pd.Series([1.0, float("nan"), 3.0], index=["A", "B", "C"])
        signals = to_signals(s, "f1", _AS_OF)
        # 2/3 有效
        assert abs(signals[0].confidence - 2.0 / 3.0) < 1e-10

    def test_all_valid_confidence_one(self):
        s = pd.Series([1.0, 2.0, 3.0], index=["A", "B", "C"])
        signals = to_signals(s, "f1", _AS_OF)
        assert abs(signals[0].confidence - 1.0) < 1e-10


class TestToSignalsIdempotency:
    def test_key_format(self):
        s = pd.Series([1.0], index=["A.SH"])
        signals = to_signals(s, "mom_20d", _AS_OF)
        expected = "mom_20d:A.SH:20260615"
        assert signals[0].idempotency_key == expected

    def test_key_with_prefix(self):
        s = pd.Series([1.0], index=["A.SH"])
        signals = to_signals(s, "mom_20d", _AS_OF, idempotency_key_prefix="batch1:")
        assert signals[0].idempotency_key.startswith("batch1:")

    def test_key_unique_per_symbol(self):
        s = pd.Series([1.0, 2.0], index=["A.SH", "B.SH"])
        signals = to_signals(s, "f1", _AS_OF)
        keys = {sig.idempotency_key for sig in signals}
        assert len(keys) == 2


class TestToSignalsVersion:
    def test_default_version(self):
        s = pd.Series([1.0], index=["A.SH"])
        signals = to_signals(s, "f1", _AS_OF)
        assert signals[0].factor_version == "1.0"

    def test_custom_version(self):
        s = pd.Series([1.0], index=["A.SH"])
        signals = to_signals(s, "f1", _AS_OF, factor_version="2.1.0")
        assert signals[0].factor_version == "2.1.0"
