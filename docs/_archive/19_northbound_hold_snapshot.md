---
ttl: permanent
---

> **归档注记（2026-08-30）**：自 design_memos/implementation_plans 归档（候选核销批 greatwall_20260830——内容全量施工完毕核销，审计链保留，原位索引已同步标注）。
>
> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：doc_type=architecture_view · title=北向资金季度持仓快照 fetcher 施工计划 · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.1 · date=2026-08-16 · topic=northbound_hold_snapshot · scope=07_trading_decision_architecture · depends_on=- 15_data_feature_layer_spec - 62_business_registry_construction · related_modules=- src/zephyr/data/implementations/akshare_provider.py - src/zephyr/data/config/known_data_gaps.yaml

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-15/16 数据补充批（会话 AI-NORTH-001，13 笔提交，合并 87f50a5e3f）按本档计划落码北向季度持仓快照 fetcher——tushare hk_hold 接口已验证可用；tushare_provider 冲突手工合并后双能力并存。
>
> **最终成果**：季度末北向持仓快照可采集落库，替代日频断档的北向持仓数据。
>
> **未做事项及原因**：北向日频持仓未做——数据源层面永久断档（港交所停发日频持仓），非施工缺口，本档即该断档的替代方案。
>
> **复核补记（AI-NIGHT-001 复核 2026-08-19）**：fetcher 链路与登记实证一致（northbound_hold_fetcher.py 落码 + tasks.yaml northbound_hold_snapshot_refresh 登记 + schemas/categories/market_northbound_hold_snapshot.py + business_data_categories.yaml 品类 + data_asset_registry.yaml 条目 + known_data_gaps.yaml 三失效接口与撞码条目均在）。§6 方法论 MVP 边界（§6.3 个股增减持排名 + §6.5 季度净流入估算，"Δ持股数量 × 当季 VWAP"单公式 pandas 数十行）**未落码**（grep 实证无对应函数/脚本）——属 fetcher 落库后的分析层，外资行为因子未立项故未排期；南向季度快照按 §8/§9 裁定暂不采集。

> ## 结案报告回填（2026-08-28 代码实证复核）
> 原复核补记"§6.5 分析层未落码"已过时：src/zephyr/data/northbound_hold_analysis.py 已落码 estimate_quarterly_net_inflow（Δ持股×VWAP 季度净流入估算）；fetcher（northbound_hold_fetcher.py tushare hk_hold）+schema（market_northbound_hold_snapshot.py）+tasks.yaml northbound_hold_snapshot_refresh 全在位。
> **仍真实未完工**：南向季度快照（§8/§9 裁定不采集，非缺口）；外资行为因子未立项（下游非本档职责）。

# 北向资金季度持仓快照 fetcher 施工计划

> 本备忘是北向资金数据断档（2024-08-19 港交所停止公布日频）后的**替代数据源选型 + 季度持仓快照 fetcher 施工计划 + 外资行为分析方法论**。
> 性质：**施工计划文档**（§4.4 施工计划类），按"目标→现状→改动→验证→不做"组织。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)；数据资产注册表见 [62_business_registry_construction](62_business_registry_construction.md) §3 第 9 项（REG-DATAFLOW-001）。
> 关联：[15_data_feature_layer_spec](15_data_feature_layer_spec.md)（数据层总纲）｜ [known_data_gaps.yaml](../../../../src/zephyr/data/config/known_data_gaps.yaml)（数据缺口登记）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G19 北向资金季度持仓快照（数据地基层子项） |
| 创建 | 2026-08-10 |
| 优先级 | P2（非 P0——[check_algo_quality.py](../../../../scripts/governance/d5_architecture/checkers/check_algo_quality.py) 已确认 factor/strategy 无北向日频信号依赖，非数据黑洞） |
| 状态 | draft（方案已验证，待施工） |
| 上游 | [15_data_feature_layer_spec](15_data_feature_layer_spec.md)｜[62_business_registry_construction](62_business_registry_construction.md) |
| 下游 | 外资行为因子（待立项）｜[25_multifactor_strategy_detail](25_multifactor_strategy_detail.md)（潜在消费方） |

## 2. 背景

### 2.1 数据断档事件

- **2024-05-13**：沪深港通盘中实时交易信息停止披露（第一阶段）
- **2024-08-19**：沪深港通日终数据停止披露（第二阶段），北向资金日频净流入/净买入永久停发
- **调整后只剩**：每个交易日收市后公布成交总额/总笔数/ETF 成交额/前十大活跃证券；**每季度第 5 个沪深股通交易日**公布上季度末单只证券沪深股通投资者合计持有数量

