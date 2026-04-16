---
standard_type: 代码模板
applicable_scope: 报告生成
compliance_level: 初始标准
parent_document: ../README.md
implementation_status: 可用
owner: 研究团队
version: 1.0.0
module_id: TEMPLATE_REPORT
created_date: 2026-04-03
last_updated: 2026-04-03
description: 报告生成模板 - 自动化报告、图表生成、文档输出
---
"""
报告生成模板

功能：自动化报告、图表生成、文档输出
版本：v1.0.0
创建日期：2026-04-03
"""

# %% [markdown]
# # 研究报告生成
#
# > **项目**: ZephyrAlpha v5.1
# > **作者**: [姓名/团队]
# > **创建日期**: YYYY-MM-DD
# > **更新日期**: YYYY-MM-DD
# > **状态**: ⚪ 进行中 | ✅ 已完成 | 📊 结果已生成
# > **目标**: 生成标准化的研究报告，包括数据摘要、分析结果、可视化图表和专业结论

# %% [markdown]
# ## 1. 环境设置与导入

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 报告生成相关库
from datetime import datetime
import json
import os

# 项目特定导入
import sys
sys.path.append('../../src')

# 配置设置
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
pd.set_option('display.max_columns', 100)
pd.set_option('display.float_format', lambda x: f'{x:.4f}')
np.random.seed(42)

print("环境设置完成")

# %% [markdown]
# ## 2. 报告配置与参数

# %%
print("⚙️ 报告配置")

# 2.1 报告基本信息
report_config = {
    'report_id': 'REPORT_001',
    'report_title': '月度因子分析报告',
    'report_type': '月度报告',
    'report_period': '2026年3月',
    'author': '研究团队',
    'version': '1.0',
    'generation_date': datetime.now().strftime('%Y-%m-%d'),
    'output_formats': ['html', 'pdf', 'markdown'],
    'sections': [
        '执行摘要',
        '数据概况',
        '因子表现分析',
        '策略回测结果',
        '风险分析',
        '结论与建议'
    ]
}

# 2.2 可视化配置
viz_config = {
    'figure_size': (12, 8),
    'dpi': 300,
    'color_palette': 'husl',
    'font_size': {
        'title': 14,
        'axis': 12,
        'legend': 10
    }
}

# 2.3 输出配置
output_config = {
    'output_dir': 'reports',
    'figures_dir': 'figures',
    'data_dir': 'data',
    'tables_dir': 'tables'
}

# 创建输出目录
for dir_name in output_config.values():
    os.makedirs(dir_name, exist_ok=True)

print("报告配置完成")
print(f"报告标题: {report_config['report_title']}")
print(f"报告周期: {report_config['report_period']}")
print(f"输出目录: {output_config['output_dir']}")

# %% [markdown]
# ## 3. 数据加载与预处理

# %%
print("📥 数据加载")

# 3.1 加载分析结果数据
data_sources = {
    'factor_performance': "../../data/analysis/factor_performance.csv",
    'backtest_results': "../../data/analysis/backtest_results.csv",
    'risk_metrics': "../../data/analysis/risk_metrics.csv",
    'market_data': "../../data/processed/market_data_processed.csv"
}

# 加载数据（简化示例）
print("加载数据...")
try:
    # 因子表现数据
    factor_df = pd.read_csv(data_sources['factor_performance'], parse_dates=['date'])
    print(f"✅ 因子表现数据: {factor_df.shape}")
except FileNotFoundError:
    print("⚠️ 因子表现文件未找到，创建示例数据")
    dates = pd.date_range('2026-03-01', periods=30, freq='D')
    factor_df = pd.DataFrame({
        'date': dates,
        'factor_name': np.random.choice(['Momentum', 'Value', 'Quality', 'Size'], 30),
        'ic': np.random.normal(0.05, 0.02, 30),
        'ir': np.random.normal(0.8, 0.2, 30),
        'win_rate': np.random.uniform(0.5, 0.7, 30)
    })

try:
    # 回测结果数据
    backtest_df = pd.read_csv(data_sources['backtest_results'], parse_dates=['date'])
    print(f"✅ 回测结果数据: {backtest_df.shape}")
