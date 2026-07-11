---
module_id: MOD-INF-037
submodule_path: src/zephyr/governance/registry_governance
title: "注册表治理"
doc_type: blueprint
status: Draft
version: "0.2.0"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
date: "2026-05-16"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/infrastructure/registry_governance.py"
last_updated: "2026-05-16"
last_verified: "2026-05-16"
generation: 1
functional_domain: governance
summary: "注册表体系架构+功能域注册表+SSoT门禁+一致性校验+物理路径树(REG-017)+路径归属图(REG-018)+路径树刷新门禁(G6_PT)"
template_for: blueprint
tags: [registry, governance, ssot, scaffold]
priority: P1
runtime_plane: warm
belongs_to: "MOD-MASTER_BLUEPRINT"
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-INF-005
    at: §3
    why: scaffold.py是注册表创建的唯一入口
  - target: MOD-INF-017
    at: §2
    why: code_dedup_engine提供Token级去重，功能域注册表补充语义级去重
  - target: MOD-INF-026
    at: §4
    why: 资产盘点系统消费注册表数据
  - target: MOD-GATE_ENGINE
    at: §3
    why: Gate Engine执行G6_PT路径树刷新门禁
references:
  - path: docs/registry_of_registries.yaml
    section: ""
    why: 43个注册表的主索引
  - path: docs/01_policies_and_standards/templates/register-registry.md
    section: ""
    why: TPL-REGISTER-001注册表模板
ssot_claims:
  - claim: "功能域注册表是模块/脚本功能域声明的唯一真源"
    scope: global
  - claim: "SSoT门禁是创建新模块/脚本时功能域重叠检测的唯一入口"
    scope: global
  - claim: "物理路径树快照(project-path-tree.yaml)是项目目录结构的唯一磁盘事实真源"
    scope: global
  - claim: "路径归属声明(path_ownership_map.yaml)是蓝图→文件路径映射的唯一真源"
    scope: global
responsibility_domain: 
design_maturity: design
build_status: generated
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
蓝图 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/check_blueprint_compliance.py <蓝图路径>
-->
<!--
REQUIRED_SECTIONS:
  overview: "概述"
  §0: "代码对齐验证"
  §0.1: "代码文件清单"
  §0.2: "对齐验证矩阵"
  §0.3: "版本-代码映射"
  §0.4: "SSoT与责任唯一性"
  §0.5: "代码目录唯一性"
  §1: "设计背景与目标"
  §1.1: "背景"
  §1.2: "目标范围"
  §1.4: "运行场景约束"
  §1.5: "利益相关者"
  §1.6: "差距"
  §1.7: "典型场景"
  §2: "模块边界"
  §2.1: "职责边界"
  §3: "架构设计"
  §3.1: "组件架构"
  §3.2: "数据流"
  §3.3: "状态生命周期"
  §4: "接口契约"
  §4.1: "公共 API"
  §4.2: "数据模型"
  §4.3: "输入契约"
  §4.4: "输出契约"
  §4.5: "MCP 接口"
  §4.6: "契约版本"
  §4.7: "OCP 扩展点"
  §5: "约束条件"
  §5.1: "技术约束"
  §5.2: "容量估算"
  §5.3: "迁移"
  §5.4: "非功能需求与服务水平"
  §5.7: "禁止模式与导入约束"
  §6: "错误处理"
  §6.1: "可观测性"
  §6.2: "退化矩阵"
  §8: "安全考量"
  §9: "测试策略"
  §10: "依赖关系"
  §10.5: "概念重叠声明"
  §10.6: "依赖链风险评级"
  §11: "产出物"
  §12: "集成目标"
  §13: "需要更新"
  §14: "风险"
  §16: "施工指引"
  §16.7: "参考实现规格"
  §16.8: "施工参考卡"
  §16.10: "故障与操作"
  §16.12: "并发操作"
  §17: "容量升级"
  §18: "决策记录"
  glossary: "术语表"
  blindspots: "已知问题"
  checklist: "自检与闭合清单"
  maturity: "成熟度"
  roadmap: "版本演进路线图"
  pre_1: "Vibe Coding"
  pre_2: "安全删除"
  pre_3: "必备链接"
  pre_4: "已有类似功能"
  pre_5: "涉及的文件范围"
  ssot_claims: "frontmatter必须包含ssot_claims字段"
  consumer_min: "§11产出物表格必须包含consumer_min列"
  overlap_check: "§2.1必须包含职责唯一性声明表格"
END_REQUIRED_SECTIONS
-->

# Registry Governance 蓝图+施工图 — 注册表体系架构+功能域注册表+SSoT门禁

> module_id: MOD-INF-037 | version: 0.2.0 | status: Draft | domain: infra_ops
> actual_disk_path: src/zephyr/infra_ops/ | generation: 1 | construction_progress: partially_implemented

## 概述

