---
ttl: permanent
doc_type: architecture_view
title: 数据与特征层规范
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.3"
date: 2026-08-15
topic: data_feature_layer_spec
scope: 07_trading_decision_architecture
---

> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：六要点中五项生产实证——① schemas/categories/ 103 个 DDL-as-Code schema + business_data_categories.yaml 三库注册 + apply_*_ddl.py 建表链；② miniQMT tick 双轨（轨 A miniqmt_provider + tick_subscriber + WAL，轨 B market_data VendorRegistry/FailoverManager）；③ PIT 双层（backtest/core/pit_manager.py 的 as_of_join/apply_embargo/pit_consistency_test/check_survivorship_bias 四函数实证 + data/pit_query.py）；⑤ 因子工程总纲（factor/ 治理流水线：factor_pool_manager/abs001_gate/ic_decay/decay_monitor + technical_indicators 7 文件）；⑥ 质量门控（gov_enforcement/rule_enforcement/quality_gate.py apply_quality_gate 实证 + cross_source_validator + known_data_gaps.yaml）。
>
> **最终成果**：数据与特征层规范 active v1.0.3 定稿（完整版丢失后按已施工代码重建）；"数据进来后怎么用"的统一规范落成。
>
> **未做事项及原因**：① 要点④特征仓库存储层未施工——轻量三层选型已定，但 schemas/categories/ 实证无特征值宽表，data_asset_registry 登记待 62 号 P1；② DQ_SPECS 八维 check_func 未绑定（data_governance/data_quality.py 注册表仅字符串、无 check_completeness 等实现实证，§6 待裁定项）；③ Embargo BDay→真交易日历未切换——依赖 calendar_event 表回填，而 calendar_event_refresh 任务未登记（tasks.yaml 实证，17 号 §6.6-2）；④ backtest 前置检查器绑定（BM-BT-02-D）未施工（暂缓：重评条件=首批回测因数据质量返工 ≥2 次）；⑤ 轨 A/轨 B 合流未施工（轨 B 无 miniQMT connector——维持双轨至多厂商需求真实出现的既定裁定）。

# 数据与特征层规范

> **性质**：spec / 工程规范（G01，地基层 1x 段位）。与 [64_data_source_download_spec](64_data_source_download_spec.md) 边界：**64 号管"数据怎么进来"（Provider/调度/落库/韧性），本文管"数据进来后怎么用"（schema 规范/PIT/特征/因子/质量门控）**。
> **现状**：六要点中五项已有生产级代码，why 散落在 103 个 schema docstring 与 #ARCH 裁定中——本文将其汇总成统一规范；**特征仓库（要点④）是唯一近乎空白的要点**，架构选型见 §3.4。
> **历史说明**：00_index 标本文"active v1.21.2"，磁盘仅存骨架——完整版曾丢失，本版按已施工代码重建为 1.0.0。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G01 数据与特征层规范 |
| 所属 | 作战地图 01/02 + 跨切 |
| 依赖 | 无（地基） |
| 对标 | WorldQuant Alpha 工厂 / Numerai 数据管线 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P0（地基，但可后置——策略定义不阻塞） |
| 状态 | ✅ active v1.0.3（五项已施工回填 why；特征仓库选型已定、实现待施工） |

## 2. 背景

**项目处境**：数据底座的"进"侧已由 64 号覆盖（15 数据源/154 任务/三库落库）；"用"侧设施在施工中自然生长——ClickHouse 103 表、PIT 双层实现、因子治理流水线、质量门控——但设计决策散落在各文件 docstring 与 #ARCH 裁定里，没有一份统一规范。AI 并发施工模式下，规范缺失 = 各对话各自发明口径。

**核心问题**：数据进来后，①表该怎么建（schema 规范）？②行情/财报怎么保证不用未来数据（PIT 铁律）？③特征怎么算/存/版本化？④因子从挖掘到上线的总纲是什么？⑤坏数据怎么挡在门外？

**约束条件**：单机 ClickHouse（无集群）、个人运维、AI 100% 写码——规范必须可机器校验（DDL-as-Code + 守卫），不能依赖人肉 review。

## 3. 决策：六要点规范

### 3.1 要点① ClickHouse schema 规范（已施工）

**体系：DDL-as-Code。** `schemas/categories/` 103 个 schema 文件是单表结构唯一真源（头部 `[MODIFY-GUARD] schema-change` + `human_only` 守卫）；SSoT 链：`business_data_categories.yaml`（113 category_id，三库 c0_meta/c1_market/c3_fundamental）→ `data/table_registry.py` → schemas/categories → `scripts/ch/apply_*_ddl.py` 执行建表 + `--verify` 一致性校验。

