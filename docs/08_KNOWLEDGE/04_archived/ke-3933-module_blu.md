---
module_id: KE-3781
title: 1.6 不包含的目标
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 1.6 不包含的目标

1.6 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | Web Dashboard / UI | 当前阶段纯 CLI |
| 2 | 自动修复（Auto-Fixer） | C4 阶段只跟踪不自动修——修复是两条生产线的职责 |
| 3 | GitHub Actions / CI 云端集成 | 暂不需要——项目在本地 |
| 4 | entity-graph 构建（D12 幻觉检测完全体） | 先上 SelfCheckGPT 零资源方案，entity-graph 是 beta |
