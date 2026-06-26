---
module_id: KE-4128
title: 5. 风险与缓解
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5. 风险与缓解

5. 风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | git revert 冲突——回滚的 commit 与后续 commit 有冲突 | 中 | 高 | preflight 预检冲突风险 → high→拒绝自动回滚 → DEFER_TO_HUMAN |
| R2 | 频繁自动回滚——auto_guard 后验失败率高 | 中 | 中 | Loop Detector：3 次/h → 暂停 agent 自动回滚权限 + 升级 |
| R3 | 多 IDE 并发回滚——两个对话同时回滚同一文件 | 低 | 高 | 全局 `rollback.lock` + 并发请求排队，超时 10s 返回 BUSY |
| R4 | 自动回滚震荡——revert 后 agent 重复犯错 | 中 | 高 | Agent Cooldown 5min 隔离 + Loop Detector 检测 |
| R5 | SQLite dump 失败——磁盘满 / 权限不足 | 低 | 中 | dump 失败 → 拒绝 commit（不产生无 DB 快照的 commit）→ 告警 |
| R6 | JSONL 与 git 版本不一致——dump 在 commit 前完成但后续手动改了 SQLite | 低 | 高 | 回滚重建后跑 DB 一致性验证（B3）→ 不一致则从最近一致 JSONL 重建 |
| R7 | partial_revert 留下未 revert 的孤儿变更 | 低 | 中 | partial_revert 后强制全量 G0 验证——被保留文件 + 被 revert 文件都存在 |
| R8 | discard 误操作——丢弃了 Owner 手动编辑的未 commit 变更 | 低 | 高 | discard 前检查被丢弃文件是否包含 owner_session_id → 是则拒绝 + 告警 Owner |
| R9 | 回滚中途崩溃——OOM kill / 断电导致回滚半完成（v0.5.0 新增）| 低 | 高 | execution_id + in_flight 文件 + 步骤级状态追踪 → 崩溃恢复从最后 SUCCESS 步继续（B43）|
| R10 | 回滚演练失败——DiRT drill 连续 2 次失败但未被察觉（v0.5.0 新增）| 低 | 高 | 每周自动 drill → 连续 2 次 FAIL → P0 Alert → 熔断所有自动回滚（B41）|
| R11 | 回滚风暴——10 个 agent 同时触发回滚耗尽系统资源（v0.5.0 新增）| 低 | 中 | 回滚预算管理：并发 ≤ 3 + 日配额 ≤ 20 → 超 budget 切换 forward-fix（B55）|
| R12 | 回滚快照被篡改——恶意 Agent 或攻击者修改 JSONL 快照（v0.5.0 新增）| 低 | 高 | JSONL Merkle 树 + HMAC-SHA256 签名 → 重建前完整性验证 → 不一致则拒绝（B49）|
| R13 | 依赖断裂——回滚模块 A 的代码导致下游模块 B 状态不一致（v0.5.0 新增）| 中 | 中 | 回滚前 dependency_impact_analysis + 广播 MODULE_ROLLBACK_NOTIFICATION 通知自愈（B48）|
| R14 | 回滚系统自毁——rollback_executor.py 本身被破坏导致回滚不可用（v0.6.0 新增）| 低 | 高 | rollback_bootstrap.py 零依赖最小化回滚 + chmod 444 只读锁定（B56）|
| R15 | AI 幻觉污染——AI 对回滚后状态产生幻觉理解导致错误决策（v0.6.0 新增）| 中 | 高 | hallucination_guard.py state_verification_round + VeriTrail DAG 溯源（B57）|
| R16 | 变形逃逸——恶意 AI 回滚后换写法达成同样破坏目的绕过门禁（v0.6.0 新增）| 低 | 中 | semantic_similar_detector AST 语义特征比较 + L2 Skill Kill 升级（B58）|
| R17 | 依赖漏洞复引入——回滚带回已知 CVE 的旧版依赖（v0.6.0 新增）| 中 | 中 | 回滚后自动 vulnerability_rescan + 尝试升级→失败通知 Owner（B59）|
| R18 | Token 浪费——过量回滚消耗 LLM API 费用（v0.6.0 新增）| 中 | 低 | rollback_budget token_cost + max_daily_tokens 100000 限制（B60）|
| R19 | GPG 签名链断裂——revert commit 无签名破坏可验证性（v0.6.0 新增）| 低 | 中 | preflight 检测 gpgSign → 自动传 --gpg-sign（B65）|
| R20 | Submodule 分裂——父仓库回滚但 submodule 版本不同步（v0.6.0 新增）| 低 | 中 | git submodule update --init --recursive + topology_change_log（B75）|
| R21 | Prompt 注入——恶意指令随 commit message 注入 AI 回滚后上下文（v0.7.0 新增）| 中 | 高 | prompt_injection_filter 输入消毒 + 结构化 context restoration prompt（B76）|
| R22 | 策略硬编码——回滚规则在 Python 源码中，改策略需要改代码（v0.7.0 新增）| 中 | 中 | rollback_policy_engine YAML 声明式策略 + Gate 校验合法性（B77）|
| R23 | GDPR 违规——回滚恢复已被合法删除的用户个人数据（v0.7.0 新增）| 低 | 高 | right_to_be_forgotten_registry + preflight 拦截禁止（B78）|
| R24 | 连接池中毒——回滚重建 DB 后连接池持有旧文件 inode（v0.7.0 新增）| 中 | 中 | db_reconnect_broadcast signal + connection_health_checker 自动重建（B79）|
| R25 | 告警疲劳——过量回滚通知导致 Owner 麻木忽略关键告警（v0.7.0 新增）| 高 | 中 | notification_throttle + daily_digest + realtime_alert 分级（B83）|
| R26 | 决策疲劳——过多 DEFER_TO_HUMAN 耗尽 Owner 决策能力（v0.7.0 新增）| 中 | 中 | auto_defer_cooldow
