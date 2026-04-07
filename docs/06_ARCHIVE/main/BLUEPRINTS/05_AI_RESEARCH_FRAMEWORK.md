---
module_id: 05_AI_RESEARCH_FRAMEWORK
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - AI辅助研究框架文档
---

﻿---
module_id: ARCHIVE_BP_AI_RESEARCH_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 归档文档、历史版本
standard_type: 专业量化机构蓝图
applicable_scope: 全系统架构设?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---


# AI辅助研究框架
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 务实版AI辅助量化研究实现方案
>
> **版本**: v1.0
> **最后更?*: 2026-03-28
> **设计原则**: 简单直接，拒绝过度工程?
> **索引**: `AI.RESEARCH.001`

---

## 一、设计原?

### 1.1 核心理念

```
?4.0过度设计: LangChain + LangGraph + AutoGen + CrewAI + 多Agent协作
?5.0务实设计: LangChain调用LLM + 简单工具封?
```

### 1.2 为什么拒绝完整Agent框架?

| 因素 | 完整Agent框架 | 简化LLM调用 |
|------|---------------|-------------|
| **学习成本** | 高（每个框架都要学） | 低（只会LangChain?|
| **维护成本** | 高（多个框架升级?| 低（只维护一处） |
| **调试难度** | 高（多Agent交互复杂?| 低（线性调用链?|
| **收益不确?* | 高投入可能无回报 | 快速见?|
| **个人时间** | 5小时/天不够用 | 轻松hold?|

### 1.3 务实决策

```
?? LangChain的prompt模板 + tools封装
?? 基于文档的RAG检?
?? 简单的Chain调用
?不做: 复杂的状态机编排
?不做: 多智能体协作
?不做: 自主决策循环
```

---

## 二、架构设?

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────?
?                     用户交互?                             ?
?             (Streamlit / Jupyter / CLI)                    ?
└─────────────────────────────────────────────────────────────?
                              ?
                              ?
┌─────────────────────────────────────────────────────────────?
?                   LangChain 调用?                         ?
?                                                             ?
?  ┌──────────────?   ┌──────────────?   ┌──────────────??
?  ?Prompt模板   ?   ?Chain调用    ?   ?输出解析     ??
?  └──────────────?   └──────────────?   └──────────────??
└─────────────────────────────────────────────────────────────?
                              ?
                              ?
┌─────────────────────────────────────────────────────────────?
?                   工具封装?(Tools)                         ?
?                                                             ?
?  ┌────────? ┌────────? ┌────────? ┌────────?         ?
?  │数据查询│  │因子计算│  │回测执行│  │报告生成│          ?
?  └────────? └────────? └────────? └────────?         ?
└─────────────────────────────────────────────────────────────?
                              ?
                              ?
┌─────────────────────────────────────────────────────────────?
?                   LLM API?                               ?
?                 (DeepSeek / GPT-4o)                        ?
└─────────────────────────────────────────────────────────────?
```

### 2.2 模块职责

| 模块 | 职责 | 实现 |
|------|------|------|
| **Prompt模板** | 结构化用户问题和上下?| Jinja2模板 |
| **Chain调用** | 串联工具和LLM | LangChain Expression Language |
| **输出解析** | 解析LLM输出为结构化数据 | Pydantic模型 |
| **工具封装** | 封装本地函数为LangChain Tool | @tool装饰?|
| **RAG检?* | 检索相关研究文?| FAISS向量?|

---

## 三、工具封?

### 3.1 工具列表

| 工具名称 | 功能 | 返回格式 |
|----------|------|----------|
| `get_stock_data` | 获取股票数据 | DataFrame |
| `calculate_factor` | 计算因子?| Dict |
| `run_backtest` | 执行回测 | 回测报告 |
| `search_research_docs` | 搜索研究文档 | 文档列表 |
| `get_factor_performance` | 获取因子绩效 | IC/IR报告 |
| `generate_report` | 生成分析报告 | Markdown |

### 3.2 工具实现示例

```python
from langchain.tools import tool
from pydantic import BaseModel, Field
import pandas as pd

class GetStockDataInput(BaseModel):
    symbol: str = Field(description="股票代码，如 000001.XSHE")
    start_date: str = Field(description="开始日期，格式 YYYY-MM-DD")
    end_date: str = Field(description="结束日期，格?YYYY-MM-DD")

@tool("get_stock_data", args_schema=GetStockDataInput)
def get_stock_data(symbol: str, start_date: str, end_date: str) -> dict:
    """
    获取指定股票的历史数据?
    返回包含日期、开盘价、收盘价、成交量等信息?
    """
    # 实现代码
    data = DataHub.get_ohlcv(symbol, start_date, end_date)
    return {
        "symbol": symbol,
        "data": data.to_dict(),
        "count": len(data)
    }