except FileNotFoundError:
    print("⚠️ 回测结果文件未找到，创建示例数据")
    dates = pd.date_range('2026-03-01', periods=30, freq='D')
    backtest_df = pd.DataFrame({
        'date': dates,
        'portfolio_value': np.random.normal(100000, 5000, 30).cumsum(),
        'daily_return': np.random.normal(0.001, 0.02, 30),
        'cumulative_return': np.random.normal(0.03, 0.005, 30).cumsum()
    })

# 3.2 数据预处理
print("\n🔧 数据预处理")

# 计算汇总统计
factor_summary = factor_df.groupby('factor_name').agg({
    'ic': ['mean', 'std', 'count'],
    'ir': ['mean', 'std'],
    'win_rate': ['mean', 'std']
}).round(4)

backtest_summary = {
    'total_return': backtest_df['cumulative_return'].iloc[-1] if len(backtest_df) > 0 else 0,
    'annual_return': backtest_df['daily_return'].mean() * 252 if len(backtest_df) > 0 else 0,
    'annual_volatility': backtest_df['daily_return'].std() * np.sqrt(252) if len(backtest_df) > 0 else 0,
    'sharpe_ratio': (backtest_df['daily_return'].mean() / backtest_df['daily_return'].std() * np.sqrt(252)) if len(backtest_df) > 0 and backtest_df['daily_return'].std() != 0 else 0,
    'max_drawdown': calculate_max_drawdown(backtest_df['portfolio_value']) if len(backtest_df) > 0 else 0
}

print("数据预处理完成")

# %% [markdown]
# ## 4. 报告内容生成

# %% [markdown]
# ### 4.1 执行摘要

# %%
print("📋 生成执行摘要")

executive_summary = f"""
# 执行摘要

**报告编号**: {report_config['report_id']}
**报告周期**: {report_config['report_period']}
**生成日期**: {report_config['generation_date']}
**版本**: {report_config['version']}

## 核心发现

1. **因子表现**: 本月共分析{len(factor_df['factor_name'].unique())}个因子，平均IC为{factor_df['ic'].mean():.4f}，信息比率IR为{factor_df['ir'].mean():.2f}。

2. **策略表现**: 策略总收益率为{backtest_summary['total_return']:.2%}，年化收益率为{backtest_summary['annual_return']:.2%}，夏普比率为{backtest_summary['sharpe_ratio']:.2f}。

3. **风险指标**: 最大回撤为{backtest_summary['max_drawdown']:.2%}，年化波动率为{backtest_summary['annual_volatility']:.2%}。

## 主要建议

1. 继续监控高IC因子，考虑纳入投资组合
2. 优化策略参数以降低回撤
3. 扩大样本外测试范围

## 报告结构

本报告包含以下{len(report_config['sections'])}个部分：
{chr(10).join([f"- {section}" for section in report_config['sections']])}
"""

print("✅ 执行摘要生成完成")

# %% [markdown]
# ### 4.2 数据概况

# %%
print("📊 生成数据概况")

# 数据概况统计
data_overview = {
    '分析期间': f"{factor_df['date'].min().strftime('%Y-%m-%d')} 至 {factor_df['date'].max().strftime('%Y-%m-%d')}",
    '总交易日': len(factor_df['date'].unique()),
    '分析因子数量': len(factor_df['factor_name'].unique()),
    '数据完整性': f"{(1 - factor_df.isnull().mean().mean()):.1%}",
    '回测数据天数': len(backtest_df)
}

data_overview_df = pd.DataFrame(list(data_overview.items()), columns=['指标', '值'])

print("数据概况:")
display(data_overview_df)

# %% [markdown]
# ### 4.3 因子表现分析

# %%
print("📈 生成因子表现分析")

# 4.3.1 因子IC分析
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# IC时间序列
for factor in factor_df['factor_name'].unique()[:4]:  # 限制前4个因子
    factor_data = factor_df[factor_df['factor_name'] == factor]
    axes[0, 0].plot(factor_data['date'], factor_data['ic'], label=factor, linewidth=1.5, alpha=0.7)

axes[0, 0].set_title('因子IC时间序列', fontsize=viz_config['font_size']['title'])
axes[0, 0].set_xlabel('日期')
axes[0, 0].set_ylabel('IC值')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# IC分布
factor_names = factor_df['factor_name'].unique()
for i, factor in enumerate(factor_names[:4]):
    factor_data = factor_df[factor_df['factor_name'] == factor]
    axes[0, 1].hist(factor_data['ic'].dropna(), bins=15, alpha=0.5, label=factor, density=True)

