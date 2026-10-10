---
ttl: task_bound
title: 引擎 GPU 化·终报与验收判定（st-gpux-20261011）
created: "2026-10-11"
sid: st-gpux-20261011
family_id: GPUFEED-CAMPAIGN
lane: LANE-GPUX
evidence_grade: A（全部结论带真实面板双跑产物或 cProfile 帧；未达项也给了实测数）
---

# 终报（st-gpux-20261011，工单「引擎 GPU 化工单」）

## 〇、一句话与大白话

**一句话**：eval 面确实搬上了卡并且数值可证等价（单进程 eval 3.55x、199 格排名 Spearman ρ=1.0），
但工单两条验收线——**探索吞吐 ≥3x 与 GPU 持续利用率 ≥70%——今晚实测未达标**（6 路并发聚合折算约
1.1x，本进程归因 SM 均值 3.5%），根因不是"没搬上去"，而是**"每格一 kernel"这种搬法在并发下喂不饱卡**；
设备已按缺省关（`--eval-backend cpu`）入库，不会有人误吃这条路径。

**大白话**（给 Owner，不带行话）：
- 我们原来想的是"这台电脑的显卡在闲着，把算得的活分给它就快了"。今晚把最重的那块活（给股票打分排序）
  真的搬上显卡了，一个人干的时候确实快了 2-3 倍。
- 但**同时开 6 个工人去用同一张卡**时，每个人都要排队等卡，而且每人给卡开的"工位"（CUDA 上下文）
  光占地方就吃掉 12GB/24GB 显存——结果 6 个人加起来反而比原来在 CPU 上慢。
- 打个比方：不是"厨房没灶"，是**每人只做一道菜就喊一次灶**，灶火 90% 时间在等；要达标必须
  "一次端 50 道菜进灶"（把共用同一批数据的许多格合并成一次批量计算），这是下一班要造的家伙，
  不是今晚再调调参数能出来的。
- 还有一件更要紧的事：原本用来判"卡有没有被喂饱"的那把尺（nvidia-smi 的利用率）**本身会被桌面图形
  污染**——我实测开着零计算时它也能显示 8-57%。要是直接拿它当验收尺，我可以很轻松地"做出"70% 的假绿。
  今晚把这把尺换成了"只认我们引擎自己那份占用"的版本，所以现在的 3.5% 是**真数**，不是没测到。

## 一、验收判定（工单 §四 逐项，含实测数）

| 验收项 | 线 | 今晚实测 | 判定 |
|---|---|---|---|
| 探索负载吞吐 | ≥3x | 单分片配对：**3.00x**（循环段 408s→136s，200 格）；6 分片并发：按今晨 p2 的命中结构折算 **≈1.1x**（实测 18,264 格/时 < p2 CPU 32,900 格/时） | **未达标** |
| GPU 持续利用率 | ≥70%（窗内采样曲线） | 本进程归因 SM：均值 **3.5%**，p50 3%，max 8%，48 枚设备级采样 + 36 枚归因采样中 **≥70% 者 0 枚**；设备级 util 均值 24.1%（含桌面图形噪声，不可归因） | **未达标** |
| 三级影子阶梯容差全绿 | 8→200→1000 双绿 | 级 1（8 格）：**五项指标逐位等 PASS**；级 2（200 格）：**四项 PASS + max_drawdown 1 格越线 FAIL**；级 3（1000 格）：**未跑**（见 §三） | **未达（且级 2 有实质越线）** |
| 终报含基线对比曲线 | 必交 | 本件 §二 + `01_gpux_t0_profile.md` §四（今晨断流前的采样曲线即"改前"基线） | 交付 |

**红线自查**：判据面零动（阈值/门/抽样/manifest 列一律未改）✓；等价协议未全绿⇒**未进生产路径**，
`--eval-backend` 缺省 `cpu`、原路逐字节零漂移 ✓；探索/考试分账纪律：三次跑批全带
`--exploration-ledger` 且分册写本班 tmp（`conc6/scan_s{i}.jsonl` 六行 `kind:"exploration_scan"`），
N 账本零混入 ✓；CPU 回退路径保留 ✓；与 CH/夜跑互让：起批前实测无 tilib/backfill/grid 进程在飞 ✓
（本班未动 `exclusive_group` 面，见 §三 呈批项 ③）。

