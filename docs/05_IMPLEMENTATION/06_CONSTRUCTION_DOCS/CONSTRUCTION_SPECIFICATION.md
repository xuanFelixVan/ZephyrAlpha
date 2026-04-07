---
module_id: CONSTRUCTION_SPECIFICATION_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席架构?standard_type: 专业量化机构施工规范
responsibility:
  - 实施指南、部署文档
applicable_scope: 全系统开发和文档构建
compliance_level: 强制执行
parent_document: ../README.md
implementation_status: 强制执行
---
---


# 蓝图施工说明?
> **核心职责**: 蓝图设计和规划
> **职责边界**: 
> - ✅ 本文档负责：蓝图设计和规划相关内容
> - ❌ 本文档不负责：其他模块内容

> **版本**: v1.0
> **创建日期**: 2026-04-02
> **职责**: 规范AI和人工开发行为，确保文件夹结构、命名、文档和代码的一�?> **强制级别**: 🔴 **强制执行** - 所有开发和文档构建必须遵循本规?> **适用对象**: AI智能体、开发人员、文档编�?
---

## ⚠️ **重要提示**

### **AI施工必读**

**在开始任何开发或文档构建任务前，AI智能体必须：**

1. ?**完整阅读本说明书**
2. ?**检查现有文件夹结构**
3. ?**验证命名规范**
4. ?**使用标准模板**
5. ?**遵循施工流程**

**违反本规范的后果?*
- 🔴 文件将被移动到正确位?- 🔴 代码将被重写以符合规?- 🔴 文档将被重新生成
- 🔴 浪费时间和资?
---

## 📁 **文件夹结构规?*

### **1. 完整文件夹树状结?*

```
ZephyrAlpha/
├── docs/                           # 所有文??  ├── 00_OVERVIEW/               # 系统总览
?  ├── 01_FRAMEWORK/              # 框架定义
?  ├── 02_FACTOR_LIBRARY/         # 因子??  ├── 03_TRADING_TACTICS/        # 交易策略
?  ├── 04_EXECUTION/              # 执行引擎
?  ├── 05_IMPLEMENTATION/         # 实施指南
?  ?  ├── 01_QUICKSTART/         # 快速开??  ?  ├── 02_DEVELOPMENT/        # 开发规??  ?  ├── 03_DEPLOYMENT/         # 部署指南
?  ?  ├── 07_OPERATIONS/         # 运维手册
?  ?  ├── 05_TECHNICAL_SPECIFICATIONS/  # 技术规??  ?  └── 06_CONSTRUCTION_DOCS/  # 施工文档专区 🆕
?  ├── 06_ARCHIVE/                # 归档管理
?  ├── 07_RESEARCH/               # AI研究
?  └── 09_AUDIT/                  # 系统治理审计
?├── src/                           # 所有源代码
?  ├── strategy/                  # 策略模块
?  ?  ├── __init__.py
?  ?  ├── base.py               # BaseStrategy基类
?  ?  ├── factory.py            # StrategyFactory
?  ?  ├── registry.py           # StrategyRegistry
?  ?  ├── loader.py             # StrategyLoader
?  ?  └── scanner.py            # StrategyScanner
?  ??  ├── event_bus/                 # 事件总线模块
?  ?  ├── __init__.py
?  ?  ├── event_bus.py          # EventBus核心??  ?  ├── event.py              # Event基类
?  ?  ├── handler.py            # EventHandler基类
?  ?  ├── dispatcher.py         # 事件分发??  ?  └── exceptions.py         # 自定义异??  ??  ├── backtest/                  # 回测引擎模块
?  ?  ├── __init__.py
?  ?  ├── adapter.py            # BacktestingPyAdapter
?  ?  ├── strategy_wrapper.py   # 策略包装??  ?  ├── data_converter.py     # 数据转换??  ?  ├── result_formatter.py   # 结果格式化器
?  ?  └── exceptions.py         # 自定义异??  ??  ├── data/                      # 数据模块
?  ?  ├── __init__.py
?  ?  ├── loader.py             # 数据加载??  ?  ├── processor.py          # 数据处理??  ?  └── cache.py              # 数据缓存
?  ??  ├── risk/                      # 风险管理模块
?  ?  ├── __init__.py
?  ?  ├── manager.py            # 风险管理??  ?  ├── monitor.py            # 风险监控
?  ?  └── alerts.py             # 风险告警
?  ??  ├── execution/                 # 执行引擎模块
?  ?  ├── __init__.py
?  ?  ├── engine.py             # 执行引擎
?  ?  ├── order.py              # 订单管理
?  ?  └── position.py           # 持仓管理
?  ??  └── utils/                     # 工具模块
?      ├── __init__.py
?      ├── logger.py             # 日志工具
?      ├── config.py             # 配置工具
?      └── helpers.py            # 辅助函数
?├── tests/                         # 所有测试代??  ├── unit/                     # 单元测试
?  ├── integration/              # 集成测试
?  └── e2e/                      # 端到端测??├── config/                        # 所有配置文??  ├── system.yaml               # 系统配置
?  ├── strategy.yaml             # 策略配置
?  └── backtest.yaml             # 回测配置
?├── scripts/                       # 所有脚??  ├── deploy.sh                 # 部署脚本
?  ├── backup.sh                 # 备份脚本
?  └── monitoring.sh             # 监控脚本
?├── data/                          # 所有数据文??  ├── market_data/              # 市场数据
?  ├── backtest_results/         # 回测结果
?  └── cache/                    # 缓存数据
?├── notebooks/                     # Jupyter笔记??  └── research/                 # 研究笔记??└── logs/                          # 所有日志文?    ├── system/                   # 系统日志
    ├── strategy/                 # 策略日志
    └── backtest/                 # 回测日志
```

