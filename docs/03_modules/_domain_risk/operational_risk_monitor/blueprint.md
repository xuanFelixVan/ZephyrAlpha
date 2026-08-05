---
module_id: MOD-RK-19
doc_type: blueprint
ttl: permanent
blueprint_id: MOD-RK-19
domain_id: D_RISK
path: src/zephyr/risk/core/operational_risk_monitor.py
design_maturity: design
build_status: planned
granularity: file
ai_autonomy: ai_modifiable
safety: L
stability: evolving
responsibility_domain: 
---

# MOD-RK-19 操作风险监控器 (OperationalRiskMonitor)

## 1. 定位

D_RISK 域 A 类基础设施——操作风险阈值解释层。

组装缺口：MOD-EX-003 (auditor.py) 已提供 `OperationalRiskStats`（failure_rate /
fill_rate / latency p50/p95/max/mean），但**无阈值告警**。本模块不重算任何统计，
仅做阈值解释 + RiskCheckResult 转换，将纯统计转换为风险评估结果。

## 2. 输入/输出

| 方向 | 契约 | 类型 |
|------|------|------|
| 输入 | OperationalRiskStats (来自 MOD-EX-003) | dataclass |
| 输出 | OperationalRiskAssessment | dataclass |
| 输出 | RiskCheckResult (via to_risk_check_result) | dataclass |

## 3. 核心规则

- failure_rate_breached: failure_rate > 0.05 (默认阈值，行业标准)
- latency_breached: latency_p95_ms > 500.0 (默认阈值，行业标准)
- 严重度倍数: 实际值 >= 2×阈值 → severe
- overall_severity:
  - HALT: 任一维度 severe OR 双维度都突破（非 severe）
  - warning: 单维度突破（非 severe）
  - info: 均未突破

## 4. 依赖

- MOD-EX-003 (ex_core/audit_journal/auditor) — OperationalRiskStats 真源
- MOD-L04-001 (risk_manager_base) — RiskCheckResult

## 5. 验收

- 失败率 > 5% 触发告警
- 延迟 p95 > 500ms 触发告警
- severe (>=2×阈值) → HALT
- 双维度突破 → HALT
- 零提交数据 → info + insufficient data finding
- RiskCheckResult severity 映射正确
