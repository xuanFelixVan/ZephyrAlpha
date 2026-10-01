---
ttl: task_bound
title: e1_mine_repair (20261001 删除事故后重建)
note: 重建件
---

# E1 挖矿数值修复环节簿（车道C 夜链 20261001）

> 会话 st-lanech-20261001 / 车道C E1 / 施工区 worktree `D:/ZephyrAlpha/.worktrees/st-lanech-20261001`（基线 dev HEAD=68fe30bd）
> 病根三处：miner residualize 不滤 Inf / _fitness 无兜底 / MCGINLEY 断层上溢。照方施工，红→绿全程留证。
> 注记：本簿原落主区 `docs/_working/lane_c_chain_night_20261001/`，20261001 他队清理事故删除（untracked 无护盾）后重建于 worktree git 跟踪目录，内容按施工时点原文复刻。

## 0. 自审闸三态结论：**挖干**

三处病根全部修复且红绿证据闭合；真实面板探针（只读）+ smoke 挖掘一发全通过。
残余风险两条（见 §6），均不阻断本环节交付。

## 1. 改动清单（全部在 worktree，未 commit——总包统一收口）

| 文件 | 改动 |
|---|---|
| `scripts/backtest/lane_c_formula_miner.py` | ① `residualize()`（:213）mask 双侧全滤：`~np.isnan(baseline).any(axis=1)` → `np.isfinite(baseline).all(axis=1)`；`lstsq` 包 `try/except np.linalg.LinAlgError → return x.copy()`（放弃残差化不炸批）。② `make_incremental_ic_fitness()._fitness` 整体包 `try/except Exception → return 0.0`，签名 (y, y_pred, _w) 不变保持 gplearn 兼容 |
| `src/zephyr/factor/technical_indicators/trend.py` | `MCGINLEY.compute`（:657）递推前播种检查 `np.isnan(prev)` → `not np.isfinite(prev) or prev <= 0` → 重置播种 `prev=c[i]`（与 NaN 播种同语义）；输出前 `md[~np.isfinite(md)] = np.nan` 终防护；docstring 写明断层自愈语义 |
| `tests/backtest/test_lane_c_formula_miner.py` | 新增 `TestResidualizeInfGuard`（2 例）+ `TestFitnessExceptionGuard`（1 例），23 例→26 例 |
| `tests/backtest/test_mine_numerics.py`（新建，tests/ 豁免 CREATE-GUARD） | `TestMcGinleyGapSelfHeal`（2 例：断层全有限/重置回价格量纲）+ `TestMcGinleyRegression`（2 例：恒价/上行滞后，零 talib 依赖） |

diff 规模：miner +31/-12 行内、trend +16/-2、test 文件 +38；零其他文件触碰（探针脚本在主区 `.runtime/tmp/`）。

## 2. 六向台账（按修复对象）

### 2.1 MCGINLEY.compute（md_14 生产端）

| 向 | 内容 |
|---|---|
| 上游触发 | TI 日频计算链（`market_technical_indicator` 生产/回填）；断层数据源=个股单日大跌（实证形态 44→12.6，单日 -71%） |
| 下游消费 | md_14 落 CH `market_technical_indicator` → `lane_c_formula_miner.fetch_panel()` 的 baseline 矩阵（REG-IND-001 基座 212 列之一）→ `residualize()`（旧 Inf 直接炸 lstsq，本链闭环） |
| 输入 | `DataFrame["close"]` |
| 输出 | `DataFrame["md_14"]`（修复后保证全有限） |
| 真源锚 | `src/zephyr/factor/technical_indicators/trend.py::MCGINLEY`（docstring 含语义）；回归=`tests/zephyr/factor/technical_indicators/test_trend.py::TestMcGinleyNumeric`；新增=`tests/backtest/test_mine_numerics.py` |

### 2.2 residualize（增量 IC 基座剥离）

| 向 | 内容 |
|---|---|
| 上游触发 | `make_incremental_ic_fitness()._fitness`（gplearn 每个体评估各一次，热路径） |
| 下游消费 | 返回残差向量 → `rank_ic()` → gplearn fitness |
| 输入 | `x (n,)` 候选因子、`baseline (n×m)` TI 基座 |
| 输出 | `(n,)` 残差（x 或 baseline 非有限的行=NaN；有效样本<10 或 lstsq 奇异→退回 x.copy()） |
| 真源锚 | `scripts/backtest/lane_c_formula_miner.py:213`；测试=`tests/backtest/test_lane_c_formula_miner.py::TestResidualize*`（3 旧+2 新） |

### 2.3 make_incremental_ic_fitness._fitness（验收评分）

| 向 | 内容 |
|---|---|
| 上游触发 | gplearn `generations` 评估循环（smoke 30×3，正式 1000×50） |
| 下游消费 | gplearn fitness 矩阵（越大越好） |
| 输入 | `(y, y_pred, w)`（gplearn 契约签名） |
| 输出 | float 增量 rank IC；任何异常→0.0（单公式报废不炸批） |
| 真源锚 | `scripts/backtest/lane_c_formula_miner.py:235`；测试=`TestFitnessExceptionGuard` |

## 3. 红绿证据（命令+读数）

### 红（修复前）

1. **inline 旧逻辑复算**（断层序列 `[44,44.45,43.98,12.6]`+40 日 2% 波动）：
   `i=4 → 1.6288e8`，`i=5 → -1.9390e19`，**首个非有限值 i=32**（约断层后 29 bar），
   `RuntimeWarning: overflow encountered in scalar divide`——与工单"|prev| 每轮指数放大、约 25 个交易日上溢"吻合。
