# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §16 Phase 2b
# [MODULE] zephyr.security.adversarial_validation.cold_start
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] game_day_runner.py; validator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] New module/MCP server joining MUST auto-register adversarial scenarios; bootstrap per §8.1 onboarding protocol
# [MODIFY-GUARD] Registration writes to _scenario-registry.yaml with atomic os.replace; bootstrap phases: SCAN→MAP→REGISTER→VERIFY
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BootstrapVerificationError if bootstrap fails post-registration verification
# [TESTS] tests/red_blue/test_cold_start.py
# [A_module] module_id=MOD-SEC_cold_start | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
import os
import uuid
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

__all__: list[str] = ["BootstrapPhase", "BootstrapVerificationError", "ColdStart"]

_REGISTRY_PATH: Path = Path(__file__).parent / "_scenario-registry.yaml"

REGISTRATION_TEMPLATES: Final[dict[str, dict]] = {
    "python_module": {
        "name": "Onboard inspection of {module_name}",
        "description": "Auto-generated adversarial scenario for newly joined module {module_name}",
        "tier": "L1",
        "severity": "MEDIUM",
        "target_module": "{module_name}",
        "injection_vector": "{module_name}.import_attack",
        "defense": "{module_name}.verify_imports",
        "blast_radius": "FILE",
    },
    "mcp_server": {
        "name": "MCP security inspection of {server_id}",
        "description": "Auto-generated adversarial scenario for new MCP server {server_id}",
        "tier": "L1",
        "severity": "MEDIUM",
        "target_module": "zephyr.infrastructure.mcp_server",
        "injection_vector": "mcp.{server_id}.tool_abuse",
        "defense": "mcp_auth.verify_tool_access",
        "blast_radius": "MODULE",
    },
    "script": {
        "name": "Script integrity check of {script_path}",
        "description": "Auto-generated adversarial scenario for new script {script_path}",
        "tier": "L1",
        "severity": "LOW",
        "target_module": "{script_path}",
        "injection_vector": "{script_path}.execution_hijack",
        "defense": "immutable_core.verify_roles",
        "blast_radius": "FILE",
    },
}


class BootstrapPhase(str, Enum):
    SCAN = "SCAN"
    MAP = "MAP"
    REGISTER = "REGISTER"
    VERIFY = "VERIFY"
    COMPLETE = "COMPLETE"


class BootstrapVerificationError(RuntimeError):
    pass


class ColdStart:
    def __init__(self, registry_path: Path | None = None) -> None:
        self._registry_path: Path = registry_path or _REGISTRY_PATH
        self._phase: BootstrapPhase = BootstrapPhase.SCAN

    @property
    def phase(self) -> BootstrapPhase:
        return self._phase

    def onboard_module(self, module_path: str) -> str | None:
        self._phase = BootstrapPhase.SCAN

        if self._is_registered("target_module", module_path):
            logger.info("module_already_registered module=%s", module_path)
            self._phase = BootstrapPhase.COMPLETE
            return None

        self._phase = BootstrapPhase.MAP
        artifact_type = self._classify(module_path)

        self._phase = BootstrapPhase.REGISTER
        template = REGISTRATION_TEMPLATES.get(artifact_type, REGISTRATION_TEMPLATES["python_module"])
        scenario_id = self._create_scenario(template, module_path)

        self._phase = BootstrapPhase.VERIFY
        if not self._verify_registration(scenario_id):
            raise BootstrapVerificationError(f"Registration verification failed for {scenario_id}")

        self._phase = BootstrapPhase.COMPLETE
        logger.info("cold_start_complete module=%s scenario_id=%s", module_path, scenario_id)
        return scenario_id

    def onboard_batch(self, paths: list[str]) -> list[str]:
        ids: list[str] = []
        for path in paths:
            sid = self.onboard_module(path)
            if sid:
                ids.append(sid)
        return ids

    def _classify(self, path: str) -> str:
        if "mcp_server" in path or path.startswith("mcp."):
            return "mcp_server"
        if path.endswith(".py") and "scripts/" in path:
            return "script"
        return "python_module"

    def _create_scenario(self, template: dict, identifier: str) -> str:
        scenario_id = f"RB-CS-{uuid.uuid4().hex[:8]}"

        new_scenario = {
            "scenario_id": scenario_id,
            "name": template["name"]
            .replace("{module_name}", identifier)
            .replace("{server_id}", identifier)
            .replace("{script_path}", identifier),
            "description": template["description"]
            .replace("{module_name}", identifier)
            .replace("{server_id}", identifier)
            .replace("{script_path}", identifier),
            "tier": template["tier"],
            "severity": template["severity"],
            "target_module": template["target_module"]
            .replace("{module_name}", identifier)
            .replace("{script_path}", identifier),
            "injection_vector": template["injection_vector"]
            .replace("{module_name}", identifier)
            .replace("{server_id}", identifier)
            .replace("{script_path}", identifier),
            "defense": template["defense"]
            .replace("{module_name}", identifier)
            .replace("{server_id}", identifier)
            .replace("{script_path}", identifier),
            "blast_radius": template["blast_radius"],
            "auto_cleanup": True,
            "realism_score": 0.7,
            "source": "cold_start",
            "status": "active",
        }

        if not self._registry_path.exists():
            self._init_registry()

        with open(self._registry_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        raw.setdefault("scenarios", []).append(new_scenario)

        tmp = self._registry_path.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(raw, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp, self._registry_path)

        return scenario_id

    def _init_registry(self) -> None:
        initial: dict[str, Any] = {"scenarios": [], "total_count": 0}
        with open(self._registry_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(initial, f, allow_unicode=True)

    def _is_registered(self, field: str, value: str) -> bool:
        if not self._registry_path.exists():
            return False
        with open(self._registry_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        for scenario in raw.get("scenarios", []):
            if scenario.get(field) == value:
                return True
        return False

    def _verify_registration(self, scenario_id: str) -> bool:
        if not self._registry_path.exists():
            return False
        with open(self._registry_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        for scenario in raw.get("scenarios", []):
            if scenario.get("scenario_id") == scenario_id:
                return True
        return False
