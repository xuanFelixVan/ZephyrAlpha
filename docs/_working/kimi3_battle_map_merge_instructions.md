---
ttl: task_bound
target_executor: Kimi3
task: 将 docs/_working/架构图/ 下 11 个草稿整合入作战地图全景图
estimated_duration: 8 hours
date: 2026-08-04
author: Owner
---

# Kimi3 执行指令：将 11 个架构草稿整合入作战地图全景图

> **致 Kimi3**：这是一份你需要独立执行 8 小时的完整指令文档。请严格按本文档执行，不要跳过任何铁律与前置检查。本文档自包含——你只需读这一份即可开工。**用户已睡觉，无法实时答疑，遇到歧义按"最保守、最符合铁律"的方式处理并记录在执行日志中。**

---

## 0. 一句话任务目标

将 `d:\ZephyrAlpha\docs\_working\架构图\` 下 11 个架构草稿的**交易作战相关内容**，通过真源（DB + YAML）整合进作战地图全景图（`battle_map_panorama.md` 及 12 个分阶段文档），使作战地图更全面、更细致地覆盖草稿中的所有作战细节。**最终交付：草稿中所有允许挂载的作战内容已进入作战地图真源并经生成器渲染到文档，被禁止挂载的内容有明确去向说明。**

---

## 1. 强制铁律（违反任一条 = 任务失败）

### 铁律 1：禁止手编目标文档
`battle_map_panorama.md` 和 `battle_map_01..12_*.md` 这 13 个文件**都是 `generate_battle_map_diagram.py` 的自动生成产物**，文件头部明确写"禁止手编（改环节→改 DB/YAML 真源→重跑生成器）"。
- **禁止**：直接编辑这 13 个 md 文件的正文/Mermaid 代码块
- **正确**：改 DB 表 + YAML 真源 → 运行生成器 → 文档自动更新

### 铁律 2：SSoT 真源分类（写数据前必查）
两类数据写不同地方，禁止混淆：
| 数据类型 | 真源位置 | 写入工具 |
|---|---|---|
| **架构数据**（环节/锚点/边/模块依赖） | PostgreSQL `battle_map_*` / `nodes` 等表 | `apply_depgraph.py` / `apply_battle_map.py` |
| **叙事数据**（环节中文描述、6件套结构化数据） | `module_translation_registry.yaml` §battle_map_steps 段 | 直接编辑该 YAML |
| **规则数据**（域白名单） | `battle_map_domain_policy.yaml` | 直接编辑该 YAML（本任务一般不改） |

### 铁律 3：依赖关系先行（L1，防幻觉治本规则）
任何新作战环节若锚定新模块，**必须先**用 `apply_depgraph.py --add-design-node` 在 depgraph 登记该模块（build_status=planned），**然后才能**用 `apply_battle_map.py` 建环节+锚点。禁止"先建环节后补模块"或"临时编造依赖"。

### 铁律 4：四图对齐（治本规则）
建完 depgraph 设计态节点后，`sync_panorama_module.py` 会自动派生其余 3 图；之后必须跑 `align_panoramas.py` + `align_battle_map.py` 验证 4 类对齐问题（孤儿/状态漂移/域不一致/设计态孤立）干净。**对齐不干净就停下来修，不要带病推进。**

### 铁律 5：域白名单硬约束（BM-INV-004）
作战地图每个 flow_stage 只允许挂载特定 domain 的模块（白名单见 §5）。**禁止挂载白名单外的域**（当前是 warn 不阻断，但会造成语义污染，必须自觉遵守）。
- **被禁止的 5 类内容绝不进作战地图**：治理架构、安全架构主体、运维架构主体、Agent 架构主体、合规架构主体。这些留在各自架构图域，作战地图只在被某环节真正调用时挂锚点指向。

### 铁律 6：防幽灵锚点（BM-INV-002）
锚点的 `target_id` 必须能在 `target_graph`（depgraph 或 candidate）找到。**禁止**锚定"草稿提到但 depgraph 未登记"的模块——要么先登记模块，要么不挂锚点。

### 铁律 7：备份先行
- `apply_depgraph.py` / `apply_battle_map.py` 内置 `backup_pg_architecture()` 自动 PG 备份，会自动执行
- 你若写 oneoff 脚本批量处理，**运行前先 git commit 当前代码**（君子协定，防回滚丢失）

### 铁律 8：禁止后台 Agent 幻觉
禁止使用 `run_in_background: true` 的 Agent 工具伪装并行。所有工作串行，用 TodoWrite 追踪进度，透明记录当前步骤。

### 铁律 9：双向对齐（用户强调，写入即验证）
作战地图与全景图/候选池的锚点关系**必须双向可查**。每写入一个锚点（battle_map_anchors 一行），必须同时满足两个方向：
- **方向A（step→modules）**：从作战环节能查到它挂载的所有模块/候选——`SELECT target_graph,target_id FROM battle_map_anchors WHERE step_id=?`
- **方向B（module→step）**：从全景图/候选池的任一模块能反查到它在作战地图的环节——`SELECT step_id FROM battle_map_anchors WHERE target_graph=? AND target_id=?`
- **写入校验**：每写完一批锚点，跑两条反查 SQL 确认双向都有结果。若某模块在 depgraph 存在但无作战环节挂载（方向B查不到），且该模块属于作战相关域，说明该挂没挂，补挂；若某作战环节挂了锚点但 target_id 在 depgraph/candidate 查不到（方向A查不到），是幽灵锚点，违反铁律6，删除或补登记模块。
- `align_battle_map.py` 会自动验证双向，但**写入时即时自检**比事后批量验证更可靠。

### 铁律 9.5：禁止在全景图表/候选池/翻译真源反向加 battle_map 字段（重要设计决策）
**绝对禁止**在以下位置添加 `battle_map_step_ids` / `battle_map_step_id` / `panorama_step_ids` 等反向字段：
- depgraph.nodes / nodes_metadata（依赖全景图）
- dataflow_jobs / dataflow_datasets / dataflow_edges（数据流全景图）
- decision_nodes / decision_layers / decision_edges（决策流全景图）
- blueprint_links（蓝图）
- candidate_module_registry.yaml（候选池）
- module_translation_registry.yaml（翻译真源）

**理由**（项目设计者主动决定，BM-INV-005 已明确）：
1. `battle_map_anchors` 表就是**双向查找的唯一真源**（表注释："方向A(step→modules)和方向B(module→step)都从此表查询"），它已经满足全部双向查询需求
2. 在各全景图表反向加字段 = 多真源，改一处要同步 6 处，必然漂移，违反 SSoT 铁律
3. 设计者**考虑过且主动放弃**在 depgraph.nodes 加 battle_map_step_ids 派生缓存字段（方案B 降级，详见 battlemap_schema.py L247-253 + battle_map_positioning.md §8.4）

**双向查询的正确做法**：永远只用 `battle_map_anchors` 一张表反查，不要给其他表加字段。若需"某模块在作战地图哪个环节"，跑：
```sql
SELECT step_id, target_role FROM battle_map_anchors
WHERE target_graph='depgraph' AND target_id='<模块path>'
```

**生成器已显化 anchors 枢纽（2026-08-04 已改生成器代码，无需你再处理）**：
- panorama.md 顶部说明已加"🔑 双向对齐枢纽"行，基本信息表已加"锚点总数（双向对齐枢纽）"行
- 12 个分阶段文档顶部说明已加"🔑 锚点表是双向对齐枢纽"行，基本信息表已加"锚点数（双向对齐）"行
- 你重跑 `generate_battle_map_diagram.py` 时自动继承显化，**不要手编 md 去加这些说明**（md 是生成器产物，手编会被覆盖）

---

## 2. 关键事实速查表（开工前必读）

### 2.1 真源三件套位置
| 真源 | 路径 / 表 |
|---|---|
| 作战地图 DB 表 | `battle_map_steps`(285环节) / `battle_map_anchors`(381锚点) / `battle_map_edges`(119边) |
| depgraph DB 表 | `nodes`(6188节点) / `edges` / `nodes_metadata` 等 |
| 叙事 YAML | `docs/01_policies_and_standards/_registry/translations/module_translation_registry.yaml` §battle_map_steps 段 |
| 域白名单 YAML | `docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml` |
| 生成器脚本 | `scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py` |
| 写入脚本 | `scripts/governance/apply_battle_map.py` / `scripts/governance/apply_depgraph.py` |
| 对齐脚本 | `scripts/governance/d5_architecture/generators/align_panoramas.py` / `scripts/governance/align_battle_map.py` |
| 同步脚本 | `scripts/governance/sync_panorama_module.py` |
| 目标生成文档目录 | `docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/` |
| 草稿目录 | `docs/_working/架构图/` |

### 2.2 数据库连接
配置文件：`config/.env.postgres`
```
POSTGRES_HOST=localhost  POSTGRES_PORT=5432  POSTGRES_DB=depgraph
POSTGRES_USER=zephyr  POSTGRES_PASSWORD=zephyr_dev_2026
POSTGRES_READER_USER=depgraph_reader  POSTGRES_READER_PASSWORD=reader_dev_2026
POSTGRES_WRITER_USER=depgraph_writer  POSTGRES_WRITER_PASSWORD=writer_dev_2026
```
连接方式参考各 schema 模块的 `get_depgraph_pg_connection()` / `get_battle_map_pg_connection()`。

### 2.3 现状数字（合并前基线）
| 指标 | 数值 |
|---|---|
| battle_map_steps 总环节 | 285（depth=0: 96, depth=1: 159, depth=2: 26, depth=3: 4）|
| battle_map_anchors 总锚点 | 381（depgraph: 287, candidate: 94）|
| battle_map_edges 总边 | 119（data_flow: 92, trigger: 25, degradation: 2）|
| design_maturity | production: 163, design: 122 |
| depgraph nodes 总节点 | 6188（module: 2863, test: 2384, script: 663, config: 197, blueprint: 71...）|
| build_status | generated: 4208, stable: 1796, planned: 101, deprecated: 83 |

### 2.4 step_id 命名约定（必须遵守）
格式：`BM-<阶段缩写>-<序号>[-<子层标记>][-<孙层标记>][-<曾孙标记>]`
- 阶段缩写：RES(研究孵化) / MT(模型训练) / BT(回测验证) / SIM(仿真验证) / SEL(选股) / BUY(买入) / SELL(卖出) / POS(仓位) / RC(风控管控) / EXE(执行) / REC(对账)
- 例：`BM-BUY-02-A-1-a` = 买入阶段第2环节的A子环节的第1孙环节的a曾孙环节
- 现有各阶段顶层环节序号已用到：BT-01~07 / BUY-01~07 / EXE-01~06 / MT-01~05 / POS-01~12(跳号) / REC-01~05 / RES-01~07 / RC-01~08 / SELL-01~09(跳号) / SIM-01~07 / SEL-01~23(跳号)。**新增环节续号，先查 max(序号)+1**

### 2.5 11 个草稿体量
| 草稿文件 | 行数 | KB | H2 | H3 | H4 | H5 | 处理策略 |
|---|---|---|---|---|---|---|---|
| 00-架构图总览与索引.md | 394 | 32.5 | 6 | 12 | 13 | 0 | 仅作索引参考，§2边界定义/§5交叉引用要参考，不挂载 |
| 交易决策架构.md | 10806 | 1466 | 31 | 271 | 376 | 19 | **主体挂载，工作量最大** |
| Agent架构.md | 2051 | 224 | 21 | 84 | 43 | 0 | 仅 D_ORCHESTRATOR 部分挂 buy_flow，其余不挂 |
| 学习系统架构.md | 2479 | 291 | 16 | 60 | 13 | 0 | 主体挂载（research/model_training/stock_selection）|
| 数据架构.md | 3630 | 367 | 18 | 202 | 27 | 0 | 主体挂载（多阶段）|
| 合规架构.md | 1466 | 155 | 15 | 64 | 44 | 0 | 仅买入合规闸部分挂，其余不挂 |
| 安全架构.md | 2161 | 203 | 15 | 53 | 23 | 0 | 仅 D_SECURITY 在 risk_control 挂（MOD-INF-018安全基线），主体不挂 |
| 运维架构.md | 1653 | 159 | 14 | 64 | 54 | 1 | 仅 D_OPS 在 reconciliation 挂，主体不挂 |
| 治理架构.md | 1360 | 195 | 18 | 39 | 16 | 0 | **完全不挂** |
| 集成架构.md | 1800 | 186 | 28 | 94 | 55 | 0 | 仅 D_INTEGRATION 在选股/买入挂，基础设施部分不挂 |
| 风险架构.md | 1661 | 193 | 17 | 50 | 18 | 0 | 主体挂载（risk_control/execution/buy_flow）|

**草稿 H3 合计约 893 个**——不是全部都变环节，需按 §4 决策树过滤。

---

## 3. 粒度规则：双轨制（你已确认的策略）

作战地图的"细"和草稿的"细"模型不同：
- **草稿**：H1→H5 的文字叙事层级（5层）
- **作战地图**：step_id 树 + indicators JSONB（环节嵌套树 + 结构化数据）

### 双轨制规则
| 轨道 | 承载内容 | 写入位置 | 上图？ |
|---|---|---|---|
| **环节嵌套轨** | 有触发/消费/数据流的"作战动作" | `battle_map_steps` 新行（depth 0-3） | 上 Mermaid 图 |
| **indicators 轨** | 参数/契约/时序/数值/边界规则/配置 | 现有或新环节的 `indicators` JSONB 字段（6件套：trigger/consumes/params/data_flow/code_mapping/degradation）| 不上图，结构化可查 |
| **叙事轨** | 环节中文描述 | `module_translation_registry.yaml` §battle_map_steps | 图上显示简版 |

### depth 嵌套上限（已用 H5 实际内容验证，结论确定）
- **最大 depth=3（曾孙）**：技术上 DB 无硬 CHECK 约束（实测 0 个 depth 约束），但 BM-INV-006 设计最大 2，会触发 `align_battle_map.py` 的 depth 超限告警（warn 不阻断）。**允许用到曾孙（depth=3），step_id 命名到 5 段（如 `BM-BUY-02-A-1-a`）为止**。
- **曾曾孙（depth≥4）禁止**：会破坏 BM-INV-006，Mermaid subgraph 嵌套 5 层后渲染近乎不可读，step_id 到 6 段人眼无法辨识。
- **草稿 H5 实际内容验证结论**（2026-08-04 实测交易决策19个H5+运维1个H5）：
  - 红白对抗四层架构(7个) → 安全域，**禁止挂**（铁律5）
  - AI原生开发范式约束6.1-6.5(5个) → 治理性约束，归 indicators 或留治理域
  - 硬件性能预算/资金约束/外部接口约束(3个) → 参数表，**归 indicators JSONB**
  - 日历因果说明/变更管理补充(2个) → 说明性内容，**归 indicators**
  - 实验可复现性子能力/模型风险管理子能力(2个) → 现有C-003/C-029子能力，做 **depth=3 曾孙**
  - **0 个需要 depth=4**。草稿 H5 内容本质是参数/说明/被禁域，做成 depth=4 环节是模型错配。
- **草稿 H4/H5 级细节处理**：不下沉到 depth=4，而是转入 indicators JSONB（params/data_flow 字段）或叙事 YAML 的详细描述。这样既保留信息又控制嵌套深度。

### 环节总量控制
- 目标：作战环节总数从 285 增长到 **不超过 450**（Mermaid 节点数超 300 后静态 md 渲染开始失真，这也是为什么有可缩放 HTML 版）。
- 若草稿过滤后可挂环节超过 165 个增量，优先挂"生产态/高价值"环节，其余以 indicators 形式附在父环节。

---

## 4. "已有 vs 新增"决策树（每个草稿 H3 都过一遍）

```
草稿某 H3 标题内容 X（如"撮合引擎""T+1约束"）
│
├─ ① 是作战动作吗？（有触发/消费/数据流，是流程一环）
│   ├─ 否 → 是参数/契约/时序/术语/方法论引用？
│   │        ├─ 是 → 归 indicators JSONB 或叙事 YAML，不建 step
│   │        └─ 否（是纯引用/术语表/成功指标）→ 不进作战地图，记录到执行日志"已排除"
│   └─ 是 → ② 查 depgraph.nodes 有无等价已登记模块？（用功能关键词 + path 广搜）
│            ├─ 有 → 这是"模块级重复"。X 作为锚点挂到现有环节，不新建 step
│            └─ 无 → ③ 查 battle_map_steps 有无等价环节？（用 step_name 关键词搜）
│                     ├─ 有 → 对比 X 与现有环节的 indicators/叙事：
│                     │        • X 更细更优 → 更新现有环节 indicators + 叙事 YAML（真源）
│                     │        • 现有更优 → 丢弃 X 或仅补 X 独有细节到 indicators
│                     │        • 两者可拼 → 合并到现有环节（不要建两个同名环节）
│                     └─ 无 → ④ X 锚定的模块域在白名单内？（查 §5）
│                              ├─ 是 → 新建 step（design_maturity=design 先登记）
│                              │        先 apply_depgraph 登记模块(planned) → apply_battle_map 建 step+anchor
│                              └─ 否 → 不挂，记录到执行日志"域禁止"
```

### 冲突处理原则
草稿是 v9.0（交易决策）/v3.0（总览），版本可能比作战地图现有认知更新，**但不能默认草稿赢**：
- 判断"该不该有"→ 查域文档（设计意图真源，禁用 depgraph）
- 判断"现在是不是这样"→ 查 depgraph 已 stable 模块（事实真源）
- 草稿若与已 stable 代码实现冲突：要么草稿过时（改草稿留档）、要么代码待重构（走 depgraph 改造流程，**不是直接覆盖**）
- 优先级：已 stable 代码实现 > 草稿设计。草稿 design 内容登记为 design_maturity=design，不覆盖 production。

---

## 5. 域白名单完整清单（BM-INV-004，写锚点前必查）

以下每个 flow_stage 只允许挂列出的 domain 的模块。完整真源在 `battle_map_domain_policy.yaml`。

### 5.1 各阶段允许的 domain
| flow_stage | 允许的 domain | 对应草稿 |
|---|---|---|
| research_incubation | D_RESEARCH, D_DATA, D_ML_TRAIN, D_KNOWLEDGE, D_INTELLIGENCE, D_DATA_ENG, D_DATA_GOV, D_DATA_SEC | 学习系统/数据架构(部分) |
| model_training | D_ML_TRAIN, D_FACTOR, D_DATA, D_RESEARCH | 学习系统/数据架构(部分) |
| backtest_validation | D_BACKTEST, D_DATA, D_FACTOR, D_SIMULATION, D_RISK, D_POSITION, D_EXEC_SIM | 交易决策§回测/风险架构 |
| simulation_validation | D_SIMULATION, D_BACKTEST, D_RISK, D_DIGITAL_TWIN | 交易决策§仿真 |
| stock_selection | D_FACTOR, D_ASHARE_SIGNAL, D_FUNDAMENTAL_SIGNAL, D_SIGNAL, D_INTELLIGENCE, D_KNOWLEDGE, D_INTEGRATION, D_MKT_DATA, D_DATA, D_ML_SERVE, D_ML_TRAIN, D_ALT_DATA, D_CROSS_ASSET, D_INFRA_RUNTIME, D_SHARED, D_SIGQC | 交易决策§选股/数据架构/学习系统 |
| buy_flow | D_PF_CORE, D_PF_ALLOC, D_TRADING, D_RISK, D_INTEGRATION, D_ORCHESTRATOR, D_INTELLIGENCE, D_COMPLIANCE, D_ASHARE_SIGNAL | 交易决策§买入/风险架构/集成/Agent(编排器)/合规(闸) |
| sell_flow | D_SELL_DECISION, D_TRADING, D_RISK, D_POSITION | 交易决策§卖出/风险架构 |
| position_management | D_POSITION, D_PF_CORE, D_PF_ALLOC, D_RISK | 交易决策§仓位/风险架构 |
| risk_control | D_RISK, D_REPORTING, D_POSITION, D_TRADING, D_SECURITY | 风险架构/安全架构(仅MOD-INF-018) |
| execution | D_EX_CORE, D_EX_SOR, D_TRADING, D_RISK, D_REPORTING | 交易决策§执行/风险架构 |
| reconciliation | D_REPORTING, D_BACKTEST, D_SIMULATION, D_TRADING, D_FACTOR, D_FEEDBACK_LOOP, D_FBL_DETECTORS, D_FBL_DIAGNOSERS, D_FBL_VERIFICATION, D_OPS | 交易决策§对账/运维架构(仅D_OPS) |

### 5.2 11 草稿逐个挂载判定（用户已确认策略）
| 草稿 | 主要域 | 处理策略 | 进作战地图？ |
|---|---|---|---|
| 00-总览与索引 | 元文档 | 仅参考§2边界定义/§5交叉引用，不挂载 | ❌ 不挂 |
| 交易决策架构 | D_FACTOR/D_SIGNAL/D_PF_*/D_RISK/D_TRADING/D_BACKTEST 等 | 主体挂载，11 阶段全覆盖（工作量最大） | ✅ 主体 |
| 风险架构 | D_RISK | 主体挂载 risk_control/execution/buy_flow | ✅ 主体 |
| 数据架构 | D_DATA/D_MKT_DATA/D_DATA_ENG/D_ALT_DATA | 多阶段挂载（选股/研究/训练/回测/对账都有 D_DATA） | ✅ 主体 |
| 学习系统架构 | D_ML_TRAIN/D_ML_SERVE/D_INTELLIGENCE | 挂 research_incubation/model_training/stock_selection | ✅ 主体 |
| 集成架构 | D_INTEGRATION + D_INFRA_* | **仅 D_INTEGRATION 在选股/买入挂**；D_INFRA_A2A/A2A/OPS/RECOVERY/TELEMETRY 基础设施不挂 | ⚠️ 部分 |
| 合规架构 | D_COMPLIANCE | **仅买入合规闸部分（BM-BUY-08 A股交易纪律四项严禁）挂 buy_flow**；合规审计/报送/留痕主体不挂 | ⚠️ 部分 |
| 安全架构 | D_SECURITY/D_SECURITY_LLM | **仅 D_SECURITY 在 risk_control 挂（MOD-INF-018 安全基线）**；安全架构主体不挂 | ⚠️ 部分 |
| 运维架构 | D_INFRA_OPS/D_OPS | **仅 D_OPS 在 reconciliation 挂（反馈循环运营）**；D_INFRA_OPS 主体不挂 | ⚠️ 部分 |
| 治理架构 | D_GOV_*/D_GOVERNANCE | **完全不挂**（治理是元层面，不属于交易作战流程） | ❌ 不挂 |
| Agent架构 | D_ORCHESTRATOR/D_AUTONOMY_* | **仅 D_ORCHESTRATOR 在 buy_flow 挂**；D_AUTONOMY_CORE/PERM 不挂 | ⚠️ 部分 |

### 5.3 不挂载内容的去向
被禁止挂载的 5 类内容（治理/安全主体/运维主体/Agent 主体/合规主体）**不是丢弃**，而是：
- 保留在各自架构图域（`docs/02_enterprise_architecture/` 其他位置）
- 在作战地图执行日志中记录"草稿X的§Y内容因域政策不挂载，留原架构图"
- 若某作战环节确实调用到这些域的某个模块（如买入环节调用合规闸模块），则在**该环节挂锚点**指向 depgraph 已登记的该模块，模块本身不进作战地图

---

## 6. 写入真源的完整流程（不可手编 md！）

### 6.1 单个新作战环节的标准写入流程
```
1. (若锚定新模块) apply_depgraph.py --add-design-node
   → 登记 depgraph.nodes 一行 (build_status=planned, design_maturity=design)
   → 该模块 path/domain 必须真实存在

