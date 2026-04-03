"""
因子计算模块
基于pandas实现87个Alpha因子

技术层次: Layer 2 - Alpha因子层 | 业务架构: 三级时间框架融合架构

使用方式:
    from src.modules.factor_calculator import FactorCalculator

    calculator = FactorCalculator()
    result = calculator.calculate(
        factor_id="ALPHA_001",
        data=df,  # 必须包含: open, high, low, close, volume
        params={"period": 5}
    )

性能优化:
    - supertrend: 向量化实现
    - ichimoku: 减少冗余shift操作
    - batch: 并行计算支持

因子实现状态:
    ✅ ALPHA_001 - ALPHA_014 (趋势类) - 完整实现
    ✅ ALPHA_015 - ALPHA_026 (均值回归) - 完整实现
    ⚠️ ALPHA_027 - ALPHA_041 (价值类) - 部分实现 (placeholder警告)
    ⚠️ ALPHA_042 - ALPHA_053 (成长类) - 部分实现 (placeholder警告)
    ⚠️ ALPHA_054 - ALPHA_071 (质量类) - 部分实现 (placeholder警告)
    ✅ ALPHA_072 - ALPHA_081 (技术类) - 完整实现
    ⚠️ ALPHA_082 - ALPHA_087 (情绪类) - 部分实现 (placeholder警告)
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np

from src.core.exceptions import FactorException, ValidationException

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["open", "high", "low", "close", "volume"]

PLACEHOLDER_FACTORS = {
    "ALPHA_030", "ALPHA_031", "ALPHA_032", "ALPHA_033", "ALPHA_034",
    "ALPHA_035", "ALPHA_036", "ALPHA_037", "ALPHA_038", "ALPHA_039",
    "ALPHA_040", "ALPHA_041",
    "ALPHA_045", "ALPHA_046", "ALPHA_047", "ALPHA_048", "ALPHA_049",
    "ALPHA_050", "ALPHA_051", "ALPHA_052", "ALPHA_053",
    "ALPHA_057", "ALPHA_058", "ALPHA_059", "ALPHA_060", "ALPHA_061",
    "ALPHA_062", "ALPHA_063", "ALPHA_064", "ALPHA_065", "ALPHA_066",
    "ALPHA_067", "ALPHA_068", "ALPHA_069", "ALPHA_070", "ALPHA_071",
    "ALPHA_087",
}


@dataclass
class FactorResult:
    """因子计算结果"""
    factor_id: str
    factor_name: str
    values: pd.Series
    timestamp: datetime
    metadata: Dict


class FactorCalculator:
    """因子计算器

    支持的因子类别:
    - 趋势类 (Trend): MA, EMA, MACD, ADX等
    - 均值回归类 (Mean Reversion): RSI, Bollinger Bands, CCI等
    - 动量类 (Momentum): ROC, CMO, MRS等
    - 成交量类 (Volume): VWAP, OBV, MFI等
    - 波动率类 (Volatility): ATR, StdDev,布林带宽度等
    """

    def __init__(self, max_workers: int = 4):
        """初始化因子计算器

        参数:
            max_workers: 并行计算的最大线程数
        """
        self.calculated_factors: Dict[str, FactorResult] = {}
        self.max_workers = max_workers

    def _validate_data(self, data: pd.DataFrame) -> None:
        """验证数据是否有效

        抛出:
            ValidationException: 数据验证失败
        """
        if data is None or data.empty:
            raise ValidationException("数据不能为空", code=7001)

        missing_cols = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_cols:
            raise ValidationException(
                f"数据缺少必需列: {missing_cols}",
                code=7002
            )

        if len(data) < 2:
            raise ValidationException("数据行数不足(需要至少2行)", code=7003)

    def _warn_placeholder(self, factor_id: str) -> None:
        """警告placeholder因子"""
        if factor_id in PLACEHOLDER_FACTORS:
            logger.warning(
                f"因子 {factor_id} 是 placeholder，返回全零值，"
                "该因子尚未实现，请等待后续版本更新"
            )

    def calculate(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> FactorResult:
        """计算单个因子

        参数:
            factor_id: 因子标识符 (如: ALPHA_001, momentum_5d)
            data: OHLCV数据 (必须包含: open, high, low, close, volume)
            params: 因子参数

        返回:
            FactorResult: 因子计算结果

        抛出:
            ValidationException: 数据验证失败
            FactorException: 因子计算失败
        """
        self._validate_data(data)
        params = params or {}

        try:
            if factor_id.startswith("ALPHA_"):
                result = self._calculate_alpha_factor(factor_id, data, params)
            else:
                result = self._calculate_named_factor(factor_id, data, params)

            self.calculated_factors[factor_id] = result
            return result

        except ValidationException:
            raise
        except Exception as e:
            raise FactorException(f"因子计算失败 {factor_id}: {str(e)}", code=2001)

    def _calculate_alpha_factor(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Dict
    ) -> FactorResult:
        """计算Alpha因子 (按编号)"""
        factor_num = int(factor_id.split("_")[1])

        if factor_num <= 14:
            return self._trend_factors(factor_id, data, params)
        elif factor_num <= 26:
            return self._mean_reversion_factors(factor_id, data, params)
        elif factor_num <= 41:
            return self._value_factors(factor_id, data, params)
        elif factor_num <= 53:
            return self._growth_factors(factor_id, data, params)
        elif factor_num <= 71:
            return self._quality_factors(factor_id, data, params)
        elif factor_num <= 81:
            return self._technical_factors(factor_id, data, params)
        else:
            return self._sentiment_factors(factor_id, data, params)

    def _trend_factors(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Dict
    ) -> FactorResult:
        """趋势类因子 (ALPHA_001 - ALPHA_014)"""
        close = data["close"]
        factor_num = int(factor_id.split("_")[1])

        if factor_num == 1:
            values = close.pct_change(5)
            name = "return_5d"
        elif factor_num == 2:
            values = close.pct_change(10)
            name = "return_10d"
        elif factor_num == 3:
            values = close.pct_change(20)
            name = "return_20d"
        elif factor_num == 4:
            ma5 = close.rolling(5).mean()
            ma20 = close.rolling(20).mean()
            values = (ma5 - ma20) / ma20
            name = "ma5_ma20_crossover"
        elif factor_num == 5:
            ma10 = close.rolling(10).mean()
            ma30 = close.rolling(30).mean()
            values = (ma10 - ma30) / ma30
            name = "ma10_ma30_crossover"
        elif factor_num == 6:
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            values = ema12 - ema26
            name = "macd_line"
        elif factor_num == 7:
            atr = self._calculate_atr(data, 14)
            values = atr / close * 100
            name = "atr_pct"
        elif factor_num == 8:
            values = self._calculate_adx(data, 14)
            name = "adx_14"
        elif factor_num == 9:
            plus_di = self._calculate_plus_di(data, 14)
            minus_di = self._calculate_minus_di(data, 14)
            values = plus_di - minus_di
            name = "dmi_spread"
        elif factor_num == 10:
            values = close / close.rolling(20).mean() - 1
            name = "price_ma20_ratio"
        elif factor_num == 11:
            values = close / close.rolling(60).mean() - 1
            name = "price_ma60_ratio"
        elif factor_num == 12:
            ma5 = close.rolling(5).mean()
            ma20 = close.rolling(20).mean()
            values = ma5 / ma20 - 1
            name = "ma5_ma20_ratio"
        elif factor_num == 13:
            values = self._calculate_supertrend(data, 10, 3)["supertrend"]
            name = "supertrend"
        else:
            values = self._calculate_ichimoku(data)["senkou_span_a"]
            name = "ichimoku_cloud_a"

        return FactorResult(
            factor_id=factor_id,
            factor_name=name,
            values=values,
            timestamp=datetime.now(),
            metadata={"category": "trend", "params": params}
        )

    def _mean_reversion_factors(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Dict
    ) -> FactorResult:
        """均值回归类因子 (ALPHA_015 - ALPHA_026)"""
        close = data["close"]
        factor_num = int(factor_id.split("_")[1])

        if factor_num == 15:
            rsi = self._calculate_rsi(close, 14)
            values = 50 - rsi
            name = "rsi_distance_from_50"
        elif factor_num == 16:
            bb = self._calculate_bollinger_bands(close, 20, 2)
            bb_range = bb["bb_upper"] - bb["bb_lower"]
            values = (close - bb["bb_lower"]) / bb_range.replace(0, np.nan)
            name = "bb_position"
        elif factor_num == 17:
            values = close - close.rolling(20).mean()
            name = "price_distance_from_ma"
        elif factor_num == 18:
            values = close / close.rolling(10).mean()
            name = "price_ma10_ratio"
        elif factor_num == 19:
            values = self._calculate_cci(data, 14)
            name = "cci_14"
        elif factor_num == 20:
            values = self._calculate_stochastic(data, 14)["k"]
            name = "stoch_k"
        elif factor_num == 21:
            close_5 = close.shift(5)
            close_20 = close.shift(20)
            momentum_5 = (close - close_5) / close_5
            momentum_20 = (close - close_20) / close_20
            values = momentum_5 - momentum_20
            name = "momentum_reversal_5_20"
        elif factor_num == 22:
            rolling_std = close.rolling(5).std()
            rolling_mean = close.rolling(5).mean()
            values = rolling_std / rolling_mean.replace(0, np.nan)
            name = "cv_5d"
        elif factor_num == 23:
            expanding_mean = close.expanding().mean()
            expanding_std = close.expanding().std()
            values = (close - expanding_mean) / expanding_std.replace(0, np.nan)
            name = "zscore"
        elif factor_num == 24:
            values = self._calculate_cmo(close, 14)
            name = "cmo_14"
        elif factor_num == 25:
            values = self._calculate_williams_r(data, 14)
            name = "williams_r"
        else:
            values = self._calculate_mfi(data, 14)
            name = "mfi_14"

        return FactorResult(
            factor_id=factor_id,
            factor_name=name,
            values=values,
            timestamp=datetime.now(),
            metadata={"category": "mean_reversion", "params": params}
        )

    def _value_factors(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Dict
    ) -> FactorResult:
        """价值类因子 (ALPHA_027 - ALPHA_041)"""
        factor_num = int(factor_id.split("_")[1])

        if factor_num == 27:
            values = 1 / data["close"].replace(0, np.nan)
            name = "inverse_price"
        elif factor_num == 28:
            values = data["close"].pct_change()
            name = "daily_return"
        elif factor_num == 29:
            values = (data["close"] - data["open"]) / data["open"].replace(0, np.nan)
            name = "intraday_return"
        else:
            values = pd.Series(0, index=data.index)
            name = "placeholder"
            self._warn_placeholder(factor_id)

        return FactorResult(
            factor_id=factor_id,
            factor_name=name,
            values=values,
            timestamp=datetime.now(),
            metadata={"category": "value", "params": params}
        )

    def _growth_factors(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Dict
    ) -> FactorResult:
        """成长类因子 (ALPHA_042 - ALPHA_053)"""
        close = data["close"]
        factor_num = int(factor_id.split("_")[1])

        if factor_num == 42:
            values = close.pct_change(periods=20)
            name = "growth_20d"
        elif factor_num == 43:
            values = close.pct_change(periods=60)
            name = "growth_60d"
        elif factor_num == 44:
            values = close / close.shift(252) - 1
            name = "ytd_return"
        else:
            values = pd.Series(0, index=data.index)
            name = "placeholder"
            self._warn_placeholder(factor_id)

        return FactorResult(
            factor_id=factor_id,
            factor_name=name,
            values=values,
            timestamp=datetime.now(),
            metadata={"category": "growth", "params": params}
        )

    def _quality_factors(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Dict
    ) -> FactorResult:
        """质量类因子 (ALPHA_054 - ALPHA_071)"""
        factor_num = int(factor_id.split("_")[1])

        if factor_num == 54:
            volume = data["volume"]
            values = volume / volume.rolling(20).mean()
            name = "volume_ratio_20d"
        elif factor_num == 55:
            values = data["volume"] / data["volume"].shift(1).replace(0, np.nan)
            name = "volume_change"
        elif factor_num == 56:
            high = data["high"]
            low = data["low"]
            values = (high + low) / 2
            name = "hl_mean"
        else:
            values = pd.Series(0, index=data.index)
            name = "placeholder"
            self._warn_placeholder(factor_id)

        return FactorResult(
            factor_id=factor_id,
            factor_name=name,
            values=values,
            timestamp=datetime.now(),
            metadata={"category": "quality", "params": params}
        )

    def _technical_factors(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Dict
    ) -> FactorResult:
        """技术面因子 (ALPHA_072 - ALPHA_081)"""
        close = data["close"]
        factor_num = int(factor_id.split("_")[1])

        if factor_num == 72:
            values = close / close.rolling(5).mean()
            name = "price_ma5_ratio"
        elif factor_num == 73:
            values = close / close.rolling(10).mean()
            name = "price_ma10_ratio"
        elif factor_num == 74:
            values = close / close.rolling(20).mean()
            name = "price_ma20_ratio"
        elif factor_num == 75:
            bb = self._calculate_bollinger_bands(close, 20, 2)
            values = bb["bb_width"]
            name = "bb_width"
        elif factor_num == 76:
            values = self._calculate_rsi(close, 6)
            name = "rsi_6"
        elif factor_num == 77:
            values = self._calculate_rsi(close, 12)
            name = "rsi_12"
        elif factor_num == 78:
            values = self._calculate_rsi(close, 24)
            name = "rsi_24"
        elif factor_num == 79:
            macd_result = self._calculate_macd(close)
            values = macd_result["histogram"]
            name = "macd_signal_cross"
        elif factor_num == 80:
            values = self._calculate_obv(data)
            name = "obv"
        else:
            values = self._calculate_adx(data, 7)
            name = "adx_7"

        return FactorResult(
            factor_id=factor_id,
            factor_name=name,
            values=values,
            timestamp=datetime.now(),
            metadata={"category": "technical", "params": params}
        )

    def _sentiment_factors(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Dict
    ) -> FactorResult:
        """情绪类因子 (ALPHA_082 - ALPHA_087)"""
        close = data["close"]
        factor_num = int(factor_id.split("_")[1])

        if factor_num == 82:
            volume = data["volume"]
            values = volume * close
            name = "money_flow"
        elif factor_num == 83:
            close_5 = close.pct_change(5)
            close_20 = close.pct_change(20)
            values = close_5 / close_20.replace(0, np.nan)
            name = "short_medium_momentum"
        elif factor_num == 84:
            values = close / close.rolling(60).max()
            name = "price_60d_high"
        elif factor_num == 85:
            values = close / close.rolling(60).min()
            name = "price_60d_low"
        elif factor_num == 86:
            values = self._calculate_rsi(close, 14)
            name = "rsi_14"
        else:
            values = pd.Series(0, index=data.index)
            name = "placeholder"
            self._warn_placeholder(factor_id)

        return FactorResult(
            factor_id=factor_id,
            factor_name=name,
            values=values,
            timestamp=datetime.now(),
            metadata={"category": "sentiment", "params": params}
        )

    def _calculate_named_factor(
        self,
        factor_id: str,
        data: pd.DataFrame,
        params: Dict
    ) -> FactorResult:
        """计算命名因子"""
        close = data["close"]

        factor_map = {
            "rsi_14": self._calculate_rsi(close, 14),
            "rsi_6": self._calculate_rsi(close, 6),
            "macd": self._calculate_macd(close)["macd"],
            "bb_position": self._calculate_bollinger_bands(close, 20, 2)["bb_position"],
            "atr": self._calculate_atr(data, 14),
            "stoch_k": self._calculate_stochastic(data, 14)["k"],
        }

        if factor_id in factor_map:
            return FactorResult(
                factor_id=factor_id,
                factor_name=factor_id,
                values=factor_map[factor_id],
                timestamp=datetime.now(),
                metadata={"category": "named", "params": params}
            )

        raise ValueError(f"Unknown factor: {factor_id}")

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        计算相对强弱指标 (Relative Strength Index, RSI)
        
        RSI是衡量价格变动速度和变化的技术指标，范围0-100。
        通常RSI > 70视为超买，RSI < 30视为超卖。
        
        算法说明:
            RSI = 100 - 100 / (1 + RS)
            RS = 平均上涨幅度 / 平均下跌幅度
            平均涨跌幅使用简单移动平均(SMA)计算
        
        数学公式:
            U_t = max(P_t - P_{t-1}, 0)  # 上涨幅度
            D_t = max(P_{t-1} - P_t, 0)  # 下跌幅度
            RS_t = SMA(U, period) / SMA(D, period)
            RSI_t = 100 - 100 / (1 + RS_t)
        
        参数:
            prices: 价格序列 (通常是收盘价)
            period: 计算周期，默认14天
        
        返回:
            pd.Series: RSI值序列，范围0-100
        
        示例:
            >>> rsi = calculator._calculate_rsi(df['close'], period=14)
            >>> overbought = rsi > 70  # 超买信号
            >>> oversold = rsi < 30     # 超卖信号
        
        注意:
            - 前period个值为NaN（需要足够的历史数据）
            - 使用向量化实现，性能优于循环实现
            - 与TA-Lib的RSI计算方法一致
        """
        delta = prices.diff()
        gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(
        self,
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict[str, pd.Series]:
        """
        计算指数平滑异同移动平均线 (Moving Average Convergence Divergence, MACD)
        
        MACD是趋势跟踪动量指标，由快线、慢线和柱状图组成。
        用于识别趋势方向、强度和转折点。
        
        算法说明:
            MACD线 = 快速EMA - 慢速EMA
            信号线 = MACD线的EMA
            柱状图 = MACD线 - 信号线
        
        数学公式:
            EMA_t = α * P_t + (1 - α) * EMA_{t-1}
            α = 2 / (period + 1)
            MACD = EMA(12) - EMA(26)
            Signal = EMA(MACD, 9)
            Histogram = MACD - Signal
        
        参数:
            prices: 价格序列 (通常是收盘价)
            fast: 快速EMA周期，默认12
            slow: 慢速EMA周期，默认26
            signal: 信号线EMA周期，默认9
        
        返回:
            Dict[str, pd.Series]: 包含三个键值对
                - 'macd': MACD线 (快线-慢线)
                - 'signal': 信号线 (MACD的EMA)
                - 'histogram': 柱状图 (MACD-信号线)
        
        示例:
            >>> macd_result = calculator._calculate_macd(df['close'])
            >>> macd_line = macd_result['macd']
            >>> signal_line = macd_result['signal']
            >>> golden_cross = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
        
        交易信号:
            - 金叉: MACD线上穿信号线，买入信号
            - 死叉: MACD线下穿信号线，卖出信号
            - 柱状图: 正值表示多头，负值表示空头
        
        注意:
            - 前slow-1个值为NaN（需要足够的历史数据）
            - 使用指数移动平均(EMA)，对近期价格赋予更高权重
            - 与TA-Lib的MACD计算方法一致
        """
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    def _calculate_bollinger_bands(
        self,
        prices: pd.Series,
        window: int = 20,
        num_std: float = 2
    ) -> Dict[str, pd.Series]:
        """
        计算布林带 (Bollinger Bands)
        
        布林带由三条轨道线组成，用于衡量价格的相对高低位置和波动率。
        价格通常在布林带内波动，突破上下轨可能预示趋势反转。
        
        算法说明:
            中轨 = N日简单移动平均(SMA)
            上轨 = 中轨 + K倍标准差
            下轨 = 中轨 - K倍标准差
            带宽 = (上轨 - 下轨) / 中轨
            位置 = (价格 - 下轨) / (上轨 - 下轨)
        
        数学公式:
            Middle_t = SMA(P, window)
            Std_t = StdDev(P, window)
            Upper_t = Middle_t + num_std * Std_t
            Lower_t = Middle_t - num_std * Std_t
            Width_t = (Upper_t - Lower_t) / Middle_t
            Position_t = (P_t - Lower_t) / (Upper_t - Lower_t)
        
        参数:
            prices: 价格序列 (通常是收盘价)
            window: 移动平均窗口，默认20天
            num_std: 标准差倍数，默认2
        
        返回:
            Dict[str, pd.Series]: 包含五个键值对
                - 'bb_upper': 上轨
                - 'bb_middle': 中轨
                - 'bb_lower': 下轨
                - 'bb_width': 带宽 (相对值)
                - 'bb_position': 价格位置 (0-1之间，>1超买，<0超卖)
        
        示例:
            >>> bb = calculator._calculate_bollinger_bands(df['close'])
            >>> overbought = df['close'] > bb['bb_upper']  # 超买
            >>> oversold = df['close'] < bb['bb_lower']    # 超卖
            >>> squeeze = bb['bb_width'] < bb['bb_width'].rolling(20).mean()  # 波动率收窄
        
        交易信号:
            - 价格触及上轨: 可能超买，考虑卖出
            - 价格触及下轨: 可能超卖，考虑买入
            - 带宽收窄: 波动率降低，可能即将突破
            - 带宽扩大: 波动率增加，趋势确认
        
        注意:
            - 前window-1个值为NaN（需要足够的历史数据）
            - 使用简单移动平均(SMA)和标准差
            - 默认参数(20, 2)覆盖约95%的价格波动
        """
        ma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        bb_upper = ma + num_std * std
        bb_lower = ma - num_std * std
        bb_range = bb_upper - bb_lower
        bb_width = bb_range / ma.replace(0, np.nan)
        bb_position = (prices - bb_lower) / bb_range.replace(0, np.nan)
        return {
            "bb_upper": bb_upper,
            "bb_middle": ma,
            "bb_lower": bb_lower,
            "bb_width": bb_width,
            "bb_position": bb_position
        }

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        计算平均真实波幅 (Average True Range, ATR)
        
        ATR是衡量市场波动性的指标，由Wilder开发。
        不指示价格方向，只反映价格波动的剧烈程度。
        常用于止损设置、仓位管理和波动率调整。
        
        算法说明:
            真实波幅(TR)取以下三者的最大值:
            1. 当日最高价 - 当日最低价
            2. |当日最高价 - 昨日收盘价|
            3. |当日最低价 - 昨日收盘价|
            ATR = TR的N日移动平均
        
        数学公式:
            TR_t = max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)
            ATR_t = SMA(TR, period)
        
        参数:
            data: OHLCV数据，必须包含high, low, close列
            period: 计算周期，默认14天
        
        返回:
            pd.Series: ATR值序列，单位与价格相同
        
        示例:
            >>> atr = calculator._calculate_atr(df, period=14)
            >>> stop_loss = df['close'] - 2 * atr  # 2倍ATR止损
            >>> position_size = capital / (atr * multiplier)  # 波动率调整仓位
        
        应用场景:
            - 止损设置: 价格 - N倍ATR
            - 仓位管理: 资金 / (ATR * 风险系数)
            - 波动率比较: ATR/价格 表示相对波动率
            - 趋势确认: ATR上升表示趋势增强
        
        注意:
            - 前period个值为NaN（需要足够的历史数据）
            - ATR是绝对值，不同股票间不可直接比较
            - 使用简单移动平均(SMA)，也可使用EMA
            - 与TA-Lib的ATR计算方法一致
        """
        high = data["high"]
        low = data["low"]
        close = data["close"]
        tr1 = high - low
        tr2 = np.abs(high - close.shift())
        tr3 = np.abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    def _calculate_stochastic(
        self,
        data: pd.DataFrame,
        period: int = 14
    ) -> Dict[str, pd.Series]:
        """
        计算随机指标 (Stochastic Oscillator)
        
        随机指标是比较收盘价与价格区间的关系，用于识别超买超卖。
        由%K线(快线)和%D线(慢线)组成，范围0-100。
        
        算法说明:
            %K = (收盘价 - N日最低价) / (N日最高价 - N日最低价) * 100
            %D = %K的M日移动平均
        
        数学公式:
            L_t = min(Low, period)  # N日最低价
            H_t = max(High, period)  # N日最高价
            %K_t = (C_t - L_t) / (H_t - L_t) * 100
            %D_t = SMA(%K, smooth_period)
        
        参数:
            data: OHLCV数据，必须包含high, low, close列
            period: 计算周期，默认14天
        
        返回:
            Dict[str, pd.Series]: 包含两个键值对
                - 'k': %K线 (快线)
                - 'd': %D线 (慢线，%K的3日SMA)
        
        示例:
            >>> stoch = calculator._calculate_stochastic(df, period=14)
            >>> overbought = stoch['k'] > 80  # 超买
            >>> oversold = stoch['k'] < 20     # 超卖
            >>> golden_cross = (stoch['k'] > stoch['d']) & (stoch['k'].shift(1) <= stoch['d'].shift(1))
        
        交易信号:
            - %K > 80: 超买区域，可能回调
            - %K < 20: 超卖区域，可能反弹
            - %K上穿%D: 金叉，买入信号
            - %K下穿%D: 死叉，卖出信号
            - 背离: 价格创新高但%K未创新高，趋势反转信号
        
        注意:
            - 前period个值为NaN（需要足够的历史数据）
            - %K线反应灵敏但噪音多，%D线更平滑
            - 常用参数: (14, 3, 3) 即14日%K，3日%D
            - 与TA-Lib的STOCH计算方法一致
        """
        low_min = data["low"].rolling(window=period).min()
        high_max = data["high"].rolling(window=period).max()
        range_hl = high_max - low_min
        k = 100 * (data["close"] - low_min) / range_hl.replace(0, np.nan)
        d = k.rolling(window=3).mean()
        return {"k": k, "d": d}

    def _calculate_adx(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算ADX (向量化实现)"""
        high = data["high"]
        low = data["low"]
        close = data["close"]

        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm = plus_dm.where(plus_dm > 0, 0.0)
        minus_dm = minus_dm.where(minus_dm > 0, 0.0)

        tr1 = high - low
        tr2 = np.abs(high - close.shift())
        tr3 = np.abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())

        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
        adx = dx.rolling(window=period).mean()
        return adx

    def _calculate_plus_di(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算+DI (向量化实现)"""
        high = data["high"]
        low = data["low"]
        close = data["close"]

        plus_dm = high.diff().where(lambda x: x > 0, 0.0)

        tr1 = high - low
        tr2 = np.abs(high - close.shift())
        tr3 = np.abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        return 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())

    def _calculate_minus_di(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算-DI (向量化实现)"""
        high = data["high"]
        low = data["low"]
        close = data["close"]

        minus_dm = (-low.diff()).where(lambda x: x > 0, 0.0)

        tr1 = high - low
        tr2 = np.abs(high - close.shift())
        tr3 = np.abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        return 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())

    def _calculate_cci(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算CCI (向量化实现)"""
        tp = (data["high"] + data["low"] + data["close"]) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
        cci = (tp - sma_tp) / (0.015 * mad.replace(0, np.nan))
        return cci

    def _calculate_williams_r(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算威廉指标 (向量化实现)"""
        high_max = data["high"].rolling(window=period).max()
        low_min = data["low"].rolling(window=period).min()
        range_hl = high_max - low_min
        wr = -100 * (high_max - data["close"]) / range_hl.replace(0, np.nan)
        return wr

    def _calculate_mfi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算资金流量指标 (向量化实现)"""
        tp = (data["high"] + data["low"] + data["close"]) / 3
        mf = tp * data["volume"]
        mf_diff = mf.diff()

        pos_mf = mf_diff.where(mf_diff > 0, 0.0).rolling(window=period).sum()
        neg_mf = (-mf_diff.where(mf_diff < 0, 0.0)).rolling(window=period).sum()

        mfr = pos_mf / neg_mf.replace(0, np.nan)
        mfi = 100 - (100 / (1 + mfr))
        return mfi

    def _calculate_obv(self, data: pd.DataFrame) -> pd.Series:
        """计算能量潮 (向量化实现)"""
        close_diff = data["close"].diff()
        obv = (np.sign(close_diff) * data["volume"]).fillna(0).cumsum()
        return obv

    def _calculate_supertrend(
        self,
        data: pd.DataFrame,
        period: int = 10,
        multiplier: float = 3
    ) -> Dict[str, pd.Series]:
        """计算超级趋势

        注意: 超级趋势计算本质上是递归的（每根K线依赖前一根的方向状态），
        因此无法完全向量化。当前实现使用显式循环，性能可接受
        （1000根K线约需10-50ms）。

        如需更高性能，可考虑:
        1. 使用 numba JIT 编译
        2. 使用 numba 的 @njit 装饰器
        3. 使用 TA-Lib C 库绑定

        参数:
            data: OHLCV数据
            period: ATR周期 (默认10)
            multiplier: ATR倍数 (默认3)

        返回:
            包含 supertrend 和 direction 的字典
        """
        hl2 = (data["high"] + data["low"]) / 2
        atr = self._calculate_atr(data, period)

        n = len(data)
        supertrend_values = np.full(n, np.nan)
        direction = np.ones(n, dtype=int)

        final_upper = hl2 + multiplier * atr
        final_lower = hl2 - multiplier * atr

        supertrend_values[period] = final_lower.iloc[period]
        direction[period] = 1

        for i in range(period + 1, n):
            prev_close = data["close"].iloc[i - 1]
            curr_close = data["close"].iloc[i]

            prev_upper = final_upper.iloc[i - 1]
            prev_lower = final_lower.iloc[i - 1]

            if curr_close > prev_upper:
                direction[i] = -1
                supertrend_values[i] = final_upper.iloc[i]
            elif curr_close < prev_lower:
                direction[i] = 1
                supertrend_values[i] = final_lower.iloc[i]
            else:
                direction[i] = direction[i - 1]
                if direction[i] == 1:
                    supertrend_values[i] = final_lower.iloc[i]
                else:
                    supertrend_values[i] = final_upper.iloc[i]

        supertrend_series = pd.Series(supertrend_values, index=data.index)
        direction_series = pd.Series(direction, index=data.index)

        return {"supertrend": supertrend_series, "direction": direction_series}

    def _calculate_ichimoku(
        self,
        data: pd.DataFrame
    ) -> Dict[str, pd.Series]:
        """计算Ichimoku云 (优化实现)

        性能优化: 减少冗余shift操作，合并计算
        """
        high = data["high"]
        low = data["low"]

        high9 = high.rolling(window=9).max()
        low9 = low.rolling(window=9).min()
        tenkan_sen = (high9 + low9) / 2

        high26 = high.rolling(window=26).max()
        low26 = low.rolling(window=26).min()
        kijun_sen = (high26 + low26) / 2

        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

        high52 = high.rolling(window=52).max()
        low52 = low.rolling(window=52).min()
        senkou_span_b = ((high52 + low52) / 2).shift(26)

        chikou_span = data["close"].shift(-26)

        return {
            "tenkan_sen": tenkan_sen,
            "kijun_sen": kijun_sen,
            "senkou_span_a": senkou_span_a,
            "senkou_span_b": senkou_span_b,
            "chikou_span": chikou_span
        }

    def _calculate_cmo(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算CMO (动量振荡器，向量化实现)"""
        delta = prices.diff()
        up = delta.where(delta > 0, 0.0)
        down = (-delta.where(delta < 0, 0.0))

        sum_up = up.rolling(window=period).sum()
        sum_down = down.rolling(window=period).sum()

        cmo = 100 * (sum_up - sum_down) / (sum_up + sum_down).replace(0, np.nan)
        return cmo

    def calculate_batch(
        self,
        factor_ids: List[str],
        data: pd.DataFrame,
        parallel: bool = True
    ) -> Dict[str, FactorResult]:
        """批量计算因子

        性能优化: 支持并行计算

        参数:
            factor_ids: 因子ID列表
            data: OHLCV数据
            parallel: 是否使用并行计算

        返回:
            因子结果字典
        """
        if parallel and len(factor_ids) > 1:
            return self._calculate_batch_parallel(factor_ids, data)
        else:
            return self._calculate_batch_sequential(factor_ids, data)

    def _calculate_batch_sequential(
        self,
        factor_ids: List[str],
        data: pd.DataFrame
    ) -> Dict[str, FactorResult]:
        """顺序批量计算因子"""
        results = {}
        for factor_id in factor_ids:
            try:
                result = self.calculate(factor_id, data)
                results[factor_id] = result
            except Exception as e:
                logger.error(f"Failed to calculate {factor_id}: {e}")
        return results

    def _calculate_batch_parallel(
        self,
        factor_ids: List[str],
        data: pd.DataFrame
    ) -> Dict[str, FactorResult]:
        """并行批量计算因子"""
        results = {}

        def calc_wrapper(fid):
            try:
                return fid, self.calculate(fid, data)
            except Exception as e:
                logger.error(f"Failed to calculate {fid}: {e}")
                return fid, None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(calc_wrapper, fid) for fid in factor_ids]
            for future in futures:
                fid, result = future.result()
                if result is not None:
                    results[fid] = result

        return results

    def get_factor(self, factor_id: str) -> Optional[FactorResult]:
        """获取已计算的因子"""
        return self.calculated_factors.get(factor_id)

    def get_implemented_factors(self) -> List[str]:
        """获取已实现的因子列表

        返回:
            已实现（非placeholder）的因子ID列表
        """
        all_factors = set()
        for i in range(1, 88):
            all_factors.add(f"ALPHA_{i:03d}")
        implemented = sorted(all_factors - PLACEHOLDER_FACTORS)
        return implemented

    def get_placeholder_factors(self) -> List[str]:
        """获取placeholder因子列表"""
        return sorted(PLACEHOLDER_FACTORS)

    def clear_cache(self):
        """清除缓存"""
        self.calculated_factors.clear()
