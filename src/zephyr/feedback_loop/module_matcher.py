# [BLUEPRINT] MOD-FBL-002 | docs/03_modules/_domain_feedback_loop/module_matcher/blueprint.md
# [MODULE] zephyr.feedback_loop.module_matcher
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] 无（协议核心纯内存；embedder 全注入，余弦相似度本地计算）
# [CONSUMERS] 运行时装配批（capability_tags 注册表装配 / embedder 接 EmbeddingRouter / 知识包功能需求匹配路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] capability_tags 注册表闭合(规范化去重排序); tag 命中预筛后 embedding 余弦相似度; EXACT(>0.85)/PARTIAL(0.5~0.85)/NO_MATCH(<0.5)三档(恰等归低档); 候选按 (-score,module_id) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_feedback_loop/module_matcher/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ModuleMatcherError(占位 ZA-FBL-UNREGISTERED-MODULE-MATCHER)——空模块/重复注册/空标签/空需求/非法阈值/非法向量/embedder 异常时抛
# [TESTS] tests/feedback_loop/test_module_matcher.py
# [A_module] module_id=MOD-FBL-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""


ModuleMatcher — 模块匹配器（MOD-FBL-002）。

B12-03549（AUD-DRAFT-001-DIGEST P2 波 P2-W14，CAND-FBL-004，B12）：
提取知识包功能需求 → 按 capability_tags 注册表搜索（tag 命中预筛）→
embedding 语义相似度（注入 embedder，余弦本地计算）→ EXACT(>0.85) /
PARTIAL(0.5~0.85) / NO_MATCH(<0.5) 三档判定输出（阈值边界恰等归低档）。

查重分工（蓝图 §0）：agent_orchestrator=角色能力评分路由（本件不做评分
路由）；llm_agent_router=LLM 服务选路（零交集）；skill_library=技能条目
向量检索（本件=模块 capability 匹配，不建技能库）。embedder 全注入，本件
仅实现注册表 + 余弦 + 三档判定。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: embedder 参数
#   fields: 参数 embedder（无注解）
#   code: module_matcher.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: exact_threshold 参数
#   fields: 参数 exact_threshold（无注解）
#   code: module_matcher.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: partial_threshold 参数
#   fields: 参数 partial_threshold（无注解）
#   code: module_matcher.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ModuleMatcher
#   name_en: ModuleMatcher
#   intro: 模块匹配器（capability_tags 注册表 + embedding 余弦 + 三档判定）。
#   desc: 模块匹配器（capability_tags 注册表 + embedding 余弦 + 三档判定）。；公共方法（定义序）: register_module, match；源码 L141-L273
#   inputs: embedder exact_threshold partial_threshold
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: ModuleMatcher
#   downstream: 运行时装配批（capability_tags 注册表装配 / embedder 接 EmbeddingRouter / 知识包功能需求匹配路由）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "MatchCandidate",
    "MatchResult",
    "MatchTier",
    "ModuleEntry",
    "ModuleMatcher",
    "ModuleMatcherError",
]

#: 三档判定默认阈值（恰等归低档：>EXACT 为 EXACT，>=PARTIAL 为 PARTIAL）
_EXACT_THRESHOLD: Final[float] = 0.85
_PARTIAL_THRESHOLD: Final[float] = 0.5


class ModuleMatcherError(Exception):
    """模块匹配器输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FBL-UNREGISTERED-MODULE-MATCHER。
    """


class MatchTier(str, Enum):
    """匹配档位（词表闭合）。"""

    EXACT = "exact"
    PARTIAL = "partial"
    NO_MATCH = "no_match"


@dataclass(frozen=True)
class ModuleEntry:
    """capability_tags 注册表条目（frozen；tags 规范化去重排序）。"""

    module_id: str
    capability_tags: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class MatchCandidate:
    """单模块匹配候选（frozen）。"""

    module_id: str
    score: float
    matched_tags: tuple[str, ...]


@dataclass(frozen=True)
class MatchResult:
    """匹配结果 Schema（三档判定输出，frozen）。

    candidates 按 (-score, module_id) 确定性排序；tag 预筛全空时
    best=None 且 candidates=()；score 低于 PARTIAL 阈值时 tier=NO_MATCH
    但保留候选供留痕。
    """

    requirement: str
    tier: MatchTier
    best: MatchCandidate | None
    candidates: tuple[MatchCandidate, ...]


