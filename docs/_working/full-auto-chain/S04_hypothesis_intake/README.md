---
ttl: task_bound
title: S04 假说进货与预审挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S04 假说进货与预审（策略工厂 E0/E1/E2 段）

## 1 现状盘点（自动化状态+file:line 证据）

**结论先行：本环节是 S01-S03 之外自动化程度最高的一段——周六 10:00 计划任务已把"进货→预审→构造→翻译"串成一条链，但存在 deferred 滞留、F 车道断链、双台账无对账三个堵点。**

### 1.1 触发与编排（E0 算力闸 + E1 进货编排）
- 计划任务 `ZephyrAlpha_FactoryLaneC`：**已注册且 Ready**（PowerShell Get-ScheduledTask 实测，周六 10:00，StartBoundary 2026-09-14T10:00+08:00），动作为 `scripts/run_factory_lane_c.ps1`。
- `scripts/run_factory_lane_c.ps1:28-35` 全链条：`lane_c_formula_miner.py mine --top 10` → `factory_intake_pipeline.py run --with-lane-b --limit-precheck 15` → `factory_intake_pipeline.py construct` → `hypothesis_translator.py translate --seeds 5`（后两步是 S05/S06 供料， Owner 2026-09-15 全自动 mandate 加入）。
- 编排层 `scripts/backtest/factory_intake_pipeline.py`（MOD-BT-154）：`run` 子命令 L87-145 = E1D 三高→（可选）E1B 生成→E2 幂等预审自动接续；`_LANE_SPECS` L49-60 声明 D/B/C/F 四车道规格；`preflight_compute_gate` L70-84 每车道开工先问 E0 闸。
- E0 拉式闸 `scripts/backtest/compute_window_gate.py`（MOD-BT-151）：`classify_window` L67-75（交易日 <15:30 = light_only）、`gate_decision` L83-98（日历未知对重任务 fail-closed `REASON_DENY_CALENDAR_UNKNOWN` L90-92）。**实证**：`.runtime/logs/factory_lane_c.log` 2026-09-14 07:10/07:11 两次 `gate_deny_trading_hours` exit 3（盘中手动点火被拒）——闸门真实生效；周六 10:00 属休市日=heavy_ok 放行。

### 1.2 五车道进货现状
| 车道 | 模块 | 台账 | 自动化 | 存量 |
|------|------|------|--------|------|
| A 社区 | MOD-BT-035（人工收集版） | data/strategy_intake/raw_manifest.csv | ❌ 无爬虫（人工 C1 收集） | **597 条** |
| B AI 生成 | `lane_b_idea_generator.py`（MOD-BT-150）：12 主题种子 L56-59、内容寻址去重 L100-103、出生证 L106-117、LLM 经 OllamaChat(LSG) | lane_b_candidates.csv | ✅ 随周批 `--with-lane-b` | 4 条 |
| C 公式挖掘 | `lane_c_formula_miner.py`（MOD-BT-155）：E0 问闸 L353-356、白名单 fail-closed（config/factor_mining_whitelist.yaml L52） | lane_c_candidates.csv | ✅ 周六 10:00 首动作 | 10 条 |
| C2 智能体 | `lane_c2_agentic_miner.py`（MOD-BT-158） | lane_c2_candidates.csv | 部分（会话触发） | 8 条 |
| D 产业链三高 | `three_high_screen.py`（MOD-BT-090） | three_high_candidates.csv | ✅ 随周批 run | 40 条 |
| F 组合网格 | factory_grid_executor（MOD-BT-196），`factory_intake_pipeline.py:63-67` 解析最新 grid_* manifest | grid_20260915-*/（5 批已落盘） | ⚠️ 半断（见堵点 2） | manifest 若干 |

### 1.3 E2 预审（MOD-BT-091）
- `scripts/backtest/hypothesis_precheck.py`：六问 prompt（机制/前视/成本/可证伪/同义反复/边界）L80-95；verdict 三态+理由码代码生成 L55-62；解析失败关键词兜底 L134-145；deferred 不冤枉想法（LLM 异常→defer_llm_unreachable L160-167）；落 CH 台账 c1_backtest.hypothesis_precheck（insert L194-211）。
- 幂等：`fetch_prechecked_ids` L183-191 `SELECT DISTINCT candidate_id`（**无 verdict 过滤**——堵点 1）。
- 四车道常态化消费：`factory_intake_pipeline.py:114-143` 逐台账 `hypothesis_precheck.run()`，漏斗汇总进 `report["e2_precheck"]`。
- P2 赛马计分板：`race_scoreboard` L252-269 + `cmd_race` L272-302（按 birth_channel 聚合预审漏斗；代码自述 E4 层赛马"待首批候选进入考试后自动可比"）。

