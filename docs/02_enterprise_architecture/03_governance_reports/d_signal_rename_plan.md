---
ttl: permanent
---

# D-SIGNAL* 4 域改名执行方案（施工细节版 v2）

> **文档定位**：推翻裁定#ARCH-002（保留命名）和#ARCH-004（保留 D-SIGNAL 占位域原名）的详细执行方案
> **制定日期**：2026-06-25
> **版本**：v2（基于深度调研重写，修正 v1 的统计遗漏）
> **方案性质**：待用户批准后执行
> **依据**：第一性原理分析 + 命名规则 + AI 适用性（100% AI 开发项目）

---

## 第一部分：裁定概述

### 1.1 推翻的裁定

| 原裁定 | 原结论 | 推翻理由（第一性原理） |
|---|---|---|
| #ARCH-002 | 不重命名 D-SIGNAL_*（命名前缀不等于子域关系） | 命名上"看着像子域"会误导 AI 和人类，违反"所有域平级无子域"硬约束的精神；100% AI 开发项目中 AI 依赖命名语义判断归属 |
| #ARCH-004 | 保留 D-SIGNAL 原名为占位域 | D-SIGNAL 本质是"拆分后遗留的设计态规划"（45个虚拟节点，0生产代码），非3个子域的父域；保留原名持续暗示父子关系 |

### 1.2 新裁定#204：4 域改名

| 原域 ID | 新域 ID | domain_name | 性质 | 改名理由 |
|---|---|---|---|---|
| D-SIGNAL_ASHARE | **D-ASHARE_SIGNAL** | A股特色信号 | 平级业务域 | 前缀 D-ASHARE 独立，_SIGNAL 后缀保留语义 |
| D-SIGNAL_FUNDAMENTAL | **D-FUNDAMENTAL_SIGNAL** | 基本面信号 | 平级业务域 | 前缀 D-FUNDAMENTAL 独立，_SIGNAL 后缀保留语义 |
| D-SIGNAL_QUALITY | **D-SIGQC** | 信号质量控制 | 平级业务域 | "信号质量"→"信号质量控制"，QC 业界通用缩写 |
| D-SIGNAL | **D-SIGLEGACY** | 信号遗留设计态 | 设计态占位域 | SIGLEGACY=Signal Legacy，明确表达"拆分后遗留的设计态规划" |

### 1.3 改名后 4 域平级关系

```
D-ASHARE_SIGNAL      ← A股特色信号（平级业务域）
D-FUNDAMENTAL_SIGNAL ← 基本面信号（平级业务域）
D-SIGQC              ← 信号质量控制（平级业务域）
D-SIGLEGACY          ← 信号遗留设计态（平级，设计态占位，含45个虚拟规划节点）
```

4 个域命名上完全独立，无 D-SIGNAL_ 前缀暗示父子关系。

---

## 第二部分：第一性原理分析

### 2.1 D-SIGNAL 本质调研（depgraph.db 实测 2026-06-25）

| 维度 | 实测值 | 结论 |
|---|---|---|
| nodes | 45 个，全部路径如 `信号域-审计/D-SIGNAL-06` | 虚拟设计态规划节点，从"全系统模块清单.md"扫描 |
| build_status/design_maturity | 全部 planned/design | 设计态，非生产代码 |
| ssot_path | 空字符串 | 无代码目录 |
| production_nodes | 0 | 无生产代码 |
| contracts | 38 个（provider 24 + consumer 14） | 设计态契约定义 |
| invariants | 13 个 | 架构前置条件 |
| domain_events | 4 个 source + 2 个 target | 事件定义 |

### 2.2 第一性原理结论

D-SIGNAL 的本质是**信号域拆分后遗留的整体设计态规划**，不是 3 个子域的父域。45 个节点是从"全系统模块清单.md"扫描的虚拟规划，无实际代码。保留 D-SIGNAL 原名会持续暗示父子关系，违反"所有域平级无子域"硬约束的精神。

---

## 第三部分：影响范围（精确统计，v2 修正）

### 3.1 总体统计（v1 vs v2 对比）

| 类别 | v1 估算 | v2 实测 | 差异原因 |
|---|---|---|---|
| DB 行数 | ~315 | **488** | v1 遗漏 nodes.belongs_to 181行；v2第2轮审查新增 domain_mapping.domain_id 1行 |
| 代码文件 | 11 | **10** | v1 误将 alpha_signal_pipeline.py 列入（实际[DOMAIN]=D-FACTOR） |
| 生成器脚本 | 6 | 6 | 一致 |
| 手动维护文档 | ~27/~135行 | **29/~198行** | v1 严重低估；v2初次误将7个生成制品计入，审查后修正移至3.7节 |
| 生成制品 | ~3300行 | ~3300行 | 一致（重新生成） |

### 3.2 DB 修改清单（12表含domain列，11表需UPDATE+edges为boolean无需改，488行，通过 apply_depgraph.py）

