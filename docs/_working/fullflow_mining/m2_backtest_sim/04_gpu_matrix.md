---
ttl: task_bound
volume: 04_gpu_matrix
session: st-commitspeed-tbl-20260924
---

# 04 · GPU 三层矩阵搜索（prereg→T0→T1/T2→考试→DSR→毕业生）

## 一、环节定义与边界
算法搜索主战链：预注册冻结（fail-closed 预算闸）→条件轴输入包→T0 标定→T1/T2 分层网格（五档成本门全程真跑）→f06 考试→n_trial_ledger DSR 记账→毕业生→模拟盘观察档。上游=数据链+输入包生成器；下游=考试门（05 册）/auto_mount 挂图/模拟盘。**本车道挖矿期间 T1 在飞，只读观测。**

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | config/search_space_prereg.yaml（schema v2.0.0，frozen_at=2026-09-24T22:00 裁定#413，frozen_by/owner_signoff=#413）；网格轴机器真源=config/position_recipe_grid_schema.yaml（GridCompiler 消费，I_cost_tier 恒折叠=成本档禁作搜索轴）；条件输入包=data/strategy_intake/grid_t0_conditional_v1/（matrix 1816 行×18 列/cells 20 胞 15 达标/negatives 5 条，sha256 三锚在 t0 FINAL_REPORT 任务④） |
| 下游消费 | data/strategy_intake/grid_<ts>/manifest.csv+negatives.csv+net_returns.parquet（无 pyarrow 兜底 csv.gz）；T2 晋级集=主效应前 20%；f06_e4_wfa_exam 考试；n_trial_ledger（DSR 分母，裁定#306 N_eff 口径）；negative_result_promise=负结果如实入库禁删改 |
| 自动化触发 | **当前 T1=脱管进程非计划任务**（实测 PID 30924 命令行 factory_grid_executor，21:32 发车）；另有计划任务 ZephyrAlpha_F06Grid（State=Ready，考卷侧）；跑中禁改 prereg（冻结语义：改空间=作废重开） |
| 真源与注册表 | 03_gpu_campaign.md（方案②现行+方案①升级案）；e2e_integration/LEDGER.md（注水验证册=T0 200→T1 17100→T2 13000 原口径）；prereg budget_caps（预算封顶）；cmd_ledger R43 点火记录 |
| 门禁与质量尺 | _apply_prereg_budget fail-closed（缺册/缺字段=SystemExit 禁开跑，factory_grid_executor.py:923-967）；轻档须为全档子集（validate_scan_tiers 两档合法）；T1 完赛验收四零=manifest 3700 行/backtest_dead=0/eval_dead=0/degraded=0（03_gpu_campaign.md §二4）；主目标函数=cost_adjusted_sharpe（毛夏普仅观察） |
| 当前运行状态 | **绿（在飞）**：grid_20260924-213246 发车 09-24 21:32，T1 3700 格全档，35.33s/格实测口径→预计周六 08:00-14:00 完；本轮实测（01:25）进程活+日志增长 195KB；产物目录空=设计使然（完赛一次性落盘，见堵点2） |

## 三、子模块清单（9 子环节）

| # | 子环节 | 入口 file:line | 状态 |
|---|---|---|---|
| 4.1 | 预注册冻结+预算闸：budget_caps 读取（缺册 SystemExit 文案与原逐字一致）；分层语义字段 cost_gate_t1_tiers_bp（null=在场未冻结 fail-closed；非子集 SystemExit） | factory_grid_executor.py:919-967（STAGED_TIERS_KEY）；方案①代码班已落地（03_gpu_campaign.md §三1 的"代码缺口"已闭） | 绿 |
| 4.2 | 批次 A 主入口 run_batch：recipe 求值→回测→逐格五档成本扫描（引擎口径唯一=daily_net_returns slippage_bp kwarg，门零重实现）；扫描异常=gate 层阴性 fail-closed 禁静默 | factory_grid_executor.py:667-812（cost_gate_tiers_bp kwarg :667；档位扫描 :797-812） | 绿 |
| 4.3 | 产物落盘：manifest（asdict+values_json）+全员阴性批兼容（legacy KeyError 崩批已修，errors="ignore" 注记）+net_returns parquet/csv.gz 兜底 | factory_grid_executor.py:854-890 | 绿 |
| 4.4 | 数据面：mkt_cap 宽表（total_mv 2020-01 起，空→None fail-closed 记阴性）；行业锚一次拉取失败→行业族格点 fail-closed 降级记 degraded；industry_map 剔非词表行（grid log 实测 1 行） | factory_grid_executor.py:210,230,257,291 | 绿 |
| 4.5 | 条件轴输入包：情绪灰度×大盘状态两轴全史，30 日地板达标胞才可作条件轴/可计 n；板块腿 17 交易日=观察标注层禁入统计判据 | src/zephyr/backtest/regime_validation/condition_package.py:17-32；condition_attribution（T0 首跑 1800 行主效应表，e2e LEDGER:141） | 绿；测试 test_condition_package.py/test_condition_attribution.py |
| 4.6 | T0 条件包（做T 维）：t1_amp_bucket3 边界 116.75/188.25bp 只用 ≤2025-09-09 定档（变异探针证越切点即红）；euphoria/ignition 不达地板如实入 negatives 禁凑轴 | t0_matrix/FINAL_REPORT.md 任务④；scripts/audit/t0_gpu_condition_pack.py（一条命令重建）；tests/audit/test_t0_gpu_condition_pack.py | 绿 |
| 4.7 | 做T 矩阵判卷：34 法三态（✅可考 7/⏳待料 13/⛔阻断 8/🔧执行层 6）；E4 双门重考 verdict=STATE_GATE_NEVER_TRIGGERED（真实日内往返 26 对<30 土规，禁造料）；两门互斥发现（闭卷窗 1566 日同时放行仅 200 日 12.8%，两支路交集=0→GPU 条件维实际自由度≈1） | docs/_working/t0_matrix/T0_SCHEME_MATRIX.md（判定口径表）；FINAL_REPORT.md 一/二章 | 绿（judgment 诚实不足如实落档） |
| 4.8 | GPU 交易域监控件（gpu_monitor/gpu_consensus_scheduler，与跑批巡检三处并存） | src/zephyr/trading/gpu_monitor.py:21；gpu_consensus_scheduler.py:28 | 绿（结构）；合并机会见 01 册 |
| 4.9 | DSR 记账与负结果库：n_trial_ledger（summary.json 会自动计 DSR 分母=科学污染，故 t0 包明令不落 summary.json——D-6）；negatives.csv schema 合 NegativeRecord 带死亡层+死因 | t0 FINAL_REPORT 清单 A D-6/D-7；src/zephyr/backtest/core/n_trial_ledger.py | 绿 |

