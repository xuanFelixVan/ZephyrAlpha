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
6. **终态刷新+终验（15:45-16:15）**：夜跑 runner 52 片全退后 --apply 重放 24 月全 OK
   （月写入与首写一致=同键集合同行数自证）→ **终验探针 5/5 全对**（000001 两键/600528/
   300750/002415，最新版=本地 HEAD 修复码重算值逐位≤1e-6）→ T2 交付完成。
   T3 dry-run 两次 500（bcure 链压 CH，argMax 推导 JOIN 需安静窗）；T6 触发器(a)探针
   结果见 §六。

## 三、T3 limit_up_down 断供回补——待回填收官

现读（开班令口径）：仅 2026-07-20 起 5,397 行；冻结窗需 2019-01-04 起 1,622 交易日。验收尺=nightmine `02_breadth_derivation_report.yaml` 7 条广度序列对齐。数据源与排程勘察中；执行排 53472 收官后（禁双开）。

## 四、T4 夜矿断供补——待回填收官+小批验门

断供面（OD-9）：kline_daily_hfq / technical_indicator / emotion_index 断在 2026-09-30（普通日线到 10-09）。表族级联口径：daily 指标源已切 kline_daily_hfq（B4-M2，主区在途），hfq 是根——补齐顺序=hfq→TI→（情绪指数归其 builder 链）。小批验门方案（日线改周线跟不跟）：按 WO-004 先例，周月线必须同批跟改（kline_weekly_hfq/kline_monthly_hfq 同源派生），方案细则排程后落 `03_t4_cascade_gate_plan.md`。执行前提=53472 收官单开。

## 五、T5 情绪快照器修复+日批连跑

- 正身核实：`scripts/data/emotion_index_snapshot.py` 在 HEAD 且健康（append-only 快照+manifest，tests/data/alt_data 有测）；10-08 后停更根因=无任何调度（非脚本病）。
- **day1 连跑=2026-10-10 12:10 已执行**：`emotion_index_20261010T041044Z.jsonl.gz`，8,660 行，sha256=8fbad68d…，max_trade_date=2026-10-09（manifest 追加行留痕）。
- keep 已登（process_reaper_keep.txt 追加 emotion_index_snapshot）。
- day2/day3 连跑+满 3 天钉任务=已建值守自动化（每日 12:35；判据=manifest ≥3 条连续日批后钉 `ZephyrAlpha_EmotionIndexSnapshot` 计划任务+回执写本台账）。钉任务规格：`schtasks /create /tn ZephyrAlpha_EmotionIndexSnapshot /sc daily /st 12:35 /tr "python D:\ZephyrAlpha\scripts\data\emotion_index_snapshot.py"`（工作目录 D:\ZephyrAlpha；跑前 PATH=Python312）。
- **钉任务回执（2026-10-11 16:39，Owner 加速授权）**：`ZephyrAlpha_EmotionIndexSnapshot` 已钉（每日 12:35，cmd cd 工作目录+全量 python 路径），schtasks /run 实弹验证通过——manifest 新增 20261011T163918Z（8,662 行，sha256 前 8=9d3bd453，close_final 8619 含 WO-004 链修复的 10-08/09 行）。"连跑 2-3 天"观察期经 Owner 对话加速授权豁免（脚本 4 轮实弹零失败+两份历史产物在案为据）。值守 ZCode 自动化同批退役（Windows 任务接管）。
- 对象勘误留痕（final4 §二·6）：`ZephyrAlpha_NightlySentiment`/`ZephyrAlpha_SectorSnapshot` 是新闻情绪/板块快照，与本件无关，勿混认。三册对齐（fms/capreg）归治理域，本班未碰。

## 六、T6 P5 触发器监测与执行（条件件）

三触发器：(a) CH 空闲窗窄窗读复测通过（215 列剪枝窄窗探针，排 53472 收官后安静窗跑）；(b) T1 停算落地（✅ 本班已落地，今晚 02:30 起结构性降写入）；(c) 比对基低内存通道（架构面，非本班可自决）。任一成立⇒按 Owner 已批窗排 CH OPTIMIZE（23:30 后、避夜跑；前后 df 对拍，预期回收 5.5~42 GiB，实收记账）。**P5 顺序铁律**：T2 冷档先行；今晚若 53472 拖过 23:00 则 OPTIMIZE 顺延（23:00 W1 窗 GPU/IO 让位二号）。

## 七、本班事故与治本留痕（防后人）

- **误判死接管（14:34，st-fwin-exec 同款第三次复刻）**：心跳守护 ~12:30 idle 自退
  （last_activity 未刷新），接管扫描以「exited 残留+死子进程 PID」判死本班并登记 open
  接管条目（held 3 件+worktree dirty4），TAKEOVER-PENDING 闸挡提交。自救=alive-owner
  自证：SessionRegistry 重登记+heartbeat 刷新+守护重拉（PID 33624，_spawn_heartbeat_daemon
  的 exited 残留守卫已按 1d5c0d36c4 增补令走无条件重 spawn）+接管条目 --resolve 自关。
  教训：①长睡眠窗会话必须周期性 register/heartbeat（本班已起 15min keepalive 循环）；
  ②「心跳审计末条 exited」= 前代守护自退证明，重拉前须清 pid 文件（增补令③①已治本）。
- **CREATE-GUARD 冤拦与 token 先行袋**：入队预检=落地仿真态读 **HEAD 版注册册**
  （M2.1 st-qcure-20260925），磁盘/PG 已登记未入 HEAD 的 token 一律判无 → 内容件必被拦
  （99_delivery 三连拦实证）。处方=final4 先例 efb5a72214「token 先行袋」：HEAD 册+仅本班
  4 块（+17 行零删除；worktree 渲染盘面曾带他会话待落地 token 11 块已外科剔除）→ f3cb27d8
  先行 → 内容件 d0010388 随即过检。

## 八、降级直改登记

- 主区直改 1 处：`src/zephyr/data/implementations/internal_compute_provider.py`（对平 T1，原因见 §一；GW 计数以实际标记为准）。

## 十、T7 bcure 链收官（追加令执行记录，2026-10-10 16:1x）

- **属主三态判定**：`st-bcure-20261008` 不在 SessionRegistry 活跃清单（会话目录在=已死）
  ⇒ 按处方走"死则停进程+state 归档"。
- **停点安全证据**：驱动 26768 当时处于内存闸等待（log 实录"[mem] 3.58GiB >= 2.5GiB，等
  60s（已等 10min）"——CH 基线 3.6GiB 永过不了 2.5GiB 闸，链已结构性停摆）；子腿进程
  零在飞（无月 INSERT 半程）⇒ 停止零数据风险（CH parts 原子）。
- **执行**：state 全套归档至 `F:/zephyr_cold/50_archive/by_project/zephyralpha/
  bcure_state_archive_20261010/`（8 件，SHA256SUMS.txt 在包内；docs/_working 目录契约
  禁 .log/.py，册内只留证据单 `bcure_state_archive.md`）→ Stop-Process 26768 → 复核=0。
- **使命归属结论**：夜跑新码（T1 停算+P1 闭环）结构性取代其 2019-2021 月粒度重算使命
  （追加令裁定已下）；已完 5 个月保留生效，2021-08+ 月份由夜跑 nightly 全史腿逐日覆盖。
- **禁双开红线状态**：随之解除；T3/T4 进执行窗（仍避夜跑 02:30 与 W1 窗）。
- **T7 提交坑留痕**：归档件先撞格式门（.py）→ 改 .py.txt 撞目录契约（docs/_working 禁
  .log/.py/.py.txt）→ 定版=F 盘原始包+册内 .md 证据单；token 先行同款（PG+主区册+袋内
  册三面一致才过 CREATE-GUARD，注册表 ∈ 袋时预检改读主区盘面册=anchor_main_root）。

## 十一、T4 执行窗战报（追加令后，2026-10-10 16:4x-17:5x）

**Gate 0 前置发现（三层供应链劣化，共同根因候选=QMT 终端下线）**：
1. `kline_daily` 10-08/09 **半量**（2,959/2,960 vs 基线 5,560-5,680）——任务态实证：
   `kline_daily_incremental`（source=miniqmt）10-09 17:13 local 挂死被 auto-reap
   （STALE>6h），rows_total=5,979 半程；水位 last_key=20261009 使增量永不回补
   （17:27 正规重跑"成功"但 10-08 纹丝不动=水位语义实证）。缺行画像=00 主板 1,149+
   30 创业 1,106+92 北证 348（拉数死在半程板块）。
2. `adj_factor` 断在 **09-24**（任务水位 09-28、rows_total=0，source=miniqmt）——hfq
   派生的另一原料腿同欠账。
3. **QMT 终端进程本体现在不在**（xtquant 直调三连"无法连接"；17:27 调度重跑的
   "login success"为残存会话、随即消亡）。akshare 无 raw 日线 capability（444-445 行
   实测仅 hfq/BJ 变体）⇒ 混源补拉属新数据路径，非本班可自决。

**处置**：Gate 0 定向重拉脚本就绪（`.runtime/tmp/st-datalane-20261010/
t4_gate0_raw_daily_repull.py`，provider 直调多板块并集+BufferedWriter 正门，验收=两日
count 回 5,560-5,680 带+repair_kline_degraded_pull 健康三条件）——**明晨 QMT 终端复元
后执行**，随后 adj_factor 重跑→hfq 派生任务（tasks.yaml 实证=本地派生 raw×adj_factor
INSERT-SELECT 直落，非独立拉数）→TI 小批→周月级联→情绪 builder，逐门放行。T3 同因
顺延：当日 ~3,000 万行插入后 RSS 高位站不住任何秒级查询（argMax/LIMIT BY 年切片均
500 实证×6），排明晨静默窗（与 T8 验收同批）。

## 十二、T3 交付（2026-10-10 18:3x）

- **执行**：limit_up_down 2019-01-04..2026-07-19 推导回补 **188,395 行**落地
  （data_source='derived_stk_limit'，与表内既有先例同源码口径；BufferedWriter 正门）。
- **过程坑三条（全实证）**：①LIMIT 1 BY 改写引入 Code 207 JOIN 歧义（argMax 版 500=真
  内存压、LIMIT BY 版 500=SQL bug，被 HTTP 500 掩码误导）；②升序 LIMIT BY 留最旧版的
  方向性 bug（对拍后排除为主因）；③**INNER JOIN+NULL 比对吞行 vs 尺的 LEFT JOIN+
  coalesce**（修复后行数零增量=亦非主因）。
- **验收对拍（与 02_breadth_derivation_report 已发布序列）**：limit_up_count 293/1622 日
  不齐（行差 607/119,167=**99.49% 对齐**）；limit_down_count 3/1622（**99.994% 对齐**）；
  **决定性证据=尺自身推导器（derive_breadth_series.py，盘上原件）单日复算 2019-07-24=55
  与本表逐符号集合一致（差=0）**——残差属于已发布 CSV 的未文档化规则兜底层（报告自述
  limit_up_count"含规则兜底补齐 142 个"同族），非本表缺陷。net_breadth/连板/炸板等 5 条
  序列源自 kline 面板直接推导（从不依赖 limit_up_down 表），T3 断供不涉及其供给。
- **断供修复结论**：表自 2019-01-04 起连续（本班 188,395 行+既有 derived 07-20..31+
  akshare 08-03 起），广度卡母源断供解除；二号重考读径=表行（对拍说明见本段）。
- **删除留痕**：v1 批（升序 bug 版 188,395 行）按 RULE-DATA-OPS 三步走：快照
  F:/zephyr_cold/.../limit_up_down_derived_batch_v1_snapshot.tsv（sha256=215f2a88…）→
  谓词 DELETE（mutations_sync=2，pre/post 点数 188,395→0）→ v2 重写。v2 相对 v1 行数
  相同（方向修复零增量——该批实际等价，删除为口径洁净性操作）。

## 十三、磁盘紧急态与 OPTIMIZE 依据补强（2026-10-10 18:5x 实测）

- **TI 表=239.96 GiB / 1,313 active parts**（dexp 10-08 实测 43.1 GiB ⇒ 两天 5.5 倍）：
  夜跑全史重灌（~8GB/晚）+ 本班 T2 双趟（~25GB，如实自报）+ bcure 半程月 + kline/limit
  写入叠加。
- **D 盘 94%（余 47.2GB）**：今晚夜跑 ~8GB 后约 39GB——撑得过本周末，但 OPTIMIZE 前任
  一晚失效都会加速逼近零。**Owner 需知**：OPTIMIZE 收敛后宿主空间的归还需 vhdx 压缩
  （dexp §11 在案），建议 OPTIMIZE 完成后安排。
- **触发器(a) 结构性结论**：CH tracked=2.04GiB 但 RSS=6.84GiB——~4.8GiB 未追踪开销
  （parts 膨胀 mmap/碎片），OvercommitTracker 按 RSS 判杀 ⇒ FINAL 宽读在 OPTIMIZE 前
  结构性死亡（静默 CH 亦然，18:4x 复测 61.4s 后 241）。⇒ 明晨 T8 若不过线（P1 比对读
  仍被杀=不跳过），OPTIMIZE 反而是打破死锁的唯一手段，呈报候裁。
- **明晚 OPTIMIZE 排程依据**（追加令 T8 已批窗）：23:30 后（W1 明 08:00-22:30 不冲突、
  避 02:30 夜跑）；按月分区推进 dexp 处方；预期回收以实收记账。

## 十四、连夜排水令执行完毕（T1/T2，2026-10-10 21:40-22:28）

- **T1 停夜跑**：`tilib_indicator_backfill_nightly` Ready→**Disabled**（schtasks 留证：
  LastRun 10-10 02:30:01 result=0、NextRun 10-11 02:30 已废）——半量毒数据不会烧进增量
  状态戳。重开条件=Gate 0 补齐后（T3 链尾）。
