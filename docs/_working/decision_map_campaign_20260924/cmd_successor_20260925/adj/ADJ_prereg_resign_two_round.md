---
ttl: task_bound
title: ADJ 案卷·方案①两轮制 prereg 重签字段清单与 12h 时帽口径矛盾
---

# ADJ · 方案① prereg 重签（含时帽口径矛盾）

> 触发条件：红蓝标定达标（Spearman≥0.99 / top50 重合≥90% / 轻档单格≤8s，17 号文冻结判据）。本卷只汇编"要改哪些字段"，**未改任何阈值**，亦未复核红蓝是否达标（判据面归 LANE-RB）。

## ① 一句话问的是什么

两轮制代码已建成且是**字段门控**的——问的是：**重签 `config/search_space_prereg.yaml` 时要动哪几个字段、每字段的两难在哪，以及"12h 时帽 vs T1 实测 36h"这个矛盾到底是谁过期了**。

## ② 现状实测

### 2.1 现行册子（`config/search_space_prereg.yaml`，81 行，实测全文核过）

| 字段:行号 | 现值 | 消费方（实测定位） |
|---|---|---|
| `frozen_at` :12 | `'2026-09-24T22:00:00+08:00'` | 裁定#413 签发注记 |
| `frozen_by` / `owner_signoff` :13/:14 | `裁定#413` | `factory_grid_executor._apply_prereg_budget`（钳制+fail-closed） |
| `tracks.f06_grid.condition_stratification.cells_eligible_measured` :43 | `9` | 分层键实测注记 |
| `objective.cost_caliber` :20 | `_c4_engine` 冻结土规（佣金 2.5bp 双边+印花 10bp 卖+滑点 5bp）+档位扫描 | 口径声明（散文，无代码消费，实测 grep 无该键消费者） |
| `…cost_gate.tiers_bp` :24 | `[0,5,10,20,40]`（真源=`config/exam_scale_cost_gate.yaml`，册内禁双头改） | `_load_cost_gate_tiers`（`factory_grid_executor.py:938-945`） |
| `budget_caps.wall_clock_hours` :55 | `59` | 声明面 |
| `budget_caps.effective_duty_pct` :56 | `80` | 口径来源 w3_w5_precheck §2.5 |
| `budget_caps.per_point_seconds_measured` :57 | `35.33`（T0 实测回填，run=grid_20260924-080309，7065s/200 格，全成本门真跑） | `_apply_prereg_budget` stage 帽换算 |
| `budget_caps.grid_points_cap` :58 | `25000` | 总帽钳制 |
| `budget_caps.trial0_calibration_points` :59 | `200`（注释："唯一用途=实测 s/格 并回填上一行"） | stage t0 帽 |
| `budget_caps.tier1_points` :60 | `3700` | stage t1 帽 |
| `budget_caps.tier2_points` :61 | `900` | stage t2 帽 |
| `budget_caps.cost_gate_in_every_tier` :62 | `true` | `_apply_prereg_budget` 首条 fail-closed（false/缺失即 SystemExit，实测 `factory_grid_executor.py:994-995`） |
| `budget_caps.single_job_wall_clock_cap_hours` :67 | `12` | **全仓零消费方**（见 2.3） |

### 2.2 两轮制代码已存在，且是"字段在场即生效"（实测）

`scripts/backtest/factory_grid_executor.py`：
- `:919` `STAGED_TIERS_KEY = "cost_gate_t1_tiers_bp"`
- `:947-979` `_resolve_stage_cost_tiers(stage, caps)`：**caps 无该键 → 返回 None → 现行语义逐字零变化**；有键但值为 null → `SystemExit`（"分层语义字段在场但未冻结值（fail-closed）"）；有值 → 校验非空/严格升序/首档必为 0bp（`src/zephyr/backtest/regime_validation/exam_cost_gate.py:100-117` `validate_scan_tiers`），且必须是全档 `[0,5,10,20,40]` 的**子集**，否则 SystemExit（"档位口径漂移，禁开跑"）。启用后 `t1→轻档`、`t0/t2→全档`、`stage=""→不启用`。
- `:996-997` `_apply_prereg_budget` 内：只要键在场就无条件跑一次校验（"冻结册损坏无论哪个 stage 都 fail-closed"）。
- 实测确认：**现册 `config/search_space_prereg.yaml` 内不存在 `cost_gate_t1_tiers_bp`**（全文 81 行核过）→ 两轮制今日仍处休眠，T1 现跑的是全档五成本门（与 35.33s/格实测一致）。
- 因此 09 号文 LK-11"T1 轻档代码缺"与 19 号文①"零新工程（代码已建）"**两句中后者为真**（实测），前者口径已过时。

