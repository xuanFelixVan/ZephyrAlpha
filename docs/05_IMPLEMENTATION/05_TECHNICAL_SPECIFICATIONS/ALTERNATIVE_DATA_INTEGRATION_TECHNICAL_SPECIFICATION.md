---
module_id: ALT_DATA_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 因子计算
  - 数据源
  - 机器学习
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵
applicable_scope: Layer 2 Alphaﮒ ﮒ­ﺅﺟ?- ﮒ۵ﻝﺎﭨﮔﺍﮔ؟ﮔﭦﻠﺅﺟ?| ﻛﺕﮒ۰ﮔﭘﮔ: ﻛﺕﻝﭦ۶ﮔﭘﻠﺑﮔ۰ﮔﭘﻟﮒﮔﭘﮔ
compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md
implementation_status: ﻟ۶ﮒﻠﭘﮔ؟ﭖ---


# ﮒ۵ﻝﺎﭨﮔﺍﮔ؟ﮔﭦﻠﮔﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **ﻟ۶ﮔ ﺙﻛﺗ۵ﻝﺙﺅﺟ?*: SPEC-ALT-DATA-2026-001
> **ﻟ۶ﮔ ﺙﻛﺗ۵ﻝﺅﺟ?*: v1.0
> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02
> **ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟**: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
> **ﻟﺁﮒ؟۰ﻝﭘﺅﺟﺛ?*: ﺅﺟ?ﮒﺓﺎﮔﺗﺅﺟ?
---

## ﻭ ﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ﮔ۵ﻟﺟﺍ

### ﮔﮔ۰۲ﻝ؟ﻝ

ﮔ؛ﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ﻟﺁ۵ﻝﭨﮒ؟ﻛﺗﻛﭦﮒ۵ﻝﺎﭨﮔﺍﮔ؟ﮔﭦﻠﮔﻠ۰ﺗﻝ؟ﻝﮔﮔﮔﮔﺁﻝﭨﻟﺅﺙﮒﮔ؛ﮔﭘﮔﻟ؟ﺝﻟ؟۰ﻙﮔ۴ﮒ۲ﮒ؟ﻛﺗﻙﮔﺍﮔ؟ﮔ۷۰ﮒﻙﻝ؟ﮔﺏﮒ؟ﻝﺍﻙﮔﭖﻟﺁﻝ­ﻝ۴ﻝ­ﺅﺙﻛﺕﭦﮒﺙﮒﮒ۱ﻠﮔﻛﺝﮒ؟ﮔﺑﻝﮔﮔﺁﮔﮒﺁﺙﺅﺟﺛ?
### ﻠﻝ۷ﻟﮒﺑ

ﮔ؛ﻟ۶ﮔ ﺙﻛﺗ۵ﻠﻝ۷ﻛﭦﺅﺙ
- ﮔﺍﮔ؟ﮒﺓ۴ﻝ۷ﮒﺕﺅﺙﮔﺍﮔ؟ﮔﭦﮔ۴ﮒ۴ﮒﮔﺍﮔ؟ﻠﻠ
- NLPﮒﺓ۴ﻝ۷ﮒﺕﺅﺙﮔﮔﮒﮔﮒﻛﭦﻛﭨﭘﮔﺅﺟ?- ﮒ ﮒ­ﻝ ﻝ۸ﭘﮒﺅﺙﮒ ﮒ­ﮔﮒﭨﭦﮒﻠ۹ﺅﺟ?- ﮔﭖﻟﺁﮒﺓ۴ﻝ۷ﮒﺕﺅﺙﻝﺏﭨﻝﭨﮔﭖﻟﺁﮒﻟﺑ۷ﻠﻛﺟﺅﺟ?
---

## ﻛﺕﻙﮔ۵ﺅﺟ?
### 1.1 ﻟ؟ﺝﻟ؟۰ﻟﮔﺁ

ﮔ ﺗﮔ؟Layer 2 Alphaﮒ ﮒ­ﮒﺎﮔﮔﺁﻟﺁﮒ؟۰ﻝﭨﮔﺅﺙ**ﮔﺍﮔ؟ﮔﭦﮒﺗﺟﮒﭦ۵ﻛﺕﺅﺟ?*ﮔﺁP0ﻝﭦ۶ﻠﭨﮔ­ﮔ۶ﻠ۲ﻠ۸ﻙﮒﺛﮒﻝﺏﭨﻝﭨﻛﭨﻛﺝﻟﭖiFinDﻙBaostockﻙAkShareﻛﺕﻛﺕ۹ﮔﺍﮔ؟ﮔﭦﺅﺙﻝﺙﭦﮒﺍﮔﺍﻠﭨﻙﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﻙﮒﮔﮒﺕﻠ۱ﮔﻝ­ﮒ۵ﻝﺎﭨﮔﺍﮔ؟ﺅﺙﻛﺕ۴ﻠﻠﮒﭘﻛﭦﮒ ﮒ­ﻝ ﻝ۸ﭘﮔﺓﺎﮒﭦ۵ﮒﮒﮒﮔ۶ﺅﺟﺛ?
### 1.2 ﮔﮔﺁﮒ؟ﺅﺟ?
**Layerﮒ؟ﻛﺛ**: Layer 2 - Alphaﮒ ﮒ­ﮒﺎﺅﺙﮔﺍﮔ؟ﮔﭦﮔ۸ﮒﺎﺅﺙ

**ﮔﮔﺁﮔﻝﮒﭦ۵**: ﮔﻝﺅﺙﮒﭦﻛﭦﮒ؛ﮒﺙAPIﮒﮒﺙﮔﭦﮒﺓ۴ﮒﺓﺅﺙ

**ﮒ؟ﮔﺛﮒ۳ﮔﺅﺟ?*: ﻛﺕ­ﻝ­ﺅﺙﻠﻟ۵NLPﮒ۳ﻝﮒﮒ ﮒ­ﮔﮒﭨﭦﺅﺙ

### 1.3 ﻝﮔ؛ﻛﺟ۰ﮔﺁ

| ﻝﮔ؛ | ﮔ۴ﮔ | ﮒﮔﺑﻟﺁﺑﮔ | ﻛﺛﺅﺟﺛ?|
|------|------|---------|------|
| v1.0 | 2026-04-02 | ﮒﮒ۶ﻝﮔ؛ | ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟ |

---

## ﻛﭦﻙﻟﺁ۵ﻝﭨﮔﭘﮔﻟ؟ﺝﺅﺟ?
### 2.1 ﮔﺑﻛﺛﮔﭘﮔﺅﺟ?
```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?ﺅﺟ?                   ﮒ۵ﻝﺎﭨﮔﺍﮔ؟ﮔﭦﻠﮔﮔﭘﺅﺟ?                                ﺅﺟ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?ﺅﺟ?                                                                    ﺅﺟ?ﺅﺟ? Layer 1: ﮔﺍﮔ؟ﮔﭦﮒﺎ (Data Sources)                                   ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮔﺍﻠﭨﮔﺍﮔ؟ﺅﺟ?                                                    ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻟﺑ۱ﻟﻝ۳ﺝAPI (CailianNewsDataSource)                         ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮔﺍﮔﭖ۹ﻟﺑ۱ﻝﭨAPI (SinaFinanceDataSource)                       ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻛﺕﮔﺗﻟﺑ۱ﮒﺁAPI (EastMoneyDataSource)                         ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﮔﺍﮔ؟ﺅﺟ?                                                ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮒﺝ؟ﮒAPI (WeiboDataSource)                                 ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻠ۹ﻝﻝﺛﻝ؛ﺅﺟ?(XueqiuDataSource)                             ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻛﺕﮔﺗﻟﺑ۱ﮒﺁﻟ۰ﮒ۶ (GubaDataSource)                             ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮒﮔﮒﺕﻠ۱ﮔﮔﺍﮔ؟ﮔﭦ                                               ﺅﺟ?ﺅﺟ?     ﻗﻗﻗ ﻛﺕﮔﺗﻟﺑ۱ﮒﺁﮒﮔﮒﺕﻠ۱ﺅﺟ?(AnalystExpectationDataSource)          ﺅﺟ?ﺅﺟ?     ﻗﻗﻗ ﮒﻟﺎﻠ۰ﭦﻝ ﺅﺟ?(ResearchReportDataSource)                      ﺅﺟ?ﺅﺟ?                                                                    ﺅﺟ?ﺅﺟ? Layer 2: ﮔﺍﮔ؟ﻠﻠﺅﺟ?(Data Collection)                              ﺅﺟ?ﺅﺟ? ﻗﻗﻗ APIﻠﻠﺅﺟ?(APIAdapter)                                        ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻝﭨﻛﺕAPIﻟﺍﻝ۷ﮔ۴ﮒ۲                                           ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻠﻟﺁﺁﮒ۳ﻝﮒﻠﻟﺁﮔﭦﺅﺟ?                                        ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻠ۱ﻝﻠﮒﭘﮔ۶ﮒﭘ                                               ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﻝ؛ﻟ،ﮒﺙﮔ (CrawlerEngine)                                      ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ Scrapyﮔ۰ﮔﭘ                                                ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ Seleniumﮒ۷ﮔﻠ۰ﭖﺅﺟ?                                         ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮒﻝ؛ﻟ،ﻝ­ﺅﺟ?                                                ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮒ؟ﮔﭘﮔﺍﮔ؟ﺅﺟ?(DataStream)                                       ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ WebSocketﻟﺟﮔ۴                                             ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ Kafkaﮔﭘﮔﺁﻠﮒﺅﺙﮒﺁﻠﺅﺙ                                      ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮔﺍﮔ؟ﻟﺍﮒﭦ۵ﺅﺟ?(DataScheduler)                                    ﺅﺟ?ﺅﺟ?     ﻗﻗﻗ Apache Airflow                                            ﺅﺟ?ﺅﺟ?     ﻗﻗﻗ ﮒ؟ﮔﭘﻛﭨﭨﮒ۰ﻝ؟۰ﻝ                                               ﺅﺟ?ﺅﺟ?                                                                    ﺅﺟ?ﺅﺟ? Layer 3: ﮔﺍﮔ؟ﮒ۳ﻝﺅﺟ?(Data Processing)                              ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮔﺍﮔ؟ﮔﺕﮔﺑ (DataCleaner)                                        ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮒﭨﻠﻙﮒﭨﺅﺟ?                                               ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮔ ﺙﮒﺙﮔ ﮒﺅﺟ?                                                ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮒﺙﮒﺕﺕﮔ۲ﺅﺟ?                                                  ﺅﺟ?ﺅﺟ? ﻗﻗﻗ NLPﮒ۳ﻝ (NLPProcessor)                                        ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮔﮔﮒﮔ (SentimentAnalyzer)                              ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻛﭦﻛﭨﭘﮔﮒ (EventExtractor)                                 ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮒ؟ﻛﺛﻟﺁﮒ، (EntityRecognizer)                               ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮒﺏﻝﺏﭨﮔﺛﮒ (RelationExtractor)                              ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮒﻠﺅﺟ?(Vectorizer)                                           ﺅﺟ?ﺅﺟ?     ﻗﻗﻗ ﮔﮔ؛ﮒﻠﺅﺟ?                                                ﺅﺟ?ﺅﺟ?     ﻗﻗﻗ ﮒﻠﮒ­ﮒ۷                                                   ﺅﺟ?ﺅﺟ?                                                                    ﺅﺟ?ﺅﺟ? Layer 4: ﮒ ﮒ­ﮔﮒﭨﭦﺅﺟ?(Factor Construction)                          ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮔﺍﻠﭨﮒ ﮒ­ (NewsFactors)                                        ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮔﮔﮒ ﮒ­ (SentimentFactor)                                ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮒ ﮒ­ (EventDrivenFactor)                          ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻝ­ﮒﭦ۵ﮒ ﮒ­ (HeatFactor)                                     ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮔﻝﭨ۹ﮒ ﮒ­ (SentimentFactors)                                   ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮒﺕﮒﭦﮔﻝﭨ۹ (MarketSentimentFactor)                          ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻛﺕ۹ﻟ۰ﮔﻝﭨ۹ (StockSentimentFactor)                           ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﻠ۱ﮔﮒ ﮒ­ (ExpectationFactors)                                 ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻠ۱ﮔﮒﺓ؟ﮒﺙﮒ ﮒ­ (ExpectationGapFactor)                       ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻟﺁﻝﭦ۶ﮒﮒﮒ ﮒ­ (RatingChangeFactor)                         ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮒﺏﮔﺏ۷ﮒﭦ۵ﮒ ﺅﺟ?(AttentionFactors)                                 ﺅﺟ?ﺅﺟ?     ﻗﻗﻗ ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﻝ­ﮒﭦ۵ﮒ ﮒ­ (SocialHeatFactor)                        ﺅﺟ?ﺅﺟ?                                                                    ﺅﺟ?ﺅﺟ? Layer 5: ﮒ ﮒ­ﻝ؟۰ﻝﺅﺟ?(Factor Management)                            ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮒ ﮒ­ﮒ­ﮒ۷ (FactorStorage)                                      ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ SQLiteﮔﺍﮔ؟ﺅﺟ?                                             ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ChromaDBﮒﻠﮔﺍﮔ؟ﺅﺟ?                                        ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ICﻠ۹ﻟﺁ (ICValidator)                                          ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ICﻟ؟۰ﻝ؟                                                    ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ICIRﻟ؟۰ﻝ؟                                                  ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮔﮔﮔ۶ﮔ۲ﺅﺟ?                                                ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮒ ﮒ­ﻝﮔ۶ (FactorMonitor)                                      ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﮒ؟ﮔﭘﻝﮔ۶                                                   ﺅﺟ?ﺅﺟ? ﺅﺟ?  ﻗﻗﻗ ﻟ۰ﺍﮒﮔ۲ﺅﺟ?                                                  ﺅﺟ?ﺅﺟ? ﻗﻗﻗ ﮒ ﮒ­ﮔﺏ۷ﮒ (FactorRegistry)                                     ﺅﺟ?ﺅﺟ?     ﻗﻗﻗ ﻟ۹ﮒ۷ﮔﺏ۷ﮒ                                                   ﺅﺟ?ﺅﺟ?     ﻗﻗﻗ ﮒﮔﺍﮔ؟ﻝ؟۰ﺅﺟ?                                                ﺅﺟ?ﺅﺟ?                                                                    ﺅﺟ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺅﺟ?```

