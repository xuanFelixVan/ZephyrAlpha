---
module_id: DOC_NAMING_STANDARD_8197
version: 2.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-16
owner: 首席文档架构师
responsibility:
  - 全库文档命名规范（含原 file-naming-standard 并入内容）
layer: layer_09
standard_type: 专业量化机构标准
applicable_scope: 全系统所有 .md 文件及代码文件
compliance_level: 专业标准
parent_document: ../INDEX.md
tags: ["命名规范", "文档治理", "合规标准"]
---

# 文档命名标准（Doc Naming Standard）

> **范围**：全库所有 Markdown 文档、Python 脚本、YAML 配置文件的命名规则。
> **真源**：本文件是命名规范的唯一真源；原 `file-naming-standard.md` 内容已并入本文件。
> **执行**：`scripts/hooks/doc_guard_pre_commit.py --check-naming` 在提交时自动校验。

---

## 1. 合规目标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 命名规范符合率 | ≥95% | 符合规范文件数 / 总文件数 |
| 中文命名率 | 0% | 中文命名文件数 / 总文件数 |
| 空格命名率 | 0% | 含空格文件名数 / 总文件数 |
| 命名格式一致性 | ≥90% | 格式一致文件数 / 总文件数 |

---

## 2. 四大核心原则

| 原则 | 说明 |
|------|------|
| **清晰性** | 文件名应清晰反映文件内容 |
| **一致性** | 同类文件使用统一的命名格式 |
| **简洁性** | 文件名应简洁，避免超过 50 个字符（docs/）或 100 个字符（scripts/） |
| **可读性** | 使用大写字母+下划线（文档）或小写字母+下划线（代码） |

### 2.1 通用禁止项

| 禁止项 | 原因 |
|--------|------|
| 中文字符 | 跨平台兼容性问题、命令行操作困难 |
| 空格 | 命令行操作困难、URL 编码问题 |
| 特殊字符（`@#$%&`等） | 系统兼容性问题 |
| 纯通用名（`DOC.md`、`README_NEW.md`、`OLD.md`） | 无法反映内容，造成歧义 |

---

## 3. Markdown 文档命名规范

### 3.1 单轨标准：全小写 kebab-case（自 2026-04-16 起）

```
^[a-z0-9][a-z0-9_-]*\.md$
```

**所有新建 `.md` 文件必须使用全小写 + 连字符（kebab-case）或下划线（snake_case）。**

```
✅ 合法
  doc-naming-standard.md
  construction-plan-l01-data-processing.md
  governance-asset-inventory.yaml
  KE-011-data-layer-design.md        ← 知识条目专属格式
  DR-ARCH-20260416-001.md            ← 决策记录专属格式
  session-20260416-010.md            ← Session log 专属格式

❌ 阻断（新建文件）
  DataSourcePlan.md                  ← 含大写（新建时阻断）
  construction plan v2.md            ← 含空格+版本号
  策略引擎.md                         ← 含中文
```

> **工具执行**：`scripts/hooks/doc_guard_pre_commit.py --check-naming`
> 中文 / 空格 / 特殊字符 / 版本号后缀 / 新建大写文件 → **硬阻断**
> 历史遗留大写文件（git 已追踪）→ **警告不阻断**，在 Pipeline A 波次中逐步迁移

### 3.2 永久固定名称（不受命名规则约束）

| 名称 | 用途 |
|------|------|
| `INDEX.md` | 目录索引（每个目录主索引） |
| `README.md` | 模块说明 |
| `CHANGELOG.md` | 版本变更记录 |
| `AGENTS.md` | 跨工具 AI 治理约束（仓库根） |
| `LICENSE` | 开源许可证 |
| `SITEMAP.md` | 仓库全局导航 |
| `CONTRIBUTING.md` | 贡献指南 |
| `SECURITY.md` | 安全政策 |

### 3.3 专属命名模式（特定类型文件的固定格式）

| 类型 | 格式 | 示例 |
|------|------|------|
| 知识条目 | `KE-{NNN}-{kebab-slug}.md` | `KE-011-data-layer-design.md` |
| 决策记录 | `DR-{TYPE}-{YYYYMMDD}-{NNN}.md` | `DR-ARCH-20260416-001.md` |
| Session Log | `session-{YYYYMMDD}-{suffix}.md` | `session-20260416-010.md` |

### 3.4 文档类型后缀（小写，供命名参考）

| 文档类型 | 推荐后缀 | 示例 |
|---------|---------|------|
| 蓝图设计 | `-blueprint.md` | `strategy-engine-blueprint.md` |
| 技术规格 | `-technical-spec.md` | `scenario-analyzer-technical-spec.md` |
| 施工图 | `construction-plan-{layer}-{name}.md` | `construction-plan-l01-data-processing.md` |
| 使用指南 | `-usage-guide.md` | `factor-library-usage-guide.md` |
| API 文档 | `-api-reference.md` | `factor-engine-api-reference.md` |
| 标准规范 | `-standard.md` | `doc-naming-standard.md` |
| 审计报告 | `-audit-report-{YYYYMMDD}.md` | `deep-audit-report-20260407.md` |
| Playbook | `-playbook.md` | `construction-change-impact-playbook.md` |

