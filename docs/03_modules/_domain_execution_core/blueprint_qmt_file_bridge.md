---
module_id: MOD-L06-001-QMTFB
submodule_path: src/zephyr/ex_core/adapters
title: "QMT File Bridge Broker 蓝图 — 大QMT文件桥执行器适配器"
doc_type: blueprint
status: Draft
version: "0.2.0"
layer: L2_domain
layer_name: trade_execution
functional_domain: execution
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-08-26"
last_updated: "2026-08-26"
last_verified: "2026-08-26"
valid_from: "2026-08-26"
ttl: permanent
actual_disk_path: "src/zephyr/ex_core/adapters/"
belongs_to: "MOD-L06-001"
parent_module: "MOD-L06-001"
generation: 2
codification_level: L1
rule_form: structural
scope: module
stability: evolving
verifiability: manual
ssot_yaml: "docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md"
summary: "QMT File Bridge Broker——大QMT文件桥执行器适配器，实现BrokerInterface异步文件语义版本。通过指令CSV文件与沙箱内哑执行器(v14)双向通信，替代miniQMT xttrader直连。核心差异：submit_order写入指令文件返回本地order_id，broker_order_id等柜台remark确认后异步回填。"
tags: [trade-execution, l06, qmt-file-bridge, miniqmt-replacement, async-broker, file-based-execution]
priority: P0
runtime_plane: hot
depends_on:
  - target: "MOD-L06-001"
    at: "BrokerInterface"
    why: "继承OCP-003扩展点，实现异步文件语义"
  - target: "MOD-L00-001"
    at: "N/A"
    why: "无共享连接（文件桥无实时连接，与D_DATA解耦）"
  - target: "MOD-BT-001"
    at: "MatchingLogic"
    why: "复用撮合逻辑做无盘口预校验（降级模式）"
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\07_trading_decision_architecture\\design_memos\\93_qmt_file_bridge_playbook.md"
    section: "全篇"
    why: "操作手册：配置步骤、验证结果、排障指南、v14机制说明"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_execution_core\\blueprint.md"
    section: "§16.7.1 MiniQmtBroker"
    why: "参考：A股约束校验、价格笼子、幂等模式、错误码映射"
responsibility_domain: 
design_maturity: design
build_status: generated
---

# QMT File Bridge Broker 蓝图 — 大QMT文件桥执行器适配器

> **真源声明**：本蓝图是 QMT File Bridge Broker 模块的唯一真源。
> **上游衔接**：[93_qmt_file_bridge_playbook.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/93_qmt_file_bridge_playbook.md)（操作手册+实证证据）→ 本蓝图（架构设计+接口契约）→ 施工代码。

## 1. 一句话定位

**QMT File Bridge Broker 是 BrokerInterface 的异步文件语义实现——通过"写指令CSV → 沙箱哑执行器消费 → 读回执/柜台确认"替代 miniQMT xttrader 直连，在穿透式监管合规框架下实现项目大脑与券商柜台的双向通道。**

## 2. 背景与必然性

### 2.1 政策倒逼（已兑现）

- 2026-09-18 miniQMT 全面清退，xttrader 直连模式死亡
- 大QMT 沙箱模式唯一合规：策略跑在券商视野内，文件交换是官方认可介质

### 2.2 与 MiniQmtBroker 的本质差异

| 维度 | MiniQmtBroker (xttrader) | QmtFileBridgeBroker (文件桥) |
|---|---|---|
| 连接方式 | TCP 实时连接 xttrader | **无连接**，异步文件轮询 |
| submit_order | 同步返回 broker_order_id | **返回本地 order_id**，broker_order_id 异步回填 |
| 延迟 | 毫秒级 | **1~2 秒**（tick 触发）+ 柜台确认 1~2 秒 |
| 幂等机制 | idempotency_key 内存映射 | **两阶段文件状态机**（#SENDING→#DONE） |
| 撤单定位 | broker_order_id 直接撤 | **按 remark（userOrderId）反查 sysid** |
| 行情依赖 | 实时 5 档盘口 | **无实时盘口**，预校验降级 |
| 断线重连 | 四步重连机制 | **无概念**，文件持久化天然容错 |

## 3. 模块边界

### 3.1 职责（What it does）

