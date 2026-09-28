---
ttl: task_bound
title: "F68 GPU 矩阵/工厂格子——prereg 冻结 v2→T0/T1→判卷→DSR（T1 dedup 完赛 all_green=false 本日新态）"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F68 · GPU 矩阵/工厂格子（总册状态 built（M2：GPU T1 在跑禁中动）/P1；本卷复核=**在飞态已翻页：T1 dedup 于 09-26 08:00 完赛，handover 判卷 all_green=false**，新跑批 230010 疑静默）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | prereg=config/search_space_prereg.yaml（**schema v2.0.0，frozen_at 2026-09-24T22:00，frozen_by/owner_signoff=裁定#413，头注实测**）；网格轴机器真源=config/position_recipe_grid_schema.yaml（schema_id=position_recipe_grid_v2，GridCompiler 消费，默认 context 名义 N_raw=362,880/全激活 11,612,160——头注实测）；条件输入包=grid_t0_conditional_v1（M2-04：matrix 1816 行×18 列/cells 20 胞 15 达标） |
| 下游消费 | data/strategy_intake/grid_<ts>/（manifest.csv+negatives.csv+net_returns.parquet 无 pyarrow 兜底 csv.gz）；T2 晋级=主效应前 20%；f06_e4_wfa_exam 考试；n_trial_ledger DSR 分母；handover_verdict.yaml=T1→T2 交接判卷件（schema t1_t2_handover/verdict-1 实测） |
| 自动化触发 | 计划任务 ZephyrAlpha_F06Grid（State=Ready；f06_grid.log 实测 09-19 23:00 与 09-26 23:00 两次 fire）；重型跑批=脱管进程手动发车（M2-04）；**prereg 冻结语义=跑中改空间作废重开**（头注+handover prereg_hash_drift 首轮建基线 da8fbbfb… 实测） |
| 真源与注册表 | executor=scripts/backtest/factory_grid_executor.py（_apply_prereg_budget fail-closed :919-967，M2-04 实锚）；卷宗=decision_map_campaign_20260924/03_gpu_campaign.md+e2e_integration/LEDGER.md；引擎口径唯一=daily_net_returns slippage_bp kwarg（:667/:797-812，M2-04 实锚） |
| 门禁与质量尺 | 预算缺册=SystemExit 禁开跑；轻档须为全档子集（validate_scan_tiers）；**T1 完赛验收四零**=manifest 3700/backtest_dead=0/eval_dead=0/degraded=0；主目标=cost_adjusted_sharpe（毛夏普仅观察，prereg objective 实测）；negative_result_promise（负结果如实入库禁删改） |
| 当前运行状态 | **翻页（本日新证）**：09-24 原发 T1（grid_20260924-213246）产物恒空+日志停 09-25 01:49→restart 09-25 11:12（log 68B 即殁）→restart2 grid_20260925-232032 完赛 09-26 02:35→并行 T0 两轮（grid_t0_base_oldeng/grid_t0_neweng）→**T1 dedup grid_20260926-024947 完赛 09-26 08:00（manifest 2.2MB+negatives 971B+handover_verdict.yaml）**；现无 factory_grid 进程在跑（本日 CIM 实测，唯 keeper PID 37548=st-ddup-20260925 会话保持进程，task_files=executor/_c4_engine/exam_cost_gate） |

## 二、子模块三级枚举（跑批三级：prereg 面→执行面→判卷面；本日实扫+M2-04 引用）

