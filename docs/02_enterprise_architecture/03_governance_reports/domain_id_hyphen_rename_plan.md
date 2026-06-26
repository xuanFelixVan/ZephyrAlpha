---
ttl: permanent
---

# 6 域 ID 连字符→下划线改名执行方案（施工细节版 v1）

> **文档定位**：统一域 ID 命名风格，消除 NR-002 违规（连字符→下划线）的详细执行方案
> **制定日期**：2026-06-26
> **版本**：v1（基于深度调研 + 精确扫描）
> **方案性质**：待用户批准后执行
> **依据**：NR-002 命名规则 + 第一性原理分析 + 精确影响扫描（修正 MOD-XXX 子串误匹配）
> **任务卡**：已生成 14 张任务卡（7 主卡 + 7 元审查卡），见 [domain_id_hyphen_rename_taskcards/index.md](domain_id_hyphen_rename_taskcards/index.md)
>
> **裁定#208 阶段D 追加说明（2026-06-26）**：本文档中提到的模块 ID `MOD-LLM_SECURITY` 已于裁定#208 阶段D 重编号为派生轨 ID `MOD-LLM_SECURITY`（蓝图+实现统一）。本文档保留旧名 `MOD-LLM_SECURITY` 作为历史扫描结果上下文，仅作可追溯性保留，不再代表当前实际 module_id。同理，文档中其他模块 ID（如 MOD-GOV-SCRIPTS、MOD-INTEGRATION-GATEWAY）如有后续重编号亦以裁定#208 产出物为准。

---

## 第一部分：裁定概述

### 1.1 问题总数量：8 个域

| # | 域 ID | 问题类型 | 严重度 | 本次处理 |
|---|---|---|---|---|
| 1 | D-GOV-DOCS | NR-002 违规（连字符） | error | **执行** |
| 2 | D-GOV-ENFORCEMENT | NR-002 违规（连字符） | error | **执行** |
| 3 | D-GOV-SCRIPTS | NR-002 违规（连字符） | error | **执行** |
| 4 | D-GOV_AUDIT_TESTS | NR-002 违规 + NR-001 盲区 | error | **执行** |
| 5 | D-INTEGRATION-GATEWAY | NR-002 违规（连字符） | error | **执行** |
| 6 | D-SECURITY-LLM | NR-002 违规（连字符） | error | **执行** |
| 7 | D-GOV_AUDIT | domain_name='audit-trail' 含连字符 | warning | **延期**（涉及物理目录） |
| 8 | D-OPS | domain_name='feedback-loop' 含连字符 | warning | **延期**（涉及物理目录） |

### 1.2 新裁定 #ARCH-REN-001：6 域 ID 改名

| 原域 ID | 新域 ID | domain_name | 改名理由 |
|---|---|---|---|
| D-GOV-DOCS | **D-GOV_DOCS** | architecture_docs | NR-002：连字符→下划线；GOV_DOCS 独立表达"治理文档"语义 |
| D-GOV-ENFORCEMENT | **D-GOV_ENFORCEMENT** | rule_enforcement | NR-002：连字符→下划线；GOV_ENFORCEMENT 独立表达"治理执行"语义 |
| D-GOV-SCRIPTS | **D-GOV_SCRIPTS** | code_dedup | NR-002：连字符→下划线；GOV_SCRIPTS 独立表达"治理脚本"语义 |
| D-GOV_AUDIT_TESTS | **D-AUDITTEST** | audit_test_suite | NR-002 修复 + **消除 NR-001 盲区**：D-GOV_AUDIT_TESTS 语义暗示 D-GOV_AUDIT 子域（GOV_AUDIT 段匹配 D-GOV_AUDIT），改为独立 ID D-AUDITTEST |
| D-INTEGRATION-GATEWAY | **D-INTEGRATION_GATEWAY** | mcp_servers | NR-002：连字符→下划线；INTEGRATION_GATEWAY 独立表达"集成网关"语义 |
| D-SECURITY-LLM | **D-SECURITY_LLM** | llm_defense | NR-002：连字符→下划线；SECURITY_LLM 独立表达"安全 LLM 防御"语义 |

### 1.3 延期项说明（#7-#8）

| 域 ID | domain_name 现状 | 延期理由 |
|---|---|---|
| D-GOV_AUDIT | audit-trail → audit_trail | 'audit-trail' 不仅是 domain_name，还对应物理目录 `src/zephyr/governance/audit_trail/`（已用下划线）和 nodes.subdomain_id 63 行。但 'audit-trail' 字符串在 30+ 脚本文件中作为路径/模块名出现（如 `src/zephyr/feedback-loop/`），涉及目录重命名和 import 路径变更，风险远大于 ID 文本替换 |
| D-OPS | feedback-loop → feedback_loop | 'feedback-loop' 对应物理目录 `src/zephyr/feedback-loop/`，在 scripts/ 中 20+ 处引用（add_file_headers.py, auto_sync_all_registries.py, scaffold.py 等），需单独分析目录重命名影响 |

**延期项处理**：本方案完成后，另立 `domain_name_hyphen_rename_plan.md` 单独处理 #7-#8。

### 1.4 NR 规则合规性验证（6 新 ID）

| NR 规则 | D-GOV_DOCS | D-GOV_ENFORCEMENT | D-GOV_SCRIPTS | D-AUDITTEST | D-INTEGRATION_GATEWAY | D-SECURITY_LLM |
|---|---|---|---|---|---|---|
| NR-001 无父子前缀 | ✅ GOV 段不匹配任何已存在域（无 D-GOV 域，仅有 D-GOVERNANCE） | ✅ 同左 | ✅ 同左 | ✅ 无下划线，不适用 | ✅ INTEGRATION 段不匹配 D-INTEGRATION（不同字符串） | ✅ SECURITY 段不匹配 D-SECURITY（不同字符串） |
| NR-002 全大写下划线 | ✅ `^D-[A-Z][A-Z0-9_]*$` | ✅ | ✅ | ✅ | ✅ | ✅ |
| NR-003 语义独立性 | ✅ GOV_DOCS 独立 | ✅ GOV_ENFORCEMENT 独立 | ✅ GOV_SCRIPTS 独立 | ✅ AUDITTEST 独立 | ✅ INTEGRATION_GATEWAY 独立 | ✅ SECURITY_LLM 独立 |
| NR-005 中文名一致 | ✅ architecture_docs | ✅ rule_enforcement | ✅ code_dedup | ✅ audit_test_suite | ✅ mcp_servers | ✅ llm_defense |

**新 ID 冲突检查**：6 个新 ID 均不在现有 53 域列表中（已逐一核对），`--rename-domain` 的"禁止覆盖"校验将二次确认。

---

## 第二部分：第一性原理分析

### 2.1 为什么必须改名

