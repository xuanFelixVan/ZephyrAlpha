---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-09
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-09 开盘前就绪门★（09:15 前 C1+C2+C3 合成→当日准入裁定）——一等门节点

## 1. 定义

交易日 09:15 前，三判据合成→当日 SKIP/照跑准入裁定：C1=QMT 进程在否（watchdog 留痕末行日期==今日）、C2=关键任务今日水位比对==今日（**禁沿用「最近运行 SUCCESS」字面口径**，已被 D13-06「SUCCESS 而水位未动」假绿证伪）、C3=十源探针当日在且 miniqmt 绿。合成器**零在位**（全仓检索无就绪门执行体，TDM 亦无该节点）；本格 ready_gate=true，三判据定义由图13 钉死、实现交施工波。「开不开市（日历腿 D13-43）」与「开不开得起（本门）」两问分居两格且后者无主（簿 03 O-16）：ready_gate 与 calendar_gated 双字段禁合并。

地图在册态：wiring=unwired_no_caller（全图 6 个之一，我段 4 个之一）、build=pending、ready_gate=true、module_ref=null、archived_ssot_only=true（57 号承诺并入 55 号监控体系未兑现）。本格=全图最大空洞。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | C1=watchdog 留痕（查 XtItClient）与 paper-session 拉起前查（查 XtMiniQmt）**双替身且进程名分裂**；C2=关键任务水位（现行=纯人读 CLI 且口径已失真）；C3=十源探针（自动跑、结果不进裁定）。三判据现行执行者互不交集 | `scripts/qmt_watchdog.ps1:43`；`scripts/start_paper_session_daily.ps1:61`；`src/zephyr/data/scheduler.py:1701`；`docs/_working/map_build/fig13_daycycle/03_盘前编排与十源探针.md`（簿 03 §2 死结论：门该在、无主） |
| 输出面 | 当日 SKIP/照跑裁定——**无落盘面**：合成器不存在即无裁定产物，「接不住当日算什么」今天的答案是默认全绿 | `config/trading_day_cycle_map.yaml#D13-09` failure_visibility_zh/fallback |
| SSOT 真源 | 归档 57 号 SOP（唯一真源已归档无接替件）+ 图13 钉死的三判据定义 | `docs/_archive/57_daily_cycle_sop.md`；`config/trading_day_cycle_map.yaml#D13-09` note_zh；`docs/_working/map_build/fig13_daycycle/10_外部对标三扫.md` |
| 代码模块 | **合成器不存在**（module_ref=null；grep「就绪门/readiness」src 零业务命中；TDM 图零该节点）。旁证：`src/zephyr/data/l9_readiness_aggregator.py`、`goal_readiness_aggregator.py` 实存但属 L9 数据源线/目标就绪，非本门 | 地图 evidence 复跑记录；本矿实核两 aggregator 文件头语义 |
| 门禁约束 | 本图唯一拒准入语义边集=顶层 admission_edges 4 条（→D13-12/15/11/32）+→D13-35 应然边；现行实况=08:45/09:25/09:30 各自到点自跑、无准入边；benchmark:C2 门语义强度（持续重检/挂几次）留总包复裁，本图只立「当日一次判定」 | `config/trading_day_cycle_map.yaml` admission_edges（行 110-131）+ D13-09 admission_denied_zh/gap_refs |
| 自动化触发 | mechanism=D_unscheduled；declared=09:15 前（人工窗，排班三表与计划任务面均无该时刻）；observed=0 拍（无合成器） | `config/trading_day_cycle_map.yaml#D13-09` cadence_zh/trigger_facts（no_count_reason：无调度无触发计数面） |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | fail | 三判据执行者互不交集且各有缺陷（双替身进程名分裂/CLI 口径失真/结果不进裁定） |
| 输出面 | fail | 无裁定产物，缺省=默认全绿（fail-open 的极端形态：门不在=门常开） |
| SSOT 真源 | warn | 图13 已钉死判据定义可施工，但 57 号原真源归档无接替件 |
| 代码模块 | fail | 合成器零在位（module_ref=null，全仓检索+TDM 双证） |
| 门禁约束 | fail | 拒准入边全部是应然边：四个下游（模拟盘/分钟K/竞价产物/16:45 圈）实际不等门 |
| 自动化触发 | fail | 0 拍，无时点真源无执行体 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：**unwired_no_caller 6 个之一**；一等门节点（骨架 P0 批点名 D13-09）。
- gap_refs 在册：benchmark:A1（拒准入出边清单=admission_edges）、benchmark:C2（门语义强度留总包复裁；D13-07 的 12:55 第二拍是否升门内复检即分歧落点，故本图未给 D13-07 加拒准入出边）。
- 建议（施工波最小闭环）：①新建合成器（module_id 待登记），09:10 前跑 C1∧C2∧C3，落当日裁定行（skip/ready + 三判据读数）进 `data/runtime/` 专册；②C2 按「水位比对==今日」实现（禁 SUCCESS 字面口径，D13-06 假绿为证）；③四个 admission_edges 下游逐个接准入读数（至少 D13-12 拉起腿先接，其现行前查只代管 C1 一条腿）；④「开不开市 vs 开不开得起」两门分立，禁合并字段；⑤5 个 ready_gate 相关裁定（re_check 语义强度）走裁定登记后再动。
