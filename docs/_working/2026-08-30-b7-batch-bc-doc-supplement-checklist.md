---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=design_memo_working · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-30 · topic=data_utilization_batch_bc_doc_supplement · scope=07_trading_decision_architecture · completes_when=批次 B/C 17 张表六字段消费级文档落位三目标文档且 ARCH-300 三空表前置闭环后归档。

# B7：63号文 批次 B/C 补文档——评估结论 + 补文档清单与要点

> **上游真源**：[63_data_utilization_audit](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/63_data_utilization_audit.md) §6.2 批次 B/C + §7.2 第二波施工计划 + §7.0.1 六字段模板。
> **评估结论（2026-08-30 ClickHouse 实证）**：主体为**纯文档补全且数据源可定位**（17 张目标表中 14 张在库有数据、DDL/采集配置/代码引用均可定位），走"清单+要点"路径；**3 张表任务已配置但 0 行在库**（concept_sector/sector_list/convertible_bond_list），属新发现采集层前置缺口，登记 **ARCH-300（open）**；5 张 §6.1b dormant 表前置为 Q8 待人决策（63 号 §10.2 已在跟踪，不重复登记）。

---

## 1. 任务提取（63号文要求）

- **范围**：批次 B（事件驱动/策略模块）+ 批次 C（板块轮动/行业分类）共 25 张表的消费级文档缺口；目标是消费层覆盖率 35.9% → ~68.9%。
- **数据血缘可追溯具体要求**（§7.0.1 六字段模板 + §7.0.6 验收三级）：每表在消费方文档至少含 ①业务含义 ②关键字段（消费字段非 DDL 全列）③消费频率 ④下游逻辑（算什么指标/触发什么规则）⑤依赖上游（对齐 frontmatter depends_on）⑥实证支撑（无则写"待回测验证"）；验收 L1 表名+稳定 path 命中 / L2 消费关系三字段命中 / L3 语义与代码行为一致（人工抽检）。浅覆盖反例：仅列名无字段/频率/逻辑。
- **已落地部分**：26/22/15 号三目标文档附录"数据资产消费登记（63 号审查批次 B+C，2026-08-20 登记）"已在位（未消费登记口径，3-5 字段汇总行）；**剩余 = 升级为 §7.0.1 六字段消费级正文小节**。跨批次拓扑序（§7.0.3）：被依赖表先补最小文档（如 sector_list 先于 sector_meta/concept_sector）。
- **不在本批**：62 号注册表路径 5 张（index_list/market_index/etf_list/lof_list/index_weight，D-7 裁定归 62 号施工线）；auction_book（D-6 随 24 号挂起）。

## 2. 在库实证（2026-08-30，system.tables + count 直查）

| 表 | 库.行数 | 状态归类 |
|---|---|---|
| share_change | c3_fundamental · 190,094 | ✅ 有数据，可直接升级 |
| rights_issue | c3_fundamental · 80,803 | ✅ 有数据 |
| equity_pledge_detail | c3_fundamental · 120,628 | ✅ 有数据 |
| analyst_forecast | c3_fundamental · 65,665 | ✅ 有数据 |
| industry_class_suppl | c3_fundamental · 5,203 | ✅ 有数据 |
| index_constituent | c1_market · 580,476 | ✅ 有数据 |
| stock_indicator | c1_market · 97,663 | ✅ 有数据 |
| convertible_bond_iv（cb_iv） | c1_market · 4,664 | ✅ 有数据 |
| sector_meta | c1_market · 1,080 | ✅ 有数据 |
| calendar_event | c1_market · 396 | ✅ 有数据 |
| concept_board | c1_market · 375 | ✅ 有数据 |
| concept_board_constituent | c1_market · 23,461 | ✅ 有数据（弱活跃，路由映射级） |
| **concept_sector** | c1_market · **0** | ⚠️ 任务已配置（`concept_sector_refresh` monthly_static akshare）但 0 行 → ARCH-300 |
| **sector_list** | c1_market · **0** | ⚠️ 任务已配置（`sector_list_refresh` monthly_static miniqmt）但 0 行 → ARCH-300；且为拓扑被依赖表（22 号附录注明须先补） |
| **convertible_bond_list** | c1_market · **0** | ⚠️ 任务已配置（`convertible_bond_list_refresh` monthly_static akshare）但 0 行 → ARCH-300 |
| index_adjustment | c1_market · 0 | ⏸ §6.1b dormant，待 Q8 裁定（63 号 §10.2 在跟踪） |
| ipo_schedule | c1_market · 0 | ⏸ §6.1b dormant，待 Q8 |
| margin_target_adjustment | c1_market · 0 | ⏸ §6.1b dormant，待 Q8 |
| stock_valuation | c1_market · 0 | ⏸ §6.1b dormant，待 Q8 |
| msci_adjustment | c1_market · 0 | ⏸ §6.1b dormant，待 Q8（已移出消费文档队列） |

> 注：63 号 v2.1.0 标注 concept_sector/sector_list/convertible_bond_list "代码活跃✓"系代码引用扫描口径；本日实证三张**库内 0 行**——采集任务配置在位但未见产出（月度任务未跑成/静默失败/调度未触发待排查），消费文档"下游逻辑"字段对空表无法通过 L3 语义抽检，故列前置缺口。

