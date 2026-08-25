# [BLUEPRINT] MOD-ALT-006 | docs/03_modules/_domain_alt_data/concept_factor_mapper/blueprint.md
# [MODULE] zephyr.alt_data.concept_factor_mapper
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.shared.foundation.errors（判定核心纯内存；行/版本全注入）
# [CONSUMERS] 运行时装配批（成分行接 akshare_provider market_concept_board 系列表产物；输出供 signal_ashare 与 sector_factor_manager attach_constituent_map 挂接位消费）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 判定核心纯内存无IO；单条非法Fail-Closed到条；PIT严格（asof仅取effective_date≤查询日最新版本）；索引双向字典序确定性；质量校验边界恰等不命中（<min/>max/距as_of>stale_days才报）；frozen dataclass asdict JSON可序列化；同输入必同输出；仅映射数据语义无下单含义
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/concept_factor_mapper/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] symbol/concept空白/effective_date非法→InvalidConceptRowError（单条Fail-Closed）；min/max/stale_days配置非法→InvalidConceptMapperConfigError（构造期Fail-Closed）
# [TESTS] tests/alt_data/test_concept_factor_mapper.py
# [A_module] module_id=MOD-ALT-006 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ConceptFactorMapper — 概念因子映射引擎（MOD-ALT-006）

B1-00596（AUD-DRAFT-001-DIGEST P1 波 W-P1-14，§1 子模块清单 37）：股票↔概念
映射字典 + 逆向索引（概念→成分）+ 质量校验（成分数合理性/更新及时性）+
映射变更 PIT 记录（effective_date 版本化 asof 查询）+ Excel 分号概念字段
解析兼容层（全角；/半角; 混用），输出供 signal_ashare 与板块因子（86）
消费。

