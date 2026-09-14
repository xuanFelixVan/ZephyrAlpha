---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成（1 条，逐条摘录）**
> - L47: - 禁令：禁 --no-verify/--allow-multi-domain/裸 git；失败 3 轮挂起写交接包（`.runtime/handoffs/handoff_<sid>.json`）等 Owner
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 1 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 实时新闻+产业链→盘中决策：后端接线施工指令（交接线会话执行）

> **签发**：TDM 后端负责人会话 st-tdmbe-20260909，Owner 2026-09-09 晚裁定分工——**接线施工归你（接线会话），地图入图归增长轨（st-tdmbe），模块施工归施工轨**。
> **目标一句话**：把"实时新闻 + 产业链图谱 → 盘中交易决策"这条链的后端管道接通，交付给地图入图。
> **真源参考**：`sop/industry_chain_data_audit_sop.md`（图谱侧）+ 本指令（接线侧）。

## §0 职责边界（先读，防撞车）

| 你做 | 你不做 |
|---|---|
| 产业链图谱服务化查询、新闻事件→图谱传导器、冲击标的生成、盘中消费端点、DS-* 数据资产登记 | **禁碰 `config/trading_decision_map.yaml`**（入图由增长轨统一落，你交付节点规格即可）；禁碰今晚施工轨域包（signal_ashare/regime/position/plan_engine/ex_sor 的在改文件）；禁碰 validation 四件套、前端三件套、chainmap |

## §1 现状零件盘点（动手前先逐个反查，能复用不重建）

| 零件 | 已有代码 | 反查确认点 |
|---|---|---|
| 产业链图谱 | 你的长城任务成果（ig_* 表/引擎 18196→3 收敛/全球链/股权表） | 是否已有服务化查询接口（非 CLI）？ |
| 新闻采集 | alt_data/social_sentiment_collector + research_report_collector + web_scraper_engine | 实时性够吗（盘中分钟级 vs 盘后批量）？ |
| 新闻情绪/NLP | intelligence/news_sentiment_analyzer + news_symbol_linker + nlp/news_dual_tagger + news_impact_grader | 实体链接到个股已有；**链接到产业链节点有没有？**（预期=没有，这是 W3） |
| 事件评分 | intelligence/event_score + event_factor_matrix + event_causal_reasoner | 输出格式能否直接喂传导器 |
| 盘中情绪管道 | data/intraday_sentiment_loop | 与新闻流的汇合点在哪 |

## §2 接线施工清单（P0→P2，按序）

| # | 任务 | 落点建议（先反查） | 验收口径 |
|---|---|---|---|
| W1 | 图谱查询服务化：产业链子图查询（节点/上下游/股权）封装只读服务接口 | scripts/industry_graph/ 现有引擎包装，或 src/zephyr/industry_graph?（先反查归属域） | 一条查询：<产业节点>→上下游 N 跳+受影响标的清单，毫秒级返回 |
| W2 | 新闻实时性核对+补齐：确认盘中新闻流延迟；不足则接实时源（复用 alt_data connector 体系） | alt_data/ | 从新闻发布到入库 ≤N 分钟（N 由你实测后定并披露） |
| W3 | **事件→产业链传导器**（核心新件）：新闻实体/事件词 → 产业链节点匹配（复用 news_symbol_linker 思路升维到图谱节点） | 建议落 intelligence/ 或图谱域包（反查后定） | 一条真实新闻→命中产业链节点+置信度；测试含未命中/歧义路径 |
| W4 | **冲击标的生成器**：图谱节点受冲击→上下游扩散→受影响标的/板块清单+冲击方向（利好/利空/中性） | 同 W3 域 | N 跳扩散+方向判定；与 event_score 融合口径写明 |
| W5 | 盘中消费端点（只读）：给偏离监控/盘中扫描/负面否决供"事件冲击流" | 复用 api_server 只读端点惯例或 EventBus 主题（你选型后写明） | 端到端 dry-run：一条真实新闻→传导→标的清单→消费端可见 |
| W6 | DS-* 登记：新数据流全部入 data_asset_registry（事件冲击流/图谱快照） | data_asset_registry.yaml | datainfo 页可见 |

## §3 入图交接协议（你↔增长轨）

每个交付物（W3/W4/W5）附一份**节点规格卡**：建议 node_id/name_zh/decision_question（≤100 字）/algo_note 大白话/data_refs（DS-*/DS 新登记号）/module_ref（你的实现路径+MOD-ID）/拟挂母节点（L1-S0、L2-09、L3-04、L0-02）。交给增长轨（st-tdmbe），**由增长轨按四道前置检查统一落图**——你不开图。

## §4 验收与纪律

- 循环验收 2 轮 0 错误；每模块 tests 配套；红蓝对抗 ≥3 手法（边界/故障/前视）留痕
- 提交走网关（`git_commit.py --session <你的sid> --files 逐一列出 --allow-overlap`）；改完 30 分钟内提交
- **暂存区预警**：已知 sess-26548 + worker-69d94 两活会话占着共享暂存区，被拦就按 66 号排队（≥5 分钟间隔），禁清别人 staged
- 禁令：禁 --no-verify/--allow-multi-domain/裸 git；失败 3 轮挂起写交接包（`.runtime/handoffs/handoff_<sid>.json`）等 Owner
