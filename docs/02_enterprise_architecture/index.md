---
module_id: GOV-036
doc_type: index
status: Active
version: 3.0.0
generated: '2026-06-30'
depends_on:
- target: DOCS-INDEX
  at: §子目录
  why: 根目录索引——02抽屉为根 docs/ 子目录，引用其抽屉一览
- target: AGENTS.md
  at: architecture_model/ YAML SSoT + GATE-A
  why: 双轨制+双层对齐 canonical 规则——本文件仅引用，不重复定义
title: 02 Enterprise Architecture
ttl: permanent
---

# 02 Enterprise Architecture — 目录索引

> **架构设计状态**：本目录在架构设计阶段已提前搭建完整骨架——所有子目录、索引文件和结构边界均已在施工前就位，后续按需填充内容。

---

## 0. YAML SSoT + 代码对齐（规则引用）

本目录遵循 AGENTS.md 定义的架构治理铁律，**不在此重复定义**：

| 规则 | Canonical SSoT | 本文角色 |
|------|---------------|---------|
| 双轨制（YAML 机器 SSoT + MD 人类视图） | architecture_model/ YAML SSoT | 导航到对应位置 |
| 冲突裁决（YAML vs MD → 以 YAML 为准） | YAML canonical SSoT 铁律 | 同上 |
| 代码对齐闸门（GATE-A） | GATE-A 代码↔YAML 对齐 | 同上 |
| AI 施工即时约束 | GATE-A 代码↔YAML 对齐 | 同上 |

> **原则**：同一规则不在两处定义。AGENTS.md 是全局宪法，本索引只做导航——不重新声明、不复述、不独立维护副本。

---

## 责任声明（Single Responsibility）

本目录只存放：**企业架构文档 — TOGAF 视图（人类可读）+ 架构模型 YAML（机器 SSoT）**。

## 子目录一览

| 子目录 | 说明 | 入口 | 轨道 |
|--------|------|------|:---:|

> `archive/` 目录已于 2026-06-23 物理删除（DM-200908）。历史文档价值已提取至 `project_memory.md` Lessons Learned。

> `designs/` 和 `by-domain/` 目录已于 2026-05-03 物理删除（僵尸目录——索引已移除引用但物理目录未删，现已彻底清除）。
>
> `adr/` 目录已于 2026-05 前全量迁入 `knowledge` 表（33 条 KB 决策记录，全部 VERIFIED），物理目录及配套文件（registry、template、protocol、adr_ingest.py）已删除。KB 决策记录 现通过 KE 管线检索，不再作为独立子目录存在。

## 顶层文件清单

| 文件 | 说明 | 轨道 |
|------|------|:---:|
| [→ rules/trae_081_audit_dimensions_framework.yaml](../01_policies_and_standards/rules/trae_081_audit_dimensions_framework.yaml) | 审计审查维度框架（54 维度基座，维度号+名+核心问题） | 规则 |
| _archive/architecture_debt_registry_v2.md | 已归档：架构债务注册表 v2.0.0（2026-07-24 归档，裁定#221/#222，活跃治理改由三件套承接） | 人类视图 |
| 04_architecture_principles_decisions/dependency_path_panorama.md | 依赖与路径全景图能力定位书（双态模型+SSoT分层+生命周期+生成器覆盖矩阵） | 人类视图 |
| _archive/architecture_decisions_pending.md | 已归档：决策清单（T6/T7/T17已裁定,T18暂缓） | 人类视图 |
| _archive/ssot_authority_map.md | 已归档：SSoT权威映射（权威角色已被专门YAML取代，validate_ssot.py不消费） | 人类视图 |
| _archive/t18_implementation_plan.md | 已归档：T18实施计划（暂缓，重启条件未满足） | 人类视图 |

## 排除规则（严禁放入本目录的内容）

- ❌ 治理规范/标准/协议 → `01_policies_and_standards/`
- ❌ 模块蓝图/施工图 → `03_modules/`
- ❌ 代码文件（`.py`、`.js`、`.ts` 等）→ `src/zephyr/` 或 `scripts/`
- ❌ 临时脚本、调试文件 → 要么走 AGENTS.md §6.5 入库，要么不存在
- ❌ 不属于"机器 SSoT"或"人类视图"的任何其他内容

## 父级目录

- 父级：docs 根目录
