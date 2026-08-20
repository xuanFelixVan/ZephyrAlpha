# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.quality_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: data
# category: quality_interface
# status: active
# created: "2026-05-05"
# ---

"""D_DATA — Data Quality Gate

数据质量门禁。对 D_DATA 接入的原始市场数据进行质量校验，不合格数据拒绝下发。

核心职责：
  - 行情质量评分（缺失检测、异常值检测、时间戳校验）
  - 停牌/涨跌停检测
  - 质量问题分级告警：DataQualityError（CTR-ERR-001）

CTR 契约：
  生产者 — CTR-ERR-001 (DataQualityError) -> D_FACTOR

依赖方向：D_DATA 内部——provider -> quality_gate -> 下游 D_FACTOR/D_SIGNAL/D_RESEARCH
"""

from __future__ import annotations

import abc
import inspect
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import ClassVar


class QualityFailureReason(str, Enum):
    MISSING_TICK = "missing_tick"
    STALE_DATA = "stale_data"
    OUTLIER_PRICE = "outlier_price"
    TIMESTAMP_FUTURE = "timestamp_future"
    SUSPENSION_DETECTED = "suspension_detected"
    VOLUME_ZERO = "volume_zero"


class RecoveryHint(str, Enum):
    RETRY = "RETRY"
    SKIP_SYMBOL = "SKIP_SYMBOL"
    SWITCH_SOURCE = "SWITCH_SOURCE"
    HALT = "HALT"


@dataclass(frozen=True)
class QualityReport:
    """单条数据质量校验报告"""

    symbol: str
    quality_score: float  # 0.0 ~ 1.0，< 0.7 不合格
    passed: bool
    failure_reason: QualityFailureReason | None = None
    failed_field: str | None = None
    failed_value: str | None = None
    recovery_hint: RecoveryHint = RecoveryHint.SKIP_SYMBOL
    checked_at: datetime = field(default_factory=datetime.utcnow)


