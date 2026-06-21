# [A_module] module_id=MOD-GOV_audit_logger | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    def __init__(self, config=None):
        self.config = config or {}
        self._entries = []

    def log(self, event_type, actor, target, details=None):
        entry = {
            'event_type': event_type,
            'actor': actor,
            'target': target,
            'details': details or {},
        }
        self._entries.append(entry)
        logger.info(f'AUDIT: {event_type} by {actor} on {target}')

    def query(self, filters=None):
        return self._entries

    def count(self):
        return len(self._entries)

def create_audit_logger(config=None):
    return AuditLogger(config=config)
