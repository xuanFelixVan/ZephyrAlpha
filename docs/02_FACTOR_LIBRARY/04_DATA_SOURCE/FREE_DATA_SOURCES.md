---
module_id: DATA_FREE_SOURCES_001
version: 3.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-03
owner: ��ϯ�ĵ��ܹ�??standard_type: ����Դ��??applicable_scope: ����Դ��??compliance_level: רҵ��׼
parent_document: ./INDEX.md
implementation_status: ����??--- ����??
---

# T.01.DS001.�������Դ��??

> ����Դ��Alpha����
>
> **�����ĵ�**??
> - ���ĵ���[../../INDEX.md](../../03_TRADING_TACTICS/INDEX.md)
> - ���ӿ�������[FACTOR_MASTER_INDEX.md](IFIND/FACTOR_MASTER_INDEX.md)
> - ����Դ������[数据源索引](./INDEX.md)

***

## 1. ����Դ��??

| ��??| ���� |
|------|------|
| ���ӱ�� | T.01.DS001 |
| �������� | �������Դ��??|
| �������� | ����Դ�� |
| ����??| Baostock / AkShare / Efinance / Tushare / ���� / ��Ѷ |
| ����Ƶ�� | ��Ƶ/ʵʱ |

**��������**�����϶���������Դ������������A��������ϵ���������顢�����ʽ������ά��

**���ó���**�������������ס������о����ز�����׼??

***

## 2. ����Դ����

| ����??| �������� | ���� | �������� | ���� |
|--------|----------|------|----------|------|
| Baostock | 28+ | ??????| ��������ȫ�桢��ʷ�� | ��� |
| AkShare | 115+ | ??????| ����ȫ�桢ʵʱ�Ժ� | ��� |
| Efinance | 65+ | ???? | �ʽ������ݶ�??| ��� |
| Tushare | 35+ | ????| ����֡������??| ����� |
| ���˲ƾ� | 28+ | ????| ʵʱ���� | ��� |
| ��Ѷ�ƾ� | 21+ | ?? | �������� | ��� |

***

## 3. Baostock����Դ��28+����??

### 3.1 ��������??4����

```python
class BaostockQuote:
    """Baostock��������"""

    COLUMNS = {
        '��������': ['date', 'code', 'open', 'high', 'low', 'close', 'preclose'],
        '��������': ['volume', 'amount', 'turn', 'pctChg'],
        '��ֵ��??: ['peTTM', 'psTTM', 'pcfNcfTTM', 'pbMRQ'],
        '״̬��??: ['isST']
    }

    def get_daily(self, code, start_date, end_date):
        """
        ��ȡ������������

        Parameters:
            code: ��Ʊ���룬�� 'sh.600000'
            start_date: ��ʼ���ڣ�??'2024-01-01'
            end_date: �������ڣ��� '2024-12-31'

        Returns:
            DataFrame with columns: date, code, open, high, low, close, volume, amount, turn, pctChg, isST, peTTM, psTTM, pcfNcfTTM, pbMRQ
        """
        pass

    def get_realtime(self, codes):
        """
        ��ȡʵʱ����

        Parameters:
            codes: ��Ʊ�����б�

        Returns:
            DataFrame with realtime quote
        """
        pass
```

### 3.2 ��������??1����

```python
class BaostockFinance:
    """Baostock��������"""

    INDICATORS = {
        '����????: [
            'Ӫҵ����', 'Ӫҵ�ɱ�', 'Ӫҵ����',
            '�����ܶ�', '������', 'ÿ������', 'ROE'
        ],
        '�ʲ���ծ��7??: [
            '����??, '�����ʲ�', '�̶��ʲ�',
            '�ܸ�??, '������??, '�ɶ�Ȩ��', '�ʲ���ծ��'
        ],
        '�ֽ�����????: [
            '��Ӫ��ֽ�??, 'Ͷ�ʻ�ֽ�??,
            '���ʻ�ֽ�??, '�ֽ�����??
        ],
        'ҵ��Ԥ��3??: [
            'ҵ���䶯����', 'Ԥ�⾻��������', 'Ԥ�⾻��������'
        ]
    }

    def get_finance(self, code, start_date, end_date, statements='all'):
        """
        ��ȡ��������

        Parameters:
            code: ��Ʊ����
            start_date: ��ʼ��??
            end_date: ��������
            statements: 'all'/'income'/'balance'/'cash'

        Returns:
            DataFrame with financial data
        """
        pass

    def get_performance(self, start_date, end_date):
        """
        ��ȡҵ��Ԥ��/�챨

        Parameters:
            start_date: ��ʼ��??
            end_date: ��������

        Returns:
            DataFrame with performance preview
        """
        pass
```

### 3.3 ʹ��ʾ��

```python
import baostock as bs
import pandas as pd

# ��¼
lg = bs.login()
print(f'Login respond error_code:{lg.error_code}')
print(f'Login respond error_msg:{lg.error_msg}')

# ��ȡ��������
rs = bs.query_history_k_data_plus(
    "sh.600000",
    "date,code,open,high,low,close,volume,amount,pctChg",
    start_date='2024-01-01',
    end_date='2024-12-31',
    frequency="d"
)

# ת��ΪDataFrame
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
df = pd.DataFrame(data_list, columns=rs.fields)

# �ǳ�
bs.logout()

print(df.head())
```

***

## 4. AkShare����Դ��115+����??

### 4.1 A�����飨45����

```python
class AkShareQuote:
    """AkShare��������"""

    def stock_zh_a_spot_em(self):
        """
        ��ȡA��ʵʱ��??

        Returns:
            DataFrame with columns: ����, ����, ���¼�, �ǵ�?? �ǵ�??
            �ɽ�?? �ɽ�?? ���, ��?? ��?? ��, ����, ����, �����ʵ�
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
        ��ȡA����ʷ��??

        Parameters:
            symbol: ��Ʊ����
            period: 'daily'/'weekly'/'monthly'
            start_date: ��ʼ��??
            end_date: ��������
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
        ��ȡ����K����??

        Parameters:
            symbol: ��Ʊ����
            period: '1'/'5'/'15'/'30'/'60'
            adjust: 'qfq'/'hfq'/'none'

        Returns:
            DataFrame with minute data
        """
        pass
```

### 4.2 ��������??4����

```python
class AkShareFinance:
    """AkShare��������"""

    def stock_financial_report_sina(self, stock: str, symbol: str = "����??):
        """
        ��ȡ���񱨱�

        Parameters:
            stock: ��Ʊ����
            symbol: '����??/'�ʲ���ծ��'/'�ֽ�����??

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
        ��ȡ����ָ��

        Returns:
            DataFrame with ROE, EPS, etc.
        """
        pass
```

### 4.3 �г�����??9����

```python
class AkShareMarket:
    """AkShare�г�����"""

    def stock_lhb_detail_em(self, date: str = None):
        """
        ��ȡ��������??

        Parameters:
            date: �ϰ����ڣ��� '2024-01-15'

        Returns:
            DataFrame with columns: ����, ����, �ϰ�����, �ϰ�ԭ��,
            ������, �������, ��?? ����ϯλ, ����ϯλ
        """
        pass

    def stock_margin_detail(self, symbol: str = None, date: str = None):
        """
        ��ȡ������ȯ��ϸ

        Returns:
            DataFrame with �������, ��������?? ��ȯ���??
        """
        pass

    def stock_block_trade_em(self, start_date: str, end_date: str):
        """
        ��ȡ���ڽ�������

        Returns:
            DataFrame with �ɽ�?? �ɽ�?? �ɽ����, ���??
        """
        pass
```

### 4.4 ָ��������??