### 2.2 已施工设施盘点（项目已有治理，通用规则 #11）

项目在数据断档治理上已先行（2026-08-12 按 [01 号规范](01_design_memo_management_spec.md) §5.2 引用纪律核验：只留稳定标识、不写行号）：

- [known_data_gaps.yaml](../../../../src/zephyr/data/config/known_data_gaps.yaml) 条目 `hk_connect_flow_source_discontinued`：标 `status: accepted`，root_cause 记明"港交所 2024-08-16 停止公布日频明细"
- [akshare_provider.py](../../../../src/zephyr/data/implementations/akshare_provider.py) `_fetch_hk_connect_flow`：docstring 记明"有效数据范围 2014-11-17 ~ 2024-08-16"，NaN 行自动过滤
- [check_algo_quality.py](../../../../scripts/governance/d5_architecture/checkers/check_algo_quality.py) 常量 `DEAD_DATA_SOURCES`：登记 `hk_connect_flow`/`hk_connect_daily`/`northbound_flow`/`northbound_capital` 四个死数据源（停发 2024-08-19），AST+正则双检测
- **factor/strategy 无实盘信号依赖北向日频净流入**（2026-08-10 排查确认）

### 2.3 核心问题

日频净流入永久消失，但**季度持仓快照仍可用**（交易所每季度发布）。问题转化为：如何获取季度快照 + 如何用季度快照做外资行为分析。

## 3. 现状（数据源实测）

### 3.1 akshare 1.18.75 实测（2026-08-10 三轮验证）

| 接口 | 状态 | 说明 |
|---|---|---|
| stock_hsgt_hist_em | ⚠️ 8-19 后净流入全 NaN | 仅领涨股/沪深300 有值 |
| stock_hsgt_individual_em | ✅ 仅历史 | 单股日频持股，~2024-08-16 |
| stock_hsgt_individual_detail_em | ✅ 仅历史 | 单股按机构明细，~2024-09-30 |
| stock_hsgt_hold_stock_em | ❌ 接口失效 | NoneType（本应是季度快照来源）|
| stock_hsgt_board_rank_em | ❌ 接口失效 | NoneType |
| stock_hsgt_stock_statistics_em | ❌ 接口失效 | NoneType |

> ⚠️ **2026-08-12 核验修正**：三条失效接口**尚未登记** [known_data_gaps.yaml](../../../../src/zephyr/data/config/known_data_gaps.yaml)（初稿声称"L158-210 已登记 `akshare_hsgt_hold_stock_em_broken` 等"为不实引用，实际不存在）——已列入 §9 开放问题，施工 fetcher 时同步补登记（gap_type=interface_broken）。

### 3.2 tushare hk_hold 实测（2026-08-10）

| 查询日期 | 北向(SH+SZ) | 南向(HK) | 说明 |
|---|---|---|---|
| 20240816（8-16 前）| 3337 | 791 | 完整 |
| 20240819（8-19 当天）| 0 | 792 | 北向归零 |
| 20260807（最新日频）| 0 | 955 | 北向仍无 |
| 20240930（季度末）| 3540 | 0 | **北向季度快照完整** |
| 20251231（季度末）| 3325 | 875 | **北向季度快照完整** |

**关键结论**：tushare `pro.hk_hold(trade_date=季度末)` 能返回完整北向持股快照，20251231 返回 3325 只，京东方A 27.6 亿股（与官方公布 27.05 亿吻合）。

## 4. 方案选型

### 4.1 候选方案

| 方案 | 来源 | 频率 | 成本 | 实测可行性 |
|---|---|---|---|---|
| A | 沪深交易所官网直抓 | 季度 | 免费 | 可行但工程量大（爬虫+反爬）|
| B | 东方财富网页 | 季度 | 免费 | akshare 接口已断，需自写爬虫 |
| C | tushare pro.hk_hold | 季度 | 已有 token | ✅ **实测可行** |
| D | Wind/Choice/iFind | 季度 | 付费 | 未测 |

### 4.2 裁定：走方案 C

理由：
1. 实测验证——季度末日期能返回完整北向持股，数据质量与官方一致
2. 项目已有 tushare 集成基础（token 已配，1.4.29）
3. 工程量最小——无需写爬虫、无需处理反爬
4. 方案 A/B 工程量大且不稳定（网页改版风险），方案 D 需付费

