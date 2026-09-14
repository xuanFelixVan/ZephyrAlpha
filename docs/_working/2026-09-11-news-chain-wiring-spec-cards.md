---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：设计/计划类且无落地证据，保守保留。处置=**保留**。**
>
> **✅ 已完成（1 条，摘录）**
> - L134: - **现象**：`/api/chainmap-search` 任何查询 100% 报错 `字段关联 "name" 是不明确的`——前端搜索框完全不可用（st-igfe 收官批次之后回归）。
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 7 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 实时新闻+产业链→盘中决策：后端接线交付包（wiring-news-ig-001）

> **签发**：接线会话 wiring-news-ig-001（2026-09-11 深夜批）
> **接收**：TDM 增长轨（st-tdmbe）——按四道前置检查统一落图，本会话不开图
> **真源**：`docs/_working/2026-09-09-news-industry-wiring-directive.md`（W1-W6）
> **交付状态**：W1 复用实证 / W2 实测定案 / W3-W5 代码+tests 落地 / W6 DS-224/225 已登记

---

## §0 一句话给增长轨

W3/W4/W5 三个模块全部落码并过验收（55 单测+红蓝 9 手法），depgraph 设计态已挂合规 id
（MOD-INT_NEWS_CHAIN / MOD-INT_CHAIN_IMPACT / MOD-INT_IMPACT_STREAM，node_id
12555281/82/83 + import_depends 边×3），**就等你把下面三张规格卡落进
`config/trading_decision_map.yaml` 的预留坑位**（module_ref=null 的两个 + 一个新端点说明）。

---

## §1 节点规格卡（§3 入图交接协议格式）

### 卡 1：事件图谱传导（W3 → 预留节点 TDM-E-L2-09-1）

```yaml
建议挂载: TDM-E-L2-09-1（事件图谱传导，现 module_ref=null）
node_id: TDM-E-L2-09-1            # 沿用现坑位，不新造
name_zh: 事件图谱传导
decision_question: "这条新闻在说产业链上哪个环节？把握多大？"   # ≤100字
algo_note_zh: >
  拿到一条新闻，先在产业链图谱的环节名里找它提到的词（比如"光伏""光刻胶"）。
  找词有三个规矩：合并掉的死环节（名字带"已并入"的墓碑）不认；一个词对应太多环节
  （超过 8 个，像"行业聚合"这种滚总词）不认；英文短词要整词认（"IPO"里的"IP"不算）。
  命中几个环节就报几个，同一名字在多条链都有的标"歧义"，把握度打七到九折。
data_refs:
  - DS-224（governance.ig_industry_graph，ig_* 四表族）
  - DS-225（intelligence.chain_impact_stream，下游流载体）
module_ref: src/zephyr/intelligence/news_chain_node_linker.py::ChainNodeLinker（MOD-INT_NEWS_CHAIN）
拟挂母节点: L1-S0（情绪/新闻感知层）；上游真锚=TDM-E-L1-S0-1（MOD-INT-AISA，已挂）
input: 新闻 title+content 文本
output: tuple[ChainNodeHit]（node_id/chain_id/node_name/tier/matched_term/confidence 0-1/ambiguous）
```

### 卡 2：冲击标的生成（W4 → 预留节点 TDM-E-L2-09-2）

```yaml
建议挂载: TDM-E-L2-09-2（冲击标的生成，现 module_ref=null）
node_id: TDM-E-L2-09-2            # 沿用现坑位
name_zh: 冲击标的生成
decision_question: "这个环节被新闻砸中后，买卖哪些票、方向是什么？"
algo_note_zh: >
  某个环节被新闻命中后，沿产业链上下游走两步（图谱的边是无向走的），把路上每个环节
  挂着的公司都收进来，离命中环节越近把握越大（每走一步把握乘 0.6）。方向只有三个：
  利好/利空/中性，由上游情绪分决定（正负 0.15 之间算中性不报），整条链同向传导——
  即"新闻利好上游，就当全链利好"的粗口径；成本反号传导（上游涨价利空下游）这类
  细分留到事件类型打标之后再说。同一家公司从多个环节被够到时只报把握最大的一条，
  并记"几个环节够到它"作为共振观察位。
data_refs:
  - DS-224（ig_edge 1378 边 + ig_node_company 16900 行 PIT 有效行）
module_ref: src/zephyr/intelligence/chain_impact_resolver.py::ChainImpactResolver（MOD-INT_CHAIN_IMPACT）
拟挂母节点: L2-09（事件传导层）
input: tuple[ChainNodeHit]（卡 1 产出）+ polarity∈[-1,1]（L1-S0-1 情绪 polarity，
       或 event_score surprise_direction——两者同口径直喂，融合口径已写死在 INVARIANTS）
output: tuple[ImpactTarget]（symbol/hop/path 传导链/direction ±1,0/confidence/role/sources）
```

