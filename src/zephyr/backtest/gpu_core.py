# [BLUEPRINT] MOD-BT-233 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.gpu_core
# [DOMAIN] D_BACKTEST
# [TTL] permanent
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/backtest/test_gpu_core_parity.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [ERROR_CONTRACT] 后端显式不可用->fail-closed 降级 CPU 并记 degraded（禁静默）；backend 取值非法->ValueError；
#   输入含非有限值不特殊处理（与引擎同域：NaN=fail-open 语义由调用方/掩码承担）
# [DEPENDENCIES] numpy; cupy(可选,缺省无); pandas(仅入参鸭子类型); zephyr.shared.utils.time_utils(now_utc)
# [CONSUMERS] 尚无生产消费方（st-gpu-conv-20260928 P0 落地件，加性快路径，引擎公共 API 零改动；
#   预定消费方=factory_grid_executor/exam_cost_gate 后续接线，见 docs/_working/gpu_rewrite/rewrite_architecture_three_tiers.md §二）
# [STARTUP] manual
# [MATURITY] trial
# [INVARIANTS] FP64 红线绝对： scoring 路径全程 float64，禁 float32/TF32/FP16（cupy asarray 保 dtype，
#   调用方传入非 float64 一律 astype(float64) 收口）;
#   单一代码路径：CPU(numpy)/GPU(cupy) 走同一 xp 抽象函数体，语义一分叉即违宪（get_array_module 模式的显式变体）;
#   CPU 路径与 scripts/backtest/translated/_c4_engine.py 的 _backtest_core+_net_line 逐位一致
#   （ffill/pct_change/gate 1e-12 判定/sum skipna/cost 标量式同序同精度；parity test 逐位对拍钉住）;
#   串行闸循环（apply_fillability_gate 的逐日 prev 依赖）保留原形态——普查 L2-a 判定"不建议改"（收益 1.3%、风险>收益）;
#   成本常量=镜像 _c4_engine.py:52-54 冻结土规（COMMISSION_BP=2.5/STAMP_BP=10.0/SLIPPAGE_BP=5.0），真源在引擎，parity test 钉住漂移;
#   显式 gpu 后端 + cupy/CUDA 不可用 = 降级 CPU 且记 degraded 出声（rewrite_architecture_three_tiers.md §二回退路径，禁静默）;
#   指数对齐/reindex 等索引语义留在 CPU pandas 侧（本件只吃已对齐的等形数组，禁在本件内做索引重排）;
#   判定面（三门/DSR/单调性）永不移入本件（治理面与算力面分离，rewrite_architecture_three_tiers.md §〇）
"""GPU/CPU 双后端回测张量核——考试引擎热路径的 CuPy 薄核（P0）。

针对对象（真源=docs/_working/gpu_rewrite/hotspot_census.md §一/§二 +
rewrite_architecture_three_tiers.md §二 L2）：scripts/backtest/translated/_c4_engine.py
的 _backtest_core 张量面（ffill→pct_change→可成交性闸→gross/turnover）+ _net_line 多档
标量成本线。L1 去重（commit 62898892ed）落地后，单 pass 剩余算力面=张量数学
（普查实测掩码面 74-78% 已被向量化+缓存消解），即 L2 设计钉定的 GPU 靶。

设计要点：
  - 加性快路径：不改引擎任何公共 API；本件是独立薄核，接线由后续批次完成。
  - 后端开关：环境变量 ZEPHYR_COMPUTE_BACKEND=gpu|cpu|auto（缺省 auto=cupy+CUDA 可用则 gpu 否则 cpu）。
  - 单一代码路径：全函数体只写一份，xp（numpy|cupy）由后端决定——cupy.get_array_module
    模式的显式变体（后端是会话级决策，不是逐数组派生）。
  - FP64 红线：所有数组 float64 收口，禁 float32/TF32/FP16（宪法硬规则 10 同族纪律）。
  - CPU 逐位等价：gate_limits=False 时与引擎 _backtest_core+_net_line 逐位一致
    （parity test 断言 array_equal）；gate_limits=True 且注入合成掩码时同样逐位一致
    （掩码原料 CH 查询留在引擎侧，本件不碰 CH——CH 停机夜测试全合成数据）。
# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/gpu_core.yaml
"""

from __future__ import annotations

import logging
import os
from types import ModuleType  # xp 双后端模块注解（numpy|cupy module 对象）
from typing import Any, Final, Sequence

import numpy as np

