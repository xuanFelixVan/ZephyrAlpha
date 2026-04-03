---
standard_type: 代码模板
applicable_scope: 策略研究
compliance_level: 初始标准
parent_document: ../README.md
implementation_status: 可用
owner: 研究团队
version: 1.0.0
module_id: TEMPLATE_STRATEGY
created_date: 2026-04-03
last_updated: 2026-04-03
description: 策略研究模板 - 策略逻辑实现、参数优化、回测验证
---
"""
策略研究模板

功能：策略逻辑实现、参数优化、回测验证
版本：v1.0.0
创建日期：2026-04-03
"""

# %% [markdown]
# # 策略研究与回测分析
# 
# > **项目**: ZephyrAlpha v5.1
# > **作者**: [姓名/团队]
# > **创建日期**: YYYY-MM-DD
# > **更新日期**: YYYY-MM-DD
# > **状态**: ⚪ 进行中 | ✅ 已完成 | 📊 结果已生成
# > **目标**: 实现新的交易策略，进行参数优化和回测验证，评估策略性能

# %% [markdown]
# ## 1. 环境设置与导入

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 项目特定导入
import sys
sys.path.append('../../src')

# 尝试导入策略相关模块
try:
    from src.modules.strategy_engine import StrategyEngine
    from src.modules.backtester import Backtester
    print("✅ 成功导入策略模块")
except ImportError:
    print("⚠️ 无法导入策略模块，使用简化实现")
    class StrategyEngine:
        """简化版策略引擎"""
        @staticmethod
        def calculate_signals(data, params):
            """计算交易信号"""
            # 简化实现
            signals = pd.Series(0, index=data.index)
            # 示例：简单均线策略
            if 'close' in data.columns:
                short_ma = data['close'].rolling(window=params.get('short_window', 10)).mean()
                long_ma = data['close'].rolling(window=params.get('long_window', 30)).mean()
                signals[short_ma > long_ma] = 1  # 买入信号
                signals[short_ma <= long_ma] = -1  # 卖出信号
            return signals
    
    class Backtester:
        """简化版回测器"""
        @staticmethod
        def backtest(signals, prices, initial_capital=100000, transaction_cost=0.001):
            """执行回测"""
            # 简化实现
            returns = prices.pct_change()
            strategy_returns = signals.shift(1) * returns
            cumulative_returns = (1 + strategy_returns).cumprod()
            portfolio_value = initial_capital * cumulative_returns
            return portfolio_value, strategy_returns

# 配置设置
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
pd.set_option('display.max_columns', 100)
pd.set_option('display.float_format', lambda x: f'{x:.4f}')
np.random.seed(42)

print("环境设置完成")

# %% [markdown]
# ## 2. 数据加载与预处理

# %%
print("📥 数据加载")

# 数据加载 - 根据实际数据路径修改
data_path = "../../data/processed/market_data_processed.csv"  # 示例路径
print(f"加载数据: {data_path}")

try:
    df = pd.read_csv(data_path, parse_dates=['date'])
    print("✅ 数据加载成功")
except FileNotFoundError:
    print("⚠️ 文件未找到，创建示例数据")
    # 创建示例数据用于演示
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    df = pd.DataFrame({
        'date': dates,
        'open': np.random.normal(100, 10, 500).cumsum(),
        'high': np.random.normal(105, 10, 500).cumsum(),
        'low': np.random.normal(95, 10, 500).cumsum(),
        'close': np.random.normal(102, 10, 500).cumsum(),
        'volume': np.random.randint(1000000, 10000000, 500)
    })

# 数据预处理
print("\n🔧 数据预处理")
df = df.sort_values('date')
df['returns'] = df['close'].pct_change()
df['log_returns'] = np.log(df['close'] / df['close'].shift(1))

print(f"📊 数据形状: {df.shape}")
print(f"📅 时间范围: {df['date'].min()} 到 {df['date'].max()}")
print(f"💰 价格范围: {df['close'].min():.2f} 到 {df['close'].max():.2f}")

# 查看数据
print("\n数据示例:")
display(df.head())

# %% [markdown]
# ## 3. 策略定义与实现

# %%
print("🎯 策略定义与实现")

