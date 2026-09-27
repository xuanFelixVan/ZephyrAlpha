---
ttl: task_bound
title: F23 E4 考试咽喉（全厂唯一判定权）——L03 接线矿道案卷
session: zc-l03-20260927
---

# F23 · E4 考试咽喉

> 挖矿基册=01_strategy_factory/b2_f23_e4_exam.md（SF-B）。本卷=09-27 独立复核+增量（台账 +10 行/滞留 9→11 天/FACT 及格 5→6/考卷件 91→85 勘误）。

## 一、六向台账
| 向 | 实证锚点（09-27 实测） |
|----|------|
| 上游 | translated/ **85 个 c4_*.py（含 c4_fact_* 6 件）**——基册"91 文件"系 85+6 双计（勘误③）；f06_survivors.csv 1 行（38b453ca）；E2 过审 13 条（race 实测 D8+B4+C1，与 L02 卷 13 维持） |
| 下游 | c1_backtest.strategy_screen 台账 **total=1351（基册 1341，+10）/uniq 574**（strategy_screen_query.py summary 实跑）；c4_batch_completed→intake；E4 档案 data/backtest_artifacts/runs/ **154 项**（SCR-C4-*/E4-F06-38b453ca/E4-BIZMINE-* 在盘） |
| 自动触发 | 无计划任务；c4_batch_due=HEAVY（pipeline_events.py:143 实证 `HEAVY_KINDS=frozenset({"c4_batch_due"})`）只经显式 drain；**滞留 2 条 PIPE-20260916-* attempts=0，11 天未 drain（基册 9 天，恶化）**=BP-3 未执行 |
| 真源注册表 | 图 FAC-E4 built；MOD-BT-039/076/211/IBT-REEXAM/194/200 TrialLedger；判定管线 run_strategy_validation+DecisionGate+OverfittingDetector；config/exam_scale_cost_gate.yaml 在盘（tiers_bp=[0,5,10,20,40] 实读） |
| 门禁质量尺 | IS 冻结窗；DSR N 缺失 fail-closed；RB-STATS-01 证据充分性闸；OOS/IS<0.70 线；成本门五档单调+全档存活+换手≤8x；落库未确认 RuntimeError |
| 运行状态 | **绿（人工批考）+红（自动链关隘）**。bothwin tested=85/passed=16（其中 **FACT 件 6 个全及格**——基册"5 件"勘误②）；f06 判定列三阶段 FAIL 在案（判定权真实咬人）；批次清单无任何 f06 批=BP-4（F06 判定不进统一台账）维持 |

## 二、子模块三级枚举
1. **代码面**：c4_batch_screen.py（:216-223 OOS 终点=动态"上个周六"实证未变；`--auto-only/--defer-emit`）；f06_e4_wfa_exam.py（三阶段正考）；exam_cost_reexam.py；distribution_forecast_eval.py；src/zephyr/backtest/core/n_trial_ledger.py+strategy_validation_pipeline.py。工作树与 HEAD 一致（git status 空，无在途改动）。
2. **注册表/文档面**：c1_backtest.strategy_screen（考试成绩+判定书主档，幂等四键 batch/sid/verdict/source_file）；FAC-E4 图节点；m2_backtest_sim/05_cost_gates.md 交叉（成本门哑门病史已闭+CONSUMERS 在码；**E4 存活 17 vs 修后成本合格 3 池基悬空**=邻册待裁案）。
3. **数据面**：runs/ 154 项；pending_events.jsonl 6 条（c4_batch_due×2 attempts=0＋pf_alloc×3 毒丸＋sim_observe×1 毒丸）；bothwin 16 名单含 6 FACT+10 CAND。

## 三、接线四态独立复核
- 总册 built → **维持 built**（判定引擎/台账/成本门/档案全实证）。
- **骨架勘误**：①基册"translated 91 文件（含 6 fact）"双计——实为 **85 件（含 6）**（c4_*.py glob 本身含 c4_fact_*）；②"passed=16 含 FACT 5 件"→09-27 复测 **6 件全及格**；③滞留天数 9→**11**（attempts=0 无任何 drain 发生）。总册 F23 行 built 判定与 L02 交叉一致，无态变。
- L02 三 P0 交叉：过审-考卷转化率 4/13 **维持**（13 pass vs 考卷件 4=3 翻译 D+1 构造 C）。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | c4_batch_due 滞留 11 天（2 条 85+1 件） | pending_events attempts=0 since 09-16 | Owner 派工 `pipeline_events drain --allow-heavy`（分钟级）；纳入月度审计班 | **P0** |
| 2 | 过审→考卷转化 4/13，9 条滞留（B3 llm_error+D4 未试+2 阴性） | race 计分板 13 vs manifest 考卷 4 | L02 缺口①同案：统一排产器；llm_error 幂等占坑解除 | **P0** |
| 3 | F06 判定不进 strategy_screen（平行判定权） | summary 批次清单 0 条 f06 | BP-4：判定行追加落账或 screen_source 联查，M 级 | P1 |
| 4 | E4 存活池 17 vs 成本合格 3 池基悬空 | m2 05 册堵点 3 | 邻册 pending_rulings 同案（IBT-B04） | P1 |
| 5 | E4a/E4b 拆分开放决策点 | 图上原样挂 | 待裁，不阻断 | P2 |
| 6 | OOS 终点=动态周六与冻结语义张力 | :216-223 | 观察项+月度窗口漂移播报（BP-7） | P2 |

## 五、自审闸三态
**挖干可施工（复核维持）**。六向全实跑复核；built 成立；增量=台账+10/FACT 6/滞留恶化 2 天/考卷件计数勘误。E4a/E4b 与池基悬空=待裁单列。

## 六、复跑命令
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python scripts/backtest/strategy_screen_query.py summary   # total=1351/uniq=574
python scripts/backtest/strategy_screen_query.py bothwin   # tested=85/passed=16（FACT×6）
python -c "import json;[print(e['id'],e['attempts']) for e in map(json.loads,open('.runtime/strategy_pipeline/pending_events.jsonl',encoding='utf-8')) if e['kind']=='c4_batch_due']"
ls scripts/backtest/translated/c4_*.py | wc -l             # 85（含 fact 6）
python scripts/backtest/factory_intake_pipeline.py race    # passed 8+4+1=13
```
