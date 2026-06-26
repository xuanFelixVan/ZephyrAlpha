---
doc_type: audit_report
title: "向内收4原则审查报告 — docs/01_policies_and_standards"
status: in_progress
ttl: task_bound
created_by: agent
created_at: 2026-06-26
owner: ZephyrAlpha-Owner
layer: cross_layer
module_id: AUDIT-INWARD-001
tags:
  - audit-report
  - inward-convergence
  - policies-and-standards
  - circadian-scheduler
  - orphan-cleanup
  - p3-deep-audit
summary: "对 docs/01_policies_and_standards 及子目录用向内收4原则审查，完成 P0-P2-4 + 遗留1-2 + P3 深入文档级治理（索引一致性/词表硬编码/frontmatter字段/模板一致性/幽灵引用）。本报告基于 git commit 历史重建+P3 实时记录。"
completes_when: "用户确认本次审查收尾后归档至 .runtime/working_archive/（P3 已全部完成，待用户确认）"
related_rationale:
  - "向内收4原则定义见 trae_060_inward_consolidation.yaml"
  - "审查范围：docs/01_policies_and_standards/ 全树"
---

# 向内收4原则审查报告

**审查日期**：2026-06-26
**审查范围**：`docs/01_policies_and_standards/` 及其全部子目录（policies/、rules/、_registry/、templates/）
**审查原则**：向内收4原则
1. **唯一真源**（Single Source of Truth）—— 消除重复副本，扩展已有而非创造新文件
2. **事件驱动**（Event-Driven）—— 废除定时轮询，改为事件触发
3. **第一性原理**（First Principles）—— 治本不治标，从根因解决问题
4. **新AI可发现性**（AI Discoverability）—— 规则必须有指针引用真源，新AI能定位

## 修复优先级总览

| 优先级 | 范围 | 状态 | 核心提交 |
|--------|------|------|----------|
| P0 | GitCommitGateway 缺口审查 | ✅ 完成 | `f0227f306` (auto-sync 标记) |
| P1 | scope 过滤重复 + GATE-ID-UNIQ 修复 | ✅ 完成 | `bb86302de`, `400c72586` |
| P2-1 | 删除 document_metadata_index_registry.yaml 真重 | ✅ 完成 | `ca88e472e` |
| P2-2 | 生成器解析逻辑修复（trae_047 代码头格式） | ✅ 完成 | `ab0a3f812` |
| P2-3 | L0 executors 补全 + 词表硬编码修复 | ✅ 完成 | `a83044260`, `798520d99` |
| P2-4 | CircadianScheduler 完整迁移废除 | ✅ 完成 | `c4f4f3791d` |
| 遗留1 | stale_task_recovery 文档更新（事件驱动覆盖） | ✅ 完成 | `3c67cd296e` |
| 遗留2 | 孤儿文件清理（4个 __init___from_orches.py） | ✅ 完成 | `3c67cd296e` |
| P3 | 文档级治理（索引一致性/词表硬编码/frontmatter/模板/幽灵引用） | ✅ 完成 | `52084d4db9`, `8725de30c3` |
| F1 | trae_056/059 可选字段补全（references/enforcement/metadata/provenance） | ✅ 完成 | 本次提交 |
| F2 | catalog 生成器恢复+重新生成（generate_rule_catalog.py 修复5个bug） | ✅ 完成 | 本次提交 |

---

## P0 — GitCommitGateway 缺口审查

**提交**：`f0227f306` (session: p0-review-gateway-gaps-20260626)

**审查内容**：GitCommitGateway 作为项目唯一合法 git commit 入口，检查其门禁覆盖完整性。

**结果**：P0 级阻塞问题已在 P0 阶段清零，后续 P1-P2 修复均通过 GitCommitGateway 提交验证。

---

## P1 — scope 过滤重复 + GATE-ID-UNIQ 修复

### P1-1: 提取 _in_audit_scope() 单一真源

**提交**：`bb86302de` (Fix 1)

**问题**：scope 过滤逻辑在多处重复实现，违反唯一真源原则。

**修复**：提取 `_in_audit_scope()` 为单一真源方法，消除 scope 过滤重复。

### P1-2: GATE-ID-UNIQ registry 空格手误修复

**提交**：`400c72586`

**问题**：GATE-ID-UNIQ registry 中存在空格手误（`scripts/` 与 `scripts/` 不一致）。

