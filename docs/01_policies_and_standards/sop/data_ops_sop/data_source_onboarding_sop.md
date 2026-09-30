---
ttl: permanent
doc_type: policy
completes_when: 持续有效（方法论常驻真源，退役须有替代件并走 ROOR/Owner 流程）
rule_form: procedural
verifiability: manual
title: 数据源全生命周期 SOP——从挖矿到消费端接线（流程编排真源）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.0.0"
date: 2026-10-01
topic: data_ops_sop
---

# 数据源全生命周期 SOP——从挖矿到消费端接线（流程编排真源）

> **真源关系**：本件=数据源**流程编排**真源（新数据源从找→建→接→通→消费的标准路径）。纪律真源=data_ops_policy.md（三步验证/写入红线/PIT/判重，本件各阶段引用不重复）；需求真源=骨架总图（docs/_working/altdata_line/01，中类=需求单元）；源资产真源=architecture_model/data/data_sources_registry.yaml（DS-* 条目）；挖矿方法论=mining_sop（六向寻路/三重扫描判据；产出 MUST 映射本件 §9A 六问接线坐标系）；**骨架层上位=skeleton_mining_policy.md（mining_sop 族，新域开工先挖骨架——本件 §2 是骨架 ⬜ 的中类级下游）**。
> **诞生背景**：2026-09-17 数据线会话定调。三个真实教训直接催生本件：①股东户数表 7 月断供两月才被发现（任务存在却不生效——「任务存在≠管线活着」）；②macro_data 频率口径混乱（annual/日频混用）；③多个 ⬜ 中类的数据源从未做过全网挖矿。

## §1 需求立项

1. 需求入口两种：骨架总图的 ⬜ 中类（供给侧补全）或消费端缺口（某因子/某分析链缺数，需求侧拉动）。
2. 立项登记：中类编号 + 需求描述 + 目标消费端，写进当次施工文档（如 altdata_line 域文档）。
3. 先查重：该中类是否已有表/任务（tasks.yaml + system.tables + known_data_gaps.yaml）——防重复建源。

## §2 数据源挖矿（全网挖干）

> 上位：域级骨架未建时先走 [skeleton_mining_policy.md](../mining_sop/skeleton_mining_policy.md)（骨架先挖根）；本节 = 骨架 ⬜ 中类的数据源级挖矿。

1. **全景清单**：对该中类做全网数据源挖矿，判据沿用三重扫描（按生产者扫：官方/交易所/协会/公司/海外/另类机构；按获取方式扫：API免费/API注册/文件下载/爬虫/手动；按因子文献扫）。
2. **获取方式分类与默认立场**：
   - API 免费（akshare/tushare 直连）→ 默认推进；
   - API 注册（免费账号）→ 进待注册表，打包报 Owner；
   - 文件下载（官方公开数据集）→ 推进，注意更新频率与断更风险；
   - 爬虫 → **默认否决**，需专项裁定（ToS/反爬/维护成本三查，gsxt 地狱级反爬案例在案；旧版 4.0 已因法律风险归档爬虫管理系统）；
   - 付费/便宜 → 进待注册表标注价格，由 Owner 筛选。
3. **产出登记**：全部候选写入 `docs/_working/altdata_line/10_data_source_candidates.yaml`（待注册表，见 §3）。

## §3 待注册表与 Owner 报批

**文件**：`docs/_working/altdata_line/10_data_source_candidates.yaml`（与 data_sources_registry.yaml 同目录同风格；YAML 优于 DB：可 diff、走门禁、免并发写库）。

**条目字段**：
```yaml
- cand_id: DS-CAND-001          # 毕业后升格为 DS-* 正式条目
  name: ""                      # 中文名
  vendor: ""                    # 生产者/机构
  acquire_mode: api_free        # api_free | api_register | download | crawler | manual | paid_api
  cost: free                    # free | cheap(<500/年，标价) | paid(标价)
  register_barrier: ""          # 注册门槛：手机号/企业资质/审核期
  coverage: ""                  # 数据范围
  frequency: daily              # 历史深度+更新频率
  history_depth: ""
  anti_crawl_risk: none         # none | light | heavy | hell（gsxt 级）
  tos_risk: ""                  # ToS/PIPL 合规注记
  score: {availability: 0, signal: 0, fit: 0, maintenance: 0}   # 四格=90收敛判据
  target_table: ""              # 拟落表（§5 设计后回填）
  status: candidate             # candidate|approved|registering|integrated|promoted|rejected
  notes: ""
```

**报批流**：免费+四格≥3 → 直接推进；api_register → 打包报 Owner 批量注册；paid → 标价报审。Owner 只见筛选结果，但**全部候选都有记录**（筛选可见、过程可溯）。

**毕业流程**：integrated → 在 data_sources_registry.yaml 建 DS-* 正式条目（同步 data_source_assets）→ cand 状态改 promoted。

