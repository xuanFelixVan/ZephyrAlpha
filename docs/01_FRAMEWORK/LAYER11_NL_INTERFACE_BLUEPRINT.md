---
module_id: LAYER11_NL_INTERFACE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席架构师
standard_type: 专业机构级架构
applicable_scope: 全系统文字交互层
compliance_level: 专业标准
parent_document: ../ARCHITECTURE.md
implementation_status: 设计阶段
---

# Layer 11 文字驱动层架构蓝图

> 清风量化交易系统 v5.2 - Layer 11文字驱动层完整架构设计
> **索引**: `LAYER11.NL.INTERFACE.001`
> **开发周期**: 200小时（基础设施搭建 + 工具集成）
> **核心定位**: 全系统文字交互层，实现零代码操作量化交易系统
> **技术栈**: Open WebUI + LangChain 1.0 + Ollama + VNPY

---

## 一、架构设计概述

### 1.1 设计目标

**核心目标**：
- ✅ **零代码操作**：用户通过自然语言完成所有操作
- ✅ **生产就绪**：使用成熟开源项目，快速部署
- ✅ **本地优先**：100%本地部署，数据隐私安全
- ✅ **企业级特性**：权限管理、监控、安全、可扩展

**关键指标**：
| 指标 | 目标值 | 说明 |
|------|--------|------|
| 意图识别准确率 | ≥95% | 正确理解用户意图 |
| 工具调用成功率 | ≥90% | 成功调用系统功能 |
| 响应时间 | ≤3秒 | 平均响应时间 |
| 用户满意度 | ≥4.5/5.0 | 用户评分 |
| 部署时间 | ≤2周 | 完成基础设施搭建 |

### 1.2 三层架构设计

```
┌─────────────────────────────────────────────────────────┐
│  Layer 11: 文字驱动层 (Natural Language Interface)      │
│  ├─ Open Agent Platform (无代码Agent构建)               │
│  ├─ LangChain 1.0 (生产级Agent框架)                     │
│  └─ Open WebUI (用户友好的聊天界面)                      │
└─────────────────────────────────────────────────────────┘
                          ↓ 文字指令
┌─────────────────────────────────────────────────────────┐
│  Layer 0-9: ZephyrAlpha量化交易系统                      │
│  ├─ 数据层 (QMT/iFind/Baostock)                         │
│  ├─ 因子层 (Alpha因子挖掘)                               │
│  ├─ 策略层 (策略引擎)                                    │
│  └─ 风控层 (风险管理)                                    │
└─────────────────────────────────────────────────────────┘
                          ↓ API调用
┌─────────────────────────────────────────────────────────┐
│  Layer -1: 量化交易平台层 (Execution Platform)           │
│  ├─ VNPY (VeighNa) - 国内最成熟平台                      │
│  ├─ QuantConnect - 国际化云平台                          │
│  └─ QuantDinger - 本地AI驱动平台                         │
└─────────────────────────────────────────────────────────┘
```

**架构说明**：
- **Layer 11**：文字驱动层，负责自然语言理解和工具调度
- **Layer 0-9**：量化交易核心系统，提供业务功能
- **Layer -1**：执行平台层，负责实际交易执行

### 1.3 核心价值

**对个人开发者的价值**：
1. **零编程门槛**：不需要编程知识即可操作整个系统
2. **效率提升**：自然语言交互比代码操作快10倍
3. **错误减少**：AI辅助验证，减少人为错误
4. **学习曲线平缓**：类似ChatGPT的界面，零学习成本

**对系统的价值**：
1. **统一入口**：所有操作通过统一界面完成
2. **可扩展性**：新功能只需注册工具即可
3. **可维护性**：清晰的分层架构，易于维护
4. **专业性**：使用生产级开源项目，符合专业机构标准

---

## 二、核心技术选型

### 2.1 Web界面层：Open WebUI

**项目信息**：
- **GitHub**: open-webui/open-webui
- **Stars**: 50k+
- **License**: MIT
- **最后更新**: 2026-03（活跃维护）

**推荐理由**：
| 维度 | 评价 | 说明 |
|------|------|------|
| 用户友好 | ⭐⭐⭐⭐⭐ | 类似ChatGPT的界面，零学习成本 |
| 本地部署 | ⭐⭐⭐⭐⭐ | 100%离线，数据隐私安全 |
| 功能丰富 | ⭐⭐⭐⭐⭐ | 支持RAG、工具调用、多模型、语音视频 |
| 成熟稳定 | ⭐⭐⭐⭐⭐ | 生产级质量，活跃社区 |
| 易于集成 | ⭐⭐⭐⭐⭐ | 支持Ollama和OpenAI API |

**核心功能**：

```
界面特性:
  - 响应式设计（PC/手机/平板）
  - PWA支持（手机离线使用）
  - Markdown + LaTeX支持
  - 语音/视频通话
  - 深色/浅色主题

AI能力:
  - 多模型对话（同时使用多个模型）
  - RAG文档检索（上传PDF/Word/TXT）
  - 网络搜索集成
  - 图像生成
  - Python函数调用工具

管理功能:
  - 用户权限管理（RBAC）
  - 多语言支持
  - 模型管理
  - 对话历史
  - 插件系统
```

**部署方式**：

```bash
# Docker一键部署（推荐）
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:11434/v1 \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# 访问地址
http://localhost:3000
```

**配置文件**：

```yaml
# config/open-webui/config.yaml
webui:
  host: "0.0.0.0"
  port: 8080
  
  # 数据存储
  data_dir: "/app/backend/data"
  
  # 模型配置
  models:
    - name: "qwen2.5:14b"
      type: "ollama"
      base_url: "http://host.docker.internal:11434/v1"
    - name: "deepseek-r1:14b"
      type: "ollama"
      base_url: "http://host.docker.internal:11434/v1"
  
  # RAG配置
  rag:
    enabled: true
    embedding_model: "text-embedding-3-small"
    chunk_size: 1000
    chunk_overlap: 200
  
  # 工具调用配置
  tools:
    enabled: true
    timeout: 30
  
  # 安全配置
  security:
    jwt_secret: "${JWT_SECRET}"
    enable_auth: true
    default_user_role: "user"
```

---

### 2.2 Agent框架层：LangChain 1.0 + Open Agent Platform

#### 2.2.1 LangChain 1.0（2025年最新版）

**项目信息**：
- **GitHub**: langchain-ai/langchain
- **Stars**: 90k+
- **License**: MIT
- **最后更新**: 2026-03（活跃维护）

**推荐理由**：
| 维度 | 评价 | 说明 |
|------|------|------|
| 生产级架构 | ⭐⭐⭐⭐⭐ | ReAct循环 + Middleware中间件 |
| 标准化设计 | ⭐⭐⭐⭐⭐ | create_agent()一行代码创建Agent |
| 跨模型兼容 | ⭐⭐⭐⭐⭐ | 支持OpenAI、Claude、国产模型 |
| 企业级特性 | ⭐⭐⭐⭐⭐ | 错误处理、重试、监控、安全 |

**核心特性**：

```python
# LangChain 1.0 标准化Agent创建
from langchain.agents import create_agent
from langchain.tools import Tool

# 定义量化交易工具
tools = [
    Tool(
        name="配置策略",
        func=configure_strategy,
        description="配置交易策略参数"
    ),
    Tool(
        name="调整风控",
        func=adjust_risk_control,
        description="调整风控参数"
    ),
    Tool(
        name="查询状态",
        func=query_system_status,
        description="查询系统运行状态"
    )
]

# 创建Agent（一行代码）
agent = create_agent(
    model="gpt-4",  # 或 "qwen-max", "deepseek-chat"
    tools=tools,
    system_prompt="你是ZephyrAlpha量化交易系统的AI助手..."
)

# 运行Agent
result = agent.invoke("我想创建一个动量因子策略，持仓5天，止损10%")
```

**架构设计**：

```
LangChain 1.0 架构:
├── Core Layer
│   ├── Agent Runtime (ReAct循环)
│   ├── Tool Registry (工具注册中心)
│   └── Memory Manager (对话记忆)
│
├── Middleware Layer
│   ├── Error Handler (错误处理)
│   ├── Retry Logic (重试逻辑)
│   ├── Rate Limiter (限流)
│   └── Logger (日志记录)
│
├── Integration Layer
│   ├── Model Adapters (模型适配器)
│   │   ├── OpenAI Adapter
│   │   ├── Claude Adapter
│   │   ├── Ollama Adapter
│   │   └── Qwen Adapter
│   │
│   ├── Tool Adapters (工具适配器)
│   │   ├── Python Function Tool
│   │   ├── REST API Tool
│   │   └── Database Tool
│   │
│   └── Vector Store Adapters (向量存储适配器)
│       ├── ChromaDB
│       ├── Pinecone
│       └── Weaviate
│
└── Monitoring Layer
    ├── Metrics Collector (指标收集)
    ├── Tracing (链路追踪)
    └── Alerting (告警)
```

#### 2.2.2 Open Agent Platform（2025年5月发布）

**项目信息**：
- **GitHub**: langchain-ai/open-agent-platform
- **License**: MIT
- **发布时间**: 2025-05

**推荐理由**：
| 维度 | 评价 | 说明 |
|------|------|------|
| 无代码构建 | ⭐⭐⭐⭐⭐ | 拖拽式创建Agent |
| 可视化界面 | ⭐⭐⭐⭐⭐ | 图形化配置工具和知识库 |
| 多Agent协作 | ⭐⭐⭐⭐⭐ | Agent Supervisor编排 |
| 企业级安全 | ⭐⭐⭐⭐⭐ | 内置认证和权限控制 |

**核心功能**：

```
可视化Agent构建:
  - 拖拽式工具组合
  - 图形化流程设计
  - 实时预览和测试
  - 一键部署

多Agent协作:
  - Agent Supervisor（协调者）
  - Agent Worker（执行者）
  - 任务分发和结果聚合
  - 错误处理和重试

知识库管理:
  - 文档上传和管理
  - 自动向量化
  - 语义检索
  - 知识图谱

监控和调试:
  - 实时日志查看
  - 执行流程可视化
  - 性能指标监控
  - 错误追踪
```

**配置示例**：

```yaml
# config/open-agent-platform/config.yaml
platform:
  name: "ZephyrAlpha Agent Platform"
  version: "1.0.0"
  
  # Agent配置
  agents:
    - name: "量化交易助手"
      type: "supervisor"
      model: "qwen2.5:14b"
      workers:
        - "策略管理Agent"
        - "因子管理Agent"
        - "风控管理Agent"
    
    - name: "策略管理Agent"
      type: "worker"
      model: "qwen2.5:14b"
      tools:
        - "创建策略"
        - "修改策略"
        - "查询策略"
    
    - name: "因子管理Agent"
      type: "worker"
      model: "qwen2.5:14b"
      tools:
        - "挖掘因子"
        - "验证因子"
        - "查询因子"
    
    - name: "风控管理Agent"
      type: "worker"
      model: "qwen2.5:14b"
      tools:
        - "调整风控"
        - "查询风险"
  
  # 知识库配置
  knowledge_bases:
    - name: "策略文档库"
      type: "rag"
      documents:
        - "docs/03_TRADING_TACTICS/**/*.md"
        - "docs/02_FACTOR_LIBRARY/**/*.md"
      embedding_model: "text-embedding-3-small"
    
    - name: "API文档库"
      type: "rag"
      documents:
        - "docs/API/**/*.md"
        - "docs/01_FRAMEWORK/**/*.md"
      embedding_model: "text-embedding-3-small"
  
  # 安全配置
  security:
    enable_auth: true
    session_timeout: 3600
    max_retries: 3
```

---

### 2.3 本地LLM：Ollama

**项目信息**：
- **官网**: https://ollama.com
- **License**: MIT
- **支持平台**: Windows、macOS、Linux

**推荐理由**：
| 维度 | 评价 | 说明 |
|------|------|------|
| 本地部署 | ⭐⭐⭐⭐⭐ | 100%离线，数据隐私安全 |
| 易于使用 | ⭐⭐⭐⭐⭐ | 一键安装和运行 |
| 模型丰富 | ⭐⭐⭐⭐⭐ | 支持Llama、Qwen、DeepSeek等 |
| 性能优化 | ⭐⭐⭐⭐⭐ | GPU加速，推理速度快 |

**支持的模型**：

| 模型 | 参数量 | 中文能力 | 推理能力 | 推荐场景 |
|------|--------|---------|---------|---------|
| qwen2.5:14b | 14B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 中文对话、策略创建 |
| deepseek-r1:14b | 14B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 复杂推理、策略优化 |
| llama3.1:8b | 8B | ⭐⭐⭐ | ⭐⭐⭐⭐ | 英文对话、快速响应 |
| qwen2.5:32b | 32B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 高质量对话（需要更多资源） |

**部署方式**：

```bash
# Windows安装
# 下载安装包: https://ollama.com/download

# 下载模型
ollama pull qwen2.5:14b      # 中文能力强
ollama pull deepseek-r1:14b  # 推理能力强

# 启动服务
ollama serve

# 测试
ollama run qwen2.5:14b
```

**配置文件**：

```yaml
# config/ollama/config.yaml
ollama:
  host: "0.0.0.0"
  port: 11434
  
  # 模型配置
  models:
    - name: "qwen2.5:14b"
      path: "~/.ollama/models/qwen2.5:14b"
      context_length: 32768
      temperature: 0.7
    
    - name: "deepseek-r1:14b"
      path: "~/.ollama/models/deepseek-r1:14b"
      context_length: 32768
      temperature: 0.7
  
  # GPU配置
  gpu:
    enabled: true
    memory_fraction: 0.8
  
  # 并发配置
  concurrency:
    max_requests: 10
    timeout: 60
```

---

### 2.4 量化平台层：VNPY (VeighNa)

**项目信息**：
- **GitHub**: vnpy/vnpy
- **Stars**: 28.4k
- **License**: MIT
- **最后更新**: 2026-03（活跃维护）

**推荐理由**：
| 维度 | 评价 | 说明 |
|------|------|------|
| 国内最成熟 | ⭐⭐⭐⭐⭐ | 600+机构用户，私募基金首选 |
| 接口丰富 | ⭐⭐⭐⭐⭐ | 支持40+交易接口（CTP、XTP、QMT等） |
| 全流程支持 | ⭐⭐⭐⭐⭐ | 策略开发→回测→实盘 |
| 中文社区 | ⭐⭐⭐⭐⭐ | 活跃的本土化生态 |

**核心模块**：

```
vnpy.gateway: 交易接口（40+种）
vnpy.engine: 交易引擎
  - CtaEngine: CTA策略引擎
  - AlphaEngine: Alpha策略引擎
  - PortfolioStrategyEngine: 组合策略引擎
vnpy.app: 应用层
  - CtaBacktester: 回测模块
  - CtaTrader: 实盘交易
  - RiskManager: 风险管理
vnpy.chart: K线图表
vnpy.trader: 交易核心
```

**集成方式**：

```python
# VNPY作为ZephyrAlpha的执行层
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

# 创建主引擎
event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# 添加QMT网关
from vnpy_qmt import QmtGateway
main_engine.add_gateway(QmtGateway)

# 连接QMT
main_engine.connect({
    "userid": "您的账号",
    "password": "您的密码"
}, "QMT")

# 启动UI
qapp = create_qapp()
main_window = MainWindow(main_engine, event_engine)
main_window.show()
qapp.exec()
```

**配置文件**：

```yaml
# config/vnpy/config.yaml
vnpy:
  # 交易引擎配置
  engine:
    type: "main"
    event_engine: true
  
  # 网关配置
  gateways:
    - name: "QMT"
      type: "vnpy_qmt.QmtGateway"
      enabled: true
      config:
        userid: "${QMT_USERID}"
        password: "${QMT_PASSWORD}"
    
    - name: "CTP"
      type: "vnpy_ctp.CtpGateway"
      enabled: false
      config:
        userid: "${CTP_USERID}"
        password: "${CTP_PASSWORD}"
        brokerid: "9999"
        td_address: "180.168.146.187:10200"
        md_address: "180.168.146.187:10210"
  
  # 策略引擎配置
  strategy_engines:
    - name: "CtaEngine"
      type: "vnpy.app.cta_strategy.CtaEngine"
      enabled: true
    
    - name: "AlphaEngine"
      type: "vnpy.app.alpha_strategy.AlphaEngine"
      enabled: true
  
  # 风控配置
  risk_manager:
    enabled: true
    config:
      max_order_volume: 100
      max_order_price: 100000
      max_notional: 1000000
```

---

## 三、与策略层的整合设计

### 3.1 两层协作架构

```
┌─────────────────────────────────────────────────────────┐
│  Layer 11: 文字驱动层（通用控制层）                      │
│  ├─ Open WebUI (用户界面)                               │
│  ├─ LangChain 1.0 (Agent框架)                           │
│  └─ 统一工具注册中心                                     │
└─────────────────────────────────────────────────────────┘
                        ↓ 文字指令
┌─────────────────────────────────────────────────────────┐
│  策略层专用设计（功能实现层）                            │
│  ├─ 策略创建Agent (NLStrategyCreator)                   │
│  ├─ 策略修改Agent (NLStrategyModifier)                  │
│  ├─ 策略管理Agent (NLStrategyManager)                   │
│  └─ 策略查询Agent (NLStrategyQuery)                     │
└─────────────────────────────────────────────────────────┘
                        ↓ API调用
┌─────────────────────────────────────────────────────────┐
│  策略引擎核心                                            │
│  ├─ StrategyFactory                                     │
│  ├─ StrategyRegistry                                    │
│  └─ StrategyPool                                        │
└─────────────────────────────────────────────────────────┘
```

### 3.2 职责划分

| 层级 | 职责 | 具体功能 |
|------|------|---------|
| **Layer 11** | 通用控制层 | 意图识别、工具调度、对话管理、错误处理 |
| **策略层** | 功能实现层 | 策略创建、修改、管理、查询的具体实现 |
| **策略引擎** | 核心业务层 | 策略加载、执行、监控、风控 |

### 3.3 工具注册机制

```python
# src/strategy/nl_interface.py
from langchain.tools import Tool

class StrategyTools:
    """策略层工具集 - 注册到Layer 11"""
    
    def __init__(self):
        self.creator = NLStrategyCreator()
        self.modifier = NLStrategyModifier()
        self.manager = NLStrategyManager()
        self.query = NLStrategyQuery()
    
    def get_tools(self):
        """返回LangChain工具列表"""
        return [
            Tool(
                name="创建策略",
                func=self.creator.create_strategy_from_nl,
                description="创建量化交易策略，支持均线、动量、均值回归等类型"
            ),
            Tool(
                name="修改策略",
                func=self.modifier.modify_strategy,
                description="修改策略参数或逻辑"
            ),
            Tool(
                name="管理策略",
                func=self.manager.deploy_strategy,
                description="上架/下架/启用/禁用策略"
            ),
            Tool(
                name="查询策略",
                func=self.query.query,
                description="查询策略表现、持仓、风险等"
            )
        ]
```

### 3.4 协作流程示例

**用户输入**：
```
"帮我创建一个均线交叉策略，短期5日，长期20日"
```

**Layer 11处理**：
```python
# 1. Open WebUI接收用户输入
user_input = "帮我创建一个均线交叉策略，短期5日，长期20日"

# 2. LangChain Agent进行意图识别
from langchain.agents import create_agent

agent = create_agent(
    model="qwen2.5:14b",
    tools=strategy_tools.get_tools(),
    system_prompt="你是ZephyrAlpha量化交易系统的AI助手..."
)

# 3. Agent识别意图并调用工具
intent = agent.invoke(user_input)
# intent = {
#     "action": "create_strategy",
#     "strategy_type": "均线交叉",
#     "parameters": {"short_period": 5, "long_period": 20}
# }

# 4. 调用策略层工具
result = agent.invoke(intent)
```

**策略层处理**：
```python
# NLStrategyCreator具体实现
class NLStrategyCreator:
    def create_strategy_from_nl(self, user_input: str):
        # 1. 解析用户意图
        intent = self._parse_user_intent(user_input)
        # {"strategy_type": "均线交叉", "short_period": 5, "long_period": 20}
        
        # 2. 生成策略代码
        strategy_code = self.code_generator.generate(intent)
        
        # 3. 验证策略
        validation = self.validator.validate(strategy_code)
        
        # 4. 返回结果
        return StrategyCreationResult(
            strategy=strategy,
            code=strategy_code,
            description="...",
            need_user_confirmation=True
        )
```

**系统回复**：
```
✅ 策略创建成功！

策略名称：MA_Cross_5_20
策略类型：均线交叉策略
策略参数：
  - 短期均线：5日
  - 长期均线：20日

是否需要：
1. 立即回测这个策略？
2. 修改策略参数？
3. 添加风控规则？
```

---

## 四、完整实施方案

### 4.1 Phase 1：基础设施搭建（Week 1-2）

#### Week 1：部署Web界面和Agent框架

**Day 1-2：部署Open WebUI**

```bash
# 1. 安装Docker（如果没有）
# Windows: 下载Docker Desktop
# https://www.docker.com/products/docker-desktop

# 2. 启动Open WebUI
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:11434/v1 \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# 3. 访问界面
# http://localhost:3000
```

**验证标准**：
- ✅ Open WebUI成功启动
- ✅ 可以访问 http://localhost:3000
- ✅ 界面正常显示

**Day 3-4：部署Ollama（本地LLM）**

```bash
# 1. 安装Ollama
# Windows: 下载安装包
# https://ollama.com/download

# 2. 下载模型（推荐Qwen2.5或DeepSeek）
ollama pull qwen2.5:14b      # 中文能力强
ollama pull deepseek-r1:14b  # 推理能力强

# 3. 启动Ollama服务
ollama serve

# 4. 测试
ollama run qwen2.5:14b
```

**验证标准**：
- ✅ Ollama成功启动
- ✅ 模型下载完成
- ✅ 可以进行对话测试

**Day 5-7：集成LangChain**

```bash
# 1. 安装依赖
pip install langchain langchain-openai langchain-community

# 2. 创建Agent配置文件
# config/agent_config.py
```

```python
# config/agent_config.py
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, Tool

# 配置本地LLM
llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Ollama不需要真实API key
    model="qwen2.5:14b"
)

# 定义量化交易工具
tools = [
    Tool(
        name="配置策略",
        func=lambda x: "策略配置功能待实现",
        description="配置交易策略参数，包括因子选择、持仓周期、止损等"
    ),
    Tool(
        name="查询状态",
        func=lambda x: "系统状态查询功能待实现",
        description="查询系统运行状态和交易表现"
    )
]

# 创建Agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
    你是ZephyrAlpha量化交易系统的AI助手。
    
    你可以帮助用户：
    1. 创建交易策略
    2. 修改策略参数
    3. 管理策略（上架/下架）
    4. 查询策略表现
    
    请根据用户需求调用相应工具。
    """
)
```

**验证标准**：
- ✅ LangChain成功安装
- ✅ Agent创建成功
- ✅ 可以进行基础对话

---

#### Week 2：实现策略层工具集成

**Day 1-3：实现策略层工具**

```python
# src/strategy/nl_interface.py
from langchain.tools import Tool
from typing import Dict, Any

class NLStrategyCreator:
    """自然语言策略创建器"""
    
    def __init__(self):
        self.llm_client = LLMClient(model="qwen2.5:14b")
        self.code_generator = FinRobotCodeGenerator()
        self.validator = StrategyValidator()
    
    def create_strategy_from_nl(self, user_input: str) -> Dict[str, Any]:
        """从自然语言创建策略"""
        
        # 1. 理解用户意图
        intent = self._parse_user_intent(user_input)
        
        # 2. 生成策略代码
        strategy_code = self.code_generator.generate(
            strategy_type=intent["strategy_type"],
            parameters=intent["parameters"],
            entry_rule=intent["entry_rule"],
            exit_rule=intent["exit_rule"]
        )
        
        # 3. 验证策略代码
        validation_result = self.validator.validate(strategy_code)
        
        if not validation_result.is_valid:
            # 自动修复问题
            strategy_code = self._auto_fix(strategy_code, validation_result.errors)
        
        # 4. 创建策略实例
        strategy = self._create_strategy_instance(strategy_code, intent)
        
        # 5. 生成策略说明
        strategy_description = self._generate_description(strategy)
        
        return {
            "success": True,
            "strategy": strategy,
            "code": strategy_code,
            "description": strategy_description,
            "need_user_confirmation": True
        }
    
    def _parse_user_intent(self, user_input: str) -> Dict[str, Any]:
        """解析用户意图"""
        prompt = f"""
        分析以下用户输入，提取策略创建意图：
        
        用户输入：{user_input}
        
        请返回JSON格式：
        {{
            "strategy_type": "策略类型",
            "parameters": {{参数}},
            "entry_rule": "入场规则",
            "exit_rule": "出场规则"
        }}
        """
        
        response = self.llm_client.chat(prompt)
        return json.loads(response)

class NLStrategyModifier:
    """自然语言策略修改器"""
    
    def __init__(self):
        self.llm_client = LLMClient(model="qwen2.5:14b")
        self.strategy_registry = StrategyRegistry()
    
    def modify_strategy(self, user_input: str) -> Dict[str, Any]:
        """修改策略"""
        
        # 1. 识别目标策略
        strategy_id = self._identify_strategy(user_input)
        
        # 2. 解析修改意图
        modification = self._parse_modification(user_input)
        
        # 3. 应用修改
        strategy = self.strategy_registry.get(strategy_id)
        modified_strategy = self._apply_modification(strategy, modification)
        
        # 4. 验证修改
        validation = self._validate_modification(modified_strategy)
        
        return {
            "success": True,
            "strategy": modified_strategy,
            "modification": modification,
            "need_user_confirmation": True
        }

class NLStrategyManager:
    """自然语言策略管理器"""
    
    def __init__(self):
        self.llm_client = LLMClient(model="qwen2.5:14b")
        self.deployment_manager = DeploymentManager()
    
    def deploy_strategy(self, user_input: str) -> Dict[str, Any]:
        """部署策略"""
        
        # 1. 识别操作类型
        action = self._identify_action(user_input)
        
        # 2. 识别目标策略
        strategy_id = self._identify_strategy(user_input)
        
        # 3. 执行操作
        if action == "deploy":
            result = self.deployment_manager.deploy(strategy_id)
        elif action == "undeploy":
            result = self.deployment_manager.undeploy(strategy_id)
        elif action == "enable":
            result = self.deployment_manager.enable(strategy_id)
        elif action == "disable":
            result = self.deployment_manager.disable(strategy_id)
        
        return {
            "success": True,
            "action": action,
            "strategy_id": strategy_id,
            "result": result
        }

class NLStrategyQuery:
    """自然语言策略查询器"""
    
    def __init__(self):
        self.llm_client = LLMClient(model="qwen2.5:14b")
        self.performance_analyzer = PerformanceAnalyzer()
    
    def query(self, user_input: str) -> Dict[str, Any]:
        """查询策略"""
        
        # 1. 识别查询类型
        query_type = self._identify_query_type(user_input)
        
        # 2. 识别目标策略
        strategy_id = self._identify_strategy(user_input)
        
        # 3. 执行查询
        if query_type == "performance":
            result = self.performance_analyzer.analyze(strategy_id)
        elif query_type == "risk":
            result = self.performance_analyzer.analyze_risk(strategy_id)
        elif query_type == "position":
            result = self.performance_analyzer.get_positions(strategy_id)
        
        return {
            "success": True,
            "query_type": query_type,
            "strategy_id": strategy_id,
            "result": result
        }
```

**Day 4-5：注册工具到Layer 11**

```python
# src/layer11/tool_registry.py
from langchain.tools import Tool
from src.strategy.nl_interface import StrategyTools

class ToolRegistry:
    """Layer 11工具注册中心"""
    
    def __init__(self):
        self.tools = []
    
    def register_strategy_tools(self):
        """注册策略层工具"""
        strategy_tools = StrategyTools()
        self.tools.extend(strategy_tools.get_tools())
    
    def register_factor_tools(self):
        """注册因子层工具"""
        # TODO: 实现因子层工具
        pass
    
    def register_risk_tools(self):
        """注册风控层工具"""
        # TODO: 实现风控层工具
        pass
    
    def get_all_tools(self):
        """获取所有工具"""
        return self.tools

# 注册工具
registry = ToolRegistry()
registry.register_strategy_tools()
tools = registry.get_all_tools()
```

**Day 6-7：集成测试**

```python
# tests/test_layer11_integration.py
import pytest
from src.layer11.tool_registry import ToolRegistry
from langchain.agents import create_agent

def test_strategy_creation():
    """测试策略创建"""
    registry = ToolRegistry()
    registry.register_strategy_tools()
    tools = registry.get_all_tools()
    
    agent = create_agent(
        model="qwen2.5:14b",
        tools=tools,
        system_prompt="你是ZephyrAlpha量化交易系统的AI助手..."
    )
    
    result = agent.invoke("帮我创建一个均线交叉策略，短期5日，长期20日")
    
    assert result["success"] == True
    assert "strategy" in result
    assert result["need_user_confirmation"] == True

def test_strategy_modification():
    """测试策略修改"""
    # TODO: 实现测试
    pass

def test_strategy_management():
    """测试策略管理"""
    # TODO: 实现测试
    pass

def test_strategy_query():
    """测试策略查询"""
    # TODO: 实现测试
    pass
```

**验证标准**：
- ✅ 策略创建工具成功注册
- ✅ 策略修改工具成功注册
- ✅ 策略管理工具成功注册
- ✅ 策略查询工具成功注册
- ✅ 集成测试通过

---

### 4.2 Phase 2：扩展功能模块（Week 3-4）

#### Week 3：因子层和风控层工具

**Day 1-3：因子层工具**

```python
# src/factor/nl_interface.py
from langchain.tools import Tool

class FactorTools:
    """因子层工具集"""
    
    def __init__(self):
        self.discoverer = FactorDiscoverer()
        self.validator = FactorValidator()
    
    def get_tools(self):
        """返回LangChain工具列表"""
        return [
            Tool(
                name="挖掘因子",
                func=self.discover_factor,
                description="挖掘新的Alpha因子"
            ),
            Tool(
                name="验证因子",
                func=self.validate_factor,
                description="验证因子有效性"
            ),
            Tool(
                name="查询因子",
                func=self.query_factor,
                description="查询因子表现和IC值"
            )
        ]
    
    def discover_factor(self, user_input: str):
        """挖掘因子"""
        # TODO: 实现因子挖掘
        pass
    
    def validate_factor(self, user_input: str):
        """验证因子"""
        # TODO: 实现因子验证
        pass
    
    def query_factor(self, user_input: str):
        """查询因子"""
        # TODO: 实现因子查询
        pass
```

**Day 4-5：风控层工具**

```python
# src/risk/nl_interface.py
from langchain.tools import Tool

class RiskTools:
    """风控层工具集"""
    
    def __init__(self):
        self.risk_manager = RiskManager()
    
    def get_tools(self):
        """返回LangChain工具列表"""
        return [
            Tool(
                name="调整风控",
                func=self.adjust_risk,
                description="调整风控参数"
            ),
            Tool(
                name="查询风险",
                func=self.query_risk,
                description="查询系统风险状态"
            )
        ]
    
    def adjust_risk(self, user_input: str):
        """调整风控"""
        # TODO: 实现风控调整
        pass
    
    def query_risk(self, user_input: str):
        """查询风险"""
        # TODO: 实现风险查询
        pass
```

**Day 6-7：集成测试**

```python
# tests/test_layer11_full_integration.py
def test_full_integration():
    """测试完整集成"""
    registry = ToolRegistry()
    registry.register_strategy_tools()
    registry.register_factor_tools()
    registry.register_risk_tools()
    
    tools = registry.get_all_tools()
    
    agent = create_agent(
        model="qwen2.5:14b",
        tools=tools,
        system_prompt="你是ZephyrAlpha量化交易系统的AI助手..."
    )
    
    # 测试策略创建
    result = agent.invoke("创建一个动量策略")
    assert result["success"] == True
    
    # 测试因子挖掘
    result = agent.invoke("挖掘一个动量因子")
    assert result["success"] == True
    
    # 测试风控调整
    result = agent.invoke("调整止损为10%")
    assert result["success"] == True
```

**验证标准**：
- ✅ 因子层工具成功注册
- ✅ 风控层工具成功注册
- ✅ 完整集成测试通过

---

#### Week 4：VNPY集成和优化

**Day 1-3：VNPY集成**

```python
# src/execution/vnpy_integration.py
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_qmt import QmtGateway

class VNPYExecutor:
    """VNPY执行器"""
    
    def __init__(self):
        self.event_engine = EventEngine()
        self.main_engine = MainEngine(self.event_engine)
        self.main_engine.add_gateway(QmtGateway)
    
    def connect_qmt(self, userid: str, password: str):
        """连接QMT"""
        self.main_engine.connect({
            "userid": userid,
            "password": password
        }, "QMT")
    
    def deploy_strategy(self, strategy):
        """部署策略到VNPY"""
        # TODO: 实现策略部署
        pass
    
    def start_strategy(self, strategy_id: str):
        """启动策略"""
        # TODO: 实现策略启动
        pass
    
    def stop_strategy(self, strategy_id: str):
        """停止策略"""
        # TODO: 实现策略停止
        pass
```

**Day 4-5：性能优化**

```python
# src/layer11/performance_optimizer.py
class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.async_executor = AsyncExecutor()
    
    def optimize_tool_execution(self, tool_func):
        """优化工具执行"""
        # 1. 添加缓存
        @self.cache.cached(ttl=300)
        def cached_func(*args, **kwargs):
            return tool_func(*args, **kwargs)
        
        # 2. 添加异步执行
        async def async_func(*args, **kwargs):
            return await self.async_executor.run(cached_func, *args, **kwargs)
        
        return async_func
```

**Day 6-7：监控和日志**

```python
# src/layer11/monitor.py
import logging
from prometheus_client import Counter, Histogram

class Layer11Monitor:
    """Layer 11监控"""
    
    def __init__(self):
        self.logger = logging.getLogger("layer11")
        
        # Prometheus指标
        self.request_counter = Counter(
            'layer11_requests_total',
            'Total requests'
        )
        self.latency_histogram = Histogram(
            'layer11_request_latency_seconds',
            'Request latency'
        )
    
    def log_request(self, user_input: str, result: dict):
        """记录请求"""
        self.request_counter.inc()
        self.logger.info(f"Request: {user_input}, Result: {result}")
    
    def log_error(self, error: Exception):
        """记录错误"""
        self.logger.error(f"Error: {error}")
```

**验证标准**：
- ✅ VNPY成功集成
- ✅ 性能优化完成
- ✅ 监控和日志正常

---

### 4.3 Phase 3：生产部署（Week 5-6）

#### Week 5：Docker化和部署

**Day 1-3：Docker化**

```dockerfile
# docker/Dockerfile.layer11
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src/ ./src/
COPY config/ ./config/

# 启动服务
CMD ["python", "src/layer11/main.py"]
```

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OPENAI_API_BASE_URL=http://ollama:11434/v1
    volumes:
      - open-webui-data:/app/backend/data
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
  
  zephyr-alpha:
    build:
      context: ..
      dockerfile: docker/Dockerfile.layer11
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama

volumes:
  open-webui-data:
  ollama-data:
```

**Day 4-5：部署脚本**

```bash
# scripts/deploy_layer11.sh
#!/bin/bash

echo "部署Layer 11文字驱动层..."

# 1. 构建镜像
docker-compose -f docker/docker-compose.yml build

# 2. 启动服务
docker-compose -f docker/docker-compose.yml up -d

# 3. 等待服务启动
sleep 10

# 4. 检查服务状态
curl -f http://localhost:3000 || exit 1
curl -f http://localhost:11434 || exit 1

echo "部署完成！"
echo "Open WebUI: http://localhost:3000"
echo "Ollama API: http://localhost:11434"
```

**Day 6-7：生产测试**

```python
# tests/test_production.py
def test_production_deployment():
    """测试生产部署"""
    import requests
    
    # 测试Open WebUI
    response = requests.get("http://localhost:3000")
    assert response.status_code == 200
    
    # 测试Ollama
    response = requests.get("http://localhost:11434")
    assert response.status_code == 200
    
    # 测试对话
    response = requests.post(
        "http://localhost:3000/api/chat",
        json={"message": "创建一个均线策略"}
    )
    assert response.status_code == 200
```

**验证标准**：
- ✅ Docker镜像构建成功
- ✅ 服务启动成功
- ✅ 生产测试通过

---

#### Week 6：文档和培训

**Day 1-3：用户文档**

```markdown
# Layer 11 文字驱动层用户手册

## 快速开始

### 1. 访问系统
打开浏览器访问：http://localhost:3000

### 2. 创建策略
输入："帮我创建一个均线交叉策略，短期5日，长期20日"

### 3. 修改策略
输入："把均线策略的短期均线改成10日"

### 4. 部署策略
输入："把均线策略上架到模拟盘"

### 5. 查询策略
输入："均线策略最近表现怎么样？"

## 常用指令

### 策略管理
- "创建一个[策略类型]策略"
- "修改[策略名称]的参数"
- "上架/下架[策略名称]"
- "启用/禁用[策略名称]"

### 因子管理
- "挖掘一个[因子类型]因子"
- "验证[因子名称]的有效性"
- "查询[因子名称]的IC值"

### 风控管理
- "调整止损为[X]%"
- "查询系统风险状态"
- "设置最大持仓为[X]只"
```

**Day 4-5：API文档**

```python
# docs/api/layer11_api.md
# Layer 11 API文档

## 1. 对话接口

### POST /api/chat
发送对话消息

**请求**：
```json
{
  "message": "创建一个均线策略",
  "context": {}
}
```

**响应**：
```json
{
  "success": true,
  "message": "策略创建成功！",
  "data": {
    "strategy_id": "MA_Cross_5_20",
    "strategy_name": "均线交叉策略"
  }
}
```

## 2. 工具接口

### GET /api/tools
获取所有可用工具

**响应**：
```json
{
  "tools": [
    {
      "name": "创建策略",
      "description": "创建量化交易策略"
    },
    {
      "name": "修改策略",
      "description": "修改策略参数或逻辑"
    }
  ]
}
```
```

**Day 6-7：培训材料**

```markdown
# Layer 11 培训材料

## 一、系统概述

Layer 11是清风量化交易系统的文字驱动层，提供自然语言交互界面。

## 二、核心功能

1. 策略管理：创建、修改、部署、查询策略
2. 因子管理：挖掘、验证、查询因子
3. 风控管理：调整风控参数、查询风险状态

## 三、使用示例

### 示例1：创建策略
用户："帮我创建一个动量策略，持仓5天，止损10%"
系统："✅ 策略创建成功！策略名称：Momentum_5D_SL10"