**修复**：修正空格手误，补通用词扩展提示。此修复被并发 session sweep 提交，本次提交仅修正空格。

### P1-3: GATE-ID-UNIQ 引号绕过漏洞修复

**提交**：`7b708ab63`

**问题**：GATE-ID-UNIQ 钩子存在引号绕过漏洞。

**修复**：修复引号绕过漏洞 + AGENTS.md 补注册门禁（红蓝对抗修改）。

### P1-4: ttl decision_tree 机器可读化

**提交**：`9463dd11a`

**问题**：ttl decision_tree 非机器可读，内容判定逻辑不治本。

**修复**：ttl decision_tree 机器可读化 + 内容判定治本。

---

## P2-1 — 删除 document_metadata_index_registry.yaml 真重

**提交**：`ca88e472e` (session: p2-1-doc-metadata-delete)

**问题**：`document_metadata_index_registry.yaml` 是真重（与另一个 registry 内容重复），违反唯一真源原则。

**修复**：向内收删除该文件，保留权威 registry。

**验证**：post-commit auto-sync `c6c5dda7a` 确认无破坏性影响。

---

## P2-2 — 生成器解析逻辑修复

**提交**：`ab0a3f812` (session: p2-2-generator-parser)

**问题**：`trae_047` 代码头格式不被生成器解析支持，`CFG-` 前缀无法识别，存在自跳过 bug。

**修复**：
- 修复生成器解析逻辑，支持 `trae_047` 代码头格式
- 支持 `CFG-` 前缀
- 修复自跳过 bug

**验证**：post-commit auto-sync `985a3057d` 确认生成器输出正常。

---

## P2-3 — L0 executors 补全 + 词表硬编码修复

### P2-3a: L0 空 executors 补全

**提交**：`a83044260` (session: p2-3-l0-executors)

**问题**：6条规则的 `enforcement executors` 为空数组，导致线上约束无机械执行路径（违反第一性原理——约束必须可机械验证）。

**修复**：补全 6条规则的 enforcement executors，执行脚本与 `trae_018` 同款。

**验证**：post-commit auto-sync `929656e52` 确认无破坏。

### P2-3b: 词表硬编码副本修复

**提交**：`798520d99` (session: p2-3-audit-update)

**问题**：trae_060 审计发现 13 处硬编码词表副本，违反唯一真源原则。

**修复**：
- 13处修复为64处2词表全量排查结果
- TRAE-042 引用 section 名同步

### P2-3c: 附加修复（P2-3 审计期间发现）

| 提交 | 修复内容 |
|------|----------|
| `6e0d0204a` | Fix 5: 向内收消除 `analyze_orphan_consumers.py` 重复消费者地图 |
| `63c65c44c` | 修复7个生成器脚本 doc_type 硬编码为合法值，防止 GATE-DOMAIN-DOC reconciler 重新生成时覆盖回非法值 |
| `dceeba447` | 修复 `_validate_ssot_linkage` 文档残留 + 补顶部 docstring 可发现性 |
| `e4cb24bcd` | split AGENTS.md L157 completes_when+reconciler into main line + indented sub-item for Grep visibility |
| `dcbffbdb1` | cure 6 inward-convergence audit violations（6处向内收审计违规修复：删除CN别名v4/删除冗余section 7 v6/移动R7-R8设计权衡到代码docstring v6/替换CLI cmd为capability_id指针v2+3/添加git add -A lesson v1） |

---

## P2-4 — CircadianScheduler 完整迁移废除

**提交**：`c4f4f3791d` (session: p2-4-circadian) — 33 files changed, 85 insertions(+), 2649 deletions(-)

**问题**：CircadianScheduler 是定时调度机制，违反事件驱动原则。MOD-INF-030 规则要求红蓝对抗验证器采用事件驱动触发，废除 CircadianScheduler 定时触发。

**修复范围**：
- 删除核心文件 3 个：`circadian_scheduler.py`、`circadian_tasks/` 目录、死数据文件
- 修改源文件 15 个：移除 CircadianScheduler import/调用/引用
- 更新测试 16 个：重写测试匹配事件驱动新机制
- 清理死数据：`schedule_state.json`、`schedule-state.json`
- 更新红蓝场景：`_scenario-registry.yaml` 中 CircadianScheduler 相关场景标记 deprecated

