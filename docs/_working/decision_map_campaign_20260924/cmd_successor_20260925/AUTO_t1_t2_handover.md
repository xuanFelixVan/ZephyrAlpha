---
ttl: task_bound
title: LANE-AUTO · T1→T2 守望交接件（断链重建案卷）
created: '2026-09-26'
session: st-qmine-20260925
lane: LANE-AUTO
---

# LANE-AUTO · T1→T2 守望交接件（断链重建案卷）

> 交付三件：`scripts/backtest/t1_t2_handover.py`（幂等交接状态机）＋
> `tests/backtest/test_t1_t2_handover.py`（四证尺+两条附加护栏）＋本案卷。
> 本车道未发车 T2（T1 未完赛，纪律），全部验证走合成数据。

## 一、断链证据（09-25 21:00 总筹实测，本车道接手复核）

1. 上一轮总指挥留的"守望器自动化"（每 30 分钟：T1 完赛自动验收→自动发 T2 900 格→自删，
   外加正午 W-M1 评估窗与死信自愈）只存在于自然语言，从未成为仓内代码或计划任务：
   `qoder_cron list` 仅剩一条已停用旧监控（enabled:false, pauseReason:manual），
   12:00-13:00 窗口零执行痕迹。
2. T1 在跑实证：PID 3584，`factory_grid_executor.py --stage t1 --start 2019-01-04
   --end 2025-09-09`，09-25 11:12:12 起；运行目录 `data/strategy_intake/grid_20260925-111219/`
   （manifest 期末一次落盘，跑中为空=正常；`grid_20260924-213246/` 为空壳遗留）。
3. 仓内反查（内收原则）：Grep `handover`/`t2`/`promote` 于 `scripts/`——无任何既有交接件
   可复用（`factory_grid_executor` 只管跑批、`factory_grid_anova` 只管归因、
   `promotion_combo_gate` 属 league 组合晋级，另一对象不并）。故新建，**替代条目=
   03 号文 §二"守望要点"第 4/5 条的自然语言巡检+T2 接棒**（其"自删"语义改为
   claim.launched 在场即 ALREADY_CLAIMED 空转，由总筹退役薄壳任务）。

## 二、设计（幂等状态机，STATUS 单行机读）

每次调用一遍即退（pull-once，无常驻循环——定时器在外部薄壳，宪法 §9.3 不违反）：

| 状态 | 触发条件 | 退出码 |
|---|---|---|
| WAITING | manifest 缺 且 T1 进程在（psutil cmdline 含 factory_grid_executor 且 --stage t1）| 0 |
| T1_DIED | manifest 缺 且进程亡 → 附 `.runtime/logs/grid_t1*.log` 尾部指针，**不自动重启** | 1 |
| VERDICT_RED | 验收有阻塞判据或垃圾线命中 → 不认领不发车，下轮重验自愈 | 1 |
| SUBSPACE/ACCEPTANCE_ERROR | 选层不可行/产物损坏 → 交人 | 1 |
| ALREADY_CLAIMED | claim 在场（O_EXCL 原子创建防双发 T2=头号护栏）；已发车则使命完成 | 0 |
| STALE_CLAIM | 未发车 claim 超 6h=半路死亡，禁自动删，交人 `--release-claim` | 1 |
| DEFERRED | GPU 独占探测忙（executor 进程在 或 nvidia-smi python 计算进程≥1GB）或 E0 问闸拒 → **撤销本次 claim** 下轮重试 | 0 |
| LAUNCH_FAILED | 发车短窗（25s）内进程亡（含执行器内 E0 拒）→ 撤 claim | 1 |
| LAUNCHED | 无窗脱管子进程存活过观察窗，claim 回填 pid/日志 | 0 |

发车方式=沿用既有 CLI：`python scripts/backtest/factory_grid_executor.py --stage t2
--subspace-json <run>/t2_subspace.json --start 2019-01-04 --end 2025-09-09`
（预算帽钳制/全档成本门/E0 问闸均由执行器自身 fail-closed，本件不旁路、不代跑）。
cmdline 子串 `factory_grid_executor` 已在 `data/runtime/process_reaper_keep.txt`
在册（`ensure_reaper_keep` 幂等补登记）。

