---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_15_recon_ledger.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-15 账务对账挖矿作业簿（B1 批次，2026-10-06）——全链最薄环节，本簿真挖

## §0 环节档案

- **覆盖坐标**：FIG13 D13-29 日终三账核对（15:40 `eod_reconciliation` 槽）+ D13-31 当日回测跑批（对账 L1 基准腿）｜FIG12 DSC-15 日终三账对账（S5_recon 段）+ DSC-20 任务级对账 + DSC-GAP-TERMINUS（域终点不可证）。
- **真源锚**：FIG13 `docs/_working/map_build/fig13_daycycle/06_盘后结算与三账.md`（D13-29 三证死结论，现役挖掘=st-fig13-bone-20261004，本簿只读收编）+ `08_盘后批次与当日回测.md` §2（D13-31 改判）；FIG12 `config/data_supply_chain_map.yaml`（机生，DSC-15/DSC-20/DSC-GAP-TERMINUS 行级）；本簿新增 2026-10-06 独立 grep 实查（§4 轮 2-4）。
- **职责一句话**：收盘后回答"回测与柜台今天还对得上吗"——L1 交易级/L2 持仓级/L3 PnL 三账核对，差异 append-only 落台账并触发 C 类告警；任务书定性"全链最薄环节"经本簿复核**成立且比预想更薄**：名义三件实现、实际零接线、唯一活着的对账是另一义（任务级档期对账 DSC-20）。
- **状态总判**：D13-29=🌑（环节今日不存在，fig13 三证+本簿复核维持）｜DSC-15=⬜ unwired_slot_hollow（图12 机生在册）｜D13-31=⬜ 角色在册被挂起｜**account_nav_daily=状态变更（已接线，本簿新证）**。

## §1 六向台账

| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 上（触发面——"谁调用"逐路证死） | ①APScheduler 槽：`schedule.yaml` eod_reconciliation `40 15 * * 0-4`——2026-10-06 实测该键**物理三写**（:255/:447/:540，三写内容一致，PyYAML 后写生效行为无差，疑合并残留）；②槽内任务：tasks.yaml `schedule: eod_reconciliation` **零挂载**（grep）；③特殊分支：`grep eod_reconciliation src/zephyr/data/scheduler.py` **零命中**=无 `_run_special_schedule` 分支→槽每日 firing"时段无任务"→APScheduler 记 success（fig13 簿06 15:40:03 现场捕获三行=假通道实抓）；④schtasks：`grep eod_reconciliation scripts/*.ps1` 零命中=无计划任务替身；⑤事件面：`pipeline_events.py`/`wire_data_scheduler.py` 零资金对账钩子；⑥**人工逃生口也不存在**：`grep "__main__\|argparse" src/zephyr/trading/recon_runner.py` 零命中=无 CLI 入口 | fig12 DSC-15 行级 slot_refs=[eod_reconciliation]，downstream_action=none | signal |
| 下（产物/消费面——三张表逐一判） | ①`reconciliation_differences` **双真源双空**：DuckDB governance.db（DDL=`reporting/reconciliation_schema.py:42`，唯一写者 `trading/recon_runner.py:117` INSERT）+ CH `c1_market.reconciliation_differences`（DDL=`schemas/.../market_reconciliation_differences.py`，挂 `scripts/ch/apply_market_tables_ddl.py:544`）——两库皆空在册（`src/zephyr/data/config/known_data_gaps.yaml:1587` reconciliation_differences_dual_empty_disease，2026-09-30 CH 复核 0 行；fig13 簿06 09-24 governance.db 0 行）；消费方仅 `frontend/dashboard/api_server.py:1587` 标签"对账差异"→**恒空表前端恒真**；`src/zephyr/data/dual_source_guard.py:28-30` 在册防"双空被误读"；②`c1_market.execution_report`：生产端 `ExecutionReportProducer` 已接 QMT 文件桥（`ex_core/adapters/qmt_file_bridge_integration.py:40,133,191-198` attach，断点 E4，"未接线=零行为变更"）——表侧 09-24 读数全表 1 行（fig13 簿06），**2026-10-06 当前行数=实查待施工批**（本簿 DB 不直查）；③`c1_market.account_nav_daily` **状态变更（本簿最重要新发现）**：known_data_gaps.yaml:1446 `account_nav_daily_writer_zero_caller`（09-29 复测 0 行）→已由 **st-c9-emptyfill 2026-09-29 接线**：`scripts/run_post_settlement.py:435-445` 净值腿（GAP-F-29，延迟 import `zephyr/position/live_nav_recorder.py`，ch_writer 正门 TSV，基准缺失 NULL 降级）挂在 15:30 PostSettlement 计划任务内=机制 B 真触发；消费方三处在等：`infrastructure/system_telemetry/alerts/ops_alert_feed.py:39,192-228`（存活度分析 SurvivalInput）/api_server.py:1575/SPM FAC-E8/E9（DSC generator:1575）；**接线后是否日日真产行=实查待施工批** | reconcile_execution_log 87,999 行=门禁/自愈环留痕（列语义全 gate_id/commit_message，写者 `governance/audit/reconcile_runner.py:232`），与资金三账零关系——查"governance.db 有无对账留痕"得强阳性即中假绿（fig13 簿06 §5 专段） | signal |
| 内（实现面——三件同名"三账"逐一验活） | **三件实现零接线（2026-10-06 grep 复核维持 fig13 结论）**：①MOD-TRADING-007 `trading/recon_runner.py:392 run_daily_reconciliation`（L1+L2+L3，C 类告警清单必出 `:9` INVARIANTS）——生产调用方=0（命中仅 schedule.yaml 注释×3/自身/d5 generator/DSC map），且无 CLI；②MOD-TRADING-013 `trading/three_way_reconciliation.py:175 ThreeWayReconEngine`——**自标 [MATURITY] production 而全仓唯一引用=`ex_core/eod_reconciliation.py:21` 一句注释**；`tests/trade/trading/test_tdm_false_auto_census.py:21` 另证 TDM-E-L4-13 的 auto 无生产执行者背书；③MOD-L06-003 `ex_core/eod_reconciliation.py`（账户级：持仓+资金+未成交单转 EXPIRED）——调用方=0（仅 `qmt_file_bridge_broker.py:388` 注释+`tests/trade/ex_core/test_eod_reconciliation.py`）；④事件入口腿 `position/position_reconciler.py:123 handle_execution_report`——BRK-016 在册断点，零生产触发者；`orchestrator/execution/reconciliation_loop.py` 经 BRK-017 显式澄清**不是**成交-持仓对账链（只调和编排器 5 不变量）——误接=假闭环 | 内收判据 w5_1（宪法 §4.2）：同域重复簇→收敛唯一｜零触发零消费→退役——三件实现是现成候选案例 | signal |
| 旁（同名不同物与配对腿） | ①**FIG12 DSC-20 任务级对账=唯一活腿**（wired_special_branch，`src/zephyr/data/integrity_checker.py` 第 4 类检核：应跑/成功/漏跑/失败四计数案卷）——"调度档期对账"活、"资金三账"死，"对账"一词两义必须分格，否则 DSC-20 绿会被读成 ENV-15 绿；②FIG12 DSC-GAP-TERMINUS 在册自证："对账 PASS 语义的唯一实现 DSC-15 未接线，故（数据）达标面今天由本缺口承担，不许冒充"；③FIG13 D13-31 基准腿：簿08 §2 改判"角色在册被挂起"——CAND-BT-003（`docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml:7799-7820`）自陈"向量化不对账、56 号文 §2 已定分工"，阻塞问题「向量化产出是否会被用做对账基准」登记 34 天未裁决；④盘中 Timer 腿（D13-27，300s 真跑）**无持久化**（阶段2"对账历史持久化"未实现）→日终侧拿不到盘中差异积累，两腿各缺一半 | battle_map BM-REC-* 承载装配落点（让渡 3），本簿不重复建装配账 | signal |
| 史 | #234 已建表先于接线且接线至今未到（`recon_runner.py:59` 在册引用）；57 号文 §5 时代三账=人工步骤，GAP 族核销批把它改成"槽位"而未改"调用"=名实分离起点；`run_daily_reconciliation` 模块头仍自陈"本模块不挂调度"（`:22`）与 schedule.yaml 注释"唯一入口=本函数"（三处）方向相反——文档与代码互相指认、双方都未被运行时兑现 | — | signal |
| 新 | **本簿 2026-10-06 新增三条**：①schedule.yaml 8 槽键物理三写（含本槽，598 行/34 unique 槽——fig13 骨架 09-24 口径 29 槽已漂移），结构性脏登记交总包（热文件 CAS 纪律，本簿不修）；②account_nav_daily 已接线（状态变更，见"下"向③）——**ENV-15 四张账表从"三死"变"一活三死"**；③recon_runner 无 CLI 入口=连"人工先跑起来"的最低成本验证路都不存在——三件实现不仅未自动接线，也未被人肉验证过 | 无 | signal |

## §2 挖干自评

- **三扫收敛**：①生产者路（代码/配置/注册面三面 grep）✅；②形态路（三件实现逐一验活+四张表逐一判）✅；③消费者路（api_server/ops_alert_feed/SPM/DSC-20 下游三族）✅——三扫齐，增量归零。
- **长尾（如实登记的受阻项）**：`reconciliation_differences`/`execution_report`/`account_nav_daily` 三表**当前行数=实查待施工批**（本簿 DB 不直查约束）；fig13 簿06 的 09-24 读数（双空/1 行）为最近在册证据，接线判定不依赖行数新鲜度（写侧接线面已由代码证死/证活）。
- **🌑 清点**：柜台侧真实结算单（模拟盘 account=8886156677 无经纪商真结算文件，QMT 离线降级不伪造比对）与交易所日终完成时刻外部真源——两项骨架 🌑-3/🌑-4 在册，属"三账 L1 券商腿的物理上限"，不因接线而消。