**事件驱动覆盖验证**：
- `Conductor.plan_cycle()` 在每次规划周期开始时调用 `recover_stale_claims()`（见 `src/zephyr/trading/conductor.py:79-98`）
- `register_boot_cron_jobs` 仅保留 `bus.subscribe("skill.freshness_critical")` 事件订阅
- 失去的只是"CircadianScheduler 不运行时的定时清理"——低风险回归，已被 Conductor 事件驱动覆盖

**6 个 [CONSUMERS] 注释漂移清理**（P2-4 主提交未覆盖的残余）：
- `src/zephyr/autonomy_core/skill_freshness_ext.py`
- `src/zephyr/trading/resource_optimization.py`
- `src/zephyr/security/adversarial_validation/commit_trigger.py`
- `src/zephyr/governance/audit_trail/pipeline_runner.py`
- `src/zephyr/governance/finding_ingest.py`
- `src/zephyr/governance/audit_orchestrator/pipeline_runner.py`

---

## 遗留1 — stale_task_recovery 文档更新

**提交**：`3c67cd296e` (session: cleanup-orphans)

**问题**：P2-4 废除 CircadianScheduler 后，`_scenario-registry.yaml` 中 stale_task_recovery 相关场景的 defense 描述仍指向已废除的定时调度，需更新为反映 Conductor 事件驱动覆盖现状。

**修复**：
- `RB-SCEN-045` defense 更新为：`"transition() DM-401 warning + Conductor.plan_cycle recover_stale_claims 事件驱动 + session close IN_PROGRESS=0 check"`
- `RB-SCEN-046` defense 更新为：`"circadian_scheduler 已废除（2026-06-26），本攻击向量失效；Conductor.plan_cycle() 已事件驱动覆盖 recover_stale_claims"`
- `[CHANGE-NOTE]` 更新为：`Conductor.plan_cycle() 已事件驱动覆盖 recover_stale_claims`
- `tests/unit/db/test_dm400_stale_task_fix.py` docstring 更新为：`recover_stale_claims 方法（Conductor.plan_cycle 事件驱动覆盖，CircadianScheduler 定时注册已废除）`

---

## 遗留2 — 孤儿文件清理

**提交**：`3c67cd296e` (session: cleanup-orphans) — 10 files changed, 9 insertions(+), 520 deletions(-)

**问题**：4 个 `__init___from_orches.py`（三下划线变体名）文件无任何 import 引用，是历史迁移遗留的孤儿文件。

**验证**：`grep -r "import.*__init___from_orches"` 返回空，确认无消费者。

**修复**：
- 删除 4 个孤儿文件：
  - `src/zephyr/autonomy_core/__init___from_orches.py` (238行)
  - `src/zephyr/integration/__init___from_orches.py` (109行)
  - `src/zephyr/integration/governance/__init___from_orches.py` (35行)
  - `src/zephyr/trading/__init___from_orches.py` (129行)
- 更新 4 个 [CONSUMERS] 注释（`zephyr.integration.governance.__init___from_orches` → `zephyr.integration.governance`，指向真正的消费者 `__init__.py` 的 `__all__` 导出）：
  - `src/zephyr/integration/governance/protocol.py:5`
  - `src/zephyr/integration/governance/phase_hold.py:5`
  - `src/zephyr/integration/governance/governance_adapter.py:5`
  - `src/zephyr/integration/governance/auditor.py:5`

**Import 验证**：`from zephyr.integration.governance import protocol, phase_hold, governance_adapter, auditor` 通过。

---

## P3 — 深入文档级治理

**状态**：✅ 完成
**提交**：`52084d4db9`（批次1-3：索引+词表硬编码+L编号）、`8725de30c3`（批次4-7：ttl批量+结构修复+幽灵引用+gateway修复）

用户指令"确认执行需要深入 P3 审查，执行所有遗留工作"后，对 docs/01_policies_and_standards/ 全树执行完整向内收4原则审查。

### P3-1: policies/ vs rules/ 结构审查

**问题**：
- `parallel_session_coordination_policy.md` frontmatter 重复 `ttl: permanent`（第5行+第27行）
- `templates/protocol_template.md` 引用已废弃 doc_type（protocol 已 migrated_to policy，2026-06-26 裁定）
- `index.md` 目录树仍列 protocol_template.md，计数 11 未更新
- `templates/index.md` 计数 10 但仍列 protocol_template.md（三重不自洽）

