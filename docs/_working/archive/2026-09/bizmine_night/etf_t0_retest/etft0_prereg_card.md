---
ttl: task_bound
rule_form: data
verifiability: manual
title: ETFT0 预注册卡——高波资产做T 振幅经济学勘测（三宇宙，宇宙选择规则先于测量，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（本卡于任何宇宙筛选取数之前写死；实验启动后任何字段不得改动，改动即作废重开）
lane: W3（bizmine_general_order.md §7，Owner 裁定：T3 判定不外推到高波宇宙）
family_id: ETFT0-SCREEN
session: st-bizmine-etft0-20260919
parent_context: bizmine_general_order.md §7/§8 + t0_regime_prereg_card.md（frozen，方法论复刻母本）+ t0_regime_narrow_test_results.md（510300 基准：H 桶 req_cap=0.355 YELLOW，判定 TERMINATE）+ src/zephyr/backtest/core/cost_model_calibration.py:175-235（ADV 五分位与档位滑点真源）
---

# ETFT0：高波资产的 15min 振幅 economics 是否达成本门（三宇宙勘测）

## 1. 假设（H1，唯一，写死）

**510300=全市场最低波资产=做T 最不利样本，其 TERMINATE 判定不外推。在高波资产宇宙（行业/主题 ETF、T+0 类 ETF、高波个股）中，存在标的其高波状态桶的日中位 15min bar 振幅使所需捕获率 ≤0.50（脱红）乃至 ≤0.25（绿区）。**

零假设 H0：三宇宙全部标的×全部状态桶的所需捕获率均 >0.50（全红），或高波资产宇宙不存在振幅集中性。

诚实条款：本卡是**勘测族**（振幅分布×状态桶分解），不是逐笔考试族；结论只能是**振幅经济学**级（成本门槛数学可行性），任何手法的真实净边际仍须逐笔预注册卡出证。全部结果全量披露（含 RED），禁事后挑样。

## 2. 宇宙选择规则（先于测量，frozen；禁事后挑）

IS 期（选择窗）= **2024-01-01 → 2025-08-31**（本战役各车道统一考试窗）。

### 宇宙 A：行业/主题 ETF（top10）
- 母体 = `c1_market.kline_etf_15min` IS 期全部 ETF（名称经 `c1_market.etf_list` 匹配，代码映射 sh+5xxxxx/sz+15xxxx）。
- 分类关键词（对 etf_name 全名做子串匹配，规则写死）：半导体|芯片|集成电路|存储|消费电子|电子元件|软件|计算机|信息技术|人工智能|AI|机器人|通信|5G|6G|传媒|游戏|影视|动漫|文化|券商|证券|保险|银行|金融科技|军工|国防|航天|航空|船舶|光伏|光电|新能源|锂电池|电池|储能|煤炭|钢铁|有色|稀土|矿业|化工|化学|建材|地产|房地产|基建|电力|环保|水务|医药|医疗|生物|创新药|疫苗|健康|白酒|酒|食品|饮料|农业|养殖|畜牧|生猪|汽车|家电|消费|零售|旅游|纺织|造纸|物流|交运|港口|机场|云计算|大数据|信息安全|网络安全|区块链|数字经济|央企|国企|黄金|有色金属。
- 前置门槛（同下 B/C）：IS 期日均成交额（ADV）≥ **2 亿元**；15min 数据可用率 ≥80%（可用日定义见 §4；分母=该标的 IS 期在 kline_etf_15min 的自然存在日数）。
- 入组 = 分类命中 ∧ 门槛全过者中，按 **IS 期日中位 15min bar 振幅的全期中位数** 降序取 **top10**（排名指标=入组勘测同一指标，选择偏置如实披露，OOS 窗平行披露作诚实对照）。

### 宇宙 B：T+0 类 ETF（全入组，不设 topN）
- 类别定义（A 股唯一可真日内回转的标的，执行语义与 T+1 不同，单列判定）：
  - 债券：etf_type='债券型' 或名称含「债」；
  - 黄金/商品期货：名称含 黄金|原油|油气|石油|豆粕|豆一|豆二|商品 且**不含**「产业」「股票」（黄金产业/黄金股 ETF=T+1 股票类，归 A）；
  - 跨境 QDII：名称含 纳斯达克|纳指|标普|道琼斯|日经|德国|法国|沙特|亚太|东南亚|中概|恒生|香港|港股|美国|海外|全球|QDII；
  - REITs：名称含 REITs|基础设施（交易所 REITs 支持当日回转，机构实践口径）。
  - 排除：etf_type='货币型' 或名称含 货币|理财|现金（零振幅噪声源）。
