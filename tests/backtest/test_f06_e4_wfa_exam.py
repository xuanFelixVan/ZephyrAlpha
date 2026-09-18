# [BLUEPRINT] MOD-BT-211 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.backtest.test_f06_e4_wfa_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.f06_e4_wfa_exam
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 折切分无泄露（每折训练窗全部早于测试窗+测试窗互不重叠，合成数据机械验证）；三线 verdict 映射经真实 DecisionGate+OverfittingDetector 管线驱动（零真库依赖）；阈值全取注册常量；判定族夹具三维度全供数（R-055b 起"缺维=不可判定=不通过"，缺位维数由检测器实报的 not_assessed_dimensions 反推，禁写死）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_f06_e4_wfa_exam.py — F-06 E4 WFA 正考件单元测试（合成数据，无 CH 依赖）。"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "f06_e4_wfa_exam", _REPO / "scripts" / "backtest" / "f06_e4_wfa_exam.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)

from zephyr.backtest.core.decision_gate import evaluate_dsr
from zephyr.backtest.core.strategy_validation_pipeline import StrategyValidationRequest, run_strategy_validation


class TestBuildFolds:
    def test_default_scheme_8_folds_2020_to_2025_08(self) -> None:
        folds = mod.build_folds("2020-01-01", "2025-08-31", train_months=24, test_months=6, step_months=6)
        assert len(folds) == 8
        f0, f7 = folds[0], folds[-1]
        assert f0["train_start"] == pd.Timestamp("2020-01-01")
        assert f0["train_end"] == pd.Timestamp("2021-12-31")
        assert f0["test_start"] == pd.Timestamp("2022-01-01")
        assert f0["test_end"] == pd.Timestamp("2022-06-30")
        # 末折测试窗截到全窗尾 2025-08-31
        assert f7["test_start"] == pd.Timestamp("2025-07-01")
        assert f7["test_end"] == pd.Timestamp("2025-08-31")
        assert [f["fold"] for f in folds] == list(range(8))

    def test_no_overlap_leakage_train_all_before_test(self) -> None:
        folds = mod.build_folds("2020-01-01", "2025-08-31")
        for i, f in enumerate(folds):
            # 每折训练窗全部早于测试窗（无重叠泄露）
            assert f["train_end"] < f["test_start"]
            assert f["train_start"] < f["train_end"]
            if i > 0:
                prev = folds[i - 1]
                # 测试窗互不重叠且时序递增
                assert prev["test_end"] < f["test_start"]
                # 步进 6 个月: 下折训练窗起点 = 上折训练窗起点 + step
                assert f["train_start"] == prev["train_start"] + pd.DateOffset(months=6)

    def test_window_widths_exact_months(self) -> None:
        folds = mod.build_folds("2020-01-01", "2025-08-31")
        for f in folds[:-1]:
            assert f["train_start"] + pd.DateOffset(months=24) - pd.Timedelta(days=1) == f["train_end"]
            assert f["test_start"] + pd.DateOffset(months=6) - pd.Timedelta(days=1) == f["test_end"]

    def test_step_smaller_than_test_raises(self) -> None:
        # step < test 会使测试窗重叠 → 拼接路径不可交易 → 构造期即拒绝
        with pytest.raises(ValueError, match="重叠"):
            mod.build_folds("2020-01-01", "2025-08-31", train_months=24, test_months=6, step_months=3)

    def test_invalid_params_raise(self) -> None:
        with pytest.raises(ValueError, match="train_months"):
            mod.build_folds("2020-01-01", "2025-08-31", train_months=0)
        with pytest.raises(ValueError, match="非法"):
            mod.build_folds("2025-01-01", "2024-01-01")

    def test_window_too_short_raises(self) -> None:
        with pytest.raises(ValueError, match="不足以切出任何折"):
            mod.build_folds("2020-01-01", "2020-06-30", train_months=24, test_months=6)

    def test_custom_scheme_folds(self) -> None:
        folds = mod.build_folds("2020-01-01", "2022-12-31", train_months=12, test_months=6, step_months=6)
        assert len(folds) >= 3
        for i, f in enumerate(folds):
            assert f["train_end"] < f["test_start"]
            if i > 0:
                assert folds[i - 1]["test_end"] < f["test_start"]


