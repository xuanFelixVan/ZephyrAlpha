# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.construction.demo_a2a_chat
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.construction.check_statuses
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
A2A 多 Agent 聊天演示 - Alpha 和 Beta 讨论项目评估
"""

import threading
import time
from collections.abc import Callable


# 共享消息路由器
class SharedMessageRouter:
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}
        self._lock = threading.Lock()

    def register_handler(self, agent_id: str, handler: Callable):
        with self._lock:
            if agent_id not in self._handlers:
                self._handlers[agent_id] = []
            self._handlers[agent_id].append(handler)

    def route(self, from_agent: str, to_agent: str, content: str):
        with self._lock:
            handlers = self._handlers.get(to_agent, [])
            if handlers:
                for handler in handlers:
                    handler(content, {"from_agent": from_agent})
                return True
            else:
                print(f"⚠️  目标 Agent {to_agent} 未注册")
                return False


# Agent Alpha
class AgentAlpha:
    def __init__(self, router: SharedMessageRouter):
        self.agent_id = "agent-trae-alpha"
        self.name = "Trae Alpha"
        self.router = router
        self.router.register_handler(self.agent_id, self.handle_message)

    def handle_message(self, content, metadata):
        print(f"\n{self.name} 收到消息:")
        print("─────────────────────────────")
        print(content)
        print("─────────────────────────────")

        if "架构完整" in content or "综合评分" in content:
            print(f"\n{self.name} 正在回复...")
            reply = """
同意你的观点！我再补充几点：

1. A2A 协议已经实现三层架构（发现、通信、协调）
2. 集成测试 21 个全部通过，单元测试覆盖率逐步提升
3. 触发条件监控已经就位，等待多 Agent 场景激活
4. 安全防护考虑周全，支持 OWASP ASI07 等标准

总体来看，在量化系统中属于中等偏上水平！随着更多实际场景验证，评分有望进一步提升。
"""
            time.sleep(1)  # 模拟思考时间
            self.send_message("agent-trae-beta", reply)

    def send_message(self, to_agent, content):
        print(f"\n📤 {self.name} 发送消息给 Trae Beta...")
        self.router.route(self.agent_id, to_agent, content)

    def start_discussion(self):
        initial_message = """
你好 Beta！我们来讨论一下当前这个 ZephyrAlpha 项目。

从量化系统的角度评估，你认为这个项目处于什么水平？

评估维度可以参考：
1. 架构完整性
2. 代码质量
3. 测试覆盖率
4. 功能完备度
5. 安全性
6. 可扩展性

期待你的专业分析！
"""
        self.send_message("agent-trae-beta", initial_message)


# Agent Beta
class AgentBeta:
    def __init__(self, router: SharedMessageRouter):
        self.agent_id = "agent-trae-beta"
        self.name = "Trae Beta"
        self.router = router
        self.router.register_handler(self.agent_id, self.handle_message)

    def handle_message(self, content, metadata):
        print(f"\n{self.name} 收到消息:")
        print("─────────────────────────────")
        print(content)
        print("─────────────────────────────")

        if "评估" in content or "水平" in content:
            print(f"\n{self.name} 正在分析并回复...")
            reply = """
你好 Alpha！很高兴和你讨论这个话题。

从量化系统的角度评估 ZephyrAlpha 项目：

📊 架构完整性：★★★★☆ (4/5)
- A2A 协议实现了三层架构（发现、通信、协调）
- 模块化设计清晰
- 但多协议网关还在规划阶段

📝 代码质量：★★★★☆ (4/5)
- Pydantic 类型安全
- Ruff 代码检查
- 文档覆盖率较高

🧪 测试覆盖率：★★★☆☆ (3/5)
- 集成测试 21 个通过
- 单元测试覆盖核心模块
- 但端到端测试还需完善

⚡ 功能完备度：★★★☆☆ (3/5)
- A2A 核心功能已实现
- 触发条件监控就绪
- 等待实际场景激活

🔒 安全性：★★★★☆ (4/5)
- OWASP ASI07 防护
- JWT 身份验证
- 死锁/活锁防护

📈 可扩展性：★★★★☆ (4/5)
- 插件化设计
- CapabilityRegistry 自动发现
- 易于添加新 Agent

📊 综合评分：★★★★☆ (约 3.8/5)

总体评价：在同类量化系统中属于**中等偏上水平**，核心功能完整，安全性考虑周全，但还需要更多实际场景验证。

你怎么看？
"""
            time.sleep(0.5)  # 模拟思考时间
            self.send_message("agent-trae-alpha", reply)

    def send_message(self, to_agent, content):
        print(f"\n📤 {self.name} 发送消息给 Trae Alpha...")
        self.router.route(self.agent_id, to_agent, content)


def main():
    print("=== A2A 多 Agent 聊天演示 ===")
    print("Alpha 和 Beta 将讨论 ZephyrAlpha 项目评估\n")

    # 创建共享路由器
    router = SharedMessageRouter()

    # 创建两个 Agent
    alpha = AgentAlpha(router)
    beta = AgentBeta(router)

    print("✅ Agent Alpha 已就绪")
    print("✅ Agent Beta 已就绪")
    print("\n🚀 Alpha 发起讨论...\n")

    # Alpha 发起讨论
    alpha.start_discussion()

    # 等待对话完成
    time.sleep(8)

    print("\n🎉 讨论结束！")


if __name__ == "__main__":
    main()