## §4 字段设计

1. **时间列 = PIT 锚**，命名随语义定并全表唯一：行情 trade_date/trade_time、公告类 announce_date、报告期 end_date/report_date。**禁止裸 timestamp 无时区**（RULE-SCHEMA-TZ：DateTime64(3)+显式时区）。
2. **三件套必备**：`data_source`（LowCardinality(String)）、`quality_flag`、`ingest_ts`（DateTime64(3,'UTC')）——macro_data 缺 frequency 口径统一的教训：**频率字段枚举固定**（annual/quarterly/monthly/weekly/daily/intraday，禁中文混写）。
3. 数值列带 `unit` 说明或独立单位列；枚举值字典化（进 field_vocabularies 或表内注释）。
4. 主键语义明确：symbol+date 类自然键 vs 代理键，回补幂等性在 design 阶段定（引用 data_ops_policy §3）。

## §5 表设计

1. **庁前缀路由**：c1_market（行情/另类）/ c3_fundamental（财务/预期）/ c1_backtest（回测/因子/筛选）。表名 snake_case，语义完整（shareholder_count 而非 gdhs——可搜索性）。
2. **DDL-as-Code 单真源**：`schemas/categories/<域>/<表>.py` 立字段 → `scripts/ch/apply_*.py` 部署 → `verify()` 对 system.tables 做引擎一致性校验（防假成功，CH ALTER 假成功事故在案）。
3. ReplacingMergeTree + 月分区为默认引擎（例外需注明理由）；ORDER BY (symbol, <date>)。
4. 新表登记：anchored_state（tasks 警告教训）+ capability_canonical_file_registry。

## §6 Provider 接入

1. `src/zephyr/data/implementations/` 新增 provider；接口经 capability 三闸（capability_validator/semantic_gate/symbol_gate）。
2. `fallback_sources` 必填（哪怕显式置空+原因）——DATA-TASK-COMPLETENESS 门禁盯防；单源无备=停更即断供（月报/口岸/水库三案）。

## §7 任务登记与调度

tasks.yaml 条目模板（字段以现有任务为准）：

```yaml
- task_id: <域>_<内容>_incremental     # 命名含内容不含中文
  table: <db>.<table>
  source: <provider>
  schedule: <槽位>
  incremental: true
  date_col: <PIT 锚列>
  dependencies: []
  capability: <capability>
  fallback_sources: [...]
  extra:
    description: "一句话（含 akshare 接口名，便于溯源）"
```

**调度槽位选择规则**（对照 schedule.yaml）：
- 盘后行情/财务类 → daily_kline（16:30 系）；
- 低频校准/月度静态 → weekend_calibration / monthly_static；
- 事件驱动增量 → daily_event。**⚠️ daily_event 槽位有断供前科**（shareholder_incremental 断供两月、daily_crypto 曾挂空池）——**选它必须加探活验收（§8）**；
- 下载时间三原则：源端更新之后（别抢在官网发布前）、错峰（CH 安全窗 04:00-05:00、避开整点拥堵）、休市后；
- disabled 必带 disabled_reason（门禁硬拦）。

## §8 通道打通与接通验收（本 SOP 的灵魂）

1. 首跑全量回填：分块、断点续传（progress_store）、缺口登记 known_data_gaps.yaml。
2. 对账：行数 vs 源端口径；抽样字段比对。
3. 质量闸：quality_gate → integrity_checker（行数 vs 历史日均）→ cross_source_validator（有备源必比）。
4. **接通验收三查（缺一不算通）**：
   - ①表有数且 max(date) 新鲜；
   - ②调度器日志/心跳可见该任务真实执行记录（**反例入册：shareholder_incremental 任务在、断供两月无人知**）；
   - ③目标消费者实际查得到数（§9 路由落地）。
5. 失败必须留痕 failures/{date}_{task}.json——静默失败=断供起点。

## §9 消费端接线（接通哪里——路由表=初猜，终局以 §9A 六问挖掘为准）

| 数据域 | 默认消费端 |
|---|---|
| 行情/高频 | 回测引擎、因子计算、传导链公司节点（ig_node_binding） |
| 财务/预期 | c3 派生层（DS-230）、预期因子（B7） |
| 宏观 | 传导链宏观节点（macro_data indicator 绑定）、宏观因子 |
| 商品/另类 | 传导链商品节点（BOM 叶挂价）、行业因子 |
| 实体/关系 | D1 产业链图谱、02 实体图 |
| 公告/文本 | 03 公告因子家族、C/G 情绪线 |
| 事件流 | 作战室/日刊、反向归因 |

