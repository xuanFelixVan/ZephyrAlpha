---
ttl: task_bound
completes_when: Owner 对 SOP 草案点单（批准/修订）后转 archived
session: st-live-readiness-20260922
date: '2026-09-22'
---

# 小资金实盘 SOP 草案 — 小资金实盘准入准备班 · 件2

> 班次：st-live-readiness-20260922（通宵令 §3 分包2）
> **性质声明**：本件是**草案**。全部数值参数均为 proposed 档，生效前置=件4 门禁 G1–G12 全绿+Owner 对参数逐项 confirmed。凡标 ⏸ 的参数=等 Owner 点单。
> 事实口径：对照既有系统行为写（kill_switch/crisis_gate/日循环均有代码与实证背书，见件1 证据列）；未实现的能力**如实标注"未接电"**，不写未来时。

---

## §1 适用范围

| 维度 | 草案口径 | 依据 |
|------|----------|------|
| 资金规模 | "小资金"具体金额 ⏸（建议以风险预算反推：单笔风险额=总资金×单笔止损%，能承受连续 10 笔止损+一次日亏熔断而不伤筋动骨） | Owner 三差异②"风险预算倒推仓位"（owner-vision-system-mapping.md:26-28） |
| 档位 | pilot 档（B-007 五档阶梯 shadow→paper→**pilot**→daily_review→auto 的第三档；pilot 前必须走完 paper 档） | system_charter.md:106 |
| 品种（首选） | **300ETF 波段+底仓 T**（Owner 周期定策略包：震荡期只做确定性高的 300ETF，不碰个股板块） | mapping:65-67；卡1 口径 mapping:49 |
| 品种（扩容） | 个股/进攻板块包：仅当 regime 趋势期解锁，且依赖 **≥2 个已毕业策略包**（毕业=S-OWNER 考试链产出，禁手填） | mapping:50 卡2 口径；owner_gate_list.md:33-34 |
| 品种（备选） | 币圈 7×24 捷径：**在案未立项**（crypto 全层有意空壳 v1，等 A 股链验证后移植 by-design） | skeleton-coverage-audit.md:259；archive crypto_probe 三件 |
| 频率 | 日线波段为主+小时/分钟做 T 为辅（Owner 原话：日线做波段，小时/分钟做 T）；开盘竞价不做（A' 桥接完工前竞价窗口非消费面） | mapping:65 附录A |
| 换汇/衍生品 | 期货对冲腿=纸面演练档（real_channel_locked=true 恒真，解锁须≥3 次演练+Owner 批） | paper_hedge.yaml:42 |

## §2 盘前流程（挂当日循环，已实证）

1. **16:45 盘后带自动圈**（已批已施工，2026-09-21 实证 16 段 15 ok+1 skipped）：日循环产出 regime/六段状态/预算切片。
2. **盘前五层门快照**（daily_gate_snapshot，只读采集面）：L1 regime PIT 读 → L2 板块门（**v1 恒 absent**：依赖板块门的包当日禁用）→ L3 六段×四开关查表 → L4 预算日切片 → L5 kill_switch 读态+drawdown/price_cage/t1_sellable。
3. **仓位预算生成**：总仓位=min(六段预算带，60% 硬顶) ⏸（参数待 confirmed，见件1-P1）。预算带：capitulation 0-10% / accumulation 20-30% / ignition 30-50% / expansion 50-70% / euphoria≤30% 只卖不买 / distribution 0%；过渡带系数 0.5-0.7。
4. **no_trade 权**：三源合成，任何一源成立=当日不开新仓（编排器"有权说今天不交易"——这是 SOP 的第一纪律，不是异常）。
5. **人工确认点**：pilot 档每笔开仓 Owner 确认 ⏸（或 Owner 授权的确认口径）；kill_switch 态非 NORMAL=当日流程终止。

## §3 盘中流程

1. **执行链顺序**：信号→pre_execution_checker（闸门1 kill_switch_gate fail-closed）→execution_engine（HALT 拒单）→order_manager。任一环节拒单=终止该笔，不重试绕行。
2. **五级熔断在场**（自动，无需人工）：位置超限→只许平仓；日亏 -3% AUM→撤全部挂单+禁新单（当日不再恢复）；连续拒单≥5 或价偏>5%→断 Broker；延迟>1s 或成交率<50%→全系统暂停；API 超时>10s 或心跳丢≥3→杀当前 Session。触发后动作见件3 E4。
3. **做 T 纪律**（底仓额度内）：时段准入+量能闸+连败熔断+底仓容量 ADV×3 天四件（存档参考：archive/2026-09/c_class_scattered/2026-09-07-tdm-pre-backtest-review-checklist.md:170）。⚠ 做T v2 已裁砍（裁定#331，复活窄考 RED），**本节仅在 Owner 就底仓 T 另立新卡（新因子族+预注册假设）后生效**，此前做 T=禁。
4. **禁改清单**：盘中禁改任何阈值/flag/注册表；盘中异常走件3 手册，不现场发明动作。

