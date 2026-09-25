---
ttl: task_bound
---

# DAY 车道：交易日整日跳过 + 哨兵尺子选错 + 告警死总线

lane: LANE-DAY | session: st-qmine-20260925 | 执行人: P0 修复车道 | 状态: 三件已办（①证伪 ②治尺已施工+双红证 ③判退役+定性零处置），零 git 操作，待落清单见 §⑤
来源: L09 深挖交回（`landing/lane_mine_l09.yaml` §cross_lane_hard_evidence / §trd_a06_alert_acceptance_line）
一句话结论: **"09-25 交易日被整日跳过"不成立（当日中秋休市，真源日历无开市行）；但哨兵用 `max()` 当尺是
独立的选型错误——它今日报平安属"歪打"，跳日/超前行都能把它捂死，本卷把它换成期望交易日口径并出了双红证。**
约束遵守: 禁 git add/commit/push、禁跑 git_commit.py/commit_queue.py、DB 只读经 DatabaseService、
未碰 ex_core / ops_guard.py / evaporation_blackbox.py / gpu_rewrite、pytest 全带显式路径、零 GPU、未杀进程、未修生产数据。

## ① 跳日复证（只读探针）

结论：**交案前提不成立——2026-09-25 在真源交易日历里不是交易日（中秋节休市），"该交易日被整日跳过"是误判。**
探针（只读，`zephyr.infrastructure.database_service` reader，`.runtime/tmp/lane_day_probe.py` + `lane_day_probe2.py`，
跑于 2026-09-25 夜）：

| 断言（交案原文） | 实测 | 判定 |
|---|---|---|
| `last_audit.json` 当日零记号 | 35 记号，无任何 `*:2026-09-25` 键；末批值 = `2026-09-25T00:42–00:43Z`（=09-25 08:43 北京）写的是 `pf_alloc_daily:2026-09-24` 等 09-24 键 | 事实成立，但**释义不成立**：休市日无当日记号是正常态 |
| `kline_index max = 2026-09-24` | 2026-09-24 | 事实成立，释义不成立（09-25 休市，本就不该有 09-25 bar） |
| `decision_daily` 缺 09-25 目标行 | 缺 | **不是缺陷**：09-25 非交易日，本就不该有行 |
| `decision_daily` 有 09-28 目标行（"未来日"） | 存在 1 行：target=2026-09-28 / asof_data_date=2026-09-24 / ingest=2026-09-25T00:43Z | **不是未来日**：09-24 的次开市日正是 09-28（`trade_date` 列注释="拍板生效日=次交易日"） |

日历真源 `c1_market.trade_calendar`（exchange=SSE，8797 行全 `is_open=1`，即"只存开市日"，覆盖 1990-12-19..2026-12-31）：
2026-09 开市日 = …09-21,09-22,09-23,09-24,**09-28**,09-29,09-30（09-25/26/27 零行）；10-01..10-07 零行、10-08/09 开市。
2025 同期对照件自洽（09-29/30 开、10-01..10-08 零行、10-09/10 开）⇒ 日历不是"尾部缺数据"，是按公告只落开市日。
外部独立复核（非本仓真源，仅旁证，见 §⑧）：2026-09-25 为中秋节、沪深交易所休市。

`decision_daily` 目标日分布（72 行全量）：09-16（66 行，单次批量）· 09-21(2, asof 09-18) · 09-22(asof 09-21) ·
09-23(asof 09-22) · 09-24(asof 09-23) · 09-28(asof 09-24)——**逐档"次开市日"完全连续，零跳日**。

⇒ 交案的"监控报了平安=假绿"这一次没有成立：哨兵今日 lag=0 的**结论是对的**（只是尺子选型仍错，见 §②）。
⇒ 同族另两条不依赖此前提，继续办：`alert_aggregator` 全仓零生产 import（§③a，实测复核成立）、
`attribution_results` 实测 **0 行**（§③a 附带复证成立）。

唯一残留的真异常（降级为观察项，非跳日）：target=09-28 那行由 **09-25 08:43 北京晨批**（与 sim_ledger/sim_journal/
attribution/pf_alloc 同批）产出，而 09-21/22/23/24 四行均由前一交易日 **16:3x–16:5x 北京晚批**产出
（09-21 另有 05:18 追加行）⇒ 产出节拍从"前一交易日收盘后"漂到"当日盘前"，离 09:40 哨兵仅 57 分钟余量。
登记为 L09-S6/S1 侧的节拍观察项，本车道不改写侧。