本蓝图描述注册表治理模块——解决43个注册表58%无蓝图、scaffold.py功能查重形同虚设、功能域注册表不存在三个核心问题。核心职责：功能域注册表管理、SSoT门禁、注册表一致性校验。上游依赖scaffold.py(MOD-INF-005)和code_dedup_engine(MOD-INF-017)，下游被asset_index(MOD-INF-026)消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 优化规则：先 Layer 1（蓝图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-037`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 归属判定 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|---------|
| 1 | registry_governance.py | §3.1 | 功能域注册表管理+SSoT门禁+一致性校验入口 | ✅ | 本模块 | — |
| 2 | `scripts/governance/generate_project_path_tree.py` | §3.1 | 物理路径树快照生成(REG-017) | ✅ | 本模块 | — |
| 3 | `scripts/governance/generators/generate_path_ownership_map.py` | §3.1 | 路径归属声明生成+冲突检测(REG-018) | ✅ | 本模块 | — |
| 4 | `src/zephyr/governance/rule_enforcement/g6-path-tree-freshness.yaml` | §3.1 | 路径树刷新强制门禁(G6_PT) | ✅ | 本模块 |
| 5 | `__init__.py` | §3.1 |   init   | 已实现 | — |
| 6 | `auto_diagnostics.py` | §3.1 | auto diagnostics | 已实现 | — |
| 7 | `config.py` | §3.1 | config | 已实现 | — |
| 8 | `config_validator.py` | §3.1 | config validator | 已实现 | — |
| 9 | `contract_tester.py` | §3.1 | contract tester | 已实现 | — |
| 10 | `cost_tracker.py` | §3.1 | cost tracker | 已实现 | — |
| 11 | `dry_run_simulator.py` | §3.1 | dry run simulator | 已实现 | — |
| 12 | `event_bus_upgrade.py` | §3.1 | event bus upgrade | 已实现 | — |
| 13 | `event_store.py` | §3.1 | event store | 已实现 | — |
| 14 | `finding_task_bridge.py` | §3.1 | finding task bridge | 已实现 | — |
| 15 | `infrastructure_base.py` | §3.1 | infrastructure base | 已实现 | — |
| 16 | `kill_switch_sim.py` | §3.1 | kill switch sim | 已实现 | — |
| 17 | `local-model.py` | §3.1 | local-model | 已实现 | — |
| 18 | `pydantic_v2_migrator.py` | §3.1 | pydantic v2 migrator | 已实现 | — |
| 19 | `registry_governance.py` | §3.1 | registry governance | 已实现 | — |
| 20 | `warm_hot_gate.py` | §3.1 | warm hot gate | 已实现 | — | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 代码目录存在且非空 | `ls src/zephyr/infrastructure/runtime_integration/registry_governance.py` | ✅ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" registry_governance.py` | ✅ |
| 代码 [BLUEPRINT] 头部指向 = MOD-INF-037 | `grep "\[BLUEPRINT\]" registry_governance.py` | ✅ |
| 路径树生成脚本 [BLUEPRINT] = MOD-INF-037 | `grep "\[BLUEPRINT\]" scripts/governance/generate_project_path_tree.py` | ✅ |
| 归属图生成脚本 [BLUEPRINT] = MOD-INF-037 | `grep "\[BLUEPRINT\]" scripts/governance/generators/generate_path_ownership_map.py` | ✅ |
| G6_PT门禁已注册到gate registry | `grep "G6_PT" src/zephyr/governance/rule_enforcement/_registry.yaml` | ✅ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (基线) | FunctionalDomainRegistry+DomainEntry+OverlapResult | RegistryConsistencyChecker+CheckResult+SSoTGate | 待Phase 3施工 |
| v0.2.0 (路径树) | +generate_project_path_tree.py+generate_path_ownership_map.py+g6-path-tree-freshness.yaml | RegistryConsistencyChecker+CheckResult+SSoTGate | 待Phase 3施工 |

### §0.4 SSoT 与责任唯一性声明

| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | 功能域注册表数据 | ✅ | ❌ | — |
| 2 | SSoT门禁判定逻辑 | ✅ | ❌ | — |
| 3 | 注册表一致性校验规则 | ✅ | ❌ | — |
| 4 | 注册表YAML格式Schema | ❌ | ✅ | TPL-REGISTER-001 |
| 5 | scaffold.py创建入口 | ❌ | ✅ | MOD-INF-005 §3 |
| 6 | 物理路径树快照数据 | ✅ | ❌ | — |
| 7 | 路径归属声明数据 | ✅ | ❌ | — |
| 8 | 路径树刷新门禁规则 | ✅ | ❌ | — |

### §0.5 代码目录唯一性声明

| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/infra_ops/` |
| 2 | 脚本目录 | `scripts/governance/` (generate_project_path_tree.py, generate_path_ownership_map.py) |
| 3 | 门禁目录 | `src/zephyr/governance/rule_enforcement/` (g6-path-tree-freshness.yaml) |
| 4 | 已知副本目录 | 无 |
| 5 | 副本处置状态 | 无副本 |

---

## §1 设计背景与目标

### 1.1 背景

| 问题 | 数据 | 影响 |
|------|------|------|
| 43个注册表58%无蓝图 | registry_of_registries.yaml登记43个，仅18个有蓝图 | 注册表设计无据可查，AI无法理解注册表意图 |
| scaffold.py功能查重形同虚设 | scaffold.py仅做文件名冲突检测，无语义级功能域查重 | 同功能模块/脚本可重复创建 |
| 功能域注册表不存在 | Grep确认无functional-domain-registry | 模块/脚本的功能域声明无处登记 |

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 功能域注册表（functional-domain-registry.yaml） | 每个模块/脚本声明功能域，支持查询和重叠检测 |
| 2 | ✅ 包含 | SSoT门禁（scaffold.py加固） | 创建新模块/脚本时强制检查功能域重叠 |
| 3 | ✅ 包含 | 注册表一致性校验脚本 | 检测注册表间引用断裂、条目过期、Schema漂移 |
| 4 | ❌ 排除 | 注册表内容迁移 | 现有43个注册表数据不动，仅新增功能域注册表 |
| 5 | ❌ 排除 | 注册表Schema统一 | 各注册表保持现有Schema，仅定义功能域注册表Schema |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 施工轨道：T轨可施工 | AI可按§16施工指引执行 |
| 功能域注册表为YAML静态文件 | 无数据库依赖，读写均为文件I/O |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 功能域注册表SSoT权威性 | 设计+施工 | 审批功能域分类体系 |
| AI Agent | 创建新模块/脚本时功能域查重 | 施工 | 必须通过SSoT门禁 |
| 治理脚本 | 注册表一致性校验 | 运行 | 消费注册表数据 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 功能域声明 | 不存在 | 每个模块/脚本声明功能域 | 功能域注册表+声明流程 | P1 |
| 功能域查重 | scaffold.py仅文件名冲突 | 语义级功能域重叠检测 | SSoT门禁逻辑 | P1 |
| 注册表一致性 | 无自动校验 | 定期校验+断裂告警 | 一致性校验脚本 | P2 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 新建模块 | `scaffold.py module <pkg> <name>` | ①scaffold读取功能域注册表→②查询--domain参数对应功能域→③检测重叠→④无重叠→创建+注册功能域 | 模块创建成功+功能域注册 |
| 功能域重叠 | scaffold检测到重叠 | ①输出重叠报告(已有模块+功能域)→②建议复用或扩展→③AI决策 | 重叠报告+复用建议 |
| 注册表断裂 | 定期校验或CI触发 | ①扫描所有注册表→②检查条目引用完整性→③输出断裂清单 | 断裂报告 |

---

## §2 模块边界

### 2.1 职责边界

> **核心职责声明**：本蓝图的核心职责是 `注册表体系的功能域声明、SSoT门禁、一致性校验、物理路径树生成、路径归属声明、路径树刷新门禁`。职责数量：6。

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 功能域注册表管理 | 维护functional-domain-registry.yaml，提供load/query_domain/check_overlap/register | 本模块 |
| 2 | ✅ 包含 | SSoT门禁 | scaffold.py创建流程中嵌入功能域重叠检测 | 本模块(scaffold加固) |
| 3 | ✅ 包含 | 注册表一致性校验 | 检测注册表间引用断裂、条目过期、Schema漂移 | 本模块 |
| 4 | ✅ 包含 | 物理路径树生成 | 磁盘扫描→project-path-tree.yaml，AI冷启动第一步 | 本模块 |
| 5 | ✅ 包含 | 路径归属声明+冲突检测 | 蓝图§0.1聚合→path_ownership_map.yaml，检测同路径多蓝图冲突 | 本模块 |
| 6 | ✅ 包含 | 路径树刷新门禁 | G6_PT强制文件创建/删除/移动后刷新路径树，Session关门前--check | 本模块 |
| 7 | ❌ 排除 | 注册表创建 | scaffold.py已有，不重复 | MOD-INF-005 |
| 8 | ❌ 排除 | Token级代码去重 | code_dedup_engine已有 | MOD-INF-017 |
| 9 | ❌ 排除 | 资产盘点 | asset_index已有 | MOD-INF-026 |

#### 职责唯一性声明

| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 功能域注册表管理 | [MOD-INF-005, MOD-INF-017] | `python scripts/governance/d5_architecture/checkers/check_ssot_uniqueness.py --warn-only` |
| SSoT门禁 | [MOD-INF-005, MOD-GATE_ENGINE] | 同上 |
| 注册表一致性校验 | [MOD-INF-026] | 同上 |
| 物理路径树生成 | [MOD-INF-005, MOD-INF-026] | `python scripts/governance/generate_project_path_tree.py --check` |
| 路径归属声明+冲突检测 | [MOD-INF-005] | `python scripts/governance/generators/generate_path_ownership_map.py --conflicts` |
| 路径树刷新门禁 | [MOD-GATE_ENGINE] | `grep "G6_PT" src/zephyr/governance/rule_enforcement/_registry.yaml` |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | FunctionalDomainRegistry | 功能域注册表CRUD+重叠检测 | functional-domain-registry.yaml | 同步调用 |
| 2 | SSoTGate | scaffold创建流程中的功能域门禁 | FunctionalDomainRegistry | 同步调用(scaffold注入) |
| 3 | RegistryConsistencyChecker | 注册表间引用断裂+过期+漂移检测 | registry_of_registries.yaml | 同步调用(CI/手动) |
| 4 | PathTreeGenerator | 磁盘扫描→物理路径树快照 | os.walk + pathlib | CLI: --write/--check |
| 5 | PathOwnershipAggregator | 蓝图§0.1聚合→路径归属+冲突检测 | 蓝图frontmatter+§0.1 | CLI: --write/--check/--conflicts |
| 6 | G6_PT PathTreeFreshnessGate | 路径树刷新强制门禁 | PathTreeGenerator+PathOwnershipAggregator | Gate Engine执行 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|--------|---------|---------|---------|---------|
| 1 | scaffold.py | ①读取--domain参数→②调用SSoTGate.check_overlap()→③无重叠→创建文件→④调用FunctionalDomainRegistry.register() | functional-domain-registry.yaml | str→DomainEntry→YAML | domain字符串→DomainEntry Pydantic模型→YAML序列化 |
| 2 | registry_of_registries.yaml | ①遍历所有注册表条目→②检查物理文件存在性→③检查条目Schema合规→④输出断裂清单 | stdout/报告文件 | YAML→dict→CheckResult | YAML解析→字段校验→CheckResult |
| 3 | 磁盘文件系统 | ①os.walk扫描5个根目录→②过滤__pycache__/.git等→③构建嵌套树结构→④YAML序列化 | project-path-tree.yaml | pathlib→dict→YAML | 目录树→嵌套dict→YAML |
| 4 | 蓝图§0.1+frontmatter | ①扫描所有蓝图→②提取actual_disk_path+§0.1文件列表→③构建完整路径→④检测同路径多蓝图冲突 | path_ownership_map.yaml | Markdown→dict→YAML | 表格行→路径条目→YAML |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| empty | scaffold创建模块 | registered | --domain参数非空+无重叠 |
| registered | 功能域变更 | updated | 变更通过SSoT门禁 |
| registered | 模块废弃 | deprecated | 无其他模块依赖此功能域 |

---

## §4 接口契约

### 4.1 公共 API

```python
class FunctionalDomainRegistry:
    """功能域注册表管理——加载/查询/重叠检测/注册"""

    def __init__(self, registry_path: Path | str | None = None):
        """初始化，指定注册表路径(默认PROJECT_ROOT/REGISTRY_PATH)"""

    def load(self) -> None:
        """加载功能域注册表YAML(幂等，已加载则跳过)"""

    def query_domain(self, domain: str, subdomain: str | None = None) -> list[DomainEntry]:
        """查询指定功能域下的所有条目，可按subdomain过滤"""

    def check_overlap(self, domain: str, subdomain: str, covers: list[str] | None = None, name: str = "", description: str = "") -> OverlapResult:
        """检测功能域重叠——创建前调用，支持精确匹配+covers交集+别名匹配"""

    def register(self, domain: str, subdomain: str, ssot_module: str, ssot_path: str, covers: list[str] | None = None, aliases: list[str] | None = None, stability: str = "evolving", ai_autonomy: str = "human_gated") -> None:
        """注册新条目到功能域注册表(重叠时抛ValueError)"""

    def list_domains(self) -> list[str]:
        """列出所有功能域(去重排序)"""

    def list_subdomains(self, domain: str) -> list[str]:
        """列出指定功能域下所有子域(排序)"""

    @property
    def entry_count(self) -> int:
        """当前注册表条目数"""
