---
ttl: task_bound
lane: LANE-T0
sid: st-qmine-20260925
executor: lane-t0-20260926
created: "2026-09-25"
status: running
run_progress_snapshot: "3/271 批完成（1min 已产 31,038 对），稳态 876s/批 ⇒ 全程 ≈66h 墙钟；全量进程存活，未跑完=未出任何判据结论"
peak_rss_mb_measured: 4078.9
memcap_line_mb: 5500
key_findings:
  - "前一轮零批次残留：无 manifest / 无 pairs / 冒烟日志 0 字节 ⇒ 无可续跑断点"
  - "等价复算抓出真缺陷：R01 ≠ 材料线 M0 逐位一致，根因=全局 astype(float64)，界量 0.102% pair / ≤+0.16bp 净均"
  - "实测吞吐超预检报备 2.8 倍（66h vs 23.3h），17 号文 §三.1 强制分层条件已触发"
  - "指令点名的 process_extrema.set_process_priority 全仓不存在，等价能力落在引擎内"
  - "CREATE-GUARD token 登记被他会话热册蒸发挡住（HEAD=1/DISK=0 ×4），只上报未代修"
evidence_grade: "B+（断点勘查=盘面直查；冒烟=真库真跑；全量=批 0 实测吞吐外推，未完跑完前不出任何判据结论）"
inputs:
  - docs/_working/decision_map_campaign_20260924/links/L05_t0/t0_state_match_readme.md
  - docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_cards/r01_fixed_grid_day_t.yaml
  - docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md §三
  - scripts/backtest/t0_rule_engine.py
  - scripts/backtest/t0_state_match_matrix.py
  - scripts/backtest/t0_material_line.py
  - docs/_working/decision_map_campaign_20260924/links/L05_t0/material_precapacity_sample20_stats.yaml
---

# LANE-T0 做T多周期引擎夜跑案卷（断点勘查 + 起跑 + 冒烟双证 + 吞吐实测）

> 一句话结论：**前一轮零批次残留（无可续跑断点，从头起跑）；引擎管道与闭卷闸经红绿双证确认可用，
> 但等价复算抓出一处真实缺陷——R01 与材料线 M0 并不逐位一致（全局 float64 强转翻转边界，
> 0.102% pair 受影响、净均 ≤+0.16bp，根因已做可重放实验定位，见 §4.3）；
> 全量 v1 已脱管起跑（R01×5 周期×271 批，below-normal 调度档，批峰值 RSS 实测 3.5GB）；
> 按批 0 实测 1084.9s/20 只外推，全程 ≈81.7h 墙钟 > 48h 预算 ⇒ 17 号文 §三.1 强制分层条件已触发，
> 分层方案已备好交总筹裁，本车道未自改判据面。**
>
> 判据零改动声明：31.2bp / 前置 ≥30bp / 30 对土规 / Wilson LB 排序 / n<30 禁并格 / 闭卷切点
> 2025-09-09 全部 import 复用或硬继承，本件未触碰任何阈值与口径。本件动的是**运维档**
> （调度优先级、批大小、内存哨兵）与**续跑一致性闸**，二者均不改判据结果；
> §4.3 的 float64 偏差是**交付态既有缺陷**，本车道只定位+界量+报，未夜改判定路径。


## 1. 断点勘查（前一轮遗产核账，盘面直查非记忆）

| 查什么 | 实测 | 判读 |
|---|---|---|
| `data/backtest_artifacts/t0_rule_engine/` | 存在但**零文件**（目录 mtime 2026-09-25 13:02） | 引擎建了目录、没写完任何一批 |
| `t0_rule_manifest_*.yaml` / `t0_rule_pairs_*.parquet` / `t0_rule_stats_*.yaml` | 全库 find **零命中** | 无 manifest ⇒ 无断点锚可续 |
| `links/L05_t0/t0_state_match_*.csv` / `_meta_*.yaml` | 不存在 | 匹配矩阵从未产出 |
| `.runtime/tmp/t0_rule_smoke20.log` | **0 字节** | 上一轮冒烟起跑即阵亡，连一批都没打完 |
| `.runtime/sessions/st-t0-matrix-20260924/heartbeat.jsonl` 末行 | `status=exited, reason="session not in registry"`，ts 2026-09-23T17:59:19Z | 施工班死亡时刻与死因留痕 |
| 已跑格数 / 剩格数 | **已跑 0 格，全部待跑**（矩阵格数在语料跑完前不可知） | — |
| 已跑批 / 总批 | **0 / 271**（5,410 只 ÷ 20 只/批；设计册的 109 批=50 只/批，本车道因内存自律改小，见 §3.3） | — |
| 材料线预检产物 | `.runtime/tmp/t0_material_precap/` 5 份 parquet + `t0_material_stats_precap20.yaml` **完好**，耐久副本在 `links/L05_t0/material_precapacity_sample20_stats.yaml` | **口径底座可复用**——本轮拿它做 R01 等价复算基准（§4.3），不必重跑预检 |

