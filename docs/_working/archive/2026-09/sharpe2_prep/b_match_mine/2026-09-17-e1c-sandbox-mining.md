---
ttl: task_bound
---

# E1C 车道沙箱增量挖掘（新适应度口径 IC_IR）— Sharpe2 决赛准备战·分包 B 任务③

- 会话：st-sharpe2b-20260917 ｜ 日期：2026-09-17 ｜ 性质：沙箱文档（**一个候选都不写库/不进 intake CSV/不进注册表**）
- 底档：`.runtime/tmp/sharpe2b/e1c_sandbox/result.json`（批号 E1C-SANDBOX-20260917-031345）
- **再生声明**：本件系第三度自底档机械再生（原始生成 st-sharpe2b-20260917；再生原因=他会话 worktree pre_merge stash 扫走事故两起，本件前两版分别于当日 03:05-03:16 与 04:41 前后被扫离工作区，无 stash 可恢复）。全部数字由底档 result.json 机械重导出，经核对与原版一致。

## 0. 通道定义核对（真源只读）

- 车道：`config/strategy_production_map.yaml` 节点 FAC-E1C"车道C-公式挖掘机"（stage=E1, lane=C, build_status=partial, module_ref=MOD-BT-155）。三轨=gplearn（MOD-BT-155）/智能体（MOD-BT-158）/MCTS（历史笔记；本批考证 production map 未单列 MCTS 节点，AlphaGen 为 design_ref）。
- 算子约束真源：`config/factor_mining_whitelist.yaml`（active；批准算子 14 个=arithmetic 4+nonlinear_safe 4+order_stat 2+ts_cs 4；禁 sin/cos/tan/inv；Owner 四裁定=双轨分期/增量IC基座 REG-IND-001/种群 1000×50/白名单审定制）。
- 既有批次：`data/strategy_intake/` 现存 14 个 `grid_*` 批目录（最新 grid_20260917-003812）+ lane_c_candidates.csv。生产适应度=**对 REG-IND-001 基座（technical_indicator 124 列日频）残差的增量 IC 均值**（`lane_c_formula_miner.make_incremental_ic_fitness`），FWD=5 日。

## 1. 增量点（三选一：新适应度口径）

**生产口径只看增量 IC 均值——对"块间稳定性"与"前后半程一致性"盲视**。本沙箱增量=新适应度口径：

1. **IC_IR**：把面板按日期码时序切 6 块，逐块算残差增量 IC，取 `mean/std`（方向随均值符号）——惩罚"某一段独强、其余段平庸"的一次性幸运公式。
2. **70/30 后半程验证**：时间序前 70% 与后 30% 两段的增量 IC 必须同号为正才入"稳健池"。

生产件（`lane_c_formula_miner.py`/`lane_c2_agentic_miner.py`/`factory_intake_pipeline.py`）**只 import 不改**；gplearn 装配复用 `SymbolicTransformer`+白名单 function_set，搜索/验收分离语义与生产一致。

## 2. 跑批规模（诚实声明）

| 项 | 本沙箱 | 正式档（Owner 裁定） |
|----|--------|---------------------|
| 种群×代数 | 80×5（工程烟测当量，与 sharpe2a 共库错峰让算力） | 1000×50 |
| 面板 | universe=成交额 top40 × 250 交易日（n=10,074） | 同构 |
| 基座 | REG-IND-001 技术指标 124 列 | 同 |
| 随机种子 | 42（白名单 constraints 同源） | 42 |

结论外推受限：本批为**口径对照试验**，不是正式量产，挖掘覆盖度远小于正式档。

## 3. 结果（79 个终端程序全评，数字自底档 result.json 机械重导）

- 生产口径（增量 IC 均值）>0：**24/79**
- IC_IR 口径 >0：**21/79**
- 两口径 Top10 重合：**5/10**（IC_IR 把深嵌套 ts_corr 复合式提进了前十——它们均值 IC 不冒尖但 6 块全正，正是新口径要捕捉的稳定性）
- **稳健池（双口径为正+前后半程同正）：13 个**

