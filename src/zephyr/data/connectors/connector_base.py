# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [MODULE] zephyr.data.connectors.connector_base
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.data.connectors.file_connector; zephyr.data.connectors.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Connector 只拉数据返回行集，不写库（与 provider_base 同纪律）；fetch_batch 失败不抛零散异常——统一 ConnectorError
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 连接/拉取失败 → ConnectorError；数据集不存在 → ConnectorError
# [TESTS] tests/zephyr/data/test_connectors.py
# [A_module] module_id=MOD-L00-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据连接器抽象基类（MOD-L00-005 data/connectors/ 核心抽象）。

连接器 = 外部数据源的传输适配层：只负责"连得上、拉得到"，返回统一批结构；
落库/调度归上层（与 data/provider_base 的 Provider 抽象分工——Provider 面向
表级采集策略，Connector 面向传输会话与批量拉取）。
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Final

__all__: Final = [
    "ConnectorBatch",
    "ConnectorError",
    "ConnectorRequest",
    "DataConnector",
]


class ConnectorError(Exception):
    """连接器统一错误（连接失败/拉取失败/数据集不存在）。"""


@dataclass(frozen=True)
class ConnectorRequest:
    """批量拉取请求。

    Attributes:
        dataset: 数据集标识（连接器自定义命名空间，如表名/文件名主干）
        symbols: 标的过滤（None=全部）
        start: 起始日期 ISO 串（含，None=不限）
        end: 结束日期 ISO 串（含，None=不限）
        extra: 连接器专属参数
    """

    dataset: str
    symbols: tuple[str, ...] | None = None
    start: str | None = None
    end: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ConnectorBatch:
    """批量拉取结果。

    Attributes:
        dataset: 数据集标识
        columns: 列名顺序（与 rows tuple 顺序一致）
        rows: 数据行
        source: 来源标识（连接器名/端点）
        error: 错误信息（None=成功；调用方判空兜底）
    """

    dataset: str
    columns: tuple[str, ...]
    rows: tuple[tuple, ...]
    source: str = ""
    error: str | None = None


class DataConnector(abc.ABC):
    """数据连接器抽象：connect / health_check / fetch_batch / close 四件套。"""

    @abc.abstractmethod
    def connect(self) -> None:
        """建立连接（幂等——重复调用不报错）。失败 → ConnectorError。"""

    @abc.abstractmethod
    def health_check(self) -> bool:
        """探活：True=可用。不抛异常（探活语义=尽力而为）。"""

    @abc.abstractmethod
    def fetch_batch(self, request: ConnectorRequest) -> ConnectorBatch:
        """按请求拉取一批数据。数据集不存在/未连接 → ConnectorError。"""

    @abc.abstractmethod
    def close(self) -> None:
        """释放连接（幂等）。"""
