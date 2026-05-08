---
module_id: KE-module_blu-16_5-000
title: 16.5 施工顺序
category: module_blueprint
---

# 16.5 施工顺序

16.5 施工顺序

```
Phase scaffold (当前: ✅ 已完成)
  └── 7 个 .py 文件全部实现 + 4 份测试

Phase experimental (待施工: T-DB-001~004)
  ├── T-DB-004: SSoT 修复（已修复——v2.1 蓝图审计）
  ├── T-DB-001: database_manager 测试（运维底线）
  └── T-DB-002: audit_schema 测试（审计底线）

Phase beta (增强: T-DB-005~011)
  ├── T-DB-005: 备份验证
  ├── T-DB-006: 死信队列
  ├── T-DB-007: 查询计划分析
  ├── T-DB-008: 迁移预览
  ├── T-DB-009: Metrics 导出
  ├── T-DB-011: 连接泄漏检测
  └── T-DB-010: FTS5 搜索

Phase stable (生产就绪)
  └── 全量测试 + 备份恢复演练 + 故障注入测试
```
