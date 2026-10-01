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
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
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
