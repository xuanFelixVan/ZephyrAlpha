---
module_id: L11_QUANT_AGENT_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席文档架构师
layer: Layer 11
module_type: 核心模块
priority: P0
estimated_hours: 30
standard_type: 设计文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# L11_QUANT_AGENT: 量化交易Agent模块设计文档

> **版本**: v1.0  
> **创建日期**: 2026-04-02  
> **所属层级**: Layer 11 - 文字驱动层  
> **设计状态**: ✅ 设计完成  
> **优先级**: P0 (核心模块)

---

## 📋 目录

- [1. 模块概述](#1-模块概述)
- [2. Agent架构](#2-agent架构)
- [3. 模型管理](#3-模型管理)
- [4. 工具集成](#4-工具集成)
- [5. 记忆管理](#5-记忆管理)
- [6. 安全机制](#6-安全机制)
- [7. 性能优化](#7-性能优化)
- [8. 测试方案](#8-测试方案)

---

## 1. 模块概述

### 1.1 功能定位

**L11_QUANT_AGENT**是Layer 11的智能Agent模块，基于LangChain 1.0构建，负责智能推理和工具调用。

**核心职责**：
- 🧠 **智能推理**：基于LLM进行复杂推理
- 🔧 **工具调用**：调用量化交易工具集
- 💭 **记忆管理**：管理对话历史和长期记忆
- 🛡️ **安全控制**：PII检测和权限控制
- 📊 **性能监控**：监控Agent性能指标

### 1.2 技术栈

```yaml
核心框架:
  - LangChain 1.0: Agent框架
  - LangGraph: 状态图执行引擎
  - LangSmith: 监控和调试平台

模型支持:
  本地模型:
    - deepseek-r1:14b (推理强)
    - qwen2.5-coder:14b (编程强)
    - qwen3-coder:30b (综合最强)
  
  云端API:
    - GPT-4 Turbo (OpenAI)
    - Claude 3.5 Sonnet (Anthropic)
    - Qwen-Max (阿里云)

工具集成:
  - QuantTradingTools (量化交易工具)
  - SystemTools (系统管理工具)
  - DataTools (数据分析工具)
```

### 1.3 模块边界

```yaml
输入:
  - 用户意图
  - 提取的参数
  - 对话上下文

输出:
  - 工具调用决策
  - 执行结果
  - 智能建议

不包含:
  - 自然语言理解 (由TEXT_DRIVER负责)
  - UI渲染 (由WEB_UI负责)
  - 工具实现 (由TOOLS负责)
```

---

## 2. Agent架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│  QuantTradingAgent                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │  ModelManager (模型管理)                         │   │
│  │  ├─ LocalModelManager (本地模型)                │   │
│  │  └─ CloudModelManager (云端模型)                │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↓                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  AgentCore (Agent核心)                          │   │
│  │  ├─ ReActLoop (推理循环)                        │   │
│  │  ├─ ToolSelector (工具选择)                     │   │
│  │  └─ DecisionMaker (决策器)                      │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↓                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  ToolIntegration (工具集成)                      │   │
│  │  ├─ QuantTools (量化工具)                       │   │
│  │  ├─ SystemTools (系统工具)                      │   │
│  │  └─ DataTools (数据工具)                        │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↓                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MemoryManager (记忆管理)                        │   │
│  │  ├─ ConversationMemory (对话记忆)               │   │
│  │  ├─ LongTermMemory (长期记忆)                   │   │
│  │  └─ WorkingMemory (工作记忆)                    │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↓                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  SecurityLayer (安全层)                          │   │
│  │  ├─ PIIDetector (PII检测)                       │   │
│  │  ├─ PermissionChecker (权限检查)                │   │
│  │  └─ AuditLogger (审计日志)                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 ReAct循环

**LangChain 1.0标准化ReAct循环**：

```python
# ReAct循环：Reason → Act → Observe → Decide

class ReActLoop:
    """ReAct推理循环"""
    
    def execute(self, user_input: str) -> str:
        """执行ReAct循环"""
        
        # 1. Reason (推理)
        thought = self.reason(user_input)
        
        # 2. Act (行动)
        action = self.act(thought)
        
        # 3. Observe (观察)
        observation = self.observe(action)
        
        # 4. Decide (决策)
        decision = self.decide(observation)
        
        # 循环直到得到最终答案
        while not decision.is_final:
            thought = self.reason(observation)
            action = self.act(thought)
            observation = self.observe(action)
            decision = self.decide(observation)
        
        return decision.answer
```

### 2.3 核心类设计

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

class QuantTradingAgent:
    """量化交易AI Agent"""
    
    def __init__(self, config: dict):
        """
        初始化Agent
        
        Args:
            config: 配置字典
                - model_name: 模型名称
                - tools: 工具列表
                - system_prompt: 系统提示词
        """
        # 1. 初始化模型
        self.llm = self._init_model(config["model_name"])
        
        # 2. 初始化工具
        self.tools = config["tools"]
        
        # 3. 初始化记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 4. 系统提示词
        self.system_prompt = config.get("system_prompt", self._default_prompt())
        
        # 5. 创建Agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            memory=self.memory,
            system_prompt=self.system_prompt
        )
    
    def _init_model(self, model_name: str):
        """初始化模型"""
        
        if model_name in ["gpt-4-turbo", "gpt-4", "claude-3"]:
            # 云端API
            return ChatOpenAI(
                model=model_name,
                temperature=0.1
            )
        else:
            # 本地Ollama
            return ChatOpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
                model=model_name,
                temperature=0.1
            )
    
    def chat(self, user_input: str) -> str:
        """
        与Agent对话
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent回复
        """
        try:
            result = self.agent.invoke({"input": user_input})
            return result["output"]
        except Exception as e:
            return f"抱歉，处理您的请求时出现错误：{str(e)}"
    
    def _default_prompt(self) -> str:
        """默认系统提示词"""
        return """你是ZephyrAlpha量化交易系统的AI助手，专门帮助用户通过自然语言操作量化交易系统。

## 你的身份
- 专业量化交易顾问
- 系统操作助手
- 风险管理专家

## 你的能力
1. **策略配置**：理解用户的策略描述，提取参数并配置
2. **风控调整**：理解风险偏好，调整风控参数
3. **状态查询**：查询系统状态并用自然语言反馈
4. **回测分析**：运行策略回测，分析结果
5. **智能建议**：根据市场情况给出专业建议

## 工作流程
1. 分析用户意图（配置/查询/调整/建议）
2. 提取关键参数
3. 调用对应的系统工具
4. 将结果转换为友好的自然语言反馈

## 专业术语映射
- "动量策略" → momentum
- "价值策略" → value
- "质量策略" → quality
- "成长策略" → growth
- "持仓5天" → holding_period=5
- "止损10%" → stop_loss=0.10
- "最大回撤15%" → max_drawdown=0.15
- "单只仓位5%" → position_limit=0.05

## 回复风格
- 专业但不晦涩
- 简洁但不失细节
- 友好但保持专业
- 提供数据支持建议

## 重要提示
- 所有参数必须通过工具调用，不能直接执行
- 涉及资金的操作需要用户确认
- 提供数据支持的建议，不给出绝对承诺
"""
```

---

## 3. 模型管理

### 3.1 本地模型管理

```python
class LocalModelManager:
    """本地模型管理器"""
    
    def __init__(self):
        self.models = {
            "deepseek-r1:8b": {
                "size": "5.2GB",
                "vram": "~6GB",
                "strength": "推理快",
                "use_case": "简单查询"
            },
            "deepseek-r1:14b": {
                "size": "9.0GB",
                "vram": "~10GB",
                "strength": "推理强",
                "use_case": "策略配置"
            },
            "qwen2.5-coder:14b": {
                "size": "9.0GB",
                "vram": "~10GB",
                "strength": "编程强",
                "use_case": "代码生成"
            },
            "qwen3-coder:30b": {
                "size": "18GB",
                "vram": "~20GB",
                "strength": "综合最强",
                "use_case": "复杂分析"
            }
        }
    
    def get_model(self, model_name: str) -> ChatOpenAI:
        """获取模型实例"""
        return ChatOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            model=model_name,
            temperature=0.1
        )
    
    def check_availability(self, model_name: str) -> bool:
        """检查模型是否可用"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags")
            models = response.json().get("models", [])
            return any(m["name"] == model_name for m in models)
        except:
            return False
```

### 3.2 云端模型管理

```python
class CloudModelManager:
    """云端模型管理器"""
    
    def __init__(self, api_keys: dict):
        self.api_keys = api_keys
        self.models = {
            "gpt-4-turbo": {
                "provider": "openai",
                "cost": "¥0.03/1k tokens",
                "strength": "推理最强"
            },
            "claude-3.5-sonnet": {
                "provider": "anthropic",
                "cost": "¥0.02/1k tokens",
                "strength": "长文本分析"
            },
            "qwen-max": {
                "provider": "alibaba",
                "cost": "¥0.01/1k tokens",
                "strength": "中文理解"
            }
        }
    
    def get_model(self, model_name: str) -> ChatOpenAI:
        """获取模型实例"""
        
        if model_name.startswith("gpt"):
            return ChatOpenAI(
                model=model_name,
                api_key=self.api_keys["openai"],
                temperature=0.1
            )
        elif model_name.startswith("claude"):
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=model_name,
                api_key=self.api_keys["anthropic"],
                temperature=0.1
            )
        # ... 其他模型
```

### 3.3 智能路由

```python
class ModelRouter:
    """模型智能路由"""
    
    def __init__(self, local_manager, cloud_manager):
        self.local = local_manager
        self.cloud = cloud_manager
    
    def route(self, user_input: str, intent: str) -> str:
        """智能路由到合适的模型"""
        
        # 1. 简单查询 → 本地小模型
        if intent == "query_status":
            return "deepseek-r1:8b"
        
        # 2. 策略配置 → 本地中模型
        elif intent == "configure_strategy":
            return "deepseek-r1:14b"
        
        # 3. 代码生成 → 本地编程模型
        elif intent == "generate_code":
            return "qwen2.5-coder:14b"
        
        # 4. 复杂分析 → 本地大模型
        elif intent == "complex_analysis":
            return "qwen3-coder:30b"
        
        # 5. 紧急任务 → 云端API
        elif intent == "urgent_task":
            return "gpt-4-turbo"
        
        # 6. 默认 → 本地中模型
        else:
            return "deepseek-r1:14b"
    
    def get_model_instance(self, model_name: str):
        """获取模型实例"""
        
        # 检查是否为本地模型
        if model_name in self.local.models:
            if self.local.check_availability(model_name):
                return self.local.get_model(model_name)
        
        # 回退到云端模型
        return self.cloud.get_model(model_name)
```

---

## 4. 工具集成

### 4.1 工具注册

```python
from langchain.tools import Tool

class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, func: callable, description: str):
        """注册工具"""
        self.tools[name] = Tool(
            name=name,
            func=func,
            description=description
        )
    
    def get_tool(self, name: str) -> Tool:
        """获取工具"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> list:
        """获取所有工具"""
        return list(self.tools.values())
```

### 4.2 工具分类

```python
class ToolCategories:
    """工具分类"""
    
    # 策略管理工具
    STRATEGY_TOOLS = [
        "配置策略",
        "修改策略",
        "删除策略",
        "启动策略",
        "停止策略"
    ]
    
    # 风控管理工具
    RISK_TOOLS = [
        "调整风控参数",
        "设置止损止盈",
        "调整仓位限制"
    ]
    
    # 数据查询工具
    QUERY_TOOLS = [
        "查询持仓",
        "查询委托",
        "查询成交",
        "查询资金",
        "查询系统状态"
    ]
    
    # 系统管理工具
    SYSTEM_TOOLS = [
        "查看日志",
        "导出报告",
        "系统配置"
    ]
    
    # 回测分析工具
    BACKTEST_TOOLS = [
        "运行回测",
        "查看回测结果",
        "优化参数"
    ]
```

### 4.3 工具调用流程

```python
class ToolExecutor:
    """工具执行器"""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
    
    def execute(self, tool_name: str, params: dict) -> dict:
        """执行工具"""
        
        # 1. 获取工具
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"工具 {tool_name} 不存在"
            }
        
        # 2. 参数验证
        validated_params = self._validate_params(tool, params)
        
        # 3. 执行工具
        try:
            result = tool.func(validated_params)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_params(self, tool: Tool, params: dict) -> dict:
        """验证参数"""
        # 参数验证逻辑
        return params
```

---

## 5. 记忆管理

### 5.1 对话记忆

```python
from langchain.memory import ConversationBufferMemory

class ConversationMemory:
    """对话记忆"""
    
    def __init__(self, max_history: int = 100):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.max_history = max_history
    
    def add(self, role: str, content: str):
        """添加对话"""
        if role == "user":
            self.memory.chat_memory.add_user_message(content)
        else:
            self.memory.chat_memory.add_ai_message(content)
    
    def get_history(self, last_n: int = None) -> list:
        """获取历史"""
        history = self.memory.chat_memory.messages
        if last_n:
            return history[-last_n:]
        return history
    
    def clear(self):
        """清空记忆"""
        self.memory.clear()
```

### 5.2 长期记忆

```python
from langchain.vectorstores import Milvus
from langchain.embeddings import OpenAIEmbeddings

class LongTermMemory:
    """长期记忆（向量数据库）"""
    
    def __init__(self, collection_name: str = "quant_memory"):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Milvus(
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
    
    def store(self, text: str, metadata: dict = None):
        """存储记忆"""
        self.vectorstore.add_texts(
            texts=[text],
            metadatas=[metadata] if metadata else None
        )
    
    def retrieve(self, query: str, k: int = 5) -> list:
        """检索记忆"""
        results = self.vectorstore.similarity_search(
            query=query,
            k=k
        )
        return results
```

### 5.3 工作记忆

```python
class WorkingMemory:
    """工作记忆（当前会话状态）"""
    
    def __init__(self):
        self.state = {
            "current_strategy": None,
            "current_task": None,
            "user_preferences": {},
            "context": {}
        }
    
    def update(self, key: str, value: Any):
        """更新状态"""
        self.state[key] = value
    
    def get(self, key: str) -> Any:
        """获取状态"""
        return self.state.get(key)
    
    def clear(self):
        """清空状态"""
        self.state = {
            "current_strategy": None,
            "current_task": None,
            "user_preferences": {},
            "context": {}
        }
```

---

## 6. 安全机制

### 6.1 PII检测

```python
import re

class PIIDetector:
    """PII检测器"""
    
    def __init__(self):
        self.patterns = {
            "phone": r"\d{11}",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "id_card": r"\d{17}[\dXx]",
            "bank_card": r"\d{16,19}"
        }
    
    def detect(self, text: str) -> list:
        """检测PII"""
        detected = []
        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected.append({
                    "type": pii_type,
                    "matches": matches
                })
        return detected
    
    def mask(self, text: str) -> str:
        """脱敏"""
        for pii_type, pattern in self.patterns.items():
            text = re.sub(pattern, f"[{pii_type.upper()}_MASKED]", text)
        return text
```

### 6.2 权限控制

```python
class PermissionChecker:
    """权限检查器"""
    
    def __init__(self):
        self.permissions = {
            "guest": ["query_status"],
            "user": ["query_status", "configure_strategy", "run_backtest"],
            "admin": ["query_status", "configure_strategy", "run_backtest", "system_config"]
        }
    
    def check(self, user_role: str, action: str) -> bool:
        """检查权限"""
        allowed_actions = self.permissions.get(user_role, [])
        return action in allowed_actions
```

### 6.3 审计日志

```python
import logging
from datetime import datetime

class AuditLogger:
    """审计日志"""
    
    def __init__(self, log_file: str = "logs/audit.log"):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
    
    def log(self, user: str, action: str, details: dict):
        """记录审计日志"""
        self.logger.info({
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "details": details
        })
```

---

## 7. 性能优化

### 7.1 模型缓存

```python
from functools import lru_cache

class ModelCache:
    """模型缓存"""
    
    @lru_cache(maxsize=10)
    def get_model(self, model_name: str):
        """获取模型（带缓存）"""
        return ChatOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            model=model_name,
            temperature=0.1
        )
```

### 7.2 并发控制

```python
from concurrent.futures import ThreadPoolExecutor

class ConcurrentExecutor:
    """并发执行器"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def execute(self, func: callable, *args, **kwargs):
        """并发执行"""
        future = self.executor.submit(func, *args, **kwargs)
        return future.result()
```

### 7.3 性能监控

```python
import time

class PerformanceMonitor:
    """性能监控"""
    
    def __init__(self):
        self.metrics = {
            "response_time": [],
            "tool_call_time": [],
            "model_inference_time": []
        }
    
    def record(self, metric: str, value: float):
        """记录指标"""
        self.metrics[metric].append(value)
    
    def get_stats(self, metric: str) -> dict:
        """获取统计"""
        values = self.metrics[metric]
        return {
            "avg": sum(values) / len(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "count": len(values)
        }
```

---

## 8. 测试方案

### 8.1 单元测试

```python
def test_agent_creation():
    """测试Agent创建"""
    config = {
        "model_name": "deepseek-r1:14b",
        "tools": [],
        "system_prompt": "测试"
    }
    
    agent = QuantTradingAgent(config)
    assert agent is not None

def test_model_routing():
    """测试模型路由"""
    router = ModelRouter(local_manager, cloud_manager)
    
    # 测试简单查询路由
    model = router.route("查询状态", "query_status")
    assert model == "deepseek-r1:8b"
    
    # 测试策略配置路由
    model = router.route("配置策略", "configure_strategy")
    assert model == "deepseek-r1:14b"
```

### 8.2 集成测试

```python
def test_end_to_end_conversation():
    """端到端对话测试"""
    agent = QuantTradingAgent(config)
    
    # 测试策略配置
    response = agent.chat("我想创建一个动量因子策略，持仓5天，止损10%")
    assert "策略" in response
    
    # 测试多轮对话
    response = agent.chat("运行回测")
    assert "回测" in response
```

### 8.3 性能测试

```python
def test_response_time():
    """响应时间测试"""
    agent = QuantTradingAgent(config)
    
    times = []
    for i in range(10):
        start = time.time()
        agent.chat("查询系统状态")
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    assert avg_time < 3.0  # 平均响应时间小于3秒
```

---

## 9. 部署配置

### 9.1 配置文件

**文件路径**: `config/layer_11/agent_config.yaml`

```yaml
# Agent配置
agent:
  # 默认模型
  default_model: "deepseek-r1:14b"
  
  # 模型配置
  models:
    local:
      - name: "deepseek-r1:8b"
        use_case: "简单查询"
      - name: "deepseek-r1:14b"
        use_case: "策略配置"
      - name: "qwen2.5-coder:14b"
        use_case: "代码生成"
      - name: "qwen3-coder:30b"
        use_case: "复杂分析"
    
    cloud:
      - name: "gpt-4-turbo"
        use_case: "紧急任务"
        api_key: "${OPENAI_API_KEY}"
  
  # 记忆配置
  memory:
    max_history: 100
    long_term:
      enabled: true
      collection: "quant_memory"
  
  # 安全配置
  security:
    pii_detection: true
    permission_check: true
    audit_log: true
  
  # 性能配置
  performance:
    model_cache_size: 10
    max_concurrent: 4
    timeout: 30
```

---

## 📚 相关文档索引

### 核心蓝图文档

| 文档名称 | 路径 | 说明 |
|---------|------|------|
| [Layer 11架构蓝图](./LAYER_11_ARCHITECTURE.md) | `docs/module_designs/layer_11/LAYER_11_ARCHITECTURE.md` | Layer 11整体架构 |
| [Layer 11工具封装蓝图](./LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md` | 工具封装架构、单一AI层设计 |
| [Layer 11工具接口规范](./LAYER_11_TOOL_INTERFACE_SPECIFICATION.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_INTERFACE_SPECIFICATION.md` | 所有模块工具接口详细定义 |
| [文字驱动核心模块](./L11_TEXT_DRIVER.md) | `docs/module_designs/layer_11/L11_TEXT_DRIVER.md` | NLU设计、意图识别、参数提取 |

---

> **设计完成时间**: 2026-04-02  
> **设计状态**: ✅ 已完成  
> **下一阶段**: 编码实施
