# 数据字典详细说明

> **版本**: v1.0
> **创建日期**: 2026-04-02
> **目的**: 为所有新建模块补充详细的数据字典说明

---

## 一、合规监控模块数据字典

### 1.1 compliance_checks (合规检查表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| check_id | VARCHAR | 50 | 是 | - | 检查记录唯一标识 | check_20260402_001 | 格式: check_YYYYMMDD_NNN |
| order_id | VARCHAR | 50 | 是 | - | 关联的订单ID | order_20260402_001 | 外键关联订单表 |
| check_type | VARCHAR | 20 | 是 | - | 检查类型 | trading_compliance | 枚举: trading_compliance, risk_compliance |
| check_result | VARCHAR | 10 | 是 | - | 检查结果 | pass | 枚举: pass, fail, warning |
| violations | TEXT | - | 否 | NULL | 违规项列表(JSON) | [{"type": "volume_limit_exceeded"}] | JSON格式存储 |
| action_taken | VARCHAR | 20 | 是 | - | 采取的行动 | approved | 枚举: approved, blocked, reviewed |
| check_time | DATETIME | - | 是 | CURRENT_TIMESTAMP | 检查时间 | 2026-04-02 10:30:00 | 自动生成 |
| reviewer | VARCHAR | 20 | 是 | - | 审核者 | AI | 枚举: AI, MANUAL |

**索引**:
- PRIMARY KEY: check_id
- INDEX: order_id (用于快速查询订单的合规检查记录)
- INDEX: check_time (用于按时间范围查询)

**业务约束**:
- check_result为fail时，action_taken必须为blocked
- violations字段仅在check_result为fail或warning时有值

---

### 1.2 risk_limits (风险限额表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| limit_id | VARCHAR | 50 | 是 | - | 限额配置唯一标识 | limit_001 | 格式: limit_NNN |
| limit_type | VARCHAR | 30 | 是 | - | 限额类型 | position_limit | 枚举: position_limit, loss_limit, var_limit |
| limit_value | DECIMAL | (15,2) | 是 | - | 限额值 | 1000000.00 | 正数，单位：元 |
| warning_threshold | DECIMAL | (5,2) | 是 | 0.80 | 预警阈值 | 0.80 | 0.00-1.00，表示使用率 |
| critical_threshold | DECIMAL | (5,2) | 是 | 0.90 | 临界阈值 | 0.90 | 0.00-1.00，表示使用率 |
| is_active | BOOLEAN | - | 是 | TRUE | 是否激活 | TRUE | 布尔值 |
| updated_at | DATETIME | - | 是 | CURRENT_TIMESTAMP | 更新时间 | 2026-04-02 10:30:00 | 自动更新 |

**索引**:
- PRIMARY KEY: limit_id
- INDEX: limit_type (用于按类型查询限额)

**业务约束**:
- warning_threshold < critical_threshold
- limit_value必须大于0

---

### 1.3 regulatory_reports (监管报告表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| report_id | VARCHAR | 50 | 是 | - | 报告唯一标识 | report_20260402_001 | 格式: report_YYYYMMDD_NNN |
| report_type | VARCHAR | 30 | 是 | - | 报告类型 | daily_report | 枚举: daily_report, weekly_report, monthly_report |
| period_start | DATE | - | 是 | - | 报告周期开始日期 | 2026-04-01 | YYYY-MM-DD格式 |
| period_end | DATE | - | 是 | - | 报告周期结束日期 | 2026-04-01 | YYYY-MM-DD格式 |
| compliance_status | VARCHAR | 20 | 是 | - | 合规状态 | compliant | 枚举: compliant, non_compliant, partial |
| violations_count | INTEGER | - | 是 | 0 | 违规次数 | 0 | 非负整数 |
| report_content | TEXT | - | 是 | - | 报告内容(Markdown) | # 监管合规报告... | Markdown格式 |
| generated_at | DATETIME | - | 是 | CURRENT_TIMESTAMP | 生成时间 | 2026-04-02 18:00:00 | 自动生成 |

**索引**:
- PRIMARY KEY: report_id
- INDEX: report_type (用于按类型查询报告)
- INDEX: period_start, period_end (用于按周期查询)

**业务约束**:
- period_end >= period_start
- violations_count与compliance_status一致

---

