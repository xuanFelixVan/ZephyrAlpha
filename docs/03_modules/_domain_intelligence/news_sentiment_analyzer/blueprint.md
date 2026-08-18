---
module_id: MOD-INT-AISA
title: "AI 舆情分析器蓝图 — 规则法情绪打分桩+窗口聚合+事件信号（MVP）"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
design_maturity: production
layer: L02_intelligence
layer_name: intelligence
functional_domain: intelligence
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-18"
last_updated: "2026-08-18"
priority: P1
blueprint_level: module
---

# MOD-INT-AISA | News Sentiment Analyzer AI 舆情分析器

> **域**: D_INTELLIGENCE | **层**: L2 非结构化数据 | **优先级**: P1 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: design（MVP 已施工，planned→production 流转待 merge 回 dev） | **版本**: 0.1.0 | **SSoT**: depgraph MOD-INT-AISA

## 1. 模块定位

舆情分数信号生产方——对新闻/公告文本做情绪打分与时间窗聚合，产出结构化舆情分数与事件信号，辅助 A 股政策驱动行情判断（候选转正：CAND-AISA-001，P1）。

数据流：`fund_news_data`（多源新闻主表）→ 逐条情绪打分 → 时间窗聚合 sentiment_index → 突破阈值产 SentimentEvent → 下游信号生成（MOD-SIG-002，拟定）。

依据: CAND-AISA-001（candidate_module_registry）+ 26_event_driven_strategy_detail.md §舆情（复用已建 news_data+NLP 管道裁定）

## 2. 不变量 (INVARIANTS)

