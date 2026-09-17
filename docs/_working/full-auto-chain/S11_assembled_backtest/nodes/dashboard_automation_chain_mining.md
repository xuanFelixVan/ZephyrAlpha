---
ttl: task_bound
title: T2 节点挖矿：前端仪表盘自动化链（真读路径 / 死面板 / 拍板闭环 / 静默失败面）
session: st-qoder-t1a-20260915
date: 2026-09-17
parent: S11_assembled_backtest
lane: H
---

# 节点挖矿：前端仪表盘自动化链（父环节 S11_assembled_backtest）

> 范围：Owner 每天唯一真正盯着看的部件——桌面仪表盘。挖四件事：①页面**实际**读什么（页→JS→端点→
> Python→存储的每一跳）；②52 页里哪些是活面板、哪些是静态 HTML 却挂着「真源/已接线」牌子；
> ③转正拍板闭环是否端到端自动（还是"人必须在某个没接线的地方点一下"）；④前端/API 路径上的静默失败面。
> 方法：全部结论以 `file:line` + 可复跑命令为锚。AST 级普查吞异常、集合差分证消费者数、
> 盘上 artifact（`.runtime/strategy_pipeline/last_receipt.json`、`data/backtest_artifacts/runs/*`）取证。
> 只读纪律：本节点零写 `data/`、零 DB 写、未直查 CH（全部证据取自仓内代码与已落盘产物）。
> 与既有节点的边界：`S13_frontend_approval/README.md` 记的是"施工交付清单"，本文记的是"交付物的实际可达性"，
> 二者冲突以本文为准（附命令可复核）。Grafana 那条线由 `dashboard_blueprint.md` 自认未接线，本文不重复。

## 1 现状盘点（逐条带 file:line）

### 1.1 骨架与"唯一 HTTP 通道"

| 构件 | 锚点 | 事实 |
|---|---|---|
| 壳 + 片段 | `web/core/loader.js:3` | `window.ZK_BUILD='20260915-1'`；`loadJs` 是**硬编码顺序 Promise 链**，无依赖图、无按需加载 |
| 页面清单 | `web/core/loader.js:6` | `PAGES` 实测 52 个 id；同文件 `:1` 注释仍写"fetch 47 页面片段…37 个页面引擎文件"——自描述已漂移（实测 52 页 / 69 引擎） |
| 路由 | `web/core/app1.js:14` | `GRP_OF` 注释自认："09-15 增 govm（治理操作全景，#govm hash 直达组高亮兜底）" |
| 通道 | `web/services/api.js:2` | 自称"前端↔后端唯一接触点；所有取数经此"，实测该文件导出 40 个键（含 `fetchJson` 与 3 个 SWR 工具），即 **36 个端点封装** |
| 破口 | `web/features/tdm.js:20,92,110,618`、`web/features/govm.js:14,36`、`web/features/factory/factory.js:17,111,131,625,701,719` | 三页绕过 `ZK.api`，裸 `fetch(API_BASE+...)`——"唯一通道"对 tdm/govm/factory 不成立 |
| 服务绑定 | `api_server.py:57` | `allow_origins=["*"]` + `allow_methods=["GET","POST"]`；`:4447` 绑 `127.0.0.1:8890`。CORS 全开 + 本机任意进程可 POST（见 §1.4） |

### 1.2 页面 ↔ 后端可达性普查（52 页全量，非抽样）

判定口径：该页在 `loader.js` 里挂的引擎文件是否出现 `ZK.api.<wrapper>(` 或字面 `/api/...`。

```
$ python（AST/正则，见 §2 ⑤）→ 结果
  PAGES 声明          = 52
  web/pages/*.html    = 52            # 无缺页
  features/*.js       = 69
  loadJs('features/…') = 69           # 无孤儿引擎（0 死 JS）
  index.html 导航项    = 51            # 52 页里唯一无导航入口 = govm（仅 #hash 可达）
  触达后端的页         = 14
  从未触达后端的页     = 38
```

14 个活页与端点归属（`→` = 该页引擎实际引用的端点）：
`backtest`→{`/api/strategies:553`,`/api/backtest-list:645`,`/api/backtest-detail:701`,`/api/backtest-run:916,976`,`/api/framework-plans:1062`,`/api/framework-backtest-run:1091,1170`,`/api/battle-map-flow:586`}｜
`stockq`→{`/api/kline:167`,`/api/quote:277`,`/api/position:350`,`/api/events:409`,`/api/orderbook:441`,`/api/signals:1181`,`/api/stock-header:203`,`/api/stock-search:499`}｜
`chainmap`→6 个 `/api/chainmap-*`｜`services`→{`/api/health:162`,`/api/services-status:1284`,`/api/services-control:1294`}｜
`promotion`→{`/api/promotion-advisories:4325`,`/api/promotion-decide:4348`,`/api/ops-notifications:4396`}｜
`pattern`→3 个 `/api/pattern-*`｜`warroom`→`/api/signals-overview:1230`｜`datasrc`→`/api/sources-status:1327`｜
`download`→{`/api/download-status:1681`,`/api/data-asset:2045`}｜`bridge`→`/api/bridge-status:2112`｜
`tdm`→`/api/tdm:2313`｜`factory`→`/api/factory:2595`｜`govm`→`/api/govm:2665`｜`position`→`/api/signals:1181`。

