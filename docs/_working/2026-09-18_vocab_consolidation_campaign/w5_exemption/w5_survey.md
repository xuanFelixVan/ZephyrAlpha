---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---

# W5 全仓普查：`validate_target_layer` 型假红同族（治本前置调研）

> 战役：`st-vocabconsol-20260918` ｜ 环节：W5 ｜ 性质：**只读调研 + 本产出文档**
> 工位边界：本环节**未改动任何文件**（含未登记 noqa 标记、未改校验器、未清洗 registry）。
> 主路径治本（收紧 `_TARGET_LAYER_RE`）归 W3 工位，本文只供数与定性。
> 上游输入：`00_workorder_施工包.md`「校验器基线」段、`w1_mining/w1c_gates.md §4`、裁定#335（`ruling_registry.yaml:4294`）。

---

## 0. 结论速览

| 问 | 答 |
|---|---|
| 同族命中点总数 | **141 处 / 12 组**（族① 51 · 族② 2 · 族③ 88） |
| 三类占比 | ① `target_layer` 赋值撞名 **36.2%** ｜ ② 校验器宽正则 **1.4%** ｜ ③ 兄弟字段撞名 **62.4%** |
| 实际产红（ERROR）点 | **13 处，全部**在 `tests/knowledge/test_knowledge_artifact_store.py`，与 W1c 既有记账完全一致，**零新增盲区** |
| 真违规（该值确实非法、应随 W3 变红） | **0 处** |
| 收紧正则后差分 | 消失红 **13** ｜ 新增红 **0** ｜ 残余红 **0**（23→10 命中，ERROR 13→0，WARNING 0→0） |
| **给 W3 的关键增量** | 照 docstring 字面收紧成 `(D_[A-Z_]+\|基础设施)` 会**连带脱落 4 个连字符废弃值**（`D-DATA`/`D-SIGNAL`/`D-FACTOR`/`D-RESEARCH`）的 WARNING 检测；实测建议式 **`(D[-_][A-Z_]+\|基础设施)` + `\b` 词首锚定**——同样 10 命中 / 0 ERROR / 0 WARNING，且保住连字符族防再发（详见 §5 末表） |
| 是否需要 `# noqa: target-layer-exempt` | **不需要**（4 条独立否决判据，任一条即成立；见 §6） |
| 附带发现（超出 W5 授权，移交） | 5 条：扩面雷点 / `.bak` 挂真源目录 / `index.md` 计数漂移 / 校验器零门禁挂载 / 6 套 "L 值" 命名空间并存的语义债（见 §7） |

---

## 1. 根因复述与实证基线

### 1.1 承诺 vs 实现的背离（定性=校验器缺陷，非词表缺口）

`scripts/governance/d5_architecture/validators/validate_target_layer.py`：

| 位置 | 内容 |
|---|---|
| `:24`（docstring 承诺） | `正则匹配 target_layer\s*=\s*["'](D_[A-Z_]+\|基础设施)["'] 模式` |
| `:78`（注释复述承诺） | `匹配 target_layer="D_XXX" 或 target_layer='D_XXX' 或 target_layer="基础设施"` |
| `:79`（**实现**） | `re.compile(r'target_layer\s*=\s*["\']([^"\']+)["\']')` |

实现把值域从 `(D_[A-Z_]+\|基础设施)` 放宽成 `([^"\']+)`——**任何**非空字符串都进判定，随后 `:127-136` 落入 `else` 分支报 `ERROR: 未知值`。因此本假红族的充要触发条件是"字段名恰为 `target_layer` + 值为任意非 D_ 字面量"，与被赋值的**语义**无关。

### 1.2 实测基线（本工位执行，只读）

```
$ python scripts/governance/d5_architecture/validators/validate_target_layer.py
✗ 13 个未知 target_layer 值！        # exit=1（EXIT_FINDINGS）
```

13 条 ERROR 精确行号：`tests/knowledge/test_knowledge_artifact_store.py` L52, 80, 89, 98, 107, 116, 125, 139, 152, 229, 235, 264, 279
值分布：`L1`×8（L80-152）／`L2`×4（L52,235,264,279）／`L3`×1（L229）= 13。**与 `w1c_gates.md §4` 逐行核对一致，无遗漏、无多余。**

### 1.3 该族字段为何是合法异语义（豁免论证的事实底座）

