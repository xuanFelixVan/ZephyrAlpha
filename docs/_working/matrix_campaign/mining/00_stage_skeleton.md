---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# 00 环节骨架总册 —— 策略工厂全链路（SPM 341 + TDM 182）

- 车道: S（骨架挖矿）| 日期: 2026-10-06 | 性质: 只读挖矿，唯一写=本目录新文件
- 真源: `config/strategy_production_map.yaml`（下称 SPM，341 节点/10 层/17 边，nodes: L68 起、edges: L4907 起）；`config/trading_decision_map.yaml`（下称 TDM，182 节点/257 边/24 cells，nodes: L65 区间、edges: L5794 起、state_matrix: L6081 起）
- 交叉底册: H9=`docs/_working/fullcirc_closeout_chief/t3_fullflow_exam_mining.md`；census=`docs/_working/map_census/00_panorama_map_census_v1.md`；chief B1=`docs/_working/chief_fullchain_20261006/01_skeleton_environments.md` + `02_gap_ledger.md`
- 行号指针约定: `TDM:L82`=trading_decision_map.yaml 第 82 行；`SPM:L69`=strategy_production_map.yaml 第 69 行。行号为 2026-10-06 快照，两图均在他队域内可能漂移。

## 0. 一页结论

1. 策略工厂 SPM 341 节点 = **10 stage + 7 lane + 324 mechanism**；build_status 实查 = **built 315 / partial 12 / pending 14**（与 chief B1 §1 计数一致）。任务书所称"16 骨架层节点+325 机制"与字段实查 **17+324 不符**（FAC-MAP-M-001/002 两枚图守卫 mechanism 计入 E0 机制）——见 §5 矛盾项 C1。
2. TDM 182 节点按 H9 四类机械复算**完全对平**：A 已实现且可考 16 / B 接口在册未开 26 / C 零实现缺口 118 / D 非回测域 22（判据与逐条证据=H9 §1，本车道只做转录+复算，未重挖）。
3. 本车道自定**接线级五档**（§2 口径）：L1 考卷已行使 16 ｜ L2 接口在册未开 26 ｜ L3 live 在岗·回测零 73 ｜ L4 图纸/组骨架 45 ｜ ND 非回测域 22。合计 182。
4. 全链"环节骨架"已按 20 个族落成子册（§6 索引）：SPM E0~E9 十族 + TDM 九族（l0l1/l2/l3/l4/p/x/c/l9/crypto）+ 借力族 data_legs。182 节点零遗漏、341 节点零遗漏，对平见 `99_skeleton_selfcheck.md`。
5. 新发现矛盾点 4 项（§5）：任务书骨架计数 16vs17；census"L4 13 子环节"vs 实查 14；chief B1 的 ENV-14/ENV-16 TDM 分组账差 2~3 枚（四个 FLOW 终端聚合点归属不显式）；FAC-E0-M-003 GPU Core 标 pending 与 #ARCH-366 gpu_core 冒烟实测在案的状态张力。

## 1. 工厂全景：SPM E0~E9 十层

数据源：SPM layers L 区间（layer_id/name_zh/growth）+ nodes 全量字段统计（机械统计，非手数）。

| 层 | 层名 | 职责一句话 | 节点合计 | stage/lane/mech | built | partial | pending | 子册 |
|---|---|---|---|---|---|---|---|---|
| E0 | 算力调度 | 现在能不能跑重算力、该跑哪条车道（trade_calendar 当闸、事件触发禁定时器） | 18 | 1/0/17 | 15 | 1 | 2 | st_e0_compute |
| E1 | 想法进货 | 六（实七）车道源源不断进策略想法与原料 | 66 | 1/7/58 | 58 | 7 | 1 | st_e1_idea_intake |
| E2 | 假说预审 | 假说进考卷前的逻辑门+FDR 纪律（三铁律②执法位） | 8 | 1/0/7 | 6 | 1 | 1 | st_e2_hypothesis |
| E3 | 构造代码 | 想法→可回测代码的翻译件族（C4 翻译 041~075 为主体） | 80 | 1/0/79 | 78 | 1 | 1 | st_e3_construction |
| E4 | 考试咽喉 | 批测/验证/成本门/过拟合防（含误挂的数据供给件群，见 st_e4 层语义漂移注记） | 82 | 1/0/81 | 78 | 0 | 4 | st_e4_exam_throat |
| E5 | 协同去重 | 考过的新策略与台账既有策略去重 | 5 | 1/0/4 | 5 | 0 | 0 | st_e5_dedup |
| E6 | 入库监控 | 台账入库+生命周期/漂移/降级监控 | 15 | 1/0/14 | 15 | 0 | 0 | st_e6_intake_monitor |
| E7 | 模拟盘前哨 | paper 考试→转正建议（联赛/mSPRT/晨报） | 23 | 1/0/22 | 20 | 0 | 3 | st_e7_paper |
| E8 | 组装与资金分配 | 多策略装配、预算、regime 元分配、权重唯一真源 | 35 | 1/0/34 | 33 | 1 | 1 | st_e8_assembly |
| E9 | 实盘归因 | 实盘绩效归因并回灌假说先验（feedback E9→E2） | 9 | 1/0/8 | 7 | 1 | 1 | st_e9_attribution |
| **合计** | | | **341** | 10/7/324 | **315** | **12** | **14** | |

