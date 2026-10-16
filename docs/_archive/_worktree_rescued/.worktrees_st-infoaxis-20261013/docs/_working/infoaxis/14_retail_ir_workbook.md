---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
session: st-infoaxis-20261013
date: 2026-10-13
title: 信息供给轴 P0 作业簿·千股千评·互动易域（散户情绪/IR 质量）
status: mining_sealed_pending_gate
goal_block:
  goal_statement: 从千股千评＋互动易两表中提取独占线索——机构参与度/主力成本衍生字段的散户情绪微信号＋互动易回复及时性/回避率的 IR 质量事件流；60 天采样窗内证伪则按 Q8 退役
  output_contract: retail_sentiment 微信号流（机构参与度 org_participation/主力成本衍生字段＋attention_index 正交化）＋ ir_quality_event 事件流（回复及时性/回避率/回复质量），全带 PIT 滞后面登记与退役判据绑定
  exam_ref: 与股吧/换手率正交化后增量 IC＋事件研究（预注册）＋Q8 退役判据（60 天采样窗：覆盖率低或正交化后 IC≈0 则退役）
  campaign_ref: st-infoaxis-20261013（裁定#516；Q8 已批"出信号先行"；挂情绪线 L2-05 水温＋板块情绪）
---

# 千股千评·互动易域作业簿（14_retail_ir_workbook.md）

## §1 问题定义（它出什么）

千股千评与互动易是散户注意力与公司 IR 行为两路数据。对标文献后独有价值收窄为两条：
①**机构参与度/主力成本**两衍生字段（千股千评独占，东财无第二家同口径）；②**回复
及时性/回避率**（互动易 IR 质量事件，Non-Answers FM 2026 增量信息）。其余字段
（情绪代理/阅读量/注意力）与股吧、换手率、百度指数高度重叠——正交化后无增量即退役
（Q8 判据绑定）。供：情绪线 L2-05 水温（daily_condition_sensor 11 信号）＋板块情绪。

## §2 输出契约 v0

```
retail_sentiment 微信号流（表名走 TableRegistry 派生，P2 定形）：
  code, trade_date, org_participation(0-1 原生), main_cost_dev(主力成本衍生,
  口径=加权均价对现价偏离, P2 冻结), attention_index_orth(对股吧/换手率正交化残差),
  pipeline_tag∈{orthogonalized, raw}, pit_lag 注册, freeze_batch_id
ir_quality_event 事件流（表名走 TableRegistry 派生）：
  code, question_ts, answer_ts, response_lag_days, evasion_flag(回避率判定),
  answer_quality_grade(positive/neutral/negative 公司口径＋置信度门 0.7 承接
  irm_interactive_extraction 现有件), event_type∈{timeliness, evasion, quality},
  pit_lag 注册, freeze_batch_id
枚举纪律：回避/及时/质量三态在本域唯一出口产出；千股千评无好评差评枚举为既定事实，
  禁止凭连续量伪造离散情绪档。
```

## §3 外部对标（2026-10-13 全网搜，详见班账 §8 车道回报）

| 来源 | 可借鉴点 |
|---|---|
| 东财千股千评（data.eastmoney.com/stockcomment） | 字段本身即情绪代理——与源站同义，非独占 |
| 江娇《金融研究》2017 | 股吧发帖情绪：含信息量高、情绪预示反转——但为股吧源非本域源（正交化对照项） |
| Gao 2019 | 股吧异常阅读量预测订单失衡——阅读量类信号归股吧，本域 attention_index 需对之正交 |
| Titman（NBER） | 注意力冲高回归——attention_index 原生语义，正交化后若无残差增量即归并 |
| 独占字段 | 机构参与度/主力成本两衍生字段：公开渠道无第二家同口径——本域保留核心理由 |
| Li 2023（DiD） | 线上互动降崩盘风险——互动易存在性效应，作 IR 质量事件研究先验 |
| Non-Answers（FM 2026) | 回答回避度/质量含增量信息——ir_quality_event 流的直接对标物 |
| Zhang 2013 / 百度指数 | SVI 标准代理——注意力对照组，非本域源 |

