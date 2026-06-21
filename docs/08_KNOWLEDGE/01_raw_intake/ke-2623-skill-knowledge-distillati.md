---
module_id: KE-2528
status: active
title: 9.8 Skill Knowledge Distillation & Merge Detection
category: module_blueprint
---

# 9.8 Skill Knowledge Distillation & Merge Detection

9.8 Skill Knowledge Distillation & Merge Detection

```yaml
skill_distillation:
  description: "当多个 Skills 覆盖重叠领域时——自动检测并建议合并或拆分"

  merge_candidates:
    detection_method: "embedding similarity——两个 Skill 的 description + L2 body 合并向量的余弦相似度 ≥ 0.85 → 标记为 merge candidate"
    human_review: "Owner 审查——确认 merge 是否合理 → 创建合并 Skill → 废弃旧 Skill → 更新触发表"

  split_candidates:
    detection_method: "Skill 的 Checklist ≥ 15 步 → 建议拆分为 2+ 个 Sub-Skills"
    human_review: "Owner 审查——确认是否应拆分 → 创建 Sub-Skills → 原 Skill 作为 Orchestrator（只负责按顺序调用 Sub-Skills）"

  consolidation_schedule:
    frequency: "每 30 天运行一次 distillation analysis"
    report: "生成 Top-10 merge candidates + Top-5 split candidates → Owner 审查"
```
