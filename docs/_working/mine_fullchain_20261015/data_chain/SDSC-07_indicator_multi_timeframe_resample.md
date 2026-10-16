---
ttl: task_bound
---
# SDSC-07 技术指标 / 多周期重采样

> 挖矿工程：全链路图12 数据供给链 S3 衍生段 1/4｜真源=config/data_supply_chain_map.yaml#DSC-07｜挖矿时点=2026-10-15（含当日只读复跑）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：技术指标/多周期重采样，node_type=stage，build_status=partial，verified_scope=structure，行级状态=分面（indicator 腿 ✅ / resample 腿 🔨；骨架口径：任一整腿不 ✅ 则行级不 ✅）。
- 职责一句话：指标腿=2 个 internal 任务（technical_indicator_incremental 挂 daily_kline、full_refresh 挂周末校准）；重采样腿在生产上有 5 处并行实现互不复用，kline_resampler.py 独立合成器事实已被 provider 内联实现取代。
- 决策问句（图原文）：派生表比上游新吗？多周期 K 线该走哪一条实现？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-06→DSC-07（原始表就绪→衍生）；上游=kline_daily/tick 派生原料；跨槽 dependencies 全 advisory（判已满足防死锁） | config/data_supply_chain_map.yaml edges DSC-06→07+DSC-07 fallback |
| 输出面 | c1_market.technical_indicator/kline_{15,30,60}min/kline_sector_intraday→DSC-HA 出图（TDM 因子/工厂/图13）；本批复跑：technical_indicator max=2026-10-15（指标腿鲜）、kline_sector_intraday max=2026-10-15 15:00（板块分钟线复活）；消费锚=factor/indicator_reader.py:20/45+TI 册 26 | config/data_supply_chain_map.yaml#DSC-07 data_refs/facets/consumers；本批 CH 直查 |
| SSOT 真源 | internal 任务真源=tasks.yaml（internal_task_ids 28 条族）；语义层=图12 DSC-07；重采样五实现簇 manifest=03 簿 §1 | src/zephyr/data/config/tasks.yaml；docs/_archive/_working_cleared/map_build/fig12_datachain/03_衍生加工三族.md §1 |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/kline_resampler.py；执行体 kline_resampler.py/ch_tick_kline.py/tqcenter_provider.py 实存 | src/zephyr/data/kline_resampler.py；src/zephyr/data/implementations/ch_tick_kline.py；src/zephyr/data/implementations/tqcenter_provider.py（本批 ls） |
| 门禁约束 | 检测≠修复（downstream_action=detect_only）；档期倒挂静默吃 T-1 数据（3 组在册：cohort_ledger/emotion_index_close_final/daban_engine_load）；内收判据 w5_1 要求同域重复簇收敛唯一 | config/data_supply_chain_map.yaml#DSC-07 fallback/gaps；AGENTS.md §4.2 内收判据 |
| 自动化触发 | wired_cron：daily_kline/weekend_calibration 档期派工；09-24 案卷列该族 5 任务漏跑（DSC-20 输出）；指标腿末写 11:41 不落任何档期=节拍盲区显影位 | config/data_supply_chain_map.yaml#DSC-07 facets resample 腿 evidence+trigger_facts |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 原料主表今日新鲜（kline_daily max=10-15），衍生供料成立 |
| 输出面 | warn | 指标腿+板块分钟线今日全鲜（双复活）；但 kline_weekly/kline_monthly 已不存在（CH Code 60，本批复跑）——10-07 重构为 kline_weekly_hfq/kline_monthly_hfq（+preeng_backup_20261007 备份双件），图 data_refs 仍指旧表名=产出面指针漂移 |
| SSOT 真源 | warn | 图 data_refs 两表名失效（Code 60）；tasks.yaml internal 族在册但该重构未回写图——真源三层出现一处不同步 |
| 代码模块 | pass | 三执行体实存 |
| 门禁约束 | warn | advisory 假依赖不报错+3 组档期倒挂 residual 在册；五实现簇内收项（收敛唯一正门）未动工 |
| 自动化触发 | warn | 指标腿节拍盲区（末写不落任何档期）在册；resample 族曾 5 任务零打卡（09-24 案卷），现产物复活但按日节拍证据未补 |

## 4. 缺口与建议

1. 【warn→建议收口】kline_weekly/kline_monthly 重命名漂移：10-07 重构（*_hfq+备份件）后未回写图12 data_refs（也未在骨架 §1 反映）；建议随下次 generate_data_supply_chain_map 重生成同步改挂新表名，并给 preeng_backup 双件定退役时点（防备份件永生）。
2. 【warn 持续】重采样 5 处并行实现（内收判据同域重复簇）：收敛唯一正门是叶层收簇项，建议指定 provider 内联实现为唯一正门、kline_resampler.py 降级为废弃预告，逐月减一实现。
3. 【warn 持续】指标腿末写 11:41 不落档期=节拍盲区：建议 technical_indicator_incremental 打卡进 task_runs 档期桶（现 5×SUCCESS 有跑无档），或图侧明示该腿为事件型。
4. 【正向证据】CASEBOOK-001#outage 的 kline_sector_intraday 断供案（09-11~09-22）已复活（今日 max=10-15 15:00），建议补闭合记录。
