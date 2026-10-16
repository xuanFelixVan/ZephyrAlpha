---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C05
name_zh: in-process 门禁链执行
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C05
---

# D11-C05 in-process 门禁链执行

## 1. 定义
提交车道第五环节（全图门禁密度最高节点，purpose_tags 12 标签全中，30d 触发 189273 次）：进程内门禁链。决策问题=「本改动按 priority 逐台过了门禁册登记的 in-process 门禁吗？（数量以册 total_gates 字段为准）」机制=in_process_gate_registry.yaml 动态注册（gate_auto_registrar）+锁外预跑/锁内指纹采信（gate_preflight）+结果缓存+漂移观察；worktree 跳过面 _WORKTREE_SKIP_GATES；审批判定收敛器=approval_resolver（marker 防伪[查无即拒]+裁定册授权+都不命中三通道）。

## 2. 六向台账

### 2.1 输入面
- 本提交文件集+staged 指纹（write-tree/HEAD/flags mtime 三元 F）
- 双册：`docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`（total_gates=107，2026-10-15 实查字段值=条目实扫=107）+config/flags.yaml（gate_preflight enabled=true production）

### 2.2 输出面
- 逐台 gate 结果+阻断状态（exit 3/5/6/8/9 五码出口）
- 预检审计：`.runtime/audit/preflight_events.jsonl`（实查在盘；图记 924KB@09-25）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C05`（wired/production，gate_cluster=in_process，machine_facts.gate_registry_facts 双计数一致）
- 骨架：05_门禁链与precommit通道.md（99 条目明细=叶层 INV-1 不进图）

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/gate_auto_registrar.py`（动态注册，实存在盘）
- `git_commit_gateway.py:375` `_preflight_flag_enabled`+`:2879` 预检入口+`_check_gates_with_drift_watch`（门禁链窗口注释 :42）
- `src/zephyr/gov_enforcement/commit_gates/approval_resolver.py`（_strip_worktree_prefix 单数形态治本 5611dbf3ca）+`create_guard.py:728` anchor_main_root（主区盘面=登记即时真源，#ARCH-324 先例）
- FORGED-GW-MARKER 亦挂本册（in_process 册 :49 实读）

### 2.5 门禁约束
- 本环节即门禁本体；own-scope 作用域铁律（宪法 §3：内容扫描型 gate 默认 own-diff；own_scope 字段册面无——priority/own_scope 真源在代码 GateSpec，O-C12 在案）
- 治本变更门=六门阻断硬闸（exit 1 处方）

### 2.6 自动化触发
- 提交流程自动逐台执行；锁外预跑+缓存命中采信（漂移即重跑）；30d 触发 189273 次（图 trigger_facts）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 文件集+指纹+双册实存 |
| 输出面 | pass | 五码出口+preflight 审计在盘 |
| SSOT真源 | warn | 册面 107=实扫 107 一致；但挖矿骨架行「91 门」无实指（rule_enforcement 包内 GateSpec( 构造实查=0，全 gov_enforcement GateSpec 出现 219 处）——91 为过期计数待骨架勘误 |
| 代码模块 | pass | 四模块实存+行锚在位 |
| 门禁约束 | pass | own-scope/六门阻断/防伪三通道在码 |
| 自动化触发 | pass | 预跑/缓存/漂移观察全自动 |

## 4. 缺口与建议
- 【计数勘误】「91 门」(骨架 C05 代码指针列)与册面 107 并存，建议骨架回写统一为「以册 total_gates 字段为准=107」；同时 gate_registry 生成器注释「in-process ∩ pre-commit 交集 0」已过期（实测交集 1 台 GATE-VOCAB 双执行，O-C10 在案）应一并修。
- 【建议】107 台中 zero_trigger_gates 6 台（GATE-ARCH/GATE-NAMING-AUDIT/GATE-FRONTMATTER-AUDIT/GATE-BP-PLACE/GATE-DEDUP/ISSUE-RESOLVED-INTEGRITY，30d 零触发）——按内收判据 w5_1「零触发零消费→退役」应逐台评估，注意零触发≠零消费（131/134 有 consumer）。
