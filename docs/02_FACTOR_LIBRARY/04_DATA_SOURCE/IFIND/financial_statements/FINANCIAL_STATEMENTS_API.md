---
module_id: DATA_IFIND_FINANCIAL_API_001
version: 1.0.0
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构师
standard_type: API参考文档
applicable_scope: iFind财务数据API
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 已完成
responsibility: 财务报表API接口与数据获取
---

# iFind财务数据API参考

> **核心职责**: 财务报表数据API接口和使用说明
> **职责边界**: 
> - ✅ 本文档负责：财务报表数据API接口和使用说明
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: iFind财务数据API接口文档
- 提供完整的iFind财务数据API接口说明
- 说明财务报表获取和指标计算方法
- 提供API使用示例和最佳实践

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 财务索引 | [INDEX.md](./INDEX.md) | 上级索引 | 财务数据模块索引 |
| 指标清单 | [THS_BD_COMPLETE_INDICATOR_LIST.md](./THS_BD_COMPLETE_INDICATOR_LIST.md) | 参考资料 | 完整指标清单 |

**职责边界**:
- ✅ 本文档负责: 财务数据API接口定义和使用说明
- ❌ 本文档不负责: 指标详细清单（由 THS_BD_COMPLETE_INDICATOR_LIST.md 负责）

> 清风量化系统 - 同花顺iFind财务数据API文档
> **核心定位**: 提供完整的iFind财务数据API接口说明，指导财务数据获取和使用

---

## 1. API概述

### 1.1 核心功能

| 功能模块 | 说明 | 主要用途 |
|----------|------|----------|
| **财务报表获取** | 资产负债表、利润表、现金流量表 | 基本面分析 |
| **财务指标计算** | ROE、ROA、毛利率等 | 因子计算 |
| **财务数据查询** | 历史财务数据、财务快报 | 回测分析 |
| **财务数据更新** | 实时财务数据同步 | 实时监控 |

### 1.2 快速开始

```python
from zephyr.data.ifind import FinancialDataAPI

# 创建API实例
api = FinancialDataAPI()

# 获取资产负债表
balance_sheet = api.get_balance_sheet(
    symbols=['000001.SZ'],
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 获取利润表
income_statement = api.get_income_statement(
    symbols=['000001.SZ'],
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 获取现金流量表
cash_flow = api.get_cash_flow_statement(
    symbols=['000001.SZ'],
    start_date='2023-01-01',
    end_date='2023-12-31'
)
```

---

## 2. FinancialDataAPI类

### 2.1 初始化参数

```python
FinancialDataAPI(
    api_key: Optional[str] = None,     # iFind API密钥
    timeout: int = 30,                 # 请求超时时间（秒）
    retry_count: int = 3,              # 失败重试次数
    cache_enabled: bool = True,        # 启用缓存
    cache_dir: str = './cache/ifind'   # 缓存目录
)
```

**参数说明**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| api_key | str | None | iFind API密钥（None时从环境变量读取） |
| timeout | int | 30 | 请求超时时间（秒） |
| retry_count | int | 3 | 失败重试次数 |
| cache_enabled | bool | True | 是否启用本地缓存 |
| cache_dir | str | './cache/ifind' | 缓存目录路径 |

### 2.2 核心方法

#### get_balance_sheet()

获取资产负债表数据。

```python
def get_balance_sheet(
    symbols: Union[str, List[str]],    # 股票代码
    start_date: str,                   # 开始日期
    end_date: str,                     # 结束日期
    report_type: str = '合并',         # 报告类型
    fields: Optional[List[str]] = None # 指定字段
) -> pd.DataFrame:
    """
    获取资产负债表数据
    
    Args:
        symbols: 股票代码或代码列表
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        report_type: 报告类型（合并/单季/调整）
        fields: 指定返回字段（None返回全部）
        
    Returns:
        pd.DataFrame: 资产负债表数据
        
    Raises:
        InvalidSymbolError: 股票代码无效
        DataNotFoundError: 数据不存在
    """
```

**示例**:

```python
# 获取单个股票的资产负债表
df = api.get_balance_sheet(
    symbols='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 获取多个股票的资产负债表
df = api.get_balance_sheet(
    symbols=['000001.SZ', '000002.SZ'],
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 获取指定字段
df = api.get_balance_sheet(
    symbols='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31',
    fields=['总资产', '总负债', '股东权益']
)
```