## §4 仓位与止损纪律（参数档 ⏸）

| 参数 | 草案建议档 | 状态 |
|------|------------|------|
| 总仓位上限 | min(预算带，60% 硬顶) | proposed（blueprint:187），等 Owner confirmed |
| 单笔风险 | 总资金的 0.5%–1%（小资金取下限 0.5% 起步） | proposed，等 Owner |
| 单笔止损 | 按 ATR 或固定百分比（建议 −5%±，与风险预算联动反推股数） | proposed，等 Owner |
| 日亏熔断 | −3% AUM（已有代码定义）撤单+禁新单 | 已定义（trading_kill_switch DAILY_LOSS），小资金建议是否收紧至 −2% ⏸ |
| 建仓方式 | TD 阶<0 金字塔建仓、波段上沿分批减仓（Owner 规则化口径） | 规则在册但 **pyramiding_rules 未接电**（件1-P2 红）——接电前本行=人工执行口径 |
| 减仓 | 波段上沿分批减；euphoria 段只卖不买 | 预算带已含 |
| 隔夜 | pilot 档默认不留隔夜负债仓位；ETF 波段可持隔夜（无杠杆） | proposed |
| 对冲 | 纸面腿（IM，β=1.0 假设值×0.5 比例）仅演练；真实期货通道禁碰 | paper_hedge.yaml 在册 |

**止损哲学对齐 Owner 原话**："全仓不是错，无规则的全仓才是错"（mapping:26-28）——本节全部存在意义=把规则先写下来再谈仓位。

## §5 人工干预点（Owner 门位清单）

| # | 干预点 | 触发条件 | 依据 |
|---|--------|----------|------|
| H1 | kill_switch 复位 | 任一级熔断触发后 | 系统级 reset 需 Owner（kill_switch.py:300-318）；qmt_e2e_runbook.md:30 |
| H2 | crisis θ 校准 | 月度演练回看误报率 | crisis_gate.yaml:19 O1 注 |
| H3 | 仓位参数改动 | 60% 硬顶/预算带/过渡带 | blueprint:187 |
| H4 | 换档 | paper→pilot→daily_review→auto 任何升/降档 | B-007，AI 不可自动升档 |
| H5 | real_channel_locked 解锁 | 纸面≥3 次演练后；**解锁同日 paper_auto_confirm 必须置 false** | paper_hedge.yaml:42 与 paper_auto_confirm 注 |
| H6 | 模拟→实盘切换令牌 | LiveSimulationSwitcher 一次性令牌签发 | live_simulation_switcher.py:8,26-30 |
| H7 | 注册表净删/flag 出厂翻转/production 流转 | 高危域四类操作 | risk_tier_registry.yaml:42-47 |
| H8 | 密钥轮换 | 定期+曝光事件后 | tc_10 步骤5 |

## §6 盘后流程

1. **验证环**：close_verify→settle 段序（已实证 0→6 常态化）；判定/结算分离铁律（forecast 判定台账口径）。
2. **对账**：当日成交/撤单/资金流水对账（QMT 通道对账在 sim 档先跑熟，pilot 档沿用同一对账件）。
3. **留痕**：作战室 postmarket 段上链；异常事件按件3 手册留痕 crisis_gate_log / 告警注册表。
4. **月度**：分层 attribution 回看（L1-L5 逐层归因，"整条链赚钱≠每层有用，不赚钱的层砍掉"，mapping:28）；crisis θ 误报率回看（H2）。

## §7 升级/降级路径

```
shadow → paper → pilot(本 SOP 适用档) → daily_review → auto
```
- 升档唯一通道：Owner 审批（B-007）；AI 提请材料=件4 门禁 G1–G12 快照+paper 档 N 日绿记录+分层 attribution 月报。
- 降档可由证据自动触发建议（连续 error/回撤越限），执行仍须 Owner 确认。
- pilot→daily_review 的额外前置：≥2 个毕业包+月度 attribution 至少两个月正贡献（proposed ⏸）。

## §8 本 SOP 的未接电依赖（如实声明）

| 依赖 | 现状 | 补齐路径 |
|------|------|----------|
| 执行链实弹 | 代码就绪、实盘链路零实跑（件1-R2） | 件4-G5 sim 演练 |
| 金字塔建仓接电 | 仅导出无消费（件1-P2） | 另立施工卡 |
| 交易运行时心跳 | 缺位（件1-M4） | 件4-S3/G9 |
| 交易级告警 | 注册表无专条（件1-A1） | 件4-S2/G8 |
| 熔断态持久化 | 内存态（件1-R3） | 件4-S3/G9 |
| 竞价窗口消费 | A' 桥接施工单在案未施工 | 按 09-17 施工单另行立项 |
