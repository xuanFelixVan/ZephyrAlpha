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

> **🔔 2026-08-05 增补（重要，必读）**：上一轮执行后用户验证发现大量遗漏（6 类 v8.2/v8.1/v7.0 特性在 13 个 battle_map MD 里 `count=0`）。根因：旧检查 A（只看 H3 标题）和检查 B（只看 depgraph 已登记模块）都查不到"草稿正文/升级注记/图框里点名了但还没登记成模块的特性"。本次增补六处：①§3.1 颗粒度达标定义（5 载体可检索） ②§8 第9步新增**检查F（术语级 grep）+ 检查G（源文档章节对齐）** ③§8.1 循环终止条件加"术语级覆盖全净" ④§11.5 已知 6 项遗漏清单 + 对照方法 ⑤**§5.4 自主新增 flow_stage 授权与流程**（用户明确授权，业务范围内可加新阶段，含横切机制归轨区分） ⑥§12 验收标准加"横切正确归轨"。**检查 F 是最强遗漏探测器，每轮必做，count=0 即遗漏。**

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
- **新增阶段缩写**：若草稿引入现有 11 阶段都装不下的新作战生命周期阶段，Kimi 有权按 §5.4 流程新增 flow_stage + 定义新缩写（2-3 字母），但必须同步改 4 处定义 + 通过对齐验证
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

### 3.1 颗粒度达标定义（2026-08-05 补充，治本"做了但有遗漏"）

> **上一轮执行的教训**：H3 都过了决策树、双向对齐也干净，但用户仍发现大量遗漏。根因：**"颗粒度"不止于 H3 标题**。草稿正文/图框/升级注记里的具名特性（模型名、方法名、机制名）若没在 battle_map 任何位置出现，就是遗漏，但旧检查 A（只看 H3）和检查 B（只看 depgraph 已登记模块）都查不到它们。

**"全部体现"的判定标准（二元，必须满足）**：
草稿里每一个**具名特性/模型/方法/机制/参数**，必须在以下 5 个载体之一里**可检索到**（grep 能命中）：
1. battle_map 某环节的 `step_name` 或 `step_id`（环节嵌套轨）
2. battle_map 某锚点 `target_id` 指向的 depgraph 模块（锚点轨）
3. 某环节的 `indicators` JSONB 内容（6件套，indicators 轨）
4. `module_translation_registry.yaml` §battle_map_steps 的叙事文本（叙事轨）
5. `module_translation_registry.yaml` §**battle_map_cross_cutting** 段（横切轨，贯穿多阶段的全局机制走此轨，详见 §5.4.3）

**且**：该内容必须经 `generate_battle_map_diagram.py` 渲染后，在 13 个 battle_map MD 文档之一里**有文字显示**（不只存在于 DB，要渲染出来肉眼可见——用户验收时是看 MD 文档，不是查 DB）。

**高风险遗漏区（重点扫描，上一轮全漏在这里）**：
- **🆕v8.x 升级注记**：草稿开头的版本摘要（如 `交易决策架构.md` L433）会点名一批新特性（Kronos/Mamba/TCP-RM/FactorMAD/模型量化等），这些**不是 H3 标题**，旧检查 A 抓不到
- **图框内具名项**：决策流全景图 ASCII 框里的模型/方法名（如 L2-A 信号层框里的 "Kronos-mini/base""Mamba/SSM""TCP-RM/DDCI"）
- **机制名**：如"因子直通(Model-Free Factor Fusion)""投票优先多Agent架构"——是机制不是 H3
- **参数/公式/方法论名**：如"半Kelly""Copula-GARCH""收缩估计"——方法论细节

**判定流程**：拿到草稿任一段落 → 提取其中所有具名特性 → 每个特性跨 13 个 battle_map MD 做 `Select-String -Pattern "<特性名>" -SimpleMatch` → `count=0` 即遗漏（详见 §8 第9步检查F）。

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

### 5.4 自主新增 flow_stage 的授权与流程（用户 2026-08-05 明确授权）

> **用户授权原话**："如果他有新的阶段是不是可以自主的增加阶段？不只现在的12个阶段可以自己再增加新的阶段，但是也是要符合我们作战地图里面的这个业务范围内的，不能是治理或者其他范围的，对吧"

**核心原则**：Kimi **有权**在必要时自主新增 flow_stage（第 12、13…个阶段），但必须严格限定在**交易作战业务范围**内。这不是鼓励新增——95% 的情况现有 11 阶段 + indicators 双轨制已足够；只有当草稿明确引入一个**全新的作战生命周期阶段**（现有 11 阶段都装不下）才考虑。