项目硬约束（project_memory）：
> "域ID格式必须为全大写+下划线，禁止使用连字符或小写字母"

NR-002（severity=error）：
> "域ID格式必须为 D- 前缀 + 全大写字母+数字+下划线（^D-[A-Z][A-Z0-9_]*$），禁止使用连字符"

当前 6 个域 ID 使用连字符（D-GOV-DOCS 等），违反 NR-002。在 100% AI 开发项目中，AI 依赖命名语义判断域归属——连字符风格的 D-GOV-DOCS 与下划线风格的 D-GOV_AUDIT 混用，AI 无法从命名推断"是否同一族域"。

### 2.2 为什么 D-GOV_AUDIT_TESTS 需要改为 D-AUDITTEST 而非 D-GOV_AUDIT_TESTS

D-GOV_AUDIT_TESTS 含两段下划线：GOV / AUDIT / TESTS。NR-001 仅检查第一段（GOV），GOV 不匹配任何已存在域，故 NR-001 字面通过。但语义上，"GOV_AUDIT" 段匹配已存在域 D-GOV_AUDIT，暗示 TESTS 是 GOV_AUDIT 的子域——这是 NR-001 的**盲区**。

改名 D-AUDITTEST（无下划线，单段 ID）彻底消除此歧义。

### 2.3 改名安全性分析

| 维度 | 结论 |
|---|---|
| ssot_path 是否含域 ID | ❌ 6 域的 ssot_path 均不含域 ID 字符串（如 docs/02_enterprise_architecture/、src/zephyr/governance/rule_enforcement/），改名不影响路径映射 |
| 物理目录是否需重命名 | ❌ 不需要。文件名已用 snake_case（如 32_d_gov_docs.md），不含域 ID |
| src/ [DOMAIN] 声明 | ❌ 0 匹配。6 域在 src/ 下无 [DOMAIN] 声明行（仅有 [BLUEPRINT] MOD-XXX 模块 ID 头，模块 ID 不改） |
| 新 ID 是否冲突 | ❌ 6 个新 ID 均不在现有 53 域中 |
| 改名顺序依赖 | ❌ 无。6 个旧 ID 互不为子串（D-GOV-DOCS 不是 D-GOV-SCRIPTS 的子串），B1 兜底 REPLACE 无误伤风险 |

---

## 第三部分：影响范围（精确统计）

### 3.1 总体统计

| 类别 | 数量 | 处理方式 |
|---|---|---|
| DB 行数（6 域合计） | **4323 行** | `apply_depgraph.py --rename-domain`（17 步 + B1 兜底） |
| 手动修改文件（去重后） | **17 个文件** | 直接替换 / 追加说明 |
| 生成制品（重新生成） | **~15+ 个文件** | DB 改名后重新运行生成器 |
| src/ [DOMAIN] 声明 | **0** | 无需改 |
| 物理目录重命名 | **0** | 无需改 |

### 3.2 DB 修改清单（6 域 × 11 表 + B1 兜底，4323 行）

| 域 ID | domains | nodes.domain_id | nodes.subdomain_id | nodes.belongs_to | nodes.owner | arch_directory_tree | arch_path_mappings | domain_mapping | 小计 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| D-GOV-DOCS | 1 | 127 | 127 | 127 | 127 | 245 | 2 | — | **756** |
| D-GOV-ENFORCEMENT | 1 | 107 | 107 | 107 | 107 | 1 | 6 | — | **436** |
| D-GOV-SCRIPTS | 1 | 416 | 108+392 | 356+144 | 356+144 | 1+587 | 12 | — | **2517** |
| D-GOV_AUDIT_TESTS | 1 | 152 | — | — | — | 1 | 2 | — | **156** |
| D-INTEGRATION-GATEWAY | 1 | — | 82 | 81 | 81 | 1 | 6 | — | **252** |
| D-SECURITY-LLM | 1 | — | 63+5 | 63 | 63 | 1 | 6 | 4 | **206** |
| **合计** | **6** | **802** | **884** | **878** | **878** | **837** | **34** | **4** | **4323** |

**说明**：
- `nodes.owner` 列不在 17 步枚举中，但 B1 兜底扫描（`_scan_replace_all_text_columns`）会覆盖所有 TEXT 列
- `nodes.subdomain_id` 的"前缀匹配"行（如 D-GOV-SCRIPTS-META）由 B1 兜底的 REPLACE+LIKE 处理
- `arch_directory_tree.domain_id` 的前缀匹配行同理由 B1 处理
- B1 排除 3 表：`domain_naming_rules`（规则示例有意保留旧名）、`_schema_version`、`governance_audit_logs`
- B1 排除 3 列：`blueprint_id`、`path`、`blueprint_path`（由专门步骤处理）

### 3.3 代码文件修改清单（0 个文件）

**确认**：src/ 下 0 个 [DOMAIN] 声明需修改。所有 src/ 匹配均为 `[BLUEPRINT] MOD-XXX` 模块 ID 头（MOD-GOV-SCRIPTS、MOD-INTEGRATION-GATEWAY、MOD-LLM_SECURITY），模块 ID 不随域 ID 改名而变。

### 3.4 YAML registry 修改清单（1 个文件，7 行改）

**文件**：`docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml`

| 行号 | 原内容 | 新内容 | 所属域 |
|---|---|---|---|
| L27 | `- domain: D-GOV-ENFORCEMENT` | `- domain: D-GOV_ENFORCEMENT` | D-GOV-ENFORCEMENT |
| L54 | `- domain: D-GOV-SCRIPTS` | `- domain: D-GOV_SCRIPTS` | D-GOV-SCRIPTS |
| L212 | `- domain: D-SECURITY-LLM` | `- domain: D-SECURITY_LLM` | D-SECURITY-LLM |
| L757 | `- domain: D-INTEGRATION-GATEWAY` | `- domain: D-INTEGRATION_GATEWAY` | D-INTEGRATION-GATEWAY |
| L811 | `- domain: D-GOV-SCRIPTS` | `- domain: D-GOV_SCRIPTS` | D-GOV-SCRIPTS（重复条目） |
| L903 | `- domain: D-GOV_AUDIT_TESTS` | `- domain: D-AUDITTEST` | D-GOV_AUDIT_TESTS |
| L921 | `- domain: D-GOV-DOCS` | `- domain: D-GOV_DOCS` | D-GOV-DOCS |

### 3.5 生成器脚本修改清单（3 个文件，~5 处硬编码）

