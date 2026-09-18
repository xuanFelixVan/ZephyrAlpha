# [BLUEPRINT] MOD-BT-211 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.backtest.test_rb_stats_validator_teeth
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.f06_e4_wfa_exam; zephyr.backtest.core.overfitting_detector; zephyr.backtest.core.strategy_validation_pipeline; zephyr.backtest.core.n_trial_ledger
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 本件是"验证器自身能红"的反假牙测试：全部输入为 numpy 生成的 iid 零均值高斯收益（真值年化 Sharpe=0，不存在 alpha），故任何"通过"判定都是假阳性；DSR 折减分母必须可对账复算，分母不可核验时 E4 禁判通过；过拟合检测器未评估维=R-055b fail-closed（不可判定=不通过），比率门=R-055c 双向（异常好=泄漏否决）；零真库依赖（合成数据 + tmp_path）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""红队 RB-STATS 车道 · 验证器牙齿测试（攻面一=过拟合）。

来源：全流通战役红蓝对抗车道 st-ff-rb-stats-20260918。首役红队自律声明指出
§6 攻击面的"过拟合"与"regime 误报率"两面从未被攻；本件是前者留下的**永久**能红
证据（一次性探针见战役记录，本件负责回归保护）。

四条被钉死的判据：
  1. 诚实折减分母下，纯噪声挑最优**过不了** E4（尺子有牙）。
  2. 把 DSR 分母写小（等价改 f06_survivors.csv 的 n_trials_eff 一列），纯噪声
     **能过**——故 E4 必须对分母做可复算对账，不可核验时禁判"通过"。
  3. OverfittingDetector 三维度中未提供的维度 = **不可判定 = 不通过**（R-055b 治掉了
     原"未检测=默认稳定"的 fail-open）；比率门自 R-055c 起**双向**——OOS/IS 显著>1 是
     选参泄漏签名而非加分项。E4 只评估 1 维时同样不得据此放行。
  4. N_eff 对账函数的三态（verified/mismatch/unverifiable）机械可判。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "f06_e4_wfa_exam", _REPO / "scripts" / "backtest" / "f06_e4_wfa_exam.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)

from zephyr.backtest.core.n_trial_ledger import compute_effective_rank
from zephyr.backtest.core.overfitting_detector import OOS_IS_RATIO_UPPER_BOUND, OverfittingDetector
from zephyr.backtest.core.strategy_validation_pipeline import (
    StrategyValidationRequest,
    run_strategy_validation,
)

PPY = 244.0  # 与 f06_e4_wfa_exam.fold_metrics_from_net 年化口径一致
N_IS = 1100
M_TRIALS = 2000  # 试错次数=参数网格规模（与战役记录的一次性探针同参，数字可复算）
SEED = 20260918


def _sharpe(x: np.ndarray) -> float:
    s = float(x.std())
    return float(x.mean() / s * np.sqrt(PPY)) if s > 0 else 0.0


def _dsr(returns, n_trials: int) -> float:
    from zephyr.simulation.deflated_sharpe_calculator import DeflatedSharpeCalculator, DSRConfig

    return float(
        DeflatedSharpeCalculator(DSRConfig(periods_per_year=int(PPY)))
        .calculate([float(v) for v in returns], num_trials=int(n_trials)).dsr
    )


def _verdict(
    is_sharpe: float,
    oos_sharpe: float,
    dsr: float | None,
    perturbed_results: list[dict] | None = None,
    period_results: list[dict] | None = None,
    **kw,
):
    """用真实管线（DecisionGate + OverfittingDetector）驱动三线 verdict，零 mock 判定件。

    过拟合维度2/3 由入参显式供数（R-055b 起"不供数=不可判定=不通过"，
    故凡想测"四线全绿"的对照组都必须真把三维灌满，否则绿是假的）。
    """
    pipe = run_strategy_validation(
        StrategyValidationRequest(
            strategy_id="RB-STATS-NOISE",
            is_sharpe=float(is_sharpe),
            params={"probe": "noise"},
            walk_forward_results=[{"sharpe": float(oos_sharpe), "max_drawdown": -0.05}] * 8,
            perturbed_results=perturbed_results or [],
            period_results=period_results or [],
            oos_sharpe=float(oos_sharpe),
            params_locked=True,
            dsr=dsr,
        )
    )
    return mod.map_exam_verdict(pipe.gate, pipe.overfitting, mod.evaluate_dsr(dsr).band, **kw), pipe


