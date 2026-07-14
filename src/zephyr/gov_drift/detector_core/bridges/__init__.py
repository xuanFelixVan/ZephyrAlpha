# [A_module] module_id=MOD-GOV_DRIFT_bridges | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_DRIFT_bridges | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [TTL] permanent
"""
Drift Detector — MOD-GOV_DRIFT_bridges
=============================
Agent行为漂移检测：签名一致性 + 输出分布监控.

bridges/ 是向后兼容垫片，位于 drift_detector_core/ 下。
当前真源：zephyr.gov_drift（66 文件主包，ARCH-042 裁定 T_soft=120 合规）。
本垫片代理到 drift_detection，请直接从 drift_detection 导入。

正确导入路径:
  from zephyr.gov_drift.drift_engine import scan
  from zephyr.gov_drift.reconciler import AutoFixer
  from zephyr.gov_drift.state_machine import DriftStateMachine
"""

import warnings

warnings.warn(
    "zephyr.gov_drift.detector_core.bridges 已废弃，请直接从 zephyr.gov_drift 导入。"
    "本兼容层将在 2 个版本后移除。",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from zephyr.gov_drift.ai_construction_detectors import AIConstructionDetectors
    from zephyr.gov_drift.drift_engine import scan
    from zephyr.gov_drift.drift_models import DriftEvent, DriftState
    from zephyr.gov_drift.reconciler import AutoFixer
    from zephyr.gov_drift.state_machine import DriftStateMachine
except ImportError:
    pass

__all__ = ['drift_bridge']

__version__ = "1.0.0"
__module_id__ = "MOD-GOV_DRIFT_bridges"