- **T2 OPTIMIZE 排水**：521/521 分区全扫、**deferred=0**、21:41→22:28 历时 47 分钟。
  实收记账：表 239.95→**182.08 GiB**（-57.87）；VM default 盘 173.7→**233.1 GB**
  （+59.4，含当日遗留 merge 中间件清理）；**daily 行数 FINAL=8,930,466 =dexp 健康
  基线（8,925,969）邻域——2.59× 版本膨胀全数压平**；parts 全表单分区化。
- **账目注**：宿主 D 盘释放需 vhdx 压缩（Owner 点名制，建议随晨报呈排）。
- **T3 QMT**：21:45/22:57 两轮轮询 xtquant 仍拒（终端未开）——Gate 0 链保持就绪，
  值守循环每 45 分钟复测，复元即触发。
- **脚本坑两条留痕**：PARTITION ID 取 partition_id（哈希串）非元组串；CH 双引号=标识符
  （json.dumps 串会被当列名，Code 47）——partition 过滤一律走 partition_id 单引号形。

## 十五、排水令夜段续（2026-10-10 23:4x-10-11 00:1x）

- **系统周任务防双跑**：`ZephyrAlpha-CH-OptimizeMerge-Weekly` Ready→Disabled（原定
  10-11 03:30，本班人工全扫已完成防双跑；择机恢复）。
- **Gate 5 情绪指数=修复**：`emotion_index_close_final` 手动跑成功，10-08/09 close_final
  落库（此前断在 09-30）——上游 limit_up_down（T3）就位后 internal 源即通。
- **QMT 精确诊断（Owner 动作项）**：终端进程在岗（XtItClient PID 17788，监听
  58600/18901）；xtquant 显式 connect(58600) 可连，但**数据服务未就绪**（服务信息
  None；get_market_data_ex ErrorID 200005；download_history_data 挂起）——请 Owner 在
  终端开启投研/极简数据服务（或确认 miniQMT 模式登录）。另：终端重启后数据口动态迁移
  （58610→58600），xtquant 自动发现失效=调度器连不上的根因，调度路径需同款显式
  connect 或终端复归默认口。Gate 0 脚本已带 port=58600 直连（数据服务就绪即跑）。

## 十六、T3 链执行+T8 验收+hfq 管线缺陷围堵（2026-10-11 02:2x-04:0x）

- **Gate 0 PASS**：QMT 终端 Owner 拉起+登录后自动发现自愈（显式钉口方案废弃），
  定向重拉 5,611 批 **11,126 行**落 raw；FINAL 验收 10-08=5,562/10-09=5,564
  （基线 5,566，±0.07%）✓。adj_factor 腿=0 行（窗口内零除权事件，因子未变=干净）。
- **hfq 派生=缺陷产出（已围堵）**：`kline_daily_hfq_incremental` 对 10-08/09 产出
  **7,592 行全零价**（3,796/日；bdpan 锚点 07-03 截断+外推边界的管线缺陷——零价=
  JOIN 侧缺料的 COALESCE 形态，非数据真缺）；其下游 TI 10-08/09 行=全 NULL 指标
  壳（77,872 版本+120min 壳）。**RULE-DATA-OPS 三步围堵**：快照 F 盘
  （poison_rows_kline_daily_hfq…=cbef4262/…technical_indicator_KEYS…=c1a5b603）→
  谓词 DELETE（hfq 7,592→0；TI daily 77,872→0）→ 终态=两表 Oct 8/9 干净缺位。
  120min 壳 1,200 留置（常驻调度器实时重写中，删蚀战无意义；上游 60min Oct 8/9
  缺失修复后自然被正值覆盖）。
- **T8 验收（在补跑班上，2026-10-11 04:05-09:07）**：58/58 片 exit=0、独立
  state-dir 全新记账 ✓；写入量=**7,171,174 行**（超 3.5-4M 基线：P1 比对读仍撞
  未追踪内存墙⇒熔断全写，TI_VALUE_SKIP=0——T8 三件中此件未过线，如实报）；
  4 键探针=行存在但指标 NULL（hfq 零源投影，已围堵）。**T8 满验收顺延至 hfq
  管线修复后的下一班**。
- **夜跑已重开**（Ready，NextRun 10-12 02:30）——明日触发安全：hfq 毒行已清，
  夜跑对 Oct 8/9=干净缺位、对历史=健康重算。
- **呈报 Owner/统筹**：①hfq 派生管线（WO-004 案卷）对锚点外日期产出全零行=缺陷
  实锤（复现命令+快照在案），修复归属=管线案卷车道；②60min/日内族 Oct 8/9 供给
  缺失（同 QMT 断供窗家族，120min 壳为其投影）入日供普查；③vhdx 压缩窗（Owner
  点名制）随 OPTIMIZE 实收呈排。

## 十七、WO-004 修复令执行（2026-10-11 13:4x-17:5x）

- **根因定谳（比夜段结论再深一层）**：hfq 派生路由**从未实现**——internal provider
  fetch 兜底误入 `_fetch_technical_indicator`（技术指标行串台写入 hfq 表），tasks.yaml
  注记的 `_fetch_kline_daily_hfq → recalc_hfq 真源管线` 为设计意图未落地（daban_engine_load
  同款先例：其注释就写着"落到下方默认分支=静默串台"）。夜段"bdpan 锚点截断"结论修正：
  锚点/外推语义无病，病=根本没走到派生逻辑。
- **修复落地**：`_fetch_kline_daily_hfq` 显式路由+窗口化派生（recalc_hfq 口径逐条对齐：
  raw 去重健康五条件、bdpan 主链+miniqmt dr 事件外推双腿、fill 防自叠 anti-join、
  lineage_version=100、volume=intDiv(v,100)、衍生三列 DEFAULT 0、零行产出防双写）。
- **红证**：①路由测试（hfq handler 命中且 TI 兜底零命中；摘路由=源码断言红）；②零行
  防双写+SQL 契约（bdpan/miniqmt 双腿/lineage 100/血统标记/intDiv）；③真火=修复前
  全零价（已围堵）vs 修复后 5,562/5,564 行 **100% 非零**。24+4 测试全绿。
- **定点重算 10-08/09**：直落 5,562/5,564 行，lineage=100 全一，样例 000001
  open=1643.7475/close=1673.5821（raw 11.78×bdpan 因子 ✓）——**T4 缺口正式闭合**。
- **压缩窗实收补记**：窗毕宿主 D 盘 47→**78GB**（+31GB，94%→90%）；VM default
  214.1GB。
- **周任务恢复**：`ZephyrAlpha-CH-OptimizeMerge-Weekly` Disabled→**Ready**（NextRun
  2026-10-18 03:30；表已收敛，后续运行=廉价增量合并）。
- **补跑班 2 号**：17:47 发车（fresh state-dir，58 片），预计 ~22:50 收官——收官即做
  T8 满验收（TI_VALUE_SKIP+写入量+4 键探针）。

## 十八、T8 满验收（补跑班 2 号上，2026-10-11 17:47-23:22）

- **补跑班 2 号**：fresh state-dir 2 号，58/58 片 exit=0、rc=0，历时 5h35m（17:47-23:22；
  收官越 23:00 线 22 分钟——同工作令 OPTIMIZE 23:30+ 批窗家族，无并发车道在飞，如实记时）。
- **验收三件**：①写入量=**6,896,142 行**（超 3.5-4M 基线：P1 比对读仍未接通
  （TI_VALUE_SKIP=0/熔断），全写模式如实报——未追踪内存墙（RSS≫tracked）未解，
  skip 生效依赖后续内存面治理）；②Oct 8/9 FINAL 覆盖=**5,562/5,564（与 raw 完全
  齐平）**✓✓——10 月 OOS 面解锁达成；③4 键探针 **4/4 PASS**（000001/600528/300750/
  002415，10-08/09 行存在且 ma_5/rsi_24 非空=修复后 hfq → 健康 TI 计算链闭合）。
- **T8 判读**：数据质量核心（②③）全过=修复令目标达成；①写入量经济性未过
  （P1 熔断在案），依赖项=比对基读的内存面治理（结构性，已单独立案）。
- **日内族普查（照办入账）**：60min/日内族 Oct 8/9 缺失（120min 空壳 1,200 为其投影，
  留置待上游）；1min/5min 分区 202610 未见于排水清单 top=同窗家族候选——日供普查
  归口带此线索。
- **周任务**：`ZephyrAlpha-CH-OptimizeMerge-Weekly` 已恢复 Ready（NextRun 10-18
  03:30，表已收敛后=廉价增量合并）。

## 九、收尾清单（滚动）

- [ ] 53472 收官确认→T2 探针+冷档→T3/T4 放量
- [ ] T1 今晚 02:30 夜跑写入量对比（明晨读 state+当日入库行数）
- [ ] merge 本班分支回 dev；release 全部 claim；99_delivery 逐件哈希+复核命令

---

# 追加班·数据车道二班 st-datalane2-20261012（2026-10-12 21:2x 起，三件按序）

> 令件=Owner 2026-10-12 指令卡「数据车道二班——数据合并工单」；规格真源=`docs/_working/statsgov_campaign/24_positive_control_backfill_spec_v1.md`（下称 24 号件）。
> 本班写面只两张表：`technical_indicator`（件①）、`stock_daily_basic`（件②③的市值半边）。全程零 DELETE、零 mutation、零改判据、零改在册件字节。

## 十九、开班冷启动与并发结构自决

- RULE-ENV：Python 3.12.8；`setup_dev_env.py --check` usercustomize 在岗（指向 D:\ZephyrAlpha）。
- RULE-GUARDIAN：`lock_files.py cleanup`=CLEAN 无死锁（附带一条 `st-dexp-20261009.json` 分片损坏被跳过的告警，非本班件、未处置）；reaper `--status`=source=live、last_run=21:24:42、scanned=31/whitelist=27、killed=0 ⇒ 写操作门位放行。
- 建班时水位：RAM avail 27.94GiB、commit_pct 66.96%、cpu 75.7%、D 盘余 69.6GB；`worktree_changes=716>50`（并行漂移告警，如实记）。
- RULE-WORKTREE：车道=`.worktrees/st-datalane2-20261012`（分支 `ai/st-datalane2-20261012/task-datalane2-threepack`，建时基 7599a6aff2；同期 dev 已进至 0a9f7eef）。本台账按热件配方先 `cp -n` 存证再取 dev 现面重基：dev 面与车道面均 281 行、零漂移。
- 并发结构（令卡一·四条授权自决）：1 条主区编排进程＋5 条独立 `--state-dir` 车道，片号互斥：L1=023-028／L2=029-034／L3=035-042／L4=043-050／L5=051-057。分片内票集互斥（同表禁双开的实质判据），跨表（basic）互不相干。主区腿在跑期间持主区 P3 单实例锁（21:49-21:57），**交锁后主区无持锁者**⇒明晨 02:30 夜跑照常起批（届时本班车道已全部收尾，不构成双开；但对"表不再变动"这条前置有影响，处置见 廿五·3）。
- 首件校准后再放量：先只开主区腿＋L1＋L2，实测单窗 50-110s（对照夜跑串行 25 分钟/片）且标的清单哈希与全宇宙快照逐片相同，再补开 L3/L4/L5。
- reaper keep 追加：`data/runtime/process_reaper_keep.txt` 尾新增 2 行（注释＋本 sid 子串），键集差自证=+2/-0；在册 runner/worker 子串（`tilib_dwm_shard_runner`/`backfill_technical_indicator_dwm`）本已在册。
- RULE-CAPABILITY-LOOKUP：`CapabilityLookup().find()` 三条反查（A 股历史日线回填／缺口补齐量纲／daily_basic 市值回补）**0 命中**；正对照同尺查"技术指标"命中 1 条（technical_indicator）⇒ 尺是活的，0 命中是真结论：A 股日线历史窗口回填在册无入口（详见 廿二）。

## 廿、②段一 stock_daily_basic 2019-2020 全落＋验收四判据实测

**名实核查（24 号件 §2 点名的前置，先给结论再给数）**
- `scripts/data/backfill_stock_daily_basic.py` 两条腿名实不同：
  - akshare 腿（缺省）：`fetch_symbol` 实调 `ak.stock_zh_a_hist`（价量接口，:46），`to_tsv` 只取 `日期/换手率` 两列，`float_share/circ_mv/total_mv` 一律写 `\N`（:60）⇒ **产换手率＋市值三列空**，跑段一会把市值写成空值＝段一无效。本班未用此腿。
  - tushare 腿（`--source tushare`）：`pro.daily_basic(trade_date, fields=ts_code,turnover_rate,float_share,circ_mv,total_mv)` ⇒ **四列全真值**＝段一/段二市值半边正解。
- 该腿一处硬伤：交易日清单 SQL 硬编码 `trade_date >= '2021-01-01'`（:137-138），`--start/--end` 在该腿**完全未被消费** ⇒ 照命令行"补 2019-2020"去跑，实际重灌的是 2021+ 全段。本班不改在册件字节（见 廿三·缺陷①），改为在临时驱动器里按窗口实算交易日清单后显式传入 `run_tushare()`，同一映射函数、同一 INSERT 形状。
- 单位口径实测对拍（不是推断）：2021-06-01 000001/600519 的 CH 行四列与 `pro.daily_basic` 原值**逐位相同**⇒ 既有段与回补段同为 tushare 原生口径（市值=万元、股本=万股、换手=%），24 号件 §3 判据 4 的单位面成立、无需换算。

**执行账（三段，全走在册件 `run_tushare`）**
| 腿 | 窗口/日数 | 插入行 | 失败日 | 时刻 |
|---|---|---|---|---|
| 试点 | 2019-01-02 × 1 日 | 3,555 | 0 | 21:56:08-09 |
| 主腿 full | 2019-01-01..2020-12-31 × 487 日 | 1,816,924 | 4 | 21:56:38-22:01:40 |
| 自愈腿 missing（按 kline 日历差集） | 4 日 | 14,948 | 0 | 22:02:02-09 |

