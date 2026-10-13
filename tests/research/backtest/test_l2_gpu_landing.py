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

    # 桩形须与 _c4_engine.run_backtest_full 同签（exec_caliber/px_exec 由 st-ddup-20260925
    # 双产物改造引入，本班补齐——此前整波被 None.reindex 打死，这条漂移从未暴露过）。
    # 故意**不写 **kwargs**：桩与生产签名一旦再度漂移要像这次一样大声 TypeError，不要静默吞参。
    def run_backtest_full(
        weights,
        px,
        gate_limits=True,
        slippage_bp=None,
        *,
        backend=None,
        pre_tensor=None,
        exec_caliber="close",
        px_exec=None,
    ):
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


def test_vram_admission_gate_refuses_and_agrees_with_registry():
    """准入闸判别力钉（总统统筹 2026-10-11 05:3x 裁定③）：册上预算必须真被代码消费。

    三面缺一不可：①读到的预算与 `search_space_prereg.yaml` 的键值同源相等（防"册写一个数、
    代码用另一个数"）；②预算设成不可能的天文值时必须**拒绝**上卡并计 vram_refused（尺能红）；
    ③预算=0（缺键语义）时不得拦路（禁把"读不到"变成"不许跑"）。
    """
    import yaml

    budget_key = yaml.safe_load(Path(fac.PREREG_PATH).read_text(encoding="utf-8"))["budget_caps"]["vram"][
        "per_path_budget_mib"
    ]
    fac._VRAM_BUDGET_MIB = None
    assert fac._vram_per_path_budget_mib() == int(budget_key) > 0, "册值与代码读数不同源"

    old_backend, old_budget = fac._EVAL_BACKEND, fac._VRAM_BUDGET_MIB
    for k in fac._EVAL_GPU_STATS:
        fac._EVAL_GPU_STATS[k] = 0
    try:
        fac._EVAL_BACKEND = "gpu"
        fac._VRAM_BUDGET_MIB = 10**9  # 天文预算：任何机器都该拒
        assert fac._dev_xp() is None, "显存准入闸零判别力（永不拒绝）"
        refused_after_first = fac._EVAL_GPU_STATS["vram_refused"]
        assert refused_after_first >= 1, "拒绝未计数"
        fac._VRAM_BUDGET_MIB = 0  # 缺键语义=不设闸，不得拦路
        xp = fac._dev_xp()
        # 判据用增量而非总计：上面那次拒绝合法在册，拿总计==0 断言是测试自己的记账错
        assert xp is not None, "预算为 0 时仍拦路=把读不到当成不许跑"
        assert fac._EVAL_GPU_STATS["vram_refused"] == refused_after_first, "缺键语义下不得新增拒绝计数"
    finally:
        fac._EVAL_BACKEND, fac._VRAM_BUDGET_MIB = old_backend, old_budget


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


def test_host_mem_admission_gate_refuses_and_agrees_with_registry():
    """主机 RAM 准入闸判别力钉（2026-10-11 N-3 实测补腿）：册上 host_mem 预算必须真被消费。

    病案：六路并发 × 逐路峰值 RSS 4.4GB 把 64GB 主机打到零，两路 GPU 波在 numpy 分配
    37.4MiB 时 MemoryError→整波重跑 CPU。显存腿单独立册拦不住这件事，故第二腿同闸同计数。
    四面缺一不可：①代码读数与 `search_space_prereg.yaml` 键值同源相等；②天文预算必拒并计
    host_mem_refused（尺能红）；③水位不可测（-1）只计数不拦路；④预算=0（缺键语义）不拦路。
    """
    import yaml

    key = yaml.safe_load(Path(fac.PREREG_PATH).read_text(encoding="utf-8"))["budget_caps"]["host_mem"][
        "per_path_peak_mib"
    ]
    fac._PREREG_BUDGET_SECTIONS.clear()
    fac._HOST_MEM_BUDGET_MIB = None
    assert fac._host_mem_per_path_peak_mib() == int(key) > 0, "册值与代码读数不同源"

    old = (fac._EVAL_BACKEND, fac._VRAM_BUDGET_MIB, fac._HOST_MEM_BUDGET_MIB, fac._HOST_MEM_PROBE)
    for k in fac._EVAL_GPU_STATS:
        fac._EVAL_GPU_STATS[k] = 0
    try:
        fac._EVAL_BACKEND = "gpu"
        fac._VRAM_BUDGET_MIB = 0  # 关掉显存腿，本支只测主机腿（否则两闸混在一起读不出归因）
        fac._HOST_MEM_BUDGET_MIB = 10**9  # 天文预算：任何机器都该拒
        fac._HOST_MEM_PROBE = (fac.time.perf_counter(), 1000)  # 假水位=可用 1000MiB（TTL 内不被真探针覆写）
        assert fac._dev_xp() is None, "主机内存准入闸零判别力（永不拒绝）"
        refused = fac._EVAL_GPU_STATS["host_mem_refused"]
        assert refused >= 1, "拒绝未计数"

        fac._HOST_MEM_PROBE = (fac.time.perf_counter(), -1)  # 不可测面：不得当成"不许跑"
        unmeasured_before = fac._EVAL_GPU_STATS["host_mem_unmeasured"]
        xp = fac._dev_xp()
        assert xp is not None, "水位读不到时拦路=把不可测当成不许跑"
        assert fac._EVAL_GPU_STATS["host_mem_unmeasured"] == unmeasured_before + 1, "不可测未计数"
        assert fac._EVAL_GPU_STATS["host_mem_refused"] == refused, "不可测不得冒充拒绝"

        fac._HOST_MEM_BUDGET_MIB = 0  # 缺键语义=不设闸
        fac._HOST_MEM_PROBE = (fac.time.perf_counter(), 1)
        assert fac._dev_xp() is not None, "预算为 0 时仍拦路"
        assert fac._EVAL_GPU_STATS["host_mem_refused"] == refused, "缺键语义下不得新增拒绝计数"
    finally:
        fac._EVAL_BACKEND, fac._VRAM_BUDGET_MIB, fac._HOST_MEM_BUDGET_MIB, fac._HOST_MEM_PROBE = old
        fac._PREREG_BUDGET_SECTIONS.clear()
        fac._HOST_MEM_BUDGET_MIB = None


