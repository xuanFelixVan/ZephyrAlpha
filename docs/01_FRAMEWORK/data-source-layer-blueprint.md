---
module_id: DATA_SOURCE_LAYER_001_0069
version: 1.0.0
status: Active
created_date: 2026-04-05
last_updated: '2026-04-07'
owner: 首席架构师
layer: layer_00
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 0 - 数据源层
compliance_level: 顶级专业标准
reference_models:
- Bloomberg Terminal
related_documents:
- ARCHITECTURE.md
parent_document: ../INDEX.md
implementation_status: 设计阶段
responsibility:
- 数据管理架构设计与实施规范与优化维护
---

# Layer 0: 数据源层蓝图

> **核心职责**: Data Source Layer蓝图设计

> **职责边界**: 

> - ✅ 本文档负责：Data Source Layer蓝图设计相关内容

> - ❌ 本文档不负责：其他模块内容





> **版本**: v1.0

> **创建日期**: 2026-04-05

> **实施周期**: 1周

> **目标**: 构建专业级数据源接入体系，对标Bloomberg、Wind数据标准



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。数据源注册、拉取/订阅、凭证与配额、健康状态与切换若通过接口/事件暴露，须在该真源或本文后续接口说明中闭合。



## 验收标准（可检查）



- 能在本文中明确至少一条“数据源接入 → 质量/可用性信号 → 切换或降级 → 审计留痕”的可检查闭环，并能映射到 `API_Contract.md` 的对应契约入口（或写明豁免与补全计划）。



## 已知限制



- 具体厂商 SDK、凭证轮换与网络拓扑以施工文档阶段为准；以本节门禁为准。



```
```---
```



## 📋 执行摘要



### 核心定位



Layer 0数据源层是清风量化系统的**数据基石**，负责：

- 多源数据接入（QMT、iFind、SuperCommand）

- 数据源质量管理（完整性、准确性、及时性）

- 数据源切换与容灾（自动切换、降级策略）

- 数据源成本优化（成本监控、智能调度）



### 个人使用价值



| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评分 |

|---------|-------------|-------------|---------|

| **多源接入** | Bloomberg+Wind+Reuters | QMT+iFind+SuperCommand | ⭐⭐⭐⭐⭐ |

| **数据质量** | 99.9%可用性 | 95%+可用性 | ⭐⭐⭐⭐ |

| **容灾切换** | 毫秒级切换 | 秒级切换 | ⭐⭐⭐⭐ |

| **成本优化** | 企业级议价 | 开源+低成本数据源 | ⭐⭐⭐⭐⭐ |



**综合价值评分**: ⭐⭐⭐⭐⭐ (5/5) - **强烈推荐实施**



```
```---
```



## 一、架构设计



### 1.1 Layer 0整体架构



