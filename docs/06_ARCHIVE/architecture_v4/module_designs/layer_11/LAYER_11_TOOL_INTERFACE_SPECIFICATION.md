---
module_id: LAYER_11_TOOL_INTERFACE_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席蓝图架构师
standard_type: 专业量化机构蓝图
applicable_scope: Layer 11工具接口规范
compliance_level: 专业机构标准
parent_document: ./LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md
implementation_status: 设计阶段
---

# Layer 11工具接口规范

> 清风量化交易系统 v5.2 - 所有模块工具接口详细定义
> **索引**: `LAYER_11_TOOL_SPEC_001`
> **核心定位**: 明确每个模块支持的操作、参数和返回值，避免重复文字交付设计
> **关键原则**: Layer 11统一意图识别，各模块只提供纯API接口


## 一、设计原则

### 1.1 核心原则

| 原则 | 说明 |
|------|------|
| **单一AI层** | Layer 11负责所有意图识别和参数提取 |
| **纯执行层** | 各模块只提供API接口，不包含AI理解 |
| **工具化封装** | 每个模块封装为工具，通过统一接口调用 |
| **接口标准化** | 所有工具遵循统一的输入输出格式 |

### 1.2 细化层次

```
┌─────────────────────────────────────────────────────────┐
│  Layer 11: 文字交付层（统一细化）                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  意图识别 + 参数提取（需要细化设计）                 │ │
│  │  - 用户说"创建动量策略" → 意图: configure_strategy │ │
│  │  - 提取参数: {type: momentum, period: 5}          │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  策略工具     │  │  因子工具     │  │  风控工具     │
│  (工具接口)   │  │  (工具接口)   │  │  (工具接口)   │
│  不需要细化   │  │  不需要细化   │  │  不需要细化   │
│  文字交付     │  │  文字交付     │  │  文字交付     │
└──────────────┘  └──────────────┘  └──────────────┘
```

**关键点**：
- ✅ Layer 11需要细化意图识别和参数提取
- ❌ 各模块不需要细化文字交付设计
- ✅ 各模块只需要明确工具接口规范


## 二、工具接口统一规范

### 2.1 输入参数规范

```python
{
    "action": "操作类型",  # 必需：具体操作名称
    "params": {            # 必需：操作参数
        "param1": "value1",
        "param2": "value2"
    }
}
```

### 2.2 输出结果规范

```python
{
    "success": True,       # 必需：是否成功
    "message": "操作结果描述",  # 必需：结果描述
    "data": {              # 可选：返回数据
        "key1": "value1",
        "key2": "value2"
    },
    "error": None          # 可选：错误信息
}
```


## 三、P0模块工具接口规范

### 3.1 策略工具（StrategyTool）

**模块ID**: L11_TOOL_STRATEGY_001
**优先级**: P0
**覆盖模块**: Layer 5 策略执行层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **configure** | 配置新策略 | strategy_type, holding_period, stop_loss, take_profit | strategy_id |
| **start** | 启动策略 | strategy_id | 启动状态 |
| **stop** | 停止策略 | strategy_id | 停止状态 |
| **status** | 查询策略状态 | strategy_id | 策略状态详情 |
| **list** | 列出所有策略 | 无 | 策略列表 |
| **backtest** | 回测策略 | strategy_id, start_date, end_date | 回测结果 |
| **optimize** | 优化策略参数 | strategy_id, param_ranges | 优化结果 |

#### 操作详细定义

##### 3.1.1 configure（配置策略）

**输入参数**：
```python
{
    "action": "configure",
    "params": {
        "strategy_type": "momentum",      # 必需：策略类型
        "holding_period": 5,               # 可选：持仓周期（天）
        "stop_loss": 0.1,                  # 可选：止损比例
        "take_profit": 0.2,                # 可选：止盈比例
        "position_size": 0.05,             # 可选：仓位大小
        "universe": ["000001.SZ", "600000.SH"]  # 可选：股票池
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "策略配置成功",
    "data": {
        "strategy_id": "STRAT_20260402_001",
        "strategy_name": "动量策略_5日持仓",
        "created_at": "2026-04-02T10:30:00Z",
        "status": "configured"
    }
}
```

