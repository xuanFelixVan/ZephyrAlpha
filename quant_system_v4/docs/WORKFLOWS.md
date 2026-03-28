# WORKFLOWS.md - 工作流规格

> **版本**：v4.0
> **日期**：2026-03-28
> **状态**：设计阶段

---

## 1. 工作流概览

| 工作流 | 触发方式 | 说明 |
|--------|----------|------|
| **daily_pipeline** | 每日19:00 | 每日量化流水线 |
| **backtest_pipeline** | 按需触发 | 回测流水线 |
| **factor_optimization** | 每周 | 因子优化流水线 |
| **strategy_update** | 每月 | 策略更新流水线 |

---

## 2. daily_pipeline - 每日流水线

```
┌─────────────────────────────────────────────────────────────────┐
│                    每日量化流水线 (daily_pipeline)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  18:00 ─┬─→ 数据更新 ─→ 数据清洗 ─→ 数据存储                     │
│          │                                                       │
│  19:00 ─┼─→ 因子计算 ─→ 因子验证                                 │
│          │                                                       │
│  19:30 ─┼─→ 策略信号 ─→ 风险校验                                 │
│          │                                                       │
│  20:00 ─┼─→ 生成报告 ─→ 发送通知                                 │
│          │                                                       │
│  20:30 ─┴─→ 完成                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 详细步骤

```yaml
workflow:
  name: "daily_pipeline"
  schedule: "0 19 * * 1-5"  # 周一至周五19:00

  steps:
    - name: "data_update"
      time: "18:00"
      module: "data_collector"
      action: "collect_all"
      params:
        date: "${yesterday}"
      error_action: "retry"

    - name: "data_clean"
      time: "18:30"
      module: "data_cleaner"
      action: "clean"
      params:
        source: "raw"
        dest: "processed"
      depends_on: ["data_update"]

    - name: "factor_calc"
      time: "19:00"
      module: "factor_calculator"
      action: "calculate_selected"
      params:
        top_n: 50
      depends_on: ["data_clean"]

    - name: "strategy_signals"
      time: "19:30"
      module: "strategy_engine"
      action: "run_all"
      depends_on: ["factor_calc"]

    - name: "risk_validation"
      time: "20:00"
      module: "risk_manager"
      action: "validate_signals"
      depends_on: ["strategy_signals"]

    - name: "generate_report"
      time: "20:30"
      module: "report_generator"
      action: "generate_daily_report"
      depends_on: ["risk_validation"]
```

---

## 3. backtest_pipeline - 回测流水线

```
┌─────────────────────────────────────────────────────────────────┐
│                      回测流水线 (backtest_pipeline)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  start ─→ 参数验证 ─→ 数据准备 ─→ 逐日回测 ─→ 绩效计算            │
│                │                                        │        │
│                ▼                                        ▼        │
│           验证失败 ──────────────────────────────────→ 生成报告  │
│                                                          │        │
│                                                          ▼        │
│                                                    过拟合检验    │
│                                                          │        │
│                                                          ▼        │
│                                                    完成            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.1 详细步骤

```yaml
workflow:
  name: "backtest_pipeline"
  trigger: "manual"  # 手动触发

  steps:
    - name: "validate_params"
      module: "backtest_framework"
      action: "validate_params"
      params:
        required: ["strategy_id", "start_date", "end_date"]

    - name: "prepare_data"
      module: "data_storage"
      action: "load_backtest_data"
      depends_on: ["validate_params"]

    - name: "run_backtest"
      module: "backtest_framework"
      action: "run"
      depends_on: ["prepare_data"]

    - name: "calculate_metrics"
      module: "backtest_framework"
      action: "calculate_metrics"
      depends_on: ["run_backtest"]

    - name: "check_overfitting"
      module: "backtest_framework"
      action: "check_overfitting"
      depends_on: ["calculate_metrics"]

    - name: "generate_report"
      module: "report_generator"
      action: "generate_backtest_report"
      depends_on: ["check_overfitting"]
```

---

## 4. 任务依赖图

```
                    ┌──────────────┐
                    │  daily_pipeline │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ 因子计算  │    │ 策略信号  │    │ 风险校验  │
    └─────┬────┘    └─────┬────┘    └─────┬────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  生成报告    │
                   └──────────────┘
```

---

## 5. 调度配置

```yaml
schedules:
  daily_pipeline:
    cron: "0 19 * * 1-5"
    timezone: "Asia/Shanghai"
    enabled: true

  weekly_factor_optimization:
    cron: "0 2 * * 0"  # 每周日凌晨2点
    timezone: "Asia/Shanghai"
    enabled: true

  monthly_strategy_review:
    cron: "0 3 1 * *"  # 每月1日凌晨3点
    timezone: "Asia/Shanghai"
    enabled: false  # 暂时禁用
```

---

## 6. 错误处理

```yaml
error_handling:
  retry:
    max_attempts: 3
    backoff: "exponential"
    initial_delay: 60  # 秒

  fallback:
    enabled: true
    action: "use_previous_data"

  notification:
    on_failure: true
    on_success: false
    channels: ["log", "console"]
```

---

## 7. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 初始版本，工作流规格设计 |