2. sync_panorama_module.py 自动派生其余3图（或手动 --all）

3. apply_battle_map.py 新增 battle_map_steps 一行
   → step_id 按 §2.4 命名约定续号
   → flow_stage 查 §5 白名单确认该模块域允许
   → design_maturity=design（先登记，验证后转 production）
   → parent_step_id 填父环节（嵌套时）
   → depth 按父+1（最大3）

4. apply_battle_map.py 新增 battle_map_anchors 一行
   → step_id = 上面的新环节
   → target_graph = depgraph（或 candidate）
   → target_id = 步骤1登记的模块 path 或 blueprint_id（禁止用 node_id！）

5. (若需要) apply_battle_map.py 新增 battle_map_edges
   → from_step_id/to_step_id 填环节流转
   → edge_type: data_flow/trigger/degradation

6. 叙事写入 module_translation_registry.yaml §battle_map_steps 段
   → 环节中文描述（草稿里的描述句）
   → 6件套结构化数据（trigger/consumes/params/data_flow/code_mapping/degradation）
   → BM-INV-003: 禁止生成器硬编码叙事

7. align_panoramas.py + align_battle_map.py 验证对齐干净
   → 有孤儿/漂移/域不一致 → 修，不要带病推进

8. (批次完成后) generate_battle_map_diagram.py 重新生成 13 个文档
   → 全景图 panorama.md + 12 个分阶段文档
   → 这一步会自动渲染 Mermaid 图、更新统计数字