同一标识符 `target_layer` 在本仓承载 **6 套互不相干的值空间**，其中被校验器误用为唯一真源的只有第 1 套：

| # | 命名空间 | 值空间 | 真源 | 是否在扫描面 |
|---|---|---|---|---|
| 1 | `TaskCard.target_layer`（CT-PIPE 目标功能域） | `D_[A-Z_]+` 45 值 + 9 废弃值 | `target_layer_vocabulary.yaml v1.0.0` | 是（校验器唯一服务对象） |
| 2 | 知识制品"目标层级"（6 维索引之一） | 自由文本，实测 L1–L3 | `knowledge_artifact_store.py:83` `_INDEX_DIMS` + `:95` `target_layer: str` | 是 → **13 红源** |
| 3 | 决策图归属层 | L1–L6 | `candidate_module_registry.yaml` `decisiongraph.target_layer`；`query_candidate_registry.py:103` 打印为"决策层" | 否 |
| 4 | depgraph 运行时栈层 | L0_infrastructure/L1_foundation/L2_domain/L3_application | `depgraph_schema.py:431,1147,1154`（字段名 `layer_id`，带 CHECK） | 否（字段名不同） |
| 5 | 决策节点层 | L5…；另有 E4 系（`test_strategy_production_map_adversarial.py:72`） | `decisiongraph_schema.py:176,206`（`layer_id` PK） | 否（字段名不同） |
| 6 | RBAC / 审计 / 门禁防线层 | L0_immutable_core / L1_rbac / L0–L4 / L00–L13 / L1_Sweep… | 各自类定义（`layer=` kwarg） | 否（字段名不同） |

第 2 套与第 3 套**同名 `target_layer` 但都 ≠ 第 1 套**——这是"异语义字段撞名"，不是"值填错"。
第 6/7 类（4/5/6 套）字段名不同，故当前零红；但它们是 §6 判定"不得加宽正则"的量化依据。

---

## 2. 普查方法与扫描面

- **目录面**：`src/ tests/ scripts/ schemas/ docs/`；**排除**：`.aidrafts/`、`.runtime/`、`_archive/`、`__pycache__/`、`docs/_working/`（战役自述文档单列为"文档示例"族）、`.worktrees/`（17 个会话工作树副本，未排除会使所有计数 ×17；校验器扫描面 `scan_dirs=[REPO_ROOT/"src", REPO_ROOT/"tests"]` 天然不含 `.worktrees/`，已核实）。
- **判定面**：以校验器真实扫描面（`src/`+`tests/` 的 `*.py`）为准出"红/绿"结论；`scripts/`、`schemas/`、`docs/` 命中单独分类，不参与红绿账。
- **实证方式**：除静态 grep 外，用一次性内联脚本（不落盘）在真实词表下做**双正则差分**，把 §5 的数字做成实测而非推断。
- **命令留痕**（可复跑）：
  ```bash
  grep -rnE "target_layer[\"']?[[:space:]]*=[[:space:]]*[\"'][^\"']*[\"']" src tests scripts
  grep -rlE "(^|[^_a-zA-Z])layer[[:space:]]*=[[:space:]]*[\"'](L[0-9][^\"']*)[\"']" src tests
  grep -rn "target_layer" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml   # 0 命中
  ```

---

## 3. 命中台账（12 组 / 141 处）

### 族① `target_layer` 赋值/关键字参数值为 L0/L1/L2/L3 或非 D_ 值 —— 51 处（36.2%）

