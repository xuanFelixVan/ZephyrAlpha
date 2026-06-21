# [A_module] module_id=MOD-INF_events | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-094 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.shared_services.events
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] 
# [ERROR_CONTRACT] 
# [TESTS] 
"""core.events — auto-generated package init."""
from . import event_reactor
from . import event_store
from . import hook_dispatcher

__all__ = ['event_bus', 'event_reactor', 'event_store', 'hook_dispatcher']

class DriftEvent:
    def __init__(self, event_id='', drift_type='', severity='medium', description='', timestamp=None, source='', target=''):
        self.event_id = event_id
        self.drift_type = drift_type
        self.severity = severity
        self.description = description
        self.timestamp = timestamp
        self.source = source
        self.target = target

class DriftType:
    SCHEMA = 'SCHEMA'
    CONTRACT = 'CONTRACT'
    BEHAVIORAL = 'BEHAVIORAL'
    CONFIGURATION = 'CONFIGURATION'
    DEPENDENCY = 'DEPENDENCY'
    PERFORMANCE = 'PERFORMANCE'
    SECURITY = 'SECURITY'
    UNKNOWN = 'UNKNOWN'

class DriftState:
    DETECTED = 'DETECTED'
    ANALYZING = 'ANALYZING'
    FIXING = 'FIXING'
    VERIFIED = 'VERIFIED'
    ESCALATED = 'ESCALATED'
    RESOLVED = 'RESOLVED'
    IGNORED = 'IGNORED'
