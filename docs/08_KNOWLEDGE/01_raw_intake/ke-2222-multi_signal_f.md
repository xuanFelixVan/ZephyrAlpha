---
module_id: KE-2129-----------multi-signal-f-005
status: active
title: 3.5.1 多信号源新鲜度引擎（Multi-Signal Freshness Engine）
category: module_blueprint
ttl: permanent
---

# 3.5.1 多信号源新鲜度引擎（Multi-Signal Freshness Engine）

3.5.1 多信号源新鲜度引擎（Multi-Signal Freshness Engine）

> **盲点#45+#46**：专业机构（Google SRE KM、Shopify Developer Knowledge）和顶尖开源项目（LangChain、dbt）的知识管理系统的共同特征：**不使用单一的时间衰减信源**。它们融合至少 3 种信号来判断一条知识的"健康度"。

**四信号源融合公式**：

```
freshness_multi = min(
    freshness_time,              // 信号1：时间衰减（§3.5 半衰期）
    freshness_code_change,      // 信号2：代码变更触发（§3.5.1a）
    freshness_dependency_health, // 信号3：依赖链健康度（§3.5.1b）
    freshness_coverage_conflict  // 信号4：新知识覆盖/冲突（§3.5.1c）
)
```

> **设计原理**：取 `min()` 而非加权平均——任何一个信号拉响警报，新鲜度=该信号值（而非被其他信号平均掉）。防御优先于平滑。

**(a) 信号2：代码变更触发（Code-Triggered Freshness Reassessment）**

定义 **KE→代码锚点映射**：KE 的 `evidence.md` 中自动提取或手动标注引用的代码对象（文件路径 + 符号名 + 版本号）。

```
触发条件：
  pyproject.toml 变更 → 所有引用该依赖的 A5/A6 类 KE → 新鲜度立即设为其 fresh(0d) * 0.9
  src/zephyr/kb/*.py 变更 → 所有属于 infrastructure 领域的 KE → 新鲜度衰减加速至 0.5x
  docs/03_modules/**/*.md 变更 → 所有引用该模块的蓝图类 KE → Q_retention_IDEAL(λ_d=0.85) * 0.7
  .cursor/rules/*.mdc 变更 → 所有 A8 类 KE → 触发全量审查

周末 cron 扫描（§7.4.1 的一部分）：
  → git diff HEAD~7d HEAD --name-only
  → 比对 KE→code_anchor 映射
  → 生成 CodeDrivenFreshnessReport → 推送 Owner
```

**(b) 信号3：依赖链健康度（Dependency Health Scoring）**

```
若 KE-A depends_on KE-B，且 KE-B 新鲜度 < 0.3：
  → KE-A 新鲜度自动钳制至 ≤ min(KE-A.freshness_current, 0.5)
  → 原因：上游知识已腐烂，下游知识的正确性存疑
```

**(c) 信号4：新知识覆盖/冲突（Semantic Coverage & Competition）**

```
若新增 KE-C 与已有 KE-Old 语义相似度 > 0.85 且创建时间差 > 30d：
  → KE-Old 新鲜度自动钳制至 ≤ 0.4
  → 触发 Owner 决策：KE-Old 是否应标记为 SUPERSEDED_BY KE-C
  → 对标：学术界的 "literature obsolescence"——新论文出现后旧论文引用价值下降
```

> **对标**：Google SRE Book 第 27 章 "Managing Critical State"——"**consistency must be enforced actively, not assumed passively**"。Shopify Developer Knowledge System 的 `freshness_score = f(time, code_churn_rate, dependency-graph)`——三变量函数而非单变量衰减。本蓝图的多信号源引擎汲取了这两个系统的核心思想但适配到单机+AI的上下文。
