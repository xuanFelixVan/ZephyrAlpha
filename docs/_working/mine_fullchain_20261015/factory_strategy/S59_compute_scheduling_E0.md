---
ttl: task_bound
---
# S59 FAC-E0 算力调度（骨架行 59）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E0）。所有数字为 2026-10-15 实读。

## 1. 定义

算力调度心跳（FAC-E0，stage 节点，build_status=partial）：判定"现在能不能跑重算力任务、该跑哪条车道的活"。交易日白天只许轻任务，重算力（挖掘训练/批测/遗传优化）全排收盘后与休市日；trade_calendar 当闸门；事件触发禁定时器；日历缺失 fail-closed。回测量是工厂经济学最大成本项。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | `config/resource_profile_registry.yaml`（实读：total_entities=109、mem_ceiling_gb 在册、e0_mapping_note 行 48）；`scripts/backtest/compute_window_gate.py`（265 行，NODE_CLASS_WEIGHT：local→light，local_gpu/mixed→heavy，缺省从重 fail-closed）；`src/zephyr/data/trading_calendar.py` 实存 |
| 输出面 | 图 store_refs：调度日志 `.runtime/logs/`（key=时间窗，retention 90 天）；闸门产出 gate_decision 四枚理由码（compute_window_gate.py 行 65 WINDOW_HEAVY_OK 等）；`src/zephyr/backtest/core/batch_window_preflight.py` 批次窗预检（FAC-E0-M-002）实存 |
| SSOT 真源 | `config/strategy_production_map.yaml`（REG-MAP-FACTORY-001，ROOR 行 617-620）E0 组 18 节点；e0 映射真源=`scripts/backtest/compute_window_gate.py`（registry e0_mapping_note 自注"E0 真源 compute_window_gate.py 不动"）；排班真源=`config/resource_profile_registry.yaml`（机生，生成器=`scripts/governance/generators/generate_resource_profile_registry.py`，e0 映射在其行 2056） |
| 代码模块 | `scripts/backtest/compute_window_gate.py`（MOD-BT-151 拉式闸门本体：classify_window 行 90/check_ignition）；`src/zephyr/data/scheduler.py`、`src/zephyr/trading/process_reaper.py`（实存）；dir: 卡=`docs/03_modules/_domain_infrastructure_runtime/resource_scheduler`、`docs/03_modules/_domain_data_eng/gpu_resource_manager`（实存）；`src/zephyr/intelligence/model_profiling/exam_trigger_scheduler.py` 实存 |
| 门禁约束 | RESOURCE-SCHEDULE gate（in_process_gate_registry.yaml 行 708-713，priority=144：互斥组重叠/内存天花板/E0 交易时段三检查+真源漂移 warn，own-scope，E0 纯函数最小 import 复用 compute_window_gate，异常/日历未知 fail-closed）；测试=`tests/governance/commit_gates/test_resource_schedule_gate.py` |
| 自动化触发 | 事件触发（trade_calendar 闸门+数据到达），无 cron/sleep-loop（compute_window_gate.py 行 30/12 自注）；模型考试触发=event_model_exam_trigger 排班实体（exam_trigger_scheduler.py [CONSUMERS] 头注：task_gate_dispatch_hook 硬门 opt-in 默认不启用） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | pass | 109 实体注册表+映射规则双实证 |
| 输出面 | pass | 闸门理由码+调度日志落位明确 |
| SSOT 真源 | warn | e0 映射不在注册表在生成器（registry 自注），审计需读生成器行 2056，两跳可达但非单点 |
| 代码模块 | pass | 全部指针实存（含两个 dir: 卡） |
| 门禁约束 | pass | RESOURCE-SCHEDULE 在册 enabled、own-scope、fail-closed 语义齐 |
| 自动化触发 | pass | 事件触发合规；exam_trigger opt-in 默认不启用=声明与实现一致 |

小计：5 pass / 1 warn / 0 fail。

## 4. 缺口与建议

1. 本层 18 节点中 17 个 mechanism 节点零边（全图 17 条边里 E0 只占 1 条出边 E0→E1）——层内机制挂载为"名挂"非"线挂"。
2. trigger_facts=null 15/18（F3 车道回填欠账，图自注 pending-facts）。
3. FAC-E0 stage 本体 build_status=partial（15:30 收盘缓冲/MOD-BT-151 已建但层判 partial）。
4. 全段共性缺口（挂本层守卫）：本图守卫 FAC-MAP-M-001/M-002（MOD-BT-080/081，stage=E0）声称的 commit 门禁链三断——gate_registry.yaml FACTORY-MAP status=deprecated redirect_to MAP-ALIGNMENT（行 1953-1967）→ MAP-ALIGNMENT files_trigger 无 config/strategy_production_map.yaml → in_process_gate_registry 107 门无 strategy_factory_map_gate 条目；门体文件 `src/zephyr/gov_enforcement/commit_gates/strategy_factory_map_gate.py` 成孤儿（自注 priority=148，图头注 142，对齐清单 §3 图 9 行写 142——三处数字漂移）。建议：恢复注册或把图 YAML/校验器补进 MAP-ALIGNMENT 触发行，三处 priority 对齐。
