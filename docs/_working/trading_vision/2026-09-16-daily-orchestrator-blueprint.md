---
ttl: task_bound
completes_when: Owner 对 §八 待批准点逐条裁定；蓝图获批后刀1（一库）/刀2（一闸）可挂单开工；§九自裁记录无 Owner 否决。
---

# 日度编排器施工蓝图 v1（BT-P1-031 本体——交易决策链的心脏）

> 2026-09-16，st-orchbp-20260916。**只起草不动工**——本文=蓝图，施工待 Owner 批准（BT-P1-031 plan_note 明确"编排器设计须先落蓝图过审"）。
> 底稿=骨架覆盖审计报告 §七 基建最小方案（[`2026-09-16-skeleton-coverage-audit.md`](2026-09-16-skeleton-coverage-audit.md)）；愿景语境=[`2026-09-16-owner-vision-system-mapping.md`](2026-09-16-owner-vision-system-mapping.md)。
> 诚实条款：本文引用的既有模块/表全部经 grep 核实在盘（§十引用清单）；设计不了的标"待讨论"，禁硬编。

## 一、架构定位

1. **日度编排器 = T2 每日晨判的执行者，持有"今日不交易权"**。审计 §六 R2/R3：拍板体不存在、"今日不交易"语义散在三处（C1 预算带 0% / sit_out_list 禁做清单 / kill_switch 熔断）无日度拍板与留痕——编排器把三源合成收拢为**一行可审计的日度决策快照**。
2. **它是调度器不是策略**：只串联既有件（L1 regime 快照 / L2-L5 各层门与模块），**不新增任何判断逻辑**——判断归各层模型（regime 归 MOD-REGIME-001、预算带归 TDM-F-C1 语义、熔断归 kill_switch/drawdown_state_machine、包归属归 state_matrix 配置真源）。编排器只做三件事：**读齐 → 合成拍板 → 落库分发**。
3. 与最接近件 `daily_warroom_pipeline`（MOD-PLAN-018，testing，仓库内零调用方）的关系：**复用其骨架**（两段编排 / fail-open / 幂等口径 / 次交易日解析），不改造其职责（它继续只管 scenario 样本积累）；编排器是**并列新增的拍板体**，非其子类。避免把"零调用"债务升级成"零调用+新职责"。
4. 决策权边界：编排器**不填** state_matrix 的 `pending-owner-adoption` 格子（Owner 资金分配门位，AI 禁自填）；空格子=该段无包可启（安全侧），并在快照中标注"包选择残缺"催 Owner 采纳。
5. 语义澄清（自裁）：**"今日不交易" = 禁新开仓，≠ 清仓指令**。distribution 段 TDM 口径="存量由 X 流信号驱动离场"（state_matrix TDM-F-C1×distribution 格注记）；存量保命件（kill_switch / drawdown_state_machine / ashare_stop_loss_engine）是横切持续件，**独立于编排器运行**——编排器缺席/休眠不阻塞保命。这是全部降级设计的安全底座。

## 二、每日流程设计（T2 晨判序列，按时间轴）

> 节拍语义澄清（对齐审计方法注记 §一.2）：T2 拍判据在 T4 盘后计算（盘后算、盘前用）。机械时点上，编排器拍板发生在**盘后批数据齐之后**（daily_kline 入库 SUCCESS 唤醒），拍板的**生效日=次交易日**（target_date）。"晨判"是业务语义，机械时点=前一交易日盘后批尾——晚到即晚拍，开盘前无决策=安全侧（§六）。

