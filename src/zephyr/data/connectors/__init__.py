# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [MODULE] zephyr.data.connectors
# [DOMAIN] D_DATA
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""
Data Connectors sub-package——外部数据源传输连接器（抽象 + 文件连接器实现）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, Final, ConnectorBatch, ConnectorError, ConnectorRequest,…
#   code: __init__.py import L38
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 annotations, Final, ConnectorBatch, ConnectorError, ConnectorRequest, DataC…
#   desc: __init__ import L38；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（7 符号）
#   name_en: __all__
#   intro: annotations, Final, ConnectorBatch, ConnectorError, ConnectorRequest, DataConne…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

from zephyr.data.connectors.connector_base import (
    ConnectorBatch,
    ConnectorError,
    ConnectorRequest,
    DataConnector,
)
from zephyr.data.connectors.file_connector import FileConnector

__all__: Final = [
    "ConnectorBatch",
    "ConnectorError",
    "ConnectorRequest",
    "DataConnector",
    "FileConnector",
]
