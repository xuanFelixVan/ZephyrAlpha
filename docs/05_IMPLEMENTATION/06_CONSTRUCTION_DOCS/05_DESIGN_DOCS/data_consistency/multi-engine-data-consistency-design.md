---
module_id: MULTI_ENGINE_DATA_CONSISTENCY_DESIGN
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - ﮒ۳ﮒﺙﮔﮔﺍﮔﻛﺕﻟﺑﮔ۶ﻟﺝﻟ۰ﮔﺗﮔ۰文档
layer: layer_05
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ؟ﮔﺛﮔﮒ
applicable_scope: ﮒ۳ﮒﺙﮔﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻛﺟﻠ?
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---
> **核心职责**: 文档内容说明
**ﻝﮔ؛**: v1.0
**ﮔﺑﮔﺍ**: 2026-04-02
**Layer**: Layer 4 (ﮔ۶ﻟ۰ﮒﺎ? + Layer 1 (ﮔﺍﮔ؟ﮒﺎ?
**ﻛﺙﮒﻝﭦ?*: P1 - ﮒ۳ﮒﺙﮔﮔﭘﮔﮔﺕﮒﺟﮒﭦﻝ۰
---
## 设计目标



### 主要目标



1. **功能完整性**: 确保文档内容完整，满足使用需求

2. **易用性**: 提高文档可读性，便于快速理解

3. **可维护性**: 文档结构清晰，便于后续维护

4. **一致性**: 确保文档格式和风格统一



### 质量目标



- 文档完整性: 100%

- 格式规范性: 100%

- 内容准确性: 100%





## 1. ﻠ؟ﻠ۱ﮒﮔﻛﺕﮔﮔ?



### 1.1 ﮒ۳ﮒﺙﮔﮔﺍﮔ؟ﮒﮔ۴ﻠ؟ﻠ۱?



| ﮒﺙﮔ | ﮔﺍﮔ؟ﮒﮒ۷ﮔﺗﮒﺙ | ﮔﺍﮔ؟ﮔﺙﮒﺙ | ﮒﮔ۴ﻠﺝﻝﺗ |

|------|--------------|----------|----------|

| **vn.py** | MongoDB + SQLite | Pythonﮒﺁﺗﻟﺎ۰ + ﮒﺏﻝﺏﭨﻟ۰?| ﮒ؟ﮔﭘﻛﭦ۳ﮔﮔﺍﮔ؟ﻠﮒ۳۶ﺅﺙﻝﭘﮔﮒﮔﺑﻠ۱ﻝﺗ?|

| **RQAlpha** | HDF5 + ﮒﮒﮒﺁﺗﻟﺎ۰ | ﻝﭨﮔﮒﮔﺍﻝﭨ?| ﮒﮔﭖﮒﭦﮔﺁﮔﺗﻠﮒ۳ﻝﺅﺙﮔﺍﮔ؟ﻝﮔ؛ﮒ۳ |

| **Backtrader** | CSV + ﮒﮒﮒﺁﺗﻟﺎ۰ | Pandas DataFrame | ﮒ۳ﮔﭘﻠﺑﮔ۰ﮔﭘﺅﺙﻟ۹ﮒ؟ﻛﺗﮔﺍﮔ؟ﮔﭦ |

| **QMT** | ﮒﺕﮒﮔﺍﮔ؟ﮒﭦ?+ ﮔ؛ﮒﺍﻝﺙﮒ | ﻛﺕﮔﻛﭦﻟﺟﮒﭘﮔﺙﮒﺙ?| ﮒﺕﮒﮔ۴ﮒ۲ﻠﮒﭘﺅﺙﻠﮔ۷۰ﮔﻝﮒﮔ?|

| **backtesting.py** | Pandas DataFrame | ﻟﺛﭨﻠﻝﭦ۶ﮒﮒﻝﭨﮔ?| ﮒﺟ،ﻠﮒﮔﭖﺅﺙﮔﮔﻛﺗﮒﮒﮒ۷ |



### 1.2 ﮒﺏﻠ؟ﮔﺍﮔ؟ﮒﮔ۴ﻠﮔﺎ?



#### 1.2.1 ﮔﻛﭨﮔﺍﮔ؟ﮒﮔ۴

- **ﮒﮔ۴ﮒ؟ﻛﺛ**: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﻙﮔﻛﭨﮔﺍﻠﻙﮔﮔ؛ﻛﭨﺓﻙﮔﭖ؟ﮒ۷ﻝﻛﭦ?

- **ﮒﮔ۴ﮔﭘﮔﭦ**: ﻛﭦ۳ﮔﮔ۶ﻟ۰ﮒﮒ؟ﮔﭘﮒﮔ۴ﻙﮔﺁﮔ۴ﮔﭘﻝﮒﮔﺗﻠﮒﮔ۴

- **ﻛﺕﻟﺑﮔ۶ﻟ۵ﮔﺎ?*: ﮒﺙﭦﻛﺕﻟﺑﮔ۶ﺅﺙﮔﻛﭨﮔﺍﻠﮒﺟﻠ۰ﭨﻝﺎﺝﻝ۰؟ﻛﺕﻟﺑﺅﺙ



#### 1.2.2 ﻟﭖﻠﮔﺍﮔ؟ﮒﮔ۴

- **ﮒﮔ۴ﮒ؟ﻛﺛ**: ﮒﺁﻝ۷ﻟﭖﻠﻙﮒﭨﻝﭨﻟﭖﻠﻙﮔﭨﻟﭖﻛﭦ۶ﻙﮒﺛﮔ۴ﻝﻛﭦ?

- **ﮒﮔ۴ﮔﭘﮔﭦ**: ﻛﭦ۳ﮔﮒﮒﮒ؟ﮔﭘﮒﮔ۴ﻙﻟﭖﻠﮒﻟﺛ؛ﮔﭘﮒﮔ۴

- **ﻛﺕﻟﺑﮔ۶ﻟ۵ﮔﺎ?*: ﮒﺙﭦﻛﺕﻟﺑﮔ۶ﺅﺙﻟﭖﻠﮔﭨﻠ۱ﮒﺟﻠ۰ﭨﻝﺎﺝﻝ۰؟ﻛﺕﻟﺑﺅﺙ



#### 1.2.3 ﻟ؟۱ﮒﻝﭘﮔﮒﮔ?

- **ﮒﮔ۴ﮒ؟ﻛﺛ**: ﻟ؟۱ﮒIDﻙﻝﭘﮔﺅﺙﮒﺝﮔﻛﭦ?ﻠ۷ﮒﮔﻛﭦ۳/ﮒ؟ﮒ۷ﮔﻛﭦ۳/ﮒﺓﺎﮒﮔﭘﺅﺙﻙﮔﻛﭦ۳ﮔﺍﻠﻙﮔﻛﭦ۳ﮒﻛﭨ?

- **ﮒﮔ۴ﮔﭘﮔﭦ**: ﻟ؟۱ﮒﻝﭘﮔﮒﮔﺑﮔﭘﮒ؟ﮔﭘﮒﮔ۴

- **ﻛﺕﻟﺑﮔ۶ﻟ۵ﮔﺎ?*: ﮔﻝﭨﻛﺕﻟﺑﮔ۶ﺅﺙﮒﻟ؟ﺕﻝﮔﮒﭨﭘﻟﺟﺅﺙ?



### 1.3 ﮔﮔﺁﮔﮔﻟﺁﻝﭦ?



| ﮔﮔ | ﻠ۲ﻠ۸ﻝﻝﭦ۶ | ﮒﺛﺎﮒ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |

|------|----------|------|----------|

| **ﻟﺓ۷ﮒﺙﮔﻛﭦﮒ۰ﮒﮒﮔ?* | P0ﺅﺙﻠ،ﻠ۲ﻠ۸ﺅﺙ?| ﮔﺍﮔ؟ﻛﺕﻛﺕﻟﺑﮒﺁﺙﻟﺑﻛﭦ۳ﮔﻠﻟﺁ?| Sagaﮔ۷۰ﮒﺙ + ﻟ۰۴ﮒﺟﻛﭦﮒ۰ |

| **ﻝﺛﻝﭨﮒﮒﭦﮒ؟ﺗﮒﺟ** | P1ﺅﺙﻛﺕﻠ۲ﻠ۸ﺅﺙ?| ﮒﺙﮔﻠﺑﻠﻛﺟ۰ﻛﺕﮔ | ﻠﻟﺁﮔﭦﮒﭘ + ﮔ؛ﮒﺍﻝﺙﮒ |

| **ﮔ۶ﻟﺛﮒﺙﻠ** | P1ﺅﺙﻛﺕﻠ۲ﻠ۸ﺅﺙ?| ﮒﮔ۴ﮒﭨﭘﻟﺟﮒﺛﺎﮒﻛﭦ۳ﮔ | ﮒﺙﮔ۴ﮒ۳ﻝ + ﮔﺗﻠﮒﮒﺗﭘ |

| **ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ۳ﮔﮔ?* | P1ﺅﺙﻛﺕﻠ۲ﻠ۸ﺅﺙ?| ﮒﮔﭨﻠﭨﻟﺝﻠﻟﺁﺁ | ﻝﭘﮔﮔﭦ + ﮒﺗﻝﻟ؟ﺝﻟ؟۰ |

| **ﮔﺍﮔ؟ﮔﺙﮒﺙﻟﺛ؛ﮔ۱** | P2ﺅﺙﻛﺛﻠ۲ﻠ۸ﺅﺙ?| ﮔﺙﮒﺙﻛﺕﻛﺕﻟ?| ﻝﭨﻛﺕﮔﺍﮔ؟ﮔ۷۰ﮒ + ﻠﻠﮒ?|



---



## 2. ﮔﮔﺁﮔﺗﮔ۰ﻟﺁﻛﺙ?



### 2.1 ﮒ۳ﻠﮔﺗﮔ۰ﮒﺁﺗﮔﺁ?



| ﻝﭨﺑﮒﭦ۵ | **Sagaﮔ۷۰ﮒﺙ** (ﮔ۷ﻟ) | **ﻛﺕ۳ﻠﭘﮔ؟ﭖﮔﻛﭦ?(2PC)** | **ﻛﭦﻛﭨﭘﮔﭦﺁﮔﭦ (Event Sourcing)** |

|------|---------------------|---------------------|-----------------------------|

| **ﻛﺕﻟﺑﮔ۶ﮔ۷۰ﮒ?* | ﮔﻝﭨﻛﺕﻟﺑﮔ?ﻗ?ﮒﺙﭦﻛﺕﻟﺑﮔ?| ﮒﺙﭦﻛﺕﻟﺑﮔ?| ﮔﻝﭨﻛﺕﻟﺑﮔ?|

| **ﮔ۶ﻟﺛ** | ﻠ،ﺅﺙﮒﺙﮔ۴ﮔ۶ﻟ۰ﺅﺙ?| ﻛﺛﺅﺙﮒﮔ۴ﻠﭨﮒ۰ﺅﺙ?| ﻛﺕﺅﺙﻛﭦﻛﭨﭘﻠﮔﺝﺅﺙ?|

| **ﮒﺁﻝ۷ﮔ?* | ﻠ،ﺅﺙﮔﮒﻝﺗﮔﻠﺅﺙ | ﻛﺛﺅﺙﮒﻟﺍﻟﮒﻝﺗﺅﺙ | ﻠ،ﺅﺙﻛﭦﻛﭨﭘﮒﮒ۷ﻠ،ﮒﺁﻝ۷ﺅﺙ |

| **ﮒ۳ﮔﮒﭦ?* | ﻛﺕﺅﺙﻠﻟ۰۴ﮒﺟﻠﭨﻟﺝﺅﺙ?| ﻠ،ﺅﺙﮒﻟﺍﻟﮒ۳ﮔﺅﺙ | ﻠ،ﺅﺙﻛﭦﻛﭨﭘﮔ۷۰ﮒﻟ؟ﺝﻟ؟۰ﺅﺙ?|

| **ﮔ۸ﮒﺎﮔ?* | ﻠ،ﺅﺙﮔﺍﮒ۱ﮒﺙﮔﮔﺅﺙ | ﻛﺛﺅﺙﮒﻟ؟؟ﻠﮒﭘﺅﺙ?| ﻛﺕﺅﺙﻛﭦﻛﭨﭘﮒﮒ۷ﮔ۸ﮒﺎﺅﺙ?|

| **ﻠﮒﮒﭦﮔﺁ** | ﻠﺟﻛﭦﮒ۰ﻙﻟﺓ۷ﻝﺏﭨﻝﭨ | ﻝﻛﭦﮒ۰ﻙﮒﺙﭦﻛﺕﻟ?| ﮒ؟۰ﻟ؟۰ﻟﺟﺛﻟﺕ۹ﻙﻝﭘﮔﻠﮒﭨ?|

| **ﮒ؟ﻝﺍﮔﮔ؛** | ﻛﺕﺅﺙ3-5ﮒ۳۸ﺅﺙ | ﻠ،ﺅﺙ5-7ﮒ۳۸ﺅﺙ | ﻠ،ﺅﺙ7-10ﮒ۳۸ﺅﺙ |



### 2.2 ﮔ۷ﻟﮔﺗﮔ۰ﺅﺙSagaﮔ۷۰ﮒﺙ + PostgreSQL + Redis



#### 2.2.1 ﮔﭘﮔﻛﺙﮒﺟ

1. **ﮔﻝﭨﻛﺕﻟﺑﮔ۶ﮒﺁﮒﻝﭦ۶ﮒﺙﭦﻛﺕﻟﺑﮔ?*: ﻠﻟﺟﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ؟ﻝﺍﻛﺕﮒ۰ﮒﺎﻠ۱ﻝﮒﺙﭦﻛﺕﻟﺑﮔ?

2. **ﮔﮒﻝﺗﮔﻠ?*: ﮔﻛﺕﮒﺟﮒﻟﺍﻟﺅﺙﮔﺁﻛﺕ۹ﮒﺙﮔﻝ؛ﻝ،ﮒ۳ﻝﻟ۹ﮒﺓﺎﻝﻛﭦﮒ?

3. **ﻠ،ﮔ۶ﻟﺛ**: ﮒﺙﮔ۴ﮔ۶ﻟ۰ﺅﺙﮔﺁﮔﮔﺗﻠﮔﻛﺛﺅﺙﮒﭨﭘﻟﺟ<50ms

4. **ﮔﻛﭦﮔ۸ﮒﺎ**: ﮔﺍﮒ۱ﮒﺙﮔﮒ۹ﻠﮒ؟ﻝﺍSagaﮒﻛﺕﮔ۴ﮒ۲

5. **ﮒ؟ﺗﻠﻟﺛﮒﮒﺙ?*: ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮔﭦﮒﭘﻛﺟﻟﺁﮒﺙﮒﺕﺕﮔﭘﮔﺍﮔ؟ﮒ؟ﮒ?



#### 2.2.2 ﮔﮔﺁﮔﻠﮔ۸

- **ﻛﭦﮒ۰ﮒﻟﺍ**: ﻟ۹ﮒ؟ﻛﺗSagaﮒﻟﺍﮒ۷ﺅﺙPythonﺅﺙ?

- **ﻝﭘﮔﮒﮒ?*: PostgreSQLﺅﺙﮒﺙﭦﻛﺕﻟﺑﮔ۶ﻛﺟﻟﺁﺅﺙ

- **ﻛﭦﻛﭨﭘﻠ۸ﺎﮒ۷**: Redis Streamsﺅﺙﻛﺛﮒﭨﭘﻟﺟﮔﭘﮔﺁﺅﺙ?

- **ﻝﮔ۶ﮒﻟ۵**: Prometheus + Grafanaﺅﺙﻛﭦﮒ۰ﮒ۴ﮒﭦﺓﻝﮔ۶ﺅﺙ



---



## 3. ﮔﭘﮔﻟ؟ﺝﻟ؟۰



### 3.1 ﮔﺑﻛﺛﮔﭘﮔﮒ?



```

ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?

ﻗ?                  ﮒ۳ﮒﺙﮔﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﮔﭘﮔ?                       ﻗ?

ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?

ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?        ﻗ?

ﻗ? ﻗ?  vn.py     ﻗ? ﻗ? RQAlpha    ﻗ? ﻗ?Backtrader  ﻗ?        ﻗ?

ﻗ? ﻗ? ﮒﺙﮔﻠﻠﮒ?ﻗ? ﻗ? ﮒﺙﮔﻠﻠﮒ? ﻗ? ﻗ? ﮒﺙﮔﻠﻠﮒ? ﻗ?        ﻗ?

ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?        ﻗ?

ﻗ?        ﻗ?               ﻗ?               ﻗ?               ﻗ?

ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﺑﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﺑﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﺑﻗﻗﻗﻗﻗﻗﻗ?        ﻗ?

ﻗ? ﻗ? Sagaﮒﻛﺕﮔ? ﻗ? ﻗ? Sagaﮒﻛﺕﮔ? ﻗ? ﻗ? Sagaﮒﻛﺕﮔ? ﻗ?        ﻗ?

ﻗ? ﻗ? (Participant)ﻗ? ﻗ? (Participant)ﻗ? ﻗ? (Participant)ﻗ?        ﻗ?

ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?        ﻗ?

ﻗ?        ﻗ?               ﻗ?               ﻗ?               ﻗ?

ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?

ﻗ?        ﻗ?               ﻗ?               ﻗ?               ﻗ?

ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?        ﻗ?

ﻗ? ﻗ?Redis Streamsﻗ? ﻗ?PostgreSQL  ﻗ? ﻗ?  Sagaﮒﻟﺍﮒ?ﻗ?        ﻗ?

ﻗ? ﻗ? (ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟ)   ﻗ? ﻗ?(ﻝﭘﮔﮒﮒ?  ﻗ? ﻗ?(Coordinator)ﻗ?        ﻗ?

ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?        ﻗ?

ﻗ?        ﻗ?               ﻗ?               ﻗ?               ﻗ?

ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?        ﻗ?

ﻗ? ﻗ?            ﻝﮔ۶ﻛﺕﮒﻟ۵ﻝﺏﭨﻝﭨ?                      ﻗ?        ﻗ?

ﻗ? ﻗ?        (Prometheus + Grafana)               ﻗ?        ﻗ?

ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?        ﻗ?

ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?

```



### 3.2 ﮔﺍﮔ؟ﮔﭖﻟ؟ﺝﻟ؟?



#### 3.2.1 ﮔ۲ﮒﺕﺕﮔ۶ﻟ۰ﮔﭖﻝ۷ﺅﺙﮔﮒﺅﺙ

1. **ﻛﭦﮒ۰ﮒﺁﮒ۷**: ﮒﻟﺍﮒ۷ﮒﮒﭨﭦSagaﻛﭦﮒ۰ﺅﺙﮒﻠﮒﺁﻛﺕID

2. **ﻠ۱ﮔ۲ﮔ۴ﻠﭘﮔ؟?*: ﮒﮒﺙﮔﮔ۲ﮔ۴ﻟﭖﮔﭦﮒﺁﻝ۷ﮔ۶ﺅﺙﻟﭖﻠﻙﮔﻛﭨﺅﺙ

3. **ﮔ۶ﻟ۰ﻠﭘﮔ؟ﭖ**: ﻠ۰ﭦﮒﭦﮔ۶ﻟ۰ﮒﮒﺙﮔﻝﮔ؛ﮒﺍﻛﭦﮒ۰

4. **ﻝ۰؟ﻟ؟۳ﻠﭘﮔ؟ﭖ**: ﮔﮔﮒﺙﮔﮔ۶ﻟ۰ﮔﮒﮒﻝ۰؟ﻟ؟۳ﻛﭦﮒ۰

5. **ﮒ؟ﮔﻠﻝ۴**: ﮒﮒﺕﻛﭦﮒ۰ﮒ؟ﮔﻛﭦﻛﭨﭘﺅﺙﮔﺑﮔﺍﮒ۷ﮒﺎﻝﭘﮔ?



#### 3.2.2 ﻟ۰۴ﮒﺟﮔ۶ﻟ۰ﮔﭖﻝ۷ﺅﺙﮒ۳ﺎﻟﺑ۴ﺅﺙ

1. **ﮒ۳ﺎﻟﺑ۴ﮔ۲ﮔﭖ?*: ﻛﭨﭨﻛﺛﮒﺙﮔﮔ؛ﮒﺍﻛﭦﮒ۰ﮒ۳ﺎﻟﺑ۴

2. **ﮒﮔ۱ﮔ۶ﻟ۰**: ﮒﻟﺍﮒ۷ﮒﮔ۱ﮒﻝﭨﮒﺙﮔﮔ۶ﻟ۰?

3. **ﻟ۰۴ﮒﺟﻟ۶۵ﮒ**: ﮔﻠﮒﭦﻟ۶۵ﮒﮒﺓﺎﮔ۶ﻟ۰ﮒﺙﮔﻝﻟ۰۴ﮒﺟﻛﭦﮒ۰

4. **ﻝﭘﮔﮒﮔﭨ?*: ﮒﮒﺙﮔﮒﮔﭨﮒﺍﻛﭦﮒ۰ﮒﻝﭘﮔ?

5. **ﮒ۳ﺎﻟﺑ۴ﻠﻝ۴**: ﮒﮒﺕﻛﭦﮒ۰ﮒ۳ﺎﻟﺑ۴ﻛﭦﻛﭨﭘﺅﺙﻟ؟ﺍﮒﺛﻠﻟﺁﺁﮔ۴ﮒﺟ?



### 3.3 ﮔﺕﮒﺟﻝﭨﻛﭨﭘﻟ؟ﺝﻟ؟۰



#### 3.3.1 Sagaﮒﻟﺍﮒ?(SagaCoordinator)

```python

class SagaCoordinator:

    """Sagaﮔ۷۰ﮒﺙﮒﻟﺍﮒ?""

    

    def __init__(self, postgres_client, redis_client):

        self.pg = postgres_client

        self.redis = redis_client

        self.participants = {}  # ﮒﺙﮔID -> ﮒﻛﺕﮔﺗﮒ؟۱ﮔﺓﻝ،ﺁ

        

    async def execute_transaction(self, transaction: SagaTransaction) -> SagaResult:

        """ﮔ۶ﻟ۰Sagaﻛﭦﮒ۰"""

        # 1. ﮒﮒﭨﭦﻛﭦﮒ۰ﻟ؟ﺍﮒﺛ

        tx_id = await self._create_transaction_record(transaction)

        

        # 2. ﮔ۶ﻟ۰ﻠ۱ﮔ۲ﮔ?

        precheck_results = await self._execute_precheck(tx_id, transaction)

        if not all(r.success for r in precheck_results):

            return SagaResult.failed("ﻠ۱ﮔ۲ﮔ۴ﮒ۳ﺎﻟﺑ?, precheck_results)

            

        # 3. ﻠ۰ﭦﮒﭦﮔ۶ﻟ۰ﮔ؛ﮒﺍﻛﭦﮒ۰

        executed_participants = []

        for participant_id, command in transaction.commands.items():

            try:

                result = await self._execute_local_transaction(

                    participant_id, command, tx_id

                )

                if not result.success:

                    # ﻟ۶۵ﮒﻟ۰۴ﮒﺟ

                    await self._trigger_compensation(

                        tx_id, executed_participants

                    )

                    return SagaResult.failed(f"ﮒﻛﺕﻟ{participant_id}ﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴", result)

                    

                executed_participants.append(participant_id)

                

            except Exception as e:

                await self._trigger_compensation(tx_id, executed_participants)

                return SagaResult.failed(f"ﮔ۶ﻟ۰ﮒﺙﮒﺕﺕ: {str(e)}")

                

        # 4. ﻝ۰؟ﻟ؟۳ﻛﭦﮒ۰ﮒ؟ﮔ

        await self._confirm_transaction(tx_id)

        return SagaResult.success(tx_id)

        

    async def _trigger_compensation(self, tx_id: str, participants: List[str]):

        """ﻟ۶۵ﮒﻟ۰۴ﮒﺟﻛﭦﮒ۰"""

        # ﮔﻠﮒﭦﻟ۶۵ﮒﻟ۰۴ﮒﺟ

        for participant_id in reversed(participants):

            await self._execute_compensation(participant_id, tx_id)

```



#### 3.3.2 Sagaﮒﻛﺕﮔ?(SagaParticipant)

```python

class SagaParticipant:

    """Sagaﮔ۷۰ﮒﺙﮒﻛﺕﮔﺗﺅﺙﮒﺙﮔﻠﻠﮒ۷ﻠﮔﺅﺙ"""

    

    def __init__(self, engine_adapter: BaseEngineAdapter):

        self.engine = engine_adapter

        self.local_tx_log = {}  # ﮔ؛ﮒﺍﻛﭦﮒ۰ﮔ۴ﮒﺟ

        

    async def execute_local_transaction(

        self, command: LocalCommand, tx_id: str

    ) -> ParticipantResult:

        """ﮔ۶ﻟ۰ﮔ؛ﮒﺍﻛﭦﮒ۰"""

        # ﻟ؟ﺍﮒﺛﻛﭦﮒ۰ﮒﺙﮒ۶?

        await self._log_transaction_start(tx_id, command)

        

        try:

            # ﮔ۶ﻟ۰ﮒﺙﮔﻝﺗﮒ؟ﮔﻛﺛ

            if command.type == "position_transfer":

                result = await self._transfer_position(command)

            elif command.type == "capital_adjustment":

                result = await self._adjust_capital(command)

            elif command.type == "order_sync":

                result = await self._sync_order(command)

            else:

                raise ValueError(f"ﮔ۹ﻝ۴ﮒﺛﻛﭨ۳ﻝﺎﭨﮒ: {command.type}")

                

            # ﻟ؟ﺍﮒﺛﻛﭦﮒ۰ﮔﮒ

            await self._log_transaction_success(tx_id, result)

            return ParticipantResult.success(tx_id, result.data)

            

        except Exception as e:

            # ﻟ؟ﺍﮒﺛﻛﭦﮒ۰ﮒ۳ﺎﻟﺑ۴

            await self._log_transaction_failure(tx_id, str(e))

            return ParticipantResult.failed(tx_id, str(e))

            

    async def compensate_transaction(self, tx_id: str) -> CompensationResult:

        """ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﺅﺙﮒﮔﭨﺅﺙ"""

        tx_log = await self._get_transaction_log(tx_id)

        if not tx_log:

return CompensationResult.skipped(f"ﻛﭦﮒ۰{tx_id}ﻛﺕﮒﮒ?)

            

        try:

            # ﮔ۶ﻟ۰ﻟ۰۴ﮒﺟﻠﭨﻟﺝ

            if tx_log.command.type == "position_transfer":

                # ﮒﮒﻟﺛ؛ﻝ۶ﭨﮔﻛﭨ

                await self._reverse_position_transfer(tx_log)

            elif tx_log.command.type == "capital_adjustment":

                # ﮒﮒﻟﺍﮔﺑﻟﭖﻠ

                await self._reverse_capital_adjustment(tx_log)

            elif tx_log.command.type == "order_sync":

# ﻟ؟۱ﮒﮒﮔ۴ﮔﻠﻟ۰۴ﮒﺟﺅﺙﮒ۹ﻟﺁﭨﺅﺙ

                pass

                

            await self._log_compensation_success(tx_id)

            return CompensationResult.success(tx_id)

            

        except Exception as e:

            await self._log_compensation_failure(tx_id, str(e))

            return CompensationResult.failed(tx_id, str(e))

```



---



## 4. ﮔﺍﮔ؟ﮔ۷۰ﮒﻟ؟ﺝﻟ؟۰



### 4.1 PostgreSQLﻟ۰۷ﻝﭨﮔ?



#### 4.1.1 saga_transactions (Sagaﻛﭦﮒ۰ﻟ۰?

```sql

CREATE TABLE saga_transactions (

    tx_id VARCHAR(64) PRIMARY KEY,

    transaction_type VARCHAR(32) NOT NULL,  -- 'position_sync', 'capital_sync', 'order_sync'

    status VARCHAR(16) NOT NULL,           -- 'pending', 'prechecking', 'executing', 'compensating', 'completed', 'failed'

    initiator_engine VARCHAR(32) NOT NULL, -- ﮒﻟﭖﺓﮒﺙﮔ

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    metadata JSONB                         -- ﻛﭦﮒ۰ﮒﮔﺍﮔ?

);



CREATE INDEX idx_saga_transactions_status ON saga_transactions(status);

CREATE INDEX idx_saga_transactions_created ON saga_transactions(created_at);

```



#### 4.1.2 saga_participants (ﮒﻛﺕﻟﻝﭘﮔﻟ۰۷)

```sql

CREATE TABLE saga_participants (

    id SERIAL PRIMARY KEY,

    tx_id VARCHAR(64) NOT NULL REFERENCES saga_transactions(tx_id) ON DELETE CASCADE,

engine_id VARCHAR(32) NOT NULL,        -- ﮒﺙﮔﮔﻟﺁ

    participant_status VARCHAR(16) NOT NULL, -- 'pending', 'precheck_passed', 'executed', 'compensated', 'failed'

    command_type VARCHAR(32) NOT NULL,     -- ﮒﺛﻛﭨ۳ﻝﺎﭨﮒ

    command_data JSONB NOT NULL,           -- ﮒﺛﻛﭨ۳ﮔﺍﮔ؟

    result_data JSONB,                     -- ﮔ۶ﻟ۰ﻝﭨﮔ

    error_message TEXT,                    -- ﻠﻟﺁﺁﻛﺟ۰ﮔﺁ

    executed_at TIMESTAMP,

    compensated_at TIMESTAMP,

    

    UNIQUE(tx_id, engine_id)

);



CREATE INDEX idx_saga_participants_tx_id ON saga_participants(tx_id);

CREATE INDEX idx_saga_participants_engine ON saga_participants(engine_id);

```



#### 4.1.3 consistency_snapshots (ﻛﺕﻟﺑﮔ۶ﮒﺟ،ﻝ۶ﻟ۰۷)

```sql

CREATE TABLE consistency_snapshots (

    snapshot_id VARCHAR(64) PRIMARY KEY,

    snapshot_type VARCHAR(32) NOT NULL,    -- 'daily', 'transaction', 'emergency'

    engines JSONB NOT NULL,                -- ﮒﻛﺕﮒﺙﮔﮒﻟ۰۷

    status VARCHAR(16) NOT NULL,           -- 'collecting', 'verifying', 'consistent', 'inconsistent'

    discrepancies JSONB,                   -- ﻛﺕﻛﺕﻟﺑﻠ۰ﺗﻟﺁ۵ﮔ

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    verified_at TIMESTAMP,

    

    CHECK (status IN ('collecting', 'verifying', 'consistent', 'inconsistent'))

);



CREATE INDEX idx_consistency_snapshots_type ON consistency_snapshots(snapshot_type);

CREATE INDEX idx_consistency_snapshots_status ON consistency_snapshots(status);

```



### 4.2 Redis Streamsﻟ؟ﺝﻟ؟۰



#### 4.2.1 ﻛﭦﻛﭨﭘﮔﭖﮒ؟ﻛﺗ?

```python

# Redis Streamsﻠ؟ﮒ؟ﻛﺗ?

REDIS_STREAMS = {

    "saga_commands": "stream:saga:commands",      # Sagaﮒﺛﻛﭨ۳ﮔﭖ?

    "saga_events": "stream:saga:events",          # Sagaﻛﭦﻛﭨﭘﮔﭖ?

    "compensation_commands": "stream:compensation:commands",  # ﻟ۰۴ﮒﺟﮒﺛﻛﭨ۳ﮔﭖ?

    "consistency_checks": "stream:consistency:checks",        # ﻛﺕﻟﺑﮔ۶ﮔ۲ﮔ۴ﮔﭖ

}



# ﻛﭦﻛﭨﭘﻝﺎﭨﮒ

EVENT_TYPES = {

    "TRANSACTION_STARTED": "saga.transaction.started",

    "TRANSACTION_COMPLETED": "saga.transaction.completed",

    "TRANSACTION_FAILED": "saga.transaction.failed",

    "PARTICIPANT_EXECUTED": "saga.participant.executed",

    "PARTICIPANT_COMPENSATED": "saga.participant.compensated",

    "CONSISTENCY_ALERT": "consistency.alert",

}

```



#### 4.2.2 ﻛﭦﻛﭨﭘﮔﺙﮒﺙ

```json

{

  "event_id": "evt_1234567890",

  "event_type": "saga.transaction.started",

  "timestamp": "2026-04-02T10:30:00Z",

  "tx_id": "tx_abcdef123456",

  "data": {

    "transaction_type": "position_sync",

    "initiator": "vn.py",

    "participants": ["rqalpha", "backtrader", "qmt"],

    "metadata": {

      "strategy_id": "strategy_001",

      "symbol": "000001.SZ",

      "quantity": 1000

    }

  }

}

```



---



## 5. Sagaﮔ۷۰ﮒﺙﻟﺁ۵ﻝﭨﮒ؟ﻝﺍ



### 5.1 ﻛﭦﮒ۰ﻝﭘﮔﮔﭦ



```

                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?

                    ﻗ?  pending   ﻗ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?

                           ﻗ?ﮒﺙﮒ۶ﻛﭦﮒ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?

                    ﻗ?prechecking ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                 ﻗ?

                           ﻗ?ﻠ۱ﮔ۲ﮔ۴ﻠﻟﺟ               ﻗ?ﻠ۱ﮔ۲ﮔ۴ﮒ۳ﺎﻟﺑ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?           ﻗﻗﻗﻗﻗﻗﻗﺑﻗﻗﻗﻗﻗﻗﻗ?

                    ﻗ?executing   ﻗ?           ﻗ?  failed   ﻗ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?           ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?

                           ﻗ?ﮔ۶ﻟ۰ﮒﻛﺕﮔ?                 ﻗ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?                 ﻗ?

                    ﻗ?executing   ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?  ﻗ?

                    ﻗ?(ﮒﻛﺕﮔ?)    ﻗ?             ﻗ?  ﻗ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?             ﻗ?  ﻗ?

                           ﻗ?ﮔ۶ﻟ۰ﮒﻛﺕﮔﺗN         ﻗ?  ﻗ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?             ﻗ?  ﻗ?

                    ﻗ?completing  ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?  ﻗ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                 ﻗ?

                           ﻗ?ﻝ۰؟ﻟ؟۳ﮒ؟ﮔ                ﻗ?ﻛﭨﭨﻛﺛﮒﻛﺕﮔﺗﮒ۳ﺎﻟﺑ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?           ﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?

                    ﻗ? completed  ﻗ?           ﻗcompensatingﻗ?

                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?           ﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?

                                                     ﻗ?ﻟ۰۴ﮒﺟﮒﻛﺕﮔﺗN

                                              ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?

                                              ﻗcompensating ﻗ?

                                              ﻗ?(ﮒﻛﺕﮔﺗN-1) ﻗ?

                                              ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?

                                                     ﻗ?ﻟ۰۴ﮒﺟﮒﻛﺕﮔ?

                                              ﻗﻗﻗﻗﻗﻗﻗﻗﺙﻗﻗﻗﻗﻗﻗﻗ?

                                              ﻗ?  failed    ﻗ?

                                              ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?

```



### 5.2 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟ؟ﺝﻟ؟۰ﮒﮒ



#### 5.2.1 ﮒﺗﻝﮔ۶ﻟ؟ﺝﻟ؟?

- **ﻟ۰۴ﮒﺟﮒﺛﻛﭨ۳ﮒﺗﻝ**: ﮒﻛﺕﻛﭦﮒ۰ﻝﻟ۰۴ﮒﺟﮒﺛﻛﭨ۳ﮒﺁﻠﮒ۳ﮔ۶ﻟ۰ﺅﺙﻝﭨﮔﻛﺕﻟ?

- **ﻝﭘﮔﮔ۲ﮔ?*: ﻟ۰۴ﮒﺟﮒﮔ۲ﮔ۴ﮒﺛﮒﻝﭘﮔﺅﺙﻠﺟﮒﻠﮒ۳ﻟ۰۴ﮒﺟ

- **ﻝﭨﮔﻟ؟ﺍﮒﺛ**: ﻟ؟ﺍﮒﺛﻟ۰۴ﮒﺟﻝﭨﮔﺅﺙﮒﻝﭨﻟ۰۴ﮒﺟﻝﺑﮔ۴ﻟﺟﮒﮔﮒ?



#### 5.2.2 ﮒﺁﻠﻟﺁﮔ۶ﻟ؟ﺝﻟ؟?

- **ﮔﮒ۳۶ﻠﻟﺁﮔ؛۰ﮔ?*: ﮔﺁﻛﺕ۹ﻟ۰۴ﮒﺟﮔﻛﺛﮔﮒ۳ﻠﻟﺁ?ﮔ؛?

- **ﻠﻠﺟﻝﻝ?*: ﮔﮔﺍﻠﻠﺟﻠﻟﺁﺅﺙ1s, 2s, 4sﺅﺙ?

- **ﻟﭘﮔﭘﻟ؟ﺝﻝﺛ؟**: ﮒﮔ؛۰ﻟ۰۴ﮒﺟﮔﻛﺛﮔﻠ?0ﻝ۶?



#### 5.2.3 ﻛﺕﮒ۰ﻟﺁﻛﺗﻟ۰۴ﮒﺟ

- **ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟ**: ﮒﮒﻟﺛ؛ﻝ۶ﭨﻝﺕﮒﮔﺍﻠﻝﮔﻛﭨ?

- **ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟ**: ﮒﮒﻟﺍﮔﺑﻝﺕﮒﻠﻠ۱ﻝﻟﭖﻠ?

- **ﻟ؟۱ﮒﮒﮔ۴ﻟ۰۴ﮒﺟ**: ﮔﻠﻟ۰۴ﮒﺟﺅﺙﮒ۹ﻟﺁﭨﮔﻛﺛﺅﺙ



### 5.3 ﮒﺏﻠ؟ﻝ؟ﮔﺏﮒ؟ﻝﺍ



#### 5.3.1 ﻠ۱ﮔ۲ﮔ۴ﻝ؟ﮔﺏ?

```python

async def precheck_position_transfer(

    self, tx_id: str, transfer: PositionTransfer

) -> PrecheckResult:

    """ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻠ۱ﮔ۲ﮔ?""

    checks = []

    

    # ﮔ۲ﮔ۴ﮔﭦﮒﺙﮔﮔﻛﭨﮔﺁﮒ۵ﻟﭘﺏﮒ۳

    source_position = await self._get_position(

        transfer.source_engine, transfer.symbol

    )

    if source_position.available < transfer.quantity:

        checks.append(PrecheckItem(

            type="position_sufficiency",

            passed=False,

            message=f"ﮔﭦﮒﺙﮔﮔﻛﭨﻛﺕﻟﭘ? {source_position.available} < {transfer.quantity}"

        ))

    else:

        checks.append(PrecheckItem(

            type="position_sufficiency",

            passed=True,

            message="ﮔﻛﭨﮒﻟﭘﺏ"

        ))

    

# ﮔ۲ﮔ۴ﻝ؟ﮔﮒﺙﮔﮔﺁﮒ۵ﮔﺁﮔﻟﺁ۴ﻟ۰ﻝ۴۷

    target_supported = await self._check_symbol_support(

        transfer.target_engine, transfer.symbol

    )

    checks.append(PrecheckItem(

        type="symbol_support",

        passed=target_supported,

message="ﻝ؟ﮔﮒﺙﮔﮔﺁﮔﻟﺁ۴ﻟ۰ﻝ۴? if target_supported else "ﻝ؟ﮔﮒﺙﮔﻛﺕﮔﺁﮔﻟﺁ۴ﻟ۰ﻝ۴۷"

    ))

    

    # ﮔ۲ﮔ۴ﮔﺁﮒ۵ﮒ۷ﻛﭦ۳ﮔﮔﭘﻠﺑﺅﺙﻠﺟﮒﻠﻛﭦ۳ﮔﮔﭘﻠﺑﻟﺛ؛ﻝ۶ﭨﺅﺙ?

    in_trading_hours = await self._is_in_trading_hours()

    checks.append(PrecheckItem(

        type="trading_hours",

        passed=in_trading_hours,

        message="ﮒ۷ﻛﭦ۳ﮔﮔﭘﻠﺑﮒ" if in_trading_hours else "ﻠﻛﭦ۳ﮔﮔﭘﻠ?

    ))

    

    all_passed = all(c.passed for c in checks)

    return PrecheckResult(

        tx_id=tx_id,

        passed=all_passed,

        checks=checks,

        timestamp=datetime.now()

    )

```



#### 5.3.2 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟﺍﮒﭦ۵ﻝ؟ﮔﺏ

```python

async def schedule_compensation(

    self, tx_id: str, failed_participant_id: str, executed_participants: List[str]

) -> CompensationSchedule:

    """ﻟﺍﮒﭦ۵ﻟ۰۴ﮒﺟﻛﭦﮒ۰"""

    # ﻝ۰؟ﮒ؟ﻠﻟ۵ﻟ۰۴ﮒﺟﻝﮒﻛﺕﻟﺅﺙﻠﮒﭦﺅﺙ?

    participants_to_compensate = []

    for participant_id in executed_participants:

        participants_to_compensate.append(participant_id)

        if participant_id == failed_participant_id:

            break

    

    # ﻠﮒﭦﮔﮒﺅﺙﮒﮔ۶ﻟ۰ﻝﮒﻟ۰۴ﮒﺟﺅﺙ?

    participants_to_compensate.reverse()

    

    # ﮒﮒﭨﭦﻟ۰۴ﮒﺟﻟ؟۰ﮒ

    schedule = CompensationSchedule(

        tx_id=tx_id,

        participants=participants_to_compensate,

        current_index=0,

        max_retries=3,

        status="pending"

    )

    

# ﮒﮒ۷ﻟ۰۴ﮒﺟﻟ؟۰ﮒ

    await self._store_compensation_schedule(schedule)

    

    # ﻟ۶۵ﮒﻝ؛؛ﻛﺕﻛﺕ۹ﻟ۰۴ﮒ?

    if participants_to_compensate:

        await self._trigger_participant_compensation(

            tx_id, participants_to_compensate[0]

        )

    

    return schedule

```



---



## 6. ﮒ؟ﮔﺛﻟﺓﺁﮒﺝ



### 6.1 ﻝ؛؛ﻛﺕﻠﭘﮔ؟ﭖﺅﺙﮒﭦﻝ۰ﮔ۰ﮔﭘﮔﮒﭨﭦﺅﺙ?-5ﮒ۳۸ﺅﺙ



#### 6.1.1 ﮔﺕﮒﺟﻝﭨﻛﭨﭘﮒﺙﮒ?

- **Day 1-2**: Sagaﮒﻟﺍﮒ۷ﮒﭦﻝ۰ﮔ۰ﮔﭘ

  - ﻛﭦﮒ۰ﻝﭘﮔﮔﭦﮒ؟ﻝﺍ

  - PostgreSQLﻟ۰۷ﻝﭨﮔﮒﮒﭨ?

  - ﮒﭦﻝ۰APIﻟ؟ﺝﻟ؟۰

  

- **Day 3**: ﮒﻛﺕﮔﺗﮔ۴ﮒ۲ﮒ؟ﻛﺗ?

  - ﻝﭨﻛﺕﮒﻛﺕﮔﺗﮔ۴ﮒ?

  - ﮒﺙﮔﻠﻠﮒ۷ﻠﮔﻝﺗﻟ؟ﺝﻟ؟۰

  - ﻠ۱ﮔ۲ﮔ۴ﮔﭦﮒﭘﮒ؟ﻝ?

  

- **Day 4-5**: Redis Streamsﻠﮔ

  - ﻛﭦﻛﭨﭘﮔﭖﮒ؟ﻛﺗﻛﺕﮒ؟ﻝﺍ

  - ﻛﭦﻛﭨﭘﮒﮒﺕ/ﻟ؟۱ﻠﮔﭦﮒﭘ

  - ﻝﮔ۶ﻛﺕﮔ۴ﮒﺟﻠﮔ?



#### 6.1.2 ﮔﭖﻟﺁﻠ۹ﻟﺁ

- **ﮒﮒﮔﭖﻟﺁ**: Sagaﮒﻟﺍﮒ۷ﻝﭘﮔﮔﭦﮔﭖﻟﺁ

- **ﻠﮔﮔﭖﻟﺁ**: ﮒﮒﺙﮔﻝ؟ﮒﮒﮔ۴ﮔﭖﻟﺁ?

- **ﮔ۶ﻟﺛﮔﭖﻟﺁ**: ﮒﻛﭦﮒ۰ﮒﭨﭘﻟﺟ?50msﻠ۹ﻟﺁ



### 6.2 ﻝ؛؛ﻛﭦﻠﭘﮔ؟ﭖﺅﺙﮒﺙﮔﻠﻠﻠﮔﺅﺙ?-3ﮒ۳۸ﺅﺙ



#### 6.2.1 ﮒﺙﮔﻠﻠﮒ۷ﮔ۸ﮒﺎ?

- **vn.pyﻠﻠﮒ?*: ﮔﻛﭨ/ﻟﭖﻠﮒﮔ۴ﮔ۴ﮒ۲ﮒ؟ﻝﺍ

- **RQAlphaﻠﻠﮒ?*: ﮒﮔﭖﮔﺍﮔ؟ﮒﮔ۴ﮔ۴ﮒ۲

- **Backtraderﻠﻠﮒ?*: ﮒ۳ﮔﭘﻠﺑﮔ۰ﮔﭘﮔﺍﮔ؟ﮒﮔ?



#### 6.2.2 ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ؟ﻝﺍ

- **ﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻟ۰۴ﮒﺟ**: ﮒﮒﮔﻛﭨﻟﺛ؛ﻝ۶ﭨﻠﭨﻟﺝ

- **ﻟﭖﻠﻟﺍﮔﺑﻟ۰۴ﮒﺟ**: ﮒﮒﻟﭖﻠﻟﺍﮔﺑﻠﭨﻟﺝ

- **ﻟ؟۱ﮒﮒﮔ۴ﻟ۰۴ﮒﺟ**: ﮒ۹ﻟﺁﭨﮔﻛﺛﮔﻟ؟ﺍ



### 6.3 ﻝ؛؛ﻛﺕﻠﭘﮔ؟ﭖﺅﺙﻝﻛﭦ۶ﻝﭦ۶ﻛﺙﮒﺅﺙ?-3ﮒ۳۸ﺅﺙ



#### 6.3.1 ﻝﮔ۶ﮒﻟ۵ﮒ؟ﮒ

- **ﮒ۴ﮒﭦﺓﮔ۲ﮔ?*: ﻛﭦﮒ۰ﮔﮒﻝﻝﮔ?

- **ﮒﭨﭘﻟﺟﻝﮔ۶**: ﮒﻠﭘﮔ؟ﭖﮔ۶ﻟ۰ﮔﭘﻠﺑﻝﮔ?

- **ﮒﻟ۵ﻟ۶ﮒ**: ﻛﺕﻛﺕﻟﺑﮔ۲ﮔﭖﻟ۹ﮒ۷ﮒﻟ?



#### 6.3.2 ﮔ۶ﻟﺛﻛﺙﮒ

- **ﮔﺗﻠﮒ۳ﻝ**: ﮔﺁﮔﮔﺗﻠﻛﭦﮒ۰ﮒ۳ﻝ

- **ﮒﺙﮔ۴ﻛﺙﮒ**: ﻠﻠﭨﮒ۰IOﻛﺙﮒ

- **ﻝﺙﮒﻛﺙﮒ**: ﻠ،ﻠ۱ﮔﺍﮔ؟ﻝﺙﮒ



#### 6.3.3 ﮒ؟ﺗﻠﮒ۱ﮒﺙﭦ

- **ﻝﺛﻝﭨﮒﮒﭦﮒ۳ﻝ**: ﮒﺙﮔﻝ۵ﭨﻝﭦﺟﮒ۳ﻝﮔﭦﮒﭘ

- **ﮔﺍﮔ؟ﻛﺟ؟ﮒ۳ﮒﺓ۴ﮒﺓ**: ﮔﮒ۷ﮔﺍﮔ؟ﻛﺟ؟ﮒ۳ﮒﺓ۴ﮒﺓ

- **ﻝﺝﻠﺝﮔ۱ﮒ۳**: ﮒ۷ﻠﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻛﺟ؟ﮒ۳?



---



## 7. ﮔﭖﻟﺁﮔﺗﮔ۰



### 7.1 ﮒﮒﮔﭖﻟﺁ



| ﮔﭖﻟﺁﻝﺎﭨﮒ، | ﮔﭖﻟﺁﻝ؟ﮔ | ﮔﭖﻟﺁﮔﺗﮔﺏ | ﻠ۱ﮔﻝﭨﮔ |

|----------|----------|----------|----------|

| **ﻝﭘﮔﮔﭦﮔﭖﻟﺁ** | ﻛﭦﮒ۰ﻝﭘﮔﮔﭖﻟﺛ؛ﮔ۲ﻝ۰؟ﮔ?| ﮔ۷۰ﮔﮔﮔﻝﭘﮔﻟﺛ؛ﮔ?| 100%ﻝﭘﮔﻟﺛ؛ﮔ۱ﮔ۲ﻝ۰?|

| **ﻠ۱ﮔ۲ﮔ۴ﮔﭖﻟﺁ?* | ﻟﭖﮔﭦﮔ۲ﮔ۴ﻠﭨﻟﺝﮔ۲ﻝ۰؟ﮔ?| ﮔ۷۰ﮔﮒﻝ۶ﻟﭖﮔﭦﮒﭦﮔﺁ | ﮔ۲ﻝ۰؟ﻟﺁﮒ،ﻟﭖﮔﭦﻛﺕﻟﭘﺏ |

| **ﻟ۰۴ﮒﺟﮔﭖﻟﺁ** | ﻟ۰۴ﮒﺟﻠﭨﻟﺝﮔ۲ﻝ۰؟ﮔ?| ﮔ۷۰ﮔﮒ۳ﺎﻟﺑ۴ﮒﭦﮔﺁﻟ۶۵ﮒﻟ۰۴ﮒﺟ | ﮔﺍﮔ؟ﮒ؟ﮒ۷ﮒﮔﭨ |



### 7.2 ﻠﮔﮔﭖﻟﺁ



| ﮔﭖﻟﺁﮒﭦﮔﺁ | ﮒﻛﺕﮒﺙﮔ | ﮔﭖﻟﺁﮔﺍﮔ؟ | ﻠ۹ﻟﺁﮔﮔ |

|----------|----------|----------|----------|

| **ﮒﮒﺙﮔﮔﻛﭨﮒﮔ?* | vn.py + RQAlpha | 100ﮒ۹ﻟ۰ﻝ۴۷ﮔﻛﭨ?| ﮔﻛﭨﮔﺍﻠﻛﺕﻟﺑﺅﺙﻟﺁﺁﮒﺓ؟=0 |

| **ﻛﺕﮒﺙﮔﻟﭖﻠﮒﮔ?* | vn.py + Backtrader + QMT | 1000ﻛﺕﻟﭖﻠﻟﺍﮔ?| ﻟﭖﻠﮔﭨﻠ۱ﻛﺕﻟﺑﺅﺙﻟﺁﺁﮒﺓ؟<0.01ﮒ?|

| **ﮒ۷ﮒﺙﮔﻟ؟۱ﮒﮒﮔ?* | ﮔﮔ?ﻛﺕ۹ﮒﺙﮔ?| 1000ﻛﺕ۹ﻟ؟۱ﮒﻝﭘﮔ?| ﻟ؟۱ﮒﻝﭘﮔﮔﻝﭨﻛﺕﻟ?|



### 7.3 ﮒﮒﮔﭖﻟﺁ



| ﮒﮒﻝﭨﺑﮒﭦ۵ | ﮔﭖﻟﺁﮔ۰ﻛﭨﭘ | ﮒﮔﺙﮔﮒ | ﻝﮔ۶ﮔﮔ |

|----------|----------|----------|----------|

| **ﮒﺗﭘﮒﻛﭦﮒ۰** | 100ﻛﺕ۹ﮒﺗﭘﮒﻛﭦﮒ?| ﮔﮒﻝ?99.9% | ﻛﭦﮒ۰ﮔﮒﻝﻙﮒﺗﺏﮒﮒﭨﭘﻟﺟ?|

| **ﮒ۳۶ﮔﺍﮔ؟ﻠ** | 10ﻛﺕﮔﻛﭨﮒﮔ?| ﮒ؟ﮔﮔﭘﻠﺑ<5ﮒﻠ | ﮒﮒﻠﻙﮒﮒﻛﺛﺟﻝ?|

| **ﻠﺟﮔﭘﻠﺑﻟﺟﻟ۰?* | ﻟﺟﻝﭨﻟﺟﻟ۰72ﮒﺍﮔﭘ | ﮔﮒﮒﮔﺏﮔﺙ?| ﮒﮒﮒ۱ﻠﺟ<10% |



### 7.4 ﮔﻠﮔﺏ۷ﮒ۴ﮔﭖﻟﺁ



| ﮔﻠﻝﺎﭨﮒ | ﮔﺏ۷ﮒ۴ﮔﺗﮒﺙ | ﻠ۱ﮔﻟ۰ﻛﺕﭦ | ﮔ۱ﮒ۳ﻠ۹ﻟﺁ |

|----------|----------|----------|----------|

| **ﮒﺙﮔﮒ؟ﮔﭦ** | ﮔ۶ﻟ۰ﻛﺕﮒﮔ۱ﮒﺙﮔ?| ﻟ۶۵ﮒﻟ۰۴ﮒﺟﻛﭦﮒ۰ | ﮔﺍﮔ؟ﮒﮔﭨﮔﮒ |

| **ﻝﺛﻝﭨﻛﺕﮔ** | ﮔﮒﺙﮒﺙﮔﻝﺛﻝﭨ | ﻠﻟﺁﮔﭦﮒﭘﻝﮔ | ﻝﺛﻝﭨﮔ۱ﮒ۳ﮒﻟ۹ﮒ۷ﻝﭨ۶ﻝﭨ?|

| **ﮔﺍﮔ؟ﮒﭦﮔﻠ?* | ﮒﮔ۱PostgreSQL | ﻛﭦﮒ۰ﮔﮒﺅﺙﻛﺕﻛﺕ۱ﮒ۳ﺎ | ﮔﺍﮔ؟ﮒﭦﮔ۱ﮒ۳ﮒﻝﭨ۶ﻝﭨ |

| **Redisﮔﻠ** | ﮒﮔ۱Redis | ﻠﻝﭦ۶ﻛﺕﭦﮒﮔ۴ﻟﺍﻝ?| Redisﮔ۱ﮒ۳ﮒﻟ۹ﮒ۷ﮒﮔ?|



---



## 8. ﻠ۲ﻠ۸ﻟﺁﻛﺙﺍﻛﺕﻝﺙﻟ۶۲ﮔ۹ﮔ?



### 8.1 ﮔﮔﺁﻠ۲ﻠ?



| ﻠ۲ﻠ۸ | ﮔ۵ﻝ | ﮒﺛﺎﮒ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |

|------|------|------|----------|

| **ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒ۳ﺎﻟﺑ۴** | ﻛﺕ?| ﻠ،ﺅﺙﮔﺍﮔ؟ﻛﺕﻛﺕﻟﺑﺅﺙ | 1. ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﮒﺗﻝﻟ؟ﺝﻟ؟۰<br>2. ﮔﮒ۷ﻛﺟ؟ﮒ۳ﮒﺓ۴ﮒﺓ<br>3. ﮒ؟ﮔﻛﺕﻟﺑﮔ۶ﮔ۲ﮔ?|

| **ﻝﺛﻝﭨﮒﮒﭦﮒﺁﺙﻟﺑﻟﻟ۲** | ﻛﺛ?| ﻠ،ﺅﺙﮔﺍﮔ؟ﮒﺎﻝ۹ﺅﺙ?| 1. ﮒﻠﮔﭘﻠﮒﺎﻝ۹ﮔ۲ﮔﭖ?br>2. ﻛﭦﭦﮒﺓ۴ﮒﺗﺎﻠ۱ﮔﭖﻝ۷<br>3. ﮔﮒﮒﮒ۴ﻟﮒﭦﻝﻝ?|

| **ﮔ۶ﻟﺛﻝﭘﻠ۱** | ﻛﺕ?| ﻛﺕﺅﺙﮒﭨﭘﻟﺟﮒ۱ﮒﺅﺙ?| 1. ﮔﺗﻠﮒ۳ﻝﻛﺙﮒ<br>2. ﮒﺙﮔ۴ﻠﻠﭨﮒ۰ﻟ؟ﺝﻟ؟?br>3. ﻝﺙﮒﻝﻝﺗﮔﺍﮔ؟ |

| **ﮒﺙﮔﮔ۴ﮒ۲ﮒﮔﺑ** | ﻠ،?| ﻛﺛﺅﺙﻠﻠﮔﮔ؛ﺅﺙ?| 1. ﮔﺛﻟﺎ۰ﮔ۴ﮒ۲ﻠﻝ۵ﭨﮒﮒ<br>2. ﻝﮔ؛ﮒﺙﮒ؟ﺗﮔ۶ﮔﭖﻟﺁ?br>3. ﮔﺕﻟﺟﮒﺙﻟﺟﻝ۶?|



### 8.2 ﮒ؟ﮔﺛﻠ۲ﻠ۸



| ﻠ۲ﻠ۸ | ﮔ۵ﻝ | ﮒﺛﺎﮒ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |

|------|------|------|----------|

| **ﮒﺙﮒﻟﭖﮔﭦﻛﺕﻟﭘ?* | ﻛﺕ?| ﻛﺕﺅﺙﮒﭨﭘﮔﺅﺙ?| 1. ﮒﻠﭘﮔ؟ﭖﮒ؟ﮔ?br>2. ﻛﺙﮒﮔﺕﮒﺟﮒﻟﺛ<br>3. ﮒ۳ﻠ۷ﮒ۷ﻟﺁ۱ﮔﺁﮔ |

| **ﮒ۱ﻠﮔﻟﺛﻝﺙﭦﮒ?* | ﻛﺛ?| ﻛﺕﺅﺙﻟﺑ۷ﻠﻠ۲ﻠ۸ﺅﺙ?| 1. ﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲<br>2. ﻛﭨ۲ﻝﻟﺁﮒ؟۰ﮔﭦﮒﭘ<br>3. ﮒﺗﻟ؟ﻛﺕﻝ۴ﻟﺁﻟﺛ؛ﻝ۶?|

| **ﻛﺝﻟﭖﮒﭦﮒﺙﮒ؟ﺗﮔ?* | ﻠ،?| ﻛﺛﺅﺙﮒﺁﻟ۶۲ﮒﺏﺅﺙ | 1. ﻝﮔ؛ﻠﮒ؟ﻝﻝ۴<br>2. ﻟﮔﻝﺁﮒ۱ﻠﻝ۵ﭨ<br>3. ﮒ۳ﻠﮔﺗﮔ۰ﮒﮒ۳?|



### 8.3 ﻟﺟﻝﭨﺑﻠ۲ﻠ۸



| ﻠ۲ﻠ۸ | ﮔ۵ﻝ | ﮒﺛﺎﮒ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |

|------|------|------|----------|

| **ﻝﮔ۶ﻝﺙﭦﮒ۳ﺎ** | ﻛﺛ?| ﻠ،ﺅﺙﻠ؟ﻠ۱ﻠﺝﮒﻝﺍﺅﺙ | 1. ﮒ؟ﮒﻝﮔ۶ﮔﮔ<br>2. ﻟ۹ﮒ۷ﮒﻟ۵ﮔﭦﮒﭘ<br>3. ﮒ؟ﮔﮒ۴ﮒﭦﺓﮔ۲ﮔ?|

| **ﮔﺍﮔ؟ﻛﺟ؟ﮒ۳ﮒ۳ﮔ** | ﻛﺕ?| ﻛﺕﺅﺙﮔ۱ﮒ۳ﮔﭘﻠﺑﻠﺟﺅﺙ | 1. ﻟ۹ﮒ۷ﮒﻛﺟ؟ﮒ۳ﮒﺓ۴ﮒ?br>2. ﻛﺟ؟ﮒ۳ﮔﭖﻝ۷ﮔﮔ۰۲ﮒ?br>3. ﮔ۷۰ﮔﻝﺁﮒ۱ﻠ۹ﻟﺁ |

| **ﮒ؟ﺗﻠﻟ۶ﮒﻛﺕﻟﭘﺏ** | ﻛﺛ?| ﻛﺕﺅﺙﮔ۶ﻟﺛﻛﺕﻠﺅﺙ?| 1. ﮒ؟ﺗﻠﻝﮔ۶ﻠ۱ﻟ۵<br>2. ﻟ۹ﮒ۷ﮔ۸ﮒ؟ﺗﻟ؟ﺝﻟ؟۰<br>3. ﮔ۶ﻟﺛﮒﮔﭖﻠ۹ﻟﺁ |



---



## 9. ﮔﮔ۰۲ﮔﺎﭨﻝﻠﮔ



### 9.1 System_Manifest.mdﻝﺑ۱ﮒﺙﮔﺑﮔﺍ



```markdown

### 4.4 ﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻛﺟﻠﮔ۷۰ﮒ?



**ﮔ۷۰ﮒID**: DATA_CONSISTENCY_001

**ﮔ۷۰ﮒﮒﻝ۶ﺍ**: ﮒ۳ﮒﺙﮔﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻛﺟﻠﻝﺏﭨﻝﭨ?

**Layerﮒ؟ﻛﺛ**: Layer 4 (ﮔ۶ﻟ۰ﮒﺎ? + Layer 1 (ﮔﺍﮔ؟ﮒﺎ?

**ﮔﺕﮒﺟﻟﻟﺑ۲**: ﻛﺟﻠvn.pyﻙRQAlphaﻙBacktraderﻙQMTﻙbacktesting.pyﻛﭦﻛﺕ۹ﮒﺙﮔﻠﺑﻝﮔﺍﮔ؟ﻛﺕﻟﺑﮔ?



**ﮒﺏﻠ؟ﮔﮔ۰۲**:

- ﮒ۳ﮒﺙﮔﮔﺍﮔ؟ﻛﺕﻟﺑﮔ۶ﻟ؟ﺝﻟ؟۰ﮔﺗﮔ۰?md - ﻛﺕﭨﻟ؟ﺝﻟ؟۰ﮔﮔ۰?

- Sagaﮔ۷۰ﮒﺙﮒ؟ﻝﺍﮔﭖﻝ۷ﮒ?md - ﮔﭖﻝ۷ﮒﺝﮔﮔ۰?

- ﻟ۰۴ﮒﺟﻛﭦﮒ۰ﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲.md - ﻟ۰۴ﮒﺟﮔﭦﮒﭘﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰



**ﮔ۴ﮒ۲ﻟ۶ﻟ**:

- `SagaCoordinator.execute_transaction()` - ﮔ۶ﻟ۰Sagaﻛﭦﮒ۰

- `SagaParticipant.execute_local_transaction()` - ﮔ۶ﻟ۰ﮔ؛ﮒﺍﻛﭦﮒ۰

- `SagaParticipant.compensate_transaction()` - ﻟ۰۴ﮒﺟﻛﭦﮒ۰



**ﮔﺍﮔ؟ﮔﭖ?*: ﮒﺙﮔﻠﻠﮒ?ﻗ?Sagaﮒﻛﺕﮔ?ﻗ?Redis Streams ﻗ?PostgreSQL ﻗ?ﻝﮔ۶ﻝﺏﭨﻝﭨ

```



### 9.2 ﮔ۷۰ﮒﻟﻟﺑ۲ﻟﺝﺗﻝ



| ﮔ۷۰ﮒ | ﻟﻟﺑ۲ | ﻛﺕﻟﺑﻟﺑ?|

|------|------|--------|

| **Sagaﮒﻟﺍﮒ?* | ﻛﭦﮒ۰ﮒﻟﺍﻙﻝﭘﮔﻝ؟۰ﻝﻙﻟ۰۴ﮒﺟﻟﺍﮒﭦ?| ﮒﺙﮔﮒﺓﻛﺛﮔﻛﺛﻙﮔﺍﮔ؟ﮒﮒ۷ﮒ؟ﻝ?|

| **Sagaﮒﻛﺕﮔ?* | ﮒﺙﮔﻠﻠﻙﮔ؛ﮒﺍﻛﭦﮒ۰ﮔ۶ﻟ۰ﻙﻟ۰۴ﮒﺟﮔ۶ﻟ۰?| ﻟﺓ۷ﮒﺙﮔﮒﻟﺍﻙﮒ۷ﮒﺎﻝﭘﮔﻝ؟۰ﻝ?|

| **PostgreSQLﮒﮒ۷** | ﻛﭦﮒ۰ﻝﭘﮔﮔﻛﺗﮒﻙﻛﺕﻟﺑﮔ۶ﮒﺟ،ﻝ?| ﻛﺕﮒ۰ﻠﭨﻟﺝﻙﻛﭦﻛﭨﭘﮒﮒﺕ?|

| **Redis Streams** | ﻛﭦﻛﭨﭘﮒﮒﺕ/ﻟ؟۱ﻠﻙﮒﺛﻛﭨ۳ﮒﮒ?| ﻝﭘﮔﮔﻛﺗﮒﻙﻛﺕﮒ۰ﻠﭨﻟﺝ |



### 9.3 ﻝﮔ؛ﻝ؟۰ﻝﻝﻝ۴



#### 9.3.1 ﻝﮔ؛ﮔﻟﺁﻟ۶ﮒ

- **v1.0.0**: ﮒﭦﻝ۰ﮔ۰ﮔﭘﺅﺙﮔﺁﮔﮒﮒﺙﮔﮒﮔ۴

- **v1.1.0**: ﮒ۷ﮒﺙﮔﮔﺁﮔﺅﺙﮒ۱ﮒﺙﭦﻟ۰۴ﮒﺟﮔﭦﮒﭘ

- **v1.2.0**: ﮔ۶ﻟﺛﻛﺙﮒﺅﺙﮔﺗﻠﮒ۳ﻝﮔﺁﮔ?

- **v2.0.0**: ﮔﭘﮔﮒﻝﭦ۶ﺅﺙﮔﺁﮔﮒﮒﺕﮒﺙﻠ۷ﻝﺛﺎ



#### 9.3.2 ﮒﮒﮒﺙﮒ؟ﺗﻛﺟﻟﺁ

- **APIﮒﺙﮒ؟ﺗ**: v1.xﻝﮔ؛ﻠﺑAPIﮒ؟ﮒ۷ﮒﺙﮒ؟ﺗ

- **ﮔﺍﮔ؟ﮒﺙﮒ؟ﺗ**: ﮔﺍﮔ؟ﮒﭦSchemaﮒﮔﺑﮔﻛﺝﻟﺟﻝ۶ﭨﻟﮔ؛

- **ﻠﻝﺛ؟ﮒﺙﮒ؟ﺗ**: ﻠﻝﺛ؟ﮔﻛﭨﭘﮒﮒﮒﺙﮒ؟ﺗﺅﺙﮒﭦﮒﺙﮒﮔﺍﻟ۵ﮒ?



---



## 10. ﮔﮒﮔﮔﻛﺕﻠ۹ﮔﭘﮔﮒ?



### 10.1 ﮒﻟﺛﻠ۹ﮔﭘﮔﮒ



| ﮒﻟﺛﻝ?| ﻠ۹ﮔﭘﮔﮒ | ﮔﭖﻟﺁﮔﺗﮔﺏ |

|--------|----------|----------|

| **ﮔﻛﭨﮒﮔ۴** | 5ﻛﺕ۹ﮒﺙﮔﮔﻛﭨﮔﺍﻠﮒ؟ﮒ۷ﻛﺕﻟ?| ﻠﮔﭦﻠﮒ100ﮒ۹ﻟ۰ﻝ۴۷ﮒﺁﺗﮔﺁﮔﻛﭨ?|

| **ﻟﭖﻠﮒﮔ۴** | 5ﻛﺕ۹ﮒﺙﮔﻟﭖﻠﮔﭨﻠ۱ﻟﺁﺁﮒﺓ؟<0.01ﮒ?| ﮒ۳۶ﻠ۱ﻟﭖﻠﻟﺛ؛ﻝ۶ﭨﮔﭖﻟﺁ |

| **ﻟ؟۱ﮒﮒﮔ۴** | ﻟ؟۱ﮒﻝﭘﮔﮔﻝﭨﻛﺕﻟﺑﺅﺙﮒﭨﭘﻟﺟ<5ﻝ۶?| ﮔ۷۰ﮔ1000ﻛﺕ۹ﻟ؟۱ﮒﻝﭘﮔﮒﮔ?|

| **ﻟ۰۴ﮒﺟﻛﭦﮒ۰** | ﮒ۳ﺎﻟﺑ۴ﮒﭦﮔﺁﮔﺍﮔ؟ﮒ؟ﮒ۷ﮒﮔﭨ | ﮔﺏ۷ﮒ۴ﮒﻝﺎﭨﮔﻠﮔﭖﻟﺁﮒﮔﭨ |



### 10.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘﮔﮒ



| ﮔﮔ | ﮒﮔﺙﮔﮒ | ﮔﭖﻟﺁﮔ۰ﻛﭨﭘ |

|------|----------|----------|

| **ﮒﻛﭦﮒ۰ﮒﭨﭘﻟﺟ?* | <50ms (P95) | ﮔ۲ﮒﺕﺕﻝﺛﻝﭨﻝﺁﮒ۱ |

| **ﮒﺗﭘﮒﮒﮒﻠ?* | >100ﻛﭦﮒ۰/ﻝ۶?| 10ﻛﺕ۹ﮒﺗﭘﮒﮒ؟۱ﮔﺓﻝ،ﺁ |

| **ﻟ۰۴ﮒﺟﮒﭨﭘﻟﺟ** | <100ms (P95) | ﮒﮒﺙﮔﮒ۳ﺎﻟﺑ۴ﮒﭦﮔ?|

| **ﮒﮒﻛﺛﺟﻝ۷** | <512MB | 10ﻛﺕﻛﭦﮒ۰ﮒ۳ﻝ?|



### 10.3 ﮒﺁﻠﮔ۶ﻠ۹ﮔﭘﮔﮒ?



| ﮔﮔ | ﮒﮔﺙﮔﮒ | ﮔﭖﻟﺁﮔﺗﮔﺏ |

|------|----------|----------|

| **ﻛﭦﮒ۰ﮔﮒﻝ?* | >99.9% | 24ﮒﺍﮔﭘﮒﮒﮔﭖﻟﺁ |

| **ﮔﺍﮔ؟ﻛﺕﻟﺑﮔ?* | 100%ﻛﺕﻟ?| ﮒ؟ﮔﻛﺕﻟﺑﮔ۶ﮔ۲ﮔ?|

| **ﮔﻠﮔ۱ﮒ۳** | <5ﮒﻠ | ﮔ۷۰ﮔﮒﺙﮔﮒ؟ﮔﭦﮔ۱ﮒ۳ |

| **ﻝﮔ۶ﻟ۵ﻝﻝ?* | 100%ﮒﺏﻠ؟ﮔﮔ | ﻝﮔ۶ﻛﭨ۹ﻟ۰۷ﮔﺟﻠ۹ﻟﺁ?|



---



## 11. ﮒﻝﭨﮔﺙﻟﺟﻟ۶ﮒ



### 11.1 ﻝﮔﻛﺙﮒﺅﺙ?-2ﻛﺕ۹ﮔﺅﺙ?



1. **ﮔ۶ﻟﺛﻛﺙﮒ**

   - ﮔﺗﻠﻛﭦﮒ۰ﮒ۳ﻝﮔﺁﮔ

   - ﮔﭖﮔﺍﺑﻝﭦﺟﮒﺗﭘﻟ۰ﮔ۶ﻟ۰?

- ﮒﮒﮔﺍﮔ؟ﮒﭦﻝﺙﮒ?



2. **ﻝﮔ۶ﮒ۱ﮒﺙﭦ**

   - ﮒ؟ﮔﭘﻛﺕﻟﺑﮔ۶ﻛﭨ۹ﻟ۰۷ﮔﺟ

- ﮔﭦﻟﺛﮒﻟ۵ﻟ۶ﮒ

- ﻟ۹ﮒ۷ﮒﮔﺗﮒﮒﮔ?



### 11.2 ﻛﺕﮔﮔ۸ﮒﺎﺅﺙ?-6ﻛﺕ۹ﮔﺅﺙ?



1. **ﮔﭘﮔﮒﻝﭦ۶**

   - ﮒﮒﺕﮒﺙSagaﮒﻟﺍﮒ?

- ﮒ۳ﮔﺍﮔ؟ﻛﺕﮒﺟﮔﺁﮔ?

   - ﮒﭦﮒﻠﺝﮒ؟۰ﻟ؟۰ﻟﺟﺛﻟﺕ?



2. **ﮒﻟﺛﮔ۸ﮒﺎ**

   - ﮒ؟ﮔﭘﮔﭖﮒﺙﻛﺕﻟﺑﮔ۶ﮔ۲ﮔ?

- ﮔﭦﮒ۷ﮒ۵ﻛﺗﮒﺙﮒﺕﺕﮔ۲ﮔﭖ?

   - ﻟ۹ﮒ۷ﮒﻛﺟ؟ﮒ۳ﮒﭨﭦﻟ؟?



### 11.3 ﻠﺟﮔﮔﺟﮔﺁﺅﺙ?-12ﻛﺕ۹ﮔﺅﺙ?



1. **ﮔﭦﻟﺛﻟ۹ﮔﺎﭨ**

   - ﻟ۹ﻠﮒﭦﻛﺕﻟﺑﮔ۶ﻝﭦ۶ﮒ،ﻟﺍﮔ?

   - ﻠ۱ﮔﭖﮔ۶ﻟ۰۴ﮒﺟﻛﺙﮒ?

   - ﻟ۹ﻛﺟ؟ﮒ۳ﮔﺍﮔ؟ﻛﺕﻟﺑﮔ?



2. **ﻝﮔﻠﮔ?*

- ﻝ؛؛ﻛﺕﮔﺗﮒﺙﮔﮔﮒﮔ۴ﮒ?

   - ﻛﭦﮒﻝﻠ۷ﻝﺛﺎﻛﺙﮒ?

   - ﮒﺙﮔﭦﻝ۳ﺝﮒﭦﻟﺑ۰ﻝ?



---



## ﻠﮒﺛAﺅﺙﮔﺁﻟﺁﻟ۰۷



| ﮔﺁﻟﺁ | ﮒ؟ﻛﺗ |

|------|------|

| **Sagaﮔ۷۰ﮒﺙ** | ﻛﺕﻝ۶ﻝ؟۰ﻝﻠﺟﮔﭘﻠﺑﻟﺟﻟ۰ﻛﭦﮒ۰ﻝﮔ۷۰ﮒﺙﺅﺙﮒﺍﮒ۳۶ﻛﭦﮒ۰ﮔﮒﻛﺕﭦﮒ۳ﻛﺕ۹ﮔ؛ﮒﺍﻛﭦﮒ۰ﺅﺙﻠﻟﺟﻟ۰۴ﮒﺟﮔﭦﮒﭘﻛﺟﻟﺁﻛﺕﻟﺑﮔ?|

| **ﻟ۰۴ﮒﺟﻛﭦﮒ۰** | ﻝ۷ﻛﭦﮔ۳ﻠﮒﺓﺎﮔ۶ﻟ۰ﮔ؛ﮒﺍﻛﭦﮒ۰ﻝﮔﻛﺛﺅﺙﻛﺟﻟﺁﻛﭦﮒ۰ﮒ۳ﺎﻟﺑ۴ﮔﭘﮔﺍﮔ؟ﻛﺕﻟﺑﮔ?|

| **ﮔﻝﭨﻛﺕﻟﺑﮔ?* | ﻝﺏﭨﻝﭨﻛﺟﻟﺁﮒ۷ﮔﺎ۰ﮔﮔﺍﻝﮔﺑﮔﺍﻝﮔﮒﭖﻛﺕﺅﺙﮔﻝﭨﮔﮔﮒﺁﮔ؛ﻠﺛﻛﺙﻟﺝﺝﮒﺍﻛﺕﻟﺑﻝﻝﭘﮔ?|

| **ﮒﺙﭦﻛﺕﻟﺑﮔ?* | ﻛﭨﭨﻛﺛﻟﺁﭨﮒﮔﻛﺛﻠﺛﮒ۴ﺛﮒﻛﭨ۴ﮔﻝ۶ﻠ۰ﭦﮒﭦﻛﺕﮔ؛۰ﻛﺕﻛﺕ۹ﮒﺍﮔ۶ﻟ۰ﺅﺙﻛﺕﮔﺁﻛﺕ۹ﻟﺁﭨﮔﻛﺛﻠﺛﻟﺟﮒﮔﻟﺟﻛﺕﮔ؛۰ﮒﮔﻛﺛﻝﻝﭨﮔ?|

| **ﻠ۱ﮔ۲ﮔ?* | ﮒ۷ﮔ۶ﻟ۰ﻛﭦﮒ۰ﮒﮔ۲ﮔ۴ﻟﭖﮔﭦﮒﺁﻝ۷ﮔ۶ﮒﻝﭦ۵ﮔﮔ۰ﻛﭨﭘﺅﺙﻠﺟﮒﮔﮔﻛﭦﮒ۰ﮔ۶ﻟ۰?|

| **ﮒﺗﻝﮔ?* | ﮒﻛﺕﮔﻛﺛﮔ۶ﻟ۰ﻛﺕﮔ؛۰ﮔﮒ۳ﮔ؛۰ﻝﮔﮔﻝﺕﮒﺅﺙﻛﺕﻛﺙﻛﭦ۶ﻝﮒﺁﻛﺛﻝ?|



## ﻠﮒﺛBﺅﺙﻝﺕﮒﺏﮔﮔ۰۲ﻝﺑ۱ﮒﺙ?



1. MULTI_ENGINE_BLUEPRINT.md - ﮒ۳ﮒﺙﮔﮔﭘﮔﻟﮒ?

2. STORAGE_TIER.md - ﮒﮒ۷ﮒﺎﮔﭘﮔﻟ؟ﺝﻟ؟?

3.  - ﮒﺙﮔﻠﻠﮒ۷ﻟ؟ﺝﻟ؟?

4.  - ﻛﭦ۳ﮔﮔﮔ؛ﮔ۷۰ﮒﻟ؟ﺝﻟ؟۰



---



**ﮔﮔ۰۲ﻝﮔ؛ﮒﮒﺎ**:

- v1.0.0 (2026-04-02): ﮒﮒ۶ﻝﮔ؛ﺅﺙﮒ؟ﮔﺑSagaﮔ۷۰ﮒﺙﻟ؟ﺝﻟ؟۰ﮔﺗﮔ۰



**ﮒ؟۰ﮔﺕﻟ؟ﺍﮒﺛ**:

- ﮔﭘﮔﮒ؟۰ﮔﺕ: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?

- ﮔﮔﺁﮒ؟۰ﮔ? ﮒﺝﮒ؟۰ﮔ?

- ﻛﺕﮒ۰ﮒ؟۰ﮔﺕ: ﮒﺝﮒ؟۰ﮔ?



**ﮒﻟ۶ﮔ۶ﮔ۲ﮔ?*:

- ﻗ?Layerﮒ؟ﻛﺛﮔ۲ﻝ۰؟ (Layer 4 + Layer 1)

- ﻗ?ﻟﻟﺑ۲ﻟﺝﺗﻝﮔﺕﮔﺍ

- ﻗ?ﮔ۴ﮒ۲ﮒ؟ﻛﺗﮒ؟ﮔﺑ

- ﻗ?ﮔﺍﮔ؟ﮔﭖﮒﺝﮒﻝ۰؟

- ﻗ?ﮒ؟ﮔﺛﻟﺓﺁﮒﺝﮒﺁﻟ۰

- ﻗ?ﮔﮔ۰۲ﻝﺑ۱ﮒﺙﮒ؟ﮔﺑ

- ﻗ?ﻝﮔ؛ﮔﻟﺁﮔﻝ۰؟

- ﻗ?ﻠ۲ﻠ۸ﻟﺁﮒ،ﮒ۷ﻠ۱

- ﻗ?ﻝ؛۵ﮒﻛﺕﻛﺕﮔﭦﮔﮔﮒ (ﻠ۱ﻟ؟۰ﮒﻟ۶ﻝﻗ۴95%)

