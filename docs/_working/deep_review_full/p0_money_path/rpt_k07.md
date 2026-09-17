---
ttl: task_bound
title: 深度审查作业簿——回撤控制器
owner: st-deeprev-20260918
created: 2026-09-18
reviewed: 2026-09-18
---

# 深度审查报告：回撤控制器（K07）

- 状态: **已审**
- 级别: P0｜类型: 闸门
- 基线 commit: 2fa92002c3（目标文件基线后零漂移；6 commits=稳定）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/drawdown_controller.py:329`（evaluate :388-458；恢复系数 :554-570；校验 :613-624）
- 生产调用方（实测 grep）: `ex_core/risk_layer_orchestrator.py:459,803`（风控主链真实消费，BS-007→K01 同一熔断仲裁点 :826-828）；`scripts/start_paper_session.py:458`（生产装配）；`frontend/services/dashboard_feeds.py:462`（展示面）——**已接线非孤儿，且为 K06 缺位后的组合级主防线**
- 测试文件: tests/position/test_drawdown_controller.py（39 用例全绿）
- 运行结果: `python -m pytest tests/position/test_drawdown_controller.py -q` → 39 passed（Python 3.12.8）

## 1 对象快照

- **范围**：控制器本体（系统性 5 级/策略止损/黑天鹅 7 模式/回补恢复/var_breach 乘性折扣）；上游喂入（orchestrator evaluate_intraday 的 DrawdownInfo/VarCvarMetrics 构造）与下游（position_cap/allow_new_position 消费）审接线面。
- **排除项**：DrawdownTracker（组合回撤 5/10/15% 分级与 EMERGENCY 告警真源，独立模块）；黑天鹅模式库检测器（本报告 D 轴已核其接线状态）。
- **材料缺项声明**：数据画像未取；DrawdownTracker 本体未深审（长尾）。
- **测试覆盖概况**：39 用例含分级/恢复/取严/折扣；断言强（信任）；恢复触发点跳变行为被测试锁死为"正确"（见 P2-1——测试锁死与设计意图需 Owner 区分）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **恢复系数在回补触发点非单调跳变**：recovered<50% → factor=1.0（无约束）；recovered 恰过 50% → steps=int(0.5/0.25)=2 → factor=0.5（**仓位上限骤减一半**），之后 0.75→1.0 逐步回升。净效果=cap 作为 nav 的函数在谷底(1.0)→半程(0.5)→峰(1.0)呈 V 形——**净值回升穿过半程时权限反而收紧**；且 docstring 声称序列"0.25/0.50/0.75/1.0"实际首步=0.5，0.25 永不可达（文档 vs 代码漂移）。position_cap 被 TradingSession 真实消费→跳变会传导为真实减仓指令 | drawdown_controller.py:554-570（实现）vs :557-559（docstring）；:311-312（默认参数）；reduce_ratio 仅 dashboard 展示消费（grep frontend/services/dashboard_feeds.py:481） | **P2** | `evaluate(DrawdownInfo(-0.10,1.0,0.949,0.0),…)` 与 `(…,0.951,…)` 对比 position_cap：前者=risk_cap，后者=0.5×risk_cap |
| A | NaN 输入穿透校验→GREEN：validate 只查 var_95<0/cvar<var（NaN 比较恒 False 全部放行）→NaN var_95/cvar → _evaluate_risk_level 返回 GREEN → cap=1.0。与 K05 的 portfolio_value NaN 穿透构成跨模块链：VaR NaN → var_pct=NaN → 本件 GREEN → 满仓上限（复合 fail-open 链） | drawdown_controller.py:483-491,619-622；链上口 risk_layer_orchestrator.py:801-806（`is not None` 不拦 NaN） | **P2** | `evaluate(di, VarCvarMetrics(float("nan"), float("nan")))` → GREEN 不抛 |
| A | recovered_pct 无范围校验：负值→steps=int(负/0.25)=0→factor=0.0→position_cap=0→**全清指令**。当前唯一生产喂入方已钳位 [0,1]（orchestrator:868-872 max(0,min(1,..))），但控制器自身不设防，dashboard_feeds:462 与未来调用方可绕过 | drawdown_controller.py:569-570,613-624；risk_layer_orchestrator.py:868-872 | P3 | 直接 `evaluate(DrawdownInfo(-0.08,1.0,0.92,-0.1),…)` → position_cap=0 |
| A | 分级阈值数学：VaR 2/4/6%、CVaR 10% 严格大于（恰等取低级）；配置校验强制单调；ORANGE cap=0.5 非单调问题已有 P1-4 裁定在案（2026-08-16 双轮审查） | drawdown_controller.py:91-100,358-365 | 已查无 | 读码+已有裁定注释 |
| A | 取严组合数学正确：caps=[risk_cap×breach_mult, bs_cap?, 0 if kill]→min→×recovery→clamp[0,1]；BS005/BS006 cap=-1 外部决定语义正确；breach 折扣 NORMAL/BREACHED/RECOVERY=1.0/0.8/0.9 与 36 号协同表一致，未知状态 fail-closed 抛错 | drawdown_controller.py:428-437,460-474,125-137 | 已查无 | 已有测试对拍 |
| B | 上游：drawdown_info 来自 DrawdownTracker 快照（回撤真源，5.145 治本注释确认快照接口不算回撤的口径正确）；var/es 来自 FHS/VaR 链（K05）；controller 异常→degraded 降级且回撤链仍生效（Fail-Safe） | risk_layer_orchestrator.py:803-813,814-829 | 已查无 | 读码 |
| C | 下游：response→RiskLayerSnapshot→position_cap/allow_new_position 被 TradingSession 缩放目标权重消费；kill_switch_advised→_engage_kill_switch 同一仲裁点（不直接发单，边界干净）；重复触发由 K01 闩+幂等兜住 | drawdown_controller.py:33-34,275-286；risk_layer_orchestrator.py:826-828 | 已查无 | 读码+rpt_k01 E 轴 |
| D | **黑天鹅分支生产休眠**：编排器调 controller.evaluate 从不传 black_swan（默认空集）→BS-001~BS-007 处置与 BS-007→KillSwitch 建议链在生产永不激活；检测器 black_swan_pattern_library 同样零生产消费（仅 re-export）。生产实际熔断触发源=回撤 EMERGENCY/尾部 EMERGENCY/破产底线/系统性 LEVEL_3/五态 UNWINDING——头注 INVARIANT 所称 BS-007 路径实况缺席 | risk_layer_orchestrator.py:803-813（无 black_swan 实参）；grep black_swan_pattern_library 生产消费=0；risk_layer_orchestrator.py:114 | **P2** | `grep -n "black_swan" src/zephyr/ex_core/risk_layer_orchestrator.py`（仅注释与 dataclass 字段，无实参传递） |
| D | 口径漂移排查：三级响应阈值（soft5%/hard10%）与 DrawdownTracker 5/10/15% 与 K06 亏损限额（日2/周5/月10%）三套百分比并存——语义不同层（策略/组合回撤/亏损限额）但无总表文档，阈值体系全景靠读码拼凑（模式 #1 边缘） | drawdown_controller.py:26-29,304-321 | P3 | 建议产出阈值总表（转挂起疑问 1） |
| E | 假阳性过关：NaN 链（P2 第二条）；策略止损 abs(dd)>阈值用 abs——但 _validate 拒正 drawdown_pct→策略 PnL 符号翻转即整轮评估降级（fail-closed 方向，可用性损失非风险损失） | drawdown_controller.py:498-503,615-616 | P3 | strategy_pnls=[("s",+0.06)]→raise→orchestrator degraded |
| E | 静默失败：无吞异常；异常上抛由 orchestrator 转 degraded+CRITICAL 留痕——链路健康可见 | drawdown_controller.py 全文；risk_layer_orchestrator.py:814-817 | 已查无 | — |
| E | 重复触发：纯函数无状态；kill_switch_advised 重复→K01 幂等闩；时序：var_breach_state 由状态机外部推进，本件只读（正交乘性，无死角） | drawdown_controller.py:403-406 | 已查无 | — |
| A.3 | 测试：39 用例断言强；恢复序列用例锁死 0.5→0.75→1.0（未覆盖恰在触发点前后的 cap 跳变对比与 0.25 不可达） | tests/position/test_drawdown_controller.py | P3 | 查 recovery 相关用例 |

## 3 SOTA 对照（轴 F）

- **回撤分级降仓/回补恢复**：CTA/资管实务的 drawdown-based de-risking（回撤加深逐级降杠杆、恢复期渐进复仓）与本件 5 级+回补步进同构，**对等已有**；但实务中恢复期约束通常在"回撤深→恢复中"全程压制（先低后高单调），本件实现为"恢复过半才压制且起点骤降"——与业界常规单调恢复曲线不同构（强化 P2 首条立卡依据）。本战役检索预算已用于 K02/K05，本项未独立 WebSearch，如实记录。
- **VaR breach ×回撤正交乘性折扣**（36 号 §3.15）：多因子仓位约束乘性叠加属常规做法，**对等已有**。

## 4 缺陷清单（按严重级排序）

1. **[P2] 恢复系数触发点跳变 + docstring 漂移**：现状→回补 49%→51% 仓位上限 1.0×→0.5× 骤减，与"逐步恢复"意图相反；0.25 档不可达。影响→深回撤恢复半程 position_cap 骤减（TradingSession 缩放目标权重真实消费），恢复中段产生非预期减仓；爆炸半径=组合级仓位指令。建议修法→明确语义后改 monotone：恢复中 factor 从低位起步单调升到 1.0，或回补<trigger 时 factor=低位常数；同步修 docstring+测试。验证法→§2 首条对拍命令。
2. **[P2] 黑天鹅分支生产休眠**：BS-007→KillSwitch 设计链路（头注 INVARIANT 明示）在生产装配中无信号产源也无传参——设计承诺的第 7 类熔断触发源实际缺席。建议→接线 black_swan_pattern_library 进 evaluate_intraday 或文档标注"未接线"。验证法→§2 D 轴 grep。
3. **[P2] NaN 输入穿透→GREEN 满仓上限**：validate 增加 `math.isfinite(var_95/cvar_95)`（fail-closed raise）；与 K05 的 portfolio_value isfinite 修法配套，掐断复合链。验证法→§2 P2 第二条命令。
4. **[P3] 四条打包**：recovered_pct 控制器内无钳位（生产方已钳）；策略 PnL 正值触发整轮降级；三套阈值体系无总表；恢复跳变测试缺前后对比断言。

## 5 挂起疑问

1. 三套百分比体系（本件策略止损 5/10%、DrawdownTracker 5/10/15%、K06 亏损限额日2/周5/月10%）的语义分层需一张 Owner 级阈值总表（建议收口时产出，防口径漂移——模式 #1）。
2. 恢复触发点跳变是"有意保守"（恢复中期再验证）还是实现走样？测试已锁死现行为——需 Owner 裁定语义后才能动。
3. 黑天鹅模式库（black_swan_pattern_library）的检测器是否有接线排期？无排期则建议按 K06 同款"接线或退役"二选一裁处。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；数学四问逐公式过（分级/取严/折扣/恢复）；E 轴五问逐条。
- 长尾清单：① DrawdownTracker 本体（回撤峰值追踪/三级告警）未深审——建议补一对象；② black_swan_pattern_library 的检测逻辑正确性未审（孤儿状态下优先级低）；③ dashboard_feeds 展示面的 DrawdownInfo 构造正确性未审。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2 回补过50%仓位上限骤减一半(V形非单调)+BS-007黑天鹅分支生产休眠(编排器从不传): 挂起登记。
