---
ttl: task_bound
---

# 2026-08-30 本会话产出清单

> **会话性质**：A6 残余施工 + PIT 回填成本核算 + B5/B6 启用冒烟 checklist + B20 裁定书草稿。
> **约束遵守**：未触碰前端文件、blueprint 文件、`.runtime/session_registry.json`；每改一个文件已先 `git add`。

## 产出文件列表

| # | 文件路径 | 任务 | 状态 |
|---|---|---|---|
| 1 | `scripts/register_paper_session_task.ps1` | A6 残余：注册 `ZephyrAlpha_PaperSession` 计划任务（09:25 Daily + StartWhenAvailable 复活语义，注册即 DISABLED，92 号 D3 口径） | ✅ 新建 |
| 2 | `scripts/start_paper_session_daily.ps1` | A6 残余：计划任务 wrapper——is_trading_day 守卫 + xtMiniQmt 进程预检 + `python scripts/start_paper_session.py --service` 落盘日志 | ✅ 新建 |
| 3 | `scripts/deadman_switch.ps1` | A6 残余：第四路 live_strategy_biz 心跳监控（交易时段 09:30-15:00 门控，stale >10min 告警，含重启命令） | ✅ 修改 |
| 4 | `scripts/estimate_pit_backfill_cost.py` | PIT 回填成本核算：DeepSeek/Qwen 双通道 × v1/v2 双模式 × 730 交易日 dry-run 估算，实证 exit 0 | ✅ 新建 |
| 5 | `docs/_working/2026-08-30-b5b6-enable-checklist.md` | B5/B6 启用冒烟 checklist：B5 四组 19 项 + B6 三组 10 项逐项检查点+通过标准 | ✅ 新建 |
| 6 | `docs/_working/2026-08-30-l3-snapshot-datasource-adjudication.md` | B20 裁定书草稿：miniqmt 持仓快照 vs 结算单反推优缺点对比 + 推荐裁定 + Owner 勾选位 | ✅ 新建 |
| 7 | `docs/_working/2026-08-30-session-output-manifest.md` | 本清单 | ✅ 新建 |

## 关键验证

- `python scripts/estimate_pit_backfill_cost.py` 实证输出：DeepSeek v4-flash 谷时 v1 730 日 ≈ ¥15.11，v2 ≈ ¥19.05；Qwen v1 ≈ ¥1.97，v2 ≈ ¥3.29。
- `deadman_switch.ps1` 语法检查通过（无 PowerShell 解析错误）。
- `register_paper_session_task.ps1` 与 `start_paper_session_daily.ps1` 未实际执行注册（Owner 窗口动作，DISABLED 态保留一键恢复）。

## 后续 Owner 动作

1. 阅读并勾选 `2026-08-30-b5b6-enable-checklist.md` 全部检查点。
2. 阅读并勾选 `2026-08-30-l3-snapshot-datasource-adjudication.md` 方案 A/B/C。
3. 裁定后执行：`powershell -ExecutionPolicy Bypass -File scripts\register_paper_session_task.ps1`（注册 DISABLED）→ 按需 `Enable-ScheduledTask ZephyrAlpha_PaperSession`。
