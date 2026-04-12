---
module_id: LAYER_11_TOOL_INTERFACE_SPECIFICATION
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - LAYER_11_TOOL_INTERFACE技术规范
layer: layer_06
applicable_scope: Layer 11ﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻟ۶ﻟ
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔﮒ
parent_document: ./LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ
---
---





# Layer 11ﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻟ۶ﻟ

> **核心职责**: 文档内容说明

> **职责边界**: 

> - ✅ 本文档负责：文档内容说明相关内容

> - ❌ 本文档不负责：其他模块内容





> ﮔﺕﻠ۲ﻠﮒﻛﭦ۳ﮔﻝﺏﭨﻝﭨ v5.2 - ﮔﮔﮔ۷۰ﮒﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ?> **ﻝﺑ۱ﮒﺙ**: `LAYER_11_TOOL_SPEC_001`

> **ﮔﺕﮒﺟﮒ؟ﻛﺛ**: ﮔﻝ۰؟ﮔﺁﻛﺕ۹ﮔ۷۰ﮒﮔﺁﮔﻝﮔﻛﺛﻙﮒﮔﺍﮒﻟﺟﮒﮒﺙﺅﺙﻠﺟﮒﻠﮒ۳ﮔﮒﻛﭦ۳ﻛﭨﻟ؟ﺝﻟ؟۰

> **ﮒﺏﻠ؟ﮒﮒ**: Layer 11ﻝﭨﻛﺕﮔﮒﺝﻟﺁﮒ،ﺅﺙﮒﮔ۷۰ﮒﮒ۹ﮔﻛﺝﻝﭦﺁAPIﮔ۴ﮒ۲





## ﻛﺕﻙﻟ؟ﺝﻟ؟۰ﮒﮒ?

### 1.1 ﮔﺕﮒﺟﮒﮒ



| ﮒﮒ | ﻟﺁﺑﮔ |

|------|------|

| **ﮒﻛﺕAIﮒﺎ?* | Layer 11ﻟﺑﻟﺑ۲ﮔﮔﮔﮒﺝﻟﺁﮒ،ﮒﮒﮔﺍﮔﮒ |

| **ﻝﭦﺁﮔ۶ﻟ۰ﮒﺎ** | ﮒﮔ۷۰ﮒﮒ۹ﮔﻛﺝAPIﮔ۴ﮒ۲ﺅﺙﻛﺕﮒﮒ،AIﻝﻟ۶۲ |

| **ﮒﺓ۴ﮒﺓﮒﮒﺍﻟ۲?* | ﮔﺁﻛﺕ۹ﮔ۷۰ﮒﮒﺍﻟ۲ﻛﺕﭦﮒﺓ۴ﮒﺓﺅﺙﻠﻟﺟﻝﭨﻛﺕﮔ۴ﮒ۲ﻟﺍﻝ۷ |

| **ﮔ۴ﮒ۲ﮔﮒﮒ?* | ﮔﮔﮒﺓ۴ﮒﺓﻠﭖﮒﺝ۹ﻝﭨﻛﺕﻝﻟﺝﮒ۴ﻟﺝﮒﭦﮔﺙﮒﺙ?|



### 1.2 ﻝﭨﮒﮒﺎﮔ؛۰



```



**ﮒﺏﻠ؟ﻝ?*ﺅﺙ?- ﻗ?Layer 11ﻠﻟ۵ﻝﭨﮒﮔﮒﺝﻟﺁﮒ،ﮒﮒﮔﺍﮔﮒ

- ﻗ?ﮒﮔ۷۰ﮒﻛﺕﻠﻟ۵ﻝﭨﮒﮔﮒﻛﭦ۳ﻛﭨﻟ؟ﺝﻟ؟?- ﻗ?ﮒﮔ۷۰ﮒﮒ۹ﻠﻟ۵ﮔﻝ۰؟ﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻟ۶ﻟ?



## ﻛﭦﻙﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻝﭨﻛﺕﻟ۶ﻟ



### 2.1 ﻟﺝﮒ۴ﮒﮔﺍﻟ۶ﻟ



```python

{

    "action": "ﮔﻛﺛﻝﺎﭨﮒ",  # ﮒﺟﻠﺅﺙﮒﺓﻛﺛﮔﻛﺛﮒﻝ۶?    "params": {            # ﮒﺟﻠﺅﺙﮔﻛﺛﮒﮔ?        "param1": "value1",

        "param2": "value2"

    }

}

```



### 2.2 ﻟﺝﮒﭦﻝﭨﮔﻟ۶ﻟ



```python

{

    "success": True,       # ﮒﺟﻠﺅﺙﮔﺁﮒ۵ﮔﮒ?    "message": "ﮔﻛﺛﻝﭨﮔﮔﻟﺟﺍ",  # ﮒﺟﻠﺅﺙﻝﭨﮔﮔﻟﺟ?    "data": {              # ﮒﺁﻠﺅﺙﻟﺟﮒﮔﺍﮔ؟

        "key1": "value1",

        "key2": "value2"

    },

    "error": None          # ﮒﺁﻠﺅﺙﻠﻟﺁﺁﻛﺟ۰ﮔﺁ

}

