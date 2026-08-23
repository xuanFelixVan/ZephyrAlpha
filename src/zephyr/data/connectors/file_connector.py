# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [MODULE] zephyr.data.connectors.file_connector
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.connectors.connector_base
# [CONSUMERS] zephyr.data.connectors.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读不写；{dataset}.csv 命名约定；日期过滤要求 trade_date 列；幂等（重复 fetch 同结果）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] base_dir 不存在/数据集缺失 → ConnectorError；CSV 解析失败 → ConnectorError
# [TESTS] tests/zephyr/data/test_connectors.py
# [A_module] module_id=MOD-L00-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""文件连接器（MOD-L00-005 具体实现①）。

本地 CSV 目录连接器：{base_dir}/{dataset}.csv 命名约定，支持 symbols/start/end
过滤（start/end 要求 CSV 含 trade_date 列，ISO 串字典序比较）。用途：离线回放、
测试夹具、应急降级数据源（本地快照目录作为兜底"数据源"挂进连接器框架）。
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Final

from zephyr.data.connectors.connector_base import (
    ConnectorBatch,
    ConnectorError,
    ConnectorRequest,
    DataConnector,
)

__all__: Final = ["FileConnector"]


class FileConnector(DataConnector):
    """本地 CSV 目录连接器（只读）。"""

    def __init__(self, base_dir: str | Path, *, date_column: str = "trade_date", symbol_column: str = "symbol") -> None:
        self._base_dir = Path(base_dir)
        self._date_column = date_column
        self._symbol_column = symbol_column
        self._connected = False

    @property
    def name(self) -> str:
        return f"file:{self._base_dir}"

    def connect(self) -> None:
        """校验目录存在（幂等）。"""
        if not self._base_dir.is_dir():
            raise ConnectorError(f"base_dir 不存在或不是目录: {self._base_dir}")
        self._connected = True

    def health_check(self) -> bool:
        return self._connected and self._base_dir.is_dir()

    def fetch_batch(self, request: ConnectorRequest) -> ConnectorBatch:
        """读取 {dataset}.csv 并按 symbols/start/end 过滤。"""
        if not self._connected:
            raise ConnectorError("未 connect（先调 connect()）")
        path = self._base_dir / f"{request.dataset}.csv"
        if not path.is_file():
            raise ConnectorError(f"数据集不存在: {path}")
        try:
            with path.open("r", encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                columns = tuple(reader.fieldnames or ())
                rows: list[tuple] = []
                for rec in reader:
                    if request.symbols is not None and self._symbol_column in columns:
                        if rec[self._symbol_column] not in request.symbols:
                            continue
                    if (request.start or request.end) and self._date_column in columns:
                        d = rec[self._date_column]
                        if request.start and d < request.start:
                            continue
                        if request.end and d > request.end:
                            continue
                    rows.append(tuple(rec[c] for c in columns))
        except csv.Error as e:
            raise ConnectorError(f"CSV 解析失败: {path}: {e}") from e
        return ConnectorBatch(
            dataset=request.dataset,
            columns=columns,
            rows=tuple(rows),
            source=self.name,
        )

    def close(self) -> None:
        self._connected = False
