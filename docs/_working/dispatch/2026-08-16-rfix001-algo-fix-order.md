---
doc_type: dispatch_order
ttl: task_bound
status: active
date: 2026-08-16
---

施工会话 AI-RFIX-001。任务：双轮审查算法修复批落地（裁定书 docs/_working/reviews/2026-08-16-dual-review-adjudication.md §二/§六）。
worktree 已由统筹创建：D:\ZephyrAlpha\.worktrees\AI-RFIX-001（分支 ai/AI-RFIX-001/task-algo-fix-batch，自 dev 4c287e18d7 切出）。进入后 `. .\activate_env.ps1`。

范围（逐项裁定书，F3 已由 RRESIL-001 施工不重复）：
1. F1 [P1] ES 线性插值致尾部样本抖动 → `method='lower'`+memo 36 §3.10 补插值口径裁定
2. F2+F4 [P1+P2] VaRCalculator 静默过滤 NaN+Inf → `np.isfinite` 过滤+nan_dropped 计数入 VaRResult+超阈值 raise
3. Qwen P1 群：
   a) 5 级仓位上限非单调（YELLOW 0.5→ORANGE 0.7 倒挂）→数值表修正
   b) 撤单计数未接线 → 接入 ASM-001 日申报硬计数器（CancelRateGuard，已有 production 实例）
   c) POT 小样本：60 日窗口+50% 负日常态→exceedances 仅 3 个 < 门槛 5，降级为"样本不足时跳过 POT 仅历史 ES"+验证降级路径告警
   d) D1-D9 文档-代码漂移清单 → 逐条对账，memo 36 修正或登记 CAND
4. F5 [P2] RegimeMeta 死代码两则 → 清理（数学证明不可达）
5. FHS 漂移：memo 36 §3.10 以可执行语气引用 `fhs_engine.enable()`，但 src 零匹配 → 裁定转"远期候选"明确语气，或登记 CAND-AUTONOMYCORE-002

避让：
- trading_session.py / risk_layer_orchestrator.py 已由 RWIRE-001 接线，你只修算法层不改动接线点
- fill_handler / PositionTracker / DefaultRiskValidator 已由 RRESIL-001 施工，你只读不碰内部（撤单计数接入点在外层 CancelRateGuard）
- tests/ 域 GOV-001 仍施工中（包③），你只新增/修改本任务域测试文件

验收：①新增测试 2 轮全绿+既有 risk/pf_alloc/ex_core 套件不回归 ②Step 1+Step 6（14 节版）双 PASS ③全走 GitCommitGateway（[GW:AI-RFIX-001]）④F1/F2 数值修正须有红队实证（构造小样本/NaN 注入场景验证行为变更）
完工反馈六要素：commit hash/Step 1/Step 6/测试轮次/改动清单/遗留项。worktree 保留待统筹统一 merge。