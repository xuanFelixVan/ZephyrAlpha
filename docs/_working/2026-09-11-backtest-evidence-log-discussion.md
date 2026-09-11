---
ttl: task_bound
date: 2026-09-11
---

# 回测证据链与验证档案——现状盘点 + 增量设计 + 规范总清单（讨论稿）

> **日期**：2026-09-11 ｜ **状态**：讨论稿（待 Owner 逐条裁定）
> **缘起**：Owner 问——①每个回测点是否有单独日志+总日志+专门的库；②验证档案是否与前端节点详情打通；③每条验证档案的字段与命名怎么定（要能看到"用了哪些数据→跑出什么→判定什么→为什么"）；④除日志外还有哪些要规范（一次列全）。
> **关联真源**：`docs/_working/2026-09-09-node-backtest-governance.md`（PB-01~16 已裁定，个人量化精简版）｜`sop/backtest_system_sop/`（SOP-A/B/C，2026-09-11 定稿）。

## 一、现状盘点：你要的东西大部分已经有了（防撞车盘点）

| Owner 的问题 | 项目现状 | 状态 |
|---|---|---|
| 每个回测点有单独日志？ | `c1_backtest.node_verdict` 台账（ClickHouse MergeTree，只追加不删改），**每行=某节点某次验证的成绩单** | ✅ 已施工（PB-02） |
| 有总日志/专门的库？ | 三层：①CH `c1_backtest` 库（节点验证台账）②PG decisiongraph `decision_nodes` L5 学习层（策略级 BacktestResult 证据，evidence_hash）③`data/backtest_artifacts/bt-*.json`（run 级回测产物含 trade_log） | ✅ 三层都在 |
| 前端节点详情右侧栏打通？ | tdm.js 抽屉「验证档案（回测台账）」区已上线（PB-04）：验证态徽章（valid/噪音/pending/未验证/衰减中）+ 历次验证记录列表，只读端点 `/api/tdm/validation?node_id=`，失败降级不阻断地图 | ✅ 已施工 |
| 每条记录的字段？ | 12 字段已定（DDL 真源 `schemas/categories/backtest_node_verdict.py`）：run_id/snapshot_commit/window_start/window_end/node_id/validation_method/triggers/hit_ratio/significance/verdict/verdict_at/notes | ✅ 已定 |
| 名字怎么取？ | run_id=`VAL-YYYYMMDD-HHMMSS`（验证）/ `bt-*`（策略回测产物）/ 对象=`BT-<批次>-<序号>`（SOP-A） | ⚠️ 三套并存，待统一登记 |
| 判定标准（专业机构怎么做）？ | 2026-09-09 §六已全网调研 12 条：全部有业界依据（Fed SR 11-7/OCC 2026-13 模型清单、WorldQuant 六态、Quant-Agent 七态、alphalens、López de Prado"回测中做研究=酒后驾车"、Finantrix PIT 快照、私募月度复盘衰减即下线）；土规已代码化（触发<30 不下结论 / OOS 衰减≥50% 判存疑 / 滑点 20bp/40bp 容差线） | ✅ 已调研+已代码化 |
| 五类验证方法学？ | validation_method_registry.yaml：sensor_monotonicity / agg_discrimination / exec_quality / exit_counterfactual / portfolio_attribution；runner 按 layer+flow 自动推导 | ✅ 已施工（P1-2） |

**结论**：Owner 设想的"验证档案跟回测打通"不是要新建，而是**已通**——缺的是下面第二节的三块增量。

## 二、增量缺口（本轮真正要建的）

**缺口 G1：过程档案层（Owner 本轮最想要的）。** node_verdict 只存"结论成绩单"，notes 只有一句话。Owner 要的"这一条用了哪些数据、跑出来什么情况、判定、判定原因"= SOP-B 七步循环的**过程留痕**（候选算法清单 / DATA-GAP 清单 / 宽测结果 / 剪枝记录 / 迭代 diff）目前散落对话里，落库无门、前端看不到。

**缺口 G2：判定原因结构化。** verdict 怎么来的现在埋在 notes 文本（"滑点均值 X bp（基准口径=…）"）——判定链明明是代码化的（runner 土规），但 reason 没有结构化字段，前端没法显示"为什么"。

**缺口 G3：策略快筛台账。** SOP-C ④ 快筛批测（600 条海选）没有结构化存储（node_verdict 是节点级，strategy 级只有 decisiongraph 的 BacktestResult 单条通道，缺批量 scoreboard 表）。

