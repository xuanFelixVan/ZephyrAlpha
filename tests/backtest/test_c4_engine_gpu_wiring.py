# [BLUEPRINT] MOD-BT-233 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_c4_engine_gpu_wiring
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; scripts.backtest.translated._c4_engine; zephyr.backtest.gpu_core(可选)
# [CONSUMERS] MODIFY-GUARD: scripts/backtest/translated/_c4_engine.py（P1 接线面）+ scripts/backtest/factory_grid_executor.py（L1 hoist 调用面）
# [STARTUP] imported
# [MATURITY] trial
# [INVARIANTS] backend="cpu" 恒原 pandas 路径逐位一致（零漂移红线，hoisted/pre_tensor 同）;
#   run_backtest_full_with_tiers 单趟三产物与 run_backtest_full+net_returns_by_tiers 两连调逐位一致;
#   非法 backend=ValueError; 快路径资格=等形对齐（px 多列/索引错位=回 pandas 原路径且输出逐位一致）;
#   auto 档小面板（<_GPU_AUTO_MIN_CELLS）不因 GPU 在场而漂移（尺寸守卫，实测依据
#   docs/_working/gpu_rewrite/p1_wiring_benchmark.md §四）;
#   GPU 后端（cupy 可用时）vs CPU 相对差<=1e-12（FP64 红线）; 全合成数据零 CH 依赖
# # （_load_seal_masks monkeypatch，CH 停机夜可跑）
# [MODIFY-GUARD] scripts/backtest/translated/_c4_engine.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败；cupy/gpu_core 不可用->GPU 用例 skip（CPU 用例恒跑）
# [TESTS] pytest tests/backtest/test_c4_engine_gpu_wiring.py
# [TTL] permanent
"""P1 接线守护测试——CPU 逐位红线 + 单趟三产物等价 + 后端开关/资格守卫 + GPU parity。

数据全合成（numpy seeded float64），零 CH（_load_seal_masks monkeypatch）；
gpu_core 缺件（P0 未落地树）时 GPU 用例自动 skip，CPU 用例不依赖 gpu_core。
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


def _load_gpu_core():
    """gpu_core 双世界解析（动态导入=可选依赖，P0 未落地树零硬引用）：
    包导入优先（P0 落地树），缺件回退同仓文件注入（工作树本地验证），全缺= None（GPU 用例 skip）。"""
    try:
        return importlib.import_module("zephyr.backtest.gpu_core")
    except ImportError:
        pass
    _gc_file = _REPO / "src" / "zephyr" / "backtest" / "gpu_core.py"
    if _gc_file.exists():  # pragma: no cover - 分支取决于落地状态
        _spec = importlib.util.spec_from_file_location("zephyr.backtest.gpu_core", _gc_file)
        _mod = importlib.util.module_from_spec(_spec)
        sys.modules["zephyr.backtest.gpu_core"] = _mod
        _spec.loader.exec_module(_mod)
        return _mod
    return None


gpu_core = _load_gpu_core()

SEED = 20260929
T, S = 300, 80
TIERS = (0.0, 5.0, 10.0, 20.0, 40.0)


def _synthetic():
    rng = np.random.default_rng(SEED)
    idx = pd.bdate_range("2022-01-03", periods=T)
    cols = [f"{600000 + i}" for i in range(S)]
    px = pd.DataFrame(100.0 + np.cumsum(rng.normal(0, 1.0, size=(T, S)), axis=0), index=idx, columns=cols)
    px.iloc[:10, :5] = np.nan
    px.iloc[50:55, 10:20] = np.nan
    su = pd.DataFrame(rng.random((T, S)) < 0.02, index=idx, columns=cols)
    sd = pd.DataFrame(rng.random((T, S)) < 0.02, index=idx, columns=cols)
    return px, su, sd


@pytest.fixture()
def synth(monkeypatch):
    px, su, sd = _synthetic()
    monkeypatch.setattr(eng, "_load_seal_masks", lambda index, columns: (su, sd))
    return px


def _weights(px, k=0):
    rng = np.random.default_rng(SEED + 100 + k)
    w = rng.normal(0, 0.05, size=px.shape)
    w[w < 0] = 0.0
    rs = w.sum(axis=1, keepdims=True)
    rs[rs == 0] = 1.0
    wd = pd.DataFrame(w / rs, index=px.index, columns=px.columns)
    wd.iloc[:5, :8] = np.nan
    return wd


def test_cpu_backend_bitexact_hoisted(synth):
    """backend=cpu：hoisted/pre_tensor 与原路径逐位一致（零漂移红线）。"""
    w = _weights(synth)
    s0, n0 = eng.run_backtest_full(w, synth, backend="cpu")
    pre = eng.prep_px_tensor(w.index, synth)
    s1, n1 = eng.run_backtest_full(w, synth, backend="cpu", pre_tensor=pre)
    s2, n2 = eng.run_backtest_full(w, synth, pre_tensor=pre)
    assert np.array_equal(n0.values, n1.values) and s0 == s1
    assert np.array_equal(n0.values, n2.values) and s0 == s2
    assert np.array_equal(eng.daily_net_returns(w, synth, backend="cpu", pre_tensor=pre).values, n0.values)
    assert eng.run_backtest(w, synth, backend="cpu") == s0


def test_tiers_single_pass_bitexact(synth):
    """单趟三产物 vs 两连调：stats/net/五档 net 逐位一致。"""
    w = _weights(synth, 1)
    pre = eng.prep_px_tensor(w.index, synth)
    st1, net1, tiers1 = eng.run_backtest_full_with_tiers(w, synth, TIERS, backend="cpu", pre_tensor=pre)
    st2, net2 = eng.run_backtest_full(w, synth, backend="cpu", pre_tensor=pre)
    tiers2 = eng.net_returns_by_tiers(w, synth, TIERS, backend="cpu", pre_tensor=pre)
    assert st1 == st2 and np.array_equal(net1.values, net2.values)
    assert set(tiers1) == set(tiers2)
    for bp in TIERS:
        assert np.array_equal(tiers1[float(bp)].values, tiers2[float(bp)].values)


def test_invalid_backend_raises(synth):
    w = _weights(synth)
    with pytest.raises(ValueError):
        eng.run_backtest_full(w, synth, backend="tpu")
    with pytest.raises(ValueError):
        eng._resolve_engine_backend("TPU")


def test_fastpath_ineligible_falls_back_bitexact(synth):
    """px 多列 / 索引错位 = 资格否决回 pandas 原路径，输出与 canonical 逐位一致。"""
    w = _weights(synth)
    px_extra = synth.copy()
    px_extra["999999"] = 50.0
    s0, n0 = eng.run_backtest_full(w, px_extra, backend="cpu")
    s1, n1 = eng.run_backtest_full(w, px_extra, backend="cpu", pre_tensor=eng.prep_px_tensor(w.index, px_extra))
    assert np.array_equal(n0.values, n1.values) and s0 == s1
    w_short = w.iloc[10:]
    s2, n2 = eng.run_backtest_full(w_short, synth, backend="cpu")
    s3, n3 = eng.run_backtest_full(w_short, synth)
    assert np.array_equal(n2.values, n3.values) and s2 == s3


@pytest.mark.skipif(gpu_core is None or not gpu_core.HAS_GPU, reason="cupy/CUDA 不可用（GPU 用例跳过）")
def test_gpu_parity_within_1e12(synth):
    """GPU 后端 vs CPU：相对差 <=1e-12（FP64 红线）。"""
    w = _weights(synth, 2)
    _, n_cpu = eng.run_backtest_full(w, synth, backend="cpu")
    _, n_gpu = eng.run_backtest_full(w, synth, backend="gpu")
    common = n_cpu.notna() & n_gpu.notna()
    rel = float((abs(n_gpu[common] - n_cpu[common]) / (abs(n_cpu[common]) + 1e-300)).max())
    assert rel <= 1e-12
    st1, net1, tiers1 = eng.run_backtest_full_with_tiers(w, synth, TIERS, backend="gpu")
    st2, net2, tiers2 = eng.run_backtest_full_with_tiers(w, synth, TIERS, backend="cpu")
    assert set(tiers1) == set(tiers2)
    for bp in TIERS:
        d = np.abs(tiers1[float(bp)].values - tiers2[float(bp)].values)
        scale = np.abs(tiers2[float(bp)].values) + 1e-300
        assert float((d / scale).max()) <= 1e-12


@pytest.mark.skipif(gpu_core is None or not gpu_core.HAS_GPU, reason="cupy/CUDA 不可用（守卫用例按 CPU 恒等断言恒跑）")
def test_auto_small_panel_no_gpu_drift(synth, monkeypatch):
    """auto 档尺寸守卫：小面板（<_GPU_AUTO_MIN_CELLS）输出与显式 cpu 逐位一致。"""
    monkeypatch.delenv("ZEPHYR_COMPUTE_BACKEND", raising=False)
    w = _weights(synth)
    assert w.size < eng._GPU_AUTO_MIN_CELLS
    s0, n0 = eng.run_backtest_full(w, synth, backend="cpu")
    s1, n1 = eng.run_backtest_full(w, synth)  # backend=None → auto
    assert np.array_equal(n0.values, n1.values) and s0 == s1


def test_resolve_backend_values(monkeypatch):
    """_resolve_engine_backend 三态：cpu 恒 cpu；非法值 ValueError；缺 gpu_core 件=cpu 回退。"""
    monkeypatch.delenv("ZEPHYR_COMPUTE_BACKEND", raising=False)
    assert eng._resolve_engine_backend("cpu") == "cpu"
    if gpu_core is None:
        assert eng._resolve_engine_backend(None) == "cpu"
    else:
        assert eng._resolve_engine_backend(None) in ("cpu", "gpu")