### 2.2 Layerﮒ؟ﻛﺛﻟﺁﺑﮔ

| Layer | ﮒ؟ﻛﺛ | ﻟﻟﺑ۲ | ﮔﮔﺁﮔ  |
|-------|------|------|--------|
| **Layer 1** | ﮔﺍﮔ؟ﮔﭦﮒﺎ | ﮔﻛﺝﮒﮒ۶ﮔﺍﮔ؟ | ﮒ؛ﮒﺙAPIﻙﻝ؛ﺅﺟ?|
| **Layer 2** | ﮔﺍﮔ؟ﻠﻠﺅﺟ?| ﮔﺍﮔ؟ﻠﻠﮒﻟﺍﺅﺟ?| RequestsﻙScrapyﻙAirflow |
| **Layer 3** | ﮔﺍﮔ؟ﮒ۳ﻝﺅﺟ?| ﮔﺍﮔ؟ﮔﺕﮔﺑﮒNLPﮒ۳ﻝ | GLM-4-Flashﻙﮔ­۲ﮒﻟ۰۷ﻟﺝﺝﮒﺙ |
| **Layer 4** | ﮒ ﮒ­ﮔﮒﭨﭦﺅﺟ?| ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮒﮔﺅﺟ?| NumPyﻙPandas |
| **Layer 5** | ﮒ ﮒ­ﻝ؟۰ﻝﺅﺟ?| ﮒ ﮒ­ﮒ­ﮒ۷ﮒﻠ۹ﺅﺟ?| SQLiteﻙChromaDB |

### 2.3 ﮔ۷۰ﮒﻟﻟﺑ۲ﻟﺝﺗﻝ

```
ﮔﺍﮔ؟ﮔﭦﮒﺎ ﺅﺟ?ﮔﺍﮔ؟ﻠﻠﺅﺟ?ﺅﺟ?ﮔﺍﮔ؟ﮒ۳ﻝﺅﺟ?ﺅﺟ?ﮒ ﮒ­ﮔﮒﭨﭦﺅﺟ?ﺅﺟ?ﮒ ﮒ­ﻝ؟۰ﻝﺅﺟ?    ﺅﺟ?          ﺅﺟ?          ﺅﺟ?          ﺅﺟ?          ﺅﺟ? ﮒﮒ۶ﮔﺍﮔ؟    ﻠﻠﮔﺍﮔ؟    ﮔﺕﮔﺑﮔﺍﮔ؟    ﮒ ﮒ­ﮔﺍﮔ؟    ﮔﺏ۷ﮒﮒ ﮒ­
```

**ﻟﻟﺑ۲ﻟﺝﺗﻝ**:
- **ﮔﺍﮔ؟ﮔﭦﮒﺎ**: ﻛﭨﻟﺑﻟﺑ۲ﮔﻛﺝﮒﮒ۶ﮔﺍﮔ؟ﺅﺙﻛﺕﮔﭘﮒﮔﺍﮔ؟ﮒ۳ﺅﺟ?- **ﮔﺍﮔ؟ﻠﻠﺅﺟ?*: ﻛﭨﻟﺑﻟﺑ۲ﮔﺍﮔ؟ﻠﻠﺅﺙﻛﺕﮔﭘﮒﻛﺕﮒ۰ﻠﭨﻟﺝ
- **ﮔﺍﮔ؟ﮒ۳ﻝﺅﺟ?*: ﻛﭨﻟﺑﻟﺑ۲ﮔﺍﮔ؟ﮔﺕﮔﺑﮒNLPﮒ۳ﻝﺅﺙﻛﺕﮔﭘﮒﮒ ﮒ­ﻟ؟۰ﻝ؟
- **ﮒ ﮒ­ﮔﮒﭨﭦﺅﺟ?*: ﻛﭨﻟﺑﻟﺑ۲ﮒ ﮒ­ﻟ؟۰ﻝ؟ﺅﺙﻛﺕﮔﭘﮒﮔﺍﮔ؟ﮒ­ﺅﺟ?- **ﮒ ﮒ­ﻝ؟۰ﻝﺅﺟ?*: ﻛﭨﻟﺑﻟﺑ۲ﮒ ﮒ­ﮒ­ﮒ۷ﮒﻠ۹ﻟﺁﺅﺙﻛﺕﮔﭘﮒﮒ ﮒ­ﻟ؟۰ﻝ؟

---

## ﻛﺕﻙﮔ۴ﮒ۲ﮒ؟ﺅﺟ?
### 3.1 ﮔﺍﮔ؟ﮔﭦﮔ۴ﺅﺟ?
#### 3.1.1 ﮔﺍﻠﭨﮔﺍﮔ؟ﮔﭦﮔ۴ﺅﺟ?
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

