# [MODULE] tests.gov.governance.test_registry_ledger_context_anchor
# [DOMAIN] D_AUDITTEST
# [TTL] permanent
# [DEPENDENCIES] zephyr.governance.registry_ledger.baseline
# [CONSUMERS] pytest（tests/gov/governance/）
# [STARTUP] imported
# [MATURITY] production
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [INVARIANTS] 零 DB 连接：全部用假游标喂 bundle 形态，验的是判据不是库
# [MODIFY-GUARD] 新建 2026-10-10 st-maint1-20261010（维护一班 T1 件①红证）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=自锚防线缺失；永不 skip
# [TESTS] 本文件即测试
"""账本自锚上下文对抗测试（st-maint1-20261010 件①）。

病灶（2026-10-10 实弹）：CAP 册投影的 header/trailing/身份声明三项上下文**唯一来源是
盘面 YAML**，而盘面又是同一快照的渲染产物。盘面被剥光后，publish 读剥光盘面→产出空
上下文快照→render 再产出剥光盘面，账本↔投影恒 zero-drift，腐蚀被 noop 幂等当稳定态
永久固化（registry_snapshot v157→v177 连续十五版 header_lines=[]/trailing_scalars=[]）。
可见征状＝顶层 `di_seam_exemptions` 消失 → REGISTRY-YAML-PARSE「顶层 di_seam_exemptions
键缺失」→ 全仓新建件入库同签名熔断 6 次。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts" / "session_worktree.py").exists())

from zephyr.governance.registry_ledger import baseline  # noqa: E402

assert str(_ROOT) in baseline.__file__, f"装载来源非本仓（假绿风险）: {baseline.__file__}"


class _FakeCursor:
    """最小假游标：按 SQL 片段路由返回值，记录执行序列。"""

    def __init__(self, rows: dict[str, tuple | None], *, raise_on: str | None = None) -> None:
        self._rows = rows
        self._raise_on = raise_on
        self.sql_log: list[str] = []
        self._current: tuple | None = None

    def execute(self, sql: str, params=None) -> None:  # noqa: ANN001
        self.sql_log.append(sql)
        if self._raise_on and self._raise_on in sql:
            raise RuntimeError("人为连接故障")
        self._current = None
        for frag, row in self._rows.items():
            if frag in sql:
                self._current = row
                return
        self._current = None

    def fetchone(self) -> tuple | None:
        return self._current

    def __enter__(self) -> _FakeCursor:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


class _FakeConn:
    def __init__(self, cursor: _FakeCursor) -> None:
        self._cursor = cursor

    def cursor(self) -> _FakeCursor:
        return self._cursor


def _anchor_rows(header: object, trailing: object, decl: object) -> dict[str, tuple]:
    return {
        "bundle->'header_lines'": (162, header, trailing, decl),
    }


# ── ① 锚提取 ═──────────────────────────────────────────────────────────────


def test_anchor_parses_pg_bundle_shape() -> None:
    """蓝证基础：jsonb 形态（已是 list/dict）能正确还原三件上下文。"""
    cur = _FakeCursor(
        _anchor_rows(
            ["<!-- GENERATED FILE — regenerate: x -->", "unique_key:", "  capabilities:", "  - capability_id"],
            [["di_seam_exemptions", []]],
            {"capabilities": ["capability_id"]},
        )
    )
    header, trailing, decl = baseline._projection_context_from_snapshot_anchor(
        "REG-X", "registry_ledger", _FakeConn(cur)
    )

    assert len(header) == 4
    assert trailing == [["di_seam_exemptions", []]]
    assert decl == {"capabilities": ("capability_id",)}


def test_anchor_parses_json_string_shape() -> None:
    """psycopg 未自动解 jsonb 时（str 形态）同样可用——两形态都得吃，否则实弹即空锚。"""
    cur = _FakeCursor(
        _anchor_rows(
            json.dumps(["banner", "unique_key:"]),
            json.dumps([["di_seam_exemptions", []]]),
            json.dumps({"creation_tokens": ["file", "token"]}),
        )
    )
    header, trailing, decl = baseline._projection_context_from_snapshot_anchor(
        "REG-X", "registry_ledger", _FakeConn(cur)
    )

    assert header == ["banner", "unique_key:"]
    assert trailing == [["di_seam_exemptions", []]]
    assert decl == {"creation_tokens": ("file", "token")}


def test_anchor_absent_returns_none() -> None:
    """查无锚=不补（禁凭空造上下文）。"""
    cur = _FakeCursor({})
    assert baseline._projection_context_from_snapshot_anchor("REG-X", "registry_ledger", _FakeConn(cur)) is None


def test_anchor_db_error_returns_none_not_raise() -> None:
    """锚不可读不得炸发布主链（退现行为）。"""
    cur = _FakeCursor({}, raise_on="bundle->'header_lines'")
    assert baseline._projection_context_from_snapshot_anchor("REG-X", "registry_ledger", _FakeConn(cur)) is None


def test_anchor_rejects_degenerate_declaration() -> None:
    """声明计划里空/非字符串段=退化，整族丢弃（无效声明=无声明，不污染键序）。"""
    cur = _FakeCursor(_anchor_rows(["banner"], [["di_seam_exemptions", []]], {"capabilities": ["", 3]}))
    _header, _trailing, decl = baseline._projection_context_from_snapshot_anchor(
        "REG-X", "registry_ledger", _FakeConn(cur)
    )

    assert decl == {}


# ── ② 补洞方向性（判据本体）──────────────────────────────────────────────


def test_heal_fills_every_missing_piece() -> None:
    """红证主案：盘面三项全空（10-10 事故现场）→ 三件全由锚补回，manifest 可见。"""
    header, trailing, decl, manifest = baseline._heal_projection_context(
        [], [], {}, (["banner", "unique_key:"], [["di_seam_exemptions", []]], {"capabilities": ("capability_id",)})
    )

    assert header == ["banner", "unique_key:"]
    assert trailing == [["di_seam_exemptions", []]]
    assert decl == {"capabilities": ("capability_id",)}
    assert manifest == {
        "header_lines": 2,
        "trailing_scalars": ["di_seam_exemptions"],
        "unique_key_fields": ["capabilities"],
    }, manifest


def test_heal_never_overrides_disk_values() -> None:
    """方向性反向证：盘面已有的件必须赢，锚只补空洞（否则=拿历史盖当前）。"""
    header, trailing, decl, manifest = baseline._heal_projection_context(
        ["盘面前进后的 banner"],
        [["some_new_trailing", 1]],
        {"capabilities": ("capability_id",)},
        (["陈旧 banner"], [["di_seam_exemptions", []]], {"capabilities": ("stale",)}),
    )

    assert header == ["盘面前进后的 banner"]
    assert trailing == [["some_new_trailing", 1]]
    assert decl == {"capabilities": ("capability_id",)}
    assert manifest == {}


def test_heal_with_no_anchor_is_identity() -> None:
    """无锚=原样返回且 manifest 空（发布照走，绝不因补检失败而卡死主链）。"""
    header, trailing, decl, manifest = baseline._heal_projection_context([], [], {}, None)

    assert (header, trailing, decl, manifest) == ([], [], {}, {})


def test_heal_is_selective_per_piece() -> None:
    """逐件独立：只缺 trailing 时仅补 trailing，其余不动、不误记。"""
    header, trailing, decl, manifest = baseline._heal_projection_context(
        ["banner"],
        [],
        {"capabilities": ("capability_id",)},
        (["陈旧 banner"], [["di_seam_exemptions", []]], {"capabilities": ("stale",)}),
    )

    assert header == ["banner"]
    assert trailing == [["di_seam_exemptions", []]]
    assert decl == {"capabilities": ("capability_id",)}, "盘面声明在位时锚不得覆盖"
    assert manifest == {"trailing_scalars": ["di_seam_exemptions"]}


def test_anchor_sql_targets_only_context_bearing_snapshots() -> None:
    """锚查询必须按"header 或 trailing 非空"筛候选，且取最新版——把 unique_key_fields
    （对象）误塞进 jsonb_array_length 会让整条锚查询报错，这里钉住 SQL 形态。"""
    sql = baseline._SQL_SNAPSHOT_CONTEXT_ANCHOR

    assert "jsonb_array_length(COALESCE(bundle->'header_lines', '[]'::jsonb)) > 0" in sql
    assert "jsonb_array_length(COALESCE(bundle->'trailing_scalars', '[]'::jsonb)) > 0" in sql
    assert "jsonb_array_length(COALESCE(bundle->'unique_key_fields" not in sql, "对象键被误当数组求长=锚查询必炸"
    assert "ORDER BY snapshot_version DESC LIMIT 1" in sql


@pytest.mark.parametrize("empty_flag", ["header", "trailing", "decl"])
def test_missing_piece_alone_triggers_anchored_heal(empty_flag: str) -> None:
    """三件任一缺失都得走补洞——旧码这里是"缺一件也照烤空值"（10-10 即此形态）。"""
    disk = {"header": ["b"], "trailing": [["t", []]], "decl": {"f": ("x",)}}
    header = [] if empty_flag == "header" else disk["header"]
    trailing = [] if empty_flag == "trailing" else disk["trailing"]
    decl = {} if empty_flag == "decl" else disk["decl"]

    _h, _t, _d, manifest = baseline._heal_projection_context(
        header, trailing, decl, (disk["header"], disk["trailing"], disk["decl"])
    )

    assert manifest, f"{empty_flag} 缺失却未触发补洞＝腐蚀仍可被固化"
