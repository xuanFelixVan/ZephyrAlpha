# CODE_QUALITY.md - 代码质量标准

> **版本**：v4.0
> **更新日期**：2026-03-28
> **状态**：已制定

---

## 1. 代码状态标记规范

### 1.1 状态标记定义

| 旧标记 | 新标记 | 含义 | 颜色 |
|--------|--------|------|------|
| `{# TODO: 回测阶段实现}` | `[PLACEHOLDER: TODO: 回测阶段实现]` | 待实现代码 | 红色 |
| `{# EXAMPLE: 研究阶段示例}` | `[STUDY_ONLY: 示例代码]` | 仅用于研究的示例 | 黄色 |
| `{# EXECUTABLE: 验证代码}` | `[EXECUTABLE: 已验证可运行]` | 可执行代码 | 绿色 |

### 1.2 标记使用示例

```python
# ✅ 正确示例
def calculate_factor(stock_data):
    """
    计算因子值

    [PLACEHOLDER: TODO: 回测阶段实现 - 需要添加缓存机制]
    """
    pass

# ❌ 错误示例
def calculate_factor(stock_data):
    """
    # TODO: 回测阶段实现
    """
    pass
```

### 1.3 代码文件头部模板

```python
"""
模块名称：[MODULE_NAME]
功能描述：[DESCRIPTION]
代码状态：[PLACEHOLDER | STUDY_ONLY | EXECUTABLE]
创建日期：[YYYY-MM-DD]
最后更新：[YYYY-MM-DD]
依赖模块：[DEPENDENCIES]
配置位置：[CONFIG_PATH]
"""

# [STUDY_ONLY: 此代码仅用于研究，不可用于生产]
# [PLACEHOLDER: 此代码待实现]
# [EXECUTABLE: 此代码已验证可运行]
```

---

## 2. 代码命名规范

### 2.1 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| Python模块 | snake_case | `data_collector.py` |
| 配置文件 | snake_case | `system_config.yaml` |
| 测试文件 | `test_*.py` | `test_data_collector.py` |
| 文档文件 | kebab-case | `code-quality.md` |

### 2.2 函数命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 普通函数 | snake_case | `calculate_rsi()` |
| 私有函数 | `_snake_case` | `_validate_data()` |
| 异步函数 | `async_snake_case` | `async_fetch_data()` |

### 2.3 类命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 普通类 | PascalCase | `DataCollector` |
| 异常类 | PascalCase + Exception | `DataException` |
| 数据类 | PascalCase | `MarketData` |

---

## 3. 代码格式规范

### 3.1 Python PEP 8

```python
# 行长度：最大100字符
# 缩进：4个空格
# 变量命名：snake_case
# 类命名：PascalCase
# 常量命名：UPPER_SNAKE_CASE
```

### 3.2 导入顺序

```python
# 1. 标准库
import os
import sys
from datetime import datetime

# 2. 第三方库
import pandas as pd
import numpy as np

# 3. 本地模块
from src.core.base import Result
from src.modules.data_collector import DataCollector

# 4. 配置文件
from config import settings
```

---

## 4. 代码文档规范

### 4.1 Docstring格式

```python
def calculate_factor(factor_id: str, date: str, params: dict = None) -> Result:
    """
    计算指定因子的值

    Parameters:
        factor_id (str): 因子ID
        date (str): 计算日期，格式 YYYY-MM-DD
        params (dict, optional): 因子参数字典

    Returns:
        Result: 包含计算结果的Result对象

    Raises:
        FactorException: 因子计算失败时抛出

    [PLACEHOLDER: TODO: 添加缓存机制]
    """
    pass
```

### 4.2 注释规范

```python
# ✅ 好的注释：解释为什么，不是做什么
# 使用缓存避免重复计算（因为因子计算开销大）
cache_key = f"{factor_id}_{date}"

# ❌ 坏的注释：重复代码内容
# 将因子ID和日期组合成缓存键
cache_key = f"{factor_id}_{date}"
```

---

## 5. 硬编码禁止规范

### 5.1 禁止的硬编码

| 类型 | 示例 | 正确做法 |
|------|------|----------|
| 数据源 | `url = "http://api.example.com"` | `url = config.get("data_source.url")` |
| 阈值 | `if price > 100:` | `if price > config.get("threshold.price"):` |
| 路径 | `path = "/data/raw"` | `path = config.get("paths.raw_data")` |
| 字符串 | `status = "active"` | `status = Status.ACTIVE.value` |

### 5.2 配置文件引用模式

```python
# ✅ 正确：从配置读取
MAX_POSITION = config.get("risk.max_single_position", 0.2)

# ❌ 错误：硬编码
MAX_POSITION = 0.2
```

---

## 6. 测试规范

### 6.1 测试文件结构

```python
# test_data_collector.py

import pytest
from src.modules.data_collector import DataCollector

class TestDataCollector:
    """DataCollector测试类"""

    @pytest.fixture
    def collector(self):
        """测试fixture"""
        return DataCollector()

    def test_collect_returns_dataframe(self, collector):
        """测试collect返回有效数据"""
        result = collector.collect("stock", ["000001"], "2026-01-01", "2026-01-31")
        assert result.is_success
        assert result.data is not None
```

### 6.2 测试覆盖率要求

| 模块类型 | 最低覆盖率 |
|----------|-----------|
| 核心模块 | 80% |
| 业务逻辑 | 70% |
| 工具函数 | 60% |

---

## 7. 代码审查清单

### 7.1 提交前检查

```
□ 所有硬编码已替换为配置引用
□ 所有TODO已标记为 [PLACEHOLDER]
□ 所有示例代码标记为 [STUDY_ONLY]
□ 所有可执行代码标记为 [EXECUTABLE]
□ 所有函数有docstring
□ 测试覆盖率达到要求
□ 代码通过flake8检查
□ 代码通过black格式化
```

### 7.2 审查重点

1. **硬编码检查**：搜索数字、字符串常量
2. **路径检查**：确保使用相对路径或配置路径
3. **异常处理**：检查是否有裸露的except语句
4. **敏感信息**：检查是否包含API密钥、密码等

---

## 8. 相关文档

| 文档 | 说明 |
|------|------|
| [CONFIG_STANDARD.md](./CONFIG_STANDARD.md) | 配置文件标准 |
| [ERROR_HANDLING.md](./ERROR_HANDLING.md) | 错误处理规范 |
| [SECURITY.md](./SECURITY.md) | 安全规范 |

---

*最后更新：2026-03-28*
