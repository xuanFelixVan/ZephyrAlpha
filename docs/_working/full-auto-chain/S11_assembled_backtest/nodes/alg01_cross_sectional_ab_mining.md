---
ttl: task_bound
title: T1-α 节点挖矿：ALG-01 横截面结构特征 A/B（MOD-REGIME-007 + builder 开关）
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 挖矿节点 7：ALG-01 横截面结构特征 A/B（MOD-REGIME-007）

> 挖矿日期：2026-09-15 ｜ 会话：st-qoder-t1a-20260915 ｜ 唯源骨架：S11_assembled_backtest/nodes/
> 挖矿依据：feature_pipeline_mining §4 待挖子节点第 2 件——ALG-01 横截面 A/B。
> 编号溯源：ALG-01 = 2026-08 架构审查 P1 项（#ARCH-140，92 号清单波 2）→ 落地为
> cross_sectional_features.py（556 行，4 特征纯函数）+ RegimeFeatureBuilder enable_cross_sectional
> 开关（默认关）+ A/B 报告（docs/_archive/2026-08-22-alg01-cross-sectional-ab.md）。
> 证据等级：全源码逐行 + ClickHouse 只读实测（ch_reader，top800 池 2023-12~2026-06 共
> 497,600 行 + 全市场对照 734,389 行 + c1_market.adj_factor 306 万行），复权对照、共线性、
> 目标事件（2024-02 微盘踩踏）检测力全部实测。
> 产出=数据，采纳裁定归主力会话施工班。

## 0 现状盘点（逐条带 file:line 锚点）

- **4 特征**（cross_sectional_features.py:93-98 列序钉死）：C1 cross_dispersion（截面收益
  IQR/1.35，20 日平滑，L302-323）；C2 avg_pairwise_corr（60 日窗两两 Pearson 均值，
  流动性 10 层等量抽样 ~200 只、20 日再平衡、确定性种子，L367-438）；C3 vol_dispersion
  （20 日 HV 年化的截面 std，L529-537）；C4 momentum_breadth（close>MA20 占比 %，L545-556）。
- **开关**（regime_feature_builder.py:157/275-278/289-297）：默认 False 逐字节一致（测试
  test_switch_off_byte_identical 钉死）；开时尾部追加 4 列，active_feature_names() 6→10 联动。
- **面板**（builder L651-692）：kline_daily，A_share+quality_flag=1，**每日成交额 top800**
  （LIMIT 800 BY trade_date），data_load_start~backtest_end 全量惰性加载，带缓存。
- **A/B 报告**（_archive/2026-08-22）：区间 [2024-01-01, 2026-06-30] 601 交易日，
  B 臂 X=(T,10)；两臂 schedule Pearson 0.9999、|Δ|均值 0.0007、max 0.0198（L41-42）；
  结论"边际影响很小，保持默认关，仅作诊断维度观察"（L62）。
- **消费方**：全仓 grep——enable_cross_sectional 唯一 True 出现在测试
  （tests/regime/test_cross_sectional_features.py:286）；scripts/ 与 frontend 零消费。
  **生产既开不了也没有任何"诊断观察"出口。**

## 1 头号发现 ALG2-1（P1）：top800 采样池与检测目标结构性错配——模块立项要抓的事件，池构造保证它看不见

#ARCH-140 立项原文（architecture_issue_registry.yaml:17991-17994）：横截面特征是
"2024-02 微盘流动性危机：指数未崩但小盘股踩踏"的**唯一可见维度**。但面板池=每日成交额
top800（builder L672），微盘踩踏发生在流动性分布**底部**——池把目标信号截掉了。

**实证（2024-02-05，踩踏峰值日，ClickHouse 只读）**：