def test_eval_memory_pressure_degrades_to_cpu_not_cell_death():
    """MemoryError 是资源态不是判据态（2026-10-11 N-3 实测：22 格因此被记成 eval 阴性）。

    三面同钉：①首次 MemoryError 后卸缓存+停卡+计数，重试成功=本格正常出分（不记阴性）；
    ②本批此后 `_dev_xp()` 必返回 None（禁刚卸完资源又立刻上卡把 RAM 再顶到零）；
    ③二次仍 MemoryError 必须上抛给既有记账口（禁静默——真耗尽要照旧出声）。
    """
    old = (fac._EVAL_BACKEND, fac._VRAM_BUDGET_MIB, fac._HOST_MEM_BUDGET_MIB, fac._EVAL_MEM_PRESSURE)
    base = {k: fac._EVAL_GPU_STATS[k] for k in fac._EVAL_GPU_STATS}
    fac._DEV_PANEL_CACHE["sentinel"] = object()
    calls = {"n": 0}

    def _boom_once():
        calls["n"] += 1
        if calls["n"] == 1:
            raise MemoryError("Unable to allocate 37.4 MiB for an array with shape (970, 5058)")
        return ("weights", ("degraded",))

    try:
        fac._EVAL_BACKEND = "gpu"
        fac._VRAM_BUDGET_MIB = 0
        fac._HOST_MEM_BUDGET_MIB = 0
        w, d = fac._eval_cell_mem_retry(_boom_once)
        assert (w, d) == ("weights", ("degraded",)), "重试成功后本格应正常出分"
        assert calls["n"] == 2, "未真正重试一次"
        assert fac._EVAL_GPU_STATS["memory_pressure"] == base["memory_pressure"] + 1, "内存压力未计数"
        assert not fac._DEV_PANEL_CACHE, "设备面板缓存未卸（下格还会顶上去）"
        fac._HOST_MEM_PROBE = (fac.time.perf_counter(), 10**9)  # 水位充足，唯一可能的拦路=停卡旗
        assert fac._dev_xp() is None, "MemoryError 后本批仍上卡=没停卡"

        def _boom_always():
            raise MemoryError("still exhausted")

        raised = False
        try:
            fac._eval_cell_mem_retry(_boom_always)
        except MemoryError:
            raised = True
        assert raised, "二次失败必须上抛给既有 eval 记账口（禁静默成正常格）"
        assert fac._EVAL_GPU_STATS["memory_pressure"] == base["memory_pressure"] + 2
    finally:
        (
            fac._EVAL_BACKEND,
            fac._VRAM_BUDGET_MIB,
            fac._HOST_MEM_BUDGET_MIB,
            fac._EVAL_MEM_PRESSURE,
        ) = old
        fac._DEV_PANEL_CACHE.clear()


def test_device_attempt_failure_is_never_silent_in_counters():
    """零计数不得等于"未知态"（2026-10-11 06:32 假配对病案）。

    那次 `--eval-backend gpu` 的子进程把 `zephyr` 解析到了**主区旧字节**（worktree 裸 python 导主区包），
    `from ... import nvml_device_memory` 抛 ImportError → 被 `_dev_xp` 的宽 except 吞成"降级 CPU"，
    而 summary.eval_gpu **十个计数全零**、只在 stderr 留一行 → 产物看起来像"跑了，只是没上卡"，
    本班据此把一轮 CPU-vs-CPU 当成了 CPU-vs-GPU 等价性证据。两条静默出口现在都必须计数。
    """
    old = (fac._EVAL_BACKEND, fac._VRAM_BUDGET_MIB, fac._HOST_MEM_BUDGET_MIB, fac._EVAL_MEM_PRESSURE)
    for k in fac._EVAL_GPU_STATS:
        fac._EVAL_GPU_STATS[k] = 0
    try:
        fac._EVAL_BACKEND = "gpu"
        fac._VRAM_BUDGET_MIB = 0
        fac._HOST_MEM_BUDGET_MIB = 0
        fac._EVAL_MEM_PRESSURE = False

        import zephyr.backtest.gpu_core as gc

        real = gc.resolve_backend
        try:
            gc.resolve_backend = lambda req=None: "cpu"
            assert fac._dev_xp() is None
            assert fac._EVAL_GPU_STATS["resolve_not_gpu"] == 1, "resolve 出口未计数（零计数=未知态）"

            def _boom(req=None):
                raise ImportError("cannot import name 'nvml_device_memory' from 'zephyr.backtest.gpu_core'")

            gc.resolve_backend = _boom
            assert fac._dev_xp() is None
            assert fac._EVAL_GPU_STATS["dev_attempt_failed"] == 1, "宽 except 出口未计数"
        finally:
            gc.resolve_backend = real
        assert fac._EVAL_GPU_STATS["prefix_gpu"] == 0 and fac._EVAL_GPU_STATS["cell_gpu"] == 0
    finally:
        (
            fac._EVAL_BACKEND,
            fac._VRAM_BUDGET_MIB,
            fac._HOST_MEM_BUDGET_MIB,
            fac._EVAL_MEM_PRESSURE,
        ) = old


def test_no_shadowed_test_names_in_gpu_suite():
    """尺的尺：同文件内 `test_` 名重复定义＝后名静默遮蔽前名，遮蔽那份**永不执行**。

    病案（2026-10-11 上一班留档，本袋 A 清偿）：`test_industsize_ctrl_demeaned_...` 在同文件被定义
    两次（:853 与 :927），Python 只把最后一份绑进命名空间 ⇒ 第一份 57 行从未跑过，而采集计数看着
    正常。属"采集计数骗后来人"族（同族：collected 含虚数、收 0 项而退出码 0）。
    判据按**单文件**算（跨文件同名合法＝不同命名空间），故不能只数全目录名集合。
    """
    import ast
    import collections

    here = Path(__file__).resolve().parent
    scanned = []
    for nm in (
        Path(__file__).resolve().name,
        "test_gpu_core_parity.py",
        "test_factory_grid_instruments.py",
        "test_c4_engine_gpu_wiring.py",
    ):
        fp = here / nm
        if not fp.exists():
            continue  # 缺件不算通过：由下面 scanned 数量兜住（禁把"没扫到"读成"扫过且干净"）
        scanned.append(fp.name)
        tree = ast.parse(fp.read_text(encoding="utf-8"))
        names = [
            n.name
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")
        ]
        dup = sorted(k for k, v in collections.Counter(names).items() if v > 1)
        assert not dup, f"{fp} 内同名重复定义（后名遮蔽前名，前者永不执行）: {dup}"
    assert len(scanned) >= 2, f"本尺实际只扫到 {scanned}——覆盖面不足即失去判别力"


# ═══ B1a（st-gpux2-20261011，2026-10-11 夜）：λ 链上卡与它的两面钉 ═══


def _lambda_matrix(t: int, s: int, seed: int) -> np.ndarray:
    """造覆盖全部敏感形态的权重矩阵：首行全 NaN（前置 NaN 不衰减 old_wt）／全 NaN 行
    （row-sum 走 0→NaN→fillna 路径）／全零行／相邻等值（原码"常数列短路"）／连续 7 个 NaN
    （old_wt 连乘）／S 取 7·8·129·135 与 450（numpy 成对树的 n<8／8≤n≤128／递归分裂三形）。
    """
    rng = np.random.default_rng(seed)
    w = np.zeros((t, s))
    for i in range(t):
        k = int(min(int(rng.integers(1, 40)), s))
        pick = rng.choice(s, size=k, replace=False)
        v = rng.random(k) + 0.01
        w[i, pick] = v / v.sum()
    w[rng.random((t, s)) < 0.03] = np.nan
    w[3] = np.nan
    w[11, :] = 0.0
    w[12, 5 % s] = w[11, 5 % s]
    for j in range(0, s, 37):
        w[40:47, j] = np.nan
    w[0, :] = np.nan
    return w


