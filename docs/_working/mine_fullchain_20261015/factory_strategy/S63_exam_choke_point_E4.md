---
ttl: task_bound
---
# S63 FAC-E4 考试咽喉（骨架行 63）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E4）。所有数字为 2026-10-15 实读。

## 1. 定义

考试咽喉（FAC-E4，stage，built）：全厂唯一判定权（三铁律之一"运动员不兼任裁判"）。IS 2020-2023 冻结窗口+冻结土规成本（2.5bp 佣金+10bp 印花+5bp 滑点）→DSR 批内折减→OOS 新考卷（2024-2026 已跑）→双窗口及格线。护栏栈：WFO/purged CV+embargo/CPCV（测试在库）/Optuna-on-purged/PBO+DSR 签核；分布预测件加双标准（PIT 校准+锐度）。82 节点=1 stage+81 mechanism（80 built、1 pending）——全图最大层。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | 考卷三表 data_refs：`c1_market.kline_daily_hfq`、`c1_market.stk_limit`、`c1_market.kline_index`（图 E4）；E3 考卷件（translated/）；数据侧挂 `dir:_domain_data/auto_backfiller`、`multi_timeframe_fusion` 等 E4 数据保障机制 12 件（M-028..M-058） |
| 输出面 | `c1_backtest.strategy_screen`+`data/backtest_artifacts/runs/`（key=strategy_id+screen_batch，retention 永久，图 store_refs；runs/ 实存）；判定书流向图15 D15-S6 判绿/S7 判红/S8 不可判 |
| SSOT 真源 | `config/exam_scale_cost_gate.yaml`（150 行实读：v1 冻结四块 cost_gate/scale_gate/turnover_gate/search_objective+裁定#435 B案 breakeven_cost_gate v2.0.0 五道门+cost_gate_active 指针块 active_version='2.0.0' wired 2026-09-30+裁定#506 net_fee 块 landed 2026-10-15）；`config/strategy_production_map.yaml` E4 组 82 节点 |
| 代码模块 | `scripts/backtest/f06_e4_wfa_exam.py`（724 行）；`scripts/backtest/t1_t2_handover.py`（load_cost_gate_params 行 123-141：active_version='2.0.0' 且 breakeven 块在场→v2 五道门，缺→回退 v1 冻结键行为零变化；发车闸 launch_gate_scope=P1/P2）；`src/zephyr/backtest/core/closed_book_gate.py`；`scripts/backtest/`{`sector_prereg_exam_runner`,`reexam_cpcv_harness`,`exam_cost_reexam`,`dsr_recalc_backfill`,`replay_drill`}.py 全实存；af: 别名机制 16 件（vectorized_engine/e2_stationary_bootstrap 等，M-064..M-082） |
| 门禁约束 | cost_gate v1：五档滑点 [0,5,10,20,40]bp、survival_floor=0.0、单调容差 1e-09、min_days=60 fail-closed；breakeven v2：G-COST-BREAKEVEN-40BP 五道门（p1 中位数≥40bp/p2 p10≥0/p3 层占比≥0.80 层内 n≥30/p4 规模敏感≤0.20/p5 数据版本五字段）+三态 PASS/INDETERM/FAIL（INDETERM 禁默认降级）+dsr_gate（dsr_min=0.95、n_trials=3700 禁填抽样 50、pbo_max=0.20）；net_fee=25.0bp 常数解（judge_face=metrics_only，存量卡不追溯=裁定#506） |
| 自动化触发 | 考试由工厂管线/重考事件触发（E0 问闸 heavy 档前置）；FAC-E4-M-023 批末记账红证 pending；A 股四条年化强制（禁 sqrt252/Ljung-Box q=252/ddof=0/停牌双剔）钉死口径 |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | pass | 考卷三表+数据保障机制族在册 |
| 输出面 | pass | strategy_screen+runs/ 双落位实证 |
| SSOT 真源 | pass | 参数册六块全实读、版本指针机制（v1/v2 回退）有测试钉死（册注"tests 钉死"，`tests/backtest/test_net_fee_param_face.py` 实存对拍两面值） |
| 代码模块 | pass | 724 行主考件+五辅件+closed_book+16 af 件全实存 |
| 门禁约束 | warn | net_fee 最低佣金两键"登记面非计算面"（册 140-142 行自注：_round_trip_cost_bp 无名义额形参，接线须动 calibration_exam.py，在途袋防撞）；成本口径差异（引擎 turnover 缩放 vs 消费腿固定扣费）登记未修；scale_gate participation_rate 缺省 None=规模维禁用（裁定：成本档不带规模参数=验收门恒过，接线形参=格点成交额/ADV 未接） |
| 自动化触发 | warn | M-023 试验台账批末记账红证（MOD-BT-228）pending——病历页记账腿未闭 |

小计：4 pass / 2 warn / 0 fail。

## 4. 缺口与建议

1. 边分布：E4 仅 2 条边（E3→E4、E4→E5）；81 个 mechanism 零边。
2. 跨图断缝：E4 判绿判红权与图15 D15-S5..S8 执行态靠 `handoffs.product_state_map_ref` 文字声明衔接（strategy_production_map.yaml 行 52-53），无边、无机械对账件——骨架 §3.13 已立案（毕业包→挂图→生产闭环对账缺失），本席实证补强。
3. 三项在册未接线：net_fee 最低佣金代码腿、scale_gate 参与率形参、成本口径统一——均有在途袋防撞约束，建议按册内指引（docs/_working/automation_campaign/feedback/to_impl.md 2026-10-15 ⑤席 02 班条）排期。
4. 开放决策点 7：是否拆 E4a 免回测快筛（省时 25%+）+E4b 全量——留 Owner 裁定。