##### 3.1.2 start（启动策略）

**输入参数**：
```python
{
    "action": "start",
    "params": {
        "strategy_id": "STRAT_20260402_001"  # 必需：策略ID
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "策略已启动",
    "data": {
        "strategy_id": "STRAT_20260402_001",
        "status": "running",
        "started_at": "2026-04-02T10:35:00Z"
    }
}
```

##### 3.1.3 stop（停止策略）

**输入参数**：
```python
{
    "action": "stop",
    "params": {
        "strategy_id": "STRAT_20260402_001"  # 必需：策略ID
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "策略已停止",
    "data": {
        "strategy_id": "STRAT_20260402_001",
        "status": "stopped",
        "stopped_at": "2026-04-02T11:00:00Z"
    }
}
```

##### 3.1.4 status（查询策略状态）

**输入参数**：
```python
{
    "action": "status",
    "params": {
        "strategy_id": "STRAT_20260402_001"  # 必需：策略ID
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "策略状态查询成功",
    "data": {
        "strategy_id": "STRAT_20260402_001",
        "status": "running",
        "performance": {
            "total_return": 0.15,
            "sharpe_ratio": 1.2,
            "max_drawdown": 0.08,
            "win_rate": 0.65
        },
        "positions": [
            {"symbol": "000001.SZ", "weight": 0.05, "pnl": 0.02},
            {"symbol": "600000.SH", "weight": 0.05, "pnl": -0.01}
        ]
    }
}
```

##### 3.1.5 list（列出所有策略）

**输入参数**：
```python
{
    "action": "list",
    "params": {}
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "策略列表查询成功",
    "data": {
        "strategies": [
            {
                "strategy_id": "STRAT_20260402_001",
                "name": "动量策略_5日持仓",
                "status": "running",
                "created_at": "2026-04-02T10:30:00Z"
            },
            {
                "strategy_id": "STRAT_20260401_002",
                "name": "均值回归策略",
                "status": "stopped",
                "created_at": "2026-04-01T09:00:00Z"
            }
        ],
        "total_count": 2
    }
}
```

---

### 3.2 因子工具（FactorTool）

**模块ID**: L11_TOOL_FACTOR_001
**优先级**: P0
**覆盖模块**: Layer 2 因子层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **query** | 查询因子数据 | factor_name, start_date, end_date | 因子数据 |
| **mine** | AI挖掘新因子 | factor_type, constraints | 新因子定义 |
| **validate** | 验证因子有效性 | factor_id, test_period | 验证结果 |
| **monitor** | 监控因子漂移 | factor_id, threshold | 漂移报告 |

#### 操作详细定义

##### 3.2.1 query（查询因子）

**输入参数**：
```python
{
    "action": "query",
    "params": {
        "factor_name": "momentum",         # 必需：因子名称
        "start_date": "2026-01-01",        # 可选：开始日期
        "end_date": "2026-03-31",          # 可选：结束日期
        "symbols": ["000001.SZ", "600000.SH"]  # 可选：股票代码
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "因子数据查询成功",
    "data": {
        "factor_name": "momentum",
        "factor_values": [
            {"symbol": "000001.SZ", "date": "2026-01-01", "value": 0.05},
            {"symbol": "600000.SH", "date": "2026-01-01", "value": -0.02}
        ],
        "statistics": {
            "mean": 0.015,
            "std": 0.08,
            "ic": 0.12
        }
    }
}
```

##### 3.2.2 mine（挖掘新因子）

**输入参数**：
```python
{
    "action": "mine",
    "params": {
        "factor_type": "momentum",         # 必需：因子类型
        "constraints": {                    # 可选：约束条件
            "max_period": 20,
            "min_ic": 0.05
        }
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "新因子挖掘成功",
    "data": {
        "factor_id": "FACTOR_20260402_001",
        "factor_name": "动量因子_10日",
        "formula": "close.shift(10) / close - 1",
        "ic": 0.08,
        "performance": {
            "mean_return": 0.02,
            "win_rate": 0.55
        }
    }
}
```

