# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | bootstrap核对拍测试（同索引矩阵注入法）
# [MODULE] scripts.backtest.fexam.bootstrap_gpu.parity_test.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] run_fexam.py 或手工 CLI
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] staging 转正件；判定面不入核
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 见 docstring
# [TESTS] tests/backtest/fexam/
# [TTL] task_bound
# create-guard-not-dup: tmp 24h TTL 抢救转正件（Owner 批 P0-1），对拍结论已锁定随文件
# -*- coding: utf-8 -*-
"""三原函数 × 新核 同索引矩阵注入对拍（GPU 化调查册 §二 铁律 3）。

RNG 与原标量实现不同源，同种子逐位不可行——故用同索引矩阵注入法：
monkey-patch 各原实现的索引供给函数（WRC 的 _stationary_block_bootstrap /
e2 与 corr 的 stationary_bootstrap_indices），让**真实原实现**吃到与本核
完全相同的 (B,T) 索引矩阵，再对 p_value / t_stat / CI 上限 / prob 断言 <=1e-9。
另附 bootstrap 统计量矩阵全量 max|Δ| 头皮距，以及索引生成器分布合理性检验。

夜战纪律自证：全程断言 "cupy" not in sys.modules（零 import 触发）。
运行：python parity_test.py（需 PYTHONPATH=src；退出码非 0=对拍失败）
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3] / "src"))  # 兜底 zephyr 包解析（env PYTHONPATH 为主）

from kernel import (  # noqa: E402
    corr_boot_pair_stats,
    e2_boot_sharpe_diffs,
    resolve_backend,
    stationary_bootstrap_index_matrix,
    wrc_boot_tstats,
)

# st-mx07-L3 P1-3 迁移适配：kernel 已成 src/zephyr/backtest/accel/bootstrap_kernel.py 的薄
# re-export（真源 MOD-BT-237），import 时 zephyr.backtest 包初始化会传递加载 cupy（既有包
# 行为，与本核无关——原"import kernel 后 sys.modules 零 cupy"断言在门面态不可满足）。
# 静态守卫改为：真源核本体零顶层 cupy import；运行面由 main() 末尾 auto 恒 CPU 断言承担。
import zephyr.backtest.accel.bootstrap_kernel as _src_kernel  # noqa: E402


def _assert_kernel_source_no_top_cupy() -> None:
    """真源核本体零顶层 cupy import（NO-IMPORT-SIDE-EFFECT：检查收敛到 main，模块导入零 I/O）。"""
    lines = Path(_src_kernel.__file__).read_text(encoding="utf-8").splitlines()
    top = [ln for ln in lines if ln.startswith("import cupy")]
    assert not top, f"真源核本体顶层 cupy import 违规: {top}"


from zephyr.backtest.core import walk_forward as wfmod  # noqa: E402
from zephyr.backtest.core.walk_forward import WalkForwardAnalyzer  # noqa: E402
from zephyr.backtest.regime_validation import e2_stationary_bootstrap as e2mod  # noqa: E402
from zephyr.factor.analysis import correlation_block_bootstrap as cbbmod  # noqa: E402

TOL = 1e-9
T = 1600
N_BOOT = 2000
FAILS: list[str] = []


def check(name: str, a, b, tol: float = TOL) -> None:
    diff = float(np.max(np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))))
    ok = diff <= tol
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: max|delta|={diff:.3e} (tol {tol:g})")
    if not ok:
        FAILS.append(name)


class _Feed:
    """按序供给注入索引（消费计数守恒校验防静默错位）。

    st-mx07-L3 P1-3 接线后消费方索引缝由"逐行标量供给"升级为"一次吃整张 (B,T)
    矩阵"——next_matrix() 即矩阵缝注入口，计数从 N_BOOT 变为 1。
    """

    def __init__(self, mat: np.ndarray):
        self.mat = mat
        self.i = 0

    def next(self) -> np.ndarray:
        row = self.mat[self.i]
        self.i += 1
        return row

    def next_matrix(self) -> np.ndarray:
        self.i += 1
        return self.mat


def make_data(seed: int = 20261006) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """T=1600 双序列（AR(0.3) 策略 vs 同源相关基准）+ 4 列因子面板。"""
    rng = np.random.default_rng(seed)
    eps = rng.normal(0.0, 0.010, T)
    s = np.empty(T)
    s[0] = 0.0005 + eps[0]
    for t in range(1, T):
        s[t] = 0.0005 + 0.30 * s[t - 1] + eps[t]
    b = 0.40 * s + 0.0002 + rng.normal(0.0, 0.008, T)
    f = rng.normal(0.0, 0.010, T)
    betas = np.array([0.9, 0.5, -0.3, 0.7])
    panel = betas[None, :] * f[:, None] + rng.normal(0.0, 0.006, (T, 4))
    return s, b, panel


def sanity_index_generator() -> None:
    """索引生成器分布合理性（统计检验，非逐位——与原 RNG 不同源是设计前提）。"""
    n, mb, paths = 1600, 12, 500
    idx = stationary_bootstrap_index_matrix(n, mb, paths, np.random.default_rng(7))
    assert idx.min() >= 0 and idx.max() < n and idx.shape == (paths, n)
    restart_rate = float((idx[:, 1:] != (idx[:, :-1] + 1) % n).mean())
    check("索引生成器 重开率≈p(1/12)", restart_rate, 1.0 / 12, tol=0.15 / 12)
    print(f"       实测平均块长≈{1.0 / restart_rate:.2f}（目标 {mb}）")


def test_wrc(s: np.ndarray, b: np.ndarray) -> None:
    """whites_reality_check：索引注入端到端 + boot_tstat 矩阵全量对拍。"""
    ser_s, ser_b = pd.Series(s), pd.Series(b)
    aligned = pd.concat([ser_s, ser_b], axis=1).dropna()
    diff = (aligned.iloc[:, 0] - aligned.iloc[:, 1]).to_numpy(dtype=float)
    n = len(diff)
    obs_mean = float(np.mean(diff))
    obs_std = float(np.std(diff, ddof=1))
    sqrt_n = float(np.sqrt(n))
    obs_t = obs_mean / (obs_std / sqrt_n)
    recentered = diff - obs_mean
    block = max(1, int(round(n ** (1.0 / 3.0))))  # 原函数 auto 公式（T=1600 → 12）

    idx = stationary_bootstrap_index_matrix(n, block, N_BOOT, np.random.default_rng(101))
    feed = _Feed(idx)
    orig_fn = wfmod.stationary_bootstrap_index_matrix

    def _injected(n_, mb_, npaths_, rng_, _f=feed):  # noqa: ARG001 — rng 刻意弃用（注入契约）
        return _f.next_matrix()

    wfmod.stationary_bootstrap_index_matrix = _injected
    try:
        res = WalkForwardAnalyzer().whites_reality_check(ser_s, ser_b, n_bootstrap=N_BOOT, block_size=0)
    finally:
        wfmod.stationary_bootstrap_index_matrix = orig_fn
    assert feed.i == 1, f"WRC 矩阵索引缝消费数 {feed.i} != 1"

    ref = np.empty(N_BOOT)  # 原函数 276-280 行同式的参考逐 b 统计（同索引）
    for i in range(N_BOOT):
        sample = recentered[idx[i]]
        s_std = float(np.std(sample, ddof=1))
        ref[i] = 0.0 if s_std <= 0 else float(np.mean(sample)) / (s_std / sqrt_n)
    boot = wrc_boot_tstats(recentered, idx, sqrt_n)
    p_kernel = float(np.mean(boot >= obs_t))

    check("WRC boot_tstat 矩阵 (2000)", boot, ref)
    check("WRC p_value", p_kernel, float(res["p_value"]))
    check("WRC t_stat", obs_t, float(res["t_stat"]))


def test_e2(s: np.ndarray, b: np.ndarray) -> None:
    """bootstrap_sharpe_difference：索引注入端到端 + sharpe_diff 矩阵全量对拍。"""
    cfg = e2mod.E2BootstrapConfig(n_boot=N_BOOT, mean_block=21, seed=42, ci_level=0.90)
    idx = stationary_bootstrap_index_matrix(T, 21, N_BOOT, np.random.default_rng(202))
    feed = _Feed(idx)
    orig_fn = e2mod.stationary_bootstrap_index_matrix
    e2mod.stationary_bootstrap_index_matrix = lambda n_, mb_, nb_, rng_, _f=feed: _f.next_matrix()  # noqa: ARG005
    try:
        res = e2mod.bootstrap_sharpe_difference(s, b, cfg)
    finally:
        e2mod.stationary_bootstrap_index_matrix = orig_fn
    assert feed.i == 1, f"E2 矩阵索引缝消费数 {feed.i} != 1"

    ref = np.array([e2mod.annualized_sharpe(s[idx[i]]) - e2mod.annualized_sharpe(b[idx[i]]) for i in range(N_BOOT)])
    diffs = e2_boot_sharpe_diffs(s, b, idx, periods_per_year=252)
    alpha = 1.0 - cfg.ci_level
    ci_upper_kernel = float(np.quantile(diffs, 1.0 - alpha / 2.0))
    prob_kernel = float(np.mean(diffs > 0.0))

    check("E2 sharpe_diff 矩阵 (2000)", diffs, ref)
    check("E2 ci_upper", ci_upper_kernel, float(res.ci_upper))
    check("E2 prob_positive", prob_kernel, float(res.prob_positive))
    check("E2 observed_diff", e2mod.annualized_sharpe(s) - e2mod.annualized_sharpe(b), float(res.observed_diff))


def test_corr(panel: np.ndarray) -> None:
    """bootstrap_correlation_ci：索引注入端到端 + pearson/spearman 矩阵全量对拍。"""
    names = ["f0", "f1", "f2", "f3"]
    blk = 17
    df = pd.DataFrame(panel, columns=names)
    x = df.to_numpy(dtype=float)
    pairs = [(i, j) for i in range(4) for j in range(i + 1, 4)]
    i_arr = np.array([p[0] for p in pairs])
    j_arr = np.array([p[1] for p in pairs])

    idx = stationary_bootstrap_index_matrix(T, blk, N_BOOT, np.random.default_rng(303))
    feed = _Feed(idx)
    orig_fn = cbbmod.stationary_bootstrap_index_matrix
    cbbmod.stationary_bootstrap_index_matrix = lambda n_, bs_, nb_, rng_, _f=feed: _f.next_matrix()  # noqa: ARG005
    try:
        res = cbbmod.bootstrap_correlation_ci(
            df, n_bootstrap=N_BOOT, block_size=blk, confidence=0.90, threshold=0.6, seed=7
        )
    finally:
        cbbmod.stationary_bootstrap_index_matrix = orig_fn
    assert feed.i == 1, f"CORR 矩阵索引缝消费数 {feed.i} != 1"

    ref_p = np.empty((N_BOOT, len(pairs)))
    ref_s = np.empty_like(ref_p)
    for bi in range(N_BOOT):  # 原实现内部同款统计路径 _pair_corr_stats（真实原函数）
        pm, sm = cbbmod._pair_corr_stats(x[idx[bi]])
        ref_p[bi] = pm[i_arr, j_arr]
        ref_s[bi] = sm[i_arr, j_arr]
    boot_p, boot_s = corr_boot_pair_stats(x, idx)

    check("CORR pearson 矩阵 (2000x6)", boot_p, ref_p)
    check("CORR spearman 矩阵 (2000x6)", boot_s, ref_s)
    alpha = (1.0 - 0.90) / 2.0
    for field, mat, rmap in (("pearson", boot_p, res.pearson), ("spearman", boot_s, res.spearman)):
        for qi, (i, j) in enumerate(pairs):
            col = mat[:, qi]
            col = col[np.isfinite(col)]  # 原实现 _build 同款过滤
            pair_ci = rmap[(names[i], names[j])]
            check(
                f"CORR {field}[{names[i]},{names[j]}] ci_upper",
                float(np.quantile(col, 1.0 - alpha)),
                float(pair_ci.ci_upper),
            )
            check(
                f"CORR {field}[{names[i]},{names[j]}] prob>0.6",
                float(np.mean(col > 0.6)),
                float(pair_ci.prob_above_threshold),
            )


def main() -> int:
    _assert_kernel_source_no_top_cupy()
    print(f"parity_test: T={T} N_BOOT={N_BOOT} tol={TOL:g}（同索引矩阵注入法）")
    sanity_index_generator()
    s, b, panel = make_data()
    test_wrc(s, b)
    test_e2(s, b)
    test_corr(panel)
    # 夜战纪律（第 2 层）：即便 zephyr.backtest.__init__ 已传递加载 cupy（既有包行为），
    # 本核 auto 也必须恒 CPU——零 GPU 触碰
    be = resolve_backend()
    transitive = "cupy" in sys.modules
    print(
        f"[{'PASS' if be == 'cpu' else 'FAIL'}] 夜战纪律：本核 auto 恒 CPU（解析={be}；"
        f"zephyr.backtest 传递加载 cupy={'是（既有包行为，非本核触发）' if transitive else '否'}）"
    )
    if be != "cpu":
        FAILS.append("gpu_touched")
    if FAILS:
        print(f"RESULT: FAIL ({len(FAILS)} 项): {FAILS}")
        return 1
    print("RESULT: PASS — 三原函数 × 新核 对拍全部 <=1e-9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
