---
module_id: 00_MANAGEMENT_README_001
version: 1.0.3
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 项目办公室（00_MANAGEMENT）总入口与外链索引
standard_type: 导航说明
applicable_scope: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT
---

# 项目办公室（00_MANAGEMENT）

本文件夹放**规章、清单、终稿门禁、登记表**，不放具体模块的蓝图正文（蓝图在 `../01_BLUEPRINTS/`）。

**给任意 AI / 新协作者交接时**：请先读 [项目办公室 AI 交接说明](./PROJECT_OFFICE_AI_HANDOFF.md)（阅读顺序、真源优先级、常见任务）。**机构式分层总览**见 [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md)（L0～L5、与审计边界）。

**全库治理文档**（`09_AUDIT`、`10_GOVERNANCE_COMPLIANCE` 等）**真源仍在原目录**；办公室只提供一张总地图： [全库治理文档导航](./GOVERNANCE_DOCUMENTS_NAVIGATION.md)（说明为何不整体搬进办公室、为何不放进图纸柜）。

**例外（已定）**：**施工门禁**与**蓝图卫生总案**正文已迁入 [CANON/](./CANON/README.md)，作为蓝图终稿 / 放行的**唯一受控路径**；全库链接已指向该目录。

### 全库文档治理流程（摘要）

与「蓝图终稿任务」**交叉**：重复 / 同题多稿须在任务清单 **任务 1** 内闭环，方法不在此重复发明。**总清单链接核对**：Owner 默认 **100% 全量**逐条验证（见任务清单任务 1；抽检仅书面豁免）。

1. **蓝图与建设文档收口**：[全库蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md)（分解真源）+ [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md)（合并视角）。
2. **孤儿与重复 / 重叠**：[孤儿与重复治理 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) + [重复文档处理标准](../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md)；重复簇台账：[CANONICAL_POINTERS.md](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md)。
3. **审计区其余入口**：[全库治理文档导航](./GOVERNANCE_DOCUMENTS_NAVIGATION.md)。

---

## 本文件夹内（优先打开）

| 文档 | 说明 |
|------|------|
| [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) | 专业机构式 **L0～L5 分层**、控制流、与 `09_AUDIT` 边界 |
| [CANON 目录说明](./CANON/README.md) | 施工门禁 + 蓝图卫生总案（**真源**） |
| [施工门禁](./CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md) | 三阶段、蓝图终稿五条、§3 总清单 |
| [蓝图卫生总案](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) | P0–P3 清洁与退出标准 |
| [项目办公室 AI 交接说明](./PROJECT_OFFICE_AI_HANDOFF.md) | 接手文档/蓝图治理时的必读顺序与约定 |
| [图纸柜执行协议（防幻觉 · 可复制指令）](./BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md) | 整理图纸柜时必须遵守；内含发给 AI 的一段话 |
| [01_BLUEPRINTS 图纸柜文件治理规则](./01_BLUEPRINTS_REPOSITORY_RULES.md) | 图纸柜根目录能放什么、过程稿放哪、指示牌分层 |
| [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) | 目标态：四支柱 + 三阶段映射 + 合并自检（与门禁/任务清单对齐） |
| [蓝图终稿定义与认可](./BLUEPRINT_FINAL_SIGNOFF.md) | 什么叫终稿、谁认可、终稿后怎么改 |
| [全库蓝图终稿任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) | 阶段收尾勾选进度 |
| [受控文档登记表](./CONTROLLED_DOCUMENTS_REGISTER.md) | 易混淆/跨目录正式稿台账（按需填行） |
| [全库治理文档导航](./GOVERNANCE_DOCUMENTS_NAVIGATION.md) | 审计/标准/合规入口汇总（链接到真源，不搬迁正文） |

---

## 建设文档根目录（同级 `../`）

与施工、规范、模板相关的文件若在仓库中位于 `06_CONSTRUCTION_DOCS/` 根目录，从这里进入：

| 文档 | 说明 |
|------|------|
| [建设文档总索引](../INDEX.md) | 档案室大门（须与真实子目录一致） |
| [建设文档说明](../README.md) | 整棵建设文档树的说明 |
| [施工规范](../CONSTRUCTION_SPECIFICATION.md) | 施工层规范 |
| [版本管理指南](../VERSION_MANAGEMENT_GUIDE.md) | Git / 版本与发布习惯 |
| [蓝图空白模板](../BLUEPRINT_TEMPLATE.md) | 新建蓝图时套用 |
| [AI 施工速查](../AI_CONSTRUCTION_QUICK_REFERENCE.md) | AI 协作速查 |
| [新员工入职指南](../NEW_EMPLOYEE_ONBOARDING_GUIDE.md) | 上手路径 |
| [实施进度](../IMPLEMENTATION_PROGRESS.md) | 进度黑板（阶段切换时记得更新） |

---

## 全库级（仓库其他路径）

| 文档 | 说明 |
|------|------|
| [蓝图阶段完整总结](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md) | 全库蓝图内容清单与口径（总清单入口之一） |
| [蓝图阶段文档卫生总计划](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) | 文档收拾批次与要求（**CANON** 真源） |
| [TODO/TBD 清理清单](../../../09_AUDIT/REPORTS/TODO_CLEANUP_INVENTORY_20260406.md) | 占位符清理台账（若仍使用） |

---

## 常用脚本

- 刷新 `01_BLUEPRINTS/INDEX.md`：在仓库根目录执行  
  `python scripts/generate_01_blueprints_index.py`

---

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.3 | 2026-04-10 | 增加 [文档治理架构](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) 入口 |
| 1.0.2 | 2026-04-10 | 治理流程摘要：总清单链接默认全量核对（100%） |
| 1.0.1 | 2026-04-10 | 增加全库文档治理流程摘要（含孤儿/重复真源链） |
| 1.0.0 | 2026-04-10 | 首版：办公室总入口 + 外链表 |