```

### 6.2 node_id 禁用规则
- `node_id` 是 depgraph DB 自增主键，每次 regenerate 会重分配，**非稳定标识符**
- **跨表/跨文件引用禁止用 node_id**，必须用 `path` 或 `blueprint_id` 作为稳定标识符
- battle_map_anchors.target_id 用 path/blueprint_id，**禁止填数字 node_id**

### 6.3 备份机制
- `apply_depgraph.py` / `apply_battle_map.py` 内置 `backup_pg_architecture()` 自动 PG 备份（pg_dump + 事务回滚）
- 你若写 oneoff 批量脚本：运行前 `git commit` 当前代码（君子协定）

---

## 7. 草稿间重叠预处理（合并前必做）

草稿之间本身就有重叠，**合并前先解决草稿间重叠，否则作战地图会重复挂载**：
- 交易决策架构 §9 风控 ↔ 风险架构（同一批风控内容两处都有）
- 数据架构 ↔ 交易决策架构 §2 L0 数据层 ↔ 学习系统架构 §数据
- 合规架构 ↔ 交易决策架构 §买入合规闸
- 安全架构 ↔ 运维架构 ↔ 治理架构（三者都谈安全基线/审计）

**处理原则**：重叠内容只挂一次，以**最权威的草稿**为准（通常是对应域的专门架构图 > 交易决策架构的总览描述）。在执行日志中记录重叠处理决策。

---

## 8. 执行流程：循环审查机制（核心要求，用户强调）

> **重要**：这不是"跑一遍就完"的任务。AI 第一遍执行会漏掉大量功能，**必须循环执行"整合→检查→再整合"直到检查不出能加入的新功能（功能数=0）才算结束**。用户已睡觉，要求自动循环。

### 8.0 循环总体结构
```
第1轮完整执行（步骤1-8）→ 第9步检查 → 若发现遗漏 → 第2轮（步骤2-8）→ 第9步检查 → ...
    ↓                                                                     ↓
 git commit                                                            git commit
    └──────────────────────── 循环直到第9步检查结果=0个新功能 ────────────┘
                                    ↓
                            任务结束（最终验收）
