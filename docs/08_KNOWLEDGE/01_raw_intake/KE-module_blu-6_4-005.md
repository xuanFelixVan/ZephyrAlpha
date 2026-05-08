---
module_id: KE-module_blu-6_4-005
title: 6.4 推荐施工路线（重排后）
category: module_blueprint
---

# 6.4 推荐施工路线（重排后）

6.4 推荐施工路线（重排后）

```
Phase 1 (scaffold — 立即，解决 B1/B2/B3 结构性问题):
  1. 数据模型统一决议：选 git-native + SQLite dump (B1/B3)
  2. 区分 revert(已commit) vs discard(未commit) 两套流程 (B2)
  3. RollbackExecutor + preflight_check + preview (B4/B5)

Phase 2 (experimental):
  4. Partial Revert 能力 (B7)
  5. Loop Detector + Agent Cooldown (B6/B8)
  6. 回滚队列 + Concurrency Serialization (B9)
  7. 失败信号分类器 (hard/soft/transient) (B15)

Phase 3 (beta):
  8. Rollback Simulator + Test Framework (B11)
  9. Rollback Metrics + MTTR Tracking (B12)
  10. Anti-Patterns 章节 (B19)
  11. Hard Reset token gating (B13)

Phase 4 (production):
  12. 1人运维 CLI (rollback status/stats/preview/cancel)
  13. Remote Sync 冲突处理 (B14)
  14. BREAK_GLASS adaption for rollback (B20)
  15. CT-RBK-GATE-001 集成契约落地 (B17)

Phase 5 (resilience):
  16. 幂等回滚执行器 + 状态机 (B43/B42)
  17. 定期回滚演练 + 混沌工程 (B41/B52)
  18. 三级 Kill Switch (B46)
  19. Forward-Fix 决策 + 对话上下文恢复 (B51/B44)
  20. 依赖感知 + JSONL 完整性保护 (B48/B49)
  21. 30 秒仪表盘 + 回滚预算 (B47/B55)
  22. Down-migration 生成 + Checkpoint GC (B45/B50)

Phase 6 (sovereign):
  23. 自举回滚器 + AI 幻觉防护 (B56/B57)
  24. 语义变形检测 + 依赖漏洞复扫 (B58/B59)
  25. Token 会计 + 温备热切 (B60/B61)
  26. 语义化 Tag + 分支拓扑回滚 (B62/B63)
  27. Git 基础设施防护 + GPG 签名链 (B64/B65)
  28. 密钥轮替感知 + 跨平台 Shell (B66/B67)
  29. venv 同步 + env 热重载 + 时间上下文修复 (B68/B69/B70)
  30. Owner 覆盖 + 网络分区超时 (B71/B72)
  31. S3 防过期 + 外部证明 + Submodule 同步 (B73/B74/B75)

Phase 7 (metacognitive):
  32. Prompt 注入过滤 + 声明式策略引擎 (B76/B77)
  33. GDPR 遗忘权 + 连接池重建 (B78/B79)
  34. 嵌套环境检测 + MCP 操作回滚 (B80/B81)
  35. 确定性重放 + 告警疲劳抑制 (B82/B83)
  36. 渐进式回滚 + git bisect 保护 (B84/B85)
  37. File Watcher 暂停 + Shallow Clone 恢复 (B86/B87)
  38. git notes 标注 + 软删除 trash (B88/B89)
  39. filter-branch 恢复 + 决策疲劳防护 (B90/B91)
  40. 跨 Vendor 同步 + 回滚反馈闭环 + 热力图 + 威胁情报 (B92/B93/B94/B95)

Phase 8 (forensic):
  41. 独立审计 Sidecar + git 二进制完整性 (B96/B97)
  42. Shell 注入全量审计 + 外部时间证明 (B98/B99)
  43. git bit rot 检测 + TOCTOU 双检 (B100/B101)
  44. TPM 硬件信任锚 + 原子化审计_write (B102/B103)
  45. in_flight GC + WAL 清除 + 决策可问责 (B104/B105/B106)
  46. reflog 备份 + git notes 沙箱 (B107/B108)
  47. 持续完整证明链 + 取证只读 snapshot (B109/B110)

Phase 9 (governance):
  48. Owner 心跳 + 死手开关 + 分级自治 (B111)
  49. Feature Flag 注册表 + flag_flip_undo (B112)
  50. LLM 模型版本契约 + 行为漂移检测 (B113)
  51. AI 置信度量化 + 低置信度降级 (B114)
  52. 回滚系统自复杂度分析 + 简化建议 (B115)
  53. Error Budget 自治门禁 (B116)
  54. git rebase/cherry-pick/am in-progress 检测 (B117)
  55. Commit Message 质量审计 + 最低标准 (B118)
  56. fail-open/fail-closed 声明式策略 (B119)
  57. 上下文窗口累积污染 + GC (B120)

Phase 10 (adversarial-security):
  58. Agent 执行沙盒集成 (Docker/Bubblewrap/E2B) (B121)
  59. 回滚系统自防卫 + 核心文件完整性强制校验 (B122)
  60. 回滚后 Runbook 自动生成 (B123)
  61. knowngoodstate 已验证正确状态收据账本 (B124)
  62. 回滚目标陈旧度风险评估 (B125)
  63. 回滚后凭据泄露检测 + 自动轮替 (B126)
  64. 回滚预写日志 (Rollback WAL) (B127)
  65. 多 Agent 文件冲突检测 + 广播 (B128)
  66. 操作意图存档 (Intent Archiver) (B129)
  67. 回滚系统武器化滥用检测 (B130)
```
