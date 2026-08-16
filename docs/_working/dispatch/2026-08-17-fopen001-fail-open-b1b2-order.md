---
ttl: task_bound
---

施工会话 AI-FOPEN-001。任务：fail-open 敞口治理 B1+B2 全量落地（Owner 2026-08-17 裁定，tracker #116，方案真源=docs/_working/reports/2026-08-17-fail-open-analysis.md，当前无并发施工会话）。
worktree 已由统筹创建：D:\ZephyrAlpha\.worktrees\AI-FOPEN-001（分支 ai/AI-FOPEN-001/task-fail-open-b1b2，自 dev 5f141ad75a 切出）。进入后 `. .\activate_env.ps1`。

背景：
- 报告逐点实证：PG 离线时 5 个 depgraph 类硬阻断门禁静默放行，#1/#2/#3/#5 仅进程内 warning、commit 成功后零追账锚点=真实敞口。Owner 裁定 B1+B2 全量：放行可留痕可追账+探针区分"DB 离线"vs"真无违规"。
- 既有先例（直接对齐，禁另造机制）：#4 panorama_alignment_gate 的 log_gate_failure（src/zephyr/governance/audit/reconciliation_registry.py L1357，写 sqlite reconcile_execution_log，下次 commit 网关 banner 自动浮现；调用先例=commit_gates/panorama_alignment_gate.py L113-198）。

范围（三项，逐项真源引用）：
1. **B1 核心——4 个 gate 的 fail-open 分支统一接 log_gate_failure 持久化**（保持放行语义不变，只加留痕）：
   - #1 RENAME-DEPGRAPH-SYNC：src/zephyr/gov_enforcement/commit_gates/rename_depgraph_sync_gate.py L141-159/L189-191（except→return None→continue 分支）
   - #2 NEW-FILE-DEPGRAPH-ENFORCEMENT：src/zephyr/gov_enforcement/commit_gates/new_file_depgraph_gate.py L184-199/L247-249（except→None→continue 分支）
   - #3 DEPGRAPH-PRE-REGISTRATION：src/zephyr/gov_enforcement/commit_gates/depgraph_pre_registration_gate.py L184-200/L221-223（None≠"planned"→skip 分支）
   - #5 PRE-MERGE-TOPO-CHECK：src/zephyr/gov_enforcement/rule_bridge/session_worktree.py L6414-6614（module_ids==0/超时/exit 2/JSON 失败→降级放行四分支；checker 缺失才 fail-closed 的分支不动）
   - 顺手项：scripts/governance/d11_compliance/verify_schema_health.py L324——连接调用移入 try 块，PG 离线从"未捕获异常崩溃式阻断"转"明确告警阻断"（含错误码与引导文案）
   - 留痕语义统一：critical_warn 级+gate_id+放行原因（DB 离线降级）+受影响文件清单，与 #4 同款签名；同签名当日去重（防 PG 长期离线告警疲劳，对齐报告 §3 缓解条）
2. **B2 增强——PG 可用性前置探针**：
   - D1 查重先行：Grep 全仓既有 PG 探活（rule_engine/rule_engine.py L189-202 PG 探测先例、depgraph_scan_cache、redis_config 式单真源模式），有则复用扩写，无则新建最小探针模块（建议 src/zephyr/governance/ 内，走 creation_token 全登记链）
   - 探针产出：.runtime/pg_probe_state.json {reachable: bool, checked_at: ISO8601}——网关 commit 前置执行（TCP 5432 连接，≤1s 超时，失败不阻断只落状态）；post-commit reconciler 可复跑刷新
   - gate 读取联动：#1/#2/#3/#5 的留痕分支读探针状态——探针离线→"DB 离线降级"留痕放行（B1 路径）；探针在线而 gate 自身连接失败→真实错误按原语义上报（不静默）
   - DEPGRAPH-FRESHNESS 豁免：src/zephyr/gov_enforcement/commit_gates/depgraph_freshness_gate.py——探针离线超 24h 时豁免 saved_at 停更误伤（报告 §1.3 联动修复），离线期豁免留痕
3. **测试**：4 gate 各一组"DB 离线→放行+log_gate_failure 落盘可断言"用例（monkeypatch 连接 raise）；探针状态文件读写/陈旧判定/豁免联动用例；verify_schema_health 优雅阻断用例；既有 commit_gates/session_worktree/panorama 套件零回归

避让：
- 无并发施工会话，但主仓 reconciler/watchdog 活跃——Tracked 区改动全走本 worktree
- reconciliation_registry.py L1357 log_gate_failure 本体只调用不修改；governance.db schema 不动
- fail-open 报告本身（docs/_working/reports/）不动；tracker/handoff 统筹面不碰

验收：①新增测试 2 轮全绿+tests/governance 关联套件零回归（基线 10 项存量失败 #115 同集不扩大）②红队实证：PG 真实停服模拟（或 monkeypatch 等效）→4 gate 放行且 sqlite 留痕可查询+下次 commit banner 浮现；探针在线而 gate 连接失败→不静默；探针离线 24h+→FRESHNESS 豁免 ③verify_schema_health PG 离线→明确告警阻断（非崩溃栈） ④Step 1+Step 6（14 节版）双 PASS ⑤全走 GitCommitGateway（[GW:AI-FOPEN-001]）⑥新文件 creation_token+capability+translation+ARCH 引用（#ARCH-119）登记链齐全
完工反馈六要素：commit hash/Step 1/Step 6/测试轮次/改动清单/遗留项。worktree 保留待统筹统一 merge。
