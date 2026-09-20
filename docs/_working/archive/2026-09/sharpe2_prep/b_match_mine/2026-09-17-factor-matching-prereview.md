---
ttl: task_bound
---

# 因子库撮合预审表（E4 考纲三态判定）— Sharpe2 决赛准备战·分包 B 任务①

- 会话：st-sharpe2b-20260917 ｜ 日期：2026-09-17 ｜ 性质：沙箱研究文档（不进注册表/不写库）
- 机读版：[prereview.csv](prereview.csv)（564 行全量判定）
- **再生声明**：本件系第三度自底档机械再生（原始生成 st-sharpe2b-20260917；再生原因=他会话 worktree pre_merge stash 扫走事故两起，本件初版与第二版分别于当日 03:05-03:16 与 04:41 前后被扫离工作区，无 stash 可恢复）。数字全部由底档 `.runtime/tmp/sharpe2b/prereview_rows.json`（564 行）机械重导出，三态统计与排期经脚本复核与原版一致。
- 判定人：AI 施工子代理（三态为分析判断，非门禁结论；正式考试判定权在 E4 管线 + Owner 门位）

---

## 0. 条目数实查口径（当日为准，历史口径已漂移）

| 库 | 真源 | 声明 entry_count | 当日实查 | 历史口径 | 备注 |
|----|------|----------------|---------|---------|------|
| 指标库 | technical_indicator_registry.yaml | 102 | **102**（active 101 / deprecated 1） | 73 | 已扩容，last_updated 2026-08-15 |
| 图形库 | chart_pattern_registry.yaml | 287 | **287**（active 10 / candidate 277） | 287 | last_updated 2026-09-14 |
| 因子库 | factor_registry.yaml | （无声明字段） | **175**（candidate 170 / experimental 4 / deprecated 1） | — | last_updated 2026-08-28 |

**任务书口径勘误（诚实条款）**：
1. 任务书称因子库"含 C5 五 candidate 与 PP-001 配比 6 条 verified"——**实查不符**。factor_registry.yaml 中无 C5/PP-001 字样、无 verified 状态（status 仅 candidate/experimental/deprecated）。实查定位：C5 批候选的家族对质证据在 **strategy_registry.yaml**（`evidence` 字段记 "2026-09-13 C5聚类对质报告"，run=SCR-C4-20260913-002056）；PP-001 配比的 verified 语义落在 **config/framework_plans.yaml** 的 `fw-tdm-current` 方案（14 sleeves，其中 6 条 STR-VREV-025/VREV-026/MOMTREND-033/DABAN-023/TSMALL-001/VAL-001 各 0.05 观察档）。两处均为只读核实，未改动。
2. 任务书称"图形库 147 装配根已挂 JOB-108、market_pattern_event 物化事件 16/16"——实查 market_pattern_event：**22,791,117 行，2021-09-01..2026-09-15，distinct 事件类型（name）=104**（pattern_id 是事件实例 id，uniq=18,371，非类型数）。147 装配根与 16/16 口径未在表内复现，以本表实查为准。

## 1. E4 考纲口径（真源）

- 考纲文档：`docs/02_enterprise_architecture/02_domain_architecture_docs/35_d_backtest.md` §MOD-BT-211（F-06 E4 三阶段正考）。
- 考件：`scripts/backtest/f06_e4_wfa_exam.py`（IS→滚动 WFA→OOS；折法=训练 24 月/测试 6 月/步进 6 月，全窗 2020-01..2025-08 共 8 折；OOS/IS Sharpe 比率硬线 **0.70**（P0-9/SIM-38，`DEFAULT_OOS_SHARPE_THRESHOLD_RATIO`）；**精确 DSR** 由官方件 MOD-SIM-024 `c4_deflated_sharpe_runner` 注入，fail-closed）。
- 判定管线：`src/zephyr/backtest/core/strategy_validation_pipeline.py`（只编排不重造：OverfittingDetector 三维检测 + DecisionGate 三阶段门控；IS 准入 Sharpe>0.5；WFA 单折>0 且多数通过+灾难回撤 50% 否决；过拟合=WF 正折占比<60% 或 CV>1.5 或 OOS 比率<0.70；can_deploy 仍需人工审批；**IS 未过时按"阶段不可跳级"直接拦截 WFA/OOS**——本包任务②考试中 0/0 折即此跳过语义）。
- 回测口径：`_c4_engine` 冻结土规（佣金 2.5bp 双边 + 印花 10bp 卖 + 滑点 5bp）+ T+1（w.shift(1)）。

