---
created: 2026-10-01
ttl: task_bound
title: E11 F 车道消费断点——E2 侧 recipe 适配器施工簿（st-lanech-20261001 代理E）
worktree: .worktrees/st-lanech-20261001
rebuild: 20261001 主区 docs/_working/lane_c_chain_night_20261001/ 被他队清理事故删除，本簿按代理E上下文原文重建于 worktree（内容与原版一致，仅补本注记）
---

# E11：F 车道消费断点（pipeline :73-74 欠账销项）

> 注记：本簿原落点=主区 `docs/_working/lane_c_chain_night_20261001/e11_lane_f_adapter.md`，
> 2026-10-01 被他队清理事故删除后按施工代理上下文原文重建于此（worktree 内）。施工产物
> 本就在 worktree，重建零信息损失。

病根：F 车道进货活（F06Grid 计划任务驱动 executor 落 grid_*/manifest.csv，活到 09-29），
但 E2 预审消费断——`_LANE_SPECS` F 条目自注"E2 侧适配器待挂"，`intake_sources` 六车道无 F，
且条目 intake 指向**不存在的** `grid_latest_manifest.csv`（幻影路径）。

## 一、挖矿结论

### 1.1 manifest 真实 schema（grid_20260925-232032 实测）

```
recipe_id,prefix_key,degraded_dimensions,sharpe,ann_return,max_drawdown,avg_turnover,net_days,values_json
0caa81205873,"{""A1_factor_normalize"":""industsize_neutral"",...}",(),0.108,-0.0109,-0.566,0.037,1622,"{...13轴全量...}"
```

- `recipe_id`=sha1(全维取值规范 JSON)[:12]（`position_recipe_compiler.PositionRecipe`，
  内容寻址——**同参数组合跨批次同 id**，幂等天然键）；`prefix_key`=信号侧差异维子集 JSON；
  `degraded_dimensions`=降级维元组字串（如 `()` / `('A1_factor_normalize',)`）；
  `values_json`=13 轴全参数（A1 normalize…K capital_ramp，含布尔轴 J_regime_switch=false）；
  T3 档位扫描启用批多 cost 两列（适配器按列名宽容读取不受影响）。

### 1.2 批次现状（主区 data/strategy_intake/，2026-10-01 01:00 点货）

- grid_* 目录 26 个：**24 个有 manifest.csv、共约 24,657 行 recipe**（最大单批 10,080 行）；
  1 个空目录（grid_20260926-230010）、1 个缺 manifest（grid_20260915-051448）；
  最新两批（09-29 040003/040141）=空 manifest（仅表头，0 recipe）→ 适配器必须诚实处理空批。
- worktree 只带 3 个跟踪批：**024947（3,700 行，含 handover_verdict.yaml 的已交接批）**+两个 09-29 空批。

### 1.3 执行器产出语义（factory_grid_executor MOD-BT-196 + compiler）

recipe=**仓位参数网格机械产物**（组合层：normalize×combine×top_n×sizing×调仓×cap×universe×
成本档的笛卡尔格点），带样本内回测指标（sharpe/年化/回撤/换手/净值天数）；阴性格点另落
negatives.csv。**manifest 无机制叙事字段**——轴中文描述真源在
`config/position_recipe_grid_schema.yaml`（每维带 desc，如"因子标准化"）。

### 1.4 E2 消费契约（hypothesis_precheck MOD-BT-091）

- CSV 四列硬校验：`candidate_id/hypothesis_zh/birth_channel/birth_batch`（load_candidates）；
- 幂等键=candidate_id vs CH 判定台账终局集（`SQL_ALREADY`：verdict≠deferred，deferred 可重审）；
- 前置对账 `intake_ledger_recon.preflight`：台账名不在 `LEDGER_CHANNELS` 表 →
  `unknown_ledger` fail-open 跳过（不阻断）；
- 判定 prompt 六问（机制/前视/成本/可证伪/同义反复/边界）——假说文本必须能承载六问审。

### 1.5 照葫芦的葫芦（D/C/G 车道适配模式）

模块级 `_INTAKE_CSV`+`BIRTH_CHANNEL`+`make_candidate_id`+确定性假说构造+出生证机器写入+
台账追加写（header=not exists、utf-8-sig）；编排层"车道干完活即卸台账，本编排只幂等消费"；
写口升级件=intake_ledger_recon.`append_ledger_rows`（CAS safe_write_text，F16 治本唯一追加口）。

## 二、方案（自审核对点，全部通过）

1. **新建** `scripts/backtest/lane_f_grid_adapter.py`（MOD-BT-E1F-001 暂编号）：
   `latest_manifest()`（字典序=时间序取尾）/`load_axis_descs()`（schema YAML desc 真源，
   读不到退裸轴 id 不造词）/`recipe_to_hypothesis()`（确定性纯函数）/
   `convert_manifest()`（纯读，单行 values_json 损坏记 skipped_malformed 不炸整批）/
   `run_intake()`（幂等过滤→CAS 追加卸账；空批不落空文件；台账存在但不可读=RuntimeError
   fail-closed 防重复卸货）。
2. **candidate_id=`F06-<recipe_id>`**：recipe_id 本身内容寻址 → 跨批重复 recipe 同 id 跳过。
3. **假说转换语义（机制缺失如实降级）**：批次出处+recipe_id+全参数轴（desc 真源翻译）+
   prefix_key 差异维+降级维+样本内指标（标注"仅描述性证据非机制主张"）+显式声明
   "网格产物不带机制叙事，不编造机制"——把六问之5（数据挖掘巧合）诚实交 E2 判。