结论：**没有可续跑的断点，只能从批 0 起跑**；但口径真源、4 张预注册卡、预检实测基线全部完好，
未重造任何口径（README 与卡的哈希都进了 manifest，改卡即中断的机制继承未动）。

## 2. 防误杀登记（硬前置，已核已补）

- 计划任务存活核实：`ZephyrAlpha_ProcessReaper State=Ready`；`--status` 回执
  `last_run=2026-09-25 01:47:24 dry_run=False killed=0`。写操作前提成立。
- `data/runtime/process_reaper_keep.txt` 原册**已含** `t0_rule_engine`（上一轮登记，覆盖引擎命令行）。
- 本车道补齐三条（矩阵与标签子串不在原覆盖面上）：`t0_state_match_matrix`、`lanet0_`、
  `r01_grid100bp_full_v1`。登记走 `safe_write_text` CAS（热文件纪律），
  before_sha256=`9b7df6f8…9d2497` → after_sha256=`2b3c9594…70331`，现册 195 行，进程外回读核实通过。
- 读码所得（决定本车道三条纪律，非直觉）：`classify_process` 里 **whitelist 命中先于**
  `dangerous:mem`（10GB）、`orphan_aged`（2h）、`runtime_dir_orphan`（30min）三道闸 ⇒
  ① 命中 keep 清单后**内存这件事外部不会兜底，只能自律**（故有 §3.4）；
  ② 全量跑的命令行**刻意不含 `.runtime/`**（产物走 README 规定的 `data/backtest_artifacts/…`），
     日志重定向只发生在启动器侧，不进 python 进程的 cmdline。

## 3. 限并发与内存自律（GPU T1 车道的共存约束）

### 3.1 起跑期现场
T1 搜索 `factory_grid_executor.py --stage t1` **PID 3584 存活**，WS 5.3–5.6GB 波动；
`CpuLoadPct=88%`，逻辑核 20，起跑 FreeGB 22.4（reaper watermark 口径 ram_avail 19.3）。

### 3.2 线程与调度档
- 启动器（`.runtime/tmp/t0_lane_launch.ps1`，纯 ASCII）为子进程设
  `OMP/OPENBLAS/MKL/NUMEXPR/VECLIB/ARROW = 4` 线程上限。
- 引擎新增 `--process-priority low`（**Owner 指定口径**）= BELOW_NORMAL CPU 档，
  进程内自设，回执 `{"cpu":"below_normal","applied":"below_normal_cpu"}`，
  并**落进 manifest 的 `ops` 段**（案卷可复核）。
- **不夸口**：IO 档在本机不可达——`SetProcessInformation` 对 IoPriority / MemoryPriority
  四种载荷变体一律返 `winerr=87 ERROR_INVALID_PARAMETER`（实测，非猜），
  回执如实记 `io: SetProcessInformation_failed_winerr=87`。内存真实约束由 §3.3 分批承担。
- 为何弃用启动器侧的 Win32 `Idle` 档（我第一轮试过，是错的路）：微冒烟实测
  4 只×4 规则×5 周期 = 墙钟 745.8s 只计得 CPU 552.4s ⇒ **有效核 0.74**，
  24h 长跑会长期饿在不足 1 核上。改用引擎内 BELOW_NORMAL，读写回验（§4.2 红证）。

### 3.3 批大小 50 → 20 的改判（纯执行面，非口径）
实测驱动：4 只批峰值 RSS **805MB** ⇒ 线性外推 20 只 ≈ 4.0GB、**50 只 ≈ 9.5GB**。
50 只的峰值贴着 reaper `dangerous:mem=10GB` 线，而本进程因 keep 在册**不会被杀**——
也就是说越线之后没人踩刹车，直接把 T1 的 5.6GB 挤进换页。故按"分批保守"取 20 只/批。
批大小不改任何判据结果：配对=同票同日（`build_pairs`），批只是 symbol 的切分方式，
`plan_batches` 为 sorted universe 确定性等分；批 20 与批 50 的并集恒等。批数 109 → **271**。
实测：全量运行中 RSS 稳定在 **3.49–3.52GB 不再增长**，与外推吻合。