```

| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `__init__()` | ①接收registry_path→②None则用默认路径→③初始化_entries=[]和_loaded=False | — |
| `load()` | ①检查_loaded→②读取YAML→③解析entries列表→④构建DomainEntry→⑤标记_loaded=True | YAML不存在→WARNING+空列表；解析异常→ERROR+空列表 |
| `query_domain()` | ①load()→②按domain匹配→③subdomain非空则再过滤→④返回条目列表 | domain不存在→返回空列表 |
| `check_overlap()` | ①load()→②精确匹配(domain+subdomain)→③covers交集检测→④别名匹配(name/description)→⑤构建OverlapResult | 任何匹配→has_overlap=True |
| `register()` | ①load()→②check_overlap()→③有重叠→抛ValueError→④无重叠→构建DomainEntry→⑤追加→⑥_write_registry()原子写入 | 有重叠→ValueError阻断 |
| `list_domains()` | ①load()→②去重+排序→③返回域名列表 | — |
| `list_subdomains()` | ①load()→②按domain过滤→③排序→④返回子域列表 | — |
| `entry_count` | ①load()→②返回len(_entries) | — |

### 4.2 数据模型

```python
from dataclasses import dataclass, field

@dataclass
class DomainEntry:
    domain: str
    subdomain: str
    ssot_module: str
    ssot_path: str
    covers: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    stability: str = "evolving"
    ai_autonomy: str = "human_gated"

@dataclass
class OverlapResult:
    has_overlap: bool = False
    overlapping_entries: list[DomainEntry] = field(default_factory=list)
    overlap_details: list[str] = field(default_factory=list)
