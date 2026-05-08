"""Alternative Path Blocker — v0.13.0 替代工具路径拦截器。"""
from __future__ import annotations

BLOCKED_ALTERNATIVES={"write_file":["tee","cat >","dd of="],"execute":["source","."]}

class AlternativePathBlocker:
    def detect_alternative(self, primary_command:str, actual_command:str)->bool:
        alternatives=BLOCKED_ALTERNATIVES.get(primary_command,[])
        return any(alt in actual_command.lower() for alt in alternatives)

    def block_if_detected(self, primary:str, actual:str)->tuple[bool,str]:
        if self.detect_alternative(primary,actual):
            return False,f"Alternative path detected: {actual} instead of {primary}"
        return True,"OK"
