# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.backtest.test_factory_grid_stage_cost_tiers
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_executor; zephyr.backtest.regime_validation.exam_cost_gate
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 缺省路径逐位零漂移（summary/manifest 不出新键新列、扫描零调用）; T1 轻档两档只扫不判（三门判定恒全档证据）; 档位扫描失败=gate 层阴性 fail-closed; CPU 合成数据零真回测零真库
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_factory_grid_stage_cost_tiers.py — 方案①两轮制 stage-aware 成本档位（T3, 裁定#413 下一窗口升级案）。

四覆盖点（施工清单验收口径）:
  ① 默认零漂移——新代码缺省（cost_gate_tiers_bp=None / prereg 无分层字段）与旧行为逐位一致;
  ② T1 两档生效——t1 解析出 prereg 轻档 [0,5]，run_batch 逐点两档扫描落盘;
  ③ T2 全档不变——t2/t0 解析全档（exam_scale_cost_gate.yaml 真源），判定面仍 fail-closed 全档;
  ④ 预算闸新字段缺省兼容——cost_gate_t1_tiers_bp 缺省=现行语义逐字零变化；在场=fail-closed 校验。
CPU mock（stub 引擎注入），不跑真回测、不触 GPU、不写生产路径（产物落 tmp_path）。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from zephyr.backtest.regime_validation.exam_cost_gate import (
    CostGateConfig,
    run_cost_tier_scan,
    validate_scan_tiers,
)

_REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "factory_grid_executor", _REPO / "scripts" / "backtest" / "factory_grid_executor.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)

ENGINE = Path("scripts/backtest/translated/_c4_engine.py")
FULL_TIERS = [0, 5, 10, 20, 40]

# 缺省（未启用档位扫描）manifest 列序基准——零漂移硬验收的逐列对照
BASELINE_MANIFEST_COLS = [
    "recipe_id",
    "prefix_key",
    "degraded_dimensions",
    "sharpe",
    "ann_return",
    "max_drawdown",
    "avg_turnover",
    "net_days",
    "values_json",
]
BASELINE_SUMMARY_KEYS = {
    "run_ts",
    "mode",
    "subspace",
    "stratify_dims",
    "n_raw",
    "n_sampled",
    "evaluated",
    "eval_dead",
    "backtest_dead",
    "degraded_recipes",
    "window",
    "seed",
    "out_dir",
    "net_returns_file",
    "n_trials_effective",
    "n_eff_meta",
}


def _synth_closes(n_days: int = 160, n_sym: int = 36, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=n_days)
    base = rng.uniform(5, 50, n_sym)
    drift = rng.normal(0.0004, 0.0002, n_sym)
    noise = rng.normal(0, 0.015, (n_days, n_sym))
    px = base * np.exp(np.cumsum(drift + noise, axis=0))
    return pd.DataFrame(px, index=idx, columns=[f"{300000 + i}"[:6] for i in range(n_sym)])


def _synth_closes_rotating(n_days: int = 160, n_sym: int = 36, seed: int = 7) -> pd.DataFrame:
    """轮动面板: 逐票相位错开的正弦漂移——动量 top5 随周期换仓（换手>0）。

    静态持仓面板对滑点不敏感，档位探针会失去判据力（test_cost_gate_tier_wiring
    2026-09-23 首版同款教训），接线测试必须用本生成器。
    """
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=n_days)
    base = rng.uniform(5, 50, n_sym)
    t = np.arange(n_days)
    drift_mat = 0.003 * np.sin(t[:, None] / 12.0 + np.arange(n_sym)[None, :] * 1.3)
    noise = rng.normal(0, 0.02, (n_days, n_sym))
    px = base * np.exp(np.cumsum(drift_mat + noise, axis=0))
    return pd.DataFrame(px, index=idx, columns=[f"{300000 + i}"[:6] for i in range(n_sym)])


def _turnover_panel(n_days: int = 180, n_sym: int = 12):
    """带换手面板（档位扫描对滑点必须敏感，静态持仓探针无判据力）。"""
    rng = np.random.default_rng(11)
    idx = pd.bdate_range("2025-01-02", periods=n_days)
    cols = [f"S{i}" for i in range(n_sym)]
    block = np.arange(n_days) // 5
    hold = (block[:, None] + np.arange(n_sym)[None, :]) % 3 == 0
    w = pd.DataFrame(hold.astype(float), index=idx, columns=cols)
    w = w.div(w.sum(axis=1), axis=0)
    px = pd.DataFrame(
        100.0 * np.cumprod(1.0 + rng.normal(0.0008, 0.010, (n_days, n_sym)), axis=0),
        index=idx,
        columns=cols,
    )
    return w, px


