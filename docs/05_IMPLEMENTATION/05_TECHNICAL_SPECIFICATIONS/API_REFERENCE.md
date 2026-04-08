---
module_id: LAYER7_API_REFERENCE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: '2026-04-07'
owner: 首席技术评审官
responsibility:
- 系统实施与部署管理与优化维护
standard_type: API接口文档
applicable_scope: Layer 7 AI报告层
compliance_level: 专业标准
---
---


# Layer 7 AI报告层 - 统一API接口文档
> **核心职责**: 分析报告和评估结果
> **职责边界**: 
> - ✅ 本文档负责：分析报告和评估结果相关内容
> - ❌ 本文档不负责：其他模块内容


**文档ID**: LAYER7_API_REFERENCE_001
**版本**: v1.0.0
**创建日期**: 2026-04-02
**适用范围**: Layer 7所有报告模?所有报告模块
---

## 一、API概览

### 1.1 基础信息

- **基础URL**: `http://localhost:8000/api/v1/reports/`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: JWT Bearer Token

### 1.2 认证机制

**获取Token**:
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**使用Token**:
```http
GET /api/v1/reports/realtime-risk/current
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1.3 通用响应格式

**成功响应**:
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2026-04-02T10:30:00Z",
  "request_id": "req_123456"
}
```

**错误响应**:
```json
{
  "status": "error",
  "error_code": "INVALID_PARAMETER",
  "error_message": "Invalid scenario_type parameter",
  "timestamp": "2026-04-02T10:30:00Z",
  "request_id": "req_123456"
}
```

### 1.4 错误码定?
| 错误?| HTTP状态码 | 描述 |
|--------|-----------|------|
| INVALID_PARAMETER | 400 | 参数错误 |
| UNAUTHORIZED | 401 | 未授?|
| FORBIDDEN | 403 | 无权限|
| NOT_FOUND | 404 | 资源不存?|
| INTERNAL_ERROR | 500 | 内部错误 |

---

## 二、情景分析API

### 2.1 执行情景分析

**接口**: `POST /api/v1/reports/scenario/analyze`

**描述**: 分析特定情景下的投资组合表现

**请求参数**:

| 参数据| 类型 | 必填 | 描述 |
|--------|------|------|------|
| portfolio_id | string | ?| 投资组合ID |
| scenario_type | string | ?| 情景类型（见情景类型表） |
| custom_shock | object | ?| 自定义冲击参?|
| output_format | string | ?| 输出格式（json/markdown/pdf），默认json |

**情景类型?*:

| 情景类型 | 描述 | 默认冲击参数 |
|---------|------|-------------|
| market_crash | 市场崩盘 | equity: -20%, vol: +50% |
| rate_hike | 加息周期 | bond: -5%, equity: -10% |
| liquidity_crisis | 流动性危?| spread: +100%, vol: +30% |
| sector_rotation | 行业轮动 | sector_shift: 15% |
| currency_crisis | 货币危机 | fx: 10%, equity: -15% |
| commodity_shock | 商品冲击 | commodity: 20% |
| credit_crisis | 信用危机 | credit_spread: +200bp |
| custom | 自定?| 需提供custom_shock |

**请求示例**:
```json
{
  "portfolio_id": "PORTFOLIO_001",
  "scenario_type": "market_crash",
  "output_format": "json"
}
```

**响应示例**:
```json
{
  "status": "success",
  "report_id": "SCENARIO_RPT_20260402_000001",
  "timestamp": "2026-04-02T10:30:00Z",
  "scenario_result": {
    "scenario_name": "市场崩盘情景",
    "portfolio_impact": -0.152,
    "var_increase": 0.085,
    "max_drawdown": 0.220,
    "risk_metrics": {
      "pre_scenario_var": 0.05,
      "post_scenario_var": 0.135,
      "expected_shortfall": 0.180
    },
    "sensitivity_analysis": {
      "equity_sensitivity": 0.85,
      "bond_sensitivity": 0.15,
      "volatility_sensitivity": 0.30
    },
    "sector_impacts": {
      "科技": -0.25,
      "金融": -0.18,
      "消费": -0.12
    }
  }
}
```

