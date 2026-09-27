---
ttl: task_bound
title: F13 E0 算力问闸（compute_window_gate）——L02 接线矿道案卷
session: zc-l02-20260927
---

# F13 · E0 算力问闸（compute_window_gate）

> 挖矿基册=docs/_working/fullflow_mining/01_strategy_factory/01_f13_e0_compute_gate.md（SF-A，09-25）。本卷=L02 独立复核+09-27 增量实证，不重抄基册。

## 一、六向台账
| 向 | 实证锚点（09-27 复核） |
|----|------|
| 上游 | c1_market.trade_calendar（CH）；fetch_is_trading_day→zephyr.data.ch_writer.get_client_strict，日历缺失 fail-closed（compute_window_gate.py:111-131） |
| 下游 | 消费端实测 17 文件命中（grep compute_window_gate，09-27）：backtest 侧 6 件（compute_window_gate/factory_intake_pipeline/factory_grid_executor/hypothesis_translator/lane_c2_agentic_miner/lane_c_formula_miner）+t1_t2_handover.py（SF-A 13 家单之外新增）+generate_resource_profile_registry+ai_layer/scheduling/dispatcher+frontend/api_server+gov_enforcement/resource_schedule_gate+intelligence/exam_trigger_scheduler+config/{comparison_policy,resource_profile_registry}.yaml+script-manifest.yaml |
| 自动触发 | 无常驻无计划任务：拉式纯函数+CLI，schtasks /query 09-27 实测 factory/lane/intake/compute 零命中；`noqa: m11-perm-manual-legitimate` 在码 |
| 真源注册表 | MOD-BT-151=path_ownership_map.yaml:9397,15774（grep 实证）；图 9 节点 FAC-E0 build_status: partial（strategy_production_map.yaml:45-63，本日重读）；docs/03_modules 无本 MOD 蓝图目录（grep 全域仅 path_ownership_map 命中） |
| 门禁质量尺 | 四理由码封闭枚举；naive datetime 拒收；未知 compute_class 从重 fail-closed（:88-90）；CLI exit 0/3/1 契约；tests/backtest/test_compute_window_gate.py 在盘 |
| 运行状态 | 绿（本体）。09-16 凌晨窗误拒治本注释在码（:69-77）；代码 grep 零 jsonl/log 写盘——**审计落盘仍缺**（store_refs 承诺 .runtime/logs/ 90 天未兑现） |

## 二、子模块三级枚举
1. **代码面（scripts/backtest/compute_window_gate.py，行号 09-27 复核）**：classify_window:69｜needs_heavy_window:88｜gate_decision:93（四理由码）｜fetch_is_trading_day:117｜check_gate:131｜CLI main:141。
2. **注册表/文档面**：path_ownership_map.yaml:9397,15774（MOD-BT-151）；strategy_production_map.yaml FAC-E0（store_refs 声称调度日志 .runtime/logs/ 90d）；设计出处=2026-09-13-strategy-factory-pipeline-discussion.md（v4/v5 自研薄调度层）；tests/backtest/test_compute_window_gate.py。
3. **运行面**：.runtime/logs/ 无 gate 审计文件（判决零落盘实况）；无常驻/无计划任务（合法形态）；消费端 17 文件接线为真实 import 面。

## 三、接线四态独立复核
- 图 9 四态：partial（build_status 自报）→ **本卷维持 partial**，差距唯一=审计落盘。
- 消费端接线独立重数：SF-A 记 13，09-27 实测 17 文件命中（新增 t1_t2_handover.py 消费+script-manifest 登记+2 个 tmp 残骸计入 grep）——接线只增未减。
- **骨架勘误**：①SF-A 概述断点⑩"scripts/backtest/ 残留 5 个 .tmp.*"已失效——09-27 find scripts -name "*.tmp.*" 实测 backtest 侧零残留；但 **scripts/ 根部新增 2 个 script-manifest.yaml.*.tmp 残骸**（safe_write 中断残留，禁本车道代清，登记待施工批）。②图 9 name_zh"心跳"仍误导（实为拉式问闸，无心跳进程）——沿用基册勘误未改。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 判决零审计落盘 | store_refs 承诺 .runtime/logs/ 90d；代码零写盘；.runtime/logs 无 gate 文件 | 施工：check_gate 追加 append-only JSONL（logs/ 子目录合法位）≈0.5 天 | P1 |
| 2 | 命名误导"心跳" | FAC-E0 name_zh vs 拉式库函数实态 | 文档工：下版图改名"算力问闸" | P2 |
| 3 | scripts/ 根 2 个 script-manifest tmp 残骸 | scripts\script-manifest.yaml.40056.tmp、.35456.tmp（09-27 ls 实证） | 施工批代清+查 safe_write 残留根因 | P2 |
| 4 | 09:00/15:30 边界口径无单页文档 | 代码注释在、对外文档缺 | 文档工（低优） | P2 |

## 五、自审闸三态
- **三态：built（闸门本体）／partial（按图 9 store_refs 承诺口径）**。沿用基册结论+复核无新缺口（审计落盘仍缺、接线面只增）；勘误仅涉 tmp 残骸现状（§三）。

## 六、复跑命令
```bash
python scripts/backtest/compute_window_gate.py window
python scripts/backtest/compute_window_gate.py check --purpose mining_audit --compute-class local_gpu
grep -rln "compute_window_gate" scripts/ src/ config/ | grep -v __pycache__ | wc -l   # 17（含 manifest+tmp）
grep -n "jsonl\|append\|log" scripts/backtest/compute_window_gate.py                  # 零写盘=缺口①实证
find scripts -name "*.tmp.*" 2>/dev/null
```