def _engine():
    spec = importlib.util.spec_from_file_location("_c4_engine_stage_tiers", ENGINE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _caps(**over) -> dict:
    """现行 prereg budget_caps 等效合成册（字段值与 config/search_space_prereg.yaml 同构）。"""
    caps = {
        "wall_clock_hours": 59,
        "per_point_seconds_measured": 35.33,
        "grid_points_cap": 25000,
        "trial0_calibration_points": 200,
        "tier1_points": 3700,
        "tier2_points": 900,
        "cost_gate_in_every_tier": True,
    }
    caps.update(over)
    return caps


def _fake_repo(tmp_path: Path, monkeypatch, caps: dict | None = None, cost_tiers=FULL_TIERS, with_cost_yaml=True):
    """tmp 仓库骨架 + monkeypatch mod.__file__，使 _load_prereg_caps/_load_cost_gate_tiers 落在 tmp。"""
    scripts_dir = tmp_path / "scripts" / "backtest"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / "config").mkdir(exist_ok=True)
    fake_self = scripts_dir / "factory_grid_executor.py"
    fake_self.write_text("# stub", encoding="utf-8")
    if caps is not None:
        (tmp_path / "config" / "search_space_prereg.yaml").write_text(
            yaml.safe_dump({"budget_caps": caps}, allow_unicode=True), encoding="utf-8"
        )
    if with_cost_yaml:
        (tmp_path / "config" / "exam_scale_cost_gate.yaml").write_text(
            yaml.safe_dump({"cost_gate": {"tiers_bp": cost_tiers}}, allow_unicode=True), encoding="utf-8"
        )
    monkeypatch.setattr(mod, "__file__", str(fake_self))


class TestScanTierOverride:
    """exam_cost_gate.run_cost_tier_scan 档位子集覆盖（扫描面）+ validate_scan_tiers 校验。"""

    def test_two_tier_light_scan_delivered_as_kwargs(self):
        """T1 轻档两档逐项以关键字送达，gate_limits 不被档值污染（位置传参错位复发=红）。"""
        seen: list[tuple] = []

        def spy(weights, px_close, gate_limits=True, slippage_bp=None):
            seen.append((gate_limits, slippage_bp))
            return pd.Series(0.001, index=weights.index)

        w, px = _turnover_panel()
        out = run_cost_tier_scan(w, px, spy, CostGateConfig(), tiers_bp=[0, 5])
        assert list(out) == [0.0, 5.0]
        assert [s[1] for s in seen] == [0.0, 5.0]
        assert all(s[0] is True for s in seen)

    def test_default_none_uses_config_tiers_zero_drift(self):
        """tiers_bp 缺省 None=现行行为：档位集恒等 config 五档（签名演进零漂移）。"""
        seen: list[float] = []
        cfg = CostGateConfig()

        def spy(weights, px_close, gate_limits=True, slippage_bp=None):
            seen.append(slippage_bp)
            return pd.Series(0.001, index=weights.index)

        w, px = _turnover_panel()
        out = run_cost_tier_scan(w, px, spy, cfg)
        assert list(out) == list(cfg.tiers_bp) == sorted(set(seen))
        assert len(seen) == len(cfg.tiers_bp)

    def test_validate_scan_tiers_rejects_malformed(self):
        with pytest.raises(ValueError, match="空"):
            validate_scan_tiers([])
        with pytest.raises(ValueError, match="升序"):
            validate_scan_tiers([5, 0])
        with pytest.raises(ValueError, match="0bp"):
            validate_scan_tiers([5])
        with pytest.raises(ValueError, match="数值序列"):
            validate_scan_tiers(["a", "b"])
        assert validate_scan_tiers([0, 5]) == (0.0, 5.0)  # 两档轻档合法（判定面另管）

    def test_real_engine_two_tier_monotone(self):
        """真引擎两档扫描: 档间严格下降（0bp 对照档 >= 轻滑点档），缺档即哑门。"""
        eng = _engine()
        w, px = _turnover_panel()
        out = run_cost_tier_scan(w, px, eng.daily_net_returns, CostGateConfig(), tiers_bp=[0, 5])
        assert set(out) == {0.0, 5.0}
        assert out[0.0] > out[5.0], f"轻档非严格下降={out}——滑点未进入计算"


