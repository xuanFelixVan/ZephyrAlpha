---
module_id: KE-1069
status: active
title: 6.2 TRAE 域（AI Session 强制注入规则）
category: governance_rule
ttl: permanent
---

# 6.2 TRAE 域（AI Session 强制注入规则）

6.2 TRAE 域（AI Session 强制注入规则）

> 来源：`.trae/rules/project_rules.md`（Trae IDE 自动注入每个 AI 对话上下文）
> 这些规则不是文档声明——它们由 Trae IDE 在每次对话启动时自动注入为 hard context。
> 但依据 RULE-FOUR（创建即注册协议），它们 MUST 在此登记表中登记。

| 登记号 | 规则内容 | 强制方式 | 来源路径 |
|--------|---------|---------|---------|
| TRAE-001 | RULE-ZERO：AI 对话文件锁协议——写前必须 check→acquire→release | doc | `.trae/rules/project_rules.md` RULE-ZERO |
| TRAE-002 | RULE-ONE：Python 脚本并发写入安全——temp+rename 原子模式 | doc | `.trae/rules/project_rules.md` RULE-ONE |
| TRAE-003 | RULE-TWO：反孤儿功能——新产出必须可被发现和调用（五问+集成清单） | doc | `.trae/rules/project_rules.md` RULE-TWO |
| TRAE-004 | RULE-THREE：删除前置确认协议——不经过三步审判不删任何文件 | doc | `.trae/rules/project_rules.md` RULE-THREE |
| TRAE-005 | RULE-FOUR：创建即注册协议——文件落盘同时注册表必须更新 | doc | `.trae/rules/project_rules.md` RULE-FOUR |
| TRAE-006 | RULE-FIVE：临时文件零残留铁律——session 结束时根目录不得有临时文件 | doc | `.trae/rules/project_rules.md` RULE-FIVE |
| TRAE-007 | RULE-SIX：任务粒度边界——二元四指标机械门判定是否创建 TaskCard | doc | `.trae/rules/project_rules.md` RULE-SIX |
| TRAE-008 | RULE-SEVEN：脚本多线程强制——独立子进程/I/O 必须 ThreadPoolExecutor 并行 + 创建即自测自修 | doc | `.trae/rules/project_rules.md` RULE-SEVEN |
| TRAE-009 | RULE-EIGHT：强制功能发现协议——不搜索已有功能证明没有同功能代码，不新建 | doc | `.trae/rules/project_rules.md` RULE-EIGHT |
| TRAE-010 | 冷启动 STEP 4.5：AI MUST 读 unified-asset-index.yaml 了解全项目资产规模与健康状态（对标 K8s `kubectl api-resources` + Linux `man hier`） | doc | `.trae/rules/project_rules.md` 强制 Session 冷启动序列 STEP 4.5 |
| TRAE-011 | AI Session 快速参考卡：每个 AI 入项目后 MUST 能引用附录 C 中的资产摘要卡——"项目规模认知"是 RULE-TWO 强制五问的第一答 | doc | `03_modules/infra_ops/asset-inventory/blueprint.md` 附录 C |

---