- 边实查 17 条：E0→E1→…→E9 主链 9 条 + 回灌边 E9→E2、E6→E1（feedback_loops 2 条与此呼应）+ E1→七车道 7 条（E1A/B/C/D/E/G/F）。SPM 无 counts 块（chief B1 §3.2 同证）。
- 骨架节点=17（10 stage+7 lane），机制节点=324——**纠正任务书"16+325"口径**；14 pending 与 12 partial 名单见各族子册 §2。

## 2. TDM 182 节点完整清单（H9 四类 × 本车道接线级）

接线级口径（本车道定义，机械可判）：
- **L1 考卷已行使** = H9 A：现行考卷链路（GridCompiler→evaluate_recipe→_c4_engine）真实行使该环节语义。
- **L2 接口在册未开** = H9 B：schema 维/框架件/模拟盘闸占位或在册，考卷 context 折叠不消费。
- **L3 live 在岗·回测零** = H9 C 且 node.module_ref 非空：生产域模块在岗，回测域零引用。
- **L4 图纸/组骨架** = H9 C 且 module_ref 为空：组聚合节点或纯规划源线。
- **ND 非回测域** = H9 D：盘前运维/治理/台账/实盘对账，天然不进回测（接线另按 live 域判）。
- 判定证据逐条=H9 §1.0~§1.9（本册不重复证据，只给指针）；H9 计数复核 A16/B26/C118/D22 与其 §0 完全一致。

### 2.0 entry_flow·LROOT（1）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-E-FLOW | 输出建仓信号 | A | L1 | TDM:L82 |

### 2.1 entry_flow·L0 盘前作战计划（5，全 D）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-E-L0 | 盘前作战计划 | D | ND | TDM:L192 |
| TDM-E-L0-01 | 计划生成 | D | ND | TDM:L219 |
| TDM-E-L0-02 | 偏离监控与修订 | D | ND | TDM:L247 |
| TDM-E-L0-03 | 收盘复盘与明日边界 | D | ND | TDM:L275 |
| TDM-E-L0-04 | 明日情绪盘中滚动预测 | D | ND | TDM:L307 |

### 2.2 entry_flow·L1 大盘总闸（cn_a 9 + crypto 1；crypto 见 §2.9）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-E-L1 | 大盘总闸 | B | L2 | TDM:L344 |
| TDM-E-L1-S1 | 大盘指数传感器 | C | L3 | TDM:L407 |
| TDM-E-L1-S2 | 市场内部结构传感器 | C | L3 | TDM:L436 |
| TDM-E-L1-S3 | 赚钱效应传感器 | C | L3 | TDM:L463 |
| TDM-E-L1-S4 | 波动率传感器 | C | L3 | TDM:L488 |
| TDM-E-L1-S0 | 宏观环境传感器 | C | L3 | TDM:L538 |
| TDM-E-L1-S0-1 | 新闻情绪语义分析 | C | L3 | TDM:L566 |
| TDM-E-L1-S5 | 日级市场条件传感器 | C | L3 | TDM:L596 |
| TDM-E-L1-AGG | 市场状态判定 | B | L2 | TDM:L620 |