@needs_gpu
@pytest.mark.parametrize(("t", "s"), [(970, 450), (200, 130), (64, 7), (64, 135)])
@pytest.mark.parametrize("lam_name", ["lambda_5bp", "lambda_15bp", "lambda_0"])
def test_lambda_chain_gpu_bitwise_matches_pandas(t, s, lam_name):
    """B1a 正向钉：设备 λ 链与 `_apply_cap_and_lambda` **逐位**等（禁降级成相对容差）。

    逐位不是洁癖：λ 段产物直接进仓位与换手，而 drift_band 的判据是 `nansum>0.2` 这种硬阈值——
    换求和结合序就换调仓日，换调仓日就换净值，那已经不是"容差内"而是换题。
    真源=pandas 2.3.3 aggregations.pyx:1791-1827 + core/window/ewm.py:97 + numpy 2.3.5
    loops_utils.h.src:80-145（本机已对源码逐行誊写并验过树与 pandas 行和逐位等）。
    """
    import cupy as cp

    x = _lambda_matrix(t, s, 20261011 + s)
    ref = fac._apply_cap_and_lambda(pd.DataFrame(x), "cap10", lam_name).to_numpy()
    lam = fac._LAMBDA_PEN[lam_name] * 100.0
    got = cp.asnumpy(gpu_core.lambda_chain_gpu(cp.asarray(x), 0.10, lam))
    if not np.array_equal(ref, got, equal_nan=True):
        bad = np.nonzero(~((ref == got) | (np.isnan(ref) & np.isnan(got))))
        i0, j0 = int(bad[0][0]), int(bad[1][0])
        pytest.fail(
            f"λ 链设备镜像偏离 shape={(t, s)} lam={lam_name} 不符={len(bad[0])} "
            f"首处 t={i0} c={j0} pandas={ref[i0, j0]!r} gpu={got[i0, j0]!r} 输入={x[i0, j0]!r}"
        )


@needs_gpu
def test_lambda_chain_gpu_naive_alpha_route_deviates(monkeypatch):
    """两面钉的反面（3′ 纪律：守卫必须能红）：省掉 pandas 的 alpha→com→alpha 往返，
    设备链必须**偏离** pandas——否则上面那条"逐位等"是空跑。

    病形实测：pandas 不吃字面 0.05，它先 com=(1-α)/α 再由核内 α=1/(1+com) 反解，
    得 0.05000000000000001（差 1 ULP）。少这一步＝整条递推系统偏离，且不报错。
    """
    import cupy as cp

    x = _lambda_matrix(200, 129, 99)
    ref = fac._apply_cap_and_lambda(pd.DataFrame(x), "cap10", "lambda_5bp").to_numpy()
    lam = fac._LAMBDA_PEN["lambda_5bp"] * 100.0
    assert np.array_equal(ref, cp.asnumpy(gpu_core.lambda_chain_gpu(cp.asarray(x), 0.10, lam)), equal_nan=True)
    monkeypatch.setattr(gpu_core, "ewm_alpha_pair", lambda alpha: (1.0 - alpha, alpha))
    naive = cp.asnumpy(gpu_core.lambda_chain_gpu(cp.asarray(x), 0.10, lam))
    assert not np.array_equal(ref, naive, equal_nan=True), "字面 alpha 与往返 alpha 同解＝本钉失焦"


def test_device_kernel_sources_forbid_single_precision_intrinsics():
    """静默降级尺：CUDA 的 `__fadd_rn/__fmul_rn/__fdiv_rn` 是**单精度**内在函数，喂 double 会
    静默降 float32（本班实测：偏离相对量级 9e-8、不报错、不改判据——比 FMA 融合更阴）。
    双精度唯一正确拼写是 `__dadd_rn/__dmul_rn/__dsub_rn/__ddiv_rn`。

    判据扫 gpu_core 全部 `*_SRC` 内核源；探测器自带红证（含样例必判红），防"尺空跑"。
    """
    import ast
    import re

    tree = ast.parse(Path(gpu_core.__file__).read_text(encoding="utf-8"))
    srcs: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            if not isinstance(node.value.value, str):
                continue
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id.endswith("_SRC"):
                    srcs[tgt.id] = node.value.value
    assert srcs, "没扫到任何内核源常量＝尺空跑"
    single = re.compile(r"__f(add|sub|mul|div|sqrt)_rn")
    offenders = {k: sorted(set(single.findall(v))) for k, v in srcs.items() if single.search(v)}
    assert not offenders, f"内核源出现单精度内在函数（double 静默降 float32）: {offenders}"
    ewm_src = srcs.get("_EWM_LAMBDA_KERNEL_SRC")
    assert ewm_src is not None, "λ 链内核源不在位（B1a 未落地或被改名）"
    assert "__dmul_rn" in ewm_src and "__dadd_rn" in ewm_src and "__ddiv_rn" in ewm_src, (
        "λ 递推段退回裸运算符＝nvcc 默认 -fmad=true 会把乘加融成一条 FMA＝换结合序"
        "（pandas 的 C 编译无此融合，逐位等的前提失效）"
    )
    assert single.search("void k(){ a = __fmul_rn(x, y); }"), "探测器失效：连样例都抓不住"


@needs_gpu
@pytest.mark.parametrize(
    ("trigger", "lam", "glue", "expect_hc", "expect_glue"),
    [
        ("periodic", 0.05, True, False, True),
        ("periodic", 0.05, False, True, False),
        ("drift_band", 0.05, True, True, False),
        ("drift_band", 0.0, True, True, False),
        ("periodic", 0.0, True, False, False),
    ],
)
def test_eval_cell_glue_gpu_switch_matrix(trigger, lam, glue, expect_hc, expect_glue):
    """开关矩阵钉：glue 只清它真接管的段。drift_band 的串行扫归 B1b，未接管就不许装成已上卡
    （host_continue 必须继续出声，`glue_lambda` 必须为 False）。缺省关＝现网逐字节零漂移。
    """
    import cupy as cp

    px = _synth_px()
    combined = _synth_factors(px, k=1)[0]
    rank_desc = combined.rank(axis=1, ascending=False)
    vol = _vol_panel(px).to_numpy(np.float64)
    out = gpu_core.eval_cell_gpu(
        cp.asarray(combined.to_numpy(np.float64)),
        cp.asarray(rank_desc.to_numpy(np.float64)),
        top_n=10,
        sizing_mode="equal_weight",
        freq_step=5,
        trigger=trigger,
        cap=0.10,
        lam=lam,
        vol20=cp.asarray(vol),
        backend="gpu",
        glue_gpu=glue,
    )
    assert out["host_continue"] is expect_hc, (trigger, lam, glue, out["host_continue"], expect_hc)
    assert out["glue_lambda"] is expect_glue, (trigger, lam, glue, out["glue_lambda"], expect_glue)


def test_eval_glue_gpu_wiring_is_single_point():
    """接线钉（防 WO-A4 同型病：包装段各手写一遍参数→漏一处静默回全空间）：
    ①`_EVAL_GLUE_GPU` 缺省 False（判据面零动的机械保证）；②CLI 是 store_true；
    ③全文件对该局部的赋值**只有一处**注入点（加上声明共两处），多一处就多一条分叉真源。
    """
    import ast

    tree = ast.parse((_REPO / "scripts" / "backtest" / "factory_grid_executor.py").read_text(encoding="utf-8"))
    decl = [
        n
        for n in tree.body
        if isinstance(n, ast.AnnAssign)
        and isinstance(n.target, ast.Name)
        and n.target.id == "_EVAL_GLUE_GPU"
        and isinstance(n.value, ast.Constant)
        and n.value.value is False
    ]
    assert len(decl) == 1, "_EVAL_GLUE_GPU 必须有一处 `: bool = False` 缺省声明"
    writes = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
            if any(isinstance(t, ast.Name) and t.id == "_EVAL_GLUE_GPU" for t in tgts):
                writes.append(n)
    assert len(writes) == 2, f"_EVAL_GLUE_GPU 赋值点应=2（声明+main 注入），实测 {len(writes)}＝出现第二真源"
    text = (_REPO / "scripts" / "backtest" / "factory_grid_executor.py").read_text(encoding="utf-8")
    assert '"--eval-glue-gpu"' in text and "store_true" in text.split('"--eval-glue-gpu"')[1][:200], (
        "CLI 旗须为 store_true（缺省关）"
    )


