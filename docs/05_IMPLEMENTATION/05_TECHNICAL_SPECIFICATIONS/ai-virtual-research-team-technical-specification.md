---
module_id: AI_VIRTUAL_RESEARCH_TEAM_TECHNICAL_SPECIFICATION_8597
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
- AI_VIRTUAL_RESEARCH_TEAM_TECHNICAL技术规范
layer: layer_05
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵
applicable_scope: 'Layer 9 - AIﮒﮔﺍﺅﺟ?| ﻛﺕﮒ۰ﮔﭘﮔ: ﻛﺕﻝﭦ۶ﮔﭘﻠﺑﮔ۰ﮔﭘﻟﮒﮔﭘﮔ'
compliance_level: ﻛﺕﻛﺕﮔﮒ
parent_document: ../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/AI_ENHANCEMENT_INTEGRATION_BLUEPRINT.md
implementation_status: ﻟ۶ﮒﻠﭘﮔ؟ﭖ
---
## ﻭ ﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵ﮔ۵ﻟﺟﺍ







### ﮔﮔ۰۲ﻝ؟ﻝ







ﮔ؛ﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵ﻟﺁ۵ﻝﭨﮒ؟ﻛﺗﻛﭦAIﻟﮔﻝﻝ۸ﭘﮒ۱ﻠﻠ۰ﺗﻝ؟ﻝﮔﮔﮔﮔﺁﻝﭨﻟﺅﺙﮒﮔ؛ﮔﭘﮔﻟ؟ﺝﻟ؟۰ﻙﮔ۴ﮒ۲ﮒ؟ﻛﺗﻙﮔﺍﮔ؟ﮔ۷۰ﮒﻙﻝ؟ﮔﺏﮒ؟ﻝﺍﻙﮔﭖﻟﺁﻝﻝ۴ﻝﺅﺙﻛﺕﭦﮒﺙﮒﮒ۱ﻠﮔﻛﺝﮒ؟ﮔﺑﻝﮔﮔﺁﮔﮒﺁﺙﺅﺟﺛ?



```
```---
```







## ﻛﺕﻙﮔ۵ﺅﺟ?



### 1.1 ﻟ؟ﺝﻟ؟۰ﻟﮔﺁ







### 1.2 ﮔﮔﺁﮒ؟ﺅﺟ?



**Layerﮒ؟ﻛﺛ**: Layer 9 - AIﮒﮔﺍﺅﺟ?



**ﮔﮔﺁﮔﻝﮒﭦ۵**: ﮔﻝﺅﺙﮒﭦﻛﭦGLM-4ﮒ۳۶ﮔ۷۰ﮒﺅﺙ







**ﮒ؟ﮔﺛﮒ۳ﮔﺅﺟ?*: ﻛﺕﻝﺅﺙﻠﻟ۵ﮒ۳AIﮒﻛﺛﮒﻝ۴ﻟﺁﮒﭦﻠﮔﺅﺟ?



### 1.3 ﻝﮔ؛ﻛﺟ۰ﮔﺁ







| ﻝﮔ؛ | ﮔ۴ﮔ | ﮒﮔﺑﻟﺁﺑﮔ | ﻛﺛﺅﺟﺛ?|



|------|------|---------|------|



| v1.0 | 2026-04-03 | ﮒﮒ۶ﻝﮔ؛ | ﻠ۵ﮒﺕﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟ |







```
```---
```







## ﻛﭦﻙﻟﺁ۵ﻝﭨﮔﭘﮔﻟ؟ﺝﺅﺟ?



### 2.1 ﮔﺑﻛﺛﮔﭘﮔﺅﺟ?



```







```---







## ﻛﺕﻙﮔ۴ﮒ۲ﮒ؟ﺅﺟ?



### 3.1 ﻝﻝ۸ﭘﻛﺕﭨﻝ؟۰ﮔ۴ﮒ۲