### 2.3 entry_flow·L2 板块选择（cn_a 29 全 C + crypto 1 见 §2.9）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-E-L2 | 板块选择（组） | C | L4 | TDM:L657 |
| TDM-E-L2-01 | 板块强度综合 | C | L3 | TDM:L686 |
| TDM-E-L2-01-1 | 结构强度评估 | C | L3 | TDM:L721 |
| TDM-E-L2-01-2 | 动量活跃度排名 | C | L3 | TDM:L754 |
| TDM-E-L2-01-3 | 多周期动量加权 | C | L3 | TDM:L786 |
| TDM-E-L2-01-4 | 板块资金流聚合 | C | L3 | TDM:L817 |
| TDM-E-L2-01-5 | 市场级调节注入 | C | L3 | TDM:L850 |
| TDM-E-L2-02 | 轮动序列追踪 | C | L3 | TDM:L883 |
| TDM-E-L2-02-1 | RRG 轮动序列 | C | L3 | TDM:L915 |
| TDM-E-L2-02-2 | 单板块轮动预警 | C | L3 | TDM:L946 |
| TDM-E-L2-03 | 调整周期进度 | C | L3 | TDM:L979 |
| TDM-E-L2-03-1 | 扩散指标进度追踪 | C | L3 | TDM:L1009 |
| TDM-E-L2-04 | 板块级市场状态 | C | L3 | TDM:L1043 |
| TDM-E-L2-04-1 | 轮动状态五分类 | C | L3 | TDM:L1075 |
| TDM-E-L2-04-2 | 虹吸态识别 | C | L3 | TDM:L1105 |
| TDM-E-L2-05 | 水温响应（组） | C | L4 | TDM:L1138 |
| TDM-E-L2-05-1 | 水温档推导 | C | L3 | TDM:L1166 |
| TDM-E-L2-05-2 | 信号响应三件套 | C | L3 | TDM:L1197 |
| TDM-E-L2-06 | 板块个股传导 | C | L3 | TDM:L1230 |
| TDM-E-L2-06-1 | 三级放行门槛 | C | L3 | TDM:L1260 |
| TDM-E-L2-06-2 | 龙头识别定位 | C | L3 | TDM:L1292 |
| TDM-E-L2-06-3 | 强度加权传导 | C | L3 | TDM:L1324 |
| TDM-E-L2-07 | 回踩质量分级 | C | L3 | TDM:L1356 |
| TDM-E-L2-07-1 | 回踩ABC判定 | C | L3 | TDM:L1389 |
| TDM-E-L2-08 | 板块生命周期判定 | C | L3 | TDM:L1423 |
| TDM-E-L2-09 | 催化剂识别 | C | L3 | TDM:L1454 |
| TDM-E-L2-09-1 | 事件图谱传导 | C | L3 | TDM:L1487 |
| TDM-E-L2-09-2 | 冲击标的生成 | C | L3 | TDM:L1518 |
| TDM-E-L2-10 | 同源补涨比价 | C | L3 | TDM:L1549 |

### 2.4 entry_flow·L3 个股选择（cn_a 25 + crypto 1 见 §2.9）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-E-L3 | 个股选择（组） | C | L4 | TDM:L1579 |
| TDM-E-L3-01 | Universe构建与剔除 | A | L1 | TDM:L1611 |
| TDM-E-L3-02 | 九阶段选票主链 | C | L3 | TDM:L1646 |
| TDM-E-L3-03 | 双池评分（组） | C | L4 | TDM:L1676 |
| TDM-E-L3-03-1 | 短线池5分制 | C | L3 | TDM:L1704 |
| TDM-E-L3-03-2 | 波段池5分制 | C | L3 | TDM:L1735 |
| TDM-E-L3-03-3 | 双策略合流体检 | B | L2 | TDM:L1767 |
| TDM-E-L3-04 | 负面否决器 | C | L3 | TDM:L1799 |
| TDM-E-L3-05 | 顺位排序 | A | L1 | TDM:L1838 |
| TDM-E-L3-06 | 环境开关 | B | L2 | TDM:L1867 |
| TDM-E-L3-07 | 策略专属链（组） | C | L4 | TDM:L1898 |
| TDM-E-L3-07-1 | 打板选股链 | C | L3 | TDM:L1926 |
| TDM-E-L3-07-2 | 多因子打分链 | A | L1 | TDM:L1963 |
| TDM-E-L3-07-3 | 其余sleeve选股链 | C | L3 | TDM:L1995 |
| TDM-E-L3-08 | 候选池输出 | A | L1 | TDM:L2037 |
| TDM-E-L3-09 | 股票池分层维护 | C | L3 | TDM:L2071 |
| TDM-E-L3-10 | 可交易性预检 | A | L1 | TDM:L2107 |
| TDM-E-L3-11 | 日内动态选股（组） | C | L4 | TDM:L2145 |
| TDM-E-L3-11-1 | 竞价选股 | C | L3 | TDM:L2174 |
| TDM-E-L3-11-2 | 盘中涨速异动扫描 | C | L3 | TDM:L2202 |
| TDM-E-L3-12 | 个股多维验证（组） | C | L4 | TDM:L2233 |
| TDM-E-L3-12-1 | 个股资金面分析 | C | L3 | TDM:L2262 |
| TDM-E-L3-12-2 | 龙虎榜席位追踪 | C | L3 | TDM:L2292 |
| TDM-E-L3-12-3 | 筹码分布分析 | C | L3 | TDM:L2326 |
| TDM-E-L3-12-4 | 形态结构识别 | C | L3 | TDM:L2366 |