### 1.4 audit_trail (审计追踪表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| audit_id | VARCHAR | 50 | 是 | - | 审计记录唯一标识 | audit_20260402_001 | 格式: audit_YYYYMMDD_NNN |
| event_type | VARCHAR | 30 | 是 | - | 事件类型 | compliance_check | 枚举: compliance_check, report_generation, violation_alert |
| user_id | VARCHAR | 50 | 是 | - | 用户ID | user_001 | 关联用户表 |
| action | VARCHAR | 50 | 是 | - | 执行的操作 | check_trading_compliance | 操作名称 |
| details | TEXT | - | 否 | NULL | 详细信息(JSON) | {"order_id": "order_001"} | JSON格式存储 |
| result | VARCHAR | 20 | 是 | - | 操作结果 | success | 枚举: success, failure |
| ip_address | VARCHAR | 50 | 否 | NULL | IP地址 | 192.168.1.1 | IPv4或IPv6格式 |
| timestamp | DATETIME | - | 是 | CURRENT_TIMESTAMP | 时间戳 | 2026-04-02 10:30:00 | 自动生成 |

**索引**:
- PRIMARY KEY: audit_id
- INDEX: user_id (用于查询用户操作记录)
- INDEX: timestamp (用于按时间范围查询)

**业务约束**:
- 所有合规相关操作必须记录审计追踪

---

## 二、实盘监控模块数据字典

### 2.1 realtime_monitoring (实时监控表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| monitor_id | VARCHAR | 50 | 是 | - | 监控记录唯一标识 | monitor_20260402_001 | 格式: monitor_YYYYMMDD_NNN |
| order_count | INTEGER | - | 是 | - | 订单数量 | 15 | 非负整数 |
| volume | INTEGER | - | 是 | - | 交易量 | 500000 | 非负整数，单位：股 |
| turnover | DECIMAL | (15,2) | 是 | - | 成交金额 | 7750000.00 | 非负数，单位：元 |
| status | VARCHAR | 20 | 是 | - | 监控状态 | normal | 枚举: normal, warning, critical |
| alerts | TEXT | - | 否 | NULL | 告警信息(JSON) | [{"type": "high_frequency"}] | JSON格式存储 |
| timestamp | DATETIME | - | 是 | CURRENT_TIMESTAMP | 时间戳 | 2026-04-02 10:30:00 | 自动生成 |

**索引**:
- PRIMARY KEY: monitor_id
- INDEX: timestamp (用于按时间范围查询)

**业务约束**:
- status与alerts字段一致

---

### 2.2 position_risk (持仓风险表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| risk_id | VARCHAR | 50 | 是 | - | 风险记录唯一标识 | risk_20260402_001 | 格式: risk_YYYYMMDD_NNN |
| position_id | VARCHAR | 50 | 是 | - | 持仓ID | pos_001 | 关联持仓表 |
| symbol | VARCHAR | 20 | 是 | - | 股票代码 | 000001.SZ | 标准格式 |
| position_value | DECIMAL | (15,2) | 是 | - | 持仓市值 | 1000000.00 | 非负数，单位：元 |
| unrealized_pnl | DECIMAL | (15,2) | 是 | - | 未实现盈亏 | 50000.00 | 可正可负 |
| risk_exposure | DECIMAL | (5,2) | 是 | - | 风险敞口 | 0.05 | 0.00-1.00 |
| var_value | DECIMAL | (15,2) | 是 | - | VaR值 | -20000.00 | 负数，表示潜在损失 |
| risk_status | VARCHAR | 20 | 是 | - | 风险状态 | normal | 枚举: normal, warning, critical |
| timestamp | DATETIME | - | 是 | CURRENT_TIMESTAMP | 时间戳 | 2026-04-02 10:30:00 | 自动生成 |

**索引**:
- PRIMARY KEY: risk_id
- INDEX: position_id (用于查询持仓风险)
- INDEX: timestamp (用于按时间范围查询)

**业务约束**:
- var_value必须为负数
- risk_status根据risk_exposure和var_value自动判定

---

### 2.3 anomaly_alerts (异常告警表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| alert_id | VARCHAR | 50 | 是 | - | 告警唯一标识 | alert_20260402_001 | 格式: alert_YYYYMMDD_NNN |
| anomaly_type | VARCHAR | 30 | 是 | - | 异常类型 | abnormal_order | 枚举: abnormal_order, high_frequency, price_deviation |
| severity | VARCHAR | 10 | 是 | - | 严重程度 | high | 枚举: low, medium, high, critical |
| description | TEXT | - | 是 | - | 异常描述 | 订单金额异常大: 1500000 | 文本描述 |
| is_resolved | BOOLEAN | - | 是 | FALSE | 是否已解决 | FALSE | 布尔值 |
| resolved_by | VARCHAR | 50 | 否 | NULL | 解决者 | user_001 | 关联用户表 |
| resolved_at | DATETIME | - | 否 | NULL | 解决时间 | 2026-04-02 11:00:00 | 解决时自动填充 |
| timestamp | DATETIME | - | 是 | CURRENT_TIMESTAMP | 时间戳 | 2026-04-02 10:30:00 | 自动生成 |

