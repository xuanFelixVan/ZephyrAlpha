"""auto_bootstrap — 全自动遥测注入钩子（MOD-INF-015 v0.9.0）

触发时机 —— 零手动代码，完全自动：
    zephyr 包被 import → auto_bootstrap 执行 → 全局 Telemetry 单例创建
    SessionContinuity 初始化 → print_restore_summary 被 monkey-patch → 自动发送 session_start 事件
    Phase Manager 运行检查 → PHASE_SEQUENCE 访问被拦截 → 自动发送 gate_check 事件

对标: K8s admission webhook — 注入 sidecar 无需应用感知
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

_logger = logging.getLogger(__name__)

_global_telemetry: Any = None
_bootstrap_time: str = ""


def get_global_telemetry():
    """获取全局 Telemetry 单例（惰性创建，避免循环 import）"""
    global _global_telemetry
    if _global_telemetry is None:
        from zephyr.l12_system_telemetry.facade import Telemetry
        _global_telemetry = Telemetry(
            module_id="zephyr_core",
            environment="auto",
            test_mode=False,
        )
        _global_telemetry.metrics.counter("telemetry.bootstrap")
        _logger.info("Auto-telemetry bootstrapped")
    return _global_telemetry


def _patch_session_continuity():
    """Monkey-patch SessionContinuity.print_restore_summary → 自动发送 session_start 遥测"""
    try:
        from zephyr.core.session_continuity import SessionContinuity
        _orig_restore = SessionContinuity.print_restore_summary

        def _wrapped_restore(self, *args, **kwargs):
            t0 = time.time()
            telemetry = get_global_telemetry()
            telemetry.metrics.counter("session.start")
            telemetry.logs.info("session_restore_begin")
            result = _orig_restore(self, *args, **kwargs)
            elapsed = time.time() - t0
            telemetry.metrics.gauge("session.restore_elapsed_ms", elapsed * 1000)
            telemetry.logs.info("session_restore_complete", elapsed_ms=round(elapsed * 1000))
            return result

        SessionContinuity.print_restore_summary = _wrapped_restore
        _logger.info("auto_telemetry: patched SessionContinuity.print_restore_summary")
    except Exception:
        _logger.debug("auto_telemetry: SessionContinuity patch skipped", exc_info=True)


def _patch_phase_manager():
    """Monkey-patch PhaseGate.run_checks → 每次 gate check 自动发送遥测"""
    try:
        from zephyr.governance.phase_manager import PhaseGate

        _orig_run_checks = PhaseGate.run_checks

        def _wrapped_run_checks(self, *args, **kwargs):
            telemetry = get_global_telemetry()
            phase_name = str(self.phase.value) if hasattr(self, "phase") else "unknown"
            check_count = len(self.gate_checks) if hasattr(self, "gate_checks") else 0
            t0 = time.time()
            telemetry.logs.info("phase_check_begin", phase=phase_name, check_count=check_count)
            result = _orig_run_checks(self, *args, **kwargs)
            elapsed = time.time() - t0
            telemetry.metrics.gauge(f"phase.{phase_name}.elapsed_ms", elapsed * 1000)
            telemetry.metrics.counter(f"phase.{phase_name}.complete")
            telemetry.logs.info(
                "phase_check_complete",
                phase=phase_name,
                elapsed_ms=round(elapsed * 1000),
                result=str(result),
            )
            return result

        PhaseGate.run_checks = _wrapped_run_checks
        _logger.info("auto_telemetry: patched PhaseGate.run_checks")
    except Exception:
        _logger.debug("auto_telemetry: PhaseManager patch skipped", exc_info=True)


def _patch_blueprint_metrics():
    """注入 export 钩子到 blueprint_metrics → 每次蓝图读取自动入遥测"""
    try:
        from zephyr.l12_system_telemetry.metrics import blueprint_metrics as bm

        _orig_record = bm.record_blueprint_read

        def _wrapped_record(blueprint_id: str, session_id: str = "", task_id: str = "", **kwargs):
            telemetry = get_global_telemetry()
            telemetry.metrics.counter("blueprint.read", blueprint_id=blueprint_id)
            telemetry.ai_behavior.record(
                decision="blueprint_read",
                model="",
                reason=blueprint_id,
                session_id=session_id,
                task_id=task_id,
            )
            return _orig_record(blueprint_id, session_id=session_id, task_id=task_id, **kwargs)

        bm.record_blueprint_read = _wrapped_record
        _logger.info("auto_telemetry: patched blueprint_metrics.record_blueprint_read")
    except Exception:
        _logger.debug("auto_telemetry: blueprint_metrics patch skipped", exc_info=True)


def bootstrap() -> dict:
    """执行全自动遥测注入。

    调用方: zephyr/__init__.py（包加载末尾自动执行）
    返回: bootstrap 状态摘要
    """
    global _bootstrap_time
    _bootstrap_time = datetime.now(timezone.utc).isoformat()

    results = {
        "ts": _bootstrap_time,
        "session_continuity": False,
        "phase_manager": False,
        "blueprint_metrics": False,
    }

    _patch_session_continuity()
    results["session_continuity"] = True

    _patch_phase_manager()
    results["phase_manager"] = True

    _patch_blueprint_metrics()
    results["blueprint_metrics"] = True

    if not _bootstrap_time:
        _bootstrap_time = datetime.now(timezone.utc).isoformat()

    _logger.info(
        "auto_telemetry bootstrap complete: %s",
        json.dumps(results, default=str),
    )
    return results