## 二、今晚真交付了什么（三清单之一：交付面）

| # | 件 | 内容 | 证据 |
|---|---|---|---|
| 1 | `src/zephyr/backtest/gpu_core.py` +426/−0 | eval 面设备核全套（单 xp 码路径、FP64）+ `nvml_process_util()` 归因尺 | 试件新增 37 支用例全绿；`test_gpu_core_parity.py` 无新增红 |
| 2 | `scripts/backtest/factory_grid_executor.py` +385/−52 | `--eval-backend` 开关（缺省 cpu）＋前缀/单格两级分流＋串行交接点＋心跳归因三键；`_ic_weight_frame`/`_FREQ_STEPS`/`_LAMBDA_PEN` 上提共用 | 删除面 52 行逐条对上账（02 件 §三，含可复现自证命令） |
| 3 | `tests/research/backtest/test_l2_gpu_landing.py` +555/−0 | 20 支新试件函数（采集面 39 支用例）：层1 逐位、层2 ≤1e-12、七形态定尺寸、IC 切分面、口径双向钉、降级不杀格 | 69 passed（4 支试件文件合跑），红集合=dev 同 6 支预存红 |
| 4 | `tests/research/backtest/test_factory_grid_instruments.py` +13/−3 | 心跳采样三元组契约（归因不可用时**禁伪造 0**） | 6 passed |
| 5 | 01/02/03 三件账袋 | T0/T1 实测、T2 采用、T3 阶梯与越线定位、验收判定 | 本家族目录 |
| 6 | 缺陷当班修 | `bool(ndarray)` 杀 6/8 考格、`cupy.fmin.reduce` 未实现致 44 格白回退、drift_band 换序、industsize 组均值口径、无锚列负索引 | 02 件 §四 D-1..D-7，各配试件 |

## 三、未达的原因分解与下一班入口（三清单之二：残余）

**为什么搬上卡却没到 3x（三条都有数）**：

1. **Amdahl 帽**：eval 只占格耗时 82%；单格剩余 CPU 侧（bt 0.107s + 五档成本门 + 编排 + 把设备结果
   物化回 pandas）构成地板。级 2 GPU 的 hit 格 tot=0.184s 里 eval 只占 0.127s ⇒ 就算 eval 归零也只有 ~1.8x。
2. **并发争用**：6 分片把 hit 格单格耗时从 0.184s 撑到 0.487s（2.6x），且 **6 个 CUDA 上下文常驻吃掉
   12,171MiB/24576MiB** 显存——这与 `search_space_prereg.yaml:106 vram.concurrency: 1`（"单卡禁共存"）
   的在册口径正面冲突，也在挤压本地 LLM 预算。
3. **"每格一 kernel"喂不饱卡**：单格设备时长 ~0.02-0.05s，中间全是 CPU 空隙 ⇒ 归因 SM 只有 3.5%。
   这正是 `00_gpufeed_report.md §五 T2-D`（多 worker 喂单 GPU 流/异步流水线）与
   `p1_wiring_benchmark.md §五` 当年立为候补、至今未造的那件家伙。

**下一班入口（按性价比排序，本班不代做）**：

| 入口 | 要干什么 | 预期 | 前置 |
|---|---|---|---|
| N-1 批并行核 | 同前缀 N 格合成 (N,T,S) 一次算完（top_n/sizing/cap 全批化），一次 launch 干 50-200 格的活 | 唯一能让"≥70% + ≥3x"同时成立的路；把每格设备时长从 0.03s 抬到 1-3s | 需先定 N 的显存预算（现 40MB/面板） |
| N-2 权重直供 bt | 设备权重不 D2H、不建 DataFrame，直接喂 `gpu_core.tensor_core` | 去掉 hit 格 0.06s 的主机侧固定开销 + 免 19ms/格 D2H | 等形守卫（`_c4_engine` 索引/列等形判定） |
| N-3 级 3 补跑 | 6 分片 × 25,000 格（复刻 p2 池几何）双后端配对，约 50 分钟/侧 | 给出真并发下的聚合倍数；现在 1.1x 是外推不是实测 | 日历窗问闸 + `--exploration-ledger` 分册 + reaper keep 登记 |
| N-4 越线那格 | 3 格近并列翻转的处置：或把设备前缀限定在 top_n 不敏感的形态，或提呈 max_drawdown 线的绝对地板 | 让级 2 能名正言顺绿 | **属主/裁定通道**（见 §四） |

