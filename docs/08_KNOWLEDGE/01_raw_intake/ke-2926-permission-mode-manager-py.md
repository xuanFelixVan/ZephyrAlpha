---
module_id: KE-2826-----000
status: active
title: permission_mode_manager.py — 新增文件（横切面D 组件）
category: module_blueprint
---

# permission_mode_manager.py — 新增文件（横切面D 组件）

permission_mode_manager.py — 新增文件（横切面D 组件）
class PermissionModeManager:
    """权限模式管理器——横切面D核心组件"""
    
    async def set_mode(self, mode: str, session_id: str) -> ModeChangeResult:
        """切换权限模式——更新L1 RBAC行为 + 通知Gate Engine"""
    
    async def get_current_mode(self) -> PermissionMode:
        """获取当前活动的权限模式"""
    
    async def activate_profile(self, profile_name: str) -> ProfileActivationResult:
        """激活配置profile——mode+sandbox+network+model 一体化切换"""
    
    def allowed_in_current_mode(self, action: Action) -> bool:
        """快速查询——当前模式下这个操作是否允许"""
```

---