```





## ﻛﺕﻙP0ﮔ۷۰ﮒﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻟ۶ﻟ



### 3.1 ﻝﻝ۴ﮒﺓ۴ﮒﺓﺅﺙStrategyToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_STRATEGY_001

**ﻛﺙﮒﻝﭦ?*: P0

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 5 ﻝﻝ۴ﮔ۶ﻟ۰ﮒﺎ?

#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **configure** | ﻠﻝﺛ؟ﮔﺍﻝﻝ?| strategy_type, holding_period, stop_loss, take_profit | strategy_id |

| **start** | ﮒﺁﮒ۷ﻝﻝ۴ | strategy_id | ﮒﺁﮒ۷ﻝﭘﮔ?|

| **stop** | ﮒﮔ۱ﻝﻝ۴ | strategy_id | ﮒﮔ۱ﻝﭘﮔ?|

| **status** | ﮔ۴ﻟﺁ۱ﻝﻝ۴ﻝﭘﮔ?| strategy_id | ﻝﻝ۴ﻝﭘﮔﻟﺁ۵ﮔ?|

| **list** | ﮒﮒﭦﮔﮔﻝﻝ?| ﮔ?| ﻝﻝ۴ﮒﻟ۰۷ |

| **backtest** | ﮒﮔﭖﻝﻝ۴ | strategy_id, start_date, end_date | ﮒﮔﭖﻝﭨﮔ |

| **optimize** | ﻛﺙﮒﻝﻝ۴ﮒﮔﺍ | strategy_id, param_ranges | ﻛﺙﮒﻝﭨﮔ |



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 3.1.1 configureﺅﺙﻠﻝﺛ؟ﻝﻝ۴ﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "configure",

    "params": {

"strategy_type": "momentum",      # ﮒﺟﻠﺅﺙﻝﻝ۴ﻝﺎﭨﮒ?        "holding_period": 5,               # ﮒﺁﻠﺅﺙﮔﻛﭨﮒ۷ﮔﺅﺙﮒ۳۸ﺅﺙ?        "stop_loss": 0.1,                  # ﮒﺁﻠﺅﺙﮔ۱ﮔﮔﺁﻛﺝ

"take_profit": 0.2,                # ﮒﺁﻠﺅﺙﮔ۱ﻝﮔﺁﻛﺝ

        "position_size": 0.05,             # ﮒﺁﻠﺅﺙﻛﭨﻛﺛﮒ۳۶ﮒﺍ

        "universe": ["000001.SZ", "600000.SH"]  # ﮒﺁﻠﺅﺙﻟ۰ﻝ۴۷ﮔﺎ?    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

"message": "ﻝﻝ۴ﻠﻝﺛ؟ﮔﮒ",

    "data": {

        "strategy_id": "STRAT_20260402_001",

"strategy_name": "ﮒ۷ﻠﻝﻝ۴_5ﮔ۴ﮔﻛﭨ?,

        "created_at": "2026-04-02T10:30:00Z",

        "status": "configured"

    }

}

```



##### 3.1.2 startﺅﺙﮒﺁﮒ۷ﻝﻝ۴ﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "start",

    "params": {

"strategy_id": "STRAT_20260402_001"  # ﮒﺟﻠﺅﺙﻝﻝ۴ID

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

"message": "ﻝﻝ۴ﮒﺓﺎﮒﺁﮒ?,

    "data": {

        "strategy_id": "STRAT_20260402_001",

        "status": "running",

        "started_at": "2026-04-02T10:35:00Z"

    }

}

```



##### 3.1.3 stopﺅﺙﮒﮔ۱ﻝﻝ۴ﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "stop",

    "params": {

"strategy_id": "STRAT_20260402_001"  # ﮒﺟﻠﺅﺙﻝﻝ۴ID

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

"message": "ﻝﻝ۴ﮒﺓﺎﮒﮔ?,

    "data": {

        "strategy_id": "STRAT_20260402_001",

        "status": "stopped",

        "stopped_at": "2026-04-02T11:00:00Z"

    }

}

```



##### 3.1.4 statusﺅﺙﮔ۴ﻟﺁ۱ﻝﻝ۴ﻝﭘﮔﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "status",

    "params": {

"strategy_id": "STRAT_20260402_001"  # ﮒﺟﻠﺅﺙﻝﻝ۴ID

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

"message": "ﻝﻝ۴ﻝﭘﮔﮔ۴ﻟﺁ۱ﮔﮒ?,

    "data": {

        "strategy_id": "STRAT_20260402_001",

        "status": "running",

        "performance": {

            "total_return": 0.15,

            "sharpe_ratio": 1.2,

            "max_drawdown": 0.08,

            "win_rate": 0.65

        },

        "positions": [

            {"symbol": "000001.SZ", "weight": 0.05, "pnl": 0.02},

            {"symbol": "600000.SH", "weight": 0.05, "pnl": -0.01}

        ]

    }

}

```



##### 3.1.5 listﺅﺙﮒﮒﭦﮔﮔﻝﻝ۴ﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "list",

    "params": {}

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

"message": "ﻝﻝ۴ﮒﻟ۰۷ﮔ۴ﻟﺁ۱ﮔﮒ",

    "data": {

        "strategies": [

            {

                "strategy_id": "STRAT_20260402_001",

"name": "ﮒ۷ﻠﻝﻝ۴_5ﮔ۴ﮔﻛﭨ?,

                "status": "running",

                "created_at": "2026-04-02T10:30:00Z"

            },

            {

                "strategy_id": "STRAT_20260401_002",

"name": "ﮒﮒﺙﮒﮒﺛﻝﻝ?,

                "status": "stopped",

                "created_at": "2026-04-01T09:00:00Z"

            }

        ],

        "total_count": 2

    }

}

```



---



### 3.2 ﮒﮒﮒﺓ۴ﮒﺓﺅﺙFactorToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_FACTOR_001

**ﻛﺙﮒﻝﭦ?*: P0

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 2 ﮒﮒﮒﺎ?

#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **query** | ﮔ۴ﻟﺁ۱ﮒﮒﮔﺍﮔ؟ | factor_name, start_date, end_date | ﮒﮒﮔﺍﮔ؟ |

| **mine** | AIﮔﮔﮔﺍﮒﮒ?| factor_type, constraints | ﮔﺍﮒﮒﮒ؟ﻛﺗ?|

| **validate** | ﻠ۹ﻟﺁﮒﮒﮔﮔﮔ?| factor_id, test_period | ﻠ۹ﻟﺁﻝﭨﮔ |

