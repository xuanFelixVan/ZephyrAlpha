---
ttl: task_bound
doc_type: construction_plan
---

# Vocabulary 自动同步链路断裂修复方案（施工细节版 v1）

> **文档定位**：议题 #ARCH-008 的详细执行方案，修复 vocabulary YAML → 派生文件 / DB 缓存自动同步链路自项目建立以来从未真正工作过的根因性故障
> **制定日期**：2026-06-26
> **版本**：v1（基于 5 路并行深度调研综合编写）
> **方案性质**：待用户批准后执行
> **依据**：第一性原理分析 + SSoT 硬约束（YAML 是规则数据唯一真源）+ trae_028 snake_case 一条规则零例外

---

## 第一部分：议题与背景

### 1.1 议题登记

| 字段 | 值 |
|---|---|
| 议题编号 | **#ARCH-008**（#ARCH-001~007 已用，全项目 Grep `#ARCH-008` 无命中，可申请） |
| 议题分类 | 词汇表同步链路根因性失效 |
| 发现日期 | 2026-06-25 |
| 议题状态 | 待裁定 |
| 影响等级 | P1（SSoT 硬约束被违反，但当前无运行时功能阻断） |
| 关联议题 | #ARCH-005（layer_id 非法值）、#ARCH-007（CHECK 约束）、裁定#203-C |
| 关联裁定 | 待申请 #206（在 panorama 第 1993 行裁定#203 之后补录） |

### 1.2 历史脉络

| 时间 | 事件 |
|---|---|
| 2026-05-03 | `layer_vocabulary.yaml` 创建，确立 `data/infra_ops/...` 16 值语义命名体系作为 SSoT；同时 `doc_type_vocabulary.yaml` 等 24 个 vocabulary YAML 创建 |
| 2026-05-03 | `generate_derived_files.py` v1.0.0 创建（GATE-GENERATE, P2），声明派生链 vocabulary YAML → frontmatter-field-registry.md / architecture-contract.yaml / frontmatter-schema.json——**但路径常量从首日起就用连字符+错扩展名，同步从未生效** |
| 2026-05-03 前后 | `sync_yaml_to_depgraph.py` 的 `sync_vocabularies` 函数（#157）实现，但第 441 行读错 YAML 键（`field_name` vs `vocabulary_name`），DB 缓存写入脏值 |
| 2026-05-03 至今 | 3 个派生文件全靠人工维护；DB `field_vocabularies` 表脏值累积；`triage.py` 等生产代码硬编码副本各自漂移 |
| 2026-06-25 | 调研 Agent 发现根因，议题 #ARCH-008 浮现 |

### 1.3 影响范围概览

| 维度 | 数量 |
|---|---|
| 必改 Python 代码文件 | 7 |
| 必改 YAML/JSON/规则文件 | 8+ |
| 必改文档/索引文件 | 6+ |
| 必重生成派生文件 | 3 |
| 必清理 DB 表数据 | 1 表（field_vocabularies） |
| 必删孤儿模块 | 2（kb/triage.py、kb/pipeline/triage.py） |
| 已识别 Bug | 8 个（A~H） |
| 派生副本漂移位置 | 9 处（含 3 派生文件 + 3 triage.py + 1 g2_triage.yaml + 2 validator） |

---

## 第二部分：根因分析

### 2.1 Bug 全景（8 个 bug，A~H）

#### Bug A：路径常量错配（generate_derived_files.py:81-91）— P0 根因

| 行号 | 当前值 | 目标值 |
|---|---|---|
| [81](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L81) | `FIELD_REGISTRY_PATH = CATALOGS_DIR / "frontmatter-field-registry.md"` | `CATALOGS_DIR / "frontmatter_field_registry.yaml"` |
| [82](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L82) | `ARCH_CONTRACT_PATH = CONTRACTS_DIR / "architecture-contract.yaml"` | `CONTRACTS_DIR / "architecture_contract.yaml"` |
| [83](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L83) | `SCHEMA_JSON_PATH = SCHEMAS_DIR / "frontmatter-schema.json"` | `SCHEMAS_DIR / "frontmatter_schema.json"` |
| [86](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L86) | `"doc_type": "doc_type-vocabulary.yaml"` | `"doc_type": "doc_type_vocabulary.yaml"` |
| [87](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L87) | `"status": "status-vocabulary.yaml"` | `"status": "status_vocabulary.yaml"` |
| [88](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L88) | `"rule_form": "rule_form-vocabulary.yaml"` | `"rule_form": "rule_form_vocabulary.yaml"` |
| [89](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L89) | `"ttl": "ttl-vocabulary.yaml"` | `"ttl": "ttl_vocabulary.yaml"` |
| [90](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L90) | `"layer": "layer-vocabulary.yaml"` | `"layer": "layer_vocabulary.yaml"` |

**失效机制**：8 处路径常量全部用连字符 + 错扩展名（.md），磁盘上实际是 snake_case + .yaml/.json。每个 `_sync_*` 函数开头 `if not PATH.exists(): return False`（行 142/196/246）静默返回 False，主循环（行 338-358）打印"✅ 所有派生文件与 vocabulary YAML 一致"并 exit 0——形成**虚假绿灯**。

#### Bug B：键名错配（sync_yaml_to_depgraph.py:441）— P0 根因

