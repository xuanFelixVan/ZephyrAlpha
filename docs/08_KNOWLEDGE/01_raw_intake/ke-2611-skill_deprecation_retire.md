---
module_id: KE-2516---retire-000
status: active
title: 9.2 Skill Deprecation & Retirement Lifecycle（决策 D-019-11）
category: module_blueprint
ttl: permanent
---

# 9.2 Skill Deprecation & Retirement Lifecycle（决策 D-019-11）

9.2 Skill Deprecation & Retirement Lifecycle（决策 D-019-11）

> **决策 D-019-11（新增）**：Skills 必须有结构化的废弃与退役生命周期。没有废弃路径的 Skill 注册表会"静默腐烂"——过时的 Skill 继续被 Agent 执行，产出的代码基于过时知识。
>
> **决策依据**：
> - Gaia Skill Tree RFC #74：提出 active → deprecated → retired 三态 + supersededBy 图边 + 证据失效触发器
> - Vercel Skills #501：完整实现 active → deprecated → yanked → removed 四阶段 + 消费侧 lifecycle awareness
> - Agent-Docs-Patterns：Machine-readable deprecation signals（HTTP headers: X-Deprecated + X-Sunset + X-Deprecation-Migration）

```yaml
skill_lifecycle:
  description: "Skill 从创建到退役的完整生命周期——四阶段模型"
  stages:
    active:
      description: "正常可加载、可执行、被 AGENTS.md 触发表引用"
      freshness_check: "30 天周期——freshness_score < 60 时标记 warning，< 30 时自动进入 deprecation review"

    deprecated:
      description: "暂时仍可加载，但发出警告——用户/Agent 被引导到替代 Skill"
      frontmatter:
        status: "deprecated"
        deprecated_reason: "Blueprint MOD-INF-XXX v3.0 已废弃 §3 接口契约"
        replacement_skill: "SKILL-DOM-DB-002"  # 替代 Skill ID
        sunset_date: "2026-08-01"               # 预计完全移除日期
      behavior:
        - "加载时在 Session Log 中写入 DEPRECATION WARNING"
        - "Agent 收到'此 Skill 即将废弃'的提醒 → 建议使用替代 Skill"
        - "仍允许执行（向后兼容）"

    retired:
      description: "不再可加载，但保留文件作为历史参考——只读存档"
      frontmatter:
        status: "retired"
        retired_date: "2026-08-01"
        archived_to: "docs/archive/skills/database-v1/"
      behavior:
        - "AGENTS.md 触发表移除该条目"
        - "SkillLoader 在加载时直接拒绝并报错"
        - "Skills registry 中标记 retired，默认隐藏"
        - "历史 Audit Trail 保留此 Skill 的所有执行记录"

    removed:
      description: "完全删除——仅在极少数情况下使用（e.g. Skill 包含安全漏洞）"
      condition: "Security 团队批准 + 没有任何活跃 session 引用 + 所有替代 Skill 已稳定运行 ≥ 30 天"

  deprecation_triggers:
    auto_triggers:
      T1_blueprint_breaking_change: "关联蓝图的 MAJOR 版本变更 → 对应的 Domain Skill 自动进入 deprecation review"
      T2_evidence_dead: "L3 reference 中 100% 的文件引用失效 → 自动触发 deprecation proposal"
      T3_unused: "Skill 在 90 天内未被任何 session 加载 → 自动标记为 'candidate_for_deprecation'"
      T4_freshness_zero: "freshness_score = 0 持续 ≥ 14 天 → 自动进入 retirement review"

    human_triggers:
      H1_owner_deprecate: "Owner 宣布 Skill 不再适用 → 人工执行废弃流程"
      H2_merge_replace: "两个 Skill 合并为一个 → 旧 Skill 废弃 → 触发表更新"

  grace_period:
    description: "Skill 从 deprecated 到 retirement 的缓冲期"
    duration: "≥ 30 天（给所有引用此 Skill 的上下游缓冲时间来迁移）"
    migration_window: "废弃日期 → 退役日期 中间的完整 CI 周期（≥ 6 次 CI 触发）"
```
