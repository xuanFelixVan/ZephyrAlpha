---
module_id: DOC_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席文档架构�?standard_type: 专业量化机构文档
applicable_scope: 全系�?compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计完成
---

# Layer 11: 文字驱动层架构蓝�?
> **版本**: v1.0  
> **创建日期**: 2026-04-02  
> **所属层�?*: Layer 11 - 文字驱动�? 
> **设计状�?*: �?设计完成  
> **优先�?*: P0 (核心需�?  
> **预计工时**: 80小时

---

## 📋 目录

- [1. 概述](#1-概述)
- [2. 架构设计](#2-架构设计)
- [3. 技术选型](#3-技术选型)
- [4. 核心模块](#4-核心模块)
- [5. 实施方案](#5-实施方案)
- [6. 硬件配置](#6-硬件配置)
- [7. 成本评估](#7-成本评估)
- [8. 部署指南](#8-部署指南)
- [9. 测试方案](#9-测试方案)
- [10. 监控运维](#10-监控运维)
- [11. 演进规划](#11-演进规划)
- [12. 风险评估](#12-风险评估)

---

## 1. 概述

### 1.1 功能定位

**Layer 11: 文字驱动�?*是ZephyrAlpha量化交易系统�?*用户交互核心�?*，负责将用户的自然语言描述转换为系统操作指令，实现"零代�?量化交易系统操作�?
**核心价�?*�?- 🎯 **零门槛操�?*：用户无需编程知识，通过文字描述即可操作整个系统
- 🧠 **智能理解**：基于大语言模型（LLM）理解用户意图和上下�?- 🔒 **数据隐私**：本地部署优先，策略参数和交易数�?00%保密
- �?**实时响应**：本地GPU加速，响应速度媲美云端API
- 💰 **零成本运�?*：本地模型免费，无API调用费用

### 1.2 业务场景

| 场景 | 用户描述 | 系统执行 |
|------|----------|----------|
| **策略配置** | "我想创建一个动量因子策略，持仓5天，止损10%" | 自动配置策略参数 |
| **风控调整** | "最近市场波动大，把最大回撤限制从15%调整�?0%" | 更新风控参数 |
| **状态查�?* | "告诉我当前系统的运行状况和最近的交易表现" | 生成系统状态报�?|
| **回测分析** | "对这个策略运�?023年的回测" | 执行回测并分析结�?|
| **智能建议** | "根据当前市场情况，给我一些策略建�? | AI分析并给出建�?|

### 1.3 设计原则

| 原则 | 说明 | 检查标�?|
|------|------|----------|
| **本地优先** | 优先使用本地模型，保护数据隐�?| 90%操作使用本地模型 |
| **智能路由** | 根据任务复杂度自动选择模型 | 简单任务用小模型，复杂任务用大模型 |
| **混合架构** | 本地+云端双备份，保证可用�?| 本地故障时自动切换云�?|
| **渐进增强** | 从基础功能逐步扩展到智能增�?| Phase 1-3分阶段实�?|
| **用户友好** | 界面简洁，零学习成�?| 新用�?分钟上手 |

### 1.4 系统架构�?
```
┌─────────────────────────────────────────────────────────�?�? 用户文字描述                                             �?�? "我想创建一个动量因子策略，持仓5天，止损10%"            �?└─────────────────────────────────────────────────────────�?                        �?┌─────────────────────────────────────────────────────────�?�? Layer 11: 文字驱动�?                                    �?�? ┌─────────────────────────────────────────────────�?  �?�? �? 11.1 Web界面�?(Open WebUI)                     �?  �?�? �? - 用户友好的聊天界�?                           �?  �?�? �? - 支持文字/语音/文件输入                        �?  �?�? �? - 对话历史管理                                  �?  �?�? └─────────────────────────────────────────────────�?  �?�?                       �?                               �?�? ┌─────────────────────────────────────────────────�?  �?�? �? 11.2 Agent框架�?(LangChain 1.0)                �?  �?�? �? - 自然语言理解                                  �?  �?�? �? - 意图识别                                      �?  �?�? �? - 参数提取                                      �?  �?�? �? - 工具调用                                      �?  �?�? └─────────────────────────────────────────────────�?  �?�?                       �?                               �?�? ┌─────────────────────────────────────────────────�?  �?�? �? 11.3 智能路由�?(Model Router)                  �?  �?�? �? - 简单查�?�?deepseek-r1:8b                    �?  �?�? �? - 策略配置 �?deepseek-r1:14b                   �?  �?�? �? - 代码生成 �?qwen2.5-coder:14b                 �?  �?�? �? - 复杂分析 �?qwen3-coder:30b                   �?  �?�? �? - 紧急任�?�?GPT-4/Claude (云端)               �?  �?�? └─────────────────────────────────────────────────�?  �?�?                       �?                               �?�? ┌─────────────────────────────────────────────────�?  �?�? �? 11.4 工具�?(Quant Tools)                       �?  �?�? �? - 配置策略                                      �?  �?�? �? - 调整风控                                      �?  �?�? �? - 查询状�?                                     �?  �?�? �? - 运行回测                                      �?  �?�? �? - 导出报告                                      �?  �?�? └─────────────────────────────────────────────────�?  �?└─────────────────────────────────────────────────────────�?                        �?┌─────────────────────────────────────────────────────────�?�? Layer 0-9: ZephyrAlpha量化交易系统                      �?�? ├─ Layer 0: 数据源层 (QMT/iFind/Baostock)              �?�? ├─ Layer 1: 数据预处理层                                �?�? ├─ Layer 2: Alpha因子�?                                �?�? ├─ Layer 3: 因子组合�?                                 �?�? ├─ Layer 4: 机器学习�?                                 �?�? ├─ Layer 5: 策略引擎�?                                 �?�? ├─ Layer 6: 风险管理�?                                 �?�? ├─ Layer 7: 执行引擎�?                                 �?�? ├─ Layer 8: 监控告警�?                                 �?�? └─ Layer 9: AI增强�?                                   �?└─────────────────────────────────────────────────────────�?                        �?┌─────────────────────────────────────────────────────────�?�? 量化交易平台：VNPY (VeighNa)                            �?�? ├─ 策略执行引擎                                         �?�? ├─ 风险管理引擎                                         �?�? └─ 交易接口 (QMT/CTP/XTP)                              �?└─────────────────────────────────────────────────────────�?```

---

## 2. 架构设计

### 2.1 三层架构

#### 2.1.1 Web界面�?(Open WebUI)

**技术栈**: Open WebUI (开源项�?  
**GitHub**: https://github.com/open-webui/open-webui  
**Stars**: 50k+

**核心功能**�?```yaml
用户界面:
  - 响应式设�? PC/手机/平板自适应
  - PWA支持: 手机离线使用
  - 深色/浅色主题: 自动切换
  - Markdown + LaTeX: 富文本显�?
交互方式:
  - 文字输入: 主要交互方式
  - 语音输入: 内置语音识别
  - 文件上传: PDF/Word/TXT文档
  - 图片上传: 图表分析

AI能力:
  - 多模型切�? 一键切换不同模�?  - RAG文档检�? 上传文档后智能检�?  - 网络搜索: 集成搜索引擎
  - 图像生成: DALL-E/SD集成

管理功能:
  - 用户权限管理: RBAC权限控制
  - 对话历史: 永久保存
  - 模型管理: 拉取/删除模型
  - 插件系统: 扩展功能
```

**部署方式**�?```bash
# Docker一键部�?docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

#### 2.1.2 Agent框架�?(LangChain 1.0)

**技术栈**: LangChain 1.0 + LangGraph  
**GitHub**: https://github.com/langchain-ai/langchain  
**Stars**: 90k+

**核心架构**�?```python
# LangChain 1.0 标准化Agent创建
from langchain.agents import create_agent
from langchain.tools import Tool

# 定义工具
tools = [
    Tool(name="配置策略", func=configure_strategy, description="..."),
    Tool(name="调整风控", func=adjust_risk_control, description="..."),
    Tool(name="查询状�?, func=query_system_status, description="...")
]

# 创建Agent（一行代码）
agent = create_agent(
    model="deepseek-r1:14b",  # 本地模型
    tools=tools,
    system_prompt="你是ZephyrAlpha量化交易系统的AI助手..."
)
```

**核心特�?*�?```yaml
ReAct循环:
  - Reason: 推理用户意图
  - Act: 调用工具执行
  - Observe: 观察执行结果
  - Decide: 决定下一步行�?
Middleware中间�?
  - PII检�? 自动脱敏敏感信息
  - 人工审批: 关键操作需确认
  - 自动重试: 失败自动重试
  - 监控钩子: 实时监控执行

Memory记忆:
  - 对话历史: 多轮对话上下�?  - 长期记忆: 向量数据库存�?  - 工作记忆: 当前会话状�?```

#### 2.1.3 智能路由�?(Model Router)

**核心逻辑**�?```python
def route_request(user_input: str) -> str:
    """根据任务复杂度智能路�?""
    
    # 1. 简单查�?�?本地小模型（最快）
    if is_simple_query(user_input):
        return "deepseek-r1:8b"  # 5.2GB，推理快
    
    # 2. 策略配置 �?本地中模型（平衡�?    elif is_strategy_config(user_input):
        return "deepseek-r1:14b"  # 9GB，推理强
    
    # 3. 代码生成 �?本地编程模型
    elif is_code_generation(user_input):
        return "qwen2.5-coder:14b"  # 编程专用
    
    # 4. 复杂分析 �?本地大模型（最强）
    elif is_complex_analysis(user_input):
        return "qwen3-coder:30b"  # 18GB，综合最�?    
    # 5. 紧急任�?�?云端API（备份）
    elif is_urgent_task(user_input):
        return "gpt-4-turbo"  # 云端最�?    
    # 6. 默认 �?本地中模�?    else:
        return "deepseek-r1:14b"
```

**路由策略�?*�?
| 任务类型 | 模型选择 | 显存占用 | 响应时间 | 适用场景 |
|----------|----------|----------|----------|----------|
| **简单查�?* | deepseek-r1:8b | ~6GB | <1s | 状态查询、参数查�?|
| **策略配置** | deepseek-r1:14b | ~10GB | 1-2s | 策略创建、参数调�?|
| **代码生成** | qwen2.5-coder:14b | ~10GB | 1-2s | 策略代码生成 |
| **复杂分析** | qwen3-coder:30b | ~20GB | 2-3s | 市场分析、风险评�?|
| **紧急任�?* | gpt-4-turbo | 云端 | 1-2s | 本地故障、特殊任�?|

---

## 3. 技术选型

### 3.1 核心技术栈

| 层级 | 技术选型 | 版本 | Stars | 推荐理由 |
|------|----------|------|-------|----------|
| **Web界面** | Open WebUI | Latest | 50k+ | 用户友好、功能丰富、本地部�?|
| **Agent框架** | LangChain | 1.0 | 90k+ | 生产级架构、标准化设计 |
| **本地LLM** | Ollama | Latest | 100k+ | 一键部署、模型丰�?|
| **量化平台** | VNPY | 4.0+ | 28.4k | 国内最成熟、接口最�?|
| **向量数据�?* | Milvus | 2.0+ | 30k+ | 高性能、可扩展 |

### 3.2 模型选择

#### 3.2.1 本地模型（推荐）

| 模型 | 大小 | 显存需�?| 中文能力 | 推理能力 | 编程能力 | 推荐指数 |
|------|------|----------|----------|----------|----------|----------|
| **deepseek-r1:8b** | 5.2GB | ~6GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐�?| ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **deepseek-r1:14b** | 9.0GB | ~10GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐�?| ⭐⭐⭐⭐�?| ⭐⭐⭐⭐�?|
| **qwen2.5-coder:14b** | 9.0GB | ~10GB | ⭐⭐⭐⭐�?| ⭐⭐⭐⭐ | ⭐⭐⭐⭐�?| ⭐⭐⭐⭐�?|
| **qwen3-coder:30b** | 18GB | ~20GB | ⭐⭐⭐⭐�?| ⭐⭐⭐⭐�?| ⭐⭐⭐⭐�?| ⭐⭐⭐⭐�?|

**推荐配置**�?- **主力模型**: `deepseek-r1:14b`（推理能力强，适合策略决策�?- **编程模型**: `qwen2.5-coder:14b`（编程能力强，适合策略开发）
- **最强模�?*: `qwen3-coder:30b`（综合最强，RTX 3090完美支持�?
#### 3.2.2 云端API（备份）

| 模型 | 提供�?| 成本 | 推理能力 | 适用场景 |
|------|--------|------|----------|----------|
| **GPT-4 Turbo** | OpenAI | ¥0.03/1k tokens | ⭐⭐⭐⭐�?| 复杂分析、紧急任�?|
| **Claude 3.5 Sonnet** | Anthropic | ¥0.02/1k tokens | ⭐⭐⭐⭐�?| 长文本分析、代码生�?|
| **Qwen-Max** | 阿里�?| ¥0.01/1k tokens | ⭐⭐⭐⭐�?| 中文理解、成本优�?|

### 3.3 量化平台选择

#### 为什么选择VNPY�?
**专业机构的选择逻辑**�?
| 机构类型 | 选择平台 | 理由 |
|----------|----------|------|
| **私募基金** | VNPY | 国内接口最全，合规性好 |
| **券商自营** | VNPY + 自研 | 稳定性要求高，本地部�?|
| **量化团队** | QuantConnect | 国际化，多市场支�?|
| **个人量化** | VNPY | 开源免费，社区活跃 |

**VNPY核心优势**�?```yaml
市场覆盖:
  - 股票: 上交所、深交所、北交所
  - 期货: 上期所、大商所、郑商所、中金所
  - 期权: 股票期权、商品期�?  - 外盘: 美股、港股、加密货�?
接口支持:
  - 券商接口: QMT、XTP、LTS、中泰、华鑫等40+
  - 数据接口: 迅投研、米筐、Tushare、AkShare
  - 行情接口: CTP、飞马、易盛、恒�?
策略引擎:
  - CTA策略: 趋势跟踪、均值回�?  - Alpha策略: 多因子、机器学�?  - 组合策略: 多标的、跨市场
  - 套利策略: 期现套利、跨期套�?
风控系统:
  - 实时风控: 止损止盈、仓位控�?  - 合规风控: 敞口限制、交易限�?  - 资金管理: 资金分配、风险预�?
回测系统:
  - 高性能回测: 分钟级、秒�?  - 精确撮合: 滑点、手续费、冲击成�?  - 绩效分析: 夏普比率、最大回撤、胜�?```

---

## 4. 核心模块

### 4.1 模块清单

| 模块ID | 模块名称 | 功能描述 | 优先�?| 预计工时 |
|--------|----------|----------|--------|----------|
| **L11_WEB_UI** | Web界面模块 | Open WebUI部署和配�?| P0 | 8h |
| **L11_AGENT** | Agent框架模块 | LangChain Agent开�?| P0 | 20h |
| **L11_ROUTER** | 智能路由模块 | 模型选择和路由逻辑 | P0 | 12h |
| **L11_TOOLS** | 工具集模�?| 量化交易工具开�?| P0 | 24h |
| **L11_MEMORY** | 记忆管理模块 | 对话历史和长期记�?| P1 | 8h |
| **L11_SECURITY** | 安全模块 | PII检测、权限控�?| P1 | 8h |

### 4.2 工具集详细设�?
#### 4.2.1 核心工具列表

| 工具名称 | 功能描述 | 输入参数 | 输出结果 |
|----------|----------|----------|----------|
| **配置策略** | 创建或修改交易策�?| strategy_type, holding_period, stop_loss | 策略ID和配置确�?|
| **调整风控** | 调整风控参数 | max_drawdown, position_limit, stop_loss | 风控配置确认 |
| **查询状�?* | 查询系统运行状�?| query_type | 系统状态报�?|
| **运行回测** | 执行策略回测 | strategy_id, start_date, end_date | 回测结果报告 |
| **查询持仓** | 查询当前持仓 | �?| 持仓列表和详�?|
| **查询委托** | 查询委托订单 | �?| 委托列表和状�?|
| **查询成交** | 查询成交记录 | �?| 成交列表和详�?|
| **查询资金** | 查询资金状况 | �?| 资金余额和明�?|
| **导出报告** | 导出交易报告 | report_type, date_range | 报告文件 |
| **智能建议** | AI分析和建�?| market_data | 策略建议报告 |

#### 4.2.2 工具实现示例

**文件路径**: `src/layer_11/tools/quant_tools.py`

```python
"""
ZephyrAlpha量化交易工具�?用于LangChain Agent调用
"""
from langchain.tools import Tool
from typing import Dict, Any, Optional
import json

class QuantTradingTools:
    """量化交易工具�?""
    
    def __init__(self):
        """初始化工具集"""
        self.strategies = {}  # 策略存储
        self.risk_config = {  # 风控配置
            "max_drawdown": 0.15,
            "position_limit": 0.1,
            "stop_loss": 0.08
        }
    
    def configure_strategy(self, params: str) -> str:
        """
        配置交易策略
        
        参数格式（JSON字符串）�?        {
            "strategy_type": "momentum",  # 策略类型
            "holding_period": 5,  # 持仓周期（天�?            "stop_loss": 0.1,  # 止损比例
            "max_position": 20  # 最大持仓数�?        }
        """
        try:
            # 解析参数
            if isinstance(params, str):
                config = json.loads(params)
            else:
                config = params
            
            strategy_type = config.get("strategy_type", "momentum")
            holding_period = config.get("holding_period", 5)
            stop_loss = config.get("stop_loss", 0.1)
            max_position = config.get("max_position", 20)
            
            # 生成策略ID
            strategy_id = f"strategy_{len(self.strategies) + 1}"
            
            # 保存策略配置
            self.strategies[strategy_id] = {
                "type": strategy_type,
                "holding_period": holding_period,
                "stop_loss": stop_loss,
                "max_position": max_position,
                "status": "configured"
            }
            
            return f"""�?策略配置成功�?
策略ID: {strategy_id}
策略类型: {self._get_strategy_name(strategy_type)}
持仓周期: {holding_period}�?止损比例: {stop_loss*100}%
最大持�? {max_position}只股�?
预计年化收益: 15-25%
建议风险等级: 中等

是否需要立即启动回测验证？"""
            
        except Exception as e:
            return f"�?策略配置失败：{str(e)}"
    
    def adjust_risk_control(self, params: str) -> str:
        """
        调整风控参数
        
        参数格式（JSON字符串）�?        {
            "max_drawdown": 0.10,  # 最大回�?            "position_limit": 0.05,  # 单只仓位上限
            "stop_loss": 0.08  # 止损比例
        }
        """
        try:
            # 解析参数
            if isinstance(params, str):
                config = json.loads(params)
            else:
                config = params
            
            # 更新风控配置
            if "max_drawdown" in config:
                self.risk_config["max_drawdown"] = config["max_drawdown"]
            if "position_limit" in config:
                self.risk_config["position_limit"] = config["position_limit"]
            if "stop_loss" in config:
                self.risk_config["stop_loss"] = config["stop_loss"]
            
            return f"""�?风控参数已更新！

当前风控配置�?- 最大回撤限�? {self.risk_config['max_drawdown']*100}%
- 单只股票仓位上限: {self.risk_config['position_limit']*100}%
- 止损比例: {self.risk_config['stop_loss']*100}%

风险等级: {'低风�? if self.risk_config['max_drawdown'] < 0.1 else '中等风险'}
建议: {'当前配置较为保守，适合稳健型投资�? if self.risk_config['max_drawdown'] < 0.1 else '当前配置适中，适合平衡型投资�?}"""
            
        except Exception as e:
            return f"�?风控调整失败：{str(e)}"
    
    def query_system_status(self, query: str = "") -> str:
        """查询系统状�?""
        try:
            # 模拟系统状态数�?            status = {
                "system_health": 95,
                "strategies_count": len(self.strategies),
                "active_strategies": sum(1 for s in self.strategies.values() if s.get("status") == "active"),
                "recent_return": 8.5,
                "max_drawdown": 6.2,
                "positions_count": 15,
                "last_update": "2026-04-02 15:30:00"
            }
            
            return f"""📊 系统运行状�?
系统健康�? {status['system_health']}�?运行时间: 72小时无中�?
📈 策略概况
- 已配置策�? {status['strategies_count']}�?- 运行中策�? {status['active_strategies']}�?
💰 最�?0天表�?- 收益�? {status['recent_return']}%
- 最大回�? {status['max_drawdown']}%
- 夏普比率: 1.85

📦 持仓情况
- 当前持仓: {status['positions_count']}只股�?- 主要板块: 消费(35%)、科技(30%)、金�?20%)

最后更�? {status['last_update']}
建议: 系统运行正常，策略表现良好，建议保持当前配置�?""
            
        except Exception as e:
            return f"�?状态查询失败：{str(e)}"
    
    def run_backtest(self, params: str) -> str:
        """
        运行回测
        
        参数格式�?        {
            "strategy_id": "strategy_1",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_capital": 1000000
        }
        """
        try:
            # 解析参数
            if isinstance(params, str):
                config = json.loads(params)
            else:
                config = params
            
            strategy_id = config.get("strategy_id", "strategy_1")
            start_date = config.get("start_date", "2023-01-01")
            end_date = config.get("end_date", "2023-12-31")
            initial_capital = config.get("initial_capital", 1000000)
            
            # 模拟回测结果
            return f"""📊 回测完成�?
回测区间: {start_date} �?{end_date}
初始资金: ¥{initial_capital:,.0f}

📈 回测结果
- 总收益率: 45.2%
- 年化收益�? 45.2%
- 最大回�? 12.3%
- 夏普比率: 2.15
- 胜率: 62.5%
- 盈亏�? 1.85

💰 资金曲线
- 起始: ¥{initial_capital:,.0f}
- 最�? ¥{initial_capital * 1.52:,.0f}
- 最�? ¥{initial_capital * 0.88:,.0f}
- 结束: ¥{initial_capital * 1.45:,.0f}

�?策略表现优秀，建议实盘部署�?是否需要启动模拟交易？"""
            
        except Exception as e:
            return f"�?回测失败：{str(e)}"
    
    def _get_strategy_name(self, strategy_type: str) -> str:
        """获取策略中文名称"""
        strategy_names = {
            "momentum": "动量因子策略",
            "value": "价值因子策�?,
            "quality": "质量因子策略",
            "growth": "成长因子策略",
            "multi_factor": "多因子策�?
        }
        return strategy_names.get(strategy_type, strategy_type)
    
    def get_tools(self) -> list:
        """获取LangChain工具列表"""
        return [
            Tool(
                name="配置策略",
                func=self.configure_strategy,
                description="""配置交易策略参数�?                
输入格式（JSON字符串）�?{
    "strategy_type": "momentum",  # 策略类型：momentum/value/quality/growth
    "holding_period": 5,  # 持仓周期（天�?    "stop_loss": 0.1,  # 止损比例�?.1表示10%�?    "max_position": 20  # 最大持仓数�?}

示例�?{"strategy_type": "momentum", "holding_period": 5, "stop_loss": 0.1, "max_position": 20}"""
            ),
            Tool(
                name="调整风控",
                func=self.adjust_risk_control,
                description="""调整风控参数�?                
输入格式（JSON字符串）�?{
    "max_drawdown": 0.10,  # 最大回撤限制（0.10表示10%�?    "position_limit": 0.05,  # 单只仓位上限�?.05表示5%�?    "stop_loss": 0.08  # 止损比例�?.08表示8%�?}

示例�?{"max_drawdown": 0.10, "position_limit": 0.05}"""
            ),
            Tool(
                name="查询状�?,
                func=self.query_system_status,
                description="查询系统运行状态、策略表现、持仓情况等。输入任意字符串即可�?
            ),
            Tool(
                name="运行回测",
                func=self.run_backtest,
                description="""运行策略回测�?                
输入格式（JSON字符串）�?{
    "strategy_id": "strategy_1",  # 策略ID
    "start_date": "2023-01-01",  # 开始日�?    "end_date": "2023-12-31",  # 结束日期
    "initial_capital": 1000000  # 初始资金
}

示例�?{"strategy_id": "strategy_1", "start_date": "2023-01-01", "end_date": "2023-12-31"}"""
            )
        ]
```

---

## 5. 实施方案

### 5.1 分阶段实施计�?
#### Phase 1：基础部署�?周）

**目标**：搭建基础架构，实现核心功�?
**Day 1-2：部署Open WebUI**
```bash
# 1. 安装Docker（如果没有）
# Windows: 下载Docker Desktop
# https://www.docker.com/products/docker-desktop

# 2. 启动Open WebUI
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# 3. 访问界面
# http://localhost:3000
```

**Day 3-4：配置本地模�?*
```bash
# 您已有模型，只需验证
ollama run deepseek-r1:14b  # 测试推理能力
ollama run qwen2.5-coder:14b  # 测试编程能力
ollama run qwen3-coder:30b  # 测试综合能力

# 可选：下载更专业的模型
ollama pull qwen2.5:14b  # 通义千问最新版
ollama pull llama3.2:latest  # Meta最新开源模�?```

**Day 5-7：安装VNPY**
```bash
# 1. 安装VNPY核心
pip install vnpy

# 2. 安装QMT接口
pip install vnpy_qmt

# 3. 安装策略引擎
pip install vnpy_ctastrategy vnpy_ctabacktester

# 4. 安装风控模块
pip install vnpy_riskmanager

# 5. 安装图表模块
pip install vnpy_chartwizard

# 6. 验证安装
python -c "import vnpy; print(vnpy.__version__)"
```

**交付�?*�?- �?Open WebUI运行正常
- �?本地模型可用
- �?VNPY安装成功

#### Phase 2：核心开发（2周）

**目标**：开发核心工具集和Agent

**Week 2：开发工具集**
- 创建`src/layer_11/tools/quant_tools.py`
- 实现10个核心工�?- 编写单元测试

**Week 3：创建Agent**
- 创建`src/layer_11/agent/quant_agent.py`
- 实现智能路由逻辑
- 集成LangChain 1.0
- 测试多轮对话

**交付�?*�?- �?10个核心工具可�?- �?Agent可以理解用户意图
- �?多轮对话正常

#### Phase 3：集成部署（1周）

**目标**：集成所有模块，部署上线

**Day 1-3：系统集�?*
- 集成Open WebUI + LangChain + VNPY
- 端到端测�?- 性能优化

**Day 4-5：安全加�?*
- PII检�?- 权限控制
- 数据加密

**Day 6-7：生产部�?*
- 部署脚本
- 监控告警
- 文档完善

**交付�?*�?- �?系统集成完成
- �?安全加固完成
- �?生产环境部署

### 5.2 技术难点与解决方案

| 技术难�?| 解决方案 | 风险等级 |
|----------|----------|----------|
| **自然语言理解准确�?* | 使用专业Prompt + 领域术语映射 | �?|
| **多轮对话上下文管�?* | LangChain Memory + 向量数据�?| �?|
| **工具调用安全�?* | Middleware中间�?+ 人工审批 | �?|
| **模型推理速度** | GPU加�?+ 模型量化 | �?|
| **系统稳定�?* | 本地+云端双备�?+ 自动重试 | �?|

---

## 6. 硬件配置

### 6.1 当前硬件评估

**用户配置**�?```yaml
GPU: NVIDIA GeForce RTX 3090 24GB
    评级: ⭐⭐⭐⭐�?(专业�?
    能力: 可运�?0B参数模型
    
内存: 64GB DDR4 2400MHz
    评级: ⭐⭐⭐⭐�?(充足)
    能力: 支持大模型推�?    
CPU: Intel Core i7-12700KF 3.60GHz
    评级: ⭐⭐⭐⭐�?(高性能)
    能力: 多任务处理能力强
    
存储: 1.82TB (剩余630GB)
    评级: ⭐⭐⭐⭐ (足够)
    能力: 可存储多个模�?```

**综合评分**: ⭐⭐⭐⭐�?**专业级配�?*

### 6.2 硬件需求对�?
| 配置�?| 最低要�?| 推荐配置 | 您的配置 | 评级 |
|--------|----------|----------|----------|------|
| **GPU显存** | 8GB | 16GB | 24GB | ⭐⭐⭐⭐�?|
| **内存** | 16GB | 32GB | 64GB | ⭐⭐⭐⭐�?|
| **CPU核心** | 4�?| 8�?| 12�?| ⭐⭐⭐⭐�?|
| **存储空间** | 50GB | 200GB | 630GB可用 | ⭐⭐⭐⭐ |

### 6.3 性能预估

**本地模型性能**�?```yaml
deepseek-r1:8b:
  推理速度: 50-80 tokens/s
  响应延迟: <500ms
  显存占用: ~6GB
  
deepseek-r1:14b:
  推理速度: 30-50 tokens/s
  响应延迟: <1s
  显存占用: ~10GB
  
qwen3-coder:30b:
  推理速度: 20-30 tokens/s
  响应延迟: 1-2s
  显存占用: ~20GB
```

**对比云端API**�?```yaml
GPT-4 Turbo:
  推理速度: 30-60 tokens/s
  响应延迟: 500-1000ms
  成本: ¥0.03/1k tokens
  
结论: 本地模型性能不逊于云端API
```

---

## 7. 成本评估

### 7.1 硬件成本

| 项目 | 配置 | 成本 | 说明 |
|------|------|------|------|
| **服务�?* | 本地PC | ¥0 | 使用现有设备 |
| **GPU（可选）** | RTX 3090 24GB | ¥0 | 已有 |
| **云服务器（可选）** | 4�?6G | ¥200/�?| 阿里�?腾讯�?|

### 7.2 软件成本

| 项目 | 方案 | 成本 | 说明 |
|------|------|------|------|
| **LLM API** | 本地Ollama | ¥0 | 完全免费 |
| **LLM API** | GPT-4 API | ¥10-50/�?| 按使用量计费 |
| **LLM API** | 通义千问 | ¥5-30/�?| 国产模型更便�?|
| **量化平台** | VNPY开源版 | ¥0 | 完全免费 |
| **Web界面** | Open WebUI | ¥0 | 开源免�?|
| **向量数据�?* | Milvus | ¥0 | 开源免�?|

### 7.3 总成本对�?
**方案A：完全本地化（推荐）**
```yaml
初期投入: ¥0
月度成本: ¥0
年度成本: ¥0

优势:
  - 数据隐私100%
  - 无API费用
  - 不依赖网�?```

**方案B：云端部�?*
```yaml
初期投入: ¥0
月度成本: ¥200-500
  - 云服务器: ¥200/�?  - API费用: ¥0-300/�?年度成本: ¥2400-6000

优势:
  - 随时随地访问
  - 无需本地设备
```

**方案C：混合架构（最佳）**
```yaml
初期投入: ¥0
月度成本: ¥0-100
  - 本地优先: ¥0
  - 云端备份: ¥0-100
年度成本: ¥0-1200

优势:
  - 本地优先，数据隐�?  - 云端备份，高可用�?  - 成本可控
```

### 7.4 ROI分析

**投入产出�?*�?```yaml
投入:
  - 开发时�? 80小时
  - 硬件成本: ¥0
  - 软件成本: ¥0/�?
产出:
  - 节省API费用: ¥300-500/�?  - 提升效率: 10倍（无需编程�?  - 数据隐私: 无价

ROI: 无限大（零成�?+ 正收益）
```

---

## 8. 部署指南

### 8.1 快速部署脚�?
**文件路径**: `start_quant_system.py`

```python
"""
ZephyrAlpha量化交易系统启动脚本
"""
import subprocess
import time
import webbrowser
from pathlib import Path

def check_ollama():
    """检查Ollama服务"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """启动Ollama服务"""
    print("🚀 启动Ollama服务...")
    subprocess.Popen(["ollama", "serve"], shell=True)
    time.sleep(3)

def start_open_webui():
    """启动Open WebUI"""
    print("🌐 启动Open WebUI...")
    subprocess.Popen([
        "docker", "start", "open-webui"
    ], shell=True)
    time.sleep(5)

def main():
    """主函�?""
    print("=" * 60)
    print("ZephyrAlpha量化交易系统启动")
    print("=" * 60)
    
    # 1. 检查Ollama
    if not check_ollama():
        print("⚠️  Ollama服务未启动，正在启动...")
        start_ollama()
    else:
        print("�?Ollama服务已运�?)
    
    # 2. 启动Open WebUI
    print("🌐 启动Web界面...")
    start_open_webui()
    
    # 3. 打开浏览�?    print("📱 打开浏览�?..")
    webbrowser.open("http://localhost:3000")
    
    print("\n" + "=" * 60)
    print("�?系统启动成功�?)
    print("=" * 60)
    print("\n访问地址: http://localhost:3000")
    print("\n可用模型:")
    print("  - deepseek-r1:14b (推荐，推理强)")
    print("  - qwen2.5-coder:14b (编程�?")
    print("  - qwen3-coder:30b (综合最�?")
    print("\n使用方法:")
    print("  1. 在Web界面选择模型")
    print("  2. 输入文字描述操作需�?)
    print("  3. 系统自动理解并执�?)
    print("\n示例对话:")
    print('  - "我想创建一个动量因子策略，持仓5天，止损10%"')
    print('  - "把最大回撤限制调整到10%"')
    print('  - "告诉我系统当前状�?')
    print("\n按Ctrl+C退出系�?)

if __name__ == "__main__":
    main()
```

### 8.2 部署检查清�?
```markdown
## 部署前检�?
### 环境准备
- [ ] Docker Desktop已安�?- [ ] Ollama已安�?- [ ] Python 3.9+已安�?- [ ] Git已安�?
### 模型准备
- [ ] deepseek-r1:14b已下�?- [ ] qwen2.5-coder:14b已下�?- [ ] qwen3-coder:30b已下载（可选）

### 依赖安装
- [ ] vnpy已安�?- [ ] vnpy_qmt已安�?- [ ] langchain已安�?- [ ] langchain-openai已安�?
### 配置文件
- [ ] 系统配置文件已创�?- [ ] Agent配置文件已创�?- [ ] 工具配置文件已创�?
### 测试验证
- [ ] Ollama服务正常
- [ ] Open WebUI可访�?- [ ] 模型推理正常
- [ ] Agent对话正常
- [ ] 工具调用正常
```

---

## 9. 测试方案

### 9.1 单元测试

**文件路径**: `tests/layer_11/test_quant_tools.py`

```python
"""
量化交易工具集单元测�?"""
import pytest
from src.layer_11.tools.quant_tools import QuantTradingTools

class TestQuantTradingTools:
    """量化交易工具集测�?""
    
    def setup_method(self):
        """测试前准�?""
        self.tools = QuantTradingTools()
    
    def test_configure_strategy(self):
        """测试策略配置"""
        params = '{"strategy_type": "momentum", "holding_period": 5, "stop_loss": 0.1, "max_position": 20}'
        result = self.tools.configure_strategy(params)
        
        assert "�?策略配置成功" in result
        assert "动量因子策略" in result
        assert "5�? in result
        assert "10%" in result
    
    def test_adjust_risk_control(self):
        """测试风控调整"""
        params = '{"max_drawdown": 0.10, "position_limit": 0.05}'
        result = self.tools.adjust_risk_control(params)
        
        assert "�?风控参数已更�? in result
        assert "10%" in result
        assert "5%" in result
    
    def test_query_system_status(self):
        """测试状态查�?""
        result = self.tools.query_system_status("")
        
        assert "📊 系统运行状�? in result
        assert "系统健康�? in result
        assert "收益�? in result
    
    def test_run_backtest(self):
        """测试回测运行"""
        params = '{"strategy_id": "strategy_1", "start_date": "2023-01-01", "end_date": "2023-12-31"}'
        result = self.tools.run_backtest(params)
        
        assert "📊 回测完成" in result
        assert "收益�? in result
        assert "夏普比率" in result
```

### 9.2 集成测试

**文件路径**: `tests/layer_11/test_integration.py`

```python
"""
集成测试
"""
import pytest
from src.layer_11.agent.quant_agent import QuantTradingAgent

class TestIntegration:
    """集成测试"""
    
    def setup_method(self):
        """测试前准�?""
        self.agent = QuantTradingAgent(model_name="deepseek-r1:14b")
    
    def test_strategy_configuration_flow(self):
        """测试策略配置流程"""
        # 用户输入
        user_input = "我想创建一个动量因子策略，持仓5天，止损10%"
        
        # Agent处理
        result = self.agent.chat(user_input)
        
        # 验证结果
        assert "策略" in result
        assert "配置" in result
    
    def test_multi_turn_conversation(self):
        """测试多轮对话"""
        # 第一�?        response1 = self.agent.chat("我想创建一个策�?)
        assert "策略" in response1
        
        # 第二轮（记住上下文）
        response2 = self.agent.chat("动量因子")
        assert "动量" in response2
        
        # 第三轮（记住上下文）
        response3 = self.agent.chat("持仓5�?)
        assert "5" in response3
```

### 9.3 性能测试

```python
"""
性能测试
"""
import time
from src.layer_11.agent.quant_agent import QuantTradingAgent

def test_response_time():
    """测试响应时间"""
    agent = QuantTradingAgent(model_name="deepseek-r1:14b")
    
    # 测试10�?    times = []
    for i in range(10):
        start = time.time()
        agent.chat("查询系统状�?)
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    print(f"平均响应时间: {avg_time:.2f}�?)
    
    assert avg_time < 3.0  # 平均响应时间小于3�?```

---

## 10. 监控运维

### 10.1 监控指标

| 指标类别 | 指标名称 | 阈�?| 告警级别 |
|----------|----------|------|----------|
| **系统性能** | CPU使用�?| >80% | P1 |
| **系统性能** | 内存使用�?| >90% | P1 |
| **系统性能** | GPU显存使用�?| >90% | P1 |
| **模型性能** | 推理延迟 | >5s | P2 |
| **模型性能** | 吞吐�?| <10 tokens/s | P2 |
| **业务指标** | 工具调用成功�?| <95% | P0 |
| **业务指标** | 用户满意�?| <80% | P1 |

### 10.2 日志规范

```python
"""
日志配置
"""
import logging
from pathlib import Path

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/layer_11.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('Layer11')

# 日志示例
logger.info("系统启动")
logger.info("用户输入: 我想创建一个动量因子策�?)
logger.info("模型选择: deepseek-r1:14b")
logger.info("工具调用: 配置策略")
logger.info("执行结果: 策略配置成功")
```

### 10.3 告警规则

```yaml
告警规则:
  P0级告警（立即处理�?
    - 系统崩溃
    - 工具调用失败�?> 10%
    - 数据泄露风险
    
  P1级告警（2小时内处理）:
    - CPU使用�?> 80%
    - 内存使用�?> 90%
    - GPU显存使用�?> 90%
    
  P2级告警（24小时内处理）:
    - 推理延迟 > 5s
    - 用户满意�?< 80%
```

---

## 11. 演进规划

### 11.1 版本路线�?
```yaml
v1.0 (2026-04-02):
  功能:
    - 基础文字驱动
    - 10个核心工�?    - 本地模型支持
  状�? �?设计完成

v1.1 (2026-05-01):
  功能:
    - 增加工具数量�?0�?    - 优化自然语言理解
    - 添加语音输入
  状�? 📅 计划�?
v1.2 (2026-06-01):
  功能:
    - 多Agent协作
    - 智能建议系统
    - 自动化报告生�?  状�? 📅 计划�?
v2.0 (2026-09-01):
  功能:
    - 自主决策Agent
    - 强化学习优化
    - 多模态输入（图片、视频）
  状�? 📅 规划�?```

### 11.2 技术演�?
```yaml
短期�?-3个月�?
  - 优化Prompt工程
  - 增加工具数量
  - 提升推理速度

中期�?-6个月�?
  - 多Agent协作
  - 强化学习
  - 知识图谱

长期�?-12个月�?
  - 自主决策Agent
  - 多模态理�?  - 联邦学习
```

---

## 12. 风险评估

### 12.1 风险矩阵

| 风险类别 | 风险描述 | 发生概率 | 影响程度 | 风险等级 | 缓解措施 |
|----------|----------|----------|----------|----------|----------|
| **技术风�?* | 模型理解不准�?| �?| �?| P0 | 专业Prompt + 人工确认 |
| **技术风�?* | 工具调用失败 | �?| �?| P1 | 自动重试 + 异常处理 |
| **安全风险** | 数据泄露 | �?| 极高 | P0 | 本地部署 + PII检�?|
| **性能风险** | 推理速度�?| �?| �?| P2 | GPU加�?+ 模型量化 |
| **运维风险** | 系统崩溃 | �?| �?| P1 | 本地+云端双备�?|

### 12.2 应急预�?
```yaml
场景1: 模型理解错误
  应急措�?
    1. 提示用户确认
    2. 人工审核关键操作
    3. 回滚错误操作
  
场景2: 工具调用失败
  应急措�?
    1. 自动重试3�?    2. 切换到备用工�?    3. 通知管理�?  
场景3: 系统崩溃
  应急措�?
    1. 自动重启服务
    2. 切换到云端API
    3. 恢复最近备�?```

---

## 📚 相关文档索引

### 核心蓝图文档

| 文档名称 | 路径 | 说明 |
|---------|------|------|
| [Layer 11工具封装蓝图](./LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md` | 工具封装架构、单一AI层设计、纯执行层分�?|
| [Layer 11工具接口规范](./LAYER_11_TOOL_INTERFACE_SPECIFICATION.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_INTERFACE_SPECIFICATION.md` | 所有模块工具接口详细定义、操作规�?|
| [文字驱动核心模块](./L11_TEXT_DRIVER.md) | `docs/module_designs/layer_11/L11_TEXT_DRIVER.md` | NLU设计、意图识别、参数提�?|
| [量化交易Agent模块](./L11_QUANT_AGENT.md) | `docs/module_designs/layer_11/L11_QUANT_AGENT.md` | Agent框架、模型管理、工具集�?|

---

## 📚 参考文�?
### 开源项�?
1. **Open WebUI** - 用户友好的Web界面
   - GitHub: https://github.com/open-webui/open-webui
   - Stars: 50k+
   - 文档: https://docs.openwebui.com

2. **LangChain** - Agent框架
   - GitHub: https://github.com/langchain-ai/langchain
   - Stars: 90k+
   - 文档: https://python.langchain.com

3. **VNPY** - 量化交易平台
   - GitHub: https://github.com/vnpy/vnpy
   - Stars: 28.4k
   - 文档: https://www.vnpy.com

4. **Ollama** - 本地LLM运行
   - GitHub: https://github.com/ollama/ollama
   - Stars: 100k+
   - 文档: https://ollama.com

### 技术文�?
1. **LangChain 1.0 Documentation**
   - https://python.langchain.com/docs/

2. **Open WebUI Documentation**
   - https://docs.openwebui.com/

3. **VNPY Documentation**
   - https://www.vnpy.com/docs/

4. **Ollama Documentation**
   - https://github.com/ollama/ollama/blob/main/docs/api.md

---

## 📝 版本历史

| 版本 | 日期 | 作�?| 变更说明 |
|------|------|------|----------|
| v1.0 | 2026-04-02 | 首席文档架构�?| 初始版本，完整架构设�?|

---

> **设计完成时间**: 2026-04-02  
> **设计状�?*: �?已完�? 
> **下一阶段**: 进入编码实施阶段  
> **关联文档**: [MODULE_DESIGN_PLAN.md](../../02_FACTOR_LIBRARY/MODULE_DESIGN_PLAN.md)
