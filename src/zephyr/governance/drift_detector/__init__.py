"""
Drift Detector — MOD-INF-023
=============================
Agent行为漂移检测：签名一致性 + 输出分布监控.

v1.0.0+: 统一入口已迁移至 zephyr.drift_detector（B 轨平台能力）。
本子包作为向后兼容层保留, 内部代理到主模块。

迁移路径:
  旧: from zephyr.governance.drift_detector import events, rollback_bridge
  新: from zephyr.drift_detector.drift_engine import scan
      from zephyr.drift_detector.reconciler import AutoFixer
"""

import warnings

warnings.warn(
    "zephyr.governance.drift_detector 已迁移至 zephyr.drift_detector (v1.0.0)。"
    "请更新 import 路径。本兼容层将在 2 个版本后移除。",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from zephyr.drift_detector.drift_engine import AIConstructionDetectors, scan
    from zephyr.drift_detector.reconciler import AutoFixer
    from zephyr.drift_detector.state_machine import DriftStateMachine
    from zephyr.drift_detector.drift_models import DriftEvent, DriftState
except ImportError:
    pass

__all__ = ['events', 'rollback_bridge']

__version__ = "1.0.0"
__module_id__ = "MOD-INF-023"