| # | 位置 | 处数 | 值 | 分类 |
|---|---|---|---|---|
| 1-A | `tests/knowledge/test_knowledge_artifact_store.py` L52,80,89,98,107,116,125,139,152,229,235,264,279 | 13 | L1×8 / L2×4 / L3×1 | **同族假红（已产红）** |
| 1-B | 同文件 L171 `_put(store, target_layer="")` | 1 | `""` | 同族假红（**未**产红：`[^"\']+` 要求 ≥1 字符） |
| 1-C | `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml` `decisiongraph.target_layer`（L258,394,477,564,649,797,882,966,1283,1368,1447,1525,1604,1684,1774,1862,6690） | 17 | L1×5 L2×3 L3×1 L4×1 L5×1 L6×6 | 文档示例/登记数据（异语义=决策层；`docs/` 不在扫描面） |
| 1-D | 同目录 `candidate_module_registry.yaml.bak_pre_one_question` 同字段 | 16 | 同上（少 L1283 一处） | 文档示例 + **卫生缺陷**（`.bak` 悬挂于 catalogs/ 真源目录 → 任何目录级 YAML 扫描双计） |
| 1-E | `scripts/governance/d5_architecture/validators/validate_target_layer.py:78` 注释内 3 个占位字面量（`"D_XXX"`×2、`'D_XXX'`×1、`"基础设施"`×1） | 1 行（3 命中） | D_XXX / 基础设施 | 文档示例（注释）+ **扩面雷点**，见 §7-1 |
| 1-F | `docs/_working/…/w1a_consumers.md:30,47,229`（`target_layer="X"`、`"L1/L2/L3"` 自述） | 3 | X / L1L2L3 | 文档示例（`*.md` 永不入扫描面） |

**族①阴性结论（同为必答项）**：`schemas/` 目录 `target_layer` **0 命中**（无 JSON Schema enum 约束该字段）；`src/` 生产代码 `target_layer="<字面量>"` **0 命中**（生产侧只透传变量：`context_assembler.py:485`、`task_manager_server.py:239`、`ct_pipe_routing.py:156`）；`blueprint_decomposer.py:186-199` `_FUNC_DOMAIN_TO_TARGET_LAYER` 13 个映射值 100% 命中现存合法 values（逐值核过：D_MKT_DATA/D_FACTOR/D_SIGLEGACY/D_RISK/D_BACKTEST/D_GOV_ENFORCEMENT/D_GOVERNANCE/D_OPS/D_INTELLIGENCE/D_EX_CORE/D_INFRA_OPS/D_INFRA_RUNTIME/D_AUTONOMY_PERM）→ 零真违规。

### 族② 其他校验器是否同带宽正则 —— 2 处（1.4%）

| # | 位置 | 分类 |
|---|---|---|
| 2-A | `validate_target_layer.py:79` `_TARGET_LAYER_RE` | **校验器本体缺陷（全仓唯一）** |
| 2-B | `scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py:100` `_DEPRECATED_LAYER_RE = re.compile(r"^L\d{2}$")` | **无问题**（对照范式，见下） |

排查覆盖面与结论：

- 全 `scripts/` 目录 `re.compile(.*[Ll]ayer.*)` **仅 1 处命中** = 2-A 自身；`re.search|findall|match(.*layer.*)` **0 处**。→ **宽正则同族缺陷在全仓治理脚本中唯一存在，无第二处需治本。**
- 含 `target_layer` 字样的其余 7 个治理脚本逐一定性，全部非判定逻辑：
  `apply_depgraph.py`（3211/3452/3516/3584/5333… 全部为"裁定#ARCH-target_layer_v1.0.0"注释文本）、
  `d3_metadata/validate_module_id_naming.py:170`（命名约定注释）、
  `d5_architecture/analyzers/analyze_contract_impact.py:85,109,132`（读 `cross_layer_contracts.yaml` 的 **复数**字段 `target_layers`，与本字段无关）、
  `d5_architecture/detect_causal_conflicts.py:212`（输出 dict 键 `"target_layer": dep_layer`，值为运行时变量、非字面量）、
  `d5_architecture/detect_constraint_violations.py:98`（`# noqa: gate-vocab` 注释自述"非 target_layer 词表全集校验"）、
  `d8_doc_sync/sync_yaml_to_depgraph.py:124`（`"compliance": "D_GOV_ENFORCEMENT"` 映射，合法值）、
  `query_candidate_registry.py:103`（读族①-C 的决策层语义，**用法正确**）。
- 兄弟 layer 校验器不共用该缺陷：`validate_rule_frontmatter.py:105`、`validate_ssot.py:181`、`generate_module_algorithm_overview.py:144` 均经 `load_vocabulary_values("layer_vocabulary.yaml")` **动态加载 + 结构化取值**（YAML/frontmatter 解析，不拿正则扫源码），GATE-VOCAB `check_vocab_hardcode.py` 走 **AST 变量名/字面量集合**判定且面为 `src/+scripts/`（不含 `tests/`）→ 均不会捕到 13 假红，也不含宽文本正则。
- **2-B 恰是收紧后应有的写法范式**：字段值来自 `yaml`/frontmatter 结构化解析（`fm.get("layer")`）而非源码文本正则；模式 `^L\d{2}$` 两端锚定且只认两位数字，故 `L1/L2/L3` 单数字**不**命中。

