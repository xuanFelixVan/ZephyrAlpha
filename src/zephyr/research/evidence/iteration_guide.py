# [BLUEPRINT] MOD-EVIDENCE_CHAIN | 待统筹登记（18号清单 §6 波4-11 / 11号文 §4.2 Phase 0 / apply_depgraph 设计态登记建议见 .runtime/p3_fragments/w4_11.md）
# [MODULE] zephyr.research.evidence.iteration_guide
# [DOMAIN] D_KNOWLEDGE  # 2026-08-22 统筹裁定：D_RESEARCH 不在 depgraph domains 表，归属 D_KNOWLEDGE（知识管理——假设/证据=知识资产）
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.io.paths; zephyr.research.evidence.evidence_chain; pyyaml
# [CONSUMERS] zephyr.research.evidence.batch_entry; tests/research/test_evidence_phase0.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 规则按配置顺序首命中生效；每条建议必带命中 rule_id + 证据计数 + 规则中文理由（可追溯，11号文 P0-3）；recommendation ∈ {continue, pivot, abandon} 三态词表；规则表 config 化（config/iteration_guide_rules.yaml），未知条件键/重复 rule_id/词表外建议 加载即拒；无命中规则→显式报错（不静默给建议）
# [MODIFY-GUARD] tests/research/test_evidence_phase0.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] IterationGuideError(ZA-RE-0020)——无规则命中；IterationGuideConfigError(ZA-RE-0021)——规则配置非法（结构/词表/条件键/重复 id）
# [TESTS] tests/research/test_evidence_phase0.py
# [A_module] module_id=MOD-EVIDENCE_CHAIN | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""迭代引导器（Iteration Guide）——研究证据关联组件 P0-3（11号文 §4.2）。

职责：按显式规则集，从假设的证据聚合输出"继续（continue）/转向（pivot）/
放弃（abandon）"迭代建议——这正是 AQuA"证据保留→迭代引导"机制的落地
（11号文 §2.2/§3.1）。

Why 显式规则而非学习模型（11号文 §3.1）：个人项目假设量级（数十至数百条）
不足以训练置信度更新模型；显式规则（如"独立反驳证据≥2 条且近 4 周无新支持 →
建议放弃"）可审计、可交叉验证，符合"AI 生成代码需交叉验证"的自治约束（§2.3）。

规则表 config 化：默认真源 config/iteration_guide_rules.yaml；evaluate 顺序
评估、首命中生效。每条建议携带命中规则 id + 证据计数 + 规则理由，全链路可追溯。

条件键词表（AND 语义，全部满足才命中）：
    support_gte / contradict_gte / neutral_gte / evidence_gte（总数）: int——≥阈值
    support_eq / contradict_eq: int——等于阈值
    no_support_within_weeks: int/float——近 N 周内无新支持证据
    （无支持证据或最新支持早于 N 周前，视为满足）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 证据聚合视图
#   fields: EvidenceSummary（support/contradict/neutral/total 计数 + latest_support_at/latest_at）
#   code: IterationGuide.evaluate(summary, at=...) 入口
# - id: I2
#   name: 规则表 config（YAML）
#   fields: rules[]（rule_id/recommendation/conditions/rationale_zh）
#   code: load_rules（默认 config/iteration_guide_rules.yaml；非法配置 ZA-RE-0021 加载即拒）
# 层: 算法
# - id: A1
#   name_zh: ① 规则表校验
#   name_en: _validate_rules
#   desc: rule_id 非空去重 + recommendation 三态词表 + 条件键词表/非负数值校验——非法即拒
#   inputs: I2 或注入规则
#   outputs: 规范化规则表
# - id: A2
#   name_zh: ② 顺序求值首命中
#   name_en: evaluate
#   desc: 按配置顺序逐规则 AND 求值条件（含 no_support_within_weeks 时窗判定），首命中即产出建议；无命中 raise ZA-RE-0020
#   inputs: I1 + A1
#   outputs: 命中规则
# 层: 输出
# - id: O1
#   name_zh: 迭代建议（可追溯）
#   name_en: Guidance（hypothesis_id/recommendation/rule_id/rationale_zh/evidence_counts/generated_at）
#   downstream: zephyr.research.evidence.batch_entry（批量评估落盘）；tests/research/test_evidence_phase0.py
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A2
# A1 --> A2
# A2 --> O1

依据: 11号文 §3.1/§4.2 P0-3 + 18号清单 §6 波4-11
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Final, Iterable

import yaml

