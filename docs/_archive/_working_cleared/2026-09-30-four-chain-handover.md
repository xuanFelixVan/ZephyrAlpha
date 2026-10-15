---
archived_doc_type: handover
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
title: 四链路建设体检 · 交接文档
date: 2026-09-30
rebuilt: 2026-10-14（原版灭失，从工作区记忆重建 + 并入 10-14 复核结果）
session: workbuddy-external-audit-20260930
status: delivered
scope: 只读审计（未做任何代码改动；10-14 收口仅重建本文件并 git add）
note: 本文件 09-30 原版为未跟踪文件，在 10-01~10-14 期间蒸发灭失（既不在磁盘也不在 git）。
      本版为重建版，已 git add 入索引防二次蒸发；正式入 HEAD 需走 scripts/git_commit.py。
基线: 09-30 主树 dev @ 9938b2ed8b / 10-14 主树 dev @ c100cb43c3
---

# ZephyrAlpha 四链路建设体检 · 交接文档

> ⚠️ **本文件是 2026-10-14 重建版。** 09-30 原版因从未 `git add`（未跟踪状态）在项目日常
> 活动中蒸发灭失——这正是本仓库记录在案的"untracked 产物蒸发"连环案（`10_evaporation_forensics.md`）。
> 重建内容来自 `.workbuddy/memory/2026-09-30.md` + `MEMORY.md`，并补入 10-14 的复核结果。

---

## §0 · 10-14 收口复核（14 天后的现状）

主树已从 `9938b2ed8b` 推进到 `c100cb43c3`，660 个未提交改动在途。三条关键复核：

| 09-30 时的状态 | 10-14 现状 | 判定 |
|---|---|---|
| gpu_core 锁在 worktree 未合入主树（299 行） | **`src/zephyr/backtest/gpu_core.py` 已入主树，68,568 字节（10-13 21:59），已 git 跟踪，9+ 处生产消费方** | ✅ **已解决且远超预期** |
| `c4_batch_due` 自 09-16 积压 2 条 attempts=0 | 旧 2 条**已清除**；但新增 3 条（10-01 85 件 / 10-08 2 件 / 10-12 4 件）attempts 仍=0 | ⚠️ **部分缓解，仍在积压** |
| `GRADUATED_PACKAGES` 恒空（裁定#305） | **仍恒空**（`daily_decision_orchestrator.py:125`） | ❌ **未变，整装回测仍结构性空转** |

### GPU 侧的重大进展（值得单独说）

`gpu_core.py` 已从 299 行膨胀到 68KB，且**不再是"写了没接线"**：

- 已 git 跟踪（`git ls-files` 命中）
- 生产消费方 9 处：`_c4_engine.py:192/649/719/779`、`factory_grid_executor.py:994/1001/2196/2541/3071`、
  `src/zephyr/backtest/__init__.py:60`
- 头注 `[CONSUMERS]` 明示三路：`_c4_engine`（P1 接线/L2-B）、`factory_grid_executor`（L2-C --engine 三态透传）、
  `l2_bench_probe`（L2 终验探针）
- **已进入 L2 阶段**：RawKernel 融合扫描 `fillability_gate_scan`（一 thread 一列、时间轴寄存器内推进，
  T 次小 kernel → 1 次）——**正面解决**了 09-30 那份基准里"hs300/zz500 反而慢 0.25-0.53x"的
  kernel-launch 税问题；MOD-BT-232 god 区收编、L2-E 双核归一
- 测试已从 `tests/backtest/` 迁到 `tests/research/backtest/`（parity + l2_gpu_landing）

→ **09-30 那份"小尺寸上 GPU 反而慢"的基准已经过时**，新架构专治此病。若还要引用加速比，
请以 `docs/_working/gpu_rewrite/` 下的 L2 新基准为准。

### 新增的一条故障（09-30 时不存在）

```
PIPE-20261011-084204-336356  kind=t0_condition_pack_due
attempts=4  poison=true
last_error: AttributeError: 'NoneType' object has no attribute 'close'
```
这条**已被标记为 poison（死信）**，不会再自动重试，需要人工介入。属新发现的遗留项。

---

## 〇、一键复制：新会话开场指令

> 复制整段作为新会话第一条消息。