| **monitor** | ﻝﮔ۶ﮒﮒﮔﺙﻝ۶ﭨ | factor_id, threshold | ﮔﺙﻝ۶ﭨﮔ۴ﮒ |



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 3.2.1 queryﺅﺙﮔ۴ﻟﺁ۱ﮒﮒﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "query",

    "params": {

"factor_name": "momentum",         # ﮒﺟﻠﺅﺙﮒﮒﮒﻝ۶?        "start_date": "2026-01-01",        # ﮒﺁﻠﺅﺙﮒﺙﮒ۶ﮔ۴ﮔ?        "end_date": "2026-03-31",          # ﮒﺁﻠﺅﺙﻝﭨﮔﮔ۴ﮔ

"symbols": ["000001.SZ", "600000.SH"]  # ﮒﺁﻠﺅﺙﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

"message": "ﮒﮒﮔﺍﮔ؟ﮔ۴ﻟﺁ۱ﮔﮒ",

    "data": {

        "factor_name": "momentum",

        "factor_values": [

            {"symbol": "000001.SZ", "date": "2026-01-01", "value": 0.05},

            {"symbol": "600000.SH", "date": "2026-01-01", "value": -0.02}

        ],

        "statistics": {

            "mean": 0.015,

            "std": 0.08,

            "ic": 0.12

        }

    }

}

```



##### 3.2.2 mineﺅﺙﮔﮔﮔﺍﮒﮒﺅﺙ?

**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "mine",

    "params": {

"factor_type": "momentum",         # ﮒﺟﻠﺅﺙﮒﮒﻝﺎﭨﮒ?        "constraints": {                    # ﮒﺁﻠﺅﺙﻝﭦ۵ﮔﮔ۰ﻛﭨﭘ

            "max_period": 20,

            "min_ic": 0.05

        }

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

"message": "ﮔﺍﮒﮒﮔﮔﮔﮒ?,

    "data": {

        "factor_id": "FACTOR_20260402_001",

"factor_name": "ﮒ۷ﻠﮒﮒ_10ﮔ?,

        "formula": "close.shift(10) / close - 1",

        "ic": 0.08,

        "performance": {

            "mean_return": 0.02,

            "win_rate": 0.55

        }

    }

}

```



---



### 3.3 ﻠ۲ﮔ۶ﮒﺓ۴ﮒﺓﺅﺙRiskControlToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_RISK_001

**ﻛﺙﮒﻝﭦ?*: P0

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 6 ﻠ۲ﮔ۶ﮒﺎ?

#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **adjust_params** | ﻟﺍﮔﺑﻠ۲ﮔ۶ﮒﮔﺍ | max_drawdown, position_limit | ﮔﺑﮔﺍﮒﻝﮒﮔﺍ |

| **set_stop_loss** | ﻟ؟ﺝﻝﺛ؟ﮔ۱ﮔ | strategy_id, stop_loss | ﮔ۱ﮔﻟ؟ﺝﻝﺛ؟ |

| **set_take_profit** | ﻟ؟ﺝﻝﺛ؟ﮔ۱ﻝ | strategy_id, take_profit | ﮔ۱ﻝﻟ؟ﺝﻝﺛ؟ |

| **get_risk_report** | ﻟﺓﮒﻠ۲ﻠ۸ﮔ۴ﮒ | ﮔ?| ﻠ۲ﻠ۸ﮔ۴ﮒ |



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 3.3.1 adjust_paramsﺅﺙﻟﺍﮔﺑﻠ۲ﮔ۶ﮒﮔﺍﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "adjust_params",

    "params": {

        "max_drawdown": 0.10,      # ﮒﺟﻠﺅﺙﮔﮒ۳۶ﮒﮔ?        "position_limit": 0.05,    # ﮒﺟﻠﺅﺙﮒﻟ۰ﻛﭨﻛﺛﻛﺕﻠ?        "daily_loss_limit": 0.02   # ﮒﺁﻠﺅﺙﮒﮔ۴ﻛﭦﮔﻛﺕﻠ

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

    "message": "ﻠ۲ﮔ۶ﮒﮔﺍﻟﺍﮔﺑﮔﮒ",

    "data": {

        "max_drawdown": 0.10,

        "position_limit": 0.05,

        "daily_loss_limit": 0.02,

        "updated_at": "2026-04-02T10:30:00Z"

    }

}

```



##### 3.3.2 set_stop_lossﺅﺙﻟ؟ﺝﻝﺛ؟ﮔ۱ﮔﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "set_stop_loss",

    "params": {

"strategy_id": "STRAT_20260402_001",  # ﮒﺟﻠﺅﺙﻝﻝ۴ID

"stop_loss": 0.08                     # ﮒﺟﻠﺅﺙﮔ۱ﮔﮔﺁﻛﺝ?    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

"message": "ﮔ۱ﮔﻟ؟ﺝﻝﺛ؟ﮔﮒ",

    "data": {

        "strategy_id": "STRAT_20260402_001",

        "stop_loss": 0.08,

        "updated_at": "2026-04-02T10:35:00Z"

    }

}

```



---



### 3.4 ﮔﮔﮒﺓ۴ﮒﺓﺅﺙApprovalToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_APPROVAL_001

**ﻛﺙﮒﻝﭦ?*: P0

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 8 ﮔﮔﮒﺎ?

#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **confirm** | ﮔﮔﻝ۰؟ﻟ؟۳ | decision_id, approved | ﮔﮔﻝﭨﮔ |

| **reject** | ﮔﻝﭨﮔﮔ | decision_id, reason | ﮔﻝﭨﻝﭨﮔ |

