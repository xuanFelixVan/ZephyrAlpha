"""
数据源层模块 (Data Layer)
提供实时数据流、数据质量监控、数据冗余管理、数据缓存管理

技术层次: Layer 0 - 数据源层 | 业务架构: 三级时间框架融合架构

模块清单:
    - realtime_feed: 实时行情数据流
    - quality_monitor: 数据质量监控
    - redundancy_manager: 数据冗余管理
    - cache_manager: 数据缓存管理
    - macro_engine: 宏观经济数据引擎
    - clickhouse_client: ClickHouse客户端

状态说明:
    ✅ P0级模块（立即实施）：realtime_feed, quality_monitor, redundancy_manager, cache_manager
    ⏳ P1级模块（1个月内）：macro_engine, clickhouse_client
    ⏳ P2级模块（3个月内）：ai_engine, high_freq_processor, governance
"""

from src.data.realtime_feed import RealtimeDataFeed
from src.data.quality_monitor import DataQualityMonitor
from src.data.redundancy_manager import DataRedundancyManager
from src.data.cache_manager import DataCacheManager

__all__ = [
    "RealtimeDataFeed",
    "DataQualityMonitor",
    "DataRedundancyManager",
    "DataCacheManager",
]