| 步 | 动作 | 读什么（全部已核实在盘） | 产出 |
|---|---|---|---|
| S1 | **查交易日历** | `c1_market.trade_calendar`（is_open=1 开市日行集；休市=查无此行）；次交易日解析=`is_open=1 且 cal_date > 数据日 LIMIT 1`（warroom 同款口径） | target_date；查无→走 §三 日历降级分叉 |
| S2 | **读 regime 昨收状态** | `c1_backtest.regime_snapshot_history` 最新 PIT 行（trade_date≤数据日；7 维概率/dominant/confidence_signal/risk_signal/shrinkage；读法对齐 `pf_alloc/allocation_inputs.py` SQL_LATEST_REGIME_SNAPSHOT 先例） | 六段市场状态+谨慎度输入 |
| S3 | **读各层参与门快照** | 一闸只读采集（§四.2；L1 快照/L2 放行档/L3 开关表/L4 预算带与熔断/L5 笼子与 T+1 资格），零判定改动 | gate_snapshot 载荷 |
| S4 | **策略包选择** | 对接 S-OWNER-002 切换器接口（§五.2）：查 `config/trading_decision_map.yaml` state_matrix 已填格（mounted sleeves）→{启用包集合, 各包上限系数}；pending-owner-adoption 格=该段无包+标注残缺 | PackageDecision |
| S5 | **定总仓位上限 + "今日不交易"判定** | E-L1 总闸语义（TDM-E-L1：消费 RegimeSnapshot 概率=谨慎度→当日总仓位上限；`pf_alloc/core/vol_target_allocator.py` 波动率目标化系数）× TDM-F-C1 六段预算带带内插值（capitulation 0-10% / accumulation 20-30% / ignition 30-50% / expansion 50-70% / euphoria ≤30% 只卖不买 / distribution 0% 空仓）；过渡带（最大隶属度<60%）×0.5-0.7；总仓位=min(预算带, 60% 硬顶)（审计 §五 L4 口径）；no_trade 三源合成=预算带 0% ∨ kill_switch 熔断 active ∨ regime 快照缺席 | position_cap + no_trade(+reason 枚举) |
| S6 | **产出当日决策快照（一库）** | 写 `c1_backtest.decision_daily`（§四.1 schema 草案）；业务日级幂等 marker（先拍板先占，重拍=新 run_id 追加） | 决策快照行=当日唯一放行凭证 |
| S7 | **分发到执行面** | 播报前缀（对齐 REGIME_SNAPSHOT_PREFIX 先例，日志/告警面可 grep）；下游=一图仪表盘+留痕；**首版不驱动执行单**（BT-P2-055 未在，生产流转=Owner 门位，§五.4） | 分发完成 |

**T3 盘中挂点（只定义接口，不展开）**：`intraday_revoke(reason)`——kill_switch/熔断触发时对当日决策追加**修订行**（新 run_id，no_trade=1，原文不变，MergeTree 只增不改）；盘中重判/盘中调度=明确不做（对齐 warroom 自述边界）。修订权限归属=待 Owner 批准点 §八-7。

**T4 盘后挂点（只定义接口，不展开）**：`postmarket_reconcile(data_date)`——当日决策 vs 实际的核对留痕（对接既有 plan_deviation_monitor 口径），供逐层归因链消费。首版仅签名与占位。

## 三、事件触发设计（宪法 §9.3：禁 cron/Timer/sleep-loop，必须事件触发）

**触发源：daily_kline SUCCESS 唤醒（照 regime_snapshot_history 先例，血管已通）。**

1. 机制真源=`src/zephyr/strategy_pipeline/pipeline_events.py`（MOD-BT-190）：DataScheduler task_completed 轻钩子（`wire_data_scheduler()` → `scheduler.subscribe("task_completed", ...)`）；日件唤醒任务子串=`SIM_DAILY_WAKE_TASKS = ("daily_kline", "kline_daily", "kline_index")`。
2. **编排器排第三棒**：同一 daily_kline SUCCESS 唤醒点上的既有顺序=regime 快照刷新（先，pf_alloc 读其口径）→ pf_alloc 日分配（`maybe_emit_pf_alloc_daily` → 子进程 `-m zephyr.pf_alloc.allocation_orchestrator`，PF_ALLOC_TIMEOUT_S=900）→ **编排器（新增）**。排第三的理由：编排器 S2 步消费 regime 快照、S3 步消费 alloc_budget_daily 当日 run——两者缺席即触发降级矩阵（§六），排后使正常路径零降级。
3. **不建新事件 kind**（自裁，对齐 REGIME_SNAPSHOT_KIND 先例"幂等键前缀+业务日级 marker，不建事件 kind=零新机制"）：编排器 handler 以业务日级 date-marker 做幂等闸（同日重唤醒直接跳过）；轻 kind 语义（有界耗时/分钟级）对齐 LIGHT_KINDS 既有判据；子进程隔离+超时边界照 pf_alloc_daily 模式（超时视同失败进重试计数，不挂住调度器线程）。
4. 上游唤醒的其它分叉：kline_daily/kline_index 唤醒同样有效（子串匹配已含）；非交易日无 daily_kline SUCCESS=自然休眠（**不开闹钟**——日历只作 S1 粗筛与告警哨兵，不作唤醒源，避免"日历说开市而数据永不来"的挂起态）。