## 四、呈批与不自决项（三清单之三）

Owner 只需在下面几格里回话；本班一律不自裁：

| # | 事项 | 为什么需要您 | 不回话的后果 |
|---|---|---|---|
| ① | 验收未达标要不要**续投一晚**（N-1 批并行核是 1-2 天工程，非 tweaks） | 涉及排产优先级：今晚的结论是"方向对、家伙不对"，续投=再造一层 | GPU 化停在"等价但更慢"的半成品态；缺省关着不出错，但 24G 卡继续闲着 |
| ② | `max_drawdown` 相对线（1e-4）要不要补一条**绝对地板**并写明"top_n 敏感格另判" | 这是**判据面/容差线**，改它必须您或裁定通道点头，本班不碰 | 级 2 永远因 1/199 的近并列翻转不绿；有人可能为了"过线"去动卡（错的方向） |
| ③ | 执行器是否挂进 `exclusive_group=gpu_default`，或把 `vram.concurrency` 改成"允许多路"并写明预算 | 排班资源政策（6 路实测已在发生，但册上仍写 1，属纪律与现实的矛盾） | 并发跑批继续靠临时看门狗让路，在册口径与现实不符 |
| ④ | `#ARCH-TORCH-CPU-ONLY` 与本机实装 torch 2.13.0+cu126 的漂移要不要处理 | 架构裁定面；本班已按 CuPy 施工，未用 torch | 后人可能误以为 torch 可用而绕开在册载体 |

## 五、本班自犯并如实上报的（不藏）

1. 主区直接编辑共享件（违 RULE-WORKTREE 默认）→ 已搬进车道、主区 `git status` 复核为空。
2. 第一版归因自测判据写错（denormal 浮点通过 `0<x<=100`）→ 当场报了"尺可用:True"的假绿；
   已改三阶段对照实测。
3. 开局据单格首行读数就下"回测核占 81%"的口头判断 → 全量聚合后自我推翻（首格=装载预热伪影）。
4. 两次 Edit 锚点吞结构：`def _normalize(` 的换行、`--verify-counts` 的 `ap.add_argument(` 开头、
   以及一处旧试件体残留三行——**全部由编译/试件当场抓到**，未流入产物。
5. 双跑探针自身两只坑（`combine_cache` 传两遍被 run_batch 吞成阴性；git-bash 路径 `/d/…` 交
   Windows python 打不开）→ 未用假成功的探针下结论，改由已有产物 + 合成口径钉出诊断。

## 六、复核命令

```bash
# 试件全绿面（车道内，PYTHONPATH 必指车道）
cd D:/ZephyrAlpha/.worktrees/st-gpux-20261011
export PYTHONPATH=$PWD/src;$PWD
python -m pytest tests/research/backtest/test_l2_gpu_landing.py \
  tests/research/backtest/test_gpu_core_parity.py \
  tests/research/backtest/test_c4_engine_gpu_wiring.py \
  tests/research/backtest/test_factory_grid_instruments.py -q     # 应 69 passed + 同 6 支预存红
# 阶梯产物（级1 与级2）
ls data/strategy_intake/grid_20261011-032628 data/strategy_intake/grid_20261011-034706 \
   data/strategy_intake/grid_20261011-034911 data/strategy_intake/grid_20261011-035629 \
   data/strategy_intake/grid_20261011-040137_s*of6
# 归因尺自测（证明它能红：CPU-only 不入计算表 / 忙时上升 / 停算回落）
python .runtime/tmp/st-gpux-20261011/meter_validate.py
# 分账红线（六行探索扫描记录，N 账本无 exploration:* 条目）
cat /d/ZephyrAlpha/.runtime/tmp/st-gpux-20261011/conc6/scan_s*.jsonl
```