停手声明：按"前提被证伪即停"，本车道**不**继续构造"整日跳过"叙事，也**不**修任何生产数据；
②③ 两项各自独立成立（尺子选型缺陷可由合成场景证明、死总线实测零消费），故照常交付。

## ② 治尺：哨兵滞后判据改期望交易日口径（已施工，红证已出）

施工文件唯一：`scripts/governance/decision_chain_sentinel.py`（+ 其自有测试
`tests/governance/test_decision_chain_sentinel.py`）。**未动任何阈值册/其他判据文件**，未新建 gate/脚本。

旧尺病灶（HEAD 版逐行）：`last = SELECT max(trade_date) FROM decision_daily`（**无上界**），
`ref = min(日历最近开市日, kline_index max)`，`lag = (last, ref] 开市日数 if ref > last else 0`。
⇒ 台账里只要存在任一"超前于当日"的行——而"次交易日口径下 09-25 晨批写 target=09-28"正是**合法常态**——
`last > ref` 恒成立 ⇒ lag 恒 0 ⇒ 无论尾部还是中间整日缺失，全部被 max 掩盖。这就是尺子选错，
与本次 09-25 是否跳日无关（见 §①：那次没跳）。

新尺（期望交易日口径，交易日历真源驱动，**零硬编码 2026 节假日**）：
- 期望日 `E = min(cal_date) FROM c1_market.trade_calendar FINAL WHERE exchange='SSE' AND is_open=1 AND cal_date >= 今日`
  （=本应产出的最新一日；休市/周末自动跳到次开市日，不再靠人肉判"今天算不算交易日"）；
- 实评日 `act = max(trade_date) WHERE trade_date <= E`（**带上界**，超前行不得参与判据）；
- `act == E` → ok, lag=0；`act != E` → **缺即告警**（exit 4），`lag = (act, E]` 开市日数；
- 超前行只以 `decision_max_unclamped` / `rows_beyond_axis` 两字段露出供人工判异常；
- 降级路径（日历"期望日腿"查询失败或超出日历覆盖 2026-12-31）→ 回落到参照日轴，`--lag-days`（默认 2，
  真源 `scripts/governance/_shared/thresholds.py` 未动）语义原样保留，记录里 `ruler="reference_day_degraded"` 留痕；
- 全史零行=断供、双腿全废=error+exit 8、fail-soft 单行日志——原契约不变；时间戳仍只走 `now_utc()`（RULE-SCHEMA-TZ，零墙钟新算法）。

红证 A（**生产 CH 只读实跑**，`--alert-log` 重定向 `.runtime/tmp/`，未写生产告警文件）：
```
python .runtime/tmp/lane_day_old_sentinel_head.py --ref-date 2026-09-17  → INFO 决策链在供（lag=0 < 2）        old_exit=0   ← 旧尺哑火
python scripts/governance/decision_chain_sentinel.py --ref-date 2026-09-17 → WARNING 期望交易日 2026-09-17 无 decision_daily 行
                                       （最近实评日 2026-09-16, 缺勤 1 个交易日）  new_exit=4   ← 新尺报警
python scripts/governance/decision_chain_sentinel.py --ref-date 2026-09-25 → INFO 期望交易日 2026-09-28 已有决策行  exit=0  ← 休市跳档不误鸣
```
（09-17 那行 jsonl 全字段在案：`ruler=expected_open_day, last_decision_date=2026-09-16,
decision_max_unclamped=2026-09-28, rows_beyond_axis=true`——超前行把旧尺顶成 lag=0 的机理直接可见。）

红证 B（合成场景 + 回归钉，`python -m pytest tests/governance/test_decision_chain_sentinel.py -q` → **17 passed**）：
- `test_tail_skipped_trading_day_alerts_while_legacy_max_ruler_was_silent`：日历开市 09-25、台账
  {09-22,09-23,09-24,09-28} ⇒ 新尺 alert（lag=1，点名 09-25）；同批事实上 `_legacy_max_ruler(...)==("ok",0)`
  被断言钉住=旧尺哑火不可回退；
- `test_holiday_gap_expected_day_jumps_to_next_open_day_and_stays_green`：09-25 休市形态 ⇒ E=09-28 行在 ⇒ 绿且不写告警行；
- `test_expected_day_axis_comes_from_calendar_true_source`：期望日必须问 `trade_calendar`（表名经 TableRegistry），
  且件内禁立第二份节假日真源；
