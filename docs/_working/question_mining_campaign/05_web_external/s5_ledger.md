---
ttl: task_bound
title: S5 全网外部挖矿台账 · st-pqmine-20260927
session: st-pqmine-20260927 (S5 路)
date: '2026-09-27'
产出: s5_candidates.yaml（S5-001~S5-028，28 题草稿，拟议 PQ-0284+）
---

# S5 全网外部挖矿台账

## 一、搜索账（9 轮 WebSearch，超出 6 轮底线）

| 轮 | 查询 | 收成 | 备注 |
|----|------|------|------|
| R1 | quantitative trading data quality checks best practices completeness timeliness outlier detection | 有结果 | 服务部分 429 限频；收 outlier/bounds、completeness、reconciliation、staleness 四范式与 6 个可回查 URL |
| R2 | factor validation checklist quantitative research IC stability factor decay crowding | 限频，无直接 URL | 前后端 429；获得范式描述（ICIR/衰减/拥挤），出处降级为行业共识+ canonical 文献标注（S5-006/008 已在 origin 内显式声明限频） |
| R3 | backtest overfitting deflated sharpe ratio probability of backtest overfitting CSCV Lopez de Prado | 有结果 | DSR（JPM 40(5)）、PBO/CSCV、Paulsen arXiv；SSRN 2460551 / 2326253 为可回查 canonical ID |
| R4 | transaction cost analysis market impact model implementation shortfall square root law best execution | 有结果 | square-root law（impact≈σ√(Q/V)，Loeb 1983）、Hasbrouck IS 分解、TCA best execution；URL：prachub/studylib/arithmion/pages.stern.nyu.edu |
| R5 | point in time data survivorship bias backtest universe construction delisted stocks | 有结果 | algoseek vendor 必答清单、ghost alpha（缺退市收益）、PIT 宇宙构建、delisting return -100% |
| R6 | SR 11-7 model risk management validation model inventory independent validation ongoing monitoring | 限频，无直接 URL | 429 多轮；SR 11-7 内容按官方文件落出处 federalreserve.gov/supervisionreg/srletters/sr1107.htm（稳定 URL） |
| R7 | China A-share backtest limit up limit down suspension T+1 tradability constraints | 大多限频/跑题 | 范式=涨跌停不可成交/T+1/停牌估值；出处取搜索建议的 Qlib（github.com/microsoft/qlib）框架共识并显式声明限频 |
| R8 | walk-forward validation purged k-fold cross validation leakage combinatorial purged CV | 有结果 | purge+embargo、CPCV（skfolio.org）、arXiv 2026 purged rolling WFA |
| R9 | factor crowding measure pairwise correlation valuation spread MSCI methodology | 部分 | MSCI Factor Crowding Model（Bhaskarla/Lang 2017）确认存在，msci.com 站内可查；精确 PDF 未命中（限频），已如实标注 |

**限频诚实声明**：R2/R6/R7 三轮主体 429，题面范式仍成立但出处密度低；对应题（S5-006/007/008/011/016/017/018）origin 字段均显式标注"限频+canonical 文献"，intake 质量闸可按此降置信。

## 二、行业范式发现（→ 题面映射）

1. **数据质量六维**（completeness/uniqueness/timeliness/validity/consistency/accuracy）→ S5-001（validity：OHLC 边界）、S5-003（consistency：双源对账）、S5-004（completeness：日历双向）、S5-005（timeliness：哨兵覆盖）、S5-027（uniqueness：主键）。
2. **因子验证 triplet**（IC 均值 / ICIR / IC t 值）+ 衰减曲线 + 拥挤五维（MSCI）→ S5-006/007/008（登记资产过程闸，非单因子预测力题，避开退役雷区）。
3. **回测过拟合家族**（DSR/PBO/CSCV/多重检验加息）→ S5-009/010/011。
4. **TCA 家族**（square-root law、参与率上限、IS=delay+execution 分解）→ S5-019/020/021。
5. **PIT/幸存者偏差**（退市股纳含、退市收益显式处置、修订版本保留、基准口径）→ S5-013/014/015/026。
6. **SR 11-7 模型风险管理**（inventory 六要素、developer≠validator、ongoing monitoring+benchmarking）→ S5-022/023/024。
7. **A 股制度约束**（涨跌停不可成交、T+1、停牌、参与率）→ S5-016/017/018。
8. **切分卫生**（purge+embargo）与**可复现性**（双跑哈希一致）与**统计显著性登记**（SE(SR)/MinTRL）→ S5-025/012/028。

