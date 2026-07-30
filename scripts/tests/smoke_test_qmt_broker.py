# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] scripts.tests.smoke_test_qmt_broker
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] task_bound
"""QMT Broker 运行时冒烟测试（manual，不入 CI）。

治本核心（#ARCH-XTQUANT-API-COMPAT-001）：用运行时实证堵住 100% AI 开发的契约漂移。
静态阅读 xtquant 源码无法 100% 确认的开放点（order_stock 失败返回值、price_type 值、
subscribe 必要性、session int 要求），本脚本对接真实模拟盘验证。

前置条件：
  1. miniQMT 模拟终端已启动并登录（XtMiniQmt.exe 运行中）
  2. config/.env.qmt 已配置 QMT_SIM_PATH / QMT_SIM_ACCOUNT
  3. xtquant 250807.1.2+ 已安装（E:\\xtquant 或 site-packages）

运行：
  python scripts/tests/smoke_test_qmt_broker.py

验证链路：
  connect() → get_positions()（查资金）→ 挂远期限价单（不成交）→
  query_order()（查委托）→ cancel_order()（撤单）→ query_order()（查撤单状态）
"""
from __future__ import annotations

import os
import sys
from decimal import Decimal
from pathlib import Path

# 确保项目 src 在 path 中
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))


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


def main() -> int:
    from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker, MiniQmtBrokerError
    from zephyr.trading.trading_contracts.execution.order import (
        Order,
        OrderSide,
        OrderType,
    )

    qmt_path, qmt_account = _load_env_qmt()
    print(f"[INFO] QMT path={qmt_path}")
    print(f"[INFO] QMT account={qmt_account}")

    broker = MiniQmtBroker(
        path=qmt_path,
        session_id="smoke_test",
        account_id=qmt_account,
    )

    # 1. 连接
    print("\n=== STEP 1: connect() ===")
    try:
        broker.connect()
        print("[OK] 连接成功")
    except MiniQmtBrokerError as e:
        print(f"[FAIL] 连接失败: {e}")
        return 1

    try:
        # 2. 查询持仓/资金
        print("\n=== STEP 2: get_positions() ===")
        try:
            snapshot = broker.get_positions()
            print(f"[OK] cash={snapshot.cash}")
            print(f"     total_market_value={snapshot.total_market_value}")
            print(f"     holdings={dict(snapshot.holdings) if snapshot.holdings else '(空)'}")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 查询持仓失败: {e}")
            return 1

        # 3. 挂远期限价单（不成交）
        #    600000.SH 浦发银行，限价 1.00 元（远低于现价 ~10 元），不会成交
        print("\n=== STEP 3: submit_order() 远期限价单 ===")
        order = Order(
            idempotency_key=f"smoke-{int(__import__('time').time())}",
            order_id=f"smoke-{int(__import__('time').time())}",
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            side=OrderSide.BUY,
            strategy_id="smoke_test",
            symbol="600000.SH",
            limit_price=Decimal("1.00"),  # 远低于现价，不成交
        )
        try:
            broker_order_id = broker.submit_order(order)
            print(f"[OK] 下单成功 broker_order_id={broker_order_id}")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 下单失败: {e}")
            return 1

        # 4. 查询委托
        print("\n=== STEP 4: query_order() ===")
        try:
            queried = broker.query_order(broker_order_id)
            if queried is not None:
                print(f"[OK] 委托存在 status={queried.status}")
            else:
                print("[WARN] 委托查询返回 None（可能延迟，非致命）")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 查询委托失败: {e}")
            return 1

        # 5. 撤单
        print("\n=== STEP 5: cancel_order() ===")
        try:
            broker.cancel_order(broker_order_id)
            print("[OK] 撤单成功")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 撤单失败: {e}")
            return 1

        # 6. 再查委托状态（应 CANCELLED）
        print("\n=== STEP 6: query_order() 验证撤单 ===")
        try:
            final = broker.query_order(broker_order_id)
            if final is not None:
                print(f"[OK] 最终状态 status={final.status}")
            else:
                print("[WARN] 委托查询返回 None")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 查询委托失败: {e}")
            return 1

        print("\n=== 冒烟测试全部通过 ===")
        return 0

    finally:
        try:
            broker.disconnect()
            print("[INFO] 已断开连接")
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] 断开连接时出错: {e}")


if __name__ == "__main__":
    sys.exit(main())
