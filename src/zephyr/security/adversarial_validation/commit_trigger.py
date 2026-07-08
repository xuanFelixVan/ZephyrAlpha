# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §67
# [MODULE] zephyr.security.adversarial_validation.commit_trigger
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.validator; zephyr.security.adversarial_validation.circuit_breaker; zephyr.security.adversarial_validation.models
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway; zephyr.trading.boot_hooks
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] detect_formal_files MUST be ms-cost (no YAML/import); write_trigger_record MUST be atomic; consumer thread MUST fail-closed on gate
# [MODIFY-GUARD] formal header regex per project_memory 红蓝触发条件; poll interval MUST NOT < 10s
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] detect_formal_files swallows OSError; consumer thread swallows all + logs; CircuitBreakerOpenError->skip+retry
# [TESTS] tests/red_blue/test_commit_trigger.py
# [A_module] module_id=MOD-SEC_commit_trigger | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CommitTrigger — 事件驱动红蓝对抗触发器 (MOD-INF-030).

将 GitCommitGateway 的 post-commit 事件桥接到 RedBlueValidator，触发提交后的
对抗验证会话（TIER_1 全量）。

设计要点（对齐 .trae/documents/event_driven_red_blue_trigger_plan.md）:
  - **锁内轻量 emit**：detect_formal_files + write_trigger_record 毫秒级，
    不跑对抗、不调 SteadyState、不调 cleanup（避免破坏性 unlink 阻塞 commit 锁）。
  - **文件队列异步媒介**：不用 EventBusBackpressure（其 emit 同步派发 handler，
    在 commit 锁内会阻塞全局 commit 锁 TTL=1800s）。改用持久 JSON 队列文件。
  - **消费线程锁外执行**：RedBlueTriggerConsumer daemon 线程轮询队列，门禁达标时
    跑 TIER_1 对抗，受 CircuitBreaker 频率保护。
  - **就位 + 门禁激活**：钩子代码始终就位（emit 总发生）；门禁 env var
    ZEPHYR_RED_BLUE_AUTO_ENABLED=1 时才实跑，否则只 log + 清队列（fail-closed）。
  - **唯一触发路径**：CircadianScheduler 定时调度已废除（2026-06-26），
    本模块是红蓝对抗的唯一触发入口，由 GitCommitGateway post-commit 事件驱动。

用法:
    # 锁内（GitCommitGateway post-commit 钩子）:
    from zephyr.security.adversarial_validation.commit_trigger import (
        detect_formal_files, write_trigger_record,
    )
    formal = detect_formal_files(files)
    if formal:
        write_trigger_record(commit_hash, session_id, formal)

    # 锁外（boot_hooks 启动消费线程）:
    from zephyr.security.adversarial_validation.commit_trigger import RedBlueTriggerConsumer
    RedBlueTriggerConsumer().start()