class NewsDataSource(ABC):
    """ﮔﺍﻠﭨﮔﺍﮔ؟ﮔﭦﮒﭦﺅﺟ?""
    
    @abstractmethod
    def get_realtime_news(self, limit: int = 100) -> List[Dict]:
        """
        ﻟﺓﮒﮒ؟ﮔﭘﮔﺍﻠﭨ
        
        Args:
            limit: ﻟﺟﮒﮔﺍﻠﭨﮔﺍﻠ
            
        Returns:
            ﮔﺍﻠﭨﮒﻟ۰۷ﺅﺙﮔﺁﻛﺕ۹ﮔﺍﻠﭨﮒﮒ،ﺅﺙ
            - news_id: ﮔﺍﻠﭨID
            - title: ﮔ ﻠ۱
            - content: ﮒﮒ؟ﺗ
            - publish_time: ﮒﮒﺕﮔﭘﻠﺑ
            - source: ﮔﺍﮔ؟ﺅﺟ?            - url: ﻠﺝﮔ۴
        """
        pass
    
    @abstractmethod
    def get_stock_news(self, 
                       stock_code: str, 
                       start_date: datetime, 
                       end_date: datetime) -> List[Dict]:
        """
        ﻟﺓﮒﻛﺕ۹ﻟ۰ﻝﺕﮒﺏﮔﺍﻠﭨ
        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            start_date: ﮒﺙﮒ۶ﮔ۴ﺅﺟ?            end_date: ﻝﭨﮔﮔ۴ﮔ
            
        Returns:
            ﮔﺍﻠﭨﮒﻟ۰۷
        """
        pass
    
    @abstractmethod
    def search_news(self, 
                    keyword: str, 
                    start_date: datetime, 
                    end_date: datetime) -> List[Dict]:
        """
        ﮔﻝﺑ۱ﮔﺍﻠﭨ
        
        Args:
            keyword: ﮒﺏﻠ؟ﺅﺟ?            start_date: ﮒﺙﮒ۶ﮔ۴ﺅﺟ?            end_date: ﻝﭨﮔﮔ۴ﮔ
            
        Returns:
            ﮔﺍﻠﭨﮒﻟ۰۷
        """
        pass
```

#### 3.1.2 ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﮔﺍﮔ؟ﮔﭦﮔ۴ﺅﺟ?
```python
class SocialMediaDataSource(ABC):
    """ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﮔﺍﮔ؟ﮔﭦﮒﭦﺅﺟ?""
    
    @abstractmethod
    def get_stock_posts(self, 
                        stock_code: str, 
                        page: int = 1) -> List[Dict]:
        """
        ﻟﺓﮒﻟ۰ﻝ۴۷ﻝﺕﮒﺏﻟ؟۷ﻟ؟ﭦ
        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            page: ﻠ۰ﭖﻝ 
            
        Returns:
            ﻟ؟۷ﻟ؟ﭦﮒﻟ۰۷ﺅﺙﮔﺁﻛﺕ۹ﻟ؟۷ﻟ؟ﭦﮒﮒ،ﺅﺙ
            - post_id: ﮒﺕﮒ­ID
            - user_id: ﻝ۷ﮔﺓID
            - user_name: ﻝ۷ﮔﺓﺅﺟ?            - content: ﮒﮒ؟ﺗ
            - publish_time: ﮒﮒﺕﮔﭘﻠﺑ
            - likes: ﻝﺗﻟﭖﺅﺟ?            - comments: ﻟﺁﻟ؟ﭦﺅﺟ?            - reposts: ﻟﺛ؛ﮒﺅﺟ?        """
        pass
    
    @abstractmethod
    def get_hot_topics(self) -> List[Dict]:
        """
        ﻟﺓﮒﻝ­ﻠ۷ﻟﺁﻠ۱
        
        Returns:
            ﻝ­ﻠ۷ﻟﺁﻠ۱ﮒﻟ۰۷
        """
        pass
    
    @abstractmethod
    def get_user_posts(self, 
                       user_id: str, 
                       limit: int = 50) -> List[Dict]:
        """
        ﻟﺓﮒﻝ۷ﮔﺓﮒﮒﺕﮒﮒ؟ﺗ
        
        Args:
            user_id: ﻝ۷ﮔﺓID
            limit: ﻟﺟﮒﮔﺍﻠ
            
        Returns:
            ﻝ۷ﮔﺓﮒﮒﺕﮒﮒ؟ﺗﮒﻟ۰۷
        """
        pass
```

#### 3.1.3 ﮒﮔﮒﺕﻠ۱ﮔﮔﺍﮔ؟ﮔﭦﮔ۴ﮒ۲

```python
class AnalystExpectationDataSource(ABC):
    """ﮒﮔﮒﺕﻠ۱ﮔﮔﺍﮔ؟ﮔﭦﮒﭦﻝﺎﭨ"""
    
    @abstractmethod
    def get_analyst_rating(self, stock_code: str) -> List[Dict]:
        """
        ﻟﺓﮒﮒﮔﮒﺕﻟﺁﺅﺟ?        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            
        Returns:
            ﻟﺁﻝﭦ۶ﮒﻟ۰۷ﺅﺙﮔﺁﻛﺕ۹ﻟﺁﻝﭦ۶ﮒﮒ،ﺅﺙ
            - analyst_name: ﮒﮔﮒﺕﮒ۶ﺅﺟ?            - institution: ﮔﭦﮔﮒﻝ۶ﺍ
            - rating: ﻟﺁﻝﭦ۶
            - target_price: ﻝ؟ﮔ ﺅﺟ?            - report_date: ﮔ۴ﮒﮔ۴ﮔ
        """
        pass
    
    @abstractmethod
    def get_consensus_forecast(self, stock_code: str) -> Dict:
        """
        ﻟﺓﮒﻛﺕﻟﺑﻠ۱ﺅﺟ?        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            
        Returns:
            ﻛﺕﻟﺑﻠ۱ﮔﮔﺍﮔ؟ﺅﺙ
            - eps_forecast: EPSﻠ۱ﮔﭖ
            - revenue_forecast: ﻟ۴ﮔﭘﻠ۱ﮔﭖ
            - rating_consensus: ﻟﺁﻝﭦ۶ﻛﺕﻟﺑﻠ۱ﺅﺟ?        """
        pass
    
    @abstractmethod
    def get_rating_history(self, 
                          stock_code: str, 
                          start_date: datetime, 
                          end_date: datetime) -> List[Dict]:
        """
        ﻟﺓﮒﻟﺁﻝﭦ۶ﮒﮒﺎ
        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            start_date: ﮒﺙﮒ۶ﮔ۴ﺅﺟ?            end_date: ﻝﭨﮔﮔ۴ﮔ
            
        Returns:
            ﻟﺁﻝﭦ۶ﮒﮒﺎﮒﻟ۰۷
        """
        pass
```

### 3.2 NLPﮒ۳ﻝﮔ۴ﮒ۲

#### 3.2.1 ﮔﮔﮒﮔﮔ۴ﮒ۲

```python
class SentimentAnalyzer:
    """ﮔﮔﮒﮔﺅﺟ?""
    
    def analyze_sentiment(self, text: str) -> float:
        """
        ﮒﮔﮔﮔ؛ﮔﮔ
        
        Args:
            text: ﮔﮔ؛ﮒﮒ؟ﺗ
            
        Returns:
            ﮔﮔﮒﺝﮒﺅﺟ?1ﺅﺟ?ﺅﺟ?            -1: ﮔﮒﭦ۵ﻟﺑﻠ۱
            0: ﻛﺕ­ﺅﺟﺛ?            1: ﮔﮒﭦ۵ﮔ­۲ﻠ۱
        """
        pass
    
    def batch_analyze(self, texts: List[str]) -> List[float]:
        """
        ﮔﺗﻠﮔﮔﮒﮔ
        
        Args:
            texts: ﮔﮔ؛ﮒﻟ۰۷
            
        Returns:
            ﮔﮔﮒﺝﮒﮒﻟ۰۷
        """
        pass
```

#### 3.2.2 ﻛﭦﻛﭨﭘﮔﮒﮔ۴ﮒ۲

```python
class EventExtractor:
    """ﻛﭦﻛﭨﭘﮔﮒﺅﺟ?""
    
    def extract_events(self, text: str) -> Dict:
        """
        ﮔﮒﮔﺍﻠﭨﻛﭦﻛﭨﭘ
        
        Args:
            text: ﮔﺍﻠﭨﮔﮔ؛
            
        Returns:
            ﻛﭦﻛﭨﭘﻛﺟ۰ﮔﺁﺅﺟ?            - event_type: ﻛﭦﻛﭨﭘﻝﺎﭨﮒ
            - event_summary: ﻛﭦﻛﭨﭘﮔﻟ۵
            - related_stocks: ﻝﺕﮒﺏﻟ۰ﻝ۴۷
            - impact_level: ﮒﺛﺎﮒﻝ­ﻝﭦ۶ﺅﺙﻠ،/ﺅﺟ?ﻛﺛﺅﺙ
            - sentiment: ﮔﮔﮒﺝﮒﺅﺙﮔ­۲ﺅﺟ?ﻟﺑﻠ۱/ﻛﺕ­ﮔ۶ﺅﺙ
        """
        pass
