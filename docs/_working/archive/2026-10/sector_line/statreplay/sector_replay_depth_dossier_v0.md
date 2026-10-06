---
ttl: task_bound
completes_when: 深窗回放落地且对拍两轮零新发现
created: 2026-09-23
sid: st-statreplay-20260923
lane: sector_line
status: draft
title: 状态层历史回放·深度案卷与降档申报（基线冻结件）
---

# 状态层历史回放 深度案卷（st-statreplay-20260923）

Owner 夜窗令③要求"禁另立派生口径"，本案卷只报实测，不做口径替换。

## §1 冻结基线（令"随批"第2/3条，必做件）

复现（只读，reader 角色服务端强制 readonly=1）：

```bash
cd D:/ZephyrAlpha && PYTHONPATH=src python \
  .runtime/sessions/st-statreplay-20260923/staging/freeze_baseline.py
```

| 冻结对象 | 实测 | sha256（链式：按日 hash 再串接） |
|---|---|---|
| `kline_sector_880` period='1d' | 443,380 行 / 1,585 日 / 469 板 / 2020-03-17→2026-09-23 | `710fe24490fbfe29dcbf90daf5f53904883add86782492bcd6cc6663f440ddd0` |
| `sector_state` 活值全量（8 列逐字段） | 7,973 行 / 17 日（close_final 16 + pre_open 1） | `011d45280c233548314461e0295284da76d6439c6059c1fb9955d406f38fa73a` |

**hash 是实现的函数，不是数据的函数**：本班一次性的探量脚本用另一种十进制/NULL 编码，
得出 `da6b6f24…`/`72ec5516…` 两个不同值。故基线只能由**本驱动单一真源**产出，
manifest 与 `freeze_baseline.py` 必须同批入库；任何人换一套格式化重算都等于换卷。

驱动三态已验（绿/红/漂移）：`--selftest-red` 微扰一个收盘价→链 hash 必变（710fe244→3216af3d，
exit 0）；`--manifest` 对篡改件 exit 2 报 DRIFT、对干净件 exit 0 报 MATCH；三次独立复跑同值。
判过对拍的脚本先证明能红，方计入红蓝一轮。

活值 NULL 普查（同批实测）：`capital_score` **7,973/7,973 全空**、`net_inflow_pct` 259、`strength` 56。
`capital_score` 在活表从未落值 ⇒ 该轴无"活值"可对拍，回放只能如实产 NULL。

对拍期 880 表禁动：任何 `kline_sector_880` 回补都会使上述两个 hash 失效（secbuild 的
09-01→09-21 就是手工回补产物，tqcenter 日增量尚未开，风险为真）。

## §2 可回放日历（修正版，含一次自纠红证）

**首版算错过并已在案**：初次用 `sector_constituent_snapshot`（仅 2 个快照日）作成分真源，
得出"四轴全齐=2 日/0.1%"。管道 `_CONSTITUENT_SQL` 实读 `sector_constituent`
（SCD-2，`valid_from≤T AND (valid_to IS NULL OR valid_to>T)`），改用管道真谓词后为 17 日。
差异已留痕，两版数字均可复现。

1,585 日骨架上各轴可得性（全部本人实测）：

| 轴 | 依赖 | 可得日数 | 首日 |
|---|---|---|---|
| `momentum_pct` + `rrg_quadrant` | 仅板块日K（价） | **985**（板数≥367 窗） | 2022-09-01 |
| 同上，截面较稳（板数≥400） | — | 765 | 2023-08-01 |
| `net_inflow_pct` | money_flow ∩ 成分 | **45** | 2026-07-23 |
| `strength` | limit_up_pool ∩ 成分 | **17** | 2026-09-01 |
| `capital_score` | 活表从未落值 | 0 | — |
| **四轴齐备** | 交集 | **17 = 1.1%** | 2026-09-01 |

成分缺陷量化：`sector_constituent.valid_to` 95,124 行全 NULL，4 个 `valid_from` 批次
（07-23/07-28/08-01/09-03）在 **T≥2026-09-03 起 42 日内 `constituent_count` 重复计数**。
确定性可复现 ⇒ 与活值逐位一致，但**非真 PIT 归属**（令"随批"第5条，缺陷归数据线）。

## §3 三件降档申报（禁硬凑）

**T1 sector_state 全史**：任务书"880 板块 1584 日"两处失真——880 是通达信板块码前缀族非计数
（实宽 469），1,584 日跨度属实但 2020/2021 仅 2/8 个板（439/1,585≈28% 日期为退化截面），
单板最长 1,548 日。**全轴齐备仅 17 日**。按冻结公式跑全史=忠实但 98.9% 稀疏。
另：`run_pre_open` 不可历史驱动（内部恒取表内最大日，传参仅作输出标签），且它另写第二张表
`sector_preference` ⇒ 回放只能 close_final。

**T2 六段情绪周期**：判 `INSUFFICIENT` 收口（令③）。三重理由——①无六段判定器，活标签来自
`REGIME_TO_SEGMENT` 代理映射（代码自注"判定器接电后切换真源"），回放它等于验证一张查表；
②冻结 v0.1.0 输入 `limit_up_pool`/`daban_board_event` 仅 17/16 日，且东财源侧只留近约 30
交易日=结构不可回补；③派生腿上界虽 1,875 日（2019-01-03 起连续），但属新口径=异轴顶替，
先例同罪（st-t0-revival）。先例引文：st-emomine"不顺延窗、不换成分集重考（预承诺）"。

