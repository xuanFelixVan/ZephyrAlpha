# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.construction.demo_a2a_coordination
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.integration.__init__
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
A2A 协议协调任务演示

场景：架构师 Agent 需要完成一个完整的功能开发
- 任务分解：需求分析 → 架构设计 → 代码实现 → 测试编写 → 部署
- 多个 Agent 协同完成
- Supervisor 协调分配任务
"""

from zephyr.integration.agent_communication.layer1_discovery import A2ARegistry, AgentCapability, AgentCard
from zephyr.integration.agent_communication.layer2_communication import (
    A2AStateMachine,
    A2ATask,
    A2ATaskStatus,
)
from zephyr.integration.agent_communication.layer3_coordination import DeadlockGuard, Supervisor


def setup_multi_agent_environment() -> tuple[A2ARegistry, AgentCard, AgentCard, AgentCard]:
    """设置多 Agent 环境：架构师、开发者、测试员"""
    registry = A2ARegistry()

    # 架构师 Agent
    architect = AgentCard(
        agent_id="agent-architect",
        name="架构师 AI",
        description="负责需求分析和架构设计",
        capabilities=[AgentCapability.READ, AgentCapability.SEARCH],
        model_preferences=["deepseek"],
    )

    # 开发者 Agent
    developer = AgentCard(
        agent_id="agent-developer",
        name="开发者 AI",
        description="负责代码实现",
        capabilities=[AgentCapability.WRITE, AgentCapability.BASH],
        model_preferences=["deepseek"],
    )

    # 测试员 Agent
    tester = AgentCard(
        agent_id="agent-tester",
        name="测试员 AI",
        description="负责测试编写和验证",
        capabilities=[AgentCapability.READ, AgentCapability.GREP],
        model_preferences=["deepseek"],
    )

    registry.register(architect)
    registry.register(developer)
    registry.register(tester)

    return registry, architect, developer, tester


def demo_task_coordination() -> None:
    """演示 A2A 任务协调流程"""
    print("=== A2A 协议协调任务演示 ===\n")

    # 1. 设置环境
    registry, architect, developer, tester = setup_multi_agent_environment()
    print(f"已注册 Agent: {[a.agent_id for a in registry.discover()]}\n")

    # 2. 初始化 Supervisor（协调器）
    supervisor = Supervisor()
    deadlock_guard = DeadlockGuard()

    print("🚀 Supervisor 开始协调任务...\n")

    # 3. 架构师创建任务并提交给 Supervisor
    print("📋 架构师提交任务：开发一个用户管理系统")
    task_overview = A2ATask(
        task_id="a2a-task-user-mgmt-001",
        from_agent=architect.agent_id,
        to_agent="supervisor",
        description="开发用户管理系统：包含用户注册、登录、权限管理功能",
    )

    # 4. Supervisor 分解任务
    print("\n🔧 Supervisor 分解任务...")

    subtask_details = [
        {
            "id": "a2a-task-sub-001",
            "name": "需求分析",
            "assignee": "agent-architect",
            "description": "分析用户管理系统需求",
        },
        {
            "id": "a2a-task-sub-002",
            "name": "架构设计",
            "assignee": "agent-architect",
            "description": "设计系统架构和数据库",
        },
        {
            "id": "a2a-task-sub-003",
            "name": "代码实现",
            "assignee": "agent-developer",
            "description": "实现核心功能代码",
        },
        {"id": "a2a-task-sub-004", "name": "测试编写", "assignee": "agent-tester", "description": "编写单元测试"},
        {"id": "a2a-task-sub-005", "name": "部署验证", "assignee": "agent-developer", "description": "部署到测试环境"},
    ]

    for i, subtask in enumerate(subtask_details, 1):
        print(f"  {i}. [{subtask['id']}] {subtask['name']} → {subtask['assignee']}")

    # 5. Supervisor 分配任务
    print("\n📤 Supervisor 分配任务给各 Agent...")
    for subtask in subtask_details:
        task = A2ATask(
            task_id=subtask["id"],
            from_agent="supervisor",
            to_agent=subtask["assignee"],
            description=subtask["description"],
        )
        supervisor.submit_task(task)
        print(f"  ✓ {subtask['name']} 已分配给 {subtask['assignee']}")

    # 6. 模拟任务执行状态
    print("\n⏰ 任务执行中...")
    for subtask in subtask_details:
        A2AStateMachine.transition(
            A2ATask(task_id=subtask["id"], from_agent="supervisor", to_agent=subtask["assignee"], description=""),
            A2ATaskStatus.IN_PROGRESS,
        )
        print(f"  🟡 {subtask['name']}: 执行中...")

    # 7. 检测死锁
    print("\n🔍 Supervisor 检测死锁...")
    deadlocks = supervisor.detect_deadlocks()
    if deadlocks:
        print(f"  ⚠️ 发现 {len(deadlocks)} 个死锁")
        for d in deadlocks:
            print(f"    - {d['task_id']} ({d['agent']})")
    else:
        print("  ✅ 未发现死锁")

    # 8. 任务完成
    print("\n🎉 所有子任务完成！")
    for subtask in subtask_details:
        A2AStateMachine.transition(
            A2ATask(task_id=subtask["id"], from_agent="supervisor", to_agent=subtask["assignee"], description=""),
            A2ATaskStatus.COMPLETED,
        )
        print(f"  ✅ {subtask['name']}: 已完成")

    # 9. 生成协调报告
    print("\n📊 A2A 协调报告")
    print("-" * 40)
    print(f"总任务数: {len(subtask_details)}")
    print("参与 Agent: 3 (架构师、开发者、测试员)")
    print("协调状态: 成功")
    print(f"死锁检测: {len(deadlocks)} 个")
    print("Agent 负载:")
    print(f"  - 架构师: {supervisor.get_agent_load(architect.agent_id)} 任务")
    print(f"  - 开发者: {supervisor.get_agent_load(developer.agent_id)} 任务")
    print(f"  - 测试员: {supervisor.get_agent_load(tester.agent_id)} 任务")
    print("\n✅ A2A 协调功能正常工作！")


if __name__ == "__main__":
    demo_task_coordination()
