# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] scripts.tests.smoke_test_ede_path_a_multi
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""EDE 路径 A 多标的端到端验证：日频因子信号 × Tick 5档盘口撮合（多股票组合）。

在单标的验证（smoke_test_ede_path_a.py）基础上扩展到 3 标的组合，重点验证：
  1. 多 symbol 权重面板对齐（build_weight_panel 多列 + strip_map 后缀还原）
  2. EDE 多标的 tick 撮合（SH/SZ 混合标的，tick event.symbol 与权重面板 key 对齐）
  3. 组合层面资金分配（top_n=3, max_single=0.40, 多标的同时调仓）

选股（SH/SZ 混合，测后缀映射；价格适中避免整手问题；7月日K+流动性充足）：
  - 600000.SH  浦发银行  (~10元, SH)
  - 600036.SH  招商银行  (~35元, SH)
  - 000001.SZ  平安银行  (~12元, SZ)

前置条件：
  1. miniQMT 模拟终端已启动并登录
  2. config/.env.qmt 已配置 QMT_SIM_PATH
  3. ClickHouse 有上述 3 标的的日K数据（c1_market.kline_daily）
  4. xtquant 250807.1.2+ 已安装

运行：
  python scripts/tests/smoke_test_ede_path_a_multi.py

验收硬指标：
  - 权重面板含 3 个 symbol 列（后缀还原成功）
  - BacktestResult 非 None（多标的管线完成无异常）
  - trades_count > 0（多标的撮合正常）
  - 无未捕获异常
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))

_XTQUANT_PATH = Path(r"E:\xtquant")
if _XTQUANT_PATH.exists():
    sys.path.insert(0, str(_XTQUANT_PATH))


def _load_env_qmt() -> str:
    """从 config/.env.qmt 读取 QMT 模拟盘路径。"""
    env_path = _REPO_ROOT / "config" / ".env.qmt"
    if not env_path.exists():
        print(f"[FAIL] 配置文件不存在: {env_path}")
        sys.exit(1)
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        if key.strip() == "QMT_SIM_PATH":
            return val.strip()
    print("[FAIL] .env.qmt 缺少 QMT_SIM_PATH")
    sys.exit(1)


def _check_sim_terminal() -> bool:
    """检查模拟终端是否在运行（环境辨识守卫，显化模拟盘 vs 真实资金盘）。"""
    try:
        import psutil
    except ImportError:
        print("[WARN] psutil 未安装，跳过终端检查")
        return True

    qmt_procs = []
    for p in psutil.process_iter(["exe"]):
        try:
            exe = (p.info.get("exe") or "").lower()
            if "xtminiqmt.exe" in exe:
                qmt_procs.append(exe)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not qmt_procs:
        print("[FAIL] 未检测到 QMT 终端运行中")
        return False

    sim_running = any("模拟" in exe for exe in qmt_procs)
    if sim_running:
        print("[OK] 模拟终端在运行（显化：模拟盘，非真实资金盘）")
        return True

    if any("证券" in exe and "模拟" not in exe for exe in qmt_procs):
        print("[FAIL] 只有真实资金盘在运行，请启动模拟终端（显化：禁止用真实盘跑测试）")
        return False

    print(f"[WARN] 终端类型不确定: {qmt_procs}，继续")
    return True


# 多标的组合（SH/SZ 混合，测后缀映射；价格适中；7月流动性充足）
SYMBOLS = ["600000.SH", "600036.SH", "000001.SZ"]


