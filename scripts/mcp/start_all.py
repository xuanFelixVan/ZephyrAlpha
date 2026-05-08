"""MCP 全 Server 启动脚本（MOD-INF-013 §14 DAG 顺序）。

启动顺序（遵守 §14 依赖图）：SQLite → ChromaDB → 7 Server → Gateway。
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent.parent

SERVER_SCRIPTS: list[tuple[str, str]] = [
    ("knowledge_base", "src/zephyr/mcp/knowledge_base_server.py"),
    ("gate_engine", "src/zephyr/mcp/gate_engine_server.py"),
    ("doc_guard", "src/zephyr/mcp/doc_guard_server.py"),
    ("sentinel", "src/zephyr/mcp/sentinel_server.py"),
    ("blueprint_search", "src/zephyr/mcp/blueprint_search_server.py"),
    ("task_manager", "src/zephyr/mcp/task_manager_server.py"),
    ("gateway", "src/zephyr/mcp/gateway_server.py"),
]


def start_all() -> dict[str, bool]:
    results: dict[str, bool] = {}
    for name, script in SERVER_SCRIPTS:
        script_path = REPO_ROOT / script
        if not script_path.exists():
            print(f"[SKIP] {name}: {script} not found")
            results[name] = False
            continue
        try:
            proc = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(0.5)
            if proc.poll() is None:
                print(f"[OK] {name}: pid={proc.pid}")
                results[name] = True
            else:
                print(f"[FAIL] {name}: exited with code {proc.returncode}")
                results[name] = False
        except Exception as exc:
            print(f"[ERROR] {name}: {exc}")
            results[name] = False
    return results


if __name__ == "__main__":
    results = start_all()
    ok = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nSummary: {ok}/{total} started")
    sys.exit(0 if ok == total else 1)
