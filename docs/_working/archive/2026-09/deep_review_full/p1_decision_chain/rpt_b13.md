---
ttl: task_bound
title: 深度审查作业簿——验证方法学runner
owner: st-deeprev-20260918
created: 2026-09-18
reviewed_by: GLM-5.3-Flash/st-deeprev-20260918
---

# 深度审查报告：验证方法学runner（B13）

- 状态: **已审**
- 级别: P1｜类型: 管线
- 基线 commit: 2fa92002c3（基线=HEAD=工作区一致，已验）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/trading/validation/runner.py:480`（run_validation）
- 生产调用方: 台账写入口=手工/编排触发（src+scripts 仅 replay_drill.py:60 dry_run 演练命中）；台账消费方=dashboard/api_server.py:2417（/api/tdm/validation 只读）+decay_watch.py:43（尾随巡检）+auto_mount.py:784
- 测试文件: tests/trading/test_validation_runner.py（37 用例实跑全绿）
- 变更热力: **9 commits/3.5 月（8 对象中最高）**——反复返工高危区，与本轮发现的多处文档-行为漂移相印证
- 备注: PB-08 保密考卷/PB-13 土规落地件

## 1 对象快照

- 审查范围：全文件 646 行——节点清单推导、holdout 切分（滚动锁/定稿锚点双模式）、exec/exit 两类指标、两土规判定链、台账 TSV 写入、run 档案 fail-closed、衰减巡检尾随。
- 排除项：decay_watch 内部判定（消费方，另件）；ablation 对照器（X 流对照源，未放行）。
- 材料包缺项声明：生产 node_verdict 台账近况未拉（写入口无自动触发者，观察面=dashboard）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **side 词表窄匹配**：`direction = 1.0 if f.get("side")=="buy" else -1.0`（:262）与 `exits=[f for f ... if f.get("side")=="sell"]`（:334）只认小写。实测真实产物 bt-02b18b48.json trade_log side∈{buy:180, sell:216} 全小写——**当前正确**；但仓内 portfolio.Fill 词表为**大写** BUY/SELL（portfolio.py:118 且 :212 强制校验），若未来产物经 portfolio 路径写出，买入滑点符号静默翻转（direction 恒 -1 → 均值被拉向负/零 → verdict 系统性偏向 valid）、exits 归零。对比 cost_attribution._side_of 的宽词表+抛错防御，本件零防御 | runner.py:262,334; portfolio.py:109-118,212; 实测 data/backtest_artifacts/bt-02b18b48.json | **P2** | `python -c` 读任一 bt-*.json 统计 side Counter（本轮已做）；对照 portfolio.py Fill 校验 |
| A | holdout 切分数学正确：月减法+`min(day,28)` 截断 ✓；脏时间戳按保密（宁严勿漏）✓；定稿锚点解析失败显式抛错 ✓ | :186-226 | 通过 | 单测 :62-68 覆盖边界日 |
| A | 滑点方向口径：buy 正=劣于决策价 ✓；sell (p-dp) 反号后正=劣 ✓；decision_price 优先/VWAP 兜底/mixed 披露 ✓；缺基准跳过不猜 ✓ | :257-281 | 通过 | 单测 :457-478 |
| A | 两土规：样本量闸→衰减闸→容差判定的判定链与 verdict_reason 一一对应（禁手填落地）✓；exit 避损方向（≤0→noise）✓ | :291-312,345-368 | 通过 | 读码对照 verdict_mapping |
| A.3 | 测试信任判定：37 用例含边界日/脏时间戳/空窗口/写失败路径，断言强——**信任**；但 fixture 全用小写 side（:62-98）与 portfolio 词表无交集，词表回归风险无测试网 | tests/trading/test_validation_runner.py | 通过（带备注） | 实跑全绿 |
| B | 输入=bt-*.json trade_log（load_fills）：损坏 JSON 跳过+warning（:166-170）——**跳过计数不进任何披露**，多产物损坏时窗口静默收窄；建议在 report 里披露 skipped 数 | :160-183 | P3 | 构造坏 json 目录跑 load_fills |
| B | 土规阈值 20/40bp 硬编码于 :308-312；头部声明方法学真源=validation_method_registry.yaml，grep 该 yaml 无 20/40/tolerance 数值——**阈值真源实际只在代码**，"真源在 yaml"的声明失真（双承载漂移土壤，模式 #4 变体） | :296,308-312; docs/01_policies_and_standards/_registry/catalogs/validation_method_registry.yaml | P3 | `grep -nE "20\.0|40\.0|tolerance" validation_method_registry.yaml` 零命中 |
| C | 输出消费方：c1_backtest.node_verdict → dashboard（只读）+decay_watch（尾随，失败不阻断）✓ 事件驱动无 cron ✓；**14 个节点共享同一批级统计**（流水无节点归因，已知限制披露在 notes）——爆炸半径=一批 verdict 同涨同跌，节点级衰减判定跨节点完全相关（面板徽章语义需带此保留） | :535-583; docstring :31-33 | P2（已披露，保留意见） | 读 notes 组装段 |
| C | `hit_ratio` 恒 NULL（流水无未成交记录）——如实置空 ✓ 不造假 ✓ | :286,576,587 | 通过 | — |
| D | 兄弟实现：slip 口径与 cost_attribution 的 realized 轨同源（price vs decision_price）一致 ✓；exit 代理（卖出流水全量）与 ablation.py 对照器分工声明一致 ✓ | :552-558; ablation.py:5 | 通过 | — |
| D | **头部 [INVARIANTS] 与默认行为漂移**：不变量写"holdout 排除最近 12 个月"，但 ValidationConfig.finalized_at **默认="2026-09-09"**（锚点模式：D 前全锁、D 后全可考，含最近 12 个月）——Owner 裁定的有意变更已留注释，但头部不变量与行内 notes 文本（"默认 None=12 个月滚动锁"）都未同步，三方矛盾 | :8 vs :82-84 vs :566 | P3 | 读三处对照 |
| E | run_id=秒级时间戳 `VAL-%Y%m%d-%H%M%S`：同秒双批（L4+XFLOW 背靠背/测试注入）→ 台账同 run_id 两批行混写，无法以 run_id 区分批次 | :518 | P3 | 连跑两批观察 run_id |
| E | verdict_at 用 naive `datetime.now()`（:504,533）本地时区字符串入库（RULE-SCHEMA-TZ 邻域；CH 表列型若带时区则依赖服务器 tz 解释）——登记不判定 | :504,533 | P3 | 查 DDL backtest_node_verdict.py 列型 |
| E | 写台账失败→written=False+error 日志+档案保持未 finalize（诚实态）✓；dry_run 不建档案 ✓；空行拒绝写 ✓ | :597-614 | 通过 | 单测覆盖 writer 注入 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 执行质量以 decision_price（arrival price）为滑点基准 | **对等已有**：TCA 标准即 implementation shortfall/arrival-price 口径；VWAP 代理兜底+口径披露（slip_basis）符合实务 | Talos "Execution Insights Through TCA"（talos.com, ≈2023） |
| holdout 保密窗/只考一次/定稿锚点（防止验证集泄漏的时点锁定） | **对等已有（变体）**：walk-forward+纯 OOS holdout 是回测方法学标准；"定稿锚点 D"（D 前全锁）是项目自定义的一次性冻结变体，逻辑自洽，未见业界同名实践——立卡备案而非照抄 | Palomar, Portfolio Optimization §8.3 backtesting dangers（portfoliooptimizationbook.com, 2023） |
| 事件驱动衰减巡检（验证批尾随事件，不挂 cron） | **对等已有**：与监控事件驱动化共识一致，无 cron 轮询反模式 | 项目运维红线 §9.3 自洽，业界 SRE 事件驱动告警通行做法 |

## 4 缺陷清单

1. **P2｜side 词表窄匹配+词表仓内分裂**（:262,334）：当前真实产物小写故无症状；一旦上游产物经 portfolio.Fill（大写）路径写出，买入滑点符号翻转+exits 归零，verdict 系统性偏向 valid 且无任何告警。建议：仿 cost_attribution._side_of 做宽词表归一+未知方向显式抛错或计数披露。
   - 验证法：读 portfolio.py:118 与任一 bt-*.json side Counter 对照。
2. **P2（保留意见）｜节点级 verdict 是批级统计的 14/18 份复制**：面板/衰减按 node_id 读取，统计相关性 100%；披露在案但消费端（徽章/衰减判定）无相应降权。建议：verdict 行加 batch-level flag 或面板聚合展示。
3. **P3｜土规阈值单承载在代码**：与"方法学真源=validation_method_registry.yaml"声明不符；建议 yaml 落数值+代码加载，或改声明。
4. **P3｜[INVARIANTS]/notes/config-default 三方矛盾**（12 个月滚动锁 vs 锚点默认）：以注释裁定为准修头部与 notes 文本。
5. **P3｜load_fills 损坏产物静默跳过不披露**（:166-170）。
6. **P3｜run_id 秒级碰撞 + naive now 时区**（:504,518,533）。

## 5 挂起疑问

- 定稿锚点 D=2026-09-09 后，在验窗口仅 D 后流水（截至今日≈7 个交易日），triggers<30 大概率恒 pending——L4 批是否实质处于"不可出结论"态，需收口方拉台账核实（无生产自动写入口，可能整批尚未真跑过）。
- X 流批对照数据（ablation_diff）生产接线状态：runner 参数已备，调用方未发现（等消融器放行，与 docstring 声明一致）。
- verdict_at 入 CH 的列型与时区解释（DDL 未核）。

## 6 完备性自评

- 六轴全查：A（切分/方向/土规逐式+真实产物实测）✓ B（trade_log 加载/阈值真源/坏件处理）✓ C（台账消费方全列+批级复制爆炸半径）✓ D（与 cost_attribution 同源对照+不变量漂移）✓ E（五问：碰撞/时区/写失败/重复触发幂等）✓ F ✓。
- 长尾：decay_watch 判定内部（他件）；生产台账实际运行证据（无自动触发者，可能零生产运行）；ablation 对照器未放行态。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2 side 大小写分裂+批级统计共享: 挂起登记。文档漂移（9 commits 热力）: 挂起。
- 修复提交: q-0024（B11 冲击腿）。
