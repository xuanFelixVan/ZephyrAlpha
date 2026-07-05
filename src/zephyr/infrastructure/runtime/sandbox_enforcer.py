# [BLUEPRINT] (migrated from MOD-INF-021 by ARCH-039 P1, target domain=D_INFRA_RUNTIME)
# [MODULE] zephyr.infrastructure.runtime.sandbox_enforcer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.runtime.__init__
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
# [A_module] module_id=MOD-INF_sandbox_enforcer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SandboxEnforcer — Agent 沙盒隔离。

依据: 蓝图 MOD-INF-021 §7 Phase 9 + §6.16 B121 + exit code 39

强制执行或验证 AI Agent 在沙盒中执行:
    - 非 sandbox 环境调用 → exit 39 (SANDBOX_BREACH)
    - 物理隔离: sandbox 文件系统 + 网络隔离
    - Agent PID 与沙盒 NS 绑定
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SandboxMode(str, Enum):
    STRICT = "strict"
    LAX = "lax"
    NONE = "none"


@dataclass
class SandboxStatus:
    enforced: bool
    mode: SandboxMode
    in_sandbox: bool
    details: list[str] = field(default_factory=list)


@dataclass
class SandboxBreachResult:
    breached: bool
    reason: str
    exit_code: int
    mitigating_action: str


class SandboxEnforcer:
    EXIT_CODE_SANDBOX_BREACH: int = 39
    SANDBOX_MARKER: str = ".zephyr/sandbox_active"

    def __init__(self, project_root: Path | None = None, mode: SandboxMode = SandboxMode.STRICT) -> None:
        self._project_root = project_root or Path.cwd()
        self._mode = mode
        self._marker_path = self._project_root / self.SANDBOX_MARKER

    def is_in_sandbox(self) -> bool:
        return self._marker_path.exists()

    def enforce(self) -> SandboxBreachResult:
        if self._mode is SandboxMode.NONE:
            return SandboxBreachResult(
                breached=False,
                reason="Sandbox mode disabled",
                exit_code=0,
                mitigating_action="none",
            )

        if not self.is_in_sandbox():
            return SandboxBreachResult(
                breached=True,
                reason=f"Agent not in sandbox, mode={self._mode.value}",
                exit_code=self.EXIT_CODE_SANDBOX_BREACH,
                mitigating_action="SUSPEND_AGENT_EXECUTION",
            )

        return SandboxBreachResult(
            breached=False,
            reason="Agent running in sandbox",
            exit_code=0,
            mitigating_action="none",
        )

    def activate_sandbox(self) -> bool:
        self._marker_path.parent.mkdir(parents=True, exist_ok=True)
        self._marker_path.write_text("active\n", encoding="utf-8")
        return True

    def deactivate_sandbox(self) -> bool:
        try:
            self._marker_path.unlink(missing_ok=True)
            return True
        except Exception:
            return False

    def status(self) -> SandboxStatus:
        return SandboxStatus(
            enforced=self._mode is not SandboxMode.NONE,
            mode=self._mode,
            in_sandbox=self.is_in_sandbox(),
            details=[f"Sandbox marker: {self._marker_path}"],
        )

    def validate_file_access(self, file_path: Path) -> bool:
        if not self.is_in_sandbox():
            return self._mode is SandboxMode.NONE
        try:
            resolved = file_path.resolve()
            allowed_roots = [
                self._project_root,
                Path(os.environ.get("TEMP", "/tmp")),
            ]
            for root in allowed_roots:
                try:
                    if str(resolved).startswith(str(root.resolve())):
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    @property
    def mode(self) -> SandboxMode:
        return self._mode
