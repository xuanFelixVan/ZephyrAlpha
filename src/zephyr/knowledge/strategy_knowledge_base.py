# [BLUEPRINT] MOD-KNW-006 | docs/03_modules/_domain_knowledge/strategy_knowledge_base/blueprint.md
# [MODULE] zephyr.knowledge.strategy_knowledge_base
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（纯内存策略卡；kb_writer/backfill_adapter/clock/sqlite_conn 全注入）
# [CONSUMERS] 运行时装配批（策略卡注册入库 / experiment_tracking 回填适配器绑定 / 教训 FTS 挂 sqlite 连接）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 状态机 DRAFT→ACTIVE→RETIRED 闭合不可逆; 表现仅经注入回填适配器写入（无适配器 Fail-Closed 不旁路）; 教训 FTS 检索强制注入 sqlite 连接; 查询按 strategy_id/(-指标值,strategy_id) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/strategy_knowledge_base/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StrategyKbError(占位 ZA-KNW-UNREGISTERED-STRATEGY-KB)——空字段/未知策略/重复注册/非法状态迁移/回填适配器缺失或空返回/指标非数值/FTS连接缺失/空查询时抛
# [TESTS] tests/knowledge/test_strategy_knowledge_base.py
# [A_module] module_id=MOD-KNW-006 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
StrategyKnowledgeBase — 策略知识库（MOD-KNW-006）。

B10-02182（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-005，A1 D-KNOWLEDGE-03）：
**策略卡**（定义+表现+教训三要素 Schema）入 vector_memory decisions 集合语义
（**注入 kb_writer 回调**）+ 表现字段从 experiment_tracking **回填**（注入回填
适配器，未注入 Fail-Closed 不旁路）+ 策略卡查询（按状态/风格/表现区间，确定性
排序）+ 教训 **FTS 检索**（注入 sqlite 连接，FTS5）。

查重分工（蓝图 §0）：experiment_tracking=实验指标真源（本件仅经注入适配器回
填快照，不重算指标）；kb_engine=通用 CRUD 门面（本件仅挂其 decisions 集合语
义）；factor_knowledge_base=因子三表（本件=策略卡，零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: strategy_knowledge_base.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: kb_writer 参数
#   fields: 参数 kb_writer（无注解）
#   code: strategy_knowledge_base.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: backfill_adapter 参数
#   fields: 参数 backfill_adapter（无注解）
#   code: strategy_knowledge_base.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: sqlite_conn 参数
#   fields: 参数 sqlite_conn（无注解）
#   code: strategy_knowledge_base.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① StrategyKnowledgeBase
#   name_en: StrategyKnowledgeBase
#   intro: 策略知识库（策略卡三要素 + 回填 + FTS 教训检索 + 确定性查询）。
#   desc: 策略知识库（策略卡三要素 + 回填 + FTS 教训检索 + 确定性查询）。；公共方法（定义序）: register_card, get_card, get_status, refresh_performance, g…
#   inputs: clock kb_writer backfill_adapter sqlite_conn
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: StrategyKnowledgeBase
#   downstream: 运行时装配批（策略卡注册入库 / experiment_tracking 回填适配器绑定 / 教训 FTS 挂 sqlite 连接）
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
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "Lesson",
    "PerformanceRecord",
    "StrategyCard",
    "StrategyKbError",
    "StrategyKnowledgeBase",
    "StrategyStatus",
    "StatusTransition",
]

#: 合法状态迁移（DRAFT→ACTIVE→RETIRED 闭合；DRAFT 可直接下线）
_ALLOWED_TRANSITIONS: Final[dict[StrategyStatus, frozenset[StrategyStatus]]] = {}

#: 教训 FTS5 表名（注入 sqlite 连接上建表）
_FTS_TABLE: Final[str] = "strategy_lesson_fts"


class StrategyKbError(Exception):
    """策略知识库输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-STRATEGY-KB。
    """


class StrategyStatus(str, Enum):
    """策略卡状态机（词表闭合）。"""

    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"


_ALLOWED_TRANSITIONS.update(
    {
        StrategyStatus.DRAFT: frozenset({StrategyStatus.ACTIVE, StrategyStatus.RETIRED}),
        StrategyStatus.ACTIVE: frozenset({StrategyStatus.RETIRED}),
        StrategyStatus.RETIRED: frozenset(),
    }
)


@dataclass(frozen=True)
class StrategyCard:
    """策略卡定义要素（frozen）：标识/名称/风格/定义。"""

    strategy_id: str
    name: str
    style: str
    definition: Mapping[str, object]


@dataclass(frozen=True)
class PerformanceRecord:
    """表现要素（frozen）：指标快照 + 来源 + 回填时刻。"""

    strategy_id: str
    metrics: Mapping[str, float]
    source: str
    updated_at: datetime.datetime


@dataclass(frozen=True)
class Lesson:
    """教训要素（frozen）：确定性 lesson_id 回链策略卡。"""

    lesson_id: str
    strategy_id: str
    text: str
    created_at: datetime.datetime