**失败安全：上游缺席时的降级=今天不出决策（安全侧）。**

- 拍板三前置（regime 快照新鲜 ∧ alloc_budget_daily 当日 run 在 ∧ 日历可证）任一不满足 → 不出常规决策：落一行 `no_trade=1` 的**降级快照**（reason 枚举如实），禁新开仓；存量交横切保命件（§一.5）。
- 编排器自身异常 → fail-open（warroom 骨架既有口径）：不留半行、告警出声（播报前缀），下游无凭证=各自保守侧。
- **为什么"不出决策=安全侧"成立**：执行面首版不接（S7 只留痕+仪表盘）；未来执行面接入时，决策快照行=放行凭证（对齐 alloc_budget_daily.adjudication_id 下单链凭证先例）——**无快照行=无新开仓令**，机会成本单向可控（§六）。

**交易日历年度续期机制（依赖检查结论：表预载至 2026-12-31，2027-01-01 起查无此行与休市不可区分——必须设计续期）。**

- 现状事实：`trade_calendar_refresh` 任务（`src/zephyr/data/config/tasks.yaml`，monthly_static 全量重建，baostock 主源+akshare 新浪 fallback）每交易日只存 `is_open=1` 行、含 `pretrade_date`；新浪源年度日历通常**每年 12 月底才发布次年**——2026-12-01 的月刷也补不出 2027 行，续期天然滞后，不能靠现有月刷兜底。
- 设计三层：
  1. **哨兵（编排器流程内，出声不续）**：S1 解析时若 `max(cal_date) < target_date`（或表尾距 target < 10 个交易日提前量），发日历续期告警（播报前缀+告警面）。续期动作归属数据域既有任务链，编排器不代拉网络（域边界）。
  2. **交叉验证与降级运行（data_proven 模式）**：第二真源=`zephyr.data.trading_calendar`（XSHG 本地日历，exchange_calendars 纯本地计算不依赖 DB，production/stable）；**业务日终极真源=行情最新入库日**（pipeline_events 既有口径）。日历查无此行时：若当日存在 daily_kline SUCCESS 记录 → 判开市（calendar_source=data_proven，degraded=1）；查无且无数据 → 判休市休眠。XSHG 本地日历作旁证（三方一致才记 calendar_source=trade_calendar 正常态）。
  3. **急修通道（人工）**：连续 N 日 data_proven 运行 → 升级告警（N 值=待 Owner 批准点 §八-4），Owner 批准后人工触发日历全量刷新或临时注入。

## 四、一库一闸设计

### 4.1 一库：日度决策快照表 `c1_backtest.decision_daily`（schema 草案）

- 选型（自裁，§八-5 留 Owner 确认）：**新增 ClickHouse 表**而非挂 prediction_log。理由：①"谁在哪个格子拍了板"=留痕真源，需结构化列供一图 SQL 直查与 no_trade 误报率统计；②与 `alloc_budget_daily`/`regime_snapshot_history` 同库（c1_backtest）便于同日对账；③prediction_log（SQLite，`reporting/prediction_log_writer.py`）payload_json 形态不利结构化聚合。是否**同时**落 prediction_log decision 族行（复用其幂等 UNIQUE 键与现成通道）=小批准点。
- DDL-as-Code 落点：`schemas/categories/decision_daily.py`（照 alloc_budget_daily.py 模式：TABLE_NAME/DDL/列清单唯一真源；模块头带 [CREATION-TOKEN]；施工时走 depgraph 登记 + `scripts/ch/verify_schema_truth.py` 漂移校验）。

