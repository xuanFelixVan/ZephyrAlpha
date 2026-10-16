---
ttl: task_bound
---
# S64 FAC-E5 协同去重（骨架行 64）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E5）。所有数字为 2026-10-15 实读。

## 1. 定义

协同去重（FAC-E5，stage，built）：单因子好看没用——加进池子能涨分才准入（purpose_tag=策略加池子才准入）。正交化四法对照后选对称正交化（保可解释性最佳且不依赖收益数据）；对动量/波动/流动性基准因子正交化后增量 IC 显著才准入；组合权重走 IC_IR 加权禁朴素等权。5 节点=1 stage+4 mechanism，全部 built——全图最小层。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | E4 考试幸存者（E4→E5 主干边）；本层 data_refs=**空**（图 E5，无独立数据源声明） |
| 输出面 | 去重标注：redundant_of 只标注不删行（`config/synergy_dedup.yaml` 行 13 变更纪律）；E4→E6 归档段 E5 挂点（册行 10） |
| SSOT 真源 | `config/synergy_dedup.yaml`（22 行实读：corr_threshold=0.70，F24 接线 st-ffchief-20261001，净零声明=替代 MOD-BT-086 硬编码默认档 0.70 的"判据值"身份）；`config/strategy_production_map.yaml` E5 组 5 节点 |
| 代码模块 | MOD-BT-086 相关性聚类+簇首选择（贪心 O(n²) 单遍；测试=`tests/research/research/backtest/test_synergy_dedup.py`——注意实际路径为 research 双重嵌套，非图注 tests/backtest/）；MOD-BT-024（E5-M-002）；`dir:_domain_signal_quality/signal_dedup`（E5-M-003 模块卡） |
| 门禁约束 | 缺册/非法 fail-closed 拒考（册行 8-9，裁定#325 假绿防线同款，禁静默回落代码默认档）；改值须历史回放比对+Owner 定案（册行 13-14） |
| 自动化触发 | 声明触发点=f06_e4_wfa_exam.py 的 E4→E6 归档段 E5 挂点（册自报消费方）——见三态 fail |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | warn | 输入全靠上游边，本层零 data_refs 声明；输入数据契约（聚类用的收益/IC 矩阵来源）未落字 |
| 输出面 | pass | redundant_of 标注语义+只增不删纪律明确 |
| SSOT 真源 | **fail** | 册自称"生产链一律经 load_synergy_threshold 读本册"，但全仓 grep（排除 worktree/aidrafts 归档镜像）**load_synergy_threshold 零命中**；`scripts/backtest/f06_e4_wfa_exam.py`（724 行）内 "synergy" 关键词 **0 次**——判据值唯一真源册建成（2026-10-01）至今无生产消费腿，fail-closed 缺册拒考防线实际不存在（册在、读数腿断） |
| 代码模块 | warn | MOD-BT-086 本体+测试在库，但测试实际路径 `tests/research/research/backtest/test_synergy_dedup.py` 与图注 `tests/backtest/test_synergy_dedup.py` 漂移（research 双管线目录嵌套异常，骨架 §3.9 关联）；对称正交化选型/IC_IR 加权未见独立机制件（挂 E8 MOD-PA 族） |
| 门禁约束 | pass | 册内变更纪律+净零声明合规（宪法 §4.1 替代声明在册） |
| 自动化触发 | warn | 触发点声明在 f06_e4_wfa_exam 归档段，但读数腿未接=触发链同名存实亡（与 SSOT fail 同根） |

小计：2 pass / 3 warn / 1 fail。

## 4. 缺口与建议

1. **最高优先修复（本段唯一 fail）**：把 `load_synergy_threshold`（缺册 fail-closed）接进 f06_e4_wfa_exam.py E5 挂点，或修正册头消费方声明；接线前 E5 实际运行在"代码默认档 0.70 兜底"状态，与"禁静默回落"的册纪律矛盾。改 f06_e4_wfa_exam.py 须先查在途袋（防撞惯例）。
2. 边分布：E5 仅 2 条边（E4→E5、E5→E6）；4 个 mechanism 零边。
3. 测试路径归位：test_synergy_dedup.py 从 tests/research/research/backtest/ 嵌套异常路径移正（涉文件移动须走 RENAME-DEPGRAPH-SYNC 门禁流程，本席只登记）。
4. 正交化增量 IC 验收（"对基准因子正交化后增量 IC 显著才准入"）未见独立机制件，与 E8 IC_IR 加权同属"图注有、件族未单列"，建议在 E8/M-006 MOD-PA-014 三维筛选挂接处显式互引。
