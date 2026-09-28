---
ttl: task_bound
volume: wiring_C_cleaning
session: st-ailayer-final-20260924
creation_token: w3c-cleaning-three-engine-wiring-20260926
---

# wiring_C_cleaning — R-M1-06 清洗三引擎接线施工记录（车道 W3-C，2026-09-26）

> 裁法出处=`90_chief_rulings_wave1.md` R-M1-06（"先接线（DSL 载体 YAML + 一处调用点）再谈其余"）
> ＋`91_chief_command_wave1.md` §三.3 接线类（无门位）＋`94_chief_rulings_wave2.md` §三 AI-4#7 R-3
> （YAML 自称真源而代码硬编码=P0 施工项，必配"改 YAML 能改变行为"红测）。
> 取证真源=`m1_data/02_cleaning.md` C1 / `m1_data/补挖波_20260925/08_f04_cleaning_zero_wiring.md` C1'-C1''
> / `m1_data/90_backfill_wave.md` §三 3.1＋B1/B1'。

## 一、现状接线面（开工前实测，非记忆）

**"三引擎"指代**（02 册 §三 点名，08 册增补第四件）：
`cleaning_rule_engine`（DSL 引擎）/ `cleaning_anomaly_engine` / `data_anomaly_alerter`（+第四件
`expectation_governance`）。

零调用的机械证据（本车道 2026-09-26 复跑，排除 tests/__pycache__）：

| 件 | 定义点 | 全仓命中（=接线面） |
|---|---|---|
| cleaning_rule_engine | `src/zephyr/data/cleaning_rule_engine.py:274 class CleaningRuleEngine`、`:376 def run_quality_gate` | 仅 `src/zephyr/data/__init__.py:33` `:74` re-export → **生产调用零** |
| cleaning_anomaly_engine | `src/zephyr/data_eng/cleaning_anomaly_engine.py:123`、`:154 detect` | 仅 `src/zephyr/data_eng/__init__.py:7` re-export ＋ `incremental_update_engine.py:25` 注释文字 |
| data_anomaly_alerter | `src/zephyr/data_eng/data_anomaly_alerter.py:300`、`:154 detect_price_jumps` | 仅 `src/zephyr/data_eng/__init__.py:8` `:50` re-export |

承载面缺口（复跑）：`ls config/ | grep -iE "clean|rule|sentinel"` = alert_rules / cleaning_policy /
context_rules / iteration_guide_rules / quality_sentinel_tables 五件，**无 cleaning_rules.yaml**；
`grep -rn "cleaning_rules" src config scripts tests` 开工前=**零命中**（既无插头也无插座）。

现行写前质量面（不是三引擎）：`src/zephyr/data/ch_writer.py:1006` 只挂 `apply_quality_gate`
四门禁（ohlc/change/swing/adj），flagged 仅 WARN 不阻断（`:1008-1021`）。

头注虚标（B1'/C1''）：`cleaning_rule_engine.py:5` 标 `[CONSUMERS] zephyr.data.ch_writer`、
`:7` 标 `[MATURITY] production`，与 grep 事实相反 → 本批随接线回写为真（改后 CONSUMERS=
`cleaning_rules_hosting`，MATURITY=trial，并明文"ch_writer 写路径仍未接"）。

## 二、接线面（唯一调用点）

- **调用点**：`src/zephyr/data/supply_sentinel.py:540`
  `summary["cleaning_gate"] = _run_hosted_cleaning_gate(alerter)`
  （位于 `run_supply_sentinel` 内、紧随既有 `summary["quality_sweep"]` 之后；
  宿主实现=`src/zephyr/data/supply_sentinel.py:564-586 _run_hosted_cleaning_gate`）。
- **走既有管线入口**：L13 `data_supply_sentinel` 排班槽位（06:50 日批，`src/zephyr/data/config/schedule.yaml`）
  的**托管第二段**，与 quality_sentinel 的 `run_hosted_sweep` 完全同族
  （先例=`config/quality_sentinel_tables.yaml` wiring 块 `host_schedule: data_supply_sentinel`）。
  **未新建平行管线、未新开排班槽位、未加 cron/Timer**（R-021 空槽位=静默假通道；宪法 §9.3）。
- **新模块**：`src/zephyr/data/cleaning_rules_hosting.py`（承载册加载/校验 → DSL 引擎 → CH 只读取行
  → `run_quality_gate` → 报告 JSON + Alerter 出声）。四要素：触发=宿主槽位；运行=`run_hosted_cleaning_gate`；
  维护=`wiring.cadence_days` 节奏闸（报告文件名即状态真源，不另立 state）；关闭=`wiring.disabled_flag` 标记文件实查。
