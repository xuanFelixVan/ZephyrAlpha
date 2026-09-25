---
ttl: task_bound
lane: M1 数据链
segment: #ARCH-351 miniQMT 清退退役映射表（裁定#376 落地物）
mined_at: 2026-09-25
session: st-commitspeed-tbl-20260924
---

# c351_migration_plan — miniQMT 清退退役映射表与迁移计划（C1 施工件）

> 授权边界：裁定#376「351=退役映射表落地」+ #ARCH-351 final_adjudication「退役映射表落地+跨时段时窗校验设计」。
> 施工铁律：**只切不删**（退役净删=Owner 门位，本文只登记净删候选）；时窗/覆盖洞任务只登记不切。
> 证据基线：2026-09-25 02:30-03:00 实测（tasks.yaml 271 任务 yaml 解析 + 各 provider CapabilityContract 声明清单 + CH 只读 SELECT（DatabaseService）+ data/failures + tick_subscriber_biz.heartbeat + E:\qmt_bridge_sim 实列）。

## 一、运行态基线（切换决策的前提事实）

1. **miniQMT 客户端尚未物理关停**：分钟K/ETF/LOF/tick_data/ex_dividend_event 等表 max_date=2026-09-24 持续到数；9/18「清退」是决策而非断电，全系统现仍跑在 miniqmt 供给上。本计划=清退前的预置换源，不是断流抢救。
2. **TickSubscriber 心跳实测 mode=xtdata**（2026-09-25T01:52:55 重启帧，tmp/tick_subscriber_biz.heartbeat），非 01_ingest 所记「桥模式」；tick_data 当日 2,776 万行全部 data_source='miniqmt'。桥模式（TICK_SOURCE=bridge）未在产。
3. **桥 tick 通道覆盖洞（本计划最关键证据）**：tick_data 全量表 qmt_bridge 行止于 2026-09-15（全历史仅 140 万行，峰值日 74 万）；同期 xtdata/miniqmt 日均 2,100-3,000 万行——**桥 tick 流比 xtdata 薄约 5-100 倍**。依赖 tick_data 聚合的桥分钟K合成链（qmt_bridge kline_1min/5min→synth_tick_kline，15/30/60→synth_kline_from_1min）capability 已点亮（qmt_bridge_provider.py:261-283）但**输入覆盖不足**，切过去=分钟K符号覆盖塌方。
4. **已在阵任务（静默断供，无 failure json——#ARCH-352 health 跳过路径）**：hk_kline 与 futures_kline_qmt max_date=2026-09-16；earnings_forecast=2026-07-03；express_report=2026-07-02；l2_tick 恒空（extra.disabled=true）。
5. **9/18 后已有换源先例**：index_quote_snapshot 已切 akshare（tasks.yaml:1017），auction 双件 9/17 切 qmt_bridge——证明「akshare/qmt_bridge 升主源+留痕注释」是既定模式。
6. **调度器 tasks.yaml 启动时装载**（scheduler.py:1238 `_load_tasks`）：任何切换须 DataScheduler 重载/重启才生效；重启窗口=运维决策，本文只登记不执行。

## 二、口径对账：在案「24 任务」→ 现势盘点 41+3

#ARCH-351 在案口径=TF01 8 主源 + TF02 16 全裸（=24），TF10 ex_dividend_event 为资金面涟漪单列。现势盘点（tasks.yaml 2026-09-25 解析，56 个 source=miniqmt 任务全查）：

| 口径 | 数 | 说明 |
|---|---|---|
| 在案 24 | 24 | TF01 8（index_quote_snapshot 已于 9/18 后切 akshare→现存 7）+ TF02 16 |
| TF10 补充 | 3 | earnings_forecast / express_report / ex_dividend_event |
| 盘点新增 | 31 | 在案三报告未覆盖的 miniqmt-无退路任务（周月K/ETF日K/美股/可转债增量/板块静态/财务主营业务/期权Greeks 等）|
| **无可用退路合计** | **41** | fallback 缺失、fallback 指向未声明 capability（假 fallback）、或 fallback=bdpan 死源 |
| 有可用 fallback（自动 failover 可达） | 12 | akshare/baostock capability 已声明且实现（adj_factor/四大财务报表现状/fallback 族）|
| QMT 无接口占位 | 3 | margin_trading/dragon_tiger/block_trade_qmt_placeholder——akshare 同类任务已在产，净删候选 |
| 合计 | 56 | 与 tasks.yaml miniqmt 计数闭合 |

