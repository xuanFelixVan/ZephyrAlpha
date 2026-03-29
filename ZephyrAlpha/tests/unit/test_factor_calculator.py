"""
因子计算器单元测试
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.modules.factor_calculator import FactorCalculator, FactorResult, PLACEHOLDER_FACTORS


def create_sample_ohlcv_data(n_days: int = 100, base_price: float = 100.0) -> pd.DataFrame:
    """创建示例OHLCV数据"""
    np.random.seed(42)

    dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')

    close_prices = base_price * (1 + np.random.randn(n_days).cumsum() * 0.02)

    data = pd.DataFrame({
        'open': close_prices * (1 + np.random.randn(n_days) * 0.005),
        'high': close_prices * (1 + np.abs(np.random.randn(n_days) * 0.01)),
        'low': close_prices * (1 - np.abs(np.random.randn(n_days) * 0.01)),
        'close': close_prices,
        'volume': np.random.randint(1000000, 10000000, n_days)
    }, index=dates)

    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)

    return data


class TestFactorCalculatorInit:
    """测试 FactorCalculator 初始化"""

    def test_default_init(self):
        """测试默认初始化"""
        calculator = FactorCalculator()
        assert calculator.max_workers == 4
        assert calculator.calculated_factors == {}

    def test_custom_max_workers(self):
        """测试自定义并行数"""
        calculator = FactorCalculator(max_workers=8)
        assert calculator.max_workers == 8


class TestDataValidation:
    """测试数据验证"""

    def test_valid_data(self):
        """测试有效数据"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        calculator._validate_data(data)

    def test_empty_data(self):
        """测试空数据"""
        from src.core.exceptions import ValidationException

        calculator = FactorCalculator()

        with pytest.raises(ValidationException) as exc_info:
            calculator._validate_data(pd.DataFrame())

        assert "数据不能为空" in str(exc_info.value)

    def test_missing_columns(self):
        """测试缺少必需列"""
        from src.core.exceptions import ValidationException

        calculator = FactorCalculator()
        data = pd.DataFrame({'close': [100, 101, 102]})

        with pytest.raises(ValidationException) as exc_info:
            calculator._validate_data(data)

        assert "数据缺少必需列" in str(exc_info.value)

    def test_insufficient_rows(self):
        """测试数据行数不足"""
        from src.core.exceptions import ValidationException

        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(1)

        with pytest.raises(ValidationException) as exc_info:
            calculator._validate_data(data)

        assert "数据行数不足" in str(exc_info.value)