38 个"零后端"页里，**13 页仍在 HTML 上打「真源」牌子，共 38 处**（同一文件内并列 `演示数据` 徽标，但 badge 字样是"真源"）：
`overview.html:65,82,128,164,180,193,196`(7)｜`live.html:3,105,115,128,185`(5)｜`sentiment.html:3,24,49,160,167`(5)｜
`sysstatus.html:93,144,158`(3)｜`design`/`modlib`(各 3)｜`sector`(4)｜`news`(2)｜`projmap`(2)｜`rating.html:3`｜`models.html:3`｜`aichat.html:3`｜`resweek.html:13`。
其中三处是**可判伪的具体声明**：
- `models.html:3` "真源=model_registry（8 条，BFE-40）+ML 监控族（prod）"——`/api/model-registry` 一类端点在服务端 39 个清单里**不存在**，该页 0 引擎 0 端点，"8 条"无从核。
- `aichat.html:3` "真源：MOD-INT-RESEARCH-AGENT ReAct 助手（prod）"——同页 0 端点。
- `t0.html:51` 静态散文"今日信号命中率：3 命中 / 1 半命中 / 0 失手（75%）"，同行自认"当前 mock 数据渲染"——**数字写在 HTML 里，每日不变**。

诚实性分级（避免过度指控）：`overview.html:164,180`、`sysstatus.html:93`、`sentiment.html:160,167`、`review.html:184`
都挂了 `<span class="badge b-na">演示数据</span>`，且 `live.html:3`/`sentiment.html:3` 的"真源=B31/B32/B33"后面
带 **`（I-2 接线后转真）`** 标记——这是本仓自己的"待接线"暗号，属已登记欠账，不算自欺。不算的是：
- `datasrc.html:16` "alerter 真实失败汇总（data/failures/*.json 最新 8 条）——**ERROR/CRITICAL 已触达飞书**"。
  飞书/SMTP 已于 2026-09-15 裁撤（`src/zephyr/data/alerter.py:28` 明示），此句为**假**，且它挂在"真源"徽标旁边。
- `review.html:183` "推送微信/邮件（BFE-38）"——`rg -n "BFE-38" --glob '*.py' --glob '*.yaml'` → **零命中**；
  微信/邮件 sender 类确有其物（`src/zephyr/frontend/implementations/notification_channel_senders.py`），
  但其注册入口 `register_channel` 全仓仅 `default_notification_manager.py:75` 一处定义、**零生产调用点**
  （`rg -n "register_channel" src/` → 6 命中，全部是注释/文档字符串/定义本体）。该卡片区是静态 HTML，无任何 JS 引用。

### 1.3 真读路径：活链逐跳 + 一条"自产自快照"跳

以 Owner 最常看的两个端点逐跳拆开（页→JS→端点→Python→存储）：

**A. `/api/services-status`（服务总闸，Owner 唯一能"动手"的页）**
`services/sv-page.js:31` → `ZK.api.fetchServicesStatus`（`api.js:80`）→ `api_server.py:1284` →
`services_registry.get_services_status()`（`services_registry.py:33-176` 目录 + 五类探测器 heartbeat/flag/proc/task/file_fresh/env_tcp）→
无 DB，读 `tmp/` 心跳文件 + `psutil` + `schtasks`。审计写 `services_registry.py:25-27`
`_REPO/"tmp"/"services_control_log.jsonl"`。
**目录口径三处不一致（实测 = AST 数）**：`services_registry.py:29` 注释"16 项"、`api_server.py:1280` 注释"真源=…（16 启动项）"、
`api.js:80` 注释"34 启动项"，而 `SERVICE_CATALOG` 实为 **35 条**（AST `len(elts)`；tier 分布 guard 13 / external 10 / free 6 / confirm 5 / self 1；
带 `start` 命令的只有 **11 条**）。三个数字 16/34/35 没有一个互洽，"启动项"到底指全集还是可拉起子集无人定义。

**B. `/api/strategies`（回测页策略多选）**
`backtest/bt-engine.js:548-576` → `api.js` `fetchBacktestList` 族 → `api_server.py:553` →
`_strategy_rows()`（`:783`）→ `StrategyRegistry.list_all()` + `TickStrategyBase._registry`（`autodiscover` import 期填充）→
快照 `data/runtime/strategy_registry_snapshot.json`（`:750`）。
生产者核验结论与预想相反：**不是"reconciler 未触发"**。写方就是 api_server 自己——
`_save_strategy_snapshot`（`:828-837`）由 `_warm_strategy_registry`（`:854-866`）在线程 `bt-strategy-warm`（`:868`，import 期启动）里调，
且每次 `/api/strategies` 全量构建后回写（`:573`）。盘上实测该文件 `saved_at=2026-09-17T05:08:57`，8 条策略，与 `StrategyRegistry` 一致。
真正的问题在**新鲜度与标志位**：
- `_load_strategy_snapshot`（`:840-851`）只校验 schema（`modes` 键在不在），**从不校验 `saved_at` 年龄**——进程长期不重启则快照永不过期；
  快照仅在 `_warm`/全量构建成功后刷新，所以 `strategy_registry.yaml` 改生命周期后，本页要等服务重启才反映。
- 未预热完成时返回 `{"ok": True, …, "stale": True}`（`:568`、`:578`）。`rg -n "stale" web/` →
  命中仅 `pos-signal-board.js:74,87` 与 `sq-fav-list.js:118-124`（都是别的字段），**无人消费 `/api/strategies.stale`**，
  且 `bt-engine.js:573` 立刻 `swrSave('zk_btgrid_v1', …)` 把 stale 包写进 localStorage。

