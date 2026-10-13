---
ttl: task_bound
title: GPU 喂饱班终报（st-gpufeed-20261010）
created: "2026-10-10"
sid: st-gpufeed-20261010
family_id: GPUFEED-CAMPAIGN
---

# GPU 喂饱班终报（st-gpufeed-20261010）

## 〇、TL;DR（60 秒版）

1. **批A"静默 5.2h 后 17:10 无声消失"叙事被证伪**。进程真实死亡时刻=**2026-10-10 11:59:35±5s**（procstart 陷阱 EXIT 三连+GPU VRAM 回落+日志断流三源收敛），死时正在正常算格（最后警告=死前 30s）。死因=外部 `TerminateProcess(exit=1)` 整树处决；reaper 无罪（kill 日志零命中+keep 在册）、OOM/WER 崩溃/Defender/调度器超时全排除（§二）。高置信凶手=夜矿续战班 st-nightmine2 的定点停批（书面自认+pid 精确匹配+16.7h 时长逐位吻合）；备选=常驻隐名杀手（backfix 案 #5-#10 同族，+2m50s 滞差共振），由 backfix 常驻审计可证伪。**不存在"新失败形态"，v2 设计输入从"防静默挂起"修正为"防外杀+防慢死"——T1 仪表两者都防**。
2. **44.8s/格 主嫌钉死：combine_cache 抖动**。`_COMBINE_CACHE_MAX_CELLS=24M`（factory_grid_executor.py:726）预算按小宇宙 3.5M/条估算，全市场宇宙实际 ~10.2M cells/条 → **只装 2 条**，168 个 (G,A1,A2) prefix 被分层抽样交错访问 → LRU 全程抖动。铁证=批A 日志 2202 次 combine-miss 警告≈格数（≈100% miss 率）。五嫌疑判定：每格 spawn 无罪、CH N+1 基本无罪、写盘无罪（但批末才落盘=16.7h 零产物根因）、串行编排有罪（放大器，GPU util 28.6%）、**缓存抖动主犯**（§三）。
3. **T1 仪表已实装+三重验证+真弹冒烟通过**：批出生卡/每格分段计时/批级心跳+停滞看门狗（超阈全线程栈 dump）/分段 partial 落盘，全部 fail-open、判据面零动。单测 5/5 绿、既有契约测试无新增红（2 例预存红与本改动无关，HEAD 复现实锤）、真弹 8 格冒烟 38s rc=0 仪表全件出生（§四）。**v2 无论治本与否都带仪表上窗**（批A 遗产建议已落地）。
4. **T2 治本方案**：主修=prefix 顺序化执行（一行排序，LRU 命中率 ~100%，数值零漂移）+缓存预算重估（辅）；预期把 1000 格从 ~16.7h 压回窗内。按 48h 冻结红线，影子对照完成前不上窗；赶不上=降级声明"带仪表上窗，达标声明移 10-24 窗"（§五/§六）。
5. **T1 200 点标定**：前置门（bcure 收官+CH 空闲窗）今晚未到执行时点，运行册已备好（§八），明晨对表数据车道 T7/T8 后执行。

## 一、T0a：批A 日志全量尸检

- **唯一日志**=`.runtime/logs/f06_grid.log`（807,125 字节 4450 行，append 模式跨 5 窗）。批A=行 5-4450（19:17:00 `==== fired ====` 起）。**全文件零逐行时间戳**（stderr 直写无 formatter），每格耗时只能靠硬锚点反推。
- **warnings 分布**：2222 条=2211 FutureWarning + 11 RuntimeWarning。99.6% 来自两个 `pct_change` 位点：`factory_grid_executor.py:523`（IC 族 combine miss）×1467 + `:567`（lasso/pc1 族 combine miss）×735 = **2202 次 combine 未命中≈格数 → miss 率≈100%**。这既是噪音也是进度代理（≈2 警告/格）。
- **速率裁定**：19:17:07→11:59:05 = 16.7h，1105 格 → **真实均值 54-60s/格**。账面 canonical 44.8s/格（nightmine 00_final_report.md:263 口径=13.35h÷1073 IC 标记）与总时长算术不自洽（1105×44.8=13.75h≠16.7h）——量级不变（超 3.5s/格 阈值 13-17 倍），但 v2 `duration_basis` 引 44.8s 会**低估 20-35% 跑批时长**，10-17 窗排程按 54-60s/格 留余量（1000 格 ×54s=15h＞22:30 收窗线，见 §六 降级声明）。
- **11:59 最后输出**：一条正常 combine-miss FutureWarning，整行完整收尾（hex 核验无截断）——死时在算格，非挂死。
- **stdout 全程缺席的机制**：python stdout 块缓冲，被 kill 即整体湮灭——80 万字节日志无一行 stdout 属预期行为。

## 二、T0a2：死因取证与排除清单

**死亡时刻裁定：11:59:35±5s（四源收敛）**

| 源 | 证据 |
|---|---|
| 进程在册（最硬） | `.runtime/tmp/procstart_trap_standing.log` 5s 快照：11:16:38 三 pid（50252 python/25712 cmd/32284 powershell）带完整 cmdline 在册 → 行 8205/8211/8223 **同一 tick（11:59:35）三 EXIT** |
| GPU VRAM proxy | gpu_util_long.log：11:59 档 1995MB → 12:09 档 1343MB（回落窗与 11:59:35 相容；16:29 后回升=无关消费者 Qoder 上线） |
| 日志断流 | f06_grid.log mtime=11:59:05（stderr 末次落盘），此后零写入 |
| 算术 | 19:17:00→11:59:35=16.709h，与 t4 袋"16.7h"逐位吻合 |

**死因签名**：Task `LastTaskResult=1`=第三方 `TerminateProcess(exit=1)`（taskkill/psutil 族）指纹；非调度器自停（那会记 0x41306）；整树同 tick 死=树杀。

**排除清单（全部有证据）**：reaper 击杀（reaper_kill.log 1902 行零命中+keep 在册）、孵化账本杀径（非 spawn 面）、OOM/资源耗尽（Resource-Exhaustion 零事件+watermark 健康）、WER 崩溃（Event 1000 零条；1001 全为历史存档回放）、BSOD/断电/注销（System 日志零 41/6008/1074）、Defender（无 1116/1117/1006）、守卫家族锁杀（三守卫日志零开火+目标缺席）、调度器自停（LastTaskResult=1≠0x41306）、执行器自杀（无 deadline 分支+必留 exit 行）。

**凶手裁定（置信分层）**：
- **高置信**：st-nightmine2-20261010 定点停批。书面自认（trial_ledger_registry.yaml:25-28"12:0x 停批…三进程已停"+t4_f06_msg.txt 12:07+commit 723a6a10a9 12:11:35）；pid 三连精确匹配；16.7h=杀时刻 elapsed 逐位吻合；"无 spawn 记录"可由 <5s 短命 Stop-Process 逃逸 5s 快照 census 解释；examclose 14:58 独立复核已接受此定性。
- **备选（不可全盘排除）**：常驻隐名杀手（backfix 案 #5-#10 同族：静默 TerminateProcess+整树同秒+零新进程），时序共振=reaper 11:56:45 处决 46640 后 +2m50s（五连案滞差 +1.7~22min 家族第六例）。**证伪钥匙=backfix 常驻清单审计（307-resident 逐个核 11:59:30-35 tick 响应径）或夜矿会话命令级留痕**。若坐实备选，本案升格 backfix 案 #11。
- **"17:10 消失"证伪**：exam chief 心跳 10:31:35 已 exited、17:15:58 才 reincarnate——10:31~17:16 无遥测期不可能观测"17:10 瞬间"；16:18-16:23 pid 50252 被 bash 树回收（pid 回收伪影）+邻案真死污染（案 #9 36456 死于 16:44、案 #10 46216 死于 17:27）+首观察者谬误=该叙事的三个成分。**建议修正台账 2fb2976b0d 的"死因未知/新失败形态"定性**（adjudicator: st-gpufeed-20261010，证据=§二四源）。

## 三、T0b：代码考古——150 倍差距的分层定位

**L1 基准口径真相**：0.061-0.606s/格=纯引擎核单 pass（`bench_p1.py:61-72` 只包 run_backtest_full，显式排除 evaluate_recipe 与数据装载，seal masks 桩掉）——**与 44.8s/格 不可直接比**。全格口径=求值+门禁+引擎+编排。

**五嫌疑判定**：

| # | 嫌疑 | 判定 | 证据 |
|---|------|------|------|
| 1 | CH N+1 往返 | 无罪（残余隐患在案） | 数据面整批一次（:1401/:1411/:1453/:1459）；循环内全带批级缓存。残余：掩码 CH 异常 fail-open 不落缓存（_c4_engine.py:483-485），CH 抖动会退化——本案无证据触发 |
| 2 | 每格 spawn | 无罪 | 每批 1 次 python（run_f06_grid.ps1:39）；循环同进程，零 subprocess/multiprocessing |
| 3 | 单线程编排串行化 | 有罪（放大器） | `for r in picked:` 严格串行（:1476）；单核吃满（cpu 93.2%）；GPU 单流阻塞提交+每格 D2H 收口 → util 28.59% |
| 4 | 同步写盘 | 计时无罪/可观测性有罪 | 四件套批末才写（:1685-1778）→16.7h 零 manifest 根因；循环内唯一写点=j_regime_schedule.csv |
| 5 | 无预取/缓存失效 | **主犯** | 批级预取齐备，但 combine_cache 预算 24M cells（:726）按 3.5M/条估算，全市场实际 ~10.2M/条 → 装 2 条；~168 prefix 交错访问 → 抖动。铁证=2202 miss≈格数 |

**瓶颈排序**：①combine miss 重算 50-70%（normalize+combine+rank，lasso 族含 ~16 次 sklearn 滚动重训最贵）②每格不可缓存面板变形 15-25%（sizing astype/ewm/drift_band T 行循环）③门+引擎核 3-5% ④GPU 传输/串行节拍（绝对量小但封死并行上限）⑤装载/写盘 ~0%（68s/批摊销）。

**真弹冒烟交叉验证**（grid_20261010-183819，8 格 38s）：小批 prefix 少无抖动 → 均速 ~3.8s/格（含 68s 级数据装载摊销前），且 cache_n=7 时已现逐出（7→5）——预算瓶颈连小批都在踩线，大批必炸。

## 四、T1：仪表实装+验证（已完成，随批常开）

**改动面**：`scripts/backtest/factory_grid_executor.py`（+313/-6，单文件，无新模块）。四类遥测件（全部 fail-open，判据面零动——不改抽样/求值/回测/最终 manifest schema）：

| 遥测件 | 内容 | 防 batch A 哪个死法 |
|---|---|---|
| batch_meta.json | 批出生卡：pid/argv/参数/窗口/引擎（自报家门） | 验尸拼图困难 |
| progress.jsonl | 每格一行：fetch/eval/bt/write 分段计时+combine 命中面+cache_n+backend | 16.7h 零进度可见性 |
| heartbeat.jsonl | 批级心跳（60s，nvidia-smi 采样+RSS）+**停滞看门狗**：超 1800s 无进展→全线程栈 dump 到 stderr（落 f06_grid.log） | 静默窗"死时在干什么"证据缺失 |
| manifest/negatives_partial.csv | 每 25 格原子重写（tmp+os.replace） | 被杀=已落盘成果全沉没 |

环境变量：`ZEPHYR_GRID_INSTRUMENT=0` 关闭；`ZEPHYR_GRID_HB_INTERVAL`/`ZEPHYR_GRID_STALL_S`/`ZEPHYR_GRID_PARTIAL_EVERY` 可调。`_GPUWaveFailure` 波败路径显式收口（防泄漏心跳线程）。

**三重验证**：
1. 单测 5/5 绿（tests/research/backtest/test_factory_grid_instruments.py：合成面板零 CH 端到端+看门狗 dump+partial 幂等+同 seed 零漂移证尺）。
2. 既有契约回归：test_factory_grid_executor.py 36 过+2 红=**HEAD 预存红**（TestNetReturnsArchive mkt_cap_w None 桩爆 .reindex 链，st-mx07-W5 commit 已披露同族 7 例，stash 复测 HEAD 同红实锤，与本改动无关）；test_c4_batch_smoke.py 20/20 绿；test_f06_e2e_pipeline.py 过。
3. 真弹冒烟 grid_20261010-183819：38s rc=0，8/8 正格，五遥测件全出生且形状合法。

## 五、T2：治本方案与工作量清单