**铁律：每个新数据集必须登记 ≥1 个实际消费者并验证可查**——防"接而不通"（edb_data 表 0 行停止更新的教训）。接通后 **MUST 继续 §9A 六问挖掘**——"≥1 消费者"是最低线不是终点（情绪温度计六成分仅 C2 有消费、技术指标 81% 零消费两案在案）。

## §9A 数据用途挖掘六问（接通≠终点——v2.0.0 新设）

> **定位**：§1-§8 答"数据进来"，§9 答"接到哪"，本节答"**还能用在哪**"。触发三个：①新数据过 §8 接通验收后 MUST；②存量数据按 §9C 批次回补；③T2 半年复审 / 新策略立项反查。方法论=mining_sop 六向寻路，产出按本节六问坐标系逐问入账；**查无也是结论，逐问留痕**（情绪温度计六成分仅 C2 有消费、技术指标 81% 零消费两案在案——"算完就躺"是系统性盲点）。

六问记录写进当次施工文档"挖矿增补"章节（mining_sop §7 惯例）；接线结论回填对应注册册：

| # | 六问 | 挖法 | 入账口 |
|---|------|------|--------|
| Q1 | 能产出哪些因子？ | 字段×变换枚举（量价/统计/横截面/事件/文本）→ 转 [factor_mining_sop](../mining_sop/factor_mining_sop_policy.md) S0-S7（regime 条件化必报） | factor_registry candidate 卡 |
| Q2 | 哪些策略需要？ | 反查 strategy_registry 全卡（inputs/data_refs）+ TDM 十职能逐族扫（大盘/板块/个股/执行/持仓/离场/组合/资讯/推演/新市场） | 策略卡 data_refs 补挂 + TDM 节点 data_refs |
| Q3 | 哪些模块需要？ | capability_lookup 反查 + grep 消费端 + §9D 消费普查 | data_asset_registry.consumed_by_jobs 回填 |
| Q4 | 哪些环节需要？ | trading_day_cycle_map 44 环节四段（A盘前/B盘中/C盘后/D夜窗）逐段配 downstream_action | tasks.yaml 调度挂钩 + 环节契约骨架回写 |
| Q5 | 哪些地图需要？ | TDM 决策图 / GOMAP / 产业链图（MOD-SIG-125）/ 概念板块图 / 骨架总图，逐图扫挂点 | 图谱节点挂链 / TDM data_refs |
| Q6 | 还有哪些盲点？ | 六问查无记档 + 跨册状态汇总（指标册在位/因子册 skip/TDM DATA-GAP 三处状态无人汇总=盲点本体） | census 台账 → wiring_registry（§9D） |

## §9B 多用途展开矩阵（同一数据×应用面，强制逐格判定）

> 同一数据天然多用途：KDJ 可用于大盘（kline_index）/板块（kline_sector_880/881）/个股（kline_daily）/做T（盘中 1min/5min）；hog_* 猪价链可用于产业链地图（BOM 叶挂价）+ alt_regime F10/F11/F12 + 通胀宏观因子。**禁"算一次只接一处"**。

1. **应用面清单（12 面）**：大盘/指数、板块/行业、个股、做T（日内）、可转债、ETF/LOF、期货/商品、币圈、宏观/择时、产业链/传导、事件驱动、文本/情绪。新应用面出现时先扩充本清单再挖。
2. **逐格判定**：数据集（或指标/因子）× 应用面 = 适用（写明消费目标=接线工单）/ 不适用（一句话原因）——**两态都留痕**：不适用留痕防漏判，适用留痕即工单。
3. 矩阵随六问记录同章节落盘；跨数据集汇总视图**不另建账**——机生消费普查（§9D）即汇总视图（净零：零新账本零新门禁）。

## §9C 存量数据回补批次（考古式清产）

1. 工作队列=消费普查孤岛台账（`data/runtime/consumption_census_ledger.json`；2026-09-30 读数 473 岛：indicator 115 / factor 126 / strategy 129 / table_residual 61 / macro 15 / 其余 27），按 value_score 降序分批。
2. 每批逐实体过 §9A 六问 + §9B 矩阵 → **三态出口**：接线 / 挂账（defer_reason 必填，90 天门照计龄）/ 判退役（走 §10 源死亡处置）。三态全留痕。
3. 批次纪律沿用 [skeleton_mining_policy §4](../mining_sop/skeleton_mining_policy.md) 考古批：批次号+批次日志+挖干判据（六问全查无+无未挖长尾），禁"一次全清"空头承诺。

## §9D 接线闭环与盲点账（机生链路，禁手维护）

1. 消费普查台账（census）=孤岛事实源 → `scripts/governance/d3_metadata/generate_wiring_registry.py` 产机器视图 → 交总筹落 `wiring_registry.yaml`（wiring_status ∈ unwired/wired/exempt）——生成器禁直写登记册，`--check` 对账漂移≠0 即待入账。
2. 超期门：`scripts/governance/check_wiring_orphan.py`——unwired 且登记超 90 天=orphan（`--strict` 拦截；defer_reason 非免死牌，超期须重评）。
3. 复扫节奏：新数据接通后 / 存量批次每批收口后 / 半年 T2 复审，各跑一轮 census；unwired 实证 state=active 即自动记 wired 治愈事件。