### 1.4 拍板闭环逐跳：管道是通的，龙头不出水

Owner 四件事之一的"策略转正批准"。链路（每跳带锚点）：

```
scripts/backtest/sim_governance.py:175  _emit_promotion_advisory_event(recs)
  :137-138  if not any(r.get("recommendation") for r in recs): return   ← 闸门
  :142      record("promotion_advisory_due", …) → :143 drain(allow_heavy=False)
pipeline_events.py:243-244              kind in OPTIONAL_DUE_KINDS → run_optional_due
  :128-132  OPTIONAL_DUE_KINDS["promotion_advisory_due"]=("…promotion_advisory","run_promotion_advisory_due")
promotion_advisory.py:522-549           run_promotion_advisory_due → :527 build_advisories()
  :492-519  build_advisories：三路证据合流；:505 hold 不产包；:510 out 非空才 mkdir
  :553-570  list_advisories：glob ADVISORY_DIR（:99 = data/strategy_intake/promotion_advisories）
api_server.py:4325-4345                 GET /api/promotion-advisories → 空则 ok:true,count:0,data:[]
web/features/promotion/promotion.js:91  if(!LIST.length) → 渲染 EMPTY_TXT(:38)
promotion.js:113-145 decide()  → POST /api/promotion-decide（api_server.py:4348-4382）
  → promotion_advisory.decide(:733-810) → _update_registry_lifecycle(:627-650) 写 strategy_registry.yaml
```

**关键实证（盘上产物，非推断）**：`.runtime/strategy_pipeline/last_receipt.json`（mtime 2026-09-17 06:18）
```json
{"processed":[{"id":"PIPE-20260917-061855-fe39b2","kind":"promotion_advisory_due",
  "result":{"event_id":"PIPE-20260917-061855-fe39b2","built":0,"advisories":[],"pushed":[]}}],
 "failed":[],"skipped":[],"stop_reason":null,"pending_left":2}
```
即：**事件今天真的跑过、真的成功了、真的产出了 0 份建议包**。"从未触发"的说法是错的；
正确诊断是"链全通、源头空"。为什么空，两路证据各自封死：
- 证据①（治理建议）：`data/backtest_artifacts/runs/SCR-SIMGOV-20260917-012204/04_wide/sim_governance_advice.json`
  全文 2 条目，`"recommendation": null` ×2（`months_evaluated` 分别 0 和 1），`why="观察期数据不足或表现中性"`。
  注：`promotion_advisory.py:129-140`（glob 在 `:131`）`_read_latest_governance` 取 `runs[-1]`，读得到，但值是 null →
  `_decide_recommendation`（`:455-464`）走兜底。
- 证据②（月度偏离判定史）：`_read_deviation_months`（`:142-163`）按 **(strategy_id, month) 去重**，
  17 份 `SCR-DEV-*/04_wide/deviation_report.json` 实测只塌缩成 **1 个键** `("STR-VREV-025","2026-08")`（`ok:true`）。
  `pass_months=1 < 2` → 兜底也判 hold。另一 sim 条目 `STR-E-TIMING-001` 偏离史为**零**。

结论：**`build_advisories` 当前恒返回 `[]`，且这是结构性不可达而非时点问题**——promote 需要 ≥2 个**不同自然月**的
`monthly_pass`（`:460`），而 `_OBSERVING_LIFECYCLES=("sim","paper")`（`:120`）里只有 2 个策略，
其月度判定由 `pipeline_events.py:400-415` `run_sim_deviation_monthly` 按 `MONTHLY_DAYS=30`（`:135`）的月频标记驱动。
最早可能出现的 promote 建议 ≈ 连续两月不断更之后（`last_audit.json` 的 `sim_deviation` 标记为 2026-09-14T22:53，
下一次窗口 ≥10-14）。因此 `ADVISORY_DIR` 至今**不存在于盘上**（`ls data/strategy_intake/promotion_advisories` →
No such file or directory；`data/strategy_intake/` 同级只有 `c4_deferrals.csv`/`grid_*` 等），
`promotion.js:38` 的 `EMPTY_TXT`"模拟盘+整装回测出成绩后自动出现在这里"是**当前真话**，
但页面同时写着"通知唯一出口=本页"（`promotion.js:8`）——那句话是假的，见 §1.5。

**写回是不是 SSOT？是。** `decide` 的落点不是 UI 状态：
- `:787` `_update_registry_lifecycle` → `:627-650` 对 `strategy_registry.yaml` 做文本手术 + `safe_write_text` CAS
  （`:640-643` 未确认写入即 `raise` fail-closed）+ `:644-648` **写后重读磁盘复核** `lifecycle_status` 真值。
- `:789-804` decision 台账 `ADV-*.decision.json`（`safe_write_text` 在 `:801`，`:804` 未确认即抛）。
- `:747-752` kill-switch fail-closed 探针；`:777-785` PA-1 四条件实据预授权（`_PreauthDenied` 拒批不落墓碑）。
这四条是本节点挖到的**真好消息**——拍板执行体不是玩具。UI 侧只有 `promotion.js:129`
在 POST 成功后本地补一个 `decided_at: new Date().toISOString()`（服务器 `receipt.decided_at` 在 `:794` 已有），
属"本地镜像多写一个字段"，不是"本地态掩盖未落库"。

