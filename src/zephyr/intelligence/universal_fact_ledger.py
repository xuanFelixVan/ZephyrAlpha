# [BLUEPRINT] MOD-INT-FACT-LEDGER | docs/03_modules/_domain_intelligence/universal_fact_ledger/blueprint.md
# [MODULE] zephyr.intelligence.universal_fact_ledger
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（UFL 账本与双锁校验核心纯内存；clock 注入）
# [CONSUMERS] 运行时装配批（事实写入接数据检索层 / DoubleLock 校验接 LLM 输出管线 / 强度档位装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 事实五要素(entity/attribute/value/timestamp/source)非空；类型三类词表闭合(numeric|enum|relation)；NUMERIC 值须为数；confidence=1.0 硬约束；账本仅追加写后不可改；实体锁+数值锁任一不过即拒绝且不可降级须修正重提；强度三档词表闭合(strict|standard|lenient)；查询确定性排序；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/universal_fact_ledger/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FactLedgerError(占位 ZA-IT-UNREGISTERED-FACT-LEDGER)——五要素缺失/非法类型/非法值域/confidence≠1.0/非法强度/非法容差/双锁拒绝强制（enforce）时抛
# [TESTS] tests/intelligence/test_universal_fact_ledger.py
# [A_module] module_id=MOD-INT-FACT-LEDGER | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
UniversalFactLedger — 通用事实账本与双重锚定（MOD-INT-FACT-LEDGER）。

B10-01952（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-AISA-014，A1 §29.24-1）：
VeNRA 架构 UFL——**追加式事实账本**（{entity/attribute/value/timestamp/
source} 五要素 + 数值/枚举/关系 3 类型词表闭合，confidence=1.0 硬约束，
写后不可改）+ **DoubleLockGrounding 校验器**（LLM 输出实体不存在于 UFL
或数值非检索自 UFL 即拒绝，**拒绝不可降级须修正重提**）+ **约束强度 3 档**
可配 + 查询接口。canonical 承接 AISA-012 归并。

查重分工（蓝图 §0）：venra_double_lock_anchor=VeNRA 锚定门禁（本件=事实
账本与其上的 grounding 校验语义，不重建锚定流水线）；sentinel_hallucination
_detector=幻觉检测哨兵（本件=双锁拒绝不评分，零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: universal_fact_ledger.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① UniversalFactLedger
#   name_en: UniversalFactLedger
#   intro: UFL 追加式事实账本（写后不可改；查询确定性排序）。
#   desc: UFL 追加式事实账本（写后不可改；查询确定性排序）。；公共方法（定义序）: append, contains, get, facts_of, entities, size；源码 L152-L210
#   inputs: clock
#   outputs: 返回值
# - id: A2
#   name_zh: ② DoubleLockGrounding
#   name_en: DoubleLockGrounding
#   intro: DoubleLockGrounding 校验器（实体锁 + 数值锁；拒绝不可降级须修正重提）。
#   desc: DoubleLockGrounding 校验器（实体锁 + 数值锁；拒绝不可降级须修正重提）。 - 实体锁：LLM 输出引用的每个实体须存在于 UFL； - 数值锁：每条数值断言…；公共方法（定义序）: validat…
#   inputs: ledger strength numeric_tolerance
#   outputs: 返回值
#   （注：A2 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（9 定义）
#   name_en: public defs
#   intro: UniversalFactLedger, DoubleLockGrounding
#   downstream: 运行时装配批（事实写入接数据检索层 / DoubleLock 校验接 LLM 输出管线 / 强度档位装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "ConstraintStrength",
    "DoubleLockGrounding",
    "FactLedgerError",
    "FactRecord",
    "FactType",
    "GroundingResult",
    "GroundingViolation",
    "NumericClaim",
    "UniversalFactLedger",
]


class FactLedgerError(Exception):
    """UFL 输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-IT-UNREGISTERED-FACT-LEDGER。
    """


