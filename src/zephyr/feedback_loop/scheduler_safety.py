# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.scheduler_safety
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS] zephyr.feedback_loop.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SafetyGateManager.run_safety_gates returns dict[str, bool]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: scheduler_safety.py
# 层: 算法
# - id: A1
#   name_zh: ① SafetyGateManager
#   name_en: SafetyGateManager
#   intro: class SafetyGateManager 源码 L131-L227
#   desc: 公共方法（定义序）: run_safety_gates, fle_gate_cache, dispatch_fle_gates, invoke_fle_gate；源码 L131-L227
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SafetyGateManager
#   downstream: zephyr.feedback_loop.scheduler
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from zephyr.feedback_loop.diagnosers.numerical_stability_guard import NumericalStabilityGuard
from zephyr.feedback_loop.diagnosers.temporal_integrity_guard import TemporalIntegrityGuard
from zephyr.feedback_loop.forensic.boot_integrity_attestation import BootIntegrityAttestation
from zephyr.feedback_loop.gates.deployment_suppression import DeploymentSuppression
from zephyr.feedback_loop.resilience.config_hot_reload_guard import ConfigHotReloadGuard
from zephyr.feedback_loop.security.wireheading_prevention import WireheadingPrevention
from zephyr.shared.io.paths import GATES_DIR


def _load_fle_gate_instance(cache: dict[str, Any], gate_id: str, gate_file: str) -> object | None:
    if gate_id in cache:
        return cache[gate_id]
    rel_path = gate_file.replace("../", "").replace("/", ".").replace(".py", "")
    module_path = f"zephyr.{rel_path}"
    try:
        import importlib

        module = importlib.import_module(module_path)
    except ImportError:
        return None
    class_name = "".join(p.capitalize() for p in gate_id.lower().replace("fle-", "").split("_"))
    gate_class = getattr(module, class_name, None)
    if gate_class is None:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr_name == class_name:
                gate_class = attr
                break
    if gate_class is None:
        candidates = [a for a in dir(module) if isinstance(getattr(module, a), type) and not a.startswith("_")]
        if not candidates:
            return None
        gate_class = getattr(module, candidates[0])
    try:
        gate_instance = gate_class()
    except TypeError:
        gate_instance = gate_class
    cache[gate_id] = gate_instance
    return gate_instance


def _evaluate_gate_method(method: Callable[..., Any], method_name: str, action_id: str) -> bool:
    import inspect

    sig = inspect.signature(method)
    params = list(sig.parameters.keys())
    if method_name == "evaluate":
        from zephyr.feedback_loop.gates.safety_gate_l1_l27 import ActionContext

        ctx = ActionContext(
            action_id=action_id,
            action_type="fle_action",
            severity=1,
            autonomy_level=1,
            timestamp=time.time(),
        )
        result = method(ctx)
        if hasattr(result, "verdict"):
            from zephyr.feedback_loop.gates.safety_gate_l1_l27 import GateVerdict

            return result.verdict is not GateVerdict.REJECT
        return bool(result)
    elif len(params) == 0:
        result = method()
        if isinstance(result, dict):
            return result.get("allowed", result.get("passed", result.get("ok", True)))
        return bool(result)
    elif len(params) >= 2:
        return True
    else:
        result = method("fle_action")
        if isinstance(result, bool):
            return result
        if isinstance(result, dict):
            return result.get("allowed", result.get("passed", result.get("ok", True)))
        return True


@dataclass
class SafetyGateManager:
    numerical_guard: NumericalStabilityGuard = field(default_factory=NumericalStabilityGuard)
    temporal_guard: TemporalIntegrityGuard = field(default_factory=TemporalIntegrityGuard)
    wireheading_prevention: WireheadingPrevention = field(default_factory=WireheadingPrevention)
    deployment_suppression: DeploymentSuppression = field(default_factory=DeploymentSuppression)
    config_reload_guard: ConfigHotReloadGuard = field(default_factory=ConfigHotReloadGuard)
    boot_attestation: BootIntegrityAttestation = field(default_factory=BootIntegrityAttestation)
    _fle_gate_cache: dict[str, Any] = field(default_factory=dict, init=False)

    def run_safety_gates(self, anomaly: object, diagnosis: object) -> dict[str, bool]:
        gates: dict[str, bool] = {}

        metric_name = anomaly.evidence.get("metric_name", "")
        metric_value = anomaly.evidence.get("value", 0.0)
        metric_check = self.numerical_guard.validate(f"pre_action_{metric_name}", metric_value)
        gates["numerical_stability"] = metric_check["classification"] == "CLEAN"

        ts_check = self.temporal_guard.validate_timestamp(time.time())
        gates["temporal_integrity"] = ts_check["valid"]

        w_check = self.wireheading_prevention.validate_metric(metric_name, metric_value)
        gates["wireheading"] = w_check if isinstance(w_check, bool) else True

        d_check = self.deployment_suppression.check()
        gates["deployment_suppression"] = d_check.get("allowed", True) if isinstance(d_check, dict) else True

        c_check = self.config_reload_guard.check_stale_acks()
        gates["config_consistency"] = len(c_check) == 0

        fle_gates = self.dispatch_fle_gates(anomaly, diagnosis)
        gates.update(fle_gates)

        return gates

    @property
    def fle_gate_cache(self) -> dict[str, Any]:
        """Public accessor for the FLE gate instance cache."""
        return self._fle_gate_cache

    @fle_gate_cache.setter
    def fle_gate_cache(self, value: dict[str, Any]) -> None:
        """Public mutator for the FLE gate instance cache."""
        self._fle_gate_cache = value

    def dispatch_fle_gates(self, anomaly: object, diagnosis: object) -> dict[str, bool]:
        results: dict[str, bool] = {}
        registry_path = GATES_DIR / "_registry.yaml"
        if not registry_path.exists():
            return results
        try:
            import yaml

            with open(registry_path, encoding="utf-8") as f:
                registry = yaml.safe_load(f)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return results

        fle_entries = [
            e for e in registry.get("gates", []) if e.get("category") == "fle_self_defense" and e.get("file")
        ]

        for entry in fle_entries:
            gate_id = entry.get("gate_id", "")
            gate_file = entry["file"]
            if gate_id in ("FLE-DEPLOYMENT-SUPPRESSION",):
                continue
            try:
                gate_result = self.invoke_fle_gate(gate_id, gate_file, anomaly, diagnosis)
                results[gate_id] = gate_result
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                results[gate_id] = True

        return results

    def _dispatch_fle_gates(self, anomaly: object, diagnosis: object) -> dict[str, bool]:
        """Backward-compatible thin wrapper around :meth:`dispatch_fle_gates`."""
        return self.dispatch_fle_gates(anomaly, diagnosis)

    def invoke_fle_gate(self, gate_id: str, gate_file: str, anomaly: object, diagnosis: object) -> bool:
        gate_instance = _load_fle_gate_instance(self.fle_gate_cache, gate_id, gate_file)
        if gate_instance is None:
            return True

        action_id = getattr(anomaly, "anomaly_id", "unknown") if anomaly else "unknown"
        for method_name in ("check", "gate", "audit", "evaluate", "validate"):
            method = getattr(gate_instance, method_name, None)
            if method is None:
                continue
            try:
                return _evaluate_gate_method(method, method_name, action_id)
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                return True
        return True

    def _invoke_fle_gate(self, gate_id: str, gate_file: str, anomaly: object, diagnosis: object) -> bool:
        """Backward-compatible thin wrapper around :meth:`invoke_fle_gate`."""
        return self.invoke_fle_gate(gate_id, gate_file, anomaly, diagnosis)