### **2. 文件夹职责说?*

| 文件?| 职责 | 允许内容 | 禁止内容 |
|--------|------|---------|---------|
| `docs/` | 所有文?| .md, .yaml, .json | .py, .ipynb |
| `src/` | 所有源代码 | .py, .pyx | .md, .yaml |
| `tests/` | 所有测试代?| .py, .json | .md |
| `config/` | 所有配置文?| .yaml, .yml, .json | .py, .md |
| `scripts/` | 所有脚?| .py, .sh, .bat | .md |
| `data/` | 所有数据文?| .csv, .parquet, .feather | .py, .md |
| `notebooks/` | Jupyter笔记?| .ipynb | .py |
| `logs/` | 所有日志文?| .log | .py, .md |

### **3. 禁止创建的文件夹**

🔴 **以下文件夹禁止创?*（已有标准命名）:

```
?src/strategies/          ?应使?src/strategy/
?src/strategy_factory/    ?应使?src/strategy/factory.py
?src/event/               ?应使?src/event_bus/
?src/events/              ?应使?src/event_bus/
?src/backtesting/         ?应使?src/backtest/
?src/backtest_engine/     ?应使?src/backtest/
?src/risk_management/     ?应使?src/risk/
?src/execution_engine/    ?应使?src/execution/
?docs/documentation/      ?应使?docs/
?docs/docs/               ?应使?docs/
```

---

## 📝 **命名规范**

### **1. 文件命名规范**

#### **Python文件命名**

```python
# ?正确
strategy_factory.py          # 小写+下划?event_bus.py                 # 小写+下划?backtest_adapter.py          # 小写+下划?
# ?错误
StrategyFactory.py           # 大驼?strategyFactory.py           # 小驼?strategy-factory.py          # 连字?Strategy_Factory.py          # 混合
```

#### **文档文件命名**

```markdown
# ?正确
STRATEGY_FACTORY_GUIDE.md    # 大写+下划?EVENT_BUS_GUIDE.md           # 大写+下划?README.md                    # 全大?
# ?错误
strategy_factory_guide.md    # 小写
StrategyFactoryGuide.md      # 大驼?strategy-factory-guide.md    # 连字?```

#### **配置文件命名**

```yaml
# ?正确
strategy_config.yaml         # 小写+下划?backtest_config.yaml         # 小写+下划?system_config.yaml           # 小写+下划?
# ?错误
StrategyConfig.yaml          # 大驼?strategy-config.yaml         # 连字?STRATEGY_CONFIG.yaml         # 全大?```