```

┌─────────────────────────────────────────────────────────────────┐

│                  Layer 0: 数据源层架构                          │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              0.1 数据源接入层                             │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ QMT数据源 (QMT Data Source)                        │ │ │

│  │  │  ├── 行情数据（实时/历史）                        │ │ │

│  │  │  ├── 交易数据（订单/成交）                        │ │ │

│  │  │  ├── 账户数据（资金/持仓）                        │ │ │

│  │  │  └── 本地数据（SQLite缓存）                      │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ iFind数据源 (iFind Data Source)                    │ │ │

│  │  │  ├── 财务数据（三张表）                          │ │ │

│  │  │  ├── 研报数据（分析师预测）                      │ │ │

│  │  │  ├── 宏观数据（经济指标）                        │ │ │

│  │  │  └── 行业数据（产业链）                          │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ SuperCommand数据源 (SuperCommand Data Source)      │ │ │

│  │  │  ├── 新闻数据（财经新闻）                        │ │ │

│  │  │  ├── 社交媒体（雪球/东方财富）                  │ │ │

│  │  │  ├── 另类数据（卫星/电商）                      │ │ │

│  │  │  └── 自定义数据（爬虫/API）                     │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              0.2 数据源管理层                             │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 数据源注册中心 (Data Source Registry)              │ │ │

│  │  │  ├── 数据源元数据（类型/状态/优先级）            │ │ │

│  │  │  ├── 数据源配置（连接参数/认证信息）            │ │ │

│  │  │  ├── 数据源监控（健康检查/性能指标）            │ │ │

│  │  │  └── 数据源切换（自动切换/降级策略）            │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 数据源路由器 (Data Source Router)                  │ │ │

│  │  │  ├── 智能路由（基于数据类型/成本/延迟）        │ │ │

│  │  │  ├── 负载均衡（请求分发/并发控制）            │ │ │

│  │  │  ├── 缓存策略（热点数据/过期策略）            │ │ │

│  │  │  └── 降级策略（数据源不可用时的备选方案）    │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 数据源监控器 (Data Source Monitor)                 │ │ │

│  │  │  ├── 实时监控（延迟/错误率/吞吐量）            │ │ │

│  │  │  ├── 质量评估（完整性/准确性/及时性）        │ │ │

│  │  │  ├── 成本统计（API调用/流量/费用）            │ │ │

│  │  │  └── 告警通知（异常检测/阈值告警）            │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              0.3 数据源适配层                             │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 统一数据接口 (Unified Data Interface)              │ │ │

│  │  │  ├── 标准化格式（OHLCV/财务/新闻）              │ │ │

│  │  │  ├── 统一API（get_market_data/get_financial）  │ │ │

│  │  │  ├── 数据转换（格式转换/单位统一）            │ │ │

│  │  │  └── 异常处理（错误重试/降级返回）            │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  └───────────────────────────────────────────────────────────┘ │

└─────────────────────────────────────────────────────────────────┘

```



### 1.2 模块职责边界



| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |

|------|---------|------|------|---------|

| **数据源接入层** | 多源数据采集 | API请求/数据库查询 | 原始数据 | 数据源管理层 |

| **数据源管理层** | 数据源治理 | 数据请求 | 路由决策/监控指标 | 数据源适配层 |

| **数据源适配层** | 数据标准化 | 原始数据 | 标准化数据 | Layer 1 |



```
```---
```



## 二、核心组件详细设计



### 2.1 数据源接入层



#### 2.1.1 QMT数据源 (QMT Data Source)



**核心职责**：

1. **行情数据接入**：实时行情/历史行情

2. **交易数据接入**：订单状态/成交记录

3. **账户数据接入**：资金余额/持仓明细

4. **本地数据缓存**：SQLite本地存储



**技术实现**：



```python

from typing import Dict, List, Optional

from datetime import datetime, timedelta

import pandas as pd

import sqlite3

from dataclasses import dataclass

from enum import Enum



class DataType(Enum):

    """数据类型"""

    MARKET_DATA = "market_data"      # 行情数据

    TRADE_DATA = "trade_data"        # 交易数据

    ACCOUNT_DATA = "account_data"    # 账户数据

    FINANCIAL_DATA = "financial_data" # 财务数据



@dataclass

class DataSourceConfig:

    """数据源配置"""

    source_id: str

    source_name: str

    source_type: str

    priority: int  # 优先级，数字越小优先级越高

    connection_params: Dict

    auth_params: Dict

    rate_limit: int  # 每分钟请求限制

    timeout: int     # 超时时间（秒）

    retry_times: int # 重试次数

    enabled: bool