| 表 | 列 | D-SIGNAL | ASHARE | FUND | QUAL | 小计 | 操作 |
|---|---|---:|---:|---:|---:|---:|---|
| domains | domain_id | 1 | 1 | 1 | 1 | 4 | UPDATE domain_id |
| nodes | domain_id | 45 | 27 | 25 | 17 | 114 | UPDATE domain_id |
| nodes | subdomain_id | 2 | 7 | 23 | 7 | 39 | UPDATE subdomain_id |
| nodes | **belongs_to** | **114** | **27** | **23** | **17** | **181** | UPDATE belongs_to（**v1遗漏！**） |
| domain_dependencies | from_domain | 6 | 6 | 6 | 6 | 24 | UPDATE from_domain |
| domain_dependencies | to_domain | 8 | 8 | 8 | 8 | 32 | UPDATE to_domain |
| domain_events | source_domain | 4 | 0 | 0 | 0 | 4 | UPDATE source_domain |
| domain_events | target_domains | 2 | 0 | 0 | 0 | 2 | UPDATE target_domains（JSON/TEXT，用REPLACE） |
| contracts | provider_domain | 24 | 0 | 0 | 0 | 24 | UPDATE provider_domain |
| contracts | consumer_domain | 14 | 0 | 0 | 0 | 14 | UPDATE consumer_domain |
| invariants | domain_id | 13 | 0 | 0 | 0 | 13 | UPDATE domain_id |
| arch_constraints | from_domain | 1 | 0 | 0 | 0 | 1 | UPDATE from_domain |
| arch_constraints | to_domain | 0 | 0 | 0 | 0 | 0 | UPDATE to_domain（0行，但UPDATE保留以防新增） |
| arch_directory_tree | domain_id | 0 | 7 | 15 | 7 | 29 | UPDATE domain_id |
| arch_path_mappings | domain_id | 1 | 1 | 2 | 1 | 5 | UPDATE domain_id |
| domain_mapping | domain_id | 0 | 0 | 1 | 0 | 1 | UPDATE domain_id（**v2第2轮审查新增！**） |
| domain_mapping | subdomain_id | 0 | 0 | 1 | 0 | 1 | UPDATE subdomain_id（**值含-FACTOR后缀，需用REPLACE**） |
| rule_bindings | domain_id | 0 | 0 | 0 | 0 | 0 | 无需改 |
| edges | cross_domain | - | - | - | - | - | boolean(0/1/NULL)，**无需改**（第12表，含domain列但不存domain ID） |
| **合计** | | **235** | **84** | **105** | **64** | **488** | |

**注意**：
- edges 表有 `cross_domain` 列（INTEGER boolean 0/1/NULL），是12张含domain相关列表中的第12张，但不存储domain ID字符串，无需UPDATE。
- domain_mapping 表 mapping_id=91 的记录有两列需更新：`domain_id='D-SIGNAL_FUNDAMENTAL'`（精确匹配可覆盖）和 `subdomain_id='D-SIGNAL_FUNDAMENTAL-FACTOR'`（带后缀，精确匹配**无法**覆盖，需用REPLACE）。
- 第2轮审查修正：v2原表遗漏 domain_mapping.domain_id 行（1行）和 arch_constraints.to_domain 行（0行），且4列小计有算术错误（D-SIGNAL 225→235、ASHARE 85→84、QUAL 73→64）。

### 3.3 代码文件修改清单（10个文件，全部在 src/zephyr/signal_fundamental/）

| # | 文件路径 | 行号 | 原内容 | 新内容 | 说明 |
|---|---|---|---|---|---|
| 1 | src/zephyr/signal_fundamental/pipeline.py | L3 | `# [DOMAIN] D-SIGNAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | **预存bug**：文件在 fundamental/ 目录下，头部误标 D-SIGNAL |
| 2 | src/zephyr/signal_fundamental/synth/signal_synthesizer.py | L3 | `# [DOMAIN] D-SIGNAL_FUNDAMENTAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | 正常改名 |
| 3 | src/zephyr/signal_fundamental/strategy/implementations/default_capital_allocator.py | L3 | `# [DOMAIN] D-SIGNAL_FUNDAMENTAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | 正常改名 |
| 4 | src/zephyr/signal_fundamental/strategy/capital_allocator.py | L3 | `# [DOMAIN] D-SIGNAL_FUNDAMENTAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | 正常改名 |
| 5 | src/zephyr/signal_fundamental/gen/implementations/default_signal_aggregator.py | L3 | `# [DOMAIN] D-SIGNAL_FUNDAMENTAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | 正常改名 |
| 6 | src/zephyr/signal_fundamental/gen/aggregator_base.py | L3 | `# [DOMAIN] D-SIGNAL_FUNDAMENTAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | 正常改名 |
| 7 | src/zephyr/signal_fundamental/combiner/synthesized_signal.py | L3 | `# [DOMAIN] D-SIGNAL_FUNDAMENTAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | 正常改名 |
| 8 | src/zephyr/signal_fundamental/capital/default_capital_allocator.py | L3 | `# [DOMAIN] D-SIGNAL_FUNDAMENTAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | 正常改名 |
| 9 | src/zephyr/signal_fundamental/capital/capital_allocator.py | L3 | `# [DOMAIN] D-SIGNAL_FUNDAMENTAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | 正常改名 |
| 10 | src/zephyr/signal_fundamental/capital/capital_allocation_result.py | L3 | `# [DOMAIN] D-SIGNAL_FUNDAMENTAL` | `# [DOMAIN] D-FUNDAMENTAL_SIGNAL` | 正常改名 |

