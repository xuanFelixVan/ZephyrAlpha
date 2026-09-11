---
module_id: MOD-SELL-015
title: "止损猎杀防护器蓝图 — 止损位偏移+软止损OBSERVING观察期"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
design_maturity: production
layer: L03_sell_decision
layer_name: sell_decision
functional_domain: sell_decision
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
---

# MOD-SELL-015 | Stop-Hunting Protector 止损猎杀防护器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P1 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: stable | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-015 (node 7878036)

## 1. 模块定位

止损猎杀防护器——防护做市商/HFT 主动猎杀止损位: ① 止损位偏移(不精确设在技术位, 偏移1-2%) ② 软止损模式(触及→OBSERVING观察期→确认跌破→CONFIRMED执行/收回→CLEARED解除)。产出 AdjustedStopLevel。

依据: `D:\临时工作区\依赖图\31-D-SELL-DECISION-卖出决策域.md` §1.2 SELL-15

## 2. 不变量 (INVARIANTS)

- **止损位偏移**: BELOW→original×(1-pct), ABOVE→original×(1+pct)
- **软止损状态机**: NORMAL→OBSERVING→CONFIRMED/CLEARED
- **OBSERVING触发**: 价格 ≤ 止损位(含等于, 保守)
- **CONFIRMED触发**: 观察期内收盘价 < 止损位
- **CLEARED触发**: 观察期内价格回升 > 止损位
- **CONFIRMED是终态**: 由调用方重置(不自动回退)
- **confidence**: NORMAL/CLEARED=0.0, OBSERVING=0.5, CONFIRMED=1.0
- **无状态设计**: 软止损状态作为输入参数, 检测器不持久化

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidStopHuntInputError | ZA-SELL-0015 | symbol空 / 止损位≤0 / 价格≤0 / 偏移比例越界 / 默认偏移>10% |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.shared.foundation.errors | ZephyrBaseError | 错误基类 |
| 依赖 | MOD-SELL-001 SellSignalCollector | SellDirection | 复用卖出方向枚举 |
| 消费 | MOD-SELL-005 止损策略族 | 原始止损位 | SELL-05 计算的止损位(输入) |
| 产出 | MOD-SELL-005 止损策略族 | AdjustedStopLevel | 偏移后止损位(SELL-05 消费) |
| 产出 | MOD-SELL-007 融合引擎 | AdjustedStopLevel | 软止损状态反馈 |

## 5. 防护逻辑

### ① 止损位偏移
```
BELOW: adjusted = original × (1 - offset_pct)   # 下移防向上猎杀
ABOVE: adjusted = original × (1 + offset_pct)   # 上移
默认 offset_pct = 0.02 (2%)
```

### ② 软止损状态机
```
NORMAL + price ≤ stop → OBSERVING
OBSERVING + close < stop → CONFIRMED (执行清仓)
OBSERVING + price > stop → CLEARED (解除)
CONFIRMED → CONFIRMED (终态, 调用方重置)
CLEARED + price ≤ stop → OBSERVING (重新触发)
```

### confidence 映射
| 状态 | confidence | direction | 说明 |
|------|:----------:|-----------|------|
| NORMAL | 0.0 | REPLACE(占位) | 正常持有 |
| OBSERVING | 0.5 | REDUCE | 观察期减仓 |
| CONFIRMED | 1.0 | CLEAR | 确认跌破清仓 |
| CLEARED | 0.0 | REPLACE(占位) | 解除 |

## 6. 接口

### 输入
```python
# 止损位偏移
protector.adjust_stop_level(symbol, original_stop, offset_pct=None, direction=BELOW) -> AdjustedStopLevel
# 软止损评估
protector.evaluate_soft_stop(symbol, stop_level, current_price, close_price, current_state=NORMAL) -> AdjustedStopLevel
```

### 输出数据模型
```python
@dataclass(frozen=True)
class AdjustedStopLevel:
    symbol: str
    original_stop: float
    adjusted_stop: float
    offset_pct: float           # [0,1]
    offset_direction: StopHuntOffsetDirection
    soft_stop_state: SoftStopState  # NORMAL/OBSERVING/CONFIRMED/CLEARED
    confirmed: bool             # CONFIRMED=True
    confidence: float           # [0,1]
    direction: SellDirection    # CLEAR/REDUCE/REPLACE
    reason: str
    metadata: dict              # prev_state/new_state
    timestamp: datetime
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| A类基础设施(纯防护逻辑) | 不涉及"止损位怎么算"(SELL-05职责), 只定义偏移+软止损契约 |
| 无状态设计(状态作输入参数) | 检测器可并发, 状态持久化由上层(持仓状态机)负责 |
| 偏移默认2% | 设计文档 §1.2 SELL-15 "偏移1-2%", 取上限防猎杀 |
| 软止损OBSERVING观察期 | 防做市商假跌破猎杀, 收盘价确认才执行 |
| CONFIRMED终态 | 确认跌破后不自动回退, 由调用方重置(避免反复触发) |
| 价格≤止损位触发(含等于) | 保守原则, 等于也视为触及 |
| confidence=1.0(CONFIRMED) | 最高优先级, 喂给融合引擎主导决策 |

## 8. 测试计划

- 止损位偏移 BELOW/ABOVE/自定义比例
- 软止损 NORMAL→OBSERVING(触及)
- 软止损 OBSERVING→CONFIRMED(收盘跌破)
- 软止损 OBSERVING→CLEARED(回升)
- 软止损 CONFIRMED 终态保持
- 软止损 CLEARED→OBSERVING(重新触发)
- 价格==止损位触发 OBSERVING
- 输入校验(symbol空/止损位≤0/价格≤0/偏移越界)
- 构造器校验(默认偏移≤0/>10%)
- AdjustedStopLevel 校验
- 事件回调触发+故障隔离
- 时钟注入
- 端到端生命周期(NORMAL→OBSERVING→CONFIRMED)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-015`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-015` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-015` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-015 | MOD-SELL-015 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 9.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §9（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


