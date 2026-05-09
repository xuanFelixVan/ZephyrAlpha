"""
A2A 中心消息路由器 - 让多个 Agent 能够互相通信
"""

import threading
import time
from typing import Dict, Callable, List

class SharedMessageRouter:
    """共享消息路由器 - 支持多 Agent 间通信"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._running = True
    
    def register_handler(self, agent_id: str, handler: Callable):
        """为特定 Agent 注册消息处理器"""
        with self._lock:
            if agent_id not in self._handlers:
                self._handlers[agent_id] = []
            self._handlers[agent_id].append(handler)
    
    def route(self, from_agent: str, to_agent: str, content: str):
        """路由消息到目标 Agent"""
        with self._lock:
            handlers = self._handlers.get(to_agent, [])
            if handlers:
                for handler in handlers:
                    handler(content, {"from_agent": from_agent})
                return True
            else:
                print(f"⚠️  目标 Agent {to_agent} 未注册，消息无法投递")
                return False
    
    def list_agents(self):
        """列出已注册的 Agent"""
        with self._lock:
            return list(self._handlers.keys())

# 全局共享路由器
_shared_router = SharedMessageRouter()

def get_shared_router():
    """获取全局共享消息路由器"""
    return _shared_router