---

### 3.3 风控工具（RiskControlTool）

**模块ID**: L11_TOOL_RISK_001
**优先级**: P0
**覆盖模块**: Layer 6 风控层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **adjust_params** | 调整风控参数 | max_drawdown, position_limit | 更新后的参数 |
| **set_stop_loss** | 设置止损 | strategy_id, stop_loss | 止损设置 |
| **set_take_profit** | 设置止盈 | strategy_id, take_profit | 止盈设置 |
| **get_risk_report** | 获取风险报告 | 无 | 风险报告 |

#### 操作详细定义

##### 3.3.1 adjust_params（调整风控参数）

**输入参数**：
```python
{
    "action": "adjust_params",
    "params": {
        "max_drawdown": 0.10,      # 必需：最大回撤
        "position_limit": 0.05,    # 必需：单股仓位上限
        "daily_loss_limit": 0.02   # 可选：单日亏损上限
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "风控参数调整成功",
    "data": {
        "max_drawdown": 0.10,
        "position_limit": 0.05,
        "daily_loss_limit": 0.02,
        "updated_at": "2026-04-02T10:30:00Z"
    }
}
```

##### 3.3.2 set_stop_loss（设置止损）

**输入参数**：
```python
{
    "action": "set_stop_loss",
    "params": {
        "strategy_id": "STRAT_20260402_001",  # 必需：策略ID
        "stop_loss": 0.08                     # 必需：止损比例
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "止损设置成功",
    "data": {
        "strategy_id": "STRAT_20260402_001",
        "stop_loss": 0.08,
        "updated_at": "2026-04-02T10:35:00Z"
    }
}
```

---

### 3.4 授权工具（ApprovalTool）

**模块ID**: L11_TOOL_APPROVAL_001
**优先级**: P0
**覆盖模块**: Layer 8 授权层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **confirm** | 授权确认 | decision_id, approved | 授权结果 |
| **reject** | 拒绝授权 | decision_id, reason | 拒绝结果 |
| **list_pending** | 列出待授权决策 | 无 | 待授权列表 |

#### 操作详细定义

##### 3.4.1 confirm（授权确认）

**输入参数**：
```python
{
    "action": "confirm",
    "params": {
        "decision_id": "DEC_20260402_001",  # 必需：决策ID
        "approved": True,                    # 必需：是否授权
        "comment": "同意上架策略"             # 可选：备注
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "授权确认成功",
    "data": {
        "decision_id": "DEC_20260402_001",
        "status": "approved",
        "approved_at": "2026-04-02T10:30:00Z",
        "approved_by": "user"
    }
}
```


## 四、P1模块工具接口规范

### 4.1 舆情工具（SentimentTool）

**模块ID**: L11_TOOL_SENTIMENT_001
**优先级**: P1
**覆盖模块**: Layer 3 舆情层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **query** | 查询舆情 | symbol, start_date, end_date | 舆情数据 |
| **alert** | 舆情预警 | threshold, keywords | 预警列表 |

#### 操作详细定义

##### 4.1.1 query（查询舆情）

**输入参数**：
```python
{
    "action": "query",
    "params": {
        "symbol": "000001.SZ",        # 必需：股票代码
        "start_date": "2026-03-01",   # 可选：开始日期
        "end_date": "2026-03-31",     # 可选：结束日期
        "keywords": ["业绩", "利好"]   # 可选：关键词
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "舆情查询成功",
    "data": {
        "symbol": "000001.SZ",
        "sentiment_score": 0.65,
        "news": [
            {
                "date": "2026-03-15",
                "title": "平安银行业绩超预期",
                "sentiment": 0.8,
                "source": "财经新闻"
            }
        ]
    }
}
```

---

### 4.2 ML工具（MLTool）

