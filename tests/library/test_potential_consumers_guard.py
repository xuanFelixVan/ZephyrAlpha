# [A_test] module_id: MOD-LIB-001 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LIB-001 | docs/03_modules/_domain_library/blueprint.md | §1
# [MODULE] tests.library.test_potential_consumers_guard
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-LIB-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_potential_consumers_guard.py — 供数反查轴（potential_consumers）守卫回归（总筹裁-07）。

背景：09-24~27 三轮全量 ingest 把 #410② 回填 68 资产的供数轴清零。根因链：
①952a827db6 窗口 Python `or []` 把缺省变显式空数组；②1e9b34999d 的 VALUES
COALESCE(%s::text[], '{}') 在 INSERT 求值期把 NULL 预空成 '{}'，冲突分支引用
EXCLUDED 的守卫恒失效。本文件锁死三层回归：
- 结构层（零 DB）：冲突分支必须引用裸参数 %s，禁现 EXCLUDED.potential_consumers
- 参数层（零 DB）：act/register_batch 15 占位、potential_consumers 传两次
- 语义层（pg_db 独立测试 PG，ZEPHYR_TEST_PG=1 激活；未配置即 skip，零生产触碰）：
  register None 保留存量 / 显式 [] 清空 / 全量 ingest 缩水守卫触发
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.library.library_regen_reconciler as g  # noqa: E402
from zephyr.library.collectors import ingest_all  # noqa: E402
from zephyr.library.ledger_schema import _SQL_UPSERT_ASSET  # noqa: E402
from zephyr.library.librarian import Librarian  # noqa: E402


# ── 结构层（零 DB，本缺陷类的最小锁定断言）───────────────────────────────────
def test_conflict_branch_references_raw_param_not_excluded() -> None:
    """冲突分支必须引用裸参数（VALUES COALESCE 已预空 EXCLUDED，引用它=守卫失效）。"""
    conflict_clause = _SQL_UPSERT_ASSET.split("ON CONFLICT", 1)[1]
    assert "potential_consumers = COALESCE(%s::text[], lib_assets.potential_consumers)" in conflict_clause
    # 本次事故的最小反证断言：EXCLUDED 形态=09-24~27 清零根因，禁回归
    assert "EXCLUDED.potential_consumers" not in conflict_clause
    assert _SQL_UPSERT_ASSET.count("%s") == 15


# ── 参数层（零 DB，recording conn 数占位）────────────────────────────────────
class _RecordingCur:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def __enter__(self) -> _RecordingCur:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def execute(self, sql: object, *args: object) -> None:
        self.calls.append((sql, args))

    def fetchone(self) -> tuple:
        return (1,)


class _RecordingConn:
    def __init__(self) -> None:
        self.cur = _RecordingCur()

    def cursor(self) -> _RecordingCur:
        return self.cur

    def commit(self) -> None:
        pass


def test_act_passes_potential_consumers_at_both_positions() -> None:
    """act 缺省=None 且 15 参：VALUES 位（10）与冲突位（14）都传字段本身。"""
    conn = _RecordingConn()
    lib = Librarian(conn)  # type: ignore[arg-type]
    lib.act("register", "MOD:x.py", actor="t", fields={"kind": "module", "home": "src/x.py"})
    params = conn.cur.calls[-1][1][0]
    assert len(params) == 15
    assert params[10] is None and params[14] is None
    # 显式数组：两个位置一致
    lib.act(
        "register", "MOD:y.py", actor="t", fields={"kind": "module", "home": "src/y.py", "potential_consumers": ["A"]}
    )
    params2 = conn.cur.calls[-1][1][0]
    assert params2[10] == ["A"] and params2[14] == ["A"]


def test_register_batch_passes_missing_field_as_none_twice() -> None:
    """采集器资产不携字段：register_batch 两位均 None（=SQL 层保留存量）。"""
    conn = _RecordingConn()
    lib = Librarian(conn)  # type: ignore[arg-type]
    ingest_all(lib, {"fs": [{"asset_id": "MOD:z.py", "kind": "module", "home": "src/z.py"}]}, actor="t")
    params = conn.cur.calls[-1][1][0]
    assert len(params) == 15
    assert params[10] is None and params[14] is None


# ── 守卫闸（零 DB，计数注入缝）───────────────────────────────────────────────
class _StubLibrarian:
    def __init__(self) -> None:
        self.audit_calls: list[tuple] = []

    def register_batch(self, assets: list, actor: str) -> int:
        return len([a for a in assets if "error" not in a and a.get("asset_id")])

    def act(self, action: str, asset_id: str, *, actor: str = "", detail=None) -> int:
        self.audit_calls.append((action, asset_id, actor, detail))
        return 1


