---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-48
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-48 盘后板块K等权撮合（tdx 永久断供的收敛终点）

## 1. 定义

每日 15:40（Windows 计划任务 ZephyrAlpha_SectorEqwIntraday，2026-10-08 由 sector_eqw_intraday
规范化改名），等权链式聚合 runner（MOD-DATA-061，scripts/kline_sector_intraday_from_constituents.py）
以 sector_constituent 成分 × kline_1min 个股分钟 → kline_sector_intraday
（data_source='internal_eqw'，写前精准 DELETE 幂等；synth_sh=09-30 前历史行字面量）。
这是 tdx 板块源永久断供后的收敛终点（known_data_gaps 2026-10-04 B1 三退役批 Owner 批）。
图内决策问题："昨日/今日板块K撮合产了吗？行数与板块数够 580 族吗？"——CH 实证：10-08 改名后
首个交易日 internal_eqw 五周期满格（1m=171,351 行×711 族；5m/15m/30m/60m 同族满格）；
对拍达标（行业段 corr 0.9954-0.9990/地区 0.9953-0.9980/概念段 0.85-0.95=成分回溯误差已知项）。

## 2. 六向台账

### 2.1 输入面
- sector_constituent 成分表（新鲜：max(updated_at)=09-30 21:38 UTC）。
- kline_1min 个股分钟K（收盘 ~15:05 后可得——注册脚本 :10 注记"after kline_1min close ~15:05"）。
- tdx 源最后行=09-10 15:00 后零行（断供永久定性，不再作为输入面期望）。

### 2.2 输出面
- 产物：kline_sector_intraday（逻辑名，表名真源=TableRegistry，图内禁库名前缀字面量——
  TABLE-NAME-REGISTRY 口径），data_source='internal_eqw' 五周期。
- consumers=[]（map 消费者账面为空——本格 outputs 侧账面缺口，见三态）。
- 下游：板块域传感器/L2 门供料（D13-25 侧 sector_state 描述称"L2 门三原料供料真源"——跨格语义，
  未在本格 consumers 登记为边）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-48（wired/built/✅，production）。
- 簿 06；docs/_working/map_build/fig13_daycycle/06_盘后结算与三账.md。
- 注册契约：scripts/tasks/register/register_sector_eqw_task.ps1（:1 幂等注册声明、:16 taskName、
  :21 trigger 15:40、:25 REGISTERED 输出面；:3 注记 map D13-48 tn/query faces 对齐）。

### 2.4 代码模块
- module_id=MOD-DATA-061；module_ref=scripts/kline_sector_intraday_from_constituents.py:1
  （实存，internal_eqw 关键字在码——exec_evidence grep 路径在册）。
- runner MATURITY=production（2026-10-08 升级，ops 车道 st-fig13-followup）。

### 2.5 门禁约束
- 幂等纪律：写前精准 DELETE（同键域清除后重写）；假日零行自然安全（非交易日不撮合）。
- 表名真源=TableRegistry（禁库名前缀字面量在图 laws/NOTE 面）；synth_sh 历史行=字面量边界
  （09-30 前为合成行，与实撮分行以 data_source 区分）。
- casebooks=[]（本格无案例挂靠）。

### 2.6 自动化触发
- 机制=B_windows_task；schtasks=ZephyrAlpha_SectorEqwIntraday（registered=true+declared=true）。
- trigger_facts：count=1，last_run=2026-10-08T15:40:00（Result=0）；cadence declared
  "每日 15:40"、observed"交易日每日 1 跑（假日零行自然安全）"。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 成分表新鲜+个股分钟K时序匹配（15:05 后）；tdx 断供已收敛定性 |
| 输出面 | warn | 五周期满格+对拍达标实证，但 map consumers=[] 空账——下游消费关系未入账 |
| SSOT 真源 | pass | 图节点+簿 06+注册脚本注释三方对齐（tn/时点/幂等语义） |
| 代码模块 | pass | runner 实存且 MOD-DATA-061 在册，MATURITY=production |
| 门禁约束 | pass | 精准 DELETE 幂等+TableRegistry 表名真源+synth_sh 边界全在册 |
| 自动化触发 | pass | schtasks 双证+last_run Result=0 |

## 4. 缺口与建议

- 不在本段 4 gap/11 未接线清单内（wired/built，收敛终点格）。
- 建议：consumers 空账补登——把 L2 板块传感器/情绪面对 kline_sector_intraday(internal_eqw) 的
  读取点挂入 consumers 机生面（消费关系已事实上存在，账面为空会让"删表影响面"评估失真）。
