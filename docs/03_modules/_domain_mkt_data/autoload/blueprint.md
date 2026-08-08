---
module_id: MOD-MKT-005
title: "自动加载器蓝图 — 从配置自动创建+注册行情数据源"
doc_type: blueprint
status: Active
version: "0.1.1"
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

# MOD-MKT-005 Autoload — 自动加载器 蓝图

> **module_id**: MOD-MKT-005 | **域**: D_MKT_DATA | **层**: L1 基础平台
> **优先级**: P1 | **成熟度**: production
> **SSoT**: depgraph MOD-MKT-005

## 1. 定位

自动加载器——从配置列表自动创建 MarketDataVendor 实例并注册到 VendorRegistry。
通过 vendor_factory 回调解调解具体 vendor 创建逻辑, 与具体数据源实现解耦。

属 A 类基础设施(配置驱动加载), 纯基础层不涉及策略。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | list[VendorConfig] (配置列表) | — |
| 输入 | vendor_factory (回调创建函数) | — |
| 输入 | VendorRegistry (目标注册表) | MOD-MKT-001 |
| 输出 | AutoloadResult (加载结果) | — |

## 3. 核心设计

### 3.1 VendorConfig

| 字段 | 类型 | 说明 |
|------|------|------|
| vendor_id | str | vendor 唯一标识 |
| vendor_type | str | vendor 类型(如 'tushare'/'akshare') |
| is_default | bool | 是否设为默认数据源 |
| params | dict | vendor 特定参数(API key/timeout等) |

### 3.2 MarketDataAutoloader

- `__init__(registry, vendor_factory)` — 接收注册表和工厂回调
- `load(configs)` — 批量加载: 逐个创建+注册+设默认
- 容错: 单个 vendor 创建/注册失败不阻断整体加载, 记录到 errors

### 3.3 AutoloadResult

| 字段 | 类型 | 说明 |
|------|------|------|
| registered_count | int | 成功注册数 |
| default_vendor_id | str\|None | 默认 vendor ID |
| errors | tuple[str, ...] | 失败项(vendor_id列表) |

## 4. 关键不变量 (INVARIANTS)

- VendorConfig/AutoloadResult 为 frozen dataclass
- load() 不抛异常(单个失败记录到 errors), 除非 registry 操作本身失败
- vendor_factory 为 Callable[[VendorConfig], MarketDataVendor]
- 纯加载层, 不包含具体 vendor 实现

## 5. 错误契约

- `AutoloadError` (ZA-MKT-0005): 加载配置非法(空vendor_id等)

## 6. 依赖

- `zephyr.market_data.vendor_registry` (VendorRegistry)
- `zephyr.market_data.vendor_base` (MarketDataVendor)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)

## 7. 测试

- `tests/market_data/test_autoload.py`
- 覆盖: 正常加载/默认源设置/容错(单个失败不阻断)/空配置/重复vendor跳过/结果统计

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-MKT-005`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-MKT-005` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-MKT-005` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-MKT-005 | MOD-MKT-005 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/market_data/test_autoload.py` | ✅ 已实现 | |

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
