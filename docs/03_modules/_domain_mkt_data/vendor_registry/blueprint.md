---
module_id: MOD-MKT-001
title: "Vendor注册表蓝图 — 行情数据源注册/查询/默认源管理"
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

# MOD-MKT-001 Vendor Registry — 行情数据源注册表 蓝图

> **module_id**: MOD-MKT-001 | **域**: D_MKT_DATA | **层**: L1 基础平台
> **优先级**: P1 | **成熟度**: production | **对标能力**: 行情数据源管理
> **SSoT**: depgraph MOD-MKT-001

## 1. 定位

行情数据源注册表——管理所有已注册的 MarketDataVendor 实例。提供注册/注销/
查询/默认源管理功能, 供 autoload(MOD-MKT-005)自动加载和 connectors
(MOD-MKT-003)适配查找。

属 A 类基础设施(注册表模式), 纯基础层不涉及策略。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | MarketDataVendor 实例 (注册) | MOD-MKT-002 |
| 输入 | vendor_id (查询/注销) | — |
| 输出 | MarketDataVendor / list[MarketDataVendor] | MOD-MKT-002 |
| 输出 | 默认 vendor | — |

## 3. 核心设计

### 3.1 VendorRegistry 类

| 方法 | 说明 |
|------|------|
| `register(vendor)` | 注册 vendor, 重复 vendor_id 报错 |
| `unregister(vendor_id)` | 注销 vendor |
| `get(vendor_id)` | 按 ID 查询 vendor |
| `list_vendors(status=None)` | 列出所有/按状态过滤 |
| `set_default(vendor_id)` | 设置默认数据源 |
| `get_default()` | 获取默认数据源 |
| `count` (property) | 已注册 vendor 数 |

### 3.2 注册规则

- vendor_id 唯一, 重复注册抛 VendorAlreadyRegisteredError
- 注销不存在的 vendor_id 抛 VendorNotFoundError
- 默认源必须已注册, 否则抛 VendorNotFoundError
- 线程安全(threading.Lock 保护 _vendors 字典)

## 4. 关键不变量 (INVARIANTS)

- VendorRegistry 内部 _vendors 为 dict[str, MarketDataVendor]
- 读写加 threading.Lock, 支持并发注册/查询
- default_vendor_id 为 str | None
- register/unregister/set_default 返回操作结果

## 5. 错误契约

- `VendorAlreadyRegisteredError` (ZA-MKT-0001): 重复注册
- `VendorNotFoundError` (ZA-MKT-0007): vendor 不存在

## 6. 依赖

- `zephyr.trading` → 无 (本模块不依赖 trading)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 依赖: MOD-MKT-002 (MarketDataVendor 基类)
- 消费者: MOD-MKT-005(autoload), MOD-MKT-003(connectors)

## 7. 测试

- `tests/market_data/test_vendor_registry.py`
- 覆盖: 注册/注销/查询/默认源/重复注册报错/不存在报错/状态过滤/线程安全

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-MKT-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-MKT-001` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-MKT-001` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-MKT-001 | MOD-MKT-001 | ✅ |
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
| `src/zephyr/market_data/vendor_registry.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/market_data/test_vendor_registry.py` | ✅ 已实现 | |

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