| **list_pending** | ﮒﮒﭦﮒﺝﮔﮔﮒﺏﻝ?| ﮔ?| ﮒﺝﮔﮔﮒﻟ۰?|



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 3.4.1 confirmﺅﺙﮔﮔﻝ۰؟ﻟ؟۳ﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "confirm",

    "params": {

"decision_id": "DEC_20260402_001",  # ﮒﺟﻠﺅﺙﮒﺏﻝID

"approved": True,                    # ﮒﺟﻠﺅﺙﮔﺁﮒ۵ﮔﮔ?        "comment": "ﮒﮔﻛﺕﮔﭘﻝﻝ۴"             # ﮒﺁﻠﺅﺙﮒ۳ﮔﺏ۷

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

    "message": "ﮔﮔﻝ۰؟ﻟ؟۳ﮔﮒ",

    "data": {

        "decision_id": "DEC_20260402_001",

        "status": "approved",

        "approved_at": "2026-04-02T10:30:00Z",

        "approved_by": "user"

    }

}

```





## ﮒﻙP1ﮔ۷۰ﮒﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻟ۶ﻟ



### 4.1 ﻟﮔﮒﺓ۴ﮒﺓﺅﺙSentimentToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_SENTIMENT_001

**ﻛﺙﮒﻝﭦ?*: P1

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 3 ﻟﮔﮒﺎ?

#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **query** | ﮔ۴ﻟﺁ۱ﻟﮔ | symbol, start_date, end_date | ﻟﮔﮔﺍﮔ؟ |

| **alert** | ﻟﮔﻠ۱ﻟ۵ | threshold, keywords | ﻠ۱ﻟ۵ﮒﻟ۰۷ |



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 4.1.1 queryﺅﺙﮔ۴ﻟﺁ۱ﻟﮔﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "query",

    "params": {

"symbol": "000001.SZ",        # ﮒﺟﻠﺅﺙﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ?        "start_date": "2026-03-01",   # ﮒﺁﻠﺅﺙﮒﺙﮒ۶ﮔ۴ﮔ?        "end_date": "2026-03-31",     # ﮒﺁﻠﺅﺙﻝﭨﮔﮔ۴ﮔ

        "keywords": ["ﻛﺕﻝﭨ۸", "ﮒ۸ﮒ۴ﺛ"]   # ﮒﺁﻠﺅﺙﮒﺏﻠ؟ﻟﺁ?    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

    "message": "ﻟﮔﮔ۴ﻟﺁ۱ﮔﮒ",

    "data": {

        "symbol": "000001.SZ",

        "sentiment_score": 0.65,

        "news": [

            {

                "date": "2026-03-15",

                "title": "ﮒﺗﺏﮒ؟ﻠﭘﻟ۰ﻛﺕﻝﭨ۸ﻟﭘﻠ۱ﮔ?,

                "sentiment": 0.8,

                "source": "ﻟﺑ۱ﻝﭨﮔﺍﻠﭨ"

            }

        ]

    }

}

```



---



### 4.2 MLﮒﺓ۴ﮒﺓﺅﺙMLToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_ML_001

**ﻛﺙﮒﻝﭦ?*: P1

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 4 ﮔﭦﮒ۷ﮒ۵ﻛﺗﮒﺎ?

#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **train** | ﻟ؟ﻝﭨﮔ۷۰ﮒ | model_type, features, target | ﻟ؟ﻝﭨﻝﭨﮔ |

| **query** | ﮔ۴ﻟﺁ۱ﮔ۷۰ﮒﻟ۰۷ﻝﺍ | model_id | ﮔ۷۰ﮒﻟ۰۷ﻝﺍ |



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 4.2.1 trainﺅﺙﻟ؟ﻝﭨﮔ۷۰ﮒﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "train",

    "params": {

"model_type": "LSTM",              # ﮒﺟﻠﺅﺙﮔ۷۰ﮒﻝﺎﭨﮒ?        "features": ["momentum", "volume"], # ﮒﺟﻠﺅﺙﻝﺗﮒﺝﮒﻟ۰?        "target": "return_5d",             # ﮒﺟﻠﺅﺙﻝ؟ﮔﮒﻠ?        "train_period": "2020-2025"        # ﮒﺁﻠﺅﺙﻟ؟ﻝﭨﮔﻠﺑ

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

"message": "ﮔ۷۰ﮒﻟ؟ﻝﭨﮔﮒ",

    "data": {

        "model_id": "MODEL_20260402_001",

        "model_type": "LSTM",

        "performance": {

            "train_accuracy": 0.75,

            "val_accuracy": 0.68,

            "test_accuracy": 0.65

        },

        "trained_at": "2026-04-02T10:30:00Z"

    }

}

```



---



### 4.3 ﻝﭨﮒﮒﺓ۴ﮒﺓﺅﺙPortfolioToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_PORTFOLIO_001

**ﻛﺙﮒﻝﭦ?*: P1

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 6 ﻝﭨﮒﮒﺎ?

#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **optimize** | ﻝﭨﮒﻛﺙﮒ | method, constraints | ﻛﺙﮒﻝﭨﮔ |

| **query** | ﮔ۴ﻟﺁ۱ﻝﭨﮒﻠﻝﺛ؟ | ﮔ?| ﻝﭨﮒﻠﻝﺛ؟ |

| **adjust** | ﻟﺍﮔﺑﻝﭨﮒﮔﻠ | symbol, weight | ﻟﺍﮔﺑﻝﭨﮔ |



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 4.3.1 optimizeﺅﺙﻝﭨﮒﻛﺙﮒﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "optimize",

    "params": {

        "method": "mean_variance",    # ﮒﺟﻠﺅﺙﻛﺙﮒﮔﺗﮔﺏ?        "constraints": {              # ﮒﺁﻠﺅﺙﻝﭦ۵ﮔﮔ۰ﻛﭨﭘ

            "max_weight": 0.1,

            "min_weight": 0.01

        }

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

    "message": "ﻝﭨﮒﻛﺙﮒﮔﮒ",

    "data": {

        "optimized_weights": [

            {"symbol": "000001.SZ", "weight": 0.08},

            {"symbol": "600000.SH", "weight": 0.06}

        ],

        "expected_return": 0.12,

        "expected_risk": 0.15,

        "sharpe_ratio": 0.8

    }

}

```