**索引**:
- PRIMARY KEY: alert_id
- INDEX: is_resolved (用于查询未解决的告警)
- INDEX: timestamp (用于按时间范围查询)

**业务约束**:
- is_resolved为TRUE时，resolved_by和resolved_at必填

---

### 2.4 performance_metrics (性能指标表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| metric_id | VARCHAR | 50 | 是 | - | 指标记录唯一标识 | metric_20260402_001 | 格式: metric_YYYYMMDD_NNN |
| latency_ms | DECIMAL | (10,2) | 是 | - | 延迟(毫秒) | 15.50 | 非负数 |
| throughput | INTEGER | - | 是 | - | 吞吐量(请求/秒) | 1000 | 非负整数 |
| cpu_usage | DECIMAL | (5,2) | 是 | - | CPU使用率 | 0.45 | 0.00-1.00 |
| memory_usage | DECIMAL | (5,2) | 是 | - | 内存使用率 | 0.60 | 0.00-1.00 |
| timestamp | DATETIME | - | 是 | CURRENT_TIMESTAMP | 时间戳 | 2026-04-02 10:30:00 | 自动生成 |

**索引**:
- PRIMARY KEY: metric_id
- INDEX: timestamp (用于按时间范围查询)

**业务约束**:
- cpu_usage和memory_usage必须在0.00-1.00范围内

---

## 三、性能分析模块数据字典

### 3.1 performance_metrics (性能指标表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| metric_id | VARCHAR | 50 | 是 | - | 指标记录唯一标识 | metric_20260402_001 | 格式: metric_YYYYMMDD_NNN |
| module_name | VARCHAR | 50 | 是 | - | 模块名称 | factor_calculator | 模块标识符 |
| cpu_usage | DECIMAL | (5,2) | 是 | - | CPU使用率 | 0.45 | 0.00-1.00 |
| memory_usage | DECIMAL | (5,2) | 是 | - | 内存使用率 | 0.60 | 0.00-1.00 |
| io_wait | DECIMAL | (5,2) | 否 | 0.00 | I/O等待时间占比 | 0.20 | 0.00-1.00 |
| network_latency | INTEGER | - | 否 | 0 | 网络延迟(ms) | 50 | 非负整数 |
| timestamp | DATETIME | - | 是 | CURRENT_TIMESTAMP | 时间戳 | 2026-04-02 10:30:00 | 自动生成 |

**索引**:
- PRIMARY KEY: metric_id
- INDEX: module_name (用于按模块查询)
- INDEX: timestamp (用于按时间范围查询)

**业务约束**:
- 所有使用率字段必须在0.00-1.00范围内

---

### 3.2 performance_bottlenecks (性能瓶颈表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| bottleneck_id | VARCHAR | 50 | 是 | - | 瓶颈记录唯一标识 | bottleneck_20260402_001 | 格式: bottleneck_YYYYMMDD_NNN |
| module_name | VARCHAR | 50 | 是 | - | 模块名称 | factor_calculator | 模块标识符 |
| bottleneck_type | VARCHAR | 30 | 是 | - | 瓶颈类型 | cpu_bottleneck | 枚举: cpu_bottleneck, memory_bottleneck, io_bottleneck |
| severity | VARCHAR | 10 | 是 | - | 严重程度 | high | 枚举: low, medium, high, critical |
| description | TEXT | - | 是 | - | 瓶颈描述 | CPU使用率过高: 85% | 文本描述 |
| impact_score | DECIMAL | (5,2) | 是 | - | 影响分数 | 0.85 | 0.00-1.00 |
| is_resolved | BOOLEAN | - | 是 | FALSE | 是否已解决 | FALSE | 布尔值 |
| resolved_at | DATETIME | - | 否 | NULL | 解决时间 | 2026-04-02 11:00:00 | 解决时自动填充 |
| timestamp | DATETIME | - | 是 | CURRENT_TIMESTAMP | 时间戳 | 2026-04-02 10:30:00 | 自动生成 |

**索引**:
- PRIMARY KEY: bottleneck_id
- INDEX: module_name (用于按模块查询)
- INDEX: is_resolved (用于查询未解决的瓶颈)

**业务约束**:
- is_resolved为TRUE时，resolved_at必填

---

