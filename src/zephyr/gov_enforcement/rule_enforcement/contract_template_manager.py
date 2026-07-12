# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.contract_template_manager
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_contract_template_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ContractTemplateManager: manage MCP tool contract templates
============================================================
Task ID : T-2-31 (C55)
safety_level : L
Depends : none

Manages MCP (Model Context Protocol) tool contract templates:
  - Register new contract templates with schema validation
  - Look up templates by tool name
  - List all registered templates
  - Validate tool invocations against registered contracts
  - Persist templates to disk as JSON
"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from zephyr.integration.shared.schema.schemas import BASE_CONFIG

__all__ = [
    "ContractParameter",
    "ContractTemplate",
    "ContractTemplateManager",
]


class ContractParameter(BaseModel):
    model_config = BASE_CONFIG

    name: str = Field(min_length=1, description="Parameter name")
    param_type: str = Field(min_length=1, description="Parameter type (str, int, float, bool, list, dict)")
    required: bool = Field(default=True, description="Whether parameter is required")
    description: str = Field(default="", max_length=500, description="Parameter description")
    default: str | None = Field(default=None, description="Default value as string representation")

    @field_validator("param_type")
    @classmethod
    def valid_param_type(cls, v: str) -> str:
        allowed = {"str", "int", "float", "bool", "list", "dict"}
        if v not in allowed:
            raise ValueError(f"param_type must be one of {allowed}, got '{v}'")
        return v


class ContractTemplate(BaseModel):
    model_config = BASE_CONFIG

    tool_name: str = Field(min_length=1, max_length=200, description="MCP tool name")
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$", description="Semantic version")
    description: str = Field(default="", max_length=1000, description="Tool description")
    parameters: list[ContractParameter] = Field(default_factory=list, description="Tool parameters")
    return_type: str = Field(default="dict", description="Return type of the tool")
    safety_level: str = Field(default="L", pattern=r"^[LMH]$", description="Safety level L/M/H")
    created_at: datetime = Field(description="Template creation timestamp")
    updated_at: datetime = Field(description="Template last update timestamp")

    @field_validator("parameters")
    @classmethod
    def no_duplicate_param_names(cls, v: list[ContractParameter]) -> list[ContractParameter]:
        names = [p.name for p in v]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate parameter names are not allowed")
        return v

    @field_validator("updated_at")
    @classmethod
    def updated_not_before_created_check(cls, v: datetime) -> datetime:
        return v


class ContractTemplateManager:
    """Manage MCP tool contract templates.

    Parameters
    ----------
    store_path : Path | None
        Optional file path for persisting templates as JSON.
        If None, templates are kept in-memory only.
    """

    def __init__(self, store_path: Path | None = None) -> None:
        self._templates: dict[str, ContractTemplate] = {}
        self._store_path = store_path

    def register(self, template: ContractTemplate) -> ContractTemplate:
        key = template.tool_name
        if key in self._templates:
            existing = self._templates[key]
            if existing.version == template.version and existing.updated_at >= template.updated_at:
                raise ValueError(f"Template '{key}' v{template.version} already registered")
        self._templates[key] = template
        return template

    def get(self, tool_name: str) -> ContractTemplate | None:
        return self._templates.get(tool_name)

    def list_templates(self) -> list[ContractTemplate]:
        return sorted(self._templates.values(), key=lambda t: t.tool_name)

    def remove(self, tool_name: str) -> bool:
        if tool_name in self._templates:
            del self._templates[tool_name]
            return True
        return False

    def validate_invocation(self, tool_name: str, params: dict[str, object]) -> list[str]:
        template = self.get(tool_name)
        if template is None:
            return [f"Unknown tool: {tool_name}"]

        errors: list[str] = []
        required_names = {p.name for p in template.parameters if p.required}
        provided_names = set(params.keys())

        missing = required_names - provided_names
        for name in sorted(missing):
            errors.append(f"Missing required parameter: {name}")

        known_names = {p.name for p in template.parameters}
        unknown = provided_names - known_names
        for name in sorted(unknown):
            errors.append(f"Unknown parameter: {name}")

        return errors

    def flush(self) -> int:
        if self._store_path is None:
            return 0
        data = {k: v.model_dump(mode="json") for k, v in self._templates.items()}
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._store_path.write_text(
            dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return len(self._templates)

    def load(self) -> int:
        if self._store_path is None or not self._store_path.exists():
            return 0
        raw = self._store_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        loaded: dict[str, ContractTemplate] = {}
        for key, val in data.items():
            loaded[key] = ContractTemplate.model_validate(val)
        self._templates = loaded
        return len(loaded)

    def clear(self) -> int:
        count = len(self._templates)
        self._templates.clear()
        return count

    @property
    def template_count(self) -> int:
        return len(self._templates)

    @property
    def store_path(self) -> Path | None:
        return self._store_path