统一设计决策（why 汇总）：
1. **全库 ReplacingMergeTree 无版本列**——重复行自动合并，防重复导入事故；
2. **治理四列全表标配**——`data_source` / `quality_flag` / `ingest_ts` / `recorded_time`（审计与延迟建模）；
3. **`exchange` + `symbol_canonical` MATERIALIZED 派生列**——跨表 JOIN 身份统一（TRAE-082）；
4. **分区策略**：月分区 `toYYYYMM(trade_date)`——93 亿行 tick 规模下日分区 >8000 个 merge 过载；
5. **排序键按查询模式选型**——kline_daily `ORDER BY (symbol, trade_date)`（preload 全内存）；tick_data 5 字段 `(market_type, symbol, trade_date, timestamp, price)`，第 5 键 price 防同时刻不同价位成交被误合并（#ARCH-CH-002）；
6. **双时间戳**——`timestamp`（业务墙钟，Asia/Shanghai）+ `recorded_time`（本地接收），差值=端到端延迟供回测延迟建模（P0-1）；时区防线 #ARCH-CH-022；
7. **跳数索引补救**——tick 表 `idx_ts minmax + idx_symbol set(10000)`，补救 ORDER BY 前缀导致的单标的裁剪失效（#ARCH-CH-028）；
8. **复权 NULL 语义**——`adj_factor Nullable`，NULL=缺失 / 1=无复权（#ARCH-ADJFACTOR-NULL-001）；
9. **calc_mode 三态**——preload（日K 回测全内存）/ lazy（分钟线按需）/ replay（tick 逐条回放=实盘一致）。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-01-E | 原始数据缓存 | §3.1（落库原始表 schema：ReplacingMergeTree 保留原始行 + 治理四列 `ingest_ts`/`recorded_time` 审计） | production已建 |
| BM-SEL-01-F | 标准化行情产出 | §3.1（`exchange`+`symbol_canonical` MATERIALIZED 派生列身份统一、复权 NULL 语义）/ §3.6（质量门控四条单行级门禁产出带 quality_flag 的标准行情） | production已建 |
| BM-BT-03-B | Tick回放引擎 | §3.1 第 9 条 calc_mode 三态之 replay（tick 逐条回放=实盘一致） | production已建 |

### 3.2 要点② miniQMT tick 接入契约（已施工，双轨）

**轨 A 生产链路**（D_DATA 域，大规模运行）：`data/implementations/miniqmt_provider.py` 封装 xtquant 对接 40+ 表（单线程模型、方法内 import 防硬依赖）；`data/tick_subscriber.py` 常驻订阅——**tick 契约 15 字段**（trade_date/timestamp/recorded_time/symbol/market_type/price/volume/amount/direction/data_source/bid/ask 价量/quality_flag），callback 线程只 put_nowait → flush 线程批量 500 条 → WAL 先落盘再异步 drain CH（#ARCH-CH-013）；`redundant_source/` 主备容灾（PRIMARY→BACKUP 状态机 30 秒防抖切回 + TDX 备源）。`governance/data_governance/miniqmt_provider.py` 的 `MiniQmtQuoteProvider` 是另一类（Tick 18 字段含 5 档盘口），供实盘行情与 ex_core 共用 xtquant 连接——UTC→北京时间治本转换有专门事故教训注释。
**轨 B 厂商抽象**（D_MKT_DATA 域，MOD-MKT-001~006）：VendorRegistry + Connector 6 态状态机 + FailoverManager（PRIORITY/ROUND_ROBIN 双策略、切换原子性、ALL_FAILED 兜底）——为将来多厂商统一定价/切换准备的干净抽象。
**轨 B 自动加载契约（BM-SEL-01-D，production，MOD-MKT-005 autoload）**：启动时自动加载行情模块——**启动加载 SLA <10s 完成全部模块加载**；流程=配置读取 → 模块发现（VendorRegistry 扫描已注册 connector）→ 依赖注入 → 实例化（Connector 状态机置初态）；配置热刷新生效路径=配置管理写回 → autoload 监听刷新 → 重建 connector 实例 → 路由规则热更新（不中断在途订阅）；自动加载失败→降级手动加载+告警。**与 64 号 §9.2 消歧**：本文 autoload 管**模块级**加载/配置热刷新（进程启动与配置变更时"装什么"），64 号 §9.2 冗余源热切换管**运行态进程级**主备源零中断切换（tick 推送"跑着换"）——分工不重叠。
why 双轨：轨 A 在 xtquant 单线程约束下求生（任务制下载+常驻订阅+WAL），轨 B 是 A 类基础设施先建。**缺口**：两轨未合流（轨 B 无 miniQMT connector 实现）——登记 §7。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-01-A | 供应商注册与适配器 | §3.2 轨B（VendorRegistry 厂商注册 + Connector 抽象） | production已建 |
| BM-SEL-01-B | 行情连接器管理 | §3.2 轨B（Connector 6 态状态机） | production已建 |
| BM-SEL-01-C | 故障切换与Failover | §3.2（轨B FailoverManager PRIORITY/ROUND_ROBIN 双策略+ALL_FAILED 兜底；轨A redundant_source 主备容灾 30 秒防抖切回） | production已建 |