方案 A 作为 fallback（若 tushare 未来也断，再走交易所官网）。

## 5. 施工改动

### 5.1 新建 fetcher

在 tushare_provider 新增 `_fetch_northbound_hold_snapshot`：

- 接口：`pro.hk_hold(trade_date=季度末)`
- 过滤：`exchange in ('SH', 'SZ')`（仅北向，剔除 HK 南向）
- 字段映射：code→src_code, trade_date→trade_date, ts_code→ts_code, name→name, vol→hold_share, ratio→hold_ratio, exchange→exchange
- **设计刻意保持最小**：单接口、单表、全量覆盖写入（季度 3000-4000 行，无增量/无分页状态机），无反爬/无代理池/无重试编排——季度级任务失败下季度重跑即可

### 5.2 落表 schema

新建 `c1_market.northbound_hold_snapshot`（季度颗粒）：

| 列 | 类型 | 说明 |
|---|---|---|
| trade_date | Date | 季度末日期 |
| ts_code | String | 证券代码（带交易所后缀）|
| name | String | 证券名称 |
| hold_share | UInt64 | 持股数量（股）|
| hold_ratio | Float32 | 持股数量占 A 股百分比 |
| exchange | LowCardinality(String) | SH/SZ |
| data_source | LowCardinality(String) | tushare |
| ingested_at | DateTime | 入库时间（as-built：DateTime64(3,'UTC') DEFAULT now()，对齐家族 ingest 审计列精度惯例；列名从 memo） |

ORDER BY (ts_code, trade_date)，分区 toYYYYMM(trade_date)。
**as-built**：引擎 ReplacingMergeTree（全量覆盖幂等去重）；DDL-as-Code 真源 [market_northbound_hold_snapshot.py](../../../../schemas/categories/market_northbound_hold_snapshot.py)；品类登记 market_northbound_hold_snapshot（business_data_categories.yaml）。

### 5.3 调度

> **as-built（2026-08-15）**：挂既有 `nightly_financial` 时段（22:00 周一~五，与十大股东同层季度披露族）每日跑——fetcher 内 PIT 守卫（季度末+20 自然日才采新季度）使每日运行幂等无代价（全量 8 季度 ~16 次调用 ~3 万行，秒级），新季度发布当晚即采，优于 memo 原设想的季度单次（不新建 quarterly 调度层，9 档分层架构不扩散）。任务 task_id=northbound_hold_snapshot_refresh（tasks.yaml）。

- 频率：每季度第 6 个沪深股通交易日跑一次（官方第 5 个交易日发布，留 1 天缓冲）→ as-built 每日+PIT 守卫（见上）
- 回填：从 2024-09-30 开始按季度回填到最新（2024Q3/2024Q4/2025Q1/2025Q2/2025Q3/2025Q4）——**as-built 已完成回填**：8 季度（至 2026Q2）30331 行入库
- 历史补充：8-16 前的日频数据已在 hk_connect_flow 表，不重复采集

### 5.4 注册表登记

- [data_asset_registry.yaml](../../../../01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml) 登记 `northbound_hold_snapshot` 数据资产（62 号 §3 第 9 项 REG-DATAFLOW-001 下）
- [field_dictionary.yaml](../../../../01_policies_and_standards/_registry/catalogs/field_dictionary.yaml) 登记新字段（若 62 号 P2 字段字典施工已启动）
- [known_data_gaps.yaml](../../../../src/zephyr/data/config/known_data_gaps.yaml) 补登记三条 akshare 失效接口（§3.1 核验修正项）

## 6. 外资行为分析方法论

基于季度快照的外资行为分析（参考东证期货《北向资金跟踪系列》框架；2026 年行业实证：国信/招商证券每季度发布外资动向跟踪，按"长线稳定型/短线灵活型"拆解净流入——季度快照行为分析是行业标配做法）。

> **MVP 边界（2026-08-12 过度工程审查裁定）**：本节 6 小节是完整方法论地图，**首期只做 §6.3（个股增减持排名）+ §6.5（季度净流入估算）两项**——两者只需"Δ持股数量 × 当季 VWAP"一个公式，pandas 数十行可落地；§6.1/§6.2/§6.4 待外资行为因子立项后随需求演进，不提前施工。

### 6.1 持市值变化分解