### 3.4 内存哨兵 `--mem-cap-mb`（warn-only 默认）
全量设 5500MB 线。设计取向是**只留证据不当刽子手**：误报杀 24h 长跑比超卖更糟，
所以默认把越线写进 `data/backtest_artifacts/t0_rule_engine/t0_memalert_<tag>.log`（边沿触发，
不每 5s 刷盘）并继续跑；`--mem-cap-hard` 才自退出（码 3）。`peak_rss_mb` 由哨兵线程就地
刷新，随逐批 manifest 落盘，跑后可复核峰值。

## 4. 冒烟双证（绿证 + 能红的证尺）

### 4.1 绿证：最小样本真库真跑通
命令（产物目录刻意指到 `.runtime/tmp/` 不污染 `data/`）：

```bash
python scripts/backtest/t0_rule_engine.py --sample 4 --rule r01,r02,r03,r04 \
  --period 1,5,15,30,60 --batch-size 4 --tag lanet0_micro4 --out .runtime/tmp/lanet0_smoke
```

回执：`elapsed_seconds=745.8`，20 份 pairs parquet + manifest + stats 齐；
4 张卡哈希入 manifest（r01 `f9384361…`，r02 `68bcabfd…`，r03 `c5d4a765…`，r04 `e0f0f54e…`）；
r01/r02/r03/r04 分别产出 2009 / 861 / 2953 / 1938 对（1min）。
**Decimal 坑回归确认未退回去（就 dtype 与不炸而言）**：`run_batch` 里 bars 的 OHLCV
`astype("float64")` 在位，四规则产出的 pairs 列 `gross_bp/net_bp/vwap_buy/vwap_sell` 逐列 dtype
全为 float64，`decimal_leak=NONE`（r02/r03/r04 是向量算术腿，Decimal 一漏必炸，此处四腿全跑通即为证）。
**但该强转有代价且已实测暴露**：它使 r01 偏离材料线 M0 的逐位一致——见 §4.3（勿把本节的
"dtype 正常"读成"与预检同语料"）。
闭卷：pairs 的 `max(trade_date)=2025-09-09`，未越切点。经济值方向与预检一致
（r01 净均 −43.42bp，预检 20 只 −39.12bp，同为 M0 无信息探针 FAIL 形态，非本轮判据结论）。

### 4.2 红证：这四条都能红，所以"通过"不是假绿
| 红证 | 命令/做法 | 实测 |
|---|---|---|
| 闭卷硬拦 | `--end 2025-09-10` | `FAIL: --end 2025-09-10 越闭卷切点 2025-09-09` ⇒ 未写任何产物 |
| 周期白名单 | `--period 120` | `FAIL: 周期 [120] 不在允许集 (1,5,15,30,60)` |
| 规则白名单 | `--rule r09` | `FAIL: 未知规则 ['r09']（允许集 …）` |
| 调度档真落 | 进程内 `GetPriorityClass` 读回 | `NORMAL → BELOW_NORMAL → NORMAL` 三态可逆，非只改回执 |
| 内存哨兵不误杀 | `--mem-cap-mb 1`（远低于真实 RSS） | 打 `WARN …（warn-only，不中断）`、进程存活、证据文件落盘 ⇒ 硬退出路径与告警路径分离确证 |
| 自家改动不破交付面 | `pytest tests/backtest/test_t0_rule_engine.py + matrix + material_line` | **36 passed**（改引擎前 36 passed，改后仍 36 passed） |

### 4.3 等价复算（R01 与材料线 M0 逐行对账，口径不采信"应该一样"）
README §2 硬要求"r01 对数须与 `material_precapacity_sample20_stats.yaml` 同值"。
做法：拿预检那 20 只（`deterministic_sample` 的等距点，票单已抄进 `--symbols`，不重新抽样）
在本引擎上以 `--rule r01 --batch-size 5 --tag lanet0_smoke20_r01` 真跑，再与
`.runtime/tmp/t0_material_precap/t0_material_pairs_precap20_<P>min.parquet`
做**逐行**（symbol+trade_date 键）对账，不止比总数。

