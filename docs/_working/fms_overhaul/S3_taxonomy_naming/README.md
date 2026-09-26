---
ttl: task_bound
title: S3 分类学与命名 · 挖矿簿（命名三套普查/镜像树测量/非ASCII清单/分类学v2规格/施工处方）
created: 2026-09-27
sid: st-fms-chief-20260927
lane: S3
status: 挖干（1 项口径裁定留总筹，见 §5.4，不阻塞 B9 开工）
---

# S3 分类学与命名 — 挖矿簿

## ① 职责一句话

为 docs/03_modules 的三套并存命名体系给出十年级收敛规格（镜像树映射函数 + 命名规则 + 深度/扇出帽 + 渐进迁移棘轮），并指认规格真源落点与执法门挂点。

## ② 现状实测（本会话 2026-09-27 实测，证据均为 file:line 或命令可复现）

### 2.1 三套命名体系普查（docs/03_modules，共 4,776 件 = yaml 3,353 + md 1,423）

| 体系 | 规模 | 形态 | 写者 | 管辖门 |
|------|------|------|------|--------|
| A. MOD-\* 大写扁平 | 仅存 2 件：`docs/03_modules/MOD-ALT-EMOTION-INDEX-BUILDER.md` + `docs/03_modules/MOD-CHAINPILE-METAQ/blueprint.md` | 单文件/单目录蓝图，SCREAMING ID 即文件名 | 人(AI)手写蓝图 | check_ssot_gate（[MODULE] 冲突检测，.pre-commit-config.yaml:542-549） |
| B. \_domain\_\*/algo_flow 树 | 56 个 `_domain_*` 目录；algo_flow 下 3,353 个 yaml | 每 .py 一份外部算法真源 yaml，子目录镜像 src 子包（如 `_domain_gov_enforcement/algo_flow/behavioral_admission/`） | 生成器（code_algorithm_extractor 出仓批；样例头自述"2026-09-15 P2-1 契约头减负批量出仓"） | GATE-ALGO-FLOW（.pre-commit-config.yaml:131-140）+ algo_flow_link_gate（src/zephyr/gov_enforcement/commit_gates/algo_flow_link_gate.py:9-11，锚指向 yaml 必须存在+可解析+图可达） |
| C. 模块目录树（含 \_cross_layer 叠层） | 544 个含 blueprint.md 的模块目录；blueprint.md 553 + index.md 842；`_cross_layer` 70 件、`_master_blueprint` 5 件、`_system_master` 2 件 | kebab/snake 模块目录，内含手写 blueprint.md + 生成 index.md | blueprint=人(AI)手写+AUTOGEN 全景节生成（generate_blueprint_panorama.py + sync_panorama_module.py，见 MOD-ALT-EMOTION-INDEX-BUILDER.md:24）；index.md=生成器 scripts/governance/d1_structure/generate_missing_index_md.py:1-2（MOD-INF-005, production） | check_ssot_gate 间接 + gate-17-orphan-py（.pre-commit-config.yaml:398-405，只管 .py 不管 docs）；check_blueprint_automation_sync.py **已导出未接线**（仅 scripts/governance/d5_architecture/checkers/__init__.py:6 引用，pre-commit 无 entry=执法空洞） |

- 体系 B yaml 样例（docs/03_modules/_domain_data/algo_flow/alerter.yaml:1-7）：`doc_type: architecture_view` / `ttl: permanent` / `module: src.zephyr.data.alerter` / `source_of_truth: src/zephyr/data/alerter.py`——文件即"算法地图外部真源"，由 .py 内单行锚 `# [ALGO_FLOW] external: <yaml路径>` 反向指认（样例 src/zephyr/gov_enforcement/behavioral_admission/admission_controller.py:21）。
- 蓝图 [MODULE] 自证行机制（docs/03_modules/MOD-ALT-EMOTION-INDEX-BUILDER.md:9-12）：`# [BLUEPRINT] MOD-...` + `<!-- [MODULE] zephyr.alt_data.emotion_index_builder -->` 注释锚把 md 绑到 dotted module path。**覆盖率仅 55/553 blueprint.md**——多数蓝图的代码绑定靠 frontmatter `module_id` + path_ownership_map 的 depgraph_node 声明，自证行未普及。
- 漂移史：体系 A 曾是主流，commit 250a8e3bf5b（fix(ARCH-056)）"删除140个空蓝图，移动对齐引擎蓝图到功能域子目录"= 大迁移已发生过一轮；template_registry.yaml:18-20 引用的 blueprint_registry.yaml 已整体退役（全仓仅存 scripts/_archive/governance/d3_metadata/validate_blueprint_registry.py）。