### 卡 3：盘中事件冲击流端点（W5 → 建议在 L2-09 下游消费面注记，不新造节点）

```yaml
建议挂载: 不新造节点——作为 TDM-E-L2-09-1/2 的落地载体注记（payload 透出通道）
端点: GET /api/chain-impact-stream?minutes=30&min_confidence=0.0   （api_server:8890，只读拉式）
name_zh: 盘中事件冲击流
decision_question: "此刻盘内正在发酵什么事件？影响哪些票？"
algo_note_zh: >
  盘中每隔几分钟拉一次这个接口，它自动取最近 N 分钟新闻（实测入库延迟中位数 6 分钟、
  九成在 13 分钟内），跑完"情绪打分→找环节→列公司"全套，返回按把握排序的标的清单。
  任何一环坏了会如实标 degraded 并留错误记录，不吐假数据。选型说明：消费方
  （偏离监控/盘中扫描/负面否决）都是拉式场景，EventBus 推式要常驻订阅者，MVP 不合算。
module_ref: src/zephyr/intelligence/chain_impact_stream.py::ChainImpactStream（MOD-INT_IMPACT_STREAM）
        + src/zephyr/frontend/dashboard/api_server.py::chain_impact_stream_endpoint
data_refs: [DS-225]
payload: {ok, window, news_count, matched_count, items[](含新闻+hits+targets), all_targets[](聚合去重),
          vocab_size, graph_size, latency_ms, degraded, errors[]}
```

---

## §2 W1/W2 核对结论（指令 §1 反查收口）

| 项 | 结论 | 证据 |
|---|---|---|
| W1 图谱服务化 | **不用新建**——api_server 既有 cm_* 通道（`_cm_pg()`→depgraph PG 只读 + /api/chainmap-galaxy/cluster/node/search/company 全套）已覆盖"节点/上下游/股权"查询，chainmap 前端在用 | api_server.py L2434-3500；本会话端点同通道复用 `get_depgraph_pg_connection` |
| W2 新闻实时性 | **分钟级增量已存在**——tasks.yaml `news_data_incremental/news_cls_incremental/news_eastmoney_incremental` 全部 event_driven 多源（rss 12 源+财联社电报+东财 7x24），实测发布→入库 **p50≈6.07min / p90≈12.58min**（300s flush buffer 为地板）；盘中覆盖无空窗（36 个 10min 桶仅收盘桶 1 个 <3 条） | CH 实测 2026-09-10 盘中 542 条样本 crawl_time-publish_time |

## §3 端到端 dry-run 实证（2026-09-11 02:37，24h 窗 800 条新闻）

```
新闻 800 → 图谱命中 10（词表 788 活词/活节点 1103/链 635 active）→ 5.5s
样例：
  "现货白银大跌5%"              [-0.20] → 白银 → 300697.SZ 利空 hop0
  "'医药一哥'1类重磅创新药获批"  [-0.20] → 创新药(歧义×2) → 000963/002755/300158... 利空
  "光伏史上最大硅料并购案"       [+0.20] → 光伏 → 000591/300724/300751/688223... 利好
  "半导体零部件供应商订单+80%"   [+0.20] → 零部件 → 002241/002475 利好（含 AAPL.US hop2 扩散）
端点冒烟（TestClient in-process）：/api/chain-impact-stream 200；minutes 越界 422；
  240min 窗 183 新闻→2 命中→300697.SZ 利空透出 ✓
```

## §4 验收与纪律留痕

- tests：`tests/intelligence/test_news_chain_node_linker.py`(22) + `test_chain_impact_resolver.py`(23) + `test_chain_impact_stream.py`(10) = **55 全过，终态代码 3 连跑 0 错**
- 红蓝对抗 9+ 手法：边界（空白文本/子串攻击/环形图/菱形路径/max_hops=0/墓碑隔离）、故障（PG 不可达 fail-closed 上抛、CH 故障 fail-open 降级、单条异常不炸批）、前视（畸形词表注入、超界 polarity、脏数据 conf>1 截断、ASCII 拆词 "IP"⊂"IPO"/"AIPC"⊂"AIPCB"——dry-run 实证回归）
- depgraph：设计态三节点 12555281/82/83（MOD-INT_NEWS_CHAIN/MOD-INT_CHAIN_IMPACT/MOD-INT_IMPACT_STREAM，全过裁定#208 正则）+ import_depends 边 17375505-07；**旧连字符 id 设计节点（12545924-26）已删除重登**（裁定#214 BLUEPRINT-FORMAT 实证）
- W6：DS-224（ig_* 图谱底座，postgres_table 型首例）+ DS-225（盘中事件冲击流）已登记；entry_counts 同步 224/87
- 禁令遵守：未碰 trading_decision_map.yaml / validation 四件套 / 前端三件套 / 他会话在途文件

