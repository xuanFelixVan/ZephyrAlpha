# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations
# [DOMAIN] D_DATA
# [TTL] permanent
"""
数据源 Provider 实现集合（MOD-L00-004 §4.3）。

每个 Provider 封装一个数据源 SDK，继承 IngestProviderBase。
SDK import 在方法内部（懒加载），模块加载时不依赖具体 SDK 已安装。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Final, CryptoEventCalendarProvider, CryptoProfileProvider, OnchainPro…
#   code: __init__.py import L38
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Final, CryptoEventCalendarProvider, CryptoProfileProvider, OnchainProvider,…
#   desc: __init__ import L38；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（6 符号）
#   name_en: __all__
#   intro: Final, CryptoEventCalendarProvider, CryptoProfileProvider, OnchainProvider, Aks…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

from zephyr.data.implementations.crypto_event_calendar import CryptoEventCalendarProvider
from zephyr.data.implementations.crypto_profile_provider import CryptoProfileProvider
from zephyr.data.implementations.onchain_provider import OnchainProvider

from .akshare_provider import AkshareIngestProvider
from .miniqmt_provider import MiniQmtIngestProvider

__all__: Final = [
    "MiniQmtIngestProvider",
    "AkshareIngestProvider",
    "OnchainProvider",
    "CryptoEventCalendarProvider",
    "CryptoProfileProvider",
]
