# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [MODULE] scripts.ai_layer.sync_ai_source_quota
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.perceive.source_registry (load_source_registry);
#                zephyr.infrastructure.database_service (get_depgraph_pg_connection, 经 DatabaseService 唯一通道)
# [CONSUMERS] CLI python scripts/ai_layer/sync_ai_source_quota.py [--schema ai_intake] [--verify] [--dry-run];
#             L2 入库闸 gate.py 配额闸（读 T5——本器是 T5 唯一合法写路径）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 配额真源=config/ai_source_registry.yaml（L1 DESIGN §2.1），T5=只读缓存（L2 DESIGN §2.2 T5
#              过渡裁定：L1 落地后降级只读缓存，生成器同步）; 本 CLI 是 T5 唯一合法写路径（直接写路径关闭：
#              每行 note 钉"read-only cache"出生证 + --verify 漂移机检，任何旁路写入会被 verify 判 drift）;
#              幂等（ON CONFLICT DO UPDATE，重跑两次行内容一致，updated_at 除外）;
#              墓碑不删除：T5 中真源已不存在的行不 DELETE，只由 --verify 报 t5_extra drift（人工裁决）;
#              降级修订（贫矿减半/quota=1）改真源 YAML 后经本器落地，本器不做降级计算（RULE-SSOT）;
#              全部读写经 DatabaseService/depgraph 通道，禁裸连接
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L1_perceive/DESIGN.md §2.1（配额治理三闸）;
#                docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.2 T5（只读缓存裁定）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源缺文件/结构不合规→SourceRegistryError 上抛退出码 2（fail-closed，绝不同步半截面）;
#                  PG 不可达→退出码 2; --verify 发现漂移→退出码 3 并列 drift 清单（真源缺行/字段不符/T5 多余行）;
#                  --dry-run 零写入（只打印将同步的行）
# [TESTS] tests/ai_layer/perceive/test_quota_sync.py（纯函数层：行派生/retired 墓碑保留/note 出生证/
#         --dry-run 零写；PG 层（可达才跑，不可达 skip）：临时 schema 两次同步幂等逐位一致/
#         verify 一致零漂移/篡改 T5 后 verify 报 drift/T5 多余行报 t5_extra）
"""sync_ai_source_quota — 配额缓存同步器：源注册表 YAML → L2 T5 `ai_intake_source_quota`（施工项 2）。

设计真源：``docs/_working/ai_layer_vision/L1_perceive/DESIGN.md`` §2.1（配额真源三闸）+
``docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md`` §2.2 T5（过渡件降级只读缓存裁定）。

方向只有一个：YAML → T5。T5 的直接写路径自本器落地起关闭——写配额改
``config/ai_source_registry.yaml``，再跑本器同步；旁路写入会被 ``--verify`` 判 drift（退出码 3）。

用法::

    python scripts/ai_layer/sync_ai_source_quota.py --dry-run   # 只看将同步的行
    python scripts/ai_layer/sync_ai_source_quota.py             # 全量同步（幂等）
    python scripts/ai_layer/sync_ai_source_quota.py --verify    # 只核对 T5 与真源一致性
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.ai_layer.perceive.source_registry import (  # noqa: E402
    DEFAULT_REGISTRY_PATH,
    SourceRegistry,
    load_source_registry,
)

log = logging.getLogger("ai_perceive.quota_sync")

DEFAULT_SCHEMA: Final = "ai_intake"
EXIT_OK: Final = 0
EXIT_ERROR: Final = 2
EXIT_DRIFT: Final = 3
NOTE_STAMP: Final = "read-only cache; truth=config/ai_source_registry.yaml (REG-AISRC-001)"


def build_quota_rows(registry: SourceRegistry) -> list[dict[str, Any]]:
    """真源 → T5 行派生（纯函数；retired 墓碑保留同步，配额取真源值禁清零）。"""
    rows: list[dict[str, Any]] = []
    for source in registry.sources:
        rows.append(
            {
                "source_slug": source.slug,
                "track": source.track,
                "daily_quota": max(int(source.daily_quota), registry.per_source_floor),
                "note": f"{NOTE_STAMP}; health={source.health}; verified={source.last_verified}",
            }
        )
    return rows


def _upsert_sql(schema: str) -> str:
    return (
        f"INSERT INTO {schema}.ai_intake_source_quota "  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
        "(source_slug, track, daily_quota, note, updated_at) "
        "VALUES (%s, %s, %s, %s, now()) "
        "ON CONFLICT (source_slug) DO UPDATE SET "  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
        "track = EXCLUDED.track, daily_quota = EXCLUDED.daily_quota, "
        "note = EXCLUDED.note, updated_at = now()"
    )


def sync(
    schema: str = DEFAULT_SCHEMA,
    registry_path: Path | str | None = None,
    conn: Any | None = None,
) -> dict[str, Any]:
    """全量同步（幂等 upsert）；conn 可注入（测试用临时 schema），缺省走 depgraph 通道。"""
    registry = load_source_registry(registry_path)
    rows = build_quota_rows(registry)
    if conn is None:
        from zephyr.infrastructure.database_service import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                _upsert_sql(schema),
                (row["source_slug"], row["track"], row["daily_quota"], row["note"]),
            )
    log.info("配额缓存同步完成: schema=%s 行数=%d", schema, len(rows))
    return {"synced": len(rows), "schema": schema, "total_daily_cap": registry.total_daily_cap}


def verify(
    schema: str = DEFAULT_SCHEMA,
    registry_path: Path | str | None = None,
    conn: Any | None = None,
) -> list[str]:
    """T5 ↔ 真源一致性核对，返回 drift 清单（空=一致）。"""
    registry = load_source_registry(registry_path)
    expected = {row["source_slug"]: row for row in build_quota_rows(registry)}
    if conn is None:
        from zephyr.infrastructure.database_service import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT source_slug, track, daily_quota FROM {schema}.ai_intake_source_quota"  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
        )
        actual = {r[0]: (r[1], int(r[2])) for r in cur.fetchall()}
    drift: list[str] = []
    for slug, row in expected.items():
        if slug not in actual:
            drift.append(f"missing_in_t5:{slug}")
        elif actual[slug] != (row["track"], row["daily_quota"]):
            drift.append(f"mismatch:{slug}: t5={actual[slug]} truth=({row['track']}, {row['daily_quota']})")
    for slug in actual:
        if slug not in expected:
            drift.append(f"t5_extra:{slug}")
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="源注册表 → T5 配额只读缓存同步器")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="目标 schema（默认 ai_intake）")
    parser.add_argument("--registry", default=None, help="真源 YAML 路径（默认 config/ai_source_registry.yaml）")
    parser.add_argument("--verify", action="store_true", help="只核对一致性不同步")
    parser.add_argument("--dry-run", action="store_true", help="只打印将同步的行，零写入")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        if args.dry_run:
            registry = load_source_registry(args.registry)
            for row in build_quota_rows(registry):
                print(f"{row['source_slug']}\t{row['track']}\tquota={row['daily_quota']}")
            print(f"总量闸={registry.total_daily_cap}/日；dry-run 零写入")
            return EXIT_OK
        if args.verify:
            drift = verify(args.schema, args.registry)
            if drift:
                for line in drift:
                    print(f"DRIFT {line}")
                print(f"--verify 漂移 {len(drift)} 条", file=sys.stderr)
                return EXIT_DRIFT
            print("T5 与真源一致（零漂移）")
            return EXIT_OK
        result = sync(args.schema, args.registry)
        print(f"同步完成: {result}")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001——CLI 边界统一 fail-closed 退出码 2
        print(f"ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班/人工点火, 非自动常驻任务
    raise SystemExit(main())