---



### 4.4 ﮔ۴ﮒﮒﺓ۴ﮒﺓﺅﺙReportToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_REPORT_001

**ﻛﺙﮒﻝﭦ?*: P1

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 7 ﮔ۴ﮒﮒﺎ?

#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **query** | ﮔ۴ﻟﺁ۱ﮒﮒﺎﮔ۴ﮒ | report_type, date | ﮔ۴ﮒﮒﮒ؟ﺗ |

| **analyze** | ﮒﺕﮒﭦﮒﮔ | market_scope | ﮒﮔﮔ۴ﮒ |



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 4.4.1 queryﺅﺙﮔ۴ﻟﺁ۱ﮔ۴ﮒﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "query",

    "params": {

        "report_type": "daily",      # ﮒﺟﻠﺅﺙﮔ۴ﮒﻝﺎﭨﮒ?        "date": "2026-04-01"         # ﮒﺁﻠﺅﺙﮔ۴ﮔ

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

    "message": "ﮔ۴ﮒﮔ۴ﻟﺁ۱ﮔﮒ",

    "data": {

        "report_type": "daily",

        "date": "2026-04-01",

        "content": {

            "pnl": 0.02,

            "positions": 5,

            "trades": 3,

            "risk_metrics": {

                "var": 0.05,

                "max_drawdown": 0.08

            }

        }

    }

}

```





## ﻛﭦﻙP2ﮔ۷۰ﮒﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻟ۶ﻟ



### 5.1 ﮔﺍﮔ؟ﮔﭦﮒﺓ۴ﮒﺓﺅﺙDataSourceToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_DATASOURCE_001

**ﻛﺙﮒﻝﭦ?*: P2

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 0 ﮔﺍﮔ؟ﮔﭦﮒﺎ



#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **configure_qmt** | ﻠﻝﺛ؟QMTﮔﺍﮔ؟ﮔﭦ?| account, password | ﻠﻝﺛ؟ﻝﭨﮔ |

| **configure_ifind** | ﻠﻝﺛ؟iFindﮔﺍﮔ؟ﮔﭦ?| account, password | ﻠﻝﺛ؟ﻝﭨﮔ |

| **test_connection** | ﮔﭖﻟﺁﮔﺍﮔ؟ﮔﭦﻟﺟﮔ?| source | ﻟﺟﮔ۴ﻝﭘﮔ?|

| **status** | ﮔ۴ﻟﺁ۱ﮔﺍﮔ؟ﮔﭦﻝﭘﮔ?| ﮔ?| ﻝﭘﮔﻛﺟ۰ﮔ?|



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 5.1.1 configure_qmtﺅﺙﻠﻝﺛ؟QMTﮔﺍﮔ؟ﮔﭦﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "configure_qmt",

    "params": {

"account": "your_account",    # ﮒﺟﻠﺅﺙﻟﺑ۵ﮒ?        "password": "your_password",  # ﮒﺟﻠﺅﺙﮒﺁﻝ?        "server": "127.0.0.1"         # ﮒﺁﻠﺅﺙﮔﮒ۰ﮒ۷ﮒﺍﮒ

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

    "message": "QMTﮔﺍﮔ؟ﮔﭦﻠﻝﺛ؟ﮔﮒ?,

    "data": {

        "source": "QMT",

        "status": "connected",

        "configured_at": "2026-04-02T10:30:00Z"

    }

}

```



---



### 5.2 ﻠ۱ﮒ۳ﻝﮒﺓ۴ﮒﺓﺅﺙPreprocessingToolﺅﺙ?

**ﮔ۷۰ﮒID**: L11_TOOL_PREPROCESSING_001

**ﻛﺙﮒﻝﭦ?*: P2

**ﻟ۵ﻝﮔ۷۰ﮒ**: Layer 1 ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝﮒﺎ



#### ﮔﺁﮔﻝﮔﻛﺛ?

| ﮔﻛﺛ | ﻟﺁﺑﮔ | ﮒﮔﺍ | ﻟﺟﮒﮒ?|

|------|------|------|--------|

| **configure_cleaner** | ﻠﻝﺛ؟ﮔﺕﮔﺑﻟ۶ﮒ | rules | ﻠﻝﺛ؟ﻝﭨﮔ |

| **configure_normalizer** | ﻠﻝﺛ؟ﮔﮒﮒﮔﺗﮔﺏ?| method | ﻠﻝﺛ؟ﻝﭨﮔ |

| **validate** | ﻠ۹ﻟﺁﮔﺍﮔ؟ﻟﺑ۷ﻠ | dataset | ﻠ۹ﻟﺁﻝﭨﮔ |



#### ﮔﻛﺛﻟﺁ۵ﻝﭨﮒ؟ﻛﺗ



##### 5.2.1 configure_cleanerﺅﺙﻠﻝﺛ؟ﮔﺕﮔﺑﻟ۶ﮒﺅﺙ



**ﻟﺝﮒ۴ﮒﮔﺍ**ﺅﺙ?```python

{

    "action": "configure_cleaner",

    "params": {

        "rules": {                    # ﮒﺟﻠﺅﺙﮔﺕﮔﺑﻟ۶ﮒ?            "remove_outliers": True,

            "fill_missing": "mean",

            "remove_duplicates": True

        }

    }

}

```



**ﻟﺝﮒﭦﻝﭨﮔ**ﺅﺙ?```python

{

    "success": True,

    "message": "ﮔﺕﮔﺑﻟ۶ﮒﻠﻝﺛ؟ﮔﮒ",

    "data": {

        "rules": {

            "remove_outliers": True,

            "fill_missing": "mean",

            "remove_duplicates": True

        },

        "configured_at": "2026-04-02T10:30:00Z"

    }

}

```