### 稳健池前列（沙箱候选清单，[0] 号自底档导出）

| # | 公式（截断） | IC_IR | 增量IC | 前70% IC | 后30% IC | 长度 |
|---|-------------|-------|--------|----------|----------|------|
| 1 | ts_corr_20(ts_delta_5(ts_corr_20(ts_delta_5(mul(-0.614,close_ma20)), min(close_ma20,ts_zscore_20(vol_20d)))), …) | 1.6076 | 0.0212 | 0.0039 | 0.0631 | 15 |
| 2 | ts_corr_20(ts_delta_5(ts_corr_20(ts_delta_5(mul(-0.614,close_ma20)), min(rank_cs(ret_1d),ts_zscore_20(vol_20d)))), …) | 1.4924 | 0.0229 | 0.0004 | 0.0861 | 16 |
| 3 | ts_corr_20(ret_1d, min(close_ma20, ts_zscore_20(vol_20d))) | 1.1732 | 0.0577 | 0.0476 | 0.0665 | 6 |
| 4-8 | 同簇变体（gplearn 重复个体与 min/mul 组合式，明细见底档 stable_pool 全列） | 0.78-1.17 | 0.049-0.058 | 0.033-0.055 | 0.033-0.067 | 8-9 |

机制自述（大白话）：优势簇=**日收益与"量能标准化×20 日乖离压缩"的 20 日滚动相关**——量价背离结构族（ret 与 vol_z 的相关越负→放量下跌越狠→反转弹性越大），与既有三因子基座（动量/低波/乖离）信息面不同源；#1/#2 是该族的二阶变化率版本（IC 稳定但均值小、式子长，过拟合疑点更高）。

### 口径对照发现（增量点的价值证据）

- 新口径淘汰了生产口径前十里"重复个体刷榜"的部分（`ts_corr_20(ret_1d, min(close_ma20, mul(-0.614,close_ma20)))` 这类同式变体在生产口径前十占 3 席，IC_IR 前十里被复合稳定式替换 4 席）。
- `mul(-0.614, close_ma20)` 单因子（负乖离反转）在两口径都上榜——回归基座残差后仍存的裸反转暴露，提示基座 124 列未完全吸收反转效应（对基座完整性是一次反向体检）。

## 4. 为什么一个都不进注册表（硬约束声明）

1. 规模不达标：80×5 远低于 Owner 裁定的 1000×50，样本选择偏差不可控；
2. 流程未走：E2 幂等预审/E3 构造环/E0 问闸（heavy 档）均未执行——沙箱无权自我评分；
3. 验收未做：对既有 lane_c_candidates/grid_* 幸存者的表达级+相关级去重未跑，增量 IC 声明未经正式面板复核；
4. 纪律：写入 intake CSV/注册表/CH 表的动作一个都没做（本批零写库，产物=本文档+tmp json）。

**下批建议**：稳健池 13 个可作下批正式档（1000×50）的种子注入（lane_c 已有假说反哺机制），或先跑对 grid 批幸存者的相关级去重再决定是否值得种子化。

## 5. 可复现附录

```bash
# 沙箱挖掘脚本(生产件只读 import, 零改动零写库)
python .runtime/tmp/sharpe2b/e1c_sandbox_mine.py
# 关键实现:
#   面板/白名单/算子集: lane_c_formula_miner.fetch_panel/load_whitelist/build_function_set
#   IC_IR: 按 date_codes 切 6 块 → 逐块 rank_ic(residualize(pred, baseline), y_fwd5) → mean/std
#   后半程: date_codes 70/30 切, 两段增量 IC 同号为正才入稳健池
#   底档: .runtime/tmp/sharpe2b/e1c_sandbox/result.json (批号 E1C-SANDBOX-20260917-031345)
# 共库礼仪: fetch_panel 撞 CH 内存上限(sharpe2a 在跑)时 30/60/90s 退避重试
```

合规声明：研究方法与工程产出，不构成投资建议；候选未经任何正式验收，禁止直接投产。
