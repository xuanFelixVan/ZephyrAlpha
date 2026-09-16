# [BLUEPRINT] MOD-BT-171 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_auto_mount_sle3
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.auto_mount; zephyr.factor.analysis.bhy_fdr; zephyr.pf_core.strategy_engine.framework_composer(只读词表对表)
# [CONSUMERS] MOD-BT-171 SLE-3 验收（车道 B 收口批）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离：全 fake 面板/fake 引擎零 IO，禁触 ClickHouse/生产 data/，输出一律 tmp_path
# [MODIFY-GUARD] scripts/backtest/auto_mount.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""auto_mount SLE-3 行为测试——动态判定窗/微观相位 overlay/BHY-FDR 门（车道 B 收口批）。

覆盖三新行为：①IS_WIN 终点随快照表最新可用日动态前移（SLE-3②，禁写死日期）；
②euphoria/distribution 经 phase_overlay 可进入候选与激活链（SLE-3③，L1 防御格自此
可检验）；③BHY-FDR q=10% 族级接受/拒绝边界含 SR 方向/OOS 反向/大族 HLZ 三门
（SLE-3①）。另兑现 auto_mount.py:125 注释点名的守卫件
test_r2six_drift_guard_vs_framework_composer（R2SIX 与 composer 孪生表防漂移）。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import backtest.auto_mount as am  # noqa: E402
from backtest.auto_mount import (  # noqa: E402
    CLASS_CANDIDATE_STATES,
    IS_WIN_START,
    PIT_TAIL_LAG,
    R2SIX,
    apply_multiple_testing,
    load_phase_panel,
    phase_overlay,
    resolve_six_phase,
    window_of,
)


def _snap_df(dates, doms="r3"):
    return pd.DataFrame({"dom": [doms] * len(dates)}, index=pd.DatetimeIndex(dates))


def _flat_breadth(dates):
    idx = pd.DatetimeIndex(dates)
    return pd.DataFrame({"close": np.full(len(idx), 100.0),
                         "adv": np.full(len(idx), 500.0),
                         "dec": np.full(len(idx), 500.0)}, index=idx)


# ---------- ① SLE-3②：判定窗终点=快照最新可用日回退 PIT 尾窗（禁写死） ----------
class TestDynamicWindow:
    def test_endpoint_follows_latest_snapshot(self, monkeypatch):
        dates = pd.bdate_range("2026-08-03", periods=20)  # 全 fake 近期窗：终点只能来自数据
        calls: dict[str, object] = {}

        def fake_snap(start, end):
            calls["start"], calls["end"] = start, end
            return _snap_df(dates)

        monkeypatch.setattr(am, "_snapshot_rows", fake_snap)
        monkeypatch.setattr(am, "_breadth_frame", lambda s, e: _flat_breadth(pd.date_range(s, e)))
        panel = load_phase_panel()
        assert calls["start"] == IS_WIN_START and calls["end"] is None  # 终点不写死=入参 None
        assert panel.index[-1] == dates[-1 - PIT_TAIL_LAG]  # 尾日回退不入样
        assert window_of(panel) == f"{IS_WIN_START}..{dates[-1 - PIT_TAIL_LAG].date()}"
        # 快照多一天 → 终点跟着前移一天（动态性反证，非巧合相等）
        more = dates.append(pd.DatetimeIndex([dates[-1] + pd.Timedelta(days=1)]))
        monkeypatch.setattr(am, "_snapshot_rows", lambda s, e: _snap_df(more))
        assert load_phase_panel().index[-1] == more[-1 - PIT_TAIL_LAG]

    def test_insufficient_snapshot_raises(self, monkeypatch):
        monkeypatch.setattr(am, "_snapshot_rows",
                            lambda s, e: _snap_df(pd.bdate_range("2026-01-05", periods=PIT_TAIL_LAG)))
        with pytest.raises(RuntimeError, match="无判定样本"):
            load_phase_panel()