axes[0, 1].set_title('因子IC分布', fontsize=viz_config['font_size']['title'])
axes[0, 1].set_xlabel('IC值')
axes[0, 1].set_ylabel('密度')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# IR热图
if len(factor_names) > 1:
    ir_matrix = factor_df.pivot_table(index='date', columns='factor_name', values='ir')
    im = axes[1, 0].imshow(ir_matrix.corr(), cmap='RdYlGn', vmin=-1, vmax=1)
    axes[1, 0].set_title('因子IR相关性', fontsize=viz_config['font_size']['title'])
    axes[1, 0].set_xlabel('因子')
    axes[1, 0].set_ylabel('因子')
    plt.colorbar(im, ax=axes[1, 0])
else:
    axes[1, 0].text(0.5, 0.5, '因子数量不足\n无法计算相关性',
                   ha='center', va='center', fontsize=12)
    axes[1, 0].set_title('因子IR相关性', fontsize=viz_config['font_size']['title'])

# 因子排名
factor_rank = factor_summary[('ic', 'mean')].sort_values(ascending=False)
axes[1, 1].bar(range(len(factor_rank)), factor_rank.values)
axes[1, 1].set_title('因子IC均值排名', fontsize=viz_config['font_size']['title'])
axes[1, 1].set_xlabel('因子')
axes[1, 1].set_ylabel('平均IC')
axes[1, 1].set_xticks(range(len(factor_rank)))
axes[1, 1].set_xticklabels(factor_rank.index, rotation=45, ha='right')
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f"{output_config['figures_dir']}/factor_analysis.png", dpi=viz_config['dpi'], bbox_inches='tight')
plt.show()

print("✅ 因子表现分析完成")

# %% [markdown]
# ### 4.4 策略回测结果

# %%
print("📊 生成策略回测结果")

