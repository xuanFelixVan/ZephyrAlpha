# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] scripts.tests.smoke_test_trading_session
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] task_bound
"""TradingSession 端到端冒烟测试（manual，不入 CI）。

验证 TradingSession 编排器与 MiniQmtBroker 的完整集成：
  connect() → get_positions() → signal → strategy → delta → risk → submit → report → stop()

前置条件：
  1. miniQMT 模拟终端已启动并登录（XtMiniQmt.exe 运行中）
  2. config/.env.qmt 已配置 QMT_SIM_PATH / QMT_SIM_ACCOUNT
  3. xtquant 250807.1.2+ 已安装（E:\\xtquant 或 site-packages）
  4. 建议盘中运行（9:30-15:00），盘外运行仅验证连接+持仓查询

运行：
  python scripts/tests/smoke_test_trading_session.py

安全设计：
  - 使用 mock 信号（不依赖因子计算）
  - max_single=0.01（1% 仓位，小额测试）
  - 限价单 price=最新收盘价（盘外不会成交）
  - stop() 自动撤所有未成交单
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))

# 确保使用独立 xtquant（Python 3.12 兼容版）
_xtquant_path = r"E:\xtquant"
import os  # noqa: E402

if os.path.isdir(_xtquant_path) and _xtquant_path not in sys.path:
    sys.path.insert(0, _xtquant_path)


def _load_env_qmt() -> tuple[str, str]:
    """从 config/.env.qmt 读取 QMT 模拟盘配置。"""
    env_path = _REPO_ROOT / "config" / ".env.qmt"
    if not env_path.exists():
        print(f"[FAIL] 配置文件不存在: {env_path}")
        sys.exit(1)

    qmt_path = ""
    qmt_account = ""
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if key == "QMT_SIM_PATH":
            qmt_path = val
        elif key == "QMT_SIM_ACCOUNT":
            qmt_account = val

    if not qmt_path or not qmt_account:
        print("[FAIL] .env.qmt 缺少 QMT_SIM_PATH 或 QMT_SIM_ACCOUNT")
        sys.exit(1)

    return qmt_path, qmt_account


def _make_xtdata_price_provider():
    """使用 xtdata 获取最新收盘价的 price_provider。"""

    def _provider(universe: list[str]) -> dict[str, Decimal]:
        try:
            from xtquant import xtdata
        except ImportError:
            print("[WARN] xtquant 不可用，价格提供商返回空")
            return {}

        prices: dict[str, Decimal] = {}
        for symbol in universe:
            try:
                data = xtdata.get_market_data_ex([], [symbol], period="1d", count=1)
                df = data.get(symbol) if data else None
                if df is not None and len(df) > 0:
                    close = float(df["close"].iloc[-1])
                    if close > 0:
                        prices[symbol] = Decimal(str(close))
                        continue
            except Exception as e:  # noqa: BLE001
                print(f"[WARN] 获取 {symbol} 价格失败: {e}")
            # 回退：用固定价格 10 元（仅冒烟测试用）
            prices[symbol] = Decimal("10")
            print(f"[WARN] {symbol} 使用回退价格 10.00")
        return prices

    return _provider


def main() -> int:
    from datetime import datetime, timezone

    from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker
    from zephyr.ex_core.order_manager import OrderManager
    from zephyr.ex_core.signal_providers import make_mock_signal_provider
    from zephyr.ex_core.trading_session import TradingSession, TradingSessionConfig
    from zephyr.governance.adapters.risk_validation_bridge import RiskValidationBridge
    from zephyr.pf_core.topn_momentum_strategy import TopNMomentumStrategy
    from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator
    from zephyr.shared.contracts.risk_limits import RiskLimits

    qmt_path, qmt_account = _load_env_qmt()
    print(f"[INFO] QMT path={qmt_path}")
    print(f"[INFO] QMT account={qmt_account}")

    # 组件装配
    broker = MiniQmtBroker(
        path=qmt_path,
        session_id="smoke_ts",
        account_id=qmt_account,
    )
    om = OrderManager()
    om.register_broker("miniqmt", broker)

    strategy = TopNMomentumStrategy()
    risk_validator = RiskValidationBridge(DefaultRiskValidator())

    universe = ["600000.SH", "000001.SZ"]
    signals = {"600000.SH": 1.0, "000001.SZ": 0.8}

    now = datetime.now(timezone.utc)
    config = TradingSessionConfig(
        universe=universe,
        broker_id="miniqmt",
        strategy_id="smoke_test",
        rebalance_interval_seconds=0,  # 仅手动
        strategy_constraints={"top_n": 2, "max_single": 0.01},  # 1% 仓位
        risk_limits=RiskLimits(
            as_of_date=now,
            idempotency_key=f"smoke-{now.isoformat()}",
            max_single_position=0.02,
        ),
    )

    session = TradingSession(
        broker=broker,
        strategy=strategy,
        risk_validator=risk_validator,
        signal_provider=make_mock_signal_provider(signals),
        price_provider=_make_xtdata_price_provider(),
        order_manager=om,
        config=config,
    )

    # 1. 启动
    print("\n=== STEP 1: start() ===")
    try:
        session.start()
        print("[OK] TradingSession 启动成功")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 启动失败: {e}")
        return 1

    try:
        # 2. 查询初始持仓
        print("\n=== STEP 2: 初始持仓 ===")
        snapshot = broker.get_positions()
        print(f"[OK] cash={snapshot.cash}")
        print(f"     total_market_value={snapshot.total_market_value}")
        print(f"     holdings={dict(snapshot.holdings) if snapshot.holdings else '(空)'}")

        # 3. 调仓
        print("\n=== STEP 3: rebalance() ===")
        orders = session.rebalance()
        print(f"[OK] 提交订单数: {len(orders)}")
        for o in orders:
            print(f"     {o.side} {o.symbol} qty={o.quantity} price={o.limit_price} status={o.status}")

        # 4. 会话报告
        print("\n=== STEP 4: get_session_report() ===")
        report = session.get_session_report()
        for k, v in report.items():
            print(f"     {k}: {v}")

        print("\n=== 冒烟测试通过 ===")
        return 0

    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 调仓失败: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        try:
            session.stop()
            print("[INFO] TradingSession 已停止（未成交单已撤销）")
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] 停止时出错: {e}")


if __name__ == "__main__":
    sys.exit(main())
