# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_paper_pool_gate.py | paper池进池判据门 单测
"""paper_pool_gate 单测：合成已知真值验证三线判定 + Bonferroni/DSR 校正数学（零 DB 零 CH）。

合成设计（已知真值构造，非对拍自身输出）：
- Bonferroni 真值 = 解析式 p_single=2(1−Φ(|t|))、p_mult=min(1,p_single·N)，用 statistics.NormalDist
  独立重算对拍（与被测 erfc 路径数学恒等但数值路径不同）；
- "运气 vs 真技巧"分界用 t=ICIR·√T 的解析可控性构造：T=60、ICIR=0.35 → t=2.71，
  N=1 时 p_mult=0.0067<0.05 过、N=143 时 p_mult=0.96 被聚合层折掉——同一样本仅 N 不同，
  判定翻转即校正层在干活（裁定#489③"143 候选×运气=必然假阳"的机理复现）；
- DSR 全序列路径用精确零均值化噪声（中心化后 ICIR≡0，t≡0，DSR=Φ(−E[maxZ])<0.5 确定性不显著）
  与强技巧序列（ICIR≈0.3·√T 量级 t≈6.7，DSR≥0.95）两头夹逼。
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pytest

FEXAM = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"
if str(FEXAM) not in sys.path:
    sys.path.insert(0, str(FEXAM))

from paper_pool_gate import (  # noqa: E402
    BONFERRONI_ALPHA,
    PAPER_POOL_PASS_LINE,
    aggregate_correction,
    dsr_from_ic_series,
    paper_pool_entry,
    paper_pool_from_factor_book,
    three_lines_and,
)

from zephyr.simulation.deflated_sharpe_calculator import (  # noqa: E402
    DSR_SIGNIFICANCE_THRESHOLD,
    SimulationError,
)

_NORM = NormalDist()


def _p_two_sided(t: float) -> float:
    """解析真值：双侧 p = 2(1−Φ(|t|))（独立数值路径，与被测 erfc 路径对拍）。"""
    return 2.0 * (1.0 - _NORM.cdf(abs(t)))


# ---------- 三线判定（裁定#489③ 冻结 v1） ----------


def test_three_lines_all_pass():
    ok, reasons = three_lines_and(ic=0.05, icir=0.6, retain=0.8)
    assert ok is True
    assert reasons == ["三线全过"]


def test_three_lines_each_line_violated():
    for kwargs, frag in (
        ({"ic": 0.01, "icir": 0.6, "retain": 0.8}, "|ic|"),  # IC 线不过
        ({"ic": 0.05, "icir": 0.2, "retain": 0.8}, "icir"),  # ICIR 线不过
        ({"ic": 0.05, "icir": 0.6, "retain": 0.4}, "retain"),  # 衰减线不过
    ):
        ok, reasons = three_lines_and(**kwargs)
        assert ok is False, kwargs
        assert any(frag in r for r in reasons), (kwargs, reasons)


def test_three_lines_nonfinite_failclosed():
    for kwargs in (
        {"ic": float("nan"), "icir": 0.6, "retain": 0.8},
        {"ic": 0.05, "icir": float("inf"), "retain": 0.8},
        {"ic": 0.05, "icir": 0.6, "retain": float("nan")},
    ):
        ok, reasons = three_lines_and(**kwargs)
        assert ok is False
        assert any("非有限" in r for r in reasons)


def test_pass_line_matches_roster_prereg_v1():
    """防漂移交叉核对：本门冻结线必须与 roster.PREREG_V1 因子及格线同值（裁定#489③=冻结同一组数）。"""
    from roster import PREREG_V1  # noqa: E402 — path 注入后平铺导入（同簇测试惯例）

    prereg = PREREG_V1["factor_pass_line"]
    for key, val in PAPER_POOL_PASS_LINE.items():
        assert float(prereg[key]) == float(val), f"漂移: {key} 本门={val} vs prereg={prereg[key]}"


# ---------- 聚合层 Bonferroni 校正（解析真值对拍） ----------


def test_bonferroni_matches_analytic_truth():
    r = aggregate_correction(icir=0.29, n_obs=100, num_candidates=10, method="bonferroni")
    t_expected = 0.29 * math.sqrt(100)
    assert r["t_single"] == pytest.approx(t_expected, rel=1e-12)
    assert r["p_single"] == pytest.approx(_p_two_sided(t_expected), rel=1e-9)
    assert r["p_bonferroni"] == pytest.approx(min(1.0, _p_two_sided(t_expected) * 10), rel=1e-9)
    # t=2.9, N=10: p_mult≈0.0373<0.05 → 过
    assert r["bonferroni_pass"] is True


