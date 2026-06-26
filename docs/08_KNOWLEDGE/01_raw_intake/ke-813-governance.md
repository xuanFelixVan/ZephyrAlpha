---
module_id: KE-736
status: active
title: 13. 模块间交互规则
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 13. 模块间交互规则

13. 模块间交互规则

模块间的运行时交互受以下规则约束——这些规则补充了单模块治理（GOV-MOD-ALPHA_SIGNAL_DOMAIN~005）未覆盖的跨模块场景：

1. **调用失败不扩散**：A 调用 B 失败时，A 必须处理异常（重试/降级/报错），不得让错误向上游传播至 C
2. **循环调用禁止**：禁止 A → B → A 的直接或间接循环调用。循环引用应在 depends_on 设计阶段被 MAD-003 捕获
3. **跨层调用的契约强制**：跨层调用（如 hot→cold）必须通过 frozen 契约进行，禁止绕过契约直接操作
4. **级联退役通知**：当模块退役（deprecated/archived）时，必须在 Session Log 中列出所有 consumers，并逐个确认迁移状态（GOV-MOD-003 MLC-003）