### 2.3 "12h 时帽 vs 36h 长批"矛盾的实测定性

- `single_job_wall_clock_cap_hours` 全仓出现处**只有两处、且都是 yaml**：`config/search_space_prereg.yaml:67` 与 `config/schedule_gate_policy.yaml:97`（后者键名 `timebox_by_class_hours.gpu: 12`）。实测 grep `src/ scripts/ config/` 无任何 .py 读取前者。
- 后者的唯一代码消费方：`src/zephyr/ai_layer/scheduling/order_daemon.py:126` `"timebox_hours": int(dispatch["timebox_by_class_hours"].get(resource_class, 4))` —— **只是把这个数写进任务书的预算块**。全仓再无第二处消费 `timebox_hours`（实测 grep 仅此 1 处）。
- `scripts/backtest/factory_grid_executor.py` 内**无任何** `deadline / elapsed / abort / SIGTERM` 逻辑（实测 grep 0 命中）。
- T1 运行面实测：进程 PID 3584 `factory_grid_executor.py --stage t1`，2026-09-25 11:12 起，日志 `.runtime/logs/grid_t1_restart2_20260925.log` 21:37 仍在写（引自本轮 LEDGER 实测+本班盘上复核）；预计 36h（引自 HANDOVER 线 1，未复测）。
- **结论：这不是"T1 绕过了调度层时帽"，也不是"时帽口径过期"，而是第三种情形——该字段从来没有中止能力**。`search_space_prereg.yaml:67` 行尾注释"超时=调度层中止"是一句与代码不符的散文断言（实测证伪）。真正有约束意义的窗口声明是 `wall_clock_hours: 59`，而 36h<59h，**与预注册本身不冲突**。

## ③ 可选路径（重签怎么签）

**路径 A：最小增量重签——只加一个字段**
- 改：`budget_caps.cost_gate_t1_tiers_bp: [0, 5]`（须为全档子集、首档 0、严格升序——三条都是代码硬校验，实测）+ 重签 `frozen_at/frozen_by/owner_signoff`。
- 不动：`cost_gate_in_every_tier: true`（代码强制须 true，改 false 直接 SystemExit）、`tiers_bp` 真源、判据数值。
- 连带必答：`tier1_points` 3700→?（19 号文①主张"等效 2 倍（4,640→9,600）"，即 T1 轻档容量≈9,600；但 `per_point_seconds_measured=35.33` 是**全档**实测，轻档单格耗时未知 → 若沿用 35.33 做预算换算，会**系统性高估成本**、把 T1 帽压得过保守）。
- 代价：必须先跑一次 **T0 轻档标定**（`trial0_calibration_points=200` 的设计用途正是"实测 s/格 并回填"，实测注释原文）→ 新增 200 格 GPU 占用窗（与 T1 单卡互斥，`vram.concurrency: 1`，实测）。
- 不可逆点：**"字段在场但值为 null"= 全 stage fail-closed**（实测 `:963`）→ 半签状态会让下一次任何 T0/T1/T2 起跑都直接炸；所以"加键"与"给值"必须在同一 commit 完成（净零/原子性纪律）。

**路径 B：整册版本升 v3 重签（含口径声明重写）**
- 改：schema_version 2.0.0→3.0.0、objective.cost_caliber 补两轮制分档描述、`per_point_seconds_measured` 拆为 `{t1_light, full}` 两值、`wall_clock_hours` 重排、`:67` 假注释删除或改为"预算记账口径，无运行时中止力"。
- 代价：改动面大、与"同卷同纪"预注册纪律的摩擦面大（改判据=作废重开），审查成本高。
- 不可逆点：schema_version 一升，旧册的对照基线即断（若旧值未留档则不可回读）。

**路径 C：不重签，改跑"全档 T1 两轮"**
- 用现有全档语义跑两轮（第一轮粗筛用别的机械判据、非成本档）→ 避开 prereg 冲突，但与 19 号文①"等效 2 倍"的收益来源不再一致，等于放弃①。
- 代价：低（零字段改动）；收益：也低。

## ④ 专业对照（外部论据，URL+发布方+年份）