**但门位本身没上锁**：`api_server.py:4373` 调 `decide(..., token=None, via="frontend")`，
`_token_check`（`:654-669`）在 `:663-664` 明确 `if provided is None: return secret, None`——**服务端自取 Owner 密钥**，
文档字符串 `:655-658` 自述理由="前端拍板=Owner 点击即授权"。叠加 `api_server.py:57` 的 `allow_origins=["*"]`，
本机任意进程 `POST /api/promotion-decide` 即完成"Owner 已授权"的语义。今天不构成实害，唯一原因是 §1.4 那个空龙头
（`:754-756` advisory 文件不存在 → `FileNotFoundError` → `api_server.py:4376-4378` 映射为 `not_found`）。
`OWNER_TOKEN_KEY` 是否已配置未实证（不读凭据存储）；若未配置则 `:661-662` 直接 deny，属第二层巧合性防线。
可判定：`SELECT` 类核验命令 = `python -m zephyr.strategy_pipeline.promotion_advisory`（CLI `:824-851`）。

### 1.5 通知出口对不上（"通知唯一出口=本页"是半假）

2026-09-15 裁定"通知以前端 promotion 页为准"（`kimi_deep_mining_charter.md:§8`、`alert_rules.yaml:30-32`、
`ops_alert_feed.py` 头注释）。promotion 页横幅的唯一数据源是 `/api/ops-notifications`（`api_server.py:4396-4410`）
→ `OpsAlertFeed.list_active()`。落这块板的**生产方**实测四类：
`ops_alert_feed.py:689,804`（规则 tick 自产）、`data/implementations/breadth_freshness_alerts.py:197-204,308`、
`infrastructure/system_telemetry/alerts/resource_schedule_alerts.py:99-118`、
`signal_ashare/strategy_signal/strategy_decay_certifier.py:230-257`（退役建议）。
**转正链路一份都不落这块板**：`promotion_advisory.py:538-546`（建议包）与 `:811-822`（拍板回执）都走
`Alerter().notify(level="ERROR")` → `alerter.py:53` `data/failures/*.json`，
而 failures 目录只被 `api_server.py:1362-1372` 读**最新 8 条**、只在 **datasrc 页**渲染（`features/datasrc/ds-page.js:49,87-88`）。
`_notify_decision` 的文档字符串 `:812` 还写着"ERROR 级触达飞书+failure 文件"（飞书已裁撤）。
后果：Owner 在裁定里被告知的"看 promotion 页就知道有没有要我拍板"，与实现"拍板相关事件只进 datasrc 页滚动窗口 8 条"
不是同一条路；一旦 failures 目录当日新增 >8 条，转正建议推送就被挤出可见区（`:1364` 取 `[:8]`，`:1372` `except Exception: continue`）。

### 1.6 死产出核验：一个端点零消费者（命令与结果内嵌）

```
# 服务端端点 vs 前端引用字符串集合差分
$ python: srv={@app.(get|post)("/api/…")}  web={web/**.{js,html} 中的 api/[a-z0-9-]+}
  srv endpoints = 39
  web endpoint strings = 39
  SERVER, ZERO WEB CONSUMER = ['/api/chain-impact-stream']
  WEB, NO EXACT SERVER MATCH = ['/api/pattern-']      # 模板字面量前缀（/api/pattern-${kind}），pattern-* 实为活

$ rg -n "chain_impact_stream|chain-impact-stream" src/ --glob "*.py"
  src/zephyr\frontend\dashboard\api_server.py:4138,4139,4147,4149      # 端点定义与惰性 import
  src/zephyr\intelligence\news_chain_node_linker.py:5                  # [CONSUMERS] 头声明
  src/zephyr\intelligence\chain_impact_resolver.py:5                   # [CONSUMERS] 头声明
  src/zephyr\intelligence\chain_impact_stream.py:2,5,14                # 自身 MODULE/CONSUMERS/TESTS
  → 9 命中，除定义处与头声明外，无任何调用方；web/ 树 0 命中（已由上一步集合差分证明）

$ rg -n "chain_impact|news_chain|ChainImpact|冲击流" \
    src/zephyr/signal_fundamental/negative_veto.py src/zephyr/plan_engine/plan_deviation_monitor.py
  rc=1（零命中）
```
被声明的消费者确实存在图上的边：`config/trading_decision_map.yaml:4392-4393`
`TDM-E-L2-09-2 --feed--> TDM-E-L3-04` / `--feed--> TDM-E-L0-02`，节点本体 `:1300-1323`
（`module_ref: src/zephyr/intelligence/chain_impact_resolver.py` `:1318`、`strategy_mounts: []` `:1321`、
`activation: continuous` `:1322`、`ai_autonomy: auto` `:1323`），`algo_note_zh:1309-1310` 逐字写着
"利空子集喂 L3-04 负面否决；冲击流喂 L0-02 盘中偏离监控"。两端消费代码零命中（rc=1）。
裁定：**图上有边、YAML 里 `ai_autonomy: auto`、代码里无人接收**——`chain_impact_stream.py:5` 的
`[CONSUMERS]` 头声明（"api_server…；TDM 预留节点…下游消费面（偏离监控/盘中扫描/负面否决）"）
后半句为假；`api_server.py:4145` 端点文档字符串"消费方=偏离监控/盘中扫描/负面否决"同样为假。
这条链的产物**今天在任何地方都看不到**（既不进前端，也不进决策）。

