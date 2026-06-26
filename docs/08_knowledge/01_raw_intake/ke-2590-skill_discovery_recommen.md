---
module_id: KE-2495---recommen-003
status: active
title: 8.9 Skill Discovery & Recommendation Engine
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 8.9 Skill Discovery & Recommendation Engine

8.9 Skill Discovery & Recommendation Engine

```yaml
skill_discovery:
  description: "当 Skills 从 8 个增长到 100+ 个时，关键字匹配不再可靠——需要语义级的 Skill 发现与推荐"

  methods:
    keyword_match:
      description: "当前 AGENTS.md 触发表的匹配方式——Task-Type → Skill 精确映射"
      scope: "50 个以内的 Skills——超过后触发表膨胀到不可维护"
      weakness: "无法处理模糊/跨领域任务"

    embedding_semantic_match:
      description: "将任务描述和 Skill description 分别做 embedding → 余弦相似度匹配 Top-3 候选 Skill"
      implementation: "BGE-M3 或 text-embedding-3-small → 离线预计算 Skill embedding → 运行时匹配"
      scope: "100+ Skills——不需要人工维护触发表"

    hybrid_approach:
      description: "Keyword + Embedding 融合"
      rule: "Keyword 精确命中 → 直接加载（最快）；Keyword 无命中 → Embedding Top-3 候选 → Agent 选择或都加载"

  skill_recommendation:
    trigger: "AI session 开始时或在 Skill 执行后自动建议下一个 Skill"
    data_source: "Skill 共现频率（Skill A 和 Skill B 在同一 session 中被同时加载的频率）"
    recommendation_list: "Top-3 related skills → 在 Session Resume 中留给下一个 session"
```