**缺口 G4：命名与登记统一。** VAL-* / bt-* / BT-* 三套 ID 并存，无一处登记"哪个 run 属于哪个对象、用了哪些数据版本"。

## 三、设计方案：三层证据体系（补增量，不重造）

```
层1 对象级  BT-*        SOP-A backlog 注册条目（验收阈值预注册）          → data/backtest/backtest_backlog.yaml
层2 run 级  RUN 档案    一次执行=一个目录（过程档案容器）【新建 G1/G4】    → data/backtest_artifacts/runs/<run_id>/
层3 结论级  台账行      node_verdict（节点）/ strategy_screen（策略）【G3】+ decisiongraph L5（策略证据）
```

### 3.1 层2 run 档案（G1 核心，文件制）

- **落点**：`data/backtest_artifacts/runs/<run_id>/`，一次 run 一个目录：
  ```
  meta.json           # run 元数据（见 3.2）
  01_survey.md        # SOP-B①候选算法清单（≥3 候选+出处）
  02_data_gap.yaml    # SOP-B②DATA-GAP 清单（needs-driven）
  03_data_manifest.yaml  # 实际取数清单【G4 一部分】：每项=数据源/表/区间/PIT 时点/降级标记
  04_wide_result.*    # SOP-B④宽回测结果（分状态原始分布）
  05_prune_log.yaml   # SOP-B⑤剪枝记录（剪了什么/为什么/剪后表现）
  06_narrow_result.*  # SOP-B⑥窄回测结果（全成本+WFA/OOS）
  07_iteration_log.yaml  # SOP-B 迭代 diff（每轮：改了什么/为什么/结果）【多重检验计数器同步】
  verdict.md          # ⑦归档判定书（三出口之一+理由）
  ```
- **为什么文件制不进库**：产物异构（表/文本/图），CH/PG 不适合；decisiongraph 已有"路径+evidence_hash"引用先例；`bt-*.json` 已是文件制先例。
- **关联**：node_verdict.run_id / strategy_screen.run_id / meta.json.object_id 三键互查——前端从台账行点 run_id 即可打开过程档案（tdm.js 已有 nlink 助手）。

### 3.2 meta.json 字段（run 元数据）

```
run_id            # 命名规范见 §四
object_id         # BT-<批次>-<序号>（SOP-A backlog 主键；无对象的老 run 允许空）
kind              # VAL(节点验证) | BACKTEST(策略回测) | SCREEN(策略快筛) | ABLATION(消融对照)
snapshot_commit   # git rev-parse --short HEAD（PB-06 轻量快照，已有）
window / holdout_cut  # 验证窗口 + 保密考卷截止线（PB-08）
cost_mode         # rough(粗) | full(全五项，约束一)
data_manifest     # → 03 文件
steps             # {survey: done, data_gap: done, ..., verdict: pending} 七步状态机
attempts          # 迭代轮数（喂 Deflated Sharpe 的试验计数）
```

### 3.3 判定原因结构化（G2）

- node_verdict 加一列 `verdict_reason`（LowCardinality 枚举，由 runner 代码生成，**禁 AI 手填**）：
  `insufficient_samples / oos_decay_suspect / slip_within_tolerance / slip_marginal / slip_above_tolerance / counterfactual_missing / avoided_negative / reference_price_missing / method_not_applicable`
- notes 保留为人话补充；前端徽章 hover/下钻显示 reason。存量行 reason=`legacy_notes` 兼容。

### 3.4 策略快筛台账（G3）

- 新表 `c1_backtest.strategy_screen`（同 DDL-as-Code 模式）：run_id / screen_batch / strategy_id / source_file / translated(是否) / is_sharpe / deflated_sharpe / max_drawdown / turnover / oos_years_decay / cluster_id / verdict(screened_in|rejected|failed_translate) / verdict_reason / notes；ORDER BY (screen_batch, strategy_id)。
- 与 SOP-C C4/C5 一一对应；入库 strategy_registry 的条目必须能回指 screen run。

## 四、命名规范（统一登记）