对账判据与结果（**实测已回填，结论=不逐位一致，已定位根因**）：

```bash
python scripts/backtest/t0_rule_engine.py --symbols 000001,000776,002022,002305,002596,002896,\
300146,300437,300716,301001,301316,600115,600486,600807,601619,603213,603712,688005,688316,688701 \
  --rule r01 --period 1,5,15,30,60 --batch-size 5 --tag lanet0_smoke20_r01 \
  --out .runtime/tmp/lanet0_smoke --process-priority low --mem-cap-mb 2500
```

| 周期 | 材料线 M0 基线 n_pairs | 引擎 R01 n_pairs | 净均 bp（基线 → 引擎） | 前置≥30bp 占比 | 判定 |
|---|---|---|---|---|---|
| 1min | 11332 | 11337 | −39.12 → −38.96（+0.16） | 59.02 → 59.10 | 键差 5、值差若干 ⇒ **不逐位一致** |
| 5min | 11332 | 11337 | −40.75 → −40.62（+0.13） | 57.74 → 57.80 | 同上 |
| 15min | 11328 | 11333 | −38.41 → −38.32（+0.09） | 55.92 → 55.98 | 同上 |
| 30min | 11325 | 11330 | −38.14 → −38.04（+0.10） | 53.59 → 53.65 | 同上 |
| 60min | 11317 | 11322 | −37.85 → −37.75（+0.09） | 50.46 → 50.52 | 同上 |
| 合计 | 56,634 | 56,659 | — | — | 受影响 pair 累计 **58 条 = 0.102%** |

**先排除数据漂移**（零成本只读探针）：同一 20 只、同一窗，当前 CH 直查
`count()=4,615,139 / uniqExact(symbol,trade_date,trade_time)=4,615,139 / 975 日 / 20 只`
——与预检记录**逐位相同** ⇒ 差异不在源数据面。

**根因已定位并做可重放实验（不是推测）**：差异来自 `run_batch` 里那句全表
`bars[["open","high","low","close","volume"]].astype("float64")`（上一轮为修 r02/r03/r04 的
Decimal 向量算术炸而加的全局强转）。对 4 个分歧 symbol-day 分别用两条腿跑**同一个**
`t0_material_line.run_model_m0`：

| symbol\|date | Decimal 腿（=材料线路径） | float64 腿（=引擎路径） | 盘上 parquet 实际 |
|---|---|---|---|
| 000776\|2023-06-20 | `no_touch` 不出对 | `pair` gross 26.94 | 基线 ABSENT → 引擎 26.94 |
| 300146\|2023-09-14 | `no_touch` 不出对 | `pair` gross 74.43 | 基线 ABSENT → 引擎 74.43 |
| 601619\|2022-04-13 | `pair` gross −75.76 | `pair` gross 100.00 | −75.76 → 100.00 |
| 688316\|2023-06-20 | `pair` gross −293.56 | `pair` gross 132.58 | −293.56 → 132.58 |

⇒ **两腿分别逐位复现各自一侧的盘上产物**，全局强转是唯一差异源：`low <= base×0.99` 这类
边界判定的双方一侧被 float64 二进制舍入翻转（价格 2 位小数的精确比较在 Decimal 下才是经济真值，
float64 会造出**非真实的边界命中**，本样本 5 例"多出的对"皆属此类）。

旁证本次对账同时**复算通过**：Decimal 腿的 1min 净均 = **−39.12bp**，与预检报告写死的
−39.12bp 同值 ⇒ 预检件本身没造料，差异纯在引擎侧。

判读与处置（交总筹裁，本车道未自决）：
1. **影响量级已界**：0.102% 的 pair、净均 ≤+0.16bp、前置命中与胜率 ≤+0.08pp，
   不改变"M0 无信息探针在 frozen 判据下 FAIL"的方向；但**语料不是同一件**，
   引擎头注与设计册 §1 的"R01 与 M0 同参同模型/逐位一致"一句**按交付态不成立**，不得引用为已证。
2. **修法**（外科且零成本择时）：把全局 `astype` 改为**按规则分腿**——r01 传未转的 Decimal bars
   （恢复与 M0 逐位一致），r02/r03/r04 保留 float64（它们确需向量算术）。
