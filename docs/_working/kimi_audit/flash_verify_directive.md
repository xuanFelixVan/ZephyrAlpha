---
ttl: task_bound
rule_form: data
verifiability: manual
title: Flash 机械复验指令 v1.0（原 Kimi 案中的复验/漂移/接线面移交）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-17
---

# Flash 机械复验指令 v1.0

> **一句话**：你负责**体力与广度**——接线核对、全量扫描、跑测试、执行红蓝场景、编排出证。你不做裁定：任何"这个算法该不该这样、这个尺子对不对、这场战役要不要砍"的疑问，登记到疑点清单交给 Kimi 或 Owner。
> **与 Kimi 的关系**（铁律）：两份文档互不引用结论。你**不许**把 Kimi 报告里的判断当成"已核实"照抄；Kimi 也不把你的"已核对"当事实。你只交证据，它只交判断。
> 深度战场真源：[kimi_deep_adjudication.md](kimi_deep_adjudication.md)（不归你，但你需要知道哪些活已被拿走）。对象底册：[kimi_audit_checklist.md](kimi_audit_checklist.md)（全仓底数与 A1-A8 对象表，你按 §下面 V 表使用其机械面）。

## 0. 任务表（按此序干；每块完成即落盘+提交）

| # | 任务 | 入口 | 交付形状 | 估工 |
|---|---|---|---|---|
| V1 | **业务层六线设备接线核对** | `docs/_working/automation/campaign/CAMPAIGN_LEDGER.md` + 七连提交（fe8fce25 / 2a11b881 / a240714e / 9729a733 / 40ca90eb+dc285476 / 71257b59b2 / 383c0af8） | 逐线"产方是谁/消方是谁/证据文件/断点"四栏表 | 中 |
| V2 | **排班 v2 收尾复核** | W1-W4 + P2-a/P2-b/P3/P4-α/P5 各批 + L-3/L-4/L-5/L-6/L-8/L-9/C-3/C-8/C-11/C-13 | 72 实体注册表 ↔ schedule.yaml ↔ 实际执行记录三方对账表 | 中 |
| V3 | **daban 链产消闭合复验** | 车道 A/B2/D2/E/E2a/M/#12 交付 + 裁定 #271..#274、#302 | 四表三事件逐表行数/最新日/消费方 grep 反查证据 | 轻 |
| V4 | **ALGO_FLOW 出仓配对抽查** | 3158 份外迁 yaml ↔ 源码 external 锚 | 1:1 配对全量脚本核验 + 抽查 60 件（按域分层）内容等价性 | 轻（脚本化） |
| V5 | **八分包 T2 机械面** | `docs/_working/greatwall_integration/2026-09-16-eight-greatwall-e2e-integration.md`（155d2a16）+ 12 条跨线 | 逐分包"声称证据文件是否存在、命令能否复跑、数字能否复现"三态表（**不判对错，只记复现结果**） | 重 |
| V6 | **全量漂移扫描** | 542 蓝图 + 昨夜新增约 2000 份 `docs/03_modules/**` ↔ 源码 | 漂移清单（file:line + 型别：双份承载/幽灵引用/假完成/孤儿死码/YAML 静默），按域分组，**只列不改结论** | 重 |
| V7 | **五通道接线普查** | 数据（`python -m zephyr.data` 7 子命令）/ 决策（TDM 138 节点 parent_node+factor_refs+data_refs 悬空）/ 执行（策略→plan_engine→position→ex_sor）/ 治理（reconciler 事件触发合规+队列 dead 循环）/ 启动（boot_autostarch+reaper+健康检查） | 逐环有产有消表 + 断链清单 | 中 |
| V8 | **红蓝场景执行** | Kimi 的 S12 实验规格（不变式集+注入样本）+ 现有 63 条 metamorphic | 执行日志 + 每条"能否让被测对象变红"的实证 | 中 |
| V9 | **测试套与门禁复跑** | 逐目录跑（全量一次跑会内存耗尽，成例见 09-15 事故） | 分目录绿底报告 + 失败归因（自家/他队/环境） | 重 |
| V10 | **长任务编排** | 需要小时级回测/重考/聚合的项 | 夜间无人值守任务登记（`data/runtime/process_reaper_keep.txt` 防误杀）+ 产物落 `data/backtest_artifacts/runs/` 供 Kimi 判读 | 轻 |

**已知在途债**（V5/V6 重点密度区）：autoclaw ALGO_FLOW 残余（机械面已清零，作者语义欠账在册）；S19 硬违规暂计软；FRONTMATTER-SYNC reconciler 曾超时 ×4；`f06_e4_wfa_exam.py:355-367` OOS/IS 分子分母两口径不可比（P1，Kimi 会裁，你复现它）；分包B 产物两度遭扫离（第三度机械再生）——**你的产物一律落正式目录并在台账留再生脚本**。

## 1. 冷启动与提交纪律

```
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
python --version                                  # 必须 3.12.x
python scripts/lock_files.py cleanup
python -m zephyr.trading.process_reaper --status   # 计划任务不存在 = 禁任何写操作
```

每处修改：
```
python scripts/lock_files.py acquire <文件> flash-verify
python scripts/git_commit.py --session flash-verify --skip-preflight --allow-non-worktree --allow-overlap --files "<逗号分隔清单>" --message "verify(<域>): <一句话> [GW:flash-verify:non-worktree]"
python scripts/lock_files.py release <文件> flash-verify
```
- 禁裸 `git commit`；禁 plumbing 绕过；锁忙自动入队后继续干下一条，别空等。
- 禁无 claim 直改工作区（并发回滚会吞无主编辑）。
- 热文件（注册表/AGENTS.md/tracker）用 `safe_write_text` + `expected_base_sha256`，禁裸 Edit。
- 提交粒度=一个 V 任务一批；提交后 `git log -1 --name-only` 核实归属。
- 队列正门四条铁律照旧（含 `--adopt-prior-work` 重试带、`--allow-multi-domain` 留痕、队列项 dead 读 dead_reason 修正后 requeue）。

## 2. 五条铁律（防"跑了很多但什么都没证明"）

1. **判通过的脚本，先证明它能红**：任何你写的核验/验收脚本，必须先构造一个必然失败的样本跑红一次，再跑真数据。做不到就在交付里标"未证伪"。
2. **只交证据，不交判断**：疑点写进 `open_questions.md` 交 Kimi/Owner，禁自行裁定算法与尺子。
3. **禁顺手重构**：你改的范围=让证据能复现/让断链能接上/让漂移能对齐。任何"顺便优化"=超范围。
4. **产物防扫离**：结论性产物必须落 `docs/_working/flash_verify/`（正式区）+ 附机械再生脚本；`.runtime/tmp/` 只是中转，禁当终态。
5. **诚实条款**：没做到的明示+证据，跑不动的标"未跑（原因）"。宁可交一份"覆盖率 60%+缺口清单"，也不要交一份"看起来全绿"。

## 3. 产出与收官

- 落点：`docs/_working/flash_verify/`，按 V1-V10 各一份 + `drift_list.md`（V6 汇总）+ `open_questions.md`（疑点移交面）+ `green_baseline.md`（V9 绿底）。
- 收官：连续两轮自检零问题（每轮查：证据文件是否真实存在、脚本是否能复跑、提交是否落地、claim 是否 release、临时文件是否清零）。
- 汇报格式：任务表逐行"完成/部分/未做（原因）"+ commit 清单。**不要**用"全部完成"这种无锚点表述。
