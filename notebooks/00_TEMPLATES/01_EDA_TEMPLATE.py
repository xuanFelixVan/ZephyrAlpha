---
standard_type: 代码模板
applicable_scope: 探索性数据分析
compliance_level: 初始标准
parent_document: ../README.md
implementation_status: 可用
owner: 研究团队
version: 1.0.0
module_id: TEMPLATE_EDA
created_date: 2026-03-31
last_updated: 2026-04-03
description: 探索性数据分析模板 - 数据质量检查、分布分析、相关性研究
---
"""
探索性数据分析 (EDA) 模板

功能：数据质量检查、分布分析、相关性研究
版本：v1.0
创建日期：2026-03-31
"""

# %% [markdown]
# # 探索性数据分析 (EDA)
# 
# > **项目**: ZephyrAlpha v5.1
# > **作者**: [姓名/团队]
# > **创建日期**: YYYY-MM-DD
# > **更新日期**: YYYY-MM-DD
# > **状态**: ⚪ 进行中 | ✅ 已完成 | 📊 结果已生成
# > **目标**: 对数据集进行全面的探索性分析，包括数据质量检查、分布分析和相关性研究

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
sys.path.append('../../src')  # 添加项目路径

# 配置设置
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
pd.set_option('display.max_columns', 100)
pd.set_option('display.float_format', lambda x: f'{x:.4f}')
np.random.seed(42)  # 可重复性

print("环境设置完成")
print(f"Pandas版本: {pd.__version__}")
print(f"NumPy版本: {np.__version__}")

# %% [markdown]
# ## 2. 数据加载

# %%
# 数据加载 - 根据实际数据路径修改
data_path = "../../data/raw/sample_data.csv"  # 示例路径
print(f"加载数据: {data_path}")

try:
    df = pd.read_csv(data_path)
    print("✅ 数据加载成功")
except FileNotFoundError:
    print("⚠️ 文件未找到，创建示例数据")
    # 创建示例数据用于演示
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'date': dates,
        'open': np.random.normal(100, 10, 100),
        'high': np.random.normal(105, 10, 100),
        'low': np.random.normal(95, 10, 100),
        'close': np.random.normal(102, 10, 100),
        'volume': np.random.randint(100000, 1000000, 100),
        'symbol': 'AAPL'
    })

# 显示数据基本信息
print(f"\n📊 数据形状: {df.shape}")
print(f"📅 时间范围: {df['date'].min()} 到 {df['date'].max()}")
print(f"🔤 数据列: {df.columns.tolist()}")

# 查看前几行
print("\n前5行数据:")
display(df.head())

# %% [markdown]
# ## 3. 数据质量检查

# %%
print("🔍 数据质量检查")

# 3.1 缺失值分析
print("\n1. 缺失值分析:")
missing_df = pd.DataFrame({
    '列名': df.columns,
    '缺失值数量': df.isnull().sum(),
    '缺失值比例': df.isnull().mean().round(4)
})
display(missing_df)

# 3.2 数据类型检查
print("\n2. 数据类型:")
dtype_df = pd.DataFrame({
    '列名': df.columns,
    '数据类型': df.dtypes,
    '唯一值数量': df.nunique()
})
display(dtype_df)

# 3.3 重复值检查
print(f"\n3. 重复行数量: {df.duplicated().sum()}")

# 3.4 描述性统计
print("\n4. 数值列描述性统计:")
display(df.describe())

# %% [markdown]
# ## 4. 单变量分析

# %%
print("📈 单变量分析")

# 选择数值列进行分布分析
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"数值列: {numeric_cols}")

# 创建分布图表
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.ravel()

for i, col in enumerate(numeric_cols[:6]):  # 限制前6个列
    ax = axes[i]
    
    # 直方图
    df[col].hist(ax=ax, bins=30, edgecolor='black', alpha=0.7)
    ax.set_title(f'{col} 分布', fontsize=12)
    ax.set_xlabel(col)
    ax.set_ylabel('频率')
    
    # 添加统计信息
    mean_val = df[col].mean()
    median_val = df[col].median()
    ax.axvline(mean_val, color='r', linestyle='--', alpha=0.7, label=f'均值: {mean_val:.2f}')
    ax.axvline(median_val, color='g', linestyle='--', alpha=0.7, label=f'中位数: {median_val:.2f}')
    ax.legend(fontsize=9)

# 隐藏多余的子图
for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 5. 时间序列分析 (如果适用)