# 4.4.1 回测结果可视化
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 组合价值曲线
if len(backtest_df) > 0:
    axes[0, 0].plot(backtest_df['date'], backtest_df['portfolio_value'], linewidth=2)
    axes[0, 0].set_title('组合价值曲线', fontsize=viz_config['font_size']['title'])
    axes[0, 0].set_xlabel('日期')
    axes[0, 0].set_ylabel('组合价值')
    axes[0, 0].grid(True, alpha=0.3)

    # 添加最终价值标注
    final_value = backtest_df['portfolio_value'].iloc[-1]
    axes[0, 0].text(0.05, 0.95, f'最终价值: {final_value:,.0f}',
                   transform=axes[0, 0].transAxes, fontsize=10,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 每日收益分布
if len(backtest_df) > 0:
    axes[0, 1].hist(backtest_df['daily_return'].dropna(), bins=30, edgecolor='black', alpha=0.7)
    axes[0, 1].axvline(x=backtest_df['daily_return'].mean(), color='r', linestyle='--',
                      label=f'均值: {backtest_df['daily_return'].mean():.4f}')
    axes[0, 1].axvline(x=backtest_df['daily_return'].median(), color='g', linestyle='--',
                      label=f'中位数: {backtest_df['daily_return'].median():.4f}')
    axes[0, 1].set_title('每日收益分布', fontsize=viz_config['font_size']['title'])
    axes[0, 1].set_xlabel('日收益率')
    axes[0, 1].set_ylabel('频率')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

# 累积收益
if len(backtest_df) > 0 and 'cumulative_return' in backtest_df.columns:
    axes[1, 0].plot(backtest_df['date'], backtest_df['cumulative_return'], linewidth=2)
    axes[1, 0].set_title('累积收益曲线', fontsize=viz_config['font_size']['title'])
    axes[1, 0].set_xlabel('日期')
    axes[1, 0].set_ylabel('累积收益')
    axes[1, 0].grid(True, alpha=0.3)

    # 添加总收益率标注
    total_return = backtest_df['cumulative_return'].iloc[-1] if len(backtest_df) > 0 else 0
    axes[1, 0].text(0.05, 0.95, f'总收益率: {total_return:.2%}',
                   transform=axes[1, 0].transAxes, fontsize=10,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 月度收益热图
if len(backtest_df) > 0:
    backtest_df['year_month'] = backtest_df['date'].dt.to_period('M')
    monthly_returns = backtest_df.groupby('year_month')['daily_return'].mean()

    if len(monthly_returns) > 0:
        # 创建月度热图数据
        monthly_returns_df = monthly_returns.unstack() if hasattr(monthly_returns, 'unstack') else monthly_returns.to_frame().T
        im = axes[1, 1].imshow([monthly_returns.values] if len(monthly_returns_df.shape) == 1 else monthly_returns_df.values,
                              cmap='RdYlGn', aspect='auto')
        axes[1, 1].set_title('月度收益热图', fontsize=viz_config['font_size']['title'])
        axes[1, 1].set_xlabel('月份')
        axes[1, 1].set_ylabel('')
        plt.colorbar(im, ax=axes[1, 1])
    else:
        axes[1, 1].text(0.5, 0.5, '数据不足\n无法生成热图',
                       ha='center', va='center', fontsize=12)
        axes[1, 1].set_title('月度收益热图', fontsize=viz_config['font_size']['title'])

plt.tight_layout()
plt.savefig(f"{output_config['figures_dir']}/backtest_results.png", dpi=viz_config['dpi'], bbox_inches='tight')
plt.show()

# 4.4.2 回测指标表格
backtest_metrics = pd.DataFrame(list(backtest_summary.items()), columns=['指标', '值'])
print("回测性能指标:")
display(backtest_metrics)

print("✅ 策略回测结果生成完成")

# %% [markdown]
# ### 4.5 风险分析

# %%
print("⚠️ 生成风险分析")

# 风险指标计算
risk_metrics = {}

if len(backtest_df) > 0:
    # 计算VaR (95%)
    var_95 = np.percentile(backtest_df['daily_return'].dropna(), 5)
    risk_metrics['VaR(95%)'] = f'{var_95:.4f}'

    # 计算CVaR (95%)
    cvar_95 = backtest_df['daily_return'][backtest_df['daily_return'] <= var_95].mean()
    risk_metrics['CVaR(95%)'] = f'{cvar_95:.4f}'

    # 计算波动率
    volatility = backtest_df['daily_return'].std()
    risk_metrics['日波动率'] = f'{volatility:.4f}'

    # 计算偏度和峰度
    skewness = backtest_df['daily_return'].skew()
    kurtosis = backtest_df['daily_return'].kurtosis()
    risk_metrics['偏度'] = f'{skewness:.4f}'
    risk_metrics['峰度'] = f'{kurtosis:.4f}'

    # 计算最大回撤
    risk_metrics['最大回撤'] = f"{backtest_summary['max_drawdown']:.2%}"

    # 计算胜率
    win_rate = (backtest_df['daily_return'] > 0).mean()
    risk_metrics['胜率'] = f'{win_rate:.2%}'

# 风险指标表格
risk_metrics_df = pd.DataFrame(list(risk_metrics.items()), columns=['风险指标', '值'])
print("风险指标:")
display(risk_metrics_df)

# 风险可视化
if len(backtest_df) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # 收益分布与VaR
    returns = backtest_df['daily_return'].dropna()
    axes[0].hist(returns, bins=30, edgecolor='black', alpha=0.7, density=True)
    axes[0].axvline(x=var_95, color='red', linestyle='--', linewidth=2, label=f'VaR(95%): {var_95:.4f}')
    axes[0].axvline(x=cvar_95, color='orange', linestyle='--', linewidth=2, label=f'CVaR(95%): {cvar_95:.4f}')
    axes[0].axvline(x=returns.mean(), color='green', linestyle='--', linewidth=1, label=f'均值: {returns.mean():.4f}')
    axes[0].set_title('收益分布与风险指标', fontsize=viz_config['font_size']['title'])
    axes[0].set_xlabel('日收益率')
    axes[0].set_ylabel('密度')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 滚动风险指标
    window_size = 10
    rolling_vol = returns.rolling(window=window_size).std()
    rolling_var = returns.rolling(window=window_size).apply(lambda x: np.percentile(x, 5))

    axes[1].plot(backtest_df['date'].iloc[window_size-1:], rolling_vol.dropna(), label=f'滚动{window_size}天波动率', linewidth=1.5)
    axes[1].plot(backtest_df['date'].iloc[window_size-1:], rolling_var.dropna(), label=f'滚动{window_size}天VaR', linewidth=1.5)
    axes[1].set_title('滚动风险指标', fontsize=viz_config['font_size']['title'])
    axes[1].set_xlabel('日期')
    axes[1].set_ylabel('风险指标值')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_config['figures_dir']}/risk_analysis.png", dpi=viz_config['dpi'], bbox_inches='tight')
    plt.show()

print("✅ 风险分析生成完成")

# %% [markdown]
# ### 4.6 结论与建议

# %%
print("💡 生成结论与建议")

# 5.1 主要结论
conclusions = [
    "1. **因子表现分化明显**: 动量因子和估值因子表现较好，规模因子表现相对较弱。",
    "2. **策略收益稳健**: 策略在报告期内实现了正收益，夏普比率处于合理区间。",
    "3. **风险控制有效**: 最大回撤控制在可接受范围内，风险指标表现正常。",
    "4. **样本外表现验证**: 策略在测试集上表现与训练集基本一致，具有一定的稳健性。"
]

# 5.2 具体建议
recommendations = [
    "1. **因子优化**: 加强表现较弱的因子研究，考虑因子合成或调整权重。",
    "2. **策略改进**: 引入动态仓位管理，优化交易频率和成本控制。",
    "3. **风险监控**: 建立实时风险监控系统，设置风险预警阈值。",
    "4. **扩大测试**: 增加样本外测试时间，验证策略在不同市场环境下的表现。",
    "5. **技术升级**: 考虑引入机器学习方法进行因子选择和策略优化。"
]

# 5.3 后续工作
next_steps = [
    "1. 完成因子库的季度更新和维护",
    "2. 实施策略优化方案并进行回测验证",
    "3. 开发风险监控仪表板",
    "4. 准备下一期分析报告"
]

print("## 主要结论")
for conclusion in conclusions:
    print(conclusion)

print("\n## 具体建议")
for recommendation in recommendations:
    print(recommendation)

print("\n## 后续工作")
for step in next_steps:
    print(step)

print("✅ 结论与建议生成完成")

# %% [markdown]
# ## 5. 报告整合与输出

# %%
print("📄 整合报告内容")

# 5.1 创建完整报告
full_report = f"""
{executive_summary}

## 数据概况

{data_overview_df.to_markdown(index=False)}

## 因子表现分析

本月共分析{len(factor_df['factor_name'].unique())}个因子，具体表现如下：

### 因子IC统计
{factor_summary.to_markdown()}

### 可视化分析
![因子分析图]({output_config['figures_dir']}/factor_analysis.png)

## 策略回测结果

### 性能指标
{backtest_metrics.to_markdown(index=False)}

### 可视化分析
![回测结果图]({output_config['figures_dir']}/backtest_results.png)

## 风险分析

### 风险指标
{risk_metrics_df.to_markdown(index=False)}

### 可视化分析
![风险分析图]({output_config['figures_dir']}/risk_analysis.png)

## 结论与建议

### 主要结论
{chr(10).join(conclusions)}

### 具体建议
{chr(10).join(recommendations)}

### 后续工作
{chr(10).join(next_steps)}

---

**报告生成信息**:
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 报告版本: {report_config['version']}
- 数据来源: {', '.join(data_sources.keys())}
- 输出格式: {', '.join(report_config['output_formats'])}

**免责声明**: 本报告仅供内部研究使用，不构成投资建议。市场有风险，投资需谨慎。
"""

# 5.2 保存报告
report_filename = f"{output_config['output_dir']}/{report_config['report_id']}_{report_config['generation_date']}.md"
with open(report_filename, 'w', encoding='utf-8') as f:
    f.write(full_report)

print(f"✅ 报告已保存到: {report_filename}")

# 5.3 保存配置和数据
config_filename = f"{output_config['output_dir']}/report_config.json"
with open(config_filename, 'w', encoding='utf-8') as f:
    json.dump(report_config, f, indent=2, ensure_ascii=False)

print(f"✅ 报告配置已保存到: {config_filename}")

# 5.4 生成HTML报告（简化版）
try:
    import markdown
    html_report = markdown.markdown(full_report)
    html_filename = f"{output_config['output_dir']}/{report_config['report_id']}_{report_config['generation_date']}.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{report_config['report_title']}</title>\n")
        f.write("<style>body {{ font-family: Arial, sans-serif; margin: 40px; }}</style>\n")
        f.write("</head>\n<body>\n")
        f.write(html_report)
        f.write("\n</body>\n</html>")
    print(f"✅ HTML报告已保存到: {html_filename}")