```python
class AkShareIndex:
    """AkShareָ������"""

    def index_zh_a_spot_em(self):
        """
        ��ȡָ��ʵʱ����

        Returns:
            DataFrame with ��Ҫָ��ʵʱ����
        """
        pass

    def index_zh_a_hist(self, symbol: str, period: str = "daily", start_date: str = None, end_date: str = None):
        """
        ��ȡָ����ʷ����

        Parameters:
            symbol: ָ�����룬�� '000001'����ָ֤����
            period: 'daily'/'weekly'/'monthly'

        Returns:
            DataFrame with index OHLCV
        """
        pass

    def stock_board_industry_name_em(self):
        """
        ��ȡ��ҵ����б�

        Returns:
            DataFrame with ��ҵ���ɷ�??
        """
        pass

    def stock_board_concept_name_em(self):
        """
        ��ȡ�������б�

        Returns:
            DataFrame with ������ɷ�??
        """
        pass
```

### 4.5 ʹ��ʾ��

```python
import akshare as ak
import pandas as pd

# ��ȡʵʱ����
df_spot = ak.stock_zh_a_spot_em()
print(df_spot[['����', '����', '���¼�', '�ǵ�??]].head())

# ��ȡ��ʷK??
df_hist = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"
)
print(df_hist.head())

# ��ȡ����??
df_lhb = ak.stock_lhb_detail_em(date="20240115")
print(df_lhb.head())

# ��ȡ��ҵ���
df_industry = ak.stock_board_industry_name_em()
print(df_industry.head())
```

***

## 5. Efinance����Դ��65+����??

### 5.1 ��Ʊ����??8����

```python
class EFinanceQuote:
    """EFinance��������"""

    def get_quote(self, codes):
        """
        ��ȡʵʱ����

        Parameters:
            codes: ��Ʊ�����б����� ['000001', '000002']

        Returns:
            DataFrame with realtime quote
        """
        pass

    def get_kline(self, code, start_date=None, end_date=None, klt='101'):
        """
        ��ȡK����??

        Parameters:
            code: ��Ʊ����
            start_date: ��ʼ��??
            end_date: ��������
            klt:  Kline type, '101'=����, '102'=����, '103'=����

        Returns:
            DataFrame with OHLCV data
        """
        pass
```

### 5.2 �ʽ�����??3����?������??

```python
class EFinanceMoneyFlow:
    """EFinance�ʽ�����??- ��������"""

    def get_individual_money_flow(self, stock: str, date: str = None):
        """
        ��ȡ�����ʽ�����

        Parameters:
            stock: ��Ʊ����
            date: ����

        Returns:
            DataFrame with columns:
            - ����������
            - ���󵥾�����
            - �󵥾�����
            - �е�������
            - С��������
        """
        pass

    def get_sector_money_flow(self, sector_type: str = "��ҵ", date: str = None):
        """
        ��ȡ����ʽ�����

        Parameters:
            sector_type: '��ҵ'/'����'
            date: ����

        Returns:
            DataFrame with columns:
            - �������
            - ����������
            - �ǵ�??
            - ����??
        """
        pass

    def get_north_money_flow(self, date: str = None):
        """
        ��ȡ�����ʽ�����

        Returns:
            DataFrame with columns:
            - ����
            - ����ͨ������
            - ���ͨ������
            - �����ʽ�ϼ�
        """
        pass
```

### 5.3 ʹ��ʾ��

```python
from efinance import stock
import pandas as pd

# ��ȡʵʱ����
df = stock.get_quote(['000001', '000002'])
print(df[['����', '����', '���¼�', '�ǵ�??]].head())

# ��ȡ�����ʽ�����
df_mf = stock.get_individual_money_flow('000001', '20240115')
print(df_mf)

# ��ȡ�����ʽ�
df_north = stock.get_north_money_flow('20240115')
print(df_north)
```

***

## 6. Tushare����Դ��35+����??

### 6.1 ��������??5����

```python
class TushareData:
    """Tushare����"""

    def get_daily(self, ts_code, start_date, end_date):
        """
        ��ȡ��������

        Returns:
            DataFrame with date, ts_code, open, high, low, close, vol, amount, pct_chg
        """
        pass

    def get_weekly(self, ts_code, start_date, end_date):
        """��ȡ��������"""
        pass

    def get_monthly(self, ts_code, start_date, end_date):
        """��ȡ��������"""
        pass

    def get_restricted_shares(self, start_date, end_date):
        """
        ��ȡ���۹ɽ����??

        Returns:
            DataFrame with ��Ʊ����, �������, �������, �������
        """
        pass
```

### 6.2 �������ݣ���2000����??

```python
class TusharePro:
    """Tushare Pro�������ݣ������??""

    def get_minute_data(self, ts_code, trade_date, freq='5min'):
        """
        ��ȡ��������

        Parameters:
            ts_code: ��Ʊ����
            trade_date: ��������
            freq: '1min'/'5min'/'15min'/'30min'/'60min'

        Returns:
            DataFrame with minute OHLCV
        """
        pass

    def get_financial(self, ts_code, period_type='annual'):
        """
        ��ȡ���񱨱�

        Parameters:
            ts_code: ��Ʊ����
            period_type: 'annual'/'quarter'

        Returns:
            DataFrame with ����?? �ʲ���ծ��, �ֽ�����??
        """
        pass

    def get_money_flow(self, ts_code, trade_date):
        """
        ��ȡ�ʽ�����

        Returns:
            DataFrame with ����������, ɢ��������
        """
        pass
```

### 6.3 ʹ��ʾ��

```python
import tushare as ts

# ����token
ts.set_token('your_token_here')
pro = ts.pro_api()

# ��ȡ��������
df = pro.daily(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20241231'
)
print(df.head())

# ��ȡ��������
df_fin = pro.fina_indicator(ts_code='000001.SZ')
print(df_fin[['ts_code', 'ann_date', 'roe', 'eps']].head())
```

***

## 7. ���ݴ洢�ܹ�

### 7.1 �洢Ŀ¼�ṹ

```python
DATA_STORAGE_STRUCTURE = {
    '��������': {
        '����': 'data/quotes/daily/{stock_code}.parquet',
        '����': 'data/quotes/weekly/{stock_code}.parquet',
        '����': 'data/quotes/monthly/{stock_code}.parquet',
        '5����': 'data/quotes/5min/{stock_code}_{date}.parquet',
        '15����': 'data/quotes/15min/{stock_code}_{date}.parquet',
        '30����': 'data/quotes/30min/{stock_code}_{date}.parquet',
        '60����': 'data/quotes/60min/{stock_code}_{date}.parquet',
    },
    '��������': {
        '����??: 'data/financial/income/{stock_code}_{period}.parquet',
        '�ʲ���ծ��': 'data/financial/balance/{stock_code}_{period}.parquet',
        '�ֽ�����??: 'data/financial/cashflow/{stock_code}_{period}.parquet',
        'ҵ��Ԥ��': 'data/financial/performance/{stock_code}_{date}.parquet',
    },
    '��ֵ��??: {
        'ÿ�չ�??: 'data/valuation/daily/{date}.parquet',
        '��ʷ��??: 'data/valuation/history/{stock_code}.parquet',
    },
    '�ʽ�����': {
        '�����ʽ�??: 'data/money_flow/individual/{stock_code}_{date}.parquet',
        '����ʽ�??: 'data/money_flow/sector/{sector}_{date}.parquet',
        '�����ʽ�': 'data/money_flow/north/{date}.parquet',
    },
    '�г�����': {
        '������ȯ': 'data/market/margin/{date}.parquet',
        '���ڽ���': 'data/market/block/{date}.parquet',
        '����??: 'data/market/lhb/{date}.parquet',
        '���۽��': 'data/market/restricted/{date}.parquet',
    }
}
```

