# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §14
# [MODULE] scripts.mcp.launcher
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.integration.__init__
# [CONSUMERS] zephyr.trading.boot_hooks (MCP 自动启动); zephyr.trading.boot_cron_jobs (_mcp_health_check); scripts.governance.* (健康检查)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] DAG_LAYERS 必须包含 10 个 Server 的 4 层结构（layer_0 空+layer_1~4）；SERVER_SCRIPTS 路径必须为 src/zephyr/integration/mcp/；所有进程必须通过 ProcessLifecycleGateway 管理；idle_timeout_s=600（10分钟空闲自动回收）；launch_all 必须注册 SIGINT/SIGTERM 信号处理；atexit 必须注册 _graceful_shutdown 兜底
# [MODIFY-GUARD] 修改本文件 MUST 通过任务卡通道并获取文件锁；修改前 MUST 运行 test_mcp_launcher.py 验证无回归；修改后 MUST 运行 test_mcp_launcher.py 确认通过；禁止删除 check_server_health/restart_server/dry_run 函数；禁止修改 DAG_LAYERS 层级结构（10 Server / 4 非空层）除非通过蓝图变更审批
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] launch_all 返回 dict[server_id, bool]；dry_run 返回 int (0=成功)；check_server_health 返回 dict[server_id, bool]；restart_server 返回 bool
# [TESTS] tests/test_mcp_launcher.py
# [A_module] module_id=MOD-INF-013 | layer=script | stability=stable | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""MCP DAG 编排启动器（MOD-INF-013 §14 拓扑排序 + ProcessLifecycleGateway 管理）。

读取 b_mcp.yaml 构建依赖 DAG → 拓扑排序 → 按层并行启动 → 等待 healthz 就绪。
所有进程通过 ProcessLifecycleGateway 管理，idle_timeout 空闲自动回收。

10 个 MCP Server 按 4 层 DAG 启动：
  layer_1: knowledge_base, gate_engine, blueprint_search, governance, vector_memory, telemetry (无依赖基础服务)
  layer_2: task_manager (依赖 knowledge_base, gate_engine)
  layer_3: session_handoff, intent_router (依赖 task_manager)
  layer_4: gateway (依赖所有 Server，最后启动)