```

#### 3.2.3 ﮒ؟ﻛﺛﻟﺁﮒ،ﮔ۴ﮒ۲

```python
class EntityRecognizer:
    """ﮒ؟ﻛﺛﻟﺁﮒ،ﺅﺟ?""
    
    def extract_stocks(self, text: str) -> List[str]:
        """
        ﮔﮒﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
        
        Args:
            text: ﮔﮔ؛ﮒﮒ؟ﺗ
            
        Returns:
            ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﮒﻟ۰۷
        """
        pass
    
    def extract_companies(self, text: str) -> List[str]:
        """
        ﮔﮒﮒ؛ﮒﺕﮒﻝ۶ﺍ
        
        Args:
            text: ﮔﮔ؛ﮒﮒ؟ﺗ
            
        Returns:
            ﮒ؛ﮒﺕﮒﻝ۶ﺍﮒﻟ۰۷
        """
        pass
```

### 3.3 ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮔ۴ﮒ۲

#### 3.3.1 ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮒﭦﻝﺎﭨ

```python
from abc import ABC, abstractmethod

class AlternativeDataFactorCalculator(ABC):
    """ﮒ۵ﻝﺎﭨﮔﺍﮔ؟ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮒﭦﻝﺎﭨ
    
    ﻟﻟﺑ۲ﻟﺝﺗﻝﻟﺁﺑﮔ:
    - ﮔ؛ﻝﺎﭨﻛﺕﻠ۷ﻝ۷ﻛﭦﮒ۵ﻝﺎﭨﮔﺍﮔ؟ﮒ ﮒ­ﺅﺙﮔﺍﻠﭨﮔﮔﻙﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﻝ­ﺅﺟ?    - ﮒﭦﻝ۰ﮒ ﮒ­ﺅﺙﻛﭨﺓﮒﺙﻙﮔﻠﺟﻙﮒ۷ﻠﻝ­ﺅﺙﻝﺎFactorCalculatorﮔ۷۰ﮒﻟﺑﻟﺑ۲
    - ﮒﺅﺟﺛ? [FACTOR_CALCULATOR](./FACTOR_CALCULATOR_TECHNICAL_SPECIFICATION.md)
    """
    
    @abstractmethod
    def calculate(self, 
                  stock_code: str, 
                  date: datetime, 
                  **kwargs) -> float:
        """
        ﻟ؟۰ﻝ؟ﮒ ﮒ­ﺅﺟ?        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            date: ﻟ؟۰ﻝ؟ﮔ۴ﮔ
            **kwargs: ﮒﭘﻛﭨﮒﮔﺍ
            
        Returns:
            ﮒ ﮒ­ﺅﺟ?        """
        pass
    
    @abstractmethod
    def batch_calculate(self, 
                       stock_codes: List[str], 
                       date: datetime) -> pd.Series:
        """
        ﮔﺗﻠﻟ؟۰ﻝ؟ﮒ ﮒ­
        
        Args:
            stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﮒﻟ۰۷
            date: ﻟ؟۰ﻝ؟ﮔ۴ﮔ
            
        Returns:
            ﮒ ﮒ­ﮒﺙﮒﭦﮒﺅﺙindex=stock_codeﺅﺟ?        """
        pass
    
    def get_factor_info(self) -> Dict:
        """
        ﻟﺓﮒﮒ ﮒ­ﻛﺟ۰ﮔﺁ
        
        Returns:
            ﮒ ﮒ­ﻛﺟ۰ﮔﺁﺅﺟ?            - factor_name: ﮒ ﮒ­ﮒﻝ۶ﺍ
            - factor_type: ﮒ ﮒ­ﻝﺎﭨﮒ
            - description: ﮒ ﮒ­ﮔﻟﺟﺍ
            - update_frequency: ﮔﺑﮔﺍﻠ۱ﻝ
            - data_window: ﮔﺍﮔ؟ﻝ۹ﮒ۲
            - expected_ic: ﻠ۱ﮔIC
        """
        pass
```

#### 3.3.2 ﮔﺍﻠﭨﮒ ﮒ­ﮔ۴ﮒ۲

```python
class NewsSentimentFactor(AlternativeDataFactorCalculator):
    """ﮔﺍﻠﭨﮔﮔﮒ ﮒ­"""
    
    def calculate(self, 
                  stock_code: str, 
                  date: datetime, 
                  window: int = 7) -> float:
        """
        ﻟ؟۰ﻝ؟ﮔﺍﻠﭨﮔﮔﮒ ﮒ­
        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            date: ﻟ؟۰ﻝ؟ﮔ۴ﮔ
            window: ﮔﭘﻠﺑﻝ۹ﮒ۲ﺅﺙﮒ۳۸ﺅﺟ?            
        Returns:
            ﮒ ﮒ­ﮒﺙﺅﺙ-1ﺅﺟ?ﺅﺟ?        """
        pass

class EventDrivenFactor(AlternativeDataFactorCalculator):
    """ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮒ ﮒ­"""
    
    def calculate(self, 
                  stock_code: str, 
                  date: datetime) -> float:
        """
        ﻟ؟۰ﻝ؟ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮒ ﮒ­
        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            date: ﻟ؟۰ﻝ؟ﮔ۴ﮔ
            
        Returns:
            ﮒ ﮒ­ﮒﺙﺅﺙﻛﭦﻛﭨﭘﮒﺛﺎﮒﮒﺝﮒﺅﺟ?        """
        pass

class NewsHeatFactor(AlternativeDataFactorCalculator):
    """ﮔﺍﻠﭨﻝ­ﮒﭦ۵ﮒ ﮒ­"""
    
    def calculate(self, 
                  stock_code: str, 
                  date: datetime, 
                  window: int = 7) -> float:
        """
        ﻟ؟۰ﻝ؟ﮔﺍﻠﭨﻝ­ﮒﭦ۵ﮒ ﮒ­
        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            date: ﻟ؟۰ﻝ؟ﮔ۴ﮔ
            window: ﮔﭘﻠﺑﻝ۹ﮒ۲ﺅﺙﮒ۳۸ﺅﺟ?            
        Returns:
            ﮒ ﮒ­ﮒﺙﺅﺙﻝ­ﮒﭦ۵ﮒﺝﮒﺅﺟ?        """
        pass
```

### 3.4 ﮒ ﮒ­ﻝ؟۰ﻝﮔ۴ﮒ۲

#### 3.4.1 ﮒ ﮒ­ﮔﺏ۷ﮒﮔ۴ﮒ۲

```python
class FactorRegistry:
    """ﮒ ﮒ­ﮔﺏ۷ﮒﺅﺟ?""
    
    def register_factor(self, 
                       factor_name: str,
                       factor_type: str,
                       calculator: AlternativeDataFactorCalculator,
                       metadata: Dict) -> str:
        """
        ﮔﺏ۷ﮒﮒ ﮒ­
        
        Args:
            factor_name: ﮒ ﮒ­ﮒﻝ۶ﺍ
            factor_type: ﮒ ﮒ­ﻝﺎﭨﮒ
            calculator: ﮒ ﮒ­ﻟ؟۰ﻝ؟ﺅﺟ?            metadata: ﮒ ﮒ­ﮒﮔﺍﺅﺟ?            
        Returns:
            ﮒ ﮒ­ID
        """
        pass
    
    def get_factor(self, factor_id: str) -> Dict:
        """
        ﻟﺓﮒﮒ ﮒ­ﻛﺟ۰ﮔﺁ
        
        Args:
            factor_id: ﮒ ﮒ­ID
            
        Returns:
            ﮒ ﮒ­ﻛﺟ۰ﮔﺁ
        """
        pass
    
    def list_factors(self, factor_type: Optional[str] = None) -> List[Dict]:
        """
        ﮒﮒﭦﮒ ﮒ­
        
        Args:
            factor_type: ﮒ ﮒ­ﻝﺎﭨﮒﺅﺙﮒﺁﻠﺅﺙ
            
        Returns:
            ﮒ ﮒ­ﮒﻟ۰۷
        """
        pass
