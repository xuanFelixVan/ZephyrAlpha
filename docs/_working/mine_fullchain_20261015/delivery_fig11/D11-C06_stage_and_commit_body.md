---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C06
name_zh: 暂存与提交本体
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C06
---

# D11-C06 暂存与提交本体

## 1. 定义
提交车道第六环节：git 动作的机械本体。决策问题=「gitignored-tracked 怎么分离？rename 检出与 [GW:] 尾标防伪谁守？」机制=_commit_locked：gitignored-tracked 分离、pathspec-from-file add/rm、rename fallback（_has_staged_renames 检出 R100 自动切无 pathspec+_verify_staged_is_clean）、--no-verify -F msg 提交+[GW:<sid>] 尾标；FORGED-GW-MARKER 门禁守伪标。

## 2. 六向台账

### 2.1 输入面
- 过完 C05 门禁链的提交意图（message 文件+target_files+session_id）
- 索引卫生输入：两把 index（主区/临时）状态

### 2.2 输出面
- dev 上带 [GW:<sid>] 尾标的 commit（hash 回填 CommitResult）
- 索引卫生审计：`.runtime/gate_audit/gateway_index_hygiene.jsonl`（图实查在盘）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C06`（wired/production，gate_cluster=gw_marker_chain，exit_codes=[1,10]）
- 骨架：05_门禁链与precommit通道.md

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:3514` `def _commit_locked(`（图记 :2971，行锚漂移 +543）
- 同文件 `:56`（code 锚 _commit_with_file_message 注记）+`:1323`（rename fallback 调用段）+`_has_staged_renames/_verify_staged_is_clean`（INVARIANTS :8 实读语义在案）
- FORGED-GW-MARKER：in_process 册 :49 在册（gate_id 引用不抄正文）

### 2.5 门禁约束
- gate_refs=[FORGED-GW-MARKER]（30d 触发 607 次）：手写 [GW:] 判 forged→POST-COMMIT-GUARD reset 回滚（宪法 §9.8）
- 环境变量契约：ZEPHYR_COMMIT_GATEWAY=1+in_commit_flow 守卫（C01）

### 2.6 自动化触发
- 门禁链放行即自动暂存提交；rename 场景自动降级 fallback；失败自动走 exit 1/10

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 门禁放行后的提交意图契约清晰 |
| 输出面 | pass | [GW:] commit+卫生审计在盘 |
| SSOT真源 | pass | 图/骨架一致 |
| 代码模块 | pass | 锚点实存（行锚漂移 +543） |
| 门禁约束 | pass | FORGED-GW-MARKER 在册高频触发 |
| 自动化触发 | pass | 全自动+fallback 自动 |

## 4. 缺口与建议
- 【行锚滞后】gateway 漂移 +543 同 S09 建议：批量重扫。
- 【观测建议】_commit_locked 的 gitignored-tracked 分离正确性依赖 .gitignore 与册面一致，建议在 C13 观测面加一条「分离事件计数」，异常升高即 .gitignore 漂移信号。