### 1.4 注册表/图谱锚点
- 蓝图真源 config/strategy_production_map.yaml：E0 L33/E1 L34（五车道 L66-189）/E2 L191-210，edges L366-381，全图三铁律 L18-22（运动员不兼任裁判/量越大及格线越狠/事件触发禁定时器）。
- E2 store_refs=预审判定记录（永久），feedback_loops L383-385：E9→E2 归因回灌、E6→E1 衰减反馈——**两条回灌均为声明未接线**（见堵点 5）。

## 2 六向挖矿日志表

| 轮 | 方向 | 矿脉 | 判定 | 关键产出 |
|----|------|------|------|---------|
| 1 | ①上游 | F 车道 grid manifest→E2 供料 | signal | grid_20260915-* 5 批已产 manifest，但 `_LANE_SPECS` L57 自注"E2 消费器需按 recipe_id/values_json 解析（跨线协作项，E2 侧适配器待挂）"——recipe 行不是 hypothesis_zh，E2 跑不到 |
| 2 | ①上游 | lane A 社区货源自动化 | signal | 597 条存量为人工收集；无自动爬取；扩容候选 Scrapling（config 图 L94 引 github.com/D4Vinci/Scrapling）；E6/E9→E1 反馈回灌仅蓝图声明 |
| 3 | ②下游 | E2 台账 verdict 流向 | signal | `fetch_prechecked_ids` L188-190 DISTINCT 不分 verdict → **deferred 候选永久滞留**，无重审队列（注释自称"deferred 可重跑语义"只在幂等查询失败降级时才成立） |
| 4 | ②下游 | E4 层赛马可比性 | noise | race 计分板只到 E2 漏斗；E4 层聚合无件（须先有 S06 首跑数据），本轮无可入图新发现 |
| 5 | ③机制 | LLM 假说生成/预审业界（全网） | signal | FaVOR arxiv.org/html/2608.30192v1（arXiv，2026，回测前机制验证=本项目 E2 同构，蓝图已引）；AlphaAgent arxiv.org/html/2502.16789v1（KDD 2025，假说生成→因子→评估闭环+抗衰减正则，蓝图"借监不引码"）；RD-Agent(Q) arxiv.org/abs/2505.15155（Microsoft Research，2025，数据为中心因子/模型自动 R&D 闭环）；Alpha-R1 arxiv.org/html/2512.23515v2（2026，RL 对齐的免回测五维 AlphaEval 快筛——对应蓝图"E4a 免回测快筛"开放决策点 7）；FITEE LLM alpha mining 综述 jzus.zju.edu.cn/iparticle.php?doi=10.1631/FITEE.2500386（浙大学报，2026） |
| 6 | ④后端 | E0 闸+计划任务实证 | signal | FactoryLaneC Ready（首次全链触发=2026-09-19 周六 10:00）；factory_lane_c.log 证实闸门拒盘中点火 exit 3；ps1 首命令 exit 3 时 `$ErrorActionPreference="Stop"`+`2>&1|` 在 PS5.1 有 stderr ErrorRecord 中断风险（后三命令未在旧日志出现，09-14 版本仅 mine 命令，待首跑核验） |
| 7 | ⑤前端 | 进货漏斗可视化 | noise | 前端无 factory 进货/预审漏斗面板；报告仅 JSON stdout+日志。按纪律只登记不施工（S12/S13 告警推送施工时顺带） |
| 8 | ⑥数据字段 | 台账字段完整性 | signal | CSV 进货台账列齐（candidate_id/hypothesis_zh/birth 三件套）；但 E2 判定在 CH、候选在 CSV——双存储无对账件；F 车道 recipe_id/values_json 字段无假说文本映射=GAP |

**计数：signal 6 / noise 2 / 受阻 0**（全网搜索 2 次均命中，无 429）。

## 3 业界与开源对照

