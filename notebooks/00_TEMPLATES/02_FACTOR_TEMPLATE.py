---
standard_type: 代码模板
applicable_scope: 因子开发
compliance_level: 初始标准
parent_document: ../README.md
implementation_status: 可用
owner: 研究团队
version: 1.0.0
module_id: TEMPLATE_FACTOR
created_date: 2026-03-31
last_updated: 2026-04-03
description: 因子开发模板 - 新因子计算、IC分析、回测验证
---
"""
因子开发模板

功能：新因子计算、IC分析、回测验证
版本：v1.0
创建日期：2026-03-31
"""

# %% [markdown]
# # 因子开发与分析
# 
# > **项目**: ZephyrAlpha v5.1
# > **作者**: [姓名/团队]
# > **创建日期**: YYYY-MM-DD
# > **更新日期**: YYYY-MM-DD
# > **状态**: ⚪ 进行中 | ✅ 已完成 | 📊 结果已生成
# > **目标**: 开发新的Alpha因子，进行IC分析、分组回测和性能验证

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

# 尝试导入因子计算模块
try:
    from src.modules.factor_calculator import FactorCalculator
    print("✅ 成功导入因子计算模块")
except ImportError:
    print("⚠️ 无法导入因子计算模块，使用替代实现")
    class FactorCalculator:
        """简化版因子计算器"""
        @staticmethod
        def calculate_momentum(data, period=20):
            """计算动量因子"""
            return data['close'].pct_change(period)
        
        @staticmethod
        def calculate_volume_ratio(data, short_period=5, long_period=20):
            """计算量比因子"""
            return data['volume'].rolling(short_period).mean() / data['volume'].rolling(long_period).mean()

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
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    data_list = []
    for symbol in symbols:
        base_price = np.random.uniform(50, 500)
        returns = np.random.normal(0.0005, 0.02, 500)
        prices = base_price * np.exp(np.cumsum(returns))
        
        for i, date in enumerate(dates):
            data_list.append({
                'date': date,
                'symbol': symbol,
                'open': prices[i] * np.random.uniform(0.99, 1.01),
                'high': prices[i] * np.random.uniform(1.01, 1.03),
                'low': prices[i] * np.random.uniform(0.97, 0.99),
                'close': prices[i],
                'volume': np.random.randint(1000000, 10000000),
                'market_cap': np.random.uniform(1e9, 1e12)
            })
    
    df = pd.DataFrame(data_list)

# 数据预处理
print("\n🔧 数据预处理")

# 确保日期排序
df = df.sort_values(['symbol', 'date'])

# 添加基本衍生特征
df['returns'] = df.groupby('symbol')['close'].pct_change()
df['log_returns'] = np.log(df['close'] / df.groupby('symbol')['close'].shift(1))

print(f"📊 数据形状: {df.shape}")
print(f"📅 时间范围: {df['date'].min()} 到 {df['date'].max()}")
print(f"📈 股票数量: {df['symbol'].nunique()}")
print(f"📅 总交易日: {df['date'].nunique()}")

# 查看数据
print("\n数据示例:")
display(df.head())

# %% [markdown]
# ## 3. 因子定义与计算

# %%
print("🧮 因子定义与计算")

# 3.1 定义新因子
def calculate_new_factor(data, params=None):
    """
    计算新因子
    
    参数:
        data: 包含价格和交易量数据的DataFrame
        params: 因子参数字典
        
    返回:
        Series: 因子值
    """
    if params is None:
        params = {
            'momentum_period': 20,
            'volume_period': 10,
            'volatility_period': 20
        }
    
    # 示例因子：动量与量比结合
    momentum = data['close'].pct_change(params['momentum_period'])
    volume_ratio = data['volume'].rolling(params['volume_period']).mean() / \
                   data['volume'].rolling(params['volume_period'] * 2).mean()
    volatility = data['returns'].rolling(params['volatility_period']).std()
    
    # 因子公式：动量 * 量比 / 波动率
    # 避免除以零
    volatility = volatility.replace(0, np.nan)
    factor = momentum * volume_ratio / volatility
    
    return factor

# 3.2 计算因子值
print("计算因子值...")

# 为每个股票计算因子
factor_values = []
for symbol, group in df.groupby('symbol'):
    group = group.copy()
    group['factor'] = calculate_new_factor(group)
    factor_values.append(group[['date', 'symbol', 'factor']])