```python



from abc import ABC, abstractmethod



from typing import List, Dict, Optional



from datetime import datetime







class ResearchDirectorInterface(ABC):



"""ﻝﻝ۸ﭘﻛﺕﭨﻝ؟۰ﮔ۴ﮒ۲"""







    @abstractmethod



    def plan_research_direction(self, market_state: Dict) -> List[str]:



        """



ﻟ۶ﮒﻝﻝ۸ﭘﮔﺗﮒ







        Args:



            market_state: ﮒﺕﮒﭦﻝﭘﮔﻛﺟ۰ﺅﺟ?



        Returns:



ﻝﻝ۸ﭘﮔﺗﮒﮒﻟ۰۷



        """



        pass







    @abstractmethod



    def generate_tasks(self, research_direction: Dict) -> List[Dict]:



        """



ﻝﮔﻝﻝ۸ﭘﻛﭨﭨﮒ۰







        Args:



research_direction: ﻝﻝ۸ﭘﮔﺗﮒ







        Returns:



            ﻛﭨﭨﮒ۰ﮒﻟ۰۷



        """



        pass







    @abstractmethod



    def evaluate_result(self, task: Dict) -> Dict:



        """



ﻟﺁﻛﺙﺍﻝﻝ۸ﭘﮔﮔ







        Args:



task: ﻝﻝ۸ﭘﻛﭨﭨﮒ۰







        Returns:



            ﻟﺁﻛﺙﺍﻝﭨﮔ



        """



        pass



```







### 3.2 ﮒﮒﻝﻝ۸ﭘﮒﮔ۴ﺅﺟ?



```python



class FactorResearcherInterface(ABC):



"""ﮒﮒﻝﻝ۸ﭘﮒﮔ۴ﺅﺟ?""







    @abstractmethod



    def mine_factors(self,



                    data: pd.DataFrame,



                    target: pd.Series,



                    factor_type: str = 'all') -> List[Dict]:



        """



ﮔﮔﮒﮒ







        Args:



            data: ﮒﮒ۶ﻝﺗﮒﺝﮔﺍﮔ؟



target: ﻝ؟ﮔﮔﭘﻝﺅﺟ?            factor_type: ﮒﮒﻝﺎﭨﮒ







        Returns:



ﮒﮒﮒﻟ۰۷



        """



        pass







    @abstractmethod



    def validate_factor(self,



                       factor: Dict,



                       data: pd.DataFrame,



                       target: pd.Series) -> Dict:



        """



ﻠ۹ﻟﺁﮒﮒﮔﮔﺅﺟ?



        Args:



factor: ﮒﮒﻛﺟ۰ﮔﺁ



            data: ﮔﺍﮔ؟



target: ﻝ؟ﮔﮔﭘﻝﺅﺟ?



        Returns:



            ﻠ۹ﻟﺁﻝﭨﮔ



        """



        pass







    @abstractmethod



    def optimize_factor(self, factor: Dict, data: pd.DataFrame) -> Dict:



        """



ﻛﺙﮒﮒﮒ







        Args:



factor: ﮒﮒﻛﺟ۰ﮔﺁ



            data: ﮔﺍﮔ؟







        Returns:



ﻛﺙﮒﮒﻝﮒﮒ



        """



        pass







    @abstractmethod



    def generate_report(self, factor: Dict) -> str:



        """



ﻝﮔﮒﮒﻝﻝ۸ﭘﮔ۴ﮒ







        Args:



factor: ﮒﮒﻛﺟ۰ﮔﺁ







        Returns:



            ﮔ۴ﮒﮒﮒ؟ﺗ



        """



        pass



```







### 3.3 ﻝﻝ۴ﻝﻝ۸ﭘﮒﮔ۴ﺅﺟ?



