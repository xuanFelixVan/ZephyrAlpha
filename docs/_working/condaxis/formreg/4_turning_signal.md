---
ttl: task_bound
title: 环节[4] 拐点信号——CUSUM/BOCPD；ARL 虚报率预算；PIT 滞后钉死
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 1. 逐项台账（✅ 均为 2026-10-13 本车道 Read/grep 实查）

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| 单边 CUSUM 实现（可扩展复用） | src/zephyr/factor/analysis/correlation_drift_monitor.py 实读：:152 cusum_upper_alarm()（S⁺ₜ=max(0,S⁺ₜ₋₁+(ρₜ−ρ₀)−k)，S⁺>h 告警）、:60-61 CUSUM_K_SIGMA=0.5/H_SIGMA=4.0、:8 INVARIANTS"只检上行漂移(S⁺单边)；σ=0降级不告警" | ✅ 实查在产 | 策略对漂移监控（PSI 辅助 :199） | **两态拐点需双边**（S⁻ 下行扩展）+检测对象从相关系数换特征/价格——扩展不改本尊 | ③+④ |
| CUSUM→校准联动先例 | src/zephyr/governance/lifecycle_governance/drift_observatory_orchestrator.py 实读：:20/:29/:48 L2 cusum_alarm→L4 calibration flush 事件链 | ✅ 实查在产 | ML 漂移观测 | 拐点信号→状态机重估/告警的事件触发接线同款（宪法 §9.3 禁 cron 纪律） | ②下游 |
| BOCPD | grep "bocpd" 全仓唯一命中=src/zephyr/position/core/strategy_book.py:158,166（SentimentStageSignal 接口注释占位，**无实现**）实读 | ⬜ 空白待建 | 信号灰度 p(r_t=0)；strategy_book 链路2 契约已预留位 | robust 观测模型（Student-t，ICML 2023）；hazard 先验敏感须 A 股重标 | ③ |
| PIT 尾窗机制 | scripts/backtest/auto_mount.py:83 实读 PIT_TAIL_LAG=1（"决策日只能用 ≤T-1 信息"） | ✅ 实查在产 | 判定窗派生（:302/:318/:334） | 两态拐点信号的滞后面数照此钉死+卡面披露（研究册 §11 问题 6 三源各自滞后） | ③+⑥ |
| closed_book 纪律 | src/zephyr/backtest/core/closed_book_gate.py:31 实读（CLOSED_BOOK_CUTOFF 与 t0_material_line 同一点互证；cutoff 由 holdout_cutoff(finalized_at=2026-09-09, months=12) 派生，**本件不落第二个切点常数**） | ✅ 实查在产 | 全回测读库口 | 拐点验证窗同守此切点；两态新件禁落第三切点 | ③ |
| B4 事件吻合验证（确认延迟先例） | src/zephyr/regime/validation/phase2/historical_events.yaml 实读：8 事件（4 CRISIS+4 RECOVERY，:27-:103 逐条）、±5 交易日命中窗、≥6/8 PASS；b4_transition_accuracy.py（ls 实据） | ✅ 实查在产 | phase2 B4 | 两态拐点打靶的直接靶场；A股牛熊锚点年表扩充进此库或另立姊妹库（P2 定） | ②+⑥ |
| ARL 虚报率预算 | 无仓内对应件（FDR_Q=0.10/T_STAR_HLZ=2.8 为检验校正非检测预算，auto_mount 实读属另一物） | ⬜ 空白待建 | CUSUM/BOCPD 阈值标定 | 数值待 P2 按历史拐点密度反推呈批（研究册 §13-5，禁自拟） | ③ |
| 拐点三元组（位置/方向/严重度） | 无仓内落地件（strategy_book 占位不含三元组） | ⬜ 空白待建 | 供给卡/状态切换触发器 | Wood 系"position+severity"同构（研究册 §6/§10） | ②+⑤ |
| 离线复核（ruptures PELT 等） | 全仓 grep "ruptures" src+scripts 零命中（2026-10-13） | ⬜ 空白待建 | P3 离线全量标注复核 | 依赖 [2] P-S 规则层先立真值段才有对照基准 | ③ |

