---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---
# W1a — target_layer 词表消费方挖矿（只读调研）

> 战役：target_layer 词表收编（+16 值 / 9 值折叠为别名）
> 对象真源：`docs/01_policies_and_standards/_registry/vocabularies/target_layer_vocabulary.yaml`
> 方法：Grep/Read + 只读脚本（AST 模拟 / PG `depgraph_reader` / SQLite `mode=ro`），未修改任何仓库文件
> 时间：2026-09-18

---

## 0. 一页结论

| 指标 | 数值 | 证据 |
|---|---|---|
| 词表当前规模 | 45 合法值 + 9 废弃值 + 3 foundation_domains；`vocabulary_name: target_layer`(L56) / `total_values: 45`(L57) | `target_layer_vocabulary.yaml:56,57,72,79,281` |
| 别名现状 | 仅 2 个值带 `aliases`：`D_PF_CORE=[D_PORTFOLIO_CORE]`、`D_EX_CORE=[D_EXECUTION_CORE]` | `target_layer_vocabulary.yaml` values 段 |
| **真读词表内容的消费方** | **4** | §1 A 组 |
| **glob 批量读到本词表的消费方** | **4**（含 1 个死代码） | §1 B 组 |
| **注释/文档串"假读"消费方** | **3**（只提文件名，不读内容） | §1 C 组 |
| **测试链消费方** | **1**（当前豁免本词表） | §1 D 组 |
| **消费方合计** | **12**（+ 5 个"域命名空间权威"共 17 个受影响点） | §1 全表 |
| 代码 `[DOMAIN]` 标注总量 | 5460 条 / 71 个不同值（src+tests+scripts+config+schemas+architecture_model+acceptance+meta） | §4 复算命令 |
| 标注值中不在 45 合法值 | **25 个**（= 16 待新增 + 9 待折叠，正好对齐战役口径） | §4.1 |
| PG depgraph `domains` 表 | 75 行；`nodes` 11923 行 | §5 |
| GATE-VOCAB 因 +16 新增的命中 | **+1 处**（实测，非估算） | §6 R4 |
| `validate_target_layer.py` 现有基线 | **13 个 ERROR**（全是 `target_layer="L1/L2/L3"` 同族假红，与本次改动无关） | §6 R7 |

**一句话风险定位**：真正约束代码里 `D_*` 取值的是 **`functional_domain_registry.yaml` + GATE-DOMAIN-FK（仅 staged `.py`）**，
本词表在生产链路上**没有任何"逐值"硬拦截**（唯一逐值校验器 `validate_target_layer.py` 不在 169 条 gate 里）。
但注意一个反向陷阱：词表文件路径本身落在 **GATE-VOCAB 的 `files_trigger`**（`gate_registry.yaml:175` / `.pre-commit-config.yaml:364-366`），
所以**这次提交一定会跑门禁**——风险形态不是"暗处被炸"，而是①自家提交被 +1 新命中卡住（R4），②其余消费方静默漂移、改完无人报警。

---

## 1. 消费方清单表

### A 组：真正读取词表内容（4 个）

| # | 消费方 | 读取段 | 读取方式 | 缓存时机 | 消费语义 | 证据（file:line） |
|---|---|---|---|---|---|---|
| 1 | `src/zephyr/infrastructure/pipeline/ct_pipe_routing.py` | **仅 `foundation_domains`**，不读 `values` | `load_vocabulary_section_list("target_layer_vocabulary.yaml","foundation_domains")` | 模块 import 期 → `frozenset`，进程内常驻（事实上永久缓存） | CT-PIPE-ORC-001 路由：`target_layer ∈ foundation_domains → M5`，否则 `M6`；入参先 `.strip().upper()` | `ct_pipe_routing.py:67,69`（加载）/ `:142`（归一化）/ `:208`（判定） |
| 2 | `src/zephyr/infrastructure/pipeline/routing_plugins.py` | 仅 `foundation_domains` | 同上 | import 期 `frozenset` | LayerFilter 过滤：命中→M5 插件，否则 M6 | `routing_plugins.py:68,70` / `:201`（`LayerFilter.apply`） |
| 3 | `scripts/governance/d5_architecture/validators/validate_target_layer.py` | **`values[].value` + `deprecated_values[].value/.replacement`** | 自带 `yaml.safe_load`（**绕过 SSoT helper**） | 每次 CLI 运行加载；无缓存 | 正则扫 `src/`+`tests/` 里 `target_layer="X"` 字面量：废弃→WARNING，未知→ERROR | `:73,75`（路径）/ `:83`（加载函数）/ `:100±`（`valid_values`、`deprecated_map={v["value"]: v.get("replacement","")}`）/ `:120±`（`_TARGET_LAYER_RE`）/ `:134`（未知值消息） |
| 4 | `src/zephyr/shared/io/yaml_utils.py`（SSoT 加载层，被 `scripts/governance/_shared/yaml_utils.py` 再导出） | `values[].value` / `values[].definition`；`foundation_domains`（裸字符串段）；`deprecated_values` | `_collect_vocab_values` / `load_vocabulary_values` / `load_vocabulary_section_list` / `load_vocabulary_deprecated_map` / `load_all_vocabulary_values` | 纯函数按需读盘；同类先例 `_TTL_VALID_VALUES: Final = load_vocabulary_values("ttl_vocabulary.yaml", strict=False)`（import 期缓存） | ①**只取 `value`/`definition` → `aliases` 键永不进入任何消费者的值集**；②`load_vocabulary_deprecated_map(migrated_to_key="migrated_to")` 与本文件的 `replacement:` 键**不匹配** | `yaml_utils.py:300`（docstring 以本词表举例）；`_collect_vocab_values` / `load_vocabulary_section_list` / `load_vocabulary_deprecated_map` 函数体 |

### B 组：glob 目录批量读到本词表（4 个，文件名无关 → 隐形消费方）