from zephyr.research.evidence.evidence_chain import EvidenceSummary
from zephyr.research.evidence.hypothesis_registry import CST
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "DEFAULT_RULES_PATH",
    "KNOWN_CONDITION_KEYS",
    "GuideRule",
    "Guidance",
    "IterationGuide",
    "IterationGuideConfigError",
    "IterationGuideError",
    "Recommendation",
    "load_rules",
]

log = logging.getLogger(__name__)

# ============================================================================
# 1. 错误契约（ZA-RE-0020~0021）
# ============================================================================


class IterationGuideError(ZephyrBaseError):
    """ZA-RE-0020: 迭代引导器基础错误（无规则命中——不静默给建议）。"""

    error_code = "ZA-RE-0020"


class IterationGuideConfigError(IterationGuideError):
    """ZA-RE-0021: 规则配置非法（结构/词表/条件键/重复 rule_id）。"""

    error_code = "ZA-RE-0021"


# ============================================================================
# 2. 常量与词表
# ============================================================================

#: 默认规则表真源（规则表 config 化）
DEFAULT_RULES_PATH: Final[Path] = REPO_ROOT / "config" / "iteration_guide_rules.yaml"

#: 条件键词表——词表外键加载即拒（防拼写漂移静默失效）
KNOWN_CONDITION_KEYS: Final = frozenset(
    {
        "support_gte",
        "support_eq",
        "contradict_gte",
        "contradict_eq",
        "neutral_gte",
        "evidence_gte",
        "no_support_within_weeks",
    }
)


class Recommendation(str, Enum):
    """迭代建议三态（11号文 §3.1：继续/转向/放弃）。"""

    CONTINUE = "continue"
    PIVOT = "pivot"
    ABANDON = "abandon"


# ============================================================================
# 3. 规则与建议
# ============================================================================


@dataclass(frozen=True)
class GuideRule:
    """迭代引导规则——条件全满足（AND）即命中，产出 recommendation。"""

    rule_id: str
    recommendation: Recommendation
    conditions: dict[str, Any] = field(default_factory=dict)
    rationale_zh: str = ""


@dataclass(frozen=True)
class Guidance:
    """迭代建议——必带命中规则 id + 证据计数 + 规则理由（P0-3 可追溯验收）。"""

    hypothesis_id: str
    recommendation: Recommendation
    rule_id: str
    rationale_zh: str
    evidence_counts: dict[str, int]
    generated_at: str  # ISO 8601（CST）

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "recommendation": self.recommendation.value,
            "rule_id": self.rule_id,
            "rationale_zh": self.rationale_zh,
            "evidence_counts": dict(self.evidence_counts),
            "generated_at": self.generated_at,
        }


# ============================================================================
# 4. 规则加载与校验（config 化）
# ============================================================================


def _validate_rules(rules: Iterable[GuideRule]) -> list[GuideRule]:
    """规则表校验——非法配置加载即拒（fail-fast，不静默跳过坏规则）。"""
    normalized: list[GuideRule] = []
    seen: set[str] = set()
    for rule in rules:
        if not isinstance(rule.rule_id, str) or not rule.rule_id.strip():
            raise IterationGuideConfigError(f"规则 rule_id 为空或非字符串: {rule!r}")
        rule_id = rule.rule_id.strip()
        if rule_id in seen:
            raise IterationGuideConfigError(f"规则 rule_id 重复: {rule_id}")
        seen.add(rule_id)
        try:
            rec = Recommendation(rule.recommendation)
        except ValueError:
            raise IterationGuideConfigError(
                f"规则 {rule_id} 建议取值越出三态词表: {rule.recommendation!r}（词表：continue/pivot/abandon）"
            ) from None
        if not isinstance(rule.conditions, dict):
            raise IterationGuideConfigError(f"规则 {rule_id} conditions 非映射: {rule.conditions!r}")
        unknown = set(rule.conditions) - KNOWN_CONDITION_KEYS
        if unknown:
            raise IterationGuideConfigError(
                f"规则 {rule_id} 含词表外条件键: {sorted(unknown)}（词表：{sorted(KNOWN_CONDITION_KEYS)}）"
            )
        for key, value in rule.conditions.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                raise IterationGuideConfigError(f"规则 {rule_id} 条件 {key} 取值非法: {value!r}（须为非负数值）")
        normalized.append(
            GuideRule(
                rule_id=rule_id,
                recommendation=rec,
                conditions=dict(rule.conditions),
                rationale_zh=str(rule.rationale_zh),
            )
        )
    if not normalized:
        raise IterationGuideConfigError("规则表为空——迭代引导无规则可依")
    return normalized


