---
module_id: MOD-MKT-005
title: "自动加载器蓝图 — 从配置自动创建+注册行情数据源"
doc_type: blueprint
status: Active
version: "0.1.0"
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