**三态判定定义（本文口径）**：
- **值得考**：三要素齐——①数据可得（CH 表/字段/时间覆盖支撑 E4 全窗或声明适配窗）；②可信号化（能翻译成日频仓位规则：截面 rank→top_n 多头 / 事件窗持有 / regime 开关）；③门可通过（成本后 OOS 期望现实性无先验否决）。给拟考窗+一句话信号化思路。
- **必死**：死因明确且不可修复——纯日内微观结构（E4 日频口径不可回测表达）、信号不可机械表达（叙事性条件/人工画线）、与既有池完全同源（已消费 regime 信号/已挂图另轨）、知识性/风控条目无考纲语义。
- **缺数据**：机制可考但数据面不达标——写明缺哪张表哪段覆盖（如未物化/DL 训练集未建/积累天数不足/历史未回补）。

## 2. 三态分布总表（底档 prereview_rows.json 机械重导，与原版一致）

| 库 | 条目 | 值得考 | 必死 | 缺数据 |
|----|------|-------|------|-------|
| 指标库 | 102 | 101 | 1（deprecated） | 0 |
| 图形库 | 287 | 78（已物化可考） | 50（主观图形：fibonacci 18 全灭/elliott 8 全灭/其他人工画线 24） | 159（未物化：JOB-108 未覆盖回补、缠论笔段缺接线、DL 训练集缺） |
| 因子库 | 175 | 126 | 39（日内 31、已消费同源 3、知识性 2、风控 1、数据资产 1、退役 1） | 10（情绪积累不足 9、日频估值未回补 1） |
| **合计** | **564** | **305** | **90** | **169** |

（csv 中可复核逐条 reason/exam_window；分类口径为机械规则+关键条目人工覆写，脚本存 `.runtime/tmp/sharpe2b/prereview_classify.py`）

### 各库判定要点

**指标库（101 值得考）**：全部条目 inputs ⊆ OHLCV，`technical_indicator` 表 3.54 亿行（2019-01-04 起，预热覆盖 2020 开考）机械可算。trend/momentum 族与 C4-v1 三因子（f_mom20/f_lowvol20/f_ma_gap）同源风险最高，考前须过**增量 IC 对基座预检**；volume/statistics 族（OBV/MFI/ADOSC/NVI 等 14 档）信息面最独立，排期最前。1 条 deprecated 判死。

**图形库（78 值得考 / 50 必死 / 159 缺数据）**：78 条已物化类型（market_pattern_event 2021-09 起）直接可考——考窗适配为 2021-10..2025-08（折法 18m/6m，仍满足无泄露切折）；信号化=事件日→事件股 T+1..T+5 条件超额或板块映射。必死 50 条集中于 fibonacci（18 全灭）与 elliott_wave（8 全灭）——人工画线/波浪计数无机械识别口径；chart_pattern/structure 另有 24 条高主观性判死。缺数据 159 条：DL 模型类（dl_training_dataset 空）、缠论笔/段/中枢（算法未接线）、以及规则法 candidate 未进物化管线的——修复路径=JOB-108 接线回补，不是死。
- 命名漂移发现（诚实记录）：物化事件中约 31 个类型名与注册表 name/name_zh/别名无法机械对映（如 TA-Lib `CDL3BLACKCROWS` 数词命名、`双顶` 中文命名、`X-` 前缀变体），已物化属实但**归属映射待人工挂接**；修复=一次性别名登记，不是重扫。