### 3.5 版本化/日期化文档

```
{module-name}-{doc-type}-v{版本号}.md     # 版本化（极少用）
{module-name}-{doc-type}-{YYYYMMDD}.md   # 日期化（报告类）
```

---

## 4. 施工图命名规范（Phase 2 专用）

施工图是 Phase 2 的核心产出物，**全部使用小写 kebab-case**：

```
construction-plan-{layer-code}-{layer-name}.md
```

| 文件名（新规范） | 对应层 | 备注 |
|----------------|--------|------|
| `CONSTRUCTION_PLAN_L00_DATA_SOURCE.md` | L00 数据基础设施 | 历史文件，祖父条款保留 |
| `construction-plan-l01-data-processing.md` | L01 数据处理 | 待创建 |
| `construction-plan-l02-feature-engineering.md` | L02 特征工程 | 待创建 |
| `construction-plan-l03-signal-generation.md` | L03 信号生成 | 待创建 |
| `construction-plan-l04-risk-management.md` | L04 风险管理 | 待创建 |
| `construction-plan-l05-portfolio-construction.md` | L05 组合构建 | 待创建 |
| `construction-plan-l06-trade-execution.md` | L06 交易执行 | 待创建 |
| `construction-plan-l07-post-trade-analytics.md` | L07 交易后分析 | 待创建 |
| `construction-plan-shared.md` | Cross-Layer 共享 | 待创建 |

---

## 5. 知识条目命名规范（KE 编号）

```
KE-{NNN}-{kebab-case-slug}.md
```

- `NNN`：三位数序号，从 001 起，自增
- `slug`：小写字母+连字符，反映主题

**示例**：
- `KE-001-ai-memory-architecture-comparison.md`
- `KE-011-data-layer-design-decision.md`

**KE 编号分配规则**：每次 session 开始前执行：
```powershell
Get-ChildItem -Path docs/08_KNOWLEDGE -Recurse -Filter "KE-*.md" | Sort-Object Name -Descending | Select-Object -First 1
```

---

## 6. Python/脚本文件命名规范

### 6.1 模块文件

```
{功能描述}.py  # 小写字母+下划线
```

**示例**：
- `factor_calculator.py`
- `risk_budget_system.py`
- `scan_index_health.py`

**禁止**：`FactorCalculator.py`（PascalCase）、`risk-budget.py`（连字符）

### 6.2 测试文件

```
test_{模块名称}.py
```

**示例**：`test_factor_calculator.py`、`test_risk_budget_system.py`

### 6.3 治理/审计脚本

```
{动词}_{名词}.py   # 例：scan_index_health.py, generate_blueprint_registry.py
```

---

## 7. YAML/JSON 配置文件命名规范

| 文件类型 | 命名规则 | 示例 |
|---------|---------|------|
| YAML 配置 | `{功能名称}.yaml` 或 `{功能名称}.yml` | `subsystem-registry.yaml` |
| JSON 状态文件 | `{功能名称}_{YYYYMMDD}.json` | `audit_state_20260416.json` |
| JSON 注册表 | `{注册表名}.json` | `module_id_registry.json` |

---

## 8. 命名校验工具

### 8.1 Pre-commit 自动校验

每次 `git commit` 时，`check-file-naming` hook 自动运行：

```bash
# 触发：所有 docs/ 下的 .md 文件提交时
python scripts/hooks/doc_guard_pre_commit.py --check-naming
```

### 8.2 手动扫描

```powershell
# 扫描全库命名合规情况
python scripts/hooks/doc_guard_pre_commit.py --check-naming --all
```

---

## 9. 违规分类与处置

| 违规类型 | 严重度 | 示例 | 处置 |
|---------|--------|------|------|
| 中文命名 | 🔴 高 | `策略引擎蓝图.md` → `STRATEGY_ENGINE_BLUEPRINT.md` | 立即重命名 |
| 空格命名 | 🟡 中 | `Strategy Engine.md` → `STRATEGY_ENGINE_BLUEPRINT.md` | 立即重命名 |
| 特殊字符 | 🟡 中 | `risk@system.md` → `RISK_SYSTEM_BLUEPRINT.md` | 立即重命名 |
| 过长命名（>50字符） | 🟡 中 | 缩写核心词 | 尽快修复 |
| 格式不一致 | 🟢 低 | `risk_budget_blueprint.md`（小写）→ 大写 | 计划修复 |

---

