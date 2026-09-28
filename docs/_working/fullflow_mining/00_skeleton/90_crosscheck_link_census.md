---
created: 2026-09-26
ttl: task_bound
title: 全环节总册交叉验证与补漏（90_crosscheck_link_census）
session: st-fflead-census
---

# 全环节总册交叉验证与补漏（90_crosscheck_link_census）

> 立册 2026-09-26 ｜ 只读交叉验证册：**不改任何既有册、不写代码、零 git 写操作**。
> 被测：`00_全环节总册.md`（F01–F122/13 段）＋ `00_skeleton_fullflow.md`（M0 76 环节）。
> 口径真源：作业簿模板与挖干判据=`../00_orchestration.md:15-31`。

## 一、定义与边界

- **做**：①四轴穷尽性验真（TDM/ROOR/SOP/代码侧）→ 候选漏项清单；②F ↔ L01–L09 双编号映射与收敛建议；③M0"75/76＋扩展项未挖"追索到原文锚点；④抽 6 环节做三级枚举并测算"每子类目单独成册"规模，供总筹排并发。
- **不做**：逐环节挖子孙内容（派单后由各车道做）；不裁 Owner 门位事项（一律写 §六 待裁）。
- 环境实测：`export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version` → **Python 3.12.8**。

## 二、六向台账

| 向 | 实证 |
|---|---|
| 上游输入 | 4 条独立证据轴实测：TDM 顶层节点 **182**（E128/P18/X19/F13/C4）｜ROOR `registry_id` **77**（summary=76）｜SOP **11 个 `*_sop/` 目录＋3 根文件＝14 条目、48 md**｜代码侧 `src/zephyr` 顶层域 **57**＋能力卡 **44**；取数命令见 §七 |
| 下游消费 | 总筹派单册（本册 §三·H 规模测算＝并发波次输入）＋各车道作业簿（现行 115 md 册） |
| 自动化触发 | 无触发器（纯调研只读册）；本册发现的"手工静态清单漂移"病灶的反查脚本属 §五 建议，须另开工单，不在本册自施 |
| 真源与注册表 | 环节清单真源=`00_全环节总册.md:20-207`；覆盖率真源=`00_skeleton_fullflow.md:165-170`；第二套编号真源=`docs/_working/decision_map_campaign_20260924/links/L0*_*/SKEL.md`（9 份）＋`09_link_skeletons.md:23-46`（四套切分自认） |
| 门禁与质量尺 | orchestration §三 挖干三态；本册每个数字带可复跑命令，无命令处一律标"查无＋检索面"（§三·G 已标 1 处） |
| 当前运行状态 | **绿**（四轴 4/4 完成实测）——复跑=`bash §七` 全部命令，输出应与本册表格逐项一致 |

## 三、子模块清单（四轴验真＋映射＋75/76 追索＋三级规模）

### A 轴 1：TDM 地图 `config/trading_decision_map.yaml`

| 项 | 实测 | 册内声称 | 判定 |
|---|---|---|---|
| 顶层节点 `^- node_id:` | **182** | F 册 182（`00_全环节总册.md:73`）；M0 T1 与 `09_link_skeletons.md:27` 均称 **138** | 182 成立；**138＝过期口径**（M0:33、09:27 两处须勘误，本册不改） |
| 分流 E/P/X/F/C | **128/18/19/13/4** | F 册"entry 132/position 18/exit 19/portfolio 13" | entry 132＝128＋crypto 4 混计 → **口径漂移 D-1**；P/X/F 三数吻合 |
| E 层细分 L0/L1/L2/L3/L4/L9 | **5/9/29/25/15/44** | F37–F41＋F30–F36 | 六层全落环节 ✅ |
| `module_ref:` 行 / null | **182 / 38** | F 册 §二 只点名 7 处断链 | **38 个登记态节点未逐一对应环节**＝轴 1 候选漏项面（须生成器出"null 节点→F 环节"映射表逐条判） |
| 顶层结构轴 | `nodes`:26／`edges`:5274-5558（**254 条边**）／`state_matrix`:5556（**82 行**）／`portfolio_plan`:5639 | F 册只用 nodes＋edges（§二 DAG），**未把 state_matrix、portfolio_plan 当环节** | **候选漏项 A-1、A-2**（地图内一等公民，无 F 位；09:34 亦注"state_matrix=配置矩阵非节点"） |