class TestStitchAndFoldMetrics:
    def _w(self, start: str, end: str, col: str = "000001") -> pd.DataFrame:
        idx = pd.bdate_range(start, end)
        return pd.DataFrame(0.5, index=idx, columns=[col])

    def test_stitch_concat_and_order(self) -> None:
        w1, w2 = self._w("2022-01-03", "2022-02-28"), self._w("2022-03-01", "2022-04-29")
        st = mod.stitch_fold_weights({1: w2, 0: w1})
        assert len(st) == len(w1) + len(w2)
        assert st.index.is_monotonic_increasing and not st.index.has_duplicates

    def test_stitch_overlap_raises(self) -> None:
        w1, w2 = self._w("2022-01-03", "2022-02-28"), self._w("2022-02-01", "2022-04-29")
        with pytest.raises(ValueError, match="重叠"):
            mod.stitch_fold_weights({0: w1, 1: w2})

    def test_fold_metrics_from_net_known_values(self) -> None:
        folds = mod.build_folds("2020-01-01", "2021-06-30", train_months=6, test_months=6, step_months=6)
        idx = pd.bdate_range("2020-07-01", "2021-06-30")
        # 交替正收益（均值>0、方差>0）: sharpe 为正、累计权益单调上行、回撤 0
        net = pd.Series(([0.0015, 0.0005][i % 2] for i in range(len(idx))), index=idx)
        rows = mod.fold_metrics_from_net(net, folds)
        assert len(rows) == len(folds)
        for r in rows:
            assert r["days"] > 0
            assert r["sharpe"] > 0
            assert r["max_drawdown"] == 0.0
        # 逐折窗口天数与折定义一致
        for r, f in zip(rows, folds):
            seg_days = len(net[(net.index >= f["test_start"]) & (net.index <= f["test_end"])])
            assert r["days"] == seg_days


def _dim2_perturbed_stable(base_sharpe: float) -> list[dict]:
    """过拟合维度2（参数敏感性）供数：微调后 Sharpe 相对变化 ≤3%，远低于 PARAM_MAX_CHANGE_THRESHOLD(0.30)。"""
    return [{"sharpe_ratio": base_sharpe * 0.97}, {"sharpe_ratio": base_sharpe * 1.02}]


def _dim3_periods_stable(oos_sharpe: float) -> list[dict]:
    """过拟合维度3（泛化能力）供数：跨时段 Sharpe 全正，变异系数远低于 GEN_CV_THRESHOLD(1.50)。"""
    spans = (0.90, 1.00, 0.80)
    return [{"sharpe_ratio": oos_sharpe * f} for f in spans]


def _drive_pipeline(fold_sharpes: list[float], fold_mdds: list[float], is_sharpe: float, oos_sharpe: float, dsr: float | None):
    """经真实管线（run_strategy_validation→DecisionGate+OverfittingDetector）产出判定输入。

    本夹具是"三线 verdict 映射"族的正对照基线：R-055b 把过拟合检测器的口径从
    "未提供的维度=默认稳定"改成"**未提供=不可判定=不通过**"后，只灌维度1 的样本
    不再是"干净通过"而是必然被否决——故此处三维全供数，让每个用例只破它要测的那一条线。
    `n_dims_evaluated` 由检测器实报的 not_assessed_dimensions 反推（旧夹具用默认值 3，
    等于替被测件谎报"证据已评满"，是一条假绿通道）。
    """
    pipe = run_strategy_validation(
        StrategyValidationRequest(
            strategy_id="t-E4WFA",
            is_sharpe=is_sharpe,
            params={"k": "v"},
            param_sensitivity=None,
            walk_forward_results=[
                {"sharpe": s, "max_drawdown": m} for s, m in zip(fold_sharpes, fold_mdds)
            ],
            oos_sharpe=oos_sharpe,
            params_locked=True,
            perturbed_results=_dim2_perturbed_stable(is_sharpe),
            period_results=_dim3_periods_stable(oos_sharpe),
            dsr=dsr,
        )
    )
    band = evaluate_dsr(dsr).band
    n_dims = mod.OVERFIT_DIMENSIONS_TOTAL - len(pipe.overfitting.get("not_assessed_dimensions", ()))
    return mod.map_exam_verdict(pipe.gate, pipe.overfitting, band, n_dims_evaluated=n_dims), pipe


