# [BLUEPRINT] MOD-BT-233 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_gpu_core_parity
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; scripts.backtest.translated._c4_engine; zephyr.backtest.gpu_core
# [CONSUMERS] MODIFY-GUARD: zephyr.backtest.gpu_core（CPU 逐位等价红线 + GPU 1e-12 相对差红线）
# [STARTUP] imported
# [MATURITY] trial
# [INVARIANTS] CPU 后端与引擎 _backtest_core+_net_line 逐位一致（array_equal，含闸开/闸关两态、
#   合成掩码注入——CH 停机夜零 CH 依赖，monkeypatch _load_seal_masks）;
#   GPU 后端（skipif 无 cupy）与 CPU 相对差 <=1e-12（FP64 红线：全程 float64，禁 float32/TF32）;
#   后端开关三态：env 未设=auto（cupy 可用即 gpu 否则 cpu）、env=cpu 恒 CPU、
#   env=gpu 且 cupy 不可用=fail-closed 降级 CPU 并出声（degrade 台账非空，禁静默）;
#   FP64 dtype 收口断言（非 float64 输入被 astype 收口）;
#   GPU smoke（无 cupy 跳过）：小阵列真机执行并打印设备名（记录不 assert）
# [MODIFY-GUARD] zephyr.backtest.gpu_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败；cupy 不可用->gpu 用例 skip（CPU 用例恒跑）
# [TESTS] pytest tests/backtest/test_gpu_core_parity.py
# [TTL] permanent
"""gpu_core 对拍守护测试——CPU 逐位等价 + GPU 1e-12 相对差 + 后端开关三态。

数据纪律：全合成（numpy seeded float64），零 CH 依赖（CH 停机夜 2026-09-28 也能跑）；
真机 GPU smoke 仅在 cupy 真实可用时执行，设备名只记录不 assert。
"""

from __future__ import annotations

import os
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

import _c4_engine  # noqa: E402

from zephyr.backtest import gpu_core  # noqa: E402

SEED = 20260928
T, S = 300, 80


def _synthetic() -> tuple[pd.DataFrame, pd.DataFrame, tuple[np.ndarray, np.ndarray]]:
    """合成面板：float64 权重+价格，撒 NaN（leading/interior）与合成封板掩码。"""
    rng = np.random.default_rng(SEED)
    px = 100.0 + np.cumsum(rng.normal(0, 1.0, size=(T, S)), axis=0)
    w = rng.normal(0, 0.05, size=(T, S))
    w[w < 0] = 0.0
    px[:10, :5] = np.nan  # leading NaN（ffill 语义）
    px[50:55, 10:20] = np.nan  # interior NaN（ffill 填充）
    w[:8, :7] = np.nan  # weights leading NaN（fillna(0) 语义）
    w[100:102, 30:40] = np.nan
    su = rng.random((T, S)) < 0.02  # 封涨停 2%
    sd = rng.random((T, S)) < 0.02  # 封跌停 2%
    su[0, :] = False  # 首日无闸语义可对照（prev 全零）
    sd[0, :] = False
    idx = pd.date_range("2024-01-01", periods=T, freq="B")
    cols = pd.RangeIndex(S)
    return (
        pd.DataFrame(w, index=idx, columns=cols),
        pd.DataFrame(px, index=idx, columns=cols),
        (su, sd),
    )


def _engine_ref(w_df: pd.DataFrame, px_df: pd.DataFrame, masks, gate: bool):
    """引擎参照（真身函数，零重实现）：mask 注入走 monkeypatch，不触 CH。"""
    su_df = pd.DataFrame(masks[0], index=w_df.index, columns=w_df.columns)
    sd_df = pd.DataFrame(masks[1], index=w_df.index, columns=w_df.columns)
    orig = _c4_engine._load_seal_masks
    _c4_engine._load_seal_masks = lambda i, c: (su_df, sd_df)  # type: ignore[method-assign]
    try:
        gross, turnover = _c4_engine._backtest_core(w_df, px_df, gate_limits=gate)
        net = _c4_engine._net_line(gross, turnover, _c4_engine.SLIPPAGE_BP)
    finally:
        _c4_engine._load_seal_masks = orig  # type: ignore[method-assign]
    return gross.to_numpy(), turnover.to_numpy(), net.to_numpy()


# ——— 1. CPU 逐位等价（闸关：纯张量面）———


def test_cpu_bitwise_vs_engine_gate_off():
    w_df, px_df, masks = _synthetic()
    ref = _engine_ref(w_df, px_df, masks, gate=False)
    out = gpu_core.tensor_core(w_df, px_df, gate_masks=masks, gate_limits=False, backend="cpu")
    assert np.array_equal(out["gross"], ref[0]), "gross 逐位失配（gate off）"
    assert np.array_equal(out["turnover"], ref[1]), "turnover 逐位失配（gate off）"
    assert np.array_equal(out["nets"][float(_c4_engine.SLIPPAGE_BP)], ref[2]), "net 逐位失配（gate off）"


# ——— 2. CPU 逐位等价（闸开：合成掩码注入，串行闸循环同式）———


def test_cpu_bitwise_vs_engine_gate_on():
    w_df, px_df, masks = _synthetic()
    ref = _engine_ref(w_df, px_df, masks, gate=True)
    out = gpu_core.tensor_core(w_df, px_df, gate_masks=masks, gate_limits=True, backend="cpu")
    assert np.array_equal(out["gross"], ref[0]), "gross 逐位失配（gate on）"
    assert np.array_equal(out["turnover"], ref[1]), "turnover 逐位失配（gate on）"
    assert np.array_equal(out["nets"][float(_c4_engine.SLIPPAGE_BP)], ref[2]), "net 逐位失配（gate on）"