### 7.2 ���ݸ���Ƶ��

| �������� | ����Ƶ�� | ��ȡ��ʽ |
|----------|----------|----------|
| ʵʱ���� | ʵʱ | ����/��ѶAPI |
| �������� | ����??| Baostock/AkShare |
| ����K??| ���� | AkShare/EFinance |
| �������� | ����/�걨 | Baostock/AkShare |
| �ʽ����� | ��Ƶ | EFinance�����ң� |
| ����??| ���� | AkShare |
| ������ȯ | ��Ƶ | AkShare |

***

## 8. ����Դѡ����

### 8.1 ������������ѷ�����

```python
RECOMMENDED_FREE_SETUP = {
    '��������': 'Baostock + AkShare',
    '��������': 'Baostock',
    '�ʽ�����': 'EFinance',
    '�г�����': 'AkShare',
    'ʵʱ����': 'AkShare + ����',
    'ָ������': 'AkShare'
}
```

### 8.2 ��������??

| ����??| ������� | �Ƽ�����??| ��Ҫ??|
|--------|----------|------------|--------|
| P0 | �۸�/�ɽ�??| Baostock/AkShare | ??????|
| P0 | �������� | Baostock | ??????|
| P1 | �ʽ����� | EFinance | ??????|
| P1 | ����??| AkShare | ???? |
| P2 | ������ȯ | AkShare | ????|
| P2 | ָ���ɷ� | AkShare | ????|
| P3 | ������� | AkShare | ?? |

***

## 9. Pythonʵ��

```python
import pandas as pd
from typing import Optional, List, Dict
import warnings
warnings.filterwarnings('ignore')

class DataSourceIntegrator:
    """
    �������Դ������
    ͳһ�ӿڻ�ȡ�������Դ������
    """

    def __init__(self):
        self.baostock = None
        self.akshare = None
        self.efinance = None
        self.tushare = None

    def init_baostock(self):
        """��ʼ��Baostock"""
        try:
            import baostock as bs
            lg = bs.login()
            if lg.error_code == '0':
                self.baostock = bs
                print(f"Baostock��¼�ɹ�")
            else:
                print(f"Baostock��¼ʧ��: {lg.error_msg}")
        except ImportError:
            print("�밲װbaostock: pip install baostock")

    def init_akshare(self):
        """��ʼ��AkShare"""
        try:
            import akshare as ak
            self.akshare = ak
            print(f"AkShare��ʼ����??)
        except ImportError:
            print("�밲װakshare: pip install akshare")

    def init_efinance(self):
        """��ʼ��EFinance"""
        try:
            from efinance import stock
            self.efinance = stock
            print(f"EFinance��ʼ����??)
        except ImportError:
            print("�밲װefinance: pip install efinance")

    def get_daily_quote(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        ��ȡ�������飨����Baostock��ʧ����AkShare??

        Parameters:
            code: ��Ʊ���룬�� '000001'
            start_date: ��ʼ���ڣ�??'2024-01-01'
            end_date: �������ڣ��� '2024-12-31'

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
                print(f"Baostock��ȡʧ��: {e}")

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
                print(f"AkShare��ȡʧ��: {e}")

        return df

    def get_money_flow(self, code: str, date: str) -> Optional[pd.DataFrame]:
        """
        ��ȡ�ʽ�����EFinance����??

        Parameters:
            code: ��Ʊ����
            date: ����

        Returns:
            DataFrame with ����/����??��/�е�/С��������
        """
        if self.efinance:
            try:
                df = self.efinance.get_individual_money_flow(code, date)
                return df
            except Exception as e:
                print(f"EFinance��ȡʧ��: {e}")

        return None

    def get_lhb(self, date: str) -> Optional[pd.DataFrame]:
        """
        ��ȡ��������??

        Parameters:
            date: ����

        Returns:
            DataFrame with ��������??
        """
        if self.akshare:
            try:
                df = self.akshare.stock_lhb_detail_em(date=date)
                return df
            except Exception as e:
                print(f"��ȡ������ʧ?? {e}")

        return None

    def get_north_money(self, date: str) -> Optional[pd.DataFrame]:
        """
        ��ȡ�����ʽ�

        Parameters:
            date: ����

        Returns:
            DataFrame with ����??���ͨ������
        """
        if self.efinance:
            try:
                df = self.efinance.get_north_money_flow(date)
                return df
            except Exception as e:
                print(f"��ȡ�����ʽ�ʧ��: {e}")

        if self.akshare:
            try:
                df = self.akshare.stock_hsgt_north_flow_em()
                return df
            except Exception as e:
                print(f"AkShare��ȡ�����ʽ�ʧ��: {e}")

        return None

    def __del__(self):
        """����ʱ�ǳ�Baostock"""
        if self.baostock:
            self.baostock.logout()
```

