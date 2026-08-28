---
title: 双轮审查差异比对与裁定书（Kimi K3 一审 × Qwen3.8-Max 盲审二审）
date: 2026-08-16
ttl: permanent
adjudicator: "第五统筹 coord-0815-gov3"
---

# 双轮审查差异比对与裁定书

> 一审：`2026-08-16-kimi-review-report-round1.md`（上下文红利型）
> 二审：`2026-08-16-qwen-review-report-round2.md`（盲审独立推算型，未读一审报告）
> 比对方法：交集=高置信 / 独有=盲区暴露 / 阴性互证=排除项

## 一、裁定总则：Qwen P0-1 改变了整个优先级

**核心事态**：风控三件套（35 回撤/36 VaR-ES/37 流动性）+Kill Switch+对账器——**模块全写完、4.5 万测试全绿、生产链路零接线**。统筹独立复核确认：`RiskOrchestrator` src 零匹配；`VaRCalculator()/TailRiskMonitor()/DrawdownController()` 实例化仅存在于自身定义文件；trading/ 生产链只有 Protocol 契约无实现注入；`execute_kill_switch_liquidation` 唯一调用点在 tests。

**边界澄清（避免误读为"全无防护"）**：trading_session 生产链已接入的是**合规层**（ASM-001 2026-08-16 merge：C-004 四道合规闸+ReportGate+日申报硬计数器+KillSwitchLite 策略级当日熔断）。缺的是**组合级风控层**（回撤 EMERGENCY→KillSwitch、VaR/ES breach、流动性危机 LEVEL_3、PositionReconciler 对账）。

**定性**：这不是算法 bug，是集成缺口。Qwen 比喻准确——"消防栓装了没接水管"。tracker #78 装配批范围本来就只含合规模块，风控接线属后续批——**审查的价值在于把"后续批"提前曝光为 P0**。

## 二、双模型交集（独立命中，置信度封顶）

| 发现 | 一审编号 | 二审编号 | 裁定 |
|---|---|---|---|
| 幽灵持仓检测枚举缺口（策略侧无记录=None 不报） | F3 [P1] | P1 群"幽灵持仓枚举漏无记录" | **成立**。但受 P0-1 影响重排——该函数经 DefaultRiskValidator→Orchestrator 链整体未接线，修复随接线批一并施工（枚举补第三种 ghost_type="unknown_to_strategy"），不单列 |

## 三、Qwen 独有发现（一审盲区暴露，全部采纳）

| # | 发现 | 裁定 |
|---|---|---|
| P0-1 | 风控全链路零接线 | **成立（统筹 grep 复核）**。立专项批，见 §五 |
| P0-2 | crash 恢复无重放+apply_fill 明示不去重+Saga 补偿新 fill_id 绕过去重+超时分支吞成交 | **成立**。docstring 原文"幂等性由调用方保证"+重启账本归零→空仓错觉下重复建仓。随接线批施工（启动重建以券商为准+fill_id 持久化去重集+Saga 超时强制查询终态） |
| P0-3 | Kill Switch 纯内存状态（重启即解除熔断）+清算无幂等键/无状态锁（重复触发=重复全量卖单） | **成立**。极端行情=crash 高发=熔断最易失效时刻，逻辑链严丝合缝。随接线批施工（状态落盘 Fail-Closed+LIQUIDATING 状态锁+以券商实时持仓为准） |
| 深挖③ | POT 小样本：60 日窗口+50% 负日常态→exceedances 仅 3 个 < 代码自身 ≥5 门槛，GPD 拟合是噪声发生器；盈利侧死代码 | **成立**（用代码自身门槛反证样本不足，证据形式漂亮）。算法修复批处理：60 日窗口与 POT 天然不兼容——裁定=POT 拟合窗口扩至 252 日或降级为"样本不足时跳过 POT 修正仅历史 ES"（后者已与 fit_pot 返回 None 的设计兼容，需验证降级路径告警） |
| 深挖④ | FHS 代码不存在（src 零匹配），memo 36 §3.10 以可执行语气引用 fhs_engine.enable() | **成立**。文档-代码漂移：memo 修正为"远期候选"明确语气，或登记 CAND。算法修复批处理 |
| P1 | 5 级仓位上限非单调（YELLOW 0.5→ORANGE 0.7 倒挂） | **成立即修**（数值表错误，算法修复批） |
| P1 | 撤单计数未接线（申报额度口径缺口） | 与 ASM 日申报计数器联动，算法修复批 |
| P1 | 多 Protocol 无仲裁（两触发源无互斥） | 随 P0-3 单一仲裁点一并解 |
| D1-D9 | 文档-代码漂移清单 | 算法修复批逐条对账 |