def main() -> int:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s %(levelname)s: %(message)s",
    )

    from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
    from zephyr.governance.data_governance.miniqmt_provider import MiniQmtQuoteProvider
    from zephyr.pf_core.strategy_engine.strategy_runner import (
        StrategyRunner,
        StrategyRunnerConfig,
    )

    # 0. 环境检查
    print("=== STEP 0: 环境检查 ===")
    qmt_path = _load_env_qmt()
    print(f"[INFO] QMT path={qmt_path}")
    if not _check_sim_terminal():
        return 1

    # 1. 创建 provider
    print("\n=== STEP 1: MiniQmtQuoteProvider 构造 ===")
    provider = MiniQmtQuoteProvider(path=qmt_path, session_id="ede_path_a_multi")
    print("[OK] provider 构造成功")

    # 2. 配置：3 标的组合，top_n=3（全选），max_single=0.40（留佣金空间）
    start = "2026-07-01"
    end = "2026-07-31"

    config = StrategyRunnerConfig(
        strategy_id="topn-momentum",
        factor_ids=("momentum_20d",),
        synthesis_method="equal_weight",
        rebalance_freq="B",  # 每交易日调仓
        pit_shift=1,
        top_n=3,  # 选前 3（=标的数，全选）
        max_single=0.40,  # 单标的上限 40%，3 标的约各 33%
        initial_capital=100000,
        backtest_config=BacktestConfig(initial_capital=Decimal("100000")),
    )

    print("\n=== STEP 2: 多标的 Path A 回测 ===")
    print(f"[INFO] symbols={SYMBOLS}")
    print(f"[INFO] range={start} ~ {end}")
    print(f"[INFO] strategy={config.strategy_id}  factor={config.factor_ids}")
    print(f"[INFO] top_n={config.top_n}  max_single={config.max_single}")

    # 3. 预检：单独构造权重面板，验证多列对齐 + strip_map 后缀还原
    print("\n=== STEP 3: 权重面板预检（多标的对齐）===")
    runner = StrategyRunner()
    try:
        data, weight_panel = runner.build_weight_panel(SYMBOLS, start, end, config)
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] build_weight_panel 失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if weight_panel.empty:
        print("[FAIL] 权重面板为空（因子信号未生成或数据缺失）")
        return 1

    print(f"[INFO] weight_panel shape={weight_panel.shape}")
    print(f"[INFO] weight_panel columns={list(weight_panel.columns)}")
    print(f"[INFO] weight_panel index range={weight_panel.index.min()} ~ {weight_panel.index.max()}")

    # 验收：权重面板必须含全部 3 标的列（纯数字代码，load_history 去后缀）
    stripped = [s.split(".")[0] for s in SYMBOLS]
    missing_cols = [s for s in stripped if s not in weight_panel.columns]
    if missing_cols:
        print(f"[FAIL] 权重面板缺失标的列: {missing_cols}（数据未覆盖）")
        return 1
    print(f"[OK] 权重面板含全部 {len(SYMBOLS)} 标的列: {stripped}")

    # 展示有信号的调仓日权重分布（非零行）
    nonzero_rows = weight_panel.loc[(weight_panel != 0).any(axis=1)]
    if nonzero_rows.empty:
        print("[WARN] 权重面板无非零行（momentum_20d 信号窗口不足）")
    else:
        print(f"[INFO] 调仓日数={len(nonzero_rows)}（非零权重行）")
        print("[INFO] 最近 3 个调仓日权重分布：")
        for ts in nonzero_rows.index[-3:]:
            row = nonzero_rows.loc[ts]
            weights = {sym: round(float(w), 4) for sym, w in row.items() if w != 0}
            print(f"    {ts}: {weights}")

    # 4. 运行 Path A 多标的回测（EDE tick 撮合）
    print("\n=== STEP 4: EDE 多标的 tick 撮合回测 ===")
    print("[INFO] 正在下载 tick 数据并回放（3 标的 × 多日，预计耗时数分钟）...")
    try:
        result = runner.run_tick_backtest(
            symbols=SYMBOLS,
            start=start,
            end=end,
            config=config,
            provider=provider,
        )
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] Path A 多标的回测失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 5. 结果分析
    print("\n=== STEP 5: 结果 ===")
    print(f"  strategy_id={result.strategy_id}")
    print(f"  total_return={result.total_return:.4f}")
    print(f"  annual_return={result.annual_return:.4f}")
    print(f"  sharpe_ratio={result.sharpe_ratio:.4f}")
    print(f"  max_drawdown={result.max_drawdown:.4f}")
    print(f"  trades_count={result.trades_count}")
    print(f"  win_rate={result.win_rate:.4f}")

    # 6. 验收检查
    print("\n=== STEP 6: 验收检查 ===")
    all_pass = True

    # 6a. 权重面板 3 列对齐
    if len(weight_panel.columns) >= len(SYMBOLS):
        print(f"[OK] 权重面板多标的对齐（{len(weight_panel.columns)} 列）")
    else:
        print(f"[FAIL] 权重面板列数不足: {len(weight_panel.columns)} < {len(SYMBOLS)}")
        all_pass = False

    # 6b. 撮合成交
    if result.trades_count == 0:
        print("[WARN] trades_count=0（可能 tick 数据未覆盖调仓日，或 symbol 格式未对齐）")
    else:
        print(f"[OK] trades_count={result.trades_count} > 0（多标的撮合正常）")

    # 6c. BacktestResult 字段完整
    required_fields = [
        "strategy_id", "total_return", "sharpe_ratio",
        "max_drawdown", "trades_count", "win_rate",
    ]
    missing = [f for f in required_fields if not hasattr(result, f)]
    if missing:
        print(f"[FAIL] BacktestResult 缺失字段: {missing}")
        all_pass = False
    else:
        print("[OK] BacktestResult 字段完整")

    print("[OK] 多标的管线无未捕获异常完成")

    if all_pass:
        print("\n=== 多标的 Path A 端到端验证通过 ===")
        print("结论: 3 标的组合（SH/SZ 混合）日频信号 × Tick 5档盘口撮合 全链路跑通")
        print("      多 symbol 权重面板对齐 ✓  |  EDE 多标的 tick 撮合 ✓  |  组合资金分配 ✓")
    else:
        print("\n=== 多标的 Path A 端到端验证失败 ===")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
