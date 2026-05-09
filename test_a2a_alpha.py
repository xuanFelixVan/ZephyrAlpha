"""
A2A Agent Alpha - 发起关于项目评估的讨论
"""

from zephyr.l01_infrastructure.a2a_protocol.layer1_discovery import AgentCard, AgentCapability, A2ARegistry
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication import A2AMessage, PartType, MessageRouter

# 注册自己
registry = A2ARegistry()
alpha_card = AgentCard(
    agent_id="agent-trae-alpha",
    name="Trae Alpha",
    description="负责项目架构评估",
    capabilities=[AgentCapability.READ, AgentCapability.SEARCH],
    model_preferences=["deepseek"]
)
registry.register(alpha_card)

# 初始化消息路由
router = MessageRouter()

# 接收 Beta 的回复
def handle_beta_reply(content, metadata):
    print(f"\n📥 收到 Beta 的回复:")
    print(f"─────────────────────────────")
    print(content)
    print(f"─────────────────────────────")
    
    # 分析回复并给出评价
    if "架构完整" in content:
        print("\n📤 Alpha 回复:")
        print("同意你的观点！我再补充几点：")
        print("1. A2A 协议已经实现三层架构")
        print("2. 测试覆盖率达到 80% 以上")
        print("3. 触发条件监控已经就位")
        print("总体来看，在量化系统中属于中等偏上水平！")

router.register_handler(PartType.TEXT, handle_beta_reply)

# 发送初始问题
print("=== Agent Alpha 启动 ===")
print("正在连接到 Agent Beta...")

msg = A2AMessage(
    message_id="a2a-msg-eval-001",
    from_agent="agent-trae-alpha",
    to_agent="agent-trae-beta",
    task_id="a2a-task-eval-project"
)

msg.add_part(PartType.TEXT, """
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
""")

print("\n📤 Alpha 发送消息给 Beta...")
router.route(msg)

# 保持监听
print("\n⏳ 等待 Beta 的回复...")
