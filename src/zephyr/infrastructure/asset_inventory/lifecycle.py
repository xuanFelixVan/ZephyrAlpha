# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.lifecycle
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.gov_audit.writer
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-026 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AssetLifecycle — MOD-INF-026 L5 ITIL生命周期自动化管理器

蓝图 §3.5 + §22：三条自动化规则（TIME-DECAY / ZERO-REF / DIR-CONVENTION）
从 active -> stale -> deprecated -> archived 全自动生命周期管理。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: decay_days 参数
#   fields: 参数 decay_days（无注解）
#   code: lifecycle.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: root 参数
#   fields: 参数 root（无注解）
#   code: lifecycle.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① Lifecycle
#   name_en: Lifecycle
#   intro: ITIL 生命周期自动化管理器——Phase 1 实现（蓝图 §3.5）。
#   desc: ITIL 生命周期自动化管理器——Phase 1 实现（蓝图 §3.5）。；公共方法（定义序）: evaluate, main；源码 L93-L256
#   inputs: decay_days root
#   outputs: 返回值
# - id: A2
#   name_zh: ② main
#   name_en: main
#   intro: main() 源码 L265-L266
#   desc: 源码 L265-L266
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: Lifecycle, main
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

from zephyr.infrastructure.asset_inventory.models import (
    AssetLifecycleEvent,
    AssetStatus,
    AssetType,
    ClassifiedAsset,
    Priority,
    UnifiedAssetIndex,
)
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

DEFAULT_DECAY_DAYS: dict[AssetType, int] = {
    AssetType.MODULE: 360,
    AssetType.SCRIPT: 180,
    AssetType.GATE: 360,
    AssetType.DOC: 365,
    AssetType.CONFIG: 90,
    AssetType.TEST: 180,
    AssetType.DATA: 30,
    AssetType.REGISTRY: 365,
    AssetType.UNKNOWN: 180,
}


