---
ttl: task_bound
---

# W1c 门禁与测试口径挖矿——target_layer 词表收编连坐清单

- 战役：st-vocabconsol-20260918 · 环节 W1（三路侦察之门禁/测试侧）
- 实查日期：2026-09-18 · 方法：只读 grep/Read/registry 交叉核对（全部路径均实查）
- 三件改动基准：① `docs/01_policies_and_standards/_registry/vocabularies/target_layer_vocabulary.yaml`（A 组 16 值入 values + B 组 9 值入 aliases/deprecated + total_values 45→61 + version 1.1.0）；② `scripts/governance/d5_architecture/validators/validate_target_layer.py`（total_values 自校 + L1/L2/L3 假红治本）；③ 新增 `scripts/governance/d5_architecture/validators/check_vocab_domain_convergence.py`（常驻差集校验，暂名）。

---

## §1 结论速览（先读）

1. **tests/ 全库无任何测试断言词表内容**——`target_layer_vocabulary` / `validate_target_layer` / `total_values` 三个关键词在 tests/ 零命中；**改词表不会直接变红任何 pytest 测试**。真正的连坐在 commit 门禁链与注册表/清单派生件。
2. **validate_target_layer.py 不在 pre-commit / CI / hook 链**（`.pre-commit-config.yaml` 与 `.github/workflows/*.yml` 零调用），也**未登记为 gate_registry 的 gate**；它只存在于注册表/清单派生面。修它无 CI 连坐，但新增同族脚本要过完整准入链（§3.3）。
3. **校验器零豁免机制**：只有 `--warn-only` 与 `.aidrafts/` 路径跳过，无 noqa/白名单；13 条假红治本首选「正则按 docstring 既有承诺收紧」而非发明新豁免（§4）。
4. **最危险连坐点**（详见 §2）：
   - `TRANSLATION-COVERAGE`（priority=59，硬阻断）+ `CREATE-GUARD`（priority=60，硬阻断，tests/ 豁免）+ `MANUAL-ONLY-PERMANENT`（priority=43，硬阻断）对新 .py 三连拦——W3c 差集脚本若无大白话简介/creation_token/manual-noqa 即 commit 被卡。
   - `GATE-VOCAB`（files_trigger 含 `vocabularies/.*\.yaml`）——**任何词表编辑都触发** `check_vocab_hardcode.py --ci` + `generate_derived_files.py --check`；A 组 16 值扩集会让「≥2 值字面量集合恰为词表子集」的存量代码点进入新可检出域（§3.1）。
   - `REGISTRY-MASS-DELETION`（priority=140）——B 组若使 `functional_domain_registry.yaml`/`module_translation_registry.yaml`（在 `_registry/catalogs/`，命中判定目录）条目数减少即硬阻断，需 `[allow-mass-deletion:reason≥10字]` commit message 逃生或保证不减条目。

---

## §2 连坐清单总表（改动 × 受影响件 × 判据/断言 × 处置建议）

### 2.1 改动① 词表 YAML 收编