## 三、去重账

- **对照既有 283 题**：逐题 dedup_check.nearest 给出最近邻 PQ 编号与语义区分理由。既有 283 题主力=源线谱 U1-U6 逐线审计 + 闭卷窗具体因子 IC/事件研究 + meta_question 治理自反；本题集全部为**过程闸/机制完备性/制度约束题**，无一题重跑既有因子预测力实测。最近邻聚类：S5-005↔U3 线（监控面 vs 口径面）、S5-009↔PQ-0104（晋级 DSR vs E1C 预注册）、S5-015↔PQ-0022/0155（存储语义 vs 取数口径）、S5-016~019↔PQ-0094/0049/0020（交易制度面 vs 仓位面）。
- **对照退役 30 题**：唯一显式对照点=S5-025↔退役 PQ-0024（PIT 口径 IC 差，no_alpha）。S5-025 审切分机制的 purge/embargo 执行（代码/索引断言），不复算任何因子预测力结论，非翻案，已在题内声明。其余 27 题与退役簇（均线斜率族/尾盘主买族/业绩超预期族/传导族/加密族等）零交集。
- **跨路交叉**：S5-006/007/008 与 S2 因子路（factor_registry 175 因子）存在登记面交叉，已在文件头与题内标注，待 90_consolidated 汇总时合并裁定，本路不预占。

## 四、自审三态

| 方向 | 三态 | 依据 |
|------|------|------|
| 数据质量范式（R1/R5） | **挖干**（相对本轮搜索深度） | 六维每维至少 1 题；限频下可回查 URL 已用尽，继续搜同类关键词边际收益趋零 |
| 因子验证范式（R2/R9） | **未干**（受限频） | R2/R9 主体 429，拥挤五维/估值差维度只出 1 题（S5-007）；MSCI 精确论文 URL、WorldQuant alpha 101 检验范式未深挖，限频解除后可补 |
| 回测过拟合家族（R3/R8） | **挖干** | DSR/PBO/CSCV/purge/MinTRL 全链出题，canonical SSRN ID 可回查 |
| TCA（R4） | **未干**（可续挖） | 已出参与率/模型形式/IS 分解 3 题；Almgren-Chriss 最优执行、VWAP/TWAP 基准偏离、滑点实测校准（闭卷窗后）未出，属切点后样本依赖题，本轮刻意未收 |
| SR 11-7（R6） | **未干**（受限频） | 已出 inventory/独立性/监控 3 题；conceptual soundness 挑战记录、文档标准、三道防线未出题，官方 PDF 细读后可补 |
| A 股制度约束（R7） | **未干**（受限频） | 已出涨跌停/T+1/停牌 3 题；ST 摘帽、新股上市初期限、大宗交易/融券约束未出，R7 直接命中 URL 为零 |

**总评**：28 题草稿落盘，五要素齐+出处可回查+去重留痕。三态合计=挖干 3 路/未干 3 路（未干主因=搜索服务 429 限频，非矿脉枯竭；限频解除后 S5 可二次进场补 6-10 题）。

## 五、纪律自检

- 产出只写文件：本目录 s5_candidates.yaml + s5_ledger.md，未触 meta_question 正门（intake 由汇总批执行）。
- 未执行任何写库/施工操作；闭卷纪律未破（全部题面为过程/机制断言，不重跑退役因子结论）。
- 频率枚举/层级枚举按 meta_question_layers_vocabulary.yaml（L0-L6）与宪章格式对齐。