```

#### 3.4.2 ICﻠ۹ﻟﺁﮔ۴ﮒ۲

```python
class ICValidator:
    """ICﻠ۹ﻟﺁﺅﺟ?""
    
    def calculate_ic(self, 
                     factor_values: pd.Series,
                     returns: pd.Series) -> float:
        """
        ﻟ؟۰ﻝ؟ICﺅﺟ?        
        Args:
            factor_values: ﮒ ﮒ­ﮒﺙﮒﭦﺅﺟ?            returns: ﮔﭘﻝﻝﮒﭦﺅﺟ?            
        Returns:
            ICﺅﺟ?        """
        pass
    
    def calculate_icir(self, 
                      ic_series: pd.Series) -> float:
        """
        ﻟ؟۰ﻝ؟ICIRﺅﺟ?        
        Args:
            ic_series: ICﮔﭘﻠﺑﮒﭦﮒ
            
        Returns:
            ICIRﺅﺟ?        """
        pass
    
    def validate_factor(self, 
                       factor_values: pd.DataFrame,
                       returns: pd.DataFrame,
                       min_ic: float = 0.03,
                       min_icir: float = 1.0) -> Dict:
        """
        ﻠ۹ﻟﺁﮒ ﮒ­ﮔﮔﺅﺟ?        
        Args:
            factor_values: ﮒ ﮒ­ﮒﺙﺅﺙindex=date, columns=stock_codeﺅﺟ?            returns: ﮔﭘﻝﻝﺅﺙindex=date, columns=stock_codeﺅﺟ?            min_ic: ﮔﮒﺍICﻠﺅﺟﺛ?            min_icir: ﮔﮒﺍICIRﻠﺅﺟﺛ?            
        Returns:
            ﻠ۹ﻟﺁﻝﭨﮔﺅﺟ?            - ic_mean: ICﮒﺅﺟﺛ?            - icir: ICIR
            - ic_std: ICﮔ ﮒﺅﺟ?            - is_valid: ﮔﺁﮒ۵ﮔﮔ
        """
        pass
```

---

## ﮒﻙﮔﺍﮔ؟ﮔ۷۰ﮒﻛﺕﮒ­ﮒ۷

### 4.1 ﮔﺍﮔ؟ﮒﭦﻟ۰۷ﻝﭨﮔ

#### 4.1.1 ﮔﺍﻠﭨﮔﺍﮔ؟ﺅﺟ?
```sql
CREATE TABLE news_data (
    news_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    publish_time TIMESTAMP NOT NULL,
    source TEXT NOT NULL,
    url TEXT,
    stock_codes TEXT,  -- JSON array
    sentiment REAL,
    event_type TEXT,
    event_summary TEXT,
    impact_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_publish_time ON news_data(publish_time);
CREATE INDEX idx_news_source ON news_data(source);
CREATE INDEX idx_news_sentiment ON news_data(sentiment);
CREATE INDEX idx_news_event_type ON news_data(event_type);
```

**ﮒ­ﮔ؟ﭖﻟﺁﺑﮔ**:
| ﮒ­ﮔ؟ﭖﺅﺟ?| ﻝﺎﭨﮒ | ﻟﺁﺑﮔ | ﻝﺑ۱ﮒﺙ |
|--------|------|------|------|
| news_id | TEXT | ﮔﺍﻠﭨﮒﺁﻛﺕIDﺅﺙﻛﺕﭨﻠ؟ﺅﺙ | PRIMARY |
| title | TEXT | ﮔﺍﻠﭨﮔ ﻠ۱ | - |
| content | TEXT | ﮔﺍﻠﭨﮔ­۲ﮔ | - |
| publish_time | TIMESTAMP | ﮒﮒﺕﮔﭘﻠﺑ | INDEX |
| source | TEXT | ﮔﺍﮔ؟ﮔ۴ﮔﭦ | INDEX |
| url | TEXT | ﮒﮔﻠﺝﮔ۴ | - |
| stock_codes | TEXT | ﻝﺕﮒﺏﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﺅﺙJSONﺅﺟ?| - |
| sentiment | REAL | ﮔﮔﮒﺝﮒﺅﺟ?1ﺅﺟ?ﺅﺟ?| INDEX |
| event_type | TEXT | ﻛﭦﻛﭨﭘﻝﺎﭨﮒ | INDEX |
| event_summary | TEXT | ﻛﭦﻛﭨﭘﮔﻟ۵ | - |
| impact_level | TEXT | ﮒﺛﺎﮒﻝ­ﻝﭦ۶ | - |

---

#### 4.1.2 ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﮔﺍﮔ؟ﺅﺟ?
```sql
CREATE TABLE social_posts (
    post_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,  -- weibo, xueqiu, guba
    user_id TEXT,
    user_name TEXT,
    content TEXT NOT NULL,
    publish_time TIMESTAMP NOT NULL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    stock_codes TEXT,  -- JSON array
    sentiment REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_platform ON social_posts(platform);
CREATE INDEX idx_posts_publish_time ON social_posts(publish_time);
CREATE INDEX idx_posts_sentiment ON social_posts(sentiment);
CREATE INDEX idx_posts_user ON social_posts(user_id);
```

---

#### 4.1.3 ﮒﮔﮒﺕﻠ۱ﮔﮔﺍﮔ؟ﻟ۰۷

```sql
CREATE TABLE analyst_expectations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,
    analyst_name TEXT,
    institution TEXT,
    rating TEXT,
    target_price REAL,
    eps_forecast REAL,
    revenue_forecast REAL,
    report_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analyst_stock ON analyst_expectations(stock_code);
CREATE INDEX idx_analyst_date ON analyst_expectations(report_date);
CREATE INDEX idx_analyst_institution ON analyst_expectations(institution);
```

---

#### 4.1.4 ﮒ ﮒ­ﮔﺍﮔ؟ﺅﺟ?
```sql
CREATE TABLE alternative_factors (
    factor_id TEXT PRIMARY KEY,
    factor_name TEXT NOT NULL,
    factor_type TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    date DATE NOT NULL,
    factor_value REAL NOT NULL,
    data_source TEXT,
    calculation_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(factor_name, stock_code, date)
);

CREATE INDEX idx_factor_type ON alternative_factors(factor_type);
CREATE INDEX idx_factor_date ON alternative_factors(date);
CREATE INDEX idx_factor_stock ON alternative_factors(stock_code);
CREATE INDEX idx_factor_name ON alternative_factors(factor_name);
```

---

#### 4.1.5 ﮒ ﮒ­ﮒﮔﺍﮔ؟ﻟ۰۷

```sql
CREATE TABLE factor_metadata (
    factor_id TEXT PRIMARY KEY,
    factor_name TEXT NOT NULL UNIQUE,
    factor_type TEXT NOT NULL,
    description TEXT,
    update_frequency TEXT,  -- daily, weekly, monthly
    data_window INTEGER,
    expected_ic REAL,
    ic_mean REAL,
    icir REAL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metadata_type ON factor_metadata(factor_type);
CREATE INDEX idx_metadata_active ON factor_metadata(is_active);
```

---

### 4.2 ﮒﻠﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﺅﺟ?
#### 4.2.1 ChromaDB Collectionﻟ؟ﺝﻟ؟۰

```python
from chromadb import Client
from chromadb.config import Settings

class VectorStore:
    """ﮒﻠﮒ­ﮒ۷"""
    
    def __init__(self, persist_directory: str = "./data/vector_db"):
        self.client = Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        
        # ﮔﺍﻠﭨﮒﻠﻠﮒ
        self.news_collection = self.client.get_or_create_collection(
            name="news_vectors",
            metadata={"description": "ﮔﺍﻠﭨﮔﮔ؛ﮒﻠ"}
        )
        
        # ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﮒﻠﻠﮒ
        self.posts_collection = self.client.get_or_create_collection(
            name="posts_vectors",
            metadata={"description": "ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﮔﮔ؛ﮒﻠ"}
        )
```

#### 4.2.2 ﮒﻠﮒ­ﮒ۷ﮔ ﺙﮒﺙ

**ﮔﺍﻠﭨﮒﻠ**:
```python
{
    "id": "news_001",
    "embedding": [0.1, 0.2, ...],  # 768ﻝﭨﺑﮒﺅﺟ?    "metadata": {
        "news_id": "news_001",
        "title": "ﮔﺍﻠﭨﮔ ﻠ۱",
        "publish_time": "2026-04-02T10:00:00",
        "source": "cailian",
        "sentiment": 0.8
    },
    "document": "ﮔﺍﻠﭨﮔ­۲ﮔﮒﮒ؟ﺗ"
}
```

**ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﮒﻠ**:
```python
{
    "id": "post_001",
    "embedding": [0.1, 0.2, ...],  # 768ﻝﭨﺑﮒﺅﺟ?    "metadata": {
        "post_id": "post_001",
        "platform": "weibo",
        "publish_time": "2026-04-02T10:00:00",
        "likes": 100,
        "sentiment": 0.6
    },
    "document": "ﮒﺝ؟ﮒﮒﮒ؟ﺗ"
}
```

---

### 4.3 ﮔﺍﮔ؟ﮔﭖﻟ؟ﺝﺅﺟ?
```
ﮔﺍﮔ؟ﺅﺟ?ﺅﺟ?ﮔﺍﮔ؟ﻠﻠ ﺅﺟ?ﮔﺍﮔ؟ﮔﺕﮔﺑ ﺅﺟ?NLPﮒ۳ﻝ ﺅﺟ?ﮒ ﮒ­ﻟ؟۰ﻝ؟ ﺅﺟ?ﮒ ﮒ­ﮒ­ﮒ۷
  ﺅﺟ?        ﺅﺟ?         ﺅﺟ?         ﺅﺟ?         ﺅﺟ?         ﺅﺟ?ﮒﮒ۶ﮔﺍﮔ؟  ﻠﻠﮔﺍﮔ؟   ﮔﺕﮔﺑﮔﺍﮔ؟   ﻝﭨﮔﮒﮔﺍﺅﺟ? ﮒ ﮒ­ﮔﺍﮔ؟   ﮔﺏ۷ﮒﮒ ﮒ­
```

**ﮔﺍﮔ؟ﮔﭖﻟﺛ؛ﻟﺟﻝ۷**:

1. **ﮔﺍﮔ؟ﻠﻠ**: ﻛﭨﮔﺍﮔ؟ﮔﭦﻟﺓﮒﮒﮒ۶ﮔﺍﮔ؟
2. **ﮔﺍﮔ؟ﮔﺕﮔﺑ**: ﮒﭨﻠﻙﮒﭨﮒ۹ﻙﮔ ﺙﮒﺙﮔ ﮒﮒ
3. **NLPﮒ۳ﻝ**: ﮔﮔﮒﮔﻙﻛﭦﻛﭨﭘﮔﮒﻙﮒ؟ﻛﺛﻟﺁﺅﺟ?4. **ﮒ ﮒ­ﻟ؟۰ﻝ؟**: ﮒﭦﻛﭦﮒ۳ﻝﮒﻝﮔﺍﮔ؟ﻟ؟۰ﻝ؟ﮒ ﮒ­
5. **ﮒ ﮒ­ﮒ­ﮒ۷**: ﮒ­ﮒ۷ﮒ ﮒ­ﮔﺍﮔ؟ﮒﮒﮔﺍﮔ؟
6. **ﮒ ﮒ­ﮔﺏ۷ﮒ**: ﮔﺏ۷ﮒﮒ ﮒ­ﮒﺍﮒ ﮒ­ﮒﭦ

---

## ﻛﭦﻙﻝ؟ﮔﺏﮒ؟ﻝﺍﻟﺁﺑﺅﺟ?
### 5.1 ﮔﮔﮒﮔﻝ؟ﮔﺏ

#### 5.1.1 ﻝ؟ﮔﺏﮒﻝ

ﻛﺛﺟﻝ۷GLM-4-Flashﻟﺟﻟ۰ﮔﮔﮒﮔﺅﺙﻠﻟﺟPrompt Engineeringﮒﺙﮒﺁﺙﮔ۷۰ﮒﻟﺝﮒﭦﮔﮔﮒﺝﮒﺅﺟ?
#### 5.1.2 ﮒ؟ﻝﺍﻛﭨ۲ﻝ 

```python
class SentimentAnalyzer:
    """ﮔﮔﮒﮔﺅﺟ?""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "glm-4-flash"
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
    def analyze_sentiment(self, text: str) -> float:
        """
        ﮒﮔﮔﮔ؛ﮔﮔ
        
        Args:
            text: ﮔﮔ؛ﮒﮒ؟ﺗ
            
        Returns:
            ﮔﮔﮒﺝﮒﺅﺟ?1ﺅﺟ?ﺅﺟ?        """
        prompt = f"""
        ﻟﺁﺓﮒﮔﻛﭨ۴ﻛﺕﻟﺑ۱ﻝﭨﮔﺍﻠﭨﻝﮔﮔﮒﺝﮒﺅﺙﻟﺟﺅﺟ?1ﺅﺟ?ﻛﺗﻠﺑﻝﮔﮔﮒﺝﮒﺅﺙ
        -1ﻟ۰۷ﻝ۳ﭦﮔﮒﭦ۵ﻟﺑﻠ۱ﺅﺟ?ﻟ۰۷ﻝ۳ﭦﻛﺕ­ﮔ۶ﺅﺙ1ﻟ۰۷ﻝ۳ﭦﮔﮒﭦ۵ﮔ­۲ﻠ۱
        
        ﮔﺍﻠﭨﮒﮒ؟ﺗﺅﺙ{text}
        
        ﻟﺁﺓﮒ۹ﻟﺟﮒﮔﮔﮒﺝﮒﮔﺍﮒﺙﺅﺙﻛﺕﻟ۵ﮒﭘﻛﭨﻟ۶۲ﻠﺅﺟ?        """
        
        response = self._call_api(prompt)
        sentiment_score = float(response.strip())
        
        # ﻝ۰؟ﻛﺟﮒﺝﮒﮒ۷[-1, 1]ﻟﮒﺑﺅﺟ?        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        return sentiment_score
    
    def _call_api(self, prompt: str) -> str:
        """ﻟﺍﻝ۷GLM-4 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        result = response.json()
        
        return result['choices'][0]['message']['content']
```

#### 5.1.3 ﮒ۳ﮔﮒﭦ۵ﮒﺅﺟ?
- **ﮔﭘﻠﺑﮒ۳ﮔﺅﺟ?*: O(n)ﺅﺙﮒﭘﻛﺕ­nﻛﺕﭦﮔﮔ؛ﻠﺟﺅﺟ?- **ﻝ۸ﭦﻠﺑﮒ۳ﮔﺅﺟ?*: O(1)
- **APIﻟﺍﻝ۷ﮔﮔ؛**: 0.1ﺅﺟ?ﻝﺝﻛﺕtokens

---

### 5.2 ﻛﭦﻛﭨﭘﮔﮒﻝ؟ﮔﺏ

#### 5.2.1 ﻝ؟ﮔﺏﮒﻝ

ﻛﺛﺟﻝ۷GLM-4-Flashﻟﺟﻟ۰ﻛﭦﻛﭨﭘﮔﮒﺅﺙﻟﺁﮒ،ﮔﺍﻠﭨﻛﺕ­ﻝﮒﺏﻠ؟ﻛﭦﻛﭨﭘﻙﮒﺛﺎﮒﻝ­ﻝﭦ۶ﮒﻝﺕﮒﺏﻟ۰ﻝ۴۷ﺅﺟ?
#### 5.2.2 ﮒ؟ﻝﺍﻛﭨ۲ﻝ 

```python
class EventExtractor:
    """ﻛﭦﻛﭨﭘﮔﮒﺅﺟ?""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "glm-4-flash"
        self.event_types = [
            'ﻛﺕﻝﭨ۸ﮒ؛ﮒ', 'ﮒﺗﭘﻟﺑ­ﻠﻝﭨ', 'ﻟ۰ﮔﮒﮒ۷', 'ﻠ،ﻝ؟۰ﮒﮒ۷',
            'ﻛﭦ۶ﮒﮒﮒﺕ', 'ﮔﺟﻝ­ﮒﺛﺎﮒ', 'ﻟ۰ﻛﺕﮒ۷ﺅﺟﺛ?, 'ﮒﺕﮒﭦﻛﭦﻛﭨﭘ'
        ]
        
    def extract_events(self, text: str) -> Dict:
        """
        ﮔﮒﮔﺍﻠﭨﻛﭦﻛﭨﭘ
        
        Args:
            text: ﮔﺍﻠﭨﮔﮔ؛
            
        Returns:
            ﻛﭦﻛﭨﭘﻛﺟ۰ﮔﺁﮒ­ﮒﺕ
        """
        prompt = f"""
        ﻟﺁﺓﻛﭨﻛﭨ۴ﻛﺕﻟﺑ۱ﻝﭨﮔﺍﻠﭨﻛﺕ­ﮔﮒﮒﺏﻠ؟ﻛﭦﻛﭨﭘﻛﺟ۰ﮔﺁﺅﺙ
        
        ﮔﺍﻠﭨﮒﮒ؟ﺗﺅﺙ{text}
        
        ﻟﺁﺓﻟﺟﮒJSONﮔ ﺙﮒﺙﺅﺟ?        {{
            "event_type": "ﻛﭦﻛﭨﭘﻝﺎﭨﮒﺅﺙﻛﭨﻛﭨ۴ﻛﺕﻠﮔ۸ﺅﺙ{', '.join(self.event_types)}ﺅﺟ?,
            "event_summary": "ﻛﭦﻛﭨﭘﮔﻟ۵ﺅﺟ?0ﮒ­ﻛﭨ۴ﮒﺅﺙ",
            "related_stocks": ["ﻝﺕﮒﺏﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ "],
            "impact_level": "ﮒﺛﺎﮒﻝ­ﻝﭦ۶ﺅﺙﻠ،/ﺅﺟ?ﻛﺛﺅﺙ",
            "sentiment": "ﮔﮔﮒﺝﮒﺅﺙﮔ­۲ﺅﺟ?ﻟﺑﻠ۱/ﻛﺕ­ﮔ۶ﺅﺙ"
        }}
        
        ﮒ۹ﻟﺟﮒJSONﺅﺙﻛﺕﻟ۵ﮒﭘﻛﭨﻟ۶۲ﻠﺅﺟﺛ?        """
        
        response = self._call_api(prompt)
        event_info = json.loads(response)
        
        return event_info
