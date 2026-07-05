# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | CT-ORC-SCRIPT-001
# [MODULE] zephyr.trading.orchestrator.execution.script_runner
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] zephyr.trading.orchestrator.agent_orchestrator; AutoRuntime Core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] ThreadPoolExecutor并行执行; 每个脚本exit code独立采集; 超时60s/script
# [MODIFY-GUARD] CT-ORC-SCRIPT-001 脚本执行协议变更必须同步更新CLI+contract
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 脚本路径不存在返回RunResult(error=FILE_NOT_FOUND); 超时返回error=TIMEOUT
# [TESTS] scripts/connect/orc_script.py --trigger
# [A_module] module_id=MOD-ORC_script_runner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Orc→Script 脚本执行器 — run_audit() 生产者

CT-ORC-SCRIPT-001: Orchestrator 接到审计任务后批量执行审计脚本, 按 RULE-SEVEN 并行。
"""

from __future__ import annotations

import logging
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "RunResult",
    "ScriptResult",
    "ScriptRunner",
    "run_audit",
]


@dataclass
class ScriptResult:
    script: str
    exit_code: int = -1
    output: str = ""
    error: str = ""
    duration_ms: int = 0


@dataclass
class RunResult:
    task_id: str = ""
    results: list[ScriptResult] = field(default_factory=list)
    total_scripts: int = 0
    failed: int = 0
    warnings: int = 0
    passed: int = 0
    total_duration_ms: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "total_scripts": self.total_scripts,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "total_duration_ms": self.total_duration_ms,
            "error": self.error,
            "results": [
                {"script": r.script, "exit_code": r.exit_code, "duration_ms": r.duration_ms} for r in self.results
            ],
        }


class ScriptRunner:
    def run_audit(
        self,
        task_id: str,
        scripts: list[str],
        max_workers: int = 8,
        timeout_per_script: int = 60,
    ) -> RunResult:
        t0 = time.perf_counter()
        result = RunResult(task_id=task_id, total_scripts=len(scripts))

        resolved = self._resolve_scripts(scripts)
        if not resolved:
            result.error = "NO_VALID_SCRIPTS"
            result.total_duration_ms = round((time.perf_counter() - t0) * 1000)
            return result

        with ThreadPoolExecutor(max_workers=min(max_workers, len(resolved))) as executor:
            futures = {
                executor.submit(self._run_one, script_path, timeout_per_script): script_path for script_path in resolved
            }
            for future in as_completed(futures):
                script_result = future.result()
                result.results.append(script_result)
                if script_result.exit_code == 0:
                    result.passed += 1
                elif script_result.exit_code == 2:
                    result.warnings += 1
                else:
                    result.failed += 1

        result.total_duration_ms = round((time.perf_counter() - t0) * 1000)
        logger.info(
            "[ORC-SCRIPT] audit: task=%s total=%d passed=%d failed=%d warn=%d elapsed=%dms",
            task_id,
            len(resolved),
            result.passed,
            result.failed,
            result.warnings,
            result.total_duration_ms,
        )

        self._submit_to_gate(result, task_id)
        self._publish_to_kb(result, task_id)

        return result

    def _run_one(self, script_path: str, timeout: int) -> ScriptResult:
        start = time.perf_counter()
        try:
            proc = subprocess.run(
                [sys.executable, script_path, "--warn-only"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed = round((time.perf_counter() - start) * 1000)
            return ScriptResult(
                script=script_path,
                exit_code=proc.returncode,
                output=proc.stdout[:500],
                error=proc.stderr[:500],
                duration_ms=elapsed,
            )
        except subprocess.TimeoutExpired:
            elapsed = round((time.perf_counter() - start) * 1000)
            return ScriptResult(
                script=script_path,
                exit_code=124,
                error="TIMEOUT",
                duration_ms=elapsed,
            )
        except Exception as exc:
            elapsed = round((time.perf_counter() - start) * 1000)
            return ScriptResult(
                script=script_path,
                exit_code=255,
                error=str(exc)[:500],
                duration_ms=elapsed,
            )

    def _resolve_scripts(self, scripts: list[str]) -> list[str]:
        resolved = []
        for s in scripts:
            p = Path(s)
            if p.exists():
                resolved.append(str(p))
            else:
                alt = Path("scripts") / s
                if alt.exists():
                    resolved.append(str(alt))
                else:
                    logger.warning("[ORC-SCRIPT] script not found: %s", s)
        return resolved

    def _submit_to_gate(self, result: RunResult, task_id: str) -> None:
        try:
            from zephyr.infrastructure.script_system.gate_bridge import submit_to_gate

            findings: list[dict[str, Any]] = []
            for r in result.results:
                dim_map = {"passed": "D1", "failed": "D5", "warnings": "D9"}
                if r.exit_code == 0:
                    dim = "D1"
                elif r.exit_code == 2:
                    dim = "D9"
                else:
                    dim = "D5"
                findings.append(
                    {
                        "dimension": dim,
                        "script": r.script,
                        "exit_code": r.exit_code,
                        "duration_ms": r.duration_ms,
                        "message": r.error or r.output[:200],
                    }
                )
            if findings:
                submit_to_gate(findings, task_id=task_id)
        except Exception:
            logger.debug("[SCRIPT-GATE] submit skipped", exc_info=True)

    def _publish_to_kb(self, result: RunResult, task_id: str) -> None:
        try:
            from zephyr.infrastructure.script_system.kb_bridge import publish_to_kb

            findings: list[dict[str, Any]] = [
                {
                    "dimension": "audit",
                    "script": r.script,
                    "exit_code": r.exit_code,
                    "duration_ms": r.duration_ms,
                    "message": r.error or r.output[:200],
                }
                for r in result.results
            ]
            if findings:
                publish_to_kb(findings, task_id=task_id)
        except Exception:
            logger.debug("[SCRIPT-KB] publish skipped", exc_info=True)


def run_audit(
    task_id: str,
    scripts: list[str],
    max_workers: int = 8,
    timeout_per_script: int = 60,
) -> RunResult:
    return ScriptRunner().run_audit(task_id, scripts, max_workers, timeout_per_script)