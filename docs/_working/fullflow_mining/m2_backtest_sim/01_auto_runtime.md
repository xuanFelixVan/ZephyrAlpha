---
ttl: task_bound
volume: 01_auto_runtime
session: st-commitspeed-tbl-20260924
---

# 01 · AutoRuntime Core（python -m zephyr.trading）

## 一、环节定义与边界
常驻运行时骨架：boot 自检→组件装配→reconcile 心跳循环→优雅停机。上游=配置（RuntimeConfig）+能力注册表；下游=交易域全部子服务（任务队列/夜班队列/dream cycle/健康监控）。**运行态巡检归 M5**，本册挖代码结构与接线。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | RuntimeConfig（runtime_config.py）；CapabilityRegistry（capability_registry.py）；boot_hooks |
| 下游消费 | task_queue/blueprint_watcher/fle_scheduler/dream_cycle/health_monitor/night_shift_queue（auto_runtime_core.py:184-306 属性装配体）；status_dashboard |
| 自动化触发 | CLI 手动启动（__main__.py:17-18 双豁免注记：M02 主入口 reconcile 循环、M10 time.sleep 心跳均登记豁免）；boot 后自走 |
| 真源与注册表 | blueprint=docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md（MOD-INF-035）；algo_flow=docs/03_modules/_domain_trading/algo_flow/__main__.yaml |
| 门禁与质量尺 | tests/trading/ 86 件；MEMORY 上限=容器外 RLIMIT_AS 4GB（__main__.py:36-53，Windows 无 resource 模块静默跳过——实测本机不生效）；SIGINT+SIGTERM 双信号优雅停机（__main__.py:85-88，5.26.5 修复） |
| 当前运行状态 | **黄**：本车道禁跑常驻未实测 boot；代码面全在（auto_runtime_core.py 1300 行，boot():308，reconcile 循环 __main__.py:94-103）；心跳 daemon 41380 存活性=reaper --status 输出 drift 段（本轮实测活） |

## 三、子模块清单（8 子环节，两源交叉=ls src/zephyr/trading/ × grep 装配点）

| # | 子环节 | 入口 file:line | 状态 |
|---|---|---|---|
| 1.1 | CLI 入口+内存防线 | src/zephyr/trading/__main__.py:56（main），:36（_set_memory_limit） | 绿（豁免注记在） |
| 1.2 | Boot 编排（RBAC/任务队列/蓝图 watcher/FLE） | auto_runtime_core.py:308 boot()，:353 _bootstrap_rbac，:414 cron 注册，:429 hooks，:437 队列，:445 watcher | 绿（结构）；运行态黄 |
| 1.3 | Reconcile 心跳 | __main__.py:94-103（poll_interval 缺省 5s，--once 单轮） | 绿 |
| 1.4 | 组件装配体（13 属性注入：lifecycle/fle/local/vms/registry/audit/night/dream/health/task_learner/ollama/embedding） | auto_runtime_core.py:184-306 | 绿 |
| 1.5 | Ollama 拉活与升级协议 | auto_runtime_core.py:385-411（ensure_ollama_running/escalation_protocol） | 绿 |
| 1.6 | GPU 侧监控件 | gpu_monitor.py:21（nvidia-smi 采集器）；gpu_consensus_scheduler.py:28（algo_flow 外锚，asyncio，Stage4 gpu_status:226） | 绿（结构）；M2 车道实测=本轮 nvidia-smi 巡检由 GPU 战役卷宗执行，本册不重复 |
| 1.7 | 交易域兄弟件（60+：conductor/work_orchestrator/work_dag/verdict_engine/eod_processor/settlement_reconciliation/three_way_reconciliation/post_settlement_pipeline/pnl_calculator/admission_controller/stop_gate 等） | src/zephyr/trading/ 实测 ls 60 文件 | 黄：逐一六向属 M5/13 车道，本册只登记不展开 |
| 1.8 | 进程 reaper（守护闭环） | process_reaper.py；计划任务经 scripts/register_process_reaper_task.ps1 | 绿（本轮实测：scanned=20 whitelist_hits=13 killed=0） |

## 四、堵点与病灶
1. **RLIMIT_AS 在 Windows 恒不生效**（__main__.py:44-46 静默 return）——内存二级防线在本机为空，兜底只剩 reaper watermark。修法：Windows 用 Job Object API 或 job 参数量级告警。工作量 S。**不属本车道**（M5/运行时）。
2. **reconcile 循环为轮询设计**（M10 豁免自注"转纯事件驱动需重构 AutoRuntimeCore 内部架构"）——与宪法 §9.3"reconciler 禁 sleep-loop"存在豁免张力，豁免已登记属合法，但"永久系统四要素"审计时需带此注记。
3. boot_report 失败仅 print+exit(1)（__main__.py:72-74），无告警通道——人工启动场景可接受，若被调度拉起则静默死。修法：接 AlertManager。工作量 S。

## 五、提速与合并机会
- gpu_monitor/gpu_consensus_scheduler 与 scripts/backtest/factory_grid_executor 的 GPU 巡检（nvidia-smi 手工口径，03_gpu_campaign.md §二）三处并存：可合并为单一 GPU 健康探针（M5 提速案候选）。

## 六、自审闸三态
**挖干可施工**（结构面六向有证；运行态两向如实标黄并移交 M5 实测 boot）。堵点 3 条均有根因+修法，均不属本车道修。

## 七、复核命令
```bash
sed -n '56,110p' src/zephyr/trading/__main__.py
grep -n "def boot\|def reconcile" src/zephyr/trading/auto_runtime_core.py
ls src/zephyr/trading/ | wc -l   # 60+
ls tests/trading | wc -l         # 86
```