```
你是 ZephyrAlpha 项目的接续执行会话。项目根目录 D:/ZephyrAlpha（Windows + Python 3.12）。

【背景】我是 Owner。09-30 做了一轮"四链路建设体检"（只读审计），10-14 复核并重建了交接文档：
D:/ZephyrAlpha/docs/_working/2026-09-30-four-chain-handover.md。请先完整读这份文档。

【你的任务】按该文档 §5/§6/§7 章的遗留任务、待裁定任务、剩余任务清单推进工作。
不要重复已完成的事（见 §4 与 §0 复核）。

【入场必做（不可跳过）】
1. 先读 docs/01_policies_and_standards/sop/backtest_system_sop/ 下的 README+A+B+C+D 五册（回测体系真源）。
2. 按 AGENTS.md §0 冷启动序列执行：RULE-ENV（Python 3.12 PATH 修正）→ RULE-GUARDIAN
   （reaper 计划任务存活核验，不存在则禁止任何写操作）→ RULE-WORKTREE → RULE-CAPABILITY-LOOKUP。
3. 施工前必读：docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md
   与 docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md。
4. 提交一律走 scripts/git_commit.py，禁止裸 git commit。

【纪律红线】
- 不确定的事先查真源，不要凭记忆写路径（用 python -m zephyr.library.lookup 或 ROOR 解析）。
- 破坏性操作三步验证（必要性/真实性/可逆性）；判重禁用聚合数。
- 涉及 Owner 门位的（生产流转/注册表净删/flag 翻转/资金操作）必须停下来问我。
- 只读区（scripts/ch、scripts/backup、disk_reorg_campaign）不要碰。
- 【血泪教训】新建文件必须 git add 入索引，禁止让交付文档长期停留在未跟踪状态——
  本交接文档的 09-30 原版就是这么蒸发灭失的。

【起手第一步建议】
① 处理 poison 死信 PIPE-20261011-084204-336356（t0_condition_pack_due，NoneType.close 报错）；
② drain 三条新的 c4_batch_due（10-01/10-08/10-12，attempts=0）。
先给我这两件事的可行性确认（含要读的文件清单和预计改动面），我拍板后你再动手。
```

---

## 〇-B · 一键复制：**调查模式**指令（10-14 版，只读核查用）

> 适用场景：你想让新会话**先把现状摸清楚再干活**，而不是直接动手改。
> 与上面的执行版指令二选一，**不要同时用**。

```
你是 ZephyrAlpha 项目的只读调查会话。项目根目录 D:/ZephyrAlpha（Windows + Python 3.12）。

【铁律：本次只调查，不施工】
- 禁止修改任何文件、禁止 git 提交、禁止清理、禁止删文件、禁止跑写库操作。
- 唯一例外：可以写一份调查报告到 docs/_working/，且写完立刻 git add 入索引
  （本仓库有"未跟踪文件蒸发"前科，两份交接文档都这么丢的）。
- 发现需要改动的地方，只记录"建议怎么改"，等我拍板。

【背景】
09-30 做过一轮"四链路建设体检"（整装回测/数据消费/策略工厂/GPU），10-14 做过收口复核，
结论写在 D:/ZephyrAlpha/docs/_working/2026-09-30-four-chain-handover.md。先完整读它。
注意：文档正文是 09-30 快照，§0 是 10-14 复核结果——两者都读，以 §0 为现状基线。

【调查任务 A：复核四链路现状（09-30 结论是否还成立）】
A1 整装回测：GRADUATED_PACKAGES 是否仍为空？
    → src/zephyr/strategy_pipeline/daily_decision_orchestrator.py（09-30 在 :121，10-14 在 :125）
    → 裁定#305 是否已被推翻？查 docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
A2 GPU：src/zephyr/backtest/gpu_core.py 当前多大、几处消费方、L2 RawKernel 是否已投产？
    → 旧基准（hs300/zz500 上 GPU 反而慢 0.25-0.53x）是否已被新架构推翻？
    → 新基准在 docs/_working/gpu_rewrite/
A3 策略工厂：车道 C scripts/backtest/lane_c_formula_miner.py 的 gplearn SVD 崩溃是否已修？
    → 看 .runtime/logs/factory_lane_c.log 最新运行时间与产出
A4 数据消费：data/runtime/consumption_census_ledger.json 的 zero 计数是否还是 473？
    → 财务/研报因子是否已从 experimental 晋级？

【调查任务 B：核实遗留任务当前状态】
B1 poison 死信 PIPE-20261011-084204-336356（t0_condition_pack_due，
   AttributeError: 'NoneType' object has no attribute 'close'）——是否已处理？根因是什么？
B2 .runtime/strategy_pipeline/pending_events.jsonl 现有几条？c4_batch_due 积压是否还在？
B3 断点 BP-1~BP-7（docs/_working/fullflow_mining/01_strategy_factory/B_后半断点清单.md）
   各自是否已修？逐条给证据。
B4 IBT 31 项施工项（docs/_working/decision_map_campaign_20260924/11_integrated_backtest_audit.md §10）
   现在还剩多少 OPEN？P0-1~P0-5 各自状态？

【调查任务 C：核实待裁定清单】
C1 M2 车道 R-M2-1~6：docs/_working/fullflow_mining/m2_backtest_sim/pending_rulings.md
   哪些已被裁定、哪些还挂着？
C2 Owner 门位 F1-F6：docs/_working/decision_map_campaign_20260924/19_gpu_plan_and_master_backlog.md:85-96
   特别是 F5（GPU ③ 立项）——L2 已在施工，是否属于"先斩后奏"需要追认？
C3 requirements.txt 钉 torch==2.13.0+cpu（裁定 #ARCH-TORCH-CPU-ONLY），
   但实测环境是 torch 2.13.0+cu126。这个依赖口径矛盾是否还在？
C4 全仓还有多少 status: proposed/open 的议题？
   ⚠️ 教训：09-30 曾用正则 grep "status:\s*(open|proposed)" 得到 0，是**假阴性**。
   必须用朴素 grep 逐个 status 值验证，且看 status 值全集。
   重点查：ruling_registry.yaml、architecture_issue_registry.yaml、
   strategy_registry.yaml（STR-AUTO 是否仍为 0）、backtest_backlog.yaml（142 对象进度）

【调查任务 D：项目卫生（可选，但建议）】
D1 git worktree 现在多少个？（09-30 约 9 个会话 worktree，10-14 约 54 个）
   哪些属已死会话可清理？注意 .qoder/worktrees 是另一批。
D2 .runtime/tmp 文件数量（10-14 记录约 80 万个，最大宗是死会话 runlane 遗物）
D3 scripts/backtest/factory_grid_executor.py.tmp.* 五个（10-10 18:2x，生成进程已退出）
   是否还有留存价值？
D4 提交队列死信数（10-14 记录 97 dead）；主树未提交改动数（10-14 记录 660）

【判"资产不存在"的正确姿势——必读，别踩坑】
本仓有 100+ worktree，在途资产常以**未跟踪文件（??）**躺在 .worktrees/.aidrafts/.qoder 隔离区。
`Glob` 默认忽略点开头目录、`git ls-files` 只列已跟踪文件——**两者同时为"无"不等于资产不存在**。
正确做法：先 `git worktree list` 拿全清单，再逐区 `git status --porcelain` 看 ?? 条目。
（09-30 我曾因此误报"gpu_core 不存在"，实际 299 行代码就在两个 worktree 里。）

【输出要求】
给我一份调查报告，包含：
1. 一页结论：A1-A4 四条链路当前各自什么状态（通/半通/断），与 09-30 相比变好还是变差。
2. B/C 两张表：每项遗留/待裁的【当前状态 + 证据文件路径 + 行号】，状态标
   已完成 / 仍开放 / 已过时（不再适用）/ 无法判断。
3. 一份"现在最该做的三件事"建议（按性价比排序），每件事附预计工作量和前置依赖。
4. 明确列出哪些是你这次调查新发现的、09-30 文档里没有的问题。
5. 不确定项单独列一节，不要猜。

不要给施工方案，只要事实和证据。报告写完 git add 入索引。
```