def load_rules(path: Path | str | None = None) -> list[GuideRule]:
    """从 YAML 加载规则表（默认 config/iteration_guide_rules.yaml）。"""
    rules_path = Path(path) if path is not None else DEFAULT_RULES_PATH
    try:
        payload = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    except IterationGuideConfigError:
        raise
    except Exception as exc:
        raise IterationGuideConfigError(
            f"规则表读取/解析失败: {rules_path}",
            details={"path": str(rules_path), "cause": repr(exc)},
        ) from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("rules"), list):
        raise IterationGuideConfigError(
            f"规则表结构非法——须为含 rules 列表的映射: {rules_path}",
            details={"path": str(rules_path)},
        )
    try:
        raw_rules = [
            GuideRule(
                rule_id=r.get("rule_id"),
                recommendation=r.get("recommendation"),
                conditions=r.get("conditions") or {},
                rationale_zh=r.get("rationale_zh", ""),
            )
            for r in payload["rules"]
        ]
    except AttributeError as exc:
        raise IterationGuideConfigError(
            f"规则表条目结构非法（须为映射）: {rules_path}",
            details={"path": str(rules_path), "cause": repr(exc)},
        ) from exc
    return _validate_rules(raw_rules)


# ============================================================================
# 5. 条件求值与引导器
# ============================================================================


def _parse_ts(iso: str, hypothesis_id: str) -> datetime:
    try:
        ts = datetime.fromisoformat(iso)
    except ValueError as exc:
        raise IterationGuideError(
            f"证据时间戳不可解析: {iso!r}",
            details={"hypothesis_id": hypothesis_id, "created_at": iso},
        ) from exc
    return ts if ts.tzinfo is not None else ts.replace(tzinfo=CST)


def _condition_holds(conditions: dict[str, Any], summary: EvidenceSummary, at: datetime) -> bool:
    """AND 语义——全部条件满足才命中。"""
    for key, threshold in conditions.items():
        if key == "support_gte" and not summary.support_count >= threshold:
            return False
        if key == "support_eq" and summary.support_count != threshold:
            return False
        if key == "contradict_gte" and not summary.contradict_count >= threshold:
            return False
        if key == "contradict_eq" and summary.contradict_count != threshold:
            return False
        if key == "neutral_gte" and not summary.neutral_count >= threshold:
            return False
        if key == "evidence_gte" and not summary.total_count >= threshold:
            return False
        if key == "no_support_within_weeks":
            if summary.latest_support_at is not None:
                latest = _parse_ts(summary.latest_support_at, summary.hypothesis_id)
                if latest >= at - timedelta(weeks=threshold):
                    return False  # 近 N 周内仍有新支持 → 不满足
    return True


class IterationGuide:
    """迭代引导器——规则按配置顺序评估，首命中生效。

    Args:
        rules: 规则表；None → load_rules() 加载默认 config/iteration_guide_rules.yaml。
    """

    def __init__(self, rules: list[GuideRule] | None = None) -> None:
        self._rules = _validate_rules(rules) if rules is not None else load_rules()

    @property
    def rules(self) -> tuple[GuideRule, ...]:
        return tuple(self._rules)

    def evaluate(self, summary: EvidenceSummary, *, at: datetime | None = None) -> Guidance:
        """单假设证据聚合 → 迭代建议（含命中规则与证据计数，可追溯）。"""
        now = at or datetime.now(CST)
        now = now if now.tzinfo is not None else now.replace(tzinfo=CST)
        for rule in self._rules:
            if _condition_holds(rule.conditions, summary, now):
                return Guidance(
                    hypothesis_id=summary.hypothesis_id,
                    recommendation=rule.recommendation,
                    rule_id=rule.rule_id,
                    rationale_zh=rule.rationale_zh,
                    evidence_counts=summary.counts_dict(),
                    generated_at=now.isoformat(),
                )
        raise IterationGuideError(
            f"无规则命中假设 {summary.hypothesis_id}——规则表缺兜底规则，拒绝静默给建议",
            details={"hypothesis_id": summary.hypothesis_id, "evidence_counts": summary.counts_dict()},
        )

    def evaluate_all(self, summaries: Iterable[EvidenceSummary], *, at: datetime | None = None) -> list[Guidance]:
        """批量评估（日/周频批量入口消费）。"""
        now = at or datetime.now(CST)
        return [self.evaluate(s, at=now) for s in summaries]
