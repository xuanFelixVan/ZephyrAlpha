---
ttl: task_bound
completes_when: 全流通战役收口报告归档
---

# req_sentinel_01 · quality_sentinel 排班正门形态（车道 st-ff-sentinel-20260918）

**事实（均亲验）**
- `src/zephyr/data/quality_sentinel.py` 成品在册（49 条测试），但从未被任何生产入口调用；
- `schedule.yaml` 的 L11 `integrity_check` / L13 `data_supply_sentinel` 槽位在册；
- `scheduler.py:204 _run_special_schedule` 是硬编码分支白名单，`:2110` 对"时段无任务"
  只 `log.warning("时段 %s 无任务")` 后 `return {}`（静默成功）；
- tasks.yaml 266 条任务全部绑 source/capability/provider，特殊时段槽位
  （integrity_check / catchup_guard / data_supply_sentinel / consensus_crosscheck /
  nightly_sentiment）**无一在 tasks.yaml 有条目**。

**冲突**：任务书要求"给 quality_sentinel 补 tasks.yaml 任务条目 + L11 槽位"。字面执行的两条路
各自都造新盲区：新开有名无实的槽位=R-021 假通道（每班唤醒、打日志、返回成功）；
硬塞任务条目=调度器按 provider fetch 必失败。而唯一能干净接线的文件 `scheduler.py` 对本车道是禁写面。

**本车道已做（不需要批准）**：把变异巡检**托管进已活的 L13 槽位**
（`supply_sentinel.run_supply_sentinel` → `quality_sentinel.run_hosted_sweep`），
四要素各有实跑证据（首班真跑 2 findings + 2 告警 / 次班节奏闸跳过零 CH 调用 / 总闸关不查库）。

**请裁**（任一即可闭环，本车道未停等）：
- 甲：认可"托管"为哨兵族唯一排班正门，并把 `scheduler.py` 的 `_run_special_schedule`
  扩为注册表驱动（新槽位无需改码）——需总包放行改 scheduler.py；
- 乙：由 z-failopen/z-alarm（scheduler.py 成品方）加 8 行 `quality_sentinel` 独立分支，
  本车道已备好处方（函数即 `run_hosted_sweep`，含总闸与节奏闸）；
- 丙：判定"哨兵族不应有独立槽位"，则 req 关闭、托管形态转正为惯例。

**默认状态**：托管已生效（不改也不影响其它车道）。风险项：全史 epoch 扫描首次执行较重，
故节奏闸默认 7 天（比原设计"每晚"少，但比"从未执行"多）；若裁定要日频，只需把
`config/quality_sentinel_tables.yaml` 的 `sweep_cadence_days` 改 1。