### 族③ `responsibility_layer` / `layer_id` 与 `target_layer` 在测试断言中混用 —— 88 处（62.4%）

| # | 位置 | 处数 | 分类 |
|---|---|---|---|
| 3-A | **严格意义"同一测试文件内 `layer_id`/`responsibility_layer` 与 `target_layer` 混用"** | **0** | 无——已逐文件交叉核验（对 `grep -rl "layer_id\|responsibility_layer" tests` 的每个文件再 `grep -q target_layer`，命中集为空） |
| 3-B | `tests/architecture/test_layer_isolation.py:143,144,147,157` 局部变量 `target_layer = _layer_of_file(...)`（语义=架构层） | 4 | 同族撞名（未产红：赋值右端无引号字面量） |
| 3-C | 扫描面内 `layer="L<digit>…"` 异语义 kwarg，14 文件：`src/.../permission_guard.py:10`、`rbac_guard.py:15`、`orphan_judge/{judge:1,reference_graph_engine:1,registration_checker:1,standalone_evaluator:4,unique_analyzer:5}.py`、`code_dedup/false_negative_auditor.py:3`；`tests/agent_rbac/{exceptions_agent_rbac:1,permission_guard:1,rbac_core:4}`、`tests/audit/audit_core/test_audit_orphan_judge_e2e.py:6`、`tests/gate/test_gate_context.py:3`、`tests/governance/scripts_governance/test_validate_ssot_unit.py:6` | 61 | **同族潜在误捕**（字段名不同故当前零红；一旦有人"顺手"把正则加宽到 `layer=` 即全红——实测模拟 156 命中、ERROR 156，见 §6-判据4） |
| 3-D | `layer_id` 值空间与 CHECK/断言点：`depgraph_schema.py:431,1147,1154`（4 值 CHECK + 双触发器）、`decisiongraph_schema.py:176,206`（PK/FK）、`tests/backtest/test_backtest_decisiongraph_adapter.py:92,94,151`（`assert node["layer_id"]=="L5"`）、`tests/backtest/test_strategy_production_map_adversarial.py:72`（`layer_id != "E4"`——**第三套值空间 E4 与 L 系并存**）、`tests/audit/test_incremental_scanner.py:106`（注释：DB 真值 `L0_infrastructure` ≠ `l01-infrastructure`）、`src/.../dependency.py:245`（`Infer layer_id … aligned with layer_vocabulary.yaml v2.0.0`） | 11 | 异语义字段（运行时栈/决策图坐标轴），与 `target_layer` **零交叉**；混用风险=命名而非值 |
| 3-E | `responsibility_layer`：`src/tests/scripts/schemas` **代码 0 命中**；文档 12 处（`ruling_registry.yaml:4294,4311,4313`；`00_skeleton.md:19,36,52,53`；`w1d_layers.md:218,256`；`w2_self_ruling_335.md:37,38,57`） | 12 | 文档示例（W4 待建字段，裁定#335 结论 5 已定名并明令"生成器不得从 `layer_id` 直推"） |

**族③ 定性结论**：不存在"`target_layer` 与兄弟字段在同一断言里混用"的既成事实（3-A=0）；风险全部以**"字段名撞名 + 值空间重叠"**形态存在（3-B/3-C/3-D 合计 76 处）。这决定了处置方向是"**保住字段名精确匹配 + 值域锚定**"，而不是"发明逐行豁免"。

---

## 4. 三分类裁定汇总