@needs_gpu
@pytest.mark.parametrize("freq_step", [1, 5])
@pytest.mark.parametrize("with_nan", [False, True])
def test_eval_cell_glue_gpu_substitution_is_bitwise(freq_step, with_nan):
    """替换面双面钉（B1a 的真实命题）：**同一份卡上产物**在"回主机跑 pandas λ"与"卡上跑 λ 链"
    之间必须逐位等。

    刻意不与 `_sizing` 的 pandas 全链对拍——那条上游映射在册只到 rel≤1e-12
    （test_eval_cell_end_to_end_matches_pandas_chain），拿它当基线会把上游的既有偏差
    误算到本刀头上（判据要指准自己改的那一段）。

    两个参数轴都是**实测逼出来的**，不是排列组合凑数：
    ·freq_step=5 会让主机续跑段先过 `iloc[::step].reindex(ffill)`，那一帧变 F 序；
    ·F 序 + 无 NaN 时 pandas 的行和走**朴素顺序累加**而不是成对树（见
     test_pandas_rowsum_order_follows_layout_rule）——本袋最初版本正是漏了这条，
     才在 t=5 暴露 1-2 ULP 偏离（不符 14689 元素，最大 4.16e-17）。
    """
    import cupy as cp

    px = _synth_px()
    combined = _synth_factors(px, k=1)[0]
    if with_nan:
        combined = combined.copy()
        combined.iloc[::7, 0] = np.nan
    else:
        combined = combined.fillna(0.0)
    rank_desc = combined.rank(axis=1, ascending=False)
    vol = _vol_panel(px)
    if not with_nan:
        vol = vol.fillna(0.0)
    freq = "daily" if freq_step == 1 else "weekly"
    lam = fac._LAMBDA_PEN["lambda_5bp"] * 100.0
    args = dict(
        top_n=10,
        sizing_mode="inv_vol",
        freq_step=freq_step,
        trigger="periodic",
        cap=0.10,
        lam=lam,
        vol20=cp.asarray(vol.to_numpy(np.float64)),
        backend="gpu",
    )
    base = gpu_core.eval_cell_gpu(
        cp.asarray(combined.to_numpy(np.float64)),
        cp.asarray(rank_desc.to_numpy(np.float64)),
        glue_gpu=False,
        **args,
    )
    assert base["host_continue"] is True and base["glue_lambda"] is False
    w_off = pd.DataFrame(np.asarray(base["weights"]), index=combined.index, columns=combined.columns)
    assert bool(np.isnan(combined.to_numpy()).any()) is bool(with_nan), "输入夹具形态与声明不符"
    # 臂 A 的确切形态：主机先重跑幂等 trigger，再跑 pandas cap+λ
    ref = fac._apply_cap_and_lambda(fac._apply_freq_trigger(w_off, freq, "periodic"), "cap10", "lambda_5bp")
    glued = gpu_core.eval_cell_gpu(
        cp.asarray(combined.to_numpy(np.float64)),
        cp.asarray(rank_desc.to_numpy(np.float64)),
        glue_gpu=True,
        **args,
    )
    assert glued["host_continue"] is False and glued["glue_lambda"] is True
    ok = np.array_equal(ref.to_numpy(), glued["weights"], equal_nan=True)
    if not ok:
        a, b = ref.to_numpy(), glued["weights"]
        bad = np.nonzero(~((a == b) | (np.isnan(a) & np.isnan(b))))
        i0, j0 = int(bad[0][0]), int(bad[1][0])
        pytest.fail(
            f"续跑段替换偏离（step={freq_step} nan={with_nan}）：不符={len(bad[0])} "
            f"最大={float(np.nanmax(np.abs(a[bad] - b[bad]))):.3e} 首处 t={i0} c={j0} "
            f"回主机={a[i0, j0]!r} 卡上={b[i0, j0]!r} 入参={base['weights'][i0, j0]!r}"
        )


def test_pandas_rowsum_order_follows_layout_rule():
    """常驻尺（量的是**主机参照自身**，不是我的实现）：`_apply_cap_and_lambda` 里被 sum 的那一帧
    是 clip→ewm 的输出帧（实测恒 F 序），于是 pandas 的行和结合序只由"有无 NaN"决定：

      有 NaN  → skipna 造新连续数组 → 成对树；
      无 NaN  → 归约轴跨步 → 朴素顺序累加（-0.0 起手）。

    来源=2026-10-11 实测（`.runtime/tmp/st-gpux2-20261011/pandas_sum_layout_probe.py`，
    S=36/450/846/5217 一致）。B1a 的 `pairwise` 判据完全建立在它上面；pandas 若改内部布局或
    skipna 路径，本尺先红，设备镜像判据必须重估——禁沿用旧律静默换数。
    """
    rng = np.random.default_rng(20261011)
    x = np.clip(rng.normal(size=(240, 36)) * 0.05, None, 0.10)

    def tree(r: np.ndarray) -> float:
        n = len(r)
        if n < 8:
            s = -0.0
            for v in r:
                s += float(v)
            return s
        if n <= 128:
            a = [float(r[k]) for k in range(8)]
            i = 8
            stop = n - (n % 8)
            while i < stop:
                for k in range(8):
                    a[k] += float(r[i + k])
                i += 8
            res = ((a[0] + a[1]) + (a[2] + a[3])) + ((a[4] + a[5]) + (a[6] + a[7]))
            while i < n:
                res += float(r[i])
                i += 1
            return res
        n2 = n // 2
        n2 -= n2 % 8
        return tree(r[:n2]) + tree(r[n2:])

    def seq(r: np.ndarray) -> float:
        s = -0.0
        for v in r:
            s += float(v)
        return s

    for src in (np.ascontiguousarray(x), np.asfortranarray(x)):
        we = pd.DataFrame(src).clip(upper=0.10).ewm(alpha=0.05, adjust=False).mean()
        v = we.to_numpy()
        assert not v.flags["C_CONTIGUOUS"], "被 sum 的帧应变 F 序（律的前提），布局假设变了要重估 pairwise"
        rs = we.sum(axis=1).to_numpy()
        tr = np.array([tree(r) for r in v])
        sq = np.array([seq(r) for r in v])
        assert not np.array_equal(tr, sq), "两把参照自己相同＝本尺失去判别力"
        assert np.array_equal(rs, sq) and not np.array_equal(rs, tr), "无 NaN 应=顺序累加且≠成对树"

    xn = x.copy()
    xn[rng.random(xn.shape) < 0.15] = np.nan
    for src in (np.ascontiguousarray(xn), np.asfortranarray(xn)):
        we = pd.DataFrame(src).clip(upper=0.10).ewm(alpha=0.05, adjust=False).mean()
        v = we.to_numpy()
        rs = we.sum(axis=1).to_numpy()
        tr = np.array([tree(np.where(np.isnan(r), 0.0, r)) for r in v])
        sq = np.array([seq(np.where(np.isnan(r), 0.0, r)) for r in v])
        assert not np.array_equal(tr, sq), "有 NaN 组两参照相同＝失去判别力"
        assert np.array_equal(rs, tr) and not np.array_equal(rs, sq), "有 NaN 应=成对树（skipna 掩码后新连续数组）"


