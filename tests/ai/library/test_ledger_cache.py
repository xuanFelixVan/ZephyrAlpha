# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] tests.library.test_ledger_cache
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.library.ledger_cache; zephyr.library.ledger_fingerprint; zephyr.library.lookup
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 零真库写：真源触点一律 monkeypatch（_live_version/_load_rows），实弹用例只读；红队三案必测=①100 并发打进同一失效瞬间·真源加载恰好 1 次（single-flight 证明）②世代上界 2 且加载第 3 代时第 1 代已释放③PG 不可达不得把旧代伪装成真源（降级打标/严格模式报错/无代时原样上抛）；SQL 腿用测试侧独立 ILIKE 参考实现回灌同批夹具行，与内存腿红蓝对拍
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测失败；真账本对拍用例在 PG 不可达或测试期间账本翻代时 skip（不误判红）
# [TESTS] self
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""世代缓存（ledger_cache）与读侧接线（lookup_assets）测试——图书馆内存条战役 R1。

体例循既有零 DB 护栏先例（`test_lookup_tombstone.py`：fake conn/cursor）：单位层完全
离线，仅 :func:`test_real_ledger_cache_matches_direct_sql` 一条实弹只读对拍（S2 §⑤G2）。
"""

from __future__ import annotations

import gc
import logging
import re
import threading
import weakref
from datetime import UTC, datetime
from typing import Any

import pytest

from zephyr.governance import depgraph_schema
from zephyr.library import ledger_cache, lookup
from zephyr.library.ledger_cache import LedgerFilters
from zephyr.library.ledger_fingerprint import SQL_LEDGER_FINGERPRINT

_NEEDLE_COLS = ("asset_id", "home", "title")


# ---------------------------------------------------------------- 合成账本夹具


def _row(asset_id: str, **overrides: Any) -> dict[str, Any]:
    """合成账本行：键集=装载列集（投影列 + 过滤器附加列），缺省值可覆写。"""
    row: dict[str, Any] = dict.fromkeys(ledger_cache._LOAD_COLUMNS)
    row.update(
        {
            "asset_id": asset_id,
            "kind": "file",
            "home": f"docs/{asset_id}",
            "status": "active",
            "title": f"标题 {asset_id}",
            "built_at": datetime(2026, 9, 28, tzinfo=UTC),
            "owner_domain": "D_GOVERNANCE",
            "tags": ["doc", "治理"],
        }
    )
    row.update(overrides)
    return row


# 装载序=PG ``ORDER BY asset_id``（C collation=码点序）——夹具照此排，两腿才有可比序
_DEFAULT_ROWS: tuple[dict[str, Any], ...] = (
    _row("DOC:stale", kind="doc", status="stale"),
    _row("FILE:docs/100%.md", title="含百分号与下划线 a_b"),
    _row("FILE:docs/alpha.md"),
    _row("MOD:src/zephyr/library/ledger_cache.py", kind="module", tags=["治理", "library"]),
    _row(
        "TBL:c1.market_kline_daily",
        kind="table",
        home="c1_market.market_kline_daily",
        owner_domain="D_DATA",
    ),
)


def _ilike_pattern_to_regex(pattern: str) -> re.Pattern[str]:
    """PG ILIKE 语义的测试侧独立实现：``%``/``_`` 通配、``\\X`` 字面量、大小写无关。"""
    chunks: list[str] = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "\\" and index + 1 < len(pattern):
            chunks.append(re.escape(pattern[index + 1]))
            index += 2
            continue
        if char == "%":
            chunks.append(".*")
        elif char == "_":
            chunks.append(".")
        else:
            chunks.append(re.escape(char))
        index += 1
    return re.compile("".join(chunks), re.IGNORECASE | re.DOTALL)


def _sql_leg_rows(sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    """SQL 腿参考实现（与缓存匹配码不同源）：按真语句的图案/过滤器/limit 回灌同一批夹具行。"""
    patterns = [str(p) for p in params[:3]]
    tail = list(params[3:-1])
    limit = int(params[-1])
    rows = [
        row
        for row in _DEFAULT_ROWS
        if any(
            _ilike_pattern_to_regex(p).search(str(row.get(col) or ""))
            for col, p in zip(_NEEDLE_COLS, patterns, strict=True)
        )
    ]
    if " AND kind = " in sql:
        want = tail.pop(0)
        rows = [row for row in rows if row["kind"] == want]
    if " AND owner_domain = " in sql:
        want = tail.pop(0)
        rows = [row for row in rows if row["owner_domain"] == want]
    for _ in range(sql.count("= ANY(tags)")):
        tag = tail.pop(0)
        rows = [row for row in rows if tag in (row["tags"] or [])]
    if " AND status = " in sql:
        want = tail.pop(0)
        rows = [row for row in rows if row["status"] == want]
    if " AND home LIKE " in sql:
        prefix = _ilike_pattern_to_regex(str(tail.pop(0)))
        rows = [row for row in rows if prefix.search(str(row["home"]))]
    assert not tail, f"SQL 腿参数未被消费（过滤器形状漂移）：{tail}"
    ordered = sorted(rows, key=lambda row: str(row["asset_id"]))
    return ordered[:limit]


# ---------------------------------------------------------------- 假真源


class _FakeLedger:
    """假真源：水位读出 + 整表装载，带调用计数、故障注入、在途世代数采样。"""

    def __init__(self, version: int = 100, rows: tuple[dict[str, Any], ...] = _DEFAULT_ROWS) -> None:
        self.version = version
        self.rows = rows
        self.probe_calls = 0
        self.load_calls = 0
        self.fail_probe = False
        self.fail_load = False
        self.build_hold: threading.Event | None = None
        self.build_started: threading.Event | None = None
        self.live_samples: list[int] = []

    def live_version(self) -> int:
        self.probe_calls += 1
        if self.fail_probe:
            raise RuntimeError("fake: pg down")
        return self.version

    def load_rows(self) -> tuple[dict[str, Any], ...]:
        self.load_calls += 1
        # 采样"建代瞬间"的并存世代数（服务代 + 正在构建的这一代）——上界断言依据
        self.live_samples.append(ledger_cache._SLOTS.live_count())
        if self.build_started is not None:
            self.build_started.set()
        if self.build_hold is not None:
            self.build_hold.wait(5)
        if self.fail_load:
            raise RuntimeError("fake: pg down mid-build")
        return tuple(dict(row) for row in self.rows)


@pytest.fixture(autouse=True)
def _clean_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """每例前后清世代槽，并把两枚逃生旗恢复出厂关（禁受宿主 LIBRAM_* 环境变量污染）。"""
    monkeypatch.delenv(ledger_cache.ENV_DIRECT, raising=False)
    monkeypatch.delenv(ledger_cache.ENV_STRICT_FRESH, raising=False)
    ledger_cache._reset_state()
    yield
    ledger_cache._reset_state()


def _install(monkeypatch: pytest.MonkeyPatch, fake: _FakeLedger) -> _FakeLedger:
    monkeypatch.setattr(ledger_cache, "_live_version", fake.live_version)
    monkeypatch.setattr(ledger_cache, "_load_rows", fake.load_rows)
    return fake


def _acquire_and_drop() -> Any:
    """在独立栈帧里取代：返回即销毁本帧引用（换代即时释放的可观测形态）。"""
    return ledger_cache.acquire_generation()


# ---------------------------------------------------------------- 指纹件（S1 案 B）


def test_fingerprint_sql_is_shared_constant() -> None:
    """指纹 SQL 单点真源=max(event_id)（PK O(1)）；max(built_at) 全表扫方案已否。"""
    tokens = SQL_LEDGER_FINGERPRINT.split()
    assert tokens == ["SELECT", "max(event_id)", "FROM", "lib_events"]
    assert "built_at" not in SQL_LEDGER_FINGERPRINT


def test_read_ledger_fingerprint_shape() -> None:
    """读出件零自建连接（注入 conn）：正常→int，NULL/无行→0，且执行的就是共享常量。"""
    from zephyr.library.ledger_fingerprint import read_ledger_fingerprint

    class _Cur:
        def __init__(self, value: Any) -> None:
            self._value = value
            self.sql = ""

        def __enter__(self) -> _Cur:
            return self

        def __exit__(self, *args: object) -> bool:
            return False

        def execute(self, sql: str, params: object = None) -> None:
            self.sql = sql

        def fetchone(self) -> tuple[Any, ...] | None:
            return self._value

    class _Conn:
        def __init__(self, value: Any) -> None:
            self._cur = _Cur(value)

        def cursor(self) -> _Cur:
            return self._cur

    assert read_ledger_fingerprint(_Conn((7,))) == 7  # type: ignore[arg-type]
    assert read_ledger_fingerprint(_Conn((None,))) == 0  # type: ignore[arg-type]
    assert read_ledger_fingerprint(_Conn(None)) == 0  # type: ignore[arg-type]
    conn: Any = _Conn((9,))
    assert read_ledger_fingerprint(conn) == 9
    assert conn.cursor().sql == SQL_LEDGER_FINGERPRINT


# ---------------------------------------------------------------- 投影与匹配语义


def test_fixture_rows_are_in_ledger_order() -> None:
    """夹具自检：行序=asset_id 升序（模拟装载 SQL 的 ORDER BY，否则两腿无可比序）。"""
    ids = [str(row["asset_id"]) for row in _DEFAULT_ROWS]
    assert ids == sorted(ids)


def test_projection_columns_derived_from_true_source() -> None:
    """投影列由 _SQL_LOOKUP 派生（真源改列=缓存自动跟随；本断言=形状漂移警报器）。"""
    assert ledger_cache.LEDGER_PROJECTION_COLUMNS == (
        "asset_id",
        "kind",
        "home",
        "status",
        "title",
        "built_at",
        "disposition_authority",
        "successor_of",
    )
    assert set(ledger_cache._NEEDLE_COLUMNS) <= set(ledger_cache.LEDGER_PROJECTION_COLUMNS)
    assert set(ledger_cache._FILTER_COLUMNS) <= set(ledger_cache._LOAD_COLUMNS)


def test_hit_reuses_generation_with_zero_data_sql(monkeypatch: pytest.MonkeyPatch) -> None:
    """水位未变→同一代对象服务；账本数据装载恒 1 次（每读只付 1 次 O(1) 水位探测）。"""
    fake = _install(monkeypatch, _FakeLedger())
    first = ledger_cache.search("alpha", 5)
    second = ledger_cache.search("alpha", 5)
    assert [row["asset_id"] for row in first] == ["FILE:docs/alpha.md"]
    assert [row["asset_id"] for row in second] == ["FILE:docs/alpha.md"]
    assert (fake.load_calls, fake.probe_calls) == (1, 2)
    assert ledger_cache.cache_status().degraded is False


def test_version_bump_triggers_reload(monkeypatch: pytest.MonkeyPatch) -> None:
    """水位翻代→重建一次并换行集（失效自动跟上，无 invalidate 钩子可挂）。"""
    fake = _install(monkeypatch, _FakeLedger())
    ledger_cache.search("alpha", 5)
    assert ledger_cache.cache_status().version == 100
    fake.version = 200
    fake.rows = (_row("FILE:docs/beta.md"),)
    assert [row["asset_id"] for row in ledger_cache.search("beta", 5)] == ["FILE:docs/beta.md"]
    assert (fake.load_calls, ledger_cache.cache_status().version) == (2, 200)


def test_returned_rows_expose_projection_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """对外行键=投影列（owner_domain/tags 附加列不外泄，与直查真源逐键同形）。"""
    _install(monkeypatch, _FakeLedger())
    rows = ledger_cache.search("alpha", 5)
    assert list(rows[0]) == list(ledger_cache.LEDGER_PROJECTION_COLUMNS)


def test_ilike_semantics_lowercase_and_three_axes(monkeypatch: pytest.MonkeyPatch) -> None:
    """ILIKE 等价：大小写无关、三列任一命中、按装载序（=PG ORDER BY 序）返回。"""
    _install(monkeypatch, _FakeLedger())
    assert [row["asset_id"] for row in ledger_cache.search("ALPHA", 5)] == ["FILE:docs/alpha.md"]
    assert [row["asset_id"] for row in ledger_cache.search("market_kline", 5)] == ["TBL:c1.market_kline_daily"]
    assert [row["asset_id"] for row in ledger_cache.search("标题", 5)] == [
        "DOC:stale",
        "FILE:docs/alpha.md",
        "MOD:src/zephyr/library/ledger_cache.py",
        "TBL:c1.market_kline_daily",
    ]
    assert [row["asset_id"] for row in ledger_cache.search("file:docs", 5)] == [
        "FILE:docs/100%.md",
        "FILE:docs/alpha.md",
    ]


def test_wildcard_chars_are_literal_not_patterns(monkeypatch: pytest.MonkeyPatch) -> None:
    """``%``/``_`` 在 SQL 腿被转义为字面量，内存腿同样字面匹配（转义口径一致）。"""
    _install(monkeypatch, _FakeLedger())
    assert [row["asset_id"] for row in ledger_cache.search("100%", 5)] == ["FILE:docs/100%.md"]
    assert [row["asset_id"] for row in ledger_cache.search("a_b", 5)] == ["FILE:docs/100%.md"]
    assert ledger_cache.search("zzz%", 5) == []


def test_needle_separator_blocks_cross_column_false_hit(monkeypatch: pytest.MonkeyPatch) -> None:
    """NUL 分隔=零伪命中：跨列边界的词不得匹配（朴素拼接会假命中 "mdFILE"）。"""
    _install(monkeypatch, _FakeLedger())
    assert ledger_cache.search("mdFILE", 5) == []
    assert ledger_cache.search("docs/alpha.mdFILE", 5) == []


def test_limit_and_filters_five_axes(monkeypatch: pytest.MonkeyPatch) -> None:
    """limit 边界（≤0 空、截断）+ T5 五轴过滤器语义（tags 为 AND）。"""
    _install(monkeypatch, _FakeLedger())
    assert ledger_cache.search("docs", 0) == []
    assert [row["asset_id"] for row in ledger_cache.search("", 2)] == ["DOC:stale", "FILE:docs/100%.md"]
    assert ledger_cache.search("alpha", 5, LedgerFilters(kind="module")) == []
    assert [row["asset_id"] for row in ledger_cache.search("docs", 5, LedgerFilters(kind="file"))] == [
        "FILE:docs/100%.md",
        "FILE:docs/alpha.md",
    ]
    assert [
        row["asset_id"] for row in ledger_cache.search("alpha", 5, LedgerFilters(home_prefix="docs/FILE:docs/a"))
    ] == ["FILE:docs/alpha.md"]
    assert ledger_cache.search("alpha", 5, LedgerFilters(home_prefix="c1_market")) == []
    assert ledger_cache.search("alpha", 5, LedgerFilters(owner_domain="D_DATA")) == []
    assert [row["asset_id"] for row in ledger_cache.search("", 5, LedgerFilters(tags=["治理", "library"]))] == [
        "MOD:src/zephyr/library/ledger_cache.py"
    ]
    assert ledger_cache.search("", 5, LedgerFilters(tags=["治理", "nope"])) == []
    assert [row["asset_id"] for row in ledger_cache.search("", 5, LedgerFilters(status="stale"))] == ["DOC:stale"]


def test_exact_asset_id_point_axis(monkeypatch: pytest.MonkeyPatch) -> None:
    """索书号精确轴（by_id）：命中回投影行，未命中 None。"""
    _install(monkeypatch, _FakeLedger())
    gen = ledger_cache.acquire_generation()
    got = gen.get("DOC:stale")
    assert got is not None and got["status"] == "stale"
    assert list(got) == list(ledger_cache.LEDGER_PROJECTION_COLUMNS)
    assert gen.get("FILE:不存在的卡") is None


# ---------------------------------------------------------------- 红队①：single-flight


def test_single_flight_hundred_concurrent_one_load(monkeypatch: pytest.MonkeyPatch) -> None:
    """红队①：100 个并发查询打进同一失效瞬间，真源整表加载只发生 1 次。"""
    fake = _install(monkeypatch, _FakeLedger())
    assert ledger_cache.search("alpha", 5)
    baseline = fake.load_calls
    assert baseline == 1

    hold = threading.Event()
    started = threading.Event()
    fake.version = 999  # 翻代：100 个请求者同时看到"水位已变"
    fake.build_hold = hold
    fake.build_started = started
    served: list[Any] = []
    barrier = threading.Barrier(100)

    def _worker() -> None:
        barrier.wait(timeout=10)
        served.append(_acquire_and_drop())

    threads = [threading.Thread(target=_worker) for _ in range(100)]
    for thread in threads:
        thread.start()
    assert started.wait(10), "无请求者进入建代"
    assert fake.load_calls == baseline + 1, f"single-flight 失效：失效瞬间真源加载 {fake.load_calls - baseline} 次"
    hold.set()
    for thread in threads:
        thread.join(timeout=15)
    assert fake.load_calls == baseline + 1, "锁等待者出锁后又重复建代"
    assert len(served) == 100
    assert {gen.version for gen in served} == {999}
    assert len({id(gen) for gen in served}) == 1, "并发请求者拿到了不同代对象"


def test_double_check_after_lock_skips_load(monkeypatch: pytest.MonkeyPatch) -> None:
    """双检路径：锁等待者进锁后复查到同水位即复用，不再触碰真源。"""
    fake = _install(monkeypatch, _FakeLedger())
    with ledger_cache._BUILD_LOCK:
        waiter = threading.Thread(target=ledger_cache.acquire_generation)
        waiter.start()
        assert not waiter.join(timeout=0.3)  # 阻塞在锁上，未取得代
        assert fake.load_calls == 0
    waiter.join(timeout=10)
    assert ledger_cache.acquire_generation().version == 100
    assert fake.load_calls == 1


# ---------------------------------------------------------------- 红队②：世代上界


def test_generation_cap_two_and_first_released(monkeypatch: pytest.MonkeyPatch) -> None:
    """红队②：上界常量封死=2；加载第 3 代时第 1 代必须已释放；任一时刻并存世代 ≤2。"""
    assert ledger_cache._MAX_GENERATIONS == 2
    fake = _install(monkeypatch, _FakeLedger(version=10))

    held = _acquire_and_drop()
    ref_first = weakref.ref(held)
    fake.version = 20
    held = _acquire_and_drop()  # 换代：第 1 代失最后引用
    ref_second = weakref.ref(held)
    gc.collect()
    assert ref_first() is None, "第 1 代在第 2 代服务期仍存活（旧代未即时释放）"

    fake.version = 30
    held = _acquire_and_drop()
    ref_third = weakref.ref(held)
    gc.collect()
    assert ref_second() is None, "加载第 3 代时第 2 代未释放"
    assert ref_third() is held
    assert ledger_cache._SLOTS.live_count() == 1
    assert fake.live_samples and max(fake.live_samples) <= ledger_cache._MAX_GENERATIONS, fake.live_samples


def test_slots_have_no_history_field() -> None:
    """上界是结构性的：_Slots 只有"服务代 + 在途加载代水位号"两格，禁历史槽/队列/逐条容器。"""
    assert set(ledger_cache._Slots.__dataclass_fields__) == {"serving", "loading_version"}


# ---------------------------------------------------------------- 红队③：真源不可达


def test_pg_down_with_old_gen_marks_degraded(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    """红队③a：水位读失败 + 有旧代 → 服务旧代但显式打降级标（degraded/reason/failures）+ WARNING。"""
    fake = _install(monkeypatch, _FakeLedger())
    assert ledger_cache.search("alpha", 5)
    fake.fail_probe = True
    with caplog.at_level(logging.WARNING, logger="zephyr.library.ledger_cache"):
        rows = ledger_cache.search("alpha", 5)
    assert rows, "有旧代可服务时不该空手"
    status = ledger_cache.cache_status()
    assert (status.degraded, status.reason, status.failures) == (True, "fingerprint_read_failed", 1)
    assert any("降级" in record.message for record in caplog.records)
    fake.fail_probe = False
    ledger_cache.search("alpha", 5)
    assert ledger_cache.cache_status().degraded is False  # 真源恢复即自动清标


def test_pg_down_strict_flag_raises_instead_of_stale(monkeypatch: pytest.MonkeyPatch) -> None:
    """红队③b：LIBRAM_STRICT_FRESH=1 ⇒ 降级态直接报错，绝不把旧代当真源。"""
    fake = _install(monkeypatch, _FakeLedger())
    ledger_cache.search("alpha", 5)
    fake.fail_probe = True
    monkeypatch.setenv(ledger_cache.ENV_STRICT_FRESH, "1")
    with pytest.raises(RuntimeError, match="pg down"):
        ledger_cache.search("alpha", 5)


def test_first_query_with_pg_down_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    """红队③c：首查即不可达且无代可服务 ⇒ 异常原样上抛（与直查真源逐字节一致）。"""
    fake = _install(monkeypatch, _FakeLedger())
    fake.fail_probe = True
    with pytest.raises(RuntimeError, match="pg down"):
        ledger_cache.search("alpha", 5)
    assert fake.load_calls == 0
    assert ledger_cache.cache_status().version is None


def test_mid_build_failure_keeps_previous_generation(monkeypatch: pytest.MonkeyPatch) -> None:
    """红队③d：建代中途失败→服务代未动（切换前失败=天然无损）+ 降级标；恢复后翻代成功。"""
    fake = _install(monkeypatch, _FakeLedger())
    before = ledger_cache.acquire_generation()
    fake.version = 500
    fake.fail_load = True
    assert ledger_cache.acquire_generation() is before
    status = ledger_cache.cache_status()
    assert (status.degraded, status.reason, status.version) == (True, "generation_build_failed", 100)
    fake.fail_load = False
    assert ledger_cache.acquire_generation().version == 500


# ---------------------------------------------------------------- 接线：lookup_assets


class _FakeCursor:
    def __init__(self) -> None:
        self.description = tuple((column,) for column in ledger_cache.LEDGER_PROJECTION_COLUMNS)
        self._rows: list[dict[str, Any]] = []

    def __enter__(self) -> _FakeCursor:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def execute(self, sql: str, params: object = None) -> None:
        self._rows = _sql_leg_rows(sql, tuple(params or ()))

    def fetchall(self) -> list[tuple[Any, ...]]:
        return [tuple(row[column] for column in ledger_cache.LEDGER_PROJECTION_COLUMNS) for row in self._rows]


class _FakePooledConn:
    """假池化连接：区分 close（弃池）与 release（归还），供本批清偿项断言。"""

    def __init__(self) -> None:
        self.closed = False
        self.sqls: list[str] = []

    def cursor(self) -> _FakeCursor:
        return _FakeCursor()

    def commit(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True


def _install_fake_conn(monkeypatch: pytest.MonkeyPatch) -> tuple[_FakePooledConn, list[Any]]:
    """假借还接线（R4 起兼容两种绑定形态）。

    lookup.py 的 depgraph_schema import 已下沉到使用点（函数内），故真源模块属性
    才是必然生效的接缝；`lookup` 命名空间上的同名属性在 R4 前是绑定点、R4 后不存在，
    两边都打（lookup 侧 raising=False）即可不分前后版本都测到同一语义。
    """
    conn = _FakePooledConn()
    released: list[Any] = []
    monkeypatch.setattr(depgraph_schema, "get_depgraph_pg_connection", lambda *a, **k: conn)
    monkeypatch.setattr(depgraph_schema, "release_depgraph_pg_connection", released.append)
    monkeypatch.setattr(lookup, "get_depgraph_pg_connection", lambda *a, **k: conn, raising=False)
    monkeypatch.setattr(lookup, "release_depgraph_pg_connection", released.append, raising=False)
    return conn, released


def test_lookup_assets_serves_from_cache_without_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    """接线主证：命中即零连接借用（借还接口被引爆即失败），整表装载 1 次。"""
    fake = _install(monkeypatch, _FakeLedger())

    def _boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("缓存命中路径不该借连接")

    for holder, raising in ((lookup, False), (ledger_cache, True), (depgraph_schema, True)):
        monkeypatch.setattr(holder, "get_depgraph_pg_connection", _boom, raising=raising)
        monkeypatch.setattr(holder, "release_depgraph_pg_connection", _boom, raising=raising)
    assert [row["asset_id"] for row in lookup.lookup_assets("alpha", limit=5)] == ["FILE:docs/alpha.md"]
    assert [row["asset_id"] for row in lookup.lookup_assets("alpha", limit=5, kind="file")] == ["FILE:docs/alpha.md"]
    assert fake.load_calls == 1


def test_cache_leg_and_sql_leg_agree_on_same_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    """红蓝对拍（合成夹具）：内存腿 vs 独立 ILIKE 参考实现的 SQL 腿逐条一致。"""
    _install(monkeypatch, _FakeLedger())
    _install_fake_conn(monkeypatch)
    combos = [
        LedgerFilters(),
        LedgerFilters(kind="file"),
        LedgerFilters(tags=["治理"]),
        LedgerFilters(status="stale"),
        LedgerFilters(owner_domain="D_DATA"),
        LedgerFilters(home_prefix="docs/FILE"),
        LedgerFilters(kind="file", status="active", tags=["doc"]),
    ]
    for term in ("alpha", "标题", "TBL", "100%", "a_b", "nope", "docs", ""):
        for filters in combos:
            cached = [row["asset_id"] for row in ledger_cache.search(term, 3, filters)]
            direct = [row["asset_id"] for row in lookup._lookup_terms_via_sql([term], 3, filters)[0]]
            assert cached == direct, (term, filters, cached, direct)


def test_direct_escape_hatch_borrows_and_releases(monkeypatch: pytest.MonkeyPatch) -> None:
    """LIBRAM_DIRECT=1 旁路：走真源直查，且用毕**归还**连接（conn.close() 弃池反模式已清偿）。"""
    conn, released = _install_fake_conn(monkeypatch)
    monkeypatch.setenv(ledger_cache.ENV_DIRECT, "1")
    rows = lookup.lookup_assets("alpha", limit=5, tags=["doc"])
    assert [row["asset_id"] for row in rows] == ["FILE:docs/alpha.md"]
    assert released == [conn]
    assert conn.closed is False, "lookup 又用 conn.close() 弃池（本批清偿项）"


def test_feeds_query_releases_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    """供数反查腿同样归还连接（第二处弃池点，S2 §3.6 顺手清偿）。"""
    conn, released = _install_fake_conn(monkeypatch)
    monkeypatch.setattr(lookup.Librarian, "lookup_by_feeds", lambda self, keyword, limit=20: [])
    assert lookup._run_feeds_query("kw", 5) == 1
    assert released == [conn] and conn.closed is False


# ---------------------------------------------------------------- 实弹只读对拍（真账本）


def test_real_ledger_cache_matches_direct_sql(monkeypatch: pytest.MonkeyPatch) -> None:
    """真账本抽样对拍（补 S2 §⑤G2 缺口）：ILIKE/转义/序/过滤器零差才算默认开得住。

    只读不写；账本在测试期间翻代（并发写者）时 skip，不误判红。
    """
    try:
        version_before = ledger_cache._live_version()
    except Exception as exc:  # noqa: BLE001 — 环境无 PG 时 skip（非红）
        pytest.skip(f"depgraph PG 不可达，实弹对拍需真源：{exc}")
    gen = ledger_cache.acquire_generation()
    assert gen.rows, "真账本装载为空=环境异常"
    sampled = [
        str(gen.rows[0]["asset_id"]),
        str(gen.rows[37]["home"]),
        str(gen.rows[11].get("title") or "")[:6],
    ]
    terms = [term for term in sampled if term] + [
        "margin_trading",
        "MOD:src/zephyr/library",
        "%",
        "_",
        "MOD:",
        "龙虎榜",
    ]
    combos = [
        LedgerFilters(),
        LedgerFilters(kind="file"),
        LedgerFilters(status="active", home_prefix="docs/"),
        LedgerFilters(kind="table", owner_domain="D_DATA"),
    ]
    mismatched: list[tuple[str, LedgerFilters, list[str], list[str]]] = []
    for term in terms:
        for filters in combos:
            cached = [row["asset_id"] for row in ledger_cache.search(term, 5, filters)]
            direct = [row["asset_id"] for row in lookup._lookup_terms_via_sql([term], 5, filters)[0]]
            if cached != direct:
                mismatched.append((term, filters, cached, direct))
    try:
        assert not mismatched, f"内存腿与真源 SQL 腿差异：{mismatched[:3]}"
    finally:
        if ledger_cache._live_version() != version_before:
            pytest.skip("账本在并发写下降中翻代：两侧读取跨代，本次对拍不作判据")
