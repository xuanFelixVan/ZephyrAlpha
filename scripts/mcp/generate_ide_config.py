# [BLUEPRINT] MOD-INF-005 | scripts/mcp/generate_ide_config.py | §
# [MODULE] scripts.mcp.generate_ide_config
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
"""从 config/mcp.json 生成各 IDE MCP 配置文件（MOD-INF-013 §5.3 Step 2）。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parents[1] / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402

MCP_CONFIG = REPO_ROOT / "config" / "mcp.json"


def generate_ide_configs() -> dict[str, bool]:
    if not MCP_CONFIG.exists():
        print(f"[ERROR] {MCP_CONFIG} not found")
        return {"error": False}

    with open(MCP_CONFIG, encoding="utf-8") as fh:
        cfg = json.load(fh)

    servers = cfg.get("servers", {})
    ide_targets: dict[str, Path] = {
        "trae": REPO_ROOT / ".trae" / "mcp.json",
        "cursor": REPO_ROOT / ".cursor" / "mcp.json",
        "claude": REPO_ROOT / ".claude" / "mcp.json",
        "vscode": REPO_ROOT / ".vscode" / "mcp.json",
    }

    results: dict[str, bool] = {}
    for ide_name, target_path in ide_targets.items():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        ide_config = {"mcpServers": {}}
        for sid, srv in servers.items():
            if srv.get("status") == "planning":
                continue
            ide_config["mcpServers"][sid] = {
                "command": sys.executable,
                "args": ["-m", f"zephyr.integration.mcp.{srv['module']}"],
            }
        with open(target_path, "w", encoding="utf-8") as fh:
            json.dump(ide_config, fh, indent=2, ensure_ascii=False)
        print(f"[OK] {ide_name}: {target_path}")
        results[ide_name] = True

    return results


if __name__ == "__main__":
    results = generate_ide_configs()
    ok = sum(1 for v in results.values() if v)
    print(f"\nGenerated {ok}/{len(results)} IDE configs")