## §3 挖后自审闸三态裁定

**挂起排期**（全链五格中最接近"可施工"的一格，但仍卡 Owner 裁定，非卡证据）。
- 理由：①证据面已三扫收敛：链空转的落点逐格钉死（见下"缺口落点"），不存在"挖清楚才能施工"的前置；②施工方案面有三个 Owner 级决策未裁：**(a) 接线归属**——15:40 槽挂 recon_runner（补特殊分支+CLI），还是并入 15:30 PostSettlement 管线作第 5 棒（净值腿先例：st-c9-emptyfill 走的正是后者，且 15:30 件已有 schtasks 真触发与补火语义）；**(b) 三件实现收敛**——MOD-TRADING-007/013/L06-003 按 w5_1 收敛为一件（建议收敛至 recon_runner，其余两件退役或降 demo 态），三件并存是"假绿温床"（production 自标零引用）；**(c) L1 基准腿供给**——CAND-BT-003 阻塞问题（向量化产出可否作对账基准）34 天未裁，不裁则 L1 永远单边；③**任何单件先施工=替未裁问题投票**（D13-31 同款教训）。
- **缺口落点清单（施工批验收锚）**：未产表=`reconciliation_differences` 双库 0 行（唯一写者未接线）｜有码未接线=MOD-TRADING-007/013/L06-003+`handle_execution_report`（BRK-016）｜任务缺调度=eod_reconciliation 槽零任务零分支+无 schtasks 替身+无事件钩子+无 CLI｜基准腿=D13-31 无槽且角色挂起｜**最小验收判据：`reconciliation_differences` 出现非零行，或 eod_reconciliation 假通道槽消失（删槽/改 description 如实标未接线），二者取一——禁"恒空表+每日假 success"共存态延续**。
- 解锁条件：fig13 封矿 ∧ Owner 对 (a)(b)(c) 三项同批裁定 ∧ fig12 施工令下达（DSC-15 行级转 built 须同源证据）。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 产出 |
|---|---|---|---|
| 1 | fig13 簿06 §5（D13-29 三证）+簿08 §2（D13-31 改判）+图12 DSC-15/20/GAP-TERMINUS 机生行收编 | 挂接完成；DSC-20 与资金三账分格判定 | §0/§1 旁 |
| 2 | grep `run_daily_reconciliation`/`ThreeWayReconEngine`/`ex_core.eod_reconciliation` 全调用面（src+scripts+config+tests） | signal：三件实现 2026-10-06 仍零生产调用方；recon_runner 无 `__main__`/argparse | §1 上/内 |
| 3 | grep `reconciliation_differences`/`account_nav_daily`/`execution_report` 全写读面 + known_data_gaps 对账族条目 | signal：双空病在册（:1587）；**account_nav_daily 已由 st-c9-emptyfill 09-29 接线进 15:30 管线**（:1446→run_post_settlement.py:435-445）；execution_report 生产端接桥可选 attach | §1 下/新 |
| 4 | 触发面逐路证死：schedule.yaml 结构（键三写实测）/tasks.yaml 挂载/scheduler.py 分支/ps1/事件钩子/CLI | signal：六路全零=环节事实不存在；schedule.yaml 34 unique 槽 8 键三写（结构性脏，交总包） | §1 上/新 |
| 5 | 三态裁定自审（含缺口落点清单与最小验收判据） | 挂起排期成立，三项 Owner 裁定点显式化 | §3 |

### 附：本簿实查命令（可复跑；2026-10-06 已跑）

```bash
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
grep -rn "run_daily_reconciliation" --include=*.py --include=*.yaml src scripts config   # 仅注释/自身/generator/map
grep -rn "ThreeWayReconEngine" --include=*.py src scripts tests | grep -v "three_way_reconciliation.py:"
grep -rn "from zephyr.ex_core.eod_reconciliation" --include=*.py src scripts tests
grep -n "eod_reconciliation" src/zephyr/data/scheduler.py; grep -n "schedule: *eod_reconciliation" src/zephyr/data/config/tasks.yaml   # 双零=假通道
grep -E "^  [a-z_0-9]+:" src/zephyr/data/config/schedule.yaml | sed 's/:.*//' | sort | uniq -c | sort -rn | head   # 8 键三写实证
grep -n "account_nav_daily" src/zephyr/data/config/known_data_gaps.yaml scripts/run_post_settlement.py   # :1446 旧缺口 vs :435-445 接线
sed -n '2478,2500p' scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py   # DSC-15 行级真源
# 行数复核（施工批执行，本簿未跑——DB 不直查）：
python -c "from zephyr.infrastructure.database_service import get_db_service as g;c=g().get_clickhouse_conn();print(c.execute('SELECT count(),max(trade_date) FROM c1_market.account_nav_daily')[0],c.execute('SELECT count(),max(trade_date) FROM c1_market.execution_report')[0])"
```
