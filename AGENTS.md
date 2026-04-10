# ZephyrAlpha — AI Agent 入口（持久）

本仓库使用 **Cursor** 时，每轮对话会自动加载 `.cursor/rules/zephyr-governance-agent.mdc`（`alwaysApply: true`）。

## 接到「继续未完成的工作」时

1. 打开并遵循 **[自主接力运行队列](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/AUTONOMOUS_GOVERNANCE_RUN_QUEUE.md)**：先读 **「当前指针」**，再执行 **「下一步队列项」**。  
2. 全量 backlog 与口径以 **[REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md)** 为准。  
3. 工具命令表：**[GOVERNANCE_TOOLS_INDEX.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)**。  
4. 可复制阶段流程：**[GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GLOBAL_FILE_GOVERNANCE_SESSION_HANDOFF.md)**。

**说明**：单次对话无法连续运行数小时；靠本文件 + 运行队列里的 **「当前指针」** 跨会话接力，直至队列与 REPO_WIDE 未勾项收敛（D 类正文合稿仍须 Owner）。

## 防死循环（L1 / Git 冲突 / 反复修复）

- **同一任务**（例如：把 `sentinel_l1` 判无效压到 0、或解决某次 merge/rebase 冲突）若 **连续 3 次**尝试仍失败或每轮修复后 **仍回到同类错误**，**立即停止**在该任务上继续自动改。  
- 在 **[AUTONOMOUS_GOVERNANCE_RUN_QUEUE.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/AUTONOMOUS_GOVERNANCE_RUN_QUEUE.md)** 中按该文档 **「[STUCK] 标注」** 规则写入（`notes` 与/或对应队列行），将 **next_queue_id** 指到**下一项**；本轮回复中明确告知用户 **已 [STUCK]**、失败摘要与建议 Owner 动作。  
- **禁止**在同一对话里无上限地「再试一次」链式改同一批文件。