```

| 模型名 | SSoT文件 | 其他定义位置 | 状态 |
|--------|---------|------------|------|
| DomainEntry | registry_governance.py | — | ✅ 唯一源 |
| OverlapResult | registry_governance.py | — | ✅ 唯一源 |
| CheckResult | — | — | ⚠️ 待实现(代码中不存在) |

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `__init__()` | `registry_path` | ❌ | Path/str/None，None则用默认路径 |
| `load()` | — | — | 无参数，路径由__init__指定 |
| `query_domain()` | `domain` | ✅ | 非空字符串 |
| `query_domain()` | `subdomain` | ❌ | 字符串，非空则按子域过滤 |
| `check_overlap()` | `domain` | ✅ | 非空字符串 |
| `check_overlap()` | `subdomain` | ✅ | 非空字符串 |
| `check_overlap()` | `covers` | ❌ | list[str]，功能覆盖列表 |
| `check_overlap()` | `name` | ❌ | 字符串，用于别名匹配 |
| `check_overlap()` | `description` | ❌ | 字符串，用于别名匹配 |
| `register()` | `domain` | ✅ | 非空字符串 |
| `register()` | `subdomain` | ✅ | 非空字符串 |
| `register()` | `ssot_module` | ✅ | 模块ID，如MOD-INF-037 |
| `register()` | `ssot_path` | ✅ | 真源路径 |
| `register()` | `covers` | ❌ | list[str]，默认[] |
| `register()` | `aliases` | ❌ | list[str]，默认[] |
| `register()` | `stability` | ❌ | frozen/stable/evolving/volatile，默认evolving |
| `register()` | `ai_autonomy` | ❌ | immutable_core/human_gated/ai_modifiable，默认human_gated |
| `list_domains()` | — | — | 无参数 |
| `list_subdomains()` | `domain` | ✅ | 非空字符串 |
| `entry_count` | — | — | 属性，无参数 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `__init__()` | FunctionalDomainRegistry实例 | — |
| `load()` | None(内部缓存_entries) | YAML不存在→WARNING+空列表；解析异常→ERROR+空列表 |
| `query_domain()` | `list[DomainEntry]`：空列表表示无匹配 | — |
| `check_overlap()` | `OverlapResult`：has_overlap=False表示无重叠 | — |
| `register()` | None：注册成功+原子写入YAML | `ValueError`：存在重叠，消息含重叠详情 |
| `list_domains()` | `list[str]`：去重排序的域名列表 | — |
| `list_subdomains()` | `list[str]`：排序的子域列表 | — |
| `entry_count` | `int`：当前条目数 | — |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增功能域 | ✅ 向后兼容 | 不影响已有条目 |
| 新增DomainEntry字段 | ✅ 向后兼容 | Optional字段 |
| 删除/重命名DomainEntry字段 | ❌ 破坏性 | 需Owner审批+迁移方案 |
| check_overlap返回值变更 | ❌ 破坏性 | scaffold.py依赖此接口 |

### 4.7 OCP 扩展点

本模块无 OCP 扩展点。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 功能域声明是强制的 | scaffold创建时必须指定--domain参数 |
| 2 | 功能域注册表格式 | YAML，遵循TPL-REGISTER-001模板 |
| 3 | 写入方式 | 原子写入(temp-file+os.replace) |
| 4 | 功能域分类体系 | 首批：governance/security/orchestration/resilience/observability/data/intelligence/infrastructure/testing/automation |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 功能域条目数 | 0 | 500 | 10000 | ✅ | YAML文件，无硬上限 |
| 注册表数量 | 43 | 60 | 无上限 | ✅ | registry_of_registries.yaml扩展 |

### 5.3 迁移/废弃方案

无迁移/废弃。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 功能域查询成功率 | 99.9% | 调用计数 | 查询成功/总查询 | 99.9% | ≤1次/月失败 | 连续3次失败 |
| 可维护性 | MTTR | <15min | 故障记录 | — | — | — | — |

### §5.5 自动化触发机制

| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| 功能域查重 | auto_event | scaffold创建时触发 | ⚠️待实现 |
| 注册表一致性校验 | auto_scheduled | CI pipeline | ⚠️待实现 |
| 功能域注册 | auto_event | scaffold创建成功后触发 | ⚠️待实现 |

### §5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | open(path, "w")直接写 | temp-file+os.replace()原子写入 | RULE-ONE |
| 2 | 导入源 | zephyr.l00_* | zephyr.infra_ops.* | 分层约束 |
| 3 | 编码模式 | for+subprocess串行 | ThreadPoolExecutor | RULE-SEVEN |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 功能域注册表YAML损坏 | YAML解析异常 | 读取备份+告警 | 功能域查重不可用 |
| 2 | 功能域注册表文件不存在 | FileNotFoundError | 自动创建空注册表 | 首次运行 |
| 3 | 注册表引用断裂 | 物理文件不存在 | 输出断裂清单 | 一致性报告 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| domain_overlap_detected | Counter | 自动埋点 | >0 | P2 |
| registry_broken_refs | Gauge | 校验脚本 | >0 | P2 |
| registry_consistency_check_duration | Histogram | 自动埋点 | >60s | P3 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| FunctionalDomainRegistry | — | 功能域查重+注册 | scaffold跳过查重(告警) | YAML文件恢复 |
| RegistryConsistencyChecker | — | 一致性校验 | 跳过校验(告警) | 依赖注册表恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | AI直接修改功能域注册表 | 数据完整性破坏 | [AI_AUTONOMY]=immutable_core，AI不可直接修改YAML | PermissionGuard检查 |
| 2 | 功能域注册表被误删 | 功能域查重失效 | 原子写入+备份机制 | 文件存在性检查 |
| 3 | 恶意功能域注册 | 功能域污染 | register()必须通过scaffold入口 | scaffold入口唯一 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | FunctionalDomainRegistry.load/query_domain/check_overlap/register | 空注册表/单条目/多条目/重叠检测/注册冲突 | 覆盖率≥90% |
| 2 | 单元测试 | RegistryConsistencyChecker | 断裂引用/过期条目/Schema漂移 | 覆盖率≥90% |
| 3 | 集成测试 | scaffold→SSoTGate→FunctionalDomainRegistry端到端 | 创建模块→功能域查重→注册→验证 | 端到端通过 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-005 | 必须 | scaffold.py创建入口+--domain参数注入 | ≥当前 | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` |
| MOD-INF-017 | 可选 | Token级去重结果作为功能域查重补充 | ≥当前 | `docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md` |
| MOD-INF-026 | 可选 | 资产盘点消费注册表数据 | ≥当前 | `docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在registry中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-037` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 未对齐 | 同上 |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| registry_governance.py | scaffold.py | FunctionalDomainRegistry类 | import检查 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| functional-domain-registry.yaml | scaffold.py | 功能域条目 | YAML文件读取 |
| registry_governance.py | check_registry_consistency.py | CheckResult | 函数调用 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 单文件模块，无复杂依赖 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | 防漂移 | CI门禁 | validate_path_alignment.py | 需新增MOD-INF-037条目 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 不适用 | 无临时内容 | — | — | — | — | — |

### 10.5 概念重叠声明

| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | 代码去重 | 语义级功能域去重 vs Token级代码去重 | MOD-INF-017 | 共存——功能域注册表做语义级，code_dedup做Token级 | 已处置 |
| 2 | 文件名冲突检测 | scaffold已有文件名冲突检测 | MOD-INF-005 | 本模块委托对方——文件名冲突由scaffold处理 | 已处置 |

### 10.6 依赖链风险评级

| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|---------|---------|---------|
| 1 | MOD-INF-037→MOD-INF-005 | 1 | L1 | 无需 | 不适用 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整路径（相对优先） | 职责 | consumer_min | 注册位置 |
|----------|---------------|------|:-----------:|---------|
| 蓝图文件 | `docs/03_modules/_domain_governance/registry_governance/blueprint.md` | 本文件 | ≥0 | blueprint_registry.yaml |
| 功能域注册表 | `docs/01_policies_and_standards/_registry/catalogs/functional-domain-registry.yaml` | 功能域条目数据 | ≥1 | registry_of_registries.yaml |
| 物理路径树快照 | `docs/01_policies_and_standards/_registry/catalogs/project-path-tree.yaml` | 磁盘目录树自动快照(REG-017) | ≥1 | registry_of_registries.yaml |
| 路径归属声明 | `docs/03_modules/path_ownership_map.yaml` | 蓝图→路径映射+冲突检测(REG-018) | ≥1 | registry_of_registries.yaml |
| 业务代码 | `src/zephyr/infrastructure/runtime_integration/registry_governance.py` | 功能域注册表管理+一致性校验 | ≥1 | `__init__.py` __all__ |
| 校验脚本 | `scripts/governance/d3_metadata/check_registry_consistency.py` | 注册表一致性校验CLI | ≥0 | script-manifest.yaml |
| 路径树生成脚本 | `scripts/governance/generate_project_path_tree.py` | 物理路径树快照生成 | ≥0 | script-manifest.yaml |
| 归属图生成脚本 | `scripts/governance/generators/generate_path_ownership_map.py` | 路径归属声明生成+冲突检测 | ≥0 | script-manifest.yaml |
| 路径树刷新门禁 | `src/zephyr/governance/rule_enforcement/g6-path-tree-freshness.yaml` | GOV-DOC-004 §四-A 强制门禁(G6_PT) | ≥0 | gate _registry.yaml |
| 测试代码 | `tests/infrastructure/test_registry_governance.py` | 测试用例 | ≥0 | pytest自动发现 |
| Frontmatter字段注册表 | `docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml` | 40个Frontmatter字段定义（REG-FRONTMATTER-001） | ≥1 | registry_of_registries.yaml |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| scaffold.py | 修改现有接口 | 新增--domain参数+SSoTGate调用 | `scaffold.py module test_pkg test_mod --domain governance` exit 0 |
| CI Pipeline | 新增校验步骤 | check_registry_consistency.py | CI exit 0 |
| registry_of_registries.yaml | 新增条目 | REG-FUNC-DOMAIN-001功能域注册表 | 条目存在且可查询 |

