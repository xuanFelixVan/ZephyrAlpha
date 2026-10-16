---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-S02
name_zh: worktree 分配与池化
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-S02
---

# D11-S02 worktree 分配与池化

## 1. 定义
会话车道第二环节：为会话分配隔离施工 worktree。决策问题=「本会话 worktree 从哪来？池 lease 还是直接创建？并发阻断怎么判？」路径=session_worktree_start 原子注册→优先 WorktreePool.lease（失败 fall back 直建，池永不阻断启动）→lease 后异步 prefetch 补池；breaking_change 双向并发阻断。

## 2. 六向台账

### 2.1 输入面
- 启动请求（session_id/worktree 根/breaking_change/allow_concurrent 参数）
- 并发阻断判据：`src/zephyr/security/access_control/session_concurrency.py`（find_breaking_change_session 只读查找活跃 breaking 会话，INVARIANTS :8 在案）
- 首 claim 指路输入：`scripts/lock_files.py:1801` `_deliver_first_acquire_guide`（首次 acquire 弹施工 playbook 锚点，fail-open）

### 2.2 输出面
- 会话 worktree 目录：`.aidrafts/<sid>/`（2026-10-15 实查 2 个在途会话 worktree）
- 池目录：`.aidrafts_pool/`（实存在盘）
- 上户口合一入口：`scripts/governance/register_asset.py`（实存在盘，裁定#480 C-2：creation_token/大白话/depgraph 五道手续一条命令）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-S02`（wired/production）
- 骨架：`docs/_archive/_working_cleared/map_build/fig11_delivery/01_会话启动与worktree池.md`
- 政策真源：`docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md`（隔离施工默认制）

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:2663` `def session_worktree_start(`（图记 :2607，行锚漂移 +56，符号在位）
- `src/zephyr/gov_enforcement/rule_bridge/worktree_pool.py:277` `def lease(self, session_id)`（行锚一致；INVARIANTS 记载 P3.3 池化+prefetch_async 补池）
- `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:15`（INVARIANTS：lease 经 git worktree move+分支重命名瞬时返回，消除 add 开销 2-5s/Windows）

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=并行协调政策 §10（降级直改=显式申请制）+breaking_change 双向阻断（BREAKING_CHANGE_CONCURRENCY_BLOCKED / BREAKING_CHANGE_AVOIDANCE_BLOCKED，异常 fail-open 降级放行）

### 2.6 自动化触发
- 池 lease+prefetch 全自动（daemon 线程异步补池）
- 孤儿辅助脚本自动清理：session_worktree_start 顺带清 .aidrafts/ 根 age>1h 的 `_*` 文件（_cleanup_orphan_draft_scripts）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 启动参数+并发阻断判据实存 |
| 输出面 | pass | .aidrafts 2 worktree+.aidrafts_pool 在盘 |
| SSOT真源 | pass | 图/骨架/政策三层齐 |
| 代码模块 | pass | 四锚点全实存（session_worktree_start 行锚漂移 +56） |
| 门禁约束 | pass | 政策 §10+双向阻断在码 |
| 自动化触发 | pass | 池化 prefetch+孤儿清理自动 |

## 4. 缺口与建议
- 【行锚滞后】图 source_anchors 停在 2026-09-25 快照（:2607），现值 :2663——session_worktree.py 高频演化文件，建议生成器对 source_anchors 做重扫刷新或标注快照日期。
- 【观测面】.aidrafts 在途会话数从 12（09-25）降至 2（今日），池周转健康；建议 health 面补一条 worktree 池水位指标（pool 剩余/lease 命中率）。