class CalculateFactorInput(BaseModel):
    factor_name: str = Field(description="因子名称")
    symbol: str = Field(description="股票代码")
    date: str = Field(description="日期")

@tool("calculate_factor", args_schema=CalculateFactorInput)
def calculate_factor(factor_name: str, symbol: str, date: str) -> dict:
    """
    计算指定因子在给定日期的值?
    """
    factor_value = FactorCalculator.calculate(factor_name, symbol, date)
    return {
        "factor": factor_name,
        "symbol": symbol,
        "date": date,
        "value": factor_value
    }
```

### 3.3 工具注册

```python
from langchain.chat_models import ChatDeepSeek
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate

# 初始化LLM
llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.7,
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

# 注册工具
tools = [
    get_stock_data,
    calculate_factor,
    run_backtest,
    search_research_docs,
    get_factor_performance,
    generate_report,
]

# 绑定到LLM
llm_with_tools = llm.bind_tools(tools)
```

---

## 四、Prompt模板

### 4.1 系统提示?

```python
SYSTEM_PROMPT = """你是一位专业的量化交易研究员，专注于A股市场?

你的职责是帮助用户：
1. 分析市场数据和交易策?
2. 研究因子的有效性和预测能力
3. 优化策略参数和风险管?
4. 生成专业的研究报?

工作原则?
- 基于数据和逻辑给出建议
- 指出策略的风险点和局限?
- 推荐具体的改进方?
- 避免过度拟合和未来函?

当需要执行计算时，使用提供的工具获取数据和分析结果?
"""

USER_PROMPT_TEMPLATE = """用户问题：{user_question}

上下文信息：
{context}

请基于以上信息回答用户问题。如需执行分析，使用相关工具获取数据?
"""
```

### 4.2 策略分析Prompt

```python
STRATEGY_ANALYSIS_PROMPT = """你是一位量化策略分析师。请分析以下策略?

策略代码?
```python
{strategy_code}
```

历史回测表现?
- 年化收益：{annual_return}%
- 夏普比率：{sharpe_ratio}
- 最大回撤：{max_drawdown}%
- 胜率：{win_rate}%

请分析：
1. 策略的优势和特点
2. 可能存在的风险点
3. 过拟合的可能?
4. 具体的改进建?
"""
```

---

## 五、RAG检?

### 5.1 文档向量?

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import DirectoryLoader

class ResearchDocStore:
    """研究文档向量?""

    def __init__(self, doc_dir: str):
        self.doc_dir = doc_dir
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None

    def build_index(self):
        """构建文档索引"""
        loader = DirectoryLoader(
            self.doc_dir,
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()

        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)

        # 创建向量索引
        self.vectorstore = FAISS.from_documents(
            documents=splits,
            embedding=self.embeddings
        )

    def search(self, query: str, k: int = 5) -> list:
        """检索相关文?""
        if self.vectorstore is None:
            self.build_index()

        results = self.vectorstore.similarity_search(query, k=k)
        return results
```

### 5.2 检索增强调?

```python
def rag_augmented_query(user_question: str) -> str:
    """检索增强的用户问题"""
    doc_store = ResearchDocStore("./docs/02_FACTOR_LIBRARY")
    relevant_docs = doc_store.search(user_question, k=3)

    context = "\n\n".join([
        f"文档 {i+1}: {doc.page_content}"
        for i, doc in enumerate(relevant_docs)
    ])

    return f"""基于以下相关文档回答问题?

{context}

用户问题：{user_question}
"""
```

---

## 六、Chain调用

### 6.1 简单分析Chain

```python
from langchain.schema import HumanMessage
from langchain.prompts import ChatPromptTemplate

def analyze_strategy(user_question: str, strategy_code: str = None):
    """简单的策略分析Chain"""

    # 构建提示?
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT_TEMPLATE)
    ])

    # 创建Chain
    chain = prompt | llm_with_tools

    # 构建上下?
    context = ""
    if strategy_code:
        # 执行回测获取上下?
        backtest_result = run_backtest.invoke({"code": strategy_code})
        context = f"策略代码：\n{strategy_code}\n\n回测结果：\n{backtest_result}"

    # 调用Chain
    response = chain.invoke({
        "user_question": user_question,
        "context": context
    })

    return response
```

### 6.2 带工具调用的Chain

```python
def research_agent(user_question: str):
    """带工具调用的研究Agent"""

    # 构建提示?
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{user_question}"),
        ("assistant", "{agent_scratchpad}")
    ])

    # 创建Agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 运行Agent
    result = agent.invoke({
        "user_question": user_question
    })

    return result
```

---

## 七、使用示?

### 7.1 策略分析

```python
# 用户输入
question = """
帮我分析这个均线交叉策略?
1. 策略逻辑是否合理?
2. 参数是否需要优化？
3. 可能存在哪些风险?
"""

# 调用分析
response = analyze_strategy(question, strategy_code=strategy_code)
print(response.content)
```

