---
ttl: task_bound
title: 数据车道班台账（T1-T6 滚动）
session: st-datalane-20261010
completes_when: 六件收官+99_delivery 落地（本件随批滚动）
---

# 数据车道班台账（sid=st-datalane-20261010，2026-10-10）

> 开班令=总统统筹 2026-10-10（Owner 已批）；六件 T1-T6；台账本件随批滚动追加。
> worktree=`.worktrees/st-datalane-20261010`（分支 ai/st-datalane-20261010/task-datalane-sixpack，基线 dev@0544db35bd→已 ff 至 7b81f39121）；心跳守护 PID 16312。

## 〇、冷启动与在岗证据

- RULE-ENV：Python 3.12.8（PATH 修正后）；`setup_dev_env.py --check` usercustomize 在岗。
- RULE-GUARDIAN：reaper source=live（11:34:52 实扫，ghosts=0）；工作区 watermark 11:34 实读 RAM avail 25.95GiB/degraded=False。
- 本班 keep 登记：`data/runtime/process_reaper_keep.txt` 追加 `emotion_index_snapshot`（T5 配套）。
- 铁律盘点：在飞回填三条腿实测（12:00 进程表）——夜跑 runner PID 34644（02:30 起）、全史 daily 回填 PID 53472（11:42 起，--start-daily 2021-01-01 全量）、selfheal 驱动 PID 26768（10-08 起）。**本班写库面全部让位至 53472 收官**（禁双开红线），期间只做轻探针与纸面件。

## 一、T1 退役指标停算（裁定#489①+#494② 执行）——已落地

- **commit=bebba60c**（本班分支，2 文件 +147：provider 过滤+红证测试）；收尾时随分支并 dev。
- 位置勘误（如实记）：处方原文"_compute_all_indicators 过滤"，实测夜跑批写链走 `build_rows_vectorized`（P1-1 切挂后），`_compute_all_indicators` 不在写链——过滤挂 `_fetch_single_period` 的 `list_all()` 消费点（向量/迭代两腿唯一源头，同收夜跑与手动回填）。
- 过滤面：仅 REG-IND-001 `status==active` 进写链（retired 6 件 #489① + deprecated 5 件 #494②=停用同口径；candidate/experimental 未晋升不入产线宽表）；join 键=输出列（册 outputs↔代码 meta.output_columns）；册读不到 fail-open+warning（宁多算不少写）；缓存按 mtime。
- 红证：A=摘消费点过滤调用⇒`test_fetch_path_wiring` 红（实测复现后原样还原）；B=HEAD 未修码⇒TestRegistryStatusFilter 4 例全红，修复后 21 passed 全绿（含 fail-open/划分完整性/kdj-macd 不受牵连阴性对照）。ruff check+format 净；PYTHONNOUSERSITE=1 且 `zephyr.__file__` 落车道内跑测（final4 假绿教训）。
- **主区对平（降级直改主区，登记原因=T1 验收窗=今晚 02:30 夜跑读主区码，final4 先例）**：已把 bebba60c 两 hunk 外科叠加到主区工作副本（B2/B4-M2 在途 hunks 逐字保留，纯插入锚点替换，AST 核过）；主区实测 21 passed。主区该文件现有未提交面=B2 hunks+本班 hunks，归属吸收按 489777c60e 在案口径。
- 行为变更声明：retired/deprecated 11 件（13 输出列）自下一夜跑起不再重算写库，新增行该 13 列=NULL（诚实缺位）。
- **T1 闭环面追加（commit 24fec802，同日第二笔）**：复盘发现 T1 单独落地存在交互缺陷——
  新算行退役列=NULL vs 存量旧值 ⇒ P1 值级比对逐行必不等 ⇒ 跳过永不生效 ⇒ 夜跑全史重灌
  不停（写入量验收尺落空）且 T2 写入会被下一夜 NULL 版本掩埋。治本=P1 比对面排除退役
  列集（与计算腿同册同读径），复算与存量在 199 active 列上逐位相等 ⇒ 整行跳过。红证=
  摘退出面⇒只差 wad 的行判"变"必写（红测在案）；30 passed 全绿。主区已对平（该两文件
  主区无在途 WIP，整文件对平），夜跑/自愈腿下一进程起读新码。
- 写入量验收修正声明：T1 停算本身不减 INSERT 量（行仍整行写入）；结构性下降由 T1 闭环面
  （P1 跳过恢复生效）兑现——且依赖比对基读可得（final4 熔断在案：读不到基的窗口仍全量写，
  宁多写不少写）。

## 二、T2 squeeze/wad 定点重算（为二号重考清口径）

关键盘面（改变处方的实测）：夜跑每晚全史重写 2021+（dexp §10 R4），公式修复 1a9ab332f58 落地后，**窗口内同键的最新 ingest_ts 版本可能已是新口径**——若证实，T2=验证+冷档+通知（收敛靠 T6 OPTIMIZE），无需二次重灌。D7 申请包见 `02_t2_squeeze_wad_d7_application.md`。探针/冷档/重算全排 53472 收官后的安静窗。

### 探针法证（12:3x-13:0x 实测，轻查询未撞红线）

1. 000001 窗内 3 日最新版（ingest_ts=10:21 local，属 02:30 夜跑腿）：**旧口径实锤**——
   四象限对表（全史 cumsum）：hfq+old=-1667.74/-1688.88/-1923.16 vs CH=-2416.24/-2437.38/-2671.66，
   差值恒 =-748.5（同增量不同累积基 ⇒ 源=hfq、公式=old、基=某截断窗，非任何 HEAD 象限）。