class QMTDataSource:

    """QMT数据源"""

    

    def __init__(self, config: DataSourceConfig):

        self.config = config

        self.connection = None

        self.cache_db = sqlite3.connect('qmt_cache.db')

        self._init_cache_db()

        

    def _init_cache_db(self):

        """初始化缓存数据库"""

        cursor = self.cache_db.cursor()

        cursor.execute('''

            CREATE TABLE IF NOT EXISTS market_data_cache (

                stock_code TEXT,

                data_type TEXT,

                timestamp TEXT,

                data TEXT,

                created_at TEXT,

                PRIMARY KEY (stock_code, data_type, timestamp)

            )

        ''')

        self.cache_db.commit()

        

    def get_market_data(

        self,

        stock_code: str,

        start_date: datetime,

        end_date: datetime,

        frequency: str = '1d'

    ) -> pd.DataFrame:

        """获取行情数据"""

        

        cache_key = f"{stock_code}_{frequency}_{start_date}_{end_date}"

        cached_data = self._get_from_cache(cache_key)

        if cached_data is not None:

            return cached_data

        

        try:

            data = self._fetch_from_qmt(stock_code, start_date, end_date, frequency)

            self._save_to_cache(cache_key, data)

            return data

        except Exception as e:

            self._handle_error(e)

            return self._get_fallback_data(stock_code, start_date, end_date)

    

    def _fetch_from_qmt(

        self,

        stock_code: str,

        start_date: datetime,

        end_date: datetime,

        frequency: str

    ) -> pd.DataFrame:

        """从QMT获取数据"""

        

        pass

    

    def _get_from_cache(self, cache_key: str) -> Optional[pd.DataFrame]:

        """从缓存获取数据"""

        cursor = self.cache_db.cursor()

        cursor.execute(

            'SELECT data FROM market_data_cache WHERE cache_key = ?',

            (cache_key,)

        )

        result = cursor.fetchone()

        if result:

            return pd.read_json(result[0])

        return None

    

    def _save_to_cache(self, cache_key: str, data: pd.DataFrame):

        """保存数据到缓存"""

        cursor = self.cache_db.cursor()

        cursor.execute(

            'INSERT OR REPLACE INTO market_data_cache VALUES (?, ?, ?)',

            (cache_key, data.to_json(), datetime.now().isoformat())

        )

        self.cache_db.commit()

    

    def _handle_error(self, error: Exception):

        """错误处理"""

        print(f"QMT数据源错误: {error}")

        

    def _get_fallback_data(

        self,

        stock_code: str,

        start_date: datetime,

        end_date: datetime

    ) -> pd.DataFrame:

        """降级数据获取"""

        return pd.DataFrame()

```



#### 2.1.2 iFind数据源 (iFind Data Source)



**核心职责**：

1. **财务数据接入**：资产负债表/利润表/现金流量表

2. **研报数据接入**：分析师预测/评级调整

3. **宏观数据接入**：GDP/CPI/PMI等

4. **行业数据接入**：产业链/竞争格局



**技术实现**：



```python

class iFindDataSource:

    """iFind数据源"""

    

    def __init__(self, config: DataSourceConfig):

        self.config = config

        self.api_client = None

        

    def get_financial_data(

        self,

        stock_code: str,

        report_type: str = 'all',

        period: str = 'latest'

    ) -> Dict:

        """获取财务数据"""

        

        try:

            data = self._fetch_from_ifind(stock_code, report_type, period)

            return self._normalize_financial_data(data)

        except Exception as e:

            self._handle_error(e)

            return {}

    

    def get_research_report(

        self,

        stock_code: str,

        start_date: datetime,

        end_date: datetime

    ) -> List[Dict]:

        """获取研报数据"""

        

        pass

    

    def _normalize_financial_data(self, raw_data: Dict) -> Dict:

        """标准化财务数据"""

        

        normalized = {}

        

        if 'balance_sheet' in raw_data:

            normalized['balance_sheet'] = self._convert_units(raw_data['balance_sheet'])

        if 'income_statement' in raw_data:

            normalized['income_statement'] = self._convert_units(raw_data['income_statement'])

        if 'cash_flow' in raw_data:

            normalized['cash_flow'] = self._convert_units(raw_data['cash_flow'])

            

        return normalized

    

    def _convert_units(self, data: Dict) -> Dict:

        """单位转换（万元->元）"""

        

        converted = {}

        for key, value in data.items():

            if isinstance(value, (int, float)):

                converted[key] = value * 10000  # 万元转元

            else:

                converted[key] = value

        return converted

