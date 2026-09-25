---
ttl: task_bound
title: F43 P2 做T与加减仓——TDM 持仓流 P2 环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52，前半 F37-F42 归 TD-A）
---

# F43 P2 做T与加减仓（TDM-P-P2 + P2-01..04）

> **一句话**：底仓上做T降成本（不改变底仓股数）+两路减仓再平衡；资格三道门→三策略调度→闭环判定，减仓并行。
> **上游**：P1-06 体检动作清单（可做T/可加仓/减仓）、P1-04 风险否决（冻结做T资格）、L1-AGG 六段（状态门）、X-R1（熔断停做T）。**下游**：P3-01 加仓资格、X-S2 离场执行、F-C3-01 归因（做T统计）。

## 一、环节定义与边界
- 做T=在底仓上高抛低吸赚差价，与加减仓是三件事（做T 不改底仓股数）。树 4 节点（P2-01 资格→P2-02 调度→P2-03 闭环；P2-04 减仓再平衡并行）。
- 冲突优先级（D44）：风控减仓 > 做T收口 > 做T新开（收口 BM-SELL-06 deprecated；schema v1.8 候选字段化，当前以 yaml 注释承载）。

## 二、状态机血肉（判定用离散状态机，D108）
| 节点 | 判定轴 | 离散状态/规则 |
|------|--------|--------------|
| P2-01 资格与成本前置 | 五道门（外审 R2-08 对齐） | 状态门（仅 accumulation/expansion 开做T，L1-AGG 直喂）+标的质量门（20 日均振幅≥3%）+成本门（D111 终裁绝对金额制：s*(N)=来回费用÷N+滑点余量，单笔下限 N_floor≈5.86 万@万0.854）+风险否决冻结（P1-04）+熔断停做T（X-R1）。invalidation：盘中转单边→当日资格全作废 |
| P2-02 策略调度 | 三策略并发+仲裁 | 冲高回落/盘口失衡/VWAP 回归三策略；单次≤底仓 30%；方向术语=buy-first/sell-first（D41）；D58 欠账：双轨止损（价差 0.3-0.5%+时间止损）、sell-first 复原铁律（禁 T+0 变 T+1 加仓）、连败 2 笔熔断、主策略减仓优先于做T overlay |
| P2-03 闭环判定 | 每 5min 核对+14:50 冠军规则 | 14:50 未闭环无条件平敞口；成功=收盘股数不变+总成本降；跨窗（m-13）：14:50 强平单 14:55 未成交深市留竞价/沪市 14:56 前撤改重挂，次日复原性卖单豁免禁开新T（m-22）；D50 欠账：做T配对核算器+底仓复原语义+笔数偏差熔断 |
| P2-04 减仓与再平衡 | 两路触发+划算判据 | P1-05 漂移越带 + 置换（新标的预期收益>现持仓 1.5×）；减多少=回目标权重；划算=改善>2×交易成本；D55 欠账：隔夜资格门（14:30-14:57 逐仓判定）+隔夜风险预算二维表+节前决策表；减仓执行不迟于 14:55（m-21） |

## 三、六向台账
- **上游输入**：P1-06 动作清单（edge P1-06→P2-01/P3-01 daily）、L1-AGG 状态（broadcast daily）、X-R1 中断（broadcast）。
- **下游消费**：P2-03 统计→F-C3-01；P2-04→X-S2-01；P2-03→X-S2-01（强平）。
- **自动化触发**：**无任何计划任务/daemon 调用 t_trade_coordinator/t0_trading_pipeline**（grep src+scripts 零命中；t1_sellable 例外见下）——P2 链整体纯库挂机。
- **真源与注册表**：config/trading_decision_map.yaml:2587-2979（P2 组+4 节点）；DAL-T0-CLOSE（production）；CST-T0-001；RLM-POSITION-011。
- **门禁与质量尺**：ai_autonomy P2-01=auto、P2-02/03/04=paper；materiality P2-01/03=critical+decay monthly。
- **当前运行状态**：**红（未运行）**——代码在、编排缺。yaml 自注"红节点（编排缺口）"×2（P2-01/P2-02）；唯一真实消费=t1_sellable（MOD-POS-028，66 行小件）被 6 处消费（autonomy_core/t0_trader_agent、dashboard_feeds、intraday_position_constraint、firm_risk_aggregator、risk_veto_engine、daily_gate_snapshot）。

## 四、子模块清单（存在性 2026-09-25 批量实测）
| 模块 | 行数 | 消费方（grep 实测） | 状态 |
|------|------|--------------------|------|
| position/core/t1_sellable.py（MOD-POS-028） | 66 | 6 处外部消费 | wired |
| sell_decision/core/t_trade_coordinator.py（MOD-SELL-018） | 166 | 仅 core_satellite_allocator+t0_trading_pipeline（paper 族内） | 纯库挂机 |
| signal_ashare/intraday_t0/t0_trading_pipeline.py（MOD-SIG-090） | 401 | 仅本包族内 | 纯库挂机 |
| position/core/rebalance_engine.py（MOD-POS-004） | 405 | rebalance_cost_analyzer/cross_strategy_position_merger/position_audit_logger（域内） | 域内 wired、无编排 |
| position/core/position_adjudication_center.py（MOD-POS-024） | 285 | allocation_orchestrator/core_satellite_allocator | wired（paper 决策链） |

## 五、堵点与病灶
1. **做T链零编排**（现象：无调度体调 t_trade_coordinator；根因：X/P 流血肉 D60 轮只落了库不落编排；修法：随"做T统一调度"空白件（P 流三空白之二，MOD-SELL-018 planned 语义）立编排工单；量级 2-3 天；本车道可修）。
2. **BT-P0-003 做T成本双节点存疑**（P2-01/P2-03 做T配对 24<30 土规 insufficient_samples，代理口径净价差 mean −45.0bp——开仓前置毛价差≥30bp 下净收益为负，做T经济性存疑；需 Flash F02 重考扩样本；回测车道）。
3. **除权除息污染做T成本归因**（D49 欠账，归公司行动处理 26 号消费侧，非本车道）。
4. **棘轮/复原类"调用方持久化"欠账悬空**：D50 复原语义、止损位 max(old,new) 都写明"调用方持久化"，而调用方不存在——欠账随编排缺位连锁悬空。

## 六、提速与合并机会
t1_sellable 已是 P2-01/S2-02/风控/前端四头共用件——新增做T编排时禁再造可卖判断；t0_trading_pipeline 与 t_trade_coordinator 职责边界（信号 vs 调度）需在编排工单里一次说清，防双调度体。

## 七、自审闸三态
**挖干可施工**（六向有实证：yaml 逐节点血肉+模块行数+消费方 grep+BT-P0-003 实考结果；堵点有根因+修法）。施工序列=先编排工单（P2-01→02→03 接线）后 Flash F02 重考。

## 八、复核命令（10 分钟）
```bash
grep -n "node_id: TDM-P-P2" config/trading_decision_map.yaml          # 节点血肉
grep -rln "t_trade_coordinator" src/zephyr --include="*.py" | grep -v __pycache__   # 消费方=3 文件
grep -A16 "object_id: BT-P0-003" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml  # P0 实考状态
```
