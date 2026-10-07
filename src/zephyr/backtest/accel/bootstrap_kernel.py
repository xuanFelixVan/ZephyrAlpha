# [BLUEPRINT] MOD-BT-237 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.accel.bootstrap_kernel
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; cupy(可选，仅显式 backend="gpu" 受守卫 import)
# [CONSUMERS] zephyr.backtest.core.walk_forward(WRC 内循环)；
#   zephyr.backtest.regime_validation.e2_stationary_bootstrap(E2 内循环)；
#   zephyr.factor.analysis.correlation_block_bootstrap(G07 rep 循环)；
#   scripts/backtest/fexam/bootstrap_gpu/kernel.py(薄 re-export，保旧 import 路径)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] FP64 红线：入口 _as_f64 收口，禁 float32/TF32/FP16;
#   auto 恒 CPU：不 import cupy、不采纳他模块已加载的 cupy（静默上 GPU=禁区），
#   仅显式 backend="gpu" 允许受守卫 import，不可用=fail-closed 降级 CPU 并记 degrade_log 出声;
#   单一代码路径：CPU(numpy)/GPU(cupy) 同一函数体，xp 由后端决定，语义零分叉;
#   判定面不入核：只产出 bootstrap 统计量矩阵，p_value/CI/prob/阈值判定留调用方;
#   对拍契约：索引生成器与三原实现索引过程分布同构但 RNG 不同源，逐位对拍必走同索引注入（<=1e-9）;
#   输入校验面（NaN/长度/样本量业务断言）留调用方原函数，核只做形状/dtype 防御
# [MODIFY-GUARD] none
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] backend 非法->ValueError; 形状/dtype 不符->ValueError;
#   显式 gpu 但 cupy/CUDA 不可用->fail-closed 降级 CPU 并记 degrade_log（禁静默）
# [TESTS] tests/backtest/test_bootstrap_kernel_wiring.py
# [TTL] permanent
# -*- coding: utf-8 -*-
"""bootstrap 统一族 xp 纯函数核——三热循环合一（MOD-BT-237）。

三核合一（向量化加速核），逐个镜像三个串行热循环：
  - wrc_boot_tstats        <- walk_forward.whites_reality_check 内层 b 循环
  - e2_boot_sharpe_diffs   <- e2_stationary_bootstrap.bootstrap_sharpe_difference b 循环
  - corr_boot_pair_stats   <- correlation_block_bootstrap.bootstrap_correlation_ci rep 循环

设计纪律（继承 zephyr.backtest.gpu_core.resolve_backend 模式，xp 切换自实现）：
  - 后端开关：显式入参 > env ZEPHYR_BOOTSTRAP_BACKEND > auto；显式 gpu 但 cupy/CUDA
    不可用 = fail-closed 降级 CPU 并记 degrade_log 出声（禁静默）；backend 非法 = ValueError。
  - auto 恒 CPU：既不主动 import cupy，也不采纳他模块（如 zephyr.backtest.__init__
    -> gpu_core 顶层）已加载的 cupy（实测教训：采纳会让核在宿主不知情时静默上 GPU）；
    仅显式 backend="gpu" 才允许受守卫 import。
  - FP64 红线：入口 _as_f64 收口，禁 float32/TF32/FP16。
  - 单一代码路径：CPU(numpy)/GPU(cupy) 同一函数体，xp 由后端决定，语义零分叉。
  - 判定面不入核：核只产出 bootstrap 统计量矩阵（t 统计量/Sharpe 差/成对相关系数）；
    p_value、CI、prob、阈值判定（WFA 三门/DSR/PIT）由调用方按原语义聚合。
  - 对拍契约：索引生成器产出 (B,T) int64 索引矩阵，同批索引分别喂原实现与新核
    （RNG 不同源不可逐位，注入法钉住 p_value/t_stat/CI <=1e-9）。
  - 输入校验面（NaN/长度/样本量业务断言）留调用方原函数——核只做形状/dtype 防御。

索引生成器 stationary_bootstrap_index_matrix 与三个原实现的索引过程分布同构
（块长 L~Geometric(p=1/mean_block) iid、块起点 U[0,n) iid、环绕取模；E2 的逐步
"以 p 重开否则顺移"与块式过程为同一过程两种采样），但 RNG 流与原标量实现不同源
——故对拍必须走索引注入而非同种子复现。索引在宿主 numpy Generator 生成后由
xp.asarray 上传（B*T int64@2000x1600=25MB，一次传输可忽略；cupy 端原生 RNG 属后续优化）。

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/bootstrap_kernel.yaml
# A1(索引矩阵生成) --> O1((B,T) int64 索引)；A2(三核统计量) --> O2(bootstrap 统计量矩阵)
"""