```



#### 2.1.3 SuperCommand数据源 (SuperCommand Data Source)



**核心职责**：

1. **新闻数据接入**：财经新闻/公告解读

2. **社交媒体接入**：雪球/东方财富股吧

3. **另类数据接入**：卫星数据/电商数据

4. **自定义数据接入**：爬虫数据/API数据



**技术实现**：



```python

class SuperCommandDataSource:

    """SuperCommand数据源"""

    

    def __init__(self, config: DataSourceConfig):

        self.config = config

        self.news_api = None

        self.social_api = None

        

    def get_news_data(

        self,

        keywords: List[str],

        start_date: datetime,

        end_date: datetime,

        source: str = 'all'

    ) -> List[Dict]:

        """获取新闻数据"""

        

        try:

            news = self._fetch_news(keywords, start_date, end_date, source)

            return self._filter_and_rank_news(news)

        except Exception as e:

            self._handle_error(e)

            return []

    

    def get_social_media_data(

        self,

        stock_code: str,

        platform: str = 'xueqiu',

        limit: int = 100

    ) -> List[Dict]:

        """获取社交媒体数据"""

        

        pass

    

    def _filter_and_rank_news(self, news: List[Dict]) -> List[Dict]:

        """过滤和排序新闻"""

        

        filtered = [n for n in news if self._is_relevant(n)]

        ranked = sorted(filtered, key=lambda x: x['importance_score'], reverse=True)

        return ranked[:50]  # 返回前50条重要新闻

    

    def _is_relevant(self, news: Dict) -> bool:

        """判断新闻相关性"""

        

        keywords = ['业绩', '盈利', '亏损', '并购', '重组', '高管']

        title = news.get('title', '')

        content = news.get('content', '')

        

        return any(kw in title or kw in content for kw in keywords)

```



```
```---
```



### 2.2 数据源管理层



#### 2.2.1 数据源注册中心 (Data Source Registry)



**核心职责**：

1. **数据源元数据管理**：类型/状态/优先级

2. **数据源配置管理**：连接参数/认证信息

3. **数据源监控**：健康检查/性能指标

4. **数据源切换**：自动切换/降级策略



**技术实现**：



```python

from typing import Dict, List

from enum import Enum

import json



class DataSourceStatus(Enum):

    """数据源状态"""

    ACTIVE = "active"          # 活跃

    DEGRADED = "degraded"      # 降级

    INACTIVE = "inactive"      # 不活跃

    ERROR = "error"            # 错误



class DataSourceRegistry:

    """数据源注册中心"""

    

    def __init__(self):

        self.registry: Dict[str, DataSourceConfig] = {}

        self.status: Dict[str, DataSourceStatus] = {}

        self.metrics: Dict[str, Dict] = {}

        

    def register(self, config: DataSourceConfig):

        """注册数据源"""

        self.registry[config.source_id] = config

        self.status[config.source_id] = DataSourceStatus.ACTIVE

        self.metrics[config.source_id] = {

            'request_count': 0,

            'error_count': 0,

            'avg_latency': 0.0,

            'last_success': None

        }

        

    def get_data_source(self, source_id: str) -> Optional[DataSourceConfig]:

        """获取数据源配置"""

        return self.registry.get(source_id)

    

    def update_status(self, source_id: str, status: DataSourceStatus):

        """更新数据源状态"""

        self.status[source_id] = status

        

    def get_active_sources(self) -> List[DataSourceConfig]:

        """获取活跃数据源"""

        return [

            self.registry[sid]

            for sid, status in self.status.items()

            if status == DataSourceStatus.ACTIVE

        ]

    

    def health_check(self, source_id: str) -> bool:

        """健康检查"""

        

        try:

            source = self.registry[source_id]

            return self._ping_source(source)

        except Exception as e:

            self.update_status(source_id, DataSourceStatus.ERROR)

            return False

    

    def _ping_source(self, source: DataSourceConfig) -> bool:

        """Ping数据源"""

        

        pass

```



#### 2.2.2 数据源路由器 (Data Source Router)



**核心职责**：

