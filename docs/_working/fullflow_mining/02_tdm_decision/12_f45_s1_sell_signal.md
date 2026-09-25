---
ttl: task_bound
title: F45 S1 卖出信号收集评分——TDM 离场流 S1 环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52）
---

# F45 S1 卖出信号收集评分（TDM-X-S1 + S1-01..06）

> **一句话**：六桶分类收集→止损族/止盈族/破位退潮族并行判定→融合紧迫度评分→强制清仓绕过通道，产出"卖不卖+多急"。
> **上游**：P1-04 风险否决/P1-06 动作清单/P2（sequence）、L1-AGG 六段。**下游**：X-S2 离场执行（sequence+feed）。

## 一、环节定义与边界
- 树 6 节点：S1-01 收集分类→{S1-02 止损族/S1-03 止盈族/S1-04 破位情绪}→S1-05 融合评分；S1-06 强清绕过通道并行（42 号 §3.2 最高优先级）。
- 42 号卖出流 spec 十节吸收完成；sell_decision 域 9 个 production 模块锚定。**全族纯库挂机（见三向台账）是本册核心发现**。

## 二、状态机血肉
| 节点 | 判定轴 | 离散状态/规则 |
|------|--------|--------------|
| S1-01 收集与六桶分类 | 8 类信号源聚合去重 | 六桶=risk/signal/target/trailing/time/volatility（42 号 7 类归并，§2.29 D61）；分类决定判定链+确认模式；triage 三档定扫描频率（D104 终裁：WATCH 秒级/MONITOR 1min/HOLD 5min） |
| S1-02 止损族 | 五路并行+棘轮 | Chandelier 双区（亏损区 N=10/M=3.0，盈利区 N=22/M=2.0；ATR 缺失降级锚=max(最高收盘,入场价)，rpt_e03 修悬崖）+固定 -7% 生死线+支撑破位双触发（D91：硬底 -7%~-8% 或 2×ATR 立即走+软确认次日 30min 观察窗；同层多档取最严）+时间止损（盈利仓 5 日不涨/亏损仓 3 日）+分时破位（跌破分时均线 30min）；**止损只升不降**（棘轮 clamp=D50 欠账"调用方持久化"——调用方不存在，悬空）；UP-2 前瞻概率止损建议通道（DAL-FWD-STOP trial，P(跌)≥0.65 阈值冻结，评审非强制）；游资红线 2% 不进触发器（移 S2-06 复盘对照）；A股六模式引擎 MOD-RK-09 零生产消费（地图不越权催接线） |
| S1-03 止盈族 | 三式 | 移动止盈（Chandelier 盈利区 2×ATR）+峰值回撤（peak_pnl 回落 30% 兑现，D50 落位）+目标位（打板票=次日不板走）；只看市场状态变量不看连赢次数（D57） |
| S1-04 破位与情绪退潮 | 三路 | 突破失败（连冲 3 次失败→强清喂 S1-06）+情绪退潮（L1 六段 distribution+情绪票→加权卖出）+龙虎榜派发（五规则，PIT 纪律 M-43：只用 T-1 及更早榜）；D68 必改：除权除息日分母改除权参考价；D69：假破位（盘中破收盘收回=洗盘持有加分）+时段可靠性（9:30-10:00 假信号高发从严）；D99 终裁：天地板改个股级（板块家数规则实证证伪） |
| S1-05 融合与紧迫度 | 加权 0~1+确认层 | 桶权重 止损 0.9/破位 0.7/止盈 0.5+多周期共振+0.2；紧迫度三档 >0.8 立即市价/0.5-0.8 分批/<0.5 等确认；D69 确认层三段式 triggered→confirmed→released，分桶确认（risk/time/volatility=immediate，signal/target/trailing=close_confirm）；去抖三参数（confirm_bars∈{0,1}/buffer 0.2-0.5%/量能≥20日均量 1.5×）；**去抖与强清互斥** |
| S1-06 强制清仓绕过 | 四触发任一 | 风控 KillSwitch（组合级）/黑天鹅（立案暴雷）/K≥3 连续破位失败/主力弃庄→紧迫度 1.0 直送 S2-01，不经过融合仲裁；与 X-R1 分工=R1 管组合熔断、本节点管单仓强清；连亏熔断已落码=trade_level_circuit_breaker.py；红节点（编排缺口）；回测 V1 声明不含黑天鹅/主力弃庄分支（M-50 无可计算代理） |