def test_bonferroni_alpha_boundary_two_sides():
    """alpha 边界两侧各造一样本：p_mult 恰跨 0.05 的判定翻转（校正数学方向正确性）。"""
    # N=10 → 单检验线 p_single<0.005；t=2.9→p≈0.0037 过 / t=2.7→p≈0.0069 不过
    r_pass = aggregate_correction(icir=0.29, n_obs=100, num_candidates=10, method="bonferroni")
    r_fail = aggregate_correction(icir=0.27, n_obs=100, num_candidates=10, method="bonferroni")
    assert r_pass["p_bonferroni"] < BONFERRONI_ALPHA and r_pass["bonferroni_pass"] is True
    assert r_fail["p_bonferroni"] > BONFERRONI_ALPHA and r_fail["bonferroni_pass"] is False


def test_bonferroni_aggregate_layer_bites_luck():
    """裁定#489③ 机理复现：同一样本（T=60, ICIR=0.35, t=2.71），N=1 过、N=143 被折——
    三线全过的'运气候选'只有聚合层校正挡得住。"""
    luck = {"icir": 0.35, "n_obs": 60}
    solo = aggregate_correction(icir=luck["icir"], n_obs=luck["n_obs"], num_candidates=1, method="bonferroni")
    batch = aggregate_correction(icir=luck["icir"], n_obs=luck["n_obs"], num_candidates=143, method="bonferroni")
    assert solo["bonferroni_pass"] is True  # 单指标阈值视角：p=0.0067<0.05 放行
    assert batch["p_bonferroni"] == pytest.approx(min(1.0, solo["p_single"] * 143), rel=1e-9)
    assert batch["p_bonferroni"] > BONFERRONI_ALPHA and batch["bonferroni_pass"] is False
    # 剪发读数（SSOT 复用）：N=1 无多重测试折减（haircut 恒 0，SSOT 数学性质），
    # N=143 剪发严格为正且剪后 ICIR 更低
    assert solo["haircut_fraction"] == 0.0
    assert batch["haircut_fraction"] > solo["haircut_fraction"]
    assert batch["corrected_icir"] < solo["corrected_icir"]


def test_correction_method_closed_set():
    r_bonf = aggregate_correction(icir=0.5, n_obs=60, num_candidates=5, method="bonferroni")
    assert r_bonf["dsr_pass"] is None and r_bonf["dsr"] is None  # 未选 DSR → None 非 False
    # N=5, t=0.5·√60=3.87 → p_mult≈5.4e-4<0.05：bonferroni 读数照出且判定可复核
    r_dsr = aggregate_correction(icir=0.5, n_obs=60, num_candidates=5, method="dsr")
    assert r_dsr["bonferroni_pass"] is True
    assert r_dsr["dsr_pass"] is True


# ---------- DSR 校正（合成已知真值） ----------


def test_dsr_moments_skill_vs_luck():
    """矩路径两头夹逼：强技巧（t≈10）DSR≥0.95 过；运气（t=2.71, N=143）DSR≈0.49 不过。"""
    strong = aggregate_correction(icir=0.45, n_obs=500, num_candidates=143, method="dsr")
    assert strong["dsr"] >= DSR_SIGNIFICANCE_THRESHOLD and strong["dsr_pass"] is True
    assert strong["dsr_degenerate"] is False
    luck = aggregate_correction(icir=0.35, n_obs=60, num_candidates=143, method="dsr")
    assert luck["dsr"] < 0.6 and luck["dsr_pass"] is False


def test_dsr_monotone_in_num_candidates():
    """校正单调性：同一样本，N 越大 DSR 越低（多重测试惩罚方向正确）。"""
    dsr_n1 = aggregate_correction(icir=0.35, n_obs=60, num_candidates=1, method="dsr")["dsr"]
    dsr_n143 = aggregate_correction(icir=0.35, n_obs=60, num_candidates=143, method="dsr")["dsr"]
    assert dsr_n1 > dsr_n143


def test_dsr_series_exact_zero_skill_never_significant():
    """全序列路径·确定性真值：精确中心化噪声 ICIR≡0 → t≡0 → DSR=Φ(−E[maxZ])<0.5 必不显著。"""
    rng = np.random.default_rng(20261007)
    noise = rng.normal(0.0, 1.0, 250)
    noise = noise - noise.mean()  # 精确零均值：技能严格为零，非抽样近似
    res = dsr_from_ic_series(noise.tolist(), num_candidates=143)
    assert res["dsr_degenerate"] is False
    assert res["dsr_pass"] is False
    assert res["dsr"] < 0.5


