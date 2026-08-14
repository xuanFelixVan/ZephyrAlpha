---
module_id: MOD-SELL-003
title: "突破成败检测器蓝图 — 压力位突破判定+强制清仓"
doc_type: blueprint
status: Active
version: "0.1.1"
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

# MOD-SELL-003 | Breakout Failure Detector 突破成败检测器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P1 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: stable | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-003 (node 7604388)

## 1. 模块定位

突破成败检测器——消费 L1 因子层压力位计算结果, 判定突破成功/失败, 产出 BreakoutResult 喂给 SELL-01 收集器(第⑧类信号源)和 D-POSITION(持有/加仓信号)。

插入位置: D-SELL-DECISION 信号生成层(第一层), 消费 D-FACTOR 压力位, 产出 BreakoutResult。

依据: `D:\临时工作区\依赖图\31-D-SELL-DECISION-卖出决策域.md` §1.1 SELL-03

## 2. 不变量 (INVARIANTS)

- **突破成功**: 价格 > 压力位 → SUCCESS(持有/加仓, 不卖出)
- **突破失败**: 价格 ≤ 压力位 → FAILURE(减仓), 累计挑战次数+1
- **强制清仓**: 第 K 次挑战失败 K≥阈值(默认3) → FORCED_CLEAR(清仓, confidence=1.0 最高优先级)
- **confidence ∈ [0,1]**: 强制清仓=1.0, 突破失败随次数递增(base 0.5 + 0.1/次, 上限 0.9)
- **不可变值对象**: BreakoutResult frozen=True
- **挑战次数由调用方维护**: 检测器不持久化状态, challenge_count 作为输入参数

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidBreakoutInputError | ZA-SELL-0003 | symbol 空 / 压力位≤0 / 价格≤0 / 挑战次数<0 / 阈值<1 / success_confidence 越界 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.shared.foundation.errors | ZephyrBaseError | 错误基类 |
| 依赖 | MOD-SELL-001 SellSignalCollector | SellDirection | 复用卖出方向枚举 |
| 消费 | D-FACTOR L1因子层 | 压力位(resistance_level) | 压力位计算结果(外部输入) |
| 产出 | MOD-SELL-001 收集器 | BreakoutResult→SellSignal第⑧类 | 突破失败→止损卖出信号源 |
| 产出 | D-POSITION | BreakoutResult(SUCCESS) | 突破成功→持有/加仓信号 |

## 5. 检测逻辑

### 状态判定
```
if current_price > resistance_level:
    → SUCCESS (突破成功, 持有)
elif challenge_count + 1 >= threshold:
    → FORCED_CLEAR (强制清仓, confidence=1.0)
else:
    → FAILURE (突破失败, 减仓)
```

### confidence 计算
| 状态 | confidence | 说明 |
|------|:----------:|------|
| SUCCESS | 0.8(可配置) | 突破成功置信度 |
| FAILURE | 0.5 + 0.1×(失败次数-1), 上限0.9 | 随挑战次数递增 |
| FORCED_CLEAR | 1.0 | 最高优先级 |

### 强制清仓阈值
- 默认 K≥3 (设计文档 §1.1 SELL-03)
- 可配置(forced_clear_threshold 参数)

## 6. 接口

### 输入
```python
detector.detect(
    symbol: str,
    resistance_level: float,    # 压力位(>0)
    current_price: float,        # 当前价格(>0)
    challenge_count: int,        # 历史挑战失败次数(>=0)
    now: datetime | None = None,
) -> BreakoutResult
```

### 输出数据模型
```python
@dataclass(frozen=True)
class BreakoutResult:
    symbol: str
    status: BreakoutStatus       # SUCCESS/FAILURE/FORCED_CLEAR
    resistance_level: float
    current_price: float
    challenge_count: int         # 含本次(成功不累计)
    confidence: float            # [0,1]
    direction: SellDirection     # SUCCESS→REPLACE(持有) / FAILURE→REDUCE / FORCED_CLEAR→CLEAR
    reason: str
    metadata: dict               # breakout_pct / forced_clear / threshold
    timestamp: datetime
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| A类基础设施(纯检测逻辑) | 不涉及"压力位怎么算"(D-FACTOR职责), 只定义检测契约 |
| 挑战次数由调用方维护 | 检测器无状态, 可并发使用, 状态持久化由上层(D-POSITION/持仓状态机)负责 |
| 价格==压力位视为失败 | 未确认突破, 保守原则(与卖出优先一致) |
| 强制清仓 confidence=1.0 | 最高优先级, 喂给融合引擎时主导决策 |
| 失败置信度随次数递增 | 屡次失败→信号越强, 但上限0.9(不超强制清仓) |
| direction 用 REPLACE 占位持有 | SUCCESS 不卖出, 但 direction 必填, 用 REPLACE 语义=置换(此处=不操作) |
| 事件回调可注入 | 预留 E-SELL-03 BreakoutDetected 事件发布接口 |

## 8. 测试计划

- 突破成功(价格>压力位) + 突破幅度记录
- 突破失败(价格<压力位) + 挑战次数累计
- 价格==压力位视为失败
- 强制清仓(K≥3, confidence=1.0)
- 自定义阈值(K≥2)
- 阈值以下仍是 FAILURE
- 失败置信度递增 + 上限0.9
- 输入校验(symbol空/压力位≤0/价格≤0/挑战次数<0)
- 构造器校验(阈值<1/置信度越界)
- BreakoutResult 校验
- 事件回调触发 + 故障隔离
- 时钟注入
- 多标的独立检测

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-003` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-003` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-003 | MOD-SELL-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
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
