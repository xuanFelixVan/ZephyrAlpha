---
ttl: task_bound
---
# S65 FAC-E6 入库监控（骨架行 65）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E6）。所有数字为 2026-10-15 实读。

## 1. 定义

入库监控（FAC-E6，stage，built）：台账只增+判死行追加；oos_years_decay≥0.5 判存疑；decay_cause 枚举（crowding/regime/overfitting/tech/depletion）；业界规则参照=月度 IC 连续 3 月降超 20% 挂起、IR 阈值随 regime 动态调整；结论反馈回灌 E2 假说库+E1 进货方向。15 节点=1 stage+14 mechanism，全部 built。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | `c1_backtest.strategy_screen`（图 E6 data_refs）；E5 去重标注（redundant_of）；图15-S2 candidate 态宿主册衔接（strategy_card_lifecycle_map.yaml 行 13-23：registry_host=experiment_registry） |
| 输出面 | 判定书/衰减巡检 `data/backtest_artifacts/runs/`（key=run_id，retention 永久，实存）；在库三册（实读计数）：`docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml`（factors=175）、`strategy_registry.yaml`（strategies=161、lifecycle_status_values=9）、`portfolio_model_registry.yaml`（portfolio_models=11）——骨架注 "catalogs/..." 简写路径，真身在此 |
| SSOT 真源 | `config/strategy_production_map.yaml` E6 组 15 节点；宿主册=`docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`（CARD-* 契约条目，图15 行 17/21）；battle_map 互挂 BM-BT-05-D/BM-MT-05/BM-SEL-02-G |
| 代码模块 | MOD-BT-078（生命周期台账本体）；`scripts/backtest/strategy_lifecycle_advisor.py` 实存；MOD-BT-018/188/189/192/212/213/214（M-002..M-008）；`src/zephyr/experiment_tracking`（13 py 实存）；`dir:_domain_ml_serve/model_drift_monitor`、`dir:_domain_signal_quality/signal_degradation_monitor` 等 5 个监控卡 |
| 门禁约束 | 台账只增+判死行追加（不可变量）；判绿判红权在 E4、图15 D15-S5..S8（handoffs 声明，行 53） |
| 自动化触发 | 衰减巡检（月度 IC 挂起规则为"业界规则参照"口径）；E6→E1 反馈环=feedback_loops 第 2 条声明 |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | pass | strategy_screen 读点+候选卡宿主衔接明确 |
| 输出面 | pass | 三册实数（175/161/11）+巡检报告落位实证 |
| SSOT 真源 | pass | 双宿主（图+experiment_registry）登记一致，路径已核真身 |
| 代码模块 | pass | advisor+漂移/衰减监控卡族全实存 |
| 门禁约束 | pass | 只增不变量+判定权归属清晰 |
| 自动化触发 | warn | 月度巡检/衰减扫描未见 scheduler 槽位或事件源实证（src/zephyr/data/scheduler.py 中无 E6 相关槽，grep pf_alloc/lane_g 之外零命中）；E6→E1 反馈环在 feedback_loops 声明但 edges 17 条中**无此边**——已声明未落边 |

小计：5 pass / 1 warn / 0 fail。

## 4. 缺口与建议

1. 边分布：E6 仅 2 条主干边（E5→E6、E6→E7）；14 个 mechanism 零边。
2. 反馈环落边：feedback_loops（E6→E1"衰减/失效结论反馈进货方向"）未进 edges 块——与 E9→E2（两条都在）不同，这条只在 loops 声明。建议生成器补落边或校验器加"声明环必须在 edges 存在"检查。
3. 巡检触发挂载：建议比照 E8 pf_alloc_rebalance_check 先例（scheduler 槽+disabled 总闸）给月度衰减巡检一个显式槽位或事件源，消除"参照规则无人定时执行"的隐性空转。
