---
module_id: KE-1140
status: active
title: IFC-003：语义化版本兼容性
category: governance
ttl: permanent
---

# IFC-003：语义化版本兼容性

IFC-003：语义化版本兼容性

接口契约版本号遵循语义化版本（MAJOR.MINOR.PATCH）：

| 变更类型 | 版本变更 | 兼容性 |
|---------|---------|--------|
| 修复 bug，不改变接口 | PATCH+1 | 完全兼容 |
| 新增可选字段/端点 | MINOR+1 | 向后兼容 |
| 删除字段/修改类型/改变语义 | MAJOR+1 | 破坏性变更 |

向后兼容的变更（PATCH/MINOR）可以不通知消费方。破坏性变更（MAJOR）必须：

1. 创建 KB 决策记录
2. 通知所有消费方
3. 提供至少 30 天的迁移期
4. 迁移期内同时支持新旧版本
