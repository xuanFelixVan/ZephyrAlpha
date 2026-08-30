# [BLUEPRINT] MOD-CMP-017 | docs/03_modules/_domain_compliance/regulatory_change_tracker/blueprint.md
# [MODULE] zephyr.compliance.regulatory_change_tracker
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] 无（协议核心纯内存；clock/公告源/NLP抽取器/影响域表 全注入；仅 stdlib）
# [CONSUMERS] 运行时装配批（公告源与LLM抽取统一注入 / 评审任务入人工确认队列）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 公告源/抽取器未注入Fail-Closed; 公告按(published_at,notice_id)确定性处理; notice_id去重幂等; 抽取结果结构化校验(变更类型词表/生效日期/条款非空串); 影响域=条款关联表确定性并集排序; 评审任务PENDING→人工CONFIRMED; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_compliance/regulatory_change_tracker/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RegulatoryTrackerError(占位 ZA-CMP-UNREGISTERED-REGULATORY-TRACKER)——源/抽取器缺失/公告非法/抽取结构非法/未知任务/重复确认时抛
# [TESTS] tests/compliance/test_regulatory_change_tracker.py
# [A_module] module_id=MOD-CMP-017 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
RegulatoryChangeTracker — 监管变更追踪器（MOD-CMP-017）。

B14-04671（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-CMP-008，A9 M36-S05）：
证监会/交易所**公告采集**（注入源，不真发请求）+ **NLP 变更抽取**（注入
llm：变更类型/生效日期/涉及条款**结构化校验**）+ **影响域映射**（规则库
条款关联表）→ **合规规则评审任务**（人工确认后入 Policy-as-Code 规则库
语义）。

设计要点：
- **纯内存/DI**：公告源与 NLP 抽取器全部注入（不触网不调用真实 LLM）；
  时钟注入；影响域关联表 init 注入。
- **Fail-Closed**：源/抽取器未注入、公告元素非法、抽取结果缺键/类型不
  符/变更类型越词表/生效日期非法一律抛 RegulatoryTrackerError。
- **确定性**：公告按 (published_at, notice_id) 排序处理；notice_id 去重
  幂等；影响域为条款关联表的排序去重并集；评审任务 task_id 由 notice_id
  唯一决定，同输入必同输出。

查重分工：feedback_loop 可靠性族 regulatory_audit=反馈回路审计（无公告采
集/影响域映射/评审任务语义）；compliance_policy_engine=规则库版本与激活
（本件只产出评审任务，确认后由装配批入规则库，不直连引擎）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: regulatory_change_tracker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: source 参数
#   fields: 参数 source（无注解）
#   code: regulatory_change_tracker.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: extractor 参数
#   fields: 参数 extractor（无注解）
#   code: regulatory_change_tracker.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: impact_table 参数
#   fields: 参数 impact_table（无注解）
#   code: regulatory_change_tracker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RegulatoryChangeTracker
#   name_en: RegulatoryChangeTracker
#   intro: 监管变更追踪器（采集 → 抽取校验 → 影响域映射 → 评审任务）。
#   desc: 监管变更追踪器（采集 → 抽取校验 → 影响域映射 → 评审任务）。 Args: clock: 时钟注入。 source: 公告采集源注入（不真发请求）；None → Fail-…；公共方法（定义序）: collect…
#   inputs: clock source extractor impact_table
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: RegulatoryChangeTracker
#   downstream: 运行时装配批（公告源与LLM抽取统一注入 / 评审任务入人工确认队列）
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
from typing import Callable, Final, Iterable, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "Announcement",
    "ChangeType",
    "ExtractedChange",
    "RegulatoryChangeTracker",
    "RegulatoryTrackerError",
    "ReviewStatus",
    "ReviewTask",
]


class RegulatoryTrackerError(Exception):
    """监管变更追踪输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-CMP-UNREGISTERED-REGULATORY-TRACKER。
    """


class ChangeType(str, Enum):
    """监管变更类型（词表闭合）。"""

    NEW_RULE = "new_rule"  # 新规发布
    AMENDMENT = "amendment"  # 修订
    REPEAL = "repeal"  # 废止
    INTERPRETATION = "interpretation"  # 解释/指引