# ---------- ② SLE-3③：微观相位 overlay 可达 + 宏观冰点/复苏优先 ----------
def _rally_then_break_breadth():
    """定稿 v2 合成序列：400 日横盘 → 30 日亢奋拉升 → 破位退潮（全 trailing，无前视）。"""
    n = 460
    dates = pd.bdate_range("2025-01-01", periods=n)
    close = np.full(n, 100.0)
    rng = np.random.default_rng(7)
    close *= 1.0 + rng.normal(0, 1e-4, n)  # 微噪声防分位退化
    adv = np.full(n, 500.0)
    e0, e1 = 400, 430  # 亢奋段：拉升+广度占优
    close[e0:e1] = close[e0 - 1] * np.cumprod(np.full(e1 - e0, 1.015))
    adv[e0:e1] = 900.0
    b0 = e1 + 2  # 破位段：价格跌破 MA20 且广度转弱
    close[b0:] = close[b0 - 1] * np.cumprod(np.full(n - b0, 0.985))
    adv[b0:] = 100.0
    return pd.DataFrame({"close": close, "adv": adv, "dec": 1000.0 - adv}, index=dates)


class TestPhaseOverlay:
    def test_euphoria_and_distribution_detectable(self):
        br = _rally_then_break_breadth()
        ov = phase_overlay(br)
        assert ov["euphoria"].sum() >= 5, "亢奋段应被探测（改造前六段轴恒 0 的盲区）"
        assert ov["distribution"].sum() >= 5, "退潮段应被探测"
        first_euph = ov.index[ov["euphoria"]][0]
        first_dist = ov.index[ov["distribution"]][0]
        assert first_dist > first_euph  # 退潮需亢奋记忆窗（先亢奋后派发）

    def test_overlay_feeds_six_phase_with_preemption(self):
        br = _rally_then_break_breadth()
        ov = phase_overlay(br)
        # 震荡宏观态 r2（R2SIX 不路由）日由微观腿补出 euphoria/distribution
        dom = pd.Series("r2", index=br.index)
        six = resolve_six_phase(dom, ov)
        assert (six[ov["distribution"]] == "distribution").all()
        assert (six[ov["euphoria"] & ~ov["distribution"]] == "euphoria").all()  # 双读日按派发优先
        assert set(R2SIX.values()).isdisjoint({"euphoria", "distribution"})  # 盲区实锤：宏观腿永不出这两态
        # 冰点/复苏优先：r10 日即使微观读亢奋也不被覆盖
        dom2 = dom.copy()
        eu_day = ov.index[ov["euphoria"]][0]
        dom2.loc[eu_day] = "r10"
        six2 = resolve_six_phase(dom2, ov)
        assert six2.loc[eu_day] == "capitulation"
        # distribution 优先于 euphoria（同日双读=派发不按亢奋路由）
        ov3 = ov.copy()
        ov3["distribution"] = ov3["distribution"] | ov3["euphoria"]
        assert (resolve_six_phase(dom, ov3)[ov["euphoria"]] != "euphoria").all()

    def test_candidate_states_expose_overlay_phases_to_l1(self):
        # 候选态已含 overlay 两相（L1 防御格不再永不触发的语义前提）
        assert {"euphoria", "distribution"} <= CLASS_CANDIDATE_STATES["value_reversal"]


# ---------- ②端到端 + ③FDR 门：judge → apply_multiple_testing → activated ----------
class _FakeMod:
    def build(self, start, end):
        return None, None


class _FakeC4:
    def __init__(self, net: pd.Series):
        self._net = net

    def daily_net_returns(self, weights, closes):
        return self._net


def _panel_with_phases(days: int = 300) -> pd.DataFrame:
    idx = pd.bdate_range("2025-01-02", periods=days)
    six = pd.Series(np.nan, index=idx, dtype=object)
    six[100:161] = "euphoria"
    return pd.DataFrame({"dom": "r2", "euphoria": True, "distribution": False, "six": six})


def _seg(p: float, **kw) -> dict:
    st = {"n": 61, "sr": 2.5, "vol": 0.18, "t": 4.0, "p": p,
          "oos_n": 0, "oos_sr": 0.0}
    st.update(kw)
    return st


