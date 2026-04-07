---
module_id: TECH_SPEC_MARKET_PARTICIPANT_SIM_UPDATE_002
version: 2.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 技术规范、实现标准、接口定义
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ﮔﺑﮔﺍﮔﮔ۰۲
applicable_scope: ﮒﺕﮒﭦﮒﻛﺕﻟﻟ۰ﻛﺕﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨ?compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ./MARKET_PARTICIPANT_SIMULATION_SPEC.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ
---
---


# ﮒﺕﮒﭦﮒﻛﺕﻟﻟ۰ﻛﺕﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ﮔﺑﮔﺍﮔﮔ۰۲
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **ﻝﮔ؛**: v2.0
> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-03
> **ﮔﺑﮔﺍﮒﮒ؟ﺗ**: ﮔﺁﻟﺁ­ﮔ ﮒﮒﻙﻟﭖﻠﮔﭖﮒﻝﮔ۶ﮔ۴ﮒ۲ﻙﮔﭦﻟﺛﻛﺛﮒﮔﺍﻠﻝﺛ؟ﻙﮔﺍﮔ؟ﻟﺓﮒﮔ۷۰ﮒ?> **ﻛﺝﮔ؟ﮔﮔ۰۲**: MARKET_PARTICIPANT_BEHAVIOR_RESEARCH_SUPPLEMENT.md

---

## ﻭ ﻛﺕﻙﮔﺁﻟﺁ­ﮔ ﮒﮒﮔﺑﮔﺍ

### 1.1 ﮔ ﺕﮒﺟﮔﺁﻟﺁ­ﮔﺟﮔ۱ﮒﺁﺗﻝ۶ﻟ۰?
ﮔ ﺗﮔ؟ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﺅﺙﮒﺁﺗﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵ﻛﺕ­ﻝﮔﺁﻟﺁ­ﻟﺟﻟ۰ﮔ ﮒﮒﮔﺑﮔﺍﺅﺙ

| ﮒﮔﺁﻟﺁ?| ﮔﺍﮔﺁﻟﺁ­ﺅﺙﻛﺕﻛﺕﮔ ﮒﺅﺙ?| ﻟﺎﮔﮔﺁﻟﺁ­ | ﮔﺟﮔ۱ﻟﮒﺑ |
|--------|-------------------|---------|---------|
| ﻛﺕﭨﮒ | **ﮔﭦﮔﻟﭖﻠ** | Institutional Capital | ﮒ۷ﮔﮔ۰?|
| ﻛﺕﭨﮒﻟﭖﻠ | **ﮔﭦﮔﻟﭖﻠ** | Institutional Capital | ﮒ۷ﮔﮔ۰?|
| ﻛﺕﭨﮒ/ﮔﺕﺕﻟﭖﮔﭦﻟﺛﻛﺛ?| **ﮔﭦﮔ/ﻝ­ﻠﺎﮔﭦﻟﺛﻛﺛ?* | Institutional/Hot Money Agent | ﮔﭦﻟﺛﻛﺛﮒﻝ۶?|
| ﻛﺕﭨﮒﮔ۶ﻝ | **ﮔﭦﮔﮔ۶ﻝ** | Institutional Control | ﻟ۰ﻛﺕﭦﮔﻟﺟﺍ |
| ﻛﺕﭨﮒﻟ۰ﻛﺕﭦ | **ﮔﭦﮔﻟﭖﻠﻟ۰ﻛﺕﭦ** | Institutional Capital Behavior | ﻝ ﻝ۸ﭘﻠ۱ﮒ |
| ﮒﺛﮒ؟ﭘﻠ?| **ﻛﺕﭨﮔﮒﭦﻠ** | Sovereign Funds | ﮒ­۵ﮔﺁﮒﭦﮔﺁ |
| ﮔﺕﺕﻟﭖ | **ﻝ­ﻠﺎ** | Hot Money | ﻠ۲ﻠ۸ﻝﮔ۶ﮒﭦﮔﺁ |
| ﮔ۲ﮔﺓ | **ﻠﭘﮒ؟ﮔﻟﭖﻟ?* | Retail Investors | ﮒ­۵ﮔﺁﮒﭦﮔﺁ |

### 1.2 ﮔﭦﻟﺛﻛﺛﮒﺛﮒﻟ۶ﻟ?
**ﮔﺑﮔﺍﮒﻝﮔﭦﻟﺛﻛﺛﮒﺛﮒﻛﺛﻝﺏ?*ﺅﺙ?
```
ﻛﺕﻝﭦ۶ﮒﻝﺎﭨﺅﺙﮒ­۵ﮔﺁﮔ ﮒﺅﺙﺅﺙ
ﻗﻗﻗ ﮔﭦﮔﮔﻟﭖﻟﺅﺙInstitutional Investorsﺅﺙ?ﻗ?  ﻗﻗﻗ ﻛﺕﭨﮔﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙSovereign Fund Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.SOVEREIGN_FUND.001
ﻗ?  ﻗﻗﻗ ﮒ؛ﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙMutual Fund Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.MUTUAL_FUND.001
ﻗ?  ﻗﻗﻗ ﻝ۶ﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙPrivate Equity Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻠﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙQuantitative Fund Agentﺅﺙ?ﻗ?  ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.QUANT_FUND.001
ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﺕﭨﻟ۶ﻝ۶ﮒﮔﭦﻟﺛﻛﺛﺅﺙDiscretionary PE Agentﺅﺙ?ﻗ?  ﻗ?      ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.DISCRETIONARY_PE.001
ﻗ?  ﻗﻗﻗ ﮒ۳ﻟﭖﮔﭦﻟﺛﻛﺛﺅﺙForeign Capital Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.FOREIGN_CAPITAL.001
ﻗ?  ﻗﻗﻗ ﻛﺟﻠ۸ﻟﭖﻠﮔﭦﻟﺛﻛﺛﺅﺙInsurance Fund Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.INSURANCE_FUND.001
ﻗ?  ﻗﻗﻗ ﻛﭦ۶ﻛﺕﻟﭖﮔ؛ﮔﭦﻟﺛﻛﺛﺅﺙIndustrial Capital Agentﺅﺙ?ﻗ?      ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.INDUSTRIAL_CAPITAL.001
ﻗﻗﻗ ﻠﭘﮒ؟ﮔﻟﭖﻟﺅﺙRetail Investorsﺅﺙ?    ﻗﻗﻗ ﻠ،ﮒﮒﺙﻛﺕ۹ﻛﭦﭦﮔﭦﻟﺛﻛﺛﺅﺙHigh Net Worth Agentﺅﺙ?    ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.HNW.001
    ﻗﻗﻗ ﮔ۲ﮔﺓﮔﭦﻟﺛﻛﺛﺅﺙRetail Investor Agentﺅﺙ?        ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.RETAIL.001
```

---

## ﻭ ﻛﭦﻙﻟﭖﻠﮔﭖﮒﻝﮔ۶ﮔﮔ ﮔ۴ﮒ۲ﻟ؟ﺝﻟ؟?
### 2.1 DDX/DDE/BBDﮔﺍﮔ؟ﻟﺓﮒﮔ۴ﮒ۲

#### 2.1.1 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

**ﮔ۴ﮒ۲ﮒﻝ۶ﺍ**ﺅﺙCapitalFlowDataFetcher

**ﮔ۴ﮒ۲ID**ﺅﺙINTERFACE.CAPITAL_FLOW.001

**ﮔﺍﮔ؟ﮔﭦ?*ﺅﺙﮒﻟﺎﻠ۰ﭦiFinD

**ﮔﺑﮔﺍﻠ۱ﻝ**ﺅﺙﮒ؟ﮔﭘﺅﺙﻝﻛﺕ­ﺅﺙﻙﮔ۴ﮒﭦ۵ﺅﺙﻝﮒﺅﺙ?
**ﮔ۴ﮒ۲ﻟ۶ﻟ**ﺅﺙ?
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

@dataclass
class DDXIndicator:
    """DDXﮔﮔ ﮔﺍﮔ؟ﻝﭨﮔ
    
    ﻝﺑ۱ﮒﺙ: DATA.DDX.001
    ﮒ؟ﻛﺗ: ﮒ۳۶ﮒﮒ۷ﮒﮔﮔ 
    ﮒ؛ﮒﺙ: DDX = (ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴ + ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴) / ﮔﭖﻠﻝ ﺣ 10000
    """
    stock_code: str
    timestamp: datetime
    ddx_value: float  # DDXﮒ?    ddx_ma5: float  # 5ﮔ۴ﮒﮒ?    ddx_ma10: float  # 10ﮔ۴ﮒﮒ?    ddx_consecutive_days: int  # ﻟﺟﻝﭨ­ﻝﺟﭨﻝﭦ۱/ﻝﺟﭨﻝﭨﺟﮒ۳۸ﮔﺍ
    super_large_net_buy: float  # ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴ﺅﺙﻛﺕﮒﺅﺙ
    large_net_buy: float  # ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴ﺅﺙﻛﺕﮒﺅﺙ
    circulation_cap: float  # ﮔﭖﻠﻝﺅﺙﻛﺕﮒﺅﺙ
    confidence: float  # ﮔﺍﮔ؟ﻝﺛ؟ﻛﺟ۰ﮒﭦ?    
@dataclass
class DDEIndicator:
    """DDEﮒﺏﻝ­ﻝﺏﭨﻝﭨﮔﺍﮔ؟ﻝﭨﮔ
    
    ﻝﺑ۱ﮒﺙ: DATA.DDE.001
    ﮒ؟ﻛﺗ: ﮒ۳۶ﮒﮒﻠﻙﮔ۲ﮔﺓﮔﺍﻠﻙﮒ۳۶ﮒﻠﻠ۱?    """
    stock_code: str
    timestamp: datetime
    large_order_net_ratio: float  # ﮒ۳۶ﮒﮒﻠﺅﺙﮒ ﮔﭖﻠﻝﮔﺁﻝﺅﺙ?    retail_participation: float  # ﮔ۲ﮔﺓﮔﺍﻠﺅﺙﮒﻛﺕﮒﭦ۵ﺅﺙ?    large_order_amount: float  # ﮒ۳۶ﮒﻠﻠ۱ﺅﺙﻛﺕﮒﺅﺙ
    net_inflow_amount: float  # ﮒﮔﭖﮒ۴ﻠﻠ۱ﺅﺙﻛﺕﮒﺅﺙ
    confidence: float

@dataclass
class BBDIndicator:
    """BBDﮔﮔ ﮔﺍﮔ؟ﻝﭨﮔ
    
    ﻝﺑ۱ﮒﺙ: DATA.BBD.001
    ﮒ؟ﻛﺗ: ﻝﺗﮒ۳۶ﮒﻛﺗﺍﮒﮒﺓ؟ﻠ۱?    ﮒ؛ﮒﺙ: BBD = ﻝﺗﮒ۳۶ﮒﮔﭖﮒ۴ﮒﻠﻠﻠ۱?    """
    stock_code: str
    timestamp: datetime
    bbd_value: float  # BBDﮒﺙﺅﺙﻛﺕﮒﺅﺙ?    super_large_inflow: float  # ﻝﺗﮒ۳۶ﮒﮔﭖﮒ۴ﺅﺙﻛﺕﮒﺅﺙ?    super_large_outflow: float  # ﻝﺗﮒ۳۶ﮒﮔﭖﮒﭦﺅﺙﻛﺕﮒﺅﺙ?    total_amount: float  # ﮔﭨﮔﻛﭦ۳ﻠ۱ﺅﺙﻛﺕﮒﺅﺙ
    cannibalization_rate: float  # ﻠﮒﻝ?= BBD / ﮔﻛﭦ۳ﻠ۱?ﺣ 100
    confidence: float

