---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# 外部因子集入库路线：Alpha101 / GTJA191 / Alpha158 2026-09-20

> 来源：小红书帖（"10年过去了，101 个 α 还有多少能用"，配论文标题页图）+"猜你想搜"线索。三套都是公开成熟因子集，判定 **B（入库路线就绪）**，核心纪律见 §3。

## 1. 《101 Formulaic Alphas》（Zura Kakushadze, 2015-12）`[外部]`

- 全文免费：**arXiv:1601.00991**（https://arxiv.org/abs/1601.00991 ，22 页）；SSRN 有正式页但编号未直连核实，引用以 arXiv 为准。
- 开源复现：`yli188/WorldQuant_alpha101_code`（870★）与 `popbo/alphas`（587★，**含 101+191+backtrader**，2023-04 更新）。
- 论文要点：101 条公式化 alpha；截稿时 80 条在实盘；"超级 alpha"=海量因子整合+交易内部净额撮合省执行成本（执行层存档思想）。
- 帖内社区实测校准：3 试 1 勉强能用、"很多过时"、"单因子没用组合里有用"——**入库预期管理：按组合原料对待，不按圣杯对待**。
- 与 191 有重叠，重叠部分社区评价"还有点用"。

## 2. GTJA191《基于短周期价量特征的多因子选股体系》`[外部]`

- 出处证实：**国泰君安金工（刘富兵、李辰），数量化专题之九十三，2017-06-15**，191 个短周期价量因子（A 股价量事实标准之一）。
- 原文 PDF 无官方公开渠道（第三方扫描件）；开源复现充分：`wpwpwpwpwpwpwpwpwp/Alpha-101-GTJA-191`（148★）、popbo/alphas、DolphinDB 教程、Qlib 插件打包（JustinF8/qlib-factor-zoo）。

## 3. Alpha158/Alpha360（微软 Qlib）`[外部]`

- 因子定义：`qlib/contrib/data/handler.py`（`from qlib.contrib.data.handler import Alpha158`）；官方文档 https://qlib.readthedocs.io/en/latest/component/data.html 。
- A 股 T+1 设计的 label 口径（`Ref($close,-2)/Ref($close,-1)-1`）值得本项目回测对齐参考。
- 判定 D：**借"表达式→handler"工程范式多于借因子本身**。

## 内部挖矿 `[亲验]`

- 项目**无表达式横截面因子库**；E1C 双轨（gplearn `lane_c_formula_miner.py` + 智能体 `lane_c2_agentic_miner.py`）的算子白名单=`config/factor_mining_whitelist.yaml`（active）——这是三套因子集的落地层。
- AlphaGen（RL 挖公式）在 production map 中仅为 design_ref，未实现。

## 入库路线（纪律先行）

1. **层级判定**：Alpha101/191 是横截面表达式因子（rank/ts_ 算子族），落 **E1C 表达式层 + factor_mining_whitelist 扩算子**，**不进 tilib 时序指标库**（两层语义不同）。
2. **批量翻译**：从 popbo/alphas 取实现，逐条转为本项目 DSL；`trade_when` 类条件调仓算子一并入白名单候选。
3. **E4 本地重考是铁律**（判读 #15）：任何外部因子集不分出身，逐条过 DSR/PBO/WFO；预期放行率参照社区实测（低放行是正常态，批 9→E4 存活 17/81 先例）。
4. **同质化去重**：入库前过 clone_guard/因子相关性检查（101 与 191 重叠、与现有 138 指标重叠先查重）。
5. **批次建议**：不一次性吞 292 条；先挑 20~30 条与现有族低相关的（量价高频类、rank 类）试一批，验证管线后再扩。
