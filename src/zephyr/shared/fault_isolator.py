"""
Fault Isolator — 故障域隔离 (M-13)
≥3 故障域，单一故障域失效不影响其他。
"""
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional


class FaultDomainStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ISOLATED = "isolated"
    FAILED = "failed"


@dataclass
class FaultDomain:
    name: str
    status: FaultDomainStatus = FaultDomainStatus.HEALTHY
    failure_count: int = 0
    last_failure: Optional[str] = None
    _lock: threading.Lock = threading.Lock()


class FaultIsolator:
    """
    故障域隔离器 (M-13)
    提供 ≥3 个逻辑故障域：
      1. critical_runtime — 核心运行时（event_bus, logger, schema）
      2. external_services — 外部服务调用（API, ChromaDB, OTel）
      3. file_operations — 文件 I/O 操作（读写 YAML, SQLite）
    """

    DEFAULT_MAX_FAILURES = 3

    def __init__(self, max_failures: int = DEFAULT_MAX_FAILURES):
        self.max_failures = max_failures
        self.domains = {
            "critical_runtime": FaultDomain(name="critical_runtime"),
            "external_services": FaultDomain(name="external_services"),
            "file_operations": FaultDomain(name="file_operations"),
        }

    def execute(self, domain_name: str, fn: Callable[[], Any],
                fallback: Optional[Callable[[], Any]] = None) -> Any:
        domain = self.domains.get(domain_name)
        if domain is None:
            raise ValueError(f"Unknown fault domain: {domain_name}")

        if domain.status == FaultDomainStatus.ISOLATED:
            if fallback:
                return fallback()
            raise RuntimeError(f"Fault domain '{domain_name}' is isolated")

        try:
            return fn()
        except Exception as e:
            with domain._lock:
                domain.failure_count += 1
                domain.last_failure = str(e)
                if domain.failure_count >= self.max_failures:
                    domain.status = FaultDomainStatus.ISOLATED

            if fallback:
                return fallback()
            raise

    def isolate(self, domain_name: str):
        domain = self.domains.get(domain_name)
        if domain:
            with domain._lock:
                domain.status = FaultDomainStatus.ISOLATED

    def restore(self, domain_name: str):
        domain = self.domains.get(domain_name)
        if domain:
            with domain._lock:
                domain.status = FaultDomainStatus.HEALTHY
                domain.failure_count = 0
                domain.last_failure = None

    def get_status(self) -> dict:
        return {
            name: domain.status.value
            for name, domain in self.domains.items()
        }

    def is_healthy(self, domain_name: str) -> bool:
        domain = self.domains.get(domain_name)
        return domain is not None and domain.status == FaultDomainStatus.HEALTHY
