---
ttl: task_bound
title: 深度审查作业簿——突破失败降级
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：突破失败降级（P52）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/sell_decision/core/breakout_failure_detector.py:154`（BreakoutFailureDetector.detect）
- TDM 节点: TDM-E-L4-08（stage，config/trading_decision_map.yaml:2324，双锚声明）
- 生产调用方: **零**——`BreakoutFailureDetector(` 全仓仅测试文件与自身 docstring 实例化；`sell_decision/core/__init__.py:11-13` 仅包级导出；`false_breakout_trap_detector.py:20` 仅文档性对账提及。同节点双锚之一 `pf_alloc/batched_position_builder.detect_breakout_failure`（:200）本身链路孤儿（allocation_orchestrator 之外零实例化）
- 测试文件: tests/sell_decision/test_breakout_failure_detector.py（231 行 18 测试，同批 77 passed 5.52s）

## 1 对象快照

- 范围：BreakoutFailureDetector 全文件（294 行）——纯检测器：detect() 三态判定（SUCCESS/FAILURE/FORCED_CLEAR）+confidence 计算+回调通知；不含压力位计算（上游 D-FACTOR 职责）与挑战次数持久化（调用方职责）。
- 排除项：batched_position_builder.detect_breakout_failure 数学细节归 pf_alloc 域对象（本报告只按 TDM 双锚口径对账引用，其空数据门禁实现已抽查合格）；false_breakout_trap_detector（MOD 分工在案）不在本对象。
- 测试覆盖概况：边界覆盖良好（等价压力位=失败/自定义阈值/置信度封顶/回调隔离/时钟注入）；**无"成功后计数是否重置"语义测试、无盘中价 vs 收盘价喂入纪律测试、无 direction=REPLACE 占位语义的消费方契约测试**。
- 材料包缺项声明：运行时证据包未取（生产零调用无运行痕迹）；数据画像不适用（无表消费）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿死码+保护链路断链**（checklist #8，双重）：①detector 自身生产调用方=0，header 却声明 `[MATURITY] production`；②sell_signal_collector 第⑧类 BREAKOUT_FAILURE 桶（:92）已声明但无代码从本 detector 喂入；③TDM-E-L4-08 声明"K≥3 次突破失败→强制清仓（最高优先级）"，其下游 X-S1-06 强清编排（strategy_abnormal_exit_orchestrator）grep 零 breakout/challenge 输入接线——**该触发的强制清仓在当前基线永远不会触发**。双锚另一锚 pf_alloc 链同样孤儿（checklist 案例 d9c5f4bb12 在案），即 TDM-E-L4-08 两锚全断 | breakout_failure_detector.py:7；sell_signal_collector.py:33,92；grep BreakoutFailureDetector src/ 仅 __init__/测试；grep "breakout\|challenge" strategy_abnormal_exit_orchestrator.py 零命中；config/trading_decision_map.yaml:2324-2352 | P1 | `grep -rn "BreakoutFailureDetector(" src/ --include=*.py`（零生产）；`grep -n "BREAKOUT_FAILURE" src/zephyr/sell_decision/core/*.py` 看喂入点是否存在 |
| D | **双锚口径分叉无纪律文档**：TDM 同节点两套突破失败口径并存——pf_alloc 版=收盘价连续 2 根 K 线确认+10 日前低（防日内假跌破，:210-229 实现与 TDM 一致）；本 detector=单 tick 即判（"默认单根确认"，:31），**无收盘纪律约束**。调用方若喂盘中价，影线假突破即计一次失败，K≥3 可被盘中噪音提前凑满→误强清。隐式契约"只许喂收盘价"未写入 docstring | breakout_failure_detector.py:31,230-233 vs pf_alloc/batched_position_builder.py:200-229；config/trading_decision_map.yaml:2330-2332 | P2 | 两函数并排读判定条件；构造盘中高点回落序列喂 detect 看 challenge 累计 |
| A | **challenge_count 跨成功不重置**：detect 的 challenge_count 由调用方传入，SUCCESS 分支不累计也**不提供重置信号/API**——实测序列 失败(1)→成功(计数仍 1)→失败(2)：突破成功后旧失败计数继续携带，跨行情段累计后第 3 次失败即 FORCED_CLEAR（若调用方按返回值回传即自然发生）。设计注释"历史挑战失败次数(由调用方维护)"未声明成功是否清零 | breakout_failure_detector.py:230,240（"成功不累计"仅指本次不+1）；探针实测三连判定 | P2 | `python -c` 三连 detect（失败→成功→失败）看 challenge_count 携带（本次审查已实测：1→1→2） |
| A | **direction=REPLACE 占位"持有"是语义地雷**：SellDirection.REPLACE 全枚举语义=置换卖出（collector 六桶之一），SUCCESS 分支用它占位"不卖出"（:105-106 自注）。当前零消费方未爆雷；一旦 collector 接线按 direction 字面分流，**突破成功反而触发置换卖出**（反向事故）。测试还把该占位断言固化（test:31-36） | breakout_failure_detector.py:33,105-106,242；tests/sell_decision/test_breakout_failure_detector.py:31-36 | P2 | grep SellDirection.REPLACE 在 collector 的语义定义；接线评审时检查按 direction 分流的消费代码 |
| A | confidence 口径轻症：FAILURE 置信度 0.5+0.1×(n-1) 封顶 0.9，threshold=3 时最后一次 FAILURE（第 2 次）仅 0.6<SUCCESS 0.8——若下游按 confidence 排序处理优先级，失败信号恒排在成功持有之后；数值无稳定性问题（纯线性） | breakout_failure_detector.py:146-148,263-266 | P3 | 读公式+两测试断言值（0.5/0.6） |
| B | 上游隐式契约：resistance_level 来源（L1 因子层压力位）无单位/复权口径声明；除权日压力位若未同步复权，价格跳变会被误判失败——本模块无校验只能靠调用方（无文档） | breakout_failure_detector.py:23,222-223 | P3 | 查压力位上游产出锚（D-FACTOR 域） |
| E | 回调异常隔离已做（_notify try/except+error 日志）——五问中"回调炸死检测器"已防；检测器无状态无并发面（frozen dataclass 输出） | breakout_failure_detector.py:289-294 | —（已防） | — |
| A(亮点) | 输入校验完备（空 symbol/非正价格/负计数/confidence 越界全拦截）；边界"价格==压力位=失败"有测试锁定 | breakout_failure_detector.py:122-132,220-227 | — | — |

## 3 SOTA 对照

- 突破失败即离场判据：**对等已有**——业界常规把"突破后 N 根 K 线内收回位内"定义为 failed breakout 并立即触发离场（TradingView False Breakout 脚本族口径，tradingview.com，2026；Investopedia Breakout Trading，investopedia.com，2026）。本模块"单 tick 触及即计失败"比业界"收盘确认"口径更激进，双锚中 pf_alloc 版（2 根收盘确认）才与业界对齐——两套并存属口径分叉（见轴 D 发现）。
- 连续失败强清（K≥3 三振出局）：**对等已有（立卡确认合理性）**——ForTraders False Breakouts 建议风险预算按"连续 2-3 次失败仍在日亏限额内"设计（fortraders.com，2026），K≥3 强清与该风险预算逻辑同构；但业界同时强调失败判定须用收盘价确认，单 tick 计数会虚增 K。
- 空数据无罪推定（pf_alloc 版门禁）：**对等已有**——与本项目 37 号 hysteresis"无数据=状态不变"同口径，属项目内已固化纪律（无需外部源）。

## 4 缺陷清单

1. **[P1] 孤儿死码+K≥3 强清链路双锚全断**（checklist #8）。现状：detector 零生产调用、collector 第⑧桶无人喂、X-S1-06 无 K≥3 输入、pf_alloc 链孤儿；TDM-E-L4-08 按在网口径书写且 header 冒充 production。影响：突破失败降级与强清保护在当前基线=纸面能力，"首仓失败不加仓/暂停批次"全不发生。建议修法：接线评审（collector ⑧喂入+X-S1-06 消费）前把节点补红+MATURITY 降 draft；或按 42 号编排批次正式接线。验证法：§2 轴 C 验证法。
2. **[P2] direction=REPLACE 占位语义地雷**。建议修法：SUCCESS 返回专用枚举（如 HOLD/None）或文档级铁律"direction 仅 FAILURE/FORCED_CLEAR 可执行"；补消费方契约测试。验证法：接线评审时 grep 消费方对 REPLACE 的分流。
3. **[P2] 挑战计数跨成功不重置+无收盘纪律**。建议修法：detect 增加 challenge_count 重置语义（成功清零或由调用方显式传 0 的文档铁律）；docstring 声明"仅许喂收盘确认价"。验证法：本次审查三连探针复现计数携带。
4. **[P3] 双锚口径分叉声明**：TDM 节点内显式标注两锚各自适用面（batch 切面用收盘 2 根版、单仓信号面用本 detector），防接线时混用。验证法：读 TDM 节点注释是否已分工。
5. **[P3] FAILURE 置信度与 SUCCESS 倒挂**：若 confidence 参与排序优先级需重新校准（或文档声明 confidence 不作排序键）。验证法：读公式对照 0.6<0.8。

## 5 挂起疑问

- K≥3 强清在本项目风险评估里属 X-S1-06 四触发之一（红节点编排缺口已在 TDM 注释声明）——"已知缺口"与"header production"的矛盾是登记疏漏还是有意保留，请 Owner 裁定（影响 P1 定级是否降 P2）。
- challenge_count 的持久化真源应放哪（strategy_book/信号台账）——调用方职责声明存在但全仓无人承担。

## 6 完备性自评

六轴全查（A 数学四问：线性 confidence/breakout_pct 公式逐个过、边界=等价压力位/零/负值全测；B 上游=压力位契约已查；C 下游=消费方 grep 全仓判孤儿；D 双锚对账+false_breakout_trap_detector 分工已查；E 五问：静默失败=无（回调隔离）、假阳性=单 tick 假突破、断供=不适用、重复触发=无状态幂等、时序=时钟注入）。长尾：①压力位上游计算（D-FACTOR）质量未查；②pf_alloc detect_breakout_failure 数学详查归 pf_alloc 域对象；③X-S1-06 编排接线后的端到端联测无从做（未接线）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