```python



class StrategyResearcherInterface(ABC):



"""ﻝﻝ۴ﻝﻝ۸ﭘﮒﮔ۴ﺅﺟ?""







    @abstractmethod



    def design_strategy(self,



                       factors: List[Dict],



                       market_state: Dict) -> Dict:



        """



ﻟ؟ﺝﻟ؟۰ﻝﻝ۴







        Args:



factors: ﮒﮒﮒﻟ۰۷



            market_state: ﮒﺕﮒﭦﻝﭘﺅﺟﺛ?



        Returns:



ﻝﻝ۴ﻟ؟ﺝﻟ؟۰



        """



        pass







    @abstractmethod



    def backtest_strategy(self,



                         strategy: Dict,



                         historical_data: pd.DataFrame) -> Dict:



        """



ﮒﮔﭖﻝﻝ۴







        Args:



strategy: ﻝﻝ۴ﻟ؟ﺝﻟ؟۰



            historical_data: ﮒﮒﺎﮔﺍﮔ؟







        Returns:



            ﮒﮔﭖﻝﭨﮔ



        """



        pass







    @abstractmethod



    def optimize_strategy(self,



                         strategy: Dict,



                         backtest_result: Dict) -> Dict:



        """



ﻛﺙﮒﻝﻝ۴







        Args:



strategy: ﻝﻝ۴ﻟ؟ﺝﻟ؟۰



            backtest_result: ﮒﮔﭖﻝﭨﮔ







        Returns:



ﻛﺙﮒﮒﻝﻝﻝ۴



        """



        pass



```







### 3.4 ﮒﺕﮒﭦﮒﮔﮒﺕﮔ۴ﺅﺟ?



```python



class MarketAnalystInterface(ABC):



    """ﮒﺕﮒﭦﮒﮔﮒﺕﮔ۴ﺅﺟ?""







    @abstractmethod



    def analyze_market(self, market_data: Dict) -> Dict:



        """



        ﮒﮔﮒﺕﮒﭦﻝﭘﺅﺟﺛ?



        Args:



            market_data: ﮒﺕﮒﭦﮔﺍﮔ؟







        Returns:



            ﮒﺕﮒﭦﮒﮔﻝﭨﮔ



        """



        pass







    @abstractmethod



    def interpret_news(self, news: Dict) -> Dict:



        """



        ﻟ۶۲ﻟﺁﭨﮔﺍﻠﭨ







        Args:



            news: ﮔﺍﻠﭨﻛﺟ۰ﮔﺁ







        Returns:



            ﮔﺍﻠﭨﻟ۶۲ﻟﺁﭨﻝﭨﮔ



        """



        pass







    @abstractmethod



    def analyze_sentiment(self, social_data: Dict) -> Dict:



        """



        ﮒﮔﮒﺕﮒﭦﮔﻝﭨ۹







        Args:



            social_data: ﻝ۳ﺝﻛﭦ۳ﮒ۹ﻛﺛﮔﺍﮔ؟







        Returns:



            ﮔﻝﭨ۹ﮒﮔﻝﭨﮔ



        """



        pass



```







### 3.5 ﻝ۴ﻟﺁﻝ؟۰ﻝﮒﮔ۴ﺅﺟ?



```python



class KnowledgeManagerInterface(ABC):



    """ﻝ۴ﻟﺁﻝ؟۰ﻝﮒﮔ۴ﺅﺟ?""







    @abstractmethod



    def extract_knowledge(self, research_result: Dict) -> Dict:



        """



ﻛﭨﻝﻝ۸ﭘﮔﮔﻛﺕﮔﮒﻝ۴ﻟﺁ







        Args:



research_result: ﻝﻝ۸ﭘﮔﮔ







        Returns:



            ﮔﮒﻝﻝ۴ﺅﺟ?        """



        pass







    @abstractmethod



    def store_knowledge(self, knowledge: Dict) -> str:



        """



ﮒﮒ۷ﻝ۴ﻟﺁﮒﺍﻝ۴ﻟﺁﮒﭦ







        Args:



            knowledge: ﻝ۴ﻟﺁﻛﺟ۰ﮔﺁ







        Returns:



            ﻝ۴ﻟﺁID



        """



        pass







    @abstractmethod



    def retrieve_knowledge(self, query: str, top_k: int = 5) -> List[Dict]:



        """



        ﮔ۲ﻝﺑ۱ﻝ۴ﺅﺟ?



        Args:



            query: ﮔ۴ﻟﺁ۱ﮔﮔ؛



            top_k: ﻟﺟﮒﮔﺍﻠ







        Returns:



            ﻝ۴ﻟﺁﮒﻟ۰۷



        """



        pass



```







