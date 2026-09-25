---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F13 E0 算力调度心跳（拉式闸门）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-BT-151
map_node: FAC-E0
---

# F13 · E0 算力闸（compute_window_gate）

## 一、环节定义与边界
一句话：重算力任务在被事件触发的开工时刻先问闸——交易日 09:00-15:30 只许轻任务，重算力（挖掘训练/批测/遗传优化）排收盘后（≥15:30）、开盘前（<09:00）与休市日；trade_calendar 当闸，日历缺失 fail-closed。
上游供料=c1_market.trade_calendar（CH，SSE 口径）；下游消费=全工厂重任务开工点（六车道挖掘/网格执行/翻译/批测）+治理侧（commit gate）+AI 层调度。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | `c1_market.trade_calendar`（SQL_CAL_DAY，compute_window_gate.py:111-114）；`fetch_is_trading_day` 经 `zephyr.data.ch_writer.get_client_strict`，日历未覆盖/通道故障→None→fail-closed |
| 下游消费 | grep 实测 13 文件：factory_intake_pipeline.py:84（preflight）、factory_grid_executor.py、hypothesis_translator.py、lane_c_formula_miner.py:403、lane_c2_agentic_miner.py、ai_layer/scheduling/dispatcher.py、frontend/dashboard/api_server.py、gov_enforcement/commit_gates/resource_schedule_gate.py、intelligence/model_profiling/exam_trigger_scheduler.py + config/comparison_policy.yaml、config/resource_profile_registry.yaml |
| 自动化触发 | 无常驻（铁律正确形态）：拉式纯函数+CLI，`noqa: m11-perm-manual-legitimate` 声明在案；"自动触发"由各任务自身事件链承担 |
| 真源与注册表 | MOD-BT-151 在 path_ownership_map.yaml:9397,15774 在册；图9 FAC-E0 build_status=partial；设计出处=讨论稿 v4/v5"自研薄调度层（不引 Airflow/Dagster）" |
| 门禁与质量尺 | 四枚理由码（gate_allow_light_always/gate_allow_off_hours/gate_deny_trading_hours/gate_deny_calendar_unknown）；naive datetime 拒收（RULE-SCHEMA-TZ）；未知 compute_class 从重 fail-closed（compute_window_gate.py:88-90）；CLI 约定 exit 0=放行/3=拒/1=基础设施失败 |
| 当前运行状态 | **绿（本体）**。证据：①tests/backtest/test_compute_window_gate.py 在盘；②治本记录在码——09-16 classify_window 凌晨窗修正（09-14 07:10/07:11 与 09-16 00:21 三次误拒实证，compute_window_gate.py:69-77 注释）；③消费端 13 处真实 import 接线（非纸面）。**黄点**：闸门判决零落盘（见堵点①） |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| 窗档分类纯函数 classify_window | scripts/backtest/compute_window_gate.py:69 | built（09-16 治本版） |
| 闸门判决纯函数 gate_decision | 同上:93 | built（四理由码） |
| compute_class→权重映射 needs_heavy_window | 同上:88 | built（local/api=轻，local_gpu/mixed=重，未知=重） |
| 日历查询 fetch_is_trading_day | 同上:117 | built（fail-closed→None） |
| 开工第一问 check_gate | 同上:131 | built |
| CLI（check/window） | 同上:141-163 | built |
| 闸门判决落盘/审计 | — | **missing**（store_refs 声称 .runtime/logs/ 90 天，代码无任何写盘；.runtime/logs/ 实测无 gate 相关文件） |

## 四、堵点与病灶
1. **判决零审计**：现象=重任务问闸结果无落盘，owner 无法回溯"何时谁被拒/放行"；根因=模块设计为纯函数返回 dict，store_refs（图9）的调度日志承诺无人兑现；修法=check_gate 追加 append-only JSONL（.runtime/logs/compute_gate.jsonl，purpose/decision/reason_code/ts，注意 .runtime 根禁写→放 logs/ 子目录合法）或轻量 CH 表；工作量≈0.5 天；属本车道可修。
2. **命名误导**："心跳"实为拉式问闸库——无常驻心跳进程（这恰是"事件触发禁定时器"的正确形态）；修法=图9 下版把 name_zh 改"算力问闸"；纯文档工。
3. **时钟边界双缓冲依赖人工理解**：09:00/15:30 保守带在码有注释，但无对外口径文档单页；低优。

## 五、提速与合并机会
- 已是全项目复用件（13 消费端）；无需合并。可合并点=各车道的问闸样板代码（check_gate+smoke 豁免判断）可抽 1 个 `ensure_heavy_window_or_smoke(purpose, smoke)` 装饰器——五处样板合一，≈0.5 天。

## 六、自审闸三态
- **三态结论：built（闸门本体）／图9 partial 的差距=审计落盘缺位**。
- **差什么才算 built（按图9 store_refs 承诺口径）**：①闸门判决落盘（JSONL 或 CH）+90 天保留；②（可选）夜批汇总带 gate 统计。若按"拉式闸门纯函数"最小口径，现状即 built。

## 七、复核命令
```bash
python scripts/backtest/compute_window_gate.py window          # 现态窗档
python scripts/backtest/compute_window_gate.py check --purpose mining_audit --compute-class local_gpu  # 问闸演练
grep -rln "compute_window_gate" scripts/ src/ | grep -v __pycache__   # 13 消费端
python -m pytest tests/backtest/test_compute_window_gate.py -q
```
