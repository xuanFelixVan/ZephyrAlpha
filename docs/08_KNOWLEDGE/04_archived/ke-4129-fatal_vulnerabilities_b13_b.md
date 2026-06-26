---
module_id: KE-3974
title: 2. Fatal Vulnerabilities B13-B20
category: module_blueprint
ttl: permanent
---

# 2. Fatal Vulnerabilities B13-B20

2. Fatal Vulnerabilities B13-B20

| # | 致命漏洞 | 严重度 | 实现文件 | 约行数 | DD |
|---|---------|:---:|------|:---:|:---:|
| B13 | 兜底层自腐 | P0 | fallback_staleness_gate.py | ~150 | DD87 |
| B14 | 因果链断裂 | P0 | context_outcome_tracker.py | ~350 | DD88 |
| B15 | 单人无审查 | P0 | solo_dev_safety_net.py | ~300 | DD89 |
| B16 | 配置自毁 | P1 | config_safety_guard.py | ~200 | DD90 |
| B17 | 主机资源治理 | P1 | host_resource_governor.py | ~250 | DD91 |
| B18 | 嵌入版本锁 | P1 | embedding_version_lock.py | ~200 | DD92 |
| B19 | 上下文债务 | P1 | context_debt_score.py | ~200 | DD93 |
| B20 | LSG 模式逃逸 | P2 | lsg_pattern_tracker.py | ~250 | DD94 |