### 12.1 域契约锚点

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| MOD-GOVERNANCE | 治理域 | 功能域注册表是治理域的功能域声明SSoT | MOD-INF-005 | 修改功能域注册表Schema必须同步更新scaffold |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整路径（相对优先） | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块ID注册表 | `architecture_model/module_id_registry.yaml` | 新增MOD-INF-037 | 新模块注册 |
| 2 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | 新增registry-governance蓝图 | 蓝图注册 |
| 3 | 注册表总索引 | `docs/registry_of_registries.yaml` | 新增REG-FUNC-DOMAIN-001条目 | 功能域注册表注册 |
| 4 | scaffold.py | `scripts/scaffold.py` | 新增--domain参数+SSoTGate调用 | 门禁集成 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 功能域分类体系不完整导致频繁变更 | 中 | 中 | 首批10域+subdomain扩展，避免过度分类 | 风险 |
| 2 | 现有模块/脚本缺少功能域声明 | 高 | 低 | 渐进回填——新模块强制声明，旧模块按需补充 | 负面后果 |
| 3 | scaffold.py改动影响现有创建流程 | 低 | 高 | --domain参数可选(默认"unclassified")，向后兼容 | 风险 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 4 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3个Phase |
| 施工模式 | 新建 |
| 核心风险 | scaffold.py改动影响现有流程 |
| 目标 generation | 1 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | scaffold.py可正常运行 | hard | ✅ | ☐ |
| 2 | registry_of_registries.yaml可正常读取 | hard | ✅ | ☐ |
| 3 | TPL-REGISTER-001模板已理解 | soft | ✅ | ☐ |

### 16.3 实施步骤

#### 步骤 1：创建功能域注册表

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2 DomainEntry数据模型 |
| 产出位置 | `docs/01_policies_and_standards/_registry/catalogs/functional-domain-registry.yaml` |
| 验收标准 | YAML文件存在+Schema合规+可被FunctionalDomainRegistry.load()解析 |
| 验证命令 | `python -c "import yaml; yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/functional-domain-registry.yaml'))"` |
| G7 检查项 | 上游：TPL-REGISTER-001模板已读取；下游：scaffold.py可读取 |
| AI 自治范围 | ai_modifiable |
| 检查点 | YAML文件存在且非空 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整路径（相对优先） |
|-----------|--------|----------|------------|
| MOD-INF-037 | functional-domain-registry.yaml | register | `docs/01_policies_and_standards/_registry/catalogs/functional-domain-registry.yaml` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| functional-domain-registry.yaml | 功能域注册表初始数据 | 10个功能域分类(governance/security/orchestration/resilience/observability/data/intelligence/infrastructure/testing/automation)+Schema声明+条目schema定义 |

#### 步骤 2：编写registry_governance.py

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 FunctionalDomainRegistry类+RegistryConsistencyChecker类 |
| 产出位置 | `src/zephyr/infrastructure/runtime_integration/registry_governance.py` |
| 验收标准 | 所有公共API可调用+单元测试通过+十五字段头部完整 |
| 验证命令 | `python -m pytest tests/infrastructure/test_registry_governance.py -v` |
| G7 检查项 | 上游：functional-domain-registry.yaml已创建；下游：scaffold.py可import |
| AI 自治范围 | ai_modifiable |
| 检查点 | `python -c "from zephyr.infra_ops.registry_governance import FunctionalDomainRegistry"` exit 0 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整路径（相对优先） |
|-----------|--------|----------|------------|
| MOD-INF-037 | registry_governance.py | code | `src/zephyr/infrastructure/runtime_integration/registry_governance.py` |
| MOD-INF-037 | test_registry_governance.py | test | `tests/infrastructure/test_registry_governance.py` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| registry_governance.py | FunctionalDomainRegistry类(4方法)+RegistryConsistencyChecker类+DomainEntry/OverlapResult/CheckResult模型 | 十五字段头部+原子写入+ThreadPoolExecutor(校验时) |
| test_registry_governance.py | 单元测试+集成测试 | load/query_domain/check_overlap/register/consistency_check各至少2用例 |

