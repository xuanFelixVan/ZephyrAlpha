---
module_id: L11_TEXT_DRIVER_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席文档架构�?
layer: Layer 11
module_type: 核心模块
priority: P0
estimated_hours: 40
standard_type: 设计文档
applicable_scope: 全系�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# L11_TEXT_DRIVER: 文字驱动核心模块设计文档

> **版本**: v1.0  
> **创建日期**: 2026-04-02  
> **所属层�?*: Layer 11 - 文字驱动�? 
> **设计状�?*: �?设计完成  
> **优先�?*: P0 (核心模块)

---

## 📋 目录

- [1. 模块概述](#1-模块概述)
- [2. 功能设计](#2-功能设计)
- [3. 技术架构](#3-技术架�?
- [4. 接口设计](#4-接口设计)
- [5. 数据流设计](#5-数据流设�?
- [6. 配置管理](#6-配置管理)
- [7. 错误处理](#7-错误处理)
- [8. 测试方案](#8-测试方案)
- [9. 部署方案](#9-部署方案)

---

## 1. 模块概述

### 1.1 功能定位

**L11_TEXT_DRIVER**是Layer 11的核心模块，负责将用户的自然语言描述转换为系统操作指令�?

**核心职责**�?
- 🎯 **自然语言理解**：理解用户的文字描述
- 🧠 **意图识别**：识别用户的操作意图
- 📊 **参数提取**：从描述中提取关键参�?
- 🔧 **工具调用**：调用对应的系统工具
- 💬 **结果反馈**：将执行结果转换为自然语言

### 1.2 模块边界

```yaml
输入:
  - 用户文字描述
  - 对话历史
  - 系统状�?

输出:
  - 工具调用指令
  - 执行结果反馈
  - 智能建议

不包�?
  - 模型推理（由Agent模块负责�?
  - 工具实现（由工具模块负责�?
  - UI渲染（由Web界面负责�?
```

### 1.3 依赖关系

```yaml
上游依赖:
  - L11_WEB_UI: 用户输入
  - L11_AGENT: 模型推理

下游依赖:
  - L11_TOOLS: 工具调用
  - Layer 0-9: 系统操作

外部依赖:
  - LangChain 1.0
  - Ollama
  - Open WebUI
```

---

## 2. 功能设计

### 2.1 核心功能

#### 2.1.1 自然语言理解

**功能描述**：理解用户的自然语言描述

**实现方式**�?
```python
class NaturalLanguageUnderstanding:
    """自然语言理解"""
    
    def __init__(self, model_name: str = "deepseek-r1:14b"):
        self.llm = ChatOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            model=model_name,
            temperature=0.1
        )
    
    def understand(self, user_input: str) -> dict:
        """
        理解用户输入
        
        返回:
        {
            "intent": "configure_strategy",  # 意图
            "entities": {  # 实体
                "strategy_type": "momentum",
                "holding_period": 5,
                "stop_loss": 0.1
            },
            "confidence": 0.95  # 置信�?
        }
        """
        prompt = f"""
        分析以下用户输入，提取意图和关键参数�?
        
        用户输入: {user_input}
        
        请返回JSON格式�?
        {{
            "intent": "意图类型",
            "entities": {{}},
            "confidence": 0.0-1.0
        }}
        """
        
        response = self.llm.invoke(prompt)
        return json.loads(response.content)
```

#### 2.1.2 意图识别

**支持的意图类�?*�?

| 意图类型 | 描述 | 示例 |
|----------|------|------|
| **configure_strategy** | 配置策略 | "创建一个动量因子策�? |
| **adjust_risk_control** | 调整风控 | "把最大回撤限制调整到10%" |
| **query_status** | 查询状�?| "告诉我系统当前状�? |
| **run_backtest** | 运行回测 | "对这个策略运�?023年的回测" |
| **export_report** | 导出报告 | "导出本月的交易报�? |
| **get_suggestion** | 获取建议 | "给我一些策略建�? |

**意图识别逻辑**�?
```python
class IntentRecognizer:
    """意图识别�?""
    
    def recognize(self, user_input: str) -> str:
        """识别用户意图"""
        
        # 关键词匹�?
        keywords = {
            "configure_strategy": ["创建", "配置", "设置", "策略"],
            "adjust_risk_control": ["调整", "风控", "回撤", "止损"],
            "query_status": ["查询", "状�?, "表现", "持仓"],
            "run_backtest": ["回测", "测试", "验证"],
            "export_report": ["导出", "报告", "下载"],
            "get_suggestion": ["建议", "推荐", "意见"]
        }
        
        for intent, words in keywords.items():
            if any(word in user_input for word in words):
                return intent
        
        return "unknown"
```

#### 2.1.3 参数提取

**参数提取规则**�?

```python
class ParameterExtractor:
    """参数提取�?""
    
    def extract(self, user_input: str, intent: str) -> dict:
        """提取参数"""
        
        if intent == "configure_strategy":
            return self._extract_strategy_params(user_input)
        elif intent == "adjust_risk_control":
            return self._extract_risk_params(user_input)
        # ... 其他意图
    
    def _extract_strategy_params(self, user_input: str) -> dict:
        """提取策略参数"""
        
        params = {}
        
        # 策略类型
        strategy_types = {
            "动量": "momentum",
            "价�?: "value",
            "质量": "quality",
            "成长": "growth"
        }
        for key, value in strategy_types.items():
            if key in user_input:
                params["strategy_type"] = value
        
        # 持仓周期
        import re
        match = re.search(r"持仓(\d+)�?, user_input)
        if match:
            params["holding_period"] = int(match.group(1))
        
        # 止损比例
        match = re.search(r"止损(\d+)%", user_input)
        if match:
            params["stop_loss"] = int(match.group(1)) / 100
        
        return params
```

### 2.2 辅助功能

#### 2.2.1 对话历史管理

```python
class ConversationManager:
    """对话历史管理"""
    
    def __init__(self):
        self.history = []
        self.max_history = 100
    
    def add_message(self, role: str, content: str):
        """添加消息"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        
        # 限制历史长度
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_context(self, last_n: int = 5) -> str:
        """获取上下�?""
        recent = self.history[-last_n:]
        return "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in recent
        ])
```

#### 2.2.2 智能提示

```python
class SmartPrompter:
    """智能提示"""
    
    def suggest_next_action(self, context: dict) -> str:
        """建议下一步操�?""
        
        if context.get("strategy_configured"):
            return "策略已配置，是否需要运行回测验证？"
        elif context.get("backtest_completed"):
            return "回测完成，是否需要启动模拟交易？"
        else:
            return "您还需要什么帮助？"
```

---

## 3. 技术架�?

### 3.1 架构�?

```
┌─────────────────────────────────────────────────────────�?
�? 用户输入                                                 �?
└─────────────────────────────────────────────────────────�?
                        �?
┌─────────────────────────────────────────────────────────�?
�? NaturalLanguageUnderstanding                           �?
�? ├─ InputPreprocessor (输入预处�?                       �?
�? ├─ IntentRecognizer (意图识别)                          �?
�? └─ ParameterExtractor (参数提取)                        �?
└─────────────────────────────────────────────────────────�?
                        �?
┌─────────────────────────────────────────────────────────�?
�? ConversationManager (对话管理)                          �?
�? ├─ HistoryManager (历史管理)                            �?
�? ├─ ContextBuilder (上下文构�?                          �?
�? └─ MemoryManager (记忆管理)                             �?
└─────────────────────────────────────────────────────────�?
                        �?
┌─────────────────────────────────────────────────────────�?
�? ToolDispatcher (工具调度)                               �?
�? ├─ ToolSelector (工具选择)                              �?
�? ├─ ParameterValidator (参数验证)                        �?
�? └─ ExecutionMonitor (执行监控)                          �?
└─────────────────────────────────────────────────────────�?
                        �?
┌─────────────────────────────────────────────────────────�?
�? ResultFormatter (结果格式�?                            �?
�? ├─ NaturalLanguageGenerator (自然语言生成)              �?
�? ├─ SmartPrompter (智能提示)                             �?
�? └─ FeedbackCollector (反馈收集)                         �?
└─────────────────────────────────────────────────────────�?
```

### 3.2 核心类设�?

```python
class TextDriver:
    """文字驱动核心�?""
    
    def __init__(self, config: dict):
        self.nlu = NaturalLanguageUnderstanding(config["model"])
        self.conversation_manager = ConversationManager()
        self.tool_dispatcher = ToolDispatcher()
        self.result_formatter = ResultFormatter()
    
    def process(self, user_input: str) -> str:
        """处理用户输入"""
        
        # 1. 理解用户输入
        understanding = self.nlu.understand(user_input)
        
        # 2. 更新对话历史
        self.conversation_manager.add_message("user", user_input)
        
        # 3. 调度工具
        tool_result = self.tool_dispatcher.dispatch(
            understanding["intent"],
            understanding["entities"]
        )
        
        # 4. 格式化结�?
        response = self.result_formatter.format(tool_result)
        
        # 5. 更新对话历史
        self.conversation_manager.add_message("assistant", response)
        
        return response
```

---

## 4. 接口设计

### 4.1 对外接口

```python
class ITextDriver(ABC):
    """文字驱动接口"""
    
    @abstractmethod
    def process(self, user_input: str) -> str:
        """处理用户输入"""
        pass
    
    @abstractmethod
    def get_conversation_history(self) -> list:
        """获取对话历史"""
        pass
    
    @abstractmethod
    def reset_conversation(self):
        """重置对话"""
        pass
```

### 4.2 内部接口

```python
class INaturalLanguageUnderstanding(ABC):
    """自然语言理解接口"""
    
    @abstractmethod
    def understand(self, user_input: str) -> dict:
        """理解用户输入"""
        pass

class IToolDispatcher(ABC):
    """工具调度接口"""
    
    @abstractmethod
    def dispatch(self, intent: str, params: dict) -> dict:
        """调度工具"""
        pass
```

---

## 5. 数据流设�?

### 5.1 主数据流

```
用户输入
  �?
[预处理] �?清洗、分词、标准化
  �?
[意图识别] �?识别操作意图
  �?
[参数提取] �?提取关键参数
  �?
[上下文构建] �?结合对话历史
  �?
[工具选择] �?选择合适的工具
  �?
[参数验证] �?验证参数合法�?
  �?
[工具执行] �?执行工具操作
  �?
[结果格式化] �?生成自然语言响应
  �?
用户反馈
```

### 5.2 数据结构

```python
# 用户输入
user_input = "我想创建一个动量因子策略，持仓5天，止损10%"

# 理解结果
understanding = {
    "intent": "configure_strategy",
    "entities": {
        "strategy_type": "momentum",
        "holding_period": 5,
        "stop_loss": 0.1
    },
    "confidence": 0.95
}

# 工具调用
tool_call = {
    "tool": "configure_strategy",
    "params": {
        "strategy_type": "momentum",
        "holding_period": 5,
        "stop_loss": 0.1,
        "max_position": 20
    }
}

# 执行结果
tool_result = {
    "success": True,
    "message": "策略配置成功",
    "data": {
        "strategy_id": "strategy_1",
        "config": {...}
    }
}

# 响应
response = """�?策略配置成功�?

策略ID: strategy_1
策略类型: 动量因子策略
持仓周期: 5�?
止损比例: 10%

预计年化收益: 15-25%
建议风险等级: 中等

是否需要立即启动回测验证？"""
```

---

## 6. 配置管理

### 6.1 配置文件

**文件路径**: `config/layer_11/text_driver_config.yaml`

```yaml
# 文字驱动配置
text_driver:
  # 模型配置
  model:
    default: "deepseek-r1:14b"
    fallback: "qwen2.5-coder:14b"
    
  # 对话配置
  conversation:
    max_history: 100
    context_window: 5
    
  # 意图识别
  intent:
    confidence_threshold: 0.8
    unknown_intent_handler: "ask_clarification"
    
  # 参数提取
  parameter:
    strict_validation: true
    default_values:
      holding_period: 5
      stop_loss: 0.1
      max_position: 20
      
  # 工具调度
  tool:
    timeout: 30
    retry_times: 3
    retry_delay: 1
```

### 6.2 配置加载

```python
import yaml

class ConfigManager:
    """配置管理�?""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def get(self, key: str, default=None):
        """获取配置"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value or default
```

---

## 7. 错误处理

### 7.1 错误类型

```python
class TextDriverError(Exception):
    """文字驱动基础错误"""
    pass

class IntentRecognitionError(TextDriverError):
    """意图识别错误"""
    pass

class ParameterExtractionError(TextDriverError):
    """参数提取错误"""
    pass

class ToolDispatchError(TextDriverError):
    """工具调度错误"""
    pass
```

### 7.2 错误处理策略

```python
class ErrorHandler:
    """错误处理�?""
    
    def handle(self, error: Exception, context: dict) -> str:
        """处理错误"""
        
        if isinstance(error, IntentRecognitionError):
            return "抱歉，我不太理解您的意思，能换种说法吗�?
        
        elif isinstance(error, ParameterExtractionError):
            return f"参数提取失败，请提供更详细的信息�?
        
        elif isinstance(error, ToolDispatchError):
            return f"操作执行失败：{str(error)}"
        
        else:
            return "系统出现错误，请稍后重试�?
```

---

## 8. 测试方案

### 8.1 单元测试

```python
def test_intent_recognition():
    """测试意图识别"""
    recognizer = IntentRecognizer()
    
    # 测试策略配置意图
    intent = recognizer.recognize("我想创建一个动量因子策�?)
    assert intent == "configure_strategy"
    
    # 测试风控调整意图
    intent = recognizer.recognize("把最大回撤限制调整到10%")
    assert intent == "adjust_risk_control"

def test_parameter_extraction():
    """测试参数提取"""
    extractor = ParameterExtractor()
    
    # 测试策略参数提取
    params = extractor.extract(
        "我想创建一个动量因子策略，持仓5天，止损10%",
        "configure_strategy"
    )
    
    assert params["strategy_type"] == "momentum"
    assert params["holding_period"] == 5
    assert params["stop_loss"] == 0.1
```

### 8.2 集成测试

```python
def test_end_to_end():
    """端到端测�?""
    driver = TextDriver(config)
    
    # 测试完整流程
    response = driver.process("我想创建一个动量因子策略，持仓5天，止损10%")
    
    assert "策略配置成功" in response
    assert "动量因子策略" in response
    assert "5�? in response
    assert "10%" in response
```

---

## 9. 部署方案

### 9.1 部署架构

```yaml
部署方式: 本地部署
运行环境: Python 3.9+
依赖服务:
  - Ollama (本地LLM)
  - Open WebUI (Web界面)
  
资源需�?
  CPU: 4�?
  内存: 16GB+
  GPU: 8GB+ (推荐)
  存储: 50GB+
```

### 9.2 启动脚本

```python
# start_text_driver.py
from src.layer_11.text_driver import TextDriver

def main():
    # 加载配置
    config = ConfigManager("config/layer_11/text_driver_config.yaml").config
    
    # 初始化文字驱�?
    driver = TextDriver(config)
    
    # 启动服务
    print("文字驱动模块已启�?)
    
    # 测试
    response = driver.process("查询系统状�?)
    print(response)

if __name__ == "__main__":
    main()
```

---

## 📚 相关文档索引

### 核心蓝图文档

| 文档名称 | 路径 | 说明 |
|---------|------|------|
| [Layer 11架构蓝图](./LAYER_11_ARCHITECTURE.md) | `docs/module_designs/layer_11/LAYER_11_ARCHITECTURE.md` | Layer 11整体架构 |
| [Layer 11工具封装蓝图](./LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md` | 工具封装架构、单一AI层设�?|
| [Layer 11工具接口规范](./LAYER_11_TOOL_INTERFACE_SPECIFICATION.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_INTERFACE_SPECIFICATION.md` | 所有模块工具接口详细定�?|
| [量化交易Agent模块](./L11_QUANT_AGENT.md) | `docs/module_designs/layer_11/L11_QUANT_AGENT.md` | Agent框架、模型管理、工具集�?|

---

> **设计完成时间**: 2026-04-02  
> **设计状�?*: �?已完�? 
> **下一阶段**: 编码实施
