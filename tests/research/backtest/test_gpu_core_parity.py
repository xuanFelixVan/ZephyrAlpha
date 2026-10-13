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

_REPO = Path(__file__).resolve().parents[3]
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


# ——— 8. B2 设备驻留（st-gpux3-20261012）：载体直通＋hold_days 两面逐位等 ———
# 本节的**唯一断言对象**="驻留是纯数据搬运，不改任何数值"。它必须能红：
# 9.1 的失焦对照故意把 `> 0` 写成 `>= 0`、把 NaN 留成 NaN，用例集须翻出差异，
#     否则本节只是一条恒绿装饰（在册教训：判通过的尺须先证明能红）。

_HOLD_FRAMES: tuple[str, ...] = (
    "top_n_equal_nan",  # 最贴生产：每行 top_n 个 1/top_n，其余 NaN
    "all_nan_rows",  # 全 NaN 行（pandas skipna→0.0 不 >0）
    "all_zero_rows",  # 和恰为 0 的边界
    "denormal_positive",  # 下溢量级正项
    "signed_weights",  # 带符号权重（抽掉"非负⇒求和序无关"这条便利前提仍须同解）
)
# 不设 inf 用例：权重是 ≤cap 的分数，inf 在生产形状里不可产生，而它触发的 RuntimeWarning
# 落在 gross/turnover 路径（inf-inf），与本节要断言的 hold_days 无关——用本仓
# filterwarnings=error 下会红的用例去测另一个位＝测的不是想测的东西（禁造第二病）。


