# [BLUEPRINT] MOD-KNW-007 | docs/03_modules/_domain_knowledge/ai_knowledge_extractor/blueprint.md
# [MODULE] zephyr.knowledge.ai_knowledge_extractor
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（纯内存批处理管线；llm_extractor/kb_writer/clock 全注入）
# [CONSUMERS] 运行时装配批（三类源注册 / 真实 LLM 回调绑定 / KB 写入接 knowledge 集合 / 人工复核队列消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 源类型词表闭合(experiment_report|research_note|strategy_code); LLM 结构化输出 schema 校验坏输出 Fail-Closed 不入库; 置信度低于阈值强制转人工队列不直写 KB; checkpoint 导出/恢复后同批不重跑（COMPLETED 幂等跳过，FAILED 可重试）; 批处理按注册序确定性执行; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/ai_knowledge_extractor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AiExtractorError(占位 ZA-KNW-UNREGISTERED-AI-EXTRACTOR)——空字段/未知源/重复注册/LLM回调缺失/输出schema非法/置信度越界/kb_writer缺失/未知复核项时抛
# [TESTS] tests/knowledge/test_ai_knowledge_extractor.py
# [A_module] module_id=MOD-KNW-007 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
AiKnowledgeExtractor — AI 自动知识提取器（MOD-KNW-007）。

B10-02191（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-007，A1 D-KNOWLEDGE-17）：
实验报告/研究笔记/策略代码**三类源**（词表闭合）经 LLM 抽取写 KB 的**批处理
管线**——源注册 + 抽取（**注入 llm 回调**，结构化输出 **schema 校验**，坏输出
**Fail-Closed** 标记 FAILED 不落库）+ **人工确认队列**（置信度低于阈值强制转
人工，不直写 KB）+ 批处理进度**断点续跑**（CheckpointState 导出/恢复，
COMPLETED 幂等跳过、FAILED 可重试）+ **写 KB 注入回调**。

查重分工（蓝图 §0）：feedback_loop/collectors/knowledge_capture=在线知识捕获
（事件流逐条，本件=离线批处理管线）；kb_engine=通用 CRUD 门面（本件仅经注入
kb_writer 写入）；strategy_knowledge_base/factor_knowledge_base=目的端 KB
Schema（本件产物经 kb_writer 路由，不识目的端结构）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: llm_extractor 参数
#   fields: 参数 llm_extractor（无注解）
#   code: ai_knowledge_extractor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: kb_writer 参数
#   fields: 参数 kb_writer（无注解）
#   code: ai_knowledge_extractor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: ai_knowledge_extractor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: confidence_threshold 参数
#   fields: 参数 confidence_threshold（无注解）
#   code: ai_knowledge_extractor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AiKnowledgeExtractor
#   name_en: AiKnowledgeExtractor
#   intro: AI 知识抽取批处理管线（源注册→LLM抽取→人工队列/写KB→断点续跑）。
#   desc: AI 知识抽取批处理管线（源注册→LLM抽取→人工队列/写KB→断点续跑）。；公共方法（定义序）: register_source, source_status, run_batch, export_checkpoin…
#   inputs: llm_extractor kb_writer clock confidence_threshold checkpoint
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: AiKnowledgeExtractor
#   downstream: 运行时装配批（三类源注册 / 真实 LLM 回调绑定 / KB 写入接 knowledge 集合 / 人工复核队列消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AiExtractorError",
    "AiKnowledgeExtractor",
    "BatchReport",
    "CheckpointState",
    "KnowledgeItem",
    "KnowledgeSource",
    "SourceStatus",
    "SourceType",
]

#: LLM 结构化输出必填字段
_REQUIRED_ITEM_FIELDS: Final[tuple[str, ...]] = ("title", "content", "confidence")


class AiExtractorError(Exception):
    """AI 知识抽取管线输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-AI-EXTRACTOR。
    """


class SourceType(str, Enum):
    """知识源类型（词表闭合）。"""

    EXPERIMENT_REPORT = "experiment_report"
    RESEARCH_NOTE = "research_note"
    STRATEGY_CODE = "strategy_code"


