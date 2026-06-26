---
module_id: KE-753
status: active
title: 16. 异常豁免机制
category: governance
ttl: permanent
---

# 16. 异常豁免机制

16. 异常豁免机制

**默认**：MLC-001 和 MLC-002 对所有模块同等约束。

**例外通道**：以下场景可申请豁免：

| 豁免场景 | 豁免内容 | 约束 |
|---------|---------|------|
| Phase 边界转换 | 临时跳过 testing→active 的集成测试前置条件 | Owner 审批，仅限 scaffold→1 |
| testing→in_dev 回退 | 允许从 testing 退回 in_dev | 前提：因外部依赖不可用导致（已在 MLC-001 表中标注为允许例外） |
| 紧急热修复 | 跳过 in_design→in_dev 的接口契约冻结条件 | 24h 内补齐契约 + Session Log 记录 |

**豁免规则**：每份豁免必须指定：豁免的 MLC 编号、豁免范围（具体模块）、有效截止日期。过期不续。
