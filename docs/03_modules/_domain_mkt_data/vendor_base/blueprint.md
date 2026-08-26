---
module_id: MOD-MKT-002
title: "Vendor基类蓝图 — 行情数据源抽象接口+状态管理+能力声明"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L01_foundation
layer_name: market_data
functional_domain: mkt_data
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-MKT-002 Vendor Base — 行情数据源基类 蓝图

> **module_id**: MOD-MKT-002 | **域**: D_MKT_DATA | **层**: L1 基础平台
> **优先级**: P1 | **成熟度**: production | **对标能力**: 行情数据源抽象
> **SSoT**: depgraph MOD-MKT-002

## 1. 定位

行情数据源基类——定义所有行情数据 vendor 的统一抽象接口。提供状态管理
(ACTIVE/INACTIVE/DEGRADED/ERROR)、能力声明(支持K线/Tick/Level2)和
健康检查接口, 供 VendorRegistry 注册管理和 Connectors 适配。

属 A 类基础设施(抽象接口定义), 纯基础层不涉及策略。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | symbol, start_date, end_date (查询参数) | — |
| 输出 | list[NormalizedMarketData] (CTR-001) | CTR-001 |
| 输出 | VendorStatus (状态) | — |
| 输出 | VendorCapabilities (能力声明) | — |

## 3. 核心设计

### 3.1 VendorStatus 枚举

| 状态 | 说明 |
|------|------|
| ACTIVE | 正常运行 |
| INACTIVE | 未激活/已停用 |
| DEGRADED | 降级运行(延迟/部分不可用) |
| ERROR | 错误状态(不可用) |

### 3.2 VendorCapabilities 能力声明

| 字段 | 类型 | 说明 |
|------|------|------|
| supports_daily_kline | bool | 支持日K数据 |
| supports_tick | bool | 支持Tick数据 |
| supports_level2 | bool | 支持Level2行情 |
| supports_realtime | bool | 支持实时推送 |

### 3.3 MarketDataVendor ABC

抽象基类, 子类(tushare/akshare/wind等)实现具体接口:
- `vendor_id` (property): vendor 唯一标识
- `status` (property): 当前状态
- `capabilities` (property): 能力声明
- `fetch_daily_kline(symbol, start, end)`: 获取日K数据(抽象方法)
- `health_check()`: 健康检查(抽象方法)

## 4. 关键不变量 (INVARIANTS)

- VendorStatus/VendorCapabilities 为 frozen dataclass/enum
- MarketDataVendor 为 ABC, 不可直接实例化
- status 变更通过 set_status() 方法, 非直接属性赋值
- 纯抽象层, 不包含具体数据源实现

## 5. 错误契约

- `VendorError` (ZA-MKT-0002): vendor 操作异常

## 6. 依赖

- `zephyr.shared.contracts.market_data` (NormalizedMarketData, CTR-001)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-MKT-001(vendor_registry), MOD-MKT-003(connectors)

## 7. 测试

- `tests/market_data/test_vendor_base.py`
- 覆盖: 状态转换合法性、能力声明、ABC不可实例化、子类实现验证

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-MKT-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-MKT-002` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-MKT-002` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-MKT-002 | MOD-MKT-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/market_data/vendor_base.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/market_data/test_vendor_base.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