**因子库（126 值得考 / 39 必死 / 10 缺数据）**：
- 值得考主力：liquidity 34 / momentum 31 / technical 29（kline_daily_hfq 全史可算，增量 IC 预检）；**event 16**（事件面在库：market_pattern_event/calendar_event/typhoon_track，考窗适配 2021-10 起）；**expectations 6 全数排最前**——`consensus_daily_repaired` 165.5 万行（2017-01..2026-09-15）日频覆盖完整，字段含 eps_consensus/eps_std/n_orgs/rating_score_mean/n_buy，EP/修正动量/修正广度/异常覆盖/分歧度/评级动量六因子全部可考且机制独立（分析师预期=价量之外的信息面）；quality 6（financial_indicator 38.9 万行含 announce_date，PIT 滞后对齐）。
- 必死 39：intraday 31 条（E4 日频口径不可回测表达，含 FCT-INTRADAY-015"急跌必有急反"——叙事性条件陈述无参数化定义，双重死因）；已消费同源 3（BDI/温度/台风族中与 alt_regime_signal 现存 8 信号重复的变换）；knowledge_only 2 / risk_rule 1 / data_asset 1 / deprecated 1。
- 缺数据 10：sentiment 9 条（千股千评自 2026-09-11 起仅 4 个交易日、人气榜 13 天，截面因子需 ≥20-60 日积累——**时间会自动治愈，非永久死**）；value 1（daily_valuation 仅 2026-08 起 1.5 个月，stock_valuation 空表）。

## 3. 考位排期建议（值得考按 数据就绪度×机制独立性 排序，前 20，底档机械重导与原版一致）

排序分 = readiness(3=当日可得日频/2=滞后或短窗可得)×3 + independence(3=新信息面/2=独立变换/1=同源需预检)×2 + bonus(新数据面 +2 / 已物化 +2)。机读明细在 prereview.csv `priority_score` 列。

| 排期 | 库 | 条目 | 名称 | 分 | 拟考窗 |
|-----|----|------|------|----|--------|
| 1 | factor | FCT-EXP-001 | 一致预期EP | 17 | 2017-07..2025-08 |
| 2 | factor | FCT-EXP-002 | 修正动量 | 17 | 2017-07..2025-08 |
| 3 | factor | FCT-EXP-003 | 修正广度 | 17 | 2017-07..2025-08 |
| 4 | factor | FCT-EXP-004 | 异常覆盖 | 17 | 2017-07..2025-08 |
| 5 | factor | FCT-EXP-005 | 分歧度 | 17 | 2017-07..2025-08 |
| 6 | factor | FCT-EXP-006 | 评级动量 | 17 | 2017-07..2025-08 |
| 7-20 | indicator | IND-VOLUME-001..014 | OBV/MFI/VWAP/VR/AD/PVT/WVAD/VWMA/ADOSC/EOM/KVO/NVI/PVI/FORCE_INDEX | 15 | 2020-01..2025-08 |

排期逻辑：
1. **一致预期六因子最前**：唯一"新信息面+全史日频"双满格的族（consensus 2017 起 9.6 年），机制上与价量池正交，六因子共享一张表一次装配可成批考。
2. **量能指标族次之**（14 档并列 15 分）：technical_indicator 表现成，成交量为 v1 三因子未覆盖的信息面；批量同族考可摊薄数据装配成本。
3. **已物化图形 78 条**建议排在量能族之后成批考（事件窗统一框架一次建好，逐类型只换 pattern 名）。
4. expectations 考窗特殊（2017-07 起、折法 30m train/6m test 适配）已写入 csv exam_window 列，排产时勿用默认 2020 窗。

## 4. 可复现附录

```bash
# 1) 三库条目数实查（当日口径）
python -c "import yaml,io; d=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml',encoding='utf-8')); print(len(d['indicators']))"
# 2) 三态判定分类器（机械口径真源，读 registry_dump.json 底档可离线重跑）
python .runtime/tmp/sharpe2b/prereview_classify.py   # 产 prereview.csv + 判定分布
# 3) E4 硬线常量核对
python -c "from zephyr.backtest.core.overfitting_detector import DEFAULT_OOS_SHARPE_THRESHOLD_RATIO as r; print(r)"  # 0.70
# 4) market_pattern_event 物化类型数
# SELECT uniq(name) FROM c1_market.market_pattern_event  → 104
```

合规声明：本文档为研究方法与工程产出，不构成投资建议；全部结论基于当日只读实查，历史口径漂移处以实查为准。