#### get_income_statement()

获取利润表数据。

```python
def get_income_statement(
    symbols: Union[str, List[str]],    # 股票代码
    start_date: str,                   # 开始日期
    end_date: str,                     # 结束日期
    report_type: str = '合并',         # 报告类型
    fields: Optional[List[str]] = None # 指定字段
) -> pd.DataFrame:
    """
    获取利润表数据
    
    Args:
        symbols: 股票代码或代码列表
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        report_type: 报告类型（合并/单季/调整）
        fields: 指定返回字段（None返回全部）
        
    Returns:
        pd.DataFrame: 利润表数据
    """
```

**示例**:

```python
# 获取利润表
df = api.get_income_statement(
    symbols='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 获取指定字段
df = api.get_income_statement(
    symbols='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31',
    fields=['营业收入', '营业成本', '净利润']
)
```

#### get_cash_flow_statement()

获取现金流量表数据。

```python
def get_cash_flow_statement(
    symbols: Union[str, List[str]],    # 股票代码
    start_date: str,                   # 开始日期
    end_date: str,                     # 结束日期
    report_type: str = '合并',         # 报告类型
    fields: Optional[List[str]] = None # 指定字段
) -> pd.DataFrame:
    """
    获取现金流量表数据
    
    Args:
        symbols: 股票代码或代码列表
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        report_type: 报告类型（合并/单季/调整）
        fields: 指定返回字段（None返回全部）
        
    Returns:
        pd.DataFrame: 现金流量表数据
    """
```

**示例**:

```python
# 获取现金流量表
df = api.get_cash_flow_statement(
    symbols='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 获取指定字段
df = api.get_cash_flow_statement(
    symbols='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31',
    fields=['经营活动现金流', '投资活动现金流', '筹资活动现金流']
)
```

#### get_financial_indicator()

获取财务指标数据。

```python
def get_financial_indicator(
    symbols: Union[str, List[str]],    # 股票代码
    indicators: List[str],             # 指标列表
    start_date: str,                   # 开始日期
    end_date: str,                     # 结束日期
    frequency: str = '季'              # 频率（季/年）
) -> pd.DataFrame:
    """
    获取财务指标数据
    
    Args:
        symbols: 股票代码或代码列表
        indicators: 指标列表
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        frequency: 频率（季/年）
        
    Returns:
        pd.DataFrame: 财务指标数据
    """
```

**示例**:

```python
# 获取财务指标
df = api.get_financial_indicator(
    symbols='000001.SZ',
    indicators=['ROE', 'ROA', '毛利率', '净利率'],
    start_date='2023-01-01',
    end_date='2023-12-31',
    frequency='季'
)
```

#### get_financial_report_dates()

获取财报发布日期。

```python
def get_financial_report_dates(
    symbols: Union[str, List[str]],    # 股票代码
    year: int,                         # 年份
    report_type: str = '全部'          # 报告类型
) -> pd.DataFrame:
    """
    获取财报发布日期
    
    Args:
        symbols: 股票代码或代码列表
        year: 年份
        report_type: 报告类型（全部/一季报/半年报/三季报/年报）
        
    Returns:
        pd.DataFrame: 财报发布日期信息
    """
```

**示例**:

```python
# 获取财报发布日期
df = api.get_financial_report_dates(
    symbols='000001.SZ',
    year=2023,
    report_type='年报'
)
```

---

## 3. 财务数据字段

### 3.1 资产负债表字段

| 字段名称 | 说明 | 单位 |
|----------|------|------|
| **总资产** | 企业总资产 | 万元 |
| **总负债** | 企业总负债 | 万元 |
| **股东权益** | 股东权益合计 | 万元 |
| **流动资产** | 流动资产合计 | 万元 |
| **流动负债** | 流动负债合计 | 万元 |
| **货币资金** | 货币资金 | 万元 |
| **应收账款** | 应收账款净额 | 万元 |
| **存货** | 存货净额 | 万元 |
| **固定资产** | 固定资产净额 | 万元 |
| **无形资产** | 无形资产净额 | 万元 |

### 3.2 利润表字段