| # | 消费方 | 读取段 | 语义 | 证据 | 收编影响 |
|---|---|---|---|---|---|
| 5 | `scripts/governance/d3_metadata/check_vocab_hardcode.py` | 全部 `values`（经 `load_all_vocabulary_values`） | **GATE-VOCAB** 的"检测 4/9/10"：AST 取字面量集合，若 `hit_count == len(str_values) 且 ≥ 2`（即**全子集**）→ 判硬编码违规；命中即需 `# noqa: gate-vocab` + 登记 `config/governance/noqa_exempt_registry.yaml` | `check_vocab_hardcode.py:302-325`（`_load_all_vocab_values`）/ `:361-395`（`_match_vocab_values` 全子集阈值）/ `:936,942,975`（主流程）；**门禁接线 `gate_registry.yaml:169-179`（`gate_id: GATE-VOCAB`，entry = `check_vocab_hardcode.py --ci` + `generate_derived_files.py --check`）** | ⚠ **`files_trigger` 含 `docs/01_policies_and_standards/_registry/vocabularies/.*\.yaml`（`gate_registry.yaml:175`）→ 本次改词表会「自我触发」整条 GATE-VOCAB**；且词表每加一个值，全仓字面量集合的合法域就扩大 → 实测新增 1 处命中（§6 R4） |
| 6 | `scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py` | `values` + `vocabulary_name` | 同步 **#157 词汇表 → PG `field_vocabularies`**（列：`field_name,value,definition,ai_consumption,source_yaml`）；另 **#156** 从 registry 同步 `domains` 表 | `sync_yaml_to_depgraph.py:86`（表名）/ `:774-796`（#157 + INSERT）/ `:909-938`（#160）；实测 DB 现状 `field_name='target_layer'` **45 行**（与 45 值全等） | 改 YAML 后不跑 sync → DB 镜像停留在 45 值；跑 sync → 61 行 |
| 7 | `scripts/governance/d5_architecture/validators/validate_architecture_contract_internal.py` | **仅文件名存在性** | `vocab_dir.glob("*.yaml")` 得到"已存在词表集"，校验架构契约引用的词表是否存在 | `:201-202` | 不受值变化影响（除非重命名文件） |
| 8 | `scripts/governance/d11_compliance/validate_vocabulary_coverage.py` | 应为"值级覆盖度"，但**函数体为空** | `find_vocabularies(vocab_dir) -> set[str]` 只有 docstring、**无 return**（隐式 None），且文件无 `main()`；仅登记在 `scripts/script-manifest.yaml:3207` / `scripts/governance/script_manifest.yaml:632` / `scripts_registry.yaml:370`，**未接入任何 gate** | `:105-111`（空实现）/ `:113-123`（`__manifest__` 声明 `warn_only: false`） | ⚠ 死代码陷阱：若战役"顺手把它接上门禁"，调用方会对 `None` 做集合运算直接崩（§6 R13） |

### C 组：注释/文档串"假读"（3 个，不读内容 → 改词表不会让其报错，但会让其**语义漂移**）

| # | 消费方 | 形态 | 硬编码镜像内容 | 证据 |
|---|---|---|---|---|
| 9 | `src/zephyr/shared/blueprint_tools/blueprint_decomposer.py` | 注释声明"对齐 v1.0.0"，实为**本地硬编码 dict** | `_FUNC_DOMAIN_TO_TARGET_LAYER` 14 条（`"data"→D_MKT_DATA`、`"execution"→D_EX_CORE`、`"capacity"→D_INFRA_OPS`、`"infra"→D_INFRA_RUNTIME`、`"compliance"→D_GOV_ENFORCEMENT`…）+ `_LAYER_TO_TARGET_LAYER`（`"L0_infrastructure"→D_INFRA_OPS`）；`_infer_target_layer(fm)` 从 frontmatter `functional_domain`/`layer` 推断 | `:183,185`（注释）/ `:186`（dict）/ `:219`（"对齐 target_layer_vocabulary.yaml v1.0.0"）/ `:251`（调用点） |
| 10 | `scripts/_archive/migration/inject_domain_fields.py` | `[DEPRECATED]` 头，指向词表为"正确命名约定" | 无值读取 | `:4` |
| 11 | `src/zephyr/shared/io/yaml_utils.py` docstring | 以本词表为**唯一示例** | — | `:300` |

### D 组：测试链消费方（1 个，当前豁免）

| # | 消费方 | 断言 | 是否覆盖本词表 | 证据 |
|---|---|---|---|---|
| 12 | `tests/infrastructure/test_vocab_sync_chain.py` | Bug A~H 回归：路径 snake_case、`vocabulary_name` 键、`--check` exit 0、`field_vocabularies.field_name` 无 `_vocabulary` 脏值、只读 PG 连通 | **否**——枚举式豁免：`test_vocab_field_map_uses_snake_case_filenames` 只遍历 `VOCAB_FIELD_MAP`（其中无 `target_layer`）；`test_all_vocab_yamls_use_vocabulary_name_key` 只检查硬编码 5 文件清单（doc_type/status/rule_form/ttl/layer） | `:135-142`、`:507-518`、`:167-199` |

### E 组：域命名空间"权威"（不读词表，但决定 `D_*` 是否合法 → 收编必须同框考虑，5 个）

