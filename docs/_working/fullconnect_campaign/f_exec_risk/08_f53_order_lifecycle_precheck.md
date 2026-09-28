---
ttl: task_bound
title: "F53 订单生命周期与预检——订单状态机/订单级预检/部分成交撤改/价格笼子（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F53 · 订单生命周期与预检（ex_core 订单域核心）

> 上游=F41 L4/F46 S2（供单）；下游=F56 QMT 桥（落地）、F57 结算对账、execution_report→D_REPORTING。
> 证据基线：m7 04/06 册+本日（09-27）独立复扫。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | TradingSession.rebalance（trading_session.py:514→_compute_order_deltas:636→_build_order:738→_validate_and_submit:758，四道闸 :908/:942/:979/:1124）；S1/S2 卖出计划 |
| 下游消费 | broker.submit_order→QMT 桥；Fill→_on_fill（order_manager.py:531）→fill_callbacks；ExecutionReport（CTR-P1-007 frozen）→D_REPORTING；audit_journal→operational_risk_monitor |
| 自动化触发 | rebalance 事件触发（ex_core.rebalance.requested，B4 治本删 Timer）；eod 15:40 槽内 expire_open_orders 日终未成交转 EXPIRED |
| 真源与注册表 | 蓝图=docs/03_modules/_domain_execution_core/（blueprint+algo_flow 机生）；包入口=MOD-L06-001（ex_core 56 件本日 ls 复证）；订单契约=shared/contracts/order+order_enums.py 63 行 |
| 门禁与质量尺 | VALID_TRANSITIONS 白名单（order_manager.py:136-150，非法转换 ValueError）；Saga 六步严格序+补偿幂等；幂等键 sha256（:267-272）；整手/价格笼子预校验（双 broker 消费）|
| 当前运行状态 | **黄**——主链（rebalance→delta→提交→成交→报告）sim 实弹绿（09-23 卖腿实证）；precheck 四级闸已接线（start_paper_session.py:565 attach_pre_execution_gate 本日实锚）； Saga 双编排+合规门零注入两 P0 在案 |

## 二、子模块三级枚举（本日实扫 wc -l）

- **订单生命周期面**：order_manager.py 595（create/submit/transition/cancel/on_fill/expire/拒单分类）｜order_enums.py 63（**码面 7 态** PENDING/SUBMITTED/PARTIAL/FILLED/CANCELLED/REJECTED/EXPIRED+封闭转换表）｜order_execution_saga.py 894（六步 Saga+补偿+超时恢复，**零生产调用方**——M7-04 B1 本班 grep 独立复证）｜fill_handler.py 499（已接线 run_post_settlement:273,429）｜async_fill_dispatcher（paper 必装配）｜cancel_rate_guard.py 295（500 完结窗/12% 警/15% 冻/15 笔秒限/5000 警 1 万阻）
- **预检面**：pre_execution_checker.py 351（闸 1 kill_switch_gate :243/:252→闸 1.5 live_env_gate :272→闸 2 session_window_gate :286/:295→闸 3 snapshot_gate :309→闸 4 verdict.rule_id :321——**check_id 族本日实锚**）
- **微结构守卫**：price_cage.py 264+board_lot+pricing_policy+corporate_action_adjuster（production 已接线经 qmt broker 预校验 :524-545，M7-01 实锚）
- **节流**：local_order_queue.py 271（已接线 integration:165）

## 三、接线四态独立复核

| 面 | 四态 | 复核证据（本日） |
|---|---|---|
| precheck 四级闸 | 已接线 | start_paper_session.py:565 kill_switch_probe 注入实锚 |
| 订单状态机 | built（7 态） | order_enums.py:52-63+order_manager :136-150 |
| Saga 编排 | **码成闸空** | OrderExecutionSaga( 生产调用零命中；TradingSession 走自有直连路径——双编排待裁（M7-04 B1：①session 切 Saga 重/②显式降级 Saga 为参照实现轻）|
| 合规门注入 | **零注入** | OrderManager( 全仓 6 处裸构造本日复证：qmt_trading_session:115/integration:52/app_panel:524/start_paper_session:492/demo_e2e:326/smoke:230——report_gate/declaration_guard/manipulation_monitor 三参全 None（归 F62 P0，交叉登记）|

### 骨架勘误
总册 F53 行"订单级预检"判据散文"五查"（资金/持仓/熔断/禁做/笼子）vs 码面 check_id 四 gate 族+rule_id——口径漂移在 f41 册 §三已登记（禁做清单入口待核），维持。无新勘误。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | Saga vs TradingSession 双编排并存（Saga 安全语义不在直连路径） | 二选一待裁：①session 切 Saga（2-3 天）②降级 Saga 为参照实现+头注声明（0.5 天）| P0（待裁）|
| 2 | 券商九态→码面 7 态映射桥缺失 | 桥层补映射表 1 天（f41 册堵点 1 同件）| P1 |
| 3 | 6 处 OrderManager 裸构造=合规门零注入 | F62 施工批（Owner 报送先行+同批注入）| P0（归 F62）|
| 4 | app_panel:524 第三只裸实例（订单数据三面分裂） | 面板改只读消费 live_portfolio（0.5 天）| P1 |
| 5 | 零消费者件群（aggregate_root_manager/repository_interface/performance_monitor） | 内收季度审计处置 | P2 |

## 五、自审闸三态
**挖干可施工**（订单全流转 file:line 实证；54 测试件 tests/ex_core/ 在册；两 P0 均有明确处置序与归属；本车道可修项=4/5）。

## 六、复跑命令
```bash
sed -n '136,150p' src/zephyr/ex_core/order_manager.py          # 状态机白名单
grep -rn "OrderManager(" src/zephyr scripts --include="*.py" | grep -v __pycache__ | grep -v test   # 6 处裸构造
grep -rn "OrderExecutionSaga(" src/zephyr scripts --include="*.py" | grep -v __pycache__ | grep -v test   # 零生产调用
sed -n '565,566p' scripts/start_paper_session.py               # precheck 注入锚
wc -l src/zephyr/ex_core/order_manager.py src/zephyr/ex_core/pre_execution_checker.py src/zephyr/ex_core/order_execution_saga.py
```