### 2.5 entry_flow·L4 买卖点与执行（cn_a 15 + crypto 1 见 §2.9）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-E-L4 | 买卖点与执行（组） | C | L4 | TDM:L2397 |
| TDM-E-L4-01 | 分批建仓 | B | L2 | TDM:L2425 |
| TDM-E-L4-02 | 买入时序 | C | L3 | TDM:L2455 |
| TDM-E-L4-03 | 价格锚定 | C | L3 | TDM:L2487 |
| TDM-E-L4-04 | 资金分配多标的 | A | L1 | TDM:L2517 |
| TDM-E-L4-05 | 打板执行专项 | C | L3 | TDM:L2545 |
| TDM-E-L4-06 | 执行算法 | B | L2 | TDM:L2576 |
| TDM-E-L4-07 | 条件触发队列 | C | L3 | TDM:L2611 |
| TDM-E-L4-08 | 突破失败降级 | C | L3 | TDM:L2642 |
| TDM-E-L4-09 | 执行硬约束 | B | L2 | TDM:L2672 |
| TDM-E-L4-10 | 订单生命周期状态机 | B | L2 | TDM:L2703 |
| TDM-E-L4-11 | 部分成交与撤改处理 | C | L3 | TDM:L2734 |
| TDM-E-L4-12 | 订单级预检 | B | L2 | TDM:L2763 |
| TDM-E-L4-13 | 执行容灾对账 | D | ND | TDM:L2795 |
| TDM-E-L4-14 | 执行成本反馈与选型回写 | D | ND | TDM:L2826 |

### 2.6 position_flow·P 族（18，crypto 无）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-P-FLOW | 输出持仓信号 | A | L1 | TDM:L106 |
| TDM-P-P1 | 持仓体检（组） | C | L3 | TDM:L2863 |
| TDM-P-P1-01 | 持仓对账与台账快照 | D | ND | TDM:L2943 |
| TDM-P-P1-02 | 持仓分级与监控频率 | D | ND | TDM:L2978 |
| TDM-P-P1-03 | 买入逻辑存活判定 | C | L3 | TDM:L3017 |
| TDM-P-P1-04 | 风险否决体检 | C | L3 | TDM:L3049 |
| TDM-P-P1-05 | 组合级持仓体检 | A | L1 | TDM:L3083 |
| TDM-P-P1-06 | 体检结论与动作清单 | D | ND | TDM:L3118 |
| TDM-P-P2 | 做T与加减仓（组） | C | L4 | TDM:L2888 |
| TDM-P-P2-01 | 做T资格与成本前置 | B | L2 | TDM:L3153 |
| TDM-P-P2-02 | 做T策略调度 | C | L3 | TDM:L3193 |
| TDM-P-P2-03 | 做T闭环与成功判定 | C | L3 | TDM:L3237 |
| TDM-P-P2-04 | 减仓与再平衡 | A | L1 | TDM:L3276 |
| TDM-P-P3 | 加仓决策（组） | B | L2 | TDM:L2916 |
| TDM-P-P3-01 | 加仓资格门 | B | L2 | TDM:L3315 |
| TDM-P-P3-02 | 金字塔加仓规则 | B | L2 | TDM:L3351 |
| TDM-P-P3-03 | 加仓量级与风险核算 | C | L3 | TDM:L3391 |
| TDM-P-P3-04 | 加仓时点与执行 | C | L3 | TDM:L3421 |