### 3.3 要点③ PIT 铁律（已施工，双层）

**铁律表述**：任何决策时点 T 可见的数据，必须满足 `available_time ≤ T`（财报用公告日，行情用交易日）；标签与决策时点之间必须隔 Embargo 窗口。2026 年 MLOps 共识（Feast point-in-time joins 一脉）：PIT 正确性是训练-服务一致性的不可协商项——本铁律与之同构。
- **回测层（pandas 平面）** `backtest/core/pit_manager.py`：`as_of_join()`（泄漏防护 + 版本对齐取 available_time 最大且≤T 者，模拟 Feature Store 语义）+ `apply_embargo()`（默认 5 个交易日，BDay 近似）+ `pit_consistency_test()`（训练 vs 回测平面偏差>1% 告警）+ `check_survivorship_bias()`（退市股覆盖率）；
- **数据层（ClickHouse SQL 平面）** `data/pit_query.py`：9 张财报表白名单（非白名单直接报错防越权），`LIMIT 1 BY symbol, report_period` 利用"保留全版本"的物理设计实现 AS OF JOIN 语义；`survivorship_universe()` 用 stock_list SCD-2 时点过滤含未来退市股；
- **因子评估层**：`factor/core/evaluation/backtest.py` 自动注入 FINAL 去重、前向收益 shift 仅限评估、禁用 ingested_at 只用 trade_date 截面对齐（INV-004）。
why 双层：回测在 pandas 里跑（可单测、不连库），取数在 SQL 里跑（性能）——两层语义显式对齐（pit_query.py docstring 17-31 声明映射关系）。**缺口**：行情表无 available_at 列（多版本对齐仅财报可用，行情靠 ReplacingMergeTree FINAL）；Embargo 用 BDay 近似非真交易日历——登记 §7。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-BT-02-E | 幸存者偏差防护 | §3.3（`check_survivorship_bias()` 退市股覆盖率 + `survivorship_universe()` stock_list SCD-2 时点过滤含未来退市股） | design待施工 |
| BM-BT-04-A | PIT三公理与AS OF JOIN | §3.3（铁律表述 + `as_of_join()` 泄漏防护/版本对齐 + `pit_query.py` `LIMIT 1 BY` AS OF JOIN 语义） | production已建 |
| BM-BT-04-B | Embargo期管理 | §3.3（`apply_embargo()` 默认 5 个交易日 BDay 近似；BDay→真交易日历待决策登记 §7） | production已建 |

### 3.4 要点④ 特征仓库架构（选型已定，实现待施工）

**已施工的相关件**：FactorDAG（`factor/core/factor_dag/dag.py`：pydantic 节点/环检测/Kahn 分层，从 FactorMeta.dependencies 自动建图）+ 双执行器（ThreadPool 层内并行 / ProcessPool 绕 GIL）+ `FactorBase.incremental_compute`（盘中只重算新增点拼接缓存）+ FactorSignal 流转契约（z-score+rank_pct+NaN 处理，批量缓冲输出给 D_SIGNAL/D_RISK/D_PF_CORE）。

**FactorSignal NaN 填充裁定（BM-BT-03-D，design→口径已定）**：①**前值填充（ffill）为默认策略**；②**禁用向后填充与插值**——backfill/线性插值都引入未来数据=前视偏差（违反 §3.3 PIT 铁律），横截面均值填充稀释截面排序信息，一并禁用；③**指标预热期剔除**——窗口期内 NaN（如 MA60 前 59 点）不填充、整段剔除出回测样本，防预热期伪信号污染 IS 段指标。why 登记于此而非另建服务：NaN 语义是 FactorSignal 流转契约的一部分，独立服务化（真源 BT-26 services/nan_processor.py planned）暂无必要；重评条件=出现消费方要求差异化填充策略（如事件驱动策略盘口快照 NaN 语义）时再独立成服务。