### 7.2 因子研究

```python
# 用户输入
question = """
研究MACD因子在A股市场的有效性：
1. 不同周期的IC表现如何?
2. 与哪些因子组合效果更好？
3. 适合哪些市场环境?
"""

# 调用研究
response = research_agent(question)
```

### 7.3 报告生成

```python
# 用户输入
question = """
基于最近的研究，帮我生成一份因子分析周报：
1. 本周因子表现总结
2. 下周研究计划
3. 重点关注的方?
"""

# 生成报告
report = generate_report.invoke({"type": "weekly", "focus": "factors"})
print(report)
```

---

## 八、技术栈

### 8.1 依赖?

```
langchain>=0.1.0
langchain-community>=0.0.10
deepseek>=0.1.0  # ?openai
faiss-cpu>=1.7.0
pydantic>=2.0
```

### 8.2 配置文件

```yaml
# config/ai_research.yaml
llm:
  provider: deepseek  # ?openai
  model: deepseek-chat
  temperature: 0.7
  api_key: ${DEEPSEEK_API_KEY}

vectorstore:
  type: faiss
  persist_dir: ./data/vectorstore

documents:
  research_dir: ./docs/02_FACTOR_LIBRARY
  max_retrieve: 5
```

---

## 九、扩展计?

### 9.1 当前版本（v1.0?

- ?LangChain基础调用
- ?简单工具封?
- ?RAG检?
- ?基础Prompt模板

### 9.2 未来扩展（按需?

| 功能 | 时机 | 说明 |
|------|------|------|
| 多轮对话 | 确有需求后 | 当前单轮足够 |
| 复杂Chain编排 | 确有需求后 | LangGraph过度设计 |
| 多Agent协作 | 确有需求后 | AutoGen暂不需?|
| 模型微调 | 有足够数据后 | 当前API足够 |

### 9.3 TradingAgents 对比与借鉴

> 参? [TradingAgents](https://github.com/TauricResearch/TradingAgents) - Multi-Agents LLM Financial Trading Framework

#### 9.3.1 系统对比

| 维度 | TradingAgents | ZephyrAlpha |
|------|--------------|-------------|
| **定位** | 多Agent LLM交易框架 | 全链路量化系?|
| **核心** | Agent协作决策 | 策略+因子+风控+执行 |
| **目标** | LLM驱动的分析决?| 可执行的量化策略 |
| **数据驱动** | 依赖实时新闻+LLM | ?历史因子+回测 |
| **策略验证** | 无回测验?| ?完整回测体系 |
| **风控精细?* | 基础风控 | ?完整风控模块 |
| **实盘能力** | 仅模?| ?QMT实盘 |
| **个人适配** | 通用框架 | ?专为个人优化 |

#### 9.3.2 TradingAgents Agent架构

```
┌─────────────────────────────────────────────────────────────?
?             TradingAgents Agent团队                          ?
├─────────────────────────────────────────────────────────────?
? Analyst Team:                                             ?
? ├── Fundamentals Analyst (基本?                          ?
? ├── Sentiment Analyst (舆情)                             ?
? ├── News Analyst (新闻)                                  ?
? └── Technical Analyst (技术面)                           ?
?                                                            ?
? Researcher Team:                                          ?
? ├── Bullish Researcher (多头)                            ?
? └── Bearish Researcher (空头)                            ?
?                                                            ?
? Trader Agent                                              ?
? Risk Management + Portfolio Manager                       ?
└─────────────────────────────────────────────────────────────?
```

#### 9.3.3 可借鉴之处

| 可借鉴?| 说明 | 融入位置 |
|---------|------|---------|
| **多Agent辩论机制** | 多角度分析市场，减少偏见 | Layer 8 人机交互 |
| **Structured Debate** | 多空双方辩论决策 | Layer 8 AI报告 |
| **Sentiment Analyst** | 社交媒体舆情分析 | Layer 3 舆情分析 |

#### 9.3.4 借鉴实现思路

```python
# ?Layer 8 (人机交互? 增加多Agent辩论

class TradingDebateAgent:
    """多Agent辩论决策"""

    def __init__(self):
        self.analysts = {
            'bullish': BullishResearcher(),
            'bearish': BearishResearcher(),
        }

    async def debate(self, market_data: dict) -> dict:
        """执行多空辩论"""

        # 1. 并行获取多空观点
        bullish_view = await self.analysts['bullish'].analyze(market_data)
        bearish_view = await self.analysts['bearish'].analyze(market_data)

        # 2. LLM综合辩论结果
        final_decision = llm.invoke(f"""
        多方观点: {bullish_view}
        空方观点: {bearish_view}
        请给出最终投资建议及置信度?
        """)

        return final_decision
```

---

**设计原则**: 保持简单，快速见效，拒绝过度工程?

**维护?*: 清风量化系统
**版本**: v1.0
**最后更?*: 2026-03-28
