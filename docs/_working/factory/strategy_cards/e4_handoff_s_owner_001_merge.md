---
ttl: task_bound
completes_when: 分支 ai/st-sowner001-20260916/s-owner-001-300etf-band-t 合并回 dev 后本交接包归档。
---

# E4 考试收尾交接包 — S-OWNER-001（st-sowner001-20260916）

- 状态: 考试已完结（verdict=FAIL，裁定 #293 已登记），**仅剩分支落库一步**。
- 分支: `ai/st-sowner001-20260916/s-owner-001-300etf-band-t`（基点 2bdc9f074a，2 个 commit）：
  - `b4c3c6f26d` 实现+冻结文档+注册表登记（19 文件）
  - `23ed6ef080` 出证报告+考试产物+裁定 #293 原子登记（5 文件）
- 阻断原因: 合并时 dev 主区有他会话未提交文件（sharpe2_prep/pipeline-research/trading_vision 等
  _working WIP，与本分支无内容冲突，纯 index 写入受阻）。按 owner 责任制不代修不 stash。
- **合并指令（主区净窗时执行）**:
  `echo yes | python scripts/session_worktree.py merge st-sowner001-20260916`
  或直接 `git merge ai/st-sowner001-20260916/s-owner-001-300etf-band-t`。
- 注意: 主区 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` 若已被
  他车道追加 #293+，合并时以"编号不撞、双条目并存、按时间序"为准（本分支 #293 与他道条目
  不冲突即可，若他道也占了 #293 则后者改号）。
- worktree: `.worktrees/st-sowner001-20260916`（合并确认后可 abort 清理；.runtime/tmp/sowner001_cache
  为数据 parquet cache，可删，产物已 commit 不依赖 cache）。
