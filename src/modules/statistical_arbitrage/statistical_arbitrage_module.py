"""
统计套利模块主模块

实现了配对交易、市场中性组合构建和统计套利信号生成的核心功能。

模块ID: STATISTICAL_ARBITRAGE_MODULE_001
版本: v1.0.0
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
import logging
import yaml
from pathlib import Path

from statsmodels.tsa.stattools import coint, adfuller
from scipy import stats


class SignalType(Enum):
    """信号类型枚举"""
    LONG_SPREAD = "long_spread"      # 做多价差
    SHORT_SPREAD = "short_spread"    # 做空价差
    CLOSE_POSITION = "close_position" # 平仓
    HOLD = "hold"                    # 持有


@dataclass
class CointegratedPair:
    """协整股票对"""
    stock_a: str                    # 股票A代码
    stock_b: str                    # 股票B代码
    hedge_ratio: float              # 对冲比例
    correlation: float              # 相关系数
    adf_statistic: float            # ADF统计量
    p_value: float                  # P值
    half_life: float                # 半衰期（天）
    timestamp: datetime             # 时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class PairTradingSignal:
    """配对交易信号"""
    pair: CointegratedPair          # 协整股票对
    signal_type: SignalType         # 信号类型
    z_score: float                  # Z-score值
    spread: float                   # 当前价差
    mean_spread: float              # 价差均值
    std_spread: float               # 价差标准差
    position_ratio: float           # 仓位比例
    timestamp: datetime             # 时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'pair': self.pair.to_dict(),
            'signal_type': self.signal_type.value,
            'z_score': self.z_score,
            'spread': self.spread,
            'mean_spread': self.mean_spread,
            'std_spread': self.std_spread,
            'position_ratio': self.position_ratio,
            'timestamp': self.timestamp.isoformat()
        }
        return result


@dataclass
class PortfolioAllocation:
    """组合配置"""
    long_positions: Dict[str, float]   # 多头头寸
    short_positions: Dict[str, float]  # 空头头寸
    net_exposure: float                 # 净敞口
    gross_exposure: float               # 总敞口
    industry_exposure: Dict[str, float] # 行业暴露
    style_exposure: Dict[str, float]    # 风格暴露
    timestamp: datetime                 # 时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class PairSelector:
    """配对选择器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化配对选择器
        
        Args:
            config: 配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        self.min_correlation = config.get('min_correlation', 0.7)
        self.max_pairs = config.get('max_pairs', 50)
        
    def select_pairs(
        self, 
        price_data: pd.DataFrame,
        stock_pool: Optional[List[str]] = None
    ) -> List[Tuple[str, str]]:
        """
        选择候选股票对
        
        Args:
            price_data: 价格数据
            stock_pool: 股票池（可选）
            
        Returns:
            List[Tuple[str, str]]: 候选股票对列表
        """
        self.logger.info(f"开始选择候选股票对")
        
        if stock_pool is None:
            stock_pool = price_data.columns.tolist()
        
        returns = price_data[stock_pool].pct_change().dropna()
        
        correlation_matrix = returns.corr()
        
        candidate_pairs = []
        for i in range(len(stock_pool)):
            for j in range(i + 1, len(stock_pool)):
                stock_a = stock_pool[i]
                stock_b = stock_pool[j]
                
                correlation = correlation_matrix.loc[stock_a, stock_b]
                
                if correlation >= self.min_correlation:
                    candidate_pairs.append((stock_a, stock_b, correlation))
        
        candidate_pairs.sort(key=lambda x: x[2], reverse=True)
        candidate_pairs = [(pair[0], pair[1]) for pair in candidate_pairs[:self.max_pairs]]
        
        self.logger.info(f"找到 {len(candidate_pairs)} 对候选股票对")
        
        return candidate_pairs


