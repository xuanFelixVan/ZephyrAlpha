---
module_id: KE-2418
title: 7. 风险登记
category: module_blueprint
---

# 7. 风险登记

7. 风险登记

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|:---:|------|------|
| 五级预算过度限流 | 中 | AI 频繁被拦截→施工效率下降 | 每级独立配置 + Borrow 机制 + Tier-0 永远可用 |
| **Stream Abort 过于激进**（🆕 v0.4.0） | 中 | 正常长输出被误中断→任务无法完成 | 仅当 `quality_score < 0.3 AND output_fragment_unusual` 才 abort；正常超长输出仅 warn |
| Burn Rate 误报 | 低 | 频繁触发不必要的降级 | 7 天基线自适应 + 告警冷却 |
| 循环检测误杀正常重试 | 低 | 正常的 3 次重试被阻断 | 阈值 ≥ 3 + fingerprint_ttl 5 分钟 |
| 语义缓存污染 | 低 | 过期数据被返回 | 审计每条 hit + TTL 强制过期 + 加密 |
| LiteLLM 定价同步失败 | 低 | 价格失真→预算控制不准 | 本地缓存 + 3 天同步失败告警 |
| 降级螺旋 | 中 | 连续降级导致系统不可用 | Anti-spiral max 1/min + recovery cooldown |
| **ENV Profile 切换错误**（🆕 v0.4.0） | 中 | dev 环境误用 production profile→浪费预算 | 每次新 Task 自动重置 + `ZEPHYR_ENV` 显式设置 + dev 环境永久哨兵检查 |
| **策略沙盘 vs 实际不一致**（🆕 v0.4.0） | 低 | dry-run 通过但上线后卡住 | Sandbox 使用真实历史数据回放 + Score differential alert |
| **上下文浪费检测自身开销**（🆕 v0.4.0） | 低 | 每次调用后额外 LLM 校验增加成本 | waste 检测只在 10% 采样执行 + 仅 warn 模式 |
| **新模型自动发现被忽略**（🆕 v0.4.0） | 高 | Owner 不知道有更便宜的模型可用→持续多付钱 | 每周摘要置顶新模型发现 + 月度备忘提醒 |
| **Timeout Guard 误杀长构建**（🆕 v0.5.0） | 中 | 大型重构/测试需要 > 1h 但被 timeout 截断 | sidestep 机制：显式标记 `--no-timeout` 可绕过单次任务超时 |
| **指令膨胀检测误报**（🆕 v0.5.0） | 低 | 合理的大型 AGENTS.md 被标记为膨胀 | 仅超过 `session_budget × 0.25` 才告警——正常 2000 字指令不会触发 |
| **自修复螺旋误杀**（🆕 v0.5.0） | 低 | 正常的迭代调试被当作螺旋 | 仅 lint_error_count 增长才触发——功能改进不会被拦截 |
| **长上下文定价 drifts**（🆕 v0.5.0） | 中 | Provider 默默调整溢价阈值→系统仍用旧阈值 | 价格同步中也同步定价策略（非仅价格数字） |
| **预算储蓄被 exploit**（🆕 v0.5.0） | 低 | Agent 故意用最便宜模型以储蓄→影响产出质量 | 储蓄池仅在预算紧张时自动释放——不鼓励行为 |
| **Self-Budget 自身触发熔断**（🆕 v0.6.0） | 中 | Budget Enforcer 自身用光预算→所有 guard 降级为 warn-only | 同行无解——这是终极防线挑战。用 LLM-free guard 逐步替换来降低概率 |
| **Spiral EWS 入报警阈值不准**（🆕 v0.6.0） | 中 | 正常多步推理被误判为 spiral | 阈值为 Pearson r > 0.7（强相关才触发）+ 需要 5 轮趋势确认 |
| **Poison Cascade DAG 开销自噬**（🆕 v0.6.0） | 低 | provenance DAG 自身数据量随调用增加而膨胀 | TTL 1h 过期 + 仅保留 contradiction 节点 |
| **Parent-Child 归因循环引用**（🆕 v0.6.0） | 低 | A委托B委托C委托A 形成循环归因 | DAG cycle detection + max_depth=4 |
| **Think-Time 成本模型滞后**（🆕 v0.6.0） | 中 | Provider 暗改推理价格→模型失真 | 通过 actual_charges 异常检测（> 20% deviation → 强制重新校准） |
| **Ed25519 密钥丢失**（🆕 v0.7.0） | 高 | 私钥丢失→所有预算策略锁定，无法修改 | 密钥存储于1Password/YubiKey + 纸质备份 + 紧急恢复流程文档 |
| **Trust Ring 自身崩溃**（🆕 v0.7.0） | 高 | Ring 0 组件崩溃→签名验证失败→所有写操作被误判为非法 | Triple-modular redundancy：Ring 0 至少 3 个独立进程验证（agree≥2 才通过） |
| **Tamper-Evident chain 被 DoS**（🆕 v0.7.0） | 低 | 恶意 agent 制造海量审计事件撑爆 hash chain | 审计事件 rate limit——每秒最多 100 条；超过则降级为统计聚合 |
| **Bootstrapping 卡在 calibrated 出不来的状态**（🆕 v0.7.0） | 中 | 30 天内未收集到 100 个任务→永远不退出校准模式 | Owner 手动 exit-calibration + 使用 default 保守阈值（非 P95） |
| **信任根悖论**（🆕 v0.7.0 不可修复） | — | 整个系统是 AI 构建的——Ring 0 代码也是 AI 生成的。谁保证 Ring 0 代码没有 bug？ | **哲学上限**——100% AI 施工体系无法自证正确性。缓解：Ring 0 代码量最小化（< 200 行），Owner 逐行审计，Hash 冻结后不可再改 |

---
