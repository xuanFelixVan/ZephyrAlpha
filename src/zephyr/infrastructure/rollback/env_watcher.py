# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.env_watcher
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_env_watcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
EnvWatcher — 环境变量热重载监控器。

依据: 蓝图 MOD-INF-021 §6.12 B69

监控 .env 文件修改 → 写入 last_env_reload sentinel 文件。
回滚涉及 .env 变更时 → watcher 检测 sentinel → 通知 Agent 需要 re-source。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class EnvChangeAlert:
    env_file: str
    changed_keys: list[str]
    changed_at: str
    agent_action: str


class EnvWatcher:
    SENTINEL_FILE: str = ".zephyr/last_env_reload.json"
    ENV_FILES: list[str] = [".env", ".env.local"]

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._sentinel_path = self._project_root / self.SENTINEL_FILE
        self._sentinel_path.parent.mkdir(parents=True, exist_ok=True)

    def check_for_changes(self) -> EnvChangeAlert | None:
        current_state = self._read_env_files()
        if not current_state:
            return None

        previous_state = self._read_sentinel()

        changed_keys: list[str] = []
        for key, value in current_state.items():
            if key not in previous_state or previous_state[key] != value:
                changed_keys.append(key)

        if not changed_keys:
            return None

        self._write_sentinel(current_state)

        return EnvChangeAlert(
            env_file=",".join(self.ENV_FILES),
            changed_keys=changed_keys,
            changed_at=datetime.now(UTC).isoformat(),
            agent_action="RELOAD_ENV_FROM_SENTINEL",
        )

    def notify_agent_reload_required(self) -> dict[str, Any]:
        alert = self.check_for_changes()
        if not alert:
            return {"reload_required": False}
        return {
            "reload_required": True,
            "changed_keys": alert.changed_keys,
            "sentinel_path": str(self._sentinel_path),
            "instruction": "re-source environment from .env files before proceeding",
        }

    def _read_env_files(self) -> dict[str, str]:
        state: dict[str, str] = {}
        for env_file in self.ENV_FILES:
            path = self._project_root / env_file
            if not path.exists():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    state[key.strip()] = value.strip()
        return state

    def _read_sentinel(self) -> dict[str, str]:
        if not self._sentinel_path.exists():
            return {}
        try:
            return json.loads(self._sentinel_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _write_sentinel(self, state: dict[str, str]) -> None:
        self._sentinel_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
