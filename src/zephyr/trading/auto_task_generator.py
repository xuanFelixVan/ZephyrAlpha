# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.auto_task_generator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.shared.event_bus; zephyr.governance.ops_governance.event_hook
# [CONSUMERS] zephyr.trading.boot_hooks._subscribe_eventbus_consumers
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_auto_task_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AutoTaskGenerator — 自动任务生成器
====================================
从项目代码、知识条目、审计日志中自动生成 L2 推理任务，
持续送进 LocalModelScheduler 保持 GPU 忙碌。

数据源:
    src/**/*.py       -> task_classification, tag_completion, naming_suggest
    data/capability_cards/*.yaml -> summary_extraction
    data/audit_logs/*.jsonl      -> anomaly_triage
    architecture_model/**/*.yaml -> summary_extraction

机制:
    - 每次 MAPE-K 调和周期生成一批任务
    - 维护已处理文件去重表，避免重复提交
    - 限制每批任务数量，防止队列膨胀
"""

from __future__ import annotations

from typing import Final
import hashlib
import logging
import time
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler

_log = logging.getLogger(__name__)

MAX_BATCH_SIZE: Final[int] = 12
MAX_QUEUE_DEPTH: Final[int] = 50
COOLDOWN_S: Final[float] = 120.0
FILE_READ_LIMIT_CHARS: Final[int] = 800


class AutoTaskGenerator:
    """自动任务生成器——扫描项目 -> 生成推理任务 -> 送入调度器。"""

    def __init__(
        self,
        project_root: Path | str,
        *,
        max_batch: int = MAX_BATCH_SIZE,
        max_queue_depth: int = MAX_QUEUE_DEPTH,
        cooldown_s: float = COOLDOWN_S,
    ) -> None:
        self._root = Path(project_root)
        self._max_batch = max_batch
        self._max_queue_depth = max_queue_depth
        self._cooldown = cooldown_s
        self._processed: set[str] = set()
        self._file_queue: deque[Path] = deque()
        self._last_scan_ts: float = 0.0
        self._stats: dict[str, int] = {"generated": 0, "submitted": 0, "skipped": 0}

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    def generate_and_submit(
        self,
        scheduler: LocalModelScheduler | None,
        *,
        force: bool = False,
    ) -> int:
        """生成一批任务并提交到调度器。返回提交数量。"""
        now = time.time()
        if not force and (now - self._last_scan_ts) < self._cooldown:
            if self._file_queue:
                return self._drain_queue(scheduler)
            return 0

        self._last_scan_ts = now

        if not self._file_queue:
            self._scan_sources()

        submitted = self._drain_queue(scheduler)

        if not self._file_queue or submitted < self._max_batch:
            self._scan_sources()
            submitted += self._drain_queue(scheduler)

        return submitted

    def _scan_sources(self) -> None:
        """扫描各数据源，发现新的文件加入处理队列。"""
        sources: list[tuple[str, str]] = [
            ("src/zephyr/**/*.py", "python"),
            ("architecture_model/**/*.yaml", "blueprint"),
            ("docs/**/*.md", "doc"),
        ]

        for glob_pattern, source_type in sources:
            try:
                for fp in self._root.glob(glob_pattern):
                    if not fp.is_file():
                        continue
                    fp_hash = self._file_hash(fp)
                    if fp_hash in self._processed:
                        continue
                    if len(self._file_queue) >= self._max_queue_depth:
                        break
                    self._file_queue.append(fp)
                    self._processed.add(fp_hash)
            except Exception:
                continue

        _log.debug(
            "AutoTaskGenerator: scanned sources, queue=%d files",
            len(self._file_queue),
        )

    def _drain_queue(self, scheduler: LocalModelScheduler | None) -> int:
        """从文件队列中消耗，生成推理任务提交到调度器。"""
        if scheduler is None:
            return 0

        submitted = 0
        while self._file_queue and submitted < self._max_batch:
            fp = self._file_queue.popleft()

            try:
                content = self._read_file_snippet(fp)
                if not content:
                    self._stats["skipped"] += 1
                    continue

                tasks = self._file_to_tasks(fp, content)
                for task_id, capability, payload in tasks:
                    try:
                        scheduler.enqueue(task_id, capability, payload)
                        submitted += 1
                        self._stats["submitted"] += 1
                    except Exception as exc:
                        _log.debug(
                            "AutoTaskGenerator: enqueue failed for %s: %s",
                            task_id,
                            exc,
                            exc_info=True,
                        )
                self._stats["generated"] += len(tasks)
            except Exception:
                self._stats["skipped"] += 1

        if submitted > 0:
            _log.info(
                "AutoTaskGenerator: submitted %d tasks (total: %d generated, %d skipped)",
                submitted,
                self._stats["generated"],
                self._stats["skipped"],
            )

        return submitted

    def _file_to_tasks(self, fp: Path, content: str) -> list[tuple[str, str, dict]]:
        """根据文件类型生成不同的推理任务。"""
        tasks: list[tuple[str, str, dict]] = []
        suffix = fp.suffix.lower()
        stem = fp.stem
        task_prefix = f"GEN-{stem[:20]}-"

        if suffix == ".py":
            tasks.append(
                (
                    f"{task_prefix}classify",
                    "task_classification",
                    {"text": f"classify this module: {stem}\n{content[:FILE_READ_LIMIT_CHARS]}"},
                )
            )
            tasks.append(
                (
                    f"{task_prefix}tag",
                    "tag_completion",
                    {"text": f"generate tags for: {stem}\n{content[:FILE_READ_LIMIT_CHARS]}"},
                )
            )
            if len(stem) > 3:
                tasks.append(
                    (
                        f"{task_prefix}name",
                        "naming_suggest",
                        {"text": f"suggest alternative names for module: {stem}\n{content[:FILE_READ_LIMIT_CHARS]}"},
                    )
                )

        elif suffix in (".yaml", ".yml"):
            tasks.append(
                (
                    f"{task_prefix}summary",
                    "summary_extraction",
                    {"text": f"summarize: {stem}\n{content[:FILE_READ_LIMIT_CHARS]}"},
                )
            )
            tasks.append(
                (
                    f"{task_prefix}tag",
                    "tag_completion",
                    {"text": f"generate tags for config: {stem}\n{content[:FILE_READ_LIMIT_CHARS]}"},
                )
            )

        elif suffix == ".md":
            tasks.append(
                (
                    f"{task_prefix}summary",
                    "summary_extraction",
                    {"text": content[:FILE_READ_LIMIT_CHARS]},
                )
            )
            tasks.append(
                (
                    f"{task_prefix}classify",
                    "task_classification",
                    {"text": f"classify this document: {stem}\n{content[:FILE_READ_LIMIT_CHARS]}"},
                )
            )

        return tasks

    def _read_file_snippet(self, fp: Path, max_chars: int = FILE_READ_LIMIT_CHARS) -> str:
        """读取文件前 N 个字符作为任务输入。"""
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")
            return content[:max_chars]
        except Exception:
            return ""

    @staticmethod
    def _file_hash(fp: Path) -> str:
        """文件路径 + mtime 哈希，用于去重。"""
        try:
            stat = fp.stat()
            raw = f"{fp.as_posix()}:{stat.st_mtime}:{stat.st_size}"
        except OSError:
            raw = fp.as_posix()
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ============================================================================
# P3 生成器自动触发接入——boot_hooks 任务状态事件轨
# ============================================================================

# 模块级调度器引用——由 AutoRuntimeCore/PipelineOrchestrator 启动时通过 set_scheduler() 注入。
# 设计理由：LocalModelScheduler 无 singleton，实例由上层组件持有；
# 模块级引用避免 singleton 模式，同时让事件回调可获取调度器实例。
_scheduler_ref: Any = None
_subscribed = False


def set_scheduler(scheduler: LocalModelScheduler | None) -> None:
    """注入 LocalModelScheduler 实例（由 AutoRuntimeCore/PipelineOrchestrator 启动时调用）。

    AutoTaskGenerator.generate_and_submit 需要 scheduler.enqueue(task_id, capability, payload)
    接口。LocalModelScheduler 实例由上层组件创建并持有，本函数让事件回调可获取该实例。

    Args:
        scheduler: LocalModelScheduler 实例（需有 enqueue 方法）。
    """
    global _scheduler_ref
    _scheduler_ref = scheduler
    _log.info("AutoTaskGenerator: scheduler injected (%s)", type(scheduler).__name__)


def subscribe_eventbus() -> None:
    """订阅 task_completed 事件——任务完成后自动生成新任务填满队列。

    boot_hooks 的 _subscribe_eventbus_consumers() 统一调用本函数。
    幂等：重复调用不会重复订阅（_subscribed 标志位）。

    事件轨选择（P3 生成器触发接入）：
    - 接入 boot_hooks 任务状态事件轨（EventBusBackpressure topic-based）
    - 触发条件：task_completed 事件到达（任务 COMPLETED 队列空闲时）
    - 回调行为：若有 scheduler 实例，调用 generate_and_submit 生成新任务；
      若无 scheduler（系统未启动），仅日志记录（与 autopilot 模式一致）
    """
    global _subscribed
    if _subscribed:
        return
    try:
        from zephyr.shared.event_bus import EventBusBackpressure

        bus = EventBusBackpressure()
        bus.subscribe("task_completed", _on_task_completed)
        _subscribed = True
        _log.info("AutoTaskGenerator: subscribed to task_completed event")
    except Exception as e:
        _log.warning("AutoTaskGenerator: subscribe_eventbus failed: %s", e, exc_info=True)


def _on_task_completed(payload: object) -> None:
    """task_completed 事件回调——任务完成后自动生成新任务。

    payload 期望字段: {timestamp, source_function, severity, detail}
    若 scheduler 未注入（系统未启动），仅日志记录（与 autopilot 模式一致）。
    """
    try:
        if _scheduler_ref is None:
            _log.debug("AutoTaskGenerator: no scheduler injected, skip task generation")
            return

        from zephyr.shared.io.paths import REPO_ROOT
        generator = AutoTaskGenerator(project_root=REPO_ROOT)
        submitted = generator.generate_and_submit(_scheduler_ref)
        if submitted > 0:
            _log.info("AutoTaskGenerator: submitted %d tasks after task_completed", submitted)
    except Exception as exc:
        _log.debug("AutoTaskGenerator: _on_task_completed failed: %s", exc, exc_info=True)