### 2.2 镜像树可行性测量（src/zephyr 58 包目录全集实测，非抽样）

- 包级文档覆盖：55/55 实包（除 `__pycache__`）在 docs/03_modules 均有 algo_flow yaml —— **覆盖 100%**。零覆盖疑点排雷：ai_layer 有档（docs/03_modules/_domain_ai_layer/algo_flow/approval_router.yaml:1 注明真源 src/zephyr/ai_layer/switch_engine/approval_router.py，仅 `module:` 行缺首段导致正则漏计）；strategy_factory 有档（docs/03_modules/_domain_portfolio_core/algo_flow/strategy_factory.yaml）。
- 文件级锚覆盖：3,297/3,736 个 src/zephyr .py 带 `[ALGO_FLOW] external` 锚 = **88.3%**；`# [MODULE]` 标记 3,558/3,736 = 95.2%。
- 但**物理目录 ≠ 1:1 镜像**：包名→域目录需经改名典（实测样例）——market_data→`_domain_mkt_data`、ml_train→`_domain_machine_learning_train`、execution_simulation→`_domain_execution_sim`、ex_core→`_domain_execution_core`、pf_core→`_domain_portfolio_core`、signal_ashare→`_domain_signal`、signal_fundamental→`_domain_fundamental_signal`、infra_ops→`_domain_infrastructure_operations`、infra_runtime→`_domain_infrastructure_runtime`；跨域安放：cross_asset→`_domain_trading`、nlp→`_domain_intelligence`、strategy_pipeline→`_domain_backtest`、experiment_tracking→`_domain_infrastructure`、clone_guard→`_domain_gov_enforcement`+`_cross_layer/clone_guard`。同包双目录漂移：`_domain_plan` 与 `_domain_plan_engine` 都装 plan_engine 文档；`_domain_pf_alloc` 与 `_domain_portfolio_alloc` 并存。该改名典**无任何真源文件承载**（散落在提取器/生成器代码与历史约定里）。
- "代码↔文档"现行对齐靠四层叠加（无单一平面）：(1) `[ALGO_FLOW] external` 锚（强，双门管辖）；(2) `# [MODULE]` dotted 路径（中，check_ssot_gate 只查冲突不查存在）；(3) docs/03_modules/path_ownership_map.yaml:1-17——自动生成（generate_path_ownership_map.py，2026-09-17），8,096 条 path claim + 22 条 ssot claim + 0 冲突；(4) 注册表：module_translation_registry.yaml（docs/01_policies_and_standards/_registry/catalogs/，unique_key=module_path 精确 .py 路径 :22-26，条目样例 :34/:46/:58 带 domain_id=D_EX_CORE/D_RISK）；capability_canonical_file_registry.yaml:9-12（v1.1.0 起canonical_file/module_id/domain 全部由 CapabilityLookup 从磁盘头部+git log 自动派生，YAML 只写能力索引）；functional_domain_registry.yaml:27-35（entry_schema 含 ssot_path，:1226 自述 63 域）。

### 2.3 深度与扇出

- 全仓路径段数分布（git ls-files | awk -F/ NF）：峰值 10 段仅 3 件（src/zephyr/frontend/dashboard/web/assets/media/img/brand/ 静态图）；≥8 段 226 件基本全是 frontend 资产；主流量在 4-6 段（6,188+2,817）；≥6 段 = 4,341 件（与总筹晨测 4,338 差 3 = 在途漂移，口径一致）。
- 目录扇出 top：`docs/03_modules/_domain_data/algo_flow` 120 件、`_domain_signal/algo_flow` 104、`_domain_trading/algo_flow` 97、`_domain_factor/algo_flow` 84——top10 全部 >69，全是体系 B 生成区；手写区扇出温和。