- `test_lag_boundary_equals_threshold_alerts_below_passes` 改写为在**降级轴**上继续守 `--lag-days` 边界（N 鸣 / <N 放行），
  阈值旋钮未被废除，只是不再能压制"当日无计划"。

## ③ 告警总线定性 + 09-28 行定性

### ③a `alert_aggregator`（MOD-RPT-030）：判**退役**，出死亡证明（本车道零删除）

反查三路（先反查再动手，留审计）：
1. Grep 全仓排除 `docs/_working/`：`src/ scripts/ schemas/ config/` 内命中仅 **件本体 + __pycache__** ⇒ 生产零 import 复证成立；
   其余命中全是册籍登记（module_translation_registry:46079、capability_canonical_file_registry:10524/10552/23883、
   candidate_module_registry:8461/13848-13854、path_ownership_map:43087/55967、
   `_domain_reporting/algo_flow/alert_aggregator.yaml` + index.md:23）与其自测 `tests/reporting/test_alert_aggregator.py`；
   `notification_channel_senders.py:5,81` 只在头注里把它列为"候选消费方"，无代码依赖。
2. `CapabilityLookup().find("alert aggregator 告警聚合", session_id="st-qmine-20260925")` 及另两条关键词 ⇒ **零命中**（能力反查审计已落 LOOKUP_AUDIT_DIR）。
3. 件自证：`[CONSUMERS] （候选：总览页"今日告警"卡…）`= 意向而非实接；`[MATURITY] testing`；
   四条 THD-TRD-001..004 在 `alert_threshold_registry.yaml:961-1032` 全 `status: design`，
   consumer 字段同指一个未建件"trading 运行时监控（G2b/G5 接线点）" ⇒ 0/4 有消费代码复证成立。

在产替代总线实证（这才是判退役的依据，不是"没接线就删"）：
- 唯一合法出口 = **OpsAlertFeed**（MOD-INF-OPS-ALERT-FEED）：板文件 `.runtime/ops_notifications/notifications.jsonl`
  实测 531 KB、最后写 2026-09-25 22:23（活跃在产），投影端点 `GET /api/ops-notifications`
  （`src/zephyr/frontend/dashboard/api_server.py:4415-4462`，头注明写"通知唯一出口=前端 promotion 页，飞书/SMTP 裁撤"）；
- 职责重叠逐条对上：确定性 id/同批去重 ↔ 板内 dedup key 静默窗口刷新；严重度分级 ↔ `config/alert_rules.yaml`；
  解除态 ↔ `resolve()` + resolved_at 灰显；派发外部通道 ↔ **已裁定删除**，故 alert_aggregator 的
  `min_dispatch_severity`+`notification_manager` 派发段在现行政策下**无合法去处**；
- 三源自各有在产去向：`data_quality`→`zephyr.data.alerter` + `zephyr.data.alert_webhook_dispatch`
  （`scan_critical_failures`/`scan_kill_switch`/`dispatch_on_failure_event`，blocked/failed 投影到真板，
  `tests/data/test_alert_webhook_dispatch.py` ①-⑥ 在案）；`risk`→`risk/core/alert_generator` 由风控编排消费；
  `backtest`→无生产者；
- 监测件接板的既有姿势有先例可循：`alerts/resource_schedule_alerts.py`（自报 module_id 调 publish）、
  车道 G 广度断供哨兵（`tests/data/implementations/test_breadth_freshness_alerts.py` 头注"唯一出口=OpsAlertFeed（promotion 页）"）。

判据落点（宪法 §4.2 内收铁律两条同时命中）：**零触发零消费→退役**；**同域重复簇→收敛唯一**。
否弃"接线"方案的理由（如实记，别把它读成偷懒）：给这条死总线补生产者＝在 OpsAlertFeed 之外再立一份
聚合/去重/派发真源，且其派发段只能挂外部通道——与"通知唯一出口=前端 promotion 页"的现行政策相冲，
违 §9.2/§4.1；四条交易告警的正解是**直接 publish 进 OpsAlertFeed**（接线位=L09-C05"交易运行时监控"那一个件，
非四个），该件建不建属 Owner 裁定项，本车道不代拍、不代建。
连带改判建议：**L09-S6-G1 原主张"接上 alert_aggregator（零新件纯接线）"应改为"接 OpsAlertFeed；alert_aggregator 退役"**，
否则 P0 清单会把车道引向第二总线。

