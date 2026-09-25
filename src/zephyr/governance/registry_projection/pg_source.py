# [MODULE] zephyr.governance.registry_projection.pg_source
# [DOMAIN] D_GOV_CODE_QUALITY
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [TTL] permanent
# [DEPENDENCIES] zephyr.infrastructure.database_service (get_depgraph_conn read_only=True)；
#   zephyr.governance.registry_projection.model
# [CONSUMERS] zephyr.governance.registry_projection.generator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 生成器是 registry_snapshot 的只读消费方（乙号文 §2.4 四消费面②）；
#   只读连接（禁裸 psycopg2，DatabaseService 唯一真源）；PG 不可达/表未建 →
#   ProjectionUnavailable（调用方零写退出+降级观察行，绝不阻塞任何调用方）
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildB-20260923（W-M1 波0 车道B，接口以乙号文为准）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有失败归一为 ProjectionUnavailable（含缺表/连接失败/bundle 结构不符）
# [TESTS] tests/governance/registry_projection/test_projection_pg_source.py
"""pg_source.py — registry_snapshot 快照表只读消费 + bundle ⇄ 快照模型。

bundle JSON 契约（与车道乙对齐，jsonb 保序形态）::

    {"registry_id": str, "snapshot_version": int, "ledger_revision": int,
     "content_sha256": str, "header_lines": [str],
     "sections": [{"root_key": str, "entries": [[[key, value], ...], ...]}],
     "trailing_scalars": [[key, value], ...]}

条目=有序 [key, value] 对数组（jsonb 保序+重复键可表达）；value 递归同构。


# [ALGO_FLOW]
层: 只读消费
- 连接: DatabaseService 只读连接读 registry_snapshot 最新发布版
- 降级: 不可用/未建表 → ProjectionUnavailable（零阻塞）"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from zephyr.governance.registry_projection.model import ProjectionSnapshot, Section

__all__: Final = ["ProjectionUnavailable", "load_latest_snapshot", "snapshot_from_bundle"]


class ProjectionUnavailable(RuntimeError):
    """快照不可取（PG 宕机/缺表/registry 未入账本）——生成器零写退出方向。"""


_SCHEMA = "registry_ledger"


def snapshot_from_bundle(bundle: dict[str, object], physical_path: str) -> ProjectionSnapshot:
    try:
        sections = [
            Section(
                root_key=str(sec["root_key"]),
                entries=[[(str(k), v) for k, v in entry] for entry in sec["entries"]],
            )
            for sec in bundle["sections"]
        ]
        return ProjectionSnapshot(
            registry_id=str(bundle["registry_id"]),
            physical_path=physical_path,
            header_lines=[str(line) for line in bundle["header_lines"]],
            sections=sections,
            trailing_scalars=[(str(k), v) for k, v in bundle["trailing_scalars"]],
            ledger_revision=int(bundle.get("ledger_revision") or 0),
            snapshot_version=int(bundle.get("snapshot_version") or 0),
            content_sha256=str(bundle.get("content_sha256") or ""),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProjectionUnavailable(f"bundle 结构不符契约: {exc}") from exc


def load_latest_snapshot(registry_id: str, physical_path: str) -> ProjectionSnapshot:
    """读 registry_snapshot 最新发布版（read_only 连接；失败归一 ProjectionUnavailable）。"""
    try:
        from zephyr.infrastructure.database_service import DatabaseService

        conn = DatabaseService().get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT snapshot_version, manifest, bundle, content_sha256, entry_count "
                f"FROM {_SCHEMA}.registry_snapshot "
                f"WHERE registry_id = %s ORDER BY snapshot_version DESC LIMIT 1",
                (registry_id,),
            )
            row = cur.fetchone()
    except ProjectionUnavailable:
        raise
    except Exception as exc:  # noqa: BLE001 — PG 宕机/缺表/权限全归一
        raise ProjectionUnavailable(f"registry_snapshot 不可读: {type(exc).__name__}: {exc}") from exc
    if row is None:
        raise ProjectionUnavailable(f"registry_id={registry_id} 无已发布快照")
    bundle = row["bundle"] if isinstance(row.get("bundle"), dict) else json.loads(row["bundle"])
    snap = snapshot_from_bundle(bundle, physical_path)
    snap.content_sha256 = str(row.get("content_sha256") or snap.content_sha256)
    return snap


def snapshot_from_json_file(path: str | Path) -> ProjectionSnapshot:
    """JSON 文件源（影子期对账/红蓝测试/Phase-0 预览通道）。"""
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ProjectionUnavailable(f"快照 JSON 不可读: {exc}") from exc
    bundle = payload.get("bundle", payload)
    physical = str(payload.get("physical_path") or bundle.get("physical_path") or "")
    return snapshot_from_bundle(bundle, physical)
