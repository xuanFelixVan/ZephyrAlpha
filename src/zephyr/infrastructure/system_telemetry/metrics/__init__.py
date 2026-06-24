# [A_module] module_id=MOD-INF_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infra_ops/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.metrics
# [STABILITY] evolving
# [SAFETY] M
# [INVARIANTS] 蓝图读取事件MUST通过blueprint_metrics记录;输出JSONL格式
# [MODIFY-GUARD] blueprint_metrics.py; facade.py
# [CONSUMERS] facade.py; auto_bootstrap.py
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] JSONL写入失败→日志warning
# [TESTS] tests/unit/telemetry/
"""L12 · metrics — SLI/SLO 与业务指标流"""

__all__ = ["blueprint_metrics"]


class MetricType:
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"
    SUMMARY = "SUMMARY"
    TIMER = "TIMER"


class MetricSnapshot:
    def __init__(self, name="", value=0.0, metric_type=None, timestamp=None, tags=None):
        self.name = name
        self.value = value
        self.metric_type = metric_type
        self.timestamp = timestamp
        self.tags = tags or {}


class MetricsRegistry:
    def __init__(self):
        self._metrics = {}

    def register(self, name, metric_type, description=""):
        self._metrics[name] = {"type": metric_type, "description": description}

    def get(self, name):
        return self._metrics.get(name)


def get_registry():
    return MetricsRegistry()
