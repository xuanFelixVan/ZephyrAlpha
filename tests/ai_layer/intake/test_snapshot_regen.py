# [MODULE] tests.ai_layer.intake.test_snapshot_regen
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""gen_intake_ref_snapshots 幂等重跑断言（复审 P2-d / P1 施工方案批次 3 顺带项）。

两层断言（测试禁写生产路径铁律下的可行口径）：
1. 纯函数层（零 PG 依赖）：build_family 连续两次抽取逐位一致（含顺序）——
   只读生产注册表 YAML 与 src 标记行，零写入；
2. DB 层（PG 可达才跑，PG 不可达=pytest.skip 非 fail）：refresh 两次真实 upsert
   落 conftest 一次性临时 schema（ai_intake_test_aibase，session 结束 DROP），
   断言两次表内容逐位一致——refreshed_at 按设计每次刷新（ON CONFLICT DO UPDATE），
   不在幂等断言域，其余四列（ref_family/ref_key/text_norm/simhash）逐位比对。
生成器对生产 schema（ai_intake）零接触。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

GEN_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "ai_layer" / "gen_intake_ref_snapshots.py"


def _pg_reachable() -> bool:
    """PG 可达性探测（与同目录 conftest.pg_reachable 同款判定；任何异常都判不可达）。"""
    try:
        from zephyr.infrastructure.database_service import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001  可达性探测，skip 而非假绿
        return False


PG_OK = _pg_reachable()


def _load_gen() -> ModuleType:
    """按路径装载生成器脚本（scripts/ 无包结构，conftest 装载 DDL 同款先例）。"""
    spec = importlib.util.spec_from_file_location("gen_intake_ref_snapshots_under_test", GEN_SCRIPT)
    assert spec and spec.loader, f"无法装载生成器: {GEN_SCRIPT}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# ────────────────────────── 纯函数层幂等（零 PG） ──────────────────────────


def test_build_family_idempotent_pure() -> None:
    gen = _load_gen()
    for family in gen.GENERATED_FAMILIES:
        first, skipped_first = gen.build_family(family)
        second, skipped_second = gen.build_family(family)
        assert first == second, f"{family} 面两次抽取不逐位一致"
        assert skipped_first == skipped_second
        assert first, f"{family} 面不应为空"
        keys = [key for key, _text in first]
        assert len(keys) == len(set(keys)), f"{family} 面 ref_key 应唯一"


def test_module_constants_contract() -> None:
    # 不经 refresh()（其无条件构造 IntakeDedup，属 DB 依赖）——常量契约用纯常量断言
    gen = _load_gen()
    assert gen.GENERATED_FAMILIES == ("chart", "indicator", "algo_flow")
    assert set(gen.COLLECTORS) == set(gen.GENERATED_FAMILIES)


# ────────────────────────── DB 层幂等（PG gated，临时 schema） ──────────────────────────


def _dump_ref_snapshot(schema: str) -> list[tuple[str, str, str, str]]:
    from zephyr.infrastructure.database_service import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(
        f"SELECT ref_family, ref_key, text_norm, simhash::text "
        f"FROM {schema}.ai_intake_ref_snapshot ORDER BY ref_family, ref_key"
    )
    return [tuple(row) for row in cur.fetchall()]


@pytest.mark.skipif(not PG_OK, reason="PostgreSQL 不可达（skip 而非假绿）")
def test_refresh_twice_idempotent_on_test_schema(test_schema: str) -> None:
    gen = _load_gen()

    # dry-run 两次：抽取计数逐位一致（零写入路径）
    dry1 = gen.refresh(gen.GENERATED_FAMILIES, schema=test_schema, dry_run=True)
    dry2 = gen.refresh(gen.GENERATED_FAMILIES, schema=test_schema, dry_run=True)
    assert dry1["families"] == dry2["families"]

    # 真实 upsert 两次：表内容逐位一致（refreshed_at 按设计刷新，不在断言域）
    summary1 = gen.refresh(gen.GENERATED_FAMILIES, schema=test_schema)
    rows1 = _dump_ref_snapshot(test_schema)
    summary2 = gen.refresh(gen.GENERATED_FAMILIES, schema=test_schema)
    rows2 = _dump_ref_snapshot(test_schema)

    assert rows1, "快照面不应为空"
    assert rows1 == rows2, "两次 refresh 后登记不逐位一致（幂等破坏）"
    for family in gen.GENERATED_FAMILIES:
        assert summary1["families"][family]["rows"] == summary2["families"][family]["rows"] > 0
    dumped_families = {row[0] for row in rows1}
    assert dumped_families == set(gen.GENERATED_FAMILIES)
