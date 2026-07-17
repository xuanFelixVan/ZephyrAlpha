# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.gov_audit.contracts
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.models
# [CONSUMERS] audit-orchestrator.*; pipeline_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 所有审计组件必须实现对应契约; 契约方法签名不可变
# [MODIFY-GUARD] 修改契约必须同步所有实现类
# [STABILITY] frozen
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] 违反契约抛ContractViolationError
# [TESTS] tests/audit-orchestrator/test_contracts.py
# [A_module] module_id=MOD-GOV_contracts | layer=module | stability=frozen | safety=H | ai_autonomy=immutable_core
# [TTL] permanent
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from zephyr.gov_audit.models import (
    AuditContext,
    AuditIssue,
    DiscoveryReport,
    GlobalAuditReport,
    OrchestratorStatus,
)

__all__ = [
    "AuditDiscoverer",
    "AuditIndexer",
    "AuditQuery",
    "AuditWriter",
    "ContractViolationError",
    "IntegrityChecker",
]


class ContractViolationError(Exception):
    error_code = "ZA-GV-0035"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class AuditDiscoverer(ABC):
    @abstractmethod
    def discover_changes(self, session_id: str) -> DiscoveryReport: ...

    @abstractmethod
    def get_changed_files(self, since: str | None = None) -> list[dict[str, Any]]: ...


class AuditIndexer(ABC):
    @abstractmethod
    def build_index(self, force: bool = False) -> dict[str, Any]: ...

    @abstractmethod
    def lookup(self, key: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def cold_start_cache(self) -> dict[str, Any]: ...


class AuditWriter(ABC):
    @abstractmethod
    def write_report(self, report: GlobalAuditReport, path: Path | None = None) -> Path: ...

    @abstractmethod
    def write_issue(self, issue: AuditIssue, report_dir: Path) -> Path: ...

    @classmethod
    def write(cls, **kwargs: Any) -> dict[str, Any]:
        """委托到全局 AuditWriter 单例（_GLOBAL_WRITER）写入核心审计链。

        设计意图（writer.py _GLOBAL_WRITER 注释"供 contracts.py 委托桥接使用"）：
        治理层调用此方法 → 自动路由到核心不可变 JSONL 哈希链，
        确保所有审计写入都进入核心链，不存在桩绕过或独立审计流逃逸。

        Args:
            **kwargs: 审计事件字段（agent_id, permission, resource 等）。

        Returns:
            包含 chain_hash 的 dict。

        Raises:
            ContractViolationError: 全局 writer 未初始化时。
        """
        from zephyr.gov_audit import writer as _writer_mod  # lazy import 避免循环依赖

        # 通过模块引用读取 _GLOBAL_WRITER（而非 from...import 值拷贝），
        # 确保 test 设置 writer_mod._GLOBAL_WRITER = writer 后类方法能看到最新值。
        global_writer = _writer_mod._GLOBAL_WRITER
        if global_writer is None:
            raise ContractViolationError(
                "Global AuditWriter not initialized — call writer.set_global_writer() first"
            )
        event: dict[str, Any] = dict(kwargs)
        event.setdefault("event_type", "rbac_decision")
        entry_hash = global_writer.write(event)
        return {"chain_hash": entry_hash, **kwargs}


class AuditQuery(ABC):
    @abstractmethod
    def get_status(self) -> OrchestratorStatus: ...

    @abstractmethod
    def get_history(self, limit: int = 50) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_issues(self, audit_id: str) -> list[AuditIssue]: ...


class IntegrityChecker(ABC):
    @abstractmethod
    def check(self, context: AuditContext) -> dict[str, Any]: ...

    @abstractmethod
    def verify_merkle(self, hour_key: str, expected_root: str) -> bool: ...