```sql
CREATE TABLE IF NOT EXISTS c1_backtest.decision_daily
(
    ingest_ts          DateTime64(3,'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC,DB侧生成;RULE-SCHEMA-TZ)',
    run_id             String COMMENT '决策 run 标识 decision-<trade_date>-<uuid6>(重拍=新 run_id 追加,修订行同制)',
    trade_date         Date   COMMENT '拍板生效日=次交易日(target_date)',
    asof_data_date     Date   COMMENT '拍板时点所见数据日(PIT:决策只用≤此日信息)',
    market_state       LowCardinality(String) COMMENT '六段状态(capitulation/accumulation/ignition/expansion/euphoria/distribution)',
    state_confidence   Float64 COMMENT 'dominant 态概率(来自 regime_snapshot_history)',
    budget_band_low    Float64 COMMENT '六段预算带下缘(TDM-F-C1)',
    budget_band_high   Float64 COMMENT '六段预算带上缘',
    position_cap       Float64 COMMENT '当日总仓位上限=E-L1 总闸输出,min(预算带插值,60%硬顶)',
    package_set_json   String COMMENT '启用包集合+各包上限系数(S-OWNER-002 输出)+state_matrix 格子溯源',
    gate_snapshot_json String COMMENT 'L1-L5 五层门态只读采集(一闸,含 absent 标记)',
    no_trade           UInt8  COMMENT '0=可交易(限仓) 1=今日不交易(禁新开仓,≠清仓)',
    no_trade_reason    LowCardinality(String) COMMENT '枚举:distribution_band/kill_switch/regime_missing/budget_run_missing/calendar_ambiguous/transition_band(带 reason 明文于 note)',
    sit_out_list_json  String COMMENT '禁做清单快照(plan_engine/sit_out_list.py 三源合成)',
    calendar_source    LowCardinality(String) COMMENT 'trade_calendar|xshg_local|data_proven(日历真源降级轨迹)',
    degraded           UInt8  COMMENT '0=正常 1=降级运行(降级矩阵任一分支触发)',
    degrade_reasons    String COMMENT '降级原因清单(分号分隔,空=无)',
    note               String COMMENT '备注/残缺标注(如 pending-owner-adoption 催采纳)',
    schema_version     LowCardinality(String) COMMENT '行契约版本',
    INDEX idx_nt no_trade TYPE set(2) GRANULARITY 2
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, run_id)
COMMENT '日度编排器决策快照表(T2 拍板留痕真源,BT-P1-031)'
```

- 写侧纪律：只增不改（重拍/修订=新 run_id 追加，同 alloc_budget_daily/regime_snapshot_history 口径，禁 ReplacingMergeTree 静默覆盖）；写侧生成器禁 `datetime.now()/time.time()`（ingest_ts 由 DB 侧生成）；写路径唯一=编排器（审计 §七"写侧只挂一器"）；落库走 DatabaseService/既定 CH 写通道，零裸 SQL。

### 4.2 一闸：分层参与门快照（只读采集，零判定改动）

器侧聚合查询优先（门模块不改动），确需只读口的门模块走"暴露 read-only 快照函数"最小改动：

| 层 | 采集源（全部已核实在盘） | 采集内容 | 缺席语义 |
|---|---|---|---|
| L1 | `regime/core/regime_detector.py` 产物表 regime_snapshot_history（PIT 读） | dominant/confidence/confidence_signal/risk_signal/shrinkage | 快照缺席→no_trade（§六） |
| L2 | `signal_ashare/sector/sector_gate.py`（三级放行） | 放行档位 | 缺席=该层门关，依赖 L2 门参与的包今日禁用 |
| L3 | `signal_ashare/core/environment_switch.py`（六段×四开关查表）+ `signal_ashare/tradability_preflight.py`（五查，新件零调用方，接线顺带挂） | 开关表状态 | 缺席=门关 |
| L4 | `alloc_budget_daily` 当日 run 切片 + `position/core/firm_risk_aggregator.py`（约束栈） | 预算带/约束态 | budget run 缺席→no_trade（预算无来源=不出预算） |
| L5 | `security/access_control/kill_switch.py`（get_kill_switch 态）+ `risk/core/drawdown_state_machine.py` 级位 + `ex_core/price_cage.py` 配置态 + `position/core/t1_sellable.py` 资格语义 | 熔断/回撤级位/笼子/T+1 | kill_switch 缺席读态=按熔断保守侧处理（保命件方向不猜） |

采集失败不炸拍板：缺席项在 gate_snapshot_json 中标 `absent`，由 §六降级矩阵接管；`position/core/pyramiding_rules.py`（加仓资格四重门，零调用方）列为 L4 采集扩展位，首版不接。

## 五、接口契约