**假 fallback 新发现（在案报告未记，须随批修正或登记）**：kline_weekly_hfq/kline_monthly_hfq（akshare 未声明该 capability）、index_weight_refresh、stock_list_refresh（同前）、tick_data_snapshot（bdpan 未注册源）。

## 三、判定规则（可切 vs 留登）

- **可切（本批执行）**：替代源 provider 已 CapabilityContract 声明该 capability 且实现与目标表 schema 兼容（有在产任务同通道实证），且无跨时段 DAG 时窗洞、无符号覆盖洞。
- **留登**：替代源缺失 / 替代源 capability 未声明（切了过不了启动契约校验 capability_validator.py:84-106）/ 存在时窗洞或覆盖洞（切了=换一种断供）。

## 四、首批切换（已执行，1 任务）

### kline_cb_incremental（可转债日K增量，daily_kline 槽）

| 项 | 内容 |
|---|---|
| 现状源 | miniqmt get_market_data_ex（capability kline_cb，miniqmt_provider.py:234 路由）|
| 替代源 | **akshare 新浪 bond_zh_hs_cov_daily**（akshare_provider.py:1085 CapabilityContract 声明、:10152 _fetch_kline_cb 实现：窗口过滤+张→手/10 单位换算+symbols null 自建转债清单；kline_cb_full_refresh 周末任务 fallback 同通道在产实证）|
| 切换步骤 | ①tasks.yaml source: miniqmt→akshare（留痕注释）；②fallback_sources=[{miniqmt, kline_cb}]（**只切不删**，旧源降 fallback 保温）；③extra.description 更新；④DataScheduler 重启后生效（登记运维窗，不在本批）|
| 回滚步骤 | 还原 source: miniqmt + 删 fallback_sources 块（git revert 单 commit 即可，任务无 dependencies、无表结构变更，ReplacingMergeTree 同键幂等）|
| 风险 | 新浪转债日K盘后更新时点晚于 miniqmt 盘中抓取→daily_kline 晚间槽无影响；成交量口径差异已由 /10 换算消化（实现注释在案）；转债清单按 bond_zh_cov 现势清单，退市转债增量回补能力弱于 miniqmt（存量由 weekend full_refresh 兜底）|
| 验证 | yaml 解析+validate_tasks_yaml 通过；akshare 源连通探针实测（见 §七）；表近 N 日到达基线=2026-09-24（miniqmt 供给），切换后首个交易日同口径复测留观 |

## 五、留登任务（40+3，逐任务：现状/替代结论/后续步骤草案/回滚/风险）

### G1 TF02 分钟K族 16 任务（intraday_minute 槽，全部留登——桥覆盖洞）

覆盖：kline_{1,5,15,30,60}min_incremental（5，通用 capability）+ kline_etf_{1,5,15,30,60}min_incremental（5）+ kline_lof_{1,5,15,30,60}min_incremental（5）+ market_breadth_snapshot_minute（1）。

| 项 | 内容 |
|---|---|
| 现状源 | miniqmt get_market_data_ex（全市场/ETF 板块/LOF 表读标的）；market_breadth=get_full_tick 全市场聚合 |
| 替代结论 | ①通用 5 任务：qmt_bridge kline_1min..60min capability **已声明**但输入=tick_data 聚合，桥 tick 流薄 5-100 倍（§一.3）→**符号覆盖洞，不切**；②ETF/LOF 10 任务：桥 meta **未声明** kline_etf_*/kline_lof_* capability（qmt_bridge_provider.py:261-283 仅通用六 ID），切了直接 CAP-NOT-FOUND；且 LOF 标的读 lof_list 表，桥 tick 是否覆盖 ETF/LOF 未实证；③market_breadth：桥 quote 通道未实现（known_issues「quote 族/指数取价桥通道未实现」）|
| 后续步骤草案 | ①大QMT 沙箱桥 TICKDUMP 通道扩容至全市场+段频对齐（基建立卡，非本车道）；②桥 meta 补 ETF/LOF capability+ch_tick_kline 补表路由；③market_breadth 等 quote 通道或改由 tick_depth_5 聚合重推导；④以上就绪后按本表模板逐任务切 source+留 miniqmt fallback |
| 回滚 | 还原 tasks.yaml 单字段（未切，无回滚对象）|
| 风险 | miniQMT 断电后全市场分钟K/宽度快照停更——**在案 P1 的真身**，在 24 命中里风险最高；依赖它的下游（daban_engine_load 依赖 market_breadth_snapshot_minute，tasks.yaml:3428）连带断供 |

### G2 TF01 盘中实时族 7 任务（intraday_realtime 槽，留登）

