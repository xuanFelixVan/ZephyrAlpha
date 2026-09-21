---
ttl: task_bound
title: 深度审查作业簿——做T闭环与成功判定
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：做T闭环与成功判定（P65）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/intraday_t0/t0_trading_pipeline.py:190`（T0TradingPipeline.run_day:214）
- TDM 节点: TDM-P-P2-03（stage，config/trading_decision_map.yaml:2859，materiality: critical，ai_autonomy: paper）
- 生产调用方: **零**——T0TradingPipeline 全仓仅包导出（signal_ashare/__init__.py:44,72）与文档分工提及（day_trade_pnl_estimator.py:26）；header 自认 [MATURITY] testing、CONSUMERS"候选"
- 测试文件: tests/signal_ashare/intraday_t0/test_t0_trading_pipeline.py（40 passed 同批 3.04s）

## 1 对象快照

- 范围：T0TradingPipeline 全文件（401 行）——信号（MOD-SIG-068 复用）→决策（价差/轮次/手数/置信度/延迟预算硬约束）→执行（executor 注入）→当日复盘（T0DayReport）；底仓自平衡最高不变量（单轮买=卖量/EOD 强制平衡/回滚失败 escalation）。
- 排除项：t0_point_analyzer 信号算法（MOD-SIG-068）；day_trade_pnl_estimator（docstring 声明零交集）；交易成本口径（自注"归执行层"）。
- 测试覆盖概况：完成轮/回滚/EOD 强平/延迟中止覆盖（40 passed）；无"回滚后再失败"链式场景细查、无 14:50 时段语义（模块也无）。
- 材料包缺项声明：运行时证据包未取（testing 态无生产痕迹）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **节点成功判定与闭环核对语义零承载**（对账主发现）：TDM-P-P2-03 声明「盘中每 5 分钟核对当日做T买卖是否闭环；**14:50 还没闭环的不管盈亏无条件平掉敞口**（冠军规则）；**收盘判定：股数不变+总成本降=成功**；成功/失败/损耗统计喂 C3 归因」——模块：①无 5 分钟周期核对（信号驱动开闭轮，非定时对账）；②EOD 强平挂靠"bars 用尽"（:330 bars[-1]）**无 14:50 墙钟判定**——bar 流若 14:45 截止即 14:45 强平、若含盘后数据则更晚，时点语义漂移；③"总成本降=成功"判定零实现（report 只有 realized_spread_pct 价差合计，无成本调整后成败、无失败/损耗分桶）；④统计喂 C3 归因出边无人消费。D50 欠账（做T 配对核算器/底仓复原笔数偏差熔断）同样零代码 | config/trading_decision_map.yaml:2859-2895 vs t0_trading_pipeline.py:329-378,391-401 | P1 | 对照 TDM 四点逐条 grep；读 T0DayReport 字段表 |
| A | 回滚方向正确性实测核读：开 BUY 腿→平衡 SELL 失败→回滚 SELL（卖出已买股份复原底仓）✓；开 SELL→回滚 BUY ✓；回滚再失败→escalation+notes 不静默 ✓（:297-323）；spread 公式两方向口径正确（SELL 开轮=(开−闭)/开、BUY 开轮=(闭−开)/开，:260-264,275-279） | t0_trading_pipeline.py:260-279,297-323 | —（已核） | — |
| A | 价差门槛用信号价预判+成交价实结的双口径正确（:265 用 sig.price 预判、:276 用 fill2.price 实结）——滑点使预判达标/实结亏损轮如实计入 realized（负值保留）✓ | t0_trading_pipeline.py:265-280 | —（已核） | — |
| E | **回滚单无价格保护语义**：回滚/强平以 sig.price/last_price 直发 executor（:300,333），契约无 limit/保护价字段——14:57 后深市集合竞价不可撤时段若强平未成交（:360-362 escalation 已覆盖失败），但**撮合价位无下限保护**（跌停价成交也会接受），实现层（executor 生产侧未接）须补保护价纪律（联动 X-S2-02 跌停语义） | t0_trading_pipeline.py:299-301,331-334 | P2 | 接线评审检查 executor 生产实现的保护价 |
| A.4 | 状态机完备性好：开轮腿未成交→放弃该信号继续（:246-248）；延迟预算耗尽只停开轮不停平衡腿（:251-253,325-327，不变量优先级正确）——**但"平衡腿超预算"的 notes 留痕声明（docstring :33-34"违例留 notes"）无对应代码**：超预算执行平衡腿时不加任何 note | t0_trading_pipeline.py:33-34 vs 269-271,331-333 | P3 | 读平衡腿执行路径确认无 notes.append |
| B | 延迟预算只累计 executor 上报 latency_ms，无时钟预算上限（若 executor 挂起无超时契约）——executor 契约未声明延迟上界/异常语义（抛异常会中断整日 run_day 且无轮次收尾——**executor 抛异常=底仓平衡被跳过**，与自平衡不变量冲突，fail 方向错误） | t0_trading_pipeline.py:203-212,239-333（无 try/except 包 executor 调用） | P2 | mock executor 中途 raise 看 run_day 直接抛、open_round 悬空 |
| A(亮点) | 底仓自平衡作为最高不变量的设计纪律（延迟预算让位平衡腿/EOD 强平/escalation 显式）与 TDM"14:50 无条件平掉敞口"精神一致（时点语义见轴 D）；T0DayReport frozen+asdict 可序列化；配置校验完备（手数对齐/轮次/预算） | t0_trading_pipeline.py:8,28-39,87-113 | — | — |

## 3 SOTA 对照

- 底仓做T 日内闭环（持仓数量不变+降成本）：**对等已有**——A 股变相 T+0 社区标准（百度百科"日内回转交易"：通过维持持股数量不变降低成本，baike.baidu.com；知乎/雪球做T 教程，zhihu.com/xueqiu.com，2023-2026）；本模块自平衡不变量是该范式的工程化正确表达。
- 尾盘强制平敞口时点：**对等已有**——做T 社区纪律"14:50 后只平不开"（TDM 冠军规则同源，雪球教程 xueqiu.com，2024-2026）；模块用 bar 流末尾近似该时点，缺墙钟硬限（本报告轴 D 发现②）。
- 执行延迟预算（latency budget）：**对等已有**——执行算法的延迟预算与降级（放弃新开、保平仓）是执行系统常规设计（TT TWAP+ 订单类型 library.tradingtechnologies.com，2026，同 P51 引）；预算内优先级排序（平衡>开新）正确。

## 4 缺陷清单

1. **[P1] 成功判定（股数不变+总成本降）/14:50 墙钟强平/5 分钟闭环核对/归因出边四项零承载**。建议修法：EOD 判定加墙钟硬限（bar 时间戳≥14:50 即触发强平而非等 bars 尽）；T0DayReport 增加成本调整后成败判定（对接 CST-T0-001）与失败/损耗分桶；归因出边随 C3 接线批。验证法：§2 轴 D 对照。
2. **[P2] executor 异常路径破坏自平衡不变量**（抛异常=open_round 悬空直接冒泡）。建议修法：run_day 内 executor 调用包 fail-closed（异常→视同 fill 未成交走回滚/escalation 路径）；executor 契约补超时与异常语义。验证法：mock raise 探针。
3. **[P2] 回滚/强平单无价格保护**。建议修法：T0OrderIntent 增 protection_price 字段（联动 X-S2-02 跌停/笼子语义），executor 生产实现强制消费。验证法：接线评审。
4. **[P3] 平衡腿超预算 notes 缺留痕+trade_date 字符串切片格式依赖**。建议修法：补 notes；trade_date 用显式日期解析。验证法：读代码路径。

## 5 挂起疑问

- 与 MOD-SELL-018（P64）的收口裁定（蓝图自注"未收口"）——建议 Owner 终裁分工矩阵后回填两节点注释（本报告建议见 P64 §4.2）。
- executor 生产侧实现（接 QMT/下单网关）的候选件是谁——无生产接线则 materiality: critical 的节点纯属沙盘。

## 6 完备性自评

六轴全查（A 数学四问：spread 两方向公式/延迟累计/轮次上限逐个过+实测核读；B 上游=MOD-SIG-068 信号契约（confidence 0-100 口径）+bars 格式（ts 字符串）已查；C 下游=零调用方判孤儿（testing 诚实）；D=与 TDM 四点对账（主发现）+与 P64/day_trade_pnl_estimator 分工核读；E 五问：静默失败=executor 异常路径、假阳性=预判达标实结亏损如实计、断供=escalation 显式、重复触发=EOD 幂等、时序=墙钟缺位）。长尾：①MOD-SIG-068 信号质量未审；②executor 生产实现不存在故保护价无从实测；③40 测试逐断言抽查级。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
