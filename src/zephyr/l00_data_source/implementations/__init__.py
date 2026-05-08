"""L00 — Data Source Concrete Implementations

Phase C 具体实现包。包含所有抽象基类的默认生产级实现。

实现清单：
  - AkshareProvider     : DataSourceBase 的具体实现（Akshare 金融数据接入）
  - MemoryProvider      : DataSourceBase 的具体实现（合成数据，无需网络）
  - DefaultQualityGate  : DataQualityGate 的具体实现（5 项质检规则）
"""

from zephyr.l00_data_source.implementations.akshare_provider import AkshareProvider
from zephyr.l00_data_source.implementations.default_quality_gate import DefaultQualityGate
from zephyr.l00_data_source.implementations.memory_provider import MemoryProvider

__all__ = ['AkshareProvider', 'DefaultQualityGate', 'MemoryProvider', 'akshare_provider', 'default_quality_gate', 'memory_provider']