## §5 已知边界（大白话，不藏着）

1. **方向是粗口径**：全链同向传导，"上游涨价利空下游"这种反号没做（需要事件类型细分，涨价/降价/断供/扩产各不同）——写了 INVARIANTS 里，不是忘了。
2. **歧义命中全量产出**："晶圆制造"四条链都有，全部报出+标歧义，不做链级消歧（需要上下文模型）。
3. **"长城汽车回购"会命中"汽车"环节节点**：环节级链接与标的级链接（既有 news_symbol_linker）互补，前者管板块联动、后者管个股——消费端两个都接就全。
4. **标的含 AAPL.US 等非 A 股**：ig_node_company 本身含全球链映射，消费端按 market 过滤即可。
5. **无蓝图 md**：三模块 [BLUEPRINT] 均标"待统筹登记"（对标 intraday_sentiment_loop 先例），蓝图补画归施工轨。
6. **提交排队**：A 批（src 三件）因 st-perf-plan-20260910 门禁批占共享暂存区反复被其文件触发的硬闸拦（VOCAB-HARDCODE/MANUAL-ONLY-PERMANENT，均系其文件非本批），按 66 号排队 ≥5 分钟间隔重试中；交接包 `.runtime/handoffs/handoff_wiring-news-ig-001.json` 同步留痕。


---

## §6 深夜批追加（2026-09-11 04:4x，循环核查发现与修复）

### 6.1 修复：chainmap 前端搜索框全坏（api_server.py SQL 裸列名）

- **现象**：`/api/chainmap-search` 任何查询 100% 报错 `字段关联 "name" 是不明确的`——前端搜索框完全不可用（st-igfe 收官批次之后回归）。
- **根因**：`chainmap_search` 的 ig_node JOIN ig_chain 查询里 `AND name NOT LIKE '（已并入…'` 未写表前缀，两表同名列歧义，PG 4 错误。
- **修复**：`n.name NOT LIKE`（api_server.py L2845，全类扫过仅此一处裸列名）；8890 已重启上线，前端实测搜索恢复（光伏 7 链 7 节点/晶圆 10 条带链归属）。

### 6.2 服务重启三项（凌晨死窗执行，同命令重启）

| 服务 | 端口 | 结果 |
|---|---|---|
| api_server（uvicorn） | 8890 | ✅ search 修复+`/api/chain-impact-stream` 新端点上线（137ms 实测） |
| Panel 仪表盘 | 5006 | ✅ 14 Tab 渲染正常（注意：必须带 `--allow-websocket-origin 127.0.0.1:5006 --allow-websocket-origin localhost:5006`，否则页面壳在、websocket 403 全空——首启踩坑已修） |
| web 静态壳 | 8899 | ✅ `python -m http.server 8899`（web/ 目录），产业地图入口 |

### 6.3 浏览器级验收（IAB 实测截图）

- 产业地图三层全通：星系（44 族 3D 星云，"44 族·599 链·8645 公司"口径行与 DB active=599 一致）→ 搜索（晶圆→10 条环节+链归属）→ 链层甬道（半导体行业 30 链 113 环节全量绘制、聚焦高亮、真源标注、股权/职能徽章图例）。
- Panel 主仪表盘 14 Tab 正常（图谱语料 Tab 在列）。

### 6.4 数据正确性：DS-224 快照已钉时点

图谱正被他会话活跃施工（02:10→04:4x：链 830→839/active 635→599/公司映射 16900→11158 行，S24 治理批在跑）。DS-224 format_summary 已改为**"活跃施工期，计数以实时查询为准"+双时点快照对账**，防止未来误引快照数。前端显示与 DB 实时一致（599=599 ✓）。

### 6.5 结构性风险登记（增长轨转 #ARCH 立项候选，本会话不抢注）

**workspace_hygiene_reconciler（priority=890）会 git restore 误判文件**：他会话每次 commit 事件触发，本会话三个 src 模块的模块 id 头曾被打回索引旧版（04:04 事件）。防御姿势=**编辑后立即 git add 同步索引**（restore 取索引版，同步后 restore 无害）。多会话并发期所有在途编辑者应遵守"改完即 add"。已按 RULE-WORKSPACE-WIP 判读器口径处置，未动他会话任何 staged。
