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
