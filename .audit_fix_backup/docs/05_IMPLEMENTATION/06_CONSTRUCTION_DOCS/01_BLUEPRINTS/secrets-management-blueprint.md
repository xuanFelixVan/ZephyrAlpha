---

module_id: SECRETS_MANAGEMENT_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 首席文档架构师

responsibility:

  - 密钥管理

  - 敏感信息加密存储

  - 密钥轮换

  - 访问控制

standard_type: 专业量化机构蓝图

compliance_level: 专业标准

layer: layer_05

---



# 密钥管理蓝图



> **核心职责**: 提供安全的密钥存储、管理和访问控制，保护API密钥、数据库密码等敏感信息

> **职责边界**: 

> - ✅ 本文档负责：密钥存储、加密、轮换、访问控制

> - ❌ 本文档不负责：数据加密（由数据加密模块负责）、网络安全（由网络安全模块负责）



## 核心定位



负责密钥管理模块的设计与构建，提供安全的密钥存储、自动密钥轮换、细粒度访问控制，确保敏感信息安全，支持合规审计。



## 设计目标



### 主要目标



1. **安全存储**: API密钥、数据库密码等敏感信息加密存储

2. **密钥轮换**: 支持自动和手动密钥轮换机制

3. **访问控制**: 基于角色的细粒度访问控制

4. **审计追踪**: 所有密钥访问操作可追溯



### 质量目标



- 密钥存储安全性: 100%

- 密钥轮换成功率: 99.9%

- 访问控制准确性: 100%

- 审计日志完整性: 100%



## 开源方案选型



### 推荐方案: Infisical



| 属性 | 详情 |

|------|------|

| **GitHub** | https://github.com/Infisical/infisical |

| **Stars** | 15,000+ |

| **License** | MIT |

| **语言** | Go/TypeScript |

| **特点** | 开源密钥管理，开发者友好 |



**选择理由**:

1. **开源免费**: MIT许可证，功能完整

2. **易于部署**: Docker一键部署，配置简单

3. **开发者友好**: CLI工具、SDK支持多种语言

4. **Git集成**: 支持密钥版本控制

5. **个人友好**: 适合个人开发者使用



### 备选方案



| 项目 | Stars | 特点 | 推荐度 |

|------|-------|------|--------|

| **HashiCorp Vault** | 30k+ | 企业级密钥管理 | ⭐⭐⭐⭐⭐ |

| **Doppler** | 商业 | 开发者友好的密钥管理 | ⭐⭐⭐⭐ |



## 核心功能设计



### 1. 密钥存储模块



```python

from infisical import InfisicalClient



class SecretsManager:

    """密钥管理器"""

    

    def __init__(self, client_id: str, client_secret: str, workspace_id: str):

        self.client = InfisicalClient(

            client_id=client_id,

            client_secret=client_secret,

            workspace_id=workspace_id

        )

    

    def store_secret(

        self,

        key: str,

        value: str,

        environment: str = "dev",

        tags: list = None

    ):

        """存储密钥"""

        secret = self.client.create_secret(

            secret_name=key,

            secret_value=value,

            environment=environment,

            tags=tags or []

        )

        

        return {

            "id": secret.id,

            "key": secret.name,

            "environment": secret.environment,

            "created_at": secret.created_at

        }

    

    def get_secret(self, key: str, environment: str = "dev"):

        """获取密钥"""

        secret = self.client.get_secret(

            secret_name=key,

            environment=environment

        )

        

        return secret.secret_value

    

    def update_secret(

        self,

        key: str,

        new_value: str,

        environment: str = "dev"

    ):

        """更新密钥"""

        secret = self.client.update_secret(

            secret_name=key,

            secret_value=new_value,

            environment=environment

        )

        

        return {

            "id": secret.id,

            "key": secret.name,

            "version": secret.version,

            "updated_at": secret.updated_at

        }

    

    def delete_secret(self, key: str, environment: str = "dev"):

        """删除密钥"""

        return self.client.delete_secret(

            secret_name=key,

            environment=environment

        )

```



### 2. 密钥轮换模块