**确认**：
- D-SIGNAL_ASHARE / D-SIGNAL_QUALITY 在 src/ 下 **0匹配**（signal_ashare/ 和 signal_quality/ 是空壳包，只有 __init__.py 占位）
- src/zephyr/factor/alpha_signal_pipeline.py 的 [DOMAIN] 是 D-FACTOR，不需改（L4 的 D-SIGNAL-06 是依赖引用，非域声明）

### 3.4 YAML registry 修改清单（1个文件，4行改+1条新增）

| 文件 | 行号 | 修改内容 |
|---|---|---|
| docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml | L11 | 注释更新：`# 裁定#201` → `# 裁定#204（推翻#ARCH-002/#ARCH-004）` |
| 同上 | L939 | `- domain: D-SIGNAL_ASHARE` → `- domain: D-ASHARE_SIGNAL` |
| 同上 | L953 | `- domain: D-SIGNAL_FUNDAMENTAL` → `- domain: D-FUNDAMENTAL_SIGNAL` |
| 同上 | L971 | `- domain: D-SIGNAL_QUALITY` → `- domain: D-SIGQC` |
| 同上 | 新增 | `- domain: D-SIGLEGACY` 条目（ssot_path 留空，covers 含"45个设计态规划节点"） |

### 3.5 生成器脚本修改清单（6个文件，~23处硬编码）

| # | 文件 | 行号 | 类型 | 原内容 | 新内容 |
|---|---|---|---|---|---|
| 1 | scripts/governance/d5_architecture/generators/domain_name_mapping.py | L44 | 字典映射 | `"D-SIGNAL": "信号",` | `"D-SIGLEGACY": "信号遗留设计态",` |
| 1 | 同上 | L45 | 字典映射 | `"D-SIGNAL_ASHARE": "A股特色信号",` | `"D-ASHARE_SIGNAL": "A股特色信号",` |
| 1 | 同上 | L46 | 字典映射 | `"D-SIGNAL_FUNDAMENTAL": "基本面信号",` | `"D-FUNDAMENTAL_SIGNAL": "基本面信号",` |
| 1 | 同上 | L47 | 字典映射 | `"D-SIGNAL_QUALITY": "信号质量",` | `"D-SIGQC": "信号质量控制",` |
| 2 | scripts/governance/d5_architecture/dm200912_rewrite_views.py | L819 | 域列表(逗号串) | `D-FACTOR, D-SIGNAL, D-SIGNAL_FUNDAMENTAL, D-SIGNAL_ASHARE, D-SIGNAL_QUALITY` | `D-FACTOR, D-SIGLEGACY, D-FUNDAMENTAL_SIGNAL, D-ASHARE_SIGNAL, D-SIGQC` |
| 3 | scripts/governance/d5_architecture/dm200913_rewrite_diagrams.py | L508 | 域列表(list) | `["D-FACTOR","D-SIGNAL","D-SIGNAL_FUNDAMENTAL","D-SIGNAL_ASHARE","D-SIGNAL_QUALITY"]` | `["D-FACTOR","D-SIGLEGACY","D-FUNDAMENTAL_SIGNAL","D-ASHARE_SIGNAL","D-SIGQC"]` |
| 3 | 同上 | L78,107,108,156,157,190,199,294,295,464,585,615,828 | 展示型(13处) | 含 `D-SIGNAL` 文本 | 批量替换为新域名显示文本 |
| 4 | scripts/governance/d5_architecture/dm200916_write_direct.py | L314-317 | YAML primary_domains | 4个旧域名各一行 | 4个新域名各一行 |
| 4 | 同上 | L425 | YAML name | `name: D-SIGNAL × C2` | `name: D-SIGLEGACY × C2` |
| 4 | 同上 | L426 | YAML domain | `domain: D-SIGNAL` | `domain: D-SIGLEGACY` |
| 5 | scripts/governance/d5_architecture/generators/generate_capability_heatmap.py | L59 | 域列表 | `["D-FACTOR","D-SIGNAL","D-SIGNAL_FUNDAMENTAL","D-SIGNAL_ASHARE","D-SIGNAL_QUALITY"]` | `["D-FACTOR","D-SIGLEGACY","D-FUNDAMENTAL_SIGNAL","D-ASHARE_SIGNAL","D-SIGQC"]` |
| 6 | scripts/governance/audit_domain_nodes.py | L316 | 域列表(domains_13) | `"D-SIGNAL",` | `"D-SIGLEGACY",` |
| 6 | 同上 | L363 | print标签 | `"STEP 4: D-SIGNAL / D-SIMULATION details"` | `"STEP 4: D-SIGLEGACY / D-SIMULATION details"` |
| 6 | 同上 | L364 | SQL迭代 | `for dom in ["D-SIGNAL", "D-SIMULATION"]:` | `for dom in ["D-SIGLEGACY", "D-SIMULATION"]:` |

**确认**：无动态拼接 domain_id（所有引用均为静态字面量）

### 3.6 手动维护文档修改清单（29个文件，~198行）

#### 3.6.1 活文档（当前有效配置，直接替换域名）

