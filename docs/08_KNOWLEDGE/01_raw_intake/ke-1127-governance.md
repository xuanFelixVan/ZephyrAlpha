---
module_id: KE-1042
title: 9. 变更记录
category: governance_rule
---

# 9. 变更记录

9. 变更记录

| 1.4.6 | 2026-05-07 | 新增 TRAE-011。(1) 登记 AI Session 快速参考卡规则：每个 AI 入项目后 MUST 能引用附录 C 中的资产摘要卡。(2) 统计更新：134→135 条（+1 TRAE → 11）。版本号 patch +1。 |
| 1.4.5 | 2026-05-07 | 新增 TRAE-010。(1) 登记冷启动 STEP 4.5：AI MUST 读 unified-asset-index.yaml 了解全项目资产规模与健康状态。(2) 统计更新：133→134 条（+1 TRAE → 10）。版本号 patch +1。 |
| 1.4.4 | 2026-05-07 | 新增 TRAE-009。(1) 登记 RULE-EIGHT：强制功能发现协议——不搜索已有，不新建。复用四选一决策（完全覆盖→直接用 / 80%→扩展 / 50%→重构+扩展 / 0%→可新建）。(2) 统计更新：132→133 条（+1 TRAE → 9）。版本号 patch +1。 |
| 1.4.3 | 2026-05-07 | 新增 TRAE-008。(1) 登记 RULE-SEVEN：脚本多线程强制——独立子进程/I/O 必须 ThreadPoolExecutor 并行 + 创建即自测自修。(2) 统计更新：131→132 条（+1 TRAE）。版本号 patch +1。 |
| 1.4.2 | 2026-05-07 | 新增 TRAE 域。(1) 登记 TRAE-001~007：RULE-ZERO（锁协议）到 RULE-SIX（任务粒度二元四指标机械门）七条 AI Session 强制注入规则。(2) 统计更新：124→131 条（+7 TRAE）。版本号 patch +1。 |
| 1.3.0 | 2026-05-02 | 新增 SCRIPT 域。(1) 登记 SCRIPT-QUALITY-001（审计脚本质量标准）13 条 MUST 规则。(2) 统计更新：111→124 条（44 ABS + 51 COND + 29 独立）。(3) SCRIPT-003 映射 ABS-43（shell=True 禁止）。版本号 minor +1。 |
| 1.2.2 | 2026-05-06 | AUDIT-02：`PS-STD-012 §2.1` 的索引失真阻断已注册 **META-V21**（PS-STD-001 §14.1）；修正 §9 变更记录 1.2.1 行表述。 |
| 1.2.1 | 2026-05-01 | meta/ 最终审查。(1) depends_on 格式 V2 确认（结构化行级）。(2) META-V17 违规 ID 冲突已解决：PS-STD-012 §2.1 不再错误复用 META-V17（该 ID 在 PS-STD-001 §14.1 中定义为 blueprint_refs 废弃蓝图检查），改为待分配占位（**META-V21** 已于 2026-05-06 正式分配——见本文件 1.2.2）。版本号 patch +1。 |
| 1.2.0 | 2026-05-01 | depends_on 升级为结构化行级格式（DOC-009 行级精度死规则）：`{target: module_id, at: "§N", why: "原因"}`。版本号 minor +1。 |
| 1.1.0 | 2026-05-01 | 结构修复。(1) 新增 `depends_on: [PS-STD-003, PS-STD-001]`（M-2 修复）。(2) 修复 COND→ABS 升格后映射未同步：DOC-015 COND-20→ABS-45、DOC-016 COND-21→COND-50、DOC-017 COND-22→COND-21、DOC-021 COND-26→ABS-46、DOC-022 COND-27→COND-52、DOC-023 COND-28→ABS-47、DOC-024 COND-29→ABS-48。版本号 minor +1。 |
| 1.0.1 | 2026-05-01 | 编辑性修复。(1) 新增缺失的 `date: "2026-05-01"` 字段（Draft 阶段 7 必填之一）。(2) `version` 补加引号（`1.0.0`→`"1.0.0"`）。(3) frontmatter 字段排序对齐 PS-STD-001 §2.3（ai_autonomy 移至 verifiability 之后）。版本号 patch +1。 |
| 1.0.0 | 2026-04-29 | 初始创建。登记全部 111 条规则（44 ABS + 49 COND + 11 REC + 7 CODE），覆盖 META/DOC/STRUCT/AUDIT/INFRA/CODE 六大域。 |