1. **智能路由**：基于数据类型/成本/延迟选择最优数据源

2. **负载均衡**：请求分发/并发控制

3. **缓存策略**：热点数据缓存/过期策略

4. **降级策略**：数据源不可用时的备选方案



**技术实现**：



```python

from typing import Optional, Dict

import hashlib



class DataSourceRouter:

    """数据源路由器"""

    

    def __init__(self, registry: DataSourceRegistry):

        self.registry = registry

        self.cache = {}

        self.cache_ttl = 300  # 5分钟缓存

        

    def route(

        self,

        data_type: DataType,

        params: Dict,

        strategy: str = 'auto'

    ) -> str:

        """路由到最优数据源"""

        

        if strategy == 'auto':

            return self._auto_route(data_type, params)

        elif strategy == 'cost_first':

            return self._cost_first_route(data_type, params)

        elif strategy == 'latency_first':

            return self._latency_first_route(data_type, params)

        else:

            return self._default_route(data_type, params)

    

    def _auto_route(self, data_type: DataType, params: Dict) -> str:

        """自动路由（综合考虑成本和延迟）"""

        

        candidates = self._get_candidates(data_type)

        if not candidates:

            raise Exception(f"No available data source for {data_type}")

        

        scored = [

            (source, self._calculate_score(source))

            for source in candidates

        ]

        scored.sort(key=lambda x: x[1], reverse=True)

        

        return scored[0][0].source_id

    

    def _calculate_score(self, source: DataSourceConfig) -> float:

        """计算数据源得分"""

        

        metrics = self.registry.metrics.get(source.source_id, {})

        

        latency_score = 1.0 / (metrics.get('avg_latency', 1.0) + 1)

        reliability_score = 1.0 - (metrics.get('error_count', 0) / max(metrics.get('request_count', 1), 1))

        priority_score = 1.0 / source.priority

        

        return latency_score * 0.4 + reliability_score * 0.4 + priority_score * 0.2

    

    def _get_candidates(self, data_type: DataType) -> List[DataSourceConfig]:

        """获取候选数据源"""

        

        active_sources = self.registry.get_active_sources()

        return [

            s for s in active_sources

            if self._supports_data_type(s, data_type)

        ]

    

    def _supports_data_type(self, source: DataSourceConfig, data_type: DataType) -> bool:

        """判断数据源是否支持该数据类型"""

        

        return True

    

    def get_from_cache(self, key: str) -> Optional[any]:

        """从缓存获取"""

        return self.cache.get(key)

    

    def save_to_cache(self, key: str, data: any, ttl: int = None):

        """保存到缓存"""

        self.cache[key] = {

            'data': data,

            'expires_at': datetime.now() + timedelta(seconds=ttl or self.cache_ttl)

        }

```



#### 2.2.3 数据源监控器 (Data Source Monitor)



**核心职责**：

1. **实时监控**：延迟/错误率/吞吐量

2. **质量评估**：完整性/准确性/及时性

3. **成本统计**：API调用/流量/费用

4. **告警通知**：异常检测/阈值告警



**技术实现**：