class ReviewStatus(str, Enum):
    """评审任务状态机。"""

    PENDING = "pending"
    CONFIRMED = "confirmed"


@dataclass(frozen=True)
class Announcement:
    """监管公告（采集源注入载体，frozen）。"""

    notice_id: str
    issuer: str  # 发布机构（如 CSRC/SSE/SZSE）
    title: str
    body: str
    published_at: datetime.datetime


@dataclass(frozen=True)
class ExtractedChange:
    """NLP 抽取的结构化变更（经校验后载体，frozen）。"""

    change_type: ChangeType
    effective_date: datetime.date
    clauses: tuple[str, ...]


@dataclass(frozen=True)
class ReviewTask:
    """合规规则评审任务（人工确认后入规则库语义，frozen）。"""

    task_id: str
    notice_id: str
    issuer: str
    change_type: ChangeType
    effective_date: datetime.date
    clauses: tuple[str, ...]
    affected_domains: tuple[str, ...]
    status: ReviewStatus
    created_at: datetime.datetime


_EXTRACTION_KEYS: Final[frozenset[str]] = frozenset({"change_type", "effective_date", "clauses"})


class RegulatoryChangeTracker:
    """监管变更追踪器（采集 → 抽取校验 → 影响域映射 → 评审任务）。

    Args:
        clock: 时钟注入。
        source: 公告采集源注入（不真发请求）；None → Fail-Closed。
        extractor: NLP 变更抽取器注入（不真调 LLM）；None → Fail-Closed。
        impact_table: 条款 → 影响域关联表注入；None 视为空表（影响域恒空）。
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        source: Callable[[], Iterable[Announcement]] | None = None,
        extractor: Callable[[Announcement], Mapping] | None = None,
        impact_table: Mapping[str, Iterable[str]] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        if source is None or not callable(source):
            raise RegulatoryTrackerError("公告采集源未注入（Fail-Closed）")
        if extractor is None or not callable(extractor):
            raise RegulatoryTrackerError("NLP 变更抽取器未注入（Fail-Closed）")
        self._source = source
        self._extractor = extractor
        table: dict[str, tuple[str, ...]] = {}
        for clause, domains in (impact_table or {}).items():
            if not isinstance(clause, str) or not clause:
                raise RegulatoryTrackerError(f"影响域表条款键非法: {clause!r}")
            table[clause] = tuple(sorted({str(d) for d in domains}))
        self._impact_table = table
        self._tasks: dict[str, ReviewTask] = {}  # notice_id → task

    # ── 公告校验 ──────────────────────────────────────────────────────────

    @staticmethod
    def _validate_announcement(item: object) -> Announcement:
        if not isinstance(item, Announcement):
            raise RegulatoryTrackerError(f"公告元素非法: {type(item).__name__!r}")
        if not item.notice_id:
            raise RegulatoryTrackerError("notice_id 为空")
        if not item.issuer:
            raise RegulatoryTrackerError(f"issuer 为空: {item.notice_id!r}")
        if not isinstance(item.published_at, datetime.datetime):
            raise RegulatoryTrackerError(f"published_at 非法: {item.notice_id!r}")
        return item

    # ── 抽取结果结构化校验 ─────────────────────────────────────────────────

    @staticmethod
    def _validate_extraction(notice_id: str, raw: object) -> ExtractedChange:
        if not isinstance(raw, Mapping):
            raise RegulatoryTrackerError(f"抽取结果非 Mapping: {notice_id!r}")
        missing = _EXTRACTION_KEYS - set(raw)
        if missing:
            raise RegulatoryTrackerError(f"抽取结果缺键: {notice_id!r} {sorted(missing)}")
        try:
            change_type = ChangeType(raw["change_type"])
        except ValueError as exc:
            raise RegulatoryTrackerError(f"变更类型越词表: {notice_id!r} {raw['change_type']!r}") from exc
        effective = raw["effective_date"]
        if not isinstance(effective, datetime.date):
            raise RegulatoryTrackerError(f"生效日期非法: {notice_id!r} {effective!r}")
        clauses_raw = raw["clauses"]
        if not isinstance(clauses_raw, Sequence) or isinstance(clauses_raw, (str, bytes)):
            raise RegulatoryTrackerError(f"涉及条款非法（须为序列）: {notice_id!r}")
        clauses: list[str] = []
        for clause in clauses_raw:
            if not isinstance(clause, str) or not clause:
                raise RegulatoryTrackerError(f"涉及条款含空串/非字符串: {notice_id!r} {clause!r}")
            clauses.append(clause)
        return ExtractedChange(
            change_type=change_type,
            effective_date=effective,
            clauses=tuple(clauses),
        )

    # ── 影响域映射 ─────────────────────────────────────────────────────────

    def _affected_domains(self, clauses: tuple[str, ...]) -> tuple[str, ...]:
        domains: set[str] = set()
        for clause in clauses:
            domains.update(self._impact_table.get(clause, ()))
        return tuple(sorted(domains))

    # ── 采集 → 评审任务 ────────────────────────────────────────────────────

    def collect(self) -> list[ReviewTask]:
        """采集公告并生成评审任务（去重幂等；确定性排序处理）。"""
        raw = self._source()
        if not isinstance(raw, Iterable) or isinstance(raw, (str, bytes, Mapping)):
            raise RegulatoryTrackerError("公告源返回非法（须为可迭代 Announcement 序列）")
        announcements = [self._validate_announcement(item) for item in raw]
        announcements.sort(key=lambda a: (a.published_at, a.notice_id))
        out: list[ReviewTask] = []
        for announcement in announcements:
            existing = self._tasks.get(announcement.notice_id)
            if existing is not None:
                continue  # notice_id 去重幂等
            change = self._validate_extraction(announcement.notice_id, self._extractor(announcement))
            task = ReviewTask(
                task_id=f"REV-{announcement.notice_id}",
                notice_id=announcement.notice_id,
                issuer=announcement.issuer,
                change_type=change.change_type,
                effective_date=change.effective_date,
                clauses=change.clauses,
                affected_domains=self._affected_domains(change.clauses),
                status=ReviewStatus.PENDING,
                created_at=self._clock(),
            )
            self._tasks[announcement.notice_id] = task
            out.append(task)
            _log.info(
                "监管变更评审任务: %s type=%s effective=%s domains=%s",
                task.task_id,
                task.change_type.value,
                task.effective_date,
                task.affected_domains,
            )
        return out

    # ── 人工确认 ──────────────────────────────────────────────────────────

    def confirm_task(self, task_id: str) -> ReviewTask:
        """人工确认评审任务（仅 PENDING；确认后语义上入 Policy-as-Code 规则库）。"""
        task = self._find_task(task_id)
        if task.status is not ReviewStatus.PENDING:
            raise RegulatoryTrackerError(f"非法确认: {task_id!r} 当前 {task.status.value}（重复确认）")
        confirmed = ReviewTask(
            task_id=task.task_id,
            notice_id=task.notice_id,
            issuer=task.issuer,
            change_type=task.change_type,
            effective_date=task.effective_date,
            clauses=task.clauses,
            affected_domains=task.affected_domains,
            status=ReviewStatus.CONFIRMED,
            created_at=task.created_at,
        )
        self._tasks[task.notice_id] = confirmed
        _log.info("评审任务确认: %s（人工确认后入规则库）", task_id)
        return confirmed

    def _find_task(self, task_id: str) -> ReviewTask:
        for task in self._tasks.values():
            if task.task_id == task_id:
                return task
        raise RegulatoryTrackerError(f"未知评审任务: {task_id!r}")

    # ── 查询 ─────────────────────────────────────────────────────────────

    def pending_tasks(self) -> list[ReviewTask]:
        """待评审任务（按 (created_at, task_id) 确定性排序）。"""
        out = [t for t in self._tasks.values() if t.status is ReviewStatus.PENDING]
        out.sort(key=lambda t: (t.created_at, t.task_id))
        return out

    def task_of(self, notice_id: str) -> ReviewTask:
        """按 notice_id 查任务（未知 → Fail-Closed）。"""
        task = self._tasks.get(notice_id)
        if task is None:
            raise RegulatoryTrackerError(f"未知公告任务: {notice_id!r}")
        return task

    def tracked_notices(self) -> tuple[str, ...]:
        """已追踪公告 notice_id（确定性排序）。"""
        return tuple(sorted(self._tasks))
