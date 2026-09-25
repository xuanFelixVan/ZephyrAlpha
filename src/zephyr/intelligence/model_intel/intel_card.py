# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §model_intel
# [MODULE] zephyr.intelligence.model_intel.intel_card
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] 无仓内依赖（纯函数库；时间由调用方注入，禁本模块内取时）
# [CONSUMERS] zephyr.intelligence.model_intel.scanner（建卡/校验/去重）；M2 模型库入库器（施工项 C3，消费过闸卡）
# [STARTUP] event_driven
# [MATURITY] evolving
# [INVARIANTS] 情报卡 schema=OBJ_M DESIGN §2.3 v0（MI-<source>-<yyyymmdd>-<seq>）；四闸=挖矿 SOP §5 复用
#              （来源可溯四字段全填/交叉验证≥2 独立源/适配/可用性）；价格类 kind（price_change|new_model）
#              必带 evidence_quote+evidence_url（零编造引文）；free_window 必带 window_expr+quota；
#              injection_probe 必填（宪法 §9.11 指令-数据边界落点）；simhash=64bit 汉明指纹，
#              距离 ≤k(默认 3) 判换皮；hash 用 hashlib（禁内建 hash()，防 PYTHONHASHSEED 随机化）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §2.3
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] validate_four_gates 永不抛异常——数据畸形按缺失处理计入违规清单（空清单=过闸）；
#                  simhash64/hamming 对空串返回 0；全部纯函数、零 IO、零时钟
# [TESTS] tests/intelligence/model_intel/test_intel_card.py
# [TTL] permanent
"""intel_card — M1 情报卡 schema 与四闸校验（OBJ_M DESIGN §2.3）。

分层：``IntelCard`` 是纯 dataclass（可 JSON 序列化）；``validate_four_gates()`` 是纯校验器
（返回违规清单，空=过闸，不抛异常）；``simhash64()``/``hamming()`` 是查重口径（换皮情报防反复进货）。
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Final

__all__: Final = [
    "CardKind",
    "Claimed",
    "CrossValidation",
    "FourGates",
    "IntelGateVerdict",
    "IntelCard",
    "SourceRef",
    "SIMHASH_BITS",
    "DEDUP_K_DEFAULT",
    "hamming",
    "simhash64",
    "validate_four_gates",
]

SIMHASH_BITS: Final = 64
DEDUP_K_DEFAULT: Final = 3

_KIND_VALUES: Final = ("new_model", "price_change", "free_window", "promo", "deprecation")
# 价格类 kind：情报原文必须给出可核引文+出处（零编造引文铁律）
_PRICE_KINDS: Final = ("price_change", "new_model")
_PROVENANCE_PASS: Final = "pass"


class CardKind(str, Enum):
    """情报卡类型（DESIGN §2.3 枚举，值与 YAML 口径一致用小写）。"""

    NEW_MODEL = "new_model"
    PRICE_CHANGE = "price_change"
    FREE_WINDOW = "free_window"
    PROMO = "promo"
    DEPRECATION = "deprecation"

    @classmethod
    def values(cls) -> tuple[str, ...]:
        return _KIND_VALUES


@dataclass(frozen=True)
class SourceRef:
    """闸1 来源可溯：四字段必填（name/url/publisher/fetched_at）。"""

    name: str
    url: str
    publisher: str
    fetched_at: str


@dataclass(frozen=True)
class Claimed:
    """情报原文声称值（未核事实，生熟分离的"生"面）。"""

    price_before: float | None = None
    price_after: float | None = None
    window_expr: str = ""
    quota: str = ""
    evidence_quote: str = ""
    evidence_url: str = ""


@dataclass(frozen=True)
class CrossValidation:
    """闸2 交叉验证：≥2 独立来源才 pass。"""

    independent_sources: int = 0
    note: str = ""


@dataclass(frozen=True)
class IntelGateVerdict:
    """闸3/闸4 结论（adaptation 适配性 / availability 可用性）。"""

    verdict: str = "pending"
    note: str = ""


@dataclass(frozen=True)
class FourGates:
    """四闸（挖矿 SOP §5 复用）：来源可溯由 SourceRef 承载，此处存闸 2-4 + provenance 结论。"""

    provenance: str = "pending"
    cross_validation: CrossValidation = field(default_factory=CrossValidation)
    adaptation: IntelGateVerdict = field(default_factory=IntelGateVerdict)
    availability: IntelGateVerdict = field(default_factory=IntelGateVerdict)


@dataclass(frozen=True)
class IntelCard:
    """M1 情报卡（DESIGN §2.3 v0）：未过闸=生，过闸+入库登记=熟。"""

    card_id: str
    source: SourceRef
    kind: str
    model_refs: list[str] = field(default_factory=list)
    claimed: Claimed = field(default_factory=Claimed)
    four_gates: FourGates = field(default_factory=FourGates)
    injection_probe: str = ""
    action: dict[str, str] = field(default_factory=dict)
    labor_killed: str = ""
    dedup_simhash: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """可 JSON 序列化视图（枚举转值，字段顺序稳定）。"""
        data = asdict(self)
        data["kind"] = self.kind
        return data

    def fingerprint_text(self) -> str:
        """simhash 查重的规范化文本（kind+模型引用+声称值，稳定排序）。"""
        claimed = self.claimed
        parts = [
            f"kind={self.kind}",
            f"models={','.join(sorted(self.model_refs))}",
            f"price={claimed.price_before}->{claimed.price_after}",
            f"window={claimed.window_expr}",
            f"quota={claimed.quota}",
            f"quote={re.sub(r'\s+', '', claimed.evidence_quote.lower())[:120]}",
        ]
        return "|".join(parts)


def _mk(kind: str) -> CardKind:
    return CardKind(kind)


def validate_four_gates(card: IntelCard) -> list[str]:
    """四闸字段校验：返回违规清单（空=过闸）。纯函数，永不抛异常。

    规则族（与 MODIFY-GUARD §2.3 对齐）：
      1. 来源四字段必填（name/url/publisher/fetched_at）；
      2. kind 必须在枚举内（new_model|price_change|free_window|promo|deprecation）；
      3. 价格类 kind（price_change|new_model）必须有 evidence_quote+evidence_url；
      4. free_window 必须有 window_expr+quota；
      5. cross_validation.independent_sources ≥2 才 pass；
      6. injection_probe 非空（注入探针，宪法 §9.11）。
    """
    violations: list[str] = []
    src = card.source
    for fname in ("name", "url", "publisher", "fetched_at"):
        if not str(getattr(src, fname, "") or "").strip():
            violations.append(f"source.{fname}_missing")
    try:
        _mk(card.kind)
    except ValueError:
        violations.append(f"kind_invalid:{card.kind}")
    kind = str(card.kind)
    if kind in _PRICE_KINDS:
        if not card.claimed.evidence_quote.strip():
            violations.append("claimed.evidence_quote_missing")
        if not card.claimed.evidence_url.strip():
            violations.append("claimed.evidence_url_missing")
    if kind == "free_window":
        if not card.claimed.window_expr.strip():
            violations.append("claimed.window_expr_missing")
        if not card.claimed.quota.strip():
            violations.append("claimed.quota_missing")
    if int(card.four_gates.cross_validation.independent_sources) < 2:
        violations.append(
            f"cross_validation.independent_sources_lt_2:{card.four_gates.cross_validation.independent_sources}"
        )
    if not card.injection_probe.strip():
        violations.append("injection_probe_missing")
    return violations


def _feature_hashes(text: str) -> list[int]:
    """特征集：小写化→词元→相邻 bigram（词元不足时退化为单字符 bigram 覆盖 CJK）。"""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if not normalized:
        return []
    tokens = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", normalized)
    if len(tokens) >= 2:
        feats = [f"{a}~{b}" for a, b in zip(tokens, tokens[1:])]
    else:
        chars = normalized.replace(" ", "")
        feats = [f"{a}{b}" for a, b in zip(chars, chars[1:])] or [chars]
    return [int.from_bytes(hashlib.blake2b(f.encode("utf-8"), digest_size=8).digest(), "big")
            for f in feats]


def simhash64(text: str) -> int:
    """64bit simhash 指纹：bigram 特征加权投票（仓内查重口径，稳定可复现）。"""
    v = [0] * SIMHASH_BITS
    for fh in _feature_hashes(text):
        for i in range(SIMHASH_BITS):
            v[i] += 1 if (fh >> i) & 1 else -1
    out = 0
    for i, x in enumerate(v):
        if x > 0:
            out |= 1 << i
    return out


def hamming(a: int, b: int) -> int:
    """两指纹的汉明距离（异或后按位计数）。"""
    return bin((a ^ b) & ((1 << SIMHASH_BITS) - 1)).count("1")
