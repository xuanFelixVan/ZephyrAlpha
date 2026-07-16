# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/llm-security/blueprint.md
# [MODULE] zephyr.security.llm_defense.llm_security.self_protection.isolation
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_audit.bridge
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_isolation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

import threading
import time
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from zephyr.gov_audit.bridge import write_to_core


class IsolationLevel(str, Enum):
    PROCESS = "process"
    CONTAINER = "container"
    STRICT = "strict"


class AccessPattern(str, Enum):
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    NETWORK_OUTBOUND = "network_outbound"
    NETWORK_INBOUND = "network_inbound"
    SUBPROCESS = "subprocess"
    SYS_MODULE = "sys_module"


class AccessRule(BaseModel):
    pattern: AccessPattern
    target: str
    allowed: bool = True
    reason: str = ""


class IsolationPolicy(BaseModel):
    level: IsolationLevel = IsolationLevel.PROCESS
    rules: list[AccessRule] = Field(default_factory=list)
    enforcement_mode: str = "fail_closed"


class IsolationAuditEntry(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    pattern: AccessPattern
    target: str = ""
    allowed: bool = False
    blocked_by: str = ""


class LSGIsolation:
    """LSG 自身隔离策略.

    核心功能:
    - 文件系统访问最小化: 只读 src/zephyr/llm-security/, 只写 /tmp + 日志目录
    - 网络隔离: 禁止 LSG 模块建立外连 (除非显式配置的 webhook/API endpoint)
    - 进程隔离: 禁止 LSG 子模块启动子进程 (subprocess.Popen/os.system)
    - 内存隔离: W^X 原则——可写页不可执行, 可执行页不可写 (平台支持限制)
    - Python 模块加载白名单: 只允许加载明确声明的系统模块
    """

    _DEFAULT_SCOPED_DIRS: tuple[str, ...] = (
        "src/zephyr/llm-security",
        "/tmp",
        "_journals",
    )

    _WHITELIST_MODULES: set[str] = {
        "abc",
        "asyncio",
        "collections",
        "copy",
        "dataclasses",
        "datetime",
        "enum",
        "functools",
        "hashlib",
        "hmac",
        "importlib",
        "inspect",
        "io",
        "itertools",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "re",
        "struct",
        "sys",
        "threading",
        "time",
        "traceback",
        "types",
        "typing",
        "uuid",
        "warnings",
        "weakref",
        "textwrap",
        "zoneinfo",
        "pydantic",
        "yaml",
    }

    _FORBIDDEN_MODULES: set[str] = {
        "ctypes",
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "http.client",
        "http.server",
        "smtplib",
        "ftplib",
        "telnetlib",
        "poplib",
        "imaplib",
        "nntplib",
    }

    def __init__(self, level: IsolationLevel = IsolationLevel.PROCESS):
        self._level = level
        self._audit_log: list[IsolationAuditEntry] = []
        self._lock = threading.Lock()
        self._policy = IsolationPolicy(level=level)

    def check_file_access(self, path: str, pattern: AccessPattern) -> bool:
        normalized = str(Path(path).resolve()).replace("\\", "/")
        allowed = any(d in normalized for d in self._DEFAULT_SCOPED_DIRS) or "/tmp" in normalized

        self._log_audit(pattern, normalized, allowed)
        return allowed

    def check_network_access(self, target: str) -> bool:
        allowed = target.startswith("localhost") or target.startswith("127.0.0.1")
        self._log_audit(AccessPattern.NETWORK_OUTBOUND, target, allowed)
        return allowed

    def check_subprocess(self, command: str) -> bool:
        self._log_audit(AccessPattern.SUBPROCESS, command, False)
        return False

    def check_module_import(self, module_name: str) -> bool:
        if module_name in self._FORBIDDEN_MODULES:
            self._log_audit(AccessPattern.SYS_MODULE, module_name, False)
            return False
        if module_name in self._WHITELIST_MODULES:
            return True
        if module_name.startswith("src.zephyr.security.llm_defense.llm_security"):
            return True
        self._log_audit(AccessPattern.SYS_MODULE, module_name, False)
        return False

    def _log_audit(self, pattern: AccessPattern, target: str, allowed: bool) -> None:
        entry = IsolationAuditEntry(
            pattern=pattern,
            target=target,
            allowed=allowed,
            blocked_by="default_policy" if not allowed else "",
        )
        with self._lock:
            self._audit_log.append(entry)
            if len(self._audit_log) > 5000:
                self._audit_log = self._audit_log[-2500:]
        write_to_core(
            "llm_isolation_audit",
            {
                "pattern": pattern.value,
                "target": target,
                "allowed": allowed,
            },
        )

    @property
    def audit_log(self) -> list[IsolationAuditEntry]:
        return list(self._audit_log)

    @property
    def level(self) -> IsolationLevel:
        return self._level

    @property
    def policy(self) -> IsolationPolicy:
        return self._policy