3. **代价**：改后 r01 结果会变 ⇒ 今晚已跑的 float64 批不可与新批混用同 tag，须**换新 tag 全量重跑**。
   若分层裁定走"向量化改造后重算"（§5.3 方案 2），本修可在同一轮零额外代价并入；
   若裁定维持现跑，则本件与矩阵 meta 须带上"float64 基线、边界 0.1% 已知偏差"的显式披露，
   不得让下游以为等价于预检语料。


## 5. 全量跑：参数、实测吞吐、ETA 与分层触发申报

### 5.1 起跑命令（可复算，逐字）

```bash
python scripts/backtest/t0_rule_engine.py --rule r01 --period 1,5,15,30,60 \
  --batch-size 20 --tag r01_grid100bp_full_v1 --resume \
  --process-priority low --mem-cap-mb 5500
# 启动方式：.runtime/tmp/t0_lane_launch.ps1（Start-Process 脱管，Threads=4，Priority=BelowNormal）
# 日志：.runtime/logs/lanet0_full_v1.{out,err}.log ; 内存峰值证据：data/backtest_artifacts/t0_rule_engine/t0_memalert_r01_grid100bp_full_v1.log
# 产物：data/backtest_artifacts/t0_rule_engine/t0_rule_{manifest|pairs|stats}_r01_grid100bp_full_v1*（README §1 规定目录，禁 glob 消费，禁 summary.json）
```

规则面 = **1 规则（R01，卡 status=frozen_for_v1_run）× 5 周期**，与设计册 §4 报备一致；
R02/R03/R04 仍停在 `registered_not_precap`，本车道**未跑、未扩、未改卡**。

### 5.2 实测吞吐与 ETA
- 批 0（20 只，含 sorted universe 列举与首次数取）：**elapsed_s=1084.9**，
  pairs = 1min 10463 / 5min 10461 / 15min 10454 / 30min 10445 / 60min 10438。
- **稳态单价（用累计 elapsed 差分，非首批外推）**：批 1 增量 **812.1s**、批 2 增量 **939.4s**
  ⇒ 均值 ≈**876s/20 只批**（≈43.8s/只墙钟）。
  271 批 × 876s ⇒ **全程 ≈66h 墙钟**（批 0 的 1084.9s 含冷启动，不用于定 ETA）。
  该单价是在与等价复算跑（§4.3）争抢 below-normal 份额期间测得；复算跑已于 elapsed 1432s 收尾，
  独享后单价应更好，明晨复核后回填。
- 并行侧证：复算跑 5 只/批增量 408.8 → 313.7 → 363.9s，两跑互抢 ⇒ "只数份额"随并发数变化。
- 内存实测（哨兵自采，写进 manifest 的 `ops.mem_watchdog.peak_rss_mb`）：**4078.9MB**，
  与 §3.3 的"20 只 ≈4.0GB"外推吻合，全程**未越** 5500MB 线
  （`t0_memalert_r01_grid100bp_full_v1.log` **不存在** = 零越线的正向证据，非默认缺件）。
  50 只/批按同斜率 ≈9.95GB，会贴着 reaper `dangerous:mem=10GB` 线跑 ⇒ 改小批的决定被实测追认。
- T1 共存核查：全程 `factory_grid_executor --stage t1` PID 3584 存活，WS 在 4.0–5.6GB 波动
  （非单调下滑），系统 FreeGB 稳定 14.6–17.7，未把 T1 挤死。
- 对照预检报备的 23.3h：差在**有效核 + 引擎 CPU 成本**。按 CPU 秒口径批 0 ≈690s CPU/20 只 ⇒
  全程 ≈52h CPU，而预检建模 21.4h + 取数 1.9h；即本引擎在同一 r01×5 工作上的
  CPU 成本约为材料线的 **2 倍**（`list(bars.groupby())` 全量物化 + 批内重分组是首要嫌疑，
  未做归因实验，不写死结论）。



### 5.3 分层触发申报（交总筹裁，本车道未自决）
17 号文 §三.1 的硬规矩是"容量预检报告先行，超 48h CPU 预算即分层"。
**实测已越过 48h 线**。设计册 §4 已预注册的三条分层路径，本车道按可用性排序：

1. **按周期分层 {1,5}min 先行**（信息主轴）：≈33h 墙钟即可出 1/5 与 5/5 两套矩阵，
   与 D2 主视图的"周期轴"判读主轴重合；15/30/60 次批续跑（`--resume` + 新 tag 天然兼容）。
