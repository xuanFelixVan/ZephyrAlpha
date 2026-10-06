---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e4_exam_throat —— E4 考试咽喉（SPM 82 节点）

- 真源: `config/strategy_production_map.yaml`；行号=SPM:L*。
- 职责: 策略考试的机器：批测引擎/验证管线/成本门/过拟合防护 + 数据载荷后勤（**含 24 枚数据供给/基础设施件，层语义漂移见 §3**）。
- 计数: 82 = 1 stage(built) + 81 mech（built 77 / pending 4）。
- **编号空洞（补充挖矿发现）**: E4 机制从 M-002 起，M-001 号位缺位（图上无注记，疑退役未补位或跳号；此处有意不写完整 ID 防对账器幻影计数）——81 枚机制=M-002..M-082。

## 1. 族内节点全清单

| 节点段 | 数 | 内容 | 状态 | module | 行 |
|---|---|---|---|---|---|
| FAC-E4 | 1 | 考试咽喉（stage） | built | MOD-BT-027 | SPM:L307 |
| FAC-E4-M-002 | 1 | 成本模型标定真源 | built | MOD-BT-001 | SPM:L2684 |
| FAC-E4-M-003 | 1 | data_handler 数据来源手 | **pending** | MOD-BT-006 | SPM:L2712 |
| FAC-E4-M-004~009 | 6 | 数值格式化/命中率快照/报告组装缓存/报告聚合判定/诊断报告聚合/分层验证管道C-003 | built | MOD-BT-019~027 | SPM:L2725~2822 |
| FAC-E4-M-010 | 1 | 策略级 CPCV 打分矩阵 | built | MOD-BT-028 | SPM:L2838 |
| FAC-E4-M-011~013 | 3 | P0 印教材 / 新旧状态双轨对照器 / P0 成本验证件 | built | MOD-BT-032/033/034 | SPM:L2853~2883 |
| FAC-E4-M-014~015 | 2 | C4 快筛批测入口 / C4 批测冒烟守卫 | built | MOD-BT-076/077 | SPM:L2917~2948 |
| FAC-E4-M-016~020 | 5 | 台账数据源 / 分布预测双标准考尺 / 网格结构知识方差分解 / 整装回测自动触发件 / N试次账本（FDR 预算证据位） | built | MOD-BT-191/194/197/198/200 | SPM:L2965~3014 |
| FAC-E4-M-021 | 1 | F06 幸存者 WFA 正考（F 车道考卷） | built | MOD-BT-211 | SPM:L3043 |
| FAC-E4-M-022 | 1 | EXP 六因子 IC 出证编排 | **pending** | MOD-BT-218 | SPM:L3059 |
| FAC-E4-M-023 | 1 | P0-6 试验台账批末记账红证（病历页） | **pending** | MOD-BT-228 | SPM:L3071 |
| FAC-E4-M-024~041 | 18 | 数据供给件群：数据库集成蓝图/跨境双活传输/调度对账补跑/轻量InstrumentMaster/自动补数/数据源SLA追踪/多周期融合/参考数据/压缩归档/行情源注册~缓存六件/数据库层/Redis共享状态/WAL监控 | built | SH-DB-001/MOD-DATA-072/MOD-L00-021/MOD-DATA-069/MOD-MKT-001~006 等 | SPM:L3083~3299 |
| FAC-E4-M-042 | 1 | 复现管理器（ML 域边界件） | built | dir:_domain_machine_learning_train/reproducibility_manager | SPM:L3311 |
| FAC-E4-M-043~050 | 8 | 信号质量基准/场景生成器/仿真结果分析/参数鲁棒性/未来函数检测/Sharpe修正(DSR)/DSR计算器/过拟合防护门 | built | MOD-SIM-005/012/021/022/023/024 等 | SPM:L3323~3414 |
| FAC-E4-M-051~054 | 4 | 公司行动处理器(复权口径)/参考数据管理(trading域)/因子研究案例库/因子模型共评器 | built | MOD-TRADING-004/MOD-L02-027 等 | SPM:L3414~3463 |
| FAC-E4-M-055~057 | 3 | 冷数据归档管理 / 数据异常告警 / 数据湖管理 | built | dir:_domain_data_eng/* | SPM:L3463~3499 |
| FAC-E4-M-058 | 1 | 质量 SLA 违约预测 | **pending** | dir:_domain_data_eng/quality_sla_breach_predictor | SPM:L3499 |
| FAC-E4-M-059~063 | 5 | 板块预注册考试跑批器 / CPCV 重考 harness / 考试成本重考件 / DSR 重算回填 / 复现演练器 | built | scripts/backtest/* | SPM:L3511~3557 |
| FAC-E4-M-064~082 | 19 | 框架件 af:*：向量化引擎/事件驱动引擎/WFO滚动/PurgedKFold/CPCV/撮合引擎(Tick级)/Tick回放/数据处理器/PIT管理器/决策门控/考试成本门/成本归因/回测调度器/过拟合检测器/闭卷闸/策略验证管线/批测预检/平稳自助法/闭卷读取闸 | built | src/zephyr/backtest/* | SPM:L3569~3767 |

段计数核对：1+1+1+6+1+3+2+5+1+1+1+18+1+8+4+3+1+5+19 = 81 mech ✓；pending 4 = M-003/M-022/M-023/M-058 ✓。

## 2. 接线现状与缺口判定

- 已接线：E4 是两图全链 wiring 最厚的一层——af:* 19 枚框架件即 H9 全册的证据基座（matching_engine/walk_forward/cpcv/purged_kfold/decision_gate/exam_cost_gate 等，H9 §5 资产清单同源）；F06 WFA 正考（M-021）= 现行考卷族一员（H9 §1.8 C3-04 判 A 的载体）。
- 缺口 4 枚：M-003 数据来源手 pending（考卷数据载荷泛化正身，H9 S2 建议 load_px 泛化的落点）；M-022 EXP 六因子 IC 出证编排 pending；M-023 批末记账红证 pending（病历闭环末页）；M-058 SLA 违约预测 pending。
- 可考性：E4 本身就是考场，骨架可考性全场最高；缺口性质是"考务后勤"而非"缺考场"。

## 3. 层语义漂移（补充挖矿发现）

E4 名义="考试咽喉"，但 **M-024~M-041（18 枚）+ M-051~M-052 + M-055~M-058 = 24 枚明确的数据供给/基础设施件**（另 M-042 复现管理器、M-053 案例库为边界件）——与图12 数据供给链（chief ENV-01..05）职能重叠。判定：非错误但层语义混装；矩阵考试读 E4 应按"考场(57)+考务后勤(24)"双层。此发现 census/chief 均未记载（本车道补充挖矿）；与 st_data_legs 互链。

## 4. 交叉验证

- H9 §0/§5：考卷引擎与框架件清单与本层 af:* 段一一对应——两册互为底册。
- H9 §3.1 T3a 改造点（factory_grid_executor/_c4_engine）在 E1F/E4 交界域。
- chief B1 ENV-16/ENV-17 计数一致；ENV-16"sim 腿仅钩子"的 sim 件群在 E7（见 st_e7），E4 承接其回测半腿。
