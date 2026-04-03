"""
统计套利模块使用示例

演示如何使用统计套利模块进行配对交易和市场中性组合构建。

模块ID: STATISTICAL_ARBITRAGE_MODULE_001
版本: v1.0.0
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from statistical_arbitrage_module import (
    SignalType,
    CointegratedPair,
    PairTradingSignal,
    PortfolioAllocation,
    StatisticalArbitrageModule
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def generate_mock_price_data(
    n_stocks: int = 10,
    n_days: int = 252
) -> pd.DataFrame:
    """
    生成模拟价格数据
    
    Args:
        n_stocks: 股票数量
        n_days: 天数
        
    Returns:
        pd.DataFrame: 价格数据
    """
    np.random.seed(42)
    
    dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')
    
    stocks = [f'Stock_{i:02d}' for i in range(n_stocks)]
    
    prices = pd.DataFrame(index=dates, columns=stocks)
    
    for i, stock in enumerate(stocks):
        if i < n_stocks // 2:
            base_price = 100 + i * 10
            trend = np.random.randn(n_days).cumsum() * 0.5
            noise = np.random.randn(n_days) * 2
            prices[stock] = base_price + trend + noise
        else:
            correlated_stock = stocks[i - n_stocks // 2]
            hedge_ratio = 0.8 + np.random.rand() * 0.4
            prices[stock] = prices[correlated_stock] * hedge_ratio + np.random.randn(n_days) * 3
    
    return prices


def example_find_cointegrated_pairs():
    """示例1: 寻找协整股票对"""
    print("\n" + "="*80)
    print("示例1: 寻找协整股票对")
    print("="*80 + "\n")
    
    module = StatisticalArbitrageModule()
    
    price_data = generate_mock_price_data(n_stocks=10, n_days=252)
    
    print(f"价格数据形状: {price_data.shape}")
    print(f"股票列表: {price_data.columns.tolist()}")
    
    pairs = module.find_cointegrated_pairs(price_data)
    
    print(f"\n找到 {len(pairs)} 对协整股票对:")
    for i, pair in enumerate(pairs[:5], 1):
        print(f"\n配对 {i}:")
        print(f"  股票A: {pair.stock_a}")
        print(f"  股票B: {pair.stock_b}")
        print(f"  对冲比例: {pair.hedge_ratio:.4f}")
        print(f"  相关系数: {pair.correlation:.4f}")
        print(f"  半衰期: {pair.half_life:.2f} 天")
        print(f"  P值: {pair.p_value:.4f}")


def example_generate_trading_signals():
    """示例2: 生成配对交易信号"""
    print("\n" + "="*80)
    print("示例2: 生成配对交易信号")
    print("="*80 + "\n")
    
    module = StatisticalArbitrageModule()
    
    price_data = generate_mock_price_data(n_stocks=10, n_days=252)
    
    pairs = module.find_cointegrated_pairs(price_data)
    
    if len(pairs) == 0:
        print("未找到协整股票对")
        return
    
    signals = module.generate_pair_trading_signals(price_data, pairs)
    
    print(f"生成 {len(signals)} 个交易信号:")
    for i, signal in enumerate(signals[:5], 1):
        print(f"\n信号 {i}:")
        print(f"  配对: {signal.pair.stock_a} - {signal.pair.stock_b}")
        print(f"  信号类型: {signal.signal_type.value}")
        print(f"  Z-score: {signal.z_score:.4f}")
        print(f"  价差: {signal.spread:.4f}")
        print(f"  仓位比例: {signal.position_ratio:.4f}")


def example_construct_portfolio():
    """示例3: 构建市场中性组合"""
    print("\n" + "="*80)
    print("示例3: 构建市场中性组合")
    print("="*80 + "\n")
    
    module = StatisticalArbitrageModule()
    
    price_data = generate_mock_price_data(n_stocks=10, n_days=252)
    
    pairs, signals, allocation = module.run_full_pipeline(price_data)
    
    print(f"组合配置:")
    print(f"  多头头寸数量: {len(allocation.long_positions)}")
    print(f"  空头头寸数量: {len(allocation.short_positions)}")
    print(f"  净敞口: {allocation.net_exposure:.4f}")
    print(f"  总敞口: {allocation.gross_exposure:.4f}")
    
    if allocation.long_positions:
        print(f"\n多头头寸:")
        for stock, weight in list(allocation.long_positions.items())[:5]:
            print(f"  {stock}: {weight:.4f}")
    
    if allocation.short_positions:
        print(f"\n空头头寸:")
        for stock, weight in list(allocation.short_positions.items())[:5]:
            print(f"  {stock}: {weight:.4f}")


def example_full_pipeline():
    """示例4: 完整流程"""
    print("\n" + "="*80)
    print("示例4: 完整统计套利流程")
    print("="*80 + "\n")
    
    module = StatisticalArbitrageModule()
    
    price_data = generate_mock_price_data(n_stocks=20, n_days=252)
    
    print("步骤1: 寻找协整股票对")
    pairs = module.find_cointegrated_pairs(price_data)
    print(f"  找到 {len(pairs)} 对协整股票对")
    
    print("\n步骤2: 生成交易信号")
    signals = module.generate_pair_trading_signals(price_data, pairs)
    print(f"  生成 {len(signals)} 个交易信号")
    
    print("\n步骤3: 构建市场中性组合")
    allocation = module.construct_market_neutral_portfolio(signals)
    print(f"  净敞口: {allocation.net_exposure:.4f}")
    print(f"  总敞口: {allocation.gross_exposure:.4f}")
    
    print("\n步骤4: 导出结果")
    print(f"  协整股票对: {len(pairs)} 对")
    print(f"  交易信号: {len(signals)} 个")
    print(f"  多头头寸: {len(allocation.long_positions)} 只")
    print(f"  空头头寸: {len(allocation.short_positions)} 只")


def example_signal_analysis():
    """示例5: 信号分析"""
    print("\n" + "="*80)
    print("示例5: 信号分析")
    print("="*80 + "\n")
    
    module = StatisticalArbitrageModule()
    
    price_data = generate_mock_price_data(n_stocks=10, n_days=252)
    
    pairs, signals, allocation = module.run_full_pipeline(price_data)
    
    if len(signals) == 0:
        print("未生成交易信号")
        return
    
    print("信号统计:")
    
    signal_types = {}
    for signal in signals:
        signal_type = signal.signal_type.value
        signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
    
    for signal_type, count in signal_types.items():
        print(f"  {signal_type}: {count} 个")
    
    z_scores = [signal.z_score for signal in signals]
    print(f"\nZ-score统计:")
    print(f"  平均值: {np.mean(z_scores):.4f}")
    print(f"  标准差: {np.std(z_scores):.4f}")
    print(f"  最大值: {np.max(z_scores):.4f}")
    print(f"  最小值: {np.min(z_scores):.4f}")
    
    position_ratios = [signal.position_ratio for signal in signals]
    print(f"\n仓位比例统计:")
    print(f"  平均值: {np.mean(position_ratios):.4f}")
    print(f"  标准差: {np.std(position_ratios):.4f}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("统计套利模块使用示例")
    print("="*80)
    
    example_find_cointegrated_pairs()
    example_generate_trading_signals()
    example_construct_portfolio()
    example_full_pipeline()
    example_signal_analysis()
    
    print("\n" + "="*80)
    print("示例执行完成")
    print("="*80 + "\n")
