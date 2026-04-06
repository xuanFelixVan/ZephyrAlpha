---
module_id: DATA_ADAPTERS_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-05
owner: 首席文档架构师
standard_type: 数据源文档
applicable_scope: 数据源适配器
compliance_level: 专业标准
parent_document: ./INDEX.md
implementation_status: 进行中
responsibility:
  - 数据质量 (Layer 1)
---

# 数据源适配器

## 文档职责说明

**本文档职责**: 数据源适配器架构设计
- 定义统一数据源接口规范
- 管理多数据源优先级和降级策略
- 提供数据源健康检查机制

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 免费数据源规格 | [FREE_DATA_SOURCES.md](./FREE_DATA_SOURCES.md) | 详细规格 | 免费数据源的具体接口定义 |
| 数据源索引 | [INDEX.md](./INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: 定义统一适配器接口和架构
- ❌ 本文档不负责: 具体数据源的接口细节（由 FREE_DATA_SOURCES.md 负责）

> 多数据源统一接入管理，支持股票、期货、期权、宏观等各类数据

---

## 1. 数据源概览

| 数据源 | 类型 | 数据质量 | 主要用途 | 权限 |
|--------|------|---------|---------|------|
| Baostock | 官方API | ⭐⭐⭐⭐⭐ | 历史行情、财务数据、复权因子 | 免费注册 |
| AkShare | 开源库 | ⭐⭐⭐⭐ | 实时行情、概念板块、资金流向 | 完全免费 |
| Efinance | 开源库 | ⭐⭐⭐⭐ | 资金流向、北向资金、实时行情 | 完全免费 |
| Tushare Pro | 官方API | ⭐⭐⭐⭐⭐ | 深度数据、因子数据、专业指标 | 积分制 |
| 新浪财经 | 网络API | ⭐⭐⭐ | 实时行情备用、历史数据 | 免费 |
| 腾讯财经 | 网络API | ⭐⭐⭐ | 实时行情备用、基础数据 | 免费 |

---

## 2. 多数据源适配器设计

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@dataclass
class DataSourceConfig:
    """数据源配置"""
    name: str
    source_type: str              # 'api', 'web', 'database'
    priority: int                 # 优先级，数字越小优先级越高
    rate_limit: Optional[int]     # 速率限制（请求/秒）
    timeout: int = 30            # 超时时间（秒）
    retry_count: int = 3         # 重试次数
    is_available: bool = True    # 是否可用

class DataSource(ABC):
    """数据源基类"""

    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.name = config.name

    @abstractmethod
    def fetch_stock_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        freq: str = 'daily'
    ) -> pd.DataFrame:
        """获取股票OHLCV数据"""
        pass

    @abstractmethod
    def fetch_financial_data(
        self,
        symbol: str,
        report_type: str = 'annual'
    ) -> pd.DataFrame:
        """获取财务报表数据"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """健康检查"""
        pass
```

---

## 3. 具体数据源实现

### 3.1 Baostock 数据源

```python
import baostock as bs

class BaostockDataSource(DataSource):
    """Baostock 数据源

    适用场景：
    - 历史行情（日线、周线、月线）
    - 复权数据（前后复权）
    - 财务报表（资产负债表、利润表、现金流量表）
    - 融资融券数据
    """

    def __init__(self, config: DataSourceConfig = None):
        if config is None:
            config = DataSourceConfig(
                name='Baostock',
                source_type='api',
                priority=1,
                rate_limit=100
            )
        super().__init__(config)
        self.login()

    def login(self):
        """登录Baostock"""
        bs.login()

    def logout(self):
        """登出"""
        bs.logout()

    def fetch_stock_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        freq: str = 'daily',
        adjust: str = 'qfq'
    ) -> pd.DataFrame:
        """获取股票行情数据

        参数:
            symbol: 股票代码，如 '600000.SH'
            start_date: 开始日期，如 '2026-01-01'
            end_date: 结束日期，如 '2026-03-28'
            freq: 频率，'d'=日线，'w'=周线，'m'=月线
            adjust: 复权类型，'qfq'=前复权，'hfq'=后复权，''=不复权
        """
        code = self._normalize_symbol(symbol)

        fields = 'date,code,open,high,low,close,volume,amount'

        rs = bs.query_history_k_data_plus(
            code,
            fields,
            start_date=start_date,
            end_date=end_date,
            frequency=freq,
            adjust=adjust
        )

        data = []
        while rs.error_code == '0' and rs.next():
            data.append(rs.get_row_data())

        df = pd.DataFrame(data, columns=rs.fields)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

        return df

    def fetch_financial_data(
        self,
        symbol: str,
        report_type: str = 'annual'
    ) -> Dict[str, pd.DataFrame]:
        """获取财务报表

        返回:
            包含 balance_sheet, income_statement, cash_flow 的字典
        """
        code = self._normalize_symbol(symbol)

        # 资产负债表
        balance_rs = bs.query_balance_sheet(code, year=2024, quarter=4)
        balance_df = self._rs_to_df(balance_rs)

        # 利润表
        income_rs = bs.query_profit_statement(code, year=2024, quarter=4)
        income_df = self._rs_to_df(income_rs)

        # 现金流量表
        cash_rs = bs.query_cash_flow_statement(code, year=2024, quarter=4)
        cash_df = self._rs_to_df(cash_rs)

        return {
            'balance_sheet': balance_df,
            'income_statement': income_df,
            'cash_flow': cash_df
        }

    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码"""
        if symbol.endswith('.SH') or symbol.endswith('.SZ'):
            return symbol
        elif symbol.startswith('6'):
            return f"{symbol}.SH"
        else:
            return f"{symbol}.SZ"

    def _rs_to_df(self, rs) -> pd.DataFrame:
        """结果集转DataFrame"""
        data = []
        while rs.error_code == '0' and rs.next():
            data.append(rs.get_row_data())
        return pd.DataFrame(data, columns=rs.fields)

    def health_check(self) -> bool:
        try:
            bs.query_history_k_data_plus(
                '600000.SH',
                'date,close',
                start_date='2026-03-27',
                end_date='2026-03-28'
            )
            return True
        except:
            return False
