# T.01.DS001.免费数据源整合

> 数据源类Alpha因子
>
> **配套文档**：
> - 主文档：[SPEC.md](../../../../SPEC.md)
> - 因子库索引：[因子库主索引](./因子主索引.md)
> - 数据源索引：[数据源 README](./README.md)

***

## 1. 数据源概述

| 属性 | 内容 |
|------|------|
| 因子编号 | T.01.DS001 |
| 因子名称 | 免费数据源整合 |
| 因子类型 | 数据源类 |
| 数据源 | Baostock / AkShare / Efinance / Tushare / 新浪 / 腾讯 |
| 更新频率 | 日频/实时 |

**核心理念**：整合多个免费数据源，构建完整的A股数据体系，覆盖行情、财务、资金、舆情等维度

**适用场景**：个人量化交易、因子研究、回测数据准备

***

## 2. 数据源总览

| 数据源 | 因子数量 | 评级 | 核心优势 | 费用 |
|--------|----------|------|----------|------|
| Baostock | 28+ | ⭐⭐⭐⭐⭐ | 财务数据全面、历史长 | 免费 |
| AkShare | 115+ | ⭐⭐⭐⭐⭐ | 覆盖全面、实时性好 | 免费 |
| Efinance | 65+ | ⭐⭐⭐⭐ | 资金流数据独家 | 免费 |
| Tushare | 35+ | ⭐⭐⭐ | 需积分、深度数据 | 需积分 |
| 新浪财经 | 28+ | ⭐⭐⭐ | 实时行情 | 免费 |
| 腾讯财经 | 21+ | ⭐⭐ | 基础数据 | 免费 |

***

## 3. Baostock数据源（28+因子）

### 3.1 行情数据（14个）

```python
class BaostockQuote:
    """Baostock行情数据"""

    COLUMNS = {
        '基础行情': ['date', 'code', 'open', 'high', 'low', 'close', 'preclose'],
        '交易数据': ['volume', 'amount', 'turn', 'pctChg'],
        '估值数据': ['peTTM', 'psTTM', 'pcfNcfTTM', 'pbMRQ'],
        '状态数据': ['isST']
    }

    def get_daily(self, code, start_date, end_date):
        """
        获取日线行情数据

        Parameters:
            code: 股票代码，如 'sh.600000'
            start_date: 开始日期，如 '2024-01-01'
            end_date: 结束日期，如 '2024-12-31'

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

### 3.2 财务数据（21个）

```python
class BaostockFinance:
    """Baostock财务数据"""

    INDICATORS = {
        '利润表7个': [
            '营业收入', '营业成本', '营业利润',
            '利润总额', '净利润', '每股收益', 'ROE'
        ],
        '资产负债表7个': [
            '总资产', '流动资产', '固定资产',
            '总负债', '流动负债', '股东权益', '资产负债率'
        ],
        '现金流量表4个': [
            '经营活动现金流', '投资活动现金流',
            '筹资活动现金流', '现金净增加额'
        ],
        '业绩预告3个': [
            '业绩变动类型', '预测净利润下限', '预测净利润上限'
        ]
    }

    def get_finance(self, code, start_date, end_date, statements='all'):
        """
        获取财务数据

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

# 获取日线数据
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

## 4. AkShare数据源（115+因子）

### 4.1 A股行情（45个）

```python
class AkShareQuote:
    """AkShare行情数据"""

    def stock_zh_a_spot_em(self):
        """
        获取A股实时行情

        Returns:
            DataFrame with columns: 代码, 名称, 最新价, 涨跌幅, 涨跌额,
            成交量, 成交额, 振幅, 最高, 最低, 今开, 昨收, 量比, 换手率等
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

### 4.2 财务数据（24个）