| 对象 | 前缀 | 格式 | 例 |
|---|---|---|---|
| 回测对象（SOP-A backlog） | `BT-` | `BT-<批次>-<序号>` | BT-P0-001 |
| 节点验证 run | `VAL-` | `VAL-<batch>-<YYYYMMDD-HHMMSS>`（batch=L4/XFLOW/…） | VAL-XFLOW-20260911-180000 |
| 策略回测 run（引擎产物） | `bt-` | `bt-<YYYYMMDD>-<slug>`（沿用既有） | bt-20260911-daban-sleeve |
| 策略快筛 run | `SCR-` | `SCR-<YYYYMMDD-HHMMSS>` | SCR-20260912-090000 |
| 消融对照 run | `ABL-` | `ABL-<对象>-<序号>` | ABL-BT-P1-003-01 |

铁律：run_id 全局唯一、只增不改；台账行通过 run_id 挂到唯一 run 目录。

## 五、前端验证档案信息架构（增量，沿既有六助手）

1. 现状保留：徽章 + 历次记录列表；
2. 每行增列：verdict_reason 中文徽章（"样本不足/衰减存疑/滑点超容差…"）+ run_id（nlink 打开 run 目录 verdict.md 摘要）；
3. 下钻页（后置 P2）：全局验证总览页（所有节点当前 verdict 矩阵：节点 × 六段状态）。

## 六、业界对标补充（2026-09-09 调研之外，本机制的两个直接对标）

- **实验跟踪（experiment tracking）**：MLflow run（run_id + params + metrics + artifacts 目录）与 W&B run 是业界标准形态——我们"run 目录 + meta.json + 七步产物"即其文件制轻量版（50 号备忘录已调研过 MLflow，结论是不引重型平台，自建轻量台账，方向一致）。
- **模型清单（Model Inventory）**：SR 11-7/OCC 2026-13 要求"每模型唯一 ID+验证状态+验证日期+已知局限"——node_verdict + backlog 即我们的 Model Inventory，字段覆盖度已够（个人量化精简版口径）。

## 七、除日志外，回测还需要规范的清单（Owner 最后一问，一次列全）

| # | 规范 | 现状 | 归属 |
|---|---|---|---|
| 1 | ID 与 run 命名规范（四前缀+时间戳+只增不改） | 本稿 §四 新提 | 本稿裁定 |
| 2 | run 过程档案规范（目录结构/每步产物模板/保留策略） | 本稿 §三 新提 | 本稿裁定 |
| 3 | verdict+reason 枚举规范（判定链代码化，禁手填） | 本稿 §3.3 新提 | 本稿裁定 |
| 4 | 数据来源清单规范（data_manifest：源/区间/PIT/降级标记）——PB-15 数据哈希被砍后的轻量替代 | 本稿 §3.1 新提 | 本稿裁定 |
| 5 | 成本口径与窗口声明规范（引用结论必带 口径×区间×holdout 状态） | SOP 总纲 §7 已有 | ✅ |
| 6 | 验收阈值与搜索空间预注册规范 | SOP-B 护栏已有 | ✅ |
| 7 | 迭代留痕与多重检验计数规范（attempts 喂 DSR） | SOP-B 留痕铁律 → 落地为 meta.attempts | 本稿落地 |
| 8 | 策略快筛统一口径规范（同区间/同成本/T+1/同引擎 + Deflated Sharpe 强制） | SOP-C C4 已有 → 补表结构 §3.4 | 本稿补 |
| 9 | holdout 保密考卷纪律（12 个月/定稿锚点/考完作废前移） | PB-08 + runner 已代码化 | ✅ |
| 10 | 并发纪律（同对象禁双 run 并行；复用 session 文件锁） | 新提（轻量） | 本稿裁定 |
| 11 | 归档与退役联动（BT 对象判死→节点降级→PB-03 噪音闭环；策略判死→registry 退役态） | 骨架已有（PB-03/decay_watch） | ✅ |
| 12 | 复现演练（抽样 run 重跑对照，人工比对净值/交易数一致） | 新提（可选轻量，P2） | 待裁定 |

## 八、待 Owner 裁定

| # | 问题 | 建议 |
|---|---|---|
| R1 | run 过程档案采用文件制 `data/backtest_artifacts/runs/<run_id>/`（§3.1） | 认可（最轻，与 bt-*.json 先例一致） |
| R2 | node_verdict 加 verdict_reason 列（代码生成枚举，存量=legacy_notes） | 认可（DDL 变更走 apply DDL + verify_schema_truth） |
| R3 | 新建 strategy_screen 表承接 SOP-C 快筛 | 认可（SOP-C 启动前建好即可） |
| R4 | 命名规范按 §四 统一（VAL 带 batch 段） | 认可 |
| R5 | 复现演练（#12）本期做不做 | 建议 P2 按需（对齐 YAGNI） |