```---







## ﮒﻙﮔﺍﮔ؟ﮔ۷۰ﮒﻛﺕﮒﮒ۷







### 4.1 ﮔﺍﮔ؟ﮒﭦﻟ۰۷ﻝﭨﮔ







#### 4.1.1 ﻝﻝ۸ﭘﻛﭨﭨﮒ۰ﺅﺟ?



```sql



CREATE TABLE research_tasks (



    task_id TEXT PRIMARY KEY,



    task_type TEXT NOT NULL,



    priority INTEGER NOT NULL,



    description TEXT NOT NULL,



    assigned_to TEXT NOT NULL,



    deadline TIMESTAMP NOT NULL,



    status TEXT NOT NULL,



    result TEXT,



    evaluation TEXT,



    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,



    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP



);







CREATE INDEX idx_task_status ON research_tasks(status);



CREATE INDEX idx_task_assigned ON research_tasks(assigned_to);



CREATE INDEX idx_task_deadline ON research_tasks(deadline);



```







#### 4.1.2 ﻝﻝ۸ﭘﮔﮔﺅﺟ?



```sql



CREATE TABLE research_results (



    result_id TEXT PRIMARY KEY,



    task_id TEXT NOT NULL,



    result_type TEXT NOT NULL,



    result_data TEXT NOT NULL,



    quality_score REAL,



    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,



    FOREIGN KEY (task_id) REFERENCES research_tasks(task_id)



);







CREATE INDEX idx_result_task ON research_results(task_id);



CREATE INDEX idx_result_type ON research_results(result_type);



```







#### 4.1.3 ﻝ۴ﻟﺁﮒﭦﻟ۰۷







```sql



CREATE TABLE knowledge_base (



    knowledge_id TEXT PRIMARY KEY,



    knowledge_type TEXT NOT NULL,



    title TEXT NOT NULL,



    summary TEXT NOT NULL,



    key_points TEXT,



    applicable_scenarios TEXT,



    risk_warnings TEXT,



    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,



    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP



);







CREATE INDEX idx_knowledge_type ON knowledge_base(knowledge_type);



CREATE INDEX idx_knowledge_created ON knowledge_base(created_at);



```







```---







## ﻛﭦﻙﻝ؟ﮔﺏﮒ؟ﻝﺍﻟﺁﺑﺅﺟ?



### 5.1 ﻝﻝ۸ﭘﮔﺗﮒﻟ۶ﮒﻝ؟ﮔﺏ







#### 5.1.1 ﻝ؟ﮔﺏﮒﻝ







ﻛﺛﺟﻝ۷GLM-4ﮒ۳۶ﮔ۷۰ﮒﺅﺙﻠﻟﺟPrompt Engineeringﮒﺙﮒﺁﺙﮔ۷۰ﮒﮔﺗﮔ؟ﮒﺕﮒﭦﻝﭘﮔﻟ۶ﮒﻝﻝ۸ﭘﮔﺗﮒﺅﺟﺛ?



#### 5.1.2 ﮒ؟ﻝﺍﻛﭨ۲ﻝ







