# MOD-INF-021 任务卡索引

> rollback-system 蓝图分解任务卡清单
> 生成日期: 2026-05-06 | 二次确认修正: 2026-05-07 | session: session-20260506-001

## 任务卡总览 (70张)

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
| TASK-INF-0242 | Phase 6 | 密钥轮替感知——过期检测 + 自动轮替 + DEFER_TO_HUMAN |
| TASK-INF-0243 | Phase 6 | 跨平台 Shell 双输出——.sh (Linux) + .ps1 (Windows) |
| TASK-INF-0244 | Phase 6 | venv 版本同步——pip install -r + freeze 差异审计 |
| TASK-INF-0245 | Phase 6 | env 变量热重载——env_watcher.py + last_env_reload sentinel |
| TASK-INF-0246 | Phase 6 | AI 时间上下文断裂修复——NTP+TOTP 时间证明 |
| TASK-INF-0247 | Phase 6 | Owner 目标覆盖 CLI——zephyr rollback --to + ACL |
| TASK-INF-0248 | Phase 6 | 网络分区超时保护——10s timeout + 3次重试 + CDN fallback |
| TASK-INF-0249 | Phase 6 | S3 快照防生命周期过期——lifecycle policy + 净化 cron |
| TASK-INF-0250 | Phase 6 | 外部可验证 Merkle Proof——回滚完整性第三方验证 |
| TASK-INF-0251 | Phase 6 | Submodule/Monorepo 同步回滚——多仓库一致回滚 |
| TASK-INF-0252 | Phase 7 | GDPR 遗忘权检查——right_to_be_forgotten_registry |
| TASK-INF-0253 | Phase 7 | LLM Prompt Injection 防护——回滚 trigger/message 扫描 |
| TASK-INF-0254 | Phase 7 | PSQL 连接池恢复——pg_bouncer health check + 自动重连 |
| TASK-INF-0255 | Phase 7 | 嵌套环境检测——Docker/K8s/VM 检测 + 参数自适应 |
| TASK-INF-0256 | Phase 7 | MCP 不可逆操作识别——reflog expire/gc --prune 禁止清单 |
| TASK-INF-0257 | Phase 7 | 通知洪流节制——throttle_window 300s + 摘要合并 |
| TASK-INF-0258 | Phase 7 | Self-Audit Conflict 解决——audit_findings.json 双写冲突 |
| TASK-INF-0259 | Phase 7 | Git Binary 完整性验证——sha256(git.exe) + 篡改 → L3 Kill |
| TASK-INF-0260 | Phase 7 | 反向预言自我实现防护——prediction ↔ act 隔离 |
| TASK-INF-0261 | Phase 7 | 青野 检查点密度——10min 最小间隔 + token-aware 节流 |
| TASK-INF-0262 | Phase 7 | AI 自主感知——autonomy_dashboard + healthy_gauge |
| TASK-INF-0263 | Phase 7 | 持续信任评估——continuous_trust_ledger + tier 分级自主 |
| TASK-INF-0264 | Phase 8 | 取证基础设施——Shell注入/hash存证/NTP/BitRot/TOCTOU |
| TASK-INF-0265 | Phase 8 | 取证加固——kill9原子写入/in_flight GC/SQLite WAL/NonRep/reflog |
| TASK-INF-0266 | Phase 8 | 取证扩展——git notes/证明链/只读/Owner缺席分级/Feature Flag |
| TASK-INF-0267 | Phase 9 | 操作治理——模型漂移/置信度/Error Budget/fail策略/沙盒/AI自防御 |
| TASK-INF-0268 | Phase 10 | 对抗性安全——Runbook/KnowGood/陈旧度/凭据/WAL/冲突/意图/滥用 |
| TASK-INF-0269 | Cross-cut | 蓝图分解覆盖审计——七维全覆盖验证 |

**审计报告**: [AUDIT-INF-0200.md](AUDIT-INF-0200.md)
**二次确认修正详情**: 见 AUDIT-INF-0200.md §三 纠正明细