| 字段名称 | 说明 | 单位 |
|----------|------|------|
| **营业收入** | 营业收入 | 万元 |
| **营业成本** | 营业成本 | 万元 |
| **营业利润** | 营业利润 | 万元 |
| **利润总额** | 利润总额 | 万元 |
| **净利润** | 净利润 | 万元 |
| **销售费用** | 销售费用 | 万元 |
| **管理费用** | 管理费用 | 万元 |
| **财务费用** | 财务费用 | 万元 |
| **所得税** | 所得税费用 | 万元 |

### 3.3 现金流量表字段

| 字段名称 | 说明 | 单位 |
|----------|------|------|
| **经营活动现金流** | 经营活动产生的现金流量净额 | 万元 |
| **投资活动现金流** | 投资活动产生的现金流量净额 | 万元 |
| **筹资活动现金流** | 筹资活动产生的现金流量净额 | 万元 |
| **现金净增加额** | 现金及现金等价物净增加额 | 万元 |
| **期末现金余额** | 期末现金及现金等价物余额 | 万元 |

### 3.4 财务指标字段

| 指标名称 | 说明 | 计算公式 |
|----------|------|----------|
| **ROE** | 净资产收益率 | 净利润 / 股东权益 |
| **ROA** | 总资产收益率 | 净利润 / 总资产 |
| **毛利率** | 销售毛利率 | (营业收入 - 营业成本) / 营业收入 |
| **净利率** | 销售净利率 | 净利润 / 营业收入 |
| **资产负债率** | 资产负债率 | 总负债 / 总资产 |
| **流动比率** | 流动比率 | 流动资产 / 流动负债 |
| **速动比率** | 速动比率 | (流动资产 - 存货) / 流动负债 |

---

## 4. 高级用法

### 4.1 批量获取财务数据

```python
# 批量获取多只股票的财务数据
symbols = ['000001.SZ', '000002.SZ', '000004.SZ']

# 获取资产负债表
balance_sheets = api.get_balance_sheet(
    symbols=symbols,
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 获取利润表
income_statements = api.get_income_statement(
    symbols=symbols,
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 获取现金流量表
cash_flows = api.get_cash_flow_statement(
    symbols=symbols,
    start_date='2023-01-01',
    end_date='2023-12-31'
)
```

### 4.2 财务数据缓存管理

```python
# 启用缓存
api = FinancialDataAPI(cache_enabled=True)

# 获取数据（首次从API获取，后续从缓存读取）
df1 = api.get_balance_sheet('000001.SZ', '2023-01-01', '2023-12-31')

# 清除缓存
api.clear_cache()

# 禁用缓存
api = FinancialDataAPI(cache_enabled=False)
```

### 4.3 财务数据更新检查

```python
# 检查财务数据是否有更新
has_update = api.check_update('000001.SZ', '2023-12-31')

if has_update:
    # 重新获取最新数据
    df = api.get_balance_sheet('000001.SZ', '2023-01-01', '2023-12-31')
    print("数据已更新")
else:
    print("数据无更新")
```

### 4.4 财务数据质量检查

```python
# 检查财务数据质量
quality_report = api.check_data_quality(
    symbols='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

print(f"完整性: {quality_report['completeness']:.2%}")
print(f"准确性: {quality_report['accuracy']:.2%}")
print(f"一致性: {quality_report['consistency']:.2%}")
```

---

## 5. 错误处理

### 5.1 异常类型

```python
from zephyr.data.ifind.exceptions import (
    IFindAPIError,              # iFind API基础异常
    InvalidSymbolError,         # 股票代码无效
    DataNotFoundError,          # 数据不存在
    AuthenticationError,        # 认证失败
    RateLimitError,             # 请求频率限制
    TimeoutError                # 请求超时
)
```

### 5.2 错误处理示例

```python
from zephyr.data.ifind import FinancialDataAPI
from zephyr.data.ifind.exceptions import *

api = FinancialDataAPI()

try:
    # 获取财务数据
    df = api.get_balance_sheet(
        symbols='000001.SZ',
        start_date='2023-01-01',
        end_date='2023-12-31'
    )
    
except InvalidSymbolError as e:
    print(f"股票代码无效: {e}")
    
except DataNotFoundError as e:
    print(f"数据不存在: {e}")
    
except RateLimitError as e:
    print(f"请求频率超限: {e}")
    # 等待后重试
    time.sleep(60)
    df = api.get_balance_sheet('000001.SZ', '2023-01-01', '2023-12-31')
    
except TimeoutError as e:
    print(f"请求超时: {e}")
    
except IFindAPIError as e:
    print(f"API错误: {e}")
```