## 四、一审独有发现（二审未覆盖，仍然成立）

| # | 发现 | 裁定 |
|---|---|---|
| F1 [P1] | ES 线性插值致尾部样本数抖动 | 成立。与 Qwen"离散收益下 VaR 可报 0"互为补充（同为小样本口径族）。修法：`method='lower'`+memo 补插值口径裁定 |
| F2 [P1] | VaRCalculator 静默过滤 NaN（数据缺口期间风险低估且无信号） | 成立。修法：isfinite 过滤+nan_dropped 计数入 VaRResult+超阈值 raise |
| F4 [P2] | Inf 穿透 | 并入 F2 修法（np.isfinite 一并滤） |
| F5 [P2] | RegimeMeta 死代码两则 | 成立（数学证明不可达）。清理即可 |

## 五、阴性互证区（双模型一致排除，不再复查）

年化 √252 方向 ✓ / water-filling N=2 兜底 ✓ / shrinkage 无双重折扣 ✓ / Kelly 公式与截 0 ✓ / 追高等值边界 ✓ / 对账无 unknown 静默兜底桶 ✓

## 六、修复优先级裁定（替代任务书原排序）

> **铁律：算法修复在接线前不产生实际保护（Qwen 原则，采纳）。**

| 批次 | 内容 | 时点 |
|---|---|---|
| **P0 风控接线批（新立，最高优先）** | ①trading_session 盘前/盘中注入 DrawdownController.evaluate+VaR/TailRisk，position_cap 喂仓位引擎 ②DrawdownTracker EMERGENCY→trigger_kill_switch+清算监听链 ③KillSwitch 状态持久化 Fail-Closed+LIQUIDATING 锁+幂等键+单一仲裁点 ④启动恢复：券商持仓全量重建 PositionTracker（重建完成前禁下单）+fill_id 持久化去重+Saga 超时终态查询 ⑤PositionReconciler 盘中定时接入 | **首批策略进 SHADOW 前必须完成**（与 #95 QUANT-002 同时点——Crash-only 外部化与本批天然同域，建议合并施工）；当前 tick 数据链验证（08-17）不受影响 |
| 算法修复批（次优） | F1 ES 插值/F2 NaN+Inf/F3 幽灵第三枚举/Qwen P1 群（仓位上限非单调/撤单计数/POT 降级/D1-D9 漂移）/F5 死代码 | 接线批 merge 后 |
| CAND 登记 | FHS 实现（若 memo 裁定保留则为 CAND；POT 窗口扩展备选） | 算法修复批内裁定 |

**与在途 6 路 TD2 的关系**：零冲突——TD2 改 tests/ 域，接线批改 src/ex_core+risk 运行时域。可立即并发派单。

## 七、流程沉淀（双轮审查方法论确认）

本轮实证了"一审（上下文）+二审（盲审）"的互补价值：一审的 F1/F2 是细粒度数值口径发现，二审的 P0-1 是"退一步问谁调用"的结构性发现——**后者只有零上下文视角才能看到**（一审知道 35/36/37 已 merge 的"完工叙事"，反而被叙事遮蔽）。后续重大审查沿用此双轮制，盲审纪律（禁读一审报告）写入 SOP 候选。