class TestEuphoriaEndToEnd:
    def test_euphoria_can_activate_through_fdr_gate(self, monkeypatch):
        panel = _panel_with_phases()
        rng = np.random.default_rng(3)
        net = pd.Series(0.0, index=panel.index)
        eu = panel["six"] == "euphoria"
        net[eu] = 0.003 + rng.normal(0, 0.0005, int(eu.sum()))   # 亢奋段显著正超额
        net[~eu] = 0.0001 + rng.normal(0, 0.0005, int((~eu).sum()))
        monkeypatch.setattr(am, "_load_translated_module", lambda rel: _FakeMod())
        monkeypatch.setitem(sys.modules, "_c4_engine", _FakeC4(net))
        j = am.judge_activation_state("STR-FAKE-001", "value_reversal", "x.py", panel)
        assert "euphoria" in j["segments"], "解冻+补映射后亢奋相位必须进入检验队列"
        assert j["segments"]["euphoria"]["n"] == int(eu.sum())
        receipt = apply_multiple_testing([j], q=am.FDR_Q)
        assert receipt["m"] >= 1 and "euphoria" in j["activated"]
        assert j["segments"]["euphoria"]["accepted"] is True


class TestBhyFdrGate:
    def test_accept_reject_boundary_q10(self):
        # 族 p 值 {0.001,0.001,0.005,0.02,0.2}，BHY q=0.10 m=5：c(5)=2.2833，
        # crit_i=i·q/(m·c)=i·0.008759 → [0.0088,0.0175,0.0263,0.0350,0.0438]；
        # 升序 0.001/0.001/0.005/0.02 均 ≤ 对应临界 → k=4 拒绝 H0；0.2 > 0.0438 保留。
        j1 = {"sid": "A", "activated": [], "segments": {"euphoria": _seg(0.001),
                                                        "distribution": _seg(0.2)}}
        j2 = {"sid": "B", "activated": [], "segments": {
            "accumulation": _seg(0.02),
            "capitulation": _seg(0.005, sr=-1.5),                    # FDR 过但方向为负
            "expansion": _seg(0.001, oos_n=40, oos_sr=-0.9)}}        # FDR 过但 OOS 反向
        receipt = apply_multiple_testing([j1, j2], q=0.10)
        assert receipt["m"] == 5 and receipt["n_rejected"] == 4
        assert j1["activated"] == ["euphoria"]
        assert j1["segments"]["distribution"]["fdr_rejected"] is False
        assert "FDR" in j1["segments"]["distribution"]["reject_reason"]
        assert j2["activated"] == ["accumulation"]
        assert "SR=" in j2["segments"]["capitulation"]["reject_reason"]
        assert "OOS 反向" in j2["segments"]["expansion"]["reject_reason"]

    def test_large_family_hlz_upgrade(self):
        segs = {f"s{i:03d}": _seg(1e-4, t=2.5) for i in range(102)}  # >FDR_LARGE_FAMILY
        j = {"sid": "BIG", "activated": [], "segments": segs}
        receipt = apply_multiple_testing([j], q=0.10)
        assert receipt["hlz"] is True and receipt["n_rejected"] == 102  # FDR 全拒 H0
        assert j["activated"] == []  # 但大族 t=2.5<2.8 一律不放行
        assert "2.8" in j["segments"]["s000"]["reject_reason"]

    def test_no_family_noop(self):
        assert apply_multiple_testing([], q=0.10)["m"] == 0


# ---------- B2 接线：auto_mount.py:125 点名的 R2SIX 漂移守卫件（此前只有名字没有实现） ----------
def test_r2six_drift_guard_vs_framework_composer():
    # framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE 是 R2SIX 的组合期孪生表
    # （其文件头自述"两处必须同步"），任何一侧改动必须同批——漂移即红。
    from zephyr.pf_core.strategy_engine.framework_composer import (
        REGIME_STATE_TO_ACTIVATION_PHASE,)
    assert R2SIX == REGIME_STATE_TO_ACTIVATION_PHASE
