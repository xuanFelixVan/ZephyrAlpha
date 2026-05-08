---
module_id: KE-documentat-4_2-005
title: 4.2 规则层级条件禁止
category: documentation
---

# 4.2 规则层级条件禁止

4.2 规则层级条件禁止

| #       | 条件禁止行为              | 触发条件                  | 替代方案          | 来源                              |
| ------- | ------------------- | --------------------- | ------------- | ------------------------------- |
| COND-05 | L3 文档使用 MUST/SHOULD | doc\_type 属于 L3 基础模板时 | 使用信息性措辞       | PS-STD-002                      |
| COND-06 | L2 文档使用 MUST        | doc\_type 属于 L2 设计模板时 | 使用 SHOULD/MAY | PS-STD-002                      |
| COND-07 | B 轨反向依赖 C 轨         | 平台能力模块依赖业务模块时         | 重新设计依赖方向      | directory-structure-standard.md |
| COND-08 | C 轨内部反向依赖           | 低层依赖高层时               | 逐层向下依赖        | directory-structure-standard.md |
