---
module_id: KE-2346
title: 6. 决策记录
category: module_blueprint
---

# 6. 决策记录

6. 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-024-01 | 四级自动降级，不需要 Owner 介入 | 2026-05-05 | 预算超限是技术问题不是审批问题，自动降级更及时 |
| D-024-02 | 三级→五级预算体系（Request→Turn→Task→Session→Global） | 2026-05-05 | 专业机构 4 级实践 + Turn 级是 token spiral 锚点 |
| D-024-03 | Pre-flight Gate 事前拦截——调用前预估+拦截，不再纯事后反应 | 2026-05-05 | Google Adaptive Budgeting / kagenti pre-request blocking |
| D-024-04 | 🆕 v0.4.0 模型路由方向反转——默认最低→质量不达标才升级 + Batch 路由（50% 折扣） | 2026-05-05 | Cost Engineering for Agents + Vibe Coding 模型组合拳 |
| D-024-05 | 🆕 v0.4.0：六级降级链新增 L1.5 沉没成本干预 + 预算耗尽用户沟通协议 | 2026-05-05 | 再试一次就好了 是成本超支的心理陷阱——系统必须主动干预 |
| D-024-06 | Loop Detector：工具调用指纹匹配 + 3/5/10 三级阈值 | 2026-05-05 | 87% 成本超支来自过度自治 + AICosts.ai real-world disasters |
| D-024-07 | Semantic Cache：三层缓存（Prompt/Tool/Embedding）+ 可观测 | 2026-05-05 | Anthropic cache-aware + Agent 成本控制实战（缓存降本 30-50%） |
| D-024-08 | 🆕 v0.4.0：Cost Attribution 新增 Outcome（成功/失败/部分）维度 + LLM-as-Judge 独立核算 + 数据生命周期 | 2026-05-05 | FinOps for AI chargeback + 失败消耗和成功消耗的 ROI 完全不同 |
| D-024-09 | 🆕 v0.4.0：Burn Rate 新增 Distribution Shift 检测 + Rate Limit 浪费追踪 | 2026-05-05 | 结构异常往往先于总量异常 + 被限流的重试是纯浪费 |
| D-024-10 | 🆕 v0.4.0：Solo Maintainer 扩展——ENV Profile + 新模型发现 + 一键回滚 + 沙盘守卫 + 数据自动清理 | 2026-05-05 | 1人+AI维护的零运维需求 |
| D-024-11 | 🆕 v0.4.0：Stream Abort Guard——流式输出中途二次预算确认（每 500 token checkpoint） | 2026-05-05 | Pre-flight 只能管输入，in-flight 缺失导致 87% 成本超支发生在输出阶段 |
| D-024-12 | 🆕 v0.4.0：Output Quality Gate——前 200/300 token 快速质量校验（格式/相关性/幻觉） | 2026-05-05 | 实时质量信号比事后 ROI 分析更有成本控制价值 |
| D-024-13 | 🆕 v0.4.0：ENV Profile——dev/staging/prod 三套预算策略 + dev 环境永远锁在免费模型 | 2026-05-05 | 调试时不小心烧预算是一人维护模式的最大风险 |
| D-024-14 | 🆕 v0.4.0：Budget Policy Sandbox——dry-run 模拟（4 场景）+ Policy Versioning（回滚/diff） | 2026-05-05 | 预算策略上线前不验证 = 拿生产环境当试验田 |
| D-024-15 | 🆕 v0.4.0：辅助能力——上下文浪费检测 + 冷启动豁免 + 自托管模型成本模型 | 2026-05-05 | 隐性成本在 solo 语境下持续累积至不可忽略 |
| D-024-16 | 🆕 v0.5.0：Instruction Bloat Detector——检测 AGENTS.md/指令文件膨胀（Boris Cherny 数据：14% 浪费） | 2026-05-05 | 指令文件每 turn 都被发送——膨胀的边际成本极大 |
| D-024-17 | 🆕 v0.5.0：Conversation History Tax Detector——对话历史加权衰减 + 有效引用率（Boris Cherny 数据：13% 浪费） | 2026-05-05 | 压缩解决大小不解决价值——80% 压缩后历史仍无价值 |
| D-024-18 | 🆕 v0.5.0：Timeout Guard——独立 asyncio daemon timer，wall-clock 超时即 abort（AgentGuard 三大 guard 之一） | 2026-05-05 | 存在 token 少但耗时极长的任务——仅 token/cost 预算无法覆盖 |
| D-024-19 | 🆕 v0.6.0：Self-Budget——Budget Enforcer 自身运营成本管控（GUARDS 不是免费的） | 2026-05-05 | SUPERVISORAGENT (ICLR 2026) LLM-free trigger 原则——传统 guards 自身消耗 token 评估 token |
| D-024-20 | 🆕 v0.6.0：Token Spiral EWS——上下文膨胀/工具链扩张/委托深度爆炸/时间递增四维检测 | 2026-05-05 | TechAhead 2026——1 task → 47 API calls spiral pattern |
| D-024-21 | 🆕 v0.6.0：Context Poisoning Cascade——幻觉 upstream 输出指数污染 downstream agents | 2026-05-05 | SUPERVISORAGENT——单点 hallucination → pipeline 级成本放大 |
| D-024-22 | 🆕 v0.6.0：Hierarchical Parent-Child Agent 成本归因——委托链树状成本 | 2026-05-05 | MAS coordinator 委托模式需要归因到 delegation pattern 级别 |
| D-024-23 | 🆕 v0.6.0：Think-Time Cost 模型 + LLM-Free Guard 升级路径——推理 token 隐藏成本 + 渐进降本 | 2026-05-05 | Reasoning