产物落位（全部在 T1 run 目录内，与出生证同进退）：`handover_verdict.yaml`（机读验收单：
每条 measured/threshold/pass+垃圾线状态+prereg/manifest sha256）、`t2_subspace.json`
（引擎 `--subspace-json` 既有 .json 消费面，真源=executor main 的 `_json.loads`，
**不为躲 DCR 门禁改格式**；元数据另落 `t2_subspace_meta.yaml`）、`t2_handover_claim.yaml`。

## 三、验收判据引用（口径真源，本件不复制不修改）

- 判据与垃圾触发线 = `docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md` §一（锚：「GPU 成绩单判据」表）。
- 点数/预算/单卡帽 = `config/search_space_prereg.yaml` `budget_caps`（tier1_points/tier2_points/vram.concurrency/cost_gate_in_every_tier）。
- 档位/存活地板/单调容差 = `config/exam_scale_cost_gate.yaml` `cost_gate`（脚本内常数仅镜像 17 号文文字线，数值判据一律从 YAML 读）。
- DSR 行：17 号文度量列=自动管线（n_trial_ledger 累计口径），**非 T2 发车前置**——verdict 中如实标 deferred（诚实位：≠"已完成"声明）。
- 条件轴零样本线：读 `condition_attribution.csv`（MOD-BT-COND-ATTR 产）；归因件未生成时标 not_evaluable（不判命中、留痕汇报）。
- 成本门真实性双径：manifest 有 cost 列走列验证；**当前 T1 实测无该列**（prereg 缺
  `cost_gate_t1_tiers_bp` 字段→`_resolve_stage_cost_tiers` 返回 None→跑批未做 per-point 档位扫描，
  证据=grid_t1_restart2 日志零条 "[prereg] stage=t1 per-point 成本档位"），故自动走"抽查重放"腿
  （≥50 格、冻结种子 20260925、复用引擎 `run_cost_tier_scan` 零重实现，结果缓存进 verdict 防每巡重放）。

## 四、T2 选层规则（S1-S4，确定性可复算）

同一 manifest 必产出同一 `t2_subspace.json`（无随机源；平局一律按维名/层 json 键升序）：

- S1 候选维=manifest values_json 中取值数>1 的维（常量维如 I_cost_tier 不入册，由 schema 折叠）；
- S2 主效应/可砍判定复用 MOD-BT-197 ANOVA（`importance_table`/`prunable_dims`，冻结阈
  PRUNE_THRESHOLD=0.005）——弱维（prunable）=参数展开维，保留全部观测层；
- S3 主效应维各取"层均值主目标（cost_adjusted_sharpe 在场即用，否则 sharpe）前 20%"
  （ceil，至少 1 层）=prereg"主效应前 20% 层"注；全维可砍病态时强制重要性第 1 维入主效应维；
- S4 subspace=逐维值集（执行器笛卡尔过滤语义）；穷尽点数超 tier2_points 时按全局最低层分
  逐层剔除直至 ≤cap（生产用 GridCompiler 真匹配数注入 count_fn，缺省=积算上界）；
  引擎侧另有双保险：`_apply_prereg_budget` 把 --n-samples 钳到 tier2_points、
  stratified_sample 固定 seed 确定性抽样。

复算入口（任何审计者）：`python -c` 载 manifest → `build_t2_subspace` → 与盘上 JSON 比对字节。

## 五、薄壳自动化调用（总筹亲自建 cron，本车道未调 qoder_cron）

每 30 分钟一条命令即可（工作目录任意，脚本自解析仓根）：

```
python D:\ZephyrAlpha\scripts\backtest\t1_t2_handover.py
```

- 机读面=stdout 末行 `STATUS=<token>`+退出码（见 §二表）；日志建议追加写
  `.runtime/logs/t1_t2_handover_cron.log`。
- 退役判据（替代旧"自删"）：verdict 出现 `ALREADY_CLAIMED` 且 claim.launched=true
  （=T2 已发车）后，该薄壳任务即可由总筹注销；人工解锁通道
  `python scripts/backtest/t1_t2_handover.py --release-claim --t1-run grid_<ts>`。
- 冒烟实证（09-26 本车道实测）：现网直调 → `STATUS=WAITING` exit 0，零写入、未触碰 PID 3584。

## 六、红证记录（每条证尺先证"缺陷在即红"，09-26 pytest 8.4.2 / Python 3.12.8 实测）