```
Δ持股市值 = 主动增减仓 + 股价变动效应
主动增减仓 ≈ Δ持股数量 × 当季成交量加权均价(VWAP)
股价变动效应 ≈ 期末持股数 × Δ股价
```
主动增减仓才是外资真实意图，股价效应是被动浮盈浮亏。

### 6.2 行业超配/低配（存量结构）

```
超配比例 = 北向持有该行业市值占比 − 全A该行业市值占比
```

### 6.3 个股增减持排名（流量信号）——MVP ①

按"主动增减仓金额"排序，取 top 加仓/top 减仓。

### 6.4 板块切换能力评估（择时验证）

当季加仓行业 vs 下季该行业涨跌幅，算相关性。**注意样本量约束**：季度颗粒下有效样本每年仅 4 个观测点，2-3 年数据仅 8-12 个点，相关性结论统计功效弱——只做方向性参考，不做硬信号。

### 6.5 季度净流入估算（总量）——MVP ②

```
季度净流入 ≈ Σ_all_stocks(Δ持股数量 × 当季VWAP)
```
这是现在唯一能算出的"准北向净流入"（季度颗粒度）。行业对标：国信证券估算 2026Q2 北向净流入 ~2193 亿元（创单季新高），本公式落地后可与之交叉验证误差范围。

### 6.6 数据需求

季度末持股数量（本 fetcher）+ 当季个股 VWAP（项目已有）+ 申万行业分类（项目已有）+ 全 A 市值（项目已有）。

## 7. 验证

> **as-built 实证（2026-08-15 AI-NORTH-001 联调，拉取→落库→回读全链路）**：
> - 数据完整性：8 季度回读行数 3540/3602/3637/3788/3820/4014/4108/4065（2024Q3~2026Q2）；2026Q2 撞码 243 组经 code 自洽判别全救回、零误剔后 4065 只（官方 3958 只，差值=官方口径不含 ETF，见 §9）
> - 锚点核对：京东方A（000725.SZ）2025Q4 hold_share=2,760,058,253（27.6 亿股）与官方公布吻合；2026Q2 持股量 top10（京东方A/TCL科技/工商银行/三一重工/京沪高铁/紫金矿业/潍柴动力/农业银行/长江电力/招商银行）符合北向重仓常识
> - 字段质量：hold_share>0 且 hold_ratio∈[0,100] 违例 0 行（fetcher 内置校验拦截）
> - 与历史衔接：2024-08-16 前 hk_connect_flow 日频 vs 2024-09-30 季度快照 3540 只，量级连续无突变

- 数据完整性：每季度末日期返回 ~3300-4000 只北向持股（2026Q2 官方公布 3958 只，标的持续扩容），与官方公布 top10（宁德时代/中际旭创/北方华创等）核对
- 与历史衔接：2024-08-16 前 hk_connect_flow 日频数据 vs 2024-09-30 季度快照，持股数量应连续（无突变）
- 字段质量：hold_share > 0，hold_ratio ∈ [0, 100]

## 8. 不做什么

| 不做 | 理由 |
|---|---|
| 不试图恢复日频净流入 | 上游永久停发，不可逆 |
| 不在 factor/strategy 里依赖日频北向信号 | check_algo_quality 已标死数据源 |
| 不走方案 A 爬交易所官网 | 方案 C 已验证可行，工程量更小 |
| 不做外资行为因子开发（本备忘） | 因子开发单独立项，本备忘只到"数据就绪" |
| 不采集南向（HK）数据 | 本备忘聚焦北向；南向仍日频可用，另议 |
| 不做增量/断点续传/重试编排 | 季度全量覆盖即可（§5.1），复杂状态机是过度工程 |

## 9. 开放问题