## §10 运维常态与退役

1. 常态：integrity 日巡检、缺口自动登记+auto_backfiller 回补、source_sla_tracker/熔断器在岗。
2. **停更检测**：max(date) 落后阈值（日频>3 天/月频>45 天）即告警——月报停 2025-06 三个月才发现的教训。
3. 源死亡处置：disabled+disabled_reason 留痕 → **能力迁移清单**（DS-IFIND 范式：逐 capability 写明去向）→ 表处置（留史/归档）。
4. 退役评审引用骨架总图计数更新。

## §11 一页检查单（新数据源上线 14 查）

①骨架中类编号？②查重过？③全网挖矿三扫描？④candidates.yaml 登记？⑤报批状态？⑥字段含 PIT 锚+三件套？⑦DDL-as-Code+verify 过？⑧anchored_state+capability 登记？⑨provider 过三闸？⑩fallback_sources 有？⑪schedule 槽位选对+探活？⑫接通三查过？⑬消费者登记且查到？⑭巡检/停更阈值生效？


## §12 存储分层与落盘位置（冷热分离，2026-09-18 增补）

> 来源：G 盘冷库建成（3.7T，G:\zephyr_cold）+ 冷热分离定调。本节回答「新数据源接通后，数据放哪」。

**三层存放**：
| 层 | 位置 | 放什么 |
|---|---|---|
| 热 | ClickHouse c1/c3 + 本地数据盘 | 清洗后用于回测/消费的结构化数据（唯一回测真源） |
| 温 | 本地 Parquet 离线仓（factor/offline_store、E 盘归档器） | 因子离线仓、批量预取 |
| 冷 | **G:\zephyr_cold**（00_manifest/10_inbox/20_raw 原料/30_corpus 语料/40_migration/50_archive/90_tmp） | 原始抓取物、原文快照（PDF/HTML/网页）、大体积低频原料、旧项目归档 |

**新数据源落盘规则**：
1. 原始抓取物/网页快照 → 冷库 10_inbox 走入库四步（登记 00_manifest/drawers.jsonl 后归位 20_raw/30_corpus，抽屉=骨架大类编号）；
2. 清洗后结构化数据 → 只进 CH，**禁入冷库、禁双真源**（冷库副本仅作 archive）；
3. 完整规程（命名规范/immutable/出库流程/E 盘与 F 盘迁移计划）= [docs/_working/altdata_line/10_g_drive_cold_storage_sop.md](../../../_working/altdata_line/10_g_drive_cold_storage_sop.md)。

**存量迁移令（2026-09-18）**：E 盘 数据下载\研报（3 万份/85GB）→ G:\zephyr_cold_corpus
esearch_reports9_bundle\；F 盘研报 PDF（约 6 万份）→ 30_corpus
esearch_reports\。分批搬运、hash 抽检 5%、原目录留 30 天双备份期。执行归数据子分包（09 清单 D9）。

## §13 一页检查单（增补 2 查）
15. 原文快照/原料是否已存冷库并登记 manifest？（冷热分离）
16. 清洗数据是否只进 CH、未在冷库留第二工作副本？（禁双真源）

## §14 一页检查单（增补 3 查，v2.0.0 用途挖掘）
17. §9A 六问逐问跑过并留痕（查无也留痕）？
18. §9B 矩阵逐应用面判定过（适用+不适用两态都留）？
19. 接线回执已入账（consumed_by_jobs / factor 卡 / TDM data_refs / 图谱）+ §9D 复扫与 90 天门在岗？

## 修订记录

| 日期 | 版本 | 变更 | 批准 |
|------|------|------|------|
| 2026-09-18 | 1.0.0→1.1.0 | 初稿（§1-§11 接入前半环：挖矿→设计→接通→验收）+ §12 冷库分层增补 | 2026-09-17 数据线会话 |
| 2026-10-01 | 2.0.0 | 后半环补全：§9A 六问用途挖掘（因子/策略/模块/环节/地图/盲点，逐问挖法+入账口）+ §9B 多用途展开矩阵（12 应用面，KDJ/猪价链两例）+ §9C 存量回补批次（census 473 岛为首批队列）+ §9D 接线闭环（census→wiring_registry→90 天门）；§9 路由表降级为初猜；§14 增补 3 查 | Owner"数据进来→六问用途挖掘→接线齐全无遗漏"SOP 指令；2026-09-30 全仓孤儿深审实证（473 孤岛/情绪六成分仅 C2 有消费/技术指标 81% 零消费） |
