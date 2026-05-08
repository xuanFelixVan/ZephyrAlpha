---
module_id: KE-module_blu-canary_report_yaml-000
title: canary_report.yaml —— 每次全量扫描自动生成
category: module_blueprint
---

# canary_report.yaml —— 每次全量扫描自动生成

canary_report.yaml —— 每次全量扫描自动生成
canary:
  positives:
    total: 8
    detected: 7
    missed: 1                             # 灵敏度下降——漏掉了一个已知重复
    missed_case: "canary_002——函数被拆分为两个嵌套函数后引擎不再识别为重复"
    sensitivity: 87.5%                    # 上次98%→本次87.5%——恶化！
  negatives:
    total: 6
    correctly_exempted: 6
    incorrectly_flagged: 0
    specificity: 100%
```
