# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations
# [DOMAIN] D_DATA
# [TTL] permanent
"""
数据源 Provider 实现集合（MOD-L00-004 §4.3）。

每个 Provider 封装一个数据源 SDK，继承 IngestProviderBase。
SDK import 在方法内部（懒加载），模块加载时不依赖具体 SDK 已安装。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/implementations__init__.yaml
"""

from typing import Final

from zephyr.data.implementations.crypto_event_calendar import CryptoEventCalendarProvider
from zephyr.data.implementations.crypto_profile_provider import CryptoProfileProvider
from zephyr.data.implementations.onchain_provider import OnchainProvider

from .akshare_provider import AkshareIngestProvider
from .miniqmt_provider import MiniQmtIngestProvider
from .qmt_bridge_provider import QmtBridgeIngestProvider

__all__: Final = [
    "MiniQmtIngestProvider",
    "QmtBridgeIngestProvider",
    "AkshareIngestProvider",
    "OnchainProvider",
    "CryptoEventCalendarProvider",
    "CryptoProfileProvider",
]