```python

from collections import defaultdict

import time



class DataSourceMonitor:

    """数据源监控器"""

    

    def __init__(self, registry: DataSourceRegistry):

        self.registry = registry

        self.metrics_history = defaultdict(list)

        self.alert_thresholds = {

            'latency': 5.0,      # 延迟阈值（秒）

            'error_rate': 0.05,  # 错误率阈值（5%）

            'throughput': 100    # 吞吐量阈值（请求/分钟）

        }

        

    def record_request(

        self,

        source_id: str,

        latency: float,

        success: bool

    ):

        """记录请求"""

        

        metrics = self.registry.metrics[source_id]

        metrics['request_count'] += 1

        if not success:

            metrics['error_count'] += 1

        

        metrics['avg_latency'] = (

            (metrics['avg_latency'] * (metrics['request_count'] - 1) + latency)

            / metrics['request_count']

        )

        

        if success:

            metrics['last_success'] = datetime.now()

        

        self._check_alerts(source_id, metrics)

    

    def _check_alerts(self, source_id: str, metrics: Dict):

        """检查告警"""

        

        if metrics['avg_latency'] > self.alert_thresholds['latency']:

            self._send_alert(source_id, 'high_latency', metrics['avg_latency'])

        

        error_rate = metrics['error_count'] / max(metrics['request_count'], 1)

        if error_rate > self.alert_thresholds['error_rate']:

            self._send_alert(source_id, 'high_error_rate', error_rate)

    

    def _send_alert(self, source_id: str, alert_type: str, value: float):

        """发送告警"""

        

        print(f"ALERT: {source_id} - {alert_type}: {value}")

        

    def get_metrics_report(self, source_id: str) -> Dict:

        """获取指标报告"""

        

        metrics = self.registry.metrics.get(source_id, {})

        return {

            'source_id': source_id,

            'request_count': metrics.get('request_count', 0),

            'error_count': metrics.get('error_count', 0),

            'error_rate': metrics.get('error_count', 0) / max(metrics.get('request_count', 1), 1),

            'avg_latency': metrics.get('avg_latency', 0.0),

            'last_success': metrics.get('last_success'),

            'status': self.registry.status.get(source_id, DataSourceStatus.INACTIVE).value

        }

```



```
```---
```



### 2.3 数据源适配层



#### 2.3.1 统一数据接口 (Unified Data Interface)



**核心职责**：

1. **标准化格式**：OHLCV/财务/新闻统一格式

2. **统一API**：get_market_data/get_financial_data

3. **数据转换**：格式转换/单位统一

4. **异常处理**：错误重试/降级返回



**技术实现**：



```python

from abc import ABC, abstractmethod



class UnifiedDataInterface(ABC):

    """统一数据接口"""

    

    @abstractmethod

    def get_market_data(

        self,

        stock_code: str,

        start_date: datetime,

        end_date: datetime,

        frequency: str = '1d'

    ) -> pd.DataFrame:

        """获取行情数据"""

        pass

    

    @abstractmethod

    def get_financial_data(

        self,

        stock_code: str,

        report_type: str = 'all',

        period: str = 'latest'

    ) -> Dict:

        """获取财务数据"""

        pass

    

    @abstractmethod

    def get_news_data(

        self,

        stock_code: str,

        start_date: datetime,

        end_date: datetime

    ) -> List[Dict]:

        """获取新闻数据"""

        pass



class DataFacade(UnifiedDataInterface):

    """数据门面"""

    

    def __init__(

        self,

        qmt_source: QMTDataSource,

        ifind_source: iFindDataSource,

        supercmd_source: SuperCommandDataSource,

        router: DataSourceRouter

    ):

        self.qmt = qmt_source

        self.ifind = ifind_source

        self.supercmd = supercmd_source

        self.router = router

        

    def get_market_data(

        self,

        stock_code: str,

        start_date: datetime,

        end_date: datetime,

        frequency: str = '1d'

    ) -> pd.DataFrame:

        """获取行情数据"""

        

        cache_key = f"market_{stock_code}_{frequency}_{start_date}_{end_date}"

        cached = self.router.get_from_cache(cache_key)

        if cached:

            return cached

        

        source_id = self.router.route(DataType.MARKET_DATA, {

            'stock_code': stock_code,

            'start_date': start_date,

            'end_date': end_date,

            'frequency': frequency

        })

        

        if source_id == 'qmt':

            data = self.qmt.get_market_data(stock_code, start_date, end_date, frequency)

        else:

            data = pd.DataFrame()

        

        self.router.save_to_cache(cache_key, data)

        return data

    

    def get_financial_data(

        self,

        stock_code: str,

        report_type: str = 'all',

        period: str = 'latest'

    ) -> Dict:

        """获取财务数据"""

        

        source_id = self.router.route(DataType.FINANCIAL_DATA, {

            'stock_code': stock_code,

            'report_type': report_type,

            'period': period

        })

        

        if source_id == 'ifind':

            return self.ifind.get_financial_data(stock_code, report_type, period)

        else:

            return {}

    

    def get_news_data(

        self,

        stock_code: str,

        start_date: datetime,

        end_date: datetime

    ) -> List[Dict]:

        """获取新闻数据"""

        

        source_id = self.router.route(DataType.NEWS_DATA, {

            'stock_code': stock_code,

            'start_date': start_date,

            'end_date': end_date

        })

        

        if source_id == 'supercmd':

            return self.supercmd.get_news_data([stock_code], start_date, end_date)

        else:

            return []

