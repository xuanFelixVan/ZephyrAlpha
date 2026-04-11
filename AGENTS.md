# ZephyrAlpha — AI Agent 入口（持久）

本仓库使用 **Cursor** 时，每轮对话会自动加载 `.cursor/rules/zephyr-governance-agent.mdc`（`alwaysApply: true`）。

## 接到「继续未完成的工作」时

1. 打开 **[全仓库文件治理任务清单](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)**：优先核对 **§3.6**（合并专项）、**P5 / §7**（按目录前缀尽治）未勾项，并按 **§7.1** 从最新 `REPO_DIRECTORY_ROLLUP_*` 拆批执行。  
2. 工具命令表：**[GOVERNANCE_TOOLS_INDEX.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)**。  
3. 可复制阶段流程：**[GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md)**。

**说明**：单次对话无法连续运行数小时；跨会话靠 **REPO_WIDE 勾选状态 + PR/commit 说明中的批次摘要** 接力，直至未勾项收敛（D 类正文合稿仍须 Owner）。

## Git 暂存（禁止一锅端）

- **禁止**使用 `git add -A`、`git add --all` 或 `git add .` 将**全工作区**未区分地纳入暂存区（极易把与当前任务无关的大量改动一并提交）。  
- **必须**使用 **`git add <明确路径>…`**（或等价地逐文件 `git add`），且与本轮任务一致；**仅当用户在对话中明文要求**「全量暂存 / 全部 add」时，才可使用上述一锅端命令，并在 commit 说明中写明系用户授权。

## 防死循环（L1 / Git 冲突 / 反复修复）

- **同一任务**（例如：把 `sentinel_l1` 判无效压到 0、或解决某次 merge/rebase 冲突）若 **连续 3 次**尝试仍失败或每轮修复后 **仍回到同类错误**，**立即停止**在该任务上继续自动改。  
- 在**本轮回复**中明确标注 **[STUCK]**，写清失败摘要与建议 Owner 动作；**禁止**在同一对话里无上限地「再试一次」链式改同一批文件。可选：在 [REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **版本记录**留一行备忘（非强制）。
