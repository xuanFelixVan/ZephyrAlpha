---
module_id: DEV_ENVIRONMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 开发环境标准化
  - 开发容器配置
  - 环境一致性保证
  - 开发工具集成
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: layer_05
---

# 开发环境标准化蓝图

> **核心职责**: 提供标准化的开发环境，确保所有开发者使用一致的开发配置
> **职责边界**: 
> - ✅ 本文档负责：开发环境标准化、开发容器配置、环境一致性保证、开发工具集成
> - ❌ 本文档不负责：生产环境部署（由部署模块负责）、CI/CD配置（由CI/CD模块负责）

## 核心定位

负责开发环境标准化的设计与构建，实现开发环境容器化、开发工具集成、环境一致性保证，确保所有开发者使用一致的开发环境。

## 设计目标

### 主要目标

1. **环境一致性**: 确保所有开发者使用相同的开发环境
2. **快速启动**: 新开发者可以快速启动开发环境
3. **工具集成**: 集成常用开发工具和扩展
4. **版本管理**: 管理开发环境的版本和依赖

### 质量目标

- 环境一致性: 100%
- 环境启动时间: <5分钟
- 工具覆盖率: 100%
- 配置自动化: 100%

## 开源方案选型

### 推荐方案: VS Code DevContainer

| 属性 | 详情 |
|------|------|
| **VS Code** | https://github.com/microsoft/vscode |
| **DevContainer** | https://github.com/microsoft/vscode-dev-containers |
| **Stars** | 155k+ / 4k+ |
| **License** | MIT |
| **特点** | 容器化开发环境 |

**选择理由**:
1. **容器化**: 使用Docker容器隔离开发环境
2. **VS Code集成**: 与VS Code无缝集成
3. **个人友好**: 适合个人开发者使用
4. **跨平台**: 支持Windows、Mac、Linux
5. **配置简单**: 使用JSON配置文件

### 备选方案

| 项目 | Stars | 特点 | 推荐度 |
|------|-------|------|--------|
| **Docker** | 67k+ | 容器化平台 | ⭐⭐⭐⭐⭐ |
| **Vagrant** | 26k+ | 虚拟机管理 | ⭐⭐⭐⭐ |
| **Gitpod** | 1k+ | 云端开发环境 | ⭐⭐⭐⭐ |

## 核心功能设计

### 1. DevContainer配置

```json
// .devcontainer/devcontainer.json
{
  "name": "ZephyrAlpha Development Environment",
  "dockerFile": "Dockerfile",
  "context": "..",
  
  "settings": {
    "python.defaultInterpreterPath": "/usr/local/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=100"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    },
    "files.exclude": {
      "**/__pycache__": true,
      "**/*.pyc": true,
      "**/.pytest_cache": true
    }
  },
  
  "extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-azuretools.vscode-docker",
    "eamodio.gitlens",
    "streetsidesoftware.code-spell-checker",
    "redhat.vscode-yaml",
    "tamasfe.even-better-toml",
    "yzhang.markdown-all-in-one"
  ],
  
  "forwardPorts": [8000, 5432, 6379],
  
  "postCreateCommand": "pip install -r requirements.txt && pip install -r requirements-dev.txt",
  
  "remoteUser": "vscode",
  
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.10"
    },
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/git:1": {
      "version": "latest"
    }
  }
}
```

### 2. Dockerfile配置

```dockerfile
# .devcontainer/Dockerfile
FROM python:3.10-slim

LABEL maintainer="ZephyrAlpha Team"
LABEL description="Development environment for ZephyrAlpha"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    vim \
    htop \
    tree \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

RUN pip install \
    black \
    flake8 \
    pylint \
    mypy \
    isort \
    pytest \
    pytest-cov \
    pytest-asyncio \
    ipython \
    jupyter

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

WORKDIR /workspace

CMD ["sleep", "infinity"]
```

### 3. Docker Compose配置

```yaml
# .devcontainer/docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile
    
    volumes:
      - ..:/workspace:cached
      - ~/.ssh:/home/vscode/.ssh:ro
      - ~/.gitconfig:/home/vscode/.gitconfig:ro
    
    environment:
      - PYTHONPATH=/workspace/src
      - DATABASE_URL=postgresql://test:test@db:5432/zephyr_dev
      - REDIS_URL=redis://redis:6379/0
    
    depends_on:
      - db
      - redis
    
    ports:
      - "8000:8000"
      - "8888:8888"
    
    command: sleep infinity
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: zephyr_dev
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 4. 环境管理工具

```python
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import json

