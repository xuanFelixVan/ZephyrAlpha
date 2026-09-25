# [MODULE] tests.ai_layer.perceive.test_quota_sync
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""施工项 2 验收机检面：T5 与真源一致 / T5 直接写路径关闭（verify 漂移机检）/ 幂等。

两层断言（tests/ai_layer/intake/test_snapshot_regen.py 同款口径）：
1. 纯函数层（零 PG）：行派生/retired 墓碑保留/note 出生证；
2. DB 层（PG 可达才跑，不可达 skip 非 fail）：一次性临时 schema 两次同步幂等 + verify 漂移机检。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts" / "ai_layer" / "sync_ai_source_quota.py"


def _load_sync() -> ModuleType:
    spec = importlib.util.spec_from_file_location("sync_ai_source_quota_under_test", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _write_registry(path: Path, *, with_retired: bool = False) -> Path:
    sources = [
        {
            "slug": "src-active", "track": "github", "url": "https://example.com/a",
            "fetch": "监视", "frequency": "weekly", "daily_quota": 7,
            "health": "active", "last_verified": "2026-09-17", "basis": "桩",
        }
    ]
    if with_retired:
        sources.append(
            {
                "slug": "src-retired", "track": "academic", "url": "https://example.com/r",
                "fetch": "停扫", "frequency": "monthly", "daily_quota": 1,
                "health": "retired", "last_verified": "2026-09-17", "basis": "墓碑桩",
            }
        )
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "sources": sources,
                "longtail_candidates": [],
                "quota_governance": {"total_daily_cap": 40, "per_source_floor": 1, "demotion": {}},
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


def test_build_quota_rows_pure_layer(tmp_path: Path) -> None:
    sync = _load_sync()
    from zephyr.ai_layer.perceive.source_registry import load_source_registry

    registry = load_source_registry(_write_registry(tmp_path / "r.yaml", with_retired=True))
    rows = sync.build_quota_rows(registry)
    assert {r["source_slug"] for r in rows} == {"src-active", "src-retired"}
    active = next(r for r in rows if r["source_slug"] == "src-active")
    retired = next(r for r in rows if r["source_slug"] == "src-retired")
    # note=出生证：T5 直接写路径关闭的留痕面（真源指针+健康度+核验日）
    assert "read-only cache" in active["note"] and "config/ai_source_registry.yaml" in active["note"]
    assert "health=retired" in retired["note"]  # 墓碑保留同步（禁清零，quota=1 底线）
    assert retired["daily_quota"] == 1
    assert active["daily_quota"] == 7 and active["track"] == "github"


def test_real_registry_rows_count_matches_truth() -> None:
    sync = _load_sync()
    from zephyr.ai_layer.perceive.source_registry import load_source_registry

    rows = sync.build_quota_rows(load_source_registry())
    assert len(rows) == 12
    assert sum(r["daily_quota"] for r in rows) > 0


# ────────────────────────── DB 层（PG 可达才跑） ──────────────────────────


def _pg_reachable() -> bool:
    try:
        from zephyr.infrastructure.database_service import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001  可达性探测，skip 而非假绿
        return False


PG_SKIP = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


@PG_SKIP
def test_sync_idempotent_and_verify_zero_drift(test_schema: str, tmp_path: Path) -> None:
    """验收原文：T5 与真源一致；幂等（两次同步行内容逐位一致，updated_at 除外）。"""
    sync = _load_sync()
    from zephyr.infrastructure.database_service import get_depgraph_pg_connection

    registry_path = _write_registry(tmp_path / "r.yaml", with_retired=True)
    first = sync.sync(test_schema, registry_path)
    assert first["synced"] == 2
    conn = get_depgraph_pg_connection(read_only=True)
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT source_slug, track, daily_quota, note FROM {test_schema}.ai_intake_source_quota "
            "ORDER BY source_slug"
        )
        after_first = cur.fetchall()
    sync.sync(test_schema, registry_path)
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT source_slug, track, daily_quota, note FROM {test_schema}.ai_intake_source_quota "
            "ORDER BY source_slug"
        )
        after_second = cur.fetchall()
    assert after_first == after_second  # 幂等：逐位一致
    assert sync.verify(test_schema, registry_path) == []  # T5 与真源一致


@PG_SKIP
def test_verify_detects_drift_and_extra_row(test_schema: str, tmp_path: Path) -> None:
    """验收原文：T5 直接写路径关闭——任何旁路写入被 verify 判 drift（退出码 3 的机检面）。"""
    sync = _load_sync()
    from zephyr.infrastructure.database_service import get_depgraph_pg_connection

    # 用例隔离：session 级临时 schema 跨用例共享，先清表防前用例残留判 drift
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {test_schema}.ai_intake_source_quota")
    registry_path = _write_registry(tmp_path / "r.yaml")
    sync.sync(test_schema, registry_path)
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    # 旁路篡改配额
    with conn.cursor() as cur:
        cur.execute(
            f"UPDATE {test_schema}.ai_intake_source_quota SET daily_quota = 99 "
            "WHERE source_slug = 'src-active'"
        )
    drift = sync.verify(test_schema, registry_path)
    assert any(d.startswith("mismatch:src-active") for d in drift)
    # 旁路插入真源没有的行
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO {test_schema}.ai_intake_source_quota (source_slug, track, daily_quota) "
            "VALUES ('ghost-src', 'github', 5)"
        )
    drift = sync.verify(test_schema, registry_path)
    assert "t5_extra:ghost-src" in drift
    # 再同步恢复一致（幂等收敛；墓碑行不删除，ghost 行由人工裁决）
    sync.sync(test_schema, registry_path)
    remaining = sync.verify(test_schema, registry_path)
    assert remaining == ["t5_extra:ghost-src"]


@PG_SKIP
def test_cli_verify_exit_code_3_on_drift(test_schema: str, tmp_path: Path) -> None:
    sync = _load_sync()
    from zephyr.infrastructure.database_service import get_depgraph_pg_connection

    # 用例隔离：清掉前用例残留（ghost-src 等）再断言退出码
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {test_schema}.ai_intake_source_quota")
    registry_path = _write_registry(tmp_path / "r.yaml")
    assert sync.main(["--schema", test_schema, "--registry", str(registry_path)]) == 0
    assert sync.main(["--schema", test_schema, "--registry", str(registry_path), "--verify"]) == 0
    # 篡改后 CLI --verify 必须退出码 3
    with conn.cursor() as cur:
        cur.execute(
            f"UPDATE {test_schema}.ai_intake_source_quota SET daily_quota = 42 "
            "WHERE source_slug = 'src-active'"
        )
    assert sync.main(["--schema", test_schema, "--registry", str(registry_path), "--verify"]) == 3
