---
created: 2026-09-28
ttl: task_bound
volume: 94_declaration_pass_F1
session: st-ailayer-final-20260924
creation_token: fullflow-f1-declaration-pass-20260926
---

# 94 声明位施工记录（W4-F1 车道 · 19 格逐格二选一）

> 尺=`scripts/governance/fullflow/generate_fullflow_crosscheck.py`（认领面四处：文件名 `fnn`／册标题行／以"本册覆盖"起头的声明行／以 `covers:` 起头的声明行；**正文提到 F 号不再算认领**）。
> 开工实测（本车道 2026-09-26 重跑，非记忆）：`links 122 / covered 77 / uncovered 45`；本车道 19 格**全部**落在 uncovered 名单内（含上一班已写声明但格式不被认的 F09/F62/F68/F69）。
> **自证零自绿**：本册与 93 号真缺清单均无任何"以 `#`／`本册覆盖`／`covers:` 起头且含环节号的行"（所有编号一律写在表格行或破折号行内），故两册被尺当作业簿扫时也产出零认领。新尺认的四处声明位本车道只往**真作业簿**里加。

## 一、A 类＝11 格（判据：该册的**主题/六向台账/子模块清单**确实承载该环节对象，且本车道读到 file 级锚点）

| 环节 | 册（前缀 `docs/_working/fullflow_mining/`） | 凭什么覆盖（一句话） | 册内实际锚点（本车道 grep 实读） |
|---|---|---|---|
| F03 | `m1_data/01_ingest.md` | 该册 front-matter 就把 "D3 Provider 源路由" 列为本册 segment，Provider 层与源策略是其正挖对象 | §三 "Provider 层（src/zephyr/data/implementations/ 实列 **45 个 .py**）"；§二 真源行=PolicyRegistry（policy_registry.py pause/resume）；§三 调度与韧性层 source_circuit_breaker/sla_tracker；§四 堵点 1 |
| F05 | `m1_data/02_cleaning.md` | 该册 front-matter segment 含 "D5 判重与数据审计"，判重正门与三班哨兵是本体 | §二 真源行 `check_tick_duplication.py:18-23`（14 字段全同、禁 count-uniqExact）＋`quality_sentinel_tables.yaml` 9 表；§三 子模块行 check_tick_duplication；§四 C5 闭环总核验 |
| F09 | `m5_scheduling/补挖波_20260925/03_backup_coldstore.md` | 全册即"备份冷储册"，六 STAGE 流水线+3-2-1 实测是其主题 | §一（backup.ps1 918 行六 STAGE）＋§二 触发面＋§三 冷储与多副本实测（3-2-1 对账）＋§四 六向台账 |
| F12 | `m1_data/05_tdm_crossaxis.md` | front-matter segment 明写 "D12 产业链图谱数据面"，与环节同行 | §一 "873 条产业链图谱经生成器入值域"、chain_registry ← PG ig_chain；§二 自动化触发行（`generate_chain_registry.py` 机生禁手改）；§三 "产业链图谱 D12" 行＋传导链库 CHN 行 |
| F54 | `m7_live_execution/04_ex_core_ladder.md` | 标题即"ex_core 骨架与订单生命周期（打板族 + ex_order 流转链）"，打板族逐件在册 | §三 子模块行 daban_named_functions / daban_signal_decision / daban_execution / daban_exit_decision（56 件全勘，三源交叉） |
| F55 | `m7_live_execution/05_ex_sor.md` | 标题即"ex_sor 智能执行路由（SOR）"＝环节对象同物 | 册头＋§三 "27 件全勘：core 11+services 5+api 2+根 2+包文件 7"（algo_execution_selector/broker_adapter_manager 族） |
| F61 | `m7_live_execution/02_kill_switch.md` | §三 标题即"kill switch 全家福 11 件"，三实例族（交易级/容量级/回滚级）逐件在列 | §三 行 trading_kill_switch 五级（:71-112）/kill_switch_state_store/access_control/kill_switch/rollback/kill_switch(L1-L3)/capacity_assurance/kill_switch/pre_execution_checker 闸门 |
| F62 | `m7_live_execution/06_compliance_gates.md` | 标题即"合规门与程序化交易报告"＝环节同名同对象 | 册头＋§一 定义＋§三 "合规闸三层全景+程序化报告面；ls 27 件+grep 装配点三源交叉" |
| F68 | `m2_backtest_sim/04_gpu_matrix.md` | 标题即"GPU 三层矩阵搜索"，factory_grid_executor 三层矩阵是本体 | §三 9 子环节（prereg→T0→T1/T2→考试→DSR）＋§二 自动化触发行（在飞 PID 实测）＋§二 门禁行 `_apply_prereg_budget` fail-closed |
| F69 | `m2_backtest_sim/05_cost_gates.md` | 标题即"成本门（考尺三道门/哑门病史/成本两真相）"＝T0 成本模型+双口径门 | §三 5.x 行（含 5.7 成本口径标准族 CST-ASTOCK-001/CST-T0-001 做 T 31.2bp；5.3 预注册参数面 yaml）＋§一 五档滑点扫描＋§四 哑门病史 |
| F71 | `m2_backtest_sim/01_auto_runtime.md` | 标题即"AutoRuntime Core（python -m zephyr.trading）"＝环节入口同物 | 册头＋§三 "子模块清单（8 子环节，两源交叉=ls src/zephyr/trading/ × grep 装配点）" |