# 合并结果
factor_df = pd.concat(factor_values, ignore_index=True)

# 转换为宽格式（股票×日期）
factor_pivot = factor_df.pivot(index='date', columns='symbol', values='factor')

print(f"✅ 因子计算完成")
print(f"因子数据形状: {factor_pivot.shape}")
print(f"因子覆盖日期: {factor_pivot.index.min()} 到 {factor_pivot.index.max()}")

# 显示因子统计
print("\n因子描述性统计:")
display(factor_pivot.describe())

# %% [markdown]
# ## 4. 因子数据质量检查

# %%
print("🔍 因子数据质量检查")

# 4.1 缺失值分析
missing_by_date = factor_pivot.isnull().mean(axis=1)
missing_by_stock = factor_pivot.isnull().mean(axis=0)

print(f"1. 整体缺失率: {factor_pivot.isnull().mean().mean():.2%}")

# 4.2 缺失值可视化
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 按日期缺失率
axes[0].plot(missing_by_date.index, missing_by_date.values * 100, linewidth=1)
axes[0].set_title('按日期缺失率 (%)', fontsize=12)
axes[0].set_xlabel('日期')
axes[0].set_ylabel('缺失率 (%)')
axes[0].grid(True, alpha=0.3)
axes[0].axhline(y=missing_by_date.mean() * 100, color='r', linestyle='--', 
                label=f'平均: {missing_by_date.mean()*100:.1f}%')

# 按股票缺失率
sorted_stocks = missing_by_stock.sort_values(ascending=False)
axes[1].bar(range(len(sorted_stocks)), sorted_stocks.values * 100)
axes[1].set_title('按股票缺失率 (%)', fontsize=12)
axes[1].set_xlabel('股票索引')
axes[1].set_ylabel('缺失率 (%)')
axes[1].grid(True, alpha=0.3, axis='y')
axes[1].axhline(y=missing_by_stock.mean() * 100, color='r', linestyle='--',
                label=f'平均: {missing_by_stock.mean()*100:.1f}%')

plt.tight_layout()
plt.show()

# 4.3 因子分布检查
print("\n2. 因子分布检查:")

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# 因子值分布
factor_flat = factor_pivot.values.flatten()
factor_flat = factor_flat[~np.isnan(factor_flat)]

axes[0].hist(factor_flat, bins=50, edgecolor='black', alpha=0.7)
axes[0].set_title('因子值分布', fontsize=12)
axes[0].set_xlabel('因子值')
axes[0].set_ylabel('频率')
axes[0].axvline(x=np.mean(factor_flat), color='r', linestyle='--', 
                label=f'均值: {np.mean(factor_flat):.4f}')
axes[0].axvline(x=np.median(factor_flat), color='g', linestyle='--',
                label=f'中位数: {np.median(factor_flat):.4f}')
axes[0].legend()

# 因子值随时间变化
mean_factor_by_date = factor_pivot.mean(axis=1)
axes[1].plot(mean_factor_by_date.index, mean_factor_by_date.values, linewidth=1)
axes[1].set_title('平均因子值随时间变化', fontsize=12)
axes[1].set_xlabel('日期')
axes[1].set_ylabel('平均因子值')
axes[1].grid(True, alpha=0.3)

# 因子值相关性
if len(factor_pivot.columns) > 1:
    factor_corr = factor_pivot.corr()
    mask = np.triu(np.ones_like(factor_corr, dtype=bool))
    
    im = axes[2].imshow(factor_corr, cmap='coolwarm', vmin=-1, vmax=1)
    axes[2].set_title('因子值相关性', fontsize=12)
    axes[2].set_xlabel('股票')
    axes[2].set_ylabel('股票')
    plt.colorbar(im, ax=axes[2])
else:
    axes[2].text(0.5, 0.5, '股票数量不足\n无法计算相关性', 
                 ha='center', va='center', fontsize=12)
    axes[2].set_title('因子值相关性', fontsize=12)

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 5. IC分析 (信息系数分析)

# %%
print("📈 IC分析 (信息系数分析)")

# 5.1 准备收益率数据
# 计算未来N期收益率
lookforward_periods = [1, 5, 20]  # 1天、5天、20天
returns_data = {}