1. **指令生成**：将 Order 契约转换为文件桥指令 CSV 行（order_id,action,symbol,side,qty,pricetype,price）
2. **指令写入**：原子写入指令文件（`orders_{env}.csv`），防并发覆盖
3. **状态轮询**：周期性读取指令文件状态（裸行→#SENDING→#DONE/#FAIL），驱动本地订单状态机
4. **回执解析**：读取回执文件（`ack_{env}.csv`），提取 SENT/CONFIRMED/FAIL/CANCEL_SENT 事件
5. **柜台同步**：读取官方导出 Order.csv/Deal.csv，按 remark 反查 broker_order_id，回填 Order.broker_order_id
6. **持仓快照**：读取 PositionStatics.csv + Account.csv，构造 PositionSnapshot
7. **撤单路由**：生成 cancel 指令行，按目标订单 remark 定位

### 3.2 非职责（What it does NOT do）

- ❌ 不直接调用 passorder/cancel（沙箱内哑执行器 v14 的职责）
- ❌ 不维护实时行情（无 xtdata 连接，行情由 D_DATA 其他 Provider 负责）
- ❌ 不做算法单切片决策（TWAP/VWAP 切片逻辑在 ExecutionEngine/LocalOrderQueue，本 Broker 只执行单笔指令写入）
- ❌ 不做风控校验（OrderManager/ExecutionEngine 已前置）
- ❌ 不管理订单队列（LocalOrderQueue 负责算法单排队，本 Broker 只负责单笔下发的文件写入）

## 4. 接口契约

### 4.1 继承 BrokerInterface 的语义扩展

```python
class QmtFileBridgeBroker(BrokerInterface):
    """文件桥语义扩展说明：

    connect() -> bool:
        语义：校验桥接目录可读写 + 指令文件可创建
        返回：True=目录就绪，False=目录不可写

    submit_order(order: Order) -> str:
        语义：写入指令行到 orders_{env}.csv，返回**本地 order_id**（非 broker_order_id）
        关键：order.idempotency_key 作为指令 order_id 写入，柜台 remark 将携带此值
        异步：真实 broker_order_id 等柜台 remark 确认后，由 _sync_counter_orders() 回填

    cancel_order(broker_order_id: str) -> bool:
        语义：写入 cancel 指令行，target=broker_order_id（即 remark）
        关键：broker_order_id 在此上下文中=原订单的 idempotency_key（remark）
        异步：撤单结果等柜台确认后，由 _sync_counter_orders() 更新状态

    query_order(broker_order_id: str) -> Order | None:
        语义：从本地缓存 + 官方导出 Order.csv 合并查询
        关键：broker_order_id 在此上下文中=本地 order_id 或 remark

    get_positions() -> PositionSnapshot:
        语义：读取 PositionStatics.csv + Account.csv，构造快照
    """
```

### 4.2 新增内部契约

```python
@dataclass
class FileBridgeInstruction:
    """文件桥指令行（CSV 一行）"""
    order_id: str           # 本地订单 ID = idempotency_key = 柜台 remark
    action: str             # "order" | "cancel"
    symbol: str             # 标的代码（如 510300.SH）
    side: str               # "buy" | "sell"（action=order 时有效）
    qty: int                # 数量（股）
    pricetype: str          # "latest" | "limit"
    price: float            # 限价（pricetype=limit 时有效，否则 0）


@dataclass
class FileBridgeAck:
    """回执事件（ack_{env}.csv 一行）"""
    order_id: str
    status: str             # SENT | CONFIRMED | FAIL | CANCEL_SENT | RETRY
    detail: str             # 附加信息（sysid / error_msg / attempt_n）


@dataclass
class CounterOrderRecord:
    """柜台委托记录（官方导出 Order.csv 一行解析后）"""
    remark: str             # 投资备注 = 本地 order_id
    sysid: str              # 柜台合同编号
    status: str             # 已报 | 已撤 | 已报待撤 | 已成 | 等
    symbol: str
    price: float
    qty: int
    filled_qty: int
```

## 5. 数据流

### 5.1 下单流程（Import）——支持算法单排队

**场景 A：整笔直发（做 T 手动/条件单触发）**

```
策略层 Order (CTR-004)
    ▼
ExecutionEngine.execute_order(algo=MARKET)
    ▼
OrderManager.submit_order(broker_id="qmt_real" 或 "qmt_sim")
    ▼
QmtFileBridgeBroker.submit_order(order)
    │ ① A股约束校验（board_lot/price_cage 降级无盘口）
    │ ② 生成 FileBridgeInstruction(order_id=idempotency_key)
    │ ③ 原子写入 orders_{env}.csv
    │ ④ 本地缓存 _order_cache[order_id] = Order(status=SUBMITTED)
    │ ⑤ 返回 order_id（broker_order_id 异步回填）
    ▼
[异步] 沙箱 v14 消费 → passorder → ack → 柜台
    ▼
[异步] _sync_loop()（3秒轮询）→ 读 Order.csv → 回填 broker_order_id + 状态更新
```

