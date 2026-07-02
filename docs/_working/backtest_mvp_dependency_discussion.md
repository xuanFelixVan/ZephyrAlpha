# D_BACKTEST MVP 依赖调研与讨论记录

> **类型**：临时讨论文档（ttl=task_bound，任务结束后可删）
> **创建**：2026-07-02
> **背景**：数据库即将建成，讨论开发顺序 → 确定先做回测引擎 → D_BACKTEST 蓝图已起草（MOD-BT-001 v1.0.0）→ §13 三项待办已完成 → 进入 MVP 5 模块施工前依赖调研

---

## 一、讨论脉络（已完成）

| 阶段 | 结论 |
|------|------|
| 1. 开发顺序 | 数据库建成后先做回测引擎（因子库前置依赖） |
| 2. 蓝图检查 | 项目内无回测蓝图 → 新建 D_BACKTEST 域蓝图 MOD-BT-001 |
| 3. 全面调研 | 发现五方真源不一致等问题 → 从第一性原理修复 |
| 4. 先修复后起草 | 修复已发现问题 → 起草双模式回测蓝图 |
| 5. ADR 否决 | 项目禁用 ADR 术语（决策随时可推翻），改用"架构决策"/"架构裁定" |
| 6. §13 待办执行 | blueprint_registry 注册 + depgraph 激活 + master_blueprint 索引（3项已完成） |
| 7. 工具 bug 修复 | apply_depgraph.add_file_node 补 subdomain_id + extract_depgraph._build_modules_view 修 belongs_to=None |
| 8. MVP 5 模块讨论 | 5 模块大白话解释 + 依赖调研（本文档） |

---

## 二、MVP 5 个模块（大白话）

蓝图 §16.7 列出 MVP 待实现的 5 个模块：

| 模块 | 大白话 | Phase |
|------|--------|:-----:|
| `core/matching_engine.py` | 撮合引擎：模拟交易所怎么成交你的单子（市价/限价/滑点/手续费） | 1 |
| `core/portfolio.py` | 记账本：多少钱、多少股、赚了还是亏了、净值曲线 | 1 |
| `core/data_handler.py` | 水管：从数据库按时间一根K线一根K线喂给回测，禁止偷看未来（PIT） | 1 |
| `core/metrics.py` | 打分器：算 Sharpe/Sortino/MaxDD/IC/IR，衡量策略好坏 | 1 |
| `implementations/event_driven_engine.py` | 组装工：逐bar推进的精确回测（EventLoop），把上面3个零件串起来 | 2 |

**数据流**（蓝图 §3.2 已定死）：
```
data_handler ──按bar推送OHLCV──→ engine ──信号──→ matching_engine ──成交──→ portfolio ──净值──→ metrics ──→ BacktestResult
```

---

## 三、5 模块依赖关系

### 3.1 依赖全景图

```
                        ┌─ 行情数据库（存储层）
                        ↓
                DatabaseService（统一数据访问闸门）
                        ↓
                 data_handler ←── CTR-001 NormalizedMarketData 契约
                        ↓ (按bar推送OHLCV)
                 engine ──→ matching_engine ──→ portfolio ──→ metrics ──→ BacktestResult
                                  ↑                ↑
                        BacktestConfig         Decimal(禁float)
                        (滑点/手续费)
```

### 3.2 分模块依赖

| 模块 | 依赖 | 是否外部 | 说明 |
|------|------|:--------:|------|
| data_handler | 行情数据库 + DatabaseService + CTR-001契约 | 是 | 读数据的"水管"，必须走 DatabaseService |
| matching_engine | BacktestConfig（滑点/手续费）+ A股T+1规则 | 否 | 纯算账，只读配置 |
| portfolio | Decimal + matching_engine成交回报 | 否 | 纯记账本 |
| metrics | portfolio净值序列 + BacktestResult结构 | 否 | 纯计算器 |
| event_driven_engine | data_handler + matching_engine + portfolio + BacktestEngineBase | 否 | 组装工，串前3个零件 |

**结论**：3 个模块（matching/portfolio/metrics）纯计算不连外部，1 个（data_handler）连数据库，1 个（event_driven）纯组装。

---

## 四、调研结论：两个关键问题

### 问题 1：DatabaseService 用哪个 + 蓝图过时 ⚠️ 重大

#### 4.1.1 两个 DatabaseService 实现

