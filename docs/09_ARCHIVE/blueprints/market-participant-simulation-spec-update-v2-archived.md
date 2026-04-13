---
module_id: MARKET_PARTICIPANT_SIMULATION_SPEC_UPDATE_V2_ARCHIVED
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - MARKET_PARTICIPANT_SIMULATION_UPDATE_V2_ARCHIVED技术规范
layer: layer_09
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵ﮔﺑﮔﺍﮔﮔ۰۲
applicable_scope: "ﮒﺕﮒﭦﮒﻛﺕﻟﻟ۰ﻛﺕﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨ?compliance_level: ﻛﺕﻛﺕﮔﮒ"
parent_document: ./MARKET_PARTICIPANT_SIMULATION_SPEC.md
implementation_status: ﻟ؟ﺝﻟ؟۰ﻠﭘﮔ؟ﭖ
---
```
```---
```











# ﮒﺕﮒﭦﮒﻛﺕﻟﻟ۰ﻛﺕﭦﮔ۷۰ﮔﻝﺏﭨﻝﭨﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵ﮔﺑﮔﺍﮔﮔ۰۲



> **核心职责**: 文档内容说明



> **职责边界**: 



> - ✅ 本文档负责：文档内容说明相关内容



> - ❌ 本文档不负责：其他模块内容











> **ﻝﮔ؛**: v2.0



> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-03



> **ﮔﺑﮔﺍﮒﮒ؟ﺗ**: ﮔﺁﻟﺁﮔﮒﮒﻙﻟﭖﻠﮔﭖﮒﻝﮔ۶ﮔ۴ﮒ۲ﻙﮔﭦﻟﺛﻛﺛﮒﮔﺍﻠﻝﺛ؟ﻙﮔﺍﮔ؟ﻟﺓﮒﮔ۷۰ﮒ?> **ﻛﺝﮔ؟ﮔﮔ۰۲**: MARKET_PARTICIPANT_BEHAVIOR_RESEARCH_SUPPLEMENT.md







```
```---
```







## ﻭ ﻛﺕﻙﮔﺁﻟﺁﮔﮒﮒﮔﺑﮔﺍ







### 1.1 ﮔﺕﮒﺟﮔﺁﻟﺁﮔﺟﮔ۱ﮒﺁﺗﻝ۶ﻟ۰?







| ﮒﮔﺁﻟﺁ?| ﮔﺍﮔﺁﻟﺁﺅﺙﻛﺕﻛﺕﮔﮒﺅﺙ?| ﻟﺎﮔﮔﺁﻟﺁ | ﮔﺟﮔ۱ﻟﮒﺑ |



|--------|-------------------|---------|---------|



| ﻛﺕﭨﮒ | **ﮔﭦﮔﻟﭖﻠ** | Institutional Capital | ﮒ۷ﮔﮔ۰?|



| ﻛﺕﭨﮒﻟﭖﻠ | **ﮔﭦﮔﻟﭖﻠ** | Institutional Capital | ﮒ۷ﮔﮔ۰?|



| ﻛﺕﭨﮒ/ﮔﺕﺕﻟﭖﮔﭦﻟﺛﻛﺛ?| **ﮔﭦﮔ/ﻝﻠﺎﮔﭦﻟﺛﻛﺛ?* | Institutional/Hot Money Agent | ﮔﭦﻟﺛﻛﺛﮒﻝ۶?|



| ﻛﺕﭨﮒﮔ۶ﻝ | **ﮔﭦﮔﮔ۶ﻝ** | Institutional Control | ﻟ۰ﻛﺕﭦﮔﻟﺟﺍ |



| ﻛﺕﭨﮒﻟ۰ﻛﺕﭦ | **ﮔﭦﮔﻟﭖﻠﻟ۰ﻛﺕﭦ** | Institutional Capital Behavior | ﻝﻝ۸ﭘﻠ۱ﮒ |



| ﮒﺛﮒ؟ﭘﻠ?| **ﻛﺕﭨﮔﮒﭦﻠ** | Sovereign Funds | ﮒ۵ﮔﺁﮒﭦﮔﺁ |



| ﮔﺕﺕﻟﭖ | **ﻝﻠﺎ** | Hot Money | ﻠ۲ﻠ۸ﻝﮔ۶ﮒﭦﮔﺁ |



| ﮔ۲ﮔﺓ | **ﻠﭘﮒ؟ﮔﻟﭖﻟ?* | Retail Investors | ﮒ۵ﮔﺁﮒﭦﮔﺁ |







### 1.2 ﮔﭦﻟﺛﻛﺛﮒﺛﮒﻟ۶ﻟ?



**ﮔﺑﮔﺍﮒﻝﮔﭦﻟﺛﻛﺛﮒﺛﮒﻛﺛﻝﺏ?*ﺅﺙ?



```



ﻛﺕﻝﭦ۶ﮒﻝﺎﭨﺅﺙﮒ۵ﮔﺁﮔﮒﺅﺙﺅﺙ



ﻗﻗﻗ ﮔﭦﮔﮔﻟﭖﻟﺅﺙInstitutional Investorsﺅﺙ?ﻗ?  ﻗﻗﻗ ﻛﺕﭨﮔﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙSovereign Fund Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.SOVEREIGN_FUND.001



ﻗ?  ﻗﻗﻗ ﮒ؛ﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙMutual Fund Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.MUTUAL_FUND.001



ﻗ?  ﻗﻗﻗ ﻝ۶ﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙPrivate Equity Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻠﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙQuantitative Fund Agentﺅﺙ?ﻗ?  ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.QUANT_FUND.001



ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﺕﭨﻟ۶ﻝ۶ﮒﮔﭦﻟﺛﻛﺛﺅﺙDiscretionary PE Agentﺅﺙ?ﻗ?  ﻗ?      ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.DISCRETIONARY_PE.001



ﻗ?  ﻗﻗﻗ ﮒ۳ﻟﭖﮔﭦﻟﺛﻛﺛﺅﺙForeign Capital Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.FOREIGN_CAPITAL.001



ﻗ?  ﻗﻗﻗ ﻛﺟﻠ۸ﻟﭖﻠﮔﭦﻟﺛﻛﺛﺅﺙInsurance Fund Agentﺅﺙ?ﻗ?  ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.INSURANCE_FUND.001



ﻗ?  ﻗﻗﻗ ﻛﭦ۶ﻛﺕﻟﭖﮔ؛ﮔﭦﻟﺛﻛﺛﺅﺙIndustrial Capital Agentﺅﺙ?ﻗ?      ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.INDUSTRIAL_CAPITAL.001



ﻗﻗﻗ ﻠﭘﮒ؟ﮔﻟﭖﻟﺅﺙRetail Investorsﺅﺙ?    ﻗﻗﻗ ﻠ،ﮒﮒﺙﻛﺕ۹ﻛﭦﭦﮔﭦﻟﺛﻛﺛﺅﺙHigh Net Worth Agentﺅﺙ?    ﻗ?  ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.HNW.001



    ﻗﻗﻗ ﮔ۲ﮔﺓﮔﭦﻟﺛﻛﺛﺅﺙRetail Investor Agentﺅﺙ?        ﻗﻗﻗ ﻛﭨ۲ﮒﺓﺅﺙAGENT.RETAIL.001



```







```
```---
```







## ﻭ ﻛﭦﻙﻟﭖﻠﮔﭖﮒﻝﮔ۶ﮔﮔﮔ۴ﮒ۲ﻟ؟ﺝﻟ؟?



### 2.1 DDX/DDE/BBDﮔﺍﮔ؟ﻟﺓﮒﮔ۴ﮒ۲







#### 2.1.1 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ







**ﮔ۴ﮒ۲ﮒﻝ۶ﺍ**ﺅﺙCapitalFlowDataFetcher







**ﮔ۴ﮒ۲ID**ﺅﺙINTERFACE.CAPITAL_FLOW.001







**ﮔﺍﮔ؟ﮔﭦ?*ﺅﺙﮒﻟﺎﻠ۰ﭦiFinD







**ﮔﺑﮔﺍﻠ۱ﻝ**ﺅﺙﮒ؟ﮔﭘﺅﺙﻝﻛﺕﺅﺙﻙﮔ۴ﮒﭦ۵ﺅﺙﻝﮒﺅﺙ?



**ﮔ۴ﮒ۲ﻟ۶ﻟ**ﺅﺙ?



```python



from abc import ABC, abstractmethod



from dataclasses import dataclass



from datetime import datetime



from typing import List, Dict, Optional



import pandas as pd







@dataclass



class DDXIndicator:



"""DDXﮔﮔﮔﺍﮔ؟ﻝﭨﮔ



    



    ﻝﺑ۱ﮒﺙ: DATA.DDX.001



ﮒ؟ﻛﺗ: ﮒ۳۶ﮒﮒ۷ﮒﮔﮔ



    ﮒ؛ﮒﺙ: DDX = (ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴ + ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴) / ﮔﭖﻠﻝ ﺣ 10000



    """



    stock_code: str



    timestamp: datetime



ddx_value: float  # DDXﮒ?    ddx_ma5: float  # 5ﮔ۴ﮒﮒ?    ddx_ma10: float  # 10ﮔ۴ﮒﮒ?    ddx_consecutive_days: int  # ﻟﺟﻝﭨﻝﺟﭨﻝﭦ۱/ﻝﺟﭨﻝﭨﺟﮒ۳۸ﮔﺍ



    super_large_net_buy: float  # ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴ﺅﺙﻛﺕﮒﺅﺙ



    large_net_buy: float  # ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴ﺅﺙﻛﺕﮒﺅﺙ



    circulation_cap: float  # ﮔﭖﻠﻝﺅﺙﻛﺕﮒﺅﺙ



    confidence: float  # ﮔﺍﮔ؟ﻝﺛ؟ﻛﺟ۰ﮒﭦ?    