**模块ID**: L11_TOOL_ML_001
**优先级**: P1
**覆盖模块**: Layer 4 机器学习层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **train** | 训练模型 | model_type, features, target | 训练结果 |
| **query** | 查询模型表现 | model_id | 模型表现 |

#### 操作详细定义

##### 4.2.1 train（训练模型）

**输入参数**：
```python
{
    "action": "train",
    "params": {
        "model_type": "LSTM",              # 必需：模型类型
        "features": ["momentum", "volume"], # 必需：特征列表
        "target": "return_5d",             # 必需：目标变量
        "train_period": "2020-2025"        # 可选：训练期间
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "模型训练成功",
    "data": {
        "model_id": "MODEL_20260402_001",
        "model_type": "LSTM",
        "performance": {
            "train_accuracy": 0.75,
            "val_accuracy": 0.68,
            "test_accuracy": 0.65
        },
        "trained_at": "2026-04-02T10:30:00Z"
    }
}
```

---

### 4.3 组合工具（PortfolioTool）

**模块ID**: L11_TOOL_PORTFOLIO_001
**优先级**: P1
**覆盖模块**: Layer 6 组合层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **optimize** | 组合优化 | method, constraints | 优化结果 |
| **query** | 查询组合配置 | 无 | 组合配置 |
| **adjust** | 调整组合权重 | symbol, weight | 调整结果 |

#### 操作详细定义

##### 4.3.1 optimize（组合优化）

**输入参数**：
```python
{
    "action": "optimize",
    "params": {
        "method": "mean_variance",    # 必需：优化方法
        "constraints": {              # 可选：约束条件
            "max_weight": 0.1,
            "min_weight": 0.01
        }
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "组合优化成功",
    "data": {
        "optimized_weights": [
            {"symbol": "000001.SZ", "weight": 0.08},
            {"symbol": "600000.SH", "weight": 0.06}
        ],
        "expected_return": 0.12,
        "expected_risk": 0.15,
        "sharpe_ratio": 0.8
    }
}
```

---

### 4.4 报告工具（ReportTool）

**模块ID**: L11_TOOL_REPORT_001
**优先级**: P1
**覆盖模块**: Layer 7 报告层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **query** | 查询历史报告 | report_type, date | 报告内容 |
| **analyze** | 市场分析 | market_scope | 分析报告 |

#### 操作详细定义

##### 4.4.1 query（查询报告）

**输入参数**：
```python
{
    "action": "query",
    "params": {
        "report_type": "daily",      # 必需：报告类型
        "date": "2026-04-01"         # 可选：日期
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "报告查询成功",
    "data": {
        "report_type": "daily",
        "date": "2026-04-01",
        "content": {
            "pnl": 0.02,
            "positions": 5,
            "trades": 3,
            "risk_metrics": {
                "var": 0.05,
                "max_drawdown": 0.08
            }
        }
    }
}
```


## 五、P2模块工具接口规范

### 5.1 数据源工具（DataSourceTool）

**模块ID**: L11_TOOL_DATASOURCE_001
**优先级**: P2
**覆盖模块**: Layer 0 数据源层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **configure_qmt** | 配置QMT数据源 | account, password | 配置结果 |
| **configure_ifind** | 配置iFind数据源 | account, password | 配置结果 |
| **test_connection** | 测试数据源连接 | source | 连接状态 |
| **status** | 查询数据源状态 | 无 | 状态信息 |

#### 操作详细定义

##### 5.1.1 configure_qmt（配置QMT数据源）

**输入参数**：
```python
{
    "action": "configure_qmt",
    "params": {
        "account": "your_account",    # 必需：账号
        "password": "your_password",  # 必需：密码
        "server": "127.0.0.1"         # 可选：服务器地址
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "QMT数据源配置成功",
    "data": {
        "source": "QMT",
        "status": "connected",
        "configured_at": "2026-04-02T10:30:00Z"
    }
}
```

---

### 5.2 预处理工具（PreprocessingTool）

**模块ID**: L11_TOOL_PREPROCESSING_001
**优先级**: P2
**覆盖模块**: Layer 1 数据预处理层