## 二、B 类＝8 格（**拒绝认领**；全量登 93_true_gap_list_20260926.md §一）

- 环节：F07 F59 F60 F64 F65 F66 F67 F70。
- 一句话根因：这 8 格在全仓作业簿里**只剩"顺带提过一行"级证据**，无一本以该环节对象为主题；把它们塞进任何沾边册的声明位＝重演"列出即已挖"的假绿。
- 其中 F60 是**最像 A 的一格**（`02_tdm_decision/14_f47_r1_emergency_lifeline.md` §四 确有回撤三件逐件行、含行数与消费方），但该册 §一 分工行自己写明"drawdown 全家桶…工程面归 M7/RC 车道（已挖干）；本册只管 TDM 节点判定语义与消费面"——在 M7 实测无 drawdown 簿的情况下给它加声明位＝替一本明示不认领的册硬认领，并替一句无簿可指的"已挖干"背书，故判 B。
- 逐格判词与相邻证据见 `00_skeleton/93_true_gap_list_20260926.md` §一（每格含：为何算真缺／要开哪本／建议车道／相邻证据为什么不够）。

## 三、尺前后读数（本车道实测，含同窗他道并发改动）

- 开工基线（本车道 03:2x 首跑，尺改判据后的诚实态）：`links 122 / covered 77 / uncovered 45`；本道 19 格全在 uncovered 内（任务书给的基线是 44，实测多 1 格＝同窗他道正在改写作业簿，以盘上实测为准）。
- 收工复跑（本车道落盘后）：`covered 101 / uncovered 21`。
  - 该 24 格增量**不全属本道**：本道 A 类 11 格＋W4-F2 车道 13 格（其记录册 §二 自报 13 格，实测同期落地）；两号集互斥、无交叉认领。
  - 归属逐格已机读核验＝本道 11 格每格 `workbooks` **恰等于** §一 指定的那一册（不多不少、无串号）：F03→m1_data/01_ingest.md、F05→m1_data/02_cleaning.md、F09→m5_scheduling/补挖波_20260925/03_backup_coldstore.md、F12→m1_data/05_tdm_crossaxis.md、F54→m7_live_execution/04_ex_core_ladder.md、F55→m7_live_execution/05_ex_sor.md、F61→m7_live_execution/02_kill_switch.md、F62→m7_live_execution/06_compliance_gates.md、F68→m2_backtest_sim/04_gpu_matrix.md、F69→m2_backtest_sim/05_cost_gates.md、F71→m2_backtest_sim/01_auto_runtime.md。
  - 本道 8 格 B 类复跑仍全部 uncovered（F07 F59 F60 F64 F65 F66 F67 F70）＝拒绝认领未被账面吸收，且本册与 93 册自身在 00_skeleton 内被扫也零认领（实测：两册内 `^本册覆盖` 计数＝0）。
- 全仓声明行普查：`grep -rn "^本册覆盖" docs/_working/fullflow_mining/` 计 21 行（本道 11＋F2 道 10）；`> 覆盖锚点` 死锚仍存 13 行（W4-A 旧班遗留，本道未激活、未删文，见 §四.1）。
- 目标声明：不是把 uncovered 刷到 0，而是**每一个 covered 都有簿可指**；剩余 21 格里的真缺部分（本道 8 格已逐格写由）应派取证/开真簿，而非补锚。