```python



def plan_research_direction(self, market_state: Dict) -> List[str]:



    """



ﻟ۶ﮒﻝﻝ۸ﭘﮔﺗﮒ







ﻝ؟ﮔﺏﮔ۴ﻠ۹۳ﺅﺟ?    1. ﮔﮒﭨﭦﮒﺕﮒﭦﻝﭘﮔﮔﺅﺟ?    2. ﻟﺍﻝ۷GLM-4ﻝﮔﻝﻝ۸ﭘﮔﺗﮒ



3. ﻟ۶۲ﮔﮒﻠ۹ﻟﺁﻝﻝ۸ﭘﮔﺗﺅﺟ?    """



    prompt = f"""



ﻛﺛﻛﺕﭦﻠﮒﻝﻝ۸ﭘﻛﺕﭨﻝ؟۰ﺅﺙﻟﺁﺓﮔﺗﮔ؟ﮒﺛﮒﮒﺕﮒﭦﻝﭘﮔﻟ۶ﮒﮔ۹ﮔ۴ﻛﺕﮒ۷ﻝﻝﻝ۸ﭘﮔﺗﮒﺅﺟ?



    ﮒﺕﮒﭦﻝﭘﮔﺅﺙ



    - ﮒﺕﮒﭦﻟﭘﮒﺟﺅﺙ{market_state.get('trend', 'unknown')}



    - ﮔﺏ۱ﮒ۷ﻝﺅﺙ{market_state.get('volatility', 'unknown')}



    - ﮒﺕﮒﭦﮔﻝﭨ۹ﺅﺙ{market_state.get('sentiment', 'unknown')}



    - ﻟﺟﮔﻛﭦﻛﭨﭘﺅﺙ{market_state.get('recent_events', [])}







ﻟﺁﺓﻟﺟﮒJSONﮔﺙﮒﺙﻝﻝﻝ۸ﭘﮔﺗﮒﮒﻟ۰۷ﺅﺙ



    {{



        "research_directions": [



            {{



"direction": "ﻝﻝ۸ﭘﮔﺗﮒﮒﻝ۶ﺍ",



                "priority": ﻛﺙﮒﺅﺟ?1-5),



                "reason": "ﻠﮔ۸ﻝﻝﺎ",



                "expected_outcome": "ﻠ۱ﮔﮔﮔ"



            }}



        ]



    }}



    """







    response = self._call_glm4(prompt)



    plan = json.loads(response)







    return plan['research_directions']



```







```---







### 5.2 ﮒﮒﮔﮔﻝ؟ﮔﺏ







#### 5.2.1 ﻝ؟ﮔﺏﮒﻝ







#### 5.2.2 ﮒ؟ﻝﺍﻛﭨ۲ﻝ







```python



def mine_factors(self,



                data: pd.DataFrame,



                target: pd.Series,



                factor_type: str = 'all') -> List[Dict]:



    """



ﮔﮔﮒﮒ







ﻝ؟ﮔﺏﮔ۴ﻠ۹۳ﺅﺟ?    1. ﻟﺍﻝ۷AIﮒﮒﮔﮔﮔ۷۰ﮒ



2. ﻠ۹ﻟﺁﮒﮒﮔﮔﺅﺟ?    3. ﻟﺟﮒﻠ۹ﻟﺁﻠﻟﺟﻝﮒﺅﺟ?    """



# 1. ﻛﺛﺟﻝ۷AIﮒﮒﮔﮔﮔ۷۰ﮒﮔﮔﮒﮒ



    factors = self.ai_factor_miner.mine_factors(



        data=data,



        target=target,



        methods=['deep_learning', 'reinforcement_learning', 'genetic_algorithm'],



        min_ic=0.03,



        max_factors=20



    )







# 2. ﻠ۹ﻟﺁﮒﮒﮔﮔﺅﺟ?    validated_factors = []



    for factor in factors:



        validation_result = self.validate_factor(factor, data, target)



        if validation_result['is_valid']:



            factor['validation'] = validation_result



            validated_factors.append(factor)







    return validated_factors



```







```---







## ﮒﻙﮒ؟ﮔﺛﮔﮔﺁﮔ







### 6.1 ﻝﺙﻝ۷ﻟﺁﻟ۷ﮒﮔ۰ﺅﺟ?



| ﮔﮔﺁﻠ۱ﺅﺟ?| ﮔﮔﺁﻠﮒ | ﻝﮔ؛ | ﻟﺁﺑﮔ |