class CapitalFlowDataFetcher(ABC):
    """ﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﻟﺓﮒﮒ۷ﮔﺛﻟﺎ۰ﮒﭦﻝﺎ?    
    ﻝﺑ۱ﮒﺙ: INTERFACE.CAPITAL_FLOW.001
    ﻟﻟﺑ۲: ﻛﭨiFinDﻟﺓﮒDDXﻙDDEﻙBBDﮔﺍﮔ؟
    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD
    """
    
    @abstractmethod
    def fetch_ddx(self, 
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[DDXIndicator]]:
        """ﻟﺓﮒDDXﮔﮔ ﮔﺍﮔ؟
        
        ﮒﮔﺍ:
            stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﮒﻟ۰۷ﺅﺙﮒ۵ ['600519.SH', '000858.SZ']ﺅﺙ?            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ
            
        ﻟﺟﮒ:
            Dict[str, List[DDXIndicator]]: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ  -> DDXﮔﮔ ﮒﻟ۰۷
            
        ﮔﺍﮔ؟ﮔﭦﮔ ﮒﺍ?
            iFinDﮒﺛﮔﺍ: THS_DDX
            ﮒ­ﮔ؟ﭖﮔ ﮒﺍ:
                - ddx_value: DDX
                - super_large_net_buy: ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴
                - large_net_buy: ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴
        """
        pass
    
    @abstractmethod
    def fetch_dde(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[DDEIndicator]]:
        """ﻟﺓﮒDDEﮒﺏﻝ­ﮔﺍﮔ؟
        
        ﮒﮔﺍ:
            stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﮒﻟ۰۷
            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ
            
        ﻟﺟﮒ:
            Dict[str, List[DDEIndicator]]: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ  -> DDEﮔﮔ ﮒﻟ۰۷
            
        ﮔﺍﮔ؟ﮔﭦﮔ ﮒﺍ?
            iFinDﮒﺛﮔﺍ: THS_DDE
            ﮒ­ﮔ؟ﭖﮔ ﮒﺍ:
                - large_order_net_ratio: ﮒ۳۶ﮒﮒﻠ?                - retail_participation: ﮔ۲ﮔﺓﮔﺍﻠ
                - large_order_amount: ﮒ۳۶ﮒﻠﻠ۱
        """
        pass
    
    @abstractmethod
    def fetch_bbd(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[BBDIndicator]]:
        """ﻟﺓﮒBBDﮔﮔ ﮔﺍﮔ؟
        
        ﮒﮔﺍ:
            stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﮒﻟ۰۷
            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ
            
        ﻟﺟﮒ:
            Dict[str, List[BBDIndicator]]: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ  -> BBDﮔﮔ ﮒﻟ۰۷
            
        ﮔﺍﮔ؟ﮔﭦﮔ ﮒﺍ?
            iFinDﮒﺛﮔﺍ: THS_BBD
            ﮒ­ﮔ؟ﭖﮔ ﮒﺍ:
                - bbd_value: BBDﮒ?                - super_large_inflow: ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?                - super_large_outflow: ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?        """
        pass
    
    @abstractmethod
    def fetch_realtime_capital_flow(self,
                                    stock_codes: List[str]) -> Dict[str, Dict]:
        """ﻟﺓﮒﮒ؟ﮔﭘﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﺅﺙﻝﻛﺕ­ﺅﺙ
        
        ﮒﮔﺍ:
            stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﮒﻟ۰۷
            
        ﻟﺟﮒ:
            Dict[str, Dict]: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ  -> ﮒ؟ﮔﭘﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟
            
        ﮔﺑﮔﺍﻠ۱ﻝ:
            ﻝﻛﺕ­: 3ﮒﻠﮒﭨﭘﻟﺟ
            ﻝﮒ: ﮔ۴ﮒﭦ۵ﮔﺑﮔﺍ
        """
        pass
```

#### 2.1.2 iFinDﮒ؟ﻝﺍﻝﺎ?
```python
import THSAPI as ths
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd

class IFindCapitalFlowFetcher(CapitalFlowDataFetcher):
    """iFinDﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﻟﺓﮒﮒ۷ﮒ؟ﻝ?    
    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.IFIND_CAPITAL_FLOW.001
    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD
    ﻛﺝﻟﭖ: THSAPI (iFinD Pythonﮔ۴ﮒ۲)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.ifs_client = ths.THSApi()
        
    def fetch_ddx(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[DDXIndicator]]:
        """ﻟﺓﮒDDXﮔﮔ ﮔﺍﮔ؟
        
        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:
            ths.ED_query(
                'ths_ddx_stock',
                stock_codes,
                'ddx,ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴,ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴',
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
        """
        result = {}
        
        for stock_code in stock_codes:
            try:
                df = self.ifs_client.ED_query(
                    'ths_ddx_stock',
                    stock_code,
                    'ddx,ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴,ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴,ﮔﭖﻠﮒﺕﮒ?,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                indicators = []
                for _, row in df.iterrows():
                    indicator = DDXIndicator(
                        stock_code=stock_code,
                        timestamp=row['time'],
                        ddx_value=row['ddx'],
                        ddx_ma5=self._calculate_ma(row['ddx'], 5),
                        ddx_ma10=self._calculate_ma(row['ddx'], 10),
                        ddx_consecutive_days=self._calculate_consecutive_days(row['ddx']),
                        super_large_net_buy=row['ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴'],
                        large_net_buy=row['ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴'],
                        circulation_cap=row['ﮔﭖﻠﮒﺕﮒ?],
                        confidence=0.95
                    )
                    indicators.append(indicator)
                
                result[stock_code] = indicators
                
            except Exception as e:
                print(f"Error fetching DDX for {stock_code}: {e}")
                result[stock_code] = []
        
        return result
    
    def fetch_dde(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[DDEIndicator]]:
        """ﻟﺓﮒDDEﮒﺏﻝ­ﮔﺍﮔ؟
        
        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:
            ths.ED_query(
                'ths_dde_stock',
                stock_codes,
                'ﮒ۳۶ﮒﮒﻠ?ﮔ۲ﮔﺓﮔﺍﻠ,ﮒ۳۶ﮒﻠﻠ۱',
                start_date,
                end_date
            )
        """
        result = {}
        
        for stock_code in stock_codes:
            try:
                df = self.ifs_client.ED_query(
                    'ths_dde_stock',
                    stock_code,
                    'ﮒ۳۶ﮒﮒﻠ?ﮔ۲ﮔﺓﮔﺍﻠ,ﮒ۳۶ﮒﻠﻠ۱,ﮒﮔﭖﮒ۴ﻠﻠ۱',
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                indicators = []
                for _, row in df.iterrows():
                    indicator = DDEIndicator(
                        stock_code=stock_code,
                        timestamp=row['time'],
                        large_order_net_ratio=row['ﮒ۳۶ﮒﮒﻠ?],
                        retail_participation=row['ﮔ۲ﮔﺓﮔﺍﻠ'],
                        large_order_amount=row['ﮒ۳۶ﮒﻠﻠ۱'],
                        net_inflow_amount=row['ﮒﮔﭖﮒ۴ﻠﻠ۱'],
                        confidence=0.95
                    )
                    indicators.append(indicator)
                
                result[stock_code] = indicators
                
            except Exception as e:
                print(f"Error fetching DDE for {stock_code}: {e}")
                result[stock_code] = []
        
        return result
    
    def fetch_bbd(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[BBDIndicator]]:
        """ﻟﺓﮒBBDﮔﮔ ﮔﺍﮔ؟
        
        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:
            ths.ED_query(
                'ths_bbd_stock',
                stock_codes,
                'BBD,ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?ﮔﭨﮔﻛﭦ۳ﻠ۱',
                start_date,
                end_date
            )
        """
        result = {}
        
        for stock_code in stock_codes:
            try:
                df = self.ifs_client.ED_query(
                    'ths_bbd_stock',
                    stock_code,
                    'BBD,ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?ﮔﭨﮔﻛﭦ۳ﻠ۱',
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                indicators = []
                for _, row in df.iterrows():
                    cannibalization_rate = (row['BBD'] / row['ﮔﭨﮔﻛﭦ۳ﻠ۱'] * 100) if row['ﮔﭨﮔﻛﭦ۳ﻠ۱'] > 0 else 0
                    
                    indicator = BBDIndicator(
                        stock_code=stock_code,
                        timestamp=row['time'],
                        bbd_value=row['BBD'],
                        super_large_inflow=row['ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?],
                        super_large_outflow=row['ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?],
                        total_amount=row['ﮔﭨﮔﻛﭦ۳ﻠ۱'],
                        cannibalization_rate=cannibalization_rate,
                        confidence=0.95
                    )
                    indicators.append(indicator)
                
                result[stock_code] = indicators
                
            except Exception as e:
                print(f"Error fetching BBD for {stock_code}: {e}")
                result[stock_code] = []
        
        return result
    
    def fetch_realtime_capital_flow(self,
                                    stock_codes: List[str]) -> Dict[str, Dict]:
        """ﻟﺓﮒﮒ؟ﮔﭘﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﺅﺙﻝﻛﺕ­ﺅﺙ
        
        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:
            ths.HQ_query(stock_codes, 'ﮔﮔﺍﻛﭨﺓ,ﮔﭘ۷ﻟﺓﮒﺗ?DDX,DDE,BBD')
        """
        result = {}
        
        try:
            df = self.ifs_client.HQ_query(
                stock_codes,
                'ﮔﮔﺍﻛﭨﺓ,ﮔﭘ۷ﻟﺓﮒﺗ?DDX,DDE,BBD,ﻟﭘﮒ۳۶ﮒﮒﮔﭖﮒ۴,ﮒ۳۶ﮒﮒﮔﭖﮒ۴'
            )
            
            for _, row in df.iterrows():
                stock_code = row['ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ']
                result[stock_code] = {
                    'price': row['ﮔﮔﺍﻛﭨﺓ'],
                    'change_pct': row['ﮔﭘ۷ﻟﺓﮒﺗ?],
                    'ddx': row['DDX'],
                    'dde': row['DDE'],
                    'bbd': row['BBD'],
                    'super_large_net_inflow': row['ﻟﭘﮒ۳۶ﮒﮒﮔﭖﮒ۴'],
                    'large_net_inflow': row['ﮒ۳۶ﮒﮒﮔﭖﮒ۴'],
                    'timestamp': datetime.now()
                }
                
        except Exception as e:
            print(f"Error fetching realtime capital flow: {e}")
        
        return result
    
    def _calculate_ma(self, values: pd.Series, window: int) -> float:
        """ﻟ؟۰ﻝ؟ﻝ۶ﭨﮒ۷ﮒﺗﺏﮒ"""
        if len(values) < window:
            return values.mean()
        return values.rolling(window=window).mean().iloc[-1]
    
    def _calculate_consecutive_days(self, ddx_series: pd.Series) -> int:
        """ﻟ؟۰ﻝ؟DDXﻟﺟﻝﭨ­ﻝﺟﭨﻝﭦ۱/ﻝﺟﭨﻝﭨﺟﮒ۳۸ﮔﺍ"""
        if len(ddx_series) == 0:
            return 0
        
        last_value = ddx_series.iloc[-1]
        count = 0
        
        for value in reversed(ddx_series):
            if (last_value > 0 and value > 0) or (last_value < 0 and value < 0):
                count += 1
            else:
                break
        
        return count
```

### 2.2 ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻟ۶۲ﮔﮔ۴ﮒ?
#### 2.2.1 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

```python
@dataclass
class DragonTigerListItem:
    """ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻠ۰ﺗ
    
    ﻝﺑ۱ﮒﺙ: DATA.DRAGON_TIGER.001
    ﮒ؟ﻛﺗ: ﻠﺝﻟﮔ۵ﻛﺗﺍﮒﮔﻝﭨ?    """
    stock_code: str
    stock_name: str
    trade_date: datetime
    close_price: float
    change_pct: float
    turnover_rate: float
    reason: str  # ﻛﺕﮔ۵ﮒﮒ 
    
    buy_seats: List[Dict]  # ﻛﺗﺍﮒ۴ﮒﺕ­ﻛﺛﮒﻟ۰۷
    sell_seats: List[Dict]  # ﮒﮒﭦﮒﺕ­ﻛﺛﮒﻟ۰۷
    
    net_buy_amount: float  # ﮒﻛﺗﺍﮒ۴ﻠﻠ۱ﺅﺙﻛﺕﮒﺅﺙ
    institutional_buy_count: int  # ﮔﭦﮔﻛﺗﺍﮒ۴ﮒﺕ­ﻛﺛﮔﺍﻠ
    institutional_sell_count: int  # ﮔﭦﮔﮒﮒﭦﮒﺕ­ﻛﺛﮔﺍﻠ
    
    hot_money_flag: bool  # ﮔﺁﮒ۵ﮔﻝ۴ﮒﮔﺕﺕﻟﭖ?    institutional_flag: bool  # ﮔﺁﮒ۵ﮔﮔﭦﮔﻛﺕﻝ۷ﮒﺕ­ﻛﺛ?
class DragonTigerDataParser(ABC):
    """ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻟ۶۲ﮔﮒ۷ﮔﺛﻟﺎ۰ﮒﭦﻝﺎﭨ
    
    ﻝﺑ۱ﮒﺙ: INTERFACE.DRAGON_TIGER.001
    ﻟﻟﺑ۲: ﻟ۶۲ﮔﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﺅﺙﻟﺁﮒ،ﮔﭦﮔﮒﺕ­ﻛﺛﮒﮔﺕﺕﻟﭖﮒﺕ­ﻛﺛ?    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinDﻙﻛﭦ۳ﮔﮔﮒ؛ﮒﺙﮔﺍﮔ؟
    """
    
    @abstractmethod
    def fetch_dragon_tiger_list(self,
                                start_date: datetime,
                                end_date: datetime,
                                reason_filter: Optional[List[str]] = None) -> List[DragonTigerListItem]:
        """ﻟﺓﮒﻠﺝﻟﮔ۵ﮒﻟ۰?        
        ﮒﮔﺍ:
            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ
            reason_filter: ﻛﺕﮔ۵ﮒﮒ ﻟﺟﮔﭨ۳ﺅﺙﮒ۵ ['ﮔﭘ۷ﮒ', 'ﻟﺓﮒ', 'ﮔ۱ﮔﻝﮒﺙﮒﺕ?]ﺅﺙ?            
        ﻟﺟﮒ:
            List[DragonTigerListItem]: ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﮒﻟ۰?            
        ﮔﺍﮔ؟ﮔﭦﮔ ﮒﺍ?
            iFinDﮒﺛﮔﺍ: THSﻠﺝﻟﮔ۵?            ﮒ­ﮔ؟ﭖﮔ ﮒﺍ:
                - stock_code: ﻟﺁﮒﺕﻛﭨ۲ﻝ 
                - trade_date: ﻛﭦ۳ﮔﮔ۴ﮔ
                - buy_seats: ﻛﺗﺍﮒ۴ﮒﺕ­ﻛﺛ
                - sell_seats: ﮒﮒﭦﮒﺕ­ﻛﺛ
        """
        pass
    
    @abstractmethod
    def identify_institutional_seats(self,
                                    seats: List[Dict]) -> List[Dict]:
        """ﻟﺁﮒ،ﮔﭦﮔﻛﺕﻝ۷ﮒﺕ­ﻛﺛ
        
        ﮒﮔﺍ:
            seats: ﮒﺕ­ﻛﺛﮒﻟ۰۷
            
        ﻟﺟﮒ:
            List[Dict]: ﮔﭦﮔﮒﺕ­ﻛﺛﮒﻟ۰۷
            
        ﻟﺁﮒ،ﻟ۶ﮒ:
            1. ﮒﺕ­ﻛﺛﮒﻝ۶ﺍﮒﮒ،"ﮔﭦﮔﻛﺕﻝ۷"
            2. ﮒﺕ­ﻛﺛﮒﻝ۶ﺍﮒﮒ،"ﮒ؛ﮒ"ﻙ?ﻝ۳ﺝﻛﺟ"ﻙ?ﻛﺟﻠ۸"
            3. ﮒﺕ­ﻛﺛﻛﭨ۲ﻝ ﻝ؛۵ﮒﮔﭦﮔﮒﺕ­ﻛﺛﻝﺙﻝ ﻟ۶ﮒ
        """
        pass
    
    @abstractmethod
    def identify_hot_money_seats(self,
                                seats: List[Dict]) -> List[Dict]:
        """ﻟﺁﮒ،ﻝ۴ﮒﮔﺕﺕﻟﭖﮒﺕ­ﻛﺛ
        
        ﮒﮔﺍ:
            seats: ﮒﺕ­ﻛﺛﮒﻟ۰۷
            
        ﻟﺟﮒ:
            List[Dict]: ﮔﺕﺕﻟﭖﮒﺕ­ﻛﺛﮒﻟ۰۷
            
        ﻟﺁﮒ،ﻟ۶ﮒ:
            1. ﻝ۴ﮒﮔﺕﺕﻟﭖﻟ۴ﻛﺕﻠ۷ﮒﮒﺅﺙﮒ۵ﺅﺙﮒﻠ،ﻛﺕﮔﭖﺓﮒﮒ؛ﮒﺕﻙﻟﺑ۱ﻠﮔ­ﮒﺓﻛﺛﻟﺎﮒﭦﻟﺓﺁﻝ­ﺅﺙ?            2. ﮒﮒﺎﮔﻛﺛﻠ۲ﮔ ﺙﮒﺗﻠ
        """
        pass
    
    @abstractmethod
    def analyze_institutional_behavior(self,
                                       item: DragonTigerListItem) -> Dict:
        """ﮒﮔﮔﭦﮔﻟﭖﻠﻟ۰ﻛﺕﭦ
        
        ﮒﮔﺍ:
            item: ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻠ۰ﺗ
            
        ﻟﺟﮒ:
            Dict: ﮔﭦﮔﻟ۰ﻛﺕﭦﮒﮔﻝﭨﮔ
            
        ﮒﮔﻝﭨﺑﮒﭦ۵:
            1. ﮔﭦﮔﮒﻛﺗﺍﮒ۴ﻠﻠ۱
            2. ﮔﭦﮔﻛﺗﺍﮒ۴/ﮒﮒﭦﮒﺕ­ﻛﺛﮔﺍﻠﮒﺁﺗﮔﺁ
            3. ﮔﭦﮔﮒﮒﮒﭦ۵ﺅﺙﮒ۳ﮒ؟ﭘﮔﭦﮔﮒﮔﭘﻛﺗﺍﮒ۴ﺅﺙ?            4. ﮔﺕﺕﻟﭖﻛﺕﮔﭦﮔﮒﮒﺙﮔﮒ?        """
        pass
```

#### 2.2.2 iFinDﮒ؟ﻝﺍﻝﺎ?
```python
class IFindDragonTigerParser(DragonTigerDataParser):
    """iFinDﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻟ۶۲ﮔﮒ۷ﮒ؟ﻝﺍ
    
    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.IFIND_DRAGON_TIGER.001
    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.ifs_client = ths.THSApi()
        
        self.known_hot_money_seats = {
            'ﮒﻠ،ﻟﺁﮒﺕﮔﻠﻟﺑ۲ﻛﭨﭨﮒ؛ﮒﺕﻛﺕﮔﭖﺓﮒﮒ؛ﮒ?: 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',
            'ﻟﺑ۱ﻠﻟﺁﮒﺕﻟ۰ﻛﭨﺛﮔﻠﮒ؛ﮒﺕﮔ­ﮒﺓﻛﺛﻟﺎﮒﭦﻟﺓﺁﻟﺁﮒﺕﻟ۴ﻛﺕﻠ۷': 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',
            'ﮒﺛﮔﺏﺍﮒﮒ؟ﻟﺁﮒﺕﻟ۰ﻛﭨﺛﮔﻠﮒ؛ﮒﺕﻛﺕﮔﭖﺓﮒﮒ؛ﮒ?: 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',
            'ﻛﺕ­ﮒﺛﻛﺕ­ﻠﻟﺑ۱ﮒﺁﻟﺁﮒﺕﮔﻠﮒ؛ﮒﺕﮒﻛﭦ؛ﮒﮒ؛ﮒ?: 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',
            'ﮒﮔﺏﺍﻟﺁﮒﺕﻟ۰ﻛﭨﺛﮔﻠﮒ؛ﮒﺕﮔﺓﺎﮒﺏﮒﮒ؛ﮒ?: 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',
        }
    
    def fetch_dragon_tiger_list(self,
                                start_date: datetime,
                                end_date: datetime,
                                reason_filter: Optional[List[str]] = None) -> List[DragonTigerListItem]:
        """ﻟﺓﮒﻠﺝﻟﮔ۵ﮒﻟ۰?        
        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:
            ths.ED_query(
                'thsﻠﺝﻟﮔ۵?,
                '',
                'ﻟﺁﮒﺕﻛﭨ۲ﻝ ,ﻟﺁﮒﺕﻝ؟ﻝ۶?ﻛﭦ۳ﮔﮔ۴ﮔ,ﮔﭘﻝﻛﭨ?ﮔﭘ۷ﻟﺓﮒﺗ?ﮔ۱ﮔﻝ?ﻛﺕﮔ۵ﮒﮒ ,ﻛﺗﺍﮒ۴ﮒﺕ­ﻛﺛ,ﮒﮒﭦﮒﺕ­ﻛﺛ',
                start_date,
                end_date
            )
        """
        items = []
        
        try:
            df = self.ifs_client.ED_query(
                'thsﻠﺝﻟﮔ۵?,
                '',
                'ﻟﺁﮒﺕﻛﭨ۲ﻝ ,ﻟﺁﮒﺕﻝ؟ﻝ۶?ﻛﭦ۳ﮔﮔ۴ﮔ,ﮔﭘﻝﻛﭨ?ﮔﭘ۷ﻟﺓﮒﺗ?ﮔ۱ﮔﻝ?ﻛﺕﮔ۵ﮒﮒ ,ﻛﺗﺍﮒ۴ﮒﺕ­ﻛﺛ,ﮒﮒﭦﮒﺕ­ﻛﺛ',
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if reason_filter:
                df = df[df['ﻛﺕﮔ۵ﮒﮒ '].isin(reason_filter)]
            
            for _, row in df.iterrows():
                buy_seats = self._parse_seats(row['ﻛﺗﺍﮒ۴ﮒﺕ­ﻛﺛ'])
                sell_seats = self._parse_seats(row['ﮒﮒﭦﮒﺕ­ﻛﺛ'])
                
                institutional_buy = self.identify_institutional_seats(buy_seats)
                institutional_sell = self.identify_institutional_seats(sell_seats)
                
                hot_money_buy = self.identify_hot_money_seats(buy_seats)
                hot_money_sell = self.identify_hot_money_seats(sell_seats)
                
                net_buy = sum([seat['ﻛﺗﺍﮒ۴ﻠﻠ۱'] for seat in buy_seats]) - \
                         sum([seat['ﮒﮒﭦﻠﻠ۱'] for seat in sell_seats])
                
                item = DragonTigerListItem(
                    stock_code=row['ﻟﺁﮒﺕﻛﭨ۲ﻝ '],
                    stock_name=row['ﻟﺁﮒﺕﻝ؟ﻝ۶?],
                    trade_date=row['ﻛﭦ۳ﮔﮔ۴ﮔ'],
                    close_price=row['ﮔﭘﻝﻛﭨ?],
                    change_pct=row['ﮔﭘ۷ﻟﺓﮒﺗ?],
                    turnover_rate=row['ﮔ۱ﮔﻝ?],
                    reason=row['ﻛﺕﮔ۵ﮒﮒ '],
                    buy_seats=buy_seats,
                    sell_seats=sell_seats,
                    net_buy_amount=net_buy,
                    institutional_buy_count=len(institutional_buy),
                    institutional_sell_count=len(institutional_sell),
                    hot_money_flag=len(hot_money_buy) > 0 or len(hot_money_sell) > 0,
                    institutional_flag=len(institutional_buy) > 0 or len(institutional_sell) > 0
                )
                
                items.append(item)
                
        except Exception as e:
            print(f"Error fetching dragon tiger list: {e}")
        
        return items
    
    def identify_institutional_seats(self, seats: List[Dict]) -> List[Dict]:
        """ﻟﺁﮒ،ﮔﭦﮔﻛﺕﻝ۷ﮒﺕ­ﻛﺛ"""
        institutional_seats = []
        
        for seat in seats:
            seat_name = seat.get('ﻟ۴ﻛﺕﻠ۷ﮒﻝ۶?, '')
            
            if 'ﮔﭦﮔﻛﺕﻝ۷' in seat_name or \
               'ﮒ؛ﮒ' in seat_name or \
               'ﻝ۳ﺝﻛﺟ' in seat_name or \
               'ﻛﺟﻠ۸' in seat_name or \
               'QFII' in seat_name:
                institutional_seats.append(seat)
        
        return institutional_seats
    
    def identify_hot_money_seats(self, seats: List[Dict]) -> List[Dict]:
        """ﻟﺁﮒ،ﻝ۴ﮒﮔﺕﺕﻟﭖﮒﺕ­ﻛﺛ"""
        hot_money_seats = []
        
        for seat in seats:
            seat_name = seat.get('ﻟ۴ﻛﺕﻠ۷ﮒﻝ۶?, '')
            
            if seat_name in self.known_hot_money_seats:
                hot_money_seats.append(seat)
        
        return hot_money_seats
    
    def analyze_institutional_behavior(self, item: DragonTigerListItem) -> Dict:
        """ﮒﮔﮔﭦﮔﻟﭖﻠﻟ۰ﻛﺕﭦ"""
        institutional_buy_seats = self.identify_institutional_seats(item.buy_seats)
        institutional_sell_seats = self.identify_institutional_seats(item.sell_seats)
        
        institutional_net_buy = sum([seat['ﻛﺗﺍﮒ۴ﻠﻠ۱'] for seat in institutional_buy_seats]) - \
                               sum([seat['ﮒﮒﭦﻠﻠ۱'] for seat in institutional_sell_seats])
        
        hot_money_buy_seats = self.identify_hot_money_seats(item.buy_seats)
        hot_money_sell_seats = self.identify_hot_money_seats(item.sell_seats)
        
        hot_money_net_buy = sum([seat['ﻛﺗﺍﮒ۴ﻠﻠ۱'] for seat in hot_money_buy_seats]) - \
                           sum([seat['ﮒﮒﭦﻠﻠ۱'] for seat in hot_money_sell_seats])
        
        return {
            'stock_code': item.stock_code,
            'trade_date': item.trade_date,
            'institutional_net_buy': institutional_net_buy,
            'institutional_buy_count': len(institutional_buy_seats),
            'institutional_sell_count': len(institutional_sell_seats),
            'institutional_coordination': len(institutional_buy_seats) >= 3,
            'hot_money_net_buy': hot_money_net_buy,
            'institutional_vs_hot_money': 'institutional' if institutional_net_buy > hot_money_net_buy else 'hot_money',
            'signal_strength': self._calculate_signal_strength(
                institutional_net_buy,
                len(institutional_buy_seats),
                item.net_buy_amount
            )
        }
    
    def _parse_seats(self, seats_str: str) -> List[Dict]:
        """ﻟ۶۲ﮔﮒﺕ­ﻛﺛﮒ­ﻝ؛۵ﻛﺕ?""
        seats = []
        
        return seats
    
    def _calculate_signal_strength(self,
                                   institutional_net_buy: float,
                                   institutional_count: int,
                                   total_net_buy: float) -> float:
        """ﻟ؟۰ﻝ؟ﻛﺟ۰ﮒﺓﮒﺙﭦﮒﭦ۵"""
        if total_net_buy == 0:
            return 0.0
        
        ratio = institutional_net_buy / abs(total_net_buy)
        count_bonus = min(institutional_count / 5.0, 1.0)
        
        strength = (ratio * 0.7 + count_bonus * 0.3)
        
        return min(max(strength, 0.0), 1.0)
```

### 2.3 ﮒﮒﻟﭖﻠﻝﮔ۶ﮔ۴ﮒ۲

#### 2.3.1 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

```python
@dataclass
class NorthboundCapitalFlow:
    """ﮒﮒﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﻝﭨﮔ
    
    ﻝﺑ۱ﮒﺙ: DATA.NORTHBOUND.001
    ﮒ؟ﻛﺗ: ﮒﮒﻟﭖﻠﺅﺙﮔﺎ۹ﻟ۰ﻠ?ﮔﺓﺎﻟ۰ﻠﺅﺙﮔﭖﮒﮔﺍﮔ؟
    """
    trade_date: datetime
    shanghai_connect_net_buy: float  # ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴ﺅﺙﻛﭦﺟﮒﺅﺙ
    shenzhen_connect_net_buy: float  # ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴ﺅﺙﻛﭦﺟﮒﺅﺙ
    total_net_buy: float  # ﮔﭨﮒﻛﺗﺍﮒ۴ﺅﺙﻛﭦﺟﮒﺅﺙ
    
    shanghai_connect_balance: float  # ﮔﺎ۹ﻟ۰ﻠﻛﺛﻠ۱ﺅﺙﻛﭦﺟﮒﺅﺙ?    shenzhen_connect_balance: float  # ﮔﺓﺎﻟ۰ﻠﻛﺛﻠ۱ﺅﺙﻛﭦﺟﮒﺅﺙ?    
    top_buy_stocks: List[Dict]  # ﻛﺗﺍﮒ۴ﮒ?0ﻟ۰ﻝ۴۷
    top_sell_stocks: List[Dict]  # ﮒﮒﭦﮒ?0ﻟ۰ﻝ۴۷
    
    sector_allocation: Dict[str, float]  # ﻟ۰ﻛﺕﻠﻝﺛ؟

@dataclass
class NorthboundHolding:
    """ﮒﮒﻟﭖﻠﮔﻛﭨﮔﺍﮔ؟ﻝﭨﮔ
    
    ﻝﺑ۱ﮒﺙ: DATA.NORTHBOUND_HOLDING.001
    ﮒ؟ﻛﺗ: ﮒﮒﻟﭖﻠﮔﻛﭨﮔﻝﭨ
    """
    stock_code: str
    stock_name: str
    hold_amount: float  # ﮔﻟ۰ﮔﺍﻠﺅﺙﻛﺕﻟ۰ﺅﺙ
    hold_value: float  # ﮔﻟ۰ﮒﺕﮒﺙﺅﺙﻛﺕﮒﺅﺙ?    hold_ratio: float  # ﮔﻟ۰ﮒ ﮔﺁﺅﺙ?ﺅﺙ?    change_amount: float  # ﮔﻟ۰ﮒﮒﺅﺙﻛﺕﻟ۰ﺅﺙ
    change_ratio: float  # ﮔﻟ۰ﮒﮒﮔﺁﻛﺝﺅﺙ?ﺅﺙ?
class NorthboundCapitalMonitor(ABC):
    """ﮒﮒﻟﭖﻠﻝﮔ۶ﮒ۷ﮔﺛﻟﺎ۰ﮒﭦﻝﺎ?    
    ﻝﺑ۱ﮒﺙ: INTERFACE.NORTHBOUND.001
    ﻟﻟﺑ۲: ﻝﮔ۶ﮒﮒﻟﭖﻠﮔﭖﮒﮒﮔﻛﭨﮒﮒ?    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinDﻙﮔﺕﺁﻛﭦ۳ﮔﮒ؛ﮒﺙﮔﺍﮔ؟
    """
    
    @abstractmethod
    def fetch_daily_flow(self,
                        start_date: datetime,
                        end_date: datetime) -> List[NorthboundCapitalFlow]:
        """ﻟﺓﮒﮒﮒﻟﭖﻠﮔ۴ﮒﭦ۵ﮔﭖﮒ
        
        ﮒﮔﺍ:
            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ
            
        ﻟﺟﮒ:
            List[NorthboundCapitalFlow]: ﮔ۴ﮒﭦ۵ﮔﭖﮒﮔﺍﮔ؟ﮒﻟ۰۷
            
        ﮔﺍﮔ؟ﮔﭦﮔ ﮒﺍ?
            iFinDﮒﺛﮔﺍ: THSﮒﮒﻟﭖﻠ
            ﮒ­ﮔ؟ﭖﮔ ﮒﺍ:
                - total_net_buy: ﮒﮒﻟﭖﻠﮒﻛﺗﺍﮒ۴
                - shanghai_connect_net_buy: ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴
                - shenzhen_connect_net_buy: ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴
        """
        pass
    
    @abstractmethod
    def fetch_holdings(self,
                      stock_codes: Optional[List[str]] = None,
                      top_n: int = 100) -> List[NorthboundHolding]:
        """ﻟﺓﮒﮒﮒﻟﭖﻠﮔﻛﭨﮔﻝﭨ
        
        ﮒﮔﺍ:
            stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﮒﻟ۰۷ﺅﺙﮒﺁﻠﺅﺙﻠﭨﻟ؟۳ﻟﺟﮒﮒ۷ﻠ۷ﺅﺙ?            top_n: ﻟﺟﮒﮒNﮒ۹ﻟ۰ﻝ۴۷ﺅﺙﻠﭨﻟ؟۳100ﺅﺙ?            
        ﻟﺟﮒ:
            List[NorthboundHolding]: ﮔﻛﭨﮔﻝﭨﮒﻟ۰۷
            
        ﮔﺍﮔ؟ﮔﭦﮔ ﮒﺍ?
            iFinDﮒﺛﮔﺍ: THSﮒﮒﮔﻟ۰
            ﮒ­ﮔ؟ﭖﮔ ﮒﺍ:
                - hold_amount: ﮔﻟ۰ﮔﺍﻠ
                - hold_value: ﮔﻟ۰ﮒﺕﮒ?                - hold_ratio: ﮔﻟ۰ﮒ ﮔﺁ
        """
        pass
    
    @abstractmethod
    def analyze_sector_preference(self,
                                 flow_data: List[NorthboundCapitalFlow]) -> Dict[str, float]:
        """ﮒﮔﮒﮒﻟﭖﻠﻟ۰ﻛﺕﮒﮒ۴ﺛ
        
        ﮒﮔﺍ:
            flow_data: ﮔﭖﮒﮔﺍﮔ؟
            
        ﻟﺟﮒ:
            Dict[str, float]: ﻟ۰ﻛﺕﻠﻝﺛ؟ﮔﺁﻛﺝ
            
        ﮒﮔﮔﺗﮔﺏ:
            1. ﻝﭨﻟ؟۰ﻛﺗﺍﮒ۴/ﮒﮒﭦﮒ?0ﻟ۰ﻝ۴۷ﻝﻟ۰ﻛﺕﮒﮒﺕ?            2. ﻟ؟۰ﻝ؟ﮒﻟ۰ﻛﺕﮒﻛﺗﺍﮒ۴ﻠﻠ۱
            3. ﻟﺁﮒ،ﻟ۰ﻛﺕﻟﺛ؟ﮒ۷ﻟﭘﮒﺟ
        """
        pass
    
    @abstractmethod
    def detect_smart_money_signal(self,
                                 flow_data: List[NorthboundCapitalFlow],
                                 threshold_days: int = 5,
                                 threshold_amount: float = 60.0) -> Dict:
        """ﮔ۲ﮔﭖﻟ۹ﮔﻠﺎﻛﺟ۰ﮒﺓ
        
        ﮒﮔﺍ:
            flow_data: ﮔﭖﮒﮔﺍﮔ؟
            threshold_days: ﻟﺟﻝﭨ­ﮒ۳۸ﮔﺍﻠﮒﺙﺅﺙﻠﭨﻟ؟۳5ﮒ۳۸ﺅﺙ
            threshold_amount: ﮒﻛﺗﺍﮒ۴ﻠﻠ۱ﻠﮒﺙﺅﺙﻠﭨﻟ؟۳60ﻛﭦﺟﮒﺅﺙ?            
        ﻟﺟﮒ:
            Dict: ﻟ۹ﮔﻠﺎﻛﺟ۰ﮒ?            
        ﻛﺟ۰ﮒﺓﻟ۶ﮒ:
            1. ﻟﺟﻝﭨ­5ﮔ۴ﮒﻛﺗﺍﮒ۴ﻟﭘ?0ﻛﭦﺟﮒﺅﺙﮔﺍﻟﺛﮔﭦﻙﻝﭖﮒ­ﮔﺟﮒﻟﻝ?0%
            2. ﮒﮔ۴ﮒﮔﭖﮒﭦﻟﭘ?0ﻛﭦﺟﮒﺅﺙﻠ،ﻛﺙﺍﮒﺙﮔﭘﻟﺑﺗﻟ۰ﮒﺗﺏﮒﮒﮔ۳5.3%
        """
        pass
```

#### 2.3.2 iFinDﮒ؟ﻝﺍﻝﺎ?
```python
class IFindNorthboundCapitalMonitor(NorthboundCapitalMonitor):
    """iFinDﮒﮒﻟﭖﻠﻝﮔ۶ﮒ۷ﮒ؟ﻝ?    
    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.IFIND_NORTHBOUND.001
    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.ifs_client = ths.THSApi()
    
    def fetch_daily_flow(self,
                        start_date: datetime,
                        end_date: datetime) -> List[NorthboundCapitalFlow]:
        """ﻟﺓﮒﮒﮒﻟﭖﻠﮔ۴ﮒﭦ۵ﮔﭖﮒ
        
        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:
            ths.ED_query(
                'thsﮒﮒﻟﭖﻠ',
                '',
                'ﻛﭦ۳ﮔﮔ۴ﮔ,ﮒﮒﻟﭖﻠﮒﻛﺗﺍﮒ۴,ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴,ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴,ﮔﺎ۹ﻟ۰ﻠﻛﺛﻠ۱?ﮔﺓﺎﻟ۰ﻠﻛﺛﻠ۱?,
                start_date,
                end_date
            )
        """
        flows = []
        
        try:
            df = self.ifs_client.ED_query(
                'thsﮒﮒﻟﭖﻠ',
                '',
                'ﻛﭦ۳ﮔﮔ۴ﮔ,ﮒﮒﻟﭖﻠﮒﻛﺗﺍﮒ۴,ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴,ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴,ﮔﺎ۹ﻟ۰ﻠﻛﺛﻠ۱?ﮔﺓﺎﻟ۰ﻠﻛﺛﻠ۱?,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            for _, row in df.iterrows():
                flow = NorthboundCapitalFlow(
                    trade_date=row['ﻛﭦ۳ﮔﮔ۴ﮔ'],
                    shanghai_connect_net_buy=row['ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴'] / 10000,
                    shenzhen_connect_net_buy=row['ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴'] / 10000,
                    total_net_buy=row['ﮒﮒﻟﭖﻠﮒﻛﺗﺍﮒ۴'] / 10000,
                    shanghai_connect_balance=row['ﮔﺎ۹ﻟ۰ﻠﻛﺛﻠ۱?] / 10000,
                    shenzhen_connect_balance=row['ﮔﺓﺎﻟ۰ﻠﻛﺛﻠ۱?] / 10000,
                    top_buy_stocks=self._fetch_top_stocks(row['ﻛﭦ۳ﮔﮔ۴ﮔ'], 'buy'),
                    top_sell_stocks=self._fetch_top_stocks(row['ﻛﭦ۳ﮔﮔ۴ﮔ'], 'sell'),
                    sector_allocation={}
                )
                
                flows.append(flow)
                
        except Exception as e:
            print(f"Error fetching northbound capital flow: {e}")
        
        return flows
    
    def fetch_holdings(self,
                      stock_codes: Optional[List[str]] = None,
                      top_n: int = 100) -> List[NorthboundHolding]:
        """ﻟﺓﮒﮒﮒﻟﭖﻠﮔﻛﭨﮔﻝﭨ
        
        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:
            ths.ED_query(
                'thsﮒﮒﮔﻟ۰',
                '',
                'ﻟﺁﮒﺕﻛﭨ۲ﻝ ,ﻟﺁﮒﺕﻝ؟ﻝ۶?ﮔﻟ۰ﮔﺍﻠ,ﮔﻟ۰ﮒﺕﮒ?ﮔﻟ۰ﮒ ﮔﺁ,ﮔﻟ۰ﮒﮒ,ﮔﻟ۰ﮒﮒﮔﺁﻛﺝ',
                '',
                ''
            )
        """
        holdings = []
        
        try:
            df = self.ifs_client.ED_query(
                'thsﮒﮒﮔﻟ۰',
                '',
                'ﻟﺁﮒﺕﻛﭨ۲ﻝ ,ﻟﺁﮒﺕﻝ؟ﻝ۶?ﮔﻟ۰ﮔﺍﻠ,ﮔﻟ۰ﮒﺕﮒ?ﮔﻟ۰ﮒ ﮔﺁ,ﮔﻟ۰ﮒﮒ,ﮔﻟ۰ﮒﮒﮔﺁﻛﺝ',
                '',
                ''
            )
            
            if stock_codes:
                df = df[df['ﻟﺁﮒﺕﻛﭨ۲ﻝ '].isin(stock_codes)]
            
            df = df.head(top_n)
            
            for _, row in df.iterrows():
                holding = NorthboundHolding(
                    stock_code=row['ﻟﺁﮒﺕﻛﭨ۲ﻝ '],
                    stock_name=row['ﻟﺁﮒﺕﻝ؟ﻝ۶?],
                    hold_amount=row['ﮔﻟ۰ﮔﺍﻠ'],
                    hold_value=row['ﮔﻟ۰ﮒﺕﮒ?],
                    hold_ratio=row['ﮔﻟ۰ﮒ ﮔﺁ'],
                    change_amount=row['ﮔﻟ۰ﮒﮒ'],
                    change_ratio=row['ﮔﻟ۰ﮒﮒﮔﺁﻛﺝ']
                )
                
                holdings.append(holding)
                
        except Exception as e:
            print(f"Error fetching northbound holdings: {e}")
        
        return holdings
    
    def analyze_sector_preference(self,
                                 flow_data: List[NorthboundCapitalFlow]) -> Dict[str, float]:
        """ﮒﮔﮒﮒﻟﭖﻠﻟ۰ﻛﺕﮒﮒ۴ﺛ"""
        sector_allocation = {}
        
        for flow in flow_data:
            for stock in flow.top_buy_stocks:
                sector = stock.get('sector', 'Unknown')
                amount = stock.get('buy_amount', 0)
                
                if sector not in sector_allocation:
                    sector_allocation[sector] = 0
                sector_allocation[sector] += amount
        
        total = sum(sector_allocation.values())
        if total > 0:
            sector_allocation = {k: v / total for k, v in sector_allocation.items()}
        
        return sector_allocation
    
    def detect_smart_money_signal(self,
                                 flow_data: List[NorthboundCapitalFlow],
                                 threshold_days: int = 5,
                                 threshold_amount: float = 60.0) -> Dict:
        """ﮔ۲ﮔﭖﻟ۹ﮔﻠﺎﻛﺟ۰ﮒﺓ"""
        if len(flow_data) < threshold_days:
            return {
                'signal_type': 'INSUFFICIENT_DATA',
                'confidence': 0.0
            }
        
        recent_flows = flow_data[-threshold_days:]
        
        consecutive_buy = all([f.total_net_buy > 0 for f in recent_flows])
        total_buy = sum([f.total_net_buy for f in recent_flows])
        
        if consecutive_buy and total_buy >= threshold_amount:
            return {
                'signal_type': 'STRONG_BUY',
                'total_net_buy': total_buy,
                'consecutive_days': threshold_days,
                'confidence': 0.80,
                'target_sectors': ['ﮔﺍﻟﺛﮔﭦ?, 'ﻝﭖﮒ­'],
                'expected_win_rate': 0.80,
                'reasoning': f'ﮒﮒﻟﭖﻠﻟﺟﻝﭨ­{threshold_days}ﮔ۴ﮒﻛﺗﺍﮒ۴ﻟﭘ{threshold_amount}ﻛﭦﺟﮒﺅﺙﮒﮒﺎﮔﺍﮔ؟ﮔﺝﻝ۳ﭦﮔﺍﻟﺛﮔﭦﻙﻝﭖﮒ­ﮔﺟﮒﻟﻝﻟﺝﺝ80%'
            }
        
        recent_flow = flow_data[-1]
        if recent_flow.total_net_buy < -80:
            return {
                'signal_type': 'RISK_ALERT',
                'net_outflow': abs(recent_flow.total_net_buy),
                'confidence': 0.85,
                'risk_sectors': ['ﻠ،ﻛﺙﺍﮒﺙﮔﭘﻟﺑﺗﻟ۰'],
                'expected_drawdown': 0.053,
                'reasoning': f'ﮒﮒﻟﭖﻠﮒﮔ۴ﮒﮔﭖﮒﭦﻟﭘ?0ﻛﭦﺟﮒﺅﺙﮒﮒﺎﮔﺍﮔ؟ﮔﺝﻝ۳ﭦﻠ،ﻛﺙﺍﮒﺙﮔﭘﻟﺑﺗﻟ۰ﮒﺗﺏﮒﮒﮔ۳5.3%'
            }
        
        return {
            'signal_type': 'NEUTRAL',
            'confidence': 0.50,
            'reasoning': 'ﮒﮒﻟﭖﻠﮔﭖﮒﮔ۹ﻟﺝﺝﮒﺍﮔﺝﻟﻛﺟ۰ﮒﺓﻠﮒ?
        }
    
    def _fetch_top_stocks(self, trade_date: datetime, direction: str) -> List[Dict]:
        """ﻟﺓﮒﻛﺗﺍﮒ۴/ﮒﮒﭦﮒ?0ﻟ۰ﻝ۴۷"""
        stocks = []
        
        return stocks
```

---

## ﻭ۳ ﻛﺕﻙ?ﻝﺎﭨﮔﭦﻟﺛﻛﺛﻟﺁ۵ﻝﭨﮒﮔﺍﻠﻝﺛ؟

### 3.1 ﻛﺕﭨﮔﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙSovereign Fund Agentﺅﺙ?
**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.SOVEREIGN_FUND.001

**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﮒﺕﮒﭦﻝ۷ﺏﮒ؟ﮒ۷ﺅﺙﮔﺟﻝ­ﻠ۸ﺎﮒ۷
- ETFﻠﻝﺛ؟ﻛﺕﭦﻛﺕﭨﺅﺙﻠﺟﮔﮔﮔ?- ﻛﭨﮒ۷ﮒﺕﮒﭦﮒﺙﮒﺕﺕﮔﺏ۱ﮒ۷ﮔﭘﻛﭨﮒ?
**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?
```yaml
sovereign_fund_agent:
  name: "ﻛﺕﭨﮔﮒﭦﻠﮔﭦﻟﺛﻛﺛ?
  type: "institutional_investor"
  
  decision_model:
    type: "rule_engine_llm_hybrid"
    rule_weight: 0.70
    llm_weight: 0.30
    llm_model: "GLM-4-7B-Flash"
  
  intervention_threshold:
    market_drop: -0.05
    volatility_spike: 2.0
    sentiment_panic: -0.8
    liquidity_crisis: 0.3
  
  etf_allocation:
    hs300:
      weight: 0.60
      code: "510300.SH"
      description: "ﮔﺎ۹ﮔﺓﺎ300ETF"
    zz500:
      weight: 0.25
      code: "510500.SH"
      description: "ﻛﺕ­ﻟﺁ500ETF"
    zz1000:
      weight: 0.15
      code: "512100.SH"
      description: "ﻛﺕ­ﻟﺁ1000ETF"
  
  position_limit:
    max_single_etf: 0.05
    max_total: 0.15
  
  holding_period:
    min_days: 90
    avg_days: 180
    max_days: 365
  
  policy_signal_sources:
    - "ﮒ۳؟ﻟ۰ﮒ؛ﮒ"
    - "ﻟﺁﻝﻛﺙﮒ؛ﮒ?
    - "ﮒﺛﮒ۰ﻠ۱ﮔﺟﻝ­ﮔﻛﭨ?
    - "ﮔﺍﮒﻝ۳ﺝﻝ۳ﺝﻟ؟?
  
  market_stability_indicators:
    - "ﮒﺕﮒﭦﮔﺏ۱ﮒ۷ﻝ?
    - "ﮔﭖﮒ۷ﮔ۶ﮔﮔ ?
    - "ﮒﺕﮒﭦﮔﻝﭨ۹ﮔﮔﺍ"
    - "ﻟﻝ­ﺗﻟ۰ﻟﭖﻠﮔﭖﮒ?
  
  reward_function:
    market_stability_weight: 0.50
    policy_alignment_weight: 0.30
    long_term_return_weight: 0.20
  
  risk_control:
    max_intervention_per_day: 1
    cooldown_period: 5
    stop_loss_threshold: -0.10
```

### 3.2 ﮒ؛ﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙMutual Fund Agentﺅﺙ?
**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.MUTUAL_FUND.001

**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻟﭖﻠﻟﻝ۵ﺅﺙﻠ،ﻛﭨﻛﺛﻟﺟﻟ۰
- ﮒﭦﮔ؛ﻠ۱ﻠ۸ﺎﮒ۷ﺅﺙﮔﭦﮔﮒﮒ
- ﮒﺗﺏﮒﻛﭨﻛﺛ86.40%

**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?
```yaml
mutual_fund_agent:
  name: "ﮒ؛ﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛ?
  type: "institutional_investor"
  
  decision_model:
    type: "rl_fundamental_hybrid"
    rl_algorithm: "SAC"
    rl_weight: 0.60
    fundamental_weight: 0.40
  
  sector_focus:
    ai_computing:
      weight: 0.35
      keywords: ["AIﻝ؟ﮒ", "GPU", "ﮔﺍﮔ؟ﻛﺕ­ﮒﺟ"]
      target_stocks: ["ﮔﭖ۹ﮔﺛ؟ﻛﺟ۰ﮔﺁ", "ﻛﺕ­ﻝ۶ﮔﮒ", "ﮒﺁﮔ­۵ﻝﭦ?]
    
    medical_tech:
      weight: 0.25
      keywords: ["ﮒﭨﻝﮔﺍﻝ۶ﮔ", "ﮒﮔﺍﻟ?, "ﮒﭨﻝﮒ۷ﮔ۱ﺍ"]
      target_stocks: ["ﮔﻝﮒﭨﻟﺁ", "ﻟﺟﻝﮒﭨﻝ", "ﻟﺁﮔﮒﭦﺓﮒﺝﺓ"]
    
    humanoid_robot:
      weight: 0.20
      keywords: ["ﻛﭦﭦﮒﺛ۱ﮔﭦﮒ۷ﻛﭦ?, "ﻛﺙﭦﮔﻝﭖﮔﭦ", "ﮒﻠﮒ۷"]
      target_stocks: ["ﻛﺕﻟﺎﮔﭦﮔ۶", "ﮔﺎﮒﺓﮔﮔ?, "ﻝﭨﺟﻝﻟﺍﮔﺏ۱"]
    
    new_energy:
      weight: 0.20
      keywords: ["ﮔﺍﻟﺛﮔﭦ?, "ﮒﻛﺙ", "ﮒ۷ﻟﺛ"]
      target_stocks: ["ﮒ؟ﮒﺝﺓﮔﭘﻛﭨ۲", "ﻠﮒﭦﻝﭨﺟﻟﺛ", "ﮔﺁﻛﭦﻟﺟ?]
  
  fundamental_criteria:
    roe_min: 0.12
    revenue_growth_min: 0.15
    profit_growth_min: 0.20
    debt_ratio_max: 0.60
  
  position_management:
    target_position: 0.8640
    min_position: 0.70
    max_position: 0.95
    rebalance_frequency: "quarterly"
  
  institutional_coordination:
    coordination_threshold: 0.60
    peer_holding_weight: 0.30
  
  holding_period:
    min_days: 30
    avg_days: 90
    max_days: 365
  
  reward_function:
    alpha_return_weight: 0.50
    benchmark_beat_weight: 0.30
    risk_adjusted_return_weight: 0.20
  
  risk_control:
    max_single_stock: 0.10
    max_sector: 0.30
    stop_loss_threshold: -0.15
    max_drawdown: -0.20
```

### 3.3 ﮒ۳ﻟﭖﮔﭦﻟﺛﻛﺛﺅﺙForeign Capital Agentﺅﺙ?
**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.FOREIGN_CAPITAL.001

**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻛﭨﺓﮒﺙﮔﻟﭖﺅﺙﮔﺟﮒﻟﺛ؟ﮒ۷
- ﻟ۹ﮔﻠﺎﮔﮒﭦﺅﺙﻠﺟﮔﻠﻝﺛ؟
- ﮔﺝﮒﺙﻛﺙ ﻝﭨﮔ ﺕﮒﺟﻟﭖﻛﭦ۶ﺅﺙﻟﺛ؛ﮒﻠ،ﮔﻠﺟﮒﭘﻠ?
**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?
```yaml
foreign_capital_agent:
  name: "ﮒ۳ﻟﭖﮔﭦﻟﺛﻛﺛ?
  type: "institutional_investor"
  
  decision_model:
    type: "rl_value_hybrid"
    rl_algorithm: "PPO"
    rl_weight: 0.50
    value_weight: 0.50
  
  value_criteria:
    pe_max: 30
    pb_max: 5
    roe_min: 0.15
    dividend_yield_min: 0.02
  
  sector_rotation:
    growth_manufacturing:
      weight: 0.50
      sectors: ["ﻝﭖﮒ­", "ﮒﭦﻝ۰ﮒﮒﺓ۴", "ﻝﭖﮒﻟ؟ﺝﮒ۳"]
    
    traditional_core:
      weight: 0.20
      sectors: ["ﻠ۲ﮒﻠ۴؟ﮔ", "ﮒﭨﻟﺁ"]
    
    scarce_assets:
      weight: 0.30
      sectors: ["ﻛﺕ­ﻟﺁ", "ﻝﺛﻠ"]
  
  fx_factors:
    usd_cny_weight: 0.30
    dollar_index_weight: 0.20
    risk_premium_weight: 0.20
  
  smart_money_signal:
    consecutive_buy_days: 5
    net_buy_threshold: 60.0
    target_sectors: ["ﮔﺍﻟﺛﮔﭦ?, "ﻝﭖﮒ­"]
    expected_win_rate: 0.80
  
  position_management:
    target_position: 0.85
    min_position: 0.60
    max_position: 0.95
  
  holding_period:
    min_days: 90
    avg_days: 180
    max_days: 730
  
  reward_function:
    long_term_return_weight: 0.50
    value_realization_weight: 0.30
    currency_gain_weight: 0.20
  
  risk_control:
    max_single_stock: 0.08
    max_sector: 0.25
    stop_loss_threshold: -0.20
    fx_hedge_ratio: 0.50
```

### 3.4 ﻠﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙQuantitative Fund Agentﺅﺙ?
**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.QUANT_FUND.001

**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻠ،ﻠ۱ﻛﭦ۳ﮔﺅﺙﻝ؟ﮔﺏﻠ۸ﺎﮒ?- ﮒﮔ۲ﮒﺅﺙﻝﭦ۹ﮒﺝﮔ۶ﮒﺙﭦ
- ﮔﻛﭨﮔﭘﻠﺑﻝ­ﻟﺏﮔﺁ،ﻝ۶ﻝﭦ?
**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?
```yaml
quantitative_fund_agent:
  name: "ﻠﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛ?
  type: "institutional_investor"
  
  decision_model:
    type: "high_frequency_algorithm"
    ai_model: "Transformer-LSTM"
    signal_frequency: "millisecond"
  
  trading_strategy:
    type: "multi_strategy"
    strategies:
      - name: "statistical_arbitrage"
        weight: 0.30
        holding_period: "seconds"
      
      - name: "momentum"
        weight: 0.25
        holding_period: "minutes"
      
      - name: "mean_reversion"
        weight: 0.25
        holding_period: "hours"
      
      - name: "market_making"
        weight: 0.20
        holding_period: "milliseconds"
  
  high_frequency_features:
    - "level2_order_book"
    - "tick_by_tick_trade"
    - "order_flow_imbalance"
    - "volume_weighted_price"
  
  position_management:
    max_single_position: 0.02
    max_total_positions: 100
    leverage_ratio: 2.0
  
  execution:
    algorithm: "TWAP_VWAP_hybrid"
    max_slippage: 0.001
    market_impact_limit: 0.002
  
  risk_control:
    stop_loss_pct: -0.02
    take_profit_pct: 0.03
    max_drawdown: -0.05
    var_limit: 0.01
  
  reward_function:
    sharpe_ratio_weight: 0.40
    alpha_weight: 0.30
    execution_quality_weight: 0.30
  
  infrastructure:
    colocation: true
    latency_requirement: "microsecond"
    data_feed: "level2_realtime"
```

### 3.5 ﻝ­ﻠﺎﮔﭦﻟﺛﻛﺛﺅﺙHot Money Agentﺅﺙ?
**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.HOT_MONEY.001

**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﮔﮔﺟﮔﮔﺏﺅﺙﮒﺟ،ﻟﺟﮒﺟ،ﮒ?- ﻠ۱ﮔﻠ۸ﺎﮒ۷ﺅﺙﮔﻝﭨ۹ﮔﺝﮒ۳?- ﮔﻛﭨﮒ۷ﮔﻝ­ﺅﺙﮔ?ﮒ۷ﺅﺙ

**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?
```yaml
hot_money_agent:
  name: "ﻝ­ﻠﺎﮔﭦﻟﺛﻛﺛ?
  type: "speculator"
  
  decision_model:
    type: "rl_emotion_hybrid"
    rl_algorithm: "DQN"
    rl_weight: 0.60
    emotion_weight: 0.40
  
  limit_up_strategy:
    iron_rules:
      - "no_limit_up_no_buy"
      - "no_volume_surge_no_buy"
      - "no_board_no_stop"
    
    entry_timing:
      - "pre_market_hot_topic"
      - "intraday_breakthrough"
      - "late_afternoon_rally"
    
    exit_strategy:
      - "next_day_sell"
      - "profit_target_5pct"
      - "stop_loss_3pct"
  
  topic_detection:
    hot_keywords:
      - "AI"
      - "ﻛﭦﭦﮒﺛ۱ﮔﭦﮒ۷ﻛﭦ?
      - "ﮔﺍﻟﺛﮔﭦ?
      - "ﮒﺗﭘﻟﺑ­ﻠﻝﭨ"
    
    sentiment_threshold: 0.70
    volume_surge_threshold: 2.0
  
  position_management:
    max_single_position: 0.20
    max_total_positions: 5
    leverage_ratio: 1.5
  
  holding_period:
    min_days: 1
    avg_days: 3
    max_days: 7
  
  reward_function:
    short_term_profit_weight: 0.60
    win_rate_weight: 0.30
    risk_adjusted_return_weight: 0.10
  
  risk_control:
    stop_loss_threshold: -0.05
    take_profit_threshold: 0.10
    max_consecutive_loss: 3
    position_reduce_after_loss: 0.50
```

### 3.6 ﻛﺟﻠ۸ﻟﭖﻠﮔﭦﻟﺛﻛﺛﺅﺙInsurance Fund Agentﺅﺙ?
**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.INSURANCE_FUND.001

**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻠﺟﮔﻠﻝﺛ؟ﺅﺙﻝ۷ﺏﮒ۴ﮔﻟﭖ?- ﻠ،ﻟ۰ﮔﺁﮒﮒ۴ﺛﺅﺙﻠ۲ﻠ۸ﮒﮔﭘ
- ﮔﻛﭨﮒ۷ﮔﻠﺟﺅﺙﮒﺗﺑﮒﭦ۵ﺅﺙ?
**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?
```yaml
insurance_fund_agent:
  name: "ﻛﺟﻠ۸ﻟﭖﻠﮔﭦﻟﺛﻛﺛ?
  type: "institutional_investor"
  
  decision_model:
    type: "rule_engine_value_hybrid"
    rule_weight: 0.60
    value_weight: 0.40
  
  investment_criteria:
    dividend_yield_min: 0.03
    pe_max: 20
    pb_max: 2
    roe_min: 0.10
    market_cap_min: 500
  
  sector_preference:
    banking:
      weight: 0.35
      reason: "ﻠ،ﻟ۰ﮔﺁﻙﻛﺛﻛﺙﺍﮒ?
    
    infrastructure:
      weight: 0.25
      reason: "ﻝﺍﻠﮔﭖﻝ۷ﺏﮒ؟?
    
    real_estate:
      weight: 0.15
      reason: "ﻠﺟﮔﻠﻝﺛ؟"
    
    utilities:
      weight: 0.15
      reason: "ﻠﺎﮒﺝ۰ﮔ۶ﮒﺙﭦ"
    
    other:
      weight: 0.10
  
  position_management:
    target_position: 0.30
    min_position: 0.20
    max_position: 0.40
    rebalance_frequency: "yearly"
  
  holding_period:
    min_days: 365
    avg_days: 730
    max_days: 1825
  
  reward_function:
    dividend_income_weight: 0.40
    capital_preservation_weight: 0.40
    long_term_return_weight: 0.20
  
  risk_control:
    max_single_stock: 0.05
    max_sector: 0.20
    max_drawdown: -0.10
    liquidity_requirement: 0.30
```

### 3.7 ﻛﭦ۶ﻛﺕﻟﭖﮔ؛ﮔﭦﻟﺛﻛﺛﺅﺙIndustrial Capital Agentﺅﺙ?
**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.INDUSTRIAL_CAPITAL.001

**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻛﺟ۰ﮔﺁﻛﺙﮒﺟﺅﺙﮔﻝ۴ﮒﺕﮒﺎ
- ﮒ۱ﮔﮒﻟﺑ­ﺅﺙﻛﭨﺓﮒﺙﻟ؟۳ﮒ?- ﻠﺟﮔﮔﮔ

**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?
```yaml
industrial_capital_agent:
  name: "ﻛﭦ۶ﻛﺕﻟﭖﮔ؛ﮔﭦﻟﺛﻛﺛ?
  type: "institutional_investor"
  
  decision_model:
    type: "rule_engine_strategic_hybrid"
    rule_weight: 0.70
    strategic_weight: 0.30
  
  strategic_focus:
    industry_chain_integration:
      weight: 0.40
      description: "ﻛﭦ۶ﻛﺕﻠﺝﮔﺑﮒ?
    
    technology_acquisition:
      weight: 0.30
      description: "ﮔﮔﺁﻟﺓﮒ?
    
    market_share_expansion:
      weight: 0.30
      description: "ﮒﺕﮒﭦﻛﭨﺛﻠ۱ﮔ۸ﮒﺙ "
  
  buyback_criteria:
    price_below_book: true
    price_below_intrinsic_value: true
    undervaluation_threshold: 0.30
  
  position_management:
    max_single_position: 0.15
    min_holding_period: 365
  
  holding_period:
    min_days: 365
    avg_days: 1095
    max_days: 3650
  
  reward_function:
    strategic_value_weight: 0.50
    long_term_return_weight: 0.30
    market_share_weight: 0.20
  
  risk_control:
    max_single_stock: 0.15
    related_party_transaction_limit: 0.10
```

### 3.8 ﻠﭘﮒ؟ﮔﻟﭖﻟﮔﭦﻟﺛﻛﺛﺅﺙRetail Investor Agentﺅﺙ?
**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.RETAIL.001

**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻝﺝﻝﺝ۳ﮔﮒﭦﺅﺙﮔﻝﭨ۹ﻠ۸ﺎﮒ?- ﻟﺟﺛﮔﭘ۷ﮔﻟﺓﺅﺙﻝ­ﮔﮔﮔ
- ﻛﺟ۰ﮔﺁﮒ۲ﮒﺟ

**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?
```yaml
retail_investor_agent:
  name: "ﻠﭘﮒ؟ﮔﻟﭖﻟﮔﭦﻟﺛﻛﺛ"
  type: "retail_investor"
  
  decision_model:
    type: "behavioral_finance"
    herding_weight: 0.40
    emotion_weight: 0.40
    rational_weight: 0.20
  
  behavioral_biases:
    herding_effect:
      weight: 0.40
      description: "ﻟﺓﻠﻛﺕﭨﮔﭖﻟﭖﻠ"
    
    disposition_effect:
      weight: 0.30
      description: "ﮒﮒﭦﻝﮒ۸ﻟ۰ﺅﺙﮔﮔﻛﭦﮔﻟ?
    
    overconfidence:
      weight: 0.20
      description: "ﻟﺟﮒﭦ۵ﻟ۹ﻛﺟ۰"
    
    loss_aversion:
      weight: 0.10
      description: "ﮔﮒ۳ﺎﮒﮔﭘ"
  
  emotion_indicators:
    fear_greed_index:
      threshold: 0.70
      impact: "buy_when_greedy"
    
    social_media_sentiment:
      weight: 0.30
      sources: ["ﻠ۹ﻝ", "ﻛﺕﮔﺗﻟﺑ۱ﮒﺁﻟ۰ﮒ۶"]
  
  position_management:
    max_single_position: 0.30
    avg_position_count: 5
    leverage_ratio: 1.0
  
  holding_period:
    min_days: 1
    avg_days: 14
    max_days: 90
  
  reward_function:
    short_term_profit_weight: 0.50
    following_trend_weight: 0.30
    avoiding_loss_weight: 0.20
  
  risk_control:
    stop_loss_threshold: -0.10
    take_profit_threshold: 0.20
    max_consecutive_loss: 5
```

---

## ﻭ۵ ﮒﻙﮔﺍﮔ؟ﻟﺓﮒﮔ۷۰ﮒﮒ؟ﮔﺑﮒ؟ﻝ?
### 4.1 ﻝﭨﻛﺕﮔﺍﮔ؟ﻟﺓﮒﮒ?
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

@dataclass
class MarketParticipantDataBundle:
    """ﮒﺕﮒﭦﮒﻛﺕﻟﮔﺍﮔ؟ﮒ
    
    ﻝﺑ۱ﮒﺙ: DATA.BUNDLE.001
    ﻝ۷ﻠ? ﮔﺑﮒﮔﮔﮒﺕﮒﭦﮒﻛﺕﻟﻝﺕﮒﺏﮔﺍﮔ?    """
    timestamp: datetime
    
    capital_flow_data: Dict  # DDX/DDE/BBDﮔﺍﮔ؟
    dragon_tiger_data: List  # ﻠﺝﻟﮔ۵ﮔﺍﮔ?    northbound_flow_data: Dict  # ﮒﮒﻟﭖﻠﮔﭖﮒ
    northbound_holdings: List  # ﮒﮒﻟﭖﻠﮔﻛﭨ
    
    level2_data: Optional[Dict] = None  # Level-2ﻟ۰ﮔ
    sentiment_data: Optional[Dict] = None  # ﮒﺕﮒﭦﮔﻝﭨ۹
    news_data: Optional[List] = None  # ﮔﺍﻠﭨﮔﺍﮔ؟

class MarketParticipantDataFetcher:
    """ﮒﺕﮒﭦﮒﻛﺕﻟﮔﺍﮔ؟ﻝﭨﻛﺕﻟﺓﮒﮒ?    
    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.DATA_FETCHER.001
    ﻟﻟﺑ۲: ﻝﭨﻛﺕﻟﺓﮒﮔﮔﮒﺕﮒﭦﮒﻛﺕﻟﻝﺕﮒﺏﮔﺍﮔ?    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        self.capital_flow_fetcher = IFindCapitalFlowFetcher(config)
        self.dragon_tiger_parser = IFindDragonTigerParser(config)
        self.northbound_monitor = IFindNorthboundCapitalMonitor(config)
    
    def fetch_all_data(self,
                      stock_codes: List[str],
                      start_date: datetime,
                      end_date: datetime) -> MarketParticipantDataBundle:
        """ﻟﺓﮒﮔﮔﮒﺕﮒﭦﮒﻛﺕﻟﮔﺍﮔ?        
        ﮒﮔﺍ:
            stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﮒﻟ۰۷
            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ
            
        ﻟﺟﮒ:
            MarketParticipantDataBundle: ﮔﺑﮒﮔﺍﮔ؟ﮒ?        """
        
        capital_flow_data = self.capital_flow_fetcher.fetch_ddx(
            stock_codes, start_date, end_date
        )
        
        dragon_tiger_data = self.dragon_tiger_parser.fetch_dragon_tiger_list(
            start_date, end_date
        )
        
        northbound_flow_data = self.northbound_monitor.fetch_daily_flow(
            start_date, end_date
        )
        
        northbound_holdings = self.northbound_monitor.fetch_holdings(
            stock_codes=stock_codes
        )
        
        return MarketParticipantDataBundle(
            timestamp=datetime.now(),
            capital_flow_data=capital_flow_data,
            dragon_tiger_data=dragon_tiger_data,
            northbound_flow_data=northbound_flow_data,
            northbound_holdings=northbound_holdings
        )
    
    def fetch_realtime_data(self,
                           stock_codes: List[str]) -> MarketParticipantDataBundle:
        """ﻟﺓﮒﮒ؟ﮔﭘﮔﺍﮔ؟ﺅﺙﻝﻛﺕ­ﺅﺙ
        
        ﮒﮔﺍ:
            stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﮒﻟ۰۷
            
        ﻟﺟﮒ:
            MarketParticipantDataBundle: ﮒ؟ﮔﭘﮔﺍﮔ؟ﮒ?        """
        
        capital_flow_data = self.capital_flow_fetcher.fetch_realtime_capital_flow(
            stock_codes
        )
        
        return MarketParticipantDataBundle(
            timestamp=datetime.now(),
            capital_flow_data=capital_flow_data,
            dragon_tiger_data=[],
            northbound_flow_data={},
            northbound_holdings=[]
        )
```

### 4.2 ﮔﺍﮔ؟ﻝﺙﮒ­ﻛﺕﮔﺑﮔﺍﻝ­ﻝ?
```python
from datetime import datetime, timedelta
from typing import Dict, Optional
import redis
import json

class DataCacheManager:
    """ﮔﺍﮔ؟ﻝﺙﮒ­ﻝ؟۰ﻝﮒ?    
    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.CACHE.001
    ﻟﻟﺑ۲: ﻝ؟۰ﻝﮒﺕﮒﭦﮒﻛﺕﻟﮔﺍﮔ؟ﻝﺙﮒ­?    ﻝﺙﮒ­ﻛﭨﻟﺑ۷: Redis
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        
        self.cache_ttl = {
            'ddx_daily': 86400,
            'ddx_realtime': 180,
            'dragon_tiger': 86400,
            'northbound_flow': 86400,
            'northbound_holdings': 3600
        }
    
    def get_cached_data(self,
                       data_type: str,
                       key: str) -> Optional[Dict]:
        """ﻟﺓﮒﻝﺙﮒ­ﮔﺍﮔ؟
        
        ﮒﮔﺍ:
            data_type: ﮔﺍﮔ؟ﻝﺎﭨﮒﺅﺙddx_daily, ddx_realtimeﻝ­ﺅﺙ
            key: ﻝﺙﮒ­ﻠ?            
        ﻟﺟﮒ:
            Optional[Dict]: ﻝﺙﮒ­ﮔﺍﮔ؟ﺅﺙﻛﺕﮒ­ﮒ۷ﮒﻟﺟﮒNone
        """
        cache_key = f"{data_type}:{key}"
        cached = self.redis_client.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        return None
    
    def set_cached_data(self,
                       data_type: str,
                       key: str,
                       data: Dict) -> None:
        """ﻟ؟ﺝﻝﺛ؟ﻝﺙﮒ­ﮔﺍﮔ؟
        
        ﮒﮔﺍ:
            data_type: ﮔﺍﮔ؟ﻝﺎﭨﮒ
            key: ﻝﺙﮒ­ﻠ?            data: ﮔﺍﮔ؟ﮒﮒ؟ﺗ
        """
        cache_key = f"{data_type}:{key}"
        ttl = self.cache_ttl.get(data_type, 3600)
        
        self.redis_client.setex(
            cache_key,
            ttl,
            json.dumps(data, default=str)
        )
    
    def clear_cache(self, data_type: Optional[str] = None) -> None:
        """ﮔﺕﻠ۳ﻝﺙﮒ­
        
        ﮒﮔﺍ:
            data_type: ﮔﺍﮔ؟ﻝﺎﭨﮒﺅﺙﮒﺁﻠﺅﺙﻛﺕﮔﮒ؟ﮒﮔﺕﻠ۳ﮔﮔﺅﺙ
        """
        if data_type:
            pattern = f"{data_type}:*"
        else:
            pattern = "*"
        
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
```

---

## ﻭ ﻛﭦﻙﻠﮔﮔﭖﻟﺁﻛﺕﻠ۹ﻟﺁ

### 5.1 ﮔﺍﮔ؟ﻟﺓﮒﮔ۴ﮒ۲ﮔﭖﻟﺁﻝ۷ﻛﺝ

```python
import unittest
from datetime import datetime, timedelta

class TestCapitalFlowDataFetcher(unittest.TestCase):
    """ﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﻟﺓﮒﮒ۷ﮔﭖﻟﺁ?""
    
    def setUp(self):
        self.fetcher = IFindCapitalFlowFetcher(config={})
        self.test_stocks = ['600519.SH', '000858.SZ']
        self.test_date = datetime.now() - timedelta(days=7)
        self.end_date = datetime.now()
    
    def test_fetch_ddx(self):
        """ﮔﭖﻟﺁDDXﮔﺍﮔ؟ﻟﺓﮒ"""
        result = self.fetcher.fetch_ddx(
            self.test_stocks,
            self.test_date,
            self.end_date
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('600519.SH', result)
        
        if result['600519.SH']:
            ddx_indicator = result['600519.SH'][0]
            self.assertIsInstance(ddx_indicator, DDXIndicator)
            self.assertIsNotNone(ddx_indicator.ddx_value)
    
    def test_fetch_dde(self):
        """ﮔﭖﻟﺁDDEﮔﺍﮔ؟ﻟﺓﮒ"""
        result = self.fetcher.fetch_dde(
            self.test_stocks,
            self.test_date,
            self.end_date
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('600519.SH', result)
    
    def test_fetch_bbd(self):
        """ﮔﭖﻟﺁBBDﮔﺍﮔ؟ﻟﺓﮒ"""
        result = self.fetcher.fetch_bbd(
            self.test_stocks,
            self.test_date,
            self.end_date
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('600519.SH', result)
    
    def test_fetch_realtime_capital_flow(self):
        """ﮔﭖﻟﺁﮒ؟ﮔﭘﻟﭖﻠﮔﭖﮒﻟﺓﮒ"""
        result = self.fetcher.fetch_realtime_capital_flow(
            self.test_stocks
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('600519.SH', result)

class TestNorthboundCapitalMonitor(unittest.TestCase):
    """ﮒﮒﻟﭖﻠﻝﮔ۶ﮒ۷ﮔﭖﻟﺁ?""
    
    def setUp(self):
        self.monitor = IFindNorthboundCapitalMonitor(config={})
        self.test_date = datetime.now() - timedelta(days=30)
        self.end_date = datetime.now()
    
    def test_fetch_daily_flow(self):
        """ﮔﭖﻟﺁﮔ۴ﮒﭦ۵ﮔﭖﮒﻟﺓﮒ"""
        result = self.monitor.fetch_daily_flow(
            self.test_date,
            self.end_date
        )
        
        self.assertIsInstance(result, list)
        if result:
            flow = result[0]
            self.assertIsInstance(flow, NorthboundCapitalFlow)
            self.assertIsNotNone(flow.total_net_buy)
    
    def test_detect_smart_money_signal(self):
        """ﮔﭖﻟﺁﻟ۹ﮔﻠﺎﻛﺟ۰ﮒﺓﮔ۲ﮔﭖ?""
        flow_data = self.monitor.fetch_daily_flow(
            self.test_date,
            self.end_date
        )
        
        signal = self.monitor.detect_smart_money_signal(flow_data)
        
        self.assertIsInstance(signal, dict)
        self.assertIn('signal_type', signal)
        self.assertIn('confidence', signal)
```

---

## ﻭ ﮒ­ﻙﮔﺑﮔﺍﮔ۴ﮒﺟ?
| ﻝﮔ؛ | ﮔ۴ﮔ | ﮔﺑﮔﺍﮒﮒ؟ﺗ | ﻛﺛﻟ?|
|------|------|----------|------|
| v2.0 | 2026-04-03 | ﮔﺁﻟﺁ­ﮔ ﮒﮒﻙﻟﭖﻠﮔﭖﮒﻝﮔ۶ﮔ۴ﮒ۲ﻙﮔﭦﻟﺛﻛﺛﮒﮔﺍﻠﻝﺛ؟ﻙﮔﺍﮔ؟ﻟﺓﮒﮔ۷۰ﮒ?| Spec-Approver |

---

**ﻝﮔ؛**: v2.0 | **ﮔﺑﮔﺍ**: 2026-04-03 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?