## 3. 补文档清单 + 每份要点

### 3.1 → 26_event_driven_strategy_detail（11 张，事件流语义）

统一结构：附录"未消费登记"行 → 升级为 §2.2 事件源节后正文小节（六字段），消费频率盘后增量为主。

| 表 | 六字段要点（关键字段/下游逻辑为核心） |
|---|---|
| convertible_bond_iv | 转债 IV 曲面点位；下游=转债事件 sleeve 定价参考（IV 低位+正股事件催化→弹性机会）；实证=90 号 §18 可转债 P1 待验证（写"待回测验证"） |
| convertible_bond_list ⚠️ | 转债标的池；下游=正股事件→转债映射查询；**前置=ARCH-300 采集实证**（0 行，达标级 L3 受阻；可先落最小文档标注空表状态） |
| calendar_event | 市场级事件日历（议息/宏观发布）；下游=事件前后窗口进出场规则（§2.4 衰减表事件日对齐）、与 10 号 regime 事件日历互补；频率=事件触发 |
| index_adjustment ⏸ | 指数调仓事件；下游=调入股被动买入/调出股被动卖出套利窗；**前置=Q8**（dormant，先维持登记行） |
| ipo_schedule ⏸ | IPO 日程；下游=IPO sleeve+37 号流动性抽离预警；**前置=Q8** |
| share_change | 股本变动（增发/送转/拆并）；下游=送转填权/增发摊薄事件信号；关键字段=change_type/shares_changed/announce_date（以 DDL 实列为准） |
| rights_issue | 配股方案；下游=配股除权前后价格压制/填权行情；频率=事件触发 |
| equity_pledge_detail | 质押逐笔（质押方/比例/预警线）；下游=高质押+临预警线→强平抛压事件预警；频率=盘后增量 |
| margin_target_adjustment ⏸ | 两融标的调入调出；下游=调入→杠杆可达性提升/调出→降杠杆抛压；**前置=Q8**；口径差异（§6.2 指派 25 号/§7.2 指派 26 号）维持 26 号事件流登记不重复 25 号 |
| concept_board | 概念板块清单；下游=概念利好事件→成分股筛选入口（与 constituent 配对，拓扑先补） |
| concept_board_constituent | 概念-成分映射；下游=概念事件→受益个股池生成 |

### 3.2 → 22_sector_rotation_spec（4 张，板块轮动语义）

| 表 | 六字段要点 |
|---|---|
| sector_list ⚠️ | 板块全集定义（880xxx/881xxx 推送池候选源，§5.1）；**拓扑被依赖表先补**；**前置=ARCH-300**（0 行） |
| sector_meta | 行业归属/成分数/编制规则；下游=板块属性特征归并、强度权重 40/30/30 分组基准 |
| concept_sector ⚠️ | 概念-个股/行业映射；下游=概念热度→成分股联动、与行业维度 RRG 象限确认互补；**前置=ARCH-300**（0 行） |
| index_constituent | 指数成分及权重；下游=板块 vs 指数重叠度分析、调仓被动资金流预判；580k 行实证活跃 |

### 3.3 → 15_data_feature_layer_spec（4 张，因子原料语义）

| 表 | 六字段要点 |
|---|---|
| industry_class_suppl | 官方分类外补充口径；下游=factor_registry 行业中性化/行业偏离裁剪的行业归属补充真源候选 |
| stock_valuation ⏸ | 个股估值日频快照；下游=价值类因子（BP/EP/SP）原料；**前置=Q8** |
| analyst_forecast | 盈利预测/评级/目标价；下游=一致预期变化/预期差因子（与 26 号 SUE 同源）、news_dual_tagger PIT 锚（report_date≤数据日已 production 实证）；实证=forage.ai 2026 nowcasting |
| stock_indicator | 个股指标宽表；下游=因子工程预计算指标直接读取层；**须标注与 16 号技术指标 machinery 的派生/原生边界**（附录既定注记） |

## 4. 工作量与前置条件评估

- **工作量**：14 张有数据表 × 六字段小节（每节 15-30 行）≈ 纯文档施工 1-2 天可分 3 小批（按目标文档分批，与 63 号"未来工程-小型"裁定一致）；L3 语义抽检按 §7.0.6 走。
- **前置条件**：
  1. **ARCH-300（本批登记，open）**：concept_sector/sector_list/convertible_bond_list 三表采集任务已配置但 0 行——须先排查月度任务执行链（miniqmt trading_day_only 月初遇周末跳过/akshare 接口变更/静默失败）并实证灌数；期间三表仅可落"最小文档+空表状态标注"，不达标 L3。
  2. **Q8（63 号 §10.2 已在跟踪，不重复登记）**：5 张 dormant 表（index_adjustment/ipo_schedule/margin_target_adjustment/stock_valuation/msci_adjustment）待人决策 dormant vs 补采集。
- **不依赖外部数据**：全部源为既有 akshare/miniqmt/tqcenter 管道与在库表，无新供应商申请。