```python
class AkShareFinance:
    """AkShare财务数据"""

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

### 4.3 市场数据（29个）

```python
class AkShareMarket:
    """AkShare市场数据"""

    def stock_lhb_detail_em(self, date: str = None):
        """
        获取龙虎榜明细

        Parameters:
            date: 上榜日期，如 '2024-01-15'

        Returns:
            DataFrame with columns: 代码, 名称, 上榜日期, 上榜原因,
            买入金额, 卖出金额, 净额, 买入席位, 卖出席位
        """
        pass

    def stock_margin_detail(self, symbol: str = None, date: str = None):
        """
        获取融资融券明细

        Returns:
            DataFrame with 融资余额, 融资买入额, 融券余额等
        """
        pass

    def stock_block_trade_em(self, start_date: str, end_date: str):
        """
        获取大宗交易数据

        Returns:
            DataFrame with 成交价, 成交量, 成交金额, 溢价率
        """
        pass
```

### 4.4 指数与板块数据

```python
class AkShareIndex:
    """AkShare指数数据"""

    def index_zh_a_spot_em(self):
        """
        获取指数实时行情

        Returns:
            DataFrame with 主要指数实时数据
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
            DataFrame with 行业板块成分股
        """
        pass

    def stock_board_concept_name_em(self):
        """
        获取概念板块列表

        Returns:
            DataFrame with 概念板块成分股
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

# 获取历史K线
df_hist = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"
)
print(df_hist.head())

# 获取龙虎榜
df_lhb = ak.stock_lhb_detail_em(date="20240115")
print(df_lhb.head())

# 获取行业板块
df_industry = ak.stock_board_industry_name_em()
print(df_industry.head())
```

***

## 5. Efinance数据源（65+因子）

### 5.1 股票行情（28个）

```python
class EFinanceQuote:
    """EFinance行情数据"""

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

### 5.2 资金流向（13个）✨独家优势

```python
class EFinanceMoneyFlow:
    """EFinance资金流数据 - 独家优势"""

    def get_individual_money_flow(self, stock: str, date: str = None):
        """
        获取个股资金流向

        Parameters:
            stock: 股票代码
            date: 日期

        Returns:
            DataFrame with columns:
            - 机构净流入
            - 超大单净流入
            - 大单净流入
            - 中单净流入
            - 小单净流入
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
            - 机构净流入
            - 涨跌幅
            - 领涨股
        """
        pass

    def get_north_money_flow(self, date: str = None):
        """
        获取北向资金流向

        Returns:
            DataFrame with columns:
            - 日期
            - 沪股通净流入
            - 深股通净流入
            - 北向资金合计
        """
        pass
```

### 5.3 使用示例

```python
from efinance import stock
import pandas as pd

# 获取实时行情
df = stock.get_quote(['000001', '000002'])
print(df[['代码', '名称', '最新价', '涨跌幅']].head())

# 获取个股资金流向
df_mf = stock.get_individual_money_flow('000001', '20240115')
print(df_mf)

# 获取北向资金
df_north = stock.get_north_money_flow('20240115')
print(df_north)
```

***

## 6. Tushare数据源（35+因子）

### 6.1 基础数据（25个）

```python
class TushareData:
    """Tushare数据"""

    def get_daily(self, ts_code, start_date, end_date):
        """
        获取日线行情

        Returns:
            DataFrame with date, ts_code, open, high, low, close, vol, amount, pct_chg
        """
        pass

    def get_weekly(self, ts_code, start_date, end_date):
        """获取周线数据"""
        pass

    def get_monthly(self, ts_code, start_date, end_date):
        """获取月线数据"""
        pass

    def get_restricted_shares(self, start_date, end_date):
        """
        获取限售股解禁数据

        Returns:
            DataFrame with 股票代码, 解禁日期, 解禁数量, 解禁比例
        """
        pass
```

### 6.2 进阶数据（需2000积分）

```python
class TusharePro:
    """Tushare Pro进阶数据（需积分）"""

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
        获取资金流向

        Returns:
            DataFrame with 机构净流入, 散户净流入
        """
        pass
```

### 6.3 使用示例

```python
import tushare as ts

# 设置token
ts.set_token('your_token_here')
pro = ts.pro_api()

