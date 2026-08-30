# [BLUEPRINT] MOD-DAT-REF-DATA | docs/03_modules/_domain_data/reference_data_manager/blueprint.md
# [MODULE] zephyr.data.reference_data_manager
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（判定核心纯内存；event_publisher 注入）
# [CONSUMERS] 运行时装配批（SQLite 建表读写 / event_publisher 接 event_bus / akshare 行业与指数成分采集接线）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 行业分类双码全空 Fail-Closed；指数成分 PIT effective_date/removed_date 时点语义；ID 映射确定性翻译缺失返回 None；publisher 异常不阻断登记
# [MODIFY-GUARD] docs/03_modules/_domain_data/reference_data_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 symbol/空指数码/未知映射源→ValueError；映射缺失→None 留痕
# [TESTS] tests/zephyr/data/test_reference_data_manager.py
# [A_module] module_id=MOD-DAT-REF-DATA | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



ReferenceDataManager — 参考数据管理器（MOD-DAT-REF-DATA）

B13-04240（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，D-DATA-08，§17.1）：
行业分类（GICS+申万）、指数成分（PIT effective_date）、多源 ID 映射
（miniqmt↔tushare↔akshare）登记/查询/变更事件发布；SQLite reference_data
表族 DDL 常量随模块交付（建库执行留装配批）。

查重裁定：instrument_master（MOD-L00-IM）为轻量 IM 15 字段+ST/板块 PIT
最小核，本模块复用其最小字段集为锚、不复制，只补行业分类/指数成分/多源
映射/变更事件四项缺口。B13-04355（D-TRADING-14）dig 已裁定重复并入本模块。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: event_publisher 参数
#   fields: 参数 event_publisher（无注解）
#   code: reference_data_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ReferenceDataManager
#   name_en: ReferenceDataManager
#   intro: 参考数据管理器（判定核心纯内存，事件外发注入式）。
#   desc: 参考数据管理器（判定核心纯内存，事件外发注入式）。；公共方法（定义序）: change_events, upsert_industry, industry_of, set_index_constituent, remo…
#   inputs: event_publisher
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: ReferenceDataManager
#   downstream: 运行时装配批（SQLite 建表读写 / event_publisher 接 event_bus / akshare 行业与指数成分采集接线）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final, Optional

log = logging.getLogger(__name__)

__all__: Final = [
    "IdMapping",
    "IndexConstituent",
    "IndustryRecord",
    "RefChangeEvent",
    "ReferenceDataManager",
    "REF_ID_MAPPING_DDL",
    "REF_INDEX_CONSTITUENT_DDL",
    "REF_INDUSTRY_DDL",
]

#: 行业分类表 DDL（SQLite；GICS+申万双轨）
REF_INDUSTRY_DDL: Final[str] = """
CREATE TABLE IF NOT EXISTS ref_industry_classification (
    symbol TEXT NOT NULL,
    gics TEXT DEFAULT '',
    sw TEXT DEFAULT '',
    source TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (symbol, source)
)
""".strip()

#: 指数成分表 DDL（SQLite；PIT effective_date/removed_date）
REF_INDEX_CONSTITUENT_DDL: Final[str] = """
CREATE TABLE IF NOT EXISTS ref_index_constituent (
    index_code TEXT NOT NULL,
    symbol TEXT NOT NULL,
    effective_date TEXT NOT NULL,
    removed_date TEXT DEFAULT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (index_code, symbol, effective_date)
)
""".strip()

#: 多源 ID 映射表 DDL（SQLite；miniqmt↔tushare↔akshare）
REF_ID_MAPPING_DDL: Final[str] = """
CREATE TABLE IF NOT EXISTS ref_id_mapping (
    symbol TEXT NOT NULL PRIMARY KEY,
    minqmt TEXT DEFAULT NULL,
    tushare TEXT DEFAULT NULL,
    akshare TEXT DEFAULT NULL,
    updated_at TEXT NOT NULL
)
""".strip()

MAPPING_SOURCES: Final = ("minqmt", "tushare", "akshare")


@dataclass(frozen=True)
class IndustryRecord:
    symbol: str
    gics: str
    sw: str
    source: str
    updated_at: datetime.datetime


@dataclass(frozen=True)
class IndexConstituent:
    index_code: str
    symbol: str
    effective_date: datetime.date
    removed_date: datetime.date | None = None


@dataclass(frozen=True)
class IdMapping:
    symbol: str
    minqmt: str | None = None
    tushare: str | None = None
    akshare: str | None = None


@dataclass(frozen=True)
class RefChangeEvent:
    kind: str
    payload: dict
    occurred_at: datetime.datetime