- **prereg/预算面**：search_space_prereg.yaml（v2.0.0 冻结+预算封顶+pass_criteria 三门真源注"禁双头改"）；position_recipe_grid_schema.yaml（GridCompiler，I_cost_tier 恒折叠=成本档禁作搜索轴）；_apply_prereg_budget（executor :919-967）
- **执行面**：factory_grid_executor.py（run_batch :667-812 逐格五档成本扫描；产物一次性落盘 :854-890——跑中目录恒空=设计使然，M2-04 堵点 2）；_c4_engine（向量化考尺）；数据面 fail-closed（mkt_cap 空→None 记阴性/行业锚失败→降级记 degraded，M2-04 4.4）
- **判卷/记账面**：handover_verdict.yaml 五 criteria+garbage_lines+blocking_criteria（本日全文实读）；n_trial_ledger（DSR 分母，裁定#306 N_eff 口径）；T0 条件包=scripts/audit/t0_gpu_condition_pack.py 一条命令重建（M2-04 4.6）
- **监控件两件（总册锚点）**：trading/gpu_monitor.py（NVIDIA 状态采集，CONSUMERS=resource_optimization，head 实测）；trading/gpu_consensus_scheduler.py（**LLM 双模型共识调度器 MOD-INF-033，CONSUMERS 自注"production 零导入=zombie 候选"AI-06 审计**，head 实测）

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| prereg 冻结 v2+预算闸 | built wired | yaml 头注+executor :919-967；本轮 prereg_hash 零漂移（handover 实测） |
| T1 dedup 跑批 | 完赛但**验收不过** | handover_verdict：manifest 3698≠3700（fail）/backtest_dead=2（fail）/degraded=0（pass）/negatives accounted 3700（pass）/n_eff 19≥12（pass）/**cost_gate_spot bad=28/50**（40bp 档 sharpe<survival_floor 0，bad_head 10 例实测）→**all_green=false，blocking=[manifest_points, dead_zero, cost_gate_spot]** |
| F06Grid 计划任务 | **疑静默** | 09-26 23:00:01 fire（f06_grid.log）+grid_20260926-230010/ 产物空+现无进程+无完成行=新发现嫌疑（诚实登记，M2-04"跑中目录恒空"口径下不能判死也不能判活，需 09-27 核日志增长） |
| 监控两件 | 半接线/错位消费 | gpu_monitor 有消费方；gpu_consensus_scheduler 零生产导入（与 GPU 矩阵跑批无血缘，见勘误） |

### 骨架勘误
- **总册 F68 锚点"src/zephyr/trading/gpu_consensus_scheduler.py"语义错位**：该件=LLM 双模型共识路由（MOD-INF-033，AI-06 审计 zero production imports，zombie 候选），非 GPU 矩阵计算调度；GPU 矩阵真锚=scripts/backtest/factory_grid_executor.py+GridCompiler（schema）。M2-04 4.8"GPU 交易域监控件"命名亦系同源误读，本卷勘误升级（head [CONSUMERS] 原文为证）。
- 总册"35.33s/格×4640 格"口径=原方案①全档推算与现行方案②（T1 3700 格）并存三套规模口径，R-M2-1 待裁在案（"24990"无出处勘误 M2 已立）；本卷补实测：**dedup 轮实际完赛 3698 格**。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | T1 dedup 验收三阻断（缺 2 格+backtest_dead 2+cost_gate_spot 28/50 不过） | ①核 2 死格死因（negatives 已按纪律入册）②cost_gate_spot 口径复核：spot 判"40bp sharpe≥0"对高频格天然过严还是 gate 应然——**先复核判卷口径再决定重跑或降档晋级**（涉 R-M2-3 池基悬空同案） | P0 |
| 2 | grid_20260926-230010 静默嫌疑 | 本日核 .runtime/logs/ f06_grid 相关日志增长+tasklist；死则读 dead_reason 处置 | P1 |
| 3 | GPU 规模口径三套并存（R-M2-1） | 总筹定版"T0 200/T1 3700/T2 900"（M2 建议①） | P1（Owner/总筹） |
| 4 | 跑中观测性（产物完赛才落盘+stdout 缓冲+FutureWarning 淹没=假绿温床） | progress.jsonl 每 N 格 append+python -u+warnings 收敛（M2-04 堵点 2/3 修法，T1 已完赛**现在可修**） | P1 |
| 5 | 考试循环未自动运行（IBT-E07） | GPU 完赛事件触发考后一链（与 F66 缺口 2 同案） | P1 |
| 6 | gpu_consensus_scheduler zombie 候选 | 内收判据评审（零触发零消费→退役）归总筹 | P2 |

## 五、自审闸三态
**挖干可施工（在飞禁令解除：T1 dedup 已完赛，跑中禁动约束翻页为完赛处置窗口）**；缺口 1 口径复核先行防误判，3 Owner 门位；"GPU T1 在跑禁中动"前提已失效，施工可排（keeper 会话 st-ddup-20260925 在飞件除外）。

## 六、复跑命令
```bash
head -12 config/search_space_prereg.yaml     # v2.0.0/frozen_at/#413
python -c "import yaml,io;d=yaml.safe_load(io.open('data/strategy_intake/grid_20260926-024947/handover_verdict.yaml',encoding='utf-8'));print(d['all_green'],d['blocking_criteria'])"
grep -E "measured|pass" data/strategy_intake/grid_20260926-024947/handover_verdict.yaml | head -20
cat .runtime/logs/f06_grid.log; ls data/strategy_intake/grid_20260926-230010/   # 静默嫌疑取证
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ? { \$_.CommandLine -match 'factory_grid' } | select ProcessId"   # 现=无（keeper 除外）
head -6 src/zephyr/trading/gpu_consensus_scheduler.py | grep CONSUMERS -A1   # zombie 候选原文
```