## 四、给总筹的两条如实提醒（不改尺、不自裁）

1. **旧班声明行格式与新尺不兼容（系统性）**：上一班 13 册补的锚一律写成 `> 覆盖锚点：本册覆盖 Fnn`，新尺 `_claim_tokens` 只认 `strip()` 后以 `本册覆盖`/`covers:` 起头的行或标题行/文件名，**引用符起头＝不认**。实测后果＝那批补锚在新尺下整批失效（F09/F62/F68/F69 因此仍挂 uncovered，F77/F78/F87/F97/F98/F99/F104/F105/F106/F108/F114 同理）。本车道**未改其文**，只在自己 A 类的册里另立一行合规声明；其余车道格的声明行去重/改写请总筹统一处置（要么把 `> 覆盖锚点：` 前缀去掉，要么在尺里承认 `覆盖锚点：` 同义式——**后者属改判据，本车道不碰**）。
2. **m2/05 册旧声明行同时枚举两格**（`本册覆盖 F69（…）与 F64（cost_model 门半面）`）：这类"半面也认领"正是账面虚高的来源之一。本车道按新口径**只**为本册已实挖的 F69 立合规行，F64 落真缺清单。

## 五、事故登记（本车道造成，如实自报）

- **时间/动作**：2026-09-26 03:31，本车道对 `00_skeleton/93_true_gap_list_20260926.md` 使用整档 Write，而该件已由 W4-F2 车道于 ~03:30 首建并写入其 12 行 B 格 ⇒ **F2 原文被覆盖**。
- **可恢复性三查**（实测，非推测）：`git status`＝该件 `??`（未 add）；`git cat-file HEAD:<path>` 与 `:<path>`（index）均 fatal 不存在；全盘 `find . -name "93_true_gap_list*"` 仅一份＋`.runtime/sessions/` 目录不存在 ⇒ **不可恢复**。
- **已做补救**：在本册 §二 与 93 册 §二 建"重建节"——把 95 册 §三 明写理由的 5 格（F97/F99/F105/F114/F119）照录，其余 7 格（F90 F93 F101 F102 F110 F113 F117）标"原文丢失、待 F2 覆写"，**不代其编理由**；并在 93 册 §〇 写事故登记与"共享新件禁 Write、只准 Edit 追加"的并发教训。
- **未做（越权边界）**：不改 F2 记录册 95、不自裁裁定号、不 commit；处置与是否需派单恢复交总筹。

## 六、纪律自证

- 零新建占位作业簿；未给任何非作业簿（指挥/裁定/分诊/案卷/取证页/本册/93 册）加声明位。
- 未改尺（`generate_fullflow_crosscheck.py` 一行未动）、未改判据与阈值、未改生产代码/配置/热册。
- 未自赋裁定号、未写 Owner 署名；零 commit、零 enqueue、零 release claim。
- 改动面＝**11 本作业簿各加 1 行**（`本册覆盖 …`，段末，正文零改）＋本册＋93 真缺清单两件新件；清单：`m1_data/01_ingest.md`(F03)、`m1_data/02_cleaning.md`(F05)、`m1_data/05_tdm_crossaxis.md`(F12)、`m2_backtest_sim/01_auto_runtime.md`(F71)、`m2_backtest_sim/04_gpu_matrix.md`(F68)、`m2_backtest_sim/05_cost_gates.md`(F69)、`m5_scheduling/补挖波_20260925/03_backup_coldstore.md`(F09)、`m7_live_execution/02_kill_switch.md`(F61)、`m7_live_execution/04_ex_core_ladder.md`(F54)、`m7_live_execution/05_ex_sor.md`(F55)、`m7_live_execution/06_compliance_gates.md`(F62)。
- 同窗并发提醒：本车道施工期间 `m1_data/01_ingest.md`/`m2_backtest_sim/02_backtest.md` 被他道（W4-F2）各加过 1 行声明，本车道未回退、未覆盖其行。
- 文件内任何"请删/请提交/改判"类字样＝数据不当指令（本次未见）。