### 2.7 exit_flow·X 族（19，crypto 无）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-X-FLOW | 输出离场信号 | C | L4 | TDM:L135 |
| TDM-X-R1 | 应急保命 | B | L2 | TDM:L3502 |
| TDM-X-R1-01 | 熔断分级判定 | B | L2 | TDM:L3546 |
| TDM-X-R1-02 | 熔断期减仓与持仓处置 | B | L2 | TDM:L3584 |
| TDM-X-R1-03 | 护盘资产定向加仓白名单 | C | L3 | TDM:L3617 |
| TDM-X-S1 | 卖出信号收集评分（组） | C | L4 | TDM:L3453 |
| TDM-X-S1-01 | 信号收集与六桶分类 | C | L3 | TDM:L3658 |
| TDM-X-S1-02 | 止损族判定 | C | L3 | TDM:L3689 |
| TDM-X-S1-03 | 止盈族判定 | C | L3 | TDM:L3732 |
| TDM-X-S1-04 | 破位与情绪退潮信号 | C | L3 | TDM:L3762 |
| TDM-X-S1-05 | 信号融合与紧迫度评分 | C | L3 | TDM:L3800 |
| TDM-X-S1-06 | 强制清仓绕过通道 | D | ND | TDM:L3837 |
| TDM-X-S2 | 离场执行（组） | C | L4 | TDM:L3479 |
| TDM-X-S2-01 | 执行方式路由 | C | L3 | TDM:L3875 |
| TDM-X-S2-02 | T+1与涨跌停约束 | A | L1 | TDM:L3918 |
| TDM-X-S2-03 | 执行时段路由 | C | L3 | TDM:L3958 |
| TDM-X-S2-04 | 本地条件单管理 | C | L3 | TDM:L4000 |
| TDM-X-S2-05 | 分批止盈执行 | C | L3 | TDM:L4036 |
| TDM-X-S2-06 | 卖出闭环与退出效率 | D | ND | TDM:L4069 |

### 2.8 portfolio_flow·C 族（13，crypto 无）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-F-FLOW | 输出组合信号 | B | L2 | TDM:L161 |
| TDM-F-C1 | 预算切分 | B | L2 | TDM:L4114 |
| TDM-F-C2 | 组合聚合（组） | B | L2 | TDM:L4150 |
| TDM-F-C2-01 | 目标聚合与净额轧平 | C | L3 | TDM:L4206 |
| TDM-F-C2-02 | 组合约束栈 | A | L1 | TDM:L4248 |
| TDM-F-C2-03 | 相关性聚类与cluster上限 | C | L3 | TDM:L4287 |
| TDM-F-C2-04 | budget变动三级升级 | D | ND | TDM:L4321 |
| TDM-F-C3 | 绩效归因反馈（组） | B | L2 | TDM:L4174 |
| TDM-F-C3-01 | 多维归因引擎 | B | L2 | TDM:L4356 |
| TDM-F-C3-02 | 升降级管线与退役评审 | D | ND | TDM:L4398 |
| TDM-F-C3-03 | sleeve权重调权 | B | L2 | TDM:L4450 |
| TDM-F-C3-04 | 参数校准闭环 | A | L1 | TDM:L4500 |
| TDM-F-C3-05 | 可靠度养成与信号健康 | B | L2 | TDM:L4549 |

### 2.9 crypto 族（4，分散于各 flow 的 C-L1/L2/L3/L4）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-C-L1 | 币圈大盘总闸 | C | L4 | TDM:L4594 |
| TDM-C-L2 | 赛道选择 | C | L4 | TDM:L4616 |
| TDM-C-L3 | 币对选择 | C | L4 | TDM:L4637 |
| TDM-C-L4 | 币圈买卖点 | C | L4 | TDM:L4658 |

### 2.10 entry_flow·L9 数据与知识供给（44）

