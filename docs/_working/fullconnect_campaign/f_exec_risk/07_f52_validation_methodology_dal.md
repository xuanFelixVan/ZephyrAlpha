---
ttl: task_bound
title: "F52 验证方法学与决策算法库——REG-VALM-001+REG-DAL-001+validation runner（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F52 · 验证方法学与决策算法库（REG-VALM-001 + REG-DAL-001）

> 节点级"怎么算对错"唯一真源（五类验证方法）+决策算法唯一登记处；消费件=validation runner 一问一考。
> 上游=F23/F35/F66；下游=182 节点置信度三态、S2 evidence 回填、S3 知识漂移预检。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | trading_decision_map.yaml 节点清单、data/backtest_artifacts/bt-*.json trade_log、两注册表 yaml |
| 下游消费 | c1_backtest.node_verdict 台账→前端 /api/tdm/validation+/api/tdm/verdicts；P2-1 衰减巡检（decay_watch）|
| 自动化触发 | **手动**——runner 无调度；decay_watch 调度挂载**本日 grep scripts/register_*.ps1 零命中复证**（登记遗留 Owner 二选一未解）|
| 真源与注册表 | docs/01_policies_and_standards/_registry/catalogs/{validation_method_registry,decision_algo_registry,backtest_backlog}.yaml；runner=src/zephyr/trading/validation/runner.py 645 行（MOD-TDMVAL-001，_VERDICT_TABLE="c1_backtest.node_verdict" :57 本日实锚）|
| 门禁与质量尺 | INVARIANTS：holdout 12 月/触发<30 pending/台账只追加/空数据不造假/verdict_reason 代码生成禁手填 |
| 当前运行状态 | **绿（机制）×黄（结论）**——台账 60 行实弹全 verdict=pending+insufficient_samples（holdout 保密窗纪律，"宁可 pending 不作弊"裁定 3）；decay checked=60/decayed=0 |

## 二、子模块三级枚举（本日实扫）

- **trading.validation**：runner.py 645（五方法分派：sensor_monotonicity/agg_discrimination/exec_quality/exit_counterfactual/portfolio_attribution；batch="L4"/"XFLOW"）｜decay_watch.py 251（建成+3 单测，调度未挂）｜ablation.py 304（建成+9 用例，run_ablation 零生产调用，实弹待 Owner 放行协议 §12）
- **注册表三册（本日计数）**：validation_method_registry.yaml **5 方法**（method_id 计数）｜decision_algo_registry.yaml **32 条**（15 production/5 trial/12 design）｜backtest_backlog.yaml **142 对象/132 个 plan:null**（本日 grep -c 实锚）

### 骨架勘误
1. 总册 F52 行"27 条 DAL 决策算法"——**实测 32 条**（漂移已在 19 册登记，本日复核仍 32，骨架行待回填）。
2. 总册 F66 行"backtest_backlog 137 对象"——**实测 142 对象/132 plan:null**（同批勘误，归 L07 复飞正式收口，此处交叉登记）。

## 三、接线四态独立复核

| 面 | 四态 | 复核证据 |
|---|---|---|
| 五方法注册 | built | VALM 5 method_id 本日计数 |
| DAL 与代码绑定 | 30/32 有码 | DAL-BUDGET-BAND/DAL-GRADIENT-TRIM design code_ref=null |
| 台账写入链 | built（手动批） | runner :57 表锚+60 行实弹 |
| 调度挂载 | 未接线 | register_*.ps1 零命中（本日复证）|

## 四、缺口清单（B 半验证欠账总口径，按生死线排序）

| # | 欠账 | 处置 | 优先 |
|---|---|---|---|
| 1 | BT-P0-003 成本三件套：L4-09 过/X-S2-01 过/P2-01+P2-03 存疑（做T 24<30 样本，净价差 mean −45.0bp 披露在案） | Flash F02 重考扩样本 | P0 |
| 2 | X 流 18 节点全 pending | exit_counterfactual 真结论待窗口前移重跑 | P1 |
| 3 | 消融器实弹待 Owner 放行（§12） | 放行后 run_ablation→batch="XFLOW" | P1 |
| 4 | 消融动作标注自动化（SellSignal 流未接回测） | 与欠账 3 同根同修 | P1 |
| 5 | P/F 流验证零启动（agg_discrimination/portfolio_attribution 无一行实弹） | 随 C3-04 工单链立项 | P1 |
| 6 | BTB 132/142 plan:null | 批次决策点填写并冻结前禁跑（SOP-B 护栏③）| P1 |
| 7 | decay_watch 调度挂载 Owner 二选一 | 晨报裁定 | P2 |

## 五、自审闸三态
**挖干可施工**（机制三件全建成+台账实弹；真结论产出受 holdout 纪律约束属"正确等待"非欠账；欠账七条各有归属）。

## 六、复跑命令
```bash
grep -c "dal_id:" docs/01_policies_and_standards/_registry/catalogs/decision_algo_registry.yaml          # 32
grep -c "method_id:" docs/01_policies_and_standards/_registry/catalogs/validation_method_registry.yaml   # 5
grep -c "object_id:" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml             # 142
grep -c "plan: null" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml             # 132
grep -n "_VERDICT_TABLE" src/zephyr/trading/validation/runner.py
grep -rn "decay_watch" scripts/register_*.ps1 2>/dev/null   # 零命中=调度未挂
```
