---
module_id: KE-2493---m-004
status: active
title: 8.7 Skill Failure Recovery & Model-Skill Affinity
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 8.7 Skill Failure Recovery & Model-Skill Affinity

8.7 Skill Failure Recovery & Model-Skill Affinity

```yaml
skill_failure_recovery:
  description: "Skill 执行失败时的恢复协议 + 模型-Skill 亲和力矩阵"

  failure_categories:
    F1_SKILL_FAULT:
      description: "Skill 指令自身有问题（歧义/错误/冲突）"
      recovery: "降级——跳过该 Skill → 写入 Anomaly → 标记 freshness_score=0"

    F2_MODEL_SKILL_MISMATCH:
      description: "Skill 的 model_hint 与当前模型不匹配"
      examples:
        - "Claude 优化的 Skill（长链推理）→ DeepSeek 执行时混乱"
        - "DeepSeek 优化的 Skill（代码生成）→ GLM 执行时质量下降"
      recovery: "如果可用，调用 model_hint 指定的模型重新执行"

    F3_CONTEXT_OVERFLOW:
      description: "Skill 加载后上下文超限——Agent 无法完整接收 Skill 指令"
      recovery: "自动 Compact（只加载 CRITICAL 规则 + 3 条核心 Checklist）"

    F4_CHAIN_FAILURE:
      description: "Skill Chain 中间一环失败"
      recovery: "终止 Chain 并回滚（对接 MOD-INF-021）→ 记录失败点 → 下一个 session 从断点继续"

  model_skill_affinity:
    description: "不同模型对 Skill 的理解与执行能力矩阵"
    matrix:
      DeepSeek:
        strength: "代码生成、SQL、数据库操作"
        weakness: "长链推理、架构设计"
        recommended_for: "数据库 specialist、实现者 Role Skill"

      Claude:
        strength: "架构设计、长链推理、安全审计、多 Skill 组合"
        weakness: "批量代码生成速度"
        recommended_for: "架构师 Role Skill、治理员 Role Skill、drift-detector"

      GLM:
        strength: "中文文档、需求分析"
        weakness: "复杂代码重构"
        recommended_for: "文档类 Skill、蓝图审查"

      Kimi:
        strength: "长文本理解、全量蓝图阅读"
        weakness: "快速迭代施工"
        recommended_for: "全量审计类 Skill"

      Qwen:
        strength: "通用编码、工具调用"
        weakness: "领域专业知识"
        recommended_for: "通用 fallback Skill 执行"
```