# 3.1 定义策略类
class TradingStrategy:
    """交易策略基类"""
    
    def __init__(self, params=None):
        self.params = params or {}
        self.signals = None
        self.performance = {}
    
    def calculate_signals(self, data):
        """计算交易信号 - 子类需重写此方法"""
        raise NotImplementedError("子类必须实现calculate_signals方法")
    
    def optimize_parameters(self, data, param_grid):
        """参数优化"""
        # 简化实现 - 实际应使用网格搜索或贝叶斯优化
        best_score = -np.inf
        best_params = {}
        
        # 示例参数优化逻辑
        for params in param_grid:
            # 这里应实现参数评估逻辑
            score = self.evaluate_parameters(data, params)
            if score > best_score:
                best_score = score
                best_params = params
        
        self.params.update(best_params)
        return best_params, best_score
    
    def evaluate_parameters(self, data, params):
        """评估参数性能"""
        # 简化实现
        return np.random.random()
    
    def run(self, data):
        """运行策略"""
        self.signals = self.calculate_signals(data)
        return self.signals

# 3.2 具体策略实现 - 移动平均交叉策略
class MovingAverageCrossover(TradingStrategy):
    """移动平均交叉策略"""
    
    def calculate_signals(self, data):
        """实现移动平均交叉策略"""
        short_window = self.params.get('short_window', 10)
        long_window = self.params.get('long_window', 30)
        
        # 计算移动平均
        short_ma = data['close'].rolling(window=short_window).mean()
        long_ma = data['close'].rolling(window=long_window).mean()
        
        # 生成交易信号
        signals = pd.Series(0, index=data.index)
        signals[short_ma > long_ma] = 1    # 买入信号
        signals[short_ma <= long_ma] = -1  # 卖出信号
        
        # 添加持仓信息
        positions = signals.diff()
        
        return pd.DataFrame({
            'signal': signals,
            'position': positions,
            'short_ma': short_ma,
            'long_ma': long_ma
        })

# 3.3 实例化并运行策略
print("实例化移动平均交叉策略...")
strategy_params = {
    'short_window': 20,
    'long_window': 50
}

strategy = MovingAverageCrossover(strategy_params)
signals_df = strategy.run(df)

print(f"✅ 策略计算完成")
print(f"信号数据形状: {signals_df.shape}")
print(f"信号统计:")
print(f"  买入信号: {(signals_df['signal'] == 1).sum()}")
print(f"  卖出信号: {(signals_df['signal'] == -1).sum()}")
print(f"  无信号: {(signals_df['signal'] == 0).sum()}")

# %% [markdown]
# ## 4. 策略可视化

# %%
print("📈 策略可视化")

fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

# 4.1 价格与移动平均
axes[0].plot(df['date'], df['close'], label='收盘价', linewidth=1.5, alpha=0.7)
axes[0].plot(df['date'], signals_df['short_ma'], label=f"短期MA({strategy_params['short_window']}天)", 
             linewidth=2, alpha=0.8)
axes[0].plot(df['date'], signals_df['long_ma'], label=f"长期MA({strategy_params['long_window']}天)", 
             linewidth=2, alpha=0.8)
axes[0].set_title('价格与移动平均线', fontsize=12)
axes[0].set_ylabel('价格')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 4.2 交易信号
buy_signals = df.loc[signals_df['position'] == 1, 'date']
sell_signals = df.loc[signals_df['position'] == -1, 'date']

axes[1].plot(df['date'], df['close'], label='收盘价', linewidth=1, alpha=0.5)
axes[1].scatter(buy_signals, df.loc[df['date'].isin(buy_signals), 'close'], 
                color='green', s=50, marker='^', label='买入信号', alpha=0.7)
axes[1].scatter(sell_signals, df.loc[df['date'].isin(sell_signals), 'close'], 
                color='red', s=50, marker='v', label='卖出信号', alpha=0.7)
axes[1].set_title('交易信号', fontsize=12)
axes[1].set_ylabel('价格')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# 4.3 信号强度
axes[2].plot(df['date'], signals_df['signal'], drawstyle='steps', linewidth=1.5)
axes[2].fill_between(df['date'], 0, signals_df['signal'], 
                     where=signals_df['signal']>=0, color='green', alpha=0.3, label='买入区间')
axes[2].fill_between(df['date'], 0, signals_df['signal'], 
                     where=signals_df['signal']<=0, color='red', alpha=0.3, label='卖出区间')
axes[2].set_title('信号强度', fontsize=12)
axes[2].set_xlabel('日期')
axes[2].set_ylabel('信号')
axes[2].set_yticks([-1, 0, 1])
axes[2].set_yticklabels(['卖出', '持有', '买入'])
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 5. 回测分析

# %%
print("📊 回测分析")

# 5.1 执行回测
print("执行回测...")

# 简化回测实现
initial_capital = 100000
transaction_cost = 0.001  # 0.1%交易成本

# 计算策略收益
strategy_returns = signals_df['signal'].shift(1) * df['returns']
strategy_returns = strategy_returns.fillna(0)