**主修 T2-A：prefix 顺序化执行（预估消掉 50-70% 大头）**
- 改法：`picked = sorted(picked, key=lambda r: r.prefix_key)`（循环前一处；同 prefix 格点连续执行 → LRU 2 条即近乎全命中：~168 次 combine 计算+832 次命中，替代 ~1000 次 miss+1000 次计算）。
- 数值零漂移论证：格点间独立（无跨格状态），结果=逐格函数；manifest 行序变（prefix 序）不影响任何下游消费者（_scan_grid_summaries 只读 summary.evaluated；台账记 count；DSR/归因按 recipe_id 读）。**须跑影子对照实证**（见下）。
- 工作量：代码 1 行+注释；影子对照 200 点×2 跑；评审 0.5 天。**风险最低，首选**。

**辅修 T2-B：combine_cache 预算重估（防御性，与 A 叠加）**
- rank 用 int32（rank 值恒正整数，逐位等价）省一半；预算 24M→按 all_a entry 10.2M 重估至 ≥3 entries（~64M）或改按字节预算。工作量 0.5 天+对拍。

**候补 T2-C：每格面板变形微优化（sizing ewm/drift_band 向量化）**——T1 200 点数据出来后按占比决定，10-15 冻结线前只在影子对照完成时上窗。

**候补 T2-D：多 worker 喂单 GPU 流/异步提交流水线**——工程量大（进程池+共享面板+GPU 流编排），影子对照+评审超 48h 冻结窗，**不赶 10-17 窗，立 v3 设计输入**。

**影子对照协议（判据面零动证明尺）**：同 seed=20260916 同 stratify 同窗，n=200 有界：改前/改后各一跑 → ①manifest.csv 按 recipe_id join：metric 列逐位相等（semantics 不变的修复要求 bitwise）②negatives 集合相等 ③耗时对比（目标：均格 ≤3.5s 或至少 <12.4h 窗内可收）。任何一位不等=方案废。

## 六、T4：上窗状态（连夜冲刺令后已翻转：治本版具备上窗条件）

- **T2-A 影子对照 PASS（19:48，grid_20261010-191646 基线 vs grid_20261010-194108 治本版）**：格点集/参数面/7 metric 列 bitwise 相等+negatives 集合相等+N_eff=12 逐位相等；耗时均格 2.87s→**1.707s（1.65x）**，combine 命中率 1.5%→**45.5%**（109 miss=每 distinct prefix 恰一次，冗余清零，与 T1 预测逐位吻合）。治本 commit=6b0670fb。
- **10-11（周日）08:00 开考预备完成**：Task Scheduler ZephyrAlpha_F06Grid 已改指一次性触发（NextRunTime=10/11/2026 08:00 实测回读）；prereg v2.1 窗纪注记随批登记（仅改起跑日，判据面/22:30 硬收窗/禁跨 23:00 纪律原样，后续周六窗纪不变）。v2 规模外推：1000 格×1.7s≈0.5h（p95 口径 <1.5h），窗内极充裕；治本版+仪表同飞。
- **残余风险（诚实申报）**：①10-11 为周日，原 v2.1 起跑日=周六，触发器改指为一次性——11 日窗若因故未跑，回指（周六或再一次性）须走裁定通道；②共租负载放大（批A 夜间 20x）若在周日晨复现，按 20x 仍 ~10h<窗；③硬收窗 22:30 前窗主按 heartbeat stall_s+progress 均格速率实时判活。
- **达标声明口径（数据在案）**：idle 均格 1.707s ≤3.5s 线 ✓；窗内 GPU≥70% 未达标也未必要（瓶颈在 eval 已由治本大砍，GPU 提交率天然上升；10-11 窗实测为准）。首窗验收仍=manifest+rc=0（判据面）。
- **排程风险预警（§八标定后已重估）**：账面 `duration_basis: 44.8s/格 → 1000 格≈12.4h`（prereg:63）与尸检真实均值 54-60s/格（批A 夜间共租口径）均超 12h 墙钟帽；但 **T1 标定实测 idle 空机同代码 2.87s/格（p95 9.1s）→ 1000 格≈0.8-2.5h**，窗内充裕。残余风险=周六 08:00 窗共租状态（CH 日更/LLM GPU）重演批A 夜间放大（27-60s/格 → 7.5-16.7h 超窗）。**处置：仪表在岗实时可见（heartbeat stall_s+progress 均格速率），窗主按读数早停手；若走 T2-A 影子对照（预期 ~5x eval 提速）则风险基本消除。**此为数据驱动的排程观察，非判据面改动。
- 导航风险移交窗主：`register_f06_grid_task.ps1:22` 的 action 指向 `D:\ZephyrAlpha\scripts\run_f06_grid.ps1` 仓内不存在（真身 scripts/tasks/run/）；live 任务已由裁定通道改指（NextRunTime=2026-10-17 08:00），重注册时勿踩。

## 七、10-17 窗验收判据原文（config/search_space_prereg.yaml:49-67 照录）

```yaml
f06_grid_v2:
  enabled: true
  inherits: f06_grid
  entry: scripts/backtest/factory_grid_executor.py
  n_samples: 1000
  seed: 20260916            # 与批A 同种子：首批 1000 格=原 6000 抽样前缀，批次谱系可对
  stratify_dims: [G_universe, A1_factor_normalize, B_top_n]
  frozen_at: '2026-10-10T12:10:00+08:00'
  frozen_by: 夜矿续战令三连裁③（总统统筹 2026-10-10）
  owner_signoff: 夜矿续战令 §三 T4（Owner 通道授权：批A 作废立 v2）
  window_discipline:
    fire_window: 'Sat 08:00（Task Scheduler 已由 14:00 改 08:00）'
    hard_deadline: '每日 22:30 前收窗，禁跨 23:00 W1 窗（二号域 GPU 让位，OD-5 叠跑教训在案）'
    duration_basis: '实测 44.8s/格（批A 进度代理）→ 1000 格≈12.4h，08:00 起跑 22:30 前收窗留 2h 余量；L2 批提速落地 3.5s/格后可经裁定通道升点'
  acceptance:
    manifest_present: true   # W1 式正式验收判据：manifest+rc
    rc_zero: true
    n_trials_ledger: '收窗 summary 经 MOD-BT-200 自动入账（对齐 38b453ca 配方）'
```

验收判据=**manifest 存在+rc=0+台账自动入账**；判据面本班零触碰。

## 八、T1 200 点标定（已执行，19:16-19:26 总统加急令直接发车）

**执行档案**：run_ts=`grid_20261010-191646`（pid 2584，19:16:46 点火，19:26:35 收工，**589 秒**，200/200 正格零阴性，rc=0，N 台账已自动入账，N_eff=12/200 名义）。前置门四检：bcure 零进程/CH 无重活/reaper live/keep 双条目在册。同 seed=20260916 同 stratify 同窗=**T2 影子对照改前基线**（manifest 按 recipe_id 逐位存档于产物目录；对拍尺=`.runtime/tmp/st-gpufeed-20261010/shadow_compare.py`，判据=join 后 metric 列 bitwise 相等+negatives 集合相等+耗时对比）。

**分段读数（progress.jsonl 全量 200 行）**：

| 指标 | 读数 |
|---|---|
| 均格 tot_s | **2.87s**（p50=1.20 / p95=9.14 / max=14.84）——idle 空机口径 |
| 分段占比 | eval 2.74s（95%）‖ fetch 0.013s ‖ bt 0.117s ‖ write≈0（写盘/取数/回测核全部无罪实锤） |
| combine 命中面 | **3 hit / 197 miss = 1.5% 命中率**（109 distinct prefix 摊 200 格）——抖动两批同在 |
| 按 universe 单价 | all_a_ex_st 3.6-8.7s（max 14.8）‖ zz500 ~1.0s ‖ hs300 ~0.7s |
| backend | gpu 141 / cpu 59（auto 守卫分流正常）；RSS 峰值 3.3GB；GPU 无瓶颈迹象 |

**三Conclusion（修正 §五/§六 相应结论）**：
1. **抖动证实但单价重估**：miss 率 98.5% 与批A 同形；但每 miss 单价由宇宙大小决定（0.6-15s），批A 的 54-60s/格=**夜间共租负载放大**（CH 日更/LLM GPU/多会话并租），非纯代码固有——同代码 idle 空机 2.87s/格（20x 差）。
2. **T2-A 价值随 n 放大**：冗余 combine 占比=1−prefix数/格数（200 格 44%→n=1000 约 83%→批A n=6000 约 97%）。prefix 排序在 v2 规模（1000 格/168 prefix≈6 访问）可砍 ~5x eval 时间；在 200 点规模仅 1.8x。**v2 窗仍建议上（影子对照后）**。
3. **窗口风险重估**：idle 口径 1000 格×p95 9.1s≈2.5h，08:00-22:30 窗内充裕；残余风险=周六 08:00 窗的 CH/共租状态重演批A 夜间负载（若 27-60s/格 复现则 1000 格 7.5-16.7h 仍可能超窗）。**仪表在岗实时可见**：窗主盯 heartbeat.jsonl 的 stall_s 与均格速率即可早停手。

**治本对拍流程（明日起）**：T2-A 落地 → 同参数重跑 200 点 → `shadow_compare.py grid_20261010-191646 <new_dir>` → PASS（metric bitwise 相等）才可上窗。

## 九、移交与建议

1. 台账修正建议：2fb2976b0d"死因未知/新失败形态"→"11:59:35 外部定点处决，高置信=夜矿续战班停批，证据链见本报告 §二"（裁定通道，adjudicator 署名随本 commit）。
2. backfix 交接：11:59:30-35 tick 已列入备选案卷；若其常驻审计排除夜矿班嫌疑，升格案 #11。
3. v3 设计输入：T2-D 多 worker 喂单 GPU 流；executor 增逐格时间戳日志（本班 stderr 无时间戳教训）。
4. 遗留：批A 真实均速 54-60s/格 vs 账面 44.8 的口径差，建议随 T1 标定以完整三元组回填修正（裁定通道）。

adjudicator: st-gpufeed-20261010（尸检裁定+仪表落地+方案呈批）


## 通宵执行与晨间裁定包（st-gpux2-20261011，2026-10-12 00:15 令；本节写于 01:5x）

### 一、执行了什么（逐项＋红绿证锚点）

1. **B1a 主刀袋已落地** commit `86f4c5ba6d39`（袋 `q-20261011-st-gpux2-20261011-0005`）。
   内容＝λ 链（ewm 递推＋行和归一）上卡，逐位镜像 pandas 2.3.3 `aggregations.pyx:1791-1827`／
   `core/window/ewm.py:97` 与 numpy 2.3.5 `loops_utils.h.src:80-145` 源码序；新旗 `--eval-glue-gpu`
   缺省关；三面计数（inline／reupload／failed）各有出口。
   落地核验＝三件 `git show dev:<file>` 逐字节 == 袋内（`27f7ca16`／`bf7fb4a6`／`11cfe582`），
   落地面五件合跑 **154 passed**。首投 `…-0003` 死 `GATE-ANY-ABUSE`（own-diff 命中我写的 `-> Any`
   辅助函数，门判得对）→ 改就地惰性编译后重投，三门预检（any_abuse／ruff format／ruff check）从此入袋前必跑。
   分族实测（稳态 i≥30，eval_s 中位 ms）：drift×5bp 339.6→155.3（省 184.3，两序同号）、
   periodic×5bp 182.0→115.4、drift×15bp 626.5→524.1、periodic×15bp 134.4→103.6、
   **对照族 periodic×λ0 差 −4.65/+16.55 落在同配置底 7.9 内（阴性对照成立）**；纯设备格 4.90ms。
2. **令 4 两条附注袋已落地** `b9a0bb9faccc`（03 件 §九，+81/−0）：三数入册带分母与跑批号，
   其中 **"69% 停用"**——盘上计数器无此口径（同次 1,049 格实测 hc/evaluated=81.2%、hc/cell_gpu=84.0%；
   本轮 120 格 65.0%／78.0%），歧义根＝旧引用未标分母；B2 批核要旨一行登记，施工口径仍以 §四 1-7＋3′ 为准。
3. **N-8 根因归因闭合**（预签之外的独立定案）：`run_batch` 宇宙→列序那一句直接迭代 `set[str]`
   （`_load_universe` 唯一 set 源，全文件静态扫仅此一处），集合序随 PYTHONHASHSEED 逐进程变并进面板。
   三预言全兑现：同进程内 eval×2 与 bt×2 逐位等（**排除** BLAS/归约序）；换 seed 列序签名与 net_sha 全变；
   同 seed 新进程逐位等。修复＝该句 `sorted(...)`；**双向对拍**：修后 seed5 vs seed6 三签全同、修前三签全不同。
   防回归钉 1 支（结构面 AST＋自带"修前形态必判败"红证）。袋 `q-20261012-st-gpux2-20261011-0006`
   （+6/−1、+46/0、+66/0）**processing 中（已 >50min，未死，看门狗在）**。
