# [BLUEPRINT] MOD-SIG-152 | docs/_working/decision_map_campaign/links/L04_stock_wire/SKEL.md §3（M-41/D22 落地）
# [MODULE] tests.signal_ashare.test_candidate_pool_snapshot
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.core.candidate_pool_snapshot; zephyr.signal_ashare.core.candidate_pool_aggregator; schemas.categories.market.market_stock_candidate_pool
# [CONSUMERS] pytest
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 测试隔离：零生产路径写入（落表一律 fake writer 注入捕获，CH 不可达不涉；
#   注册制来源 save/restore 防泄漏）——宪法 §9.6；构造数据全走聚合器公开镜像类型
#   （PoolCandidateInput/VetoMark），零生产数据依赖；
#   覆盖=快照写入（列契约/行内容/顺位沉底）+幂等重跑（同输入必同行）+空池日（零行
#   fail-visible+零写）+注入制（注册幂等/单源异常 fail-open）+run_pool_batch_for_day
#   状态三态（ok/empty/absent）+DDL 列契约同序核对
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=AssertionError
# [TESTS] self
# [A_module] module_id=MOD-SIG-152 | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] test-candidate-pool-snapshot-l04c01-20260925
"""candidate_pool_snapshot 单测（L04-C01 载体施工验收：写入/幂等/空池三主轴）。

验收口径（SKEL §3 L04-C01）：
    表建成且连续 10 个交易日有盘后真值行；回放任一历史日可取当日池快照
    ——本件覆盖"行可产、重放幂等、空池不脏写"三个机检面（真值行连续性属生产
    日循环观察面，非单测口径）。
"""

from __future__ import annotations

import json

import pytest

from schemas.categories.market.market_stock_candidate_pool import (
    CATEGORY_ID as DDL_CATEGORY_ID,
)
from schemas.categories.market.market_stock_candidate_pool import (
    INSERT_COLUMNS as DDL_INSERT_COLUMNS,
)
from schemas.categories.market.market_stock_candidate_pool import (
    STOCK_CANDIDATE_POOL_DDL,
)
from schemas.categories.market.market_stock_candidate_pool import (
    TABLE_NAME as DDL_TABLE_NAME,
)
from zephyr.signal_ashare.core import candidate_pool_snapshot as cps
from zephyr.signal_ashare.core.candidate_pool_aggregator import (
    PoolCandidateInput,
    VetoMark,
    aggregate_candidate_pool,
)

DAY = "2026-09-24"


# ── 构造数据工装（聚合器公开镜像类型，零生产数据依赖）─────────────────────
def _pool():
    """双来源合流+否决沉底的构造池：600001 双 sleeve 合流留最优、300003 否决沉底。"""
    return aggregate_candidate_pool(
        dual_pool_candidates=(
            PoolCandidateInput(symbol="600001", sleeve="short_term", rank_score=3.2, source_rank=1),
            PoolCandidateInput(symbol="000002", sleeve="swing", rank_score=2.5, source_rank=2),
            PoolCandidateInput(symbol="300003", sleeve="short_term", rank_score=1.8),
        ),
        strategy_chain_candidates=(PoolCandidateInput(symbol="600001", sleeve="daban", rank_score=1.0),),
        veto_marks=(VetoMark(symbol="300003", reasons=("st_flag", "negative_news")),),
        as_of=DAY,
    )


_ENV_KW = {
    "market_state": "ignition",
    "turnover_yi": 12000.0,
    "switches": {
        "state": "ignition",
        "first_board_filter_on": True,
        "short_term_chain_on": True,
        "swing_chain_on": True,
        "tighten_risk": False,
    },
}


class _CaptureWriter:
    """fake 落表通道：捕获 FetchResult 断言零生产写入。"""

    def __init__(self) -> None:
        self.results: list = []

    def __call__(self, result) -> bool:
        self.results.append(result)
        return True


@pytest.fixture(autouse=True)
def _isolate_registry():
    """注册表 save/restore：测试泄漏防线（零全局态残留）。"""
    saved = cps.registered_bundle_sources()
    cps.clear_bundle_sources()
    yield
    cps.clear_bundle_sources()
    for src in saved:
        cps.register_pool_bundle_source(src)


