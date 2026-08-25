---
blueprint_id: MOD-ALT-006
module_name: concept_factor_mapper
domain: D_ALT_DATA
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
domain_id: D_ALT_DATA
path: src/zephyr/alt_data/concept_factor_mapper.py
granularity: file
---

# MOD-ALT-006 concept_factor_mapper 蓝图（概念因子映射引擎 / 37）

> **module_id**: MOD-ALT-006 | **域**: D_ALT_DATA | **优先级**: P1
> **来源**: B1-00596（AUD-DRAFT-001-DIGEST P1 波 W-P1-14，§1 子模块清单 37）
> 代码：`src/zephyr/alt_data/concept_factor_mapper.py`

## 0. 定位

**股票↔概念统一映射入口**：股票→概念映射字典 + 逆向索引（概念→成分）+
质量校验（成分数合理性/更新及时性）+ 映射变更 PIT 记录（effective_date
版本化 asof 查询）+ Excel 分号概念字段解析兼容层（全角；/半角; 混用），
输出供 signal_ashare 与板块因子（86，sector_factor_manager 预留的
attach_constituent_map 挂接位）消费。

查重分工（W-P1-14 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| akshare_provider | MOD-L00-004 | 概念板块/成分**采集**（market_concept_board 系列表，tasks.yaml 已接线） | 采集面；本件消费其行产物建索引不重复采集 |
| sector_factor_manager | MOD-L00-004 | 板块覆盖校验/轮动因子化/质量评分；`attach_constituent_map` 注入位 | 其 docstring 明示"37 概念因子映射引擎产出位的挂接点"——本件即该产出位 |
| sector_ranking_engine | MOD-L00-004 | 板块排名 | 排名面；不涉个股↔概念映射 |

不做什么：不采集概念成分（akshare_provider 职责）、不做板块轮动因子
（sector_factor_manager 职责）、不触网不触库（行数据全部注入）。

## 1. 判定规则（确定性，纯函数）

- `parse_excel_field(field)`：Excel 分号概念字段兼容层——全角；/半角; 混用
  统一切分，strip+去空白项+保序去重 → tuple[str, ...]；None/非 str/全空白
  → ()；
- `build(rows)`：ConceptConstituentRow(symbol/concept/effective_date) 单条
  校验 Fail-Closed 到条（symbol/concept 空白、日期非法→rejected 留痕）；
  按 (symbol, concept, effective_date) 去重 → ConceptMappingIndex：
  symbol_to_concepts（保序去重按 concept 字典序）+ concept_to_symbols
  逆向索引（symbol 字典序）+ latest_effective_date；
- `check_quality(index, as_of, config)`：成分数 < min_constituents →
  EMPTY_CONCEPT；> max_constituents → OVERSIZED_CONCEPT；
  latest_effective_date 距 as_of > stale_days → STALE_MAPPING；issues 按
  (kind, concept) 字典序确定性输出；
- `asof(versions, date)`：MappingVersion(effective_date, index) 序列中
  取 effective_date ≤ date 的最新版本（PIT）；无 → None。

## 2. 接口

```python
@dataclass(frozen=True) ConceptConstituentRow: symbol/concept/effective_date
@dataclass(frozen=True) ConceptMappingIndex: symbol_to_concepts/
    concept_to_symbols/row_count/latest_effective_date
@dataclass(frozen=True) MappingVersion: effective_date/index
@dataclass(frozen=True) QualityIssue: kind/concept/detail
@dataclass(frozen=True) QualityReport: issues/empty_count/oversized_count/
    stale/concept_count/symbol_count
class ConceptFactorMapper(config=None):
    .parse_excel_field(field) / .build(rows) / .check_quality(index, as_of)
    / .asof(versions, date)
class ConceptMapperConfig: min_constituents=2/max_constituents=2000/stale_days=30
class InvalidConceptRowError / InvalidConceptMapperConfigError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO（行/版本全部注入，单测不触网不触库）；
- 单条非法 Fail-Closed 到条（rejected 留痕）；配置非法构造期 Fail-Closed；
- PIT 严格（asof 仅取 effective_date ≤ 查询日的最新版本）；
- 索引确定性：concept/symbol 均字典序；同输入必同输出；
- frozen dataclass asdict JSON 可序列化；仅映射数据语义，无下单含义。

## 4. 依赖

- MOD-L00-004 akshare_provider（设计边：概念板块/成分采集产物来源面）
- MOD-L00-004 sector_factor_manager（设计边：attach_constituent_map 挂接位——本件即其预留的 37 引擎产出位）
- MOD-L00-004 sector_ranking_engine（设计边：板块排名面分工）

## 5. 测试

`tests/alt_data/test_concept_factor_mapper.py`：Excel 字段解析（全角/半角/
混用/空白/None/保序去重）、索引构建（双向/字典序/去重/拒绝留痕）、
质量校验（成分过少/过多/过期/边界恰等不命中）、asof PIT（取≤查询日最新/
无版本→None/未来版本不取）、配置 Fail-Closed、确定性、frozen。