class DevEnvironmentManager:
    """开发环境管理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.devcontainer_dir = self.project_root / ".devcontainer"
    
    def check_environment(self) -> Dict[str, Any]:
        """检查开发环境"""
        checks = {
            "docker_installed": self._check_docker(),
            "docker_running": self._check_docker_running(),
            "vscode_installed": self._check_vscode(),
            "devcontainer_configured": self._check_devcontainer(),
            "python_version": self._check_python_version(),
            "required_ports_available": self._check_ports()
        }
        
        return {
            "all_passed": all(checks.values()),
            "checks": checks
        }
    
    def setup_environment(self):
        """设置开发环境"""
        print("🔧 设置开发环境...")
        
        self._create_devcontainer_dir()
        self._create_dockerfile()
        self._create_devcontainer_json()
        self._create_docker_compose()
        self._create_vscode_settings()
        self._create_vscode_extensions()
        
        print("✅ 开发环境设置完成！")
    
    def start_environment(self):
        """启动开发环境"""
        print("🚀 启动开发环境...")
        
        subprocess.run(
            ["docker-compose", "-f", ".devcontainer/docker-compose.yml", "up", "-d"],
            cwd=self.project_root,
            check=True
        )
        
        print("✅ 开发环境已启动！")
    
    def stop_environment(self):
        """停止开发环境"""
        print("🛑 停止开发环境...")
        
        subprocess.run(
            ["docker-compose", "-f", ".devcontainer/docker-compose.yml", "down"],
            cwd=self.project_root,
            check=True
        )
        
        print("✅ 开发环境已停止！")
    
    def rebuild_environment(self):
        """重建开发环境"""
        print("🔄 重建开发环境...")
        
        subprocess.run(
            ["docker-compose", "-f", ".devcontainer/docker-compose.yml", "down", "-v"],
            cwd=self.project_root,
            check=True
        )
        
        subprocess.run(
            ["docker-compose", "-f", ".devcontainer/docker-compose.yml", "build", "--no-cache"],
            cwd=self.project_root,
            check=True
        )
        
        subprocess.run(
            ["docker-compose", "-f", ".devcontainer/docker-compose.yml", "up", "-d"],
            cwd=self.project_root,
            check=True
        )
        
        print("✅ 开发环境已重建！")
    
    def _check_docker(self) -> bool:
        """检查Docker是否安装"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _check_docker_running(self) -> bool:
        """检查Docker是否运行"""
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _check_vscode(self) -> bool:
        """检查VS Code是否安装"""
        try:
            result = subprocess.run(
                ["code", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _check_devcontainer(self) -> bool:
        """检查DevContainer是否配置"""
        devcontainer_json = self.devcontainer_dir / "devcontainer.json"
        return devcontainer_json.exists()
    
    def _check_python_version(self) -> bool:
        """检查Python版本"""
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True
            )
            version = result.stdout.strip().split()[1]
            major, minor = map(int, version.split('.')[:2])
            return major == 3 and minor >= 10
        except (FileNotFoundError, IndexError):
            return False
    
    def _check_ports(self) -> bool:
        """检查端口是否可用"""
        import socket
        
        ports = [8000, 5432, 6379]
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                return False
        
        return True
    
    def _create_devcontainer_dir(self):
        """创建.devcontainer目录"""
        self.devcontainer_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_dockerfile(self):
        """创建Dockerfile"""
        dockerfile_content = """FROM python:3.10-slim

LABEL maintainer="ZephyrAlpha Team"

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

RUN pip install \\
    black \\
    flake8 \\
    pylint \\
    mypy \\
    isort \\
    pytest \\
    pytest-cov

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \\
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

USER $USERNAME

WORKDIR /workspace

CMD ["sleep", "infinity"]
"""
        
        dockerfile_path = self.devcontainer_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content, encoding='utf-8')
    
    def _create_devcontainer_json(self):
        """创建devcontainer.json"""
        config = {
            "name": "ZephyrAlpha Dev Environment",
            "dockerFile": "Dockerfile",
            "context": "..",
            "settings": {
                "python.defaultInterpreterPath": "/usr/local/bin/python",
                "python.linting.enabled": True,
                "python.formatting.provider": "black"
            },
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance"
            ],
            "forwardPorts": [8000, 5432, 6379]
        }
        
        config_path = self.devcontainer_dir / "devcontainer.json"
        config_path.write_text(json.dumps(config, indent=2), encoding='utf-8')
    
    def _create_docker_compose(self):
        """创建docker-compose.yml"""
        compose_content = """version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace:cached
    ports:
      - "8000:8000"
    command: sleep infinity
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: zephyr_dev
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
"""
        
        compose_path = self.devcontainer_dir / "docker-compose.yml"
        compose_path.write_text(compose_content, encoding='utf-8')
    
    def _create_vscode_settings(self):
        """创建VS Code设置"""
        settings_dir = self.project_root / ".vscode"
        settings_dir.mkdir(exist_ok=True)
        
        settings = {
            "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True,
            "python.formatting.provider": "black",
            "editor.formatOnSave": True
        }
        
        settings_path = settings_dir / "settings.json"
        settings_path.write_text(json.dumps(settings, indent=2), encoding='utf-8')
    
    def _create_vscode_extensions(self):
        """创建VS Code扩展推荐"""
        recommendations = {
            "recommendations": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "ms-azuretools.vscode-docker",
                "eamodio.gitlens"
            ]
        }
        
        extensions_path = self.project_root / ".vscode" / "extensions.json"
        extensions_path.write_text(json.dumps(recommendations, indent=2), encoding='utf-8')