### 2.4 非 ASCII 路径（交付物 `_data/non_ascii_paths.txt`，126 条已写盘）

- 分布全在 docs/：`docs/_working` 84（archive/ 31、fullflow_mining/ 29、automation/ 21、同花顺资料/ 2、2026-09-18_vocab_consolidation_campaign/ 1）+ `docs/_archive` 42（依赖图/ 31、架构图/ 11）。
- 年代：`_archive` 两族停在 2026-08-28（冷死区）；`_working/archive` 2026-09-20、fullflow_mining 最近提交 2026-09-26（昨日仍活跃的历史挖矿作业区）、automation 2026-09-18、同花顺资料 2026-09-09。
- 避让核验：与 st-p15-phantom 作业面（decision_map_campaign_20260924/three_piece_infra）重叠 **0 条**；与本战役区重叠 **0 条**。均不在在途避让清单内，处置主责归 S2（生命周期），S3 仅供基线。

## ③ 六向台账（对象="模块文档分类学与命名"这一事实类）

- **真源**：锚平面的真源是 .py 内 `[ALGO_FLOW] external` 单行（每文件自带，无中心册）；目录语义真源=无（改名典散落生成器代码）；命名规则真源=docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml:12-13（REG-DOMAIN-NAMING-001，"域命名规则唯一真源"，NR-001..005 仅覆盖域 ID，不覆盖路径/文件名）+ trae_028_doc_structure_naming.yaml §doc_001（路径小写 snake_case、禁 kebab-case、禁大写 L 前缀）+ validate_module_id_naming.py DOMAIN_ID_RE（NR-002 指认的执行真源）。
- **写者**：体系 B=生成器批量出仓（单写者达成）；体系 C blueprint=人(AI) 手写+全景节生成器；index.md=generate_missing_index_md.py；path_ownership_map=generate_path_ownership_map.py；改名典=无写者（隐性知识，最大治理缺口）。
- **消费者**：algo_flow_link_gate/GATE-ALGO-FLOW（锚↔yaml）；check_ssot_gate（[MODULE]）；generate_blueprint_panorama.py/sync_panorama_module.py（全景）；capability_lookup（模块翻译注册表）；总包对齐 alignment_checklist（module_id 对齐键）；图书馆 lookup。
- **漂移史**：(1) MOD-\* 扁平→功能域子目录大迁移（commit 250a8e3bf5b，删 140 空蓝图）；(2) blueprint_registry.yaml 退役（template_registry.yaml:18-20 引用残留=死指向）；(3) 2026-09-15 P2-1 与 2026-09-25 P1 两轮契约头出仓批量造出 3,353 yaml；(4) 同包双目录（_domain_plan vs _domain_plan_engine、_domain_pf_alloc vs _domain_portfolio_alloc）；(5) check_blueprint_automation_sync 导出未接线。
- **冲突面**：(a) 总骨架 §6.1 "ASCII kebab-case" vs TRAE-028 §doc_001 "禁 kebab-case"——战役自证纪律与在册法律正面冲突，须总筹裁定（本战役实际文件名均为 snake，实质无违反）；(b) st-p1b-libr 在改 module_translation_registry/capability_canonical 两册——本规格不碰这两册，映射函数落共享新模块；(c) S1 的 FMS-HYGIENE 新路径 ASCII 查类消费本簿基线清单——只读交接；(d) 非 ASCII 存量处置与 S2 的 _working/_workspace 陈化方案同机耦合。
- **净零方案**：规格=扩展现有 domain_naming_rules.yaml（新增 NR-006+ 条目），不立新册；物理镜像迁移=复用既有 git mv+RENAME-DEPGRAPH-SYNC+锚重写脚本，不新增第二套对齐机制，退役 path_ownership_map 之外的隐性改名典（收敛进 resolver 单写者）；MOD-\* 残件 2 件墓碑化后体系 A 归零。

## ④ 分类学 v2 规格草案（十年级，供 B9 方案批采纳/修订）

### 4.1 镜像树规则（映射函数）