### B 轴 2：ROOR `docs/registry_of_registries.yaml`

实测：`grep -c "registry_id:"` = **77**；`summary.total_registries` = **76**（:881）→ F 册 §五.3 自述漂移**复现成立**（移交 M3，不在本册修）。
机械反查（id 或 `physical_path` 文件名是否出现在 F 册全文）：**55/77 未出现**。逐条语义甄别后＝**真候选漏项 15 项 ＋ 登记面欠账 40 项**（后者环节已在、册内未点注册表名，属"出口真源未登记"而非环节漏项）。

| # | 候选漏项（注册表） | 判据（F 册为何无位） | 建议落位 | 优先 |
|---|---|---|---|---|
| B-1 | REG-TECHNICAL-INDICATOR-001 技术指标册 | 无"指标库"环节（F52 只覆盖 DAL 27 算法） | 新增或并入 F52 | P1 |
| B-2 | REG-PAT-001 图表形态册 | 同上 | 并入 F52 | P2 |
| B-3 | REG-EXA-001 执行算法册 | F55 有码无册（出口真源未登记） | F55 补真源 | P2 |
| B-4 | REG-SEAT-001 席位册 | 龙虎榜席位数据线无环节 | 新增（C 段源线） | P1 |
| B-5 | REG-EVT-001 事件日历册 | 事件线（除权/披露/日历）无环节，F30 仅并列字面 | 新增（A/C 段） | P1 |
| B-6 | REG-MAC-001 宏观指标册 | F38 有宏观传感器，无宏观数据线环节 | 新增或 F38 补子目 | P1 |
| B-7 | REG-FLD-001 字段字典 | 字段/schema 治理面无环节 | 新增（A/K 交界） | P1 |
| B-8 | REG-DATAFLOW-001 数据资产册 | 数据资产台账无位（F11 只挂交叉轴） | 新增或并入 F11 | P1 |
| B-9 | **REG-MIGRATION-001 迁移册** | **DB schema 迁移环节缺位**（F07 只写 depgraph） | **新增 P0**（架构数据=DB 侧写通道） | **P0** |
| B-10 | REG-ARCH-ISSUE-001 架构问题册 | 架构议题台账无环节（K 段空白） | 新增（K 段） | P1 |
| B-11 | REG-INTF-001 接口契约册 | F110 只覆盖 freeze_manifest＋error_code | 并入 F110 | P1 |
| B-12 | **REG-STATE-VOCAB-001 状态词表册** | GATE-VOCAB 是**真实在拦的门禁**（死信 0036 死于词表，`00_orchestration.md:46`）却无环节 | **新增（K 段）P0** | **P0** |
| B-13 | REG-TASK-META-001 任务卡元数据册 | 自动化任务卡元数据无环节 | 新增（I 段） | P1 |
| B-14 | REG-TEMPLATE-001／REG-FRONTMATTER-001／REG-SCRIPT-001·002／REG-CAP-001 | F117 只写"目录册＋资产索引"，文档/脚本/技术栈资产族无位 | F117 细化或新增 1–2 环节 | P2 |
| B-15 | REG-CROSS-002 跨模块依赖册／REG-CATALOG-001 master_index／REG-SM-001 状态机册 | F109 只点 ROOR+master_index+一致性契约，跨模块依赖与状态机注册无位 | 新增或 F109 子目 | P2 |

### C 轴 3：SOP 方法论族