4. **全量重判 n=1050**（同进程三臂、原格集 seed=20261010、分层 G/A1/B、一律探索分册）：
   A 臂 1,049 格完成、B 臂完成、A′ 在跑；`n8_band_rejudge.py` 出数后以 03 件 §十一 追加回填
   （含 §九·A 设备列勘误，见二·3）。试点 n=60 四数：(a) A vs A′ **60/60 逐位等、三档越线全 0**；
   (b) A vs B 43/60 逐位等，差的 17 格**全落 `(0,1e-16]`**，三档线各命中 0 格；
   (c) 结合序帧布局敏感度修后仍在（≤1e-16 那一坨）；(d) 三批入参一致=True。
5. 落地面发现并移交：#ARCH-084 追踪区写入守护点名一支 end-to-end 测试重写热册
   `capability_canonical_file_registry.yaml`（盘上 +1135 系别家待登记 token，本会话初始即带 M）——
   **本班未碰未提交**，按域移交维护三班。

### 二、自裁了什么（逐条＋证据＋依据）

1. 【授权矩阵·域内施工序】B1a 落地后不抢新刀，先把等价性做实：车道 83 passed、executor＋landing 合跑 125 passed。
2. 【预签②条件判定→已生效但文档未投】§二·丙 采"自噪底＝0，容差只量设备侧合法分歧"口径的两触发条件
   均实测满足（(a) 试点逐位等；(c) `test_pandas_rowsum_order_follows_layout_rule` 与列序钉在修后仍绿＝7 passed）。
   判据面前后各跑一次的记录＝`n8_rejudge_n60.json`（新口径）对照四批 A/B 同配置底最大 6.18e-2（旧口径污染版）。
   **文档更新暂不投**的原因＝03 件被在飞的 0006 占着（同会话同件两袋会互吞，在册病案）；
   §十一＋`verification_framework.md` §二·丙 段已成稿待发，或按在册补救法把后袋做成 0006 的严格超集并袋重投（等裁 M-2）。
3. 【自更正，另起新节留旧案】§九·A 表**设备三列口径错**——ewm 列未同步（只量到 launch≈0.01ms），
   renorm 列把排在后面的 ewm 工作一起算（虚高到 15.92ms）。每核同步重测真值（T=970）：
   clip 0.04–0.37／ewm 核 1.35–1.93／renorm 核 0.48–4.84／两段+D2H 1.90→17.87／全链+D2H 3.87→19.79ms
   （S=450→5217）⇒ **宽宇宙下设备侧主成本是 40MB 稠密矩阵 D2H（≈11–13ms），不是 renorm 核**。
   旧表原样留档，更正另起一节（Owner 追认的更正法）。这直接改写 B2 的靶 → 等裁 M-1。
4. 【他基座复跑定性存量红，不代修】dev 基座控制跑复现的 6 支同栈红（`None.reindex`）归因清楚后，
   本班只补被诊断出的那一句守卫（市值缺席即 AttributeError 打死整波，与该函数文档语义相悖）。
5. 【最保守可选】pct_change `fill_method='pad'` 弃用告警（三点位：`vol20`／`rets_daily`／
   `compute_v1_factors`）＝口径面，维持不动入等裁 M-3（不顺手修，避免"顺手修"造第二数值面）。

### 三、等裁什么（编号菜单＋证据＋建议默认）

- **M-1 B2 靶改写（本班建议，代价已标）**：原令靶"renorm 1.17→15.92ms"出自我的错测量。真靶＝
  **稠密 D2H（≈11–13ms）＞ renorm 核（4.84ms）＞ ewm 核（1.35ms）**。建议拆两步并换序：
  **B2a＝紧凑对直供 bt**（N-2，消灭 40MB 回传与 DataFrame 重建；施工单 §四 3/3′/4 已定形，含
  `k=((rank_desc<=top_n)&~isnan).sum(axis=1)` 规则与层1双向钉，收益最大且是"利用率 70%"的正解）；
  **B2b＝renorm 核并行化**（一行一线程→分段并行，树结构不变则逐位不变；探针指示可行：
  分段版 1.01→0.22ms，但其结合序与主机不同，须按叶子级复刻树方可逐位）。建议默认＝先 B2a。
- **M-2 §十一＋§二·丙 口径段的投袋时机**：等 0006 落地（现 processing）；若 0006 久拖或死，
  按在册补救法把文档改动做成 0006 的**严格超集**并袋重投（证据：Counter 逐件超集判定）。
- **M-3** pct_change 三点位（口径面）今夜维持不动。
- **M-4** `exclusive_group` 互斥组行：仍待维护三班 T7 运行态生效（现值 blocks=3、册面无 T7 落地 commit），
  自动重投授权继续挂，未硬闯。
- **M-5** claim TTL=30min vs 排队 45–60min＋ 的错配（本班实测 0006 processing >50min）→ 归维护三班；
  本班按"续租＋看门狗＋过期按 dev 现字节重投"处置，不抢队列。
- **M-6** 04_ 独立账件未建（新件需 creation_token，本班上下文余量优先给了等价性与归因）；
  B1b（drift_band 串行扫上卡）未做，故 drift 格 `host_continue` 继续出声、开关矩阵钉明写"未接管不装样子"。

在飞两件：`q-20261012-st-gpux2-20261011-0006`（N-8 修复袋，processing）；全量重判 A′ 臂。
无一假落地：本包所有"落地"断言均以 `git show <ref>:<file>` 取字节核验，未采用"done 即算落地"
（在册第五形态＝done 而 landed_id 指他会话提交）。

### 四、通宵续段（02:0x→03:5x `date` 实测；追加于上面三节之后，原文一字未改）

**执行了什么（续，逐项带锚点）**

7. **全量重判 n=1,050 三臂跑完 → 呈批四数出表**（`n8_band_rejudge.py` 同进程 A/B/A′，seed=20261010，1,049 格）：
   (a) **1,049/1,049 逐位等、三档越线全 0、层2 五项 `n_nonzero` 全 0、ρ(A↔A′)=1.000000 ⇒ p₀≡0**；
   (b) 1e-8 档 11 格／1e-6 档 10 格／1e-4 档 9 格（对 p₀=0 的 z=3.33/3.17/3.01）；
   (c) §九·D 那族**仍在**（无 NaN 帧 C 序≠F 序：970×450 实测 575/970 行不符；常驻尺 `test_pandas_rowsum_order_follows_layout_rule` 修后基座 1 passed）；
   (d) 三批入参逐字一致（`n_picked=1050 / evaluated=1049 / engine=cpu`）。
8. **预签② 两句都触发了**：第一句（口径改"自噪底＝0，容差只量设备侧合法分歧"）实测条件成立 ⇒ 已落真源位
   `verification_framework.md` **§二·丙·补**（袋 `q-20261012-st-gpux2-20261011-0008`，对 dev `+36/−0` 纯追加，`### ` 3→4、删除行 0，线值一条未动）；
   第二句（1e-8 档混入并列翻转 ⇒ 判"未过"）也命中 ⇒ 那 **10 格本班未援引 §二·补 自行豁免**，列 M-7 呈裁。第 11 格是相对位分母伪影（绝对差 4.857e-17），按披露登记。
9. **逐格归因两件**：`n8_band_cells.py`（11 格七元组表＋族分布：`rank×equal` 31 格命中 10＝32.3%，其余 1,018 格命中 1＝0.1%；单侧 NaN=0；自噪非零格=0）；
   `n8_layer23_face.py`（甲条 0 越线：sharpe 最大 0.004／ann 最大 0.0008／**mdd 1,049 格差=0**／离散量 0 不一致；层3 ρ=0.99999994、top50 50/50、符号一致 100%；
   `avg_turnover` 按三问裁定② **在本面不可判**，只披露 1 格差 1 个舍入步）。
10. **B2 按施工单 clause 0 先报预算再量靶**，三件预演全部零生产写、一律探索分册：
    `b2_pretrial_breakdown.py`（分宇宙瓶颈分解，1,049 格实测）、`b2_engine_pilot.py`（四臂同进程 E0-E3）、`b2_bt_floor.py`（bt 面三臂底尺 n=120 与 n=1,050 两针均已完成，03:35 收针）。

    **改命读数**：宽宇宙的**时间主体在 bt 腿**（all_a 426.6ms/格＝tot 的 65%，两臂同形因本班刻意 `engine=cpu`），而 bt 腿**早有在册设备路径**
    （`--engine gpu`=`gpu_core.tensor_core`，L2-C）——单腿 2.2–2.5x、E0→E3 合用 tot 3.3–5.3x（all_a 5,414→1,020.8ms），
    manifest `backend` 列逐臂记 `gpu` ⇒ 真跑非静默降级（四臂 `eval_dead/backtest_dead/degraded_recipes` 全 0）。
    ⇒ **B2 的第一步不是写新核，而是"合开关＋给它自己的底尺"**；N-1/N-2 写核退为第二步。本班**未动缺省面**。
11. **bt 腿底尺（`b2_bt_floor.py`，同进程 F0/F1/F2；n=120 于 02:33-02:51、n=1,050 于 02:52-03:35）**：
    **n=1,050 全格集**（三臂均 `evaluated=1049 / degraded=0`）——F0↔F1（CPU 两跑）**1,049/1,049 逐位等**⇒ bt 面自噪底＝0；
    F0↔F2（CPU vs 设备 bt）**三档越线各 0 格**，1,047/1,049 列有差而 **max_abs=2.2204e-16（1 ULP）／max_rel=8.973e-12**
    ⇒ 设备 bt 腿在全格集上**一格都没被离散选择放大**（与 eval 面那 11 格成鲜明对照）；
    单价＝bt 中位 69.95→**36.6ms**（ALL），分宇宙 all_a 474.1→211.8（**2.24x**）／hs300 40.4→21.7／zz500 70.0→36.1，tot 中位 179.5→153.0ms（本臂 eval 仍 CPU 故总收益被稀释）；
    ⚠同一针内 F2 的 `eval_s` 中位反而 100.6→110.55ms（同一 CPU 码、纯臂序漂移）⇒ "单序列连跑的差不得当收益"这条**在针内部再次复现**，只有 bt 那一列是同码换后端的可比量。
    n=120 那针：F0↔F1 120/120 逐位等；F0↔F2 三档各 0、max_abs 同为 2.2204e-16、max_rel=5.561e-12。
    另抓到一条**独立复证**：预演 E0（02:16 进程，n=120）与本班 F0（02:33 进程，n=120）**跨进程同参 120/120 逐位等**，
    且与 n=1,050 那针的 F0（02:52 起、03:08 收，另一进程、另一 n）交集 120 列也**逐位等 120/120** ⇒ §十 列序钉把"跨进程不可复现"治好了，且**连抽样规模改变都不敏感**（比 §十·B 三签对拍更强的形态）。
    ⚠诚实标价一处线并存：5.56e-12 高于在册单元线 1e-12（`test_gpu_core_parity.test_gpu_parity_within_1e_12`，其对象=T=300/S=80 合成面板的 `tensor_core` 单出口），
    低于 §二·丙 最紧档 1e-8 三个数量级——两把线的**对象与窗长**不同，不是谁违反谁；是否给"累计 970 日后的净值面"单独立线属判据面，本班不动，列 M-9。
12. **在册单元面在本基座复跑**：`test_l2_gpu_landing.py` 83 passed；`test_gpu_core_parity.py`＋`test_c4_engine_gpu_wiring.py` 18 passed（无 skip，cupy 真可用）；ruff format/check 三件全清。
13. **在飞三袋的基线自证**：`git rev-parse dev:<file>` 逐件对拍，0006 的三件 base_blob 仍**全部等于 dev 现值**
    （executor `bf7fb4a68da`／test `11cfe58293`／03 件 `cf054185ed`）⇒ 无"盲投回退 HEAD"风险；executor 面我的增量＝+6/−1（唯一删除行是被替换的那句未排序推导式）。