| 特征 | top800 池（生产口径） | 全市场 5367 只对照 |
|---|---|---|
| C4 momentum_breadth | 25.79%（窗口内 12.6 pctile） | **4.27%（5 个月内 0.0 pctile）** |
| C1 cross_dispersion | 0.02850（窗口内 50.2 pctile，中位数！） | 0.01789（69.3 pctile） |
| C3 vol_dispersion | 0.2289（19.8 pctile） | 0.19663（24.8 pctile） |

同一事件同一指标，池口径 25.8% vs 全市场 4.3%——**6 倍失真**；C1 在池口径下踩踏日
只是中位数。模块的 raison d'être 事件在其生产数据口径下不可见。连锁后果：A/B 报告
"两臂无差异"部分是**池构造的先定结果**（B 臂从未收到目标事件类信号），不能据此判
"特征无增量"。

## 2 ALG2-2（P1）：收益用不复权 close——18 个月 494 条除权假收益混入截面，表内 adj_factor 是死列

- 面板 SQL 只取 close（builder L662），pct_change(fill_method=None) 出收益
  （cross_sectional_features.py:191-192）。kline_daily.close 为原始收盘价
  （schemas/categories/kline/market_kline_daily.py:49），表内 adj_factor 列
  **8,701,773 行（2018~2026-06）全部恒 1、0 个 NULL**（CH 实测，与 akshare_provider.py:293-294
  "#198 实证全表 9,659,286 行恒 1" 记载一致）；pct_change 列与 close 逐日收益零偏离
  （411,486 对 >2pp 偏离=0）→ **表内无任何复权口径可用**。
- **实证（对照 c1_market.adj_factor 独立表，日频 7009 行/日，池覆盖 5096/5097）**：
  top800 池 2023-12~2026-06 共 **494 条 |raw−hfq|>2pp 假收益（0.120%），213 个交易日，
  5-7 月分红送转季占 78.5%**。极值：002594 2025-07-29 raw −66.94% vs hfq +0.37%；
  300857 2026-04-22 raw −14.38% vs hfq +20.00%（**符号翻转**）。
- 对 4 特征的实际污染（同窗 raw vs hfq 全量重算）：C1 corr 0.9999、mean|Δ|/σ=0.009
  （IQR 稳健口径近免疫）；C3 corr 0.9630、mean|Δ|/σ=0.159、max|Δ|=0.039（20 日 HV
  把假收益留窗 20 天，受污染最重）；C4 corr 0.9989、mean|Δ|=0.76pp、max 5.36pp。
  修复件现成：join c1_market.adj_factor 出 hfq close 即可（本挖矿已验证全流程可行）。

## 3 ALG2-3（P1）：A/B 报告三重方法学缺陷——"边际影响小"不可作为转正/退役的终局证据

1. **不可复现**：生成脚本全仓不存在（scripts/ 与 src/ 零命中"enable_cross_sectional"），
   报告只有结果没有实验代码，参数无法审计（_archive/2026-08-22-alg01-cross-sectional-ab.md 全文仅 62 行）。
2. **臂配置未披露且≠生产配置**：报告只写 walk-forward/detect_window=60（L12），
   risk/overlay/phase2c 臂未记；构造器默认 enable_full_risk=False（builder L154），
   而 print_regime_history 生产默认 full+overlay+phase2c（feature_pipeline_mining §1.1）——
   实验跑在简化管线上，即使结论成立外推性也存疑。
3. **一致性指标≠检测能力指标**：以"两臂 schedule 相关 0.9999"论证无增量，但两臂一致
   完全可以同为盲（ALG2-1 证明 B 臂对目标事件类失明）；报告未做任何事件窗口对照
   （2024-02 踩踏、2025-04 关税日两臂差异均未披露）、未做下游任务（收益/回撤）评估。
   附：schedule 分布 99% 日 ≈0.98-1.0、重节流仅 1%（L29-36），动态区间极窄，
   |Δ|max 0.0198 永远翻不动档位阈值。