实测：`ls -d sop/*/` = **11 个 `*_sop` 目录**；`ls sop/` = **14 条目**（11 目录＋`README.md`＋`index.md`＋`audit_prompts_20_ai.md`）；`.md` 总数 **48**。
判定：F 册 F116 行自述"12 目录实测"（`00_全环节总册.md:201`）与 M0 §五.3"12 族"＝把 11 目录＋根 audit_prompts 合算，**与 11 目录实扫不矛盾**（差 1＝`index.md` 未计入）；AGENTS §6"九族索引"是三数中最过期的一套。**环节层无漏项**，但族数口径三写并存 → §四 病灶-4。
SOP 声明步骤侧抽验：施工族 15 步（`construction_workflow_policy.md`，宪法 §0.4 指为 07 域真源）→ 落 F116 方法论面＋F97 commit 链（引用不重挖），无独立环节；回测族 sop_a/sop_b 七步循环→F66；数据源接入族工段③→F02。三处均有 F 位 ✅。

### D 轴 4：代码侧（`src/zephyr/` 顶层域＋`data/capability_cards/`）

实测：顶层目录（剔 `__pycache__`）**57**（F 册 :12 称"56 包"＝漂移 1，新增目录未刷新）；能力卡 **44**（与 M0 一致）；全仓 `.py` **3758**、二级目录 **393**、三级目录 **86**。
名称级未匹配：域 **17** 个、能力卡 **39** 张（后者的 `ai_perceive_l1`/`skill_dom_*` 多数已被 F86/F90 语义覆盖＝登记面欠账）。语义甄别后**真候选漏项 13 个代码域**：

| 代码域 | 判据 | 建议 | 优先 |
|---|---|---|---|
| `alt_data` | F31 只落 TDM 源线节点，无 alt_data 代码域锚点 | 新增（C 段） | P1 |
| `data_eng` | 数据工程/构建管道无位 | 新增（A 段） | P1 |
| `data_governance` | 与 F11/F109 对象不同（数据治理本体） | 新增（A/K 交界） | **P0** |
| `data_security` | 与 F88 LSG（LLM 防御）不同域 | 新增（K 段） | P1 |
| `market_data` | 与 F10/F03 存在双真源嫌疑 | 并入 F03/F10＋勘误 | P1 |
| `ml_train` | 训练线无环节（F19 仅"模型基线对台"） | 新增（B/J 段） | P1 |
| `ml_serve` | 推理/服务线无环节 | 新增 | P1 |
| `nlp` | NLP 线无环节（F30 千股千评/互动易的后端） | 新增 | P2 |
| `intelligence` | 情报线无环节（F96 胃＝产物 inbox 非域） | 并入 F96＋勘误 | P2 |
| `knowledge` | 知识面与 F93 图书馆边界未定 | **待裁**（§六 裁-5） | P2 |
| `infra_ops` | 运维域仅被 F85/F118 碎片覆盖 | 新增（I/M 段） | P1 |
| `infra_runtime` | 与 F71 AutoRuntime 是否同物未证 | **待裁**（§六 裁-5） | P1 |
| `gov_rule` | 规则域与 F101 关系未登记 | 并入 F101＋勘误 | P2 |

（`experiment_tracking`→F67、`red_blue_validator`→F100、`signal_quality`→F40、`strategy_factory`→F17/F23 已语义覆盖，不计漏项。）

### E 四轴合并结论：**122 环节有漏，非零遗漏**

- 四轴交叉后**去重候选漏项＝ 29 项**：轴 1 两项（A-1 state_matrix、A-2 portfolio_plan）＋轴 2 十五项（B-1…B-15）＋轴 4 十三项（代码域）＋轴 3 零项（口径漂移另计病灶）。
- 其中 **P0 级 4 项**：B-9 DB 迁移、B-12 状态词表（GATE-VOCAB）、D-`data_governance`、轴 1 的 38 个 `module_ref: null` 节点映射面。
- 另有**环节内缺口**而非环节缺口 2 项：L02 大盘情绪（2026-09-22 定桩独立状态变量，F38 只当传感器）与 L04 板块→个股传导（跨 F39/F40 无线）——见 §三·F。
- 结论表述：**F01–F122 编号无空洞**（实测 2 位 id 去重 99＝F01–F99 全在，3 位 23＝F100–F122 全在，合计 122 行，无重号无断号），但**环节集合不完备**，建议 122 → **~151 环节**（＋29，去重后按落位方案可缩至 ~140）。

