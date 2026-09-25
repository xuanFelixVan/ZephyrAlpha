---
ttl: task_bound
lane: M2 回测模拟链
session: st-commitspeed-tbl-20260924
created: "2026-09-25"
status: mining_delivered
create_guard: 挖矿车道零 commit 零 enqueue；本目录 8 册 creation_token 由落地车道随批补办（同 11_integrated_backtest_audit.md 先例）
---

# M2 车道作业簿 · 总览（回测/模拟盘/GPU 矩阵链）

> 只读挖矿实证（零实跑回测/零下单路径）；挖掘窗口 2026-09-25 00:30-01:40，期间 GPU T1（grid_20260924-213246）在跑，本车道只读观测未干预。
> 模板与判据真源=本目录上级 `00_orchestration.md` §二/§三。

## 一、分册清单与子环节数

| 册 | 环节域 | 子环节数 | 三态 |
|---|---|---|---|
| 01_auto_runtime.md | AutoRuntime Core 入口+常驻骨架 | 8 | 挖干可施工（运行态归 M5 实测） |
| 02_backtest.md | 回测脚本面（演练/危机/挂图/EXP 出证/联赛/翻译引擎） | 10 | 挖干可施工 |
| 03_sim_daily.md | 模拟盘日链（plan-bridge/e4-replay/report/settle/bridge-execute/账本/日刊/治理） | 11 | 挖干可施工 |
| 04_gpu_matrix.md | GPU 三层矩阵（prereg→输入包→T0/T1/T2→考试→DSR→毕业生） | 9 | 挖干可施工（T1 跑批中在飞） |
| 05_cost_gates.md | 成本门（考尺三道门/哑门病灶/成本两真相分裂） | 7 | 挖干可施工（2 项待裁） |
| 06_ibt_backtest.md | IBT 整装回测（四窗/协议/红蓝/HOLDOUT/审计八环节） | 8 | 挖干可施工（3 项跨车道移交） |
| 07_pf_alloc.md | pf_alloc 组合分配链（五模块装配体+13 分配器） | 6 | 挖干可施工 |
| pending_rulings.md | 待裁台账（5 案） | — | 待裁 |

**合计子环节 59**；三态汇总：挖干可施工 7 册 / 待挖 0 / 待裁 5 案（见 pending_rulings.md）。

## 二、链路一张图（M2 视角，供 M0 骨架班交叉验证）

```
数据链(M1) → 回测引擎两体: _c4_engine(向量化考尺) + DefaultBacktestEngine(整装 IBT)
  → 策略管线(strategy_pipeline: fw_backtest/intake/lifecycle_fsm/promotion_advisory)
  → 考试门(f06_e4_wfa_exam + exam_cost_gate 五档成本门 + 换手门)
  → GPU 三层矩阵搜索(factory_grid_executor: prereg→T0 200→T1→T2→n_trial_ledger DSR)
  → 毕业生 → auto_mount 挂图 → pf_alloc 组合分配(SIM_DAILY 事件驱动再权)
  → 模拟盘(sim_paper_ledger 账本 → sim_daily_runner plan-bridge/bridge-execute
     → sim_platform_journal 日刊 → deviation/attribution/governance/promotion)
  → (实盘侧四禁+三道锁，归 13_trading_chain_audit.md / M3，本车道只引用不重挖)
```

## 三、历史病灶闭环总账（Owner 点名的五类，全车道横向）

| 病灶 | 状态 | 证据锚点 |
|---|---|---|
| 假绿 | **两活体**：①kline_sector_intraday 5m/15m/30m/60m 四档停 09-10 仍报 SUCCESS；②GPU 巡检口径"产物目录增长"与实现矛盾（manifest 完赛才一次性落盘，跑中目录恒空） | e2e_integration/LEDGER.md ④·进度；factory_grid_executor.py:854-886 |
| 超时 | **已防未愈**： serializer 链挂死提交进程占 lease 2.4h 被"CPU 双采样零增长+超时 48 倍"机械判死（IBT 台账 06:0x）——判死机制有效；SessionRegistry PID 复用/心跳超时误判仍登记为在飞风险 | IBT-CAMPAIGN-LEDGER.md 尾；10_evaporation_forensics.md:66 |
| 新鲜窗 | **主链已闭**：日刊健检1 `expected_fresh_date` 时点感知治本（09-15..21 十行假阳→T-1 口径，fail-closed 回退）；**未闭**：IBT 批 D 新鲜窗重考产物仓内未见（IBT-F01），OOS 敏感性跨批 sharpe 漂移（hfq 夜跑带推进）已用"同批六档"配方闭 | sim_platform_journal.py:59-83；11_integrated_backtest_audit.md §0⑥ |
| 成本门哑门 | **已修**：prereg pass_criteria 曾全仓 0 消费（哑门三修批 A）→ k4 池化终批以陈旧快照落地吞并复活件（00:43 P0）→ 复活批 q-0006 落地；现 exam_cost_gate 消费面=f06/exam_cost_reexam/批F 三路实证在码 | exam_cost_gate.py 头 CONSUMERS；factory_grid_executor.py:799-812 |
| 状态轴列名坑 | **主干已修**：温度计冒充六段（异轴顶替）→ 改用法定判定器 `resolve_six_phase`（auto_mount.py:248）物化 1816 日标签表；`load_phase_panel` 双写翻倍+PIT 尾窗已修（D-3，76 项测试绿）；**未闭**：六段词表三套映射两套冲突（同闸宽差 75%，D-14）升级 Owner 未裁；financial_derived 探针列名不符已澄清为探测问题非数据缺失 | t0_matrix/FINAL_REPORT D-1/D-3/D-14；IBT-DATA-MATRIX.md:28 |

## 四、与邻车道边界（防重挖）

- 提交链/commit 侧=commit_speedup 战役，不重挖。
- 实盘四禁与权限门=13_trading_chain_audit.md（已挖，本车道 03 册只引用其四禁正典与三道锁）。
- 计划任务/belt/daemon 群=M5（本车道只实测了 4 个 M2 相关任务 State=Ready）。
- 数据面 469 vs 800+ 宇宙问题=12 数据面宇宙审计（引用不重挖）。

## 五、复核命令（10 分钟总览）

```bash
# 1) 各册六向台账抽查
ls docs/_working/fullflow_mining/m2_backtest_sim/
# 2) GPU T1 在飞（只读观测）
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Select-Object ProcessId,CommandLine | Format-List" | grep -i grid
ls -la .runtime/logs/grid_t1_20260924.log   # 日志应增长
# 3) 关键锚点文件存在性
ls scripts/backtest/ibt/ scripts/backtest/sim_daily_runner.py config/search_space_prereg.yaml config/exam_scale_cost_gate.yaml src/zephyr/pf_alloc/allocation_orchestrator.py
# 4) 测试面计数（禁实跑，只数）
ls tests/backtest | wc -l   # 119
```
