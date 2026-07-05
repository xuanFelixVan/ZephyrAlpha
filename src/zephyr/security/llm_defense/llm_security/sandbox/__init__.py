# [A_module] module_id=MOD-SEC_sandbox | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [TTL] permanent
"""LSG 代码执行沙箱包。

为 L3 输出安全层提供隔离代码执行能力：
- WASI 运行时沙箱
- 进程级隔离
- 文件系统审计
- 资源限制与超时控制
"""

__all__ = []