### F F 编号 ↔ L01–L09 映射表（两套并存是事实，逐个给判定）

| L | 环节名（册题原文） | 对应 F 环节 | 判定 |
|---|---|---|---|
| L01_regime | 大盘状态判定（regime/六段相位） | **F38** | 一一对应 ✅ |
| L02_emotion | 大盘情绪链路 | **F38 子目**（六传感器之赚钱效应）＋F33（L9-V2 快照） | **无一对一**＝F 侧漏项（情绪升格独立状态变量未在总册落位） |
| L03_sector | 板块状态与轮动（八子块） | **F39** | 一一对应 ✅ |
| L04_stock_wire | 板块→个股传导（选股/成分映射/因子） | **F39→F40 跨段**（F40 只到"个股选择"） | **无一对一**＝F 侧漏项（传导线无位） |
| L05_t0 | 个股做T 链路 | **F43**（P2 做T与加减仓） | 对应 ✅（F43 含减仓，比 L05 宽） |
| L06_exam_alloc | 策略考试与条件共振上岗 | **F23**（E4 考试）＋F66/F68（回测预注册/GPU 格子） | 部分对应；**"条件共振上岗"在 F 体系无位**（最近似=F73 A/B 联赛/F74 转正门，均 design/missing 态） |
| L07_exec | 执行链路（下单/滑点/盘口） | **F41＋F53/F54/F55＋F46** | 一对多（L 粗 F 细）✅ |
| L08_risk | 风控链路（组合/回撤/熔断） | **F59/F60/F61＋F47＋F49** | 一对多 ✅ |
| L09_review | 复盘与监控 | **F37＋F50＋F28＋F81** | 一对多 ✅ |

反向：122 环节中 **99 个在 L 体系无对应**（L 战役只覆盖决策消费侧，映射 23 个）——L 体系天然不是全链册。
**收敛建议（不擅自改，交总筹裁）**：
1. **`00_全环节总册.md`（F 编号）作环节级唯一真源**；TDM yaml 保持节点级真源（两者不同粒度，不互斥）。
2. **L01–L09 降级为"TDM 决策子域视图"**，不退役：其 9 册含 135 行子块台账（实测各册子块行数 28/0/8/9/24/13/19/20/14，L02 用异 id 系＝该 pattern 下**查无**，检索面=对 `links/L02_emotion/SKEL.md` 跑 `^### ` 得 9 小节）＋四判据＋LK-xx 缺口编号，是**子块级证据资产**，退役＝净丢（违宪法 §4 内收判据"零触发零消费才退役"，此册有强消费）。
3. 补一层**机生映射表**（`L↔F↔TDM 节点`）由生成器产出，两套册只引用——理由：`09_link_skeletons.md:25-46` 自认仓内**四套切分并存**（九环节/TDM 138 节点/骨架覆盖审计五层 SKL1-5/battle_map 12 域），且已因此产生 138↔182 节点数漂移；不收敛则每轮都有人引用过期数。
4. **M0 76 编号（D/T/B/A/G/S/F/X）应退役**为映射表附注：F 册已逐行给 M0 列（`00_全环节总册.md:26-207` 每行末列）＝同真源可派生→必并（宪法 §4.2）。

### G M0"75/76 覆盖＋扩展项未挖"追索（原文为准）