**选型裁定（个人单机轻量路线）**：不引入 Feast/Tecton 等 Feature Store 框架（64 号 §2.3 已排除；2026 年行情：Feast/Tecton 规模化部署需 4-6 FTE + 月 $15k-40k 云成本，对单人是纯过度工程），采用三层轻量架构：
1. **计算层**——FactorDAG + incremental_compute（已施工）；
2. **存储层**——特征值落 ClickHouse 宽表（仿 technical_indicator 表单表+period 列模式，该模式已验证可行）；因子元数据/版本/衰减状态登记 factor_registry.yaml（已施工，111 条目）；
3. **版本层**——Semantic Versioning + git commit 充 immutable（62 号 §4 原则 9 已定），不建独立特征版本服务。
why 轻量：个人系统无"离线/在线特征一致性"的多团队痛点（计算与消费同代码库），Feast 的 registry/serving 层全是多余运维面；真正需要的是"特征值可复用、可审计"，一张 CH 宽表 + 注册表即可。**实现标"待施工"**（data_asset_registry 登记载体待 62 号 P1）。

### 3.5 要点⑤ 因子工程总纲（已施工，框架最完整）

**流水线总纲**：因子定义（FactorBase/FactorMeta，装饰器注册 FactorRegistry）→ IC 评估（`evaluation/backtest.py` → EvaluationResult：ic_mean/ir/oos_positive_rate/is_overfitted）→ 三级判定（优秀/合格/淘汰）+ 5 分位分层多空 → **ABS001 上线四门禁**（|IC|≥0.03、IR≥0.5、OOS 正率≥0.5、非过拟合，阈值读 governance/_config.yaml 不硬编码）→ 六步治理流（research→…→grayscale→production，FactorGovernanceEngine 编排）→ 灰度阶梯 → production。
**衰减监控**：`analysis/ic_decay.py`（lag 1..20 IC 衰减曲线+线性插值半衰期）+ `decay_monitor.py`（半衰期<10 判 decaying）→ 状态回写 factor_registry 的 decay_state 字段。
**过拟合/冗余**：OOS/IS 比率检测 + correlation_dedup 相关矩阵去重 + factor_attribution 按月/行业归因。
why 这套总纲：因子是消耗品——IC 衰减是必然，治理流水线保证"新因子持续进、失效因子体面退"；注册表 40+ 字段（pit_policy/decay_halflife/drift_psi/null_rate…）让每个因子的健康状态可机器查询，供 AI 并发施工时读真源而非问人。

### 3.6 要点⑥ 数据质量门控（已施工，多层）

1. **写入路径轻量门（主防线）**：`gov_enforcement/rule_enforcement/quality_gate.py apply_quality_gate()`——四条单行级门禁（OHLC 结构/涨跌幅≤20%/振幅≤30%/0<adj_factor≤1000）；异常行 quality_flag=0 **保留审计不丢弃**（#ARCH-CH-021 P0-4）；
2. **领域抽象门**：DataQualityGate ABC——quality_score<0.7 必须抛错、停牌 MUST 显式标记禁静默跳过、每种 failure 给 recovery_hint（RETRY/SKIP_SYMBOL/SWITCH_SOURCE/HALT）；
3. **DQ 八维体系**：完整性/准确性/异常/一致性/新鲜度/时效/唯一/有效，方向感知打分；
4. **配套**：cross_source_validator（主备源交叉校验落 cross_validation_log 表）/ known_data_gaps.yaml（已知缺口注册表 #ARCH-CH-029）/ backtest 前置 data_quality_checker。
5. **backtest 前置检查器绑定（BM-BT-02-D，design）**：回测数据加载后自动检查的前置门——定位是回测域的**消费引用方**而非新建检查器：检查逻辑复用本要点第 1 条单行级门禁的批次版 + DQ_SPECS 八维 check_func 既有登记（§6 待裁定项实现绑定后自动生效），backtest 侧只做"加载后调用 → 按 quality_flag 过滤 → 阻断/告警报告"。阈值/规则绑定：单标的缺失率 >5% 阻断、截面缺失率 >1% 告警；异常检测规则与写入路径四条门禁同口径（OHLC 结构/涨跌幅≤20%/振幅≤30%/adj_factor 区间）。暂缓理由：数据层门控已覆盖写入路径，回测前置是二道防线；重评条件=首批策略回测因数据质量问题致结论返工 ≥2 次。
why "保留不丢弃"：坏行也是证据——丢弃会让缺口不可见，quality_flag=0 保留后既可过滤又可审计缺口分布。