class Lifecycle:
    """ITIL 生命周期自动化管理器——Phase 1 实现（蓝图 §3.5）。"""

    def __init__(
        self,
        decay_days: dict[AssetType, int] | None = None,
        root: Path | None = None,
    ) -> None:
        self.decay_days = decay_days or DEFAULT_DECAY_DAYS
        self.root = root or REPO_ROOT

    def evaluate(self, index: UnifiedAssetIndex) -> tuple[list[AssetLifecycleEvent], UnifiedAssetIndex]:
        now = datetime.now(UTC)
        events: list[AssetLifecycleEvent] = []
        updated_assets: list[ClassifiedAsset] = []

        for asset in index.assets:
            asset_events = self._evaluate_one(asset, now, index)
            if asset_events:
                events.extend(asset_events)
                last_event = asset_events[-1]
                asset.status = last_event.to_status
            updated_assets.append(asset)

        new_index = index.model_copy(update={"assets": updated_assets})
        return events, new_index

    def _evaluate_one(
        self, asset: ClassifiedAsset, now: datetime, index: UnifiedAssetIndex
    ) -> list[AssetLifecycleEvent]:
        events: list[AssetLifecycleEvent] = []
        triggered_by: list[str] = []

        event = self._check_time_decay(asset, now)
        if event:
            events.append(event)
            triggered_by.append("TIME-DECAY")

        event = self._check_zero_ref(asset, index)
        if event:
            events.append(event)
            triggered_by.append("ZERO-REF")

        event = self._check_dir_convention(asset)
        if event:
            events.append(event)
            triggered_by.append("DIR-CONVENTION")

        return events

    def _check_time_decay(self, asset: ClassifiedAsset, now: datetime) -> AssetLifecycleEvent | None:
        if asset.status not in (AssetStatus.ACTIVE, AssetStatus.STALE):
            return None

        max_days = self.decay_days.get(asset.asset_type, 180)
        mtime = asset.mtime_utc

        if mtime.tzinfo is None:
            mtime = mtime.replace(tzinfo=UTC)

        age = now - mtime

        if age > timedelta(days=max_days * 2) and asset.status is AssetStatus.STALE:
            return AssetLifecycleEvent(
                event_id=_generate_event_id(),
                event_type="TIME_DECAY",
                asset_path=asset.relative_path,
                from_status=AssetStatus.STALE,
                to_status=AssetStatus.DEPRECATED,
                rule_detail=f"最后修改 {age.days} 天前，超过 {max_days * 2} 天",
            )
        if age > timedelta(days=max_days) and asset.status is AssetStatus.ACTIVE:
            return AssetLifecycleEvent(
                event_id=_generate_event_id(),
                event_type="TIME_DECAY",
                asset_path=asset.relative_path,
                from_status=AssetStatus.ACTIVE,
                to_status=AssetStatus.STALE,
                rule_detail=f"最后修改 {age.days} 天前，超过 {max_days} 天",
            )
        return None

    def _check_zero_ref(self, asset: ClassifiedAsset, index: UnifiedAssetIndex) -> AssetLifecycleEvent | None:
        if asset.priority is Priority.P0:
            return None
        if asset.status in (AssetStatus.DEPRECATED, AssetStatus.ARCHIVED):
            return None

        if not asset.registered_in and asset.asset_type not in (AssetType.REGISTRY,):
            return AssetLifecycleEvent(
                event_id=_generate_event_id(),
                event_type="ZERO_REF",
                asset_path=asset.relative_path,
                from_status=asset.status,
                to_status=AssetStatus.DEPRECATED,
                rule_detail=f"{asset.asset_type.value} 未在任何注册表登记，建议废弃",
            )
        return None

    def _check_dir_convention(self, asset: ClassifiedAsset) -> AssetLifecycleEvent | None:
        path = asset.relative_path
        if "/_deprecated/" in path and asset.status is not AssetStatus.DEPRECATED:
            return AssetLifecycleEvent(
                event_id=_generate_event_id(),
                event_type="DIR_CONVENTION",
                asset_path=path,
                from_status=asset.status,
                to_status=AssetStatus.DEPRECATED,
                rule_detail="文件位于 _deprecated/ 目录",
            )
        if "/_archived/" in path and asset.status is not AssetStatus.ARCHIVED:
            return AssetLifecycleEvent(
                event_id=_generate_event_id(),
                event_type="DIR_CONVENTION",
                asset_path=path,
                from_status=asset.status,
                to_status=AssetStatus.ARCHIVED,
                rule_detail="文件位于 _archived/ 目录",
            )
        return None

    def _write_audit_events(self, events: list[AssetLifecycleEvent]) -> None:
        if not events:
            return
        try:
            from zephyr.gov_audit.writer import AuditWriter

            writer = AuditWriter()
            for evt in events:
                writer.write(
                    {
                        "event_type": "lifecycle_state_change",
                        "agent_id": "asset-inventory",
                        "session_id": "auto",
                        "target_path": evt.asset_path,
                        "operation": evt.event_type,
                        "status": f"{evt.from_status.value}->{evt.to_status.value}",
                        "payload": {
                            "from_status": evt.from_status.value,
                            "to_status": evt.to_status.value,
                            "rule_detail": evt.rule_detail,
                        },
                        "provenance": "automated",
                        "metadata": {"event_id": evt.event_id},
                    }
                )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in lifecycle", exc_info=True)

    def main(self) -> None:
        index_path = self.root / "data" / "asset_index" / "unified-asset-index.yaml"
        if not index_path.exists():
            print("警告: 索引文件不存在")
            return

        import yaml

        raw = yaml.safe_load(index_path.read_text(encoding="utf-8"))
        index = UnifiedAssetIndex(**raw)
        events, new_index = self.evaluate(index)

        print(f"  LIFECYCLE   {len(events)} 个生命周期变更")
        for e in events:
            print(f"    {e.event_type:18s}  {e.asset_path:50s}  {e.from_status.value:10s} -> {e.to_status.value:10s}")


def _generate_event_id() -> str:
    now = datetime.now(UTC)
    seq = str(now.timestamp()).replace(".", "")[-4:]
    return f"LCEVT-{now.strftime('%Y%m%d')}-{seq}"


def main() -> None:
    Lifecycle().main()


if __name__ == "__main__":
    main()
