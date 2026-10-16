---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-S07
name_zh: 合并回主区（merge 正门）
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-S07
---

# D11-S07 合并回主区（merge 正门）

## 1. 定义
会话车道第七环节：worktree 成果并回 dev 主区。决策问题=「现在能 merge 吗？HIGH drift 与 commit 后新增门禁规则挡不挡？」双检设计=_run_pre_merge_topo_check（HIGH drift 阻断，checker 缺失 fail-closed/DB 不可用 fail-open）+_pre_merge_gate_check（reset --soft 模拟 staged 重跑 worktree-compatible 门禁）；**现行行为=常量 _PRE_MERGE_SKIP_ALL_COMMIT_GATES=True 使门预演默认整体短路，只保留 TOPO-CHECK**（图重大加注在案）。

## 2. 六向台账

### 2.1 输入面
- session 分支 commits（S06 产物）
- merge 请求（session_worktree_merge，--no-ff+_WorktreeLock 串行化）
- finalize 配套：`scripts/git_commit.py:1053` --merge-finalize（拒 MERGE_HEAD 晾置，exit 10）

### 2.2 输出面
- dev 上的 merge commit；reconcile_verify 默认 True→merge 后自动触发全部已注册 reconciler（_run_reconcilers_after_merge，补 path_ownership/depgraph_ops 等漂移）
- force 审计：`.runtime/gate_audit/force_merge_usage.jsonl`（图实查在盘）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-S07`（build_status=built、wiring_status=partial、red_reason=unwired——「代码在盘而默认不跑」的如实记法）
- 骨架：`docs/_archive/_working_cleared/map_build/fig11_delivery/03_merge回主区与收尾.md`（骨架状态列仍 ✅ 未回写 partial）

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:391` `_PRE_MERGE_SKIP_ALL_COMMIT_GATES = True`（图记 :389；消费点 :7273-7274：force 或本常量为 True 即跳所有 commit gate）
- 同文件 `:6889` `def session_worktree_merge(`（图记 :6714）；`:6160` TOPO 检不受跳过权支配的说明段
- _run_pre_merge_topo_check/_pre_merge_gate_check 在位（subprocess 调 MAIN 副本 check_blueprint_code_alignment.py --scan-root）

### 2.5 门禁约束
- gate_refs=[WORKTREE-REQUIRED]；gate_cluster=pre_merge_topo_check
- 运行事实：pre-merge 门禁覆盖面收窄为 TOPO-CHECK 独苗（补位机制=落地侧 commit_queue_landing「门禁一套不裁」全链照跑）

### 2.6 自动化触发
- merge 请求触发 topo 检查（HIGH drift 阻断）；merge 后 reconciler 自动触发

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 分支产物+finalize 配套在位 |
| 输出面 | pass | merge+reconciler 自动触发+审计面 |
| SSOT真源 | warn | 图已如实记 partial+加注，但骨架状态列 ✅ 与图 partial 并存未清（转性归总包） |
| 代码模块 | pass | 全锚点实存（行锚微漂 +2/+175） |
| 门禁约束 | warn | 门预演默认短路=覆盖收窄是运行事实，补位仅靠落地侧全链 |
| 自动化触发 | pass | topo 检查+reconciler 触发自动 |

## 4. 缺口与建议
- 【账务收口】骨架 S07 状态列应回写为 partial（与图对齐）；现行短路是 ImportError 假阻断的权宜，建议立项「主区 sys.path 与 worktree 代码版本错位」治本后恢复双检。
- 【依赖说明】merge 侧门禁收窄的安全性论证（落地侧全门禁链兜底）建议写进并行协调政策，防后续会话误判 merge 免检。
