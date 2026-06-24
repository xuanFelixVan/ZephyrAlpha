---
module_id: KE-331----p0-003
title: 4.2 experimental SLI/SLO 基线（P0 必采）
category: documentation
---

# 4.2 experimental SLI/SLO 基线（P0 必采）

4.2 experimental SLI/SLO 基线（P0 必采）

| 服务 | SLI 指标 | SLO 阈值 | 告警动作 |
|------|---------|:--------:|---------|
| Context Engine | `build()` 延迟 P99 | < 500ms | FLE → CE 降级规则基 |
| Vector Memory | `search()` 延迟 P99 | < 200ms（稳态）| FLE → 检查 ChromaDB 健康 |
| Vector Memory | `bulk_bootstrap` 冷启动 | < 60s/200 文档 | FLE → 容量检查 |
| Agent Orchestrator | 任务 P99 排队时延 | < 5s | FLE → 并发阈值告警 |
| Agent Orchestrator | 幻觉检测漏检率 | < 10% | TECH-09 升级触发 |
| Feedback Loop | 异常检测延迟 | < 30s | 自监控自告警 |
| LSG | 误拦率 | < 2% | 红队评估触发 |
| LSG | 漏拦率 | < 5% | TECH-16 升级触发 |
| LSG | fail-closed 触发频率 | < 0.1%/天 | 人工介入 |

**SLO 来源**：每项 SLO 都有 `technology_landscape.yaml upgrade_watchboard` 中对应的升级阈值。
