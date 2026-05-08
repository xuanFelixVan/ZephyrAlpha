"""LSG 自防护包（自我安全韧性机制）。

LSG 自身的防御能力：
- 凭据生命周期管理
- 配置完整性检查
- 日志防篡改
- 健康检查与自愈
- 降级策略管理
"""

__all__ = ['adversarial_mutator', 'code_integrity', 'isolation', 'l7_validation', 'red_team_scanner']