```

### 3.2 AkShare 数据源

```python
import akshare as ak

class AkShareDataSource(DataSource):
    """AkShare 数据源

    适用场景：
    - 实时行情
    - 概念板块、行业分析
    - 资金流向
    - 宏观数据
    """

    def __init__(self, config: DataSourceConfig = None):
        if config is None:
            config = DataSourceConfig(
                name='AkShare',
                source_type='web',
                priority=2,
                rate_limit=10
            )
        super().__init__(config)

    def fetch_realtime_quote(self, symbol: str) -> Dict:
        """获取实时行情"""
        try:
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == symbol]
            if not stock.empty:
                return stock.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
        return {}

    def fetch_concept_board(self) -> pd.DataFrame:
        """获取概念板块数据"""
        try:
            return ak.stock_board_concept_name_em()
        except Exception as e:
            logger.error(f"获取概念板块失败: {e}")
            return pd.DataFrame()

    def fetch_industry_board(self) -> pd.DataFrame:
        """获取行业板块数据"""
        try:
            return ak.stock_board_industry_name_em()
        except Exception as e:
            logger.error(f"获取行业板块失败: {e}")
            return pd.DataFrame()

    def fetch_money_flow(
        self,
        symbol: str,
        market: str = 'A'
    ) -> pd.DataFrame:
        """获取资金流向"""
        try:
            return ak.stock_individual_fund_flow(stock_code=symbol, market=market)
        except Exception as e:
            logger.error(f"获取资金流向失败: {e}")
            return pd.DataFrame()

    def fetch_macro_data(self, indicator: str) -> pd.DataFrame:
        """获取宏观数据"""
        macro_funcs = {
            'gdp': ak.macro_china_gdp,
            'cpi': ak.macro_china_cpi,
            'ppi': ak.macro_china_ppi,
            'pmi': ak.macro_china_pmi,
            'lpr': ak.macro_china_lpr,
        }

        func = macro_funcs.get(indicator)
        if func:
            try:
                return func()
            except Exception as e:
                logger.error(f"获取宏观数据失败: {e}")
        return pd.DataFrame()

    def health_check(self) -> bool:
        try:
            ak.stock_zh_a_spot_em()
            return True
        except:
            return False
