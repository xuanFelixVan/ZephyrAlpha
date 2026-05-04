---
module_id: EA-INDEX
doc_type: index
status: active
version: 2.1.0
generated: '2026-05-03'
depends_on:
  - {target: DOCS-INDEX, at: "§子目录", why: "根目录索引——02抽屉为根 docs/ 子目录，引用其抽屉一览"}
  - {target: AGENTS.md, at: "§6.9~§6.10", why: "双轨制+双层对齐 canonical 规则——本文件仅引用，不重复定义"}
---

# 02 Enterprise Architecture — 目录索引

> **架构设计状态**：本目录在架构设计阶段已提前搭建完整骨架——所有子目录、索引文件和结构边界均已在施工前就位，后续按需填充内容。

---

## 0. 双轨制 + 双层对齐（规则引用）

本目录遵循 AGENTS.md 定义的架构治理铁律，**不在此重复定义**：

| 规则 | Canonical SSoT | 本文角色 |
|------|---------------|---------|
| 双轨制（YAML 机器 SSoT + MD 人类视图） | [AGENTS.md §6.9](file:///D:/ZephyrAlpha/AGENTS.md) | 导航到对应位置 |
| 冲突裁决（YAML vs MD → 以 YAML 为准） | [AGENTS.md §6.9](file:///D:/ZephyrAlpha/AGENTS.md) | 同上 |
| 双层对齐闸门（GATE-A/B） | [AGENTS.md §6.10](file:///D:/ZephyrAlpha/AGENTS.md) | 同上 |
| AI 施工即时约束 | [AGENTS.md §6.10](file:///D:/ZephyrAlpha/AGENTS.md) | 同上 |

> **原则**：同一规则不在两处定义。AGENTS.md 是全局宪法，本索引只做导航——不重新声明、不复述、不独立维护副本。

---

## 责任声明（Single Responsibility）

本目录只存放：**企业架构文档 — TOGAF 视图（人类可读）+ ADR（决策记录）+ 架构模型 YAML（机器 SSoT）**。

## 子目录一览

| 子目录 | 说明 | 入口 | 轨道 |
|--------|------|------|:---:|
| `adr/` | 架构决策记录 | [adr/index.md](adr/index.md) | 人类视图 |
| `target-architecture/` | 目标架构视图（TOGAF 10 + 2 正交 + YAML SSoT + 图表） | [target-architecture/index.md](target-architecture/index.md) | 人 + 机 |

> `designs/` 和 `by-domain/` 目录已于 2026-05-03 物理删除（僵尸目录——索引已移除引用但物理目录未删，现已彻底清除）。

## 顶层文件清单

| 文件 | 说明 | 轨道 |
|------|------|:---:|
| architecture-rationale-log.md | 架构推导与决策链日志 | 人类视图 |
| ssot-authority-map.md | SSoT 权威映射 | 人类视图 |

## 排除规则（严禁放入本目录的内容）

- ❌ 治理规范/标准/协议 → `01_policies_and_standards/`
- ❌ 模块蓝图/施工图 → `03_modules/`
- ❌ 代码文件（`.py`、`.js`、`.ts` 等）→ `src/zephyr/` 或 `scripts/`
- ❌ 临时脚本、调试文件 → 要么走 AGENTS.md §6.5 入库，要么不存在
- ❌ 不属于"机器 SSoT"或"人类视图"的任何其他内容

## 父级目录

- 父级：[docs 根目录](file:///D:/ZephyrAlpha/docs/index.md)
