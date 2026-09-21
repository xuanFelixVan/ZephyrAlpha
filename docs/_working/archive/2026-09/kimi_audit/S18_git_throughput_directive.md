---
ttl: task_bound
rule_form: data
verifiability: manual
title: S18 战场指令书——提交与门禁链路提速（治本）+ 子代理并发协议
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-17
---

# S18 战场指令书 + 子代理并发开工协议

> 配套：[owner_addendum_v2_20260917.md](owner_addendum_v2_20260917.md)（时间表与死线）、[kimi_deep_adjudication.md](kimi_deep_adjudication.md)（十五战场与三问边界）。
> 本件承载 S18 的判据与任务卡，指令正文只给指针——**结论入真源，不散在对话里**。

## 0. 为什么这件事排进今晚（Owner 判定）

本项目夜间 50–100 个施工队并发，**提交与门禁链路的吞吐 = 全项目的开发速度**。这条链快 50%，等于所有车道的交付快 50%。它和"赚钱策略"并列当前最高优先。

Owner 的验收口径是**治本**：不接受"把超时从 180s 调到 600s"这类止痛交付。

## 1. 证据真源（已实测，按此取证，别去翻报告）

| 账本 / 位置 | 体量 | 覆盖 | 用来回答 |
|---|---|---|---|
| `.runtime/audit/commit_block_events.jsonl` | 1191 行 | 09-13→09-17 | 堵了多少次、每次堵在哪个门禁、堵多久 |
| `.runtime/audit/bottleneck_ledger.jsonl`（**堵点本**） | 2312 行 | 09-15→09-17 | 堵点归因主料：设计如此 vs 实现低效 |
| `.runtime/audit/gate_execution_stats.jsonl` | 735 行 | 09-15→09-17 | 每个门禁的耗时分布与触发率 |
| `.runtime/audit/preflight_events.jsonl` | 1124 行 | 09-15→09-17 | 提交前检查的失败/耗时结构 |
| `.runtime/audit/hook_tracked_drift.jsonl` | 1994 行 | 08-15→09-17 | 钩子漂移提醒是否为噪声 |
| `.runtime/audit/safe_write.jsonl` | 43712 行 | 08-23→09-17 | CAS 写热文件的实际频率与冲突率 |
| `.runtime/audit/worktree_drift_watchdog.jsonl` | **156617 行** | 08-15→ | **嫌疑犯：一个看门狗自身即高频写入源** |
| `.runtime/commit_queue/*.seq` | 322 个（近 24h 有动作 44） | — | 队列深度、死信成因、串行化行为 |
| `.runtime/abuse_monitor/abuse_baseline.json`、`.runtime/ai_error_patterns/aggregated_patterns.json` | — | — | 滥用基线与 AI 错误模式聚合 |

**git 侧实测（同一时窗，可直接引用）**：

- 近 24h 314 笔提交中衍生/治理税 **78 笔 = 24.8%**（integrity post-flush 重登记 29、其他 chore 23、reconciler batched 19、merge 4、watchdog 派生收敛 3）。
- **Kimi 自己这段班次更狠**：13:00→17:34 共 28 笔，其中真实交付 5 笔（S1/S2/S13/S3/S14 各一）+ 衍生 7 笔（integrity 4、reconciler 1、watchdog 2）——**衍生税 ≈58%**，且 `chore(integrity) post-flush re-register` 明写"时序竞态治本 2026-08-02"却仍以每 3–4 分钟一次的频率复发。
- 提交堵点提醒近 24h **215 次**：TOP ×86（P50 **81s**）、CLAIM-REQUIRED ×40（P50 33s）、DANGLING-REFERENCE ×16（P50 35s）。
- `GATE-REGENERATE: reconciler timed out (timeout=180s)`；`DEPGRAPH-FRESHNESS WARN 1048min`；`SECRET-REGISTRY-DRIFT required_key_missing[...]` 噪声。

## 2. 产出形状（S18 交付物，缺一即未做）

### 2.1 根因表（主件）`docs/_working/kimi_audit/S18_提交链路根因表.md`

一行一病灶，五栏：

`编号｜现象（含日志计数与 file:line）｜机理（为什么自激 / 为什么慢 / 为什么会互相踩）｜治本改法（改哪一层结构）｜为何不再复发（机读判据 + 反例样本 + 什么算红）`

加两列标注：`symptomatic?`（见 §2.2）、`连锁半径`（这一层高摩擦或静默失效时，多少个车道的工时/哪些"已通过"结论同时失去意义——即严重级，判据同 S4）。

**以下三类不算治本，写进表必须标 `symptomatic`**：①加大超时值（180s→600s）；②加重试/退避；③加日志或把日志降级。
**治本长这样**：消除自激触发环（谁触发谁、为什么不停下来）、O(全仓) 扫描改 O(diff) 且差分基线可复用（复用 `604f414846` 已落地的"git index + HEAD 基线差分 + 全绿短路"口径）、串行单通道改结构化并发、看门狗只在状态变化时落盘、衍生提交并入触发它的那一笔而非另起一笔。

### 2.2 并发吞吐模型（必答，这是只有强模型能做的部分）

给定：夜间 N 个车道（N=50/100 两档）、每车道每次提交的 own-file 数分布（可从 `safe_write.jsonl` 与队列 seq 估）、门禁单件耗时（`gate_execution_stats.jsonl`）、claim TTL 30min。
求：**当前架构的系统上限（笔/小时）**，以及三条瓶颈各自的提速倍数——
①锁与 claim 粒度；②commit-queue serializer 单通道；③内容扫描型门禁的 O(仓库) 成本。
每条给"改到什么程度、上限抬到多少笔/小时、副作用半径"。**没有这个模型的 S18 视为未完成。**

