# 开发规范 (Development Standards)

> **适用**: 个人开发者  
> **状态**: 必须遵守核心规范

---

##  文档导航

| 文档 | 说明 | 重要性 |
|------|------|--------|
| [code-quality.md](./code-quality.md) | 代码质量标准 |  必须 |
| [config-standard.md](./config-standard.md) | 配置文件标准 |  必须 |
| [error-handling.md](./error-handling.md) | 错误处理规范 |  必须 |
| [logging-standard.md](./logging-standard.md) | 日志记录规范 |  必须 |
| [path-standard.md](./path-standard.md) | 路径处理规范 |  建议 |
| [testing-standard.md](./testing-standard.md) | 测试规范 |  建议 |
| [security.md](./security.md) | 安全规范 |  必须 |

---

##  必须遵守（安全红线）

以下规范**必须遵守**，否则可能导致严重问题：

### 1. 禁止硬编码密钥

```python
#  错误
api_key = "sk_live_xxxxx"

#  正确
import os
api_key = os.getenv("API_KEY")
```

### 2. 所有配置使用 YAML 文件

```python
#  错误
threshold = 0.05

#  正确
# config.yaml: threshold: 0.05
config = load_config()
threshold = config["threshold"]
```

### 3. 错误必须记录日志

```python
#  错误
try:
    risky_operation()
except Exception as e:
    pass

#  正确
try:
    risky_operation()
except Exception as e:
    logger.error(f"操作失败：{e}", exc_info=True)
```

### 4. 敏感信息使用环境变量

```bash
# .env 文件
API_KEY=your_secret_key
DB_PASSWORD=your_password
```

---

##  建议遵守（最佳实践）

以下规范**建议遵守**，提升代码质量：

### 1. 函数添加文档字符串

```python
def calculate_sharpe(returns):
    """
    计算夏普比率

    Args:
        returns: 收益率序列

    Returns:
        float: 夏普比率
    """
    return returns.mean() / returns.std()
```

### 2. 编写单元测试

```python
def test_calculate_sharpe():
    returns = pd.Series([0.01, 0.02, -0.01])
    assert calculate_sharpe(returns) > 0
```

### 3. 代码格式化工整

```bash
# 使用 Black 格式化
black src/

# 使用 isort 排序导入
isort src/
```

---

##  可选遵守（锦上添花）

- 参与贡献时遵循完整规范
- 使用类型注解
- 保持函数简洁（< 50 行）

---

##  学习路径

1. **新手**: 先遵守  必须规范
2. **进阶**: 遵守  建议规范
3. **专家**: 遵循所有规范，参与改进

---

##  相关文档

- [快速开始](../01_QUICKSTART/README.md)
- [常见问题](../04_OPERATIONS/faq.md)

---

**最后更新**: 2026-03-28  
**状态**:  可用