class DataQualityGate(abc.ABC):
    """数据质量门禁抽象基类（OCP 扩展点）

    实现者要求：
      - check(): 逐条校验行情数据，返回 QualityReport
      - quality_score < 0.7 时 MUST 抛出 DataQualityError（CTR-ERR-001）
      - 停牌标的 MUST 标记 is_suspended=True 而非静默跳过
      - 每种 failure_reason 必须给出对应的 recovery_hint

    安全约束：
      - 禁止静默丢弃数据——不合格必须显式抛出 CTR-ERR-001
      - 禁止降级质量阈值——0.7 是硬编码最低线
    """

    QUALITY_THRESHOLD: ClassVar[float] = 0.7
    # Phase-B 骨架，插件注册表备将来发现（__init_subclass__ 自动注册，读取侧工厂待 Phase-B 落地）
    _registry: ClassVar[dict[str, type[DataQualityGate]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls) and "__gate_id__" in cls.__dict__:
            DataQualityGate._registry[cls.__gate_id__] = cls

    @abc.abstractmethod
    def check(
        self,
        symbol: str,
        open_price: Decimal,
        high: Decimal,
        low: Decimal,
        close: Decimal,
        volume: Decimal,
        timestamp: datetime,
        prev_close: Decimal | None = None,
    ) -> QualityReport:
        """对单条行情数据执行质量校验"""
        ...

    @staticmethod
    def is_within_normal_range(price: Decimal, prev_close: Decimal, limit_pct: Decimal = Decimal("0.10")) -> bool:
        """涨跌停范围校验（A 股 ±10%，科创板/创业板 ±20%）"""
        if prev_close <= Decimal("0"):
            return False
        change_pct = abs(price - prev_close) / prev_close
        return change_pct <= limit_pct


__all__ = [
    "DataQualityGate",
    "QualityFailureReason",
    "QualityReport",
    "RecoveryHint",
    "MarketDataValidator",
    "apply_quality_gate",
]


# ---------------------------------------------------------------------------
# #ARCH-CH-021 P0-4: 写入路径异常值校验器（轻量，4 条门禁）
#
# quality_flag 语义（裁定 #ARCH-CH-021 P0-4，2026-07-23）：
#   1 = 已校验通过（validated passed）
#   0 = 检出异常（anomaly detected，保真标记，行保留供审计）
# 列默认 DEFAULT 1 原意为"未触碰"，本裁定将其语义反转为"已校验通过"——
# 凡经过 apply_quality_gate 的行：通过=1，异常=0。未经校验的行仍带默认 1，
# 但语义为"未校验"（全链路对齐后下游可据 ingest_ts/quality_flag 联合判定）。
# 四条门禁（单行级，无 DB 查询，写入路径轻量）：
#   1. OHLC 逻辑：high >= max(open,close) >= min(open,close) >= low > 0
#   2. 涨跌幅：|close - ref|/ref <= change_limit（ref=prev_close 优先，否则 open；
#      默认阈值且有 symbol 列时按板块推断：北交所 0.30/科创创业 0.20/主板 0.10，#209③）
#   3. 缺口/振幅：intraday 振幅 (high-low)/open <= swing_limit（防数据错位）
#   4. 复权：若 adj_factor 列存在，0 < adj_factor <= adj_max
# ---------------------------------------------------------------------------

# OHLC 列名别名（小写匹配），覆盖 open_price/openPrice 等
_OHLC_ALIASES = {
    "open": ("open", "open_price", "openprice", "open_px"),
    "high": ("high", "high_price", "highprice", "high_px"),
    "low": ("low", "low_price", "lowprice", "low_px"),
    "close": ("close", "close_price", "closeprice", "close_px", "last", "last_price"),
}
_VOLUME_ALIASES = ("volume", "vol", "volume_long", "turnover_vol")
_ADJ_ALIASES = ("adj_factor", "adjust_factor", "adjustfactor", "adjfactor")
_PREVCLOSE_ALIASES = ("prev_close", "pre_close", "preclose", "yesterday_close")
_QFLAG_ALIASES = ("quality_flag", "qflag", "quality", "qf")
# 标的代码列名别名（板块推断用；词表对齐 pit_manager.INSTRUMENT_COLUMN_CANDIDATES）
_SYMBOL_ALIASES = ("symbol", "ticker", "code", "instrument", "ts_code")
# 涨跌幅门禁默认阈值（向后兼容基准值；默认构造时按 symbol 板块推断覆盖）
_DEFAULT_CHANGE_LIMIT = Decimal("0.20")


def _to_decimal(v):
    """安全转 Decimal；None/NaN/非数值返回 None。"""
    if v is None:
        return None
    try:
        from math import isnan

        if isinstance(v, float) and isnan(v):
            return None
        d = Decimal(str(v))
        return d
    except Exception:
        return None


def _detect_column_index(columns, aliases):
    """在 columns 列表里按别名（小写）找首个匹配列的索引，找不到返回 None。"""
    lower_cols = {c.lower(): i for i, c in enumerate(columns)}
    for alias in aliases:
        if alias in lower_cols:
            return lower_cols[alias]
    return None


def _gate_ohlc_logic(o, h, l, c):
    """门禁1：OHLC 结构一致性。"""
    if None in (o, h, l, c):
        return False
    return o > 0 and h > 0 and l > 0 and c > 0 and h >= o and h >= c and l <= o and l <= c and h >= l


def _gate_price_change(o, c, prev_c, change_limit):
    """门禁2：涨跌幅。prev_c 优先作基准，否则用 open。"""
    ref = prev_c if prev_c and prev_c > 0 else (o if o and o > 0 else None)
    if ref is None or c is None:
        return True  # 无基准不校验（保守放行）
    return abs(c - ref) / ref <= change_limit


def _gate_swing(o, h, l, swing_limit):
    """门禁3：日内振幅 (high-low)/open，防数据错位导致的异常宽幅。"""
    if None in (o, h, l) or o <= 0:
        return True  # 无基准不校验
    return (h - l) / o <= swing_limit


def _gate_adjustment(adj, adj_max):
    """门禁4：复权因子合理性 0 < adj_factor <= adj_max。"""
    if adj is None:
        return True  # 无复权列不校验
    return 0 < adj <= adj_max


def _infer_change_limit(symbol, default: Decimal) -> Decimal:
    """按代码前缀推断板块涨跌幅门禁阈值（2026-08-20 AI-NIGHT-001 #209③）。

    口径与 matching_engine._infer_limit_pct 对齐（同源板块规则）：
    北交所(4xx/8xx/92x) ±30%、科创(68x)/创业(30x) ±20%、其余 6 位数字 A 股
    主板 ±10%；无法识别的代码（港股/指数前缀外异形/空值）回退 default
    （保守不误伤未知板块）。修复原默认 0.20 一刀切将北交所 ±30% 合法行
    误标 quality_flag=0 的问题；显式自定义 change_limit 时不调用本推断
    （调用方显式接管阈值，保持完全向后兼容）。
    """
    code = str(symbol or "").strip().split(".")[0]
    if code.startswith(("68", "30")):
        return Decimal("0.20")
    if code.startswith(("4", "8", "92")):
        return Decimal("0.30")
    if len(code) == 6 and code.isdigit():
        return Decimal("0.10")
    return default


class MarketDataValidator:
    """写入路径轻量异常值校验器（#ARCH-CH-021 P0-4）。

    四条门禁逐行校验 OHLC 行情数据，异常行置 quality_flag=0（保留行供审计）。
    设计为无副作用、无 DB 查询、O(n) 复杂度，可在 ch_writer.write_result 批量写入前调用。
    """

    def __init__(self, change_limit=_DEFAULT_CHANGE_LIMIT, swing_limit=Decimal("0.30"), adj_max=Decimal("1000")):
        self.change_limit = change_limit
        self.swing_limit = swing_limit
        self.adj_max = adj_max


def _build_col_map(columns):
    """构造列名→索引映射（OHLC/volume/adj/prev_close/quality_flag）。无 dict 返回 None。"""
    idx = {}
    for field, aliases in _OHLC_ALIASES.items():
        i = _detect_column_index(columns, aliases)
        if i is not None:
            idx[field] = i
    has_ohlc = all(k in idx for k in ("open", "high", "low", "close"))
    if not has_ohlc:
        return None
    for key, aliases in (
        ("volume", _VOLUME_ALIASES),
        ("adj_factor", _ADJ_ALIASES),
        ("prev_close", _PREVCLOSE_ALIASES),
        ("quality_flag", _QFLAG_ALIASES),
        ("symbol", _SYMBOL_ALIASES),
    ):
        i = _detect_column_index(columns, aliases)
        if i is not None:
            idx[key] = i
    return idx


def apply_quality_gate(table, columns, rows, validator=None):
    """对批量行执行四门禁校验，异常行置 quality_flag=0。

    Args:
        table: 表名（仅用于日志/统计）
        columns: 列名列表（与 rows 列序对齐）
        rows: 行列表（list of tuple/list）
        validator: MarketDataValidator 实例，None 用默认

    Returns:
        (rows, stats): rows 为处理后的行列表（异常行 quality_flag=0），
        stats = {"table", "total", "checked", "flagged", "by_gate"}
    """
    v = validator or MarketDataValidator()
    col_map = _build_col_map(list(columns))
    stats = {
        "table": table,
        "total": len(rows),
        "checked": 0,
        "flagged": 0,
        "by_gate": {"ohlc": 0, "change": 0, "swing": 0, "adj": 0},
    }
    if col_map is None:
        return rows, stats  # 非 OHLC 表，跳过
    qf_idx = col_map.get("quality_flag")
    pc_idx = col_map.get("prev_close")
    adj_idx = col_map.get("adj_factor")
    sym_idx = col_map.get("symbol")
    # #209③：默认阈值（0.20 未自定义）且有 symbol 列时按板块推断逐行阈值；
    # 显式自定义 change_limit 的 validator 视为调用方接管，保持原一刀切行为
    board_aware = v.change_limit == _DEFAULT_CHANGE_LIMIT
    out_rows = []
    for row in rows:
        r = list(row)
        o = _to_decimal(r[col_map["open"]])
        h = _to_decimal(r[col_map["high"]])
        l = _to_decimal(r[col_map["low"]])
        c = _to_decimal(r[col_map["close"]])
        pc = _to_decimal(r[pc_idx]) if pc_idx is not None else None
        adj = _to_decimal(r[adj_idx]) if adj_idx is not None else None
        stats["checked"] += 1
        ok = True
        if not _gate_ohlc_logic(o, h, l, c):
            ok = False
            stats["by_gate"]["ohlc"] += 1
        change_limit = v.change_limit
        if board_aware and sym_idx is not None:
            change_limit = _infer_change_limit(r[sym_idx], v.change_limit)
        if not _gate_price_change(o, c, pc, change_limit):
            ok = False
            stats["by_gate"]["change"] += 1
        if not _gate_swing(o, h, l, v.swing_limit):
            ok = False
            stats["by_gate"]["swing"] += 1
        if not _gate_adjustment(adj, v.adj_max):
            ok = False
            stats["by_gate"]["adj"] += 1
        if not ok:
            stats["flagged"] += 1
            if qf_idx is not None:
                r[qf_idx] = 0
        out_rows.append(tuple(r) if isinstance(row, tuple) else r)
    if stats["flagged"]:
        import logging

        logging.getLogger("zephyr.data.quality_gate").info(
            "apply_quality_gate(%s): %d/%d rows flagged (ohlc=%d change=%d swing=%d adj=%d)",
            table,
            stats["flagged"],
            stats["checked"],
            stats["by_gate"]["ohlc"],
            stats["by_gate"]["change"],
            stats["by_gate"]["swing"],
            stats["by_gate"]["adj"],
        )
    return out_rows, stats
