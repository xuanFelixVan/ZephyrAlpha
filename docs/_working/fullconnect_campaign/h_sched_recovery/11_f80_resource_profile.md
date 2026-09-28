---
ttl: task_bound
title: F80 资源画像与排班（96→99 实体 18 字段+五件套闭环）——L08 复飞矿道案卷
session: zc-l08-20260927
---

# F80 · 资源画像与排班

> 总册行：I 段 F80，状态 built，P1，MOD-RESCHED-PROFILE/SAMPLER/GATE/ALERT/VIEW 五模块。M0=S5。
> 本卷=09-27 复飞复测。基册=m5_scheduling/01 册 D 族+补挖波_20260925/04_perf_watermark.md §二（画像五件套链关系）。

## 一、六向台账（实证锚点，09-27 活探）

| 向 | 内容 |
|----|------|
| 上游输入 | DataScheduler 槽位采样（SamplerScan PT10M）；schtasks 任务面（50 项，07 卷全列）；schedule.yaml（排班真源挂接字段 schedule_truth_source） |
| 下游消费 | ResourceRegenCheck（PT1H 漂移检出+--auto-regen 再生）；Writeback 05:40/ViewPublish 05:50/MorningReport 06:31 三生成器；MeasureCalibration 周标定；晨报消费 |
| 自动化触发 | 09-27 实测五件全 result 0 或语义内：SamplerScan 06:48:41 result 0、RegenCheck 06:21:22 **result 3（检出漂移语义，常态化非零=S6 活病）**、Writeback 05:40 result 0、ViewPublish 05:50 result 0、MorningReport 06:31 result 0 |
| 真源与注册表 | config/resource_profile_registry.yaml **机生**（generated_by=scripts/governance/generators/generate_resource_profile_registry.py；**09-27 实读 total_entities=99，generated_at 2026-09-26T22:21Z**——98（09-25）→99（09-26）随任务面扩容自愈） |
| 门禁与质量尺 | 生成注册表禁手改；全链无人工编辑位（采样→对账→再生→发布闭环）；"检出问题 vs 自身崩溃"分码欠账（S6） |
| 当前运行状态 | **绿（带 S6 黄点）**：五件套任务级四态当日全探；画像册 24h 内再生（09-26T22:21Z） |

## 二、子模块三级枚举

1. **画像册**：resource_profile_registry.yaml（99 实体×18 字段；schedule_truth_source 逐实体挂排班真源；触发器登记=总册四要素①判据的载体）。
2. **五任务**：SamplerScan（PT10M 采样入画像）/RegenCheck（PT1H 对账+auto-regen）/SamplerWriteback（05:40）/ResourceViewPublish（05:50 周历）/ResourceMorningReport（06:31 晨报）+MeasureCalibration（周一 06:17 标定）。
3. **生成器面**：generate_resource_profile_registry.py/generate_resource_week_view.py/generate_resource_morning_report.py（scripts/governance/generators 族；机生真源，禁手改）。

## 三、接线四态独立复核

- 总册 built → **维持 built**（闭环五环任务级全绿+册 24h 内再生）。
- **骨架勘误**：总册 F80"96 实体 18 字段"→**99 实体**（09-27 实测；96=骨架挖矿时点口径，册为机生自愈型，此漂移会随任务面扩容继续——文档计数应引字段不写死，宪法 §4.3 正例/反例各一）。

## 四、缺口清单

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | RegenCheck exit 3 语义与崩溃同码（S6 活病在 F80 的落点） | 分码方案（检出=3/干净=0/崩溃=其他）+晨报消费字段（归 M3） | P1 |
| 2 | 画像册实体数持续漂移（96→98→99） | 文档侧引用字段不写死；M5/总册回填 99 | P2 |
| 3 | 新任务入画像的时滞（DecisionChainSentinel/EvaporationBlackbox 09-25 后新增——是否已被 09-26T22:21Z 批次收录未逐条验） | 逐条 grep 画像册核收录 | 待裁 |
| 4 | 画像冲突闸（MOD-RESCHED-GATE）消费面证据薄（本卷未独立探） | 归 M5 深挖批 | P2 |
| STALE 13/假绿 5 | **不属 F80**（归 F77/F79 §四） | — | — |

## 五、自审闸三态

**部分挖干（复核维持）**：04 补挖册六向全证+本卷五任务/册头字段当日五探；缺口=冲突闸消费面与 99 实体逐条收录未验（登记）。三态=**维持 built，实体计数勘误一条**。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
grep -m2 "total_entities\|generated_at" config/resource_profile_registry.yaml   # 99 / 09-26T22:21Z
for t in ResourceSamplerScan ResourceRegenCheck ResourceSamplerWriteback ResourceViewPublish ResourceMorningReport; do powershell -NoProfile -Command "(Get-ScheduledTaskInfo -TaskName ZephyrAlpha_$t)|fl TaskName,LastRunTime,LastTaskResult"; done
grep -c "DecisionChainSentinel\|EvaporationBlackbox" config/resource_profile_registry.yaml   # 新任务收录核验
```
