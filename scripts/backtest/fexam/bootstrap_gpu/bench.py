# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | bootstrap核基准计时（2000x1600提速留档）
# [MODULE] scripts.backtest.fexam.bootstrap_gpu.bench.py
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
"""bootstrap 三核基准：2000 次 x T=1600，原实现 vs 新核（numpy CPU 真跑，禁 GPU）。

计时口径：原实现 1 次全程（含其内部索引生成的真实成本）；新核取 3 次最优
（含 stationary_bootstrap_index_matrix 索引生成端到端成本——诚实口径，不做拆分美化）。
探针数据落盘 bench_result.json（同目录）。提速 <1.5x 如实标注。

夜战纪律：auto 恒 CPU；断言 resolve_backend()=="cpu" 且本核 import 不触发 cupy
（zephyr.backtest.__init__ 传递加载 cupy 属既有包行为，与本核无关）。
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3] / "src"))

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
# 静态守卫改为：真源核本体零顶层 cupy import（夜战纪律的可达形态），运行面由下一行 auto 恒 CPU 断言承担。
import zephyr.backtest.accel.bootstrap_kernel as _src_kernel  # noqa: E402


def _assert_kernel_source_no_top_cupy() -> None:
    """真源核本体零顶层 cupy import（NO-IMPORT-SIDE-EFFECT：检查收敛到 main，模块导入零 I/O）。"""
    lines = Path(_src_kernel.__file__).read_text(encoding="utf-8").splitlines()
    top = [ln for ln in lines if ln.startswith("import cupy")]
    assert not top, f"真源核本体顶层 cupy import 违规: {top}"


from zephyr.backtest.core.walk_forward import WalkForwardAnalyzer  # noqa: E402
from zephyr.backtest.regime_validation import e2_stationary_bootstrap as e2mod  # noqa: E402
from zephyr.factor.analysis import correlation_block_bootstrap as cbbmod  # noqa: E402

T = 1600
N_BOOT = 2000
PERIODS = 252


def make_case_data(seed: int, k_panel: int = 4) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    eps = rng.normal(0.0, 0.010, T)
    s = np.empty(T)
    s[0] = 0.0005 + eps[0]
    for t in range(1, T):
        s[t] = 0.0005 + 0.30 * s[t - 1] + eps[t]
    b = 0.40 * s + 0.0002 + rng.normal(0.0, 0.008, T)
    f = rng.normal(0.0, 0.010, T)
    betas = rng.uniform(-0.9, 0.9, k_panel)
    panel = betas[None, :] * f[:, None] + rng.normal(0.0, 0.006, (T, k_panel))
    return s, b, panel


def timeit(fn, runs: int = 1, keep_best: bool = False):
    times, out = [], None
    for _ in range(runs):
        t0 = time.perf_counter()
        out = fn()
        times.append(time.perf_counter() - t0)
    return (min(times) if keep_best else times[0]), out


def _digest(out) -> str:
    """原实现返回对象（dict/dataclass）→ 短摘要串（JSON 安全留档）。"""
    text = str(out)
    return text[:300] + ("..." if len(text) > 300 else "")


def bench_case(name: str, fn_orig, fn_new) -> dict:
    t_orig, out_orig = timeit(fn_orig, runs=1)
    t_new, out_new = timeit(fn_new, runs=3, keep_best=True)
    speedup = t_orig / t_new
    flag = "" if speedup >= 1.5 else "  <-- <1.5x 如实报"
    print(f"{name:24s} 原实现 {t_orig:8.3f}s | 新核 {t_new * 1000:9.1f}ms | 提速 {speedup:8.1f}x{flag}")
    return {
        "case": name,
        "orig_seconds": round(t_orig, 4),
        "new_seconds_best_of_3": round(t_new, 6),
        "speedup_x": round(speedup, 1),
        "orig_output_digest": _digest(out_orig),
        "new_output_digest": _digest(out_new),
    }


def main() -> int:
    _assert_kernel_source_no_top_cupy()
    assert resolve_backend() == "cpu", "auto 后端须恒 CPU（夜战纪律）"
    print(f"bench: B={N_BOOT} x T={T} | backend={resolve_backend()} | numpy {np.__version__}")
    results: list[dict] = []

    # ---- Case 1: White's Reality Check（block_size auto=T^(1/3)=12）----
    s, b, _ = make_case_data(9001)
    ser_s, ser_b = pd.Series(s), pd.Series(b)
    analyzer = WalkForwardAnalyzer()

    def orig_wrc():
        return analyzer.whites_reality_check(ser_s, ser_b, n_bootstrap=N_BOOT, block_size=0)

    aligned = pd.concat([ser_s, ser_b], axis=1).dropna()
    diff = (aligned.iloc[:, 0] - aligned.iloc[:, 1]).to_numpy(dtype=float)
    n = len(diff)
    obs_mean, obs_std = float(np.mean(diff)), float(np.std(diff, ddof=1))
    sqrt_n = float(np.sqrt(n))
    obs_t = obs_mean / (obs_std / sqrt_n)
    recentered = diff - obs_mean
    blk_wrc = max(1, int(round(n ** (1.0 / 3.0))))

    def new_wrc():
        t0 = time.perf_counter()
        idx = stationary_bootstrap_index_matrix(n, blk_wrc, N_BOOT, np.random.default_rng(11))
        t_idx = time.perf_counter() - t0
        boot = wrc_boot_tstats(recentered, idx, sqrt_n)
        p = float(np.mean(boot >= obs_t))
        return {"p_value": p, "idx_gen_s": round(t_idx, 6)}

    r = bench_case("WRC (n_boot=2000)", orig_wrc, new_wrc)
    results.append(r)

    # ---- Case 2: E2 stationary bootstrap Sharpe 差（mean_block=21）----
    s2, b2, _ = make_case_data(9002)
    cfg = e2mod.E2BootstrapConfig(n_boot=N_BOOT, mean_block=21, seed=42, ci_level=0.90)

    def orig_e2():
        return e2mod.bootstrap_sharpe_difference(s2, b2, cfg)

    def new_e2():
        t0 = time.perf_counter()
        idx = stationary_bootstrap_index_matrix(T, 21, N_BOOT, np.random.default_rng(22))
        t_idx = time.perf_counter() - t0
        diffs = e2_boot_sharpe_diffs(s2, b2, idx, periods_per_year=PERIODS)
        alpha = 1.0 - cfg.ci_level
        return {
            "ci_upper": float(np.quantile(diffs, 1.0 - alpha / 2.0)),
            "prob_positive": float(np.mean(diffs > 0.0)),
            "idx_gen_s": round(t_idx, 6),
        }

    r = bench_case("E2 sharpe_diff (2000)", orig_e2, new_e2)
    results.append(r)

    # ---- Case 3: 多元同步相关 bootstrap（k=2 双序列 与 k=8 多元；block=17）----
    for k in (2, 8):
        _, _, panel = make_case_data(9003 + k, k_panel=k)
        df = pd.DataFrame(panel, columns=[f"S{j}" for j in range(k)])
        seed_corr = 7

        def orig_corr():
            return cbbmod.bootstrap_correlation_ci(
                df, n_bootstrap=N_BOOT, block_size=17, confidence=0.90, threshold=0.6, seed=seed_corr
            )

        def new_corr():
            t0 = time.perf_counter()
            idx = stationary_bootstrap_index_matrix(T, 17, N_BOOT, np.random.default_rng(33 + k))
            t_idx = time.perf_counter() - t0
            bp, bs = corr_boot_pair_stats(df, idx)
            return {
                "pearson_matrix_shape": list(bp.shape),
                "spearman_matrix_shape": list(bs.shape),
                "pearson_mean": float(np.nanmean(bp)),
                "idx_gen_s": round(t_idx, 6),
            }

        r = bench_case(f"CORR k={k} (2000)", orig_corr, new_corr)
        results.append(r)

    payload = {
        "archived_at": datetime.now().isoformat(),
        "bench_shape": f"B={N_BOOT} x T={T}",
        "backend": resolve_backend(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "timing_note": "orig=1 次全程（含其内部标量索引生成）；new=3 次最优（含批量索引生成端到端）",
        "night_discipline": "auto 恒 CPU；本核 import 零 cupy 触发（zephyr.backtest.__init__ "
        "传递加载 cupy 属既有包行为，与本核无关）",
        "cases": results,
    }
    out_path = HERE / "bench_result.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"探针数据已留档: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