for period in lookforward_periods:
    returns = df.pivot(index='date', columns='symbol', values='close').pct_change(period).shift(-period)
    returns_data[f'ret_{period}d'] = returns

print(f"计算未来收益率: {lookforward_periods} 天")

# 5.2 计算IC
ic_results = {}

for period in lookforward_periods:
    returns = returns_data[f'ret_{period}d']
    
    # 对齐因子和收益率数据
    common_dates = factor_pivot.index.intersection(returns.index)
    factor_aligned = factor_pivot.loc[common_dates]
    returns_aligned = returns.loc[common_dates]
    
    # 计算每日IC (Rank IC)
    daily_ic = []
    dates_ic = []
    
    for date in common_dates:
        factor_today = factor_aligned.loc[date]
        returns_future = returns_aligned.loc[date]
        
        # 对齐数据（删除NaN）
        aligned_data = pd.DataFrame({
            'factor': factor_today,
            'return': returns_future
        }).dropna()
        
        if len(aligned_data) > 5:  # 至少需要5个数据点
            # 计算Rank IC (Spearman相关系数)
            ic = aligned_data['factor'].corr(aligned_data['return'], method='spearman')
            daily_ic.append(ic)
            dates_ic.append(date)
    
    ic_series = pd.Series(daily_ic, index=dates_ic)
    ic_results[f'IC_{period}d'] = ic_series
    
    print(f"IC_{period}d: 均值={ic_series.mean():.4f}, 标准差={ic_series.std():.4f}, "
          f"IR={ic_series.mean()/ic_series.std():.4f}")