## 10. 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-04-07 | 初始版本 |
| v1.1.0 | 2026-04-16 | 重建（编码损坏恢复）；增加施工图命名规范；合并原 file-naming-standard |
| v1.2.0 | 2026-04-16 | 从单轨（大写）升级为双轨命名体系（轨道A小写/轨道B大写）；修复 check-file-naming hook 与标准矛盾；修复 hook 文件名接收 bug |
| v2.0.0 | 2026-04-16 | 彻底统一为单轨小写标准；废除双轨体系；施工图命名改为 construction-plan-*.md；历史遗留大写文件通过 git 祖父条款自动豁免 |

---

## 附录：文件命名标准（原 file-naming-standard，已并入）

### 📋 规范概要

**规范版本**: v1.0.0
**适用范围**: 全系统所有文件（包括文档和代码）
**规范目标**: 确保文件命名清晰、一致、无歧义
**规范性质**: 强制性标准

### 🎯 命名基本原则

#### 四大核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **清晰性** | 文件名应清晰反映文件内容 | `FACTOR_CALCULATION_FRAMEWORK.md` |
| **一致性** | 同类文件使用统一的命名格式 | 所有蓝图文件使用 `_BLUEPRINT.md` 后缀 |
| **简洁性** | 文件名应简洁明了，避免过长 | `RISK_BUDGET_SYSTEM.md` |
| **可读性** | 文件名应易于阅读和理解 | `PORTFOLIO_OPTIMIZATION.md` |

#### 禁止事项

| 禁止项 | 原因 | 示例 |
|--------|------|------|
| **中文命名** | 跨平台兼容性问题 | ❌ 风险预算系统.md |
| **空格** | 命令行操作困难 | ❌ Risk Budget System.md |
| **特殊字符** | 系统兼容性问题 | ❌ Risk@Budget#System.md |
| **过长命名** | 可读性差 | ❔ RISK_BUDGET_SYSTEM_PORTFOLIO_OPTIMIZATION_FRAMEWORK_V2.md |

### 📝 文档命名规范

#### Markdown 文档命名规范

**标准格式**：`[模块名称]_[文档类型].md`

**文档类型后缀**：

| 文档类型 | 后缀 | 示例 |
|---------|------|------|
| **标准规范** | `_STANDARD.md` | `FACTOR_CALCULATION_STANDARD.md` |
| **蓝图设计** | `_BLUEPRINT.md` | `RISK_BUDGET_SYSTEM_BLUEPRINT.md` |
| **实施指南** | `_GUIDE.md` | `DEPLOYMENT_GUIDE.md` |
| **操作手册** | `_MANUAL.md` | `OPERATION_MANUAL.md` |
| **分析报告** | `_REPORT.md` | `AUDIT_REPORT.md` |
| **测试文档** | `_TEST.md` | `UNIT_TEST.md` |
| **API文档** | `_API.md` | `FACTOR_ENGINE_API.md` |
| **配置文档** | `_CONFIG.md` | `SYSTEM_CONFIG.md` |

**特殊文档命名**：

| 文档名称 | 用途 |
|---------|------|
| **README.md** | 模块说明和快速入门 |
| **INDEX.md** | 目录索引和导航 |
| **ARCHITECTURE.md** | 架构设计文档 |
| **CHANGELOG.md** | 变更记录 |

#### 版本化文档命名

```
[模块名称]_[文档类型]_V[版本号].md
[模块名称]_[文档类型]_[YYYYMMDD].md
```

**示例**：
- `FACTOR_CALCULATION_STANDARD_V1.md`
- `AUDIT_REPORT_20260407.md`

### 💻 代码文件命名规范

#### Python 文件命名规范

**模块文件**：使用小写字母和下划线

```
factor_calculator.py     # 正确
risk_budget_system.py    # 正确
FactorCalculator.py      # 错误（PascalCase）
风险预算系统.py          # 错误（中文）
```

**测试文件**：`test_{模块名称}.py`

**工具脚本**：`{功能描述}_{工具类型}.py`

#### 配置文件命名规范

```
config.yaml / database.yml / logging.yaml    # YAML
package.json / tsconfig.json                 # JSON
```

### 🔍 命名检查机制

| 检查项 | 规则 | 严重程度 |
|--------|------|---------|
| **中文检查** | 文件名不得包含中文字符 | 🔴 高风险 |
| **空格检查** | 文件名不得包含空格 | 🟡 中风险 |
| **特殊字符检查** | 文件名不得包含特殊字符 | 🟡 中风险 |
| **长度检查** | 文件名长度不超过100字符 | 🟢 低风险 |
| **格式检查** | 文件名符合标准格式 | 🟡 中风险 |

### 📊 命名质量标准

| 等级 | 规范符合率 | 状态 | 行动 |
|------|-----------|------|------|
| **优秀** | ≥99% | ✅ | 保持现状 |
| **良好** | 95-99% | ✅ | 持续改进 |
| **合格** | 90-95% | ⚠️ | 立即改进 |
| **不合格** | <90% | ❌ | 紧急修复 |