class FactType(str, Enum):
    """事实类型（三类词表闭合）。"""

    NUMERIC = "numeric"
    ENUM = "enum"
    RELATION = "relation"


class ConstraintStrength(str, Enum):
    """DoubleLock 约束强度三档（词表闭合）。"""

    STRICT = "strict"
    STANDARD = "standard"
    LENIENT = "lenient"


@dataclass(frozen=True)
class FactRecord:
    """UFL 事实五要素 + 类型（frozen；confidence 恒 1.0 硬约束）。"""

    entity: str
    attribute: str
    value: object
    timestamp: datetime.datetime
    source: str
    fact_type: FactType
    confidence: float = 1.0


@dataclass(frozen=True)
class NumericClaim:
    """LLM 输出中的数值断言（须经 UFL 检索锚定）。"""

    entity: str
    attribute: str
    value: float


@dataclass(frozen=True)
class GroundingViolation:
    """双锁违规（frozen；kind ∈ entity_miss|numeric_miss）。"""

    kind: str
    detail: str


@dataclass(frozen=True)
class GroundingResult:
    """双锁校验结果（frozen；accepted=False 即拒绝，不可降级）。"""

    accepted: bool
    violations: tuple[GroundingViolation, ...]
    strength: ConstraintStrength


class UniversalFactLedger:
    """UFL 追加式事实账本（写后不可改；查询确定性排序）。"""

    def __init__(self, *, clock: Callable[[], datetime.datetime] | None = None) -> None:
        self._clock = clock or datetime.datetime.now
        self._facts: list[FactRecord] = []

    # ── 写（仅追加） ──────────────────────────────────────────────────────

    def append(self, fact: FactRecord) -> int:
        """追加事实：五要素非空 + 类型词表闭合 + 值域匹配 + confidence=1.0 硬约束。"""
        if not fact.entity:
            raise FactLedgerError("entity 为空")
        if not fact.attribute:
            raise FactLedgerError("attribute 为空")
        if fact.value is None or fact.value == "":
            raise FactLedgerError("value 为空")
        if not fact.source:
            raise FactLedgerError("source 为空")
        if not isinstance(fact.fact_type, FactType):
            raise FactLedgerError(f"非法事实类型: {fact.fact_type!r}")
        if fact.confidence != 1.0:
            raise FactLedgerError(f"confidence={fact.confidence!r} 违反硬约束（UFL 事实恒为 1.0）")
        if fact.fact_type is FactType.NUMERIC:
            if isinstance(fact.value, bool) or not isinstance(fact.value, (int, float)):
                raise FactLedgerError(f"NUMERIC 事实值须为数: {fact.value!r}")
        elif not isinstance(fact.value, str):
            raise FactLedgerError(f"{fact.fact_type.value} 事实值须为字符串: {fact.value!r}")
        self._facts.append(fact)  # 追加式：写后不可改（无 update/delete 接口）
        _log.info("UFL 追加: %s.%s = %r (%s)", fact.entity, fact.attribute, fact.value, fact.fact_type.value)
        return len(self._facts) - 1

    # ── 查询 ─────────────────────────────────────────────────────────────

    def contains(self, entity: str) -> bool:
        """实体是否存在。"""
        return any(f.entity == entity for f in self._facts)

    def get(self, entity: str, attribute: str) -> FactRecord:
        """最新事实（同刻按写入序后者优先；无 → Fail-Closed）。"""
        matches = [(i, f) for i, f in enumerate(self._facts) if f.entity == entity and f.attribute == attribute]
        if not matches:
            raise FactLedgerError(f"UFL 无事实: {entity!r}.{attribute!r}")
        matches.sort(key=lambda kv: (kv[1].timestamp, kv[0]))
        return matches[-1][1]

    def facts_of(self, entity: str, attribute: str) -> tuple[FactRecord, ...]:
        """全历史（按 (timestamp, 写入序) 确定性升序）。"""
        matches = [(i, f) for i, f in enumerate(self._facts) if f.entity == entity and f.attribute == attribute]
        matches.sort(key=lambda kv: (kv[1].timestamp, kv[0]))
        return tuple(f for _, f in matches)

    def entities(self) -> tuple[str, ...]:
        """全部实体（确定性排序去重）。"""
        return tuple(sorted({f.entity for f in self._facts}))

    def size(self) -> int:
        """事实总数。"""
        return len(self._facts)


