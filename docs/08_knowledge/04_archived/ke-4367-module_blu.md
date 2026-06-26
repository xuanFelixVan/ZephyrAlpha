---
module_id: KE-4205
title: 任务卡总览 (70张)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 任务卡总览 (70张)

任务卡总览 (70张)

| task_id | Phase | 标题 |
|---------|-------|------|
| TASK-INF-0200 | Phase 0 | 模块骨架搭建——目录结构与注册 |
| TASK-INF-0201 | Phase 1 | 数据模型统一——git-native+SQLite dump 双轨Checkpoint |
| TASK-INF-0202 | Phase 1 | 区分 revert vs discard——pre-commit FAIL 悖论解决 |
| TASK-INF-0203 | Phase 1 | RollbackExecutor 核心封装——preflight_check+preview+四级操作 |
| TASK-INF-0204 | Phase 1 | RollbackVerifier——G0门禁+pycache清理+DB一致性自愈 |
| TASK-INF-0205 | Phase 1 | AutoRollbackTrigger——失败信号三分类 |
| TASK-INF-0206 | Phase 2 | Partial Revert——file-glob 选择性回滚 |
| TASK-INF-0207 | Phase 2 | Loop Detector + Agent Cooldown——回滚震荡防护 |
| TASK-INF-0208 | Phase 2 | 回滚队列+并发序列化+优先级排序——rollback_lock |
| TASK-INF-0209 | Phase 2 | Non-tracked文件保护——.env/secrets备份恢复 |
| TASK-INF-0210 | Phase 3 | Rollback Simulator+Test Framework——隔离worktree模拟 |
| TASK-INF-0211 | Phase 3 | Rollback Metrics+MTTR Tracking——回滚SLA可观测性 |
| TASK-INF-0212 | Phase 3 | Hard Reset token gating——不可逆操作强制保护 |
| TASK-INF-0213 | Phase 3 | Remote Sync冲突处理——preflight中remote超前检查 |
| TASK-INF-0214 | Phase 3 | Anti-Patterns落地——AP1~AP44防护实现索引 |
| TASK-INF-0215 | Phase 4 | 1人运维CLI——zephyr rollback 完整命令集 |
| TASK-INF-0216 | Phase 4 | BREAK_GLASS adaption——Owner紧急取消回滚 |
| TASK-INF-0217 | Phase 4 | CT-RBK-GATE-001集成契约——48 exit code落地 |
| TASK-INF-0218 | Phase 5 | 回滚幂等执行器——execution_id+in_flight+崩溃恢复 |
| TASK-INF-0219 | Phase 5 | 回滚状态机——步骤级状态追踪+部分失败恢复 |
| TASK-INF-0220 | Phase 5 | 定期回滚演练调度器——每周DiRT drill+混沌场景 |
| TASK-INF-0221 | Phase 5 | 三级Kill Switch——L1/L2/L3+自动递进升级 |
| TASK-INF-0222 | Phase 5 | Forward-Fix优先决策——变更评估后优先forward-fix |
| TASK-INF-0223 | Phase 5 | AI对话上下文恢复——回滚后注入context restoration prompt |
| TASK-INF-0224 | Phase 5 | 依赖感知回滚——blueprint dependency graph+impact broadcast |
| TASK-INF-0225 | Phase 5 | Down-migration脚本自动生成——pre-commit hook+.sh/.ps1 |
| TASK-INF-0226 | Phase 5 | 30秒回滚仪表盘——Markdown零依赖dashboard+IM推送 |
| TASK-INF-0227 | Phase 5 | JSONL完整性保护——Merkle树+HMAC-SHA256签名 |
| TASK-INF-0228 | Phase 5 | Differential验证——回滚前后逐行比较DB表 |
| TASK-INF-0229 | Phase 5 | Checkpoint GC策略——快照保留上限100+90天max_age |
| TASK-INF-0230 | Phase 5 | 回滚审计Nexus集成——audit event聚合到Nexus AuditLog |
| TASK-INF-0231 | Phase 5 | 基于LLM的commit impact analyzer——语义级风险评估 |
| TASK-INF-0232 | Phase 6 | 自举回滚器——rollback_bootstrap.py 零依赖最小化回滚 + chmod 444 |
| TASK-INF-0233 | Phase 6 | AI 幻觉防护——回滚后强制 state_verification_round |
| TASK-INF-0234 | Phase 6 | 语义变形检测——AST/调用链/敏感API相似度 >70% → L2 Kill |
| TASK-INF-0235 | Phase 6 | 依赖漏洞复扫——回滚后 CVE 检测 + 自动升级 |
| TASK-INF-0236 | Phase 6 | Token 会计——max_daily_tokens 100000 + CLI stats --tokens |
| TASK-INF-0237 | Phase 6 | 温备热切——git worktree 副本 + <100ms RTO |
| TASK-INF-0238 | Phase 6 | 语义化 Rollback Tag——TASK/refactor/migration 边界 git tag |
| TASK-INF-0239 | Phase 6 | 分支拓扑回滚——topology_change_log + reflog 恢复 |
| TASK-INF-0240 | Phase 6 | Git 基础设施防护——git_infra_snapshot + inotify hooks/config 监控 |
| TASK-INF-0241 | Phase 6 | GPG 签名链保持——preflight gpgSign → git revert --gpg-sign |
| TASK-INF-0242 | Phase 6 | 密钥轮替感知——过期检测 + 自动轮替 + DEFER