## 三、六向台账
- **上游输入**：P1-04/P1-06/P2 三条 feed、L1-AGG 状态、L9-V1/V2 T-1 快照（时间分层铁律）。
- **下游消费**：S1-05/S1-06→S2-01。
- **自动化触发**：**零——`from zephyr.sell_decision` 全仓 grep 仅包内自引，包外零消费者**（本册 2026-09-25 独立复核 + xflow 批报告 L35 双源一致）。
- **真源与注册表**：trading_decision_map.yaml:3298-3497；42 号卖出流（archive memos 在档）；RLM-DRAWDOWN-001/002/006；MOD-SELL-000/001/003/004/005/007/015/018 家族。
- **门禁与质量尺**：ai_autonomy S1-01..06 全 auto（但无调用方，auto 语义空转）。
- **当前运行状态**：**红（未运行）**——12 个核心文件 327/254/131/294/426/396 行等全部在盘、测试在盘（tests/sell_decision/），零生产调用。

## 四、子模块清单（核心 12 件全部实测在盘）
sell_signal_collector(327)/stop_loss_strategy(254)/take_profit_strategy(131)/breakout_failure_detector(294)/sell_signal_fusion_engine(426)/strategy_abnormal_exit_orchestrator(396)/position_triage(202)/sell_urgency_scorer(317)/exit_scenario_planner(208)/scaling_out(165)/sell_execution_quality_tracker(210)/trade_level_circuit_breaker（sell_decision/core/ 下，非 src/zephyr/trading/）。

## 五、堵点与病灶
1. **S1 全族零消费**（根因=42 号 spec 落码了判定库但编排体从未立项；后果：全部 auto 语义空转、棘轮 clamp 悬空、离场靠人；修法：立"S1 信号扫描编排"工单挂 continuous 节拍，先 paper 档；量级 3-5 天；本车道可修）。
2. **X 流 18 节点验证全 pending**（VAL-20260909-164042，exit_counterfactual+insufficient_samples；消融对照器 ablation.py 已建成但 run_ablation 零生产调用方，实弹待 Owner 放行 §12；SellSignal 流未接入回测=消融动作标注无法自动生成）。
3. **S1-06 编排缺口**（四触发中 KillSwitch 组合级边已画，黑天鹅/K≥3/主力弃庄触发源在码但无扫描循环）。
4. **MOD-RK-09 A股六模式引擎 38 测试全绿零接线**（P1-04 消费缺位属 TD-A P1 面，此处仅登记联动）。

## 六、提速与合并机会
S1-01 收集器与 P1-02 position_triage 共享分级频率表（D104 已统一口径）——编排工单应共用一个扫描循环而非两套 ticker；sell_signal_accuracy_monitor(163) 与 S2-06 quality_tracker 互补勿重复建。

## 七、自审闸三态
**挖干可施工**（血肉/模块/双源零消费实证/验证欠账全链登记）。

## 八、复核命令
```bash
grep -rln "from zephyr.sell_decision" src/zephyr scripts --include="*.py" | grep -v __pycache__ | grep -iv sell_decision   # 空输出=零外部消费
grep -n "node_id: TDM-X-S1" config/trading_decision_map.yaml
sed -n '28,40p' docs/_working/2026-09-10-xflow-batch-report.md   # 18 行 pending 实弹台账
```