def test_universe_column_order_is_pinned_sorted():
    """跨进程可复现钉（根因入法，2026-10-12 n8 归因）：宇宙→列序那一句**必须**是有序生成。

    病案：`cols = [c for c in universe_cache[g] if ...]` 里 `universe_cache[g]` 是 `set[str]`，
    集合迭代序随字符串哈希（PYTHONHASHSEED）**逐进程变**，而 cols 随即进面板
    （`closes_eval[cols]`→因子→`universe_cols`）⇒ 同 seed 同参的两次跑批列序不同→并列票位置翻转
    →净值不可复现。实测三预言（`.runtime/tmp/st-gpux2-20261011/n8_attribution_probe.py`，
    24 格，PYTHONHASHSEED=1/2/1）：同进程 eval×2 与 bt×2 全逐位等（排除 BLAS/归约序）；
    换 seed 则列序签名与 net_sha 全变；同 seed 重跑逐位等 ⇒ 列序是唯一变量。
    修复后（seed=5 vs 6 两进程）列序签名／w_sha／net_sha 三者全同。

    判据取**结构面**而非跨进程 subprocess： subprocess 两支会把"跑批一次"的成本与 CH 依赖
    引进单测（在册病案：测试禁靠生产数据面自证）；而语义面钉"`cols == sorted(cols)`"必须由
    生成式保证，AST 直接判那一句的形态最有效且零数据依赖。
    红证自带：同一判据打在修复前的原文上必须判败（见 _PRE_FIX 分支）。
    """
    import ast

    text = (_REPO / "scripts" / "backtest" / "factory_grid_executor.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == "cols" for t in tgts):
                hits.append(node)
    assert hits, "没扫到任何 `cols =` 赋值＝尺空跑"
    universe_cols_assigns = [
        n
        for n in hits
        if isinstance(n.value, (ast.ListComp, ast.GeneratorExp, ast.Call)) and "universe_cache" in ast.dump(n.value)
    ]
    assert len(universe_cols_assigns) == 1, (
        f"宇宙→列序的生成点应恰 1 处（多一处就多一条无序真源），实测 {len(universe_cols_assigns)}"
    )
    stmt = universe_cols_assigns[0]
    assert (
        isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "sorted"
    ), f"那一行必须经 sorted() 定序；实测形态={ast.dump(stmt.value)[:160]}"
    # 红证：修复前的原形态（无 sorted 的裸列表推导）在同判据下必须判败
    pre_fix = ast.parse("cols = [c for c in universe_cache[g] if c in closes_eval.columns]").body[0]
    assert not (isinstance(pre_fix.value, ast.Call) and getattr(pre_fix.value.func, "id", "") == "sorted"), (
        "红证失效：修复前形态也能过这条判据＝本钉没有牙"
    )


def test_eval_gpu_stats_has_all_glue_exits():
    """三面出口各有计数（在册教训：零计数器与"未触发"同形＝假绿）：卡内做完／回灌卡上／
    卡面异常回退，任一为空都要能从 summary 读出"到底是没走还是走了没成"。
    """
    for key in ("glue_gpu_inline", "glue_gpu_reupload", "glue_gpu_failed"):
        assert key in fac._EVAL_GPU_STATS, f"缺计数键 {key}＝该出口无从判读"
        assert fac._EVAL_GPU_STATS[key] == 0, f"{key} 应为模块级零值（测试期不得被生产计数污染）"


# ——— 八、批级设备面板缓存的纪律（st-gpux5-20261013 修法乙＋丙）———
# 被测面全部用 numpy 替身跑，不占卡、不碰 CH：要判读的是"命中三闸与逐出策略"，
# 与设备无关。真设备面由 §十六 的全格集分族验收针负责，两把尺各判各的，禁互相顶替。
_PC_KEYS = ("pc_hit", "pc_put", "pc_identity_miss", "pc_dirty_hit", "pc_evict", "pc_verifier_off")


class _FakeXP:
    """xp 替身：记"真的建了几趟"，于是 hit/miss 能从调用数差分判读而不是从叙述判读。

    `asarray` 必须**拷**而不是取视图：真设备路里 `xp.asarray` 出来的是一份与主机缓冲无关的
    设备副本，缓存值因此不会被宿主后来的就地改写带着一起变。取视图的话"重建件与原件不等"
    这条判据会假绿（本班首版就假在这——改完宿主，连缓存里那枚旧值也跟着改了）。
    """

    def __init__(self) -> None:
        self.builds = 0

    def asarray(self, a):
        self.builds += 1
        return np.array(a, dtype=np.float64, copy=True)


def _pc_reset(verify: bool = False, strict: bool = False) -> None:
    fac.set_panel_cache_verify(verify, strict)
    fac.reset_panel_cache()
    for k in _PC_KEYS:
        fac._EVAL_GPU_STATS[k] = 0


def _pc(**want: int) -> None:
    got = {k: fac._EVAL_GPU_STATS[k] for k in want}
    assert got == dict(want), f"面板缓存计数不符：得到 {got}，期望 {dict(want)}"


def _panel_frame(seed: int = 11, rows: int = 30, cols: int = 6) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        rng.normal(1.0, 0.3, size=(rows, cols)),
        index=pd.bdate_range("2022-01-03", periods=rows),
        columns=[f"{600000 + i}" for i in range(cols)],
    )


def test_panel_cache_exposes_all_six_exits():
    """六出口各有键（零计数器与"未触发"同形是在册病型，先证读数面齐）。"""
    for k in _PC_KEYS:
        assert k in fac._EVAL_GPU_STATS, f"缺计数键 {k}＝该出口无从判读"


def test_panel_cache_rejects_same_key_different_host():
    """乙：键撞而宿主不是同一对象＝必须不命中并重建（id() 复用型脏命中的正面判据）。

    现实里这条的触发形态是"上一块面板被 GC、新面板拿到同一个地址"——那在测试里不可靠，
    所以这里直接把"同键＋不同宿主"当它的等价形喂进来（键由 id() 组成，两对象同址时键必等）。
    """
    _pc_reset()
    xp = _FakeXP()
    key = ("logmv", 1234, 6, "600000", "600005", 30)
    host_a = _panel_frame(11)
    first = fac._dev_panel(key, lambda: host_a, xp, host=host_a)
    _pc(pc_put=1, pc_hit=0)
    second = fac._dev_panel(key, lambda: host_a, xp, host=host_a)
    assert first is second, "同宿主同键必须复用同一枚设备缓冲（没复用＝本刀白做）"
    _pc(pc_put=1, pc_hit=1)
    assert xp.builds == 1, f"第二次不该再建一趟，实际建了 {xp.builds} 趟"

    host_b = _panel_frame(12)  # 同形不同内容，且是另一个对象
    third = fac._dev_panel(key, lambda: host_b, xp, host=host_b)
    _pc(pc_put=2, pc_hit=1, pc_identity_miss=1)
    assert xp.builds == 2, "身份不符却没重建＝pin 判定失守（脏命中）"
    assert not np.array_equal(third, first), "重建件与脏件同值＝比较器没有牙，上面那条判绿是白判"


def test_panel_cache_sentinel_catches_in_place_mutation():
    """丙：同一宿主被就地改写（乙的 `is` 仍真）必须被内容指纹抓到并重建。"""
    _pc_reset(verify=True)
    xp = _FakeXP()
    key = ("vol", 4321, 6, "600000", "600005")
    host = _panel_frame(21)
    first = fac._dev_panel(key, lambda: host, xp, host=host)
    _pc(pc_put=1, pc_dirty_hit=0)
    host.iloc[5, 2] = 9.995  # 就地改写：对象身份不变，乙挡不住这一类
    second = fac._dev_panel(key, lambda: host, xp, host=host)
    _pc(pc_put=2, pc_hit=0, pc_dirty_hit=1)
    assert not np.array_equal(second, first), "抓到脏命中却没重建＝哨兵只是摆设"


