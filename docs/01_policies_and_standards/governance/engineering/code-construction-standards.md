---
module_id: GOV-ENG-001
title: "代码构建标准"
doc_type: standard
status: active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: human_gated
created_by: human_plus_agent
date: "2026-05-04"
valid_from: "2026-05-04"
ttl: periodic_review_90d
summary: "ZephyrAlpha 全模块统一的代码构建标准。定义命名约定、文件组织、类型注解强制层级、导入规范及 SSoT 守卫规则。供 AI 编码时按需加载。"
tags: [standard, engineering, code-quality, naming, typing, imports]
depends_on:
  - {target: GOV-ARCH-001, at: "$", why: "治理架构蓝图——定义本标准的架构上下文"}
  - {target: MOD-INF-005, at: "§7", why: "script-system 脚本质量标准——脚本质量规则的先例"}
  - {target: MOD-INF-001, at: "$", why: "capacity-assurance 定义 pre-commit 工具链标准"}
---

# 代码构建标准

> **目的**：定义 ZephyrAlpha 所有 Python 模块必须遵守的代码构建规范。AI 在写代码前应加载本标准。
> **适用层级**：全 14 层（L00-L15），分层级有不同的类型注解强制要求。
> **module_id**: GOV-ENG-001 | **version**: 1.0.0 | **status**: active

---

## §1 命名约定

### 1.1 文件命名

| 类型 | 约定 | 示例 |
|------|------|------|
| 模块文件 | `snake_case.py` | `batch_ingest.py`, `market_data.py` |
| 测试文件 | `test_{module}.py` | `test_batch_ingest.py`, `test_market_data.py` |
| 配置文件 | `snake_case.yaml` | `cross_layer_contracts.yaml` |
| 蓝图文件 | `blueprint.md`（固定名） | `blueprint.md` |
| 索引文件 | `index.md`（固定名） | `index.md` |
| `__init__.py` | 最小原则——仅导出公开 API | `__init__.py` |

### 1.2 标识符命名

| 类型 | 约定 | 示例 |
|------|------|------|
| 类名 | `PascalCase` | `MarketDataPipeline`, `RiskLimits` |
| 函数名 | `snake_case` | `process_tick()`, `calculate_exposure()` |
| 变量名 | `snake_case` | `raw_tick`, `adjusted_price` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_POSITION_SIZE`, `DEFAULT_MIN_INTERVAL_US` |
| 私有成员 | `_leading_underscore` | `_validate_input()`, `_cache` |
| 模块级私有 | `__double_underscore`（仅当必要） | `__internal_state` |
| 布尔变量 | `is_` / `has_` / `can_` 前缀 | `is_valid`, `has_position`, `can_execute` |

### 1.3 禁止的命名

- 禁止单字母变量名（`x`、`i` 除外——仅限推导式/循环索引）
- 禁止拼音命名
- 禁止在变量名中嵌入类型（`str_name`、`list_items`）——类型注解已承担此职责
- 禁止 `data`、`info`、`result` 等无意义命名

---

## §2 文件组织

### 2.1 文件大小约束

| 约束 | 值 |
|------|----|
| 单文件最大行数 | 300 行 |
| 单函数最大行数 | 50 行 |
| 单类最大行数 | 200 行 |
| 超限处理 | 拆分为同目录下的多个模块文件 |

### 2.2 `__init__.py` 最小原则

```python
# ✅ 正确：仅导出公开 API
from zephyr.alpha.market_data_pipeline import MarketDataPipeline
from zephyr.alpha.market_data_pipeline import TickNormalizer

__all__ = ["MarketDataPipeline", "TickNormalizer"]

# ❌ 错误：在 __init__.py 中写业务逻辑
# ❌ 错误：from .module import * （破坏静态分析）
```

### 2.3 目录组织

```
src/zephyr/{layer}/
├── __init__.py          # 仅导出公开 API
├── models.py            # Pydantic/dataclass 数据模型
├── {feature}.py         # 按功能拆分的模块文件
├── {feature}_test.py    # 测试文件（与源码同目录）...或放在 tests/ 下
└── sub_module/          # 复杂功能拆分子目录
    ├── __init__.py
    ├── core.py
    └── adapters.py