# 考虑交易成本
position_changes = signals_df['signal'].diff().abs()
trading_costs = position_changes * transaction_cost
net_returns = strategy_returns - trading_costs

# 计算累积收益
cumulative_strategy = (1 + net_returns).cumprod()
cumulative_buy_hold = (1 + df['returns']).cumprod()

# 计算组合价值
portfolio_value = initial_capital * cumulative_strategy
buy_hold_value = initial_capital * cumulative_buy_hold

# 5.2 回测结果可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 累积收益对比
axes[0, 0].plot(df['date'], cumulative_strategy, label='策略收益', linewidth=2)
axes[0, 0].plot(df['date'], cumulative_buy_hold, label='买入持有', linewidth=2, alpha=0.7)
axes[0, 0].set_title('累积收益对比', fontsize=12)
axes[0, 0].set_xlabel('日期')
axes[0, 0].set_ylabel('累积收益倍数')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 组合价值
axes[0, 1].plot(df['date'], portfolio_value, label='策略组合', linewidth=2)
axes[0, 1].plot(df['date'], buy_hold_value, label='买入持有', linewidth=2, alpha=0.7)
axes[0, 1].set_title('组合价值对比', fontsize=12)
axes[0, 1].set_xlabel('日期')
axes[0, 1].set_ylabel('组合价值 (元)')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 每日收益分布
axes[1, 0].hist(net_returns.dropna(), bins=50, edgecolor='black', alpha=0.7)
axes[1, 0].axvline(x=net_returns.mean(), color='r', linestyle='--', 
                   label=f'均值: {net_returns.mean():.4f}')
axes[1, 0].axvline(x=net_returns.median(), color='g', linestyle='--',
                   label=f'中位数: {net_returns.median():.4f}')
axes[1, 0].set_title('每日收益分布', fontsize=12)
axes[1, 0].set_xlabel('日收益率')
axes[1, 0].set_ylabel('频率')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# 滚动收益
rolling_window = 30
rolling_sharpe = net_returns.rolling(window=rolling_window).mean() / net_returns.rolling(window=rolling_window).std() * np.sqrt(252)
axes[1, 1].plot(df['date'], rolling_sharpe, linewidth=1.5)
axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
axes[1, 1].set_title(f'滚动{rolling_window}天夏普比率', fontsize=12)
axes[1, 1].set_xlabel('日期')
axes[1, 1].set_ylabel('夏普比率')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 6. 性能指标计算

# %%
print("📈 性能指标计算")

# 6.1 计算关键指标
total_return = cumulative_strategy.iloc[-1] - 1
annual_return = (1 + total_return) ** (252 / len(df)) - 1
annual_volatility = net_returns.std() * np.sqrt(252)
sharpe_ratio = annual_return / annual_volatility if annual_volatility != 0 else 0

# 最大回撤
cumulative_max = cumulative_strategy.expanding().max()
drawdown = (cumulative_strategy - cumulative_max) / cumulative_max
max_drawdown = drawdown.min()

# 胜率
win_rate = (net_returns > 0).mean()
profit_factor = net_returns[net_returns > 0].sum() / abs(net_returns[net_returns < 0].sum())

# 6.2 显示性能指标
performance_metrics = {
    '总收益率': f'{total_return:.2%}',
    '年化收益率': f'{annual_return:.2%}',
    '年化波动率': f'{annual_volatility:.2%}',
    '夏普比率': f'{sharpe_ratio:.2f}',
    '最大回撤': f'{max_drawdown:.2%}',
    '胜率': f'{win_rate:.2%}',
    '盈亏比': f'{profit_factor:.2f}',
    '总交易次数': f'{position_changes[position_changes != 0].sum():.0f}',
    '平均持仓周期': f'{len(df) / max(1, position_changes[position_changes != 0].sum()):.1f} 天'
}

print("策略性能指标:")
for metric, value in performance_metrics.items():
    print(f"  {metric}: {value}")

# 6.3 性能指标表格
performance_df = pd.DataFrame(list(performance_metrics.items()), columns=['指标', '值'])
display(performance_df)

# %% [markdown]
# ## 7. 参数优化

# %%
print("⚙️ 参数优化")

# 7.1 定义参数网格
param_grid = [
    {'short_window': 5, 'long_window': 20},
    {'short_window': 10, 'long_window': 30},
    {'short_window': 20, 'long_window': 50},
    {'short_window': 30, 'long_window': 100}
]

print(f"测试参数组合: {len(param_grid)} 个")

# 7.2 参数优化（简化版）
optimization_results = []