## 4. 考虑过的替代方案

| 方案 | 拒绝理由 |
|---|---|
| Feast/Tecton Feature Store | 拒绝——64 号 §2.3 已排除；registry/serving 层对个人是多余运维面（2026 年仍需 4-6 FTE），CH 宽表+factor_registry 等价 |
| 行情表也加 available_at 多版本 | 暂缓——行情无"修订重发"语义（不同于财报），ReplacingMergeTree FINAL 去重已够；若未来接入多源行情对账再评 |
| 坏数据直接丢弃 | 拒绝——见 §3.6 why |
| data_eng 域承载特征管道编排 | 暂缓——该域当前为空壳（7 个 __init__），管道编排并入 factor 治理流水线，data_eng 待有真实 ETL 需求再启用 |

## 5. 上限定义

**系统上限**：DDL-as-Code + PIT 双层 + 轻量特征三层 + 因子治理流水线 + 质量多层门控，对个人单机已是上限。**演进路径**：特征存储层（CH 宽表）施工 → data_asset_registry 登记 → 衰减监控调度化（当前 monitor_decay 是按需函数）。**为何是上限**：机构级 Feature Store（在线 serving/多团队共享/特征市场）超出单人单库硬边界；因子工厂对标 WorldQuant 的部分（众包 alpha 挖掘）不适用单人模式。

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| #ARCH-CH-009 ingest_ts 版本列统一（蓝图 §4.0 vs §4.2 DDL 矛盾） | 以可执行 DDL 为准运行中 | 下次 schema 大修时裁定 |
| L2 权限缺失降级（#ARCH-DATA-014） | miniQMT L2 权限未开通 | 权限开通后启用 l2_tick 全字段 |
| 衰减监控调度化（定时任务） | 按需函数当前够用 | 因子数 >50 或周复盘需要衰减报表时 |
| DQ_SPECS 八维 check_func 实现绑定 | 注册表先于实现 | 数据质量月报需求出现时 |

## 7. 待定问题（G01 六要点逐项裁定）

- [x] ① **ClickHouse schema 规范**——✅ 已施工已汇总（§3.1，9 条统一决策）。
- [x] ② **miniQMT tick 接入契约**——✅ 已施工（§3.2）。⚠️ **待决策**：轨 A/轨 B 合流时机（轨 B 无 miniQMT connector）——建议维持双轨至多厂商需求真实出现。
- [x] ③ **PIT 铁律**——✅ 双层已施工（§3.3）。⚠️ 待决策：Embargo 的 BDay 近似是否换真交易日历（接 hk_trade_calendar 同族 calendar_event）；pit_manager.py 零单测需补。
- [x] ④ **特征仓库架构**——🔨 轻量三层选型已定（§3.4），存储层+data_asset_registry **待施工**。
- [x] ⑤ **因子工程总纲**——✅ 已施工（§3.5）。⚠️ 内容对齐缺口：factor_registry 111 条目 vs 代码实装因子数量悬殊，Step1-3 回填归 62 号。
- [x] ⑥ **数据质量门控**——✅ 已施工（§3.6）。