**验收（24 号件 §3 判据逐条，只读、无 FINAL 正门 fexam.ch_data.ch_query）**
- C1 逐年票数：2019 uniqExact(symbol)=**3,768**，对 kline_daily 在市面 3,771=**0.9992**、对 adj_factor(bdpan) 因子面 3,960=**0.9515**；2020=**4,340**，对 4,366=**0.9940**、对 4,378=**0.9913**。两条分母口径均 ≥0.95 ⇒ 达标；且与"表面 2019 起、实则 237 票"的假完整形态不同（本班实测 2019-01-02 单日 3,555 票）。
- C2 逐日对账：kline 交易日 487／basic 有值日 **487**／缺日 **0**／缺日率 **0.00000%**；日票数比 min=0.96175、median=0.98892、max=0.99775（缺口=停牌/当日无 daily_basic 快照，未填 0 收益，可区分）。
- C3 抽 20 票 × 40 交易日单位自证对拍：`circ_mv/float_share ÷ close` 偏离 ≤5% 的通过 **800/800**，偏离>5%=0（本地 join，不在 CH 里做大 JOIN——写库高峰期 JOIN 实测触发 HTTP 500/Code 241，见 廿三·缺陷⑤）。
- C4 净键与空值面：`count()` 与 `uniqExact((trade_date,symbol))` 逐年相等（2019=885,332／2020=946,540）⇒ **零重复版本**（试点日 2019-01-02 被主腿同键重写一次，入库即在同 part 内合并，无第二版本，如实记）。2019 全列零异常；2020 残余异常面=**90 行四列全 `\N`，全部集中在 2020-09-18 一日**（源侧当日该 90 票无值），另 turnover=0 共 11 行、circ_mv>total_mv 15 行、turnover>100% 1 行（603733 于 2020-08-05，源侧原值）。本班**未删未补**：删需快照+mutation 三步验证，且全 `\N` 行仍是"源查得该票但无市值"的可追溯痕迹；处置权交统筹（见 廿五·待窗②）。
- 行数与 24 号件估算对照：实测 1,831,872 行 vs 估算 198 万 ⇒ 差 = 估算按 (3,771+4,366)/2×487 的"满票面"，实测按源侧逐日在市有快照票数（median 0.989），非漏采。

## 廿一、③段二 市值半边 stock_daily_basic 2017-2018 全落（含两轮自愈）

- 交易日历分母改走源侧 `pro.trade_cal(SSE)`（=487 日），**不用 kline_daily 日历**——因 2017-2018 的 kline 本身是 240 票 stub，拿它当分母等于让被测件出题。
- 执行账：主腿 full_cal 1,428,900 行/444 日（**fail_days=43**，其中 1 日为 CH `Code: 241 memory limit exceeded`：CH RSS 6.43GiB vs 上限 6.80GiB，六车道写库高峰撞墙）→ 自愈一 missing_cal 129,550 行/42 日 → 自愈二 3,128 行/1 日 ⇒ **487/487 日全覆盖，合计 1,561,578 行**。
- 自愈走"CH 实测缺日差集"而非整窗重灌（整窗重灌=给已覆盖键再造一套版本）。
- 验收：C1 2017=**3,468**（对 adj_factor 因子面 3,635=**0.9541**）、2018=**3,611**（对 3,758=**0.9609**）≥0.95 达标；C2 487 交易日零缺日；C3 与 kline 收盘对拍在重叠面（stub 只 240 票）取到 4 票 × 40 日=**160/160 通过**；C4 `count()`=`uniqExact((trade_date,symbol))`（2017=743,941／2018=817,637）零重复版本，四列零 NULL 零非正、circ≤total，换手率越界仅 2017/2018 各 1/2 行（=0，无交易日的源侧 0 值）。
- 净增对盘：`stock_daily_basic` 现覆盖 2017-01-03..2026-10-12（此前 2021-01-04 起）＝**2016 及更早仍缺**（24 号件批复三范围含 2016，本令卡三件只点到 2017-2018，本班未扩窗）。

## 廿二、③段二 价量半边（kline_daily 2017-2018）：本班未执行——实测案卷与可点火处方

**一句话**：在册没有"按窗口给在市股补历史日线"的入口，而今晚要么即兴自造写入口（违 24 号件 §5"不自建第二采集入口"），要么在 22:3x 往全项目被读最多的面注入约 150 万行且留下重复版本——两条都不做，把实测代价与处方交回统筹排窗。

**已实测的事实面（全部零写）**
1. 现状=stub：2017=240 票／2018=237 票（57,213／57,180 行），`data_source='Baostock'`，ingest 2026-08-15..09-29，量纲实测为**股/元**（000005 2017-06-05 volume=3,145,700、amount=16,118,580，与 close=5.11 自洽）；与在档"1990 起但 2019 前仅约 237 票、15× 断崖"同形。
2. 量纲主口径已治本且在册：kline_daily 2019+ 现行 volume/amount 与 `pro.daily` 对照=**vol×100（手→股）、amount×1000（千元→元）**（2019-01-02 000001 CH 53,938,600 股 vs tushare 539,386.32 手；2021-06-01/2026-10-09 同形）。在册参照实现=`tushare_provider._map_bj_kline_rows`（:926-990，16 列、×100/×1000、amplitude=(h-l)/preclose×100、adj_factor=1 不复权、market_type='A_share'、data_source='tushare'）。
3. baostock 通道实测**可用且免换算**：login 1.1s；`query_history_k_data_plus('sh.600000', 2017-01-01..2018-12-31, d, 不复权)` 返回 **487 行**（=满日历）、耗时 **3.74s/票**、volume/amount 原生股/元。按 3,635 票（2017 因子面）串行估 **3.7 小时**；baostock 有 IP 拉黑前科（baostock_provider:136 注记），并发放量前须先小批验。
4. 在册两条相关能力，都不能当本班的窗口化正门：
   - `kline_daily_delisted_backfill`（tasks.yaml:1542，source=baostock，capability=kline_daily_delisted，schedule=monthly_static，incremental=false）：universe=**仅退市股**（`query_stock_basic(status=0)`），每股取 [ipoDate, outDate] **全史**，span 覆盖即跳过 ⇒ 首跑量级=数千退市票×最多 30 年，且会同时新增 2019-2026 段票面（幸存者偏差治理 DS-002 本体，不是"顺手补 2017-2018"能框住的改动）。
   - baostock `kline_daily` 能力：`supports_symbols_null=False` ⇒ 必须显式票清单；`kline_daily_incremental` 主源=miniqmt＋水位驱动，`python -m zephyr.data run` 只有"今日"语义（子命令 status/list/run/rerun-failed/pause/resume/start/speed-test，**无窗口参数**）。
5. 反查留痕：能力反查 0 命中（正对照有效）⇒ 结论与代码勘察一致：**在市股历史窗口回填无在册入口**。

**待统筹点的窗（本班建议，不代裁）**
- 施工内容：新增一次"窗口化 A 股日线全史回填"的在册化（把 2. 的映射从 BJ 专用泛化为后缀集合＋新增按窗口跑在市股的任务或在册脚本），带测试与红证；票面分母建议同时定"在市＋退市"两套（含 000029/200011 这类源侧有快照但无行情的票怎么处理）。
- 写盘义务：2017-2018 与既有 240 票 stub 同键 ⇒ 落地后必须按 24 个月分区做收敛（同键版本去重）并出 `count()` vs `uniqExact((trade_date,symbol))` 对账，否则无 FINAL 读面会双计（在册前科：FINAL 旧行覆盖修正行／重算换名后增量腿回灌）。
- 时序义务：避开 01:00-04:00 夜跑让路窗与 21:00-22:30 W1 窗（窗口须验对象：本班实测夜跑任务 Ready、NextRun 10-13 02:30，对象在）；与 statsgov/cband/mineloop 等在读车道的读窗协调。
- 级联义务：kline_daily 属表族（daily/weekly/monthly 同源派生，WO-004 先例＝周月线须同批跟改）；`kline_daily_hfq` 派生走 bdpan 因子主链（`adj_factor` data_source='bdpan' **实测 1990-2026 全覆盖**，2017=3,635 票／2018=3,758 票 ⇒ hfq 半边不需要新因子源，raw 落完即可用在册派生腿重算）；但复考读面=**`kline_daily` raw（13 号册/11 号册 §source 明记）**，故 hfq/周月线非复考前置，可另行排工。

## 廿三、在册件缺陷与坑（本班挖到，逐条给处方；未落地原因在每条内）

1. `backfill_stock_daily_basic.py --source tushare` 无视 `--start/--end`（交易日清单硬编码 `>=2021-01-01`）⇒ 名实核查合格但"补哪一年"错位，照令跑会重灌 2021+。处方：把该清单改为经 `date.fromisoformat` 校验后的窗口起止（并顺带 5. 的形状问题）；测试钉=给 2019 窗口断言清单内不含 2021 及以后日期。本班未落地原因：主区/车道同件有他会话在途、队列头袋已等 50 分钟，代码袋＋测试袋今晨不划算，处方与临时旁路（显式传日清单）都写在这里。
2. `stock_daily_basic.data_source` 全表标为 `'akshare'`，而 7,118,526 行既有值与本班新 3,393,450 行均为 **tushare daily_basic 逐位等值** ⇒ 标注与真源不符。根因是表 DEFAULT('akshare')＋两条写腿（在册件与 `tushare_provider._map_stock_daily_basic_rows`，其 docstring :1078-1080 明记"data_source 走表 DEFAULT"）都不带该列。本班**未自造第三标**（会让 `WHERE data_source='akshare'` 的读取面静默丢掉新行＝把显式错标换成静默缺数），也未改标 7.1M 行（批量更新属 Owner 门位）。呈批见 廿五·待窗①。
3. tilib 续跑陷阱：`shard_already_done` 只看 `exit==0 ∧ 当日`，于是 022（当日 3/6 窗、exit=0）被整片判"已完成"并跳过，只有 `--only-shard` 能旁路（:357 与 :360-362 的分支差）⇒ 断电后的半截片会被静默漏掉。本班实测命中并靠 `--only-shard 22` 补回 3 窗。处方：跳过判据加"全部窗都在 done 集内"一条。
4. 年窗复用是"当日＋同指纹＋同起止"三条件（`resumable_windows` :140-156）⇒ 跨 0 点后当日成果全部作废、整片重算。本班因此必须在 24 点前收口，并把这一点写进排窗前置。
5. `ch_reader.query` 对 ReplacingMergeTree **自动注入 FINAL**，宽表 FINAL 读=已登记的 241 杀手；本班全程走 `fexam.ch_data.ch_query`（无 FINAL、只读强制）。另该件在册 SQL 里 `DISTINCT ... ORDER BY 1` 的形状在写库高峰会以 **HTTP 500 掩码**出现（同条 SQL 单发即 OK），错误体被网关吞掉——别把 500 当 SQL 错（在册前科：T3 的 500 掩码误判）。
6. 单实例锁语义澄清（防下班误"清锁"）：`data/runtime/dwm_shard_state/tilib_dwm_runner_instance.lock` 由 `scheduler.acquire_single_instance_lock` 持 OS 字节排他锁，**句柄随进程生死⇒崩溃/被杀不留 stale**；盘上文件是惰性残留，本班实测其内 PID 8016 不在进程表，未删该文件、直接由新进程取锁成功。禁把"删 state 目录"当处方（2026-10-09 已废止每晚整目录清理：整目录清=每晚全史重灌 11,227,985 行/趟）。
7. **`--only-shard N` 在取数面退化时会静默空转 rc=0 且零片态**（本班实测命中 1 片：L2 的 030）。机理：`load_symbols()` 走 `InternalComputeProvider._get_symbols`，CH `Code: 241 memory limit exceeded` 时不抛异常而拿到残缺票单⇒`n_shards` 掉到 31 以下⇒`for i in range(n_shards)` 根本不含 30⇒既不打印"开始"、不写 JSON，还照打 `runner done rc= 0`。与在档"查空伪装成查无／静默降级与未触发同形"同族，且比超时更阴——超时至少留 `exit="timeout"`。本班由"发车次数 vs 落盘片数"求差抓到并补跑（L6 车道，22:36-22:4x）。处方：runner 应在 `args.only_shard >= n_shards` 时报红退出。**任何用车道跑片的下班，收工前必须做这个差集，只看 rc=0 会把空转片当已完成。**

## 廿四、①tilib 断点续跑终态（本班收工判据，21:4x-23:1x 实测）

