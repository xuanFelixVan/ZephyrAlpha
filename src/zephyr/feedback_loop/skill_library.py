# [BLUEPRINT] MOD-FBL-003 | docs/03_modules/_domain_feedback_loop/skill_library/blueprint.md
# [MODULE] zephyr.feedback_loop.skill_library
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] 无（协议核心纯内存；embedder/clock 全注入）
# [CONSUMERS] 运行时装配批（反馈回路技能检索/复用登记/版本演进统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 技能类别词表闭合(code_snippet|strategy_template|factor_formula); skill_id 确定性递增(skill-NNNN); 向量索引经注入 embedder 构建+余弦 TopK 检索(同分按 skill_id 升序 tie-break); 复用登记仅已注册技能; 更新即版本递增(version+1)且内容变更重算向量; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_feedback_loop/skill_library/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SkillLibraryError(占位 ZA-FBL-UNREGISTERED-SKILL-LIBRARY)——非法类别/空内容/空来源任务/非法成功指标/未知技能/向量维度不符/非法top_k/embedder未注入时抛
# [TESTS] tests/feedback_loop/test_skill_library.py
# [A_module] module_id=MOD-FBL-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""


SkillLibrary — Voyager 式技能库（MOD-FBL-003）。

B12-03612（AUD-DRAFT-001-DIGEST P2 波 P2-W14，CAND-FBL-005，B12）：技能条目
Schema（**代码片段 / 策略模板 / 因子公式**三类词表闭合 + 来源任务 + 成功指标）
+ **向量索引**（注入 embedder，余弦相似度 TopK 检索）+ 新任务检索**复用登记**
+ **版本递增**（每次更新 version+1，内容变更重算向量）。

纯内存确定性：embedder/时钟全注入，无网络/无子进程；同输入必同输出。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: embedder 参数
#   fields: 参数 embedder（无注解）
#   code: skill_library.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: skill_library.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SkillLibrary
#   name_en: SkillLibrary
#   intro: Voyager 式技能库（注册 + 向量检索 TopK + 复用登记 + 版本递增）。
#   desc: Voyager 式技能库（注册 + 向量检索 TopK + 复用登记 + 版本递增）。；公共方法（定义序）: register_skill, update_skill, retrieve, register_reuse…
#   inputs: embedder clock
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: SkillLibrary
#   downstream: 运行时装配批（反馈回路技能检索/复用登记/版本演进统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "SkillEntry",
    "SkillKind",
    "SkillLibrary",
    "SkillLibraryError",
    "SkillReuseRecord",
]


class SkillLibraryError(Exception):
    """技能库输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FBL-UNREGISTERED-SKILL-LIBRARY。
    """


class SkillKind(str, Enum):
    """技能类别（词表闭合）。"""

    CODE_SNIPPET = "code_snippet"  # 代码片段
    STRATEGY_TEMPLATE = "strategy_template"  # 策略模板
    FACTOR_FORMULA = "factor_formula"  # 因子公式


@dataclass(frozen=True)
class SkillEntry:
    """技能条目 Schema（frozen；更新产生新实例，version 递增）。"""

    skill_id: str
    kind: SkillKind
    content: str
    source_task: str
    success_metrics: dict
    embedding: tuple[float, ...]
    version: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class SkillReuseRecord:
    """复用登记记录（frozen）。"""

    record_id: str
    skill_id: str
    task_description: str
    similarity: float
    reused_at: datetime.datetime


