---
ttl: task_bound
doc_type: log
title: L04-S1 子模块挖矿簿 · 板块→个股传导段（L2-06 家族：强度调节分/三级放行/龙头定位）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L04
status: MINE 完成（六向封口，缺口三态见 §5；长尾 2 条见 §6 尾）
---

# L04 · S1 传导段（板块→个股两字段边界）

覆盖父簿 SKEL.md 的 **W0** 子块（TDM-E-L2-06 / L2-06-1 / L2-06-2 / L2-06-3）。

**① 职责一句话**：把板块层结论以"强度调节分 + 龙头定位"**两个封闭字段**下沉到个股层，并守住层级隔离（个股层不得直引板块买卖结论）——本环节唯一的跨层写入口。

**② 现状实测**

| 项 | 实测值 | 出处（本册 Read/Grep 实测） |
|---|---|---|
| 传导核码件 | `src/zephyr/signal_ashare/core/sector_conduction.py` 99 行，MOD-SIG-136，MATURITY=design，STABILITY=evolving | 文件头 :7/:10；函数 `strength_conduction_bonus` :60、`apply_strength_conduction` :80 |
| 乘数口径 | 三锚点 10 分=+15%、6 分=+5%、<6 分=−10%（平段，不随深度扩大）；6→10 线性插值每分 +2.5%；乘数恒 ∈[0.90,1.15]；`adjusted = stock_score × multiplier` 保序不重排名 | :22-25/:37-44/:71-77/:93-94 |
| fail-closed | 强度 ∉[0,10] 或个股 score<0/NaN → `SectorConductionError` | :47/:69-70/:90-91 |
| 准入闸码件 | `src/zephyr/signal_ashare/sector/sector_gate.py` 169 行，MOD-SIG-026，MATURITY=new；四态常量 CORE_HOT/SECONDARY/WILDCARD/BLOCKED | :7/:43-46；`admission_gate` :117、`water_temp_response` :91、`apply_rrg_filter` :153 |
| 阈值版本 | v2.1（0.70/0.90→0.60/0.80，依据"板块一日游 Top3 次日重合率 14.8%"），**注记"待 G05 回测校准/spec §6 待裁定"** | :19-21/:29/:40 |
| 龙头定位码件 | `src/zephyr/signal_ashare/sector/sector_leader.py` 614 行，MOD-SIG-062，MATURITY=testing；四档 leader/backbone/follower/neutral，传导权重 1.5/1.2/0.8/0 走 `SectorLeaderConfig` 不硬编码 | :7/:22-27/:139-152/:166/:183/:196；入口 `identify_sector_leaders` :507 |
| 龙头依赖表 | `c1_market.kline_daily` + `c1_market.stk_limit` + `c1_market.sector_constituent`（SCD-2 时点过滤，PIT ≤ trade_date） | 文件头 :4/:8 |
| 地图节点 | `config/trading_decision_map.yaml:1073-1097`（L2-06，point=盘后，activation=postmarket，module_ref=sector_conduction.py，factor_refs 与 data_refs **均为空**）；:1100-1129（L2-06-1，point=盘中，activation=intraday，data_refs=[DS-059]，fallback="Top 热门列表缺失→只走超强个股通配通道≥0.80"） | 本册 sed 实测（原 SKEL 引用行号成立） |
| 生产触发面（传导） | **无**：全仓 grep `sector_conduction\|apply_strength_conduction` 命中仅 ①`signal_ashare/__init__.py:121` 导出面 ②`tests/signal_ashare/sector/test_sector_conduction.py` ③新载体 `candidate_pool_snapshot` 的 `conduction_adj` **占位列**——无任何调用方计算并注入 sector_strength | 本册 grep 实测 |
| 生产触发面（放行闸） | `admission_gate` 调用方 **=0**（仅 :29/:32 自述与 `tests/test_sector_gate.py`）；同件内 `water_temp_response` **有**在产侧带：`src/zephyr/strategy_pipeline/daily_gate_snapshot.py:248`（注释明确"查表=采集非判定"，:187 记 Owner 已批方案甲，L03-C02 步1 落地） | 本册 grep 实测 |
| 生产触发面（龙头） | 库内调用方**非零**：`signal_ashare/limit_up/war_pool_generator.py:56-59,330`、`signal_ashare/mainline_probability.py:51-52`（均 import `identify_sector_leaders`/`SectorLeaderBoard`）；两者自身是否有生产挂点＝本册未尽（见 §6 长尾 T1） | 本册 grep 实测（**净改判** SKEL W0④"无生产调用方"） |
| 日循环链路 | `daily_decision_orchestrator.py:75,688` → `collect_gate_snapshot(day, market_state, reader)` → `daily_gate_snapshot.py:418` → `_collect_candidate_pool`（:290）→ 落 `c1_market.stock_candidate_pool`；`config` 侧 `src/zephyr/data/config/tasks.yaml` grep `daily_gate\|candidate` **零命中** = 该链不在数据采集批里，走策略侧编排器 | 本册 grep/sed 实测 |
| 数据起止与新鲜度（输入侧） | 成分腿 `sector_constituent` FINAL 止 2026-09-03、`sector_constituent_snapshot` 当日到（两表劈叉，SKEL W1② 基线，本册未复核）；`stk_limit` 921 万行（12 号文 :59 基线）；**`kline_daily.pct_change` 列 2026-08-22 实证全 0 未填充**（故龙头件当日涨幅由相邻收盘自推） | sector_leader.py:8 注记（"字段在≠数据可得"本环节实证） |
| 落库载体（输出侧） | `schemas/categories/market/market_stock_candidate_pool.py` DDL 已存在（repo 根，另有 .worktrees/.aidrafts 副本）+ 生产者 `signal_ashare/core/candidate_pool_snapshot.py`（MOD-SIG-152，CREATION-TOKEN `candidate-pool-snapshot-l04c01-20260925`，16 列 INSERT 与 DDL 严格同序，MATURITY=testing）——**列在、值 None**：`conduction_adj` 显式缺省，"None=显式缺省禁拍 1.0 冒充中性"，注记"W0 接线后回填" | 本册 Read 实测 :1/:5/:8/:17/:97/:166/:181/:185/:214/:389/:396 |

