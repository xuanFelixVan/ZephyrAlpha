# [BLUEPRINT] SRC-084 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.adaptation.prompt_version_manager
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.adaptation.execution_tuner
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_prompt_version_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Prompt Version Manager — 版本化 Prompt 治理。

依据：
    蓝图 MOD-TASK_SYSTEM §6.7 + v0.6.0
    任务卡 TASK-INF-0112
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class PromptVersion:
    prompt_id: str
    version: str
    content: str
    model: str
    pipeline_module: str
    performance_score: float = 0.0
    usage_count: int = 0
    last_used: str = ""
    deprecated: bool = False


@dataclass
class PromptRegistry:
    prompts: dict[str, list[PromptVersion]]
    current_versions: dict[str, str]
    last_updated: str


class PromptVersionManager:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/adaptation/prompts")
        self._registry = PromptRegistry(
            prompts={},
            current_versions={},
            last_updated=datetime.now(UTC).isoformat(),
        )

    def register(
        self, prompt_id: str, version: str, content: str, model: str = "deepseek", pipeline_module: str = ""
    ) -> PromptVersion:
        prompt = PromptVersion(
            prompt_id=prompt_id,
            version=version,
            content=content,
            model=model,
            pipeline_module=pipeline_module,
            last_used=datetime.now(UTC).isoformat(),
        )

        if prompt_id not in self._registry.prompts:
            self._registry.prompts[prompt_id] = []
        self._registry.prompts[prompt_id].append(prompt)
        self._registry.current_versions[prompt_id] = version
        self._registry.last_updated = datetime.now(UTC).isoformat()

        self._persist()

        return prompt

    def get_current(self, prompt_id: str) -> PromptVersion | None:
        versions = self._registry.prompts.get(prompt_id, [])
        current_ver = self._registry.current_versions.get(prompt_id)

        if not current_ver:
            return None

        for pv in versions:
            if pv.version == current_ver and not pv.deprecated:
                pv.usage_count += 1
                pv.last_used = datetime.now(UTC).isoformat()
                return pv

        return None

    def deprecate(self, prompt_id: str, version: str) -> bool:
        versions = self._registry.prompts.get(prompt_id, [])
        for pv in versions:
            if pv.version == version:
                pv.deprecated = True
                self._persist()
                return True
        return False

    def rollback_to(self, prompt_id: str, version: str) -> bool:
        versions = self._registry.prompts.get(prompt_id, [])
        for pv in versions:
            if pv.version == version:
                self._registry.current_versions[prompt_id] = version
                pv.deprecated = False
                self._persist()
                return True
        return False

    def list_versions(self, prompt_id: str) -> list[PromptVersion]:
        return self._registry.prompts.get(prompt_id, [])

    def _persist(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        registry_path = self._data_dir / "prompt_registry.json"

        data = {
            "last_updated": self._registry.last_updated,
            "current_versions": self._registry.current_versions,
            "prompts": {
                pid: [
                    {
                        "version": pv.version,
                        "model": pv.model,
                        "performance_score": pv.performance_score,
                        "usage_count": pv.usage_count,
                        "last_used": pv.last_used,
                        "deprecated": pv.deprecated,
                    }
                    for pv in versions
                ]
                for pid, versions in self._registry.prompts.items()
            },
        }

        registry_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
