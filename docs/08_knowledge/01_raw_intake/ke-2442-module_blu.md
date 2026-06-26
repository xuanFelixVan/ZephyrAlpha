---
module_id: KE-2347
title: 6. 风险与缓解（扩展）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 6. 风险与缓解（扩展）

6. 风险与缓解（扩展）

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | 蓝图与 Skill 漂移——蓝图更新但 Skill 未同步 | 高 | 高 | freshness_score 机制：蓝图 version 变更 → 关联 Skill 自动降分；CI 门禁：降分超过阈值 → 触发 Skill 重审 |
| R2 | Skill 指令模糊——AI 执行时歧义导致错误 | 高 | 中 | 强制 Checklist 格式（非建议/描述）；反馈环对接——模糊导致失败 → 记录 → 人工优先修复 |
| R3 | Domain Skill 爆炸——100+ 模块维护成本 | 中 | 中 | Factory Agent 自举 + freshness_score 自动优先级排序；只审查 freshness < 阈值 的 Skill |
| R4 | 多 Skill 组合冲突——Domain 和 Role 对同一操作给出不同指令 | 中 | 中 | 明确优先级规则：Domain > Role（更具体优先）；冲突检测脚本 |
| R5 | AGENTS.md 膨胀——触发表条目过多 | 低 | 中 | 触发表保持 30 条以内；超出则拆分为独立 `trigger_table.yaml`（AGENTS.md 引用） |
| R6 | Token 预算在组合加载下超限 | 中 | 高 | Progressive Disclosure L1→L2→L3 递进；组合预算 ≤ 800 tokens；超降自动降级 L3 全部跳过 |
| R7 | Skill 执行无状态——跨 session 丢失进度 | 高 | 中 | Session Resume 协议：Skill 卸载时写入结构化执行摘要 → 下一个 session 的 AGENTS.md 中加载 |
| R8 | Skill 生成质量不一——Factory Agent 产出不稳定 | 中 | 中 | 模板驱动 + 人工审查批准；gate 检查 Skill 格式合规性（SKILL.md 标准格式校验） |
| R9 | 多 AI 模型对同一 Skill 理解不同 | 低 | 低 | model_hint 字段明确推荐模型；Skill 内容使用结构化表格 > 长篇散文 |
| R10 | Skill 注入攻击——Skill 文件被污染导致 Agent 行为被劫持 | 低 | 高 | Defense in Depth 四层防护（Parse→Validate→Simulate→Audit）；LLM Security 集成；Skill 哈希校验 |
| R11 | Skill Chain 死锁——A→B→A 循环导致上下文无限增长 | 中 | 高 | Chain depth limit=3 + 循环检测（O(1)）；超出深度自动终止并升级到 Owner |
| R12 | 上下文碎片化——多 Skill 分散导致注意力稀释、Agent 遗忘前面的指令 | 高 | 中 | Skill Compact 合并机制 + Attention Weighting 权重标注；第 3 个 Skill 加载后第 1 个 Skill 可能已被遗忘 |
| R13 | Canary 评估失效——20% 样本过小导致统计显著性不足 | 中 | 中 | Canary 二期 ramp 到 50% 扩大样本；Welch's t-test p<0.05；≤200 会话的测试不做 A/B 决策 |
| R14 | Cross-IDE 翻译失真——不同 IDE 的加载机制差异导致 Skill 指令被截断或误解 | 中 | 中 | AGENTS.md 作为单一事实源（SSOT）；IDE 翻译层附带 schema valid + diff test |
| R15 | Skill 执行评估不可靠——LLM-as-a-Judge 评分与人类判断不一致 | 中 | 中 | 强制 Spearman ρ ≥ 0.80 校准阈值；不达标的 Skill 人工审查 transcripts |
| R16 | Skill 成本无边——100+ Skills 无限制加载导致经济崩溃 | 高 | 高 | Skill Economics 成本模型 + Budget Enforcer 强约束 + 模型路由优化（简单→低价模型） |
| R17 | 废弃 Skill 静默腐烂——过时 Skill 继续被 Agent 执行 | 高 | 中 | Deprecation Lifecycle 四阶段（active→deprecated→retired→removed）+ 自动检测过期触发器 |
| R18 | AI 自主修改 Skill 导致门禁下降——L2/L3 自主度被滥用 | 中 | 高 | Autonomy Spectrum L0-L4 分级 + CI 门禁阻断 + 事故不适自动 revert |
| R19 | Agent 事故无法追溯 Skill——没有事故→Skill 修复的闭环 | 高 | 高 | Incident Postmortem Engine：事故→Timeline重建→根因→Skill fix PR |
| R20 | Skill 目录损坏/被删——系统无法恢复 | 低 | 高 | GitOps disaster recovery + 每日备份验证 + SHA256 corruption detection |
| R21 | 新 session 冷启动过长——无 Onboarding Skill 首次交互成本过高 | 中 | 低 | 前三 session 自动加载 Onboarding Skill + Session Warm-up + 第 4 次起跳过 |
| R22 | 双语 Skill 在多模型下表现不一致——中文 Skill 在 Claude 上质量下降 | 低 | 低 | 双语对照字段 + 跨模型 pass_rate 对比测试（差异 ≤ 5%） |

---