**场景 B：算法单排队（TWAP/VWAP 切片，本地队列缓冲）**

```
策略层 Order (CTR-004, 1000股)
    ▼
ExecutionEngine.execute_order(algo=TWAP, slices=10)
    │ 生成 10 笔子订单（每笔 100股）
    ▼
LocalOrderQueue（本地订单队列，新增模块）
    │ 入队 10 笔子订单，按时间间隔排序（如每 3 分钟 1 笔）
    │ 队列状态：[T1待发][T2待发][T3待发]...
    ▼
[每 3 分钟] LocalOrderQueue.dequeue() → 取 1 笔
    ▼
OrderManager.submit_order(broker_id="qmt_real")
    ▼
QmtFileBridgeBroker.submit_order(order)  ← 同场景 A
    │ 写入 orders_real.csv（**只写 1 行**，QMT 通道窄但本地排队）
    ▼
...（3 分钟后下一笔，直到队列空）
```

**关键设计**：QMT 通道窄（一次 1~2 单），但**排队在本地**，QMT 永远不觉得挤。算法逻辑在本地大脑，QMT 只是执行器。

### 5.2 撤单流程

```
策略层 cancel_order(order_id)
    ▼
OrderManager.cancel_order(order_id)
    │ _order_broker_map 路由到 qmt_file_bridge
    ▼
QmtFileBridgeBroker.cancel_order(broker_order_id=remark)
    │ ① 生成 FileBridgeInstruction(action="cancel", order_id=f"C{original_order_id}", symbol=original_remark)
    │ ② 写入 orders_{env}.csv
    │ ③ 返回 True（**仅表示指令已写入**，不表示柜台已撤）
    ▼
[异步] 沙箱哑执行器 v14 消费 → cancel(sysid) → 写 ack
    ▼
[异步] _sync_counter_orders() 检测到 status="已撤" → 更新本地 Order.status=CANCELLED
```

### 5.3 持仓查询流程（Export）

```
QmtFileBridgeBroker.get_positions()
    │ ① 读 E:\qmt_bridge{env}\Stock\PositionStatics.csv（GBK，共享读模式）
    │ ② 读 E:\qmt_bridge{env}\Stock\Account.csv
    │ ③ 解析为 holdings/cash/market_values
    │ ④ 构造 PositionSnapshot
    ▼
返回 PositionSnapshot（CTR-006）
```

## 6. 五图对齐

### 6.1 模块依赖图

```
QmtFileBridgeBroker (env="real"/"sim")
    ├── BrokerInterface (trading_contracts) [继承]
    ├── Order/Fill/PositionSnapshot (shared.contracts) [消费]
    ├── board_lot (ex_core) [复用：A股整手校验]
    ├── price_cage (ex_core) [复用：价格笼子，降级无盘口]
    ├── MatchingLogic (backtest.core) [复用：预校验，降级模式]
    └── [无] xttrader/xtdata [彻底解耦]

LocalOrderQueue（新增，算法单排队）
    ├── Order (shared.contracts) [消费]
    ├── ExecutionEngine (ex_core) [被调用：算法单切片入队]
    └── OrderManager (ex_core) [调用：按间隔逐笔 submit]
```

### 6.2 状态机图（本地订单）

```
PENDING → SUBMITTED（指令写入文件）
    │
    ├──→ FILLED（柜台确认"已成"）
    │
    ├──→ CANCELLED（柜台确认"已撤"）
    │
    ├──→ REJECTED（柜台"废单" 或 #FAIL 3次重试失败）
    │
    └──→ PARTIAL（柜台"部成"）→ FILLED
```

### 6.3 文件状态机图（指令行生命周期）

```
裸行（待消费）
    │
    ▼ _mark_sending() 原子改名
#SENDING（已发待柜台确认）
    │
    ├──→ #DONE（柜台 remark 匹配，确认）
    │
    ├──→ 裸行（30 tick 超时，回滚重试）
    │
    └──→ #FAIL（3次重试失败，终态）
```

### 6.4 数据流图（双向）

```
Import（项目→QMT）：
  Order → [整笔直发] → FileBridgeInstruction → orders_{env}.csv → [沙箱v14] → 柜台
         ↘ [算法单] → LocalOrderQueue 排队 → 按间隔逐笔 → 同上

Export（QMT→项目，3秒轮询）：
  柜台 → 官方导出 CSV ─┬─→ Order.csv → _sync_counter_orders() → Order.status/broker_order_id
                      ├─→ Deal.csv → _parse_fills() → Fill → OrderManager._on_fill()
                      ├─→ PositionStatics.csv → get_positions()
                      └─→ Account.csv → get_positions()
```

