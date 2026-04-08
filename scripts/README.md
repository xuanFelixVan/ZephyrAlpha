---
standard_type: 技术文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
owner: 文档维护者
version: 1.0.0
module_id: DOC_README_ARCHIVED_2
created_date: 2026-04-01
last_updated: 2026-04-02
responsibility:
  - 模块说明、快速入门、使用指南
---
---
# 脚本目录 (Scripts)

> 清风量化系统 v5.1 - 自动化脚本工具集
> 
> **版本**: v1.0
> **创建日期**: 2026-04-01
> **维护者**: Audit Sentinel
> **定位**: 系统维护和开发辅助脚本

---

## 📋 脚本清单

| 脚本 | 语言 | 功能 | 使用频率 |
|------|------|------|----------|
| [clean_cache.py](clean_cache.py) | Python 3.6+ | 自动化缓存清理 | 每周/每月 |
| [clean_cache.bat](clean_cache.bat) | Windows批处理 | 缓存清理（Windows包装器） | 每周/每月 |

---

## 🧹 缓存清理脚本

### 功能概述
清理项目中的各种缓存文件、测试文件、临时文件，基于 `.gitignore` 文件配置。

### 清理范围
- **Python缓存**: `__pycache__/`, `*.py[cod]`, `*.pyc`, `*.pyo`, `*.pyd`
- **包构建文件**: `build/`, `dist/`, `*.egg-info/`, `*.egg`
- **虚拟环境**: `venv/`, `env/`, `.venv/` (通常保留)
- **IDE文件**: `.vscode/`, `.idea/`, `*.swp`, `*.swo`
- **测试缓存**: `.pytest_cache/`, `.mypy_cache/`, `.coverage`, `htmlcov/`
- **代码质量工具**: `.pylint.d/`, `.flake8`, `.cache/`
- **Notebook缓存**: `.ipynb_checkpoints/`, `*.ipynb_checkpoints`
- **临时文件**: `*~`, `*.bak`, `*.tmp`, `*.temp`, `*.log.*`

### 保留目录（默认不清理）
- `.trae/` - Trae IDE工作区
- `data/` - 数据目录
- `docs/00_RESOURCES/` - 外部文档资源

### 使用方法

#### Python脚本（跨平台）
```bash
# 查看帮助
python scripts/clean_cache.py --help

# 干运行（只显示要清理的文件）
python scripts/clean_cache.py --dry-run --verbose

# 实际清理
python scripts/clean_cache.py

# 清理所有缓存（包括通常保留的目录）
python scripts/clean_cache.py --all

# 详细输出
python scripts/clean_cache.py --verbose
```

#### Windows批处理
```batch
# 查看帮助
clean_cache.bat --help

# 干运行
clean_cache.bat --dry-run --verbose

# 实际清理
clean_cache.bat

# 清理所有
clean_cache.bat --all
```

### 输出示例
```
==========================================================
开始清理项目缓存...
项目根目录: D:\ZephyrAlpha
使用模式数: 45
==========================================================
成功: 文件: .\.coverage
成功: 目录: .\.mypy_cache
成功: 目录: .\.pytest_cache
==========================================================
清理完成!
已清理 1 个文件和 2 个目录
释放空间: 12.55 MB

提示:
1. 可以使用 'git status' 查看清理后的变化
2. 可以使用 'git clean -n' 查看git建议清理的文件
3. 定期运行此脚本可保持项目整洁
```

---

## 🔄 集成到开发工作流

### 手动运行
```bash
# 在项目根目录运行
cd /d D:\ZephyrAlpha
python scripts/clean_cache.py
```

### Git Hook（自动清理）
在 `.git/hooks/pre-commit` 中添加：
```bash
#!/bin/bash
# 在提交前自动清理缓存
python scripts/clean_cache.py --dry-run
if [ $? -eq 0 ]; then
    echo "缓存检查完成"
else
    echo "发现可清理的缓存文件，运行 'python scripts/clean_cache.py' 清理"
fi
```

### 计划任务（Windows）
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置每周执行
4. 程序: `python`
5. 参数: `D:\ZephyrAlpha\scripts\clean_cache.py`

### CI/CD集成
在GitLab CI或GitHub Actions中添加：
```yaml
cache_clean:
  stage: cleanup
  script:
    - python scripts/clean_cache.py
  only:
    - schedules  # 定期执行
```

---

## ⚙️ 配置说明

### 自定义清理规则
脚本从 `.gitignore` 文件读取清理规则。要添加新的清理模式：

1. 编辑 `.gitignore` 文件
2. 添加新的忽略模式
3. 脚本会自动识别并清理

### 排除特定目录
如果要排除某些目录不被清理，即使它们匹配清理模式：
```python
# 在 clean_cache.py 中修改 preserve_dirs 列表
preserve_dirs = [
    ".trae",        # Trae IDE 工作区
    "data",         # 数据目录
    "docs/00_RESOURCES",  # 外部文档资源
    "my_custom_dir",  # 添加你的自定义目录
]
```

### 安全机制
1. **干运行模式**: 使用 `--dry-run` 先查看将要清理的文件
2. **保留目录**: 默认保留重要目录
3. **错误处理**: 单个文件删除失败不影响其他文件
4. **详细日志**: 使用 `--verbose` 查看详细过程

---

## 🚨 注意事项

### 重要警告
1. **虚拟环境**: 脚本默认保留 `venv/`, `env/`, `.venv/` 目录
2. **数据文件**: `data/` 目录默认保留
3. **外部文档**: `docs/00_RESOURCES/` 目录默认保留（包含大文件）
4. **Trae工作区**: `.trae/` 目录默认保留

### 恢复被误删的文件
如果误删了文件：
1. 检查Git历史：`git log --all --full-history -- "路径/文件名"`
2. 使用Git恢复：`git checkout HEAD -- "路径/文件名"`
3. 如果没有版本控制，需要从备份恢复

### 性能考虑
- 首次运行可能需要较长时间扫描整个项目
- 后续运行会更快，因为缓存文件已清理
- 建议在开发间隙或非高峰时间运行

---

## 📝 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-04-01 | 创建缓存清理脚本，支持干运行、详细输出、保留目录 |

---

## 🔗 相关文档

- [.gitignore配置](../.gitignore) - 清理规则来源
- [开发规范](../docs/05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPER_RULES.md) - 开发工作流
-  - 系统监控体系

---

**状态**: ✅ 活跃 | **维护**: Audit Sentinel