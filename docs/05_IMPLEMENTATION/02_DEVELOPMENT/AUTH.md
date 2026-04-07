---
module_id: AUTH_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 实施指南、部署文档

---
---

---
module_id: IMPL_DEV_AUTH_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
responsibility:
  - 因子计算
  - 数据源
  - 机器学习
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?---



# 简化认证模块蓝�?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 清风量化系统 v5.0 - 简化认证授权系�?
> **索引**: `AUTH.001`
> **开发时�?*: 5h
> **核心定位**: 提供简化的身份认证和权限控制，支持AI权限管理


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **简�?* | 不追求企业级复杂性，够用即可 |
| **JWT** | 标准JWT令牌，支持过期和刷新 |
| **分层权限** | 运营/研究/风控三层权限 |
| **AI友好** | 支持API Key认证，便于AI调用 |


## 2. 认证类型

### 2.1 认证方式

| 类型 | 用�?| 场景 |
|------|------|------|
| **JWT Token** | 用户登录认证 | Web界面、API调用 |
| **API Key** | AI/系统认证 | AI Agent、系统间调用 |
| **Session** | 短期会话 | Web界面 |


## 3. 核心实现

### 3.1 用户和权限模�?

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import jwt
import secrets

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

class Role(Enum):
    OPERATOR = "operator"      # 运营人员
    RESEARCHER = "researcher"  # 研究人员
    RISK_MANAGER = "risk_manager"  # 风控人员
    ADMIN = "admin"            # 管理�?
    AI_SYSTEM = "ai_system"   # AI系统

@dataclass
class User:
    """用户模型

    索引: AUTH.001-D01
    """
    user_id: str
    username: str
    password_hash: str
    role: Role
    permissions: List[Permission]
    api_keys: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True

@dataclass
class APIKey:
    """API Key模型

    索引: AUTH.001-D02
    """
    key_id: str
    key_hash: str
    user_id: str
    name: str
    permissions: List[Permission]
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
```

### 3.2 认证服务

```python
class AuthService:
    """认证服务

    索引: AUTH.001-M01
    上游: API Layer, AI Agent
    下游: UserStorage, LogManager
    """

    def __init__(self, config: Dict):
        self.config = config
        self.secret_key = config['jwt_secret']
        self.token_expiry = config.get('token_expiry_hours', 24)
        self.algorithm = 'HS256'
        self.user_store = UserStore()
        self.api_key_store = APIKeyStore()

    def authenticate(
        self,
        username: str,
        password: str
    ) -> Optional[AuthResult]:
        """用户名密码认�?

        参数:
            username: 用户�?
            password: 密码

        返回:
            AuthResult: 认证结果，包含token
        """
        user = self.user_store.get_by_username(username)

        if not user or not user.is_active:
            return None

        password_hash = self._hash_password(password)
        if password_hash != user.password_hash:
            return None

        token = self._generate_token(user)
        self.user_store.update_last_login(user.user_id)

        return AuthResult(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            token=token,
            expires_in=self.token_expiry * 3600
        )

    def authenticate_api_key(self, api_key: str) -> Optional[AuthResult]:
        """API Key认证

        参数:
            api_key: API Key

        返回:
            AuthResult: 认证结果
        """
        key_hash = self._hash_api_key(api_key)
        key_obj = self.api_key_store.get_by_hash(key_hash)

        if not key_obj or not key_obj.is_active:
            return None

        if key_obj.expires_at and key_obj.expires_at < datetime.now():
            return None

        self.api_key_store.update_last_used(key_obj.key_id)

        user = self.user_store.get_by_id(key_obj.user_id)

        return AuthResult(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            permissions=key_obj.permissions,
            token=api_key,
            token_type='api_key'
        )

    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """验证JWT Token

        参数:
            token: JWT Token

        返回:
            TokenPayload: Token内容
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def create_api_key(
        self,
        user_id: str,
        name: str,
        permissions: List[Permission],
        expires_in_days: Optional[int] = None
    ) -> str:
        """创建API Key

        参数:
            user_id: 用户ID
            name: Key名称
            permissions: 权限列表
            expires_in_days: 过期天数

        返回:
            生成的API Key
        """
        api_key = f"qfs_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_api_key(api_key)

        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        key_obj = APIKey(
            key_id=secrets.token_hex(8),
            key_hash=key_hash,
            user_id=user_id,
            name=name,
            permissions=permissions,
            expires_at=expires_at
        )

        self.api_key_store.save(key_obj)
        return api_key

    def revoke_api_key(self, key_id: str) -> bool:
        """撤销API Key

        参数:
            key_id: Key ID

        返回:
            是否成功
        """
        return self.api_key_store.revoke(key_id)

    def _generate_token(self, user: User) -> str:
        """生成JWT Token"""
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'permissions': [p.value for p in user.permissions],
            'exp': datetime.now() + timedelta(hours=self.token_expiry)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def _hash_password(self, password: str) -> str:
        """哈希密码"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _hash_api_key(self, api_key: str) -> str:
        """哈希API Key"""
        return hashlib.sha256(api_key.encode()).hexdigest()