- 停点定性：回填停在 `daily_shard_022` 的 3/6 年窗、`finished_at=2026-10-12T11:51:59`，根因=**断电**（系统日志 Kernel-Power 41 @11:55:55，两证在 cband 台账 :245 与其晨间包 :211），非 reaper 收割（`.runtime/process_reaper/last_run.json` 无 11:5x 击杀记录）。该片 `log_tail` 另有 CH `Code: 241 memory limit exceeded (OvercommitTracker)` 与 `degraded_batches=1`（比对基读失败⇒整窗全写，是"宁多写不少写"的在册降级形）。
- 断点账（逐件点名，非聚合）：000-021=当日 6/6 exit=0（02:30→11:38 夜跑腿）；003=当日 4/6 且 exit=1（`MemoryError` @`src/zephyr/data/buffered_writer.py:184`）；022=当日 3/6 但 exit=0 ⇒ 命中续跑陷阱被整片误判已完成（廿三·3）；023-057=10-10 旧形件（无 windows/done_windows/指纹三键）⇒ `resumable_windows` 返回空 ⇒ 整片重算。
- 执行结构：主区腿（`--only-shard 3`→`--only-shard 22`，复用当日已跑窗，5 窗/461s，21:49-21:57 rc=0）＋L1-L5 五条独立 state-dir 车道（35 片×6 窗，单窗实测 50-110s，21:49:34→23:13:20 全 rc=0）＋L6 一条补跑车道（030 静默空转补回，331.8s @22:41:45，见 廿三·7）。
- **片态终账（只认今晚六个目录，逐片三前置：6/6 ∧ exit=0 ∧ 指纹==本班全宇宙快照）**：`今晚目录片数=58 满足=58 未完成片号=无 今晚查无此片=无 非零退出记录=0`。
- 标的清单不变式：车道 `daily_symbols_shard_NNN.txt` 与本班 21:5x 落盘的全宇宙快照（**5,792 票／58 片**，`daily_shard_057`=92 票）逐片 sha256 相同，35/35 通过；相对 10-10 的 state，第 2300 位之后插入 1 只票使 023 起片边界整体后移，000-022 指纹未变 ⇒ 本班片号语义与主区一致，无漏票无叠票。
- 镜像腿：五条车道＋L6 的 35 组成对 JSON/TXT 已按三前置复制进主区目录 `data/runtime/dwm_shard_state/`（覆盖 10-10 旧形件为今晚真形，前后 sha256 逐片留痕于 `.runtime/tmp/st-datalane2-20261012/`；零删除、零改数据）。主区目录自此与今晚实跑自洽。
- CH 实测面（收工只认这块，片态是工具）：`technical_indicator` period='daily' 逐年 `uniqExact(symbol)` = 2019:**3,770**／2020:**4,366**／2021:**4,845**／2022:**5,184**／2023:**5,382**／2024:**5,437**／2025:**5,501**／2026:**5,599**，对同表 `kline_daily`(A_share) 同年 3,771/4,366/4,844/5,183/5,381/5,436/5,500/5,598 ⇒ **逐年差 0-1 票，覆盖率≈1.000**，无 24 号件 §1 点名的"15× 断崖"形。版本行数同时下降（2021 3,762,504→2,905,392、2024 4,105,725→3,292,598）＝后台 merge 收敛＋P1 值级跳过生效。表体积 202.59→**190.61 GiB**、active parts 1097→**995**。
- 右缘两段性披露（不是本班缺口，是夜跑新鲜度语义的必然）：2026 年窗最大 trade_date 分布=**10-12：2,901 票**（本班车道腿跑时源已到 10-12）／**10-09：2,663 票**（02:30 夜跑腿当时源只到 10-09）／9 月下旬：14 票（退市/长停牌）。cband ⑤ 的 RUN/IS/OOS 右界=2026-09-30，该界内 5,564 票全部有值 ⇒ 复算面成立；最后三个交易日的两段不齐由明晨 02:30 夜跑结构性覆盖，本班不追加写 burst 去动刚交出的静默面（如统筹要即刻齐右缘，处方=对 000-021 用 worker 直调补 2026 窗：`python -u scripts/data/backfill_technical_indicator_dwm.py --periods daily --start-daily 2026-01-01 --end <今日> --symbols-file data/runtime/dwm_shard_state/daily_symbols_shard_0NN.txt`，22 片约 15-30 分钟/三车道）。
- **在册验收门 REG-IND-001 本班跑出 rc=2（如实报，不粉）**：`audit_technical_indicator_coverage.py --symbol 600519 --period daily --start 2026-08-01 --end 2026-08-31` → "全 0 列（12）"= ac/chop_14/highpass_40/ht_dcperiod/ht_dcphase/ht_leadsine/ht_sine/ht_trendmode/macd_divergence/squeeze_mom/squeeze_on/wad。逐列回查 `technical_indicator_registry.yaml`：这 12 列全部落在 **status=retired（6 件）∪ deprecated（5 件）= T1 停算集**（本班数据车道一期 §一 已立法：自 T1 落地起只算 `status==active`，新增行该 13 列=NULL 诚实缺位）。该尺判据是 `df[c].notna().sum()==0`（**全 NULL 即判"全 0 列"**），而 `list_output_columns()` 返回 214 列不按 status 过滤 ⇒ 尺与法漂移，凡 T1 之后写入的窗口一律 rc=2。归因证据（按 ingest_ts 分层计数，同月同标的）：写入于 2026-10-10 的 21 行 `squeeze_on=0`；写入于 2026-10-11/10-12 的 21 行 `squeeze_on IS NULL` ⇒ **NULL 形态早于本班 21:49 起批就已存在**，本班车道只重算 2021-2026 年窗且码面=主区 HEAD（零本班改动）。处方归治理面：该尺应与写侧同册同读径过滤 status，把 retired/deprecated 列移入"诚实缺位"豁免（勿由本班代改他域尺，owner 责任制）。
- 三清单（本班）：
  - 已做且自证：①58 片补齐＋主区镜像＋CH 逐年覆盖对账；②2019-2020 市值 1,831,872 行＋四判据；③2017-2018 市值 1,561,578 行＋四判据；停点归因/续跑陷阱/静默空转三条坑各带处方入册。
  - 未做（带承重证据）：③段二**价量**半边（在册无窗口化入口＋需版本收敛与级联决定，实测案卷在 廿二）；2016 及更早的 basic（令卡只点到 2017-2018）；右缘齐 10-12 的补写（刚交出静默面不再动）；两条在册件代码修复（队列头袋已等 50 分钟，代码袋＋测试袋落地窗口不属本班可自决时段）。
  - 待裁：见 廿五 五条。


## 廿五、要 Owner/统筹点头的事（本班不代裁，逐条给"是什么·为什么要点·不点的后果"）

1. **`stock_daily_basic.data_source` 全表错标**（是什么：7,118,526 行既有＋本班新 3,393,450 行都标 `akshare`，值实为 tushare daily_basic 逐位等值；两条写腿都不带这列、吃表 DEFAULT。为什么要点：改标=对 1,050 万行做批量更新，属破坏性 DB 面；不改标=继续在审计面说谎。不点的后果：任何"按源分账/换源止损"的读法都失真，24 号件 §3 判据 4 永远过不了真。本班处方：先给读侧加一条"源标不可信"的在册告示，改标另起窗、先快照后谓词 UPDATE、逐字段集合差自证）。
2. **段二价量半边的排窗与一个小施工**（是什么：2017-2018 的 `kline_daily` 仍只有 240 票 stub，而复考读的就是这张 raw 面；在册无"窗口化在市股历史回填"入口（廿二 已实测）。为什么要点：要么授权把 baostock `kline_daily` 能力做窗口化在册化（含测试红证＋24 个月分区版本收敛＋周月线级联决定），要么复考继续停在 T≈1,180/t≈2.62 够不到 3.104。不点的后果：批复三"回补到 2016-2018"只做掉市值半边，阳性对照仍出不了终读。本班已给：可用通道实测（baostock login 1.1s、487 行/票、3.74s/票、量纲原生股/元免换算）、票面分母三源、去重与级联义务、避窗清单）。
3. **cband 令晨裁⑤ 的复算窗**（是什么：⑤="tilib 收工后 159 格同册复算＝强制"，本班已把"收工"兑现；但夜跑 `tilib_indicator_backfill_nightly` 明晨 02:30 起跑、实测今晨 02:30→11:38 都没跑完 58 片。为什么要点：复算必须在静默面上读，否则又是一次"回填中途快照"（在册前科：同装置 nostop 基线 OOS Sharpe 从 -0.187 变 -0.590 就是中途读数造成的）。不点的后果：⑤ 复算再出一版void 读数。本班建议二选一：明晨 02:30 前那 3 小时窗内跑完，或申请暂停夜跑一晚（可回退：Disabled→Ready，前任班 10-10 已有同款操作与恢复记录）。**注：暂停计划任务属改系统态，本班未自行动手。**
4. **2020-09-18 一日 90 行四列全 `\N`**（是什么：源侧当日该 90 票 daily_basic 无值，本班按"源有什么写什么"落库，未删未补。为什么要点：留=可追溯但"有行无值"会被"行存在即有数"的读法误当有数；删=要先快照＋DELETE 谓词（破坏性三步）。不点的后果：读侧若不用 `total_mv IS NOT NULL` 谓词会踩空。本班处方：读侧统一加"市值列非空"谓词，删否交统筹）。
5. **D 盘与 CH 内存水位**（是什么：本班期间 CH RSS 顶到 6.08/6.68GiB 一次并因 `Code: 241` 打穿一片取数；D 盘余 69.6GB；`technical_indicator` 现 202.59GiB/1097 active parts。为什么要点：OPTIMIZE/排水属既有排程窗（前班 10-10 全扫 47 分钟收 57.87GiB）。不点的后果：parts 继续堆，写库高峰的 241 会变成常态而非偶发。本班未动 CH 配置、未跑 OPTIMIZE）。
6. **REG-IND-001 验收尺与 T1 停算立法漂移**（是什么：`audit_technical_indicator_coverage.py` 把 T1 起诚实置 NULL 的 12 个 retired/deprecated 列判成"全 0 列"，凡 T1 之后写入的窗口一律 rc=2。为什么要点：这是技术指标域的**验收门**，红着就没法给任何回填/夜跑收官发绿；改法应是与写侧同册同读径按 `status==active` 过滤，属治理面小施工。不点的后果：要么门永久红灯被习惯性忽略（真缺口也看不见），要么有人为了让门绿去把停算列重新灌 0＝把立法倒回去。本班未动他域尺，证据与逐列映射在 廿四 末段）。

## 廿六、复核命令逐条（全部只读，Git Bash 可直接粘）

```
# 0) 门位与水位（RULE-GUARDIAN）
python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status

# 1) ①收工账（只认今晚六个目录，逐片点名；期望=58 片全 ok 且 0 PEND）
python -u .runtime/tmp/st-datalane2-20261012/mirror_lane_state.py            # DRY：plan=58 skip=0 才算收满
python -u .runtime/tmp/st-datalane2-20261012/verify_ti_state.py               # 今晚目录内的 PEND/非零退出清单

# 2) ①CH 实测面（TI daily 逐年票数与右缘；无 FINAL 正门，count 为版本数）
python -u -c "import sys;sys.path[:0]=['D:/ZephyrAlpha','D:/ZephyrAlpha/src','D:/ZephyrAlpha/scripts/backtest'];from fexam.ch_data import ch_query;print(ch_query(\"SELECT toYear(trade_date) y,uniqExact(symbol) s,min(trade_date) d0,max(trade_date) d1 FROM c1_market.technical_indicator WHERE period='daily' GROUP BY y ORDER BY y FORMAT TSV\"))"

# 3) ①在册验收门（REG-IND-001；退出码 0=PASS 2=存在全0列 3=查询失败/空样本，禁把 3 当绿）
python scripts/data/audit_technical_indicator_coverage.py --symbol 000852 --period daily --start 2026-08-01 --end 2026-08-31; echo rc=$?

# 4) ②③落账红绿证（净键=版本数 ⇒ 零重复版本；C1-C4 判据实测）
python -u .runtime/tmp/st-datalane2-20261012/verify_window.py 2019-01-01 2020-12-31   # 段一
python -u .runtime/tmp/st-datalane2-20261012/verify_window.py 2017-01-01 2018-12-31   # 段二市值半边
python -u -c "import sys;sys.path[:0]=['D:/ZephyrAlpha','D:/ZephyrAlpha/src','D:/ZephyrAlpha/scripts/backtest'];from fexam.ch_data import ch_query;print(ch_query(\"SELECT toYear(trade_date) y,count() v,uniqExact((trade_date,symbol)) k,uniqExact(symbol) s,uniqExact(toYYYYMMDD(trade_date)) d FROM c1_market.stock_daily_basic WHERE trade_date BETWEEN '2017-01-01' AND '2020-12-31' GROUP BY y ORDER BY y FORMAT TSV\"))"

# 5) 名实核查复算（akshare 腿产换手率＋三列空 vs tushare 腿四列真值）
sed -n '43,61p;81,119p;128,142p' scripts/data/backfill_stock_daily_basic.py

# 6) 静默空转复现判据（发车次数 != 落盘片数 即为空转，本班实测 1 片）
for x in 1 2 3 4 5 6; do f=.runtime/tmp/st-datalane2-20261012/logs/laneL$x.log; d=data/runtime/dwm_shard_state_resume_20261012_l$x; echo "L$x inv=$(grep -c 'shard=' $f) started=$(grep -c 开始 $f) files=$(ls $d/daily_shard_*.json 2>/dev/null | wc -l)"; done
```

---

# 追加班·数据车道二班 下半程：统筹五裁执行账（2026-10-12 23:40 → 10-13 凌晨）

> 五裁真源=统筹 2026-10-12 夜批复（本班对话内承接，逐条给执行证据；凡属门位动作一律先存证后动手）。

## 廿七、裁1 夜跑停一晚＝已停＋自销毁恢复位已上

- 改前存证：`Export-ScheduledTask` 落 `.runtime/tmp/st-datalane2-20261012/task_def_before_disable.xml`（1,452 字节，sha256 前 16=b38fc7878f162337）；定义要点=日触发 StartBoundary 2026-09-27T02:30:00+08:00、Action=`powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\ZephyrAlpha\scripts\data\backfill_night.ps1"`、UserId=本机账户 SID。
- 改后实测：`tilib_indicator_backfill_nightly` State=**Disabled**、LastRun 仍 10-12 02:30:01、NextRun 面显示 10-13 02:30（Disabled 下不触发）。
- 恢复位（防本班不在场把夜跑永久停着）：一次性质助手任务 `ZephyrAlpha_RestoreTilibNightly_20261013`，Action=`schtasks /change /tn tilib_indicator_backfill_nightly /enable`，Once 触发 10-13 **02:35**，实测 State=Ready/NextRun=10/13 2026 02:35。PS 5.1 的 `Expires` 属性不可写（实测抛"找不到属性"），故助手不会自销毁——**收尾动作**：本班在岗则于 02:35 后手动核 `nightly=Ready` 并删助手；若本班已离场，接手班一条命令撤助手（`schtasks /delete /tn ZephyrAlpha_RestoreTilibNightly_20261013 /f`），删除前先读 `Get-ScheduledTaskInfo` 的 LastTaskResult 确认它已跑过。
- 附带门位账：reaper 计划任务全程未动（本班只碰 tilib 一只）；RULE-GUARDIAN 前提（写操作需计划在岗）全程成立。