| # | 权威 | 真源 | 与本词表关系 | 证据 |
|---|---|---|---|---|
| 13 | **GATE-DOMAIN-FK**（`src/zephyr/gov_enforcement/commit_gates/domain_fk_gate.py`） | `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml` | **完全不看 target_layer 词表**；只扫 staged `.py` 的 `# [DOMAIN] X` 头 | `_DOMAIN_REGISTRY_REL` / `_DOMAIN_HEADER_RE = ^#\s*\[DOMAIN\]\s*(\S+)` / `_YAML_DOMAIN_ENTRY_RE = ^-\s*domain:\s*(\S+)`；`GateSpec(gate_id="GATE-DOMAIN-FK", priority=78)` |
| 14 | PG `domains` 表 + FK | `functional_domain_registry.yaml`（#156） | `CHECK` 是**格式正则**，不是值枚举 → 任何 `D_[A-Z][A-Z0-9_]{0,59}` 都能入库 | `scripts/governance/d3_metadata/validate_module_id_naming.py:172`（`DOMAIN_ID_RE`）；`apply_depgraph` 的 NR-001/002/003 命名规则表 + `--apply-domain-id-check-constraint` |
| 15 | `scripts/governance/apply_depgraph.py` | 迁移动词 | `--merge-domain`（**target 必须已存在于 domains 表**）/ `--rename-domain`（18 步 UPDATE、11 张表）/ 全表 TEXT 替换 | 见 §4 B 组矩阵 FK 列 |
| 16 | 中文名/前缀映射（生成器输入） | `domain_name_mapping.py`、`error_code_registry.yaml` | 以 `domain_id` 为键；含 **B 组值**：`domain_name_mapping.py:158,236 "D_INFRASTRUCTURE"`；`error_code_registry.yaml:37,39 IF/INT: D_INFRASTRUCTURE`、`:49 RE: D_RESEARCH` | `domain_name_mapping.py:1-40`（4 层真源优先级 DB→YAML→硬编码测试域→id） |
| 17 | 派生文档/全景图 | `generate_derived_files.py`(`VOCAB_FIELD_MAP`)、`generate_panorama_registry.py`、`architecture_model/index.yaml`、`cross_cutting/capability_heatmap.yaml` | `VOCAB_FIELD_MAP` 有 `"domain": "domain_vocabulary.yaml"`（那是**小写知识域词表**，与本词表同名异义），**无 target_layer**；B 组值散布于生成产物（`generate_panorama_registry.py:575` 提到 `D_RISK/D_PORTFOLIO`） | §6 R14 |

> **"第 7 个消费方"结论**：存在，但不是单个文件——是**按目录 glob 的一族**（表 B 组 #5/#6/#7/#8）。
> 其中 #5 `check_vocab_hardcode.py`（GATE-VOCAB）与 #6 `sync_yaml_to_depgraph.py`（DB 镜像）是**只有 glob 才能发现**的真消费方：
> `grep -rn "target_layer_vocabulary" --include="*.py" src scripts tests` 只返回 6 处（全在 A/C 组），**完全漏掉 B 组 4 个**。

---

## 2. TaskCard 面（必查面 2）

