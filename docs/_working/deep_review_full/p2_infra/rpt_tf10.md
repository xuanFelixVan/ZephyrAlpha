---
ttl: task_bound
doc_type: report
title: 深度审查报告——TF10 daily_event盘后事件族(42任务)
object: TF10 daily_event 盘后事件任务族
target: "src/zephyr/data/config/tasks.yaml（schedule: daily_event 实测 42 条，主锚 594/660/672/684/712/724/738/750/1846/1924/2500-2555/1960-2042/2562-2938/3294-3338）；schedule.yaml:85-89"
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审；任务书"39任务"为旧版口径）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF10 daily_event盘后事件族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **42 任务**（disabled 2：audit_opinion/rights_issue）。19:00 default 池，交易日守卫（schedule.yaml:85-89；trading_calendar.py:157）。构成：事件经典 8（analyst_forecast/earnings_forecast(miniqmt)/express_report(miniqmt)/ex_dividend_event(miniqmt)/equity_pledge×2/disclosure_plan/repurchase）、D3 宏观六表（macro_price/pmi/credit_money/activity/trade_gauge+macro_daily_gauge 归 TF09）、J4/J5（index_adjustment 归 TF15、rate_decision 归 TF09）、生猪 3、另类 28（akshare_alt：千股千评/航运/台风×3/深圳开放数据 20/恐贪/转债溢价/alt_regime(internal)/商品 2）。
- 哨兵：D3 六表+J5+深圳域多表已入 data_supply_sentinel.yaml（16 表清单，config/data_supply_sentinel.yaml:28-124）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | **miniqmt 三件无退路（退役直接命中）**：earnings_forecast_incremental（QMT ProfitForecast，tasks.yaml:660-670）、express_report_incremental（QMT Performance，672-682）、ex_dividend_event_incremental（QMT get_divid_factors，712-722）全为 miniqmt 独有源且 fallback 缺省。迁移台账 §2.2-C 明列前三件（shareholder 已 9/18 治本切源，本三件未动）。**ex_dividend_event 断供有资金面涟漪**：dr=当日综合除权因子是"stk_limit 公式法唯一输入"（tasks.yaml:722）——除权除息日涨跌停价计算失真风险 | tasks.yaml:660-722；migration-ledger §2.2-C | **P1** | 9/19 起查 ex_dividend_event/earnings_forecast/express_report 三表断更；除权日抽查 stk_limit |
| A | D3 宏观六表"月频表挂 daily_event 日更全量幂等"设计（单表 200-600 行）——规避 monthly_static 月初跑漏月中公布，与 catchup_guard 月度桶互补；哨兵阈值已配（tasks.yaml:1955-1959 注释自证）——设计-哨兵-对账三层闭环核对通过 | tasks.yaml:1955-2042；data_supply_sentinel.yaml:71-99 | 已查无 | 对照 sentinel yaml 六表条目 |
| B | akshare_alt 28 任务的 capability 全部在 AkshareAltProvider 声明（含 alt_stock_comment/alt_shipping_index/alt_typhoon_track 三件走 dict 路由而非 CapabilityContract 字面量——AST 提取器 `_route_caps_from_tree` 模式覆盖 dict keys，meta 对齐校验仍有效）；**但 akshare_alt 不在运行时启动校验的 source_to_meta 清单**（scheduler.py:1150-1156 只挂 3 源）——契约靠 commit gate CAP-CONSISTENCY（capability_validator.py:402-431），运行时零校验（系统发现 S3 的一部分） | akshare_alt_provider.py:278,563-582；scheduler.py:1150-1156 | P3 | 对比 source_to_meta 与 create_provider 分支集 |
| B | alt_regime_signal_refresh（internal）依赖 crypto_fear_greed_incremental（同时段）——强约束有效；上游断供→BLOCKED 传播正确 | tasks.yaml:2645-2654 | 已查无 | mock 恐贪失败看 BLOCKED |
| C | 千股千评/恐贪/转债溢价写入 c1_market.sentiment_panel 与 alt_stock_comment 等——F15/F25 因子消费端在 p1 决策链；本族断供→因子 NaN→消费端 fillna 策略未见声明（北向"加零不报错"前科 checklist #6 同型风险点，登记移交 p1 班次） | tasks.yaml:2621-2643 | P2 | grep F15/F25 消费端空值处理 |
| D | ex_dividend_event（miniqmt dividend capability）与已停用 dividend_incremental（schedule: disabled，tasks.yaml:701-711）——旧任务字段名不匹配事故留痕完整（方案D 停用），ex_dividend 治本替代——历史缺陷闭环质量好 | tasks.yaml:701-722 | 已查无 | — |
| E | 深圳开放数据 20 表单源（appKey 订阅制）+start_days_back 90 首刷窗+last_key 推进自愈（如 alt_sz_visibility tasks.yaml:2737）——"数据先行"事故防线（DDL 前置校验不阻断+local_fallback 回灌，scheduler.py:1346-1383）覆盖写侧；key 失效=env_missing 静默跳过（S2 同修项） | tasks.yaml:2725-2927；scheduler.py:1346-1383 | P2 | 清 SZ_OPEN_DATA_APPKEY_NEW 复跑看告警缺失 |
| F | 受阻（未检索）。恐贪指数（alternative.me）为社区指标非学术口径，仅记账不进决策（tasks.yaml:2631 描述） | — | 受阻 | — |

## 3 SOTA 对照
- 受阻。另类数据（航运 BDI/台风路径/生猪）为项目特色资产库（16 表挂 TDM 交叉轴），无通用 SOTA 对照项。

## 4 缺陷清单
1. **P1 miniqmt 三件（earnings_forecast/express_report/ex_dividend_event）**：按 §2.2-C 节奏切源（东财 datacenter/akshare 同类接口评估）——ex_dividend 优先（stk_limit 公式法输入）→验证法=切换日除权股票的 stk_limit 与交易所公布价对拍。
2. P2 key 类静默跳过显式化（深圳域新钥匙/FRED 同修）。
3. P2 情绪面板断供的消费端 NaN 语义确认（移交 p1 班次，本报告挂账）。

## 5 挂起疑问
- alt_sz_climate_hist_refresh（1953 起逐时 48.9 万行全量重拉）每日跑在 19:00 池——全量幂等重拉日耗带宽与 akshare_alt 单例 claim 竞争（与 27 件同池）的实际轮转时长未画像。
- hog_province_spot 增量=false 且"当天28省"（tasks.yaml:2555）——非交易日跑出旧值/空值行为未验证。

## 6 完备性自评
六轴全查（F 受阻）。长尾：42 任务中 28 件 alt 表 DDL 与源字段映射（如 crt_date/tj_date/ddate/tdate 各异）逐列核未做——建议收口方对 supply_sentinel 已覆盖的 16 表跑一轮"哨兵阈值 vs 表实况"画像。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