# ── DDL 列契约（真源同序核对）────────────────────────────────────────────
def test_insert_columns_match_ddl_truth():
    """POOL_INSERT_COLUMNS 与 DDL INSERT_COLUMNS 严格同序（16 列，producer 契约）。"""
    assert cps.CATEGORY_ID == DDL_CATEGORY_ID == "market_stock_candidate_pool"
    assert f"c1_market.{DDL_TABLE_NAME}" == cps._TARGET_TABLE
    ddl_cols = DDL_INSERT_COLUMNS.strip("()").split(", ")
    assert list(cps.POOL_INSERT_COLUMNS) == [c.strip() for c in ddl_cols]
    assert len(cps.POOL_INSERT_COLUMNS) == 16
    # RULE-SCHEMA-TZ：ingest_ts 显式时区
    assert "DateTime64(3, 'Asia/Shanghai')" in STOCK_CANDIDATE_POOL_DDL
    assert "ReplacingMergeTree" in STOCK_CANDIDATE_POOL_DDL
    assert "ORDER BY (trade_date, stage, symbol)" in STOCK_CANDIDATE_POOL_DDL


# ── 主轴 1：快照写入 ────────────────────────────────────────────────────
def test_snapshot_write_rows_contract():
    """写入契约：表/列/行内容逐项（sleeve 合流/pool_rank/否决沉底/meta 留痕）。"""
    writer = _CaptureWriter()
    report = cps.run_pool_batch_for_day(
        DAY, params=cps.PoolSnapshotParams(**_ENV_KW, conduction_adj=None), bundle_source=_StaticSource(), writer=writer
    )
    assert report["status"] == "ok" and report["persisted"] is True
    assert report["rows"] == 3 and report["actual_size"] == 2 and report["vetoed"] == 1
    assert len(writer.results) == 1
    res = writer.results[0]
    assert res.table == "c1_market.stock_candidate_pool"
    assert res.columns == list(cps.POOL_INSERT_COLUMNS)
    rows = dict(zip(res.columns, res.rows[0], strict=True))
    # 合流去重留最优：600001 双 sleeve，主标签=顺位最优来源，全集按定义序
    assert rows["symbol"] == "600001"
    assert rows["sleeve"] == "short_term"
    assert json.loads(rows["sleeves"]) == ["short_term", "daban"]
    assert rows["pool_rank"] == 1 and rows["vetoed"] == 0
    # 不可产字段显式缺省（禁拍假值）
    assert rows["tier_slot"] is None and rows["conduction_adj"] is None
    assert json.loads(rows["score_components"]) == {}
    # 快照元：环境开关来源标尺+截断/否决清单（单表回放自足）
    meta = json.loads(rows["snapshot_meta"])
    assert meta["env"]["market_state"] == "ignition"
    assert meta["env"]["turnover_yi"] == 12000.0
    assert meta["env"]["switches"]["first_board_filter_on"] is True
    assert meta["actual_size"] == 2
    assert meta["vetoed_symbols"] == ["300003"]
    assert rows["version"] == "v1" and rows["data_source"] == "candidate_pool_aggregator"


def test_snapshot_write_vetoed_sunk_bottom():
    """否决只标记不剔除：vetoed 行沉底（pool_rank 靠后）+原因全集留痕。"""
    res = cps.run_daily_batch(_pool(), params=cps.PoolSnapshotParams(**_ENV_KW))
    all_rows = [dict(zip(res.columns, t, strict=True)) for t in res.rows]
    by_sym = {r["symbol"]: r for r in all_rows}
    assert by_sym["300003"]["vetoed"] == 1
    assert json.loads(by_sym["300003"]["veto_reasons"]) == ["st_flag", "negative_news"]
    vetoed_rank = by_sym["300003"]["pool_rank"]
    assert all(r["pool_rank"] < vetoed_rank for r in all_rows if not r["vetoed"])
    # 顺位分降序（未否决段）
    kept = [r for r in all_rows if not r["vetoed"]]
    assert [r["rank_score"] for r in kept] == sorted((r["rank_score"] for r in kept), reverse=True)