| 问题 | 决策状态 |
|---|---|
| 落表用新表 northbound_hold_snapshot 还是扩展 hk_connect_flow | ✅ 已定：新表（颗粒度不同：日频 vs 季度）——2026-08-15 施工落地 c1_market.northbound_hold_snapshot |
| 是否同步采集南向季度快照 | 本备忘暂不做，待外资行为因子需要时再议 |
| 外资行为因子何时立项 | 待本 fetcher 落地 + 数据积累 2-3 个季度后评估 |
| tushare hk_hold 单次返回上限 4200 行——分页风险 | ✅ 已闭环（2026-08-15 施工）：exchange SH/SZ 拆分双调用，单侧 <2100 行，上限余量翻倍，构造性消除分页需求；20260630 实测 SH 2039/SZ 2269 原始行 |
| tushare hk_hold 2026Q2 响应 ts_code 撞码（施工联调新发现） | ✅ 已处置+监控：243 组撞码（50ETF 撞 603000.SH=人民网、中航成飛302132 撞 300132.SZ=青松股份），单证券查询同样撞码（无 API 修复路径）；probe 实证组内结构=真主行 code 自洽（int(code)+offset==ts_code 数字部，SH+510000/SZ+223000，name 为繁体真名）+入侵行（ETF/他股假码），恰好 1 行自洽率 100%；fetcher `_resolve_code_collisions` 判别救回真主行（判别失效兜底整组剔除，宁缺毋错）+warn 日志，2026Q2 全救回零误剔（4065 只）；已登记 known_data_gaps.yaml `tushare_hk_hold_2026q2_code_collision`（status=monitoring），上游修复后每日全量重拉自愈；2024Q3~2026Q1 七季度零撞码 |
| 三条 akshare 失效接口（§3.1）known_data_gaps.yaml 补登记 | ✅ 已闭环（2026-08-15 随施工完成）：`akshare_hsgt_{hold_stock,board_rank,stock_statistics}_em_broken` 三条 gap_type=interface_broken 登记 |

## 10. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-10 | 0.1.0 | 初稿 | 北向日频断档后，实测 akshare 失效/tushare 可行，建立季度快照 fetcher 施工计划 + 外资行为分析方法论 |
| 2026-08-11 | 0.1.1 | 文件被 git clean 误删后从对话历史重建 | #ARCH-GIT-CLEAN-GUARD-FIX：git alias 无法覆盖内置 clean 命令，文件物理删除 |
| 2026-08-12 | 0.2.0 | ①frontmatter version 与修订记录对齐（0.1.0→0.2.0，修复 0.1.1 未同步）；②§2.2 改「已施工设施盘点」并按 01 号 §5.2 引用纪律去行号（条目 id/常量名/方法名为稳定标识），修正 DEAD_DATA_SOURCES 键名与代码一致；③§3.1 修正不实引用——三条失效接口尚未登记 known_data_gaps，列入 §5.4/§9；④§6 方法论加 MVP 边界（首期只做 6.3+6.5，6.4 补样本量约束警示）；⑤§5.1 补最小设计声明、§8 补"不做增量/重试编排"（过度工程审查）；⑥§7 验证标准更新（2026Q2 官方 3958 只）、§9 分页风险升级（逼近 4200 上限）、§6 开头补行业实证（国信/招商季度跟踪） | 多轮审查：核验发现虚构引用与行号漂移，过度工程审查裁定 MVP 边界，2026Q2 行业数据入库（2026-08-12 三次并发回滚后重建） |
| 2026-08-15 | 0.2.1 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-08）；§2.2 引用纪律核验注记精简 | 实测表/方案裁定/开放问题零丢失，通读+自审零发现，不为压而压 |
| 2026-08-15 | 1.0.0 | 施工落地（AI-NORTH-001 task-19-northbound-snapshot）：①status draft→active；②§5 as-built 回填（独立 fetcher 文件/exchange 拆分/撞码剔除/ReplacingMergeTree/nightly_financial 每日+PIT 守卫/8 季度 30331 行回填完成）；③§7 验证实证回填（行数/锚点/质量零违例）；④§9 三开放问题闭环（新表裁定/分页风险构造性消除/三接口补登）+新增撞码发现处置记录；⑤src_code 映射未落列（§5.1 vs §5.2 冲突以表 schema 为准） | 施工完成按 01 号规范 §4.4 闭环；联调新发现上游撞码（243 组）整组剔除并登记 known_data_gaps |
| 2026-08-16 | 1.0.1 | 撞码处置策略升级（AI-NORTH-001 遗留项深挖）：`_drop_code_collisions`→`_resolve_code_collisions`——code 自洽判别救回真主行（SH+510000/SZ+223000==ts_code 数字部），判别失效兜底整组剔除（宁缺毋错底线不变）；§7 联调数据 3822→4065、§9 撞码条目同步 as-built（243 组全救回零误剔，gap 条目转 monitoring） | probe6-9 实证组内恰好 1 行自洽率 100%（真主行 name 繁体真名、入侵行 ETF/他股假码），修复后 2026Q2 不再缺 243 只 |
