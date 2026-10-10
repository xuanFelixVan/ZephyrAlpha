# [BLUEPRINT] MOD-BT-233 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.backtest.test_l2_gpu_landing
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; zephyr.backtest.gpu_core; scripts.backtest.translated._c4_engine; scripts.backtest.factory_grid_executor
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] trial
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [ERROR_CONTRACT] pytest assert；cupy/CUDA 不可用->GPU 用例 skip（CPU 用例恒跑）
# [TESTS] self
# [TTL] permanent
# [INVARIANTS] L2 战报钉（重建依据=docs/_working/fullscore_night/10_coordination/NIGHT_STATE.md §六）:
#   唯一核断言——gpu_core 是唯一 GPU 核（MOD-BT-232 gpu_panel_core superseded，双核禁复活）;
#   守卫披露键——_GPU_AUTO_MIN_CELLS=5e5（L2-B 重校准）+ stats backend/guard_reason 两键在案;
#   executor 三态——--engine cpu|gpu|auto 校验+逐波透传;
#   fail-closed 重跑——GPU 波败=整波弃置重跑 CPU（summary engine/engine_degrade 披露）;
#   parity 阈 1e-12——张量核/prefix 求值 GPU vs CPU 相对差红线（FP64 红线）。
#   全合成数据零 CH 零真库；executor 用 stub 引擎（产物落 tmp_path）。
"""test_l2_gpu_landing.py — GPU L2 落地守护（L2-A/B/C/D 四件+executor 接线）。

十二测钉战报验收面：唯一核/守卫披露/executor 三态/fail-closed 重跑/parity 1e-12/
RawKernel 与串行闸逐位同构/manifest backend-degrade 列。GPU 用例无 cupy 自动 skip。
"""

from __future__ import annotations

