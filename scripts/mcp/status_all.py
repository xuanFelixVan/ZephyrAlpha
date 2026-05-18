# [BLUEPRINT] MOD-INF-005 | scripts/mcp/status_all.py | §
"""MCP 全 Server 状态检查脚本（MOD-INF-013 §14）。"""

from __future__ import annotations

import subprocess
import sys

if __name__ == "__main__":
    if sys.platform == "win32":
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True, text=True,
        )
        lines = [l for l in result.stdout.splitlines() if "mcp" in l.lower()]
        print(f"MCP python processes: {len(lines)}")
        for line in lines:
            print(f"  {line}")
    else:
        subprocess.run(["pgrep", "-f", "mcp.*server"])