**③ 六向台账**

| 向 | 发现（内部反查 ＋ 全网搜索） |
|---|---|
| ①上游该喂什么 | 内部：conduction 头注 :4 明确"板块强度由调用方从 **DS-059** 算好注入（纯函数核零 IO）"——实测仓内**无任何调用方做这件事**（见 §②生产触发面）；gate 需三原料（板块强度/个股强度/日成交额）+ Top 热门榜 + RRG 象限 + WaterTemp（:23 水温归 regime/情绪周期，本模块不判）；leader 需 kline/stk_limit/成分三表。地图侧 L2-06 节点 `data_refs` 与 `factor_refs` 双空（yaml:1087-1088），L2-06-1 仅 DS-059 → **两字段中"强度调节分"的输入契约未落图**。外部：传导沿"领涨股→同板块跟风股"路径有实证支持——海通证券《行业与概念板块的动量溢出效应》（2018-12-11，BigQuant 转载 https://bigquant.com/wiki/doc/ZnRQswCSAk ）；《中国A股市场行业动量效应实证研究》（CNKI 学位论文，2025-05 https://read.cnki.net/web/Dissertation/Article/10561-1011190596.nh.html ）；A 股"经济关联与股票回报"lead-lag 谱系（https://economy.alljournals.cn/view_abstract.aspx?aid=0677DA8E81D857F73EAAA8377EB89347&pcid=4182BDE6AAE91C51 ）→ 现役把系数挂在"板块强度"标量上，文献主机制是"龙头收益 lead-lag"，两者不同构 = L04-S1-G1 |
| ②下游该喂谁 | 内部：唯一已建消费位=新载体表列 `stock_candidate_pool.conduction_adj`（占位 None，禁 1.0 冒充）；导出面仅 `signal_ashare/__init__.py:121`；龙头榜下游=战池/主线概率两件（已实测非零 import）；`[CONSUMERS]` 自述"G05 选股引擎打分池（待接线）"（conduction:5）与"待 G05 选股引擎漏斗准入层/RRG 象限过滤层"（gate:5）——**两文件的自述消费方至今停在"待"**。外部：传导输出到组合层的业界范式=截面加权/TopK 换手（qlib TopK-Dropout，SKEL §4 已入图，本册标"沿用"不重复登记，防同论断二次入图） |
| ③算法/机制业界学界 | 内部：三锚点+线性插值+平段（:22-25）与"先 gate 后 weight"次序（gate:19）；龙头四档评分三维加权（情绪 30%/地位 25%/形态 20%，筹码 15%/基本面 10% 留扩展口不参与归一，:29-35）+中秩 ties 约定。外部：**龙头股 ≠ 领涨股** 的区分在中文量化圈已成公共口径（《行业动量の龙头股 VS 领涨股》，知乎专栏量化专辑，2023-07 https://zhuanlan.zhihu.com/p/645456445 ）与海通溢出研报（上一行，2018）两独立来源互证 → 可入图结论：**"谁在板块内领先"本身需要独立度量（lead-lag/Granger 类），不能用角色分档代理**；本仓同类件已存在=`limit_up/limit_up_ecosystem_leadership.py:450`（`leadership_coef > granger_threshold` → is_leader，Granger 因果定领导者）——**该件与 sector_leader 四档之间无对表**（本册净新增观察）→ L04-S1-G2 |
| ④后端代码缺什么 | 内部：缺三件——(a) sector_strength 注入腿（无"sector_state→10 分制强度"取数函数，DS-059 无生产读取方）；(b) `admission_gate` 零接线（且 activation=intraday 声明无任何盘中挂点）；(c) 传导结果回填 `conduction_adj` 的赋值点（载体列在、生产者写 None）。外部已查无（查法：以"sector strength multiplier applied to single-stock score library python"主题检索，未见可复用开源件；qlib 的 sector-neutral/tilt 属组合优化层不同位，已在 SKEL §4 登记） |
| ⑤前端怎么呈现（只登记） | 内部：`sector_leader.py:5` 自列候选消费方含"Dashboard D-05 龙头/中军/跟风榜"与"SEC-01 板块盘后报告器"——**均为待接项**；本册未逐一核对前端资产面（预算限制，见 §6 长尾 T2），登记不施工。外部：已查无（查法：榜单型呈现无外部方法论诉求，四档角色榜=内部语义） |
| ⑥数据字段有没有 | 内部逐个核对：`sector_strength`（依赖 L03 sector_state，独立层边界 G9 待追认）✗无注入件；`stock_score`（W2 漏斗产，内存）✓；`symbol/role/consec_limit`（leader 产，frozen asdict 可序列化）✓；`日成交额>2 亿`门槛原料=**daily_valuation/stock_daily_basic，正被 DU-11 部分写入病日毁**（09-24 仅 1,000 行 vs 应 ~5,560）→ 门槛实测会因缺数误放行/误拦截；`kline_daily.pct_change` 全 0（已绕开）；`Top 热门榜`（fallback 分支输入）=未核。外部：业界"相对强弱/板块强度"常规口径为对基准比值的排序分位（RS 类），与 10 分制分位口径一致——单源，**待验证**级不入图（闸 2） |