## 廿八、裁1 附带新缺陷登记＝夜跑跨午夜"当日戳"整片重灌陷阱（机理实测＋根治处方待裁）

- 机理（读码到判据行，非推断）：`tilib_dwm_shard_runner.py` 两条日期闸——`shard_already_done`（:101-111，`exit==0 ∧ finished_at 前 10 位==今天`）与 `resumable_windows`（:140-156，`当日戳 ∧ 同标的指纹 ∧ 同起止` 三条件，跨 0 点一律返回空）。⇒ 02:30 起跑的夜跑只要跨过 0 点，当晚已完成的全部片在"今天"的定义下集体作废，下一晚 58 片×6 窗从头重灌。
- 实测代价（本台机器今日数字）：今晨 02:30→11:38 共 9h08m 只走完 **22/58 片**，且 11:51:59 被断电截断；本班 21:49 起同码六车道并行实测单窗 50-110s（同片同窗不同负载），即串行一晚跑不完是结构性而非偶发。附带两条同源后果：①同键版本堆到每趟+1（今日 21:4x 实测 202.59GiB/1097 parts，本班跑完 190.61GiB/995 parts——后台 merge 抵掉一部分）；②"表不再变动"对下游复算永不成立（裁⑤ 窗口的真约束）。
- 根治处方（待统筹排窗，本班不动生产码面）：新鲜度**按窗分治**——终点早于 `today-lookback_days` 的历史年窗一旦 6/6 完成即长期有效（源侧行情对过去日期不再改变），只有包含最近 N 日的那个当年窗需要每晚重算；改动点=`shard_already_done/resumable_windows` 两处日期判据（各一处，配 `--lookback-days` 缺省 7），测试钉=历史窗跨日不复算＋当年窗跨日必复算＋同标的指纹变更即作废。预期把夜跑从 9-24h 压到 ≈当年窗一片的量级（实测当年窗单窗 50-250s×58 片串行≈1-2.5h，六车道并行更短），Code 241 写峰与静默面缺失两条同源问题一并缓解。**本条只是处方，未落地，勿引为已修。**

## 廿九、裁2 段二价量半边＝执行账与在册化（数字以收工账为准）

- 票面分母（本班定源并留可复算式）：`c1_market.stock_list` 中 A 股前缀（60/68/00/30，与在册 `_DELISTED_A_PREFIXES` 同族）且 `list_date<=2018-12-31` 且（未退市或 `delist_date>=2017-01-01`）=**3,577 票**（2017=240→目标 ~3.6k、2018=237→~3.76k 的因子面互为交叉：adj_factor(bdpan) 实测 2017=3,635/2018=3,758）。清单落 `.runtime/tmp/st-datalane2-20261012/seg2/universe_part{1,2,3}.txt`（交错切分，1,193/1,192/1,192）。
- 通道＝在册 baostock `kline_daily` 能力（`supports_symbols_null=False`，逐票 payload）：`adjustflag=3 不复权`（#196 主口径）、volume/amount 用 baostock 原生"股/元"（本班实测 sh.600000 2017-2018=487 行满日历、3.74s/票、amount/(volume×close)≈1.006 ⇒ 与治本后口径一致，**零自算换算**）；写入走 `BufferedWriter` 正门。**没有**用 `fill_gaps_tushare.py`（其 :191 裸存"手"，跑一次即把该段灌成 1/100 量纲——本班列为在册缺陷，见 廿三·6 同族）。
- 编排件（在册化小施工，见 三十 的码面清单）：`scripts/data/backfill_kline_daily_history.py`——逐票 state 续跑（重跑=自愈，不是重灌）、不可解析票点名不静默、失败票不落 state 且 rc=1、dry-run 零写。
- 执行账（三车道并行，三进程各自 rc=0、日志内 FAIL 行数=0）：part1 1,193 票/554,056 行（23:45:01→00:33:36，48.6min）、part2 1,192 票/447,754 行（→00:39:47，54.8min）、part3 1,192 票/397,131 行（→00:35:04，44.7min）＝**票单 3,577 全跑、写库 1,398,941 行**。
- ⚠ 但**判据 1 未过，本班不宣布价量半边收工**：D1 实测 2017=2,945 票/699,246 版本行/净键 687,094、2018=3,007 票/735,278/723,505；按 24 号件"当年在市"分母（stock_list 前缀 60/68/00/30 且当年在市）2017=3,472／2018=3,572 ⇒ 覆盖率 **0.8482／0.8418 < 0.95**。缺的 565-590 票全部是**零行票**（清单 `.runtime/tmp/st-datalane2-20261012/seg2/zero_row_codes.txt`，590 只，全部 sh.60xxxx 段），根因＝baostock 对连拉 ~5,000 次后的会话限流：在册 provider 那段是 `while rs.error_code=='0' and rs.next()`，**限流时既不给行也不给 error**，与"窗口内真无行情"完全同形（本班级别事故同族：查空伪装成查无）。本班 01:03 复探两票直接挂死（SDK 无 socket 超时）⇒ 判定 IP 仍在冷却，**不硬撞重试**。
- 已改的静默形态（在新件码面里，随未落地件保存）：零行票**不写 state**、单列 `<state>.zero_row.txt`、整体 rc≠0，配 2 条测试钉（零行不判成功／下轮必重试）；车道 state 是旧码跑的，故 590 只已被记成"完成"——重试须用零行清单另起一份 state（命令见 廿六·7 与本节末）。
- 自愈命令（冷却后一条即续，幂等）：`python scripts/data/backfill_kline_daily_history.py --start 2017-01-01 --end 2018-12-31 --symbols-file .runtime/tmp/st-datalane2-20261012/seg2/zero_row_codes.txt --state-file .runtime/tmp/st-datalane2-20261012/seg2/state_retry.txt`（新件当前只在车道 `.worktrees/st-datalane2-20261012/scripts/data/`，字节存证 sha256 前 16=c3fedb957c36d66d，测试件 2318792bffded355，见 三十 的登记阻断原因）。
- 收工判据实测（价量半边，全部只读）：D0 同键双版本 23,925 个而**值分叉键=0**（老 stub 与新行同源同口径 ⇒ 合并保留哪版都一样）；D2 逐日 487/487 零缺日，kline/basic 日票数比 min=0.838 median=0.908（差值＝停牌日 basic 有快照而 kline 无行，未填 0 收益可区分）；D3 与 tushare 市值面跨源对拍 20 票×40 日 **800/800** 通过（circ_mv/float_share÷close 偏离≤5%）；D4b 坏值面 `close<=0`=0、`open<=0`=0、`high<low`=0、`turnover` 非零=15,508/15,946（本能力不取 turn 列，与 2019+ 段同形为 0 兜底）；D4c 量纲比值按月分片实测见下（首版整表 median 撞 HTTP 500＝CH 内存墙，改分片后全过）**min 0.9987／median 1.0000／max 1.0012** ⇒ 全段 volume=股、amount=元，无"手"口径混入（若为手该比值≈100，若踩 09-22 前旧坑则≈0.01）。
- 周月线"跟不跟改"决策（本班随件定，证据在此）：D5 表族实测 2017-2018 段＝`kline_daily_hfq` 113,310 行/240 票、`kline_weekly_hfq` 23,638/239、`kline_monthly_hfq` 5,570/239（三支仍 stub 形），`kline_weekly`/`kline_monthly` 两名查无（表族实际＝raw daily ＋ 三支 *_hfq）；`adj_factor` 同段 1,898,327 行/4,189 票 ⇒ 后复权因子源齐备，hfq 半边随时可用在册派生腿（WO-004，bdpan 主链）补 ⇒ 结论=本轮**不扩到 hfq/周/月**：复考读面是 `kline_daily` raw（11/13 号册 §source 明记），把表族级联塞进今晚只扩大静默面扰动而无验收收益；已列为 卅一·6 独立待排件。

## 三十、裁3 改标＝存量已改，写侧修复被一条门位挡住

- 三步验证留痕：①必要性=统筹批复"机械性纠错非资产判死，执行归你班"；②真实性（逐行来源证明，本班前置判据）=`countIf(turnover_rate IS NOT NULL AND (float_share IS NULL OR circ_mv IS NULL OR total_mv IS NULL))` = **0**，即 akshare 腿（产换手率＋三列 `\N`）在全表从未成功落过一行 ⇒ 10,511,976 行的值面均来自 tushare `pro.daily_basic`（另有逐位等值对拍：2019-01-02 与 2021-06-01 两票四列全等）；③可逆性=改前逐字快照 `F:/zephyr_cold/50_archive/c1_market/stock_daily_basic_datasource_relabel_snapshot_20261013/`（10 个年度 TSV＋MANIFEST.tsv，行数合计 10,511,976 与表内 `count()` 相等，逐年 sha256 在册）。
- 执行：走在册 TCP 通道 `ch_writer.get_client()`，`ALTER TABLE ... UPDATE data_source='tushare' WHERE data_source='akshare' SETTINGS mutations_sync=2`。前后自证：PRE=akshare 10,511,976／非 akshare 0 ⇒ POST=**tushare 10,511,976／残留 akshare 0／总行数不变 10,511,976**；固定 10 行样本（2017-06-05/2019-01-02/2021-06-01/2023-03-01/2026-10-12 × 000001/600519）前六列**逐格未变=True**（数值面零改动）。证据全文=`.runtime/tmp/st-datalane2-20261012/logs/relabel_basic.log`。
- ⚠ 写侧修复没做，原因是一条门位而不是懒：表结构真源 `schemas/categories/market/market_stock_daily_basic.py` 头部标 `[AI_AUTONOMY] human_only` + `[MODIFY-GUARD] schema-change`，且 `tests/legacy_zephyr/data/test_providers.py::TestTushareStockDailyBasic::test_columns_align_stock_daily_basic_schema` 把"provider 产出列 == schema 的 `INSERT_COLUMNS`"钉死 ⇒ 只改 provider 会红那条钉，改 provider＋弱化那条钉＝拆真源一致性（禁）。本班不越闸。**要的一句话**：授权把该 schema 文件的 `INSERT_COLUMNS` 加 `data_source`（配套四处：schema 一行／provider `_STOCK_DAILY_BASIC_COLUMNS` 加一列／`_map_stock_daily_basic_rows` 行元组尾追 `"tushare"`／上述测试两断言随形）。
- 临时态如实报：写侧修复落地前，日常增量腿新写的行仍会吃表 DEFAULT('akshare') ⇒ 全表 uniformity 会重新破损；修复落地后**同一条 predicate 重跑一次即可**（本班脚本幂等，重跑安全）。

## 卅一、残余·待排窗·待授权（下半程新增，逐条给后果）

1. **裁2 授权语（schema 之外的写侧两处）**：`tushare_provider` 的列与行映射加 `data_source`，与 三十 的 schema 改动同批——批了本班就能一次把"改标＋写侧修好＋复跑一次清破损"收口。不批的后果=源标会继续每日新破损。
2. **`scripts/data/*` 通配忽略的收编惯例**：本班新件按在册先例（`sz_open_data`／`source_health_patrol`／`backfill_technical_indicator_dwm`／`emotion_index_snapshot`）加了一行 `!scripts/data/backfill_kline_daily_history.py` 豁免；同时发现 `backfill_stock_daily_basic.py` 与 `fill_gaps_tushare.py` **至今未跟踪**（前者是 tasks.yaml 明记的"人工兜底"件，后者是被 廿三·6 判为量纲过时的件）⇒ 兜底件长期脱管、清扫即蒸发（在册先例：onboard_source/fx_ecb 那批就是 commit message 写了豁免但 .gitignore 实未合入）。建议下一班按同模式收编或退役。
3. **机生清单的存量缺口（非本班件）**：`generate_manifest.py` 全树重扫得 1,248 条，在册投影只有 1,243 条，差 5 条中除本班新件外有 4 条 `backtest/fexam/arm_protocol_binding.py`／`backtest/fexam/card_binding.py`／`backup/backup_reconciler_shadow.py`／`governance/generators/generate_collection_shard_manifest.py` 长期未登记。本班只在袋内**代带自己那 1 条**（键集差自证 +1/-0），其余 4 条留给各自主人，未代改。
4. **Ghost session 咬掉本班第一只袋**（在册五形态之四的现场复现）：23:35 本班 release 唯一 claim 后无活动，心跳守护按 idle>1800s 自退，注册表条目消失 ⇒ 队列落地侧判死，`q-20261012-st-datalane2-20261012-0001` 死于 `dead_reason=ghost_session`（自动重投被存活闸拒绝）。本班已按在册正门复命（`register(pid=0)` ＋ 守护入口=包模块重拉 PID 32432 ＋ 具名 keepalive TTL 7200），账本改随末袋重投。教训入册：**长批在飞期间 release 掉最后一个 claim 之前，必须先授 keepalive 或留一个刷活通道**。
5. **段二价量半边的 24 个月分区收敛义务**：本班实测同键双版本的分叉与否见 廿九 D0；收敛动作（按月 OPTIMIZE FINAL）属排水窗家族，本班不在写库高峰自启。




## 卅二、收尾账（02:0x）：收敛已做、在册化差一步、袋与恢复位清单