2. **向量化改造**（≥10×，属优化不属前置）：改点是 `run_batch` 的分组物化与
   `resample_period` 的逐日 `iloc` 循环；改后须重跑 36 例测试 + 重做 §4.3 等价复算才可采信。
3. 按规则串行分夜：对 v1（1 规则）不适用，留给 R02–R04 扩面夜。

**本车道选择：不放量、不改卡、不改判据，维持全量跑并如实报 ETA**，等总筹对 1/2 的裁定；
若裁定走方案 1，现有 271 批产物可无缝按周期切次集消费（pairs 文件名自带 `_<P>min` 段）。

## 6. 匹配矩阵与维面（语料齐了才算，现零格不出判据）

矩阵侧命令（继承设计册 §2 逐字不改）：

```bash
python scripts/backtest/t0_state_match_matrix.py \
  --manifest data/backtest_artifacts/t0_rule_engine/t0_rule_manifest_r01_grid100bp_full_v1.yaml \
  --out-dir docs/_working/decision_map_campaign_20260924/links/L05_t0 --tag v1
```

产物 = `t0_state_match_matrix_v1.csv`（全交叉六轴四元组）+
`t0_state_match_phase_period_v1.csv`（D2 主视图）+
`t0_state_match_phase_coverage_v1.csv`（逐相位样本数披露，17 §三.5）+
`t0_state_match_meta_v1.yaml`（口径/输入哈希/重算命令）。

- **新闻十分位维：维持阻断登记**，不造料。研究窗 per-symbol 新闻标注=0 条的实测证据
  在设计册 §3.4（2026-09-26 CH 直查），本车道复核了矩阵侧的落地面：`news_axis` 列
  = 常量 `blocked_no_pit_symbol_news`，解锁前提=per-symbol 标注回填 + 发布时点（PIT）审计先行。
  **未使用标题模糊匹配**（D-7/D-3 同构禁手）。
- 市值五分位维：矩阵侧走 `stock_daily_basic` T-1 `circ_mv` 日截面分位（PIT 对齐），
  零行即 `SystemExit("FAIL: stock_daily_basic 研究窗零行——市值轴不可构建，禁造料")`，不静默降级。
- 相位维 / 板块族维的已知非 PIT 缺口（板块族单快照）继承设计册 §3.3 与 §6 债项，未新立口径。

### 6.1 矩阵排练件（在 3/271 批的部分语料上真跑，只为拆雷不为出数）
目的：把"全量跑完才发现矩阵侧死掉"的风险前移。产物**刻意不落真源目录**（写
`.runtime/tmp/lanet0_matrix_rehearsal/`，tag=`lanet0_rehearsal`），防被误当 v1 交付件消费。

```bash
python scripts/backtest/t0_state_match_matrix.py \
  --manifest data/backtest_artifacts/t0_rule_engine/t0_rule_manifest_r01_grid100bp_full_v1.yaml \
  --out-dir .runtime/tmp/lanet0_matrix_rehearsal --tag lanet0_rehearsal
# 回执：pairs=159526 cells=2085 phase_period_cells=30（零异常退出）
```

排练确证的四条纪律（都是"能红"的口径闸，逐条实测）：
1. 相位轴可读：`six_phase_history_v1.csv` sha256=`45e489beea157149…`，窗内 rows=975 /
   routed=496 ⇒ 相位格、板块族格、市值五分位格三轴都跑通，**`circ_mv` 那条 Decimal 高危查询未炸**。
2. 新闻维落地形态确证：`news_axis` 全表唯一值 = `blocked_no_pit_symbol_news`（阻断维未造料）。
3. 禁并格闸确证：`n<30` 的格 **820** 个，`verdict=insufficient_no_merge` 亦 **820** 个，
   逐一对齐零漏判（不是"应该有"，是数出来相等）。
4. 闭卷双闸确证：矩阵侧 `max(trade_date)=2025-09-09` 断言通过；unrouted 单列 **479 日 / 15,146 对**
   独立成行，未并入任何相位（占比 49%，与设计册 §6.3"约 40%+"相容）。

