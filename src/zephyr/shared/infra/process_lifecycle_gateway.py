# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §2.10
# [MODULE] zephyr.shared.infra.process_lifecycle_gateway
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.lifecycle.daemon_registry; zephyr.shared.infra.process_pool
# [CONSUMERS] zephyr.trading.auto_runtime_core (ollama serve) ; scripts.mcp.launcher (MCP Server DAG)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 所有子进程创建必须经过此网关；所有池化进程必须在 DaemonRegistry 中注册；idle_timeout_s 后必须被回收；Gateway 不持有业务逻辑
# [MODIFY-GUARD] ProcessPool 和 DaemonRegistry 的接口变更必须同步更新此网关
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] launch 返回 None 表示启动失败（调用方处理）；launch_daemon 返回 bool 表示成功/失败
# [TESTS] tests/zephyr/shared/infra/test_process_lifecycle_gateway.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ProcessLifecycleGateway — 进程生命周期统一入口
=================================================

SSoT: MOD-INF-016 §2.10 | DEP-GRAPH-process-lifecycle-001

强制入口: 所有 subprocess.Popen / multiprocessing.Process 必须经过此网关。
Gateway 组合 MCPProcessPool + DaemonRegistry，提供:
  - launch(): 启动普通子进程（通过 ProcessPool）
  - launch_daemon(): 启动 daemon 进程（通过 ProcessPool + DaemonRegistry 注册）
  - terminate_all(): 关闭所有池中进程

设计根因: 裸 Popen/Process 绕过 MCPProcessPool -> 进程泄漏 -> 统一入口 + Gate 防绕过。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: idle_timeout_s 参数
#   fields: 参数 idle_timeout_s（无注解）
#   code: process_lifecycle_gateway.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ProcessLifecycleGateway
#   name_en: ProcessLifecycleGateway
#   intro: 进程生命周期统一入口。
#   desc: 进程生命周期统一入口。 组合 MCPProcessPool（进程创建/复用/僵尸/超时）和 DaemonRegistry（注册/监控/降级）。 不持有业务逻辑，纯路由 + 生命周…；公共方法（定义序）: pool, l…
#   inputs: idle_timeout_s
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ProcessLifecycleGateway
#   downstream: zephyr.trading.auto_runtime_core (ollama serve) ; scripts.mcp.launcher (MCP Ser…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging

from zephyr.shared.infra.process_pool import MCPProcessPool, PooledProcess
from zephyr.shared.lifecycle.daemon_registry import DaemonRegistry

__all__ = ["ProcessLifecycleGateway"]

logger = logging.getLogger(__name__)


class ProcessLifecycleGateway:
    """进程生命周期统一入口。

    组合 MCPProcessPool（进程创建/复用/僵尸/超时）和 DaemonRegistry（注册/监控/降级）。
    不持有业务逻辑，纯路由 + 生命周期管理。

    idle_timeout_s: 池级别默认空闲超时（秒），超时后自动回收。默认 600s。
    """

    def __init__(self, idle_timeout_s: float = 600.0) -> None:
        self._pool = MCPProcessPool(idle_timeout_s=idle_timeout_s)
        self.pool.start_zombie_scanner()

    # ----- Stage 4 公共化：属性 getter/setter -----
    @property
    def pool(self) -> MCPProcessPool:
        """Stage 4 公共化。"""
        return self._pool

    @pool.setter
    def pool(self, value: MCPProcessPool) -> None:
        self._pool = value

    def launch(
        self,
        name: str,
        cmd: list[str],
        idle_timeout_s: float = 600.0,
        priority: int = 3,
    ) -> PooledProcess | None:
        """启动普通子进程（通过 ProcessPool + DaemonRegistry 注册）。

        Args:
            name: 进程名（池中唯一标识）
            cmd: 命令行参数列表
            idle_timeout_s: 空闲超时（秒），超时后自动回收。默认 600s (10分钟)
            priority: DaemonRegistry 优先级（压力降级使用）。默认 3

        Returns:
            PooledProcess 如果启动成功，None 如果失败
        """
        entry = self.pool.get_or_create(name, cmd)
        if entry is None:
            logger.error("ProcessLifecycleGateway: launch('%s') failed", name)
            return None

        try:
            daemon_name = f"gateway:{name}"
            DaemonRegistry.register(
                daemon_name,
                start_fn=lambda n=name: self.pool.get_or_create(n),
                stop_fn=lambda n=name: self.pool.terminate(n),
                priority=priority,
            )
            logger.info(
                "ProcessLifecycleGateway: launched '%s' (pid=%d, idle_timeout=%ds)",
                name,
                entry.pid,
                idle_timeout_s,
            )
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.exception("ProcessLifecycleGateway: DaemonRegistry.register failed for '%s'", name, exc_info=True)

        return entry

    def launch_daemon(
        self,
        name: str,
        cmd: list[str],
        idle_timeout_s: float = 600.0,
        priority: int = 3,
    ) -> bool:
        """启动 daemon 进程并注册到 DaemonRegistry。

        Args:
            name: 进程名
            cmd: 命令行参数列表
            idle_timeout_s: 空闲超时（秒）。默认 600s
            priority: DaemonRegistry 优先级。默认 3

        Returns:
            True 如果启动成功，False 如果失败
        """
        entry = self.launch(name, cmd, idle_timeout_s=idle_timeout_s, priority=priority)
        if entry is None:
            return False

        try:
            DaemonRegistry.start(f"gateway:{name}")
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.exception(
                "ProcessLifecycleGateway: DaemonRegistry.start failed for 'gateway:%s'", name, exc_info=True
            )
        return True

    def terminate(self, name: str) -> bool:
        """终止指定进程。同时停止 DaemonRegistry 中的注册。"""
        daemon_name = f"gateway:{name}"
        try:
            DaemonRegistry.stop(daemon_name)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("suppressed error in process_lifecycle_gateway", exc_info=True)
        return self.pool.terminate(name)

    def terminate_all(self) -> int:
        """终止所有池中进程。

        Returns:
            已终止的进程数
        """
        count = self.pool.terminate_all()
        logger.info("ProcessLifecycleGateway: terminated_all — %d processes", count)
        return count

    def get_stats(self):
        """获取进程池统计信息。"""
        return self.pool.get_stats()

    def shutdown(self) -> None:
        """优雅关闭：终止所有进程 + 停止僵尸扫描。"""
        self.pool.stop_zombie_scanner()
        self.terminate_all()
        logger.info("ProcessLifecycleGateway: shutdown complete")
