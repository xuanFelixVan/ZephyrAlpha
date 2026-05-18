---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "System Telemetry 蓝图"
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: System Telemetry 蓝图

## CRITICAL Rules

### Core Operations
### Dead Letter Queue 操作设计 🆕

> **B48 修复**——v0.7.0 新增。蓝图摘要宣称 "DLQ 保障数据质量闭环" 与 "DLQ 自动修复"，但完整的 DLQ 操作设计此前从未落地。DLQ 是全系统遥测数据质量的最后兜底——所有被拒绝/无法处理的事件（schema 校验失败、写入失败、类型错误）进入 DLQ，而非静默丢弃。

#### DLQ 事件生命周期

```
遥测事件提交
  ├── 正常路径: schema 校验通过 → ring buffer → flush → SQLite/JSONL ✅
  ├── 软拒绝: schema 校验失败 / 类型错误 → DLQ 写入 + rejection log ✅
  ├── 硬拒绝: JSON 解析失败 / 恶意 payload → DLQ 写入 + P2 安全事件 ⚠️
  └── 系统级失败: DLQ 写入失败 → stderr fallback → 内存缓冲 → 丢弃+告警 ❌
```

#### DLQ 存储设计

| 属性 | 规格 |
|------|------|
| **存储格式** | JSONL（与正常日志格式一致，便于统一查询） |
| **存储路径** | `data/telemetry/{environment}/dlq/{date}.jsonl` |
| **TTL** | 30 天（与 logs 同级，过期后归档或删除） |
| **结构** | `{original_event, rejection_reason, rejected_by, timestamp, dlq_id}` |
| **单文件上限** | 100MB 后自动轮转 |

#### DLQ 自动修复策略

```
DLQ 自动修复流程:
  每 60min（或 DLQ 文件 > 10MB 时触发的 event-driven）:
    → 扫描 DLQ 中所有事件
    → 按 rejection_reason 分类:
      ├── SCHEMA_ERROR: schema 漂移 → Schema Registry 查询最新 schema → 尝试 re-map
      │   → 成功 → 重新走正常路径写入 → 从 DLQ 标记为 "repaired"
      │   → 失败 → 保留在 DLQ + 递增 retry_count
      ├── TYPE_ERROR: 字段类型不匹配 → 尝试类型强制转换
      │   → 成功 → repaired
      │   → 失败 → 保留 + 人工审查标记
      └── WRITE_FAILED: IO/DB 临时不可用 → 简单重试（最多 3 次）
    → 生成 DLQ repair report → 写入 Audit Trail
    → 重试超过 3 次的事件 → 标记为 DEAD → 保留 7 天后物理删除
```

#### DLQ 监控

| 指标 | 告警阈值 |
|------|:---:|
| `dlq_size_bytes` | > 100MB → P2 |
| `dlq_growth_rate` | > 10MB/h → P1（上游失控） |
| `dlq_repair_success_rate` | < 50% → P2（自动修复失效） |
| `dlq_dead_event_count` | > 1000 → P1（需人工介入） |
| `dlq_age_oldest_event` | > 24h → P2（积压） |

#### AI 消费 DLQ

```
AI 通过 MCP 接口消费 DLQ:
  get_dlq_summary() → {total_events, by_reason, repair_rate, oldest_event_age}
  get_dlq_samples(reason: str, limit: int) → list[DLQEvent]
  → AI 发现 schema 漂移趋势后主动修正蓝图或代码
```

### Unique Constraints
### CI/CD 集成约束

```
CI/CD Pipeline 中的 Observability-as-Code 步骤:
  1. Lint:     yamllint config/*.yaml
  2. Validate: Telemetry schema validator → 校验所有 YAML SSoT
  3. Diff:     与上一个 git commit 的 diff → 生成 changelog
  4. Test:     dry-run alert rules with historical data（§11b backtest）
  5. Deploy:   合并到 main 后自动生效（热加载）或通过 grafanactl push dashboards
  6. Verify:   Post-deploy 合成监控事务（§11b synth.*）
```

### Common Error Patterns
待填写

## Checklist

- [ ] Verify blueprint before implementation
- [ ] Check upstream dependencies
- [ ] Validate against acceptance criteria
- [ ] Run gate engine checks (G0-G9)

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_TIMEOUT | 30 | Default operation timeout (seconds) |

## References (L3, on-demand)

- module_blueprint.md
- integration_guide.md
- troubleshooting.md