```

---

### 5.3 ﮒ ﮒ­ﻟ؟۰ﻝ؟ﻝ؟ﮔﺏ

#### 5.3.1 ﮔﺍﻠﭨﮔﮔﮒ ﮒ­ﻝ؟ﮔﺏ

```python
class NewsSentimentFactor(AlternativeDataFactorCalculator):
    """ﮔﺍﻠﭨﮔﮔﮒ ﮒ­"""
    
    def __init__(self, news_data_source, sentiment_analyzer):
        self.news_data_source = news_data_source
        self.sentiment_analyzer = sentiment_analyzer
        
    def calculate(self, 
                  stock_code: str, 
                  date: datetime, 
                  window: int = 7) -> float:
        """
        ﻟ؟۰ﻝ؟ﮔﺍﻠﭨﮔﮔﮒ ﮒ­
        
        ﻝ؟ﮔﺏﮔ­۴ﻠ۹۳ﺅﺟ?        1. ﻟﺓﮒﻟﺟﮒﭨwindowﮒ۳۸ﻝﻝﺕﮒﺏﮔﺍﻠﭨ
        2. ﻟ؟۰ﻝ؟ﮔﺁﮔ۰ﮔﺍﻠﭨﻝﮔﮔﮒﺝﺅﺟ?        3. ﮒ ﮔﮒﺗﺏﮒﺅﺙﻟﺟﮔﮔﺍﻠﭨﮔﻠﮔﺑﻠ،ﺅﺙ
        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            date: ﻟ؟۰ﻝ؟ﮔ۴ﮔ
            window: ﮔﭘﻠﺑﻝ۹ﮒ۲ﺅﺙﮒ۳۸ﺅﺟ?            
        Returns:
            ﮒ ﮒ­ﮒﺙﺅﺙ-1ﺅﺟ?ﺅﺟ?        """
        # 1. ﻟﺓﮒﻟﺟﮒﭨwindowﮒ۳۸ﻝﻝﺕﮒﺏﮔﺍﻠﭨ
        start_date = date - timedelta(days=window)
        news_list = self.news_data_source.get_stock_news(
            stock_code, start_date, date
        )
        
        if not news_list:
            return 0.0
        
        # 2. ﻟ؟۰ﻝ؟ﮔﺁﮔ۰ﮔﺍﻠﭨﻝﮔﮔﮒﺝﺅﺟ?        sentiments = []
        for news in news_list:
            if news.get('sentiment') is not None:
                sentiment = news['sentiment']
            else:
                sentiment = self.sentiment_analyzer.analyze_sentiment(
                    news['content']
                )
            sentiments.append(sentiment)
        
        # 3. ﮒ ﮔﮒﺗﺏﮒﺅﺙﻟﺟﮔﮔﺍﻠﭨﮔﻠﮔﺑﻠ،ﺅﺙ
        weights = np.exp(np.linspace(-1, 0, len(sentiments)))
        weights = weights / weights.sum()
        
        factor_value = np.average(sentiments, weights=weights)
        
        return factor_value