|---------|---------|------|------|



| **ﻝﺙﻝ۷ﻟﺁﻟ۷** | Python | 3.9+ | ﻛﺕﭨﻟ۵ﮒﺙﮒﻟﺁﻟ۷ |



| **AIﮔ۷۰ﮒ** | GLM-4-Flash | Latest | ﻝﻝ۸ﭘﮒ۸ﮔﮔﺕﮒﺟ |



| **ﻛﭨﭨﮒ۰ﻟﺍﮒﭦ۵** | Apache Airflow | 2.7+ | ﻛﭨﭨﮒ۰ﻟﺍﮒﭦ۵ |



| **Webﮔ۰ﮔﭘ** | FastAPI | 0.104+ | APIﮔﮒ۰ |



| **ﮒﻠﮔﺍﮔ؟ﺅﺟ?* | ChromaDB | 0.4+ | ﻝ۴ﻟﺁﮒﮒ۷ |



| **ﮒﺏﻝﺏﭨﮔﺍﮔ؟ﺅﺟ?* | SQLite | 3.40+ | ﮔﺍﮔ؟ﮒﮒ۷ |







### 6.2 ﻝ؛؛ﻛﺕﮔﺗﻛﺝﺅﺟ?



| ﻛﺝﻟﭖﺅﺟ?| ﻝﮔ؛ | ﻝ۷ﺅﺟﺛ?|



|--------|------|------|



| **zhipuai** | 2.0+ | GLM-4 API |



| **langchain** | 0.1+ | AIﮒﺓ۴ﻛﺛﺅﺟ?|



| **pandas** | 2.1+ | ﮔﺍﮔ؟ﮒ۳ﻝ |



| **numpy** | 1.26+ | ﮔﺍﮒﺙﻟ؟۰ﺅﺟ?|







```---







## ﻛﺕﻙﮔﭖﻟﺁﻝﺅﺟ?



### 7.1 ﮒﮒﮔﭖﻟﺁ







#### 7.1.1 ﮔﭖﻟﺁﻟﮒﺑ







| ﮔ۷۰ﮒ | ﮔﭖﻟﺁﮒﮒ؟ﺗ | ﻟ۵ﻝﻝﻝ؟ﺅﺟ?|



|------|---------|-----------|



| **ﻝﻝ۸ﭘﻛﺕﭨﻝ؟۰** | ﻛﭨﭨﮒ۰ﻝﮔﻙﻟﺁﺅﺟ?| >85% |



| **ﮒﮒﻝﻝ۸ﭘﺅﺟ?* | ﮒﮒﮔﮔﻙﻠ۹ﺅﺟ?| >80% |



| **ﻝﻝ۴ﻝﻝ۸ﭘﺅﺟ?* | ﻝﻝ۴ﻟ؟ﺝﻟ؟۰ﻙﮒﺅﺟ?| >80% |



| **ﮒﺕﮒﭦﮒﮔﺅﺟ?* | ﮒﺕﮒﭦﮒﮔﻙﮔﻝﭨ۹ﮒﺅﺟ?| >80% |



| **ﻝ۴ﻟﺁﻝ؟۰ﻝﺅﺟ?* | ﻝ۴ﻟﺁﮔﮒﻙﮔ۲ﺅﺟ?| >85% |







#### 7.1.2 ﮔﭖﻟﺁﻝ۷ﻛﺝﻝ۳ﭦﻛﺝ







```python



import pytest







class TestResearchDirector:



"""ﻝﻝ۸ﭘﻛﺕﭨﻝ؟۰ﮔﭖﻟﺁ"""







    def test_plan_research_direction(self):



"""ﮔﭖﻟﺁﻝﻝ۸ﭘﮔﺗﮒﻟ۶ﮒ"""



        director = ResearchDirector(api_key="test_key")







        market_state = {



            'trend': 'bull',



            'volatility': 'low',



            'sentiment': 'optimistic'



        }







        directions = director.plan_research_direction(market_state)







        assert len(directions) > 0



        assert all('direction' in d for d in directions)



        assert all('priority' in d for d in directions)