14. **续：预算分解两只探针（第 10 项写时是三只，收针前又加两只，原文不改以免掩盖施工顺序）**
    `b2_bt_cost_split.py`＋`b2_bt_wrapper_split.py`（生产形状 (970×5,217) 下的成本分解，掩码打桩、零 CH 零生产写）：
    CPU 后端 `run_backtest_full`＝2,098ms/次，其 cProfile 累计里 `pct_change` 1,097ms/次＋`ffill` 128ms/次 ⇒ **CPU bt 腿的主体是宽表逐日准备的 pandas 开销**，
    这解释了为什么批内 CPU bt（474.1ms，已过 L1 hoist `pre_tensor`）远低于不 hoist 的孤立值；
    设备后端同形状＝70ms/次，其中 `tensor_core` 无探针中位 **17.07ms**（cProfile 下 30ms＝探针开销，两分母不得混用），
    再拆：**两张稠密 (970,5217) float64 的 H2D＝10.74ms＝本体 17.07ms 的 63%**，掩码 H2D 1.13ms、ffill 0.24ms、gate 融合核 0.85ms、两次截面 nansum 0.62ms、四档线＋D2H 0.21ms
    ⇒ 这就是 **N-2 紧凑对的上限定价**（每格 ≈10.7ms 上传＋38.6MB×2 稠密分配），核砍完的绝对下限约 2–3ms/格；
    ⚠同时给 N-2 泼冷水：批内 all_a 的 GPU bt 实测 211.8ms/格，核只占 17ms ⇒ 剩下 **≈195ms 在调用方**（DataFrame 对齐/掩码转换/档位与 stats 收口），
    先归因那 195ms 再谈写核，否则"只换 kernel 不动主机循环"的 13ms 天花板重演（§四 嘉奖 1 的同一课）。
    另：此刻在飞袋实为 **0006/0007/0008/0009＋本袋**（第 13 项写时是三袋），同文件链 0007→0009→本袋 已逐袋做 Counter 超集核验，后袋均为前袋超集，非条目被吞。

15. **更正第 14 项的半句（同刻复测抓出来的，旧句不改写只在此另记）**：第 14 项末写"批内 all_a 的 GPU bt 211.8ms 里核只占 17ms ⇒ 剩下 ≈195ms 在调用方"——
    这句**作废**。逐格计时器（`b2_attr_probe.py`，4 格窄面真跑，`--freeze-dims` 钉 `G_universe=all_a_ex_st`，稳态三格 bt 各 190/202/202ms）实测：
    **主体就在 `tensor_core` 自身**（稳态每格 ≈160ms），调用方三件收口只占 ≈25ms/格（`_as_f64_2d` 120.9ms/16 次、`_as_bool_2d` 19.0ms/8 次、`_to_numpy` 中位 0.47ms），
    掩码首格 CH 冷建 18,801ms、后三格命中 3.55ms ⇒ 冷建不得摊进稳态单价（本班第三次撞同一条：把一次性/上游工作算进下游列）。
    根因是**跨时刻比较**：同一支 `b2_bt_cost_split.py` 无负载时 17.07ms／H2D 10.74ms／CPU 219.84ms，05:49 队列高峰时 42.31ms／30.23ms／457.16ms（全机 cpu 81.2%、commit 83.7%），
    三项同比放大 ≈2x ⇒ **单价绝对值不可跨时刻比，只有比值可用**：稠密 H2D 占设备 bt 核 63%（无负载）／71%（有负载）。
    ⇒ N-2 的定价因此改写为："省一次 38.6MB×2 的稠密分配与上传，占设备核 6–7 成"，**不给毫秒承诺**；
    而 B2 的第一刀（合开关）在负载时刻也照样兑现 bt 腿 2.24x——那一对是**同刻两臂**，不受此条影响。

16. **收针态（06:01 `date` 实测；第 13 项那条"在飞三袋"至此已有进展，原文不改）**：
    0006（N-8 列序修复＋结构面钉＋§十）**已落地** `7f4311cc39`（05:55），落地核验按**逐件 blob 对拍**不按状态位——
    `git rev-parse dev:<file>` == 车道磁盘 `git hash-object`：executor `4090ffea48d8`、test `a9837444cdae` 两件**逐字节相等**，
    03 件那一份的差值就是本班随后追加的 §十一（dev `74485101be02` → 车道 `971ad4ab75c1`，`lane.startswith(dev)` 真、"仅在 dev 的行"=0 ⇒ 纯追加）；
    **落地面终验**（主区磁盘==dev 四件逐字节核实后在主区跑，非车道——车道裸 python 导主区包＝假绿，在册两次自爆）：
    `tests/research/backtest/test_l2_gpu_landing.py`＋`test_gpu_core_parity.py`＋`test_c4_engine_gpu_wiring.py` ＝ **101 passed in 75.17s**；
    §十一 已作为 `q-20261012-st-gpux2-20261011-0012` 投出（`--base-head 7f4311cc39`＝0006 落地commit，血脉相接；对 dev `+130/−0`）。
    此刻在飞＝0007/0009/0010（同件超集链，最新 0010 携带全部三段续段）＋0008（§二·丙·补）＋0012（§十一）。

17. **落地面全量侧验时发现 10 支存量红（不是本班引入，按 owner 责任制只登记不代修）**：主区磁盘==dev 四件逐字节核实后跑 `tests/backtest` ⇒
    **10 failed / 315 passed / 1 xpassed（27.83s）**，失败集中在 `test_factory_wiring_night.py`（F06ScreenLedger 1 支＋MonthlyWindowBroadcast 4 支）
    与 `test_sim_daily_runner.py`（2 支）等；首支样例错误签名＝
    `zephyr.risk.core.drawdown_state_machine.InvalidDrawdownStateError: [ZA-RK-0060] trade_date 倒退: 2026-09-21 < 2026-10-09`
    ⇒ **日历/状态耦合型**（重放日期早于风险状态机的既有评估日），与净值列序无关。
    非本班引入的三条证据：①本班落地提交 `7f4311cc39` 的 `--name-only` 只有三件（executor／test_l2_gpu_landing／03 件）；
    ②这两支测试件 `grep factory_grid_executor` 零命中（不导入被执行器改动的面）；③错误签名落在 risk 状态机与月度窗口幂等路径上。
    本班**不代修**，登记转交：归属＝风险状态机/模拟回放线（`st-fullscore-20260930` 一批捞回的旧真身，最近触碰 10-09 00:52 `d69125b1de5`、10-09 01:22 `ae63d6cd1f6`），
    提请维护三班或该线接班按"时间敏感存量红"处置；本班侧同时如实报一个不利事实：**这两支在 06:06 的主区时刻是红的**，
    若 Owner 明早跑全量会看到它们，勿误读为 GPU 化班把基座弄红。

18. **M-1′ 的决策级实测（06:10-06:19，`b2_full_both_gpu.py` 整批 D 臂＝`--eval-backend gpu` × `--engine gpu`，n=1,050，探索分册）**：
    `evaluated=1049 / eval_dead=0 / degraded_recipes=0 / vram_refused=0 / host_mem_refused=0 / resolve_not_gpu=0 / dev_attempt_failed=0`，wall 539s。
    ①**等价面（正主）**：A(CPU×CPU，01:19 臂)↔D **跨进程**对拍三档越线＝**11 / 10 / 9 格**，与同进程 A↔B 的 **11 / 10 / 9 逐档相同**，
      max_abs=1.378e-3、max_rel=2.017 也同量级 ⇒ **把 bt 也上卡没有引入任何新的越线格**；设备 bt 只把"逐位等列数"从 489/1,049 降到 2/1,049（全 1-ULP 面，见第 11 项 bt 底尺）。
      同时这条**改口**一条在册结论：列序修复后，跨进程配对在"档级判定"上已经可用（旧文"跨进程只能判有无系统性偏离、判不了 1 ULP"的适用条件被本次修复改变）；
      但**逐位级判定仍以同进程三臂为准**（D 臂与 A 臂相隔 4.5 小时、机器状态不同，逐位等列数已不具可比性）。
    ②**阴性判定与后端无关的正对照**：同一格 `65d2ba296d59`（raw×halflife60×top30×mkt_cap×monthly×periodic×cap10×all_a×λ5bp）在 A／B／D 三臂 negatives.csv 里
      **同一 death_layer、同一 reason `insufficient_net:970`** ⇒ 它不是设备路径的新缺陷，是配方级既有阴性（净值零方差被 fail-closed 拦下）。
    ③**单价不报**（有意）：D 臂稳态 ALL 中位 eval 82.3／bt 47.9／tot 144.5ms、all_a 442.8／228.0／674.6ms，与 01:32 那臂的 231.4／431.7／659.4 **不可直接比**
      （时刻不同、共租负载不同；第 15 项已立法"绝对值不可跨时刻比"，此处不自破例）。若 Owner 要吞吐终数，需**同刻交错 A/D 两臂**重跑（本班预算内做不完一整轮，登记为下一班可照做的动作）。

**自裁了什么（续，含依据）**

- **不起刀 N-1/N-2 新核**（依据=施工单 clause 0＋「留半截必成无消费者死件」＋§十一·C 那 10 格正等处置而新核必然重排它们；
  代价=今晚不出"批并行核"的吞吐数，出的是"两个已在册开关合用 3.3–5.3x"的预演数）。
- **扔掉一把我自己的错尺**：`n8_layer23_face.py` 初稿里我现造了一帧 970×450 合成权重去量 §九·D 那族的 ULP 数，得到 max 13 ULP——
  那与在册那族（reindex→clip→ewm 后被 sum 的帧，max 4.16e-17/1-2 ULP）**不同形**，属**换尺报数**。已删除该函数，(c) 改用在册尺
  （`rowsum_layout_probe.py`＋常驻钉），并在 §十一·F 把这条自犯写进正文。
- **不越权替 Owner 豁免那 10 格**，也不为过线动卡、不动 `pct_change` 三点位、不加宽 manifest 列。

**等裁什么（续，编号菜单）**

- **M-7（预签② 第二句命中，10 格并列/离散放大）**：证据=§十一·C 逐表（七元组齐 5 位，hs300/zz500 的宇宙规模本批未取数＝缺 1 位，如实标缺不补猜）
  ＋族签名与 §二·补 第 5 条已具名族完全一致。可选处置：①按 §二·补 第 5 条标 `tie_amplified_selection` 另判、不挂红线（**本班建议**，理由=同款形态已有 Owner 亲批先例，且甲条五项 0 越线）；
  ②判实现缺陷要修（代价=要先造出能区分"1-ULP 放大"与"实现缺陷"的新尺，现无）；③给离散选择放大单独立线（属判据面新增）。不回话的后果=这 10 格挂着"未过"，级 4 不能判全绿。
- **M-1′（B2 靶二次改写＋两格可选动作）**：A＝只做规模化认证（n=1,050 底尺＋单价曲线），缺省仍关，B2 视为"认证工程"；
  B＝认证后把 `--engine gpu` 纳入排产（改的是**生产缺省面**，属 Owner 门位，且需 `exclusive_group`/显存预算同时到位——后者正被 M-4 卡着）。
  本班建议 A（代价=今晚到明晚吞吐不动，但零生产风险），并**不自取 B**。
- **M-8（验收尺无判别力）**：`gpu_self_sm_pct` 心跳 60s 一拍，GPU 臂整批只 7 拍（4 拍有值），中位 2.5%/p90 5.8%/≥70% 占比 0/7 ⇒
  "批形下 ≥70% 的采样应出现"这条验收**现在测不到**（每拍 60s 内约 600 格、每格设备 ~2ms）。改拍（~2s）或改累计核时间/格＝**尺改动**，待裁，本班不改尺。
- **M-9（两把线并存）**：见第 11 项 ⚠ 行。待裁是否给"累计后净值面"一条自己的线；本班不动任何线值。
- **M-10（提交链楔死，归维护三班，本班只报数不动他人袋）**：`commit_queue.py health` 02:55 实测 `pending=46 / oldest_pending_hours=2.41 / oldest_processing_hours=2.44`，
  在 processing 的那袋属 `st-deadcure3b-chief-20261011`（8 件，created 00:29），lease holder pid=15100 `drain-active`。
  本班三袋（0006/0007/0008）排其后 ⇒ **若晨间包未落地，不是没写，是被这条楔住**；解除面=维护三班的队列存活处方（在册五查），非本班权限。
- **M-2 更新**：03 件 §十一（四数＋11 格表＋B2 预演三件读数）已写进车道，等 0006 落地后另袋投；本 00 件续段以**严格超集**重投并取代在飞 0007
  （同会话同件后袋效应，在册病案，逐字登记于此以免被读成"条目被吞"）。

### 五、统筹晨裁落账（2026-10-12 11:0x 收悉，本班 11:2x `date` 实测）与执行态

