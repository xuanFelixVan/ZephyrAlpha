---
ttl: task_bound
---
# DEEP_DIVE_R1 — 提交链堵点深挖 R1（Owner 点名专项）

> ttl: task_bound
> 日期: 2026-09-25 ｜ 代理: 深挖车道 R1 ｜ 性质: 只读取证（零代码/配置/门禁改动）
> 数据窗: 主窗 >=2026-09-23T00:00Z；pool_wave 窗 2026-09-24T22:34 → 09-25T03:14(+08)
> 中间数据: 本目录 `r1_data/`（10 个 .yaml）；复跑脚本: `.runtime/tmp/csx_deep_01..09_*.py`（每节标注）

---

## A. w0/w3 慢之谜 —— 结论：工位环境无结构性差异；"3-5 倍差"是**尾部事件+统计口径**造成的假象，真实结构性问题是**单件 hook 成本与件大小脱钩**

**A1. 用户引用值已精确复现并破译口径**（`csx_deep_08`，r1_data/e2_recoverable_minutes.yaml）：

| 工位 | 引用值 | 实测 mean | 实测 median | 剔除 ≥300s 尾部后 mean |
|---|---|---|---|---|
| w0 | 230.7s | **230.7s（精确命中）** | 96.8s | 95.0s |
| w1 | — | 83.5s | 53.5s | 83.5s |
| w2 | 54.3s | 97.4s | 36.3s | **54.3s（精确命中）** |
| w3 | 265.0s | 350.0s | 164.3s | 119.0s |

即：引用的"门禁链均值"实为 **precommit_channel_stats.total_ms 均值**，w2=54.3 是剔除尾部后的口径、w0=230.7 是含尾部的口径——两者口径不一致，直接对比放大了差异。逐行证据：r1_data/a3_precommit_channel_rows.yaml（全 44 行）。

**A2. 同件跨工对照证明工位等价**：同一会话 st-metaq-20260923 的 38 件大件在四工耗时 49.7 / 51.4 / 39.3 / 53.2s（w0/w1/w2/w3）——同一工作在同一工位面耗时 ±30% 内，**不存在 worktree 落后导致的系统性环境差**。st-metaq-gc-20260924 的 40 件件四工 277.0–285.9s 同样高度一致（但四工**同时**各跑一遍，见 A4）。

**A3. 尾部事件清单（9/24 单日）**：3 笔 1200s 超时（fast 子集卡在 300.1s 上限后整段烧满 1200s，rc=-1/infra_error=True：w3 18:39、w0 20:08、w3 20:22）+ 3 笔 346/497/658s 慢件。仅 3 笔超时=60min，占当日 precommit 总耗时（~163min）的 37%。**w0/w3 均值就是被这些尾部抬起来的**。

**A4. 真正的结构性问题——hook 成本不随 own-scope 收缩**：
- 1 件提交跑出 346.5s（w0, st-mapbuild）与 657.6s（w2, st-t0-matrix）；而 38 件大件只要 33–53s。residual 按件数分桶同样反相关：1 件桶 mean residual 325.5s > 16-40 件桶 235.2s（r1_data/b_residual_decomposition.yaml）。说明慢段是**全仓型 hook**（如 GATE-PANORAMA-ALIGNMENT 的 git diff 全景扫描、depgraph 类），不是件大小。
- 门禁链最贵单门 = **CREATE-GUARD**：w1 mean 179.2s/次、w3 102.8s、w0 39.5s、w2 37.1s；w2 两天累计 6713s=112min（r1_data/a2_window_20260924_detail.yaml per_gate_mean_ms）。其余重门：REGISTRY-MASS-DELETION（w0 17.9s）、RECONCILER-HEALTH（w3 31.6s）、MODULE-ID-CONSISTENCY（w3 25.9s）。
- 失败率结构差（gate_execution_stats，>=09-23）：w0 50/91=55%、w1 51%、w3 50%、**w2 仅 30%**——w0/w1/w3 每两条链一条失败重跑，这是 w0/w3 "更慢"的另一半真实成分（重复链成本见 C/E）。

