---
blueprint_id: MOD-INT-NEWS-LINK
module_id: MOD-INT-NEWS-LINK
module_name: news_symbol_linker
domain: D_INTELLIGENCE
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-INT-NEWS-LINK news_symbol_linker 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：92号清单 §8.4 M3-② + 44号备忘 §4 表 M3-② 行 + tracker #139（symbol 级舆情标的关联；26号备忘 §2.7 情绪作事件信号维度非独立 alpha）。
> 代码：`src/zephyr/intelligence/news_symbol_linker.py`

## 0. 定位

新闻/公告→标的关联层 MVP（规则法）——tracker #139 闭环。消费方：nightly_sentiment_window（夜间情绪聚合标的关联）；MOD-SIG-002 信号生成器（后续波次，tracker #139 CTR-INT-AISA 契约对齐候选）。

## 1. 接口

```python
class NewsSymbolLinker:
    def __init__(self, entries: Iterable[tuple[str, str]] = ())  # (symbol, name) 词表注入；畸形条目抛错
    @classmethod
    def from_ch(cls, ...)               # stock_basic 最新快照加载（当前可交易 universe 口径）
    def link(
        self, news_id: str, title: str, content: str = "", *,
        related_symbol: str = "", related_symbols: Iterable[str] = (),
    ) -> SymbolLinkage
    def link_df(self, df, title_col="title", content_col="content", news_id_col="news_id") -> list[SymbolLinkage]
```

工具函数：`normalize_text`（全角 ASCII→半角+去全部空白+大写）、`code_to_canonical`（6 位裸码→canonical，前缀推导交易所，与 stock_basic TRAE-082 派生规则同口径）。

## 2. 输出契约

`SymbolLinkage`（frozen dataclass slots）：news_id + symbols（canonical 形式如 600000.SH；**空元组=market 级**无标的关联）+ confidence + ambiguous（一词多标的=True，symbols 含全部候选）。

置信度档位（规则法 MVP 语义）：

| 路径 | confidence |
|---|---|
| 公告 related_symbol(s) 字段非空直用（源已标注标的） | 1.0 |
| 6 位代码显式命中词表（幻影码不关联） | 0.95 |
| 简称精确匹配唯一标的 | 0.9 |
| 一词多标的歧义关联 | 0.6 |
| 无关联→market 级 | 0.0 |

关联规则：① 6 位代码显式匹配（边界防子串误伤：前后不得再跟数字）；② 简称归一化精确子串匹配（最长匹配优先，短名被长名包含则剔除）；③ 歧义关联全部候选+ambiguous=True；④ 零命中→symbols=() 由下游按市场级情绪处理。

## 3. 不变量（头注 INVARIANTS 原文）

- 公告 related_symbol(s) 字段非空时直用（confidence=1.0）
- 新闻走规则 MVP：6 位代码显式匹配须命中词表（幻影码不关联）+ 证券简称归一化精确子串匹配（最长匹配优先，短名被长名包含则剔除）
- 一词多标的→关联全部候选且 ambiguous=True
- 零命中→symbols=() 即 market 级
- 词表为空 fail-open 不抛（全部 market 级）
- 归一化=去全部空白（含全角空格）+ 全角 ASCII 转半角 + 大写

## 4. 降级行为

- ERROR_CONTRACT：NewsSymbolLinkerError（ZA-IT-0007）——词表条目畸形（空 symbol/空 name）时抛（fail-closed）；CH 不可达/词表为空走降级不抛（全部关联结果为 market 级）

## 5. 边界（不做）

- 不做 NER 模型抽取（MVP 规则法，26号备忘 BM-SEL-19 漏斗联动候选）
- 不写库（关联结果由调用方聚合落库）
- 不做情绪打分（属 MOD-INT-AISA 施工面）

## 6. 测试

tests/intelligence/test_news_symbol_linker.py

---

## 7. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
