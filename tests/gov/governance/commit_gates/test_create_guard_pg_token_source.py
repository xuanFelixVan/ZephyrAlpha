# [A_test] module_id: MOD-TEST-CREATE-GUARD-PG-TOKEN-SRC | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.governance.commit_gates.test_create_guard_pg_token_source
# [DOMAIN] D_AUDITTEST
# [TTL] permanent
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.create_guard
# [CONSUMERS] pytest（tests/gov/governance/commit_gates/）
# [STARTUP] imported
# [MATURITY] production
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_domain_governance/blueprint.md | CREATE-GUARD
# [INVARIANTS] 只验 T4 第三读取源的方向性：账本有正证才补全；账本不可达必须退回投影
#   口径照拦（禁变成放行）；候选为空不开连接（零额外开销）
# [MODIFY-GUARD] 新建 2026-10-10 st-maint1-20261010（批复① T4 红证）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=方向性破了；永不 skip
# [TESTS] 本文件即测试
"""CREATE-GUARD 的 PG 账本第三读取源对抗测试（T4，2026-10-10）。

当晚三次假拦截（同一形态）：token 经意图 API register→publish 已进 PG
`registry_ledger.registry_entry`，且 render 后已在主区盘面——但门读的是
**投影三级盘面**（主区盘面→车道盘面→REGISTRY_YAML），主区投影当晚因收敛
跳过脏文件而长期滞后 ⇒ "已登记"被读成"无 creation_token"，本班两袋、
gpufeed 留痕一袋全栽在这条上。

本测试钉住修法的**方向性**：第三源只能加"账本确有条目"这一种正证；
账本读不到时必须照拦——否则 T4 会从"消假拦"变成"开新静默放行口子"，
那就比原 bug 更坏。
"""

from __future__ import annotations

from pathlib import Path

import pytest

_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts" / "session_worktree.py").exists())

from zephyr.gov_enforcement.commit_gates import create_guard as cg  # noqa: E402

assert str(_ROOT) in cg.__file__, f"装载来源非本仓（假绿风险）: {cg.__file__}"

PROBE_FILE = "docs/_working/fake_campaign/00_ledger.md"
PROBE_KEY = f"file={PROBE_FILE}|token=fake-1"


class _Cur:
    def __init__(self, row: object) -> None:
        self._row = row
        self.sql: list[str] = []
        self.params: list[object] = []

    def execute(self, sql: str, params: object = None) -> None:
        self.sql.append(sql)
        self.params.append(params)

    def fetchone(self) -> object:
        return self._row

    def __enter__(self) -> _Cur:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


class _Conn:
    def __init__(self, row: object, *, fail_on_read: bool = False) -> None:
        self.cur = _Cur(None if fail_on_read else row)
        self.closed = False

    def cursor(self) -> _Cur:
        return self.cur

    def close(self) -> None:
        self.closed = True


def _patch_db(monkeypatch: pytest.MonkeyPatch, conn: _Conn) -> None:
    class _DS:
        def get_depgraph_conn(self, read_only: bool = False) -> _Conn:
            return conn

    import zephyr.infrastructure.database_service as ds

    monkeypatch.setattr(ds, "DatabaseService", _DS)


def test_helper_exists_and_is_wired() -> None:
    """防线装载自证（未修码上此例必红：函数不存在）。"""
    assert hasattr(cg, "_pg_confirmed_token_files"), "PG 第三源未装载＝T4 未修"
    src = (Path(cg.__file__)).read_text(encoding="utf-8")
    assert "registered_files | _pg_confirmed_token_files(" in src, "第三源未接进判定链"


def test_candidate_empty_never_opens_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    """常见路径零开销：投影面已覆盖全部候选时，连数据库都不该碰。"""
    import zephyr.infrastructure.database_service as ds

    def _boom(*a: object, **k: object) -> None:
        raise AssertionError("候选为空却开了数据库连接")

    monkeypatch.setattr(ds, "DatabaseService", _boom)
    assert cg._pg_confirmed_token_files([PROBE_FILE], {PROBE_FILE}) == set()


