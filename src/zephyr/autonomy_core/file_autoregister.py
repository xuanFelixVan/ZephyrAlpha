# [A_module] module_id=MOD-ORC_file_autoregister | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md

# [MODULE] src.zephyr.autonomy_core.file_autoregister

# [INVARIANTS]

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

import os
from pathlib import Path
from typing import Any

import yaml


class FileAutoRegister:
    def __init__(self, manifest_path: Path | None = None):
        self.manifest_path = (
            manifest_path
            or Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "governance" / "script-manifest.yaml"
        )

    def register(self, file_path: str, module: str = "unknown") -> dict[str, Any]:
        script_name = Path(file_path).stem
        with open(self.manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}

        manifest.setdefault("scripts", {})
        manifest["scripts"][script_name] = {
            "path": file_path,
            "module": module,
            "registered_by": "file_autoregister",
        }

        tmp_path = f"{self.manifest_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(manifest, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            os.replace(tmp_path, self.manifest_path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

        return {"script_name": script_name, "registered": True}


__all__ = ["FileAutoRegister"]
