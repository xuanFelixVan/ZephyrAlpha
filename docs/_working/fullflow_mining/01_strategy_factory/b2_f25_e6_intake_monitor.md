---
ttl: task_bound
session: st-ailayer-fullflow-sf-b
title: F25 E6 入库监控——六向台账与三态结论（SF-B 后半）
date: 2026-09-25
status: mined
---

# F25 · E6 入库监控

> 组 SF·策略工厂供给链 B 后半册 3/7。上游 F24（簇首集），下游 F26（sim 前哨）/F14 反馈（进货方向回灌）。
> 环节真源：config/strategy_production_map.yaml FAC-E6（build_status: built）；注册表=docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml。

## 一、环节定义与边界

一句话：入库=簇首经 CAS only-add 写入 strategy_registry（带 run 指针证据）；监控=台账只增+判死行追加，oos_years_decay≥0.5 判存疑，decay_cause 枚举，结论反馈 E2 假说库/E1 进货方向。
供料方：E5 簇首+生命周期 FSM（candidate→sim 预授权三条件）。消费方：E7 前哨（registry lifecycle=sim 名单）、promotion_advisory（no_pending_decay_alert 条件读取衰减台账）、E1/E2 反馈环。

## 二、六向台账

| 向 | 实证 |
|----|------|
| 上游输入 | ①簇首集（intake ③步产出）；②decay 输入=strategy_screen 的 is_sharpe/oos_years_decay 行（strategy_screen_query MOD-BT-078 为 DECAY_SUSPECT 土规真源）；③E4 档案 run 指针（data/backtest_artifacts/runs/） |
| 下游消费 | ①strategy_registry.yaml 现 162 条 strategy_id（2026-09-25 实测 grep -c），1 条 lifecycle_status=sim（lane_e_quantile_baseline MOD-BT-084），余 candidate；②data/runtime/strategy_decay_ledger.json（MOD-SIG-150，schema strategy_decay/2，updated 2026-09-21，CAND-* 逐条 probation/fail-closed 判不了如实记）；③promotion_advisory 预授权三条件第 3 条=no_pending_decay_alert（promotion_advisory.py 依赖声明） |
| 自动化触发 | **建成未投产**：c4_batch_completed→run_intake_auto（pipeline_events.py:257-259）→及格→FDR→聚类→入库→挂图→sim 流转全自动 only-add；日件面 sim_ledger_daily/journal/observe（SIM_DAILY_WAKE_TASKS=daily_kline 族唤醒，marker 幂等，last_audit.json 实测 09-24 全绿） |
| 真源与注册表 | 图节点 FAC-E6；MOD-BT-078 strategy_screen_query（summary/bothwin/trace/failed/scored 五命令）；MOD-BT-187 strategy_lifecycle_advisor（decay_watch 流转建议器：decay≥0.5 存疑/双负 reject/双达标 candidate/其余 hold，只建议不终裁）；MOD-SIG-150 衰减台账；MOD-BT-188 lifecycle_fsm（8 态，sim→production Owner 门=owner_token hmac 常量时间比对，键未配置 fail-closed）；MOD-BT-192 registry_writer（CAS only-add 手术臂）；MOD-SIG-150 消费者 strategy_decay_certifier |
| 门禁与质量尺 | 注册表写入必经 safe_write_text CAS+写后复核（条目数+既有 sid 全在）；只增不改；decay 公式与 c4 OOS 批一字不差 ((IS-OOS)/\|IS\|/2.5 钳[0,1])；KillSwitch 非 normal 管线拒绝执行；EVIDENCE 文件缺失 RuntimeError fail-closed；生命周期终裁=Owner（机器只建议） |
| 当前运行状态 | **黄**。绿侧：decay ledger 真实运转（09-21 更新，fail-closed 判例在案）；日件链 09-24 marker 全绿（sim_ledger/sim_journal/sim_observe/attribution_daily）。黄侧：**C6 自动入库链生产运行=0**——6 份 intake-*.md/.yaml 报告全部含 pytest_ 路径=测试泄漏件（tests 写穿生产报告目录，违反测试隔离红线 §9.6），注册表 0 条 STR-AUTO 条目；162 条注册条目来自 2026-09-14 转正批等人工/半自动路径 |

## 三、子模块清单