### 6.5 部署图（双终端隔离）

```
┌─────────────────────────────────────────┐
│  ZephyrAlpha 本地大脑                    │
│  ├─ ExecutionEngine                     │
│  │   └─ TWAP/VWAP 切片 → LocalOrderQueue│
│  ├─ LocalOrderQueue（新增，算法单排队）  │
│  ├─ OrderManager                        │
│  │   ├─ broker_id="qmt_real" ─────┐     │
│  │   └─ broker_id="qmt_sim" ──────┼──┐  │
│  └─ QmtFileBridgeBroker ◄─────────┘  │  │
│       (env="real")                   │  │
│       │ 写 E:\qmt_bridge\orders_real.csv      │  │
│       │ 读 E:\qmt_bridge\ack_real.csv         │  │
│       │ 读 E:\qmt_bridge\Stock\*.csv          │  │
│       │                              │  │
│       └─ QmtFileBridgeBroker ◄───────┘  │
│            (env="sim")                   │
│            │ 写 E:\qmt_bridge_sim\orders_sim.csv   │
│            │ 读 E:\qmt_bridge_sim\ack_sim.csv      │
│            │ 读 E:\qmt_bridge_sim\Stock\*.csv     │
└────────────┼─────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  大QMT 实盘终端（XtItClient.exe）        │
│  ├─ 模型交易：ZEPHYR_EXEC_REAL (v14)    │
│  │   分笔线周期，1~2秒触发              │
│  │   读 orders_real.csv → passorder    │
│  │   写 ack_real.csv                   │
│  └─ 官方自动导出 → Stock/*.csv          │
└─────────────────────────────────────────┘
             │ 报单进券商柜台（8887871993）
             ▼
┌─────────────────────────────────────────┐
│  大QMT 模拟终端（XtItClient.exe）        │
│  ├─ 模型交易：ZEPHYR_EXEC (v14)         │
│  │   分笔线周期，1~2秒触发              │
│  │   读 orders_sim.csv → passorder     │
│  │   写 ack_sim.csv                    │
│  └─ 官方自动导出 → Stock/*.csv          │
└─────────────────────────────────────────┘
             │ 报单进模拟柜台（8886156677）
             ▼
┌─────────────────────────────────────────┐
│  国金证券柜台/模拟柜台                   │
└─────────────────────────────────────────┘
```

## 7. 关键设计决策

### 7.1 为什么不用长连接/共享内存？

- **合规**：穿透式监管要求策略在券商沙箱内运行，外部进程只能文件交换
- **简单**：文件是官方认可介质，零额外依赖，GBK 编码已验证
- **容错**：文件持久化天然防丢，进程崩溃重启后状态可恢复

### 7.2 为什么幂等必须用文件状态机而非内存？

- **实证**：分笔线 1~2 秒触发，handlebar 重入/嵌套，内存集合（sent/in-flight）在重入瞬间未生效
- **原子性**：`_mark_sending()` 文件改名是同步 I/O，重入者立即看见 `#SENDING` 状态
- **持久性**：策略重启后 `#SENDING` 状态仍在，30 tick 超时自动回滚，不会丢单

### 7.3 为什么预校验降级为"无盘口模式"？

- 文件桥无实时 5 档盘口，MatchingLogic 无法做精确预成交
- 降级方案：
  - 保留 board_lot 整手校验（本地规则，无需盘口）
  - 保留 price_cage 但基准价用昨收/最新价（从 D_DATA 其他 Provider 获取，非实时）
  - 取消 MatchingLogic 预成交（无盘口输入）

### 7.4 为什么撤单按 remark 反查而非 broker_order_id？

- 文件桥 submit_order 返回时还不知道 broker_order_id（异步回填）
- 撤单指令必须在 broker_order_id 未知时就能发出
- 柜台 remark = userOrderId = 本地 order_id = idempotency_key，是唯一稳定锚点

### 7.5 为什么算法单排队在本地而非 QMT 内？

- **QMT 通道窄**：实证发现柜台对程序化报单有同标的同向未成交挂单上限（约 2~3 笔），超限静默拒绝
- **本地排队灵活**：LocalOrderQueue 在本地大脑，可按任意时间间隔（3 分钟/5 分钟/自定义）逐笔发送，QMT 永远只看到 1~2 笔待执行
- **算法逻辑归属**：TWAP/VWAP 切片决策在 ExecutionEngine/LocalOrderQueue（本地），QMT 只是执行器，符合"大脑在本地"架构