**次级死产出（"唯一真源"图没画全）**：`web/frontend_map.yaml`（★唯一真源，声明 `backend_ref: api:/module:/table:`）
```
$ python：正则取全部 backend_ref 值 + 全量 /api/ 字符串（含 [a, api:/x, b] 列表式）
  backend_ref 行数        = 359   其中 none:* = 300（84%）  含 module: 条目 = 23
  map 里被引用的端点      = 31 distinct
  api_server 注册端点     = 43（顶层 39 + 嵌套 4：/api/{factory/{ledger,threehigh},tdm/{validation,verdicts}}）
  map 声明但服务端不存在  = []（零虚挂）
  顶层在跑但 map 未声明   = 8 条：/api/battle-map-flow /api/chain-impact-stream
    /api/framework-backtest-run /api/framework-plans /api/health /api/ops-notifications
    /api/services-control /api/stock-search
  另有 11 个组件条目（:252-332 连续段）共享同一条 4 端点批量 backend_ref
    "api:/api/backtest-detail × /api/backtest-list × /api/backtest-run × /api/strategies"
```
即：任何以 `frontend_map.yaml` 为准的门禁/审计会得出"8 个在用端点不存在"的结论，同时 11 个
不同组件被同一串端点糊住（组件→端点映射不可用）。图不是真源，代码才是——而 §1.2 的可达性
普查只能从代码算出来。

> 更正记录（本行是本节点唯一被复算推翻的数字）：初稿写"未声明 21 条"并称
> "chainmap/pattern/tdm/factory/govm 五页全部被漏"——错因是只统计**以 `api:` 开头**的
> `backend_ref` 值，漏掉了这五页实际使用的方括号列表式 `[module:…, api:/api/tdm]`
> （见 `:388/:445/:473/:494/:2770`）。按全量 `/api/` 字符串复算＝8 条，且这五页**均已声明**。
> 嵌套 4 端点（`/api/tdm/validation` 等）经核有真消费者（`web/features/tdm.js:110,618`、
> `web/features/factory/factory.js:131,701,719`），不得混进"死端点"结论。

### 1.7 静默失败面（AST 实测，非 grep 计数）

```
$ python AST：handler 体内只含 pass/Ellipsis 且无 raise 者计为纯吞
  api_server.py         except handlers=109  纯吞=19  行号 823,836,864,1796,2972,3100,3128,3256,3736,3760,3950,3962,4119,4425,…
  services_registry.py  except handlers= 32  纯吞= 9  行号 228,288,291,345,365,378,619,811,866
  app_panel.py          except handlers=  9  纯吞= 1  行号 433
  bare_except（`except:` 无类型）= 0（三文件皆无）
```
逐条列关键面（后果一句话）：

| 锚点 | 形态 | 后果 |
|---|---|---|
| `pipeline_events.py:494-509` | `importlib.import_module` 失败 → `log.info("可选事件执行体未交付，跳过")` + 返回 `{"skipped":"module_not_ready"}`；`drain:276-281` 见成功即 `_rewrite` **出队** | 已交付模块（`promotion_advisory.py` 今天存在）内的**任何 import 期异常**被记成"实现未交付"、事件永久丢弃、只留 INFO 级日志 |
| `api_server.py:778-780` | E0 计算窗闸"装不上=放行 + warning 审计" | 闸本体 fail-closed，端点侧对"闸缺席"降级放行 → 非交易时段照样能起回测（与 `compute_window_gate` 的裁定口径相反） |
| `api_server.py:840-851` | 快照只查 schema 不查年龄 | 注册表变更后 `/api/strategies` 无限期返旧策略集，且 `stale` 无人读（§1.3B） |
| `api_server.py:823-824,836-837,850-851,864-865` | 预热/快照读写四连 `except: pass/None` | 预热线程死了没人知道，退化为"首请求等 12s 或空列表" |
| `api_server.py:1284-1292` | `/api/services-status` 无 try/except | `get_services_status` 抛即 500；前端 `api.js:175-179` SWR `catch→return null` 不覆盖渲染 → 总闸页继续显示上次缓存灯位，无红字 |
| `services_registry.py:786-814` | host 采集 `except Exception: pass`（`:811-812`）后**无条件** `return {"ok": True, …}` | psutil 任一取数炸 → `host={}` 而 `ok=True`：CPU/内存/磁盘水位全空却报"正常" |
| `services_registry.py:798` | 盘符硬编码 `("C","D","E","F")` + `disk_usage("D:\\")` 单点（`:793`） | 换机/换盘即整块 host 静默为空（与上一格同源） |
| `api_server.py:4413-4427` | 常驻 tick 线程 `except Exception: pass`（`:4425-4426`） | 通知板探针死了，promotion 页横幅永久空 |
| `api_server.py:4432-4433` | `if "pytest" not in sys.modules:` 才起线程 | 生产 uvicorn 无 pytest，正常；但**任何**在带 pytest 的进程里起的 dev server 都不发通知（隔离红线顺带的盲区） |
| `api_server.py:1327-1372` | `/api/sources-status` 失败文件仅取 `[:8]`、逐条 `except Exception: continue`（`:1372`） | 脏告警文件静默跳过；>8 条当日告警时旧痕不可见（§1.5） |
| `api_server.py:1260-1271` | `/api/signals-overview` 字符串拼接 SQL | 注入面在只读 CH admin/dashboard 角色下，风险为"越权读"而非"改库" |
| `api_server.py:4325-4345` | 建议列表任何异常 → `ok:false` + 空列表 + 200 | 后端坏了与"今天没有待审"在前端**不可区分**（`promotion.js:91` 都渲染 EMPTY_TXT） |
| `api.js:138-179` | `swrLoad/swrSave/swr` 三处 `catch(e){}` 空吞 + 无 TTL/无容量上限 | localStorage 缓存可无限期当真数据（12 个引擎在用，含 `services/sv-page.js`、`datasrc/ds-page.js`、`warroom/wr-signal-strip.js`） |
| `promotion.js:170-176` | 横幅取数 `catch → renderAlerts([])` | "通知唯一出口"取不到数据时与"无通知"同态 |
| `app_panel.py:349-355,360-361,380,404,259-296` | 绩效取不到回落 `generate_demo_performance_data()`；`symbol="demo"`；`TradePanelData()` 无源；硬编码 `sharpe=1.85, sortino=2.31…` | 旧 Panel 已 DEPRECATED（`:19-22`，2026-08-29）但**仍在 `SERVICE_CATALOG` 里作为可启动项 `panel`**（`services_registry.py:38-42`，端口 5006）：Owner 一键能起一个把演示数据当真值的面板 |