| 任务 | 现状/表到达 | 替代结论 | 风险与后续 |
|---|---|---|---|
| tick_data_snapshot | miniqmt 3 秒 Tick；fallback=bdpan（未注册源=死 fallback）；tick_data 表 9/24 在产但写者=TickSubscriber(xtdata 模式) 非 bulk 任务 | 桥 tick_data capability=no-op 零行语义（防双写设计）——切了=任务空转成功，掩蔽真断供 | 不切。真替代=TickSubscriber 切桥模式（心跳实测仍 xtdata，基线 2 事实）；登记 OS 计划任务 TICK_SOURCE 复核项（禁 schtasks 写，Owner/运维窗）|
| option_iv_surface_incremental | 表 max=09-23（已现断续） | akshare 无现成曲面聚合 API（假 fallback 已移除留痕） | 需自建 IV 曲面构建（逐合约 IV→曲面），登记候选库评估卡 |
| convertible_bond_iv_incremental | 表 9/24 在产 | 同上 | 同上 |
| futures_kline_qmt_incremental | **max=09-16 已阵 9 日**（静默） | akshare kline_futures 存在但表/口径不同（c1_market.kline_futures，daily_capital 槽另一任务承载） | 切表/切 capability 非纯路由层；消费端映射审查后或直接并入 kline_futures 族（净删候选预登记）|
| hk_kline_incremental | **max=09-16 已阵**（静默） | akshare kline_hk_daily 存在但目标表 c1_market.kline_hk_daily（另一任务/表） | 同上，hk_kline 表消费端映射审查 |
| futures_tick_intraday | 股指期货 3 秒 Tick 写 tick_data | 桥 Future/ 目录在盘但 provider 无期货 capability | 桥期货通道评估卡 |
| l2_tick_snapshot | extra.disabled=true，l2_tick 表恒空 | L2 权限随 miniQMT 清退消失，无替代 | 已停用留册——净删候选（Owner 门位）|

### G3 TF10 基本面事件族 3 任务（daily_event 槽，留登；ex_dividend 优先）

| 任务 | 现状/表到达 | 替代结论 | 风险与后续 |
|---|---|---|---|
| ex_dividend_event_incremental | get_divid_factors；**表 9/24 在产（清退后唯一存活的关键命中）**；dr=当日综合除权因子=stk_limit 公式法唯一输入 | akshare 有 dividend（东财 20 列，dividend_incremental_akshare BRK-030 已承接旧表）与 stk_limit 直采（stk_limit_premarket/postclose 双任务在产），但**无 ex_dividend_event 同构 capability**（interest/stockBonus/dr QMT 字段映射无现成实现） | 资金面涟漪：直接踩 stk_limit 公式法的路径断供（直采路径在产可部分对冲）。后续=akshare 分红送配字段映射→ex_dividend_event schema 的专用 fetch（D2 SOP 全链），或 stk_limit 公式法改直采兜底——带裁定号立卡，**本组切换优先级最高** |
| earnings_forecast_incremental | QMT ProfitForecast；**max=07-03 已阵两月**（静默） | akshare/akshare_alt 均无该 capability（业绩预测类接口未接入） | 已断供基线，无即时恶化；接入评估卡 |
| express_report_incremental | QMT Performance；**max=07-02 已阵两月**（静默） | 同上（业绩快报 stock_yjkb_em 类接口未接入） | 同上 |

### G4 日频/衍生 K 线族 8 任务（daily_kline / daily_capital / weekend_calibration，留登）

| 任务 | 替代结论 | 后续/风险 |
|---|---|---|
| kline_weekly_incremental / kline_monthly_incremental | miniqmt 直接周/月棒；akshare/internal 均未声明 | 替代路径可走 kline_resampler（kline_daily 派生，ch_tick_kline 注释同模式）——登记 internal capability 评估卡；断供后周月表停更 |
| kline_weekly_hfq_incremental / kline_monthly_hfq_incremental | **fallback=akshare 假 fallback（capability 未声明）** | 假 fallback 修正卡（显式置空留痕或补实现，照 akshare/kline_us_daily 先例）；deps=adj_factor_incremental 无时窗洞 |
| kline_etf_daily_incremental | akshare 无 kline_etf_daily capability（fund_etf_hist_em 未接） | 接入评估卡 |
| kline_us_daily_qmt_incremental | fallback=[]，akshare/tushare 均无 kline_us_daily | 美股权限随清退消失即断供；接入评估卡 |
| hk_kline_full_refresh | weekend 全量，同 hk_kline 结论 | 随 G2 hk_kline 卡合并处置 |

