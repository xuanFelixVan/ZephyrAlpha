# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] scripts.construction.test_qmt_file_bridge_e2e
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_integration; zephyr.ex_core.order_manager
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""QMT 文件桥端到端验证脚本（模拟终端）

验证链路：
  ZephyrAlpha 代码 → QmtFileBridgeBroker → 指令文件 → QMT v14 → 柜台 → 回执 → 状态同步

用法：
  1. 确保模拟终端 QMT 开着（8886156677）
  2. 确保 ZEPHYR_EXEC v14 在模型交易运行（分笔线周期）
  3. python scripts/construction/test_qmt_file_bridge_e2e.py
"""

from __future__ import annotations

import logging
import sys
import time
from decimal import Decimal

from zephyr.ex_core.adapters.qmt_file_bridge_integration import QmtFileBridgeAssembly
from zephyr.ex_core.order_manager import OrderManager
from zephyr.shared.contracts.order import Order, OrderSide, OrderType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
_logger = logging.getLogger(__name__)


def main() -> int:
    _logger.info("=" * 60)
    _logger.info("QMT 文件桥端到端验证（模拟终端）")
    _logger.info("=" * 60)

    # Step 1: 装配
    _logger.info("Step 1: 装配 QmtFileBridgeAssembly...")
    order_manager = OrderManager()
    assembly = QmtFileBridgeAssembly(
        order_manager,
        enable_real=False,   # 实盘关闭，安全
        enable_sim=True,     # 模拟开启
        sync_interval=3.0,
    )
    assembly.assemble()
    _logger.info("装配完成 broker_ids=%s", assembly.broker_ids)

    # Step 2: 连接
    _logger.info("Step 2: 连接 Broker...")
    results = assembly.connect_all()
    for broker_id, ok in results.items():
        _logger.info("连接 %s: %s", broker_id, "OK" if ok else "FAIL")
    if not all(results.values()):
        _logger.error("连接失败，退出")
        return 1

    # Step 3: 创建订单
    _logger.info("Step 3: 创建测试订单...")
    order = order_manager.create_order(
        symbol="510300.SH",
        strategy_id="e2e_test",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("4.00"),  # 远价，不成交，安全
        broker_id="qmt_sim",
    )
    _logger.info("订单创建: order_id=%s", order.order_id)

    # Step 4: 提交订单
    _logger.info("Step 4: 提交订单到文件桥...")
    broker_order_id = order_manager.submit_order(order.order_id, broker_id="qmt_sim")
    _logger.info("提交成功: broker_order_id=%s（本地 order_id，柜台 sysid 异步回填）", broker_order_id)

    # Step 5: 等待柜台同步
    _logger.info("Step 5: 等待柜台同步（最多 30 秒）...")
    max_wait = 30
    waited = 0
    while waited < max_wait:
        synced_order = order_manager.get_order(order.order_id)
        if synced_order and synced_order.broker_order_id:
            _logger.info(
                "柜台同步成功: order_id=%s broker_order_id=%s status=%s",
                synced_order.order_id, synced_order.broker_order_id, synced_order.status
            )
            break
        time.sleep(1)
        waited += 1
        if waited % 5 == 0:
            _logger.info("等待中... %d/%d 秒", waited, max_wait)
    else:
        _logger.warning("柜台同步超时（%d 秒），继续验证撤单", max_wait)

    # Step 6: 查询持仓
    _logger.info("Step 6: 查询持仓...")
    broker = assembly.get_broker("qmt_sim")
    if broker:
        snapshot = broker.get_positions()
        _logger.info(
            "持仓快照: cash=%s holdings=%d 只 total_mv=%s",
            snapshot.cash, len(snapshot.holdings), snapshot.total_market_value
        )

    # Step 7: 撤单
    _logger.info("Step 7: 撤单...")
    cancel_ok = order_manager.cancel_order(order.order_id)
    _logger.info("撤单指令: %s", "OK" if cancel_ok else "FAIL")

    # Step 8: 等待撤单确认
    _logger.info("Step 8: 等待撤单确认（最多 30 秒）...")
    waited = 0
    while waited < max_wait:
        synced_order = order_manager.get_order(order.order_id)
        if synced_order and synced_order.status.value == "CANCELLED":
            _logger.info("撤单确认: order_id=%s status=%s", synced_order.order_id, synced_order.status)
            break
        time.sleep(1)
        waited += 1
        if waited % 5 == 0:
            _logger.info("等待撤单中... %d/%d 秒", waited, max_wait)
    else:
        _logger.warning("撤单确认超时（%d 秒）", max_wait)

    # Step 9: 清理
    _logger.info("Step 9: 断开连接...")
    assembly.disconnect_all()

    _logger.info("=" * 60)
    _logger.info("端到端验证完成")
    _logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
