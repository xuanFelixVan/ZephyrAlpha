---
ttl: task_bound
title: F43 P2 做T与加减仓——全流通挖干案卷（矿道 L05）
session: zc-l05-20260927
creation_token: fc-f43-p2-ttrade-20260927
---

# F43 P2 做T与加减仓——挖干案卷

> 一句话：底仓上做T降成本（不改底仓股数）+两路减仓再平衡；资格三道门→三策略调度→闭环判定，减仓并行。节点组=TDM-P-P2+01..04 共 5 节点（今日 yaml:2587-3111 P 段机数 P2=5，零漂移）。总册 built｜P1｜T6；上游 P1-06/P1-04/L1-AGG/X-R1，下游 P3-01/X-S2/C3-01。
> **本卷核心发现（册引+今日双源复核）：做T链整体纯库挂机——代码在、编排缺，总册 built 判仅"实件"面成立。**

## 一、六向台账（实证锚点）

| 向 | 内容（锚点） |
|---|---|
| ①上游输入 | P1-06 动作清单（可做T/可加仓/减仓，daily）、P1-04 风险否决（冻结做T资格）、L1-AGG 六段（仅 accumulation/expansion 开做T）、X-R1 熔断（停做T） |
| ②数据原料 | kline_1min（14.83 亿行/2021-09→，裁定#413④ 信号法定轴，L05_t0 SKEL A2 册引）；CST-T0-001 成本模型（RT_COST_BP=31.2bp，scripts/audit/cost_trio_exam.py:56 册引）；20 日均振幅≥3% 振幅门 |
| ③状态输出 | 做T资格三态（状态门×振幅门×成本门；成本门=D111 绝对金额制单笔下限 N_floor≈5.86 万@万0.854 册引）；调度单（proposed 假说）；闭环判定（成功=收盘股数不变+总成本降） |
| ④下游消费 | P2-03 统计→F-C3-01 归因；P2-04→X-S2-01；P2-03→X-S2-01（14:50 强平）；**唯一真实生产消费=t1_sellable（MOD-POS-028，66 行）被 6 处消费**（autonomy_core/t0_trader_agent、dashboard_feeds、intraday_position_constraint、firm_risk_aggregator、risk_veto_engine、daily_gate_snapshot——册引 f43 册 §三） |
| ⑤自动化触发 | **零**——无任何计划任务/daemon 调用 t_trade_coordinator/t0_trading_pipeline（册引 grep 实证；今日独立 grep 复核：t_trade_coordinator 全仓 3 文件命中=自身+core_satellite_allocator+t0_trading_pipeline，即 paper 族内，成立） |
| ⑥缺口债 | D58 四件欠账（双轨止损/sell-first 复原铁律/连败熔断/主策略减仓优先）；D50 做T配对核算器；D55 隔夜资格门；BT-P0-003 做T成本双节点 24<30 insufficient_samples 存疑；除权除息污染（D49） |

## 二、子模块三级枚举（2026-09-27 实扫）

- 域 `src/zephyr/sell_decision/core/`（28 件实扫）之 t_trade_coordinator.py（MOD-SELL-018，166 行）。
- 域 `src/zephyr/signal_ashare/intraday_t0/`：t0_trading_pipeline.py（MOD-SIG-090，401 行，仅本包族内）。
- 域 `src/zephyr/position/core/`（29 件实扫）：t1_sellable.py（MOD-POS-028）、rebalance_engine.py（MOD-POS-004，405 行，域内三消费方：rebalance_cost_analyzer/cross_strategy_position_merger/position_audit_logger）、position_adjudication_center.py（MOD-POS-024，285 行，wired paper 决策链）。
- 消费方核验（今日 grep 实锚）：t_trade_coordinator 3 文件、t1_sellable 6 外部消费（册引，未逐一重跑——口径维持册引）。
- 判据考试面（研究面，L05_t0 SKEL B 块）：scripts/audit/t0_*.py 7 件+t0_conditional_e4_v3（verdict=STATE_GATE_NEVER_TRIGGERED，26 对<30）+T0-CEILING 容量上界（p50=330bp，share≥L1=0.9999）。

## 三、接线四态独立复核（2026-09-27）

| 件 | 四态判定 | 独立证据 |
|---|---|---|
| t1_sellable | **生产接线** | 6 处外部消费（册引）；今日 t_trade_coordinator grep 佐证其调度族边界 |
| t_trade_coordinator+t0_trading_pipeline | **纯库挂机** | 今日独立 grep 3 文件全在 paper 族内（复核成立）；yaml 自注"红节点（编排缺口）"×2（P2-01/P2-02，册引） |
| rebalance_engine（P2-04） | **域内接线、无编排** | 域内三消费方册引；无日循环触发面 |
| 研究面考试族 | **人工触发（合法）** | L05_t0 SKEL B1⑤"考试体是判据面，可留人工触发"（T0_CHAIN_WIRING_GAPS §C 同判） |
| 做T条件维消费 | **零接线** | L05_t0 SKEL §0"研究面已闭环，消费面零接线"（T0_CHAIN_WIRING_GAPS §B，含 45 件批次盘面） |

**骨架勘误（登记待 D 线）**：
1. **总册 F43 状态"built"降格建议**：yaml 自注红节点×2+零编排双源实证下，F43 实际四态="实件 built/编排 missing"混合；建议总册行加注"编排缺口"（同 F42 勘误 1 处置路径，Owner/裁-5 同窗）。
2. f43 册 §三"t0_trading_pipeline 401 行"与 L05_t0 SKEL A2"auction/分钟腿"口径并读无冲突，维持。

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G43-1 | 做T链零编排（P2-01→02→03） | 立"做T统一调度"编排工单（2-3 天；P 流三空白之二，MOD-SELL-018 planned 语义）；禁再造可卖判断（t1_sellable 四头共用） | **P0** |
| G43-2 | LK-07 做T策略层零 verified | 三策略调度池无 verified 实体——材料线 L05-C02（T0-MATERIAL 重考，Owner 已批开闸）先行 | P1 |
| G43-3 | BT-P0-003 做T经济性存疑（净价差 mean −45.0bp，开仓前置毛价差≥30bp 下净收益为负） | Flash F02 重考扩样本（回测车道），编排工单后置 | P1 |
| G43-4 | D58/D50/D55 欠账四件（双轨止损/复原铁律/配对核算器/隔夜门） | 随编排工单一并立项；"调用方持久化"类欠账随编排缺位连锁悬空 | P1 |
| G43-5 | 除权除息污染做T成本归因（D49） | 归公司行动处理（26 号消费侧），非本卷 | P2 |

## 五、自审闸三态

**挖干可施工**（六向有实证：yaml 逐节点血肉+模块行数+消费方 grep 双源复核+BT-P0-003 实考结果；堵点有根因+修法）。施工序列=先编排工单（P2-01→02→03 接线）后 F02 重考。

### 待裁
- t0_trading_pipeline（信号）与 t_trade_coordinator（调度）职责边界——编排工单里一次说清防双调度体（册引 §六）；归属施工批排期。

## 六、复跑命令

```bash
grep -n "node_id: TDM-P-P2" config/trading_decision_map.yaml    # :2587 节点血肉
grep -rln "t_trade_coordinator" src/zephyr scripts --include="*.py" | grep -v __pycache__  # =3 文件
grep -rln "t1_sellable" src/zephyr --include="*.py" | grep -v __pycache__ | wc -l          # 共用件清点
grep -A16 "object_id: BT-P0-003" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml
```