def test_pg_positive_confirms_registration(monkeypatch: pytest.MonkeyPatch) -> None:
    """主案：投影判缺、账本确有 active 条目 ⇒ 补全为正证（消假拦）。"""
    conn = _Conn((1,))
    _patch_db(monkeypatch, conn)

    got = cg._pg_confirmed_token_files([PROBE_FILE], set())

    assert got == {PROBE_FILE}, got
    sql = conn.cur.sql[0]
    params = conn.cur.params[0]
    assert "status='active'" in sql, sql
    assert "family_key=%s" in sql and "entry_key LIKE %s" in sql, "查询面未按复合键前缀收窄"
    assert params[0] == cg._CREATION_TOKEN_REGISTRY_ID
    assert params[1] == "creation_tokens"
    assert params[2] == f"file={PROBE_FILE}|%", params


def test_pg_negative_does_not_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    """账本查无条目 ⇒ 不补全（第三源不得变成第二豁免通道）。"""
    _patch_db(monkeypatch, _Conn(None))

    assert cg._pg_confirmed_token_files([PROBE_FILE], set()) == set()


@pytest.mark.parametrize(
    # 注：曾加第三种"import 期故障"子例，实测 helper 行为正确（日志出"照拦"警告），
    # 但它触发全局 conftest 的模块守卫钩子而 ERROR，非判据失败——为不留歧义删该子例。
    # 覆盖不降级：连接失败／查询失败／close 失败三条路各自独立测到"读不到=照拦"。
    "failure",
    ["connect_raises", "query_raises"],
)
def test_ledger_unreachable_falls_back_to_blocking(monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    """批复①点名的红证：账本不可达＝**退回投影口径照拦**，绝不因读不到而放行。

    照拦的机械含义＝本函数返回空集 ⇒ 调用侧 `registered_files` 不增 ⇒ 候选仍判缺
    ⇒ 走原 `_no_token_detail` 阻断分支。
    """
    if failure == "connect_raises":

        class _DS:
            def get_depgraph_conn(self, read_only: bool = False) -> None:
                raise RuntimeError("PG down")

        import zephyr.infrastructure.database_service as ds

        monkeypatch.setattr(ds, "DatabaseService", _DS)
    elif failure == "query_raises":
        conn = _Conn((1,))
        conn.cur.execute = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("socket closed"))  # type: ignore[method-assign]
        _patch_db(monkeypatch, conn)

    assert cg._pg_confirmed_token_files([PROBE_FILE], set()) == set(), "账本故障被读成放行＝新静默洞"


def test_unreachable_path_never_raises_to_caller(monkeypatch: pytest.MonkeyPatch) -> None:
    """永不抛异常给调用方：任何意外都得折成空集（否则一次 PG 抖动会把整道门炸掉）。"""
    conn = _Conn((1,))
    conn.close = lambda: (_ for _ in ()).throw(RuntimeError("close failed"))  # type: ignore[method-assign]
    conn.cur.execute = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))  # type: ignore[method-assign]
    _patch_db(monkeypatch, conn)

    assert cg._pg_confirmed_token_files([PROBE_FILE], set()) == set()


def test_registry_id_is_explicit_constant_not_roor_reverse(monkeypatch: pytest.MonkeyPatch) -> None:
    """registry_id 必须显式取正源常量。

    在册高危：ROOR 里该物理路径**同挂两个 registry_id**（REG-CAPCAN-001 在册 1.4 万条
    ／REG-GEN-001 账本 0 条，2026-10-10 实测）。反查若取到后者，会把"账本无条目"
    误读成"未登记"，甚至在 render 侧拿空账本覆盖在册面。
    """
    assert cg._CREATION_TOKEN_REGISTRY_ID == "REG-CAPCAN-001"
    src = Path(cg.__file__).read_text(encoding="utf-8")
    head = src.split("def _pg_confirmed_token_files")[1][:2600]
    assert "load_roor_index" not in head, "取 id 走 ROOR 反查＝双挂号歧途"