基线：`python -m pytest tests/backtest/test_t1_t2_handover.py -q` → **7 passed**。
四条证尺逐一注缺陷（改真源脚本→跑目标测试→必红→回改），实录：

| # | 证尺 | 注入缺陷 | 预期 | 实测红证输出（摘要） | 回改后 |
|---|---|---|---|---|---|
| M1 | ②完成率红→不发车 | `GARBLE_COMPLETION_LT = 0.95→0.50`（阈值改错）| test_completion… 失败 | `assert (False is True)`（garbage hit 丢失，`garbage=[]` 而 measured=0.9167）| 7/7 绿 |
| M2 | ③claim 在场拒双发 | 早退分支改 `if _load_claim(...) and False:`（claim 检查去掉）| test_existing_claim… 失败 | 越过认领护栏直达 `[SUBSPACE] expected_points=8` 发车序 | 7/7 绿 |
| M3 | ④在跑不误判死 | WAITING 分支改 `if False and t1_process_alive(...)`| test_running_t1… 失败 | 存活 T1 被判 T1_DIED（断言 status=='WAITING' 红）| 7/7 绿 |
| M4 | ①≤cap 剪枝 | 剪层循环 `while cf(...) > cap` 改 `while False and ...` | test_full_pass… 失败 | probe 全弱维积 64 超 cap=8 未剪回（`pruned_levels` 空断言红）| 7/7 绿 |

旁证回归：`tests/backtest/test_factory_grid_executor.py + test_factory_grid_anova.py`
43 passed（本车道零改动被测引擎，仍按同批跑给落地车道留底）。

## 七、口径矛盾登记（待裁，本车道未改任何预注册值）

1. **12h 时帽 vs 36h 长批**：prereg `budget_caps.single_job_wall_clock_cap_hours: 12`
   （注释=「schedule_gate_policy timebox gpu 键同值（超时=调度层中止）」）与 T1 实测
   09-25 11:12 起跑、预计 09-26 23:15 完赛（≈36h）直接冲突——T1 系 Owner 窗口手动直发，
   绕过了调度层时帽执行面，该字段当前只对调度层有牙齿、对 executor 进程无牙齿（executor
   代码零消费此键，实测 grep）。T2 由本件发车时长按≈900×35.33s≈8.8h<12h 不撞帽，但**守望器
   发车同样不经调度层**——若未来 T2 超时，12h 帽不会自动中止它。处置=如实登记待裁：
   要么裁定"该帽仅约束调度层派生作业"并改注释锚，要么给交接发车链接入 watchdog 中止；
   预注册冻结值未动（跑中禁改 prereg）。
2. **"40bp 档 sharpe≥survival_floor(0)"的字面口径**：17 号文该句挂在"成本门真实性（抽查≥50 格）"
   行内，字面执行=抽查 50 格**全部**在 40bp 档 sharpe≥0 才绿。粗扫总体里 40bp 档负 sharpe 格点
   大概率存在（T0 实测冻结成本档已有 33% 格点 sharpe≤0、最低 -4.78，成本再抬到 40bp 只降不升），
   按字面本守望器几乎必红、几乎永不发车——与
   "终局全自动化"目标冲突。脚本按字面实现（未放宽），命中时如实 VERDICT_RED 交人；
   请总筹裁定抽查样本口径（如"抽查 survivors 层"或"floor 判据改由 T2 复验承担"），**勿改脚本阈值绕过**。
3. **T1 无五档扫描证据**：prereg 缺方案①分层字段 `cost_gate_t1_tiers_bp`（03 号文 §三 升级案第 3 条
   "prereg 语义字段增补+三字段重签"未完），故在跑 T1 manifest 将无 cost 列；本件以"抽查重放"腿
   兜住验收，但"五档全程真跑"的原口径实际未满足——与 §六 M 记录并列呈总筹。

## 八、遗留与交棒

- W-M1 24h 三判据评估与死信自愈重投：不在本件职责（对象不同，内收判据"跨域不同对象不并"），
  仍待总筹以同类"代码薄壳"重建（本件 STATUS 机读面可作其模板）。
- 待落清单见 `landing/lane_auto.yaml`（本车道禁 git/禁 cron，全部经 LANE-LAND）。