| # | 文件 | 行数 | 修改类型 |
|---|---|---:|---|
| 1 | docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml | 4 | 注释+正文(数据) |
| 2 | docs/02_enterprise_architecture/target_architecture/index.md | 4 | 表格 |
| 3 | docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml | 4 | 正文(数据) |
| 4 | docs/02_enterprise_architecture/target_architecture/architecture_model/contracts/cross_layer_contracts.yaml | 11 | 正文(数据) |
| 5 | docs/02_enterprise_architecture/target_architecture/architecture_model/contracts/consumer_registry.yaml | 5 | 正文(数据) |
| 6 | docs/02_enterprise_architecture/target_architecture/architecture_model/cross_cutting/runtime_planes.yaml | 4 | 正文(数据) |
| 7 | docs/02_enterprise_architecture/target_architecture/architecture_model/cross_cutting/capability_heatmap.yaml | 6 | 正文(数据) |
| 8 | docs/02_enterprise_architecture/target_architecture/application_architecture.md | 1 | 表格 |
| 9 | docs/02_enterprise_architecture/target_architecture/capability_heatmap.md | 5 | 表格 |
| 10 | docs/02_enterprise_architecture/target_architecture/technology_architecture.md | 3 | 正文+表格 |
| 11 | docs/02_enterprise_architecture/target_architecture/diagrams/c4_l2_containers.mmd | 2 | 正文+注释 |
| 12 | docs/02_enterprise_architecture/target_architecture/diagrams/dataflow_terminal.mmd | 2 | 注释+正文 |
| 13 | docs/02_enterprise_architecture/target_architecture/diagrams/capability_heatmap_visual.mmd | 4 | 正文(mermaid) |
| 14 | docs/02_enterprise_architecture/target_architecture/diagrams/c4_l3_l11_ml_platform.mmd | 1 | 正文 |
| 15 | docs/02_enterprise_architecture/target_architecture/diagrams/data_flow.mmd | 4 | 正文+注释 |
| 16 | docs/02_enterprise_architecture/target_architecture/diagrams/integration_topology.mmd | 3 | 正文+注释 |
| 17 | docs/02_enterprise_architecture/target_architecture/diagrams/runtime_topology.mmd | 1 | 正文 |
| 18 | docs/03_modules/index.md | 4 | 正文+表格/链接 |
| 19 | docs/03_modules/_domain_signal/index.md | 3 | 标题+正文 |
| 20 | docs/03_modules/_alpha_signal_domain/index.md | 1 | 正文 |
| 21 | docs/03_modules/content_layering_task_cards.md | 9 | 标题+正文+表格 |
| 22 | docs/01_policies_and_standards/templates/dependency_graph_template.md | 1 | 表格 |
| **小计** | | **82** | |

#### 3.6.2 历史记录文档（追加推翻说明，保留旧名上下文）

| # | 文件 | 行数 | 处理方式 |
|---|---|---:|---|
| 23 | docs/02_enterprise_architecture/dependency_architecture_panorama.md | 9 | **追加裁定#204**（推翻#ARCH-002/#ARCH-004）+ 在#201记录处标注"已被#204推翻" |
| 24 | docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md | ~45 | 在#ARCH-002/#ARCH-003/#ARCH-004议题处标注"已被#204推翻" + 追加#204执行记录 |
| 25 | docs/02_enterprise_architecture/architecture_upgrade_discussion.md | 12 | 历史讨论记录，追加"注：#204已推翻#ARCH-002/#ARCH-004，4域改名" |
| 26 | docs/_working/domain_split_plan_4_oversized_domains.md | 1 | 历史拆分方案，追加推翻说明 |
| 27 | docs/02_enterprise_architecture/t18_implementation_plan.md | 1 | 历史实施计划，追加推翻说明 |
| 28 | docs/02_enterprise_architecture/03_governance_reports/d_signal_rename_plan.md | ~45 | 本方案文档自身，执行后更新为"已执行" |
| 29 | data/pending_manual_completion_list.md | 3 | 待完成清单 |
| **小计** | | **~116** | |

**注**：原#28-34（cross_domain_matrix.md/runtime_plane_mapping.md/integration_topology.md/capability_heatmap.md/design_vs_production.md/constraint_violations.md/capacity_report.md）经确认全部是**生成制品**（头部含"本文档由 xxx.py 自动生成"），已移至3.7节。

### 3.7 生成制品（DB改名后重新生成，不手动改）