def test_panel_cache_sentinel_strict_raises():
    """丙的"不匹配即红"执行位：STRICT 档下同一场景直接抛，不静默重建。"""
    _pc_reset(verify=True, strict=True)
    xp = _FakeXP()
    key = ("mvw", 555, 6, "600000", "600005")
    host = _panel_frame(31)
    fac._dev_panel(key, lambda: host, xp, host=host)
    host.iloc[0, 0] = -1234.5
    with pytest.raises(RuntimeError, match="内容指纹不符"):
        fac._dev_panel(key, lambda: host, xp, host=host)
    _pc(pc_dirty_hit=1)


def test_panel_cache_in_place_mutation_slips_through_when_sentinel_off():
    """反向对照（缺省档）：哨兵关着时同一改写**必须**被判成命中并返回旧值。

    这条是上一切的判别力来源——若两档行为一致，则"丙抓到了"根本没法证伪。
    同时如实记在缺省面读数里的 `pc_verifier_off`：绿要能读出"这枚命中没吃内容校验"。
    """
    _pc_reset(verify=False)
    xp = _FakeXP()
    key = ("r60m", 777, 6, "600000", "600005")
    host = _panel_frame(41)
    first = fac._dev_panel(key, lambda: host, xp, host=host)
    host.iloc[5, 2] = 9.995
    second = fac._dev_panel(key, lambda: host, xp, host=host)
    assert first is second, "缺省档不校验内容＝这枚命中本就该是旧值（改了说明哨兵在缺省面偷偷跑）"
    _pc(pc_put=1, pc_hit=1, pc_dirty_hit=0, pc_verifier_off=1)
    assert xp.builds == 1


def test_panel_cache_fingerprint_is_nan_stable():
    """指纹不得把"含 NaN 但一字未变"判成变了（检验道自犯＝515 条假告警那一族）。"""
    host = _panel_frame(51)
    host.iloc[0, 0] = np.nan
    host.iloc[-1, -1] = np.nan
    a = fac._panel_fp(host)
    b = fac._panel_fp(host.copy())
    assert a == b, f"同一内容两副本指纹不等＝满命中假阳的源头没修掉：{a} vs {b}"
    # 无 NaN 面同判：原件与副本的内存布局可不同，归约序随之差 1 ULP（本班首版尺实测到）
    clean = _panel_frame(52)
    assert fac._panel_fp(clean) == fac._panel_fp(clean.copy()), "同内容因帧布局换末位＝布局敏感假阳"
    f_ordered = pd.DataFrame(
        np.asfortranarray(clean.to_numpy(dtype=np.float64)), index=clean.index, columns=clean.columns
    )
    assert fac._panel_fp(f_ordered) == fac._panel_fp(clean), "F 序同内容换末位＝归约序没先归一化"
    other = host.copy()
    other.iloc[0, 0] = 0.0  # NaN 与 0.0 必须是两回事，否则哨兵对首/末 NaN 失明
    assert fac._panel_fp(other) != a, "NaN 与 0.0 折成同一位＝首末元素失明"
    moved = host.copy()
    moved.iloc[7, 3] += 1.0
    assert fac._panel_fp(moved) != a, "内容变了指纹却不动＝尺瞎"


def test_panel_cache_w_site_keys_on_content_not_identity():
    """瞬态宿主站点（`w`＝每前缀新建）：乙的 `is` 永假，所以键改用内容指纹——
    既保住命中率（同内容必命中），又挡住脏命中（不同内容必不命中）。"""
    _pc_reset()
    w1 = _panel_frame(61, rows=20, cols=3)
    w2 = w1.copy()  # 同内容、不同对象＝现实里"下一个前缀新算出一张一样的权重板"
    k1 = ("w", "ic_ir", 3, fac._panel_fp(w1))
    k2 = ("w", "ic_ir", 3, fac._panel_fp(w2))
    assert k1 == k2, "同内容权重板键不等＝命中面永远空转（乙把该站点打成永久失配的前兆）"
    xp = _FakeXP()
    first = fac._dev_panel_dev(k1, lambda: xp.asarray(w1.to_numpy(dtype=np.float64)))
    second = fac._dev_panel_dev(k2, lambda: xp.asarray(w2.to_numpy(dtype=np.float64)))
    assert first is second, "内容键命中失败＝本刀在该站点只换来一次重算"
    _pc(pc_put=1, pc_hit=1)
    w3 = w1.copy()
    w3.iloc[2, 2] = 77.0
    k3 = ("w", "ic_ir", 3, fac._panel_fp(w3))
    assert k3 != k1, "不同内容同键＝脏命中的门还开着"
    fac._dev_panel_dev(k3, lambda: xp.asarray(w3.to_numpy(dtype=np.float64)))
    _pc(pc_put=2, pc_hit=1)


def test_dev_cache_put_evicts_one_not_everything():
    """N-1②：溢出改 FIFO 逐一枚。旧形整清会把工作集全丢（实测＝缓存退化成每前缀重算）。

    这里不动 `_DEV_CACHE_CAP` 的真值，只按它的当前值造溢出——若将来容量再调，
    这条判据（"逐出后仍剩 cap 枚，且最新那枚在、最旧那枚不在"）照样成立。
    """
    _pc_reset()
    cap = fac._DEV_CACHE_CAP
    keys = [(f"e{i}",) for i in range(cap + 3)]
    for kk in keys:
        fac._dev_cache_put(kk, np.zeros(16, dtype=np.float64), None, None)
    assert len(fac._DEV_PANEL_CACHE) == cap, (
        f"逐出后剩 {len(fac._DEV_PANEL_CACHE)} 枚，既不是 cap 也不是整清后的 0/1＝逐出形不可读"
    )
    assert keys[-1] in fac._DEV_PANEL_CACHE, "刚放进去的就被逐掉＝预算算错了"
    assert keys[0] not in fac._DEV_PANEL_CACHE, "最旧那枚没被逐掉＝不是 FIFO"
    assert fac._DEV_PANEL_CACHE[keys[3]] is not None, "整清复发（连中段都保不住）"
    _pc(pc_evict=3)


def test_dev_cache_put_respects_byte_budget(monkeypatch):
    """字节预算兜显驻：超预算时按 FIFO 逐，且不会把刚放入的那枚逐空自己。"""
    _pc_reset()
    monkeypatch.setattr(fac, "_DEV_PANEL_BYTE_CAP", 300)
    for i in range(6):
        fac._dev_cache_put((f"b{i}",), np.zeros(32, dtype=np.float64), None, None)  # 每枚 256B
    # 预算 300B 而每枚 256B ⇒ 稳态只能剩最新那一枚（不是 0 枚、也不是全部）：
    # 逐空自己＝把缓存改成"每格重算"，两个方向都要钉住。
    assert len(fac._DEV_PANEL_CACHE) == 1, f"预算稳态应只剩 1 枚，实际 {len(fac._DEV_PANEL_CACHE)} 枚"
    assert ("b5",) in fac._DEV_PANEL_CACHE, "留下的不是最新那枚＝FIFO 与预算的配合反了"
    assert sum(int(getattr(v, "nbytes", 0)) for (_h, v, _f) in fac._DEV_PANEL_CACHE.values()) <= 300