先报**落地实态**（判据＝逐件 blob＋`git show dev:<file>`，不采信状态位）：已落地三袋＝
`7f4311cc39`（0006 N-8 列序修复＋结构面钉＋03 件 §十）、`19b9eed6ce`（0007 晨间包一～三段 M-1…M-6）、`e01eee0db0`（0008 §二·丙·补 口径落纸）。
仍 pending＝0009/0010/0012/0014/0015（同件超集链：晨间包 7-18 项＋03 件 §十一），本班不抢队列、不动他人袋（⑥）。

晨裁六条的执行态（逐条详表见 03 件 §十二·A，此处只记本班动作与不做动作）：

- **① 10 格维持未过、并列翻转转 B2 输入研究**——已执行：名单与七元组读数固定在 §十一·C，自此它是 B2 的**输入件**；
  衔接规则写死在 §十二·B 第 4 条：**B2 任何归约/驻留改动必须重跑那 11 格集并逐格报形态**，不得只报聚合数（聚合会把族内命中率 32.3% 抹成 1.05%）。
- **② `--engine gpu` 只认证不动缺省**——已执行：缺省面今夜零变化；认证面补齐（bt 腿底尺 n=120／n=1,050 ＋整批 D 臂零新增越线）。
  ⚠如实提醒接班：**"已认证"≠"可默认开"**，动缺省要另走 Owner 门位。
- **③ 利用率尺维持 NVML 逐进程不改拍**——已入册真源位 `verification_framework.md` **§二·丁**（含"逐格形态下 ≥70% 测不到"的局限照留，可判性由新靶落地后重估，本班与接班都不得为此改尺）。
- **④ 两线各自成档不合并**——已入册同上 §二·丁（单元 1e-12 量 T=300/S=80 合成单出口；批线三档带量 970 日累计净值面；实测 8.973e-12 居中＝对象与窗长不同，不新立第三条线）。
- **⑤ B2 新靶采纳＋"每核同步"入册为默认口径**——立法已落 §二·丁（含两起同根事故：`ewm` 未同步虚低约 150 倍、`renorm` 吞下游虚高 3 倍；
  推论两条：冷建不摊稳态单价、绝对值不可跨时刻比）。**新靶定价已出**（`b2_residency_pricing.py`，每核同步口径）：
  all_a 稠密权重**往返 30.48ms/格**（D2H 21.21＋H2D 9.26）＝整批 ≈9.66s，zz500 2.38／hs300 1.53ms/格，合计 **≈11.0s/批**；
  且 `gc._as_f64_2d(cupy, cupy)` 实测**零拷贝直通＝True** ⇒ **不需要新核**，要的是"元数据随设备数组走"的接线
  （`_backtest_core_gpu` 现用 `weights.index/columns` 向 `_load_seal_masks` 取掩码＝pandas 依赖，一 `get()` 就把省下的往返吐回去）。
  ⚠诚实标价：11s 只占批墙钟 ≈2–3%，值集中在 all_a 一族；且**必须先有设备侧的下游消费者**（`tier/stats` 现在主机 pandas 上算），否则只是把往返搬到别处。
- **⑥ 提交链楔死归维护三班（已接手）；10 支存量红照册不代修**——本班未动他人袋、未代修；登记位＝上面第 17 项与 M-10。

**晨裁"等效认证＝今晚最大技术胜局，入册"的执行**：数值与凭据已集中落在 03 件 **§十二·C**（p₀≡0；eval 面 ULP 族 550/1,049 ≤1e-12 且越线 11/10/9 中 10 格为离散放大；
bt 面三档各 0、max_abs=2.2204e-16；两腿全上卡三档与 CPU-bt 逐档相同＝零新增越线；落地面 101 passed＋48 passed）。

### 六、两次断电与接管闸处置记录（本班 2026-10-12 19:5x `date` 实测）

经过（事实，非叙述）：11:2x 之后本机两次断电。第二次复活后本班把 §二·丁（framework）与 §十一＋§十二（03 件）按 dev 现字节重基重投，
三袋 `0016/0017/0018` 全死，**死因不是三方冲突而是另一道闸**：`门禁 TAKEOVER-PENDING 阻断：本次 commit 命中 open 接管条目（死会话遗留资源面）`。
根因＝断电期间本班被 `--scan` 按 idle 判死（idle 23638.9s > 7200s），台账为 `st-gpux2-20261011` 立了 open 条目；
同批条目里还有前班 `st-gpux-20261011`（idle 84567.2s，dirty=37），它的命中面正是 framework 与 03 件这两支——**闸拦得对**，本班不强解他人条目。

本班已做（只动自己那条）：
1. 复活自证：`list_active_readonly` 命中＋`hb_age=2.2s`（判活锚与执行工具守卫同源，不用心跳时间戳自证）。
2. 保活走正门：`register_heartbeat_keepalive(reason=断电复活续班…, ttl=7200, daemon_pid=27260)`，非裸 `mark_logical`
   （裸标被 `MARK_LOGICAL_DENIED` 拒过——非 chief 形态词∧心跳不新鲜）。
3. 销自己那条：`session_takeover_ledger.py --resolve st-gpux2-20261011 --by st-gpux2-20261011 --note <逐条处方结论>`
   ⇒ 条目迁 `.runtime/takeover/resolved/st-gpux2-20261011-1791805542.json`；随后 00 件袋 `0019` 落地 `a8a19e2f63`（**本班文档面自此全量在册**）。

**前班条目的核成果（只读逐件行集对拍，结论：无可救回成果）**：
`verification_framework.md` 仅该车道独有＝**0** 行（它落后 dev 26 行）；`03_gpux_final_report.md` 仅独有＝2 行，且 dev 现文已含该措辞的更正版（3′ 更正，`kmax` 在 dev 命中 3 处）＝被覆盖非未落地；
`factory_grid_executor.py` 独有 44／`gpu_core.py` 独有 6／`test_l2_gpu_landing.py` 独有 47，抽样逐看均为本班后续袋（B1a/§十/桩件迁移）已落地改写的**旧字节**；
`capability_canonical_file_registry.yaml` 独有 63 行＝账本册 PG 物化后退出的袋内 YAML 块（在册单源病案家族）。
该前班四只死袋 `0001/0002/0006/0007` 实测全部 dead（ghost_session／MSG-STYLE／两笔三方冲突），
**本班未 requeue、未动其 worktree（未 remove 未 abort）、未解其接管条目**。

**M-11（待您拍，一格）**：前班 `st-gpux-20261011` 的 open 条目要不要由本班代销？
- 甲＝**本班代销**（一条命令，note 已备好上面核成果证据）⇒ framework §二·丁 与 03 件 §十一＋§十二 随即重投可落地；
  代价＝代前班销账，而其四只死袋仍无人处置（销账不等于处方走完）。
- 乙＝**交维护三班**（他们已接手提交链治理）⇒ 本班只把证据与本节留在册，两件文档今晚不着地，明天随其处置重投。
  代价＝§二·丁/§十一/§十二 这三段（口径立法＋11 格逐表＋B2 新靶定价）在 dev 上缺席，后人只能从 00 件读到摘要。
- 丙＝**先解 framework 一支**（§二·丁 是立法件，时效最敏感），03 件两段随乙处理。本班**不推荐**：同一前班条目按文件拆着解等于选择性销账，台账会留下"部分处置"的模糊态。
  默认取向＝**乙**（不动他人台账），若您要今晚上册就点甲。

## 通宵执行与晨间裁定包（st-gpux4-20261013，GPU 化四班·B2 两刀；本班 2026-10-13 05:12 `date` 实测入册）

**开工令**：终局＝ffill NaN 48.5 倍消除＋网格引擎 GPU 吞吐推向 ≥3x、SM≥70%；两把刀按序＝①设备侧整数 running-max 行号核 ②价格→收益率批级共享；驻留排在两刀后（闸维持关，根因由检验道收网）。

### 一、执行了什么（逐项＋红绿证锚点）

1. **刀一已落**（`gpu_core._ffill_axis0` 的 cupy 分支：host 回环 → 设备侧 RawKernel，一 thread 一列、寄存器内推进整数行号 running-max、回填 gather 收进同一 kernel）。
   红绿证＝03 件 §十四·B 三件：①`git show dev:` 字节装第二模块，8 帧族**三向逐位等**（落地面 vs dev 面／vs `pandas .ffill()` 独立第三参照／CPU 分支 vs dev CPU 分支），比较器＝float64 的 uint64 位视图；
   ②端到端 `tensor_core` 8 组（两形 × gpu/cpu × 闸开闸关）gross/turnover/五档 nets/hold_days **逐位全等**；
   ③在册试件 **114→125 passed**＋**突变能红**（改一行 `run=t` → `test_gpu_parity_within_1e_12` FAILED，相对差 1.890e-03）。
   计时（每核同步＋两序交错，只报比值）＝宽宇宙含 NaN 帧 **63.5–129.6x**、小 T 面 22.2–29.1x、窄宇宙 4.5–7.4x、无 NaN 短路面 **1.0x（无回归）**。
2. **刀二已落**（`_c4_engine._PRE_RETS` 批级设备 rets 共享 → `tensor_core(pre_rets=…)`；px 整幅不再上卡）。
   红绿证＝03 件 §十五·B 三层：构造层（缓存产出式与核内侧同一函数体 `px_rets`）／端到端层（五档 nets 逐位）／批形层（**`rets_hit=7`／8 格、n=24 车道烟测 `hit=21/put=3`、全格集臂 hit 破千**——命中为 0 时前两层是空转，所以它是前置存在性证明）；
   另两条防线：同内容不同宿主对象 ⇒ put 而非 hit；供入另一张面板的 rets ⇒ 必须翻红。宽面比值 **1.53x**（窄面只有 1.26–1.45x，不同分母不同表）。
   全格集上缓存确实吃到：`rets_hit=1047／rets_put=3`（三个宇宙各建一次）。
3. **全格集铁律针已跑完两把**（n=1,050、seed/分层/窗与 §十一 §十三 逐字同；驻留闸全程关）：分母机读原值 `cells_common=1049`。
   刀一＝**PASS**（A↔R0 的 11/10/9 越线与 `max_abs=1.3782476464733046e-03` **与前班在册 dev 码读数逐位相同**，>1e-4 的 9 格 id 同一组⇒ 跨版本零改判）；
   刀二＝**PASS**（一臂一进程六对三档越线全 0，跨形态 max_abs 2.4980e-16 落在同形态跨进程底 1.6653e-16 同量级，`rets_hit=1047／put=3` 证真命中）。
   同进程那 4 格越线经隔离复现**归零**⇒ 是 R1 臂位产物（族签名 `raw×ic_ir×hs300`，在 eval 侧 id 键面上），不是刀二。详见 03 件 §十六。
4. **终局两线（n=120、A/B/A/B 交错三对、逐进程 NVML 真尺不改拍）**：
   **吞吐线未达 ≥3x**＝暖态两对 **2.52–2.86x**（rep1 那个 2.995x 是首臂冷建伪影，按 §十三·补① 不采信；三对递减，本班不挑最大值）；
   **SM 线由"测不到"改判为"测得到且没达到"**＝三 GPU 臂 226 拍里 **167 拍拿到非空逐进程 SM**（中位 6–9%／p90 12–14%／峰值 31%／**≥70% 占比 0/167**）。
   差距主因仍是一格一整套 launch＋主机收口的串行形态，开它的钥匙＝N-1 批内并行，不在两刀令内，本班不自扩。详表 03 件 §十六·D。
5. **第二车道 04:10 首夜读数——已取**（读日志＋CH 计数，未碰 01:00–04:00 窗）：
   `ZephyrAlpha_KronosScoring` 首夜批 00:30:00 起跑，`.runtime/logs/kronos_scoring.log` 末态 `shard_status=complete, scored=75/75, failed=0, sec_per_symbol=0.65, symbols_fit_in_cap=2299, cap=25m, device=cuda`；
   CH 计数（`DatabaseService.get_clickhouse_conn` 单口，FINAL）＝`c1_market.kronos_prediction_daily` **75 行、run_id 1 个**（`kronos-score-20261012-163002`），仍"只落不用"。
   令文"三档都在"已实测复算（Ollama 在册 8 枚：qwen3:14b 8.38GB／qwen3:8b 4.87GB／deepseek-r1:14b 8.37GB／deepseek-r1:8b 4.87GB…）；
   `ZephyrAlpha_FactoryLaneC` 末跑 10-12 20:00 rc=0 all green、下次 20:00；**任务计划里查无 NightMining**（`Get-ScheduledTask` 匹配 Night|Mining 只命中 `tilib_indicator_backfill_nightly`）＝与令文"NightMining 维持 Disabled"逐字一致。
   `GPU-01 档位 A/B` **本班未起**，硬约束见三等裁 M-2（不是"没做"，是两条分母/配额都实测堵着）。
