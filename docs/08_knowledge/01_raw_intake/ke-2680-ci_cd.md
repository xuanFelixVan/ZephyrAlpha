---
module_id: KE-2585
status: active
title: CI/CD 集成约束
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# CI/CD 集成约束

CI/CD 集成约束

```
CI/CD Pipeline 中的 Observability-as-Code 步骤:
  1. Lint:     yamllint config/*.yaml
  2. Validate: Telemetry schema validator → 校验所有 YAML SSoT
  3. Diff:     与上一个 git commit 的 diff → 生成 changelog
  4. Test:     dry-run alert rules with historical data（§11b backtest）
  5. Deploy:   合并到 main 后自动生效（热加载）或通过 grafanactl push dashboards
  6. Verify:   Post-deploy 合成监控事务（§11b synth.*）
```