| 文件/目录 | 生成器 | 确认方式 |
|---|---|---|
| docs/02_enterprise_architecture/02_domain_architecture_docs/domain_index.md | generate_domain_index.py | 头部"由 generate_domain_index.py 自动生成" |
| docs/02_enterprise_architecture/02_domain_architecture_docs/01-43_*.md | generate_domain_doc.py | 头部"由 generate_domain_doc.py 自动生成" |
| docs/02_enterprise_architecture/02_domain_architecture_docs/*_architecture.md | generate_domain_architecture_diagram.py | 头部"由 generate_domain_architecture_diagram.py 自动生成" |
| docs/02_enterprise_architecture/generated/domains/*.mmd | dm200913_rewrite_diagrams.py | 头部"由 dm200913 自动生成" |
| docs/02_enterprise_architecture/01_global_architecture_diagram/cross_domain_matrix.md | generate_cross_domain_matrix.py | 头部确认（L15） |
| docs/02_enterprise_architecture/01_global_architecture_diagram/runtime_plane_mapping.md | generate_runtime_plane_mapping.py | 头部确认（L15） |
| docs/02_enterprise_architecture/01_global_architecture_diagram/integration_topology.md | dm200912_rewrite_views.py | 头部确认 |
| docs/02_enterprise_architecture/01_global_architecture_diagram/capability_heatmap.md | generate_capability_heatmap.py | 头部确认（L15） |
| docs/02_enterprise_architecture/03_governance_reports/design_vs_production.md | generate_design_vs_production.py | 头部确认（L15） |
| docs/02_enterprise_architecture/03_governance_reports/constraint_violations.md | generate_constraint_violations.py | 头部确认（L15） |
| docs/02_enterprise_architecture/03_governance_reports/capacity_report.md | generate_capacity_report.py | 头部确认（L15） |
| data/asset_index/project_entity_depgraph.yaml | generate_project_depgraph.py | 生成器输出 |
| data/asset_index/target_path_tree.yaml | generate_project_depgraph.py | 生成器输出 |

---

## 第四部分：执行步骤（施工细节级）

### 4.1 阶段0：备份

```bash
# 0.1 GitCommitGateway 备份当前 depgraph.db
python scripts/git_commit.py --session rename-signal-backup \
  --files data/databases/depgraph.db \
  --message "backup: depgraph before D-SIGNAL* rename (#204)"

# 0.2 apply_depgraph.py 物理备份
python scripts/governance/apply_depgraph.py --backup "pre-rename-signal"
```

### 4.2 阶段1：DB 改名（apply_depgraph.py 新增 cmd_rename_domain）

**前提**：在 apply_depgraph.py 中新增 `cmd_rename_domain(old_id, new_id)` 命令。

**新增命令的 18 步 UPDATE 逻辑**（覆盖所有需 UPDATE 的 11 张表，edges.cross_domain 为 boolean 不需改）：

```python
def cmd_rename_domain(old_id: str, new_id: str, dry_run: bool = False):
    """重命名域ID——更新所有含 domain 相关列的表"""
    # 0. 检查 new_id 不存在
    # 1. UPDATE domains SET domain_id=new_id WHERE domain_id=old_id
    # 2. UPDATE nodes SET domain_id=new_id WHERE domain_id=old_id
    # 3. UPDATE nodes SET subdomain_id=new_id WHERE subdomain_id=old_id
    # 4. UPDATE nodes SET belongs_to=new_id WHERE belongs_to=old_id  ← v1遗漏！
    # 5. UPDATE domain_dependencies SET from_domain=new_id WHERE from_domain=old_id
    # 6. UPDATE domain_dependencies SET to_domain=new_id WHERE to_domain=old_id
    # 7. UPDATE domain_events SET source_domain=new_id WHERE source_domain=old_id
    # 8. UPDATE domain_events SET target_domains=REPLACE(target_domains, old_id, new_id) WHERE target_domains LIKE '%old_id%'
    # 9. UPDATE contracts SET provider_domain=new_id WHERE provider_domain=old_id
    # 10. UPDATE contracts SET consumer_domain=new_id WHERE consumer_domain=old_id
    # 11. UPDATE invariants SET domain_id=new_id WHERE domain_id=old_id
    # 12. UPDATE arch_constraints SET from_domain=new_id WHERE from_domain=old_id
    # 13. UPDATE arch_constraints SET to_domain=new_id WHERE to_domain=old_id
    # 14. UPDATE arch_directory_tree SET domain_id=new_id WHERE domain_id=old_id
    # 15. UPDATE arch_path_mappings SET domain_id=new_id WHERE domain_id=old_id
    # 16. UPDATE domain_mapping SET domain_id=new_id WHERE domain_id=old_id
    # 17. UPDATE domain_mapping SET subdomain_id=REPLACE(subdomain_id, old_id, new_id) WHERE subdomain_id LIKE '%old_id%'  ← v2第2轮修正：精确匹配会漏行（值为D-SIGNAL_FUNDAMENTAL-FACTOR）
    # 18. UPDATE rule_bindings SET domain_id=new_id WHERE domain_id=old_id
```

**执行 4 个改名**（顺序无依赖）：

```bash
python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL_ASHARE D-ASHARE_SIGNAL
python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL_FUNDAMENTAL D-FUNDAMENTAL_SIGNAL
python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL_QUALITY D-SIGQC
python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL D-SIGLEGACY
```

**更新 domains 表 domain_name**：

```bash
python scripts/governance/apply_depgraph.py --update-domain-name D-ASHARE_SIGNAL "A股特色信号"
python scripts/governance/apply_depgraph.py --update-domain-name D-FUNDAMENTAL_SIGNAL "基本面信号"
python scripts/governance/apply_depgraph.py --update-domain-name D-SIGQC "信号质量控制"
python scripts/governance/apply_depgraph.py --update-domain-name D-SIGLEGACY "信号遗留设计态"
```

### 4.3 阶段2：代码文件 [DOMAIN] 头部修改（10个文件）

对 3.3 节列出的 10 个文件，逐个用 Edit 工具修改 L3 的 [DOMAIN] 头部。

**施工动作示例**（以 pipeline.py 为例）：
```
文件: src/zephyr/signal_fundamental/pipeline.py
行号: L3
原内容: # [DOMAIN] D-SIGNAL
新内容: # [DOMAIN] D-FUNDAMENTAL_SIGNAL
操作: Edit(old_string="# [DOMAIN] D-SIGNAL", new_string="# [DOMAIN] D-FUNDAMENTAL_SIGNAL")
```

### 4.4 阶段3：YAML registry 修改（1个文件）

修改 functional_domain_registry.yaml（3.4 节列出的 4 行 + 1 条新增）。

### 4.5 阶段4：生成器脚本修改（6个文件）

修改 3.5 节列出的 6 个文件中的硬编码 domain_id。

**优先级**：先改 domain_name_mapping.py（域名映射中心），再改其他5个。

### 4.6 阶段5：手动维护文档修改（29个文件）

**区分两类文档**：
- **活文档**（3.6.1节，22个文件）：直接替换域名
- **历史记录文档**（3.6.2节，7个文件）：追加推翻说明，保留旧名上下文

**已确认的生成制品**（3.7节）：以下文件经头部确认全部是生成制品，DB改名后重新生成，不手动改：
- 01_global_architecture_diagram/cross_domain_matrix.md（generate_cross_domain_matrix.py）
- 01_global_architecture_diagram/runtime_plane_mapping.md（generate_runtime_plane_mapping.py）
- 01_global_architecture_diagram/integration_topology.md（dm200912_rewrite_views.py）
- 01_global_architecture_diagram/capability_heatmap.md（generate_capability_heatmap.py）
- 03_governance_reports/design_vs_production.md（generate_design_vs_production.py）
- 03_governance_reports/constraint_violations.md（generate_constraint_violations.py）
- 03_governance_reports/capacity_report.md（generate_capacity_report.py）

### 4.7 阶段6：重新生成制品

```bash
# 6.1 资产索引
python scripts/governance/generate_project_depgraph.py

# 6.2 域架构文档
python scripts/governance/d5_architecture/generators/generate_domain_index.py
python scripts/governance/d5_architecture/generators/generate_domain_doc.py --all
python scripts/governance/d5_architecture/generators/generate_domain_architecture_diagram.py --all

# 6.3 治理报告
python scripts/governance/d5_architecture/generators/generate_capacity_report.py
python scripts/governance/d5_architecture/generators/generate_design_vs_production.py
python scripts/governance/d5_architecture/generators/generate_constraint_violations.py

# 6.4 全局架构图
python scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py
python scripts/governance/d5_architecture/generators/generate_runtime_plane_mapping.py
python scripts/governance/d5_architecture/generators/generate_capability_heatmap.py
python scripts/governance/d5_architecture/dm200912_rewrite_views.py
python scripts/governance/d5_architecture/dm200913_rewrite_diagrams.py
python scripts/governance/d5_architecture/dm200916_write_direct.py
```

### 4.8 阶段7：验证

```bash
# 7.1 验证 DB 无残留旧 domain_id（11表需UPDATE全覆盖，edges为boolean除外）
# 7.2 验证新 domain_id 存在
# 7.3 Grep 全局搜索旧域名（排除生成制品和历史记录文档）
```

### 4.9 阶段8：git commit

按类别分批提交：
1. apply_depgraph.py（新增 cmd_rename_domain）+ depgraph.db
2. 代码文件 [DOMAIN] 头部
3. YAML registry
4. 生成器脚本
5. 手动维护文档
6. 重新生成的制品

---

## 第五部分：回滚方案

### 5.1 DB 回滚
```bash
git checkout HEAD~1 -- data/databases/depgraph.db
```

### 5.2 文件回滚
```bash
git checkout HEAD~1 -- src/zephyr/signal_fundamental/ docs/01_policies_and_standards/_registry/ scripts/governance/ docs/02_enterprise_architecture/
```

### 5.3 生成制品回滚
重新运行生成器即可（DB 回滚后重新生成）。

---

## 第六部分：风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|---|---|---|---|
| cmd_rename_domain 遗漏某张表 | 低 | DB 数据不一致 | 18步UPDATE覆盖11表（12表含domain列，edges为boolean除外），dry-run先行 |
| nodes.belongs_to 181行未更新 | 高 | 节点归属错误 | v2已纳入18步UPDATE第4步（v1遗漏，已修正） |
| 活文档vs历史记录混淆 | 中 | 历史记录被破坏 | 3.6节明确区分两类 |
| 生成制品遗漏重新生成 | 中 | 制品与DB不一致 | 阶段6列出所有生成器 |
| domain_events.target_domains JSON未REPLACE | 高 | 事件路由错误 | 第9步用REPLACE处理JSON/TEXT |
| domain_mapping.subdomain_id 精确匹配漏行 | 高 | mapping_id=91未更新 | 第17步改为REPLACE+LIKE匹配（第2轮审查发现） |
| 生成器脚本硬编码遗漏 | 低 | 重新生成的制品错误 | 3.5节逐行列出~23处 |

---

## 第七部分：根因分析（漂移和幻觉的根因）

### 7.1 到底是什么发生了漂移和幻觉？

**核心漂移链**：

```
根因1：命名规则未写入DB（AI看不见）
    ↓
D-SIGNAL 被创建为"信号域"（合理），后拆分为3子域
    ↓
子域命名为 D-SIGNAL_ASHARE/FUNDAMENTAL/QUALITY（前缀暗示父子）
    ↓
裁定#ARCH-002 误判"命名前缀不等于子域关系"（未从第一性原理分析）
    ↓
裁定#ARCH-004 误判"保留D-SIGNAL为占位域"（未分析45个虚拟节点本质）
    ↓
D-SIGNAL 持续存在，AI 在生成代码/文档时看到 D-SIGNAL_ 前缀
    ↓
AI 幻觉：认为 D-SIGNAL 是父域，D-SIGNAL_* 是子域（违反"所有域平级"硬约束）
    ↓
pipeline.py [DOMAIN] 误标为 D-SIGNAL（应为 D-SIGNAL_FUNDAMENTAL）
```

### 7.2 漂移的3个层次

| 层次 | 漂移表现 | 根因 |
|---|---|---|
| **L1 命名漂移** | D-SIGNAL_* 前缀暗示父子关系 | 命名时未查阅"无子域"硬约束 |
| **L2 裁定漂移** | #ARCH-002/#ARCH-004 误判 | 裁定时未从第一性原理分析节点本质 |
| **L3 代码漂移** | pipeline.py [DOMAIN] 误标 | AI 生成代码时看不见域定义规则 |

### 7.3 为什么 AI 会产生幻觉？

1. **规则不可见**：命名规则在 project_memory.md（Markdown），AI 在生成代码/建域时**不会主动查阅**
2. **DB 无约束**：domains 表无 CHECK 约束防止 `_` 前缀暗示父子关系
3. **无建域门禁**：新建域时无强制校验命名是否符合规则
4. **裁定历史不透明**：#ARCH-002/#ARCH-004 的裁定理由未写入 DB，AI 看不见"为什么这样命名"

---

## 第八部分：预防机制设计（规则入DB，AI建域时可见）

### 8.1 方案：在 depgraph.db 新增 domain_naming_rules 表

```sql
CREATE TABLE IF NOT EXISTS domain_naming_rules (
    rule_id TEXT PRIMARY KEY,           -- 规则ID，如 NR-001
    rule_name TEXT NOT NULL,            -- 规则名称
    rule_text TEXT NOT NULL,            -- 规则全文（AI可读）
    applies_to TEXT NOT NULL,           -- 适用场景：create_domain/rename_domain/all
    severity TEXT NOT NULL,             -- error/warning
    example_bad TEXT,                   -- 错误示例
    example_good TEXT,                  -- 正确示例
    created_at TEXT NOT NULL,
    source_doc TEXT                     -- 来源文档路径
);
```

### 8.2 初始规则数据

| rule_id | rule_name | rule_text | applies_to | severity | example_bad | example_good |
|---|---|---|---|---|---|---|
| NR-001 | 无父子前缀 | 域ID禁止使用 D-XXX_YYY 形式暗示父子关系，所有域平级 | create/rename | error | D-SIGNAL_ASHARE | D-ASHARE_SIGNAL |
| NR-002 | snake_case命名 | 域ID格式：D-大写业务词_大写类型词，全大写+下划线 | create/rename | error | D-signal-ashare | D-ASHARE_SIGNAL |
| NR-003 | 语义独立性 | 域ID必须能独立表达业务含义，不依赖父域前缀 | create/rename | error | D-SIGNAL_QUALITY（依赖SIGNAL） | D-SIGQC |
| NR-004 | 设计态标识 | 设计态占位域必须用 LEGACY/PLACEHOLDER 后缀明确标识 | create | warning | D-SIGNAL（占位域） | D-SIGLEGACY |
| NR-005 | 中文名一致 | domain_name 必须与 domain_id 的语义一致 | create/rename | warning | D-SIGQC / "信号" | D-SIGQC / "信号质量控制" |

### 8.3 apply_depgraph.py 新增建域门禁

在 `--insert-domain` 命令中新增**命名规则校验**：
1. 查询 domain_naming_rules 表所有 applies_to=create 的规则
2. 对新 domain_id 逐条校验
3. severity=error 的规则违反 → 阻断建域（exit 3）
4. severity=warning 的规则违反 → 打印警告但允许建域

```bash
# 示例：AI 尝试创建违反 NR-001 的域
python scripts/governance/apply_depgraph.py --insert-domain D-SIGNAL_NEWSUB "新子域" 业务 L2_domain src/zephyr/new/
# 输出：[NAMING-RULE VIOLATION] NR-001: 域ID禁止使用 D-XXX_YYY 形式暗示父子关系
# exit 3
```

### 8.4 domain_name_mapping.py 自动校验

在 `get_domain_name_zh()` 函数中新增校验：
- 如果 domain_id 不在 DOMAIN_NAME_ZH 字典中，查询 DB 的 domain_naming_rules 表
- 如果 domain_id 违反 NR-001（含 `_` 前缀暗示父子），打印警告

### 8.5 规则同步机制

- domain_naming_rules 表数据从 YAML 文件同步（遵循"YAML是唯一真源"硬约束）
- 新增 `docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml`
- sync_yaml_to_depgraph.py 新增同步逻辑

---

## 第九部分：裁定记录

### 9.1 新增裁定#204：D-SIGNAL* 4 域改名

- **执行日期**：待定（用户批准后执行）
- **推翻**：裁定#ARCH-002（保留命名）、裁定#ARCH-004（保留 D-SIGNAL 占位域原名）
- **内容**：
  - D-SIGNAL_ASHARE → D-ASHARE_SIGNAL
  - D-SIGNAL_FUNDAMENTAL → D-FUNDAMENTAL_SIGNAL
  - D-SIGNAL_QUALITY → D-SIGQC
  - D-SIGNAL → D-SIGLEGACY
- **依据**：第一性原理分析（D-SIGNAL 本质是遗留设计态规划，非3子域父域）+ 命名规则 + AI 适用性
- **预防措施**：新增 domain_naming_rules 表 + 建域门禁（第八部分）

---

## 附录A：检查清单（循环审查用）

| # | 检查项 | 结果 |
|---|---|---|
| 1 | DB 11表UPDATE全覆盖+edges确认无需改（无遗漏表/列） | ✅ |
| 2 | nodes.belongs_to 181行已纳入 | ✅ |
| 3 | domain_events.target_domains JSON已用REPLACE | ✅ |
| 4 | 代码文件数量正确（10个非11个） | ✅ |
| 5 | alpha_signal_pipeline.py 不需改已确认 | ✅ |
| 6 | 生成器脚本无动态拼接 | ✅ |
| 7 | 活文档vs历史记录已区分 | ✅ |
| 8 | domain_index.md确认为生成制品 | ✅ |
| 9 | 生成制品重新生成命令完整 | ✅ |
| 10 | 回滚方案可行 | ✅ |
| 11 | 根因分析完整（3层漂移） | ✅ |
| 12 | 预防机制可执行（domain_naming_rules表+门禁） | ✅ |
| 13 | 前后无冲突（裁定#204 vs #ARCH-002/#ARCH-004） | ✅ |
| 14 | 新域名无命名冲突（4个新ID不与现有53域重复） | ✅ |
| 15 | domain_mapping.subdomain_id 用REPLACE（非精确匹配，值含-FACTOR后缀） | ✅（第2轮新增） |
| 16 | 3.2节4列小计算术验证通过（235+84+105+64=488） | ✅（第2轮新增） |
| 17 | domain_mapping.domain_id 1行已纳入统计表 | ✅（第2轮新增） |
| 18 | edges.cross_domain 确认为boolean(0/1/NULL)，无需UPDATE | ✅（第2轮新增） |

## 附录B：循环审查记录

| 轮次 | 审查日期 | 发现问题数 | 修复状态 | 问题摘要 |
|---|---|---:|---|---|
| 第1轮 | 2026-06-25 | 10 | ✅ 全部修复 | ①7个生成制品误计为手动文档→移至3.7节 ②3.7节新增生成制品条目 ③3.6节手动文档数36→29 ④3.1节对比表数字更新 ⑤4.6节生成制品确认 ⑥4.6节历史文档数14→7 ⑦4.7节生成器路径修正+新增4个命令 ⑧4.2节UPDATE步数17→18 ⑨风险评估步数17→18+步骤号修正 ⑩附录B/C更新 |
| 第2轮 | 2026-06-25 | 6 | ✅ 全部修复 | ①domain_mapping.subdomain_id精确匹配漏行（值D-SIGNAL_FUNDAMENTAL-FACTOR带后缀）→UPDATE步骤17改为REPLACE+LIKE ②domain_mapping.domain_id 1行未列入3.2统计表→新增行 ③arch_constraints.to_domain 0行未列入3.2统计表→新增行 ④edges.cross_domain描述不准确（说"无domain_id列"实际有cross_domain列）→改为"boolean无需改" ⑤3.2节4列小计算术错误（D-SIGNAL 225→235、ASHARE 85→84、QUAL 73→64）→修正 ⑥"12表"表述不清→改为"12表含domain列，11表需UPDATE" |
| 第3轮 | 2026-06-25 | 1 | ✅ 已修复 | ①4.2节注释"覆盖所有含domain相关列的12张表"与全文不一致→改为"覆盖所有需UPDATE的11张表，edges.cross_domain为boolean不需改" |
| 第4轮 | 2026-06-25 | 0 | ✅ 零问题 | 全文一致性验证通过：数字一致（488/235/84/105/64）、表数一致（12表含domain列/11表需UPDATE）、步数一致（18步UPDATE）、文件数一致（29手动/10代码/6生成器/1 YAML/13生成制品）、UPDATE方法一致（步骤8和17用REPLACE） |
| 第5轮 | 2026-06-25 | 0 | ✅ 零问题 | 第4轮后仅更新附录B元数据，内容无变化。最终确认：无待审查项、无待确认项、无前后冲突。**连续2次零问题（第4轮+第5轮），循环审查通过。** |

## 附录C：待确认事项（已全部确认 ✅）

1. **01_global_architecture_diagram/*.md 是否为生成制品**：✅ 已确认——cross_domain_matrix.md（generate_cross_domain_matrix.py）、runtime_plane_mapping.md（generate_runtime_plane_mapping.py）、integration_topology.md（dm200912_rewrite_views.py）、capability_heatmap.md（generate_capability_heatmap.py）全部为生成制品，头部均含"本文档由 xxx.py 自动生成"标记
2. **03_governance_reports/design_vs_production.md 等是否为生成制品**：✅ 已确认——design_vs_production.md（generate_design_vs_production.py）、constraint_violations.md（generate_constraint_violations.py）、capacity_report.md（generate_capacity_report.py）全部为生成制品，头部均含自动生成标记
3. **生成器CLI参数**：✅ 已确认——见4.7节，generate_domain_doc.py / generate_domain_architecture_diagram.py 使用 `--all` 参数，其余无参数或使用默认配置
