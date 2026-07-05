# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [TTL] permanent
"""
Drift Detector — MOD-INF-023
=============================
Agent行为漂移检测：签名一致性 + 输出分布监控.

bridges/ 是向后兼容垫片，位于 drift_detector_core/ 下。
当前真源：zephyr.governance.drift_detection（66 文件主包，ARCH-042 裁定 T_soft=120 合规）。
本垫片代理到 drift_detection，请直接从 drift_detection 导入。

正确导入路径:
  from zephyr.governance.drift_detection.drift_engine import scan
  from zephyr.governance.drift_detection.reconciler import AutoFixer
  from zephyr.governance.drift_detection.state_machine import DriftStateMachine
"""

import warnings

warnings.warn(
    "zephyr.governance.drift_detector_core.bridges 已废弃，请直接从 zephyr.governance.drift_detection 导入。"
    "本兼容层将在 2 个版本后移除。",
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