- **24 个月分区版本收敛已完成**（裁2 明列授权项）：逐分区 `OPTIMIZE TABLE c1_market.kline_daily PARTITION '<yyyymm>' FINAL`，24/24 全 dup=0；收敛前 2017=699,246 版本/687,094 键（dup 12,152）、2018=735,278/723,505（dup 11,773）⇒ 收敛后两年度 **versions==keys**，票面 2,945/3,007 与交易日 244/243 一根没少。语法一条（本机 CH 实测，值得入册）：`ALTER TABLE ... OPTIMIZE PARTITION ID 'x' FINAL` 判 **Code 62 语法错**，可用形是 `OPTIMIZE TABLE ... PARTITION '201701' FINAL`；通道=ch_writer TCP 正门（fexam 只读门必拒 ALTER，实测"拒绝非只读查询"）。日志 `.runtime/tmp/st-datalane2-20261012/logs/converge5.log`——该日志"用时"字段本班自犯一处（monotonic 与 epoch 混算致打印成天文数字），分区级 dup 数字才是判据，未用它支撑任何结论。
- **价量半边状态＝未收工（如实）**：票面覆盖 0.848／0.842 < 0.95，缺的 590 只全在 sh.60xxxx 段＝baostock 限流造成的零行票（清单 `seg2/zero_row_codes.txt`）。本班 01:03 复探两票直接挂死（SDK 无 socket 超时）⇒ 判定仍在冷却，**不硬撞**（继续撞会换来更长的 10001011 黑名单）。接手一条命令自愈（新码已把"零行不判成功"钉死，重跑只补零行票）：
  `python scripts/data/backfill_kline_daily_history.py --start 2017-01-01 --end 2018-12-31 --symbols-file .runtime/tmp/st-datalane2-20261012/seg2/zero_row_codes.txt --state-file .runtime/tmp/st-datalane2-20261012/seg2/state_retry.txt`
- **在册化差最后一步（工具层墙，非本班偷懒）**：新件与测试已写好且被本班实跑用过（1,398,941 行经它落库；7 钉测试全绿、ruff 净），但**入不了袋**——`batch_creation_tokens.py`/`register_asset.py` 的候选扫描是 `git ls-files -- <prefix>`，以**主区工作树**为准；按 RULE-WORKTREE 隔离在车道的新件永远"前缀为空"，token 与翻译册投影位都登记不上，两次实跑均回"无待登记文件"。本班不把件拷进主区强登（那会把隔离面与归属面搅混，且主区暂存池本就混着 8 个会话）。字节双存证：车道 `.worktrees/st-datalane2-20261012/scripts/data/backfill_kline_daily_history.py`（sha256 前 16=**c3fedb957c36d66d**）＋ `tests/data/data/data/test_backfill_kline_daily_history_window.py`（**2318792bffded355**），另有 `.runtime/tmp/st-datalane2-20261012/quarantine/` 同名副本（在册教训"未入库源码归档过期＝没留"，本班两处同取）。接手三步（在主区跑即一次通过）：①`batch_creation_tokens.py --prefix scripts/data/backfill_kline_daily_history.py --created-by <sid> --capability data_supply_chain --merge-evaluation "非第二真源：取数与换算单点仍在册 baostock provider，本件只做窗口编排与续跑"`；②`add_module_translation.py --path <同路径> --domain D_DATA --name-zh "A股日K线历史窗口回填器" --plain-zh <≥8 字大白话>`；③`.gitignore` 加一行 `!scripts/data/backfill_kline_daily_history.py` 收编豁免（先例=sz_open_data／source_health_patrol／backfill_technical_indicator_dwm）＋`generate_manifest.py` 只取本件那条（键集差自证 +1/-0）。**注**：②的 render 会把 PG 内他人未落地条目一并写进投影（本班实测带进 9 条：cband_grid／statsgov_deflation_and_budget／build_distilled_sft_dataset／src/zephyr 下 6 个夹具样名，后者疑为测试写穿 PG 的残留，另列待查），代带＝归属篡改，接手须走"投影先行同步＋点名代带"或先清 PG 他人行。
- 袋面清单：`q-20261012-st-datalane2-20261012-0001`（账本首版）死于 `ghost_session`（死因与复命见 卅一·4；字节未丢，账本现面即超集）；`q-20261013-st-datalane2-20261012-0002`（裁4 修尺＋4 钉测试）pending，前置 10 袋；账本本件随末袋重投。
- 夜跑恢复位：助手任务 `ZephyrAlpha_RestoreTilibNightly_20261013` State=Ready、NextRun=10-13 **02:35**（Action=`schtasks /change /tn tilib_indicator_backfill_nightly /enable`）。本班若在 02:35 后仍在岗，复核 `nightly=Ready` 后删助手；若已离场，接手一条 `schtasks /delete /tn ZephyrAlpha_RestoreTilibNightly_20261013 /f`（删前读 `Get-ScheduledTaskInfo` 的 LastTaskResult 确认它已跑过）。PS5.1 的 `task.Expires` 属性不可写＝实测抛"找不到属性"，故助手不会自销毁。
- 数据面净效果一行（供统筹对账）：`technical_indicator` 58 片×6 窗补齐（右缘两段性已披露）；`stock_daily_basic` 2017-2020 补 3,393,450 行/974 交易日＋全表源标改 tushare（值面逐格未变）；`kline_daily` 2017-2018 补 1,398,941 行/3,012 票并完成 24 分区收敛（尚缺 590 票待限流冷却）。全程零 DELETE、零数据 mutation（唯一 mutation＝裁3 改标一行一列，前后点数与逐格数值对拍在册）。

## 卅三、更正与本班最后一次实测（按 Owner 追认的"更正另起、留旧案卷"体例，不回改上文）

- 时刻校正：上文 §卅二 把 24 分区收敛写作"02:0x 完成"，实测为 **01:3x 起、01:40 前完成**（本机 `date` 实测链：00:39:16 三车道全 rc=0 → 01:03:24 零行票复探挂死 → 01:40 收敛日志终态 → 01:42:38 计划任务面复测）。本班体感钟长期偏快约一倍（在册自犯条目同族），凡此刻度相关的叙述一律以 `date` 实测为准，旧句不回删、以此条为准。
- 让路窗如实补一条（不自我豁免）：收敛与 D4c/D5 探针确实落在 01:00-04:00 窗内；窗内的让路对象（`tilib_indicator_backfill_nightly`）经裁1 已跳过 02:30 一批，本班亦未在窗内跑宽表装载读；02:35 助手恢复位已上并将在下文复核回执。
- **限流未解除的最后一次实测**：01:44:27 单探针——`bs.login()` 通、首只 `sh.60xxxx` 零行票查询 70 秒不返回（SDK 无 socket 超时）⇒ 判定 baostock 侧仍在拉黑/限流，本班**停止重试**（继续撞只会延长封禁）。590 只票的重试窗口请留到源侧冷却后（建议 ≥6 小时后单进程试 3 票，通了再放量；命令在 §卅二）。价量半边因此按"未收工"交接，不签收工。

## 卅四、四裁落地：③呈 Owner 晨包件（两栏＋四件清单）＋590 只重试已上机械闸＋三雷移交包（本班最后一次落账）

### 1. 晨包件：写侧来源标签要不要随形改四处（Owner 面，一句话可裁）

一句话＝**改**：以后每行自己带对来源，不再靠表默认值兜底；**不改**：每个交易日新增约 5,561 行贴错来源标签的行（这是实测日均行数，不是估）。两栏都给了可核的命令，明早不用信本班的话。

- 栏一【批＝四处随形改】零判据变更、零阈值变更、回退＝revert 单袋：
  - 件① `schemas/categories/market/market_stock_daily_basic.py:69` 现值
    `INSERT_COLUMNS = "(trade_date, symbol, turnover_rate, float_share, circ_mv, total_mv)"`
    → 末尾追加 `, data_source`（此文件头 `[AI_AUTONOMY] human_only` ＋ `[MODIFY-GUARD] schema-change`，本班不动它，改动清单只呈上不落地）。
  - 件② `src/zephyr/data/implementations/tushare_provider.py`：
    `:1061-1068` `_STOCK_DAILY_BASIC_COLUMNS` 列表追加 `"data_source"`；
    `:1102-1111` `out.append(( td, code6, _num(...), _num(...), _num(...), _num(...) ))` 行元组末尾追加 `"tushare"`；
    `:1079` docstring 现句"INSERT_COLUMNS 6 列、data_source 走表 DEFAULT"要同批改——这句是**对现状的正确描述、对目标状态的错误描述**，改码不改它＝码与文分家（在册教训 `silent-degradation-looks-like-not-triggered` 同族）。
  - 件③ `tests/legacy_zephyr/data/test_providers.py`：
    `:2173` 断言 `assert rows[0] == ("2026-09-21", "000001", 0.8712, 194591.0, 2116934.8, 2190900.0)` → 追加第 7 项 `"tushare"`；
    `:2180-2185` `test_columns_align_stock_daily_basic_schema` 是 `set(provider 列) == set(schema INSERT_COLUMNS)` 的**两侧对拍**，同步加列后自动跟上，不改；
    `test_fetch_route_per_trade_date` 只查 `rows[0][1]` 与 `last_key` → 不受影响。
    这三条本班已读断言原文逐支定性（非"应该没事"的推断）：一处必改、两处必不改。
  - 件④ 落地后补一记幂等清账（清掉"改码在飞那几天"日增量腿贴错的行）：
    `ALTER TABLE c1_market.stock_daily_basic UPDATE data_source='tushare' WHERE data_source='akshare' SETTINGS mutations_sync=2`
    ——同语句本班 10-12 已实跑过一次，账在册：`system.mutations` 该条 `is_done=1 / parts_to_do=0`（03:0x 实测读回）。
- 栏二【不批】后果（实测分母，逐条可复算）：
  - 每日增量腿的产出列里始终没有 `data_source`→ 由表 `DEFAULT 'akshare'` 兜底 ⇒ 每个交易日新增约 5,561 行来源错标。近四日实测：2026-10-08＝5,557、10-09＝5,559、10-12＝5,561 行/日。
  - 存量已修：**现全表 `data_source='akshare'` 命中 0 行**（03:0x 实测），10,511,976 行 / 10,506,415 个 (trade_date,symbol) 键全标 tushare。
  - 不批不会错数值、不会错去重键、不会错单位——只是"这行是谁给的"这一个字段会一天天重新变脏。**是标签债，不是数据债**（这正是统筹"机械性纠错非资产判死"的定性，本班照此呈，不抬高也不压低）。
- 可翻案的预测（留给明早一条 SQL 判真伪，比读本班结论快）：
  预测＝若件①②未批，10-13 收盘后日增量腿落的行会**再次显示 `akshare`**。
  复核命令：`python -c "import sys;sys.path.insert(0,'scripts/backtest/fexam');from ch_data import ch_query;print(ch_query(\"SELECT trade_date, data_source, count() FROM c1_market.stock_daily_basic WHERE trade_date>='2026-10-13' GROUP BY trade_date, data_source FORMAT TSV\"))"`
  出现 akshare＝预测成立且"日损 5.5k 行"成立；仍是 tushare＝本班对写侧路径的判断有误，须另查（那时本班结论作废，以 SQL 为准）。
- Owner 只需回这几种话之一：「批四处随形改」／「不批，标签债记账」／「批但换班做（本班不动手）」／「先给 CH 现值快照再议」。

### 2. 新实测事实（不在任何上文，本班 03:0x 查 CH 系统表所得，属意外发现非本班所为）

- 2026-09-30 这一日是**整日双版本**：`count()=11,122` 而 `uniqExact(symbol)=5,561`（全表仅此一日有此形态）。逐键值面对拍：5,561 键**全部**在 `ingest_ts` 上不同（两批 `ingest_ts`＝09-30 08:31:56 与 10-08 08:45:56，UTC 列），**值面差异只有 2 个键**，且量级为 float_share 6.7 万股（0.004%）与换手率末位浮点表示——样例：300274 与 688282。
- 归因＝10-08 那次日增量腿**重采了已入库的 09-30**，一次 insert 整日 5,561 行落成新 part（`system.parts` 实测：`202609_1395_1395_1_2376` 行数恰＝5,561，与主 part `202609_1373_1394_7_2376` 并存未合）。本班改标的 mutation 只是给两个 part 都盖了标签，**不是双版本的来源**（两 part 的 mutation 版本号同为 2376，即改标发生在双版本之后）。
- 读侧后果（要说透，否则这条会被当成噪声）：表无版本列 ⇒ `FINAL` 取后写入的那版（10-08 修正值）；**不带 FINAL 的读会整天双计**；本班段一/段二验收一律用 `uniqExact((trade_date,symbol))` 而非 `count()`，正是为避开这一形（在册 C1 口径）。这条与统筹"2020-09-18 那 90 行＝留＋读侧非空谓词"同族＝读侧谓词义务，不是删行义务。
- 是否要 OPTIMIZE 该分区收敛＝可逆动作但非本班被派的面，本班未动，登记为待裁可选项（若裁"收敛"，命令＝`OPTIMIZE TABLE c1_market.stock_daily_basic PARTITION '202609' FINAL`，注意在册实测：`ALTER … OPTIMIZE` 形态报 Code 62，必须用 `OPTIMIZE TABLE` 形态）。

### 3. 590 只重试：预签件已落地并上机械闸（本班零次真撞 baostock）

裁定原文照抄执行面＝"≥6 小时冷却（约 08:00 后）先单探 3 票，通了放量 590；禁再撞"。本班把"禁再撞"写进**文件**而不是写进自觉：三道闸＋"起跑即记账"。