def test_dsr_series_strong_skill_survives():
    """全序列路径：ICIR=0.3 的强技巧长序列（t≈6.7）在 N=143 聚合折减下仍显著。

    已知真值构造：精确中心化噪声（零技能）+ 常数 0.3 漂移 → 均值精确 0.3、std≈1，
    消除抽样波动对断言的干扰（与 test_dsr_moments 的抽样版互为补充）。
    """
    rng = np.random.default_rng(7)
    noise = rng.normal(0.0, 1.0, 500)
    noise = noise - noise.mean()  # 技能严格为零
    skill = (noise + 0.3).tolist()
    res = dsr_from_ic_series(skill, num_candidates=143)
    assert res["dsr_degenerate"] is False
    assert res["dsr_pass"] is True
    assert res["dsr"] >= DSR_SIGNIFICANCE_THRESHOLD


def test_dsr_series_zero_variance_degenerate_failclosed():
    res = dsr_from_ic_series([0.5] * 50, num_candidates=143)
    assert res["dsr_degenerate"] is True
    assert res["dsr_pass"] is False
    assert res["dsr"] == 0.0


def test_dsr_series_too_short_failclosed():
    res = dsr_from_ic_series([0.1, 0.2], num_candidates=143)
    assert res["dsr_degenerate"] is True and res["dsr_pass"] is False


# ---------- 单对象进池判定 ----------


def test_paper_pool_entry_luck_cut_at_batch_scale():
    """三线全过的运气候选：N=143 双校正全折 → decision False；同值 N=1 → 进池。"""
    luck = dict(ic=0.03, icir=0.35, retain=0.6, n_obs=60)
    batch = paper_pool_entry(num_candidates=143, object_id="FCT-LUCKY", **luck)
    assert batch.three_lines_pass is True
    assert batch.bonferroni_pass is False
    assert batch.dsr_pass is False
    assert batch.decision is False
    assert any("Bonferroni" in r for r in batch.reasons)
    assert any("DSR" in r for r in batch.reasons)
    solo = paper_pool_entry(num_candidates=1, object_id="FCT-SOLO", **luck)
    assert solo.decision is True


def test_paper_pool_entry_strong_skill_admitted_at_batch_scale():
    gate = paper_pool_entry(ic=0.05, icir=0.6, retain=0.8, n_obs=250, num_candidates=143, object_id="FCT-STRONG")
    assert gate.decision is True
    assert gate.bonferroni_pass is True and gate.dsr_pass is True
    assert gate.corrected_icir > 0.0  # 剪发后 ICIR 仍为正（选择效应未剪没）


def test_paper_pool_entry_short_direction_negation():
    """direction=short 由调用方取负（同 ic_exam.judge 口径）：正 ICIR 值才进池，原始负值被三线折。"""
    ok = paper_pool_entry(ic=0.05, icir=0.6, retain=0.8, n_obs=250, num_candidates=5)
    flipped = paper_pool_entry(ic=-0.05, icir=-0.6, retain=0.8, n_obs=250, num_candidates=5)
    assert ok.decision is True
    assert flipped.three_lines_pass is False and flipped.decision is False


def test_paper_pool_entry_method_bonferroni_only():
    """method='bonferroni'：只看家族错误率，DSR 位 None 不参与判定（裁定#489③ 单选校正语义）。"""
    gate = paper_pool_entry(ic=0.03, icir=0.35, retain=0.6, n_obs=60, num_candidates=143, method="bonferroni")
    assert gate.bonferroni_pass is False
    assert gate.dsr_pass is None
    assert gate.decision is False


def test_paper_pool_entry_nonfinite_failclosed_no_raise():
    for kwargs in (
        {"ic": float("nan"), "icir": 0.5, "retain": 0.8, "n_obs": 60, "num_candidates": 5},
        {"ic": 0.05, "icir": float("nan"), "retain": 0.8, "n_obs": 60, "num_candidates": 5},
        {"ic": 0.05, "icir": 0.5, "retain": float("nan"), "n_obs": 60, "num_candidates": 5},
    ):
        gate = paper_pool_entry(**kwargs)
        assert gate.decision is False
        assert gate.dsr_degenerate is True  # "判不了"绝不翻译成放行
        assert gate.bonferroni_pass is False


def test_paper_pool_entry_ic_series_overrides_moments_dsr():
    """给了原始 IC 序列 → DSR 走全序列路径（矩自估），读数与矩路径同向。"""
    rng = np.random.default_rng(11)
    series = (rng.normal(0.35, 1.0, 200)).tolist()
    gate = paper_pool_entry(
        ic=0.05, icir=0.35, retain=0.7, n_obs=200, num_candidates=10, ic_series=series, object_id="FCT-SER"
    )
    assert gate.dsr_pass is True
    assert any("全序列路径" in r for r in gate.reasons)


