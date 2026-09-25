# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] tests.ai_layer.heritage.test_heritage_forget
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.heritage.forget; zephyr.ai_layer.heritage.store
# [CONSUMERS] pytest tests/ai_layer/heritage/test_heritage_forget.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 构造数据触发三类降级各 1 例（plan_* 纯函数，as_of 注入）；零物理删除=源码扫描断言；
#              compressed 可反查（DB 用例）；surface 判定保守（None=保留）；报告/轻事件落 tmp_path
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.8（D-L7-05）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；非法流转 RuntimeError fail-closed
# [TESTS] tests/ai_layer/heritage/test_heritage_forget.py
# [TTL] permanent
"""test_heritage_forget - 遗忘执行器验收（DESIGN 施工项 7）。"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from zephyr.ai_layer.heritage.forget import (
    HeritageForget,
    default_surface_alive,
    plan_criteria,
    plan_defect,
    plan_elite,
)
from zephyr.ai_layer.heritage.policy import load_policy
from zephyr.ai_layer.heritage.store import HeritageDraft, HeritageStore

POLICY = load_policy()
AS_OF = datetime(2026, 9, 23, tzinfo=UTC)
OLD = AS_OF - timedelta(days=400)
RECENT = AS_OF - timedelta(days=10)


def test_plan_defect_three_routes() -> None:
    rows = [
        {"entry_id": "HT-1", "status": "active", "affected_surfaces": ["src/gone.py", "src/gone2.py"],
         "last_seen": OLD, "last_hit_at": OLD},
        {"entry_id": "HT-2", "status": "active", "affected_surfaces": ["src/alive.py"],
         "last_seen": RECENT, "last_hit_at": None},
        {"entry_id": "HT-3", "status": "active", "affected_surfaces": ["src/maybe.py"],
         "last_seen": RECENT, "last_hit_at": None},
        {"entry_id": "HT-4", "status": "retired", "affected_surfaces": ["src/gone.py"],
         "last_seen": OLD, "last_hit_at": OLD},
        {"entry_id": "HT-5", "status": "retired", "affected_surfaces": ["src/gone.py"],
         "last_seen": RECENT, "last_hit_at": RECENT},
    ]
    surfaces = {"src/gone.py": False, "src/gone2.py": False, "src/alive.py": True, "src/maybe.py": None}
    decisions = plan_defect(rows, surfaces, POLICY, as_of=AS_OF)
    by_id = {d.entry_id: d for d in decisions}
    assert by_id["HT-1"].to_status == "retired", "受影响面全部退役→retired 墓碑"
    assert by_id["HT-4"].to_status == "compressed", "retired 且 4 季度零新案零 hit→compressed"
    assert set(by_id) == {"HT-1", "HT-4"}, "活面/未知面/近期 retired 全保留（保守）"


def test_plan_elite_top3_and_absorption() -> None:
    rows = [
        {"entry_id": "HT-E1", "status": "active", "rank_in_cell": 4, "updated_at": RECENT},
        {"entry_id": "HT-E2", "status": "active", "rank_in_cell": 1, "updated_at": RECENT},
        {"entry_id": "HT-E3", "status": "archived", "updated_at": OLD},
        {"entry_id": "HT-E4", "status": "archived", "updated_at": RECENT},
        {"entry_id": "HT-E5", "status": "archived", "updated_at": OLD},
    ]
    has_descendant = {"HT-E3"}
    decisions = plan_elite(rows, has_descendant, POLICY, as_of=AS_OF)
    by_id = {d.entry_id: d for d in decisions}
    assert by_id["HT-E1"].to_status == "archived", "格内跌出 top3→archived"
    assert by_id["HT-E3"].to_status == "compressed", "archived 满 12 个月且被后代吸收→compressed"
    assert set(by_id) == {"HT-E1", "HT-E3"}, "未满期/无后代/名次内全保留"


def test_plan_criteria_invalidate_and_venue_overflow() -> None:
    rows = [
        {"entry_id": "HT-C1", "status": "active", "still_valid": False, "venue_rank": 1},
        {"entry_id": "HT-C2", "status": "active", "still_valid": True, "venue_rank": 5},
        {"entry_id": "HT-C3", "status": "archived", "still_valid": False, "venue_rank": 5},
        {"entry_id": "HT-C4", "status": "archived", "still_valid": False, "venue_rank": 2},
    ]
    decisions = plan_criteria(rows, POLICY, as_of=AS_OF)
    by_id = {d.entry_id: d for d in decisions}
    assert by_id["HT-C1"].to_status == "archived", "判据翻案（still_valid=false）→archived"
    assert by_id["HT-C3"].to_status == "compressed", "archived 且 venue 跌出最近 3 代→compressed"
    assert set(by_id) == {"HT-C1", "HT-C3"}, "still_valid=true 全保留（防重复考古燃料）"


def test_default_surface_alive_conservative() -> None:
    assert default_surface_alive("src/definitely_missing_xyz_12345.py") is False
    assert default_surface_alive("src/zephyr/ai_layer/heritage/store.py") is True
    assert default_surface_alive("GATE-SOME-ID") is None, "不可解析=不可判定（保守保留）"
    assert default_surface_alive("") is None


def test_zero_physical_delete_source_scan() -> None:
    """零物理删除红线：heritage 包源码无 SQL 物理删除语句（模板/字面量两形态，DESIGN §2.8）。"""
    src_dir = Path(__file__).resolve().parents[3] / "src" / "zephyr" / "ai_layer" / "heritage"
    for py in src_dir.glob("*.py"):
        text = py.read_text(encoding="utf-8").upper()
        assert "DELETE FROM {" not in text, f"{py.name} 出现模板形态物理删除"
        assert "DELETE FROM AI_HERITAGE" not in text, f"{py.name} 出现字面形态物理删除"


def _pg_reachable() -> bool:
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        get_depgraph_pg_connection(read_only=True).cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001
        return False


needs_pg = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


def _draft_defect(surface: str) -> HeritageDraft:
    return HeritageDraft(
        entry_kind="defect",
        title="构造遗忘用缺陷",
        plain_zh="构造数据用于触发缺陷模式降级判据的集成验收样例文本",
        domain_id="tooling",
        source_kind="work_order",
        source_ref="WO-20260923-900",
        root_cause="构造根因甲",
        signature="sig-construct-alpha",
        recipe="构造配方内容与根因完全不同且长度差异超过二十个字符以上",
        pattern_norm=f"construct_pattern_{abs(hash(surface)) % 10000:04d}",
        affected_surfaces=(surface,),
        tool_id="t",
        scene="s",
    )


@needs_pg
def test_run_monthly_executes_defect_retirement(heritage_schema: str, tmp_path: Path) -> None:
    store = HeritageStore(
        heritage_schema,
        state_dir=tmp_path / "state",
        domain_lookup=lambda domain: True,
        l4_hash_lookup=lambda exp: None,
    )
    eid = store.register(_draft_defect("src/definitely_gone_xyz.py"), as_of=RECENT)
    forgetter = HeritageForget(
        store,
        state_dir=tmp_path / "state",
        surface_alive=lambda ref: False,
        policy=POLICY,
    )
    report = forgetter.run_monthly(as_of=AS_OF, execute=True)
    executed_ids = {row["entry_id"] for row in report["executed"]}
    assert eid in executed_ids, "构造数据触发缺陷降级 1 例（受影响面全退役）"
    assert store.status_of(eid) == "retired"
    events_file = tmp_path / "state" / "forget_events.jsonl"
    assert events_file.exists(), "heritage_forget_due 轻事件落盘"
    assert (tmp_path / "state" / f"forget_report-{AS_OF.strftime('%Y-%m')}.json").exists()


@needs_pg
def test_run_monthly_elite_rank_demotion(heritage_schema: str, tmp_path: Path) -> None:
    store = HeritageStore(
        heritage_schema,
        state_dir=tmp_path / "state2",
        domain_lookup=lambda domain: True,
        l4_hash_lookup=lambda exp: None,
    )
    ids = []
    for i in range(4):
        draft = HeritageDraft(
            entry_kind="elite",
            title=f"构造精英 {i}",
            plain_zh="构造数据用于触发精英格内名次降级判据的集成验收样本文本",
            domain_id="trading_algo",
            source_kind="l6_switch",
            source_ref=f"SW-2026092{i}-900",
            surface="code_module",
            winner_ref=f"MOD-C-{i}",
            diff_summary="构造差异档案：胜者与败者的差异描述需要达到三十字以上防占位校验通过线",
            evidence_ref="EX-20260918-abc",
            score_summary={"score": 1.0 - i * 0.1},
            mechanism_family="ranking",
        )
        ids.append(store.register(draft, as_of=RECENT))
    forgetter = HeritageForget(store, state_dir=tmp_path / "state2", policy=POLICY)
    report = forgetter.run_monthly(as_of=AS_OF, execute=True)
    demoted = {row["entry_id"] for row in report["executed"] if row["to"] == "archived"}
    assert ids[3] in demoted, "同格第 4 名跌出 top3→archived"
    assert ids[0] not in demoted, "top3 保留"


@needs_pg
def test_compressed_remains_queryable_after_transition(heritage_schema: str, tmp_path: Path) -> None:
    store = HeritageStore(
        heritage_schema,
        state_dir=tmp_path / "state3",
        domain_lookup=lambda domain: True,
        l4_hash_lookup=lambda exp: None,
    )
    eid = store.register(_draft_defect("src/another_gone.py"), as_of=RECENT)
    store.transition_status(eid, "retired")
    store.transition_status(eid, "compressed")
    entry = store.get(eid)
    assert entry is not None and entry["status"] == "compressed", "compressed 条目 10 年内可反查全量"
    assert store.retention_horizon().days == 3650
