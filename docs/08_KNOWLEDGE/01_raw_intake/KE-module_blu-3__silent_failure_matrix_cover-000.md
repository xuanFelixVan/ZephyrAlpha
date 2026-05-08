---
module_id: KE-module_blu-3__silent_failure_matrix_cover-000
title: 3. Silent Failure Matrix Coverage
category: module_blueprint
---

# 3. Silent Failure Matrix Coverage

3. Silent Failure Matrix Coverage

| 失效模式 | 关联盲点 | 检测机制 |
|---------|:---:|------|
| 兜底上下文陈旧但被注入 | B13 | fallback_staleness_gate SHA256+age |
| 高质量上下文导致错误决策 | B14 | context_outcome_tracker 因果关联 |
| 上下文缓慢累积偏离 | B15 | solo_dev safety_net heatmap |
| 错误配置生效但无崩溃 | B16 | config_safety_guard domain check |
| CE 吃掉所有内存 | B17 | host_resource_governor RAM probe |
| 嵌入模型静默升级 | B18 | embedding_version_lock cosine regress |
| 垃圾 KE 持续注入 | B19 | context_debt_score deprecation_risk |
| LSG 模式逃逸 | B20 | lsg_pattern_tracker pattern tracking |