def _require_finite_number(value: object, field: str) -> float:
    """数值校验：非 bool 的 int/float 且有限，否则 Fail-Closed。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SkillLibraryError(f"{field} 非数值: {value!r}")
    out = float(value)
    if not math.isfinite(out):
        raise SkillLibraryError(f"{field} 非有限数值: {value!r}")
    return out


def _cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """余弦相似度（确定性；零向量按 0.0 处理；维度不符 Fail-Closed）。"""
    if len(a) != len(b):
        raise SkillLibraryError(f"向量维度不符: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class SkillLibrary:
    """Voyager 式技能库（注册 + 向量检索 TopK + 复用登记 + 版本递增）。"""

    def __init__(
        self,
        *,
        embedder: Callable[[str], Sequence[float]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if embedder is None:
            raise SkillLibraryError("embedder 未注入（向量索引强制注入，Fail-Closed）")
        self._embedder = embedder
        self._clock = clock or datetime.datetime.now
        self._skills: dict[str, SkillEntry] = {}
        self._reuse: list[SkillReuseRecord] = []
        self._seq = 0
        self._reuse_seq = 0

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _embed(self, text: str) -> tuple[float, ...]:
        """经注入 embedder 取向量并校验（非空/数值/有限）。"""
        raw = self._embedder(text)
        if raw is None:
            raise SkillLibraryError("embedder 返回 None")
        vec = tuple(_require_finite_number(v, "embedding 分量") for v in raw)
        if not vec:
            raise SkillLibraryError("embedder 返回空向量")
        return vec

    @staticmethod
    def _normalize_kind(kind: SkillKind | str) -> SkillKind:
        if isinstance(kind, SkillKind):
            return kind
        if isinstance(kind, str):
            try:
                return SkillKind(kind)
            except ValueError:
                raise SkillLibraryError(f"非法技能类别: {kind!r}（词表闭合: {[k.value for k in SkillKind]}）") from None
        raise SkillLibraryError(f"非法技能类别类型: {kind!r}")

    @staticmethod
    def _validate_metrics(success_metrics: Mapping[str, float]) -> dict:
        if not isinstance(success_metrics, Mapping):
            raise SkillLibraryError(f"success_metrics 非映射: {success_metrics!r}")
        out: dict[str, float] = {}
        for name, value in success_metrics.items():
            if not isinstance(name, str) or not name:
                raise SkillLibraryError(f"成功指标名非法: {name!r}")
            out[name] = _require_finite_number(value, f"成功指标 {name!r}")
        return out

    def _entry_of(self, skill_id: str) -> SkillEntry:
        entry = self._skills.get(skill_id)
        if entry is None:
            raise SkillLibraryError(f"未知技能: {skill_id!r}（未注册）")
        return entry

    # ── 注册 / 更新（版本递增） ────────────────────────────────────────────

    def register_skill(
        self,
        *,
        kind: SkillKind | str,
        content: str,
        source_task: str,
        success_metrics: Mapping[str, float],
    ) -> SkillEntry:
        """登记新技能：词表校验 → embedder 建向量 → skill_id 递增、version=1。"""
        norm_kind = self._normalize_kind(kind)
        if not isinstance(content, str) or not content:
            raise SkillLibraryError("content 为空")
        if not isinstance(source_task, str) or not source_task:
            raise SkillLibraryError("source_task 为空")
        metrics = self._validate_metrics(success_metrics)
        embedding = self._embed(content)
        self._seq += 1
        now = self._clock()
        entry = SkillEntry(
            skill_id=f"skill-{self._seq:04d}",
            kind=norm_kind,
            content=content,
            source_task=source_task,
            success_metrics=metrics,
            embedding=embedding,
            version=1,
            created_at=now,
            updated_at=now,
        )
        self._skills[entry.skill_id] = entry
        _log.info("技能登记: %s (%s) v1", entry.skill_id, norm_kind.value)
        return entry

    def update_skill(
        self,
        skill_id: str,
        *,
        content: str | None = None,
        success_metrics: Mapping[str, float] | None = None,
    ) -> SkillEntry:
        """更新技能：version+1；content 变更重算向量；无更新字段 Fail-Closed。"""
        old = self._entry_of(skill_id)
        if content is None and success_metrics is None:
            raise SkillLibraryError("无更新字段（content/success_metrics 至少其一）")
        new_content = old.content if content is None else content
        if not isinstance(new_content, str) or not new_content:
            raise SkillLibraryError("content 为空")
        new_metrics = old.success_metrics if success_metrics is None else self._validate_metrics(success_metrics)
        new_embedding = old.embedding if content is None else self._embed(new_content)
        entry = SkillEntry(
            skill_id=old.skill_id,
            kind=old.kind,
            content=new_content,
            source_task=old.source_task,
            success_metrics=dict(new_metrics),
            embedding=new_embedding,
            version=old.version + 1,
            created_at=old.created_at,
            updated_at=self._clock(),
        )
        self._skills[skill_id] = entry
        _log.info("技能更新: %s v%d", skill_id, entry.version)
        return entry

    # ── 向量检索（TopK） ──────────────────────────────────────────────────

    def retrieve(self, task_description: str, *, top_k: int = 1) -> tuple[SkillEntry, ...]:
        """新任务检索：余弦相似度 TopK（同分按 skill_id 升序，确定性）。"""
        if not isinstance(task_description, str) or not task_description:
            raise SkillLibraryError("task_description 为空")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise SkillLibraryError(f"非法 top_k: {top_k!r}（须正整数）")
        if not self._skills:
            return ()
        query = self._embed(task_description)
        scored = [(_cosine(query, entry.embedding), entry.skill_id, entry) for entry in self._skills.values()]
        scored.sort(key=lambda item: (-item[0], item[1]))
        return tuple(entry for _, _, entry in scored[:top_k])

    # ── 复用登记 ──────────────────────────────────────────────────────────

    def register_reuse(self, skill_id: str, *, task_description: str, similarity: float) -> SkillReuseRecord:
        """复用登记：仅已注册技能；similarity 须 [-1,1] 有限实数。"""
        self._entry_of(skill_id)
        if not isinstance(task_description, str) or not task_description:
            raise SkillLibraryError("task_description 为空")
        sim = _require_finite_number(similarity, "similarity")
        if not (-1.0 <= sim <= 1.0):
            raise SkillLibraryError(f"similarity 越界 [-1,1]: {sim!r}")
        self._reuse_seq += 1
        record = SkillReuseRecord(
            record_id=f"reuse-{self._reuse_seq:04d}",
            skill_id=skill_id,
            task_description=task_description,
            similarity=sim,
            reused_at=self._clock(),
        )
        self._reuse.append(record)
        _log.info("技能复用: %s <- %r (sim=%.4f)", skill_id, task_description, sim)
        return record

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get(self, skill_id: str) -> SkillEntry:
        """单技能查询（未知 → Fail-Closed）。"""
        return self._entry_of(skill_id)

    def list_skills(self, kind: SkillKind | str | None = None) -> tuple[SkillEntry, ...]:
        """技能清单（可按类别过滤；按 skill_id 升序，确定性）。"""
        norm_kind = None if kind is None else self._normalize_kind(kind)
        return tuple(
            entry
            for entry in sorted(self._skills.values(), key=lambda e: e.skill_id)
            if norm_kind is None or entry.kind is norm_kind
        )

    def reuse_records(self, skill_id: str | None = None) -> tuple[SkillReuseRecord, ...]:
        """复用登记流水（可按技能过滤；按登记顺序，确定性）。"""
        if skill_id is None:
            return tuple(self._reuse)
        self._entry_of(skill_id)
        return tuple(r for r in self._reuse if r.skill_id == skill_id)

    def reuse_count(self, skill_id: str) -> int:
        """单技能复用次数（未知 → Fail-Closed）。"""
        self._entry_of(skill_id)
        return sum(1 for r in self._reuse if r.skill_id == skill_id)

    def __len__(self) -> int:
        return len(self._skills)
