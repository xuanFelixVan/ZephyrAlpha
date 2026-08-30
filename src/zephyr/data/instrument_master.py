# [BLUEPRINT] 90_methodology_open_questions.md §18（v2.0.0 裁定）
# [MODULE] zephyr.data.instrument_master
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（DDL 常量+纯行规范化；ClickHouse 写入由调用方注入）
# [CONSUMERS] 盘前 xtdata 同步脚本（接线待排期，本批仅交付模块本体）；universe_registry eligibility 联动（#15）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 最小字段集拒绝重型 IM；ST 状态 PIT 子表 effective_date 追溯；板块决定涨跌幅与最小申报单位
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 必填字段缺失/非法枚举→ValueError
# [TESTS] tests/data/test_instrument_master.py
# [A_module] module_id=MOD-L00-IM | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



D_DATA — 轻量 Instrument Master（90 号 Phase2 项，#18 资产覆盖轻量 IM）

裁定真源：90_methodology_open_questions.md §18（v2.0.0）：
  ① 采纳轻量 IM——拒绝机构 200+ 字段重型系统（公认过度设计教训），
     miniQMT 标的信息 + ClickHouse 补充字段；
  ② 最小字段集：15 字段 + A 股必需补充——板块代码（主板/科创/创业/北证，决定
     涨跌幅 ±10%/20%/30%）、ST/*ST 标志及变更日期、退市整理期标志、上市日期
     （次新过滤）、停牌标志、昨收价（算涨跌停价）、最小申报单位（主板 100 股/
     科创板 200 股起）；
  ③ ST 状态 PIT 跟踪采纳（effective_date 子表，A 股特有需求，防回测幸存者偏差）。

注意：本模块为 90 号 Phase2 交付物，MATURITY=testing；盘前 xtdata 同步接线
挂起待 Owner（宪章 B-007 纪律）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: raw 参数
#   fields: 参数 raw，类型注解 dict
#   code: instrument_master.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① normalize_instrument_row
#   name_en: normalize_instrument_row
#   intro: 规范化一行 IM 记录（盘前同步写入前校验+默认值派生）。
#   desc: 规范化一行 IM 记录（盘前同步写入前校验+默认值派生）。 Args: raw: 原始标的信息 dict（数据源字段已映射为 IM 字段名） Returns: 规范化后的 dic…；源码 L125-L151
#   inputs: raw
#   outputs: dict
# 层: 输出
# - id: O1
#   name_zh: dict
#   name_en: dict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 盘前 xtdata 同步脚本（接线待排期，本批仅交付模块本体）；universe_registry eligibility 联动（#15）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

__all__ = [
    "INSTRUMENT_MASTER_DDL",
    "ST_STATUS_PIT_DDL",
    "IM_REQUIRED_FIELDS",
    "normalize_instrument_row",
]

#: 轻量 IM 主表 DDL（ClickHouse；ReplacingMergeTree 与项目 PIT 版本语义一致）
INSTRUMENT_MASTER_DDL: str = """
CREATE TABLE IF NOT EXISTS instrument_master (
    symbol String,                          -- 证券代码（canonical ID 之一）
    exchange LowCardinality(String),        -- 交易所 SH/SZ/BJ
    security_type LowCardinality(String),   -- stock/etf/lof/reits/cb
    board LowCardinality(String),           -- 板块 main/star/gem/bse（决定涨跌幅 ±10%/20%/30%）
    list_date Date,                         -- 上市日期（次新过滤）
    delist_date Nullable(Date),             -- 退市日期
    is_st UInt8,                            -- ST/*ST 标志
    st_change_date Nullable(Date),          -- ST 状态变更日期
    in_delisting_period UInt8,              -- 退市整理期标志
    is_suspended UInt8,                     -- 停牌标志
    prev_close Float64,                     -- 昨收价（算涨跌停价）
    min_order_unit UInt32,                  -- 最小申报单位（主板100股/科创板200股起）
    float_shares Float64,                   -- 流通股本（90 号 #15 市值分层取数）
    industry String DEFAULT '',             -- 行业分类
    updated_at DateTime                     -- ReplacingMergeTree 版本列
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY symbol
""".strip()

#: ST 状态 PIT 子表 DDL（裁定③：effective_date 追溯 ST/*ST 变更）
ST_STATUS_PIT_DDL: str = """
CREATE TABLE IF NOT EXISTS instrument_st_status_pit (
    symbol String,
    effective_date Date,                    -- ST 状态生效日期（PIT）
    is_st UInt8,
    note String DEFAULT '',
    updated_at DateTime
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (symbol, effective_date)
""".strip()

#: 必填字段（轻量 IM 最小核）
IM_REQUIRED_FIELDS: tuple[str, ...] = (
    "symbol",
    "exchange",
    "security_type",
    "board",
    "list_date",
)

_VALID_EXCHANGES = frozenset({"SH", "SZ", "BJ"})
_VALID_BOARDS = frozenset({"main", "star", "gem", "bse"})

#: 板块默认最小申报单位（主板/创业/北证 100 股；科创板 200 股起，裁定②）
_BOARD_MIN_ORDER_UNIT: dict[str, int] = {
    "main": 100,
    "gem": 100,
    "bse": 100,
    "star": 200,
}


def normalize_instrument_row(raw: dict) -> dict:
    """规范化一行 IM 记录（盘前同步写入前校验+默认值派生）。

    Args:
        raw: 原始标的信息 dict（数据源字段已映射为 IM 字段名）

    Returns:
        规范化后的 dict（补齐 min_order_unit 板块默认值）

    Raises:
        ValueError: 必填字段缺失 / exchange、board 非法
    """
    missing = [f for f in IM_REQUIRED_FIELDS if raw.get(f) in (None, "")]
    if missing:
        raise ValueError(f"IM 必填字段缺失: {missing}")

    exchange = str(raw["exchange"])
    if exchange not in _VALID_EXCHANGES:
        raise ValueError(f"非法交易所代码: {exchange}（须 SH/SZ/BJ）")
    board = str(raw["board"])
    if board not in _VALID_BOARDS:
        raise ValueError(f"非法板块代码: {board}（须 main/star/gem/bse）")

    row = dict(raw)
    if row.get("min_order_unit") in (None, ""):
        row["min_order_unit"] = _BOARD_MIN_ORDER_UNIT[board]
    return row