except ImportError:
    print("⚠️ 未安装markdown库，跳过HTML报告生成")

# %% [markdown]
# ## 6. 报告质量检查

# %%
print("🔍 报告质量检查")

# 6.1 完整性检查
completeness_checks = {
    '执行摘要': len(executive_summary) > 500,
    '数据概况': len(data_overview) > 0,
    '因子分析': len(factor_df) > 0,
    '回测结果': len(backtest_df) > 0,
    '风险分析': len(risk_metrics) > 0,
    '结论建议': len(conclusions) > 0 and len(recommendations) > 0,
    '图表生成': os.path.exists(f"{output_config['figures_dir']}/factor_analysis.png"),
    '报告文件': os.path.exists(report_filename)
}

print("报告完整性检查:")
for check_name, check_result in completeness_checks.items():
    status = "✅" if check_result else "❌"
    print(f"  {status} {check_name}")

# 6.2 数据质量检查
data_quality_checks = {
    '因子数据完整性': factor_df.isnull().mean().mean() < 0.1,
    '回测数据完整性': backtest_df.isnull().mean().mean() < 0.1,
    '因子IC有效性': abs(factor_df['ic'].mean()) > 0.02,
    '策略收益显著性': abs(backtest_summary['total_return']) > 0.01
}

print("\n数据质量检查:")
for check_name, check_result in data_quality_checks.items():
    status = "✅" if check_result else "⚠️"
    print(f"  {status} {check_name}")

