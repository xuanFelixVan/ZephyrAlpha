# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | IC核GPU冒烟（空窗前置自动预检拒跑）
# [MODULE] scripts.backtest.fexam.gpu_ic.smoke_gpu.py
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
# ============================================================================
# [SMOKE-GPU] !! 今晚【不】执行 —— GPU 被 st-t3series 车道占用（vram 独占纪律）!!
#
# quiet 窗口且 nvidia-smi 空闲时执行：cupy 后端跑同一 parity_test，逐位对拍通过
# （max|dIC|<1e-9）方可替换生产内核（ic_exam.fast_rank_ic）；交易引擎
# （vectorized_engine）永远禁碰。
#
# 执行前置条件（缺一不可，脚本自带预检，非空闲自动拒绝）：
#   1) quiet 窗口：无其他 GPU 车道在跑（st-t3series 等已收工）；
#   2) nvidia-smi 无 compute 进程，且显存余量 >= 2GiB；
#   3) CH（172.24.30.100:8123）可达（真实指标对拍用例需要）。
#
# 预检两档制（--tier，默认 exclusive=原行为零变化）：
#   exclusive（默认/大网格）：vram 独占纪律——无 compute 进程且空闲显存 >= 2GiB；
#   small（白天小考试 rank-IC）：只看空闲显存 >= 8GiB 即放行，否则照旧 ABORT。
#
# numpy 对照基线（2026-10-06 今晚实测，bench_numpy.py，5000tick x 485day x 20col）：
#   rank_ic(numpy) best_total=19.508s  per_col=975.4ms（repeats 20.113/19.931/19.508s）
#   fast_rank_ic(pandas 原版) per_col=880.3ms
#   cupy 版目标：同规模下显著快于 19.5s 且对拍逐位通过，才有替换价值。
#
# 执行方式（Git Bash）：
#   export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
#   export PYTHONPATH=/d/ZephyrAlpha/src
#   python scripts/backtest/fexam/gpu_ic/smoke_gpu.py               # 默认 exclusive（原行为）
#   python scripts/backtest/fexam/gpu_ic/smoke_gpu.py --tier small  # 白天小考试（空闲>=8GiB 放行）
# ============================================================================
"""smoke_gpu — cupy 后端 GPU 冒烟：nvidia-smi 两档预检 + 同一套 parity 全用例（cupy）。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[3]
for _p in (str(_ROOT / "src"), str(_ROOT / "scripts" / "backtest" / "fexam"), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402

_FREE_MIB_MIN = 2048  # exclusive 档最低空闲显存
_FREE_MIB_MIN_SMALL = 8192  # small 档最低空闲显存（白天小考试放行线）


def gpu_status(tier: str = "exclusive") -> tuple[bool, str]:
    """(busy, reason)。预检两档：exclusive=无 compute 进程且空闲显存足够（vram 独占纪律）；
    small=只看空闲显存 >= 8GiB 即放行（白天小考试）；无 GPU/查询异常一律按"忙"拒跑（fail-closed）。"""
    free_min = _FREE_MIB_MIN_SMALL if tier == "small" else _FREE_MIB_MIN
    try:
        if tier != "small":
            apps = run_subprocess_hidden(
                ["nvidia-smi", "--query-compute-apps=pid,process_name", "--format=csv,noheader"],
                timeout=30,
            )
            if apps.returncode != 0:
                return True, f"nvidia-smi 失败 rc={apps.returncode}: {apps.stderr.strip()[:120]}"
            if apps.stdout.strip():
                return True, f"GPU compute 进程占用: {apps.stdout.strip()[:160]}"
        mem = run_subprocess_hidden(
            ["nvidia-smi", "--query-gpu=memory.free,memory.total,name", "--format=csv,noheader"],
            timeout=30,
        )
        first = mem.stdout.strip().splitlines()[0]
        free_str, _total_str, name = (s.strip() for s in first.split(","))
        free_mib = int(free_str.split()[0])
        if free_mib < free_min:
            tag = "" if tier == "exclusive" else f" (tier={tier})"
            return True, f"显存余量不足: free={free_mib}MiB < {free_min}MiB{tag}"
        return False, f"GPU 空闲（{name}, free={free_mib}MiB）"
    except FileNotFoundError:
        return True, "nvidia-smi 不存在（无 GPU/驱动）"
    except Exception as exc:  # noqa: BLE001 — 预检任何异常一律按"忙"拒跑（fail-closed）
        return True, f"nvidia-smi 预检异常: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="cupy 后端 GPU 冒烟（预检两档制）")
    parser.add_argument(
        "--tier",
        choices=("small", "exclusive"),
        default="exclusive",
        help="small=空闲显存>=8GiB 即放行（白天小考试）；exclusive=vram 独占（默认，原行为）",
    )
    args = parser.parse_args()
    busy, why = gpu_status(args.tier)
    print(f"[preflight] tier={args.tier} {why}")
    if busy:
        print("SMOKE-ABORT: GPU 非空闲——维持 vram 独占纪律，改日 quiet 窗口重试")
        return 2

    import cupy as cp  # 预检通过后才触碰 GPU（懒加载闸门）
    from gpu_rank_ic import rank_ic  # noqa: E402
    from parity_test import TOL, run_all_cases  # noqa: E402

    dev = cp.cuda.runtime.getDeviceProperties(0)["name"]
    print(f"cupy={cp.__version__} device={dev if isinstance(dev, str) else dev.decode(errors='replace')}")

    # 冒烟即全量对拍：合成三边角 + 2 列真实指标，全部走 xp="cupy"
    results = run_all_cases("cupy")
    worst = max(d for _, d in results)
    ok = worst < TOL
    tag = "SMOKE-OK" if ok else "SMOKE-FAIL"
    print(f"{tag} backend=cupy cases={len(results)} worst|dIC|={worst:.3e} tol={TOL:.0e}")
    if ok:
        print("next: cupy 版同规模计时（bench_numpy.py 同参数）对照 numpy 基线 19.508s/20col")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
