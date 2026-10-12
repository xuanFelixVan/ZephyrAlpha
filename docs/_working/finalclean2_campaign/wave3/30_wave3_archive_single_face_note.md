---
ttl: task_bound
completes_when: 维护三班确认 session_worktree archive 的双树覆盖面
---
# 终清波三·收班实测：归档器只清一面（新文件追加册，不碰已落地块）

**事实（20:1x 本班收班实测）**：`session_worktree.py archive st-fclean3-20261012 --execute` 判型 `zero_loss`、
执行成功并回报"worktree 已从注册表消失／branch -d 已删（壳分支）／session 已注销"，但复核盘面：
- `.aidrafts/st-fclean3-20261012` **已消失** ✓、`session/st-fclean3-20261012` 壳分支已删 ✓；
- ⚑ `.worktrees/st-fclean3-20261012` **仍在**（整棵 checkout 体量滞留），且 `ai/st-fclean3-20261012/task-finalclean3-sweep`
  分支仍在（实测 HEAD 为 dev 祖先＝纯冗余，但对外看着像"活分支"）。
- 回报里的 `路径: D:\ZephyrAlpha\.aidrafts\...` 说明它按 `.aidrafts` 那一面对象作业，**不覆盖 `.worktrees` 面**。

**为什么会撞上**：这正是本班今夜报的根因——同一会话被两套工法各开一棵树（`create` 开 `.worktrees`＋心跳/会话机制在 `.aidrafts` 另立一面）。
本班 §四-5（`lane_aidrafts.md`）量过该双轨每轮净增 ≈297 MiB/20,540 件；收班时它以另一形态复现：**归档只收一半，剩一半变成新的待体检遗留面**。

**给维护三班的两条口径（不属本班权限，不自改）**：
1. `archive` 的收尾完整性判据建议含"该 sid 的**所有** worktree 面（`git worktree list` 全枚举）与**所有**分支
   （`ai/<sid>/*` 与 `session/<sid>` 两族）均已消失"，否则回报不应写"已归档"；
2. 或直接把"停发第二棵树"（本班 M9 双轨收敛项）作为前置——单树会话下本问题天然消失。

**本班自清动作**：`.worktrees` 面按在册正解处理＝`git worktree remove`（**禁裸 rm**，本册 §四-1 已证该面含注册工作树管理件）
＋ `branch -d`（仅在 HEAD 为 dev 祖先时执行，实测前置成立）。本班交付 22 件在 dev 上不受影响（移除前后各核一次）。
