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

## 九、收尾清单（滚动）

- [ ] 53472 收官确认→T2 探针+冷档→T3/T4 放量
- [ ] T1 今晚 02:30 夜跑写入量对比（明晨读 state+当日入库行数）
- [ ] merge 本班分支回 dev；release 全部 claim；99_delivery 逐件哈希+复核命令