#### 支持的操作

| 操作 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| **configure_cleaner** | 配置清洗规则 | rules | 配置结果 |
| **configure_normalizer** | 配置标准化方法 | method | 配置结果 |
| **validate** | 验证数据质量 | dataset | 验证结果 |

#### 操作详细定义

##### 5.2.1 configure_cleaner（配置清洗规则）

**输入参数**：
```python
{
    "action": "configure_cleaner",
    "params": {
        "rules": {                    # 必需：清洗规则
            "remove_outliers": True,
            "fill_missing": "mean",
            "remove_duplicates": True
        }
    }
}
```

**输出结果**：
```python
{
    "success": True,
    "message": "清洗规则配置成功",
    "data": {
        "rules": {
            "remove_outliers": True,
            "fill_missing": "mean",
            "remove_duplicates": True
        },
        "configured_at": "2026-04-02T10:30:00Z"
    }
}
```


## 六、工具调用示例

### 6.1 完整调用流程

```python
# 用户输入
user_input = "创建一个动量策略，持仓5天，止损10%"

# Layer 11处理流程
agent = QuantTradingAgent()
result = agent.chat(user_input)

# 内部流程
"""
1. AI理解意图: "配置策略"
2. AI提取参数: {strategy_type: "momentum", holding_period: 5, stop_loss: 0.1}
3. AI选择工具: "策略管理工具"
4. 调用工具: StrategyTool.execute({
       "action": "configure",
       "params": {
           "strategy_type": "momentum",
           "holding_period": 5,
           "stop_loss": 0.1
       }
   })
5. 工具执行: 策略引擎.configure_strategy(...) (无AI，直接执行)
6. AI格式化结果: "策略配置成功！策略ID: STRAT_20260402_001"
"""

print(result)
# 输出: "策略配置成功！策略ID: STRAT_20260402_001"
```

### 6.2 多步骤操作示例

```python
# 用户输入
user_input = "查询动量因子的表现，然后创建一个使用该因子的策略"

# Layer 11处理流程
"""
步骤1: 查询因子
- 意图: "查询因子"
- 参数: {factor_name: "momentum"}
- 调用: FactorTool.execute({"action": "query", "params": {"factor_name": "momentum"}})
- 结果: 因子IC=0.12，表现良好

步骤2: 创建策略
- 意图: "配置策略"
- 参数: {strategy_type: "momentum", factor: "momentum"}
- 调用: StrategyTool.execute({"action": "configure", "params": {...}})
- 结果: 策略ID: STRAT_20260402_001

AI格式化结果: "动量因子表现良好（IC=0.12），已创建策略STRAT_20260402_001"
"""
```


## 七、工具注册表

### 7.1 完整工具清单

| 工具名称 | 工具类 | 优先级 | 操作数量 | 状态 |
|---------|--------|--------|---------|------|
| 策略管理 | StrategyTool | P0 | 7个 | ✅ 已设计 |
| 因子管理 | FactorTool | P0 | 4个 | ✅ 已设计 |
| 风控管理 | RiskControlTool | P0 | 4个 | ✅ 已设计 |
| 授权确认 | ApprovalTool | P0 | 3个 | ✅ 已设计 |
| 舆情查询 | SentimentTool | P1 | 2个 | ✅ 已设计 |
| 模型训练 | MLTool | P1 | 2个 | ✅ 已设计 |
| 组合优化 | PortfolioTool | P1 | 3个 | ✅ 已设计 |
| 报告查询 | ReportTool | P1 | 2个 | ✅ 已设计 |
| 数据源管理 | DataSourceTool | P2 | 4个 | ✅ 已设计 |
| 数据预处理 | PreprocessingTool | P2 | 3个 | ✅ 已设计 |
| **总计** | - | - | **34个操作** | - |

### 7.2 优先级分布

| 优先级 | 工具数量 | 操作数量 | 占比 |
|--------|---------|---------|------|
| P0 | 4个 | 18个操作 | 53% |
| P1 | 4个 | 9个操作 | 26% |
| P2 | 2个 | 7个操作 | 21% |
| **总计** | **10个** | **34个操作** | **100%** |