def test_shrink_guard_triggers_and_writes_alert_event() -> None:
    """全量入账缩水：先写 audit 告警事件，再 raise（缩水闸=事件内同步复核）。"""
    counts = iter([3, 2])
    lib = _StubLibrarian()
    with pytest.raises(g.LibraryIngestShrinkError, match="3->2"):
        g.ingest_with_shrink_guard(
            None,
            lib,
            {"fs": []},
            "t",
            count_fn=lambda: next(counts),  # type: ignore[arg-type]
        )
    assert lib.audit_calls and lib.audit_calls[0][0] == "audit"
    assert lib.audit_calls[0][1] == g._GUARD_ASSET_ID
    assert lib.audit_calls[0][3]["before"] == 3 and lib.audit_calls[0][3]["after"] == 2


def test_shrink_guard_passes_without_shrink() -> None:
    """不缩水：正常返回三元组，不写告警事件。"""
    counts = iter([2, 2])
    lib = _StubLibrarian()
    n, before, after = g.ingest_with_shrink_guard(
        None,
        lib,
        {"fs": []},
        "t",
        count_fn=lambda: next(counts),  # type: ignore[arg-type]
    )
    assert (n, before, after) == (0, 2, 2)
    assert lib.audit_calls == []


# ── 语义层（真 PG 语义，独立测试 PG；未配置即 skip，零生产触碰）───────────────
@pytest.fixture()
def lib_pg(pg_db):
    """馆员+独立测试 PG 连接（真语义轨；pg_db 未激活时整组 skip）。"""
    lib = Librarian(pg_db)
    lib.ensure_schema()
    return lib


def test_pg_register_none_preserves_existing(lib_pg) -> None:
    """回归①：register 不携字段（None）必须保留存量——本缺陷的最小真语义复现。"""
    lib_pg.act(
        "register",
        "MOD:keep.py",
        actor="t",
        fields={"kind": "module", "home": "src/keep.py", "potential_consumers": ["KEEP-A"]},
    )
    lib_pg.act("register", "MOD:keep.py", actor="t", fields={"kind": "module", "home": "src/keep.py"})
    rows = lib_pg.lookup("MOD:keep.py")
    assert rows, "资产必须存在"
    with lib_pg._conn.cursor() as cur:
        cur.execute("SELECT potential_consumers FROM lib_assets WHERE asset_id = 'MOD:keep.py'")
        assert cur.fetchone()[0] == ["KEEP-A"]


def test_pg_register_explicit_empty_clears(lib_pg) -> None:
    """回归②：显式 [] = 有意清空。"""
    lib_pg.act(
        "register",
        "MOD:clear.py",
        actor="t",
        fields={"kind": "module", "home": "src/clear.py", "potential_consumers": ["OLD"]},
    )
    lib_pg.act(
        "register",
        "MOD:clear.py",
        actor="t",
        fields={"kind": "module", "home": "src/clear.py", "potential_consumers": []},
    )
    with lib_pg._conn.cursor() as cur:
        cur.execute("SELECT potential_consumers FROM lib_assets WHERE asset_id = 'MOD:clear.py'")
        assert cur.fetchone()[0] == []


def test_pg_full_ingest_shrink_guard_triggers(lib_pg) -> None:
    """回归③：全量 ingest 把非空计数打下去 → 守卫触发（真语义端到端）。"""
    lib_pg.act(
        "register",
        "MOD:seed.py",
        actor="t",
        fields={"kind": "module", "home": "src/seed.py", "potential_consumers": ["SEED-A"]},
    )
    toxic = [
        {"asset_id": "MOD:seed.py", "kind": "module", "home": "src/seed.py", "potential_consumers": []}
    ]  # 有毒采集面：显式空数组覆盖存量
    with pytest.raises(g.LibraryIngestShrinkError):
        g.ingest_with_shrink_guard(lib_pg._conn, lib_pg, {"fs": toxic}, "t")


def test_pg_full_ingest_without_field_does_not_shrink(lib_pg) -> None:
    """回归③正例：采集器不携字段的全量再采集，非空计数不变（根因修复的端到端证明）。"""
    lib_pg.act(
        "register",
        "MOD:seed2.py",
        actor="t",
        fields={"kind": "module", "home": "src/seed2.py", "potential_consumers": ["SEED-B"]},
    )
    plain = [{"asset_id": "MOD:seed2.py", "kind": "module", "home": "src/seed2.py"}]  # 不携字段
    n, before, after = g.ingest_with_shrink_guard(lib_pg._conn, lib_pg, {"fs": plain}, "t")
    assert n == 1 and before == after == 1