```







```---







## ﮒ،ﻙﻠ۲ﻠ۸ﻛﺕﻝﭦ۵ﮔ







### 8.1 ﮔﮔﺁﻠ۲ﺅﺟ?



| ﻠ۲ﻠ۸ | ﮒﺛﺎﮒ | ﮔ۵ﻝ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |



|------|------|------|---------|



| **GLM-4 APIﻠﮒﭘ** | ﺅﺟ?| ﺅﺟ?| ﻟﺁﺓﮔﺎﻠﮒﻙﻠﻟﺁﺁﻠﺅﺟ?|



| **ﻝ۴ﻟﺁﮒﭦﮔ۶ﻟﺛ** | ﺅﺟ?| ﺅﺟ?| ﻛﺙﮒﻝﺑ۱ﮒﺙﻙﻝﺙﮒﮔﭦﺅﺟ?|



| **AIﮒﻛﺛﮒ۳ﮔﺅﺟ?* | ﺅﺟ?| ﺅﺟ?| ﻝ؟ﮒﮒﻛﺛﮔﭖﻝ۷ﻙﮔﻝ۰؟ﻟﺅﺟ?|







### 8.2 ﻝﭦ۵ﮔﮔ۰ﻛﭨﭘ







1. **APIﮔﮔ؛ﻝﭦ۵ﮔ**: ﮔﮔﺅﺟ?300ﺅﺟ?2. **ﮔﭘﻠﺑﻝﭦ۵ﮔ**: 8ﮒ۷ﮒﮒ؟ﮔ



3. **ﮔﮔﺁﻝﭦ۵ﺅﺟ?*: ﻛﺛﺟﻝ۷GLM-4ﮒ۳۶ﮔ۷۰ﺅﺟ?



```---







## ﻛﺗﻙﻠ۹ﮔﭘﮔﺅﺟ?



### 9.1 ﮒﻟﺛﻠ۹ﮔﭘ







| ﮒﻟﺛ | ﻠ۹ﮔﭘﮔﮒ |



|------|---------|



| **AIﻝﻝ۸ﭘﮒ۸ﮔ** | 5ﻛﺕ۹AIﻟ۶ﻟﺎﮒﺁﻝ۷ |



| **ﻛﭨﭨﮒ۰ﻝ؟۰ﻝ** | ﻛﭨﭨﮒ۰ﻟﺍﮒﭦ۵ﮔ۲ﮒﺕﺕ |



| **ﻝ۴ﻟﺁﮒﭦﻠﺅﺟ?* | ﻝ۴ﻟﺁﻟ۹ﮒ۷ﮒ۴ﮒﭦﺅﺟ?90% |



| **ﻝﻝ۸ﭘﮔﻝ** | ﮔﻝﮔﮒ>200% |







### 9.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘ







| ﮔﮔ | ﻝ؟ﮔﺅﺟ?|



|------|--------|



| **ﻛﭨﭨﮒ۰ﮒﮒﭦﮔﭘﻠﺑ** | <5ﺅﺟ?|



| **ﻝ۴ﻟﺁﮔ۲ﻝﺑ۱ﻠﮒﭦ۵** | <1ﺅﺟ?|



| **ﻝﺏﭨﻝﭨﮒﺁﻝ۷ﺅﺟ?* | >99% |







```---







## ﮒﻙﮒ؟ﮔﺛﻟﺓﺁﻝﭦﺟﮒﺝ







### 10.1 Phase 1: AIﻝﻝ۸ﭘﮒ۸ﮔﮒﺙﮒﺅﺙWeek 1-2ﺅﺟ?



**ﻝ؟ﮔ**: ﮒ؟ﮔ5ﻛﺕ۹AIﻝﻝ۸ﭘﮒ۸ﮔﮒﺙﺅﺟ?