```python

from datetime import datetime, timedelta

import secrets

import string



class SecretRotation:

    """密钥轮换管理器"""

    

    def __init__(self, secrets_manager: SecretsManager):

        self.manager = secrets_manager

        self.rotation_policies = {}

    

    def set_rotation_policy(

        self,

        key: str,

        rotation_days: int,

        auto_generate: bool = True,

        length: int = 32

    ):

        """设置轮换策略"""

        self.rotation_policies[key] = {

            "rotation_days": rotation_days,

            "auto_generate": auto_generate,

            "length": length,

            "last_rotation": datetime.now()

        }

    

    def generate_random_secret(self, length: int = 32):

        """生成随机密钥"""

        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"

        return ''.join(secrets.choice(alphabet) for _ in range(length))

    

    def rotate_secret(self, key: str, environment: str = "dev"):

        """轮换密钥"""

        policy = self.rotation_policies.get(key)

        

        if not policy:

            raise ValueError(f"No rotation policy for key: {key}")

        

        if policy["auto_generate"]:

            new_value = self.generate_random_secret(policy["length"])

        else:

            raise ValueError("Manual rotation required but no new value provided")

        

        old_value = self.manager.get_secret(key, environment)

        

        self.manager.update_secret(key, new_value, environment)

        

        policy["last_rotation"] = datetime.now()

        

        return {

            "key": key,

            "old_value_preview": old_value[:4] + "****",

            "new_value_preview": new_value[:4] + "****",

            "rotated_at": datetime.now().isoformat()

        }

    

    def check_rotation_needed(self):

        """检查需要轮换的密钥"""

        needs_rotation = []

        

        for key, policy in self.rotation_policies.items():

            days_since_rotation = (

                datetime.now() - policy["last_rotation"]

            ).days

            

            if days_since_rotation >= policy["rotation_days"]:

                needs_rotation.append({

                    "key": key,

                    "days_overdue": days_since_rotation - policy["rotation_days"]

                })

        

        return needs_rotation

```



### 3. 访问控制模块



```python

from enum import Enum

from typing import List, Dict



class Permission(Enum):

    READ = "read"

    WRITE = "write"

    DELETE = "delete"

    ADMIN = "admin"



class AccessControl:

    """访问控制管理器"""

    

    def __init__(self, secrets_manager: SecretsManager):

        self.manager = secrets_manager

        self.policies: Dict[str, Dict] = {}

    

    def create_policy(

        self,

        policy_name: str,

        secret_prefix: str,

        permissions: List[Permission],

        environments: List[str] = None

    ):

        """创建访问策略"""

        policy = {

            "name": policy_name,

            "secret_prefix": secret_prefix,

            "permissions": [p.value for p in permissions],

            "environments": environments or ["dev", "prod"],

            "created_at": datetime.now().isoformat()

        }

        

        self.policies[policy_name] = policy

        return policy

    

    def assign_policy_to_user(self, user_id: str, policy_name: str):

        """为用户分配策略"""

        if policy_name not in self.policies:

            raise ValueError(f"Policy {policy_name} not found")

        

        return {

            "user_id": user_id,

            "policy_name": policy_name,

            "assigned_at": datetime.now().isoformat()

        }

    

    def check_permission(

        self,

        user_id: str,

        secret_key: str,

        permission: Permission,

        environment: str

    ) -> bool:

        """检查用户权限"""

        user_policies = self._get_user_policies(user_id)

        

        for policy in user_policies:

            if self._matches_policy(policy, secret_key, permission, environment):

                return True

        

        return False

    

    def _get_user_policies(self, user_id: str) -> List[Dict]:

        """获取用户的所有策略"""

        return list(self.policies.values())

    

    def _matches_policy(

        self,

        policy: Dict,

        secret_key: str,

        permission: Permission,

        environment: str

    ) -> bool:

        """检查是否匹配策略"""

        if not secret_key.startswith(policy["secret_prefix"]):

            return False

        

        if permission.value not in policy["permissions"]:

            return False

        

        if environment not in policy["environments"]:

            return False

        

        return True

```