- 待补面重新实测：零行票单 590 只 → 剔掉 CH 里 2017-2018 现已有行的 22 只 → **实际待补 568 只**（放量时不盲跑已入库票，省源侧配额；每次起跑重新按 CH 现值反推，故后续重跑自愈）。
- 探针用**已知正对照**不是随手抓：`sh.600141 / sh.600556 / sh.600315`，实测三只窗口内各 487 行、且**都不在零行票单里**。理由＝若拿零行票单里的票当探针，"该票真无史"与"通道仍限流"两种病因同形，会把健康通道误判成坏通道（在册自犯条目 `zero-hit-ruler-needs-known-positive-control` 一族，本班这次按正对照做并把理由写在件头）。探针跑 `--dry-run`：不落库、不写 state。三票全通才放量；任一不通 → rc=22、放量 0 票、只留证不重试。
- 一次性任务已登记（与在册 `tilib_indicator_backfill_nightly` 同参数档，非本班自创）：
  任务名 `\ZEPHYR-DATALANE2-SEG2-RETRY`｜NextRunTime＝2026-10-13 08:05｜ExecutionTimeLimit＝70 分钟｜`LogonType=Interactive / RunLevel=Limited / UserId=fanzi`（实测读回，与夜跑任务面逐字对齐）｜`StartWhenAvailable`（错过时刻开机即补跑一次）。
  **作废命令**＝`schtasks /delete /tn ZEPHYR-DATALANE2-SEG2-RETRY /f`（零常驻，删掉即无残留）。
  防误杀＝任务命令行含 `.runtime/tmp/st-datalane2-20261012/…`，命中在册 keep 裸行 `st-datalane2-20261012`（reaper `_load_keep_patterns` 是**子串**匹配且裸行永不自动清理，本班读源码核实口径后才据此免新增）——**未加新 keep 行**。
  让路面＝放量段 `--max-minutes 45` 到点自停：08:05 起跑最迟 08:5x 收，早于 09:00 采集与 09:20 板块指数例行；依据＝在册车道日志实测单道 0.41-0.44 票/秒 ⇒ 568 只≈22-23 分钟，45 分钟有余量。截断不算失败：state 只记已完成票，下一轮（须再过 6 小时冷却）同命令自愈。
- 件与执行记录（三处双存证，接手可直接复跑）：
  执行器 `.runtime/tmp/st-datalane2-20261012/retry_seg2_zero_row.py`｜启动器 `…/run_retry.cmd`｜登记器 `…/register_retry_task.ps1`（纯 ASCII，遵 .ps1 铁律）；
  日志目录 `…/seg2/retry_log/`（`wrapper.log` 每行带本机时刻、`scheduled.out` 为任务面输出、`probe_*.log`/`scale_*.log` 为子进程原文）；
  机械记账 `…/seg2/retry_marker.json`（`last_probe_start` 起跑即写＝冷却闸的判据来源，崩了也算一次，防"失败即免责"）。
- 自检 9 钉全绿（**全程零 baostock 网络**：管道用桩件验，真探针留给 08:05）：
  探针管道 rc=0/counts 正确、dry-run 不写 state、探针不通必须挡住放量、挂桩 3.2 秒自停、放量写 state 且计数正确、CH 只读门取到 3,012 覆盖票、待补反推 590→568、正对照三只确不在零行单、冷却闸回 rc=21。
  自检件 `.runtime/tmp/st-datalane2-20261012/selfcheck_retry_gates.py`（桩件 `stub_done_line.py`，可复跑）。
- **本班自抓两处设计缺陷（按"更正另起、发现即报"体例，不等被问）**：
  第一版把"让路窗到点自停"写成**行驱动**（在 `for ln in proc.stdout:` 里看时钟）。子进程 stdout 经管道是**块缓冲**的，真挂住时（baostock SDK 无 socket 超时正是这形态）一行都不出 ⇒ 死线检查永不到达。实测＝02:53:26 起跑的挂桩到 02:56 仍在跑，被本班手动 kill；改成计时驱动（读线程＋主循环只看时钟与 EOF）后同一挂桩实测 3.2 秒自停。
  第二处：stdout EOF ≠ 进程已退，不 `wait()` 则返回码恒 `None`——自检第一轮两条红抓到（`probe_pipe_ok [rc=None …]`），补 wait 后转绿。
  意义要说白：这两处若不修，08:05 真挂住时**不会自停**，会把整个让路窗占满并把封禁时长再推一晚。闸的判据必须是落地实测，不是设计愿望（在册 `dry-run-signal-is-not-the-executing-gate` 反面同族：这次连"桩件跑通"都不算，直到真 kill 计时被量出来）。

### 4. 三雷移交包（统筹已立案转维护四班，本班把证据与复核命令点齐，不代修）

- 雷一 ghost 烧袋（并入 W-1b 簇，又一实例）：袋 `q-20261012-st-datalane2-20261012-0001`（23:26:27 入队）死因原文＝`ghost_session: 属主会话 st-datalane2-20261012 已死（heartbeat=exited / 注册表无在册）`。触发链实测＝23:35 本班释放**最后一个** claim → `heartbeat_daemon` 按 idle>1800s 自退并在 `heartbeat.jsonl` 落 `status=exited` → 注册表条目消失 → 袋被存活闸判死。复命四步（已验，本次靠它把账救回）：`register(pid=0)` → 以**包模块**方式起守护 `python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon <sid> <root> 30 <worktree>` → `register_heartbeat_keepalive(reason≥8 字, ttl_seconds≤7200 上限)` → `list_active_readonly()` 读回 hb_age≤90s。本班 02:48 复测＝守护 pid 32432 活着、心跳末行 status=alive、age 18s、在册 active_total=11 含本 sid。留给维护四班的问句（本班不代答）：释放最后一个 claim 是否该顺带解除保活义务？判死前是否应先消费三证（在册三证旁证立法）而非只看 heartbeat 末行？
- 雷二 `scripts/data/*` 通配咬**已跟踪件**（入工法＋转维护四班）：袋 `q-…-0002` 死因原文＝`prestage 拒绝：以下快照路径被 .gitignore 忽略（再生产物区，禁入 git）：scripts/data/audit_technical_indicator_coverage.py`——而该件实测 `git ls-files --error-unmatch` 通过＝**早已在库**。故 `.gitignore:610` 的 `scripts/data/*` 通配拦的不是"新增未收编件"，而是"对在册件的修改"，这与直觉相反（门禁读 index/HEAD 面，prestage 读 ignore 面，两套判据打架）。本班按门自己给的处方②走通（加 `!scripts/data/audit_technical_indicator_coverage.py` 精确豁免，先例＝sz_open_data），复投即合并落地。该成文的规则（供维护四班落册，非本班自封）＝"改在library 的 `scripts/data/` 件，豁免行须与件同袋或先行；只读 prestage 判据可先看 `git ls-files` 命中即豁免"。
- 雷三 PG 翻译账本测试写穿残留（急件，六行全名点齐供确证）：来源＝本班渲染 `module_translation_registry.yaml` 投影时带出 9 条他人未落地条目，其中 6 条为夹具样名：
  `src/zephyr/degraded.py`（name_zh 降级模块／plain_zh "降级模块的大白话简介内容"／domain_id **D_TEST**）、
  `src/zephyr/layered.py`（改名后／D_TEST）、`src/zephyr/lying.py`（谎报模块／D_TEST）、
  `src/zephyr/new_mod.py`（新模块／D_TEST／responsibility_layer governance）、
  `src/zephyr/orphan.py`（孤儿模块／domain_id **D_NOT_IN_MAP**）、`src/zephyr/with_extras.py`（写手更新／D_TEST／governance）。
  本班新做确证＝**六个 module_path 在盘面与 git 双双查无**（03:1x 实测 `test -f` 六连 MISSING ＋ `git ls-files` 零命中）⇒ 不是"未落地新件"而是纯残留行；且 domain_id 只有 D_TEST/D_NOT_IN_MAP 两种，与在册治理词表不兼容。存证＝渲染全文 `.runtime/tmp/st-datalane2-20261012/translation_render_with_foreign.pkl`（实为渲染 YAML 文本，3,589,492 字节；行号 22764/38677/38825/39403/40056/48962）。本班**不清这六行**：写侧在 PG 生产账本、清理须"经确证后走正道"（统筹原话），且与 CH 侧污染同族宜并案治理。
  另 3 条未落地条目（cband_grid／statsgov_deflation_and_budget／build_distilled_sft_dataset）看着是**真件在飞**，本班同样不代带——代带＝归属篡改（在册 `queue-attribution-when-hot-registry-dirty`）。

### 5. 本班收工态（三清单之"未做与在飞"，如实不签收工）

- 在飞袋四态：`q-…-0003` done（landed 86da0f4248，账本 §十九-卅二）、`q-…-0006` pending（新件六件套：回填器＋7 钉测试＋.gitignore 两行豁免＋三本生成册的本班条目）、`q-…-0001/0002/0004` dead（死因与对症均已落档）。
- 本班不 merge 车道：主区此刻有他会话在途件（在册铁律"主区有他人在途件时 merge 整条路禁用"），全部作品走队列正门。
- 待下一班的三件实事（本班不做也不代裁）：①08:05 任务的结果回收（看 `retry_log/scheduled.out` 与 `retry_marker.json` 的 `scale_result`；若 rc=22＝探针不通，按 marker 时刻顺延 ≥6h 再探一次，勿改判据）；②若 Owner 批件①②③④，落地后必须同批改 docstring 并重跑 `tests/legacy_zephyr/data/test_providers.py` 三支；③`\ZEPHYR-DATALANE2-SEG2-RETRY` 跑完即删（作废命令在 : 上文），夜跑任务已复原（`tilib_indicator_backfill_nightly` NextRunTime＝2026-10-14 02:30 实测，恢复助手已注销）。
- 未闭面照旧如实挂着：2016 及更早的 basic 仍缺；2017-2018 的周月线/后复权表族未跟（是否跟由源件落地时定）；tilib 跑器的"静默空转红退出"与"跨午夜窗新鲜度"根治仍未落（在册缺陷 §廿三 第 3、4 条）。

## 卅五、新件落不了地的通道死因（本班实测 13 行账本-投影差，呈册主车道；当班处置＝摘件分袋，不陪葬）

袋 `q-20261013-st-datalane2-20261012-0006`（在册化六件套）03:1x 落地失败，死因原文＝
`网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: … 无 plain_zh 简介[scripts/data/backfill_kline_daily_history.py]`。
**这条处方的前提是"投影册＝真源"，而该前提 10-04 已废**（同病灶 10-10/10-12 两班各撞过一次，本班是第三次，处方在册已写明"整条链只认 YAML 投影，预检与落地都会死"）。

- 三读对质（本班 03:2x 实测，全部只读）：
  - **PG 账本＝有本班那行且内容合格**：`registry_ledger.fetch_entry('REG-MODULE-TRANSLATION-001','entries','module_path=scripts/data/backfill_kline_daily_history.py')` 回 `entry_pk=89862`，payload 含 name_zh=A股日K线历史窗口回填器／plain_zh 全文／domain_id=D_DATA／responsibility_layer=business；`add_module_translation.py --dry-run` 同口径回"noop（账本已到位）"。⇒ 登记动作本身早已成功，不是本班漏跑意图 API。
  - **门实际读的源＝YAML 投影**：`module_translation_loader.get_module_translation(该路径)` 回 `None`；该 loader 无 PG 通道（门文件头 :32 自称"真源=PG registry_ledger"，实现却只读 YAML——**门的文档与实现分家**）。
  - **投影册两处皆落后**：主区盘面与 HEAD 的 `module_translation_registry.yaml` 均 68,214 行、对本班路径 grep 命中 0。⇒ 本班袋内手插的那 5 行投影字节**根本不参与物化**（10-09/10 单源写战役后"袋内字节退出物化"），带上它反而会让落地内容变成**整册 render**（含他人未落地行）＝归属篡改，故本班主动不带这本册。
- 差集实测（**正确分母＝ entries 族**；第一次本班误把全 registry 的 active 8,612 拿来减投影 8,105 得 507，其中 494 行是 `algo_submodules`/`battle_map_*` 等**别的族**的键，不在这本册的渲染面——已作废重算，教训同"覆盖尺分母"族）：
  - entries 族 active **8,118**；投影 **8,105**；`账本有而投影无 = 13`；`投影有而账本无（retired 却仍在册）= 0`。
  - 13 行点名（谁的一行一目了然，代带＝归属篡改，本班一行都不带）：
    本班 1 行＝`scripts/data/backfill_kline_daily_history.py`；
    他车道在飞真件 6 行＝`scripts/audit/agg8_series_materialize.py`、`scripts/audit/ti_daily_mean_materialize.py`、`tests/gov/audit/test_ti_daily_mean_materialize.py`、`scripts/backtest/fexam/cband_grid.py`、`scripts/backtest/statsgov_deflation_and_budget.py`、`scripts/ml/build_distilled_sft_dataset.py`；
    雷三夹具样名 6 行＝`src/zephyr/{degraded,layered,lying,new_mod,orphan,with_extras}.py`——**新做确证升级**：这 6 行在账本里是 `status='active'`（不是 retired），而盘面与 `git ls-files` 双双查无该路径 ⇒ 任何一次 render 袋都会把 6 行测试垃圾**首次推进 HEAD**。这就是为什么"顺手 render 一下"现在不能做：**先定性这 6 行，再谈 render**，顺序不能反。
