---
module_id: KE-agent_inst-8_2-006
title: 8.2 按任务类型选择规则（领域触发）
category: agent_instruction
---

# 8.2 按任务类型选择规则（领域触发）

8.2 按任务类型选择规则（领域触发）

> **全局强制**：以下所有任务类型，§6.12 AI受众优先原则**始终生效**（AI-First = 本项目头号宪法）。**任何涉及文件变更的任务完成后，MUST 执行 §5.2.2 十维审计清单。审计不是"以后再说"——不审不清，不清不继续。**

以下路径均为绝对路径，基于 `D:\ZephyrAlpha\docs\01_policies_and_standards\`：

| 你的任务 | 必须读的文件（只读这些） | Token 成本 | 禁止做的事 |
|---------|------------------------|:---:|---------|
| **首次入职 / 了解项目全貌** | `README.md` + `docs/02_enterprise_architecture/target-architecture/00-overview.md` + 本文件 §1~§5（项目根目录 → 架构概览 → AI 规则总纲）；若需了解治理体系 → `scripts/governance/QUICKSTART.md` | ~4500 | ❌ 禁止一上来就读本文件 §6~§7 全部 19 条施工原则——先知道"是什么"再知道"怎么干" / ❌ 禁止施工后跳过审计——不审不清，不清不继续 |
| **修改/优化任何规则文件** | `meta/index.md` + `meta/glossary.md` + `meta/rule-lifecycle-and-change-standard.md` | ~2000 | ❌ 禁止全量读取 meta/ 下 12 个文件 |
| **创建新标准文档** | `meta/index.md` + `meta/glossary.md` + `meta/document-structure-standard.md` + `meta/metadata-registry.md` §1~§4 | ~2500 | ❌ 禁止读 PS-STD-003 行为边界全文——仅按需查对应 ABS/COND 条目 |
| **修改代码** | `meta/glossary.md` + `src/zephyr/shared/contracts/`；若修改 `scripts/governance/` 脚本 → 加读 `scripts/governance/quality-standard.md` | ~1500 | ❌ 禁止读 meta/ 其他规则文件——代码已有 pre-commit/CI 强制 |
| **修改 config/ YAML 或审计配置** | `_registry/catalogs/declarative-contract-tracker.yaml`（必须先读） + `capabilities.yaml` + `scripts/governance/d1_structure/validate_config_integrity.py`（跑基线） | ~800 | ❌ 禁止信任 config/ 下所有 YAML 都是运行时配置 |
| **审查规则体系一致性** | `meta/index.md` + `meta/glossary.md` + `meta/rule-classification-and-arbitration-standard.md` + `meta/rule-verification-standard.md` + `_registry/catalogs/rule-registry.md` | ~3500 | ❌ 禁止读 PS-STD-002 模板文件——审查读的是内容不是格式 |
| **运行项目审计/扫描检查** | `scripts/governance/index.md` | ~600 | ❌ 禁止跳过审计直接施工——先跑 run_all.py 看当前状态 |
| **查找/操作任何登记表/注册表** | `_registry/catalogs/registry-master-index.yaml` | ~800 | ❌ 禁止跨目录翻找 YAML——先查总索引再定位到具体登记表 |
| **了解未兑现的 YAML 承诺** | `_registry/catalogs/declarative-contract-tracker.yaml`（契约跟踪登记表） | ~500 | ❌ 禁止信任有 implementation_status 的 YAML 全部兑现——先查契约跟踪表确认 |
| **创建/操作任务卡** | `blueprint_decomposer.py` + `docs/03_modules/l01_infrastructure/task-system/blueprint.md` | ~600 | ⚠️ **强制路径**：所有任务卡 MUST 通过 `decompose_blueprint()` 生成。禁止 AI 直接生成 `.md` 作为任务卡。唯一例外：MOD-INF-001（AI-GLM-5.1 直接产出，通过 `import_task_cards.py` 回填过一次） |
| **代码去重检查 / Monoculture 免疫**（MOD-INF-017） | `docs/03_modules/l01_infrastructure/code-dedup-engine/blueprint.md` + `src/zephyr/l01_infrastructure/code_dedup_engine/` | ~500 | ⚠️ 创建新代码前 MUST 先跑去重检查——RULE-EIGHT 强制。覆盖 65+ 模块：MinHash+LSH 扫描、BRS 单体文化评分、决策审计链、自我扫描。`pre-commit/verify_dedup.py` 自动触发 |
| **系统遥测 / 可观测性接入**（MOD-INF-015） | `docs/03_modules/l01_infrastructure/system-telemetry/blueprint.md` + `src/zephyr/l12_system_telemetry/` | ~400 | ⚠️ 新模块需要遥测接入时必读。9 子系统设计（metrics/logs/traces/ai_behavior/archive/profiles/health/alerts/schema）。注意：蓝图 v0.9.0 设计已完备但代码实现滞后（~8%），施工时以蓝图为准 |
| **创建新脚本工具** | `scripts/governance/index.md` + `scripts/governance/script_manifest.yaml` + **`_shared/` API 速查（见 §8.2.1）** | ~1000 | ❌ 禁止创建脚本后不注册——违反 §6.5 入库强制约定 / ❌ 禁止本地重定义 `_shared/` 已有函数/常量 |
| **创建新门禁/GATE/钩子** | `gate-registry.
