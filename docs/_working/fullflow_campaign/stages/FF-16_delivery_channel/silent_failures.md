---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# FF-16 交付通道 · 静默失效面 六向台账（车道 st-ff-silent-20260918）

> 范围＝本车道动过的 FF-16 告警投递/去重/探针注册面。**只填自己改过的子模块**，
> z-alarm 车道的 webhook 面不在本表（同目录不同文件）。
> 判据本体＝验收规范 §1 第⑥向"失败会响"。三态裁定权在总包，此处只"建议"。

| 子模块 | ①入口有料 | ②转化能跑 | ③出口有货 | ④下游能取 | ⑤哨兵在岗 | ⑥失败会响 | 三态（建议） |
|---|---|---|---|---|---|---|---|
| `data/source_health_check.py::_update_failure_streaks`（数据源连续异常告警） | 实测：`results` 由 `run_health_checks()` 逐源产出，调用点 `:554`（同文件 `_latest_results` 生产路径） | 本车道测试真调 3 次（`test_silent_latch_before_delivery.py::TestSourceHealthAlertLatch`），1.9s 内 rc=0 | 真落盘：`_STREAKS_PATH` JSON + `Alerter` failures 文件；测试断言的是**重读磁盘后的 JSON** | 读方：`_STREAKS_PATH` 由本函数自读自写（`json.loads` 于 `:72`）；告警行由 `Alerter._write_failure_file` → `_fanout_critical` 外发 | `data_supply_sentinel.yaml` 不在本件职责内；本件的"哨兵"即告警本身，冷却 300s 在 `alerter._FAILURE_COOLDOWN_SEC` | **已证明能红**：按字节还原"先置闩后投递"→ 2 条测试红；注入故障=真 `NotADirectoryError`（不 mock 防线） | **绿**（①-⑥ 皆有实测；⑥ 有变异证据） |
| `data_eng/data_anomaly_alerter.py::evaluate`（四路异常检测出口路由） | sink 由构造注入；默认 `_default_alert_sink`；实测 21 条既有测试全过 | 真调 `evaluate([sig], now_utc=…, source="t")` ×5 次 | 路由进注入 sink；`_dedup_state` 为进程内态（**无落盘**→跨重启不去重，见下"残留风险"） | sink 消费方=装配期注入；既有测试 23 条覆盖 | 分级阈值 `AL-P1..P4` 在件内；无独立哨兵行 | **已证明能红**：还原"路由前推进去重戳"→ 2 条红（重试腿 + 类型名腿） | **黄**（③④ 依赖注入装配，本车道未追到生产装配点 file:line；⑥已证） |
| `trading/resource_optimization.py::_ExternalNotifier.emit_pressure_event` | snap 由 `ResourceOptimizationEngine` 监控环产出 | 真调 3 条测试 | 外发 `zephyr.shared.event_bus.bus.emit(topic, payload)` | 订阅方未追（本车道只验投递语义）；`tests/resource/test_self_healing.py` 读档位 | 压力阈值注册表 `_load_pressure_thresholds`（既有） | **已证明能红**：还原"emit 前置档位闩"→ 2 条红 | **黄**（④下游订阅方未取证） |
| `trading/health_monitor.py::register_shared_monitoring_probes` | 由 boot 序列调用（`boot_hooks`/`auto_runtime_core` 面） | 真调（测试内） | probe 注册进 `self.probe_fns` | `tick()`/聚合视图消费（既有 21 条测试覆盖） | 本件**就是**哨兵 | **已证明能红**：还原 DEBUG→ 1 条红（WARNING 档位零记录） | **绿（本面向）**；残留：探针数少于预期时**无人计数**，只新增了可见性 → 处方化 |
| `strategy_pipeline/daily_decision_orchestrator.py::_alert`（拍板链播报） | `alert_fn` 注入优先，默认 `pipeline_events.alert` | 真调 | 落 `pipeline_events` 日志 + Alerter 文件 | 同链上游 `_cal_state_base` 等（既有测试：**0 条**，见"覆盖缺口"） | 无 | **已证明能红**：还原 DEBUG→ 1 条红；并断言 `exc_info` 非空 | **黄**（该模块此前零测试；本车道补了 1 条告警面钉，其余面未覆盖） |

## 本表的两条横向结论（交总包）

1. **"看起来在工作"的告警面，其自身测试覆盖此前接近 0**：`daily_decision_orchestrator` 全仓无测试文件
   （`find tests -name "*daily_decision*"` 实测空返回）。z-failopen 也报过同类信号
   （"因加严转红的测试 0 条 = 既有测试面覆盖不到这些路径，本身是缺陷"）。**两条独立证据同向**
   → 建议把"告警/投递面必须有能红钉"作为 FF-16 的收口判据，而非只看功能测试数。
2. **⑥向的判据要写成"下一轮会不会重试"，而不是"有没有日志"**：本车道 6 处收口里 4 处的旧实现
   **都有日志**（甚至 `exc_info=True`），病在**闩先于投递**——只看日志会全绿放过。
   验收规范 §1 第⑥向建议补一句：*"注入投递失败后，第二轮必须观察到重试或升级，
   否则该面判红（日志存在不构成通过）"*。

## 残留风险（未闭，如实列）

- `_dedup_state`（F2）与 `last_pressure_level`（F3）都是**进程内存态**：进程重启即失去去重历史，
  与 F1（**落盘态**）不同级别。F1 之所以更严重，正因为它落盘 → 静默跨重启。
- 处方 `SILENT-P3-R1`（`owner_alerted` 只写不读）落在保命升级路径上，本车道未动。