def _grid() -> np.ndarray:
    """M 条互相独立的纯噪声日收益序列（真值年化 Sharpe 全为 0）。全程固定 seed。"""
    return np.random.default_rng(SEED).normal(0.0, 0.01, size=(M_TRIALS, N_IS + 600))


def _noise_winner(leak: bool = False) -> tuple[float, float, np.ndarray]:
    """返回 (IS sharpe, OOS sharpe, OOS 收益序列)——"从噪声里挑出的最优者"。

    leak=False: 只用 IS 段挑最优（诚实切分，攻击②未得手）。
    leak=True : 用**全样本** sharpe 挑最优（攻击②得手=参数搜索空间泄漏进评估切分），
                随后仍按 IS/OOS 分别计分——正是"搜索用全样本、评估用同一切分"的形态。
    """
    g = _grid()
    score = np.array([_sharpe(s) if leak else _sharpe(s[:N_IS]) for s in g])
    winner = g[int(np.argmax(score))]
    return _sharpe(winner[:N_IS]), _sharpe(winner[N_IS:]), winner[N_IS:]


class TestPureNoiseCannotPass:
    """判据①：诚实分母下，噪声挑最优过不了 E4。"""

    def test_noise_best_of_grid_rejected_by_honest_dsr(self) -> None:
        is_sh, oos_sh, oos_ret = _noise_winner()
        dsr = _dsr(oos_ret, M_TRIALS)
        (verdict, _), _ = _verdict(is_sh, oos_sh, dsr)
        assert verdict != mod.VERDICT_PASS, (
            f"纯噪声（真值 Sharpe=0）被判通过：IS={is_sh} OOS={oos_sh} DSR={dsr} —— 尺子是假牙"
        )

    def test_dsr_denominator_is_what_decides(self) -> None:
        """判据②的前半：同一条（泄漏挑出的）噪声序列，分母从真值改成 1 ⇒ 翻盘。

        这条断言**不是**为放水背书，而是把"分母=唯一命门"钉成事实，
        使任何"把 N 当常数/当可编辑字段"的改动都能被下一条测试拦下。
        """
        _, _, oos_ret = _noise_winner(leak=True)
        honest = _dsr(oos_ret, M_TRIALS)
        bypassed = _dsr(oos_ret, 1)
        assert honest < mod.DSR_OVERFITTING_FLOOR < bypassed, (
            f"噪声序列 DSR：诚实分母={honest} / N=1={bypassed} —— 分母敏感性未被测出"
        )

    def test_full_sample_selection_is_caught_by_the_ratio_ceiling(self) -> None:
        """攻击②得手过（改前）+ 已被 R-055c 治好：全样本选参 ⇒ OOS/IS 远超 1 = 泄漏签名。

        改前此处断言"比率门被反向击穿 ⇒ 唯一还站得住的闸是 DSR"；R-055c 给比率门补了
        上界（=1+PARAM_MAX_CHANGE_THRESHOLD=1.30），本件现在**双向钉死**：
        ①比率确实异常（>上界）②门控确实因此不通过（reasons 里有泄漏字样）。
        """
        is_sh, oos_sh, oos_ret = _noise_winner(leak=True)
        honest = _dsr(oos_ret, M_TRIALS)
        (verdict, _), pipe = _verdict(is_sh, oos_sh, honest)
        assert pipe.gate.oos_stage.oos_is_ratio > mod.DEFAULT_OOS_SHARPE_THRESHOLD_RATIO
        assert pipe.gate.oos_stage.oos_is_ratio > OOS_IS_RATIO_UPPER_BOUND
        assert any("疑似选参泄漏" in x for x in pipe.gate.oos_stage.reasons), "上界未生效=比率门仍是单向"
        assert verdict != mod.VERDICT_PASS

    def test_ratio_ceiling_holds_even_when_dsr_denominator_is_bypassed(self) -> None:
        """★ R-055c 的独立验牙（考试三闸互不替代）：把 DSR 分母放水成 N=1 后，
        改前 E2 会**判通过**（唯一拦它的是 DSR，而 DSR 已被放水）；现比率上界独立拦住。
        """
        is_sh, oos_sh, oos_ret = _noise_winner(leak=True)
        bypassed_dsr = _dsr(oos_ret, 1)
        assert bypassed_dsr >= 0.95, "前提不成立：N=1 的 DSR 未达显著线，本件验不到'放水仍被拦'"
        (verdict, _), pipe = _verdict(
            is_sh,
            oos_sh,
            bypassed_dsr,
            perturbed_results=[{"sharpe_ratio": is_sh * 1.02}],
            period_results=[{"sharpe_ratio": oos_sh}, {"sharpe_ratio": oos_sh}],
        )
        assert pipe.gate.oos_stage.oos_is_ratio > OOS_IS_RATIO_UPPER_BOUND
        assert verdict != mod.VERDICT_PASS, "分母被放水时比率上界必须独立成立（三闸并列）"