```

### 8.1 循环终止条件（硬性，必须满足）
**只有当以下三个条件全部满足，任务才算结束**：
1. **新功能数=0**：第9步检查发现 11 个草稿里再无"应挂未挂"的作战功能（每个 H3 都已判定为：已挂/已排/已归indicators）
2. **双向对齐全净**：铁律9 的方向A+方向B 反查全部有结果，无幽灵锚点、无应挂未挂模块
3. **对齐脚本干净**：`align_panoramas.py` + `align_battle_map.py` 除 depth=3 告警外无其他违例

**只要还有"检查出能加入的功能"，就必须再循环一轮**，不允许以"差不多了"为由提前结束。

---

### 第 1 步：环境准备与基线确认（30 分钟，仅第1轮做）
- [ ] 读本文档全文，理解所有铁律（特别是铁律9双向对齐 + 循环机制）
- [ ] **读项目三件套（项目宪法，必读，否则会违反铁律）**：
  - `AGENTS.md`（根目录，307KB）— 项目全部铁律汇总：SSoT 真源分类、四图对齐、依赖关系先行、备份先行、文件命名规则、worktree 门禁、node_id 使用限制等核心规则的**权威真源**。本文档的铁律只是摘要，详情以 AGENTS.md 为准。
  - `.trae/rules/onboarding_detail.md`（83KB）— 详细新人指引：项目结构、工具链、开发流程、各模块职责、API 用法。执行 `apply_depgraph.py` / `apply_battle_map.py` 前必读其用法。
  - `.trae/rules/project_rules.md`（36KB）— 项目规则汇总：工程规范、commit 策略、测试要求、代码风格。
- [ ] 读 `battle_map_positioning.md`（作战地图定位文档）了解设计哲学
- [ ] 读 `battle_map_domain_policy.yaml` 全文
- [ ] 读 `module_translation_registry.yaml` §battle_map_steps 段（了解叙事格式）
- [ ] 跑 `init_battle_map_db(echo=True)` 确认 DB 连通、3 表存在
- [ ] 跑 `align_battle_map.py` 记录合并前对齐基线（应为干净，若不干净先记录现有问题）
- [ ] git commit 当前代码状态（备份先行）

### 第 2 步：建"草稿→域→阶段→能否挂"映射表（1.5 小时，第2轮起增量更新）
**这是你负责的核心分类工作**。为 11 个草稿的每个 H3 标题填一行：
| 草稿 | H3标题 | H4数 | 所属域(推断) | 是作战动作? | 对应flow_stage | 域在白名单? | 已有等价环节/模块? | 处理动作(新建step/挂锚点/归indicators/排除) |

- 用脚本扫描 11 个草稿的 H3 列表（PowerShell `Select-String '^### '`）
- 逐个 H3 判定：所属域（看内容/路径）、是否作战动作、对应阶段、白名单、是否已有等价
- 已有等价查询：`SELECT step_id,step_name FROM battle_map_steps WHERE step_name ILIKE '%关键词%'` + `SELECT path FROM nodes WHERE path ILIKE '%关键词%'`
- 输出映射表到 `docs/_working/battle_map_merge_mapping.md`（你的工作产物1）
- **过滤掉**：①域禁止的 ②非作战动作的（参数/契约/术语/引用）③草稿间重复的

### 第 3 步：草稿间重叠合并（45 分钟）
- 基于 §7 重叠清单 + 第 2 步映射表，标记重叠 H3
- 为每组重叠选定权威来源，其余标记"合并到X"
- 更新映射表

### 第 4 步：批量登记新模块到 depgraph（1 小时）
- 映射表中"处理动作=新建step 且锚定新模块"的行
- 按 §6.1 流程 1-2：`apply_depgraph.py --add-design-node` 逐个登记
- 每个模块 path/domain 必须真实（path 要对应实际代码文件或合理的 planned 路径）
- build_status=planned, design_maturity=design
- 跑 `sync_panorama_module.py --all` 派生 3 图
- 跑 `align_panoramas.py` 验证无孤儿

### 第 5 步：批量建作战环节 + 锚点 + 边（2 小时，工作量最大）
- 按 flow_stage 分批处理（建议顺序：research → model_training → backtest → simulation → stock_selection → buy → sell → position → risk_control → execution → reconciliation）
- 每个 flow_stage 内：先建顶层 step → 子 step → 孙 step（曾孙按需，多数转 indicators）
- 同步建 anchor（target_id 用 path/blueprint_id）+ edge
- 叙事写入 module_translation_registry.yaml
- 每 20-30 个环节跑一次 `align_battle_map.py` 检查，发现违例立即修
- indicators 6件套要填实（从草稿挖参数/数据流/降级逻辑）

### 第 6 步：indicators 补全（45 分钟）
- 草稿 H4/H5 级细节（参数/契约/时序/术语）下沉到对应环节的 indicators JSONB
- 不上图，但结构化可查
- 这是"细到细枝末节"的关键承载——环节图保持清晰，细节在 indicators

### 第 7 步：对齐验证 + 修复（45 分钟）
- `align_panoramas.py` 验证 4 类对齐：孤儿/状态漂移/域不一致/设计态孤立
- `align_battle_map.py` 验证：BM-INV-001(无锚点)/BM-INV-002(幽灵锚点)/BM-INV-006(depth超限)
- 所有告警逐个修，直到干净
- 若 depth=3 告警无法避免（曾孙环节），记录在执行日志说明已用双轨制曾孙策略

### 第 8 步：重跑生成器 + 本轮 git commit（每轮做）
- `generate_battle_map_diagram.py` 重新生成 13 个文档
- 本轮验收检查：
  - [ ] panorama.md 环节总数更新（应 ≤450）
  - [ ] 各分阶段文档环节数更新
  - [ ] Mermaid 图能渲染（检查代码块完整）
  - [ ] 可缩放 HTML 版重新生成（`_zoomable_html/`）
- **git commit 本轮成果**（每轮必须 commit，防回滚丢失）

---

### 第 9 步：循环检查——是否还有遗漏功能（每轮必做，决定是否继续循环）

> **这是循环机制的核心**。第8步完成后不能直接结束，必须跑这一步检查"还有没有遗漏"。

#### 9.1 遗漏检查（5 项全过才算无遗漏）

**检查 A：草稿 H3 覆盖率反查**
- 重新扫描 11 个草稿的所有 H3 标题
- 对每个 H3，在映射表里找它的"处理动作"
- 若某 H3 的处理动作是空/未判定/未执行 → **遗漏，标记为待补**
- 若某 H3 标记"新建step"但 battle_map_steps 里查不到对应 step_id → **遗漏**

**检查 B：作战相关域模块的作战环节覆盖反查（铁律9方向B）**
```sql
-- 找出 depgraph 里属于作战相关域、但作战地图没挂载的模块
SELECT n.path, n.node_name, n.domain_id
FROM nodes n
WHERE n.build_status IN ('stable','generated','planned')
  AND n.domain_id IN ('D_FACTOR','D_SIGNAL','D_ASHARE_SIGNAL','D_FUNDAMENTAL_SIGNAL',
    'D_INTELLIGENCE','D_KNOWLEDGE','D_INTEGRATION','D_MKT_DATA','D_DATA',
    'D_ML_SERVE','D_ML_TRAIN','D_ALT_DATA','D_CROSS_ASSET','D_SIGQC',
    'D_PF_CORE','D_PF_ALLOC','D_TRADING','D_RISK','D_ORCHESTRATOR','D_COMPLIANCE',
    'D_SELL_DECISION','D_POSITION','D_EX_CORE','D_EX_SOR','D_REPORTING',
    'D_BACKTEST','D_SIMULATION','D_DIGITAL_TWIN','D_RESEARCH','D_DATA_ENG',
    'D_DATA_GOV','D_DATA_SEC','D_FEEDBACK_LOOP','D_FBL_DETECTORS',
    'D_FBL_DIAGNOSERS','D_FBL_VERIFICATION','D_OPS','D_INFRA_RUNTIME','D_SHARED')
  AND NOT EXISTS (
    SELECT 1 FROM battle_map_anchors a
    WHERE a.target_graph='depgraph' AND a.target_id=n.path
  )
