# [BLUEPRINT] MOD-L02-FS | docs/03_modules/_domain_factor/blueprint.md | 15 号 §3.4 要点④
# [MODULE] zephyr.factor.feature_store_writer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] schemas.categories.factor_feature_value(DDL 真源); zephyr.data.ch_writer(写入,延迟加载)
# [CONSUMERS] FactorDAG 批量计算产物落库（管道代码就位，未挂调度不执行）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 列序以 schemas INSERT_COLUMNS 为唯一真源; 预热期 NaN→NULL 不前向填充(PIT); 缺列即抛不静默
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 缺必需列->ValueError; CH client 不可得->RuntimeError
# [TESTS] tests/factor/test_feature_store_writer.py
# [A_module] module_id=MOD-L02-FS-WRITER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #15_data_feature_layer_spec §3.4 特征仓库存储层
# [ALGO_FLOW]
# I1: 长表特征值 DataFrame(trade_date/symbol/factor_id/value) + factor_version + 可选 client(注入式)
# F1: build_feature_value_rows(校验必需列 → 对齐 INSERT_COLUMNS 的行 tuple；NaN→None 保 NULL 语义)
# F2: write_feature_values(空输入短路 0；client 缺省延迟取 get_client；分块 INSERT c1_market.factor_feature_value)
# O1: 行 tuple 列表 / 写入行数 int
# [/ALGO_FLOW]
"""


特征仓库写入管道（15_data_feature_layer_spec §3.4 要点④存储层）。

**状态：管道代码就位、不执行**——DDL apply 属 Owner 窗口（表不存在时执行本
模块写入会失败，属预期）；调度挂接（internal_compute 同族任务）亦未登记。

设计对齐 15 号 §3.4 轻量三层裁定：
  - 输入为**长表**（trade_date/symbol/factor_id/value 四列一行一值），与
    FactorDAG 批量计算的天然产物形态一致；列序以 schemas/categories/
    factor_feature_value.py 的 INSERT_COLUMNS 为唯一真源（禁硬编码表结构）。
  - 预热期 NaN → None（CH NULL）：不前向填充（15 号 §3.4 FactorSignal NaN
    裁定——ffill 是 FactorSignal 流转层策略，存储层保 NULL 原貌供审计）。
  - factor_version 随行写入（SemVer，62 号版本层：不建独立特征版本服务）。

依据: 15_data_feature_layer_spec v1.0.3 §3.4

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: values 参数
#   fields: 参数 values，类型注解 pd.DataFrame
#   code: feature_store_writer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: factor_version 参数
#   fields: 参数 factor_version，类型注解 str
#   code: feature_store_writer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: data_source 参数
#   fields: 参数 data_source，类型注解 str
#   code: feature_store_writer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: client 参数
#   fields: 参数 client（无注解）
#   code: feature_store_writer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_feature_value_rows
#   name_en: build_feature_value_rows
#   intro: 长表特征值 → INSERT 行 tuple 列表（列序对齐 INSERT_COLUMNS）。
#   desc: 长表特征值 → INSERT 行 tuple 列表（列序对齐 INSERT_COLUMNS）。 Args: values: 长表 DataFrame，必需列 trade_date…；源码 L135-L173
#   inputs: values factor_version data_source
#   outputs: list[tuple]
# - id: A2
#   name_zh: ② write_feature_values
#   name_en: write_feature_values
#   intro: 特征值写入 c1_market.factor_feature_value（分块 INSERT）。
#   desc: 特征值写入 c1_market.factor_feature_value（分块 INSERT）。 **不执行声明**：本函数仅供特征仓库管道调用；DDL 未 apply（Owne…；源码 L176-L212
#   inputs: values client factor_version data_source chunk_size
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: list[tuple]
#   name_en: list[tuple]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: FactorDAG 批量计算产物落库（管道代码就位，未挂调度不执行）
# - id: O2
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: FactorDAG 批量计算产物落库（管道代码就位，未挂调度不执行）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import pathlib
import sys

import pandas as pd

log = logging.getLogger(__name__)

try:
    from schemas.categories.factor_feature_value import (
        DATABASE,
        INSERT_COLUMNS,
        TABLE_NAME,
    )
except ImportError:  # pragma: no cover — 脚本直跑时项目根不在 sys.path
    _ROOT = str(pathlib.Path(__file__).resolve().parents[3])
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from schemas.categories.factor_feature_value import (
        DATABASE,
        INSERT_COLUMNS,
        TABLE_NAME,
    )

__all__ = ["build_feature_value_rows", "write_feature_values"]

_REQUIRED_COLUMNS = ("trade_date", "symbol", "factor_id", "value")
_FULL_TABLE = f"{DATABASE}.{TABLE_NAME}"


def _get_ch_client():
    """延迟加载 CH 写入客户端（ch_writer 不可用时返回 None，由调用方抛错）。"""
    from zephyr.data.ch_writer import get_client

    return get_client()


def build_feature_value_rows(
    values: pd.DataFrame,
    factor_version: str = "0.0.0",
    data_source: str = "factor_dag",
) -> list[tuple]:
    """长表特征值 → INSERT 行 tuple 列表（列序对齐 INSERT_COLUMNS）。

    Args:
        values: 长表 DataFrame，必需列 trade_date/symbol/factor_id/value。
        factor_version: 因子 SemVer 版本（62 号版本层）。
        data_source: 数据来源标记（默认 factor_dag=本地计算）。

    Returns:
        list[tuple]：(trade_date, symbol, factor_id, factor_version, value, data_source)；
        value 为 NaN 时写 None（CH NULL，预热期原貌）。

    Raises:
        ValueError: 缺必需列。
    """
    missing = [c for c in _REQUIRED_COLUMNS if c not in values.columns]
    if missing:
        raise ValueError(f"特征值长表缺必需列: {missing}（需要 {list(_REQUIRED_COLUMNS)}）")
    if len(values) == 0:
        return []
    rows: list[tuple] = []
    for td, sym, fid, val in zip(
        values["trade_date"], values["symbol"], values["factor_id"], values["value"], strict=False
    ):
        rows.append(
            (
                pd.Timestamp(td).date(),
                str(sym),
                str(fid),
                factor_version,
                None if pd.isna(val) else float(val),
                data_source,
            )
        )
    return rows


def write_feature_values(
    values: pd.DataFrame,
    *,
    client=None,
    factor_version: str = "0.0.0",
    data_source: str = "factor_dag",
    chunk_size: int = 100_000,
) -> int:
    """特征值写入 c1_market.factor_feature_value（分块 INSERT）。

    **不执行声明**：本函数仅供特征仓库管道调用；DDL 未 apply（Owner 窗口）前
    执行将因表不存在失败，属预期。测试经 client 注入验证，不触库。

    Args:
        values: 长表 DataFrame（见 build_feature_value_rows）。
        client: clickhouse-driver Client（注入式；None 时延迟取 ch_writer.get_client）。
        factor_version / data_source: 见 build_feature_value_rows。
        chunk_size: 单批 INSERT 行数。

    Returns:
        写入行数（空输入短路返回 0，不触库）。

    Raises:
        RuntimeError: client 未注入且 ch_writer 不可得。
    """
    rows = build_feature_value_rows(values, factor_version, data_source)
    if not rows:
        return 0
    if client is None:
        client = _get_ch_client()
    if client is None:
        raise RuntimeError("clickhouse-driver 不可用（client 未注入且 get_client 返回 None）")
    sql = f"INSERT INTO {_FULL_TABLE} {INSERT_COLUMNS} VALUES"
    for i in range(0, len(rows), chunk_size):
        client.execute(sql, rows[i : i + chunk_size])
    log.info("特征值写入 %s: %d 行（factor_version=%s）", _FULL_TABLE, len(rows), factor_version)
    return len(rows)
