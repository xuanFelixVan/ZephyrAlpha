---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-13
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-13 竞价后档位一次性聚合（情绪指数竞价档）

## 1. 定义

交易日 09:30（槽每日 firing）应在 post_auction 槽完成集合竞价收官后的一次性档位聚合（情绪指数 auction 档等）。机生判据：该槽**有效挂载数=0 ∧ 特殊槽分支不存在**=假通道槽——落到调度器「无任务」分支后静默返回空并被记为 executed successfully，日志轮转再自毁证据。决策问题：09:30 这一拍真跑了吗？还是槽位挂着、APScheduler 记 success 而什么都没执行？

地图在册态：wiring=unwired_slot_hollow（我段 4 个之一）、build=partial、red_reason=unwired、idle_slot=true、availability=unreachable、mining_recheck_status=🌑。簿 04 §0.1 A 类：本槽与 eod_reconciliation 是全仓仅有的「零任务∧零分支」两槽=恒假成功。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | D13-11 竞价窗收官产物（快照/档位表） | `config/trading_day_cycle_map.yaml` 入边 D13-11→D13-13；SD13-11 输出面 |
| 输出面 | 情绪指数 auction 档聚合产物——应产 1 拍/交易日（expected_emits_per_trading_day=1）而实产 0 | `config/trading_day_cycle_map.yaml#D13-13` expected_emits_per_trading_day/observed「名义每日 1 拍；实为 0 拍」 |
| SSOT 真源 | 图13 节点契约（行 1071-1148）+ 簿 04 假通道槽判据 | `config/trading_day_cycle_map.yaml#D13-13`；`docs/_working/map_build/fig13_daycycle/04_盘中采集层群.md` §0.1/§1 |
| 代码模块 | **执行体不存在**：post_auction 槽在 schedule.yaml:34 在册但 scheduler.py 无同名特殊分支、无挂载任务（本矿 grep 实核：`post_auction` 在 scheduler.py 零命中）；09:30 那次实跑是死在导入异常上的在途 WIP 未落 HEAD | `src/zephyr/data/config/schedule.yaml:34-37`（槽声明+幽灵池守卫代修注）；`src/zephyr/data/scheduler.py`（grep 零命中实核）；簿 04 §1 |
| 门禁约束 | 假通道槽无痕迹拦截：APScheduler 记 success=失败可见性为负（failure_visibility_zh：假通道槽的痕迹面就是它的反面）；idle_slot_expected=true 机生自证 | `config/trading_day_cycle_map.yaml#D13-13` failure_visibility_zh/machine_facts.idle_slot |
| 自动化触发 | mechanism=A_apscheduler 名义交易日 09:30；30d 任务级 count=0；slot_effective_task_count=0+special_branch_exists=false+idle_slot=true（机生三证） | `config/trading_day_cycle_map.yaml#D13-13` trigger_facts/machine_facts.slot_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 上游 D13-11 竞价采集在产（30d 1,225 拍） |
| 输出面 | fail | 应产 1 拍/交易日实产 0，聚合产物面零在位 |
| SSOT 真源 | pass | 节点契约+簿 04 判据完整；地图锚 scheduler.py:2256 现指熔断代码（锚漂移，工作树在途编辑所致，不判罚） |
| 代码模块 | fail | 槽壳在册而执行体/分支/任务三者全无（grep 实核） |
| 门禁约束 | warn | 假成功无拦截器：G01 表达缺口（unknown 态缺位）的实体案例 |
| 自动化触发 | fail | idle_slot=true： firing 是空转，0 实拍 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：**unwired_slot_hollow 5 个之一（slot:post_auction gap_refs 在册）**；同时是 **D13-G01（无产出证据态缺位，segment=A）挂边的直接受害格**（edges D13-13→D13-G01）。
- 建议：①补聚合执行体并挂任务或落特殊分支（二选一，禁再留槽壳）；②在执行体落地前把槽从 schedule.yaml 摘除或标 disabled，消灭恒假成功；③G01 的机检半边已可用：expected_emits_per_trading_day=1 ∧ idle_slot=true 并读即显红——建议巡检器消费该对。
