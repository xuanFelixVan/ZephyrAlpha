---
module_id: MOD-SIG-160
title: "A09 财经快讯情绪源线判据转化器蓝图 — 半衰加权情绪指数×密度突增×四档判据"
doc_type: blueprint
status: Active
version: "0.1.2"
design_maturity: production
ttl: permanent
layer: L05_signal
layer_name: signal
functional_domain: ashare_signal
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-10-08"
last_updated: "2026-10-08"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-160 News Sentiment Criterion — A09 财经快讯情绪源线判据转化器 蓝图

> **module_id**: MOD-SIG-160 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L9-A09（源线·财经快讯情绪，module_ref 挂载=总裁终裁批，本班不落图）
> **出身**：全流通总包交接令 R6（st-fullflow2-20261008）；红源线首批 6 判据中 st-fg-srcline1-20261005 预登记 token 未建的最后两件之一，按 MOD-SIG-157 同构先例补建；能力反查零命中（新增能力面，2026-10-08 留审计）。

## 1. 判据语义（地图节点 decision_question 逐条对码）

节点问句：**快讯流密度与情感能否量化情绪并预测次日？** 本件把快讯流（DS-104 财联社 / DS-107 东财快讯 / RSS，时戳+情感分 ∈[-1,1]，情感分由调用方接 news_sentiment_analyzer 文本打分层产出）转为三段判据：

1. **窗口情绪指数**（sentiment_index）：右闭窗 (as_of-w, as_of] 内新近度半衰加权均值 ∈[-1,1]（快讯衰减快，新讯权重高，半衰默认 120min）；
2. **密度突增**（density_burst）：当前窗计数/前等长窗计数 ≥2.0，或前窗零基准时绝对地板 ≥5 条（防稀疏单条假突增）；
3. **情绪档**（sentiment_tier）：index ≥+0.5 → POSITIVE_SPIKE；≤-0.5 → NEGATIVE_SPIKE；|index| ≥0.2 → WATCH；其余 NONE。"预测次日"为消费方（日频策略面）落地语义，本件只量化当窗情绪态。

## 2. 关键口径（proposed，待实盘标定）

- **PIT 纪律**（A09 节点 algo_note：快讯时戳不可回填，聚合窗口须右闭）：ts > as_of 一律 fail-closed（未来泄露禁入）；右闭窗边界=恰 as_of 入窗、恰 as_of-w 出窗（红测逐点锁定）。
- **尖峰档不要求 burst**：单条重磅快讯可拉满指数；burst 由 snapshot 字段透传供消费方加权。
- **行级缺陷硬失败**：build_from_news_rows 缺 ts/score 逐行 raise（新闻缺情感分=上游打分契约漏单，静默跳过会系统性偏置指数——与 MOD-SIG-157 缺行情行跳过口径相反，语义各异有据）。
- **正交性**：news_sentiment_analyzer（intelligence 域文本打分层，单条→分）与本件（窗口流→档）问句不同不并；market_sentiment_analyzer（MOD-SIG-025 价格行为情绪）口径不同不并。

## 3. 查重分工（三重反查留痕 2026-10-08）

CapabilityLookup 系列留审计（`.runtime/lookup_audit/`）；clone_guard 同构先例对照：与 MOD-SIG-157 共享"序列→判据快照"骨架但输入域（时戳流 vs 价格序列）/加权（半衰 vs 横截面分位）/PIT 纪律（右闭窗 vs 落定不修订）全异；与 news_sentiment_analyzer 为上下游分工（打分→判据），非同层重建。

## 4. INVARIANTS（代码头部同文）

纯函数核零 IO（快讯时戳/情感分与 as_of 调用方注入）；ts>as_of fail-closed（NewsSentimentInputError）；sentiment_index ∈[-1,1] 单值输出；密度突增双条件防稀疏假突增；空窗=合法静默态记 notes 判 NONE 不编方向；同输入必同输出。

## 5. 接口

- `build_news_sentiment_snapshot(items, as_of, *, window_minutes=60, half_life_minutes=120) -> NewsSentimentSnapshot`：主入口（(时戳, 情感分) 序列；datetime/epoch 双口径）。
- `build_from_news_rows(rows, as_of, ...)`：DS 读入形态入口（timestamp/sentiment 行字典序列，行级缺陷硬失败）。
- `classify_sentiment_tier(index, burst)`：四档判定（可独立复用）。
- 输出 `NewsSentimentSnapshot.to_dict()`：json.dumps 直序列化。
- 测试：`tests/signal_ashare/source_line/test_news_sentiment_criterion.py`（红蓝 20 测：PIT 泄露必红/半衰手算对拍/右闭边界逐点/密度双条件/fault 注入）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-160`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-160` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-160` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-160 | MOD-SIG-160 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/signal_ashare/source_line/test_news_sentiment_criterion.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