#### 5.4.1 允许新增 vs 禁止新增（二元判定）

| 判定 | ✅ 允许新增 flow_stage | ❌ 禁止新增（铁律5 域禁止） |
|---|---|---|
| 内容性质 | 交易作战生命周期的一个**新阶段**（有触发/消费/数据流的作战动作序列） | 治理 / 安全主体 / 运维主体 / Agent 主体 / 合规主体 |
| 示例 | 草稿 v9.x 引入"盘后模型部署"作为训练与回测之间的独立作战环节 | "治理审计阶段"——治理是元层面，不进作战地图 |
| 去向 | 新建 flow_stage + 建环节 | 留原架构图域，不挂作战地图，执行日志记录理由 |

**前置门槛（必须先过，否则不许新增）**：
1. 该内容**无法**归入现有 11 个 flow_stage 之一（逐个比对，记录为何都不合适）
2. 该内容**无法**归入 indicators 双轨制（不是参数/契约/时序，而是有独立数据流的作战动作）
3. 该内容**无法**归入横切机制（不是贯穿多阶段的全局机制，而是单一生命周期阶段）
4. 该内容属交易作战业务范围（非治理/安全主体/运维主体/Agent主体/合规主体）

#### 5.4.2 新增 flow_stage 的完整流程（4 处定义同步改 + 1 处对齐）

flow_stage 是受控词表，在 **4 处**定义。新增时 MUST 同步修改全部 4 处，否则 DB CHECK 阻断写入或生成器不渲染新阶段文档：

**① DB Schema 词表** — `src/zephyr/governance/persistence/battlemap_schema.py` L87-99 `_FLOW_STAGES` 元组
- 在元组末尾追加新值（如 `"model_deployment",  # 模型部署`）
- ⚠️ 改 Python 只影响**新建表**；现有表的 CHECK 约束需 ALTER：
  ```sql
  -- 先查现有约束名（PostgreSQL 自动命名为 battle_map_steps_flow_stage_check）
  \d battle_map_steps
  -- 删旧约束加新约束（VALUES 列表含全部旧值 + 新值，不能只写新值）
  ALTER TABLE battle_map_steps DROP CONSTRAINT battle_map_steps_flow_stage_check;
  ALTER TABLE battle_map_steps ADD CONSTRAINT battle_map_steps_flow_stage_check
    CHECK (flow_stage IN ('research_incubation','model_training','backtest_validation',
    'simulation_validation','stock_selection','buy_flow','sell_flow','position_management',
    'risk_control','execution','reconciliation','<新阶段>'));
  ```

**② 生成器词表** — `scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py`
- L93-105 `FLOW_STAGES` 列表追加 `("<new_id>", "<中文名>", "<两位编号>")`（编号续 max+1，当前 11 → 新阶段用 "12"）
- L113-125 `_STEP_PREFIX_TO_STAGE_FILE` 加前缀映射（如 `"BM-MD": "12_model_deployment"`）
- 新阶段会自动生成第 14 个文档 `battle_map_12_<new_id>.md`（panorama + 11 原阶段 + 1 横切 + 1 新阶段 = 14）

**③ 域白名单** — `docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml`
- 为新 flow_stage 添加允许的 domain 列表（参考 §5.1 格式）
- 域必须真实存在于 depgraph domain 体系，且属作战业务范围

**④ step_id 缩写** — 本文档 §2.4 + 生成器 `_STEP_PREFIX_TO_STAGE_FILE`
- 定义新阶段缩写（2-3 字母，如 MD=模型部署），续号规则同现有

**⑤ 对齐验证**：跑 `align_battle_map.py` + `align_panoramas.py` 确认无违例后才能建环节

#### 5.4.3 横切机制（battle_map_12 cross_cutting）≠ 新 flow_stage（重要区分）

> **上一轮遗漏的根因之一**：§11.5 说"挂 battle_map_12 横切视图"但没说**怎么挂**。横切内容走的是**另一条 YAML 轨道**，不是 flow_stage 步骤。

两种"新增"必须严格区分：