| # | 文件 | 行号 | 原内容 | 新内容 |
|---|---|---|---|---|
| 1 | scripts/governance/sync_yaml_to_depgraph.py | L706 | `VALUES (?, ?, 'file', 'D-GOV-DOCS', ?, 'design')` | `VALUES (?, ?, 'file', 'D-GOV_DOCS', ?, 'design')` |
| 2 | scripts/governance/d5_architecture/dm200912_rewrite_views.py | L829 | `("安全（横切）", "D-SECURITY, D-SECURITY-LLM, D-BEHAVIORAL_AUDIT, D-DATA_SEC, D-AUTONOMY_PERM")` | `("安全（横切）", "D-SECURITY, D-SECURITY_LLM, D-BEHAVIORAL_AUDIT, D-DATA_SEC, D-AUTONOMY_PERM")` |
| 2 | 同上 | L832 | `"D-INFRA_OPS, D-INFRA_RUNTIME, D-INTEGRATION, D-INTEGRATION-GATEWAY, D-SHARED, ..."` | `"D-INFRA_OPS, D-INFRA_RUNTIME, D-INTEGRATION, D-INTEGRATION_GATEWAY, D-SHARED, ..."` |
| 3 | scripts/governance/d5_architecture/generators/generate_capability_heatmap.py | L116 | `"domains": ["D-SECURITY", "D-SECURITY-LLM", ...]` | `"domains": ["D-SECURITY", "D-SECURITY_LLM", ...]` |
| 3 | 同上 | L127 | `"D-INTEGRATION-GATEWAY",` | `"D-INTEGRATION_GATEWAY",` |

### 3.6 手动维护文档修改清单

#### 3.6.1 活文档（当前有效配置，直接替换，5 个文件）

| # | 文件 | 涉及行数 | 修改方式 |
|---|---|---:|---|
| 1 | docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml | 6 | 表格中 6 个 `- id: D-XXX-YYY` → `D-XXX_YYY`（或 D-AUDITTEST） |
| 2 | docs/02_enterprise_architecture/target_architecture/capability_heatmap.md | 10 | 表格中域名引用 |
| 3 | docs/02_enterprise_architecture/target_architecture/index.md | 9 | 表格中域名引用 |
| 4 | docs/02_enterprise_architecture/target_architecture/overview.md | 2 | 域列表字符串（逗号分隔） |
| 5 | docs/02_enterprise_architecture/target_architecture/application_architecture.md | 1 | 域列表字符串 |

#### 3.6.2 工作文件（直接替换，1 个文件）

| # | 文件 | 涉及行数 | 说明 |
|---|---|---:|---|
| 6 | scripts/_t17_domain_suggestions.csv | ~15 | CSV 中域名列值，每行 `filename,D-XXX-YYY` → `filename,D-XXX_YYY` |

#### 3.6.3 历史记录文档（追加裁定说明，保留旧名上下文，7 个文件）

| # | 文件 | 涉及行数 | 处理方式 |
|---|---|---:|---|
| 7 | docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md | ~25 | 追加 #ARCH-REN-001 裁定说明，在域名不统一议题处标注"已由#ARCH-REN-001修正" |
| 8 | docs/02_enterprise_architecture/dependency_architecture_panorama.md | ~10 | 追加裁定说明 |
| 9 | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | ~3 | 追加说明 |
| 10 | docs/02_enterprise_architecture/_archive/phase4b_cleanup_construction_plan.md | ~3 | 追加说明（归档的 phase4b 清理方案，L101 引用 3 个旧域名） |
| 11 | docs/_working/domain_split_plan_4_oversized_domains.md | ~70 | 追加说明（原拆分方案引用大量旧域名，不逐一替换，仅顶部追加裁定说明） |
| 12 | docs/decomposition/tasks/DM-100254.md | ~2 | 追加说明 |
| 13 | data/archive/taskcards/DM-100257.md | ~1 | 归档任务卡，追加说明 |

#### 3.6.4 生成制品（DB 改名后重新生成，不手动改）