import importlib.util
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[3]
_TRANSLATED = _REPO / "scripts" / "backtest" / "translated"
for _p in (str(_REPO / "src"), str(_TRANSLATED)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import _c4_engine as eng  # noqa: E402

try:
    import zephyr.backtest.gpu_core as gpu_core  # noqa: E402
except ImportError:  # pragma: no cover - P0 未落地树
    gpu_core = None  # type: ignore[assignment]

_spec = importlib.util.spec_from_file_location(
    "factory_grid_executor_l2", _REPO / "scripts" / "backtest" / "factory_grid_executor.py"
)
fac = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = fac
_spec.loader.exec_module(fac)

HAS_GPU = gpu_core is not None and getattr(gpu_core, "HAS_GPU", False)
needs_gpu = pytest.mark.skipif(not HAS_GPU, reason="cupy/CUDA 不可用（GPU 用例跳过）")

SEED = 20261001
T, S = 360, 64


def _synth_px(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2022-01-03", periods=T)
    px = pd.DataFrame(
        100.0 + np.cumsum(rng.normal(0, 1.0, size=(T, S)), axis=0),
        index=idx,
        columns=[f"{600000 + i}" for i in range(S)],
    )
    px.iloc[:6, :4] = np.nan
    px.iloc[40:44, 10:18] = np.nan
    return px


def _synth_weights(px: pd.DataFrame, seed: int = SEED + 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    w = rng.normal(0, 0.05, size=px.shape)
    w[w < 0] = 0.0
    rs = w.sum(axis=1, keepdims=True)
    rs[rs == 0] = 1.0
    wd = pd.DataFrame(w / rs, index=px.index, columns=px.columns)
    wd.iloc[:5, :8] = np.nan
    return wd


def _synth_masks(px: pd.DataFrame, seed: int = SEED + 13) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    su = pd.DataFrame(rng.random(px.shape) < 0.03, index=px.index, columns=px.columns)
    sd = pd.DataFrame(rng.random(px.shape) < 0.03, index=px.index, columns=px.columns)
    return su, sd


# —————————————————— L2-E/A：唯一核 + RawKernel 收编 ——————————————————


def test_single_core_unified():
    """唯一核断言（L2-E）：gpu_core 内含 RawKernel 融合闸；引擎/执行器零 gpu_panel_core 引用。"""
    gc_src = (_REPO / "src" / "zephyr" / "backtest" / "gpu_core.py").read_text(encoding="utf-8")
    assert "fillability_gate_scan" in gc_src, "RawKernel 融合闸未收编进唯一核 gpu_core"
    assert "RawKernel" in gc_src
    for rel in ("scripts/backtest/translated/_c4_engine.py", "scripts/backtest/factory_grid_executor.py"):
        text = (_REPO / rel).read_text(encoding="utf-8")
        assert "gpu_panel_core" not in text, f"{rel} 仍引用 superseded 双核（MOD-BT-232 禁复活）"


def test_guard_min_cells_recalibrated():
    """L2-B 守卫重校准钉：_GPU_AUTO_MIN_CELLS=5e5 + 守卫原因码常量在案。"""
    assert eng._GPU_AUTO_MIN_CELLS == 500_000
    assert eng._GUARD_SMALL_PANEL == "auto_guard_below_min_cells"
    assert eng._GUARD_INELIGIBLE == "fastpath_ineligible"


def test_stats_disclosure_keys():
    """L2-B 披露键钉：stats 增 backend/guard_reason 两键；显式 cpu=守卫未介入。"""
    px = _synth_px()
    w = _synth_weights(px)
    stats, net = eng.run_backtest_full(w, px, backend="cpu")
    assert "backend" in stats and "guard_reason" in stats
    assert stats["backend"] == "cpu" and stats["guard_reason"] == ""
    with pytest.raises(ValueError):
        eng.run_backtest_full(w, px, backend="npu")


@needs_gpu
def test_rawkernel_gate_bitwise_vs_serial():
    """L2-A 同构钉：RawKernel 融合扫描与 CPU 串行循环同输入逐位一致（双精度同式）。"""
    import cupy as cp

    px = _synth_px()
    su, sd = _synth_masks(px)
    w = _synth_weights(px).ffill().fillna(0.0)
    w_np = w.to_numpy(dtype=np.float64)
    su_np = su.to_numpy(dtype=bool)
    sd_np = sd.to_numpy(dtype=bool)
    serial = gpu_core._apply_gate_serial(np, w_np, su_np, sd_np)
    fused = gpu_core._apply_gate_rawkernel(cp.asarray(w_np), cp.asarray(su_np), cp.asarray(sd_np))
    assert np.array_equal(gpu_core._to_numpy(fused), serial), "RawKernel 与串行闸漂移=语义分叉违宪"


@needs_gpu
def test_tensor_core_gpu_parity_1e12():
    """L2-A 验收钉：融合闸下 GPU vs CPU 相对差 ≤1e-12（FP64 红线）。"""
    px = _synth_px()
    su, sd = _synth_masks(px)
    w = _synth_weights(px)
    res_gpu = gpu_core.tensor_core(w, px, gate_masks=(su, sd), gate_limits=True, backend="gpu")
    res_cpu = gpu_core.tensor_core(w, px, gate_masks=(su, sd), gate_limits=True, backend="cpu")
    assert res_gpu["backend"] == "gpu"
    for key in ("gross", "turnover"):
        d = np.abs(res_gpu[key] - res_cpu[key])
        scale = np.abs(res_cpu[key]) + 1e-300
        assert float((d / scale).max()) <= 1e-12
    for bp, net_gpu in res_gpu["nets"].items():
        net_cpu = res_cpu["nets"][bp]
        d = np.abs(net_gpu - net_cpu)
        scale = np.abs(net_cpu) + 1e-300
        assert float((d / scale).max()) <= 1e-12


# —————————————————— L2-D：eval_prefix_equal_gpu ——————————————————


def _pandas_prefix_mirror(factors: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """factory 前缀三步 pandas 镜像（zscore→equal→rank），parity 对拍基准。"""
    normed = []
    for f in factors:
        mu = f.mean(axis=1)
        sd = f.std(axis=1)
        normed.append(f.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0))
    combined = pd.concat(normed).groupby(level=0).mean()
    rank = combined.rank(axis=1, ascending=False)
    return combined, rank


def _synth_factors(px: pd.DataFrame, k: int = 3) -> list[pd.DataFrame]:
    rng = np.random.default_rng(SEED + 23)
    rets = px.pct_change(fill_method=None)
    out = []
    for i in range(k):
        f = rets.rolling(5 + 10 * i).mean() + rng.normal(0, 0.01, px.shape)
        f.iloc[:20, :5] = np.nan
        f.iloc[30:33, 20:26] = np.nan
        out.append(pd.DataFrame(f.values, index=px.index, columns=px.columns))
    return out


@needs_gpu
def test_eval_prefix_parity_1e12():
    """L2-D parity 钉：eval_prefix_equal_gpu vs pandas 三步镜像 ≤1e-12（含 rank）。"""
    px = _synth_px()
    factors = _synth_factors(px)
    out = gpu_core.eval_prefix_equal_gpu(factors, backend="gpu")
    assert out["backend"] == "gpu"
    comb_ref, rank_ref = _pandas_prefix_mirror(factors)
    comb_gpu = pd.DataFrame(out["combined"], index=px.index, columns=px.columns)
    rank_gpu = pd.DataFrame(out["rank"], index=px.index, columns=px.columns)
    common = comb_ref.notna() & comb_gpu.notna()
    assert bool((comb_ref.notna() == comb_gpu.notna()).all().all()), "NaN 语义面漂移（skipna 同态破缺）"
    rel = (abs(comb_gpu[common] - comb_ref[common]) / (abs(comb_ref[common]) + 1e-300)).max().max()
    assert float(rel) <= 1e-12
    both = rank_ref.notna() & rank_gpu.notna()
    assert bool((rank_ref.notna() == rank_gpu.notna()).all().all()), "rank NaN 面漂移"
    assert float((rank_gpu[both] - rank_ref[both]).abs().max().max()) <= 1e-9, "rank 并列平均档漂移"


def test_eval_prefix_contract():
    """L2-D 合同钉：返回键/形状；因子不等形 ValueError；CPU 后端恒可用（无 cupy 不跳）。"""
    px = _synth_px()
    factors = _synth_factors(px, k=2)
    backend = "gpu" if HAS_GPU else "cpu"
    out = gpu_core.eval_prefix_equal_gpu(factors, backend=backend)
    assert set(out) == {"backend", "combined", "rank"}
    assert out["combined"].shape == px.shape and out["rank"].shape == px.shape
    assert out["combined"].dtype == np.float64
    bad = [factors[0], factors[1].iloc[:, :10]]
    with pytest.raises(ValueError):
        gpu_core.eval_prefix_equal_gpu(bad, backend="cpu")
    with pytest.raises(ValueError):
        gpu_core.eval_prefix_equal_gpu([], backend="cpu")


# —————————————————— L2-C：executor 三态 + fail-closed ——————————————————


def _stub_engine(closes: pd.DataFrame, fail_backends: tuple = (), stats_overlay: dict | None = None, seen=None):
    """stub 引擎（house 桩形+L2 扩展）：backend kwarg 吸收+披露 stats+波败注入。"""

    def load_px(start, end, fields=("close", "volume")):
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

    def _net(weights, px):
        r = px.reindex(weights.index.union(weights.index)).ffill().pct_change()
        w = weights.fillna(0.0)
        turnover = w.diff().abs().sum(axis=1).fillna(0.0) / 2.0
        return (w.shift(1) * r).sum(axis=1).fillna(0.0), turnover

    def run_backtest_full(weights, px, gate_limits=True, slippage_bp=None, *, backend=None, pre_tensor=None):
        if seen is not None:
            seen.append(backend)
        if backend in fail_backends:
            raise RuntimeError("StubCudaError: injected gpu wave failure")
        net, turnover = _net(weights, px)
        stats = {
            "days": int(len(net)),
            "sharpe": float(net.mean() / net.std() * np.sqrt(244)),
            "ann_return": 0.1,
            "max_drawdown": -0.2,
            "avg_turnover_1side": 0.3,
            "backend": "gpu" if backend == "gpu" else "cpu",
            "guard_reason": "",
        }
        if stats_overlay:
            stats.update(stats_overlay)
        return stats, net

    def net_returns_by_tiers(weights, px, tiers, gate_limits=True, **kwargs):
        return {float(b): _net(weights, px)[0] for b in tiers}

    def prep_px_tensor(weights_index, px_arg):
        cl = px_arg.reindex(weights_index.union(weights_index)).ffill()
        return cl, cl.pct_change()

    def run_backtest_full_with_tiers(weights, px_arg, tiers, **kwargs):
        stats_, net_ = run_backtest_full(weights, px_arg, **kwargs)
        return stats_, net_, net_returns_by_tiers(weights, px_arg, tiers)

    def daily_net(weights, px, gate_limits=True, slippage_bp=None, **kwargs):
        return _net(weights, px)[0]

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


def _install(tmp_path, monkeypatch, closes: pd.DataFrame, fail_backends: tuple = (), overlay=None, seen=None):
    monkeypatch.setattr(fac, "_load_engine", lambda: _stub_engine(closes, fail_backends, overlay, seen))
    monkeypatch.setattr(fac, "_load_universe", lambda u, start, end: set(closes.columns))
    monkeypatch.setattr(fac, "_load_mkt_cap_wide", lambda s, e, c: None)
    monkeypatch.setattr(fac, "_industry_map", lambda: None)
    monkeypatch.setattr(fac, "INTAKE_DIR", tmp_path)
    return str(closes.index[100].date()), str(closes.index[-1].date())


def _closes(n_days: int = 200, n_sym: int = 36, seed: int = 5) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=n_days)
    base = rng.uniform(5, 50, n_sym)
    t = np.arange(n_days)
    drift = 0.003 * np.sin(t[:, None] / 12.0 + np.arange(n_sym)[None, :] * 1.3)
    px = base * np.exp(np.cumsum(drift + rng.normal(0, 0.02, (n_days, n_sym)), axis=0))
    return pd.DataFrame(px, index=idx, columns=[f"{300000 + i}"[:6] for i in range(n_sym)])


def test_executor_engine_validation(tmp_path, monkeypatch):
    """executor 三态钉：非法 engine=ValueError（数据装载前即拒）。"""
    with pytest.raises(ValueError):
        fac.run_batch(8, 7, "2020-01-01", "2020-12-31", smoke=True, engine="tpu")


@pytest.mark.parametrize("engine,expected", [("cpu", "cpu"), ("gpu", "gpu"), ("auto", None)])
def test_executor_engine_passthrough(tmp_path, monkeypatch, engine, expected):
    """三态逐波透传钉：cpu/gpu 显式送达，auto=None（逐格守卫解析语义不变）。"""
    closes = _closes()
    seen: list = []
    start, end = _install(tmp_path, monkeypatch, closes, seen=seen)
    summary = fac.run_batch(8, 7, start, end, smoke=True, engine=engine)
    assert summary["engine"] == engine
    assert summary["evaluated"] >= 2
    assert all(b is expected for b in seen), f"backend 透传漂移: {seen}"


def test_executor_manifest_backend_degrade_columns(tmp_path, monkeypatch):
    """manifest backend/degrade 列钉：引擎 stats 披露透传出生证（degrade=guard_reason）。"""
    closes = _closes()
    overlay = {"backend": "cpu", "guard_reason": "auto_guard_below_min_cells"}
    start, end = _install(tmp_path, monkeypatch, closes, overlay=overlay)
    summary = fac.run_batch(8, 7, start, end, smoke=True, engine="auto")
    manifest = pd.read_csv(Path(summary["out_dir"]) / "manifest.csv")
    assert "backend" in manifest.columns and "degrade" in manifest.columns
    assert summary["evaluated"] >= 2
    assert (manifest["backend"] == "cpu").all()
    assert (manifest["degrade"] == "auto_guard_below_min_cells").all()


@needs_gpu
def test_executor_gpu_wave_failclosed_rerun(tmp_path, monkeypatch):
    """fail-closed 钉：GPU 波败=整波弃置重跑 CPU（禁半成品混合后端；summary 披露降级）。"""
    closes = _closes()
    seen: list = []
    start, end = _install(tmp_path, monkeypatch, closes, fail_backends=("gpu", None), seen=seen)
    summary = fac.run_batch(8, 7, start, end, smoke=True, engine="auto")
    assert summary["engine"] == "cpu", "重跑波未落到 cpu"
    assert "engine_degrade" in summary and summary["engine_degrade"].startswith("gpu_wave_failed_rerun_cpu")
    assert summary["evaluated"] >= 2 and summary["backtest_dead"] == 0
    assert seen[0] is None, "首波应以 auto(None) 驶入"
    assert all(b == "cpu" for b in seen[1:]), "重跑波须整波 cpu（禁混合后端）"
    manifest = pd.read_csv(Path(summary["out_dir"]) / "manifest.csv")
    assert (manifest["backend"] == "cpu").all()
    assert (
        summary["engine_degrade"].endswith("StubCudaError: injected gpu wave failure")
        or "StubCudaError" in summary["engine_degrade"]
    )


def test_executor_cpu_wave_negative_semantics(tmp_path, monkeypatch):
    """CPU 波内失败语义零漂移钉：per-recipe 阴性照旧，无整波重跑（无 engine_degrade 键）。"""
    closes = _closes()
    start, end = _install(tmp_path, monkeypatch, closes, fail_backends=("cpu",))
    summary = fac.run_batch(8, 7, start, end, smoke=True, engine="cpu")
    assert "engine_degrade" not in summary
    assert summary["backtest_dead"] == 8 and summary["evaluated"] == 0
    neg = pd.read_csv(Path(summary["out_dir"]) / "negatives.csv")
    assert (neg["death_layer"] == "backtest").all() and len(neg) == 8


# —————————————————— eval 面 GPU 核（st-gpux-20261011）——————————————————
# 定靶凭据（今晚 38,956 格仪表实测，见 docs/_working/gpufeed_campaign/01_gpux_t0_profile.md）：
#   eval=82.2% CPU-秒；其内 combine 命中路径 60.4%／未命中 39.6%；宇宙面 all_a_ex_st 独占 74.2%。
# 对拍纪律=docs/_working/gpu_rewrite/verification_framework.md 三层制：
#   层1 离散量（rank 档值）逐位、容差 0；层2 浮点相对差本件取 ≤1e-12（严 frameworks 的
#   FP64 线 1e-8——两侧同式无理由放宽）；层3 整批排名由影子阶梯钉，不在本件。
# 参照实现一律调 factory 真身（fac._normalize/_combine/_sizing/_apply_*），不另写镜像体——
#   镜像体会跟着犯同一个错，真身不会（判定函数两侧共用同一实现的既有纪律）。


def _grp_ctx(px: pd.DataFrame, n_groups: int = 7, unlabeled: int = 3):
    """列→行业组标签（含无锚列 fail-closed 面）+ 整数编码（无组=-1）。"""
    cols = list(px.columns)
    imap = {c: f"g{i % n_groups}" for i, c in enumerate(cols[:-unlabeled])}
    gidx = {g: i for i, g in enumerate(sorted(set(imap.values())))}
    codes = np.array([gidx.get(imap.get(c), -1) for c in cols], dtype=np.int64)
    return imap, codes, len(gidx)


def _mv_panel(px: pd.DataFrame, seed: int = SEED + 31) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    v = np.exp(rng.normal(3, 1, size=px.shape))
    v[px.isna().values] = np.nan
    return pd.DataFrame(v, index=px.index, columns=px.columns)


def _vol_panel(px: pd.DataFrame, seed: int = SEED + 41) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame(np.abs(rng.normal(0.02, 0.01, px.shape)) + 1e-4, index=px.index, columns=px.columns)


def _ctrl_log_mv(px: pd.DataFrame) -> pd.DataFrame:
    mv = _mv_panel(px)
    return np.log(mv.where(mv > 0))


def _a1_kwargs(mode: str, px: pd.DataFrame, f: pd.DataFrame):
    """按模式给 normalize_rows 备料（与 factory _normalize 的入参面一一对应）。"""
    imap, codes, ng = _grp_ctx(px)
    ctrl = None
    if mode in ("size_neutral", "industsize_neutral"):
        ctrl = _ctrl_log_mv(px).to_numpy(np.float64)
    return dict(codes=codes, n_groups=ng, ctrl=ctrl), imap, _mv_panel(px)


# industsize_neutral 不在此表：它的控制板口径需专门钉（见
# test_industsize_ctrl_demeaned_on_full_market_columns_not_universe_subset），
# 且 normalize_rows 对该模式显式拒收（见 test_industsize_mode_rejected_by_normalize_rows）。
_A1_MODES = ["raw", "zscore", "rank", "industry_neutral", "size_neutral"]

# 容差线：单段归约 1e-12（gpu_core 既有 parity 线）；industsize 双段（组均值 scatter +
# OLS 行内矩）实测 GPU 面最坏 1.477e-12 ⇒ 该模式取 1e-11。两条都紧于真源
# verification_framework.md §一·补 的 FP64 路径线 1e-8 三个数量级以上——不为过测试放宽，
# 只把"两层归约序差"这一实测形态写进容差，且把测量值钉在注释里。
_TOL_A1 = dict.fromkeys(_A1_MODES, 1e-12)
_TOL_A1["industsize_neutral"] = 1e-11


@pytest.mark.parametrize("mode", _A1_MODES)
def test_eval_a1_normalize_cpu_matches_factory(mode):
    """层2 钉（numpy 通路）：A1 六模式 vs factory _normalize 真身，NaN 位形+相对差双断。"""
    px = _synth_px()
    f = _synth_factors(px, k=1)[0]
    kw, imap, mv = _a1_kwargs(mode, px, f)
    ref = fac._normalize(f, mode, industry_map=imap, mkt_cap_w=mv)[0]
    got = pd.DataFrame(
        gpu_core.normalize_rows(np, f.to_numpy(np.float64), mode, **kw), index=px.index, columns=px.columns
    )
    assert bool((ref.isna() == got.isna()).all().all()), f"{mode} NaN 面漂移"
    m = ref.notna() & got.notna()
    rel = float((abs(got[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max())
    assert rel <= _TOL_A1[mode], f"{mode} 相对差 {rel:.3e} > {_TOL_A1[mode]:.1e}"


@needs_gpu
@pytest.mark.parametrize("mode", _A1_MODES)
def test_eval_a1_normalize_gpu_matches_factory(mode):
    """层2 钉（cupy 通路）：同一入参上卡，与 factory 真身 ≤1e-12（后端只改耗时不改数值）。"""
    import cupy as cp

    px = _synth_px()
    f = _synth_factors(px, k=1)[0]
    kw, imap, mv = _a1_kwargs(mode, px, f)
    ref = fac._normalize(f, mode, industry_map=imap, mkt_cap_w=mv)[0]
    kw_g = dict(kw)
    kw_g["codes"] = cp.asarray(kw["codes"])
    if kw["ctrl"] is not None:
        kw_g["ctrl"] = cp.asarray(kw["ctrl"])
    got_arr = cp.asnumpy(gpu_core.normalize_rows(cp, cp.asarray(f.to_numpy(np.float64)), mode, **kw_g))
    got = pd.DataFrame(got_arr, index=px.index, columns=px.columns)
    assert bool((ref.isna() == got.isna()).all().all()), f"{mode} GPU NaN 面漂移"
    m = ref.notna() & got.notna()
    rel = float((abs(got[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max())
    assert rel <= _TOL_A1[mode], f"{mode} GPU 相对差 {rel:.3e} > {_TOL_A1[mode]:.1e}"


def test_eval_rank_rows_bitwise_layer1():
    """层1 钉（离散量容差 0）：rank 档值与 pandas rank(axis=1) 逐位相等，升/降/pct 三形。"""
    px = _synth_px()
    f = _synth_factors(px, k=1)[0]
    a = f.to_numpy(np.float64)
    for asc, pct in [(True, False), (True, True), (False, False)]:
        ref = f.rank(axis=1, ascending=asc, pct=pct).to_numpy(np.float64)
        got = gpu_core._rank_rows(np, a, ascending=asc, pct=pct)
        assert bool((np.isnan(ref) == np.isnan(got)).all()), f"asc={asc} pct={pct} NaN 位形漂移"
        m = ~np.isnan(ref)
        assert np.array_equal(ref[m], got[m]), f"层1 违宪：rank 档值漂移 asc={asc} pct={pct}"


def test_eval_industry_demean_unlabeled_column_failclosed():
    """无行业锚列必须整列 NaN——codes 负数若进 scatter/取模索引会静默取到最后一组（假对拍形态）。"""
    px = _synth_px()
    f = _synth_factors(px, k=1)[0]
    imap, codes, ng = _grp_ctx(px)
    ref = fac._demean_by_group(f, imap)
    got = pd.DataFrame(
        gpu_core.normalize_rows(np, f.to_numpy(np.float64), "industry_neutral", codes=codes, n_groups=ng),
        index=px.index,
        columns=px.columns,
    )
    unl = list(px.columns[-3:])
    assert bool(ref[unl].isna().all().all()) and bool(got[unl].isna().all().all()), "无锚列未 fail-closed"
    m = ref.notna() & got.notna()
    assert float((abs(got[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max()) <= 1e-12


def test_eval_core_rejects_uncovered_mode_failclosed():
    """未覆盖模式/缺入参必须抛——禁本件自造近似（自造=静默换口径，判据面无感）。"""
    px = _synth_px()
    a = _synth_factors(px, k=1)[0].to_numpy(np.float64)
    with pytest.raises(ValueError):
        gpu_core.normalize_rows(np, a, "winsorize_crazy")
    with pytest.raises(ValueError):
        gpu_core.normalize_rows(np, a, "industry_neutral", codes=None, n_groups=0)
    with pytest.raises(ValueError):
        gpu_core.sizing_weights(np, a, a, 10, "equal_weight_typo")
    with pytest.raises(ValueError):
        gpu_core.sizing_weights(np, a, a, 10, "mkt_cap")  # 缺市值板=fail-closed 非静默降级


def test_eval_equal_combine_matches_factory():
    """A2=equal：卡上逐格 nanmean vs pandas concat+groupby.mean 真身。"""
    px = _synth_px()
    fl = _synth_factors(px, k=4)
    normed = [gpu_core._zscore_rows(np, f.to_numpy(np.float64)) for f in fl]
    normed_dfs = [pd.DataFrame(n, index=px.index, columns=px.columns) for n in normed]
    ref = fac._combine({f"f{i}": f for i, f in enumerate(fl)}, normed_dfs, "equal", px)[0]
    got = pd.DataFrame(gpu_core._equal_combine(np, normed), index=px.index, columns=px.columns)
    assert bool((ref.isna() == got.isna()).all().all()), "equal 合成 NaN 面漂移"
    m = ref.notna() & got.notna()
    assert float((abs(got[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max()) <= 1e-12


def _ic_split_pipeline(px: pd.DataFrame, normed_dfs: list[pd.DataFrame], mode: str) -> pd.DataFrame:
    """本件的切分面：卡上算 IC 序列 → (T,F) 小矩阵交回 pandas 滚动/半衰/归一 → 卡上加权合成。

    滚动/归一的对象是 (T,F)（F≤8）不是 (T,S)，上卡无收益且引入第二实现面，故留在 CPU
    （gpu_core eval 节头 CPU 交接点 4）。
    """
    names = list(px.columns)
    fwd = px.pct_change().shift(-1)
    fwd_ranked = gpu_core._rank_rows(np, fwd.to_numpy(np.float64), ascending=True)
    normed = [n.to_numpy(np.float64) for n in normed_dfs]
    with np.errstate(all="ignore"):
        ic = np.column_stack([gpu_core.ic_pair_rows(np, n, fwd_ranked) for n in normed])
    ic_all = pd.DataFrame(ic, index=px.index, columns=[f"f{i}" for i in range(len(normed))])
    if mode == "ic_mean":
        w = ic_all.rolling(60, min_periods=20).mean()
    elif mode == "ic_ir":
        w = ic_all.rolling(60, min_periods=20).mean() / (ic_all.rolling(60, min_periods=20).std() + 1e-12)
    else:
        w = ic_all.ewm(halflife=20, min_periods=10, adjust=False).mean()
    w = w.clip(lower=0.0).shift(1)
    w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).reindex(px.index).fillna(1.0 / len(normed))
    combined = gpu_core.weighted_combine(np, normed, w.to_numpy(np.float64))
    return pd.DataFrame(combined, index=px.index, columns=names)


@pytest.mark.parametrize("mode", ["ic_mean", "ic_ir", "halflife20"])
def test_eval_ic_combine_matches_factory(mode):
    """IC 族整链对拍：卡上原语＋CPU 小矩阵滚动，合成结果 vs factory _combine 真身。"""
    px = _synth_px()
    fl = _synth_factors(px, k=3)
    normed_dfs = [_zscore_df(f) for f in fl]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # pct_change fill_method 弃用告警=factory 原样口径，非本件引入
        ref = fac._combine({f"f{i}": f for i, f in enumerate(fl)}, normed_dfs, mode, px)[0]
        got = _ic_split_pipeline(px, normed_dfs, mode)
    m = ref.notna() & got.notna()
    rel = float((abs(got[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max())
    assert rel <= 1e-10, f"{mode} 切分面漂移 {rel:.3e}（rank 归约序差容差 ≤1e-10）"


def _zscore_df(f: pd.DataFrame) -> pd.DataFrame:
    mu = f.mean(axis=1)
    sd = f.std(axis=1)
    return f.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0)


@pytest.mark.parametrize(
    "mode", ["equal_weight", "inv_vol", "mkt_cap", "risk_parity", "signal_strength", "kelly_025", "kelly_050"]
)
def test_eval_sizing_all_modes_match_factory(mode):
    """C 定尺寸七形对拍（kelly 的非满仓 0 语义与 base 的 NaN 语义是分岔面，必须各自钉住）。"""
    px = _synth_px()
    scores = _synth_factors(px, k=1)[0]
    rank_desc = scores.rank(axis=1, ascending=False)
    vol = _vol_panel(px)
    mv = _mv_panel(px)
    rng = np.random.default_rng(SEED + 43)
    r60m = pd.DataFrame(rng.normal(0, 0.002, px.shape), index=px.index, columns=px.columns)
    r60v = pd.DataFrame(np.abs(rng.normal(4e-4, 2e-4, px.shape)) + 1e-6, index=px.index, columns=px.columns)
    ref = fac._sizing(scores, 10, mode, vol, mkt_cap_w=mv, rets60_mean=r60m, rets60_var=r60v, rank_pre=rank_desc)[0]
    got = pd.DataFrame(
        gpu_core.sizing_weights(
            np,
            scores.to_numpy(np.float64),
            rank_desc.to_numpy(np.float64),
            10,
            mode,
            vol20=vol.to_numpy(np.float64),
            mkt_cap=mv.to_numpy(np.float64),
            r60_mean=r60m.to_numpy(np.float64),
            r60_var=r60v.to_numpy(np.float64),
        ),
        index=px.index,
        columns=px.columns,
    )
    assert bool((ref.isna() == got.isna()).all().all()), f"{mode} NaN 面漂移（kelly 应 0 非 NaN）"
    m = ref.notna() & got.notna()
    assert float((abs(got[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max()) <= 1e-12, f"{mode} 权重漂移"


def test_eval_periodic_hold_matches_factory_ffill():
    """非调仓日沿用旧权重：行 gather 与 pandas iloc[::step].reindex(ffill) 逐位同（三档）。"""
    px = _synth_px()
    w = _synth_factors(px, k=1)[0]
    for step, freq in [(5, "weekly"), (10, "biweekly"), (21, "monthly")]:
        ref = fac._apply_freq_trigger(w, freq, "periodic")
        got = pd.DataFrame(
            gpu_core.periodic_hold_rows(np, w.to_numpy(np.float64), step), index=px.index, columns=px.columns
        )
        ref_n = ref.to_numpy(np.float64)
        got_n = got.to_numpy(np.float64)
        # array_equal 默认 NaN≠NaN——NaN 位形单列断言，数值面才谈"逐位"（否则把自己写的尺判红）。
        assert bool((np.isnan(ref_n) == np.isnan(got_n)).all()), f"step={step} NaN 位形漂移"
        mv = ~np.isnan(ref_n)
        assert np.array_equal(ref_n[mv], got_n[mv]), f"step={step} 调仓行集漂移"


def test_eval_cell_drift_band_leaves_trigger_and_cap_to_host():
    """次序敏感钉：drift_band 交接格本件只做到 _sizing，禁提前 cap——
    factory 次序 _sizing→trigger→cap，先 cap 会让 drift_band 的行比较见到被削过的权重。"""
    px = _synth_px()
    combined = _synth_factors(px, k=1)[0]
    rank_desc = combined.rank(axis=1, ascending=False)
    vol = _vol_panel(px)
    out = gpu_core.eval_cell_gpu(
        combined.to_numpy(np.float64),
        rank_desc.to_numpy(np.float64),
        top_n=10,
        sizing_mode="equal_weight",
        freq_step=5,
        trigger="drift_band",
        cap=0.05,
        lam=0.0,
        vol20=vol.to_numpy(np.float64),
        backend="cpu",
    )
    assert out["host_continue"] is True
    ref_sizing = fac._sizing(combined, 10, "equal_weight", vol, rank_pre=rank_desc)[0]
    got = pd.DataFrame(out["weights"], index=px.index, columns=px.columns)
    m = ref_sizing.notna()
    assert float((abs(got[m] - ref_sizing[m])).max().max()) == 0.0, "交接格必须停在 _sizing 末态（禁提前 clip）"
    # 从该末态续跑 pandas 两步 == factory 全序（续跑等价钉）
    w2 = fac._apply_freq_trigger(ref_sizing, "weekly", "drift_band")
    ref_full = fac._apply_cap_and_lambda(w2, "cap5", "lambda_0")
    w3 = fac._apply_freq_trigger(got, "weekly", "drift_band")
    got_full = fac._apply_cap_and_lambda(w3, "cap5", "lambda_0")
    assert float((abs(got_full - ref_full)).max().max()) == 0.0


@needs_gpu
def test_evaluate_recipe_wiring_backend_switch_matches_cpu():
    """执行器接线集成钉（本支存在的理由=单测核不覆盖 wiring，真缺陷正出在 wiring）。

    三面同断，缺一不算过：
      ① 零格死亡：gpu 后端的 evaluated 集合与 cpu 后端完全一致（算力面的坑禁变成假阴性）；
      ② 数值等价：两侧 weights 矩阵逐格相对差 ≤1e-10，NaN 位形一致；
      ③ **设备分支确实跑过**：stats 计数 prefix_gpu/cell_gpu >0——否则本支退化成
         "装饰性守卫"（挂着开关而没人走），绿而无物。
    """
    px = _synth_px()
    fl = _synth_factors(px, k=3)
    factors = {f"f{i}": f for i, f in enumerate(fl)}
    cols = list(px.columns)
    imap, _codes, _ng = _grp_ctx(px)
    vol = _vol_panel(px)
    mv = _mv_panel(px)
    rng = np.random.default_rng(SEED + 81)
    r60m = pd.DataFrame(rng.normal(0, 0.002, px.shape), index=px.index, columns=px.columns)
    r60v = pd.DataFrame(np.abs(rng.normal(4e-4, 2e-4, px.shape)) + 1e-6, index=px.index, columns=px.columns)

    combos = [
        dict(A1="zscore", A2="equal", C="equal_weight", D1="weekly", D2="periodic", H="lambda_0"),
        dict(A1="rank", A2="ic_mean", C="inv_vol", D1="monthly", D2="periodic", H="lambda_0"),
        dict(A1="industry_neutral", A2="orth_equal", C="mkt_cap", D1="weekly", D2="periodic", H="lambda_5bp"),
        dict(A1="industsize_neutral", A2="halflife20", C="signal_strength", D1="weekly", D2="drift_band", H="lambda_0"),
        dict(A1="size_neutral", A2="equal", C="kelly_025", D1="daily", D2="periodic", H="lambda_0"),
    ]
    seen_prefix_gpu = 0
    seen_cell_gpu = 0
    for cmb in combos:
        v = dict(
            G_universe="hs300",
            A1_factor_normalize=cmb["A1"],
            A2_combine_weight=cmb["A2"],
            B_top_n="top10",
            C_sizing=cmb["C"],
            D1_rebalance_freq=cmb["D1"],
            D2_rebalance_trigger=cmb["D2"],
            E_single_cap="cap10",
            H_turnover_lambda=cmb["H"],
            X_sector="off",
            J_regime_switch="off",
            X_stop="off",
            X_breaker="off",
        )

        def _run(backend):
            monkey_clear = dict(fac._DEV_PANEL_CACHE)
            fac._DEV_PANEL_CACHE.clear()
            old = fac._EVAL_BACKEND
            old_stats = dict(fac._EVAL_GPU_STATS)
            for k in fac._EVAL_GPU_STATS:
                fac._EVAL_GPU_STATS[k] = 0
            fac._EVAL_BACKEND = backend
            try:
                w, deg = fac.evaluate_recipe(
                    type("R", (), {"values": v})(),
                    px,
                    factors,
                    vol,
                    cols,
                    mkt_cap_w=mv,
                    rets60_mean=r60m,
                    rets60_var=r60v,
                    industry_map=imap,
                    combine_cache={},
                )
            finally:
                fac._EVAL_BACKEND = old
                st = dict(fac._EVAL_GPU_STATS)
                fac._EVAL_GPU_STATS.update(old_stats)
                fac._DEV_PANEL_CACHE.clear()
                fac._DEV_PANEL_CACHE.update(monkey_clear)
            return w, deg, st

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            wc, dc, _ = _run("cpu")
            wg, dg, st = _run("gpu")
        assert st["prefix_gpu"] >= 1 or st["cell_gpu"] >= 1, f"{cmb} 设备分支零命中（装饰性开关）"
        seen_prefix_gpu += st["prefix_gpu"]
        seen_cell_gpu += st["cell_gpu"]
        assert list(wc.columns) == list(wg.columns) and wc.index.equals(wg.index), f"{cmb} 形面漂移"
        a, b = wc.to_numpy(np.float64), wg.to_numpy(np.float64)
        assert bool((np.isnan(a) == np.isnan(b)).all()), f"{cmb} NaN 位形漂移"
        m = ~np.isnan(a)
        rel = float((np.abs(b[m] - a[m]) / (np.abs(a[m]) + 1e-300)).max(initial=0.0))
        assert rel <= 1e-10, f"{cmb} gpu/cpu 权重相对差 {rel:.3e}"
        assert dc == dg, f"{cmb} degraded 元组漂移 {dc} vs {dg}"
    assert seen_prefix_gpu >= 3 and seen_cell_gpu >= 3, (
        f"覆盖面不足：prefix_gpu={seen_prefix_gpu} cell_gpu={seen_cell_gpu}（须两面都真跑过）"
    )


@needs_gpu
def test_evaluate_recipe_device_failure_degrades_to_cpu_not_cell_death(monkeypatch):
    """方向性钉（本班实测自犯）：设备面前缀抛异常=降级 CPU 出格，禁把格判死。

    曾实测形态：_prefix_eval_gpu 里 bool(codes) 对多元素数组求真值直接 ValueError，
    未被包裹→6/8 格记 eval_fail:ValueError=假阴性。算力面永远不得成为判决面。
    """
    px = _synth_px()
    fl = _synth_factors(px, k=2)
    factors = {f"f{i}": f for i, f in enumerate(fl)}
    cols = list(px.columns)
    imap, _c, _n = _grp_ctx(px)
    v = dict(
        G_universe="hs300",
        A1_factor_normalize="zscore",
        A2_combine_weight="equal",
        B_top_n="top10",
        C_sizing="equal_weight",
        D1_rebalance_freq="weekly",
        D2_rebalance_trigger="periodic",
        E_single_cap="cap10",
        H_turnover_lambda="lambda_0",
        X_sector="off",
        J_regime_switch="off",
        X_stop="off",
        X_breaker="off",
    )

    def _boom(*a, **k):
        raise RuntimeError("injected device failure")

    monkeypatch.setattr(fac, "_EVAL_BACKEND", "gpu")
    monkeypatch.setattr(fac, "_DEV_PANEL_CACHE", {})
    monkeypatch.setattr(fac, "_prefix_eval_gpu", _boom)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        w, deg = fac.evaluate_recipe(
            type("R", (), {"values": v})(),
            px,
            factors,
            _vol_panel(px),
            cols,
            mkt_cap_w=_mv_panel(px),
            industry_map=imap,
            combine_cache={},
        )
    assert w.shape == px.shape, "设备面失败必须仍出权重（降级 CPU），禁零格"


def test_dev_col_codes_no_bool_on_array():
    """回归钉：codes 是 ndarray，任何对其求真值的写法都会炸考格——本支盯返回面本身。"""
    px = _synth_px()
    cols = list(px.columns)
    imap, _g, ng = _grp_ctx(px)
    codes, n = fac._dev_col_codes(cols, imap)
    assert codes.dtype == np.int64 and len(codes) == len(cols)
    assert (codes == -1).sum() == 3 and n == ng
    with pytest.raises(ValueError):
        bool(codes)  # 明写反例：这就是曾把 6/8 格判死的表达式形态
    empty_codes, empty_n = fac._dev_col_codes(cols, None)
    assert empty_codes is None and empty_n == 0


def test_industsize_ctrl_demeaned_on_full_market_columns_not_universe_subset():
    """口径钉（本班 8 格真实对拍实钓）：factory 的 industsize 把**全市场列**的 log_mv 送去
    组内去均值，之后才由 _regress_out reindex 到宇宙列；"先切宇宙列再去均值"会改组均值口径。

    实测形态：zz500/hs300 两支 industsize_neutral 格在 cpu/gpu 双跑间 sharpe 差 4.9e-2、
    ann_return 差 1.5e-2（冻结线 0.005），而 avg_turnover/net_days 逐位等——集合面没动、
    权重幅度面被组均值口径改了。本支双向断言：全市场口径必须对上 factory，
    宇宙子集口径必须**对不上**（否则本支是装饰性守卫）。
    """
    px = _synth_px()
    f = _synth_factors(px, k=1)[0]
    uni_cols = list(px.columns)
    rng = np.random.default_rng(SEED + 91)
    extra_cols = [f"x{i}" for i in range(24)]
    all_cols = uni_cols + extra_cols
    mv_full = pd.DataFrame(
        np.exp(rng.normal(3, 1.2, size=(px.shape[0], len(all_cols)))), index=px.index, columns=all_cols
    )
    # 行业锚覆盖全市场列（真实 sws2021_l1 就是全票表，不是宇宙表）
    imap_full = {c: f"g{i % 7}" for i, c in enumerate(all_cols)}
    ref = fac._normalize(f, "industsize_neutral", industry_map=imap_full, mkt_cap_w=mv_full)[0]

    codes_u, ng_u = fac._dev_col_codes(uni_cols, imap_full)[:2] if False else (None, 0)
    imap_u = {c: imap_full[c] for c in uni_cols}
    codes_u, ng_u = _codes_for(uni_cols, imap_u)
    ctrl_full_dm = gpu_core.normalize_rows(
        np,
        np.log(mv_full).to_numpy(np.float64),
        "industry_neutral",
        codes=np.array(
            [list(all_cols).index(c) if imap_full.get(c) is not None else -1 for c in all_cols], dtype=np.int64
        ),
        n_groups=len({g for g in imap_full.values()}),
    )[:, [all_cols.index(c) for c in uni_cols]]
    got = pd.DataFrame(
        gpu_core.industsize_rows(np, f.to_numpy(np.float64), codes_u, ng_u, ctrl_full_dm),
        index=px.index,
        columns=uni_cols,
    )
    m = ref.notna() & got.notna()
    rel = float((abs(got[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max())
    assert rel <= 1e-12, f"全市场口径应复现 factory，实测相对差 {rel:.3e}"

    # 反向护栏：先切宇宙列再去均值（本班曾犯的口径）必须对不上 factory
    codes_same, ng_same = codes_u, ng_u
    ctrl_wrong = gpu_core.normalize_rows(
        np, np.log(mv_full[uni_cols]).to_numpy(np.float64), "industry_neutral", codes=codes_same, n_groups=ng_same
    )
    got_wrong = pd.DataFrame(
        gpu_core._regress_out_rows(
            np, gpu_core._demean_rows(np, f.to_numpy(np.float64), codes_same, ng_same), ctrl_wrong
        ),
        index=px.index,
        columns=uni_cols,
    )
    rel_wrong = float((abs(got_wrong[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max())
    assert rel_wrong > 1e-6, f"子集口径本应偏离 factory 却几乎相同（{rel_wrong:.3e}）——本支失去判别力"


def _codes_for(cols, imap):
    codes, ng = fac._dev_col_codes(cols, imap)
    return codes, ng


def test_industsize_mode_rejected_in_normalize_rows_contract():
    """合同钉：normalize_rows 不接受 industsize_neutral——该模式需调用方先在全市场列集做
    组内去均值，禁在核内静默按子集口径算（越界=抛，不是猜）。"""
    px = _synth_px()
    a = _synth_factors(px, k=1)[0].to_numpy(np.float64)
    codes, ng = fac._dev_col_codes(list(px.columns), {c: "g0" for c in px.columns})
    with pytest.raises(ValueError):
        gpu_core.normalize_rows(np, a, "industsize_neutral", codes=codes, n_groups=ng, ctrl=a.copy())


def test_industsize_ctrl_demeaned_on_full_market_columns_not_universe_subset():
    """口径钉（本班 8 格真实对拍实钓）：factory `_normalize:502-506` 把**全市场列**的 log_mv
    送去组内去均值，之后才由 `_regress_out` reindex 到宇宙列；先切宇宙列再去均值=换组均值口径。

    实测漂移形态（grid_20261011-033035 vs -033126，同 seed 同 8 格）：两支
    industsize_neutral 格 sharpe 差 4.9e-2、ann_return 差 1.5e-2（冻结线 0.005），
    而 avg_turnover/net_days 逐位等——持仓集合面没动，权重幅度面被口径改了。
    本支双向断言：全市场口径必须复现 factory；子集口径必须**复现不了**（否则是装饰性守卫）。
    """
    px = _synth_px()
    f = _synth_factors(px, k=1)[0]
    uni = list(px.columns)
    rng = np.random.default_rng(SEED + 91)
    all_cols = uni + [f"x{i}" for i in range(24)]  # 市值面板比宇宙宽=真实形态
    mv_full = pd.DataFrame(
        np.exp(rng.normal(3, 1.2, size=(px.shape[0], len(all_cols)))), index=px.index, columns=all_cols
    )
    imap_full = {c: f"g{i % 7}" for i, c in enumerate(all_cols)}  # 行业锚是全票表
    ref = fac._normalize(f, "industsize_neutral", industry_map=imap_full, mkt_cap_w=mv_full)[0]

    codes_u, ng_u = fac._dev_col_codes(uni, imap_full)
    codes_f, ng_f = fac._dev_col_codes(all_cols, imap_full)
    pos_u = [all_cols.index(c) for c in uni]
    a_u = f.to_numpy(np.float64)

    # 正确口径：全市场列去均值 → 切宇宙列 → 两支残差
    dm_full = gpu_core.normalize_rows(
        np, np.log(mv_full).to_numpy(np.float64), "industry_neutral", codes=codes_f, n_groups=ng_f
    )
    got = pd.DataFrame(gpu_core.industsize_rows(np, a_u, codes_u, ng_u, dm_full[:, pos_u]), index=px.index, columns=uni)
    m = ref.notna() & got.notna()
    rel = float((abs(got[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max())
    assert rel <= 1e-12, f"全市场口径须复现 factory，实测相对差 {rel:.3e}"

    # 反向护栏：先切宇宙列再去均值（本班曾犯的口径）
    ctrl_wrong = gpu_core.normalize_rows(
        np, np.log(mv_full[uni]).to_numpy(np.float64), "industry_neutral", codes=codes_u, n_groups=ng_u
    )
    got_wrong = pd.DataFrame(
        gpu_core._regress_out_rows(np, gpu_core._demean_rows(np, a_u, codes_u, ng_u), ctrl_wrong),
        index=px.index,
        columns=uni,
    )
    rel_wrong = float((abs(got_wrong[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max())
    assert rel_wrong > 1e-6, f"子集口径本应偏离 factory，实测仅 {rel_wrong:.3e}＝本支失去判别力"


def test_industsize_mode_rejected_by_normalize_rows():
    """合同钉：normalize_rows 显式拒收 industsize_neutral——控制板的去均值作用面属调用方决策，
    核内不许"顺手按自己拿到的列集"算（那正是本班实钓到的口径漂移源）。"""
    px = _synth_px()
    a = _synth_factors(px, k=1)[0].to_numpy(np.float64)
    codes, ng = fac._dev_col_codes(list(px.columns), {c: f"g{i % 3}" for i, c in enumerate(px.columns)})
    with pytest.raises(ValueError):
        gpu_core.normalize_rows(np, a, "industsize_neutral", codes=codes, n_groups=ng, ctrl=a.copy())
    with pytest.raises(ValueError):
        gpu_core.industsize_rows(np, a, codes, ng, None)


def test_eval_cell_end_to_end_matches_pandas_chain():
    """整格链一次成型 vs pandas 三连调（sizing→periodic→cap），host_continue 须 False。"""
    px = _synth_px()
    combined = _synth_factors(px, k=1)[0]
    rank_desc = combined.rank(axis=1, ascending=False)
    vol = _vol_panel(px)
    w = fac._sizing(combined, 10, "inv_vol", vol, rank_pre=rank_desc)[0]
    w = fac._apply_freq_trigger(w, "weekly", "periodic")
    ref = fac._apply_cap_and_lambda(w, "cap10", "lambda_0")
    out = gpu_core.eval_cell_gpu(
        combined.to_numpy(np.float64),
        rank_desc.to_numpy(np.float64),
        top_n=10,
        sizing_mode="inv_vol",
        freq_step=5,
        trigger="periodic",
        cap=0.10,
        lam=0.0,
        vol20=vol.to_numpy(np.float64),
        backend="cpu",
    )
    assert out["host_continue"] is False
    got = pd.DataFrame(out["weights"], index=px.index, columns=px.columns)
    m = ref.notna() & got.notna()
    assert float((abs(got[m] - ref[m]) / (abs(ref[m]) + 1e-300)).max().max()) <= 1e-12


@pytest.mark.parametrize(
    ("trigger", "lam", "expect"), [("drift_band", 0.0, True), ("periodic", 0.005, True), ("periodic", 0.0, False)]
)
def test_eval_cell_host_continue_declares_cpu_handoff(trigger, lam, expect):
    """交接点出声钉：drift_band 与 lambda>0 必须置 host_continue，禁卡上自造串行近似。"""
    px = _synth_px()
    combined = _synth_factors(px, k=1)[0]
    rank_desc = combined.rank(axis=1, ascending=False)
    out = gpu_core.eval_cell_gpu(
        combined.to_numpy(np.float64),
        rank_desc.to_numpy(np.float64),
        top_n=10,
        sizing_mode="equal_weight",
        freq_step=5,
        trigger=trigger,
        cap=0.10,
        lam=lam,
        vol20=_vol_panel(px).to_numpy(np.float64),
        backend="cpu",
    )
    assert out["host_continue"] is expect


@needs_gpu
def test_eval_cell_gpu_backend_matches_cpu():
    """后端切换不得改数值：同一入参 GPU vs CPU 权重 ≤1e-12。"""
    import cupy as cp

    px = _synth_px()
    combined = _synth_factors(px, k=1)[0]
    rank_desc = combined.rank(axis=1, ascending=False)
    vol = _vol_panel(px)
    args = dict(top_n=10, sizing_mode="inv_vol", freq_step=5, trigger="periodic", cap=0.10, lam=0.0)
    a = combined.to_numpy(np.float64)
    r = rank_desc.to_numpy(np.float64)
    v = vol.to_numpy(np.float64)
    cpu = gpu_core.eval_cell_gpu(a, r, vol20=v, backend="cpu", **args)
    gpu = gpu_core.eval_cell_gpu(cp.asarray(a), cp.asarray(r), vol20=cp.asarray(v), backend="gpu", **args)
    rel = float((np.abs(gpu["weights"] - cpu["weights"]) / (np.abs(cpu["weights"]) + 1e-300)).max())
    assert rel <= 1e-12
    assert gpu["backend"] == "gpu" and cpu["backend"] == "cpu"
