﻿---
module_id: DATA_FREE_SOURCES_001
version: 3.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-06
owner: 首席文档架构师
responsibility: 免费数据源汇总与使用指南
standard_type: 数据源文档
applicable_scope: 免费数据源
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 设计阶段
---


# T.01.DS001.免费数据源技术规格书

> **核心职责**: 免费数据源清单和接入指南，涉及免费数据源技术规格书
> **职责边界**: 
> - ✅ 本文档负责：免费数据源清单和接入指南
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 免费数据源技术规格定义
- 整合和评估可用的免费数据源
- 定义免费数据源的技术规格和接入方式
- 提供数据源选型建议和对比分析

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 数据源适配器 | [DATA_SOURCE_ADAPTERS.md](./DATA_SOURCE_ADAPTERS.md) | 架构层 | 数据源适配器架构 |
| Baostock接口 | [BAOSTOCK_CONNECTOR.md](./BAOSTOCK_CONNECTOR.md) | 实现层 | Baostock数据源实现 |
| 数据源索引 | [INDEX.md](./INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: 定义免费数据源的技术规格和选型建议
- ❌ 本文档不负责: 数据源适配器架构（由 DATA_SOURCE_ADAPTERS.md 负责）
- ❌ 本文档不负责: 具体数据源实现（由各CONNECTOR文档负责）

> 清风量化系统 ZephyrAlpha
>
> **相关文档**:
> - 上级索引: [../../INDEX.md](../../INDEX.md)
> - 因子主索引: [FACTOR_MASTER_INDEX.md](02_FACTOR_LIBRARY/04_DATA_SOURCE/factor_master_index.md)
> - 数据源索引: [数据源索引](./INDEX.md)

***

## 1. 文档基本信息

| 属性 | 值 |
|------|------|
| 文档编号 | T.01.DS001 |
| 文档名称 | 免费数据源技术规格书 |
| 文档类型 | 技术规格书 |
| 数据源 | Baostock / AkShare / Efinance / Tushare / 东财 / 同花顺 |
| 更新频率 | 按需 |

**文档目的**: 为系统提供免费数据源的完整技术规格，确保在付费数据不可用时能够获取A股市场基础数据。

**适用范围**: 所有需要免费数据支持的业务场景。

***

## 2. 数据源概览

| 数据源 | 接口数量 | 稳定性 | 数据类型 | 费用 |
|--------|----------|------|----------|------|
| Baostock | 28+ | 高稳定 | 行情/财务/估值 | 免费 |
| AkShare | 115+ | 较稳定 | 行情/财务/资金 | 免费 |
| Efinance | 65+ | 较稳定 | 行情/资金流向 | 免费 |
| Tushare | 35+ | 较稳定 | 行情/财务/资金 | 部分收费 |
| 东财接口 | 28+ | 较稳定 | 行情数据 | 免费 |
| 同花顺接口 | 21+ | 稳定 | 行情/资金 | 免费 |

***

## 3. Baostock数据源（28+接口）

### 3.1 行情数据接口（4个）

```python
class BaostockQuote:
    """Baostock行情数据接口"""

    COLUMNS = {
        '基础行情字段': ['date', 'code', 'open', 'high', 'low', 'close', 'preclose'],
        '成交量价字段': ['volume', 'amount', 'turn', 'pctChg'],
        '估值指标字段': ['peTTM', 'psTTM', 'pcfNcfTTM', 'pbMRQ'],
        '状态字段': ['isST']
    }

    def get_daily(self, code, start_date, end_date):
        """
        获取日K线行情数据

        Parameters:
            code: 股票代码，格式 'sh.600000'
            start_date: 开始日期，格式 '2024-01-01'
            end_date: 结束日期，格式 '2024-12-31'

        Returns:
            DataFrame with columns: date, code, open, high, low, close, volume, amount, turn, pctChg, isST, peTTM, psTTM, pcfNcfTTM, pbMRQ
        """
        pass

    def get_realtime(self, codes):
        """
        获取实时行情

        Parameters:
            codes: 股票代码列表

        Returns:
            DataFrame with realtime quote
        """
        pass
```

### 3.2 财务数据接口（1个）

```python
class BaostockFinance:
    """Baostock财务数据接口"""

    INDICATORS = {
        '盈利能力指标': [
            '净利润', '毛利率', '净利率',
            '营业利润率', 'ROA', '总资产收益率', 'ROE'
        ],
        '偿债能力指标（7个）': [
            '流动比率', '速动比率', '资产负债率',
            '权益乘数', '利息保障倍数', '长期负债率', '股东权益比率'
        ],
        '营运能力指标（4个）': [
            '应收账款周转率', '存货周转率',
            '总资产周转率', '固定资产周转率'
        ],
        '成长能力指标（3个）': [
            '营业收入增长率', '营业利润增长率', '净利润增长率'
        ]
    }

    def get_finance(self, code, start_date, end_date, statements='all'):
        """
        获取财务报表

        Parameters:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            statements: 'all'/'income'/'balance'/'cash'

        Returns:
            DataFrame with financial data
        """
        pass

    def get_performance(self, start_date, end_date):
        """
        获取业绩预告/快报

        Parameters:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame with performance preview
        """
        pass
```

### 3.3 使用示例

```python
import baostock as bs
import pandas as pd

# 登录
lg = bs.login()
print(f'Login respond error_code:{lg.error_code}')
print(f'Login respond error_msg:{lg.error_msg}')

# 获取日K线数据
rs = bs.query_history_k_data_plus(
    "sh.600000",
    "date,code,open,high,low,close,volume,amount,pctChg",
    start_date='2024-01-01',
    end_date='2024-12-31',
    frequency="d"
)

# 转换为DataFrame
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
df = pd.DataFrame(data_list, columns=rs.fields)

# 登出
bs.logout()

print(df.head())
```

***

## 4. AkShare数据源（115+接口）

### 4.1 A股行情接口（45个）

```python
class AkShareQuote:
    """AkShare行情数据接口"""

    def stock_zh_a_spot_em(self):
        """
        获取A股实时行情

        Returns:
            DataFrame with columns: 序号, 代码, 名称, 最新价, 涨跌幅
            涨跌额, 成交量, 成交额, 振幅, 最高, 最低, 今开, 昨收
        """
        pass

    def stock_zh_a_hist(
        self,
        symbol: str,
        period: str = "daily",
        start_date: str = None,
        end_date: str = None,
        adjust: str = "qfq"
    ):
        """
        获取A股历史行情

        Parameters:
            symbol: 股票代码
            period: 'daily'/'weekly'/'monthly'
            start_date: 开始日期
            end_date: 结束日期
            adjust: 'qfq'/'hfq'/'none'

        Returns:
            DataFrame with OHLCV data
        """
        pass

    def stock_zh_a_minute(
        self,
        symbol: str,
        period: str = "5",
        adjust: str = "qfq"
    ):
        """
        获取分钟K线数据

        Parameters:
            symbol: 股票代码
            period: '1'/'5'/'15'/'30'/'60'
            adjust: 'qfq'/'hfq'/'none'

        Returns:
            DataFrame with minute data
        """
        pass
```

### 4.2 财务数据接口（4个）

```python
class AkShareFinance:
    """AkShare财务数据接口"""

    def stock_financial_report_sina(self, stock: str, symbol: str = "利润表"):
        """
        获取财务报表

        Parameters:
            stock: 股票代码
            symbol: '利润表'/'资产负债表'/'现金流量表'

        Returns:
            DataFrame with financial report
        """
        pass

    def stock_financial_analysis_indicator(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ):
        """
        获取财务指标

        Returns:
            DataFrame with ROE, EPS, etc.
        """
        pass
```

### 4.3 市场数据接口（9个）

```python
class AkShareMarket:
    """AkShare市场数据"""

    def stock_lhb_detail_em(self, date: str = None):
        """
        获取龙虎榜明细

        Parameters:
            date: 交易日期，格式 '2024-01-15'

        Returns:
            DataFrame with columns: 序号, 代码, 名称, 收盘价,
            涨跌幅, 龙虎榜净买, 龙虎榜买入, 龙虎榜卖出, 龙虎榜成交额
        """
        pass

    def stock_margin_detail(self, symbol: str = None, date: str = None):
        """
        获取融资融券数据

        Returns:
            DataFrame with 融资余额, 融资买入额, 融券余额等
        """
        pass

    def stock_block_trade_em(self, start_date: str, end_date: str):
        """
        获取大宗交易数据

        Returns:
            DataFrame with 成交价, 成交量, 成交额, 溢价率等
        """
        pass
```

### 4.4 指数数据接口

```python
class AkShareIndex:
    """AkShare指数数据"""

    def index_zh_a_spot_em(self):
        """
        获取A股指数行情

        Returns:
            DataFrame with 指数代码, 指数名称, 最新价等
        """
        pass

    def index_zh_a_hist(self, symbol: str, period: str = "daily", start_date: str = None, end_date: str = None):
        """
        获取指数历史行情

        Parameters:
            symbol: 指数代码，如 '000001'（上证指数）
            period: 'daily'/'weekly'/'monthly'

        Returns:
            DataFrame with index OHLCV
        """
        pass

    def stock_board_industry_name_em(self):
        """
        获取行业板块列表

        Returns:
            DataFrame with 行业板块名称和代码
        """
        pass

    def stock_board_concept_name_em(self):
        """
        获取概念板块列表

        Returns:
            DataFrame with 概念板块名称和代码
        """
        pass
```

### 4.5 使用示例

```python
import akshare as ak
import pandas as pd

# 获取实时行情
df_spot = ak.stock_zh_a_spot_em()
print(df_spot[['代码', '名称', '最新价', '涨跌幅']].head())

# 获取日K线
df_hist = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"
)
print(df_hist.head())

# 获取龙虎榜数据
df_lhb = ak.stock_lhb_detail_em(date="20240115")
print(df_lhb.head())

# 获取行业板块
df_industry = ak.stock_board_industry_name_em()
print(df_industry.head())
```

***

## 5. Efinance数据源（65+接口）

### 5.1 行情数据接口（8个）

```python
class EFinanceQuote:
    """EFinance行情数据接口"""

    def get_quote(self, codes):
        """
        获取实时行情

        Parameters:
            codes: 股票代码列表，如 ['000001', '000002']

        Returns:
            DataFrame with realtime quote
        """
        pass

    def get_kline(self, code, start_date=None, end_date=None, klt='101'):
        """
        获取K线数据

        Parameters:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            klt:  Kline type, '101'=日线, '102'=周线, '103'=月线

        Returns:
            DataFrame with OHLCV data
        """
        pass
```

### 5.2 资金流向接口（3个，核心优势）

```python
class EFinanceMoneyFlow:
    """EFinance资金流向接口 - 核心优势功能"""

    def get_individual_money_flow(self, stock: str, date: str = None):
        """
        获取个股资金流向

        Parameters:
            stock: 股票代码
            date: 日期

        Returns:
            DataFrame with columns:
            - 主力净流入金额
            - 超大单净流入金额
            - 大单净流入金额
            - 中单净流入金额
            - 小单净流入金额
        """
        pass

    def get_sector_money_flow(self, sector_type: str = "行业", date: str = None):
        """
        获取板块资金流向

        Parameters:
            sector_type: '行业'/'概念'
            date: 日期

        Returns:
            DataFrame with columns:
            - 板块名称
            - 主力净流入金额
            - 涨跌幅
            - 净流入率
        """
        pass

    def get_north_money_flow(self, date: str = None):
        """
        获取北向资金流向

        Returns:
            DataFrame with columns:
            - 日期
            - 北向资金净流入额
            - 北向资金余额
            - 南向资金净流入额
        """
        pass
```

### 5.3 使用示例

```python
from efinance import stock
import pandas as pd

# 获取实时行情
df = stock.get_quote(['000001', '000002'])
print(df[['股票名称', '最新价', '涨跌幅']].head())

# 获取个股资金流向
df_mf = stock.get_individual_money_flow('000001', '20240115')
print(df_mf)

# 获取北向资金
df_north = stock.get_north_money_flow('20240115')
print(df_north)
```

***

## 6. Tushare数据源（35+接口）

### 6.1 基础数据接口（5个）

```python
class TushareData:
    """Tushare基础数据"""

    def get_daily(self, ts_code, start_date, end_date):
        """
        获取日K线数据

        Returns:
            DataFrame with date, ts_code, open, high, low, close, vol, amount, pct_chg
        """
        pass

    def get_weekly(self, ts_code, start_date, end_date):
        """获取周K线数据"""
        pass

    def get_monthly(self, ts_code, start_date, end_date):
        """获取月K线数据"""
        pass

    def get_restricted_shares(self, start_date, end_date):
        """
        获取限售股解禁数据

        Returns:
            DataFrame with 解禁日期, 股票代码, 解禁数量, 解禁市值
        """
        pass
```

### 6.2 Pro版接口（需积分，2000+）

```python
class TusharePro:
    """Tushare Pro高级接口（需积分）"""

    def get_minute_data(self, ts_code, trade_date, freq='5min'):
        """
        获取分钟数据

        Parameters:
            ts_code: 股票代码
            trade_date: 交易日期
            freq: '1min'/'5min'/'15min'/'30min'/'60min'

        Returns:
            DataFrame with minute OHLCV
        """
        pass

    def get_financial(self, ts_code, period_type='annual'):
        """
        获取财务报表

        Parameters:
            ts_code: 股票代码
            period_type: 'annual'/'quarter'

        Returns:
            DataFrame with 利润表, 资产负债表, 现金流量表
        """
        pass

    def get_money_flow(self, ts_code, trade_date):
        """
        获取个股资金流向

        Returns:
            DataFrame with 主力净流入, 超大单净流入等
        """
        pass
```

### 6.3 使用示例

```python
import tushare as ts

# 设置token
ts.set_token('your_token_here')
pro = ts.pro_api()

# 获取日K线数据
df = pro.daily(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20241231'
)
print(df.head())

# 获取财务指标
df_fin = pro.fina_indicator(ts_code='000001.SZ')
print(df_fin[['ts_code', 'ann_date', 'roe', 'eps']].head())
```

***

## 7. 数据存储结构

### 7.1 存储路径

```python
DATA_STORAGE_STRUCTURE = {
    '行情数据': {
        '日线': 'data/quotes/daily/{stock_code}.parquet',
        '周线': 'data/quotes/weekly/{stock_code}.parquet',
        '月线': 'data/quotes/monthly/{stock_code}.parquet',
        '5分钟': 'data/quotes/5min/{stock_code}_{date}.parquet',
        '15分钟': 'data/quotes/15min/{stock_code}_{date}.parquet',
        '30分钟': 'data/quotes/30min/{stock_code}_{date}.parquet',
        '60分钟': 'data/quotes/60min/{stock_code}_{date}.parquet',
    },
    '财务数据': {
        '利润表': 'data/financial/income/{stock_code}_{period}.parquet',
        '资产负债表': 'data/financial/balance/{stock_code}_{period}.parquet',
        '现金流量表': 'data/financial/cashflow/{stock_code}_{period}.parquet',
        '业绩预告': 'data/financial/performance/{stock_code}_{date}.parquet',
    },
    '估值数据': {
        '估值指标': 'data/valuation/daily/{date}.parquet',
        '历史估值': 'data/valuation/history/{stock_code}.parquet',
    },
    '资金数据': {
        '个股资金流向': 'data/money_flow/individual/{stock_code}_{date}.parquet',
        '板块资金流向': 'data/money_flow/sector/{sector}_{date}.parquet',
        '北向资金': 'data/money_flow/north/{date}.parquet',
    },
    '市场数据': {
        '融资融券': 'data/market/margin/{date}.parquet',
        '大宗交易': 'data/market/block/{date}.parquet',
        '龙虎榜': 'data/market/lhb/{date}.parquet',
        '解禁股': 'data/market/restricted/{date}.parquet',
    }
}
```

### 7.2 数据源优先级

| 数据类型 | 优先数据源 | 备用数据源 |
|----------|----------|----------|
| 日线行情 | 免费 | 付费/收费API |
| 分钟行情 | 免费 | Baostock/AkShare |
| 实时K线 | 收费 | AkShare/EFinance |
| 财务数据 | 免费/收费 | Baostock/AkShare |
| 资金流向 | 收费 | EFinance（核心优势） |
| 龙虎榜 | 免费 | AkShare |
| 融资融券 | 收费 | AkShare |

***

## 8. 推荐数据源配置

### 8.1 最佳免费组合

```python
RECOMMENDED_FREE_SETUP = {
    '行情数据源': 'Baostock + AkShare',
    '财务数据源': 'Baostock',
    '资金流向源': 'EFinance',
    '市场数据源': 'AkShare',
    '龙虎榜源': 'AkShare + 东财',
    '融资融券源': 'AkShare'
}
```

### 8.2 数据源优先级

| 优先级 | 数据类型 | 推荐数据源 | 说明 |
|--------|----------|------------|--------|
| P0 | 日线/分钟行情 | Baostock/AkShare | 核心数据源 |
| P0 | 财务数据 | Baostock | 核心数据源 |
| P1 | 资金流向 | EFinance | 核心优势 |
| P1 | 龙虎榜 | AkShare | 免费 |
| P2 | 融资融券 | AkShare | 免费 |
| P2 | 大宗交易 | AkShare | 免费 |
| P3 | 解禁股 | AkShare | 免费 |

***

## 9. Python集成器

```python
import pandas as pd
from typing import Optional, List, Dict
import warnings
warnings.filterwarnings('ignore')

class DataSourceIntegrator:
    """
    免费数据源统一集成器
    提供统一接口，自动选择最佳数据源
    """

    def __init__(self):
        self.baostock = None
        self.akshare = None
        self.efinance = None
        self.tushare = None

    def init_baostock(self):
        """初始化Baostock"""
        try:
            import baostock as bs
            lg = bs.login()
            if lg.error_code == '0':
                self.baostock = bs
                print(f"Baostock登录成功")
            else:
                print(f"Baostock登录失败: {lg.error_msg}")
        except ImportError:
            print("请安装baostock: pip install baostock")

    def init_akshare(self):
        """初始化AkShare"""
        try:
            import akshare as ak
            self.akshare = ak
            print(f"AkShare初始化成功")
        except ImportError:
            print("请安装akshare: pip install akshare")

    def init_efinance(self):
        """初始化EFinance"""
        try:
            from efinance import stock
            self.efinance = stock
            print(f"EFinance初始化成功")
        except ImportError:
            print("请安装efinance: pip install efinance")

    def get_daily_quote(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取日K线数据，优先Baostock，失败则AkShare

        Parameters:
            code: 股票代码，如 '000001'
            start_date: 开始日期，格式 '2024-01-01'
            end_date: 结束日期，格式 '2024-12-31'

        Returns:
            DataFrame with OHLCV data
        """
        df = None

        if self.baostock:
            try:
                bs_code = f"sh.{code}" if code.startswith('6') else f"sz.{code}"
                rs = self.baostock.query_history_k_data_plus(
                    bs_code,
                    "date,code,open,high,low,close,volume,amount,pctChg",
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', ''),
                    frequency="d"
                )
                if rs.error_code == '0':
                    data_list = []
                    while rs.next():
                        data_list.append(rs.get_row_data())
                    df = pd.DataFrame(data_list, columns=rs.fields)
                    df['code'] = code
            except Exception as e:
                print(f"Baostock获取失败: {e}")

        if df is None and self.akshare:
            try:
                df = self.akshare.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', ''),
                    adjust="qfq"
                )
            except Exception as e:
                print(f"AkShare获取失败: {e}")

        return df

    def get_money_flow(self, code: str, date: str) -> Optional[pd.DataFrame]:
        """
        获取个股资金流向，EFinance优先

        Parameters:
            code: 股票代码
            date: 日期

        Returns:
            DataFrame with 主力/超大单/大单/中单/小单净流入
        """
        if self.efinance:
            try:
                df = self.efinance.get_individual_money_flow(code, date)
                return df
            except Exception as e:
                print(f"EFinance获取失败: {e}")

        return None

    def get_lhb(self, date: str) -> Optional[pd.DataFrame]:
        """
        获取龙虎榜数据

        Parameters:
            date: 日期

        Returns:
            DataFrame with 龙虎榜明细
        """
        if self.akshare:
            try:
                df = self.akshare.stock_lhb_detail_em(date=date)
                return df
            except Exception as e:
                print(f"获取龙虎榜失败: {e}")

        return None

    def get_north_money(self, date: str) -> Optional[pd.DataFrame]:
        """
        获取北向资金

        Parameters:
            date: 日期

        Returns:
            DataFrame with 北向资金净流入额等
        """
        if self.efinance:
            try:
                df = self.efinance.get_north_money_flow(date)
                return df
            except Exception as e:
                print(f"获取北向资金失败: {e}")

        if self.akshare:
            try:
                df = self.akshare.stock_hsgt_north_flow_em()
                return df
            except Exception as e:
                print(f"AkShare获取北向资金失败: {e}")

        return None

    def __del__(self):
        """清理资源，登出Baostock"""
        if self.baostock:
            self.baostock.logout()
```

***

## 10. 使用示例

```python
# 创建数据源集成器
integrator = DataSourceIntegrator()
integrator.init_baostock()
integrator.init_akshare()
integrator.init_efinance()

# 获取日K线数据
df_quote = integrator.get_daily_quote('000001', '2024-01-01', '2024-12-31')
print(f"获取行情数据: {len(df_quote)} 条")

# 获取个股资金流向
df_mf = integrator.get_money_flow('000001', '2024-01-15')
print(f"资金流向: {df_mf}")

# 获取龙虎榜
df_lhb = integrator.get_lhb('2024-01-15')
print(f"龙虎榜: {len(df_lhb)} 条")

# 获取北向资金
df_north = integrator.get_north_money('2024-01-15')
print(f"北向资金: {df_north}")
```

***

## 11. 注意事项

1. **API限流**: 免费接口有调用频率限制，建议合理控制请求频率。
2. **数据完整性**: 免费数据可能存在缺失，建议与付费数据交叉验证。
3. **稳定性**: 免费接口可能不稳定，建议实现重试机制。
4. **数据延迟**: 免费数据可能有延迟，不适合高频交易。

***

## 12. 另类数据扩展

> **说明**: 本节为系统_v3.0 新增AK

> **目标**: 为清风量化系统 ZephyrAlpha 提供另类数据支持，增强因子库的多样性和预测能力。

### 12.1 另类数据分类总览

| 数据类型 | 数据源 | 覆盖范围 | Alpha潜力 | 数据获取难度 |
|:---------|:-------|:---------|:---------|:------------|
| **新闻舆情数据** | 免费/付费接口 | 广 | 中等 | 较易获取 |
| **社交媒体数据** | 免费/爬虫 | 中等 | 中等 | 需合规获取 |
| **供应链数据** | 免费/爬虫 | 中等 | 较高 | 需深度挖掘 |
| **专利数据** | 免费/付费 | 中等 | 较高 | 需专业处理 |
| **招聘数据** | 免费/爬虫 | 广 | 中等 | 较易获取 |
| **电商数据** | 爬虫/付费 | 中等 | 较高 | 需合规获取 |

### 12.2 新闻舆情数据接口

```python
class NewsSentimentProvider:
    """
    新闻舆情数据提供者
    提供基于Tushare/akshare的新闻舆情数据
    """

    def __init__(self):
        self.tushare = None
        self.akshare = None

    def init_tushare(self, token: str):
        """初始化Tushare"""
        try:
            import tushare as ts
            ts.set_token(token)
            self.tushare = ts.pro_api()
        except ImportError:
            print("请安装tushare: pip install tushare")

    def get_stock_news(self, stock_code: str, date: str) -> pd.DataFrame:
        """
        获取股票新闻

        Parameters:
            stock_code: 股票代码，如 '000001'
            date: 日期，格式 '20240115'

        Returns:
            DataFrame with 新闻标题, 发布时间, 新闻来源, 新闻内容
        """
        if self.tushare:
            try:
                df = self.tushare.news(
                    token=self.tushare,
                    symbol=stock_code,
                    date=date
                )
                return df
            except Exception as e:
                print(f"获取新闻数据失败: {e}")

        return pd.DataFrame()

    def calc_sentiment(self, news_df: pd.DataFrame) -> float:
        """
        计算新闻情感分数

        Returns:
            float: -1.0 (极度悲观) ~ 1.0 (极度乐观)
        """
        if news_df.empty:
            return 0.0

        positive_keywords = ['增长', '盈利', '突破', '创新高', '利好', '上涨']
        negative_keywords = ['亏损', '下滑', '违约', '暴跌', '利空', '跌停']

        sentiment = 0.0
        for _, row in news_df.iterrows():
            content = str(row.get('title', '')) + str(row.get('content', ''))
            for kw in positive_keywords:
                if kw in content:
                    sentiment += 0.1
            for kw in negative_keywords:
                if kw in content:
                    sentiment -= 0.1

        return max(-1.0, min(1.0, sentiment / max(len(news_df), 1)))
```

### 12.3 另类数据适配器

```python
class AlternativeDataAdapter:
    """
    另类数据统一适配器
    整合多种另类数据源，提供统一接口
    """

    def __init__(self):
        self.news_provider = NewsSentimentProvider()
        self.data_sources = {}

    def add_provider(self, name: str, provider):
        """添加数据提供者"""
        self.data_sources[name] = provider

    def calc_alternative_signal(self, stock_code: str) -> dict:
        """
        计算另类数据综合信号

        Returns:
            dict: {
                'news_sentiment': float,      # 新闻情感
                'logistics_signal': float,    # 物流信号
                'consumer_signal': float,     # 消费信号
                'composite': float             # 综合信号
            }
        """
        signals = {}

        try:
            news_df = self.news_provider.get_stock_news(stock_code)
            signals['news_sentiment'] = self.news_provider.calc_sentiment(news_df)
        except Exception as e:
            print(f"获取新闻情感信号失败: {e}")
            signals['news_sentiment'] = None

        for name, provider in self.data_sources.items():
            try:
                data = provider.get_data(stock_code)
                signals[name] = self.process_data(name, data)
            except Exception as e:
                print(f"{name}数据获取失败: {e}")
                signals[name] = None

        valid_signals = [v for v in signals.values() if v is not None]
        if valid_signals:
            signals['composite'] = np.mean(valid_signals)
        else:
            signals['composite'] = None

        return signals

    def process_data(self, name: str, data) -> float:
        """处理数据，返回标准化信号"""
        return 0.0
```

### 12.4 天气数据提供者

```python
class WeatherDataProvider:
    """
    天气数据提供者
    提供基于天气/气温的行业影响因子
    """

    def get_weather(self, city: str, date: str) -> dict:
        """
        获取天气数据

        Returns:
            dict: {
                'temperature': float,    # 气温
                'precipitation': float,  # 降水量
                'weather_type': str      # 天气类型
            }
        """
        return {
            'temperature': 25.0,
            'precipitation': 0.0,
            'weather_type': '晴'
        }

    def calc_weather_factor(self, sector: str, weather_data: dict) -> float:
        """
        计算天气对行业的影响因子

        Parameters:
            sector: 行业名称
            weather_data: 天气数据

        Returns:
            float: 天气影响因子，范围-1.0 ~ 1.0
        """
        sector_weather_map = {
            '农业': ['precipitation', 'temperature'],
            '空调制造': ['temperature'],
            '旅游': ['temperature'],
            '建筑建材': ['temperature', 'precipitation']
        }

        relevant_factors = sector_weather_map.get(sector, [])
        if not relevant_factors:
            return 0.0

        factor = 0.0
        for f in relevant_factors:
            if f == 'temperature':
                temp = weather_data.get('temperature', 20)
                if temp < 0 or temp > 35:
                    factor -= 0.3
                elif 15 <= temp <= 28:
                    factor += 0.2
            elif f == 'precipitation':
                rain = weather_data.get('precipitation', 0)
                if rain > 50:
                    factor -= 0.3

        return max(-1.0, min(1.0, factor))
```

### 12.5 另类数据应用场景

| 数据类型 | 应用场景 | 难度 | 数据源 |
|---------|---------|------|------|
| 新闻舆情 | 情绪因子 | 中等 | 新闻网站 |
| 社交媒体 | 情绪因子 | 中等/付费 | Tushare积分 |
| 电商数据 | 消费因子 | 中等 | OpenWeatherMap |
| 招聘数据 | 成长因子 | 免费 | 招聘网站 |
| 专利数据 | 创新因子 | 付费 | 专利数据库 |

***

## 13. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本，整合免费数据源 |
| v1.1 | 2026-03-28 | 新增AK，增加另类数据、新闻舆情、天气数据等扩展 |
| v3.0 | 2026-04-05 | 修复编码问题，重新保存为UTF-8格式 |

---

**版本**: v3.0 | **更新**: 2026-04-05 | **状态**: ✅ 活跃

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
