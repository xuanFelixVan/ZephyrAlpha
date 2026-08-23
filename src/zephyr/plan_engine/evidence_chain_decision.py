# [BLUEPRINT] MOD-SIG-076 | 待统筹登记（缺口总账 GAP-F-42 行）
# [MODULE] zephyr.plan_engine.evidence_chain_decision
# [DOMAIN] D_PLAN
# [DEPENDENCIES] 无（纯数据结构，零 LLM/DB/网络调用）
# [CONSUMERS] 作战室预案卡扩展（W2/W6 证据链字段）；（候选：GAP-F-44 五角色 Analyst Agent / trading_debate 论点结构化引用位）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] thesis/catalyst/invalidation 三文本强制非空（strip 后）；evidence_for/evidence_against 至少各 1 条非空条目（条目 strip、空串剔除）；生成器填充缺任一字段即拒（fail-closed 且一次性列全缺失字段名）；frozen dataclass JSON 可序列化；as_of 仅接受真实 YYYY-MM-DD
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-42 行
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（五字段缺失/空白/日期非法，fail-closed 并列出字段名）
# [TESTS] tests/plan_engine/test_evidence_chain_decision.py
# [A_module] module_id=MOD-SIG-076 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""EvidenceChain — 证据链决策数据结构（GAP-F-42）。

缺口总账 GAP-F-42（作战室预案卡扩展）：预案/候选股逻辑必须带结构化证据链——
thesis（核心论点）/catalyst（催化剂）/invalidation（失效条件）/evidence_for
（支持证据）/evidence_against（反对证据）五字段强制结构化，生成器填充时强制
校验完整（缺字段 fail-closed 一次性列全），杜绝"只给结论不给证据"的决策卡。

本模块是数据结构+填充校验层，先生成供他人引用（GAP-F-44 五角色论点、
trading_debate 研究员论点、预案卡 W2/W6 展示）。

不做什么：不生成证据内容（内容生产归上游 LLM/分析模块注入）/不落库/不下单。

依据: 缺口总账 GAP-F-42；45_warroom_playbook §4 W2/W6
SSoT: depgraph node 10505564（MOD-SIG-076，待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: payload（五字段+可选 subject_id/as_of 的映射，上游装配注入）
# 算法: missing_fields 诊断 → 缺一即拒（列全字段名）→ EvidenceChain 构建（strip/剔空/日期校验）
# 输出: EvidenceChain（frozen，to_dict/from_dict JSON 往返）
"""

from __future__ import annotations

import datetime as _dt
import re as _re
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Mapping

__all__: Final = [
    "REQUIRED_CHAIN_FIELDS",
    "EvidenceChain",
    "build_evidence_chain",
    "missing_fields",
]

#: 证据链五字段（强制结构化，生成器填充校验基准）
REQUIRED_CHAIN_FIELDS: Final[tuple[str, ...]] = (
    "thesis",
    "catalyst",
    "invalidation",
    "evidence_for",
    "evidence_against",
)

_TEXT_FIELDS: Final = ("thesis", "catalyst", "invalidation")
_LIST_FIELDS: Final = ("evidence_for", "evidence_against")
_DATE_RE: Final = _re.compile(r"\d{4}-\d{2}-\d{2}")


def _clean_items(value: Any) -> tuple[str, ...]:
    """证据条目归一：转 str、strip、剔空串。"""
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        value = [value]
    try:
        return tuple(str(x).strip() for x in value if str(x).strip())
    except TypeError:
        return ()


def _check_date(name: str, value: str) -> None:
    if not _DATE_RE.fullmatch(value):
        raise ValueError(f"{name} 非法（须 YYYY-MM-DD）: {value!r}")
    try:
        _dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} 非真实日期: {value!r}") from exc


@dataclass(frozen=True, slots=True)
class EvidenceChain:
    """证据链（五字段强制结构化，frozen，JSON 可序列化）。

    Attributes:
        thesis: 核心论点（为什么做这笔交易，一句话可审计）。
        catalyst: 催化剂（触发兑现的事件/时点）。
        invalidation: 失效条件（什么发生就认错离场）。
        evidence_for: 支持证据条目（≥1 条）。
        evidence_against: 反对证据条目（≥1 条，强制双侧不留盲区）。
        subject_id: 标的/预案标识（可空，如 symbol 或 scenario 名）。
        as_of: 证据链基准日 YYYY-MM-DD（可空）。
    """

    thesis: str
    catalyst: str
    invalidation: str
    evidence_for: tuple[str, ...]
    evidence_against: tuple[str, ...]
    subject_id: str = ""
    as_of: str | None = None

    def __post_init__(self) -> None:
        for name in _TEXT_FIELDS:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} 非法（证据链五字段强制非空）: {value!r}")
            object.__setattr__(self, name, value.strip())
        for name in _LIST_FIELDS:
            items = _clean_items(getattr(self, name))
            if not items:
                raise ValueError(f"{name} 非法（至少 1 条非空证据）: {getattr(self, name)!r}")
            object.__setattr__(self, name, items)
        object.__setattr__(self, "subject_id", str(self.subject_id).strip())
        if self.as_of is not None:
            if not isinstance(self.as_of, str):
                raise ValueError(f"as_of 非法（须字符串 YYYY-MM-DD）: {self.as_of!r}")
            _check_date("as_of", self.as_of)

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return asdict(self)

    @staticmethod
    def from_dict(payload: Mapping[str, Any]) -> EvidenceChain:
        """字典还原（缺字段 fail-closed，同 build_evidence_chain 口径）。"""
        return build_evidence_chain(payload)


def missing_fields(payload: Mapping[str, Any]) -> tuple[str, ...]:
    """诊断：列出 payload 中缺失/空白的五字段名（供填充方自纠）。"""
    miss: list[str] = []
    for name in _TEXT_FIELDS:
        value = payload.get(name)
        if not isinstance(value, str) or not value.strip():
            miss.append(name)
    for name in _LIST_FIELDS:
        if not _clean_items(payload.get(name)):
            miss.append(name)
    return tuple(miss)


def build_evidence_chain(payload: Mapping[str, Any]) -> EvidenceChain:
    """生成器填充校验主入口：五字段缺一即拒（fail-closed，一次列全缺失字段名）。

    Args:
        payload: 五字段映射 + 可选 subject_id/as_of。

    Returns:
        EvidenceChain（已归一）。

    Raises:
        ValueError: 任一必填字段缺失/空白（消息列出全部缺失字段名）。
    """
    if not isinstance(payload, Mapping):
        raise ValueError(f"payload 非法（须映射）: {type(payload).__name__}")
    miss = missing_fields(payload)
    if miss:
        raise ValueError(f"证据链填充缺失字段（五字段强制完整）: {list(miss)}")
    return EvidenceChain(
        thesis=payload["thesis"],
        catalyst=payload["catalyst"],
        invalidation=payload["invalidation"],
        evidence_for=tuple(_clean_items(payload["evidence_for"])),
        evidence_against=tuple(_clean_items(payload["evidence_against"])),
        subject_id=str(payload.get("subject_id", "")),
        as_of=payload.get("as_of"),
    )
