---
module_id: KE-module_blu-track_c_owner______3-005
title: Track C：Owner 决策画像（3 类）
category: module_blueprint
---

# Track C：Owner 决策画像（3 类）

Track C：Owner 决策画像（3 类）

> 来源：聊天记录中 Owner 覆盖 AI 建议的决策 / 反复表达的偏好 / 隐性审美判断。优先级：**全部 LOW**（仅参考，不自动执行）。对标 Anthropic Claude implicit preference signals + GitHub Copilot user style learning。

| # | `category` | 含义 | 优先级 | `halflife_h` | 典型来源 | 示例 |
|:--:|-----------|------|:---:|:---:|---------|------|
| C1 | `decision_rule` | Owner 的决策启发式 | LOW | 720h(30d) | Owner 覆盖 AI 建议时自动提取 | "Owner 在 ruff vs pylint 中选 ruff——偏好 Rust 工具链" |
| C2 | `taste_signal` | Owner 的审美/偏好信号 | LOW | 720h(30d) | Owner 反复表达的偏好 | "Owner 偏好短函数 ≤30 行 + 避免过度抽象" |
| C3 | `override_log` | Owner 覆盖了 AI 的建议 | LOW | 720h(30d) | AI 建议被拒绝时记录 | "AI 建议 PostgreSQL → Owner 选 SQLite：零运维" |

**Track C 的特殊规则**：

| 维度 | Track A/B | Track C |
|------|:---:|:---:|
| 强制执行 | ✅ 是（如 A4 会阻断 CI） | ❌ 否——仅作为 context 注入，参考但不自动决策 |
| 过期策略 | 90d-360d | **30d**——偏好会漂移，短期有效 |
| 衰减机制 | usage_count↑ → 越用越强 | 30d 未再确认 → 自动 DISCARDED |
| 冲突处理 | 报错——知识冲突必须裁决 | 静默提示——"您上次说 X，但当前是 Y，要更新偏好吗？" |
| 入库条件 | G2 Triage ≥ 0.6 | Owner 重复 ≥2 次即可（不要求质量分数） |

**C→A 跨轨升级防护（盲点#22 stubs）**：C 类偏好永不会自动升级为 A 类规范。任何从 Track C 内容生成的 KE 若被分类器误判为 A 类 → 强制跨轨确认推送 Owner + 14d 冷却期 + ≥3 次独立确认后，才允许从偏好变为规范。当前不实现——KE < 200 时 C→A 升级事件 < 1/月，手动处理完全可控。

> **为什么 Track C 存在但不强制执行**：偏好是弱信号——Owner 会说"我偏好小迭代"，但紧急修复可能做一个大迭代。把偏好变硬规则会让 Owner 被自己过去的决策锁死。但完全不记录浪费可复用信息（下次 AI 就知道"这个老板喜欢短函数"）。对标 Anthropic Claude——"preference signals are suggestions, not rules"。

> **对标**：n1n.ai (2026) 三优先级分类——HIGH 直接 LTM、MID 走 MTM 晋升队列（"≥2 references → consolidate to LTM"）、LOW 丢弃。Vasilopoulos trigger table——"automatically routes tasks to appropriate specialized agents based on observable signals"。
> 大白话：三轨各有分工——Track A（施工知识）是"怎么盖房子"，强制执行；Track B（金融知识）是"盖什么房子"，强制执行；Track C（Owner 画像）是"老板喜欢什么风格"，仅参考不强制——30 天没人提就自动过期，因为人的偏好会变。