4. **共线性假说已排除**（这反而加重 ALG2-1/2）：实测 10 特征相关阵
   （2024-01~2026-06，n=476）：C1↔F1 realized_vol_pct=0.587、C2↔F1=0.392、C4↔F4
   ad_ratio=0.205、C3↔F1=0.216——4 新列携带正交方差，"无差异"不能用"冗余"解释，
   只能用"实验看不见/管线漂白"解释。

## 4 ALG2-4（P2）：C2 恐慌语义未校准——"相关趋于 1"实测峰值 0.42，且 60 日窗天然滞后

- docstring 设计语义"恐慌期一切相关趋于 1，是 CRISIS 信号"（cross_sectional_features.py:29）。
  实测：池口径窗口内 max=0.4172（2024-10-22），全市场口径 2023-11~2024-03 max=0.4809
  （2024-03-28，**踩踏后 7 周**）——含两轮危机的 2.5 年里距 1 遥远，且 60 日滚动相关
  在事件后持续高位，峰值天然滞后事件约 1-2 个月，作危机"检测器" semantics 不成立，
  更接近"结构性拥挤度的滞后描述量"。阈值从未标定，A/B 也未给出 C2 的边际贡献分解。

## 5 ALG2-5（P2）：治理僵尸态 + 文档失真

- **僵尸实验态 24 天**：8-22 A/B 出"保持默认关，仅作诊断维度观察"（blueprint.md:53）后，
  无任何诊断消费方（§0 已证），无转正/退役裁定跟踪（#ARCH-140 status=decided 即闭案，
  L18006-18007）；blueprint §6"production 启用挂起等 Owner"无挂起台账。宪法 §4 退役
  纪律与 RULE-SSOT 视角：该模块当前既非活体也非退役，处于无审计锚点的悬置态。
- **文档失真**：docstring"全市场个股日收益的截面 std"（cross_sectional_features.py:25、
  L21"全市场"）vs 实际 top800 池——ALG2-1 证明该失真恰好掩盖了核心缺陷；
  "仅作诊断维度观察"（blueprint:53）无落点。
- A/B 报告躺在 _archive 且 ttl: permanent，与蓝图/registry 三处引用无一处指向裁定动作。

## 6 ALG2-6（P2）：测试缺口

- 18 用例（registry L18005；test_cross_sectional_features.py）覆盖 PIT 截断/已知答案/
  确定性/NaN 纪律/开关回归——合成随机游走面板上质量高；但**无除权/不复权面板用例**
  （ALG2-2 对合成测试不可见）、**无池构成敏感性用例**（ALG2-1：同一事件 top800 vs
  全市场面板的输出差断言）、无 C2 抽样再平衡边界（rebalance 日恰逢数据缺口）用例。

## 7 实证结果汇总表

| # | 项 | 实测 | 结论 |
|---|----|------|------|
| 1 | kline_daily.adj_factor 列 | 8,701,773 行恒 1，0 NULL | 死列（#198 在案） |
| 2 | c1_market.adj_factor 表 | 日频 7009 行/日，池覆盖 5096/5097 | 修复件现成可用 |
| 3 | 除权假收益（池内） | 494 条/18 月，5-7 月占 78.5%，含符号翻转 | P1 污染源 |
| 4 | 特征级污染 | C1≈0、C3 0.16σ、C4 0.76pp | IQR 稳健但 C3/C4 实质受损 |
| 5 | 共线性 | C1↔F1 0.587 / C4↔F4 0.205 | 非冗余，正交方差真实存在 |
| 6 | 目标事件检测力 | 2024-02-05：池 C4 25.8% vs 全市场 4.3%；池 C1 50 pctile | 池截断目标信号 |
| 7 | C2 语义 | max 0.42（池）/0.48（全市场，滞后 7 周） | "corr→1"未兑现 |
| 8 | B 臂完整性 | detect 走 active_feature_names 10 列+季度 scaler（builder L504-507） | B 臂非静默 6 列截断，实验链路真实 |

## 8 修复优先级裁定建议