---

## §1 · 项目背景简介

**ZephyrAlpha 是一套 A 股量化交易系统**，Owner 是前摄影师/导演转行的开发者（量化小白视角），
采用"AI 全自动 + 人只做必须人做的事"（注册账号/密钥/额度授权/合规红线）的模式推进。

**核心模块**

| 模块 | 作用 | 入口 |
|---|---|---|
| AutoRuntime Core | 运行主核 | `python -m zephyr.trading` |
| 数据集成器 | 8 子命令采集/校验 | `python -m zephyr.data` |
| 回测引擎 | 向量化日频（T+1 硬断言） | `src/zephyr/backtest/implementations/vectorized_engine.py` |
| 策略流水线 | 日决策编排 | `src/zephyr/strategy_pipeline/` |
| 策略工厂 | 10 阶段质检 | `src/zephyr/pf_core/core/strategy_factory.py` |
| 因子工厂 | 9 阶段质检 | `src/zephyr/factor/factor_factory.py` |
| 仪表盘 | 面板 API | `src/zephyr/frontend/dashboard/api_server.py` |
| GitCommitGateway | 唯一合法提交入口 | `src/zephyr/gov_enforcement/rule_bridge/` |
| DatabaseService | 唯一 DB 真源（禁裸 duckdb） | `zephyr.infrastructure.database_service` |
| LSG 安全网关 | 所有 LLM 调用必经 | `zephyr.security.llm_defense.llm_security.gateway` |

**四份 SOP 真源**：`docs/01_policies_and_standards/sop/backtest_system_sop/`
= README + A 编排 + B 七步循环 + C 策略入库 + D 档案图书馆规范。

**关键纪律**：holdout 定稿锚点 D=2026-09-09，D 前流水全锁；触发<30 不下结论；OOS 衰减≥50% 判存疑。

---

## §2 · 上下文浓缩（四问结论）

| # | 问题 | 09-30 结论 | 10-14 复核 |
|---|---|---|---|
| ① | 整装回测决策链是否打通 / 能否上模拟盘 | **部分打通**。链路全通已联电，但决策层结构性空转（无毕业策略包）；首跑绩效门 C 不过 | ❌ **未变**（GRADUATED_PACKAGES 仍恒空） |
| ② | 财务/研报数据用上了吗 / 哪些没用 | 财务部分用上（有消费方、未进策略）；研报有评估器消费、未晋级；**473 张表零消费** | 未复核 |
| ③ | 策略工厂 + AI 自动化是否全链路打通 | **断**。候选侧 09-19 起停摆，车道 C 09-26 崩溃；E3→E4 事件积压；工厂本体零接线 | ⚠️ 旧积压清除但新增 3 条 |
| ④ | 回测用 CPU 还是 GPU | 实际跑 CPU；GPU 核已写完但锁在 worktree 未合入 | ✅ **已解决**（已入主树且有生产消费方） |