"""

from __future__ import annotations

from typing import Final
import json
import logging
import os
import re
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

__all__: list[str] = [
    "detect_formal_files",
    "write_trigger_record",
    "RedBlueTriggerConsumer",
    "FORMAL_HEADER_RE",
]

# ── 路径（绝对路径，对齐 project_memory 硬约束）──────────────────────────
# REPO_ROOT 由 zephyr.shared.io.paths 提供（SSoT）
_QUEUE_DIR: Path = REPO_ROOT / "data" / "red_blue" / "trigger_queue"

# ── 正式文件头部标记（对齐 project_memory 红蓝对抗触发条件）──────────────
# 命中 `# [BLUEPRINT]` 或 `# [MODULE]`（方括号格式）。
# 注意：`# blueprint:`（无方括号）不匹配——registry YAML 头部不会误触发。
FORMAL_HEADER_RE: Final[re.Pattern[str]] = re.compile(r"^#\s*\[(BLUEPRINT|MODULE)\]")
_HEADER_SCAN_LINES: int = 5  # 只扫前 5 行，毫秒级

# ── 门禁 env var（fail-closed：默认关，操作者达标后手动设 1）─────────────
_GATE_ENV: str = "ZEPHYR_RED_BLUE_AUTO_ENABLED"


# ── 锁内轻量函数（毫秒级，GitCommitGateway 持锁调用）────────────────────


def detect_formal_files(files: list[str]) -> list[str]:
    """扫描提交文件前几行是否含 [BLUEPRINT]/[MODULE] 头部标记。

    毫秒级（无 YAML 解析、无 import）。script_manifest.yaml 精确交叉校验
    留到消费阶段（锁外），保持锁内临界路径最短。

    Args:
        files: GitCommitGateway commit() 的 files 形参（相对或绝对路径）。

    Returns:
        命中头部标记的文件路径列表（空则不触发）。
    """
    formal: list[str] = []
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="ignore") as fh:
                for i, line in enumerate(fh):
                    if i >= _HEADER_SCAN_LINES:
                        break
                    if FORMAL_HEADER_RE.match(line):
                        formal.append(f)
                        break
        except OSError:
            # 文件不存在/不可读——跳过（可能是已删除文件等）
            continue
    return formal


def write_trigger_record(
    commit_hash: str,
    session_id: str,
    formal_files: list[str],
    queue_dir: Path | None = None,
) -> Path:
    """原子写一个触发记录到队列目录（锁内调用，毫秒级）。

    对齐 manage_baseline._atomic_write 模式：写 .tmp 后 os.replace 原子替换，
    避免消费线程读到半截 JSON。

    Args:
        commit_hash: commit SHA。
        session_id: GitCommitGateway session 标识。
        formal_files: detect_formal_files 命中的文件列表。
        queue_dir: 测试注入；默认 _QUEUE_DIR。

    Returns:
        写入的队列文件绝对路径。
    """
    target_dir = queue_dir if queue_dir is not None else _QUEUE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    record = {
        "commit_hash": commit_hash,
        "session_id": session_id,
        "formal_files": formal_files,
        "emitted_at": datetime.now(UTC).isoformat(),
    }
    final = target_dir / f"{ts}_{commit_hash[:8]}.json"
    tmp = final.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, final)
    logger.info(
        "commit_trigger: record written hash=%s formal=%d -> %s",
        commit_hash[:8], len(formal_files), final.name,
    )
    return final


# ── 锁外消费线程（RedBlueTriggerConsumer）──────────────────────────────


class RedBlueTriggerConsumer:
    """守护线程：轮询 trigger_queue，门禁达标时跑 TIER_1 对抗验证。

    就位 + 门禁激活:
      - 始终轮询（就位：即使门禁未达标，钩子仍会 emit 记录到此队列）。
      - ZEPHYR_RED_BLUE_AUTO_ENABLED != "1" 时：log + 删队列文件（不累积，
        留可见性，fail-closed）。
      - == "1" 时：CircuitBreaker.before_run -> 跑 TIER_1 全量 14 场景
        -> after_run -> 删队列文件。

    频率保护:
      CircuitBreaker（模块级单例）防 commit 风暴烧 LLM 预算。OPEN 态
      before_run 抛 CircuitBreakerOpenError -> 跳过本条、留队列 cool-down
      30s 后 HALF_OPEN 重试。
    """

    POLL_INTERVAL_S: int = 30  # 对齐 [MODIFY-GUARD] poll interval MUST NOT < 10s

    def __init__(self, queue_dir: Path | None = None) -> None:
        self._queue_dir: Path = queue_dir if queue_dir is not None else _QUEUE_DIR
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        # 懒加载，避免 __init__ 触发重 import 链
        self._circuit = None  # type: ignore[assignment]
        self._validator = None  # type: ignore[assignment]

    # ── 生命周期 ──────────────────────────────────────────────────────
    def start(self) -> None:
        """幂等启动 daemon 线程。"""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop,
            daemon=True,
            name="RedBlueTriggerConsumer",
        )
        self._thread.start()
        logger.info("RedBlueTriggerConsumer: started (poll=%ds)", self.POLL_INTERVAL_S)

    def stop(self, timeout: float = 5.0) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
        logger.info("RedBlueTriggerConsumer: stopped")

    # ── 主循环 ────────────────────────────────────────────────────────
    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._drain_queue()
            except Exception as e:  # noqa: BLE001 — 消费线程永不退出
                logger.warning("RedBlueTriggerConsumer: drain failed: %s", e, exc_info=True)
            self._stop.wait(self.POLL_INTERVAL_S)

    def _drain_queue(self) -> None:
        if not self._queue_dir.exists():
            return
        for qf in sorted(self._queue_dir.glob("*.json")):
            if self._stop.is_set():
                break
            try:
                self._process_one(qf)
            except Exception as e:  # noqa: BLE001 — 单条失败不影响其他
                logger.warning(
                    "RedBlueTriggerConsumer: process %s failed: %s", qf.name, e, exc_info=True
                )

    def _process_one(self, qf: Path) -> None:
        record = json.loads(qf.read_text(encoding="utf-8"))
        commit_hash = record.get("commit_hash", "?")
        formal_files = record.get("formal_files", [])
        hash8 = commit_hash[:8] if isinstance(commit_hash, str) else "?"

        # 门禁检查（fail-closed：默认关）
        if os.environ.get(_GATE_ENV, "0") != "1":
            logger.info(
                "RedBlueTriggerConsumer: trigger seen but gate closed "
                "(hash=%s formal=%d) — 就位记录，不实跑",
                hash8, len(formal_files),
            )
            qf.unlink(missing_ok=True)  # 不累积，留 log 可见性
            return

        # CircuitBreaker 频率保护
        circuit = self._get_circuit()
        try:
            circuit.before_run()
        except Exception as e:  # CircuitBreakerOpenError
            logger.warning(
                "RedBlueTriggerConsumer: circuit open, skip (hash=%s): %s — 留队列重试",
                hash8, e, exc_info=True
            )
            return  # 不删队列文件，cool-down 后重试

        # 跑 TIER_1 全量
        validator = self._get_validator()
        if validator is None:
            logger.warning(
                "RedBlueTriggerConsumer: validator unavailable, drop (hash=%s)", hash8
            )
            qf.unlink(missing_ok=True)
            return

        from zephyr.security.adversarial_validation.models import (
            AttackTier,
            BlastRadiusLevel,
        )

        report = validator.run_adversarial_session(
            session_name=f"commit_{hash8}",
            tier=AttackTier.TIER_1,
            blast_radius=BlastRadiusLevel.FILE,
        )
        circuit.after_run(report)
        logger.info(
            "RedBlueTriggerConsumer: TIER_1 done (hash=%s blocked=%d bypassed=%d total=%d)",
            hash8,
            getattr(report, "blocked", 0),
            getattr(report, "bypassed", 0),
            getattr(report, "total_scenarios", 0)
            or getattr(report, "total", 0),
        )
        qf.unlink(missing_ok=True)

    # ── 懒加载 ────────────────────────────────────────────────────────
    def _get_circuit(self):
        if self._circuit is None:
            from zephyr.security.adversarial_validation.circuit_breaker import (
                CircuitBreaker,
            )

            self._circuit = CircuitBreaker()
        return self._circuit

    def _get_validator(self):
        if self._validator is None:
            try:
                from zephyr.security.adversarial_validation.validator import (
                    RedBlueValidator,
                )

                self._validator = RedBlueValidator()
            except Exception as e:  # noqa: BLE001
                logger.warning("RedBlueTriggerConsumer: validator init failed: %s", e, exc_info=True)
                return None
        return self._validator