def _hold_frame_sets() -> dict[str, pd.DataFrame]:
    idx = pd.date_range("2020-01-01", periods=T, freq="B")
    cols = pd.Index([f"{600000 + i:06d}" for i in range(S)])
    rng = np.random.default_rng(20261012)
    base = np.full((T, S), np.nan)
    for i in range(T):
        base[i, rng.choice(S, size=max(1, S // 5), replace=False)] = 1.0 / max(1, S // 5)
    out: dict[str, np.ndarray] = {"top_n_equal_nan": base}
    m = base.copy()
    m[::7] = np.nan
    out["all_nan_rows"] = m
    m = base.copy()
    m[::5] = 0.0
    out["all_zero_rows"] = m
    out["denormal_positive"] = np.where(rng.random((T, S)) < 0.3, rng.random((T, S)) * 5e-320, np.nan)
    out["signed_weights"] = np.where(rng.random((T, S)) < 0.5, rng.normal(0.0, 1.0, (T, S)), np.nan)
    return {k: pd.DataFrame(v, index=idx, columns=cols) for k, v in out.items()}


def _px_for(frame: pd.DataFrame) -> pd.DataFrame:
    """同形价格面板（本测试只取 hold_days 一路，闸关，值不参与该位）。"""
    mat = np.where(np.isnan(frame.to_numpy()), np.nan, 100.0)
    return pd.DataFrame(mat, index=frame.index, columns=frame.columns)


@pytest.mark.parametrize(
    "be",
    ["cpu", pytest.param("gpu", marks=[pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")])],
)
@pytest.mark.parametrize("name", _HOLD_FRAMES)
def test_hold_days_device_matches_host_formula(name: str, be: str):
    """核内行归约 vs 引擎主机原式——同一取整位上逐格等（stats 落 manifest 的就是这个值）。"""
    frame = _hold_frame_sets()[name]
    host = _c4_engine._host_hold_days(frame)
    out = gpu_core.tensor_core(frame, _px_for(frame), gate_limits=False, backend=be, want_hold_days=True)
    assert round(float(out["hold_days_pct"]), 3) == round(host, 3), (name, be, host, out["hold_days_pct"])


def test_hold_days_ruler_has_teeth():
    """失焦对照：两条"错式"必须在本用例集上翻红，否则第 8 节是恒绿装饰。"""
    sets = _hold_frame_sets()
    ge_variant = {"all_zero_rows", "all_nan_rows"}  # >=0 会把"无持仓行"读成持仓
    nan_keep = {"all_nan_rows"}  # NaN 不置零会把全 NaN 行读成持仓
    seen_ge, seen_nan = set(), set()
    for name, frame in sets.items():
        vals = frame.to_numpy()
        host = _c4_engine._host_hold_days(frame)
        v_ge = float((frame.sum(axis=1) >= 0).mean())
        v_nan = float(((vals**0).sum(axis=1) > 0).mean())  # NaN**0=1 ⇒ 全 NaN 行被计入
        if round(v_ge, 3) != round(host, 3):
            seen_ge.add(name)
        if round(v_nan, 3) != round(host, 3):
            seen_nan.add(name)
    assert seen_ge & ge_variant, f">=0 错式未翻红＝比较器无判别力: {seen_ge}"
    assert seen_nan & nan_keep, f"NaN 不置零错式未翻红＝比较器无判别力: {seen_nan}"


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")
def test_device_panel_unwraps_to_same_buffer_and_keeps_labels():
    """载体直通=零拷贝（§十二·B① 的在册结论从此由测试钉住，不再靠口头）。"""
    cp = gpu_core.device_module()
    assert cp is not None
    arr = cp.zeros((T, S), dtype=cp.float64)
    idx, cols = pd.date_range("2020-01-01", periods=T), pd.Index([f"{i:06d}" for i in range(S)])
    panel = gpu_core.DevicePanel(arr, idx, cols)
    assert gpu_core._as_f64_2d(panel, cp).data.ptr == arr.data.ptr
    assert panel.shape == (T, S) and panel.size == T * S
    host = panel.to_host_frame()
    assert host.index.equals(idx) and host.columns.equals(cols)


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")
def test_backtest_core_gpu_carrier_path_matches_host_frame_bitwise():
    """B2 主断言的单元形态：同数值经载体进 vs 经宽表进 ⇒ (gross, turnover) 与 hold_days 逐位等。

    价格/掩码常驻在两次调用间会命中缓存，正是"第二次调用不该改变任何数值"这条要钉的东西。
    """
    w_df, px_df, masks = _synthetic()
    orig = _c4_engine._load_seal_masks
    _c4_engine._load_seal_masks = lambda i, c: (masks[0], masks[1])  # type: ignore[method-assign]
    try:
        cp = gpu_core.device_module()
        panel = gpu_core.DevicePanel(cp.asarray(w_df.to_numpy(dtype=np.float64)), w_df.index, w_df.columns)
        g_host, t_host = _c4_engine._backtest_core_gpu(w_df, px_df, True, "gpu")
        h_host = _c4_engine._host_hold_days(w_df)
        _c4_engine._LAST_GPU_HOLD_DAYS["hold_days_pct"] = None
        g_dev, t_dev = _c4_engine._backtest_core_gpu(panel, px_df, True, "gpu")
        h_dev = _c4_engine._LAST_GPU_HOLD_DAYS["hold_days_pct"]
        assert np.array_equal(g_host.to_numpy(), g_dev.to_numpy())
        assert np.array_equal(t_host.to_numpy(), t_dev.to_numpy())
        assert round(float(h_dev), 3) == round(h_host, 3)
        st = _c4_engine._stats_from_net(g_dev, t_dev, panel, hold_days_pct=h_dev)
        assert st["hold_days_pct"] == round(h_host, 3)
        with pytest.raises(ValueError, match="hold_days_pct"):
            _c4_engine._stats_from_net(g_dev, t_dev, panel, hold_days_pct=None)
    finally:
        _c4_engine._load_seal_masks = orig  # type: ignore[method-assign]


# ——— 9. 刀一 设备侧 ffill 扫描核 ＋ 刀二 批级 rets 共享（st-gpux4-20261013）———
# 钉的对象是"两把刀都不得改数值"：刀一换的是 _ffill_axis0 的 cupy 分支实现（host 回环→设备核），
# 刀二换的是 rets 的求值次数（逐格→批级一次）。两者按 §一 表都属 L1 级＝**逐位等、容差 0**，
# 所以这里的判据全部用 uint64 位视图（`==` 会把 -0.0/0.0 与 NaN 判成相等，不够严）。


def _bits(a: np.ndarray) -> np.ndarray:
    """float64 → uint64 位视图（逐位等的比较器；先把设备件收回主机再取位）。"""
    import cupy as _cp_local  # 仅在本文件已 skipif 到 cupy 可用的用例里调用

    if isinstance(a, _cp_local.ndarray):
        a = _cp_local.asnumpy(a)
    a = np.ascontiguousarray(a, dtype=np.float64)
    return a.view(np.uint64)


def _ffill_numpy_reference(host: np.ndarray) -> np.ndarray:
    """改动前 cupy 分支那条算式的主机同形：where(~mask, arange, 0)→maximum.accumulate→gather。

    这里**故意不 import 旧实现**（旧分支已被替换，盘上不存在），而是按算式逐字重写一遍当参照；
    跨版本的字节级参照由 `.runtime/tmp/st-gpux4-20261013/g4_ffill_verify.py` 用
    `git show dev:` 装载第二模块来给（两把尺指向不同对象：本函数证"语义没跑偏"，那针证"字节没变过"）。
    """
    t, s = host.shape
    idx = np.where(~np.isnan(host), np.arange(t)[:, None], 0)
    idx = np.maximum.accumulate(idx, axis=0)
    return host[idx, np.arange(s)[None, :]]


def _ffill_families(tt: int = 64, ss: int = 24) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(20261013)
    base = 100.0 + np.cumsum(rng.normal(0, 1.0, size=(tt, ss)), axis=0)
    halt = base.copy()
    halt[12:19, 3] = np.nan
    halt[30:44, 11] = np.nan
    lead = base.copy()
    lead[:9, :] = np.nan
    allnan = base.copy()
    allnan[:, 5] = np.nan
    sparse = np.full((tt, ss), np.nan)
    for i in range(0, tt, 4):
        sparse[i, rng.choice(ss, size=3, replace=False)] = rng.random(3) / 3.0
    edge = base.copy()
    edge[4, 2], edge[6, 7], edge[8, 9] = np.inf, -0.0, 5e-324
    edge[20, :4] = np.nan
    return {
        "halt_runs": halt,
        "leading_nan": lead,
        "all_nan_col": allnan,
        "topn_sparse": sparse,
        "bitwise_edge": edge,
        "no_nan": base.copy(),
    }


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")
@pytest.mark.parametrize("family", list(_ffill_families().keys()))
def test_ffill_device_kernel_bitwise_three_way(family: str):
    """刀一主钉：设备核 vs numpy 算式参照 vs pandas .ffill() 三向逐位等（含短路面）。"""
    import cupy as cp

    host = _ffill_families()[family]
    ref_np = _ffill_numpy_reference(host)
    ref_pd = pd.DataFrame(host).ffill().to_numpy(dtype=np.float64)
    dev = gpu_core._ffill_axis0(cp, cp.asarray(host))
    if family == "no_nan":
        assert dev is not None and np.array_equal(_bits(dev), _bits(host))
        assert ref_np.shape == host.shape
        return
    assert np.array_equal(_bits(dev), _bits(ref_np)), f"{family}: 设备核≠numpy 算式参照"
    assert np.array_equal(_bits(dev), _bits(ref_pd)), f"{family}: 设备核≠pandas .ffill()"


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")
def test_ffill_ruler_has_teeth():
    """失焦对照：两条"错式"必须与正解不等，且**两条错式彼此也不等**（同一把尺的两个参照若互等，
    说明它们量的不是同一件事——在册"两把参照必须互不相同"同族自检）。"""
    import cupy as cp

    host = _ffill_families()["leading_nan"]
    good = gpu_core._ffill_axis0(cp, cp.asarray(host))
    bad_fill0 = cp.where(cp.isnan(good), 0.0, good)  # 错式一：无前值补 0（洗掉 leading NaN）
    idx = np.minimum.accumulate(
        np.where(~np.isnan(host), np.arange(host.shape[0])[:, None], host.shape[0] - 1), axis=0
    )  # 错式二：方向写反＝bfill
    bad_bfill = cp.asarray(host)[cp.asarray(idx), cp.arange(host.shape[1])[None, :]]
    assert not np.array_equal(_bits(good), _bits(bad_fill0)), "补 0 错式未被识出＝尺对 leading NaN 无牙"
    assert not np.array_equal(_bits(good), _bits(bad_bfill)), "bfill 错式未被识出＝尺对填充方向无牙"
    assert not np.array_equal(_bits(bad_fill0), _bits(bad_bfill)), "两条错式互等＝参照构造退化"


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")
def test_ffill_rawkernel_rejects_non_float64():
    """dtype 闸：RawKernel 按 const double* 解读显存，float32 直调必须是 ValueError 不是乱码。"""
    import cupy as cp

    a = cp.ones((8, 4), dtype=cp.float32)
    a[2, 1] = cp.nan
    with pytest.raises(ValueError, match="float64"):
        gpu_core._ffill_rawkernel(a)


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")
def test_pre_rets_shared_matches_per_cell_bitwise():
    """刀二主钉：`pre_rets=None`（逐格现算）vs 传入批级共享件 ⇒ 五档 nets 逐位等。

    共享件的产出式＝`gpu_core.prep_rets_device`，与核内侧同一个 `px_rets` 函数体，
    所以这条钉的是"接线没接错"，而数值等价本身由构造给出。
    """
    w_df, px_df, masks = _synthetic()
    cp = gpu_core.device_module()
    shared = gpu_core.prep_rets_device(px_df, cp)
    kw = dict(
        gate_masks=masks,
        slippage_bps=(0.0, 5.0, 10.0, 20.0, 40.0),
        gate_limits=True,
        backend="gpu",
        want_hold_days=True,
    )
    r0 = gpu_core.tensor_core(w_df, px_df, **kw)
    r1 = gpu_core.tensor_core(w_df, px_df, pre_rets=shared, **kw)
    assert np.array_equal(_bits(r0["gross"]), _bits(r1["gross"]))
    assert np.array_equal(_bits(r0["turnover"]), _bits(r1["turnover"]))
    for bp, n0 in r0["nets"].items():
        assert np.array_equal(_bits(n0), _bits(r1["nets"][bp])), f"{bp}bp 档 nets 不等"
    assert r0["hold_days_pct"] == r1["hold_days_pct"]


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")
def test_pre_rets_teeth_wrong_panel_differs():
    """失焦对照：供入**另一张**价格面板的 rets，gross 必须变（否则上一条全等可能是空等）。"""
    w_df, px_df, masks = _synthetic()
    cp = gpu_core.device_module()
    other = px_df.copy()
    other.iloc[40:, 3] = other.iloc[39, 3]  # 造一条真不同的价格路径
    assert not other.equals(px_df)
    kw = dict(gate_masks=masks, slippage_bps=(0.0,), gate_limits=True, backend="gpu", want_hold_days=False)
    good = gpu_core.tensor_core(w_df, px_df, **kw)
    bad = gpu_core.tensor_core(w_df, px_df, pre_rets=gpu_core.prep_rets_device(other, cp), **kw)
    assert not np.array_equal(_bits(good["gross"]), _bits(bad["gross"]))


@pytest.mark.skipif(not gpu_core.gpu_available(), reason="cupy/CUDA 不可用")
def test_pre_rets_cache_hits_and_pins_host_identity():
    """缓存账：第二次必须 hit（不 hit 时"逐位等"什么都没证）；同内容不同宿主对象必须 put 而非 hit。

    键纪律钉的是"引用随值 pin 住"那一半——`_DEV_PANEL_CACHE` 的 id() 键不持引用（在册脏命中风险面），
    本缓存若退化成那种形，这条会红。
    """
    cp = gpu_core.device_module()
    px_df = _synthetic()[1]
    saved = dict(_c4_engine._PRE_RETS_STATS)
    try:
        _c4_engine._PRE_RETS.clear()
        _c4_engine._PRE_RETS_STATS.update({"rets_hit": 0, "rets_put": 0})
        first = _c4_engine._pre_rets_cache(px_df, cp)
        second = _c4_engine._pre_rets_cache(px_df, cp)
        assert _c4_engine._PRE_RETS_STATS["rets_put"] == 1
        assert _c4_engine._PRE_RETS_STATS["rets_hit"] == 1
        assert first.data.ptr == second.data.ptr  # 同一设备缓冲＝真复用，不是又算一遍
        twin = px_df.copy()
        _c4_engine._PRE_RETS.clear()
        _c4_engine._PRE_RETS_STATS.update({"rets_hit": 0, "rets_put": 0})
        _c4_engine._pre_rets_cache(px_df, cp)
        third = _c4_engine._pre_rets_cache(twin, cp)
        assert _c4_engine._PRE_RETS_STATS["rets_hit"] == 0, "同内容不同宿主被判 hit＝身份判定失守"
        assert _c4_engine._PRE_RETS_STATS["rets_put"] == 2
        assert np.array_equal(_bits(third), _bits(first)), "同内容重建件与原件不同位＝产出式随宿主身份漂移"
        assert _c4_engine._pre_rets_cache(px_df, None) is None, "xp=None 必须回 None（禁静默走设备路）"
    finally:
        _c4_engine._PRE_RETS.clear()
        _c4_engine._PRE_RETS_STATS.clear()
        _c4_engine._PRE_RETS_STATS.update(saved)
