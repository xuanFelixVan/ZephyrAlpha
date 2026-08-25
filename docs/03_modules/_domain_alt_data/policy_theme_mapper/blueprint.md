---
blueprint_id: MOD-ALT-005
module_name: policy_theme_mapper
domain: D_ALT_DATA
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_ALT_DATA
path: src/zephyr/alt_data/policy_theme_mapper.py
granularity: file
---

# MOD-ALT-005 policy_theme_mapper 蓝图（政策主题映射器 / D-ALT-19）

> **module_id**: MOD-ALT-005 | **域**: D_ALT_DATA | **优先级**: P1
> **来源**: B1-00123（AUD-DRAFT-001-DIGEST P1 波 W-P1-14，§功能域模块·D-ALT-DATA）
> 代码：`src/zephyr/alt_data/policy_theme_mapper.py`

## 0. 定位

**政策主题→行业/标的映射与政策影响持续度评估**：政策主题库（货币/产业/
监管/财政/贸易等）+ 规则关键词主题归类（可选 llm_classifier 注入升级，
输出非法回落规则留痕）+ 主题→申万行业映射表（受益/受损）+ 影响半衰期
参数 → 主题热度（时间衰减加总）与受益/受损清单，输出入信号。仅信号输入
语义，无下单含义。

查重分工（W-P1-14 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| news_impact_grader | MOD-NLP-IMPACT-001 | 单新闻 A/B/C **影响分级**（政策关键词命中即 A 级）+热点聚类计数 | 分级/计数面；无主题→行业映射与半衰期衰减 |
| sector_fund_flow_collector | MOD-L00-004 | 板块资金流**采集** | 采集面；不涉政策主题 |
| api_llm_pool | MOD-INT-API-LLM-POOL | LLM provider 池化治理 | LLM 能力经 llm_classifier 注入消费，零密钥零直连 |

不做什么：不做单新闻影响分级（MOD-NLP-IMPACT-001 职责）、不采集新闻
（data 域采集族职责）、不直连 LLM（llm_classifier 注入委托）、不做板块
资金流（采集面分工）。

## 1. 判定规则（确定性，纯函数）

`map_theme(items, as_of) -> PolicyThemeReport`：
- 输入 `PolicyNewsItem(news_id, title, text, publish_date, source)`：单条
  校验 Fail-Closed 到条（news_id/title 空白、publish_date 非法、
  publish_date > as_of → rejected 留痕，PIT 严格）；
- 主题归类：内置 DEFAULT_THEME_LIBRARY（theme_id→关键词组/半衰期天数/
  受益行业/受损行业；按库定义优先序首中即定）；无命中 → theme_id=None
  （unmatched 计数，不进热度）；llm_classifier 注入时其输出结构/值域非法
  （未知主题/方向缺）→ 回落规则并 llm_invalid 留痕；classifier 字段如实
  记录 rule|llm；
- 主题热度：age_days = (as_of − publish_date).days；weight =
  0.5 ** (age_days / half_life_days)；theme_heat = Σ weight（按 theme_id
  加总）；news_count 如实；
- 受益/受损清单：主题受益行业 heat 加总 / 受损行业 heat 加总，按 heat
  降序（同值按行业名字典序，确定性）；
- 输出 ThemeHeat(theme_id/heat/news_count/beneficiary_industries/
  damaged_industries) 按 heat 降序 + 行业级受益/受损清单。

## 2. 接口

```python
@dataclass(frozen=True) PolicyTheme: theme_id/keywords/half_life_days/
    beneficiary_industries/damaged_industries
@dataclass(frozen=True) PolicyNewsItem: news_id/title/text/publish_date/source
@dataclass(frozen=True) ThemeHeat: theme_id/heat/news_count/
    beneficiary_industries/damaged_industries
@dataclass(frozen=True) PolicyThemeReport: items_in/accepted/rejected/unmatched/
    themes/beneficiary_list/damaged_list/llm_invalid/errors
class PolicyThemeMapper(theme_library=None, llm_classifier=None):
    .map_theme(items, as_of) / .classify_one(item)
class InvalidPolicyNewsError / InvalidPolicyThemeConfigError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO（llm_classifier 注入，单测不触网）；
- 单条非法 Fail-Closed 到条（rejected 留痕）；PIT 严格（publish_date
  ≤ as_of，未来新闻 rejected）；
- 热度恒 ≥ 0；age_days=0 时 weight=1.0；主题库校验（theme_id 唯一/
  关键词非空/half_life_days 正）构造期 Fail-Closed；
- LLM 输出非法必回落规则并留痕，不出伪 LLM 结论；
- frozen dataclass asdict JSON 可序列化；同输入必同输出；仅信号输入语义。

## 4. 依赖

- MOD-NLP-IMPACT-001 news_impact_grader（设计边：单新闻影响分级分工）
- MOD-L00-004 sector_fund_flow_collector（设计边：板块资金流采集面分工）
- MOD-INT-API-LLM-POOL api_llm_pool（设计边：LLM 能力委托面）

## 5. 测试

`tests/alt_data/test_policy_theme_mapper.py`：主题归类（各主题命中/优先序/
无命中 unmatched）、热度半衰期（age=0→1.0/age=half_life→0.5/加总）、
受益受损清单（加总/降序/同值字典序）、LLM 路径（合法采纳/非法回落留痕）、
PIT 未来新闻拒绝、单条/配置 Fail-Closed、确定性、frozen。
