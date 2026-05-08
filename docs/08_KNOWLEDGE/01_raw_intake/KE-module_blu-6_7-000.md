---
module_id: KE-module_blu-6_7-000
title: 6.7 测试覆盖漂移
category: module_blueprint
---

# 6.7 测试覆盖漂移

6.7 测试覆盖漂移

```yaml
test_coverage_drift:
  description: "模块代码增长但测试比例下降"
  method: "定期统计每个模块的代码行数 vs 测试行数 → 比率趋势"
  alert: "覆盖率月环比下降 > 10%"
```
