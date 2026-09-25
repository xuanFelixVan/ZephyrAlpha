---
ttl: task_bound
---

# B0 · 衍生工件下线提交关键路径（设计+测量车道）

> 真源：测量脚本与原始输出在 `.runtime/tmp/cs-tbl/b0_probe/`（一次性探针，可复跑）；
> 阶段编号沿用 `docs/_working/commit_speedup_campaign/00_skeleton/S1_stage_inventory.md`（ST-18/19/20/16）。
> 口径提醒：本表**只**用既有遥测，不新造计数器；A2 分段计时器尚未落地，故残差如实标 UNKNOWN。

## 每件落地时间预算（slow_item 窗口反推，近 6 日 n=60 / 全量 n=174）

| 段 | 秒/件（mean / med / max） | 怎么量的（可复测） | 状态 |
|----|--------------------------|-------------------|------|
| 落地件全程墙钟 | 760 / 550 / 3192（n=174） | `bottleneck_ledger.jsonl` `kind=slow_item`（t0 = ts − seconds） | 实测，**右删失 @300s**（阈值 `commit_queue.py:178`） |
| 在进程门禁链 Σ逐门 ms | 63.7 / 39.8 / 666（n=1767） | `gate_execution_stats.jsonl` `total_ms`（=Σ逐门，非墙钟） | 实测 |
| 单条 commit 墙钟（门禁+68 hook+git+**post-commit 钩链**） | 112 / 112 / 799（commit_slow n=269）；快样 85 / 56 / 354（ok_sample n=52，12.5% 采样） | `commit_block_events.jsonl` `total_ms`（`git_commit_gateway.py:2358→2589`，锁等待+链+提交全程） | 实测，>60s 才记 → 上偏 |
| 门禁地板（他车道外推） | 81.2 + 0.96×文件数 | 见同战役 D3 结论；本车道未复核斜率 | 引用 |
| t0 → 主区收敛首条记录（落地前半段） | 632 / 443 / 1812（仅 24/60 窗可定位） | `commit_queue/main_workspace_sync.jsonl` `ts` 减反推 t0 | 半实测 |
| 收敛段内跨度 | 152 / 0 / 1887 | 同上（首末 ts 差） | 稀疏 |
| 收敛末条 → 件结束（含 180s 超时的 integrity 基线刷新） | 46.1 / 6.2 / 300.7 | 末条 `main_workspace_sync` ts → `slow_item` ts；`commit_queue_landing.py:1448-1475` | 实测（上限=超时 180s） |
| `reference-transaction` 钩（每次 ref 移动） | dev 前进 1.25 / 1.25 / 1.54；非 dev 0.39；真回退 0.44 | 直跑 `.git/hooks/reference-transaction prepared`（合成 stdin 行，未建 scratch worktree）+ PATH shim 计数：5 个 git 子进程 | 实测 |
| post-commit 内 regen 触发器（同步部分） | 0.1–1 | 直跑 `post_commit_regen_yaml.py`（`ZEPHYR_SKIP_REGENERATE=1`） | 实测 |
| **再生扇出本体（分离进程，不在关键路径上）** | CPU 总秒 97.3 / 122.5 / 234.3；墙钟 37 / 11 / 131 | 20 份 `.runtime/logs/post_commit_regen_yaml_*.log` 逐生成器 `elapsed_ms` 求和；文件名戳 vs mtime | 实测（争用代价未折算） |
| **不可归因残余** | **≈630/件** | 60 窗中 36 窗零 `main_workspace_sync` 记录、19 窗零 gate 记录 → 无锚点 | **UNKNOWN** |

单生成器 CPU 秒（同类触发下的均值）：`domain_doc` 78.7｜`governance_map` 19.1｜`path_tree` 17.5｜`battle_map` 10.8｜`decision_diagram` 7.1｜其余 12 项各 <6。
触发→实际 spawn 的存活率：近 7 日 942 commit 中 81 件命中生成器 YAML 输入源，盘上只有 20 份 regen 日志 ⇒ **≈75% 触发被 60s TTL 去重静默丢弃（丢时连日志都不写）**。

## 前三手（详见 B0_3）

| 手 | 动作 | 预期省/件 | 回滚 |
|----|------|----------|------|
| M1 | integrity 基线改「按 HEAD 派生」，删掉 per-item 180s 同步子进程 | 40–46s（尾段 max 301s） | flag `ZEPHYR_INTEGRITY_BASELINE=snapshot`（出厂态=现行为） |
| M2 | 落地 worktree 内的衍生再生**不再触发**（产物既被禁入 git 又被下件 `reset --hard` 丢弃 = 纯负收益），改主区单点事件触发+去抖合并 | 关键路径 0–1s，争用侧 30–60s（4 工 ×97 CPU-s 爆发不再同窗）| flag `ZEPHYR_REGEN_SCOPE=any` |
| M3 | `reference-transaction` 钩 5 个 git 子进程并 1，Qoder tracker 移出锁内可见段 | 2–4s/件 + 把未知项变可知 | 钩子文件 `.orig` 还原 |

合计可解释 ~50s/件；**其余 ~630s 必须靠 A2 分段计时器定性**，本车道不猜。