查重裁定：akshare_provider（MOD-L00-004）=概念板块/成分**采集**
（market_concept_board 系列表，tasks.yaml 已接线）；sector_factor_manager
（MOD-L00-004）=板块覆盖校验/轮动因子化/质量评分，其 docstring 明示
"attach_constituent_map 注入式 provider（37 概念因子映射引擎产出位的挂接
点）"——本模块即该产出位；sector_ranking_engine=板块排名面。本模块为
个股↔概念统一映射入口，与采集/因子化/排名各面正交不重复。
"""

from __future__ import annotations

import datetime
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, Optional

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ConceptConstituentRow",
    "ConceptFactorMapper",
    "ConceptMapperConfig",
    "ConceptMappingIndex",
    "InvalidConceptMapperConfigError",
    "InvalidConceptRowError",
    "MappingVersion",
    "QualityIssue",
    "QualityReport",
]

_EXCEL_SEP_PATTERN: Final = re.compile(r"[;；]+")


class InvalidConceptRowError(ZephyrBaseError):
    """概念成分行非法（Fail-Closed 到条）。"""


class InvalidConceptMapperConfigError(ZephyrBaseError):
    """映射引擎配置非法（构造期 Fail-Closed）。"""


@dataclass(frozen=True)
class ConceptConstituentRow:
    """概念成分行（frozen；effective_date=映射生效日 PIT 锚）。"""

    symbol: str
    concept: str
    effective_date: datetime.date

    def __post_init__(self) -> None:
        for name in ("symbol", "concept"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v.strip():
                raise InvalidConceptRowError(f"{name} 不能为空: {v!r}")
            object.__setattr__(self, name, v.strip())
        if not isinstance(self.effective_date, datetime.date) or isinstance(
            self.effective_date, datetime.datetime
        ):
            raise InvalidConceptRowError(
                f"effective_date 必须为 date: {type(self.effective_date).__name__}"
            )


@dataclass(frozen=True)
class ConceptMappingIndex:
    """双向映射索引（frozen；两侧均字典序确定性）。"""

    symbol_to_concepts: Mapping[str, tuple[str, ...]]  # 股票→概念（字典序）
    concept_to_symbols: Mapping[str, tuple[str, ...]]  # 概念→成分（字典序逆向索引）
    row_count: int
    latest_effective_date: Optional[datetime.date]


@dataclass(frozen=True)
class MappingVersion:
    """映射版本（frozen；effective_date=该版生效日）。"""

    effective_date: datetime.date
    index: ConceptMappingIndex

    def __post_init__(self) -> None:
        if not isinstance(self.effective_date, datetime.date) or isinstance(
            self.effective_date, datetime.datetime
        ):
            raise InvalidConceptRowError(
                f"version effective_date 必须为 date: {type(self.effective_date).__name__}"
            )
        if not isinstance(self.index, ConceptMappingIndex):
            raise InvalidConceptRowError(f"index 类型非法: {type(self.index).__name__}")


@dataclass(frozen=True)
class QualityIssue:
    """质量问题（frozen；kind∈EMPTY_CONCEPT/OVERSIZED_CONCEPT/STALE_MAPPING）。"""

    kind: str
    concept: str  # STALE_MAPPING 为整体问题置空串
    detail: str


@dataclass(frozen=True)
class QualityReport:
    """质量校验报告（frozen）。"""

    issues: tuple[QualityIssue, ...]
    empty_count: int
    oversized_count: int
    stale: bool
    concept_count: int
    symbol_count: int


@dataclass(frozen=True)
class ConceptMapperConfig:
    """质量阈值（C 类可调；默认值=候选 spec 真源）。"""

    min_constituents: int = 2  # 成分数下限（< 才报 EMPTY_CONCEPT）
    max_constituents: int = 2000  # 成分数上限（> 才报 OVERSIZED_CONCEPT）
    stale_days: int = 30  # 更新及时性（距 as_of > 才报 STALE_MAPPING）

    def __post_init__(self) -> None:
        for name in ("min_constituents", "max_constituents", "stale_days"):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, int) or v <= 0:
                raise InvalidConceptMapperConfigError(f"{name} 必须为正 int: {v}")
        if self.min_constituents > self.max_constituents:
            raise InvalidConceptMapperConfigError(
                f"min_constituents({self.min_constituents}) 不能 > max_constituents({self.max_constituents})"
            )


class ConceptFactorMapper:
    """概念因子映射引擎（双向索引 + 质量校验 + PIT 版本判定核心）。

    Args:
        config: ConceptMapperConfig（None=默认阈值）
    """

    def __init__(self, config: ConceptMapperConfig | None = None) -> None:
        if config is not None and not isinstance(config, ConceptMapperConfig):
            raise InvalidConceptMapperConfigError(
                f"config 类型非法: {type(config).__name__}"
            )
        self._config = config or ConceptMapperConfig()

    @property
    def config(self) -> ConceptMapperConfig:
        return self._config

    @staticmethod
    def parse_excel_field(field: object) -> tuple[str, ...]:
        """Excel 分号概念字段解析兼容层：全角；/半角; 混用统一切分，保序去重。"""
        if not isinstance(field, str):
            return ()
        parts = [p.strip() for p in _EXCEL_SEP_PATTERN.split(field)]
        seen: list[str] = []
        for p in parts:
            if p and p not in seen:
                seen.append(p)
        return tuple(seen)

    def build(
        self, rows: Sequence[ConceptConstituentRow | Mapping[str, object]]
    ) -> tuple[ConceptMappingIndex, tuple[tuple[int, str], ...]]:
        """构建双向索引：非法行 rejected 留痕；(symbol, concept, effective_date) 去重。"""
        accepted: list[ConceptConstituentRow] = []
        errors: list[tuple[int, str]] = []
        seen: set[tuple[str, str, datetime.date]] = set()
        for idx, raw in enumerate(rows or []):
            try:
                row = (
                    raw
                    if isinstance(raw, ConceptConstituentRow)
                    else ConceptConstituentRow(**raw)  # type: ignore[arg-type]
                )
                key = (row.symbol, row.concept, row.effective_date)
                if key in seen:
                    continue  # 重复行去重（不记 rejected）
                seen.add(key)
                accepted.append(row)
            except Exception as exc:  # noqa: BLE001 —— 单条 Fail-Closed 到条
                errors.append((idx, f"{type(exc).__name__}: {exc}"))
        symbol_map: dict[str, set[str]] = {}
        concept_map: dict[str, set[str]] = {}
        latest: Optional[datetime.date] = None
        for row in accepted:
            symbol_map.setdefault(row.symbol, set()).add(row.concept)
            concept_map.setdefault(row.concept, set()).add(row.symbol)
            if latest is None or row.effective_date > latest:
                latest = row.effective_date
        index = ConceptMappingIndex(
            symbol_to_concepts={s: tuple(sorted(cs)) for s, cs in sorted(symbol_map.items())},
            concept_to_symbols={c: tuple(sorted(ss)) for c, ss in sorted(concept_map.items())},
            row_count=len(accepted),
            latest_effective_date=latest,
        )
        return index, tuple(errors)

    def check_quality(
        self, index: ConceptMappingIndex, as_of: datetime.date
    ) -> QualityReport:
        """质量校验：成分数合理性 + 更新及时性；issues 确定性排序。"""
        if not isinstance(index, ConceptMappingIndex):
            raise InvalidConceptRowError(f"index 类型非法: {type(index).__name__}")
        if not isinstance(as_of, datetime.date) or isinstance(as_of, datetime.datetime):
            raise InvalidConceptRowError(f"as_of 必须为 date: {type(as_of).__name__}")
        issues: list[QualityIssue] = []
        empty = 0
        oversized = 0
        for concept, symbols in index.concept_to_symbols.items():
            n = len(symbols)
            if n < self._config.min_constituents:
                empty += 1
                issues.append(
                    QualityIssue(
                        kind="EMPTY_CONCEPT",
                        concept=concept,
                        detail=f"成分数 {n} < min_constituents {self._config.min_constituents}",
                    )
                )
            elif n > self._config.max_constituents:
                oversized += 1
                issues.append(
                    QualityIssue(
                        kind="OVERSIZED_CONCEPT",
                        concept=concept,
                        detail=f"成分数 {n} > max_constituents {self._config.max_constituents}",
                    )
                )
        stale = False
        if index.latest_effective_date is None:
            stale = True
            issues.append(
                QualityIssue(kind="STALE_MAPPING", concept="", detail="无任何成分行")
            )
        else:
            lag = (as_of - index.latest_effective_date).days
            if lag > self._config.stale_days:
                stale = True
                issues.append(
                    QualityIssue(
                        kind="STALE_MAPPING",
                        concept="",
                        detail=(
                            f"最新生效日 {index.latest_effective_date} 距 as_of {as_of} "
                            f"{lag} 天 > stale_days {self._config.stale_days}"
                        ),
                    )
                )
        issues.sort(key=lambda i: (i.kind, i.concept))
        return QualityReport(
            issues=tuple(issues),
            empty_count=empty,
            oversized_count=oversized,
            stale=stale,
            concept_count=len(index.concept_to_symbols),
            symbol_count=len(index.symbol_to_concepts),
        )

    @staticmethod
    def asof(
        versions: Sequence[MappingVersion], date: datetime.date
    ) -> Optional[ConceptMappingIndex]:
        """PIT 查询：取 effective_date ≤ date 的最新版本索引；无 → None。"""
        if not isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            raise InvalidConceptRowError(f"date 必须为 date: {type(date).__name__}")
        eligible = [v for v in versions or [] if v.effective_date <= date]
        if not eligible:
            return None
        return max(eligible, key=lambda v: v.effective_date).index