## 八、实施路线图

### Phase 1：P0工具开发（Week 1-2）

**目标**: 完成P0工具开发

```yaml
工作内容:
  1. 策略工具开发（7个操作）
  2. 因子工具开发（4个操作）
  3. 风控工具开发（4个操作）
  4. 授权工具开发（3个操作）

交付物:
  - 4个工具文件
  - 18个操作实现
  - 单元测试
```

### Phase 2：P1工具开发（Week 3-4）

**目标**: 完成P1工具开发

```yaml
工作内容:
  1. 舆情工具开发（2个操作）
  2. ML工具开发（2个操作）
  3. 组合工具开发（3个操作）
  4. 报告工具开发（2个操作）

交付物:
  - 4个工具文件
  - 9个操作实现
  - 集成测试
```

### Phase 3：P2工具开发（Week 5-6）

**目标**: 完成P2工具开发

```yaml
工作内容:
  1. 数据源工具开发（4个操作）
  2. 预处理工具开发（3个操作）

交付物:
  - 2个工具文件
  - 7个操作实现
  - 完整测试套件
```


## 九、关键洞察

### 9.1 细化层次总结

| 层级 | 需要细化 | 不需要细化 |
|------|---------|-----------|
| **Layer 11** | ✅ 意图识别、参数提取、工具路由 | - |
| **各模块** | ✅ 工具接口规范（操作、参数、返回值） | ❌ 文字交付设计 |

### 9.2 核心优势

| 优势 | 说明 |
|------|------|
| **避免重复** | 不需要为每个模块单独做文字交付设计 |
| **统一标准** | 所有工具遵循统一的接口规范 |
| **易于扩展** | 新增模块只需定义工具接口 |
| **维护简单** | 只需维护Layer 11的意图识别逻辑 |

### 9.3 与另一个AI方案的对比

| 对比项 | 另一个AI方案 | 本方案 | 优势 |
|--------|-------------|--------|------|
| **细化方式** | 每个模块单独做文字交付设计 | Layer 11统一意图识别 + 工具接口规范 | ✅ 避免重复 |
| **AI层数量** | 29个AI层 | 1个AI层 | ✅ 减少96.6% |
| **维护成本** | 高（29套逻辑） | 低（统一标准） | ✅ 显著降低 |
| **扩展性** | 差（新增模块需新增AI层） | 好（新增工具接口即可） | ✅ 显著提升 |


## 十、相关文档索引

### 10.1 核心参考文档

| 文档名称 | 路径 | 说明 |
|---------|------|------|
| [Layer 11工具封装蓝图](./LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md` | 工具封装架构 |
| [Layer 11架构蓝图](./LAYER_11_ARCHITECTURE.md) | `docs/module_designs/layer_11/LAYER_11_ARCHITECTURE.md` | Layer 11整体架构 |
| [文字驱动核心模块](./L11_TEXT_DRIVER.md) | `docs/module_designs/layer_11/L11_TEXT_DRIVER.md` | NLU设计 |
| [量化交易Agent模块](./L11_QUANT_AGENT.md) | `docs/module_designs/layer_11/L11_QUANT_AGENT.md` | Agent框架 |

### 10.2 代码实现位置

| 模块 | 路径 | 说明 |
|------|------|------|
| 工具基类 | `src/layer_11/tools/base_tool.py` | 工具基类定义 |
| 策略工具 | `src/layer_11/tools/strategy_tool.py` | 策略工具实现 |
| 因子工具 | `src/layer_11/tools/factor_tool.py` | 因子工具实现 |
| 风控工具 | `src/layer_11/tools/risk_control_tool.py` | 风控工具实现 |
| 工具注册中心 | `src/layer_11/tools/__init__.py` | 工具注册管理 |

---

**文档版本**: v1.0.0
**最后更新**: 2026-04-02
**维护者**: 首席蓝图架构师
