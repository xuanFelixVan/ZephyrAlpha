# [BLUEPRINT] DOM-GOV-001 | tests/integration/l01_infrastructure/a2a_protocol/__init__.py | §
"""MOD-INF-025 A2A Protocol 集成测试

Phase 1 集成测试验证核心链路: 发现→通信→任务调度→状态机→死锁检测→升级

触发条件(R81-C04): Agent>=3 AND conflict>=5/day 满足后
→ 扩展为全链路集成测试(含仲裁/语义冲突/共识/回滚/辩论/红白对抗)
"""

__version__ = "0.1.0"