```

---

## 4. 智能数据源选择器

```python
class SmartDataSourceSelector:
    """智能数据源选择器

    根据数据类型、质量、可用性自动选择最优数据源
    """

    def __init__(self):
        self.sources: Dict[str, List[DataSource]] = {}
        self.quality_stats: Dict[str, Dict] = {}
        self._register_default_sources()

    def _register_default_sources(self):
        """注册默认数据源"""
        self.register_source('ohlcv', BaostockDataSource())
        self.register_source('ohlcv', AkShareDataSource())
        self.register_source('financial', BaostockDataSource())
        self.register_source('money_flow', AkShareDataSource())

    def register_source(self, data_type: str, source: DataSource):
        """注册数据源"""
        if data_type not in self.sources:
            self.sources[data_type] = []
        self.sources[data_type].append(source)

    def fetch_data(
        self,
        data_type: str,
        params: Dict,
        preferred_source: str = None
    ) -> pd.DataFrame:
        """获取数据，自动选择最优源

        参数:
            data_type: 数据类型，如 'ohlcv', 'financial'
            params: 获取参数
            preferred_source: 首选数据源名称
        """
        if data_type not in self.sources:
            raise ValueError(f"不支持的数据类型: {data_type}")

        sources = self.sources[data_type]

        # 按优先级排序
        sources = sorted(sources, key=lambda s: s.config.priority)

        # 如果指定了首选源，优先使用
        if preferred_source:
            preferred = [s for s in sources if s.name == preferred_source]
            sources = preferred + [s for s in sources if s.name != preferred_source]

        # 尝试从各源获取数据
        for source in sources:
            if not source.config.is_available:
                continue

            try:
                df = self._fetch_from_source(source, data_type, params)
                if self._validate_data(df, data_type):
                    self._record_success(source.name, data_type)
                    return df
            except Exception as e:
                self._record_failure(source.name, data_type, str(e))
                continue

        raise Exception(f"所有{data_type}数据源获取失败")

    def _fetch_from_source(
        self,
        source: DataSource,
        data_type: str,
        params: Dict
    ) -> pd.DataFrame:
        """从指定源获取数据"""
        if data_type == 'ohlcv':
            return source.fetch_stock_ohlcv(**params)
        elif data_type == 'financial':
            return source.fetch_financial_data(**params)
        elif data_type == 'money_flow':
            return source.fetch_money_flow(**params)
        else:
            raise ValueError(f"未知数据类型: {data_type}")

    def _validate_data(self, df: pd.DataFrame, data_type: str) -> bool:
        """验证数据质量"""
        if df.empty:
            return False

        # 检查必要的列
        if data_type == 'ohlcv':
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            return all(col in df.columns or col.lower() in df.columns for col in required_cols)

        return True

    def _record_success(self, source_name: str, data_type: str):
        """记录成功"""
        key = f"{source_name}_{data_type}"
        if key not in self.quality_stats:
            self.quality_stats[key] = {'success': 0, 'failure': 0}
        self.quality_stats[key]['success'] += 1

    def _record_failure(self, source_name: str, data_type: str, error: str):
        """记录失败"""
        key = f"{source_name}_{data_type}"
        if key not in self.quality_stats:
            self.quality_stats[key] = {'success': 0, 'failure': 0}
        self.quality_stats[key]['failure'] += 1
        logger.warning(f"数据获取失败: {source_name}_{data_type}, error={error}")

    def get_source_quality_report(self) -> Dict:
        """获取数据源质量报告"""
        report = {}
        for key, stats in self.quality_stats.items():
            total = stats['success'] + stats['failure']
            success_rate = stats['success'] / total if total > 0 else 0
            report[key] = {
                'success_count': stats['success'],
                'failure_count': stats['failure'],
                'success_rate': success_rate,
                'quality_score': success_rate * 100
            }
        return report
```

---

## 5. 数据下载调度器

```python
from queue import PriorityQueue
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime, time

@dataclass(order=True)
class DownloadTask:
    """下载任务"""
    priority: int
    task_id: str = field(compare=False)
    task_type: str = field(compare=False)
    params: Dict = field(compare=False)
    status: str = field(compare='status', compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    retry_count: int = 0
    max_retries: int = 3

class SmartDownloadScheduler:
    """智能下载调度器"""

    def __init__(self, data_source_selector: SmartDataSourceSelector):
        self.task_queue = PriorityQueue()
        self.data_source = data_source_selector
        self.schedule_rules = self._init_schedule_rules()

    def _init_schedule_rules(self) -> Dict:
        """初始化调度规则"""
        return {
            'pre_market': {
                'time': (time(6, 0), time(9, 0)),
                'tasks': [
                    {'type': 'daily_ohlcv', 'priority': 1},
                    {'type': 'financial_data', 'priority': 2},
                    {'type': 'concept_board', 'priority': 3},
                ]
            },
            'trading_hours': {
                'time': (time(9, 0), time(15, 0)),
                'tasks': [
                    {'type': 'realtime_quote', 'priority': 1},
                    {'type': 'minute_bar', 'priority': 2},
                ]
            },
            'post_market': {
                'time': (time(15, 0), time(20, 0)),
                'tasks': [
                    {'type': 'complete_ohlcv', 'priority': 1},
                    {'type': 'money_flow', 'priority': 2},
                    {'type': 'margin_data', 'priority': 3},
                ]
            }
        }
```

---

**维护者**: 首席文档架构师
**索引**: `DATA_ADAPTERS_001`

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