- 分类优先级：**B 先于 A**（港股通医药→B 不入 A；中韩半导体 QDII→B；黄金产业股→A）。
- 入组 = B 命中 ∧ ADV≥2 亿 ∧ 可用率≥80%，**全量入组**。

### 宇宙 C：高波个股（top20）
- 母体 = `c1_market.kline_daily` IS 期全部个股。
- 剔除（frozen）：最新 `c1_market.stock_basic` 快照名称含 ST/退；list_date > 2023-01-01（IS 期初上市不满 1 年）；无 stock_basic 记录者（无法核名单，剔除并计数披露）。
- 门槛：IS 期 ADV（kline_daily amount 均值，元）≥ 2 亿元；`c1_market.kline_15min` 可用率 ≥80%（分母=该标的 IS 期 kline_daily 存在日数）。
- 波动指标 = IS 期逐日 rv20（20 日对数收益 std×√252，收盘价，原始未复权——诚实条款 adj_factor 恒 1）在 IS 期的**中位数**；降序取 **top20**。

### 数据缺口纪律
名称不可得（etf_list 缺口）/分钟数据缺段的标的：如实登记于报告「数据缺口」节，禁静默跳过。缺口标的若已入组（数据够 80%）照测；不足 80% 即不入组并登记。

## 3. 状态变量与分桶（与 T 车道 510300 基准完全同轴，frozen）

- 状态 = `c1_backtest.regime_state_anchored.vol_pct`（000300 hv20 滚动 250 日分位，连续灰度，PIT=rolling 只用 t 及以前）；**取 T-1 交易日**（双保险），asof 向后 7 自然日容差，弃日计数披露。
- 分桶边界 = **T 车道 frozen 边界 q33=0.328 / q67=0.700**（t0_regime_prereg_card.md §3，IS=2017-07-11→2026-05-31 已钉死；本卡复用=零新拟合+与 510300 基准逐位可比）。运行时对母本 IS 重算仅作一致性核验（偏差 >±0.005 记警告，不改判定）。
- 桶：L（vol_pct≤0.328）/ M（0.328<vol_pct≤0.700）/ H（>0.700）/ ALL。选型理由记录：任务令候选 c1_market.alt_regime_signal 经 T 车道实测为 BDI/BTC/FNG 另族信号，非大盘波动灰度；vol_pct 是与「高波状态」假设直接同构的唯一连续灰度。

## 4. 数据与振幅度量（frozen）

- 主粒度 = 15min bar：ETF 用 `c1_market.kline_etf_15min`，个股用 `c1_market.kline_15min`（IS 窗覆盖 5408 只已核实，免聚合 14.8 亿行 1min；若个别标的 15min 缺段而 1min 有，不作拼接——如实登记缺口，保持口径单一）。
- 去重：argMax(_, ingest_ts) per (symbol, trade_time)；时区：北京墙钟已核（9-15 点），去 tz 标签不平移；若运行时发现 hour≤7 行则按 +8h 规则平移并记录（承 T 卡 §4 在案规则）。
- 振幅：bar rng = (high−low)/prev_bar_close×10⁴（bp，prev=时间序前一根 bar 收盘，跨日延续；首根/prev≤0 弃）；**日统计量 = 当日全部 bar rng 中位数，bar 数 <12 的残日剔除（计数披露）**。
- 可用日 = 当日有有效日中位振幅；标的可用率 = 可用日/该标的窗内自然存在日。
- 测量双窗：**IS 窗 2024-01-01→2025-08-31（官方判定窗）+ OOS 披露窗 2025-09-01→2026-09-18**（同规则平行计算，仅披露，不参与选择与判定）。选择偏置声明：宇宙 A/C 按 IS 振幅/波动排名入选，IS 读数含选择偏置（方向=有利），OOS 披露窗为无偏对照。