from __future__ import annotations

import logging
import math
import os
from types import ModuleType
from typing import Any, Final

import numpy as np

from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

# xp 数组语义别名（numpy|cupy 无共同基类；FP64 真约束由 _as_f64 运行时收口承担）
XPArray = Any

BACKEND_ENV: Final = "ZEPHYR_BOOTSTRAP_BACKEND"
_VALID_BACKENDS: Final = ("gpu", "cpu", "auto")
_DEFAULT_CHUNK_ROWS: Final = 256  # 多元核分块宽度（控 (chunk,T,k) 中间张量内存）

_cp: Any = None  # 惰性持有；顶层绝不 import cupy
_GPU_IMPORT_ERROR: str | None = None

# fail-closed 降级台账（显式 gpu 请求但不可用时追加；禁静默）
_DEGRADE_LOG: list[dict[str, Any]] = []


def degrade_log() -> tuple[dict[str, Any], ...]:
    """本进程内降级事件台账（只读视图；测试与运维自省用）。"""
    return tuple(_DEGRADE_LOG)


def _record_degrade(reason: str) -> None:
    """降级出声：记台账 + logger.warning（禁静默）。"""
    entry = {"ts": now_utc().isoformat(), "reason": reason}
    _DEGRADE_LOG.append(entry)
    logger.warning("bootstrap_kernel 降级 CPU（fail-closed 出声）: %s", reason)


def _probe_cupy_explicit() -> bool:
    """显式 gpu 请求才可达此处：受守卫 import cupy 并探 runtime。"""
    global _cp, _GPU_IMPORT_ERROR
    if _cp is not None:
        return True
    import warnings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import cupy as mod  # noqa: F401  仅显式 gpu 路径触发
        mod.cuda.runtime.runtimeGetVersion()
        _cp = mod
        return True
    except Exception as exc:  # noqa: BLE001 — 缺包/缺驱动/缺 DLL 同态处理
        _GPU_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"
        return False


def _adopt_loaded_cupy() -> bool:
    """已废止的采纳路径（保留桩位防幽灵引用）：auto 恒 CPU，绝不采纳他模块加载的 cupy。

    实测教训：zephyr.backtest 包 __init__ 传递加载 gpu_core 会把 cupy 塞进
    sys.modules，若 auto 采纳之，核即在宿主不知情时静默上 GPU（正是禁区）。
    """
    return False


def resolve_backend(requested: str | None = None) -> str:
    """解析计算后端（gpu_core.resolve_backend 模式）。

    优先级：显式入参 > 环境变量 ZEPHYR_BOOTSTRAP_BACKEND > "auto"。
    gpu=须 cupy+CUDA 可用（不可用则 fail-closed 降级 cpu 并记台账）；
    cpu=恒 CPU；auto=恒 CPU（不 import、不采纳、不上 GPU——若要
    gpu_core 同款 auto=gpu-if-available，须以进程级显式开关为前提）。
    """
    req = (requested if requested is not None else os.environ.get(BACKEND_ENV, "auto")).strip().lower()
    if req not in _VALID_BACKENDS:
        raise ValueError(f"backend 须为 {'|'.join(_VALID_BACKENDS)}，得到 {req!r}（env {BACKEND_ENV}）")
    if req == "cpu":
        return "cpu"
    if req == "gpu":
        if _probe_cupy_explicit():
            return "gpu"
        _record_degrade(f"显式 gpu 请求但 cupy/CUDA 不可用: {_GPU_IMPORT_ERROR}")
        return "cpu"
    # auto：恒 CPU（不 import、不采纳他模块加载的 cupy）
    _adopt_loaded_cupy()  # 桩位（恒 False），保持调用面自描述
    return "cpu"