| 项 | 级别 | 动作建议 |
|----|------|---------|
| ALG2-1 | P1 | 若维持立项目标（微盘踩踏可见维度），池改全市场（quality_flag=1 全量 ~5100 只，C2 抽样机制本就为 O(N²) 而设）或 top800+小盘补集；改池属口径变更，须重跑 A/B |
| ALG2-2 | P1 | 收益改 hfq：join c1_market.adj_factor（日频、覆盖齐、本挖矿已验证）；或按模块既有"缺数据剔除"纪律把复权因子跳变日标 NaN 借用现成 NaN 链 |
| ALG2-3 | P1 | A/B 重跑三前提：生成脚本入库、臂配置=生产配置（full+overlay+phase2c）并全披露、指标加"事件检测力对照"（2024-02/2025-04 窗口两臂差异），下游指标至少附 NAV 对照 |
| ALG2-4 | P2 | C2 语义重校（改阈值/改窗口/改语义声明）或降格描述量；随 ALG2-1/2 修复后一并做 |
| ALG2-5 | P2 | Owner 三选一裁定：①按上述修复后重做转正评估；②退役归档（触发率纪律）；③降格纯诊断件并接 dashboard 出口。同步勘误"全市场"→"top800 池" |
| ALG2-6 | P2 | 补除权面板用例+池敏感性用例（与 ALG2-2 修复同批） |

## 9 正面清单（验证过正确的部分）

- **PIT 纪律扎实且测试钉死**：C1-C4 全 trailing 窗口；抽样流动性排名只用 ≤t_reb 数据
  （L464-472）；测试 test_truncated_panel_equals_full_prefix 三切点逐字节断言；下游
  detect 用 features.shift(1)（builder L400-401）。
- **B 臂实验链路完整**：X 矩阵经 active_feature_names() 10 列进入训练与 detect，季度
  RobustScaler 只 fit 训练窗（L459-463）自动覆盖新列——无"静默截断回 6 列"问题（#8 项实证）。
- **默认关零行为变化**有逐字节回归测试（test_switch_off_byte_identical）；列序契约
  （尾部追加）由 CROSS_SECTIONAL_FEATURE_NAMES+测试双钉死。
- **NaN 纪律执行到位**：pct_change(fill_method=None) 不造假收益；缺数据日剔除不填补；
  截面 <30 全 NaN"宁缺毋假"；C2 pair 协有效 <30 置 NaN、常数列剔除——协方差矩阵
  数学（列内标准化/上三角 nan 均值，L488-521）经核验正确。
- **抽样确定性**：种子 (random_state, t) 为位置参数，面板尾部扩展不影响历史输出；
  流动性 10 层等量抽样保证全谱系代表性。
- 错误契约真实：空面板/缺列/非法配置抛 CrossSectionalFeatureError；纯函数无 IO，
  可离线注入面板（builder cross_sectional_panel 参数）。

## 10 封矿判定

- **本节点封批**：模块源码+开关+A/B 报告+registry 条目四层全读；复权污染、池错配、
  共线性、目标事件检测力四项全部 ClickHouse 实测定量；B 臂完整性与训练/detect 对称性
  假设逐一验证或排除（假信号已清 2 条：共线性解释、C2 mid-sample NaN）。
- **矿脉枯竭判定**：ALG-01 子链内无更多未挖项；其下游（若转正）依赖 ALG2-1/2/3 的
  修复重跑，属施工班动作非挖矿动作。
- 一句话结论：**ALG-01 是"立项证据真实、实现纪律优秀、实验结论无效"的典型——
  PIT/NaN/确定性纪律是全仓模范生，但 top800 池把它立项要抓的事件截在了门外，
  不复权收益污染了输入，而一份不可复现、配置失真、只测一致性的 A/B 报告，
  把这三个问题全部埋进了"边际影响很小"六个字里。转正与否必须重做实验后才可裁定。**
