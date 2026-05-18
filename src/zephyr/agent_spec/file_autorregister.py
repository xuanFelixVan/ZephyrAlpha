# [BLUEPRINT] MOD-INF-019 | 03_modules/l01_infrastructure/agent-spec/blueprint.md | §

# [MODULE] zephyr.agent_spec.file_autorregister

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — File Auto-Register
Blueprint: docs/03_modules/l01_infrastructure/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class FileAutoRegister:
    """新文件自动注册——新建 .py 自动注册到 script_manifest.yaml 并关联 Domain Skill"""

    def __init__(self, manifest_path: Optional[Path] = None):
        self.manifest_path = manifest_path or Path(__file__).resolve().parent.parent.parent / "scripts" / "governance" / "script_manifest.yaml"

    def register(self, file_path: str) -> Dict[str, Any]:
        script_name = Path(file_path).stem
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}

        manifest.setdefault("scripts", {})
        manifest["scripts"][script_name] = {
            "path": file_path,
            "module": "agent_spec",
            "registered_by": "file_autorregister",
        }

        with open(self.manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(manifest, f, allow_unicode=True, default_flow_style=False)
        return {"script_name": script_name, "registered": True}
