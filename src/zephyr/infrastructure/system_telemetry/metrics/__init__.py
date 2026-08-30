# [A_module] module_id=MOD-INF-metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.metrics
# [STABILITY] evolving
# [SAFETY] M
# [INVARIANTS] 蓝图读取事件MUST通过blueprint_metrics记录;输出JSONL格式
# [MODIFY-GUARD] blueprint_metrics.py; facade.py
# [CONSUMERS] facade.py; auto_bootstrap.py
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] JSONL写入失败->日志warning
# [TESTS] tests/infrastructure/
# [TTL] permanent
"""
遥测 · metrics — SLI/SLO 与业务指标流

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① MetricsRegistry
#   name_en: MetricsRegistry
#   intro: class MetricsRegistry 源码 L79-L87
#   desc: 公共方法（定义序）: register, get；源码 L79-L87
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_registry
#   name_en: get_registry
#   intro: get_registry() 源码 L90-L91
#   desc: 源码 L90-L91
#   inputs: 无参数
#   outputs: MetricsRegistry
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: MetricsRegistry
#   name_en: MetricsRegistry
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: facade.py; auto_bootstrap.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

__all__ = ["blueprint_metrics"]


class MetricType:
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"
    SUMMARY = "SUMMARY"
    TIMER = "TIMER"


class MetricSnapshot:
    def __init__(
        self,
        name: str = "",
        value: float = 0.0,
        metric_type: str | None = None,
        timestamp: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> None:
        self.name = name
        self.value = value
        self.metric_type = metric_type
        self.timestamp = timestamp
        self.tags = tags or {}


class MetricsRegistry:
    def __init__(self) -> None:
        self._metrics: dict[str, dict[str, str]] = {}

    def register(self, name: str, metric_type: str, description: str = "") -> None:
        self._metrics[name] = {"type": metric_type, "description": description}

    def get(self, name: str) -> dict[str, str] | None:
        return self._metrics.get(name)


def get_registry() -> MetricsRegistry:
    return MetricsRegistry()
