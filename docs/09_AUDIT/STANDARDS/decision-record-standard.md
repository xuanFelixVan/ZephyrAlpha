---
module_id: DECISION_RECORD_STANDARD
version: 1.1.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-16
owner: 首席文档架构师
responsibility:
  - 5 类决策记录（DR-TRADE/DR-STRATEGY/DR-RISK/DR-ARCH/DR-MODEL）的标准格式与存档规则
layer: layer_09
standard_type: 专业量化机构标准
applicable_scope: 全系统所有决策记录
compliance_level: 专业标准
parent_document: ../INDEX.md
tags: ["决策记录", "ADR", "治理标准"]
---

# 决策记录标准（Decision Record Standard）

> **范围**：ZephyrAlpha 系统中所有需要记录的决策，涵盖交易、策略、风险、架构、模型五大类。
> **真源**：本文件是决策记录格式与流程的唯一真源。
> **关联**：技术架构决策（ADR-001~）以 `docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md` 为真源，本标准定义其格式规范。

---

## 1. 决策记录体系概述

### 1.1 为什么需要决策记录

量化交易系统的复杂性要求所有关键决策都有可追溯的记录，以便：
- 新成员（包括 AI 模型）快速理解系统设计背景
- 避免因遗忘原因而重复踩坑
- 审计时提供决策依据
- 支持系统迭代演进时的冲突裁决

### 1.2 适用范围

以下情况**必须**创建决策记录：
- 影响多个模块的架构选择（技术栈、框架、协议）
- 交易策略的关键参数或方法论确定
- 风险限额或风控规则的变更
- 数据源或数据处理方式的重大变更
- AI 模型选型或提示工程方法论

### 1.3 5 类决策记录

| 类型 | 前缀 | 适用场景 | 示例 ID |
|------|------|---------|---------|
| **交易决策** | DR-TRADE | 交易规则、下单逻辑、执行策略 | DR-TRADE-20260416-001 |
| **策略决策** | DR-STRATEGY | Alpha 策略、因子选择、回测结论 | DR-STRATEGY-20260416-001 |
| **风险决策** | DR-RISK | 风控限额、止损规则、VaR 参数 | DR-RISK-20260416-001 |
| **架构决策** | DR-ARCH | 技术栈、模块边界、API 契约 | DR-ARCH-20260416-001 |
| **模型决策** | DR-MODEL | ML 模型选型、特征工程方法、评估指标 | DR-MODEL-20260416-001 |

---

## 2. 决策记录命名规范

### 2.1 文件命名格式

```
DR-{TYPE}-{YYYYMMDD}-{NNN}.md
```

- `TYPE`：TRADE / STRATEGY / RISK / ARCH / MODEL
- `YYYYMMDD`：决策日期
- `NNN`：当日序号（三位数，从 001 起）

**示例**：
- `DR-ARCH-20260416-001.md`（选择 structlog 日志框架）
- `DR-TRADE-20260416-001.md`（确定 QMT 下单接口）

### 2.2 存放位置

所有决策记录文件统一存放于：

```
docs/09_AUDIT/STATE/DECISION_RECORDS/
```

技术架构决策（ADR 系列）的摘要同步维护在：

```
docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md
```

---

## 3. 决策记录 Frontmatter 模板

```yaml
---
module_id: DR-{TYPE}-{YYYYMMDD}-{NNN}
version: 1.0.0
status: Active        # Active | Superseded | Deprecated
created_date: YYYY-MM-DD
last_updated: YYYY-MM-DD
owner: ZephyrAlpha-Owner
decision_type: DR-ARCH  # DR-TRADE | DR-STRATEGY | DR-RISK | DR-ARCH | DR-MODEL
priority: P0            # P0 | P1 | P2
tags: ["架构决策", "技术栈"]
supersedes: ""          # 若替代旧决策，填写旧 DR ID
superseded_by: ""       # 若已被新决策替代，填写新 DR ID
related_layers: [L00, L01]
---
```

---

## 4. 决策记录正文模板

