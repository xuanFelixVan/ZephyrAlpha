---
module_id: KE-module_blu-cache_invalidation_py-000
title: cache_invalidation.py — 新增文件
category: module_blueprint
---

# cache_invalidation.py — 新增文件

cache_invalidation.py — 新增文件
class PermissionCacheInvalidator:
    """
    缓存失效器——权限变更时主动推送invalidation，而非被动等TTL。
    
    变更事件类型：
    1. rbac_roles.yaml 内容变化 → 全局失效所有Agent的L1缓存
    2. GOV-AI-001 authority变更 → 标记受影响权限为"待重算"
    3. maturity_upgrade → 该Agent的权限缓存立即失效（可能更宽松）
    4. emergency_permission_narrow → 立即失效所有指定操作的缓存
    """
    
    async def on_rbac_config_change(self, diff: ConfigDiff) -> InvalidationReport:
        """rbac_roles.yaml 变更 → 分析diff → 精准失效受影响缓存"""
        affected_agents = self._resolve_affected_agents(diff)
        affected_operations = self._resolve_affected_operations(diff)
        
        # 精准失效——只失效真正受影响的缓存条目
        invalidated_count = await self.cache.invalidate(
            agents=affected_agents,
            operations=affected_operations,
        )
        return InvalidationReport(
            config_diff=diff,
            affected_agents=len(affected_agents),
            invalidated_cache_entries=invalidated_count,
            invalidation_time_ms=self._elapsed_ms,
        )
    
    async def on_emergency_narrow(self, operation: str) -> InvalidationReport:
        """紧急收紧特定操作的权限 → 立即失效所有Agent对该操作的缓存"""
        await self.cache.invalidate(operations=[operation])
    
    def cache_window_guarantee(self) -> float:
        """最大缓存窗口——变更事件发出后，缓存中的旧值最长存活时间"""
        return 0.1  # 100ms——推送延迟上限
```

```yaml
