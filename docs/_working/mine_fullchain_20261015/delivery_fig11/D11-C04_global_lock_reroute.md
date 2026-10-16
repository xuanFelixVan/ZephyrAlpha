---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C04
name_zh: 全局串行锁与锁争用改道
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C04
---

# D11-C04 全局串行锁与锁争用改道

## 1. 定义
提交车道第四环节：单写者串行化。决策问题=「全局锁拿到吗？拿不到是等待还是自动改道入队？」机制=_GlobalCommitLock（.ailocks/git_commit_global.lock，TTL=1800s）单写者串行，gate→stage→commit 不可分割；锁超时 AUTO-ENQUEUE 自动改道 pending（flag commit_queue_interactive，前置=非 --no-auto-enqueue ∧ 非 --reconciler-verify ∧ 非 --merge-finalize）；显式 --wait 同步占锁语义保留。

## 2. 六向台账

### 2.1 输入面
- commit 请求（直连语义）
- 争用信号：锁文件占用/TTL 剩余
- flag 面：`config/flags.yaml` commit_queue_interactive（enabled=true production，2026-10-07 C300 销账注记在册）

### 2.2 输出面
- 锁失败→CommitStatus.LOCK_TIMEOUT（exit 2，auto_enqueue=true）→改道入队（C08）
- 降级审计：`.runtime/gate_audit/commit_lock_fallback.jsonl`（图实查在盘）；阻断事件：`.runtime/audit/commit_block_events.jsonl`（实查在盘）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C04`（wired/production，MOD-INF-035，exit_codes=[2]）
- laws：队列是正门（锁争用不空转；直连与队列不混抢）
- 规则：`docs/01_policies_and_standards/rules/trae_079_commit_serialization.yaml`（consumer 在案）

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:672` `class _GlobalCommitLock(`（图记 :495，行锚漂移 +177；INVARIANTS :8 TTL=1800s；k=4 池期按 project_root 键控→门禁段真并行）
- `scripts/git_commit.py:1266` --no-auto-enqueue+`:1343-1434` 改道判定段（_contention_auto_enqueue+LOCK_TIMEOUT 判别实读）

### 2.5 门禁约束
- 挂门 COMMIT-CRITICAL-SECTION-LOCK（图 trigger_facts：30d 零触发）——见自审 warn
- exit 2 处方：仅 LOCK_TIMEOUT 支自动改道（三前置取反），STASH_CONFLICT 同码不自动

### 2.6 自动化触发
- 锁超时→自动入队（flag ON 默认）；锁 TTL 超时自解；探针=读锁文件（:1343）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 请求/争用/flag 三输入实存 |
| 输出面 | pass | exit 2 改道+双审计文件在盘 |
| SSOT真源 | pass | 图/规则/laws 齐 |
| 代码模块 | pass | 锚点实存（行锚漂移 +177），改道判定段实读一致 |
| 门禁约束 | warn | 挂门 COMMIT-CRITICAL-SECTION-LOCK 30d 零触发与锁每次提交必经相矛盾，疑 gate 触发计数口径空转（待对账） |
| 自动化触发 | pass | 超时改道+TTL 自解全自动 |

## 4. 缺口与建议
- 【计数对账】COMMIT-CRITICAL-SECTION-LOCK 零触发计数来源（f5_trigger_facts 聚合）与锁的真实使用频率对不上，建议查 trigger 口径（是 gate 判定计数还是 gate 阻断计数）——若为阻断计数则零触发=健康，应改注记免误读。
- 【建议】TTL=1800s 与 --wait 上限 1800s 同值，长 --wait 会顶满 TTL；建议 exit 2 处方补一句「--wait 不得超过锁 TTL」。
