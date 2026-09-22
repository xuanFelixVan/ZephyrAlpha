---
ttl: task_bound
session: st-xhs-full-20260922
topic: xhs_full_construction_20260922
---

# Alpha158/360"表达式→handler"工程范式借鉴一页（工单 #5，判定 D）

> Owner 工单 #5：判定 D=轻施工，产"表达式→handler 范式"借鉴文档一页入档。因子本体不采，借范式。源=cutting 立档 collection_intake/factors/factor_spec_alpha101_191_158.md §3（Qlib `qlib/contrib/data/handler.py`）。

## Qlib 范式四点拆解

1. **表达式模板批量生成**：Alpha158 用公式模板（KMID/STD/ROC/MA 族 × 多窗口）+ 表达式引擎批量实例化 158 个特征字段——因子=字符串表达式，不是手写逐列代码。
2. **统一 handler 计算面**：`Alpha158` handler 声明式配置（instruments/list/factor 表达式/label/processor 链），数据层只认表达式清单，统一计算+缓存。
3. **T+1 可交易 label 口径**：`Ref($close,-2)/Ref($close,-1)-1`——跳过次日开盘不可成交的约束，label 天然 PIT 干净（这是 A 股 T+1 的正确对齐，剪报点名的可取之处）。
4. **processor 声明式链**：标准化/中性化/去极值作为 handler 配置的处理器链，特征与预处理分离、可复算可审计。

## 映射到本项目（已有等价面，禁止重复造轮）

| Qlib 范式 | 本项目对应 | 状态 |
|-----------|-----------|------|
| 表达式模板批量 | E1C 双轨（gplearn `lane_c_formula_miner.py`+智能体 `lane_c2_agentic_miner.py`），算子白名单=`config/factor_mining_whitelist.yaml` | 已有 |
| 统一 handler 计算面 | factor_base_abstraction + alpha_signal_pipeline（表达式→面板计算→E4 出证统一管线） | 已有 |
| T+1 可交易 label | 回测土规成本 T+1 冻结+前向 5 日收益 y 的 PIT 纪律（f06/E4 管线） | 已有 |
| processor 声明链 | 残差化/横截面中性化=residualize 等 E1C 纯函数（增量 IC 基座=REG-IND-001） | 已有 |

## 结论

- **范式结论**：四点全部已有等价实现，Alpha158 的增量启示只有两条：①表达式模板批量生成可作为 E1C 种群初始化的先验结构（模板族 × 窗口网格，供 #4 Alpha101 入库路线复用同一管线）；②label 的 `Ref($close,-2)` 跳一日口径值得在本项目新增 label 时作为默认检查项。
- **判定维持 D**：零代码施工；因子本体不采；本文档即工单 #5 的全部交付物。