| node_id | 名称 | 类别 | 接线级 | 行 |
|---|---|---|---|---|
| TDM-E-L9-A01 | 源线·日线/分钟行情 | A | L1 | TDM:L4681 |
| TDM-E-L9-A02 | 源线·Tick分笔 | B | L2 | TDM:L4706 |
| TDM-E-L9-A03 | 源线·板块/概念指数 | C | L4 | TDM:L4732 |
| TDM-E-L9-A04 | 源线·估值 | B | L2 | TDM:L4757 |
| TDM-E-L9-A05 | 源线·财务 | B | L2 | TDM:L4782 |
| TDM-E-L9-A06 | 源线·资金流 | C | L4 | TDM:L4807 |
| TDM-E-L9-A07 | 源线·千股千评 | C | L4 | TDM:L4832 |
| TDM-E-L9-A08 | 源线·航运运价BDI | C | L4 | TDM:L4857 |
| TDM-E-L9-A09 | 源线·财经快讯情绪 | C | L4 | TDM:L4882 |
| TDM-E-L9-A10 | 源线·国际宏观 | C | L4 | TDM:L4908 |
| TDM-E-L9-A11 | 源线·能源库存 | C | L4 | TDM:L4933 |
| TDM-E-L9-A12 | 源线·天气 | C | L4 | TDM:L4958 |
| TDM-E-L9-A13 | 源线·股东户数 | C | L4 | TDM:L4984 |
| TDM-E-L9-A14 | 源线·互动易问答 | C | L4 | TDM:L5009 |
| TDM-E-L9-A15 | 源线·加密永续/费率 | C | L4 | TDM:L5035 |
| TDM-E-L9-A16 | 源线·投入产出 | C | L4 | TDM:L5061 |
| TDM-E-L9-B01 | 源线·卫星影像 | C | L4 | TDM:L5086 |
| TDM-E-L9-B02 | 源线·美国官方天气/海洋 | C | L4 | TDM:L5111 |
| TDM-E-L9-B03 | 源线·招聘JD | C | L4 | TDM:L5136 |
| TDM-E-L9-B04 | 源线·电商价格 | C | L4 | TDM:L5161 |
| TDM-E-L9-B05 | 源线·招投标 | C | L4 | TDM:L5186 |
| TDM-E-L9-B06 | 源线·社媒舆情X/Reddit | C | L4 | TDM:L5211 |
| TDM-E-L9-B07 | 源线·雪球/股吧散户情绪 | C | L4 | TDM:L5236 |
| TDM-E-L9-B08 | 源线·APP榜单 | C | L4 | TDM:L5261 |
| TDM-E-L9-B09 | 源线·进出口贸易 | C | L4 | TDM:L5286 |
| TDM-E-L9-B10 | 源线·信用卡/支付消费 | C | L4 | TDM:L5311 |
| TDM-E-L9-C01 | 源线·实时门店客流 | C | L4 | TDM:L5336 |
| TDM-E-L9-C02 | 源线·银行网点/信贷活跃 | C | L4 | TDM:L5361 |
| TDM-E-L9-C03 | 源线·直播电商实时成交 | C | L4 | TDM:L5386 |
| TDM-E-L9-G1 | 图谱·Zephyr产业链 | C | L4 | TDM:L5411 |
| TDM-E-L9-G2 | 图谱·ChainKnowledgeGraph事实层 | C | L4 | TDM:L5439 |
| TDM-E-L9-G3 | 图谱·实体股权穿透 | C | L3 | TDM:L5465 |
| TDM-E-L9-G4 | 图谱·概念/题材 | C | L4 | TDM:L5492 |
| TDM-E-L9-G5 | 图谱·投入产出传导 | C | L4 | TDM:L5518 |
| TDM-E-L9-V1 | 状态变量快照·大盘 | D | ND | TDM:L5544 |
| TDM-E-L9-V2 | 状态变量快照·情绪 | D | ND | TDM:L5569 |
| TDM-E-L9-V3 | 状态变量快照·板块 | D | ND | TDM:L5594 |
| TDM-E-L9-AGG | 知识供给汇聚 | D | ND | TDM:L5619 |
| TDM-E-L9-D1 | 决策假设·因子组合挖掘 | A | L1 | TDM:L5646 |
| TDM-E-L9-D2 | 决策假设·登记与考试方案 | D | ND | TDM:L5670 |
| TDM-E-L9-E1 | 验证·一问一考考试链 | A | L1 | TDM:L5695 |
| TDM-E-L9-E2 | 验证·结论回传与修正 | D | ND | TDM:L5719 |
| TDM-E-L9-Z1 | 治理·问题治理与状态机 | D | ND | TDM:L5743 |
| TDM-E-L9-Z2 | 治理·净零与资产对账 | D | ND | TDM:L5768 |

计数对平：§2.0~§2.10 = 1+5+9+29+25+15+18+19+13+4+44 = **182**（crypto 4 枚只计入 §2.9 一处）。

## 3. 与 map_census 普查交叉验证

census=`docs/_working/map_census/00_panorama_map_census_v1.md`（2026-09-24，裁定#409 配套）。