## 2 六向挖矿日志表

| 向 | 挖到的东西 | 判定 | 锚点 |
|---|---|---|---|
| ①上游（谁喂它） | 14 活页的取数全部止于 39 个只读端点 + 2 个写端点；证据链最上游是 CH 表 / `data/backtest_artifacts/runs` / `tmp/` 心跳 | 活 | `api.js:8-22`、`api_server.py:8-10` |
| ②下游（谁吃它的产出） | `/api/chain-impact-stream` 零消费者；8 个在跑顶层端点未进"唯一真源"图 | **死/半死** | §1.6 两条命令输出 |
| ③算法/机制（判定规则） | 建议词表映射自洽（`promote_paper→promote`），但 promote 硬门槛=2 个不同自然月 `monthly_pass`，当前样本 1 个月/1 策略 | 活但结构性饥饿 | `promotion_advisory.py:116,456-464`、`_read_deviation_months:142-163` + 17 份 SCR-DEV 实测 |
| ④后端（事件触发链） | `promotion_advisory_due` **今天真的执行并成功**，`built:0`；`OPTIONAL_DUE_KINDS` 走 log-and-skip 且成功即出队 | 活，但吞异常语义错 | `.runtime/strategy_pipeline/last_receipt.json`、`pipeline_events.py:128-132,494-509,276-281` |
| ⑤前端（可见性） | 52 页仅 14 页触后端；38 页零后端；38 处"真源"徽标压在 13 个零后端页上；`govm` 无导航入口；`stale` 标志零消费 | 半死（诚实标注的静态区 vs 挂"真源"的静态区） | §1.2 普查、`app1.js:14`、`api_server.py:568,578` |
| ⑥数据字段（口径漂移） | `SERVICE_CATALOG` 35 条 vs 注释 16/16/34 三口径；`loader.js:1` 注释 47 页/37 引擎 vs 实测 52/69；`app_panel.py:20` 注"41 页" | 漂移，非阻塞 | `services_registry.py:29,33-176`、`api_server.py:1280`、`api.js:80` |

未挖/不再挖（矿脉枯竭判据）：38 个静态页的**内容本身**（每页要接哪个端点属施工设计，不属挖矿）；
`design`/`projmap`/`pano` 三页的元数据来源（depgraph 生成器）已由 `modledger` 线覆盖；
Grafana/Provisioning 线由 `dashboard_blueprint.md` §4-5 自认未接线，本文不重复。

## 3 业界与开源对照

| 对照物 | 它的做法 | 本仓差距 |
|---|---|---|
| Grafana（本仓蓝图的自比对象，`dashboard_blueprint.md` MOD-INF-044） | 面板声明 = 数据源查询；面板查询失败**在面板上显示红色 error**，且 provisioning 文件即真源、可 diff | 本仓失败态与空态同构（§1.7 末两行）。"红色 error"这一件在 `promotion.js:174`、`api.js:175-179` 被主动抹平 |
| Airflow UI | DAG 每次 run 落持久化历史，UI 读 run 表；失败任务显示 try 数与日志链接 | 本仓 `.runtime/strategy_pipeline/` 只有 `last_receipt.json`（单份、覆写）+ `pending_events.jsonl`，历史不可回溯，UI 也没有 drain 履历页 |
| Streamlit / Dash | 组件即数据函数，无"静态 HTML 冒充数据面板"这一态 | 本仓 38/52 页无取数路径，靠 HTML 徽标传达可信度 |
| Backtrader/vectorbt 前端惯例 | 策略清单从注册表对象实时读 | 本仓读 `strategy_registry_snapshot.json`（进程重启才刷），且 `_load_strategy_snapshot` 不查年龄 |
| 通行做法：admin 动作二次因子 | 破坏性写操作要求带外确认（TOTP/口令/PIN） | `promotion_advisory.py:663-664` 由服务端自供 Owner 密钥；`api_server.py:57` CORS 全开 |

## 4 堵点与欠账清单（文件/函数/验收标准）

