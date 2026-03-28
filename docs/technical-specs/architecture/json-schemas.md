# JSON Schemas

> 清风量化多策略系统的标准化JSON输出Schema
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 全成本模型：[modules/cost-model.md](./modules/cost-model.md)
> - Barra优化器：[architecture/barra-optimizer.md](./architecture/barra-optimizer.md)

***

## 1. 通用响应包装

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "timestamp", "layer", "status", "data"],
  "properties": {
    "version": {
      "type": "string",
      "description": "协议版本",
      "example": "1.0"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "输出时间戳"
    },
    "layer": {
      "type": "string",
      "enum": ["pre_market", "alpha", "risk", "portfolio", "execution", "monitor", "attribution"],
      "description": "层级标识"
    },
    "status": {
      "type": "string",
      "enum": ["success", "warning", "error"],
      "description": "执行状态"
    },
    "error": {
      "type": "object",
      "description": "错误信息（当status为error时）",
      "properties": {
        "code": {"type": "integer"},
        "message": {"type": "string"}
      }
    },
    "data": {
      "type": "object",
      "description": "业务数据负载"
    }
  }
}
```

***

## 2. 前置层输出Schema

```json
{
  "前置层输出": {
    "version": "string",
    "timestamp": "string",
    "market_state_prob": {
      "P_牛市": "number (0-1)",
      "P_震荡": "number (0-1)",
      "P_熊市": "number (0-1)",
      "P_混沌": "number (0-1)"
    },
    "confidence": "number (0-1)",
    "market_state": "string (牛市|震荡|熊市|混沌)",
    "dimension_scores": {
      "技术面": "number (0-1)",
      "资金面": "number (0-1)",
      "情绪面": "number (0-1)",
      "风格面": "number (0-1)",
      "全球面": "number (0-1)"
    },
    "liquidity_state": "string (高|正常|低)",
    "risk_level": "string (高|中|低)",
    "recommended_position": "number (0-1)"
  }
}
```

***

## 3. 风险模型输出Schema

```json
{
  "风险模型输出": {
    "systematic_risk": {
      "portfolio_beta": "number",
      "portfolio_volatility": "number",
      "VaR_95": "number",
      "CVaR_95": "number"
    },
    "non_systematic_risk": {
      "max_single_stock_exposure": "number",
      "max_sector_exposure": "number",
      "position_correlation": "number"
    },
    "stress_test": {
      "scenario_market_minus_5pct": "number",
      "scenario_market_minus_10pct": "number"
    },
    "risk_warnings": ["string"]
  }
}
```

***

## 4. 组合优化输出Schema

```json
{
  "组合优化输出": {
    "target_positions": [
      {
        "code": "string",
        "weight": "number",
        "shares": "integer",
        "entry_price": "number",
        "target_price": "number",
        "stop_loss": "number"
      }
    ],
    "order_list": [
      {
        "code": "string",
        "direction": "string (buy|sell)",
        "volume": "integer",
        "price_type": "string (market|limit)",
        "limit_price": "number (optional)"
      }
    ],
    "expected_return": "number",
    "expected_volatility": "number",
    "expected_sharpe": "number"
  }
}
```

***

## 5. 执行层输出Schema

```json
{
  "执行层输出": {
    "orders": [
      {
        "order_id": "string",
        "code": "string",
        "direction": "string",
        "volume": "integer",
        "price": "number",
        "status": "string (pending|filled|cancelled|rejected)",
        "filled_volume": "integer",
        "filled_price": "number",
        "fill_time": "string (optional)"
      }
    ],
    "execution_summary": {
      "total_orders": "integer",
      "filled_orders": "integer",
      "cancelled_orders": "integer",
      "total_cost": "number",
      "avg_slippage": "number"
    }
  }
}
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录I内容 |
