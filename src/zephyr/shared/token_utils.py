# [A_module] module_id=MOD-SHR_token_utils | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.token_utils

# [INVARIANTS] re-export shim only; canonical source is zephyr.ops.observability.token_utils

# [MODIFY-GUARD] do not add logic here; modify zephyr.ops.observability.token_utils instead

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

def __getattr__(name: str):
    from zephyr.ops.observability import token_utils as _tu
    if name in _tu.__all__:
        return getattr(_tu, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["DEFAULT_CONTEXT_TOKEN_BUDGET", "estimate_tokens"]
