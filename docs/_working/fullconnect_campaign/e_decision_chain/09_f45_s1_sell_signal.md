---
ttl: task_bound
title: F45 S1 卖出信号收集评分——全流通挖干案卷（矿道 L05）
session: zc-l05-20260927
creation_token: fc-f45-s1-sellsig-20260927
---

# F45 S1 卖出信号收集评分——挖干案卷

> 一句话：六桶分类收集→止损族/止盈族/破位退潮族并行判定→融合紧迫度评分→强制清仓绕过通道，产出"卖不卖+多急"。节点组=TDM-X-S1+01..06 共 7 节点（今日 yaml:3112-3497 机数=7，零漂移）。总册 built｜**P0**｜T7；上游 P1-04/P1-06/P2/L1-AGG/L9-V1/V2（T-1 快照时间分层铁律），下游 X-S2。
> **本卷核心发现（册引+今日双源复核）：S1 全族纯库挂机——`from zephyr.sell_decision` 包外零消费者，全部 auto 语义空转，离场实际靠人。**

## 一、六向台账（实证锚点）

| 向 | 内容（锚点） |
|---|---|
| ①上游输入 | P1-04 风险否决/P1-06 动作清单/P2（sequence）；L1-AGG 六段（distribution+情绪票加权）；L9-V1/V2 T-1 快照 |
| ②数据原料 | 8 类信号源（六桶=risk/signal/target/trailing/time/volatility，42 号 7 类归并 §2.29 D61）；Chandelier 双区参数（亏 N=10/M=3.0，盈 N=22/M=2.0）；龙虎榜 T-1 PIT 纪律（M-43） |
| ③状态输出 | 六桶分类+triage 三档扫描频率（D104 终裁：WATCH 秒级/MONITOR 1min/HOLD 5min）+紧迫度三档（>0.8 立即市价/0.5-0.8 分批/<0.5 等确认）+确认层三段式 triggered→confirmed→released（D69 分桶确认） |
| ④下游消费 | S1-05/S1-06→S2-01；**与 X-R1 分工=R1 管组合熔断、S1-06 管单仓强清**（四触发：KillSwitch 组合级/黑天鹅/K≥3 连续破位失败/主力弃庄→紧迫度 1.0 直送不经过融合仲裁） |
| ⑤自动化触发 | **零**——册引 2026-09-25 独立复核+xflow 批报告 L35 双源一致；今日第三源 grep 复核成立（包外零命中） |
| ⑥缺口债 | 棘轮 clamp"调用方持久化"悬空（D50）；UP-2 前瞻概率止损 trial；游资红线 2% 移 S2-06；MOD-RK-09 A股六模式引擎 38 测试全绿零接线；X 流 18 节点验证全 pending（VAL-20260909-164042） |

## 二、子模块三级枚举（2026-09-27 实扫）

- 域 `src/zephyr/sell_decision/core/`（22 件实扫）。S1 挂点 5/5 今日实锚（yaml sed）：sell_signal_collector.py（S1-01）、stop_loss_strategy.py（S1-02）、take_profit_strategy.py（S1-03）、breakout_failure_detector.py（S1-04）、sell_signal_fusion_engine.py（S1-05）；**S1-06 挂点=src/zephyr/trading/strategy_abnormal_exit_orchestrator.py（396 行今日 wc 实锚，不在 sell_decision 域——见勘误 1）**。
- 协同件（sell_decision/core 其余）：position_triage.py（P1-02 跨域挂载）、sell_urgency_scorer.py、exit_scenario_planner.py、scaling_out.py/scaling_out_architect.py、sell_execution_planner.py（S2 交界）、sell_execution_quality_tracker.py、trade_level_circuit_breaker.py（连亏熔断已落码）、sell_conflict_arbitrator.py、stop_hunting_protector.py、strategy_specific_stop_framework.py、replacement_rebalance_seller.py、sell_signal_accuracy_monitor.py、sell_signal_scorer.py、sell_strategy_ab_tester.py。
- 测试面：tests/sell_decision/（册引在盘）；消融对照器 ablation.py 已建成但 run_ablation 零生产调用（册引 §五-2）。

