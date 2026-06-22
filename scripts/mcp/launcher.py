# [BLUEPRINT] MOD-INF-005 | scripts/mcp/launcher.py | §
"""MCP DAG 编排启动器（MOD-INF-013 §14 拓扑排序 + ProcessLifecycleGateway 管理）。

读取 b_mcp.yaml 构建依赖 DAG → 拓扑排序 → 按层并行启动 → 等待 healthz 就绪。
所有进程通过 ProcessLifecycleGateway 管理，idle_timeout 空闲自动回收。
"""

from __future__ import annotations

import logging
import signal
import sys
import time
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_ROOT = REPO_ROOT / "src"
B_MCP = REPO_ROOT / "architecture-model" / "layers" / "b_mcp.yaml"

_log = logging.getLogger(__name__)

DAG_LAYERS: dict[str, list[str]] = {
    "layer_0": [],
    "layer_1": ["knowledge_base", "gate_engine", "blueprint_search"],
    "layer_2": ["task_manager"],
    "layer_3": ["session_handoff", "intent_router"],
}

SERVER_SCRIPTS: dict[str, str] = {
    "knowledge_base": "src/zephyr/mcp/knowledge_base_server.py",
    "gate_engine": "src/zephyr/mcp/gate_engine_server.py",
    "blueprint_search": "src/zephyr/mcp/blueprint_search_server.py",
    "task_manager": "src/zephyr/mcp/task_manager_server.py",
    "session_handoff": "src/zephyr/mcp/doc_guard_server.py",
    "intent_router": "src/zephyr/mcp/sentinel_server.py",
}

HEALTHZ_TIMEOUT = 15.0
STARTUP_DELAY = 0.3


def load_dag() -> dict[str, Any] | None:
    if not B_MCP.exists():
        return None
    with open(B_MCP, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def topological_order() -> list[list[str]]:
    ordered: list[list[str]] = []
    for layer_key in sorted(DAG_LAYERS.keys()):
        servers = DAG_LAYERS[layer_key]
        if servers:
            ordered.append(servers)
    return ordered


def start_server(server_id: str, gateway) -> bool:
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
        idle_timeout_s=600.0,
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


def launch_all() -> dict[str, bool]:
    from zephyr.integration.infra.process_lifecycle_gateway import ProcessLifecycleGateway

    print("MCP DAG Launcher — MOD-INF-013 §14 (via ProcessLifecycleGateway)")
    print("=" * 50)

    gateway = ProcessLifecycleGateway()
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

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

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

        for sid in layer:
            script = SERVER_SCRIPTS.get(sid, "")
            script_path = str(REPO_ROOT / script) if script else ""
            entry = gateway.launch(
                f"mcp-{sid}",
                [sys.executable, script_path] if script_path else [],
                idle_timeout_s=600.0,
            )
            if entry is None or not entry.is_alive:
                print(f"[FATAL] Layer {layer_idx + 1} server {sid!r} died after start — aborting")
                gateway.terminate_all()
                gateway.shutdown()
                return results

    print(f"\n{'=' * 50}")
    ok = sum(1 for v in results.values() if v)
    print(f"All {ok}/{len(results)} servers running")
    print("Press Ctrl+C to stop")

    try:
        while running:
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        gateway.terminate_all()
        gateway.shutdown()

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    results = launch_all()
    ok = sum(1 for v in results.values() if v)
    print(f"\nSummary: {ok}/{len(results)} servers started")
    sys.exit(0 if ok == len(results) else 1)