def _resolve_xp(backend: str | None) -> tuple[str, ModuleType]:
    be = resolve_backend(backend)
    return be, (_cp if be == "gpu" else np)


def _to_numpy(a: XPArray) -> np.ndarray:
    """xp 数组→numpy（GPU 侧收口回传；CPU 侧零拷贝透传）。"""
    if _cp is not None and isinstance(a, _cp.ndarray):
        return _cp.asnumpy(a)
    return np.asarray(a)


def _as_f64_1d(a: XPArray, xp: ModuleType) -> XPArray:
    """一维序列入参 → xp float64（FP64 红线收口点）。"""
    if hasattr(a, "to_numpy"):
        a = a.to_numpy(dtype=np.float64)
    arr = xp.asarray(a)
    if arr.dtype != xp.float64:
        arr = arr.astype(xp.float64)
    if arr.ndim != 1:
        raise ValueError(f"bootstrap_kernel 须 1D 序列，得到 ndim={arr.ndim}")
    return arr


def _as_f64_2d(a: XPArray, xp: ModuleType) -> XPArray:
    """2D 面板入参（ndarray/DataFrame）→ xp float64 矩阵（FP64 红线收口点）。"""
    if hasattr(a, "to_numpy"):
        a = a.to_numpy(dtype=np.float64)
    arr = xp.asarray(a)
    if arr.dtype != xp.float64:
        arr = arr.astype(xp.float64)
    if arr.ndim != 2:
        raise ValueError(f"bootstrap_kernel 面板须 2D (T,k)，得到 ndim={arr.ndim}")
    return arr


def _as_index_matrix(idx: XPArray, xp: ModuleType) -> XPArray:
    """(B,T) 索引矩阵 → xp int64（形状防御；取值域由生成器与调用方保证）。"""
    arr = xp.asarray(idx)
    if arr.dtype != xp.int64:
        arr = arr.astype(xp.int64)
    if arr.ndim != 2:
        raise ValueError(f"bootstrap_kernel 索引须 2D (B,T)，得到 ndim={arr.ndim}")
    return arr