***

## 10. ʹ��ʾ��

```python
# ��ʼ������Դ
integrator = DataSourceIntegrator()
integrator.init_baostock()
integrator.init_akshare()
integrator.init_efinance()

# ��ȡ��������
df_quote = integrator.get_daily_quote('000001', '2024-01-01', '2024-12-31')
print(f"��ȡ����: {len(df_quote)} ??)

# ��ȡ�ʽ�����
df_mf = integrator.get_money_flow('000001', '2024-01-15')
print(f"�ʽ�����: {df_mf}")

# ��ȡ����??
df_lhb = integrator.get_lhb('2024-01-15')
print(f"����?? {len(df_lhb)} ??)

# ��ȡ�����ʽ�
df_north = integrator.get_north_money('2024-01-15')
print(f"�����ʽ�: {df_north}")
```

***

## 11. ע������

1. **API����**���������Դ�з���Ƶ�����ƣ���������ʱ
2. **��������**��������ݿ��ܴ���ȱʧ���ӳ٣���У��
3. **�Ϲ�ʹ��**�������ظ�����Դ��ʹ����??
4. **���ݱ���**����Ҫ���ݽ��鱾�ر�??

***

## 12. �������ݿ��

> **��Դ**����������רҵ�ֲ㷽��_v3.0 ��¼AK
>
> **˵��**������������רҵ������������ҪAlpha��Դ�����˿����߿ɴ��������ݿ�ʼ�ͳɱ�����

### 12.1 ������������

| �������� | ����??| ����Ƶ�� | AlphaǱ�� | ���˿ɻ�ȡ??|
|:---------|:-------|:---------|:---------|:------------|
| **��������** | ����/�罻ý�� | ʵʱ | ???? | ??????��� |
| **��������** | ����/֧�� | ÿ�� | ????| ????���� |
| **��������** | ����/��??| ÿ�� | ???? | ?? ���� |
| **��Դ����** | ����/��ҵ�õ� | ÿ�� | ????| ?? ���� |
| **��������** | ����/���� | ʵʱ | ????| ??????��� |
| **��������** | ͣ��??�������� | ÿ�� | ??????| ??���� |

### 12.2 �������ݴ��������˿ɻ�ȡ??