### 2.2 获取情景列表

**接口**: `GET /api/v1/reports/scenario/list`

**描述**: 获取所有可用的情景类型

**响应示例**:
```json
{
  "status": "success",
  "scenarios": [
    {
      "scenario_type": "market_crash",
      "name": "市场崩盘",
      "description": "模拟2008年金融危机级别的市场崩盘",
      "default_shock": {
        "equity_shock": -0.20,
        "volatility_shock": 0.50
      }
    },
    ...
  ]
}
```

---

## 三、压力测试API

### 3.1 执行压力测试

**接口**: `POST /api/v1/reports/stress-test/run`

**描述**: 执行压力测试并生成报告
**请求参数**:

| 参数据| 类型 | 必填 | 描述 |
|--------|------|------|------|
| portfolio_id | string | ?| 投资组合ID |
| test_type | string | ?| 测试类型（historical/hypothetical/reverse/comprehensive?|
| scenarios | array | ?| 指定测试情景列表 |
| output_format | string | ?| 输出格式，默认json |

**测试类型说明**:

| 测试类型 | 描述 | 适用场景 |
|---------|------|---------|
| historical | 历史情景测试 | 使用历史危机数据 |
| hypothetical | 假设情景测试 | 自定义极端情?|
| reverse | 反向压力测试 | 寻找导致破产的情?|
| comprehensive | 综合测试 | 执行所有类型测试|

**请求示例**:
```json
{
  "portfolio_id": "PORTFOLIO_001",
  "test_type": "comprehensive",
  "scenarios": ["2008_financial_crisis", "2020_covid_crash"]
}
```

**响应示例**:
```json
{
  "status": "success",
  "report_id": "STRESS_RPT_20260402_000001",
  "timestamp": "2026-04-02T10:35:00Z",
  "test_summary": {
    "total_scenarios": 8,
    "survived_count": 7,
    "failed_count": 1
  },
  "test_results": [
    {
      "scenario_name": "2008金融危机",
      "scenario_type": "historical",
      "portfolio_loss": -0.35,
      "max_drawdown": 0.42,
      "recovery_days": 180,
      "survival_assessment": "survived",
      "risk_breaches": [
        {
          "metric": "VaR",
          "threshold": 0.10,
          "actual": 0.15,
          "breach_duration_days": 30
        }
      ]
    },
    {
      "scenario_name": "极端流动性危?,
      "scenario_type": "hypothetical",
      "portfolio_loss": -0.55,
      "survival_assessment": "failed",
      "failure_reason": "流动性枯竭导致无法平?
    }
  ],
  "recommendations": [
    "增加流动性储备至15%",
    "降低单一资产集中度至8%以下"
  ]
}
```

### 3.2 获取历史情景?
**接口**: `GET /api/v1/reports/stress-test/historical-scenarios`

**描述**: 获取可用的历史压力情?
**响应示例**:
```json
{
  "status": "success",
  "scenarios": [
    {
      "scenario_id": "2008_financial_crisis",
      "name": "2008年全球金融危?,
      "start_date": "2008-09-01",
      "end_date": "2009-03-01",
      "key_events": ["雷曼兄弟破产", "AIG救助", "量化宽松"],
      "market_impact": {
        "sp500_return": -0.52,
        "volatility_spike": 3.5
      }
    },
    ...
  ]
}
```

---

## 四、实时风险监控API

### 4.1 获取当前风险指标

**接口**: `GET /api/v1/reports/realtime-risk/current`

**描述**: 获取实时风险监控指标