**Q8 结论（在案）**：不宜直接退役。独占线索=机构参与度＋回复及时性/回避率（IR 质量
事件）；60 天采样窗证明覆盖率低或正交化后 IC≈0 则退役——保留与退役判据同时预注册。

## §4 仓内四层盘点（六向台账·前四向）

### 4.1 数据面
- c1_market.alt_stock_comment 实查 88,372 行×12 列（DDL=schemas/categories/market/
  market_alt_stock_comment.py:44），17 个交易日 2026-09-11→2026-10-13，每交易日约
  5,196-5,200 行，每日 11:00UTC 入库（仅缺 09-25 一日）——**活性=活**（daily_event
  日更，tasks.yaml:2710）。
- c3_fundamental.irm_interactive_qa 实查 500 行（5 页×100 单次采集），67 个提问日
  2026-06-19→2026-09-16，唯一 ingest_ts=2026-09-18 04:23UTC——**死水 27 天**。
- G 盘冷库快照 G:/zephyr_cold/30_corpus/web_snapshots/<日期>_irm_interactive/
  （irm_provider.py:91,236）——冷库有存档，管线死水≠数据全失。

### 4.2 模块面
- AkshareAltProvider production（akshare_alt_provider.py:9），scheduler 已接线
  （scheduler.py:1718-1720）；同管线 alt 全景约 20 张（alt_sz_*/台风/运价/NDRC 油价/
  持仓等）——活表管线成熟，非孤例。
- IrmProvider new＋manual（irm_provider.py:6-7），**全仓零 import、工厂无 irm 分支——
  tasks.yaml:2050/2065 两条 source=irm 任务为孤儿，死水根因**：模块在、任务在、装配
  断链。
- 回复质量雏形=irm_interactive_extracted（irm_interactive_extraction.py:52 sentiment
  positive/neutral/negative 公司口径；irm_extract_batch.py:190-192 置信度门 0.7→
  approved/manual_pool）——实查仅 74 行，置信度门机制现成可承接。

### 4.3 接线面
- l9_readiness：A07（:119 max_lag=3）今日→green；A14（:125 max_lag=7）lag27>2×7→
  **red**（死水在案）；考卡 A07/A14 均 blocked_on_data。
- 消费端全仓唯一真实读数=cohort_daily_ledger.py:79,113（attention_index retail 人群
  辅列，experimental 仅 CLI 对账）。
- 情绪班/水温 daily_condition_sensor.py（11 信号→S0-S4）**零命中这两表**；
  CONSUMERS=scheduler only——两表在情绪线消费面为真空。

### 4.4 词表面
- 千股千评**无好评/差评枚举**（grep 零命中），仅连续量：composite_score/rank_change/
  current_rank/attention_index(0-100)/org_participation(0-1)——离散情绪档缺失为既定
  事实，输出契约按连续量正交化走。
- 互动易活跃度雏形=praise_count＋qa_status 原值，无下游加工。
- 回复质量枚举仅 irm_interactive_extracted 三档（公司口径）＋0.7 置信度门——
  本域 ir_quality_event 枚举件的唯一在仓基础。

## §5 六向台账（后两向）

### 5.5 判据面（看数前冻结预注册）
- 正交化增量 IC：retail_sentiment 各字段对股吧情绪/换手率/百度指数回归取残差后，对
  未来收益的增量 IC（RankIC）；原始 IC 与残差 IC 分列——残差 IC≈0 触发退役。
- 事件研究（预注册）：IR 质量事件（高回避率/超时回复）后 N 日超额＋方向命中；回避率
  分桶单调性。
- Q8 退役判据（60 天采样窗，与信号同步预注册）：①覆盖率门槛（ irm_interactive_qa
  采样覆盖率）；②正交化后 IC≈0 判定阈值——数值看数前冻结呈批。
- PIT：alt_stock_comment 11:00UTC 日更延迟登记为滞后面；irm 冷库快照日期对齐校验。

### 5.6 消费面
- 挂情绪线 L2-05 水温：retail_sentiment 正交化残差进 daily_condition_sensor 11 信号
  候选（现为零命中，接线即首消费）。