**ﮒﺏﻠ؟ﻛﭨﭨﮒ۰**:



**ﻠ۹ﮔﭘﮔﮒ**:



- 5ﻛﺕ۹AIﻟ۶ﻟﺎﮒﺁﻝ۷



- ﮒﭦﮔ؛ﮒﻟﺛﮔ۲ﮒﺕﺕ







```---







### 10.2 Phase 2: ﻛﭨﭨﮒ۰ﻝ؟۰ﻝﻝﺏﭨﻝﭨﮒﺙﮒﺅﺙWeek 3-4ﺅﺟ?



**ﻝ؟ﮔ**: ﮒ؟ﮔﻛﭨﭨﮒ۰ﻟﺍﮒﭦ۵ﻝﺏﭨﻝﭨ







**ﮒﺏﻠ؟ﻛﭨﭨﮒ۰**:



1. ﻛﭨﭨﮒ۰ﻝﮔﮔ۷۰ﮒ



2. ﻛﭨﭨﮒ۰ﻟﺍﮒﭦ۵ﮔ۷۰ﮒ



3. ﻟﺟﮒﭦ۵ﻟﺓﻟﺕ۹ﮔ۷۰ﮒ



4. ﻝﭨﮔﮔﭘﻠﮔ۷۰ﮒ







**ﻠ۹ﮔﭘﮔﮒ**:



- ﻛﭨﭨﮒ۰ﻟﺍﮒﭦ۵ﮔ۲ﮒﺕﺕ



- ﻟﺟﮒﭦ۵ﻟﺓﻟﺕ۹ﮒﻝ۰؟







```---







### 10.3 Phase 3: ﻝ۴ﻟﺁﮒﭦﻠﮔﺅﺙWeek 5-6ﺅﺟ?



**ﻝ؟ﮔ**: ﮒ؟ﮔﻝ۴ﻟﺁﮒﭦﻠﺅﺟ?



**ﮒﺏﻠ؟ﻛﭨﭨﮒ۰**:



1. ﻝ۴ﻟﺁﮔﮒﮔ۷۰ﮒ



2. ﻝ۴ﻟﺁﮒ۴ﮒﭦﮔ۷۰ﮒ



3. ﻝ۴ﻟﺁﮔ۲ﻝﺑ۱ﮔ۷۰ﺅﺟ?4. ﻝ۴ﻟﺁﮔﺑﮔﺍﮔ۷۰ﮒ







**ﻠ۹ﮔﭘﮔﮒ**:



- ﻝ۴ﻟﺁﻟ۹ﮒ۷ﮒ۴ﮒﭦﺅﺟ?90%



- ﮔ۲ﻝﺑ۱ﻠﮒﭦ۵<1ﺅﺟ?



```---







### 10.4 Phase 4: ﮔﭖﻟﺁﮒﻛﺙﮒﺅﺙWeek 7-8ﺅﺟ?



**ﻝ؟ﮔ**: ﮒ؟ﮔﻝﺏﭨﻝﭨﮔﭖﻟﺁﮒﻛﺙﺅﺟ?



**ﮒﺏﻠ؟ﻛﭨﭨﮒ۰**:



1. ﮒﮒﮔﭖﻟﺁ



2. ﻠﮔﮔﭖﻟﺁ



3. ﮔ۶ﻟﺛﮔﭖﻟﺁ



4. ﻝﺏﭨﻝﭨﻛﺙﮒ







**ﻠ۹ﮔﭘﮔﮒ**:



- ﮔﮔﮔﭖﻟﺁﻠﻟﺟ



- ﻝﺏﭨﻝﭨﮔ۶ﻟﺛﻟﺝﺝﮔ







```---







**ﮔﮔﺁﻟ۶ﮔﺙﻛﺗ۵ﻝﮔ؛**: v1.0



**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-03



**ﻟﺁﮒ؟۰ﻝﭘﺅﺟﺛ?*: ﺅﺟ?ﮒﺓﺎﮔﺗﺅﺟ?



```
