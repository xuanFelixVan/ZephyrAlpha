---
blueprint_id: MOD-DAT-REF-DATA
module_name: reference_data_manager
domain: D_DATA
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_DATA
path: src/zephyr/data/reference_data_manager.py
granularity: file
---

# MOD-DAT-REF-DATA reference_data_manager 蓝图（参考数据管理器）

> **module_id**: MOD-DAT-REF-DATA | **域**: D_DATA | **优先级**: P1
> **来源**: B13-04240（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，D-DATA-08，§17.1）
> 代码：`src/zephyr/data/reference_data_manager.py`

## 0. 定位

参考数据管理器：行业分类（GICS+申万）、指数成分（PIT effective_date）、
多源 ID 映射（miniqmt↔tushare↔akshare）的登记/查询/变更事件发布；
SQLite reference_data 表族 DDL 常量随模块交付（建库执行留装配批）。

与既有族分工（查重裁定）：
- instrument_master（MOD-L00-IM，testing）：轻量 IM 15 字段+ST/板块 PIT
  子表（证券主数据最小核）。本模块**复用其最小字段集为锚、不复制**：
  只补行业分类/指数成分/多源映射/变更事件四项缺口。
- B13-04355（D-TRADING-14 Reference Data Manager）dig 已裁定"不做-重复:
  B13-04240"，Golden Record/MDM 分发并入本模块子项。

## 1. 判定核心（纯内存，无 IO）

- `upsert_industry(symbol, gics=None, sw=None, source)`：两码全空 →
  ValueError Fail-Closed；登记并产变更事件。
- `set_index_constituent(index_code, symbol, effective_date)` /
  `remove_index_constituent(index_code, symbol, removed_date)`：PIT 语义；
  `constituents_at(index_code, as_of)` 取 effective_date<=as_of 且
  （removed_date 空或 >as_of）的成分集。
- `register_mapping(symbol, minqmt=None, tushare=None, akshare=None)`：
  三码全空 → ValueError；`map_id(symbol, source, target)` 翻译，
  未知 source/target → ValueError，映射缺失 → None（留痕不炸）。
- 变更事件：每次变更内嵌不可变日志 + 经注入 `event_publisher(event)`
  外发（事件总线挂接留装配批）；publisher 异常不阻断登记（留痕）。

## 2. 接口

```python
DDL 常量: REF_INDUSTRY_DDL / REF_INDEX_CONSTITUENT_DDL / REF_ID_MAPPING_DDL（SQLite）
@dataclass(frozen=True) IndustryRecord: symbol/gics/sw/source/updated_at
@dataclass(frozen=True) IndexConstituent: index_code/symbol/effective_date/removed_date
@dataclass(frozen=True) IdMapping: symbol/minqmt/tushare/akshare
@dataclass(frozen=True) RefChangeEvent: kind/payload/occurred_at
class ReferenceDataManager(event_publisher=None):
    upsert_industry / industry_of / set_index_constituent / remove_index_constituent
    constituents_at / register_mapping / map_id / change_events
```

## 3. 不变量

- 判定核心纯内存无 IO；event_publisher 注入式。
- 指数成分 PIT：同 (index_code, symbol) 多段 effective_date 共存，
  constituents_at 确定性取 as_of 时点有效段。
- ID 映射单向翻译确定性：同输入必同输出；缺失返回 None 不抛。

## 4. 依赖

- instrument_master（设计边：最小字段集锚复用，不 import）
- MOD-INF-016 event_bus（设计边：变更事件发布通道装配位）

## 5. MVP 边界

- SQLite 物理建表/读写、event_publisher 接 event_bus、akshare 申万行业+
  指数成分采集接线留运行时装配批；本模块交付 DDL 常量 + 登记/查询/事件
  判定核心。
