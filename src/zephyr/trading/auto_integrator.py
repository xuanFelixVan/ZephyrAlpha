# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.auto_integrator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_auto_integrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AutoIntegrator — 自动接入器
=============================
蓝图: ARC-0001 §5.5
借鉴: Claude Code Self-Improving + K8s Admission Controller
临时启动 L3 高级模型分析是否接入。
"""

from dataclasses import dataclass, field
from datetime import datetime

from zephyr.trading.capability_card import CapabilityCard, CapabilityCategory
from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.module_onboarding_scanner import UnregisteredModule
from zephyr.shared.utils.time_utils import now_utc


@dataclass
class IntegrationAnalysis:
    module_path: str
    should_integrate: bool = False
    reason: str = ""
    suggested_layer: str = "local"
    suggested_priority: str = "P1"
    suggested_work_types: list[str] = field(default_factory=list)
    suggested_capability_card: CapabilityCard | None = None
    confidence: float = 0.0
    model_used: str = ""


class AutoIntegrator:
    """自动接入器——临时启动高级模型分析是否接入。

    借鉴:
      - Claude Code Self-Improving: 临时启动强推理分析
      - K8s Admission Controller: 接入前审查
    """

    def __init__(
        self,
        registry: CapabilityRegistry,
        max_daily_l3_activations: int = 10,
    ) -> None:
        self._registry = registry
        self._max_daily_l3 = max_daily_l3_activations
        self._daily_l3_count = 0
        self._last_reset_date = now_utc().strftime("%Y-%m-%d")

    def analyze_module(self, module: UnregisteredModule) -> IntegrationAnalysis:
        self._check_daily_reset()
        analysis = IntegrationAnalysis(module_path=module.discovery.module_path)

        disc = module.discovery
        has_class = disc.has_class
        has_funcs = disc.has_public_functions
        has_bp = disc.has_blueprint

        if not has_class and not has_funcs:
            analysis.should_integrate = False
            analysis.reason = "no public API (pure internal module)"
            analysis.confidence = 0.9
            return analysis

        analysis.should_integrate = True
        analysis.suggested_layer = module.suggested_layer
        analysis.suggested_priority = module.priority

        if has_bp:
            analysis.confidence = 0.85
            analysis.reason = "has blueprint definition, should integrate"
        elif has_class:
            analysis.confidence = 0.75
            analysis.reason = "has public class, likely needs integration"
        else:
            analysis.confidence = 0.6
            analysis.reason = "has public functions, may need integration"

        cap_id = f"{disc.package}-{disc.module_name}".replace("_", "-")
        category = self._infer_category(disc.package)
        analysis.suggested_capability_card = CapabilityCard(
            capability_id=cap_id,
            name=disc.module_name.replace("_", " ").title(),
            category=category,
            description=disc.docstring or f"Auto-discovered from {disc.package}/{disc.module_name}",
            tags=[disc.package, disc.module_name],
            priority=analysis.suggested_priority,
            runtime_plane="warm",
        )

        return analysis

    def should_integrate(self, analysis: IntegrationAnalysis) -> bool:
        return analysis.should_integrate and analysis.confidence >= 0.5

    def generate_card(self, analysis: IntegrationAnalysis) -> CapabilityCard | None:
        return analysis.suggested_capability_card

    def auto_register(self, analysis: IntegrationAnalysis) -> bool:
        if not self.should_integrate(analysis):
            return False
        card = self.generate_card(analysis)
        if card is None:
            return False
        if analysis.confidence >= 0.8:
            self._registry.register(card)
            return True
        return False

    def _check_daily_reset(self) -> None:
        today = now_utc().strftime("%Y-%m-%d")
        if today != self._last_reset_date:
            self._daily_l3_count = 0
            self._last_reset_date = today

    def _infer_category(self, package: str) -> CapabilityCategory:
        mapping = {
            "pipeline": CapabilityCategory.ORCHESTRATION,
            "orchestrator": CapabilityCategory.ORCHESTRATION,
            "vector-memory": CapabilityCategory.EMBEDDING,
            "gates": CapabilityCategory.SECURITY,
            "governance": CapabilityCategory.GOVERNANCE,
            "kb": CapabilityCategory.DATA,
            "llm-security": CapabilityCategory.SECURITY,
            "db": CapabilityCategory.DATA,
            "mcp": CapabilityCategory.INFRA,
            "core": CapabilityCategory.INFRA,
            "shared": CapabilityCategory.INFRA,
            "context-engine": CapabilityCategory.INFRA,
        }
        return mapping.get(package, CapabilityCategory.INFRA)
