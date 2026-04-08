---
module_id: DEPENDENCY_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 依赖管理
  - 版本控制
  - 依赖解析
  - 环境隔离
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: Layer 5 (开发工具层)
---

# 依赖管理蓝图

> **核心职责**: 提供现代化的Python依赖管理，确保依赖版本一致性、可重现性
> **职责边界**: 
> - ✅ 本文档负责：依赖管理、版本控制、环境隔离、依赖解析
> - ❌ 本文档不负责：代码质量（由代码质量检查负责）、安全扫描（由安全扫描负责）

## 核心定位

负责依赖管理模块的设计与构建，实现依赖版本控制、依赖解析、环境隔离，确保项目依赖的一致性和可重现性。

## 设计目标

### 主要目标

1. **依赖版本控制**: 精确控制依赖版本，避免版本冲突
2. **环境隔离**: 确保不同项目的依赖隔离
3. **依赖解析**: 自动解析依赖关系，避免冲突
4. **可重现构建**: 确保构建环境的可重现性

### 质量目标

- 依赖版本锁定: 100%
- 环境隔离: 100%
- 依赖冲突率: 0%
- 构建可重现率: 100%

## 开源方案选型

### 推荐方案: Poetry

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/python-poetry/poetry |
| **Stars** | 29k+ |
| **License** | MIT |
| **特点** | 现代化Python依赖管理工具 |

**选择理由**:
1. **一体化解决方案**: 依赖管理 + 虚拟环境 + 构建发布
2. **依赖解析优秀**: 使用先进的依赖解析算法
3. **版本锁定**: 自动生成poetry.lock确保可重现性
4. **个人友好**: 简单易用，适合个人开发者
5. **社区活跃**: 活跃的社区和完善的文档

### 备选方案

| 项目 | Stars | 特点 | 推荐度 |
|------|-------|------|--------|
| **pip-tools** | 7k+ | pip + pip-compile | ⭐⭐⭐⭐ |
| **Pipenv** | 24k+ | Pipfile + 虚拟环境 | ⭐⭐⭐⭐ |
| **Conda** | 6k+ | 科学计算环境管理 | ⭐⭐⭐ |

## 核心功能设计

### 1. Poetry配置文件

```toml
# pyproject.toml
[tool.poetry]
name = "zephyr-alpha"
version = "5.2.0"
description = "清风量化交易系统"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
packages = [{include = "src"}]

[tool.poetry.dependencies]
python = "^3.10"
numpy = "^1.24.0"
pandas = "^2.0.0"
scipy = "^1.10.0"
scikit-learn = "^1.3.0"
matplotlib = "^3.7.0"
seaborn = "^0.12.0"
sqlalchemy = "^2.0.0"
psycopg2-binary = "^2.9.0"
redis = "^4.5.0"
celery = "^5.3.0"
fastapi = "^0.100.0"
uvicorn = "^0.23.0"
pydantic = "^2.0.0"
python-dotenv = "^1.0.0"
pyyaml = "^6.0"
requests = "^2.31.0"
aiohttp = "^3.8.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
pytest-asyncio = "^0.21.0"
black = "^23.7.0"
flake8 = "^6.1.0"
mypy = "^1.4.0"
pylint = "^2.17.0"
isort = "^5.12.0"
pre-commit = "^3.3.0"

[tool.poetry.group.docs.dependencies]
sphinx = "^7.1.0"
sphinx-rtd-theme = "^1.2.0"
myst-parser = "^2.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 2. 依赖管理工具类

```python
import subprocess
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