### **2. 目录命名规范**

```bash
# ?正确
src/strategy/                # 小写+下划?src/event_bus/               # 小写+下划?docs/05_IMPLEMENTATION/      # 编号+大写

# ?错误
src/Strategy/                # 大驼?src/strategyFactory/         # 小驼?src/strategy-factory/        # 连字?```

### **3. 变量命名规范**

```python
# ?正确
strategy_factory = StrategyFactory()    # 小写+下划?event_bus = EventBus()                  # 小写+下划?MAX_POSITION = 0.95                     # 常量全大?下划?
# ?错误
strategyFactory = StrategyFactory()     # 小驼?StrategyFactory = StrategyFactory()     # 大驼?maxPosition = 0.95                      # 小驼峰（应为常量?```

### **4. 函数命名规范**

```python
# ?正确
def create_strategy():                  # 小写+下划?def get_event_bus():                    # 小写+下划?def _private_method():                  # 私有方法前缀下划?
# ?错误
def createStrategy():                   # 小驼?def CreateStrategy():                   # 大驼?def create-strategy():                  # 连字?```

### **5. 类命名规?*

```python
# ?正确
class StrategyFactory:                  # 大驼?class EventBus:                         # 大驼?class BacktestAdapter:                  # 大驼?
# ?错误
class strategy_factory:                 # 小写+下划?class strategyFactory:                  # 小驼?class strategy_factory:                 # 小写+下划?```

---

## 📄 **文档模板**

### **1. 标准文档模板**

所有文档必须包含以下元数据?
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

# [文档标题]

> **版本**: v1.0
> **创建日期**: YYYY-MM-DD
> **职责**: [文档职责]
> **适用对象**: [适用对象]

---

## 📋 [第一章标题]

[内容]

---

## 📝 更新记录

| 日期 | 版本 | 更新内容 | 更新?|
|------|------|---------|--------|
| YYYY-MM-DD | v1.0 | 创建文档 | [更新人] |

---

## 📞 联系方式

