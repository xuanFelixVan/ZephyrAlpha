# [BLUEPRINT] SRC-144 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.shared_services.sync.blueprint_code_sync
# [DOMAIN] D-INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_blueprint_code_sync | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
Blueprint-Code Sync — §5 蓝图-代码同步验证。

依据：
    蓝图 MOD-TASK_SYSTEM §6.4.2 + v0.6.0
    任务卡 TASK-INF-0119
    （与 0111 Part 2 互补——此为 sync/ 专用模块）
"""

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class SyncPair:
    blueprint_section: str
    code_path: str
    synced: bool
    checksum: str
    last_verified: str


@dataclass
class SyncVerification:
    total_pairs: int
    synced_count: int
    stale_count: int
    pairs: list[SyncPair]
    passed: bool
    timestamp_utc: str


class BlueprintCodeSyncService:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def verify_sync(self, pairs: list[dict[str, str]]) -> SyncVerification:
        results: list[SyncPair] = []
        synced = 0
        stale = 0

        for pair in pairs:
            bp_section = pair.get("section", "")
            code_path_str = pair.get("code_path", "")

            code_full = self._project_root / code_path_str
            synced_flag = code_full.exists()

            checksum = ""
            if synced_flag:
                checksum = hashlib.sha256(code_full.read_bytes()).hexdigest()[:16]

            results.append(
                SyncPair(
                    blueprint_section=bp_section,
                    code_path=code_path_str,
                    synced=synced_flag,
                    checksum=checksum,
                    last_verified=datetime.now(UTC).isoformat(),
                )
            )

            if synced_flag:
                synced += 1
            else:
                stale += 1

        return SyncVerification(
            total_pairs=len(pairs),
            synced_count=synced,
            stale_count=stale,
            pairs=results,
            passed=stale == 0,
            timestamp_utc=datetime.now(UTC).isoformat(),
        )

    def check_sync_consistency(self) -> dict[str, Any]:
        critical_pairs = [
            {"section": "§2.2 Data Model", "code_path": "src/zephyr/core/models.py"},
            {"section": "§3.1 Decomposer", "code_path": "src/zephyr/core/blueprint_decomposer.py"},
            {"section": "§3.2 Task Server", "code_path": "src/zephyr/mcp/task_manager_server.py"},
            {"section": "§3.1.2 Lifecycle", "code_path": "src/zephyr/core/lifecycle/task_lifecycle_manager.py"},
        ]

        result = self.verify_sync(critical_pairs)
        return {
            "synced": result.passed,
            "coverage": f"{result.synced_count}/{result.total_pairs}",
            "stale_files": [p.code_path for p in result.pairs if not p.synced],
        }
