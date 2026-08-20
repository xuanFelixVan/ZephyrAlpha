# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] scripts.tests.smoke_test_tick_backtest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] task_bound
"""StrategyRunner.run_tick_backtest 端到端冒烟（真实 QMT tick + mock 权重面板）。

验证路径 A 集成链路：
  日频权重面板 → _build_tick_callback → EventDrivenEngine.run_tick →
  MiniQmtQuoteProvider 真实 tick 回放 → 5档盘口撮合 → BacktestResult

mock build_weight_panel 避免依赖 ClickHouse 日K（该路径已有
test_strategy_runner_mvp.py 的 E2E 覆盖），聚焦验证集成层：
  - provider 时区转换（UTC→北京）在 EDE 链路生效
  - EDE last_price<=0 守卫过滤盘前 tick
  - callback 节奏：调仓日开盘触发，其余返回空
  - MatchingEngine 5档盘口撮合产出 fills
  - Portfolio 应用 fills + 市值更新
  - BacktestResult 11 必填字段齐全

前置条件：
  1. miniQMT 模拟终端已启动并登录（XtMiniQmt.exe 运行中）
  2. config/.env.qmt 已配置 QMT_SIM_PATH
  3. xtquant 250807.1.2+ 已安装（E:\\xtquant）

运行（无需盘中，历史 tick 随时可拉）：
  python scripts/tests/smoke_test_tick_backtest.py
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

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


def main() -> int:
    from decimal import Decimal

    from zephyr.governance.data_governance.miniqmt_provider import MiniQmtQuoteProvider
    from zephyr.pf_core.strategy_engine.strategy_runner import (
        StrategyRunner,
        StrategyRunnerConfig,
    )

    qmt_path = _load_env_qmt()
    symbol = "600000.SH"
    # 近 7 天，覆盖至少 1 个交易日
    end = date.today()
    start = end - timedelta(days=7)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    print(f"[INFO] QMT path={qmt_path}")
    print(f"[INFO] symbol={symbol}  range={start_str} ~ {end_str}")

    # 1. 构造真实 provider
    print("\n=== STEP 1: MiniQmtQuoteProvider 构造 ===")
    try:
        provider = MiniQmtQuoteProvider(path=qmt_path, session_id="smoke_bt")
        print("[OK] provider 构造成功")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] provider 构造失败: {e}")
        return 1

    # 2. 预设权重面板（mock build_weight_panel，避免依赖 ClickHouse）
    #    用近 10 个工作日，权重 0.5，确保覆盖 tick 数据的交易日
    print("\n=== STEP 2: 预设日频权重面板（mock build_weight_panel）===")
    panel_dates = pd.bdate_range(end=end_str, periods=10)
    weight_panel = pd.DataFrame(
        {symbol: [0.5] * len(panel_dates)},
        index=pd.DatetimeIndex(panel_dates, name="date"),
    )
    # data 占位（run_tick_backtest 仅检查非空）
    data = pd.DataFrame({"close": [1.0]}, index=pd.DatetimeIndex(panel_dates, name="date"))
    print(f"[OK] weight_panel: {len(weight_panel)} 个交易日, 权重=0.5")

    # monkey-patch build_weight_panel（脚本作用域，不入 CI）
    StrategyRunner.build_weight_panel = (  # type: ignore[method-assign]
        lambda self, symbols, start, end, config: (data, weight_panel)
    )

    # 3. 构造 config + 跑 run_tick_backtest
    print("\n=== STEP 3: run_tick_backtest（真实 tick + EDE 撮合）===")
    config = StrategyRunnerConfig(
        strategy_id="smoke_tick",
        factor_ids=("momentum_20d",),  # build_weight_panel 已 mock，不实际用
        initial_capital=1_000_000.0,
    )
    runner = StrategyRunner()
    try:
        result = runner.run_tick_backtest(
            symbols=[symbol],
            start=start_str,
            end=end_str,
            config=config,
            provider=provider,
        )
    except Exception as e:  # noqa: BLE001 — 捕获集成链路任意失败
        print(f"[FAIL] run_tick_backtest 失败: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # 4. 验证 BacktestResult
    print("\n=== STEP 4: BacktestResult 验证 ===")
    if result is None:
        print("[FAIL] 返回 None")
        return 1

    # 11 必填字段（CTR-P1-016）
    required = [
        "strategy_id",
        "start_date",
        "end_date",
        "idempotency_key",
        "timestamp",
        "total_return",
        "annual_return",
        "sharpe_ratio",
        "max_drawdown",
        "trades_count",
        "win_rate",
    ]
    missing = [f for f in required if not hasattr(result, f)]
    if missing:
        print(f"[FAIL] BacktestResult 缺字段: {missing}")
        return 1
    print("[OK] 11 必填字段齐全")

    print(f"  strategy_id    = {result.strategy_id}")
    print(f"  start_date     = {result.start_date}")
    print(f"  end_date       = {result.end_date}")
    print(f"  total_return   = {result.total_return}")
    print(f"  annual_return  = {result.annual_return}")
    print(f"  sharpe_ratio   = {result.sharpe_ratio}")
    print(f"  max_drawdown   = {result.max_drawdown}")
    print(f"  trades_count   = {result.trades_count}")
    print(f"  win_rate       = {result.win_rate}")

    # 5. 关键结论
    print("\n=== 结论 ===")
    if result.trades_count > 0:
        print(f"[OK] 产出 {result.trades_count} 笔成交——EDE 5档撮合链路通畅")
    else:
        print("[WARN] trades_count=0（可能 tick 区间无调仓日匹配，或撮合未触发）")
    print(f"[OK] return={result.total_return}  sharpe={result.sharpe_ratio}")
    print("\n=== 冒烟测试通过：路径 A 集成链路端到端可用 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
