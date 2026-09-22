---
ttl: task_bound
---

# 环节7：队列可观测面（status/租约/等待方视角）

> 挖矿：主会话亲挖（子代理限流阵亡）+ 环节2/3 子代理证据融合。

## A 现状清单

- `queue_status`（commit_queue.py:1456-1490）：读 pending/processing/done/dead 四目录 JSON，输出 counts+items（qid/session_id/state/created_at，dead 附死因，done 附 landed_id）；**--session 过滤；完全不读租约**。status CLI 调用前还先试排空（:1743）。
- 租约文件三键 pid/acquired_at/renewed_at：queue_status 零消费；renewed_at 生产零读者（仅测试）。
- 仪表盘：frontend/dashboard/components/ 有 gate_statistics/task_progress/qmt_bridge_health 等，**无队列深度/租约面板**。
- 其他观测物：health CLI（queue_health：四态计数+死因分类+最老项龄）、bottleneck_ledger.jsonl（daemon 死后断流）、main_workspace_sync.jsonl、health_alert_state.json、task_board 死信标签。

## B 等待者痛点（09-21 实录反推）

1. processing=0 + 队列"健康"但租约被占——status 视角与全局真相脱节（等待会话被迫 cat 租约+Get-CimInstance 查 pid 命令行反推）。
2. 无队列位置感：我的 5 项前面还有几项、队首是谁在磨多久——全部不可见。
3. 无 ETA/趋势：不知道该等还是该改用 worktree 直改。
4. 盲轮询节奏靠猜（sleep 300-540）。

## C 升级机会（=R5 施工蓝本）

1. 【快】queue_status 增三块（全部读现存文件，零新扫描）：
   - `lease`: {holder_pid, alive, acquired_age_s, renewed_age_s, over_ttl, state: "drain-active"|"stale"}（读 serializer.lease+is_pid_alive）；
   - `head`: {qid, session_id, files, created_at, waiting_s}（队首项）；
   - `mine`: --session 时每项给 `position_ahead`（FIFO 序=文件名排序中的前驱 pending 数）。
2. 【快】belt_daemon.lock 存在性探测 → `daemon: "online"|"offline"` 键（环节3 E6：补位消费者离线提示）。
3. 【快】"processing=0 但租约被持"时 state 标注 `drain-active(在途未取项)`，消除误导。
4. 🌑 ETA 预测（历史时长回归）：数据不足+统计口径争议——挂起，先给 waiting_s 原始量。

## D 自审闸三态裁定

施工：C1-C3（Owner R5 原文）+daemon 在线键。挂起：ETA。