退役删除面清单（**净删注册表=high 门位，须 Owner 签批后经正式提交批执行，本车道一律未动**）：
件本体、`tests/reporting/test_alert_aggregator.py`、algo_flow yaml + index 行、
module_translation_registry 1 条、capability_canonical_file_registry 3 条、candidate_module_registry 2 段、
path_ownership_map 2 条、`notification_channel_senders.py:5` 头注候选项，最后 `generate_project_depgraph.py --force` 重建。

### ③b 09-28 那行：定性=**合法产出，非日期算错、非测试写进生产表，零处置**

写侧真源对拍（`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:730-735`）：
`run_id = f"decision-{day}-{uuid6}"` 里 `day`=**数据日**，`trade_date = cal.get("target_date") or day` 里
`target_date` 由 S1 日历解析件从 `trade_calendar` 取"次开市日"。实测行全字段：
`run_id=decision-2026-09-24-685521 / trade_date=2026-09-28 / asof_data_date=2026-09-24 /
calendar_source="trade_calendar" / degraded=1 / degrade_reasons="D2_gate_absent:L2" /
gate_snapshot_json.l1.run_id=VAL-P0-20260924-164044`。
⇒ 09-24 的次开市日正是 09-28（09-25 中秋+09-26/27 周末休市），该行是日历口径下的**当期正确目标日**；
`calendar_source` 字段自带真源声明，payload 满是生产语义（门快照、预算带、降级原因、v1 安全态注记），
无任何 pytest/tmp_path 痕迹 ⇒ 宪法 §9.6"测试写进生产表"假设也不成立。
对照同批五行的 run_id/asof/target 三元组（09-21→asof 09-18、09-22→21、09-23→22、09-24→23、09-28→24）
**逐档连续，零跳日**。

处置建议：**不改**。`UPDATE/DELETE` 在此属不必要+不可逆（RULE-DATA-OPS 三步验证第一关即不过），
快照制本身也只许追加新 run_id 更正行（件头注 §18"快照只增不改"）；本次连追加都不需要。
真正要防的是**这次误判本身**——它差点把一行正确数据定性成"未来日脏数据"送去修数。
防复发已随 §② 落进代码：`rows_beyond_axis`/`decision_max_unclamped` 只露出、不参与判据，
期望日轴由日历真源给出 ⇒ 后续任何车道再拿 `max()` 当尺都会重演同一误判，本件已把它堵死。
残留观察项（移交，非本车道改）：该行由 09-25 08:43 北京晨批产出，而 09-21..09-24 四行均由前一交易日
16:3x-16:5x 晚批产出 ⇒ 拍板节拍从"前一交易日收盘后"漂到"当日盘前"，与 09:40 哨兵仅隔 57 分钟，
抗抖动余量过窄（随 L09-C01 编排器收拢一并看）。

## ④ 剩余缺口（如实报差多少）

1. 四条交易告警仍是 **0/4 有消费代码、0/4 演练**——本车道只把"接哪条总线"判清（OpsAlertFeed）并出退役证明，
   未建消费者件（L09-C05，Owner 裁定项）。
2. `attribution_results` 实测仍 **0 行**（sqlite `data/databases/governance.db` 只读复核=0），归因五接头零焊——属 S7 车道，本车道未动。
3. `alert_aggregator` 退役的删除动作未执行（门位在 Owner 侧 + 本车道禁 commit），只出了死亡证明与清单。
4. 描述面同步待落批执行：`module_translation_registry` 该件 `desc_zh` 仍是旧口径"滞后超阈值即告警"（热文件，须走
   `safe_write_text`），`scripts/governance/script_manifest.yaml` 系 `generate_script_manifest.py` 机生（我已改 `__manifest__`
   描述，需重生成），`register_decision_chain_sentinel_task.ps1` 任务描述文案——三者均属**同批文档/机生口径同步**，见 landing 清单。
5. §① 前提证伪后，"跳日"这条硬证据在 L09 册与 `_INDEX_MINE` 的表述需更正（总筹侧回写，本车道未改他会话册）。

## ⑤ 待落清单指针

见 `landing/lane_day.yaml`（本车道零 git 操作，主区 index 他人条目一律未碰）。
**落地前先读 §⑥**：本车道两件在 index 里是 `D`+`??` 分裂态，不先翻就是"提交即删除"。

## ⑥ 落袋阻断风险（实测主区 index，非本车道造成）

