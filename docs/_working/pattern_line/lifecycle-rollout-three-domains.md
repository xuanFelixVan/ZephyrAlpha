---
ttl: task_bound
---

# [BLUEPRINT] | docs/_working/pattern_line/lifecycle-rollout-three-domains.md |
<!-- [MODULE] MOD-SIG-149 -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] M -->

# 生命周期协议 v2.0 三域落地施工方案（因子/策略/指标，2026-09-15 全自主班）

> 状态：**v1.0 冻结**。上接：lifecycle-protocol-v2.md（332c6f22e6）。Owner 令：全部施工、
> 全自动零人工、循环检查连续两次零失败、红蓝对抗、Gateway 落地清理。

## 一、内部反查（颠覆性发现：三域机器零件大多已在，真缺口=生命周期层+接线）

| 域 | 已有件（实测） | 真缺口 |
|----|--------------|--------|
| 因子 | bhy_fdr.py（BHY-FDR，预注册"ICIR≥0.5+BHY q=10%+HLZ t=2.8"）+ three_level_judgment（优秀/合格/淘汰，stable）+ ic_decay/decay_monitor + factor_registry 175 条含 ic/ir/lookback_period/decay_state 字段（**全 None=runner 从未建成**） | 周复盘批量 runner（factor_decay_monitor_weekly 任务块 disabled 原因自述："遍历 factor_registry→monitor_decay→decay_state 回写施工后启用"）+ 生命周期层 |
| 策略 | c1_backtest.backtest_strategy_screen 实表（is_sharpe/**deflated_sharpe** C4 强制/oos 字段，C5 批真实数据）+ E0-E9 晋升侧 + PP-001 配比 | 衰减侧：active 策略滚动判定→probation/retired 建议→复活观察 |
| 指标 | technical_indicator_registry 92 条（indicator_id/formula）+ 使用审计先例 | 消费活性台账（静态扫描）+ 零消费退役建议 |

**关键裁定（防重建）**：因子域不新造统计件——复用 three_level_judgment（域内预注册判定）
+bhy_fdr（族校正，BHY 依赖稳健版优于 148 的 BH）；生命周期层复用 MOD-SIG-149 的
LifecycleStore（通用 key→dict JSON 台账）+ 状态机骨架。单源纪律：统计判定一律调域内
既有件，禁复制实现。

## 二、各域设计（薄适配，阈值预注册）

### 因子域 factor_lifecycle_runner（src/zephyr/factor/analysis/，MOD-L02-LIFECYCLE）
- 遍历 factor_registry → 有 ic 的因子：judge_factor(ic, ir) 三级判定（优秀=certified/
  合格=probation/淘汰=failed 候选）；族校正：bhy_fdr(全族 p 值)——p 值由
  t=ic·√(n−1)/√(1−ic²)（n=lookback_period，缺 lookback 的因子封顶 probation）；
- certified 需判定=优秀 且 BHY 拒绝；淘汰连续 RETIRED_AFTER=20 个周扫 → retired
  （复用 149 生命周期语义：死后 ic 回升过复活闸 → resurrected）；
- 产出：decay_state 回写 factor_registry（safe_write，claim+CRLF 探测）+ 台账 JSON。

### 策略域 strategy_decay_certifier（src/zephyr/signal_ashare/strategy_signal/，MOD-SIG-150）
- 读 strategy_screen 每策略最新行（FINAL）：deflated_sharpe ≥0.5 且 oos_tested→certified；
  0≤DS<0.5→probation；DS<0→failed；无行=不进宇宙；
- 连续 FAILED_WINDOWS=8 个周扫 failed→retired（建议态，写台账不直接翻转策略域
  注册表状态——晋升侧 E0-E9 归属域所有，退役建议供其消费）；
- 复活：retired 后新 screen 行 DS 回升≥0.5 → resurrected；台账 JSON。

### 指标域 indicator_usage_audit（src/zephyr/governance/，MOD-GOV-INDUSAGE）
- 全仓静态扫描 92 个 IND-id/名称引用 → 台账：active（消费者≥1）/ stale（仅注册表
  引用）/ zero（零消费，退役建议）；不做统计闸（指标无预测力语义）。

### 接线
单任务 `trading_lifecycle_weekly`（weekend_calibration 档）+ capability 三点（provider
handler 内三 runner 隔离运行、per-runner try/except 合并摘要）；factor_decay_monitor_weekly
（他会话登记的 disabled 块）保持不动，报告中注明被本任务覆盖其 runner 缺口。

## 三、挖矿日志

| 轮 | 矿脉 | 判定 | 产出 |
|---|------|------|------|
| R1（前班） | 策略衰减循环 | 部分 signal | Quantpedia 发表后衰减（淡化不消失）+QuantEvolve arXiv 2510.18569 跨 regime 存活框架 |
| R2（前班） | 序贯 α 预算 | **signal** | O'Brien-Fleming 1979/Lan-DeMets 1993（复活重试收紧依据） |
| R3（本班） | 因子多重检验门槛 | **signal** | Harvey-Liu-Zhu 2016 RFS t>3.0 门槛（2100+引）——因子域 bhy_fdr 预注册 2.8 与之同源，闸定义直接沿用域内已预注册值 |
| R4（本班内部） | 三域既有件盘点 | **signal（颠覆性）** | 因子域零件全在（bhy_fdr/three_level/decay_monitor/neff/overfitting_audit），病=接线缺失非机器缺失；策略 deflated_sharpe 现成 |

## 四、不做清单
- 不翻转策略域注册表状态（退役建议台账制，状态翻转归策略域管线）；
- 不动 factor_decay_monitor_weekly 块（他会话登记）；
- 不做指标统计闸；不做因子 IC 回测管线（ic/lookback 由域内既有评估供给，缺口另批）。
