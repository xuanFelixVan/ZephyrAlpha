---
module_id: AI_CONSTRUCTION_QUICK_REFERENCE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席架构�?standard_type: AI施工快速参�?applicable_scope: AI智能体施工必�?compliance_level: 强制执行
parent_document: ./CONSTRUCTION_SPECIFICATION.md
implementation_status: 强制执行
---

# AI施工快速参�?
> **🔴 强制阅读**: AI智能体在开始任何开发或文档构建任务前必须阅读本文档
> **完整�?*: [蓝图施工说明书](./CONSTRUCTION_SPECIFICATION.md)
> **版本**: v1.0 | **更新日期**: 2026-04-02

---

## �?**5秒快速检�?*

```
开始施工前，AI必须回答以下问题�?
�?1. 我要创建什么类型的文件�?     - 代码文件 �?src/
     - 文档文件 �?docs/
     - 配置文件 �?config/
     - 测试文件 �?tests/

�?2. 目标文件夹是否存在？
     - 使用 LS 命令检�?
�?3. 文件命名是否正确�?     - Python文件: 小写+下划�?(strategy_factory.py)
     - 文档文件: 大写+下划�?(STRATEGY_FACTORY_GUIDE.md)
     - 配置文件: 小写+下划�?(strategy_config.yaml)

�?4. 是否使用标准模板�?     - 文档: 包含必需元数�?     - 代码: 包含必需注释
```

---

## 📁 **核心文件夹结构（记住这个！）**

```
ZephyrAlpha/
├── docs/                    # 所有文�?�?  └── 05_IMPLEMENTATION/
�?      └── 06_CONSTRUCTION_DOCS/  # 施工文档专区
�?├── src/                     # 所有源代码
�?  ├── strategy/           # 策略模块（不是strategies/�?�?  ├── event_bus/          # 事件总线（不是event/或events/�?�?  ├── backtest/           # 回测引擎（不是backtesting/�?�?  ├── risk/               # 风险管理（不是risk_management/�?�?  └── execution/          # 执行引擎（不是execution_engine/�?�?├── tests/                   # 所有测�?├── config/                  # 所有配�?├── scripts/                 # 所有脚�?├── data/                    # 所有数�?└── logs/                    # 所有日�?```

---

## 🚫 **禁止创建的文件夹（记住这个！�?*

```
�?src/strategies/          �?应使�?src/strategy/
�?src/strategy_factory/    �?应使�?src/strategy/factory.py
�?src/event/               �?应使�?src/event_bus/
�?src/events/              �?应使�?src/event_bus/
�?src/backtesting/         �?应使�?src/backtest/
�?src/backtest_engine/     �?应使�?src/backtest/
�?src/risk_management/     �?应使�?src/risk/
�?src/execution_engine/    �?应使�?src/execution/
�?docs/documentation/      �?应使�?docs/
�?docs/docs/               �?应使�?docs/
```

---

## 📝 **命名规范速查�?*

| 文件类型 | 正确示例 | 错误示例 |
|---------|---------|---------|
| **Python文件** | `strategy_factory.py` | `StrategyFactory.py` |
| **文档文件** | `STRATEGY_FACTORY_GUIDE.md` | `strategy_factory_guide.md` |
| **配置文件** | `strategy_config.yaml` | `StrategyConfig.yaml` |
| **目录** | `src/strategy/` | `src/Strategy/` |
| **变量** | `strategy_factory` | `strategyFactory` |
| **函数** | `create_strategy()` | `createStrategy()` |
| **�?* | `StrategyFactory` | `strategy_factory` |
| **常量** | `MAX_POSITION` | `maxPosition` |

---

## 🔄 **标准施工流程**

```
Step 1: 检查现有结�?   �?LS d:\ZephyrAlpha\src\
   �?LS d:\ZephyrAlpha\docs\

Step 2: 确认目标位置
   �?查看本快速参考的文件夹结�?   �?确认正确路径

Step 3: 使用标准模板
   �?文档: 包含必需元数�?   �?代码: 包含必需注释

Step 4: 创建文件
   �?使用正确路径
   �?使用正确命名
   �?添加标准内容

Step 5: 验证
   �?LS 检查文件位�?   �?检查命名规�?   �?运行质量门禁
```

---

## 📄 **文档必需元数�?*

```markdown
---
module_id: [MODULE_ID]_001
version: 1.0.0
status: Active
created_date: YYYY-MM-DD
last_updated: YYYY-MM-DD
owner: [负责人]
standard_type: [文档类型]
applicable_scope: [适用范围]
compliance_level: [合规级别]
parent_document: [父文档路径]
implementation_status: [实施状态]
---
```

---

## 💻 **代码必需注释**

```python
"""
[模块名称] - [模块职责]

版本: v1.0
创建日期: YYYY-MM-DD
作�? [作者]
"""

def function_name(param1: str, param2: Optional[Dict] = None) -> Dict[str, Any]:
    """函数说明
    
    Args:
        param1: 参数1说明
        param2: 参数2说明（可选）
    
    Returns:
        返回值说�?    
    Raises:
        ValueError: 异常说明
    
    Example:
        >>> result = function_name("test")
        >>> print(result)
    """
    pass
```

---

## 🚨 **常见错误示例**

### **错误1: 文件夹命名错�?*

```bash
# �?错误
src/strategies/factory.py

# �?正确
src/strategy/factory.py
```

### **错误2: 文件命名错误**

```python
# �?错误
StrategyFactory.py

# �?正确
strategy_factory.py
```

### **错误3: 同一模块多个位置**

```bash
# �?错误
src/strategy/factory.py
src/strategies/factory.py
src/core/strategy_factory.py

# �?正确（只保留一个）
src/strategy/factory.py
```

---

## 📞 **遇到问题�?*

1. **查看完整�?*: [蓝图施工说明书](./CONSTRUCTION_SPECIFICATION.md)
2. **检查现有结�?*: 使用 LS 命令
3. **参考已有文�?*: 查看类似文件的结�?4. **询问用户**: 如果不确定，先询问用�?
---

## 🎯 **记住这句�?*

> **"在创建任何文件前，先用LS检查现有结构，确认正确路径和命名，使用标准模板，遵循施工规范�?**

---

**文档维护�?*: 首席架构�? 
**版本**: v1.0  
**最后更�?*: 2026-04-02