# ——— 3. 多档成本线（五档标量乘一趟出）———


def test_cpu_tiers_bitwise_vs_engine():
    w_df, px_df, masks = _synthetic()
    tiers = [0.0, 2.5, 5.0, 10.0, 20.0]
    su_df = pd.DataFrame(masks[0], index=w_df.index, columns=w_df.columns)
    sd_df = pd.DataFrame(masks[1], index=w_df.index, columns=w_df.columns)
    orig = _c4_engine._load_seal_masks
    _c4_engine._load_seal_masks = lambda i, c: (su_df, sd_df)  # type: ignore[method-assign]
    try:
        ref = _c4_engine.net_returns_by_tiers(w_df, px_df, tiers, gate_limits=True)
    finally:
        _c4_engine._load_seal_masks = orig  # type: ignore[method-assign]
    out = gpu_core.tensor_core(w_df, px_df, gate_masks=masks, slippage_bps=tiers, backend="cpu")
    for bp in tiers:
        assert np.array_equal(out["nets"][float(bp)], ref[bp]), f"tier {bp} net 逐位失配"


# ——— 4. GPU/CPU 对拍（<=1e-12 相对差；无 cupy 跳过）———


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用（GPU 路径 skip，CPU 路径已恒跑）")
def test_gpu_parity_within_1e_12():
    w_df, px_df, masks = _synthetic()
    cpu = gpu_core.tensor_core(w_df, px_df, gate_masks=masks, slippage_bps=[0.0, 2.5, 5.0, 10.0], backend="cpu")
    gpu = gpu_core.tensor_core(w_df, px_df, gate_masks=masks, slippage_bps=[0.0, 2.5, 5.0, 10.0], backend="gpu")
    assert gpu["backend"] == "gpu"
    for key in ("gross", "turnover"):
        scale = max(1.0, float(np.max(np.abs(cpu[key]))))
        rel = float(np.max(np.abs(gpu[key] - cpu[key]))) / scale
        assert rel <= 1e-12, f"{key} GPU/CPU 相对差 {rel:.3e} 超 1e-12"
    for bp, net_gpu in gpu["nets"].items():
        net_cpu = cpu["nets"][bp]
        scale = max(1.0, float(np.max(np.abs(net_cpu))))
        rel = float(np.max(np.abs(net_gpu - net_cpu))) / scale
        assert rel <= 1e-12, f"net[{bp}] GPU/CPU 相对差 {rel:.3e} 超 1e-12"


# ——— 5. GPU 真机 smoke（记录设备名，不 assert）———


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")
def test_gpu_smoke_real_device(capsys):
    info = gpu_core.device_info()
    print(f"[gpu-smoke] device={info}")  # 记录用：设备名/CUDA runtime/cupy 版本
    xp = gpu_core._cp
    a = xp.asarray(np.random.default_rng(1).standard_normal((64, 64)), dtype=xp.float64)
    r = float(xp.asnumpy((a @ a.T).trace()))
    assert np.isfinite(r)


# ——— 6. 后端开关三态———


def test_backend_env_unset_is_auto(monkeypatch):
    monkeypatch.delenv(gpu_core.BACKEND_ENV, raising=False)
    assert gpu_core.resolve_backend() == ("gpu" if gpu_core.gpu_available() else "cpu")
    assert gpu_core.resolve_backend("auto") == gpu_core.resolve_backend()


def test_backend_env_cpu_forces_cpu(monkeypatch):
    monkeypatch.setenv(gpu_core.BACKEND_ENV, "cpu")
    assert gpu_core.resolve_backend() == "cpu"
    out = gpu_core.tensor_core(*_synthetic()[:2], backend="cpu")
    assert out["backend"] == "cpu" and out["device"] == "cpu"


def test_backend_gpu_fallback_fail_closed(monkeypatch):
    """显式 gpu + cupy 不可用（模拟）=降级 CPU 且出声（degrade 台账非空，禁静默）。"""
    monkeypatch.setattr(gpu_core, "HAS_GPU", False)
    assert gpu_core.resolve_backend("gpu") == "cpu"
    assert gpu_core.degrade_log(), "降级未出声（禁静默降级）"


def test_backend_env_invalid_raises(monkeypatch):
    monkeypatch.setenv(gpu_core.BACKEND_ENV, "tpu")
    with pytest.raises(ValueError):
        gpu_core.resolve_backend()


# ——— 7. FP64 红线（dtype 收口）———


def test_fp64_dtype_enforced():
    w_df, px_df, masks = _synthetic()
    out = gpu_core.tensor_core(
        w_df.to_numpy(dtype=np.float32), px_df.to_numpy(dtype=np.float32), gate_masks=masks, backend="cpu"
    )
    assert out["gross"].dtype == np.float64
    assert out["turnover"].dtype == np.float64
    for net in out["nets"].values():
        assert net.dtype == np.float64


def test_output_shape_and_backend_label():
    w_df, px_df, masks = _synthetic()
    out = gpu_core.tensor_core(w_df, px_df, gate_masks=masks, backend="cpu")
    assert out["gross"].shape == (T,) and out["turnover"].shape == (T,)
    assert float(_c4_engine.SLIPPAGE_BP) in out["nets"]