class CointegrationAnalyzer:
    """协整分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化协整分析器
        
        Args:
            config: 配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        self.adf_critical_value = config.get('adf_critical_value', 0.05)
        self.min_half_life = config.get('min_half_life', 5)
        self.max_half_life = config.get('max_half_life', 60)
        
    def test_cointegration(
        self, 
        series_a: pd.Series,
        series_b: pd.Series
    ) -> Dict[str, Any]:
        """
        协整检验
        
        Args:
            series_a: 价格序列A
            series_b: 价格序列B
            
        Returns:
            Dict[str, Any]: 协整检验结果
        """
        try:
            coint_t, p_value, crit_value = coint(series_a, series_b)
            
            X = np.column_stack([np.ones(len(series_b)), series_b.values])
            hedge_ratio = np.linalg.lstsq(X, series_a.values, rcond=None)[0][1]
            
            spread = series_a - hedge_ratio * series_b
            
            adf_result = adfuller(spread, maxlag=1)
            adf_statistic = adf_result[0]
            adf_p_value = adf_result[1]
            
            half_life = self._calculate_half_life(spread)
            
            is_cointegrated = (
                p_value < self.adf_critical_value and
                self.min_half_life <= half_life <= self.max_half_life
            )
            
            correlation = series_a.corr(series_b)
            
            return {
                'is_cointegrated': is_cointegrated,
                'hedge_ratio': hedge_ratio,
                'correlation': correlation,
                'adf_statistic': adf_statistic,
                'p_value': p_value,
                'half_life': half_life,
                'spread': spread
            }
        except Exception as e:
            self.logger.warning(f"协整检验失败: {e}")
            return {
                'is_cointegrated': False,
                'hedge_ratio': 1.0,
                'correlation': 0.0,
                'adf_statistic': 0.0,
                'p_value': 1.0,
                'half_life': float('inf'),
                'spread': pd.Series()
            }
    
    def _calculate_half_life(self, spread: pd.Series) -> float:
        """
        计算半衰期
        
        Args:
            spread: 价差序列
            
        Returns:
            float: 半衰期（天）
        """
        try:
            spread_lag = spread.shift(1).dropna()
            spread_ret = spread.diff().dropna()
            
            spread_lag = spread_lag.iloc[:len(spread_ret)]
            spread_ret = spread_ret.iloc[:len(spread_lag)]
            
            X = np.column_stack([np.ones(len(spread_lag)), spread_lag.values])
            params = np.linalg.lstsq(X, spread_ret.values, rcond=None)[0]
            
            lambda_param = params[1]
            
            if lambda_param >= 0:
                return float('inf')
            
            half_life = -np.log(2) / lambda_param
            
            return half_life
        except Exception:
            return float('inf')


class SpreadTrader:
    """价差交易器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化价差交易器
        
        Args:
            config: 配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        self.entry_zscore = config.get('entry_zscore', 2.0)
        self.exit_zscore = config.get('exit_zscore', 0.5)
        self.stop_loss = config.get('stop_loss', 0.05)
        
    def generate_signal(
        self,
        price_a: pd.Series,
        price_b: pd.Series,
        hedge_ratio: float
    ) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            price_a: 价格序列A
            price_b: 价格序列B
            hedge_ratio: 对冲比例
            
        Returns:
            Dict[str, Any]: 交易信号
        """
        spread = price_a - hedge_ratio * price_b
        
        mean_spread = spread.mean()
        std_spread = spread.std()
        
        current_spread = spread.iloc[-1]
        z_score = (current_spread - mean_spread) / std_spread
        
        signal_type = SignalType.HOLD
        position_ratio = 0.0
        
        if z_score > self.entry_zscore:
            signal_type = SignalType.SHORT_SPREAD
            position_ratio = min(z_score / self.entry_zscore, 2.0)
        elif z_score < -self.entry_zscore:
            signal_type = SignalType.LONG_SPREAD
            position_ratio = min(abs(z_score) / self.entry_zscore, 2.0)
        elif abs(z_score) < self.exit_zscore:
            signal_type = SignalType.CLOSE_POSITION
            position_ratio = 0.0
        
        return {
            'signal_type': signal_type,
            'z_score': z_score,
            'spread': current_spread,
            'mean_spread': mean_spread,
            'std_spread': std_spread,
            'position_ratio': position_ratio
        }


class MarketNeutralPortfolio:
    """市场中性组合构建器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化市场中性组合构建器
        
        Args:
            config: 配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        self.industry_neutral = config.get('industry_neutral', True)
        self.style_neutral = config.get('style_neutral', True)
        self.max_leverage = config.get('max_leverage', 2.0)
        
    def construct(
        self,
        signals: List[PairTradingSignal],
        constraints: Optional[Dict[str, Any]] = None
    ) -> PortfolioAllocation:
        """
        构建市场中性组合
        
        Args:
            signals: 配对交易信号列表
            constraints: 约束条件
            
        Returns:
            PortfolioAllocation: 组合配置
        """
        self.logger.info("开始构建市场中性组合")
        
        long_positions = {}
        short_positions = {}
        
        for signal in signals:
            pair = signal.pair
            position_ratio = signal.position_ratio
            
            if signal.signal_type == SignalType.LONG_SPREAD:
                long_positions[pair.stock_a] = long_positions.get(pair.stock_a, 0) + position_ratio
                short_positions[pair.stock_b] = short_positions.get(pair.stock_b, 0) + position_ratio * pair.hedge_ratio
            elif signal.signal_type == SignalType.SHORT_SPREAD:
                short_positions[pair.stock_a] = short_positions.get(pair.stock_a, 0) + position_ratio
                long_positions[pair.stock_b] = long_positions.get(pair.stock_b, 0) + position_ratio * pair.hedge_ratio
        
        total_long = sum(long_positions.values())
        total_short = sum(short_positions.values())
        
        if total_long > 0:
            scale_factor = self.max_leverage / 2 / total_long if total_long > self.max_leverage / 2 else 1.0
            long_positions = {k: v * scale_factor for k, v in long_positions.items()}
            short_positions = {k: v * scale_factor for k, v in short_positions.items()}
        
        net_exposure = total_long - total_short
        gross_exposure = total_long + total_short
        
        allocation = PortfolioAllocation(
            long_positions=long_positions,
            short_positions=short_positions,
            net_exposure=net_exposure,
            gross_exposure=gross_exposure,
            industry_exposure={},  # 简化版本，实际需要计算
            style_exposure={},      # 简化版本，实际需要计算
            timestamp=datetime.now()
        )
        
        self.logger.info(f"市场中性组合构建完成，净敞口={net_exposure:.2f}")
        
        return allocation