- **那 1 个未覆盖环节＝ X1 SOP 方法论族**。锚点：`00_skeleton_fullflow.md:169`"若采纳 M7+扩展建议则 **75/76** = 98.7%（**仅 X1 SOP 族按口径挂总筹**）"；旁证 `00_skeleton_fullflow.md:114`（X1 归属列＝"未归属(总筹引用，禁重挖)"）、`:157`（漏项表第 20 行，口径"方法论=挖干判据输入，非施工环节"）。→ F 册已把它编为 **F116**（`00_全环节总册.md:201`），**编号层面闭合，"挖"的层面仍是口径挂起**（总筹引用不重挖），非真挖干。
- **"扩展项"具体所指**（=各车道补挖波，锚点 `00_orchestration.md:35` 原文"待挖＝扩展项未挖（各车道补挖波处理）"）：
  1. 备份 3-2-1 双链 → F09（`00_全环节总册.md:34` 标"M5 补挖项"）
  2. 冷库归档运维 → F08（`:33` 标"待深挖确认"）
  3. 反馈循环 FBL → F84（`:149` "M5 补挖项"）
  4. 环境与启动链 → F85（`:150` "M5 补挖项"）
  5. 性能水位台账 → **无独立 F 号**（M0 漏项表第 8 项 `00_skeleton_fullflow.md:145` 判"M5 已可覆盖(S4/S6)"，要求显式列台账）→ 挂 F79/F81 子目
  6. 管线路由调度属性（F122）→ `00_orchestration.md:40` 尾注"管线路由调度属性"留补挖波
  7. 报告生成 → F115（`00_全环节总册.md:195` 标"M6 补挖项"）
- **查无项 1 处**：M0 册内**没有**"扩展项"独立清单表（"扩展项"一词只在 `00_orchestration.md:35`）。检索面：`grep -rn "补挖\|扩展项" docs/_working/fullflow_mining/00_orchestration.md docs/_working/fullflow_mining/00_skeleton_fullflow.md` → 仅 4 命中（行号 35/40/41/170），无第 5 处。
- 另：M0 §三 的 24 漏项中 3 项待裁（X5/X6/X7）**已被总筹裁掉**（`00_orchestration.md:35`"研究域不编入/管线路由 M4M5 互引"），F 册对应 F121/F122 已落位（`00_全环节总册.md:206-207`）——此项无遗留。

### H 抽 6 环节三级枚举（父环节→子模块→子子模块）与成册规模测算

实测（口径：子模块＝锚定目录下的一级子包；子子模块＝子包内 `.py`；册=md 文件）：

| 环节 | 锚定目录 | 一级散 py | 子模块(目录) | 子子模块(子包内 py) | 三级目录 |
|---|---|---|---|---|---|
| F01 数据供给（数据） | `src/zephyr/data` | 70 | **10**（implementations 46／redundant_source 7／calendar 4／normalizers 4／connectors 3／wal_codec 3／symbol_normalizer 2／transport 2／satellite_geospatial_engine 1／config 0） | **72** | 0 |
| F65 回测引擎族（回测） | `src/zephyr/backtest` | 2 | **9**（core 22／regime_validation 12／services 10／implementations 5／io 3／_extensions 1／api 1／infrastructure 1／models 1） | **56** | 0 |
| F98 GateEngine 运行时门禁（治理） | `src/zephyr/gov_enforcement/rule_enforcement` | 34 | **5**（gate_engine 9／invariants 7／rule_engine 5／admission 1／task 1） | **23** | 0 |
| F86 AI 六族管线（AI 层） | `src/zephyr/ai_layer` | 1 | **9**（comparator 11／redline 10／heritage 7／scheduling 7／cleaning 6／intake 6／switch_engine 5／tools 5／perceive 4） | **61** | 0 |
| F77 数据调度常驻（调度） | `src/zephyr/trading` | 56 | **10**（trading_contracts 26／action_dispatcher 5／validation 4／runtime 2／_extensions 1／api 1／core 1／infrastructure 1／models 1／services 1） | **43** | **4**（trading_contracts 下） |
| F112 API server（前端） | `src/zephyr/frontend` | 10 | **9**（dashboard 23／implementations 6／_extensions 1／api 1／core 1／infrastructure 1／models 1／services 2／acceptance 0） | **36** | **3**（dashboard 2＋acceptance 1） |
| 合计 / 均值 | — | 173 | **52 / 8.7 每环节** | **291 / 48.5 每环节** | 7 |

全仓基数（同一命令族实测）：顶层域 57／二级目录 **393**／三级目录 **86**／`.py` **3758**。
现有册基数：`find docs/_working/fullflow_mining -name "*.md"` = **115**（含本册）；分车道＝m1 12／m2 9／m3 4／m4 7／m5 12／m6 5／m7 7／m8 5／01 策略工厂 19／02 TDM 决策 18／03 转正 4／04 知识供给 8／00_skeleton 3。