| ID | 级别 | 病灶类 | 堵点（文件/函数） | 可施工验收标准（测试可断言） |
|---|---|---|---|---|
| DASH-1 | P0 | 门位形同虚设 | `promotion_advisory._token_check:654-669` + `api_server.py:4373`（`token=None`）+ `api_server.py:57`（`allow_origins=["*"]`） | 新测试：`POST /api/promotion-decide` 不带任何凭据 → 断言 HTTP 401/403 或 `ok:false,reason:"unauthenticated"`；现有 `tests/frontend/test_promotion_advisory_api.py` 用例集合中必须存在一条"零凭据被拒"；`allow_origins` 收敛到白名单，断言 `"*"` not in CORS 配置 |
| DASH-2 | P0 | 静默失败+闭环不可达 | `pipeline_events.run_optional_due:494-509` 把 import 期异常一律判"未交付"并在 `drain:276-281` 出队 | 断言：给 `OPTIONAL_DUE_KINDS` 注入一个"模块存在但 import 抛 ImportError"的 kind，drain 后该事件仍在 `pending_events.jsonl` 且 `attempts` 自增；日志级别 ≥WARNING 且 reason=`import_failed` 与 `not_delivered` 可区分 |
| DASH-3 | P1 | 通知出口错配（裁定 vs 实现） | `promotion_advisory.py:538-546,811-822`（走 Alerter→`data/failures`）vs `api_server.py:4396-4410`（promotion 页横幅只读 OpsAlertFeed） | 断言：`build_advisories` 产出 ≥1 份 promote 包后，`OpsAlertFeed().list_active()` 非空且含 `strategy_id`；或反之——把裁定文档改为"data/failures + datasrc 页"，并让 `promotion.html` 撤销"通知唯一出口=本页"字样。二者择一，测试与文档不得并存两态 |
| DASH-4 | P1 | 死产出（零消费者） | `/api/chain-impact-stream`（`api_server.py:4138-4160`）；声明的消费者 `negative_veto.py`/`plan_deviation_monitor.py` 零引用（rc=1）；`chain_impact_stream.py:5` `[CONSUMERS]`、`data_asset_registry.yaml:9581` 同假 | 二选一：①两端各加真消费并出测试（`negative_veto` 命中利空子集 ≥1 用例）；②删端点 + 修 3 处 `[CONSUMERS]`。验收命令 `rg -o "api/[a-z0-9-]+" web/` 与服务端集合差分仍须为空集（除白名单）|
| DASH-5 | P1 | 快照新鲜度不可证 | `api_server._load_strategy_snapshot:840-851`（无年龄检查）、`:568/:578` `stale:true` 前端零消费 | 断言：`saved_at` 超阈值（建议 6h）→ `/api/strategies` 不返快照而走全量或显式 `stale`；`tests/frontend` 加一条：`bt-engine.js` 源码含 `stale` 判定，或 `swrSave` 前拒绝 `stale` 包 |
| DASH-6 | P1 | 假声明（对 Owner 说谎） | `pages/datasrc.html:16`"ERROR/CRITICAL 已触达飞书"（`alerter.py:28` 已裁撤）；`pages/review.html:183`"推送微信/邮件（BFE-38）"（BFE-38 全仓零命中）；`pages/t0.html:51` 硬编码命中率 | 门禁：新增 `web/` 文案禁词表扫描（`飞书`/`feishu`/`SMTP`/`已触达`），命中即 CI 失败；BFE-38 类标识符必须能在 `--glob '*.py'` 里解析到实现，否则同罪 |
| DASH-7 | P1 | 报"ok"的空数据 | `services_registry.py:786-814`（`except: pass` 后无条件 `ok:True`）、`:798` 盘符硬编码 | 断言：monkeypatch `psutil.cpu_percent` 抛异常 → 响应须 `ok:false` 或 `host_status:"unavailable"`；测试内不得出现字面 `D:\\`（盘符来自配置） |
| DASH-8 | P2 | 无 TTL 缓存 | `api.js:138-179`（`swrLoad/swrSave/swr`，`catch(e){}` ×3，无 TTL/配额） | 断言：缓存条目带 `ts` 且读取侧对超龄（建议 10min 交易数据 / 24h 元数据）返回未命中；`sv-page`/`ds-page` 缓存态必须渲染"上次更新"字样的既有钩子并出测试 |
| DASH-9 | P2 | 死面板仍可一键拉起 | `services_registry.py:38-42` `panel` 启动项 → `app_panel.py`（`:19-22` DEPRECATED（`:20` 仍写"41 页"），`:349-355/259-296` 演示数据当真值） | 断言：`SERVICE_CATALOG` 中 `tier=="free"` 的条目不得指向 `[STARTUP] manual` + DEPRECATED 文件；或从目录摘除并加回归测试锁定 |
| DASH-10 | P2 | 唯一真源图失真 | `frontend_map.yaml`（359 条 `backend_ref`，84% 为 `none`，仅覆盖 18/39 端点，11 条共享同一串批量 ref `:252-332`） | 断言：CI 校验 `set(map 中 api: 引用) == set(@app 注册端点)`（白名单例外须写明理由）；单条目 `backend_ref` 不得含 `×` 聚合超过 1 个端点 |
| DASH-11 | P2 | 可达页与导航脱节 | `web/pages/govm.html`（有引擎、有端点 `/api/govm:2665`，但 `index.html` 51 导航项里无它，`app1.js:14` 仅 hash 兜底） | 断言：`PAGES` 每个 id ∈ 导航 ∪ 显式白名单（白名单须含 `home`），测试直接解析 `loader.js` 与 `index.html` |
| DASH-12 | P2 | 口径漂移（注释当文档） | `services_registry.py:29`"16 项" / `api_server.py:1280`"16 启动项" / `api.js:80`"34 启动项" / 实测 35（含 `start` 者 11）；`loader.js:1`"47 页/37 引擎" / 实测 52/69 | 断言：文档字符串里的计数由代码在测试内重算（`assert "35" in doc`），禁手写数字 |