**修复**：
- 删除重复 ttl（第27行）
- 删除 `protocol_template.md`（无现存 protocol 文档依赖，catalog 中 2 条 active 条目指向已删除的 governance/ 目录=stale）
- `templates/index.md` 计数 10→9，移除 protocol 行，policy 行标注"含已废弃 protocol 类型"
- `index.md` 目录树移除 protocol 行，计数 11→10

### P3-2: _registry/ 索引一致性

**问题**：
- 顶层 `_registry/index.md` 计数全面过期（catalogs 20→26, contracts 3→4, vocabularies 12→30, schemas 3→3）
- 幽灵链接 `registry-master-index.yaml`（应为 `registry_master_index.yaml`，snake_case 硬约束）
- `vocabularies/index.md` 三重不自洽（计数11≠目录24≠实际29），13处连字符幽灵命名
- `contracts/index.md` 2处连字符（model-capability-contract→model_capability_contract）
- `schemas/index.md` 1处连字符（session-log-schema→session_log_schema）

**修复**：
- 顶层 index 计数全量更新，幽灵链接修正，排除规则更新
- `vocabularies/index.md` 完全重写，13处连字符→下划线，5个孤儿文件补充，计数11→29
- `contracts/index.md` + `schemas/index.md` 连字符修正

### P3-3: layer 词表硬编码（唯一真源违规）

**问题**：4处完整16值 layer 硬编码副本，违反"合法值集合必须从YAML词表动态加载"铁律：
- `_registry/contracts/architecture_contract.yaml:130`（layer allowed_values 内联16值）
- `_registry/catalogs/frontmatter_field_registry.yaml:180`（layer enum_values 内联16值）
- `rules/trae_043_meta_rule_metadata.yaml:610`（layer values 内联16值）
- `_registry/contracts/contract_mapping_table.yaml`（20处废弃L编号 L00/L03/L05...替代合法层名）

**修复**：
- 3处YAML硬编码改为 `"DYNAMIC_FROM_SSOT"` 指针引用（指向 `layer_vocabulary.yaml` 真源）
- `contract_mapping_table.yaml` 20处L编号修正为合法层名（L00→data, L03→signal, L05→pf_core, L06→ex_core, L07→reporting, L08→frontend, L10→compliance, L11→ml_train, L13→simulation）
- `frontmatter_schema.json` 确认为自动生成派生物，不改（生成器读取 field_registry 真源）

### P3-4: frontmatter 字段一致性

**审查**：扫描 60 个 rules/*.yaml 的 frontmatter 字段集

**结果**：
- ✅ 所有 60 文件的 12 个必填字段全齐备（rule_id/title/version/layer/module_id/ttl/stability/safety_level/ai_autonomy/severity/scope/domain）
- ✅ 17 个字段 100% 一致（含 ttl: permanent，本次批量补充）
- ⚠️ 可选字段差异（设计性，非违规）：provenance 59/60（trae_059缺）、enforcement/references/metadata 58/60（trae_056/059缺，新规则未补全可选字段）—— **已于 F1 修复**：trae_056 补全 `references`/`enforcement`/`metadata`，trae_059 补全 `provenance`/`references`/`enforcement`/`metadata`，现 60/60 全齐备

### P3-5: templates/ 模板一致性

**审查**：扫描 9 个模板（删除 protocol_template 后）的 frontmatter 字段集

**结果**：
- ✅ 13 个核心字段 9/9 全一致（layer/status/language/date/title/summary/module_id/ttl/version/doc_type/owner/classification/created_by）
- ✅ 可选字段差异属模板类型设计差异（blueprint 模板有独有字段如 generation/file_manifest/ssot_claims；risk_register/roadmap 模板较简洁）

### P3-6: rules/_index.yaml + ttl 批量补充

**问题**：60 个规则文件全量缺失 `ttl` 字段（project_memory 硬约束：所有 .md 文档 frontmatter 必须包含 ttl）

**修复**：Python 脚本批量在 `stability:` 行前插入 `ttl: permanent`，60 文件全量补充

**设计决策记录（不修改）**：
- `_index.yaml` 的 layer 字段用 L0/L1/L2 治理层级，文件用 compliance 架构层——语义不同，非冲突
- TRAE-057 severity=error（L0层但非critical）——设计决策

### P3-FIX-8: registry_consistency_contract 幽灵引用

**问题**：`_registry/catalogs/registry_consistency_contract.yaml` 中 11 处路径用连字符+错误扩展名（.md 而非 .yaml），2个条目指向不存在文件

**修复**：
- 11处路径修正（连字符→下划线, .md→.yaml）
- 删除 REG-010（虚构 script-health-registry）
- 删除 REG-013（已删除 document-metadata-index-registry）
- 添加 CHANGE-NOTE 警告：本文件 REG-XXX ID 体系与 registry_master_index.yaml 的 CFG-*/PS-REG-* 体系不同，最新真源以 registry_master_index.yaml 为准