# 2. 与既有资产的边界（不推倒重来清单）

1. **直接复用零改动**：PIT_TAIL_LAG 机制、closed_book_gate 切点派生、B4+historical_events 靶场、drift_observatory 事件触发接线模式。
2. **扩展复用（本尊不动）**：cusum_upper_alarm 加双边/多特征姊妹函数——correlation_drift_monitor 是策略对漂移监控域的在产件，两态拐点**另建新模块引用其参数学**（k=0.5σ/h=4σ 起点值+PSI 辅助），禁在其内加市场域逻辑。
3. **参数换面**：k/h 从 MathAndMarkets 相关漂移经验值起点，按 ARL 预算反推重标（P2）；BOCPD hazard 常数起点 1/250（Adams-MacKay 示例）重标。
4. **新建**：双边 CUSUM 件、BOCPD 件（或 Kats 摘模块改造）、三元组输出契约、ARL 预算标定脚本。

# 3. 施工要点（代码实读中的坑）

1. **σ=0 静默降级坑**：correlation_drift_monitor.py:8 明示"σ=0 降级不告警"——低波动横盘期残差 σ→0 时 CUSUM 哑火是**设计行为**；两态拐点在横盘起动场景恰是最需要的，扩展件必须处理零方差分支（显式 warmup 标记而非静默）。
2. **CUSUM 只检上行**：S⁺ 单边是 INVARIANTS 冻结的——下行须 S⁻ 对称件，禁在本件加参数翻转语义（改 INVARIANTS=动在产件契约）。
3. **确认延迟是预算结果**：研究册 §4.1 最快检测理论——P2 文书必须"先钉 ARL 预算、后读出延迟"，禁把延迟当自由参数调；B4 的 ±5 交易日窗是仓内先例值，两态层的窗=ARL 标定输出，两处数值不必相同但须各自留证。
4. **closed_book 两态语义撞词**：closed_book_gate.py:34 的"两态语义"=研究态 vs 闭卷考试态（本车道实读），与两态形态线**同词不同物**——文书与代码注释中"两态"必须带定语（形态两态/门禁两态），防后来者混淆。
5. **历史事件库的数据范围**：historical_events.yaml 头注明示 CH K 线 2010-01-01 起、2008 雷曼事件 in_data_range:false 仅作标注——两态锚点年表扩充时 2005-2007 段（998→6124）超出数据范围，只能作文献锚不能作打靶事件（研究册 §8.1 年表三段中仅 2013/2019 段全程在数据范围）。
6. **事件触发禁 cron**：拐点→重估/告警的接线走 drift_observatory 同款事件链（task_completed 唤醒），宪法 §9.3 红线。

# 4. 自审闸三态裁定

| 项 | 裁定 | 理由 |
|---|---|---|
| 双边 CUSUM 扩展件 | **施工** | Owner"反转信号在哪"直问；仓内参数学+实现先例，边际成本=一个纯函数件+标定脚本 |
| ARL 预算标定脚本 | **施工** | 无预算则阈值无冻结依据（判据数值零自拟纪律的前提件） |
| BOCPD 件 | **施工**（P2 后排期内） | p(r_t=0) 天然灰度+strategy_book 契约已留位；成本实算（robust 观测模型移植）后定与 CUSUM 的先后 |
| 拐点三元组输出契约 | **施工** | 信号=event 的供给卡接口；纯契约件成本 |
| ruptures 离线复核集成 | **挂起排期** | 终局有位（P3 离线标注），但对照基准=P-S 真值段；解锁条件=[2] 规则层段边界冻结 |
| Shiryaev 贝叶斯准则族 | **方案封矿** | 终局由 BOCPD（其在线近似）+CUSUM（minimax）双准则覆盖；三准则并存的增量无文献支撑，留案底 |
