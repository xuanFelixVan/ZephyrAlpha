# [BLUEPRINT] MOD-INF-005 | scripts/mcp/stop_all.py | §
# [MODULE] scripts.mcp.stop_all
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.mcp.status_all
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
"""MCP 全 Server 停止脚本（MOD-INF-013 §14）。

通过 PID 文件精准停止 MCP Server 进程，避免误杀其他 Python 进程。
PID 文件由 launcher.py / start_all.py 写入 data/mcp_pids/ 目录。
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
_GOV_DIR = _MCP_DIR.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

_PID_DIR = REPO_ROOT / "data" / "mcp_pids"


def _stop_by_pid_files() -> int:
    stopped = 0
    if not _PID_DIR.exists():
        print("[INFO] No PID directory found, nothing to stop")
        return 0

    for pid_file in sorted(_PID_DIR.glob("*.pid")):
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            stopped += 1
            print(f"[OK] Stopped PID {pid} ({pid_file.stem})")
        except ProcessLookupError:
            print(f"[SKIP] PID {pid} already gone ({pid_file.stem})")
        except PermissionError:
            print(f"[WARN] No permission to kill PID {pid} ({pid_file.stem})")
        except Exception as exc:
            print(f"[WARN] Failed to stop {pid_file.stem}: {exc}")
        finally:
            try:
                pid_file.unlink(missing_ok=True)
            except OSError:
                pass

    return stopped


def _stop_by_window_title() -> int:
    stopped = 0
    mcp_modules = [
        "task_manager_server",
        "knowledge_base_server",
        "gate_engine_server",
        "doc_guard_server",
        "sentinel_server",
        "blueprint_search_server",
        "sandbox_server",
        "governance_server",
        "telemetry_server",
        "vector_memory_server",
        "gateway_server",
    ]
    for mod in mcp_modules:
        try:
            result = subprocess.run(
                ["wmic", "process", "where", f"CommandLine like '%{mod}%' and Name='python.exe'", "call", "terminate"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if "ReturnValue = 0" in result.stdout:
                stopped += 1
                print(f"[OK] Stopped {mod}")
        except Exception as exc:
            print(f"[WARN] WMIC stop failed for {mod}: {exc}")

    return stopped


if __name__ == "__main__":
    stopped = _stop_by_pid_files()

    if stopped == 0 and sys.platform == "win32":
        stopped = _stop_by_window_title()

    if stopped == 0 and sys.platform != "win32":
        try:
            subprocess.run(["pkill", "-f", "mcp.*server"], check=False)
            print("[OK] MCP servers stopped via pkill")
            stopped = 1
        except Exception as exc:
            print(f"[WARN] pkill failed: {exc}")

    if stopped > 0:
        print(f"[DONE] Stopped {stopped} MCP server(s)")
    else:
        print("[INFO] No MCP servers were running")