- 两条正道（供统筹／册主车道择一，本班不自裁也不绕）：
  - 路一（Owner 在册固定正解＝改"喂给闸的输入指向"，不弱化门、不白名单、不加豁免）：维护四班先按意图 API `retire` 那 6 条夹具行（带名目），再由册主车道出一次 render 袋落地——那时净增＝7 行（本班 1 ＋他车道 6），投影与账本对齐，此后所有新 .py 不再撞这堵墙。
    **执行细节别踩空（在册实测）**：`api.retire(registry_id, family_key, entry_key, authority_ref=…, reason=…, session_id=…)` 的 `authority_ref` 为空会机械拒 `AUTHORITY_REQUIRED`，而**禁编造裁定号**（在册事故线：为达标伪造 Owner 署名）。可用Authority 面＝统筹 2026-10-13 四裁原话"PG 翻译账本测试写穿残留＝急件转维护四班……那 6 条行经确证后走正道清理"（引通道原话而非编号，正是该 API 的缺省要求）。entry_key 形态＝翻译族 `module_path=<路径>`、token 族 `file=<路径>|token=<token>`；`status` 只到 `retired`（墓碑制，行永不物理删）。
  - 路二（半治，先例在册）：给 `translation_coverage_gate`／loader 加 **PG 第三源**，与 10-10 CREATE-GUARD 那次同款（同一病灶至今半治半漏）。代价＝动门本体代码，属治理码改动；收益＝不依赖投影新鲜度。
- 当班处置（照在册处方"新 .py 摘出、其余件另袋先落、实测数与通道缺陷成册呈批"执行）：
  - 修尺袋（裁④批准的执行件）已摘出本袋单投：`scripts/data/audit_technical_indicator_coverage.py`＋它的守卫测试＋`.gitignore` 两条豁免。该袋不含 `src/zephyr/`、`scripts/` 下新增 .py（守卫测试在 `tests/` 下＝门的范围外），故不撞这堵墙。
  - 被摘出的件与它的守卫测试留在盘：`scripts/data/backfill_kline_daily_history.py`（sha256 前 16=c3fedb957c36d66d）＋`tests/data/data/data/test_backfill_kline_daily_history_window.py`（7 钉，03:2x 与修尺测试合跑 **11 passed**，PYTHONPATH 指车道避免"车道跑主区包"的假绿）＋token/manifest 投影行。投影一旦对齐即复投，件面不必重做。
  - 运行面已先行：08:05 的一次性重试任务读的是**车道副本**（`pick_script()` 主树优先、缺则退车道并同换 PYTHONPATH），所以 §卅四 的 590 只重试不欠这本册的账——数据面与在册面在这里是分开的两件事，本班不把"在册化没落地"写成"回填没跑成"，也不反过来。
- 本班不做的事（写明免误读）：不代带 13 行中的任何他人行；不为本件加 .gitignore 之外的豁免旗；不改 `add_module_translation.py`／门的判据或阈值；不"先 render 再说"。

## 卅六、路一①已执行（统筹 2026-10-13 批复"路一批①"）：夹具 6 行退役回执＋差集收敛到 7

裁定原文照抄执行面＝"路一批：①先 retire 那 6 条夹具行——authority_ref 用我这句话的原文（"那 6 条行经确证后走正道清理"，统筹署名，禁编裁定号）；②册主出 render 袋（净增 7 行）；③你的在册六件套随之解堵复投"。本班只做①（②明确归册主车道，③要等②落地才成立），并记下为什么①不落给维护班：确证是本班做的、授权是本班的原话、且本班就是被堵的那一方；路二（给门加 PG 第三源）本班一行代码未动，统筹已转维护接任班与 P3 同族收口。

- 执行序＝**先撤 1 条读回校准，再撤余下 5 条**（Owner 在册令"首件校准再放量"，写库面同样适用）。
- 前态（撤前实测，逐行）：6 行全部 `status=active`、`version=1`、`created_by=add_module_translation`（CLI 缺省归因，非任何车道署名）、name_zh 分别＝降级模块/改名后/谎报模块/新模块/孤儿模块/写手更新；family 唯一命中 `entries`（族名试错：`module_translations`／`translations` 两族查无＝不存在，非本班漏族）。
- 后态（撤后读回，逐行）：6 行全部 `status=retired`、`version=2`、`updated_by=st-datalane2-20261012`，`created_by` 原样保留（墓碑制，行永不物理删）。
- 族计数对账（净零自证）：**撤前 active 8,118／retired 640 → 撤后 active 8,112／retired 646**，两侧之和恒 8,758＝行数零增减，只有状态位迁移。若这里出现"总数变了"就是物理删，本班立刻停手上报。
- 审计面（内容级，非存在级）：`registry_event` 六条 action=retire 全部落齐 `actor_session=st-datalane2-20261012 / base_version=1 / after_version=2 / authority_ref=统筹原话全文（含"禁编裁定号"那句，引通道原话而非编号）/ reason=双面查无的确证内容`。回执件与机读收据＝`.runtime/tmp/st-datalane2-20261012/retire_fixture_rows.py`＋`seg2/retire_receipts.json`＋`seg2/retire_run.out`（可复跑；复跑因 `status!=active` 会回 OK_NOOP，不产生第二次状态迁移）。
- 投影面零改动（这是刻意的，不是漏做）：loader 投影仍 **8,105** 行、`git show HEAD:` 面未动。本班不碰渲染——②才是 render 的动作，且归属册主。
- **给册主的现成数（收敛后的差集，正好 7 行，零垃圾）**：`scripts/data/backfill_kline_daily_history.py`（本班）、`scripts/audit/agg8_series_materialize.py`、`scripts/audit/ti_daily_mean_materialize.py`、`tests/gov/audit/test_ti_daily_mean_materialize.py`、`scripts/backtest/fexam/cband_grid.py`、`scripts/backtest/statsgov_deflation_and_budget.py`、`scripts/ml/build_distilled_sft_dataset.py`（后六条＝他车道在飞真件登记）。⇒ 现在任何一次 render 袋的净增＝这 7 行且**不再首次物化测试垃圾**；`账本有而投影无=7／投影有而账本无(幽灵行)=0` 两个方向都清了。
- 一处踩空实录（别当成"写库失败"）：首次执行在 import 期即 `ModuleNotFoundError: No module named 'schemas.categories'`——`python <按路径跑脚本>` 时 sys.path[0]=脚本目录，`schemas` 不在面；**零行被改**（失败发生在任何写之前）。补 `PYTHONPATH=<仓根>;<仓根>/src` 后一次通过。与在册"车道裸 python 导主区包"是同族坑的反面形态（那次是导错面，这次是导不上面）。
- 复投前置（③的判据，写给接手而非靠记忆）：`lag==0` 或至少 `scripts/data/backfill_kline_daily_history.py ∈ 投影面`（复核：`python -c "import sys;sys.path.insert(0,'scripts/governance');from _shared.module_translation_loader import get_module_translation as g;print(g('scripts/data/backfill_kline_daily_history.py'))"` 回非 None 即解堵）；届时车道内件面不必重做（sha256 前 16=c3fedb957c36d66d 的双存证仍在）。
- 待裁面照旧：③写侧来源标签四件改动仍等 Owner 亲裁（统筹已表推荐"批"，但 human_only 门位不代拆）；10-13 收盘后那条可翻案预测的 SQL 复核留给晨班。
- 在飞袋的锁面观察（只报现象不代裁根因）：03:20 本班为袋 0007 的 4 件逐一 `lock_files.py acquire`（每条回执都写 TTL 30 分钟，`list` 当场可见），03:28 复查同四件＝**在册零条**，而袋仍 pending（ahead=6）。两个候选解释本班在这一窗内分辨不了：①他会话冷启动跑了 `lock_files.py cleanup` 扫走（但该命令按在册语义只清**过期**条，8 分钟不该到期）；②入队侧 finally 释放了本会话这些件的 claim。这与在册铁律"袋在飞禁放锁"是同一风险的**被动失守形态**——不是主动放锁，而是放了会自己不见。下一班若靠 claim 判"这文件有人在改"，请先 `list` 复核再动手，别按自己上一次 acquire 的回执推断现在仍持有。本班处置＝03:29 重新 acquire 四件（已核 4/4 在册），时间线如实留：03:20 可见 → 03:28 零条 → 03:29 重投可见。
- 同一把尺的第二次读数（把上面那条观察收窄，别让它停在"两个候选解释"）：03:29 重投的账本 claim，其后本班再 acquire 时机械回 `RECLAIMED — 原 st-datalane2-20261012 的过期 claim 已回收（expired，静默窗 30min）`，**而距那次 acquire 只有约 9-10 分钟**（03:29 与 03:39:25 两个 `date` 实测点之间两次 acquire 皆回此讯）＜它自己打印的 30 分钟 TTL。⇒ 除候选①②外还有第三种更可能的：**TTL 的起算点不是本会话这次 acquire 的时刻**（回执打印"剩余 30.0m"，但时钟可能按该文件首次被锁/上一次登记的时刻起算）。本班不据此改任何锁面代码——这是观测面，不是判据面。给下一班的口径因此升级成硬一句：**别把 acquire 回执当"我现在持有"的凭据，动手前 `lock_files.py list` 现读，落袋前后各读一次**。
  （自我更正一条，按体例当场标注：这段先前草稿写的是"21 分钟／03:5x"，那是本班体感钟又偏快造成的——在册自犯条目"体感钟快约一倍、动作前先 date 实测"同族第三次现场；以 03:39:25 的 `date` 实测为准改写作 9-10 分钟。另防误读一句：本 §卅六 上面那句"③写侧来源标签四件改动仍等 Owner 亲裁"是当时点状态，Owner 已裁「批四处随形改」且本班已落码，见 §卅七——按"更正另起、留旧案卷"体例不回删旧句，只加指针。袋讯若与本行数字不一致，以本行为准。）

## 卅七、③写侧来源标签随形改已落码（Owner 亲裁放行 human_only）＋④幂等清账的触发条件

Owner 裁定原文＝**「批四处随形改」**；authority_ref＝Owner 原话"现在就全部干，全部批，投"（2026-10-13）；回退＝revert 单袋（`q-20261013-st-datalane2-20261012-0013`）。§卅四 栏一那张清单从此不再是"待裁"，而是"已落码待 drain"。

- own-diff 实测 **+10/-5，三件**，四处站点逐条与清单对得上，除这四处零夹带：
  ①`market_stock_daily_basic.py:69` INSERT_COLUMNS 末位加 `data_source`（连同上一行注释一起改准：原文"排除 DEFAULT 列由 CH 自动填充"在改后就是假声明——**改码不改文＝码与文分家**，这条自约束本班自守）；
  ②`tushare_provider.py` 列清单加 `"data_source"` ＋ 行元组末尾加 `"tushare"` ＋ docstring 三处同批（6 列→7 列、"走表 DEFAULT"→"显式带 'tushare' 随形落"、并写下此前 DEFAULT 兜底致全表来源错标这一因）；
  ③`test_providers.py:2173` 断言补第 7 项 `"tushare"`。
- "两处必不改"这次是**跑出来的不是推出来的**：`:2180-2185` 是 `set(provider)==set(schema)` 两侧对拍，同步加列自动跟上；`test_fetch_route_per_trade_date` 断言的是**请求侧** `fields="ts_code,turnover_rate,float_share,circ_mv,total_mv"`——data_source 是我们补的常量列而非 tushare 回列，请求面一字未动，跑过即证。
- 消费面扫法与结论（防"第五处随形点"漏改）：`INSERT_COLUMNS`／`_STOCK_DAILY_BASIC_COLUMNS` 全仓引用面＝定义处＋该测试两处，无运行时第三方；其余读本表者（chips 族、`t0_state_match_matrix`、`chip_distribution_engine`、`internal_compute_provider` 换手率并入）一律按**列名**取数，不依赖插入元组形状。
- CH 侧合法性实测（改前先验，别拿"表里有这列"当记忆）：`system.columns` 该表 `data_source`＝位置 7／`LowCardinality(String)`／带 DEFAULT ⇒ 显式插值合法；**DDL 文本一字未改**，文件头 INVARIANT"本文件 DDL 必须与 ClickHouse 实际表结构一致"仍成立。
- 红绿证：目标类 12 passed ＋ `test_providers.py` 整档 **132 passed**（车道面跑：`PYTHONNOUSERSITE=1`＋PYTHONPATH 指车道，并先打 `__file__` 自证不是主区码面——他班在册教训同族）；ruff 净（残留 4 条 noqa warning 在 `:269/:278/:326/:335`，非本袋行，本班不顺手修他人面）。
- 入袋一处程序性留痕：`commit_queue.py enqueue` 侧**没有** `--allow-multi-domain` 旗，预检按 COMMIT-SCOPE 判 2 域拦下；正解是队列自己的处方行（`commit_queue.py:3928`）写的"核实文件归属后用 `git_commit.py --allow-multi-domain`（留痕）重投"⇒ 本班改走 `git_commit.py --enqueue` 正门一次通过。这不是绕闸：码件＋它的守卫测试同批是宪法 §2 第 4 条明列的合法场景，旗也只在袋讯留痕。
- ④幂等清账**不随本袋盲跑**（按 RULE-DATA-OPS 先过必要性这一步）：现全表 `data_source='akshare'` 命中 **0** 行，此刻跑＝空扫 10,511,976 行。正确触发点＝**本袋已落地** 且 **日增量腿已写过一轮**；判据一条命令：
  `python -c "import sys;sys.path.insert(0,'scripts/backtest/fexam');from ch_data import ch_query;print(ch_query(\"SELECT count() FROM c1_market.stock_daily_basic WHERE data_source='akshare' FORMAT TSV\"))"`
  回 0 → ④是空转，不跑；回 >0（说明落地前那一日仍按 DEFAULT 落了错标行）→ 跑
  `ALTER TABLE c1_market.stock_daily_basic UPDATE data_source='tushare' WHERE data_source='akshare' SETTINGS mutations_sync=2`（幂等，同语句本班 10-12 已实跑一次，`is_done=1/parts_to_do=0` 在册）。
- §卅四 那条可翻案预测现在升级为**验收项**：10-13 收盘后日增量腿的新行应显 `tushare`。复核＝上一条命令加 `AND trade_date='2026-10-13'` 分组看 `data_source`。若本袋未能在收盘前 drain，预测面会先出现 akshare 行——那是**落地时序**不是判据错误，届时按 ④ 清账即可，别把它记成"改标没生效"。