- 定义 `M(src/zephyr/<pkg>/.../mod.py) = docs/03_modules/<pkg>/.../mod.<kind>.yaml|md`：**首段=src 包名原样**，逐段对应，禁止改名典（mkt_data/machine_learning_train 等翻译层全部废除）；`__init__.py` → `<seg>__init__.yaml`（沿用现状命名，见 _domain_trading/algo_flow/action_dispatcher__init__.yaml）。
- 域分组降维：`_domain_*` 56 目录退役为**生成视图**（由 frontmatter `functional_domain` + functional_domain_registry 派生的索引页，归 S7 regen-clean），不再承担物理父目录职责；`_cross_layer`/`_master_blueprint`/`_system_master` 保留为**显式叠层**（无 src 归属的横切件：接口契约/总图），成员清单登记成册（可生成）。
- 现实依据：文件级映射已 88.3% 锚化，包级已 100% 有档——本规则不是新建对齐，而是**把隐性映射函数显式化+单写者化**（共享 resolver：`resolve_doc_path(module_path)` 唯一实现，锚行生成/校验/lookup 三方调用）。
- 深度帽：**文件全路径 ≤7 段（≤6 层目录）**。理由：现状 ≥8 段仅 226 件且 98% 是 frontend 静态资产；docs 树峰值 8 段；7 段内 `docs/03_modules/<pkg>/<sub>/<file>` 天然够用。新路径硬拦，存量入棘轮基线。
- 扇出帽：**手写区单目录 ≤50 条目；生成镜像区 ≤150**（超限必须按 src 子包继续分层——镜像规则天然提供分层轴）。理由：现状 max 120（_domain_data/algo_flow）；镜像区扇出与 src 包文件数线性同构，150 对应"该拆包"的架构信号。

### 4.2 命名规则

| 对象 | 规则 | 真源/执法 |
|------|------|-----------|
| 路径段（目录+文件名） | ASCII snake_case，禁 kebab/大写/中文 | 扩展 TRAE-028 §doc_001 既有约束 + S1 FMS-HYGIENE 新路径查类；存量 126 条入基线豁免（只减不增） |
| 保留文件名 | index.md / blueprint.md 为目录保留名，禁止挪用 | 新检查器（或 check_blueprint_automation_sync 接线后一并） |
| ID 类 | MOD-\*（模块蓝图）/ D\_（域）/ C-（能力）/ REG-（注册表）SCREAMING 前缀制 | domain_naming_rules.yaml NR-001..005 + validate_module_id_naming.py DOMAIN_ID_RE（现状已闭环，v2 不动） |
| 口径裁定（留总筹） | 总骨架 §6.1 "kebab-case" 与 TRAE-028 "禁 kebab" 二选一：建议统一 snake_case（在册法律+现状 96% 文件已是 snake，改口径成本最低） | Owner 裁定登记 |

### 4.3 渐进迁移策略（禁大爆炸，棘轮驱动）

- R0 即日：新文件一律新规（镜像路径 + ASCII + 双帽）——由 S1 FMS-HYGIENE 门执法，零存量动作。
- R1 收尾退役（第一批，零消费者风险）：体系 A 残件 2 件墓碑化——MOD-ALT-EMOTION-INDEX-BUILDER.md 迁入镜像模块目录并加 `successor_of`；MOD-CHAINPILE-METAQ/ 同批。blueprint_registry 死指向（template_registry.yaml:18-20）顺手清偿。
- R2 触碰即改：任何 git mv / 模块文件移动触发 RENAME-DEPGRAPH-SYNC 时，同 commit 完成"锚行重写 + doc 归位镜像位 + depgraph --force + index/ownership regen"四连（工具化为一个迁移脚本，锚行是单行路径，机械重写无歧义）；存量非 ASCII 文件被触碰（promote/归档）时同步改 ASCII 名。
- R3 试点批（验证工具链）：迁 3 个最小包 runtime(2 件)/red_blue_validator(1 件)/infra_ops(5 件)，全链 regen-clean 双向验证通过才放大。
- R4 大批量后波：同包双目录先并筒（_domain_plan 并入 _domain_plan_engine、_domain_portfolio_alloc 并入 _domain_pf_alloc），再按域逐批迁移 algo_flow 树（3,353 件），一域一 commit；每批 `regenerate && diff --exit-code` 验证。
- R5 视图化收尾：`_domain_*` 物理目录退役为生成索引视图（依赖 S7 regen-clean 就绪——**此为迁移后波的硬前置，不满足则停在 R3**）。
- 迁移顺位依据：冷区→小包→大区，死区（_archive 42 条非 ASCII）与 R1 同批，活区（fullflow_mining 等 84 条）随 S2 归档动作棘轮化。