### 5.1 与资源排班表（对话供给侧）的接口

- 排班 v1 真源（已交付）：`config/resource_profile_registry.yaml`（资源画像注册表：实体/资源档/互斥组 exclusive_group/schedule_truth_source）+ 采样样本流 `.runtime/logs/resource_samples/*.jsonl`（见 docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md）。
- **编排器只读排班、不写排班**（单向依赖，防自指）：读接口签名 `read_today_schedule() -> TodaySchedule`（今日可跑任务与资源窗口）。
- 诚实标注（待讨论）：排班 v1=画像注册表+冲突闸，**"今日可跑任务与资源"的日度视图属排班 v2 范围**（v2 施工计划已在 docs/_working/resource_schedule/resource_schedule_v2_construction_plan.md）。首版编排器该接口返回 stub（全可用语义，不阻塞拍板），仅用于 heavy 任务可跑性粗判（E0 算力闸语义）；v2 落地后切换真实现。接受度=待 Owner 批准点 §八-8。

### 5.2 与 S-OWNER-001/002 策略卡的接口（包选择输出格式）

- S-OWNER-002（regime→策略包切换器，docs/_working/factory/strategy_cards/2026-09-16-s-owner-002-regime-switcher.md）机构化定义：输入市场状态+置信度 → 输出"允许启用的策略包集合+各包仓位上限系数"；它不是策略，是策略的调度器。**编排器=该接口的首个生产消费者**（查表实现：state_matrix 已填 mounted 格→包集合）。
- 输出契约 `PackageDecision`（落 decision_daily.package_set_json）：

```
PackageDecision = {
  "enabled_packages": [str],            # 启用包 strategy_id 清单
  "per_package_cap": {sid: float},      # 各包仓位上限系数(≤1.0,受 position_cap 约束切分)
  "source_cell": "TDM-E-L1|<state>",    # state_matrix 溯源格子
  "source_confidence": "proposed|verified",  # 源格子置信度,如实透传不粉饰
  "incomplete": bool,                    # pending-owner-adoption 空格导致包选择残缺
}
```

- 依赖事实：S-OWNER-002 全量考试前置="≥2 个已毕业策略包"（当前未满足）；**首版切换器=查表骨架先行**（考试线可用简单代理包先行验证机制，卡文件既有口径）。S-OWNER-001（300ETF 波段+底仓T）为首个接入包候选（§八-2）。
- 默认行为翻转（"全时全包"→"切换器管"）=生产流转 Owner 门位（卡文件既有裁定），编排器首版不翻转任何既有行为：**纸面/模拟盘留痕先行，实盘行为零变更**。

### 5.3 与下游的接口（分发面）

- 首版下游=一图仪表盘（`frontend/dashboard/components/warroom.py` 增"今日决策"面板读 decision_daily）+ 留痕；不产执行单（BT-P2-055 未在）。
- 未来执行面接入契约（预留，不施工）：以 decision_daily 当日最新 run 行为放行凭证（对齐 alloc_budget_daily.adjudication_id 先例）；无行=无新开仓令。

## 六、爆炸半径与失败模式

### 6.1 两向护栏

| 误判方向 | 后果 | 护栏 |
|---|---|---|
| 误"今日不交易"（假休） | 错过行情=机会成本 | ①no_trade 必须 reason 枚举落库（可回放可归因）；②判据全部来自已接电真源（预算带 0%/kill_switch/regime 缺席），不引入新模糊判断；③默认形态是"限仓交易"而非二元开关——position_cap 恒≤min(预算带，60% 硬顶)，宁可少给不误禁；④运营指标（不施工，退役审计用）：no_trade 日 vs 次日行情的机会成本统计挂季度退役审计（宪法 §4.2） |
| 误"开"（假开） | 风险敞口 | ①拍板三前置齐活才出决策，任一缺席=no_trade；②position_cap 上限双重封顶（预算带插值+60% 硬顶），即使一切正常也放不出全仓；③决策快照行=放行凭证，无快照=无新开仓令；④快照不可变（只增不改），误拍可追修订行不可涂改 |

### 6.2 降级矩阵