class _StaticSource:
    """静态构造来源（三来源束打包形态，生产注册制的 fake 形态）。"""

    def fetch_bundles(self, day: str) -> cps.PoolBundles:
        return cps.PoolBundles(
            dual_pool_candidates=(
                PoolCandidateInput(symbol="600001", sleeve="short_term", rank_score=3.2, source_rank=1),
                PoolCandidateInput(symbol="000002", sleeve="swing", rank_score=2.5, source_rank=2),
                PoolCandidateInput(symbol="300003", sleeve="short_term", rank_score=1.8),
            ),
            strategy_chain_candidates=(PoolCandidateInput(symbol="600001", sleeve="daban", rank_score=1.0),),
            veto_marks=(VetoMark(symbol="300003", reasons=("st_flag", "negative_news")),),
            notes=("static",),
        )


# ── 主轴 2：幂等重跑 ────────────────────────────────────────────────────
def test_idempotent_rerun_identical_rows():
    """同输入必同行：重跑两次行元组全等（ReplacingMergeTree 同键替换语义的前提）。"""
    res1 = cps.run_daily_batch(_pool(), params=cps.PoolSnapshotParams(**_ENV_KW))
    res2 = cps.run_daily_batch(_pool(), params=cps.PoolSnapshotParams(**_ENV_KW))
    assert res1.rows == res2.rows
    assert res1.last_key == res2.last_key == f"{DAY}|close_final"
    # meta JSON 确定性（sort_keys 紧凑序列化，同输入必同串）
    row1 = dict(zip(res1.columns, res1.rows[0], strict=True))
    row2 = dict(zip(res2.columns, res2.rows[0], strict=True))
    assert row1["snapshot_meta"] == row2["snapshot_meta"]
    assert row1["sleeves"] == row2["sleeves"]


# ── 主轴 3：空池日行为 ──────────────────────────────────────────────────
def test_empty_pool_day_zero_rows_no_write(caplog):
    """空池日：零行 FetchResult + WARNING fail-visible + 落表通道零触达（非静默）。"""

    def _boom(_result):
        raise AssertionError("空池日禁止触达落表通道")

    with caplog.at_level("WARNING"):
        res = cps.run_daily_batch(
            aggregate_candidate_pool((), (), (), as_of=DAY), params=cps.PoolSnapshotParams(**_ENV_KW)
        )
        report = cps.run_pool_batch_for_day(DAY, writer=_boom)
    assert res.rows == [] and res.rows_fetched == 0
    assert report["status"] == "empty" and report["rows"] == 0
    assert report["persisted"] is False
    assert any("空池" in rec.message for rec in caplog.records)


def test_empty_day_veto_only_marks_visible_in_report():
    """纯否决留痕日（无候选可标记）：零行如实，但否决清单在侧带报告可查（不丢）。"""
    report = cps.run_pool_batch_for_day(DAY, bundle_source=_VetoOnlySource(), writer=_CaptureWriter())
    assert report["status"] == "empty" and report["vetoed"] == 1
    assert report["vetoed_symbols"] == ["300003"]


class _VetoOnlySource:
    def fetch_bundles(self, day: str) -> cps.PoolBundles:
        return cps.PoolBundles(veto_marks=(VetoMark(symbol="300003", reasons=("st_flag",)),))


# ── 注入制（注册表）─────────────────────────────────────────────────────
def test_registry_register_idempotent_and_collect():
    """注册幂等（同对象忽略）+ collect 合并三来源束。"""
    src = _StaticSource()
    cps.register_pool_bundle_source(src)
    cps.register_pool_bundle_source(src)  # 幂等
    bundles = cps.collect_bundles(DAY)
    assert len(bundles.dual_pool_candidates) == 3
    assert len(bundles.strategy_chain_candidates) == 1
    assert len(bundles.veto_marks) == 1


def test_registry_single_source_failure_fail_open():
    """单来源异常折空束+注记留痕，不炸整批（fail-open）。"""

    class _Broken:
        def fetch_bundles(self, day):
            raise RuntimeError("source down")

    cps.register_pool_bundle_source(_Broken())
    cps.register_pool_bundle_source(_StaticSource())
    report = cps.run_pool_batch_for_day(DAY, writer=_CaptureWriter())
    assert report["status"] == "ok"
    assert any("source down" in n or "RuntimeError" in n for n in report["notes"])