**代码层新发现问题**：
1. D_DATA 域超容（181/150 模块）——域拆分议题登记 architecture_issue_registry（越界，不越界改）。
2. data_eng 域为空壳（7 个 __init__ 被标 production）——域文档状态需修正（越界登记）。
3. 特征值无持久化表——与要点④互为因果，存储层施工时一并解决。
4. **00_index 同步（越界登记）**：00_index 标本文"active v1.21.2"，与本版 1.0.0 不一致，需同步（详见 33 号 §7 新发现 7 的统一登记）。

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G01
- [64_data_source_download_spec](64_data_source_download_spec.md)（边界：64=怎么进来，本文=进来后怎么用）
- [62_business_registry_construction](62_business_registry_construction.md)（factor_registry/data_asset_registry 载体）
- 域文档：11_d_data / 12_d_data_eng / 23_d_mkt_data / 46_d_factor（模块清单权威来源）
- 代码：`schemas/categories/`（103 表）、`src/zephyr/data/tick_subscriber.py`、`src/zephyr/backtest/core/pit_manager.py`、`src/zephyr/data/pit_query.py`、`src/zephyr/factor/`（governance/analysis/core）
- battle_map_01_research_incubation / battle_map_02_model_training（状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G01 讨论要点占位，待讨论填空 |
| 2026-08-12 | 1.0.0 | 骨架→active：六要点全部回填（五项已施工汇总 why + 特征仓库轻量三层选型）；登记双轨合流等 4 项新发现 | 完整版（v1.21.2）曾丢失，按已施工代码重建；设计决策汇总成统一规范供 AI 并发施工读真源；特征仓库不擅自施工，选型定后人裁定 |
| 2026-08-12 | 1.0.1 | 作战地图全覆盖补丁——闭合 BM-BT-02-D（§3.6 第 5 条 backtest 前置检查器绑定 DQ 八维）、BM-BT-03-D（§3.4 FactorSignal NaN 填充裁定：ffill 默认/禁向后插值/预热期剔除）、BM-SEL-01-D（§3.2 轨B autoload 契约+与 64 §9.2 消歧） | 数据/选股域 3 环节补丁：补契约与裁定口径，不新施工 |
| 2026-08-12 | 1.0.2 | 作战地图环节映射补强——锚定 BM-SEL-01-A/01-B/01-C/01-E/01-F、BM-BT-02-E/03-B/04-A/04-B（§3.1/§3.2/§3.3 末各增映射块） | 语义已覆盖但正文未显式编号的环节锚定到承载小节，实现环节级可追溯；不改既有正文 |
| 2026-08-15 | 1.0.3 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-08）；§1 状态版本漂移修复（v1.0.0→v1.0.3 同步） | 六要点规范表格化已充分、待裁定/待定问题无冗余，通读+自审零发现，不为压而压 |

---

## 附录：数据资产消费登记（63 号审查批次 B+C，2026-08-20 登记）

> 来源：[63_data_utilization_audit](63_data_utilization_audit.md) §6.2 批次 B（估值/预期行）+ 批次 C（行业分类补充/个股指标行）/ §7.2 第二波——消费层文档覆盖缺口施工。登记口径：每表 3-5 行（表名/内容/潜在消费场景/当前状态）；按收缩方案合并为本节表格汇总。当前状态统一为**未消费登记**（unconsumed registration）：数据已落库、代码层或有引用，但本消费方文档尚未将其作为显式数据源描述；后续实际消费接线后，按 63 号 §7.0.1 六字段模板改写为正文小节并更新状态。引用计数为 2026-08-20 工作区复扫（src/zephyr *.py，词边界匹配）。本篇为数据/因子工程总纲（63 号 §7.0.2 优先级 P2"数据源清单"中立描述），登记不涉及消费语义裁定。

| 表名 | 内容 | 潜在消费场景 | 当前状态 |
|---|---|---|---|
| `industry_class_suppl`（行业分类补充） | 行业分类补充映射（官方分类之外的补充口径） | 行业分类体系补全：factor_registry 行业中性化/行业偏离裁剪的行业归属补充真源候选 | **未消费登记**（2026-08-20 实证：src/zephyr 引用 6 次，代码活跃；消费语义未落本文档） |
| `stock_valuation`（个股估值） | 个股估值指标（PE/PB/PS/市值等日频快照） | 估值因子原料：价值类因子（BP/EP/SP）计算输入，因子工程总纲估值数据源登记 | **未消费登记·待 Q8 裁定**（2026-08-20 实证：src/zephyr 零命中，与 63 号 §10.2 Q8"代码零引用但规划已登记"口径一致；仅 schemas DDL/采集配置在位；Q8 裁定 dormant 则转"待启用"） |
| `analyst_forecast`（分析师预期） | 分析师盈利预测/评级/目标价 | 预期类因子原料：一致预期变化/预期差（与 26 号 SUE 同源语义）因子计算输入；[forage.ai 2026](https://forage.ai/blog/alternative-data-for-hedge-funds/)：另类数据核心在 nowcasting（即时预测） | **未消费登记**（2026-08-20 实证：src/zephyr 引用 5 次（akshare_provider.py），代码活跃；消费语义未落本文档） |
| `stock_indicator`（个股指标） | 个股综合技术指标/财务指标快照 | 指标宽表原料：因子工程预计算指标的直接读取层（与 16 号技术指标 machinery 产出关系待厘清，接入时标注派生/原生边界） | **未消费登记**（2026-08-20 实证：src/zephyr 引用 8 次，代码活跃；消费语义未落本文档） |
