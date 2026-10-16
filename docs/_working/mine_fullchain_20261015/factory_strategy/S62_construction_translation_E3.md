---
ttl: task_bound
---
# S62 FAC-E3 构造代码（骨架行 62）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E3）。所有数字为 2026-10-15 实读。

## 1. 定义

构造与翻译（FAC-E3，stage，partial）：外来策略翻成标准件、新想法变成可执行代码。C3 翻译（原文→权重函数+D1-D5 差异声明+因子拆解），模板已定型、35 条人工翻译=验收集；QuantCode-Bench 实证最强模型单轮通过率仅 70-76%（pass@5 仅 43%），必须带验收集+编译重试环+人工抽检。80 节点=1 stage+79 mechanism（78 built、1 pending）。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | `data/strategy_intake/normalized/`（E2 过审假说+翻译原文，实存）；E2→E3 排产流转=factory_intake_pipeline construct 子命令（过审公式候选自动生成考卷件+constructed_manifest，图 E3 algo_note_extra） |
| 输出面 | 翻译件 `scripts/backtest/translated/`（key=strategy_id，retention 永久，图 store_refs）；考卷件（供 E4）；DSL 表达式（MOD-BT-159，已通 c4_fact_e831084c 实跑验证=图注） |
| SSOT 真源 | `config/strategy_production_map.yaml` E3 组 80 节点（MOD-BT-041..075 翻译件族 35 条+MOD-BT-088/096/102-105/130/156-186 桥件族）；battle_map 互挂 BM-MT-01-B/BM-MT-03/BM-RES-01 |
| 代码模块 | `src/zephyr/factor`（95 py）、`src/zephyr/strategy_pipeline`（14 py）、`src/zephyr/backtest`（66 py）实存；MOD-BT-190 hypothesis_translator（假说轨 C3 MVP：公式化子集+阴性如实入档+表达式去重+纠错重试）；MOD-BT-159 factor_strategy_template；MOD-BT-193 graph_enrich_staging（新闻→LLM 抽供应链关系→暂存台账，绝不写 ig_fact 正图）；`dir:_domain_ml_serve/codegen_model_adapter`（E3-M-077 pending，模块卡目录） |
| 门禁约束 | 翻译件必走验收集+编译重试环+人工抽检（图注三件套）；两段式机制门已入 C2 挖矿（MOD-BT-158 build_mechanism_prompt）；构造代码本体另受图14 施工 17 段治理（见缺口 3） |
| 自动化触发 | construct 子命令事件链（E2 过审→自动排产生成考卷件）；四车道 E2 预审常态化=run 已扩全台账消费（图注） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | pass | normalized 台账+construct 编排双实证 |
| 输出面 | pass | translated/ 落位+考卷件流向 E4 明确 |
| SSOT 真源 | pass | 件族在册、实跑验证引证在案（c4_fact_e831084c） |
| 代码模块 | pass | 三包 175 py 实存，桥件族全 built |
| 门禁约束 | warn | 翻译质量三件套为图注纪律，未见机械门守 translated/ 产出质量；与图14 施工流零结构衔接（见缺口 3） |
| 自动化触发 | pass | construct 事件链+run 全台账消费实读 |

小计：5 pass / 1 warn / 0 fail。

## 4. 缺口与建议

1. 边分布：E3 仅 2 条边（E2→E3、E3→E4）；79 个 mechanism 零边——本层是零边 mechanism 最多的两层之一（与 E4 相当）。
2. pending：codegen_model_adapter（效率位，MOD-BT-195 Kronos 同批登记跳过——网络通道恢复后激活）。
3. 跨图断缝（结构性）：`config/construction_workflow_map.yaml`（图14，28 节点/33 边）全文对 FACTORY/strategy_production/E3/E4 关键词 **0 次命中**，FACTORY 图亦无反向引用——构造代码的"施工会话治理面"（D14-09 施工编码/DEPGRAPH/提交网关）与"生产图环节"（E3）无机械衔接，仅靠宪法通用规则间接覆盖。建议在 E3 节点补 handoff 注记或在图14 D14-09 补 FAC-E3 交接面。
4. Kronos 接入（MOD-BT-195）激活与车道 E 深化依赖外网通道恢复，建议登记环境依赖 issue。