| # | 受影响件 | 判据/会断言什么 | 连坐判定 | 处置建议 |
|---|---------|----------------|---------|---------|
| 1-1 | pre-commit `GATE-VOCAB`（gate_registry.yaml L169-179；entry=`run_gate_chain.py check_vocab_hardcode.py --ci` + `generate_derived_files.py --check`；files_trigger=`^(src/zephyr/.*\.py|scripts/.*\.py|docs/01_policies_and_standards/_registry/vocabularies/.*\.yaml)$`） | ①全库 .py 词表硬编码扫描（含新增值集）②派生文件一致性 | **必触发**（词表 YAML 路径命中 trigger）；`target_layer` **不在** `generate_derived_files.py` 的 `VOCAB_FIELD_MAP`（L91-114 实测 22 键，无 target_layer），且 `frontmatter_schema.json`/`architecture_contract.yaml`/`frontmatter_field_registry.yaml` 三派生件 grep 无 target_layer → 派生件**无需**同步；风险只剩硬编码子集误报 | 改后本地跑 `python scripts/governance/d3_metadata/check_vocab_hardcode.py --ci` 看 16 新值是否把存量代码（尤其 `blueprint_decomposer._FUNC_DOMAIN_TO_TARGET_LAYER` 13 值 dict、ct_pipe 系）推进新违规；命中行走 `# noqa: gate-vocab  <理由>`（注意 §2.1-4 的基线棘轮） |
| 1-2 | in-process `VOCAB-HARDCODE`（priority=80，vocab_hardcode_gate.py） | staged **新增** .py 子集检测（diff-filter=A），subprocess 复用 check_vocab_hardcode（SSoT） | 词表编辑本身不触发（只查新 .py）；与 W3c 新脚本叠加触发（见 3-x） | 无需动作；W3c 脚本内禁写字面值集合 |
| 1-3 | in-process `VOCAB-CHAIN`（priority=80/73，vocab_chain_gate.py） | staged 新增 .py 中字符串字面量匹配 `^docs/01_policies_and_standards/.*\.ya?ml$` 等 SSoT 全路径 → 硬阻断；豁免目录含 `governance/d3_metadata/`、`governance/generators/`，**不含** `d5_architecture/validators/` | 对 W3c：新脚本加载词表**只准**用 `yaml_utils.load_vocabulary_values("target_layer_vocabulary.yaml")` 裸文件名（validate_target_layer.py 用 `Path(REPO_ROOT)/"docs"/...` 分段拼接躲过——但它是存量） | 施工时以 `_shared` SSoT loader 为依赖，零全路径字符串字面量 |
| 1-4 | `check_vocab_hardcode.py` 的 gate-vocab noqa 基线棘轮（L154-164：`_NOQA_REGISTRY_PATH = config/governance/noqa_exempt_registry.yaml`，基线=len(exemptions) 自动算，fallback 33） | gate-vocab 豁免总数超基线 → GATE-VOCAB 校验失败 | 若因 16 新值需给存量文件加 `# noqa: gate-vocab`，豁免计数上涨会被棘轮拦 | 新增豁免须同步登记 `config/governance/noqa_exempt_registry.yaml` 的 exemptions 条目（该文件即基线真源） |
| 1-5 | 词表文件自身门禁：`GATE-FRONTMATTER`（check_frontmatter_metadata.py --ci，staged 文件 ttl/doc_type）、`REGISTRY-YAML-PARSE`（staged 登记表 YAML 可解析+结构） | 词表 YAML 已有 `[A_config]` 头 + schema_version/doc_type/ttl 字段 | 保持现有结构即可；values 段格式必须维持 `- value: X` dict 列表（validator `load_vocabulary` 读 `v["value"]`，L89） | A 组条目逐条 `value/definition/is_foundation/ai_keywords` 四字段齐全；**is_foundation 全 false**（true 会改 CT-PIPE M5/M6 路由=Owner 门位） |
| 1-6 | 运行时消费面（不红但漂移）：`ct_pipe_routing.py:69`、`routing_plugins.py:70` 经 `load_vocabulary_section_list("target_layer_vocabulary.yaml","foundation_domains")` 动态加载 | 只读 `foundation_domains` 段（3 值）；A/B 组不动该段 → 路由零变化 | 无 | 在 PR 说明留痕「foundation_domains 未动」 |
| 1-7 | `blueprint_decomposer.py` L186-199 `_FUNC_DOMAIN_TO_TARGET_LAYER` 硬编码 13 映射（注释宣称"对齐 v1.0.0"） | 无测试断言（tests/blueprint/test_blueprint_decomposer*.py 实测无 target_layer/D_ 断言） | 不红；但 version 1.1.0 后注释失准 | 登记为 W4/后续迁移件，或本包顺手改注释指向"以词表为准"；**勿**在 W3 扩它的 map（另生第二真源，VOCAB-HARDCODE 风险） |
| 1-8 | `capability_canonical_file_registry.yaml` L2921-2933 `target_layer_validation` capability description 写死"合法值集合（**37个**）或废弃值集合（9个）" | 散文写死计数（违 §4 文档纪律），已漂（实际 45/9） | 不阻断，但 W3a 落地后 37→61 更正时**必须**留痕 | 与 total_values 自校同批修 description；该文件是热文件+golden hash 锚定件（见 3-9） |
| 1-9 | 历史留档不修：`architecture_issue_registry.yaml:18720`（"补 D_ML_SERVE（45 值）"=历史事件记录）、词表内 L322"（28 域）（11 域）"散文（施工包三-1 已列治本） | — | issue 记录属历史事实不改 | 仅词表注释按施工包改 |
| 1-10 | B 组迁移（FDR/TR 在用值改挂）触发面：`REGISTRY-MASS-DELETION`（判定目录 marker=`/_registry/catalogs/`，净删行或 YAML 条目数减少→硬阻断，逃生=`[allow-mass-deletion:reason≥10字]` commit 标记）；`module_translation_registry.yaml`+`capability_canonical_file_registry.yaml` 是 `DEFAULT_HOT_FILES` 成员（file_utils.py L312-324）→ 必用 `safe_write_text`（CAS），且 HOT-FILE-BASE-FRESHNESS gate 查 base 新鲜度 | 条目数单调性、净删行 | **高危** | 改挂=原地改值不减条目；确需减条目走裁定+标记；TR 若被整文件重排需 `[allow-mass-deletion:...]` |
| 1-11 | `GATE-DOMAIN-FK`（priority=78，domain_fk_gate.py）：staged .py added 行 `# [DOMAIN] D_XXX` 必须 ∈ functional_domain_registry.yaml 的 `- domain:` 条目（staged 版读，L106） | B 组若从 FDR 删/改 `D_GOV` 等条目，**后续任何**仍声明旧 [DOMAIN] 的新 .py / 改 [DOMAIN] 行的 .py 被拦 | 存量 [DOMAIN] 行不动不触发（diff-based） | FDR 改挂与依赖它的 .py 头部同 commit 原子（gate 读 staged YAML 正是为此设计） |

