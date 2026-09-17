---
ttl: task_bound
title: 深度审查作业簿——执行前置闸门组+价格笼子
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：执行前置闸门组+价格笼子（X05）

- 状态: **已审**
- 级别: P0｜类型: 闸门
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/pre_execution_checker.py:147 + price_cage.py:153`
- 生产调用方: PreExecutionChecker=TradingSession.attach_pre_execution_gate（trading_session.py:472）+ scripts/start_paper_session.py:565 实接线；check_price_cage=miniqmt_broker.py:729（真盘口）/qmt_file_bridge_broker.py:476（**无盘口，见 P1-1**）/pricing_policy/signal_ashare.tradability_preflight
- 测试文件: tests/ex_core/test_pre_execution_checker.py + test_price_cage.py（合计 45 passed，实测）
- 备注: Fail-Closed 预检

## 1 对象快照

- **范围**：pre_execution_checker.py 全文 278 行（四级闸门编排：熔断→时段→快照→否决）+ price_cage.py 全文 264 行（A 股价格笼子：基准价回退链/板块差异化/夹边）。
- **排除项**：RiskDataPipeline/MOD-RK-25 快照装配内部、RiskVetoEngine（MOD-RK-24）各规则实现（仅审规则清单覆盖面）、board_lot 板块分类。
- **测试覆盖概况**：45 passed（8.57s）。pre_exec 覆盖四级 Fail-Closed/短路/探针异常；cage 覆盖各板块/回退链/夹边 tick 取整。**未覆盖**：调用方无盘口场景的笼子失效（恰为 P1-1）、探针未接线静默放行。
- **材料包缺项声明**：运行时证据包无；数据画像不适用；checklist 15 条已过——**命中 #13 外部契约（交易所笼子规则官方对照，已完成轴 F 检索）**。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 四级闸门顺序固定且短路正确：熔断激活/探针异常均 return 不建快照✓；blocks 空=allowed✓；report frozen✓ | pre_execution_checker.py:180-253 | 通过 | test 套件复跑 |
| A | 时段窗口数学：09:30-11:30/13:00-15:00 闭区间含端点；naive 按 Shanghai、aware 换算✓；交易日真源失败降级周历（周六日恒闭）✓ | pre_execution_checker.py:63-123 | 通过 | 边界时刻单测复跑 |
| A | 笼子边界数学：买入上限=max(base×1.02, base+0.1)（主板/创业板有兜底）、科创板严格 1.02、北交所 1.05；卖出镜像取 min/孰低；夹边 buy 向下/sell 向上取 tick 保证不出笼✓ | price_cage.py:96-101,199-264 | 通过 | 边界值对拍（45 tests 含） |
| A | **文件桥消费端笼子恒失效**：qmt_file_bridge_broker.py:476 调 check_price_cage 不传 ask1/bid1/last/prev_close 任一基准价 → _resolve_base_price 恒 None → 恒 UNKNOWN → clamped_price=原价原样通过（注释自称"降级无盘口"）。实盘 QMT 路径价格笼子=0 防护 | qmt_file_bridge_broker.py:470-479 + price_cage.py:123-150,186-195 | **P1** | 无盘口参数直调 check_price_cage 断言 UNKNOWN；读 file bridge 提交链 |
| B | 快照 builder 仅捕 RiskDataPipelineError，其他异常上抛——已验证调用方 trading_session.py:910 全捕获 Fail-Closed，链路安全；但其他未来调用方需自行兜底（契约未在签名标注） | pre_execution_checker.py:230-241 vs trading_session.py:910-912 | P3 | 造 builder 抛 RuntimeError 验证上抛 |
| B | veto_engine.evaluate 异常不捕获直接上抛（:244）——同上靠调用方 Fail-Closed | pre_execution_checker.py:244 | P3 | 造 veto 抛异常 |
| B | **熔断探针未接线仅 DEBUG 静默放行**：kill_switch_probe=None 时记 DEBUG 继续（"无真源不臆造"设计）；TradingSession._detect_kill_switch_probe 对缺属性的 validator 返 None → 闸门无声消失，无 WARNING/装配期断言 | pre_execution_checker.py:181-182 + trading_session.py:457-470 | P2 | 构造无 kill_switch_active 属性 validator 走 attach，断言仅 DEBUG |
| C | 消费方语义：miniqmt 传真盘口（:725-733）CLAMPED 改单+UNKNOWN warning 放行✓；file bridge 恒 UNKNOWN（见 P1-1）；tradability_preflight 信号侧预检✓ | miniqmt_broker.py:729-754 | 记录 | 读各消费方 |
| D | 旁系：veto 引擎含停牌（P20 suspended_held_symbols）/T+1 sellable/持仓超量规则，但**无涨跌停不可成交规则**（grep 规则清单 P15-P50 无涨跌停）——涨停买单/跌停卖单放行到柜台排队，占用资金预占与撤单率预算 | risk_veto_engine.py:25-30,129-218 | P2 | 造涨停价 BUY request 断言无 veto |
| E | 静默失败：UNKNOWN 笼子跳过仅 warning（miniqmt）/无日志（file bridge 直接原价）；两消费方 UNKNOWN 语义不一致（一 warning 一无日志） | miniqmt_broker.py:749-753 vs qmt_file_bridge_broker.py:476-479 | P2(并入 P1-1) | 对比两消费方日志 |
| E | 假阳性：熔断探针异常 Fail-Closed✓；时段探针异常 Fail-Closed✓；快照失败拒单✓——该拦的拦得住（除探针未接线场景 P2） | pre_execution_checker.py:184-227 | 通过 | test 复跑 |
| E | 断了没人知道：探针未接线 DEBUG（P2）；时段降级周历仅 except 静默（节假日库坏→仅周末拦截，法定节假日误放行无告警） | pre_execution_checker.py:97-99 | P2 | mock is_trading_day 抛异常，节假日断言误放行 |
| E | 重复触发/时序：check 纯函数✓；evaluated_at 可注入✓；request_id 透传✓ | pre_execution_checker.py:175-177 | 通过 | 读审 |
| F | 见 §3（官方规则对照完成，checklist#13 清偿） | — | — | — |

## 3 SOTA 对照

1. **价格笼子官方规则对照（checklist#13 清偿）**：对等已有。±2% 有效申报价格范围+超范围废单为沪深交易所现行规则（北京大学光华管理学院研究简报第 132 期：创业板 ±2%，https://www.gsm.pku.edu.cn/thought_leadership/info/9319/2487.htm ；证券时报"主板也迎来交易笼子"，https://www.stcn.com/article/detail/797860.html ）；"2%+0.1 元（十个 tick）孰高/孰低弹性空间"为深交所规则修订增设、解决低价股报单难（东方财富解读，https://emcreative.eastmoney.com/app_fortune/article/index.html?artcode=1287255810 ；解放日报主板交易制度十大变化，https://www.jfdaily.com/wx/detail.do?id=600995 ）——与本仓 `max(2%, 0.1元)` 实现一致✓；基准价=对手方最优价（买入=即时揭示最低卖价）+回退链（最新成交价→前收盘）与代码一致✓；科创板严格 ±2% 一致✓。**两处待核**：①创业板是否适用 0.1 元兜底（检索源未明确区分，代码按有兜底处理）；②北交所 ±5% 无官方来源对照（部分受阻，建议收口方核北交所交易规则原文）。
2. **交易所超范围=废单 vs 本仓夹边**：驳回（作为缺陷）。交易所对超范围申报作无效处理，本仓 pre-submit 夹边是防废单的合理工程化（有 INFO 留痕），不构成与官方规则冲突。

## 4 缺陷清单

**P1-1 文件桥（实盘 QMT 路径）价格笼子恒 UNKNOWN 形同虚设**
- 现状：qmt_file_bridge_broker 提交限价单时调 check_price_cage 不传任何基准价 → 基准价解析恒 None → UNKNOWN → 原价原样出笼，无日志无拦截。
- 证据：qmt_file_bridge_broker.py:476（调用无盘口参数）+ price_cage.py:186-195（UNKNOWN 原价返回）。
- 影响：实盘全部限价单无笼子防护，超范围申报被交易所废单（程序化报单废单率上升+撤单率预算消耗，BM-EXE-04 ≤15% 红线承压）；同时无盘口校验的乌龙价可直达柜台。爆炸半径=实盘全路径。
- 建议修法：file bridge 接入行情快照至少传 last_price/prev_close（回退链尾），或 UNKNOWN 时按配置 Fail-Close 拒单；与 miniqmt 消费方语义对齐（warning 留痕）。
- 验证法：单测——不传基准价直调 check_price_cage 断言 UNKNOWN；集成——file bridge 提交涨停价×1.1 限价单观察原价过笼。

**P2-1 熔断探针未接线仅 DEBUG 静默放行**（pre_execution_checker.py:181-182 + trading_session.py:457-470；mis-config 下 kill-switch 闸无声消失；修法：attach_pre_execution_gate 装配期 probe=None 时 WARNING 或断言；验证法：无属性 validator 走 attach 查日志级别）。
**P2-2 veto 引擎无涨跌停不可成交规则**（risk_veto_engine.py:25-30；涨停买单/跌停卖单放行排队，资金预占+撤单率预算无效消耗；修法：新增涨跌停 veto 规则（snapshot 需含涨跌停价）；验证法：涨停价 BUY 断言无 veto）。
**P2-3 交易日历降级静默误放行**（pre_execution_checker.py:97-99；节假日库失效时法定节假日放行仅靠周历，无告警；修法：降级路径加 WARNING 计数；验证法：mock 抛异常复现）。
**P3**：①check 仅捕 RiskDataPipelineError，其他异常靠调用方兜底且契约未标注（:230-241，调用方已验证安全）；②veto evaluate 异常同上（:244）；③UNKNOWN 消费方语义不一致（miniqmt warning vs file bridge 静默）；④15:00 端点含边界（收盘时刻仍放行，微小）。

## 5 挂起疑问

1. 创业板 0.1 元兜底的官方适用性（检索源未区分主板/创业板修订适用范围）——需核深交所交易规则原文。
2. 北交所 ±5% 笼子参数无官方对照（本次检索部分受阻）——checklist#13 残留项。
3. veto 引擎规则全集是否在别的快照字段承载涨跌停信息（本次仅 grep 规则清单，未逐行审 MOD-RK-24 实现）。

## 6 完备性自评

- 六轴全查：A（四级闸门数学/时段窗口/笼子边界/tick 取整全过）、B（builder/veto 异常契约+探针接线）、C（四方消费方语义逐一核）、D（veto 规则覆盖面旁系对照）、E（五问：静默=P1-1、假阳性=通过、断了没人知道=P2-1/P2-3、重复触发=纯函数通过、时序=通过）、F（官方规则对照完成+2 项待核如实记）。
- 长尾：①MOD-RK-24 veto 各规则实现未逐行（仅清单级）；②RiskDataPipeline 快照装配内部未审；③tradability_preflight 信号侧预检未深审。

## 7 收口裁定（收口方填）
- 三态逐条：
- 修复 commit:
- 复检结论:
