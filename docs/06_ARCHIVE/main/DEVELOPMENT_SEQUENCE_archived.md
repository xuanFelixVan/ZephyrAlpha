# 开发顺序文档

> 清风量化系统 v5.0 - 1人+AI模式开发顺序
>
> **版本**: v1.0
> **最后更新**: 2026-03-29
> **时间盒**: 420小时 (14h/天 × 30天)

---

## 1. 现状分析

### 1.1 已有文档

| 文档 | 内容 | 状态 |
|------|------|------|
| API_Contract.md | 6个核心模块接口 | ✅ 稳定 |
| UNIFIED_ARCHITECTURE.md | Layer 0-8统一架构 | ✅ 稳定 |
| AI_RESEARCH_FRAMEWORK.md | AI研究框架 | ✅ 稳定 |
| RESEARCH_PIPELINE.md | Pipeline蓝图 | ✅ 已完成 |
| EXPERIMENT_TRACKING.md | 实验追踪蓝图 | ✅ 已完成 |
| KNOWLEDGE_MANAGEMENT.md | 知识管理蓝图 | ✅ 已完成 |

### 1.2 现有接口差距

```
❌ 缺失接口:
├── API.RT.001 - ResearchTools (AI专用Tool)
├── API.HA.001 - HumanApproval (审批流程)
├── API.RM.001 - ResearchMemory (记忆系统)
└── API.RP.001 - ResearchPipeline (流程编排)
```

---

## 2. 开发顺序原则

### 2.1 依赖关系

```
先开发被依赖的模块，后开发依赖它们的模块：

Layer 0 (数据)  → Layer 2 (因子) → Layer 3 (策略) → Layer 5 (执行)
     ↑                  ↑               ↑
     │                  │               │
  DataHub ←── FactorCalculator ←── StrategyEngine ←── TradeExecutor
     ↑
     │
ResearchTools (需要先封装基础模块)
     ↑
     │
LangChain Agent (需要Tool接口)
```

### 2.2 开发顺序

```
第一优先: 基础设施 (其他模块都依赖)
第二优先: 工具层 (AI Agent依赖)
第三优先: Agent核心 (依赖工具层)
第四优先: Pipeline和集成 (依赖Agent核心)
```

---

## 3. 详细开发顺序

### Phase 1: 基础设施 (无依赖)

#### 1.1 DataHub 增强

| 项目 | 内容 |
|------|------|
| **索引** | API.DH.001 (已存在) |
| **开发时间** | 8h |
| **依赖** | 无 |
| **任务** | 1. 标准化Tool接口 2. 批量获取接口 3. 缓存支持 |

```python
# src/tools/data_tools.py

from langchain.tools import tool
from typing import List, Optional
import pandas as pd

class DataHubTools:
    """DataHub工具封装 - LangChain Tool格式"""

    @tool
    def get_stock_ohlcv(
        symbols: List[str],
        start_date: str,
        end_date: str,
        fields: Optional[List[str]] = None
    ) -> dict:
        """
        获取股票OHLCV数据

        Args:
            symbols: 股票代码列表，如 ["000001.XSHE", "000002.XSHE"]
            start_date: 开始日期，格式 YYYY-MM-DD
            end_date: 结束日期，格式 YYYY-MM-DD
            fields: 要获取的字段，如 ["open", "high", "low", "close", "volume"]

        Returns:
            包含状态和数据的字典
        """
        pass

    @tool
    def get_factor_data(
        factor_name: str,
        symbols: List[str],
        date: str
    ) -> dict:
        """
        获取因子值

        Args:
            factor_name: 因子名称，如 "momentum_20"
            symbols: 股票代码列表
            date: 日期

        Returns:
            包含因子值的字典
        """
        pass

    @tool
    def list_available_factors() -> List[str]:
        """
        列出所有可用的因子

        Returns:
            因子名称列表
        """
        pass
```

#### 1.2 FactorCalculator Tool封装

| 项目 | 内容 |
|------|------|
| **索引** | API.FC.001 (已存在) → API.RT.002 |
| **开发时间** | 8h |
| **依赖** | DataHub增强 |
| **任务** | 1. Tool格式封装 2. 单因子/批量计算 3. IC分析接口 |

```python
# src/tools/factor_tools.py

class FactorTools:
    """因子计算工具封装 - LangChain Tool格式"""

    @tool
    def calculate_single_factor(
        factor_name: str,
        symbol: str,
        date: str,
        params: Optional[dict] = None
    ) -> dict:
        """
        计算单个因子值

        Args:
            factor_name: 因子名称
            symbol: 股票代码
            date: 日期
            params: 因子参数，如 {"period": 20}

        Returns:
            包含因子值的字典
        """
        pass

    @tool
    def calculate_batch_factors(
        factor_names: List[str],
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> dict:
        """
        批量计算因子

        Args:
            factor_names: 因子名称列表
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            包含因子DataFrame的字典
        """
        pass

    @tool
    def analyze_factor_ic(
        factor_name: str,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> dict:
        """
        分析因子IC表现

        Args:
            factor_name: 因子名称
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            包含IC均值、ICIR等指标的字典
        """
        pass
```

---

### Phase 2: 工具层 (依赖Phase 1)

#### 2.1 BacktestTool

| 项目 | 内容 |
|------|------|
| **索引** | API.RT.003 |
| **开发时间** | 10h |
| **依赖** | DataHub增强, FactorCalculator Tool |
| **任务** | 1. Backtrader封装 2. 回测结果解析 3. 绩效指标计算 |

#### 2.2 RiskTool

| 项目 | 内容 |
|------|------|
| **索引** | API.RT.004 |
| **开发时间** | 8h |
| **依赖** | DataHub增强 |
| **任务** | 1. 风控规则检查 2. 风险指标计算 3. 仓位验证 |

#### 2.3 HumanApproval Tool

| 项目 | 内容 |
|------|------|
| **索引** | API.HA.001 |
| **开发时间** | 8h |
| **依赖** | 无 |
| **任务** | 1. 审批请求 2. 审批响应 3. 状态追踪 |

```python
# src/tools/approval_tools.py

class HumanApprovalTools:
    """人机审批工具"""

    @tool
    def request_strategy_approval(
        strategy_summary: str,
        expected_return: float,
        max_drawdown: float,
        sharpe_ratio: float
    ) -> dict:
        """
        请求策略审批

        Args:
            strategy_summary: 策略概要描述
            expected_return: 预期收益率
            max_drawdown: 最大回撤
            sharpe_ratio: 夏普比率

        Returns:
            包含审批ID的字典，稍后查询审批结果
        """
        pass

    @tool
    def get_approval_status(approval_id: str) -> dict:
        """
        查询审批状态

        Args:
            approval_id: 审批ID

        Returns:
            包含审批状态的字典
        """
        pass

    @tool
    def submit_approval_response(
        approval_id: str,
        approved: bool,
        comments: Optional[str] = None
    ) -> dict:
        """
        提交审批响应（人工操作）

        Args:
            approval_id: 审批ID
            approved: 是否批准
            comments: 审批意见

        Returns:
            确认提交成功的字典
        """
        pass
```

---

### Phase 3: 记忆系统 (依赖Phase 1)

#### 3.1 ResearchMemory

| 项目 | 内容 |
|------|------|
| **索引** | API.RM.001 |
| **开发时间** | 15h |
| **依赖** | 无 (独立模块) |
| **任务** | 1. SQLite存储 2. 实验记录 3. 上下文管理 |

```python
# src/memory/research_memory.py

class ResearchMemory:
    """AI研究记忆系统"""

    def __init__(self, db_path: str = "data/agent/memory.db"):
        self.db = sqlite3.connect(db_path)
        self.init_tables()

    def store_experiment(
        self,
        experiment_id: str,
        hypothesis: str,
        parameters: dict,
        metrics: dict,
        status: str
    ):
        """存储实验记录"""
        pass

    def get_context(self, query: str, limit: int = 5) -> List[dict]:
        """检索相关上下文"""
        pass

    def store_knowledge(
        self,
        content: str,
        category: str,
        metadata: dict
    ):
        """存储知识"""
        pass
```

---

### Phase 4: Agent核心 (依赖Phase 1-3)

#### 4.1 LangChain Agent集成

| 项目 | 内容 |
|------|------|
| **索引** | API.LC.001 |
| **开发时间** | 12h |
| **依赖** | 所有Tool |
| **任务** | 1. Agent定义 2. Prompt模板 3. 工具绑定 |

```python
# src/ai/research_agent.py

from langchain.agents import Agent, ConversationalAgent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

class ResearchAgent:
    """AI研究Agent"""

    def __init__(self, tools: List[Tool], memory: ResearchMemory):
        self.tools = tools
        self.memory = memory
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        self.agent = self._build_agent()

    def _build_agent(self) -> Agent:
        """构建Agent"""
        prompt = PromptTemplate.from_template("""
        你是一位专业的量化交易研究员。

        你的任务是帮助用户进行量化因子研究和策略开发。

        可用工具：
        {tools}

        记忆上下文：
        {memory_context}

        当前任务：
        {input}

        请使用工具完成任务，并记录关键发现到记忆中。
        """)

        return ConversationalAgent.from_llm_and_tools(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

    def research(self, objective: str) -> dict:
        """执行研究"""
        result = self.agent.run(objective)
        return {"status": "success", "result": result}
```

