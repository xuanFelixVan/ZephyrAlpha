---
ttl: task_bound
title: F70 模拟撮合与偏差检测——L08 复飞矿道案卷（涨板队列/前视偏差/过拟合保护/DSR）
session: zc-l08-20260927
---

# F70 · 模拟撮合与偏差检测

> 总册行：G 段 F70，状态 built，P1，上游 F65 回测引擎族、下游 F72 模拟盘日跑。M0=B7。
> 本卷=09-27 复飞复测。第一证据源实扫 `src/zephyr/simulation/`；姊妹带 g_backtest_gpu（F58-F69 卷族）无 F70 专卷，其 F65/F66/F69 卷为消费侧交叉。

## 一、六向台账（实证锚点）

| 向 | 内容（09-27 实测） |
|----|------------------|
| 上游输入 | F65 回测引擎（`src/zephyr/backtest/core/matching_engine.py`）产出的成交/行情序列；F64 三册（universe/benchmark/cost_model）参数；F66 预注册阈值 |
| 下游消费 | 消费方 grep 实扫（09-27）：`backtest/core/decision_gate.py`、`backtest/core/metrics.py`、`backtest/core/overfitting_adjudicator.py`、`backtest/regime_validation/c4_deflated_sharpe_runner.py`（F69 考试成本双口径门的 DSR 腿）、`factor/analysis/correlation_overfitting_audit.py`、`position/core/position_recipe_compiler.py`、`regime/validation/overfitting_guard.py`、`shared/_cross_layer/ml_experiment_pipeline.py`；下游终端=F72（sim 日跑复用同一成本模型，PR-A 册 §三-2） |
| 自动化触发 | 本环节为**库件无自触发**（无计划任务无槽位，schtasks 09-27 全查零 simulation 命中）；被 F66 七步循环/F69 考试链在测内调用 |
| 真源与注册表 | 包=`src/zephyr/simulation/`（09-27 find 实测 **23 个 .py**）；docs/library/pipeline.md 管线馆 89 条目含 tasks.yaml/register_guard_tasks.ps1 等调度件（F70 本体不在馆册=库件免册） |
| 门禁与质量尺 | overfitting_protection_gate=过拟合保护门；look_ahead_bias_detector=前视偏差检测；deflated_sharpe_calculator=DSR（#306 尺 suspect 风波的上游器件，尺本体在 standards.yaml） |
| 当前运行状态 | built 维持（消费方 8 处实扫在）；本卷零实跑（库件，跑态归 F66/F69 测链） |

## 二、子模块三级枚举（09-27 实扫）

1. **顶层件（14 支实存）**：`limit_board_queue.py`（涨板队列撮合）、`look_ahead_bias_detector.py`（前视偏差）、`overfitting_protection_gate.py`、`deflated_sharpe_calculator.py`、`divergence_attributor.py`、`parameter_robustness_tester.py`、`pipeline_base.py`、`quality_assurance_selfdrive.py`、`result_analyzer.py`、`risk_simulator.py`、`scenario_generator.py`、`sharpe_calculator_fixer.py`、`strategy_simulator.py`、`volume_aware_impact.py`。
2. **子包**：`implementations/default_experiment_pipeline.py`（唯一实件）；`core/`、`api/`、`services/`、`models/`、`infrastructure/`、`_extensions/` 六包**均仅 __init__.py 空壳**（预留结构，零内容）。
3. **测试面**：本卷未逐支验测试在盘（漏挖登记，见 §四-5）；消费侧测试归 c4_deflated_sharpe_runner/regime overfitting_guard 各自带。

## 三、接线四态独立复核

- 总册 built → **维持 built**（消费方 8 文件实扫非零，四态=已接线）。
- **骨架勘误**：①总册 F70 核心模块路径只列 3 件（look_ahead/overfitting_gate/DSR），实包 14 顶层件——涨板队列 `limit_board_queue.py` 未被骨架点名，恰是"模拟撮合"最撮合名义的件；②`core/api/services` 三空壳子包易被读成"三层已建"，实为预留位。

## 四、缺口清单

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | 六空壳子包（core/api/services/models/infrastructure/_extensions）零内容 | 按 w5_1 内收判据裁定：登记"跨域不同对象→不并"或摘壳 | P2 |
| 2 | DSR 器件被 #306 判 v1 尺 suspect 波及（dsr>0@N=4562 数学互斥）——器件本体无罪、尺要换 | 尺切换归 F74 堵点 1 同批（L08 05 卷），本件仅消费新尺 | P1（随 F74） |
| 3 | 前视偏差检测器无独立探活/消费证据（未在 8 消费文件 grep 命中名单前列） | 消费面逐件读码核实（归回测链复核批） | P2 |
| 4 | F70 与 F121 execution_simulation（research 三域设计态）名近易混 | 总册已分列，无动作，防混淆注记 | P2 |
| 5 | 本卷未逐支验 tests/（纪律：不臆造） | 待裁节登记 | P2 |
| STALE 13/假绿 5 | **不属 F70**（数据管线腿，归 F77 卷 §四标注） | — | — |

## 五、自审闸三态

**复核维持（部分挖干）**：包面实扫+消费方 grep 双源；缺口=测试面未逐支验（登记）、消费方仅到文件级未到 file:line（引用 PR-A/总册已给下游锚点）。三态=**维持 built，登记两条 P2**。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
find src/zephyr/simulation -name "*.py" | wc -l     # 23
ls src/zephyr/simulation/*.py | wc -l               # 14 顶层
grep -rln "zephyr.simulation" src/ scripts/ --include="*.py" | grep -v "src/zephyr/simulation" | wc -l  # 消费方
grep -rn "limit_board_queue\|look_ahead_bias" src/ --include="*.py" -l | head
```
