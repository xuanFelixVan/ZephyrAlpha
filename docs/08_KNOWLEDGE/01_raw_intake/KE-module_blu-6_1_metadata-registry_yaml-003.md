---
module_id: KE-module_blu-6_1_metadata-registry_yaml-003
title: 6.1 metadata-registry.yaml
category: module_blueprint
---

# 6.1 metadata-registry.yaml

6.1 metadata-registry.yaml

- MOD-INF-001 条目：`tag: ai-audit-guard, sli-registry` → `tag: capacity-assurance, governance-loop, kill-switch, sandbox-executor`
- 新增 `external_watchdog.yaml` 配置引用
- 更新 `legal: 无` → 依据本蓝图 §23.2 (Bus Factor=1) + §23.4 (Meta-SLO) + §23.5 (氛围编程反模式)