---

## 6. 性能优化

### 6.1 批量请求优化

```python
# 使用批量请求减少API调用次数
symbols = ['000001.SZ', '000002.SZ', '000003.SZ']

# 一次性获取多只股票数据（推荐）
df = api.get_balance_sheet(
    symbols=symbols,
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 避免循环单次请求（不推荐）
for symbol in symbols:
    df = api.get_balance_sheet(symbol, '2023-01-01', '2023-12-31')
```

### 6.2 缓存策略

```python
# 启用缓存减少重复请求
api = FinancialDataAPI(
    cache_enabled=True,
    cache_dir='./cache/ifind'
)

# 设置缓存过期时间（秒）
api.set_cache_expiry(86400)  # 24小时
```

### 6.3 并发请求

```python
from concurrent.futures import ThreadPoolExecutor

# 并发获取多只股票数据
symbols = ['000001.SZ', '000002.SZ', '000003.SZ']

def fetch_data(symbol):
    return api.get_balance_sheet(symbol, '2023-01-01', '2023-12-31')

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_data, symbols))
```

---

## 7. 数据验证

### 7.1 数据完整性检查

```python
# 检查数据完整性
def check_completeness(df):
    """检查财务数据完整性"""
    required_fields = ['总资产', '总负债', '股东权益', '营业收入', '净利润']
    
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        print(f"缺失字段: {missing_fields}")
        return False
    
    # 检查空值
    null_counts = df[required_fields].isnull().sum()
    if null_counts.any():
        print(f"存在空值:\n{null_counts}")
        return False
    
    return True

# 使用示例
df = api.get_balance_sheet('000001.SZ', '2023-01-01', '2023-12-31')
is_complete = check_completeness(df)
```

### 7.2 数据一致性检查

```python
# 检查会计恒等式
def check_accounting_equation(df):
    """检查会计恒等式: 资产 = 负债 + 股东权益"""
    tolerance = 1e-6  # 容差
    
    diff = abs(df['总资产'] - (df['总负债'] + df['股东权益']))
    
    if (diff > tolerance).any():
        print("会计恒等式不成立")
        return False
    
    return True

# 使用示例
df = api.get_balance_sheet('000001.SZ', '2023-01-01', '2023-12-31')
is_consistent = check_accounting_equation(df)
```

---

## 8. 财务指标计算示例

### 8.1 盈利能力指标

```python
# 计算盈利能力指标
def calculate_profitability(df):
    """计算盈利能力指标"""
    # ROE
    df['ROE'] = df['净利润'] / df['股东权益']
    
    # ROA
    df['ROA'] = df['净利润'] / df['总资产']
    
    # 毛利率
    df['毛利率'] = (df['营业收入'] - df['营业成本']) / df['营业收入']
    
    # 净利率
    df['净利率'] = df['净利润'] / df['营业收入']
    
    return df

# 使用示例
balance_df = api.get_balance_sheet('000001.SZ', '2023-01-01', '2023-12-31')
income_df = api.get_income_statement('000001.SZ', '2023-01-01', '2023-12-31')

# 合并数据
df = pd.merge(balance_df, income_df, on=['股票代码', '报告期'])

# 计算指标
df = calculate_profitability(df)
```

### 8.2 偿债能力指标

```python
# 计算偿债能力指标
def calculate_solvency(df):
    """计算偿债能力指标"""
    # 资产负债率
    df['资产负债率'] = df['总负债'] / df['总资产']
    
    # 流动比率
    df['流动比率'] = df['流动资产'] / df['流动负债']
    
    # 速动比率
    df['速动比率'] = (df['流动资产'] - df['存货']) / df['流动负债']
    
    return df

# 使用示例
df = api.get_balance_sheet('000001.SZ', '2023-01-01', '2023-12-31')
df = calculate_solvency(df)
```

---

## 9. 相关文档

- [INDEX.md](INDEX.md): 财务数据目录索引
- [THS_BD_COMPLETE_INDICATOR_LIST.md](THS_BD_COMPLETE_INDICATOR_LIST.md): iFind完整指标列表
- [../FACTOR_MASTER_INDEX.md](../FACTOR_MASTER_INDEX.md): 因子主索引

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-04 | **维护者**: 首席文档架构师

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
