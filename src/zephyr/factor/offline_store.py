# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.offline_store
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pyarrow(Parquet落盘); duckdb(读取API,注入式conn); 与 MOD-L02-FS feature_store_writer 为在线/离线对偶（无语义 import）
# [CONSUMERS] （候选：ML 训练特征抽取/回测批量读取/因子评估/PIT 验证装配批——D_BACKTEST;D_ML_TRAIN）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 7列Schema(trade_date/symbol/factor_name/value/version/computed_at/quality_flag)唯一真源 fail-closed；三目录封闭集(daily/intraday按日,snapshots按月)；同批内容重写幂等(内容寻址批文件名)；读侧同键重算取computed_at最新；默认排除quarantined；原子写(tmp+os.replace)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 缺列/非法quality_flag/非法日期/非法layer → ValueError（fail-closed）；空批→零写不报错；空仓→空列表不报错
# [TESTS] tests/factor/test_offline_store.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 7列因子值行 dict 批次 + layer(daily/intraday/snapshots) + root_dir
# A1: validate_rows——7列/日期/质量标记 fail-closed 校验
# A2: 分区映射——daily/intraday→trade_date=YYYY-MM-DD；snapshots→year=YYYY/month=MM
# A3: 写入——分区内行规范化排序→内容寻址批文件名(sha256前16)→已存在跳过(幂等)→pyarrow原子写
# A4: 读取——DuckDB read_parquet 递归扫描+因子/日期/质量过滤+ROW_NUMBER同键取最新
# O1: WriteReceipt(写入回执) / list[dict](7列行)
# [/ALGO_FLOW]
"""
离线存储 Offline Store（CAND-FAC-015 / B13-04144，feast 式 Parquet/DuckDB 离线仓）。

特征仓批量分析面：Parquet 离线三目录（daily/intraday/snapshots）+ 7 列 Schema
（trade_date/symbol/factor_name/value/version/computed_at/quality_flag）+
DuckDB 读取 API，供 ML 训练/回测/因子评估/PIT 验证批量消费。

**与 CH 写入器的单写/双写归属裁定**（TSV 既定写成裁定）：
  - c1_market.factor_feature_value（MOD-L02-FS feature_store_writer）= **在线服务面**：
    盘中低延迟单因子点查，写方=feature_store_writer（CH 单写）。
  - 本模块 = **批量分析面**：ML 训练/回测/评估批量扫描，写方=OfflineStore（Parquet 单写）。
  - **双写编排归属调用方**（factor_production_pipeline 落库批/运行时装配批决定哪些
    因子双写）；本模块不写 CH、feature_store_writer 不写 Parquet，互不静默双写。

分区裁定（TSV"按日/月分区三目录"落地）：daily/intraday 按日（trade_date=YYYY-MM-DD，
日内多批次同日落同分区）；snapshots 按月（year=YYYY/month=MM，快照为月度截面语义）。
trade_date 以 VARCHAR 存储——ISO 日期字典序=时序，hive 目录仅为物理组织，读取过滤
走列谓词（hive_partitioning=False 避免与文件内 7 列冲突）。

重算语义：同 (trade_date,symbol,factor_name,version) 多批次 → 读侧取 computed_at
最新（对齐 CH ReplacingMergeTree"重复计算取最新"幂等重算裁定）。

查重裁定（不重复既有件）：
  - feature_store_writer（MOD-L02-FS）：CH 在线长表写入器，无 Parquet/无 7 列/无 DuckDB 读。
  - storage_tiering（MOD-L00-004）：D_DATA 行情数据冷热分层 TTL 迁移决策件
    （parquet_write 注入式），非因子 7 列离线仓、无 DuckDB 读取 API。

依据: A3数据架构 §11.1.1；construction_backlog_dig.tsv B13-04144。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: rows 参数
#   fields: 参数 rows，类型注解 Iterable[Mapping]
#   code: offline_store.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: layer 参数
#   fields: 参数 layer，类型注解 str
#   code: offline_store.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: trade_date 参数
#   fields: 参数 trade_date，类型注解 str
#   code: offline_store.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① validate_rows
#   name_en: validate_rows
#   intro: 7 列 Schema fail-closed 校验。
#   desc: 7 列 Schema fail-closed 校验。 Raises: ValueError: 缺列/非法 quality_flag/非法 trade_date/非法 comput…；源码 L204-L247
#   inputs: rows
#   outputs: list[FactorValueRow]
# - id: A2
#   name_zh: ② partition_path
#   name_en: partition_path
#   intro: 分区相对路径：daily/intraday→trade_date=YYYY-MM-DD；snapshots→year=…
#   desc: 分区相对路径：daily/intraday→trade_date=YYYY-MM-DD；snapshots→year=YYYY/month=MM。 Raises: ValueEr…；源码 L250-L261
#   inputs: layer trade_date
#   outputs: str
# - id: A3
#   name_zh: ③ OfflineStore
#   name_en: OfflineStore
#   intro: 因子 Parquet 离线仓门面：三目录分区写 + DuckDB 批量读。
#   desc: 因子 Parquet 离线仓门面：三目录分区写 + DuckDB 批量读。 Args: root_dir: 离线仓根目录（本地路径；不存在时首个 write 创建）。；公共方法（定义序）: root, write, r…
#   inputs: root_dir
#   outputs: 返回值
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[FactorValueRow]
#   name_en: list[FactorValueRow]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: （候选：ML 训练特征抽取/回测批量读取/因子评估/PIT 验证装配批——D_BACKTEST;D_ML_TRAIN）
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: （候选：ML 训练特征抽取/回测批量读取/因子评估/PIT 验证装配批——D_BACKTEST;D_ML_TRAIN）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import datetime
import hashlib
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable, Mapping, Sequence

log = logging.getLogger(__name__)

__all__: Final = [
    "FactorValueRow",
    "OfflineStore",
    "SCHEMA_COLUMNS",
    "WriteReceipt",
    "partition_path",
    "validate_rows",
]

#: 7 列 Schema 唯一真源（SSoT，禁硬编码他处）
SCHEMA_COLUMNS: Final = ("trade_date", "symbol", "factor_name", "value", "version", "computed_at", "quality_flag")

#: 三目录封闭集
LAYERS: Final = ("daily", "intraday", "snapshots")

#: 质量标记封闭集
QUALITY_FLAGS: Final = frozenset({"ok", "degraded", "quarantined"})

#: 读取默认质量过滤（quarantined 默认排除，显式传入才放行）
DEFAULT_READ_QUALITY: Final = ("ok", "degraded")

_TRADE_DATE_RE: Final = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DEDUP_KEY: Final = ("trade_date", "symbol", "factor_name", "version")


@dataclass(frozen=True)
class FactorValueRow:
    """7 列因子值行（不可变，校验后产物）。

    Attributes:
        trade_date: 交易日期 ISO YYYY-MM-DD。
        symbol: 证券代码。
        factor_name: 因子名（非空）。
        value: 因子值（None=预热期 NULL 原貌，不前向填充）。
        version: 因子 SemVer 版本。
        computed_at: 计算时间戳 ISO 8601。
        quality_flag: 质量标记（ok/degraded/quarantined 封闭集）。
    """

    trade_date: str
    symbol: str
    factor_name: str
    value: float | None
    version: str
    computed_at: str
    quality_flag: str


@dataclass(frozen=True)
class WriteReceipt:
    """写入回执（不可变）。

    Attributes:
        layer: 目标目录（daily/intraday/snapshots）。
        rows_written: 写入行数。
        files_written: 新落盘文件数（幂等跳过分区不计）。
        partition_files: 批文件相对路径元组（含幂等跳过的既有文件）。
    """

    layer: str
    rows_written: int
    files_written: int
    partition_files: tuple[str, ...]


def _validate_trade_date(value: str) -> None:
    if not _TRADE_DATE_RE.match(value):
        raise ValueError(f"trade_date 非法（需 ISO YYYY-MM-DD）: {value!r}")
    datetime.date.fromisoformat(value)  # 日期真实性校验（如 2026-02-30 拒绝）


def _validate_computed_at(value: str) -> None:
    try:
        datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise ValueError(f"computed_at 非法（需 ISO 8601）: {value!r}") from None


def validate_rows(rows: Iterable[Mapping]) -> list[FactorValueRow]:
    """7 列 Schema fail-closed 校验。

    Raises:
        ValueError: 缺列/非法 quality_flag/非法 trade_date/非法 computed_at/空 factor_name/空 symbol/value 非数值。
    """
    validated: list[FactorValueRow] = []
    for row in rows:
        missing = [c for c in SCHEMA_COLUMNS if c not in row]
        if missing:
            raise ValueError(f"因子值行缺列: {missing}（7 列 Schema={list(SCHEMA_COLUMNS)}）")
        trade_date = str(row["trade_date"])
        _validate_trade_date(trade_date)
        computed_at = str(row["computed_at"])
        _validate_computed_at(computed_at)
        factor_name = str(row["factor_name"]).strip()
        if not factor_name:
            raise ValueError("factor_name 不能为空")
        symbol = str(row["symbol"]).strip()
        if not symbol:
            raise ValueError("symbol 不能为空")
        quality_flag = str(row["quality_flag"])
        if quality_flag not in QUALITY_FLAGS:
            raise ValueError(f"quality_flag 非法（封闭集 {sorted(QUALITY_FLAGS)}）: {quality_flag!r}")
        raw_value = row["value"]
        if raw_value is None:
            value = None
        else:
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                raise ValueError(f"value 非数值: {raw_value!r}") from None
        validated.append(
            FactorValueRow(
                trade_date=trade_date,
                symbol=symbol,
                factor_name=factor_name,
                value=value,
                version=str(row["version"]),
                computed_at=computed_at,
                quality_flag=quality_flag,
            )
        )
    return validated


def partition_path(layer: str, trade_date: str) -> str:
    """分区相对路径：daily/intraday→trade_date=YYYY-MM-DD；snapshots→year=YYYY/month=MM。

    Raises:
        ValueError: layer 非封闭集 / trade_date 非法。
    """
    if layer not in LAYERS:
        raise ValueError(f"layer 非法（封闭集 {list(LAYERS)}）: {layer!r}")
    _validate_trade_date(trade_date)
    if layer == "snapshots":
        return f"year={trade_date[:4]}/month={trade_date[5:7]}"
    return f"trade_date={trade_date}"


def _canonical_tuples(rows: Sequence[FactorValueRow]) -> tuple[tuple, ...]:
    """规范化排序行 tuple（内容寻址与字节级幂等的基准序）。"""
    ordered = sorted(rows, key=lambda r: (r.trade_date, r.symbol, r.factor_name, r.version, r.computed_at))
    return tuple(
        (r.trade_date, r.symbol, r.factor_name, r.value, r.version, r.computed_at, r.quality_flag) for r in ordered
    )


def _quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


class OfflineStore:
    """因子 Parquet 离线仓门面：三目录分区写 + DuckDB 批量读。

    Args:
        root_dir: 离线仓根目录（本地路径；不存在时首个 write 创建）。
    """

    def __init__(self, root_dir: str | os.PathLike) -> None:
        self._root = Path(root_dir)

    @property
    def root(self) -> Path:
        return self._root

    # ---------------------------------------------------------------- 写入

    def write(self, rows: Iterable[Mapping], layer: str) -> WriteReceipt:
        """7 列批次分区落盘（内容寻址幂等 + 原子写）。

        同一分区同一批内容重写 → 命中既有批文件，零新文件（幂等）；
        不同内容 → 新批文件追加（读侧去重取最新）。

        Raises:
            ValueError: 校验失败（见 validate_rows/partition_path）。
        """
        if layer not in LAYERS:
            raise ValueError(f"layer 非法（封闭集 {list(LAYERS)}）: {layer!r}")
        validated = validate_rows(rows)
        if not validated:
            return WriteReceipt(layer=layer, rows_written=0, files_written=0, partition_files=())

        import pyarrow as pa
        import pyarrow.parquet as pq

        by_partition: dict[str, list[FactorValueRow]] = {}
        for row in validated:
            by_partition.setdefault(partition_path(layer, row.trade_date), []).append(row)

        files_written = 0
        partition_files: list[str] = []
        for part_rel, part_rows in sorted(by_partition.items()):
            canonical = _canonical_tuples(part_rows)
            digest = hashlib.sha256(repr(canonical).encode("utf-8")).hexdigest()[:16]
            part_dir = self._root / layer / Path(part_rel)
            file_path = part_dir / f"batch_{digest}.parquet"
            partition_files.append(str(Path(layer) / part_rel / file_path.name))
            if file_path.exists():
                continue  # 幂等：同批内容重写零新文件
            table = pa.table(
                {
                    "trade_date": pa.array([t[0] for t in canonical], type=pa.string()),
                    "symbol": pa.array([t[1] for t in canonical], type=pa.string()),
                    "factor_name": pa.array([t[2] for t in canonical], type=pa.string()),
                    "value": pa.array([t[3] for t in canonical], type=pa.float64()),
                    "version": pa.array([t[4] for t in canonical], type=pa.string()),
                    "computed_at": pa.array([t[5] for t in canonical], type=pa.string()),
                    "quality_flag": pa.array([t[6] for t in canonical], type=pa.string()),
                }
            )
            part_dir.mkdir(parents=True, exist_ok=True)
            tmp_path = file_path.with_suffix(f".{os.getpid()}.tmp")
            try:
                pq.write_table(table, tmp_path)
                os.replace(tmp_path, file_path)
            except PermissionError:  # RULE-ONE：防御 tmp 残留
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
                raise
            files_written += 1
        log.info("离线仓写入 %s: %d 行 / %d 新文件（root=%s）", layer, len(validated), files_written, self._root)
        return WriteReceipt(
            layer=layer,
            rows_written=len(validated),
            files_written=files_written,
            partition_files=tuple(partition_files),
        )

    # ---------------------------------------------------------------- 读取

    def _layer_glob(self, layer: str) -> str:
        if layer not in LAYERS:
            raise ValueError(f"layer 非法（封闭集 {list(LAYERS)}）: {layer!r}")
        return (self._root / layer).as_posix() + "/**/*.parquet"

    def _has_files(self, layer: str) -> bool:
        layer_dir = self._root / layer
        return layer_dir.is_dir() and any(layer_dir.rglob("*.parquet"))

    def read(
        self,
        layer: str,
        *,
        conn=None,
        factor_names: Sequence[str] | None = None,
        start: str | None = None,
        end: str | None = None,
        quality: Sequence[str] | None = None,
    ) -> list[dict]:
        """DuckDB 批量读取：因子/日期区间/质量过滤 + 同键重算取 computed_at 最新。

        Args:
            layer: 目录（daily/intraday/snapshots）。
            conn: duckdb 连接（注入式；None 时新建 :memory: 连接）。
            factor_names: 因子名过滤（None=全部）。
            start / end: trade_date 闭区间（None=不限；ISO 字典序=时序）。
            quality: 质量标记过滤（None=DEFAULT_READ_QUALITY 排除 quarantined）。

        Returns:
            list[dict]：7 列行（trade_date/symbol/factor_name 排序）；空仓→[]。
        """
        if not self._has_files(layer):
            return []
        if conn is None:
            import duckdb

            conn = duckdb.connect(":memory:")

        quality_flags = tuple(quality) if quality is not None else DEFAULT_READ_QUALITY
        unknown = [q for q in quality_flags if q not in QUALITY_FLAGS]
        if unknown:
            raise ValueError(f"quality 过滤含非法标记: {unknown!r}")
        for bound, name in ((start, "start"), (end, "end")):
            if bound is not None and not _TRADE_DATE_RE.match(bound):
                raise ValueError(f"{name} 日期边界非法（需 ISO YYYY-MM-DD）: {bound!r}")
        where = ["quality_flag IN (" + ", ".join("?" for _ in quality_flags) + ")"]
        params: list = list(quality_flags)
        if factor_names is not None:
            names = [str(n) for n in factor_names]
            if not names:
                return []
            where.append("factor_name IN (" + ", ".join("?" for _ in names) + ")")
            params.extend(names)
        if start is not None:
            where.append("trade_date >= ?")
            params.append(start)
        if end is not None:
            where.append("trade_date <= ?")
            params.append(end)

        glob_literal = _quote_literal(self._layer_glob(layer))
        cols = ", ".join(SCHEMA_COLUMNS)
        dedup_keys = ", ".join(_DEDUP_KEY)
        sql = (
            f"SELECT {cols} FROM ("
            f"  SELECT {cols}, ROW_NUMBER() OVER ("
            f"    PARTITION BY {dedup_keys} ORDER BY computed_at DESC, factor_name"
            f"  ) AS _rn"
            f"  FROM read_parquet({glob_literal}, hive_partitioning=False)"
            f"  WHERE {' AND '.join(where)}"
            f") WHERE _rn = 1 ORDER BY trade_date, symbol, factor_name"
        )
        cursor = conn.execute(sql, params)
        out_cols = [d[0] for d in cursor.description]
        return [dict(zip(out_cols, record, strict=False)) for record in cursor.fetchall()]
