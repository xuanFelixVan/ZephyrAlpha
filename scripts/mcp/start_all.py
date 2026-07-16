# [BLUEPRINT] MOD-INF-005 | scripts/mcp/start_all.py | §
# [MODULE] scripts.mcp.start_all
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# DEPRECATED: 合并到 launcher.py (2026-05-17)
# 进程生命周期由 ProcessLifecycleGateway 统一管理。
# MCP Server 启动请使用: python scripts/mcp/launcher.py
# 停止请使用: python scripts/mcp/stop_all.py
"""MCP 全 Server 启动脚本 — DEPRECATED.

启动顺序（遵守 MOD-INF-013 §14 DAG 顺序）：SQLite → ChromaDB → 7 Server → Gateway。
⚠️ 此脚本已废弃。请使用 launcher.py（通过 ProcessLifecycleGateway 管理进程生命周期）。
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parents[1] / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent

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