4. **挂接**（factory_intake_pipeline，两处编辑）：F 条目 intake 改指
   `lane_f_candidates.csv`+销欠账注释；`run_pipeline` 内 fail-open 接续
   `run_intake(dry_run)`，台账存在才进 `intake_sources["F"]`。
5. **不碰**：intake_ledger_recon.py（LEDGER_CHANNELS 缺 F=unknown_ledger，登记不代修）、
   其他车道模块、executor。

## 三、红绿测试证据

- **红相**：`git show HEAD:scripts/backtest/factory_intake_pipeline.py` 载入断言
  `F intake=="data/strategy_intake/lane_f_candidates.csv"` → **FAILED**（旧值=幻影
  grid_latest_manifest.csv；HEAD 无 lane_f_grid_adapter 接线、intake_sources 无 F）。
- **绿相**：新增 `tests/backtest/test_lane_f_grid_adapter.py` **15/15 passed**（真实 manifest
  样本逐字夹具，tmp_path 零生产路径）：四列契约映射/确定性/轴 desc 真源+裸轴降级/损坏行不炸/
  空批诚实/写后幂等复跑（written=0, skipped_existing=2）/dry-run 零写/空批不落文件/无批 no_batch/
  损坏台账 fail-closed/最新批解析/E2 读端契约（load_candidates+select_pending 幂等）/
  values_json 回溯。
- **回归**：test_factory_intake_pipeline 14 + test_intake_ledger_recon 18 +
  test_hypothesis_precheck 29 = **61 passed**（既有 run_pipeline 桩测在 F fail-open 下不破）。
- lint：ruff check/format 全绿（import 排序+格式已 --fix）。

## 四、端到端验证（真实链路一发）

| 步骤 | 结果 |
|---|---|
| adapter CLI 空批（最新=09-29） | `status=empty_manifest, written=0`，不落文件（诚实缺） |
| adapter CLI dry-run（024947 批） | `converted=3700, written=0` |
| adapter CLI 真实回填 024947 | `written=3700` → lane_f_candidates.csv 3,701 行/7.7MB，CAS `after_sha256=90cb495a…` |
| 幂等复跑同批 | `status=no_new, skipped_existing=3700, written=0`，台账仍 3,701 行 |
| E2 真实一发 `--limit 1` | batch E2-20261001-010249：**passed 1**（F06-6a48983995b8，pass_mechanism_clear，conf 0.95）**落 CH 台账**；首轮 LLM 读超时 fail-open 转 defer 未写脏（重发即正常） |
| CH 幂等集核验 | 终局集恰 1 个 F06-* id（首轮超时零残留） |
| pipeline dry-run 端到端 | exit=0；report 含 `F_grid_adapter`（empty_manifest 诚实）+`E2_F`（prechecked 1/passed 1）；e3_ready 出现 `F06-540d2caf63ce`——真实发过的 6a48983995b8 被 CH 幂等集正确跳过审下一条 |

## 五、六向台账

| 向 | 内容 |
|---|---|
| 上游触发 | ZephyrAlpha_F06Grid 计划任务→factory_grid_executor 落批次；本适配器由 E1 编排/夜批/人工 CLI 触发（无常驻循环） |
| 下游消费 | hypothesis_precheck（E2 幂等消费 lane_f_candidates.csv）→ E3 构造排产 |
| 输入 | grid_*/manifest.csv（9 列 schema）+ position_recipe_grid_schema.yaml（轴 desc 真源） |
| 输出 | data/strategy_intake/lane_f_candidates.csv（14 列=E2 四列契约+溯源/指标/values_json）+ run_intake 报告 dict |
| 真源锚 | MOD-BT-091（E2 契约）/MOD-BT-196（executor）/position_recipe_compiler（recipe_id 派生）/file_utils.safe_write_text（CAS 写口） |
| 耗时账 | 挖矿→施工→验证全程约 2h；3700 行转换+CAS 落盘秒级；E2 单条 LLM 判定 60-120s 级（qwen3:8b） |

## 六、自审闸三态

- **挖干**：manifest schema/批次盘点/E2 契约/幂等链/转换语义——消费断点全链打通，欠账销项。
- **未干（登记移交）**：① `intake_ledger_recon.LEDGER_CHANNELS` 未登记 lane_f_candidates.csv
  （对账走 unknown_ledger fail-open——表在他文件，本环节不碰，登记待总包/后续批补登记）；
  ② 全历史 2.46 万行 recipe 仅回填 024947 批（3,700 行）——其余批次回填属数据面决策，
  适配器幂等可随时 `--manifest` 补；③ 新建 .py×2 的 CREATE-GUARD token 与翻译册登记=
  总包统一登记（lane_f_grid_adapter.py、test_lane_f_grid_adapter.py）。
- **不可挖**：无。

## 七、改动清单（worktree，未 commit——禁令遵守，交总包分簇提交）

| 文件 | 性质 |
|---|---|
| scripts/backtest/lane_f_grid_adapter.py | 新建（适配器） |
| tests/backtest/test_lane_f_grid_adapter.py | 新建（15 测试） |
| scripts/backtest/factory_intake_pipeline.py | 修改（仅 :73-84 F 条目注释+intake 路径、:184-195 run_pipeline F 接续，diff 已核纯净） |
| data/strategy_intake/lane_f_candidates.csv | 新建（真实回填产物 3,700 行，git 跟踪待遇同其他人道台账，随簇提交或总包裁量） |

> 注：worktree 另有并行代理在途改动（lane_c_formula_miner/trend.py/ps1 系），本环节零接触；
> 开工时点 git status 干净，factory_intake_pipeline.py 的 diff 经逐行核对纯本环节编辑。
