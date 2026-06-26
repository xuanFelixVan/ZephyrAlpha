---
module_id: KE-4423
title: 决策记录
category: module_blueprint
ttl: permanent
---

# 决策记录

决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-020-01 | 两层审计粒度（任务级摘要+文件级明细） | 2026-05-05 | 1人场景，任务级摘要够日常浏览，文件级明细够问题定位 |
| D-020-02 | JSONL 为唯一真源，SQLite 为派生查询索引 | 2026-05-05 | 多 IDE 并发，JSONL 天然 append-only 且 git 友好；对标 GOV-CMP-002 |
| D-020-03 | Provenance 按权限级别分级（轻量/标准/全量） | 2026-05-05 | 1人+AI场景，99%操作无草稿和仲裁，强制三件套形同虚设 |
| D-020-04 | 密码学完整性——哈希链 + HMAC + Merkle | 2026-05-05 | JSONL append-only ≠ tamper-evident；AI 可删除行后重 append；对标 Microsoft AGT Merkle-chain + W3C PROV |
| D-020-05 | 元审计——审计系统自身操作留痕 | 2026-05-05 | 1人+AI 维护，无人审计审计系统本身；对标 GOV-CMP-002 AUD-001 |
| D-020-06 | 蓝图漂移检测——实际操作 vs 蓝图规定 | 2026-05-05 | 对标 ISACA 2025 "Embedded not paper" + MOD-INF-023 Drift Detector |
| D-020-07 | AI 行为异常签名——13 种自动检测模式（v1.1.0 扩展） | 2026-05-05 | 对标 OWASP ASI-10 "Lack of Observability" + ISACA 自修改AI审计 |
| D-020-08 | 三角闭环反馈——审计聚合数据回写 Policy 驱动规则演进 | 2026-05-05 | 对接 KBG-0010 §4.4 Runtime→Policy 接口；对标 Netflix 混沌反馈 |
| D-020-09 | Lamport 逻辑时钟——多 IDE 时序一致性 | 2026-05-05 | 多 IDE `datetime.now()` 不可靠；对标 Dynamo Vector Clock |
| D-020-10 | 三层存储（热/温/冷）+ 自动迁移 | 2026-05-05 | JSONL 膨胀不可持续；对标 Goldman SecDB 分层 + AWS S3 lifecycle |
| D-020-11 | 隐私脱敏——写入时自动检测 PII 并掩码 | 2026-05-05 | 审计日志不可变 + GDPR/HIPAA 合规；对标 GOV-CMP-002 AUD-004 |
| D-020-12 | 保留期自动执行——dry-run 先行 + Owner 审批 | 2026-05-05 | 对标 GOV-CMP-002 + GOV-DATA-003；无人手动清理 |
| D-020-13 | Cold Start——git log 回溯生成历史审计基线 | 2026-05-05 | 审计系统首次启动时无历史数据；baseline 标记 low confidence |
| D-020-14 | Agent 级 Ed25519 数字签名——non-repudiation | 2026-05-05 | HMAC 系统级+CAN 不区分 Agent；对标 Microsoft AGT Ed25519 Agent Signing + OWASP ASI-09 |
| D-020-15 | LLM CoT 推理链审计 | 2026-05-05 | 对标 OWASP ASI-10 完整可观测性 + FCA 监管文件审查"推理"维度 |
| D-020-16 | 委托链审计——深度控制 + 权限缩小 | 2026-05-05 | 对标 Microsoft AGT DelegationChain + NIST 2026 委托身份追踪 |
| D-020-17 | 渐进信任分数——连续值 + 时间衰减 | 2026-05-05 | 对标 ISACA "trust degrades without continued good behavior" + AGT Trust Scoring |
| D-020-18 | 外部独立验证端点 | 2026-05-05 | 100% AI 施工——AI 不能自证清白；对标 Goldman probe/Prometheus 探测层 |
| D-020-19 | 跨 IDE 一致性交叉验证 | 2026-05-05 | 对标 Goldman SecSync 不一致检测 |
| D-020-20 | 外部工具调用链审计 | 2026-05-05 | 对标 ISACA "使用工具"三要素闭环 + Agent→MCP→API 可追溯 |
| D-020-21 | 间接操作检测 | 2026-05-05 | Agent 可通过 symlink/script/cron/MCP 绕开直写审计 |
| D-020-22 | Dry-Run vs Real 差异检测 | 2026-05-05 | AI 在 dry-run 时说 X 实际做 Y → 差异异常报告 |
| D-020-23 | 供应链审计——包安装可追溯 | 2026-05-05 | `pip install`/`npm install` 需审计记录 — 对标 OWASP 供应链安全 |
| D-020-24 | 监管证据包一键导出 | 2026-05-05 | 对标 FCA 格式 + SEC 17a-4 审计要求 |
| D-020-25 | 合规框架条款映射 | 2026-05-05 | 对标 Microsoft Agent Compliance 自动合规验证 |
| D-020-26 | 反馈循环自审计 | 2026-05-05 | 防止三角闭环自我强化错误模式 |
| D-020-27 | Git 隔离——审计日志独立存储 | 2026-05-05 | 防止 git reset 导致审计历史丢失 |
| D-020-28 | Knowledge Base 投毒防护 | 2026-05-05 | 审计数据→KB 的投毒防护门禁 |
| D-020-29 | rate_limit + volume_dos 防护 | 2026-05-05 | 防止 Agent 海量小操作 DoS 审计系统 |
| D-020-30 | trail_for_ai_context() 升级为 P0 接口 | 2026-05-05 | AI 是审计日志的主读者——输出设计为 AI 零推理可消费 |
| D-020-31 | Prompt 注入防护——审计条目禁止含 AI 指令关键词 | 2026-05-05 | trail_for_ai_context() 将审计数据注入 LLM conte