class TestEvidenceSufficiencyGates:
    """判据②③的后半：分母不可核验 / 维度未评满时，**任何**输入都不得判通过。"""

    # 门控全绿的构造性入参（IS/WFA/OOS/DSR 四线全过 + 过拟合三维**全供数**）
    # R-055b 后维度2/3 必须供满，否则"绿"本身就是不可判定的假绿（见该案的对照面测试）。
    GREEN = {
        "is_sharpe": 1.5,
        "oos_sharpe": 1.2,
        "dsr": 0.99,
        "perturbed_results": [{"sharpe_ratio": 1.45}, {"sharpe_ratio": 1.52}],
        "period_results": [{"sharpe_ratio": 1.2}, {"sharpe_ratio": 1.3}, {"sharpe_ratio": 1.1}],
    }

    def test_baseline_all_green_does_pass(self) -> None:
        """对照组：三维供满 + 分母已对账时四线全绿即判通过——证明闸门确有放行面。"""
        (verdict, _), pipe = _verdict(**self.GREEN)
        assert pipe.gate.overall_passed and not pipe.overfitting["is_overfitting"]
        assert verdict == mod.VERDICT_PASS

    def test_missing_dimensions_no_longer_pass_by_default(self) -> None:
        """R-055b 行为变更（有意的加严）：同样的四线全绿，**省掉维度2/3** 即不得判通过。

        改前此处 verdict==PASS（"没考的两门按满分计入"）——本件的存在使"缺位维默认稳定"
        一旦回退立刻变红。
        """
        green = {k: v for k, v in self.GREEN.items() if k not in ("perturbed_results", "period_results")}
        (verdict, _), pipe = _verdict(**green)
        assert pipe.overfitting["is_overfitting"] is True
        assert pipe.overfitting["not_assessed_dimensions"] == ("parameter_sensitivity", "generalization")
        assert verdict != mod.VERDICT_PASS

    def test_unverifiable_dsr_denominator_blocks_pass(self) -> None:
        (verdict, reasons), _ = _verdict(dsr_denominator_verified=False, **self.GREEN)
        assert verdict == mod.VERDICT_REVIEW
        assert any("分母" in r for r in reasons)

    def test_partial_overfitting_coverage_blocks_pass(self) -> None:
        (verdict, reasons), _ = _verdict(n_dims_evaluated=1, **self.GREEN)
        assert verdict == mod.VERDICT_REVIEW
        assert any("过拟合" in r for r in reasons)

    def test_real_exam_coverage_never_yields_pass(self) -> None:
        """E4 正考件实参（只评估 1 维）下，最 Favorable 输入也只能到"存疑"。"""
        (verdict, _), _ = _verdict(
            **self.GREEN, n_dims_evaluated=1, dsr_denominator_verified=False
        )
        assert verdict != mod.VERDICT_PASS