### 2.3 放行裁定书（一页一条，Owner 签即生效）

落 `adjudications/`，至少覆盖：`S18-R1` 噪声型提醒降级/改条件触发清单、`S18-R2` 衍生提交并入策略（integrity 重登记是否可同 commit 原子化）、`S18-R3` 并发通道数与锁粒度改制、`S18-R4` 不可放松门禁白名单（钱闸 / own-scope 差分口径 / 内容寻址 / POST-COMMIT-GUARD / RULING-REFERENCE）。

### 2.4 Flash 夜间施工包（夜间免费档执行）

每条含：改动文件清单、机读判据（阈值 + 反例样本 + 什么算红）、验收命令、预期节省（分钟/夜）、回滚方式。**判据写不出来的条目=还没想清楚，退回重想。**

## 3. 权限边界（防顺手重构）

- **允许直改**（结构性小改，改完跑相关单测、按战场粒度提交）：全绿短路、差分基线复用既有口径、锁粒度收窄、自激触发改条件触发。
- **不许动**（一律走 §2.3 裁定书等 Owner 签）：任何门禁的语义与判据、删门禁、`risk_tier_registry.yaml` 门位、serializer 通道数、`process_reaper` 语义。
- 止痛件（超时/重试/日志）**只准记账进根因表，不准当作治本结论提交**。

## 4. 子代理并发开工协议（Owner 明令：本班次起全面启用）

**执行形态**：尽量开启最大并发子代理，L0 统筹全局；分层子代理执行任务，有助于统揽全局。

分层（主代理只做判断与收口，取证与施工下沉）：

- **L0 主代理（Kimi 本人）**：战场排序、裁定、双角色复算反驳、根因表判读、统一提交、release 锁、收官自检。**L0 不做批量文件读写。**
- **L1  lane 长（每 lane 一个子代理）**：统揽本 lane 全局，拆任务给 L2，回收并压缩成 ≤1 页结论 + 证据锚点清单。
- **L2 执行子代理**：单一目标、明确产物路径、机读判据、越界清单。

**并发写纪律（硬）**：

1. 子代理**一律禁 commit**；改动留在工作区，交回 `file:line` 清单 + 自家测试结果，由 L0 按"一个战场一批"走 GitCommitGateway。
2. 每个子代理的报告**各占一个文件**（`docs/_working/kimi_audit/lane_reports/<lane_id>.md`），天然不互踩；改既有文件必先 `lock_files.py acquire <file> kimi-audit-l<n>`。
3. 热文件（注册表 / AGENTS.md / tracker / ROOR / `standards.yaml`）只准 L0 用 `safe_write_text` + `expected_base_sha256` 写，L1/L2 只出建议。
4. 子代理禁改 §3"不许动"清单里的任何东西；越界即整包作废。
5. L0 每完成一次合并即写一行台账（lane_id / 启动 / 结论 / 采纳或否决 / 理由），防上下文压缩后失忆。
6. 派完全部 lane 立刻转自己的战场，检查点一次回收，禁轮询禁 sleep/tail 盯盘。

**lane 布置（L0 一次全部派出，随后按检查点回收）**：

| lane | 目标 | 主料 | 交付 |
|---|---|---|---|
| **A1 Git 链路·提交税** | 314 笔提交逐笔归类必然代价 vs 自激循环，算可消除比例；查 post-flush 复发根因 | git log + `.runtime/commit_queue/*.seq` | `lane_reports/A1.md` |
| **A2 Git 链路·堵点** | 堵点本 2312 行 + `commit_block_events` 1191 行归因（设计如此 / 实现低效），出堵点榜 | 两份 jsonl | `lane_reports/A2.md` |
| **A3 Git 链路·并发建模** | §2.2 吞吐模型 + 三瓶颈提速倍数；含 watchdog 156k 行自激取证 | `gate_execution_stats.jsonl` + `worktree_drift_watchdog.jsonl` + 队列代码 | `lane_reports/A3.md` |
| **B1 前视取证（S14）** | 逐条在册策略把信号取数路径回溯到"数据落地时刻"，与下单时刻比较（L0 已实锤 `pit_shift` 负值静默吞成同 bar，见 `146238dabc`，沿这条模式继续扫） | `strategy_runner.py` / `framework_composer.py` / 各策略卡 | `lane_reports/B1.md` |
| **B2 假绿清单（S15）** | 抽 P0 路径做变异验证："我改坏被测代码它会不会红"；三类假绿逐个构造 | `tests/` + 昨夜新落库测试 | `lane_reports/B2.md` |
| **B3 外推合法性（S8）** | 已交付结论 × 可得数据 对账（399106 断更 / 竞价窗口缺口 / 指数分钟源 EMPTY / 北向停发 / 期货主力连续历史长度） | 底册 §2 + 数据地形 | `lane_reports/B3.md` |
| **C1 架构减法（S10）** | 542 蓝图 / 73 注册表 建·合·废·挂机械归类，只出表不决策 | `architecture_model/index.yaml` + ROOR | `lane_reports/C1.md` |
| **C2 契约草稿（S9）** | AI 层 ↔ 业务层归属边界草稿 + 缺口清单 | `ai_layer_vision/` 各 DESIGN.md | `lane_reports/C2.md` |

L0 亲自留手不外包的：S4 收口（审校器 fail-open 判定）、S5 定尺子 + 翻转清单、S3 族级批文、S6/S7 判读（实验已回读，只剩裁定）、S18 根因表定稿与裁定书、收官。

## 5. 执行节奏

尽可能多开并发、全速推进、执行多少算多少。每条 lane 回收即判读、判读即落盘、落盘即提交（按战场粒度走 GitCommitGateway），不攒批、不等齐。
