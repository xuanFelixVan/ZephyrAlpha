---
module_id: VERSION_MANAGEMENT_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 个人开发者
standard_type: 个人开发者版本管理规范
applicable_scope: 个人项目版本控制
compliance_level: 简化标准
parent_document: ../README.md
implementation_status: Active
---

# 版本管理规范（个人开发者版）

> **版本**: v1.0  
> **适用对象**: 个人开发者、AI维护项目  
> **核心理念**: 简单、高效、自动化  
> **工具**: Git + 语义化版本

---

## 🎯 **版本管理目标**

### **个人开发者的核心需求**

- ✅ **简单**: 不需要复杂的审批流程
- ✅ **高效**: 自动化版本管理
- ✅ **清晰**: 版本历史一目了然
- ✅ **可靠**: Git版本控制保障

### **不需要的内容**

- ❌ 多人协作的审批流程
- ❌ 复杂的版本回退机制
- ❌ 分支管理策略（个人开发用main分支即可）
- ❌ 代码审查流程

---

## 📋 **版本命名规范**

### **语义化版本**

格式: `vMAJOR.MINOR.PATCH`

```
v1.0.0  → 初始版本
v1.1.0  → 新增功能（MINOR）
v1.1.1  → Bug修复（PATCH）
v2.0.0  → 重大变更（MAJOR）
```

### **版本类型说明**

| 版本类型 | 说明 | 示例 |
|---------|------|------|
| **MAJOR** | 不兼容的API变更 | v1.0.0 → v2.0.0 |
| **MINOR** | 向后兼容的功能新增 | v1.0.0 → v1.1.0 |
| **PATCH** | 向后兼容的Bug修复 | v1.0.0 → v1.0.1 |

---

## 🔄 **版本管理流程**

### **简化流程（个人开发者）**

```
开发完成 → 提交Git → 创建版本标签 → 更新CHANGELOG → 继续
    ↓          ↓           ↓              ↓           ↓
  代码      commit      git tag      记录变更      下一个功能
```

### **详细步骤**

#### **Step 1: 开发完成**

```bash
# 确保代码已测试
pytest tests/

# 确保文档已更新
# 检查相关文档是否需要更新
```

#### **Step 2: 提交Git**

```bash
# 添加所有变更
git add .

# 提交（使用规范的提交信息）
git commit -m "feat: 添加策略工厂模块

- 实现BaseStrategy基类
- 实现StrategyFactory工厂
- 实现StrategyRegistry注册表
- 添加单元测试"

# 推送到远程仓库
git push origin main
```

#### **Step 3: 创建版本标签**

```bash
# 创建带注释的标签
git tag -a v1.0.0 -m "版本 1.0.0 - 策略工厂模块完成

主要功能:
- 策略工厂核心实现
- 策略注册表
- 策略加载器

改进:
- 性能优化
- 文档完善

修复:
- 修复策略加载Bug"

# 推送标签到远程
git push origin v1.0.0
```

#### **Step 4: 更新CHANGELOG**

```bash
# 编辑CHANGELOG.md
# 添加版本变更记录
```

---

## 📝 **Git提交信息规范**

### **提交信息格式**

```
<type>(<scope>): <subject>

<body>

<footer>
```

### **提交类型**

| 类型 | 说明 | 示例 |
|------|------|------|
| **feat** | 新功能 | feat: 添加策略工厂模块 |
| **fix** | Bug修复 | fix: 修复策略加载错误 |
| **docs** | 文档更新 | docs: 更新API文档 |
| **style** | 代码格式 | style: 格式化代码 |
| **refactor** | 重构 | refactor: 重构策略注册表 |
| **test** | 测试 | test: 添加单元测试 |
| **chore** | 构建/工具 | chore: 更新依赖包 |

### **提交信息示例**

```bash
# 新功能
git commit -m "feat: 添加事件总线模块

- 实现EventBus核心类
- 实现EventHandler基类
- 添加异步事件分发
- 添加单元测试"

# Bug修复
git commit -m "fix: 修复事件订阅重复问题

问题: 同一处理器被重复订阅
原因: 订阅时未检查重复
解决: 添加重复检查逻辑"

# 文档更新
git commit -m "docs: 更新策略工厂使用指南

- 添加使用示例
- 添加API文档
- 添加最佳实践"
```

---

## 🏷️ **版本标签规范**

### **标签命名**