| 文件/目录 | 生成器 | 确认方式 |
|---|---|---|
| data/asset_index/target_path_tree.yaml | generate_target_path_tree.py | 头部 `auto_generated_by` |
| data/asset_index/project_entity_depgraph.yaml | generate_project_depgraph.py | 生成器输出 |
| docs/02_enterprise_architecture/02_domain_architecture_docs/domain_index.md | generate_domain_index.py | 头部"由 generate_domain_index.py 自动生成" |
| docs/02_enterprise_architecture/02_domain_architecture_docs/01-43_*.md | generate_domain_doc.py | 头部"由 generate_domain_doc.py 自动生成" |
| docs/02_enterprise_architecture/02_domain_architecture_docs/*_architecture.md | generate_domain_architecture_diagram.py | 头部"由 generate_domain_architecture_diagram.py 自动生成" |
| docs/02_enterprise_architecture/generated/domains/*.mmd | dm200913_rewrite_diagrams.py | 头部"由 dm200913 自动生成" |
| docs/02_enterprise_architecture/01_global_architecture_diagram/cross_domain_matrix.md | generate_cross_domain_matrix.py | 头部确认 |
| docs/02_enterprise_architecture/01_global_architecture_diagram/runtime_plane_mapping.md | generate_runtime_plane_mapping.py | 头部确认 |
| docs/02_enterprise_architecture/01_global_architecture_diagram/integration_topology.md | dm200912_rewrite_views.py | 头部确认 |
| docs/02_enterprise_architecture/01_global_architecture_diagram/capability_heatmap.md | generate_capability_heatmap.py | 头部确认 |
| docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_en.md | generate_path_tree.py | 头部"Auto-generated by generate_path_tree.py" |
| docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_zh.md | generate_path_tree.py | 头部"Auto-generated by generate_path_tree.py" |
| docs/02_enterprise_architecture/03_governance_reports/design_vs_production.md | generate_design_vs_production.py | 头部确认 |
| docs/02_enterprise_architecture/03_governance_reports/constraint_violations.md | generate_constraint_violations.py | 头部确认 |
| docs/02_enterprise_architecture/03_governance_reports/capacity_report.md | generate_capacity_report.py | 头部确认 |

---

## 第四部分：执行步骤（施工细节级）

### 4.1 阶段 0：备份

**动作 0.1：Git 备份当前 depgraph.db**

```bash
python scripts/git_commit.py --session rename-hyphen-backup \
  --files data/databases/depgraph.db \
  --message "backup: pre-rename-hyphen depgraph.db snapshot [GW:rename-hyphen]"
```

**验证**：`git log --oneline -1` 确认 commit 存在，记录此 commit hash 为 `<BACKUP>`（回滚时使用）。

**回滚锚点**：若后续步骤出错，参见第五部分回滚方案。提交前回滚用 `git checkout data/databases/depgraph.db`；提交后回滚用 `git reset --hard <BACKUP>`。

### 4.2 阶段 1：DB 域 ID 改名（6 域，按字母序）

对每个域执行：先 `--dry-run` 预览，确认无误后执行实际改名。

**动作 1.1：D-GOV-DOCS → D-GOV_DOCS**

```bash
# 步骤 A：dry-run 预览
python scripts/governance/apply_depgraph.py --rename-domain D-GOV-DOCS D-GOV_DOCS --dry-run

# 预期输出（stderr）：
#   [DRY RUN] step 1 domains.domain_id='D-GOV-DOCS': 1 rows
#   [DRY RUN] step 2 nodes.domain_id='D-GOV-DOCS': 127 rows
#   [DRY RUN] step 3 nodes.subdomain_id='D-GOV-DOCS': 127 rows
#   [DRY RUN] step 4 nodes.belongs_to='D-GOV-DOCS': 127 rows
#   [DRY RUN] 兜底 nodes.owner REPLACE 'D-GOV-DOCS'->'D-GOV_DOCS': 127 rows
#   [DRY RUN] 兜底 arch_directory_tree.domain_id REPLACE ...: 245 rows
#   [DRY RUN] step 14 arch_path_mappings.domain_id='D-GOV-DOCS': 2 rows
#   [DRY RUN] cmd_rename_domain(D-GOV-DOCS -> D-GOV_DOCS): total 756 rows

# 步骤 B：执行改名
python scripts/governance/apply_depgraph.py --rename-domain D-GOV-DOCS D-GOV_DOCS

# 步骤 C：验证 0 残留
python -c "import sqlite3;c=sqlite3.connect('data/databases/depgraph.db');print(c.execute(\"SELECT COUNT(*) FROM domains WHERE domain_id LIKE '%D-GOV-DOCS%'\").fetchone()[0])"
# 预期输出：0
```

**动作 1.2：D-GOV-ENFORCEMENT → D-GOV_ENFORCEMENT**

```bash
python scripts/governance/apply_depgraph.py --rename-domain D-GOV-ENFORCEMENT D-GOV_ENFORCEMENT --dry-run
# 预期：total 436 rows
python scripts/governance/apply_depgraph.py --rename-domain D-GOV-ENFORCEMENT D-GOV_ENFORCEMENT
# 验证：SELECT COUNT(*) FROM domains WHERE domain_id LIKE '%D-GOV-ENFORCEMENT%' → 0
```

**动作 1.3：D-GOV-SCRIPTS → D-GOV_SCRIPTS**

```bash
# 注意：此域含前缀匹配（D-GOV-SCRIPTS-META 在 belongs_to 中），B1 兜底会处理
python scripts/governance/apply_depgraph.py --rename-domain D-GOV-SCRIPTS D-GOV_SCRIPTS --dry-run
# 预期：total 2517 rows（含 D-GOV-SCRIPTS-META → D-GOV_SCRIPTS-META 的 REPLACE）
python scripts/governance/apply_depgraph.py --rename-domain D-GOV-SCRIPTS D-GOV_SCRIPTS
# 验证：SELECT COUNT(*) FROM domains WHERE domain_id LIKE '%D-GOV-SCRIPTS%' → 0
```

**动作 1.4：D-GOV_AUDIT_TESTS → D-AUDITTEST**

```bash
python scripts/governance/apply_depgraph.py --rename-domain D-GOV_AUDIT_TESTS D-AUDITTEST --dry-run
# 预期：total 156 rows
python scripts/governance/apply_depgraph.py --rename-domain D-GOV_AUDIT_TESTS D-AUDITTEST
# 验证：SELECT COUNT(*) FROM domains WHERE domain_id LIKE '%D-GOV_AUDIT_TESTS%' → 0
# 注意：D-GOV_AUDIT 域不受影响（D-GOV_AUDIT_TESTS 不是 D-GOV_AUDIT 的子串前缀）
```

**动作 1.5：D-INTEGRATION-GATEWAY → D-INTEGRATION_GATEWAY**

```bash
python scripts/governance/apply_depgraph.py --rename-domain D-INTEGRATION-GATEWAY D-INTEGRATION_GATEWAY --dry-run
# 预期：total 252 rows
python scripts/governance/apply_depgraph.py --rename-domain D-INTEGRATION-GATEWAY D-INTEGRATION_GATEWAY
# 验证：SELECT COUNT(*) FROM domains WHERE domain_id LIKE '%D-INTEGRATION-GATEWAY%' → 0
```

**动作 1.6：D-SECURITY-LLM → D-SECURITY_LLM**

```bash
python scripts/governance/apply_depgraph.py --rename-domain D-SECURITY-LLM D-SECURITY_LLM --dry-run
# 预期：total 206 rows
python scripts/governance/apply_depgraph.py --rename-domain D-SECURITY-LLM D-SECURITY_LLM
# 验证：SELECT COUNT(*) FROM domains WHERE domain_id LIKE '%D-SECURITY-LLM%' → 0
```

**动作 1.7：全量残留扫描**

```bash
# 扫描 DB 所有表所有 TEXT 列，确认 6 个旧域 ID 零残留
python -c "
import sqlite3
c = sqlite3.connect('data/databases/depgraph.db')
old_ids = ['D-GOV-DOCS','D-GOV-ENFORCEMENT','D-GOV-SCRIPTS','D-GOV_AUDIT_TESTS','D-INTEGRATION-GATEWAY','D-SECURITY-LLM']
tables = [r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('domain_naming_rules','_schema_version','governance_audit_logs')\").fetchall()]
total = 0
for tbl in tables:
    cols = [col[1] for col in c.execute(f'PRAGMA table_info({tbl})').fetchall()]
    for col in cols:
        for oid in old_ids:
            cnt = c.execute(f'SELECT COUNT(*) FROM {tbl} WHERE CAST({col} AS TEXT) LIKE ?', (f'%{oid}%',)).fetchone()[0]
            if cnt > 0:
                print(f'  RESIDUAL: {tbl}.{col} contains {oid}: {cnt} rows')
                total += cnt
print(f'Total residual (excl. 3 excluded tables): {total}')
"
# 预期输出：Total residual: 0
```

**动作 1.8：Git 提交 DB 改名**

```bash
python scripts/git_commit.py --session rename-hyphen-db \
  --files data/databases/depgraph.db \
  --message "rename: 6 domain IDs hyphen→underscore (4323 rows updated) [GW:rename-hyphen]"
```

### 4.3 阶段 2：YAML registry 修改

**动作 2.1：修改 functional_domain_registry.yaml（7 行）**

逐行替换（用 Edit 工具精确替换，避免误伤）：

| 行号 | old_string | new_string |
|---|---|---|
| L27 | `- domain: D-GOV-ENFORCEMENT` | `- domain: D-GOV_ENFORCEMENT` |
| L54 | `- domain: D-GOV-SCRIPTS` | `- domain: D-GOV_SCRIPTS` |
| L212 | `- domain: D-SECURITY-LLM` | `- domain: D-SECURITY_LLM` |
| L757 | `- domain: D-INTEGRATION-GATEWAY` | `- domain: D-INTEGRATION_GATEWAY` |
| L811 | `- domain: D-GOV-SCRIPTS` | `- domain: D-GOV_SCRIPTS` |
| L903 | `- domain: D-GOV_AUDIT_TESTS` | `- domain: D-AUDITTEST` |
| L921 | `- domain: D-GOV-DOCS` | `- domain: D-GOV_DOCS` |

**注意**：L54 和 L811 都是 `- domain: D-GOV-SCRIPTS`，需用 replace_all=true 或带上下文精确替换。

**动作 2.2：同步 YAML 到 DB**

```bash
python scripts/governance/sync_yaml_to_depgraph.py
# 预期：YAML 与 DB 一致，无 diff 输出
```

### 4.4 阶段 3：生成器脚本修改

**动作 3.1：修改 sync_yaml_to_depgraph.py（1 处）**

文件：`scripts/governance/sync_yaml_to_depgraph.py`
行号：L706

```
原：VALUES (?, ?, 'file', 'D-GOV-DOCS', ?, 'design')
新：VALUES (?, ?, 'file', 'D-GOV_DOCS', ?, 'design')
```

**动作 3.2：修改 dm200912_rewrite_views.py（2 处）**

文件：`scripts/governance/d5_architecture/dm200912_rewrite_views.py`

| 行号 | 替换内容 |
|---|---|
| L829 | `D-SECURITY-LLM` → `D-SECURITY_LLM`（在域列表字符串中） |
| L832 | `D-INTEGRATION-GATEWAY` → `D-INTEGRATION_GATEWAY`（在域列表字符串中） |

**动作 3.3：修改 generate_capability_heatmap.py（2 处）**

文件：`scripts/governance/d5_architecture/generators/generate_capability_heatmap.py`

| 行号 | 替换内容 |
|---|---|
| L116 | `D-SECURITY-LLM` → `D-SECURITY_LLM`（在 Python list 中） |
| L127 | `D-INTEGRATION-GATEWAY` → `D-INTEGRATION_GATEWAY`（在 Python list 中） |

### 4.5 阶段 4：活文档修改（5 个文件）

**动作 4.1：修改 target_architecture/architecture_model/index.yaml（6 处）**

| 行号 | 替换 |
|---|---|
| L119 | `D-GOV-DOCS` → `D-GOV_DOCS` |
| L122 | `D-GOV-ENFORCEMENT` → `D-GOV_ENFORCEMENT` |
| L128 | `D-GOV-SCRIPTS` → `D-GOV_SCRIPTS` |
| L137 | `D-GOV_AUDIT_TESTS` → `D-AUDITTEST` |
| L164 | `D-INTEGRATION-GATEWAY` → `D-INTEGRATION_GATEWAY` |
| L203 | `D-SECURITY-LLM` → `D-SECURITY_LLM` |

**动作 4.2：修改 target_architecture/capability_heatmap.md（10 处）**

逐行替换所有旧域名引用为新域名。涉及行：L116, L117, L128, L130, L132, L134, L162, L163, L164, L167。

**动作 4.3：修改 target_architecture/index.md（9 处）**

逐行替换。涉及行：L99, L100, L101, L104, L121, L129, L131, L133, L135。

**动作 4.4：修改 target_architecture/overview.md（2 处）**

| 行号 | 替换内容 |
|---|---|
| L84 | 域列表字符串中 6 个旧域名 → 新域名 |
| L85 | 域列表字符串中 6 个旧域名 → 新域名 |

**动作 4.5：修改 target_architecture/application_architecture.md（1 处）**

| 行号 | 替换内容 |
|---|---|
| L119 | 域列表字符串中 6 个旧域名 → 新域名 |

### 4.6 阶段 5：工作文件修改（1 个文件）

**动作 5.1：修改 scripts/_t17_domain_suggestions.csv**

全局替换 CSV 中的 6 个旧域名 → 新域名。此文件为工作 CSV，每行格式为 `filename,D-XXX-YYY`，直接文本替换即可。

### 4.7 阶段 6：历史文档追加说明（7 个文件）

**处理原则**：历史文档不逐一替换旧域名（保留历史可追溯性），仅在文档顶部或相关议题处追加裁定说明。

**追加文本模板**（各文档适配）：

```markdown
> **裁定 #ARCH-REN-001（2026-06-26）**：6 个域 ID 连字符→下划线改名：
> D-GOV-DOCS→D-GOV_DOCS, D-GOV-ENFORCEMENT→D-GOV_ENFORCEMENT, D-GOV-SCRIPTS→D-GOV_SCRIPTS,
> D-GOV_AUDIT_TESTS→D-AUDITTEST, D-INTEGRATION-GATEWAY→D-INTEGRATION_GATEWAY, D-SECURITY-LLM→D-SECURITY_LLM。
> 本文档中出现的旧域名均为历史记录，已由上述裁定更新。
```

**GATE-15 ttl frontmatter 前置检查**（关键，否则 commit 被阻断）：

`check_frontmatter_metadata.py`（GATE-15 硬阻断）的精确行为：**仅有 frontmatter 但缺 `ttl:` 字段的 .md 文件会被阻断；无 frontmatter 的 .md 文件被跳过（不阻断）**。逐文件核查结果：

| # | 文件 | frontmatter 状态 | ttl 字段 | GATE-15 影响 |
|---|---|---|---|---|
| 1 | preexisting_db_issues_investigation_report.md | 有 | `permanent` ✓ | 通过 |
| 2 | dependency_architecture_panorama.md | 有 | `permanent` ✓ | 通过 |
| 3 | architecture_diagram_construction_plan.md | 有（module_id/doc_type/status 等）| **缺失** ✗ | **阻断** |
| 4 | _archive/phase4b_cleanup_construction_plan.md | 有 | `permanent` ✓ | 通过 |
| 5 | _working/domain_split_plan_4_oversized_domains.md | 有 | `task_bound` ✓ | 通过 |
| 6 | docs/decomposition/tasks/DM-100254.md | **无 frontmatter** | — | 跳过（不阻断） |
| 7 | data/archive/taskcards/DM-100257.md | **无 frontmatter** | — | 跳过（不阻断） |

**结论**：仅 #3（architecture_diagram_construction_plan.md）需要在追加裁定说明前先补 `ttl:` 字段，否则动作 9.1 的 commit 会被 GATE-15 阻断。

**动作 6.1~6.7**：对以下 7 个文件，在 frontmatter 后（无 frontmatter 则在标题后）插入上述追加文本模板：

| 动作 | 文件（完整路径） | 追加位置 | 前置 ttl 处理 |
|---|---|---|---|
| 6.1 | docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md | 文档顶部 frontmatter 后 | 无需（ttl=permanent） |
| 6.2 | docs/02_enterprise_architecture/dependency_architecture_panorama.md | 文档顶部 | 无需（ttl=permanent） |
| 6.3 | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | 文档顶部 frontmatter 后 | **先补 `ttl: task_bound` 到 frontmatter**（见动作 6.3a） |
| 6.4 | docs/02_enterprise_architecture/_archive/phase4b_cleanup_construction_plan.md | frontmatter 后 | 无需（ttl=permanent） |
| 6.5 | docs/_working/domain_split_plan_4_oversized_domains.md | 文档顶部 | 无需（ttl=task_bound） |
| 6.6 | docs/decomposition/tasks/DM-100254.md | 文档顶部（无 frontmatter） | 无需（无 frontmatter 跳过） |
| 6.7 | data/archive/taskcards/DM-100257.md | 文档顶部（无 frontmatter） | 无需（无 frontmatter 跳过） |

**动作 6.3a（前置 ttl 补全，仅 architecture_diagram_construction_plan.md）**：

在文件现有 frontmatter 的最后一行 `---` 之前，插入一行 `ttl: task_bound`。原 frontmatter（节选）：

```yaml
---
module_id: GOV-036-ARCH-DIAGRAM-PLAN
doc_type: architecture_construction_plan
status: Draft
version: 0.1.0
created: '2026-06-22'
last_updated: '2026-06-22'
owner: human
purpose: ...
...
depends_on:
  - target: GOV-036-ARCH-DISCUSSION
    at: §2.1 43域裁定
    why: ...
  - target: 依赖与架构全景图能力定位书
---
```

修改后：

```yaml
---
module_id: GOV-036-ARCH-DIAGRAM-PLAN
doc_type: architecture_construction_plan
status: Draft
version: 0.1.0
created: '2026-06-22'
last_updated: '2026-06-22'
owner: human
purpose: ...
...
depends_on:
  - target: GOV-036-ARCH-DISCUSSION
    at: §2.1 43域裁定
    why: ...
  - target: 依赖与架构全景图能力定位书
ttl: task_bound          # ← 新增此行（status=Draft 的施工方案，绑定时序任务）
---
```

**为何选 `task_bound` 而非 `permanent`**：该文档 `status: Draft` 且为施工方案（task-bound），符合 `ttl_vocabulary.yaml` 中 task_bound 的语义"绑定具体任务时序"；同类已归档的 phase4b_cleanup_construction_plan.md 用 `permanent` 是因其 `status: Active` 且已归档为永久参考。

**动作 6.3b**：在 frontmatter 后（紧接 `---` 之后）插入追加文本模板（同其他历史文档）。

### 4.8 阶段 7：重新生成制品

> ⚠️ **已废弃（2026-06-26 派生产物删除裁定）**：本阶段"重新生成 target_path_tree.yaml / project_entity_depgraph.yaml"已失效——`generate_target_path_tree.py` 脚本与 7 个派生 YAML 产物均已删除。depgraph.db 是唯一查询入口，禁止重新创建派生 YAML 副本。域名变更后改为直接查 depgraph.db（见 AGENTS.md §11 决策树）。

**动作 7.1：重新生成 target_path_tree.yaml**

```bash
python scripts/governance/generate_target_path_tree.py
```

**动作 7.2：重新生成 project_entity_depgraph.yaml**

```bash
python scripts/governance/generate_project_depgraph.py
```

**动作 7.3：重新生成域架构文档**

```bash
# 生成 domain_index.md
python scripts/governance/d5_architecture/generators/generate_domain_index.py

# 生成各域文档（6 个改名域）
python scripts/governance/d5_architecture/generators/generate_domain_doc.py --domain D-GOV_DOCS
python scripts/governance/d5_architecture/generators/generate_domain_doc.py --domain D-GOV_ENFORCEMENT
python scripts/governance/d5_architecture/generators/generate_domain_doc.py --domain D-GOV_SCRIPTS
python scripts/governance/d5_architecture/generators/generate_domain_doc.py --domain D-AUDITTEST
python scripts/governance/d5_architecture/generators/generate_domain_doc.py --domain D-INTEGRATION_GATEWAY
python scripts/governance/d5_architecture/generators/generate_domain_doc.py --domain D-SECURITY_LLM
```

**动作 7.4：重新生成全局架构图**

```bash
python scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py
python scripts/governance/d5_architecture/generators/generate_runtime_plane_mapping.py
python scripts/governance/d5_architecture/generators/generate_capability_heatmap.py
python scripts/governance/d5_architecture/dm200912_rewrite_views.py
python scripts/governance/d5_architecture/dm200913_rewrite_diagrams.py
python scripts/governance/d5_architecture/generators/generate_path_tree.py
```

**动作 7.5：重新生成治理报告**

```bash
python scripts/governance/d5_architecture/generators/generate_design_vs_production.py
python scripts/governance/d5_architecture/generators/generate_constraint_violations.py
python scripts/governance/d5_architecture/generators/generate_capacity_report.py
```

### 4.9 阶段 8：循环验收（2 轮零错误）

**动作 8.1：post_sync_standard 第 1 轮**

```bash
python scripts/governance/diagnose_depgraph.py
```

**判定**：
- 若输出 0 error → 进入第 2 轮
- 若输出 N error → 修复后重新执行第 1 轮

**动作 8.2：post_sync_standard 第 2 轮**

```bash
python scripts/governance/diagnose_depgraph.py
```

**判定**：
- 连续 2 轮 0 error → 验收通过
- 否则 → 继续修复 + 重新执行 2 轮

**动作 8.3：文件残留扫描**

```bash
# 扫描所有手动修改的文件，确认旧域名零残留
python -c "
import os, re
old_ids = ['D-GOV-DOCS','D-GOV-ENFORCEMENT','D-GOV-SCRIPTS','D-GOV_AUDIT_TESTS','D-INTEGRATION-GATEWAY','D-SECURITY-LLM']
pat = re.compile('|'.join(r'(?<![A-Z])' + re.escape(d) for d in old_ids))
# 仅扫描活文档、脚本和工作文件（排除历史文档——保留旧名+追加说明；排除生成制品——重新生成）
check_files = [
    'docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml',
    'docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml',
    'docs/02_enterprise_architecture/target_architecture/capability_heatmap.md',
    'docs/02_enterprise_architecture/target_architecture/index.md',
    'docs/02_enterprise_architecture/target_architecture/overview.md',
    'docs/02_enterprise_architecture/target_architecture/application_architecture.md',
    'scripts/governance/sync_yaml_to_depgraph.py',
    'scripts/governance/d5_architecture/dm200912_rewrite_views.py',
    'scripts/governance/d5_architecture/generators/generate_capability_heatmap.py',
    'scripts/_t17_domain_suggestions.csv',
]
total = 0
for f in check_files:
    if not os.path.exists(f):
        continue
    content = open(f, encoding='utf-8', errors='ignore').read()
    for m in pat.finditer(content):
        start = m.start()
        if start > 0 and content[start-1].isupper():
            continue  # MOD-XXX false match, skip
        if '[BLUEPRINT]' in content[max(0,start-50):start+50]:
            continue  # module ID header, skip
        print(f'  RESIDUAL: {f}:{content.count(chr(10),0,start)+1}: {m.group()}')
        total += 1
print(f'Total file residual: {total}')
"
# 预期输出：Total file residual: 0
```

**动作 8.4：GATE-15 ttl 前置校验（commit 前置门禁）**

在动作 9.1 commit 之前，必须确认所有待提交的 .md 文件通过 GATE-15（否则 commit 会被 pre-commit 钩子阻断）。对 7 个历史 .md 文件做增量校验：

```bash
python scripts/governance/d3_metadata/check_frontmatter_metadata.py \
  docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md \
  docs/02_enterprise_architecture/dependency_architecture_panorama.md \
  docs/02_enterprise_architecture/architecture_diagram_construction_plan.md \
  docs/02_enterprise_architecture/_archive/phase4b_cleanup_construction_plan.md \
  docs/_working/domain_split_plan_4_oversized_domains.md \
  docs/decomposition/tasks/DM-100254.md \
  data/archive/taskcards/DM-100257.md
```

**预期输出**：`OK: no .md files to check`（无 frontmatter 的文件被跳过）或无任何 `missing required field 'ttl'` / `invalid ttl` 行。退出码 0。

**判定**：
- 退出码 0 → 进入动作 9.1 commit
- 退出码 1（EXIT_FINDINGS）→ 有 .md 文件缺 ttl 或 ttl 非法 → 回到动作 6.3a 补 ttl 后重跑动作 8.4
- 退出码 2（EXIT_ERROR）→ 脚本异常 → 检查 `ttl_vocabulary.yaml` 是否可读

**为何此步必要**：动作 9.1 会一次性提交 17 个文件（含 7 个 .md 历史文档），GATE-15 pre-commit 钩子在 commit 时触发，任何 .md 文件缺 ttl 会导致整个 commit 失败（pre-commit 钩子整体回滚）。动作 8.4 提前在 commit 前增量校验，避免 commit 失败后的部分回滚混乱。

### 4.10 阶段 9：Git 提交所有文件变更

**动作 9.1：提交所有修改文件（17 个）**

`--files` 参数为逗号分隔的单字符串（见 `git_commit.py` 的 `_parse_files`），不可用空格分隔。路径基于 cwd（项目根目录）解析：

```bash
python scripts/git_commit.py --session rename-hyphen-files \
  --files "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml,scripts/governance/sync_yaml_to_depgraph.py,scripts/governance/d5_architecture/dm200912_rewrite_views.py,scripts/governance/d5_architecture/generators/generate_capability_heatmap.py,docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml,docs/02_enterprise_architecture/target_architecture/capability_heatmap.md,docs/02_enterprise_architecture/target_architecture/index.md,docs/02_enterprise_architecture/target_architecture/overview.md,docs/02_enterprise_architecture/target_architecture/application_architecture.md,scripts/_t17_domain_suggestions.csv,docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md,docs/02_enterprise_architecture/dependency_architecture_panorama.md,docs/02_enterprise_architecture/architecture_diagram_construction_plan.md,docs/02_enterprise_architecture/_archive/phase4b_cleanup_construction_plan.md,docs/_working/domain_split_plan_4_oversized_domains.md,docs/decomposition/tasks/DM-100254.md,data/archive/taskcards/DM-100257.md" \
  --message "rename: 6 domain IDs hyphen→underscore - file sync (17 files) [GW:rename-hyphen]"
```

**动作 9.2：提交重新生成的制品**

`--files` 同样为逗号分隔。目录条目（以 `/` 结尾）作为 pathspec 传入，`git add` 会递归添加目录下所有变更文件。注意：`git_commit.py` 的 `os.path.isfile()` 对目录返回 False，会触发 `git ls-files --error-unmatch` 二次校验——已跟踪目录会通过校验（日志可能误报"已跟踪但工作区已删除"，属正常行为，不阻断提交）。

```bash
python scripts/git_commit.py --session rename-hyphen-regen \
  --files "data/asset_index/target_path_tree.yaml,data/asset_index/project_entity_depgraph.yaml,docs/02_enterprise_architecture/02_domain_architecture_docs/,docs/02_enterprise_architecture/generated/,docs/02_enterprise_architecture/01_global_architecture_diagram/,docs/02_enterprise_architecture/03_governance_reports/design_vs_production.md,docs/02_enterprise_architecture/03_governance_reports/constraint_violations.md,docs/02_enterprise_architecture/03_governance_reports/capacity_report.md" \
  --message "rename: regenerate artifacts after 6 domain ID rename [GW:rename-hyphen]"
```

---

## 第五部分：回滚方案

> **关键前提**：回滚前必须先确认阶段 0 备份 commit 的 hash。执行 `git log --oneline -5` 找到动作 0.1 的 backup commit（message 含 `backup: pre-rename-hyphen`），记为 `<BACKUP>`。

### 5.1 场景 A：提交前回滚（DB 改名尚未 commit）

适用：阶段 1 执行中或 dry-run 后发现问题，DB 改名仅在工作区未提交。

```bash
# DB：丢弃工作区修改，恢复到 HEAD（= 阶段 0 备份点）
git checkout data/databases/depgraph.db
```

### 5.2 场景 B：提交后回滚（已有 commit）

适用：DB 改名已 commit（动作 1.8）或后续阶段已 commit，需要整体回退到备份点。

```bash
# 整体硬回退到备份点（DB + 文件 + 生成制品全部恢复）
# 警告：此操作丢弃 <BACKUP> 之后的所有 commit，仅限回滚场景使用
git reset --hard <BACKUP>
```

若仅回退 DB 不回退文件（部分回滚），用 checkout 指定 commit：

```bash
# 仅恢复 DB 到备份点
git checkout <BACKUP> -- data/databases/depgraph.db
```

### 5.3 文件回滚（场景 A：工作区未提交）

```bash
# 恢复所有修改文件到 HEAD（= 备份点）
git checkout -- \
    docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml \
    scripts/governance/sync_yaml_to_depgraph.py \
    scripts/governance/d5_architecture/dm200912_rewrite_views.py \
    scripts/governance/d5_architecture/generators/generate_capability_heatmap.py \
    docs/02_enterprise_architecture/target_architecture/ \
    scripts/_t17_domain_suggestions.csv \
    docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md \
    docs/02_enterprise_architecture/dependency_architecture_panorama.md \
    docs/02_enterprise_architecture/architecture_diagram_construction_plan.md \
    docs/02_enterprise_architecture/_archive/phase4b_cleanup_construction_plan.md \
    docs/_working/domain_split_plan_4_oversized_domains.md \
    docs/decomposition/tasks/DM-100254.md \
    data/archive/taskcards/DM-100257.md
```

### 5.4 生成制品回滚（场景 A：工作区未提交）

```bash
git checkout -- data/asset_index/target_path_tree.yaml data/asset_index/project_entity_depgraph.yaml
git checkout -- docs/02_enterprise_architecture/02_domain_architecture_docs/ docs/02_enterprise_architecture/generated/
git checkout -- docs/02_enterprise_architecture/01_global_architecture_diagram/ docs/02_enterprise_architecture/03_governance_reports/
```

> **注意**：5.4 中 `git checkout -- docs/02_enterprise_architecture/03_governance_reports/` 会同时恢复历史文档（5.3 已含）和生成报告。为避免混淆，场景 A 下优先执行 5.4 目录级恢复，再执行 5.3 补充恢复 5.4 未覆盖的目录外文件（functional_domain_registry.yaml、scripts/、docs/_working/、docs/decomposition/、data/archive/）。

---

## 第六部分：验收标准

| # | 验收项 | 验证命令 | 预期结果 |
|---|---|---|---|
| C1 | 6 旧域 ID 在 DB 零残留 | `SELECT COUNT(*) FROM domains WHERE domain_id IN ('D-GOV-DOCS','D-GOV-ENFORCEMENT','D-GOV-SCRIPTS','D-GOV_AUDIT_TESTS','D-INTEGRATION-GATEWAY','D-SECURITY-LLM')` | 0 |
| C2 | 6 新域 ID 在 DB 存在 | `SELECT COUNT(*) FROM domains WHERE domain_id IN ('D-GOV_DOCS','D-GOV_ENFORCEMENT','D-GOV_SCRIPTS','D-AUDITTEST','D-INTEGRATION_GATEWAY','D-SECURITY_LLM')` | 6 |
| C3 | DB 全表残留扫描 | 阶段 1.7 脚本 | Total residual: 0 |
| C4 | post_sync_standard 连续 2 轮零错误 | `python scripts/governance/diagnose_depgraph.py` ×2 | 2 轮均 0 error |
| C5 | 活文档+脚本文件残留扫描 | 阶段 8.3 脚本 | Total file residual: 0 |
| C6 | YAML registry 与 DB 一致 | `python scripts/governance/sync_yaml_to_depgraph.py` | 无 diff |
| C7 | 生成制品已重新生成 | 检查文件 mtime | 晚于 DB 改名时间 |
| C8 | Git 提交完整 | `git log --oneline -5` | 4 个 commit 存在（backup + db + files + regen） |

---

## 第七部分：风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|---|---|---|---|
| B1 兜底 REPLACE 误伤其他列值 | 低 | 中 | dry-run 预览确认受影响行数后再执行；B1 排除 blueprint_id/path 列 |
| D-GOV-SCRIPTS-META 前缀匹配被错误替换 | 低 | 低 | B1 REPLACE 将 D-GOV-SCRIPTS-META → D-GOV_SCRIPTS-META，语义正确（仅连字符→下划线） |
| 生成器脚本修改后语法错误 | 低 | 中 | 修改后逐个运行生成器验证 |
| 生成制品重新生成失败 | 中 | 低 | 可从 DB 重新生成，不丢失数据 |
| 历史文档追加说明位置不当 | 低 | 低 | 追加在 frontmatter 后、正文前，不影响原有内容 |

---

## 附录 A：手动修改文件清单（17 个文件）

> 生成制品（target_path_tree.yaml、project_entity_depgraph.yaml、domain docs、全局架构图、治理报告等）不在此表，详见第 3.6.4 节，DB 改名后由生成器重新生成。

| # | 文件路径 | 类别 | 处理方式 |
|---|---|---|---|
| 1 | docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml | 活文档 | 直接替换 7 行 |
| 2 | docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml | 活文档 | 直接替换 6 行 |
| 3 | docs/02_enterprise_architecture/target_architecture/capability_heatmap.md | 活文档 | 直接替换 10 行 |
| 4 | docs/02_enterprise_architecture/target_architecture/index.md | 活文档 | 直接替换 9 行 |
| 5 | docs/02_enterprise_architecture/target_architecture/overview.md | 活文档 | 直接替换 2 行 |
| 6 | docs/02_enterprise_architecture/target_architecture/application_architecture.md | 活文档 | 直接替换 1 行 |
| 7 | scripts/governance/sync_yaml_to_depgraph.py | 脚本 | 直接替换 1 行 |
| 8 | scripts/governance/d5_architecture/dm200912_rewrite_views.py | 脚本 | 直接替换 2 行 |
| 9 | scripts/governance/d5_architecture/generators/generate_capability_heatmap.py | 脚本 | 直接替换 2 行 |
| 10 | scripts/_t17_domain_suggestions.csv | 工作文件 | 直接替换 ~15 行 |
| 11 | docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md | 历史文档 | 追加说明 |
| 12 | docs/02_enterprise_architecture/dependency_architecture_panorama.md | 历史文档 | 追加说明 |
| 13 | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | 历史文档 | 追加说明 |
| 14 | docs/02_enterprise_architecture/_archive/phase4b_cleanup_construction_plan.md | 历史文档 | 追加说明 |
| 15 | docs/_working/domain_split_plan_4_oversized_domains.md | 历史文档 | 追加说明 |
| 16 | docs/decomposition/tasks/DM-100254.md | 历史文档 | 追加说明 |
| 17 | data/archive/taskcards/DM-100257.md | 归档 | 追加说明 |

**另**：`data/asset_index/project_entity_depgraph.yaml`（13.8MB）+ `data/asset_index/target_path_tree.yaml` + 所有 domain docs + 全局架构图 + 治理报告均为生成制品，DB 改名后重新生成（见第 3.6.4 节）。

## 附录 B：MOD-XXX 子串误匹配排除说明

扫描修正记录：初版扫描用 `(?<!MOD-)` 4 字符 lookbehind 排除 MOD-XXX 模块 ID 中的 D-XXX 子串。但发现盲区：`MOD-LLM_SECURITY` 中 `D-SECURITY-LLM` 起始于位置 2（前仅 2 字符 "MO"），4 字符 lookbehind 因字符不足而静默失败，导致误匹配。

**修正**：改用 `(?<![A-Z])` 1 字符 lookbehind——真域引用前必为非大写字母（空格/引号/逗号/行首），而 MOD-XXX 中 D 前为 'O'（大写）→ 正确排除。

**验证**：修正后 src/ 45 文件的 [BLUEPRINT] MOD-XXX 匹配全部排除，真引用从 128 文件降至 17 文件。
