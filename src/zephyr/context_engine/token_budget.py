# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.token_budget

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] zephyr.shared.observability.token_utils; zephyr.context_engine.*

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
token_budget.py — Token 估算工具 SSoT

根因修复：此前 _estimate_tokens() 在 3 个文件中重复定义，
且存在微差（空字符串处理不一致），说明各自演化已产生分歧。

对标：
  - OpenAI tiktoken: token 计算应统一入口
  - LangChain: token 估算使用统一工具函数
"""

DEFAULT_CONTEXT_TOKEN_BUDGET: int = 8000


def estimate_tokens(text: str) -> int:
    """估算文本的 token 数量。

    使用简单的 1 token ≈ 4 字符启发式估算。
    对于中文等非拉丁语系，此估算偏低，但作为预算控制足够。

    Args:
        text: 待估算的文本字符串。空字符串返回 0。

    Returns:
        估算的 token 数量（≥ 0）。
    """
    if not text:
        return 0
    return max(len(text) // 4, 1)


__all__ = [
    "DEFAULT_CONTEXT_TOKEN_BUDGET",
    "estimate_tokens",
]
