# [A_module] module_id=MOD-GOV_bridges | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [TTL] permanent
"""
Drift Detector — MOD-INF-023
=============================
Agent行为漂移检测：签名一致性 + 输出分布监控.

v1.0.0+: 统一入口已迁移至 zephyr.governance.drift_detection（B 轨平台能力）。
本子包作为向后兼容层保留, 内部代理到主模块。

迁移路径:
  旧: from zephyr.governance.drift_detection import events, rollback_bridge
  新: from zephyr.governance.drift_detector_core.drift_engine import scan
      from zephyr.governance.drift_detector_core.reconciler import AutoFixer
"""

import warnings

warnings.warn(
    "zephyr.governance.drift_detection 已迁移至 zephyr.governance.drift_detector_core (v1.0.0)。"
    "请更新 import 路径。本兼容层将在 2 个版本后移除。",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from zephyr.governance.drift_detection.ai_construction_detectors import AIConstructionDetectors
    from zephyr.governance.drift_detection.drift_engine import scan
    from zephyr.governance.drift_detection.drift_models import DriftEvent, DriftState
    from zephyr.governance.drift_detection.reconciler import AutoFixer
    from zephyr.governance.drift_detection.state_machine import DriftStateMachine
except ImportError:
    pass

__all__ = ['drift_bridge']

__version__ = "1.0.0"
__module_id__ = "MOD-INF-023"