class TestResolveStageCostTiers:
    """stage → 档位集解析（②T1 两档生效 / ③T2 全档 / ①缺省 None 零漂移）。"""

    def test_field_absent_returns_none_for_all_stages(self):
        """分层字段缺省=现行语义：任何 stage 都不启用 per-point 扫描（零漂移契约）。"""
        for stage in ("", "t0", "t1", "t2"):
            assert mod._resolve_stage_cost_tiers(stage, _caps()) is None, f"stage={stage}"

    def test_t1_resolves_light_two_tiers(self, tmp_path, monkeypatch):
        _fake_repo(tmp_path, monkeypatch, caps=_caps(cost_gate_t1_tiers_bp=[0, 5]))
        assert mod._resolve_stage_cost_tiers("t1", _caps(cost_gate_t1_tiers_bp=[0, 5])) == (0.0, 5.0)

    def test_t2_t0_resolve_full_tiers_from_ssot(self, tmp_path, monkeypatch):
        """t2/t0 恒全档，且真源=config/exam_scale_cost_gate.yaml（禁双头硬编码）。"""
        caps = _caps(cost_gate_t1_tiers_bp=[0, 5])
        _fake_repo(tmp_path, monkeypatch, caps=caps, cost_tiers=[0, 5, 10, 20, 40])
        assert mod._resolve_stage_cost_tiers("t2", caps) == (0.0, 5.0, 10.0, 20.0, 40.0)
        assert mod._resolve_stage_cost_tiers("t0", caps) == (0.0, 5.0, 10.0, 20.0, 40.0)

    def test_plain_batch_no_scan_even_with_field(self, tmp_path, monkeypatch):
        """无 stage 名义（""）：字段在场也只校验不启用扫描（普通批次零漂移）。"""
        _fake_repo(tmp_path, monkeypatch, caps=_caps(cost_gate_t1_tiers_bp=[0, 5]))
        assert mod._resolve_stage_cost_tiers("", _caps(cost_gate_t1_tiers_bp=[0, 5])) is None

    def test_malformed_light_fails_closed(self, tmp_path, monkeypatch):
        caps = _caps(cost_gate_t1_tiers_bp=[5, 0])  # 降序
        _fake_repo(tmp_path, monkeypatch, caps=caps)
        with pytest.raises(SystemExit, match="分层档位非法"):
            mod._resolve_stage_cost_tiers("t1", caps)
        for bad in ([5], []):  # 缺 0bp 对照档 / 空集
            caps_bad = _caps(cost_gate_t1_tiers_bp=bad)
            with pytest.raises(SystemExit, match="分层档位非法"):
                mod._resolve_stage_cost_tiers("t1", caps_bad)

    def test_subset_violation_fails_closed(self, tmp_path, monkeypatch):
        """轻档 [0,3] 不在全档 [0,5,10,20,40] 内=档位口径漂移，禁开跑。"""
        caps = _caps(cost_gate_t1_tiers_bp=[0, 3])
        _fake_repo(tmp_path, monkeypatch, caps=caps)
        with pytest.raises(SystemExit, match="子集"):
            mod._resolve_stage_cost_tiers("t1", caps)

    def test_null_field_fails_closed(self, tmp_path, monkeypatch):
        """字段在场但 null=冻结册损坏（不得静默当缺省）。"""
        caps = _caps(cost_gate_t1_tiers_bp=None)
        _fake_repo(tmp_path, monkeypatch, caps=caps)
        with pytest.raises(SystemExit, match="未冻结值"):
            mod._resolve_stage_cost_tiers("t1", caps)

    def test_missing_full_tier_ssot_fails_closed(self, tmp_path, monkeypatch):
        """全档真源册缺失/空——分层语义无法闭环，禁开跑。"""
        caps = _caps(cost_gate_t1_tiers_bp=[0, 5])
        _fake_repo(tmp_path, monkeypatch, caps=caps, with_cost_yaml=False)
        with pytest.raises(SystemExit, match="全档真源缺失"):
            mod._resolve_stage_cost_tiers("t2", caps)
        _fake_repo(tmp_path, monkeypatch, caps=caps, cost_tiers=[])
        with pytest.raises(SystemExit, match="全档真源损坏"):
            mod._resolve_stage_cost_tiers("t2", caps)