| 实现 | 域 | 成熟度 | 业务库支持 |
|------|-----|--------|-----------|
| [infrastructure/database_service.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/database_service.py) (MOD-INF-002) | D_INFRA_RUNTIME | stable | ClickHouse/Redis 预留但**抛 NotImplementedError** |
| [governance/persistence/database_service.py](file:///d:/ZephyrAlpha/src/zephyr/governance/persistence/database_service.py) (SH-DB-001) | D_GOVERNANCE | prototype | 无业务库接口 |

#### 4.1.2 重大发现：蓝图与现实脱节

**infrastructure/database_service.py 第 35 行明确写**：
> "market.duckdb（DuckDB 业务时序库）已于 Spiral 1 删除，按母蓝图改用 ClickHouse"

**但 D_BACKTEST 蓝图 §5.1 仍写**：
> "数据库访问:必须通过DatabaseService,禁止裸duckdb.connect(market.duckdb)"
> "数据库连接:必须显式指定read_only=True"

**现实情况**（从终端确认）：用户正在把行情数据导入 **ClickHouse**（`c1_market.kline_1min`，clickhouse_driver），不是 DuckDB。

#### 4.1.3 矛盾清单

| 项 | 蓝图 §5.1 说的 | 现实 | DatabaseService 支持的 |
|----|--------------|------|---------------------|
| 存储引擎 | DuckDB（market.duckdb） | ClickHouse（c1_market） | ClickHouse 接口未实现 |
| 访问方式 | 禁止裸 duckdb.connect | 用 clickhouse_driver | get_clickhouse_conn() 抛 NotImplementedError |
| read_only | 必须 read_only=True | — | 未实现 |

#### 4.1.4 阻塞影响

**data_handler 是硬依赖 DatabaseService 的**，但：
1. 蓝图说用 DuckDB → 过时，实际用 ClickHouse
2. DatabaseService 的 ClickHouse 接口还没实现（NotImplementedError）
3. → **data_handler 无法通过 DatabaseService 读 ClickHouse，当前是阻塞状态**

#### 4.1.5 待决策

- **决策 A**：先实现 DatabaseService.get_clickhouse_conn()，再写 data_handler（治本，但增加前置工作）
- **决策 B**：data_handler 直接用 clickhouse_driver（绕过 DatabaseService，违反蓝图约束）
- **决策 C**：data_handler 先用 pandas 读 ClickHouse 导出的 parquet（临时方案，绕过数据库）
- **决策 D**：先做不依赖 data_handler 的 3 个模块（matching/portfolio/metrics），data_handler 等 DatabaseService 补齐

---

### 问题 2：NormalizedMarketData 多真源 + 数据脏 ⚠️ 重大

#### 4.2.1 多处定义（违反 SSoT）

Grep 发现 NormalizedMarketData 至少有 **4 处定义/引用**：

| # | 文件 | 性质 | 问题 |
|---|------|------|------|
| 1 | [shared/contracts/market_data.py](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/market_data.py) | CTR-001 codegen 产物（AUTO-GENERATED） | **idempotency_key 重复 3 次**（line 39-41） |
| 2 | [shared/contracts/market/market_data.py](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/market/market_data.py) | backward-compat shim | 转发到 #4 |
| 3 | [market_data/market_data.py](file:///d:/ZephyrAlpha/src/zephyr/market_data/market_data.py) | 又一个 codegen 产物（D_MKT_DATA） | **trace_context 未 import**（latent NameError） |
| 4 | [trading/trading_contracts/market/market_data.py](file:///d:/ZephyrAlpha/src/zephyr/trading/trading_contracts/market/market_data.py) | 真源（被 shim 指向） | 待确认字段一致性 |

#### 4.2.2 数据脏问题

**问题 A：idempotency_key 重复 3 次**
- `shared/contracts/market_data.py` line 39-41：`idempotency_key: str` 出现 3 次
- 根因：`cross_layer_contracts.yaml` CTR-001 的 fields 里 idempotency_key 也重复 3 次（line 115-117）
- 影响：codegen 生成的 dataclass 字段重复（Python 允许但语义错误，后定义覆盖前定义）

**问题 B：trace_context 未 import**
- `market_data/market_data.py` line 47：`trace_context: TraceContext | None = None`
- 但文件 line 17-21 只 import 了 dataclass/field/datetime/Decimal，**没 import TraceContext**
- 影响：运行时 `TraceContext` 未定义 → NameError（但 frozen dataclass 在实例化时才求值，目前可能未触发）

#### 4.2.3 CTR-001 契约声明的 physical_path

契约 `cross_layer_contracts.yaml` CTR-001 声明：
> `physical_path: src/zephyr/shared/contracts/market_data.py`

但实际被 shim 转发到 `zephyr.trading.trading_contracts.market.market_data`。**physical_path 与真源不一致**。

#### 4.2.4 待决策

- **真源归一**：确定 NormalizedMarketData 的唯一真源（shared/contracts 还是 trading/trading_contracts？）
- **数据清洗**：修复 cross_layer_contracts.yaml 中 idempotency_key 重复 3 次的脏数据
- **codegen 修复**：重新 codegen 生成 contract 类，消除重复字段 + 补 import

---

## 五、衍生问题清单

| # | 问题 | 严重度 | 来源 |
|---|------|:------:|------|
| 1 | D_BACKTEST 蓝图 §5.1 DuckDB 约束已过时（market.duckdb 已删） | 高 | 问题1调研 |
| 2 | DatabaseService.get_clickhouse_conn() 未实现（NotImplementedError） | 高 | 问题1调研 |
| 3 | 两个 DatabaseService 实现职责重叠（infrastructure vs governance） | 中 | 问题1调研 |
| 4 | NormalizedMarketData 多真源（4处定义）违反 SSoT | 高 | 问题2调研 |
| 5 | cross_layer_contracts.yaml CTR-001 idempotency_key 重复 3 次 | 中 | 问题2调研 |
| 6 | market_data/market_data.py trace_context 未 import（latent NameError） | 中 | 问题2调研 |
| 7 | CTR-001 physical_path 与实际真源不一致 | 低 | 问题2调研 |

---

## 六、已就位的依赖（不用造）

| 依赖 | 状态 | 位置 |
|------|------|------|
| BacktestEngineBase | ✅ 已实现 | [engine_base.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/engine_base.py) |
| BacktestConfig / BacktestResult | ✅ 已实现 | 同上 |
| CTR-001 契约定义 | ✅ 已冻结 locked-5yr | [cross_layer_contracts.yaml](file:///d:/ZephyrAlpha/architecture_model/contracts/cross_layer_contracts.yaml#L78) |
| CTR-002 契约定义 | ✅ 已冻结 | 同上 |
| 行情数据 | ⏳ 导入中 | ClickHouse c1_market.kline_1min |
| DatabaseService（治理+depgraph） | ✅ 已实现 | infrastructure + governance 两处 |
| DatabaseService（ClickHouse 业务库） | ❌ 未实现 | NotImplementedError |

---

## 七、待用户决策项

1. **DatabaseService ClickHouse 接口**：先实现再写 data_handler？还是 data_handler 临时绕过？
2. **施工顺序**：先做不依赖数据库的 3 模块（matching/portfolio/metrics）？还是等 data_handler 通了再一起？
3. **NormalizedMarketData 真源归一**：哪个是唯一真源？是否现在清洗？
4. **蓝图 §5.1 过时更新**：DuckDB → ClickHouse 的约束更新何时做？
5. **metrics 公式先行**：是否按建议 C 先把 metrics 的 Sharpe/MaxDD/IC 公式定死再施工？

---

## 八、下一步建议

**推荐路径（决策 D + 建议C 组合）**：

1. **先做 3 个纯计算模块**（matching_engine / portfolio / metrics）——不依赖数据库，不阻塞
2. **同时补 DatabaseService.get_clickhouse_conn()**——治本，data_handler 的前置
3. **metrics 公式先定死**——防止算错指标导致假 alpha
4. **data_handler 等 ClickHouse 接口就位后再做**
5. **event_driven_engine 最后做**（Phase 2，依赖前 4 个）

**理由**：3 个纯计算模块零外部依赖，可立即开工；DatabaseService ClickHouse 补齐可与施工并行；这样既不阻塞又能治本。

---

## 九、回测设计 4 处碎片化材料完整对照

> 用户指出回测设计散落 4 处。以下为逐材料对照，标注"已纳入蓝图/遗漏/应纳入"。

### 材料 1：[_domain_simulation/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_domain_simulation/blueprint.md)（MOD-L13-001 实验管理平台）

| 项 | 内容 |
|----|------|
| 状态 | ⛔ ARB-11 T2-deferred，禁止施工（开工条件：B轨容量升级 CAP-C01~C03 + T1层全部激活） |
| 内容 | L13 实验管线层蓝图，含实验管理/模型推断/实验结果上报 |
| 与 D_BACKTEST 关系 | 蓝图 §10.5 已声明"回测与仿真正交，D_BACKTEST 撮合引擎可被 D_SIMULATION 复用" |
| 已纳入蓝图 | ✅ 概念正交声明（回测=过去怎样 vs 仿真=如果怎样） |
| 遗漏 | 无（ARB-11 禁止施工，D_BACKTEST 已独立，不需从此蓝图提取设计） |
| 应纳入蓝图 | 否（此蓝图被 ARB-11 锁定，D_BACKTEST 解除 ARB-11 后已独立） |

### 材料 2：[24_d_backtest.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/02_domain_architecture_docs/24_d_backtest.md)（自动生成域架构文档）

| 项 | 内容 |
|----|------|
| 状态 | 2026-07-02 06:22:06 自动生成快照（**D_BACKTEST 激活前**） |
| 内容 | 7 个空 prototype 模块（全是 `__init__.py`），域内依赖 0，跨域入边 0，跨域出边 0 → **孤立域** |
| 与 D_BACKTEST 关系 | 这是激活前的旧状态。当前 depgraph 已更新：3 production + 6 prototype + 1 deprecated，全部关联 MOD-BT-001 |
| 已纳入蓝图 | ❌ 蓝图未提及此文档 |
| 遗漏 | 此文档**未刷新**（generate_domain_doc.py 未重跑），仍显示孤立域 → 误导后续 AI |
| 应纳入蓝图 | 间接——需重跑 generate_domain_doc.py 刷新此文档，使其反映激活后状态（10 节点 + 跨域依赖） |

### 材料 3：[19-D-SIMULATION-仿真域.md](file:///D:/临时工作区/依赖图/19-D-SIMULATION-仿真域.md)（临时工作区依赖图）⚠️ 遗漏最多

| 项 | 内容 |
|----|------|
| 状态 | DRAFT，L0 未启动，71 个子模块 |
| 内容 | **20+ 个子模块直接回测相关**，含详细能力描述/优先级/理论依据/合并记录 |
| 与 D_BACKTEST 关系 | 大量回测设计散落在此，D_BACKTEST 蓝图只纳入了"方向"，遗漏了"细节" |

**子模块逐项对照**：

| 仿真域子模块 | 详细设计 | 蓝图现状 | 应纳入蓝图 |
|-------------|---------|---------|:---------:|
| D-SIMULATION-40 | 事件驱动与向量化**双模式**回测引擎（双模式切换+精度校验） | ✅ 方向一致（蓝图双模式架构），❌ 未引用来源 | ✅ 蓝图 §3.1 应标注设计来源 |
| D-SIMULATION-34 | 订单撮合引擎（真实市场模拟+撮合规则+滑点模型） | ⚠️ matching_engine 只写一行 | ✅ matching_engine 应引用（撮合规则+市场微观结构） |
| D-SIMULATION-23 | **Sharpe 计算修正器**（无风险利率用中国10年期国债/样本量<60不计算/非正态用Sortino/DSR/滚动rolling/年化按频率自动选择+empyrical集成） | ❌ metrics 完全没写 | ✅✅ **必须纳入**（算错=假alpha） |
| D-SIMULATION-24 | **DSR 计算器**（Deflated Sharpe Ratio，多重测试偏差修正+试次数调整+DSR阈值） | ❌ 未纳入 | ✅ metrics 应纳入（防多重测试偏差） |
| D-SIMULATION-19 | **Walk-Forward 分析器**（滚动窗口回测+样本外验证+参数稳定性+WF审计/合规检查） | ❌ Phase 3 只提文件名 | ✅ overfitting_detector/walk_forward 应引用 |
| D-SIMULATION-25 | Walk-Forward 优化引擎（WFO ~300行+Qlib简化版+完整版+参数网格+交叉验证+过拟合检测） | ❌ 未纳入 | ✅ walk_forward.py 应引用 |
| D-SIMULATION-41 | **实盘环境模拟器**（下单延迟模拟+成交确认+滑点模拟+市场冲击模拟） | ❌ matching_engine 未提及 | ✅ matching_engine 滑点模型应引用 |
| D-SIMULATION-42 | **流动性模型与滑点模拟器**（流动性模型+滑点模型+成交优先级+交易成本模型） | ❌ 未纳入 | ✅ matching_engine 应引用 |
| D-SIMULATION-37 | 回测流水线编排器（7步骤：参数验证→数据准备→逐日回测→绩效计算→报告生成→过拟合检验） | ❌ 未纳入 | ⚠️ 可选（event_driven_engine 可参考） |
| D-SIMULATION-28 | empyrical 集成器（Sharpe/Sortino/Calmar/rolling 指标+API封装） | ❌ 未纳入 | ⚠️ metrics 可选集成 |
| D-SIMULATION-29 | quantstats 集成器（Smart Sharpe 非正态调整） | ❌ 未纳入 | ⚠️ metrics 可选集成 |
| D-SIMULATION-30 | vectorbt 向量化回测集成器（参数网格批量+向量化极快） | ❌ 未纳入 | ⚠️ vectorized_engine 可选集成 |
| D-SIMULATION-38 | 过拟合检验器（样本内vs样本外+交叉验证+多重比较偏差校正） | ⚠️ 蓝图提了 overfitting_detector，未引用细节 | ✅ Phase 3 应引用 |
| SIM-18 | 回测过拟合检测器（研究时手动检测） | ❌ 未体现"分层"概念 | ✅ 三层检测应纳入 |
| SIM-56 | 自动化过拟合检测（上线前自动门禁） | ❌ 未体现"门禁"概念 | ✅ 三层检测应纳入 |
| D-SIMULATION-45 | 回测结果统计显著性检验（t检验） | ❌ 未纳入 | ✅ metrics 应纳入 |
| D-SIMULATION-49 | 回测缓存管理器（结果缓存与复用） | ❌ 未纳入 | ⚠️ v1.1 可选 |
| D-SIMULATION-51 | 回测数据质量检查器（缺失与异常检测） | ❌ 未纳入 | ✅ data_handler 应纳入（PIT数据质量） |
| 合并记录 | SIM-46/56→SIM-18，SIM-60→SIM-49，SIM-62→SIM-51，SIM-65→SIM-54，SIM-66→SIM-55，SIM-50→SIM-45 | ❌ 未体现已做过的去重 | ✅ 蓝图应记录（避免重复造轮子） |
| §20 与回测的区别 | 回测=过去怎样/历史数据/重放；仿真=如果怎样/生成数据/What-if | ✅ 蓝图 §10.5 已纳入 | — |

### 材料 4：src/zephyr/research/backtest_base.py（已迁移）

| 项 | 内容 |
|----|------|
| 状态 | ✅ 已迁移到 backtest/core/engine_base.py（蓝图 §5.3 记录） |
| 内容 | BacktestEngineBase + BacktestResult 雏形，原标记 D_SIMULATION 域 |
| 当前磁盘状态 | research/ 只剩 `__init__.py`，backtest_base.py 已删 |
| 已纳入蓝图 | ✅ §5.3 迁移记录完整 |
| 遗漏 | 无（迁移已完成） |
| 应纳入蓝图 | 否（已完成） |

---

## 十、临时工作区全面搜索结果（架构图 + 依赖图）

> 对 `D:\临时工作区\架构图`（11 文件命中）+ `D:\临时工作区\依赖图`（28 文件命中）全面搜索回测相关内容。

### 10.1 架构图（D:\临时工作区\架构图）—— 交易决策架构最关键

**[交易决策架构.md](file:///D:/临时工作区/架构图/交易决策架构.md)** 含最丰富的回测架构定位：

| 内容 | 详情 | 应纳入蓝图 |
|------|------|:---------:|
| C-003 横切层 | 自动回测与仿真——策略/因子/信号验证算力管道 | ✅ 蓝图 §12 集成目标应引用 |
| 验证流 | 算力有空就跑→回测→模拟盘→提交上线；样本外门禁+过拟合检验(C-033) | ✅ 蓝图 §3.3 状态生命周期应参考 |
| V1~V5 分层验证 | V1方向/V2校准度/V3策略PnL/V4端到端/V5共形预测覆盖率 | ⚠️ 蓝图可纳入 v1.1（超出 MVP） |
| 回测门禁 | C-007 每轮迭代改动必须经过回测门禁（§20.7） | ✅ 蓝图 §5.5 触发机制应引用 |
| 回测管线优先级 | 运行时架构中回测管线=P1（交易流水线P0/数据接入P0） | ✅ 蓝图 §5.4 SLA 应参考 |
| Event Store 回测数据源 | 历史事件流回放→回测数据源 | ⚠️ data_handler 可参考（事件驱动模式） |
| IC 回测与评估 | 因子解析→IC回测与评估→入池审批 | ✅ metrics 的 IC 计算应参考 |
| 回测与仿真对比表 | 旧版无回测与仿真 → 新版 C-003 自动回测与仿真管道+共形V5 | ✅ 蓝图 §18 决策记录应引用 |

### 10.2 依赖图（D:\临时工作区\依赖图）—— 跨域依赖链

| 来源文件 | 回测相关内容 | 应纳入蓝图 |
|---------|------------|:---------:|
| **20-D-RESEARCH** | E-RS-02 BacktestCompleted 事件（回测完成→归因报告）；Feature Store PIT 正确性是回测可信性基石（R-02，避免 look-ahead bias）；VaR 回测要求（Kupiec POF/Christoffersen/Basel 交通灯/通过率>95%） | ✅ E-BT-01 应对齐 E-RS-02；✅ data_handler PIT 应引用 R-02 |
| **01-跨域交叉点** | C-003 自动回测与仿真（V1~V5分层验证）；研究Agent=因子研究+策略回测+实验管理；PIT三平面统一（训练AS OF JOIN+**回测事件回放**+推理Redis）；E-RS-02: L09→L07/L05/L08 | ✅ 蓝图 §3.2 数据流应引用三平面统一；✅ E-BT-01 下游应含 L07/L05/L08 |
| **03-D-FACTOR** | D-FACTOR-03 因子评估=过拟合检测3维度（Walk-Forward/参数敏感性/泛化能力）+前视偏差检测；FAC-ANALYSIS-101 Layered Backtest(GATE-101)；IC回测；PIT三平面一致性校验（训练/**回测**/推理因子值一致） | ✅ metrics 的过拟合检测应引用 D-FACTOR-03 三维度；✅ data_handler 应对齐 PIT 三平面 |
| **00-总览** | INV-004 PIT铁律：零前瞻偏差→fail_backtest（D-FACTOR）；INV-014 Survivorship Bias零容忍→fail_backtest（D-DATA） | ✅ 蓝图 §5.1 约束应引用 INV-004/INV-014 |
| **10-D-REPORTING** | BacktestCompleted→归因报告；差分隐私(ε=1.0)用于策略回测报告；Agent约束：不可绕回测应用优化 | ✅ 蓝图 §12 集成目标 D_REPORTING 应引用 |
| **11-D-RISK** | VaR 回测（1年回测3~10秒，GPU CuPy/PyTorch） | ⚠️ 间接（VaR回测属风控，非策略回测） |
| **05-D-PF-CORE** | 组合优化新方法需回测验证+人工审批(L3) | ✅ 蓝图 §12 集成目标 D_PF_CORE 应引用 |
| **场内模块清单.csv** | `l09_research_innovation/backtest_base.py`(MOD-L09-001 旧位置)；`l09_research_innovation/implementations/default_backtest_engine.py`(旧位置)；`rollback/backtest_engine.py`(MOD-INF-021 回滚引擎，非回测) | ⚠️ 旧路径已迁移；rollback/backtest_engine 是回滚不是回测，勿混淆 |

---

## 十一、应纳入蓝图的设计清单（汇总 + 优先级）

> 综合 4 处材料 + 临时工作区全面搜索，以下设计**应纳入 D_BACKTEST 蓝图**。

### 🔴 P0 必须纳入（不纳入会导致假 alpha / 回测失真）

| # | 设计 | 来源 | 纳入蓝图位置 |
|---|------|------|------------|
| 1 | **Sharpe 计算修正**：无风险利率用中国10年期国债/样本量<60不计算/非正态用Sortino/DSR/年化按频率自动选择 | D-SIMULATION-23 | metrics §4 或 §16.7 |
| 2 | **DSR（Deflated Sharpe Ratio）**：多重测试偏差修正 | D-SIMULATION-24 | metrics §4 |
| 3 | **PIT 铁律 INV-004**：零前瞻偏差→fail_backtest | 00-总览, 03-D-FACTOR | §5.1 约束 |
| 4 | **Survivorship Bias 零容忍 INV-014** | 00-总览 | §5.1 约束 |
| 5 | **PIT 三平面一致性**：训练/回测/推理因子值一致 | 01-跨域, 03-D-FACTOR | data_handler §4 |
| 6 | **Feature Store PIT 正确性**：R-02 避免look-ahead bias，回测可信性基石 | 20-D-RESEARCH | data_handler §4 |
| 7 | **过拟合检测三维度**：Walk-Forward/参数敏感性/泛化能力 | D-FACTOR-03 | overfitting_detector Phase 3 |
| 8 | **过拟合检测三层**：SIM-18研究时手动/SIM-56上线前自动门禁 | D-SIMULATION-18/56 | overfitting_detector Phase 3 |

### 🟡 P1 应纳入（提升回测精确度/完整性）

| # | 设计 | 来源 | 纳入蓝图位置 |
|---|------|------|------------|
| 9 | **撮合引擎详细设计**：真实市场模拟+撮合规则+市场微观结构 | D-SIMULATION-34 | matching_engine §4 |
| 10 | **滑点模型**：实盘环境模拟（下单延迟+成交确认+市场冲击）+流动性模型+交易成本 | D-SIMULATION-41/42 | matching_engine §4 |
| 11 | **Walk-Forward 分析器**：滚动窗口+样本外验证+参数稳定性+WF审计 | D-SIMULATION-19/25 | walk_forward Phase 3 |
| 12 | **回测门禁**：C-007 每轮迭代必须过回测门禁 | 交易决策架构 | §5.5 触发机制 |
| 13 | **回测数据质量检查**：缺失与异常检测 | D-SIMULATION-51 | data_handler §6 |
| 14 | **统计显著性检验**：t检验 | D-SIMULATION-45 | metrics §4 |
| 15 | **E-RS-02 对齐**：E-BT-01 BacktestCompleted 下游应含 L07/L05/L08 | 01-跨域, 20-D-RESEARCH | §3.2 数据流 |
| 16 | **合并记录**：SIM-46/56→SIM-18 等去重，避免重复造轮子 | D-SIMULATION §0.1 | §18 决策记录 |

### 🟢 P2 可选纳入（v1.1+ 或生态集成）

| # | 设计 | 来源 | 纳入蓝图位置 |
|---|------|------|------------|
| 17 | empyrical/quantstats/vectorbt 集成 | D-SIMULATION-28/29/30 | v1.1 生态集成 |
| 18 | 回测缓存管理器 | D-SIMULATION-49 | v1.1 |
| 19 | 回测流水线编排器（7步骤） | D-SIMULATION-37 | event_driven_engine 参考 |
| 20 | V1~V5 分层验证标准 | 交易决策架构 | v1.1 |
| 21 | Event Store 历史事件流回放 | 交易决策架构 | event_driven_engine 参考 |

---

## 十二、更新后的待决策项

> 基于全面搜索，待决策项从原 5 项扩展为 8 项。

1. **DatabaseService ClickHouse 接口**：先实现再写 data_handler？还是临时绕过？
2. **施工顺序**：先做不依赖数据库的 3 模块？还是等 data_handler 通了再一起？
3. **NormalizedMarketData 真源归一**：哪个是唯一真源？是否现在清洗？
4. **蓝图 §5.1 过时更新**：DuckDB → ClickHouse 约束更新何时做？
5. **metrics 公式先行**：是否先把 Sharpe/DSR/IC 公式定死再施工？（**P0 清单#1-2 强烈建议是**）
6. **🔴 蓝图补充 P0 设计**：是否现在把第十一节 P0 清单（8项）补进蓝图？（**建议是——不补会导致假 alpha**）
7. **🟡 蓝图补充 P1 设计**：是否现在把第十一节 P1 清单（8项）补进蓝图？
8. **24_d_backtest.md 刷新**：是否重跑 generate_domain_doc.py 刷新域架构文档（消除"孤立域"误导）？

---

## 十三、结论

**D_BACKTEST 蓝图方向正确但细节严重不足**：
- ✅ 双模式架构、撮合、过拟合检测的**方向**与仿真域设计一致（说明前序会话参考过材料）
- ❌ 但**具体设计细节大量遗漏**：Sharpe 用中国国债无风险利率、滑点的流动性模型、过拟合三层检测、PIT 三平面一致性、INV-004/INV-014 铁律等**都没从材料提炼进蓝图**
- ❌ 临时工作区有**39 个文件**涉及回测（架构图11 + 依赖图28），D_BACKTEST 蓝图只引用了其中一小部分

**风险**：若不补 P0 清单就施工，metrics 可能算错 Sharpe（假 alpha）、data_handler 可能 PIT 失守（未来函数）、overfitting_detector 可能漏检（过拟合上线）。

**建议**：施工前先把第十一节 P0 清单（8项）补进蓝图，P1 清单可与施工并行补充。

---

## 十四、循环搜索 #1 新增发现（扩展关键词搜索）

> 用扩展关键词（撮合/滑点/Sharpe/过拟合/Walk-Forward/前瞻偏差/幸存者偏差/DSR/PIT/事件驱动/向量化）搜索架构图（11文件）+依赖图（25文件），发现 **16 个文件含直接相关的回测引擎设计**，其中 **学习系统架构.md §8.1** 是最核心发现。

### 14.1 最核心发现：[学习系统架构.md](file:///D:/临时工作区/架构图/学习系统架构.md) §8.1 试运行流水线（L1410-L1605）

**这是回测引擎设计的最完整来源**，含完整验证方法栈 + 事件驱动沙盒 + 撮合 + 滑点 + 部署链：

| 设计 | 详情 | 来源行 |
|------|------|--------|
| **DSR 扩展** | 考虑策略间相关性，多策略同时测试时调整多重检验阈值 | L1429 |
| **CPCV v2** | Combinatorial Purged Cross-Validation 扩展版，更稳健的样本外性能估计 | L1433 |
| **White's Reality Check 增强** | 过拟合检测统计功效提升30% | L1437 |
| **Adaptive Walk-Forward** | 自适应窗口步进，根据市场波动率动态调整训练/测试窗口长度 | L1441 |
| **Probabilistic Backtesting** | 贝叶斯回测，输出 P(Sharpe>0)=92% 等概率区间，量化不确定性 | L1445 |
| **信息论过拟合检测**（v6.0） | 互信息/KL散度量化训练vs测试信息增益差异，比DSR更直观 | L1450 |
| **市场状态感知 Walk-Forward**（v6.0） | 趋势期用长窗口，震荡期用短窗口 | L1453 |
| **3阶段决策门控** | IS→稳定性门控→WFA→多数通过+灾难否决→OOS→参数锁定 | L229, L1474 |
| **参数稳定性区域** | 参数扫描→识别稳定高原→选高原中心→避悬崖型参数 | L231 |
| **R-117 Strategy Sandbox** | 纯Python事件驱动策略沙盒：订单→撮合→持仓→净值完整模拟 | L1549 |
| **R-118 Liquidity & Slippage Simulator** | Almgren-Chriss市场冲击模型+滑点模拟（买卖价差+市场深度+订单规模） | L1556 |
| **R-119 Order Matching Simulator** | 限价订单簿模拟+撮合引擎（市价/限价/涨跌停） | L1562 |
| **R-126 Backtest-to-Production Deployer** | 回测→门控验证→灰度发布(5%→20%→50%→100%)→全量上线 | L1575 |
| **R-93 Walk-Forward Analyzer 完整版** | 三种WFA：滚动(固定窗口)/锚定(训练起点固定)/扩展(训练窗口逐步扩展) | L1720 |
| **模拟结果数据契约** | liquidity_slippage/order_matching_result 字段定义 | L1604 |

### 14.2 其他文件新增发现

| 文件 | 新增设计 | 应纳入蓝图 |
|------|---------|:---------:|
| [02-D-DATA](file:///D:/临时工作区/依赖图/02-D-DATA-数据域.md) | PIT Query Engine（DuckDB AS OF JOIN+三平面统一+防幸存者偏差+结果缓存） | ✅ data_handler |
| [04-D-SIGNAL](file:///D:/临时工作区/依赖图/04-D-SIGNAL-信号域.md) | Signal Backtester（信号驱动回测+换手/成本/滑点+前视偏差检测+多重检验校正）；Signal OOS Validator（Walk-Forward+前瞻偏差检测） | ✅ Phase 3 |
| [06-D-PF-ALLOC](file:///D:/临时工作区/依赖图/06-D-PF-ALLOC-组合分配域.md) | 策略7状态生命周期+回测Sharpe>0.5准入门控+回测-实盘Sharpe偏差监控(>30%告警/>50%退役) | ✅ P0 门控 |
| [08-D-EX-CORE](file:///D:/临时工作区/依赖图/08-D-EX-CORE-执行核心域.md) | 3级滑点模型（固定→平方根冲击→订单簿模拟）+R-117/R-118/R-119模拟器+TCA | ✅ matching_engine |
| [09-D-EX-SOR](file:///D:/临时工作区/依赖图/09-D-EX-SOR-执行路由域.md) | Almgren-Chriss市场冲击模型+做T滑点成本(×2)+3级滑点模型 | ✅ matching_engine |
| [12-D-ML-TRAIN](file:///D:/临时工作区/依赖图/12-D-ML-TRAIN-训练域.md) | DSR/CPCV v2/White's Reality/Probabilistic BT+V1-V6分层验证门禁(Walk-Forward贯穿) | ✅ Phase 3 |
| [13-D-ML-SERVE](file:///D:/临时工作区/依赖图/13-D-ML-SERVE-推理域.md) | 回测验证(Purged K-Fold+Walk-Forward)+过拟合否决阈值（**样本外Sharpe<70%样本内→否决**） | ✅✅ P0 |
| [15-D-DATA-ENG](file:///D:/临时工作区/依赖图/15-D-DATA-ENG-数据工程域.md) | FeatureStore PIT AS OF JOIN+PITManager+PIT门控防前瞻偏差+SyntheticDataGenerator禁用于回测 | ✅ data_handler |
| [23-D-AUT-PERM](file:///D:/临时工作区/依赖图/23-D-AUT-PERM-自治保护域.md) | GAP-AP-07回测-实盘偏差监控器+Agent回测门禁约束（权重/信号/做T/择时变更需回测验证） | ✅ P0 门控 |
| [28-D-FRONTEND](file:///D:/临时工作区/依赖图/28-D-FRONTEND-前端域.md) | DSR p值/CPCV结果展示+IS-WFA-OOS决策门控UI | ⚠️ P2 |
| [31-D-SELL-DECISION](file:///D:/临时工作区/依赖图/31-D-SELL-DECISION-卖出决策域.md) | Walk-Forward防过拟合+ATR止损k通过历史回测优化+滑点追踪 | ⚠️ P2 |
| [14-D-ALT-DATA](file:///D:/临时工作区/依赖图/14-D-ALT-DATA-另类数据域.md) | AltDataBacktester+Look-Ahead Bias Detector（幸存者偏差/重述数据检测） | ✅ Phase 3 |
| [安全架构.md](file:///D:/临时工作区/架构图/安全架构.md) | PIT隔离（回测强制按时间点查询，禁止访问未来数据）+D-SIMULATION-22未来函数检测器+D-SIMULATION-56过拟合门禁 | ✅✅ P0 |
| [数据架构.md](file:///D:/临时工作区/架构图/数据架构.md) | PIT三公理+三平面统一+AS OF JOIN+**Embargo期**+pit_consistency_test() CI/CD | ✅✅ P0 |
| [风险架构.md](file:///D:/临时工作区/架构图/风险架构.md) | 过拟合否决阈值（样本外Sharpe<70%）+VaR回测(Kupiec/Christoffersen/Basel交通灯)+Walk-Forward防过拟合 | ✅ P0 门控 |

### 14.3 新增应纳入蓝图清单（在第十一节基础上扩展）

**🔴 新增 P0**（不纳入会导致假alpha/回测失真）：

| # | 设计 | 来源 | 纳入蓝图位置 |
|---|------|------|------------|
| P0-9 | **过拟合否决阈值**：样本外Sharpe<70%样本内→否决上线 | 13-D-ML-SERVE/风险架构 | §5.1 约束 |
| P0-10 | **回测Sharpe准入门控**：Sharpe>0.5才能进入模拟 | 06-D-PF-ALLOC | §5.5 触发机制 |
| P0-11 | **回测-实盘偏差监控**：偏差>30%告警/>50%退役 | 06-D-PF-ALLOC/23-D-AUT-PERM | §5.5 触发机制 |
| P0-12 | **PIT隔离**：回测强制按时间点查询，禁止访问未来数据 | 安全架构 | §5.1 约束 |
| P0-13 | **PIT三公理+Embargo期**+pit_consistency_test() CI/CD | 数据架构 | §5.1 约束 |
| P0-14 | **3阶段决策门控**：IS→WFA→OOS+参数稳定性区域 | 学习系统架构 | §3.3 状态生命周期 |

**🟡 新增 P1**（提升精确度/完整性）：

| # | 设计 | 来源 | 纳入蓝图位置 |
|---|------|------|------------|
| P1-17 | DSR扩展（考虑策略间相关性） | 学习系统架构§8.1 | metrics §4 |
| P1-18 | CPCV v2（Combinatorial Purged Cross-Validation） | 学习系统架构§8.1 | overfitting_detector |
| P1-19 | White's Reality Check增强（功效+30%） | 学习系统架构§8.1 | overfitting_detector |
| P1-20 | Adaptive Walk-Forward（自适应窗口步进） | 学习系统架构§8.1 | walk_forward |
| P1-21 | Probabilistic Backtesting（贝叶斯回测P(Sharpe>0)） | 学习系统架构§8.1 | metrics v1.1 |
| P1-22 | 3级滑点模型（固定→平方根冲击→订单簿模拟） | 08-D-EX-CORE/09-D-EX-SOR | matching_engine §4 |
| P1-23 | Almgren-Chriss市场冲击模型 | 09-D-EX-SOR/R-118 | matching_engine §4 |
| P1-24 | R-117/R-118/R-119模拟器（沙盒/滑点/撮合） | 学习系统架构 | event_driven_engine |
| P1-25 | Signal Backtester（信号驱动回测+多重检验校正） | 04-D-SIGNAL | §12 集成目标 |
| P1-26 | V1-V6分层验证门禁（Walk-Forward贯穿） | 12-D-ML-TRAIN | §3.3 状态生命周期 |
| P1-27 | Look-Ahead Bias Detector（幸存者偏差/重述数据检测） | 14-D-ALT-DATA/安全架构 | data_handler |
| P1-28 | R-126 Backtest-to-Production Deployer（门控+灰度） | 学习系统架构 | §5.5 触发机制 |
| P1-29 | R-93 Walk-Forward三种模式（滚动/锚定/扩展） | 学习系统架构 | walk_forward |
| P1-30 | FeatureStore PIT AS OF JOIN+PITManager | 15-D-DATA-ENG/02-D-DATA | data_handler |

**🟢 新增 P2**（v1.1+或生态集成）：

| # | 设计 | 来源 |
|---|------|------|
| P2-22 | 信息论过拟合检测（互信息/KL散度，v6.0） | 学习系统架构 |
| P2-23 | 市场状态感知Walk-Forward（趋势长/震荡短，v6.0） | 学习系统架构 |
| P2-24 | DSR/CPCV结果展示UI | 28-D-FRONTEND |
| P2-25 | ATR止损k通过历史回测优化 | 31-D-SELL-DECISION |
| P2-26 | VaR回测（Kupiec/Christoffersen/Basel交通灯） | 风险架构/20-D-RESEARCH |
| P2-27 | AltDataBacktester（另类数据回测） | 14-D-ALT-DATA |

### 14.4 间接相关文件（12个，仅引用无设计细节，不需纳入蓝图）

07-D-POSITION、16-D-CROSS-ASSET、17-D-COMPLIANCE、18-D-TRADING、21-D-KNOWLEDGE、30-D-OPS、00-架构图总览、治理架构、运维架构、集成架构、Agent架构、合规架构——这些文件仅引用"回测"作为流程/约束/资源调度，不含回测引擎自身设计。

### 14.5 循环搜索 #2 验证结果（第三轮关键词：Purged/CPCV/Permutation/Bayesian/Almgren/Embargo/订单簿/沙盒/TCA/市场冲击/样本外/试运行）

第三轮关键词命中 6 个新文件（前两轮未命中），逐个验证：

| 文件 | 匹配内容 | 与回测引擎设计关系 | 新增？ |
|------|---------|------------------|:-----:|
| 26-D-SECURITY-安全域.md | "沙箱"（process_sandbox/rollback_sandbox） | ❌ 安全沙箱（进程隔离），非回测 | 否 |
| 24-D-SECURITY-安全域.md | 同上（与26-D-SECURITY内容重复） | ❌ 安全沙箱，非回测 | 否 |
| 29-D-GOVERNANCE-治理域.md | "Bayesian"（PSO隐式依赖发现器理论） | ❌ 治理工具理论，非回测 | 否 |
| 22-D-AUT-CORE-自治核心域.md | "实盘-回测偏差<30%"（策略升级L1→L2条件） | ⚠️ 已在 P0-11 覆盖（06-D-PF-ALLOC/23-D-AUT-PERM） | 否 |
| 24-D-INFRA-RUNTIME.md | D-INFRA-438 策略回测基础设施（计算资源+数据管道+历史回放+沙箱环境） | ⚠️ 基础设施层支持，非回测引擎设计；P2 集成目标 | 否（标注） |
| project-entity-depgraph.yaml | PIT铁律+fail_backtest+BacktestRealtimeDeviationAlert | ⚠️ 已在 P0-3(INV-004)/P0-11(偏差监控) 覆盖 | 否 |

**循环搜索 #2 结论：新增回测引擎设计内容 = 0**

- 6 个新文件均无未纳入的回测引擎设计
- 26/24-D-SECURITY 是安全沙箱，29-D-GOVERNANCE 是治理工具，22-D-AUT-CORE/project-entity-depgraph.yaml 的回测内容已在 P0-11/P0-3 覆盖
- 24-D-INFRA-RUNTIME D-INFRA-438 可作为 P2 集成目标标注（基础设施层回测支持，非引擎设计）

**三轮搜索穷尽性确认**：
- 第一轮（回测/backtest）：39 文件命中
- 第二轮（撮合/滑点/Sharpe/过拟合/Walk-Forward/前瞻/幸存者/DSR/PIT/事件驱动/向量化）：36 文件命中，新增 16 个直接相关
- 第三轮（Purged/CPCV/Permutation/Bayesian/Almgren/Embargo/订单簿/沙盒/TCA/市场冲击/样本外/试运行）：41 文件命中，**新增 0 个回测引擎设计**
- **搜索结束，所有回测引擎相关内容已穷尽纳入讨论文档**