2. **新测试先跑（未修码）**：`python -m pytest tests/backtest/test_lane_c_formula_miner.py::TestResidualizeInfGuard tests/backtest/test_lane_c_formula_miner.py::TestFitnessExceptionGuard tests/backtest/test_mine_numerics.py -q`
   → **5 failed, 2 passed**（2 个 passed=常规序列回归例，修复前后都应绿）。
   失败明细：residualize 2 例（Inf 进 `lstsq` → LinAlgError）、fitness 1 例（注入 RuntimeError 直接上抛）、MCGINLEY 2 例（trend.py:689 overflow）。

### 绿（修复后，均以 `ZEPHYR_ALPHA_ROOT=<worktree>` 运行，见 §5 环境注记）

| # | 命令 | 读数 |
|---|---|---|
| G1 | `python -m pytest tests/backtest/test_lane_c_formula_miner.py -x -q` | **26 passed in 1.83s**（23 回归+3 新） |
| G2 | `python -m pytest tests/backtest/test_mine_numerics.py -q`（与 G1 合跑 30 passed in 4.32s） | **4 passed** |
| G3 | `python -m pytest "tests/zephyr/factor/technical_indicators/test_trend.py::TestMcGinleyNumeric" -q` | **2 passed in 4.02s**（现有回归不破） |

### 面板探针（只读，脚本=`D:/ZephyrAlpha/.runtime/tmp/lane_c_e1_probe.py`，保留待总包清理）

- `fetch_panel(universe_n=40, days=250)` 真实 CH 面板：**n=9611，baseline 212 列，universe=40**；
  baseline Inf=0 / NaN=54843，X Inf=0 / NaN=0（当前批次基座无 Inf，以注入 Inf 复现缺陷形态）。
- 注入 Inf 基座 ×7 特征列：Inf 行剔除记 NaN、其余行全有限、**不崩** → OK。
- 真实基座原样全列残差化：不崩 → OK。
- `make_incremental_ic_fitness` 真面板验收：X0 增量 IC=**0.0241**（有限）→ OK。
- 全 Inf 基座：退回 `x.copy()` → OK。总裁定：**PROBE PASS**。

### smoke 挖掘一发（真实数据全流程）

`python scripts/backtest/lane_c_formula_miner.py mine --smoke --population 30 --generations 3 --universe-n 40 --dry-run`
- batch=`E1C-20261001-005649`；E0 闸 `gate_deny_calendar_unknown` 拒 → `--smoke` 工程烟测豁免放行（符合脚本设计）；whitelist_status=**active**。
- 主链无崩溃，产出候选（top `incr_ic=0.013905`，`ts_corr_20(ts_delta_5(mul(-0.614, close_ma20)), ...)`）。
- `--dry-run` 未写台账；worktree `data/strategy_intake/` 无落盘。

## 4. 耗时账（实测）

| 项 | 耗时 |
|---|---|
| miner 测试文件全量（26 例） | 1.83s |
| miner+numerics 两文件合跑（30 例） | 4.32s |
| test_trend MCGinley 回归（含 talib importorskip） | 4.02s |
| 面板探针（CH 拉取 n=9611+212 列 + 7 列残差化×2 轮 + fitness） | 秒级（远低于 300s 超时） |
| smoke 挖掘（30×3，真面板） | 约 1 分钟级（两连发均在超时窗口内完成） |
| 红复算+红测试轮 | 秒级 |

## 5. 环境注记（对总包/后续车道重要）

1. **ZEPHYR_ALPHA_ROOT 必须指向 worktree**：usercustomize（LSG 网引导）启动时预载主区 206 个 `zephyr.*` 模块进 `sys.modules`，不设该变量时 pytest 的 `zephyr.*` 导入全部命中主区旧代码（本次 MCGINLEY 测试先红后仍红即此因，`find_spec` 与实际 import 分裂为实证）。设 `ZEPHYR_ALPHA_ROOT=<worktree>` 后 usercustomize 挂 worktree src，LSG 拦截器保持在岗（`runtime_interceptor` 已验证 in sys.modules）。`scripts.*` 命名空间不受影响（miner 自插 `_ROOT`）。
2. **他队在途改动通报**：施工期间 worktree 出现非本车道改动——`factory_intake_pipeline.py`、`register_factory_lane_c_task.ps1`、`register_ollama_serve_task.ps1`、`run_factory_lane_c.ps1`（M）+ `lane_f_grid_adapter.py`、`test_lane_f_grid_adapter.py`（??），疑车道F同 worktree 在途。本车道未触碰；开工时点这三目标文件 diff 干净（0 dirty）已核实。总包收口时请注意隔离归属。

## 6. 残余风险（如实登记，不阻断）

1. **断层 bar 当日过渡值**：MCGINLEY 重置语义下，断层当日单次递推可能留下一个有限过渡异常值（如 -514），次轮即重置回价格量纲（终防护只清非有限）。语义已写进 docstring 与 `test_gap_sequence_reseeds_to_price_scale`；若 Owner 要求断层 bar 直接记 NaN，改动点=递推后 `if prev <= 0: prev=c[i]; md[i]=prev` 前插一行 `md[i]=np.nan`，一行级。
2. **residualize 只捕 LinAlgError**：`lstsq` 契约内奇异=LinAlgError 已兜住；其他意外异常由 `_fitness` 外层 `except Exception → 0.0` 二级兜底，批级不炸。
3. 主区探针脚本 `.runtime/tmp/lane_c_e1_probe.py` 按指示保留，总包清理。