class DependencyManager:
    """依赖管理器"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.pyproject_path = self.project_path / "pyproject.toml"
        self.lock_path = self.project_path / "poetry.lock"
    
    def install_dependencies(
        self,
        group: Optional[str] = None,
        dev: bool = False
    ) -> Dict[str, Any]:
        """安装依赖"""
        cmd = ["poetry", "install"]
        
        if group:
            cmd.extend(["--with", group])
        if dev:
            cmd.append("--with-dev")
        
        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def add_dependency(
        self,
        package: str,
        group: Optional[str] = None,
        dev: bool = False
    ) -> Dict[str, Any]:
        """添加依赖"""
        cmd = ["poetry", "add", package]
        
        if group:
            cmd.extend(["--group", group])
        elif dev:
            cmd.append("--group dev")
        
        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "package": package,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def remove_dependency(
        self,
        package: str,
        group: Optional[str] = None
    ) -> Dict[str, Any]:
        """移除依赖"""
        cmd = ["poetry", "remove", package]
        
        if group:
            cmd.extend(["--group", group])
        
        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "package": package,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def update_dependencies(
        self,
        package: Optional[str] = None
    ) -> Dict[str, Any]:
        """更新依赖"""
        cmd = ["poetry", "update"]
        
        if package:
            cmd.append(package)
        
        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def show_dependencies(
        self,
        tree: bool = False,
        outdated: bool = False
    ) -> Dict[str, Any]:
        """查看依赖"""
        cmd = ["poetry", "show"]
        
        if tree:
            cmd.append("--tree")
        if outdated:
            cmd.append("--outdated")
        
        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        dependencies = self._parse_show_output(result.stdout)
        
        return {
            "success": result.returncode == 0,
            "dependencies": dependencies,
            "output": result.stdout
        }
    
    def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖"""
        result = subprocess.run(
            ["poetry", "check"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "valid": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def lock_dependencies(self) -> Dict[str, Any]:
        """锁定依赖"""
        result = subprocess.run(
            ["poetry", "lock"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def export_requirements(
        self,
        output_file: str = "requirements.txt",
        dev: bool = False,
        hash: bool = True
    ) -> Dict[str, Any]:
        """导出requirements.txt"""
        cmd = ["poetry", "export", "-f", "requirements.txt", "-o", output_file]
        
        if dev:
            cmd.append("--with-dev")
        if hash:
            cmd.append("--hash")
        
        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output_file": output_file,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def get_virtualenv_path(self) -> Optional[str]:
        """获取虚拟环境路径"""
        result = subprocess.run(
            ["poetry", "env", "info", "--path"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    
    def create_virtualenv(
        self,
        python: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建虚拟环境"""
        cmd = ["poetry", "env", "use"]
        
        if python:
            cmd.append(python)
        else:
            cmd.append("python3.10")
        
        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def _parse_show_output(self, output: str) -> List[Dict[str, str]]:
        """解析show输出"""
        dependencies = []
        for line in output.split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    dependencies.append({
                        "name": parts[0],
                        "version": parts[1],
                        "description": " ".join(parts[2:]) if len(parts) > 2 else ""
                    })
        return dependencies


class DependencyAnalyzer:
    """依赖分析器"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.manager = DependencyManager(project_path)
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """分析依赖"""
        dependencies = self.manager.show_dependencies()
        outdated = self.manager.show_dependencies(outdated=True)
        
        return {
            "total_dependencies": len(dependencies.get("dependencies", [])),
            "outdated_dependencies": len(outdated.get("dependencies", [])),
            "dependencies": dependencies.get("dependencies", []),
            "outdated": outdated.get("dependencies", []),
            "virtualenv_path": self.manager.get_virtualenv_path()
        }
    
    def check_security_vulnerabilities(self) -> Dict[str, Any]:
        """检查安全漏洞"""
        result = subprocess.run(
            ["poetry", "audit"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "has_vulnerabilities": result.returncode != 0,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def generate_dependency_report(self) -> Dict[str, Any]:
        """生成依赖报告"""
        analysis = self.analyze_dependencies()
        check_result = self.manager.check_dependencies()
        
        return {
            "project_path": str(self.project_path),
            "pyproject_exists": (self.project_path / "pyproject.toml").exists(),
            "lock_exists": (self.project_path / "poetry.lock").exists(),
            "check_valid": check_result.get("valid", False),
            "total_dependencies": analysis["total_dependencies"],
            "outdated_dependencies": analysis["outdated_dependencies"],
            "virtualenv_path": analysis["virtualenv_path"],
            "recommendations": self._generate_recommendations(analysis, check_result)
        }
    
    def _generate_recommendations(
        self,
        analysis: Dict[str, Any],
        check_result: Dict[str, Any]
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if not check_result.get("valid", False):
            recommendations.append("修复pyproject.toml配置问题")
        
        if analysis["outdated_dependencies"] > 0:
            recommendations.append(f"更新{analysis['outdated_dependencies']}个过时的依赖")
        
        if not analysis["virtualenv_path"]:
            recommendations.append("创建虚拟环境")
        
        return recommendations
```

### 3. GitHub Actions集成

```yaml
# .github/workflows/dependency-check.yml
name: Dependency Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: latest
        virtualenvs-create: true
        virtualenvs-in-project: true
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        cache: 'poetry'
    
    - name: Install dependencies
      run: poetry install --no-interaction
    
    - name: Check dependencies
      run: poetry check
    
    - name: Check for outdated dependencies
      run: poetry show --outdated
    
    - name: Export requirements.txt
      run: poetry export -f requirements.txt -o requirements.txt --without-hashes
    
    - name: Security audit
      run: poetry audit
      continue-on-error: true
```

## 部署架构

### 本地开发环境

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 配置Poetry
poetry config virtualenvs.in-project true
poetry config installer.parallel true

# 创建项目
poetry new zephyr-alpha
cd zephyr-alpha

# 初始化现有项目
poetry init

# 安装依赖
poetry install

# 添加依赖
poetry add numpy pandas

# 添加开发依赖
poetry add --group dev pytest black flake8

# 更新依赖
poetry update

# 查看依赖树
poetry show --tree

# 导出requirements.txt
poetry export -f requirements.txt -o requirements.txt
```

### CI/CD集成

```yaml
# GitHub Actions自动依赖检查
# 每次提交检查依赖
# 每周检查过时依赖
# 自动安全审计
```

## 实施计划

### 阶段1: 基础配置 (Day 1)

| 任务 | 工时 | 负责人 | 交付物 |
|------|------|--------|--------|
| 安装Poetry | 0.5h | 开发者 | Poetry安装 |
| 创建pyproject.toml | 1h | 开发者 | 配置文件 |
| 迁移现有依赖 | 2h | 开发者 | 依赖迁移 |
| 测试安装 | 0.5h | 开发者 | 测试报告 |

### 阶段2: CI/CD集成 (Day 1)

| 任务 | 工时 | 负责人 | 交付物 |
|------|------|--------|--------|
| GitHub Actions配置 | 1h | 开发者 | 工作流文件 |
| 依赖检查流程 | 1h | 开发者 | 检查流程 |
| 安全审计配置 | 1h | 开发者 | 审计配置 |

### 阶段3: 文档和培训 (Day 1)

| 任务 | 工时 | 负责人 | 交付物 |
|------|------|--------|--------|
| 使用文档编写 | 1h | 开发者 | 使用文档 |
| 最佳实践指南 | 1h | 开发者 | 指南文档 |

## 性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| **依赖安装时间** | <2分钟 | poetry install耗时 |
| **依赖冲突率** | 0% | 依赖解析失败次数 |
| **版本锁定率** | 100% | poetry.lock存在 |
| **安全漏洞数** | 0个 | poetry audit结果 |

## 成本估算

| 项目 | 开源方案成本 | 商业方案成本 |
|------|-------------|-------------|
| **软件许可** | $0 | $0 |
| **Poetry** | 免费 | 免费 |
| **总成本** | **$0** | **$0** |

## 最佳实践

### 1. 依赖分组

```toml
[tool.poetry.dependencies]
# 生产环境依赖

[tool.poetry.group.dev.dependencies]
# 开发环境依赖

[tool.poetry.group.docs.dependencies]
# 文档生成依赖

[tool.poetry.group.test.dependencies]
# 测试依赖
```

### 2. 版本约束

```toml
# 推荐：使用^版本约束
numpy = "^1.24.0"  # >=1.24.0, <2.0.0

# 避免：使用*通配符
numpy = "*"  # 不推荐

# 精确版本（特殊情况）
numpy = "1.24.3"  # 精确版本
```

### 3. 依赖更新策略

```bash
# 定期更新所有依赖
poetry update

# 更新单个依赖
poetry update numpy

# 检查过时依赖
poetry show --outdated
```

---

**文档版本**: v1.0.0
**创建日期**: 2026-04-07
**最后更新**: 2026-04-07
**状态**: Active
