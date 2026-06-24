---
module_id: KE-2888
status: active
title: sensitivity_sweep_report.yaml —— Wave 2 health-monitor.py 产出
category: module_blueprint
---

# sensitivity_sweep_report.yaml —— Wave 2 health-monitor.py 产出

sensitivity_sweep_report.yaml —— Wave 2 health-monitor.py 产出
sensitivity_sweep:
  date: "2026-06-01"
  normal_threshold_findings: 5            # 正常阈值发现 5 组
  lowered_threshold_findings: 9           # 降低阈值后发现 9 组（多了 4 组潜在漏报）
  fnr_estimate: "≈ 44%"                   # 漏报率约 44%——高！
  new_findings:
    - dup_id: "SWEEP-20260601-001"
      similarity_at_normal: 0.62          # 正常阈值 0.65 下被漏掉
      similarity_at_lowered: 0.62         # 降低到 0.50 后被检出
      functions: ["_init_db", "init_database"]
      review_result: "TRUE_DUPLICATE"     # 人工审查确认是真重复
      root_cause: "不同文件不同函数名——无签名碰撞检测触发"
  recommendation: "建议在 Stage 0.5 中增加函数名相似度匹配（Levenshtein距离≤2→进行更深层比较）"
```

```yaml
