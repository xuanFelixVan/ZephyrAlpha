---
ttl: task_bound
---

# Owner 体验 Runbook——C6 全自动管线时代的一天（交接清单⑮）

> 2026-09-15｜st-autopipeline-20260915｜对应交接档案第四组"演练一遍完整 Owner 体验"。
> 治理边界：机器自动到 sim；**sim→production 签字=Owner 唯一日常门**；KillSwitch/月度审计=人类回路。

## 一、全自动段（Owner 零参与）

```
C3 会话落翻译件 → [扫描] c4_batch_due（告警+登记）
  → c4_batch_screen --auto-only 批测落账
  → [事件] c4_batch_completed → run_intake_auto
      ①bothwin 及格 → ②BH-FDR 门（sim 用） → ③ρ>0.6 聚类（簇首=证据最强）
      → ④三轴+信号指纹差异化 → ⑤注册表追加 candidate（CAS+only-add）
      → ⑥auto_mount 挂图（only-add+38 规则） → ⑦报告+告警+回执
```

- 及格∧簇首∧差异化=自动入库 candidate；BH-FDR q≤0.10 且无衰减预警=自动进 sim（A 方案预授权三条件）。
- 全链幂等：同批事件重放零 diff；KillSwitch 激活=事件留 `.runtime/strategy_pipeline/pending_events.jsonl`，恢复后任何唤醒点自动重放。
- 触发零 cron：所有"定时感"行为=数据任务完成/批测完成等事件唤醒点上的到期评估（maybe_emit_monthly，30 天档）。

## 二、Owner 的日常动作（每月约 30 分钟）

1. **看月报**（每月 1 份，自动生成）：`docs/_working/pipeline-research/sim-memos/sim-memo-YYYYMM.md`
   - sim 档逐条评估要点+candidate 留观清单（MOD-BT-193 机器备料）。
2. **签字**（唯一门位）：对想转正的 sim 条目走 sim→production（OwnerTokenGuard，机器不带 token 天然停门）。
3. **扫异常**（有告警才看）：`data/failures/` 中 source=strategy_pipeline 的告警；挂图审计漂移（月度自动跑，drift 必报）。
4. **月度审计**（自动执行，Owner 抽查即可）：`auto_mount --audit --scan-frequency monthly` 产物+`last_receipt.json`。

## 三、Owner 的紧急动作（期望永远用不上）

| 场景 | 动作 | 效果 |
|---|---|---|
| 管线失控/误入库 | 触发 KillSwitch（reset 需 Owner） | 管线全停；事件留 journal 不丢；reset 后自动续跑 |
| 想停自动批测但不熔断全局 | 删除/不触发重资源 drain：不跑 `pipeline_events drain --all` 即可 | c4_batch_due 只登记不执行，其余照常 |
| 写入路径回锁 | 删除 `docs/_working/pipeline-research/acceptance6-replay.md` | intake dry_run=False 一律 RuntimeError（fail-closed 存在性门控） |
| 毒丸事件处置 | 修因后删 journal 中对应行（含 poison 标记） | 恢复自动消费 |

## 四、常用命令速查

```powershell
python -m zephyr.strategy_pipeline.pipeline_events status          # 看积压/最近回执
python -m zephyr.strategy_pipeline.pipeline_events drain --all     # 全量消费（含自动批测）
python scripts/backtest/c4_batch_screen.py --auto-only             # 手动触发新件批测
python scripts/backtest/auto_mount.py --replay --report            # 挂图幂等自检
python scripts/backtest/auto_mount.py --audit --scan-frequency monthly
python scripts/backtest/sim_promotion_memo.py                      # 立即生成转正建议书
```

## 五、本班验收证据索引

- 验收⑥回放 8/8 PASS：`docs/_working/pipeline-research/acceptance6-replay.md`（写入路径钥匙同件）
- E2E 沙箱全链 ≤10min PASS：事件→5 candidate→挂图 14 ops→38 规则过→报告（287.6s）
- 红蓝对抗与测试面：见最终汇报与 `tests/strategy_pipeline/`