| 类型 | 横切机制（cross_cutting） | 新 flow_stage |
|---|---|---|
| **是什么** | 贯穿**多个**阶段的全局机制 | 生命周期的一个**新阶段** |
| **例子** | 四模式开关 / 应急降级路径 / 模型量化 / 因子治理引擎 / 信号生命周期 / 硬边界约束 | （假设）盘后模型部署阶段 |
| **写入位置** | `module_translation_registry.yaml` §**battle_map_cross_cutting** 段 | `battle_map_steps` 表 + §battle_map_steps YAML |
| **渲染产物** | battle_map_12 横切视图的 CC_xx 节点 | 新分阶段文档 battle_map_NN_*.md |
| **写入工具** | 直接编辑该 YAML（规则数据，TRAE-062） | apply_battle_map.py |

**判定规则**：若内容是"贯穿多阶段的全局机制"→ 横切（写 §battle_map_cross_cutting）；若是"生命周期的新阶段"→ 新 flow_stage。

**§11.5 已知遗漏的横切归属**：
- 模型量化（#4）→ §battle_map_cross_cutting 段新增 CC 项
- 因子直通层（#5）若判定为贯穿买卖的机制 → 横切；若仅买入用 → buy_flow step
- 投票优先多Agent（#6）若判定为支撑层横切 → §battle_map_cross_cutting；注意 Agent 主体不挂（铁律5），仅"投票优先机制"作为横切登记

#### 5.4.4 记录义务
新增 flow_stage 或新增横切机制 MUST 在执行日志记录：
- 新阶段名 + 编号 + 缩写 + 允许的 domain
- 为何现有 11 阶段 + indicators + 横切都不足（引用草稿证据：文件+行号）
- 四图对齐验证结果
- 若判定为横切而非新阶段，记录判定理由

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
**只有当以下四个条件全部满足，任务才算结束**：
1. **新功能数=0**：第9步检查发现 11 个草稿里再无"应挂未挂"的作战功能（每个 H3 都已判定为：已挂/已排/已归indicators）
2. **术语级覆盖全净（检查F，2026-08-05 新增）**：草稿所有具名特性（含 🆕v8.x 升级注记 / 图框内具名项 / 机制名 / 方法论名）在 13 个 battle_map MD 里 grep `count` 全部 >0，或有明确排除理由记录在执行日志
3. **双向对齐全净**：铁律9 的方向A+方向B 反查全部有结果，无幽灵锚点、无应挂未挂模块
4. **对齐脚本干净**：`align_panoramas.py` + `align_battle_map.py` 除 depth=3 告警外无其他违例

**只要还有"检查出能加入的功能/术语"，就必须再循环一轮**，不允许以"差不多了"为由提前结束。

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

#### 9.1 遗漏检查（7 项全过才算无遗漏：A/B/C/D/E + F术语级 + G章节对齐）

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

**检查 F：术语级覆盖反查（2026-08-05 新增，治本"升级注记/图框具名特性遗漏"，最强遗漏探测器）**

> 这是上一轮遗漏的根因治本检查。检查 A 只看 H3 标题、检查 B 只看 depgraph 已登记模块，两者都查不到"草稿正文/升级注记/图框里点名了但还没登记成模块的特性"。检查 F 直接对**渲染产物（13 个 battle_map MD）**做术语 grep，`count=0` 即遗漏。**这一步是用户最关心的"颗粒度全部呈现"的硬保证。**

**步骤**：
1. 从 11 个草稿提取**具名特性清单**（重点扫以下区域，不要只扫 H3）：
   - 每个草稿开头的"升级注记/版本摘要"段（如 `交易决策架构.md` L433 的 🆕v8.x 行）
   - 决策流全景图等 ASCII 图框内的具名项
   - 正文里的模型名/方法名/机制名（Kronos/Mamba/SSM/TCP-RM/DDCI/FactorMAD/因子直通/投票优先多Agent/模型量化/Copula-GARCH/收缩估计/半Kelly 等）
   - 参数名/公式名/约束编号（C-xxx/B-xxx/E-xxx）
2. 对每个术语，跨 13 个 battle_map MD 文件计数：
   ```powershell
   cd "docs\02_enterprise_architecture\07_trading_decision_architecture\battle_map"
   $c = (Select-String -Path "battle_map_*.md" -Pattern "<术语>" -SimpleMatch).Count
   # $c=0 → 遗漏
   ```
3. `count=0` 的术语 → **遗漏**。逐个处理（参考 §11.5 已知清单的处理方向）：
   - 若属作战动作且域在白名单 → 登记 depgraph planned 模块 + 建 battle_map 环节/锚点（走 §6.1 流程）
   - 若是参数/契约/方法论细节 → 归入最相关环节的 indicators JSONB + 叙事 YAML
   - 若属禁止域（治理/安全主体等，铁律5）→ 不挂，但在执行日志记录"已审查，域禁止，留原架构图"