ORDER BY n.domain_id, n.path
```
- 逐个审查返回结果：该模块是不是"应挂未挂"？
  - 若是作战相关且该模块对应草稿里有描述 → **遗漏，补挂锚点**
  - 若是非作战动作的支撑模块（如工具类/配置类）→ 记录"已审查，非作战动作，不挂"
- 这个查询是发现遗漏的最强工具——很多第一轮漏挂的模块会在这里暴露

**检查 C：作战环节 6件套空值反查**
```sql
-- 找出 indicators 空着没填的环节（草稿里明明有细节却没下沉）
SELECT step_id, step_name, indicators
FROM battle_map_steps
WHERE (indicators IS NULL OR indicators::text = 'null'
   OR (indicators->>'trigger') IS NULL
   OR (indicators->>'data_flow') IS NULL)
  AND design_maturity='design'
```
- 对每个空 indicators 的环节，回草稿找对应内容是否有可填的参数/数据流
- 有 → **遗漏，补填 indicators**

**检查 D：草稿 H4/H5 细节覆盖反查**
- 抽查草稿里 H4/H5 的具体内容（参数表、时序、公式、边界值）
- 在对应作战环节的 indicators JSONB 里找这些细节
- 若草稿有但 indicators 没有 → **遗漏，补填**

**检查 E：双向对齐全净（铁律9）**
- 跑检查B的查询，确认方向B无"应挂未挂"
- 跑 `SELECT step_id FROM battle_map_anchors a WHERE NOT EXISTS (SELECT 1 FROM nodes n WHERE n.path=a.target_id) AND a.target_graph='depgraph'` 确认方向A无幽灵锚点

#### 9.2 循环决策
- 若 9.1 的 A/B/C/D/E **任一项发现遗漏** → 记录遗漏清单到执行日志，**回到第2步开始下一轮**（第2步增量更新映射表，重点处理遗漏项）
- 若 9.1 五项**全部通过（0个遗漏）** → 满足循环终止条件1，进入最终验收

#### 9.3 循环上限
- 最多循环 **5 轮**。若 5 轮后仍有遗漏，停下来，把遗漏清单写入执行日志"待人工复核"段，任务结束（防无限循环耗尽8小时）。
- 每轮耗时控制：第1轮最长(4-5小时)，后续轮递减(每轮1-1.5小时，因增量越来越小)。

---

### 第 10 步：最终验收（循环终止后做，仅一次）
- [ ] §12 验收标准全部满足
- [ ] 执行日志 `docs/_working/battle_map_merge_execution_log.md` 完成（含每轮循环记录）
- [ ] 映射表 `docs/_working/battle_map_merge_mapping.md` 最终版（每个H3都有处理动作）
- [ ] git commit 最终结果（带"循环N轮完成，0遗漏"说明）

---

## 9. 你的两个工作产物（必交付）

### 产物 1：`docs/_working/battle_map_merge_mapping.md`
- 11 草稿所有 H3 的"草稿→域→阶段→能否挂"映射表
- 标注每个 H3 的处理动作和理由
- 标注草稿间重叠合并决策

### 产物 2：`docs/_working/battle_map_merge_execution_log.md`
- **每轮循环记录**（轮次/起止时间/本轮新增数/本轮遗漏数）
- 新增 step 数 / 新增 anchor 数 / 新增 edge 数 / 新增 depgraph 模块数（累计）
- 被排除的内容清单（域禁止/非作战动作/重复）及理由
- depth=3 告警说明（若有）
- 对齐验证结果（双向对齐检查A/B/C/D/E 每轮结果）
- 遗留问题/待人工复核项

---

## 10. 常见坑与禁止事项清单

### 绝对禁止
- ❌ 直接编辑 13 个生成器产出的 md 文件
- ❌ 用 node_id 做锚点 target_id 或跨表外键（用 path/blueprint_id）
- ❌ 先建环节后补模块依赖（违反依赖先行）
- ❌ 挂载白名单外域的模块（治理/安全主体/运维主体/Agent主体/合规主体）
- ❌ 用 `run_in_background` Agent 伪装并行
- ❌ 在草稿与已 stable 代码冲突时直接覆盖代码实现
- ❌ 在生成器代码里硬编码环节叙事（叙事走 YAML）
- ❌ 在全景图表/候选池/翻译真源反向加 battle_map_step_ids 等字段（违反铁律9.5，双向查询只用 battle_map_anchors）
- ❌ 文件名不遵守 snake_case（唯一豁免：docker-compose.yml/AGENTS.md/Dockerfile/README.md 等已知文件）

### 易错点
- ⚠️ step_id 序号要查 max+1 续号，不要凭记忆猜（SEL 已到 23，BUY 已到 07，跳号）
- ⚠️ 锚点 target_id 用 path 不用 node_id（node_id 易变）
- ⚠️ design_maturity=design 的环节不要标成 production（已 stable 才是 production）
- ⚠️ 草稿里的"引用"（如交易决策§19-§28 全是引用）是指针不是作战内容，不要挂
- ⚠️ stock_selection 已 83 环节最挤，新增要重点去重
- ⚠️ PowerShell 写多行 Python heredoc 会出转义问题，用脚本文件而非 `-c`
- ⚠️ 写 DB 前确认 PG 连接用 writer 账号（depgraph_writer），reader 只读

### 遇到歧义的处理（用户已睡觉）
按"最保守、最符合铁律"处理 + 记录到执行日志"待人工复核"段。不要自行扩大挂载范围或绕过铁律。

---

## 11. 应急与求助

- 若 `apply_depgraph.py` / `apply_battle_map.py` 报错：读错误信息，多数是 CHECK 约束（flow_stage/design_maturity 不在受控词表）或 FK（parent_step_id/anchor target 不存在）
- 若对齐脚本报大量孤儿：检查新建环节是否漏建锚点，或锚点 target_id 拼错
- 若生成器渲染失败：检查 Mermaid 语法（subgraph 嵌套、特殊字符转义）
- DB 操作失败有自动备份，可用 backup_pg_architecture 的回滚恢复
- **禁止**为绕过错误而修改铁律脚本（如禁用 CHECK、关掉对齐验证）

---

## 12. 验收标准（用户起床后检查）

1. ✅ 13 个作战地图文档已通过生成器重新生成（git diff 显示自动更新）
2. ✅ 作战环节总数 285 → 不超过 450
3. ✅ `align_battle_map.py` + `align_panoramas.py` 干净（depth=3 告警除外，有说明）
4. ✅ 映射表（产物1）覆盖 11 草稿所有 H3，每个有处理动作
5. ✅ 执行日志（产物2）完整记录**每轮循环**（轮次/新增/遗漏/决策）
6. ✅ 被排除的 5 类内容有明确去向说明
7. ✅ indicators 6件套填实（草稿细节不丢）
8. ✅ 无幽灵锚点（BM-INV-002，铁律6）
9. ✅ 新增模块在 depgraph 有对应 planned 节点（依赖先行，铁律3）
10. ✅ git commit 已提交最终结果
11. ✅ **循环已终止**：第9步检查 5 项全过（0遗漏），或达 5 轮上限并有"待人工复核"清单
12. ✅ **双向对齐验证**（铁律9）：方向A(step→modules)+方向B(module→step)反查全部有结果，无应挂未挂模块

---

**开始执行。记住：宁可慢、宁可保守，不要违反铁律、不要污染作战地图语义边界。作战地图的价值在于"一眼看清交易作战流程"，不是"什么都往里塞的杂物间"。**
