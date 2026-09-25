---
ttl: task_bound
title: F52 验证方法学与决策算法库——REG-VALM-001+REG-DAL-001 环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52）
---

# F52 验证方法学与决策算法库（REG-VALM-001 + REG-DAL-001）

> **一句话**：节点级"怎么算对错"的唯一真源（五类验证方法+推导规则+土规纪律）与节点背后决策算法的唯一登记处（AI 施工图）；消费件=validation runner 一问一考。
> **上游**：F23 考试/F35 一问一考/F66 回测。**下游**：全部 182 节点的置信度三态（verified/proposed/untested）、S2 evidence 回填、S3 知识漂移预检。

## 一、环节定义与边界
- 方法学=REG-VALM-001（节点不加 YAML 字段，由 layer+flow+形态推导）；算法=DAL 与 IND（指标公式）/EXA（执行算法）正交。
- 消费政策真源=tdm_consumption_policy.md（S1-S9 九场合：新模块施工/挂图/回测预检/改判据/寻路/信号引擎变更/退役/复盘回放/转级检查）。

## 二、状态机血肉
### 2.1 五类验证方法（REG-VALM-001）
| method_id | 适用 | 判据核心 |
|-----------|------|---------|
| sensor_monotonicity | L1 五传感器 | 分档 vs 未来 N 日收益 Spearman≥0.8 且方向对 |
| agg_discrimination | 判定/聚合（兜底，含 P 流判定） | 相邻档后续收益差 Welch t p<0.05+高低档差>阈值 |
| exec_quality | L4 执行类 | 滑点≤CST 容差+限价成交率≥95% |
| exit_counterfactual | X 流 S1/R1 | 触发后损失<关风控对照回放（消融器差额序列） |
| portfolio_attribution | F 流 C1-C3 | 归因分解残差<1bp+符号一致率 |

推导优先序：L4→X 流→F 流→L1 传感器→兜底 agg_discrimination。全局纪律：holdout 排除最近 12 个月只考一次（考完作废前移）/触发<30=pending/样本外衰减≥50% 判存疑/lag=1 滞后重算默认开（PB-08/13/16 落地）。

### 2.2 决策算法库（REG-DAL-001）
- **实测 32 条**（15 production/5 trial/12 design，2026-09-25 grep）——**总册口径"27 条"已漂移，本册为准并回填**。
- trial 五条=DAL-CHIP-DISTRIB/DAL-FWD-STOP/DAL-RISK-BUDGET/DAL-SECTOR-DIST/DAL-TAIL-HEDGE（UP 系尾随接线，回测验证前休眠语义）。
- B 半相关：DAL-CIRCUIT-5（production，drawdown_state_machine）/DAL-T0-CLOSE（production，t0_trading_pipeline）/DAL-BUDGET-BAND（**design，code_ref=null=缺口**）/DAL-GRADIENT-TRIM（design）/DAL-FWD-STOP（S1-02 建议通道，trial）。

## 三、六向台账
- **上游输入**：trading_decision_map.yaml（节点清单解析导出）、data/backtest_artifacts/bt-*.json trade_log、两注册表 yaml。
- **下游消费**：c1_backtest.node_verdict 台账→前端 /api/tdm/validation + /api/tdm/verdicts（TD 页验证档案区）；P2-1 衰减巡检（decay_watch）。
- **自动化触发**：**手动**（runner 无调度；decay_watch 尾随验证批运行，调度挂载=登记遗留 Owner 二选一，grep m5+register_*.ps1 零命中=仍未挂）。
- **真源与注册表**：docs/01_policies_and_standards/_registry/catalogs/{validation_method_registry,decision_algo_registry,backtest_backlog}.yaml；runner=zephyr/trading/validation/runner.py（645 行，MOD-TDMVAL-001 production，TESTS=tests/trading/test_validation_runner.py）。
- **门禁与质量尺**：INVARIANTS=holdout 12 月/触发<30 pending/台账只追加不删改/空数据不造假/verdict_reason 代码生成禁手填（R2）。
- **当前运行状态**：**绿（机制）×黄（结论）**——台账实弹 60 行（42 旧 L4 + 18 新 XFLOW，run_id=VAL-20260909-164042），**全部 verdict=pending+insufficient_samples**（成交流水全落 holdout 保密窗 2026-02~08>2025-09 截止线；"宁可 pending 不作弊"晨报裁定 3）；decay checked=60/decayed=0。

