---
module_id: GOV-ENG-001
title: "代码构建标准"
doc_type: standard
status: active
version: "1.4.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: human_gated
created_by: human_plus_agent
date: "2026-05-11"
valid_from: "2026-05-04"
ttl: periodic_review_90d
summary: "ZephyrAlpha 全模块统一的代码构建标准。定义命名约定、文件组织、类型注解强制层级、导入规范及 SSoT 守卫规则。v1.4.0：§7 简化为引用 GOV-ENG-002（文件头部标准独立文件）。"
tags: [standard, engineering, code-quality, naming, typing, imports, anti-hallucination]
depends_on:
  - {target: GOV-ARCH-001, at: "$", why: "治理架构蓝图——定义本标准的架构上下文"}
  - {target: MOD-INF-005, at: "§7", why: "governance-automation 脚本质量标准——脚本质量规则的先例"}
  - {target: MOD-INF-001, at: "$", why: "capacity-assurance 定义 pre-commit 工具链标准"}
---

# 代码构建标准

> 适用层级：全 14 层（L00-L15），按 §3 分层定级。写 Python 代码前 MUST 加载本标准。
> module_id: GOV-ENG-001 | version: 1.4.0 | status: active

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

### 2.4 一个文件一个类

每个文件一个主类 + 辅助函数。超过 300 行 → 拆分辅助函数/子类到独立文件。

### 2.5 文档拆分规则

**核心原则：能不拆就不拆。** 拆 = 多一个文件 = 多一条路径 = 漂移风险 +1。

#### 阈值

| 指标 | 警告阈值 | 强制拆分阈值 | 说明 |
|------|:---:|:---:|------|
| 单文件 tokens | 40K | 60K | 128K 窗口下，60K 文档 + 蓝图 + 代码 ≈ 100K，接近极限 |
| 单文件行数 | 800 | 1200 | MD 文档行数（非代码） |

**警告阈值**：开始评估是否需要拆。评估后决定不拆 = 合理。
**强制拆分阈值**：必须拆。不拆 = AI 无法完整加载。

#### 拆分策略优先级

| 优先级 | 策略 | 适用场景 | 示例 |
|:---:|------|---------|------|
| 1 | **按功能域** | 域驱动设计，各域内聚 | D-DATA / D-RISK / D-EXECUTION |
| 2 | 按架构层 | 层级清晰的系统 | L01 基础设施 / L02 Alpha / L03 信号 |
| 3 | 按依赖深度 | 扁平依赖结构 | 核心链路 / 扩展链路 / 外围 |
| 4 | 自定义 | 混合策略 | 需在拆分索引中说明理由 |

#### 拆分后必须满足

| 要求 | 说明 |
|------|------|
| 总览索引文件 | 00-总览与索引.md，列出所有子文件 + 一句话摘要 + 链接 |
| 子文件互相引用 | 子文件头部声明 parent_file + sibling_files |
| 路径映射合规 | 拆分后的文件路径必须符合依赖图 §19 path_mappings |
| 交叉引用无断裂 | 拆分前能跳转的链接，拆分后仍然有效 |
| token 估算 | 每个子文件声明 token_estimate（选填，默认 0），供 AutoRuntime 调度 |

#### 拆分索引模板

```markdown
# {文档名称} — 总览与索引

> 状态 | 版本 | 日期

## 文件清单

| # | 文件 | 一句话 | tokens | 状态 |
|---|------|--------|:---:|------|
| 0 | 本文件（总览） | 全局入口 | ~3K | active |
| 1 | 01-{域ID}-{域名}.md | {一句话} | ~20K | active |
| 2 | 02-{域ID}-{域名}.md | {一句话} | ~15K | active |

## 拆分策略

- 策略: by_domain
- 触发原因: 单文件 > 60K tokens
- 拆分依据: 按功能域自然拆分，每个域内聚
```

#### 子文件头部模板

```markdown
# {域名称}

> parent_file: 00-总览与索引.md | sibling_count: {N}
```

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
2. 运行生成脚本重新生成 Python 代码 + 递增 `schema_version`
3. 审计所有下游模块的适配需求
4. Breaking change → 一篇 ADR（存入 `KB:decisions`）

**禁止跳过第 1 步直接修改 Python 文件。**

---

## §6 加载时机

AI session 在准备"写 Python 代码"时，按以下路径加载本标准：

```
1. AGENTS.md → 读到 §6.15 的引用 → 定位到本文件
2. 加载本文件全部章节
3. 根据当前任务所在层级（L00-L15），确定适用的类型注解强制级别（§3）
4. 代码写完后，pre-commit 阶段的 ruff + mypy 自动执行对应层级的检查
```

---

## §7 文件头部标准（防幻觉/防漂移）

> 完整规范见 [GOV-ENG-002 file-header-standard.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/file-header-standard.md)。本节仅保留快速参考。

### 7.1 表头格式映射

| header_format | 适用 file_category | 字段数 | 详见 |
|---|---|:---:|---|
| A_full | code, script | 10 | GOV-ENG-002 §3 |
| A_test | test | 6 | GOV-ENG-002 §4 |
| B_yaml | gate, registry, contract(yaml), config, data | 5 | GOV-ENG-002 §5 |
| C_json | contract(json), schema(json) | 5 | GOV-ENG-002 §6 |
| D_md | doc | — | GOV-ENG-002 §7 |
| E_shell | infra | 4 | GOV-ENG-002 §8 |