**④ 缺口清单**（沿用 L04-Cxx／LK-xx／Dxx；新缺口续编并注"册内未见"）

| 编号 | 内容 | 状态 |
|---|---|---|
| L04-C08（既有） | 传导两字段接线核验（乘数表对 yaml、三原料供数） | 沿用；本册补证：**sector_strength 注入腿完全缺件**，非"仅缺单测" |
| LK-04 / D15（既有） | L3 生产挂点缺失 / L2 门三原料 | 沿用（L3 侧 LANE-BUILD 已落 pool 快照侧带，本册 §② 实证） |
| G9（板块线在途） | 板块层独立化边界冲突 | 事实记档：本册一切"强度原料"依赖该边界，不阻断 |
| **L04-S1-G1** | 传导系数挂载对象与文献主机制不同构：现役=板块强度标量乘数，业界两源实证=领涨股→跟风股 lead-lag 溢出；缺"传导强度实证度量轴"（哪个板块的溢出真的可赚）——**册内未见** | 新登 |
| **L04-S1-G2** | 同仓已存在 Granger 型领导者识别件（`limit_up_ecosystem_leadership.py:450,457`）与 `sector_leader` 角色四档之间**零对表、零复用**，两套"谁是龙头"真源并存——**册内未见** | 新登 |
| **L04-S1-G3** | `admission_gate` 调用方=0 且节点 `activation: intraday` 无盘中挂点；同件 `water_temp_response` 却在产（半接电状态）——**册内未见（SKEL 只记"覆盖未接电"，未记半接电劈叉）** | 新登 |
| **L04-S1-G4** | L2-06 节点 `data_refs`/`factor_refs` 双空 → "强度调节分"的输入契约未落图（DS-059 只挂在 L2-06-1），机查不到该字段该由哪张表喂——**册内未见** | 新登 |
| DU-11（既有） | daily_valuation 部分写入 → 直接受害面=本闸"日成交>2 亿"第三关 | 沿用（本册补记受害点） |