### G5 静态刷新族 4 任务（monthly_static / nightly_financial，留登）

| 任务 | 替代结论 | 后续/风险 |
|---|---|---|
| stock_list_refresh | fallback=akshare:stock_list **假 fallback**（akshare 仅 st_stock_list/hk_stock_list/stock_list_delisted） | 假 fallback 修正卡；真替代=akshare stock_basic 类映射（股东户数 A4 先例模式） |
| sector_list_refresh | akshare 无 sector_list capability（有 concept_sector/sector_meta 邻接） | 映射差异评估卡（板块口径不同） |
| index_weight_refresh | fallback=akshare:index_weight **假 fallback**（_fetch_index_weight_map 内部函数存在但未声明 capability） | 补 CapabilityContract+fetch 接线评估卡（实现半成品在库） |
| main_business_incremental | akshare 无 main_business | 主营业务构成东财接口评估卡 |

### G6 已停用/占位 5 件（净删候选——**只登记，净删=Owner 门位，本批零动作**）

dividend_incremental（2026-09-09 方案D 停用留册，akshare 承接已在产）、kline_5min_history_backfill（描述自记「此任务已退役」）、l2_tick_snapshot（extra.disabled=true）、margin_trading_qmt_placeholder、dragon_tiger_qmt_placeholder、block_trade_qmt_placeholder（akshare 同类任务已在产，QMT 无接口）。

## 六、时窗洞专项登记（裁定#376 后半句，非换源范畴）

1. **TF07 daban 名义 DAG 边**（rpt_tf07）：daban_engine_load 日频消费←daban_board_event 周频生产，task_queue 对跨批依赖视为已满足（task_queue.py:147-169），周二至五装载上周事件——实盘相关。修法=跨时段 DAG 时窗校验设计（依赖边带时窗约束），带裁定号立卡。
2. **TickSubscriber 模式漂移**：心跳实测 xtdata 模式≠设计桥模式——miniQMT 断电瞬间 tick 实时链整体死亡（不止 24 命中）。OS 计划任务 TICK_SOURCE/启动参数复核+桥模式演练=清退前置条件，登记运维窗（禁 schtasks 写）。
3. **#ARCH-352 静默失败**：health 跳过路径无 failure json——本计划 4 项「已阵 N 日」全靠 CH max_date 巡检发现，值班轮询机制（#376 改裁 b）落地前，integrity 23:00 聚合是唯一兜底。

## 七、验证记录（只读）

- 2026-09-25 CH 到达基线（DatabaseService 只读 SELECT）：kline_1min 15,747,282 行/9-12 以来 max=09-24；kline_5/15/30/60min、kline_etf_*、kline_lof_*、market_breadth_snapshot、tick_data、ex_dividend_event max=09-24；option_iv_surface max=09-23；futures_kline_qmt、hk_kline max=09-16；earnings_forecast max=07-03、express_report max=07-02、l2_tick 恒空。
- 失败文件面：data/failures 近 30 件无一分钟K/实时族任务（旁证 #ARCH-352 静默路径）。
- 首批切换验证：tasks.yaml yaml.safe_load 解析通过+table_registry.validate_tasks_yaml 无新增 WARN；akshare 源连通探针（bond_zh_hs_cov_daily 单券种实测）见提交批注。

## 八、复核命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python -c "import yaml;d=yaml.safe_load(open('src/zephyr/data/config/tasks.yaml',encoding='utf-8'));t=[x for x in d['tasks'] if x['task_id']=='kline_cb_incremental'][0];print(t['source'],t['fallback_sources'])"
grep -c "CapabilityContract" src/zephyr/data/implementations/qmt_bridge_provider.py   # 桥 capability 数（8）
cat tmp/tick_subscriber_biz.heartbeat | python -m json.tool | grep mode               # 订阅器模式 witness
```

## 九、未尽事项与升级项

1. 本批只切 1/41——其余 40 任务全部留登，原因非流程惰性：**替代源普遍缺失或存在覆盖/时窗洞**（§三判定规则），强行路由层切换=把静默断供换成静默空转，违反本任务「无时窗洞才切」前置。
2. 清退前置条件清单（Owner/运维窗）：①TickSubscriber 桥模式演练+全市场桥 tick 扩容基线；②DataScheduler 重启窗口（首批切换生效）；③G3 ex_dividend 换源立卡（资金面涟漪最高优先）；④假 fallback 4 处修正批；⑤净删候选 5 件走 Owner 门位。
3. 本计划为快照口径（2026-09-25）；tasks.yaml 演进后以本册+复跑 §八命令对账，计数勿从散文引用。
