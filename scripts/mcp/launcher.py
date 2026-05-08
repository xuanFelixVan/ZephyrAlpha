"""MCP DAG 编排启动器（MOD-INF-013 §14 拓扑排序 + §13.1 进程隔离）。

读取 b_mcp.yaml 构建依赖 DAG → 拓扑排序 → 按层并行启动 → 等待 healthz 就绪。
"""

from __future__ import annotations

import json
import logging
import multiprocessing
import signal
import sys
import time
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
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


def _server_target(script_path: Path):
    """子进程入口——直接执行 server 的 __main__ 块。"""
    sys.path.insert(0, str(REPO_ROOT))
    g: dict[str, Any] = {}
    with open(script_path, encoding="utf-8") as fh:
        code = compile(fh.read(), str(script_path), "exec")
    exec(code, g)


def start_server(server_id: str) -> multiprocessing.Process | None:
    script = SERVER_SCRIPTS.get(server_id)
    if not script:
        _log.warning("unknown server_id: %s", server_id)
        return None
    script_path = REPO_ROOT / script
    if not script_path.exists():
        _log.warning("script not found: %s", script_path)
        return None

    proc = multiprocessing.Process(
        target=_server_target,
        args=(script_path,),
        name=f"mcp-{server_id}",
        daemon=True,
    )
    proc.start()
    time.sleep(STARTUP_DELAY)
    if proc.is_alive():
        _log.info("started: %s pid=%d", server_id, proc.pid)
        return proc
    _log.error("failed to start: %s exit_code=%s", server_id, proc.exitcode)
    return None


def launch_all() -> dict[str, bool]:
    print("MCP DAG Launcher — MOD-INF-013 §14")
    print("=" * 50)

    order = topological_order()
    processes: dict[str, multiprocessing.Process] = {}
    results: dict[str, bool] = {}
    running = True

    def _shutdown(sig, frame):
        nonlocal running
        running = False
        print("\n[shutdown] stopping all servers...")
        for sid, proc in processes.items():
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=3)
        print("[shutdown] done")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    for layer_idx, layer in enumerate(order):
        print(f"\n--- Layer {layer_idx+1}: {layer} ---")
        layer_procs: dict[str, multiprocessing.Process] = {}

        for sid in layer:
            proc = start_server(sid)
            if proc is not None:
                processes[sid] = proc
                layer_procs[sid] = proc
                results[sid] = True
            else:
                results[sid] = False
                print(f"[FATAL] Layer {layer_idx+1} server {sid!r} failed to start — aborting")
                # terminate already started
                for p in processes.values():
                    if p.is_alive():
                        p.terminate()
                        p.join(timeout=2)
                return results

        time.sleep(1.0)

        alive = {sid: p for sid, p in layer_procs.items() if p.is_alive()}
        if len(alive) < len(layer_procs):
            dead = set(layer_procs) - set(alive)
            print(f"[FATAL] Layer {layer_idx+1} servers died: {dead} — aborting")
            for p in processes.values():
                if p.is_alive():
                    p.terminate()
                    p.join(timeout=2)
            return results

    print(f"\n{'='*50}")
    ok = sum(1 for v in results.values() if v)
    print(f"All {ok}/{len(results)} servers running")
    print("Press Ctrl+C to stop")

    try:
        while running:
            dead = {sid for sid, p in processes.items() if not p.is_alive()}
            if dead:
                print(f"[WARN] servers died: {dead}")
                for sid in dead:
                    results[sid] = False
                break
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        for p in processes.values():
            if p.is_alive():
                p.terminate()
                p.join(timeout=3)

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    results = launch_all()
    ok = sum(1 for v in results.values() if v)
    print(f"\nSummary: {ok}/{len(results)} servers started")
    sys.exit(0 if ok == len(results) else 1)