**规模测算（三档，供并发排单）**：
- **档 1｜环节册（父级）**：122 册（补 §三·E 的 29 个新环节后 ~151 册）；现 115 册已覆盖环节主体 → **新开 ≈ 36 册**。
- **档 2｜子模块单独成册（全量，不推荐）**：122 × 8.7 ≈ **1,061 册**（或按全仓 393 二级目录口径＝393 册）→ 并发 10 班＝**39–106 波**，超预算且违宪法 §4.1 净零。
- **档 3｜阈值升册（推荐）**：子包 `.py` ≥15 才单独成册。样本实测 **5/52＝9.6%** → 393 × 9.6% ≈ **38 册**（阈值放宽到 ≥10 则 8/52＝15.4% → ≈ **60 册**）。总规模 ≈ **122＋38＝160 册（宽口径 182）**，扣现有 115 → **新开 45–67 册**。
- **派单建议**：先开"29 个候选漏项"确认册（29 册，1 波并发 10＝3 波，每册仅要求六向台账 30–60 行）；再按档 3 开 38 册（4 波）；每环节册内三级不另开册，用"子模块节"承载，`>15 py` 才拆。P0 优先序＝B-9 迁移 / B-12 状态词表 / data_governance / 38 个 null 节点映射表 → 建议同波首发 5 册（含 1 册机生映射表）。

## 四、堵点与病灶

1. **手工静态清单必然漂移（宪法 §9.5 红线）**：F 册 122 环节表、§三 DAG、§五漂移表均手工。实测已现 4 处数值漂移：M0/09 的 TDM 节点 **138 vs 实测 182**、F 册 entry **132 vs 实测 128**、ROOR **76 vs 77**、F 册顶层包 **56 vs 实测 57**。→ 根因＝无"F↔TDM↔ROOR↔src 域"生成器；修法＝一张机生四向对账表（草案 §五-1），预估 1 个施工袋。
2. **38 个 `module_ref: null` 节点无环节归属**：登记态节点是否"待建"还是"该并入现有环节"无机械判定；F 册只点名 7 处断链 → 剩 31 处未判（其中 C 段 F30/F31 系 44 个 L9 节点占大头）。
3. **双编号并存无映射真源**：`09_link_skeletons.md:25` 自认四套切分并存，L01–L09 与 F 各写各的上下游；跨战役引用靠人名记忆（本册 §三·F 是首份书面映射）。
4. **SOP 族数三写并存**：AGENTS §6"九族"／M0 §五.3"12 族"／F 册 F116"12 目录实测"／本册实扫 **11 目录＋3 根文件**；F 册与 M0 把根 `audit_prompts_20_ai.md` 计入族，`index.md` 未计 → 口径未定义即"族"的分母。属文档矛盾＝事故级（宪法 §4.3）。
5. **F111 与宪法入口冲突（活跃漂移）**：`agents.md` §7 已由他会话改为"仪表盘=`api_server.py`（8890；**app_panel.py 已弃用**）"，而 F 册 F111（`00_全环节总册.md:191`）仍标 `app_panel.py` built、M6 待裁仍挂"app_panel 退役时点"（`00_orchestration.md:41`）。本册只登记，不裁（见 §六 裁-3）。
6. **情绪线/传导线两条已定桩未落环节**：`09_link_skeletons.md:40-44`（2026-09-22 情绪独立状态变量定桩、板块升格独立层待追认 sector_gap_list G9）→ F 册 F38/F39/F40 未反映，属"在途定桩未同步"。
7. **登记面欠账 40 注册表**：环节在、册内未点真源文件 → 下游按 F 册派单会漏读真源（如 F64 只写"catalogs/universe、benchmark、cost_model_registry.yaml"合写，未给 REG 号，机检不可达）。

## 五、提速与合并机会