@dataclass(frozen=True)
class StatusTransition:
    """状态变迁留痕（frozen）。"""

    strategy_id: str
    from_status: StrategyStatus
    to_status: StrategyStatus
    changed_at: datetime.datetime


class StrategyKnowledgeBase:
    """策略知识库（策略卡三要素 + 回填 + FTS 教训检索 + 确定性查询）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        kb_writer: Callable[[Mapping[str, object]], None] | None = None,
        backfill_adapter: Callable[[str], Mapping[str, float] | None] | None = None,
        sqlite_conn: sqlite3.Connection | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._kb_writer = kb_writer
        self._backfill_adapter = backfill_adapter
        self._conn = sqlite_conn
        self._cards: dict[str, StrategyCard] = {}
        self._status: dict[str, StrategyStatus] = {}
        self._performance: dict[str, PerformanceRecord] = {}
        self._lessons: dict[str, Lesson] = {}
        self._transitions: dict[str, list[StatusTransition]] = {}
        self._lesson_seq = 0
        if self._conn is not None:
            self._conn.execute(
                f"CREATE VIRTUAL TABLE IF NOT EXISTS {_FTS_TABLE} "
                "USING fts5(lesson_id UNINDEXED, strategy_id UNINDEXED, text)"
            )

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _require_card(self, strategy_id: str) -> None:
        if strategy_id not in self._cards:
            raise StrategyKbError(f"未知策略: {strategy_id!r}（未注册）")

    def _write_kb(self, entry: Mapping[str, object]) -> None:
        if self._kb_writer is None:
            return  # kb 写入回调可选：未注入仅内存留痕
        try:
            self._kb_writer(entry)
        except Exception:  # noqa: BLE001 — 外挂 kb 失败不阻断内存策略卡
            _log.exception("kb_writer 写入失败: %s", entry.get("strategy_id"))

    # ── 策略卡注册 ────────────────────────────────────────────────────────

    def register_card(self, card: StrategyCard) -> None:
        """注册策略卡（初始 DRAFT）：空字段/重复注册 → Fail-Closed。"""
        if not card.strategy_id:
            raise StrategyKbError("strategy_id 为空")
        if not card.name:
            raise StrategyKbError(f"name 为空: {card.strategy_id!r}")
        if not card.style:
            raise StrategyKbError(f"style 为空: {card.strategy_id!r}")
        if not card.definition:
            raise StrategyKbError(f"definition 为空: {card.strategy_id!r}")
        if card.strategy_id in self._cards:
            raise StrategyKbError(f"策略卡重复注册: {card.strategy_id!r}")
        self._cards[card.strategy_id] = card
        self._status[card.strategy_id] = StrategyStatus.DRAFT
        self._write_kb(
            {
                "kind": "strategy_card",
                "strategy_id": card.strategy_id,
                "name": card.name,
                "style": card.style,
                "status": StrategyStatus.DRAFT.value,
            }
        )

    def get_card(self, strategy_id: str) -> StrategyCard:
        """单卡查询（未知 → Fail-Closed）。"""
        self._require_card(strategy_id)
        return self._cards[strategy_id]

    def get_status(self, strategy_id: str) -> StrategyStatus:
        """单卡状态查询（未知 → Fail-Closed）。"""
        self._require_card(strategy_id)
        return self._status[strategy_id]

    # ── 表现回填（experiment_tracking 注入适配器） ─────────────────────────

    def refresh_performance(self, strategy_id: str) -> PerformanceRecord:
        """从 experiment_tracking 回填表现：适配器未注入/空返回/非数值 → Fail-Closed。"""
        self._require_card(strategy_id)
        if self._backfill_adapter is None:
            raise StrategyKbError("backfill_adapter 未注入（表现仅可经 experiment_tracking 回填，禁止旁路）")
        try:
            metrics = self._backfill_adapter(strategy_id)
        except StrategyKbError:
            raise
        except Exception as exc:  # noqa: BLE001 — 适配器异常统一 Fail-Closed
            raise StrategyKbError(f"backfill_adapter 回填异常: {strategy_id!r}: {exc}") from exc
        if not metrics:
            raise StrategyKbError(f"backfill_adapter 空返回: {strategy_id!r}")
        clean: dict[str, float] = {}
        for key, value in metrics.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise StrategyKbError(f"指标非数值: {key!r}={value!r}")
            clean[str(key)] = float(value)
        record = PerformanceRecord(
            strategy_id=strategy_id,
            metrics=clean,
            source="experiment_tracking",
            updated_at=self._clock(),
        )
        self._performance[strategy_id] = record
        self._write_kb(
            {
                "kind": "strategy_performance",
                "strategy_id": strategy_id,
                "metrics": dict(clean),
                "source": record.source,
            }
        )
        return record

    def get_performance(self, strategy_id: str) -> PerformanceRecord:
        """表现快照查询（未回填 → Fail-Closed）。"""
        self._require_card(strategy_id)
        record = self._performance.get(strategy_id)
        if record is None:
            raise StrategyKbError(f"表现未回填: {strategy_id!r}")
        return record

    # ── 教训（FTS5 检索） ────────────────────────────────────────────────

    def add_lesson(self, strategy_id: str, text: str) -> Lesson:
        """追加教训：lesson_id 确定性生成；注入连接时同步入 FTS 索引。"""
        self._require_card(strategy_id)
        if not text:
            raise StrategyKbError("教训文本为空")
        self._lesson_seq += 1
        lesson = Lesson(
            lesson_id=f"{strategy_id}#L{self._lesson_seq:03d}",
            strategy_id=strategy_id,
            text=text,
            created_at=self._clock(),
        )
        self._lessons[lesson.lesson_id] = lesson
        if self._conn is not None:
            self._conn.execute(
                f"INSERT INTO {_FTS_TABLE} (lesson_id, strategy_id, text) VALUES (?, ?, ?)",
                (lesson.lesson_id, lesson.strategy_id, text),
            )
        return lesson

    def lessons_of(self, strategy_id: str) -> tuple[Lesson, ...]:
        """单卡教训列表（lesson_id 确定性排序）。"""
        self._require_card(strategy_id)
        return tuple(
            self._lessons[lid] for lid in sorted(self._lessons) if self._lessons[lid].strategy_id == strategy_id
        )

    def search_lessons(self, query: str) -> tuple[Lesson, ...]:
        """教训 FTS 检索：连接未注入/空查询 → Fail-Closed；(rank, lesson_id) 确定性排序。"""
        if self._conn is None:
            raise StrategyKbError("sqlite_conn 未注入（教训 FTS 检索强制注入连接）")
        if not query or not query.strip():
            raise StrategyKbError("检索查询为空")
        try:
            rows = self._conn.execute(
                f"SELECT lesson_id, rank FROM {_FTS_TABLE} WHERE text MATCH ? ORDER BY rank, lesson_id",
                (query,),
            ).fetchall()
        except sqlite3.Error as exc:
            raise StrategyKbError(f"FTS 检索失败: {exc}") from exc
        return tuple(self._lessons[lesson_id] for lesson_id, _ in rows)

    # ── 状态机 ────────────────────────────────────────────────────────────

    def transition_status(self, strategy_id: str, to_status: StrategyStatus) -> StatusTransition:
        """状态迁移：非法迁移 Fail-Closed；留痕 + 同步 kb 写入回调。"""
        self._require_card(strategy_id)
        if not isinstance(to_status, StrategyStatus):
            raise StrategyKbError(f"非法状态: {to_status!r}（词表闭合）")
        from_status = self._status[strategy_id]
        if to_status not in _ALLOWED_TRANSITIONS[from_status]:
            raise StrategyKbError(f"非法状态迁移: {strategy_id!r} {from_status.value} -> {to_status.value}")
        transition = StatusTransition(
            strategy_id=strategy_id,
            from_status=from_status,
            to_status=to_status,
            changed_at=self._clock(),
        )
        self._status[strategy_id] = to_status
        self._transitions.setdefault(strategy_id, []).append(transition)
        self._write_kb(
            {
                "kind": "strategy_status",
                "strategy_id": strategy_id,
                "from_status": from_status.value,
                "to_status": to_status.value,
            }
        )
        return transition

    def status_history(self, strategy_id: str) -> tuple[StatusTransition, ...]:
        """状态变迁留痕（按写入序，确定性）。"""
        self._require_card(strategy_id)
        return tuple(self._transitions.get(strategy_id, ()))

    # ── 查询 ─────────────────────────────────────────────────────────────

    def by_status(self, status: StrategyStatus) -> tuple[StrategyCard, ...]:
        """按状态查询（strategy_id 确定性排序）。"""
        if not isinstance(status, StrategyStatus):
            raise StrategyKbError(f"非法状态: {status!r}（词表闭合）")
        return tuple(self._cards[sid] for sid in sorted(self._cards) if self._status[sid] is status)

    def by_style(self, style: str) -> tuple[StrategyCard, ...]:
        """按风格查询（strategy_id 确定性排序）。"""
        if not style:
            raise StrategyKbError("style 为空")
        return tuple(self._cards[sid] for sid in sorted(self._cards) if self._cards[sid].style == style)

    def by_performance_range(
        self,
        metric: str,
        *,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> tuple[StrategyCard, ...]:
        """按表现区间查询（含端点；按 (-指标值, strategy_id) 确定性排序）。

        仅纳入已回填且含该指标的卡；双侧均缺省 → Fail-Closed（无界区间非法）。
        """
        if not metric:
            raise StrategyKbError("metric 为空")
        if min_value is None and max_value is None:
            raise StrategyKbError("表现区间双侧均缺省（无界区间非法）")
        hits = []
        for sid, record in self._performance.items():
            value = record.metrics.get(metric)
            if value is None:
                continue
            if min_value is not None and value < min_value:
                continue
            if max_value is not None and value > max_value:
                continue
            hits.append((sid, value))
        hits.sort(key=lambda item: (-item[1], item[0]))
        return tuple(self._cards[sid] for sid, _ in hits)
