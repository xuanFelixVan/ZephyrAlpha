---
module_id: KE-3860
title: 13. 风险
category: module_blueprint
---

# 13. 风险

13. 风险

| 风险 | 概率 | 缓解 |
|------|:---:|------|
| 正则提取遗漏引用（Stage 1 漏检） | 中 | 黄金数据集持续扩充 + 人工抽样验证 |
| 触发条件 B 的比较字段配置不完整 | 中 | `system_state_registry.yaml` 独立维护 |
| LLM 修复文本质量不一致 | 中 | Stage 6 输出→人工 spot-check + 固定 prompt 版本 |
| 禁碰规则过于宽泛（漏掉该修的不修） | 低 | 禁碰规则精确匹配关键词，不做语义推断 |

---