## 四、堵点与病灶
1. **规模口径三套并存+任务锚点 24990 无出处（勘误级）**：原注水册 T0 200→T1 17100→T2 13000（e2e LEDGER:30）；现行方案② T1 3700/T2 900（R43+prereg）；**挖矿令原文"T0 200格/24990格"在全仓 grep 无命中**（仅 CSV 巧合同数）。已入 pending_rulings 请总筹定版数字，防下班会按 24990 等验收。
2. **跑中观测性与守望清单矛盾（假绿风险活体）**：manifest/negatives/net_returns 全部 run_batch 末尾一次性落盘（factory_grid_executor.py:854-886），跑中 grid_<ts>/ 恒空；而 03_gpu_campaign.md §二守望点3 写"产物目录增长（grid_*/ 中间件）"——按清单巡检会误判死亡。实测佐证：产物目录自 21:32 起恒空但进程活+log 增长。修法：①守望清单改口径=tasklist+日志时间戳；②executor 加每 N 格 append 进度文件（progress.jsonl）。工作量 S，**建议 T1 完赛后修，勿跑中动**。
3. **stdout 缓冲+FutureWarning 淹没**：03_gpu_campaign.md 自注"stdout 有缓冲，钳制消息可能晚刷"；实测日志 19.5 万字节几乎全为 pct_change 弃用告警（02 册堵点2）。两因叠加=跑中"日志在长但读不到进度"。修法：python -u+warnings 收敛。
4. **方案② vs 方案①的预算差**：全档 35.33s/格（T1 36h）vs 轻档预估 6-7s/格（17h）——本轮选方案②（零代码零违规），方案①代码已落地（4.1）下窗可用；红蓝对拍（Spearman 0.9998/top50 50:50 历史基准）已有 calibrate_cost_tier_redblue.py 载体（05 册）。
5. **regime_snapshot_history 多 run 重叠无机械闸**（W_IS 2312 行=2 run，消费靠 runner 手工锁 run id，IBT-DATA-MATRIX §1）——GPU 条件轴同源风险。修法：condition_package 加 run 版本钉。M。跨车道移交。

## 五、提速与合并机会
- T1 轻档路径（4.1）已落地：下窗 T2/T3 跑批可直接省 ~50% 墙钟（36h→17h 量级，03_gpu_campaign §三5 预算复核）。
- factory_grid_executor 与 f06_e4_wfa_exam/exam_cost_reexam 三件共享五档成本扫描+引擎口径（05 册联动）：已统一引擎 kwarg，剩"考试循环本体从未自动运行"（IBT-E07）——把考试编排接 GPU 完赛事件即可全自动（提交队列入 M5 提速案）。

## 六、自审闸三态
**挖干可施工**（9 子环节 file:line+双源卷宗交叉；T1 在飞如实标注不判定完赛数字）。堵点 1 待裁，2/3/5 有修法，4 有载体。

## 七、复核命令
```bash
# 在飞观测（只读）
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ? CommandLine -match grid | select ProcessId,CommandLine"
ls -la .runtime/logs/grid_t1_20260924.log data/strategy_intake/grid_20260924-213246/
# 预算闸与冻结面
sed -n '919,967p' scripts/backtest/factory_grid_executor.py
head -30 config/search_space_prereg.yaml
# 卷宗
sed -n '8,36p' docs/_working/decision_map_campaign_20260924/03_gpu_campaign.md
grep -rn "24990" docs/_working/ 2>/dev/null | grep -v trades_   # 无命中=勘误案实证
```
