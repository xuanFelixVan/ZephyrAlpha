# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.windows_service
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_windows_service | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
WindowsService — Windows Service 包装器
=========================================
蓝图: ARC-0001 §6.1

注册方式:
  sc create ZephyrAlpha binPath= "python -m zephyr.trading"
  sc config ZephyrAlpha start= auto

卸载:
  sc delete ZephyrAlpha
"""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def install_service() -> None:
    import subprocess

    python_exe = sys.executable
    bin_path = f'"{python_exe}" -m zephyr.trading'
    subprocess.run(
        ["sc", "create", "ZephyrAlpha", f"binPath={bin_path}"],
        check=True,
    )
    subprocess.run(
        ["sc", "config", "ZephyrAlpha", "start=auto"],
        check=True,
    )
    # 5.170.6 修复: 库代码 CLI 入口 print -> logger.info
    logger.info("ZephyrAlpha Windows Service installed and set to auto-start.")


def uninstall_service() -> None:
    import subprocess

    subprocess.run(["sc", "delete", "ZephyrAlpha"], check=True)
    # 5.170.7 修复: 库代码 CLI 入口 print -> logger.info
    logger.info("ZephyrAlpha Windows Service uninstalled.")


def run_as_service() -> None:
    try:
        import win32event
        import win32service
        import win32serviceutil
    except ImportError:
        # 5.170.8 修复: 缺失依赖错误 print -> logger.error
        logger.error("pywin32 not installed. Run: pip install pywin32")
        # 5.170.9 修复: 降级提示 print -> logger.warning
        logger.warning("Falling back to console mode...")
        from zephyr.trading.__main__ import main

        main()
        return

    class _ZephyrAlphaService(win32serviceutil.ServiceFramework):
        _svc_name_ = "ZephyrAlpha"
        _svc_display_name_ = "ZephyrAlpha AutoRuntime Core"
        _svc_description_ = "Three-layer AI runtime orchestration brain"

        def __init__(self, args: tuple[str, ...]) -> None:
            super().__init__(args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        def SvcStop(self) -> None:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)

        def SvcDoRun(self) -> None:
            from zephyr.trading.auto_runtime_core import AutoRuntimeCore
            from zephyr.trading.runtime_config import RuntimeConfig

            config = RuntimeConfig()
            core = AutoRuntimeCore(config)
            core.boot()

            while True:
                rc = win32event.WaitForSingleObject(self.hWaitStop, int(config.poll_interval * 1000))
                if rc == win32event.WAIT_OBJECT_0:
                    break
                core.reconcile()

            core.shutdown()

    win32serviceutil.HandleCommandLine(_ZephyrAlphaService)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            install_service()
        elif sys.argv[1] == "uninstall":
            uninstall_service()
        else:
            run_as_service()
    else:
        run_as_service()