class TestRedBlueRankAgreement:
    """红蓝对拍标定脚本纯函数面（scripts/backtest/calibrate_cost_tier_redblue.rank_agreement）。"""

    @staticmethod
    def _rb():
        spec = importlib.util.spec_from_file_location(
            "calibrate_cost_tier_redblue", _REPO / "scripts" / "backtest" / "calibrate_cost_tier_redblue.py"
        )
        m = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = m
        spec.loader.exec_module(m)
        return m

    def test_perfect_agreement_spearman_one_overlap_full(self):
        rb = self._rb()
        light = {f"r{i}": float(i) for i in range(10)}
        full = {f"r{i}": float(i) * 2 + 0.1 for i in range(10)}  # 正单调变换
        out = rb.rank_agreement(light, full, top_k=5)
        assert out["n"] == 10 and out["spearman"] == 1.0
        assert out["top_k"] == 5 and out["top_k_overlap"] == 5 and out["top_k_overlap_pct"] == 1.0

    def test_history_baseline_style_flip_detected(self):
        """排名反转被捕捉（Spearman=-1/top-K 重合=0）——对拍失配时报告不粉饰。"""
        rb = self._rb()
        light = {f"r{i}": float(i) for i in range(10)}
        full = {f"r{9 - i}": float(i) for i in range(10)}
        out = rb.rank_agreement(light, full, top_k=5)
        assert out["spearman"] == -1.0 and out["top_k_overlap"] == 0

    def test_degenerate_samples_honest_none(self):
        """样本<2: 统计位诚实置 None（禁编造 1.0 假绿）。"""
        rb = self._rb()
        out = rb.rank_agreement({"a": 1.0}, {"a": 2.0}, top_k=50)
        assert out == {"n": 1, "spearman": None, "top_k": 1, "top_k_overlap": None, "top_k_overlap_pct": None}

    def test_light_tiers_constant_matches_prereg_draft(self):
        """脚本轻档口径与方案①草案两档一致（防双头漂移）。"""
        rb = self._rb()
        assert rb.LIGHT_TIERS_BP == (0.0, 5.0)


class TestApplyPreregBudgetCompat:
    """④预算闸新字段缺省兼容 + 在场 fail-closed。"""

    def test_prereg_file_missing_fails_closed(self, tmp_path, monkeypatch):
        _fake_repo(tmp_path, monkeypatch, caps=None, with_cost_yaml=False)
        with pytest.raises(SystemExit, match="预注册冻结缺失"):
            mod._apply_prereg_budget("t1", 100)

    def test_legacy_semantics_field_absent_byte_compatible(self, tmp_path, monkeypatch):
        """字段缺省=现行语义逐字零变化：钳制/帽/fail-closed 行为全保持。"""
        _fake_repo(tmp_path, monkeypatch, caps=_caps())
        assert mod._apply_prereg_budget("t1", 5000) == 3700  # stage 帽钳制
        assert mod._apply_prereg_budget("", 30000) == 25000  # 总帽钳制
        assert mod._apply_prereg_budget("t1", 100) == 100  # 帽内不动
        caps_no_gate = _caps(cost_gate_in_every_tier=False)
        _fake_repo(tmp_path, monkeypatch, caps=caps_no_gate)
        with pytest.raises(SystemExit, match="未冻结为 true"):
            mod._apply_prereg_budget("t1", 100)
        caps_uncal = _caps(per_point_seconds_measured=None)
        _fake_repo(tmp_path, monkeypatch, caps=caps_uncal)
        with pytest.raises(SystemExit, match="T0 未标定回填"):
            mod._apply_prereg_budget("t1", 100)

    def test_staged_field_cannot_relax_master_switch(self, tmp_path, monkeypatch):
        """分层字段在场但 cost_gate_in_every_tier=false → 仍拒跑（分层不放松主开关）。"""
        caps = _caps(cost_gate_in_every_tier=False, cost_gate_t1_tiers_bp=[0, 5])
        _fake_repo(tmp_path, monkeypatch, caps=caps)
        with pytest.raises(SystemExit, match="未冻结为 true"):
            mod._apply_prereg_budget("t1", 100)

    def test_staged_field_malformed_rejected_at_budget_gate(self, tmp_path, monkeypatch):
        caps = _caps(cost_gate_t1_tiers_bp=[40, 0])
        _fake_repo(tmp_path, monkeypatch, caps=caps)
        with pytest.raises(SystemExit, match="分层档位非法"):
            mod._apply_prereg_budget("t1", 100)

    def test_staged_field_valid_keeps_caps_logic(self, tmp_path, monkeypatch):
        """字段合法在场：预算闸照常钳制，分层语义不影响点数帽。"""
        caps = _caps(cost_gate_t1_tiers_bp=[0, 5])
        _fake_repo(tmp_path, monkeypatch, caps=caps)
        assert mod._apply_prereg_budget("t1", 5000) == 3700
        assert mod._apply_prereg_budget("t2", 5000) == 900