| # | 缺席/故障 | 判定 | 安全侧动作 | 落库痕迹 |
|---|---|---|---|---|
| D1 | regime 快照缺席/陈旧（>1 交易日） | L1 教材缺 | no_trade=1（禁新开仓），存量交横切保命件 | reason=regime_missing, degraded=1 |
| D2 | 门快照部分缺席（L2-L5 某层采集失败） | 该层不可证 | 不阻断拍板；缺席层按"门关"，依赖它的包今日禁用 | gate_snapshot_json 标 absent, degraded=1 |
| D3 | alloc_budget_daily 当日无 run | pf_alloc 链未跑（上游故障） | no_trade=1（预算无来源=不出预算） | reason=budget_run_missing, degraded=1 |
| D4 | 日历查无此行（当日） | 休市 ∨ 续期失败 | 当日有 daily_kline SUCCESS → data_proven 降级开市；否则休眠 | calendar_source=data_proven, degraded=1 |
| D5 | 日历年度续期失败（表尾<target+10 交易日） | 2027 翻转风险 | 哨兵告警出声；data_proven 模式续命；连续 N 日升级告警催人工续期 | degrade_reasons+=calendar_stale |
| D6 | kill_switch 读态失败 | 保命件方向不可猜 | 按熔断保守侧（no_trade=1） | reason=kill_switch（保守）, degraded=1 |
| D7 | 编排器自身异常 | 拍板体故障 | fail-open：不留半行、告警出声；下游无凭证=保守侧 | 仅日志/告警留痕 |

设计不变量：**D1-D7 全部收敛于"禁新开仓"或"维持现状"，无任何分支放大敞口**；保命件（kill_switch/drawdown/止损）横切独立，编排器任何故障不削弱其运行。

## 七、施工切分（按审计方案顺序：库→闸→蓝图过审→器→图）

| 刀 | 内容 | 验收标准 | 工程量复核 |
|---|---|---|---|
| 刀0（本文档） | 蓝图过审 | Owner 对 §八 逐条裁定；§九自裁无否决 | — |
| 刀1 一库 | `schemas/categories/decision_daily.py` DDL-as-Code + depgraph 登记 + apply | `scripts/ch/verify_schema_truth.py` 无漂移；写入/读取 round-trip 测试过（测试禁写生产路径，输出 tmp_path）；creation_token 已登记 | **S**（纯 schema 件，同 alloc_budget_daily 先例 0.5 天级） |
| 刀2 一闸 | 器侧五层门态聚合查询（+必要时门模块只读口最小暴露） | 五层采集单测全绿；缺席注入测试（每层 absent 路径）全绿；**零判定逻辑改动** diff 复核 | **S-M**（L1/L4/L5 读表读态现成，L2/L3 需聚合查询各 1-2 函数） |
| 刀3 一器 | 编排器模块（pipeline_events 第三棒挂点+date-marker 幂等+降级矩阵+warroom 骨架复用口径） | 事件链端到端 dry-run（非交易日休眠/唤醒拍板/修订行三场景）；降级矩阵 D1-D7 全分支单测；三前置判定测试；新 .py 登记 add_module_translation | **M-L**（对齐审计 §七 M-L 判定；依赖 state_matrix 格子 Owner 采纳程度，空格降级路径已设计不阻塞） |
| 刀4 一图 | 仪表盘"今日决策"面板读 decision_daily + TDM 高亮按节点 id 映射 | 面板读库渲染过；no_trade/degraded 状态可视；不重建图 | **M**（复用 warroom 组件与 api_server 既有模式） |

- 并行性：刀1 与刀2 可并行先行（审计 §七既有结论）；刀3 依赖刀1（写目标）+蓝图过审；刀4 依赖刀1。
- 明确不做（防膨胀）：不建新事件 kind、不接执行单源、不做盘中重判、不动 TDM 台账 F-C1 module_ref 错位（审计 Y4 另案）、不接 pyramiding_rules（Y7 随后批）。

## 八、待 Owner 批准点清单（我做不了的裁定，逐条待裁）

