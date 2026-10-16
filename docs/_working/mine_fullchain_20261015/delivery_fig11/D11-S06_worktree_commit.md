---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-S06
name_zh: 会话内 worktree 提交
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-S06
---

# D11-S06 会话内 worktree 提交

## 1. 定义
会话车道第六环节：worktree 内的提交段。决策问题=「worktree 内 commit 前，base 新鲜/stash 留痕/DCR/门禁子集四段都校齐了吗？」路径=base 过期自动对齐（防搭便车提交）→HELD-OVERLAP gate→DCR 检测（fail-closed）→worktree-compatible 门禁子集（跳过 _WORKTREE_SKIP_GATES）→直接 git add+commit（独立 index 不占全局锁）。

## 2. 六向台账

### 2.1 输入面
- session 变更文件集（_sync_files_to_worktree 同步）
- base 新鲜度输入：worktree HEAD vs 主工作区 HEAD 比对
- stash 恢复通道输入：`.runtime/workspace_alerts/stash_notice.json`（实查在盘）

### 2.2 输出面
- worktree 分支上的 [GW:] commit；堵点归因判定链（_wt_block_gate_id 直取 gate_results[0].gate_id，红蓝 v3 P1-2 治本）
- 门禁跳过审计：`.runtime/gate_audit/worktree_skip.jsonl`（实查在盘）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-S06`（wired/production，gate_cluster=worktree_compatible_subset）
- 骨架：`docs/_archive/_working_cleared/map_build/fig11_delivery/02_claim协议与暂存晋升.md`

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:4709` `def session_worktree_commit(`（图记 :4580，行锚漂移 +129）
- 同文件 `:3438` `_ensure_worktree_base_fresh`（图记 :3312；无 session commit→reset --hard 安全对齐，有→rebase 冲突 fail-loud）
- 同文件 `:369` `_WORKTREE_SKIP_GATES = frozenset({HELD-OVERLAP, CLAIM-REQUIRED, FOREIGN-CHANGE-DETECTION, WORKTREE-REQUIRED})`（单一真源，禁硬编码注记在 :371）
- stash 留痕：`:7455` `_write_stash_notice`（图记 :5254/:7261 语义段仍在）

### 2.5 门禁约束
- gate_refs=[WORKTREE-REQUIRED]（图面）；实际消费=worktree-compatible 门禁子集（数量以 _gate_registry 实际注册为准，裁定 D 治本禁硬编码）
- DCR fail-closed：subprocess 调 check_directory_contract.py（对标网关 DIRECTORY-CONTRACT gate，治本 ARCH-041 绕过）

### 2.6 自动化触发
- 提交请求触发全四段校验；base 过期自动对齐；gate 异常降级 warn 不阻断；stash 操作自动写 notice

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 同步/比对/恢复三输入实存 |
| 输出面 | pass | worktree_skip.jsonl 在盘留痕 |
| SSOT真源 | pass | 图/骨架一致 |
| 代码模块 | pass | 四锚点实存（行锚漂移 +129/+126） |
| 门禁约束 | pass | 跳门名单单一真源+DCR fail-closed 在码 |
| 自动化触发 | pass | 四段全自动+stash 自动留痕 |

## 4. 缺口与建议
- 【行锚滞后】同 S02/S04；建议生成器对 source_anchors 重扫。
- 【观测建议】worktree 内门禁子集跑的是 monkeypatch 后的网关（run_git 重定向 cwd），其通过/阻断计数未见独立聚合出口，建议并入 C13 观测面分车道出数。