### 4.4 与既有门的兼容性核验（逐门）

- RENAME-DEPGRAPH-SYNC：迁移=批量 git mv，每批必过 `generate_project_depgraph.py --force`（既有硬拦，天然兼容，且是 R2 四连的执法保障）。
- GATE-ALGO-FLOW + algo_flow_link_gate（.pre-commit-config.yaml:131-140、algo_flow_link_gate.py:9-11）：只验"锚指向的 yaml 存在+可解析+图可达"，不验路径政策——迁移同 commit 重写锚行即可两门全绿；路径政策由新规则条目管，门不重复建设（净零）。
- ORPHAN gate-17（.pre-commit-config.yaml:398-405）：管辖 .py 位置，与 docs 迁移无交集。
- check_ssot_gate（:542-549）：[MODULE] module_path 冲突检测在迁移中照常生效，是并筒批次的防撞闸。
- 蓝图 [MODULE] 自证行：v2 要求 blueprint frontmatter 增 `module_path:` 字段（新文件必填；存量触碰时补），校验挂 check_blueprint_automation_sync 接线后——该检查器已存在（scripts/governance/d5_architecture/checkers/）只差 pre-commit entry，接线移交 B9/S7，属"新门以退役旧门配对"候选。

## ⑤ 施工处方

1. **规格真源落点=扩展 `docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml`**（REG-DOMAIN-NAMING-001）：新增 NR-006（镜像映射函数与路径段规则）/NR-007（ASCII 强制）/NR-008（深度帽 ≤7 段）/NR-009（扇出帽 50/150）/NR-010（保留名），复用既有 entry_schema（rule_id/rule_text/applies_to=create|rename|both/severity——NR-002 已示范"rule_text 指认执行真源代码"的写法）。判据：命名规则同域收敛唯一（内收 w5_1"同域重复簇→收敛唯一"），不立新册；该册不在 st-p1b-libr 在途清单内（避让安全）；apply_depgraph `--insert-domain` 只消费 create 类规则，路径类规则的执法钩子各自指向 FMS-HYGIENE/迁移脚本，不塞进建域校验。
2. **映射函数单写者**：施工批新建共享 resolver（如 scripts/governance/_shared/doc_path_resolver.py），三方（锚生成器/校验门/图书馆 lookup）改调它；module_translation_registry 与 capability_canonical 两册**一字不改**（p1b 领地）；resolver 走标准仪式（14 字段头+creation_token+add_module_translation+depgraph 登记）。
3. **基线交接**：`_data/non_ascii_paths.txt`（126 条）交 S1 作 FMS-HYGIENE 生成基线豁免输入；_archive/_working 两族的处置时序与 S2 方案合并执行（promote/归档=改名时机）。
4. **移交项**：(a) snake vs kebab 口径 → 总筹裁定登记；(b) check_blueprint_automation_sync 接线 → B9/S7；(c) R5 视图化前置条件（regen-clean 框架）→ S7 对齐。
5. 改动既有文件（domain_naming_rules.yaml、TRAE-028 等）在施工波进行，先 `lock_files.py acquire <file> st-fms-chief-20260927`；本挖矿波零改动已遵守。

## ⑥ 自审闸三态

- **状态：挖干**。施工代理持本簿可直开 B9 方案批：规格条目文本（§4.2 NR-006..010 草案）、落点文件（§5.1）、迁移序列（§4.3 R0-R5）、门兼容核验（§4.4）齐备。
- 证据强度：全部数字本会话实测可复现（命令见各节）；唯一非实测引用=总筹晨测 4,338（与本测 4,341 差 3，在途漂移已注记）。
- 未干项：无。
- 受阻项：无硬阻塞；1 项软等待=§4.2 口径裁定（不阻塞 B9 起草，规格文本已按"snake_case"单方拟定，裁定若反向仅需改一词）。