# 获取日线数据
df = pro.daily(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20241231'
)
print(df.head())

# 获取财务数据
df_fin = pro.fina_indicator(ts_code='000001.SZ')
print(df_fin[['ts_code', 'ann_date', 'roe', 'eps']].head())
```

***

## 7. 数据存储架构

### 7.1 存储目录结构

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
        '每日估值': 'data/valuation/daily/{date}.parquet',
        '历史估值': 'data/valuation/history/{stock_code}.parquet',
    },
    '资金数据': {
        '个股资金流': 'data/money_flow/individual/{stock_code}_{date}.parquet',
        '板块资金流': 'data/money_flow/sector/{sector}_{date}.parquet',
        '北向资金': 'data/money_flow/north/{date}.parquet',
    },
    '市场数据': {
        '融资融券': 'data/market/margin/{date}.parquet',
        '大宗交易': 'data/market/block/{date}.parquet',
        '龙虎榜': 'data/market/lhb/{date}.parquet',
        '限售解禁': 'data/market/restricted/{date}.parquet',
    }
}
```

### 7.2 数据更新频率

| 数据类型 | 更新频率 | 获取方式 |
|----------|----------|----------|
| 实时行情 | 实时 | 新浪/腾讯API |
| 日线行情 | 收盘后 | Baostock/AkShare |
| 分钟K线 | 盘中 | AkShare/EFinance |
| 财务数据 | 季报/年报 | Baostock/AkShare |
| 资金流向 | 日频 | EFinance（独家） |
| 龙虎榜 | 次日 | AkShare |
| 融资融券 | 日频 | AkShare |

***

## 8. 数据源选择建议

### 8.1 个人量化（免费方案）

```python
RECOMMENDED_FREE_SETUP = {
    '行情数据': 'Baostock + AkShare',
    '财务数据': 'Baostock',
    '资金流向': 'EFinance',
    '市场数据': 'AkShare',
    '实时行情': 'AkShare + 新浪',
    '指数数据': 'AkShare'
}
```

### 8.2 因子优先级

| 优先级 | 因子类别 | 推荐数据源 | 重要性 |
|--------|----------|------------|--------|
| P0 | 价格/成交量 | Baostock/AkShare | ⭐⭐⭐⭐⭐ |
| P0 | 财务数据 | Baostock | ⭐⭐⭐⭐⭐ |
| P1 | 资金流向 | EFinance | ⭐⭐⭐⭐⭐ |
| P1 | 龙虎榜 | AkShare | ⭐⭐⭐⭐ |
| P2 | 融资融券 | AkShare | ⭐⭐⭐ |
| P2 | 指数成分 | AkShare | ⭐⭐⭐ |
| P3 | 宏观数据 | AkShare | ⭐⭐ |

***

## 9. Python实现

```python
import pandas as pd
from typing import Optional, List, Dict
import warnings
warnings.filterwarnings('ignore')

class DataSourceIntegrator:
    """
    免费数据源整合器
    统一接口获取多个数据源的数据
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
        获取日线行情（优先Baostock，失败用AkShare）

        Parameters:
            code: 股票代码，如 '000001'
            start_date: 开始日期，如 '2024-01-01'
            end_date: 结束日期，如 '2024-12-31'

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
        获取资金流向（EFinance独家）

        Parameters:
            code: 股票代码
            date: 日期

        Returns:
            DataFrame with 机构/超大单/大单/中单/小单净流入
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
            DataFrame with 沪股通/深股通净流入
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
        """析构时登出Baostock"""
        if self.baostock:
            self.baostock.logout()
```

***

## 10. 使用示例

