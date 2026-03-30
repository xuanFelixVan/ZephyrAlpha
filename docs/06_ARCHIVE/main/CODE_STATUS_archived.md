# 文档状态标记规范

> 代码示例的状态定义与使用指南
>
> **版本**：v2.0
> **更新日期**：2026-03-28

---

## 1. 代码状态分类

### 1.1 三种状态

| 状态 | 标记 | 含义 | 使用场景 |
|------|------|------|----------|
| **待实现** | `[PLACEHOLDER]` | 逻辑已设计，代码待实现 | 策略框架、接口定义 |
| **研究阶段** | `[STUDY_ONLY]` | 用于说明逻辑，不可运行 | 策略示例、计算公式 |
| **可执行** | `[EXECUTABLE]` | 代码已验证，可执行 | 回测代码、工具函数 |

### 1.2 状态标记格式

```markdown
<!-- 状态标记格式 -->
[PLACEHOLDER] 逻辑已设计，待实现具体代码
[STUDY_ONLY] 研究阶段示例，不可用于生产
[EXECUTABLE] 已验证可运行
```

---

## 2. 新旧标记对照

### 2.1 标记格式变更

| 旧格式 | 新格式 | 说明 |
|--------|--------|------|
| `{# TODO: 回测阶段实现}` | `[PLACEHOLDER]` | 简洁明了 |
| `{# EXAMPLE: 研究阶段示例}` | `[STUDY_ONLY]` | 明确用途 |
| `{# EXECUTABLE: 已验证可运行}` | `[EXECUTABLE]` | 简洁明确 |

### 2.2 更新示例

```markdown
<!-- 旧格式 -->
{# TODO: 回测阶段实现 #}
{# EXAMPLE: 研究阶段示例 #}
{# EXECUTABLE: 已验证可运行 #}

<!-- 新格式 -->
[PLACEHOLDER] 待回测阶段实现
[STUDY_ONLY] 仅供研究参考
[EXECUTABLE] 已验证可执行
```

---

## 3. 示例代码标记规则

### 3.1 策略示例代码

```python
[STUDY_ONLY] 超强势股策略示例 - 待回测验证
class UltraStrongStockStrategy(BaseStrategy):
    """
    只做超强势股策略

    逻辑说明：
    - 涨幅 > 5%
    - 成交额 > 10亿
    - 换手率 > 10%
    - 属于热点板块

    回测阶段需要：
    1. 接入历史数据源
    2. 验证参数合理性
    3. 加入风控逻辑
    """
    pass  # [PLACEHOLDER] 待回测阶段实现具体逻辑
```

### 3.2 框架代码标记

```python
[STUDY_ONLY] 策略基类框架设计
class BaseStrategy(ABC):
    """
    策略基类

    这是框架设计，用于说明策略应有的结构。
    回测阶段需要：
    1. 实现数据接入
    2. 添加日志记录
    3. 加入异常处理
    """
    pass  # [PLACEHOLDER] 待回测阶段完善
```

### 3.3 可执行代码标记

```python
[EXECUTABLE] 数据获取函数 - 已验证
def fetch_ohlcv_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取股票OHLCV数据

    Returns:
        DataFrame with columns: [date, open, high, low, close, volume]
    """
    # 具体实现...
    return df
```

---

## 4. 各目录代码状态

| 目录 | 当前状态 | 说明 |
|------|----------|------|
| `04_TECHNICAL_SPECS/` | 框架代码为主 | 系统架构说明，需要回测验证 |
| `03_TRADING_TACTICS/strategy-pool/` | 示例代码 | 策略逻辑示例，需要回测验证 |
| `03_TRADING_TACTICS/tactics/` | 示例代码 | 战术示例，需要回测验证 |
| `02_FACTOR_LIBRARY/01_METHODOLOGY/` | 参考代码 | 方法论参考代码，可执行 |

---

## 5. 执行阶段说明

### 5.1 当前阶段：研究/策略设计

```
目标：验证策略想法，建立方法论
代码状态：STUDY_ONLY + PLACEHOLDER
不需要：EXECUTABLE代码
```

### 5.2 下一步：回测验证

```
目标：用历史数据验证策略
代码状态：EXECUTABLE
需要：
1. 接入数据源
2. 编写回测框架
3. 验证策略逻辑
```

---

## 6. 代码状态检查清单

在将代码标记为`[EXECUTABLE]`之前，必须确认：

- [ ] 代码已接入测试数据
- [ ] 代码可正常运行
- [ ] 单元测试通过
- [ ] 错误处理完善
- [ ] 日志记录完整
- [ ] 遵循CODE_QUALITY.md中的所有规范

---

## 附录: 相关文档

| 文档 | 说明 |
|------|------|
| `05_IMPLEMENTATION/CODE_QUALITY.md` | 代码质量标准 |
| `05_IMPLEMENTATION/ERROR_HANDLING.md` | 错误处理规范 |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |
| v2.0 | 2026-03-28 | 标记格式更新为更清晰的[PLACEHOLDER]/[STUDY_ONLY]/[EXECUTABLE] |