### P3 阻塞修复: git_commit_gateway 缺失导入

**问题**：`src/zephyr/governance/git_commit_gateway.py:459` 使用 `make_rules_integrity_reconciler` 但 import 块（79-89行）未导入该函数，导致 GitCommitGateway 初始化 NameError，阻塞所有 commit

**修复**：import 块添加 `make_rules_integrity_reconciler`（第89行后插入），gateway 初始化验证通过

### P3-FIX-9: rule_catalog_registry stale 条目清理

**问题**：`_registry/catalogs/rule_catalog_registry.yaml` 自 2026-05-07 后未重新生成，153 条目中 113 条（74%）指向已删除的 `domains/`、`governance/`、`operational/` 目录文件。生成器脚本 `generate_rule_catalog.py` 已归档至 `scripts/_archive/`。

**修复**：手动清理 113 条 stale 条目（文件不存在的条目全部删除），`total_files` 154→40，`generated_at` 更新，添加 CHANGE-NOTE。清理后 0 stale，YAML 验证通过。

**遗留**：~~生成器已归档，catalog 现为手动维护。如需恢复自动生成，需从 `scripts/_archive/` 恢复 `generate_rule_catalog.py` 并适配当前目录结构。~~ **已于 F2 修复**：生成器已恢复至 `scripts/governance/d3_metadata/generate_rule_catalog.py` 并修复 5 个 bug（输出路径连字符→下划线、REPO_ROOT 改用 `zephyr.shared.io.paths` SSoT、移除已删除的 `--metadata-output` 功能、修复文件写入模式 bug、适配 `parse_frontmatter` 返回 tuple 的 API 变更），重新运行生成 84 条目 0 stale 的 catalog。

### P3-验证扫描（V1-V4）

提交后执行 4 项验证扫描确认修复落盘：
- **V1 ttl 落盘**：60/60 规则文件 `ttl: permanent` 全部存在 ✓
- **V2 protocol 残留**：`protocol_template.md` 已删除，无硬编码枚举副本残留 ✓
- **V3 索引计数自洽**：9 模板+1 index=10（index.md ✓）、9 模板（templates/index.md ✓）、60 规则 ✓、_registry 计数全对 ✓
- **V4 layer 硬编码**：4 文件含 10+ layer 值，经检查均为合法数据值（目录登记/映射表/命名规则引用），非硬编码枚举副本 ✓

### P3 次要发现（已修复）

- **F1 可选字段缺失**（已修复）：trae_056 补全顶层 `references`/`enforcement`/`metadata`；trae_059 补全 `provenance`/`references`/`enforcement`/`metadata`。trae_056 的 `references.rule_ids` 列出 14 个依赖规则，`enforcement.executors` 指向 `scaffold.py`/`lock_files.py`；trae_059 的 `enforcement.gate_id` 指向 `G_TRAE_059`，`metadata.modification_permission` 为 `immutable_core`（与 `ai_autonomy: immutable_core` 一致）。现 60/60 规则可选字段全齐备。
- **F2 生成器归档**（已修复）：从 `scripts/_archive/` 恢复 `generate_rule_catalog.py` 至 `scripts/governance/d3_metadata/`，修复 5 个 bug：(1) 输出路径 `rule-catalog-registry.yaml`（连字符）→ `rule_catalog_registry.yaml`（snake_case 硬约束）；(2) REPO_ROOT 从 `Path(__file__).resolve().parent.parent.parent.parent`（归档位置计算错误）→ 从 `_shared.constants` 导入（SSoT 链：`zephyr.shared.io.paths.REPO_ROOT` → `_shared.constants` re-export → 脚本 import）；(3) 移除 `--metadata-output` 功能（目标文件 `document-metadata-index-registry.yaml` 已在 P2-1 删除）；(4) 修复文件写入模式 bug：`open(tmp_path, encoding="utf-8")`（默认读模式）→ `open(tmp_path, "w", encoding="utf-8")`；(5) 适配 `parse_frontmatter` API 变更：函数返回 `(metadata, body)` 元组，原代码按 dict 使用导致 `AttributeError`。重新运行生成 84 条目 0 stale 的 catalog。