## 5 子节点清单

| 子节点 | 状态 | 说明 |
|---|---|---|
| `nodes/dashboard_automation_chain_mining.md`（本文） | 已封（除 §6 所列一条） | 真读路径 / 死活普查 / 拍板闭环 / 静默失败面 |
| `nodes/promotion_advisory_starvation_mining.md` | **未开（活的，建议开）** | 唯一能改变 §1.4 结论的挖掘：`sim` 池为何只有 2 条、`SCR-DEV` 为何 17 次跑只覆盖 1 个自然月、`sim_deviation_monthly` 的 30 天标记在断更/重启下是否会永久跳过。需要跨 S09/S10 节模拟盘账本，超出前端范围 |
| `nodes/frontend_static_panel_retirement_mining.md` | 未开（可延） | 38 个零后端页的逐页处置裁定（接/删/明确标注演示）。属施工与产品裁定，不属机制挖掘 |
| `nodes/ops_notification_single_outlet_mining.md` | 未开（部分被本文 DASH-3 覆盖） | 若 DASH-3 选"改裁定"方向，则本节点自动枯竭 |
| `nodes/service_catalog_truth_mining.md` | 枯竭 | 35 条目录逐个探测语义属清点工作，无矿（DASH-12 已把可判定部分固化） |

## 6 封矿判定

**部分封矿。** 已封的三块：
① 真读路径——14/52 页可达，逐跳 `file:line` 齐；39 端点消费者集合差分闭合（唯一零消费者 `/api/chain-impact-stream`）。
② 拍板闭环——执行体（CAS + 写后磁盘复核 + 决策台账 + kill-switch 探针 + PA-1 实据）经核验**是真接线**；
空转原因定位到"证据②只有 1 个自然月 × 1 个策略 + 证据①全 null"，并有今日 `last_receipt.json`（`built:0`）实证，
非推断。③ 静默失败面——AST 级普查（109/32/9 handler，19/9/1 纯吞），逐条给锚点与后果。

未封的一块：**`promotion_advisory_starvation_mining.md` 必须另开**。理由：本文能证明"龙头不出水"，
但"为什么不出水"的上游（`sim` 池规模、SIM-DEV 月度判定在 30 天标记下的推进性）属模拟盘管线节点，
本文只拿到盘上产物级证据（17 份 SCR-DEV、1 个 distinct (sid,month)、`last_audit.json` 的 `sim_deviation` 标记时间），
再往下挖要吃 CH 台账与 S09/S10 上下文，跨节点边界。

无法实证（登记，不猜）：
- 06:18:55 那条 `promotion_advisory_due` 事件的**发出者**：全仓唯一程序化产源是 `sim_governance.py:142`，
  而它受 `:137-138` 空值早退守卫，且最新 SCR-SIMGOV 档案（01:22）两条建议均 null → 该事件不可能出自当日 `main()`。
  候选为 `pipeline_events.py:878` 的 CLI `record <kind> <payload>` 手工调用，或某并行会话直调 `record()`。
  定论命令：读 `.runtime/strategy_pipeline/` 的 journal 历史（当日事件 payload 已被出队删除）或查 shell 史。
- `OWNER_TOKEN_KEY` 是否已在密钥存储中配置（不读凭据）。若未配置，DASH-1 的第二层防线成立。
- `models.html:3` 声明的"model_registry 8 条"是否与实际一致：无对应端点，无法从前端核；需走 `zephyr.data.ch_reader.query` 直读模型表（本文未查）。

## 修复优先级裁定建议

顺序 **DASH-1 → DASH-2 → DASH-3 → (DASH-4/DASH-6) → DASH-5 → DASH-7 → 其余 P2**。

- **DASH-1 必须先做**：这是唯一"修好就改变安全模型"的一行（`:663-664`）。今天不出事靠的是 §1.4 那个空龙头，
  而空龙头正是 DASH-2/§5 要修的东西——**修 starvation 之前先把门装上**，否则本清单第 2、5 项一落地，
  "服务端自签授权 + CORS 全开 + 本机任意进程"就从隐患变成可达路径。这是有先后耦合的一条，不能并列排期。
- DASH-2 是"让矿脉自己报枯"：`log-and-skip` 出队语义不改，任何后续接线（含 S12 `fw_backtest_due`）都可能静默丢事件，
  修完才能谈 DASH-3/§5 子节点的可信观测。
- DASH-3 需要 Owner 一句话裁定（改实现 or 改裁定），施工侧两种都能验收，不要替 Owner 选。
- DASH-4/DASH-6 属"对本仓最稀缺资产——Owner 信任——的直接消耗"，成本低（删端点 + 文案禁词门禁），与主线无冲突，建议同批做掉。
- DASH-5/7/8 是同一条病灶的三种表现（"取数失败=显示旧数据且报 ok"），建议合并为一个"降级可见性"小件施工，
  统一在前端侧要求 `ok:false` 或超龄必须出红字，别在三处分别打补丁。