### 示例2：修改策略
用户："把动量策略的持仓周期改成10天"
系统："✅ 策略修改成功！持仓周期：5天 → 10天"

### 示例3：部署策略
用户："把动量策略上架到模拟盘"
系统："✅ 策略上架成功！账户ID：SIM_Momentum_10D_SL10_20260402"
```

**验证标准**：
- ✅ 用户文档完成
- ✅ API文档完成
- ✅ 培训材料完成

---

## 五、成功指标

### 5.1 技术指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| 意图识别准确率 | ≥95% | 测试集评估 |
| 工具调用成功率 | ≥90% | 日志统计 |
| 响应时间 | ≤3秒 | 性能监控 |
| 系统可用性 | ≥99.5% | 运行监控 |
| 并发用户数 | ≥10 | 压力测试 |

### 5.2 用户体验指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| 用户满意度 | ≥4.5/5.0 | 用户调研 |
| 学习曲线 | ≤1小时 | 用户测试 |
| 任务完成率 | ≥85% | 用户测试 |
| 错误恢复率 | ≥90% | 日志统计 |

### 5.3 业务指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| 策略创建效率 | 提升10倍 | 时间对比 |
| 操作错误率 | 降低80% | 错误统计 |
| 用户活跃度 | ≥80% | 使用统计 |

---

## 六、风险评估与缓解措施

### 6.1 技术风险

| 风险 | 等级 | 影响 | 缓解措施 |
|------|------|------|---------|
| LLM响应慢 | P1 | 用户体验差 | 使用本地模型、添加缓存、异步处理 |
| 意图识别错误 | P1 | 功能调用失败 | 多轮确认、错误恢复机制 |
| 工具调用失败 | P1 | 功能不可用 | 重试机制、降级方案 |
| Docker部署问题 | P2 | 部署困难 | 详细文档、自动化脚本 |

### 6.2 业务风险

| 风险 | 等级 | 影响 | 缓解措施 |
|------|------|------|---------|
| 用户不接受 | P1 | 使用率低 | 用户培训、持续优化 |
| 功能不完整 | P2 | 用户不满 | 渐进式交付、用户反馈 |
| 性能不达标 | P2 | 用户体验差 | 性能优化、资源扩容 |

### 6.3 安全风险

| 风险 | 等级 | 影响 | 缓解措施 |
|------|------|------|---------|
| 数据泄露 | P0 | 严重后果 | 本地部署、数据加密 |
| 未授权访问 | P1 | 安全风险 | 权限管理、认证机制 |
| 恶意输入 | P2 | 系统异常 | 输入验证、异常处理 |

---

## 七、文档治理

### 7.1 文档索引

**本文档在系统中的位置**：
- **父文档**：[ARCHITECTURE.md](./ARCHITECTURE.md)
- **关联文档**：
  - [AI_STRATEGY_AUTOMATION_BLUEPRINT.md](./AI_STRATEGY_AUTOMATION_BLUEPRINT.md) - AI策略自动化
  - [PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md](./PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) - 专业实施蓝图
  - [STRATEGY_ENGINE_CORE_BLUEPRINT.md](../03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/STRATEGY_ENGINE_CORE_BLUEPRINT.md) - 策略引擎核心

### 7.2 版本管理

**版本历史**：
| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | 2026-04-02 | 初始版本，完整架构设计 | 首席架构师 |

### 7.3 维护责任

**文档维护**：
- **负责人**：首席架构师
- **审核人**：技术委员会
- **更新频率**：每季度或重大变更时

---

## 八、立即行动建议

### 8.1 本周任务清单

**Day 1-2**：
- [ ] 安装Docker Desktop
- [ ] 部署Open WebUI
- [ ] 测试访问 http://localhost:3000

**Day 3-4**：
- [ ] 安装Ollama
- [ ] 下载qwen2.5:14b模型
- [ ] 测试对话功能

**Day 5-7**：
- [ ] 安装LangChain
- [ ] 创建基础Agent
- [ ] 测试工具调用

### 8.2 下周任务清单

**Day 1-3**：
- [ ] 实现策略层工具
- [ ] 注册工具到Layer 11
- [ ] 集成测试

**Day 4-5**：
- [ ] 实现因子层工具
- [ ] 实现风控层工具
- [ ] 完整集成测试

**Day 6-7**：
- [ ] VNPY集成
- [ ] 性能优化
- [ ] 监控和日志

### 8.3 关键里程碑

| 里程碑 | 时间 | 验收标准 |
|--------|------|---------|
| 基础设施搭建完成 | Week 2 | Open WebUI + Ollama + LangChain正常运行 |
| 策略层工具集成完成 | Week 4 | 策略创建/修改/管理/查询功能正常 |
| 生产部署完成 | Week 6 | Docker部署成功，生产测试通过 |

---

## 九、相关文档索引

| 文档 | 说明 | 相关性 |
|------|------|--------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 系统架构设计 | ⭐⭐⭐⭐⭐ |
| [AI_STRATEGY_AUTOMATION_BLUEPRINT.md](./AI_STRATEGY_AUTOMATION_BLUEPRINT.md) | AI策略自动化 | ⭐⭐⭐⭐⭐ |
| [PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md](./PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) | 专业实施蓝图 | ⭐⭐⭐⭐⭐ |
| [STRATEGY_ENGINE_CORE_BLUEPRINT.md](../03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/STRATEGY_ENGINE_CORE_BLUEPRINT.md) | 策略引擎核心 | ⭐⭐⭐⭐ |
| [PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md](./PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) | 多时间框架架构 | ⭐⭐⭐⭐ |

---

**文档结束**

> 本蓝图由首席架构师设计，遵循专业量化机构标准，确保系统架构的完整性、一致性和可扩展性。