class TestCalculateAlphaFactor:
    """测试计算Alpha因子"""

    def test_trend_factors(self):
        """测试趋势类因子"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        for factor_id in ["ALPHA_001", "ALPHA_002", "ALPHA_003"]:
            result = calculator.calculate(factor_id, data)
            assert isinstance(result, FactorResult)
            assert result.factor_id == factor_id
            assert len(result.values) == len(data)

    def test_mean_reversion_factors(self):
        """测试均值回归类因子"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        result = calculator.calculate("ALPHA_015", data)
        assert isinstance(result, FactorResult)
        assert result.factor_name == "rsi_distance_from_50"

    def test_rsi_factor(self):
        """测试RSI因子"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        result = calculator.calculate("ALPHA_076", data)
        assert isinstance(result, FactorResult)
        assert result.factor_name == "rsi_6"

    def test_bollinger_bands(self):
        """测试布林带因子"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        result = calculator.calculate("ALPHA_016", data)
        assert isinstance(result, FactorResult)
        assert result.factor_name == "bb_position"

    def test_supertrend(self):
        """测试超级趋势因子"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        result = calculator.calculate("ALPHA_013", data)
        assert isinstance(result, FactorResult)
        assert result.factor_name == "supertrend"
        assert len(result.values) == len(data)

    def test_ichimoku(self):
        """测试一目云因子"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(100)

        result = calculator.calculate("ALPHA_014", data)
        assert isinstance(result, FactorResult)
        assert result.factor_name == "ichimoku_cloud_a"

    def test_macd(self):
        """测试MACD因子"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        result = calculator.calculate("ALPHA_079", data)
        assert isinstance(result, FactorResult)
        assert result.factor_name == "macd_signal_cross"


class TestPlaceholderFactors:
    """测试Placeholder因子"""

    def test_placeholder_factors_exist(self):
        """测试placeholder因子集合非空"""
        assert len(PLACEHOLDER_FACTORS) > 0

    def test_placeholder_warning(self):
        """测试placeholder因子产生警告"""
        import logging
        from src.core.exceptions import ValidationException

        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        with pytest.warns(UserWarning, match="placeholder"):
            result = calculator.calculate("ALPHA_030", data)
            assert result.factor_name == "placeholder"
            assert result.values.iloc[-1] == 0


class TestBatchCalculation:
    """测试批量计算"""

    def test_batch_sequential(self):
        """测试顺序批量计算"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        factor_ids = ["ALPHA_001", "ALPHA_002", "ALPHA_015"]
        results = calculator.calculate_batch(factor_ids, data, parallel=False)

        assert len(results) == 3
        assert all(fid in results for fid in factor_ids)

    def test_batch_parallel(self):
        """测试并行批量计算"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        factor_ids = ["ALPHA_001", "ALPHA_002", "ALPHA_015", "ALPHA_076"]
        results = calculator.calculate_batch(factor_ids, data, parallel=True)

        assert len(results) == 4
        assert all(fid in results for fid in factor_ids)

    def test_batch_with_invalid_factor(self):
        """测试批量计算包含无效因子"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        factor_ids = ["ALPHA_001", "INVALID_FACTOR"]
        results = calculator.calculate_batch(factor_ids, data, parallel=False)

        assert len(results) == 1
        assert "ALPHA_001" in results


class TestGetMethods:
    """测试获取方法"""

    def test_get_implemented_factors(self):
        """测试获取已实现因子"""
        calculator = FactorCalculator()

        implemented = calculator.get_implemented_factors()

        assert isinstance(implemented, list)
        assert len(implemented) > 0
        assert len(implemented) < 87

        for fid in implemented:
            assert fid not in PLACEHOLDER_FACTORS

    def test_get_placeholder_factors(self):
        """测试获取placeholder因子"""
        calculator = FactorCalculator()

        placeholders = calculator.get_placeholder_factors()

        assert isinstance(placeholders, list)
        assert len(placeholders) == len(PLACEHOLDER_FACTORS)

        for fid in placeholders:
            assert fid in PLACEHOLDER_FACTORS

    def test_get_factor_after_calculation(self):
        """测试计算后获取因子"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        calculator.calculate("ALPHA_001", data)
        result = calculator.get_factor("ALPHA_001")

        assert result is not None
        assert result.factor_id == "ALPHA_001"

    def test_get_factor_not_found(self):
        """测试获取不存在的因子"""
        calculator = FactorCalculator()

        result = calculator.get_factor("NONEXISTENT")

        assert result is None


class TestClearCache:
    """测试缓存清除"""

    def test_clear_cache(self):
        """测试清除缓存"""
        calculator = FactorCalculator()
        data = create_sample_ohlcv_data(50)

        calculator.calculate("ALPHA_001", data)
        assert len(calculator.calculated_factors) == 1

        calculator.clear_cache()
        assert len(calculator.calculated_factors) == 0


class TestEdgeCases:
    """测试边界情况"""

    def test_constant_price_data(self):
        """测试价格不变的数据"""
        calculator = FactorCalculator()

        data = pd.DataFrame({
            'open': [100.0] * 50,
            'high': [100.0] * 50,
            'low': [100.0] * 50,
            'close': [100.0] * 50,
            'volume': [1000000] * 50
        })

        result = calculator.calculate("ALPHA_001", data)
        assert not result.values.isna().all()

    def test_mixed_nan_data(self):
        """测试混合NaN数据"""
        calculator = FactorCalculator()

        data = create_sample_ohlcv_data(50)
        data.loc[data.index[10:20], 'volume'] = np.nan

        result = calculator.calculate("ALPHA_001", data)
        assert isinstance(result, FactorResult)