## ﮒﻙﮒﺓ۴ﮒﺓﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ?

### 6.1 ﮒ؟ﮔﺑﻟﺍﻝ۷ﮔﭖﻝ۷



```python

# ﻝ۷ﮔﺓﻟﺝﮒ۴

user_input = "ﮒﮒﭨﭦﻛﺕﻛﺕ۹ﮒ۷ﻠﻝﻝ۴ﺅﺙﮔﻛﭨ5ﮒ۳۸ﺅﺙﮔ۱ﮔ10%"



# Layer 11ﮒ۳ﻝﮔﭖﻝ۷

agent = QuantTradingAgent()

result = agent.chat(user_input)



# ﮒﻠ۷ﮔﭖﻝ۷

"""

1. AIﻝﻟ۶۲ﮔﮒﺝ: "ﻠﻝﺛ؟ﻝﻝ۴"

2. AIﮔﮒﮒﮔﺍ: {strategy_type: "momentum", holding_period: 5, stop_loss: 0.1}

3. AIﻠﮔ۸ﮒﺓ۴ﮒﺓ: "ﻝﻝ۴ﻝ؟۰ﻝﮒﺓ۴ﮒﺓ"

4. ﻟﺍﻝ۷ﮒﺓ۴ﮒﺓ: StrategyTool.execute({

       "action": "configure",

       "params": {

           "strategy_type": "momentum",

           "holding_period": 5,

           "stop_loss": 0.1

       }

   })

5. ﮒﺓ۴ﮒﺓﮔ۶ﻟ۰: ﻝﻝ۴ﮒﺙﮔ.configure_strategy(...) (ﮔAIﺅﺙﻝﺑﮔ۴ﮔ۶ﻟ۰?

6. AIﮔﺙﮒﺙﮒﻝﭨﮔ? "ﻝﻝ۴ﻠﻝﺛ؟ﮔﮒﺅﺙﻝﻝ۴ID: STRAT_20260402_001"

"""



print(result)

# ﻟﺝﮒﭦ: "ﻝﻝ۴ﻠﻝﺛ؟ﮔﮒﺅﺙﻝﻝ۴ID: STRAT_20260402_001"

```



### 6.2 ﮒ۳ﮔ۴ﻠ۹۳ﮔﻛﺛﻝ۳ﭦﻛﺝ?

```python

# ﻝ۷ﮔﺓﻟﺝﮒ۴

user_input = "ﮔ۴ﻟﺁ۱ﮒ۷ﻠﮒﮒﻝﻟ۰۷ﻝﺍﺅﺙﻝﭘﮒﮒﮒﭨﭦﻛﺕﻛﺕ۹ﻛﺛﺟﻝ۷ﻟﺁ۴ﮒﮒﻝﻝﻝ?



# Layer 11ﮒ۳ﻝﮔﭖﻝ۷

"""

ﮔ۴ﻠ۹۳1: ﮔ۴ﻟﺁ۱ﮒﮒ

- ﮔﮒﺝ: "ﮔ۴ﻟﺁ۱ﮒﮒ"

- ﮒﮔﺍ: {factor_name: "momentum"}

- ﻟﺍﻝ۷: FactorTool.execute({"action": "query", "params": {"factor_name": "momentum"}})

- ﻝﭨﮔ: ﮒﮒIC=0.12ﺅﺙﻟ۰۷ﻝﺍﻟﺁﮒ۴?

ﮔ۴ﻠ۹۳2: ﮒﮒﭨﭦﻝﻝ۴

- ﮔﮒﺝ: "ﻠﻝﺛ؟ﻝﻝ۴"

- ﮒﮔﺍ: {strategy_type: "momentum", factor: "momentum"}

- ﻟﺍﻝ۷: StrategyTool.execute({"action": "configure", "params": {...}})

- ﻝﭨﮔ: ﻝﻝ۴ID: STRAT_20260402_001



AIﮔﺙﮒﺙﮒﻝﭨﮔ? "ﮒ۷ﻠﮒﮒﻟ۰۷ﻝﺍﻟﺁﮒ۴ﺛﺅﺙIC=0.12ﺅﺙﺅﺙﮒﺓﺎﮒﮒﭨﭦﻝﻝ۴STRAT_20260402_001"

"""

```





## ﻛﺕﻙﮒﺓ۴ﮒﺓﮔﺏ۷ﮒﻟ۰۷



### 7.1 ﮒ؟ﮔﺑﮒﺓ۴ﮒﺓﮔﺕﮒ



| ﮒﺓ۴ﮒﺓﮒﻝ۶ﺍ | ﮒﺓ۴ﮒﺓﻝﺎ?| ﻛﺙﮒﻝﭦ?| ﮔﻛﺛﮔﺍﻠ | ﻝﭘﮔ?|

|---------|--------|--------|---------|------|

| ﻝﻝ۴ﻝ؟۰ﻝ | StrategyTool | P0 | 7ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| ﮒﮒﻝ؟۰ﻝ | FactorTool | P0 | 4ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| ﻠ۲ﮔ۶ﻝ؟۰ﻝ | RiskControlTool | P0 | 4ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| ﮔﮔﻝ۰؟ﻟ؟۳ | ApprovalTool | P0 | 3ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| ﻟﮔﮔ۴ﻟﺁ۱ | SentimentTool | P1 | 2ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| ﮔ۷۰ﮒﻟ؟ﻝﭨ | MLTool | P1 | 2ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| ﻝﭨﮒﻛﺙﮒ | PortfolioTool | P1 | 3ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| ﮔ۴ﮒﮔ۴ﻟﺁ۱ | ReportTool | P1 | 2ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| ﮔﺍﮔ؟ﮔﭦﻝ؟۰ﻝ?| DataSourceTool | P2 | 4ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| ﮔﺍﮔ؟ﻠ۱ﮒ۳ﻝ?| PreprocessingTool | P2 | 3ﻛﺕ?| ﻗ?ﮒﺓﺎﻟ؟ﺝﻟ؟?|

