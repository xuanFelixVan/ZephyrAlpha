# [BLUEPRINT] MOD-BT-233 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.gpu_core
# [DOMAIN] D_BACKTEST
# [TTL] permanent
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/backtest/test_gpu_core_parity.py; tests/backtest/test_l2_gpu_landing.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [ERROR_CONTRACT] 后端显式不可用->fail-closed 降级 CPU 并记 degraded（禁静默）；backend 取值非法->ValueError；
#   RawKernel 编译/执行异常直抛（调用方 fail-closed 整波重跑 CPU，禁半成品）；
#   输入含非有限值不特殊处理（与引擎同域：NaN=fail-open 语义由调用方/掩码承担）
# [DEPENDENCIES] numpy; cupy(可选,缺省无); cupyx.scatter_add(随 cupy,可选); pandas(仅入参鸭子类型); zephyr.shared.utils.time_utils(now_utc)
# [CONSUMERS] scripts/backtest/translated/_c4_engine.py（P1 接线/L2-B 守卫披露）；
#   scripts/backtest/factory_grid_executor.py（L2-C --engine 三态透传+manifest backend/degrade 列）；
#   scripts/backtest/l2_bench_probe.py（L2 终验探针转正件）；
#   详见 docs/_working/gpu_rewrite/rewrite_architecture_three_tiers.md §二
# [STARTUP] manual
# [MATURITY] trial
# [INVARIANTS] FP64 红线绝对： scoring 路径全程 float64，禁 float32/TF32/FP16（cupy asarray 保 dtype，
#   调用方传入非 float64 一律 astype(float64) 收口）;
#   单一代码路径：CPU(numpy)/GPU(cupy) 走同一 xp 抽象函数体，语义一分叉即违宪（get_array_module 模式的显式变体）;
#   CPU 路径与 scripts/backtest/translated/_c4_engine.py 的 _backtest_core+_net_line 逐位一致
#   （ffill/pct_change/gate 1e-12 判定/sum skipna/cost 标量式同序同精度；parity test 逐位对拍钉住）;
#   串行闸循环（apply_fillability_gate 的逐日 prev 依赖）：CPU 路径保留原形态（CPU 逐位锚，
#   parity test 钉住）；GPU 路径 L2-A 起走 RawKernel 融合扫描 fillability_gate_scan
#   （一 thread 一列、时间轴寄存器内推进，T 次小 kernel→1 次，杀 kernel-launch 税；
#   源=MOD-BT-232 god 区 gpu_panel_core 收编——L2-E 双核归一，MOD-BT-232 superseded，
#   语义与 CPU 串行循环逐式同构，同输入逐位一致由 test_l2_gpu_landing 钉住）;
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
  - L2 落地（st-fullscore-20260930 重建批）：A=RawKernel 融合闸（GPU 分支，杀 launch 税）；
    D=eval_prefix_equal_gpu（prefix 求值核：zscore+equal 合成+截面平均档 rank，
    Kahan/分块 Neumaier 补偿归约树序差，cupyx.scatter_add 做并列组计数——
    工厂 combine_cache 前缀热路径的 GPU 快通道；IC/正交等长尾合成模式留 CPU）。
# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/gpu_core.yaml
"""

from __future__ import annotations

import logging
import os
import threading
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

# NVML 归因读数的一次性装载态（ctypes 懒加载；failed 后不再重试，避免每次心跳重探）
_NVML_LIB: Any = None
_NVML_HANDLE: Any = None
_NVML_TS: int = 0
_NVML_STATE: str = "init"
_NVML_ERROR: str | None = None


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


def nvml_process_util(pid: int | None = None) -> dict[str, Any]:
    """本进程 GPU 归因读数（验收尺治本件，st-gpux-20261011）。

    为何要它：nvidia-smi 的 utilization.gpu 是**设备级**指标，本机实测零算力负载时桌面图形
    就能把它推到 8-57%（12 点采样），而夜间批跑时它只有 9.75%——单看设备曲线分不清
    "引擎在喂卡"与"IDE 在画窗口"，拿来当 ≥70% 的验收尺必假绿。本函数走 NVML 逐进程
    接口取 smUtil，并区分计算上下文（CPU-only 进程根本不出现在计算进程表里）。

    依赖纪律：ctypes 直调驱动自带的 nvml.dll——**不新增依赖**（pynvml/nvidia-ml-py 全仓
    零安装，见其 [DEPENDENCIES] 面）。NVML 不可用/结构不合=available=False 出声降级，
    禁把"读不到"报成"没占用"（ch-query-fails-soft 同族坑）。

    结构体口径按本机驱动 610.88 实测：(pid:uint32, pad, lastSeenTimeStamp:uint64,
    f0,f1,f2,f3:uint32)，f0=本进程 SM 忙碌百分比（自测：CPU-only 进程不入表、GPU 忙时
    f0 随负载升至 ~77，空闲回落）；四字段语义无公开头文件可核，故只消费 f0 且带
    sane 范围守卫（0-100 之外一律判不可用），禁据此推断编码/解码利用率。
    """
    global _NVML_LIB, _NVML_HANDLE, _NVML_TS, _NVML_STATE, _NVML_ERROR
    if _NVML_STATE == "off":
        return {"available": False, "reason": "nvml_disabled"}
    if _NVML_STATE == "failed":
        return {"available": False, "reason": _NVML_ERROR or "nvml_unavailable"}
    import ctypes

    if _NVML_LIB is None:
        try:
            _NVML_LIB = ctypes.CDLL("nvml.dll")
            if _NVML_LIB.nvmlInit_v2() != 0:
                raise OSError("nvmlInit_v2 != 0")
            h = ctypes.c_void_p()
            if _NVML_LIB.nvmlDeviceGetHandleByIndex_v2(0, ctypes.byref(h)) != 0:
                raise OSError("GetHandleByIndex != 0")
            _NVML_HANDLE = h
            _NVML_STATE = "ok"
        except Exception as exc:  # noqa: BLE001 — 采集面缺失不得影响出分
            _NVML_STATE = "failed"
            _NVML_ERROR = f"{type(exc).__name__}: {exc}"
            logger.warning("gpu_core.nvml 不可用，归因读数降级: %s", _NVML_ERROR)
            return {"available": False, "error": _NVML_ERROR}

    class _Sample(ctypes.Structure):
        _fields_ = [
            ("pid", ctypes.c_uint),
            ("ts", ctypes.c_ulonglong),
            ("f0", ctypes.c_uint),
            ("f1", ctypes.c_uint),
            ("f2", ctypes.c_uint),
            ("f3", ctypes.c_uint),
        ]

    class _Util(ctypes.Structure):
        _fields_ = [("gpu", ctypes.c_uint), ("mem", ctypes.c_uint)]

    n = ctypes.c_uint(0)
    ts = ctypes.c_ulonglong(_NVML_TS)
    fn = _NVML_LIB.nvmlDeviceGetProcessUtilization
    fn.restype = ctypes.c_int
    fn(_NVML_HANDLE, None, ctypes.byref(n), ctypes.byref(ts))
    arr = (_Sample * max(n.value, 1))()
    if fn(_NVML_HANDLE, arr, ctypes.byref(n), ctypes.byref(ts)) != 0:
        return {"available": False, "reason": "GetProcessUtilization rc!=0"}
    target = pid if pid is not None else os.getpid()
    self_sm = None
    compute_pids = []
    for s in arr[: n.value]:
        compute_pids.append(int(s.pid))
        if s.pid == target and 0 <= s.f0 <= 100:
            self_sm = int(s.f0)
        if s.ts > _NVML_TS:
            _NVML_TS = int(s.ts)
    dev = _Util()
    _NVML_LIB.nvmlDeviceGetUtilizationRates(_NVML_HANDLE, ctypes.byref(dev))
    return {
        "available": True,
        "pid": int(target),
        "sm_util_pct": self_sm,  # None=本进程当前无计算上下文（≠0，必须区分）
        "in_compute_table": int(target) in compute_pids,
        "compute_pid_count": len(compute_pids),
        "device_util_pct": int(dev.gpu),  # 设备级，含图形噪声，只作对照不作验收
        "device_mem_util_pct": int(dev.mem),
    }


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
    CPU 路径锚实现（逐位基准）；GPU 路径 L2-A 起走 _apply_gate_rawkernel（语义同构）。
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


# ——— L2-A RawKernel 融合闸扫描（GPU 分支专用；源=MOD-BT-232 gpu_panel_core 收编，
#      L2-E 双核归一定案：本件是唯一核，MOD-BT-232 superseded）———
_GATE_KERNEL_SRC = r"""
extern "C" __global__
void fillability_gate_scan(const double* W, const unsigned char* SU, const unsigned char* SD,
                           double* OUT, const long long T, const long long S)
{
    // 一 thread 一列：时间轴 T 在寄存器内串行推进（prev 依赖天然串行），
    // 同 step 各 thread 连续读 W[t*S + j] -> 合并访存；S=5.6k 列仅 ~22 个 block。
    long long j = (long long)blockIdx.x * (long long)blockDim.x + (long long)threadIdx.x;
    if (j >= S) return;
    double prev = 0.0;
    const double eps = 1e-12;
    for (long long t = 0; t < T; ++t) {
        const long long k = t * S + j;
        const double target = W[k];
        const bool su = SU[k] != 0;
        const bool sd = SD[k] != 0;
        // 与 _apply_gate_serial/_c4_engine.apply_fillability_gate 逐式同构：
        // cur = where((target>prev+eps && SU) | (target<prev-eps && SD), prev, target)
        const bool stuck = ((target > prev + eps) && su) || ((target < prev - eps) && sd);
        const double cur = stuck ? prev : target;
        OUT[k] = cur;
        prev = cur;
    }
}
"""

_GATE_KERNEL: Any = None  # 惰性编译缓存（RawKernel；进程内一次）
_GATE_KERNEL_LOCK = threading.Lock()


def _apply_gate_rawkernel(w: XPArray, su: XPArray, sd: XPArray) -> XPArray:
    """GPU 融合封板闸扫描（L2-A）——T 次小 kernel 收敛为 1 次 launch，杀 kernel-launch 税。

    输入 w/su/sd 须同形 (T,S)（w float64、su/sd bool），C-contiguous 由本函数收口；
    输出闸后权重 (T,S) float64，与 _apply_gate_serial 同输入逐位一致
    （双精度同式串行推进，test_l2_gpu_landing 钉 array_equal）。
    编译/执行异常直抛（禁吞）——调用方 fail-closed 重跑 CPU。
    """
    global _GATE_KERNEL
    t, s = w.shape
    w_c = _cp.ascontiguousarray(w)
    su_c = _cp.ascontiguousarray(su.astype(_cp.uint8))
    sd_c = _cp.ascontiguousarray(sd.astype(_cp.uint8))
    out = _cp.empty_like(w_c)
    with _GATE_KERNEL_LOCK:
        if _GATE_KERNEL is None:
            _GATE_KERNEL = _cp.RawKernel(_GATE_KERNEL_SRC, "fillability_gate_scan")
    threads = 256
    blocks = (s + threads - 1) // threads
    _GATE_KERNEL(
        (blocks,),
        (threads,),
        (w_c, su_c, sd_c, out, np.int64(t), np.int64(s)),
    )
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
        if be == "gpu":
            w_g = _apply_gate_rawkernel(w_ff, su, sd)  # L2-A：1 次 launch 融合扫描
        else:
            w_g = _apply_gate_serial(xp, w_ff, su, sd)  # CPU 逐位锚（原形态）
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


# ——— L2-D：prefix 求值核（工厂 combine_cache 前缀热路径 GPU 快通道）———
# 语义镜像 scripts/backtest/factory_grid_executor.py 的 A1 zscore→A2 equal→rank 三步：
#   zscore  = (x - mean)/std（pandas ddof=1；sd==0→NaN；全 NaN 行→NaN）
#   equal   = 多因子逐格 nanmean（pd.concat().groupby(level=0).mean() 同态）
#   rank    = 逐日截面降序平均档（pandas rank(axis=1, ascending=False) 同态；NaN→NaN）
# 精度纪律：行内归约走分块 Neumaier 补偿（块内树和+块间补偿项，消除 GPU 归约树序差，
# parity≤1e-12 红线实测富余到 1e-16 量级）；rank 并列组计数走 cupyx.scatter_add
# （numpy 路径等价 np.add.at——实现分叉、语义零分叉，同 _ffill_axis0 host 回环纪律）。

_NEUMAIER_BLOCK: Final = 512  # 分块宽度（块数=ceil(S/512)≈11 次 host 循环 @S=5.4k，可忽略）


def _neumaier_nansum_axis1(xp: ModuleType, a: XPArray) -> XPArray:
    """沿 axis1 的 NaN 跳过补偿和（pandas sum skipna 同态）——块内树和+块间 Neumaier。"""
    t, s = a.shape
    finite = ~xp.isnan(a)
    safe = xp.where(finite, a, 0.0)
    pad = (-s) % _NEUMAIER_BLOCK
    if pad:
        safe = xp.concatenate([safe, xp.zeros((t, pad), dtype=a.dtype)], axis=1)
        finite = xp.concatenate([finite, xp.zeros((t, pad), dtype=xp.bool_)], axis=1)
    blocks = safe.reshape(t, -1, _NEUMAIER_BLOCK)
    part = blocks.sum(axis=2)  # 块内树和（float64，块宽 512 内树序差 ≤1e-16 相对）
    total = xp.zeros(t, dtype=xp.float64)
    comp = xp.zeros(t, dtype=xp.float64)
    for i in range(part.shape[1]):  # 块间 Neumaier 补偿（块数≈S/512，host 循环可忽略）
        cs = part[:, i]
        t2 = total + cs
        comp = xp.where(xp.abs(total) >= xp.abs(cs), comp + (total - t2 + cs), comp + (cs - t2 + total))
        total = t2
    return total + comp


def _zscore_rows(xp: ModuleType, a: XPArray) -> XPArray:
    """逐行 zscore（ddof=1）——镜像 factory _normalize("zscore")：sd==0→NaN，全 NaN→NaN，
    单观测行（cnt=1，ddof=1 无定义）→NaN（pandas std 同态）；零除全走 where 守卫（禁告警）。"""
    cnt = (~xp.isnan(a)).sum(axis=1)
    mu = _neumaier_nansum_axis1(xp, a) / xp.where(cnt > 0, cnt, 1)
    mu = xp.where(cnt > 0, mu, xp.nan)  # 全 NaN 行→NaN（pandas mean 同态）
    centered = xp.where(xp.isnan(a), 0.0, a - mu[:, None])  # NaN 格不参与方差
    sq = _neumaier_nansum_axis1(xp, centered * centered)
    denom = cnt - 1
    sd = xp.where(denom > 0, xp.sqrt(sq / xp.where(denom > 0, denom, 1)), xp.nan)  # cnt≤1→NaN（ddof=1）
    sd_safe = xp.where(sd == 0.0, xp.nan, sd)  # sd==0→NaN（factory replace(0,nan) 同态）
    return (a - mu[:, None]) / sd_safe[:, None]


def _equal_combine(xp: ModuleType, arrs: list[XPArray]) -> XPArray:
    """多因子逐格 nanmean 等权合成——镜像 factory _combine("equal")（groupby.mean skipna 同态）。"""
    total = xp.zeros_like(arrs[0])
    for a in arrs:  # F 因子数小（≤8），host 循环可忽略；逐项加法即逐项 Neumaier（F 一阶）
        total = total + xp.where(xp.isnan(a), 0.0, a)
    cnt = xp.zeros_like(arrs[0])
    for a in arrs:
        cnt = cnt + (~xp.isnan(a)).astype(xp.float64)
    return total / xp.where(cnt > 0, cnt, 1) * xp.where(cnt > 0, 1.0, xp.nan)  # 全 NaN 格→NaN


def _rank_desc_average(xp: ModuleType, a: XPArray) -> XPArray:
    """逐行降序平均档 rank（pandas rank(axis=1, ascending=False) 同态；NaN→NaN）。

    实现：稳定降序排序→并列组界→组计数与组起始位（scatter_add 一炮双计）→
    平均档=起始位+(组大小-1)/2→散射回原位。rank 值全为小整数/半整数（float64 精确
    表示），与 pandas 逐位一致（并列判定=精确相等比较，无浮点容差）。
    """
    t, s = a.shape
    nan = xp.isnan(a)
    fill = xp.where(nan, -xp.inf, a)  # NaN 沉底（pandas rank NaN 不计位同态；-inf 实值属病理输入）
    order = xp.argsort(-fill, axis=1, kind="stable")
    sorted_vals = xp.take_along_axis(fill, order, axis=1)
    is_start = xp.ones_like(sorted_vals, dtype=xp.bool_)
    is_start[:, 1:] = sorted_vals[:, 1:] != sorted_vals[:, :-1]
    gid = xp.cumsum(is_start, axis=1) - 1  # 并列组 id（按排序位）
    n_groups = int(gid[:, -1].max()) + 1
    rows = xp.arange(t)[:, None]
    g_start = xp.zeros((t, n_groups), dtype=xp.float64)  # 组起始位（1-based；组内仅首元素非 0）
    g_size = xp.zeros((t, n_groups), dtype=xp.float64)  # 组大小
    pos1 = xp.broadcast_to(xp.arange(1, s + 1, dtype=xp.float64), (t, s))
    start_vals = xp.where(is_start, pos1, 0.0)
    if xp is np:
        np.add.at(g_start, (rows, gid), start_vals)
        np.add.at(g_size, (rows, gid), 1.0)
    else:
        import cupyx

        cupyx.scatter_add(g_start, (rows, gid), start_vals)
        cupyx.scatter_add(g_size, (rows, gid), 1.0)
    start_at = xp.take_along_axis(g_start, gid, axis=1)
    size_at = xp.take_along_axis(g_size, gid, axis=1)
    ranks_sorted = start_at + (size_at - 1.0) / 2.0  # 平均档（整数/半整数，float64 精确）
    ranks = xp.empty_like(ranks_sorted)
    xp.put_along_axis(ranks, order, ranks_sorted, axis=1)
    return xp.where(nan, xp.nan, ranks)  # NaN 回填（pandas rank NaN→NaN 同态）


def eval_prefix_equal_gpu(
    factors: Sequence[XPArray],
    backend: str | None = None,
) -> dict[str, Any]:
    """prefix 求值 GPU 核（L2-D）：A1 zscore → A2 equal 合成 → 截面降序平均档 rank。

    工厂网格 combine_cache 前缀热路径（(G,A1,A2) 相同格点共享 combined+rank）的 GPU
    快通道；IC 加权/正交/lasso 等长尾合成模式留 CPU pandas 侧（本件只吃等形数组，
    索引语义禁入）。全合成验收见 docs/_working/fullscore_night/06_gpu_compute/
    04_L2_landing_benchmark.md（all_a 实测冷启动 eval 提速见该表；<1.5x 即停手如实报）。

    入参 factors: ≥1 个 (T,S) 等形因子宽表（ndarray/DataFrame）；返回 dict：
      backend / combined (T,S) float64 / rank (T,S) float64——numpy 收口回传。
    parity：与 pandas 面三步同式（Kahan/Neumaier 补偿+精确 rank）≤1e-12（FP64 红线）。
    """
    be = resolve_backend(backend)
    xp: Any = _cp if be == "gpu" else np
    arrs = [_as_f64_2d(f, xp) for f in factors]
    if not arrs:
        raise ValueError("factors 须含 ≥1 个因子面板")
    shape = arrs[0].shape
    for i, a in enumerate(arrs):
        if a.shape != shape:
            raise ValueError(f"factors 须等形，第 {i} 个 {a.shape} vs 首个 {shape}")
    normed = [_zscore_rows(xp, a) for a in arrs]
    combined = _equal_combine(xp, normed)
    rank = _rank_desc_average(xp, combined)
    return {"backend": be, "combined": _to_numpy(combined), "rank": _to_numpy(rank)}


# ---------------------------------------------------------------------------
# eval 面 GPU 核（st-gpux-20261011，T0 实测定靶）
#
# 靶位凭据（全部实测，非推演）：今晚 38,956 格仪表 = eval 82.2% CPU-秒；其中
#   hit 路径（combine 命中，96.6% 格）60.4%、miss 路径 39.6%；宇宙面 all_a_ex_st
#   独占 74.2%。hit 路径 cProfile 逐函数 = numpy.copy 0.086s/格（24%）＋
#   pandas dtype 派发面（is_bool_dtype 20,873 次/格）——算术占比小、机械占比大，
#   正是设备侧一次成型、pandas 逐算子重做的形态差。
#   原语单价（T=975×S=5217，FP64 CuPy vs CPU pandas）：rank(pct) 0.690→0.011（66x）、
#   equal 合成 0.385→0.003（145x）、_sizing 链 0.992→0.041（24x）。
#
# 镜像对象（逐式对照，行号=scripts/backtest/factory_grid_executor.py@dev）：
#   _normalize:470 / _demean_by_group:442 / _regress_out:457 / _combine:511 /
#   _sizing:622 / _norm_rows:683 / _apply_freq_trigger:705（periodic 支）/
#   _apply_cap_and_lambda:689（lambda_0 支）
#
# CPU 交接点（本件覆盖面的边界，越界=调用方回原 pandas 路并出声，禁半成品混算）：
#   1. drift_band 逐日 prev 串行依赖（:724-728）——实测逐日 python 循环搬上卡
#      =0.214s vs CPU 0.016s（慢 14 倍），融合前禁上卡；
#   2. lambda>0 的 ewm(alpha) 时间轴递推（:699）——同族 IIR，同上；
#   3. sklearn Lasso（:595，selection=random 确定性系 CPU 实现属性）与 pc1 的
#      eigh 特征序/符号约定（:605）；
#   4. IC 权重的 rolling(60)/ewm 与归一（:544-552）——对象是 (T,F) 小矩阵（F≤8），
#      非 (T,S) 全面板，上卡无收益且引入第二实现面，故本件只交回 ic_all (T,F)；
#   5. 一切索引/列标签语义（本文件头 INVARIANTS 既有条款）。
# ---------------------------------------------------------------------------


def _rank_rows(xp: ModuleType, a: XPArray, *, ascending: bool = True, pct: bool = False) -> XPArray:
    """逐行平均档 rank（pandas DataFrame.rank(axis=1, method='average') 同态；NaN→NaN）。

    并列组计数与 _rank_desc_average 同机（scatter_add 一炮双计），只是 NaN 沉底方向随
    ascending 翻转：升序填 +inf、降序填 -inf，使 NaN 恒排在有效值之后（pandas 不计位）。
    rank 值=整数/半整数，float64 精确表示⇒与 pandas 逐位可比（无浮点容差面）。
    """
    t, s = a.shape
    nan = xp.isnan(a)
    fill = xp.where(nan, (xp.inf if ascending else -xp.inf), a)
    key = fill if ascending else -fill
    order = xp.argsort(key, axis=1, kind="stable")
    sorted_vals = xp.take_along_axis(fill, order, axis=1)
    is_start = xp.ones_like(sorted_vals, dtype=xp.bool_)
    is_start[:, 1:] = sorted_vals[:, 1:] != sorted_vals[:, :-1]
    gid = xp.cumsum(is_start, axis=1) - 1
    n_groups = int(gid[:, -1].max()) + 1
    rows = xp.arange(t)[:, None]
    g_start = xp.zeros((t, n_groups), dtype=xp.float64)
    g_size = xp.zeros((t, n_groups), dtype=xp.float64)
    pos1 = xp.broadcast_to(xp.arange(1, s + 1, dtype=xp.float64), (t, s))
    start_vals = xp.where(is_start, pos1, 0.0)
    if xp is np:
        np.add.at(g_start, (rows, gid), start_vals)
        np.add.at(g_size, (rows, gid), 1.0)
    else:
        import cupyx

        cupyx.scatter_add(g_start, (rows, gid), start_vals)
        cupyx.scatter_add(g_size, (rows, gid), 1.0)
    start_at = xp.take_along_axis(g_start, gid, axis=1)
    size_at = xp.take_along_axis(g_size, gid, axis=1)
    ranks_sorted = start_at + (size_at - 1.0) / 2.0
    out = xp.empty_like(ranks_sorted)
    xp.put_along_axis(out, order, ranks_sorted, axis=1)
    out = xp.where(nan, xp.nan, out)
    if pct:
        cnt = (~nan).sum(axis=1, dtype=xp.float64)
        out = out / xp.where(cnt > 0, cnt, xp.nan)[:, None]
    return out


def _row_mean(xp: ModuleType, a: XPArray) -> XPArray:
    """行内 skipna 均值（pandas mean(axis=1) 同态；全 NaN 行→NaN）。"""
    cnt = (~xp.isnan(a)).sum(axis=1, dtype=xp.float64)
    mu = _neumaier_nansum_axis1(xp, a) / xp.where(cnt > 0, cnt, 1.0)
    return xp.where(cnt > 0, mu, xp.nan)


def _row_std(xp: ModuleType, a: XPArray) -> XPArray:
    """行内 skipna 标准差 ddof=1（pandas std(axis=1) 同态；cnt≤1→NaN）。"""
    cnt = (~xp.isnan(a)).sum(axis=1, dtype=xp.float64)
    mu = _neumaier_nansum_axis1(xp, a) / xp.where(cnt > 0, cnt, 1.0)
    mu = xp.where(cnt > 0, mu, xp.nan)
    centered = xp.where(xp.isnan(a), 0.0, a - mu[:, None])
    sq = _neumaier_nansum_axis1(xp, centered * centered)
    denom = cnt - 1
    return xp.where(denom > 0, xp.sqrt(sq / xp.where(denom > 0, denom, 1.0)), xp.nan)


def _group_mean_rows(xp: ModuleType, a: XPArray, codes: XPArray, n_groups: int) -> tuple[XPArray, XPArray]:
    """逐日按列分组 (T,G) 均值与计数（skipna）——镜像 _demean_by_group:452 的
    `f.T.groupby(grp[valid]).mean().T`（组均值矩阵，列标签分组在本件外先编码成 codes）。"""
    t, s = a.shape
    codes = xp.asarray(codes)
    if codes.dtype != xp.int64:
        codes = codes.astype(xp.int64)
    finite = ~xp.isnan(a)
    safe = xp.where(finite, a, 0.0)
    tot = xp.zeros((t, n_groups), dtype=xp.float64)
    cnt = xp.zeros((t, n_groups), dtype=xp.float64)
    rows = xp.arange(t)[:, None]
    if xp is np:
        np.add.at(tot, (rows, codes), safe)
        np.add.at(cnt, (rows, codes), xp.where(finite, 1.0, 0.0))
    else:
        import cupyx

        cupyx.scatter_add(tot, (rows, codes), safe)
        cupyx.scatter_add(cnt, (rows, codes), xp.where(finite, 1.0, 0.0))
    mu = xp.where(cnt > 0, tot / xp.where(cnt > 0, cnt, 1.0), xp.nan)
    return mu, cnt


def normalize_rows(
    xp: ModuleType,
    a: XPArray,
    mode: str,
    *,
    codes: XPArray | None = None,
    n_groups: int = 0,
    ctrl: XPArray | None = None,
) -> XPArray:
    """A1 标准化的 xp 面（与 _normalize:470 逐式同构；degraded 判定属调用方模式派发，不在本件）。

    codes = 每列的组编码（无标签列由调用方标 -1，本件置 NaN=与 :453-454 的
    reindex(columns=原列) 后无组列→NaN 同态的 fail-closed）；ctrl = 控制变量面板（size 族）。
    """
    if mode == "raw":
        return a
    if mode == "rank":
        return _rank_rows(xp, a, ascending=True, pct=True)
    if mode == "zscore":
        return _zscore_rows(xp, a)
    if mode == "industry_neutral":
        if codes is None or n_groups <= 0:
            raise ValueError("industry_neutral 需 codes/n_groups（缺锚=调用方走降级支，禁本件猜）")
        return _demean_rows(xp, a, codes, n_groups)
    if mode == "size_neutral":
        if ctrl is None:
            raise ValueError("size_neutral 需 ctrl（log_mv）面板")
        return _regress_out_rows(xp, a, ctrl)
    if mode == "industsize_neutral":
        raise ValueError(
            "industsize_neutral 禁走本函数：factory _normalize:502-506 把**全市场列**的 log_mv "
            "送去组内去均值，之后才由 _regress_out reindex 到宇宙列；在本件里按已切片的宇宙列 "
            "做去均值会改组均值口径（st-gpux-20261011 的 8 格真实对拍实测出 sharpe 4.9e-2 漂移）。"
            "改走 industsize_rows，ctrl 由调用方在全市场列集上去均值后切列传入"
        )
    raise ValueError(f"未知 A1 mode 上卡面: {mode!r}（调用方须先判模式再决定是否走本件）")


def industsize_rows(xp: ModuleType, a: XPArray, codes: XPArray, n_groups: int, ctrl_dm: XPArray) -> XPArray:
    """FWL 两支残差：行业组内 demean 的因子，对行业组内 demean 的控制变量取逐日截面 OLS 残差。

    与 factory `_normalize("industsize_neutral")`（:502-506）逐式同构。ctrl_dm **必须**是调用方
    在市值面板的全部列上完成去均值、再切到宇宙列的结果——factory 的去均值作用面是全市场列，
    先切宇宙列再去均值=组均值口径变了（不是浮点差，是另一套数）。镜像核本身无从判断这件事，
    故本件把它写成显式入参并在 normalize_rows 里拒收该模式。
    """
    if codes is None or ctrl_dm is None or n_groups <= 0:
        raise ValueError("industsize_neutral 需 codes+n_groups+ctrl_dm（缺锚=调用方走降级支，禁本件猜）")
    return _regress_out_rows(xp, _demean_rows(xp, a, codes, n_groups), ctrl_dm)


def _demean_rows(xp: ModuleType, a: XPArray, codes: XPArray, n_groups: int) -> XPArray:
    """列分组去均值；codes<0=无组标签列→整列置 NaN（factory :453-454 的
    reindex(columns=原列) 后无组列失配同态，fail-closed 禁泄露行业效应）。

    无组列必须在 scatter 之前剔除——负下标进 scatter_add 是未定义行为，
    进 numpy 取模索引则静默取到最后一组（假对拍形态）。
    """
    valid = codes >= 0
    pos = xp.nonzero(valid)[0]
    out = xp.full(a.shape, xp.nan, dtype=xp.float64)
    if int(pos.size) == 0:
        return out
    av = a[:, pos]
    cv = xp.asarray(codes)[pos]
    mu, _ = _group_mean_rows(xp, av, cv, n_groups)
    out[:, pos] = av - mu[:, cv]
    return out


def _regress_out_rows(xp: ModuleType, f: XPArray, ctrl: XPArray) -> XPArray:
    """逐日一元 OLS 残差——镜像 _regress_out:457（配对 NaN 掩码三步同序）。"""
    m = (~xp.isnan(f)) & (~xp.isnan(ctrl))
    fw = xp.where(m, f, xp.nan)
    xw = xp.where(m, ctrl, xp.nan)
    f0 = fw - _row_mean(xp, fw)[:, None]
    x0 = xw - _row_mean(xp, xw)[:, None]
    f0 = xp.where(m, f0, xp.nan)
    x0 = xp.where(m, x0, xp.nan)
    var = _row_mean(xp, x0 * x0)
    var = xp.where(var == 0.0, xp.nan, var)
    beta = _row_mean(xp, f0 * x0) / var
    out = f0 - x0 * beta[:, None]
    return xp.where(m, out, xp.nan)


def ic_pair_rows(xp: ModuleType, nf: XPArray, fwd_ranked: XPArray) -> XPArray:
    """单因子逐日 rank-IC（镜像 _combine:534-541 循环体；fwd_ranked 由调用方算一次）。

    返回 (T,) 的 IC 序列——滚动/半衰/归一在 (T,F) 面上，由调用方在 CPU pandas 侧做
    （见本节头 CPU 交接点 4）。
    """
    xr = _rank_rows(xp, nf, ascending=True)
    m = (~xp.isnan(xr)) & (~xp.isnan(fwd_ranked))
    x = xp.where(m, xr, xp.nan)
    y = xp.where(m, fwd_ranked, xp.nan)
    xm = x - _row_mean(xp, x)[:, None]
    ym = y - _row_mean(xp, y)[:, None]
    xm = xp.where(m, xm, xp.nan)
    ym = xp.where(m, ym, xp.nan)
    cov = _row_mean(xp, xm * ym)
    sd = _row_std(xp, x) * _row_std(xp, y)
    sd = xp.where(sd == 0.0, xp.nan, sd)
    return xp.nan_to_num(cov / sd, nan=0.0)


def weighted_combine(xp: ModuleType, normed: list[XPArray], wcols: XPArray) -> XPArray:
    """按日权重合成 combined=Σ_j w[:,j]·nf_j（镜像 _combine:553-556 的逐因子累加，
    含 fillna(0.0) 语义：nf 的 NaN 以 0 参与，与 to_numpy()+fillna 同态）。"""
    acc = xp.zeros_like(normed[0])
    for j, nf in enumerate(normed):
        acc = acc + wcols[:, j][:, None] * xp.nan_to_num(nf, nan=0.0)
    return acc


def orth_equal_rows(xp: ModuleType, normed: list[XPArray]) -> XPArray:
    """逐日截面 Gram-Schmidt 正交分量等权——镜像 _combine:558-568（顺序依赖=f 声明序）。"""
    basis: list[XPArray] = []
    for a in normed:
        r = xp.nan_to_num(a, nan=0.0).copy()
        for b in basis:
            coef = (r * b).sum(axis=1, keepdims=True)
            r = r - coef * b
        nrm = xp.sqrt((r * r).sum(axis=1, keepdims=True))
        basis.append(r / (nrm + 1e-12))
    acc = xp.zeros_like(normed[0])
    for b in basis:
        acc = acc + b
    return acc / float(len(basis))


def norm_rows_div(xp: ModuleType, w: XPArray) -> XPArray:
    """行和归一＋零和行→NaN→填 0——镜像 _norm_rows:683（skipna sum 用补偿和）。"""
    rs = _neumaier_nansum_axis1(xp, w)
    rs = xp.where(rs == 0.0, xp.nan, rs)
    return xp.nan_to_num(w / rs[:, None], nan=0.0)


def sizing_weights(
    xp: ModuleType,
    scores: XPArray,
    rank_desc: XPArray,
    top_n: int,
    mode: str,
    *,
    vol20: XPArray | None = None,
    mkt_cap: XPArray | None = None,
    r60_mean: XPArray | None = None,
    r60_var: XPArray | None = None,
) -> XPArray:
    """B 选股 + C 定尺寸——镜像 _sizing:622（rank_pre 已由调用方从缓存取，:646 的跳过支同态）。"""
    mask = (rank_desc <= top_n) & (~xp.isnan(rank_desc))
    if mode in ("kelly_025", "kelly_050"):
        if r60_mean is None or r60_var is None:
            raise ValueError("kelly sizing 需 rets60 两板（调用方批级装载）")
        fraction = 0.25 if mode == "kelly_025" else 0.5
        dv = xp.where(r60_var > 1e-12, r60_var, xp.nan)
        kelly = fraction * (r60_mean / dv)
        kelly = xp.clip(kelly, 0.0, None)
        return mask.astype(xp.float64) * xp.nan_to_num(kelly, nan=0.0)
    base = xp.where(mask, 1.0, xp.nan)
    if mode == "equal_weight":
        return norm_rows_div(xp, base)
    if mode in ("inv_vol", "risk_parity"):
        if vol20 is None:
            raise ValueError("inv_vol/risk_parity 需 vol20 面板")
        iv = 1.0 / xp.where(vol20 > 0, vol20, xp.nan)
        return norm_rows_div(xp, base * iv)
    if mode == "mkt_cap":
        if mkt_cap is None:
            raise ValueError("mkt_cap sizing 需市值宽表")
        return norm_rows_div(xp, base * mkt_cap)
    if mode == "signal_strength":
        s = xp.where(mask, scores, xp.nan)
        # 全 NaN 行：pandas min(axis=1)=NaN 且不出声；nanmin 会对同形切片发 RuntimeWarning，
        # 本仓 pytest filterwarnings=error 会把它升级成失败。fmin.reduce 在 cupy 未实现
        # （实测 NotImplementedError: `cupy_fmin.reduce` is not supported yet）→ 一律用
        # +inf 占位再 min：无有效值行=+inf，随后换成 NaN，与 pandas skipna 同解且两端都支持。
        row_min_big = xp.where(mask, scores, xp.inf).min(axis=1)  # 无有效值行=+inf（不是 NaN）
        scalar = row_min_big.min()  # +inf 天然被有限值压过
        scalar = xp.where(xp.isinf(scalar), xp.nan, scalar)  # 全表无有效值→NaN（pandas 同态）
        return norm_rows_div(xp, base * xp.abs(s - scalar + 1e-9))
    raise ValueError(f"未知 C_sizing 取值上卡面: {mode!r}")


def periodic_hold_rows(xp: ModuleType, w: XPArray, step: int) -> XPArray:
    """非调仓日沿用旧权重——镜像 _apply_freq_trigger:719 的 iloc[::step].reindex(ffill)。

    索引单调且第 0 行必为调仓日（factory 既有前提），故行 gather 下标
    (i//step)*step 与 pandas ffill 逐位同解；step=1 由调用方短路（原码同）。
    """
    t = w.shape[0]
    idx = (xp.arange(t) // step) * step
    return w[idx]


def cap_clip(xp: ModuleType, w: XPArray, cap: float) -> XPArray:
    """单票上限硬 clip——镜像 _apply_cap_and_lambda:696（renorm 反禁，超额留现金）。"""
    return xp.clip(w, None, cap)


def eval_cell_gpu(
    combined: XPArray,
    rank_desc: XPArray,
    *,
    top_n: int,
    sizing_mode: str,
    freq_step: int,
    trigger: str,
    cap: float,
    lam: float,
    vol20: XPArray | None = None,
    mkt_cap: XPArray | None = None,
    r60_mean: XPArray | None = None,
    r60_var: XPArray | None = None,
    backend: str | None = None,
) -> dict[str, Any]:
    """单格权重链 GPU/CPU 双后端核（T0 实测=hit 路径 60.4% 的 eval 秒数落在此面）。

    入参须为已对齐的等形 (T,S) float64 数组：combined=合成截面、rank_desc=其降序平均档
    （二者正是 combine_cache 现有缓存物，命中格零 H2D）。返回 dict：
      backend / weights (T,S) numpy / host_continue (bool)。
    host_continue=True 表示该格含卡上未覆盖的串行步（drift_band 或 lambda>0），
    weights 只算到"可上卡的最后一步"，其余交回调用方原 pandas 函数——**交接出声，
    禁本件自造近似**（本节头 CPU 交接点 1/2）。
    """
    be = resolve_backend(backend)
    xp: Any = _cp if be == "gpu" else np
    w = sizing_weights(
        xp,
        _as_f64_2d(combined, xp),
        _as_f64_2d(rank_desc, xp),
        top_n,
        sizing_mode,
        vol20=vol20,
        mkt_cap=mkt_cap,
        r60_mean=r60_mean,
        r60_var=r60_var,
    )
    host_continue = False
    if trigger == "drift_band":
        # 串行依赖交接：本件到此为止，trigger→cap 全序交回 factory 原函数。
        # 禁在此提前 cap——factory 次序是 _sizing→_apply_freq_trigger→_apply_cap_and_lambda，
        # 先 cap 会让 drift_band 的行比较看到被削过的权重=换序即换数（次序敏感面）。
        host_continue = True
    else:
        if freq_step > 1:
            w = periodic_hold_rows(xp, w, freq_step)
        w = cap_clip(xp, w, cap)
        if lam > 0.0:
            host_continue = True  # ewm 递推+归一交回 pandas（clip 幂等，重跑无害）
    return {"backend": be, "weights": _to_numpy(w), "host_continue": host_continue}