**文档维护?*: [维护者]
**创建日期**: YYYY-MM-DD
**最后更?*: YYYY-MM-DD
**版本**: v1.0
```

### **2. 必需字段清单**

| 字段 | 必需 | 格式 | 说明 |
|------|------|------|------|
| `module_id` | ?| 大写+下划?数字 | 模块唯一标识 |
| `version` | ?| x.y.z | 语义化版?|
| `status` | ?| Active/Inactive | 文档�?|
| `created_date` | ?| YYYY-MM-DD | 创建日期 |
| `last_updated` | ?| YYYY-MM-DD | 最后更新日?|
| `owner` | ?| 字符?| 文档负责?|
| `standard_type` | ?| 字符?| 文档类型 |
| `applicable_scope` | ?| 字符?| 适用范围 |
| `compliance_level` | ?| 字符?| 合规级别 |
| `parent_document` | ?| 相对路径 | 父文档路?|
| `implementation_status` | ?| 字符?| 实施�?|

---

## 💻 **代码模板**

### **1. Python模块模板**

```python
"""
[模块名称] - [模块职责]

版本: v1.0
创建日期: YYYY-MM-DD
�? [作者]
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class [ClassName]:
    """[类名] - [类职责]
    
    Attributes:
        attr1: �?说明
        attr2: �?说明
    
    Example:
        >>> obj = ClassName()
        >>> obj.method()
    """
    
    def __init__(self, param1: str, param2: Optional[Dict[str, Any]] = None):
        """初始化[类名]
        
        Args:
            param1: 参数1说明
            param2: 参数2说明（可选）
        """
        self.param1 = param1
        self.param2 = param2 or {}
    
    def method_name(self, arg1: str) -> Dict[str, Any]:
        """方法说明
        
        Args:
            arg1: 参数说明
        
        Returns:
            返回值说?        
        Raises:
            ValueError: 异常说明
        """
        pass


if __name__ == "__main__":
    # 示例代码
    pass
```

### **2. 必需注释规范**

```python
# ?正确
def calculate_position_size(
    self,
    capital: float,
    risk_pct: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """计算仓位大小
    
    使用风险管理公式计算合适的仓位大小?    position_size = (capital * risk_pct) / (entry_price - stop_loss)
    
    Args:
        capital: 总资?        risk_pct: 风险比例?-1?        entry_price: 入场价格
        stop_loss: 止损价格
    
    Returns:
        仓位大小（股数）
    
    Raises:
        ValueError: 如果risk_pct不在0-1范围?    
    Example:
        >>> position_size = calculate_position_size(100000, 0.02, 100, 95)
        >>> print(position_size)
        400.0
    """
    if not 0 <= risk_pct <= 1:
        raise ValueError("risk_pct must be between 0 and 1")
    
    risk_amount = capital * risk_pct
    price_diff = entry_price - stop_loss
    
    if price_diff <= 0:
        raise ValueError("entry_price must be greater than stop_loss")
    
    position_size = risk_amount / price_diff
    return position_size


# ?错误（缺少注释）
def calc_pos(c, r, e, s):
    return (c * r) / (e - s)
```

### **3. 导入规范**

```python
# ?正确 - 标准库优?import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

# 第三方库
import pandas as pd
import numpy as np

# 本地模块
from strategy.base import BaseStrategy
from event_bus.event import Event


# ?错误 - 导入顺序混乱
from strategy.base import BaseStrategy
import pandas as pd
import os
from typing import Dict
import numpy as np
```

---

## 🔄 **施工流程**

### **1. 施工前检查清?*

**AI智能体在开始施工前必须完成以下检?*:

```
?1. 阅读本施工说明书
?2. 检查现有文件夹结构（使用LS命令??3. 验证目标文件夹是否存??4. 检查命名规??5. 确认使用的模??6. 检查依赖关?```

### **2. 施工步骤**

#### **Step 1: 检查现有结?*

```bash
# 使用LS命令检查现有文件夹
LS d:\ZephyrAlpha\src\
LS d:\ZephyrAlpha\docs\
```

#### **Step 2: 确认目标位置**

```
目标: 创建策略工厂模块
正确位置: src/strategy/factory.py
错误位置: src/strategies/factory.py
          src/strategy_factory/factory.py
          src/core/strategy_factory.py
```

#### **Step 3: 使用标准模板**

```
1. 复制标准模板
2. 填写必需字段
3. 遵循命名规范
4. 添加必需注释
```

#### **Step 4: 创建文件**

```
1. 创建文件到正确位?2. 使用正确命名
3. 添加标准元数?4. 编写内容
```

#### **Step 5: 验证**

```
1. 检查文件位?2. 检查命名规?3. 检查内容完�?4. 运行质量门禁检?```

### **3. 施工后验?*

```bash
# 验证文件位置
LS d:\ZephyrAlpha\src\strategy\

# 验证文件命名
# 应该看到: factory.py, registry.py, loader.py

# 验证文档
LS d:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\
```

---

## 🚨 **质量门禁**

### **1. 自动化检查项**

| 检查项 | 标准 | 自动?| 错误级别 |
|--------|------|--------|---------|
| 文件位置 | 符合文件夹结构规?| ?| 🔴 阻断 |
| 文件命名 | 符合命名规范 | ?| 🔴 阻断 |
| 文档元数?| 必需字段完整 | ?| 🔴 阻断 |
| 代码注释 | 关键函数有注?| ?| 🟡 警告 |
| 导入顺序 | 标准库→第三方→本地 | ?| 🟡 警告 |

### **2. 人工检查项**

| 检查项 | 标准 | 负责?|
|--------|------|--------|
| 架构一�?| 符合Layer 0-11架构 | 架构?|
| 职责清晰 | 模块职责不重?| 架构?|
| 代码质量 | 符合编码规范 | 代码审查?|
| 文档质量 | 内容完整准确 | 文档审查?|

### **3. 验收标准**

```
?通过标准:
   - 所有阻断项通过
   - 警告??3?   - 人工审查通过

?驳回标准:
   - 存在阻断?   - 警告?> 5?   - 人工审查不通过
```

---

## 🚫 **禁止事项清单**

### **1. 禁止创建的文件夹**

```
?src/strategies/          ?已有 src/strategy/
?src/strategy_factory/    ?已有 src/strategy/factory.py
?src/event/               ?已有 src/event_bus/
?src/events/              ?已有 src/event_bus/
?src/backtesting/         ?已有 src/backtest/
?src/backtest_engine/     ?已有 src/backtest/
?src/risk_management/     ?已有 src/risk/
?src/execution_engine/    ?已有 src/execution/
?docs/documentation/      ?已有 docs/
?docs/docs/               ?已有 docs/
```

### **2. 禁止使用的命?*

```
?文件命名:
   - StrategyFactory.py     ?应使?strategy_factory.py
   - strategyFactory.py     ?应使?strategy_factory.py
   - strategy-factory.py    ?应使?strategy_factory.py

?变量命名:
   - strategyFactory        ?应使?strategy_factory
   - StrategyFactory        ?应使?strategy_factory（变量）
   - maxPosition            ?应使?max_position

?函数命名:
   - createStrategy         ?应使?create_strategy
   - CreateStrategy         ?应使?create_strategy
   - create-strategy        ?应使?create_strategy
```

### **3. 禁止的操?*

```
?在根目录创建代码文件
?在src/目录创建文档文件
?在docs/目录创建代码文件
?创建重复的文件夹
?使用中文文件??使用空格文件??使用特殊字符文件?```

---

## 🔧 **常见问题处理**

### **问题1: 文件夹已存在但命名错?*

```bash
# 错误情况
src/strategies/factory.py

# 处理方法
1. 移动文件到正确位?   Move src/strategies/factory.py src/strategy/factory.py

2. 删除错误文件?   Remove-Item src/strategies/ -Recurse

3. 验证
   LS src/strategy/
```

### **问题2: 文件命名不符合规?*

```bash
# 错误情况
src/strategy/StrategyFactory.py

# 处理方法
1. 重命名文?   Rename-Item src/strategy/StrategyFactory.py factory.py

2. 验证
   LS src/strategy/
```

### **问题3: 同一模块有多个位?*

```bash
# 错误情况
src/strategy/factory.py
src/strategies/factory.py
src/core/strategy_factory.py

# 处理方法
1. 确认正确位置: src/strategy/factory.py
2. 合并代码（如有差异）
3. 删除错误位置文件
4. 验证
```

### **问题4: 文档元数据缺?*

```markdown
# 错误情况
# 策略工厂实施指南

## 概述
...

# 处理方法
1. 添加标准元数?---
module_id: IMPL_CONSTRUCTION_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席架构?standard_type: 专业量化机构实施指南
applicable_scope: 策略工厂模块实施
compliance_level: 专业标准
parent_document: ../README.md
implementation_status: 进行?---

# 策略工厂实施指南
...
```

---

## 📚 **参考资?*

### **内部文档**

- [施工文档总索引](./README.md)
- [专业量化系统实施蓝图](./01_BLUEPRINTS/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md)
- [文档质量门禁](./06_CHECKLISTS/DOCUMENT_QUALITY_GATE.md)

### **外部资源**

- [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Clean Code in Python](https://github.com/zedr/clean-code-python)

---

## 📝 **更新记录**

| 日期 | 版本 | 更新内容 | 更新?|
|------|------|---------|--------|
| 2026-04-02 | v1.0 | 创建蓝图施工说明?| 首席架构?|

---

## 📞 **联系方式**

**文档维护?*: 首席架构? 
**创建日期**: 2026-04-02  
**最后更?*: 2026-04-02  
**版本**: v1.0

---

## 🎯 **AI智能体必读声?*

**本说明书是强制执行的施工规范，所有AI智能体在开始任何开发或文档构建任务前必须完整阅读并遵循本规范。违反本规范将导致文件被移动、代码被重写、文档被重新生成，浪费时间和资源?*

**请将本说明书的路径添加到AI智能体的上下文中，确保每次施工都能参考本规范?*