| **ﮔﭨﻟ؟۰** | - | - | **34ﻛﺕ۹ﮔﻛﺛ?* | - |



### 7.2 ﻛﺙﮒﻝﭦ۶ﮒﮒﺕ?

| ﻛﺙﮒﻝﭦ?| ﮒﺓ۴ﮒﺓﮔﺍﻠ | ﮔﻛﺛﮔﺍﻠ | ﮒﮔﺁ |

|--------|---------|---------|------|

| P0 | 4ﻛﺕ?| 18ﻛﺕ۹ﮔﻛﺛ?| 53% |

| P1 | 4ﻛﺕ?| 9ﻛﺕ۹ﮔﻛﺛ?| 26% |

| P2 | 2ﻛﺕ?| 7ﻛﺕ۹ﮔﻛﺛ?| 21% |

| **ﮔﭨﻟ؟۰** | **10ﻛﺕ?* | **34ﻛﺕ۹ﮔﻛﺛ?* | **100%** |





## ﮒ،ﻙﮒ؟ﮔﺛﻟﺓﺁﻝﭦﺟﮒﺝ



### Phase 1ﺅﺙP0ﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙWeek 1-2ﺅﺙ?

**ﻝ؟ﮔ**: ﮒ؟ﮔP0ﮒﺓ۴ﮒﺓﮒﺙﮒ?

```yaml

ﮒﺓ۴ﻛﺛﮒﮒ؟ﺗ:

1. ﻝﻝ۴ﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ7ﻛﺕ۹ﮔﻛﺛﺅﺙ

2. ﮒﮒﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ4ﻛﺕ۹ﮔﻛﺛﺅﺙ

  3. ﻠ۲ﮔ۶ﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ4ﻛﺕ۹ﮔﻛﺛﺅﺙ

  4. ﮔﮔﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ3ﻛﺕ۹ﮔﻛﺛﺅﺙ



ﻛﭦ۳ﻛﭨﻝ?

  - 4ﻛﺕ۹ﮒﺓ۴ﮒﺓﮔﻛﭨ?  - 18ﻛﺕ۹ﮔﻛﺛﮒ؟ﻝ?  - ﮒﮒﮔﭖﻟﺁ

```



### Phase 2ﺅﺙP1ﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙWeek 3-4ﺅﺙ?

**ﻝ؟ﮔ**: ﮒ؟ﮔP1ﮒﺓ۴ﮒﺓﮒﺙﮒ?

```yaml

ﮒﺓ۴ﻛﺛﮒﮒ؟ﺗ:

  1. ﻟﮔﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ2ﻛﺕ۹ﮔﻛﺛﺅﺙ

  2. MLﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ2ﻛﺕ۹ﮔﻛﺛﺅﺙ

  3. ﻝﭨﮒﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ3ﻛﺕ۹ﮔﻛﺛﺅﺙ

  4. ﮔ۴ﮒﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ2ﻛﺕ۹ﮔﻛﺛﺅﺙ



ﻛﭦ۳ﻛﭨﻝ?

  - 4ﻛﺕ۹ﮒﺓ۴ﮒﺓﮔﻛﭨ?  - 9ﻛﺕ۹ﮔﻛﺛﮒ؟ﻝ?  - ﻠﮔﮔﭖﻟﺁ

```



### Phase 3ﺅﺙP2ﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙWeek 5-6ﺅﺙ?

**ﻝ؟ﮔ**: ﮒ؟ﮔP2ﮒﺓ۴ﮒﺓﮒﺙﮒ?

```yaml

ﮒﺓ۴ﻛﺛﮒﮒ؟ﺗ:

  1. ﮔﺍﮔ؟ﮔﭦﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ4ﻛﺕ۹ﮔﻛﺛﺅﺙ

  2. ﻠ۱ﮒ۳ﻝﮒﺓ۴ﮒﺓﮒﺙﮒﺅﺙ3ﻛﺕ۹ﮔﻛﺛﺅﺙ



ﻛﭦ۳ﻛﭨﻝ?

  - 2ﻛﺕ۹ﮒﺓ۴ﮒﺓﮔﻛﭨ?  - 7ﻛﺕ۹ﮔﻛﺛﮒ؟ﻝ?  - ﮒ؟ﮔﺑﮔﭖﻟﺁﮒ۴ﻛﭨﭘ

```





## ﻛﺗﻙﮒﺏﻠ؟ﮔﺑﮒﺁ?

### 9.1 ﻝﭨﮒﮒﺎﮔ؛۰ﮔﭨﻝﭨ



| ﮒﺎﻝﭦ۶ | ﻠﻟ۵ﻝﭨﮒ?| ﻛﺕﻠﻟ۵ﻝﭨﮒ?|

|------|---------|-----------|

| **Layer 11** | ﻗ?ﮔﮒﺝﻟﺁﮒ،ﻙﮒﮔﺍﮔﮒﻙﮒﺓ۴ﮒﺓﻟﺓﺁﻝ?| - |

| **ﮒﮔ۷۰ﮒ?* | ﻗ?ﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻟ۶ﻟﺅﺙﮔﻛﺛﻙﮒﮔﺍﻙﻟﺟﮒﮒﺙﺅﺙ | ﻗ?ﮔﮒﻛﭦ۳ﻛﭨﻟ؟ﺝﻟ؟۰ |



### 9.2 ﮔﺕﮒﺟﻛﺙﮒﺟ



| ﻛﺙﮒﺟ | ﻟﺁﺑﮔ |

|------|------|

| **ﻠﺟﮒﻠﮒ۳** | ﻛﺕﻠﻟ۵ﻛﺕﭦﮔﺁﻛﺕ۹ﮔ۷۰ﮒﮒﻝ؛ﮒﮔﮒﻛﭦ۳ﻛﭨﻟ؟ﺝﻟ؟?|