### 7.6 为什么双 Broker 实例而非单实例动态切换？

- **物理隔离铁律**：playbook 明确"多终端禁止共用同一导出目录"，实盘/模拟必须物理隔离
- **状态清晰**：`QmtFileBridgeBroker(env="real")` 和 `QmtFileBridgeBroker(env="sim")` 各自持有独立的文件路径、缓存、同步线程，永不串扰
- **OrderManager 路由明确**：`broker_id="qmt_real"` vs `"qmt_sim"`，调用方显式选择，无隐式切换风险

### 7.7 为什么同步轮询定为 3 秒？

- **做 T 场景够用**：价差窗口通常 30 秒~几分钟，3 秒知道成交状态完全不影响决策
- **稳定性优先**：1 秒轮询文件读写冲突风险高（QMT 官方导出 0.1 秒间隔，但频繁读写可能读到半截）；5 秒稍慢，3 秒是平衡点
- **可配置**：`sync_interval` 参数暴露，后续可按需调整

## 8. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| 柜台挂单上限导致丢单 | 中 | 单订单延迟 | v14 自愈重试（30 tick 超时回滚，3 次 #FAIL 报警） |
| 官方导出延迟导致状态误判 | 高 | 状态滞后 10 秒 | 状态机容忍中间态（"已报待撤"），不据此做最终决策 |
| 文件并发写入冲突 | 低 | 指令丢失 | 原子写入（先写临时文件再 rename）+ 文件锁 |
| GBK 编码解析错误 | 低 | 回执解析失败 | 统一 GBK 解码 + 容错跳过非法行 |
| 沙箱策略意外停止 | 中 | 通道中断 | 心跳检测（TICKS=n 日志），项目侧告警 |

## 9. 测试策略

### 9.1 单元测试（tests/ex_core/adapters/test_qmt_file_bridge_broker.py）

- 指令生成：Order → FileBridgeInstruction 字段映射正确
- 文件写入：原子写入防并发（多线程同时 submit）
- 状态机：#SENDING → #DONE 转换正确
- 回执解析：ack 文件各种状态（SENT/CONFIRMED/FAIL/RETRY）解析正确
- 柜台同步：Order.csv 解析 + remark 匹配 + broker_order_id 回填
- 持仓解析：PositionStatics.csv + Account.csv → PositionSnapshot

### 9.2 集成测试（模拟终端）

- 端到端：submit_order → 模拟终端消费 → ack 回读 → 状态更新
- 撤单端到端：cancel_order → 模拟终端撤单 → 状态更新
- 自愈测试：人为制造 #SENDING 卡死，验证超时回滚重试

### 9.3 实盘验证（已部分完成）

- ✅ 2026-08-26 11:26 R1001 实盘下单/撤单全链路通过

## 10. 施工清单

| # | 任务 | 产出 | 依赖 |
|---|---|---|---|
| 1 | QmtFileBridgeBroker 核心类 | `src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py` | 本蓝图 |
| 2 | 指令文件原子写入器 | 同上（内部方法） | 无 |
| 3 | 回执/柜台 CSV 解析器 | 同上（内部方法） | GBK 编码处理 |
| 4 | 后台同步线程（3秒轮询） | 同上（_sync_loop） | 无 |
| 5 | LocalOrderQueue 本地订单队列 | `src/zephyr/ex_core/local_order_queue.py` | 算法单排队 |
| 6 | ExecutionEngine 接入 LocalOrderQueue | `execution_engine.py` 修改 | TWAP/VWAP 切片入队 |
| 7 | 单元测试 | `tests/ex_core/adapters/test_qmt_file_bridge_broker.py` + `test_local_order_queue.py` | pytest |
| 8 | 集成到 OrderManager | 注册 broker_id="qmt_real"/"qmt_sim" | OrderManager 现有 |
| 9 | 模拟终端端到端验证 | 测试报告 | 模拟终端 v14 运行 |
| 10 | 文档更新 | 93 playbook + AGENTS.md 补记 | 施工完成后 |

## 11. 修订记录

| 版本 | 日期 | 内容 |
|---|---|---|
| 0.1.0 | 2026-08-26 | 初版：基于 93 playbook v1.4.0 实证结论，定义异步文件语义 BrokerInterface 扩展 |
| 0.2.0 | 2026-08-26 | 用户裁决落地：①算法单本地排队（LocalOrderQueue）非禁止；②双 Broker 实例（qmt_real/qmt_sim）物理隔离；③同步轮询 3 秒 |

