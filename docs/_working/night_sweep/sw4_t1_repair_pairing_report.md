---
ttl: task_bound
completes_when: "T1 三阻断处置对拍证据链闭环（卡1 ②③）：补跑 A/B 双跑对拍 + 直调引擎第三证 + 哨兵复跑判据五转绿"
---

# SW4 · T1 三阻断处置对拍小报告（st-nightsweep-sw4-20260929）

> 对象 run：`data/strategy_intake/grid_20260926-024947`（T1 3700 格，机判 RED：manifest 3698≠3700 / backtest_dead=2 / cost_gate 28/50）
> 性质：只读对拍+定向补跑+产物合并修复；不改预注册判据一字（config/search_space_prereg.yaml、config/exam_scale_cost_gate.yaml 零触碰）。

## 1. 缺格定位（②）

`negatives.csv` 在册 2 阴格即缺格（3698+2=3700 守恒）：
- `d6759a48a594`：A2=halflife60 × C=kelly_050 × B=top10 × E=cap10 × G=all_a_ex_st
- `4bdf3555a27d`：同族 × B=top20 × E=cap5
- 死因：`backtest_fail:RuntimeError insufficient_net:1622`（executor 的零方差 fail-closed 分支）

## 2. 补跑对拍（③，三证）

**证据 run**（工厂执行器单窗补跑，窗口 2019-01-04~2025-09-09，引擎=HEAD 62898892 版）：
- runA=`grid_20260929-040003`、runB=`grid_20260929-040141`（subspace 钉死 kelly_050×halflife60×all_a 4 组合笛卡尔）
- 两 run 4 格死因逐字段一致（backtest_layer / insufficient_net:1622）→ **确定性复现**
- 直调引擎第三证（绕过执行器，evaluate_recipe+run_backtest_full 直算）：
  两阴格 weights 全期零仓位（sum_w=0，1622/1622 日）→ net 恒 0 → std=0 → 引擎拒收；
  runA/runB/直调三者净值序列哈希一致（342432347427）→ **配方内生阴性实锤**（kelly_050 sizing 对该配比全程零仓位，非引擎 bug、非数据漂移）

## 3. 处置（②，阴性如实入册）

- `manifest.csv` 3698→3700：2 行按原 schema 追加（sharpe 留空=零方差无定义；`negative_note` 列标注 `endogenous_zero_variance` + 证据 run 指针；values_json/degraded/net_days 取直调实测）
- `negatives.csv` 清空为表头（2 行转入 manifest，negatives_discipline 3700+0=3700 守恒）
- `summary.json`：backtest_dead 2→0、evaluated=3700、追加 `repair` 留痕块（会话/日期/证据 run/处置）
- 旁证：4 组合中另 2 组合（top10×cap5=c62af220787d、top20×cap10=987c6b1a8120）同为内生阴性 → 该族（kelly_050×halflife60×all_a）整族死，与原 T1 抽样空间自洽

## 4. 哨兵复跑（④⑤⑥）

- t1_t2_handover.py 正式巡检（fresh replay，manifest sha 变更→缓存失效重放 50 格）
- **5/6 判据转绿**：manifest_points=3700 ✓ / dead_zero=0/0/0 ✓ / degraded_zero=0 ✓ / negatives_discipline ✓ / n_eff=19 ✓
- **cost_gate_spot 仍 RED**：新样本 50 格重放 30 格 40bp 档 sharpe<0（survival_floor=0），非单调=0；失败中位 40bp-sharpe=−1.689
  归因（50 格内）：H_turnover_lambda=lambda_0 失败率 84%、B_top_n=top10 85%/top20 80%、D2=drift_band 70% —— 高换手/高集中簇结构性破 40bp 存活地板
- **T2 未发车**（verdict RED → 发车序列未进入，fail-closed 正确行为）；按卡⑥如实报 BLOCKED：差 30 格、缺=40bp 档正 sharpe 格点；解锁需 Owner 门位（survival_floor 判据调整走声明通道）或新搜索空间 T1
- 修复面旁证：修复前样本 28/50 破地板（不同格集），修复后 30/50 → 破地板是网格质量结构属性，与本次修复无关

## 5. 附带修复（发车路径实障）

`t1_t2_handover.py` 发车命令给 `--subspace-json` 传**文件路径**，而执行器 main 按**内联 JSON** `_json.loads(args.subspace_json)` 解析 → T2 即便判据全绿也必 JSONDecodeError 秒崩（LAUNCH_FAILED 循环）。
已改传内联内容 + 测试断言同步（tests/backtest/test_t1_t2_handover.py 7 passed）。

## 6. 证据指针

- 修复产物：`data/strategy_intake/grid_20260926-024947/{manifest.csv,negatives.csv,summary.json}`
- 对拍 run：`data/strategy_intake/grid_20260929-040003/`、`grid_20260929-040141/`
- 判决：`data/strategy_intake/grid_20260926-024947/handover_verdict.yaml`（generated_at=2026-09-29 巡检）