1. **一个生成器出四张对账表**（替代 4 次人工交叉）：`F↔TDM 节点`／`F↔ROOR REG-id`／`F↔src 顶层域`／`F↔capability 卡`，输出 `*.yaml` 机生册＋F 册只 `include`。净零：可退役 M0 的"三、漏项清单"手工表（同真源可派生→必并）。
2. **双编号收敛为一张 YAML 映射真源**（§三·F 表机生版），L 册与 F 册各引用自身视图，停止散文复述计数（宪法 §4.3"计数用字段不写死"）。
3. **候选漏项册合并开**：轴 4 的 13 个代码域同属"未编目域"一族，可 1 册分 13 节先判归属（数据治理 3 个＋ml 2 个＋infra 2 个＋其余 6），比 13 册省 12 个并发位。
4. **轴 2 的 B-1/B-2/B-5/B-6 合并为 1 册**："行情因子类注册表族（指标/形态/事件/宏观）"，同真源可派生。
5. **复用 115 册模板**：本战役六向台账模板已在 9 套车道跑通，新增册直接套表头，禁另起格式。

## 六、自审闸三态

**本册自审＝挖干可施工**（四轴各向均有实测命令＋输出；候选漏项逐条给判据与落位；无凭记忆数字）。

作业三态：
- **挖干可施工**（总筹可直接派）：§三·E 的 29 项候选漏项确认册；§三·H 档 3 的 38 册升册清单；§四-1 生成器工单。
- **待挖**（缺证据，须再派）：①38 个 `module_ref:null` 节点逐条判归属（缺"节点→环节"机械映射）；②L02 情绪/L04 传导子块在 F 体系的重切（缺 sector/emotion gap 册的最新态）；③其余 116 环节的三级枚举（本册只抽 6）；④ROOR 40 个登记面欠账的 REG 号补注。
- **待裁（不自裁，选项＋建议，交总筹／Owner 门位）**：
  - **裁-1｜ROOR 76 vs 77 收敛**〔涉**注册表净删**＝Owner 门位，本册不自裁〕：选项 a 补 `summary.total_registries=77`（不动条目）／b 判 REG-METAQ-001 为 PG 快照双计并删条目（净删）。建议＝**a**（M0 §五.4 同族问题也是刷新口径优先；b 须 Owner 点头）。
  - **裁-2｜双编号收敛**：选项 a F 册作环节唯一真源＋L01–L09 降级视图＋M0 编号退役（本册建议）／b 三套并挂映射表／c 反以 L 为骨架。建议＝**a**；c 否（L 只覆盖 23/122，天然非全链）。
  - **裁-3｜F111 入口口径**〔涉 **production 流转**＝Owner 门位，M6 已挂晨报，勿重复自裁〕：建议＝本册只登记矛盾，待 M6 退役时点裁定后由 F 册 owner 改行。
  - **裁-4｜F62 合规门接线前置＝人工向券商报送程序化报告**：不自裁、不施工；建议＝保持 fail-closed，Owner 报送回填 `broker_ack` 后再开接线工单（M7 晨报清单原文，`00_orchestration.md:42/56`）。
  - **裁-5｜环节总数 122→~151 的改写授权**：涉及重写被验册。建议＝总筹先批"候选漏项确认册"，由确认结论再决定并册/新增，避免一次性扩表造成新的手工漂移。
  - **裁-6｜`infra_runtime` 是否与 F71 AutoRuntime 同物、`knowledge` 与 F93 图书馆边界**：架构级取舍，建议＝分别归 F71 子目／F93 扩展，由 owner 车道各出一页判定后总筹合。

## 七、复核命令