```

### 5. GitHub Actions集成

```yaml
# .github/workflows/dev-environment.yml
name: Dev Environment Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  check-environment:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Check DevContainer configuration
      run: |
        if [ -f ".devcontainer/devcontainer.json" ]; then
          echo "✅ DevContainer配置存在"
        else
          echo "❌ DevContainer配置缺失"
          exit 1
        fi
    
    - name: Validate Dockerfile
      run: |
        if [ -f ".devcontainer/Dockerfile" ]; then
          echo "✅ Dockerfile存在"
        else
          echo "❌ Dockerfile缺失"
          exit 1
        fi
    
    - name: Test DevContainer build
      run: |
        docker build -t zephyr-dev -f .devcontainer/Dockerfile .
```

## 部署架构

### 本地开发环境

```bash
# 检查环境
python scripts/check_dev_environment.py

# 设置环境
python scripts/setup_dev_environment.py

# 启动环境
docker-compose -f .devcontainer/docker-compose.yml up -d

# 在VS Code中打开
code .

# 使用DevContainer
# 按 F1 -> "Dev Containers: Reopen in Container"
```

### 环境验证

```bash
# 验证Python版本
python --version

# 验证依赖
pip list

# 验证数据库连接
psql -h localhost -U test -d zephyr_dev

# 验证Redis连接
redis-cli -h localhost -p 6379 ping
```

## 实施计划

### 阶段1: 环境配置 (Day 1)

| 任务 | 工时 | 负责人 | 交付物 |
|------|------|--------|--------|
| DevContainer配置 | 2h | 开发者 | devcontainer.json |
| Dockerfile编写 | 2h | 开发者 | Dockerfile |
| Docker Compose配置 | 1h | 开发者 | docker-compose.yml |

### 阶段2: 工具集成 (Day 2)

| 任务 | 工时 | 负责人 | 交付物 |
|------|------|--------|--------|
| VS Code配置 | 1h | 开发者 | settings.json |
| 扩展推荐 | 1h | 开发者 | extensions.json |
| 环境管理工具 | 2h | 开发者 | 管理脚本 |

## 性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| **环境启动时间** | <5分钟 | Docker启动时间 |
| **环境一致性** | 100% | 环境检查通过率 |
| **工具覆盖率** | 100% | 工具安装完整性 |
| **配置自动化** | 100% | 自动化脚本覆盖率 |

## 成本估算

| 项目 | 开源方案成本 | 商业方案成本 |
|------|-------------|-------------|
| **软件许可** | $0 | $0 |
| **VS Code** | 免费 | 免费 |
| **Docker** | 免费 | 免费 |
| **总成本** | **$0** | **$0** |

## 最佳实践

### 1. 环境隔离

```json
// 使用不同的环境变量
{
  "containerEnv": {
    "PYTHONPATH": "/workspace/src",
    "DATABASE_URL": "postgresql://test:test@db:5432/zephyr_dev"
  }
}
```

### 2. 持久化配置

```yaml
# 持久化数据卷
volumes:
  - postgres_data:/var/lib/postgresql/data
  - redis_data:/data
```

### 3. 开发工具集成

```json
// 推荐的VS Code扩展
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-azuretools.vscode-docker"
  ]
}
```

---

**文档版本**: v1.0.0
**创建日期**: 2026-04-07
**最后更新**: 2026-04-07
**状态**: Active

## 接口与契约（蓝图终稿）

- **契约真源**：`API_Contract.md`
- **对外接口边界**：本模块定义开发环境的构建、依赖与工具链集成口径；不直接定义业务 API 细节，不替代运行时服务之间的接口子契约。

## 验收标准（可检查）

- 按本蓝图指引在一台干净机器完成环境搭建，并成功执行至少 1 条端到端健康检查（例如启动关键依赖服务并通过基础连通性自检）。

## 已知限制

- 不同操作系统与硬件环境存在兼容性差异；实施阶段需在契约真源或子契约中固化最低版本矩阵与已知问题清单。
