# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.auto_bootstrap
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.shared.session_continuity; zephyr.governance.__init__
# [CONSUMERS] zephyr.trading; zephyr.autonomy_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] lazy singleton creation; monkey-patch must be reversible; zero manual code required; register_module thread-safe
# [MODIFY-GUARD] facade.py; __init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError; RuntimeError
# [TESTS] tests/system-telemetry/test_auto_bootstrap.py
# [A_module] module_id=MOD-INF_auto_bootstrap | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""auto_bootstrap — 全自动遥测注入钩子（MOD-INF-015 v2.1.0）

触发时机 —— 零手动代码，完全自动：
    zephyr 包被 import → auto_bootstrap 执行 → 全局 Telemetry 单例创建
    SessionContinuity 初始化 → print_restore_summary 被 monkey-patch → 自动发送 session_start 事件
    Phase Manager 运行检查 → PHASE_SEQUENCE 访问被拦截 → 自动发送 gate_check 事件

模块自动注册 —— 零代码接入：
    from zephyr.infrastructure.system_telemetry.auto_bootstrap import register_module
    t = register_module("MOD-INF-XXX")  # 首次创建，后续返回同一实例
    # 或更简单：任何模块 import zephyr 后自动获得全局单例
"""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.infrastructure.system_telemetry.facade import Telemetry

_logger = logging.getLogger(__name__)

_global_telemetry: Telemetry | None = None
_bootstrap_time: str = ""
_module_registry: dict[str, Any] = {}
_registry_lock = threading.Lock()


def register_module(module_id: str, environment: str = "dev") -> Any:
    """自动注册模块到全局 Telemetry（线程安全，幂等）。

    首次调用创建 Telemetry 实例并注册，后续调用返回同一实例。
    自动发送 module.registered 事件。
    """
    with _registry_lock:
        if module_id in _module_registry:
            return _module_registry[module_id]
        from zephyr.infrastructure.system_telemetry.facade import Telemetry

        t = Telemetry(module_id=module_id, environment=environment, test_mode=False)
        t.metrics.counter("module.registered", module_id=module_id)
        t.logs.info("module_auto_registered", module_id=module_id, environment=environment)
        t.health.register()
        try:
            from zephyr.infrastructure.system_telemetry.contract_metrics import get_contract_metrics

            get_contract_metrics().enable()
        except Exception:
            _logger.debug("auto_telemetry: contract_metrics enable skipped", exc_info=True)
        _module_registry[module_id] = t
        _logger.info("auto_telemetry: module registered module_id=%s", module_id)
        return t


def get_registered_modules() -> list[str]:
    """返回所有已自动注册的模块 ID 列表。"""
    with _registry_lock:
        return list(_module_registry.keys())


def get_global_telemetry():
    """获取全局 Telemetry 单例（惰性创建，避免循环 import）"""
    global _global_telemetry
    if _global_telemetry is None:
        from zephyr.infrastructure.system_telemetry.facade import Telemetry

        _global_telemetry = Telemetry(
            module_id="zephyr_core",
            environment="auto",
            test_mode=False,
        )
        _global_telemetry.metrics.counter("telemetry.bootstrap")
        _logger.info("Auto-telemetry bootstrapped")
    return _global_telemetry


def _patch_session_continuity() -> bool:
    """Monkey-patch SessionContinuity.print_restore_summary → 自动发送 session_start 遥测"""
    try:
        from zephyr.shared.session.session_continuity import SessionContinuity

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
        return True
    except Exception:
        _logger.warning("auto_telemetry: SessionContinuity patch failed", exc_info=True)
        return False


def _patch_phase_manager() -> bool:
    """Monkey-patch PhaseGate.run_checks → 每次 gate check 自动发送遥测"""
    try:
        from zephyr.governance.ops_governance.phase_manager import PhaseGate

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
        return True
    except Exception:
        _logger.warning("auto_telemetry: PhaseManager patch failed", exc_info=True)
        return False


def _patch_blueprint_metrics() -> bool:
    """注入 export 钩子到 blueprint_metrics → 每次蓝图读取自动入遥测"""
    try:
        from zephyr.infrastructure.system_telemetry.metrics import blueprint_metrics as bm

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
        return True
    except Exception:
        _logger.warning("auto_telemetry: blueprint_metrics patch failed", exc_info=True)
        return False


def bootstrap() -> dict:
    """执行全自动遥测注入。

    调用方: zephyr/__init__.py（包加载末尾自动执行）
    返回: bootstrap 状态摘要
    """
    global _bootstrap_time
    _bootstrap_time = datetime.now(UTC).isoformat()

    results = {
        "ts": _bootstrap_time,
        "session_continuity": False,
        "phase_manager": False,
        "blueprint_metrics": False,
    }

    results["session_continuity"] = _patch_session_continuity()

    results["phase_manager"] = _patch_phase_manager()

    results["blueprint_metrics"] = _patch_blueprint_metrics()

    if not _bootstrap_time:
        _bootstrap_time = datetime.now(UTC).isoformat()

    _logger.info(
        "auto_telemetry bootstrap complete: %s",
        json.dumps(results, default=str),
    )
    return results


from zephyr.infrastructure.system_telemetry._budget_telemetry_bridge import set_telemetry_getter

set_telemetry_getter(get_global_telemetry)
