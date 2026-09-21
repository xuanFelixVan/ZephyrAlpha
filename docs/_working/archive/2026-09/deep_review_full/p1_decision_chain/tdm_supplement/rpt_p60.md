---
ttl: task_bound
title: 深度审查作业簿——持仓对账与台账快照
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：持仓对账与台账快照（P60）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/position_state_machine.py:285`（PositionStateMachine）
- TDM 节点: TDM-P-P1-01（stage，config/trading_decision_map.yaml:2590，doc_ref=93_qmt_file_bridge_playbook）
- 生产调用方: **零**——`PositionStateMachine(` 全仓仅自身 docstring（:289）；header 声明的 MOD-POS-003/MOD-POS-009/MOD-POS-016/D-SELL-DECISION 四消费方 grep 零实际调用。节点声明的对账语义疑似真承载=`position/position_reconciler.py`（事件驱动三方对账）与 `ex_core/position_reconciler.py`
- 测试文件: tests/position/test_position_state_machine.py（54 passed 同批，与 P61/P62 合跑）

## 1 对象快照

- 范围：PositionStateMachine 全文件（572 行）——7 态生命周期 FSM（NONE→BUILDING→ACTIVE→OBSERVING→REDUCING→EXITING→CLOSED）+观察期（15min 确认窗）+冷却期（默认 5 日）+灰度 4 阶段（5/20/50/100%，每阶段 5 日）+E-POS-05 事件。
- 排除项：position_reconciler（对账真承载候选，本报告只按节点对账语义引用）；shared/lifecycle 基类。
- 测试覆盖概况：合法/非法转换+灰度时长+冷却期覆盖；**无观察期超时未决（confirm_by 过期）场景、无 activate() 跳过灰度纪律场景**（两处为本报告发现）。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **TDM-P-P1-01 module_ref 语义错位（对账主发现）**：节点声明「读 QMT 桥持仓文件（Stock.csv）→与 strategy_book 逐笔核对股数/成本→不平账标红；输出富台账（代码/股数/成本/归属策略/开仓日/状态机态）」——本模块只承载其中"状态机态"一个字段的生命周期语义；**对账三步（桥文件读取/逐笔核对/标红）与富台账五字段（股数/成本/策略归属/开仓日）全部零代码**。真承载候选=position/position_reconciler.py（"execution report+book record+counterparty 三方对账"，事件触发合规）——但那是成交回报驱动，非节点声明的"盘前读 Stock.csv 快照对账"，两口径也不完全重合 | config/trading_decision_map.yaml:2590-2630 vs position_state_machine.py 全文（grep Stock.csv/股数/成本/开仓日 零命中）；position/position_reconciler.py:20-48 | P1 | 对照 TDM 三步逐条 grep position 域；读 position_reconciler 入口语义比对 |
| C | **孤儿死码**（checklist #8）：FSM 零生产调用方；持仓状态机是"仓位裁决中心的状态根"（docstring :23），根无人挂——header [MATURITY] production 不实 | position_state_machine.py:7,23；grep 证据见上 | P2 | `grep -rn "PositionStateMachine(" src/ --include=*.py` |
| A.4 | **观察期 15min 确认窗只设不查**：enter_observing 计算 observing_confirm_by（:454）后全文件无任何超时检查/强制决断逻辑——"收盘前 15min 确认执行或解除"（POS-02 设计）无状态机承载，OBSERVING 可无限期滞留（期间 can_buy=False 若被查询，但无人在 fsm 侧逼决断）；FSM 转移完备性缺口：无 OBSERVING 超时→自动决断边 | position_state_machine.py:454（设），全文无 confirm_by 消费 | P2 | enter_observing 后 now+16min 调任何方法看无超时反应；grep observing_confirm_by 消费方=0 |
| A | **activate() 旁路灰度纪律**：advance_graduation 强制每阶段≥5 日，但 activate() 直接把 graduction 置 STAGE_4 并转 ACTIVE（:440-442）——调用方一步绕过全部灰度验证期；无 config 开关区分"测试快进"与"生产快进" | position_state_machine.py:436-442 vs 391-412 | P3 | start_building 后立即 activate() 成功（无 GraduationRegressionError） |
| A | can_buy() 与冷却期语义割裂：CLOSED 冷却期内 can_buy()=True（只挡 OBSERVING），重仓拦截全靠 start_building 的 CooldownPeriodError——若消费方在 CLOSED 期直接用 can_buy() 判可买即漏拦（隐式契约：CLOSED 必须用 can_rebuild） | position_state_machine.py:357-361,363-370 | P3 | CLOSED 状态调 can_buy() 看 True |
| A | 时间口径双混用：cooldown 默认"5 自然日"（docstring 自认简易模式，:497-502）、graduation stage_days 用 timedelta(days=5)（自然日）——与"交易日"设计语义（:181-184 字段名 cooldown_trading_days）不符，周末/节假日使冷却与灰度验证期实际缩短；须调用方显式传 cooldown_until 纠正 | position_state_machine.py:181-184,405-407,501-502 | P3 | 周五 close 不传 cooldown_until，看周一即可 rebuild（自然日 5 日含周末缩短为 3 交易日） |
| E | 事件监听隔离合格（:566-572）；reset() 事件 from=NONE=to 丢真实前态（:514-521，审计轨迹小失真） | position_state_machine.py:509-523,566-572 | P3 | REDUCING 态 reset 后查事件 from_state |
| A(亮点) | 转换矩阵完备性好（15 边覆盖 7 态主要路径）；错误码改号留痕（#ARCH-ERRCODE-001 裁定注释）；灰度单调性有显式异常类；frozen 配置+时钟注入可测性好 | position_state_machine.py:143-162,233-282 | — | — |

## 3 SOTA 对照

- 持仓生命周期状态机（建仓/持仓/观察/减仓/清仓/冷却）：**对等已有**——交易系统仓位生命周期 FSM 是常规工程实践，观察期确认+冷却期防反手与 vn.py/主流零售交易框架的仓位管理同构（vn.py 官方文档 vnpy.com，2026——本项目 X-S2-04 已引同一范式）；无争议项。
- 灰度发布式建仓（5/20/50/100% 阶梯放量）：**对等已有**——资金管理文献的分批建仓（scaling in）标准做法（Investopedia Scaling In/Out 词条，investopedia.com，2026）；阶段天数用自然日还是交易日业界无统一（本项目混用为本报告 P3 发现）。
- 持仓对账（券商文件 vs 本地台账）：**对等已有（承载错位）**——对账三步语义由 position_reconciler 的三方对账（execution report 事件驱动）承载更符合宪法 §9.3"事件触发"红线；TDM 的"盘前 Stock.csv 快照对账"是另一通道（93 号 playbook），两通道应在节点内显式分工。

## 4 缺陷清单

1. **[P1] 节点对账三步+富台账五字段零承载、module_ref 错位、真承载通道双轨未分工**。建议修法：TDM-P-P1-01 拆注两个承载面（盘前快照对账=93 号 playbook/position_reconciler 候选；状态机态=本模块），或补齐 Stock.csv 盘前对账件；本模块在接线前降 draft。验证法：§2 轴 D grep。
2. **[P2] FSM 孤儿**（状态根无人挂）。建议修法：随仓位裁决中心（position_adjudication_center）接线；接线前 MATURITY 降 draft。验证法：grep。
3. **[P2] OBSERVING 15min 确认窗只设不查**。建议修法：增加 check_observing_timeout(now) 业务方法（超时→自动 confirm=True 转 REDUCING 或告警），并挂转移完备性测试。验证法：超时探针。
4. **[P3] activate() 旁路灰度/can_buy 冷却盲区/自然日 vs 交易日混用/reset 事件前态丢失**。建议修法：activate 加 config.allow_skip_graduation 开关默认 False；can_buy 收紧含 CLOSED+冷却；注释显式声明日历口径；reset 事件带真实前态。验证法：各自探针。

## 5 挂起疑问

- 对账双通道（盘前 Stock.csv 快照 vs 成交回报事件驱动 reconciler）是否都要、谁是主——涉及 P1-01 节点拆分，请 Owner 裁定。
- 灰度阶段天数语义（交易日 vs 自然日）与冷却期默认值需 Owner 拍板后写回 config 注释。

## 6 完备性自评

六轴全查（A 数学四问：FSM 拓扑/灰度权重映射/时长校验逐个过、边界=非法转换/超时/快进已测；B 上游=now/cooldown_until 注入契约已查；C 下游=零调用方判孤儿；D=与 TDM 节点对账+与 position_reconciler 双承载分工（主发现）；E 五问：静默失败=OBSERVING 滞留、假阳性=can_buy 冷却盲区、断供=不适用、重复触发=转换幂等性由基类保证、时序=时钟注入全量可测）。长尾：①position_reconciler 两件详查归其对账域对象；②shared/lifecycle 基类未审；③position_adjudication_center 编排（消费本 FSM 的目标位）未审。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