- **承载册**：`config/cleaning_rules.yaml`（DSL 判据唯一真源：op/阈值/上下限/分位/护栏/回看窗/
  read_limit_rows/alert_level 全在册）。代码侧**无任何判据值**：列面由规则字段派生、窗口与上限
  与级别均读 wiring，`lookback_days/read_limit_rows/cadence_days/alert_level/enabled/host_schedule/
  report_dir/disabled_flag` 全为必填（缺键=配置错，不猜默认值）。

读侧 flag 档承诺（出厂态，默认不改变既有产出）：本腿只 `SELECT`（`role=reader`，经
`DatabaseService`，宪法 §9.1），不写库、不改 `ch_writer` 写路径、不剔除生产行；规则
`action=block` 在本腿只计入 `stats.intercepted` 并出声（测试 `test_leg_only_reads` +
`test_red_changing_yaml_action_changes_behavior` 钉住）。

## 三、红测三件（`tests/zephyr/data/test_cleaning_rules_hosting.py`，28 例全绿）

| 判据 | 结论 |
|---|---|
| ①改 YAML 能改变行为 | **绿**。`test_red_changing_yaml_threshold_changes_behavior`：同数据同执行器，只把 `upper: 20→5`，findings 由 0→1 且 `by_rule={"pct_in_band":1}`；`test_red_changing_yaml_action_changes_behavior` 只改 `action: flag→block`，(flagged,intercepted) 由 (1,0)→(0,1)；`test_findings_alert_at_yaml_level` 改 `alert_level` 出声级别随变。代码零改动 ⇒ 判据真源确在 YAML（非装饰性护栏）。 |
| ②谁调它 | **绿**。`test_wired_into_supply_sentinel_leg`：monkeypatch 后跑 `run_supply_sentinel`，断言清洗腿被实调且 `summary["cleaning_gate"]` 存在（不接=测试红）；`test_host_leg_delegates_to_real_gate` 断言托管函数把 `host_schedule="data_supply_sentinel"` 交给承载册；`test_host_mismatch_is_config_error` 令册里声明宿主≠实调宿主 ⇒ fail-closed（防"册里挂个没跑它的宿主"）。 |
| ③YAML 缺失/解析失败 fail-closed | **绿**。`test_red_missing_yaml_fail_closed`（缺册：抛错＋托管腿 `ok=False`＋ERROR 出声，**绝不回 ok=True**）、`test_red_unparseable_yaml_fail_closed`、`test_non_mapping_carrier_fail_closed`、参数化 13 案畸形册（未知键／缺必填／cadence 0／read_limit -1／lookback 0／非法 alert_level／tables 空／rules 空／非法 op／表名 SQL 片段／列名 `1=1`／schema_version 漂移）＋`test_bool_poisoning_rejected`（true→1 静默放宽必炸）。另 `test_all_degraded_never_reports_clean` 钉"全表降级≠干净"。 |

出厂真册自检：`test_shipped_carrier_loads_and_runs` 用**真** `config/cleaning_rules.yaml` 跑真代码（防 fixture 绿而出厂册坏）。

## 四、生产只读实测（2026-09-26 03:02，非模拟）

`python -m zephyr.data.cleaning_rules_hosting --no-alert --report-dir .runtime/tmp/cleaning_gate_smoke --force`
→ CH reader 连接建立（slot=cleaning_rules_hosting），`c1_market.daily_valuation` 近 10 日窗 2,000 行样本：
`flagged=5 intercepted=0 by_rule={'close_positive': 5, 'amount_positive': 5}`（零价/零额行，与 09-18
实测"D 型错数进闭环"同型长尾；正身 5,550 行/日 ⇒ 0.25% 量级，非噪音）。

**起样回撤一条**（如实记）：`volume_rolling_upper`（滚动分位 q99/window30/手写 seed）首跑命中
1,722/2,000 行=结构性永久红 ⇒ 按 BRK-046 教训（告警疲劳必被拔线）从出厂册撤下，保留为册内
注释形态＋实测注；护栏与 seed 待有正确基线再起（代码无需改动，`parse_rules` 已校验该 op）。

## 五、文件清单（本车道全部产物）

新增：
- `config/cleaning_rules.yaml`（DSL 判据承载真源）
- `src/zephyr/data/cleaning_rules_hosting.py`（托管腿＋承载册校验/加载/报告/出声）
- `tests/zephyr/data/test_cleaning_rules_hosting.py`（28 例，红测三件）
- `docs/_working/fullflow_mining/m1_data/wiring_C_cleaning.md`（本册）

修改（3 处，全部最小侵入）：
- `src/zephyr/data/supply_sentinel.py`：`:540` 一处调用点 + `:564-586` 托管函数 + 头注
  `[CONSUMERS]`/`[ERROR_CONTRACT]`/`[TESTS]` 行补记（无其它逻辑改动）