### 3.3 performance_reports (性能报告表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| report_id | VARCHAR | 50 | 是 | - | 报告唯一标识 | report_20260402_001 | 格式: report_YYYYMMDD_NNN |
| module_name | VARCHAR | 50 | 是 | - | 模块名称 | factor_calculator | 模块标识符 |
| avg_cpu_usage | DECIMAL | (5,2) | 是 | - | 平均CPU使用率 | 0.45 | 0.00-1.00 |
| avg_memory_usage | DECIMAL | (5,2) | 是 | - | 平均内存使用率 | 0.60 | 0.00-1.00 |
| bottlenecks_count | INTEGER | - | 是 | 0 | 瓶颈数量 | 3 | 非负整数 |
| report_content | TEXT | - | 是 | - | 报告内容(Markdown) | # 性能分析报告... | Markdown格式 |
| generated_at | DATETIME | - | 是 | CURRENT_TIMESTAMP | 生成时间 | 2026-04-02 18:00:00 | 自动生成 |

**索引**:
- PRIMARY KEY: report_id
- INDEX: module_name (用于按模块查询)
- INDEX: generated_at (用于按时间范围查询)

**业务约束**:
- bottlenecks_count与report_content中的瓶颈数量一致

---

### 3.4 optimization_suggestions (优化建议表)

| 字段名 | 数据类型 | 长度 | 必填 | 默认值 | 说明 | 示例值 | 业务规则 |
|--------|---------|------|------|--------|------|--------|----------|
| suggestion_id | VARCHAR | 50 | 是 | - | 建议唯一标识 | suggestion_20260402_001 | 格式: suggestion_YYYYMMDD_NNN |
| module_name | VARCHAR | 50 | 是 | - | 模块名称 | factor_calculator | 模块标识符 |
| suggestion_type | VARCHAR | 30 | 是 | - | 建议类型 | code_optimization | 枚举: code_optimization, architecture_optimization, resource_optimization |
| description | TEXT | - | 是 | - | 建议描述 | 优化CPU密集型操作 | 文本描述 |
| priority | VARCHAR | 10 | 是 | - | 优先级 | high | 枚举: low, medium, high, critical |
| estimated_improvement | DECIMAL | (5,2) | 否 | NULL | 预期改进幅度 | 0.30 | 0.00-1.00 |
| is_implemented | BOOLEAN | - | 是 | FALSE | 是否已实施 | FALSE | 布尔值 |
| implemented_at | DATETIME | - | 否 | NULL | 实施时间 | 2026-04-02 11:00:00 | 实施时自动填充 |
| timestamp | DATETIME | - | 是 | CURRENT_TIMESTAMP | 时间戳 | 2026-04-02 10:30:00 | 自动生成 |

**索引**:
- PRIMARY KEY: suggestion_id
- INDEX: module_name (用于按模块查询)
- INDEX: is_implemented (用于查询未实施的建议)

**业务约束**:
- is_implemented为TRUE时，implemented_at必填

---

## 四、数据关系图

### 4.1 合规监控模块数据关系

```
compliance_checks (合规检查表)
    ├── order_id → 订单表
    └── violations → JSON格式存储违规项

risk_limits (风险限额表)
    └── 独立配置表，无外键关联

regulatory_reports (监管报告表)
    └── 独立报告表，无外键关联

audit_trail (审计追踪表)
    └── user_id → 用户表
```

### 4.2 实盘监控模块数据关系

```
realtime_monitoring (实时监控表)
    └── 独立监控表，无外键关联

position_risk (持仓风险表)
    ├── position_id → 持仓表
    └── symbol → 股票代码

anomaly_alerts (异常告警表)
    └── resolved_by → 用户表

performance_metrics (性能指标表)
    └── 独立指标表，无外键关联
```

### 4.3 性能分析模块数据关系

```
performance_metrics (性能指标表)
    └── module_name → 模块标识符

performance_bottlenecks (性能瓶颈表)
    └── module_name → 模块标识符

performance_reports (性能报告表)
    └── module_name → 模块标识符

optimization_suggestions (优化建议表)
    └── module_name → 模块标识符
```

---

## 五、数据完整性约束

### 5.1 实体完整性
- 所有表都有主键
- 主键字段不能为NULL
- 主键值必须唯一

### 5.2 参照完整性
- 外键字段必须引用有效的主键值
- 外键字段可以为NULL（如果业务允许）

### 5.3 域完整性
- 字段值必须符合数据类型要求
- 字段值必须符合业务规则约束
- 必填字段不能为NULL

---

**版本**: v1.0 | **更新**: 2026-04-02 | **状态**: ✅ 活跃