def test_reset_panel_cache_clears_events_and_pins():
    """批起点复位面：缓存与事件一起清（乙 pin 住宿主引用，这里同时是唯一释放面）。"""
    _pc_reset(verify=True)
    xp = _FakeXP()
    host = _panel_frame(71)
    key = ("fwdrank", 909, 6, "600000", "600005")
    fac._dev_panel(key, lambda: host, xp, host=host)
    host.iloc[3, 3] = 5.5
    fac._dev_panel(key, lambda: host, xp, host=host)
    assert fac.panel_cache_events(), "抓到脏命中却不留事件＝晨间包无法复算"
    assert fac.panel_cache_stats()["pc_dirty_hit"] == 1
    fac.reset_panel_cache()
    assert not fac._DEV_PANEL_CACHE, "缓存未随批起点复位＝上一批的 id() 还在这本账上"
    assert not fac.panel_cache_events(), "事件跨批残留＝把上一批的现行犯算进本批头上"


# ——— 九、A1 归一化批内共享缓存的纪律（st-gpux6-20261013 第二把刀，承五班 §十七·I P-1）———
# 与 §八 同一判读纪律：命中三闸＋逐出＋复位各有独立计数，且"缺省档必须漏"那条反向对照
# 是哨兵一切判别力的来源。被测面全合成、零 CH、零卡时——归一化是主机 pandas 腿，
# 它的等价性由 §二·戊 族验收针在真批次上判，不由本节判。
_NC_KEYS = ("nc_hit", "nc_put", "nc_identity_miss", "nc_dirty_hit", "nc_evict", "nc_verifier_off")


def _nc_reset(verify: bool = False, strict: bool = False) -> None:
    fac.set_panel_cache_verify(verify, strict)
    fac.reset_panel_cache()
    for k in _NC_KEYS:
        fac._EVAL_GPU_STATS[k] = 0


def _nc(**want: int) -> None:
    got = {k: fac._EVAL_GPU_STATS[k] for k in want}
    assert got == dict(want), f"归一化缓存计数不符：得到 {got}，期望 {dict(want)}"