# %%
if 'date' in df.columns:
    print("⏰ 时间序列分析")
    
    # 确保日期列是datetime类型
    df['date'] = pd.to_datetime(df['date'])
    
    # 按日期排序
    df = df.sort_values('date')
    
    # 创建时间序列图表
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. 收盘价趋势
    if 'close' in df.columns:
        axes[0, 0].plot(df['date'], df['close'], linewidth=2)
        axes[0, 0].set_title('收盘价趋势', fontsize=12)
        axes[0, 0].set_xlabel('日期')
        axes[0, 0].set_ylabel('收盘价')
        axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 成交量趋势
    if 'volume' in df.columns:
        axes[0, 1].bar(df['date'], df['volume'], alpha=0.7)
        axes[0, 1].set_title('成交量趋势', fontsize=12)
        axes[0, 1].set_xlabel('日期')
        axes[0, 1].set_ylabel('成交量')
        axes[0, 1].grid(True, alpha=0.3)
    
    # 3. 滚动统计
    if 'close' in df.columns:
        rolling_mean = df['close'].rolling(window=20).mean()
        rolling_std = df['close'].rolling(window=20).std()
        
        axes[1, 0].plot(df['date'], df['close'], label='原始', alpha=0.7)
        axes[1, 0].plot(df['date'], rolling_mean, label='20日移动平均', linewidth=2)
        axes[1, 0].fill_between(df['date'], 
                                rolling_mean - rolling_std, 
                                rolling_mean + rolling_std,
                                alpha=0.2, label='±1标准差')
        axes[1, 0].set_title('移动平均与波动率', fontsize=12)
        axes[1, 0].set_xlabel('日期')
        axes[1, 0].set_ylabel('价格')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # 4. 日收益率分布
    if 'close' in df.columns:
        returns = df['close'].pct_change().dropna()
        axes[1, 1].hist(returns, bins=30, edgecolor='black', alpha=0.7)
        axes[1, 1].axvline(returns.mean(), color='r', linestyle='--', label=f'均值: {returns.mean():.4f}')
        axes[1, 1].axvline(returns.median(), color='g', linestyle='--', label=f'中位数: {returns.median():.4f}')
        axes[1, 1].set_title('日收益率分布', fontsize=12)
        axes[1, 1].set_xlabel('收益率')
        axes[1, 1].set_ylabel('频率')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# %% [markdown]
# ## 6. 多变量分析

# %%
print("🔗 多变量分析")

# 6.1 相关性矩阵
if len(numeric_cols) > 1:
    print("\n1. 相关性矩阵:")
    correlation_matrix = df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, ax=ax)
    ax.set_title('相关性矩阵热图', fontsize=14)
    plt.show()
    
    # 显示高度相关的特征对
    print("\n高度相关的特征对 (|相关性| > 0.7):")
    corr_pairs = correlation_matrix.unstack().sort_values(ascending=False)
    high_corr = corr_pairs[(corr_pairs.abs() > 0.7) & (corr_pairs < 1.0)]
    if not high_corr.empty:
        display(pd.DataFrame(high_corr, columns=['相关性']))
    else:
        print("无高度相关的特征对")

# 6.2 散点图矩阵
if len(numeric_cols) >= 3:
    print("\n2. 散点图矩阵 (前4个数值列):")
    selected_cols = numeric_cols[:4]
    
    try:
        scatter_matrix = pd.plotting.scatter_matrix(df[selected_cols], 
                                                   figsize=(12, 10),
                                                   diagonal='hist',
                                                   alpha=0.7)
        plt.suptitle('散点图矩阵', fontsize=14)
        plt.tight_layout()
        plt.show()
    except:
        print("散点图矩阵生成失败，数据可能不足")

# %% [markdown]
# ## 7. 异常值检测

# %%
print("🚨 异常值检测")

# 7.1 IQR方法检测异常值
print("\n1. IQR方法异常值检测:")
outliers_summary = []

for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    outlier_count = len(outliers)
    outlier_percent = outlier_count / len(df) * 100
    
    outliers_summary.append({
        '列名': col,
        '异常值数量': outlier_count,
        '异常值比例%': f'{outlier_percent:.2f}',
        '下限': f'{lower_bound:.2f}',
        '上限': f'{upper_bound:.2f}'
    })

outliers_df = pd.DataFrame(outliers_summary)
display(outliers_df)

