---
module_id: FOLDER_CHARTERS_INDEX
version: 1.0.0
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
responsibility:
- 管理所有一级目录的文件夹宪章
- 提供目录边界查询入口
- 监控目录容量和健康度
---

# 文件夹宪章总索引

> **用途**: 管理 `docs/` 下所有一级目录的边界定义和规范
> **更新频率**: 每季度审查，容量告警时即时更新

---

## 宪章清单（已完成5个，目标12个）

| 序号 | 目录 | 宪章文件 | 文件数 | 容量状态 | 负责人 | 审查周期 |
|------|------|----------|--------|----------|--------|----------|
| 1 | 01_FRAMEWORK | [01_FRAMEWORK_CHARTER](01_FRAMEWORK_CHARTER.md) | ~332 | 🟡 接近上限 | 首席架构师 | 季度 |
| 2 | 02_FACTOR_LIBRARY | [02_FACTOR_LIBRARY_CHARTER](02_FACTOR_LIBRARY_CHARTER.md) | ~175 | 🟢 正常 | 因子研究负责人 | 季度 |
| 3 | 05_IMPLEMENTATION | [05_IMPLEMENTATION_CHARTER](05_IMPLEMENTATION_CHARTER.md) | ~487 | 🟡 接近上限 | 实施负责人 | 月度 |
| 4 | 08_HUMAN_AI_INTERFACE | [08_HUMAN_AI_INTERFACE_CHARTER](08_HUMAN_AI_INTERFACE_CHARTER.md) | ~156 | 🟢 正常 | HCI负责人 | 季度 |
| 5 | 09_AUDIT | [09_AUDIT_CHARTER](09_AUDIT_CHARTER.md) | ~1172 | 🔴 严重超标 | 审计负责人 | **月度** |

**待创建宪章**（按优先级）：

| 优先级 | 目录 | 预计文件数 | 创建计划 |
|--------|------|------------|----------|
| P1 | 00_OVERVIEW | ~4 | Week 2 |
| P1 | 03_TRADING_TACTICS | ~64 | Week 2 |
| P1 | 04_EXECUTION | ~40 | Week 2 |
| P2 | 07_AI_REPORTING | ~52 | Week 3 |
| P2 | 10_GOVERNANCE_COMPLIANCE | ~63 | Week 3 |
| P2 | 11_STRATEGIC_DECISION | ~24 | Week 3 |

---

## 容量监控仪表盘

```
总文件数分布（一级目录）:
01_FRAMEWORK        ████████████████████░░░░░ 332/400  🟡
02_FACTOR_LIBRARY   █████████░░░░░░░░░░░░░░░░ 175/300  🟢
03_TRADING_TACTICS  ███████░░░░░░░░░░░░░░░░░░  64/200  🟢
04_EXECUTION        █████░░░░░░░░░░░░░░░░░░░░  40/200  🟢
05_IMPLEMENTATION   ███████████████████████░░ 487/500  🟡
07_AI_REPORTING     ██████████░░░░░░░░░░░░░░░  52/200  🟢
08_HUMAN_AI_INTF    ██████████████████░░░░░ 156/250  🟢
09_AUDIT            ████████████████████████████████████████████████████████ 1172/300 🔴超标
10_GOV_COMPLIANCE   ███████████░░░░░░░░░░░░░░  63/200  🟢
11_STRATEGIC_DEC    ████░░░░░░░░░░░░░░░░░░░░░  24/100  🟢
```

---

## 快速查询

### 按容量状态查询

**🔴 严重超标（需立即清理）**
- `09_AUDIT/` (~1172个文件，目标<300)

**🟡 接近上限（需监控）**
- `01_FRAMEWORK/` (~332/400)
- `05_IMPLEMENTATION/` (~487/500)

**🟢 正常**
- 其余目录

### 按审查周期查询

**月度审查（高变动目录）**
- `09_AUDIT/`（治理核心，文件变动大）
- `05_IMPLEMENTATION/`（施工活跃）

**季度审查（稳定目录）**
- `01_FRAMEWORK/`（架构设计，变动较少）
- `02_FACTOR_LIBRARY/`（业务核心，稳定扩展）
- `08_HUMAN_AI_INTERFACE/`（HCI设计，稳定扩展）

---

## 宪章模板与工具

- [文件夹宪章模板](../STANDARDS/folder-charter-template.md) - 创建新宪章的模板
- [subsystem-registry.yaml](../../subsystem-registry.yaml) - 子系统注册表（关联查询）
- [目录编号重设计划](../../11_STRATEGIC_DECISION/directory-numbering-redesign-plan.md) - 编号体系规划

---

## 变更历史

| 版本 | 日期 | 变更 | 变更人 |
|------|------|------|--------|
| v1.0.0 | 2026-04-16 | 初始创建，完成前5个宪章 | AI Assistant |