## 四、子模块清单
| 件 | 位置 | 状态 |
|----|------|------|
| 验证 runner | src/zephyr/trading/validation/runner.py（645 行） | production；batch 参数（"L4"/"XFLOW"）；18 X 流节点 compute_exit_counterfactual_metrics+soil rules |
| 衰减巡检 | src/zephyr/trading/validation/decay_watch.py | 建成+3 单测；**调度挂载遗留未解** |
| 信号消融对照器 | src/zephyr/trading/validation/ablation.py | 建成+9 用例；**run_ablation 零生产调用方，实弹待 Owner 放行（协议 §12：参数没定稿不跑回测）** |
| 台账 | c1_backtest.node_verdict（DS-222；DDL=schemas/categories/backtest/backtest_node_verdict.py） | 60 行实弹 |
| 回测欠账总表 | backtest_backlog.yaml（REG-BTB-001） | 142 对象（P0×3/P1×32/P2×56/P3×51）；**132 个 plan:null=验收阈值未预注册禁跑（SOP-B 护栏③）** |

## 五、验证欠账总清单（B 半口径，按生死线排序）
1. **BT-P0-003 成本三件套（P0 生死线第三件，横切我半三节点）**：E-L4-09 **过**（滑点 2.56bp+成本项 1467/1467 逐笔零偏差）；X-S2-01 **过**（858 笔 2.65bp≤20）；P2-01/P2-03 **存疑**（做T配对 24<30 insufficient_samples；披露：0/24 配对毛价差≥30bp 开仓前置下净价差 mean −45.0bp——做T经济性存疑）→ Flash F02 重考扩样本。
2. **X 流 18 节点全部 pending**（含 S1-01..06/S2-02..06/R1 组）：exit_counterfactual 真结论待窗口前移（2026-09-09 后新流水积累）重跑。
3. **消融器实弹**：待 Owner 放行 §12；放行后 run_ablation→rescured 序列喂 batch="XFLOW"。
4. **消融动作标注自动化**：SellSignal 流未接入回测（包外零消费者，见 12 册）——xflow_actions 现为调用方注入 v1。
5. **decay 对 exit 方法比对口径**：X 节点出 valid 后 hit_ratio（避损额语义）衰减判据待随消融器锁定。
6. **P/F 流验证零启动**：agg_discrimination（P2/P3 判定）与 portfolio_attribution（C1-C3 残差<1bp）两方法尚无一行实弹。
7. **BTB 132/142 对象 plan=null**：阈值未预注册，批次决策点填写并冻结前禁跑。

## 六、提速与合并机会
建议按月滚动验证批（xflow 报告建议 4：runner 幂等追加新 run_id，L4/X 两批同时出真结论）；SELL 决策库接入回测后消融标注自动化（欠账 3+4 同根同修）；两注册表与 runner 的方法分派表同源（禁第三处写方法映射）。

## 七、自审闸三态
**挖干可施工**（机制三件全建成+台账实弹+欠账七条各有 Owner/批次归属；真结论产出受 holdout 纪律约束属"正确等待"非欠账）。

## 八、复核命令
```bash
grep -c "dal_id:" docs/01_policies_and_standards/_registry/catalogs/decision_algo_registry.yaml   # 32
grep -c "plan: null" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml      # 132
grep -A16 "object_id: BT-P0-003" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml | tail -2
sed -n '28,40p' docs/_working/2026-09-10-xflow-batch-report.md
```
