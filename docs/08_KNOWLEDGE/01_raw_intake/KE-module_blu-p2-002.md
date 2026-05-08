---
module_id: KE-module_blu-p2-002
title: 🟢 追加 P2 中危级
category: module_blueprint
---

# 🟢 追加 P2 中危级

🟢 追加 P2 中危级

| ID | 来源领域 | 盲点 | 问题描述 | 补充方案 |
|:--:|------|------|---------|---------|
| **B68** | 环境工程 — venv/conda 污染 | **回滚恢复了代码但 venv 残留旧包——代码/依赖版本分裂** | `requirements.txt` 被回滚到 v1，但 `venv/` 中已安装的是 v2（由上次 `pip install -r requirements.txt` 安装）。Python 导入时从 `venv/` 读取 v2 包，代码却期望 v1 行为。B25 提到 pip 包安装但未处理"包已存在但版本错"的问题 | 回滚后在 G0 验证后追加 `venv_sync`：`pip install -r requirements.txt --upgrade`（`--upgrade` 强制覆盖版本差异）。如果 venv 通过 `pipenv`/`poetry` 管理，执行对应 `sync` 命令。耗时操作（>30s pip install）→ 标记为 slow recovery → 异步执行但 block Agent 直到完成 |
| **B69** | 操作系统 — 环境变量缓存 | **回滚恢复 `.env` 但终端/IDE 进程仍缓存旧环境变量** | `git revert` 恢复了 `.env` 文件。但所有正在运行的终端、IDE 进程、后台 Agent 已经 load 了旧版 `.env` 的环境变量到内存中。`os.environ` 不会因为文件变更自动刷新。Linux 的 `export`、Windows 的 `$env:` 都需要重新 source | `rollback_executor` 回滚完成后写入 `.zephyr/last_env_reload` 哨兵文件 + signal。Agent 的 `env_watcher.py` 每隔 10s 检查哨兵文件的 `mtime` → 比上次 load 新则 `os.environ.clear()` + 重新 `load_dotenv()`。回滚后强制 all agents reload env |
| **B70** | 认知科学 — AI 时间上下文断裂 | **回滚破坏 AI 对话流中的时间顺序——AI 引用"已经被回滚掉"的旧事实** | 氛围编程中，对话是连续时间流。AI 说"上一轮你让我改的那个文件"——但那个文件已被回滚。AI 的对话历史是"文件 A 已创建"→ 回滚删除了 A → AI 下一句话"把文件 A 里的 X 改成 Y"——对 AI 来说文件 A 存在，对文件系统来说不存在。时间上下文断裂导致 AI 决策混乱 | `temporal_context_adapter`：回滚后不直接注入 B44 的 prompt → 先分析回滚前后对话历史中**受影响的引用**：哪些文件/概念/变量被提到了但已不存在/已不同。生成 `TEMPORAL_INCONSISTENCY_REPORT`：`"以下你之前做的假设已不成立：[file-a 已删除 / function-b 已回滚到 v1 / table-c 不再存在]"` |
| **B71** | 运维控制 — Owner 目标覆盖 | **Owner 无法手动选择回滚到"非自动检测目标"的版本** | 蓝图只有 auto_rollback_trigger（自动检测目标）和 hard_reset（全局核弹，token-gated）。但如果 Owner 认为"自动检测建议回滚到 commit-A 但我觉得应该回滚到 commit-B"——没有 CLI 支持这个操作。K8s 有明确的 `--to-revision=N` 参数 | `zephyr rollback --to {sha_or_tag}` CLI 命令：Owner 可手动指定回滚目标 → 跳过 auto_rollback_trigger 的目标选择逻辑 → 直接进入 RollbackExecutor 的标准流程（preflight+preview+lock+execute+verify）。操作记录为 `rollback_trigger: manual_override` |
| **B72** | 网络工程 — 网络分区下的 Remote Sync 挂起 | **`git pull --rebase` 在网络断开时无限等待——preflight 停滞** | §2.2 step_0_preflight 说"remote_ahead → git pull --rebase 后再预检"。如果此时网络断开（WiFi 掉线 / VPN 断开），`git pull` 无限等待 TCP 超时（默认 300s）——整个回滚 preflight 停滞。在 1 人运维场景下，Owner 可能也在断网状态 | preflight 的 `git pull` 操作加 5s 超时：`timeout 5 git pull --rebase --timeout=3` 或 `GIT_HTTP_LOW_SPEED_LIMIT=1 GIT_HTTP_LOW_SPEED_TIME=3`。超时 → 不预检 remote → 标记 `PREFLIGHT_NO_REMOTE` → 仅本地回滚 → 事后通知 Owner "远程同步未确认" |
| **B73** | 云存储 — S3/GCS 快照生命周期冲突 | **B23 的 S3 快照被自动生命周期策略删除——git 中只剩悬挂引用** | B23 建议"大 SQLite dump 到 S3/GCS，git 只存储引用"。但 S3 bucket 可能配置了 30 天自动过期策略——超过 30 天的快照被删除，git 中 `{"s3_key": "snapshots/{sha}.jsonl.gz"}` 变成悬挂引用。回滚时 S3 GET 返回 404 | S3 snapshot 的 `{sha}.jsonl.gz` 文件名包含 `{timestamp}` → `snapshots/20260505/{sha}.jsonl.gz`。S3 lifecycle 策略只应用于 `snapshots/$DATE/` 前缀。git 引用存绝对时间戳路径 + 回滚时 fallback 到下一天尝试。或：所有 S3 快照禁止自动删除——只由 `checkpoint_gc.py` 手动触发 |
| **B74** | 合规审计 — 外部证明 (External Attestation) | **回滚审计日志无第三方可验证性——HMAC 只内部可验证** | B39 用 HMAC-SHA256 保护了审计日志，但这是对称签名——需要 Owner master key 验证。对 SOC2/SOX 审计员来说，他们无法独立验证"这个回滚记录没有被篡改"——因为 key 在系统内部。对标：区块链的时间戳证明 / AWS QLDB 的密码学完整性证明 | 每次回滚后对 audit record 生成 **Merkl