`git status --porcelain` 实测本车道两个施工文件当前是 **`D `（index 里被记为已删除）+ `??`（工作区副本未跟踪）** 的分裂态：

```
AM docs/.../DAY_daily_loop_skip.md
D  scripts/governance/decision_chain_sentinel.py        ?? scripts/governance/decision_chain_sentinel.py
D  tests/governance/test_decision_chain_sentinel.py     ?? tests/governance/test_decision_chain_sentinel.py
?? docs/.../landing/lane_day.yaml
```

同批 index 共有 **27 条 `D`**（533 A / 86 M / 27 D），且不止我这俩：
`scripts/register_decision_chain_sentinel_task.ps1`、`scripts/governance/evaporation_blackbox.py`（LANE-EV 产物）、
`replay_gate_verdicts.py`、`duckdb_runtime_gate.py`、`_tree_view.py`、多份 tests、5 个 vocabulary yaml、
1 个 csv、1 个 blueprint.md 全在列——**没有任何同名的 A/R 对手条目**（`git diff --cached --name-status | grep -i sentinel`
只出 D），故不是改名袋，是"文件被抹后按 `cp -rn` 回填、index 删除态没人翻"的残迹（与本轮已记档的抹文件事件同族）。
HEAD 侧三件俱全（`git cat-file -e HEAD:scripts/governance/decision_chain_sentinel.py` 通过），
本车道的 A/B 旧尺复述也正是从 HEAD 取来跑的。

后果（如不处理）：谁按现 index 直接落地，决策链哨兵三件 + 本车道治尺改动**在 git 里一起被删**，
盘上却还留着"看起来在"的文件——比假绿更坏的假存活。

落地批必做（本车道按任务书禁 git add/commit，一律未动他人条目、未清 index）：
1. 显式重新收录本车道两件的盘上版本（`git add scripts/governance/decision_chain_sentinel.py tests/governance/test_decision_chain_sentinel.py`
   由总筹在 GitCommitGateway 内执行，非本车道）；
2. 27 条 `D` 逐条定性（抹除回填残迹 vs 真退役），别和退役袋混一次提交——
   复核命令：`git diff --cached --name-status | awk '$1=="D"{print $2}'` 对 `git ls-tree -r --name-only HEAD` 差集 + 盘上存在性；
3. 哨兵三件同批（.py + ps1 + tests）：ps1 也在 D 列，只翻两件套会把计划任务真源留在删除态。

## ⑦ 复核命令（给下一班）

```
python -m pytest tests/governance/test_decision_chain_sentinel.py -q                     # 17 passed
python scripts/governance/decision_chain_sentinel.py --ref-date 2026-09-17 --alert-log .runtime/tmp/x.jsonl   # exit 4（新尺红）
python scripts/governance/decision_chain_sentinel.py --ref-date 2026-09-25 --alert-log .runtime/tmp/x.jsonl   # exit 0（休市不误鸣）
python .runtime/tmp/lane_day_old_sentinel_head.py --ref-date 2026-09-17 --alert-log .runtime/tmp/y.jsonl       # exit 0（旧尺哑火原样复现）
python .runtime/tmp/lane_day_probe2.py                # decision_daily 目标日分布 + 日历口径（只读）
```
生产告警文件 `.runtime/logs/decision_chain_alert.jsonl` 全程未被本车道写过（实跑一律 `--alert-log` 重定向 `.runtime/tmp/`，
实测该文件仍 ABSENT，与 L09 交案一致）。

## ⑧ 外部旁证（仅旁证，真源=本仓 `c1_market.trade_calendar`）

2026 年中秋节为 9 月 25 日（周五）、沪深交易所当日休市，与国庆假期构成 2026-09 下旬长休市窗；
检索于 2026-09-25 夜，来源为财经媒体/券商公告转载（非交易所官网直读，故只作旁证）：
- 新浪财经《明确了！休市12天》 https://finance.sina.cn/2026-09-20/detail-inisnnky6629816.d.html
- 东方财富《2026年中秋国庆假期，A股和港股的休市安排》 https://emcreative.eastmoney.com/app_fortune/article/index.html?artCode=20260923110357059987800
- 天府证券《关于 2026 年中秋节、国庆节休市及港股通交易安排的公告》 https://www.tfzq.com/2101914428457963521.html
- 财联社（亚太多地股市密集休市） https://www.cls.cn/detail/2488341