class TestRunBatchStageCostWiring:
    """run_batch 档位扫描接线（stub 引擎注入；产物落 tmp_path）。"""

    N_DAYS = 160
    START_POS = 80

    @staticmethod
    def _stub_engine(closes: pd.DataFrame, slip_kwarg: bool = True):
        """slip_kwarg=False 时 daily_net 保持旧双参签名——档位 kwarg 调用即 TypeError（fail-closed 探针）。"""

        def load_px(start, end, fields=("close",)):
            long = closes.stack().rename("close").reset_index()
            long.columns = ["trade_date", "symbol", "close"]
            long["volume"] = 1e6
            return long

        def wide(px, field="close"):
            return px.pivot(index="trade_date", columns="symbol", values=field)

        def filter_st(w, flags):
            return w

        def load_st_flags(start, end):
            return pd.DataFrame()

        if slip_kwarg:

            def daily_net(weights, px, gate_limits=True, slippage_bp=None):
                r = px.reindex(weights.index.union(weights.index)).ffill().pct_change()
                w = weights.fillna(0.0)
                turnover = w.diff().abs().sum(axis=1).fillna(0.0) / 2.0
                slip = 0.0 if slippage_bp is None else float(slippage_bp)
                return (w.shift(1) * r).sum(axis=1).fillna(0.0) - turnover * slip * 2.0 / 10000.0

        else:

            def daily_net(weights, px):  # 旧签名: 档位扫描 kwarg 调用即 TypeError（探针）
                r = px.reindex(weights.index.union(weights.index)).ffill().pct_change()
                w = weights.fillna(0.0)
                return (w.shift(1) * r).sum(axis=1).fillna(0.0)

        def run_backtest(weights, px):
            net = daily_net(weights, px)
            return {
                "sharpe": float(net.mean() / net.std() * np.sqrt(244)),
                "ann_return": 0.1,
                "max_drawdown": -0.2,
                "avg_turnover_1side": 0.3,
            }

        # st-ddup-20260925 去重改造②①适配: run_backtest_full 单趟/net_returns_by_tiers
        # 一趟多档派生，桩与引擎新调用面同构；slip_kwarg=False 探针语义保持（旧签名
        # daily_net 收到 slippage_bp kwarg 即 TypeError）。
        # st-finaldel-csib-20260929 九元组同步（cf16fa43fd 改 _load_engine 9 元组漏同步本件）:
        # 补 prep_px_tensor 批级预热与单趟三产物 run_backtest_full_with_tiers
        # （与 test_factory_grid_executor.py 同款桩形）；run_backtest_full 以 **kwargs 吸收
        # pre_tensor 透传。探针阴性层随接线面同步: 档位序列改由三产物单趟派生（backtest
        # 层内），旧签名 TypeError 在该层暴露——阴性层 gate→backtest，fail-closed 不变。
        def run_backtest_full(weights, px, gate_limits=True, slippage_bp=None, **kwargs):
            net = daily_net(weights, px)
            stats = {
                "sharpe": float(net.mean() / net.std() * np.sqrt(244)),
                "ann_return": 0.1,
                "max_drawdown": -0.2,
                "avg_turnover_1side": 0.3,
            }
            return stats, net

        def net_returns_by_tiers(weights, px, tiers, gate_limits=True):
            return {float(b): daily_net(weights, px, slippage_bp=b) for b in tiers}

        def prep_px_tensor(weights_index, px_arg):
            cl = px_arg.reindex(weights_index.union(weights_index)).ffill()
            return cl, cl.pct_change()

        def run_backtest_full_with_tiers(weights, px_arg, tiers, **kwargs):
            stats_, net_ = run_backtest_full(weights, px_arg)
            return stats_, net_, net_returns_by_tiers(weights, px_arg, tiers)

        return (
            load_px,
            wide,
            filter_st,
            load_st_flags,
            run_backtest_full,
            daily_net,
            net_returns_by_tiers,
            prep_px_tensor,
            run_backtest_full_with_tiers,
        )

    def _run(
        self, tmp_path, monkeypatch, closes: pd.DataFrame, seed: int = 7, slip_kwarg: bool = True, **run_kwargs
    ) -> dict:
        monkeypatch.setattr(mod, "_load_engine", lambda: self._stub_engine(closes, slip_kwarg))
        monkeypatch.setattr(mod, "_load_universe", lambda u, start, end: set(closes.columns))
        monkeypatch.setattr(mod, "_load_mkt_cap_wide", lambda s, e, c: None)
        monkeypatch.setattr(mod, "_industry_map", lambda: None)
        monkeypatch.setattr(mod, "INTAKE_DIR", tmp_path)
        start = str(closes.index[self.START_POS].date())
        end = str(closes.index[-1].date())
        return mod.run_batch(8, seed, start, end, smoke=True, **run_kwargs)

    def _closes(self, seed: int = 7) -> pd.DataFrame:
        return _synth_closes(self.N_DAYS, 36, seed=seed)

    # —— ① 默认零漂移 ——

    def test_default_run_no_cost_artifacts_and_no_scan_call(self, tmp_path, monkeypatch):
        """缺省（不传档位）：summary 无新键、manifest 无新列、档位扫描零调用。"""
        import zephyr.backtest.regime_validation.exam_cost_gate as ecg

        calls: list = []
        orig = ecg.run_cost_tier_scan

        def _spy(*a, **k):
            calls.append((a, k))
            return orig(*a, **k)

        monkeypatch.setattr(ecg, "run_cost_tier_scan", _spy)
        summary = self._run(tmp_path, monkeypatch, self._closes())
        assert summary["evaluated"] >= 2
        assert "cost_gate_tiers_bp" not in summary
        assert "gate_dead" not in summary
        assert set(summary) == BASELINE_SUMMARY_KEYS, "缺省路径 summary 出新键=零漂移破缺"
        manifest = pd.read_csv(Path(summary["out_dir"]) / "manifest.csv")
        assert list(manifest.columns) == BASELINE_MANIFEST_COLS, "缺省路径 manifest 出新列=零漂移破缺"
        assert calls == [], "缺省路径仍触发了档位扫描"

    # —— ② T1 两档生效 ——

    def test_t1_two_tier_scan_wired_end_to_end(self, tmp_path, monkeypatch):
        closes = _synth_closes_rotating(seed=7)  # 轮动面板: 换手>0 → 滑点档可分辨
        summary = self._run(tmp_path, monkeypatch, closes, cost_gate_tiers_bp=(0.0, 5.0))
        assert summary["cost_gate_tiers_bp"] == [0.0, 5.0]
        assert summary["gate_dead"] == 0
        assert set(summary) - BASELINE_SUMMARY_KEYS == {"cost_gate_tiers_bp", "gate_dead"}
        manifest = pd.read_csv(Path(summary["out_dir"]) / "manifest.csv")
        assert set(manifest.columns) - set(BASELINE_MANIFEST_COLS) == {"cost_tier_sharpes_json", "cost_adjusted_sharpe"}
        ok = manifest.dropna(subset=["cost_tier_sharpes_json"])
        assert len(ok) == summary["evaluated"]
        strict = 0
        for _, row in ok.iterrows():
            sharpes = json.loads(row["cost_tier_sharpes_json"])
            assert sorted(sharpes) == ["0.0", "5.0"]
            assert sharpes["5.0"] <= sharpes["0.0"] + 1e-9, "滑点档 sharpe 反升=stub 未消费滑点"
            strict += int(sharpes["0.0"] > sharpes["5.0"])
            assert row["cost_adjusted_sharpe"] == sharpes["5.0"], "成本后主目标须取最高已扫档（T1=5bp）"
            # 0bp 对照档与 manifest 主口径 sharpe（冻结土规净）同源（stub None=零滑点）
            assert row["sharpe"] == pytest.approx(sharpes["0.0"], abs=1e-3)
        # 零换手格点对滑点天然不敏感（合法），但批内必须存在换手格点——否则探针失判据力
        assert strict >= 1, "全批格点换手为零=轮动面板失效，滑点分辨力丧失（test_cost_gate_tier_wiring 同款教训）"
        # 既有产物不受影响
        f = Path(summary["out_dir"]) / summary["net_returns_file"]
        assert f.exists()

    # —— ③ T2 全档不变 ——

    def test_t2_full_five_tier_scan(self, tmp_path, monkeypatch):
        closes = _synth_closes_rotating(seed=7)
        summary = self._run(tmp_path, monkeypatch, closes, cost_gate_tiers_bp=(0.0, 5.0, 10.0, 20.0, 40.0))
        assert summary["cost_gate_tiers_bp"] == [0.0, 5.0, 10.0, 20.0, 40.0]
        assert summary["gate_dead"] == 0
        manifest = pd.read_csv(Path(summary["out_dir"]) / "manifest.csv")
        ok = manifest.dropna(subset=["cost_tier_sharpes_json"])
        sharpes = json.loads(ok.iloc[0]["cost_tier_sharpes_json"])
        assert sorted(sharpes) == ["0.0", "10.0", "20.0", "40.0", "5.0"]
        assert ok.iloc[0]["cost_adjusted_sharpe"] == sharpes["40.0"], "全档成本后主目标=40bp 全成本档"

    def test_exam_judgment_still_requires_full_tier_evidence(self, tmp_path, monkeypatch):
        """判定面不放松：轻档两档证据过三门判定=fail-closed 不通过（T2 终审语义保持）。"""
        from zephyr.backtest.regime_validation.exam_cost_gate import evaluate_exam_cost_gate

        verdict = evaluate_exam_cost_gate({0.0: 1.0, 5.0: 0.9}, mean_daily_turnover_1side=0.01, days=244)
        assert not verdict.passed
        assert any("证据不足" in r for r in verdict.reasons)

    # —— fail-closed：扫描异常=gate 层阴性 ——

    def test_scan_failure_is_negative_not_silent_skip(self, tmp_path, monkeypatch):
        """扫描跑不出（旧签名桩收不到 slippage_bp kwarg）→ 阴性落 negatives，禁静默跳过。

        st-finaldel-csib-20260929 九元组语义同步（原名 test_scan_failure_is_gate_negative_
        not_silent_skip）: 档位序列随单趟三产物 run_backtest_full_with_tiers 派生
        （backtest 层内，st-gpup1 cf16fa43fd 接线），旧签名 daily_net 的 slippage_bp
        TypeError 在该层暴露——阴性层 gate→backtest；fail-closed 语义不变（阴性全落盘、
        批不崩、gate 层零静默）。
        """
        closes = _synth_closes_rotating(seed=11)
        summary = self._run(tmp_path, monkeypatch, closes, seed=11, slip_kwarg=False, cost_gate_tiers_bp=(0.0, 5.0))
        assert summary["backtest_dead"] >= 1
        assert summary["gate_dead"] == 0
        neg = pd.read_csv(Path(summary["out_dir"]) / "negatives.csv")
        bt_rows = neg[neg["death_layer"] == "backtest"]
        assert len(bt_rows) == summary["backtest_dead"]
        assert (bt_rows["death_reason"].str.startswith("backtest_fail:TypeError")).all()
        # 全员阴性批: manifest 空表但 schema 可解析（不崩批、阴性全落 negatives.csv）
        manifest = pd.read_csv(Path(summary["out_dir"]) / "manifest.csv")
        assert len(manifest) == summary["evaluated"] == 0

    def test_list_input_tiers_accepted_and_normalized(self, tmp_path, monkeypatch):
        """prereg 侧 YAML list 直传（[0,5]）与 tuple 等价——解析层已转 float 元组。"""
        closes = _synth_closes_rotating(seed=13)
        summary = self._run(tmp_path, monkeypatch, closes, seed=13, cost_gate_tiers_bp=[0, 5])
        assert summary["cost_gate_tiers_bp"] == [0.0, 5.0]
