# 接口请求/响应示例补充文档

> **版本**: v1.0
> **创建日期**: 2026-04-02
> **目的**: 为所有新建模块补充详细的接口请求/响应示例

---

## 一、合规监控模块接口示例

### 1.1 check_trading_compliance (交易合规检查)

**请求示例**:
```json
{
    "order_id": "order_20260402_001",
    "symbol": "000001.SZ",
    "direction": "buy",
    "volume": 10000,
    "price": 15.50,
    "order_type": "limit",
    "account_id": "account_001"
}
```

**成功响应示例**:
```json
{
    "check_id": "check_20260402_001",
    "check_result": "pass",
    "violations": [],
    "action_taken": "approved",
    "check_time": "2026-04-02 10:30:00",
    "reviewer": "AI"
}
```

**失败响应示例**:
```json
{
    "check_id": "check_20260402_002",
    "check_result": "fail",
    "violations": [
        {
            "type": "volume_limit_exceeded",
            "details": "交易量超过限制: 150000 > 100000"
        }
    ],
    "action_taken": "blocked",
    "check_time": "2026-04-02 10:31:00",
    "reviewer": "AI"
}
```

### 1.2 check_risk_compliance (风控合规检查)

**请求示例**:
```json
{
    "position": {
        "position_id": "pos_001",
        "symbol": "000001.SZ",
        "value": 950000.0,
        "unrealized_pnl": 50000.0
    },
    "risk_limits": {
        "position_limit": 1000000.0,
        "loss_limit": -100000.0,
        "var_limit": -20000.0
    }
}
```

**成功响应示例**:
```json
{
    "check_result": "pass",
    "violations": [],
    "utilization_rate": 0.95,
    "status": "normal",
    "check_time": "2026-04-02 10:30:00"
}
```

**警告响应示例**:
```json
{
    "check_result": "pass",
    "violations": [],
    "utilization_rate": 0.92,
    "status": "warning",
    "check_time": "2026-04-02 10:30:00"
}
```

**失败响应示例**:
```json
{
    "check_result": "fail",
    "violations": [
        {
            "type": "position_limit_exceeded",
            "details": "持仓超过限额: 1050000 > 1000000"
        }
    ],
    "utilization_rate": 1.05,
    "status": "breach",
    "check_time": "2026-04-02 10:31:00"
}
```

### 1.3 generate_regulatory_report (监管报告生成)

**请求示例**:
```json
{
    "report_type": "daily_report",
    "period": {
        "start_date": "2026-04-01",
        "end_date": "2026-04-01"
    }
}
```

**响应示例**:
```json
{
    "report_id": "report_20260402_001",
    "report_type": "daily_report",
    "compliance_status": "compliant",
    "violations_count": 0,
    "report_content": "# 监管合规报告\n\n**报告类型**: daily_report\n...",
    "generated_at": "2026-04-02 18:00:00"
}
```

### 1.4 record_audit_trail (审计追踪记录)

**请求示例**:
```json
{
    "event_type": "compliance_check",
    "user_id": "user_001",
    "action": "check_trading_compliance",
    "details": {
        "order_id": "order_20260402_001",
        "check_result": "pass"
    },
    "result": "success",
    "ip_address": "192.168.1.1"
}
```

**响应示例**:
```json
{
    "audit_id": "audit_20260402_001",
    "status": "recorded",
    "recorded_at": "2026-04-02 10:30:00"
}
```

### 1.5 alert_compliance_violation (合规预警)

**请求示例**:
```json
{
    "check_id": "check_20260402_002",
    "violations": [
        {
            "type": "volume_limit_exceeded",
            "details": "交易量超过限制: 150000 > 100000"
        }
    ]
}
```

**响应示例**:
```json
{
    "alert_sent": true,
    "alert_channels": ["system", "email"],
    "sent_at": "2026-04-02 10:31:00"
}
```

---

## 二、实盘监控模块接口示例

### 2.1 monitor_realtime_trading (实时交易监控)

**请求示例**:
```json
{
    "order_count": 15,
    "volume": 500000,
    "turnover": 7750000.0,
    "timestamp": "2026-04-02 10:30:00"
}
```

**正常响应示例**:
```json
{
    "monitor_id": "monitor_20260402_001",
    "status": "normal",
    "alerts": [],
    "monitor_time": "2026-04-02 10:30:00"
}
```

**警告响应示例**:
```json
{
    "monitor_id": "monitor_20260402_002",
    "status": "warning",
    "alerts": [
        {
            "type": "high_frequency",
            "severity": "warning",
            "message": "订单频率过高: 120"
        }
    ],
    "monitor_time": "2026-04-02 10:31:00"
}
```

### 2.2 monitor_position_risk (持仓风险监控)

**请求示例**:
```json
{
    "position_data": {
        "position_id": "pos_001",
        "symbol": "000001.SZ",
        "value": 1000000.0,
        "unrealized_pnl": 50000.0
    },
    "market_data": {
        "current_price": 15.50,
        "change_percent": 0.02
    }
}
```

**响应示例**:
```json
{
    "risk_id": "risk_20260402_001",
    "risk_exposure": 0.05,
    "var_value": -20000.0,
    "risk_status": "normal",
    "monitor_time": "2026-04-02 10:30:00"
}
```

### 2.3 detect_anomaly (异常交易检测)

**请求示例**:
```json
{
    "order_amount": 1500000,
    "order_frequency": 60,
    "price_deviation": 0.05,
    "volume_deviation": 0.10
}
```

