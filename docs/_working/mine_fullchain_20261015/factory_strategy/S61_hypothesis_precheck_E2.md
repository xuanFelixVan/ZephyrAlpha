---
ttl: task_bound
---
# S61 FAC-E2 假说预审（骨架行 61）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E2）。所有数字为 2026-10-15 实读。

## 1. 定义

假说预审逻辑门（FAC-E2，stage，partial）：防噪音总闸——经济学上讲不通的想法死在此，不花一分回测算力。方法论底座=FaVOR 回测前机制验证+Harvey-Liu-Zhu t≥3.0 FDR 底线+López de Prado 80% 伪迹论。8 节点=1 stage+7 mechanism（6 built、1 pending、stage partial）。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | E1 各车道候选（经 `scripts/backtest/factory_intake_pipeline.py` run 子命令自动接续——E1D 进货→E1B 可选→E2 幂等预审，图 E1 algo_note 已建声明+行 431-438 子命令实读）；车道 G 假说 `data/strategy_intake/lane_g_candidates.csv` |
| 输出面 | `c1_backtest.hypothesis_precheck`（key=candidate_id，retention 永久，图 store_refs；消费面见 `src/zephyr/pf_alloc/allocation_inputs.py` 等 strategy_screen/hypothesis 族读点）；过审件流向 E3 排产（construct 子命令） |
| SSOT 真源 | `config/strategy_production_map.yaml` E2 组 8 节点；battle_map 互挂 BM-RES-03/BM-RES-03-A（裁定#483/#487）；purpose_tag=策略不讲通不花钱（Owner 2026-10-03 终审冻结） |
| 代码模块 | MOD-BT-091（预审本体，挂 FAC-E2 与 FAC-E2-M-001）；MOD-BT-187（E2-M-002）；MOD-SIG-137/141（E2-M-004/005）；`dir:_domain_ml_serve/deep_review_model_adapter`（E2-M-003 pending，模块卡目录）；MOD-LLM_SECURITY（E2-M-007，LLM 调用必经 LSG 的宪法铁律在图内落点） |
| 门禁约束 | 进货不打分/判定权专属（E1G 红线在本层兑现）；预审判定记录永久留档可倒查；三道 LLM 门（MOD-LLM_SECURITY 挂层） |
| 自动化触发 | 工厂管线事件链：进货事件自动触发幂等预审（factory_intake_pipeline run 编排，非定时器） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | pass | 与 E1 编排自动衔接，入口件实存 |
| 输出面 | pass | 判定记录表+永久 retention 明确 |
| SSOT 真源 | pass | 图层位+BM 互挂+purpose 冻结一致 |
| 代码模块 | warn | 深审复核力 pending（E2-M-003 dir: 卡在册未建）；"本地 8B-32B 可扛"为图注设计口径，复核档未落地 |
| 门禁约束 | pass | 判定权专属+LSG 挂层+留档三件齐 |
| 自动化触发 | pass | 事件链编排实证（run 子命令接续语义） |

小计：5 pass / 1 warn / 0 fail。

## 4. 缺口与建议

1. 边分布：E2 仅 2 条主干边（E1→E2、E2→E3）+1 条回流边（E9→E2，edges 第 10 条=feedback_loops 第 1 条同款）；7 个 mechanism 零边。
2. pending 件：deep_review_model_adapter（质量位）——建议随 LLM 供给（MOD-INF-045 已 built）排期补建，预审复核力双档（图注"本地 32B 初翻+API 复核"是 E3 口径，E2 复核同理可复用双池）。
3. E2 判死件去向：负结果台账 negative_archive 是五类产品之一，但 E2 store_refs 只有判定记录表，判死件入 negative_archive 的落位未在本层声明（归档面弱声明，建议补 store_refs 行）。