# 5.3 IC可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# IC时间序列
for i, period in enumerate(lookforward_periods):
    ic_series = ic_results[f'IC_{period}d']
    ax = axes[i // 2, i % 2]
    
    ax.plot(ic_series.index, ic_series.values, linewidth=1, alpha=0.7)
    ax.axhline(y=ic_series.mean(), color='r', linestyle='--', 
               label=f'均值: {ic_series.mean():.4f}')
    ax.fill_between(ic_series.index, 
                    ic_series.mean() - ic_series.std(),
                    ic_series.mean() + ic_series.std(),
                    alpha=0.2, color='gray', label='±1标准差')
    
    ax.set_title(f'IC_{period}d 时间序列', fontsize=12)
    ax.set_xlabel('日期')
    ax.set_ylabel('IC值')
    ax.grid(True, alpha=0.3)
    ax.legend()

# IC分布
ax = axes[1, 1]
for period in lookforward_periods:
    ic_series = ic_results[f'IC_{period}d']
    ax.hist(ic_series.dropna(), bins=30, alpha=0.5, label=f'IC_{period}d',
            density=True)
    
ax.set_title('IC分布对比', fontsize=12)
ax.set_xlabel('IC值')
ax.set_ylabel('密度')
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.show()

# 5.4 IC统计表
print("\nIC统计摘要:")
ic_stats = []
for period in lookforward_periods:
    ic_series = ic_results[f'IC_{period}d']
    ic_stats.append({
        '周期(天)': period,
        'IC均值': f'{ic_series.mean():.4f}',
        'IC标准差': f'{ic_series.std():.4f}',
        '信息比率(IR)': f'{ic_series.mean()/ic_series.std():.4f}',
        'IC>0比例': f'{(ic_series > 0).mean():.2%}',
        't统计量': f'{ic_series.mean()/ic_series.std()*np.sqrt(len(ic_series)):.2f}',
        '有效天数': len(ic_series)
    })

ic_stats_df = pd.DataFrame(ic_stats)
display(ic_stats_df)

# %% [markdown]
# ## 6. 分组回测分析

# %%
print("📊 分组回测分析")

# 6.1 准备分组回测数据
period = 20  # 使用20天收益率进行分析
returns_future = returns_data[f'ret_{period}d']

# 对齐数据
common_dates = factor_pivot.index.intersection(returns_future.index)
factor_aligned = factor_pivot.loc[common_dates]
returns_aligned = returns_future.loc[common_dates]

print(f"分组回测数据: {len(common_dates)} 个交易日")

# 6.2 执行分组回测
group_returns = []
group_stats = []

for date in common_dates:
    factor_today = factor_aligned.loc[date]
    returns_next = returns_aligned.loc[date]
    
    # 对齐数据
    aligned = pd.DataFrame({
        'factor': factor_today,
        'return': returns_next
    }).dropna()
    
    if len(aligned) < 10:  # 至少需要10只股票
        continue
    
    # 按因子值分组 (十分位)
    aligned['group'] = pd.qcut(aligned['factor'], q=10, labels=False, duplicates='drop')
    
    # 计算每组平均收益率
    group_mean = aligned.groupby('group')['return'].mean()
    group_returns.append(group_mean)
    
    # 记录多空收益 (第10组 - 第1组)
    if len(group_mean) >= 10:
        long_short_return = group_mean.iloc[-1] - group_mean.iloc[0]  # 第10组 - 第1组
        group_stats.append({
            'date': date,
            'long_short': long_short_return,
            'high_group': group_mean.iloc[-1],  # 因子值最高组
            'low_group': group_mean.iloc[0]     # 因子值最低组
        })

# 合并结果
group_returns_df = pd.DataFrame(group_returns, index=common_dates[:len(group_returns)])
group_stats_df = pd.DataFrame(group_stats)

print(f"有效回测天数: {len(group_returns_df)}")

# 6.3 分组收益率可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 各组平均收益率
mean_group_returns = group_returns_df.mean()
axes[0, 0].bar(range(len(mean_group_returns)), mean_group_returns.values)
axes[0, 0].set_title('各组平均收益率', fontsize=12)
axes[0, 0].set_xlabel('分组 (1=因子值最低, 10=因子值最高)')
axes[0, 0].set_ylabel(f'平均{period}天收益率')
axes[0, 0].grid(True, alpha=0.3, axis='y')

# 添加收益率数值标签
for i, val in enumerate(mean_group_returns.values):
    axes[0, 0].text(i, val, f'{val:.3f}', ha='center', va='bottom' if val >= 0 else 'top')

# 多空收益时间序列
if not group_stats_df.empty:
    axes[0, 1].plot(group_stats_df['date'], group_stats_df['long_short'].cumsum(), linewidth=2)
    axes[0, 1].set_title('多空策略累积收益', fontsize=12)
    axes[0, 1].set_xlabel('日期')
    axes[0, 1].set_ylabel('累积收益')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 计算多空策略表现
    ls_returns = group_stats_df['long_short']
    ls_cumulative = (1 + ls_returns).cumprod() - 1
    total_return = ls_cumulative.iloc[-1] if len(ls_cumulative) > 0 else 0
    axes[0, 1].text(0.05, 0.95, f'总收益: {total_return:.2%}', 
                    transform=axes[0, 1].transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 收益率分布
group_colors = plt.cm.viridis(np.linspace(0, 1, 10))
for group in range(min(10, len(mean_group_returns))):
    axes[1, 0].hist(group_returns_df[group].dropna(), bins=20, alpha=0.5, 
                    color=group_colors[group], label=f'组{group+1}', density=True)

axes[1, 0].set_title('各组收益率分布', fontsize=12)
axes[1, 0].set_xlabel(f'{period}天收益率')
axes[1, 0].set_ylabel('密度')
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].legend(loc='upper right', fontsize=8)

# 月度IC热图
if not group_stats_df.empty:
    group_stats_df['year_month'] = group_stats_df['date'].dt.to_period('M')
    monthly_ls = group_stats_df.groupby('year_month')['long_short'].mean()
    
    # 创建月度热图数据
    monthly_ls_df = monthly_ls.unstack() if hasattr(monthly_ls, 'unstack') else monthly_ls.to_frame().T
    im = axes[1, 1].imshow(monthly_ls_df.values if len(monthly_ls_df.shape) > 1 else [monthly_ls_df.values], 
                          cmap='RdYlGn', aspect='auto')
    axes[1, 1].set_title('月度多空收益热图', fontsize=12)
    axes[1, 1].set_xlabel('月份')
    axes[1, 1].set_ylabel('')
    plt.colorbar(im, ax=axes[1, 1])
else:
    axes[1, 1].text(0.5, 0.5, '数据不足\n无法生成热图', 
                    ha='center', va='center', fontsize=12)
    axes[1, 1].set_title('月度多空收益热图', fontsize=12)

plt.tight_layout()
plt.show()

# 6.4 分组回测统计
print("\n分组回测统计:")
if not group_stats_df.empty:
    ls_returns = group_stats_df['long_short']
    
    stats = {
        '总天数': len(ls_returns),
        '多空平均日收益': f'{ls_returns.mean():.4%}',
        '多空收益标准差': f'{ls_returns.std():.4%}',
        '夏普比率(年化)': f'{ls_returns.mean()/ls_returns.std() * np.sqrt(252):.4f}',
        '胜率': f'{(ls_returns > 0).mean():.2%}',
        '最大单日收益': f'{ls_returns.max():.4%}',
        '最大单日损失': f'{ls_returns.min():.4%}',
        '收益偏度': f'{ls_returns.skew():.4f}',
        '收益峰度': f'{ls_returns.kurtosis():.4f}'
    }
    
    stats_df = pd.DataFrame(list(stats.items()), columns=['指标', '值'])
    display(stats_df)
else:
    print("分组回测数据不足")

# %% [markdown]
# ## 7. 因子稳定性检验

# %%
print("📅 因子稳定性检验")

# 7.1 滚动IC分析
window_size = 63  # 3个月滚动窗口
rolling_ic = {}

for period in lookforward_periods:
    ic_series = ic_results[f'IC_{period}d']
    rolling_mean = ic_series.rolling(window=window_size, min_periods=20).mean()
    rolling_std = ic_series.rolling(window=window_size, min_periods=20).std()
    rolling_ir = rolling_mean / rolling_std
    
    rolling_ic[f'IC_{period}d'] = {
        'mean': rolling_mean,
        'std': rolling_std,
        'ir': rolling_ir
    }

# 7.2 稳定性可视化
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

colors = plt.cm.Set1(np.linspace(0, 1, len(lookforward_periods)))

for idx, period in enumerate(lookforward_periods):
    rolling_data = rolling_ic[f'IC_{period}d']
    
    # 滚动IC均值
    axes[0].plot(rolling_data['mean'].index, rolling_data['mean'].values, 
                 color=colors[idx], linewidth=1.5, label=f'IC_{period}d')
    axes[0].set_title(f'滚动{window_size}天IC均值', fontsize=12)
    axes[0].set_ylabel('IC均值')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc='upper left')
    
    # 滚动IC标准差
    axes[1].plot(rolling_data['std'].index, rolling_data['std'].values,
                 color=colors[idx], linewidth=1.5)
    axes[1].set_title(f'滚动{window_size}天IC标准差', fontsize=12)
    axes[1].set_ylabel('IC标准差')
    axes[1].grid(True, alpha=0.3)
    
    # 滚动信息比率
    axes[2].plot(rolling_data['ir'].index, rolling_data['ir'].values,
                 color=colors[idx], linewidth=1.5)
    axes[2].set_title(f'滚动{window_size}天信息比率', fontsize=12)
    axes[2].set_xlabel('日期')
    axes[2].set_ylabel('信息比率')
    axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 7.3 年度IC分析
