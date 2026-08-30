# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.orphan_detector
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
OrphanDetector — 孤儿检测器
=============================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
借鉴: K8s Orphan Pod Detection + Self-Improving Agent
持续监控孤儿率，驱动大脑向终极目标靠近。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: scanner 参数
#   fields: 参数 scanner（无注解）
#   code: orphan_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: registry 参数
#   fields: 参数 registry（无注解）
#   code: orphan_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① OrphanDetector
#   name_en: OrphanDetector
#   intro: 孤儿检测器——持续监控孤儿率，驱动大脑向终极目标靠近。
#   desc: 孤儿检测器——持续监控孤儿率，驱动大脑向终极目标靠近。；公共方法（定义序）: compute_orphan_rate, find_orphans, prioritize_orphans, report, is_goal…
#   inputs: scanner registry
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: OrphanDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field

from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.module_onboarding_scanner import ModuleOnboardingScanner, UnregisteredModule


@dataclass
class OrphanReport:
    total_modules: int = 0
    registered_modules: int = 0
    orphan_modules: int = 0
    orphan_rate: float = 1.0
    orphans_by_priority: dict[str, int] = field(default_factory=dict)
    orphans_by_package: dict[str, int] = field(default_factory=dict)
    top_priority_orphans: list[UnregisteredModule] = field(default_factory=list)
    goal_gap: float = 1.0


class OrphanDetector:
    """孤儿检测器——持续监控孤儿率，驱动大脑向终极目标靠近。"""

    def __init__(self, scanner: ModuleOnboardingScanner, registry: CapabilityRegistry) -> None:
        self._scanner = scanner
        self._registry = registry

    def compute_orphan_rate(self) -> float:
        orphans = self.find_orphans()
        all_modules = self._scanner.scan_filesystem()
        total = max(len(all_modules), 1)
        return len(orphans) / total

    def find_orphans(self) -> list[UnregisteredModule]:
        return self._scanner.diff_registered()

    def prioritize_orphans(self, orphans: list[UnregisteredModule] | None = None) -> list[UnregisteredModule]:
        if orphans is None:
            orphans = self.find_orphans()
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        return sorted(orphans, key=lambda x: priority_order.get(x.priority, 1))

    def report(self) -> OrphanReport:
        orphans = self.find_orphans()
        all_modules = self._scanner.scan_filesystem()
        total = len(all_modules)
        registered = self._registry.count()
        orphan_count = len(orphans)
        rate = orphan_count / max(total, 1)

        by_priority: dict[str, int] = {}
        by_package: dict[str, int] = {}
        for o in orphans:
            by_priority[o.priority] = by_priority.get(o.priority, 0) + 1
            pkg = o.discovery.package
            by_package[pkg] = by_package.get(pkg, 0) + 1

        prioritized = self.prioritize_orphans(orphans)

        return OrphanReport(
            total_modules=total,
            registered_modules=registered,
            orphan_modules=orphan_count,
            orphan_rate=rate,
            orphans_by_priority=by_priority,
            orphans_by_package=by_package,
            top_priority_orphans=prioritized[:10],
            goal_gap=1.0 - rate,
        )

    def is_goal_met(self) -> bool:
        return self.compute_orphan_rate() == 0.0
