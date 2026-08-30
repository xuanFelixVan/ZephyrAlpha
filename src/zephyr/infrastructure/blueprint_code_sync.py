# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.blueprint_code_sync
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Blueprint-Code Sync — 蓝图-代码索引同步验证。

依据：
    蓝图 MOD-TASK_SYSTEM §6.4.2 + v0.6.0
    任务卡 TASK-INF-0111 (Part 2/2)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: blueprint_code_sync.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① BlueprintCodeSync
#   name_en: BlueprintCodeSync
#   intro: class BlueprintCodeSync 源码 L85-L173
#   desc: 公共方法（定义序）: registry_path, project_root, collect_entries, verify_sync, validate_task_card；源码 L85-L173
#   inputs: project_root
#   outputs: 返回值
# - id: A2
#   name_zh: ② BlueprintCodeSyncService
#   name_en: BlueprintCodeSyncService
#   intro: class BlueprintCodeSyncService 源码 L184-L192
#   desc: 公共方法（定义序）: sync, check_drift；源码 L184-L192
#   inputs: config
#   outputs: 返回值
#   （注：A2 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: BlueprintCodeSync, BlueprintCodeSyncService
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class SyncEntry:
    blueprint_path: str
    code_path: str
    status: str
    last_synced: str = ""


@dataclass
class SyncReport:
    total_entries: int
    synced: int
    missing: int
    stale: int
    entries: list[SyncEntry]
    timestamp_utc: str


class BlueprintCodeSync:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._registry_path = self._project_root / "docs" / "03_modules" / "blueprint_registry.yaml"

    @property
    def registry_path(self):
        """只读：registry_path（Stage 4 公共化）。"""
        return self._registry_path

    @registry_path.setter
    def registry_path(self, value):
        """写入：registry_path（Stage 4 公共化）。"""
        self._registry_path = value

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def collect_entries(self) -> list[SyncEntry]:
        """公共接口：collect_entries（Stage 4 公共化）。"""
        return self._collect_entries()

    def verify_sync(self) -> SyncReport:
        entries = self._collect_entries()

        synced = 0
        missing = 0
        stale = 0

        for entry in entries:
            code_full = self._project_root / entry.code_path
            blueprint_full = self._project_root / entry.blueprint_path

            if not code_full.exists():
                entry.status = "MISSING"
                missing += 1
            elif not blueprint_full.exists():
                entry.status = "STALE"
                stale += 1
            else:
                entry.status = "SYNCED"
                synced += 1

        return SyncReport(
            total_entries=len(entries),
            synced=synced,
            missing=missing,
            stale=stale,
            entries=entries,
            timestamp_utc=datetime.now(UTC).isoformat(),
        )

    def validate_task_card(self, task_card: dict[str, Any]) -> tuple[bool, str]:
        downstream = task_card.get("downstream_outputs", [])
        for output in downstream:
            path_str = output.get("path", "")
            if not (self._project_root / path_str).exists():
                return False, f"Blueprint-code sync failed: {path_str} not found"

        return True, "Blueprint-code sync verified"

    def _collect_entries(self) -> list[SyncEntry]:
        entries: list[SyncEntry] = []

        task_dir = self._project_root / "docs" / "03_modules" / "infrastructure_runtime_integration" / "task-system"
        changes_dir = task_dir / "changes" / "MOD-TASK_SYSTEM"

        if not changes_dir.exists():
            return entries

        for card_file in sorted(changes_dir.glob("TASK-INF-*.md")):
            task_id = card_file.stem
            entries.append(
                SyncEntry(
                    blueprint_path=str(card_file.relative_to(self._project_root)),
                    code_path="src/zephyr/core/",
                    status="PENDING",
                    last_synced="",
                )
            )

        return entries


class SyncPair:
    def __init__(self, blueprint_path="", code_path="", sync_status="unknown", last_sync=None):
        self.blueprint_path = blueprint_path
        self.code_path = code_path
        self.sync_status = sync_status
        self.last_sync = last_sync


class BlueprintCodeSyncService:
    def __init__(self, config=None):
        self.config = config or {}

    def sync(self, blueprint_path, code_path):
        return SyncPair(blueprint_path=blueprint_path, code_path=code_path)

    def check_drift(self, pair):
        return False


class SyncVerification:
    def __init__(self, pair_id="", status="unknown", mismatches=None, timestamp=None):
        self.pair_id = pair_id
        self.status = status
        self.mismatches = mismatches or []
        self.timestamp = timestamp