- **复用不重建**：数据接入复用 MOD-DATA-NEWS-001 news_collector；LLM 打分复用 MOD-NLP-INFERENCE-001（扩展口注入），本模块不新建数据源/推理引擎
- **LLM 契约取 polarity**：LLM 通道取 `SentimentResult.polarity`（有向极性 [-1,1]），禁止误用 `score`（强度 [0,1]，neutral=0.5 会把中性伪装成 +0.5 正向）——GLM 复审 P0-1
- **ST 词边界匹配**：ST/*ST 风险警示按大小写敏感+词边界匹配（仅大写是 A 股标记，小写 st 是英文普通词子串 steady/boost/first/best）——GLM 复审 P0-2
- **反转语境先扣除**：终止/停止/暂停+距离窗口 12 字内的 重组/并购/收购，及 X失败 后向模式——命中计负向并从文本扣除命中段，防"终止重大资产重组"被"重组"判正向——GLM 复审 P0-3
- **规则法离线可跑**：默认规则法打分桩零外部依赖（不依赖 Ollama/网络），任何环境可运行
- **极性有界**：polarity ∈ [-0.90, 0.90] 硬封顶；sentiment_index ∈ [-1, 1]
- **收词纪律**：词典不收互为子串的词（"新高"已覆盖"创新高"），防同文本双计分
- **窗口整点对齐**：聚合窗口按整点 floor 对齐，非按首条新闻时间对齐（跨日可比）
- **SCD 去重**：聚合侧按 news_id 去重（keep=first 最早版本，PIT 语义），防多版本修正稿膨胀 news_count——GLM 复审 P1-3
- **去重防刷分**：同一关键词多次出现只计一次（标题重复词不放大分数）
- **降级不阻断**：LLM 打分异常自动降级 llm_fallback（polarity=0），单条失败不阻断整体
- **事件防抖**：连续同向超阈窗口只在首个窗口触发事件，不重复告警
- **MVP 不持久化**：内存态输出，不建表；落盘由下游消费方决定（扩展口）

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| NewsSentimentAnalyzerError | ZA-IT-0003 | window_minutes≤0 / aggregate_from_df 缺 time_col 或 polarity_col |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | MOD-DATA-NEWS-001 news_collector | collect_news() → DataFrame | 数据接入（D_DATA 已建，PIT 严格） |
| 依赖 | MOD-NLP-INFERENCE-001 nlp_inference | SentimentResult（LLMSentimentScorer callable 签名） | LLM 打分扩展口，TYPE_CHECKING 引用，运行时不硬依赖 |
| 依赖 | zephyr.shared.foundation.errors | ZephyrBaseError | 错误基类 |
| 产出 | MOD-SIG-002 信号生成（拟定） | SentimentEvent / SentimentWindow | 舆情分数→信号（CTR-INT-AISA 拟定） |
| 产出 | regime overlay（#ARCH-NLP-PIPELINE-001） | 舆情分数可回溯喂 bad_news_flat 类指标 | 正交消费，非本 MVP 范围 |

## 5. 打分与聚合逻辑

```
规则法打分（RuleBasedSentimentScorer，标题命中 ±0.20/词，正文 ±0.08/词，封顶 ±0.90）:
  ① 反转语境正则（终止|停止|暂停）[≤12字，标点截断]（重组|并购|收购）
     + 后向（重组|并购|收购）（失败|告吹|未成|折戟）→ 计负向并从文本扣除命中段
  ② ST/*ST：大小写敏感词边界正则 → 计负向（小写 st 英文子串不命中）
  ③ 短词典子串匹配（正 34 词 / 负 35 词，同词去重）

窗口聚合（SentimentAggregator）:
  按 time_col 整点 floor 对齐，窗口=60min（可配）
  聚合侧按 news_id 去重（SCD 多版本防膨胀，keep=first 即最早版本）
  sentiment_index = 窗口内 polarity 均值
  positive_ratio / negative_ratio = 正/负向新闻占比

事件检出（NewsSentimentAnalyzer._detect_events）:
  sentiment_index ≥ +0.30 → positive_spike（首个窗口，连续同向防抖）
  sentiment_index ≤ −0.30 → negative_spike（同上）
```

## 6. 接口

### 输入
```python
NewsSentimentAnalyzer(
    window_minutes: int = 60,
    positive_threshold: float = 0.30,
    negative_threshold: float = -0.30,
    llm_scorer: LLMSentimentScorer | None = None,  # LLM 扩展口
)
analyzer.analyze_news_df(df) -> DataFrame          # 逐条打分（+polarity/method/keywords 列）
analyzer.analyze_date_range(start, end) -> (DataFrame, list[SentimentWindow], list[SentimentEvent])
```

### 输出
- `SentimentScore`（news_id/polarity/method/keywords，冻结 dataclass）
- `SentimentWindow`（窗口 sentiment_index/正负占比/news_count）
- `SentimentEvent`（positive_spike/negative_spike，方向+强度+触发新闻数）

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 单文件模块（非子包） | MVP 不过度工程：4 个类高内聚，~450 行；将来拆分（scorer/aggregator/store）成本低于预拆 |
| 规则法为默认、LLM 为注入扩展口 | nlp_inference 零样本 F1=0.51 未达 SFT 目标，规则法确定性高可单测；扩展口签名对齐 SentimentResult，LLM 成熟后无缝切换 |
| LLM 通道取 polarity 而非 score | SentimentResult 双字段语义：score=强度[0,1]（neutral=0.5）/ polarity=有向极性[-1,1]；误用 score 会把中性新闻伪装成正向（GLM 复审 P0-1） |
| 反转语境用距离窗口正则而非固定短语 | A 股公告"终止**重大资产**重组"中间常插修饰语，固定子串匹配不到；≤12 字窗口+标点截断是中文动宾反转的标准启发式（GLM 复审 P0-3） |
| 不建 sentiment 持久化表 | MVP 边界：26 号备忘录裁定情绪分数作事件信号维度非独立 alpha，落库需求待下游确定后再建（遗留项） |
| 窗口整点对齐 | 跨日/跨周可比性；按首条新闻对齐会导致同一事件的窗口边界漂移 |
| 关键词词典静态内置+构造注入 | MVP 静态表对齐"先简单静态映射后动态模型"偏好；自定义词典走构造参数，不读外部配置文件（防第二真源） |
| 与 MOD-SIG-025 正交不合并 | 025 是价格行为情绪周期（涨跌家数/涨跌停），本模块是新闻文本舆情，数据源与算法零重叠，合并违反单一职责 |
| 已知局限（规则法天花板） | 否定词（"承诺不减持"仍判负向）与复杂语境无法覆盖——由 LLM 通道补；词典覆盖随实盘误差分析迭代 |

## 8. 测试计划

- 冻结 dataclass 不可变（3 类）
- 规则法：正/负/中性打分、标题权重>正文、自定义词典、正负抵消、0.90 封顶、同词去重
- GLM 复审回归：ST 词边界（大写命中/小写英文零误伤）+ 反转语境（终止重组净负向/常规重组仍正向）
- 聚合器：空表、缺列报错、单窗口均值/占比、多窗口、整点对齐、window≤0 报错
- 主分析器：空表、规则法链路、LLM 注入通道（polarity 契约+neutral 防伪正）、LLM 异常降级、mock collect_news 全链路、SCD 去重
- 事件：正/负 spike 触发、连续同向防抖、阈值内不触发
- 错误契约：ZA-IT-0003

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 9.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §9（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INT-AISA`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INT-AISA` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-INT-AISA` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INT-AISA | MOD-INT-AISA | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
