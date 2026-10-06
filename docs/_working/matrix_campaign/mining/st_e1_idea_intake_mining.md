---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e1_idea_intake —— E1 想法进货（SPM 66 节点，1 stage + 7 lane + 58 mech）

- 真源: `config/strategy_production_map.yaml`；行号=SPM:L*。
- 职责: 七条车道持续进策略想法与假说原料（社区货源/AI 生成/公式挖掘/产业链三高/模型基线/网格仅代码/全网搜索）。
- 计数: 66 = stage 1(partial) + lane 7（A built；B/C/D/E/G/F partial） + mechanism 58（built 57 / pending 1）。
- **命名漂移（补充挖矿发现）**: stage 名"想法进货（六车道）"（SPM:L90），实挂 **7 条 lane**（edges 含 E1→E1F，SPM edges L4907 区；FAC-E1F 在 L240）——"六车道"是 E1F 加入前的旧称。

## 1. 族内节点全清单

骨架（8）：

| node_id | 名称 | 状态 | module_ref | 行 |
|---|---|---|---|---|
| FAC-E1 | 想法进货（六车道）stage | partial | MOD-BT-154 | SPM:L90 |
| FAC-E1A | 车道A-社区货源 | built | scripts/backtest/strategy_intake_inventory.py | SPM:L108 |
| FAC-E1B | 车道B-AI生成 | partial | MOD-BT-150 | SPM:L125 |
| FAC-E1C | 车道C-公式挖掘机 | partial | MOD-BT-155 | SPM:L145 |
| FAC-E1D | 车道D-产业链三高 | partial | MOD-BT-090 | SPM:L170 |
| FAC-E1E | 车道E-模型基线 | partial | MOD-BT-084 | SPM:L193 |
| FAC-E1G | 车道G-全网搜索进货 | partial | MOD-AUTO-E1G-001 | SPM:L217 |
| FAC-E1F | 车道F-网格仅代码 | partial | code:scripts/backtest/factory_grid_executor.py | SPM:L240 |

机制（58，按子族）：

| 节点段 | 数 | 名称（首末） | 状态 | module | 行 |
|---|---|---|---|---|---|
| FAC-E1-M-001~012 | 12 | 进货编排流水线 / … / 时间周期分析 | 11 built + M-002 **pending**（进货台账对账核验器 MOD-BT-231） | MOD-BT-154 等 | SPM:L675~826 |
| FAC-E1A-M-001~003 | 3 | C2 粗筛成绩灌表 / 社媒情绪采集 / 网页爬取引擎 | built | strategy_intake_inventory 等 | SPM:L826~865 |
| FAC-E1B-M-001~004 | 4 | AI生成车道B / 嵌入模型下载器 / 本地LLM池 / API LLM池 | built | MOD-BT-150 等 | SPM:L865~919 |
| FAC-E1C-M-001~008 | 8 | gplearn轨 / MCTS第三轨 / 自动特征发现 / GP策略发现 / LLM进化搜索 / 因子投票挖掘 / 算子白名单 / 搜索空间预注册 | built | MOD-BT-155/202 等 | SPM:L919~1016 |
| FAC-E1D-M-001~010 | 10 | 产业链三高筛选 / 图谱增补暂存 / 图谱入图器 / 板块盘中聚合 / 板块报告 / 财报解析 / LLM基本面 / 事件链因果图 / 公告NLP / 政策主题映射 | built | MOD-BT-090/193/203 等 | SPM:L1016~1144 |
| FAC-E1E-M-001~009 | 9 | 分位数回归基线 / Kronos适配 / Kronos微调 / ML模型工厂 / KAN密度头 / PatchTST / QNN两阶段 / 模型版本注册表 / 时序增广 | built | MOD-BT-084/195/204 等 | SPM:L1144~1259 |
| FAC-E1F-M-001~002 | 2 | 网格批次执行器 / F车道网格配方适配器 | built | factory_grid_executor / lane_f_grid_adapter | SPM:L1259~1282 |
| FAC-E1G-M-001~010 | 10 | 车道G胃点菜 / 新闻连接器 / AI舆情分析器 / 新闻-标的关联 / 夜间舆情窗口 / 全域事实台账 / 研报采集 / 政策预期 / AI搜索矿脉 / AI源注册表 | built | MOD-AUTO-E1G-001 等 | SPM:L1282~1397 |

## 2. 接线现状与缺口判定

- 已接线：六条半车道机制面 built（58 枚中 57 built），E1F 车道直通现行考卷（factory_grid_executor 即 T1/T2 考卷执行器，H9 §0 基线）。
- 缺口 1（图内）：FAC-E1-M-002 进货台账对账核验器 pending——进货病历的对账闭环缺位。
- 缺口 2（跨册）：车道 lane_c 公式挖掘机停摆 14 天属 chief 02 §4"骨架断链组"（F16-F20 五条进货车道复活）——SPM 状态标 partial 与运行态断链并存，图账与运行账两回事。
- 可考性：E1 的"进货→考试"链路已由 F 车道实考（T1/T2）；其余车道产出进 E2 预审后走 E3/E4，链条完整。

## 3. 修复建议（一句话）

M-002 台账对账核验器补落地；lane_c 复活按 chief 02 §4 归属队列走，图侧把"六车道"改名"七车道"或注记 E1F 后加。

## 4. 交叉验证

- chief 02 §4：F16-F20 进货车道断链（lane_c 停 14 天）——与 FAC-E1C partial 互证，引用不代修。
- census 图12/图13 域（数据供给）不属本族；E1 的数据原料腿另见 st_data_legs。
- H9 §1.9 TDM-E-L9-D1（因子组合挖掘=mcts_expression_search）与 E1C-M-002 MCTS 第三轨同源——进货层与 TDM 知识供给层的交叉点，双册互链。
