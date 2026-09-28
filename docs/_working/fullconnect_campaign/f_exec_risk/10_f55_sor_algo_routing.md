---
ttl: task_bound
title: "F55 执行算法路由 SOR——智能拆单/算法选择/场所选择/卖出时段路由（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F55 · 执行算法路由 SOR（D_EX_SOR，29 件 9,271 行+18 测试件）

> 上游=F41 L4-06（EXA 六件选型判据）/F46 S2-03（时段路由判据）；下游=券商通道（api/broker_api_connector）。
> 证据基线：m7 05 册+F58 姊妹卷（g lane）+本日独立复扫。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | ex_core.execution_engine 懒加载 AlgoTradingEngine+MarketContextProvider（execution_engine.py:64-66,353-411 G7 AlgoType 映射）；SorRequest weights 和=1.0 Fail-Closed |
| 下游消费 | broker_api_connector→券商；slippage_analyzer→divergence_attributor 口径复用；**生产侧零直接消费者**——唯一桥 execution_engine 自身零生产实例化（本日 grep ExecutionEngine( 仅 risk_validation_bridge.py:81 示例+demo_e2e:340 两处非生产），**传递性不可达复证** |
| 自动化触发 | 无——execution_scheduler 有类但零装配；全族无计划任务/事件总线挂接 |
| 真源与注册表 | 蓝图=docs/03_modules/_domain_ex_sor/（六子目录）；90 号 §19 v2.0.0 路由裁定（execution_route_policy.py:3-14 全文引）；sor_agent.py:22-25 查重裁定（smart_order_router 全仓不存在）|
| 门禁与质量尺 | Level 0 纯规则禁 LLM 写入；SOR 不做风控；decide 无 IO 无下单语义（replay_id 单调）；human_gated（AI_AUTONOMY 全族最高级）|
| 当前运行状态 | **红（生产不可达）/绿（代码+测试在库）**；包头注自相矛盾**本日复核仍在**：ex_sor/__init__.py:17 "规划态占位 planning stub：尚未施工" vs 实勘 core/ 11 件+18 测试件（M7-05 B1 未修）|

## 二、子模块三级枚举（本日实扫：29 件 9,271 行）

- **core**（11 件）：sor_agent.py（Agent 实体，CONSUMERS 自注"运行时装配批待兑现"）｜algo_trading_engine.py（TWAP/VWAP/POV/IS/ALT，唯一被 ex_core 引用件）｜**algo_execution_selector.py 677 行**（MOD-XS-011，回写目标——姊妹卷 F58 复证零处消费 scorer）｜execution_route_policy.py（testing，打板专用路径+防异常拆单）｜sell_session_router.py 339（MOD-XS-016，design）｜optimal_order_router.py/execution_scheduler.py/broker_adapter_manager.py/market_context_provider.py（production 头注，零装配）｜rl_exec_{boundary,contract,env}（研究域）
- **services**（5 件）：slippage_analyzer.py｜**execution_quality_scorer.py 532 行**（F58 真身，零生产装配）｜transaction_cost_optimizer.py（715 行族内最大，零装配）｜t0_cost_model.py（testing，交叉 F69）｜rl_trainer/（研究域）
- **api+根**（4 件）：broker_api_connector.py/api_rate_limiter.py（零装配）｜risk_redline.py（**错位居所**：automation 域文件居 ex_sor 根，MOD-AUTO-L6-001，M7-05 B3 未修）｜models/infrastructure/_extensions 空壳

## 三、接线四态独立复核

| 面 | 四态 | 复核证据（本日） |
|---|---|---|
| 全族生产可达性 | **未接线（传递性不可达）** | 唯一桥 execution_engine 零生产实例化（两处命中均 demo/bridge 示例）|
| L4-14→L4-06 回写 | 未接线（码缺） | selector 零 scorer 引用（姊妹卷 F58 同判）|
| 包头注实态 | **漂移未修** | __init__.py:17 planning stub 注仍与 9,271 行实装矛盾（宪法 §4.4 文档矛盾=事故）|
| risk_redline 归位 | 错居未修 | head 实锚 MOD-AUTO 编号+automation 蓝图真源 |

### 骨架勘误
总册 F55 行状态=**built**——实测生产不可达（传递性），按四要素建议改 **partial**；wiring_gap_inventory §1.4 partial 30 清单未收编 F55，二次勘误登记。总册核心模块路径列 algo_execution_selector/broker_adapter_manager——两者皆零装配，建议骨架行加注"装配缺位（传递性不可达，M7-05 B2）"。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 全族装配缺位（父域病） | 待裁二选一：①接线=execution_route_policy→assemble 进 session 执行腿（1-2 天，与 F54 缺口 1 同批）②显式 design-frozen 头注统一（0.5 天）| P0（待裁 Owner 排期）|
| 2 | F58 闭环最后一米（selector 评分输入） | 与缺口 1 同批动 session 装配层（0.5-1 天）| P1 |
| 3 | 包头注 planning stub 漂移 | 改写实态（0.5h 可施工）| P1 |
| 4 | risk_redline.py 错居 | git mv 归 automation 域走 RENAME-DEPGRAPH-SYNC 链（0.5h）| P2 |
| 5 | sell_session_router vs sell_execution_planner 分工未声明 | 蓝图分工声明（router=时段×通道；planner=理由×数量）（0.5 天）| P2 |

## 五、自审闸三态
**挖干可施工（结论修正型）**——"设计态无实装"预判不成立：代码完备+测试在册+生产装配缺位+头注漂移；缺口 3/4 本车道可修，缺口 1 挂 Owner 裁定。

## 六、复跑命令
```bash
find src/zephyr/ex_sor -name "*.py" | grep -v __pycache__ | xargs wc -l | tail -1   # 9,271
sed -n '17,19p' src/zephyr/ex_sor/__init__.py   # planning stub 漂移原文
grep -rn "ExecutionEngine(" src/zephyr scripts --include="*.py" | grep -v __pycache__ | grep -v test   # 仅 2 处非生产
grep -rn "ex_sor" src/zephyr scripts --include="*.py" | grep import | grep -v "ex_sor" | head -3   # 唯一桥
head -8 src/zephyr/ex_sor/risk_redline.py   # 错居证据
```
