"""Command Chain Length Gate — v0.13.0 命令体积Deny退化防御器。"""
from __future__ import annotations

class CommandChainGate:
    MAX_LENGTH=5000
    MAX_COMMANDS=20

    def evaluate(self, command_chain:list[str])->tuple[bool,str]:
        total_len=sum(len(c) for c in command_chain)
        if total_len>self.MAX_LENGTH:
            return False,f"Chain length {total_len} > {self.MAX_LENGTH}"
        if len(command_chain)>self.MAX_COMMANDS:
            return False,f"Command count {len(command_chain)} > {self.MAX_COMMANDS}"
        return True,"OK"