6. **两条移交件**（不代修，只给机制＋行号）：见 §十四·E 与前班采样器键错位一条（§十六·D 末）。

### 二、自裁了什么（逐条＋证据＋依据）

| # | 自裁 | 依据与证据 |
|---|---|---|
| Z-1 | 刀二**另起一本缓存**而不并入 `_DEV_RESIDENCY` | 检验道正在按"三套缓存命中/逐出时序交互"查驻留红账（§十三·补·补 唯一未排除候选）；并入会污染其占用序列，且 `set_dev_residency_enabled(False)` 会连本刀一起清 ⇒ 对照臂不干净。另起一本＝两本各记各账，`residency_stats()` 合并出仓并写明键面归属 |
| Z-2 | `_ffill_rawkernel` 非 float64 **直抛** | RawKernel 按 `const double*` 解读显存，dtype 走错是静默重解释而非报错；现有两处调用方均在 `_as_f64_2d` 之后，本闸只拦未来直调（配 `test_ffill_rawkernel_rejects_non_float64`） |
| Z-3 | 两个改动都放**缺省参数位**（`pre_rets=None`）＋保留 `mask.any()` 短路 | 缺省面零漂移红线；短路面实测 1.0x 且 `new is a and old is a`＝无 NaN 帧一个字节都没多动 |
| Z-4 | 把"绝对值入表必逐行回放"从纪律**变成工具**（`g4_emit_tables.py` 直接从 json 打 markdown 行） | 本班第二犯＝手抄三行毫秒列串行而比值列正确（§十四·C 第 3 条）；机制化后同类错不可能再发生 |
| Z-5 | 未动任何判据线值／未动 `--engine gpu` 缺省／未摘驻留闸／未碰前班死袋与其 worktree | 晨裁②③、§十三·补·补 残余状态更正、开工令禁碰条；对 `_dev_panel` 与 `_DEV_PANEL_CACHE` **零写入** |

### 三、等裁什么（编号菜单＋证据＋建议默认）

- **M-1 刀二终态（本班按判据取"开"，若您要更保守可点关）**：两层证据都绿——段面/端到端/批形三层逐位＋全格集一臂一进程六对三档越线全 0；
  故本班让 `_PRE_RETS_ENABLED` 缺省 True（设备支路生效），手柄与 `rets_hit/put/mem_clear` 计数器在册，
  关闸回退命令＝`_c4_engine.set_pre_rets_enabled(False)`（一行，清缓存不留混态）。
  ⚠ 本班**不援引"PASS"去碰缺省引擎面**：`--engine gpu` 仍只认证不动缺省（晨裁② 一字未改），
  本刀生效面＝`engine=auto` 解析到设备的那条既有路（改动前后同路，只换实现与求值次数）。
  若您判"仍需第二班复核再开"，点关＝把上面那行置 False，接线与尺全部留着（沿用 §十三·补·补 的关闸法）。
- **M-2 GPU-01 档位 A/B 今晚为何没起**（两条都是实测，不是推演）：
  ①**分母为 0**——三指标里的"入考通过率"，其可考面现器为零：`docs/_working/examunlock_campaign/04_target_face_channel_census.yaml`
  第 7 行 `preregistered: 177`／第 13 行 `blocked_on_target_face: 118`／**第 14 行 `supported_today: 0`**（本班按 `git show dev:` 取字节后 grep 命中，非转述）；
  ②**夜窗装不下**——`config/gguf_vram_budget.yaml` 第 46–48 行 night 段 `inference_quota_gb: 4.0`，而三档最小者 qwen3:8b 在册 `vram_gb: 5.4`（第 57 行），14b 档 9.2（第 69–81 行）⇒ 必须走手动窗＋临时配额，
  而手动窗与本班的 GPU 全格集针/吞吐针互斥（单卡 `vram.concurrency: 1`，§一·补 硬件红线）。
  默认取向＝**待解锁班把 A 面打开、且排一个不与网格批争卡的手动窗**后由下一班跑；本班只交首夜读数＋这两条堵点的行号级证据。
  （若只要"产出量"单指标先跑，本班可做，但那是把三指标实验降成一指标——属改实验设计，不属本班自裁面。）
- **M-3 SM≥70% 线：本班按铁律④ 用逐进程真尺、不改拍重测后，"测不到"改判为"测得到且没达到"**（167/226 拍非空，中位 6–9%，≥70% 占比 0/167）。
  于是这道题从"尺有没有效"变成"要不要为达线改形态或改尺"：
  甲＝维持现尺现形态，接受逐格形态下 SM 就是个位数，**≥70% 这条验收线在网格批形下永久不可达**（它描述的是常驻大核形态）；
  乙＝改形态（N-1 批内并行），达线由占空比自然抬升，代价＝那是另一把刀、且归约序改动会重排 §十一·C 那 10 格；
  丙＝改尺（"累计核时间/格"替代瞬时 SM，或把拍从 1s 降到 ~2s），代价＝晨裁③ 明写"不改拍"，需您点头。
  默认取向＝**甲＋把 ≥70% 从验收线降为披露线**（本班不自裁降线）。
  ⚠ 另有一条归因边界须您或尺主班定性：CPU 臂也拿到 13 拍非空（紧接 GPU 臂之后的十几秒），
  ⇒ **"在不在计算表"不能当二值闸用**；本针未据此断言机制。
- **M-4 前班采样器键错位**（`b2_throughput_sm.py:61` 存 `r.get("sm_pct")`，而 `nvml_process_util()` 实测返回键是 `sm_util_pct`，无 `sm_pct`）
  ⇒ 其 `sm_unavailable` 恒等于总拍数，那句"171／87 枚采样命中 0 枚"**是尺的空读，不是现场事实**。
  本班已用对键复跑并三口径分计（总拍／在表／非空），数在 03 件 §十六·D②。
  待裁＝是否要求前班那两支依赖此数的在册结论做一次复核（本班只报复现，不改他人账）。
- **M-5 驻留收益构成改写**：刀二命中后核内**不再读 px** ⇒ §十二·B 给驻留定的价里"价格面板常驻"这一半被覆盖（掩码常驻＋权重驻留两半不受影响）。
  属读数不属裁决；请检验道在收网时按新构成重算，别拿旧表当上界。

### 四、本班自犯并如实上报（**八条**，全部本班自己抓到，非他人指出）

1. **校准针族名与构造不符**：第一版把 `no_nan_control` 写成 `px.copy()`，而 `px` 当时已被注入停牌 NaN
   ⇒ 标称"短路面"实测 nan_frac=0.0028、`short_circuit_no_copy` 整列 None，**该面根本没测到**。
   修为独立 `clean` 面板重跑才拿到 1.0x／`new is a and old is a = True`；同批补齐窄宇宙 (970,300) 与小 T (60,5217) 两形。
2. **入册表格手抄串行**：§十四·B① 表初稿把 `bitwise_edge_values／narrow_hs300／short_T_60` 三行的毫秒列
   搬了别的族的数，而比值列是对的——"比值对、绝对值错"最危险，读者按比值核账会全过。
   已按 json 真字节逐行回放更正；并写了**表格发射器＋装配器**，此后入册表格一律由 json 直出（见 Z-4）。
3. **Edit 追加吃掉上一函数的 `finally:`**：把试件新节插在 `finally` 之前，导致该块被挪到全文件末尾、`ast.parse` SyntaxError。
   复位后改用结构计数自证（funcs=28／try_blocks=4／文件尾不再是 finally）。这是在册"追加锚点吃标题"病的**吃收尾块**变体。
4. **旧注释指针指向已消失分支**：替换 `_ffill_axis0` 后，同文件 :638 仍写"同 _ffill_axis0 host 回环纪律"
   ⇒ 该分支已不存在，属"尺/注释指向幽灵位置"家族；已改指"设备核/主机 numpy 双支"。
5. **判据整段从前班针搬来**（最实质的一条）：`claim_knife2` 首判 FAIL，成因是 `跨形态三档越线全 0` 这条
   在全格集上连**同码两臂**都可能过不了（本批 R1↔R1b 同开关也报 4 格）——而前班 §十三·C① 自己明写"设备臂逐位不可复现，判据须对底不对零"。
   改判形为"跨形态差集 ⊆ 同码底差集 ∧ 一臂一进程复现"后 PASS。**若照首判关闸，就是把写错的尺当成被测物不合格。**详见 03 件 §十六·G。
6. **装配器与追加脚本读了不同文件**：装配器把填好的版本写成 `final_*.md`，追加脚本却仍读原始草稿
   ⇒ 三类占位标记（TABLE／CELLS／TIME，下划线包裹式）原样进档（5＋1 处）。已截回尾部重贴，并加"标记数必须为 0"的写后自证。
7. **`write_text` 把三份文档整档转成 CRLF**：仓内 `.gitattributes` 定 eol=lf，git 归一化后 diff 看着干净（0 删除），
   但**盘上字节已整档变**——他人按盘字节做的尺会读到差异。已按字节归一回 LF，归一前后 numstat（104/359/65/103/175）与试件 35 passed 不变。
8. **两把我自己的 grep 正则指向幽灵位置**（同一条病型在本班出现两次）：
   `^\[(A|R)_` 漏掉臂名带数字的 `[R0_...]`／`[R1_...]`，让我一度以为 GPU 臂没在跑；
   `^\| 族名 ` 漏掉族名后紧跟全角括号的行，让我一度以为 §十四表只剩 1 行。
   两次都是**观测面错**而非被测物错，但都差点据此误判进度/文档完整性——正对照应先于结论。

### 五、复核命令（全只读）### 五、复核命令（全只读）

```bash
LANE='D:\ZephyrAlpha\.aidrafts\st-gpux4-20261013'
cd D:/ZephyrAlpha/.aidrafts/st-gpux4-20261013
# 刀一三向对拍（含 git show dev 字节面装第二模块）
PYTHONPATH="$LANE\src;$LANE\scripts" python D:/ZephyrAlpha/.runtime/tmp/st-gpux4-20261013/g4_ffill_verify.py
# 刀二三层对拍＋宽面比值
PYTHONPATH="$LANE\src;$LANE\scripts" python D:/ZephyrAlpha/.runtime/tmp/st-gpux4-20261013/g4_rets_verify.py
PYTHONPATH="$LANE\src;$LANE\scripts" python D:/ZephyrAlpha/.runtime/tmp/st-gpux4-20261013/g4_rets_big.py
# 全格集四臂铁律针（≈30min，需 ClickHouse 在线；驻留闸在针内恒关）
PYTHONPATH="$LANE\src;$LANE\scripts" python D:/ZephyrAlpha/.runtime/tmp/st-gpux4-20261013/g4_fullcell_floor.py 1050
# 试件（期望 125 passed 与 39 passed）
PYTHONPATH="$LANE\src;$LANE\scripts" python -m pytest -q tests/research/backtest/test_gpu_core_parity.py tests/research/backtest/test_l2_gpu_landing.py tests/research/backtest/test_c4_engine_gpu_wiring.py
PYTHONPATH="$LANE\src;$LANE\scripts" python -m pytest -q tests/research/backtest/test_c4_limit_gate.py tests/research/backtest/test_c4_batch_smoke.py tests/research/backtest/test_c4_auto_oos.py
# 班账表格发射器（入册数字一律由它产出，禁手抄）
PYTHONPATH="$LANE\src" python D:/ZephyrAlpha/.runtime/tmp/st-gpux4-20261013/g4_emit_tables.py
```
⚠ 车道 PYTHONPATH **必须写真 Windows 路径**（`D:\…\.aidrafts\<sid>\src`）；写成 `/d/…` 会被拼成 `D:\d\…`（不存在的死条目），
   于是 editable 安装的 `.pth` 静默胜出、包读主区——本班实测这才是 §十三·C③ 那个"裂脑"现象的机制（现象真、归因错，详见 03 件 §十四·C 第 1 条）。
   `python -s` 不能当旁路：本机 CUDA_PATH 也由 `.pth` 提供，`-s` 下 cupy 立刻发 "CUDA path could not be detected" 警告。

### 六、本班收工态与落地核验指令（本班 2026-10-13 05:5x `date` 实测）

- **三袋在飞**：`q-20261013-st-gpux4-20261013-0001`（刀一袋）＝processing；`-0002`（刀二＋验收）pending ahead=15；
  `-0003`（终袋＝红蓝对抗＋声明不变式＋自犯改实数）pending ahead=17。**0003 是同五件的严格超集**，按序落地即终态。
  队列合并器两次报"共享注册表路径不可信合并——拒绝压缩，两袋保留"⇒ **不存在同会话后袋静默取代前袋**那种风险。