**响应示例**:
```json
{
  "status": "success",
  "timestamp": "2026-04-02T10:40:00Z",
  "portfolio_id": "PORTFOLIO_001",
  "risk_metrics": {
    "var_95": 0.052,
    "var_99": 0.078,
    "cvar_95": 0.068,
    "max_drawdown": 0.125,
    "current_drawdown": 0.082,
    "volatility": 0.185,
    "sharpe_ratio": 1.45,
    "beta": 0.92,
    "liquidity_score": 85,
    "concentration_score": 75
  },
  "greeks": {
    "delta": 0.85,
    "gamma": 0.02,
    "vega": 0.15,
    "theta": -0.005
  },
  "alerts": [
    {
      "alert_id": "ALERT_001",
      "severity": "warning",
      "metric": "VaR_95",
      "threshold": 0.05,
      "actual": 0.052,
      "message": "VaR超过阈?%",
      "timestamp": "2026-04-02T10:39:30Z"
    }
  ],
  "trend": {
    "var_trend": "increasing",
    "volatility_trend": "stable",
    "liquidity_trend": "decreasing"
  }
}
```

### 4.2 订阅实时风险推?
**接口**: `WebSocket /api/v1/reports/realtime-risk/stream`

**描述**: WebSocket实时推送风险指?
**连接示例**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/reports/realtime-risk/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Risk update:', data);
};
```

**推送消息格?*:
```json
{
  "type": "risk_update",
  "timestamp": "2026-04-02T10:40:01Z",
  "risk_metrics": {
    "var_95": 0.051,
    "volatility": 0.184
  },
  "alert": null
}
```

### 4.3 获取历史风险曲线

**接口**: `GET /api/v1/reports/realtime-risk/history`

**请求参数**:

| 参数据| 类型 | 必填 | 描述 |
|--------|------|------|------|
| portfolio_id | string | ?| 投资组合ID |
| start_date | string | ?| 开始日期（YYYY-MM-DD?|
| end_date | string | ?| 结束日期（YYYY-MM-DD?|
| metrics | array | ?| 指标列表，默认全?|

**响应示例**:
```json
{
  "status": "success",
  "data_points": [
    {
      "timestamp": "2026-04-01T09:30:00Z",
      "var_95": 0.048,
      "volatility": 0.180
    },
    {
      "timestamp": "2026-04-01T10:00:00Z",
      "var_95": 0.050,
      "volatility": 0.182
    },
    ...
  ]
}
```

---

## 五、多时间框架融合API

### 5.1 生成融合报告

**接口**: `POST /api/v1/reports/multi-timeframe/fuse`

**描述**: 融合宏观/中观/微观三层报告

**请求参数**:

| 参数据| 类型 | 必填 | 描述 |
|--------|------|------|------|
| macro_report_id | string | ?| 宏观报告ID |
| strategy_report_id | string | ?| 策略报告ID |
| execution_report_id | string | ?| 执行报告ID |
| output_format | string | ?| 输出格式，默认json |

**响应示例**:
```json
{
  "status": "success",
  "report_id": "FUSED_RPT_20260402_000001",
  "timestamp": "2026-04-02T10:45:00Z",
  "consistency_analysis": {
    "consistency_score": 85.5,
    "alignment_issues": [
      {
        "issue": "宏观层经济范式为扩张期，但策略层使用防御性策?,
        "severity": "medium",
        "recommendation": "考虑增加周期性策略权?
      }
    ]
  },
  "cross_timeframe_risks": [
    {
      "risk": "宏观层通胀风险上升，策略层通胀敏感资产权重较高",
      "severity": "high",
      "affected_layers": ["macro", "strategy"]
    }
  ],
  "optimization_opportunities": [
    {
      "opportunity": "执行层滑点较高，建议优化交易时机",
      "potential_improvement": "降低执行成本?5%"
    }
  ],
  "action_items": [
    {
      "priority": "high",
      "action": "降低通胀敏感资产权重",
      "deadline": "2026-04-05"
    }
  ]
}
```

### 5.2 获取各层报告

**接口**: `GET /api/v1/reports/multi-timeframe/layer/{layer_type}`

**描述**: 获取指定时间框架层的报告

**路径参数**:

| 参数据| 类型 | 描述 |
|--------|------|------|
| layer_type | string | 层类型（macro/strategy/execution?|

**响应示例**:
```json
{
  "status": "success",
  "layer_type": "macro",
  "report": {
    "economic_regime": "expansion",
    "regime_confidence": 0.75,
    "strategic_allocation": {
      "equity": 0.60,
      "bond": 0.30,
      "commodity": 0.10
    },
    "quarterly_return": 0.05,
    "rebalance_signals": ["增加股票配置"]
  }
}
```

---

## 六、策略生命周期API

### 6.1 生成生命周期报告

**接口**: `GET /api/v1/reports/strategy-lifecycle/report`

**描述**: 生成策略生命周期报告

**响应示例**:
```json
{
  "status": "success",
  "report_id": "LIFECYCLE_RPT_20260402_000001",
  "timestamp": "2026-04-02T11:00:00Z",
  "strategy_summary": {
    "total_strategies": 12,
    "active": 8,
    "warning": 3,
    "critical": 1,
    "retired": 0
  },
  "phase_distribution": {
    "emerging": 2,
    "growing": 3,
    "mature": 4,
    "declining": 2,
    "retired": 1
  },
  "performance_summary": {
    "avg_sharpe": 1.35,
    "avg_return": 0.18,
    "avg_ic": 0.045
  },
  "strategy_details": [
    {
      "strategy_id": "STRAT_001",
      "strategy_name": "价值策?,
      "current_phase": "mature",
      "status": "active",
      "sharpe_ratio": 1.8,
      "trading_days": 250,
      "recommendation": "继续运行"
    },
    {
      "strategy_id": "STRAT_002",
      "strategy_name": "动量策略",
      "current_phase": "declining",
      "status": "warning",
      "sharpe_ratio": 0.3,
      "trading_days": 180,
      "recommendation": "考虑退役或优化"
    }
  ],
  "recommendations": [
    "动量策略性能下降，建议评估是否退?,
    "新兴策略数量较少，建议开发新策略"
  ]
}
```

### 6.2 更新策略状态
**接口**: `PUT /api/v1/reports/strategy-lifecycle/strategy/{strategy_id}`

**描述**: 更新策略状态
**请求示例**:
```json
{
  "status": "retired",
  "retirement_reason": "性能持续下降",
  "retirement_date": "2026-04-02"
}
```

---

## 七、监管合规API

### 7.1 生成合规报告

**接口**: `POST /api/v1/reports/regulatory/compliance`

**描述**: 生成监管合规报告

**请求参数**:

| 参数据| 类型 | 必填 | 描述 |
|--------|------|------|------|
| portfolio_id | string | ?| 投资组合ID |
| reporting_period | string | ?| 报告期间 |
| report_type | string | ?| 报告类型（quarterly/annual?|

**响应示例**:
```json
{
  "status": "success",
  "report_id": "REG_RPT_20260402_000001",
  "timestamp": "2026-04-02T11:05:00Z",
  "fund_info": {
    "fund_name": "清风量化基金",
    "fund_size": 50000000,
    "reporting_period": "2026年第一季度"
  },
  "compliance_status": "compliant",
  "compliance_checks": [
    {
      "check_name": "单股权重限制",
      "requirement": "?0%",
      "actual": "8.5%",
      "status": "compliant"
    },
    {
      "check_name": "行业权重限制",
      "requirement": "?0%",
      "actual": "25%",
      "status": "compliant"
    },
    {
      "check_name": "现金最低要?,
      "requirement": "?%",
      "actual": "6%",
      "status": "compliant"
    }
  ],
  "violations": [],
  "corrective_actions": []
}
```

### 7.2 获取合规检查规范
**接口**: `GET /api/v1/reports/regulatory/rules`

**描述**: 获取所有合规检查规范
**响应示例**:
```json
{
  "status": "success",
  "rules": [
    {
      "rule_id": "RULE_001",
      "rule_name": "单股权重限制",
      "requirement": "单股权重?0%",
      "regulation_source": "证监会私募基金管理办法第15?
    },
    ...
  ]
}
```

---

## 八、AI可解释性API

### 8.1 生成可解释性报告
**接口**: `POST /api/v1/reports/ai-explainability/analyze`

**描述**: 生成AI决策可解释性报告
**请求参数**:

| 参数据| 类型 | 必填 | 描述 |
|--------|------|------|------|
| model_id | string | ?| 模型ID |
| sample_ids | array | ?| 样本ID列表，默认分析全?|
| explanation_method | string | ?| 解释方法（shap/lime），默认shap |

**响应示例**:
```json
{
  "status": "success",
  "report_id": "EXPLAIN_RPT_20260402_000001",
  "timestamp": "2026-04-02T11:10:00Z",
  "model_info": {
    "model_name": "Alpha预测模型",
    "model_type": "XGBoost"
  },
  "global_feature_importance": [
    {
      "feature_name": "PE_ratio",
      "importance_score": 0.25,
      "contribution_direction": "negative",
      "description": "PE比率与预测收益负相关"
    },
    {
      "feature_name": "momentum",
      "importance_score": 0.20,
      "contribution_direction": "positive",
      "description": "动量因子正向贡献"
    }
  ],
  "model_transparency_score": 85.0,
  "interpretability_score": 82.5
}
```

### 8.2 获取单样本解释
**接口**: `GET /api/v1/reports/ai-explainability/sample/{sample_id}`

**描述**: 获取单个样本的决策解释
**响应示例**:
```json
{
  "status": "success",
  "sample_id": "SAMPLE_001",
  "decision_output": 0.85,
  "decision_type": "买入信号",
  "confidence": 0.92,
  "decision_path": [
    "PE_ratio负向贡献（?25.3?,
    "momentum正向贡献（?0.15?,
    "ROE正向贡献（?18.5%?,
    "最终决? 买入信号"
  ],
  "alternative_scenarios": [
    {
      "scenario": "市场下跌",
      "output_change": -0.15
    }
  ]
}
```

---

## 九、执行成本API

### 9.1 生成成本分析报告

**接口**: `POST /api/v1/reports/execution-cost/analyze`

**描述**: 生成执行成本分析报告

**请求参数**:

| 参数据| 类型 | 必填 | 描述 |
|--------|------|------|------|
| portfolio_id | string | ?| 投资组合ID |
| start_date | string | ?| 开始日?|
| end_date | string | ?| 结束日期 |

**响应示例**:
```json
{
  "status": "success",
  "report_id": "EXEC_COST_RPT_20260402_000001",
  "timestamp": "2026-04-02T11:15:00Z",
  "reporting_period": "2026年第一季度",
  "execution_metrics": {
    "total_trades": 1250,
    "total_volume": 5000000,
    "total_value": 850000000,
    "avg_slippage": 0.0008,
    "max_slippage": 0.0035,
    "avg_market_impact": 0.0012,
    "avg_fill_rate": 0.96,
    "execution_efficiency": 0.92,
    "total_cost": 850000,
    "cost_per_share": 0.17
  },
  "cost_breakdown": {
    "slippage_cost": 340000,
    "market_impact_cost": 255000,
    "commission_cost": 170000,
    "spread_cost": 85000
  },
  "optimization_opportunities": [
    {
      "opportunity": "优化大单执行算法",
      "potential_saving": 50000
    }
  ]
}
```

### 9.2 获取交易执行详情

**接口**: `GET /api/v1/reports/execution-cost/trade/{trade_id}`

**描述**: 获取单笔交易执行详情

**响应示例**:
```json
{
  "status": "success",
  "trade_id": "TRADE_001",
  "symbol": "600519.SH",
  "side": "buy",
  "order_size": 10000,
  "executed_size": 9500,
  "order_price": 1800.00,
  "executed_price": 1805.00,
  "slippage": 0.0028,
  "fill_rate": 0.95,
  "market_impact": 0.0015,
  "execution_time": "2026-04-02T09:35:00Z",
  "execution_algorithm": "VWAP"
}
```

---

## 十、通用接口

### 10.1 获取报告列表

**接口**: `GET /api/v1/reports/list`

**请求参数**:

| 参数据| 类型 | 必填 | 描述 |
|--------|------|------|------|
| report_type | string | ?| 报告类型 |
| start_date | string | ?| 开始日?|
| end_date | string | ?| 结束日期 |
| limit | int | ?| 返回数量，默?0 |

### 10.2 下载报告

**接口**: `GET /api/v1/reports/{report_id}/download`

**请求参数**:

| 参数据| 类型 | 必填 | 描述 |
|--------|------|------|------|
| format | string | ?| 下载格式（json/pdf/markdown?|

### 10.3 删除报告

**接口**: `DELETE /api/v1/reports/{report_id}`

---

## 十一、SDK使用示例

### 11.1 Python SDK

```python
from zephyr_alpha.reports import ReportClient