```python
class NewsSentimentProvider:
    """
    ���������ṩ??
    ���˿����߿�ʹ��Tushare/akshare��ȡ��������
    """

    def __init__(self):
        self.tushare = None
        self.akshare = None

    def init_tushare(self, token: str):
        """��ʼ��Tushare"""
        try:
            import tushare as ts
            ts.set_token(token)
            self.tushare = ts.pro_api()
        except ImportError:
            print("�밲װtushare: pip install tushare")

    def get_stock_news(self, stock_code: str, date: str) -> pd.DataFrame:
        """
        ��ȡ��������

        Parameters:
            stock_code: ��Ʊ���룬�� '000001'
            date: ���ڣ��� '20240115'

        Returns:
            DataFrame with ���ű���, ����ʱ��, ��������, ��е÷�
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
                print(f"��ȡ����ʧ��: {e}")

        return pd.DataFrame()

    def calc_sentiment(self, news_df: pd.DataFrame) -> float:
        """
        ������е÷�

        Returns:
            float: -1.0 (����) ~ 1.0 (����)
        """
        if news_df.empty:
            return 0.0

        positive_keywords = ['����', 'ӯ��', 'ͻ��', '����', '�б�', '��Ԥ??]
        negative_keywords = ['����', '�µ�', '����', '����', 'Υ��', 'Ԥ��']

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

### 12.3 ������������??

```python
class AlternativeDataAdapter:
    """
    ������������??
    ���϶�����������Դ�����ۺ���??
    """

    def __init__(self):
        self.news_provider = NewsSentimentProvider()
        self.data_sources = {}

    def add_provider(self, name: str, provider):
        """���������ṩ??""
        self.data_sources[name] = provider

    def calc_alternative_signal(self, stock_code: str) -> dict:
        """
        �������������ۺ��ź�

        Returns:
            dict: {
                'news_sentiment': float,      # ����÷�
                'logistics_signal': float,    # �����ź�
                'consumer_signal': float,     # �����ź�
                'composite': float             # �ۺ��ź�
            }
        """
        signals = {}

        try:
            news_df = self.news_provider.get_stock_news(stock_code)
            signals['news_sentiment'] = self.news_provider.calc_sentiment(news_df)
        except Exception as e:
            print(f"�������ݻ�ȡʧ��: {e}")
            signals['news_sentiment'] = None

        for name, provider in self.data_sources.items():
            try:
                data = provider.get_data(stock_code)
                signals[name] = self.process_data(name, data)
            except Exception as e:
                print(f"{name}���ݻ�ȡʧ��: {e}")
                signals[name] = None

        valid_signals = [v for v in signals.values() if v is not None]
        if valid_signals:
            signals['composite'] = np.mean(valid_signals)
        else:
            signals['composite'] = None

        return signals

    def process_data(self, name: str, data) -> float:
        """�����������ݷ����ź�??""
        return 0.0
```

### 12.4 �������ݣ���ѿɻ�ȡ??

```python
class WeatherDataProvider:
    """
    ���������ṩ??
    �������ݶ�ũ??��Դ/���ѵȰ����Ӱ��
    """

    def get_weather(self, city: str, date: str) -> dict:
        """
        ��ȡ��������

        Returns:
            dict: {
                'temperature': float,    # �¶�
                'precipitation': float,  # ��ˮ??
                'weather_type': str      # ��������
            }
        """
        return {
            'temperature': 25.0,
            'precipitation': 0.0,
            'weather_type': '??
        }

    def calc_weather_factor(self, sector: str, weather_data: dict) -> float:
        """
        ���������԰���Ӱ������

        Parameters:
            sector: �������
            weather_data: ��������

        Returns:
            float: Ӱ�����ӣ���??-1.0 ~ 1.0
        """
        sector_weather_map = {
            'ũҵ': ['precipitation', 'temperature'],
            '����': ['temperature'],
            'ú̿': ['temperature'],
            '����': ['temperature', 'precipitation']
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

### 12.5 ���˿����߽�??

| �������� | ��ȡ�Ѷ� | �ɱ� | ���� |
|---------|---------|------|------|
| �������� | ??| ��� | ����ʵ�� |
| �罻ý�� | ??| ���/���� | Tushare���� |
| �������� | ??| ��� | OpenWeatherMap |
| �������� | ??| ���� | �ݻ� |
| �������� | ���� | ���� | ����??|

***

## 13. ���¼�¼

| �汾 | ���� | ������� |
|------|------|----------|
| v1.0 | 2026-03-28 | ��ʼ�汾�����ϸ�¼AA����Դ������??|
| v1.1 | 2026-03-28 | ���ϸ�¼AK�������ݿ�ܣ�������??�������ݴ��� |