for params in param_grid:
    # 创建新策略实例
    test_strategy = MovingAverageCrossover(params)
    test_signals = test_strategy.run(df)
    
    # 计算信号收益（简化评估）
    test_returns = test_signals['signal'].shift(1) * df['returns']
    test_returns = test_returns.fillna(0)
    
    # 计算评估指标
    total_ret = (1 + test_returns).prod() - 1
    sharpe = test_returns.mean() / test_returns.std() * np.sqrt(252) if test_returns.std() != 0 else 0
    
    optimization_results.append({
        'short_window': params['short_window'],
        'long_window': params['long_window'],
        '总收益率': total_ret,
        '夏普比率': sharpe,
        '交易次数': (test_signals['signal'].diff().abs() > 0).sum()
    })

# 7.3 显示优化结果
optimization_df = pd.DataFrame(optimization_results)
print("参数优化结果:")
display(optimization_df)

# 7.4 可视化参数敏感性
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# 总收益率热图
pivot_returns = optimization_df.pivot(index='short_window', columns='long_window', values='总收益率')
im1 = axes[0].imshow(pivot_returns.values, cmap='RdYlGn', aspect='auto')
axes[0].set_title('总收益率热图', fontsize=12)
axes[0].set_xlabel('长期窗口')
axes[0].set_ylabel('短期窗口')
axes[0].set_xticks(range(len(pivot_returns.columns)))
axes[0].set_xticklabels(pivot_returns.columns)
axes[0].set_yticks(range(len(pivot_returns.index)))
axes[0].set_yticklabels(pivot_returns.index)
plt.colorbar(im1, ax=axes[0])

# 夏普比率热图
pivot_sharpe = optimization_df.pivot(index='short_window', columns='long_window', values='夏普比率')
im2 = axes[1].imshow(pivot_sharpe.values, cmap='RdYlGn', aspect='auto')
axes[1].set_title('夏普比率热图', fontsize=12)
axes[1].set_xlabel('长期窗口')
axes[1].set_ylabel('短期窗口')
axes[1].set_xticks(range(len(pivot_sharpe.columns)))
axes[1].set_xticklabels(pivot_sharpe.columns)
axes[1].set_yticks(range(len(pivot_sharpe.index)))
axes[1].set_yticklabels(pivot_sharpe.index)
plt.colorbar(im2, ax=axes[1])

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 8. 稳健性检验

# %%
print("🔍 稳健性检验")

# 8.1 样本外测试
split_ratio = 0.7
split_idx = int(len(df) * split_ratio)

train_data = df.iloc[:split_idx]
test_data = df.iloc[split_idx:]

print(f"训练集: {len(train_data)} 天 ({train_data['date'].min()} 到 {train_data['date'].max()})")
print(f"测试集: {len(test_data)} 天 ({test_data['date'].min()} 到 {test_data['date'].max()})")

# 在训练集上优化参数
print("\n在训练集上优化参数...")
# 简化：使用最佳参数
best_params = optimization_df.loc[optimization_df['夏普比率'].idxmax()]
print(f"最佳参数: 短期窗口={best_params['short_window']}, 长期窗口={best_params['long_window']}")

# 在测试集上测试
test_strategy = MovingAverageCrossover({'short_window': int(best_params['short_window']), 
                                        'long_window': int(best_params['long_window'])})
test_signals = test_strategy.run(test_data)

# 计算测试集表现
test_returns = test_signals['signal'].shift(1) * test_data['returns']
test_returns = test_returns.fillna(0)
test_cumulative = (1 + test_returns).cumprod()
test_total_return = test_cumulative.iloc[-1] - 1

print(f"\n样本外测试结果:")
print(f"  测试集总收益率: {test_total_return:.2%}")
print(f"  训练集最佳夏普: {best_params['夏普比率']:.2f}")

# 8.2 不同市场环境测试
print("\n市场环境分析...")
# 简化：按收益率分位数划分市场环境
df['market_regime'] = pd.qcut(df['returns'], q=3, labels=['下跌', '震荡', '上涨'])

regime_performance = []
for regime in ['下跌', '震荡', '上涨']:
    regime_data = df[df['market_regime'] == regime]
    if len(regime_data) > 0:
        regime_returns = signals_df.loc[regime_data.index, 'signal'].shift(1) * regime_data['returns']
        regime_returns = regime_returns.dropna()
        if len(regime_returns) > 0:
            regime_performance.append({
                '市场环境': regime,
                '天数': len(regime_data),
                '平均日收益': regime_returns.mean(),
                '胜率': (regime_returns > 0).mean(),
                '夏普比率': regime_returns.mean() / regime_returns.std() * np.sqrt(252) if regime_returns.std() != 0 else 0
            })