```

### 2.4 一个文件一个类原则

当文件只有一个主类 + 少量辅助函数（< 300 行），符合原则。超过 300 行时，将辅助函数或子类拆分到独立文件。

---

## §3 类型注解强制层级

### 3.1 分层要求

| 层级 | mypy 模式 | 要求 |
|------|:---:|------|
| L00-L01（数据源/基础设施） | `strict` | 100% 覆盖，`disallow_untyped_defs=true` |
| L02-L08（因子→界面） | 关键接口 `strict` | 跨模块接口 100%，内部实现 80%+ |
| L09-L15（上层业务） | public API `strict` | public 函数/方法 100%，private 不强制 |

### 3.2 强制类型注解的位置

- 所有函数签名（参数 + 返回值）
- 所有类属性
- 所有跨模块数据结构
- 所有 public API

### 3.3 禁止的写法

```python
# ❌ 禁止
def process(data):               # 缺类型注解
    ...

# ❌ 禁止
def process(data: dict):         # 泛型字典——字段完全不可知
    ...

# ❌ 禁止
def process(data: Any):          # Any 绕过类型检查
    ...

# ✅ 正确
def process(tick: NormalizedMarketData) -> FactorSignal:
    ...

# ✅ 正确（真正不确定类型时，用显式 Any 而非裸写）
from typing import Any
def deserialize(raw: bytes) -> Any:  # 至少表态"我知道这里是动态类型"
    ...
```

### 3.4 `Decimal` / `Timestamp` / `Money` 强制

- 金额、价格、数量 → `Decimal`（禁止 `float`）
- 时间戳 → `Timestamp`（纳秒 UTC，禁止裸 `datetime`）
- 货币运算 → `Money` 类型

以上三条对齐 AGENTS.md §四 和 cross-layer-contracts.yaml CTR-000 契约。

---

## §4 导入规范

### 4.1 导入分组与排序

```python
# 1. 标准库
import asyncio
from pathlib import Path
from typing import Optional

# 2. 第三方库
import numpy as np
from pydantic import BaseModel

# 3. 项目内模块（绝对导入）
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.contracts.timestamp import Timestamp

# 4. 同层模块（相对导入，仅限同 package 内）
from .models import FactorSignal
from .utils import normalize_tick
```

### 4.2 禁止的导入

- `import *` — 破坏静态分析，永远禁止
- 下层导入上层 — 违反分层架构（L02 不可 `from zephyr.L03 import ...`）
- 循环导入 — 在 CI 阶段由 `import-linter` 检测
- 裸 `dict[str, Any]` 作为跨模块参数 — 使用冻结 dataclass/Pydantic 替代

---

## §5 SSoT 守卫

### 5.1 规则

YAML 是 SSoT，Python 代码是生成物/派生品。禁止跳过 YAML 直接修改 Python 数据结构定义。

```python
# ❌ 错误：在模块内部自造数据结构
class MyMarketData:
    symbol: str
    price: float  # 用 float 存价格是灾难
    ts: str       # 用 str 存时间是不规范的

# ✅ 正确：引用 CTR 契约类型
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.contracts.timestamp import Timestamp
from zephyr.shared.contracts.money import Money

def process(tick: NormalizedMarketData) -> FactorSignal:
    ...
```

### 5.2 修改数据结构的流程

1. 修改 SSoT YAML（`cross-layer-contracts.yaml`）
2. 运行生成脚本重新生成 Python 代码
3. 递增 `schema_version`
4. 审计所有下游模块的适配需求
5. Breaking change → 一篇 ADR

**禁止跳过第 1 步直接修改 Python 文件。**

---

## §6 AI 使用方式

AI session 在准备"写 Python 代码"时，按以下路径加载本标准：

1. AGENTS.md → 读到 §6.15 的引用 → 定位到本文件
2. 加载本文件全部章节
3. 根据当前任务所在层级（L00-L15），确定适用的类型注解强制级别（§3）
4. 代码写完后，pre-commit 阶段的 `ruff + mypy` 自动执行对应层级的检查

---

## §7 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-05-04 | 初始创建：从 AGENTS.md 和 shared-core 蓝图中提取分散的编码规范，整合为统一标准。覆盖命名约定（§1）、文件组织（§2）、类型注解层级（§3）、导入规范（§4）、SSoT守卫（§5） |
