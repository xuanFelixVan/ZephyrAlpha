# [BLUEPRINT] MOD-INF-014 | 03_modules/_cross_layer/llm-security/blueprint.md | §
"""LSG 自防护包（自我安全韧性机制）。

LSG 自身的防御能力：
- 凭据生命周期管理
- 配置完整性检查
- 日志防篡改
- 健康检查与自愈
- 降级策略管理
"""

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "adversarial_mutator": ("AdversarialMutator",),
    "code_integrity": ("CodeIntegrityGuard",),
    "isolation": ("LSGIsolation",),
    "l7_validation": ("ValidationLayer",),
    "red_team_scanner": ("RedTeamScanner",),
}

__all__ = [
    'adversarial_mutator', 'code_integrity', 'isolation', 'l7_validation', 'red_team_scanner',
    'AdversarialMutator', 'CodeIntegrityGuard', 'LSGIsolation', 'ValidationLayer', 'RedTeamScanner',
]


def __getattr__(name: str):
    for mod_name, symbols in _LAZY_MODULES.items():
        if name in symbols or name == mod_name:
            mod = __import__(f"zephyr.llm_security.self_protection.{mod_name}", fromlist=[name])
            try:
                return getattr(mod, name)
            except AttributeError:
                pass
    raise AttributeError(f"module 'zephyr.llm_security.self_protection' has no attribute '{name}'")
