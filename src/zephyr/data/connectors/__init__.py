# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [MODULE] zephyr.data.connectors
# [DOMAIN] D_DATA
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""Data Connectors sub-package——外部数据源传输连接器（抽象 + 文件连接器实现）。"""

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