## 5. 成本口径（各标的按自身 ADV 分档，frozen；禁统一 Q5）

- 滑点档（cost_model_calibration.py:175-234 真源）：ADV（元/日，IS 均值）<46,410,406.9→Q1 7.24bp；<90,212,531.7→Q2 5.69bp；<173,965,046.8→Q3 4.67bp；<417,979,415.5→Q4 4.00bp；≥→Q5 2.34bp（单边）。
  - 事实披露（写进报告）：ADV≥2 亿门槛在机械上把入组标的限定于 Q4/Q5 两档；档位规则照写照跑，档位分布如实披露。禁因「分档失感」而改门槛或改边界。
- 往返成本：ETF rt_bp = 2×(0.854 佣金 + 档位滑点 + 1.0 加成)（免印花）；个股 rt_bp = 上式 + 5.0（卖出印花税万5）。佣金 ¥5 地板：在 ≥10 万元单笔下不 binds，bp 式为主口径，地板对 3 万元以下碎单的影响如实披露不入判定。
- 判定门槛（口径写死一种，全表统一）：**threshold_bp = rt_bp × 1.43**（安全系数，承 T 车道 12bp/8.4bp=1.4286 同尺）。
- 所需捕获率 req_cap = threshold_bp / 桶内日中位振幅（amp_p50）；判定带（沿用）：**≤0.25 GREEN（数学可行）/ ≤0.50 YELLOW（脱红）/ >0.50 RED**。
- 可持续性诚实列：net@10% = 0.10×amp_p50 − rt_bp（每桶，如实展示符号）。

## 6. 判定与读出（frozen）

- 标的官方判定 = 其 **H 桶 IS 窗** grade（假设即「高波状态出手」）；若该标的 IS H 桶 <30 个有效日（罕见，披露）则退用 ALL 桶并显式标记。
- 宇宙判定阶梯：任一标的 GREEN → **GREEN_LANDS**；否则任一 YELLOW → **DE_RED_LANDS**；否则 **ALL_RED**。
- 池化读出（每宇宙）：池化桶统计 = 各标的桶 amp_p50 的中位数（跨标的），同 grade 规则；与逐标的表并列披露。
- OOS 持久性标记：IS 官方 GREEN/YELLOW 标的在 OOS 同桶读数并排披露；IS 绿而 OOS 红者标 fragile（不改变 IS 官方判定，但计入结论措辞）。
- 与 510300 基准对比：T3 官方 H 桶 req_cap=0.355（YELLOW，12bp 门槛）为对照锚；本卡各标的门槛=自身 rt×1.43（Q4/Q5 档下 11.99-23.89bp），对比时注明门槛差异。
- 多重检验位置（写进报告）：IS 官方 = (|A|+|B|+|C|)×4 桶 + 3 池化×4；OOS 披露同量。假阳性警惕声明：本卡是单假设（高波宇宙存在脱红标的）的勘测，不是 100 假设海选，标的×桶全披露即为诚实补救。

## 7. 执行与产物（frozen）

- 脚本：`.runtime/tmp/bizmine/etft0/etft0_screen.py`（先落本卡后取数）；宇宙中间件+结果 JSON：`.runtime/tmp/bizmine/etft0/etft0_universes.json`、`etft0_screen_result.json`。
- 产物：`docs/_working/bizmine_night/etf_t0_retest/etft0_screen_results.csv`（长表：universe,symbol,name,tier,rt_bp,threshold_bp,window,bucket,n_days,amp_p25/p50/p75,req_cap,grade,net_at_10pct_bp）+ `etft0_screen_report.md`。
- 附镜头（时间富余才做，不参与判定）：日 high-low 宽镜头（T 车道唯一绿区）在宇宙 A 上的读数。
- 合规：查库只读（DatabaseService reader，regime 表 plain MergeTree 无 FINAL）；禁下单、禁碰实盘/模拟盘；不碰 src/**、注册表（只读）、docs/03_modules/**。
- 执行模型备注（写进报告，不影响振幅勘测）：宇宙 A/C=T+1，执行模型为底仓T（昨仓卖出+当日回买），T+1 约束下「日内多次往返」受限，本勘测的桶振幅是**可捕获振幅的上界读数**；宇宙 B 可真日内回转。