class TestExamVerdictThreeLines:
    def test_pass_all_stages_clean(self) -> None:
        # 正对照：三维度全供数 + 三线全绿 ⇒ 唯一合法的 VERDICT_PASS 面
        # （缺任一维即被 R-055b 判不可判定，见 test_rb_stats_validator_teeth.py 的对照件）
        (verdict, _), pipe = _drive_pipeline(
            fold_sharpes=[1.0] * 8, fold_mdds=[-0.05] * 8, is_sharpe=1.5, oos_sharpe=1.2, dsr=0.99
        )
        assert pipe.gate.overall_passed and not pipe.overfitting["is_overfitting"]
        assert verdict == mod.VERDICT_PASS

    def test_fail_wfa_majority_not_passed(self) -> None:
        # 4/8 正折 = 50% 不大于多数线 50% → WFA 未过 → 不可跳级判不通过
        (verdict, reasons), pipe = _drive_pipeline(
            fold_sharpes=[1.0, 1.0, 1.0, 1.0, -0.2, -0.2, -0.2, -0.2],
            fold_mdds=[-0.05] * 8,
            is_sharpe=1.5,
            oos_sharpe=0.5,
            dsr=0.99,
        )
        assert not pipe.gate.wfa_stage.passed
        assert verdict == mod.VERDICT_FAIL
        assert any("WFA" in r for r in reasons)

    def test_fail_oos_ratio_below_p09_line(self) -> None:
        # WFA 全过但 OOS/IS=0.333 < 0.70（P0-9 硬否决线）
        (verdict, reasons), pipe = _drive_pipeline(
            fold_sharpes=[1.0] * 8, fold_mdds=[-0.05] * 8, is_sharpe=1.5, oos_sharpe=0.5, dsr=0.99
        )
        assert pipe.gate.wfa_stage.passed
        assert pipe.gate.oos_stage.oos_is_ratio < 0.70
        assert verdict == mod.VERDICT_FAIL
        assert any("0.70" in r or "P0-9" in r for r in reasons)

    def test_fail_disaster_drawdown(self) -> None:
        # 单折回撤 -0.6 超灾难否决线 0.5 → WFA 灾难否决
        mdds = [-0.05] * 7 + [-0.60]
        (verdict, _), pipe = _drive_pipeline(
            fold_sharpes=[1.0] * 8, fold_mdds=mdds, is_sharpe=1.5, oos_sharpe=1.2, dsr=0.99
        )
        assert pipe.gate.wfa_stage.has_disaster
        assert verdict == mod.VERDICT_FAIL

    def test_review_dsr_middle_band_only(self) -> None:
        # 各硬线全过（比率 0.8 >= 0.7），仅 DSR=0.70 落中间带 review → 存疑（fail-closed 不放行）
        (verdict, reasons), pipe = _drive_pipeline(
            fold_sharpes=[1.0] * 8, fold_mdds=[-0.05] * 8, is_sharpe=1.5, oos_sharpe=1.2, dsr=0.70
        )
        assert pipe.gate.wfa_stage.passed
        assert pipe.gate.oos_stage.oos_is_ratio >= 0.70
        assert not pipe.gate.overall_passed  # DSR 中间带 fail-closed
        assert verdict == mod.VERDICT_REVIEW
        assert any("存疑" in r for r in reasons)

    def test_fail_dsr_overfitting_band(self) -> None:
        # 比率过线但 DSR=0.3 落否决带（< 0.5 运气中值）→ 不通过
        (verdict, _), pipe = _drive_pipeline(
            fold_sharpes=[1.0] * 8, fold_mdds=[-0.05] * 8, is_sharpe=1.5, oos_sharpe=1.2, dsr=0.30
        )
        assert pipe.gate.oos_stage.oos_is_ratio >= 0.70
        assert verdict == mod.VERDICT_FAIL

    def test_fail_dsr_unavailable_is_fail_closed(self) -> None:
        # DSR 未注入 = unavailable → fail-closed 判不通过（禁误放行）
        (verdict, _), pipe = _drive_pipeline(
            fold_sharpes=[1.0] * 8, fold_mdds=[-0.05] * 8, is_sharpe=1.5, oos_sharpe=1.2, dsr=None
        )
        assert evaluate_dsr(None).band == "unavailable"
        assert verdict == mod.VERDICT_FAIL


class TestLoadSurvivorRecord:
    def test_read_registered_row(self, tmp_path: Path) -> None:
        csv = tmp_path / "survivors.csv"
        values = {"A1_factor_normalize": "raw", "G_universe": "hs300"}
        row = {
            "recipe_id": "38b453ca3683",
            "birth_batch": "grid_x",
            "values_json": json.dumps(values),
            "is_sharpe": 1.721,
            "is_window": "2020-01-01..2023-12-31",
            "dsr_eff": 0.9593,
            "n_trials_eff": 9,
            "n_trials_raw": 10080,
            "oos_sharpe": 0.831,
            "oos_window": "2024-01-01..2025-08-31",
            "mechanism": "机制",
        }
        pd.DataFrame([row]).to_csv(csv, index=False)
        rec = mod.load_survivor_record(csv, "38b453ca3683")
        assert rec["values"] == values
        assert rec["is_sharpe"] == pytest.approx(1.721)
        assert rec["n_trials_eff"] == 9 and rec["n_trials_raw"] == 10080
        assert rec["oos_sharpe_registered"] == pytest.approx(0.831)

    def test_missing_recipe_raises(self, tmp_path: Path) -> None:
        csv = tmp_path / "survivors.csv"
        csv.write_text("recipe_id,values_json,is_sharpe\nabc,{},1.0\n", encoding="utf-8")
        with pytest.raises(RuntimeError, match="不在幸存者登记面"):
            mod.load_survivor_record(csv, "38b453ca3683")

    def test_missing_csv_raises(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError, match="登记面缺失"):
            mod.load_survivor_record(tmp_path / "nope.csv", "x")