### 4. 审计日志模块



```python

import json

from datetime import datetime

from typing import Dict, Any



class AuditLogger:

    """审计日志记录器"""

    

    def __init__(self, log_file: str = "secrets_audit.log"):

        self.log_file = log_file

    

    def log_access(

        self,

        action: str,

        secret_key: str,

        user_id: str,

        environment: str,

        result: str,

        metadata: Dict[str, Any] = None

    ):

        """记录访问日志"""

        log_entry = {

            "timestamp": datetime.now().isoformat(),

            "action": action,

            "secret_key": secret_key,

            "user_id": user_id,

            "environment": environment,

            "result": result,

            "metadata": metadata or {}

        }

        

        with open(self.log_file, "a") as f:

            f.write(json.dumps(log_entry) + "\n")

    

    def get_audit_trail(

        self,

        secret_key: str = None,

        user_id: str = None,

        start_time: datetime = None,

        end_time: datetime = None

    ) -> List[Dict]:

        """获取审计记录"""

        audit_trail = []

        

        with open(self.log_file, "r") as f:

            for line in f:

                entry = json.loads(line.strip())

                

                if secret_key and entry["secret_key"] != secret_key:

                    continue

                

                if user_id and entry["user_id"] != user_id:

                    continue

                

                entry_time = datetime.fromisoformat(entry["timestamp"])

                if start_time and entry_time < start_time:

                    continue

                if end_time and entry_time > end_time:

                    continue

                

                audit_trail.append(entry)

        

        return audit_trail

```



## 部署架构



### Docker Compose部署



```yaml

version: '3.8'



services:

  infisical:

    image: infisical/infisical:latest

    ports:

      - "8081:8081"

    environment:

      - ENCRYPTION_KEY=${ENCRYPTION_KEY}

      - JWT_SECRET=${JWT_SECRET}

      - DB_CONNECTION_STRING=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/infisical

      - SITE_URL=http://localhost:8081

    depends_on:

      - postgres

    volumes:

      - infisical_data:/app/data

    restart: unless-stopped

  

  postgres:

    image: postgres:15

    environment:

      - POSTGRES_USER=postgres

      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

      - POSTGRES_DB=infisical

    volumes:

      - postgres_data:/var/lib/postgresql/data

    restart: unless-stopped



volumes:

  infisical_data:

  postgres_data:

```



## 与现有系统集成



### 1. 与数据源管理集成



```python

# 在DATA_SOURCE_MANAGEMENT_BLUEPRINT中使用密钥管理

class SecureDataSourceManager:

    """安全数据源管理器"""

    

    def __init__(self, secrets_manager: SecretsManager):

        self.secrets = secrets_manager

    

    def get_database_connection(self, db_name: str):

        """获取数据库连接"""

        password = self.secrets.get_secret(f"db_{db_name}_password")

        

        return {

            "host": self.secrets.get_secret(f"db_{db_name}_host"),

            "port": self.secrets.get_secret(f"db_{db_name}_port"),

            "user": self.secrets.get_secret(f"db_{db_name}_user"),

            "password": password

        }

    

    def get_api_credentials(self, api_name: str):

        """获取API凭证"""

        return {

            "api_key": self.secrets.get_secret(f"api_{api_name}_key"),

            "api_secret": self.secrets.get_secret(f"api_{api_name}_secret")

        }

```



### 2. 与环境变量注入集成



```python

import os

from dotenv import load_dotenv



class EnvironmentInjector:

    """环境变量注入器"""

    

    def __init__(self, secrets_manager: SecretsManager):

        self.secrets = secrets_manager

    

    def inject_secrets_to_env(self, environment: str = "dev"):

        """将密钥注入环境变量"""

        secrets = self.secrets.client.list_secrets(environment=environment)

        

        for secret in secrets:

            os.environ[secret.name] = secret.secret_value

    

    def load_to_dotenv(self, environment: str = "dev", output_file: str = ".env"):

        """导出到.env文件"""

        secrets = self.secrets.client.list_secrets(environment=environment)

        

        with open(output_file, "w") as f:

            for secret in secrets:

                f.write(f"{secret.name}={secret.secret_value}\n")

```