| 分类 | 处数 | 明细 |
|---|---|---|
| **真违规**（该值确实非法，应随 W3 变红） | **0** | 扫描面内 10 个 D_ 字面量全为现存合法值；`基础设施`/`D_DATA`/`D_COMPLIANCE` 等 9 个废弃值在 `src/`+`tests/` 的**赋值语境命中 0** → 校验器 WARNING 通道当前空转 |
| **同族假红（异语义字段撞名）** | **90** | 已产红 13（1-A）+ 未产红 1（1-B，`target_layer=""`）+ 撞名局部变量 4（3-B）+ 潜在 `layer="L*"` 61（3-C）+ 异语义 `layer_id` 值空间 11（3-D）；前四项为直接同族，末项为"字段名撞名+值空间重叠"形态的命名债 |
| **文档示例 / 登记数据**（不影响运行） | **49** | 1-C registry 决策层 17 + 1-D `.bak` 副本 16 + 1-E 校验器注释占位符 1 + 1-F 战役自述 md 3 + 3-E `responsibility_layer` 文档提及 12 |
| **校验器本体缺陷 / 对照范式** | **2** | 2-A（缺陷，W3 治本对象）+ 2-B（无问题，作收紧模板） |
| **合计（按"每处取主类"）** | **141** | = 族① 51 + 族② 2 + 族③ 88，与 §3 台账逐项可加和核对 |

> 另计**排查覆盖面但未入 141 台账**（因非赋值语境、纯文本提及）：族② 排查中 7 个治理脚本的注释/复数字段命中（`apply_depgraph.py` 等，见 §3 族② 排查清单）、`docs/01_policies_and_standards` 内 6 处词表指针文本（`architecture_issue_registry.yaml:18720,18724`、`functional_domain_registry.yaml:8`、`rule_catalog_registry.yaml:4227,4229`、`vocabularies/index.md:58`）。

---

## 5. 收紧正则后的红/绿差分（Q3 主答）

实测方式：同一词表（45 values / 9 deprecated）、同一扫描面（`src/`+`tests/` 的 `*.py`，跳 `.aidrafts/`）下跑双正则，取集合差。

| 指标 | 现状（宽 `[^"\']+`） | 收紧后（`D_[A-Z_]+\|基础设施`） | 差分 |
|---|---|---|---|
| 命中总数 | 23 | 10 | −13 |
| **ERROR（红）** | **13** | **0** | **消失 13 ／ 新增 0** |
| WARNING（废弃值） | 0 | 0 | 0 |
| 合法放行 | 10 | 10 | 0 |

- **消失红 = 13**：即 `tests/knowledge/test_knowledge_artifact_store.py` 的全部 13 条（L1×8/L2×4/L3×1）。它们被 `(D_[A-Z_]+|基础设施)` 值域排除在匹配之外，匹配阶段即不成立，故不进判定分支。
- **新增红 = 0（除 tests/knowledge 外无任何新增）**：收紧是**纯收缩**（匹配集单调变小），逻辑上不可能产生新命中；实测差集 `tightened - current = ∅` 亦证实。
- **额外验证**：加 `\b` 词首锚定的变体（`\btarget_layer\s*=`）与不加**结果完全等价**（同为 10 命中 / 0 红）→ 现仓不存在 `*_target_layer="…"` 复合标识符撞车；加 `\b` 是零成本的向前保险，建议 W3 采纳。
- **W3 词表收编（17 值入 values、8 值别名过渡）对本差分的叠加影响 = 0**：扫描面现存 10 个 D_ 字面量（`D_INFRA_OPS`×5、`D_MKT_DATA`×2、`D_FACTOR`×2、`D_GOV_ENFORCEMENT`×1）全部属于**收编前的现存 values**；收编只增合法集、不删现值，故不会把任何绿翻成红。唯一红线（与 W1c §3.1 一致）：若 W3 误删或改 `is_foundation` 掉 `D_MKT_DATA/D_INFRA_OPS/D_GOV_ENFORCEMENT`，会同时炸 CT-PIPE 路由测试与本校验器——`tests/contracts/test_ct_pipe_routing_root.py:58,109,205,214,255`、`tests/pipeline/test_ct_pipe_routing_pipeline.py:41,43`、`tests/pipeline/test_pipeline_orchestrator_root.py:82,87`、`tests/context/test_context_assembler_root.py:173`。
- **验收口径可达成性判定**：W1a R7 提出的"改完 0 ERROR 口径不可达"在收紧后**自动解除**（残余红 0），无需任何豁免即可让 W6 基线命令 `validate_target_layer.py` 走到 exit 0；`tests/knowledge` 侧 pytest 全绿不受影响（该 13 处是 `KnowledgeArtifactStore` 入参，校验器是纯文本扫描器，两者零耦合）。

**残余同族误捕清单（收紧后仍存在但当前零红，需知情不需豁免）**：