```

**ﻝ؟ﮔﺏﮒ۳ﮔﺅﺟ?*:
- ﮔﭘﻠﺑﮒ۳ﮔﺅﺟ? O(n)ﺅﺙﮒﭘﻛﺕ­nﻛﺕﭦﮔﺍﻠﭨﮔﺍﺅﺟ?- ﻝ۸ﭦﻠﺑﮒ۳ﮔﺅﺟ? O(n)

---

#### 5.3.2 ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮒ ﮒ­ﻝ؟ﮔﺏ

```python
class EventDrivenFactor(AlternativeDataFactorCalculator):
    """ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮒ ﮒ­"""
    
    # ﻛﭦﻛﭨﭘﮒﺛﺎﮒﮒﭦﮒﮒﺝﮒ
    EVENT_IMPACT_MAP = {
        'ﻛﺕﻝﭨ۸ﮒ؛ﮒ': 0.8,
        'ﮒﺗﭘﻟﺑ­ﻠﻝﭨ': 0.9,
        'ﻟ۰ﮔﮒﮒ۷': 0.7,
        'ﻠ،ﻝ؟۰ﮒﮒ۷': 0.5,
        'ﻛﭦ۶ﮒﮒﮒﺕ': 0.6,
        'ﮔﺟﻝ­ﮒﺛﺎﮒ': 0.8,
        'ﻟ۰ﻛﺕﮒ۷ﺅﺟﺛ?: 0.4,
        'ﮒﺕﮒﭦﻛﭦﻛﭨﭘ': 0.3
    }
    
    def __init__(self, news_data_source, event_extractor):
        self.news_data_source = news_data_source
        self.event_extractor = event_extractor
        
    def calculate(self, stock_code: str, date: datetime) -> float:
        """
        ﻟ؟۰ﻝ؟ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷ﮒ ﮒ­
        
        ﻝ؟ﮔﺏﮔ­۴ﻠ۹۳ﺅﺟ?        1. ﻟﺓﮒﻟﺟﮔﻠﮒ۳۶ﻛﭦﻛﭨﭘ
        2. ﻟ؟۰ﻝ؟ﮔﺁﻛﺕ۹ﻛﭦﻛﭨﭘﻝﮒﺛﺎﮒﮒﺝﺅﺟ?        3. ﻝﭨﺙﮒﻟﺁﻛﺙﺍﻛﭦﻛﭨﭘﮒﺛﺎﮒ
        
        Args:
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            date: ﻟ؟۰ﻝ؟ﮔ۴ﮔ
            
        Returns:
            ﮒ ﮒ­ﮒﺙﺅﺙﻛﭦﻛﭨﭘﮒﺛﺎﮒﮒﺝﮒﺅﺟ?        """
        # 1. ﻟﺓﮒﻟﺟﮔﻠﮒ۳۶ﻛﭦﻛﭨﭘ
        start_date = date - timedelta(days=30)
        news_list = self.news_data_source.get_stock_news(
            stock_code, start_date, date
        )
        
        # 2. ﮔﮒﻛﭦﻛﭨﭘﻛﺟ۰ﮔﺁ
        events = []
        for news in news_list:
            if news.get('event_type'):
                event_info = {
                    'event_type': news['event_type'],
                    'impact_level': news.get('impact_level', 'ﺅﺟ?),
                    'sentiment': news.get('sentiment', 'ﻛﺕ­ﺅﺟﺛ?),
                    'publish_time': news['publish_time']
                }
                events.append(event_info)
        
        if not events:
            return 0.0
        
        # 3. ﻟ؟۰ﻝ؟ﻛﭦﻛﭨﭘﮒﺛﺎﮒﮒﺝﮒ
        impact_scores = []
        for event in events:
            # ﮒﭦﮒﮒﺝﮒ
            base_score = self.EVENT_IMPACT_MAP.get(event['event_type'], 0.5)
            
            # ﮒﺛﺎﮒﻝ­ﻝﭦ۶ﻛﺗﮔﺍ
            level_multiplier = {'ﺅﺟ?: 1.0, 'ﺅﺟ?: 0.6, 'ﺅﺟ?: 0.3}.get(
                event['impact_level'], 0.6
            )
            
            # ﮔﮔﻛﺗﮔﺍ
            sentiment_multiplier = {'ﮔ­۲ﻠ۱': 1.0, 'ﻟﺑﻠ۱': -1.0, 'ﻛﺕ­ﺅﺟﺛ?: 0.0}.get(
                event['sentiment'], 0.0
            )
            
            # ﮔﭘﻠﺑﻟ۰ﺍﮒﺅﺙﻟﺟﮔﻛﭦﻛﭨﭘﮔﻠﮔﺑﻠ،ﺅﺙ
            days_ago = (date - event['publish_time']).days
            time_decay = np.exp(-days_ago / 30)  # 30ﮒ۳۸ﻟ۰ﺍﮒﮒ۷ﺅﺟ?            
            # ﻝﭨﺙﮒﮒﺝﮒ
            score = base_score * level_multiplier * sentiment_multiplier * time_decay
            impact_scores.append(score)
        
        # 4. ﻝﭨﺙﮒﻟﺁﻛﺙﺍ
        factor_value = np.mean(impact_scores)
        
        return factor_value
```

---

## ﮒ­ﻙﮒ؟ﮔﺛﮔﮔﺁﮔ 

### 6.1 ﻝﺙﻝ۷ﻟﺁ­ﻟ۷ﮒﮔ۰ﺅﺟ?
| ﮔﮔﺁﻠ۱ﺅﺟ?| ﮔﮔﺁﻠﮒ | ﻝﮔ؛ | ﻟﺁﺑﮔ |
|---------|---------|------|------|
| **ﻝﺙﻝ۷ﻟﺁ­ﻟ۷** | Python | 3.9+ | ﻛﺕﭨﻟ۵ﮒﺙﮒﻟﺁ­ﻟ۷ |
| **ﻝ؛ﻟ،ﮔ۰ﮔﭘ** | Scrapy | 2.11+ | ﮔﺍﮔ؟ﻠﻠ |
| **ﮒ۷ﮔﻠ۰ﭖﺅﺟ?* | Selenium | 4.15+ | JavaScriptﮔﺕﺎﮔ |
| **HTTPﻟﺁﺓﮔﺎ** | Requests | 2.31+ | APIﻟﺍﻝ۷ |
| **ﮔﺍﮔ؟ﮒ۳ﻝ** | Pandas | 2.1+ | ﮔﺍﮔ؟ﮒ۳ﻝ |
| **ﮔﺍﮒﺙﻟ؟۰ﺅﺟ?* | NumPy | 1.26+ | ﮔﺍﮒﺙﻟ؟۰ﺅﺟ?|

### 6.2 ﻝ؛؛ﻛﺕﮔﺗﻛﺝﺅﺟ?
| ﻛﺝﻟﭖﺅﺟ?| ﻝﮔ؛ | ﻝ۷ﺅﺟﺛ?|
|--------|------|------|
| **chromadb** | 0.4.0+ | ﮒﻠﮔﺍﮔ؟ﺅﺟ?|
| **zhipuai** | 2.0.0+ | GLM-4 API |
| **apache-airflow** | 2.7.0+ | ﻛﭨﭨﮒ۰ﻟﺍﮒﭦ۵ |
| **redis** | 5.0.0+ | ﻝﺙﮒ­ |
| **sqlalchemy** | 2.0.0+ | ORM |

### 6.3 ﻝﺁﮒ۱ﻟ۵ﮔﺎ

| ﻝﺁﮒ۱ | ﻟ۵ﮔﺎ |
|------|------|
| **ﮔﻛﺛﻝﺏﭨﻝﭨ** | Windows 10/11, Linux, macOS |
| **ﮒﮒ­** | ﺅﺟ?GB |
| **ﮒ­ﮒ۷** | ﺅﺟ?0GBﮒﺁﻝ۷ﻝ۸ﭦﻠﺑ |
| **ﻝﺛﻝﭨ** | ﻝ۷ﺏﮒ؟ﻝﻛﭦﻟﻝﺛﻟﺟﮔ۴ |

---

## ﻛﺕﻙﮔﭖﻟﺁﻝ­ﺅﺟ?
### 7.1 ﮒﮒﮔﭖﻟﺁ

#### 7.1.1 ﮔﭖﻟﺁﻟﮒﺑ

| ﮔ۷۰ﮒ | ﮔﭖﻟﺁﮒﮒ؟ﺗ | ﻟ۵ﻝﻝﻝ؟ﺅﺟ?|
|------|---------|-----------|
| **ﮔﺍﮔ؟ﻠﻠ** | APIﻟﺍﻝ۷ﻙﮔﺍﮔ؟ﻟ۶۲ﺅﺟ?| >85% |
| **NLPﮒ۳ﻝ** | ﮔﮔﮒﮔﻙﻛﭦﻛﭨﭘﮔﺅﺟ?| >80% |
| **ﮒ ﮒ­ﻟ؟۰ﻝ؟** | ﮒ ﮒ­ﻟ؟۰ﻝ؟ﻠﭨﻟﺝ | >90% |
| **ﮔﺍﮔ؟ﮒ­ﮒ۷** | ﮔﺍﮔ؟ﮒﭦﮔﺅﺟ?| >85% |

#### 7.1.2 ﮔﭖﻟﺁﻝ۷ﻛﺝﻝ۳ﭦﻛﺝ

```python
import pytest
from datetime import datetime

class TestNewsSentimentFactor:
    """ﮔﺍﻠﭨﮔﮔﮒ ﮒ­ﮔﭖﻟﺁ"""
    
    def test_calculate_with_positive_news(self):
        """ﮔﭖﻟﺁﮔ­۲ﻠ۱ﮔﺍﻠﭨﻝﮒ ﮒ­ﻟ؟۰ﺅﺟ?""
        factor = NewsSentimentFactor(mock_news_source, mock_sentiment_analyzer)
        
        # ﮔ۷۰ﮔﮔ­۲ﻠ۱ﮔﺍﻠﭨ
        mock_news_source.get_stock_news.return_value = [
            {
                'news_id': '001',
                'title': 'ﮒ۸ﮒ۴ﺛﮔﭘﮔﺁ',
                'content': 'ﮒ؛ﮒﺕﻛﺕﻝﭨ۸ﮒ۳۶ﮒﺗﮒ۱ﻠﺟ',
                'publish_time': datetime(2026, 4, 1),
                'sentiment': 0.8
            }
        ]
        
        factor_value = factor.calculate('000001.SZ', datetime(2026, 4, 2))
        
        assert factor_value > 0
        assert factor_value <= 1
    
    def test_calculate_with_no_news(self):
        """ﮔﭖﻟﺁﮔ ﮔﺍﻠﭨﮔﭘﻝﮒ ﮒ­ﻟ؟۰ﺅﺟ?""
        factor = NewsSentimentFactor(mock_news_source, mock_sentiment_analyzer)
        
        mock_news_source.get_stock_news.return_value = []
        
        factor_value = factor.calculate('000001.SZ', datetime(2026, 4, 2))
        
        assert factor_value == 0.0
```

---

### 7.2 ﻠﮔﮔﭖﻟﺁ

#### 7.2.1 ﮔﭖﻟﺁﮒﭦﮔﺁ

| ﮒﭦﮔﺁ | ﮔﭖﻟﺁﮒﮒ؟ﺗ | ﻠ۹ﮔﭘﮔ ﮒ |
|------|---------|---------|
| **ﮔﺍﮔ؟ﻠﻠﮔﭖﻝ۷** | ﻛﭨﮔﺍﮔ؟ﮔﭦﮒﺍﮔﺍﮔ؟ﮒﭦﻝﮒ؟ﮔﺑﮔﭖﺅﺟ?| ﮔﺍﮔ؟ﮒ؟ﮔﺑﺅﺟ?95% |
| **NLPﮒ۳ﻝﮔﭖﻝ۷** | ﻛﭨﮒﮒ۶ﮔﮔ؛ﮒﺍﻝﭨﮔﮒﮔﺍﺅﺟ?| ﮒﻝ۰؟ﺅﺟ?80% |
| **ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮔﭖﻝ۷** | ﻛﭨﮔﺍﮔ؟ﮒﺍﮒ ﮒ­ﻝﮒ؟ﮔﺑﮔﭖﺅﺟ?| IC>0.03 |

---

### 7.3 ﮔ۶ﻟﺛﮔﭖﻟﺁ

#### 7.3.1 ﮔ۶ﻟﺛﮔﮔ 

| ﮔﮔ  | ﻝ؟ﮔ ﺅﺟ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|--------|---------|
| **ﮔﺍﮔ؟ﻠﻠﮒﭨﭘﻟﺟ** | <5ﮒﻠ | ﮒﮒﮔﭖﻟﺁ |
| **ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮒﭨﭘﻟﺟ** | <10ﺅﺟ?| ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﮒﺗﭘﮒﮒ۳ﻝﻟﺛﮒ** | >100ﻟﺁﺓﮔﺎ/ﺅﺟ?| ﮒﺗﭘﮒﮔﭖﻟﺁ |

---

## ﮒ،ﻙﻠ۲ﻠ۸ﻛﺕﻝﭦ۵ﮔ

### 8.1 ﮔﮔﺁﻠ۲ﺅﺟ?
| ﻠ۲ﻠ۸ | ﮒﺛﺎﮒ | ﮔ۵ﻝ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |
|------|------|------|---------|
| **APIﻠ۱ﻝﻠﮒﭘ** | ﺅﺟ?| ﺅﺟ?| ﻟﺁﺓﮔﺎﻠﮒﻙﮒ۳ﻟﺑ۵ﮒﺓﻟﺛ؟ﮔ۱ |
| **ﮔﺍﮔ؟ﻟﺑ۷ﻠﻛﺕﻝ۷ﺏﺅﺟ?* | ﺅﺟ?| ﺅﺟ?| ﮔﺍﮔ؟ﮔﺕﮔﺑﻙﮒﺙﮒﺕﺕﮔ۲ﺅﺟ?|
| **NLPﮒﻝ۰؟ﻝﻛﺕﺅﺟ?* | ﺅﺟ?| ﺅﺟ?| ﮔ۷۰ﮒﻛﺙﮒﻙﻛﭦﭦﮒﺓ۴ﮔ ﺅﺟ?|
| **ﻝﺏﭨﻝﭨﮔ۶ﻟﺛﻝﭘﻠ۱** | ﺅﺟ?| ﺅﺟ?| ﮒﺙﮔ­۴ﮒ۳ﻝﻙﻝﺙﮒ­ﻛﺙﺅﺟ?|

### 8.2 ﮒ؟ﮔﺛﻠ۲ﻠ۸

| ﻠ۲ﻠ۸ | ﮒﺛﺎﮒ | ﮔ۵ﻝ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |
|------|------|------|---------|
| **ﻟﺟﮒﭦ۵ﮒﭨﭘﮔ** | ﺅﺟ?| ﺅﺟ?| ﻠ۱ﻝﻝﺙﮒﺎﻙﮒﺗﭘﻟ۰ﮒﺙﺅﺟ?|
| **ﻟﭖﮔﭦﻛﺕﻟﭘﺏ** | ﺅﺟ?| ﺅﺟ?| ﻛﺙﮒﻝﭦ۶ﻝ؟۰ﺅﺟ?|
| **ﻠﮔﺎﮒﺅﺟ?* | ﺅﺟ?| ﺅﺟ?| ﻠﮔﺎﮒﭨﺅﺟ?|

### 8.3 ﻝﭦ۵ﮔﮔ۰ﻛﭨﭘ

1. **ﮔﺍﮔ؟ﮔﭦﻝﭦ۵ﺅﺟ?*: ﻛﭨﻛﺛﺟﻝ۷ﮒﻟﺑﺗﮒ؛ﮒﺙAPI
2. **ﮔﮔ؛ﻝﭦ۵ﮔ**: ﮔﮔﺅﺟ?200ﺅﺟ?3. **ﮔﭘﻠﺑﻝﭦ۵ﮔ**: 8ﮒ۷ﮒﮒ؟ﮔ
4. **ﮔﮔﺁﻝﭦ۵ﺅﺟ?*: ﻛﺛﺟﻝ۷ﻝﺍﮔﮔﮔﺁﮔ 

---

## ﻛﺗﻙﻠ۹ﮔﭘﮔ ﺅﺟ?
### 9.1 ﮒﻟﺛﻠ۹ﮔﭘ

| ﮒﻟﺛ | ﻠ۹ﮔﭘﮔ ﮒ | ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|---------|---------|
| **ﮔﺍﮔ؟ﻠﻠ** | ﮔﺍﮔ؟ﮒ؟ﮔﺑﺅﺟ?95% | ﮔﺍﮔ؟ﻟﺑ۷ﻠﮔ۲ﺅﺟ?|
| **NLPﮒ۳ﻝ** | ﮔﮔﮒﮔﮒﻝ۰؟ﺅﺟ?80% | ﻛﭦﭦﮒﺓ۴ﮔ ﮔﺏ۷ﻠ۹ﻟﺁ |
| **ﮒ ﮒ­ﻟ؟۰ﻝ؟** | ﮒ ﮒ­ﮔﺍﻠﺅﺟ?ﺅﺟ?| ﮒﻟﺛﮔﭖﻟﺁ |
| **ICﻠ۹ﻟﺁ** | ICﮒﺅﺟﺛ?0.03 | ﻝﭨﻟ؟۰ﮔ۲ﺅﺟ?|

### 9.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘ

| ﮔﮔ  | ﻝ؟ﮔ ﺅﺟ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|--------|---------|
| **ﮔﺍﮔ؟ﻠﻠﮒﭨﭘﻟﺟ** | <5ﮒﻠ | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮒﭨﭘﻟﺟ** | <10ﺅﺟ?| ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﻝﺏﭨﻝﭨﮒﺁﻝ۷ﺅﺟ?* | >99% | ﻝﮔ۶ﻝﭨﻟ؟۰ |

### 9.3 ﻟﺑ۷ﻠﻠ۹ﮔﭘ

| ﮔﮔ  | ﻝ؟ﮔ ﺅﺟ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|--------|---------|
| **ﻛﭨ۲ﻝ ﻟ۵ﻝﺅﺟ?* | >80% | ﮒﮒﮔﭖﻟﺁ |
| **ﮔﮔ۰۲ﮒ؟ﮔﺑﺅﺟ?* | 100% | ﮔﮔ۰۲ﮒ؟۰ﮔ۴ |
| **ﻝﺏﭨﻝﭨﻝ۷ﺏﮒ؟ﺅﺟ?* | >99% | ﮒﮒﮔﭖﻟﺁ |

---

## ﮒﻙﮒ؟ﮔﺛﻟﺓﺁﻝﭦﺟﮒﺝ

### 10.1 Phase 1: ﮔﺍﮔ؟ﮔﭦﮔ۴ﮒ۴ﺅﺙWeek 1-3ﺅﺟ?
**ﻝ؟ﮔ **: ﮒ؟ﮔﮔﺍﮔ؟ﮔﭦﮔ۴ﮒ۴ﮒﮔﺍﮔ؟ﻠﻠ

**ﮒﺏﻠ؟ﻛﭨﭨﮒ۰**:
1. ﮔﺍﻠﭨﮔﺍﮔ؟ﮔﭦﮔ۴ﺅﺟ?2. ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﮔﺍﮔ؟ﮔﭦﮔ۴ﺅﺟ?3. ﮒﮔﮒﺕﻠ۱ﮔﮔﺍﮔ؟ﮔﭦﮔ۴ﮒ۴
4. ﮔﺍﮔ؟ﮒﭦﻟ۰۷ﻝﭨﮔﻟ؟ﺝﻟ؟۰
5. ﮔﺍﮔ؟ﻠﻠﻟﺍﮒﭦ۵ﻝﺏﭨﻝﭨ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻟﺏﮒﺍ3ﻛﺕ۹ﮔﺍﮔ؟ﮔﭦﮔ۴ﮒ۴
- ﮔﺍﮔ؟ﻟﺑ۷ﻠ>95%
- ﮒ؟ﮔﭘﻠﻠﮔ­۲ﮒﺕﺕﻟﺟﻟ۰

---

### 10.2 Phase 2: NLPﮒ۳ﻝﺅﺙWeek 4-5ﺅﺟ?
**ﻝ؟ﮔ **: ﮒ؟ﮔNLPﮒ۳ﻝﮔ۷۰ﮒ

**ﮒﺏﻠ؟ﻛﭨﭨﮒ۰**:
1. GLM-4-Flash APIﻠﮔ
2. ﮔﮔﮒﮔﮔ۷۰ﮒﮒﺙﺅﺟ?3. ﻛﭦﻛﭨﭘﮔﮒﮔ۷۰ﮒﮒﺙﺅﺟ?4. ﮒ؟ﻛﺛﻟﺁﮒ،ﮔ۷۰ﮒﮒﺙﺅﺟ?5. ﮒﻠﮔﺍﮔ؟ﮒﭦﻠﺅﺟ?
**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﮔﮔﮒﮔﮒﻝ۰؟ﺅﺟ?80%
- ﻛﭦﻛﭨﭘﮔﮒﮒ؟ﮔﺑ
- ﮒ؟ﻛﺛﻟﺁﮒ،ﮒﻝ۰؟ﺅﺟ?90%

---

### 10.3 Phase 3: ﮒ ﮒ­ﮔﮒﭨﭦﺅﺙWeek 6-7ﺅﺟ?
**ﻝ؟ﮔ **: ﮒ؟ﮔﮒ ﮒ­ﮔﮒﭨﭦﮒﻠ۹ﺅﺟ?
**ﮒﺏﻠ؟ﻛﭨﭨﮒ۰**:
1. ﮔﺍﻠﭨﮒ ﮒ­ﮔﮒﭨﭦ
2. ﮔﻝﭨ۹ﮒ ﮒ­ﮔﮒﭨﭦ
3. ﻠ۱ﮔﮒ ﮒ­ﮔﮒﭨﭦ
4. ﮒﺏﮔﺏ۷ﮒﭦ۵ﮒ ﮒ­ﮔﺅﺟ?5. ICﻠ۹ﻟﺁ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻟﺏﮒﺍ8ﻛﺕ۹ﮒ ﺅﺟ?- ICﮒﺅﺟﺛ?0.03
- ﮒ ﮒ­ﮔﺏ۷ﮒﮒ؟ﮔ

---

### 10.4 Phase 4: ﮔﭖﻟﺁﻠ۹ﻟﺁﺅﺙWeek 8ﺅﺟ?
**ﻝ؟ﮔ **: ﮒ؟ﮔﻝﺏﭨﻝﭨﮔﭖﻟﺁﮒﻠ۰ﺗﻝ؟ﻠ۹ﺅﺟ?
**ﮒﺏﻠ؟ﻛﭨﭨﮒ۰**:
1. ﮒﮒﮔﭖﻟﺁ
2. ﻠﮔﮔﭖﻟﺁ
3. ﮔ۶ﻟﺛﮔﭖﻟﺁ
4. ﮒﮔﭖﻠ۹ﻟﺁ
5. ﮔﮔ۰۲ﻝﺙﮒ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﮔﮔﮔﭖﻟﺁﻠﻟﺟ
- ﮔﮔ۰۲ﮒ؟ﮔﺑ
- ﻠ۰ﺗﻝ؟ﻛﭦ۳ﻛﭨ

---

## ﻠﮒﺛ

### A. APIﮔﮔ۰۲

ﻟﺁ۵ﻟ۶: [ALTERNATIVE_DATA_API_DOCUMENTATION.md](./ALTERNATIVE_DATA_API_DOCUMENTATION.md)

### B. ﮔﺍﮔ؟ﮒ­ﮒﺕ

ﻟﺁ۵ﻟ۶: [ALTERNATIVE_DATA_DICTIONARY.md](./ALTERNATIVE_DATA_DICTIONARY.md)

### C. ﮔﭖﻟﺁﮔ۴ﮒ

ﻟﺁ۵ﻟ۶: [ALTERNATIVE_DATA_TEST_REPORT.md](./ALTERNATIVE_DATA_TEST_REPORT.md)

---

**ﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ﻝﮔ؛**: v1.0  
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02  
**ﻟﺁﮒ؟۰ﻝﭘﺅﺟﺛ?*: ﺅﺟ?ﮒﺓﺎﮔﺗﺅﺟ? 
**ﻛﺕﻛﺕﮔ­۴ﻟ۰ﺅﺟ?*: ﮒﺙﮒ۶Phase 1ﮒ؟ﮔﺛ
