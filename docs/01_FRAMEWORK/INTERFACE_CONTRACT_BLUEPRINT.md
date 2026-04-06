---
module_id: INTERFACE_CONTRACT_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 专业量化机构蓝图
applicable_scope: 三级时间框架架构
compliance_level: 专业标准
parent_document: PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
layer: Layer 2 (Alpha因子层)
responsibility_boundary: |
  本文档负责三级时间框架接口契约设计，包括：
  - 模块间接口定义
  - 数据传输协议
  - 接口版本管理
  
  三级时间框架架构请参考：PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
---

# 三级时间框架接口契约蓝图

> **版本**: v1.0
> **创建日期**: 2026-04-02
> **目的**: 明确三级时间框架架构的模块间接口契约
> **核心价值**: 确保模块间通信的规范性、可靠性和可维护性

---

## 📋 一、接口契约总览

### 1.1 接口契约设计原则

| 设计原则 | 具体要求 | 验证方法 |
|---------|---------|---------|
| **接口先行** | 先定义接口再实现 | 接口定义评审 |
| **版本管理** | 所有接口都有版本号 | 版本兼容性检查 |
| **向后兼容** | 新版本不破坏旧版本 | 兼容性测试 |
| **错误处理** | 所有接口都有错误处理 | 错误场景测试 |
| **文档完整** | 所有接口都有完整文档 | 文档完整性检查 |

### 1.2 接口分类

| 接口类型 | 接口数量 | 主要用途 | 协议类型 |
|---------|---------|---------|---------|
| **层内接口** | 15+ | 同一层模块间通信 | 函数调用/消息队列 |
| **跨层接口** | 8+ | 跨层数据传递 | API/消息队列 |
| **外部接口** | 5+ | 与外部系统交互 | REST API/数据库 |

---

## 🎯 二、接口契约详细定义

### 2.1 宏观经济判断引擎接口

#### 2.1.1 接口定义

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

@dataclass
class MacroDataInput:
    """宏观经济数据输入"""
    gdp_growth: float                    # GDP增长率
    cpi: float                           # CPI
    ppi: float                           # PPI
    pmi: float                           # PMI
    m2_growth: float                     # M2增长率
    interest_rate: float                 # 利率
    credit_spread: float                 # 信用利差
    timestamp: datetime                  # 时间戳

@dataclass
class RegimeOutput:
    """经济范式输出"""
    dominant_regime: str                 # 主导航式 (expansion/stagflation/recession/recovery)
    probabilities: Dict[str, float]      # 各范式概率
    confidence: float                    # 置信度
    transition_probability: Dict[str, float]  # 范式转换概率
    recommended_assets: List[str]        # 推荐资产
    timestamp: datetime                  # 时间戳

class IEconomicRegimeEngine(ABC):
    """经济范式判断引擎接口"""
    
    @abstractmethod
    def analyze_regime(self, macro_data: MacroDataInput) -> RegimeOutput:
        """分析经济范式
        
        Args:
            macro_data: 宏观经济数据输入
            
        Returns:
            RegimeOutput: 经济范式输出
            
        Raises:
            DataValidationError: 数据验证失败
            ModelInferenceError: 模型推理失败
        """
        pass
    
    @abstractmethod
    def predict_transition(self, current_regime: str, 
                          horizon_days: int = 90) -> Dict[str, float]:
        """预测范式转换
        
        Args:
            current_regime: 当前范式
            horizon_days: 预测时间范围(天)
            
        Returns:
            Dict[str, float]: 各范式转换概率
        """
        pass
```

---

## 🔧 三、版本管理

### 3.1 版本号规则

- 主版本号：重大架构变更
- 次版本号：新增功能
- 修订号：bug修复

### 3.2 向后兼容策略

- 新增接口必须保持向后兼容
- 废弃接口必须提供过渡期
- 接口变更必须记录在变更日志中

---

## ⚠️ 四、错误处理

### 4.1 错误码定义

| 错误码 | 错误类型 | 处理策略 |
|-------|---------|---------|
| 1001 | 数据验证错误 | 返回错误信息，要求重新输入 |
| 1002 | 模型推理错误 | 返回备用结果，记录错误日志 |
| 1003 | 超时错误 | 重试机制，返回缓存结果 |
| 1004 | 权限错误 | 返回权限不足提示 |

### 4.2 错误响应格式

```json
{
    "error_code": "1001",
    "error_message": "数据验证失败",
    "details": {
        "field": "gdp_growth",
        "expected": "float",
        "actual": "string"
    },
    "timestamp": "2026-04-02T10:00:00Z"
}
```

---

## 📚 五、文档规范

### 5.1 接口文档要求

- 每个接口必须有使用示例
- 每个参数必须说明类型和取值范围
- 每个接口必须说明可能的错误情况
- 必须包含版本历史记录

---

**版本**: v1.0 | **更新**: 2026-04-06 | **状态**: 🔄 编码修复