```bash
cd /d/ZephyrAlpha; export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version   # 3.12.8
S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md

# 轴1 TDM（预期 182 / 128 18 19 13 4 / 5 9 29 25 15 44 / 38）
grep -c "^- node_id:" config/trading_decision_map.yaml
for p in TDM-E- TDM-P- TDM-X- TDM-F- TDM-C-; do echo "$p $(grep -c "^- node_id: $p" config/trading_decision_map.yaml)"; done
grep -o "^- node_id: TDM-E-L[0-9]" config/trading_decision_map.yaml | sort | uniq -c
grep -c "module_ref: null" config/trading_decision_map.yaml; grep -c "module_ref:" config/trading_decision_map.yaml
grep -n "^[a-z_]*:" config/trading_decision_map.yaml | head

# 轴2 ROOR（预期 77 / summary 76 @:881 / 55 条未匹配）
grep -c "registry_id:" docs/registry_of_registries.yaml; grep -n "total_registries" docs/registry_of_registries.yaml
for r in $(grep -o "registry_id: REG-[A-Za-z0-9_-]*" docs/registry_of_registries.yaml | sed 's/registry_id: //'); do \
  f=$(grep -m1 -A4 "registry_id: $r" docs/registry_of_registries.yaml | grep -m1 -o "physical_path:.*" | sed 's/physical_path: *//;s/.*\///;s/\.yaml//'); \
  grep -q "$r" $S || { [ -n "$f" ] && grep -qi "$f" $S; } || echo "$r|$f"; done

# 轴3 SOP（预期 11 目录 / 14 条目 / 48 md）
ls -d docs/01_policies_and_standards/sop/*/ | wc -l
ls docs/01_policies_and_standards/sop/; find docs/01_policies_and_standards/sop -name "*.md" | wc -l

# 轴4 代码侧（预期 57 域 / 44 卡 / 17 未匹配 / 393 二级 / 86 三级 / 3758 py）
find src/zephyr -maxdepth 1 -type d | grep -v __pycache__ | tail -n +2 | wc -l
ls data/capability_cards/ | wc -l
for d in $(find src/zephyr -maxdepth 1 -type d | grep -v __pycache__ | tail -n +2 | xargs -n1 basename); do grep -qw "$d" $S || echo "$d"; done
find src/zephyr -mindepth 2 -maxdepth 2 -type d | grep -v __pycache__ | wc -l
find src/zephyr -mindepth 3 -maxdepth 3 -type d | grep -v __pycache__ | wc -l
find src/zephyr -name '*.py' | grep -v __pycache__ | wc -l

# F 编号无空洞（预期 122 行；2 位去重 99；3 位 23）
grep -c "^| F[0-9]" $S
grep -o "^| F[0-9]\{2\} " $S | sort -u | wc -l
grep -o "^| F[0-9]\{3\} " $S | sort -u | wc -l

# §三·H 三级枚举（预期：data 70/10、backtest 2/9、rule_enforcement 34/5、ai_layer 1/9、trading 56/10、frontend 10/9）
for p in src/zephyr/data src/zephyr/backtest src/zephyr/gov_enforcement/rule_enforcement src/zephyr/ai_layer src/zephyr/trading src/zephyr/frontend; do \
  echo "$p top_py=$(find $p -maxdepth 1 -name '*.py' | wc -l) dirs=$(find $p -maxdepth 1 -mindepth 1 -type d | grep -vc __pycache__) all_py=$(find $p -name '*.py' | grep -vc __pycache__)"; done

# §三·G M0 75/76 与扩展项锚点
grep -n "75/76\|X1" docs/_working/fullflow_mining/00_skeleton_fullflow.md | head
grep -rn "补挖\|扩展项" docs/_working/fullflow_mining/00_orchestration.md docs/_working/fullflow_mining/00_skeleton_fullflow.md   # 仅 4 命中（:35/:40/:41/:170）

# §三·F 双编号真源
grep -n "^title:" docs/_working/decision_map_campaign_20260924/links/*/SKEL.md
grep -n "四套并存的骨架切分\|138 节点" docs/_working/decision_map_campaign_20260924/09_link_skeletons.md
for f in docs/_working/decision_map_campaign_20260924/links/*/SKEL.md; do echo "$(basename $(dirname $f)) rows=$(grep -cE '^\| ?(L[0-9]{2}-C[0-9]+|EXE-[0-9]+|RSK-[0-9]+|B[0-9]+|S[0-9]+|C[0-9]+) ' $f)"; done

# §五 现有册基数（预期 115）
find docs/_working/fullflow_mining -name "*.md" | wc -l
```
