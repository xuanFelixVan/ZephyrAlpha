---
ttl: task_bound
title: 数据车道班 99_delivery（T1-T6 逐件交付与验收尺，sid=st-datalane-20261010）
session: st-datalane-20261010
completes_when: T2/T3/T4 收官回执被二号/后续班签收 + T1 次夜写入量对账完成
---

# 数据车道班 99_delivery（sid=st-datalane-20261010，2026-10-10）

> 开班令=总统统筹 2026-10-10；台账=00_ledger.md（全程滚动）；本件=收官账。
> 逐件哈希+复核命令见 §四；草稿期数字以台账最新段为准。

## 一、T1 退役指标停算（裁定#489①+#494②）——已落地+闭环补全

- **bebba60c**：`_fetch_single_period` 写链按 REG-IND-001 status 过滤（仅 active 进写链；
  位置勘误与红证 A/B 见台账 §一）。红证：摘消费点过滤⇒wiring 测试红；HEAD 未修码⇒4 例全红。
- **24fec802**：T1 闭环面——P1 值级比对排除退役列集。复盘发现的交互缺陷（不补则 P1 永不
  跳过、夜跑全史重灌不停、T2 被 nightly NULL 版本掩埋）与红证见台账 §一。
- 主区对平×2（验收窗=当日 02:30 夜跑读主区码；final4 先例）：provider 与 backfill 两文件
  对平后主区实测 30 passed。主区 provider 文件现携带 B2/B4-M2 在途 hunks+本班 hunks，
  归属吸收按 489777c60e 在案口径。
- 验收（次晨跑）：夜跑 state 存活+finished_at=当日+TI_VALUE_SKIP 面 skipped>0（P1 复效）；
  写入量对比基线=单趟 3.5-4M 行——**注：本值依赖比对基读可得（241 熔断在案），读不到
  基的窗口宁多写不少写（行为不变）**。

## 二、T2 squeeze/wad 定点重算——执行+冷档双证（回执待二号）

- 处方盘面更新（探针法证，台账 §二）：修复 1a9ab332f58（10-10 05:11）晚于 02:30 夜跑起跑
  ⇒ 窗内最新版=旧码×hfq×截断基（四象限对表差值恒 −748.5 实锤）；在飞多腿产物出处不可
  干净归属 ⇒ 按开班令本义走自算定点重写稳健路线。
- 冷库双证：F:/zephyr_cold/50_archive/by_project/zephyralpha/datalane_t2_premutation/
  （2,643,381 键×6 窄列，parquet 38.7MB+tsv.gz 48MB，sha256 双件入 manifest.json；
  parquet=057b54ff…，tsv.gz=2d442318…）。
- 定点重写（recalc_t2_squeeze_wad.py --apply）：窗 2024-10-08..2026-09-30 daily，
  **24 个月全 OK，月写入≈7.6万-12.7万行，重算键 2,643,220（与冷档差 161=0.006% 源缺键
  保原值）**；公式=HEAD 1.1.0、源=kline_daily_hfq、wad 基=源表首 bar（基约定申报变更，
  D7 §一.3）；覆盖表 c1_market.tmp_t2_override（Memory，跑完即 DROP 零残留）。
  首写后 4 键探针 2/4（两键被在飞夜跑旧码腿重写掩埋=预判机制实证）——**21:3x 腿静默窗
  终态刷新已排**，明晨 02:30 起 T1 闭环码守值。
- 稳定性声明：写入后不可变性依赖 T1 闭环面（P1 跳过）在读得到比对基的窗口生效；若熔断
  窗口内夜跑仍全量插（ retired 列=NULL 版本），重跑本脚本即恢复（幂等 append）。
- 通知二号（R2-C 重考，归它不归本班）：读径=优先 T6 OPTIMIZE 后读宽表；PIT 稳定读=
  冷档 parquet。考试窗 UNION 2024-10-08..2026-09-30 冻结不变。

## 三、T3/T4/T6——脚本与方案就绪，执行排程如实申报