```

### 3.3 权限检�?

```python
class PermissionService:
    """权限服务

    索引: AUTH.001-M02
    """

    ROLE_PERMISSIONS = {
        Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.ADMIN],
        Role.RISK_MANAGER: [Permission.READ, Permission.EXECUTE],
        Role.RESEARCHER: [Permission.READ, Permission.WRITE],
        Role.OPERATOR: [Permission.READ],
        Role.AI_SYSTEM: [Permission.READ, Permission.EXECUTE]
    }

    def __init__(self):
        self.auth_service = AuthService()

    def check_permission(
        self,
        user_id: str,
        required_permission: Permission,
        resource: str = None
    ) -> bool:
        """检查用户权�?

        参数:
            user_id: 用户ID
            required_permission: 所需权限
            resource: 资源路径

        返回:
            是否有权�?
        """
        user = self.auth_service.user_store.get_by_id(user_id)

        if not user or not user.is_active:
            return False

        if required_permission in user.permissions:
            return True

        if required_permission in self.ROLE_PERMISSIONS.get(user.role, []):
            return True

        return False

    def require_permission(self, permission: Permission, resource: str = None):
        """权限检查装饰器

        用法:
            @require_permission(Permission.WRITE, '/strategies')
            def update_strategy(strategy_id: str):
                pass
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                token = kwargs.get('token') or request.headers.get('Authorization')

                if not token:
                    raise UnauthorizedError("Missing authentication")

                if token.startswith('Bearer '):
                    token = token[7:]
                    payload = self.auth_service.verify_token(token)
                    if not payload:
                        raise UnauthorizedError("Invalid token")
                else:
                    result = self.auth_service.authenticate_api_key(token)
                    if not result:
                        raise UnauthorizedError("Invalid API key")
                    payload = TokenPayload(
                        user_id=result.user_id,
                        username=result.username,
                        role=result.role
                    )

                if not self.check_permission(payload.user_id, permission, resource):
                    raise ForbiddenError(f"Missing permission: {permission.value}")

                kwargs['current_user'] = payload
                return func(*args, **kwargs)

            return wrapper
        return decorator
```


## 4. API接口

### 4.1 认证API

```python
# API: /api/v1/auth

class AuthAPI:
    """认证API

    索引: AUTH.001-API01
    Layer: Layer 0
    """

    @router.post("/auth/login")
    def login(self, username: str, password: str) -> AuthResponse:
        """用户登录

        参数:
            username: 用户�?
            password: 密码

        返回:
            AuthResponse: 认证响应，包含token
        """

    @router.post("/auth/logout")
    def logout(self, token: str) -> None:
        """用户登出

        参数:
            token: JWT Token
        """

    @router.post("/auth/refresh")
    def refresh_token(self, refresh_token: str) -> AuthResponse:
        """刷新Token

        参数:
            refresh_token: 刷新Token

        返回:
            新的AuthResponse
        """

    @router.post("/auth/api-key")
    def create_api_key(
        self,
        name: str,
        permissions: List[str],
        expires_days: Optional[int] = None
    ) -> APIKeyResponse:
        """创建API Key

        参数:
            name: Key名称
            permissions: 权限列表
            expires_days: 过期天数

        返回:
            APIKeyResponse: 包含生成的Key
        """

    @router.delete("/auth/api-key/{key_id}")
    def revoke_api_key(self, key_id: str) -> None:
        """撤销API Key

        参数:
            key_id: Key ID
        """

    @router.get("/auth/me")
    def get_current_user(self, token: str) -> UserResponse:
        """获取当前用户信息

        返回:
            UserResponse: 用户信息
        """
```

### 4.2 权限API

```python
# API: /api/v1/permissions

class PermissionAPI:
    """权限API

    索引: AUTH.001-API02
    """

    @router.get("/permissions/roles")
    def list_roles(self) -> List[RoleInfo]:
        """获取角色列表"""

    @router.get("/permissions/roles/{role}/permissions")
    def get_role_permissions(self, role: str) -> List[str]:
        """获取角色权限"""

    @router.get("/users/{user_id}/permissions")
    def get_user_permissions(self, user_id: str) -> UserPermissions:
        """获取用户权限"""

    @router.post("/users/{user_id}/permissions")
    def add_user_permission(
        self,
        user_id: str,
        permission: str
    ) -> None:
        """添加用户权限"""
```


## 5. 配置

### 5.1 YAML配置

```yaml
# config/auth.yaml

auth:
  jwt_secret: "${JWT_SECRET}"
  jwt_algorithm: "HS256"
  token_expiry_hours: 24

  api_key:
    prefix: "qfs_"
    default_expiry_days: 90
    max_per_user: 10

  password:
    min_length: 8
    require_special: false

roles:
  admin:
    permissions: ["read", "write", "execute", "admin"]

  risk_manager:
    permissions: ["read", "execute"]

  researcher:
    permissions: ["read", "write"]

  operator:
    permissions: ["read"]

  ai_system:
    permissions: ["read", "execute"]
```


## 6. 安全考虑

### 6.1 安全措施

| 措施 | 说明 |
|------|------|
| 密码哈希 | SHA-256，单向哈�?|
| API Key安全 | 只在创建时返回一次，之后不可查看 |
| Token过期 | 24小时过期，强制重新认�?|
| 失败锁定 | 连续5次失败，锁定15分钟 |
| 审计日志 | 所有认证事件记�?|

### 6.2 审计日志

```python
class AuthAuditLogger:
    """认证审计日志

    索引: AUTH.001-M03
    """

    def log_login(self, user_id: str, success: bool, ip: str):
        """记录登录事件"""

    def log_logout(self, user_id: str):
        """记录登出事件"""

    def log_api_key_created(self, user_id: str, key_id: str, name: str):
        """记录API Key创建"""

    def log_api_key_revoked(self, user_id: str, key_id: str):
        """记录API Key撤销"""

    def log_permission_denied(self, user_id: str, resource: str, permission: str):
        """记录权限拒绝"""
```


## 7. AI权限集成

### 7.1 AI系统认证

```python
class AIAuthIntegration:
    """AI认证集成

    索引: AUTH.001-M04
    """

    def __init__(self):
        self.auth_service = AuthService()

    def create_ai_agent_key(
        self,
        agent_name: str,
        permissions: List[Permission] = None
    ) -> str:
        """为AI Agent创建专用Key

        参数:
            agent_name: Agent名称
            permissions: 权限列表，默认只有EXECUTE

        返回:
            API Key
        """
        if permissions is None:
            permissions = [Permission.READ, Permission.EXECUTE]

        return self.auth_service.create_api_key(
            user_id='ai_system',
            name=f"AI_{agent_name}",
            permissions=permissions,
            expires_in_days=365
        )

    def verify_ai_request(self, api_key: str, required_permission: Permission) -> bool:
        """验证AI请求权限

        参数:
            api_key: API Key
            required_permission: 所需权限

        返回:
            是否通过验证
        """
        result = self.auth_service.authenticate_api_key(api_key)
        if not result:
            return False

        return required_permission in result.permissions
```


## 8. 开发任务分�?5h)

| 任务 | 时间 | 交付�?|
|------|------|--------|
| 用户和权限模�?| 0.5h | User, APIKey模型 |
| JWT认证服务 | 1h | AuthService |
| API Key认证 | 0.5h | API Key相关方法 |
| 权限检查服�?| 0.5h | PermissionService |
| FastAPI路由 | 1h | AuthAPI, PermissionAPI |
| 审计日志 | 0.5h | AuthAuditLogger |
| 配置集成 | 0.5h | auth.yaml |
| 单元测试 | 0.5h | test_auth.py |


**维护�?*: 清风量化系统
**索引**: `AUTH.001`
**最后更�?*: 2026-03-29