**复跑**：`python .runtime/tmp/csx_deep_04_window.py && python .runtime/tmp/csx_deep_05_precommit.py && python .runtime/tmp/csx_deep_08_recover.py`

---

## B. residual 336s 分解 —— 结论：门禁链+precommit 可解释 64.3%，**剩余 ~123s/笔 未解释**；主要候选=全局锁等待/落地陈旧/对账扇出

总账（116 笔 landing，>=09-24 窗，r1_data/b_residual_decomposition.yaml）：

| 项 | 值 |
|---|---|
| landing total 合计 | 755.9 min |
| 八相位 accounted 合计 | 90.8 min（12.0%） |
| **residual 合计** | **665.1 min（88.0%），mean 344s / median 177s / p90 663s** |
| residual 中门禁链（gate_execution_stats 落在 landing 窗内） | **48.2%** |
| residual 中 precommit 通道（同会话落在窗内） | 16.1% |
| 两者合计可解释 | **64.3%** |
| **未解释残差** | **237.8 min / 116 笔 ≈ 123s/笔** |

- 已核验无双计：gate_execution_stats 的 ms 表内不含任何 PRECOMMIT 门（csx_deep_08 第 1 项输出）。
- accounted 八相位内部：snapshot 39.1min、cas 23.3min、sync 14.6min 为前三（phase_sums）；conflict/worktree 可忽略。
- **未解释 123s/笔 的候选（按证据强度排序）**：
  1. **全局提交锁等待**：belt_daemon_csx.log 中 32 次 `Cannot acquire global commit lock`（GatewayError）——落地串行锁排队直接表现为相位外等待；
  2. **落地陈旧**：bottleneck_ledger `landing_staleness` 9/24 单日 130 条（前日仅 20/30）——项落地后滞留；
  3. **对账/衍生扇出**：RECONCILER-HEALTH WARN"24h 内 10 次 critical 失败"、dual-track reconcile probe fail×9、derived_stuck×1（9/24 首现）；
  4. 四工重复执行同一大件（A4/st-metaq-gc 案例）造成的锁互等。
- 方法注：窗口对齐法按 [ts−total_ms, ts] 落在窗内计入门禁链/precommit；跨窗边界链会少量互串，误差 <±10%。逐笔明细：r1_data/b_residual_per_event.yaml。

**复跑**：`python .runtime/tmp/csx_deep_03_main.py`

---

## C. 阻断后重试放大 —— 结论：重试贡献了 2038 次阻断中的 1186 次（58%）；近窗白白烧掉 723 min 门禁链

（r1_data/c_block_retry.yaml；全量 2038 事件，2026-09-13 起）

| 指标 | 值 |
|---|---|
| 阻断事件总数 | 2038 |
| (会话,门) 唯一对 | 852 |
| 同对被阻 ≥2 次 | **346 对** |
| ≥3 次 / ≥5 次 | 201 / 89 对 |
| 单对最高阻断次数 | **37 次** |
| 重试衍生额外尝试 | **1186 次（58%）** |
| 每次阻断平均白烧链长 | 75.8s |
| 阻断白烧链合计（全史） | 2574 min |
| **近窗（>=09-23）** | **383 次，723 min** |