```bash
# 格式: vMAJOR.MINOR.PATCH
v1.0.0  # 正式版本
v1.0.0-beta  # 测试版本
v1.0.0-rc.1  # 候选版本
```

### **标签注释模板**

```bash
git tag -a v1.0.0 -m "版本 1.0.0 - [版本主题]

主要功能:
- 功能1
- 功能2

改进:
- 改进1
- 改进2

修复:
- 修复1
- 修复2

已知问题:
- 问题1
- 问题2"
```

---

## 📊 **CHANGELOG规范**

### **CHANGELOG格式**

```markdown
# 更新日志

所有重要的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)

## [Unreleased]

### 新增
- 待发布的新功能

## [1.0.0] - 2026-04-02

### 新增
- 策略工厂模块
- 事件总线模块
- 回测引擎集成

### 改进
- 性能优化
- 文档完善

### 修复
- 修复策略加载Bug

## [0.1.0] - 2026-04-01

### 新增
- 初始项目结构
- 基础配置文件
```

---

## 🛠️ **自动化工具**

### **版本号自动生成脚本**

```python
# scripts/auto_version.py

import re
import subprocess
from datetime import datetime

def get_current_version():
    """获取当前版本号"""
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except:
        return 'v0.0.0'

def bump_version(current_version, bump_type='patch'):
    """升级版本号"""
    # 提取版本号
    match = re.match(r'v(\d+)\.(\d+)\.(\d+)', current_version)
    if not match:
        return 'v0.0.1'
    
    major, minor, patch = map(int, match.groups())
    
    # 根据类型升级
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    return f'v{major}.{minor}.{patch}'

def create_version_tag(version, message):
    """创建版本标签"""
    subprocess.run(['git', 'tag', '-a', version, '-m', message])
    print(f"✅ 创建版本标签: {version}")

if __name__ == '__main__':
    import sys
    
    bump_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    
    current = get_current_version()
    new_version = bump_version(current, bump_type)
    
    print(f"当前版本: {current}")
    print(f"新版本: {new_version}")
    
    message = input("请输入版本说明: ")
    create_version_tag(new_version, message)
```

**使用方法**:

```bash
# 升级PATCH版本（Bug修复）
python scripts/auto_version.py patch

# 升级MINOR版本（新功能）
python scripts/auto_version.py minor

# 升级MAJOR版本（重大变更）
python scripts/auto_version.py major
```

---

## 📋 **版本发布检查清单**

### **发布前检查**

```markdown
## 版本发布检查清单

### 代码质量
- [ ] 所有测试通过
- [ ] 代码无警告
- [ ] 文档已更新

### 版本管理
- [ ] CHANGELOG已更新
- [ ] 版本号已升级
- [ ] Git标签已创建

### 文档
- [ ] README已更新
- [ ] API文档已更新
- [ ] 使用示例已添加
```

---

## 🎯 **最佳实践**

### **1. 频繁提交**

```bash
# ✅ 好的做法 - 小步提交
git commit -m "feat: 添加BaseStrategy基类"
git commit -m "feat: 添加StrategyFactory工厂"
git commit -m "test: 添加策略工厂单元测试"

# ❌ 不好的做法 - 大步提交
git commit -m "feat: 完成策略工厂模块"
```

### **2. 清晰的提交信息**

```bash
# ✅ 好的做法
git commit -m "feat: 添加策略工厂模块

- 实现BaseStrategy基类
- 实现StrategyFactory工厂
- 添加单元测试"

# ❌ 不好的做法
git commit -m "update"
```

### **3. 定期推送**

```bash
# 每天结束前推送
git push origin main

# 创建标签后推送
git push origin v1.0.0
```

---

## 📚 **参考资料**

### **内部文档**

- [蓝图施工说明书](../CONSTRUCTION_SPECIFICATION.md)
- [文档质量门禁](../06_CHECKLISTS/DOCUMENT_QUALITY_GATE.md)

### **外部资源**

- [语义化版本](https://semver.org/lang/zh-CN/)
- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)
- [Git官方文档](https://git-scm.com/doc)

---

## 📝 **更新记录**

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|---------|--------|
| 2026-04-02 | v1.0 | 创建版本管理规范 | 个人开发者 |

---

## 📞 **联系方式**

**文档维护者**: 个人开发者  
**创建日期**: 2026-04-02  
**最后更新**: 2026-04-02  
**版本**: v1.0