```



```
```---
```



## 三、数据模型设计



### 3.1 核心数据模型



```python

@dataclass

class MarketData:

    """行情数据"""

    stock_code: str

    timestamp: datetime

    open: float

    high: float

    low: float

    close: float

    volume: int

    amount: float

    adj_factor: float = 1.0



@dataclass

class FinancialData:

    """财务数据"""

    stock_code: str

    report_date: datetime

    report_type: str  # quarterly, annual

    balance_sheet: Dict

    income_statement: Dict

    cash_flow: Dict



@dataclass

class NewsData:

    """新闻数据"""

    news_id: str

    title: str

    content: str

    source: str

    published_at: datetime

    sentiment: str  # positive, negative, neutral

    importance_score: float

    related_stocks: List[str]

```



```
```---
```



## 四、实施路线



### 4.1 Phase 1: 核心数据源接入（Week 1）



**任务清单**：

- [ ] 实现QMT数据源接入

- [ ] 实现iFind数据源接入

- [ ] 实现SuperCommand数据源接入

- [ ] 实现数据源注册中心



```
```---
```



### 4.2 Phase 2: 数据源管理（Week 1）



**任务清单**：

- [ ] 实现数据源路由器

- [ ] 实现数据源监控器

- [ ] 实现缓存策略

- [ ] 实现降级策略



```
```---
```



### 4.3 Phase 3: 统一接口（Week 1）



**任务清单**：

- [ ] 实现统一数据接口

- [ ] 实现数据标准化

- [ ] 实现异常处理

- [ ] 集成测试



```
```---
```



## 五、质量保证



### 5.1 测试策略



| 测试类型 | 覆盖率目标 | 测试工具 |

|---------|-----------|---------|

| **单元测试** | ≥90% | pytest |

| **集成测试** | ≥80% | pytest |

| **性能测试** | 关键路径 | locust |



```
```---
```



## 六、成功指标



| 指标 | 目标值 |

|------|--------|

| **数据可用性** | ≥95% |

| **数据延迟** | ≤1秒（实时数据） |

| **错误率** | ≤5% |

| **缓存命中率** | ≥80% |



```
```---
```



## 七、相关文档



| 文档 | 说明 |

|------|------|

| DATA_PREPROCESSING_LAYER_BLUEPRINT.md | 数据预处理层蓝图 |

| DATA_QUALITY_MONITORING_BLUEPRINT.md | 数据质量监控蓝图 |

| [ARCHITECTURE.md](./ARCHITECTURE.md) | 系统架构文档 |



```
```---
```



**版本**: v1.0 | **更新**: 2026-04-05 | **状态**: 活跃

```
```---
```



## 1. 文档治理



### 1.1 System_Manifest.md索引



```markdown

#### Layer 0: 数据源层

##### 0.001. Data Source Layer Blueprint

- **模块ID**: DATA_SOURCE_LAYER_BLUEPRINT_001

- **蓝图文档**: DATA_SOURCE_LAYER_BLUEPRINT.md

- **技术规格书**: 待创建

- **职责**: Layer 0 - 数据源层

- **状态**: Active

```



### 1.2 模块职责边界



| 模块 | 职责 | 边界 |

|------|------|------|

| **Data Source Layer Blueprint** | Layer 0 - 数据源层 | **核心模块** |



### 1.3 版本管理



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-05 | 初始版本创建 | 首席蓝图架构师 |



```
```---
```



**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-05 | **状态**: Active