2. 公式修复 1a9ab332f58 落地时刻=10-10 05:11 local，**晚于 02:30 夜跑起跑** ⇒ 夜跑腿载旧码，
   与探针结论自洽。
3. 11:42 腿（PID 53472）理论载修复码（05:11 后起），但其产物与 base2021+new 仍不对表
   （600528/600519 双标的双象限皆不中）——多腿叠加+hfq 派生可能随时再刷新（M1 日更腿），
   存量出处**不可干净归属**。
4. **裁决：按开班令本义走稳健路线**——等在飞腿全部收官（TI 写入静默 ≥30min）后，本班
   自算定点重写（HEAD 修复码×hfq 源×申报基约定），冷档先行；**T1 停算生效后退役列不再被
   任何夜跑重写 ⇒ 本班写入即终态**（T1→T2 顺序的设计意图，与 commit bebba60c 声明一致）。
   基约定申报：wad=cumsum 自源表该 symbol 首 bar（mathematical principled；管线旧约定=--start-daily
   2021 截断基，属申报变更，D7 包 §一.3 声明）；squeeze_mom 无基敏感（20bar 窗口）。
5. **执行（15:0x-15:4x）**：冷档双证落 F 盘（2,643,381 键，sha256 双件入 manifest）→
   --apply 24 月全 OK（月写入≈7.6万-12.7万行，重算键 2,643,220，覆盖表 Memory 即用即 DROP，
   与冷档差 161 键=0.006% hfq 源缺键 LEFT JOIN 保原值）→ 4 键验收探针 2/4（600528/300750
   单版本精确对；000001 两键被在飞夜跑旧码腿重写掩埋=预判机制实证）→ 21:3x 腿静默窗终态
   刷新（脚本重试语义已修：插入与校验分离，防 241 触发同值重插）→ 明晨 02:30 起 T1 闭环
   码守值。技术注记：严格读通道强注 FINAL=241 杀手，全链已改 fexam.ch_data.ch_query_df
   （无 FINAL 正门只读，夜矿广度推导同款）+pandas 侧 max(ingest_ts) 去重。

## 三、T3 limit_up_down 断供回补——待回填收官

现读（开班令口径）：仅 2026-07-20 起 5,397 行；冻结窗需 2019-01-04 起 1,622 交易日。验收尺=nightmine `02_breadth_derivation_report.yaml` 7 条广度序列对齐。数据源与排程勘察中；执行排 53472 收官后（禁双开）。

## 四、T4 夜矿断供补——待回填收官+小批验门

断供面（OD-9）：kline_daily_hfq / technical_indicator / emotion_index 断在 2026-09-30（普通日线到 10-09）。表族级联口径：daily 指标源已切 kline_daily_hfq（B4-M2，主区在途），hfq 是根——补齐顺序=hfq→TI→（情绪指数归其 builder 链）。小批验门方案（日线改周线跟不跟）：按 WO-004 先例，周月线必须同批跟改（kline_weekly_hfq/kline_monthly_hfq 同源派生），方案细则排程后落 `03_t4_cascade_gate_plan.md`。执行前提=53472 收官单开。

## 五、T5 情绪快照器修复+日批连跑

- 正身核实：`scripts/data/emotion_index_snapshot.py` 在 HEAD 且健康（append-only 快照+manifest，tests/data/alt_data 有测）；10-08 后停更根因=无任何调度（非脚本病）。
- **day1 连跑=2026-10-10 12:10 已执行**：`emotion_index_20261010T041044Z.jsonl.gz`，8,660 行，sha256=8fbad68d…，max_trade_date=2026-10-09（manifest 追加行留痕）。
- keep 已登（process_reaper_keep.txt 追加 emotion_index_snapshot）。
- day2/day3 连跑+满 3 天钉任务=已建值守自动化（每日 12:35；判据=manifest ≥3 条连续日批后钉 `ZephyrAlpha_EmotionIndexSnapshot` 计划任务+回执写本台账）。钉任务规格：`schtasks /create /tn ZephyrAlpha_EmotionIndexSnapshot /sc daily /st 12:35 /tr "python D:\ZephyrAlpha\scripts\data\emotion_index_snapshot.py"`（工作目录 D:\ZephyrAlpha；跑前 PATH=Python312）。
- 对象勘误留痕（final4 §二·6）：`ZephyrAlpha_NightlySentiment`/`ZephyrAlpha_SectorSnapshot` 是新闻情绪/板块快照，与本件无关，勿混认。三册对齐（fms/capreg）归治理域，本班未碰。

## 六、T6 P5 触发器监测与执行（条件件）

三触发器：(a) CH 空闲窗窄窗读复测通过（215 列剪枝窄窗探针，排 53472 收官后安静窗跑）；(b) T1 停算落地（✅ 本班已落地，今晚 02:30 起结构性降写入）；(c) 比对基低内存通道（架构面，非本班可自决）。任一成立⇒按 Owner 已批窗排 CH OPTIMIZE（23:30 后、避夜跑；前后 df 对拍，预期回收 5.5~42 GiB，实收记账）。**P5 顺序铁律**：T2 冷档先行；今晚若 53472 拖过 23:00 则 OPTIMIZE 顺延（23:00 W1 窗 GPU/IO 让位二号）。

## 七、降级直改登记

- 主区直改 1 处：`src/zephyr/data/implementations/internal_compute_provider.py`（对平 T1，原因见 §一；GW 计数以实际标记为准）。

## 八、收尾清单（滚动）

- [ ] 53472 收官确认→T2 探针+冷档→T3/T4 放量
- [ ] T1 今晚 02:30 夜跑写入量对比（明晨读 state+当日入库行数）
- [ ] merge 本班分支回 dev；release 全部 claim；99_delivery 逐件哈希+复核命令
