---
blueprint_id: MOD-023
ssot_path: src/zephyr/observability/telemetry
status: active
conflict_note: |
  DUPLICATE: src/zephyr/infrastructure/runtime_integration/system-telemetry/ contains
  near-identical files (24 files). This manifest is the canonical (design-domain) version.
  The infrastructure copy is a migration remnant from l01-infrastructure.
  Planned action: merge infrastructure-only files (logs/, metrics_bridge.py) into
  observability/telemetry/, then delete infrastructure/system-telemetry/.
  See DM-248 for tracking.
---

# telemetry/ 文件清单（自动生成 2026-06-10）

总计: 23 个文件

- __init__.py
- _budget_telemetry_bridge.py
- _trace_bridge.py
- ai_behavior/__init__.py
- ai_behavior/event_sink.py
- alerts/__init__.py
- archive/__init__.py
- archive/cold_stub.py
- auto_bootstrap.py
- contract_metrics.py
- facade.py
- health/__init__.py
- health_aggregator.py
- health_probes.py
- metrics/__init__.py
- metrics/blueprint_metrics.py
- monitoring_stack/__init__.py
- profiles/__init__.py
- schema/__init__.py
- span_stub.py
- traces/__init__.py
- traces/span_stub.py
- watchdog.py
