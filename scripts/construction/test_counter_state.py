# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] scripts.construction.test_counter_state
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_broker
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""测试柜台全量镜像（施工期验证脚本：文件桥上线验收后归档，需模拟终端导出路径已配置）"""
import time
from zephyr.ex_core.adapters.qmt_file_bridge_broker import QmtFileBridgeBroker

broker = QmtFileBridgeBroker(env="sim", sync_interval=1.0)
broker.connect()

# 等 3 秒让同步线程跑一轮
time.sleep(3)

print("=== 柜台全量镜像 ===")
print(f"所有挂单: {len(broker.get_all_counter_orders())} 笔")
for remark, o in broker.get_all_counter_orders().items():
    print(f"  {remark}: {o['symbol']} {o['side']} {o['qty']}@{o['price']} status={o['status']}")

print(f"\n所有持仓: {len(broker.get_counter_positions())} 只")
for symbol, p in broker.get_counter_positions().items():
    print(f"  {symbol}: 拥股={p['qty']} 可卖={p['available_qty']} 冻结={p['frozen_qty']} 市值={p['market_value']}")

print(f"\n资金: {broker.get_counter_account()}")
print(f"可用资金: {broker.get_available_cash()}")
print(f"510300 可卖: {broker.get_available_qty('510300')}")
print(f"510300 在途买单: {broker.get_pending_orders_count('510300', 'buy')}")

print(f"\n当日成交: {len(broker.get_counter_deals())} 笔")
for d in broker.get_counter_deals()[-3:]:
    print(f"  {d['remark']}: {d['symbol']} {d['side']} {d['qty']}@{d['price']}")

broker.disconnect()
print("\n=== 测试完成 ===")