def _norm_frames(seed: int = 5, rows: int = 24, cols: int = 5):
    """(宿主全帧, 列切片) —— 真批次里 `factors[n]` 是批级长寿命件，`f=factors[n][cols]` 每前缀新建。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2022-01-03", periods=rows)
    names = [f"{600000 + i}" for i in range(cols)]
    host = pd.DataFrame(rng.normal(1.0, 0.4, size=(rows, cols)), index=idx, columns=names)
    return host, host[names[:cols]]


def _counting_normalize(monkeypatch):
    """把 `_normalize` 换成"记账＋转调原件"——重建几趟从调用数判读，不从叙述判读。"""
    real = fac._normalize
    seen = {"n": 0}

    def spy(factor, mode, industry_map=None, mkt_cap_w=None):
        seen["n"] += 1
        return real(factor, mode, industry_map=industry_map, mkt_cap_w=mkt_cap_w)

    monkeypatch.setattr(fac, "_normalize", spy)
    return seen


def test_norm_cache_exposes_all_six_exits():
    """六出口各有键（零计数器与"未触发"同形是在册病型，先证读数面齐）。"""
    for k in _NC_KEYS:
        assert k in fac._EVAL_GPU_STATS, f"缺计数键 {k}＝该出口无从判读"


def test_norm_cache_hit_reuses_frame_and_stops_recompute(monkeypatch):
    """本刀的本体：同宿主同 mode 同列面＝第二趟必须复用，且 `_normalize` 只被调一次。

    这条同时是"没复用的话上面全部白判"的存在性前置——8 个 A2 挂在一个 (G,A1) 组上，
    复用不成＝定价 8.0 倍冗余一分未落。
    """
    _nc_reset()
    seen = _counting_normalize(monkeypatch)
    host, sl = _norm_frames(5)
    v1, d1 = fac._normalize_cached(sl, "zscore", None, None, host, "f_mom20")
    v2, d2 = fac._normalize_cached(sl, "zscore", None, None, host, "f_mom20")
    assert v1 is v2, "同键同宿主没复用同一枚帧＝本刀白做"
    assert (d1, d2) == (False, False)
    _nc(nc_put=1, nc_hit=1, nc_verifier_off=1)
    assert seen["n"] == 1, f"第二趟仍重算（{seen['n']} 趟）＝命中面没接到求值口"


def test_norm_cache_equals_fresh_normalize_by_construction(monkeypatch):
    """ "共享==逐格重算"的构造面：三档（zscore/rank/raw）＋降级档各复现直调结果。

    raw 档另钉一条：`_normalize` 在 raw 下**返回入参本身**，所以它必须直传不进缓存
    ——把瞬态切片塞进缓存＝无谓延长它的寿命，且零收益。
    """
    _nc_reset()
    seen = _counting_normalize(monkeypatch)
    for mode, expect_deg in (("zscore", False), ("rank", False), ("no_such_mode", True)):
        host, sl = _norm_frames(seed=7, rows=20, cols=4)
        before = seen["n"]
        cached, deg = fac._normalize_cached(sl, mode, None, None, host, "f_lowvol20")
        n_cached = seen["n"]
        fresh, fdeg = fac._normalize(sl, mode, industry_map=None, mkt_cap_w=None)
        assert n_cached == before + 1, f"{mode} 档缓存口没走到求值本体（本档 {n_cached - before} 趟）"
        assert deg == fdeg == expect_deg, f"{mode} 档 degraded 标志与直调不符"
        assert cached.shape == fresh.shape
        assert np.array_equal(cached.to_numpy(), fresh.to_numpy(), equal_nan=True), (
            f"{mode} 档缓存值与直调逐位不等＝同一函数体的构造论证塌了"
        )
    _nc_reset()
    host, sl = _norm_frames(seed=9)
    raw_out, raw_deg = fac._normalize_cached(sl, "raw", None, None, host, "f_ma_gap")
    assert raw_out is sl and raw_deg is False, "raw 档必须直传原切片"
    assert not fac._NORM_CACHE, "raw 档进了缓存＝瞬态切片被 pin 住"


def test_norm_cache_rejects_same_key_different_host(monkeypatch):
    """乙：键撞而宿主不是同一对象＝不命中并重建（id() 复用型脏命中的等价形，与 §八 同法）。

    现实触发形态是"上一帧被 GC、新帧拿到同一个地址"，测试里不可靠，所以直接把
    "该键位上的 pin 换成别的对象"喂进来——键由 id() 组成，两对象同址时键必等。
    """
    _nc_reset()
    seen = _counting_normalize(monkeypatch)
    host_a, sl_a = _norm_frames(11)
    host_b, sl_b = _norm_frames(12, rows=25)
    fac._normalize_cached(sl_a, "zscore", None, None, host_a, "f_mom20")
    fac._normalize_cached(sl_b, "zscore", None, None, host_b, "f_mom20")
    key_b = list(fac._NORM_CACHE)[-1]  # host_b 那一条的键位
    stored_val = fac._NORM_CACHE[key_b][1]
    fac._NORM_CACHE[key_b] = ((host_a, None, None), stored_val, False, None)  # 把 pin 换成外来宿主
    before = seen["n"]
    out, _ = fac._normalize_cached(sl_b, "zscore", None, None, host_b, "f_mom20")
    _nc(nc_put=3, nc_identity_miss=1)
    assert out is not stored_val, "身份不符却交回了外来宿主那枚＝pin 判定失守（脏命中）"
    assert seen["n"] == before + 1, "身份不符后没重建＝缓存把这枚脏命中当成了本批的数"


def test_norm_cache_sentinel_catches_in_place_mutation(monkeypatch):
    """丙：同一宿主被就地改写（乙的 `is` 仍真）必须被内容指纹抓到并重建。

    形态照真批次喂：批级宿主 `factors[n]` 长寿命、每前缀的切片 `f=factors[n][cols]` 是新副本，
    所以"下一前缀的切片"是在改写之后才取的——若哨兵不放行重建，本批就会拿上一改写前的旧值出分。
    """
    _nc_reset(verify=True)
    seen = _counting_normalize(monkeypatch)
    host, _ = _norm_frames(21)
    names = list(host.columns)
    first, _ = fac._normalize_cached(host[names], "zscore", None, None, host, "f_mom20")
    host.iloc[5, 2] = 9.995
    second, _ = fac._normalize_cached(host[names], "zscore", None, None, host, "f_mom20")
    _nc(nc_put=2, nc_dirty_hit=1)
    assert not np.array_equal(first.to_numpy(), second.to_numpy()), "抓到脏命中却没重建＝哨兵只是摆设"
    assert seen["n"] == 2


def test_norm_cache_sentinel_strict_raises():
    """丙的"不匹配即红"执行位：STRICT 档下同一场景直接抛，不静默重建。"""
    _nc_reset(verify=True, strict=True)
    host, sl = _norm_frames(31)
    fac._normalize_cached(sl, "zscore", None, None, host, "f_mom20")
    host.iloc[0, 0] = -1234.5
    with pytest.raises(RuntimeError, match="内容指纹不符"):
        fac._normalize_cached(sl, "zscore", None, None, host, "f_mom20")
    _nc(nc_dirty_hit=1)


def test_norm_cache_in_place_mutation_slips_through_when_sentinel_off(monkeypatch):
    """反向对照（缺省档）：哨兵关着时同一改写**必须**仍判命中并返回旧值。

    两档若同形，"丙抓到了"就不可证伪——这条是上一切的判别力来源（与 §八 同一条纪律）。
    """
    _nc_reset(verify=False)
    seen = _counting_normalize(monkeypatch)
    host, sl = _norm_frames(41)
    first, _ = fac._normalize_cached(sl, "zscore", None, None, host, "f_mom20")
    host.iloc[5, 2] = 9.995
    second, _ = fac._normalize_cached(sl, "zscore", None, None, host, "f_mom20")
    assert first is second, "缺省档不校验内容＝这枚命中本就该是旧值（改了说明哨兵在缺省面偷偷跑）"
    _nc(nc_put=1, nc_hit=1, nc_dirty_hit=0, nc_verifier_off=1)
    assert seen["n"] == 1


def test_norm_cache_evicts_one_not_everything(monkeypatch):
    """逐出＝FIFO 单枚＋字节预算，禁整清（整清把刚建好的一起丢掉＝缓存退化成每前缀重算）。"""
    _nc_reset()
    seen = _counting_normalize(monkeypatch)
    monkeypatch.setattr(fac, "_NORM_CACHE_CAP", 2)
    built = []
    for i in range(3):
        host, sl = _norm_frames(seed=50 + i, rows=12 + i, cols=3)
        built.append(fac._normalize_cached(sl, "zscore", None, None, host, f"f_{i}")[0])
    assert len(fac._NORM_CACHE) == 2, f"溢出后剩 {len(fac._NORM_CACHE)} 枚＝逐出策略不是单枚"
    _nc(nc_put=3, nc_evict=1)
    assert seen["n"] == 3
    assert any(v[1] is built[2] for v in fac._NORM_CACHE.values()), "最新一枚被逐出＝FIFO 认错了人"
    assert not any(v[1] is built[0] for v in fac._NORM_CACHE.values()), "最旧一枚没被逐出＝逐的不是该逐的那枚"


def test_norm_cache_respects_byte_budget(monkeypatch):
    """字节预算＝按 pandas 帧的 `memory_usage` 计（不是 `.nbytes`——2.3 版 DataFrame 无该属性，
    照搬设备侧写法会恒得 0，预算就成了永不触发的装饰件）；超预算逐最旧，逐到落下来为止。"""
    _nc_reset()
    monkeypatch.setattr(fac, "_NORM_CACHE_CAP", 24)
    h0 = _norm_frames(61, rows=16, cols=4)[0]
    v0, _ = fac._normalize_cached(h0[list(h0.columns)[:2]], "zscore", None, None, h0, "g_0")
    one = int(v0.memory_usage(deep=False).sum())
    assert one > 0, "尺先瞎了：预算按 0 计的话，下面那条断言就是空判"
    monkeypatch.setattr(fac, "_NORM_BYTE_CAP", one * 2 + 1)
    for i in (1, 2):
        h, s = _norm_frames(seed=70 + i, rows=16, cols=4)
        fac._normalize_cached(s.iloc[:, :2], "zscore", None, None, h, f"g_{i}")
    assert len(fac._NORM_CACHE) == 2, f"字节预算失守：仍留 {len(fac._NORM_CACHE)} 枚"
    assert fac._norm_cache_bytes() <= one * 2 + 1
    _nc(nc_put=3, nc_evict=1)


def test_reset_panel_cache_clears_norm_cache(monkeypatch):
    """复位腿：归一化缓存与面板缓存同批起点清空（键里带上一批宿主的 id()，留着＝脏命中温床；
    乙 pin 住宿主，这里同时是唯一释放面）。"""
    _nc_reset()
    seen = _counting_normalize(monkeypatch)
    host, sl = _norm_frames(81)
    fac._normalize_cached(sl, "zscore", None, None, host, "f_mom20")
    assert fac._NORM_CACHE, "先决条件不成立：没建进缓存，下面的复位断言是空转"
    fac.reset_panel_cache()
    assert not fac._NORM_CACHE, "归一化缓存跨批残留＝上一批的 id() 还在这本账上"
    fac._normalize_cached(sl, "zscore", None, None, host, "f_mom20")
    assert seen["n"] == 2, "复位后没重算＝缓存其实没被清（假清）"


def test_normalize_host_site_is_closed_behind_the_cache():
    """装配守卫：主机归一化站点只准经 `_normalize_cached`，禁再出现直调 `_normalize` 的站点。

    成因是在册教训（检验道 §十七·K②）——漏接站点会被宽 `except` 吞成 fail-open：
    格面照样出分、缓存计数全是零，看上去"绿"，实际那把刀一分未落。本节 §九 其余各条判的是
    缓存自身，这一条判的是"站点确实接上了"。
    """
    import ast as _ast
    import inspect as _inspect

    src = _inspect.getsource(fac)
    tree = _ast.parse(src)
    ranges = {}
    for n in _ast.walk(tree):
        if isinstance(n, _ast.FunctionDef):
            ranges[n.name] = (n.lineno, n.end_lineno or n.lineno)
    direct, via = [], []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Call) and isinstance(node.func, _ast.Name):
            if node.func.id == "_normalize":
                direct.append(node.lineno)
            if node.func.id == "_normalize_cached":
                via.append(node.lineno)
    lo, hi = ranges["_normalize_cached"]
    callers = [ln for ln in direct if not (lo <= ln <= hi)]  # 缓存口内部那一趟是本体，不是站点
    assert via, "找不到 `_normalize_cached` 的调用点＝第二把刀根本没接线"
    assert not callers, f"仍有站点直调 `_normalize`（行 {callers}）＝该站点绕过缓存，静默性能回归"