**T3 cohort 面板**：对象错配先记——cohort 无面板表，`cohort_daily_ledger` 是五人群长表账本
（170 行/17 日），其 ORDER BY **不含日期列**且无 version/run_id ⇒ 重插即毁历史行。
四资金面实测：money_flow 82 / margin_trading 497（tushare 452 止 07-17 + ifind 45，异源接缝）
/ dragon_tiger 34 / block_trade 34 ⇒ **四表面交集 31 交易日**；面板公式对 11 指标中 2 个
（`retail.attention_median`、`hot_money.board_height_max`）在回放窗内基本恒 `missing`。
**冻结声明不成立**：该公式无 version 常量、无哈希、无门禁、无 golden（与
`emotion_index`/`sector_state` 均带 version 对照），仅 13 个带硬编码 Decimal 的测试钉值。

## §4 令② 四条件进度

| 条件 | 状态 |
|---|---|
| ① 词表先行与 emoreplay 对齐 | **受阻**：`state_vocabulary_registry.yaml` 实测**未入 git**（HEAD 无此路径，untracked），且其 28 套词表**从未登记** sector `stage` 四态（`close_final` 等 0 命中）。STATE-VOCAB-REGISTRY 门本体已在 dev（warn-only）。时钟起于 2026-09-23 19:1x |
| ② DDL+骨架§6+不变式同批原子 | 待与①同批 |
| ③ 活端不可见性实证 | 可行且已定位证据点：`load_l2_admission` 与 `_COPY_PRE_OPEN_SQL` 均按字面 `stage=` 过滤，新值天然不可见；实跑证据待回放批 |
| ④ 受阻>半天回落日期方案 | 挂起计时 |

## §5 阻塞与解锁信号（总指挥令改道后版）

- **不等 st-stress-20260923-0009**：该项已撤单永不落地（压测班重编号+总指挥扣件）。
  深窗开跑条件改道为**唯一一条**：secbuild merge 落地（清扫班 0013→0015 链）即解锁冻结公式。
  实测 2026-09-23 20:0x：`git ls-tree HEAD | grep -c sector_state_aggregator.py` = **0**（仍未合），
  sweep-tail 0013=processing、0014/0015/0016 待排。
- **落地面改道（令④已获认可）**：`stage='replay_close_final'` 方案**结构性落空**——
  `state_vocabulary_registry.yaml` 从未进 git（HEAD 无此路径），且该册 28 套词表从未登记
  sector `stage` 四态。按④自动回落**日期不相交方案**：回放只写活行未覆盖的日期
  （活集 = 2026-09-01→09-23，17 日），键空间天然不撞；溯源靠"日期边界+本案卷登记"而非列。
  残留风险如实记：日后若有人回补旧日期，与回放同键、后写者胜。
- **队列根坑（本班实测一次，已解）**：在 session worktree 内直接 `git_commit.py --enqueue`
  会把袋写进 **worktree 局部队列根**，输出照样报"快照入袋即完成（零丢失）"，但主传送带
  永不排这个根——实测该袋在盘 1 小时无人认领，主队列 status 全量列举查无此项。
  处方（照 wm1-lane-b 在册配方，非新造）：`commit_queue.py --queue-root 主区 enqueue
  --worktree-root 本worktree --no-bootstrap`。已按此重入主队列
  `q-20260923-st-statreplay-20260923-0001`（branch=dev，blob `31ceca60…`/`3fa4b10e…`
  进程外核实均含 裁定#407/exam_window_cut 文本）。旧死根袋已挪至
  `.worktrees/…/.runtime/tmp/dead_queue_root/`（可逆，非删除）。
- `sector_state`/`sector_preference` **均未进 `business_data_categories.yaml`**（仅在该未合分支），
  故 dev 侧任何脚本今日取不到表名（表名注册门禁禁字面量）——落表批必须与该注册同批。
- 本班制品 promote 待 `creation_token`（新 .py/.md 7 格式），按令"禁重复登记"，
  随 secbuild 落地批一并登。

## §6 GPU 板块条件矩阵输入包·容量口径（总指挥令更新）

供给目标改为**单机 RTX 3090 24GB、周五 12:00→周日 23:00 共 59h** 的消费窗校准：

| 项 | 实测/设计值 |
|---|---|
| 面板体积 | 469 板 × 1,585 日 = 742,465 单格；float32 稠密阵 = **2.8 MB**（含 4 通道标签阵 <12 MB） |
| 结论 | 显存完全不是约束（<0.05% of 24GB）——**整阵可常驻**，消费方无需分片加载 |
| 因此本包义务 | 把**贵算的部分预先算好**交付（动量分位/RRG 象限/轮动标签/考试窗位图），不交原料价K让下游重算——59h 预算必须全部留给搜索，不能耗在预处理 |
| 打包格式 | 稠密 `.npy`/固定列 `.parquet`（禁 CSV 逐行解析；`data/strategy_intake/grid_<ts>/` 三件套照抄既存约定） |
| 窗位图 | `is_holdout` 位阵（按 裁定#407 切点 2025-09-09 打标），随包必带 S10 `NO_EDGE` 原文警示 |

待锁项：59h 是**消费窗**而非本班施工窗——本包能否在该窗内被跑完，取决于消费方的搜索空间
（矩阵单元数 × 假设数），不取决于本包体积。此点入包内 README，防被误读为"包太大跑不完"。