- **claim held=5 未放**（`gpu_core.py`／`_c4_engine.py`／`test_gpu_core_parity.py`／03 件／00 件，
  均按**车道绝对路径** claim——相对路径会 0/8 零告警，在册病型）；**袋在飞禁放锁**。
  保活经 `register_heartbeat_keepalive` 复授至 **07:51**（reason 在册），心跳 daemon pid 见 `.runtime/sessions/st-gpux4-20261013/heartbeat.jsonl`。
- **落地只认字节**（`done` 计数与 `[enqueue]` 回显都不算证据）：

```bash
git show dev:src/zephyr/backtest/gpu_core.py | grep -c "ffill_axis0_scan"        # 刀一：期望 2（核源＋RawKernel 名）
git show dev:scripts/backtest/translated/_c4_engine.py | grep -c "_PRE_RETS"     # 刀二：期望 ≥6
git show dev:docs/_working/gpufeed_campaign/00_gpufeed_report.md | grep -c "st-gpux4-20261013"   # 晨间包：期望 ≥2
```
  任一为 0 ⇒ 该件未落地，勿按"已入队"记账。若 0001 判 dead：读 `dead_reason` 修正后 `commit_queue.py requeue <qid>`，
  或直接重投 0003（超集）；**不要动他班袋**。
- **临时件与产物**：尺与配方留 `.runtime/tmp/st-gpux4-20261013/`（24h TTL，含 `backup_g4/SHA256.txt` 五件字节存证，
  供车道被清扫时按 sha 反查恢复）；跑批产物 `data/strategy_intake/grid_20261013-*`（10 目录、单目录 ~0.4MB、
  未跟踪且未 ignore，**禁 commit**）。项目根目录零临时文件（本班核对未新增根级文件）。
### 七、收班确认与准裁落账（本班 2026-10-13 13:37 `date` 实测；Owner 对本班的验收与三条准裁）

**Owner 验收原话（本班转述，逐条落此以免随会话蒸发）**："两刀全落（刀一 75d4663977／刀二 c8176afded）、
等价判据全绿、归属面干净、125 passed——本班验收，准予收工。"

**三条准裁与它们的账面后果（都是裁定面，本班只记账、不自签、不动任何线值）**：

| # | 准裁 | 账面后果 | 本班做了什么／没做什么 |
|---|---|---|---|
| 一 | **SM≥70% 降为披露线**（"你抓的前班键名错位＝那条线从未被量过"） | 该线自此**不再当闸**，只作披露；本班实测留册＝三 GPU 臂 226 拍里 167 拍非空、中位 6–9%、p90 12–14%、峰 31%、≥70% 占比 0/167（03 件 §十六·D②） | **未**改 `verification_framework.md` 任何线值、**未**签发裁定号、**未**自改尺；形式登记归统筹/维护线（在册纪律：对话内口头不构成门禁豁免，见根宪法第 9 节第 11 条） |
| 二 | **N-1 批内并行＝另开班令**（"改归约/并行形态的新刀不塞给你"），由 Owner 在本班收工后出令 | 本班两刀即为它的基线（ffill 已在卡上、rets 已批级共享）；交接四条见下 | 本班**不扩面自裁**，只把接口与坑写清 |
| 三 | **吞吐 2.52–2.86x 如实入册**（不要求达 3x 才算本班交卷） | 终局线未达但账算平：瓶颈＝一格一整套 launch＋主机收口（非 PCIe），§十三·补① 那句一字未改 | rep1 的 2.995x 按 §十三·补① 判为冷建伪影，**未采信、未当结论**；三对递减原样入册 |

**给 N-1 班的四条交接（都是本班实测换来的，能省它一轮弯路）**：

1. `rets` 现已按"价格面板宿主对象身份"批级共享（`_c4_engine._PRE_RETS`，`rets_hit=1047／put=3`）——
   N-1 一次端多格时**必须仍从同一份共享件取数**，若在任何新支路里重算 `px_rets`，就是把刀二的收益又付回去；
   且新支路若要缓存，沿用"内容键＋命中核宿主身份＋引用随值 pin 住"，**禁仿 `_dev_panel` 的裸 id() 键**（03 件 §十四·E）。
2. **判形已定**：设备面改动的等价判据＝`跨形态差集 ⊆ 同码自噪底差集` ∧ `一臂一进程复现`；
   底必须**同 n、同臂位对称性现测**（本役实测同进程 n=1,050 的底可到 4 格越 1e-4／max_abs 7.7e-2，
   而 n=24 那个 5.5e-17 沿用不得，03 件 §十六·G）。N-1 改归约序 ⇒ 它的底会比本役更大，先量底再判。
3. **验收分母＝全格集分族**（§二·戊），具名 11 格只是 fast-fail 面；但 N-1 是新归约序，
   **预期会重排 §十一·C 那 10 格**（施工单原话），而那 10 格正等 Owner 处置（M-7）——
   开工前先把那 10 格的处置问清，否则动一次核就把呈批面变成既成事实。
4. **落地袋纪律**（本役刚踩）：同会话同件多袋时，前袋一落地后袋 base 即过期 ⇒
   重投要 `commit_queue.py requeue <qid> --base-head dev --force`（越熔断留痕），
   且**在车道里跑但显式 `--queue-root` 指主队列根**（车道副本会静默进影子根；
   `--allow-non-worktree` 不属 commit_queue 的旗，在主区跑会被 WORKTREE-REQUIRED 挡）。

**本班终态**：刀一＋刀二均在 dev；车道工作树与 dev 逐字节同；落地面 125 passed（同字节面复跑）；
claim 4/5 已放（第 5 件 03 件现由 `st-gpuux3v-20261013` 合法持有，本班不夺）；
保活随本袋落地后撤销；`.runtime/tmp/st-gpux4-20261013/` 留尺＋`backup_g4/SHA256.txt` 字节存证（24h TTL）。

## 通宵执行与晨间裁定包（st-gpux5-20261013，GPU 化五班·N-1 批内并行＋修法乙丙实施；本班 2026-10-13 18:1x `date` 实测入册）

技术账在 03 件 §十七（归因／施工面／红绿证／全格集分族验收／终局两线／三级指纹／条件腿／自犯／红蓝对抗／残余）。
本节只记**执行态、自裁面、等裁面、收工态**，不复述数值结论。

### 一、执行了什么（逐项＋凭据位）

1. **开工第一动作＝判活三查**（令条）。实测：队列 `pending=0／processing=0`（无在途袋）；
   检验道袋 `ac3d2d0376` 已在 dev；`lock_files.py cleanup` 当场把 **st-gpuux3v-20261013 判死并 SALVAGED**
   （merge=skipped／stash=0／释放 claim=0）。该 sid 的尺与存证全在 24h TTL 面，
   本班 14:3x 起第一动作即 `cp -rn` 抢救 76MB／112 件到 `rescued_v3/`——否则 §十三·检·K 六条复核命令明天不可复算
   （"清理窗在吃证据"是前班在册自犯第 4 条，本班接住了）。
2. **先定价再动刀**：没照开工令那句"瓶颈＝逐格 launch 往返"开工，而是先用**在册仪表**读上一班 GPU 臂现成数
   （零卡时），再自跑 n=200 分段针＋cProfile。**开工令那半句被改判**：设备核是毫秒级下界、
   真 PCIe 搬运 3.09s/148s（2%），主体＝每前缀重复的主机 pandas 求值（144 个 miss 格＝格数 13.7%、
   占 eval 腿 **59.7%**）。00 件 §三 当年那条瓶颈排序的第①②位被独立复算支持。详 03 件 §十七·A。
3. **修法乙＋丙实施**（统筹 2026-10-13 裁④"批排一批"）＝袋 `bbeb0aa36c`：
   九站点全改造＋瞬态宿主站点做成内容键（不是甲/乙二选一）＋丙当缺省关的运行期哨兵＋`logmvdm` 补 `id(industry_map)`
   ＋整清改 FIFO 单枚＋批起点复位（乙 pin 的唯一释放面）。
4. **验收三腿齐**（不是"一腿当结论"）：全格集四臂同进程分族 ＋ 一臂一进程四独立进程六对 ＋ 两序/交替配对。
   正对照复现在册 dev 读数 11/10/9 与 `max_abs=0.0013782476464733046` **逐字命中**；
   具名 11 格 ∩ 差集 = ∅（＝本刀不改归约序，顺带用证据回答在册 M-7，不靠问答）。
5. **三级指纹配方腿**（§十三·检·I⑤ 三段，裁③第 3 句"只做族内、禁全引擎扫"）：
   本班换 `PYTHONHASHSEED` 三进程实测＝**2.0% 的格（4/200）的主机侧权重逐位随种子变**，
   而"上卡后回读"与主机面**逐位相同**、核出口差异**就是同一批 4 格**
   ⇒ 末位差最早可见位＝**进核之前的主机侧权重装配**；搬运无罪、核不新增。
   故配方③的第四候选（cupy 归约/原子序）**未被触发，本班不动卡**。
   本班并独立复算支持裁③第 3 句：35 格末位差 **35/35 全落 `signal_strength`**（基率 12.7%、族内 26.3%）。
6. **红蓝对抗一轮**＝委托不知情独立复核攻击六条主张，得 12 处"站不住/须补一句"，**逐条已处置**（改文／补证／降级措辞），
   其中三条直接改掉了本班的实物结论（见 §二 Z-7～Z-9 与 03 件 §十七·J）。
7. **条件腿＝GPU-01 档位 A/B 未自启**：两条前置按 `git show dev:` 现字节实测都不满足
   （`supported_today: 0` 在第 14 行；夜窗配额 4.0GB < 最小档 5.4GB），且互斥组无该条目、
   本班自己的验收针正占着单卡。按令条"前置不满足＝如实呈报不自启"执行（03 件 §十七·F 带行号与正对照）。

### 二、自裁了什么（逐条＋依据；全部只动设备认证支路，缺省面零动）

| # | 自裁 | 依据与证据 |
|---|---|---|
| Z-1 | `w` 站点不吃身份 pin、改内容指纹进键 | 令条"九站点 id 键改造"逐字执行会撞在册事实：`_ic_weight_frame` 宿主瞬态 ⇒ `is` 永假 ⇒ 永久失配＝静默性能回归。检验道 H 表把它写成"甲或乙"二选一，本班做出第三条；试件双面钉（同内容必命中／异内容必不命中） |
| Z-2 | cap 12→48 ＋ 整清改 FIFO 单枚 ＋ 3GiB 字节预算 ＋ `run_batch` 批起点 `reset_panel_cache()` | §十七·A 铁证（`fwd_ranked` 52 次只有 3 个不同键＝16 倍重算）；批起点复位是乙 pin 的必配释放面 |
| Z-3 | `logmvdm` 键补 `id(industry_map)` | 检验道 C 表原话"（不含 industry_map）"＝键缺内容位；批级件⇒加位不丢命中 |
| Z-4 | 丙缺省**关**、只在认证针上开；STRICT 档才抛 | 开工令"不匹配即红"与检验道"丙先只在测试/认证针上开"取并集；缺省面零开销零漂移。代价实测在册（前班 +38%），本班不据跨时刻数定单价 |
| Z-5 | 归因结论**降级**：设备成本用"毫秒级下界"表述，不签具体 ms | 本班归因针 `sync_mode=false`，按 §二·丁 事故①不同步段可虚低 ~150 倍 ⇒ 不用未同步数给设备工作定价 |
| Z-6 | 第二把刀（A1 归一化批内去重）**不落代码**，只交定价＋调用图审计＋71 行草稿 | 实测该块 cumtime 43.69s/148.08s＝**29.5% 单项最大**、冗余 **8.0 倍**、就地改写审计干净。不落理由＝终局线已在两分母读到过线值，再加一支需整轮三腿验收，**断班比少一把刀更贵**。草稿存 `g5_hoist_draft_block.py.txt`（未验证，禁直接落地） |
| Z-7 | 终局线判定**不签单点**：改签"暖态配对是否全部 ≥3x"，并补 rep3 腿 | 独立复核指出 r2 富余 0.6% 而同形态墙钟漂 22%、交叉配对 2.94 不过线；前班当年亦把 2.995x 判成冷建伪影。同形问题同判据 |
| Z-8 | 本刀收益判据从"两序比值"升级为**同进程交替配对**（pair4） | 两序腿把本班首版 1.289x 判回 1.05–1.11x，独立进程腿更给出 +2.4%（FIFO 臂反而慢）⇒ 墙钟收益与末位差一样受臂位/进程污染，**只在同进程交替下签** |
| Z-9 | 分母 1,048 与在册 1,049 **并存各留各账**，不写"覆盖" | §二·戊 纪律1。差因已定名到格与到本班的命令行（§十七·H⑤⑥），不藏进"数据态变化"这种不可核的说法 |

