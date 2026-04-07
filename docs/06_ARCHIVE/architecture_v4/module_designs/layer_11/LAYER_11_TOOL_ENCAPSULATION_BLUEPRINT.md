---
module_id: LAYER_030
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
responsibility:
  - 归档文档、历史版本
layer: Layer 3 (策略层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---
---


﻿---
module_id: LAYER_11_TOOL_ENCAPSULATION_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: é¦å¸­èå¾æ¶æå¸?standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 11æå­é©±å¨å±?compliance_level: ä¸ä¸æºææ å
parent_document: ../LAYER_11_ARCHITECTURE.md
implementation_status: è®¾è®¡é¶æ®µ
---

# Layer 11å·¥å·å°è£æ¹æ¡èå¾
> **核心职责**: Layer 11 Tool Encapsulation蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Layer 11 Tool Encapsulation蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


> æ¸é£éåäº¤æç³»ç» v5.2 - Layer 11å·¥å·å°è£è¯¦ç»è®¾è®¡
> **ç´¢å¼**: `LAYER_11_TOOL_ENCAP_001`
> **æ ¸å¿å®ä½**: ç»ä¸å·¥å·å°è£æ¶æï¼å®ç°åä¸AIäº¤äºå±?+ çº¯æ§è¡å±åç¦»
> **å³é®åå**: é¿åéå¤AIè°ç¨ï¼æåç³»ç»æç?

## ä¸ãè®¾è®¡èæ¯ä¸ç®æ 

### 1.1 é®é¢åæ

#### å½åæ¶æé®é¢

```
â?é®é¢æ¶æï¼ä¸¤æ¬¡AIè°ç¨ï¼ï¼

ç¨æ·è¾å¥: "åå»ºå¨éç­ç¥ï¼æä»?å¤?
    â?Layer 11 (AIçè§£)
    â?æå¾: éç½®ç­ç¥
    â?åæ°: {type: momentum, period: 5}
    â?è°ç¨ç­ç¥å¼æäº¤ä»ç³»ç» (AIåæ¬¡çè§£) â?åä½
    â?æå¾: éç½®ç­ç¥ (éå¤)
    â?åæ°: {type: momentum, period: 5} (éå¤)
    â?æ§è¡æä½

é®é¢ï¼?1. ä¸¤æ¬¡AIè°ç¨ï¼æçä½
2. éå¤çæå¾è¯å«ååæ°æå
3. ææ¬ç¿»åï¼APIè´¹ç¨ææ¨çæ¶é´ï¼
4. ç»´æ¤å¤æåº¦é«
```

#### ä¸ä¸æºææ­£ç¡®åæ³

```
â?æ­£ç¡®æ¶æï¼åæ¬¡AIè°ç¨ï¼ï¼

ç¨æ·è¾å¥: "åå»ºå¨éç­ç¥ï¼æä»?å¤?
    â?Layer 11 (AIçè§£) - å¯ä¸AIå±?    â?æå¾: éç½®ç­ç¥
    â?åæ°: {type: momentum, period: 5}
    â?è°ç¨ç­ç¥å¼æAPI (ç´æ¥æ§è¡ï¼æ AI) â?é«æ
    â?ç´æ¥æ§è¡ configure_strategy({type: momentum, period: 5})
    â?è¿åç»æ

ä¼å¿ï¼?1. åªæ1ä¸ªAIçè§£å±?2. æææ¨¡åéè¿å·¥å·è°ç¨
3. ç»´æ¤ææ¬ä½?4. ç¬¦åä¸ä¸æºæåæ³
```

### 1.2 è®¾è®¡ç®æ 

| ç®æ  | ä¼åçº?| ææ¯å®ç?|
|------|--------|----------|
| **åä¸AIäº¤äºå±?* | P0 | Layer 11æ¯å¯ä¸AIçè§£å±?|
| **çº¯æ§è¡å±åç¦»** | P0 | æææ¨¡ååªæä¾APIæ¥å£ï¼æ AI |
| **å·¥å·åå°è£?* | P0 | æ¯ä¸ªæ¨¡åå°è£ä¸ºå·¥å·ï¼éè¿LangChainè°ç¨ |
| **æ§è½ä¼å** | P1 | åå°AIè°ç¨æ¬¡æ°ï¼éä½å»¶è¿åææ¬ |
| **å¯ç»´æ¤æ?* | P1 | ç»ä¸å·¥å·æ¥å£ï¼æäºæ©å±åç»´æ¤ |

### 1.3 æ¶æåå

1. **åä¸èè´£åå**ï¼Layer 11è´è´£AIçè§£ï¼åæ¨¡åè´è´£æ§è¡
2. **æ¥å£éç¦»åå**ï¼å·¥å·æ¥å£æ¸æ°ï¼åæ°åè¿åå¼æç¡?3. **ä¾èµåç½®åå**ï¼å·¥å·ä¾èµäºæ½è±¡æ¥å£ï¼ä¸ä¾èµå·ä½å®ç°
4. **å¼é­åå?*ï¼å¯¹æ©å±å¼æ¾ï¼æ°å¢å·¥å·ï¼ï¼å¯¹ä¿®æ¹å°é­ï¼ç°æå·¥å·ï¼?

## äºãæ´ä½æ¶æè®¾è®?
### 2.1 æ¶æåå±

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?â? Layer 11: æå­é©±å¨å±ï¼å¯ä¸AIäº¤äºå±ï¼                         â?â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?â?â? â? ç¨æ·è¾å¥                                              â?â?â? â? "åå»ºå¨éç­ç¥ï¼æä»?å¤©ï¼æ­¢æ10%"                       â?â?â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?â?â?                         â?                                 â?â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?â?â? â? èªç¶è¯­è¨çè§£ (NLU)                                    â?â?â? â? - æå¾è¯å«: "éç½®ç­ç¥"                                â?â?â? â? - åæ°æå: {type: momentum, period: 5, stop_loss: 0.1}â?â?â? â? - å·¥å·éæ©: "ç­ç¥ç®¡çå·¥å·"                            â?â?â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?â?â?                         â?                                 â?â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?â?â? â? å·¥å·è·¯ç±å±?                                           â?â?â? â? æ ¹æ®æå¾éæ©å¯¹åºçå·¥å?                                â?â?â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?â?âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?                           â?        ââââââââââââââââââââ¼âââââââââââââââââââ?        â?                 â?                 â?ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?â? ç­ç¥å·¥å·     â? â? é£æ§å·¥å·     â? â? æ¥åå·¥å·     â?â? (æ AI)      â? â? (æ AI)      â? â? (æ AI)      â?ââââââââ¬ââââââââ? ââââââââ¬ââââââââ? ââââââââ¬ââââââââ?       â?                 â?                 â?ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?â? ç­ç¥å¼æ     â? â? é£æ§å¼æ     â? â? æ¥åå¼æ     â?â? (çº¯API)     â? â? (çº¯API)     â? â? (çº¯API)     â?ââââââââââââââââ? ââââââââââââââââ? ââââââââââââââââ?```

### 2.2 å·¥å·åç±»ä½ç³»

| å·¥å·ç±»å« | è¦çæ¨¡å | å·¥å·æ°é | ä¼åçº?|
|---------|---------|---------|--------|
| **ç­ç¥å·¥å·** | Layer 5 | 6ä¸?| P0 |
| **å å­å·¥å·** | Layer 2 | 4ä¸?| P0 |
| **é£æ§å·¥å·** | Layer 6 | 4ä¸?| P0 |
| **ææå·¥å·** | Layer 8 | 1ä¸?| P0 |
| **èæå·¥å·** | Layer 3 | 2ä¸?| P1 |
| **MLå·¥å·** | Layer 4 | 2ä¸?| P1 |
| **ç»åå·¥å·** | Layer 6 | 3ä¸?| P1 |
| **æ¥åå·¥å·** | Layer 7 | 2ä¸?| P1 |
| **æ°æ®æºå·¥å?* | Layer 0 | 4ä¸?| P2 |
| **é¢å¤çå·¥å?* | Layer 1 | 3ä¸?| P2 |
| **æ»è®¡** | - | **31ä¸?* | - |


## ä¸ãå·¥å·å°è£è§è?
### 3.1 å·¥å·åºç±»è®¾è®¡

```python
"""
å·¥å·åºç±»
ææå·¥å·å¿é¡»ç»§æ¿æ­¤ç±?"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain.tools import Tool

class BaseTool(ABC):
    """å·¥å·åºç±»"""
    
    def __init__(self, name: str, description: str):
        """
        åå§åå·¥å?        
        Args:
            name: å·¥å·åç§°
            description: å·¥å·æè¿°
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        æ§è¡å·¥å·ï¼å­ç±»å¿é¡»å®ç°ï¼
        
        Args:
            params: åæ°å­å¸ï¼ç±Layer 11 AIæåï¼?            
        Returns:
            æ§è¡ç»æå­å¸
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        éªè¯åæ°ï¼å­ç±»å¯éåï¼?        
        Args:
            params: åæ°å­å¸
            
        Returns:
            æ¯å¦ææ
        """
        return True
    
    def to_langchain_tool(self) -> Tool:
        """è½¬æ¢ä¸ºLangChainå·¥å·"""
        return Tool(
            name=self.name,
            func=lambda params: self.execute(params),
            description=self.description
        )
```

### 3.2 å·¥å·æ¥å£è§è

#### è¾å¥åæ°è§è

```python
{
    "action": "æä½ç±»å",  # å¿éï¼configure|start|stop|status|list
    "params": {            # å¿éï¼å·ä½åæ?        "param1": "value1",
        "param2": "value2"
    }
}
```

#### è¾åºç»æè§è

```python
{
    "success": True,       # å¿éï¼æ¯å¦æå?    "message": "æä½ç»ææè¿°",  # å¿éï¼ç»ææè¿?    "data": {              # å¯éï¼è¿åæ°æ®
        "key1": "value1",
        "key2": "value2"
    },
    "error": None          # å¯éï¼éè¯¯ä¿¡æ¯
}
```

### 3.3 å·¥å·å½åè§è

| è§èé¡?| æ ¼å¼ | ç¤ºä¾ |
|--------|------|------|
| **å·¥å·åç§°** | {æ¨¡åå}_{åè½} | ç­ç¥ç®¡çãå å­æ¥è¯?|
| **å·¥å·ç±»å** | {æ¨¡å}Tool | StrategyTool, FactorTool |
| **å·¥å·æä»¶å?* | {æ¨¡å}_tool.py | strategy_tool.py, factor_tool.py |
| **å·¥å·ID** | L11_TOOL_{æ¨¡å}_{åºå·} | L11_TOOL_STRATEGY_001 |


## åãæ ¸å¿å·¥å·è¯¦ç»è®¾è®?
### 4.1 ç­ç¥å·¥å·ï¼StrategyToolï¼?
**æä»¶ä½ç½®**: `src/layer_11/tools/strategy_tool.py`

```python
"""
ç­ç¥å·¥å·
å°è£ç­ç¥å¼æççº¯APIæ¥å£
"""
from typing import Dict, Any
from .base_tool import BaseTool

# å¯¼å¥ç­ç¥å¼æï¼çº¯æ§è¡å±ï¼æ AIï¼?from src.layer_5.strategy_engine import StrategyEngine

class StrategyTool(BaseTool):
    """ç­ç¥å·¥å·"""
    
    def __init__(self):
        """åå§åç­ç¥å·¥å?""
        super().__init__(
            name="ç­ç¥ç®¡ç",
            description="""ç®¡çäº¤æç­ç¥ï¼åæ¬éç½®ãå¯å¨ãåæ­¢ãæ¥è¯¢ç­æä½ã?
æ¯æçæä½ï¼
- configure: éç½®æ°ç­ç?- start: å¯å¨ç­ç¥
- stop: åæ­¢ç­ç¥
- status: æ¥è¯¢ç­ç¥ç¶æ?- list: ååºææç­ç?
åæ°æ ¼å¼ï¼?{
    "action": "configure",
    "params": {
        "strategy_type": "momentum",
        "holding_period": 5,
        "stop_loss": 0.1
    }
}
"""
        )
        # åå§åç­ç¥å¼æï¼çº¯æ§è¡å±ï¼æ AIï¼?        self.engine = StrategyEngine()
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        æ§è¡ç­ç¥æä½
        
        Args:
            params: {
                "action": "configure|start|stop|status|list",
                "params": {...}
            }
            
        Returns:
            æ§è¡ç»æ
        """
        action = params.get("action")
        action_params = params.get("params", {})
        
        # è·¯ç±å°å¯¹åºçæ§è¡æ¹æ³ï¼æ AIï¼ç´æ¥æ§è¡ï¼
        if action == "configure":
            return self.engine.configure_strategy(action_params)
        elif action == "start":
            return self.engine.start_strategy(action_params.get("strategy_id"))
        elif action == "stop":
            return self.engine.stop_strategy(action_params.get("strategy_id"))
        elif action == "status":
            return self.engine.get_strategy_status(action_params.get("strategy_id"))
        elif action == "list":
            return self.engine.list_strategies()
        else:
            return {"success": False, "error": f"æªç¥æä½ï¼{action}"}
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """éªè¯åæ°"""
        required_fields = ["action"]
        return all(field in params for field in required_fields)
```

### 4.2 å å­å·¥å·ï¼FactorToolï¼?
**æä»¶ä½ç½®**: `src/layer_11/tools/factor_tool.py`

```python
"""
å å­å·¥å·
å°è£å å­åºççº¯APIæ¥å£
"""
from typing import Dict, Any
from .base_tool import BaseTool

# å¯¼å¥å å­å¼æï¼çº¯æ§è¡å±ï¼æ AIï¼?from src.layer_2.factor_engine import FactorEngine

class FactorTool(BaseTool):
    """å å­å·¥å·"""
    
    def __init__(self):
        """åå§åå å­å·¥å?""
        super().__init__(
            name="å å­ç®¡ç",
            description="""ç®¡çå å­ï¼åæ¬æ¥è¯¢ãææãéªè¯ãçæ§ç­æä½ã?
æ¯æçæä½ï¼
- query: æ¥è¯¢å å­æ°æ®/è¡¨ç°
- mine: AIæææ°å å­?- validate: éªè¯å å­æææ?- monitor: çæ§å å­æ¼ç§»

åæ°æ ¼å¼ï¼?{
    "action": "query",
    "params": {
        "factor_name": "momentum",
        "start_date": "2026-01-01",
        "end_date": "2026-03-31"
    }
}
"""
        )
        # åå§åå å­å¼æï¼çº¯æ§è¡å±ï¼æ AIï¼?        self.engine = FactorEngine()
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """æ§è¡å å­æä½"""
        action = params.get("action")
        action_params = params.get("params", {})
        
        # è·¯ç±å°å¯¹åºçæ§è¡æ¹æ³ï¼æ AIï¼ç´æ¥æ§è¡ï¼
        if action == "query":
            return self.engine.query_factor(action_params)
        elif action == "mine":
            return self.engine.mine_factor(action_params)
        elif action == "validate":
            return self.engine.validate_factor(action_params)
        elif action == "monitor":
            return self.engine.monitor_factor(action_params)
        else:
            return {"success": False, "error": f"æªç¥æä½ï¼{action}"}
```

### 4.3 é£æ§å·¥å·ï¼RiskControlToolï¼?
**æä»¶ä½ç½®**: `src/layer_11/tools/risk_control_tool.py`

```python
"""
é£æ§å·¥å·
å°è£é£æ§ç®¡çççº¯APIæ¥å£
"""
from typing import Dict, Any
from .base_tool import BaseTool

# å¯¼å¥é£æ§ç®¡çå¨ï¼çº¯æ§è¡å±ï¼æ AIï¼?from src.layer_6.risk_manager import RiskManager

class RiskControlTool(BaseTool):
    """é£æ§å·¥å·"""
    
    def __init__(self):
        """åå§åé£æ§å·¥å?""
        super().__init__(
            name="é£æ§ç®¡ç",
            description="""ç®¡çé£é©æ§å¶ï¼åæ¬è°æ´åæ°ãè®¾ç½®æ­¢ææ­¢çç­æä½ã?
æ¯æçæä½ï¼
- adjust_params: è°æ´é£æ§åæ°
- set_stop_loss: è®¾ç½®æ­¢æ
- set_take_profit: è®¾ç½®æ­¢ç
- get_risk_report: è·åé£é©æ¥å

åæ°æ ¼å¼ï¼?{
    "action": "adjust_params",
    "params": {
        "max_drawdown": 0.10,
        "position_limit": 0.05
    }
}
"""
        )
        # åå§åé£æ§ç®¡çå¨ï¼çº¯æ§è¡å±ï¼æ AIï¼?        self.manager = RiskManager()
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """æ§è¡é£æ§æä½"""
        action = params.get("action")
        action_params = params.get("params", {})
        
        # è·¯ç±å°å¯¹åºçæ§è¡æ¹æ³ï¼æ AIï¼ç´æ¥æ§è¡ï¼
        if action == "adjust_params":
            return self.manager.adjust_risk_params(action_params)
        elif action == "set_stop_loss":
            return self.manager.set_stop_loss(action_params)
        elif action == "set_take_profit":
            return self.manager.set_take_profit(action_params)
        elif action == "get_risk_report":
            return self.manager.get_risk_report()
        else:
            return {"success": False, "error": f"æªç¥æä½ï¼{action}"}
```

### 4.4 æ°æ®æºå·¥å·ï¼DataSourceToolï¼?
**æä»¶ä½ç½®**: `src/layer_11/tools/data_source_tool.py`

```python
"""
æ°æ®æºå·¥å?å°è£æ°æ®æºç®¡çççº¯APIæ¥å£
"""
from typing import Dict, Any
from .base_tool import BaseTool

# å¯¼å¥æ°æ®æºç®¡çå¨ï¼çº¯æ§è¡å±ï¼æ AIï¼?from src.layer_0.data_source_manager import DataSourceManager

class DataSourceTool(BaseTool):
    """æ°æ®æºå·¥å?""
    
    def __init__(self):
        """åå§åæ°æ®æºå·¥å·"""
        super().__init__(
            name="æ°æ®æºç®¡ç?,
            description="""ç®¡çæ°æ®æºï¼åæ¬éç½®ãæµè¯ãæ¥è¯¢ç­æä½ã?
æ¯æçæä½ï¼
- configure_qmt: éç½®QMTæ°æ®æº?- configure_ifind: éç½®iFindæ°æ®æº?- test_connection: æµè¯æ°æ®æºè¿æ?- status: æ¥è¯¢æ°æ®æºç¶æ?
åæ°æ ¼å¼ï¼?{
    "action": "configure_qmt",
    "params": {
        "account": "your_account",
        "password": "your_password"
    }
}
"""
        )
        # åå§åæ°æ®æºç®¡çå¨ï¼çº¯æ§è¡å±ï¼æ AIï¼?        self.manager = DataSourceManager()
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """æ§è¡æ°æ®æºæä½?""
        action = params.get("action")
        action_params = params.get("params", {})
        
        # è·¯ç±å°å¯¹åºçæ§è¡æ¹æ³ï¼æ AIï¼ç´æ¥æ§è¡ï¼
        if action == "configure_qmt":
            return self.manager.configure_qmt(action_params)
        elif action == "configure_ifind":
            return self.manager.configure_ifind(action_params)
        elif action == "test_connection":
            return self.manager.test_connection(action_params.get("source"))
        elif action == "status":
            return self.manager.get_status()
        else:
            return {"success": False, "error": f"æªç¥æä½ï¼{action}"}
```


## äºãå·¥å·æ³¨åä¸­å¿?
### 5.1 æ³¨åä¸­å¿è®¾è®¡

**æä»¶ä½ç½®**: `src/layer_11/tools/__init__.py`

```python
"""
å·¥å·æ³¨åä¸­å¿
æ³¨åææå·¥å·å¹¶æä¾ç»ä¸è®¿é®æ¥å£
"""
from typing import List
from langchain.tools import Tool

from .base_tool import BaseTool
from .strategy_tool import StrategyTool
from .factor_tool import FactorTool
from .risk_control_tool import RiskControlTool
from .data_source_tool import DataSourceTool
from .report_tool import ReportTool

class ToolRegistry:
    """å·¥å·æ³¨åä¸­å¿"""
    
    def __init__(self):
        """åå§åå·¥å·æ³¨åä¸­å¿?""
        self.tools = {}
        self._register_all_tools()
    
    def _register_all_tools(self):
        """æ³¨åææå·¥å?""
        # æ³¨åP0å·¥å·
        self.register(StrategyTool())
        self.register(FactorTool())
        self.register(RiskControlTool())
        
        # æ³¨åP1å·¥å·
        self.register(DataSourceTool())
        self.register(ReportTool())
        
        # ... æ³¨åå¶ä»å·¥å·
    
    def register(self, tool: BaseTool):
        """æ³¨åå·¥å·"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        """è·åå·¥å·"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[Tool]:
        """è·åææLangChainå·¥å·"""
        return [tool.to_langchain_tool() for tool in self.tools.values()]


def get_all_tools() -> List[Tool]:
    """è·åææå·¥å·ï¼ä¾¿æ·å½æ°ï¼?""
    registry = ToolRegistry()
    return registry.get_all_tools()
```

### 5.2 å·¥å·æ³¨åè¡?
| å·¥å·åç§° | å·¥å·ç±?| ä¼åçº?| ç¶æ?|
|---------|--------|--------|------|
| ç­ç¥ç®¡ç | StrategyTool | P0 | â?å·²è®¾è®?|
| å å­ç®¡ç | FactorTool | P0 | â?å·²è®¾è®?|
| é£æ§ç®¡ç | RiskControlTool | P0 | â?å·²è®¾è®?|
| ææç¡®è®¤ | ApprovalTool | P0 | ð å¾å¼å?|
| èææ¥è¯¢ | SentimentTool | P1 | ð å¾å¼å?|
| æ¨¡åè®­ç» | MLTool | P1 | ð å¾å¼å?|
| ç»åä¼å | PortfolioTool | P1 | ð å¾å¼å?|
| æ¥åæ¥è¯¢ | ReportTool | P1 | â?å·²è®¾è®?|
| æ°æ®æºç®¡ç?| DataSourceTool | P2 | â?å·²è®¾è®?|
| æ°æ®é¢å¤ç?| PreprocessingTool | P2 | ð å¾å¼å?|


## å­ãAgentéææ¹æ¡

### 6.1 Agentè°ç¨æµç¨

```python
"""
éåäº¤æAgentï¼å¯ä¸AIäº¤äºå±ï¼
"""
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

# å¯¼å¥å·¥å·æ³¨åä¸­å¿
from ..tools import get_all_tools

class QuantTradingAgent:
    """éåäº¤æAgent"""
    
    def __init__(self, model_name: str = "deepseek-r1:14b"):
        """åå§åAgent"""
        # 1. åå§åLLMï¼å¯ä¸AIå±ï¼
        self.llm = ChatOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            model=model_name,
            temperature=0.1
        )
        
        # 2. è·åææå·¥å·ï¼çº¯æ§è¡å±ï¼æ AIï¼?        self.tools = get_all_tools()
        
        # 3. åå§åè®°å¿?        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 4. åå»ºAgent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            memory=self.memory,
            system_prompt=self._get_system_prompt()
        )
    
    def chat(self, user_input: str) -> str:
        """
        ä¸Agentå¯¹è¯
        
        æµç¨ï¼?        1. AIçè§£ç¨æ·æå¾
        2. AIæååæ°
        3. AIéæ©å·¥å·
        4. è°ç¨å·¥å·ï¼çº¯æ§è¡ï¼æ AIï¼?        5. AIæ ¼å¼åç»æ?        """
        result = self.agent.invoke({"input": user_input})
        return result["output"]
    
    def _get_system_prompt(self) -> str:
        """ç³»ç»æç¤ºè¯?""
        return """ä½ æ¯ZephyrAlphaéåäº¤æç³»ç»çAIå©æã?
## å·¥ä½æµç¨
1. çè§£ç¨æ·æå¾
2. æåå³é®åæ°
3. éæ©åéçå·¥å·
4. è°ç¨å·¥å·æ§è¡ï¼å·¥å·åé¨æ AIï¼ç´æ¥æ§è¡ï¼
5. å°ç»æè½¬æ¢ä¸ºèªç¶è¯­è¨åé¦

## éè¦æç¤º
- ä½ æ¯å¯ä¸çAIäº¤äºå±?- å·¥å·åé¨ä¸åæAIçè§£ï¼ç´æ¥æ§è¡?- ç¡®ä¿åæ°æååç¡®ï¼é¿åéå¤è°ç?"""
```

### 6.2 è°ç¨ç¤ºä¾

```python
# ç¨æ·è¾å¥
user_input = "åå»ºä¸ä¸ªå¨éå å­ç­ç¥ï¼æä»5å¤©ï¼æ­¢æ10%"

# Agentå¤çæµç¨
agent = QuantTradingAgent()
result = agent.chat(user_input)

# åé¨æµç¨
"""
1. AIçè§£æå¾: "éç½®ç­ç¥"
2. AIæååæ°: {strategy_type: "momentum", holding_period: 5, stop_loss: 0.1}
3. AIéæ©å·¥å·: "ç­ç¥ç®¡çå·¥å·"
4. è°ç¨å·¥å·: StrategyTool.execute({
       "action": "configure",
       "params": {
           "strategy_type": "momentum",
           "holding_period": 5,
           "stop_loss": 0.1
       }
   })
5. å·¥å·æ§è¡: ç­ç¥å¼æ.configure_strategy(...) (æ AIï¼ç´æ¥æ§è¡?
6. AIæ ¼å¼åç»æ? "ç­ç¥éç½®æåï¼ç­ç¥ID: STRAT_001"
"""

print(result)
# è¾åº: "ç­ç¥éç½®æåï¼ç­ç¥ID: STRAT_001"
```


## ä¸ãæ§è½ä¼åæ¹æ¡

### 7.1 æ§è½å¯¹æ¯

| ææ  | éæåï¼ä¸¤æ¬¡AIï¼?| éæåï¼åæ¬¡AIï¼?| æå |
|------|-----------------|-----------------|------|
| **ååºæ¶é´** | 2-4ç§?| 1-2ç§?| 50%â?|
| **APIææ¬** | 2å?| 1å?| 50%â?|
| **æ¨çæ¬¡æ°** | 2æ¬?| 1æ¬?| 50%â?|
| **ç»´æ¤å¤æåº?* | é«?| ä½?| æ¾èéä½ |

### 7.2 ç¼å­ç­ç¥

```python
class ToolCache:
    """å·¥å·ç¼å­"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def get(self, key: str):
        """è·åç¼å­"""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any):
        """è®¾ç½®ç¼å­"""
        if len(self.cache) >= self.max_size:
            # LRUæ·æ±°ç­ç¥
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
```


## å«ãå®æ½è·¯çº¿å¾

### Phase 1ï¼æ ¸å¿å·¥å·å¼åï¼Week 1-2ï¼?
**ç®æ **: å®æP0å·¥å·å¼å?
```yaml
å·¥ä½åå®¹:
  1. ç­ç¥å·¥å·å¼å?     - å°è£ç­ç¥å¼æAPI
     - å®ç°configure/start/stop/status/listæä½
  
  2. å å­å·¥å·å¼å?     - å°è£å å­å¼æAPI
     - å®ç°query/mine/validate/monitoræä½
  
  3. é£æ§å·¥å·å¼å?     - å°è£é£æ§å¼æAPI
     - å®ç°adjust_params/set_stop_lossç­æä½?  
  4. ææå·¥å·å¼å?     - å°è£ææç¡®è®¤API
     - å®ç°å³é®å³ç­ææ

äº¤ä»ç?
  - 4ä¸ªå·¥å·æä»?  - å·¥å·æ³¨åä¸­å¿
  - ååæµè¯
```

### Phase 2ï¼æ©å±å·¥å·å¼åï¼Week 3-4ï¼?
**ç®æ **: å®æP1-P2å·¥å·å¼å?
```yaml
å·¥ä½åå®¹:
  1. èæå·¥å·å¼å?  2. MLå·¥å·å¼å?  3. ç»åå·¥å·å¼å?  4. æ¥åå·¥å·å¼å?  5. æ°æ®æºå·¥å·å¼å?  6. é¢å¤çå·¥å·å¼å?
äº¤ä»ç?
  - 6ä¸ªå·¥å·æä»?  - éææµè¯
```

### Phase 3ï¼ä¼åå®åï¼Week 5-6ï¼?
**ç®æ **: æ§è½ä¼ååææ¡£å®å?
```yaml
å·¥ä½åå®¹:
  1. æ§è½ä¼å
     - å·¥å·ç¼å­
     - å¹¶åæ§å¶
     - éè¯¯å¤ç
  
  2. ææ¡£å®å
     - å·¥å·ä½¿ç¨ææ¡£
     - APIææ¡£
     - ç¤ºä¾ä»£ç 
  
  3. æµè¯éªè¯
     - ååæµè¯
     - éææµè¯
     - æ§è½æµè¯

äº¤ä»ç?
  - å®æ´çæµè¯å¥ä»?  - ç¨æ·æå
  - APIææ¡£
```


## ä¹ãé£é©è¯ä¼°ä¸ç¼è§£

### 9.1 ææ¯é£é?
| é£é© | å½±å | æ¦ç | ç¼è§£æªæ½ |
|------|------|------|----------|
| **å·¥å·æ¥å£ä¸ç»ä¸** | é«?| ä¸?| å¶å®ä¸¥æ ¼çæ¥å£è§è?|
| **åæ°æåéè¯¯** | é«?| ä¸?| AIåæ°æåéªè¯æºå¶ |
| **æ§è½ç¶é¢** | ä¸?| ä½?| å·¥å·ç¼å­ãå¹¶åæ§å?|
| **å·¥å·ä¾èµå²çª** | ä¸?| ä½?| ä¾èµéç¦»ãçæ¬ç®¡ç?|

### 9.2 å®æ½é£é©

| é£é© | å½±å | æ¦ç | ç¼è§£æªæ½ |
|------|------|------|----------|
| **éæå·¥ä½éè¶é¢æ** | é«?| ä¸?| åé¶æ®µå®æ½ãä¼åçº§ç®¡ç |
| **ç°æç³»ç»å¼å®¹æ?* | é«?| ä¸?| ååæµè¯ãæ¸è¿å¼è¿ç§» |
| **ææ¡£æ´æ°æ»å** | ä¸?| é«?| åæ­¥æ´æ°ææ¡£ãææ¡£å®¡è®?|


## åãç¸å³ææ¡£ç´¢å¼?
### 10.1 æ ¸å¿åèææ¡?
| ææ¡£åç§° | è·¯å¾ | è¯´æ |
|---------|------|------|
| [Layer 11æ¶æèå¾](./LAYER_11_ARCHITECTURE.md) | `docs/module_designs/layer_11/LAYER_11_ARCHITECTURE.md` | Layer 11æ´ä½æ¶æ |
| [æå­é©±å¨æ ¸å¿æ¨¡å](./L11_TEXT_DRIVER.md) | `docs/module_designs/layer_11/L11_TEXT_DRIVER.md` | NLUè®¾è®¡ |
| [éåäº¤æAgentæ¨¡å](./L11_QUANT_AGENT.md) | `docs/module_designs/layer_11/L11_QUANT_AGENT.md` | Agentæ¡æ¶ |
| [ç­ç¥å¼æèå¾](06_ARCHIVE\architecture_v4\03_TRADING_TACTICS\01_STRATEGY_FRAMEWORK\STRATEGY_ENGINE_CORE_BLUEPRINT.md) | `docs/03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/STRATEGY_ENGINE_CORE_BLUEPRINT.md` | ç­ç¥å¼æè®¾è®¡ |

### 10.2 ä»£ç å®ç°ä½ç½®

| æ¨¡å | è·¯å¾ | è¯´æ |
|------|------|------|
| å·¥å·åºç±» | `src/layer_11/tools/base_tool.py` | å·¥å·åºç±»å®ä¹ |
| ç­ç¥å·¥å· | `src/layer_11/tools/strategy_tool.py` | ç­ç¥å·¥å·å®ç° |
| å å­å·¥å· | `src/layer_11/tools/factor_tool.py` | å å­å·¥å·å®ç° |
| é£æ§å·¥å· | `src/layer_11/tools/risk_control_tool.py` | é£æ§å·¥å·å®ç° |
| å·¥å·æ³¨åä¸­å¿ | `src/layer_11/tools/__init__.py` | å·¥å·æ³¨åç®¡ç |

---

**ææ¡£çæ¬**: v1.0.0
**æåæ´æ?*: 2026-04-02
**ç»´æ¤è?*: é¦å¸­èå¾æ¶æå¸?
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Layer 11 Tool Encapsulation
- **模块ID**: LAYER_11_TOOL_ENCAPSULATION_001
- **蓝图文档**: [LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md](06_ARCHIVE\architecture_v4\module_designs\layer_11\LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: Layer 11æå­é©±å¨å±?compliance_level: ä¸ä¸æºææ å
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Layer 11 Tool Encapsulation** | Layer 11æå­é©±å¨å±?compliance_level: ä¸ä¸æºææ å | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-02 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-02 | **状态**: Active