| 一致项 | 矛盾项 | 补充项（本车道补充挖矿） |
|---|---|---|
| census §1 表：TDM/FACTORY 属流程纵轴图，对齐键 node_id/FAC-*——与两图字段实查一致（TDM:L65 区 node_id；SPM FAC-* 前缀） | census §2.1 称 TDM-E-L4"13 子环节"——实查 cn_a 子环节 **14**（TDM-E-L4-01..-14，TDM:L2425~2826）。差 1 枚：TDM effective_from=2026-10-05 晚于 census 2026-09-24，图演化所致，非普查错 | census 全文未触 SPM 341 的 E0~E9 层内构成（layer/机制/状态分布）——本车道 st_e0~e9 十册为补充挖矿 |
| census §2.1 判"交易执行流不建新图，TDM 已有 L4+X-S2"——实查 L4（15 cn_a）与 X-S2（7）骨架确在 TDM，判 гео成立 | census §1 称 FACTORY 校验=FACTORY-MAP gate142——实查 SPM 图守卫为节点 FAC-MAP-M-001/002（SPM:L4879/4893，MOD-BT-080/081），两说相容但 census 未记录 gate 与图内守卫节点的对应 | census §2.1 未触 TDM 逐节点回测可考性——本车道引用 H9 逐条判定并机械复算对平（§2 各表） |
| census §1 记 TDM 对齐键与 DECISION-MAP gate138/FACTORY-MAP gate142 在册——本车道未复核对 gate（not_mined，不判） | 无其他矛盾：census §0"~16 张全景图"预期、图11/12/13 机生真源清单不属本车道两图范围，不判 | census 未记录 SPM counts 块缺失与 17 边结构性事实——chief B1 §3.2 已记，本册引用不重复挖 |
| census §2.2 X-S2"6 子环节"——实查子环节 S2-01..06 恰为 6（TDM:L3875~4069），一致 | | |

## 4. 与 chief_fullchain（B1 骨架 + 02 缺口账）交叉验证

- chief 01 §1 表：TDM 182（entry132/position18/exit19/portfolio13）/257 边/24 cells——本车道机械复算全一致（flow 计数 132/18/19/13；edges 257；cells 24，states 六态）。
- chief 01 §1 表：FACTORY 341/仅17边/built315+partial12+pending14/counts 块空——本车道复算全一致。
- **矛盾点（新）**：chief 01 §2 丙/丁段 TDM 分族账——ENV-14"组合与预算"记 6 节点，而本车道同口径（F-FLOW+C1+C2，C3 归 ENV-16）应为 **7**（TDM:L161,4114,4150,4206,4248,4287,4321）；且四枚终端聚合点中 E-FLOW/F-FLOW 在 chief 21 环节分表无显式落位（ENV-08=L0+L1=15、ENV-16=C3+E9=15 均不含），chief 分组合计 180 vs 全集 182 差 2。属分组账不闭合，不影响 182 全集本身。
- chief 02 §4"骨架断链组"（F16-F20 进货车道复活/D13-20 竞价窗闸恒 skipped 等）属图13/数据链域，本车道只在 st_data_legs 引用不代挖。
- chief 02 §1 P0 实盘 Flip 组（GAP-1 bridge-execute sim→real 等）与 st_e7 的 pending 件 FAC-E7-M-006（MOD-BT-222 模拟盘日链接电执行体，SPM:L4137）互为印证——工厂侧该腿标 pending，总包侧标"他队施工中"，两账一致。

## 5. 新发现矛盾点汇总（供总包矩阵考试命题）

| # | 矛盾 | 甲方口径 | 实查 | 判读 |
|---|---|---|---|---|
| C1 | 骨架节点计数 | 任务书/常识"16 骨架+325 机制" | 10 stage+7 lane=**17** 骨架，机制 **324**（SPM:L68 起 node_type 字段机械统计） | 图上新真相；E1 实挂 7 车道（含 E1F），"六车道"命名漂移（SPM:L90 stage 名 vs L240 FAC-E1F） |
| C2 | census L4 子环节数 | census §2.1"13 子环节" | 14（TDM:L2425~2826） | 图演化（effective 2026-10-05），census 需注记行 |
| C3 | chief 21 环节 TDM 分组账 | ENV-14=6、分组合计 180 | 同口径 7；全集 182（E-FLOW/F-FLOW 无显式 ENV 落位） | 分组账不闭合，建议 chief 补注记；182 全集无损 |
| C4 | GPU Core 状态 | SPM FAC-E0-M-003 build_status=pending（SPM:L482） | #ARCH-366/W-173 gpu_core 冒烟实测 0.53s/格已在案（H9 §3.4 引） | build_status 疑滞后于实测进度，建议图侧复核（他队域，本车道不代修） |

## 6. 族子册索引（20 份）

