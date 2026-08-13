# [A_module] module_id=MOD-CMP-bridges | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [TTL] permanent
"""


Audit Trail — MOD-INF-020

不可变审计追踪：所有Agent操作记录 + 异常检测。
G-CT-001 (RBAC->Audit), G-CT-002 (Audit->Rollback).

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: gov_audit.bridges 审计桥接类符号（类对象）
#   fields: AnomalyDetector/AnomalyEvent/AuditWriter/DriftBridge/BridgeResult/AuditDelegationBridge/AuditFeedbackBridge/AuditTieredStorageBridge/AuditTrustBridge
#   code: zephyr.gov_audit.bridges.audit_*（bridges/__init__.py L11-17）
# - id: I2
#   name: 子模块名惰性加载请求（str）
#   fields: name——__all__ 里的子模块名（如 audit_anomaly），实际位于 zephyr.gov_audit.bridges.*
#   code: __getattr__(name)（bridges/__init__.py L42）
# 层: 算法
# - id: A1
#   name_zh: ① 审计桥接符号包级再导出聚合
#   name_en: __init__（模块级 import + __all__）
#   intro: 把7个桥接实现里的9个类汇成 audit_trail.bridges 统一入口
#   desc: 7条 from-import（L11-17）+ __all__ 15项导出清单（L19-36，含6个子模块名）；MOD-INF-020 不可变审计追踪的桥接门面
#   inputs: I1
#   outputs: 统一审计桥接API命名空间
# - id: A2
#   name_zh: ② 子模块 PEP 562 惰性加载
#   name_en: __getattr__
#   intro: 访问子模块名时才 import 对应 gov_audit.bridges.* 模块并缓存
#   desc: importlib.import_module(f"zephyr.gov_audit.bridges.{name}")（L48）→ globals()[name] 缓存（L49）→ ImportError 转 AttributeError（L51-52）
#   inputs: I2
#   outputs: 惰性加载的子模块对象
#   invariant: 同一子模块仅加载一次，缓存于 globals()
# 层: 输出
# - id: O1
#   name_zh: 审计桥接公共API面
#   name_en: __all__（15项）
#   intro: 对外暴露异常检测/审计写入/委托/漂移/反馈/分层存储/信任全套桥接类
#   downstream: 无下游/内部使用（仓内无 from zephyr.compliance.audit_trail 消费者；canonical 实现位于 zephyr.gov_audit.bridges）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> O1
# A2 --> O1
"""

from zephyr.gov_audit.bridges.audit_anomaly import AnomalyDetector, AnomalyEvent
from zephyr.gov_audit.bridges.audit_contracts import AuditWriter
from zephyr.gov_audit.bridges.audit_delegation_bridge import AuditDelegationBridge
from zephyr.gov_audit.bridges.audit_drift_bridge import BridgeResult, DriftBridge
from zephyr.gov_audit.bridges.audit_feedback_bridge import AuditFeedbackBridge
from zephyr.gov_audit.bridges.audit_tiered_storage_bridge import AuditTieredStorageBridge
from zephyr.gov_audit.bridges.audit_trust_bridge import AuditTrustBridge

__all__ = [
    "AnomalyDetector",
    "AnomalyEvent",
    "AuditDelegationBridge",
    "AuditFeedbackBridge",
    "AuditTieredStorageBridge",
    "AuditTrustBridge",
    "AuditWriter",
    "BridgeResult",
    "DriftBridge",
    "audit_anomaly",
    "audit_contracts",
    "audit_delegation_bridge",
    "audit_drift_bridge",
    "audit_feedback_bridge",
    "audit_tiered_storage_bridge",
    "audit_trust_bridge",
]

__version__ = "0.1.0"
__module_id__ = "MOD-INF-020"


def __getattr__(name: str):
    # __all__ 里的子模块名（如 audit_anomaly）实际位于 zephyr.gov_audit.bridges.*，
    # 用 __getattr__ 按需 lazy 加载（替代已删除的 `from . import spec_auditor`）
    import importlib

    try:
        mod = importlib.import_module(f"zephyr.gov_audit.bridges.{name}")
        globals()[name] = mod
        return mod
    except ImportError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