| 行号 | 当前值 | 目标值 |
|---|---|---|
| [441](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py#L441) | `field_name = data.get("field_name", yaml_file.stem)` | `field_name = data.get("vocabulary_name") or yaml_file.stem.removesuffix("_vocabulary")` |

**失效机制**：24 个 vocabulary YAML 全部用 `vocabulary_name` 键（如 [doc_type_vocabulary.yaml:32](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml#L32) `vocabulary_name: doc_type`），无 `field_name` 键。fallback 到 `yaml_file.stem` → DB `field_vocabularies` 表写入 `doc_type_vocabulary`（而非 `doc_type`），下游按 `field_name='doc_type'` 查询时全部 miss。

**期望值确认**：`_archive/validate_enum_consistency.py:61-73` 的 `VOCAB_TO_FIELD` 映射表证明下游期望裸字段名 `doc_type` / `ttl` / `layer`（不带 `_vocabulary` 后缀）。

#### Bug C：enum_values apply 分支恒 False（generate_derived_files.py:175-177）— P1 隐藏 bug

| 行号 | 当前值 | 目标值 |
|---|---|---|
| [175-177](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L175-L177) | `if apply and "allowed_values" in field: field["allowed_values"] = [...]` | 增加 `elif apply and "enum_values" in field:` 分支：过滤 `enum_values` 中不在 vocab 的项，`changed = True` |

**失效机制**：`frontmatter_field_registry.yaml` 实际用 `enum_values`（含 `{value, description}` dict），不用 `allowed_values`。当前 apply 分支只处理 `allowed_values` 字段，对 `enum_values` 字段恒为 False → 即使修了 Bug A，apply 也永远不写回 `enum_values`。

#### Bug D：open() 缺写模式（generate_derived_files.py:182/227/286）— P1 崩溃 bug

| 行号 | 当前值 | 目标值 |
|---|---|---|
| [182](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L182) | `with open(tmp_path, encoding="utf-8") as f:` | `with open(tmp_path, "w", encoding="utf-8") as f:` |
| [227](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L227) | 同上 | 同上 |
| [286](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L286) | 同上 | 同上 |

**失效机制**：默认 `'r'` 模式，tmp 文件不存在时直接 `FileNotFoundError`，不被 `except PermissionError`（行 186/231/291）捕获 → 脚本崩溃，且 tmp 文件不被清理。

#### Bug E：schema_json oneOf 重写逻辑错（generate_derived_files.py:280）— P1 写错结构 bug

| 行号 | 当前值 | 目标值 |
|---|---|---|
| [280](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L280) | `prop["enum"] = [v for v in current_enum if isinstance(v, str) and v in vocab_set]` | 重写 `prop["oneOf"]`：从 `current_enum`（实际是 oneOf）过滤 `const` 不在 vocab 的项；删除 `enum` 键回退 |

**失效机制**：`frontmatter_schema.json` 用 `oneOf+const`（行 21-35 等），无 `enum` 键。当前 apply 会写一个**空 `enum` 键**到 prop，而真正的 oneOf 条目不被清理——既不修复漂移，又污染 schema 结构。

#### Bug F：异常捕获太窄（generate_derived_files.py:186/231/291）— P2 健壮性 bug

| 行号 | 当前值 | 目标值 |
|---|---|---|
| [186](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L186) | `except PermissionError:` | `except (PermissionError, OSError) as e:` + 在 finally 中 `if os.path.exists(tmp_path): os.remove(tmp_path)` |
| [231](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L231) | 同上 | 同上 |
| [291](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L291) | 同上 | 同上 |

**失效机制**：`FileNotFoundError`、`json.JSONDecodeError`、`yaml.YAMLError` 等不被捕获，tmp 文件不被清理，长期累积产生 `.tmp` 残留。

#### Bug G：sync_yaml_to_depgraph.py 无锁保护 — P3 并发安全 bug

| 位置 | 现状 | 修复目标 |
|---|---|---|
| [sync_yaml_to_depgraph.py](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py) 全文 | 仅依赖 sqlite3 事务 + 临时 DROP 只读触发器，无跨进程文件锁 | 引入跨进程文件锁（参考 [scripts/lock_files.py](file:///d:/ZephyrAlpha/scripts/lock_files.py) 的 `cmd_acquire`/`cmd_release`）。注：apply_depgraph.py 的 `_db_write_lock`（行 204）是 `threading.Lock` 进程内锁，不能解决跨进程并发，不可直接照搬 |

**失效机制**：与 `apply_depgraph.py` 并发可能竞争 DB 写入；与 `generate_project_depgraph.py` 并发可能竞争。是治理脚本中**唯一缺锁的 DB 写入者**。

#### Bug H：DB_PATH 不一致 — P3 配置 bug

| 位置 | 现状 | 修复目标 |
|---|---|---|
| [_shared/constants.py:117](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py#L117) | `DB_PATH: Path = REPO_ROOT / "data" / "databases" / "governance.db"` | 保留（这是 governance.db 路径） |
| [sync_yaml_to_depgraph.py:51](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py#L51) | `DB_PATH = r"D:\ZephyrAlpha\data\databases\depgraph.db"`（硬编码绝对路径） | 改为引用 `_shared.constants` 中的 depgraph.db 路径常量（需新增 DEPGRAPH_DB_PATH） |

**失效机制**：两个 `DB_PATH` 指向不同 DB（governance.db vs depgraph.db），是潜在不一致点；同时 sync 脚本用硬编码绝对路径，违反"全项目绝对路径"约定（虽合规但不可移植）。

### 2.2 派生文件不一致现状

#### 2.2.1 layer 字段（16 值 SSoT）

| 来源 | 值数量 | 与 SSoT 一致性 |
|---|---|---|
| [layer_vocabulary.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/layer_vocabulary.yaml)（SSoT） | 16 | — |
| [frontmatter_field_registry.yaml:180-196](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml#L180-L196) | 16 | ✓ 完全一致 |
| [architecture_contract.yaml:129-133](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml#L129-L133) | 16 | ✓ 完全一致 |
| [frontmatter_schema.json:50-70](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/schemas/frontmatter_schema.json#L50-L70) | **16** | ✗ 命名方案不同（l00-data-source 等带 L 编号长名，vs layer_vocabulary.yaml 的语义短名 data/infra_ops）+ 下划线/连字符混用（l10_governance_compliance、l13_experiment_pipeline 用下划线，其余用连字符）；值数与 SSoT 一致但命名方案完全不同，重生成后统一 |

#### 2.2.2 doc_type 字段（26 active + 7 deprecated SSoT）

| 来源 | 值数量 | 与 SSoT 一致性 |
|---|---|---|
| [doc_type_vocabulary.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml)（SSoT） | 26 active + 7 deprecated | — |
| frontmatter_field_registry.yaml | 13 | △ 仅含 01_policies_and_standards/ 子集（设计如此？需校验） |
| architecture_contract.yaml:113 | 13 | △ 同上 |
| frontmatter_schema.json:22-34 | 13 | △ 同上 |
| [triage.py:73-95](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L73-L95) `VALID_DOC_TYPES` | 22 | ✗ 含 4 个已 deprecated 值（`ai_governance`/`candidate_pool`/`discussion_draft`/`checklist`）+ 幽灵值 `adr`（YAML 中完全不存在）+ 缺 9 个 active 值（`operational_rule`/`protocol`/`vocabulary`/`contract`/`schema`/`architecture_view`/`declaration`/`gate`/`config`） |

### 2.3 硬编码副本漂移全景

#### 2.3.1 三份 triage.py 副本

| 文件 | module_id | 是否孤儿 | VALID_LAYERS 值数 | 漂移 |
|---|---|---|---|---|
| [src/zephyr/governance/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py) | MOD-DAT_triage | 否（仅测试用） | 14 | 缺 system-telemetry、simulation |
| [src/zephyr/governance/kb/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/triage.py) | MOD-DAT_triage | **是**（零消费者） | 12 唯一（含 2 重复） | 含非法值 `l10-compliance`/`l11_human_ai_interface`，缺 7 个合法值 |
| [src/zephyr/governance/kb/pipeline/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/pipeline/triage.py) | MOD-DAT_triage | **是**（零消费者） | 12 唯一 | 同上 + `Self` 未 import bug（行 194） |

**关键问题**：三份文件 `module_id=MOD-DAT_triage` 完全相同（三向冲突），但分属两个不同蓝图（MOD-KB-001 vs MOD-INF-009），MODULE 路径各不相同。

#### 2.3.2 Validator 硬编码

| 文件 | 行号 | 常量 | 值 | 问题 |
|---|---|---|---|---|
| [validate_rule_frontmatter.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/validate_rule_frontmatter.py) | 101 | `VALID_LAYER` | `{"L0", "L1", "L2", "L3"}` | 完全废弃格式（layer_vocabulary.yaml 注释明确"L1→废弃"） |
| [validate_blueprint_placement.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py) | 69 | `VALID_LAYERS` | `L00-L13 + cross_layer`（15 值） | 第三种格式，缺 `shared` |
| [validate_ssot.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_ssot.py) | 57 | `_get_valid_layers()` | `["l01"..."l13"]`（13 值） | 第四种格式，函数体是 stub |

#### 2.3.3 rule_enforcement/g2_triage.yaml

| 文件 | 行号 | 字段 | 值数 | 问题 |
|---|---|---|---|---|
| [src/zephyr/governance/rule_enforcement/g2_triage.yaml](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/g2_triage.yaml) | 124-142 | `valid_layers` | 18 | 含 `infra_runtime`、`pf_alloc` 不在 SSoT；与 triage.py 也不同步 |

#### 2.3.4 trae_*.yaml 规则文件本身的 frontmatter

| 文件 | 行号 | 当前值 | 问题 |
|---|---|---|---|
| [trae_015_arch_path_registration.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_015_arch_path_registration.yaml) | 4 | `layer: L1` | 不在 SSoT 16 值中 |
| [trae_016_arch_drift_detection.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml) | 4 | `layer: L1` | 同上 |
| [trae_043_meta_rule_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml) | 4 | `layer: L2` | 同上 |
| [trae_047_engineering_file_header.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml) | 4 | `layer: L1` | 同上 |

### 2.4 派生 vs. 缓存概念澄清

**关键澄清**：`field_vocabularies` 表的下游消费者现状：

| 位置 | 用途 | 是否查 field_name |
|---|---|---|
| [verify_final_delivery.py:69,78](file:///d:/ZephyrAlpha/scripts/governance/verify_final_delivery.py#L69) | `SELECT COUNT(*) FROM field_vocabularies` 检查行数 > 0 | **否**，仅检查行数 |
| 全项目其他位置 | — | **无任何 `SELECT ... WHERE field_name=...`** |

**结论**：当前 Bug B 不影响运行时功能（仅 DB 缓存脏数据），但违反 SSoT 硬约束（"DB 规则表为只读缓存"），且未来一旦有代码按 `field_name` 查询会立即失败。

---

## 第三部分：影响范围（受影响文件索引）

### 3.1 必改 Python 代码文件

| # | 绝对路径 | 行号 | 修改内容 | 优先级 |
|---|---|---|---|---|
| 1 | [scripts/governance/d3_metadata/generate_derived_files.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py) | 81-91, 175-177, 182, 186, 227, 231, 280, 286, 291 | Bug A/C/D/E/F 修复 | P0/P1/P2 |
| 2 | [scripts/governance/sync_yaml_to_depgraph.py](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py) | 51, 438, 441, 全文（锁保护） | Bug B/G/H 修复 + 清理脏值 | P0/P3 |
| 3 | [scripts/governance/_shared/constants.py](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py) | 117 后新增 | 新增 `DEPGRAPH_DB_PATH` 常量供 sync 引用 | P3 |
| 4 | [scripts/governance/d3_metadata/validate_rule_frontmatter.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/validate_rule_frontmatter.py) | 101 | `VALID_LAYER` 改为从 vocabulary YAML 动态加载（或直接用 SSoT 16 值） | P1 |
| 5 | [scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py) | 69 | `VALID_LAYERS` 改为从 vocabulary YAML 动态加载（同步改 _layer_to_dir_prefix 行 79-87） | P1 |
| 6 | [scripts/governance/d5_architecture/validators/validate_ssot.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_ssot.py) | 57 | `_get_valid_layers()` stub 补全 + 改为从 vocabulary YAML 加载 | P2 |
| 7 | [src/zephyr/governance/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py) | 73-113 | `VALID_DOC_TYPES`/`VALID_LAYERS` 改为从 vocabulary YAML 加载 + 删除幽灵值 `adr` + 补齐缺失值 | P1 |

### 3.2 必改规则文件（kebab→snake）

| # | 绝对路径 | 行号 | 修改内容 | 优先级 |
|---|---|---|---|---|
| 8 | [docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml) | 4, 235, 247, 249, 443, 455, 530, 610, 1080 | frontmatter `layer: L2`→`compliance`；vocab 文件名连字符→下划线；layer 数量 14→16；真源 triage.py→layer_vocabulary.yaml | P1 |
| 9 | [docs/01_policies_and_standards/rules/trae_015_arch_path_registration.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_015_arch_path_registration.yaml) | 4 | frontmatter `layer: L1`→`governance`（需先裁定该规则属哪个层） | P1 |
| 10 | [docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml) | 4 | 同上 | P1 |
| 11 | [docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml) | 4 | 同上 | P1 |
| 12 | [docs/01_policies_and_standards/rules/trae_044_compliance_audit.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_044_compliance_audit.yaml) | 336 | vocab 数量 12→25 修正 | P2 |
| 13 | [src/zephyr/governance/rule_enforcement/g2_triage.yaml](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/g2_triage.yaml) | 124-142 | `valid_layers` 18 值→16 值（与 layer_vocabulary.yaml 对齐） | P1 |

### 3.3 必改 Registry / 派生文件

| # | 绝对路径 | 行号 | 修改内容 | 优先级 |
|---|---|---|---|---|
| 14 | [docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml) | 23-25（注释）+ 全文 `derived_from` | kebab→snake 路径修正（11 处 derived_from 字段） | P2 |
| 15 | [docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml) | 5, 60（注释）+ 全文 `derived_from` | kebab→snake 路径修正 | P2 |
| 16 | [docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml) | 40, 144 | kebab→snake 路径修正（且第 144 行自引用错误） | P2 |
| 17 | [docs/01_policies_and_standards/_registry/vocabularies/](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/) | 全部 26 个 YAML（24 个 *_vocabulary.yaml + glossary.yaml + terminology_mapping.yaml） | 检查所有 `derived_from` 字段中的 kebab 路径并修正 | P2 |
| 18 | [docs/01_policies_and_standards/_registry/schemas/frontmatter_schema.json](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/schemas/frontmatter_schema.json) | 4（注释）+ 50-70（layer oneOf） | 整体重生成（修复 Bug A/E 后跑 `--apply`） | P0 |
| 19 | [docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml) | 全文 | 整体重生成（修复 Bug A 后跑 `--apply`） | P0 |
| 20 | [docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml) | 全文 | 整体重生成（修复 Bug A/C 后跑 `--apply`） | P0 |

### 3.4 必删孤儿模块

| # | 绝对路径 | 删除理由 | 优先级 |
|---|---|---|---|
| 21 | [src/zephyr/governance/kb/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/triage.py) | 孤儿模块（零消费者）+ 含非法值 + module_id 三向冲突 | P1 |
| 22 | [src/zephyr/governance/kb/pipeline/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/pipeline/triage.py) | 同上 + `Self` 未 import bug | P1 |
| 23 | [src/zephyr/governance/kb/__init__.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/__init__.py) | 90/145 行 `__all__` 声明但无 import（幽灵导出）—需评估是否一并清理 | P2 |
| 24 | [src/zephyr/governance/kb/pipeline/__init__.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/pipeline/__init__.py) | 同上 | P2 |

### 3.5 必改 DB 数据（清理脏值）

| # | DB 表 | 操作 | 优先级 |
|---|---|---|---|
| 25 | `depgraph.db.field_vocabularies` | DELETE 旧脏值（`field_name LIKE '%_vocabulary'`）→ 重跑 sync_vocabularies 写入正确值 | P0 |

### 3.6 必改文档 / 索引

| # | 绝对路径 | 修改内容 | 优先级 |
|---|---|---|---|
| 26 | [.trae/rules/onboarding_detail.md](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md) | 补充 vocabulary 同步机制说明 + GATE-GENERATE 门禁介绍 | P2 |
| 27 | [docs/02_enterprise_architecture/dependency_architecture_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/dependency_architecture_panorama.md) | 补录裁定#204/#205 + 新议题 #ARCH-008 + 裁定#206 | P1 |
| 28 | [docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md) | 附录 B 追加议题 #ARCH-008 | P2 |
| 29 | [scripts/governance/d5_architecture/generators/generate_navigation_index.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_navigation_index.py) | 154 行硬编码"43个域"→动态从 DB stats 读取 domain_count | P3 |
| 30 | [docs/02_enterprise_architecture/00_overview_entry/navigation_index.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/00_overview_entry/navigation_index.md) | 重生成（修复 29 后） | P3 |

### 3.7 全项目 kebab 路径引用清理（合并到一次清理）

经 Grep 全项目发现以下位置仍用连字符引用派生文件路径（需统一改为下划线）：

| # | 绝对路径 | 行号 | 引用类型 |
|---|---|---|---|
| 31 | [src/zephyr/governance/registry_adapter.py](file:///d:/ZephyrAlpha/src/zephyr/governance/registry_adapter.py) | 585-586 | `YamlListAdapter("REG-FRONTMATTER-001", "frontmatter-field-registry.md", ...)` |
| 32 | [src/zephyr/infrastructure/asset_inventory/registry_adapter.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/asset_inventory/registry_adapter.py) | 583-584 | 同上（重复实现） |
| 33 | [config/blueprint_routing.yaml](file:///d:/ZephyrAlpha/config/blueprint_routing.yaml) | 814 | 字符串路径 |
| 34 | [docs/02_enterprise_architecture/target_architecture/architecture_model/module_id_registry.yaml](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/architecture_model/module_id_registry.yaml) | 176 | `path:` 字段 |
| 35 | [docs/01_policies_and_standards/_registry/catalogs/registry_consistency_contract.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/registry_consistency_contract.yaml) | 128, 130 | 登记表自描述 |
| 36 | [docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml) | 1239 | 字符串 |
| 37 | [docs/01_policies_and_standards/_registry/catalogs/document_metadata_index_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/document_metadata_index_registry.yaml) | 1242 | 字符串 |
| 38 | [docs/01_policies_and_standards/rules/trae_033_module_registration_sync.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_033_module_registration_sync.yaml) | 83 | 字符串 |
| 39 | [docs/03_modules/_domain_governance/registry_governance/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/registry_governance/blueprint.md) | 640 | 字符串 |
| 40 | [scripts/governance/validate_module_id_naming.py](file:///d:/ZephyrAlpha/scripts/governance/validate_module_id_naming.py) | 9 | 注释 MODIFY-GUARD |
| 41 | [scripts/governance/add_file_headers.py](file:///d:/ZephyrAlpha/scripts/governance/add_file_headers.py) | 11 | 注释 MODIFY-GUARD |
| 42 | [scripts/governance/d5_architecture/validators/validate_architecture_contract_internal.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_architecture_contract_internal.py) | 66 | Path 引用（孤儿脚本，路径错→EXIT_ERROR） |
| 43 | [scripts/governance/script_manifest.yaml](file:///d:/ZephyrAlpha/scripts/governance/script_manifest.yaml) | 1880, 1889 | manifest 登记 |
| 44 | [scripts/script_manifest.yaml](file:///d:/ZephyrAlpha/scripts/script_manifest.yaml) | 2258-2259 | manifest 登记（重复） |
| 45 | [docs/01_policies_and_standards/_registry/vocabularies/](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/) | verifiability:18, stability:19, scope:19, language:18, created_by:18, classification:19 | 6 处 vocabulary YAML 自描述中 `source: "... + architecture-contract.yaml frontmatter_schema"` |
| 46 | [data/scans/raw_asset_scan.json](file:///d:/ZephyrAlpha/data/scans/raw_asset_scan.json) | 28930-28932, 29150-29152 | 扫描快照历史脏数据（**磁盘不存在 kebab 文件**） |
| 47 | [data/classified/classified_assets.json](file:///d:/ZephyrAlpha/data/classified/classified_assets.json) | 43408, 43738 | 同上 |

### 3.7.1 第 2 轮审查补充发现（kebab 引用遗漏）

经第 2 轮全项目 Grep 复查，3.7 节清单（#31-#47）遗漏以下活文件（已抽样验证确实含需修改的 kebab 路径引用）：

| # | 绝对路径 | 引用类型 | 备注 |
|---|---|---|---|
| 48 | [scripts/governance/d11_compliance/validate_vocabulary_coverage.py](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/validate_vocabulary_coverage.py) | 行 23 `*-vocabulary.yaml` glob 模式 | 扫描 vocabulary 文件的模式匹配，需改 `*_vocabulary.yaml` |
| 49 | [scripts/governance/d3_metadata/validate_architecture.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/validate_architecture.py) | 行 62 `architecture-contract.yaml` 路径常量 | 路径错导致找不到文件 |
| 50 | [docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml) | 行 569 `architecture-contract.yaml` | registry 自描述 |
| 51 | [docs/01_policies_and_standards/rules/trae_041_meta_rule_classification.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_041_meta_rule_classification.yaml) | 行 490 `frontmatter-schema.json` | 规则文件引用 |
| 52 | [docs/01_policies_and_standards/_registry/schemas/index.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/schemas/index.md) | 行 22 `frontmatter-schema.json` | 索引文件 |
| 53 | [docs/01_policies_and_standards/_registry/vocabularies/index.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/index.md) | kebab 引用 | 索引文件 |
| 54 | [docs/01_policies_and_standards/_registry/contracts/index.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/index.md) | kebab 引用 | 索引文件 |
| 55 | [docs/01_policies_and_standards/_registry/catalogs/script_health_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/script_health_registry.yaml) | kebab 引用 | registry 自描述 |
| 56 | [docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml) | kebab 引用 | registry 总索引 |
| 57 | [docs/01_policies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml) | kebab 引用 | registry 自描述 |
| 58 | [scripts/governance/dm105_depgraph_triage.py](file:///d:/ZephyrAlpha/scripts/governance/dm105_depgraph_triage.py) | kebab 引用 | 治理脚本 |
| 59 | [scripts/governance/d1_structure/batch_create_index_md.py](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/batch_create_index_md.py) | kebab 引用 | 治理脚本 |
| 60 | [docs/01_policies_and_standards/rules/trae_029_doc_operation_security.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_029_doc_operation_security.yaml) | kebab 引用 | 规则文件 |
| 61 | [docs/01_policies_and_standards/index.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/index.md) | kebab 引用 | 目录索引 |
| 62 | [data/asset_index/project_entity_depgraph_v3_domain_draft.yaml](file:///d:/ZephyrAlpha/data/asset_index/project_entity_depgraph_v3_domain_draft.yaml) | kebab 引用 | 草稿数据（评估是否保留） |
| 63 | [data/security_baselines/scan_mtime_cache.json](file:///d:/ZephyrAlpha/data/security_baselines/scan_mtime_cache.json) | kebab 引用 | 扫描缓存（评估是否保留） |
| 64 | [.trae/documents/ttl_task_bound_extension_plan.md](file:///d:/ZephyrAlpha/.trae/documents/ttl_task_bound_extension_plan.md) | kebab 引用 | 计划文档 |
| 65 | [docs/09_audit/research_notes/blueprint_discussion_audit_division_plan.md](file:///d:/ZephyrAlpha/docs/09_audit/research_notes/blueprint_discussion_audit_division_plan.md) | kebab 引用 | 审计研究笔记 |

**执行建议**：上述 #48-#65 共 18 个文件为第 2 轮审查补充发现。执行时需用以下命令重新生成完整清单（因 Grep 结果可能随代码变更而变化）：

```bash
# 执行时跑此命令获取最新完整清单（排除知识库/备份/扫描快照/_archive/session_logs）
#
# 注意：必须用 rg（ripgrep），不能用 `python scripts/git_guard.py grep`！
# 原因：git_guard.py 的 DANGEROUS_SUBCOMMANDS 不含 grep，会透传为 `git grep`——
#   (1) 仅搜 git-tracked files，漏掉 untracked 活文件；
#   (2) 不支持 \| 语法（git grep 用 --or 逻辑）；
#   (3) 不支持 -rn、--include、多目录参数（语法不同）。
rg -n "frontmatter-field-registry|architecture-contract|frontmatter-schema|doc_type-vocabulary|status-vocabulary|rule_form-vocabulary|ttl-vocabulary|layer-vocabulary" \
  -g "*.py" -g "*.yaml" -g "*.json" -g "*.md" \
  d:/ZephyrAlpha/src d:/ZephyrAlpha/scripts d:/ZephyrAlpha/docs d:/ZephyrAlpha/config d:/ZephyrAlpha/.trae \
  | rg -v "_archive|data/backups|data/scans|data/classified|08_knowledge|session_logs"
```

### 3.8 受影响文件汇总统计

| 类别 | 文件数 | 必改 | 必重生成 | 必删 | 必清理 |
|---|---|---|---|---|---|
| Python 代码 | 7+3 | 10 | — | 2~4 | — |
| 规则文件 (trae_*.yaml + g2) | 6+2 | 8 | — | — | — |
| 派生文件 | 3 | — | 3 | — | — |
| Registry 文件 | 5+5 | 10+ | — | — | — |
| DB 表 | 1 | — | — | — | 1 |
| 文档/索引 | 5+5 | 10+ | — | — | — |
| kebab 引用清理 | 17+18 | 35+ | — | — | — |
| **合计** | **62+** | **62+** | **3** | **2~4** | **1** |

---

## 第四部分：修复方案

### 4.1 修复策略总览

采用**分层修复 + 阶段验收**策略，遵循"先修工具，再用工具修数据，最后修文档"原则：

```
阶段 1（P0）：修复 generate_derived_files.py 的 Bug A/C/D/E/F
   ↓
阶段 2（P0）：修复 sync_yaml_to_depgraph.py 的 Bug B + 清理脏值
   ↓
阶段 3（P0）：重生成 3 个派生文件（用修好的工具）
   ↓
阶段 4（P1）：修复 4 个 validator 的硬编码 layer
   ↓
阶段 5（P1）：处理 3 份 triage.py（修主版 + 删孤儿）
   ↓
阶段 6（P1）：修复 trae_*.yaml 规则文件的 frontmatter layer（含 layer 命名体系裁定）
   ↓
阶段 7（P2）：全项目 kebab 路径清理（17+ 处）
   ↓
阶段 8（P2）：文档与索引同步
   ↓
阶段 9（P2）：补单元测试 + 接入 pre-commit GATE-GENERATE hook
   ↓
阶段 10（P3）：sync_yaml_to_depgraph.py 锁保护 + DB_PATH 统一（Bug G/H）
```

### 4.2 layer 命名体系裁定（议题 #ARCH-009）

修复 trae_*.yaml frontmatter layer 之前需先裁定 layer 命名体系：

**裁定选项**：

| 方案 | 描述 | 优点 | 缺点 |
|---|---|---|---|
| **方案 A（推荐）** | 全面采纳 layer_vocabulary.yaml 的 16 值语义命名（`data/infra_ops/...`），废弃 `L0/L1/L2/L3` 与 `L00-L13` 两套旧格式 | 与 SSoT 一致；语义清晰；AI 易理解 | 需修 4 个 trae_*.yaml + 2 个 validator + 1 个 blueprint_placement 工具的 `_layer_to_dir_prefix` |
| 方案 B | 反向：让 layer_vocabulary.yaml 改用 L00-L13 格式 | 不动 validator | 违反 SSoT 已确立的语义命名；废弃已有 5 个月稳定运行的 vocabulary |
| 方案 C | 双轨：layer 用语义名，layer_id 用 L0_xxx（即现状） | 不动 layer_id | 但需废弃 validator 中 L0/L1/L2/L3 与 L00-L13，等于方案 A |

**推荐方案 A**：layer 字段统一用 layer_vocabulary.yaml 的 16 值。layer_id 字段保持现状（L0_infrastructure/L1_foundation/L2_domain/L3_application，CHECK 约束已落地）。

**附带裁定 #ARCH-010：apply_depgraph.py ALLOWED_LAYERS 与 DB CHECK 对齐**
- [apply_depgraph.py:1679](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L1679) `ALLOWED_LAYERS` 删除 `L1_platform`、新增 `L3_application`，与 DB CHECK 触发器一致（裁定 #203-C 落地时遗漏的代码同步问题）

### 4.3 triage.py 三份副本处理方案

**方案对比**：

| 方案 | 描述 | 优点 | 缺点 |
|---|---|---|---|
| **方案 B（推荐）** | 保持 `governance/triage.py` 硬编码，但扩展 `generate_derived_files.py` 增加 `_sync_triage_py()` 目标 + 启动时 assert 与 YAML 一致 | 零运行时影响；CI 层面新增检查；现有测试无需改造 | triage.py 作为 src 文件成为"派生目标"是新范畴 |
| 方案 A | 改为运行时从 YAML 读取（`@lru_cache` 缓存） | 物理上不可能漂移 | 跨树依赖（src→scripts）；测试需注入 YAML 路径；性能 I/O |
| 方案 C | 保留硬编码 + 仅加单元测试断言 | 最简单 | 漂移靠测试发现，无自动同步 |

**推荐方案 B** + 删除两份孤儿副本：

1. **删除** [src/zephyr/governance/kb/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/triage.py) 和 [src/zephyr/governance/kb/pipeline/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/pipeline/triage.py)（零消费者 + 含非法值 + module_id 三向冲突 + Self 未 import bug）
2. **修复** [src/zephyr/governance/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py)：
   - 删除幽灵值 `adr`
   - 删除 4 个已 deprecated 值（`ai_governance`/`candidate_pool`/`discussion_draft`/`checklist`）
   - 补齐缺失的 9 个 active 值（`operational_rule`/`protocol`/`vocabulary`/`contract`/`schema`/`architecture_view`/`declaration`/`gate`/`config`）
   - `VALID_LAYERS` 补齐 `system-telemetry`/`simulation`
3. **扩展** `generate_derived_files.py` 增加 `_sync_triage_py()` 同步目标（与 `_sync_field_registry` 同级）
4. **删除** [data/unregistered_modules_registry.md:493](file:///d:/ZephyrAlpha/data/unregistered_modules_registry.md) 陈旧条目 `from zephyr.governance.triage import Triage`（实际是 TriageGate）

### 4.4 关键架构决定

#### 4.4.1 `field_vocabularies` 表主键确认（待执行时验证）

修复 Bug B 后，`sync_vocabularies`（写 source_yaml=各 vocabulary 文件名）与 `sync_frontmatter_field_registry`（写 source_yaml='frontmatter_field_registry.yaml'）会写**相同 field_name**（如 `doc_type`）。需在执行时确认表主键定义：

```bash
# 验证命令（执行时跑）
python -c "import sqlite3; c=sqlite3.connect(r'd:\ZephyrAlpha\data\databases\depgraph.db'); print(list(c.execute('PRAGMA table_info(field_vocabularies)')))"
```

若主键含 `source_yaml`：两者共存，无冲突。  
若主键仅 `(field_name, value)`：后者覆盖前者，需在 sync_all 调用顺序中调整（行 942 sync_vocabularies 在行 947 sync_frontmatter_field_registry 之前，registry 会覆盖 vocab，但 registry 数据本就源自 vocab，影响可接受）。

**预案**：若需保留两源，建议在 `sync_vocabularies` 行 444-459 INSERT 前加 `DELETE FROM field_vocabularies WHERE source_yaml != 'frontmatter_field_registry.yaml'`（只清理 vocab 来源行，保留 registry 来源行）。

#### 4.4.2 `_shared.yaml_utils.load_yaml` vs `sync_yaml_to_depgraph.py` 自定义版

两个 `load_yaml` 行为不同：
- [`_shared/yaml_utils.py:30`](file:///d:/ZephyrAlpha/scripts/governance/_shared/yaml_utils.py#L30)：接收绝对路径，文件不存在**抛 FileNotFoundError**
- [`sync_yaml_to_depgraph.py:68-75`](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py#L68-L75)：接收相对路径，文件不存在**打印警告并返回 {}**

**决定**：保留两份实现，但 sync 脚本的宽容版用于"vocabulary 缺失不阻断 sync 全流程"，`_shared` 严格版用于"派生生成器需明确报错"。在方案文档中记录此差异。

---

## 第五部分：施工流程（动作级）

### 5.1 阶段 0：前置准备与备份

#### 5.1.1 任务认领与锁

```bash
# 1. 认领任务卡（通过 TaskRepository API；模块路径 src/zephyr/governance/persistence/task_repo.py）
#    注：无独立 task_repo.py CLI 脚本；任务卡需先用 repo.create() 创建（见第九部分任务卡清单）
#    TaskRepository 真实位置在 src/zephyr/governance/task_repo.py，persistence/task_repo.py 是代理模块
#    构造函数签名（task_repo.py:608）：
#      def __init__(self, db_path: Path|str|None = None, *,
#                  auto_init: bool = True, gate_dir=None, project_root=None, enable_gate: bool = True)
#    参数名是 db_path（不是 governance_db）；默认 DB_PATH 已指向 governance.db（sqlite_schema.py:76）
#    transition 签名（task_repo.py:1463）：
#      def transition(self, task_id: str, to_status: TaskStatus|str, *,
#                     session_id=None, waiting_for=None, note=None) -> Task
#    to_status 接受 str（会自动 TaskStatus(str) 转换）
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.persistence.task_repo import TaskRepository
repo = TaskRepository(db_path=r'd:\ZephyrAlpha\data\databases\governance.db')
repo.transition('OPS-2026062621', 'IN_PROGRESS')
print('认领成功: OPS-2026062621')
"

# 2. 获取 depgraph.db 文件锁（与并发 session 隔离）
#    lock_files.py 在 scripts/ 根目录；CLI: acquire <file_path> <owner_id> --task <desc>
python scripts/lock_files.py acquire data/databases/depgraph.db vocab-sync-2621 --task "vocabulary sync chain repair (#ARCH-008)"
```

#### 5.1.2 git 备份

```bash
# 3. 备份当前 depgraph.db（trae_054 STEP0 合规）
python scripts/git_guard.py add data/databases/depgraph.db
python scripts/git_guard.py commit -m "backup: depgraph.db before vocabulary sync chain repair (#ARCH-008)"
```

**验证**：
```bash
python scripts/git_guard.py log --oneline -1
# 期望输出：最新 commit hash + "backup: depgraph.db before vocabulary sync chain repair (#ARCH-008)"
```

**回滚**：
```bash
# 若后续步骤失败需回滚 DB
python scripts/git_guard.py checkout HEAD~1 -- data/databases/depgraph.db
```

#### 5.1.3 验证 field_vocabularies 表主键

```bash
# 4. 确认表结构
python -c "import sqlite3; c=sqlite3.connect(r'd:\ZephyrAlpha\data\databases\depgraph.db'); print('Columns:', list(c.execute('PRAGMA table_info(field_vocabularies)'))); print('PK:', list(c.execute('PRAGMA index_list(field_vocabularies)')))"
```

记录输出到施工日志，决定 4.4.1 预案是否启用。

---

### 5.2 阶段 1：修复 generate_derived_files.py（Bug A/C/D/E/F）

#### 5.2.1 修复 Bug A（路径常量，行 81-91）

**动作 1**：用 Edit 工具修改 [generate_derived_files.py:81-83](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L81-L83)

```python
# 修改前（行 81-83）
FIELD_REGISTRY_PATH = CATALOGS_DIR / "frontmatter-field-registry.md"
ARCH_CONTRACT_PATH = CONTRACTS_DIR / "architecture-contract.yaml"
SCHEMA_JSON_PATH = SCHEMAS_DIR / "frontmatter-schema.json"

# 修改后
FIELD_REGISTRY_PATH = CATALOGS_DIR / "frontmatter_field_registry.yaml"
ARCH_CONTRACT_PATH = CONTRACTS_DIR / "architecture_contract.yaml"
SCHEMA_JSON_PATH = SCHEMAS_DIR / "frontmatter_schema.json"
```

**动作 2**：用 Edit 工具修改 [generate_derived_files.py:86-90](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L86-L90)

```python
# 修改前
VOCAB_FIELD_MAP = {
    "doc_type": "doc_type-vocabulary.yaml",
    "status": "status-vocabulary.yaml",
    "rule_form": "rule_form-vocabulary.yaml",
    "ttl": "ttl-vocabulary.yaml",
    "layer": "layer-vocabulary.yaml",
}

# 修改后
VOCAB_FIELD_MAP = {
    "doc_type": "doc_type_vocabulary.yaml",
    "status": "status_vocabulary.yaml",
    "rule_form": "rule_form_vocabulary.yaml",
    "ttl": "ttl_vocabulary.yaml",
    "layer": "layer_vocabulary.yaml",
}
```

#### 5.2.2 修复 Bug D（open 缺 "w" 模式，行 182/227/286）

**动作 3**：用 Edit 工具修改 [行 182](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L182)

```python
# 修改前
with open(tmp_path, encoding="utf-8") as f:

# 修改后
with open(tmp_path, "w", encoding="utf-8") as f:
```

**动作 4**：同上修改 [行 227](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L227)

**动作 5**：同上修改 [行 286](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L286)

#### 5.2.3 修复 Bug C（enum_values apply 分支，行 175-178）

**动作 6**：用 Edit 工具修改 [行 175-178](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L175-L178)

```python
# 修改前
if apply and "allowed_values" in field:
    field["allowed_values"] = [v for v in field.get("allowed_values", []) if str(v) in vocab_set]
    changed = True

# 修改后
if apply and "allowed_values" in field:
    field["allowed_values"] = [v for v in field.get("allowed_values", []) if str(v) in vocab_set]
    changed = True
elif apply and "enum_values" in field:
    field["enum_values"] = [
        ev for ev in field.get("enum_values", [])
        if (isinstance(ev, dict) and str(ev.get("value") or ev.get("id") or "") in vocab_set)
        or (isinstance(ev, str) and ev in vocab_set)
    ]
    changed = True
```

#### 5.2.4 修复 Bug E（schema_json oneOf 重写，行 277-281）

**动作 7**：用 Edit 工具修改 [行 277-281](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L277-L281)

```python
# 修改前
if extra:
    _drift(f"schema_json.{field_name}: 多出 {len(extra)} 个不在 vocabulary 中的值: {sorted(extra)[:5]}")
    if apply:
        prop["enum"] = [v for v in current_enum if isinstance(v, str) and v in vocab_set]
        changed = True

# 修改后
if extra:
    _drift(f"schema_json.{field_name}: 多出 {len(extra)} 个不在 vocabulary 中的值: {sorted(extra)[:5]}")
    if apply:
        # 处理 enum 数组形式
        if "enum" in prop:
            prop["enum"] = [v for v in current_enum if isinstance(v, str) and v in vocab_set]
            changed = True
        # 处理 oneOf+const 形式（frontmatter_schema.json 实际用此格式）
        if "oneOf" in prop:
            new_one_of = [
                item for item in prop["oneOf"]
                if isinstance(item, dict)
                and str(item.get("const") or "") in vocab_set
            ]
            if len(new_one_of) != len(prop["oneOf"]):
                prop["oneOf"] = new_one_of
                changed = True
```

#### 5.2.5 修复 Bug F（异常捕获扩展 + tmp 清理，行 179-191/224-236/283-296）

**动作 8**：用 Edit 工具修改三处 try/except 块。以 [行 179-191](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L179-L191) 为例：

```python
# 修改前
if changed and apply:
    tmp_path = f"{FIELD_REGISTRY_PATH}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, encoding="utf-8") as f:   # ← 已在动作 3 改为 "w"
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, FIELD_REGISTRY_PATH)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

# 修改后
if changed and apply:
    tmp_path = f"{FIELD_REGISTRY_PATH}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, FIELD_REGISTRY_PATH)
    except (PermissionError, OSError) as e:
        print(f"  ⚠️ 写回 {FIELD_REGISTRY_PATH.name} 失败: {e}")
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
```

**动作 9**：同上修改 [行 224-236](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L224-L236)（arch_contract）

**动作 10**：同上修改 [行 283-296](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/generate_derived_files.py#L283-L296)（schema_json），注意 `json.dump` 而非 `yaml.dump`

#### 5.2.6 验证阶段 1

```bash
# 验证修复后脚本能正常加载（不崩）
python scripts/governance/d3_metadata/generate_derived_files.py --check

# 期望输出：
# - 不再打印"vocabulary 为空或不存在，跳过"
# - 报告 5 个字段的实际漂移（layer/schema_json 等）
# - exit 1（EXIT_FINDINGS，因为派生文件与 vocabulary 长期未同步）
```

**回滚**：
```bash
python scripts/git_guard.py checkout HEAD -- scripts/governance/d3_metadata/generate_derived_files.py
```

---

### 5.3 阶段 2：修复 sync_yaml_to_depgraph.py（Bug B）

#### 5.3.1 修复 Bug B（键名错配，行 441）

**动作 11**：用 Edit 工具修改 [sync_yaml_to_depgraph.py:441](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py#L441)

```python
# 修改前
field_name = data.get("field_name", yaml_file.stem)

# 修改后
field_name = data.get("vocabulary_name") or yaml_file.stem.removesuffix("_vocabulary")
```

**说明**：
- 优先读 `vocabulary_name` 键（24 个 vocabulary YAML 全部用此键）
- 回退时去掉 `_vocabulary` 后缀（如 `doc_type_vocabulary` → `doc_type`），保证健壮性

#### 5.3.2 添加脏值清理（行 438 之前）

**动作 12**：用 Edit 工具在 [行 438](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py#L438) `synced = 0` 之前插入：

```python
# 插入位置：行 437（return）之后，行 438（synced = 0）之前
# 清理历史脏值（Bug B 修复前写入的 *_vocabulary field_name）
cur.execute(
    "DELETE FROM field_vocabularies WHERE source_yaml != 'frontmatter_field_registry.yaml'"
)
print(f"  清理 {cur.rowcount} 个历史脏值行（Bug B 修复前写入的 *_vocabulary field_name）")
```

**说明**：`sync_frontmatter_field_registry`（行 947，在 sync_vocabularies 之后）会重新写入 registry 来源的行，所以删除 vocab 来源行不影响 registry 数据完整性。

#### 5.3.3 验证阶段 2

```bash
# 验证修复后 sync 能正确读取 vocabulary_name
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from sync_yaml_to_depgraph import load_yaml
data = load_yaml('_registry/vocabularies/doc_type_vocabulary.yaml')
print('vocabulary_name:', data.get('vocabulary_name'))
print('field_name (旧):', data.get('field_name'))
"

# 期望输出：
# vocabulary_name: doc_type
# field_name (旧): None
```

**回滚**：
```bash
python scripts/git_guard.py checkout HEAD -- scripts/governance/sync_yaml_to_depgraph.py
```

---

### 5.4 阶段 3：重生成 3 个派生文件 + 清理 DB 脏值

#### 5.4.1 重生成派生文件

**动作 13**：运行修好的 generate_derived_files.py --apply

```bash
python scripts/governance/d3_metadata/generate_derived_files.py --apply

# 期望输出：
# - 报告每个字段的同步状态
# - frontmatter_field_registry.yaml / architecture_contract.yaml / frontmatter_schema.json 被重写
# - exit 0
```

**验证**：
```bash
# 检查 frontmatter_schema.json 的 layer oneOf 是否重写为 SSoT 16 值
python -c "
import json
data = json.load(open(r'd:\ZephyrAlpha\docs\01_policies_and_standards\_registry\schemas\frontmatter_schema.json', encoding='utf-8'))
layer_prop = data.get('properties', {}).get('layer', {})
one_of = layer_prop.get('oneOf', [])
print(f'layer oneOf 值数: {len(one_of)}')
print('前 5 值:', [item.get('const') for item in one_of[:5]])
"

# 期望输出：
# layer oneOf 值数: 16
# 前 5 值: ['data', 'infra_ops', 'factor', 'signal', 'risk']
```

#### 5.4.2 重跑 sync_yaml_to_depgraph.py 清理 DB

**动作 14**：

```bash
python scripts/governance/sync_yaml_to_depgraph.py

# 期望输出：
# - "清理 N 个历史脏值行（Bug B 修复前写入的 *_vocabulary field_name）"
# - "同步 N 个词汇值"
# - exit 0
```

**验证**：
```bash
# 检查 field_vocabularies 表不再有 *_vocabulary 后缀的脏值
python -c "
import sqlite3
c = sqlite3.connect(r'd:\ZephyrAlpha\data\databases\depgraph.db')
rows = c.execute('SELECT DISTINCT field_name FROM field_vocabularies ORDER BY field_name').fetchall()
print('当前 field_name 列表:')
for r in rows:
    print(f'  {r[0]}')
dirty = [r for r in rows if '_vocabulary' in r[0]]
print(f'脏值数量: {len(dirty)}')
"

# 期望输出：脏值数量: 0
```

**回滚**：
```bash
# 回滚 DB
python scripts/git_guard.py checkout HEAD~1 -- data/databases/depgraph.db
# 回滚派生文件
python scripts/git_guard.py checkout HEAD~1 -- docs/01_policies_and_standards/_registry/
```

---

### 5.5 阶段 4：修复 4 个 validator 硬编码 layer

#### 5.5.1 修复 validate_rule_frontmatter.py（行 101）

**动作 15**：用 Edit 工具修改 [validate_rule_frontmatter.py:101-104](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/validate_rule_frontmatter.py#L101-L104)

```python
# 修改前
VALID_LAYER = {"L0", "L1", "L2", "L3"}
VALID_STABILITY = {"frozen", "stable", "evolving", "volatile"}
VALID_SAFETY = {"H", "M", "L"}
VALID_AUTONOMY = {"immutable_core", "human_gated", "ai_modifiable"}

# 修改后（从 vocabulary YAML 动态加载 — 使用公共 loader，禁止复制局部 _load_valid_values）
import sys
from pathlib import Path
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.yaml_utils import load_vocabulary_values

VALID_LAYER = load_vocabulary_values("layer_vocabulary.yaml", fallback_key="id")
VALID_STABILITY = load_vocabulary_values("stability_vocabulary.yaml", fallback_key="id")
VALID_SAFETY = load_vocabulary_values("safety_level_vocabulary.yaml", fallback_key="id")
VALID_AUTONOMY = load_vocabulary_values("ai_autonomy_vocabulary.yaml", fallback_key="id")
```

**注意**：自 v1.1.0 起，禁止各脚本复制 `_load_valid_values()` 局部函数——**MUST** 使用公共 `load_vocabulary_values()`（canonical = `scripts/governance/_shared/yaml_utils.py`，capability_id = `vocabulary_values_loader`）。理由：消除跨脚本复制粘贴（SCRIPT-QUALITY-001 D-D-05）+ 词表唯一真源（trae_060 §2）。配套门禁 GATE-VOCAB 会检测局部 loader 模式。详见 AGENTS.md §7「词表合法值加载规范」。

#### 5.5.2 修复 validate_blueprint_placement.py（行 69 + 行 79-87）

**动作 16**：用 Edit 工具修改 [validate_blueprint_placement.py:69](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L69)

```python
# 修改前
VALID_LAYERS: frozenset[str] = frozenset({f"L{i:02d}" for i in range(0, 14)} | {"cross_layer"})

# 修改后（动态加载）
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))  # scripts/governance/
from _shared.constants import GOV_DOCS_DIR
import yaml
_LAYER_VOCAB = GOV_DOCS_DIR / "_registry" / "vocabularies" / "layer_vocabulary.yaml"
_LAYER_DATA = yaml.safe_load(_LAYER_VOCAB.read_text(encoding="utf-8")) if _LAYER_VOCAB.exists() else {"values": []}
VALID_LAYERS: frozenset[str] = frozenset(
    str(v.get("value")) for v in _LAYER_DATA.get("values", []) if isinstance(v, dict)
)
```

**动作 17**：同步修改 [_layer_to_dir_prefix 行 79-87](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L79-L87)

```python
# 修改前（磁盘实际代码）
def _layer_to_dir_prefix(layer: str) -> str | None:
    """_layer_to_dir_prefix implementation."""
    if layer.startswith("L") and len(layer) == 3:
        try:
            nn = int(layer[1:])
            return f"l{nn:02d}_"
        except ValueError:
            return None
    return None
# 注：当前不处理 cross_layer/shared（返回 None），且仅识别 L00-L13 格式

# 修改后（删除 L00-L13 推导逻辑，改为查 layer_vocabulary.yaml 的 dir_prefix 字段；
# 若 vocabulary 无 dir_prefix，需先在 layer_vocabulary.yaml 中新增该字段——见裁定 #ARCH-011）
# 暂行方案：保留 layer_to_dir_prefix 但改为基于 SSoT 的映射表
_LAYER_DIR_PREFIX_MAP = {
    "data": "l00_", "infra_ops": "l01_", "factor": "l02_", "signal": "l03_",
    "risk": "l04_", "pf_core": "l05_", "ex_core": "l06_", "reporting": "l07_",
    "frontend": "l08_", "research": "l09_", "compliance": "l10_", "ml_train": "l11_",
    "system-telemetry": "l12_", "simulation": "l13_", "shared": "", "cross_layer": "",
}
def _layer_to_dir_prefix(layer: str) -> str:
    return _LAYER_DIR_PREFIX_MAP.get(layer, "")
```

**注意**：上述映射表硬编码会再次产生漂移风险。**根本方案**：在 layer_vocabulary.yaml 每个 entry 中新增 `dir_prefix` 字段（裁定 #ARCH-011），由 validator 动态读取。本方案文档建议采用根本方案，但允许分两步：第一步用映射表（停止漂移），第二步裁定 #ARCH-011 落地后改为动态读取。

#### 5.5.3 修复 validate_ssot.py（行 57）

**动作 18**：补全 [validate_ssot.py:57](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_ssot.py#L57) 的 `_get_valid_layers()` 函数体

```python
# 修改前
def _get_valid_layers():
    """stub"""
    return ["l01", "l02", ..., "l13"]  # 当前是 stub

# 修改后
def _get_valid_layers() -> list[str]:
    """从 layer_vocabulary.yaml 加载合法 layer 值"""
    from _shared.constants import GOV_DOCS_DIR
    import yaml
    vocab = GOV_DOCS_DIR / "_registry" / "vocabularies" / "layer_vocabulary.yaml"
    if not vocab.exists():
        return []
    data = yaml.safe_load(vocab.read_text(encoding="utf-8"))
    return [str(v.get("value")) for v in data.get("values", []) if isinstance(v, dict)]
```

#### 5.5.4 验证阶段 4

```bash
# 跑 validate_rule_frontmatter.py 确认 layer 校验用 SSoT 16 值
python scripts/governance/d3_metadata/validate_rule_frontmatter.py --check

# 期望：trae_015/016/043/047.yaml 因 frontmatter layer=L1/L2 报错（这就是阶段 6 要修的）
```

**回滚**：
```bash
python scripts/git_guard.py checkout HEAD -- scripts/governance/d3_metadata/validate_rule_frontmatter.py
python scripts/git_guard.py checkout HEAD -- scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py
python scripts/git_guard.py checkout HEAD -- scripts/governance/d5_architecture/validators/validate_ssot.py
```

---

### 5.6 阶段 5：处理 3 份 triage.py

#### 5.6.1 删除 2 份孤儿副本

**动作 19**：用 DeleteFile 工具删除

```
d:\ZephyrAlpha\src\zephyr\governance\kb\triage.py
d:\ZephyrAlpha\src\zephyr\governance\kb\pipeline\triage.py
```

**验证**：
```bash
# 确认无代码 import 这两份孤儿
grep -r "from zephyr.governance.kb.triage" src/ tests/ scripts/
grep -r "from zephyr.governance.kb.pipeline.triage" src/ tests/ scripts/
# 期望：无匹配（已在调研中确认零消费者）

# 检查 __init__.py 是否需要同步清理
grep -n "triage" src/zephyr/governance/kb/__init__.py src/zephyr/governance/kb/pipeline/__init__.py
```

**动作 20**：根据动作 19 的 grep 结果，用 Edit 工具清理 `kb/__init__.py` 和 `kb/pipeline/__init__.py` 中对 triage 的幽灵导出（`__all__` 列表中移除 `"TriageGate"` 和 `"triage"`）

#### 5.6.2 修复主版 triage.py

**动作 21**：用 Edit 工具修改 [src/zephyr/governance/triage.py:73-113](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L73-L113)

```python
# 修改前（行 73-95，VALID_DOC_TYPES 22 值含幽灵 adr + 4 deprecated）
VALID_DOC_TYPES = [
    "policy", "standard", "adr", "blueprint", "construction_plan", "design",
    ...
    "ai_governance", "candidate_pool", "service_spec", "discussion_draft",
    "terminology", "reference",
]

# 修改后（从 doc_type_vocabulary.yaml 加载 active 值，自动排除 deprecated）
# 实现方案 B：模块级懒加载
import sys
from pathlib import Path
_VOCAB_DIR = Path(__file__).resolve().parents[3] / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies"

def _load_vocab_values(vocab_file: str) -> list[str]:
    """从 vocabulary YAML 加载 active 值（排除 deprecated_values）"""
    p = _VOCAB_DIR / vocab_file
    if not p.exists():
        return []
    import yaml
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return [
        str(entry.get("value") or entry.get("id"))
        for entry in data.get("values", [])
        if isinstance(entry, dict)
    ]

VALID_DOC_TYPES = _load_vocab_values("doc_type_vocabulary.yaml")
VALID_LAYERS = _load_vocab_values("layer_vocabulary.yaml")
```

**注意**：此方案是"方案 B 的运行时读取变体"——但调研发现 src/ 不能 import scripts/_shared，所以这里用相对路径 `parents[3]` 推导 docs 目录。**风险**：triage.py 当前是 src 树模块，引入 docs/ 依赖会破坏分层。

**替代方案 B'（更稳健，推荐）**：保持硬编码，但用单元测试 + pre-commit hook 校验一致性：

```python
# triage.py 保持硬编码，但删除幽灵值和 deprecated 值
VALID_DOC_TYPES = [
    "policy", "standard", "operational_rule", "register", "index", "protocol",
    "template", "terminology", "reference", "vocabulary", "contract", "schema",
    "blueprint", "construction_plan", "design", "plan", "roadmap", "readme",
    "log", "knowledge_entry", "audit_report", "service_spec",
    "architecture_view", "declaration", "gate", "config",
]
VALID_LAYERS = [
    "data", "infra_ops", "factor", "signal", "risk", "pf_core", "ex_core",
    "reporting", "frontend", "research", "compliance", "ml_train",
    "system-telemetry", "simulation", "shared", "cross_layer",
]
```

**本方案推荐方案 B'**（避免引入跨树依赖），同时新增 `tests/test_triage_vocab_consistency.py` 断言与 YAML 一致。

#### 5.6.3 修复 module_id 三向冲突

**动作 22**：用 Edit 工具修改 triage.py 头部 frontmatter，统一 module_id（孤儿删除后主版独占）

```python
# 修改前（头部注释）
# [A_module] module_id=MOD-DAT_triage
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md
# [MODULE] zephyr.knowledge.kb.triage   ← 与实际路径 src/zephyr/governance/triage.py 不符

# 修改后
# [A_module] module_id=MOD-GOV-TRIAGE   ← 改为更语义化的 ID
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md
# [MODULE] zephyr.governance.triage   ← 与实际路径一致
```

**注意**：module_id 修改需同步更新 depgraph.db（用 `apply_depgraph.py --update-node`），并验证 `tests/test_kb_triage.py` 等仍能通过。

#### 5.6.4 验证阶段 5

```bash
# 跑测试
python -m pytest tests/test_kb_triage.py tests/unit/test_triage_unit.py tests/unit/kb/test_triage_kb.py tests/integration/test_kb_pipeline_gate_order.py -v

# 期望：全部通过（测试只断言 len > 0，不依赖具体值）
```

**回滚**：
```bash
# 恢复删除的孤儿
python scripts/git_guard.py checkout HEAD -- src/zephyr/governance/kb/triage.py src/zephyr/governance/kb/pipeline/triage.py
# 恢复主版修改
python scripts/git_guard.py checkout HEAD -- src/zephyr/governance/triage.py
```

---

### 5.7 阶段 6：修复 trae_*.yaml frontmatter layer（含 layer 命名体系裁定）

#### 5.7.1 裁定 layer 命名体系（议题 #ARCH-009）

在执行本阶段前，需用户先批准裁定 #ARCH-009（采纳方案 A：layer 字段统一用 layer_vocabulary.yaml 的 16 值语义命名）。

#### 5.7.2 修复 4 个 trae_*.yaml frontmatter

**动作 23**：用 Edit 工具修改 [trae_015_arch_path_registration.yaml:4](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_015_arch_path_registration.yaml#L4)

```yaml
# 修改前
layer: L1

# 修改后（架构路径注册属于治理层）
layer: compliance
```

**动作 24**：修改 [trae_016_arch_drift_detection.yaml:4](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml#L4) → `layer: compliance`

**动作 25**：修改 [trae_043_meta_rule_metadata.yaml:4](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml#L4) → `layer: compliance`

**动作 26**：修改 [trae_047_engineering_file_header.yaml:4](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml#L4) → `layer: compliance`

**注意**：需用户确认 4 个规则文件实际归属哪个 layer（推荐全部 `compliance`，因属治理规则；用户可调整）。

#### 5.7.3 修复 trae_043 内部描述（行 610）

**动作 27**：用 Edit 工具修改 [trae_043_meta_rule_metadata.yaml:610-611](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml#L610-L611)

```yaml
# 修改前
- name: layer
  values: 14值(l00-l11+shared+cross_layer)
  code_source: triage.py VALID_LAYERS

# 修改后
- name: layer
  values: 16值(data/infra_ops/factor/signal/risk/pf_core/ex_core/reporting/frontend/research/compliance/ml_train/system-telemetry/simulation/shared/cross_layer)
  canonical_sso_t: _registry/vocabularies/layer_vocabulary.yaml
```

#### 5.7.4 修复 g2_triage.yaml（行 124-142）

**动作 28**：用 Edit 工具修改 [src/zephyr/governance/rule_enforcement/g2_triage.yaml:124-142](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/g2_triage.yaml#L124-L142)

将 `valid_layers` 18 值改为 SSoT 16 值：

```yaml
# 修改后
valid_layers:
  - data
  - infra_ops
  - factor
  - signal
  - risk
  - pf_core
  - ex_core
  - reporting
  - frontend
  - research
  - compliance
  - ml_train
  - system-telemetry
  - simulation
  - shared
  - cross_layer
```

#### 5.7.5 修复 apply_depgraph.py ALLOWED_LAYERS（议题 #ARCH-010）

**动作 29**：用 Edit 工具修改 [apply_depgraph.py:1679](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L1679)

```python
# 修改前
ALLOWED_LAYERS = {"L0_infrastructure", "L1_foundation", "L1_platform", "L2_domain"}

# 修改后（与 DB CHECK 触发器一致：裁定#203-C）
ALLOWED_LAYERS = {"L0_infrastructure", "L1_foundation", "L2_domain", "L3_application"}
```

**注意**：此修复涉及 layer_id（域层级，4 值体系），与 layer（架构层，16 值体系）是不同字段，不冲突。

#### 5.7.6 验证阶段 6

```bash
# 跑 validate_rule_frontmatter.py 确认 4 个 trae_*.yaml 不再报 layer 错误
python scripts/governance/d3_metadata/validate_rule_frontmatter.py --check

# 跑 validate_blueprint_placement.py 确认 layer 校验通过
python scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py --check
```

**回滚**：
```bash
python scripts/git_guard.py checkout HEAD -- docs/01_policies_and_standards/rules/trae_015_arch_path_registration.yaml
python scripts/git_guard.py checkout HEAD -- docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml
python scripts/git_guard.py checkout HEAD -- docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml
python scripts/git_guard.py checkout HEAD -- docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml
python scripts/git_guard.py checkout HEAD -- src/zephyr/governance/rule_enforcement/g2_triage.yaml
python scripts/git_guard.py checkout HEAD -- scripts/governance/apply_depgraph.py
```

---

### 5.8 阶段 7：全项目 kebab 路径清理

#### 5.8.1 清理 17+ 处 kebab 引用

按 3.7 节清单逐个修改（每处用 Edit 工具，将 `frontmatter-field-registry.md` → `frontmatter_field_registry.yaml`、`architecture-contract.yaml` → `architecture_contract.yaml`、`frontmatter-schema.json` → `frontmatter_schema.json`、`doc_type-vocabulary.yaml` → `doc_type_vocabulary.yaml` 等）。

**注意**：动作较多但机械，建议分批处理（每批 5-10 个文件），每批跑一次 git commit。

#### 5.8.2 修复 6 处 vocabulary YAML 自描述中的 kebab

**动作 30-35**：修改 [verifiability/stability/scope/language/created_by/classification]_vocabulary.yaml 各自的 `source:` 字段（第 18/19/19/18/18/19 行）

```yaml
# 修改前
source: "PS-STD-001 + architecture-contract.yaml frontmatter_schema"

# 修改后
source: "PS-STD-001 + architecture_contract.yaml frontmatter_schema"
```

#### 5.8.3 处理扫描快照历史脏数据

**动作 36**：评估 [data/scans/raw_asset_scan.json](file:///d:/ZephyrAlpha/data/scans/raw_asset_scan.json) 和 [data/classified/classified_assets.json](file:///d:/ZephyrAlpha/data/classified/classified_assets.json) 中 kebab 引用是否需要清理。

**建议**：扫描快照是历史数据，**保留不动**（重跑扫描会自动覆盖）。仅在 `data/scans/README.md`（若存在）中加注释说明。

#### 5.8.4 验证阶段 7

```bash
# 全项目 grep 确认无 kebab 残留（排除 _archive 和 data/backups）
grep -rn "frontmatter-field-registry\|architecture-contract\|frontmatter-schema\|doc_type-vocabulary\|status-vocabulary\|rule_form-vocabulary\|ttl-vocabulary\|layer-vocabulary" \
  --include="*.py" --include="*.yaml" --include="*.json" --include="*.md" \
  d:/ZephyrAlpha/src d:/ZephyrAlpha/scripts d:/ZephyrAlpha/docs \
  | grep -v "_archive\|data/backups\|data/scans"

# 期望输出：空（无残留）
```

**回滚**：
```bash
# 按批次回滚
python scripts/git_guard.py checkout HEAD~<N> -- <文件路径>
```

---

### 5.9 阶段 8：文档与索引同步

#### 5.9.1 补录 panorama 裁定

**动作 37**：在 [dependency_architecture_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/dependency_architecture_panorama.md) 裁定表中追加：

```markdown
## 裁定 #206：vocabulary 同步链路根因性修复（议题 #ARCH-008~#011）

| 子裁定 | 议题 | 内容 | 状态 |
|---|---|---|---|
| #206-A | #ARCH-008 | vocabulary 同步链路 8 个 bug 修复 | 待执行 |
| #206-B | #ARCH-009 | layer 命名体系统一为 layer_vocabulary.yaml 16 值 | 待执行 |
| #206-C | #ARCH-010 | apply_depgraph.py ALLOWED_LAYERS 与 DB CHECK 对齐 | 待执行 |
| #206-D | #ARCH-011 | layer_vocabulary.yaml 新增 dir_prefix 字段（根本方案） | 待执行 |

## 补录裁定 #204（D-SIGNAL* 4 域改名）和 #205（d_signal_rename_blocker）
（从 d_signal_rename_plan.md 和 d_signal_rename_blocker_adjudication.md 补录）
```

#### 5.9.2 补录 preexisting_db_issues 附录 B

**动作 38**：在 [preexisting_db_issues_investigation_report.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md) 附录 B 追加议题 #ARCH-008~#011

#### 5.9.3 补充 onboarding_detail.md

**动作 39**：在 [.trae/rules/onboarding_detail.md](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md) 中追加章节：

```markdown
## Vocabulary 同步机制

项目 frontmatter 字段的合法枚举值由 vocabulary YAML 唯一定义：
- 真源：`docs/01_policies_and_standards/_registry/vocabularies/*.yaml`（26 个文件：24 个 *_vocabulary.yaml + glossary.yaml + terminology_mapping.yaml）
- 派生：3 个文件由 `scripts/governance/d3_metadata/generate_derived_files.py` 自动同步
  - `frontmatter_field_registry.yaml`（catalogs/）
  - `architecture_contract.yaml`（contracts/）
  - `frontmatter_schema.json`（schemas/）
- DB 缓存：`field_vocabularies` 表由 `sync_yaml_to_depgraph.py` 单向同步（只读）

修改流程：
1. 修改 vocabulary YAML
2. 运行 `python scripts/governance/d3_metadata/generate_derived_files.py --apply`
3. 运行 `python scripts/governance/sync_yaml_to_depgraph.py`
4. 提交（pre-commit GATE-GENERATE hook 自动校验一致性）
```

#### 5.9.4 修复 navigation_index.py 硬编码

**动作 40**：修改 [generate_navigation_index.py:154](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_navigation_index.py#L154)

```python
# 修改前
lines.append("3. 看 ... 了解43个域之间怎么互相依赖")

# 修改后（动态从 depgraph.db 读取域数）
import sqlite3
_db = sqlite3.connect(r"d:\ZephyrAlpha\data\databases\depgraph.db")
_domain_count = _db.execute("SELECT COUNT(*) FROM domains WHERE build_status != 'deprecated'").fetchone()[0]
_db.close()
lines.append(f"3. 看 ... 了解{_domain_count}个域之间怎么互相依赖")
```

**动作 41**：重生成 [navigation_index.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/00_overview_entry/navigation_index.md)

```bash
python scripts/governance/d5_architecture/generators/generate_navigation_index.py
```

---

### 5.10 阶段 9：补单元测试 + 接入 pre-commit hook

#### 5.10.1 新增测试

**动作 42**：创建 `tests/test_generate_derived_files.py`

```python
"""测试 generate_derived_files.py 派生文件与 vocabulary YAML 一致性"""
import json
import sys
from pathlib import Path
import yaml
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "governance"))
from _shared.constants import GOV_DOCS_DIR

VOCAB_DIR = GOV_DOCS_DIR / "_registry" / "vocabularies"
CATALOGS = GOV_DOCS_DIR / "_registry" / "catalogs"
CONTRACTS = GOV_DOCS_DIR / "_registry" / "contracts"
SCHEMAS = GOV_DOCS_DIR / "_registry" / "schemas"

@pytest.mark.parametrize("vocab_file,field_name", [
    ("doc_type_vocabulary.yaml", "doc_type"),
    ("status_vocabulary.yaml", "status"),
    ("rule_form_vocabulary.yaml", "rule_form"),
    ("ttl_vocabulary.yaml", "ttl"),
    ("layer_vocabulary.yaml", "layer"),
])
def test_vocab_yaml_uses_vocabulary_name_key(vocab_file, field_name):
    """确认 vocabulary YAML 用 vocabulary_name 键（不是 field_name）"""
    data = yaml.safe_load((VOCAB_DIR / vocab_file).read_text(encoding="utf-8"))
    assert data.get("vocabulary_name") == field_name
    assert "field_name" not in data

def test_frontmatter_schema_layer_matches_vocab():
    """确认 frontmatter_schema.json 的 layer oneOf 与 layer_vocabulary.yaml 一致"""
    vocab = yaml.safe_load((VOCAB_DIR / "layer_vocabulary.yaml").read_text(encoding="utf-8"))
    expected = {v["value"] for v in vocab["values"]}
    schema = json.loads((SCHEMAS / "frontmatter_schema.json").read_text(encoding="utf-8"))
    actual = {item["const"] for item in schema["properties"]["layer"]["oneOf"]}
    assert actual == expected, f"layer 漂移: 多 {actual - expected}, 缺 {expected - actual}"

def test_field_vocabularies_table_no_dirty_field_name():
    """确认 field_vocabularies 表无 *_vocabulary 后缀脏值"""
    import sqlite3
    c = sqlite3.connect(r"d:\ZephyrAlpha\data\databases\depgraph.db")
    dirty = c.execute(
        "SELECT DISTINCT field_name FROM field_vocabularies WHERE field_name LIKE '%_vocabulary'"
    ).fetchall()
    assert not dirty, f"脏值残留: {dirty}"
```

**动作 43**：创建 `tests/test_triage_vocab_consistency.py`

```python
"""测试 triage.py 的 VALID_DOC_TYPES/VALID_LAYERS 与 vocabulary YAML 一致"""
import sys
from pathlib import Path
import yaml
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zephyr.governance.triage import VALID_DOC_TYPES, VALID_LAYERS

VOCAB_DIR = Path(r"d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies")

def test_valid_doc_types_matches_vocab():
    data = yaml.safe_load((VOCAB_DIR / "doc_type_vocabulary.yaml").read_text(encoding="utf-8"))
    expected = {v["value"] for v in data["values"]}
    assert set(VALID_DOC_TYPES) == expected

def test_valid_layers_matches_vocab():
    data = yaml.safe_load((VOCAB_DIR / "layer_vocabulary.yaml").read_text(encoding="utf-8"))
    expected = {v["value"] for v in data["values"]}
    assert set(VALID_LAYERS) == expected
```

#### 5.10.2 接入 pre-commit GATE-GENERATE hook

**动作 44**：用 Edit 工具在 [.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) 中追加（在 GATE-15 之后）：

```yaml
- id: gate-generate-derived
  name: GATE-GENERATE — vocabulary YAML → 派生文件一致性
  entry: python scripts/governance/d3_metadata/generate_derived_files.py --check --warn-only
  language: system
  pass_filenames: false
  files: ^docs/01_policies_and_standards/_registry/vocabularies/.*\.yaml$
  stages: [commit]
```

#### 5.10.3 验证阶段 9

```bash
# 跑新测试
python -m pytest tests/test_generate_derived_files.py tests/test_triage_vocab_consistency.py -v

# 跑 pre-commit
python scripts/git_guard.py add tests/test_generate_derived_files.py tests/test_triage_vocab_consistency.py .pre-commit-config.yaml
python scripts/git_guard.py commit -m "test: add vocabulary sync chain tests + GATE-GENERATE hook (#ARCH-008)"
```

**期望**：测试全部通过，pre-commit hook 触发但不阻断（warn_only=true）。

---

### 5.11 阶段 10：sync_yaml_to_depgraph.py 锁保护 + DB_PATH 统一（Bug G/H）

#### 5.11.1 修复 Bug H（DB_PATH 统一）

**动作 45**：在 [_shared/constants.py:117](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py#L117) 后新增：

```python
DEPGRAPH_DB_PATH: Path = REPO_ROOT / "data" / "databases" / "depgraph.db"
```

**动作 46**：用 Edit 工具修改 [sync_yaml_to_depgraph.py:51](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py#L51)

```python
# 修改前
DB_PATH = r"D:\ZephyrAlpha\data\databases\depgraph.db"

# 修改后
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared.constants import DEPGRAPH_DB_PATH
DB_PATH = str(DEPGRAPH_DB_PATH)
```

#### 5.11.2 修复 Bug G（锁保护）

**动作 47**：在 sync_yaml_to_depgraph.py 引入跨进程文件锁（参考 scripts/lock_files.py）

```python
# 在 sync_all 函数开头（行 914 之后）添加
# lock_files.py 在 scripts/ 根目录（非 _shared/），提供跨进程文件锁
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(r"d:\ZephyrAlpha\scripts").resolve()))
import lock_files as _lock_files

_DB_REL = "data/databases/depgraph.db"  # lock_files.py 接收相对仓库根的路径
_LOCK_OWNER = "sync-yaml-depgraph"

def sync_all():
    # 获取 depgraph.db 跨进程文件锁
    if _lock_files.cmd_acquire(_DB_REL, _LOCK_OWNER, task="sync_yaml_to_depgraph") != 0:
        print("⚠️ 无法获取锁，另一 sync 进程正在运行（depgraph.db 被 hold）")
        return False
    try:
        # 原有 sync_all 逻辑（行 916 起的 conn = sqlite3.connect(...) 等）
        ...
    finally:
        _lock_files.cmd_release(_DB_REL, _LOCK_OWNER)
```

**说明**：`scripts/lock_files.py` 已存在（行 247 `cmd_acquire`、行 340 `cmd_release`），CLI 与 Python API 双形态。apply_depgraph.py 的 `_db_write_lock`（行 204）是 `threading.Lock` 进程内锁，不适用于跨进程并发，不可照搬。

#### 5.11.3 验证阶段 10

```bash
# 验证锁保护
# 终端 A：手动 acquire 锁（占住 depgraph.db）
python scripts/lock_files.py acquire data/databases/depgraph.db test-lock-holder --task "lock test"

# 终端 B：跑 sync，应失败（无法获取锁）
python scripts/governance/sync_yaml_to_depgraph.py
# 期望：打印"⚠️ 无法获取锁，另一 sync 进程正在运行"

# 清理：终端 A 释放锁
python scripts/lock_files.py release data/databases/depgraph.db test-lock-holder
```

---

## 第六部分：验证标准

### 6.1 单元测试

| 测试文件 | 覆盖范围 | 期望结果 |
|---|---|---|
| `tests/test_generate_derived_files.py` | 5 个 vocab YAML 的 vocabulary_name 键 + 派生文件一致性 + DB 脏值 | 全部 PASS |
| `tests/test_triage_vocab_consistency.py` | triage.py VALID_DOC_TYPES/VALID_LAYERS 与 YAML 一致 | 全部 PASS |
| `tests/test_kb_triage.py` 等 4 个既有测试 | TriageGate 功能 | 全部 PASS（无 regression） |

### 6.2 集成验证

```bash
# 1. 跑 generate_derived_files.py --check 应 exit 0
python scripts/governance/d3_metadata/generate_derived_files.py --check
# 期望：✅ 所有派生文件与 vocabulary YAML 一致

# 2. 跑 sync_yaml_to_depgraph.py 应 exit 0
python scripts/governance/sync_yaml_to_depgraph.py
# 期望：✅ 同步完成，无脏值

# 3. 跑 validate_rule_frontmatter.py 应无 layer 报错
python scripts/governance/d3_metadata/validate_rule_frontmatter.py --check
# 期望：无 trae_015/016/043/047 layer 违规

# 4. 跑 validate_blueprint_placement.py 应通过
python scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py --check
# 期望：exit 0

# 5. 全项目 grep 应无 kebab 残留（排除 _archive 和 backups）
# 见 5.8.4 验证命令
```

### 6.3 三方对齐

参考 `triple_alignment.py` 验证：
- 全景图（depgraph.db）中 vocabulary 节点 ↔ 蓝图 frontmatter ↔ 实际代码三方一致
- field_vocabularies 表 field_name 与 vocabulary YAML vocabulary_name 一一对应

### 6.4 循环验收

执行循环验收检查，要求连续 2 轮 0 问题：

```bash
# 注：batch_review.py 当前不存在（仅在临时脚本 _tmp_batch_transition.py 中引用）
# 循环验收改为手动执行以下验证命令 2 轮，每轮全部 PASS 才算 0 问题：
# 轮次 1
python scripts/governance/d3_metadata/generate_derived_files.py --check
python scripts/governance/sync_yaml_to_depgraph.py  # --dry-run 若支持
python scripts/governance/d3_metadata/validate_rule_frontmatter.py --check
python -m pytest tests/test_generate_derived_files.py tests/test_triage_vocab_consistency.py -v
# 记录结果，若有问题则修复后重跑本轮
# 轮次 2（确认连续 2 轮 0 问题）
# 重复上述 4 条命令
```

---

## 第七部分：回滚方案

### 7.1 阶段级回滚

| 阶段 | 回滚命令 | 影响 |
|---|---|---|
| 阶段 1 | `python scripts/git_guard.py checkout HEAD -- scripts/governance/d3_metadata/generate_derived_files.py` | 脚本回到 bug 状态，但已修复的派生文件不变 |
| 阶段 2 | `python scripts/git_guard.py checkout HEAD -- scripts/governance/sync_yaml_to_depgraph.py` | 同上 |
| 阶段 3 | `python scripts/git_guard.py checkout HEAD~1 -- data/databases/depgraph.db docs/01_policies_and_standards/_registry/` | DB 和派生文件回到修复前 |
| 阶段 4 | `python scripts/git_guard.py checkout HEAD -- scripts/governance/d3_metadata/validate_rule_frontmatter.py scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py scripts/governance/d5_architecture/validators/validate_ssot.py` | validator 回到硬编码 |
| 阶段 5 | `python scripts/git_guard.py checkout HEAD -- src/zephyr/governance/kb/triage.py src/zephyr/governance/kb/pipeline/triage.py src/zephyr/governance/triage.py` | 恢复孤儿副本和主版 |
| 阶段 6 | `python scripts/git_guard.py checkout HEAD -- docs/01_policies_and_standards/rules/trae_0*.yaml src/zephyr/governance/rule_enforcement/g2_triage.yaml scripts/governance/apply_depgraph.py` | 规则文件回到 L1/L2 |
| 阶段 7 | 按批次 `python scripts/git_guard.py checkout` | 逐个回滚 |
| 阶段 8 | `python scripts/git_guard.py checkout HEAD -- docs/02_enterprise_architecture/dependency_architecture_panorama.md .trae/rules/onboarding_detail.md` | 文档回到修复前 |
| 阶段 9 | `python scripts/git_guard.py checkout HEAD -- tests/test_generate_derived_files.py tests/test_triage_vocab_consistency.py .pre-commit-config.yaml` | 移除测试和 hook |
| 阶段 10 | `python scripts/git_guard.py checkout HEAD -- scripts/governance/sync_yaml_to_depgraph.py scripts/governance/_shared/constants.py` | 锁和 DB_PATH 回退 |

### 7.2 紧急回滚（depgraph.db 损坏）

```bash
# 1. 释放所有锁（lock_files.py 在 scripts/ 根目录；CLI: release-all <owner_id>）
python scripts/lock_files.py release-all vocab-sync-2621

# 2. 从阶段 0 的 git 备份恢复
python scripts/git_guard.py checkout <阶段0的commit_hash> -- data/databases/depgraph.db

# 3. 验证 DB 完整性
python -c "import sqlite3; c=sqlite3.connect(r'd:\ZephyrAlpha\data\databases\depgraph.db'); print('PRAGMA integrity_check:', c.execute('PRAGMA integrity_check').fetchone())"
```

### 7.3 完全回滚

```bash
# 回滚所有修改（保留 git 历史用于审计）
python scripts/git_guard.py revert --no-commit <起始commit>..HEAD
```

---

## 第八部分：风险评估

### 8.1 高风险点

| # | 风险 | 概率 | 影响 | 缓解措施 |
|---|---|---|---|---|
| R1 | 阶段 3 重生成派生文件覆盖人工维护的内容（如 enum_values 的 description 字段） | 高 | 中 | 阶段 0 必做 git 备份；重生成后人工 diff 确认 description 不丢失；若有丢失，从 git 历史恢复并人工合并 |
| R2 | 阶段 5 删除 kb/triage.py 和 kb/pipeline/triage.py 后，data/asset_index/dependency_graph.json 仍引用它们 | 中 | 低 | 同步更新 dependency_graph.json（或重跑生成器） |
| R3 | 阶段 6 修改 trae_*.yaml frontmatter layer 后，下游有代码硬编码读取 `layer: L1` | 低 | 高 | 阶段 6 前先 Grep `layer.*L[0-3]` 全项目，确认无运行时代码依赖 |
| R4 | 阶段 5 修改 triage.py 的 module_id 后，depgraph.db nodes 表需同步更新 | 高 | 中 | 用 `apply_depgraph.py --update-node` 同步；测试通过后才提交 |
| R5 | 阶段 2 sync_yaml_to_depgraph.py 锁保护引入可能与既有 apply_depgraph.py 锁冲突 | 中 | 中 | 锁文件名不同（sync_yaml_depgraph.lock vs apply_depgraph.lock）；若共享 DB 锁，参考 apply_depgraph 的锁逻辑 |
| R6 | 阶段 7 kebab 清理误改 docs/08_knowledge/ 知识库内容（历史引用） | 中 | 低 | 知识库是历史快照，**保留不动**，仅清理代码/规则/registry |
| R7 | trae_043 行 610 layer 描述错误，下游有规则引用该描述 | 低 | 低 | 阶段 6 已在动作 27 修复 |

### 8.2 中风险点

| # | 风险 | 缓解 |
|---|---|---|
| R8 | 测试 test_kb_triage.py 等可能因 VALID_DOC_TYPES 值变更而失败 | 测试只断言 len > 0，不依赖具体值，风险低；若失败则更新测试 |
| R9 | layer_vocabulary.yaml 新增 dir_prefix 字段（裁定 #ARCH-011）会修改 SSoT | 单独议题，本方案允许分两步：第一步用映射表，第二步落地 #ARCH-011 |
| R10 | 阶段 4 修复 validator 后，CI 可能因 trae_015 等 frontmatter layer=L1 报错而阻断其他提交 | 阶段 4 与阶段 6 应在同一次提交中完成；或阶段 4 用 warn_only 模式临时通过 |

### 8.3 低风险点

| # | 风险 | 缓解 |
|---|---|---|
| R11 | registry_adapter.py 两份重复实现修改不一致 | 阶段 7 同步修改两份 |
| R12 | data/scans/raw_asset_scan.json 历史脏数据 | 保留不动，仅在 README 加注释 |
| R13 | 两份 script_manifest.yaml 重复登记 | 治理债，本方案不处理，留待后续 |

### 8.4 与并发 session 的冲突风险

**当前并发任务**（截至 2026-06-26）：
- P2 PostgreSQL migration（28 张任务卡）
- D-SIGNAL rename（20 张任务卡，已执行到主卡 06）
- depgraph.db 修复（6 张任务卡，OPS-2026062502~507）
- F1-F37 核心功能依赖设计 4 个 gap

**冲突点**：
- 阶段 3 修改 depgraph.db 的 field_vocabularies 表，与 P2 migration（要把 depgraph.db 迁移到 PG）有窗口冲突
- 阶段 6 修改 apply_depgraph.py，与 D-SIGNAL rename 主卡 02（新增 cmd_rename_domain 子命令）可能冲突
- 阶段 7 修改 trae_*.yaml，与 depgraph.db 修复任务卡 OPS-2026062507（更新规则文档）可能冲突

**建议**：
1. **优先执行阶段 1-3**（修工具+重生成+清DB），与 P2 migration 不冲突（P2 还在 task card 准备阶段）
2. **暂缓阶段 6-7**（与 D-SIGNAL rename 和 depgraph 修复冲突），等并发任务完成后再执行
3. 阶段 4-5、8-10 可并行，与并发任务不冲突

---

## 第九部分：任务卡拆分

### 9.1 任务卡清单（建议 10 张主卡 + 10 张元审查卡）

| 任务卡 ID | 阶段 | 内容 | 依赖 | 优先级 |
|---|---|---|---|---|
| OPS-2026062621 | 0 | 前置备份 + field_vocabularies 主键验证 | 无 | P1（原P0，因系统142个P0冻结降级） |
| OPS-2026062622 | 1 | 修复 generate_derived_files.py（Bug A/C/D/E/F） | 2621 | P1（原P0，同上） |
| OPS-2026062623 | 2 | 修复 sync_yaml_to_depgraph.py（Bug B）+ 脏值清理 | 2622 | P1（原P0，同上） |
| OPS-2026062624 | 3 | 重生成 3 个派生文件 + 重跑 sync | 2623 | P1（原P0，同上） |
| OPS-2026062625 | 4 | 修复 4 个 validator 硬编码 layer | 2624 | P1 |
| OPS-2026062626 | 5 | 删除孤儿 + 修复主版 triage.py | 2624 | P1 |
| OPS-2026062627 | 6 | 修复 trae_*.yaml frontmatter + apply_depgraph.py | 2625（裁定 #ARCH-009 需先批准） | P1 |
| OPS-2026062628 | 7 | 全项目 kebab 路径清理 | 2627 | P2 |
| OPS-2026062629 | 8 | 文档与索引同步（panorama/onboarding/navigation） | 2628 | P2 |
| OPS-2026062630 | 9-10 | 补测试 + 接入 GATE-GENERATE hook + 锁保护 + DB_PATH 统一 | 2629, 2626 | P2-P3 |

每张主卡配 1 张元审查卡（OPS-2026062631~2640），按 RULE-THIRTEEN 颗粒度规则执行循环审查。

### 9.2 任务卡执行顺序（DAG）

```
2621 (前置)
  ↓
2622 (修工具A) → 2623 (修工具B) → 2624 (重生成) ← P0 完成
                                    ↓
                      ┌───────────┴──────────┐
                      ↓                       ↓
              2625 (validator)        2626 (triage)
                      ↓                       │
              2627 (规则+裁定#ARCH-009)        │  ← 需用户先批准 #ARCH-009
                      ↓                       │
              2628 (kebab 清理)                │
                      ↓                       │
              2629 (文档)                     │
                      ↓                       │
                      └──────────┬────────────┘
                                 ↓
                       2630 (测试 + 锁) ← P2-P3 完成
```

**说明**：2627 仅依赖 2625（validator 修复后才能验证规则）；2626（triage 修复）与 2625 并行，独立汇入 2630（测试验证）。2626 不阻塞 2627-2629 链路。

### 9.3 元审查卡验收标准

每张元审查卡检查：
1. 主卡 COMPLETED 状态是否正确
2. 修改文件清单是否完整（与方案文档 3.x 节对比）
3. 验证命令是否全部通过
4. 是否有 stash 冲突残留
5. git commit 历史是否清晰
6. 是否有未清理的临时文件
7. 是否符合 RULE-FIVE（临时脚本清理）
8. 是否符合 RULE-SEVENTEEN（git 命令通过 git_guard.py）

---

## 第十部分：时序与依赖

### 10.1 关键时序

| 时间点 | 事件 | 依赖 |
|---|---|---|
| T0 | 用户批准本方案 + 裁定 #ARCH-009~#011 | — |
| T1 | 创建 10 张任务卡到 governance.db | T0 |
| T2 | 执行 OPS-2026062621~2624（P0 阶段） | T1 |
| T3 | 执行 OPS-2026062625~2626（P1 阶段） | T2 |
| T4 | 用户确认 layer 命名体系裁定 #ARCH-009 | T3 |
| T5 | 执行 OPS-2026062627（规则 + apply_depgraph） | T4 |
| T6 | 执行 OPS-2026062628~2630（P2-P3 阶段） | T5 |

### 10.2 与并发任务的时序协调

| 并发任务 | 状态 | 与本方案冲突 | 协调策略 |
|---|---|---|---|
| P2 PostgreSQL migration | task card 准备中 | 阶段 3 修改 depgraph.db | 在 P2 migration 开始前完成阶段 1-3 |
| D-SIGNAL rename | 主卡 06 执行中 | 阶段 6 修改 apply_depgraph.py | 等主卡 06 完成后再执行阶段 6 |
| depgraph.db 修复 6 卡 | 部分完成 | 阶段 7 修改 trae_*.yaml | 等 OPS-2026062507 完成后再执行阶段 7 |
| F1-F37 4 gap | 待执行 | 无直接冲突 | 可并行 |
| GitCommitGateway | 已完成 | 阶段 9 接入 hook 无冲突 | — |

### 10.3 执行窗口建议

**推荐执行窗口**：
1. **立即执行**：阶段 1-3（P0，修工具+重生成+清DB），不与任何并发任务冲突
2. **一周内执行**：阶段 4-5（P1，validator + triage），不与并发任务冲突
3. **D-SIGNAL rename 完成后**：阶段 6（规则 + apply_depgraph）
4. **depgraph 修复完成后**：阶段 7-8（kebab 清理 + 文档）
5. **随时**：阶段 9-10（测试 + 锁）

---

## 附录 A：受影响文件索引（完整表格）

### A.1 Python 代码文件（7）

| # | 绝对路径 | 行号 | 修改类型 | 优先级 |
|---|---|---|---|---|
| 1 | d:\ZephyrAlpha\scripts\governance\d3_metadata\generate_derived_files.py | 81-91, 175-177, 182, 186, 227, 231, 280, 286, 291 | Bug A/C/D/E/F | P0/P1/P2 |
| 2 | d:\ZephyrAlpha\scripts\governance\sync_yaml_to_depgraph.py | 51, 441, 438（插入DELETE）, 全文（锁） | Bug B/G/H + 脏值清理 | P0/P3 |
| 3 | d:\ZephyrAlpha\scripts\governance\_shared\constants.py | 117 后新增 | 新增 DEPGRAPH_DB_PATH | P3 |
| 4 | d:\ZephyrAlpha\scripts\governance\d3_metadata\validate_rule_frontmatter.py | 101-104 | VALID_LAYER 动态加载 | P1 |
| 5 | d:\ZephyrAlpha\scripts\governance\d5_architecture\validators\blueprint\validate_blueprint_placement.py | 69, 79-87 | VALID_LAYERS 动态加载 + _layer_to_dir_prefix | P1 |
| 6 | d:\ZephyrAlpha\scripts\governance\d5_architecture\validators\validate_ssot.py | 57 | _get_valid_layers 补全 | P2 |
| 7 | d:\ZephyrAlpha\src\zephyr\governance\triage.py | 73-113, 头部 frontmatter | VALID_DOC_TYPES/VALID_LAYERS + module_id | P1 |

### A.2 规则文件（6）

| # | 绝对路径 | 行号 | 修改类型 | 优先级 |
|---|---|---|---|---|
| 8 | d:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml | 4, 235, 247, 249, 443, 455, 530, 610, 1080 | frontmatter layer + kebab + 描述 | P1 |
| 9 | d:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_015_arch_path_registration.yaml | 4 | frontmatter layer | P1 |
| 10 | d:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_016_arch_drift_detection.yaml | 4 | frontmatter layer | P1 |
| 11 | d:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_047_engineering_file_header.yaml | 4 | frontmatter layer | P1 |
| 12 | d:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_044_compliance_audit.yaml | 336 | vocab 数量 12→25 | P2 |
| 13 | d:\ZephyrAlpha\src\zephyr\governance\rule_enforcement\g2_triage.yaml | 124-142 | valid_layers 18→16 | P1 |

### A.3 派生文件（3，全部重生成）

| # | 绝对路径 | 重生成方式 | 优先级 |
|---|---|---|---|
| 18 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\schemas\frontmatter_schema.json | `generate_derived_files.py --apply` | P0 |
| 19 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\contracts\architecture_contract.yaml | 同上 | P0 |
| 20 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\frontmatter_field_registry.yaml | 同上 | P0 |

### A.4 Registry 文件（5+）

| # | 绝对路径 | 行号 | 修改类型 | 优先级 |
|---|---|---|---|---|
| 14 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\contracts\architecture_contract.yaml | 23-25 + 全文 derived_from | kebab→snake | P2 |
| 15 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\frontmatter_field_registry.yaml | 5, 60 + 全文 derived_from | kebab→snake | P2 |
| 16 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies\doc_type_vocabulary.yaml | 40, 144 | kebab→snake | P2 |
| 17 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies\*.yaml（其余 24 个） | 全部 derived_from 字段 | kebab→snake（待 grep 确认） | P2 |
| 35 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\registry_of_registries.yaml | 128, 130 | kebab→snake | P2 |
| 36 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\rule_catalog_registry.yaml | 1239 | kebab→snake | P2 |
| 37 | d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document_metadata_index_registry.yaml | 1242 | kebab→snake | P2 |

### A.5 删除孤儿模块（2~4）

| # | 绝对路径 | 删除理由 | 优先级 |
|---|---|---|---|
| 21 | d:\ZephyrAlpha\src\zephyr\governance\kb\triage.py | 孤儿 + 非法值 + module_id 冲突 | P1 |
| 22 | d:\ZephyrAlpha\src\zephyr\governance\kb\pipeline\triage.py | 同上 + Self 未 import | P1 |
| 23 | d:\ZephyrAlpha\src\zephyr\governance\kb\__init__.py | 评估是否清理幽灵导出 | P2 |
| 24 | d:\ZephyrAlpha\src\zephyr\governance\kb\pipeline\__init__.py | 同上 | P2 |

### A.6 DB 数据清理（1 表）

| # | DB | 表 | 操作 | 优先级 |
|---|---|---|---|---|
| 25 | depgraph.db | field_vocabularies | DELETE 脏值 + 重跑 sync | P0 |

### A.7 文档与索引（5+）

| # | 绝对路径 | 修改内容 | 优先级 |
|---|---|---|---|
| 26 | d:\ZephyrAlpha\.trae\rules\onboarding_detail.md | 补 vocabulary 同步机制说明 | P2 |
| 27 | d:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_architecture_panorama.md | 补录裁定#204/#205/#206 + 议题#ARCH-008~011 | P1 |
| 28 | d:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\preexisting_db_issues_investigation_report.md | 附录 B 追加 #ARCH-008~011 | P2 |
| 29 | d:\ZephyrAlpha\scripts\governance\d5_architecture\generators\generate_navigation_index.py | 154 行硬编码→动态 | P3 |
| 30 | d:\ZephyrAlpha\docs\02_enterprise_architecture\00_overview_entry\navigation_index.md | 重生成 | P3 |

### A.8 kebab 路径清理（17+）

详见 3.7 节表格（#31-#47）

### A.9 新增测试文件（2）

| # | 绝对路径 | 内容 | 优先级 |
|---|---|---|---|
| — | d:\ZephyrAlpha\tests\test_generate_derived_files.py | 派生文件一致性测试 | P2 |
| — | d:\ZephyrAlpha\tests\test_triage_vocab_consistency.py | triage.py 与 YAML 一致性 | P2 |

### A.10 新增/修改配置（1）

| # | 绝对路径 | 修改内容 | 优先级 |
|---|---|---|---|
| — | d:\ZephyrAlpha\.pre-commit-config.yaml | 追加 GATE-GENERATE hook | P2 |

---

## 附录 B：循环审查记录

### B.1 第 1 轮审查（2026-06-26，发现 11 个问题，已全部修复）

| # | 类别 | 文档位置 | 问题描述 | 修复 |
|---|---|---|---|---|
| 1 | 行号错误 | Bug D 表格 + 动作 3 | generate_derived_files.py field_registry `open()` 实际在行 182，文档说行 180（行 180 是 tmp_path 赋值） | 180→182 |
| 2 | 代码不符 | 动作 17 | validate_blueprint_placement.py `_layer_to_dir_prefix` "修改前"代码与磁盘实际不符（str vs str\|None，逻辑不同） | 按实际代码重写 |
| 3 | 数量错误 | 4.3 节 | "补齐缺失的 8 个 active 值"但列了 9 个，实际应补齐 9 个 | 8→9 |
| 4 | 数量错误 | 2.2.2 节 | doc_type "6 deprecated"，实际 7 个（含 governance_standard/governance_registry/registry） | 6→7 |
| 5 | 事实错误·重大 | 2.2.1 节 | schema.json layer oneOf 实际 16 值且含 L09-research-innovation，文档说"15 值+缺 L09" | 改为"16 值但命名方案不同" |
| 6 | 内部不一致 | 1.2/2.1 vs 3.3/5.9.3 | vocabulary 文件数 24 vs 25 不一致；实际目录 26 个 yaml（24 个 *_vocabulary.yaml + glossary.yaml + terminology_mapping.yaml） | 统一为 26（24 个 vocabulary + 2 个术语映射） |
| 7 | 工具路径错误·重大 | 5.1.1/7.2/5.11.2/6.4 | 4 个脚本路径不存在：task_repo.py / _shared/lock_files.py / d3_metadata/batch_review.py；lock_files.py 实际在 scripts/ 根目录 | 修正路径 + 接口 |
| 8 | 行号偏差 | 1.1 节 | "panorama 第 1989 行"裁定#203，实际在 1993 行 | 1989→1993 |
| 9 | DAG 不一致 | 9.1 表格 vs 9.2 图 | 2627 表格依赖 2625，DAG 图把 2626 也连到 2627 | 修正 DAG 图 |
| 10 | 参数错误 | 5.1.1 动作 2 / 7.2 | lock_files.py acquire/release-all 参数错误（缺 owner_id；--reason 应为 --task） | 按实际 CLI 签名修正 |
| 11 | 概念混淆 | Bug G / 5.11.2 | _db_write_lock 是进程内 threading.Lock，不能解决跨进程并发，文档建议"引入 _db_write_lock"有歧义 | 改为参考 lock_files.py 跨进程锁 |

### B.2 第 2 轮审查（2026-06-26，发现 4 个问题，已全部修复）

| # | 类别 | 文档位置 | 问题描述 | 修复 |
|---|---|---|---|---|
| 12 | 约定违规 | 7.1 节回滚表（10 处） | 全部用裸 `git checkout`，违反"git 命令必须通过 git_guard.py 封装"约定 | 改为 `python scripts/git_guard.py checkout` |
| 13 | 内部不一致 | 3.1 节 #2 vs 附录 A.1 #2 | sync_yaml_to_depgraph.py 行号：3.1 写"441, 51"，A.1 写"51, 441, 438"，3.1 漏 438 | 3.1 补为"51, 438, 441, 全文" |
| 14 | 数量错误 | 1.3 节 | "派生副本漂移位置 7 处"但 3+3+1+2=9 | 7→9 |
| 15 | 完整性遗漏·重大 | 3.7 节 | kebab 引用清单遗漏 18 个活文件（validate_vocabulary_coverage.py / validate_architecture.py / 3 个 index.md / 4 个 registry / 2 个脚本 / 2 个规则 / 4 个其他） | 新增 3.7.1 节列 #48-#65 + 执行时重 Grep 命令 + 3.8 统计更新为 62+ |

### B.3 第 3 轮审查（2026-06-26，发现 2 个问题，已全部修复）

本轮为确认轮——检查第 1、2 轮修复是否引入新问题，以及是否有遗漏的维度。经全文档复审发现 2 个新问题：

| # | 类别 | 文档位置 | 问题描述 | 修复 |
|---|---|---|---|---|
| 16 | 命令错误·重大 | 3.7.1 节执行命令 | 用 `python scripts/git_guard.py grep -rn ...`，但 git_guard.py 的 DANGEROUS_SUBCOMMANDS 不含 grep，会透传为 `git grep`——(1) 仅搜 git-tracked files 漏掉 untracked 活文件；(2) 不支持 `\|` 语法（git grep 用 --or）；(3) 不支持 `-rn`、`--include`、多目录参数 | 改用 `rg -n ... -g "*.py" -g "*.yaml" ...`，附注释说明 git_guard.py 透传陷阱 |
| 17 | API 未验证·重大 | 5.1.1 节动作 1 | `TaskRepository(governance_db=...)` 参数名错误——实际构造函数（task_repo.py:608）参数名是 `db_path`，无 `governance_db` 关键字参数；且未标注 transition 方法签名 | 改为 `TaskRepository(db_path=...)`，补注释标明构造函数和 transition 完整签名及代理模块说明 |

### B.4 第 4 轮审查（2026-06-26，发现 1 个问题，已修复）

本轮为确认轮——重点验证第 3 轮修复（rg 命令、TaskRepository API）是否引入新问题，并复查 DAG 时序与表格一致性。第 3 轮修复未引入新问题，但复查 DAG 时发现 1 个遗留不一致：

| # | 类别 | 文档位置 | 问题描述 | 修复 |
|---|---|---|---|---|
| 18 | 内部不一致 | 9.1 节任务卡清单 vs 9.2 节 DAG 图 | 2630 的依赖列只写了"2629"，但 DAG 图显示 2630 同时接收 2629 和 2626 两个入边（2626 triage 修复独立汇入 2630 测试验证）。2630 阶段 9 的 `test_triage_vocab_consistency.py` 需要 2626 先完成，否则测试会失败 | 2630 依赖改为"2629, 2626" |

### B.5 第 5 轮审查（2026-06-26，0 个问题）

本轮为确认轮——验证第 4 轮修复（2630 依赖改为"2629, 2626"）是否引入新问题，并全面复查遗漏维度。

检查维度与结论：
1. **第 4 轮修复验证**：2630 依赖"2629, 2626"与 9.2 节 DAG 图（2629→2630 + 2626→2630）完全一致 ✓
2. **全部 10 张任务卡依赖 vs DAG 一致性**：2621~2630 逐张核对，全部一致 ✓
3. **裸 git 命令检查**：全文档 Grep `^(git|git checkout|...)` 无命中，所有 git 操作均通过 `python scripts/git_guard.py` 封装 ✓
4. **vocabulary 文件数 24/26 一致性**：24 个 *_vocabulary.yaml（有 vocabulary_name 键）+ glossary.yaml + terminology_mapping.yaml = 26 个总 YAML，文档各处用法自洽 ✓
5. **附录 C 议题编号完整性**：#ARCH-008/009/010/011 + 裁定 #206（含 #206-A~D）齐全 ✓
6. **验证标准完整性**：6.1 单元测试 / 6.2 集成验证 / 6.3 三方对齐 / 6.4 循环验收 四节完整，5.8.4 验证命令引用有效 ✓

**结论**：0 个问题。

### B.6 第 6 轮审查（2026-06-26，0 个问题）

本轮为最终确认轮——因第 5 轮未做任何修改（0 问题无需修复），本轮重点确认第 5 轮结论的可重复性。

复查要点：
1. **第 5 轮无修改 → 不可能引入新问题** ✓
2. **抽查 3.7.1 节 rg 命令语法**：`rg -n "pattern" -g "*.py" -g "*.yaml" -g "*.json" -g "*.md" <dirs> | rg -v "..."`——ripgrep 语法正确（`|` 正则 OR、`-g` glob、多目录、管道过滤）✓
3. **抽查 5.1.1 节 TaskRepository API**：`TaskRepository(db_path=...)` 参数名与 task_repo.py:608 构造函数签名一致；`repo.transition(task_id, to_status_str)` 与 task_repo.py:1463 签名一致（to_status 接受 str 自动转 TaskStatus）✓
4. **抽查回滚方案 7.1-7.3**：10 个阶段回滚 + 紧急回滚 + 完全回滚，全部用 `python scripts/git_guard.py checkout/revert` 封装 ✓
5. **DAG 图与 9.1 表格最终一致性**：10 张卡 + 依赖列全部匹配 ✓

**结论**：0 个问题。

### B.7 收敛条件达成

连续 2 轮（第 5 轮 + 第 6 轮）0 问题，达成收敛条件。

审查进度：第 1 轮 11 问题 → 第 2 轮 4 问题 → 第 3 轮 2 问题 → 第 4 轮 1 问题 → **第 5 轮 0 问题** → **第 6 轮 0 问题** ✓ 收敛。

文档已提交用户批准。

---

## 附录 C：相关议题与裁定编号申请

| 编号 | 类型 | 标题 | 状态 |
|---|---|---|---|
| #ARCH-008 | 议题 | vocabulary 同步链路根因性失效（8 个 bug） | 待裁定 |
| #ARCH-009 | 议题 | layer 命名体系统一为 layer_vocabulary.yaml 16 值 | 待裁定 |
| #ARCH-010 | 议题 | apply_depgraph.py ALLOWED_LAYERS 与 DB CHECK 对齐 | 待裁定 |
| #ARCH-011 | 议题 | layer_vocabulary.yaml 新增 dir_prefix 字段（根本方案） | 待裁定 |
| #206 | 裁定 | vocabulary 同步链路根因性修复（含 #206-A~D 子裁定） | 待批准 |

---

## 文档变更历史

| 版本 | 日期 | 修订内容 | 作者 |
|---|---|---|---|
| v1.0 | 2026-06-26 | 初版，基于 5 路并行深度调研综合编写 | AI Architect |
| v1.1 | 2026-06-26 | 6 轮循环审查修复 18 个问题：行号勘误（Bug D 行 180→182、panorama 1989→1993）、工具路径修正（lock_files.py/task_repo.py/batch_review.py）、数量勘误（漂移 7→9、deprecated 6→7、schema oneOf 15→16）、DAG 依赖修正（2630 补 2626 依赖）、API 签名验证（TaskRepository db_path）、rg 命令替换（git_guard.py grep→rg）、kebab 引用补遗（+18 文件→62+）。详见附录 B.1~B.6 | AI Architect |