- **T3**：limit_up_down 2019-01-04..2026-07-19 推导回补脚本就绪
  （.runtime/tmp/st-datalane-20261010/backfill_limit_up_down_derived.py，口径=在册
  derived_stk_limit 先例+广度尺同源原语；验收=7 条广度序列×1622 交易日对拍
  02_breadth_derivation_report.yaml）。执行被在飞 bcure 全史重算链（.runtime/tmp/bcure/
  ti_shard_selfheal_driver，10-08 起月粒度爬坡）压住——禁双开红线让位，属主手工重查询
  亦 500 实证。**依赖申报：bcure 链收官后 dry-run→apply→对拍**。
- **T4**：断供链定位（hfq=根，TI=下游投影，周月=miniQMT 悬空旧基座）+五门小批验门方案
  =03_t4_cascade_gate_plan.md。执行同样排在 bcure 收官后（其 2026-10 月腿亦将重写
  当月 TI，T4 门 3 可被其覆盖性完成，届时只跑对拍）。
- **T6**：触发器监测——(a) CH 空闲窗窄窗读复测：**全天无空闲窗**（bcure 链+夜跑腿压着
  RSS 3.6~6.2GiB，窄 FINAL 读 241 两次实证、无 FINAL 窄读可通）；(b) T1 落地 ✅；
  (c) 比对基低内存通道=架构面呈报。⇒ 本班**未排 OPTIMIZE**（dexp 顺序铁律：bcure 重灌
  链在跑时收敛=白占 IO；且 23:00 W1 让位二号）。触发器(a)复测命令留档：
  `SELECT symbol,trade_date,wad FROM technical_indicator FINAL WHERE symbol='000001'
  AND trade_date='2025-06-06'`（安静窗 <60s 通过即触发）。

## 四、逐件哈希与复核命令

| 件 | 哈希/commit | 复核命令 |
|---|---|---|
| T1 计算腿停算 | bebba60c | `git show bebba60c --stat`；`PYTHONNOUSERSITE=1 python -m pytest tests/legacy_zephyr/data/test_internal_compute_provider.py -q` |
| T1 闭环面（P1 比对排除） | 24fec802 | `git show 24fec802 --stat`；`PYTHONNOUSERSITE=1 python -m pytest tests/data/data/data/test_ti_backfill_value_skip_and_shard_windows.py -q` |
| 战役文档三件 | 602edf00 | `git show 602edf00 --name-only` |
| T2 冷档 | manifest.json@F:/zephyr_cold/.../datalane_t2_premutation/ | `sha256sum F:/zephyr_cold/50_archive/by_project/zephyralpha/datalane_t2_premutation/*.parquet`（对照 manifest.parquet_sha256） |
| T2 重算脚本 | .runtime/tmp/st-datalane-20261010/recalc_t2_squeeze_wad.py | `python <脚本> --compute-only`（只读重演） |
| T5 快照器 day1 | data/emotion_index_snapshots/emotion_index_20261010T041044Z.jsonl.gz | sha256=8fbad68dc33c975ecd8a1230395c7068ab5f94b9b44f27d2658bea006731a240（manifest 对账） |
| keep 登记 | data/runtime/process_reaper_keep.txt 末段 | `grep -A1 st-datalane data/runtime/process_reaper_keep.txt` |

## 五、呈报（Owner/总统筹）

1. **bcure 全史重算链**（10-08 起，月粒度，2.2 天 5/93 月，内存闸 2.5GiB）：T3/T4/T6(a)
   全部被压。其属主车道与预期工期请统筹核——若判定其使命已被夜跑链+T1 闭环面取代，
   建议属主收官；若保留，本班 T3/T4 执行窗顺延至其收官。
2. **T1×P1 交互缺陷**（24fec802 治本）：呈报作为"计算腿过滤"类改动的通用教训——停算列
   必须同步退出值级比对面，否则跳过判据被 NULL 差异毒化。
3. **T5 钉任务**：day2/3 连跑由值守自动化执行（12:35），满 3 天自动钉
   ZephyrAlpha_EmotionIndexSnapshot+回执写台账；自动化人工撤除点=钉任务成功后。
4. **主区对平降级直改×2**：原因与范围见台账 §一/§七（GW 计数为准）。
