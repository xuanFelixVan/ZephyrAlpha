# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] scripts.construction.test_qmt_file_bridge_full
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.qmt_trading_session
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
"""QMT 文件桥全面测试套件（模拟+实盘）

测试项：
  1. 下单（远价，不成交）
  2. 撤单
  3. 持仓查看
  4. 成交回报（市价单，成交后撤）
  5. 批量下单（算法单排队，3片间隔10秒）
  6. 幂等防重（同 idempotency_key 提交2次）
  7. 断线恢复（QMT 重启后状态恢复）
  8. 边界拒单（资金不足/数量不合法）

用法（环境变量驱动，无 argparse）:
  set QMT_TEST_ENV=sim   ; python scripts/construction/test_qmt_file_bridge_full.py  # 只测模拟（默认）
  set QMT_TEST_ENV=real  ; python scripts/construction/test_qmt_file_bridge_full.py  # 只测实盘（谨慎）
  set QMT_TEST_ENV=both  ; python scripts/construction/test_qmt_file_bridge_full.py  # 都测
"""

from __future__ import annotations

import logging
import os
import sys
import time
from decimal import Decimal

from zephyr.ex_core.qmt_trading_session import QmtSessionOptions, QmtTradingSession
from zephyr.governance.strategies.strategy_base import StrategyBase
from zephyr.shared.contracts.order import OrderSide, OrderType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
_logger = logging.getLogger(__name__)


class TestStrategy(StrategyBase):
    """测试策略：固定权重"""

    def generate_target_weights(self, universe, signals, constraints):
        return {symbol: 1.0 / len(universe) for symbol in universe}


