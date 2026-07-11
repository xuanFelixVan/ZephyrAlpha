# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.degradation
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/code_dedup_engine/test_degradation_edge.py; tests/governance/budget/test_degradation.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_degradation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""降级运行管理器 — 各 Stage 独立 try/except + degradation_level + exit code.

职责：
  - 每个 Stage 独立 try/except，失败时降级而非崩溃
  - degradation_level 记录降级原因
  - 降级日志记录到 Session Log + 报告
  - exit code 约定：0=无重复 / 1=WARN / 2=ERROR / 3=工具故障 / 4=DEGRADED
"""

from __future__ import annotations

import logging
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntEnum
from typing import Any

logger = logging.getLogger(__name__)


class ExitCode(IntEnum):
    CLEAN = 0
    WARN = 1
    ERROR = 2
    FAULT = 3
    DEGRADED = 4


class DegradationLevel:
    NONE = "none"
    NO_CACHE = "no_cache"
    STAGE05_ONLY = "stage0.5_only"
    STAGE1_ONLY = "stage1_only"
    NO_AST = "no_ast"
    NO_LLM = "no_llm"


@dataclass
class StageResult:
    stage: str
    success: bool
    error: str = ""
    duration_ms: float = 0.0
    output: object = None


@dataclass
class DegradationReport:
    level: str = DegradationLevel.NONE
    stages: list[StageResult] = field(default_factory=list)
    exit_code: int = ExitCode.CLEAN
    started_at: str = ""
    finished_at: str = ""
    total_duration_ms: float = 0.0


class DegradationManager:
    """降级运行管理器."""

    def __init__(self) -> None:
        self._report = DegradationReport()
        self._degradation_log: list[dict[str, str]] = []

    # ── 公共 API ──────────────────────────────────────────────

    def run_stage(
        self,
        stage_name: str,
        func: Callable[[], Any],
        on_degrade: str | None = None,
    ) -> StageResult:
        """执行单个 Stage——独立 try/except + 降级处理."""
        stage = StageResult(stage=stage_name, success=False)
        started = datetime.now(UTC)

        try:
            output = func()
            stage.success = True
            stage.output = output
        except Exception as exc:
            stage.error = f"{type(exc).__name__}: {exc}"
            self._log_degradation(stage_name, str(exc))
            if on_degrade:
                self._report.level = on_degrade
        finally:
            stage.duration_ms = (datetime.now(UTC) - started).total_seconds() * 1000

        self._report.stages.append(stage)
        return stage

    def run_pipeline(self, stages: list[tuple[str, Callable[[], Any], str | None]]) -> DegradationReport:
        """运行完整流水线——按顺序执行所有 Stage."""
        self._report = DegradationReport(
            started_at=datetime.now(UTC).isoformat(),
        )

        all_started = datetime.now(UTC)
        for name, func, on_degrade in stages:
            self.run_stage(name, func, on_degrade)

        self._report.total_duration_ms = (datetime.now(UTC) - all_started).total_seconds() * 1000
        self._report.finished_at = datetime.now(UTC).isoformat()
        self._report.exit_code = self._compute_exit_code()

        return self._report

    def get_report(self) -> DegradationReport:
        return self._report

    def get_degradation_log(self) -> list[dict[str, str]]:
        return self._degradation_log

    # ── 内部方法 ─────────────────────────────────────────────

    def _log_degradation(self, stage: str, error: str) -> None:
        self._degradation_log.append(
            {
                "stage": stage,
                "error": error,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        logger.warning(
            "Stage %s degraded: %s\n%s",
            stage,
            error,
            traceback.format_exc()[:500],
        )

    def _compute_exit_code(self) -> int:
        """根据降级级别确定 exit code."""
        if self._report.level == DegradationLevel.NONE:
            return ExitCode.CLEAN
        return ExitCode.DEGRADED
