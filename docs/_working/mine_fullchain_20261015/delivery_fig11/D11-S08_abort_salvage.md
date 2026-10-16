---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-S08
name_zh: 放弃与死会话回收
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-S08
---

# D11-S08 放弃与死会话回收

## 1. 定义
会话车道第八环节：负出口处置。决策问题=「放弃任务或会话死了，产物怎么 salvage、claim 归谁释放？」双通道=abort 直通道（显式放弃）+lock_files cleanup auto-salvage（死会话自动回收：双证判死→merge abort+stash 归档+释放 claim，全程写 salvage_audit.jsonl）；死会话 stale claim 亦可经网关 release_files 精准释放。

## 2. 六向台账

### 2.1 输入面
- abort 请求（session_worktree_abort）
- 死会话判据输入：双证判死（三证旁证 collect_alive_side_evidence，宁可少判死、三证全空真死必判死——session_concurrency.py:13 MODIFY-GUARD）
- 队列待落项豁免：daemon idle 自退判据含「无队列待落项」（C355 豁免）

### 2.2 输出面
- salvage 审计：`.ailocks/salvage_audit.jsonl`（2026-10-15 实查 2937 行；图记 09-25 为 659 行，持续留痕）
- stash 归档件+claim 释放记录；abort 后 worktree 自删（store_refs：merge 后主仓吸收/abort 自删）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-S08`（wired/production）
- 骨架：`docs/_archive/_working_cleared/map_build/fig11_delivery/03_merge回主区与收尾.md`
- 政策：parallel_session_coordination_policy.md（死会话 stale claim 精准释放条款，宪法 §2.7）

### 2.4 代码模块
- `scripts/lock_files.py:1328` `def salvage_dead_session(`（图记 :1160，行锚漂移 +168）
- 同文件 cmd_cleanup（auto-salvage 幂等入口；本车道冷启动实跑输出 CLEAN+scanned=8/whitelist_hits=7）
- `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:7691` `def session_worktree_abort(`（图记 :7497，行锚漂移 +194）
- 精准释放：git_commit_gateway.release_files（宪法 §2.7 死会话处置正道）

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=「宁可留错不可删错」（salvage 只归档不销毁，stash 数据保留）+双证判死保守化（MODIFY-GUARD：判据分叉取更保守一侧）

### 2.6 自动化触发
- lock_files cleanup 幂等 auto-salvage（每次冷启动 RULE-GUARDIAN 步即跑）；判死→释放→归档全自动留痕

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 双证判死+豁免判据在码 |
| 输出面 | pass | salvage_audit 2937 行持续增长 |
| SSOT真源 | pass | 图/骨架/政策齐 |
| 代码模块 | pass | 三锚点实存（行锚漂移 +168/+194） |
| 门禁约束 | pass | 保守判死+只归档不销毁在码 |
| 自动化触发 | pass | cleanup 幂等入口本日实跑 |

## 4. 缺口与建议
- 【行锚滞后】同前。
- 【观测建议】salvage_audit.jsonl 永久追加（2937 行）无轮换口径，建议按年归档切片，防单文件无限增长拖慢 cleanup 扫描。