| # | 批准点 | 背景/选项 |
|---|---|---|
| 1 | **"今日不交易"判据阈值定型** | 过渡带最大隶属度阈值（TDM 注记 60%）与 dominant 置信度下限的最终数值；no_trade 触发枚举清单终稿（本文草案=distribution_band/kill_switch/regime_missing/budget_run_missing/calendar_ambiguous/transition_band） |
| 2 | **首版接入包集合** | S-OWNER-001（300ETF 波段+底仓T）是否为唯一首包；state_matrix 中 pending-owner-adoption 格子的采纳节奏（Owner 资金分配门位，AI 禁自填） |
| 3 | **仓位参数确认** | 60% 硬顶、六段预算带数值（TDM 全 proposed）、过渡带降仓系数（0.5-0.7 带内取值）——proposed→confirmed 需 Owner |
| 4 | **日历降级容忍度** | data_proven 模式连续运行 N 日升级告警的 N 值（草案 N=3）；是否接受 data_proven 作为开市判定 |
| 5 | **一库归属与双写** | decision_daily 落 c1_backtest 确认（vs 另立库）；是否同时落 prediction_log decision 族行（复用其幂等键） |
| 6 | **首版分发范围** | 仅留痕+仪表盘、不驱动执行单（实盘行为零变更）确认；执行面接入时点（挂 BT-P2-055 后另裁） |
| 7 | **T3 盘中修订权** | intraday_revoke 由 AI 自动（kill_switch 熔断联动）还是 Owner 人工；自动修订的触发白名单 |
| 8 | **排班接口 stub 期** | 排班 v2 日度视图落地前，read_today_schedule() 返回全可用 stub 是否接受 |

## 九、自裁记录（蓝图内自裁、不待 Owner 的设计决定；Owner 可否决升级为批准点）

1. 触发点=daily_kline SUCCESS 第三棒（regime→pf_alloc 之后），不建新事件 kind、不开闹钟（日历只作粗筛+哨兵，不作唤醒源）。
2. 幂等=业务日级 date-marker（REGIME_SNAPSHOT 先例），重拍/修订=新 run_id 追加（alloc_budget_daily 先例）。
3. "今日不交易"=禁新开仓≠清仓；保命件横切独立为全部降级设计的安全底座。
4. 新表而非挂 prediction_log 为主体（双写留 §八-5 小批准点）。
5. 日历歧义以 data_proven（行情入库实证）降级续命，而非误判休眠——误休眠是 2027 翻转的最大静默风险。
6. 编排器为 warroom pipeline 的并列新增拍板体，不改造后者职责（零调用债务不升级）。
7. 首版 T3/T4 只留接口签名；执行面凭证契约预留不施工。
8. no_trade 误报率统计作为运营指标写进退役审计口径，不在本工程内施工。

## 十、引用（全部 grep 核实在盘，2026-09-16 审计时点）

