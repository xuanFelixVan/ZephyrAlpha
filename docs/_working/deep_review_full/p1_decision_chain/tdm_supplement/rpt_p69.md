---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——熔断分级判定
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：熔断分级判定（P69）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/risk/core/drawdown_state_machine.py:255`（DrawdownStateMachine.evaluate:344）
- TDM 节点: TDM-X-R1-01（stage，config/trading_decision_map.yaml:3136，invalidation=L4 仅 Owner 人工解除 fail-closed）
- 生产调用方: **零在网（header 自证，诚实度满分）**——唯一 import 方 drawdown_session_persistence 虽实例化本件但其对外函数全仓零调用、JsonStateStore 根目录未装配；现役回撤分级由 DrawdownTracker+Controller 闭环（:6 header 实测声明+tests/risk/test_risk_signal_consumer_wiring.py 回归锁）
- 测试文件: tests/risk/test_drawdown_state_machine.py（105 passed 同批，与 P70/P71 合跑 4.83s）

## 1 对象快照

- 范围：DrawdownStateMachine 全文件（773 行）——6 态（NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY）+升级取最严（回撤 5/10/15/25%+VaR/CVaR 交叉验证）+降级三重守卫（半阈值+持续窗+min_hold）+RECOVERY 阶梯（25/50/75% 仓帽+毕业准则）+KILL 人工复位守卫+JsonStateStore 持久化。
- 排除项：DrawdownTracker/DrawdownController（现役在网路径，归属对象）；capital_curve_manager（peak 语义，header 自划界）。
- 测试覆盖概况：105 测试覆盖转换守卫/阶梯/复位守卫/持久化损坏——覆盖密度全场最佳。
- 材料包缺项声明：运行时证据包未取（未接线）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **节点"日亏五级"判定轴与模块"回撤六级"判定轴不同轴（对账主发现）**：TDM-X-R1-01 声明「判定轴=**组合日盈亏**+组合回撤双轴：L1 警戒=日亏≥2% 禁加仓/L2 禁开仓=日亏≥4%+白名单窄门/L3 减仓=日亏≥6% 梯度减仓/L4 保命=回撤≥25%」——本模块**无日亏轴**（evaluate 只吃 drawdown_pct/VaR/CVaR，:344-363），阈值族=回撤 5/10/15/25%（WARN/DANGER/CRISIS/KILL）；L1/L2/L3 的日亏 2%/4%/6% 触发零承载；L1 禁加/L2 停新开/L3 梯度减仓的动作映射在本模块以另一套仓帽表达（0.8/0.5/0.3/0，:312-326）。且在网路径（DrawdownTracker+Controller）是否实现日亏五级未在本次范围证实（drawdown_controller 类文件 grep 无果）——**节点声明的熔断语义当前无任何已证实代码承载** | config/trading_decision_map.yaml:3136-3180 vs drawdown_state_machine.py:146-153,399-416；grep drawdown_controller 全 risk 域无类定义 | P1 | 对照 TDM L1-L4 逐级 grep 日亏阈值；追 DrawdownTracker evaluate_intraday 阈值族（长尾移交） |
| C | 孤儿（header 自证在案）：端到端零在网，持久化落盘位未装配——熔断状态重启即回 NORMAL（无持久化=无记忆，恰是本模块要解决的痛点 §3.11 痛点 1 在现实部署中仍成立） | drawdown_state_machine.py:6,629-654 | P2 | 读 header 实测声明+grep 消费链 |
| A | 状态机数学/逻辑密度全场最佳（已核）：升级取最严多源 OR；降级不可跳级+三重守卫（半阈值 0.5+持续窗 3/3/5 日+min_hold 5/10/20 日+VaR 交叉验证，:418-460）；RECOVERY 阶梯晋升须毕业四准则（:525-552，None 全卫）；KILL 唯一人工出口+复位三确认+窗口/冷却/永久锁守卫（:556-613）；回撤加深分级保护（>15% 退级/>10% 退级/>5% 冻结，:473-501）；同日幂等/日期倒退拒绝 | drawdown_state_machine.py:344-773 | —（已核） | — |
| A | RECOVERY 空档带（dd∈(10%,15%] 且 step=0）无退级路径仅冻结兜底（:490-501 自注"空档"）——RECOVERY step0 遇 dd=12% 将无限冻结循环（仓帽 25% 保守向可辩护，但状态语义上永不回 CRISIS/KILL 除 >15%）——设计自认，记录在案 | drawdown_state_machine.py:490-501 | P3 | RECOVERY step0+dd=0.12 连续多日看永不转换 |
| A | graduation 准则小样本弱边界：graduation_min_trades=3 但 expectancy 窗=10——仅 3 笔时按 3 笔均值≥0.3R 即可毕业（样本量 vs 窗口语义未对齐）；streak 用 pnl 序列而 expectancy/compliance 用 r_multiple/rule_followed（字段三元组契约靠 duck-typing 无 schema 校验） | drawdown_state_machine.py:525-552 | P3 | 3 笔全赢的序列跑 graduation_criteria_met |
| B | 复位守卫"20 日窗"用自然日序数（:590-591 toordinal 差）vs 全模块交易日计时约定（:40-41）——双日历口径并存于同一守卫链 | drawdown_state_machine.py:40-41,590-591 | P3 | 读窗口计算确认自然日 |
| E | 持久化损坏 fail-closed（StateCorruptError 不兜底，:656-691）；KILL 自动路径不存在（:376-377）；升级持久化每转换即写（:393-394）——对抗轴五问全部有防 | drawdown_state_machine.py:376-377,656-691 | —（已防） | — |
| A(亮点) | header CONSUMERS 的"无现役消费方"自证+回归锁测试指针——是本批 26 对象中孤儿声明最诚实的范本（对照 P51-P68 多处 header production 不实） | drawdown_state_machine.py:6 | — | — |

## 3 SOTA 对照

- 日亏限额熔断（daily loss limit hard-stop）：**对等已有**——prop 行业标准 2-5% 日亏硬限+当日锁死禁再入场（ClearEdge《Automated prop firm drawdown protection》clearedge.trading，2026：daily loss 2-5%+flatten+block re-entry；TradingPlace prop rules，tradingplace.us，2026；The5ers Drawdown Rules 2026，the5ers.com——daily/max/trailing 三类）——**TDM 的日亏 2%/4%/6% 分级恰与业界 2-5% 带一致，是正确的判定轴**；模块的回撤 5/10/15/25% 是另一正统轴（max drawdown 分级）。两轴业界并行使用（daily limit 管日内、max DD 管账户级），TDM"双轴"声明合理，**代码只实现了后一轴**。
- 降级迟滞/恢复阶梯：**对等已有**——hysteresis-style 机制在业界以"次日解锁+分阶段恢复规模"形态存在（Tradeify 三阶段恢复计划 tradeify.co，2026；scaling 里程碑制 apextraderfunding.com，2026）；本模块三重守卫+毕业准则比业界典型实现更严格（设计先进性认可）。
- "最严状态优先"（the most severe state wins）：**对等已有**——模块 docstring 引 nexusfi（:27），与风控引擎通用实践一致（无需另证）。

## 4 缺陷清单

1. **[P1] 日亏轴五级（L1 2%/L2 4%/L3 6%）零承载，节点判定轴与模块判定轴不同轴**；P67（禁加门消费 L2+）/P70（窄门消费 L2/L3）消费的 L-taxonomy 只存在于 TDM 文本与 P70 的转述枚举——熔断分级在码上无单一真源。建议修法：裁定唯一判定轴（建议：日亏轴=盘中 DrawdownController 承载、回撤轴=本模块承载，节点拆注双承载分工），并把 P70 CircuitLevel 的"真源指针"改指真实承载件。验证法：§2 轴 D grep+追 DrawdownTracker。
2. **[P2] 孤儿+持久化落盘位未装配（重启失忆）**。建议修法：装配 JsonStateStore 根目录+接线事件通道（header 已给回归锁），或维持"设计件"定位并把节点声明改挂现役路径。验证法：grep 消费链。
3. **[P3] RECOVERY 空档带/毕业小样本/复位自然日窗**。建议修法：空档带补 CRISIS 回退边或文档固化；graduation 窗口对齐（min_trades≥graduation_window 或按比例）；复位守卫改交易日口径。验证法：各自探针。

## 5 挂起疑问

- 现役路径（DrawdownTracker+Controller evaluate_intraday）的阈值族是否覆盖日亏 2/4/6%——本报告未能定位 controller 类文件（grep 无 drawdown_controller 定义），若现役路径也无日亏五级，则 TDM-X-R1-01 整节点为纯声明节点，需 Owner 裁定补施工或改写节点（长尾移交收口方核实）。
- M-36"禁加期=L1 及以上"（P67 报告主发现的裁定依据）中的 L1 在代码侧无处产生——R1-01 判定轴裁定应与 P67/P70 修复同批收敛。

## 6 完备性自评

六轴全查（A 数学四问：阈值递增校验/阶梯门槛/毕业准则逐个过+105 测试背书、边界=同日幂等/日期倒退/样本不足已测；B 上游=drawdown_pct/VaR/recovered_pct/strategy_pnls 契约已查；C 下游=零在网自证+position_cap/recovery_factor 消费面声明；D=与 TDM 双轴对账（主发现）+与 DrawdownTracker/whitelist/pyramiding 三向分工核读；E 五问：静默失败=无（fail-closed 全面）、假阳性=毕业小样本、断供=持久化损坏不兜底（已防）+落盘位未装配（已立）、重复触发=同日幂等、时序=交易日约定+自然日窗混用（已记）。长尾：①DrawdownTracker/Controller/evaluate_intraday 现役链详查（本报告仅定位失败）；②capital_curve_manager peak 语义未审；③JsonStateStore 契约未审。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