**无异常响应示例**:
```json
{
    "alert_id": "alert_20260402_001",
    "anomalies": [],
    "has_anomaly": false,
    "detect_time": "2026-04-02 10:30:00"
}
```

**有异常响应示例**:
```json
{
    "alert_id": "alert_20260402_002",
    "anomalies": [
        {
            "type": "abnormal_order",
            "severity": "high",
            "description": "订单金额异常大: 1500000"
        },
        {
            "type": "high_frequency",
            "severity": "medium",
            "description": "订单频率异常高: 60"
        }
    ],
    "has_anomaly": true,
    "detect_time": "2026-04-02 10:31:00"
}
```

### 2.4 collect_performance_metrics (性能指标收集)

**请求示例**:
```json
{
    "latency_ms": 15.5,
    "throughput": 1000,
    "cpu_usage": 0.45,
    "memory_usage": 0.60,
    "timestamp": "2026-04-02 10:30:00"
}
```

**响应示例**:
```json
{
    "metric_id": "metric_20260402_001",
    "latency_ms": 15.5,
    "throughput": 1000,
    "cpu_usage": 0.45,
    "memory_usage": 0.60,
    "collected_at": "2026-04-02 10:30:00"
}
```

### 2.5 send_multi_channel_alert (多渠道告警)

**请求示例**:
```json
{
    "alert_id": "alert_20260402_002",
    "anomalies": [
        {
            "type": "abnormal_order",
            "severity": "high",
            "description": "订单金额异常大: 1500000"
        }
    ]
}
```

**响应示例**:
```json
{
    "alert_sent": true,
    "channels": ["system", "email", "sms"],
    "sent_at": "2026-04-02 10:31:00"
}
```

---

## 三、性能分析模块接口示例

### 3.1 collect_metrics (性能指标采集)

**请求示例**:
```json
{
    "module_name": "factor_calculator"
}
```

**响应示例**:
```json
{
    "cpu_usage": 0.45,
    "memory_usage": 0.60,
    "timestamp": "2026-04-02 10:30:00"
}
```

### 3.2 detect_bottlenecks (性能瓶颈识别)

**请求示例**:
```json
{
    "cpu_usage": 0.85,
    "memory_usage": 0.75,
    "io_wait": 0.20,
    "network_latency": 50
}
```

**无瓶颈响应示例**:
```json
{
    "bottlenecks": [],
    "analysis_time": "2026-04-02 10:30:00"
}
```

**有瓶颈响应示例**:
```json
{
    "bottlenecks": [
        {
            "type": "cpu_bottleneck",
            "severity": "critical",
            "description": "CPU使用率过高: 85%",
            "impact_score": 0.85
        },
        {
            "type": "memory_bottleneck",
            "severity": "high",
            "description": "内存使用率过高: 75%",
            "impact_score": 0.75
        }
    ],
    "analysis_time": "2026-04-02 10:31:00"
}
```

### 3.3 generate_performance_report (性能报告生成)

**请求示例**:
```json
{
    "avg_cpu_usage": 0.45,
    "avg_memory_usage": 0.60,
    "bottlenecks_count": 3,
    "bottlenecks": [
        {
            "type": "cpu_bottleneck",
            "severity": "high",
            "description": "CPU使用率过高"
        }
    ],
    "suggestions": [
        {
            "type": "code_optimization",
            "description": "优化CPU密集型操作",
            "priority": "high"
        }
    ]
}
```

**响应示例**:
```json
{
    "report_id": "report_20260402_001",
    "report_content": "# 性能分析报告\n\n**报告ID**: report_20260402_001\n...",
    "generated_at": "2026-04-02 18:00:00"
}
```

### 3.4 generate_optimization_suggestions (优化建议生成)

**请求示例**:
```json
[
    {
        "type": "cpu_bottleneck",
        "severity": "high",
        "description": "CPU使用率过高: 85%",
        "impact_score": 0.85
    }
]
```

**响应示例**:
```json
[
    {
        "type": "code_optimization",
        "description": "优化CPU密集型操作,考虑使用多进程或异步处理",
        "priority": "high",
        "estimated_improvement": 0.30
    }
]
```

### 3.5 analyze_trend (性能趋势分析)

**请求示例**:
```json
[
    {
        "cpu_usage": 0.45,
        "memory_usage": 0.60,
        "timestamp": "2026-04-01 10:00:00"
    },
    {
        "cpu_usage": 0.50,
        "memory_usage": 0.65,
        "timestamp": "2026-04-02 10:00:00"
    }
]
```

**响应示例**:
```json
{
    "trend": "stable",
    "avg_cpu": 0.475,
    "avg_memory": 0.625,
    "prediction": "预计CPU使用率: 47.50%, 内存使用率: 62.50%",
    "alert": false
}
```

---

## 四、接口调用最佳实践

### 4.1 错误处理

所有接口都应遵循统一的错误处理格式：

**错误响应示例**:
```json
{
    "error_code": "INVALID_PARAMETER",
    "error_message": "参数order_id不能为空",
    "timestamp": "2026-04-02 10:30:00"
}
```

### 4.2 重试机制

对于可能失败的操作，建议实现重试机制：
- 最大重试次数: 3次
- 重试间隔: 指数退避（1s, 2s, 4s）
- 超时时间: 30秒

### 4.3 性能优化

- 使用连接池管理数据库连接
- 对频繁调用的接口使用缓存
- 批量操作优于单个操作

---

**版本**: v1.0 | **更新**: 2026-04-02 | **状态**: ✅ 活跃