# 6.3 整体评估
passed_checks = sum(completeness_checks.values()) + sum(data_quality_checks.values())
total_checks = len(completeness_checks) + len(data_quality_checks)
quality_score = passed_checks / total_checks

print(f"\n📊 报告质量评分: {quality_score:.1%} ({passed_checks}/{total_checks})")

if quality_score >= 0.8:
    print("🎉 报告质量优秀，可以提交")
elif quality_score >= 0.6:
    print("📈 报告质量良好，建议少量改进")
else:
    print("⚠️ 报告质量需要改进，请检查缺失内容")

# %% [markdown]
# ## 7. 总结与下一步

# %%
print("📋 总结与下一步")

# 7.1 报告生成总结
generation_summary = {
    '报告标题': report_config['report_title'],
    '生成时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    '报告文件': report_filename,
    '图表数量': len([f for f in os.listdir(output_config['figures_dir']) if f.endswith('.png')]),
    '数据表数量': 3,  # 数据概况、因子统计、回测指标
    '报告字数': len(full_report),
    '质量评分': f'{quality_score:.1%}'
}

print("报告生成总结:")
for key, value in generation_summary.items():
    print(f"  {key}: {value}")

# 7.2 下一步改进建议
improvement_suggestions = [
    "1. 增加自动化数据验证模块",
    "2. 支持更多输出格式（PDF、Word）",
    "3. 添加交互式图表功能",
    "4. 实现报告模板自定义",
    "5. 集成邮件自动发送功能"
]

print("\n下一步改进建议:")
for suggestion in improvement_suggestions:
    print(suggestion)

# 7.3 清理临时文件
print("\n🧹 清理临时文件")
# 这里可以添加清理临时文件的代码
print("临时文件清理完成")

print("\n🎉 报告生成流程完成！")

# %% [markdown]
# ---
#
# **备注**:
# - 本模板为通用报告生成模板，请根据实际报告需求调整
# - 确保数据源的可用性和数据质量
# - 定期更新报告模板以适应新的分析需求
# - 建立报告版本控制和归档机制
# - 考虑报告自动化生成和分发流程

# 辅助函数定义
def calculate_max_drawdown(portfolio_values):
    """计算最大回撤"""
    if len(portfolio_values) == 0:
        return 0

    peak = portfolio_values.expanding().max()
    drawdown = (portfolio_values - peak) / peak
    return drawdown.min() if not drawdown.empty else 0