def test_no_registered_source_notes_honest_default():
    """无注册源=如实缺省（注记说明三来源未接线），不替上游拍候选。"""
    bundles = cps.collect_bundles(DAY)
    assert bundles.dual_pool_candidates == ()
    assert any("未接线" in n for n in bundles.notes)


# ── run_pool_batch_for_day 契约 ─────────────────────────────────────────
def test_invalid_day_folds_absent_never_raises():
    """非法日期折 status=absent（侧带永不外抛契约）。"""
    report = cps.run_pool_batch_for_day("not-a-date", writer=_CaptureWriter())
    assert report["status"] == "absent" and "error" in report


def test_aggregator_input_error_folds_absent():
    """聚合输入非法（重复对）折 absent（透传聚合器 fail-closed 后由侧带兜住）。"""

    class _DupSource:
        def fetch_bundles(self, day):
            dup = PoolCandidateInput(symbol="600001", sleeve="daban", rank_score=1.0)
            return cps.PoolBundles(strategy_chain_candidates=(dup, dup))

    report = cps.run_pool_batch_for_day(DAY, bundle_source=_DupSource(), writer=_CaptureWriter())
    assert report["status"] == "absent" and report["error"] == "CandidatePoolInputError"


# ── L04-C01 读回回环（zc-lane-t-20260927：写→读回放，验收"回放任一历史日可取当日池快照"）──
class _FakeReader:
    """fake 只读通道：捕获 SQL，返回预置行（位置序=POOL_INSERT_COLUMNS）。"""

    def __init__(self, rows):
        self.rows = rows
        self.sqls: list[str] = []

    def __call__(self, sql):
        self.sqls.append(sql)
        return self.rows


def test_load_pool_snapshot_roundtrip_exact_mode():
    """写→读回环：捕获的快照行经 fake reader 读回，JSON 四列反序列化、pool_rank 保序。"""
    writer = _CaptureWriter()
    report = cps.run_pool_batch_for_day(DAY, bundle_source=_StaticSource(), writer=writer)
    assert report["status"] == "ok" and report["persisted"] is True
    result = writer.results[0]
    reader = _FakeReader(result.rows)
    out = cps.load_pool_snapshot(DAY, mode="exact", reader=reader)
    assert out["status"] == "ok" and out["trade_date"] == DAY and out["stage"] == "close_final"
    assert len(out["pool"]) == len(result.rows)
    for got, want in zip(out["pool"], result.rows, strict=True):
        assert got["symbol"] == want[2]
        assert got["pool_rank"] == want[7]
        # JSON 列反序列化：snapshot_meta 是 dict（容量/截断元回放自足）
        assert isinstance(got["snapshot_meta"], dict) and "capacity" in got["snapshot_meta"]
        assert isinstance(got["sleeves"], list)
    # SQL 面当日等值过滤
    assert f"trade_date = '{DAY}'" in reader.sqls[0]


def test_load_pool_snapshot_pit_mode_reads_prior_partition():
    """pit 模式：SQL 用 max(trade_date)<T 子查询（shift(1) 防未来函数，daban 先例同款）。"""
    writer = _CaptureWriter()
    cps.run_pool_batch_for_day(DAY, bundle_source=_StaticSource(), writer=writer)
    reader = _FakeReader(writer.results[0].rows)
    next_day = "2026-09-25"
    out = cps.load_pool_snapshot(next_day, mode="pit", reader=reader)
    assert out["status"] == "ok" and out["trade_date"] == DAY
    assert "max(trade_date) FROM" in reader.sqls[0] and f"trade_date < '{next_day}'" in reader.sqls[0]


def test_load_pool_snapshot_absent_no_row():
    """exact 无当日行 → absent=no_pool_row（如实缺席，禁编空池）。"""
    reader = _FakeReader([])
    out = cps.load_pool_snapshot("2026-09-01", mode="exact", reader=reader)
    assert out["status"] == "absent" and out["error"] == "no_pool_row"


def test_load_pool_snapshot_invalid_stage_and_mode_fail_closed():
    """stage 越封闭集/mode 越枚举 → ValueError（fail-closed）。"""
    with pytest.raises(ValueError):
        cps.load_pool_snapshot(DAY, stage="bad_stage; DROP", reader=_FakeReader([]))
    with pytest.raises(ValueError):
        cps.load_pool_snapshot(DAY, mode="dict", reader=_FakeReader([]))
