# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] tests.ai_layer.heritage.test_heritage_snapshot
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.ai_layer.gen_heritage_dedup_snapshot（importlib 装载）; zephyr.ai_layer.heritage.store;
#                zephyr.ai_layer.intake.dedup (IntakeDedup)
# [CONSUMERS] pytest tests/ai_layer/heritage/test_heritage_snapshot.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 双临时 schema（ai_heritage_test_* + ai_intake_test_*），session 末 DROP，禁写生产路径;
#              幂等重刷：行数稳定 + refreshed_at 不回退; 只写 L7 family 行（他族行零触碰断言）;
#              baseline outbox 只发 elite|pattern 两 kind; dry-run 零写入
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.4
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] tests/ai_layer/heritage/test_heritage_snapshot.py
# [TTL] permanent
"""test_heritage_snapshot - L2 T4 快照生成器验收（DESIGN 施工项 3）。"""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from zephyr.ai_layer.heritage.store import HeritageDraft, HeritageStore

REPO = Path(__file__).resolve().parents[3]
STAMP = datetime(2026, 9, 23, tzinfo=UTC)


def _load_gen() -> object:
    spec = importlib.util.spec_from_file_location(
        "gen_heritage_snapshot_under_test", REPO / "scripts" / "ai_layer" / "gen_heritage_dedup_snapshot.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _pg_reachable() -> bool:
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        get_depgraph_pg_connection(read_only=True).cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001
        return False


needs_pg = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


def _store(schema: str, tmp_path: Path) -> HeritageStore:
    return HeritageStore(
        schema,
        state_dir=tmp_path / "state",
        domain_lookup=lambda domain: True,
        l4_hash_lookup=lambda exp: None,
    )


def _seed(store: HeritageStore) -> None:
    store.register(
        HeritageDraft(
            entry_kind="defect",
            title="快照面缺陷",
            plain_zh="构造缺陷模式用于 T4 快照面生成的集成验收样本文本内容",
            domain_id="tooling",
            source_kind="work_order",
            source_ref="WO-20260923-901",
            root_cause="快照构造根因",
            signature="sig-snapshot-alpha",
            recipe="快照构造配方内容与根因不同且长度差异超过二十个字符以上",
            pattern_norm="snapshot_seed_pattern",
            affected_surfaces=("src/x.py",),
            tool_id="t",
            scene="s",
        ),
        as_of=STAMP,
    )
    store.register(
        HeritageDraft(
            entry_kind="elite",
            title="快照面精英",
            plain_zh="构造精英档案用于 T4 快照面生成的集成验收样本文本内容",
            domain_id="governance",
            source_kind="l6_switch",
            source_ref="SW-20260923-901",
            surface="code_module",
            winner_ref="MOD-SNAP-1",
            diff_summary="快照构造差异档案：胜者与败者差异描述需要达到三十字以上防占位校验",
            evidence_ref="EX-20260918-abc",
            mechanism_family="detection",
        ),
        as_of=STAMP,
    )


@needs_pg
def test_refresh_idempotent_and_family_isolated(
    heritage_schema: str, intake_schema: str, tmp_path: Path
) -> None:
    gen = _load_gen()
    from zephyr.ai_layer.intake.dedup import IntakeDedup

    store = _store(heritage_schema, tmp_path)
    _seed(store)
    dedup = IntakeDedup(schema=intake_schema)
    conn = dedup._store.write_conn()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {intake_schema}.ai_intake_ref_snapshot (ref_family, ref_key, text_norm, simhash) "
        "VALUES ('chart', 'chart:keep', 'keepme', B'0011'::bit(64))"
    )
    conn.commit()

    summary1 = gen.refresh(store, dedup, state_dir=tmp_path / "state")
    assert summary1["faces"] == {"defect": 1, "elite": 1}
    assert summary1["baseline_events"] == 2, "只发 elite|pattern 两 kind"
    cur.execute(
        f"SELECT refreshed_at FROM {intake_schema}.ai_intake_ref_snapshot WHERE ref_family='chart'"
    )
    chart_before = cur.fetchone()[0]

    summary2 = gen.refresh(store, dedup, state_dir=tmp_path / "state")
    assert summary2["faces"] == summary1["faces"], "幂等重刷行数稳定"
    cur.execute(
        f"SELECT refreshed_at FROM {intake_schema}.ai_intake_ref_snapshot WHERE ref_family='chart'"
    )
    assert cur.fetchone()[0] == chart_before, "他族行零触碰"
    cur.execute(
        f"SELECT count(*) AS n FROM {intake_schema}.ai_intake_ref_snapshot WHERE ref_family='L7'"
    )
    assert cur.fetchone()[0] == 2
    outbox = (tmp_path / "state" / "baseline_events.jsonl").read_text(encoding="utf-8").splitlines()
    kinds = {json_kind for line in outbox if (json_kind := __import__("json").loads(line).get("kind"))}
    assert kinds == {"elite", "pattern"}, "红蓝 R1-B5：只发两 kind、不收阴性"
    assert store.dirty_since() is None, "刷新成功后清脏标记"


@needs_pg
def test_dry_run_writes_nothing(heritage_schema: str, intake_schema: str, tmp_path: Path) -> None:
    gen = _load_gen()
    from zephyr.ai_layer.intake.dedup import IntakeDedup

    store = _store(heritage_schema, tmp_path)
    _seed(store)
    dedup = IntakeDedup(schema=intake_schema)
    summary = gen.refresh(store, dedup, dry_run=True, state_dir=tmp_path / "state")
    assert summary["dry_run"] is True and "baseline_events" not in summary
    conn = dedup._store.read_conn()
    cur = conn.cursor()
    cur.execute(
        f"SELECT count(*) AS n FROM {intake_schema}.ai_intake_ref_snapshot WHERE ref_family='L7'"
    )
    row = cur.fetchone()
    assert (row[0] if isinstance(row, (list, tuple)) else row["n"]) == 0, "dry-run 零写入"


def test_dirty_marker_lifecycle(tmp_path: Path) -> None:
    store = _store("ai_heritage_test_marker", tmp_path)
    assert store.dirty_since() is None
    store.mark_snapshot_dirty("test")
    assert store.dirty_since() is not None
    store.clear_dirty_marker()
    assert store.dirty_since() is None