| 项 | 触发条件 | 现状 |
|---|---|---|
| 1-E 校验器自身注释里的 `"D_XXX"`×2、`"基础设施"`×1 | 扫描面扩到 `scripts/` | `scripts/` 不在 `scan_dirs` → 0 红；**收紧后扩面即产 2 ERROR + 1 WARNING**（校验器逐行扫、不跳注释/docstring，`:111-113`） |
| 1-C/1-D registry 的 17+16 个 `decisiongraph.target_layer: "L1".."L6"` | 有人把校验面从 `*.py` 扩到 catalogs YAML，或把该字段改名 | 0 红；异语义正确用法 |
| 3-C 的 61 个 `layer="L*"` | 正则字段名从 `target_layer` 放宽到 `layer` | 0 红；放宽即 156 命中全红 |
| **收紧式自身的覆盖度回退（实测）** | W3 若照 docstring 字面实现 `(D_[A-Z_]+\|基础设施)` | 9 个 deprecated 值中 **4 个连字符值 `D-DATA`/`D-SIGNAL`/`D-FACTOR`/`D-RESEARCH` 从 WARNING 通道静默脱落**（实测：`D_` 式对 `D-DATA` 不匹配；其余 5 值 `D_DATA`/`D_COMPLIANCE`/`D_PORTFOLIO_CORE`/`D_EXECUTION_CORE`/`基础设施` 仍匹配）。这 4 值恰是历史 bug 源 `inject_domain_fields.py` 的产物、正是本校验器该盯的对象。**当前扫描面 0 命中 → 无现行红/绿变化**，属前瞻性漏检。建议 W3 用 `(D[-_][A-Z_]+\|基础设施)`：连字符族照旧落 WARNING，且 `L1/L2/L3` 仍不匹配（实测本表 13 红差分不变） |

---

## 6. 是否需要发明 `# noqa: target-layer-exempt`

**判定：不需要（现状零豁免需求）。**

若未来判定为"需要"，前置义务是硬性的：新标记 **MUST** 先在
`docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml` 的 `markers:` 段登记
（现登记 28 个标记，无任何 target-layer 类），命名遵循该文件头 `标记命名规范：<metric_id_lower>-<语义>`，
且逐行使用必须附 ≥10 字符理由（`reason_required: true` / `reason_format`），由
`src/zephyr/gov_enforcement/commit_gates/noqa_validation_gate.py`（`GateSpec(gate_id="NOQA-VALIDATION", priority=71)`）
在提交时硬阻断；该 registry 自身 `ai_autonomy: human_gated`。
——**注意：登记只是"允许写这个标记"，不等于"红会变绿"，见判据 1。**

四条独立否决判据（任一条成立即"不需要"）：

1. **无消费端，标记是装饰品**。`validate_target_layer.py` 全文只认 `--warn-only` 与 `.aidrafts/` 路径跳过（`:105-106`、`:143`），**没有任何 noqa 解析**。在 `tests/knowledge` 挂 13 个 `# noqa: target-layer-exempt` 后，校验器输出**逐字节不变**，13 红一条不少。要让它生效必须先给校验器加 noqa 消费逻辑 = 在"消除缺陷"之外再"新增机制"，违反 §4.1 规范净零增长。
2. **密度墙结构性不可用**。`noqa_validation_gate._NOQA_DENSITY_THRESHOLD = 10`（`:84`，`_check_noqa_density` `:180-210`）：单文件**已登记**标记数 >10 即判"疑似滥用豁免机制，请重构代码而非大量标注 noqa"。13 处假红全在**同一个文件**，逐行豁免 = 13 > 10 → **该方案自身必然触发门禁违规**。
3. **对象不存在**。收紧后扫描面残余红 = **0**（§5 实测）→ 无任何待豁免客体；扫描面外的 33 处（族①-C/D）本就不产红，豁免无意义。发明豁免 = 为一个不存在的红预留规则条目。
4. **成本方向倒置**。"改一个正则字符类"（W3 已排期、零新增概念）vs "新增一个跨三处（registry 登记 + 校验器解析器 + 13 行标记与理由）的豁免面"。且同族撞名的真正解药是**保住字段名精确匹配**——一旦引入豁免，就会诱导后人用"打标记"替代"改字段名/收紧值域"，把 §3 已量化的 76 处命名债固化成豁免债。