近窗 top 常阻断门（csx_deep_03 by_gate_since_20260922）：
1. **GATE-PRECOMMIT-RUN ×114** —— 落地前 pre-commit run 失败；其 gate_chain_ms=0（成本全记在 precommit 通道里，见 A/B），根因=precommit 在 staged 面 rc=1（44 次通道运行中 40 次 rc=1，首过率 9%）；
2. 无门号 "-" ×67（详情字段缺失，需补埋点）；
3. BLUEPRINT-FORMAT ×42、MUTABLE-CONST-WITHOUT-FINAL ×35、FOREIGN-CHANGE ×22（claim 外来变更误伤类）、COMPLEXITY-GUARD ×20、SSOT-REDEFINITION ×16、HOT-FILE-BASE-FRESHNESS ×15、HELD-OVERLAP ×11。
全史 top 根因（by_gate）：NOT-CLAIMED 类（未 claim 先改，mean 14.6 件/次）、MUTABLE-CONST（86min 累计）、ALGO-NOTE-SYNC（71min，45 件大件高发）、SSOT-REDEFINITION（91min/48 次）、FOREIGN-CHANGE（67min/39 次）。

**复跑**：`python .runtime/tmp/csx_deep_03_main.py`（C 节）

---

## D. 死信谱系 —— 结论：当前 425 封死信中 97% 为三类机械成因，且 9/25 仍在新增（未修复）