# xp 数组语义别名（numpy|cupy 无共同基类可注解；签名面禁裸 Any=GATE-ANY-ABUSE，
# 语义经别名表达：真约束=FP64 红线由 _as_f64_2d 运行时收口，非类型面）
XPArray = Any

from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

BACKEND_ENV: Final = "ZEPHYR_COMPUTE_BACKEND"

# 冻结土规成本常量——真源=scripts/backtest/translated/_c4_engine.py:52-54（镜像件，
# parity test 与引擎输出逐位对拍钉住；改引擎不改此处=parity 红灯）
COMMISSION_BP: Final = 2.5
STAMP_BP: Final = 10.0
SLIPPAGE_BP: Final = 5.0

# 闸判定容差——真源=_c4_engine.py apply_fillability_gate 内联 1e-12（逐位复刻）
_GATE_EPS: Final = 1e-12

# import 守卫：cupy 在= HAS_GPU True（并轻探 CUDA runtime 确认可用，防"装了但驱动缺"）；
# 不在= HAS_GPU False，一切调用走 numpy 路径（CPU fallback 与 GPU 无关地可用）。
# warning 隔离：cupy import 会发 "CUDA path could not be detected" UserWarning（提示性，
# 装有 ctk 头后 runtime 仍可用）——pytest 的 warnings 管理可将其升级为异常炸掉探测
# （2026-09-28 实测 HAS_GPU 假阴根因），故探测自带 catch_warnings 隔离，不信环境告警策略。
try:  # pragma: no cover - 分支取决于装机环境
    import warnings as _warnings

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        import cupy as _cp

    _cp.cuda.runtime.runtimeGetVersion()
    HAS_GPU = True
    _GPU_IMPORT_ERROR: str | None = None
    _CUDA_RUNTIME_VERSION: int | None = int(_cp.cuda.runtime.runtimeGetVersion())
except Exception as _exc:  # noqa: BLE001 — 任何导入/初始化失败同态处理（缺包/缺驱动/缺 DLL）
    _cp = None  # type: ignore[assignment]
    HAS_GPU = False
    _GPU_IMPORT_ERROR = f"{type(_exc).__name__}: {_exc}"
    _CUDA_RUNTIME_VERSION = None

# fail-closed 降级台账（显式 gpu 请求但不可用时追加；禁静默降级——档案三栈 §二回退路径）
_DEGRADE_LOG: list[dict[str, Any]] = []

_VALID_BACKENDS: Final = ("gpu", "cpu", "auto")


def _record_degrade(reason: str) -> None:
    """降级出声：记台账 + logger.warning（禁静默——rewrite_architecture_three_tiers.md §二）。"""
    entry = {"ts": now_utc().isoformat(), "reason": reason}
    _DEGRADE_LOG.append(entry)
    logger.warning("gpu_core 降级 CPU（fail-closed 出声）: %s", reason)


def degrade_log() -> tuple[dict[str, Any], ...]:
    """本进程内降级事件台账（只读视图；测试与运维自省用）。"""
    return tuple(_DEGRADE_LOG)


def resolve_backend(requested: str | None = None) -> str:
    """解析计算后端。

    优先级：显式入参 > 环境变量 ZEPHYR_COMPUTE_BACKEND > "auto"。
    gpu=须 cupy+CUDA 可用（不可用则 fail-closed 降级 cpu 并记台账）；cpu=恒 CPU；auto=可用即 gpu。
    """
    req = (requested if requested is not None else os.environ.get(BACKEND_ENV, "auto")).strip().lower()
    if req not in _VALID_BACKENDS:
        raise ValueError(f"backend 须为 {'|'.join(_VALID_BACKENDS)}，得到 {req!r}（env {BACKEND_ENV}）")
    if req == "cpu":
        return "cpu"
    if HAS_GPU:
        return "gpu"
    if req == "gpu":
        _record_degrade(f"显式 gpu 请求但 cupy/CUDA 不可用: {_GPU_IMPORT_ERROR}")
    return "cpu"


def gpu_available() -> bool:
    """cupy+CUDA 是否真实可用（import 成功且 runtime 可探）。"""
    return HAS_GPU