| 问题 | 结论 | 证据 |
|---|---|---|
| `target_layer` 在哪定义？ | `TaskCard` 是 **pydantic `Task` 的纯别名**（`TaskCard = _lazy_import_governance("Task")`，**无独立类定义**，`grep "class TaskCard"` = 0 命中）；字段在 `src/zephyr/gov_enforcement/rule_enforcement/task_types.py:194` | `rule_enforcement/task_types.py:117`（`class Task`）/ `:194`（`target_layer: str | None`）；`src/zephyr/governance/models.py` 头 INVARIANTS（别名声明） |
| 有无 `Literal`/`Enum` 硬编码域清单（会连坐）？ | **无**。`target_layer` 是裸 `str | None`，字段上**无** `field_validator` 引词表 → 加/折叠词表值**不会**让 TaskCard 报校验错 | 同上（`task_types.py:194` 无 validator 关联） |
| 落在哪张表/文件？ | SQLite `data/databases/governance.db` → 表 `tasks`，列 `target_layer TEXT`（**无 CHECK**）；写入走 `task_repo.py` 的 UPSERT | `src/zephyr/governance/persistence/sqlite_schema.py:24`（物理路径声明）/ `:768`（`ALTER TABLE tasks ADD COLUMN target_layer TEXT`）；`persistence/task_repo.py:187,208,255,276,342`（列清单 + `target_layer = excluded.target_layer`）/ `:893`（`getattr(task,"target_layer","")`） |
| 历史数据实际存的是什么值？ | **2320 行为空**，146 行为**数字串 "1"~"7"**（`1:22 / 2:20 / 3:20 / 4:28 / 5:32 / 6:20 / 7:24`），全部集中在 `2026-06-13T17:01~17:07` 一次批量导入（`SRC-1006xx` 系列任务）；**零条 `D_*` 值** | 只读 `SELECT target_layer, count(*) FROM tasks GROUP BY 1`（`mode=ro` URI） |
| 由此得出 | 词表与 TaskCard 历史数据**从未真正对齐**：`target_layer` 列被复用成了"数字层"语义（与同表 `depgraph_layer` 的 "1".."7"/"module" 同源，`depgraph_layer` 非空 146+6 行）。**任何"按 target_layer ∈ 词表 路由/校验"的新代码会 100% 踩空**（§6 R2） | `PRAGMA table_info(tasks)`：76 列，含 `depgraph_layer TEXT`(#54)、`target_layer TEXT`(#60) |
| PG depgraph 侧 `domains` 历史值 | `domains` 75 行（含 B 组的 `D_INFRASTRUCTURE` / `D_RESEARCH` / `D_CONTRACTS`；**不含** `D_GOV`/`D_EXECUTION`/`D_PORTFOLIO`/`D_PLAN_ENGINE`/`D_INFRA`/`D_SIGNAL`/`D_ORDER`） | §5 实测 |

---

## 3. 蓝图 `domain:` 字段的门禁面（必查面 3）

| 子问 | 结论 | 证据 |
|---|---|---|
| 有门禁拿词表校验蓝图 YAML 的 `domain:` 吗？ | **没有**。GATE-15（`scripts/governance/d3_metadata/check_frontmatter_metadata.py`）的 `_FIELD_RULES` 只覆盖 `ttl` / `doc_type`；GATE-DOMAIN-FK 只匹配 `# [DOMAIN] X` 行（staged **`.py`**）；`gate_registry.yaml`（169 条 gate）中 `grep target_layer` = **0 命中**（GATE-22 实为"AI加载路径完整性" `validate_load_path_integrity.py`，与本词表无关；不存在 `validate_domain_vocabulary_ssot.py`）。注意 `domain_vocabulary.yaml` 是**另一套小写 10 值知识域词表**，与本词表同名异义 | `gate_registry.yaml:158-179,379-380`；`check_frontmatter_metadata.py`（`_FIELD_RULES`）；`domain_fk_gate.py`（header 正则）；`generate_derived_files.py:82`（`VOCAB_DIR`）+ `VOCAB_FIELD_MAP` 无 target_layer |
| 蓝图 frontmatter 实际用的字段名 | `functional_domain: <小写短名>`（如 `portfolio`）+ `layer: L2_domain` → 由 §1 C 组 #9 的**硬编码 dict** 翻译成 `D_*`，不经词表 | `docs/03_modules/_domain_portfolio_core/blueprint.md:9,10`（`functional_domain: portfolio` / `layer: L2_domain`） |
| 是否存在带 B 组值的未受门禁蓝图文件？ | **存在 2 个**：`docs/03_modules/_domain_governance/indicator_usage_audit/blueprint.md:4 → domain: D_GOV`、`docs/03_modules/_domain_infrastructure_operations/config_center/blueprint.md:4 → domain: D_INFRASTRUCTURE`（均为 frontmatter，折叠后成为孤儿值） | grep `^domain:` over `docs/03_modules` |
| 蓝图正文 `domain: D_*` 规模 | 302 个 blueprint.md 带 `^domain:`，Top：`D_ASHARE_SIGNAL 61 / D_KNOWLEDGE 15 / D_INTELLIGENCE 15 / D_AUTONOMY_CORE 15 / D_ALT_DATA 15 / D_ML_TRAIN 13 / D_FRONTEND 11 / D_DATA_GOV 11 / D_DATA 11 / D_PLAN 9 / D_INFRA_RUNTIME 9`…（含 16 新值中的 `D_ALT_DATA/D_DATA_GOV/D_FRONTEND/D_PLAN/D_POSITION/D_REPORTING` 等）→ 改词表**不会**触发它们，但**收编后必须重跑派生**否则文档与词表两套命名 | 同上（`grep -rh "^domain:" \| sort \| uniq -c`） |

---

## 4. B 组别名迁移影响面矩阵（必查面 4）

统计口径：`\b(D_GOV|D_EXECUTION|D_PORTFOLIO|D_PLAN_ENGINE|D_INFRASTRUCTURE|D_RESEARCH|D_SIGNAL|D_CONTRACTS|D_INFRA|D_ORDER)\b`，
扫描 `src tests scripts config schemas architecture_model acceptance meta docs`（`.py/.yaml/.yml/.md/.sql/.json/.toml`），
**已排除** `*_archive/` 目录（另列）；`annot` = 代码 `# [DOMAIN]` 头数量。

| 源值 | 折叠目标 | annot | src | tests | scripts | config | schemas | arch_model | docs_arch | docs_modules | docs_registry | `domains`表 | FK 暴露节点 | 迁移手段 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `D_GOV` | `D_GOVERNANCE` | **1** | 1 | **10** | 0 | 0 | 0 | 0 | 0 | 1 | 1 | ✗ | 0 | 纯文本 + 1 条标注 |
| `D_EXECUTION` | `D_EX_CORE` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 4 | ✗ | 0 | registry/docs 命名（别名） |
| `D_PORTFOLIO` | `D_PF_CORE` | 0 | **3** | 1 | 1 | 0 | 0 | 0 | 11 | 4 | 5 | ✗ | 0 | 含 **tuple 实参 + 测试断言** |
| `D_PLAN_ENGINE` | `D_PLAN` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | ✗ | 0 | registry/docs 命名（别名） |
| `D_INFRA` | `D_INFRA_OPS` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | ✗ | 0 | 1 行注释（历史 FK 修复记录） |
| `D_INFRASTRUCTURE` | `D_INFRA_OPS` | **40** | **41** | 0 | 12 | **4** | 0 | **5** | 899 | 3 | 40 | ✓ | **84** | **`--merge-domain`（需 FK 迁移）** |
| `D_RESEARCH` | `D_INTELLIGENCE` | 2 | 35 | 4 | 10 | 0 | 0 | 2 | 145 | 35 | 47 | ✓ | **2** | `--merge-domain` |
| `D_SIGNAL` | `D_SIGLEGACY` | **40** | 79 | 11 | 21 | 0 | **4** | 0 | 94 | 89 | 64 | ✗ | **0** | 文本层 + 契约清单（无 FK） |
| `D_CONTRACTS` | `D_SHARED` | 2 | 2 | 0 | 3 | 0 | 0 | 1 | 94 | 3 | 24 | ✓ | **2** | `--merge-domain` |
| `D_ORDER` | （仅 registry 存在） | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **5** | ✗ | 0 | registry-only，无代码 |

（合计：`D_INFRASTRUCTURE` 1005 / `D_SIGNAL` 362 / `D_RESEARCH` 278 / `D_CONTRACTS` 127 / `D_PORTFOLIO` 25 / `D_GOV` 18 / `D_ORDER` 5 / `D_EXECUTION` 6 / `D_INFRA` 3 / `D_PLAN_ENGINE` 2 次命中。）
另有历史归档侧巨型存量（**不迁移、只登记**）：`docs/01_policies_and_standards/_registry/catalogs/_archive/candidate_module_registry_harvest_archive.yaml` 含 `D_SIGNAL` 324 次（其中 `domain: D_SIGNAL` 行 322）；`docs/_archive/依赖图/17-D-COMPLIANCE-合规监管域.md` 等。

### 逐格关键证据（file:line）

**D_PORTFOLIO（唯一的 tuple 实参 + 断言，最易被"别名对加载器不可见"反噬）**
- `src/zephyr/ex_core/multi_contract_adapter.py:116` — `consumer_domains: tuple[str, ...]  # ("D_PORTFOLIO", "D_EX_SOR")`
- `src/zephyr/ex_core/multi_contract_adapter.py:322` — 注释 `CTR-004 Order 契约 Schema（D_EX_CORE 生产 → D_PORTFOLIO / D_EX_SOR 消费）`
- `src/zephyr/ex_core/multi_contract_adapter.py:328` — **`consumer_domains=("D_PORTFOLIO", "D_EX_SOR"),`**
- `tests/ex_core/test_multi_contract_adapter.py:294` — **`assert "D_PORTFOLIO" in schema.consumer_domains`**（断言源值，折叠后语义上"非法"）
- `scripts/governance/d5_architecture/generators/generate_panorama_registry.py:575` — 生成器文案 `从 D_RISK/D_PORTFOLIO 域派生`

**D_GOV**
- `src/zephyr/governance/indicator_usage_audit.py`（1 处，含 `# [DOMAIN] D_GOV` 标注 —— 全仓唯一）
- `tests/dr/test_restore_from_backup.py`（4）、`tests/governance/test_align_panoramas.py`（3）、`tests/governance/test_panorama_common.py`（2）、`tests/governance/rule_bridge/test_ssot_gate.py`（1）
- `docs/03_modules/_domain_governance/indicator_usage_audit/blueprint.md:4` — frontmatter `domain: D_GOV`

**D_INFRASTRUCTURE**
- 代码 41 处 / 40 个文件带 `# [DOMAIN] D_INFRASTRUCTURE`（例：`src/zephyr/backtest/core/engine_base.py`）
- `config/governance_operations_map.yaml:852,858,1684,2501` — `domain: D_INFRASTRUCTURE`（运维映射表 4 条）
- `architecture_model/contracts/error_code_registry.yaml:37,39,74` — 错误码前缀 `IF / INT / INF → D_INFRASTRUCTURE`
- `scripts/governance/d5_architecture/generators/domain_name_mapping.py:158,236` — 中文名 + 描述（英文 "Cross-Layer Contract Infrastructure"）
- `scripts/governance/migrate_sqlite_to_pg/07_fix_5_violations.sql:32,35` — `D_INFRASTRUCTURE (26节点,107入边)` 历史修复
- `scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py:1952` — `# 修复 ARCH-053 FK 违反：D_INFRA 不存在于 domains 表，nodes_domain_id_fkey 阻断`
- `docs/03_modules/_domain_infrastructure_operations/config_center/blueprint.md:4` — frontmatter `domain: D_INFRASTRUCTURE`

**D_SIGNAL**
- `src/zephyr/shared/contracts/freeze_manifest.yaml:39,41,48,50,104,111` — 契约生产者/消费者清单（`consumers: ["D_FACTOR","D_SIGNAL","D_RISK"]` 等；同文件 `:111` 已使用 `D_PORTFOLIO_CORE`，即**已废弃值**）
- `src/zephyr/signal_fundamental/gen/aggregator_base.py:26,37,38,42,60,85` — 架构说明 + OCP 扩展点 ID `D_SIGNAL-AGG` / `D_SIGNAL-ALC`（**注意：折叠会污染扩展点命名**）
- `scripts/construction/demo_e2e_pipeline.py`（6）、`src/zephyr/signal_ashare/signal_history_writer.py`（2，兼 `# [DOMAIN]`）
- `schemas/categories/market/market_signal_history.py`、`market_pattern_event.py` 等 4 处 schemas 引用

**D_RESEARCH**
- `src/zephyr/simulation/pipeline_base.py:4` / `src/zephyr/governance/engine/pipeline_base.py:4`（各 4 处）
- `scripts/construction/demo_e2e_pipeline.py`（5）、`tests/governance/test_battle_map_research_incubation.py`（4）
- `scripts/governance/d5_architecture/validators/validate_blind_spot_status.py:129,132,143` — **BLIND-L09 判定逻辑按 `D_RESEARCH` 目录存在性**（折叠后该盲区检查会恒 False）
- `architecture_model/contracts/error_code_registry.yaml:49` — `RE: D_RESEARCH`

**D_CONTRACTS**
- `src/zephyr/shared/contracts/ctr002_producer_validator.py` / `ctr002_consumer_adapter.py`（各 1，含 `# [DOMAIN] D_CONTRACTS`）
- `scripts/governance/migrate_sqlite_to_pg/07_fix_5_violations.sql:134,167-168` — **`INSERT ... ('D_CONTRACTS','共享契约',...)` + `UPDATE nodes SET domain_id='D_CONTRACTS'`**（当年从 `D_SHARED` **拆出**，本次收编等于**反向合并回去**）
- `architecture_model/index.yaml`（1）、`docs/02_enterprise_architecture/03_governance_reports/candidate_modules/D_CONTRACTS.md`（域专档）

### 4.1 标注值 ↔ 词表差集（= 战役 A 组 16 的独立复算）

71 个被标注值中 **25 个不在 45 合法值**（剔除 2 条中文正则伪值）：

| 分类 | 值（annot 数 / DB 节点数） |
|---|---|
| **A 组 16（应新增）** | `D_ALT_DATA` 36/37、`D_CROSS_ASSET` 7/7、`D_DATA_ENG` 19/32、`D_DATA_GOV` 26/26、`D_DATA_SEC` 10/10、`D_DIGITAL_TWIN` 8/8、D_EXEC_SIM 8/8、`D_EX_SOR` 28/26、`D_FRONTEND` 50/79、`D_PF_ALLOC` 30/37、`D_PLAN` 41/41、`D_POSITION` 41/46、`D_REGIME` 82/78、`D_REPORTING` 50/58、`D_SELL_DECISION` 29/31、`D_TEST` 1/**0** |
| **B 组 9（应折叠）** | `D_GOV` 1/0、`D_EXECUTION` 0/0、`D_PORTFOLIO` 0/0、`D_PLAN_ENGINE` 0/0、`D_INFRASTRUCTURE` 40/**84**、`D_RESEARCH` 2/**2**、`D_SIGNAL` 40/0、`D_CONTRACTS` 2/**2**、`D_INFRA` 0/0（`D_ORDER` 0/0，仅 registry） |
| **虚构废弃（战役外发现）** | `D_DATA` **473 annot / 538 节点**、`D_COMPLIANCE` **26 annot / 51 节点** —— 词表标 deprecated，但仍是**全仓第 2 大在用域** |
| 其他越界 | `D_EXECUTION_CORE` 1（词表已列 deprecated 且**同时**是 `D_EX_CORE.aliases` → 双写）、`D_SIGNAL_ASHARE` 1、`D_SIGLEGACY` 1（**唯一零标注的合法值**） |

**45 合法值中只有 `D_SIGLEGACY` 无任何代码标注**；其余 44 值均有 ≥1 落点。

---

## 5. 16 个新值"是否已存在于 DB / 契约文件"（必查面 5）

只读 PG（`depgraph_reader`）：`domains` 75 行、`nodes` 11923 行。

| 新值 | `domains` 表有行？ | `nodes` 节点数 | 契约/架构模型文件出现 |
|---|---|---|---|
| `D_ALT_DATA` | ✓ | 37 | error_code_registry / capability_heatmap / index.yaml |
| `D_CROSS_ASSET` | ✓ | 7 | capability_heatmap / index.yaml |
| `D_DATA_ENG` | ✓ | 32 | error_code_registry(`DE`) / heatmap / index |
| `D_DATA_GOV` | ✓ | 26 | heatmap / index |
| `D_DATA_SEC` | ✓ | 10 | error_code_registry / heatmap / index |
| `D_DIGITAL_TWIN` | ✓ | 8 | error_code_registry / heatmap / index |
| `D_EXEC_SIM` | ✓ | 8 | error_code_registry / heatmap / index |
| `D_EX_SOR` | ✓ | 26 | error_code_registry / heatmap / index |
| `D_FRONTEND` | ✓ | 79 | consumer_registry / cross_layer_contracts / error_code_registry(`FE`) … 共 12 文件 |
| `D_PF_ALLOC` | ✓ | 37 | error_code_registry(`PA`) / heatmap / index（7 文件） |
| `D_PLAN` | ✓ | 41 | error_code_registry(`PLAN`) / index |
| `D_POSITION` | ✓ | 46 | consumer_registry / cross_layer_contracts / error_code_registry(`POS`)（6 文件） |
| `D_REGIME` | ✓ | 78 | error_code_registry / index |
| `D_REPORTING` | ✓ | 58 | consumer_registry / cross_layer_contracts / error_code_registry(`RPT`)（12 文件） |
| `D_SELL_DECISION` | ✓ | 31 | error_code_registry(`SELL`) / heatmap / index |
| `D_TEST` | ✓（0 节点） | 0 | **无任何契约/架构模型文件**（仅 registry + 1 条测试标注） |

→ **结论：16/16 已在 `domains` 表**（即 DB 侧早已承认这些域，是**词表滞后于 DB**，而非词表扩权）；
15/16 已在 `architecture_model/contracts/**` 或 `index.yaml`/`capability_heatmap.yaml` 中出现；唯一无落点的是 `D_TEST`。
（另注：`D_GOV_SCRIPTS`/`D_GOV_RULE`/`D_KNOWLEDGE`/`D_SECURITY_LLM`/`D_INFRA_TELEMETRY`/`D_SIGQC` 等 11 个 DB-only 域见 w1d 口径。）

---

## 6. 风险点（按爆炸半径排序）

| ID | 风险 | 机理与证据 | 处置建议（只登记，不在本次实施） |
|---|---|---|---|
| **R1** | **别名对 100% 加载器不可见 → 折叠后源值从"废弃(WARNING)"降级为"未知(ERROR)"** | `yaml_utils._collect_vocab_values` 只取 `value`/`definition`，`aliases` 从未被任何消费方读到（§1 A#3、A#4）；`validate_target_layer.py` 的 `valid_values` 只含 `values[].value`，`deprecated_map` 只含 `deprecated_values[].value` → 把 `D_GOV` 放进某值的 `aliases` 后，它既不在 valid 也不在 deprecated | 折叠 ≠ 只写 `aliases`：**必须同时**把 9 个源值搬进 `deprecated_values`（带 `replacement:`），或给加载器/校验器加 `aliases` 支持并在词表加 `alias_of` 显式映射 |
| **R2** | **TaskCard 历史 `target_layer` 是数字 1–7，与词表毫无交集** | `governance.db:tasks` 2320 空 / 146 行为 `"1".."7"`（2026-06-13 单批 `SRC-1006xx`）；列 `TEXT` 无 CHECK（`sqlite_schema.py:768`） | 收编同时定义"数字层"归 `depgraph_layer`/`layer_vocabulary`，`target_layer` 侧需一次性清洗或显式声明废弃语义；新校验器**不要**假定历史值合法 |
| **R3** | **改词表拦不住代码：真正的 enforcement 在 registry** | GATE-DOMAIN-FK（priority 78，硬阻断）只比对 `functional_domain_registry.yaml` 的 `^- domain: X`（`domain_fk_gate.py`），且不读 target_layer 词表；registry 83 条 / 68 唯一，**10 个重复键**（`D_GOVERNANCE`×3、`D_SECURITY`×3、`D_GOV_AUDIT`×3、`D_INFRA_RUNTIME`×3、`D_INFRA_OPS`×3、`D_GOV_SCRIPTS`×2、`D_AUTONOMY_CORE`×2、`D_AUTONOMY_PERM`×2、`D_OPS`×2、`D_ML_TRAIN`×2） | 词表与 registry 的差集必须同批收编（否则词表合法但 registry 非法 → 提交被阻断；反之词表废弃但 registry 放行 → 静默漂移）；重复键先治，否则 `--merge-domain` 的 registry 侧改写不确定 |
| **R4** | **改词表这一笔提交会「自我触发」GATE-VOCAB，并因 +1 新命中当场卡住** | `gate_registry.yaml:175` 的 `files_trigger` 覆盖 `docs/01_policies_and_standards/_registry/vocabularies/.*\.yaml` → 提交词表改动即执行 `check_vocab_hardcode.py --ci` + `generate_derived_files.py --check`。新命中 `tests/ex_core/test_multi_contract_adapter.py:224`：`make_schema("CTR-A", consumers=("D_RISK", "D_REPORTING"))` —— 加 16 值后该 2 值 tuple 成为 target_layer 值集**全子集**（`_match_vocab_values` 的 `hit_count == len(str_values)` 且 ≥2 判据，`check_vocab_hardcode.py:393`）（AST 全量模拟，非抽样） | 该测试行加 `# noqa: gate-vocab` 并登记 `config/governance/noqa_exempt_registry.yaml`；或改用 `load_vocabulary_values` 派生。验收：战役前后各跑一次 `check_vocab_hardcode.py --ci` 做 diff——**且必须在同一次提交内完成豁免登记**，否则词表提交本身被自家门禁阻断 |
| **R5** | **B 组里只有 3 个值有 FK 暴露，其余 6 个纯文本 → 迁移手段必须分流** | FK `nodes.domain_id → domains.domain_id`；`D_INFRASTRUCTURE` 84 / `D_RESEARCH` 2 / `D_CONTRACTS` 2 节点需 `apply_depgraph --merge-domain`（target 须已存在：`D_INFRA_OPS`16 / `D_INTELLIGENCE`162 / `D_SHARED`405 节点均在表 ✓）；`D_GOV`/`D_SIGNAL`/`D_EXECUTION`/`D_PORTFOLIO`/`D_PLAN_ENGINE`/`D_INFRA`/`D_ORDER` 在 `domains` 表**无行** → 不能 merge（会 FK/存在性失败），只能改 registry+代码文本 | 分流：①FK 三值走 `--merge-domain`（并核对 `07_fix_5_violations.sql:134,167` 表明 `D_CONTRACTS` 当初**从 D_SHARED 拆出** → 反合并需确认拆分理由是否仍成立）；②其余六值仅做文本 + 别名；③别把 9 值写成同一条命令 |
| **R6** | **`D_DATA` / `D_COMPLIANCE` 的"废弃"是虚构状态** | 词表 `deprecated_values` 含二者（`D_DATA` 还有孪生 `D-DATA`），但代码 `# [DOMAIN] D_DATA` **473 条**、`D_COMPLIANCE` 26 条，DB 节点 **538 / 51**（占 11923 的 4.5% / 0.4%） | 战役若把废弃值当"已死"处理（如从 registry 移除/让 validator 升 ERROR）→ 直接引爆 GATE-DOMAIN-FK 与 panorama。应先出"废弃未清账"专章，或把二者从 deprecated 降级为"deprecated-with-migration-plan" |
| **R7** | **逐值校验器基线已经全红（13 ERROR）** | `python scripts/governance/d5_architecture/validators/validate_target_layer.py` → `✗ 13 个未知 target_layer 值！`，全部来自 `tests/knowledge/test_knowledge_artifact_store.py:116,125,139,152,229,235,264,279…` 的 `target_layer="L1"/"L2"/"L3"`（**与 `layer_vocabulary` 的 L0_infrastructure… 同族假红**，属另一个字段语义） | 战役 W5（治本全仓 L1/L2/L3 同族假红）必须在 W3 之前或同批，否则"改完 0 ERROR"的验收口径不可达；或校验器加同族豁免 |
| **R8** | **词表自描述字段与 helper 键名不匹配** | `total_values: 45`（`:57`）是**手写**值 → +16 必须同步 61（否则 §9.5"静态清单须生成"红线）；`deprecated_values` 用 `replacement:` 键（`:281+`），而 `load_vocabulary_deprecated_map` 默认 `migrated_to_key="migrated_to"` → 新代码若改用 SSoT helper 会得到**空映射**，废弃告警静默消失 | 统一键名（词表改 `migrated_to:` 或 helper 传参），并让 `total_values` 由生成器写 |
| **R9** | **唯一逐值校验器不在门禁链上** | 真源 `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`（169 条 gate）与 `in_process_gate_registry.yaml` 中 `grep validate_target_layer\|target_layer` = **0 命中**；该脚本只登记在 `scripts/script-manifest.yaml` / `scripts/governance/script_manifest.yaml` → 词表与代码可以无限漂移而无门禁报警 | 战役若要"改了就有人报"，需把 `validate_target_layer.py` 接入 gate_registry（建议 warn→hard 两段式），并复用 §1 A#3 的读取段但改走 SSoT helper（消双真源） |
| **R10** | **两个子蓝图 frontmatter 直接写 B 组值，无门禁** | `docs/03_modules/_domain_governance/indicator_usage_audit/blueprint.md:4 = domain: D_GOV`；`docs/03_modules/_domain_infrastructure_operations/config_center/blueprint.md:4 = domain: D_INFRASTRUCTURE`（GATE-15 只查 ttl/doc_type，GATE-DOMAIN-FK 只查 `.py`） | W4 的"domain 补标/生成器"应把 md frontmatter `domain:` 纳入改写集，并考虑把该字段接入 GATE-15 |
| **R11** | **契约清单与词表两套命名（含已废弃值）** | `src/zephyr/shared/contracts/freeze_manifest.yaml:39,41,48,50,104,111` 用 `D_SIGNAL`/`D_DATA`/`D_PORTFOLIO_CORE`（后两者已在 `deprecated_values`）；`multi_contract_adapter.py:328` 用 `D_PORTFOLIO`；`error_code_registry.yaml` 前缀表用 `D_INFRASTRUCTURE`/`D_RESEARCH`/`D_DATA`/`D_COMPLIANCE` | 契约侧需"按目标值批量重写"，且重写后**必须重跑派生**（consumer_registry / cross_layer_contracts / panorama / heatmap / constraint_violations.md 50 处提及） |
| **R12** | **DB 镜像与中文名/前缀映射的次生漂移** | `field_vocabularies WHERE field_name='target_layer'` 现 **45 行**（与 YAML 全等，`sync_yaml_to_depgraph.py:774-796` 产）；`domain_name_mapping.py:158,236` 与 `error_code_registry.yaml:37,39,49,74` 以 domain_id 为键 | 词表改动后跑 sync #157 + 更新 registry `domain_name_zh` + 前缀表重定向（`IF/INT/INF → D_INFRA_OPS`、`RE → D_INTELLIGENCE`）；否则中文全景图出现孤儿域 |
| **R13** | **死代码陷阱：覆盖率校验器是空实现** | `validate_vocabulary_coverage.py:105-111` `find_vocabularies` 无 return（隐式 None）、文件无 `main()`，但 `__manifest__` 声明 `warn_only: false`（`:113-123`） | 战役若"顺手接入门禁"必崩；建议同批补实现或明确标 `deprecated`，**不要**在 W3 里当作已有防线引用 |
| **R14** | **扩展点/文档 ID 与域 ID 同名冲突** | `src/zephyr/signal_fundamental/gen/aggregator_base.py:37,38,60,85` 的 OCP 扩展点 ID 形如 `D_SIGNAL-AGG` / `D_SIGNAL-ALC`（正则 `\bD_SIGNAL\b` 会命中；`--rename-domain` 全表 TEXT 替换类动词若不加边界会污染扩展点标识） | 迁移动词需带 `-` 边界保护；替换前对 `D_SIGNAL-` 前缀做白名单 |
| **R15** | **5 处潜在 GATE-DOMAIN-FK 违规（战役外存量，会被误算成本战役成果）** | registry 中已存在的越界/短写条目（`D_GOV`、`D_CONTRACTS`×2、`D_EXECUTION_CORE`、`D_SIGNAL_ASHARE`）一旦相关文件被 staged 即红；另 `D_EXECUTION_CORE` 同时是 `D_EX_CORE.aliases` 与 `deprecated_values` 条目（双写） | W2 封矿时把这 5 处显式登记为"存量"，避免 W6 两轮基线对比把它们当新增 |

---

## 7. 复算命令（全部只读）

```bash
# (1) 消费方普查：文件名直引 vs 目录 glob
grep -rn "target_layer_vocabulary" --include="*.py" src scripts tests
grep -rn "VOCAB_DIR\|vocab_dir\|glob(\"\*.yaml\")" --include="*.py" scripts src tests

# (2) 词表结构
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/vocabularies/target_layer_vocabulary.yaml',encoding='utf-8'));print(len(d['values']),len(d['deprecated_values']),d['foundation_domains'])"

# (3) TaskCard 历史值（SQLite 只读 URI）
python -c "import sqlite3;c=sqlite3.connect('file:data/databases/governance.db?mode=ro',uri=True);print(c.execute('SELECT COALESCE(NULLIF(target_layer,\"\"),\"(empty)\") v,count(*) FROM tasks GROUP BY 1 ORDER BY 2 DESC').fetchall())"

# (4) PG depgraph（depgraph_reader 只读角色）
#   domains 75 行；nodes 11923 行；field_vocabularies field_name='target_layer' 45 行

# (5) 标注差集 + GATE-VOCAB 模拟：见本文 §4 / R4 生成过程（ast + _match_vocab_values）

# (6) 逐值校验器基线
python scripts/governance/d5_architecture/validators/validate_target_layer.py   # ✗ 13 个未知值

# (7) 门禁接线核验（真源 gate 清单 = 169 条）
grep -c "^- gate_id:" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
grep -n "target_layer\|validate_target_layer" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml   # 0 命中
sed -n '169,179p' docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml   # GATE-VOCAB entry + files_trigger
```

---

## 8. 未覆盖/待确认（诚实边界）

1. `check_vocab_hardcode.py` 完整 CI 跑（全仓 AST 扫描）未执行，R4 的 +1 是**按门禁同源函数**（`_is_literal_collection` + `_match_vocab_values`）对 `src/scripts/tests/config/schemas` 全量模拟的结果；若门禁实际文件范围更宽（如含 `docs/` 内嵌 py），需以 `--ci` 实跑为准。
2. `field_vocabularies` 的**下游读取方**未逐一确认（现见 `reconciliation_registry.py:3636` 做 YAML↔DB 漂移对账、`generate_panorama_registry.py:887` 只是文案引用）→ 若战役新增消费方需补登记。
3. 先前 W1 假设中的"GATE-22 = `validate_domain_vocabulary_ssot.py`（warn-only）"**已被否证**：该脚本在树内不存在（`find scripts -name "*domain_vocabulary*" -o -name "*vocab*ssot*"` 空），`gate_registry.yaml:379` 的 GATE-22 是"AI加载路径完整性"（`validate_load_path_integrity.py`）。全 169 条 gate 无一读 target_layer 词表逐值 → 词表侧"零硬拦截"结论成立。仍开放：`field_vocabularies` 的读方清单（见 R12）与 `run_gate_chain.py` 对 `--ci` 传参的文件集（决定 R4 的实际命中范围）。
4. `architecture_model/**` 派生产物的生成顺序与幂等性未验证（属 W4 生成器面）。