class ModuleMatcher:
    """模块匹配器（capability_tags 注册表 + embedding 余弦 + 三档判定）。"""

    def __init__(
        self,
        *,
        embedder: Callable[[str], Sequence[float]],
        exact_threshold: float = _EXACT_THRESHOLD,
        partial_threshold: float = _PARTIAL_THRESHOLD,
    ) -> None:
        if not callable(embedder):
            raise ModuleMatcherError("embedder 未注入或不可调用")
        for name, v in (("exact_threshold", exact_threshold), ("partial_threshold", partial_threshold)):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ModuleMatcherError(f"非法阈值类型: {name}={v!r}")
        if not (0.0 < float(partial_threshold) < float(exact_threshold) <= 1.0):
            raise ModuleMatcherError(
                f"非法阈值区间: partial={partial_threshold!r} exact={exact_threshold!r}（须 0 < partial < exact <= 1）"
            )
        self._embedder = embedder
        self._exact = float(exact_threshold)
        self._partial = float(partial_threshold)
        self._registry: dict[str, ModuleEntry] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _embed(self, text: str) -> tuple[float, ...]:
        try:
            vec = self._embedder(text)
        except ModuleMatcherError:
            raise
        except Exception as exc:  # noqa: BLE001 — embedder 异常按 Fail-Closed 包装
            raise ModuleMatcherError(f"embedder 异常: {exc!r}") from exc
        if isinstance(vec, (str, bytes)):
            raise ModuleMatcherError(f"非法向量类型: {type(vec).__name__}")
        try:
            items = tuple(vec)
        except TypeError as exc:
            raise ModuleMatcherError(f"非法向量类型: {type(vec).__name__}") from exc
        if not items:
            raise ModuleMatcherError("空向量")
        out: list[float] = []
        for x in items:
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ModuleMatcherError(f"向量含非数值分量: {x!r}")
            out.append(float(x))
        return tuple(out)

    @staticmethod
    def _cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
        """余弦相似度（本地计算；零范数向量按 0.0 处理）。"""
        if len(a) != len(b):
            raise ModuleMatcherError(f"向量维度不一致: {len(a)} vs {len(b)}")
        dot = math.fsum(x * y for x, y in zip(a, b, strict=False))
        na = math.sqrt(math.fsum(x * x for x in a))
        nb = math.sqrt(math.fsum(y * y for y in b))
        if na == 0.0 or nb == 0.0:
            return 0.0
        return max(-1.0, min(1.0, dot / (na * nb)))

    # ── 注册表 ───────────────────────────────────────────────────────────

    def register_module(
        self,
        module_id: str,
        capability_tags: Sequence[str],
        description: str = "",
    ) -> None:
        """登记模块能力标签（tags 规范化：strip+lower+去重+排序）。"""
        if not isinstance(module_id, str) or not module_id.strip():
            raise ModuleMatcherError("module_id 为空")
        if module_id in self._registry:
            raise ModuleMatcherError(f"module_id 重复注册: {module_id!r}")
        if not isinstance(description, str):
            raise ModuleMatcherError(f"非法 description 类型: {type(description).__name__}")
        try:
            raw_tags = tuple(capability_tags)
        except TypeError as exc:
            raise ModuleMatcherError("capability_tags 不可迭代") from exc
        normalized: set[str] = set()
        for tag in raw_tags:
            if not isinstance(tag, str):
                raise ModuleMatcherError(f"非法 tag 类型: {tag!r}")
            if tag.strip():
                normalized.add(tag.strip().lower())
        if not normalized:
            raise ModuleMatcherError(f"capability_tags 为空: {module_id!r}")
        self._registry[module_id] = ModuleEntry(
            module_id=module_id,
            capability_tags=tuple(sorted(normalized)),
            description=description,
        )

    # ── 匹配 ─────────────────────────────────────────────────────────────

    def match(self, requirement: str) -> MatchResult:
        """匹配：tag 命中预筛 → 余弦相似度 → 三档判定（恰等归低档）。"""
        if not isinstance(requirement, str) or not requirement.strip():
            raise ModuleMatcherError("requirement 为空")
        req_lower = requirement.lower()

        candidates: list[MatchCandidate] = []
        req_vec: tuple[float, ...] | None = None
        for module_id in sorted(self._registry):
            entry = self._registry[module_id]
            hits = tuple(t for t in entry.capability_tags if t in req_lower)
            if not hits:
                continue
            if req_vec is None:
                req_vec = self._embed(requirement)
            cap_text = " ".join(entry.capability_tags)
            if entry.description:
                cap_text = f"{cap_text} {entry.description}"
            score = self._cosine(req_vec, self._embed(cap_text))
            candidates.append(MatchCandidate(module_id=module_id, score=score, matched_tags=hits))

        candidates.sort(key=lambda c: (-c.score, c.module_id))
        best = candidates[0] if candidates else None
        if best is None:
            tier = MatchTier.NO_MATCH
        elif best.score > self._exact:
            tier = MatchTier.EXACT
        elif best.score >= self._partial:
            tier = MatchTier.PARTIAL
        else:
            tier = MatchTier.NO_MATCH
        _log.info("模块匹配: %r -> %s (best=%s)", requirement, tier.value, best.module_id if best else None)
        return MatchResult(
            requirement=requirement,
            tier=tier,
            best=best,
            candidates=tuple(candidates),
        )