### 7.2 A_full 十字段速查

```python
# [BLUEPRINT] {module_id} | {blueprint_path} | §{N}
# [MODULE] {full.module.path}
# [INVARIANTS] {不可违反的约束，分号分隔}
# [MODIFY-GUARD] {修改此文件必须同步更新的文件，分号分隔}
# [CONSUMERS] {依赖此文件的模块，分号分隔}
# [STABILITY] {frozen|stable|evolving|volatile}
# [SAFETY] {H|M|L}
# [AI_AUTONOMY] {immutable_core|human_gated|ai_modifiable}
# [ERROR_CONTRACT] {可抛异常列表，分号分隔}
# [TESTS] {测试文件路径，分号分隔}
```

### 7.3 枚举值速查

| 字段 | 枚举值 | SSoT |
|---|--------|------|
| [STABILITY] | frozen / stable / evolving / volatile | PS-REG-012 |
| [SAFETY] | H / M / L | PS-REG-012 |
| [AI_AUTONOMY] | immutable_core / human_gated / ai_modifiable | PS-REG-012 |

### 7.4 关系声明

修改 GOV-ENG-002 的枚举值或格式 → MUST 同步更新本节速查表 + PS-REG-012 对应字段。

---

## §8 防幻觉代码级规则（#7-#18）

> 对标：AWS Bedrock Guardrails / Galileo AI 8-step Framework / Cursor 社区最佳实践。
> L0 定义了十八条铁律，§7 覆盖 #1-#6（结构追溯）。本节覆盖 #7-#18 的代码级实施标准。

### 8.1 禁止占位符（#7）

| 禁止项 | 正确做法 |
|--------|---------|
| `# TODO: ...` / `# FIXME: ...` / `# HACK: ...` | 现在就实现 |
| `def func(): ...`（Ellipsis 函数体） | 写完整实现 |
| `def func(): pass`（空函数体） | 写完整实现 |
| `raise NotImplementedError` | 写完整实现，或拆分为更小任务 |
| `# implement later` / `# will add` | 现在就实现 |

**豁免**: `@abstractmethod` + `raise NotImplementedError` 是合法接口声明。

### 8.2 编辑优先（#8）

```python
# ❌ 禁止：删除文件后重建
# 删除 old_module.py → 创建 new_module.py（丢失 git history + 注册失效）

# ✅ 正确：surgical edit
# SearchReplace 只替换变更的行
```

**判定**: `git diff` 出现整文件删除+新增 → 违反。正常 diff 应只有少量行变更。

### 8.3 最小变更（#9）

| 允许 | 禁止 |
|------|------|
| 修复指定 bug 的最小改动 | "顺便"重命名变量 |
| 添加指定功能的最小代码 | "顺手"优化相邻函数 |
| 按需求修改的精确行 | "顺便"调整代码风格 |

**判定**: diff 中任何与需求无关的变更 → 违反。

### 8.4 假设显式化（#10）

```python
# ❌ 禁止：静默假设
def process(data):
    result = api.call(data)  # 假设 api.call 返回 dict

# ✅ 正确：显式标记
def process(data):
    # [ASSUMPTION] api.call() returns dict with 'status' key
    result = api.call(data)
```

**路径和签名假设 = 禁止**。必须 Grep/Read 验证后才能使用。

### 8.5 导入验证（#12）

```python
# ❌ 禁止：直接使用未验证的导入
from zephyr.magic_module import process_all

# ✅ 正确：先验证再使用
# 1. Grep "class process_all" 或 Read zephyr/magic_module.py
# 2. 确认存在后才 import
from zephyr.magic_module import process_all
```

### 8.6 自审闭环（#13）

产出代码后 MUST 逐项检查：

| 检查项 | 判定标准 |
|--------|---------|
| 功能完整 | 需求的每个点都有对应实现 |
| 边界处理 | 空输入 / 零值 / None / 超长输入有处理 |
| 错误路径 | try/except 覆盖所有可能失败点 |
| 类型一致 | 函数签名类型与实际使用一致 |
| 导入完整 | 所有使用的类型/函数都已导入 |

### 8.7 新代码必测（#14）

| 场景 | 要求 |
|------|------|
| 新建模块 | MUST 创建 `test_{module}.py` |
| 修改函数 | MUST 更新或添加对应测试用例 |
| 修改 Bug | MUST 添加回归测试 |
| 豁免 | `__init__.py` / 纯配置 YAML |

### 8.8 安全最低通过（#15）

| 检查 | 内容 | 不通过 → 处置 |
|------|------|-------------|
| 认证检查 | 敏感操作是否有权限控制 | 缺失 → 必须添加 |
| 注入检查 | SQL/命令/路径是否有参数化 | 拼接 → 必须参数化 |
| 数据暴露 | 日志/错误信息是否泄露敏感数据 | 泄露 → 必须脱敏 |

### 8.9 计划先行（#16）

触发条件（任一满足）：修改 >3 文件 / 新增 >50 行 / 接口变更 >2 模块 / Schema 变更。

流程：输出计划 → 确认 → 执行 → 验证。

### 8.10 跨文件影响检查（#17）

修改文件前：读取 `[CONSUMERS]` → Grep 所有引用 → 评估影响 → 同步修改。

### 8.11 上下文新鲜度（#18）

对话 >30 轮 / AI 输出矛盾 / AI 重复输出 / AI 忘记决策 → 开新会话。

---