### 3. 与CI/CD集成



```yaml

# GitHub Actions集成示例

name: Deploy with Secrets



on:

  push:

    branches: [main]



jobs:

  deploy:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v3

      

      - name: Install Infisical CLI

        run: |

          curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo -E bash

          sudo apt-get update && sudo apt-get install -y infisical

      

      - name: Inject Secrets

        env:

          INFISICAL_CLIENT_ID: ${{ secrets.INFISICAL_CLIENT_ID }}

          INFISICAL_CLIENT_SECRET: ${{ secrets.INFISICAL_CLIENT_SECRET }}

        run: |

          infisical login --client-id $INFISICAL_CLIENT_ID --client-secret $INFISICAL_CLIENT_SECRET

          infisical export --env=prod > .env

      

      - name: Deploy

        run: |

          source .env

          # 部署命令

```



## 实施计划



### 阶段1: 基础部署 (Week 1)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| Docker环境搭建 | 2h | 开发者 | Docker Compose配置 |

| Infisical部署 | 4h | 开发者 | 运行中的密钥管理 |

| 基础配置 | 2h | 开发者 | 配置文件 |

| 测试验证 | 2h | 开发者 | 测试报告 |



### 阶段2: 密钥迁移 (Week 2)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| 现有密钥盘点 | 4h | 开发者 | 密钥清单 |

| 密钥迁移 | 8h | 开发者 | 迁移后的密钥库 |

| 应用集成 | 8h | 开发者 | 集成代码 |



### 阶段3: 安全增强 (Week 3)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| 访问控制配置 | 4h | 开发者 | 访问策略 |

| 审计日志配置 | 4h | 开发者 | 审计系统 |

| 密钥轮换配置 | 4h | 开发者 | 轮换策略 |



## 性能指标



| 指标 | 目标值 | 测量方法 |

|------|--------|---------|

| **密钥读取延迟** | <50ms | 平均读取时间 |

| **密钥写入延迟** | <100ms | 平均写入时间 |

| **系统可用性** | 99.9% | 月度可用性统计 |

| **加密强度** | AES-256 | 加密算法标准 |



## 安全最佳实践



### 1. 密钥命名规范



```

# 数据库密钥

db_{database_name}_host

db_{database_name}_port

db_{database_name}_user

db_{database_name}_password



# API密钥

api_{service_name}_key

api_{service_name}_secret

api_{service_name}_token



# 加密密钥

encryption_{purpose}_key

```



### 2. 环境隔离



```python

# 开发环境

environment: "dev"



# 生产环境

environment: "prod"



# 测试环境

environment: "test"

```



### 3. 密钥轮换策略



| 密钥类型 | 轮换周期 | 自动生成 |

|---------|---------|---------|

| API密钥 | 90天 | 是 |

| 数据库密码 | 180天 | 是 |

| 加密密钥 | 365天 | 否 |



## 成本估算



| 项目 | 开源方案成本 | 商业方案成本 |

|------|-------------|-------------|

| **软件许可** | $0 | $10k+/年 |

| **部署运维** | 自行维护 | 供应商支持 |

| **硬件资源** | 2核4G | 云服务费用 |

| **总成本** | $0 + 运维时间 | $10k+/年 |



```---



**文档版本**: v1.0.0

**创建日期**: 2026-04-07

**最后更新**: 2026-04-07

**状态**: Active



## 接口与契约（蓝图终稿）



- **契约真源**：`API_Contract.md`

- **对外接口边界**：本模块对外提供密钥/凭据的存取与轮换能力（含审计事件）；不替代应用侧权限控制，不直接暴露业务数据访问语义。



## 验收标准（可检查）



- 在测试环境中完成至少 1 个 secret 的创建→读取→轮换→撤销闭环，并能在审计日志中按 secret 名/时间检索到对应事件记录。



## 已知限制



- 不同环境的权限模型与密钥后端实现差异较大；实施阶段需在契约真源或子契约中固化最小权限策略、轮换周期与回滚策略。

