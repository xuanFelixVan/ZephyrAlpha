---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗段)
node_id: D13-44
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-44 日界交接（T 日盘后 → T+1 日盘前的状态移交）

## 1. 定义

夜窗收口环节（dloop next_day 段+三件边界规划器）：T 日盘后状态移交 T+1 日盘前——
src/zephyr/plan_engine/intraday_tomorrow_forecast.py / tomorrow_boundary_planner.py /
overnight_boundary_reviser.py / src/zephyr/trading/shift_handover_checklist.py；
本图唯一跨日闭环回边 D13-44→D13-01（T 日盘后移交→T+1 日 05:30 重启）。
图内决策问题："T 日的判定与边界真的交给 T+1 了吗？交接件今天有几行？"——图硬实查③判定：
交接产物表 judgment_next_day_forecast 按业务日实测已断供多个已收盘交易日；根因锁定在发射件
一处变量名错位→负值被产物校验器 fail-closed 拒发（按桶确定性杀掉多数交易日）；且断供被双层
静默掩盖（编排层段状态硬编码 ok+校准腿扫 0 行照常出数），由本车道人工复跑查出，无任何分级
告警覆盖。build=pending、supply_broken=true、wiring=partial。

## 2. 六向台账

### 2.1 输入面
- 入边四条：D13-34→44（日度拍板后）、D13-40→44、D13-41→44、D13-43→44（map edges——
  夜窗各腿向日界供料）。
- 段宿主：D13-32 圈 next_day 段（dloop_stages=[next_day]，in_phase 实扫真）。
- 业务日锚缺陷：inputs_ref 内嵌交易日串（表侧无交易日列）——不按上海日重算即差一天。

### 2.2 输出面
- 名义产物：judgment_next_day_forecast（c1_market；gap_refs 登记"在册断供，环节面在本格、
  修复归图 12"）+次日预测/边界规划件。
- 实况：supply_broken=true，observed="每圈 1 次（当日实为 0 产出）"；expected_emits_per_trading_day=1。
- fallback：次日 daily_plan 查不到即明写降级并折减置信度（不静默用旧值）——消费侧设计内兜底。
- consumers=count:55（本图最多：code=24,doc=26——src/zephyr/plan_engine/
  intraday_tomorrow_forecast.py:1、src/zephyr/signal_ashare/core/candidate_pool_aggregator.py:10、
  src/zephyr/signal_ashare/core/environment_switch.py:5、
  docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml:158）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-44（partial/pending/⬜，mining_recheck_status=🔨，
  red_reason=broken_supply）。
- 簿 09 硬实查③（断供+根因+双层静默）；骨架 §2 D13-44 行。
- boundary 第 6 条：不画 24/7 三班制交接（shift_handover_checklist 面向连续市场，不覆盖 A 股日界
  ——该件在此仅作代码挂点，非 A 股日界交接真源）。

### 2.4 代码模块
- module_id=MOD-PLAN-029；module_ref=src/zephyr/plan_engine/next_day_forecaster.py:268
  （实存；:268 行内容为弱匹配）。四件边界件实存（本批逐一 ls 核验）。
- 根因件：发射件变量名错位（负值被产物校验器 fail-closed 拒发）——修复归图 12 侧产物校验链。

### 2.5 门禁约束
- silent_layer_zh："编排层段状态与校准腿聚合面掩盖断供"——双层静默=图 laws 第 6 条
  （检出即蒸发/看着≠动手）的最重违例位。
- freshness_severity_zh（一档实测）："断供由本车道人工复跑查出，无任何分级告警覆盖"。
- gap_refs：benchmark:A2 断供无分级覆盖、A4 应产 1 次日界件而实产 0、table:
  c1_market.judgment_next_day_forecast。
- casebooks=MEM-F13#时区与假绿。

### 2.6 自动化触发
- 机制=C_inprocess_stage；cadence declared="夜窗收口→次日 05:30 重启（段界）"、observed=
  "每圈 1 次（当日实为 0 产出）"；trigger_facts metric=none（进程内段无独立产物表面）。
- 跨日闭环：feedback edge D13-44→D13-01（本图唯一跨日回边）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | warn | 四条供料入边在图，但消费这些输入的交接件实产 0 行（供料关系悬空） |
| 输出面 | fail | judgment_next_day_forecast 断供多个已收盘交易日（supply_broken=true 实证） |
| SSOT 真源 | warn | 簿 09 硬实查+gap_refs 完整；但业务日锚藏在引用串（表无交易日列）=口径缺陷在册 |
| 代码模块 | pass | 四件边界件+forecaster 全实存（件齐；坏在数据链不在代码缺失） |
| 门禁约束 | fail | 双层静默（段状态硬编码 ok+校准腿 0 行照常出数）+断供零告警覆盖（A2） |
| 自动化触发 | fail | 段在圈但当日 0 产出；无独立计数面，断供靠人工复跑发现 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：不在 4 gap/6 no_caller/5 hollow 主清单（wiring=partial），但
  supply_broken=true 使其为本段 D 段实质最红格；产物表断供在图 12 waiting_table_gaps 同根登记。
- 建议 1：修发射件变量名错位（fail-closed 拒发根因）——产物校验器保留，坏值应进隔离/重试面
  而非静默按桶杀日。
- 建议 2：双层静默收口——编排层段状态禁硬编码 ok（接段产物行数断言），校准腿 0 行时显式标
  insufficient；断供接 Alerter 分级（A2）。
- 建议 3：表加业务日列或以表名/分区承载交易日，消"引用串藏业务日"口径缺陷（换算前一切
  缺 N 日结论作废的现状）。