## 三、接线四态独立复核（2026-09-27）

| 件 | 四态判定 | 独立证据 |
|---|---|---|
| S1-01..05 判定库 | **纯库挂机** | 今日 grep `from zephyr.sell_decision` 包外零命中（第三源复核成立）；12 核心文件全在盘+测试在盘（册引） |
| S1-06 强清绕过 | **红节点（编排缺）** | 四触发中 KillSwitch 组合级边已画，黑天鹅/K≥3/主力弃庄触发源在码但无扫描循环（册引 §五-3）；yaml activation=continuous 今日实锚 |
| KillSwitch 联动 | **横切接线（唯一活线）** | F47 R1 kill_switch 三实例族独立在岗（总册 F61 built P0）；EMERGENCY 态联动 ashare_stop_loss_engine :105（册引） |
| 回测面 | **未接入** | SellSignal 流未接入回测=消融动作标注无法自动生成；X 流 18 节点验证全 pending（册引双源） |

**骨架勘误（登记待 D 线）**：
1. **F45 册 §四"12 核心文件"清单中 strategy_abnormal_exit_orchestrator(396) 未标域路径**：该件实际在 src/zephyr/trading/（今日 ls 实证，sell_decision/core/ 无此件）；TDM S1-06 module_ref=src/zephyr/trading/strategy_abnormal_exit_orchestrator.py（yaml 今日 sed 实锚）正确。册面"sell_decision 域 9 个 production 模块锚定"易误读为该件亦在 sell_decision 域——引用时须带全路径。
2. **总册 F45 状态"built"降格建议**：判定库实件面 built 成立，但全族零生产消费+18 节点验证全 pending——实际四态="实件 built/编排 missing/验证 pending"三态叠加，P0 分级（总册）与"离场靠人"现状并读=全流通咽喉位。建议总册行加注（同 F42/F43/F44 处置路径，裁-5 同窗）。
3. S1-06 与 X-R1 分工表述双真源风险：S1-06 管"单仓强清"、R1 管"组合熔断"——两卷口径一致（本卷+f47 归 R 卷），登记防后续漂移。

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G45-1 | S1 全族零消费（含 F42 G42-2 转离场评估待接线） | 立"S1 信号扫描编排"工单挂 continuous 节拍先 paper 档（3-5 天）；与 P1-02 position_triage 共享一个扫描循环（D104 已统一口径）防两套 ticker | **P0** |
| G45-2 | X 流 18 节点验证全 pending | 消融对照器已建成，实弹待 Owner 放行（§12）；SellSignal 流接入回测解锁消融标注 | **P0** |
| G45-3 | 棘轮 clamp"调用方持久化"悬空 | 随 G45-1 编排落地指定持久化宿主 | P1 |
| G45-4 | MOD-RK-09 A股六模式引擎零接线 | P1-04 消费缺位（TD-A P1 面），联动登记不越权催接线 | P2 |
| G45-5 | UP-2 trial 通道+游资红线 S2-06 移交 | 维持登记态 | P2 |

## 五、自审闸三态

**挖干可施工**（血肉/模块/三源零消费实证/验证欠账全链登记；P0 双缺口有现成修法与共享设计约束）。

### 待裁
- S1-06 黑天鹅/主力弃庄触发的扫描循环载体（并入 G45-1 编排 vs 独立守护件）——编排工单设计点。
- RL 执行/前瞻概率止损启用时点——Owner 门。

## 六、复跑命令

```bash
grep -rln "from zephyr.sell_decision" src/zephyr scripts --include="*.py" | grep -v __pycache__ | grep -iv sell_decision  # 空输出=零外部消费
grep -c "node_id: TDM-X-S1" config/trading_decision_map.yaml   # =7
sed -n '3465,3484p' config/trading_decision_map.yaml            # S1-06 module_ref=trading/ 域
ls src/zephyr/trading/strategy_abnormal_exit_orchestrator.py    # 在盘
sed -n '28,40p' docs/_working/2026-09-10-xflow-batch-report.md  # 18 行 pending 台账
```