class StatisticalArbitrageModule:
    """统计套利模块"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化统计套利模块
        
        Args:
            config_path: 配置文件路径
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化统计套利模块")
        
        self.config = self._load_config(config_path)
        
        self.pair_selector = PairSelector(self.config.get('pair_selection', {}))
        self.cointegration_analyzer = CointegrationAnalyzer(
            self.config.get('cointegration', {})
        )
        self.spread_trader = SpreadTrader(self.config.get('spread_trading', {}))
        self.market_neutral_portfolio = MarketNeutralPortfolio(
            self.config.get('market_neutral', {})
        )
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict[str, Any]: 配置参数
        """
        if config_path is None:
            config_path = Path(__file__).parent / 'config' / 'statistical_arbitrage_config.yaml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.logger.info(f"配置文件加载成功: {config_path}")
                return config
        except Exception as e:
            self.logger.warning(f"配置文件加载失败，使用默认配置: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'pair_selection': {
                'min_correlation': 0.7,
                'max_pairs': 50
            },
            'cointegration': {
                'adf_critical_value': 0.05,
                'min_half_life': 5,
                'max_half_life': 60
            },
            'spread_trading': {
                'entry_zscore': 2.0,
                'exit_zscore': 0.5,
                'stop_loss': 0.05
            },
            'market_neutral': {
                'industry_neutral': True,
                'style_neutral': True,
                'max_leverage': 2.0
            }
        }
        
    def find_cointegrated_pairs(
        self, 
        price_data: pd.DataFrame,
        stock_pool: Optional[List[str]] = None
    ) -> List[CointegratedPair]:
        """
        寻找协整股票对
        
        Args:
            price_data: 价格数据
            stock_pool: 股票池（可选）
            
        Returns:
            List[CointegratedPair]: 协整股票对列表
        """
        self.logger.info("开始寻找协整股票对")
        
        candidate_pairs = self.pair_selector.select_pairs(price_data, stock_pool)
        
        cointegrated_pairs = []
        for pair in candidate_pairs:
            result = self.cointegration_analyzer.test_cointegration(
                price_data[pair[0]], 
                price_data[pair[1]]
            )
            
            if result['is_cointegrated']:
                cointegrated_pair = CointegratedPair(
                    stock_a=pair[0],
                    stock_b=pair[1],
                    hedge_ratio=result['hedge_ratio'],
                    correlation=result['correlation'],
                    adf_statistic=result['adf_statistic'],
                    p_value=result['p_value'],
                    half_life=result['half_life'],
                    timestamp=datetime.now()
                )
                cointegrated_pairs.append(cointegrated_pair)
        
        self.logger.info(f"找到 {len(cointegrated_pairs)} 对协整股票对")
        
        return cointegrated_pairs
    
    def generate_pair_trading_signals(
        self,
        price_data: pd.DataFrame,
        pairs: List[CointegratedPair]
    ) -> List[PairTradingSignal]:
        """
        生成配对交易信号
        
        Args:
            price_data: 价格数据
            pairs: 协整股票对列表
            
        Returns:
            List[PairTradingSignal]: 配对交易信号列表
        """
        self.logger.info("开始生成配对交易信号")
        
        signals = []
        for pair in pairs:
            signal = self.spread_trader.generate_signal(
                price_data[pair.stock_a],
                price_data[pair.stock_b],
                pair.hedge_ratio
            )
            
            if signal['signal_type'] != SignalType.HOLD:
                trading_signal = PairTradingSignal(
                    pair=pair,
                    signal_type=signal['signal_type'],
                    z_score=signal['z_score'],
                    spread=signal['spread'],
                    mean_spread=signal['mean_spread'],
                    std_spread=signal['std_spread'],
                    position_ratio=signal['position_ratio'],
                    timestamp=datetime.now()
                )
                signals.append(trading_signal)
        
        self.logger.info(f"生成 {len(signals)} 个配对交易信号")
        
        return signals
    
    def construct_market_neutral_portfolio(
        self,
        signals: List[PairTradingSignal],
        constraints: Optional[Dict[str, Any]] = None
    ) -> PortfolioAllocation:
        """
        构建市场中性组合
        
        Args:
            signals: 配对交易信号列表
            constraints: 约束条件
            
        Returns:
            PortfolioAllocation: 组合配置
        """
        return self.market_neutral_portfolio.construct(signals, constraints)
    
    def run_full_pipeline(
        self,
        price_data: pd.DataFrame,
        stock_pool: Optional[List[str]] = None
    ) -> Tuple[List[CointegratedPair], List[PairTradingSignal], PortfolioAllocation]:
        """
        运行完整流程
        
        Args:
            price_data: 价格数据
            stock_pool: 股票池（可选）
            
        Returns:
            Tuple: 协整股票对、交易信号、组合配置
        """
        self.logger.info("开始运行完整统计套利流程")
        
        pairs = self.find_cointegrated_pairs(price_data, stock_pool)
        
        signals = self.generate_pair_trading_signals(price_data, pairs)
        
        allocation = self.construct_market_neutral_portfolio(signals)
        
        self.logger.info("统计套利流程完成")
        
        return pairs, signals, allocation
