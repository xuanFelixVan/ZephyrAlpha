---
ttl: task_bound
session: st-ailayer-fullflow-sc
creation_token: m5sc-perf-watermark-20260925
---

# M5 补挖分册 04：性能水位册（F79 水位面 × F80 资源画像 × F81 阈值 SSoT）

> 证据：reaper --status 活探+源码 file:line+注册表实读，2026-09-25（本波基线 01:47）。只读挖矿。
> 总册 F79"reaper 与水位监控"、F80"资源画像与排班"、F81"监控告警"三环节的水位相关面在本册合账——它们共享同一条"阈值从哪来、谁判、谁收"的链。

## 一、三层水位闸（进程级→系统级→阈值 SSoT）

### 层 1 进程级收割（reaper 内建）
- `src/zephyr/trading/process_reaper.py:161` `_DANGEROUS_MEM_GB = 10.0`：单进程 RSS≥10GB（或 children 超限，:311）即入收割判定；:417 逐进程 mem_mb 采样。
- **判定权三分互斥**（:57 头注铁律）：incubator=事前拒生（spawn 前水位门禁）；reaper=事后收割；水位准入归 host_resource_governor——三面互不长草（本件不得长水位准入，水位件不得长收割）。

### 层 2 系统级水位闸（BRK-066/BRK-078 保命链接线）
- 真源件：`src/zephyr/infrastructure/capacity_assurance/host_resource_governor.py:224` `check_system_watermark()`——probe 实测→按 `config/alert_rules.yaml` 规则判定→命中即发通知板（publish），永不抛。
- **阈值零硬编码**：规则全读 YAML（`_load_watermark_rules` 只取 metric 落在本件供给面 `system.*` 的行；规则不可读=本周期不评估，"宁漏不假绿"）。
- system.* 规则 5 条实测（config/alert_rules.yaml，MOD-INF-015）：ALERT-SYS-001 CPU>80 ｜ 002 RSS>8GB ｜ 003 commit>90% ｜ 004 mem_avail<12GB ｜ 005 mem_used>85%。
- **reaper 保命链接线**（process_reaper.py:1037-1100）：每轮收割附跑保命链评估——应急保命轨（BRK-078）+系统水位（BRK-066）；水位看护失能只报 error 不反噬收割主链（:1069-1071）； breaches 落 --status 输出。

### 层 3 阈值 SSoT（REG-ATH-001）
- `docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml` v1.6.0（09-23）：全仓监控/告警/复盘阈值唯一真源；消费统一走 `src/zephyr/shared/alerts/threshold_loader.py` fail-closed（AI-THD-001 九模块统读后码内硬编码清零）；缺文件/缺条目直接报错，禁第二真源。
- 实测唯一 THD 条目 **49 条**（grep 去重计数；总册 F81 写"38 条"=v1.4/v1.5/v1.6 三轮增补未回写，**口径漂移待回填**）。
- 消费例证：health_monitor.py:48-63 压力分级 THD-HEALTH-001~004 import 期 fail-closed 加载（显式传参=测试逃生门）；THD-ALERT-003/004（死信积压 50+冷却 6h）、THD-ALERT-007（belt 离线>24h，09-22 S7 事故补课）、THD-TRD-001..004（交易五级熔断，status=design 未落码）。

## 二、资源画像五件套（F80 调度侧水位面）
- 注册表：`config/resource_profile_registry.yaml`——生成器产出（generated_by=scripts/governance/generators/generate_resource_profile_registry.py，generated_at 09-24T21:21Z），**total_entities=98**（总册 F80 写"96 实体"=漂移待回填）；`schedule_truth_source: src/zephyr/data/config/schedule.yaml` 逐实体挂接（排班一张真源）。
- 五任务（主波 01 册 D 族已列，本册补链关系）：SamplerScan（PT10M 采样入画像）→RegenCheck（PT1H，exit 3=检出漂移语义+--auto-regen 再生）→Writeback（05:40）/ViewPublish（05:50）/MorningReport（06:31）三生成器消费画像；MeasureCalibration（周标定）。**闭环=采样→对账→再生→发布**，全链无人工编辑位（禁手改生成注册表）。

## 三、实测基线（本波 09-25 01:47 reaper --status 摘录）
```
last_run=2026-09-25 01:47:24  scanned=23 whitelist_hits=17 killed=0
watermark: ram_total 63.85GB / avail 19.27 / used 69.8%
           commit_total 95.85GB / used 74.37 / pct 77.59
           cpu 61.8  degraded=False  breached=[]      ← 五条规则零命中，绿
safety_wires: emergency_track_state=normal breaches=1（累计 breach 计数位，当态 normal）
```

## 四、六向台账
- **上游输入**：psutil 进程采样（reaper）；系统 probe（host_resource_governor）；DataScheduler 槽位画像采样（SamplerScan）；alert_rules.yaml/alert_threshold_registry.yaml（规则与阈值）。
- **下游消费**：通知板 JSONL（api_server OpsAlertFeed 30s tick 消费，api_server.py:4415-4449）；晨报（ResourceMorningReport 06:31）；收割决策（reaper 层 1）；容量档案（working_vault 外唯一 F 侧画像消费=ViewPublish 周历）。
- **自动化触发**：reaper PT10M；SamplerScan PT10M；RegenCheck PT1H；Writeback/ViewPublish/MorningReport 每日三连；MeasureCalibration 周一 06:17；OpsAlertFeed 30s（api_server 进程内线程）。
- **真源与注册表**：alert_threshold_registry.yaml（REG-ATH-001，阈值 SSoT）；alert_rules.yaml（MOD-INF-015，系统水位规则）；resource_profile_registry.yaml（机生画像）；process_reaper.py/host_resource_governor.py（双闸本体）。
- **门禁与质量尺**：fail-closed 双向（阈值加载缺条目报错；规则文件不可读宁漏不假绿）；三分互斥（拒生/收割/准入）；生成注册表禁手改；"检出问题 vs 自身崩溃"分码欠账（RegenCheck exit 3 常态化=报警疲劳，主波 04 册 S6，归 M3）。
- **当前运行状态：绿**。三闸在轨，当日 breached=[]；黄点=RegenCheck 语义码不分（S6 活病）+CAS 残留 2 件（见 §五）。

## 五、堵点与卫生观察
| # | 项 | 修法 | 归属 |
|---|---|------|------|
| 1 | 总册 F81"38 条"/F80"96 实体"漂移 | 回填 49/98（分工册 §三.5 对账回写义务） | 总筹 |
| 2 | CAS tmp 残留：catalogs/ 下 alert_threshold_registry.yaml.tmp.21732.*、infrastructure_registry.yaml.tmp.45444.*（09-22） | safe_write_text 中断残骸，清理+查 safe_write 是否缺 finally 清理 | 治理链小单（他区只登记） |
| 3 | RegenCheck exit 3 语义与崩溃同码 | 主波 S6 方案（检出=3/干净=0/崩溃=其他），归 M3 | M3 |

## 六、自审闸三态
**挖干可施工**：三层闸每层有源码锚点+活探基线+规则清单实读；阈值链（YAML→loader→消费模块）双向闭环有测试佐证（红队 36 用例在册）；漂移 2 处已量化待回填。缺口=无结构性未知。
