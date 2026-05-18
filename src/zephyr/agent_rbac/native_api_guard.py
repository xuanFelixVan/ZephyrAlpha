# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.native_api_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""原生API守卫——阻止Agent绕过Python沙箱调用原生C/OS API."""
from __future__ import annotations

from typing import Any


BLOCKED_NATIVE_APIS = [
    "ctypes", "cffi", "CDLL", "WinDLL", "windll", "oledll",
    "cython", "pybind11", "native", "_ctypes",
    "mmap.", "munmap(", "mprotect(",
    "ptrace(", "fork(", "clone(", "vfork(",
    "syscall(", "ioctl(", "fcntl.",
    "socket.socket", "socket.connect",
    "os.system(", "os.popen(", "os.execv", "os.spawn",
    "subprocess.Popen", "subprocess.call", "subprocess.run",
    "multiprocessing.Process", "threading.Thread(target=os.system",
]


class NativeApiGuard:
    def __init__(self) -> None:
        self._violations: list[dict[str, Any]] = []

    def scan(self, code: str, source: str = "unknown") -> dict[str, Any]:
        lower = code.lower()
        matched = [api for api in BLOCKED_NATIVE_APIS if api.lower() in lower]

        if matched:
            self._violations.append({"source": source, "matched_apis": matched})

        return {
            "allowed": len(matched) == 0,
            "matched": matched,
            "source": source,
        }