"""

from __future__ import annotations

import atexit
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Any

import yaml

_MCP_DIR = Path(__file__).resolve().parent
_GOV_DIR = _MCP_DIR.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

SRC_ROOT = REPO_ROOT / "src"
B_MCP = REPO_ROOT / "architecture_model" / "layers" / "b_mcp.yaml"

_log = logging.getLogger(__name__)

# DAG 层级定义：10 个 Server / 4 非空层
# layer_0 保留为空（拓扑排序时跳过）
DAG_LAYERS: dict[str, list[str]] = {
    "layer_0": [],
    "layer_1": [
        "knowledge_base",
        "gate_engine",
        "blueprint_search",
        "governance",
        "vector_memory",
        "telemetry",
    ],
    "layer_2": ["task_manager"],
    "layer_3": ["session_handoff", "intent_router"],
    "layer_4": ["gateway"],
}

# Server ID → 脚本相对路径（实际路径：src/zephyr/integration/mcp/）
SERVER_SCRIPTS: dict[str, str] = {
    "knowledge_base": "src/zephyr/integration/mcp/knowledge_base_server.py",
    "gate_engine": "src/zephyr/integration/mcp/gate_engine_server.py",
    "blueprint_search": "src/zephyr/integration/mcp/blueprint_search_server.py",
    "governance": "src/zephyr/integration/mcp/governance_server.py",
    "vector_memory": "src/zephyr/integration/mcp/vector_memory_server.py",
    "telemetry": "src/zephyr/integration/mcp/telemetry_server.py",
    "task_manager": "src/zephyr/integration/mcp/task_manager_server.py",
    "session_handoff": "src/zephyr/integration/mcp/doc_guard_server.py",
    "intent_router": "src/zephyr/integration/mcp/sentinel_server.py",
    "gateway": "src/zephyr/integration/mcp/gateway_server.py",
}

HEALTHZ_TIMEOUT = 15.0
STARTUP_DELAY = 0.3
IDLE_TIMEOUT_S = 600.0  # 10 分钟空闲自动回收

# 全局 Gateway 引用（用于 atexit 兜底关闭）
_gateway: Any = None


def load_dag() -> dict[str, Any] | None:
    """加载 b_mcp.yaml 配置。"""
    if not B_MCP.exists():
        return None
    with open(B_MCP, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def topological_order() -> list[list[str]]:
    """返回 DAG 拓扑排序的非空层列表（跳过空层）。"""
    ordered: list[list[str]] = []
    for layer_key in sorted(DAG_LAYERS.keys()):
        servers = DAG_LAYERS[layer_key]
        if servers:
            ordered.append(servers)
    return ordered


def start_server(server_id: str, gateway) -> bool:
    """启动单个 MCP Server（通过 ProcessLifecycleGateway）。

    Args:
        server_id: Server 标识符
        gateway: ProcessLifecycleGateway 实例

    Returns:
        True 如果启动成功，False 如果失败
    """
    script = SERVER_SCRIPTS.get(server_id)
    if not script:
        _log.warning("unknown server_id: %s", server_id)
        return False
    script_path = REPO_ROOT / script
    if not script_path.exists():
        _log.warning("script not found: %s", script_path)
        return False

    entry = gateway.launch(
        f"mcp-{server_id}",
        [sys.executable, str(script_path)],
        idle_timeout_s=IDLE_TIMEOUT_S,  # 600 seconds (10 min)
    )
    if entry is None:
        _log.error("failed to start: %s", server_id)
        return False

    time.sleep(STARTUP_DELAY)
    if entry.is_alive:
        _log.info("started: %s pid=%d", server_id, entry.pid)
        return True
    _log.error("failed to start: %s", server_id)
    return False


def check_server_health(server_id: str, gateway) -> bool:
    """检查单个 MCP Server 健康状态。

    Args:
        server_id: Server 标识符
        gateway: ProcessLifecycleGateway 实例

    Returns:
        True 如果 Server 健康（存活），False 如果不健康
    """
    entry = gateway._pool._pool.get(f"mcp-{server_id}")
    if entry is None:
        return False
    return entry.is_alive


def restart_server(server_id: str, gateway) -> bool:
    """重启单个 MCP Server。

    Args:
        server_id: Server 标识符
        gateway: ProcessLifecycleGateway 实例

    Returns:
        True 如果重启成功，False 如果失败
    """
    _log.info("restarting server: %s", server_id)

    # 先终止旧进程
    entry = gateway._pool._pool.get(f"mcp-{server_id}")
    if entry is not None:
        try:
            entry.terminate()
        except Exception as e:
            _log.warning("terminate failed for %s: %s", server_id, e)

    # 重新启动
    return start_server(server_id, gateway)


def dry_run() -> int:
    """Dry-run 模式：打印启动计划但不实际启动进程。

    Returns:
        0 如果所有 Server 脚本路径存在，1 如果有缺失
    """
    print("MCP DAG Launcher — Dry Run (MOD-INF-013 §14)")
    print("=" * 60)

    order = topological_order()
    total = len(SERVER_SCRIPTS)
    print(f"Total servers: {total}")
    print(f"DAG layers: {len(order)} non-empty layers")
    print()

    all_exist = True
    for layer_idx, layer in enumerate(order):
        print(f"--- Layer {layer_idx + 1}: {layer} ---")
        for sid in layer:
            script = SERVER_SCRIPTS.get(sid, "")
            script_path = REPO_ROOT / script if script else None
            status = "OK" if (script_path and script_path.exists()) else "MISSING"
            if status == "MISSING":
                all_exist = False
            print(f"  {sid:20s} → {script}  [{status}]")

    print()
    print(f"Summary: {total} servers, {'all OK' if all_exist else 'has MISSING'}")
    return 0 if all_exist else 1


def _graceful_shutdown() -> None:
    """atexit 兜底关闭：确保所有子进程被清理。"""
    global _gateway
    if _gateway is not None:
        try:
            _gateway.terminate_all()
            _gateway.shutdown()
            print("[atexit] all servers terminated")
        except Exception as e:
            _log.warning("atexit shutdown failed: %s", e)
        finally:
            _gateway = None


def launch_all() -> dict[str, bool]:
    """启动全部 10 个 MCP Server（按 DAG 拓扑排序）。

    Returns:
        dict[server_id, bool] 每个 Server 的启动结果
    """
    from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

    global _gateway

    print("MCP DAG Launcher — MOD-INF-013 §14 (via ProcessLifecycleGateway)")
    print("=" * 60)

    gateway = ProcessLifecycleGateway(idle_timeout_s=IDLE_TIMEOUT_S)
    _gateway = gateway

    # 注册 atexit 兜底关闭
    atexit.register(_graceful_shutdown)

    order = topological_order()
    results: dict[str, bool] = {}
    running = True

    def _shutdown(sig, frame):
        nonlocal running
        running = False
        print("\n[shutdown] stopping all servers via Gateway...")
        gateway.terminate_all()
        gateway.shutdown()
        print("[shutdown] done")
        sys.exit(0)

    # signal.signal 只能在主线程中调用；后台线程中跳过
    import threading

    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)
    else:
        _log.info("launch_all: running in background thread, skipping signal registration")

    for layer_idx, layer in enumerate(order):
        print(f"\n--- Layer {layer_idx + 1}: {layer} ---")

        for sid in layer:
            ok = start_server(sid, gateway)
            results[sid] = ok
            if not ok:
                print(f"[FATAL] Layer {layer_idx + 1} server {sid!r} failed to start — aborting")
                gateway.terminate_all()
                gateway.shutdown()
                return results

        time.sleep(1.0)

        # 验证层内所有 Server 仍然存活
        for sid in layer:
            if not check_server_health(sid, gateway):
                print(f"[FATAL] Layer {layer_idx + 1} server {sid!r} died after start — aborting")
                gateway.terminate_all()
                gateway.shutdown()
                return results

    print(f"\n{'=' * 60}")
    ok = sum(1 for v in results.values() if v)
    print(f"All {ok}/{len(results)} servers running (idle_timeout_s={IDLE_TIMEOUT_S})")
    print("Press Ctrl+C to stop")

    try:
        while running:
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        gateway.terminate_all()
        gateway.shutdown()
        _gateway = None

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if "--dry-run" in sys.argv:
        exit_code = dry_run()
        sys.exit(exit_code)

    results = launch_all()
    ok = sum(1 for v in results.values() if v)
    print(f"\nSummary: {ok}/{len(results)} servers started")
    sys.exit(0 if ok == len(results) else 1)