**一句话总览**：地基和管道（数据、引擎、编排、风控门）是硬的；空的是"料"（无毕业策略 + 数据大量闲置）。
GPU 这个"发动机"已于 10-13 前装好并接上油路。

---

## §3 · 关键发现详述（09-30 快照，证据链）

### 3.1 整装回测链路

**链路已实装**：
- `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py`（MOD-BT-214）S1–S7 全链
  （日历/regime/门快照/包选择/仓位/no_trade/落库/T4 核对）已实装并挂 pipeline_events 末棒。
- `src/zephyr/plan_engine/daily_loop_master_switch.py`（MOD-PLAN-033）17 段日循环总扳手，挂 16:45 自动圈。

**致命空转点**：
```
daily_decision_orchestrator.py:125  （09-30 时在 :121）
GRADUATED_PACKAGES: Final[frozenset[str]] = frozenset()   ← 恒空（裁定#305）
```
→ `enabled_packages` 恒 `[]` → **结构性不出手**（不是 bug，是安全态设计）。

**首跑四门判定**（`IBT-FINAL-DELIVERY.md`）：

| 门 | 结果 |
|---|---|
| A 链路完备 | ✅ 过 |
| B 红蓝正确性 | ✅ 过（连续两轮 0，8/8 PASS） |
| C 绩效底线 | ❌ **不过**（HOLDOUT Sharpe **-1.389**；DD 16.5% 过） |
| D 池污染披露 | ✅ 随附 |