print("\n年度IC分析:")

if not ic_results:
    print("IC数据不足")
else:
    # 使用主要周期的IC
    main_ic = ic_results[f'IC_{lookforward_periods[0]}d']
    
    # 提取年份
    main_ic_df = main_ic.reset_index()
    main_ic_df.columns = ['date', 'IC']
    main_ic_df['year'] = main_ic_df['date'].dt.year
    
    # 年度统计
    yearly_stats = main_ic_df.groupby('year')['IC'].agg([
        ('IC均值', 'mean'),
        ('IC标准差', 'std'),
        ('IC>0比例', lambda x: (x > 0).mean()),
        ('天数', 'count')
    ]).round(4)
    
    yearly_stats['信息比率'] = yearly_stats['IC均值'] / yearly_stats['IC标准差']
    
    display(yearly_stats)

# %% [markdown]
# ## 8. 因子组合与优化建议

# %%
print("💡 因子组合与优化建议")

# 8.1 因子评价
print("\n## 因子评价")

if not ic_stats_df.empty:
    main_ic_row = ic_stats_df.iloc[0]  # 使用第一个周期
    
    evaluation = {
        '预测能力': '强' if float(main_ic_row['IC均值']) > 0.05 else '中等' if float(main_ic_row['IC均值']) > 0.02 else '弱',
        '稳定性': '高' if float(main_ic_row['IC>0比例'].strip('%')) > 60 else '中等' if float(main_ic_row['IC>0比例'].strip('%')) > 55 else '低',
        '显著性': '显著' if float(main_ic_row['t统计量']) > 2 else '边缘显著' if float(main_ic_row['t统计量']) > 1.5 else '不显著',
        '实用性': '高' if float(main_ic_row['信息比率']) > 0.5 else '中等' if float(main_ic_row['信息比率']) > 0.2 else '低'
    }
    
    eval_df = pd.DataFrame(list(evaluation.items()), columns=['维度', '评价'])
    display(eval_df)