**排练又抓出一处口径缺口（新发现，交裁）**：设计册 §3.3 写"ignition 全史 2 日 ⇒ 其格如实
INSUFFICIENT"，实测该预期**在本研究窗内不可实现**——直查相位真源：ignition 全史恰 2 日
（`2019-04-08` 与 `2026-06-23`，均 routed=1，与设计册"全史 2 日"吻合），但**两日均在研究窗外**
（前者早于分钟库起点 2021-09-01，后者晚于闭卷切点 2025-09-09）⇒ 研究窗内 ignition 路由日 = **0**。
`groupby` 对空组不出行 ⇒ 矩阵与逐相位披露件里**根本没有 ignition 这一行**（既非 ok 也非
insufficient，而是静默缺席）。窗内实际相位分布：expansion 182 / distribution 118 /
capitulation 88 / accumulation 87 / euphoria 21 / **ignition 0**（routed 合计 496，余 479 日 unrouted）。
17 号文 §三.5 要求"披露各相位样本数"，缺席行不等于 INSUFFICIENT 行：下游读表者无从区分
"该相位样本不足"与"该相位没进表"。修法二选一（属矩阵件口径面，本车道未夜改）：
披露件按 `PHASES_ORDER` 全集补零行，或在 meta 显式记 `ignition: 0 routed_days in window`；
同时设计册 §3.3 那句宜改为"ignition 在研究窗内不存在（全史 2 日均越窗）"，免后人再去凑一个不可能有的格。
（顺带确证：矩阵 `load_phase_map` 对 `trade_date <= 2025-09-09` 的过滤有效——
真源里那条 2026-06-23 的 ignition 行**未泄漏进研究面**。）


⚠️ 排练件禁判读：其胜率/Wilson LB 建立在 1.1% 的语料（3/271 批）上，且承 §4.3 的 float64 基线，
**不得**据以引任何方法有无信息的结论；本节只证"管子通、闸在位"。


## 7. 本车道发现的上游缺陷与风险（只登记，不代修他人车道面）

1. **指令前提被证伪（已按等价实现并上报）**：Owner 侧口径点名的
   `process_extrema.set_process_priority` 在本仓**不存在**——
   `src/zephyr/shared/infra/process_extrema.py` 无此文件，全库 `set_process_priority` /
   `process_extrema` 两串 ripgrep **零命中**。本车道在 `t0_rule_engine.py` 内实现等价能力
   （`set_process_priority()` + `start_mem_watchdog()`），是否抽象为共享件交治理裁。
   另一处口径纠偏：reaper 的 `classify_process` 里**没有任何优先级判定**
   （Idle 不是"孤儿资源占用缓解"的触发条件）；Idle 的真实危害是**被调度饿死**（实测 0.74 核）。
2. **矩阵引擎的相位真源在已死会话的 worktree 里，不在 HEAD**：
   `SIX_PHASE_CSV` 指向 `.worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/six_phase_history_v1.csv`
   （该件实测存在，92,451 字节，2026-09-24 06:41），而主仓 `docs/_working/t0_matrix/` 下**没有**此件。
   ⇒ 相位轴（B4 六段真源）尚未落地，worktree 一旦被清理，矩阵直接 `SystemExit`。
   本车道**未改路径也未复制造第二真源**，只登记：落地车道须把该 CSV 连同 `.meta.yaml`
   归位 HEAD，之后把 `SIX_PHASE_CSV` 改指主仓。矩阵侧会把它自己的 sha256 写进 meta，可复核。
3. **续跑一致性闸缺失（已补，本车道利益相关）**：`--resume` 复用 `batches_done` 的键是**批序号**，
   而序号由 `batch_size/窗/规则/周期` 决定；原实现只比对卡哈希。⇒ 同 tag 换批大小续跑会让
   同一序号指向另一批 symbol，**语料静默漏算/重算**。现补 `plan_keys` 漂移即 `SystemExit`，
   且刻意不比 `ops`（跑中改调度档救火是合法动作）。补闸后 36 例测试仍全绿。
4. **吞吐报备低估 ~2.4 倍**（§5.2）：预检外推 23.3h，实测 52h CPU / 81.7h 墙钟。
   预检报告自述"外推禁当精确实测引用，正式跑以首批实测复核"——本轮就是那次复核，
   数字如实回填给总筹，不改预检件本体。
5. 次要：manifest 键 `created_batch_run` 实为"批数"，命名易误读（未改，改了会触发卡哈希外的
   manifest 结构漂移，留待落地车道一并裁）。
