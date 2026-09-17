---
ttl: task_bound
completes_when: GATE-ALGO-FLOW-REVERSE-ORPHAN 注册且反向孤件退役包被 Owner 裁定授权并落地
title: B 环节台账——ALGO_FLOW 反向孤件 reconciler（#ARCH-326 治本）
owner: ZephyrAlpha-Owner
session: st-anchorfix-20260918
date: 2026-09-18
---

# B：反向孤件 reconciler 环节台账（#ARCH-326）

## 目标

把 2026-09-18 一次性反向孤件普查固化成常驻事件触发观测面，并按裁定#307① 的 Owner
门位形态给出可执行的退役出口。#ARCH-326 `fix_phase` 已指定归属：并入 d8_doc_sync
事件触发对账，不进 pre-commit（3227 件全库扫描属触碰税，perf 方案 §2.6 分级不允许）。

## 证据（施工前实测）

- `src/zephyr/infrastructure/model_capability_exam/*` 在 HEAD 树与盘上双双缺失（源退役于 `6a0eca4700`）
- 镜像 `docs/03_modules/_domain_infrastructure/algo_flow/model_capability_exam/model_capability_exam__init__.yaml` 仍 tracked
- `capability_canonical_file_registry.yaml` creation_tokens 条目（token `btfix-p1p2-model-capability-exam--init---20260916`）仍在
- `git grep -l -F <镜像路径> HEAD -- '*.py'` 空 → 无反向锚点，孤件成立
- 现存镜像总数 3232（普查时点 3227），全库普查耗时 1.07s

## 块（落地件）

| 件 | 作用 |
|----|------|
| `scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py` | 普查判据 + Owner 授权退役通道（`--apply`） |
| `git_commit_gateway.py` d8_doc_sync 插件段 | 注册 GATE-ALGO-FLOW-REVERSE-ORPHAN（priority=245，传 gateway 而非 project_root） |
| `tests/scripts/governance/d8_doc_sync/test_algo_flow_reverse_orphan_reconciler.py` | 29 例：真 git 仓判据 + 4 条撤护栏变异证明 |

## 三态

- **检测面（已落）**：`file_ops={"read"}`，reconcile 只普查不删——判据三要素全真才判
  （HEAD 树缺失 + 盘上缺失 + 源确有 `--diff-filter=D` 退役提交），反向锚点命中即否决；
  命中 → `critical_warn` + `.runtime/reconcile_reports/algo_flow_reverse_orphan_*.json`
  + 可复制的退役命令。
- **退役面（等门位）**：`--apply --mirror <rel> --owner-ruling <NNN>`。授权凭据机判
  = ruling_registry 里一条 status=active 且正文点名该镜像的裁定（宪法 §9.11：对话
  口头批准不构成门禁豁免）。执行序：复核孤件 → 回收站收纳镜像（永不物理删除）→
  creation_tokens 段内锚定 CAS 摘条 → 写后进程外自检（末位键/条目数/残留）→ 不过即
  回滚 → `_commit_auto` 同批落地（信息带 `[allow-mass-deletion:…]` + `[RULING-REFERENCE:]`）。
- **依赖**：`batch_creation_tokens._creation_tokens_section`（段边界单点，防死区锚点
  漂移）、`ops_guard.guard_recycle`/`set_reconciler_context`、`file_utils.safe_write_text`。

## 下一步（W3 收口路径）

1. 登记一条 Owner 裁定（承接 09-18 对话中 Owner "批准删除"）正点名该镜像 → 状态 active；
2. `python scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py --apply
   --mirror docs/03_modules/_domain_infrastructure/algo_flow/model_capability_exam/model_capability_exam__init__.yaml
   --owner-ruling <新裁定号> --session st-anchorfix-20260918`（先 `--dry-run` 复核演算）；
3. 落地后 GATE-ALGO-FLOW-REVERSE-ORPHAN 下轮触发应转 `clean`，#ARCH-326 议题可关闭。

## 事故记录（施工期）

首次插入 `git_commit_gateway.py` 注册块被 `st-tdchain` 的 `session_worktree_pre_merge`
全量 stash 扫走（`stash@{0}`，tdchain-sweep12），表现为"注册后 reconciler 数不增且无
warning"。按宪法 §2.8 查 `.runtime/workspace_alerts/stash_notice.json` 定位为 stash 而非
覆盖；未 pop 他会话 stash（避免吸收其 WIP），改为重放同一插入并当分钟出小批落地。