**首跑数字**：W_IS -12.1%/Sharpe -0.12；W_OOS +11.9%/+0.34；W_HOLDOUT -12.2%/**-1.39**；W_POSTD -2.1%。

**三座大山**：
1. **成本吃掉全部毛 alpha**：IS 零成本 +26.5% vs 全成本 -12.1%（拖累 38.6pct）；年换手 33-39x。
2. **regime 节流无正增量**：IBT-B 四窗三负，与检测器 r4/r10 方向失真互证。
3. **池时效衰减**：IS 全负→OOS 转正→HOLDOUT 近乎全灭（盲窗仅 4/15 微正）。

**模拟盘**：执行层已在且实弹过（09-23，`delivery_report_20260923.md`：10:42 卖 510300 1100 股 @4.604）。
缺：订单语义只通"防御=空仓"（R-M2-5）；滑点校准分母为零（`sim_trade_log` 切点前 0 行）。

### 3.2 数据消费

**普查台账**：`data/runtime/consumption_census_ledger.json`（09-29）→ **active 287 / zero 473 / retired 5**

**财务**：消费方 `scripts/backtest/eval_f2_fundamental_ic.py:69`；
但因子 FCT-FQ-001/002 = experimental、FCT-FQ-003 = deprecated、`belongs_to_strategies: []` → **未进生产策略**。

**研报**：`c3_fundamental.research_report` **146,633 行 / 4,695 只**；
消费方 `scripts/backtest/eval_exp_expectations.py:145`；EXP-01~06 全 candidate，EXP-02 IC=NaN。

**零消费大户**：股东结构（`top10_circulating` 214 万行 / `shareholder_count` 50 万 / `equity_pledge` 172 万）、
宏观（`cn_macro`/`sw_daily`/`macro_*_gauge`）、深圳开放数据 `alt_sz_*` 20+、
可转债/ETF净值/期货期限结构/港股/北向、情绪成分 C1/C3/C4/C5/C6、`factor.ashare_*` 12 张。

### 3.3 策略工厂 + AI 自动化

**断点清单 BP-1~BP-7**（真源 `docs/_working/fullflow_mining/01_strategy_factory/B_后半断点清单.md`）：

| # | 断点 | 影响 | 工作量 |
|---|---|---|---|
| BP-1 | E2→E3 假说轨无自动接续（`_CONSTRUCT_LANES` 只认公式轨） | 假说过审即滞留 | M |
| BP-2 | E2 过审集读取 fail-silent（`except: return set()`） | 台账故障=构造无声空转 | S |
| **BP-3** | **E3→E4 重事件滞留（最硬断点）** | 考卷件进不了考场 | 分钟级（运行操作） |
| BP-4 | F06 判定书不进统一台账 `strategy_screen` | 车道 F 成平行判定权 | M |
| BP-5 | E4→E5/E6 轻事件无生产消费（intake 报告是 pytest 泄漏件） | 及格集堆积、E5/E6 闲置 | S-M |
| BP-6 | 幂等键三处三口径 | 潜在重考/漏考（有兜底） | S |
| BP-7 | 双窗窗口漂移无机检 | "考卷变了"无留痕 | S |

**其他**：工厂本体（strategy_factory/factor_factory）**零运行时接线**，只被 `__init__` 和 tests 引用；
`STR-AUTO` 计数=0；车道 C 09-26 崩溃（gplearn `LinAlgError: SVD did not converge`）。

**AI 自动化边界（有意设计）**：能自动挖掘/构造（受 E0 闸）、redline 三 gate、LLM 拦截器；
**必须人点头**：`ai_autonomy=human_gated`、`approved_by` 必填、`status` 恒 candidate、无 auto-approve 路径。

**E0 算力闸语义澄清**：`scripts/backtest/compute_window_gate.py` 是**按交易时窗分级的 CPU 调度闸**
（交易日 09:00–15:30=light_only），**与 GPU 无关**；`local_gpu/mixed` 只是重算力权重标签。

### 3.4 算力（CPU / GPU）

> ⚠️ 09-30 曾误报"`gpu_core` 不存在"，实际是 299 行代码以**未跟踪文件**躺在
> `.worktrees/st-gpu-conv-20260928` 与 `st-gpup1-20260929`。教训已写入长期记忆。
> **10-14 复核：已正式合入主树（68KB），见 §0。**

**硬件实测**：RTX 3090 / 24576MiB / Driver 610.88 / CUDA 13.3；
Python 3.12 下 `torch 2.13.0+cu126`、`cuda.is_available()=True`、`cupy 14.2.0`。
`requirements.txt:5-10` 钉 `torch==2.13.0+cpu`（裁定 `#ARCH-TORCH-CPU-ONLY`）——CPU/GPU 依赖口径仍需 Owner 裁。

**09-30 时的旧基准（已被 L2 新架构部分推翻）**：hs300/zz500 **0.25–0.53x（反而慢）**、
all_a 5217 列 **1.51x**、hoisted-cpu 1.78–2.31x、tiers 单趟 1.95–2.39x、parity max rel diff 2.5e-13。
`_GPU_AUTO_MIN_CELLS=8_000_000` 守卫（`_c4_engine.py:489`）即为此设。

---

## §4 · 本会话已完成的任务清单

| # | 任务 | 状态 | 证据/产出 |
|---|---|---|---|
| 1 | 四链路并行只读调研（补齐 09-16→09-30 缺口） | ✅ | 4 个 Explore 代理报告 |
| 2 | 核验 GRADUATED_PACKAGES 恒空 | ✅ | `daily_decision_orchestrator.py:86/121/385/400` |
| 3 | 核验整装回测四门判定与首跑数字 | ✅ | `IBT-FINAL-DELIVERY.md` 全文 |
| 4 | 定位数据消费普查台账与零消费族 | ✅ | `consumption_census_ledger.json` |
| 5 | 定位策略工厂 7 条断点与运行痕迹 | ✅ | `B_后半断点清单.md` |
| 6 | GPU 现状实测（硬件/驱动/torch/CUDA） | ✅ | `nvidia-smi` + torch 探测 |
| 7 | **发现并更正 gpu_core 误判** | ✅ | 深扫找到两个 worktree 副本 |
| 8 | 汇总 31 项整装回测开放施工项 | ✅ | `11_integrated_backtest_audit.md §10` |
| 9 | 汇总 M2 车道 6 条待裁项 | ✅ | `m2_backtest_sim/pending_rulings.md` |
| 10 | 汇总 Owner 门位 F1–F6 | ✅ | `19_gpu_plan_and_master_backlog.md:85-96` |
| 11 | 输出体检可视化（四链路状态图） | ✅ | 内联 SVG |
| 12 | 写入工作区记忆 | ✅ | `.workbuddy/memory/2026-09-30.md` + `MEMORY.md` |
| 13 | **(10-14) 收口审计：发现交付文档蒸发** | ✅ | 本文件重建 |
| 14 | **(10-14) 复核三条关键待办现状** | ✅ | 见 §0 |

**刻意未做**：任何代码修改、任何 git 提交、任何 DB 写入、任何文件移动。全程只读
（10-14 收口仅重建本文件并 git add）。

---

## §5 · 遗留任务清单

### 已完成（10-14 复核）

| 项 | 09-30 状态 | 10-14 |
|---|---|---|
| GPU 遗留 1 · gpu_core 合入主树 | ❌ 锁在 worktree 未跟踪 | ✅ **已入主树 + git 跟踪 + 9 处生产消费方** |
| BP-3 旧积压（09-16 两条 c4_batch_due） | ❌ 滞留 9 天 | ✅ **已清除** |

### 新增（10-14 发现）

| 项 | 详情 | 优先级 |
|---|---|---|
| **poison 死信** | `PIPE-20261011-084204-336356`，kind=`t0_condition_pack_due`，attempts=4，`poison=true`，报错 `AttributeError: 'NoneType' object has no attribute 'close'` | **P0**（已死信，不会自动重试） |
| 新积压 ×3 | `c4_batch_due` 10-01（85 件）/ 10-08（2 件）/ 10-12（4 件），attempts 均=0 | P0 |

### P0 遗留（09-30 识别，状态未复核）

| 序 | 动作 | 备注 |
|---|---|---|
| P0-2 | 车道 C 崩溃修复（gplearn `SVD did not converge`） | 09-26 崩溃后 0 新候选 |
| P0-3 | `cost_qualified_list`（17→3）落主区（IBT-B04） | 池基悬空 |
| P0-4 | 批 D 新鲜窗重考收口（IBT-F01） | GPU 搜索池基 |
| P0-5 | 落地器快照对账 fail-closed（IBT-H02） | GPU 产物落库通道 |
| P0-6 | 双引擎成本口径统一（IBT-D01） | 考尺 5bp vs 整装 ADV 分层 |

### P1 / P2（真源 `11_integrated_backtest_audit.md §10`）

P1：IBT-A01/A02/A03、IBT-B01/B05、IBT-D02、IBT-F02、IBT-H01、IBT-G01、BP-1、BP-4、BP-5
P2：IBT-A04~A07、IBT-B02、IBT-C01~C04、IBT-D03/D04、IBT-E01/E02、IBT-F03、IBT-G03/G04、IBT-H03/H04、BP-2/BP-6/BP-7

### 数据侧

473 张零消费表。优先级建议：① 股东结构族 ② 宏观族 ③ 情绪成分 C1/C3/C4/C5/C6 ④ `factor.ashare_*` 12 张。

### GPU 侧（更新）

1. ~~gpu_core 合入主树~~ ✅ 已完成
2. Phase 4 · L2 批量 GPU 立项（等 Owner 门位 F5）——**从现状看 L2 已在施工**（RawKernel/双核归一）
3. **澄清 `requirements.txt` 的 torch CPU 钉版与实测 CUDA 环境漂移** ← 仍待裁

---

## §6 · 待裁定任务清单（Owner 待批）

### 6.1 M2 车道 6 条（`docs/_working/fullflow_mining/m2_backtest_sim/pending_rulings.md`）

| # | 问题 | 建议 |
|---|---|---|
| R-M2-1 | GPU 规模口径三套并存，"24990 格"无出处 | 选①：令文勘误为"T0 200/T1 3700/T2 900" |
| R-M2-2 | 成本两真相分裂（考尺 5bp vs 整装 ADV 分层） | 选①：毕业生复考强制双口径出证 |
| R-M2-3 | 搜索池基悬空三症状一体 | 选①：池基先修再晋级 |
| R-M2-4 | 六段词表三套映射两套冲突（升级 Owner 在案） | 维持 Owner 在案不代裁 |
| R-M2-5 | 模拟盘订单语义映射扩面 | 选②：维持只防御 |
| R-M2-6 | 配比真源双头（auto_mount vs pf_alloc） | 选①：裁定 pf_alloc 为唯一真源 |

### 6.2 Owner 门位 F1–F6（`19_gpu_plan_and_master_backlog.md:85-96`）

| 门 | 内容 | 时机 |
|---|---|---|
| F1 | 密钥轮换执行（tushare.pro 重置 → secrets 更新 + 旧 key 失效验证） | 本周 |
| F2 | W-M1 翻转确认（三判据全绿后提请） | —— |
| F3 | 上岗规则 v1 + 仲裁序 v1 追认 | 稿件+成绩单齐 |
| F4 | L08-C03 三选一 / G9 板块升格边界 / 六段锚定表语义 | 各自前置齐 |
| **F5** | **GPU ③ 立项决策（等产出密度数据）** | 成绩单后（L2 已施工，建议确认是否追认） |
| F6 | 修宪挂图书馆入口 / 12 项 AI 层批文 | 有空 |

### 6.3 其他待批

- **M5 车道**：`.gitignore` 白名单行（`!scripts/data/backfill_night.bat`）需 `[ARCH-APPROVAL]`；
  或 Owner 直接重注册 tilib 任务 Execute 指向 `.ps1`。真源：`docs/_working/fullflow_mining/pending_rulings.md`
- **E7 模拟盘前哨**：滑点/容量实测档二选一；产出落点裁定（建议复用 `c1_backtest.sim_daily_report`）
- **torch CPU/CUDA 依赖口径**：`requirements.txt` 钉 CPU 但实测环境是 CUDA 版 ← **新增**
- **backtest_backlog.yaml**（09-27）：142 对象，confidence = untested 123 / valid 16 / verified 1

---

## §7 · 剩余任务执行序（10-14 更新版）

| 序 | 动作 | 前置 | 工作量 | 解锁下游 |
|---|---|---|---|---|
| **R0** | 处理 poison 死信 `PIPE-20261011-084204-336356` | 无 | S | t0_condition_pack 链 |
| **R1** | drain 三条新 c4_batch_due（85+2+4 件） | 无 | 分钟级 | E4 考试链 |
| **R2** | 修车道 C 崩溃并重跑 | 无 | S-M | 候选侧供给 |
| **R3** | cost_qualified_list 落主区 | 无 | S | 池基、GPU 搜索 |
| **R4** | 批 D 新鲜窗重考 | R3 | M-L | 整装 v2 池基 |
| **R5** | 落地器 fail-closed 治本 | 无 | M | 产物落库安全 |
| **R6** | 双引擎成本口径对照表 | 无 | M | 成绩单可信度 |
| **R7** | BP-5 清泄漏报告 + 首次自动入库验证 | R1 | S-M | E5/E6 链路 |
| **R8** | BP-1/BP-4 接线 | R7 | M | 假说轨、车道 F |
| **R9** | 整装回测 v2 正式启动 | R3+R4+R6 | —— | 决策链出真结论 |
| **R10** | 裁定 torch CPU/CUDA 依赖口径 | 无 | 裁定 | 环境一致性 |

**关键判断**：R0/R1 是"解锁型"动作（低工作量、高杠杆），当前最优先。
R9 是终点，但在 R3/R4/R6 完成前启动只会重演空转。

---

## §8 · 文件完整路径总表

### 8.1 项目必看（入场）

```
D:/ZephyrAlpha/AGENTS.md
D:/ZephyrAlpha/.trae/rules/project_rules.md
D:/ZephyrAlpha/docs/registry_of_registries.yaml                      # ROOR 唯一入口
D:/ZephyrAlpha/docs/01_policies_and_standards/sop/backtest_system_sop/   # 四份 SOP
D:/ZephyrAlpha/docs/01_policies_and_standards/sop/README.md           # 九族方法论索引
D:/ZephyrAlpha/docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md
D:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md
D:/ZephyrAlpha/SECRETS.md
D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml
D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml
D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml
D:/ZephyrAlpha/data/capability_cards/
```

### 8.2 体检证据文件

```
# 整装回测
D:/ZephyrAlpha/docs/_working/integrated_backtest/IBT-FINAL-DELIVERY.md          # 四门判定+首跑数字
D:/ZephyrAlpha/docs/_working/integrated_backtest/IBT-CAMPAIGN-LEDGER.md
D:/ZephyrAlpha/docs/_working/integrated_backtest/IBT-PROTOCOL-V1.md
D:/ZephyrAlpha/docs/_working/integrated_backtest/IBT-RUN-REPORT.md
D:/ZephyrAlpha/docs/_working/integrated_backtest/IBT-REDBLUE-REPORT.md
D:/ZephyrAlpha/docs/_working/integrated_backtest/IBT-DATA-MATRIX.md
D:/ZephyrAlpha/docs/_working/integrated_backtest/max_remediation_plan.md
D:/ZephyrAlpha/docs/_working/integrated_backtest/IBT-HANDOFF-TO-MAX.md
D:/ZephyrAlpha/docs/_working/integrated_backtest/artifacts_v2/W_OOS/
D:/ZephyrAlpha/docs/_working/decision_map_campaign_20260924/11_integrated_backtest_audit.md   # ★ 31 项
D:/ZephyrAlpha/docs/_working/decision_map_campaign_20260924/13_trading_chain_audit.md
D:/ZephyrAlpha/docs/_working/decision_map_campaign_20260924/19_gpu_plan_and_master_backlog.md # ★ F1-F6
D:/ZephyrAlpha/docs/_working/decision_map_campaign_20260924/02_rulings_and_calibers.md
D:/ZephyrAlpha/docs/_working/decision_map_campaign_20260924/10_evaporation_forensics.md       # ★ 蒸发案

# 代码链路
D:/ZephyrAlpha/src/zephyr/strategy_pipeline/daily_decision_orchestrator.py      # ★ :125 恒空常量
D:/ZephyrAlpha/src/zephyr/plan_engine/daily_loop_master_switch.py
D:/ZephyrAlpha/src/zephyr/strategy_pipeline/fw_backtest.py
D:/ZephyrAlpha/src/zephyr/pf_core/core/strategy_factory.py
D:/ZephyrAlpha/src/zephyr/factor/factor_factory.py
D:/ZephyrAlpha/src/zephyr/backtest/implementations/vectorized_engine.py
D:/ZephyrAlpha/src/zephyr/backtest/gpu_core.py                                 # ★ 10-14 已入主树
D:/ZephyrAlpha/scripts/backtest/translated/_c4_engine.py                        # ★ :480-574 接线
D:/ZephyrAlpha/scripts/backtest/lane_c_formula_miner.py                         # ★ 车道 C
D:/ZephyrAlpha/scripts/backtest/factory_grid_executor.py
D:/ZephyrAlpha/scripts/backtest/c4_batch_screen.py
D:/ZephyrAlpha/scripts/backtest/hypothesis_precheck.py
D:/ZephyrAlpha/scripts/backtest/exam_cost_reexam.py
D:/ZephyrAlpha/scripts/backtest/f06_e4_wfa_exam.py
D:/ZephyrAlpha/scripts/backtest/compute_window_gate.py                          # E0 闸
D:/ZephyrAlpha/scripts/backtest/sim_daily_runner.py
D:/ZephyrAlpha/scripts/backtest/feedback_prior.py
D:/ZephyrAlpha/src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py
D:/ZephyrAlpha/src/zephyr/backtest/core/cost_model_calibration.py
D:/ZephyrAlpha/src/zephyr/backtest/regime_validation/exam_cost_gate.py

# 数据与消费
D:/ZephyrAlpha/data/runtime/consumption_census_ledger.json
D:/ZephyrAlpha/src/zephyr/governance/consumption/consumption_census.py
D:/ZephyrAlpha/scripts/backtest/eval_f2_fundamental_ic.py                       # :69 财务消费方
D:/ZephyrAlpha/scripts/backtest/eval_exp_expectations.py                        # :145 研报消费方
D:/ZephyrAlpha/data/backtest_artifacts/runs/
D:/ZephyrAlpha/src/zephyr/backtest/run_archive.py

# 策略工厂与运行痕迹
D:/ZephyrAlpha/docs/_working/fullflow_mining/01_strategy_factory/B_后半断点清单.md   # ★ BP-1~7
D:/ZephyrAlpha/docs/_working/fullflow_mining/m2_backtest_sim/pending_rulings.md     # ★ R-M2-1~6
D:/ZephyrAlpha/docs/_working/fullflow_mining/pending_rulings.md
D:/ZephyrAlpha/docs/_working/fullflow_mining/00_orchestration.md
D:/ZephyrAlpha/docs/_working/fullflow_mining/m4_ai_layer/01_ai_layer_six_families.md
D:/ZephyrAlpha/.runtime/logs/factory_lane_c.log
D:/ZephyrAlpha/.runtime/logs/c4_exam.log
D:/ZephyrAlpha/.runtime/strategy_pipeline/pending_events.jsonl                 # ★ 10-14 有 4 条
D:/ZephyrAlpha/.runtime/strategy_pipeline/last_receipt.json

# GPU
D:/ZephyrAlpha/docs/_working/gpu_rewrite/                                      # 11 件
D:/ZephyrAlpha/docs/_working/gpu_rewrite/p1_wiring_benchmark.md
D:/ZephyrAlpha/docs/_working/gpu_rewrite/migration_roadmap.md
D:/ZephyrAlpha/docs/_working/gpu_rewrite/rewrite_architecture_three_tiers.md
D:/ZephyrAlpha/docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/GPU_merge_audit.md

# 模拟盘 / 数据地基
D:/ZephyrAlpha/docs/_working/sim_launch/delivery_report_20260923.md
D:/ZephyrAlpha/scripts/backtest/sim_deviation_report.py
D:/ZephyrAlpha/docs/_working/data_fix_campaign/final_delivery_report_20260921.md
D:/ZephyrAlpha/docs/_working/e2e_integration/LEDGER.md
D:/ZephyrAlpha/docs/_working/e2e_integration/panorama_health_snapshot_20260924.md
```

### 8.3 本会话的工作文件

```
D:/ZephyrAlpha/docs/_working/2026-09-30-four-chain-handover.md    # 本文件（10-14 重建版）
D:/ZephyrAlpha/.workbuddy/memory/2026-09-30.md                     # 工作区日志（体检快照）
D:/ZephyrAlpha/.workbuddy/memory/MEMORY.md                         # 项目长期备忘
D:/ZephyrAlpha/.workbuddy/memory/2026-10-14.md                     # 收口审计日志
```

---

## §9 · 给新会话的补充提醒

1. **本文件 09-30 原版已蒸发**。原因：从未 `git add`，长期停留在 untracked 状态。
   **铁律：新建交付文档必须立即 git add 入索引。** 本版已 git add。
2. **判"资产不存在"的姿势**：本仓 100+ worktree，在途资产常以未跟踪文件躺在隔离区。
   `Glob` 默认忽略点开头目录、`git ls-files` 只列已跟踪文件——**两者为"无"不等于不存在**。
   正确：`git worktree list` 拿全清单 → 跨区深扫。
3. **不要重复立案**：`11_integrated_backtest_audit.md` §9 有 14 条"已修案底台账"（含 commit hash），先查表。
4. **09-30 的 GPU 基准已过时**：新 L2 架构用 RawKernel 融合扫描专治 kernel-launch 税，
   "hs300/zz500 上 GPU 反而慢"的结论不再适用，请以 `docs/_working/gpu_rewrite/` L2 新基准为准。
5. **仓库卫生**：100+ worktree 堆积（`.worktrees/` `.aidrafts/` `.qoder/` `.runtime/commit_queue/`），
   多数标 locked。建议安排一次清理审计。
6. **Owner 沟通风格**：结论先说、大白话+比喻、只看批次决策点三问（淘汰/下批/口径）；
   不接受"游结论"，一切回测结论必须走 SOP-B 台账 + run 档案归档。

---

*09-30 由只读审计会话生成；2026-10-14 收口审计时发现原版蒸发，从工作区记忆重建并补入复核结果。*
*全程未做任何代码改动；10-14 仅重建本文件并 git add（未 commit，正式提交请走 scripts/git_commit.py）。*