- 底稿与语境：`docs/_working/trading_vision/2026-09-16-skeleton-coverage-audit.md`（§七基建最小方案/§六 R2/R3/§八待判定）、`docs/_working/trading_vision/2026-09-16-owner-vision-system-mapping.md`（§一五层/§三缺口/§四策略卡）
- 事件链真源：`src/zephyr/strategy_pipeline/pipeline_events.py`（MOD-BT-190：wire_data_scheduler/SIM_DAILY_WAKE_TASKS/maybe_refresh_regime_snapshot/maybe_emit_pf_alloc_daily/LIGHT_KINDS/OPTIONAL_DUE_KINDS）
- 骨架复用：`src/zephyr/plan_engine/daily_warroom_pipeline.py`（MOD-PLAN-018：两段编排/次交易日解析/幂等/fail-open）；禁做清单真源 `src/zephyr/plan_engine/sit_out_list.py`（MOD-PLAN-014）
- 表 DDL 真源：`schemas/categories/regime_snapshot_history.py`（MOD-BT-031）、`schemas/categories/alloc_budget_daily.py`（MOD-PA-040）、`src/zephyr/reporting/prediction_log_writer.py`（prediction_log 唯一真源）；PIT 读法 `src/zephyr/pf_alloc/allocation_inputs.py`（SQL_LATEST_REGIME_SNAPSHOT）
- 日历：`src/zephyr/data/trading_calendar.py`（MOD-L00-004 XSHG 本地真源/is_trading_day 降级链）、`src/zephyr/data/config/tasks.yaml` trade_calendar_refresh（monthly_static，baostock+akshare fallback）、`src/zephyr/data/implementations/akshare_provider.py` _fetch_trade_calendar（is_open=1 只存开市日/pretrade_date 口径）
- 门模块（一闸采集对象）：`src/zephyr/regime/core/regime_detector.py`、`src/zephyr/pf_alloc/core/vol_target_allocator.py`（MOD-BT-082）、`src/zephyr/signal_ashare/sector/sector_gate.py`、`src/zephyr/signal_ashare/core/environment_switch.py`、`src/zephyr/signal_ashare/tradability_preflight.py`（MOD-SIG-151）、`src/zephyr/security/access_control/kill_switch.py`、`src/zephyr/risk/core/drawdown_state_machine.py`、`src/zephyr/risk/core/ashare_stop_loss_engine.py`、`src/zephyr/position/core/firm_risk_aggregator.py`、`src/zephyr/ex_core/price_cage.py`、`src/zephyr/position/core/t1_sellable.py`、`src/zephyr/position/core/pyramiding_rules.py`
- 分配链：`src/zephyr/pf_alloc/allocation_orchestrator.py`（MOD-PA-030）、`src/zephyr/pf_alloc/allocation_persistence.py`、`src/zephyr/pf_alloc/core/regime_meta_allocator.py`
- 配置面：`config/trading_decision_map.yaml`（TDM-E-L1 总闸/TDM-F-C1 六段预算带/state_matrix 24 格/portfolio_plan PP-001）、`config/resource_profile_registry.yaml`（排班 v1）
- 策略卡：`docs/_working/factory/strategy_cards/2026-09-16-s-owner-001-300etf-band-t.md`、`docs/_working/factory/strategy_cards/2026-09-16-s-owner-002-regime-switcher.md`
- 排班语境：`docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md`、`docs/_working/resource_schedule/resource_schedule_v2_construction_plan.md`
- 仪表盘复用：`src/zephyr/frontend/dashboard/components/warroom.py`、`src/zephyr/frontend/dashboard/api_server.py`
- 工具与纪律：`src/zephyr/shared/io/file_utils.py`（safe_write_text）、`scripts/git_commit.py`、`scripts/governance/d3_metadata/batch_creation_tokens.py`

## 十一、作战室三任务产品需求（2026-09-17 自 2026-09-16-blueprint-addendum-warroom-three-tasks.md 并入，本节起为该附录唯一真源）

> 本节=《判定台账标准 v0.1》伴生件的并入体。原附录文件已完成其 task_bound 使命（completes_when 达成）。

### 定位与分工（互补不打架）
- **作战室（MOD-PLAN-018）=计划与验证的载体**：晨判计划卡/场景样本积累/Brier 校准/执行不一致记账。
- **编排器=晨判拍板+分发的心脏**：串 L1-L5 门快照→策略包选择→仓位上限→"今日不交易"判定→决策快照落库。
- **共同缺口的新增件**：盘中 L1 实时跟踪件（分钟级大盘状态判定）——挂编排器蓝图已预留的 T3 接口签名（intraday_revoke）。

### 三任务产品需求（各接判定台账标准三表，详见 judgment-ledger-standard.md）
1. **盘中实时走势分析**（原缺口）：新增盘中 L1 跟踪件，分钟级产出五态判定+概率+证据列（量比/涨跌家数比/进攻板块拉板数/缺口/隔夜参照）+尾盘预测，写 judgment_intraday_market_state。证据维度需求示例（Owner 口述直译）：成交量萎缩、低开、防御性板块主导、无券商/半导体拉板→"低迷情绪，大盘走不好，尾盘仍差"。
2. **明日走势概率**：盘后产出 judgment_next_day_forecast（三态概率+分布分位+隔夜参照指纹），接 brier_calibration 日常校准闭环（次日收盘自动回填打分）。
3. **验证昨日计划**：场景引擎——晨间 daily_plan（场景触发条件必须可测量）+盘中 scenario_hits 实时归类+EOD actual_scenario/plan_followed/deviations 验证，deviations 对接作战室既有"执行不一致"记账。

### 输入全景（晨间计划的证据清单，Owner 口径）
昨收全量数据+美股夜盘+股指期货+隔夜新闻情绪+宏观日历+情绪周期（G07 关联待查，见标准 §七）。

### 施工挂点
三任务施工=蓝图刀 3（编排器本体）的并行前置/伴随件：表与结算器先行（标准 §三/§四），任务件随刀 3 接口接线。首版分发范围遵循蓝图批准点默认（仅留痕+仪表盘，实盘行为零变更）。