**触发"需要"重新评估的条件（写死，便于 W7/后续战役机判）**：
(a) W3 把 `scan_dirs` 扩到 `scripts/`（届时 1-E 会产 2 ERROR+1 WARNING，但**首选治本是把校验器自己的注释占位符改掉或加注释跳过，仍非豁免**）；
(b) 出现"异语义但字段名恰为 `target_layer` 且值必须为 D_ 前缀"的字面量进入 `src/`+`tests/`（现无）；
(c) 收紧正则被证明会漏掉真实非法值（即需要"保留宽匹配 + 定点豁免"）。
三条任一成立，才登记形如 `target-layer-sem` 的标记，并**同步**在校验器实现该标记的消费端。

---

## 7. 附带发现与移交建议（均不属 W5 授权，未动）

1. **[移交 W3] 收紧式选型 + 扩面雷点（两条一并做）**：①值域建议写成 `(D[-_][A-Z_]+|基础设施)` 并加 `\b` 词首锚定（实测 10 命中 / 0 红，且不丢连字符废弃值），同时把 `:24` docstring 的承诺改成与实现**逐字符一致**——本次事故的本质就是"承诺与实现分叉"，只改实现对齐承诺仍是下一次漂移的温床；②校验器逐行匹配、不跳注释/docstring（`:111`），自身 `:78` 注释含 `D_XXX`/`基础设施` 字面量，建议把该注释示例改成不会命中的写法（如 `target_layer=<D_XXX>`）或在 `scan_files` 跳过 `line.lstrip().startswith("#")`。**②做完后族①-E 永久归零，扩面也不再产红。**
2. **[移交 Owner/卫生] `.bak` 挂真源目录**：`docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml.bak_pre_one_question` 与主文件并存，使 catalogs 目录级扫描对 `decisiongraph.target_layer` 双计（17→33）。建议移出 catalogs/ 或删除。
3. **[移交 W3] 计数漂移**：`docs/01_policies_and_standards/_registry/vocabularies/index.md:58` 写死"44 值"，而词表实测 `len(values)=45` 且自述 `total_values: 45`。W3 收编 17 值后必再漂移。按宪法 §4.3"计数用字段不写死在散文"，`index.md` 该格应改为引用 `total_values` 字段（或走生成器）。
4. **[记账澄清] 该 13 红不阻断任何提交**：`validate_target_layer.py` **未接入任何 pre-commit 门禁**（`gate_registry.yaml` grep `target_layer` = 0 命中；该目录另有 6 个 validator 已挂载，它不在列），只登记在 `script_manifest.yaml:2940`（D5 / P1 / manual）。→ W1c 担心的"13 红连坐提交"不成立；它唯一的杀伤是**战役 W6"基线命令 exit 0"验收口径**，收紧后自动解除。
5. **[语义债，交 W4] 6 套 "L 值" 命名空间并存**（§1.3 表）：W4 新增第 7 套 `responsibility_layer`（governance/business/ai/infrastructure）。裁定#335 结论 5 已禁止从 `layer_id` 直推，方向正确；建议 W4 顺手在 `target_layer_vocabulary.yaml` 头部 SSoT 链路注释里补一行"**本词表只管 `target_layer` 的域值空间；`layer_id`/`responsibility_layer`/知识制品层位/决策层各有独立真源，禁互相覆写**"，把本次普查得到的边界固化成真源自述（净增 1 行注释，零新机制）。

---

## 8. 本工位边界声明

- 只读执行面：`grep` / `Read` / 校验器 CLI 运行（`validate_target_layer.py` 仅 `print` 到 stderr + `sys.exit`，无写盘；词表与 registry 均为读）+ 一次性内联 Python 差分（stdin heredoc，不落盘）。
- 产出物：**仅本文件** + 其所在目录 `w5_exemption/`。
- 未做（越权项，逐条列明以免被误判为遗漏）：未改 `_TARGET_LAYER_RE`（=W3）、未登记任何 `noqa` 标记或新 marker 到 `noqa_exempt_registry.yaml`（判定为不需要，§6）、未清洗 `tests/knowledge` 的 13 处字面量、未改名 `KnowledgeArtifactStore.target_layer`、未删 `.bak` 文件、未改 `index.md` 计数。