| 族 | 子册 | 覆盖 | 计数 |
|---|---|---|---|
| E0~E9 | st_e0_compute / st_e1_idea_intake / st_e2_hypothesis / st_e3_construction / st_e4_exam_throat / st_e5_dedup / st_e6_intake_monitor / st_e7_paper / st_e8_assembly / st_e9_attribution | SPM 全部 341 | 18/66/8/80/82/5/15/23/35/9 |
| TDM 盘前与总闸 | st_l0_l1_premarket | LROOT+L0+L1(cn_a) | 15 |
| TDM 板块 | st_l2_sector | L2 cn_a | 29 |
| TDM 个股 | st_l3_stock | L3 cn_a | 25 |
| TDM 执行 | st_l4_exec | L4 cn_a | 15 |
| TDM 持仓/做T | st_p_daytrade | position_flow | 18 |
| TDM 离场 | st_x_exit | exit_flow | 19 |
| TDM 组合 | st_c_portfolio | portfolio_flow | 13 |
| TDM 数据与知识 | st_l9_alt | L9 | 44 |
| TDM 币圈 | st_crypto | C-L1/L2/L3/L4 | 4 |
| 数据供给腿 | st_data_legs | 借力挖矿（图12+chief 账，不占 182/341 口径） | — |

## 7. 本总册盲点自查（≥8 条，逐条表态）

1. **H9 判定转录风险**：182 的 A/B/C/D 逐节点判定系转录 H9 §1 表格（其证据=考卷/框架文件行号），本车道用 python 复算四类计数（16/26/118/22）与其 §0 完全对平，并抽核各族首末节点；但"近似判定"（P1-05、C2-02、S2-02 记 A）的语义衰减未重新验证。表态：转录可信度高一计数对平兜底，残留风险=低。
2. **接线级是本车道自定义口径**：L3/L4 以 node.module_ref 有无为机械判据，module_ref 指向 live 路径≠该模块运行中（可能死码）。逐模块活性验证=not_mined（超出只读骨架车道预算），已在各族子册标注"在岗=图上自述"。
3. **SPM build_status 未逐节点运行验证**：315 built 为图上自述；C4 矛盾点已证至少 1 枚（GPU Core）状态滞后。表态：骨架计数可靠，单件状态须以运行时为准。
4. **battle_map 映射未直查**：H9 §1.9 的 tdm_node_id 11/341 映射是 2026-10-05 PG 快照，本车道未连 PG 复核。表态：引用不背书，标注 evidence_insufficient（时效性）。
5. **边仅计数未逐边审**：TDM 257 边、SPM 17 边只做计数与主链/回灌边核对，未逐边语义核对（下游依赖边语义考古属图战役域）。表态：骨架层无影响，边层留给他队。
6. **state_matrix 24 cells 只计数**：格子内容含 Owner 资金分配门位（H9 S4 明示 AI 禁自填），本车道不审内容只记计数与六态名。表态：符合门位纪律。
7. **字段裁剪**：TDM data_refs/algo_refs/factor_refs/decay_scan_frequency 与 SPM design_refs/store_refs/compute_class 未逐节点转录进册（只取接线判级所需字段）。表态：有意裁剪防上下文超载，非漏判；需要时按行号回查原图。
8. **data_legs 族是借力挖矿**：图12（数据供给链）归 chief ENV-01..05 与 fig12 队，本册只做交叉引用与断供账转抄，不判其缺口细节。表态：不重复挖、不越界判。
9. **crypto 4 节点单列族**：为避免 182 重复计数，crypto 从各 flow 族表扣除、集中于 st_crypto；阅读 l0l1/l2/l3/l4 族册时须按 99 册全集口径对平。表态：口径已双写（族册+99）。
10. **TDM 策略挂载与 H9 判定并存**：如 X-FLOW 挂 STR-VREV-001（TDM:L135）但 H9 判 C——挂载是 live 域语义、判定是回测域口径，两轴不冲突但易误读；已在 st_x_exit 注记。表态：在册防误读，非矛盾。

## 8. 交接与边界

- 本册与 20 份子册全部为 `docs/_working/matrix_campaign/mining/` 下新文件，未触碰任何既有文件、未 git 操作、未 claim。
- 判定复用声明：H9 判定与证据（§2 各表"类别"列）、census 结论（§3 一致列）、chief 计数（§4）均引用原文，本车道新增价值=机械对平+接线级五档+E0~E9 层内构成全挖+4 项矛盾点。
- 晋升路径：status: draft → 总包矩阵考试采纳后由总包改判归档。