def stationary_bootstrap_index_matrix(
    n: int,
    mean_block: int,
    n_paths: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """批量 stationary bootstrap 环绕索引矩阵（宿主 numpy，(n_paths, n) int64）。

    分布同构于三个原实现的索引过程（Politis & Romano 1994）：块长
    L~Geometric(p=1/mean_block) iid、块起点 U[0,n) iid、环绕取模；
    与 e2/corr 的标量逐步生成是同一过程，与 WRC 的逐块生成亦然。

    向量化：先按均值超采样块长列，再对每行做"新块起点"散点+cumsum 定块号，
    一步 take_along_axis 展开为索引流；尾部补样循环对 p<1 以概率
    P(Geometric 和 < n) 指数衰减，实际至多 1 轮。
    """
    n = int(n)
    n_paths = int(n_paths)
    if n < 2:
        raise ValueError(f"n 需 >=2，得到 {n}")
    if int(mean_block) < 1:
        raise ValueError(f"mean_block 需 >=1，得到 {mean_block}")
    if n_paths < 1:
        raise ValueError(f"n_paths 需 >=1，得到 {n_paths}")
    p = 1.0 / max(int(mean_block), 1)
    if p >= 0.999:  # geometric(1) 恒为 1：K=n 即必足
        k0 = n + 8
    else:
        k0 = int(math.ceil(n * p * 1.5)) + 64
    lengths = rng.geometric(p, size=(n_paths, k0))
    for _ in range(8):  # 尾部补样（全行统一加宽，实现简单且浪费可忽略）
        if int((lengths.sum(axis=1) < n).sum()) == 0:
            break
        more = rng.geometric(p, size=(n_paths, k0))
        lengths = np.concatenate([lengths, more], axis=1)
    else:  # pragma: no cover — 8 轮不足属统计不可能
        raise RuntimeError("stationary_bootstrap_index_matrix: 块长补样 8 轮未覆盖 n")
    cum = np.cumsum(lengths, axis=1)
    offs = cum - lengths  # 各块在输出流中的起始位（严格递增，块 k 覆盖 [offs_k, offs_{k+1})）
    used = offs < n
    newstart = np.zeros((n_paths, n), dtype=bool)
    rows = np.broadcast_to(np.arange(n_paths)[:, None], lengths.shape)
    newstart[rows[used], offs[used]] = True
    bid = np.cumsum(newstart, axis=1, dtype=np.int64) - 1  # 每位置所属块号（offs[:,0]=0 保证无 -1）
    starts = rng.integers(0, n, size=lengths.shape, dtype=np.int64)
    start_at = np.take_along_axis(starts, bid, axis=1)
    offs_at = np.take_along_axis(offs, bid, axis=1)
    pos = np.arange(n, dtype=np.int64)
    idx = (start_at + (pos[None, :] - offs_at)) % n
    return idx


def wrc_boot_tstats(
    recentered: XPArray,
    idx_matrix: XPArray,
    sqrt_n: float,
    backend: str | None = None,
) -> np.ndarray:
    """White's RC bootstrap t 统计量核（xp 单路径，镜像 walk_forward 同式）。

    Args:
        recentered: 已中心化差分序列 (T,)（调用方按原函数 d-mean(d) 产出）；
        idx_matrix: (B,T) 索引矩阵（同批索引注入对拍契约）；
        sqrt_n: float(np.sqrt(T))（与原函数同源计算）。

    Returns:
        (B,) float64：每路径 mean(sample)/(std(sample,ddof=1)/sqrt_n)，
        std<=0 退化为 0.0（与原函数逐式同构）。
    """
    _, xp = _resolve_xp(backend)
    x = _as_f64_1d(recentered, xp)
    idx = _as_index_matrix(idx_matrix, xp)
    if idx.shape[1] != x.shape[0]:
        raise ValueError(f"recentered 长度 {x.shape[0]} 与索引矩阵 T 维 {idx.shape[1]} 不一致")
    sn = float(sqrt_n)
    samples = x[idx]  # (B,T) 同步 gather
    mu = samples.mean(axis=1)
    sd = samples.std(axis=1, ddof=1)
    ok = sd > 0
    stats = xp.where(ok, mu / (xp.where(ok, sd, 1.0) / sn), 0.0)
    return _to_numpy(stats)


def e2_boot_sharpe_diffs(
    returns_on: XPArray,
    returns_off: XPArray,
    idx_matrix: XPArray,
    periods_per_year: int = 252,
    backend: str | None = None,
) -> np.ndarray:
    """E2 开/关成对 Sharpe 差 bootstrap 核（xp 单路径，镜像 e2 同式）。

    开/关序列共用同一批索引（成对重采样，保留逐期配对结构）；
    annualized_sharpe 同式：(mean/std_ddof1)*sqrt(ppy)，std<=0 退化为 0.0。

    Returns:
        (B,) float64：每路径 sharpe(on[idx]) - sharpe(off[idx])。
    """
    _, xp = _resolve_xp(backend)
    on = _as_f64_1d(returns_on, xp)
    off = _as_f64_1d(returns_off, xp)
    if on.shape[0] != off.shape[0]:
        raise ValueError(f"开/关序列长度需一致: {on.shape[0]} vs {off.shape[0]}")
    idx = _as_index_matrix(idx_matrix, xp)
    if idx.shape[1] != on.shape[0]:
        raise ValueError(f"序列长度 {on.shape[0]} 与索引矩阵 T 维 {idx.shape[1]} 不一致")
    sq = math.sqrt(float(periods_per_year))

    def _sharpe(series: XPArray) -> XPArray:
        s = series[idx]  # (B,T)
        mu = s.mean(axis=1)
        sd = s.std(axis=1, ddof=1)
        ok = sd > 0
        return xp.where(ok, mu / xp.where(ok, sd, 1.0) * sq, 0.0)

    return _to_numpy(_sharpe(on) - _sharpe(off))


def _batch_corr(xp: ModuleType, xb: XPArray, i_arr: XPArray, j_arr: XPArray) -> XPArray:
    """(b,T,k) 批量 Pearson 相关矩阵 (b,k,k)——镜像 np.corrcoef(x, rowvar=False) 同式。

    中心化→批matmul 协方差（ddof=1 与 np.cov 一致；BLAS/cuBLAS 批 GEMM 较 einsum
    实测 3.2x，求和序差 ~1e-15 远低于 1e-9 对拍容差）→外积标准差归一（两次顺序
    除法，与 numpy corrcoef 同形态）→clip [-1,1]（numpy corrcoef 同款）→取成对元素。
    零方差列属病理输入（原模块头注明调用方须先 correlation_preprocessing），
    本核以 d_safe 守卫除零不特判其 nan 语义。
    """
    t_len = xb.shape[1]
    centered = xb - xb.mean(axis=1, keepdims=True)
    cov = xp.matmul(centered.swapaxes(1, 2), centered) / float(t_len - 1)
    kk = xp.arange(xb.shape[2])
    d = xp.sqrt(xp.abs(cov[:, kk, kk]))
    d_safe = xp.where(d > 0, d, 1.0)
    r = cov / d_safe[:, :, None] / d_safe[:, None, :]
    r = xp.clip(r, -1.0, 1.0)
    return r[:, i_arr, j_arr]


def corr_boot_pair_stats(
    panel: XPArray,
    idx_matrix: XPArray,
    backend: str | None = None,
    chunk_rows: int = _DEFAULT_CHUNK_ROWS,
) -> tuple[np.ndarray, np.ndarray]:
    """多元同步行重采样相关系数核（xp 单路径，镜像 correlation_block_bootstrap 同式）。

    同一批索引同步应用于所有列（保 cross-sectional 同期相关，禁各列独立重采样）；
    Spearman=列秩变换（单次 argsort+散射，与原 _rank_columns 双 argsort 逐位等价）
    后的同一相关矩阵式。

    Args:
        panel: (T,k) 对齐收益率面板（ndarray/DataFrame；k>=2）；
        idx_matrix: (B,T) 索引矩阵；
        chunk_rows: 分块宽度（控 (chunk,T,k) 中间张量内存，GPU 侧同样适用）。

    Returns:
        (boot_pearson, boot_spearman) 各 (B, k(k-1)/2) float64；
        列序=原 pairs 列表 [(i,j) for i<j]（=np.triu_indices(k,1) 行主序）。
        CI/阈值聚合留调用方（判定面不入核）。
    """
    _, xp = _resolve_xp(backend)
    x = _as_f64_2d(panel, xp)
    idx = _as_index_matrix(idx_matrix, xp)
    t_len, k_n = x.shape
    if k_n < 2:
        raise ValueError(f"panel 须 k>=2，得到 k={k_n}")
    if idx.shape[1] != t_len:
        raise ValueError(f"panel T={t_len} 与索引矩阵 T 维 {idx.shape[1]} 不一致")
    pi, pj = np.triu_indices(k_n, 1)
    i_arr = xp.asarray(pi)
    j_arr = xp.asarray(pj)
    b_tot = idx.shape[0]
    boot_p = np.empty((b_tot, pi.size), dtype=np.float64)
    boot_s = np.empty_like(boot_p)
    step = max(1, int(chunk_rows))
    for c0 in range(0, b_tot, step):
        sl = slice(c0, min(c0 + step, b_tot))
        xb = x[idx[sl]]  # (b,T,k) 同步行重采样
        boot_p[sl] = _to_numpy(_batch_corr(xp, xb, i_arr, j_arr))
        # 列秩变换：单次 argsort + put_along_axis 散射，与原 _rank_columns 双 argsort
        # 逐位等价（秩=同一置换下的排序位，含并列——并列次序由同一第一次 argsort 决定）；
        # 双 argsort 的第二次排序是纯散射冗余，省一半排序成本（CPU 热点实测主导项）。
        order = xp.argsort(xb, axis=1)
        ranks_i = xp.empty(xb.shape, dtype=xp.int64)
        pos = xp.broadcast_to(xp.arange(t_len, dtype=xp.int64)[None, :, None], xb.shape)
        xp.put_along_axis(ranks_i, order, pos, axis=1)
        boot_s[sl] = _to_numpy(_batch_corr(xp, ranks_i.astype(xp.float64), i_arr, j_arr))
    return boot_p, boot_s


__all__: Final = [
    "BACKEND_ENV",
    "degrade_log",
    "resolve_backend",
    "stationary_bootstrap_index_matrix",
    "wrc_boot_tstats",
    "e2_boot_sharpe_diffs",
    "corr_boot_pair_stats",
]