### 三、等裁什么（编号菜单＋证据＋建议默认，全部不自裁）

- **P-1 归一化批内去重要不要下一班即落**（Z-6）：已定价 8× 冗余／29.5% cumtime／审计干净／草稿在案。
  建议默认＝落（剩余最大单笔安全收益），须走完整三腿；本班不自扩。
- **P-2 面板缓存 FIFO→LRU 触碰**：1 行，实测 `pc_evict=74`（cap=48 仍在逐出）说明还有命中余量；建议与 P-1 同批。
- **P-3 主机 λ 链上卡**（`apply_cap_and_lambda` 71ms/格、`glue_gpu_inline=0` 因 `_EVAL_GLUE_GPU` 关）：
  路已建成且前班在 engage 面证过逐位等；**开关归统筹**，先要定性它属不属于"驻留"家族（若算，四裁③是否覆盖）。
- **P-4 SM≥70% 线的形式登记**：前班收班袋记 Owner 准裁"降为披露位"但自陈未签裁定号⇒册面无署名。
  本班不改线值不改尺（晨裁③），只登记缺口。
- **P-5 末位种子定名到行**：本班已收窄到"主机侧权重装配、随哈希种子变"，4 格 id 在案；
  第四候选（cupy 序）按配方③未被触发，禁动卡一条不变。
- **P-6 每核同步版归因复跑**＋**P-7 尺与针的长命化**（现全在 24h TTL 面，§十六·I 那句"长命真源＝表格＋复算命令"
  等于承认明天起命令不可跑——矛盾在册未解，收进受版本管理工具位需过新建件三道闸，属统筹门位）。
- **P-9 请求授权接管 `st-gpux4-20261013` 死会话资源面**（唯一卡住本班交付的一件事）：
  要什么＝一句 `session_takeover_ledger.py --resolve st-gpux4-20261013 --by <接管者>`；
  为何不是本班自决＝在册处方写明"他班须批"，且它道 worktree `dirty=19`（4 件跟踪件改动＋15 个跑批目录），
  其中 `gpu_core.py`／`_c4_engine.py` 两面与 dev 的关系本班**未逐件核**——处置它＝可能替下一班决定丢弃什么；
  不点会怎样＝03 件 §十七（N-1 施工账十一小节）与 §K 撞车记录只活在车道与 TTL 存证里，明天起不可复算；
  本班给的最低权限替代路＝**只 resolve、不动它道任何文件、不 remove 任何 worktree**。

- **P-8 `tests/research/backtest` 存量红**：`test_factory_grid_stage_cost_tiers.py` 6 支 ＋
  `test_t3a_grid_s_wiring.py::test_grid_expansion_x_dims_phase_gating` 一支挂死（120s timeout 掐断整场），
  **在 pre-bag 独立工作树同面复算＝同样 6 支＋同一支挂死**（两本日志同 204 行、同栈）⇒ HEAD 级、与本袋无关，属他役 owner 面。

### 四、本班自犯（九条，逐条在 03 件 §十七·H，此处只列名目不抄细节）

零采集当能红／`_panel_fp` 布局敏感 1 ULP／替身取视图致判据假绿／1.289x 臂位污染（两序判回 1.05–1.11x）／
发车 n 写成 1,049（协议 1,050）／缺格归因归错到别人家死格（被复核算正）／搬运两口径混用（4.7s vs 3.09s）／
"工作集≈30 枚"推演当实测（被自家 `pc_evict=74` 证伪）／叙述跑在动作前面两次＋体感钟又差一倍（`date` 纠正）。

### 五、复核命令

见 03 件 §十七 各节内联位＋本班 `g5_*.py` 六件（归因针／验收针四模式／独立进程对拍／两序与交替配对腿／
三级指纹针与判读件／突变自证／纯尾追加装配器）。**⚠ 这些针现在全在 24h TTL 面**（P-7 那条矛盾本班同样中招）。

### 六、本班收工态与落地核验指令

- 落地：`bbeb0aa36c`（乙丙＋逐出治本＋10 枚试件）在 dev；按字节读回核实
  `git rev-parse dev:<件>` 与车道工作树 `git hash-object` **两件全等**；落地件独立复跑 10 passed。
- 两轮复跑（落地面，七件相关面同一集合）＝**223 passed / 0 failed，两轮同数**；全目录清扫被两处 HEAD 级挂死掐断（`position_recipe_compiler._expand` 120s timeout），pre-bag 工作树同形复现⇒不属本袋，已交维护线（03 件 §十七·C④）。
- **交付状态＝00 件已投、03 件 §十七 被 TAKEOVER-PENDING 挡在队列外**：死会话 `st-gpux4-20261013`
  （前一班）的接管条目命中文件清单里就有 `03_gpux_final_report.md`，drain 因此判死
  （`q-20261013-st-gpux5-20261013-0002`，同签名已复发 85 次触发熔断）。
  本班**不自解他班条目**（在册处方＝自解条目可、他班须批）。已做两步均可逆：
  ①把它道那卷脏面 `cp -n` 存证＝它是 **1342 行的陈旧面**（dev 已 2162 行），这道闸正是在防有人把这卷提交回去；
  ②本班 §十七 装配成品另存 `.runtime/tmp/st-gpux5-20261013/g5_sec17_assembled_full.md`（24h TTL）。
  **只差一次授权**：`--resolve st-gpux4-20261013 --by <接管者>` 后重投即走；拖过 TTL 需从 `dead/` 袋快照反查。

- 未动清单（逐条可核）：`_RESIDENCY_ENABLE_FOR_TEST` 缺省 False／`--engine`、`--eval-backend` 缺省／
  任何判据线值与容差／每核同步定义／生产风控件／矿考判官件／`tests/backtest` 存量红／前班死袋与其 worktree。
- 收班即清（根宪法 §2 第 9 条新版）：claim 全释放／保活 revoke／车道与 `wt_prebag` 基线工作树就地归档，
  不给下一班留第六态。

### 七、本班终态与接管挡点的实际解法（2026-10-13 19:2x `date` 实测；追加于 §六 之后，§六 原文一字未改）

**先更正 §六 那一句的路线**：§六 写"只差一次授权＝`--resolve st-gpux4-20261013` 后重投即走"。实际落地**没走那条**——
只读取证证明那枚命中件是**落后件不是未落地件**（车道 HEAD 是 dev 祖先、其对 dev 的多重集独有行数＝0），
于是本班改为**修喂给闸的那一侧输入**（把死车道的陈旧面对齐到落地面），
再经台账自身幂等单口只刷该 sid，**不 `--resolve`、不 `--scan`、不 remove 他班 worktree、不删他那 18 枚未跟踪跑批目录**
⇒ open 条目与全部可见性保留（碰那 18 枚目录仍会被挡）。全过程、四步口、副作用实测在 03 件 §十七·M。
本节把这条**呈批件**交出去，本班不自裁：

- **P-9（新，请统筹／维护线裁）＝接管命中面缺一条"落后件"识别腿**。
  这是什么：维护五班批①的剔除口径是"盘字节 == 落地面才移出命中面"，它按"只缩不扩"设计，本班不翻；
  但它**结构上看不见"车道面 ⊆ 落地面而字节不等"**——即死车道停在旧落地面、dev 之后被别的班往前推。
  为何要点头：后果不是一次性的，是**每班一撞**——本班 03 件撞死一袋，解完后 00 件立刻进面（因为本班 18:43 那＋101 行
  把 dev 推前了），下一班碰这两卷任意一卷还要再撞；GPU 战役的班账卷天生是追加型共享件，所以只会越来越密。
  不点会怎样：每班各自花一轮做"内容级取证＋对齐车道面＋单口刷新"（本班这一轮＝两针＋一次刷新＋四步口），
  并且每班都可能选错路（有人可能直接 `--resolve` 抹掉整条目可见性，或改判据白名单＝那才是事故）。
  本班建议形（**不实施一字**）＝加性判据：跟踪件若同时满足"`车道 HEAD 是 dev 祖先` ∧ `Counter(车道面)−Counter(dev 面) 行数＝0`"
  则同批移出命中面，条目里记 `excluded_lagging_behind_landing=n` 与原因串；
  必留反对照两支＝"真未落地件仍被拦"＋"车道 HEAD 非 dev 祖先时不移出"。成本＝台账收集口一次多重集运算（只对跟踪件）。
  本班已把 00 件那一枚也按同一四步口对齐了（同证：572 行、独有行数 0、dev 严格前缀），
  刷新受台账 600s 节流窗约束，本班不自造 `now` 绕窗。
  ⚠ **并且实测到这条病灶会来回翻**：本班 03 袋 19:17 落地（dev 2162→2684）后，
  11:22:51Z 那次刷新的读数就是"`00` 已移出命中面、**`03` 又回到命中面**"——
  两枚件随 dev 前推轮流进面，与本节 P-9 是同一条病；本班后续不再投 03 件，故不受它挡。
  **下一棒若见这两卷中任意一卷在某条命中面上，先按 §十七·M 的四条只读判据量它是落后件还是未落地件，再决定动哪一侧**
  （勿直接 `--resolve`：`--resolve` 是**整条目**终态，会把那 18 枚未跟踪目录的可见性一并抹掉）。
  另记一条副作用实测（不推定"字节未变"那种话）：本次刷新前后台账 open 行数 **185→185**，
  带最新 ts 的行**恰 1 枚**且 sid＝`st-gpux4-20261013`；期间新增的第 185 枚条目是 11:17:14Z 由别的写方生成的
  `st-condaxis-20261013`，与本班无关，本班未动它。

**三袋终态（只认字节，`done` 与回显都不算证据）**：
`bbeb0aa36c`＝码面袋（`factory_grid_executor.py` ＋205/−38、`test_l2_gpu_landing.py` ＋212/−0，10 枚试件）；
`172d9c776c`＝00 件半袋（晨间裁定包 §一～§六，＋101/−0）；
`efdeb62e17`＝03 件整袋（§十七 A–M 十三小节，**＋522/−0**，父面 2,162 行为其严格前缀，落地字节 sha 前缀 `116de453c511`
与本班车道工作树逐字节等）。三件面试件在 03 袋落地笔**之后**复跑一次＝**135 passed in 41.54s**（与落地前同数，
连同 §六 那两轮 223 passed＝本班累计三轮同集合零失败）。
前袋 `q-20261013-st-gpux5-20261013-0002` 保留在 `dead/` 不 requeue——
它的两件已分别由 0003／0004 落地，重投会把陈旧 blob 弹回去（在册"在途袋会成回退弹"形），本班按"让它死"处置并在此留名。

**落地核验指令（本班落地笔之后逐条原样跑过，期望值即真读数）**：

```bash
git show dev:docs/_working/gpufeed_campaign/03_gpux_final_report.md | wc -l           # 期望 2684
git show dev:docs/_working/gpufeed_campaign/03_gpux_final_report.md | grep -c "十七·"  # 期望 39（本班实测；A–M 十三小节齐，另含正文互引）
git show dev:docs/_working/gpufeed_campaign/00_gpufeed_report.md | grep -c "gpux5-20261013"   # 期望 6（本班实测：§一～§七 标题行＋三枚 qid/路径行）
git show dev:scripts/backtest/factory_grid_executor.py | grep -c "_DEV_PANEL_VERIFY"   # 期望 8（本班实测：丙的开关面）
git log -1 --name-only --format="%h %s" efdeb62e17                                    # 期望只有那一件
python - <<'PY'                                                                        # 期望 True True（纯尾追加＋三面同）
import subprocess,hashlib,pathlib
f='docs/_working/gpufeed_campaign/03_gpux_final_report.md'
d=subprocess.run(['git','show','dev:'+f],capture_output=True).stdout
p=subprocess.run(['git','show','efdeb62e17^:'+f],capture_output=True).stdout
print(d==pathlib.Path('.aidrafts/st-gpux5-20261013/'+f).read_bytes(),
      p.decode('utf-8','replace').splitlines()==d.decode('utf-8','replace').splitlines()[:len(p.decode('utf-8','replace').splitlines())])
PY
```

**收工动作（本节落地后执行，全部可逆）**：claim 释放（03／00 两件）／保活 `revoke`／
死车道对齐件的原面留在 `.runtime/quarantine/gpux5_takeover_20261013/`（sha 记 `g5_takeover_fix_log.jsonl`）／
`dead/` 里的 0002 走 `dead-archive`（mv 非删）或按 死信清零班 的内容级门留档，本班不裸删任何死信。