```markdown
# DR-{TYPE}-{YYYYMMDD}-{NNN}: {决策标题}

## 状态
{Active | Superseded | Deprecated}

## 背景
{描述为什么需要做这个决策，当时面临什么问题或需求}

## 决策
{明确陈述做出了什么决策}

## 选项分析

| 选项 | 优点 | 缺点 |
|------|------|------|
| 选项 A | ... | ... |
| 选项 B | ... | ... |

## 最终选择
{选择了哪个选项，以及核心原因（1-3句话）}

## 影响
- 正面影响：...
- 负面影响 / 权衡：...
- 影响的模块/文件：...

## 验证标准
{如何验证这个决策是正确的}

## 参考资料
- {相关文档链接}
- {外部参考}
```

---

## 5. 优先级分级

| 级别 | 描述 | 示例 |
|------|------|------|
| **P0-必须** | 影响核心交易逻辑或多层架构的决策 | 交易执行框架选型 |
| **P1-应该** | 影响单层实现方式的决策 | 数据库连接池配置 |
| **P2-可以** | 影响局部实现细节的决策 | 日志格式偏好 |

---

## 6. 决策记录生命周期

### 6.1 状态流转

```
Draft → Active → Superseded / Deprecated
```

- **Active**：当前生效的决策
- **Superseded**：被更新的决策替代（须填写 `superseded_by` 字段）
- **Deprecated**：因系统变更而废弃，不再适用

### 6.2 变更流程

1. 确定需要更新/替代的旧决策（查询 `TECH_DECISION_RECORDS.md`）
2. 创建新决策记录文件
3. 在新决策的 `supersedes` 字段填写旧 DR ID
4. 将旧决策文件的 `status` 更新为 `Superseded`，填写 `superseded_by`
5. 更新 `TECH_DECISION_RECORDS.md` 摘要表

---

## 7. ADR（架构决策记录）专项规范

技术架构决策（ADR 系列）是 DR-ARCH 的特殊子集，存放在：

```
docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md
```

当前已决策的 ADR（截至 2026-04-16）：

| ADR ID | 主题 | 状态 |
|--------|------|------|
| ADR-001 | 使用 structlog 而非 logging | Accepted |
| ADR-002 | 使用 tenacity 进行 API 重试 | Accepted |
| ADR-003 | 使用 Pydantic v2 进行数据验证 | Accepted |
| ADR-004 | 使用 ZephyrBaseError 异常层次 | Accepted |
| ADR-005 | 数据存储使用 DuckDB + Parquet | Under Review |

待决策 ADR（Phase 2 施工图阶段前置依赖）：

| ADR ID | 主题 | 阻塞层 |
|--------|------|--------|
| ADR-006 | ML 框架选型 | L04、L05 |
| ADR-007 | 回测框架选型 | L05、L07 |
| ADR-008 | LLM API 选型 | Cross-Layer |
| ADR-009 | 消息队列选型 | L06 |

---

## 8. 决策记录查询

```powershell
# 查询所有 Active 的架构决策
Select-String -Path "docs/09_AUDIT/STATE/DECISION_RECORDS/DR-ARCH-*.md" -Pattern "status: Active"

# 查询影响 L04 的所有决策
Select-String -Path "docs/09_AUDIT/STATE/DECISION_RECORDS/*.md" -Pattern "L04"

# 查看 TECH_DECISION_RECORDS 摘要
Get-Content docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md
```

---

## 9. 与其他治理资产的关系

- `TECH_DECISION_RECORDS.md`：ADR 系列的速查摘要表（真源引用本文件格式）
- `MASTER_DEVELOPMENT_PLAN.md`：施工阶段决策（ADR-D1 系列）在此登记
- `lessons-learned-register.md`：因决策失误产生的教训在此记录
- `BLUEPRINT_DOMAIN_INVENTORY.yaml`：蓝图中引用的技术决策需在此注册

---

## 10. 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-04-07 | 初始版本 |
| v1.1.0 | 2026-04-16 | 重建（编码损坏恢复）；增加 ADR 待决策清单；补充生命周期流程图 |