---

### Phase 5: Pipeline和集成 (依赖Phase 4)

#### 5.1 ResearchPipeline

| 项目 | 内容 |
|------|------|
| **索引** | API.RP.001 |
| **开发时间** | 20h |
| **依赖** | Agent核心, 记忆系统 |
| **任务** | 1. Pipeline定义 2. 节点实现 3. 错误处理 |

#### 5.2 FastAPI集成

| 项目 | 内容 |
|------|------|
| **索引** | API.API.001 |
| **开发时间** | 10h |
| **依赖** | 所有模块 |
| **任务** | 1. API端点 2. 请求验证 3. 错误处理 |

---

## 4. 时间分配

### 4.1 420小时分配

| Phase | 任务 | 时间 | 累计 |
|-------|------|------|------|
| **Phase 1** | 基础设施 | 16h | 16h |
| | DataHub增强 | 8h | |
| | FactorCalculator Tool | 8h | |
| **Phase 2** | 工具层 | 26h | 42h |
| | BacktestTool | 10h | |
| | RiskTool | 8h | |
| | HumanApproval | 8h | |
| **Phase 3** | 记忆系统 | 15h | 57h |
| | ResearchMemory | 15h | |
| **Phase 4** | Agent核心 | 12h | 69h |
| | LangChain集成 | 12h | |
| **Phase 5** | Pipeline+API | 30h | 99h |
| | ResearchPipeline | 20h | |
| | FastAPI集成 | 10h | |
| **其他** | 测试+文档+Buffer | 21h | 120h |

### 4.2 每周计划

```
Week 1: Phase 1 (16h) + Phase 2部分 (10h) = 26h
├── Day 1-2: DataHub增强
├── Day 3-4: FactorCalculator Tool
└── Day 5-7: BacktestTool

Week 2: Phase 2剩余 (16h) + Phase 3 (15h) = 31h
├── Day 1-2: RiskTool
├── Day 3-4: HumanApproval
└── Day 5-7: ResearchMemory

Week 3: Phase 4 (12h) + Phase 5部分 (20h) = 32h
├── Day 1-2: LangChain Agent集成
├── Day 3-5: ResearchPipeline
└── Day 6-7: FastAPI集成

Week 4: Phase 5剩余 (10h) + 测试+优化 (21h) = 31h
├── Day 1-3: Pipeline完善
├── Day 4-5: 测试
└── Day 6-7: 优化+文档
```

---

## 5. 入口点

### 5.1 API入口

```
FastAPI路由:
/api/v1/research          - 启动研究任务
/api/v1/research/{id}     - 查询研究状态
/api/v1/approve/{id}     - 审批
/api/v1/knowledge/query   - 知识查询
/api/v1/experiments      - 实验记录
```

### 5.2 CLI入口

```bash
# 启动研究
python -m src.cli research --objective "研究MACD因子"

# 查询状态
python -m src.cli status --task-id xxx

# 审批
python -m src.cli approve --task-id xxx --approved true
```

---

## 6. 验收标准

### 6.1 Phase验收

| Phase | 验收条件 |
|-------|----------|
| Phase 1 | Tool可独立调用，返回正确数据 |
| Phase 2 | 所有Tool可组合使用 |
| Phase 3 | 记忆可存储和检索 |
| Phase 4 | Agent可完成简单研究任务 |
| Phase 5 | Pipeline端到端运行 |

### 6.2 最终验收

```
✅ 1. AI可接收研究目标并返回结果
✅ 2. 实验自动记录到记忆系统
✅ 3. 需要审批时暂停并等待
✅ 4. 研究结果可查询
✅ 5. API可调用
```

---

## 7. 索引清单

| 索引 | 模块/接口 | Phase | 状态 |
|------|-----------|-------|------|
| API.DH.001 | DataHub接口 | 1 | ✅ 已有 |
| API.FC.001 | FactorCalculator接口 | 1 | ✅ 已有 |
| API.RT.001 | DataHubTool | 1 | 🔨 开发中 |
| API.RT.002 | FactorTool | 1 | 🔨 开发中 |
| API.RT.003 | BacktestTool | 2 | 🔨 开发中 |
| API.RT.004 | RiskTool | 2 | 🔨 开发中 |
| API.HA.001 | HumanApproval | 2 | 🔨 开发中 |
| API.RM.001 | ResearchMemory | 3 | 🔨 开发中 |
| API.LC.001 | LangChain集成 | 4 | 🔨 开发中 |
| API.RP.001 | ResearchPipeline | 5 | 🔨 开发中 |
| API.API.001 | FastAPI入口 | 5 | 🔨 开发中 |

---

**最后更新**: 2026-03-29
**版本**: v1.0
**维护者**: 清风量化系统
