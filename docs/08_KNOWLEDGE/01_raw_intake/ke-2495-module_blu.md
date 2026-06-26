---
module_id: KE-2400
status: active
title: 6.7 测试覆盖漂移
category: module_blueprint
ttl: permanent
---

# 6.7 测试覆盖漂移

6.7 测试覆盖漂移

```yaml
test_coverage_drift:
  description: "模块代码增长但测试比例下降"
  method: "定期统计每个模块的代码行数 vs 测试行数 → 比率趋势"
  alert: "覆盖率月环比下降 > 10%"
```