- `src/zephyr/data/cleaning_rule_engine.py`：仅头注 `:5 [CONSUMERS]` / `:7 [MATURITY]` 回写为真（零逻辑改动）

未动：`config/flags.yaml`、`ch_writer.py`、`src/zephyr/data_eng/**`、`ex_core`、`pf_alloc`、
`comparator`、`shared/vocab`、catalogs 热册、restore_drill/services_registry。
生产库零写入/零 DDL/零 DELETE；测试输出全 `tmp_path`。

## 六、待登项（交总筹，本车道不自裁）

1. **creation_token 登记**（4 新件）：`w3c-cleaning-three-engine-wiring-20260926`（本册头注即用此值）。
2. **翻译册/能力册登记**：`zephyr.data.cleaning_rules_hosting` 大白话简介（`add_module_translation.py`，
   TRANSLATION-COVERAGE gate 会拦）＋ capability 册条目；`config/cleaning_rules.yaml` 消费方指向。
3. **depgraph 设计节点**（RULE-DEPGRAPH，本车道未改 PG）：新产物 `config/cleaning_rules.yaml`
   → `src/zephyr/data/cleaning_rules_hosting.py` → 宿主 `src/zephyr/data/supply_sentinel.py`。
4. **三数互斥（B2）/影子表退役（B3）**：不在本车道，未动。
5. **Owner 门位两项（只登记不执行）**：
   ①把 `action=block` 接到写路径（`ch_writer.py:1006` 现挂四门禁的写前段）=改 8.95B 行热路径
   ＋默认值翻转＝production 流转；②`volume_rolling_upper` 起样所需的量能基线口径（谁定阈值）。
   夜间均不自裁；本批出厂态=读侧 warn，既有产出零变化。
6. **待登的既有案卷更新建议**（本车道无权改 catalogs/他册）：`m1_data/02_cleaning.md` C1、
   `90_backfill_wave.md` B1/B1'、`m8_bottlenecks/01_open_wounds.md` A17 三处"零调用"陈述
   已被本批部分推翻（cleaning_rule_engine 现在有宿主；另两件仍零调用）。

## 七、三态结论

**完工**（限 R-M1-06 裁定的第一刀）：DSL 载体 YAML 已立且有唯一真源地位（改册即改行为，红测为证）；
一处调用点接成（走既有 L13 排班腿托管，非平行管线）；读侧 flag 档出厂；fail-closed 全链；
既有测试（`test_supply_sentinel` / `test_cleaning_rule_engine` / `test_quality_sentinel`）与生产只读
实测同绿，零既有断言被修改（本批只加文件，未改任何既有测试）。

**未完＝如实报红**：`cleaning_anomaly_engine` / `data_anomaly_alerter`（及第四件 `expectation_governance`）
**仍零调用**——本批按裁法"再谈其余"未接；它们的判据册（期望套件 YAML）与宿主选择需要单独一批
（anomaly engine 需按 symbol 取 OHLCV 帧，读侧代价与窗口口径未定，夜里硬接=给亿行表加未定尺）。

## 八、复核命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"     # 3.12.8
cd D:/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
# 1. 接线面唯一调用点（应见 supply_sentinel.py 一处 summary["cleaning_gate"] + 托管函数）
grep -n "cleaning_gate\|_run_hosted_cleaning_gate" src/zephyr/data/supply_sentinel.py
# 2. 承载册被码读（应 rc=0，且除 hosting 与测试外无第二个消费者）
grep -rn "cleaning_rules.yaml" src scripts tests --include="*.py" | grep -v __pycache__
# 3. 判据值不在代码里（应仅 _EXIT_* 运维码与标识符正则命中，无阈值/分位/窗口数值）
grep -nE "quantile|guard_|lookback_days *[=:] *[0-9]|read_limit_rows *[=:] *[0-9]" src/zephyr/data/cleaning_rules_hosting.py
# 4. 红测三件
PYTHONPATH=src python -m pytest tests/zephyr/data/test_cleaning_rules_hosting.py \
  -p no:cacheprovider -c py.ini -q --timeout=300
# 5. 既有回归（宿主与引擎原班测试）
PYTHONPATH=src python -m pytest tests/zephyr/data/test_supply_sentinel.py \
  tests/zephyr/data/test_cleaning_rule_engine.py tests/zephyr/data/test_quality_sentinel.py \
  -p no:cacheprovider -c py.ini -q --timeout=300
# 6. 生产只读实测（不写库不发告警；报告落 .runtime/tmp）
PYTHONPATH=src python -m zephyr.data.cleaning_rules_hosting --no-alert \
  --report-dir .runtime/tmp/cleaning_gate_smoke --force
```