**⑤ 自审闸三态裁定**（量尺=终局全貌：Owner 一人 + 一切可自动化者全自动化）

| 缺口 | 裁定 | 理由 |
|---|---|---|
| L04-S1-G1 | **挂起排期** | 解锁条件=`stock_candidate_pool` 载体累计 ≥120 交易日真值（L04-C01 在途）+ L04-C07 个股层条件概率表开算后，按"板块强度分位 × 龙头档"分组检验溢出可赚性；终局必须要（无人盘不可能人工感知哪个板块真传导），但先建检验会因载体无史返工——时序未到，非封矿 |
| L04-S1-G2 | **施工（内收申报）** | 两套"谁是龙头"并存=终局必炸的一致性债；收口方式=以 `sector_leader` 四档为对外真源、Granger 件降为"领先关系度量"内部件并在 doc 层交叉引用（净零：不新建第三件，不退役任何一件，只定真源方向）；成本低（doc+引用注记+一条单测对表） |
| L04-S1-G3 | **挂起排期** | 盘中挂点属日循环编排器的 intraday 通道（09 号文 §8.3.2 另案，不在本环节立项）；解锁条件=盘中事件通道有主（与 L3-11 日内动态选股同批）；当前禁在 gate 件内自造 sleep/cron（宪法 §9.3 事件触发红线） |
| L04-S1-G4 | **施工（TDM 增长轨）** | 一列 `data_refs` 补登即消灭"字段该谁喂"的人工追问；与 L04-C08 同批，禁另立图治理项目 |
| 载体改判（非缺口） | 记档 | SKEL W0③/W7②"两字段无落库载体"已过期：列已建、值未填。父簿 §3 的 L04-C01 应从"补建载体"改判为"载体在、接线未通"——移交 LANE-LAND 时随 _INDEX 汇总，不改实现码 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | signal/noise 与归因 |
|---|---|---|---|
| R1 | 内部：三件码（conduction 全文 99 行 / gate 头+签名 / leader 头+签名+常量） | signal | 乘数三锚点与插值口径、v2.1 阈值待校准注记、四档权重走 config |
| R2 | 内部：消费面全仓 grep（三件各自） | signal | 净改判 2 处（leader 库内调用方非零；conduction 零调用但载体占位列存在） |
| R3 | 内部：yaml L2-06 段 + tasks.yaml + 编排器链 | signal | 触发面劈叉实证：数据批零命中、策略侧编排器在调；发现新载体 MOD-SIG-152 与 DDL |
| R4 | 外部：行业动量溢出/lead-lag（中文圈 1 轮） | signal 2 / noise 2 | noise 归因=①futunn 资讯页（无方法论，营销文）②CSDN 转载"顶刊论文揭秘"（二手转述无原始出处）→ 二者按闸 1 一律不入图，只留"曾检"记档 |
| R5 | 外部：开源可复用件（sector tilt 类） | 已查无（查法见 §③④行） | 记档 |
| R6 | 内部：CH 实测行存/新鲜度 | **受阻**（本册未起查询，改用文档+代码注记基线，闸 1 精神：不拿未测数字当实测） | 不算查无，转长尾 T3 |

**长尾（本册调研未尽，明确列出）**
- T1 `war_pool_generator.py` / `mainline_probability.py` 自身生产挂点有无（tasks.yaml 与 AutoRuntime 双查）。
- T2 前端资产面 D-05 榜单位查重（`src/zephyr/frontend/dashboard/`）。
- T3 CH 只读实测：`sector_constituent`/`sector_constituent_snapshot`/`daily_valuation` 起止与新鲜度复核（本册引用为文档基线，未机测）。

**本册封矿判据自评**：六向均已填（含"已查无+查法"两处），但 T1-T3 未清空 → **状态=MINING（矿脉未枯，长尾在册）**，不宣告封矿。