### 2.2 改动② validate_target_layer.py（total_values 自校 + 假红治本）

| # | 受影响件 | 判据 | 连坐判定 | 处置建议 |
|---|---------|------|---------|---------|
| 2-1 | 自身：无 gate/CI/hook 调用（实查 .pre-commit-config.yaml、.github/workflows 全目录、run_gate_chain 注册面均无此脚本；gate_registry.yaml 169 gate 无 target_layer 条目） | docstring L29"pre_commit/CI 手动运行"是**失真声明** | 改逻辑零门禁连坐 | 顺手把 docstring 改为"manual + 常驻差集脚本承接"；若想转正走 §3.3 注册链 |
| 2-2 | 派生清单三件：`scripts/governance/script_manifest.yaml`（generated_by=generate_script_manifest.py，源=各 .py 的 `__manifest__` 块）、`scripts/script-manifest.yaml`（generate_manifest.py 自动扫描）、`scripts_registry.yaml`（L1014-1017 条目）| GATE-21 `validate_static_manifest_drift.py --check`（**CI governance.yml L172 + deploy.yml L77 都跑**）=自动生成版 vs 磁盘版 diff | 只改实现体、不动 `__manifest__` 字段（args 增删=动 manifest！新加 `--exempt` 类参数会使 script_manifest 漂移）→ CI 红 | `__manifest__` 的 `args` 列表与实参同步后重跑 `python scripts/governance/generators/generate_script_manifest.py`（+ `scripts/generate_manifest.py`）再提交 |
| 2-3 | `module_translation_registry.yaml` L14077-14083 已有该模块条目（plain_zh 在） | TRANSLATION-COVERAGE 只管**新增** .py | 修改不触发 | 若函数语义大改可 `add_module_translation.py` 幂等更新 plain_zh（非必需） |
| 2-4 | `ALGO-FLOW-LINK` / `ALGO-NOTE-SYNC` / `GATE-ALGO-FLOW` | validate_target_layer.py **无 [ALGO_FLOW] 标记**（头部 14 字段实查 L1-16），GATE-ALGO-FLOW 只管 src/zephyr/** | 不触发 | 若新增核心函数（total_values 自校）考虑补 ALGO_FLOW，属可选项非门禁 |
| 2-5 | 脚本自身 [STARTUP] manual + [TTL] permanent：`check_vocab_hardcode.py` 检测5 对 `_load_*` 词表函数名 + [STARTUP] 值校验（startup_vocabulary）；`m11-perm-manual-legitimate` noqa 基线（存量无标记=不在 manual-only 扫描面，因 MANUAL-ONLY-PERMANENT 只查**新增**） | 修改不触发 | 保持 `# [STARTUP] manual` 值合法即可（manual ∈ startup_vocabulary，validate_target_layer 现行头部） |
| 2-6 | 13 条假红的 pytest 侧：**pytest 全绿不受影响**——test_knowledge_artifact_store.py 的 target_layer="L1/L2/L3" 是 KnowledgeArtifactStore 的入参，与校验器无耦合 | 校验器是 .py 文本扫描器，不是 pytest | 无测试变红 | 验收=校验器 exit 0 且 tests/knowledge 全绿双确认 |
| 2-7 | depgraph：改文件内容不触发 RENAME-DEPGRAPH-SYNC（未改名）；DEPGRAPH-FRESHNESS 类 gate 只查注册完整性 | — | 无 | 无 |

### 2.3 改动③ 新增常驻差集校验脚本（W3c）——新文件准入全链

| # | 门禁 | 判据（实读源码） | 硬/软 | 过关动作 |
|---|------|----------------|------|---------|
| 3-1 | `CREATE-GUARD`（priority=60，create_guard.py） | staged 新增 .py/.yaml/.md/.sh/.ps1/.mmd/.json 无 `creation_tokens` 登记 → 阻断（tests/ 豁免，真源 `commit_gate_registry.is_test_exempt`）；**新 .py 头部 30 行内 14 字段缺一不可**（BLUEPRINT/MODULE/DOMAIN/DEPENDENCIES/CONSUMERS/STARTUP/MATURITY/INVARIANTS/MODIFY-GUARD/STABILITY/SAFETY/AI_AUTONOMY/ERROR_CONTRACT/TESTS；`__init__.py` 最低 3；codegen 豁免）；basename 碰撞检测（CapabilityLookup） | 硬 | 见 §3.2 token 登记流程实查记录；头部直接抄 validate_target_layer.py L1-16 版式换值 |
| 3-2 | `TRANSLATION-COVERAGE`（priority=59，translation_coverage_gate.py，_OBSERVATION_PERIOD=False 已转正硬阻断） | scripts/ 下新增 .py 必须在 module_translation_registry.yaml 有 entry：plain_zh 非空 + **CJK≥8** + 非通用模板（is_generic 检测）；demos/、test_*.py、__init__.py、_archive/ 豁免 | 硬 | `python scripts/governance/d3_metadata/add_module_translation.py --path scripts/governance/d5_architecture/validators/check_vocab_domain_convergence.py --domain D_GOV_SCRIPTS --name-zh <中文名> --plain-zh "<大白话：做什么/解决什么/怎么做，CJK≥8，禁模板>"`（先 --dry-run） |
| 3-3 | `GATE-DOMAIN-FK`（priority=78） | 新 .py 的 `# [DOMAIN] D_XXX` ∈ functional_domain_registry.yaml（staged 版） | 硬 | 用已注册 `D_GOV_SCRIPTS`（validate_target_layer.py 同款）；若造新域必须 FDR 条目同 commit |
| 3-4 | `MANUAL-ONLY-PERMANENT`（priority=43）+ `PERM-TRIGGER`（priority=82） | [TTL] permanent + argparse/`__main__`+sys.argv 且无事件订阅 → 阻断；while True/sleep → 阻断 | 硬 | CLI 型常驻件在头部加 `# noqa: m11-perm-manual-legitimate  M11豁免: <≥10字理由>`（格式=marker+**双空格**+reason；先例 batch_creation_tokens.py L24、manual_only_permanent_gate.py 自身）；标记必须已在 `noqa_exempt_registry.yaml` 登记（它已登记，markers 段实查） |
| 3-5 | `NOQA-VALIDATION`（priority=71，noqa_validation_gate.py） | staged .py 的自定义 `# noqa: <marker>` 未在 `docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml` 预登记 → 阻断（ruff 标准码放行） | 硬 | 只用已登记 marker（m11-perm-manual-legitimate / gate-vocab / m01-vocab-hardcode / bare-subprocess …）；**若 W3b 给校验器发明新豁免标记，必须先登记该 marker 进此 YAML 再使用，同 commit** |
| 3-6 | `VOCAB-HARDCODE`+`VOCAB-CHAIN`（见 1-2/1-3） | 差集脚本天然要碰"词表值集合"与"SSoT 路径"——两个都是它的检测对象 | 硬 | 值=动态 load（`load_vocabulary_values`/`load_all_vocabulary_values`），路径=只写裸文件名或经 `_shared` 常量；差集输出里打印值不算字面量 |
| 3-7 | `NEW-FILE-DEPGRAPH-ENFORCEMENT`（priority=58）+ RULE-DEPGRAPH | 新增 .py 未入 depgraph 节点 → 阻断；宪法 §0.5 要求先 `apply_depgraph.py --add-design-node` 登记 | 硬 | 施工序第 2-3 步先登记设计节点，再建文件（apply_depgraph 走 DB 直写，RULE-SSOT 架构数据） |
| 3-8 | `GATE-ADM`（validate_manifest_admission.py，trigger=`^scripts/governance/script_manifest\.yaml$`）+ `GATE-21`（trigger 含 script_manifest + catalogs YAML）+ CI 两处 static-manifest drift 步 | 新脚本条目进 manifest 时做准入质量扫描；manifest 与磁盘 __manifest__ 必须零 diff | 硬（CI 兜底） | 新 .py 必含 `__manifest__` 块（照 validate_target_layer.py L36-45：args/dimensions/priority/timeout_seconds/warn_only/description 六键）后重跑 generate_script_manifest.py |
| 3-9 | 热文件三连：`capability_canonical_file_registry.yaml`（token 落点）与 `module_translation_registry.yaml`（plain_zh 落点）∈ `DEFAULT_HOT_FILES`（file_utils.py L312）→ `safe_write_text` CAS + `HOT-FILE-BASE-FRESHNESS` gate 查 base 新鲜度；capability registry 另受 GATE-INTEGRITY golden hash 锚定（validate_rules_integrity.py L124，critical；TAMPERED 信息性+post-commit 自动重基线）；`REGISTRY-YAML-PARSE`（priority=54）查 capability registry 结构（creation_tokens 键存在且为 list） | 硬 | **优先用官方写入通道**（scaffold.py / batch_creation_tokens.py / add_module_translation.py），它们内部已走 CAS 硬化插入，勿手改 |
| 3-10 | `GATE-SCRIPT-Q`（trigger=`^scripts/governance/.*\.py$`，validate_script_quality 八维度 --warn-only + fix_shared_bypass --ci）+ `GATE-REG-BL`（同 trigger，audit_registration --baseline-aware + validate_index_reality --ci）+ `SCRIPTS-IMPORT-INTEGRITY`（own_scope=true） | 脚本八维度质量（warn-only）；注册审计基线差分（validate_target_layer 条目已入基线，见 scripts_registry L1014）；import 完整性 | 半硬 | 新脚本 index/注册现实同步：生成器重跑后 `audit_registration.py --incremental --baseline-aware` 本地预跑 |
| 3-11 | 若想让差集校验**真常驻**：注册为 pre-commit hook（`.pre-commit-config.yaml` local repo 加 `- id: gate-vocab-domain-convergence` + `name: "GATE-VOCAB-CONVERGENCE: ..."` 块）→ `GATE-ID-UNIQ` 查 id 唯一 → `gate_registry.yaml` 由 `generate_gate_registry.py` 自动收录（三源合并：pre-commit + commit_gates/*.py + MANUAL_GATES；machine-generated，禁手改；total_gates 字段勿写死）→ `tests/governance/generators/test_generate_gate_registry.py::test_generate_total_gates_increased` 等断言随之演进 | — | 建议 W3c 先以 manual+reconciler 事件触发形态落（宪法 §9.3 永久系统四要素），**不**新增 hook/gate，规避 gate 总量净增的 §4.1 规范预算 |

### 2.4 改动③附带：docs/_working 挖矿文档自身（本文件即样本）

| 门禁 | 判据 | 处置 |
|------|------|------|
| CREATE-GUARD 阶段2 | 新增 `.md` 也需 creation_token（_OTHER_FORMAT_EXTENSIONS L147；docs/_working/*.md 有 690 条先例 token） | W8 落地时用 `batch_creation_tokens.py --prefix docs/_working/2026-09-18_vocab_consolidation_campaign --created-by <sid> --capability vocab_consolidation` 批量登记（含本目录全部 .md） |
| GATE-FRONTMATTER | staged .md 查 ttl/doc_type（--ci）| 本文件已带 `ttl: task_bound` frontmatter（先例 2026-09-15-szopen-pipeline-handoff.md） |
| GATE-DOC-NODE-ID | docs/*.md 禁 `node_id=\d+`/`edge_id=\d+` 物理 ID | 本文只引文件路径+行号，不引 DB 自增 ID，合规 |

---

## §3 实查记录（命令级）

### 3.1 tests/ 全库 grep 结果（必查 2）

| 关键词 | 命中 | 判定 |
|--------|------|------|
| `target_layer_vocabulary` | **0** | 无测试读词表文件 |
| `validate_target_layer` | **0**（全仓亦仅注册表/清单 10 文件命中，无 tests/） | 校验器**零测试覆盖**（自身 [TESTS] 字段为空）——W3b 改动无回归锚，建议 W3 顺手补 tests/governance/（tests/ 豁免 CREATE-GUARD/TRANSLATION-COVERAGE，成本仅 pytest 文件） |
| `total_values` | **0**（全仓 python 仅 `scripts/_archive/governance/d3_metadata/validate_enum_consistency.py:136`，归档件） | 无计数断言 |
| `target_layer`（宽） | tests/architecture/test_layer_isolation.py:143-157（局部变量=架构层，无关）；tests/contracts/test_ct_pipe_routing_root.py:58,109,205,214,255（D_INFRA_OPS/D_MKT_DATA/D_FACTOR/D_GOV_ENFORCEMENT——**全部是 values∪foundation_domains 现值，改后仍合法**）；tests/context/test_context_assembler_root.py:173、tests/pipeline/test_pipeline_orchestrator_root.py:82,87、tests/pipeline/test_ct_pipe_routing_pipeline.py:41,43（同前）；tests/knowledge/test_knowledge_artifact_store.py×13（L 值，见 §4）；tests/contracts/_meta/test_schema_stability.py:124（字段类型注解锚 `"target_layer": "str | None"`，改词表不影响） | **A 组/B 组改后预计 pytest 变红数 = 0**；唯一红线=谁把 `D_MKT_DATA/D_INFRA_OPS/D_GOV_ENFORCEMENT` 从 values 里删掉或改 is_foundation 才会炸 CT-PIPE 路由测试 |
| `D_GOV`（精确） | tests/dr/test_restore_from_backup.py:92,133,152（depgraph 假节点 domain_id 合成数据）、tests/governance/test_align_panoramas.py:560,561,570（PanoramaNode 合成）、tests/governance/test_panorama_common.py:76,79（weighted_domain_vote 合成） | 均为**合成输入非真源校验**——不读 FDR/词表，B 组别名收编不使其变红 |
| `D_GOVERNANCE` | 约 300+ 处，**几乎全是测试文件头 `# [DOMAIN] D_GOVERNANCE` 注释**（GATE-DOMAIN-FK 对 tests/ 豁免；FDR 不动此值） | 无关 |

### 3.2 creation_token 登记流程（供 W3c，实读 create_guard.py + scaffold.py + batch_creation_tokens.py）

- **真源**：`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` 顶层 `creation_tokens` 列表；条目格式（create_guard.py L103-109 docstring 原文）：
  ```yaml
  creation_tokens:
    - file: "scripts/governance/d5_architecture/validators/check_vocab_domain_convergence.py"
      token: "auto-<capability>-<YYYYMMDD>"     # scaffold 通道=auto-scaffold-<cap>-<日期>；batch 通道=<cap>-<stem>-<YYYYMMDD>
      created_by: "<session-id>"                 # 例 session-sess-26244-20260704153058 / st-vocabconsol-20260918
      capability: "target_layer_validation"      # 必须挂已有 capability（防第二真源——校验器本体 capability 即此，新脚本建议并入或新建 capability 条目）
  ```
- **通道 A（单文件）**：`python scripts/scaffold.py` 创建 .py 时自动 `_register_creation_token`（scaffold.py L423/L482→L1217-1283）：内部走 `batch_creation_tokens.py` 的 `insert_block/resolve_anchor` 硬化通道（creation_tokens 段内锚定纯插入 fail-closed + `safe_write_text` CAS + 写后 parse/落位双自检，失败回滚）。
- **通道 B（批量）**：`python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <dir> --created-by <sid> --capability <cap> [--dry-run]`。
- **插入位置警告**（registry_yaml_parse_gate.py L27/L99）：capability registry 里 **L883 附近有嵌套同名 `creation_tokens` 键**——手工/脚本插入锚点=顶层 creation_tokens 列表尾、`di_seam_exemptions:` 行之前；结构破坏（非 list/尾追悬挂）被 REGISTRY-YAML-PARSE fail-closed 拦。推荐永远走通道 A/B，不手插。
- 先例锚：validate_target_layer.py 的 token=`auto-validate-target-layer-20260704`、词表 YAML 本体也有 token=`auto-target-layer-vocabulary-20260704`（L7045-7052 实查）。
- 14 字段头版式：直接复制 validate_target_layer.py L1-16（含 `[A_module]` 与 `[TTL]`），改 MODULE/DOMAIN/BLUEPRINT 值；[CONSUMERS] 可留空（CONSUMERS-ACCURACY warn-only，且空字段无 orphan/phantom 可检出——**它不背模块/domain 清单**，只 AST 比对头部声明与文件内符号/文件系统路径，扫描面 `scripts/governance/`+`src/`）。

### 3.3 gate_registry / in_process_gate_registry 结构（必查 1 答案）

- `gate_registry.yaml`：**机生件**（generated_by=`scripts/governance/generators/generate_gate_registry.py`，maintenance: auto，source=`.pre-commit-config.yaml + commit_gates/*.py + MANUAL_GATES`，total_gates=169）→ **禁手改**；validate_target_layer **未登记为 validator/gate**（无条目）。
- `in_process_gate_registry.yaml`：in-process gate 注册真源；**新 gate 追加格式**（L21-23、entry_schema L32-39）：`- gate_id + module_path + factory_function + source: in_process + enabled: true`，追加后同步头部 `total_gates:` 数字（有 test_load_real_yaml_entries 双端一致断言兜底，2026-09-10 治本注记在 L40）。**W3 三件事不新增 gate，理论上不动此文件**——除非 3-11 转正。
- 与词表相关的 gate 登记面汇总：无一个 gate 直接"校验 target_layer 值"；值校验唯一真源=validate_target_layer.py（manual 态）。

---

## §4 validate_target_layer.py 的 13 条既有假红 + 豁免机制现状（必查 3）

- **13 条精确行号**（`target_layer\s*=\s*["']([^"']+)["']` 实扫，tests/knowledge/test_knowledge_artifact_store.py）：L52, 80, 89, 98, 107, 116, 125, 139, 152, 229, 235, 264, 279（值=L1×8 / L2×4…分布：L1@80-152 共 8 条，L2@52/235/264/279 共 4 条，L3@229 共 1 条=13）。L171 `target_layer=""` 因正则要求 ≥1 字符**不**命中。
- **语义确认**：`KnowledgeArtifactStore`（src/zephyr/knowledge/knowledge_artifact_store.py L83 `_INDEX_DIMS=("source","author","artifact_type","target_layer","created_at","effect")`）的 target_layer=**知识制品"目标层级"6 维索引之一**（L1-L6 制品加工层位），与 TaskCard.target_layer（域标识）是**两个独立命名空间的同名键**。旁证：`docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml` 的 `target_layer: "L1".."L6"`（L258/394/477/564/…，docs 目录不在扫描面）。该测试文件断言的是 store 的 schema 校验/版本链/6 维查询行为，与词表零耦合。
- **根因**：脚本 docstring L24 承诺的正则是 `target_layer\s*=\s*["'](D_[A-Z_]+|基础设施)["']`，实现 L79 却是通配 `([^"']+)`——实现背离声明，L 值全部落入"未知值→ERROR"。
- **豁免机制现状**：**无任何行级豁免/白名单/noqa 读取**；全文件控制阀只有 `--warn-only`（且只降 WARNING，ERROR 照 exit 1——L162-164）与 `.aidrafts/` 跳过（L104-105）。仓内现成豁免先例三套：① `# noqa: gate-vocab  <理由>` 行内豁免+基线棘轮（check_vocab_hardcode.py `_has_noqa_exempt` L415+，登记面=config/governance/noqa_exempt_registry.yaml）；② 全局自定义 noqa marker 体系（docs/…/catalogs/noqa_exempt_registry.yaml markers 段，NOQA-VALIDATION 硬执法）；③ `panorama_exempt_list.yaml` 式登记文件。**W3b 结论建议**：主路径=按 docstring 承诺收紧正则（L1/L2/L3 天然出局，13 红清零，无需发明豁免）；同时把"豁免标记"作为第二道留给 W5（收紧后若仍有非 D_ 前缀真违规面如 `target_layer="L4"` 出现在 src/tests 新代码，再启用 `# noqa: target-layer-exempt  <理由>` 类标记——**须先在 noqa_exempt_registry.yaml 登记 marker**，否则 NOQA-VALIDATION 反手阻断）。
- **同族误捕全仓 grep**（`target_layer\s*=\s*["']L`）：仅上述 13 处；`["']D_[A-Z_-]+["']` 赋值语境 src/tests 合计 9 处全为合法现值（§3.1）；`["']基础设施["']` 命中 0（deprecated 值当前无在用赋值点，validator 的 WARNING 通道现为空转）。
- **新增面自危提醒**：W3c 新脚本自身若含 `target_layer = "D_XXX"` 测试夹具或示例字符串，会被自己扫（scan_dirs=src/+tests/ 不含 scripts/——幸免；但**若未来 scan_dirs 扩到 scripts/ 则自捕获**，正则语境一并设计）。

## §5 CI/hook 链与 panorama/蓝图锚定件（必查 4+5）

- CI 实查：`.github/workflows/governance.yml` 跑的 d5 validators 仅 validate_ssot / validate_b_track_packages / validate_static_manifest_drift / validate_load_path_integrity；L119 validate_script_quality、L123 validate_manifest_admission、L314 validate_tool_contracts_consistency。**validate_target_layer 不在任何 workflow/hook/hooks 目录**（仓内无 hooks/ 目录，pre-commit 即 .pre-commit-config.yaml）。→ 修 validator 不破 CI；但 validator 的 manifest 元数据动了不破 static-manifest-drift 即可。
- panorama/alignment：`align_all.py` 及检查器无 target_layer 引用（grep 0）；对齐键=FDR/depgraph 的 domain_id 一致性与 module_id/step_id 锚，depgraph DB 的 domains CHECK 仅格式约束 `^D_[A-Z][A-Z0-9_]*$`（depgraph_schema.py L46/L414 + 历史能力 `ARCH_target_layer_check`）→ **16 新值全为合规格式，DB CHECK 不收；词表版本/域数量无锚定义务**。
- docs/03_modules 锚定件（需同步的散文/生成物）：
  1. `docs/03_modules/_cross_layer/pipeline/blueprint.md:819` 条件散文仍写废弃值 `target_layer ∈ {D_DATA,基础设施,D_COMPLIANCE}`——**过时锚**（对照 `_master_blueprint/blueprint_baseline.md:638` 已正确写 {D_MKT_DATA,D_INFRA_OPS,D_GOV_ENFORCEMENT}）。无机器 gate 检此串，但属 §4.3 文档纪律违规，建议随 W3a 批修。
  2. `docs/03_modules/_domain_shared/algo_flow/blueprint_tools/blueprint_decomposer.yaml:28` 生成注释"映射表（13 域）"—— decomposer map 若未来扩值需重跑生成器；W3 不动 map 则不连坐。
  3. `path_ownership_map.yaml:11335` 含 validate_target_layer.py 路径——机生件（generate_path_ownership_map.py），W3c 新文件后重跑生成器即可。

## §6 遗留不确定（W2 封矿前复核）

1. `audit_registration.py --baseline-aware` 的基线文件位置与是否需要为 W3c 新脚本显式 `--update-baseline`（实查未展开，GATE-REG-BL 触发即知）。
2. GATE-VOCAB `check_vocab_hardcode.py --ci` 对 16 新值的实际误报集（需改后实跑，静态推演=blueprint_decomposer dict 与任何 ≥2 新值组合的存量字面量集；单值赋语境按盲区5 全子集规则不报）。
3. C 组裁定若要求 `D_DATA_GOV` 入 FDR（而非仅词表），GATE-DOMAIN-FK/`domain_naming_rules.yaml`（catalogs 在位）的域命名合法性未逐一核。