regime_df = pd.DataFrame(regime_performance)
print("不同市场环境表现:")
display(regime_df)

# %% [markdown]
# ## 9. 结论与建议

# %%
print("📋 结论与建议")

# 9.1 主要发现总结
print("\n## 主要发现")
print("1. **策略表现**: ", end="")
if float(performance_metrics['夏普比率'].strip('f')) > 0.5:
    print("策略表现良好，夏普比率较高")
else:
    print("策略表现一般，有待优化")

print("2. **参数敏感性**: ", end="")
param_range = optimization_df['总收益率'].max() - optimization_df['总收益率'].min()
if param_range > 0.1:
    print("参数对策略影响较大，需要仔细优化")
else:
    print("参数对策略影响相对稳定")

print("3. **稳健性**: ", end="")
if abs(test_total_return - float(performance_metrics['总收益率'].strip('%'))/100) < 0.05:
    print("样本内外表现一致，策略稳健性较好")
else:
    print("样本内外表现有差异，需要进一步验证")

# 9.2 优化建议
print("\n## 优化建议")
suggestions = []

if float(performance_metrics['最大回撤'].strip('%')) < -0.2:
    suggestions.append("最大回撤较大，建议增加止损机制")
else:
    suggestions.append("最大回撤控制在可接受范围")

if float(performance_metrics['交易次数'].split()[0]) > 50:
    suggestions.append("交易频率较高，考虑降低换手率以减少交易成本")
else:
    suggestions.append("交易频率适中")

if regime_df is not None and len(regime_df) > 0:
    weak_regime = regime_df.loc[regime_df['夏普比率'].idxmin(), '市场环境']
    suggestions.append(f"在'{weak_regime}'市场环境下表现较弱，建议针对性优化")

suggestions.append("考虑与其他因子结合，构建复合信号")
suggestions.append("进行更全面的参数优化和稳健性检验")

print("优化建议:")
for i, suggestion in enumerate(suggestions, 1):
    print(f"{i}. {suggestion}")

# 9.3 下一步工作
print("\n## 下一步工作")
next_steps = [
    "1. 扩大参数优化范围，使用更先进的优化算法",
    "2. 增加风险控制模块，包括止损和仓位管理",
    "3. 在模拟盘中进行实时验证",
    "4. 与其他策略进行对比分析",
    "5. 考虑交易成本和市场冲击成本"
]

for step in next_steps:
    print(step)

# %% [markdown]
# ## 10. 保存结果

# %%
print("💾 保存分析结果")

# 创建输出目录
import os
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# 10.1 保存策略信号
signals_df.to_csv(f'{output_dir}/strategy_signals.csv')
print(f"✅ 策略信号已保存到: {output_dir}/strategy_signals.csv")

# 10.2 保存回测结果
backtest_results = pd.DataFrame({
    'date': df['date'],
    'portfolio_value': portfolio_value,
    'strategy_returns': net_returns,
    'cumulative_returns': cumulative_strategy
})
backtest_results.to_csv(f'{output_dir}/backtest_results.csv', index=False)
print(f"✅ 回测结果已保存到: {output_dir}/backtest_results.csv")

# 10.3 保存性能指标
performance_df.to_csv(f'{output_dir}/performance_metrics.csv', index=False)
print(f"✅ 性能指标已保存到: {output_dir}/performance_metrics.csv")

# 10.4 保存优化结果
optimization_df.to_csv(f'{output_dir}/parameter_optimization.csv', index=False)
print(f"✅ 参数优化结果已保存到: {output_dir}/parameter_optimization.csv")

# 10.5 保存分析报告
report = {
    '分析日期': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
    '数据范围': f"{df['date'].min()} 到 {df['date'].max()}",
    '总交易日': len(df),
    '策略名称': '移动平均交叉策略',
    '最佳参数': f"short_window={best_params['short_window']}, long_window={best_params['long_window']}",
    '总收益率': performance_metrics['总收益率'],
    '夏普比率': performance_metrics['夏普比率'],
    '最大回撤': performance_metrics['最大回撤'],
    '样本外收益率': f'{test_total_return:.2%}'
}

import json
with open(f'{output_dir}/strategy_analysis_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

print(f"✅ 分析报告已保存到: {output_dir}/strategy_analysis_report.json")
print("\n🎉 策略分析完成！")

# %% [markdown]
# ---
# 
# **备注**: 
# - 本模板为通用策略研究模板，请根据实际策略调整计算逻辑
# - 建议进行充分的样本外测试和稳健性检验
# - 考虑实际交易成本和市场流动性
# - 定期监控策略衰减情况
# - 结合风险管理模块使用