client = ReportClient(
    base_url="http://localhost:8000/api/v1",
    token="your_jwt_token"
)

scenario_result = client.scenario.analyze(
    portfolio_id="PORTFOLIO_001",
    scenario_type="market_crash"
)
print(f"组合影响: {scenario_result['portfolio_impact']:.2%}")

stress_result = client.stress_test.run(
    portfolio_id="PORTFOLIO_001",
    test_type="comprehensive"
)
print(f"存活? {stress_result['test_summary']['survived_count']}/{stress_result['test_summary']['total_scenarios']}")

risk_metrics = client.realtime_risk.get_current()
print(f"当前VaR(95%): {risk_metrics['risk_metrics']['var_95']:.2%}")
```

### 11.2 JavaScript SDK

```javascript
const { ReportClient } = require('@zephyr-alpha/reports');

const client = new ReportClient({
  baseUrl: 'http://localhost:8000/api/v1',
  token: 'your_jwt_token'
});

const scenarioResult = await client.scenario.analyze({
  portfolio_id: 'PORTFOLIO_001',
  scenario_type: 'market_crash'
});
console.log(`组合影响: ${(scenarioResult.portfolio_impact * 100).toFixed(2)}%`);

const ws = client.realtimeRiske.subscribe((data) => {
  console.log('风险更新:', data.risk_metrics.var_95);
});
```

---

## 十二、最佳实现
### 12.1 性能优化建议

1. **批量请求**: 使用批量接口减少网络开销
2. **缓存利用**: 合理使用ETag和If-None-Match?3. **异步处理**: 长时间报告生成使用异步接?4. **WebSocket**: 实时数据优先使用WebSocket

### 12.2 错误处理建议

```python
try:
    result = client.scenario.analyze(...)
except ValidationError as e:
    print(f"参数错误: {e.message}")
except AuthenticationError as e:
    print(f"认证失败: {e.message}")
except RateLimitError as e:
    print(f"请求频率超限，请{e.retry_after}秒后重试")
except APIError as e:
    print(f"API错误: {e.message}")
```

### 12.3 安全建议

1. **Token管理**: 定期刷新Token，避免长期有?2. **HTTPS**: 生产环境强制使用HTTPS
3. **IP白名?*: 限制API访问IP范围
4. **日志审计**: 记录所有API调用日志

---

**文档版本**: v1.0.0
**最后更?*: 2026-04-02
**维护?*: Layer 7 AI报告层团?
