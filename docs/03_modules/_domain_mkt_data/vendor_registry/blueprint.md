---
module_id: MOD-MKT-001
title: "Vendor注册表蓝图 — 行情数据源注册/查询/默认源管理"
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
- `VendorNotFoundError` (ZA-MKT-0001): vendor 不存在

## 6. 依赖

- `zephyr.trading` → 无 (本模块不依赖 trading)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 依赖: MOD-MKT-002 (MarketDataVendor 基类)
- 消费者: MOD-MKT-005(autoload), MOD-MKT-003(connectors)

## 7. 测试

- `tests/market_data/test_vendor_registry.py`
- 覆盖: 注册/注销/查询/默认源/重复注册报错/不存在报错/状态过滤/线程安全
