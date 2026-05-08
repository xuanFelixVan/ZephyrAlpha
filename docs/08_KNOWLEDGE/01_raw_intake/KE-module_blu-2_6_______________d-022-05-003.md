---
module_id: KE-module_blu-2_6_______________d-022-05-003
title: 2.6 升级引擎自身故障处理（决策 D-022-05）
category: module_blueprint
---

# 2.6 升级引擎自身故障处理（决策 D-022-05）

2.6 升级引擎自身故障处理（决策 D-022-05）

> **决策 D-022-05**：升级引擎自身必须定义故障安全默认策略（fail-safe default）。引擎崩溃/超时/规则加载失败时，默认行为是"deny by default"——阻止操作并通知Owner。引擎需要健康检查端点。
>
> **决策依据**：对标 Terraform plan 的 -detailed-exitcode（exit 0=通过，1=错误→阻断，2=变更→审批）。升级引擎作为系统安全枢纽，自身不可靠则整个安全体系崩塌。

```yaml
engine_resilience:
  # === Fail-Safe 默认 ===
  fail_safe_default:
    escalation_engine_crash: "deny_by_default → blocked"
    rules_load_failure: "deny_by_default → blocked + 通知Owner"
    rules_yaml_parse_error: "deny_by_default → blocked + 通知Owner + 报告解析错误详情"
    delegation_manager_crash: "当前Agent继续自主（但不委托） + auto_guard模式"
    reason: "安全系统不能fail-open——宁可误阻断也不能误放行"

  # === 健康检查 ===
  health_check:
    endpoint: "escalation_engine.health() → {status, rules_loaded, rules_hash, last_check_time}"
    interval: "每次升级判定前先自检"
    timeout: "500ms——超时视为不健康 → deny_by_default"

  # === 降级运行 ===
  degraded_mode:
    when: "部分依赖不可用（Gate Engine超时/审计写入失败）"
    behavior: "缓存最近一次成功的规则判定结果（TTL=60s）+ 标记degraded → 通知Owner"
    recovery: "依赖恢复后自动退出降级模式"

  # === 引擎状态码 ===
  engine_exit_codes:
    - code: 0
      meaning: "判定完成——操作放行"
    - code: 1
      meaning: "判定完成——操作升级（auto_guard/blocked）"
    - code: 2
      meaning: "引擎内部错误——deny_by_default"
    - code: 3
      meaning: "规则加载失败——deny_by_default"
```

---