| 模块 | 是什么 | 入口 | 状态 |
|------|--------|------|------|
| MOD-BT-078 strategy_screen_query | 台账查询五命令+DECAY_SUSPECT 判定土规 | scripts/backtest/strategy_screen_query.py | built（本次实测两命令跑通） |
| MOD-BT-187 strategy_lifecycle_advisor | decay_watch 扫描建议器 | scripts/backtest/strategy_lifecycle_advisor.py:34 advise | built（纯函数+台账只读） |
| MOD-SIG-150 衰减台账 | data/runtime/strategy_decay_ledger.json 判死台账 | src/zephyr/signal_ashare/strategy_signal/strategy_decay_certifier.py | built（09-21 实测在更新） |
| MOD-BT-189 intake | C6 自动入库编排（及格/FDR/聚类/入库/挂图/FSM 六步） | src/zephyr/strategy_pipeline/intake.py:466 run_intake_auto | built（测试绿）——**生产零运行** |
| MOD-BT-192 registry_writer | 注册表 CAS only-add 写入器 | src/zephyr/strategy_pipeline/registry_writer.py | built |
| MOD-BT-188 lifecycle_fsm | 8 态生命周期状态机（candidate/sim/production/retired/shelved…） | src/zephyr/strategy_pipeline/lifecycle_fsm.py | built（Owner 门 fail-closed） |
| auto_mount | 挂图语义门（注册表↔TDM 挂轴） | scripts/backtest/auto_mount.py | built（测试中 CAS 冲突自愈路径在验） |
| promotion_advisory MOD-BT-199 | 衰减台账只读回+三条件回落实据 | src/zephyr/strategy_pipeline/promotion_advisory.py | built（属 F74 面，此处只列交联） |

## 四、堵点与病灶

1. **自动入库链零生产运行**（现象=报告目录 6/6 全是 pytest 泄漏、注册表 0 条自动入库；根因=c4_batch_completed 事件从未在生产 drain 消费（heavy 事件堵在 E4 前站，轻事件 emitted 时机=落账后，但 run_intake_auto 无生产触发记录）；修法=BP-5：先清测试泄漏→手动触发一次 `python -m zephyr.strategy_pipeline.pipeline_events drain` 消费 16 及格集→验证注册表 CAS 首条自动入库；工作量=S-M；本车道可修=是）。
2. **测试写穿生产报告目录**（现象=intake-20260925-*.md 含 `.runtime/tmp/pytest_28136` 路径；根因=intake 测试 fixture monkeypatch 了挂图/注册表 ROOT 但 REPORT_DIR 未随 tmp_path——半吊子隔离；修法=REPORT_DIR 改注入参数+清理 6 份泄漏报告；工作量=S；可修=是）。
3. **反馈环未建**：feedback_loops 声明 FAC-E6→FAC-E1（衰减结论反馈进货方向），全仓无消费衰减台账调整车道配额的实件（promotion_advisory 只读作晋升门槛）。属 E7/E9 之后的闭环欠账，登记不施工。
4. **registry 162 条 vs 台账 574 uniq**：漏斗下游（C2 粗筛 597→及格 16→簇首→入库）链路数字自洽，但 162 条中大量为模板批/历史条目，出生证字段完整度参差——归 F29 册处置。

## 五、提速与合并机会

- strategy_lifecycle_advisor（MOD-BT-187 建议器）与 MOD-SIG-150 衰减台账同读 strategy_screen decay——可合并为一班扫描（现各自独立跑）。
- intake 六步与 sim 日件链共享 daily_kline 唤醒波，无需新触发器。

## 六、自审闸三态

**挖干可施工**。引擎件全 built 且两源交叉验证；堵点 1/2 有根因+修法+工作量；施工项（清泄漏→首跑→首条自动入库）已在 BP-5 列为施工前置。"built"判据对 E6 成立（台账/判死/监控件全在），但"自动入库"作为能力**未投产**——此差别已在运行状态向明示。

## 七、复核命令（10 分钟）

```bash
grep -c "strategy_id:" docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml  # 162
grep -L "pytest_" docs/_working/pipeline-research/reports/intake-*.md                            # 空=全泄漏
head -c 400 data/runtime/strategy_decay_ledger.json                                              # 衰减台账
python scripts/backtest/strategy_lifecycle_advisor.py --dry-run                                  # 建议器跑通
cat .runtime/strategy_pipeline/last_audit.json | head -c 600                                     # 日件 marker
```