1. **预注册"改=作废重开"是学术与量化两侧的通则**：Registered Reports 体裁的创立论文（Chambers, *Cortex* 2013）与 *Nature Human Behaviour*/COS 的 Registered Reports 政策均规定：数据揭示前的**实质性方法变更须重走评审、否则该文降级为 unregistered**；量化侧 Harvey, Liu & Zhu（*Review of Financial Studies* 2016，"…and the Cross-Section of Expected Returns"）把"同一假设被反复试"计入试验次数并要求 t>3 门槛——二者共同支持"新增分档语义=新预注册而非改字段"。
   - https://www.sciencedirect.com/journal/cortex （Chambers 2013, Cortex, 2013）
   - https://academic.oup.com/rfs/article/29/1/5/1841737 （Oxford UP / RFS，2016）
   - https://www.cos.io/initiatives/registered-reports （Center for Open Science，2024 更新）
2. **作业时限要"真能杀"才叫上限**：Kubernetes Job 的 `activeDeadlineSeconds` 是**运行时**由控制器强制中止的绝对时限，官方文档明确它与"预算/记账"无关；而调度侧的资源配额（ResourceQuota / admission-time budget）只在**准入时**判定。二者区分正对应本仓 `timebox_by_class_hours`（准入/任务书层）与"缺一个运行时 kill"的现状。
   - https://kubernetes.io/docs/concepts/workloads/controllers/job/#job-termination-and-cleanup （Kubernetes 官方文档，2024 更新）
   - https://research.google/pubs/large-scale-cluster-management-at-google-with-borg/ （Verma, Wilkes, Neugebor，OSDI 2015；区分 task 层级与 deadline/monitored 语义）
3. **分档成本扫描的社区先例**：López de Prado，*Advances in Financial Machine Learning*（Wiley，2018）的 CPCV/deflated Sharpe 框架要求"每次试验的算力与成本口径先于结果声明"，与 `cost_gate_in_every_tier: true`（禁跳档）同构——即"轻档粗筛"必须声明为**扫描面**而非**判定面**（本仓代码注释 `validate_scan_tiers` 明写"扫描面，非判定面"、终审仍在 T2 全档，实测 `exam_cost_gate.py:100-105`），这点与业界做法一致，可作为"路径 A 合法"的专业背书。
   - https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning%2C+1st+Edition-p-9781119482086 （Wiley，2018）

来源三侧独立（学术出版/云原生官方文档/量化专著），检索日期 2026-09-25。

## ⑤ 风险（做错的最坏情形）

- **资金安全：零暴露**。搜索面产物进池仍需 `GRADUATED_PACKAGES`（实测恒空）与毕业门，不会因重签直接产生下单行为。
- 半签风险（A 的最坏形态）：`cost_gate_t1_tiers_bp:` 写成空值/漏值 → **下一个起跑的 stage 无论 t0/t1/t2 全炸**（实测 fail-closed），表现为"GPU 窗白白排队"。
- 高估成本风险：不重测轻档 s/格 就沿用 35.33 → T1 帽按错的换算被钳小 → ①宣称的 2 倍收益拿不到，还会误判"两轮制无收益"而错杀一条提速路线（**这是最坏的认识论损失，不是资金损失**）。
- 试验数污染风险：轻档粗筛若不计入 N_eff/`n_trial_ledger`（e7_defense.ledger_required: true，实测在册），DSR 分母失真 → 成绩单过优。此为预注册纪律的硬红线。
- 口径矛盾处置风险：把 `:67` 注释当事实继续引用，会在未来某次"超时为何没中止"的追查里再耗一轮（本仓已有多次"文档计数漂移"事故记录）。

## ⑥ 解锁依赖

1. **红蓝达标结论**（LANE-RB）——本项的触发前提，本班未采证。
2. **T0 轻档标定跑**（200 格）→ 得 `s/格(light)` 实测值，A 路径的 `tier1_points` 才有可签依据；须等 T1 完赛让出单卡（`vram.concurrency: 1`）。
3. 一句裁定："轻档扫描是否计入 N_eff/族下限"——**若不计入，须在同一裁定里说明为什么不算试次膨胀**，否则 E7 防线自相矛盾。
4. `:67` 注释口径的处置（改注释文字=文档级，不需要重签，但要随批）。

## ⑦ 一句话推荐（推荐待总筹拍）

推荐 **A（最小增量重签：同 commit 内"加键+给值+重签三字段"，并强制先跑 T0 轻档标定回填 `per_point_seconds_measured`）**；同时把"12h 时帽"矛盾**改判为文档口径错误**（该字段零运行时消费，实测），处置=把 `search_space_prereg.yaml:67` 行尾"超时=调度层中止"改为如实的"任务书预算记账口径，无运行时中止力"，不改数值、不新开窗口项。