def device_info() -> dict[str, Any]:
    """设备自描述（smoke/日志用；无 GPU 时给降级原因，不抛）。"""
    if not HAS_GPU:
        return {"has_gpu": False, "import_error": _GPU_IMPORT_ERROR}
    try:
        props = _cp.cuda.runtime.getDeviceProperties(0)  # type: ignore[union-attr]
        name = props.get("name", b"") if isinstance(props, dict) else b""
        name_s = name.decode() if isinstance(name, bytes) else str(name)
        return {
            "has_gpu": True,
            "cuda_runtime": _CUDA_RUNTIME_VERSION,
            "device_name": name_s,
            "cupy_version": getattr(_cp, "__version__", "unknown"),
        }
    except Exception as exc:  # noqa: BLE001 — 自描述面禁抛
        return {"has_gpu": True, "probe_error": f"{type(exc).__name__}: {exc}"}


def _as_f64_2d(a: XPArray, xp: ModuleType) -> XPArray:
    """任意 2D 数组类入参（ndarray/DataFrame）→ xp float64 矩阵（FP64 红线收口点）。"""
    if hasattr(a, "to_numpy"):  # pandas DataFrame/Series——引擎侧调用形态
        a = a.to_numpy(dtype=np.float64)
    arr = xp.asarray(a)
    if arr.dtype != xp.float64:
        arr = arr.astype(xp.float64)
    if arr.ndim != 2:
        raise ValueError(f"gpu_core 须 2D 等形数组 (T,S)，得到 ndim={arr.ndim}")
    return arr


def _as_bool_2d(a: XPArray | None, shape: tuple[int, int], xp: ModuleType) -> XPArray:
    """掩码入参→xp bool 矩阵；None=fail-open 全 False（与引擎掩码缺失语义同态）。"""
    if a is None:
        return xp.zeros(shape, dtype=xp.bool_)
    if hasattr(a, "to_numpy"):
        a = a.to_numpy()
    arr = xp.asarray(a)
    if arr.dtype != xp.bool_:
        arr = arr.astype(xp.bool_)
    return arr


def _ffill_axis0(xp: ModuleType, a: XPArray) -> XPArray:
    """沿时间轴（axis 0）逐列前向填充——pandas .ffill() 的 xp 等价（含首行 NaN 保留）。

    实现：有效行号取 max 累积 → 花式索引回填。首列无前值处 idx=0 引用首行——
    首行为 NaN 时回填值=NaN（与 pandas ffill 的 leading-NaN 语义一致）。
    """
    mask = xp.isnan(a)
    if not bool(mask.any()):
        return a
    idx = xp.where(~mask, xp.arange(a.shape[0])[:, None], 0)
    # cupy 未实现 maximum.accumulate 原语（NotImplementedError，2026-09-28 真机实测）：
    # 此处是行号（int）沿 axis0 的 running-max=前向回填，T≤1e4 且非热点主体——
    # cupy 分支走 host 等价回环（整数行号逐位恒等，parity test 钉住）；实现分叉、语义零分叉。
    if _cp is not None and xp is not np:
        import numpy as _host_np

        idx = xp.asarray(_host_np.maximum.accumulate(xp.asnumpy(idx), axis=0))
    else:
        idx = xp.maximum.accumulate(idx, axis=0)
    cols = xp.arange(a.shape[1])[None, :]
    return a[idx, cols]


def _shift1_axis0(xp: ModuleType, a: XPArray) -> XPArray:
    """沿 axis 0 下移一行，首行 NaN——pandas .shift(1) 的 xp 等价。"""
    return xp.concatenate([xp.full((1,) + a.shape[1:], xp.nan, dtype=a.dtype), a[:-1]], axis=0)


def _apply_gate_serial(xp: ModuleType, w: XPArray, su: XPArray, sd: XPArray) -> XPArray:
    """涨跌停可成交性闸的串行循环——逐位复刻 _c4_engine.apply_fillability_gate 行循环。

    逐日 prev 依赖（T 串行）：封板日禁开新仓/禁出逃，|Δ|≤1e-12 视为无交易。
    普查 L2-a 判定"不建议向量化"（收益 1.3%、串行依赖、风险>收益）——原形态保留，
    GPU 下为 T 次小 kernel（T≈1.7k，可接受）。
    """
    t, s = w.shape
    out = xp.empty_like(w)
    prev = xp.zeros(s, dtype=w.dtype)
    for i in range(t):
        target = w[i]
        cur = xp.where(
            ((target > prev + _GATE_EPS) & su[i]) | ((target < prev - _GATE_EPS) & sd[i]),
            prev,
            target,
        )
        out[i] = cur
        prev = cur
    return out