class TestOverfittingDetectorFailClosedAfterR055b:
    """判据③（R-055b 落地后改写）：**未提供的维度 = 不可判定 = 不通过**。

    改前此件名为 TestOverfittingDetectorFailOpenPinned，钉的是"缺位维默认稳定"的
    fail-open 形态；总包裁定 R-055b 把方向定为加严后，同一组入参的期望值翻转。
    """

    def test_omitted_dimensions_count_as_not_passed(self) -> None:
        det = OverfittingDetector()
        sparse = det.detect(
            walk_forward_results=[{"sharpe": 1.2, "max_drawdown": -0.05}] * 8,
            is_sharpe=1.5,
            oos_sharpe=1.2,
        )
        assert sparse["is_overfitting"] is True, "省掉维度必须转'不通过'，不得转绿(R-055b)"
        assert sparse["parameter_stable"] is False and sparse["generalization_stable"] is False
        assert sparse["not_assessed_dimensions"] == ("parameter_sensitivity", "generalization")
        assert any("不可判定" in x for x in sparse["reasons"]), "缺位维须留名，禁与'判为过拟合'混淆"

    def test_same_inputs_with_dims_supplied_are_vetoed(self) -> None:
        det = OverfittingDetector()
        full = det.detect(
            walk_forward_results=[{"sharpe": 1.2, "max_drawdown": -0.05}] * 8,
            perturbed_results=[{"sharpe_ratio": 0.01}] * 6,
            period_results=[{"sharpe_ratio": 0.02}] * 5,
            is_sharpe=1.5,
            oos_sharpe=1.2,
        )
        assert full["is_overfitting"] is True
        assert full["not_assessed_dimensions"] == (), "供满三维 ⇒ 否决必须来自数据本身，不是缺位兜底"


class TestNTrialsProvenance:
    """判据④：N_eff 对账三态机械可判（全部落 tmp_path，禁写 data/ 生产路径）。"""

    @staticmethod
    def _write_batch(tmp_path: Path, series: dict[str, pd.Series]) -> Path:
        batch = tmp_path / "grid_unit_test"
        batch.mkdir(parents=True)
        frame = pd.DataFrame(series)
        frame.to_csv(batch / "net_returns.csv.gz", index=False, compression="gzip")
        return batch

    @staticmethod
    def _synthetic_series() -> dict[str, pd.Series]:
        rng = np.random.default_rng(7)
        common = pd.Series(rng.normal(0, 0.01, 300))
        out = {f"r{i}": common + pd.Series(rng.normal(0, 0.002, 300)) for i in range(8)}
        idx = pd.date_range("2020-01-01", periods=300, freq="B")
        return {k: pd.Series(v.values, index=idx) for k, v in out.items()}

    def test_missing_archive_is_unverifiable(self, tmp_path: Path) -> None:
        rep = mod.verify_n_trials_provenance("grid_not_exist", 9, 10080, intake_dir=tmp_path)
        assert rep["status"] == "unverifiable"

    def test_recorded_value_that_matches_recomputation_is_verified(self, tmp_path: Path) -> None:
        series = self._synthetic_series()
        batch = self._write_batch(tmp_path, series)
        assert (batch / "net_returns.csv.gz").exists()
        expected, _ = compute_effective_rank({k: pd.Series(v) for k, v in series.items()})
        rep = mod.verify_n_trials_provenance("grid_unit_test", expected, 8, intake_dir=tmp_path)
        assert rep["status"] == "verified"
        assert rep["recomputed_n_eff"] == expected

    def test_understated_denominator_is_caught(self, tmp_path: Path) -> None:
        """把登记分母改小（放水形态）⇒ 必须判 mismatch，不得判 verified。"""
        series = self._synthetic_series()
        batch = self._write_batch(tmp_path, series)
        assert (batch / "net_returns.csv.gz").exists()
        expected, _ = compute_effective_rank({k: pd.Series(v) for k, v in series.items()})
        rep = mod.verify_n_trials_provenance(
            "grid_unit_test", max(expected - 1, 1), 8, intake_dir=tmp_path
        )
        assert expected > 1
        assert rep["status"] == "mismatch"

    def test_missing_batch_id_is_unverifiable(self, tmp_path: Path) -> None:
        rep = mod.verify_n_trials_provenance("", 9, 10080, intake_dir=tmp_path)
        assert rep["status"] == "unverifiable"