class SourceStatus(str, Enum):
    """源批处理状态机。"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class KnowledgeSource:
    """知识源（frozen）：标识/闭合类型/原文。"""

    source_id: str
    source_type: SourceType
    content: str
    registered_at: datetime.datetime


@dataclass(frozen=True)
class KnowledgeItem:
    """抽取产物（frozen）：确定性 item_key 回链源。"""

    item_key: str
    source_id: str
    title: str
    content: str
    confidence: float
    tags: tuple[str, ...]


@dataclass(frozen=True)
class CheckpointState:
    """断点续跑快照（frozen）：源状态表 + 产物序号。"""

    statuses: tuple[tuple[str, str], ...]  # (source_id, SourceStatus.value) 排序
    item_seq: int


@dataclass(frozen=True)
class BatchReport:
    """批处理结果（frozen）：处理/完成/失败/转人工/写 KB 计数。"""

    processed: int
    completed: int
    failed: int
    review_count: int
    written_count: int


class AiKnowledgeExtractor:
    """AI 知识抽取批处理管线（源注册→LLM抽取→人工队列/写KB→断点续跑）。"""

    def __init__(
        self,
        *,
        llm_extractor: Callable[[KnowledgeSource], Mapping[str, object]] | None = None,
        kb_writer: Callable[[KnowledgeItem], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        confidence_threshold: float = 0.7,
        checkpoint: CheckpointState | None = None,
    ) -> None:
        if not 0.0 <= confidence_threshold <= 1.0:
            raise AiExtractorError(f"confidence_threshold 越界 [0,1]: {confidence_threshold!r}")
        self._llm = llm_extractor
        self._kb_writer = kb_writer
        self._clock = clock or datetime.datetime.now
        self._threshold = float(confidence_threshold)
        self._sources: dict[str, KnowledgeSource] = {}
        self._status: dict[str, SourceStatus] = {}
        self._items: dict[str, KnowledgeItem] = {}
        self._review_queue: dict[str, KnowledgeItem] = {}
        self._item_seq = 0
        if checkpoint is not None:
            self._item_seq = checkpoint.item_seq
            for source_id, status_value in checkpoint.statuses:
                try:
                    self._status[source_id] = SourceStatus(status_value)
                except ValueError as exc:
                    raise AiExtractorError(f"checkpoint 状态词表非法: {status_value!r}") from exc

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _require_source(self, source_id: str) -> None:
        if source_id not in self._sources:
            raise AiExtractorError(f"未知知识源: {source_id!r}（未注册）")

    def _validate_llm_output(self, source_id: str, raw: object) -> list[KnowledgeItem]:
        """结构化输出 schema 校验：坏输出 Fail-Closed。"""
        if not isinstance(raw, Mapping) or not isinstance(raw.get("items"), list):
            raise AiExtractorError(f"LLM 输出 schema 非法: {source_id!r}（须含 items 列表）")
        items: list[KnowledgeItem] = []
        for entry in raw["items"]:
            if not isinstance(entry, Mapping):
                raise AiExtractorError(f"LLM 输出条目非映射: {source_id!r}")
            for field in _REQUIRED_ITEM_FIELDS:
                if field not in entry:
                    raise AiExtractorError(f"LLM 输出缺字段 {field!r}: {source_id!r}")
            title = entry["title"]
            content = entry["content"]
            confidence = entry["confidence"]
            tags = entry.get("tags", ())
            if not isinstance(title, str) or not title:
                raise AiExtractorError(f"LLM 输出 title 非法: {source_id!r}")
            if not isinstance(content, str):
                raise AiExtractorError(f"LLM 输出 content 非法: {source_id!r}")
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
                raise AiExtractorError(f"LLM 输出 confidence 非数值: {source_id!r}")
            if not 0.0 <= float(confidence) <= 1.0:
                raise AiExtractorError(f"LLM 输出 confidence 越界 [0,1]: {source_id!r}")
            if not isinstance(tags, (list, tuple)) or not all(isinstance(t, str) for t in tags):
                raise AiExtractorError(f"LLM 输出 tags 非法: {source_id!r}")
            self._item_seq += 1
            items.append(
                KnowledgeItem(
                    item_key=f"{source_id}#K{self._item_seq:04d}",
                    source_id=source_id,
                    title=title,
                    content=content,
                    confidence=float(confidence),
                    tags=tuple(tags),
                )
            )
        return items

    def _write_kb(self, item: KnowledgeItem) -> None:
        if self._kb_writer is None:
            raise AiExtractorError("kb_writer 未注入（写 KB 强制注入回调，禁止旁路）")
        try:
            self._kb_writer(item)
        except Exception as exc:  # noqa: BLE001 — 写 KB 异常统一 Fail-Closed
            raise AiExtractorError(f"kb_writer 写入失败: {item.item_key!r}: {exc}") from exc

    # ── 源注册 ────────────────────────────────────────────────────────────

    def register_source(self, source_type: SourceType, source_id: str, content: str) -> KnowledgeSource:
        """注册知识源：空字段/词表外类型/重复注册 → Fail-Closed。"""
        if not source_id:
            raise AiExtractorError("source_id 为空")
        if not isinstance(source_type, SourceType):
            raise AiExtractorError(f"非法源类型: {source_type!r}（词表闭合）")
        if not content:
            raise AiExtractorError(f"content 为空: {source_id!r}")
        if source_id in self._sources:
            raise AiExtractorError(f"知识源重复注册: {source_id!r}")
        source = KnowledgeSource(
            source_id=source_id,
            source_type=source_type,
            content=content,
            registered_at=self._clock(),
        )
        self._sources[source_id] = source
        # checkpoint 恢复：已知状态沿用（断点续跑），否则 PENDING
        self._status.setdefault(source_id, SourceStatus.PENDING)
        return source

    def source_status(self, source_id: str) -> SourceStatus:
        """单源状态查询（未知 → Fail-Closed）。"""
        self._require_source(source_id)
        return self._status[source_id]

    # ── 批处理管线 ────────────────────────────────────────────────────────

    def run_batch(self, source_ids: tuple[str, ...] | None = None) -> BatchReport:
        """批处理：按注册序（或指定序）抽取；COMPLETED 幂等跳过，FAILED 重试。

        LLM 回调未注入/输出 schema 非法/写 KB 失败 → 源标记 FAILED 并 Fail-Closed
        抛出（批中断，checkpoint 语义保留，可修复后续跑）。
        """
        if self._llm is None:
            raise AiExtractorError("llm_extractor 未注入（LLM 抽取强制注入回调）")
        if source_ids is None:
            targets = [sid for sid in self._sources]
        else:
            for sid in source_ids:
                self._require_source(sid)
            targets = list(source_ids)
        processed = completed = failed = review_count = written_count = 0
        for sid in targets:
            if self._status[sid] is SourceStatus.COMPLETED:
                continue  # 断点续跑：已完成幂等跳过
            processed += 1
            source = self._sources[sid]
            try:
                raw = self._llm(source)
            except AiExtractorError:
                self._status[sid] = SourceStatus.FAILED
                failed += 1
                raise
            except Exception as exc:  # noqa: BLE001 — LLM 回调异常按坏输出 Fail-Closed
                self._status[sid] = SourceStatus.FAILED
                failed += 1
                raise AiExtractorError(f"llm_extractor 抽取异常: {sid!r}: {exc}") from exc
            try:
                items = self._validate_llm_output(sid, raw)
            except AiExtractorError:
                self._status[sid] = SourceStatus.FAILED
                failed += 1
                _log.warning("LLM 输出 schema 校验失败（Fail-Closed 不入库）: %s", sid)
                raise
            try:
                for item in items:
                    self._items[item.item_key] = item
                    if item.confidence < self._threshold:
                        self._review_queue[item.item_key] = item  # 低置信度转人工
                        review_count += 1
                    else:
                        self._write_kb(item)
                        written_count += 1
            except AiExtractorError:
                self._status[sid] = SourceStatus.FAILED
                failed += 1
                raise
            self._status[sid] = SourceStatus.COMPLETED
            completed += 1
        return BatchReport(
            processed=processed,
            completed=completed,
            failed=failed,
            review_count=review_count,
            written_count=written_count,
        )

    # ── 断点续跑 ──────────────────────────────────────────────────────────

    def export_checkpoint(self) -> CheckpointState:
        """导出断点快照（状态表排序，确定性）。"""
        return CheckpointState(
            statuses=tuple(sorted((sid, st.value) for sid, st in self._status.items())),
            item_seq=self._item_seq,
        )

    # ── 人工确认队列 ──────────────────────────────────────────────────────

    def pending_review(self) -> tuple[KnowledgeItem, ...]:
        """待人工复核项（item_key 确定性排序）。"""
        return tuple(self._review_queue[key] for key in sorted(self._review_queue))

    def resolve_review(self, item_key: str, *, approve: bool) -> None:
        """复核裁决：通过→写 KB 出队；驳回→直接出队；未知项 → Fail-Closed。"""
        item = self._review_queue.get(item_key)
        if item is None:
            raise AiExtractorError(f"未知复核项: {item_key!r}")
        if approve:
            self._write_kb(item)
        del self._review_queue[item_key]

    # ── 产物查询 ──────────────────────────────────────────────────────────

    def items_of(self, source_id: str) -> tuple[KnowledgeItem, ...]:
        """单源抽取产物（item_key 确定性排序）。"""
        self._require_source(source_id)
        return tuple(self._items[key] for key in sorted(self._items) if self._items[key].source_id == source_id)