# 7.2 可视化异常值
if len(numeric_cols) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 箱线图
    df[numeric_cols[:min(5, len(numeric_cols))]].boxplot(ax=axes[0])
    axes[0].set_title('箱线图 (异常值检测)', fontsize=12)
    axes[0].set_ylabel('值')
    axes[0].tick_params(axis='x', rotation=45)
    
    # 散点图显示异常值
    if len(numeric_cols) >= 2:
        col1, col2 = numeric_cols[0], numeric_cols[1]
        axes[1].scatter(df[col1], df[col2], alpha=0.6, s=30)
        axes[1].set_xlabel(col1)
        axes[1].set_ylabel(col2)
        axes[1].set_title(f'{col1} vs {col2} 散点图', fontsize=12)
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# %% [markdown]
# ## 8. 数据转换建议

# %%
print("💡 数据转换建议")

recommendations = []

# 检查偏度和峰度
for col in numeric_cols:
    skewness = df[col].skew()
    kurtosis = df[col].kurtosis()
    
    rec = {'列名': col, '偏度': f'{skewness:.3f}', '峰度': f'{kurtosis:.3f}'}
    
    # 基于偏度的建议
    if abs(skewness) > 1:
        rec['建议'] = '考虑对数变换或Box-Cox变换'
    elif abs(skewness) > 0.5:
        rec['建议'] = '轻微偏斜，可能需要变换'
    else:
        rec['建议'] = '分布相对对称'
    
    # 基于峰度的建议
    if kurtosis > 3:
        rec['峰度解读'] = '尖峰分布（尾部较重）'
    elif kurtosis < 3:
        rec['峰度解读'] = '平峰分布（尾部较轻）'
    else:
        rec['峰度解读'] = '正态分布峰度'
    
    recommendations.append(rec)

rec_df = pd.DataFrame(recommendations)
display(rec_df)

# %% [markdown]
# ## 9. 结论与建议

# %%
print("📋 结论与建议")

# 9.1 主要发现总结
print("\n## 主要发现")
print("1. **数据质量**: ", end="")
missing_total = df.isnull().sum().sum()
if missing_total == 0:
    print("数据完整，无缺失值")
else:
    print(f"发现 {missing_total} 个缺失值，需要处理")

print("2. **数据规模**: ", end="")
print(f"数据集包含 {len(df)} 行，{len(df.columns)} 列")

print("3. **数据类型**: ", end="")
numeric_count = len(numeric_cols)
categorical_count = len(df.columns) - numeric_count
print(f"数值型列: {numeric_count}, 类别型列: {categorical_count}")

# 9.2 建议
print("\n## 建议与下一步")
print("1. **数据清洗**: ", end="")
if missing_total > 0:
    print("处理缺失值（填充或删除）")
else:
    print("数据已清洁，无需额外清洗")

print("2. **特征工程**: ", end="")
if len(outliers_df[outliers_df['异常值数量'] > 0]) > 0:
    print("处理异常值，考虑稳健统计量")
else:
    print("异常值较少，可直接使用")

print("3. **建模准备**: ", end="")
high_skew = rec_df[rec_df['建议'].str.contains('考虑对数变换')]
if len(high_skew) > 0:
    print(f"对 {len(high_skew)} 个高度偏斜的特征进行变换")
else:
    print("特征分布相对良好，适合直接建模")

print("4. **下一步分析**: ", end="")
print("进行特征选择、模型训练和验证")

# %% [markdown]
# ## 10. 保存结果

# %%
print("💾 保存分析结果")

# 创建输出目录
import os
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# 保存数据质量报告
quality_report = {
    '数据形状': df.shape,
    '总缺失值': int(df.isnull().sum().sum()),
    '数值列数量': len(numeric_cols),
    '分析日期': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
}

import json
with open(f'{output_dir}/eda_quality_report.json', 'w') as f:
    json.dump(quality_report, f, indent=2)

print(f"✅ 数据质量报告已保存到: {output_dir}/eda_quality_report.json")

# 保存关键统计量
key_stats = df[numeric_cols].describe().round(4)
key_stats.to_csv(f'{output_dir}/key_statistics.csv')
print(f"✅ 关键统计量已保存到: {output_dir}/key_statistics.csv")

# 保存相关性矩阵
if len(numeric_cols) > 1:
    correlation_matrix.to_csv(f'{output_dir}/correlation_matrix.csv')
    print(f"✅ 相关性矩阵已保存到: {output_dir}/correlation_matrix.csv")

print("\n🎉 EDA分析完成！")

# %% [markdown]
# ---
# 
# **备注**: 
# - 本模板为通用EDA模板，请根据实际数据调整
# - 建议定期更新EDA分析，跟踪数据质量变化
# - 对于大型数据集，考虑抽样分析以提高效率