6. **CREATE-GUARD 登记被热册蒸发挡住（阻塞本车道落地，非本车道成因）**：
   两件新建件的 creation_token 登记被 `batch_creation_tokens.py` 的写前守恒闸拦下（fail-safe 零写入），
   真因=`capability_canonical_file_registry.yaml` 盘上相对 HEAD 缺 4 条他会话 `commit-speedup-*` 条目。
   只读探针定性：4 条逐一 `git show HEAD:册` vs 盘上 grep ⇒ **HEAD=1 / DISK=0 ×4**，
   行数 HEAD=50897 / DISK=50876，且该册 `git status --porcelain` 显示已被他会话 **staged**。
   本车道不代修（政策 §3.4 owner 责任制 + 主区改热册已知死法 + 任务书禁 git 写），
   修复与重跑命令已逐字写进 `landing/lane_t0.yaml` 的 `blocking_issues`。
   附带工具缺陷：该脚本只有 `--prefix` 无单件旗，目录前缀实测会卷入 23 条错挂 capability；
   "拿文件全路径当路径前缀"可定域到恰 1 条（已验），是否固化成交路交治理裁。
7. **【最高优先】引擎自述不变量在交付态不成立**：`t0_rule_engine.py` 头注与设计册 §1 声明
   "R01 与 t0_material_line M0 同参同模型 / 同参逐位一致由测试钉住"，实测**不成立**——
   全局 `astype("float64")` 使 `low <= base×0.99` 型边界判定翻转，0.102% pair 受影响（§4.3 有
   可重放实验与两侧逐位复现）。根因是"13 例测试"只测了构造数据上的函数等价，
   **没测过真库 bars 的 dtype 路径**（构造数据本就喂 float，天然测不出这个差）。
   ⇒ 落地车道二选一：把 `astype` 改成按规则分腿（r01 用 Decimal 腿恢复逐位一致），
   或把该句声明从头注/设计册删改为"float64 基线，边界 0.1% 已知偏差"；
   **禁现状不动地把今晚语料当"与预检同基线"下游消费**（这才是本条的真风险）。



## 8. 规则卡是否扩面：本车道建议**不扩**，候选交裁

任务书允许我判断能否规则卡化更多（不违"先卡后跑"），但扩卡=改判据面，故只登记候选不自跑：

- 候选 A｜R01 网格扩档 {50, 200}bp：**否决**。属成交模型参数面变更（预检 §四.4 明令禁临场加档），
  且 3 档×5 周期 ≈66h 已判触发分层；须修卡重开 + 独立容量预检。
- 候选 B｜R02 状态门变体（带宽=f(状态, 情绪段)）：**否决**。卡在 D-14 词表悬案与"自由度≈1"
  未裁，裁前禁两维展开（设计册 §6.4）。
- 候选 C｜R04 的 OR 窗口 K 档扩展：**存疑交裁**。会引入新的自由度，需先报备再预检。
- 候选 D｜34 法"7 可考"族剩余分钟可落地子集：本车道**未新建卡**；
  已排除清单（5.4 tick 面 / 9.1 GBM / 9.3 因子族）维持设计册 §4 登记不动。
- 真正**零成本**的扩面不在卡面而在矩阵面：R01 语料一旦齐，按 相位×周期×板块族×市值五分位
  的交叉分层已由现有 4 轴覆盖，不需要新卡。⇒ 本轮的瓶颈是吞吐，不是规则数。

## 9. 待落清单与纪律

- 待落清单：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/landing/lane_t0.yaml`
  （lane / session_id / files / note）。
- 本车道**未做任何 git 写操作**（无 add / commit / push / git_commit.py / commit_queue enqueue），
  唯一落地出口=总筹指定的落地车道。
- 改前 claim 已走 `lock_files.py acquire scripts/backtest/t0_rule_engine.py lane-t0-20260926`
  （回执 `ACQUIRED`，TTL 30min，过期需重 claim）；收尾释放走 `git_commit.py --release-only` 由落地车道执行。
- 主区直改（非 worktree）的原因登记：任务书严禁本车道 git 操作，而引擎改动必须先于起跑落地，
  worktree 分支路径下产物目录与 manifest 锚点均不共享 ⇒ 降级为主区改 + 只写不改提。GW 计数与周审计按政策走。
- 数据库访问全程 `zephyr.infrastructure.database_service.DatabaseService`，零裸 duckdb/裸 ClickHouse；
  本件所有"库里有数/无数"的判断均以引擎真跑产物与耐久统计件为据，未用 `ch_writer.query` 的空串作"无数据"判据。
- 每个"通过"结论都配了能红的证尺（§4.2 六条）；未跑完不算失败，**§4.3/§5.2 未回填项一律标"待补"**，
  不出假绿。