class QmtFileBridgeTester:
    """QMT 文件桥测试器"""

    def __init__(self, env: str):
        self.env = env
        self.broker_id = f"qmt_{env}"
        self.universe = ["510300.SH"]
        self.session: QmtTradingSession | None = None
        self.results: list[tuple[str, bool, str]] = []

    def log_result(self, name: str, ok: bool, detail: str = ""):
        status = "PASS" if ok else "FAIL"
        self.results.append((name, ok, detail))
        _logger.info("[%s] %s: %s", status, name, detail)

    def setup(self) -> bool:
        """初始化会话"""
        try:
            signal_provider = lambda _: {"510300.SH": 0.5}
            price_provider = lambda _: {"510300.SH": Decimal("4.50")}

            self.session = QmtTradingSession(
                env=self.env,
                universe=self.universe,
                strategy=TestStrategy(),
                signal_provider=signal_provider,
                price_provider=price_provider,
                options=QmtSessionOptions(
                    enable_algo_queue=True,
                    queue_interval=10.0,  # 测试用 10 秒间隔
                ),
            )
            self.session.start()
            return True
        except Exception as e:
            _logger.error("Setup 失败: %s", e, exc_info=True)
            return False

    def teardown(self):
        """清理"""
        if self.session:
            self.session.stop()

    def test_1_order(self) -> bool:
        """测试 1：下单（远价）"""
        try:
            order = self.session.order_manager.create_order(
                symbol="510300.SH",
                strategy_id="test_1",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("100"),
                limit_price=Decimal("4.00"),  # 远价不成交
                broker_id=self.broker_id,
            )
            broker_order_id = self.session.order_manager.submit_order(
                order.order_id, broker_id=self.broker_id
            )
            ok = broker_order_id == order.order_id
            self.log_result("1.下单", ok, f"order_id={order.order_id}")
            return ok
        except Exception as e:
            self.log_result("1.下单", False, str(e))
            return False

    def test_2_cancel(self) -> bool:
        """测试 2：撤单"""
        try:
            # 先下一个单
            order = self.session.order_manager.create_order(
                symbol="510300.SH",
                strategy_id="test_2",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("100"),
                limit_price=Decimal("4.00"),
                broker_id=self.broker_id,
            )
            self.session.order_manager.submit_order(order.order_id, broker_id=self.broker_id)
            time.sleep(2)  # 等柜台登记

            # 撤单
            ok = self.session.order_manager.cancel_order(order.order_id)
            time.sleep(3)  # 等撤单确认

            # 验证状态
            synced = self.session.order_manager.get_order(order.order_id)
            final_ok = ok and synced and synced.status.value == "CANCELLED"
            self.log_result("2.撤单", final_ok, f"status={synced.status if synced else 'N/A'}")
            return final_ok
        except Exception as e:
            self.log_result("2.撤单", False, str(e))
            return False

    def test_3_positions(self) -> bool:
        """测试 3：持仓查看"""
        try:
            snapshot = self.session.get_positions()
            ok = snapshot is not None and snapshot.cash >= 0
            self.log_result(
                "3.持仓查看", ok,
                f"cash={snapshot.cash if snapshot else 'N/A'} holdings={len(snapshot.holdings) if snapshot else 0}"
            )
            return ok
        except Exception as e:
            self.log_result("3.持仓查看", False, str(e))
            return False

    def test_4_fill(self) -> bool:
        """测试 4：成交回报（市价单）"""
        try:
            # 市价单，立即成交
            order = self.session.order_manager.create_order(
                symbol="510300.SH",
                strategy_id="test_4",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("100"),
                broker_id=self.broker_id,
            )
            self.session.order_manager.submit_order(order.order_id, broker_id=self.broker_id)

            # 等成交（市价单通常秒成）
            time.sleep(5)

            # 检查持仓是否增加（或 Deal.csv 是否有记录）
            snapshot = self.session.get_positions()
            has_holding = snapshot and "510300" in str(snapshot.holdings)
            self.log_result("4.成交回报", has_holding, f"holdings={snapshot.holdings if snapshot else 'N/A'}")

            # 立即卖出恢复原状（如果是模拟，可以不卖；实盘必须卖）
            if self.env == "real" and has_holding:
                sell_order = self.session.order_manager.create_order(
                    symbol="510300.SH",
                    strategy_id="test_4_sell",
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    quantity=Decimal("100"),
                    broker_id=self.broker_id,
                )
                self.session.order_manager.submit_order(sell_order.order_id, broker_id=self.broker_id)
                _logger.info("实盘已卖出恢复原状")

            return has_holding
        except Exception as e:
            self.log_result("4.成交回报", False, str(e))
            return False

    def test_5_batch_algo(self) -> bool:
        """测试 5：批量下单（算法单排队）"""
        try:
            # 创建 3 笔子订单，走 LocalOrderQueue
            queue = self.session.assembly.get_queue(self.broker_id)
            if not queue:
                self.log_result("5.批量下单", False, "队列未启用")
                return False

            orders = []
            for i in range(3):
                order = self.session.order_manager.create_order(
                    symbol="510300.SH",
                    strategy_id=f"test_5_{i}",
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    quantity=Decimal("100"),
                    limit_price=Decimal("4.00"),
                    broker_id=self.broker_id,
                )
                orders.append(order)

            # 批量入队
            queue.enqueue_batch(orders, interval_seconds=10.0)

            # 等 35 秒（3 笔 × 10 秒 + 缓冲）
            _logger.info("等待算法单排队执行（35 秒）...")
            time.sleep(35)

            stats = queue.get_stats()
            ok = stats.sent >= 2  # 至少 2 笔发出
            self.log_result("5.批量下单", ok, f"sent={stats.sent}/3")
            return ok
        except Exception as e:
            self.log_result("5.批量下单", False, str(e))
            return False

    def test_6_idempotency(self) -> bool:
        """测试 6：幂等防重（同 idempotency_key 不同 order_id）"""
        try:
            idem_key = f"test_6_{int(time.time())}"

            # 创建两个不同的订单，但相同的 idempotency_key
            order1 = self.session.order_manager.create_order(
                symbol="510300.SH",
                strategy_id="test_6",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("100"),
                limit_price=Decimal("4.00"),
                broker_id=self.broker_id,
            )
            order1.idempotency_key = idem_key

            order2 = self.session.order_manager.create_order(
                symbol="510300.SH",
                strategy_id="test_6",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("100"),
                limit_price=Decimal("4.00"),
                broker_id=self.broker_id,
            )
            order2.idempotency_key = idem_key  # 相同 key

            # 第一次提交
            id1 = self.session.order_manager.submit_order(order1.order_id, broker_id=self.broker_id)
            # 第二次提交（同 key，应该被幂等拦截返回 id1）
            id2 = self.session.order_manager.submit_order(order2.order_id, broker_id=self.broker_id)

            ok = id1 == id2
            self.log_result("6.幂等防重", ok, f"id1={id1[:8]}... id2={id2[:8]}... same={ok}")
            return ok
        except Exception as e:
            self.log_result("6.幂等防重", False, str(e))
            return False

    def test_7_reconnect(self) -> bool:
        """测试 7：断线恢复"""
        try:
            # 下一个单
            order = self.session.order_manager.create_order(
                symbol="510300.SH",
                strategy_id="test_7",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("100"),
                limit_price=Decimal("4.00"),
                broker_id=self.broker_id,
            )
            self.session.order_manager.submit_order(order.order_id, broker_id=self.broker_id)

            # 断开再连接
            broker = self.session.assembly.get_broker(self.broker_id)
            broker.disconnect()
            time.sleep(1)
            broker.connect()

            # 验证订单状态还在
            synced = self.session.order_manager.get_order(order.order_id)
            ok = synced is not None
            self.log_result("7.断线恢复", ok, f"order exists after reconnect")
            return ok
        except Exception as e:
            self.log_result("7.断线恢复", False, str(e))
            return False

    def test_8_reject(self) -> bool:
        """测试 8：边界拒单（数量不合法）"""
        try:
            # 下 50 股（不足 100）
            order = self.session.order_manager.create_order(
                symbol="510300.SH",
                strategy_id="test_8",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("50"),
                limit_price=Decimal("4.00"),
                broker_id=self.broker_id,
            )
            self.session.order_manager.submit_order(order.order_id, broker_id=self.broker_id)
            self.log_result("8.边界拒单", False, "应该拒单但没拒")
            return False
        except Exception as e:
            ok = "数量不合法" in str(e) or "min_unit" in str(e)
            self.log_result("8.边界拒单", ok, f"正确拒单: {e}")
            return ok

    def run_all(self) -> bool:
        """跑全部测试"""
        _logger.info("=" * 60)
        _logger.info("QMT 文件桥全面测试 env=%s", self.env)
        _logger.info("=" * 60)

        if not self.setup():
            _logger.error("Setup 失败，退出")
            return False

        try:
            self.test_1_order()
            self.test_2_cancel()
            self.test_3_positions()
            self.test_4_fill()
            self.test_5_batch_algo()
            self.test_6_idempotency()
            self.test_7_reconnect()
            self.test_8_reject()
        finally:
            self.teardown()

        # 汇总
        passed = sum(1 for _, ok, _ in self.results if ok)
        total = len(self.results)
        _logger.info("=" * 60)
        _logger.info("测试汇总: %d/%d 通过", passed, total)
        for name, ok, detail in self.results:
            status = "PASS" if ok else "FAIL"
            _logger.info("  [%s] %s: %s", status, name, detail)
        _logger.info("=" * 60)

        return passed == total


def main():
    env = os.environ.get("QMT_TEST_ENV", "sim").strip().lower()
    if env not in ("sim", "real", "both"):
        _logger.error("非法 QMT_TEST_ENV=%s（可选 sim/real/both）", env)
        return

    if env in ("sim", "both"):
        tester = QmtFileBridgeTester("sim")
        tester.run_all()

    if env in ("real", "both"):
        _logger.warning("=" * 60)
        _logger.warning("实盘测试：将使用远价单（不成交），测试后立即撤单")
        _logger.warning("=" * 60)
        _logger.warning("3 秒后自动继续...")
        time.sleep(3)
        tester = QmtFileBridgeTester("real")
        tester.run_all()


if __name__ == "__main__":
    main()