def _net_from_gt(xp: ModuleType, gross: XPArray, turnover: XPArray, slippage_bp: float) -> XPArray:
    """冻结土规成本线——逐位复刻 _c4_engine._net_line（同序同精度标量式）。"""
    cost = turnover * (COMMISSION_BP * 2 + STAMP_BP + float(slippage_bp) * 2) / 10000.0
    return gross - cost


def _to_numpy(a: XPArray) -> np.ndarray:
    """xp 数组→numpy（GPU 侧收口回传；CPU 侧零拷贝透传）。"""
    if _cp is not None and isinstance(a, _cp.ndarray):  # type: ignore[attr-defined]
        return _cp.asnumpy(a)
    return np.asarray(a)


def tensor_core(
    weights: XPArray,
    px_close: XPArray,
    gate_masks: tuple[Any, Any] | None = None,
    slippage_bps: Sequence[float] = (SLIPPAGE_BP,),
    gate_limits: bool = True,
    backend: str | None = None,
) -> dict[str, Any]:
    """考试引擎张量核的 GPU/CPU 双后端实现（_backtest_core+_net_line 的 xp 薄核）。

    入参（须已按引擎 reindex 语义对齐为等形 (T,S)——索引语义留在 pandas 侧，本件不碰）：
      weights: 目标权重宽表（T 交易日 × S 标的；NaN=待 ffill→首行段补 0，引擎同式）；
      px_close: hfq 收盘价宽表（同形；NaN=待 ffill）；
      gate_masks: (sealed_up, sealed_down) bool (T,S)——掩码原料（CH raw close+stk_limit）
        由调用方注入（引擎 _load_seal_masks 产出 .to_numpy()）；None=fail-open 全 False
        （与引擎 CH 不可得分支同态）；gate_limits=False 时掩码被忽略（旧行为对照通道）；
      slippage_bps: 档位标量列表（None 档语义由调用方传 SLIPPAGE_BP 常量，引擎同式）；
      backend: "gpu"|"cpu"|None（None=按 resolve_backend 解析 env/auto）。

    返回 dict：backend / device / gross(T,) / turnover(T,)（一侧换手）/
      nets {bp: net(T,)}——全部 numpy float64（GPU 侧已回传收口）。

    精度与等价：CPU 后端与引擎 _backtest_core+_net_line 逐位一致（parity 钉住）；
    GPU 后端 FP64（3090 1/64 吞吐换 1e-12 相对差内一致），禁 float32/TF32。
    """
    be = resolve_backend(backend)
    xp: Any
    if be == "gpu":
        xp = _cp  # type: ignore[assignment]
        device = device_info().get("device_name", "cuda:0")
    else:
        xp = np
        device = "cpu"

    w = _as_f64_2d(weights, xp)
    px = _as_f64_2d(px_close, xp)
    if w.shape != px.shape:
        raise ValueError(f"weights/px_close 须等形，得到 {w.shape} vs {px.shape}")

    # ——— _backtest_core 张量面（xp 单路径，语义逐位镜像 _c4_engine.py:476-488）———
    closes = _ffill_axis0(xp, px)  # px.reindex(...).ffill()
    rets = closes / _shift1_axis0(xp, closes) - 1.0  # pct_change()（ffill 后首段 NaN 语义同态）
    w_ff = _ffill_axis0(xp, w)
    w_ff = xp.where(xp.isnan(w_ff), 0.0, w_ff)  # .fillna(0.0)
    if gate_limits:
        su = _as_bool_2d(gate_masks[0] if gate_masks else None, w.shape, xp)
        sd = _as_bool_2d(gate_masks[1] if gate_masks else None, w.shape, xp)
        w_g = _apply_gate_serial(xp, w_ff, su, sd)
    else:
        w_g = w_ff  # gate_limits=False=旧行为（掩码不参与）
    w_prev = _shift1_axis0(xp, w_g)
    gross = xp.nansum(w_prev * rets, axis=1)  # (w.shift(1)*rets).sum(axis=1).fillna(0)（skipna 同态）
    turnover = xp.nansum(xp.abs(w_g - w_prev), axis=1) / 2.0

    # ——— _net_line 多档标量成本线（逐位镜像 _c4_engine.py:491-497）———
    nets = {float(bp): _to_numpy(_net_from_gt(xp, gross, turnover, bp)) for bp in slippage_bps}
    return {
        "backend": be,
        "device": device,
        "gross": _to_numpy(gross),
        "turnover": _to_numpy(turnover),
        "nets": nets,
    }
