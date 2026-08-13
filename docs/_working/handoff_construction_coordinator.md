---
title: 施工统筹会话交接包（新统筹会话上下文恢复入口）
date: 2026-08-13
ttl: task_bound
completes_when: "全部批次施工完工、遗留项清零、tracker 归档后一并归档"
---

# 施工统筹会话交接包

> **用途**：新统筹会话凭本文件 + [construction_progress_tracker.md](construction_progress_tracker.md) 恢复全部上下文，接手施工统筹工作。
> **创建**：2026-08-13（第一统筹会话）
> **重建说明**：⚠️ 本文件于 2026-08-13 晚重建。原文件从未 commit，会话关闭后丢失；本版依据会话记忆 + tracker 备份重建。
> **关联 SOP**：[02_construction_workflow_sop.md](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/02_construction_workflow_sop.md) v1.3.0

## 一、统筹 AI 角色定位

你是 ZephyrAlpha 项目施工体系的**总统筹**，不直接施工业务代码，负责：

1. **分配任务**：按 tracker §五 批次规划，为每个施工会话生成一键复制指令（含任务背景 + 文件完整路径 + 约束）。
2. **核验反馈**：每个施工会话完工反馈后，逐项核验（见 §三 核验清单），结论 PASS/FAIL 记录到 tracker。
3. **登记遗留**：施工队审查发现的遗留项登记到 tracker §六，分类定级，闭环后标 ✅。
4. **维护 tracker**：每次状态变化更新 construction_progress_tracker.md，**并经 GitCommitGateway commit 落地**（防丢铁律，见 §四-6）。
5. **批次推进**：一批全部 PASS 后，规划/分配下一批；全部批次完工后 tracker 归档或删除。

## 二、上下文恢复步骤（新统筹会话必读）

按顺序执行：

1. 读本文件（角色 + 铁律）。
2. 读 [construction_progress_tracker.md](construction_progress_tracker.md)（施工队状态 + 遗留项）。
3. 读 [02_construction_workflow_sop.md](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/02_construction_workflow_sop.md)（15 步施工流程 + 附录 A 长清单）。
4. 实证环境状态：
   ```powershell
   git branch --show-current          # 应为 dev
   git status --short                 # 确认工作区噪音水平
   git branch --no-merged dev         # 确认未 merge 分支
   python scripts/session_worktree.py list   # worktree 残留检查
   ```

## 三、施工队反馈核验清单

每个施工会话反馈必须包含以下要素，统筹逐项核验：

| 要素 | 核验方式 |
|---|---|
| commit hash | `git log --oneline <branch>` 实证存在，带 `[GW:<sid>]` 标记 |
| Step 1 文档审查结论 | 施工队对话内给出（引用 AI_review_instructions.md） |
| Step 6 长清单审查结论 | 按 SOP v1.3.0 附录 A **14 节版**逐节结论（批二 6/7 队误用旧 12 节版，第三批起必须 14 节） |
| 测试结果 | 新增测试连续 2 轮全绿；域全量测试的存量失败须甄别与本任务无关 |
| 改动文件清单 | 与 `git show --stat <hash>` 一致，无跨域夹带（COMMIT-SCOPE） |
| worktree 状态 | merge 前保留；merge 后 `git worktree list` 无残留 |
| 遗留项 | 有则登记 tracker §六，定级 P0/P1/P2 |

核验结论写入 tracker §四 反馈记录区：`PASS（理由）` 或 `FAIL（缺什么、怎么补）`。

## 四、铁律（违反即事故）

1. **施工隔离**：施工一律在 session_worktree 内进行（`python scripts/session_worktree.py create <sid> <task-id>`），禁止主工作区直接施工。
2. **提交通道**：commit 必须经 GitCommitGateway（`python scripts/git_commit.py` / gateway），**禁止裸 `git commit`**（post-commit guard 会自动 reset 非 GW commit）。
3. **只清自己**：临时文件/锁/worktree 只清理本会话的，绝不动其他会话的 WIP。
4. **冲突处理**：merge 遇冲突文件，先读双方内容判断价值——两份都有价值则合并/提取有价值内容插入主线；不盲目选边。
5. **并发避让**：改动前 `git status` + 检查其他会话占用（held_files / staged 清单），被占用文件登记遗留项而非强改。
6. **防丢铁律（本次事故教训）**：tracker 与本文件**每次里程碑必须经 GitCommitGateway commit 到 dev**。"staged + .runtime 备份"不是持久化——staged 会被其他会话/reconciler 冲掉，.runtime 免跟踪目录会话关闭即失联。2026-08-13 两份文件因此丢失，靠备份+记忆重建。
7. **新建文件即 `git add`**：project_memory #ARCH-GIT-CLEAN-GUARD-FIX 教训——`git clean -fd` 物理删除 untracked 文件不进回收站。

## 五、当前状态快照（2026-08-13 晚）

- **第一批 8 队 + 第二批 7 队**：全部完工 PASS，17 个 worktree 已全部 merge 回 dev（merge 会话 21:05 完成）。
- **SOP**：v1.3.0 已在 dev。
- **第三批**：3 个会话已分配待开工（33 BudgetChange 等；注意遗留项 #17——33 号文档骨架化需先充实）。
- **遗留项**：tracker §六共 28 项登记，4 项已闭环，P0 级 5 项阻塞已解除可立即处理。
- **未 merge 分支**：仅 `ai/bm-fill/task-battlemap-coverage`（遗留项 #21，待裁定）。
- **环境**：ALGO_FLOW runner 已完工（58/58），bm-fill 会话已结束，主工作区干净。

## 六、第三批开工指令要点（供生成一键复制指令时引用）

- 每个施工会话开头必须：`python scripts/session_worktree.py create <sid> <task-id>`
- 长清单审查用 **SOP v1.3.0 附录 A 14 节版**（非旧 12 节）
- 反馈必须含：commit hash + Step 1 结论 + Step 6 结论 + 测试结果 + worktree 状态 + 遗留项
- 33 BudgetChange 任务：开工前先处理遗留项 #17（33 号文档骨架化）
- 涉及 AGENTS.md 显化修改：走 Owner 审批（PROTECTED-PATHS 门禁，遗留项 #9）
