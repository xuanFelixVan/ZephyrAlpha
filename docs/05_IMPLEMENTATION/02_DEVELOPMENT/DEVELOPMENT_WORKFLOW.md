---
module_id: IMPL_DOC_001
version: 5.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部署
compliance_level: 实施标准
parent_document: ../INDEX.md
implementation_status: 进行中
---


# 开发工作流程

> 清风量化系统 v5.1 的开发流程、提交规范、依赖管理
>
> **文档来源**: 由 DEVELOPER_RULES.md 拆分而来，遵循职责驱动原则
> **相关文档**: [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md), [DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md)


## 一、开发流程

### 1.1 标准开发流程

```
1. 创建分支
   git checkout -b feature/xxx

2. 编写代码
   - 遵循命名规范
   - 添加类型提示
   - 编写文档字符串
   - 添加单元测试

3. 本地测试
   pytest tests/ -v

4. 提交代码
   git add .
   git commit -m "feat: 描述"

5. 推送
   git push origin feature/xxx

6. 合并（审核后）
   git checkout main
   git merge feature/xxx
```

### 1.2 功能开发阶段

| 阶段 | 活动 | 输出 |
|------|------|------|
| **需求分析** | 明确功能边界、优先级 | 需求文档 |
| **技术设计** | API设计、数据库设计 | 设计文档 |
| **编码实现** | 实现核心功能 | 代码、单元测试 |
| **本地测试** | 功能测试、集成测试 | 测试报告 |
| **代码审查** | 同行评审 | 审查记录 |
| **部署上线** | 发布到测试/生产环境 | 部署记录 |


## 二、提交规范

### 2.1 提交信息格式

```bash
# ✅ 正确
git commit -m "feat: 添加S001策略"
git commit -m "fix: 修复因子计算错误"
git commit -m "docs: 更新README"
git commit -m "test: 添加单元测试"
git commit -m "refactor: 重构DataHub模块"
git commit -m "style: 代码格式调整"

# ❌ 错误
git commit -m "update"
git commit -m "fix bug"
git commit -m "WIP"
git commit -m "."
```

### 2.2 提交类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| **feat** | 新功能 | `feat: 添加MACD策略` |
| **fix** | 错误修复 | `fix: 修复数据读取错误` |
| **docs** | 文档更新 | `docs: 更新API文档` |
| **test** | 测试相关 | `test: 添加DataHub测试` |
| **refactor** | 重构代码 | `refactor: 重构因子计算模块` |
| **style** | 代码格式 | `style: 修复代码格式` |
| **perf** | 性能优化 | `perf: 优化数据查询性能` |
| **chore** | 构建/工具 | `chore: 更新依赖版本` |

### 2.3 提交信息结构

```
<type>(<scope>): <subject>

<body>

<footer>
```

**示例**:
```
feat(strategy): 添加趋势跟踪策略

- 实现双均线趋势策略
- 添加止损/止盈机制
- 集成到策略引擎

Closes #123
```


## 三、依赖管理

### 3.1 添加依赖流程

```bash
# 1. 安装到虚拟环境
pip install package_name

# 2. 更新 requirements.txt
pip freeze > requirements.txt

# 3. 更新 pyproject.toml（如果是项目依赖）
```

### 3.2 依赖版本策略

```txt
# requirements.txt
package>=1.0.0        # 最低版本
package==1.2.3        # 固定版本（生产环境）
package~=2.1.0        # 兼容版本（2.1.x）
```

### 3.3 依赖分类管理

```txt
# 核心依赖（必须）
numpy>=1.20.0
pandas>=1.3.0

# 可选依赖
backtrader>=1.9.0     # 回测引擎
fastapi>=0.68.0       # API框架

# 开发依赖
pytest>=6.2.0
black>=21.0.0         # 代码格式化
```


## 四、日志规范

### 4.1 日志级别

```python
from loguru import logger

logger.info("信息日志")        # 普通信息
logger.warning("警告日志")     # 警告信息
logger.error("错误日志")       # 错误信息
logger.debug("调试日志")       # 调试信息
logger.critical("严重日志")    # 严重错误
```

### 4.2 日志文件位置

```
logs/
├── app.log           # 应用日志
├── error.log         # 错误日志
├── trading.log       # 交易日志
└── audit.log         # 审计日志
```

### 4.3 日志格式配置

```python
import sys
from loguru import logger

# 控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 文件输出
logger.add(
    "logs/app.log",
    rotation="100 MB",        # 每100MB轮转
    retention="30 days",      # 保留30天
    compression="zip",        # 压缩存储
    level="DEBUG"
)
```


## 五、版本控制

### 5.1 分支策略

| 分支 | 目的 | 生命周期 |
|------|------|----------|
| **main** | 生产环境代码 | 长期存在 |
| **develop** | 开发环境代码 | 长期存在 |
| **feature/*** | 功能开发 | 合并后删除 |
| **release/*** | 版本发布 | 发布后删除 |
| **hotfix/*** | 紧急修复 | 修复后删除 |

### 5.2 版本号规范

```
主版本.次版本.修订版本
```

- **主版本**: 不兼容的API变更
- **次版本**: 向下兼容的功能新增
- **修订版本**: 向下兼容的问题修复

### 5.3 标签管理

```bash
# 创建标签
git tag -a v1.2.3 -m "版本1.2.3发布"

# 推送标签
git push origin v1.2.3

# 查看标签
git tag -l
```


## 六、代码审查

### 6.1 审查要点

| 类别 | 检查项 |
|------|--------|
| **代码质量** | 命名规范、代码复杂度、重复代码 |
| **功能正确** | 需求满足、边界条件、错误处理 |
| **测试覆盖** | 单元测试、集成测试、测试用例 |
| **安全合规** | 安全漏洞、敏感数据处理 |
| **性能影响** | 内存使用、时间复杂度 |

### 6.2 审查流程

1. **创建PR**: 提交代码到GitHub/GitLab
2. **自动检查**: CI/CD运行测试和检查
3. **人工审查**: 至少1人审查通过
4. **修改反馈**: 根据审查意见修改
5. **批准合并**: 审查者批准后合并


> **维护部门**: 清风量化开发部
> **最后更新**: 2026-04-01
> **文档版本**: v5.1

**相关文档**:
- [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md) - 开发标准与规范
- [DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md) - 设计原则
- [DEVELOPER_RULES.md](./DEVELOPER_RULES.md) - 原文档（已拆分）