class ReferenceDataManager:
    """参考数据管理器（判定核心纯内存，事件外发注入式）。"""

    def __init__(self, event_publisher: Callable[[RefChangeEvent], None] | None = None) -> None:
        self._publisher = event_publisher
        self._industry: dict[str, IndustryRecord] = {}
        self._constituents: list[IndexConstituent] = []
        self._mappings: dict[str, IdMapping] = {}
        self._events: list[RefChangeEvent] = []

    # ── 事件 ──

    def _emit(self, kind: str, payload: dict) -> None:
        evt = RefChangeEvent(
            kind=kind,
            payload=dict(payload),
            occurred_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self._events.append(evt)
        if self._publisher is not None:
            try:
                self._publisher(evt)
            except Exception as exc:  # noqa: BLE001 — publisher 异常不阻断登记
                log.warning("event_publisher 异常: %s", exc)

    @property
    def change_events(self) -> tuple[RefChangeEvent, ...]:
        return tuple(self._events)

    # ── 行业分类 ──

    def upsert_industry(
        self,
        symbol: str,
        gics: str | None = None,
        sw: str | None = None,
        source: str = "manual",
    ) -> IndustryRecord:
        if not symbol:
            raise ValueError("symbol 不能为空")
        if not gics and not sw:
            raise ValueError("gics 与 sw 至少填一项")
        rec = IndustryRecord(
            symbol=symbol,
            gics=gics or "",
            sw=sw or "",
            source=source,
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self._industry[symbol] = rec
        self._emit("industry_upsert", {"symbol": symbol, "gics": rec.gics, "sw": rec.sw})
        return rec

    def industry_of(self, symbol: str) -> IndustryRecord | None:
        return self._industry.get(symbol)

    # ── 指数成分（PIT）──

    def set_index_constituent(self, index_code: str, symbol: str, effective_date: datetime.date) -> IndexConstituent:
        if not index_code:
            raise ValueError("index_code 不能为空")
        if not symbol:
            raise ValueError("symbol 不能为空")
        rec = IndexConstituent(index_code=index_code, symbol=symbol, effective_date=effective_date)
        self._constituents.append(rec)
        self._emit(
            "index_constituent_add",
            {"index_code": index_code, "symbol": symbol, "effective_date": str(effective_date)},
        )
        return rec

    def remove_index_constituent(self, index_code: str, symbol: str, removed_date: datetime.date) -> None:
        active = [
            c
            for c in self._constituents
            if c.index_code == index_code and c.symbol == symbol and c.removed_date is None
        ]
        if not active:
            raise ValueError(f"无在册成分可移除: {index_code}/{symbol}")
        latest = max(active, key=lambda c: c.effective_date)
        if removed_date < latest.effective_date:
            raise ValueError("removed_date 早于 effective_date")
        self._constituents.append(
            IndexConstituent(
                index_code=index_code,
                symbol=symbol,
                effective_date=latest.effective_date,
                removed_date=removed_date,
            )
        )
        self._emit(
            "index_constituent_remove",
            {"index_code": index_code, "symbol": symbol, "removed_date": str(removed_date)},
        )

    def constituents_at(self, index_code: str, as_of: datetime.date) -> frozenset[str]:
        """PIT 查询：effective_date<=as_of 且（未移除或 removed_date>as_of）。"""
        best: dict[str, IndexConstituent] = {}
        for c in self._constituents:
            if c.index_code != index_code or c.effective_date > as_of:
                continue
            cur = best.get(c.symbol)
            if cur is None or c.effective_date >= cur.effective_date:
                if cur is not None and c.effective_date == cur.effective_date and cur.removed_date is not None:
                    continue  # 同 effective_date 保留移除记录（后到优先）
                best[c.symbol] = c
        return frozenset(sym for sym, c in best.items() if c.removed_date is None or c.removed_date > as_of)

    # ── 多源 ID 映射 ──

    def register_mapping(
        self,
        symbol: str,
        minqmt: str | None = None,
        tushare: str | None = None,
        akshare: str | None = None,
    ) -> IdMapping:
        if not symbol:
            raise ValueError("symbol 不能为空")
        if not any([minqmt, tushare, akshare]):
            raise ValueError("minqmt/tushare/akshare 至少填一项")
        m = IdMapping(symbol=symbol, minqmt=minqmt, tushare=tushare, akshare=akshare)
        self._mappings[symbol] = m
        self._emit("id_mapping_register", {"symbol": symbol})
        return m

    def map_id(self, symbol: str, source: str, target: str) -> str | None:
        if source not in MAPPING_SOURCES:
            raise ValueError(f"未知映射源: {source!r}（合法: {MAPPING_SOURCES}）")
        if target not in MAPPING_SOURCES:
            raise ValueError(f"未知映射目标: {target!r}（合法: {MAPPING_SOURCES}）")
        m = self._mappings.get(symbol)
        if m is None:
            return None
        return getattr(m, target)