@dataclass



class DDEIndicator:



"""DDEﮒﺏﻝﻝﺏﭨﻝﭨﮔﺍﮔ؟ﻝﭨﮔ



    



    ﻝﺑ۱ﮒﺙ: DATA.DDE.001



    ﮒ؟ﻛﺗ: ﮒ۳۶ﮒﮒﻠﻙﮔ۲ﮔﺓﮔﺍﻠﻙﮒ۳۶ﮒﻠﻠ۱?    """



    stock_code: str



    timestamp: datetime



large_order_net_ratio: float  # ﮒ۳۶ﮒﮒﻠﺅﺙﮒﮔﭖﻠﻝﮔﺁﻝﺅﺙ?    retail_participation: float  # ﮔ۲ﮔﺓﮔﺍﻠﺅﺙﮒﻛﺕﮒﭦ۵ﺅﺙ?    large_order_amount: float  # ﮒ۳۶ﮒﻠﻠ۱ﺅﺙﻛﺕﮒﺅﺙ



    net_inflow_amount: float  # ﮒﮔﭖﮒ۴ﻠﻠ۱ﺅﺙﻛﺕﮒﺅﺙ



    confidence: float







@dataclass



class BBDIndicator:



"""BBDﮔﮔﮔﺍﮔ؟ﻝﭨﮔ



    



    ﻝﺑ۱ﮒﺙ: DATA.BBD.001



    ﮒ؟ﻛﺗ: ﻝﺗﮒ۳۶ﮒﻛﺗﺍﮒﮒﺓ؟ﻠ۱?    ﮒ؛ﮒﺙ: BBD = ﻝﺗﮒ۳۶ﮒﮔﭖﮒ۴ﮒﻠﻠﻠ۱?    """



    stock_code: str



    timestamp: datetime



    bbd_value: float  # BBDﮒﺙﺅﺙﻛﺕﮒﺅﺙ?    super_large_inflow: float  # ﻝﺗﮒ۳۶ﮒﮔﭖﮒ۴ﺅﺙﻛﺕﮒﺅﺙ?    super_large_outflow: float  # ﻝﺗﮒ۳۶ﮒﮔﭖﮒﭦﺅﺙﻛﺕﮒﺅﺙ?    total_amount: float  # ﮔﭨﮔﻛﭦ۳ﻠ۱ﺅﺙﻛﺕﮒﺅﺙ



    cannibalization_rate: float  # ﻠﮒﻝ?= BBD / ﮔﻛﭦ۳ﻠ۱?ﺣ 100



    confidence: float







class CapitalFlowDataFetcher(ABC):



    """ﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﻟﺓﮒﮒ۷ﮔﺛﻟﺎ۰ﮒﭦﻝﺎ?    



    ﻝﺑ۱ﮒﺙ: INTERFACE.CAPITAL_FLOW.001



    ﻟﻟﺑ۲: ﻛﭨiFinDﻟﺓﮒDDXﻙDDEﻙBBDﮔﺍﮔ؟



    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD



    """



    



    @abstractmethod



    def fetch_ddx(self, 



                  stock_codes: List[str],



                  start_date: datetime,



                  end_date: datetime) -> Dict[str, List[DDXIndicator]]:



"""ﻟﺓﮒDDXﮔﮔﮔﺍﮔ؟



        



        ﮒﮔﺍ:



stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﮒﻟ۰۷ﺅﺙﮒ۵ ['600519.SH', '000858.SZ']ﺅﺙ?            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ



            



        ﻟﺟﮒ:



Dict[str, List[DDXIndicator]]: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ -> DDXﮔﮔﮒﻟ۰۷



            



ﮔﺍﮔ؟ﮔﭦﮔﮒﺍ?



            iFinDﮒﺛﮔﺍ: THS_DDX



ﮒﮔ؟ﭖﮔﮒﺍ:



                - ddx_value: DDX



                - super_large_net_buy: ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴



                - large_net_buy: ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴



        """



        pass



    



    @abstractmethod



    def fetch_dde(self,



                  stock_codes: List[str],



                  start_date: datetime,



                  end_date: datetime) -> Dict[str, List[DDEIndicator]]:



"""ﻟﺓﮒDDEﮒﺏﻝﮔﺍﮔ؟



        



        ﮒﮔﺍ:



stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﮒﻟ۰۷



            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ



            



        ﻟﺟﮒ:



Dict[str, List[DDEIndicator]]: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ -> DDEﮔﮔﮒﻟ۰۷



            



ﮔﺍﮔ؟ﮔﭦﮔﮒﺍ?



            iFinDﮒﺛﮔﺍ: THS_DDE



ﮒﮔ؟ﭖﮔﮒﺍ:



                - large_order_net_ratio: ﮒ۳۶ﮒﮒﻠ?                - retail_participation: ﮔ۲ﮔﺓﮔﺍﻠ



                - large_order_amount: ﮒ۳۶ﮒﻠﻠ۱



        """



        pass



    



    @abstractmethod



    def fetch_bbd(self,



                  stock_codes: List[str],



                  start_date: datetime,



                  end_date: datetime) -> Dict[str, List[BBDIndicator]]:



"""ﻟﺓﮒBBDﮔﮔﮔﺍﮔ؟



        



        ﮒﮔﺍ:



stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﮒﻟ۰۷



            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ



            



        ﻟﺟﮒ:



Dict[str, List[BBDIndicator]]: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ -> BBDﮔﮔﮒﻟ۰۷



            



ﮔﺍﮔ؟ﮔﭦﮔﮒﺍ?



            iFinDﮒﺛﮔﺍ: THS_BBD



ﮒﮔ؟ﭖﮔﮒﺍ:



                - bbd_value: BBDﮒ?                - super_large_inflow: ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?                - super_large_outflow: ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?        """



        pass



    



    @abstractmethod



    def fetch_realtime_capital_flow(self,



                                    stock_codes: List[str]) -> Dict[str, Dict]:



"""ﻟﺓﮒﮒ؟ﮔﭘﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﺅﺙﻝﻛﺕﺅﺙ



        



        ﮒﮔﺍ:



stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﮒﻟ۰۷



            



        ﻟﺟﮒ:



Dict[str, Dict]: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ -> ﮒ؟ﮔﭘﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟



            



        ﮔﺑﮔﺍﻠ۱ﻝ:



ﻝﻛﺕ: 3ﮒﻠﮒﭨﭘﻟﺟ



            ﻝﮒ: ﮔ۴ﮒﭦ۵ﮔﺑﮔﺍ



        """



        pass



```







#### 2.1.2 iFinDﮒ؟ﻝﺍﻝﺎ?



```python



import THSAPI as ths



from datetime import datetime, timedelta



from typing import List, Dict



import pandas as pd







class IFindCapitalFlowFetcher(CapitalFlowDataFetcher):



    """iFinDﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﻟﺓﮒﮒ۷ﮒ؟ﻝ?    



    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.IFIND_CAPITAL_FLOW.001



    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD



    ﻛﺝﻟﭖ: THSAPI (iFinD Pythonﮔ۴ﮒ۲)



    """



    



    def __init__(self, config: Dict):



        self.config = config



        self.ifs_client = ths.THSApi()



        



    def fetch_ddx(self,



                  stock_codes: List[str],



                  start_date: datetime,



                  end_date: datetime) -> Dict[str, List[DDXIndicator]]:



"""ﻟﺓﮒDDXﮔﮔﮔﺍﮔ؟



        



        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:



            ths.ED_query(



                'ths_ddx_stock',



                stock_codes,



                'ddx,ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴,ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴',



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



                    'ddx,ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴,ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴,ﮔﭖﻠﮒﺕﮒ?,



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



                        super_large_net_buy=row['ﻟﭘﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴'],



                        large_net_buy=row['ﮒ۳۶ﮒﮒﻛﺗﺍﮒ۴'],



                        circulation_cap=row['ﮔﭖﻠﮒﺕﮒ?],



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



"""ﻟﺓﮒDDEﮒﺏﻝﮔﺍﮔ؟



        



        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:



            ths.ED_query(



                'ths_dde_stock',



                stock_codes,



                'ﮒ۳۶ﮒﮒﻠ?ﮔ۲ﮔﺓﮔﺍﻠ,ﮒ۳۶ﮒﻠﻠ۱',



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



                    'ﮒ۳۶ﮒﮒﻠ?ﮔ۲ﮔﺓﮔﺍﻠ,ﮒ۳۶ﮒﻠﻠ۱,ﮒﮔﭖﮒ۴ﻠﻠ۱',



                    start_date.strftime('%Y-%m-%d'),



                    end_date.strftime('%Y-%m-%d')



                )



                



                indicators = []



                for _, row in df.iterrows():



                    indicator = DDEIndicator(



                        stock_code=stock_code,



                        timestamp=row['time'],



                        large_order_net_ratio=row['ﮒ۳۶ﮒﮒﻠ?],



                        retail_participation=row['ﮔ۲ﮔﺓﮔﺍﻠ'],



                        large_order_amount=row['ﮒ۳۶ﮒﻠﻠ۱'],



                        net_inflow_amount=row['ﮒﮔﭖﮒ۴ﻠﻠ۱'],



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



"""ﻟﺓﮒBBDﮔﮔﮔﺍﮔ؟



        



        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:



            ths.ED_query(



                'ths_bbd_stock',



                stock_codes,



                'BBD,ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?ﮔﭨﮔﻛﭦ۳ﻠ۱',



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



                    'BBD,ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?ﮔﭨﮔﻛﭦ۳ﻠ۱',



                    start_date.strftime('%Y-%m-%d'),



                    end_date.strftime('%Y-%m-%d')



                )



                



                indicators = []



                for _, row in df.iterrows():



                    cannibalization_rate = (row['BBD'] / row['ﮔﭨﮔﻛﭦ۳ﻠ۱'] * 100) if row['ﮔﭨﮔﻛﭦ۳ﻠ۱'] > 0 else 0



                    



                    indicator = BBDIndicator(



                        stock_code=stock_code,



                        timestamp=row['time'],



                        bbd_value=row['BBD'],



                        super_large_inflow=row['ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?],



                        super_large_outflow=row['ﻝﺗﮒ۳۶ﮒﮔﭖﮒ?],



                        total_amount=row['ﮔﭨﮔﻛﭦ۳ﻠ۱'],



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



"""ﻟﺓﮒﮒ؟ﮔﭘﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﺅﺙﻝﻛﺕﺅﺙ



        



        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:



            ths.HQ_query(stock_codes, 'ﮔﮔﺍﻛﭨﺓ,ﮔﭘ۷ﻟﺓﮒﺗ?DDX,DDE,BBD')



        """



        result = {}



        



        try:



            df = self.ifs_client.HQ_query(



                stock_codes,



                'ﮔﮔﺍﻛﭨﺓ,ﮔﭘ۷ﻟﺓﮒﺗ?DDX,DDE,BBD,ﻟﭘﮒ۳۶ﮒﮒﮔﭖﮒ۴,ﮒ۳۶ﮒﮒﮔﭖﮒ۴'



            )



            



            for _, row in df.iterrows():



stock_code = row['ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ']



                result[stock_code] = {



                    'price': row['ﮔﮔﺍﻛﭨﺓ'],



                    'change_pct': row['ﮔﭘ۷ﻟﺓﮒﺗ?],



                    'ddx': row['DDX'],



                    'dde': row['DDE'],



                    'bbd': row['BBD'],



                    'super_large_net_inflow': row['ﻟﭘﮒ۳۶ﮒﮒﮔﭖﮒ۴'],



                    'large_net_inflow': row['ﮒ۳۶ﮒﮒﮔﭖﮒ۴'],



                    'timestamp': datetime.now()



                }



                



        except Exception as e:



            print(f"Error fetching realtime capital flow: {e}")



        



        return result



    



    def _calculate_ma(self, values: pd.Series, window: int) -> float:



        """ﻟ؟۰ﻝ؟ﻝ۶ﭨﮒ۷ﮒﺗﺏﮒ"""



        if len(values) < window:



            return values.mean()



        return values.rolling(window=window).mean().iloc[-1]



    



    def _calculate_consecutive_days(self, ddx_series: pd.Series) -> int:



"""ﻟ؟۰ﻝ؟DDXﻟﺟﻝﭨﻝﺟﭨﻝﭦ۱/ﻝﺟﭨﻝﭨﺟﮒ۳۸ﮔﺍ"""



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







### 2.2 ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻟ۶۲ﮔﮔ۴ﮒ?



#### 2.2.1 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ







```python



@dataclass



class DragonTigerListItem:



    """ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻠ۰ﺗ



    



    ﻝﺑ۱ﮒﺙ: DATA.DRAGON_TIGER.001



    ﮒ؟ﻛﺗ: ﻠﺝﻟﮔ۵ﻛﺗﺍﮒﮔﻝﭨ?    """



    stock_code: str



    stock_name: str



    trade_date: datetime



    close_price: float



    change_pct: float



    turnover_rate: float



reason: str  # ﻛﺕﮔ۵ﮒﮒ



    



buy_seats: List[Dict]  # ﻛﺗﺍﮒ۴ﮒﺕﻛﺛﮒﻟ۰۷



sell_seats: List[Dict]  # ﮒﮒﭦﮒﺕﻛﺛﮒﻟ۰۷



    



    net_buy_amount: float  # ﮒﻛﺗﺍﮒ۴ﻠﻠ۱ﺅﺙﻛﺕﮒﺅﺙ



institutional_buy_count: int  # ﮔﭦﮔﻛﺗﺍﮒ۴ﮒﺕﻛﺛﮔﺍﻠ



institutional_sell_count: int  # ﮔﭦﮔﮒﮒﭦﮒﺕﻛﺛﮔﺍﻠ



    



hot_money_flag: bool  # ﮔﺁﮒ۵ﮔﻝ۴ﮒﮔﺕﺕﻟﭖ?    institutional_flag: bool  # ﮔﺁﮒ۵ﮔﮔﭦﮔﻛﺕﻝ۷ﮒﺕﻛﺛ?



class DragonTigerDataParser(ABC):



    """ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻟ۶۲ﮔﮒ۷ﮔﺛﻟﺎ۰ﮒﭦﻝﺎﭨ



    



    ﻝﺑ۱ﮒﺙ: INTERFACE.DRAGON_TIGER.001



ﻟﻟﺑ۲: ﻟ۶۲ﮔﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﺅﺙﻟﺁﮒ،ﮔﭦﮔﮒﺕﻛﺛﮒﮔﺕﺕﻟﭖﮒﺕﻛﺛ?    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinDﻙﻛﭦ۳ﮔﮔﮒ؛ﮒﺙﮔﺍﮔ؟



    """



    



    @abstractmethod



    def fetch_dragon_tiger_list(self,



                                start_date: datetime,



                                end_date: datetime,



                                reason_filter: Optional[List[str]] = None) -> List[DragonTigerListItem]:



        """ﻟﺓﮒﻠﺝﻟﮔ۵ﮒﻟ۰?        



        ﮒﮔﺍ:



            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ



reason_filter: ﻛﺕﮔ۵ﮒﮒﻟﺟﮔﭨ۳ﺅﺙﮒ۵ ['ﮔﭘ۷ﮒ', 'ﻟﺓﮒ', 'ﮔ۱ﮔﻝﮒﺙﮒﺕ?]ﺅﺙ?



        ﻟﺟﮒ:



            List[DragonTigerListItem]: ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﮒﻟ۰?            



ﮔﺍﮔ؟ﮔﭦﮔﮒﺍ?



iFinDﮒﺛﮔﺍ: THSﻠﺝﻟﮔ۵?            ﮒﮔ؟ﭖﮔﮒﺍ:



- stock_code: ﻟﺁﮒﺕﻛﭨ۲ﻝ



                - trade_date: ﻛﭦ۳ﮔﮔ۴ﮔ



- buy_seats: ﻛﺗﺍﮒ۴ﮒﺕﻛﺛ



- sell_seats: ﮒﮒﭦﮒﺕﻛﺛ



        """



        pass



    



    @abstractmethod



    def identify_institutional_seats(self,



                                    seats: List[Dict]) -> List[Dict]:



"""ﻟﺁﮒ،ﮔﭦﮔﻛﺕﻝ۷ﮒﺕﻛﺛ



        



        ﮒﮔﺍ:



seats: ﮒﺕﻛﺛﮒﻟ۰۷



            



        ﻟﺟﮒ:



List[Dict]: ﮔﭦﮔﮒﺕﻛﺛﮒﻟ۰۷



            



        ﻟﺁﮒ،ﻟ۶ﮒ:



1. ﮒﺕﻛﺛﮒﻝ۶ﺍﮒﮒ،"ﮔﭦﮔﻛﺕﻝ۷"



2. ﮒﺕﻛﺛﮒﻝ۶ﺍﮒﮒ،"ﮒ؛ﮒ"ﻙ?ﻝ۳ﺝﻛﺟ"ﻙ?ﻛﺟﻠ۸"



3. ﮒﺕﻛﺛﻛﭨ۲ﻝﻝ؛۵ﮒﮔﭦﮔﮒﺕﻛﺛﻝﺙﻝﻟ۶ﮒ



        """



        pass



    



    @abstractmethod



    def identify_hot_money_seats(self,



                                seats: List[Dict]) -> List[Dict]:



"""ﻟﺁﮒ،ﻝ۴ﮒﮔﺕﺕﻟﭖﮒﺕﻛﺛ



        



        ﮒﮔﺍ:



seats: ﮒﺕﻛﺛﮒﻟ۰۷



            



        ﻟﺟﮒ:



List[Dict]: ﮔﺕﺕﻟﭖﮒﺕﻛﺛﮒﻟ۰۷



            



        ﻟﺁﮒ،ﻟ۶ﮒ:



1. ﻝ۴ﮒﮔﺕﺕﻟﭖﻟ۴ﻛﺕﻠ۷ﮒﮒﺅﺙﮒ۵ﺅﺙﮒﻠ،ﻛﺕﮔﭖﺓﮒﮒ؛ﮒﺕﻙﻟﺑ۱ﻠﮔﮒﺓﻛﺛﻟﺎﮒﭦﻟﺓﺁﻝﺅﺙ?            2. ﮒﮒﺎﮔﻛﺛﻠ۲ﮔﺙﮒﺗﻠ



        """



        pass



    



    @abstractmethod



    def analyze_institutional_behavior(self,



                                       item: DragonTigerListItem) -> Dict:



        """ﮒﮔﮔﭦﮔﻟﭖﻠﻟ۰ﻛﺕﭦ



        



        ﮒﮔﺍ:



            item: ﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻠ۰ﺗ



            



        ﻟﺟﮒ:



            Dict: ﮔﭦﮔﻟ۰ﻛﺕﭦﮒﮔﻝﭨﮔ



            



        ﮒﮔﻝﭨﺑﮒﭦ۵:



            1. ﮔﭦﮔﮒﻛﺗﺍﮒ۴ﻠﻠ۱



2. ﮔﭦﮔﻛﺗﺍﮒ۴/ﮒﮒﭦﮒﺕﻛﺛﮔﺍﻠﮒﺁﺗﮔﺁ



            3. ﮔﭦﮔﮒﮒﮒﭦ۵ﺅﺙﮒ۳ﮒ؟ﭘﮔﭦﮔﮒﮔﭘﻛﺗﺍﮒ۴ﺅﺙ?            4. ﮔﺕﺕﻟﭖﻛﺕﮔﭦﮔﮒﮒﺙﮔﮒ?        """



        pass



```







#### 2.2.2 iFinDﮒ؟ﻝﺍﻝﺎ?



```python



class IFindDragonTigerParser(DragonTigerDataParser):



    """iFinDﻠﺝﻟﮔ۵ﮔﺍﮔ؟ﻟ۶۲ﮔﮒ۷ﮒ؟ﻝﺍ



    



    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.IFIND_DRAGON_TIGER.001



    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD



    """



    



    def __init__(self, config: Dict):



        self.config = config



        self.ifs_client = ths.THSApi()



        



        self.known_hot_money_seats = {



            'ﮒﻠ،ﻟﺁﮒﺕﮔﻠﻟﺑ۲ﻛﭨﭨﮒ؛ﮒﺕﻛﺕﮔﭖﺓﮒﮒ؛ﮒ?: 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',



'ﻟﺑ۱ﻠﻟﺁﮒﺕﻟ۰ﻛﭨﺛﮔﻠﮒ؛ﮒﺕﮔﮒﺓﻛﺛﻟﺎﮒﭦﻟﺓﺁﻟﺁﮒﺕﻟ۴ﻛﺕﻠ۷': 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',



            'ﮒﺛﮔﺏﺍﮒﮒ؟ﻟﺁﮒﺕﻟ۰ﻛﭨﺛﮔﻠﮒ؛ﮒﺕﻛﺕﮔﭖﺓﮒﮒ؛ﮒ?: 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',



'ﻛﺕﮒﺛﻛﺕﻠﻟﺑ۱ﮒﺁﻟﺁﮒﺕﮔﻠﮒ؛ﮒﺕﮒﻛﭦ؛ﮒﮒ؛ﮒ?: 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',



            'ﮒﮔﺏﺍﻟﺁﮒﺕﻟ۰ﻛﭨﺛﮔﻠﮒ؛ﮒﺕﮔﺓﺎﮒﺏﮒﮒ؛ﮒ?: 'ﻝ۴ﮒﮔﺕﺕﻟﭖ',



        }



    



    def fetch_dragon_tiger_list(self,



                                start_date: datetime,



                                end_date: datetime,



                                reason_filter: Optional[List[str]] = None) -> List[DragonTigerListItem]:



        """ﻟﺓﮒﻠﺝﻟﮔ۵ﮒﻟ۰?        



        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:



            ths.ED_query(



                'thsﻠﺝﻟﮔ۵?,



                '',



'ﻟﺁﮒﺕﻛﭨ۲ﻝ,ﻟﺁﮒﺕﻝ؟ﻝ۶?ﻛﭦ۳ﮔﮔ۴ﮔ,ﮔﭘﻝﻛﭨ?ﮔﭘ۷ﻟﺓﮒﺗ?ﮔ۱ﮔﻝ?ﻛﺕﮔ۵ﮒﮒ,ﻛﺗﺍﮒ۴ﮒﺕﻛﺛ,ﮒﮒﭦﮒﺕﻛﺛ',



                start_date,



                end_date



            )



        """



        items = []



        



        try:



            df = self.ifs_client.ED_query(



                'thsﻠﺝﻟﮔ۵?,



                '',



'ﻟﺁﮒﺕﻛﭨ۲ﻝ,ﻟﺁﮒﺕﻝ؟ﻝ۶?ﻛﭦ۳ﮔﮔ۴ﮔ,ﮔﭘﻝﻛﭨ?ﮔﭘ۷ﻟﺓﮒﺗ?ﮔ۱ﮔﻝ?ﻛﺕﮔ۵ﮒﮒ,ﻛﺗﺍﮒ۴ﮒﺕﻛﺛ,ﮒﮒﭦﮒﺕﻛﺛ',



                start_date.strftime('%Y-%m-%d'),



                end_date.strftime('%Y-%m-%d')



            )



            



            if reason_filter:



df = df[df['ﻛﺕﮔ۵ﮒﮒ'].isin(reason_filter)]



            



            for _, row in df.iterrows():



buy_seats = self._parse_seats(row['ﻛﺗﺍﮒ۴ﮒﺕﻛﺛ'])



sell_seats = self._parse_seats(row['ﮒﮒﭦﮒﺕﻛﺛ'])



                



                institutional_buy = self.identify_institutional_seats(buy_seats)



                institutional_sell = self.identify_institutional_seats(sell_seats)



                



                hot_money_buy = self.identify_hot_money_seats(buy_seats)



                hot_money_sell = self.identify_hot_money_seats(sell_seats)



                



                net_buy = sum([seat['ﻛﺗﺍﮒ۴ﻠﻠ۱'] for seat in buy_seats]) - \



                         sum([seat['ﮒﮒﭦﻠﻠ۱'] for seat in sell_seats])



                



                item = DragonTigerListItem(



stock_code=row['ﻟﺁﮒﺕﻛﭨ۲ﻝ'],



                    stock_name=row['ﻟﺁﮒﺕﻝ؟ﻝ۶?],



                    trade_date=row['ﻛﭦ۳ﮔﮔ۴ﮔ'],



                    close_price=row['ﮔﭘﻝﻛﭨ?],



                    change_pct=row['ﮔﭘ۷ﻟﺓﮒﺗ?],



                    turnover_rate=row['ﮔ۱ﮔﻝ?],



reason=row['ﻛﺕﮔ۵ﮒﮒ'],



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



"""ﻟﺁﮒ،ﮔﭦﮔﻛﺕﻝ۷ﮒﺕﻛﺛ"""



        institutional_seats = []



        



        for seat in seats:



            seat_name = seat.get('ﻟ۴ﻛﺕﻠ۷ﮒﻝ۶?, '')



            



            if 'ﮔﭦﮔﻛﺕﻝ۷' in seat_name or \



               'ﮒ؛ﮒ' in seat_name or \



               'ﻝ۳ﺝﻛﺟ' in seat_name or \



               'ﻛﺟﻠ۸' in seat_name or \



               'QFII' in seat_name:



                institutional_seats.append(seat)



        



        return institutional_seats



    



    def identify_hot_money_seats(self, seats: List[Dict]) -> List[Dict]:



"""ﻟﺁﮒ،ﻝ۴ﮒﮔﺕﺕﻟﭖﮒﺕﻛﺛ"""



        hot_money_seats = []



        



        for seat in seats:



            seat_name = seat.get('ﻟ۴ﻛﺕﻠ۷ﮒﻝ۶?, '')



            



            if seat_name in self.known_hot_money_seats:



                hot_money_seats.append(seat)



        



        return hot_money_seats



    



    def analyze_institutional_behavior(self, item: DragonTigerListItem) -> Dict:



        """ﮒﮔﮔﭦﮔﻟﭖﻠﻟ۰ﻛﺕﭦ"""



        institutional_buy_seats = self.identify_institutional_seats(item.buy_seats)



        institutional_sell_seats = self.identify_institutional_seats(item.sell_seats)



        



        institutional_net_buy = sum([seat['ﻛﺗﺍﮒ۴ﻠﻠ۱'] for seat in institutional_buy_seats]) - \



                               sum([seat['ﮒﮒﭦﻠﻠ۱'] for seat in institutional_sell_seats])



        



        hot_money_buy_seats = self.identify_hot_money_seats(item.buy_seats)



        hot_money_sell_seats = self.identify_hot_money_seats(item.sell_seats)



        



        hot_money_net_buy = sum([seat['ﻛﺗﺍﮒ۴ﻠﻠ۱'] for seat in hot_money_buy_seats]) - \



                           sum([seat['ﮒﮒﭦﻠﻠ۱'] for seat in hot_money_sell_seats])



        



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



"""ﻟ۶۲ﮔﮒﺕﻛﺛﮒﻝ؛۵ﻛﺕ?""



        seats = []



        



        return seats



    



    def _calculate_signal_strength(self,



                                   institutional_net_buy: float,



                                   institutional_count: int,



                                   total_net_buy: float) -> float:



        """ﻟ؟۰ﻝ؟ﻛﺟ۰ﮒﺓﮒﺙﭦﮒﭦ۵"""



        if total_net_buy == 0:



            return 0.0



        



        ratio = institutional_net_buy / abs(total_net_buy)



        count_bonus = min(institutional_count / 5.0, 1.0)



        



        strength = (ratio * 0.7 + count_bonus * 0.3)



        



        return min(max(strength, 0.0), 1.0)



```







### 2.3 ﮒﮒﻟﭖﻠﻝﮔ۶ﮔ۴ﮒ۲







#### 2.3.1 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ







```python



@dataclass



class NorthboundCapitalFlow:



    """ﮒﮒﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﻝﭨﮔ



    



    ﻝﺑ۱ﮒﺙ: DATA.NORTHBOUND.001



    ﮒ؟ﻛﺗ: ﮒﮒﻟﭖﻠﺅﺙﮔﺎ۹ﻟ۰ﻠ?ﮔﺓﺎﻟ۰ﻠﺅﺙﮔﭖﮒﮔﺍﮔ؟



    """



    trade_date: datetime



    shanghai_connect_net_buy: float  # ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴ﺅﺙﻛﭦﺟﮒﺅﺙ



    shenzhen_connect_net_buy: float  # ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴ﺅﺙﻛﭦﺟﮒﺅﺙ



    total_net_buy: float  # ﮔﭨﮒﻛﺗﺍﮒ۴ﺅﺙﻛﭦﺟﮒﺅﺙ



    



    shanghai_connect_balance: float  # ﮔﺎ۹ﻟ۰ﻠﻛﺛﻠ۱ﺅﺙﻛﭦﺟﮒﺅﺙ?    shenzhen_connect_balance: float  # ﮔﺓﺎﻟ۰ﻠﻛﺛﻠ۱ﺅﺙﻛﭦﺟﮒﺅﺙ?    



    top_buy_stocks: List[Dict]  # ﻛﺗﺍﮒ۴ﮒ?0ﻟ۰ﻝ۴۷



    top_sell_stocks: List[Dict]  # ﮒﮒﭦﮒ?0ﻟ۰ﻝ۴۷



    



    sector_allocation: Dict[str, float]  # ﻟ۰ﻛﺕﻠﻝﺛ؟







@dataclass



class NorthboundHolding:



    """ﮒﮒﻟﭖﻠﮔﻛﭨﮔﺍﮔ؟ﻝﭨﮔ



    



    ﻝﺑ۱ﮒﺙ: DATA.NORTHBOUND_HOLDING.001



    ﮒ؟ﻛﺗ: ﮒﮒﻟﭖﻠﮔﻛﭨﮔﻝﭨ



    """



    stock_code: str



    stock_name: str



    hold_amount: float  # ﮔﻟ۰ﮔﺍﻠﺅﺙﻛﺕﻟ۰ﺅﺙ



hold_value: float  # ﮔﻟ۰ﮒﺕﮒﺙﺅﺙﻛﺕﮒﺅﺙ?    hold_ratio: float  # ﮔﻟ۰ﮒﮔﺁﺅﺙ?ﺅﺙ?    change_amount: float  # ﮔﻟ۰ﮒﮒﺅﺙﻛﺕﻟ۰ﺅﺙ



    change_ratio: float  # ﮔﻟ۰ﮒﮒﮔﺁﻛﺝﺅﺙ?ﺅﺙ?



class NorthboundCapitalMonitor(ABC):



    """ﮒﮒﻟﭖﻠﻝﮔ۶ﮒ۷ﮔﺛﻟﺎ۰ﮒﭦﻝﺎ?    



    ﻝﺑ۱ﮒﺙ: INTERFACE.NORTHBOUND.001



    ﻟﻟﺑ۲: ﻝﮔ۶ﮒﮒﻟﭖﻠﮔﭖﮒﮒﮔﻛﭨﮒﮒ?    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinDﻙﮔﺕﺁﻛﭦ۳ﮔﮒ؛ﮒﺙﮔﺍﮔ؟



    """



    



    @abstractmethod



    def fetch_daily_flow(self,



                        start_date: datetime,



                        end_date: datetime) -> List[NorthboundCapitalFlow]:



        """ﻟﺓﮒﮒﮒﻟﭖﻠﮔ۴ﮒﭦ۵ﮔﭖﮒ



        



        ﮒﮔﺍ:



            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ



            



        ﻟﺟﮒ:



            List[NorthboundCapitalFlow]: ﮔ۴ﮒﭦ۵ﮔﭖﮒﮔﺍﮔ؟ﮒﻟ۰۷



            



ﮔﺍﮔ؟ﮔﭦﮔﮒﺍ?



            iFinDﮒﺛﮔﺍ: THSﮒﮒﻟﭖﻠ



ﮒﮔ؟ﭖﮔﮒﺍ:



                - total_net_buy: ﮒﮒﻟﭖﻠﮒﻛﺗﺍﮒ۴



                - shanghai_connect_net_buy: ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴



                - shenzhen_connect_net_buy: ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴



        """



        pass



    



    @abstractmethod



    def fetch_holdings(self,



                      stock_codes: Optional[List[str]] = None,



                      top_n: int = 100) -> List[NorthboundHolding]:



        """ﻟﺓﮒﮒﮒﻟﭖﻠﮔﻛﭨﮔﻝﭨ



        



        ﮒﮔﺍ:



stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﮒﻟ۰۷ﺅﺙﮒﺁﻠﺅﺙﻠﭨﻟ؟۳ﻟﺟﮒﮒ۷ﻠ۷ﺅﺙ?            top_n: ﻟﺟﮒﮒNﮒ۹ﻟ۰ﻝ۴۷ﺅﺙﻠﭨﻟ؟۳100ﺅﺙ?



        ﻟﺟﮒ:



            List[NorthboundHolding]: ﮔﻛﭨﮔﻝﭨﮒﻟ۰۷



            



ﮔﺍﮔ؟ﮔﭦﮔﮒﺍ?



            iFinDﮒﺛﮔﺍ: THSﮒﮒﮔﻟ۰



ﮒﮔ؟ﭖﮔﮒﺍ:



                - hold_amount: ﮔﻟ۰ﮔﺍﻠ



- hold_value: ﮔﻟ۰ﮒﺕﮒ?                - hold_ratio: ﮔﻟ۰ﮒﮔﺁ



        """



        pass



    



    @abstractmethod



    def analyze_sector_preference(self,



                                 flow_data: List[NorthboundCapitalFlow]) -> Dict[str, float]:



        """ﮒﮔﮒﮒﻟﭖﻠﻟ۰ﻛﺕﮒﮒ۴ﺛ



        



        ﮒﮔﺍ:



            flow_data: ﮔﭖﮒﮔﺍﮔ؟



            



        ﻟﺟﮒ:



            Dict[str, float]: ﻟ۰ﻛﺕﻠﻝﺛ؟ﮔﺁﻛﺝ



            



        ﮒﮔﮔﺗﮔﺏ:



            1. ﻝﭨﻟ؟۰ﻛﺗﺍﮒ۴/ﮒﮒﭦﮒ?0ﻟ۰ﻝ۴۷ﻝﻟ۰ﻛﺕﮒﮒﺕ?            2. ﻟ؟۰ﻝ؟ﮒﻟ۰ﻛﺕﮒﻛﺗﺍﮒ۴ﻠﻠ۱



            3. ﻟﺁﮒ،ﻟ۰ﻛﺕﻟﺛ؟ﮒ۷ﻟﭘﮒﺟ



        """



        pass



    



    @abstractmethod



    def detect_smart_money_signal(self,



                                 flow_data: List[NorthboundCapitalFlow],



                                 threshold_days: int = 5,



                                 threshold_amount: float = 60.0) -> Dict:



        """ﮔ۲ﮔﭖﻟ۹ﮔﻠﺎﻛﺟ۰ﮒﺓ



        



        ﮒﮔﺍ:



            flow_data: ﮔﭖﮒﮔﺍﮔ؟



threshold_days: ﻟﺟﻝﭨﮒ۳۸ﮔﺍﻠﮒﺙﺅﺙﻠﭨﻟ؟۳5ﮒ۳۸ﺅﺙ



            threshold_amount: ﮒﻛﺗﺍﮒ۴ﻠﻠ۱ﻠﮒﺙﺅﺙﻠﭨﻟ؟۳60ﻛﭦﺟﮒﺅﺙ?            



        ﻟﺟﮒ:



            Dict: ﻟ۹ﮔﻠﺎﻛﺟ۰ﮒ?            



        ﻛﺟ۰ﮒﺓﻟ۶ﮒ:



1. ﻟﺟﻝﭨ5ﮔ۴ﮒﻛﺗﺍﮒ۴ﻟﭘ?0ﻛﭦﺟﮒﺅﺙﮔﺍﻟﺛﮔﭦﻙﻝﭖﮒﮔﺟﮒﻟﻝ?0%



            2. ﮒﮔ۴ﮒﮔﭖﮒﭦﻟﭘ?0ﻛﭦﺟﮒﺅﺙﻠ،ﻛﺙﺍﮒﺙﮔﭘﻟﺑﺗﻟ۰ﮒﺗﺏﮒﮒﮔ۳5.3%



        """



        pass



```







#### 2.3.2 iFinDﮒ؟ﻝﺍﻝﺎ?



```python



class IFindNorthboundCapitalMonitor(NorthboundCapitalMonitor):



    """iFinDﮒﮒﻟﭖﻠﻝﮔ۶ﮒ۷ﮒ؟ﻝ?    



    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.IFIND_NORTHBOUND.001



    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD



    """



    



    def __init__(self, config: Dict):



        self.config = config



        self.ifs_client = ths.THSApi()



    



    def fetch_daily_flow(self,



                        start_date: datetime,



                        end_date: datetime) -> List[NorthboundCapitalFlow]:



        """ﻟﺓﮒﮒﮒﻟﭖﻠﮔ۴ﮒﭦ۵ﮔﭖﮒ



        



        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:



            ths.ED_query(



                'thsﮒﮒﻟﭖﻠ',



                '',



                'ﻛﭦ۳ﮔﮔ۴ﮔ,ﮒﮒﻟﭖﻠﮒﻛﺗﺍﮒ۴,ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴,ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴,ﮔﺎ۹ﻟ۰ﻠﻛﺛﻠ۱?ﮔﺓﺎﻟ۰ﻠﻛﺛﻠ۱?,



                start_date,



                end_date



            )



        """



        flows = []



        



        try:



            df = self.ifs_client.ED_query(



                'thsﮒﮒﻟﭖﻠ',



                '',



                'ﻛﭦ۳ﮔﮔ۴ﮔ,ﮒﮒﻟﭖﻠﮒﻛﺗﺍﮒ۴,ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴,ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴,ﮔﺎ۹ﻟ۰ﻠﻛﺛﻠ۱?ﮔﺓﺎﻟ۰ﻠﻛﺛﻠ۱?,



                start_date.strftime('%Y-%m-%d'),



                end_date.strftime('%Y-%m-%d')



            )



            



            for _, row in df.iterrows():



                flow = NorthboundCapitalFlow(



                    trade_date=row['ﻛﭦ۳ﮔﮔ۴ﮔ'],



                    shanghai_connect_net_buy=row['ﮔﺎ۹ﻟ۰ﻠﮒﻛﺗﺍﮒ۴'] / 10000,



                    shenzhen_connect_net_buy=row['ﮔﺓﺎﻟ۰ﻠﮒﻛﺗﺍﮒ۴'] / 10000,



                    total_net_buy=row['ﮒﮒﻟﭖﻠﮒﻛﺗﺍﮒ۴'] / 10000,



                    shanghai_connect_balance=row['ﮔﺎ۹ﻟ۰ﻠﻛﺛﻠ۱?] / 10000,



                    shenzhen_connect_balance=row['ﮔﺓﺎﻟ۰ﻠﻛﺛﻠ۱?] / 10000,



                    top_buy_stocks=self._fetch_top_stocks(row['ﻛﭦ۳ﮔﮔ۴ﮔ'], 'buy'),



                    top_sell_stocks=self._fetch_top_stocks(row['ﻛﭦ۳ﮔﮔ۴ﮔ'], 'sell'),



                    sector_allocation={}



                )



                



                flows.append(flow)



                



        except Exception as e:



            print(f"Error fetching northbound capital flow: {e}")



        



        return flows



    



    def fetch_holdings(self,



                      stock_codes: Optional[List[str]] = None,



                      top_n: int = 100) -> List[NorthboundHolding]:



        """ﻟﺓﮒﮒﮒﻟﭖﻠﮔﻛﭨﮔﻝﭨ



        



        iFinDﻟﺍﻝ۷ﻝ۳ﭦﻛﺝ:



            ths.ED_query(



                'thsﮒﮒﮔﻟ۰',



                '',



'ﻟﺁﮒﺕﻛﭨ۲ﻝ,ﻟﺁﮒﺕﻝ؟ﻝ۶?ﮔﻟ۰ﮔﺍﻠ,ﮔﻟ۰ﮒﺕﮒ?ﮔﻟ۰ﮒﮔﺁ,ﮔﻟ۰ﮒﮒ,ﮔﻟ۰ﮒﮒﮔﺁﻛﺝ',



                '',



                ''



            )



        """



        holdings = []



        



        try:



            df = self.ifs_client.ED_query(



                'thsﮒﮒﮔﻟ۰',



                '',



'ﻟﺁﮒﺕﻛﭨ۲ﻝ,ﻟﺁﮒﺕﻝ؟ﻝ۶?ﮔﻟ۰ﮔﺍﻠ,ﮔﻟ۰ﮒﺕﮒ?ﮔﻟ۰ﮒﮔﺁ,ﮔﻟ۰ﮒﮒ,ﮔﻟ۰ﮒﮒﮔﺁﻛﺝ',



                '',



                ''



            )



            



            if stock_codes:



df = df[df['ﻟﺁﮒﺕﻛﭨ۲ﻝ'].isin(stock_codes)]



            



            df = df.head(top_n)



            



            for _, row in df.iterrows():



                holding = NorthboundHolding(



stock_code=row['ﻟﺁﮒﺕﻛﭨ۲ﻝ'],



                    stock_name=row['ﻟﺁﮒﺕﻝ؟ﻝ۶?],



                    hold_amount=row['ﮔﻟ۰ﮔﺍﻠ'],



                    hold_value=row['ﮔﻟ۰ﮒﺕﮒ?],



hold_ratio=row['ﮔﻟ۰ﮒﮔﺁ'],



                    change_amount=row['ﮔﻟ۰ﮒﮒ'],



                    change_ratio=row['ﮔﻟ۰ﮒﮒﮔﺁﻛﺝ']



                )



                



                holdings.append(holding)



                



        except Exception as e:



            print(f"Error fetching northbound holdings: {e}")



        



        return holdings



    



    def analyze_sector_preference(self,



                                 flow_data: List[NorthboundCapitalFlow]) -> Dict[str, float]:



        """ﮒﮔﮒﮒﻟﭖﻠﻟ۰ﻛﺕﮒﮒ۴ﺛ"""



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



        """ﮔ۲ﮔﭖﻟ۹ﮔﻠﺎﻛﺟ۰ﮒﺓ"""



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



'target_sectors': ['ﮔﺍﻟﺛﮔﭦ?, 'ﻝﭖﮒ'],



                'expected_win_rate': 0.80,



'reasoning': f'ﮒﮒﻟﭖﻠﻟﺟﻝﭨ{threshold_days}ﮔ۴ﮒﻛﺗﺍﮒ۴ﻟﭘ{threshold_amount}ﻛﭦﺟﮒﺅﺙﮒﮒﺎﮔﺍﮔ؟ﮔﺝﻝ۳ﭦﮔﺍﻟﺛﮔﭦﻙﻝﭖﮒﮔﺟﮒﻟﻝﻟﺝﺝ80%'



            }



        



        recent_flow = flow_data[-1]



        if recent_flow.total_net_buy < -80:



            return {



                'signal_type': 'RISK_ALERT',



                'net_outflow': abs(recent_flow.total_net_buy),



                'confidence': 0.85,



                'risk_sectors': ['ﻠ،ﻛﺙﺍﮒﺙﮔﭘﻟﺑﺗﻟ۰'],



                'expected_drawdown': 0.053,



                'reasoning': f'ﮒﮒﻟﭖﻠﮒﮔ۴ﮒﮔﭖﮒﭦﻟﭘ?0ﻛﭦﺟﮒﺅﺙﮒﮒﺎﮔﺍﮔ؟ﮔﺝﻝ۳ﭦﻠ،ﻛﺙﺍﮒﺙﮔﭘﻟﺑﺗﻟ۰ﮒﺗﺏﮒﮒﮔ۳5.3%'



            }



        



        return {



            'signal_type': 'NEUTRAL',



            'confidence': 0.50,



            'reasoning': 'ﮒﮒﻟﭖﻠﮔﭖﮒﮔ۹ﻟﺝﺝﮒﺍﮔﺝﻟﻛﺟ۰ﮒﺓﻠﮒ?



        }



    



    def _fetch_top_stocks(self, trade_date: datetime, direction: str) -> List[Dict]:



        """ﻟﺓﮒﻛﺗﺍﮒ۴/ﮒﮒﭦﮒ?0ﻟ۰ﻝ۴۷"""



        stocks = []



        



        return stocks



```







```
```---
```







## ﻭ۳ ﻛﺕﻙ?ﻝﺎﭨﮔﭦﻟﺛﻛﺛﻟﺁ۵ﻝﭨﮒﮔﺍﻠﻝﺛ؟







### 3.1 ﻛﺕﭨﮔﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙSovereign Fund Agentﺅﺙ?



**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.SOVEREIGN_FUND.001







**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﮒﺕﮒﭦﻝ۷ﺏﮒ؟ﮒ۷ﺅﺙﮔﺟﻝﻠ۸ﺎﮒ۷



- ETFﻠﻝﺛ؟ﻛﺕﭦﻛﺕﭨﺅﺙﻠﺟﮔﮔﮔ?- ﻛﭨﮒ۷ﮒﺕﮒﭦﮒﺙﮒﺕﺕﮔﺏ۱ﮒ۷ﮔﭘﻛﭨﮒ?



**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?



```yaml



sovereign_fund_agent:



  name: "ﻛﺕﭨﮔﮒﭦﻠﮔﭦﻟﺛﻛﺛ?



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



description: "ﻛﺕﻟﺁ500ETF"



    zz1000:



      weight: 0.15



      code: "512100.SH"



description: "ﻛﺕﻟﺁ1000ETF"



  



  position_limit:



    max_single_etf: 0.05



    max_total: 0.15



  



  holding_period:



    min_days: 90



    avg_days: 180



    max_days: 365



  



  policy_signal_sources:



    - "ﮒ۳؟ﻟ۰ﮒ؛ﮒ"



    - "ﻟﺁﻝﻛﺙﮒ؛ﮒ?



- "ﮒﺛﮒ۰ﻠ۱ﮔﺟﻝﮔﻛﭨ?



    - "ﮔﺍﮒﻝ۳ﺝﻝ۳ﺝﻟ؟?



  



  market_stability_indicators:



    - "ﮒﺕﮒﭦﮔﺏ۱ﮒ۷ﻝ?



- "ﮔﭖﮒ۷ﮔ۶ﮔﮔ?



    - "ﮒﺕﮒﭦﮔﻝﭨ۹ﮔﮔﺍ"



- "ﻟﻝﺗﻟ۰ﻟﭖﻠﮔﭖﮒ?



  



  reward_function:



    market_stability_weight: 0.50



    policy_alignment_weight: 0.30



    long_term_return_weight: 0.20



  



  risk_control:



    max_intervention_per_day: 1



    cooldown_period: 5



    stop_loss_threshold: -0.10



```







### 3.2 ﮒ؛ﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙMutual Fund Agentﺅﺙ?



**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.MUTUAL_FUND.001







**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻟﭖﻠﻟﻝ۵ﺅﺙﻠ،ﻛﭨﻛﺛﻟﺟﻟ۰



- ﮒﭦﮔ؛ﻠ۱ﻠ۸ﺎﮒ۷ﺅﺙﮔﭦﮔﮒﮒ



- ﮒﺗﺏﮒﻛﭨﻛﺛ86.40%







**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?



```yaml



mutual_fund_agent:



  name: "ﮒ؛ﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛ?



  type: "institutional_investor"



  



  decision_model:



    type: "rl_fundamental_hybrid"



    rl_algorithm: "SAC"



    rl_weight: 0.60



    fundamental_weight: 0.40



  



  sector_focus:



    ai_computing:



      weight: 0.35



keywords: ["AIﻝ؟ﮒ", "GPU", "ﮔﺍﮔ؟ﻛﺕﮒﺟ"]



target_stocks: ["ﮔﭖ۹ﮔﺛ؟ﻛﺟ۰ﮔﺁ", "ﻛﺕﻝ۶ﮔﮒ", "ﮒﺁﮔ۵ﻝﭦ?]



    



    medical_tech:



      weight: 0.25



      keywords: ["ﮒﭨﻝﮔﺍﻝ۶ﮔ", "ﮒﮔﺍﻟ?, "ﮒﭨﻝﮒ۷ﮔ۱ﺍ"]



      target_stocks: ["ﮔﻝﮒﭨﻟﺁ", "ﻟﺟﻝﮒﭨﻝ", "ﻟﺁﮔﮒﭦﺓﮒﺝﺓ"]



    



    humanoid_robot:



      weight: 0.20



      keywords: ["ﻛﭦﭦﮒﺛ۱ﮔﭦﮒ۷ﻛﭦ?, "ﻛﺙﭦﮔﻝﭖﮔﭦ", "ﮒﻠﮒ۷"]



      target_stocks: ["ﻛﺕﻟﺎﮔﭦﮔ۶", "ﮔﺎﮒﺓﮔﮔ?, "ﻝﭨﺟﻝﻟﺍﮔﺏ۱"]



    



    new_energy:



      weight: 0.20



      keywords: ["ﮔﺍﻟﺛﮔﭦ?, "ﮒﻛﺙ", "ﮒ۷ﻟﺛ"]



      target_stocks: ["ﮒ؟ﮒﺝﺓﮔﭘﻛﭨ۲", "ﻠﮒﭦﻝﭨﺟﻟﺛ", "ﮔﺁﻛﭦﻟﺟ?]



  



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







### 3.3 ﮒ۳ﻟﭖﮔﭦﻟﺛﻛﺛﺅﺙForeign Capital Agentﺅﺙ?



**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.FOREIGN_CAPITAL.001







**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻛﭨﺓﮒﺙﮔﻟﭖﺅﺙﮔﺟﮒﻟﺛ؟ﮒ۷



- ﻟ۹ﮔﻠﺎﮔﮒﭦﺅﺙﻠﺟﮔﻠﻝﺛ؟



- ﮔﺝﮒﺙﻛﺙﻝﭨﮔﺕﮒﺟﻟﭖﻛﭦ۶ﺅﺙﻟﺛ؛ﮒﻠ،ﮔﻠﺟﮒﭘﻠ?



**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?



```yaml



foreign_capital_agent:



  name: "ﮒ۳ﻟﭖﮔﭦﻟﺛﻛﺛ?



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



sectors: ["ﻝﭖﮒ", "ﮒﭦﻝ۰ﮒﮒﺓ۴", "ﻝﭖﮒﻟ؟ﺝﮒ۳"]



    



    traditional_core:



      weight: 0.20



      sectors: ["ﻠ۲ﮒﻠ۴؟ﮔ", "ﮒﭨﻟﺁ"]



    



    scarce_assets:



      weight: 0.30



sectors: ["ﻛﺕﻟﺁ", "ﻝﺛﻠ"]



  



  fx_factors:



    usd_cny_weight: 0.30



    dollar_index_weight: 0.20



    risk_premium_weight: 0.20



  



  smart_money_signal:



    consecutive_buy_days: 5



    net_buy_threshold: 60.0



target_sectors: ["ﮔﺍﻟﺛﮔﭦ?, "ﻝﭖﮒ"]



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







### 3.4 ﻠﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛﺅﺙQuantitative Fund Agentﺅﺙ?



**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.QUANT_FUND.001







**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻠ،ﻠ۱ﻛﭦ۳ﮔﺅﺙﻝ؟ﮔﺏﻠ۸ﺎﮒ?- ﮒﮔ۲ﮒﺅﺙﻝﭦ۹ﮒﺝﮔ۶ﮒﺙﭦ



- ﮔﻛﭨﮔﭘﻠﺑﻝﻟﺏﮔﺁ،ﻝ۶ﻝﭦ?



**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?



```yaml



quantitative_fund_agent:



  name: "ﻠﮒﮒﭦﻠﮔﭦﻟﺛﻛﺛ?



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







### 3.5 ﻝﻠﺎﮔﭦﻟﺛﻛﺛﺅﺙHot Money Agentﺅﺙ?



**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.HOT_MONEY.001







**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﮔﮔﺟﮔﮔﺏﺅﺙﮒﺟ،ﻟﺟﮒﺟ،ﮒ?- ﻠ۱ﮔﻠ۸ﺎﮒ۷ﺅﺙﮔﻝﭨ۹ﮔﺝﮒ۳?- ﮔﻛﭨﮒ۷ﮔﻝﺅﺙﮔ?ﮒ۷ﺅﺙ







**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?



```yaml



hot_money_agent:



name: "ﻝﻠﺎﮔﭦﻟﺛﻛﺛ?



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



      - "ﻛﭦﭦﮒﺛ۱ﮔﭦﮒ۷ﻛﭦ?



      - "ﮔﺍﻟﺛﮔﭦ?



- "ﮒﺗﭘﻟﺑﻠﻝﭨ"



    



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







### 3.6 ﻛﺟﻠ۸ﻟﭖﻠﮔﭦﻟﺛﻛﺛﺅﺙInsurance Fund Agentﺅﺙ?



**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.INSURANCE_FUND.001







**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻠﺟﮔﻠﻝﺛ؟ﺅﺙﻝ۷ﺏﮒ۴ﮔﻟﭖ?- ﻠ،ﻟ۰ﮔﺁﮒﮒ۴ﺛﺅﺙﻠ۲ﻠ۸ﮒﮔﭘ



- ﮔﻛﭨﮒ۷ﮔﻠﺟﺅﺙﮒﺗﺑﮒﭦ۵ﺅﺙ?



**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?



```yaml



insurance_fund_agent:



  name: "ﻛﺟﻠ۸ﻟﭖﻠﮔﭦﻟﺛﻛﺛ?



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



      reason: "ﻠ،ﻟ۰ﮔﺁﻙﻛﺛﻛﺙﺍﮒ?



    



    infrastructure:



      weight: 0.25



      reason: "ﻝﺍﻠﮔﭖﻝ۷ﺏﮒ؟?



    



    real_estate:



      weight: 0.15



      reason: "ﻠﺟﮔﻠﻝﺛ؟"



    



    utilities:



      weight: 0.15



      reason: "ﻠﺎﮒﺝ۰ﮔ۶ﮒﺙﭦ"



    



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







### 3.7 ﻛﭦ۶ﻛﺕﻟﭖﮔ؛ﮔﭦﻟﺛﻛﺛﺅﺙIndustrial Capital Agentﺅﺙ?



**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.INDUSTRIAL_CAPITAL.001







**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻛﺟ۰ﮔﺁﻛﺙﮒﺟﺅﺙﮔﻝ۴ﮒﺕﮒﺎ



- ﮒ۱ﮔﮒﻟﺑﺅﺙﻛﭨﺓﮒﺙﻟ؟۳ﮒ?- ﻠﺟﮔﮔﮔ







**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?



```yaml



industrial_capital_agent:



  name: "ﻛﭦ۶ﻛﺕﻟﭖﮔ؛ﮔﭦﻟﺛﻛﺛ?



  type: "institutional_investor"



  



  decision_model:



    type: "rule_engine_strategic_hybrid"



    rule_weight: 0.70



    strategic_weight: 0.30



  



  strategic_focus:



    industry_chain_integration:



      weight: 0.40



      description: "ﻛﭦ۶ﻛﺕﻠﺝﮔﺑﮒ?



    



    technology_acquisition:



      weight: 0.30



      description: "ﮔﮔﺁﻟﺓﮒ?



    



    market_share_expansion:



      weight: 0.30



description: "ﮒﺕﮒﭦﻛﭨﺛﻠ۱ﮔ۸ﮒﺙ"



  



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







### 3.8 ﻠﭘﮒ؟ﮔﻟﭖﻟﮔﭦﻟﺛﻛﺛﺅﺙRetail Investor Agentﺅﺙ?



**ﻛﭨ۲ﮒﺓ**ﺅﺙAGENT.RETAIL.001







**ﻟ۰ﻛﺕﭦﻝﺗﮒﺝ**ﺅﺙ?- ﻝﺝﻝﺝ۳ﮔﮒﭦﺅﺙﮔﻝﭨ۹ﻠ۸ﺎﮒ?- ﻟﺟﺛﮔﭘ۷ﮔﻟﺓﺅﺙﻝﮔﮔﮔ



- ﻛﺟ۰ﮔﺁﮒ۲ﮒﺟ







**ﮒﮔﺍﻠﻝﺛ؟**ﺅﺙ?



```yaml



retail_investor_agent:



  name: "ﻠﭘﮒ؟ﮔﻟﭖﻟﮔﭦﻟﺛﻛﺛ"



  type: "retail_investor"



  



  decision_model:



    type: "behavioral_finance"



    herding_weight: 0.40



    emotion_weight: 0.40



    rational_weight: 0.20



  



  behavioral_biases:



    herding_effect:



      weight: 0.40



      description: "ﻟﺓﻠﻛﺕﭨﮔﭖﻟﭖﻠ"



    



    disposition_effect:



      weight: 0.30



      description: "ﮒﮒﭦﻝﮒ۸ﻟ۰ﺅﺙﮔﮔﻛﭦﮔﻟ?



    



    overconfidence:



      weight: 0.20



      description: "ﻟﺟﮒﭦ۵ﻟ۹ﻛﺟ۰"



    



    loss_aversion:



      weight: 0.10



      description: "ﮔﮒ۳ﺎﮒﮔﭘ"



  



  emotion_indicators:



    fear_greed_index:



      threshold: 0.70



      impact: "buy_when_greedy"



    



    social_media_sentiment:



      weight: 0.30



      sources: ["ﻠ۹ﻝ", "ﻛﺕﮔﺗﻟﺑ۱ﮒﺁﻟ۰ﮒ۶"]



  



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







```
```---
```







## ﻭ۵ ﮒﻙﮔﺍﮔ؟ﻟﺓﮒﮔ۷۰ﮒﮒ؟ﮔﺑﮒ؟ﻝ?



### 4.1 ﻝﭨﻛﺕﮔﺍﮔ؟ﻟﺓﮒﮒ?



```python



from dataclasses import dataclass



from datetime import datetime



from typing import List, Dict, Optional



import pandas as pd







@dataclass



class MarketParticipantDataBundle:



    """ﮒﺕﮒﭦﮒﻛﺕﻟﮔﺍﮔ؟ﮒ



    



    ﻝﺑ۱ﮒﺙ: DATA.BUNDLE.001



    ﻝ۷ﻠ? ﮔﺑﮒﮔﮔﮒﺕﮒﭦﮒﻛﺕﻟﻝﺕﮒﺏﮔﺍﮔ?    """



    timestamp: datetime



    



    capital_flow_data: Dict  # DDX/DDE/BBDﮔﺍﮔ؟



    dragon_tiger_data: List  # ﻠﺝﻟﮔ۵ﮔﺍﮔ?    northbound_flow_data: Dict  # ﮒﮒﻟﭖﻠﮔﭖﮒ



    northbound_holdings: List  # ﮒﮒﻟﭖﻠﮔﻛﭨ



    



    level2_data: Optional[Dict] = None  # Level-2ﻟ۰ﮔ



    sentiment_data: Optional[Dict] = None  # ﮒﺕﮒﭦﮔﻝﭨ۹



    news_data: Optional[List] = None  # ﮔﺍﻠﭨﮔﺍﮔ؟







class MarketParticipantDataFetcher:



    """ﮒﺕﮒﭦﮒﻛﺕﻟﮔﺍﮔ؟ﻝﭨﻛﺕﻟﺓﮒﮒ?    



    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.DATA_FETCHER.001



    ﻟﻟﺑ۲: ﻝﭨﻛﺕﻟﺓﮒﮔﮔﮒﺕﮒﭦﮒﻛﺕﻟﻝﺕﮒﺏﮔﺍﮔ?    ﮔﺍﮔ؟ﮔﭦ? ﮒﻟﺎﻠ۰ﭦiFinD



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



        """ﻟﺓﮒﮔﮔﮒﺕﮒﭦﮒﻛﺕﻟﮔﺍﮔ?        



        ﮒﮔﺍ:



stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﮒﻟ۰۷



            start_date: ﮒﺙﮒ۶ﮔ۴ﮔ?            end_date: ﻝﭨﮔﮔ۴ﮔ



            



        ﻟﺟﮒ:



            MarketParticipantDataBundle: ﮔﺑﮒﮔﺍﮔ؟ﮒ?        """



        



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



"""ﻟﺓﮒﮒ؟ﮔﭘﮔﺍﮔ؟ﺅﺙﻝﻛﺕﺅﺙ



        



        ﮒﮔﺍ:



stock_codes: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﮒﻟ۰۷



            



        ﻟﺟﮒ:



            MarketParticipantDataBundle: ﮒ؟ﮔﭘﮔﺍﮔ؟ﮒ?        """



        



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







### 4.2 ﮔﺍﮔ؟ﻝﺙﮒﻛﺕﮔﺑﮔﺍﻝﻝ?



```python



from datetime import datetime, timedelta



from typing import Dict, Optional



import redis



import json







class DataCacheManager:



"""ﮔﺍﮔ؟ﻝﺙﮒﻝ؟۰ﻝﮒ?



    ﻝﺑ۱ﮒﺙ: IMPLEMENTATION.CACHE.001



ﻟﻟﺑ۲: ﻝ؟۰ﻝﮒﺕﮒﭦﮒﻛﺕﻟﮔﺍﮔ؟ﻝﺙﮒ?    ﻝﺙﮒﻛﭨﻟﺑ۷: Redis



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



"""ﻟﺓﮒﻝﺙﮒﮔﺍﮔ؟



        



        ﮒﮔﺍ:



data_type: ﮔﺍﮔ؟ﻝﺎﭨﮒﺅﺙddx_daily, ddx_realtimeﻝﺅﺙ



key: ﻝﺙﮒﻠ?



        ﻟﺟﮒ:



Optional[Dict]: ﻝﺙﮒﮔﺍﮔ؟ﺅﺙﻛﺕﮒﮒ۷ﮒﻟﺟﮒNone



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



"""ﻟ؟ﺝﻝﺛ؟ﻝﺙﮒﮔﺍﮔ؟



        



        ﮒﮔﺍ:



            data_type: ﮔﺍﮔ؟ﻝﺎﭨﮒ



key: ﻝﺙﮒﻠ?            data: ﮔﺍﮔ؟ﮒﮒ؟ﺗ



        """



        cache_key = f"{data_type}:{key}"



        ttl = self.cache_ttl.get(data_type, 3600)



        



        self.redis_client.setex(



            cache_key,



            ttl,



            json.dumps(data, default=str)



        )



    



    def clear_cache(self, data_type: Optional[str] = None) -> None:



"""ﮔﺕﻠ۳ﻝﺙﮒ



        



        ﮒﮔﺍ:



            data_type: ﮔﺍﮔ؟ﻝﺎﭨﮒﺅﺙﮒﺁﻠﺅﺙﻛﺕﮔﮒ؟ﮒﮔﺕﻠ۳ﮔﮔﺅﺙ



        """



        if data_type:



            pattern = f"{data_type}:*"



        else:



            pattern = "*"



        



        keys = self.redis_client.keys(pattern)



        if keys:



            self.redis_client.delete(*keys)



```







```
```---
```







## ﻭ ﻛﭦﻙﻠﮔﮔﭖﻟﺁﻛﺕﻠ۹ﻟﺁ







### 5.1 ﮔﺍﮔ؟ﻟﺓﮒﮔ۴ﮒ۲ﮔﭖﻟﺁﻝ۷ﻛﺝ







```python



import unittest



from datetime import datetime, timedelta







class TestCapitalFlowDataFetcher(unittest.TestCase):



    """ﻟﭖﻠﮔﭖﮒﮔﺍﮔ؟ﻟﺓﮒﮒ۷ﮔﭖﻟﺁ?""



    



    def setUp(self):



        self.fetcher = IFindCapitalFlowFetcher(config={})



        self.test_stocks = ['600519.SH', '000858.SZ']



        self.test_date = datetime.now() - timedelta(days=7)



        self.end_date = datetime.now()



    



    def test_fetch_ddx(self):



        """ﮔﭖﻟﺁDDXﮔﺍﮔ؟ﻟﺓﮒ"""



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



        """ﮔﭖﻟﺁDDEﮔﺍﮔ؟ﻟﺓﮒ"""



        result = self.fetcher.fetch_dde(



            self.test_stocks,



            self.test_date,



            self.end_date



        )



        



        self.assertIsInstance(result, dict)



        self.assertIn('600519.SH', result)



    



    def test_fetch_bbd(self):



        """ﮔﭖﻟﺁBBDﮔﺍﮔ؟ﻟﺓﮒ"""



        result = self.fetcher.fetch_bbd(



            self.test_stocks,



            self.test_date,



            self.end_date



        )



        



        self.assertIsInstance(result, dict)



        self.assertIn('600519.SH', result)



    



    def test_fetch_realtime_capital_flow(self):



        """ﮔﭖﻟﺁﮒ؟ﮔﭘﻟﭖﻠﮔﭖﮒﻟﺓﮒ"""



        result = self.fetcher.fetch_realtime_capital_flow(



            self.test_stocks



        )



        



        self.assertIsInstance(result, dict)



        self.assertIn('600519.SH', result)







class TestNorthboundCapitalMonitor(unittest.TestCase):



    """ﮒﮒﻟﭖﻠﻝﮔ۶ﮒ۷ﮔﭖﻟﺁ?""



    



    def setUp(self):



        self.monitor = IFindNorthboundCapitalMonitor(config={})



        self.test_date = datetime.now() - timedelta(days=30)



        self.end_date = datetime.now()



    



    def test_fetch_daily_flow(self):



        """ﮔﭖﻟﺁﮔ۴ﮒﭦ۵ﮔﭖﮒﻟﺓﮒ"""



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



        """ﮔﭖﻟﺁﻟ۹ﮔﻠﺎﻛﺟ۰ﮒﺓﮔ۲ﮔﭖ?""



        flow_data = self.monitor.fetch_daily_flow(



            self.test_date,



            self.end_date



        )



        



        signal = self.monitor.detect_smart_money_signal(flow_data)



        



        self.assertIsInstance(signal, dict)



        self.assertIn('signal_type', signal)



        self.assertIn('confidence', signal)



```







```
```---
```







## ﻭ ﮒﻙﮔﺑﮔﺍﮔ۴ﮒﺟ?



| ﻝﮔ؛ | ﮔ۴ﮔ | ﮔﺑﮔﺍﮒﮒ؟ﺗ | ﻛﺛﻟ?|



|------|------|----------|------|



| v2.0 | 2026-04-03 | ﮔﺁﻟﺁﮔﮒﮒﻙﻟﭖﻠﮔﭖﮒﻝﮔ۶ﮔ۴ﮒ۲ﻙﮔﭦﻟﺛﻛﺛﮒﮔﺍﻠﻝﺛ؟ﻙﮔﺍﮔ؟ﻟﺓﮒﮔ۷۰ﮒ?| Spec-Approver |







```
```---
```







**ﻝﮔ؛**: v2.0 | **ﮔﺑﮔﺍ**: 2026-04-03 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ?