4. 处理后**重跑生成器**，再次 grep 确认 `count>0`（否则没生效）

**检查 G：源文档章节对齐反查（2026-08-05 新增，治本"整段章节无承载"）**
- 对每个草稿的**每个主要章节**（H2 级，如 `交易决策架构.md` 的"决策流全景图" L431-860 含 7 部分），列出它在 battle_map 的承载文件 + 环节 ID
- 任何主要章节**找不到承载者** → 遗漏
- 例：`交易决策架构.md` L431-860 的 7 部分（共享信号注入层 / 选股6层漏斗 / 买入决策流 / 卖出八层 / 仓位五层 / 执行闭环 / 支撑层）每一部分都要能指到具体 battle_map 文件和环节
- 输出对齐表到执行日志（产物2）

#### 9.2 循环决策
- 若 9.1 的 A/B/C/D/E/**F/G** **任一项发现遗漏** → 记录遗漏清单到执行日志，**回到第2步开始下一轮**（第2步增量更新映射表，重点处理遗漏项；**检查F发现的遗漏优先处理**）
- 若 9.1 七项**全部通过（0个遗漏）** → 满足循环终止条件1+2，进入最终验收

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
- 对齐验证结果（检查 A/B/C/D/E/F/G 每轮结果，F 术语级遗漏清单+G 章节对齐表）
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

## 11.5 已知遗漏清单与对照方法（2026-08-05 实测，Kimi 必须优先处理）

> 以下 6 项是 2026-08-05 用户验证后**确认在 13 个 battle_map MD 文件里 `count=0`** 的遗漏。Kimi 第 1 轮就必须处理完，不要等到循环检查 F 才发现。处理方式：能挂的登记 depgraph planned 模块 + 建环节/锚点；属参数/方法论的归 indicators；属禁止域的记录理由。处理完重跑生成器，grep 确认 `count>0`。

### 已确认遗漏（6 项，全部来自 `交易决策架构.md` L433 升级注记 + 决策流全景图 L431-860）

| # | 特性名 | 来源 | 版本 | battle_map 现状 | 处理方向 |
|---|---|---|---|---|---|
| 1 | **Kronos-mini/base**（金融K线 TSFM 零样本预测） | L433 + L465-468，L2-A 信号层图框 | v8.2 | `count=0` | L2-A 信号层，登记为 D_ASHARE_SIGNAL/D_SIGNAL 域 planned 模块，挂到 stock_selection 某信号环节，或归 BM-SEL-13 密度预测族 indicators |
| 2 | **Mamba/SSM 时序增强**（与 Transformer 互补） | L433 + L455-456，L2-A 图框 | v8.1 | `count=0` | 同上，L2-A 时序增强，挂信号环节或归 indicators |
| 3 | **TCP-RM/DDCI**（自适应保形非平稳覆盖） | L433 + L461-464，L2-A 图框 | v8.1 | `count=0`（共形预测 BM-SEL-14 已有，但自适应变体未体现） | 挂 BM-SEL-14 共形预测环节为子环节/indicators，登记 planned 模块 |
| 4 | **模型量化** | L433，横切层 | v8.1 | `count=0`（MCP 协议已在 battle_map_09，但模型量化未体现） | **横切机制**→ 写 `module_translation_registry.yaml` §battle_map_cross_cutting 段新增 CC 项（§5.4.3），不是 flow_stage step |
| 5 | **因子直通层（Model-Free Factor Fusion）** | L575-577（买入）+ L743（卖出） | v7.0 | `count=0` | 贯穿买卖两阶段→优先判定为**横切**（§5.4.3，写 §battle_map_cross_cutting）；若仅买入用则挂 buy_flow step。登记 D_SIGNAL/D_ORCHESTRATOR 域 planned 模块 |
| 6 | **投票优先多Agent架构**（先投票后辩论，投票<100行，§29.39 裁定17） | L433 + L856，支撑层 | v8.2 | `count=0`（battle_map_01 D-RESEARCH-11 有通用多Agent协作，但非此特定投票优先架构） | 支撑层横切→ §battle_map_cross_cutting 段（§5.4.3）；注意 Agent 架构主体不挂作战地图（铁律5），仅"投票优先机制"作为横切登记，在调用点挂锚点 |

### 已确认覆盖（Kimi 勿重复处理）
- FactorMAD（v8.2 因子挖掘）✓ battle_map_02
- C-045 深度拥挤度 ✓ battle_map_05/07/08/12
- R&D-Agent-Quant 联合优化 ✓ battle_map_12 L421
- 共形预测 ✓ battle_map_05 BM-SEL-14
- MCP 协议 ✓ battle_map_09

### 对照方法（实测有效，Kimi 可参考并改进）

**方法 A：术语级 grep 对照（检查F的核心，最强）**
1. 逐部分读源文档（如 `交易决策架构.md` L431-860 的 7 部分）
2. 提取每部分的具名特性（尤其 🆕v8.x 升级注记里的具名模型/方法名）
3. 对每个术语跨 13 个 battle_map MD 计数：`Select-String -Path "battle_map_*.md" -Pattern "<term>" -SimpleMatch`
4. `count=0` → 遗漏；处理完重跑生成器再 grep 确认 `count>0`

**方法 B：源文档章节对齐（检查G的核心）**
1. 把源文档按主要章节切分（如决策流全景图 7 部分）
2. 对每部分，指认它在 battle_map 的承载文件 + 环节 ID
3. 任何部分无承载者 → 遗漏

**方法 C：双向反查（已有检查B/E）**
- depgraph 作战相关域模块 → battle_map_anchors 反查（应挂未挂）
- battle_map 锚点 → depgraph 反查（幽灵锚点）

**Kimi 可用更好方法**：上述方法是基线，Kimi 若有更系统的方法（如写自动化术语提取脚本扫描全文、章节对齐表生成器）鼓励使用，但**验收标准不变**：草稿每个具名特性在 battle_map MD 里 `grep count>0` 或有排除理由，且经生成器渲染后在 MD 里有文字显示。

---

## 12. 验收标准（用户起床后检查）

1. ✅ 全部作战地图文档已通过生成器重新生成（当前 13 个：panorama + 11 阶段 + 1 横切；若按 §5.4 新增了 flow_stage 则相应增加，git diff 显示自动更新）
2. ✅ 作战环节总数 285 → 不超过 450
3. ✅ `align_battle_map.py` + `align_panoramas.py` 干净（depth=3 告警除外，有说明）
4. ✅ 映射表（产物1）覆盖 11 草稿所有 H3，每个有处理动作
5. ✅ 执行日志（产物2）完整记录**每轮循环**（轮次/新增/遗漏/决策）
6. ✅ 被排除的 5 类内容有明确去向说明
7. ✅ indicators 6件套填实（草稿细节不丢）
8. ✅ 无幽灵锚点（BM-INV-002，铁律6）
9. ✅ 新增模块在 depgraph 有对应 planned 节点（依赖先行，铁律3）
10. ✅ git commit 已提交最终结果
11. ✅ **循环已终止**：第9步检查 7 项全过（0遗漏，含 F 术语级 + G 章节对齐），或达 5 轮上限并有"待人工复核"清单
12. ✅ **双向对齐验证**（铁律9）：方向A(step→modules)+方向B(module→step)反查全部有结果，无应挂未挂模块
13. ✅ **术语级覆盖验证**（检查F，2026-08-05 新增）：草稿所有具名特性（含 🆕v8.x 升级注记 / 图框具名项 / 机制名 / 方法论名，参考 §11.5 清单 + 自行扫描 11 草稿全文）在 13 个 battle_map MD 里 `grep count` 全部 >0 或有明确排除理由记录在执行日志
14. ✅ **源文档章节对齐验证**（检查G，2026-08-05 新增）：11 草稿每个主要章节（H2 级）都能指认 battle_map 承载文件 + 环节 ID，无整段无承载
15. ✅ **已知 6 项遗漏已处理**（§11.5）：Kronos / Mamba·SSM / TCP-RM·DDCI / 模型量化 / 因子直通 / 投票优先多Agent 全部 `count>0` 或有排除理由
16. ✅ **横切机制正确归轨**（§5.4.3，2026-08-05 新增）：贯穿多阶段的全局机制写入 `module_translation_registry.yaml` §battle_map_cross_cutting 段（横切轨），而非误建为 flow_stage step；若按 §5.4 新增了 flow_stage，已同步改 4 处定义 + 对齐验证 + 执行日志记录理由

---

**开始执行。记住：宁可慢、宁可保守，不要违反铁律、不要污染作战地图语义边界。作战地图的价值在于"一眼看清交易作战流程"，不是"什么都往里塞的杂物间"。**
