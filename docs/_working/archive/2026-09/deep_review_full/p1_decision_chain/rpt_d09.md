---
ttl: task_bound
title: 深度审查报告——Wyckoff引擎（D09）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：Wyckoff引擎（D09）

- 状态: **已审**
- 级别: P1｜类型: 算法（Wyckoff 6 阶段 FSM+评分；当前证伪置零态）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/features/wyckoff_engine.py:297(detect_wyckoff_events)`、出口 `:439(wyckoff_score)`（476 行全文通读；回退支 `overlay_features.py:537-571` 与调用点 `overlay_signals_builder.py:394-395` 实地核查）
- 生产调用方: `overlay_signals_builder.py:395`（经 `overlay_features.s2_wyckoff_score` → S2 confirm keys_or_gte 的 wyckoff 腿）；历史案例锚=checklist#8（d57b379558 结构性死亡后 2026-09 复活并走完 WYF-1/3 校准闭环）
- 测试文件: `tests/regime/test_wyckoff_engine.py` + `tests/regime/validation/test_wyckoff_walkforward.py`（WYF-3 新阈值路径+证伪路径）

## 1 对象快照

- 审查范围：6 阶段事件判据/SC 量能腿 4 口径/评分尾段/证伪披露机制/回退支旁路。排除项：WYF-3 两份校准报告原文（docstring 转述，材料包缺项）；s2_spring/capitulation 等同族维度归 D11。
- 材料包缺项声明：WYF-3 walk-forward 数据（5272 日事件计数/204 网格）未复算，取 docstring+recheck_log 自述；裁定#271/#285 原文未回读。
- 测试覆盖概况：事件判据阈值锁死（DEFAULT_WYCKOFF_PARAMS）+walkforward 证伪路径有专测；回退支（MVP）的评分边界（70 档）测试归属 overlay_features 侧（D11 域）。
- 变更热力：10 次（域内第四热），与 WYF-1/3 两轮返工吻合。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **证伪态治理为域内最佳实践（正面确认）**：显式恒 0+一次性 warning+`wyckoff_dimension_status()` 只读披露+recheck_when 四条重跑触发器+recheck_log 防重复立项+裁定双登记（#271/#285）+evidence 双报告路径——"禁静默恒零"纪律完整落地；判据与算分单一真源（wyckoff_score_from_events 生产/校准共用，防"诊断版绿生产版死"复发）设计自觉 | wyckoff_engine.py:174-252,417-436 | 已查无 | 调 wyckoff_score 观察 warning+恒 0；读 status() 快照 |
| A | F-A2 事件判据 PIT 与链依赖正确：sc_low/ar_high 用 where(events).ffill 只传播已发生事件；AR 基准量 ffill+min_periods=1（WYF-1 Bug2 修复）；SC 收盘新低（WYF-1 Bug1：c<=low 滚动低点不可达）；SC 前各阶段由 NaN 比较自然 False=链序依赖成立；+1e-8 容差防浮点 | :338-396 | 已查无 | 无 SC 数据段跑 events 全 0 |
| A | F-A3 SC 判据极端严苛是证伪的结构性根因之一：z>2 & pct<-4% & 收盘新低三合一，21.7 年仅 4 次；且恐慌日量能对任何事后基准不再异常（2015-08-24 量比 1.009/分位 0.945）——"第一波放量永久抬高基准"钝化机制 docstring 有完整机理陈述，v2 三族候选 204 网格 0 合格佐证 | :40-48,190-222 | 已查无（证伪结论与判据结构自洽） | 读 evidence 报告 §钝化段对照 |
| A | F-A4 memory_window 语义双态（None=永久粘滞 vs N=有限记忆）与 latch_dichotomy 论断（生产事件集+门槛 40 ⟹ 单次 2018 事件永久在线 36.6%）：判据空间"恒零或误爆"二极化的结构证明成立——问题在判据不在门限，与"证伪判据非改阈值"的处置自洽 | :134-136,198-200 | 已查无 | 逻辑推演复核 |
| A | F-A5 sc_volume_leg 的 vol_z mode 抛 ValueError（禁引擎内重算制造第二实现）——SSOT 纪律防御到位；三族固定基准构造式 PIT 严格（rolling 含 T/expanding min_periods=260 预热 NaN 不触发） | :265-294 | 已查无 | sc_vol_mode="vol_z" 调用抛错 |
| B | F-B1 输入契约：六序列（close/high/low/volume/pct_change/vol_z）+ffill/fillna 前处理（停牌日 v=0/pct=0 不触发放量腿）；vol_z 复用 HMM F5 单一真源（不重算）✓ | :330-336 | 已查无 | — |
| C | F-C1 **证伪声明的旁路缺口（本审查主发现）**：S2 confirm 的 wyckoff 腿在 `overlay_features.s2_wyckoff_score` 有 MVP 回退支（仅 close 时 TR 收窄+中上位置→**可达 70>60 门槛**），不经过 `_DIMENSION_STATUS` 证伪门；而调用点 `overlay_signals_builder.py:394` 只 guard `close is not None`，high/low/volume/pct_change/vol_z 任一缺（Phase 2c 关/数据降级日）即静默滑入回退支——**"S2 confirm 该析取腿等价不存在"的证伪声明在回退支上不成立**。引擎侧 docstring :187-189 已自认该支"未经样本外验证，登记为遗留风险"，但未与证伪门联动（缺 once-warning、缺 status 披露） | wyckoff_engine.py:187-189,247-248 ↔ overlay_features.py:556-571 ↔ overlay_signals_builder.py:394-395 | P1 | 构造 vol_z=None 调 s2_wyckoff_score(close)→70 分可达；Phase 2c 关闭配置跑 build_shrinkage_schedule 观察 wyckoff 维非零 |
| C | F-C2 爆炸半径：回退支激活日，S2 confirm 六维之一由未验证 MVP 评分承载——S2 是危机复苏转换（RECOVERY 注入 r11），假 confirm 的代价=复苏信号假阳（加仓信号在假底）；主路（六序列全）日证伪恒 0 生效 | overlay_features.py:556-571 | P1(随 F-C1) | 同 F-C1 |
| D | F-D1 兄弟实现对账：`wyckoff_score_from_events`（研究口）与 `wyckoff_score`（生产口）共用算分尾段——无双实现；检测判据无仓内第二份（grep wyckoff 仅本引擎+overlay_features 委托）；TRANSITION_CONFIG 的 wyckoff 门槛 60 与 params.s2_confirm_gate=60 一致且后者声明"权威真源=TRANSITION_CONFIG"——声明-代码一致 | :417-436,138-141 ↔ regime_detector.py:315-318 | 已查无 | 两值对读 |
| E | F-E1 静默失败面：证伪恒 0 有声（一次性）；**回退支无声**（F-C1 的静默滑入是残余静默点——数据降级日悄然换判据，无任何日志）；`_status_warned` 进程级一次性，长进程日志轮转后披露痕迹丢失（轻微） | :224,244-251 ↔ overlay_features.py:561-571 | P1(随 F-C1) | 关 Phase 2c 跑 S2 组装观察无告警 |
| E | F-E2 幂等/时序：纯函数级联+调用方 shift(1) 契约声明（:310）；重放确定性成立（cummax/rolling 无随机） | :310 | 已查无 | — |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | Wyckoff 阶段事件量化判据 | **对等已有（证伪处置优于业界常见做法）**——Wyckoff 量化实现多为规则型（PS/SC/AR/ST/Spring 事件阈值），业界常见"定了就用"；本项目走完预注册 walk-forward 证伪闭环（含 204 点网格与样本外池化）并显式置零，处置质量高于常见实践 | 判据谱系属 Wyckoff 方法论公共域（1930s 教程体系，无单一定源 URL 如实记）；项目证据=docs/_working/wyf3/wyf3_v2_rerun_report.md（内部路径，仓内可查） |
| 2 | 事件粘滞（latch）问题 | **对等已有**——"一次性事件永久在线"与 capitulation 维度"rolling max 粘滞→衰减加权"同族（WYF-3 报告 §结构证明自引），文献/实务对事件型信号加时间局部性是常规治法（memory_window 即此设计） | 项目内同族证据=overlay_features capitulation decayed_max（D11 交叉核对项） |
| 3 | MVP 回退支的治理 | **立卡候选**——回退支应纳入同一证伪披露（status 联动或独立 once-warning+恒 0），或明确登记为"仅诊断不进 S2"；改造点=overlay_features.s2_wyckoff_score 回退支加披露+overlay_signals_builder:394 guard 收紧到六序列 | 本报告 F-C1 论证（无外部文献依赖，如实记） |

## 4 缺陷清单（按严重级）

- **F-C1/E1（P1）证伪旁路缺口**：现状=S2 confirm wyckoff 腿在数据不齐日静默滑入 MVP 回退支（可达 70 过 60 门槛），绕过 WYF-3 证伪门且无告警 → 证据=三处锚点（wyckoff_engine:187-189 自认/overlay_features:556-571 回退支/overlay_signals_builder:394 弱 guard）→ 影响=危机复苏转换可由未验证判据假触发（RECOVERY 假阳=假底加仓信号）；爆炸半径=S2 confirm 触发面（overlay 在产链）→ 建议修法=①回退支按 _DIMENSION_STATUS 联动置零（同享 once-warning）；或②guard 收紧六序列全备才组装 wyckoff 维，缺即降级 0.0+warning（与同函数 other 维度"数据缺失降级 0.0"口径一致）；③收口时核对 Phase 2c 生产配置是否实际可触发回退支 → 验证法=vol_z=None 调 s2_wyckoff_score 复现 70 分。
- **F-A1-A5/B1/D1/E2（已查无/正面）**：证伪治理、PIT、SSOT、判据结构证明——本对象主体质量高，缺陷集中于旁路一处。
- **F-E1 附注（P3）**：_status_warned 进程级一次性告警的持久性——建议披露状态同时写 status 快照文件供审计（现仅进程内）。

## 5 挂起疑问

1. 生产 C1/回放配置中 Phase 2c（enable_phase2c + data_loader）是否常开——决定 F-C1 回退支的实际触发频度（若常开且数据全，回退支日常不激活，缺口降级为配置脆弱性）。
2. wyf3 两份报告的"纯净留存段 max_score=45 仍不达门"细节未复算——证伪结论本身有多重证据链（0/5 折为正等），本审查采信其自洽性，未做独立复算。

## 6 完备性自评

- 六轴全查：A（六阶段判据逐条+证伪机理+双窗口语义）、B（六序列契约+F5 复用）、C（调用链三锚点实地核查=主发现）、D（算分单真源+门槛双承载一致性）、E（静默面=回退支、幂等、时序契约）、F（2 条带来源+1 条内部证据如实记——Wyckoff 原始文献为公共域教程体系无单一 URL）。
- 长尾清单：①wyf3 两份报告原文未复算；②overlay_features 回退支的测试归属（D11 域）未逐件审；③spring 深度分级版（P1-E9c）与 spring 三元 flag 的关系归 D11。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 MVP 回退支绕过证伪门: 挂起登记（与 D11 同案，旁路拆除裁定）。
- 修复提交: q-0021（D03/D04 NaN 防御）。
