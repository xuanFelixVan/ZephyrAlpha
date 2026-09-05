---
module_id: MOD-SELL-001
title: "卖出信号收集器蓝图 — 8类卖出信号聚合+去重"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
build_status: production
ttl: permanent
layer: L03_sell_decision
layer_name: sell_decision
functional_domain: sell_decision
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
---

# MOD-SELL-001 | Sell Signal Collector 卖出信号收集器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P0 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: stable | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-001 (node 7604386)

## 1. 模块定位

卖出信号收集器——卖出信号管道入口, 汇聚 8 类卖出信号并标准化为 SellSignal 列表, 去重后喂给 SELL-02 评分器 / SELL-07 融合引擎。

插入位置: D-SELL-DECISION 收集层(第一层)入口, 消费各域 provider 注册的信号, 产出标准化 SellSignal。

依据: `D:\临时工作区\依赖图\31-D-SELL-DECISION-卖出决策域.md` §1.1 SELL-01, §3 域间依赖

## 2. 不变量 (INVARIANTS)

- **去重规则**: 同 symbol + 同 signal_type + 同 direction → 保留 confidence 最高者
- **confidence ∈ [0,1]**: 越界抛 InvalidSellSignalError
- **8 类信号不可扩展**: 架构硬边界, 新增信号类型需架构评审(影响融合仲裁完整性)
- **每类信号最多一个 provider**: 避免多源冲突, 由 provider 内部聚合多源
- **隔离故障**: 单个 provider 收集失败不阻断其他 provider(捕获异常记录日志)
- **不可变值对象**: SellSignal frozen=True, 一旦创建不可修改
- **symbol 非空**: 必填校验

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidSellSignalError | ZA-SELL-0001 | confidence 越界 / symbol 为空 / signal_type 类型错 / provider 非 callable 且无 .provide() |
| DuplicateProviderError | ZA-SELL-0002 | 同一 signal_type 重复注册 provider |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.shared.foundation.errors | ZephyrBaseError | 错误基类 |
| 消费者 | MOD-SELL-002 评分器 | SellSignal | 卖出信号(含 signal_type/confidence/timeframe) |
| 消费者 | MOD-SELL-007 融合引擎 | SellSignal | 多信号加权融合入口 |
| 消费者 | D-POSITION | 仓位状态反馈 | 持仓状态作为 context 传入 |

## 5. 8 类卖出信号 (架构硬边界)

| signal_type | 中文名 | 来源域 |
|-------------|--------|--------|
| FUNDAMENTAL | ① 基本面恶化 | D-FUNDAMENTAL |
| TECHNICAL | ② 技术面卖出 | D-SIGNAL |
| VOLUME_PRICE_DIVERGENCE | ③ 量价背离 | D-SIGNAL |
| MAIN_FORCE_DISTRIBUTION | ④ 主力出货 | D-SIGNAL(复用 L2-B 六阶段) |
| RELATIVE_STRENGTH | ⑤ 相对强弱卖出 | D-SIGNAL |
| OPPORTUNITY_COST | ⑥ 机会成本(置换) | D-PF-CORE |
| TIME_STOP | ⑦ 时间止损 | D-PF-CORE |
| BREAKOUT_FAILURE | ⑧ 突破成败 | D-SIGNAL |

## 6. 接口

### Provider 协议
```python
class SellSignalProvider(Protocol):
    signal_type: SellSignalType
    def provide(self, symbol: str, now: datetime, context: dict | None = None) -> list[SellSignal]: ...
```

### 收集器
```python
collector = SellSignalCollector()
collector.register(SellSignalType.TECHNICAL, technical_provider)
signals = collector.collect("000001.SZ", now=datetime.now(timezone.utc))
# → 标准化去重后的 SellSignal 列表(按 confidence 降序)
```

### 数据模型
```python
@dataclass(frozen=True)
class SellSignal:
    symbol: str
    signal_type: SellSignalType
    direction: SellDirection          # REDUCE/CLEAR/REPLACE
    confidence: float                 # [0,1]
    timeframe: SignalTimeFrame        # DAILY/HOUR_60/MIN_15/MIN_5/UNKNOWN
    source: str
    reason: str
    strategy_id: str
    strength: float
    metadata: dict
    timestamp: datetime
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 聚合器模式(provider 注册) | 本模块不生成具体信号, 只定义契约+聚合+去重, 解耦信号源 |
| 每类信号单一 provider | 避免多源冲突, 由 provider 内部聚合(如 D-SIGNAL 内部合并多个技术指标) |
| 去重保留最高 confidence | 同一信号多次触发取最强, 避免重复计数 |
| SellSignal frozen 不可变 | 便于在融合仲裁中安全传递, 防止意外篡改 |
| v6.0 多时间框架字段 | 标注 timeframe 供 SELL-07 共振增强, 兼容旧源(UNKNOWN) |
| 故障隔离(捕获异常) | 单 provider 挂不影响其他, 保证管道可用性 |
| 8 类不可扩展硬边界 | 卖出信号种类影响融合仲裁完整性, 新增需架构评审 |

## 8. 测试计划

- 8 类信号类型枚举完整性
- SellSignal 校验(symbol 空/confidence 越界/signal_type 类型错)
- 注册 provider(协议对象 / 直接 callable / 重复注册抛错 / 非法 provider 抛错)
- 收集去重(同 key 保留最高 confidence)
- 收集排序(按 confidence 降序)
- 多 provider 混合收集
- 单 provider 故障隔离(异常不阻断其他)
- 注销 provider
- 注册类型列表查询
- 时间框架字段标注

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-001` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-001` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-001 | MOD-SELL-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
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


