# [BLUEPRINT] MOD-BT-214 | docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md
# [MODULE] tests.strategy_pipeline.test_decision_orchestrator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.daily_decision_orchestrator; zephyr.strategy_pipeline.daily_gate_snapshot;
#   schemas.categories.decision_daily
# [CONSUMERS] pytest
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 测试隔离：零生产路径写入（CH 读全部走注入式 FakeReader，写全部走记录式
#   FakeSink，marker 走 tmp_path，告警走捕获函数）——宪法 §9.6；
#   覆盖=蓝图 §六.2 降级矩阵 D1-D7 全分支+幂等重放+force 重拍+包集空安全态+P2b 场景引擎联测
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-214 | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] test-decision-orchestrator-mod-bt-214-20260916
"""日度编排器全流程+降级矩阵 D1-D7 全分支单测（BT-P1-031 刀 3 验收，含 P2b 联测）。

测试口径（蓝图 §七刀 3 验收标准）：
    ①事件链端到端三场景（唤醒拍板/非交易日休眠/幂等重放+force 重拍）
    ②降级矩阵 D1-D7 每分支
    ③三前置判定（regime 新鲜 ∧ alloc 当日 run ∧ 日历可证）
    ④包选择（state_matrix 查表∩已毕业包=v1 空集安全态）
    ⑤P2b 场景引擎联测：编排器读 judgment_daily_plan/plan_verification 归类结果
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.strategy_pipeline import daily_decision_orchestrator as orch
from zephyr.strategy_pipeline.daily_decision_orchestrator import (
    compute_position_cap,
    maybe_run_daily_decision,
    run_daily_decision,
    select_packages,
    write_decision_row,
)

D = "2026-09-15"           # 数据日（盘后批尾）
TARGET = "2026-09-16"      # 次交易日
PREV = "2026-09-12"

_REGIME_COLS = 15           # SQL_LATEST_REGIME_SNAPSHOT 列数

# 切源前产线占位表快照（v0 草案；真值冻结自 daily_decision_orchestrator 旧 REGIME_TO_SEGMENT
# 常量，2026-09-25 附录C 六步之第 3 步切源）。只作对照基准，禁 import 生产侧复活本地表。
_LEGACY_V0_REGIME_TO_SEGMENT = {
    "r10": "capitulation",
    "r4": "distribution",
    "r1": "accumulation",
    "r11": "accumulation",
    "r2": "ignition",
    "r12": "ignition",
    "r3": "expansion",
}


class FakeReader:
    """注入式只读通道：按 SQL 内容路由到可编排的假表（零生产路径）。"""

    def __init__(
        self,
        *,
        calendar_open: bool = True,
        next_day: str | None = TARGET,
        prev_day: str | None = PREV,
        lead_days: int = 40,
        regime: tuple | None = None,
        alloc_rows: list | None = None,
        kline_max: str = D,
        turnover_yi: float = 15700.0,
        plan_row: tuple | None = None,
        verify_row: tuple | None = None,
        regime_fail: bool = False,
        alloc_fail: bool = False,
    ) -> None:
        self.calendar_open = calendar_open
        self.next_day = next_day
        self.prev_day = prev_day
        self.lead_days = lead_days
        self.regime = regime if regime is not None else _regime_row()
        self.alloc_rows = alloc_rows if alloc_rows is not None else [_alloc_row()]
        self.kline_max = kline_max
        self.turnover_yi = turnover_yi
        self.plan_row = plan_row
        self.verify_row = verify_row
        self.regime_fail = regime_fail
        self.alloc_fail = alloc_fail
        self.queries: list[str] = []

    def __call__(self, sql: str):
        self.queries.append(sql)
        if "cal_date = " in sql and "is_open = 1" in sql:
            return [(D,)] if self.calendar_open else []
        if "min(cal_date)" in sql:
            return [(self.next_day,)] if self.next_day else [(None,)]
        if "max(cal_date)" in sql and "cal_date <" in sql:
            return [(self.prev_day,)] if self.prev_day else [(None,)]
        if "count()" in sql:
            return [(self.lead_days,)]
        if "regime_snapshot_history" in sql:
            if self.regime_fail:
                raise RuntimeError("regime channel down")
            return [self.regime] if self.regime else []
        if "alloc_budget_daily" in sql:
            if self.alloc_fail:
                raise RuntimeError("alloc channel down")
            return list(self.alloc_rows)
        if "amount FROM c1_market.kline_index" in sql:
            return [(self.turnover_yi * 1e8,)]
        if "max(trade_date) FROM c1_market.kline_index" in sql:
            return [(self.kline_max,)]
        if "judgment_daily_plan" in sql:
            return [self.plan_row] if self.plan_row else []
        if "judgment_plan_verification" in sql:
            return [self.verify_row] if self.verify_row else []
        raise AssertionError(f"FakeReader 未路由的 SQL: {sql[:120]}")


class FakeSink:
    """记录式写面（零生产写入），可注入失败。"""

    def __init__(self, disposition: str = "ch_committed", fail: bool = False) -> None:
        self.rows: list[tuple[str, str, bytes]] = []
        self.disposition = disposition
        self.fail = fail

    def __call__(self, table: str, columns: str, payload: bytes) -> str:
        if self.fail:
            raise RuntimeError("sink down")
        self.rows.append((table, columns, payload))
        return self.disposition


def _regime_row(
    trade_date: str = D,
    dominant: str = "r3",
    confidence: float = 0.99,
) -> tuple:
    # confidence 列=dominant 态概率（真源语义）；conf 放在 dominant 对应位，余量归 r1
    slots = [0.0] * 7                                  # r1,r2,r3,r4,r10,r11,r12
    dom_idx = {"r1": 0, "r2": 1, "r3": 2, "r4": 3, "r10": 4, "r11": 5, "r12": 6}.get(
        dominant, 2)
    slots[dom_idx] = confidence
    slots[0] = round(max(0.0, 1.0 - confidence - sum(slots[1:])), 6)
    row = (f"VAL-P0-TEST-{trade_date.replace('-', '')}", trade_date,
           slots[0], slots[1], slots[2], slots[3], slots[4], slots[5], slots[6],
           dominant, confidence, 0.75, 0.8, 0.9, "{}")
    assert len(row) == _REGIME_COLS
    return row


def _alloc_row(strategy_id: str = "STR-VREV-025") -> tuple:
    return (strategy_id, f"alloc-{D}-t00001", 1.0, 0.95, 0.5, 500000.0, 0.5, "NO_ACTION", "idle")


@pytest.fixture()
def tmp_marker(tmp_path: Path) -> Path:
    return tmp_path / "markers"


@pytest.fixture(autouse=True)
def _isolate_l2_admission(monkeypatch: pytest.MonkeyPatch) -> None:
    """L2 三原料供料隔离（L03-C02 batch2 接线后 load_l2_admission 走生产 CH 读，
    测试经 monkeypatch 供料件归零生产读取——宪法 §9.6 测试隔离）。"""
    monkeypatch.setattr("zephyr.strategy_pipeline.daily_gate_snapshot._load_l2_admission",
                        lambda: {"status": "absent"})


def _run(reader: FakeReader, sink: FakeSink, tmp_marker: Path, **kw):
    alerts: list[tuple[str, str]] = []
    out = run_daily_decision(D, reader=reader, sink=sink, xshg_fn=lambda d: reader.calendar_open,
                             marker_dir=tmp_marker, alert_fn=lambda m, level="INFO": alerts.append((m, level)),
                             **kw)
    return out, alerts


# ── 正常路径 ──────────────────────────────────────────────────────────────
class TestHappyPath:
    def test_full_chain_adjudicates(self, tmp_marker) -> None:
        reader, sink = FakeReader(), FakeSink()
        out, alerts = _run(reader, sink, tmp_marker)
        assert out["action"] == "adjudicated"
        assert out["no_trade"] == 0
        assert out["market_state"] == "expansion"          # r3→expansion（法定真源映射）
        assert out["trade_date"] == TARGET                 # 生效日=次交易日
        assert out["disposition"] == "ch_committed"
        assert len(sink.rows) == 1
        table, columns, payload = sink.rows[0]
        assert table == "c1_backtest.decision_daily"
        assert "ingest_ts" not in columns                  # 系统列禁写侧传（RULE-SCHEMA-TZ）
        fields = payload.decode("utf-8").rstrip("\n").split("\t")
        assert len(fields) == 18                           # 写侧声明列数
        assert any("[DAILY-DECISION]" in m for m, _ in alerts)   # S7 播报前缀
        # 正常路径无降级（末棒序：regime/alloc 均已在盘）
        assert out["degraded"] == 0 or "D2_gate_absent" in out["degrade_reasons"]

    def test_position_cap_hard_cap(self, tmp_marker) -> None:
        reader, sink = FakeReader(), FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        # expansion 带插值 0.5+0.2*0.99=0.698 → 60% 硬顶封顶
        assert out["position_cap"] == pytest.approx(0.60)
        row = sink.rows[0][2].decode("utf-8").split("\t")
        assert row[10] == "0"                              # no_trade
        pkg = json.loads(row[8])
        assert pkg["source_cell"] == "TDM-E-L1|expansion"
        assert pkg["source_confidence"] == "proposed"

    def test_ignition_transition_band(self, tmp_marker) -> None:
        reader = FakeReader(regime=_regime_row(dominant="r12", confidence=0.50))
        sink = FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        # ignition 带 0.3+0.2*0.5=0.4 → 过渡带×0.5=0.2（<60% 硬顶）；r12→ignition 新旧映射同键
        assert out["market_state"] == "ignition"
        assert out["position_cap"] == pytest.approx(0.20)
        assert "transition_band" in out["degrade_reasons"]
        assert out["no_trade"] == 0                        # 过渡带=折减不是禁做

    def test_ignition_mapped_r12_high_confidence(self, tmp_marker) -> None:
        reader = FakeReader(regime=_regime_row(dominant="r12", confidence=0.9))
        sink = FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["market_state"] == "ignition"           # r12 带内映射（切源零变化键）
        assert out["no_trade"] == 0

    def test_euphoria_band_sell_only(self, tmp_marker) -> None:
        reader = FakeReader(regime=_regime_row(dominant="r12", confidence=0.9))
        sink = FakeSink()
        cap = compute_position_cap("euphoria", 0.9)
        assert cap["sell_only"] is True
        assert cap["position_cap"] == pytest.approx(0.27)  # 0+0.3*0.9
        out, _ = _run(reader, sink, tmp_marker)
        assert out["no_trade"] == 0                        # r12→ignition 限仓非禁做
        # 切源披露：六段 euphoria/distribution 无 r 态来源（composer 注）⇒ regime 腿天然
        # 不出这两段，sell_only 语义仅剩 compute_position_cap 直呼面可达（上两行断言）。


# ── 六段温度真源链切源（附录C 六步之第 3 步：切产线+补守卫，2026-09-25）─────
class TestSixStateTruthChainSwitch:
    """产线六段映射切源对照与守卫件。

    对照基准=_LEGACY_V0_REGIME_TO_SEGMENT（切源前占位表快照）；法定真源=
    framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE（附录C 唯一映射位点，
    与挂图侧 auto_mount.R2SIX 有漂移守卫钉住）。默认行为变化仅限 r4/r2/r1 三键
    冲突处（这正是切源目的），其余四键零变化。
    """

    def test_three_key_conflict_snapshot(self) -> None:
        """三键冲突差异快照（附录C §2 逐键对照，快照即契约）。"""
        from zephyr.pf_core.strategy_engine.framework_composer import (
            REGIME_STATE_TO_ACTIVATION_PHASE as TRUTH,
        )

        legacy = _LEGACY_V0_REGIME_TO_SEGMENT
        # r4：值相反键——法定=accumulation（修复）vs 占位=distribution（退潮，语义相反）
        assert legacy["r4"] == "distribution"
        assert TRUTH["r4"] == "accumulation"
        # r2/r1：占位表凭空路由键——法定无此键=不路由（宁漏勿误）
        assert legacy.get("r2") == "ignition" and "r2" not in TRUTH
        assert legacy.get("r1") == "accumulation" and "r1" not in TRUTH
        # 差异恰好只有这三键：其余四键（r10/r11/r12/r3）全等=切源零额外行为变化
        diff = {k for k in set(legacy) | set(TRUTH)
                if legacy.get(k) != TRUTH.get(k)}
        assert diff == {"r4", "r2", "r1"}

    def test_drift_guard_production_reference_is_truth_source(self) -> None:
        """产线漂移守卫（镜像 tests/backtest/test_auto_mount_sle3 的 R2SIX 全等守卫）：
        产线引用必须就是唯一位点对象本体（同源消费，无本地副本可漂移）。"""
        from zephyr.pf_core.strategy_engine.framework_composer import (
            REGIME_STATE_TO_ACTIVATION_PHASE as TRUTH,
        )

        assert orch._regime_to_segment() is TRUTH

    def test_placeholder_table_retired_no_resurrection(self) -> None:
        """占位表已弃用且禁复活：模块面不得再持有任何本地 r→六段映射表。"""
        assert not hasattr(orch, "REGIME_TO_SEGMENT")

    @pytest.mark.parametrize(("dominant", "expect_state", "expect_no_trade",
                              "expect_cap"), [
        ("r4", "accumulation", 0, 0.295),  # 旧占位=distribution 禁做 → 新=accumulation 限仓可做
        ("r2", "unknown", 1, 0.0),         # 旧占位=ignition 凭空点火 → 新=不路由 fail-closed
        ("r1", "unknown", 1, 0.0),         # 旧占位=accumulation → 新=不路由 fail-closed
    ])
    def test_three_key_end_to_end_snapshot(self, tmp_marker, monkeypatch,
                                           dominant, expect_state,
                                           expect_no_trade, expect_cap) -> None:
        """三键行为变化端到端快照（confidence=0.95；L5 钉 normal 隔离 D6 干扰）。"""
        monkeypatch.setattr("zephyr.strategy_pipeline.daily_gate_snapshot._collect_l5",
                            lambda: {"layer": "L5", "kill_switch": {"status": "ok",
                                    "state": "normal"}})
        reader = FakeReader(regime=_regime_row(dominant=dominant, confidence=0.95))
        sink = FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["action"] == "adjudicated"
        assert out["market_state"] == expect_state
        assert out["no_trade"] == expect_no_trade
        assert out["position_cap"] == pytest.approx(expect_cap)
        if expect_no_trade:
            assert "D1_regime_state_unmappable" in out["degrade_reasons"]

    def test_truth_source_import_failure_fail_closed(self, tmp_marker, monkeypatch) -> None:
        """真源导入失败=fail-closed：按不可映射 no_trade 保守侧（禁 fallback 本地表）。

        用 builtins.__import__ 拦截模拟真源不可用（#ARCH-107 禁 sys.modules 置 None 毒）。
        """
        import builtins

        real_import = builtins.__import__

        def _boom(name, *args, **kwargs):
            if name == "zephyr.pf_core.strategy_engine.framework_composer":
                raise ImportError("simulated truth-source outage")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _boom)
        reader = FakeReader(regime=_regime_row(dominant="r3", confidence=0.99))
        sink = FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["no_trade"] == 1
        assert "regime_missing" in out["no_trade_reason"]
        assert "D1_regime_state_unmappable" in out["degrade_reasons"]
        row = sink.rows[0][2].decode("utf-8").split("\t")
        assert "真源不可用" in row[16]                     # 审计 note 如实归因导入失败


# ── 休眠与日历（S1 / D4 / D5）────────────────────────────────────────────
class TestCalendarDormancy:
    def test_non_trading_day_sleep(self, tmp_marker) -> None:
        reader = FakeReader(calendar_open=False, kline_max="2026-09-10")  # 无日历行+无行情实证
        sink = FakeSink()
        out, alerts = _run(reader, sink, tmp_marker)
        assert out["action"] == "sleep"
        assert sink.rows == []                             # 休眠=零行写入
        assert any("休眠" in m for m, _ in alerts)

    def test_d4_data_proven_degraded_open(self, tmp_marker) -> None:
        reader = FakeReader(calendar_open=False)           # 日历查无此行+行情实证在
        sink = FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["action"] == "adjudicated"              # data_proven 降级开市，非误休眠
        assert out["degraded"] == 1
        assert "calendar:data_proven" in out["degrade_reasons"]
        row = sink.rows[0][2].decode("utf-8").split("\t")
        assert row[13] == "data_proven"                    # calendar_source 列

    def test_d5_calendar_stale_sentinel(self, tmp_marker) -> None:
        reader = FakeReader(lead_days=3)                   # 表尾提前量 <10 交易日
        sink = FakeSink()
        out, alerts = _run(reader, sink, tmp_marker)
        assert "calendar_stale" in out["degrade_reasons"]
        assert any("日历续期哨兵" in m for m, lvl in alerts if lvl == "WARN")

    def test_ambiguous_no_row(self, tmp_marker) -> None:
        # 日历缺行+行情实证在（data_proven）但次交易日全源不可解析 → 无生效日不出行
        reader = FakeReader(calendar_open=False, next_day=None)
        sink = FakeSink()
        out, alerts = _run(reader, sink, tmp_marker)
        assert out["action"] == "blocked_no_target"
        assert sink.rows == []                             # 无生效日=不出行（安全侧）
        assert any("次交易日不可解析" in m for m, lvl in alerts if lvl == "ERROR")


# ── 降级矩阵 D1/D3/D6（no_trade 分支）────────────────────────────────────
class TestDegradeMatrixNoTrade:
    def test_d1_regime_missing(self, tmp_marker) -> None:
        reader, sink = FakeReader(regime=[]), FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["no_trade"] == 1
        assert "regime_missing" in out["no_trade_reason"]
        assert out["degraded"] == 1
        row = sink.rows[0][2].decode("utf-8").split("\t")
        assert float(row[7]) == 0.0                        # 降级快照仓位上限=0

    def test_d1_regime_channel_fail(self, tmp_marker) -> None:
        reader, sink = FakeReader(regime_fail=True), FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert "regime_missing" in out["no_trade_reason"]

    def test_d1_regime_stale(self, tmp_marker) -> None:
        reader = FakeReader(regime=_regime_row(trade_date="2026-09-10"))  # <前交易日
        sink = FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert "regime_missing" in out["no_trade_reason"]
        assert "D1_regime_stale" in out["degrade_reasons"]

    def test_d1_unmappable_dominant(self, tmp_marker) -> None:
        reader = FakeReader(regime=_regime_row(dominant="rX"))
        sink = FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert "regime_missing" in out["no_trade_reason"]
        assert "D1_regime_state_unmappable" in out["degrade_reasons"]

    def test_d3_budget_run_missing(self, tmp_marker) -> None:
        reader, sink = FakeReader(alloc_rows=[]), FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["no_trade"] == 1
        assert "budget_run_missing" in out["no_trade_reason"]
        assert "D3_budget_run_missing" in out["degrade_reasons"]

    def test_d6_kill_switch_probe_fail_conservative(self, tmp_marker, monkeypatch) -> None:
        def boom():
            raise RuntimeError("kill switch probe down")

        monkeypatch.setattr("zephyr.strategy_pipeline.daily_gate_snapshot._collect_l5",
                            lambda: {"layer": "L5", "kill_switch": {"status": "absent",
                                    "error": "RuntimeError", "conservative_treatment": "tripped"}})
        reader, sink = FakeReader(), FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["no_trade"] == 1
        assert "kill_switch" in out["no_trade_reason"]
        assert "D6_kill_switch_conservative" in out["degrade_reasons"]

    def test_d6_kill_switch_tripped(self, tmp_marker, monkeypatch) -> None:
        monkeypatch.setattr("zephyr.strategy_pipeline.daily_gate_snapshot._collect_l5",
                            lambda: {"layer": "L5", "kill_switch": {"status": "ok", "state": "tripped"}})
        reader, sink = FakeReader(), FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["no_trade"] == 1
        assert "kill_switch" in out["no_trade_reason"]

    def test_distribution_band_zero_budget_branch_direct(self) -> None:
        """distribution 预算带 0% 分支保活（切源披露：该段无 r 态来源，regime 腿不可达，
        附录C/composer 注如实披露；直呼单测保分支覆盖，禁经由 regime 伪造达成）。"""
        ctx = orch.LegCtx(reasons=[], degrade=[], notes=[])
        orch._no_trade_sources("distribution", ctx)
        assert "distribution_band" in ctx.reasons
        assert any("distribution 预算带 0%" in n for n in ctx.notes)


# ── D2 门缺席（不阻断拍板）与 D7 fail-open ────────────────────────────────
class TestD2D7:
    def test_d2_gate_absent_not_blocking(self, tmp_marker) -> None:
        reader, sink = FakeReader(), FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["action"] == "adjudicated"
        assert out["no_trade"] == 0                        # D2 只降级不阻断
        # L03-C02 水温桥接线后：L1 regime 在盘 → L2 出响应面不再 absent（D2_gate_absent:L2
        # 解降，wiring_proposals §三.5 预期口径）；三原料供料测试隔离=absent → gate_level
        # 如实 not_evaluated（不伪造放行门态）。
        row = sink.rows[0][2].decode("utf-8").split("\t")
        gate = json.loads(row[9])
        assert gate["l2"]["status"] == "ok"
        assert gate["l2"]["gate_level"] == "not_evaluated"
        assert "L2" not in gate["absent_layers"]

    def test_d2_gate_l2_absent_when_regime_missing(self, tmp_marker) -> None:
        """L1 regime 缺席 → 水温桥无入参 → L2 如实 absent：D2_gate_absent:L2 降级保留（D2 矩阵不删格）。"""
        reader, sink = FakeReader(regime_fail=True), FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["action"] == "adjudicated"              # 只降级不阻断
        row = sink.rows[0][2].decode("utf-8").split("\t")
        gate = json.loads(row[9])
        assert gate["l2"]["status"] == "absent"
        assert "L2" in gate["absent_layers"]
        assert any(r.startswith("D2_gate_absent") and "L2" in r
                   for r in str(out["degrade_reasons"]).split(";"))

    def test_d7_sink_fail_fail_open(self, tmp_marker) -> None:
        reader, sink = FakeReader(), FakeSink(fail=True)
        out, alerts = _run(reader, sink, tmp_marker)
        assert out["action"] == "error"                    # 不外抛，折进返回
        assert sink.rows == []                             # 不留半行
        assert any("拍板未完成" in m for m, lvl in alerts if lvl == "ERROR")
        # 先拍板先占：marker 已落（防重拍风暴）；force 可人工重拍
        out2 = run_daily_decision(D, reader=reader, sink=FakeSink(), marker_dir=tmp_marker)
        assert out2["action"] == "skipped_marker"


# ── 幂等与重拍（S6 marker 语义）──────────────────────────────────────────
class TestIdempotency:
    def test_replay_skipped(self, tmp_marker) -> None:
        reader, sink = FakeReader(), FakeSink()
        out1, _ = _run(reader, sink, tmp_marker)
        out2, _ = _run(reader, sink, tmp_marker)
        assert out1["action"] == "adjudicated"
        assert out2["action"] == "skipped_marker"
        assert len(sink.rows) == 1                         # 同日重唤醒零副作用

    def test_force_new_run_appended(self, tmp_marker) -> None:
        reader, sink = FakeReader(), FakeSink()
        out1, _ = _run(reader, sink, tmp_marker)
        out2, _ = _run(reader, sink, tmp_marker, force=True)
        assert out2["action"] == "adjudicated"
        assert out2["run_id"] != out1["run_id"]            # 重拍=新 run_id 追加
        assert len(sink.rows) == 2                         # 原行不动（只增不改）

    def test_wake_filter(self, tmp_marker) -> None:
        assert maybe_run_daily_decision("daily_kline_2026", success=False)["action"] == "skipped_wake_point"
        assert maybe_run_daily_decision("tick_loader_x", success=True)["action"] == "skipped_wake_point"
        out = maybe_run_daily_decision("kline_daily_incremental", success=True,
                                       reader=FakeReader(), sink=FakeSink(),
                                       xshg_fn=lambda d: True, marker_dir=tmp_marker,
                                       alert_fn=lambda m, level="INFO": None)
        assert out["action"] == "adjudicated"


# ── 包选择（S-OWNER-002 查表骨架，v1 空毕业集安全态）────────────────────────
class TestPackageSelection:
    def test_v1_empty_graduated_safe_state(self) -> None:
        dm = {"state_matrix": {"cells": [
            {"node_id": "TDM-E-L1", "state": "expansion", "mounted": ["STR-MOMTREND-033"],
             "confidence": "proposed"}]}}
        pkg = select_packages("expansion", decision_map=dm)
        assert pkg["enabled_packages"] == []               # 挂载∩毕业∅=安全态
        assert pkg["incomplete"] is True
        assert "无已毕业包" in pkg["note"]
        assert pkg["source_cell"] == "TDM-E-L1|expansion"

    def test_pending_owner_adoption_cell(self) -> None:
        dm = {"state_matrix": {"cells": [
            {"node_id": "TDM-E-L1", "state": "ignition", "mounted": [],
             "confidence": "proposed",
             "mounted_reason": "pending-owner-adoption 本格从未填过：填格属 Owner 资金分配门位"}]}}
        pkg = select_packages("ignition", decision_map=dm)
        assert pkg["incomplete"] is True
        assert "pending-owner-adoption" in pkg["note"]     # 空格残缺催 Owner 采纳

    def test_missing_cell(self) -> None:
        pkg = select_packages("capitulation", decision_map={"state_matrix": {"cells": []}})
        assert pkg["enabled_packages"] == []
        assert pkg["incomplete"] is True
        assert "包选择残缺" in pkg["note"]

    def test_none_state(self) -> None:
        pkg = select_packages(None)
        assert pkg["incomplete"] is True


# ── P2b 场景引擎联测（编排器读场景归类结果）────────────────────────────────
class TestP2bIntegration:
    def test_plan_context_read_into_snapshot(self, tmp_marker) -> None:
        reader = FakeReader(
            plan_row=(D, json.dumps({"scenarios": [{"scenario_id": "S1_attack"}]})),
            verify_row=(D, "S3_oscillation", '[{"scenario_id": "S1_attack", "trigger_ts": "10:31"}]',
                        "scenario_engine:intraday:2026091510"))
        sink = FakeSink()
        out, _ = _run(reader, sink, tmp_marker)
        assert out["action"] == "adjudicated"
        row = sink.rows[0][2].decode("utf-8").split("\t")
        assert "plan=2026-09-15" in row[16]                # note 列含预案读口
        assert "scenario=S3_oscillation" in row[16]        # 盘中归类结果入快照
        assert "(1hits)" in row[16]

    def test_plan_context_absent_silent(self, tmp_marker) -> None:
        reader, sink = FakeReader(), FakeSink()            # P2b 表无行=缺席不阻塞
        out, _ = _run(reader, sink, tmp_marker)
        assert out["action"] == "adjudicated"


# ── 写侧纪律（fail-closed/列序/投递如实）──────────────────────────────────
class TestWriteSide:
    def test_missing_column_raises(self) -> None:
        with pytest.raises(RuntimeError, match="缺声明列"):
            write_decision_row({"run_id": "x"}, sink=lambda t, c, p: "ch_committed")

    def test_bad_disposition_raises(self) -> None:
        from schemas.categories.decision_daily import INSERT_COLUMNS

        body = INSERT_COLUMNS.strip().strip("()")
        row = {c.strip(): "" for c in body.split(",") if c.strip()}
        row["no_trade"] = 1
        with pytest.raises(RuntimeError, match="fail-closed"):
            write_decision_row(row, sink=lambda t, c, p: "not_durable")

    def test_local_durable_accepted(self) -> None:
        from schemas.categories.decision_daily import INSERT_COLUMNS

        body = INSERT_COLUMNS.strip().strip("()")
        row = {c.strip(): "" for c in body.split(",") if c.strip()}
        n, disp = write_decision_row(row, sink=lambda t, c, p: "local_durable")
        assert (n, disp) == (1, "local_durable")           # 本地兜底=如实可接受


# ── T4 盘后核对（TRD-A17 最小实体化，L09-C02）─────────────────────────────
class ReconReader:
    """T4 核对只读通道：decision_daily 计划行+sim_trade_log 当日事件计数（构造例，零生产路径）。"""

    def __init__(self, plan_row: tuple | None = None, trade_counts: list | None = None) -> None:
        self.plan_row = plan_row
        self.trade_counts = trade_counts or []

    def __call__(self, sql: str):
        if "decision_daily" in sql:
            return [self.plan_row] if self.plan_row else []
        if "sim_trade_log" in sql:
            return list(self.trade_counts)
        raise AssertionError(f"ReconReader 未路由的 SQL: {sql[:120]}")


def _plan_row(*, no_trade: int = 0, cap: float = 0.60) -> tuple:
    """decision_daily 计划行构造（INSERT_COLUMNS 声明列序 18 列；target=TARGET）。"""
    return ("decision-2026-09-16-test01", TARGET, D, "expansion", 0.99,
            0.5, 0.7, cap, "{}", "{}", no_trade, "", "[]", "trade_calendar",
            0, "", "", "v1")


class TestPostmarketReconcile:
    """计划 vs 实际核对（TRD-A17）：一致/偏差两例+字段级 diff 计数+播报出声（DB 只读）。"""

    def _run(self, reader: ReconReader):
        alerts: list[tuple[str, str]] = []
        out = orch.postmarket_reconcile(TARGET, reader=reader,
                                        alert_fn=lambda m, level="INFO": alerts.append((m, level)))
        return out, alerts

    def test_match_plan_permits_entries(self) -> None:
        """一致例①：计划放行（no_trade=0, cap=60%）∧ 实际有进有出 → match。"""
        reader = ReconReader(plan_row=_plan_row(no_trade=0, cap=0.60),
                             trade_counts=[("entry", 2), ("exit", 1)])
        out, alerts = self._run(reader)
        assert out["verdict"] == "match"
        assert out["fields_deviated"] == 0
        assert out["fields_compared"] >= 2                 # 字段级：no_trade+position_cap 两字段核对
        assert out["actual_entry_count"] == 2
        assert out["actual_exit_count"] == 1
        assert out["plan_run_id"] == "decision-2026-09-16-test01"
        assert any("T4-RECONCILE" in m and lvl == "INFO" for m, lvl in alerts)

    def test_match_no_trade_respected(self) -> None:
        """一致例②：计划禁新开仓（no_trade=1）∧ 实际零 entry（只有存量 exit）→ match。"""
        reader = ReconReader(plan_row=_plan_row(no_trade=1, cap=0.0),
                             trade_counts=[("exit", 3)])
        out, _ = self._run(reader)
        assert out["verdict"] == "match"
        assert out["actual_entry_count"] == 0

    def test_deviation_no_trade_violated_by_entries(self) -> None:
        """偏差例：计划禁新开仓 ∧ 实际 entry=3 → deviation（字段级 diff=1/1）+WARN 出声。"""
        reader = ReconReader(plan_row=_plan_row(no_trade=1, cap=0.0),
                             trade_counts=[("entry", 3), ("exit", 1)])
        out, alerts = self._run(reader)
        assert out["verdict"] == "deviation"
        assert out["fields_deviated"] == 1
        assert out["fields_compared"] == 1
        assert out["deviations"][0]["field"] == "no_trade_vs_entries"
        assert out["deviations"][0]["actual"]["entry_count"] == 3
        assert any("T4-RECONCILE" in m and lvl == "WARN" for m, lvl in alerts)

    def test_deviation_zero_cap_entries_when_permitted(self) -> None:
        """偏差例②：计划放行但 cap=0（边界）∧ 实际 entry=1 → deviation 落 position_cap 字段。"""
        reader = ReconReader(plan_row=_plan_row(no_trade=0, cap=0.0),
                             trade_counts=[("entry", 1)])
        out, _ = self._run(reader)
        assert out["verdict"] == "deviation"
        assert out["deviations"][0]["field"] == "position_cap_vs_entries"

    def test_deviation_plan_row_missing(self) -> None:
        """计划行缺席（无快照=无放行凭证却有执行）→ deviation 落 plan_row 字段（fail-visible）。"""
        reader = ReconReader(plan_row=None, trade_counts=[("entry", 1)])
        out, _ = self._run(reader)
        assert out["verdict"] == "deviation"
        assert out["deviations"][0]["field"] == "plan_row"
        assert out["fields_deviated"] == 1

    def test_channel_error_visible_not_raised(self) -> None:
        """读通道故障→verdict=error 折进返回（永不外抛反噬结算链），错误如实留痕。"""
        class Boom:
            def __call__(self, sql: str):
                raise RuntimeError("channel down")

        out = orch.postmarket_reconcile(TARGET, reader=Boom(), alert_fn=lambda m, level="INFO": None)
        assert out["verdict"] == "error"
        assert "RuntimeError" in out["error"]

    def test_bad_date_fail_closed(self) -> None:
        """date 非法=ValueError（模块 ERROR_CONTRACT 唯一 fail-closed 例外）。"""
        with pytest.raises(ValueError):
            orch.postmarket_reconcile("20260916", reader=ReconReader())