- **回测前假说过滤已是业界共识方向**：FaVOR（arXiv 2026）把假说拆成可观测市场条件+分布证据先验检查再决定是否花回算力——本项目 E2 六问框架同构且更轻（本地 8B）；差距=FaVOR 有分布证据检查，本项目纯 LLM 单审、无第二意见/无证据检索。
- **闭环自动 R&D**：RD-Agent(Q)（Microsoft 2025）=假说→实现→回测→反馈全闭环，含因子与模型双轨；本项目五车道+E2+E3 已具雏形，缺反馈回灌（E6/E9→E1/E2）。
- **抗 alpha 衰减**：AlphaAgent（KDD 2025）用原创性/经济逻辑/简洁性正则对抗衰减——本项目 E2 六问中"同义反复"一问对应，但无量化原创度检查（lane_c2 AST 原创检查是同思想的代码版）。
- **免回测快筛**：Alpha-R1 的 AlphaEval 五维（无需回测评估因子）为蓝图"是否拆 E4a/E4b"开放决策点提供业界先例。
- A 股适配闸：五车道产出均声明不涉及做空/高频（lane_b prompt L71-72 显式约束），适配成立。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 断链等级 |
|---|------|------|---------|
| 1 | **deferred 候选永久滞留**：幂等判重不区分 verdict，LLM 不可达/解析失败转 deferred 后永不重审 | hypothesis_precheck.py:188-190 | 中（产能漏损+想法冤死） |
| 2 | **F 车道 E2 适配器未挂**：grid recipe 行进不了预审，进货即断 | factory_intake_pipeline.py:57,63-67 | 中（车道空转） |
| 3 | lane A 597 条存量无自动进货、无增量爬取 | raw_manifest.csv 598 行（597 条+表头） | 低（存量够用，增量欠账） |
| 4 | E2 单审无复核：单 LLM 单次判定 pass/reject，无第二意见/证据检查 | hypothesis_precheck.py:156-167 | 低（FaVOR 式增强=增强项） |
| 5 | E6/E9→E1/E2 反馈回灌未接线（蓝图 feedback_loops 声明） | strategy_production_map.yaml:383-385 | 低（终局有位，时序未到） |
| 6 | CSV 候选台账与 CH 判定台账无对账件（candidate_id 双写一致性靠约定） | factory_intake_pipeline.py:118-131 | 低 |
| 7 | `--limit-precheck 15` 周批上限 vs 存量 62 条候选（B4+D40+C10+C2 8）：消化速度 < 进货速度时积压 | run_factory_lane_c.ps1:32 | 低（可调参） |
| 8 | E1C 白名单审定制=Owner 门：无人值守下算子空间冻结（合规设计，非缺陷，登记产能边界） | config/factor_mining_whitelist.yaml + 蓝图裁定 | 边界登记 |

## 5 施工项建议（具体到文件/函数/验收标准）

| 项 | 内容 | 验收标准 |
|----|------|---------|
| S04-G1 | deferred 重审队列：`hypothesis_precheck.fetch_prechecked_ids` 改为排除 `verdict='precheck_deferred'` 且 `prechecked_at` 距今 ≥7 天的候选（或加 `--recheck-deferred` 子命令挂进 run_factory_lane_c.ps1） | 造 1 条 defer 假说→7 天后周批自动重审并落新 verdict 行；台账只增不被破坏 |
| S04-G2 | F 车道 E2 适配器：`factory_intake_pipeline.run` 增加 recipe→hypothesis_zh 文本化（recipe_id/values_json→中文假说句），卸入 lane_f_candidates.csv 再进 E2 | grid manifest 候选能出现在 e2_precheck 漏斗统计中 |
| S04-G3 | 双台账对账轻检查：`factory_intake_pipeline.py race` 子命令增列"CSV 有而 CH 无判定"计数并告警 | race 输出含 missing_verdict 字段；人工可据此补跑 |
| S04-G4 | （挂起排期）lane A Scrapling 增量爬取：解锁条件=站点白名单与合规审定（Owner 门）；先降级为一次性脚本探路 | —— |
| S04-G5 | （挂起排期）E2 第二意见（FaVOR 式分布证据预检）：等 E2 首批拒绝率数据出来再定是否二段审 | —— |

## 6 封矿结论

- **矿脉封矿**：连续两轮 noise 未出现（8 轮 6 signal），但候选方向已被 S04-G4/G5 挂起封批，长尾（E2 prompt 多语言稳健性、社区货源 NLP 摘要）登记待后续批次。
- **方案封矿**：无。E0 拉式闸/E1 五车道/E2 六问总闸均在终局全貌有位（消灭 Owner 审核 ideas 的人工），全部维持。
- **终局视角**：本环节周批链（FactoryLaneC）就是终局形态的骨架，施工项 G1-G3 打完即可宣称"想法进货→预审"无人值守；前端呈现归 S12/S13 统一施工。

## 7 施工班状态回填（2026-09-15）

- 本环节 G1-G3 施工项未接单，维持登记（deferred 重审队列/F 车道 E2 适配器/双台账对账均未动）。
- 关联进展（兄弟班 23a4fa4b01）：run_c4_batch_due 加 `--defer-emit` 与 IS/OOS 双窗编排对齐——E2 下游消费时点改为 OOS 齐后统一触发，不改变本环节自身欠账。
- FactoryLaneC 首次全自动全链触发=2026-09-19（周六）10:00，届时首验堵点 6（ps1 中断风险）与 `--limit-precheck 15` 消化速度。