#### 步骤 3：加固scaffold.py+编写校验脚本

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 SSoTGate + §3.1 RegistryConsistencyChecker |
| 产出位置 | `scripts/scaffold.py`(修改) + `scripts/governance/d3_metadata/check_registry_consistency.py`(新建) |
| 验收标准 | scaffold.py --domain参数可用+校验脚本exit 0/1/2 |
| 验证命令 | `python scripts/scaffold.py module test_pkg test_mod --domain governance` + `python scripts/governance/d3_metadata/check_registry_consistency.py --warn-only` |
| G7 检查项 | 上游：registry_governance.py已实现；下游：CI可调用校验脚本 |
| AI 自治范围 | human_gated(scaffold修改需Owner确认) |
| 检查点 | scaffold创建模块时功能域查重生效 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整路径（相对优先） |
|-----------|--------|----------|------------|
| MOD-INF-037 | check_registry_consistency.py | script | `scripts/governance/d3_metadata/check_registry_consistency.py` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| scaffold.py改动 | 新增--domain参数+import FunctionalDomainRegistry+check_overlap()调用 | 向后兼容(--domain默认unclassified) |
| check_registry_consistency.py | CLI入口+遍历registry_of_registries.yaml+调用RegistryConsistencyChecker | --warn-only模式+exit 0/1/2+ThreadPoolExecutor |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | YAML格式错误 | 删除functional-domain-registry.yaml重新创建 |
| 2 | import失败 | 删除registry_governance.py+test文件，恢复__init__.py |
| 3 | scaffold兼容性问题 | 移除--domain参数相关代码，恢复scaffold.py原状 |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | functional-domain-registry.yaml 存在 | `ls` exit 0 | 完成 | ☐ |
| 2 | registry_governance.py 存在且可import | `python -c "import ..."` exit 0 | 完成 | ☐ |
| 3 | 单元测试通过 | `pytest` exit 0 | 完成 | ☐ |
| 4 | scaffold --domain参数可用 | `scaffold.py --help` 包含--domain | 完成 | ☐ |
| 5 | 校验脚本可用 | `--warn-only` exit 0 | 完成 | ☐ |
| 6 | 集成测试通过 | scaffold端到端测试 | 就绪 | ☐ |
| 7 | §13 需要更新的文件全部更新 | 逐文件核对 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | — |
| verification_status | unverified | — |
| code_alignment_verified | no | — |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 功能域重叠检测算法 | 算法 | ①按domain键查找→②过滤exclude_id→③计算重叠度=len(overlapping_entries)→④>0则has_overlap=True | registry_governance.py |
| 2 | 注册表一致性校验流程 | 协议 | ①读取registry_of_registries.yaml→②遍历每个注册表→③检查物理文件存在→④检查条目Schema合规→⑤汇总CheckResult | check_registry_consistency.py |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python scripts/governance/d3_metadata/check_registry_consistency.py` | 注册表一致性校验 | `--warn-only`: 仅告警不阻断 | exit 0=CLEAN / 1=WARNING / 2=ERROR |
| 2 | 命令 | `python scripts/scaffold.py module <pkg> <name> --domain <domain>` | 创建模块+功能域注册 | `--domain`: 功能域(默认unclassified) | exit 0=成功 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | registry_governance.py import失败 | 依赖缺失 | `pip install pydantic` | 安装依赖 | 重新import |
| 2 | 运行 | 功能域注册表YAML损坏 | 手动编辑错误 | 从git恢复或重新创建 | 恢复注册表 | `load()` exit 0 |
| 3 | 运行 | scaffold --domain查重报错 | 功能域注册表不可读 | 检查文件权限+路径 | 修复权限 | scaffold exit 0 |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 多AI同时注册同一功能域 | 文件锁(RULE-ZERO) | 后写者等待锁释放 | FIFO |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 功能域条目数 | 0 | `grep -c "entry_id" functional-domain-registry.yaml` |
| 注册表数量 | 43 | `grep -c "registry_id" registry_of_registries.yaml` |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-001 | 功能域注册表不存在 | 创建functional-domain-registry.yaml | P1 | 立即 | v0.1.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.1.0 | 1 | 基线 | 功能域注册表+SSoT门禁+一致性校验 | ❌ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| FunctionalDomainRegistry | GAP-001 | registry_governance.py | Phase 1 | 待施工 |
| SSoTGate | GAP-001 | scaffold.py(修改) | Phase 3 | 待施工 |
| RegistryConsistencyChecker | GAP-001 | check_registry_consistency.py | Phase 3 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-INF037-01 | 功能域注册表存储格式 | A.YAML文件 / B.SQLite / B.JSON | A | 与现有43个注册表格式一致，无额外依赖 | 2026-05-16 |
| 2 | D-INF037-02 | --domain参数兼容策略 | A.强制必填 / B.可选默认unclassified | B | 向后兼容，避免scaffold现有流程中断 | 2026-05-16 |
| 3 | D-INF037-03 | 功能域分类粒度 | A.仅一级6域 / B.两级(域+子域) / C.自由标签 | B | 一级太粗无法精确查重，自由标签太散无法聚合 | 2026-05-16 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| 功能域注册表 | 记录模块/脚本功能域声明的YAML注册表 | 注册表总索引(registry_of_registries.yaml) | 功能域注册表记录每个条目的功能域；总索引记录所有注册表的位置 |
| SSoT门禁 | scaffold创建时检查功能域重叠的门禁逻辑 | Gate门禁(GATE-*) | SSoT门禁是功能域级别的语义查重；Gate门禁是CI级别的规则检查 |
| 功能域 | 模块/脚本所属的功能分类(governance/intelligence等) | 业务域 | 功能域是技术分类；业务域是业务分类 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 现有模块/脚本无功能域声明 | 中 | 功能域注册表之前不存在 | 渐进回填 | §5.1 #1 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ☐ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ☐ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ☐ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 中 | 每步施工后执行验证命令 | exit 0才进下一步 | ☐ |
| 9 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 10 | 后 | §0 代码对齐验证已更新 | construction_progress与实际一致 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | evolving | 中 | 功能域分类体系稳定后→stable | 首批10域可能需要调整 |
| 接口契约 | evolving | 中 | scaffold集成验证后→stable | --domain参数可能调整 |
| 数据模型 | stable | 高 | DomainEntry字段稳定 | Pydantic V2模型 |
| 施工步骤 | evolving | 中 | 步骤1完成后→stable | 首次施工 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 功能域注册表+SSoT门禁+一致性校验 | — | 待施工 |
| v0.2.0 | 现有模块功能域回填+功能域分类体系优化 | v0.1.0 | 待施工 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | 所有路径必须完整可定位 | Python非法转义序列 | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI零记忆 | 缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | — | 噪音淹没关键信息 |
| 4 | 产出物路径必须与GOV-DOC-002一致 | AI不知道目录规范 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | AI不知道边界 | 范围漂移 |
| 6 | "待定"/"建议"/"按需"等模糊词禁止使用 | AI无法处理模糊指令 | 执行漂移 |
| 7 | 蓝图必须自包含 | AI可能不读引用文件 | 信息缺失 |
| 8 | 删除文件必须遵守安全删除协议 | 删除不可逆 | 永久丢失 |
| 9 | construction_progress必须与代码实际状态一致 | — | 重复造轮子 |
| 10 | actual_disk_path必须与§11产出物路径一致 | — | 搜索失败 |
| 11 | 已实现代码不在蓝图中重复 | 双源漂移 | AI改蓝图忘改代码 |
| 12 | 临时时态内容执行完毕后从蓝图删除 | 蓝图膨胀 | 关键信息被噪音淹没 |
| 13 | 蓝图内容拆分判定 | — | 跨模块影响无法追踪 |
| 14 | 术语表不可省略 | 术语理解漂移 | 设计与意图不一致 |
| 15 | 参考实现规格vs已实现代码重复 | 删规格→AI编造 | 关键逻辑实现错误 |
| 16 | 对标验证表格vs对标散文 | 表格=验证基准 | 丢表格→无法验证 |

---

## 蓝图拆分判定标准

| 判定条件 | 结果 | 操作 |
|---------|------|------|
| 服务对象相同+变更频率同步+依赖关系重叠 | 原地升级 | 在§17容量升级附录中增量记录 |
| 有独立module_id前缀 | 拆分 | 创建子蓝图，belongs_to=本蓝图 |
| 有独立Phase路线图和交付节奏 | 拆分 | 同上 |
| 有独立依赖关系图(与主体depends_on交集<50%) | 拆分 | 同上 |
| 内容超100行且与主体无直接数据流 | 拆分 | 同上 |
| 拆分后 | MUST验证 | 子蓝图有独立frontmatter+概述+§0~§18；本蓝图§10新增引用；blueprint_registry.yaml同步更新 |

---

## ⚠️ 安全删除协议

### 蓝图中的删除决策清单

本蓝图不涉及文件废弃/迁移/删除。

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在stable搬入阶段执行 | deprecated至少保持1个Phase |
| 4 | 物理删除必须人类确认 | AI不得自行决定删除文件 |
| 5 | "宁可慢，不可漏" | 没有git备份，删了就没了 |

---

## 必备链接

| # | 文件 | module_id | 完整路径（相对优先） | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 模块ID注册表 | — | `architecture_model/module_id_registry.yaml` | 编号注册 |
| 4 | AI自治权限注册表 | GOV-AI-001 | `docs/01_policies_and_standards/_registry/catalogs/ai_autonomy_authority_registry.yaml` | AI操作权限 |
| 5 | 注册表总索引 | — | `docs/registry_of_registries.yaml` | 43个注册表主索引 |
| 6 | 注册表模板 | TPL-REGISTER-001 | `docs/01_policies_and_standards/templates/register-registry.md` | 功能域注册表Schema |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整路径（相对优先） | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | code_dedup_engine | `src/zephyr/infra_ops/code_dedup_engine/` | 去重 | Token级去重，非语义级功能域查重 |
| 2 | scaffold.py | `scripts/scaffold.py` | 文件名冲突检测 | 仅文件名级，无功能域语义 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整路径（相对优先） | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 功能域注册表 | `docs/01_policies_and_standards/_registry/catalogs/functional-domain-registry.yaml` | 新建 | 创建YAML注册表 |
| 2 | 业务代码 | `src/zephyr/infrastructure/runtime_integration/registry_governance.py` | 新建 | 创建Python模块 |
| 3 | 测试代码 | `tests/infrastructure/test_registry_governance.py` | 新建 | 创建测试文件 |
| 4 | 校验脚本 | `scripts/governance/d3_metadata/check_registry_consistency.py` | 新建 | 创建CLI脚本 |
| 5 | scaffold.py | `scripts/scaffold.py` | 修改 | 新增--domain参数+SSoTGate调用 |
| 6 | 注册表总索引 | `docs/registry_of_registries.yaml` | 修改 | 新增REG-FUNC-DOMAIN-001条目 |
| 7 | 模块ID注册表 | `architecture_model/module_id_registry.yaml` | 修改 | 新增MOD-INF-037 |
| 8 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | 修改 | 新增registry-governance蓝图条目 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 | 漂移风险 |
|------|------|--------|---------|
| 功能域注册表数据 | **functional-domain-registry.yaml** | — | 无 |
| 功能域查重逻辑 | **registry_governance.py** | — | 无 |
| 注册表一致性校验规则 | **registry_governance.py** | — | 无 |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml(派生) | 无 |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 2 | `scripts/scaffold.py` | §12 集成点 |
| Tier 3 | `src/zephyr/infrastructure/runtime_integration/registry_governance.py` | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| 接口契约新增/修改(§4) | 需Owner审批+通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改(§2) | 需Owner审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress变更 | 需§0对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充 | AI可自主修改 | — | — |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-16 | 0.1.0 | 初始版本 |
| 2026-05-16 | 0.2.0 | P0/P1修复：[BLUEPRINT]头部修正、API对齐、功能域10域、scaffold集成 |


## Consumers
- zephyr.registry_governance (internal)