- 挂板块情绪：org_participation 板块聚合层。
- ir_quality_event 进信息事件标注（不占 18 格，X2-B 先例）＋负面否决器候选线索
  （回避率异常=治理风险信号，与 13 域 L3-04 同挂不同权）。
- cohort_daily_ledger retail 辅列：attention_index_orth 替换原生列（experimental→
  正式路径裁定随 C1）。

## §6 病灶诊断（自审闸输入）

| # | 病灶 | 定级 | 处置走向 |
|---|---|---|---|
| D1 | IrmProvider 全仓零 import、工厂无 irm 分支，tasks.yaml:2050/2065 两条 source=irm 任务孤儿——irm_interactive_qa 死水根因 | 阻断级 | P2 首刀：IrmProvider 接线入工厂分支（Q8 已批出信号先行，修复成本=免费级先行项） |
| D2 | A14 lag27>2×7=red，死水 27 天在案（唯一 ingest_ts=2026-09-18） | 阻断级（随 D1 修复） | D1 修复后回补采集，考卡转绿复验；修复无效则触发 C1 退役分支 |
| D3 | irm_interactive_extracted 仅 74 行且零下游消费（置信度门 0.7 机制在岗闲置） | 缺口级 | P2：批量抽取跑满存量 500 行＋接 ir_quality_event 出口 |
| D4 | 千股千评无好评/差评枚举、互动易无回避/及时枚举——全域离散枚举真空 | 缺口级 | P2：本域唯一出口产出 ir_quality_event 三态枚举；千股千评保持连续量不伪造档位 |
| D5 | 情绪线 daily_condition_sensor 11 信号零命中两表，CONSUMERS=scheduler only | 缺口级 | P2：L2-05 水温接线（正交化残差先于原值进场） |
| D6 | attention_index 唯一消费=cohort_daily_ledger 实验列仅 CLI 对账；09-25 缺一日 | 收口级 | 正交化改造时一并收口；缺日按停市/漏采标记不插补 |

## §7 待裁项（进 P1 总表）

| # | 项 | 选项 | 建议默认 |
|---|---|---|---|
| C1 | **本域核心待裁**：修 IrmProvider 接线入 factory 免费先行 vs 直接退役 | A 先修复管线＋60 天采样窗走起；B 直接退役两表 | A（Q8 已批"出信号先行"；修复=工厂分支一线之差，60 天窗证伪再走轨 B 墓碑不迟） |
| C2 | 正交化对照组与增量 IC 门槛/覆盖率门槛/窗宽等判据数值 | 看数前冻结呈批 | 股吧＋换手率＋百度指数三对照起步；数值留 P2 |
| C3 | attention_index_orth 替换 cohort_daily_ledger 原生列 | A 替换；B 双轨并存一期 | B 双轨一期（experimental 标签未摘，对账通过再切） |
| C4 | ir_quality_event 是否挂负面否决器 L3-04 | A 挂候选线索（低权）；B 不挂仅事件流 | A 低权候选（回避率异常与 13 域恶化事件并轨不重复计权） |

## §8 车道回报存档

- 仓内四层盘点：本役车道回报（2026-10-13，全带 :行号/yaml: 锚点＋实查行数/日期，照录
  于 §4）
- 外部对标：东财千股千评/江娇 2017/Gao 2019/Titman NBER/Li 2023 DiD/Non-Answers
  FM 2026/Zhang 2013 SVI（URL 在案班账）；Q8 结论在案引用

## §9 自审闸三态裁定（封矿）

- [x] 六向台账齐（数据/模块/接线/词表/判据/消费）
- [x] 病灶全部定级＋处置走向（6 条，含 2 阻断级）
- [x] 待裁项进 P1 总表（4 项，C1 核心待裁默认已给=先修复管线 60 天采样窗走起）
- [x] 与 13 域同批互引（L3-04 并轨不重复计权=C4；判据看数前冻结=C2 同款纪律）
- 状态：**过闸·封矿**（保留/退役双判据同步预注册＝Q8 纪律不违封矿；D1 工厂接线=
  本域 P2 首刀免费先行项）
