---
module_id: KE-1607
title: 2. Blindspots B1-B12
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2. Blindspots B1-B12

2. Blindspots B1-B12

| # | 盲点 | 严重度 | 实现文件 | DD |
|---|------|:---:|------|:---:|
| B1 | CE 自举架构 | P0 | ce_bootstrap.py | DD75 |
| B2 | 上下文价值归因 | P0 | context_value_attribution.py | DD76 |
| B3 | 策略自动进化 | P1 | (ce_bootstrap 扩展) | DD77 |
| B4 | 金丝雀部署 | P1 | shadow_canary.py | DD78 |
| B5 | 上下文沙箱 | P1 | context_playground.py | DD79 |
| B6 | 统一健康分 | P1 | ContextHealthScore.py | DD80 |
| B7 | 渐进式披露 | P1 | progressive_disclosure_injector.py | DD81 |
| B8 | 对抗鲁棒性 | P1 | adversarial_robustness.py | DD82 |
| B9 | 数据分级 | P2 | sensitivity_classifier.py | DD83 |
| B10 | 知识蒸馏 | P2 | knowledge_distiller.py | DD84 |
| B11 | 对齐评分 | P2 | alignment_scorer.py | DD85 |
| B12 | 全链路 OTel | P2 | otel_instrumentation.py | DD86 |