---

## 审查统计

| 指标 | 数值 |
|------|------|
| 审查范围 | `docs/01_policies_and_standards/` 全树 |
| 修复优先级 | P0-P2-4 + 遗留1-2 + P3 深入文档级治理 + 验证扫描 + F1/F2 收尾 |
| 总提交数 | 19+ 个相关 commit（含 P3 三个批次提交+catalog清理+F1/F2 收尾） |
| 总文件变更 | 138+ 文件（P3: 66文件批次4-7 + catalog清理 + 审查报告 + F1: trae_056/059 + F2: 生成器恢复+catalog重新生成） |
| 总代码删除 | 3000+ 行（CircadianScheduler 废除）+ protocol_template.md 废弃 + 113条stale catalog条目 |
| 验证方式 | git commit 历史 + import 验证 + post-commit auto-sync + frontmatter 字段扫描 + V1-V4 落盘验证 + F1/F2 字段落盘验证 + catalog 84条目0 stale 验证 |

## 审查原则落地情况

| 原则 | 落地证据 |
|------|----------|
| **唯一真源** | P2-1 删除重复 registry；P2-3 修复词表硬编码副本；遗留2 删除孤儿文件；P3-3 修复3处layer词表硬编码为DYNAMIC_FROM_SSOT指针；P3-1 删除废弃protocol_template；P3-FIX-8 修正11处幽灵引用+删除2个虚构条目；F2 生成器 REPO_ROOT 改用 `zephyr.shared.io.paths` SSoT 链（不再用 `Path(__file__).parents[N]` 推算） |
| **事件驱动** | P2-4 完整废除 CircadianScheduler 定时调度，迁移至 Conductor.plan_cycle() 事件驱动 |
| **第一性原理** | P2-3 补全 L0 executors 机械执行路径；P1-4 ttl decision_tree 机器可读化治本；P3 阻塞修复 git_commit_gateway 缺失导入（治本：从根因解决commit阻塞）；F2 修复生成器 5 个 bug 治本（非手动维护 catalog），F1 从规则执行模型理解出发补全可选字段 |
| **新AI可发现性** | P2-3 修复 docstring 可发现性；AGENTS.md 补注册门禁；[CONSUMERS] 注释指向真正消费者；P3-2 修复索引计数+连字符幽灵命名（新AI按索引找文件不会落空）；P3-6 60规则补ttl字段（新AI可判断生命周期）；F1 补全 trae_056/059 的 `references`/`enforcement`/`metadata`（新AI可定位规则依赖与执行器）；F2 恢复生成器使 catalog 自动同步（新AI新增规则后 catalog 自动更新，无需手动维护） |

---

## 注意事项

1. **报告重建限制**：本报告 P0-P2-3 基于 git commit 历史重建，P2-4/遗留1-2/P3 有完整的对话上下文记录。如需更详细的修复前后对比，请查阅对应 commit 的 `git show <hash>`。

2. **并发 session 影响**：审查期间有其他 session（`rb3-cure`、`rb-fix-iduniq`、`trae-ttl-rejudge`、`parents-fix-b6` 等）并发提交，部分 auto-sync commit 是其他 session 的 post-commit 触发。P3 提交期间 HEAD 被推进多次，但本 session 的 commit 均在历史中。

3. **报告曾被误删**：本报告在 `112e50f556` 提交后，被 `541824d12b` 的 ghost-ref reconciler 误删（因 `status: completed` + `ttl: task_bound` 被判定为 ghost）。P3 阶段从 git 历史恢复并设 `status: in_progress` 防止再次误删。

4. **P3 已完成**：用户指令"确认执行需要深入 P3 审查，执行所有遗留工作"后，P3 全部完成。P3-1 到 P3-6 + P3-FIX-8 + 阻塞修复，覆盖索引一致性/词表硬编码/frontmatter字段/模板一致性/幽灵引用/gateway修复。待用户确认后归档。
