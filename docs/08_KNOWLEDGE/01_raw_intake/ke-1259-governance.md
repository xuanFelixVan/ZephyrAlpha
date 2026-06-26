---
module_id: KE-1172
title: MLC-001：阶段转换必须满足前置条件
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# MLC-001：阶段转换必须满足前置条件

MLC-001：阶段转换必须满足前置条件

任何模块从一个阶段转换到下一阶段，必须满足该转换的前置条件。禁止跳过阶段。

| 转换 | 前置条件 |
|------|---------|
| planned → in_design | 通过 GOV-MOD-ALPHA_SIGNAL_DOMAIN 准入门控（含 §7 #5 功能域不重叠检查）|
| in_design → in_dev | 接口契约草案完成；P0 模块需接口契约状态为 `frozen`（P0 约束详见 §8） |
| in_dev → testing | 代码实现完成，单元测试通过 |
| testing → active | 集成测试通过，Owner 审批（P0 额外约束详见 §8） |
| active → suspended | Owner 决策暂停（外部依赖不可用/业务暂停/等待条件） |
| suspended → active | 暂停原因已消除，Owner 审批恢复——**此回退不创建新 module_id** |
| active → deprecated | 有替代模块或 Owner 裁决退役（P0 额外约束详见 §6） |
| deprecated → archived | 90 天保留期满，所有引用已迁移，Owner 批准物理删除 |