```python
# 初始化数据源
integrator = DataSourceIntegrator()
integrator.init_baostock()
integrator.init_akshare()
integrator.init_efinance()

# 获取日线行情
df_quote = integrator.get_daily_quote('000001', '2024-01-01', '2024-12-31')
print(f"获取行情: {len(df_quote)} 条")

# 获取资金流向
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

1. **API限制**：免费数据源有访问频率限制，需添加延时
2. **数据质量**：免费数据可能存在缺失或延迟，需校验
3. **合规使用**：请遵守各数据源的使用条款
4. **数据备份**：重要数据建议本地备份

***

## 12. 另类数据框架

> **来源**：量化策略专业分层方案_v3.0 附录AK
>
> **说明**：另类数据是专业量化机构的重要Alpha来源，个人开发者可从舆情数据开始低成本尝试

### 12.1 另类数据类型

| 数据类型 | 数据源 | 更新频率 | Alpha潜力 | 个人可获取性 |
|:---------|:-------|:---------|:---------|:------------|
| **舆情数据** | 新闻/社交媒体 | 实时 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ 免费 |
| **消费数据** | 电商/支付 | 每日 | ⭐⭐⭐ | ⭐⭐⭐ 付费 |
| **物流数据** | 货运/快递 | 每周 | ⭐⭐⭐⭐ | ⭐⭐ 付费 |
| **能源数据** | 电网/工业用电 | 每日 | ⭐⭐⭐ | ⭐⭐ 付费 |
| **气象数据** | 天气/气温 | 实时 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ 免费 |
| **卫星数据** | 停车场/商铺人流 | 每日 | ⭐⭐⭐⭐⭐ | ⭐ 昂贵 |

### 12.2 舆情数据处理（个人可获取）

```python
class NewsSentimentProvider:
    """
    舆情数据提供商
    个人开发者可使用Tushare/akshare获取新闻数据
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
        获取个股新闻

        Parameters:
            stock_code: 股票代码，如 '000001'
            date: 日期，如 '20240115'

        Returns:
            DataFrame with 新闻标题, 发布时间, 新闻内容, 情感得分
        """
        if self.tushare:
            try:
                df = self.tushave.news(
                    token=self.tushare,
                    symbol=stock_code,
                    date=date
                )
                return df
            except Exception as e:
                print(f"获取新闻失败: {e}")

        return pd.DataFrame()

    def calc_sentiment(self, news_df: pd.DataFrame) -> float:
        """
        计算情感得分

        Returns:
            float: -1.0 (负面) ~ 1.0 (正面)
        """
        if news_df.empty:
            return 0.0

        positive_keywords = ['增长', '盈利', '突破', '合作', '中标', '超预期']
        negative_keywords = ['亏损', '下跌', '风险', '调查', '违规', '预警']

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
    另类数据适配器
    整合多种另类数据源计算综合信号
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
                'news_sentiment': float,      # 舆情得分
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
            print(f"舆情数据获取失败: {e}")
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
        """处理各类数据返回信号值"""
        return 0.0
```

### 12.4 气象数据（免费可获取）

```python
class WeatherDataProvider:
    """
    气象数据提供商
    天气数据对农业/能源/消费等板块有影响
    """

    def get_weather(self, city: str, date: str) -> dict:
        """
        获取天气数据

        Returns:
            dict: {
                'temperature': float,    # 温度
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
        计算天气对板块的影响因子

        Parameters:
            sector: 板块名称
            weather_data: 天气数据

        Returns:
            float: 影响因子，范围 -1.0 ~ 1.0
        """
        sector_weather_map = {
            '农业': ['precipitation', 'temperature'],
            '电力': ['temperature'],
            '煤炭': ['temperature'],
            '消费': ['temperature', 'precipitation']
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

### 12.5 个人开发者建议

| 数据类型 | 获取难度 | 成本 | 建议 |
|---------|---------|------|------|
| 新闻舆情 | 低 | 免费 | 优先实现 |
| 社交媒体 | 中 | 免费/付费 | Tushare爬虫 |
| 天气数据 | 低 | 免费 | OpenWeatherMap |
| 电商数据 | 高 | 付费 | 暂缓 |
| 卫星数据 | 极高 | 昂贵 | 不建议 |

***

## 13. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本，整合附录AA数据源因子体系 |
| v1.1 | 2026-03-28 | 整合附录AK另类数据框架，补充舆情/气象数据处理 |