| **ﻝﭨﻛﺕﮔﮒ** | ﮔﮔﮒﺓ۴ﮒﺓﻠﭖﮒﺝ۹ﻝﭨﻛﺕﻝﮔ۴ﮒ۲ﻟ۶ﻟ?|

| **ﮔﻛﭦﮔ۸ﮒﺎ** | ﮔﺍﮒ۱ﮔ۷۰ﮒﮒ۹ﻠﮒ؟ﻛﺗﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ |

| **ﻝﭨﺑﮔ۳ﻝ؟ﮒ?* | ﮒ۹ﻠﻝﭨﺑﮔ۳Layer 11ﻝﮔﮒﺝﻟﺁﮒ،ﻠﭨﻟﺝ |



### 9.3 ﻛﺕﮒ۵ﻛﺕﻛﺕ۹AIﮔﺗﮔ۰ﻝﮒﺁﺗﮔﺁ?

| ﮒﺁﺗﮔﺁﻠ۰?| ﮒ۵ﻛﺕﻛﺕ۹AIﮔﺗﮔ۰ | ﮔ؛ﮔﺗﮔ۰?| ﻛﺙﮒﺟ |

|--------|-------------|--------|------|

| **ﻝﭨﮒﮔﺗﮒﺙ** | ﮔﺁﻛﺕ۹ﮔ۷۰ﮒﮒﻝ؛ﮒﮔﮒﻛﭦ۳ﻛﭨﻟ؟ﺝﻟ؟?| Layer 11ﻝﭨﻛﺕﮔﮒﺝﻟﺁﮒ، + ﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﻟ۶ﻟ | ﻗ?ﻠﺟﮒﻠﮒ۳ |

| **AIﮒﺎﮔﺍﻠ?* | 29ﻛﺕ۹AIﮒﺎ?| 1ﻛﺕ۹AIﮒﺎ?| ﻗ?ﮒﮒﺍ96.6% |

| **ﻝﭨﺑﮔ۳ﮔﮔ؛** | ﻠ،ﺅﺙ29ﮒ۴ﻠﭨﻟﺝﺅﺙ?| ﻛﺛﺅﺙﻝﭨﻛﺕﮔﮒﺅﺙ?| ﻗ?ﮔﺝﻟﻠﻛﺛ |

| **ﮔ۸ﮒﺎﮔ?* | ﮒﺓ؟ﺅﺙﮔﺍﮒ۱ﮔ۷۰ﮒﻠﮔﺍﮒ۱AIﮒﺎﺅﺙ | ﮒ۴ﺛﺅﺙﮔﺍﮒ۱ﮒﺓ۴ﮒﺓﮔ۴ﮒ۲ﮒﺏﮒﺁﺅﺙ?| ﻗ?ﮔﺝﻟﮔﮒ |





## ﮒﻙﻝﺕﮒﺏﮔﮔ۰۲ﻝﺑ۱ﮒﺙ?

### 10.1 ﮔﺕﮒﺟﮒﻟﮔﮔ۰?

| ﮔﮔ۰۲ﮒﻝ۶ﺍ | ﻟﺓﺁﮒﺝ | ﻟﺁﺑﮔ |

|---------|------|------|

| Layer 11ﮒﺓ۴ﮒﺓﮒﺍﻟ۲ﻟﮒﺝ | `docs/module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md` | ﮒﺓ۴ﮒﺓﮒﺍﻟ۲ﮔﭘﮔ |

| Layer 11ﮔﭘﮔﻟﮒﺝ | `docs/module_designs/layer_11/LAYER_11_ARCHITECTURE.md` | Layer 11ﮔﺑﻛﺛﮔﭘﮔ |

| ﮔﮒﻠ۸ﺎﮒ۷ﮔﺕﮒﺟﮔ۷۰ﮒ | `docs/module_designs/layer_11/L11_TEXT_DRIVER.md` | NLUﻟ؟ﺝﻟ؟۰ |

| ﻠﮒﻛﭦ۳ﮔAgentﮔ۷۰ﮒ | `docs/module_designs/layer_11/L11_QUANT_AGENT.md` | Agentﮔ۰ﮔﭘ |



### 10.2 ﻛﭨ۲ﻝﮒ؟ﻝﺍﻛﺛﻝﺛ؟



| ﮔ۷۰ﮒ | ﻟﺓﺁﮒﺝ | ﻟﺁﺑﮔ |

|------|------|------|

| ﮒﺓ۴ﮒﺓﮒﭦﻝﺎﭨ | `src/layer_11/tools/base_tool.py` | ﮒﺓ۴ﮒﺓﮒﭦﻝﺎﭨﮒ؟ﻛﺗ |

| ﻝﻝ۴ﮒﺓ۴ﮒﺓ | `src/layer_11/tools/strategy_tool.py` | ﻝﻝ۴ﮒﺓ۴ﮒﺓﮒ؟ﻝﺍ |

| ﮒﮒﮒﺓ۴ﮒﺓ | `src/layer_11/tools/factor_tool.py` | ﮒﮒﮒﺓ۴ﮒﺓﮒ؟ﻝﺍ |

| ﻠ۲ﮔ۶ﮒﺓ۴ﮒﺓ | `src/layer_11/tools/risk_control_tool.py` | ﻠ۲ﮔ۶ﮒﺓ۴ﮒﺓﮒ؟ﻝﺍ |

| ﮒﺓ۴ﮒﺓﮔﺏ۷ﮒﻛﺕﮒﺟ | `src/layer_11/tools/__init__.py` | ﮒﺓ۴ﮒﺓﮔﺏ۷ﮒﻝ؟۰ﻝ |



---



**ﮔﮔ۰۲ﻝﮔ؛**: v1.0.0

**ﮔﮒﮔﺑﮔ?*: 2026-04-02

**ﻝﭨﺑﮔ۳ﻟ?*: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?