---
module_id: KE-3943
title: 16.6 回滚方案
category: module_blueprint
---

# 16.6 回滚方案

16.6 回滚方案

> ⚠️ 每个步骤如果出问题，**必须**有明确的回滚操作。

| 任务 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| T-DB-001 (database_manager 测试) | 测试发现健康检查 bug | 不修复、不回滚源文件——将 bug 登记到 §20 风险矩阵，新增 R14 条目 |
| T-DB-002 (audit_schema 测试) | AuditQuery 返回空结果 | 检查 events 表数据完整性——若缺数据，补充 test fixture；若代码问题，登记 bug |
| T-DB-003 (query_metrics 测试) | PercentileTracker 计算结果错误 | 审查算法正确性——对比手工计算与 tracker 输出 |
| T-DB-004 (SSoT 修复) | ✅ 已修复——无需回滚 | v2.1 蓝图审计时已完成 b_db.yaml + registry 同步 |
| T-DB-005 (备份验证) | 恢复后的 DB 与生产不一致 | 保留原始 DB 文件不动——恢复演练在临时路径进行，不影响生产 |
| T-DB-006~011 | 施工中途失败 | 新增代码限于新方法/新文件——不影响既有 7 文件功能。删除新文件即可回滚 |