dead/*.json 全量 425 封（含 dead_reason 字段 100%），r1_data/d_dead_letter_lineage.yaml + e_throughput_model.yaml dead_subcauses：

| # | 死因（规整聚类） | 封数 | 状态 | 依据/建议 |
|---|---|---|---|---|
| 1 | **COMMIT_FAILED（落地 git commit 失败）** | **219（51.5%）** | **未修复**（9/25 当天 +18） | 子因 top：GATE-PRECOMMIT-RUN×51、CREATE-GUARD×23、GATE-VOCAB×16、TRANSLATION-COVERAGE×22、PROTECTED-PATHS×9、MAP-ALIGNMENT×9——**本质是"门禁失败被记成死信"**；建议落地侧门禁失败回 rejter 队列而非死信 |
| 2 | **landing 异常** | **86（20.2%）** | 部分未修复 | 子因：注册表三向合并失败×59（死信回退人工）、LandingEnvironmentError×19（landing 环境不可用/路径错）、基底不可知×5 |
| 3 | **基底漂移冲突（入队后 dev 已推进触及同路径）** | **69（16.2%）** | **未修复**（9/25 +4） | 快速重排/路径级互斥可消 |
| 4 | blob 缺失/损坏 | 31（7.3%） | 半修复（blob 存活 22.7h 中位后死） | blob 生命周期 < 队列滞留时长，需 TTL 对齐 |
| 5 | 过期/stale TTL | 12 | 已是兜底机制正常工作 | — |
| 6 | 门禁致死/claim 类/合并冲突/人工 | 8 | 零星 | — |

- **291/425（68%）死信未被 requeue**，携带 3915 个文件不回队——按 24 件/批折算 ≈ 163 批工作量静默蒸发，等价于直接砍掉约 27% 供给。
- 历史积压对照：bottleneck_ledger 累计 dead_letter 17261 条，风暴日 9/18（1858）、9/22（6667）、9/23（5138）；9/24 仍有 2381。死信时延：COMMIT_FAILED 中位 0.5h、blob 中位 22.7h。
- 已修复批次佐证：archive_flashbiz_superseded_20260918 归档目录存在；author identity / index.lock 类（legacy 原因）当前 dead/ 中已绝迹（仅存于 9/15 前的 ledger）。

**复跑**：`python .runtime/tmp/csx_deep_06_dead.py && python .runtime/tmp/csx_deep_07_model.py`（D 节）

---

## E. 吞吐天花板模型 —— 结论：串行关键路径 ~460-600s/笔×4 工=理论上限 25-31 笔/时；实测爆发 10.7、日均 4.3；缺口 62% 来自喂料饥饿+重试环

实测节律（csx_deep_07/09，r1_data/e_throughput_model.yaml、e3_poolwave_busy.yaml）：

| 层 | 实测 |
|---|---|
| git dev 提交（09-22 起） | 380 笔；间隔 p50=343s / mean=725s / p90=1794s |
| 日吞吐 | 9/22:88、9/23:87、**9/24:188**、9/25(至03时):17 |
| 活跃小时吞吐 | p50=4 笔/h，max=18 笔/h |
| 全窗平均 | 4.3 笔/h（380/88.6h） |
| **pool_wave 专窗（22:34-03:14+08，4.67h）** | **50 笔落地 = 10.7 笔/h（爆发上限实测）** |
| 单笔串行关键路径 | landing mean 391s（其中 residual 344s）+ 链内已含门禁 48% ⇒ 全周期 p50≈460-600s |
| 4 工理论上限 | 4×3600/462 ≈ **31 笔/h** |

**缺口归因（自上而下）**：
1. **喂料饥饿**（最大项）：pool_wave 8553 次出口中 8549 次=claim_none（99.95%），no_slot 仅 4 次——队列不是满的而是**空的**；worker 以 1s 轮询空转。专窗内每工仅落地 2.7 笔，工位循环占空比 ~40%。
2. **重试环**（见 C）：近窗 723min 门禁链白烧 + precommit 42 次 rc=1/infra 重跑 134min ⇒ 合计 ~857min/2 天 ≈ **429min/天**。
3. **precommit 慢段/超时**：3×1200s 超时（60min/日）+ 346/497/658s 慢件；fast 子集 300s 封顶触发即整段 20min 报废（infra_error 路径无快速失败）。
4. **四工重复同一大件**：st-metaq-gc 40 件件四工 18:10 并发各跑一遍 ≈ 3×280s=14min/次纯重复。
5. **全局锁串行段**：belt_daemon 32 次 global commit lock 获取失败；drain 单线程 + 3 次"队列项读取失败（疑似损坏）"+ ModuleNotFoundError: scripts.governance（drain 依赖坏，守护半瘫）。

**下一个最大的可回收分钟数排序（近窗实测口径，2 天窗）**：

| 排名 | 可回收项 | 量化 | 预期回收 |
|---|---|---|---|
| 1 | 喂料饥饿（队列常备 ≥4 项） | 工位占空 40%→95% | **+~1100min/天**（4.3→10.7 笔/h 即翻 2.5 倍，无需动门禁） |
| 2 | 重试环（首过率治理：GATE-PRECOMMIT-RUN 前置自检 + CLAIM 类预防） | 723min 白烧链/2 天 | **~360min/天** |
| 3 | precommit 超时快速失败 + hook 与 own-scope 挂钩（A4 的 1 件 346/657s） | 60min 超时 + 尾部慢件 | **~80-100min/天**（并消 p90 尾） |
| 4 | 死信 291 封不回队（补 requeue/重建） | 3915 文件 | 一次性找回 ~163 批存量 |
| 5 | 四工重复执行去重（同件互斥） | 14min/次 | ~15-30min/天 |
| 6 | 全局锁等待/reconciler 扇出（B 未解释 123s/笔 的主候选） | 238min/2 天 | 待插桩后确认，潜在 **~120min/天** |

**复跑**：`python .runtime/tmp/csx_deep_07_model.py && python .runtime/tmp/csx_deep_09_busy.py`

---

## 附：未尽事项（下一轮建议）

1. "-" 阻断事件（67 次）缺 gate_id/detail——埋点缺口，需补；
2. residual 未解释 123s/笔 需落地侧逐相位插桩（全局锁等待单独计时）才能定案为锁等待 vs 对账扇出；
3. st-metaq-gc 四工并发同件属队列侧 claim 语义异常，本次只读未查 pending/processing 状态文件，需队列侧核查 claim 去重；
4. belt_daemon `ModuleNotFoundError: scripts.governance` 使 dual-track drain 半瘫，修复后专窗吞吐可能再抬升；
5. 用户口径 p50=462s 与本次 git 侧 343s 存在窗口差，建议统一以 landing_phase_stats+gate stats 合成口径为准。