class DoubleLockGrounding:
    """DoubleLockGrounding 校验器（实体锁 + 数值锁；拒绝不可降级须修正重提）。

    - 实体锁：LLM 输出引用的每个实体须存在于 UFL；
    - 数值锁：每条数值断言须可检索自 UFL——
      STRICT=最新值精确相等；STANDARD=任一历史值精确相等；
      LENIENT=与最新值之差 ≤ 注入容差。
    """

    def __init__(
        self,
        *,
        ledger: UniversalFactLedger,
        strength: ConstraintStrength = ConstraintStrength.STRICT,
        numeric_tolerance: float = 0.0,
    ) -> None:
        if not isinstance(ledger, UniversalFactLedger):
            raise FactLedgerError("ledger 未注入")
        if not isinstance(strength, ConstraintStrength):
            raise FactLedgerError(f"非法约束强度: {strength!r}")
        if numeric_tolerance < 0.0:
            raise FactLedgerError(f"numeric_tolerance 为负: {numeric_tolerance!r}")
        self._ledger = ledger
        self._strength = strength
        self._tolerance = numeric_tolerance

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _numeric_hit(self, claim: NumericClaim) -> bool:
        history = self._ledger.facts_of(claim.entity, claim.attribute)
        numerics = [float(f.value) for f in history if f.fact_type is FactType.NUMERIC]
        if not numerics:
            return False
        if self._strength is ConstraintStrength.STANDARD:
            return any(v == float(claim.value) for v in numerics)
        latest = numerics[-1]
        if self._strength is ConstraintStrength.STRICT:
            return latest == float(claim.value)
        return abs(latest - float(claim.value)) <= self._tolerance  # LENIENT

    # ── 校验 ─────────────────────────────────────────────────────────────

    def validate(
        self,
        *,
        entities: Sequence[str],
        numeric_claims: Sequence[NumericClaim] = (),
    ) -> GroundingResult:
        """双锁校验：任一违规 → accepted=False（拒绝；无降级路径，须修正重提）。"""
        violations: list[GroundingViolation] = []
        for entity in entities:
            if not entity or not self._ledger.contains(entity):
                violations.append(
                    GroundingViolation(
                        kind="entity_miss",
                        detail=f"实体 {entity!r} 不存在于 UFL",
                    )
                )
        for claim in numeric_claims:
            if not self._ledger.contains(claim.entity):
                violations.append(
                    GroundingViolation(
                        kind="entity_miss",
                        detail=f"数值断言实体 {claim.entity!r} 不存在于 UFL",
                    )
                )
            elif not self._numeric_hit(claim):
                violations.append(
                    GroundingViolation(
                        kind="numeric_miss",
                        detail=(
                            f"数值断言 {claim.entity!r}.{claim.attribute!r}={claim.value!r} "
                            f"非检索自 UFL（强度 {self._strength.value}）"
                        ),
                    )
                )
        accepted = not violations
        if not accepted:
            _log.warning("DoubleLock 拒绝（不可降级，须修正重提）: %d 项违规", len(violations))
        return GroundingResult(
            accepted=accepted,
            violations=tuple(violations),
            strength=self._strength,
        )

    def enforce(
        self,
        *,
        entities: Sequence[str],
        numeric_claims: Sequence[NumericClaim] = (),
    ) -> None:
        """强制校验：拒绝即抛（Fail-Closed；调用方须修正后重新提交）。"""
        result = self.validate(entities=entities, numeric_claims=numeric_claims)
        if not result.accepted:
            raise FactLedgerError("DoubleLockGrounding 拒绝: " + "; ".join(v.detail for v in result.violations))