# 8.2 优化建议
print("\n## 优化建议")

suggestions = []

# 基于IC分析的建议
if not ic_stats_df.empty:
    ic_mean = float(ic_stats_df.iloc[0]['IC均值'])
    ic_ir = float(ic_stats_df.iloc[0]['信息比率'])
    
    if ic_mean < 0.02:
        suggestions.append("IC值较低，建议优化因子公式或参数")
    elif ic_mean > 0.05:
        suggestions.append("IC值较高，因子预测能力强")
    
    if ic_ir < 0.3:
        suggestions.append("信息比率偏低，建议降低因子波动或提高稳定性")
    else:
        suggestions.append("信息比率良好，因子具有较好的风险调整后收益")

# 基于分组回测的建议
if not group_stats_df.empty and 'long_short' in group_stats_df.columns:
    ls_returns = group_stats_df['long_short']
    win_rate = (ls_returns > 0).mean()
    
    if win_rate < 0.55:
        suggestions.append(f"胜率较低 ({win_rate:.1%})，建议增加过滤条件或优化分组方法")
    else:
        suggestions.append(f"胜率良好 ({win_rate:.1%})")

# 通用建议
suggestions.append("考虑与其他因子的相关性，避免多重共线性")
suggestions.append("进行样本外测试验证因子稳定性")
suggestions.append("优化因子计算频率和换手率")

print("优化建议:")
for i, suggestion in enumerate(suggestions, 1):
    print(f"{i}. {suggestion}")

# 8.3 下一步工作
print("\n## 下一步工作")
next_steps = [
    "1. 进行样本外测试 (使用最近3个月数据)",
    "2. 与其他因子结合，构建复合因子",
    "3. 优化参数，进行参数敏感性分析",
    "4. 考虑换手率和交易成本",
    "5. 在模拟盘中进行验证"
]

for step in next_steps:
    print(step)

# %% [markdown]
# ## 9. 保存结果

# %%
print("💾 保存分析结果")

# 创建输出目录
import os
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# 9.1 保存因子数据
factor_pivot.to_csv(f'{output_dir}/factor_values.csv')
print(f"✅ 因子数据已保存到: {output_dir}/factor_values.csv")

# 9.2 保存IC分析结果
ic_results_df = pd.DataFrame()
for period in lookforward_periods:
    if f'IC_{period}d' in ic_results:
        ic_results_df[f'IC_{period}d'] = ic_results[f'IC_{period}d']

if not ic_results_df.empty:
    ic_results_df.to_csv(f'{output_dir}/ic_analysis.csv')
    print(f"✅ IC分析结果已保存到: {output_dir}/ic_analysis.csv")

# 9.3 保存分组回测结果
if not group_stats_df.empty:
    group_stats_df.to_csv(f'{output_dir}/group_backtest.csv', index=False)
    print(f"✅ 分组回测结果已保存到: {output_dir}/group_backtest.csv")

# 9.4 保存分析报告
report = {
    '分析日期': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
    '数据范围': f"{df['date'].min()} 到 {df['date'].max()}",
    '股票数量': df['symbol'].nunique(),
    '总交易日': df['date'].nunique(),
    '因子覆盖日期': len(factor_pivot),
    'IC分析周期': str(lookforward_periods)
}

if not ic_stats_df.empty:
    report.update(ic_stats_df.iloc[0].to_dict())

import json
with open(f'{output_dir}/factor_analysis_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

print(f"✅ 分析报告已保存到: {output_dir}/factor_analysis_report.json")
print("\n🎉 因子分析完成！")

# %% [markdown]
# ---
# 
# **备注**: 
# - 本模板为通用因子开发模板，请根据实际因子调整计算逻辑
# - 建议进行充分的样本外测试
# - 考虑实际交易成本和换手率
# - 定期监控因子衰减情况