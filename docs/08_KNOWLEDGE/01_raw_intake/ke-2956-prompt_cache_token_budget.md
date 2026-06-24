---
module_id: KE-2856---token-budget----000
status: active
title: Prompt Cache & Token Budget（提示缓存与Token预算）
category: module_blueprint
---

# Prompt Cache & Token Budget（提示缓存与Token预算）

Prompt Cache & Token Budget（提示缓存与Token预算）

```python
class PromptCacheManager:
    """AI调用前的上下文优化——缓存+压缩+预算三重优化。
    氛围编程核心运维——Token钱和上下文窗口都是有限资源。
    """
    _cache: dict[str, tuple[float, str]] = {}  # prompt_hash → (ttl, cached_response)
    _modules_total_tokens_this_session: dict[str, int] = {}  # per-module 追踪

    async fn optimize_prompt(self, module_id: str,
                              raw_context: str,
                              user_intent: str) -> str:
        """三阶段：① 检查缓存→命中直接返回 ② 压缩context→剪枝不相关文件
        ③ Token预算告警→超限提示简化"""

        # 阶段1: 缓存检查
        cache_key = sha256(user_intent.encode()).hexdigest()
        if cache_key in self._cache:
            ttl, cached = self._cache[cache_key]
            if time.time() < ttl:
                self._track_tokens(module_id, len(cached) // 4)  # ~1 token/4 chars
                return cached

        # 阶段2: 上下文压缩——只发相关文件的前N行定义
        compressed = self._compress_context(raw_context, max_chars=8000)

        # 阶段3: Token预算检查——若本月已用>80%→自动提示简化
        monthly_pct = self._get_monthly_token_pct(module_id)
        if monthly_pct > 0.80:
            compressed = f"[⚠️ Token预算已用{monthly_pct:.0%}] " + compressed[:4000]

        return compressed
```