# ---------- 参数校验（fail-closed 错误契约） ----------


def test_validation_errors():
    with pytest.raises(SimulationError):
        aggregate_correction(icir=0.5, n_obs=60, num_candidates=0)
    with pytest.raises(SimulationError):
        aggregate_correction(icir=0.5, n_obs=1, num_candidates=5)
    with pytest.raises(SimulationError):
        aggregate_correction(icir=float("nan"), n_obs=60, num_candidates=5)
    with pytest.raises(SimulationError):
        aggregate_correction(icir=0.5, n_obs=60, num_candidates=5, method="hlz_2016")  # 闭合集外
    with pytest.raises(SimulationError):
        paper_pool_entry(ic=0.05, icir=0.5, retain=0.8, n_obs=60, num_candidates=True)  # bool 冒充 int
    with pytest.raises(SimulationError):
        dsr_from_ic_series([0.1, 0.2, 0.3], num_candidates=0)


# ---------- 分数册级进池建议单（机生） ----------


def _mk_result(oid, verdict, ic, icir, retain, n_obs, direction="long"):
    return {
        "object_id": oid,
        "verdict": verdict,
        "direction": direction,
        "metrics": {"per_horizon": {"5": {"holdout": {"ic_mean": ic, "icir": icir, "n_obs": n_obs}, "retain": retain}}},
    }


def _synth_factor_book():
    """合成因子分数册：真技巧 1（long）+1（short）+ 聚合层运气 1 + 度量缺失 1 + 140 个实测 rework 填充。

    N=144 时：LUCKY（t=2.71）p_mult≈0.96>0.05、DSR≈0.49 双折；STRONG（t=9.49）双过 → 进池。
    """
    results = [
        _mk_result("FCT-STRONG", "pass", 0.05, 0.6, 0.8, 250),
        _mk_result("FCT-SHORT", "pass", -0.05, -0.6, 0.8, 250, direction="short"),
        _mk_result("FCT-LUCKY", "pass", 0.03, 0.35, 0.6, 60),
        {"object_id": "FCT-NOMETRICS", "verdict": "pass", "metrics": {}},
        _mk_result("FCT-REWORK-STRONG", "rework", 0.06, 0.7, 0.9, 250),  # 考试层已折，进池层无视
    ]
    results += [_mk_result(f"FCT-F{i:03d}", "rework", 0.005, 0.05, 0.3, 60) for i in range(140)]
    return {"prereg_v1": {"headline_horizon": 5}, "results": results}


def test_paper_pool_from_factor_book_end_to_end():
    pool = paper_pool_from_factor_book(_synth_factor_book())
    assert pool["doc_type"] == "fexam_paper_pool_gate"
    assert pool["ruling_ref"] == "裁定#489③"
    assert (
        pool["num_candidates"] == 144
    )  # 实测候选数（STRONG+SHORT+LUCKY+REWORK 4 实测+140 填充，含 rework——聚合层 N 如实）
    assert pool["measured_candidates"] == 144
    assert pool["exam_pass_total"] == 4
    assert set(pool["admitted"]) == {"FCT-STRONG", "FCT-SHORT"}  # short 方向取负后进池
    rejected = {r["object_id"]: r["reasons"] for r in pool["rejected"]}
    assert "FCT-LUCKY" in rejected  # 聚合层校正折掉的运气候选
    assert any("Bonferroni" in r for r in rejected["FCT-LUCKY"])
    assert any("fail-closed" in r for r in rejected["FCT-NOMETRICS"])  # 度量缺失不进池
    assert "FCT-REWORK-STRONG" not in rejected and "FCT-REWORK-STRONG" not in pool["admitted"]


def test_paper_pool_from_factor_book_empty_book():
    pool = paper_pool_from_factor_book({"results": []})
    assert pool["admitted"] == [] and pool["rejected"] == []
    assert pool["measured_candidates"] == 0


def test_paper_pool_from_factor_book_pass_without_measured_candidates():
    """全部 pass 但零实测候选（结构异常册）：N=0 无校正基准 → fail-closed 全不进池。"""
    book = {
        "prereg_v1": {"headline_horizon": 5},
        "results": [{"object_id": "FCT-X", "verdict": "pass", "metrics": {}}],
    }
    pool = paper_pool_from_factor_book(book)
    assert pool["num_candidates"] == 0
    assert pool["admitted"] == []
    assert pool["rejected"][0]["object_id"] == "FCT-X"
