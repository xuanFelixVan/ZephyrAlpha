---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——Tick重放器
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：Tick重放器（B06）

- 状态: **已审**
- 级别: P1｜类型: 回放内核
- 基线 commit: 2fa92002c3（对象文件基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/tick_replay.py:70`（TickReplayConfig）；TickReplayEngine :127
- 生产调用方: event_driven_engine.run_tick（主消费方）、frontend/dashboard/components/tick_replay.py（可视化回放）
- 测试文件: 头注释 [TESTS] **空**（tick_replay.py:14）；实际 tests/backtest/test_tick_replay_data_handler.py（279 行）承载部分覆盖——本报告未逐断言审（长尾）
- 备注: —

## 1 对象快照

- 范围：TickReplayEngine（加载合并/时间窗过滤/速度控制/TickSnapshot 构造/5 秒聚合）+ TickEvent/ReplayStatistics。
- 排除项：provider 侧（MiniQmt/CH adapter 归 B07）；event_driven 消费端归 B01。
- 材料包缺项声明：真实 tick 数据画像（同秒多笔/乱序率）缺——同 timestamp 排序稳定性问题的影响面只能静态判定。
- 变更热力：15 commits，末次 2026-09-15。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **同时间戳排序不确定**：`merged.sort_values("timestamp")` 默认 kind=quicksort **非稳定**——多标的同秒 tick、或聚合源同秒多行时合并顺序 run-to-run/版本间可变，违反头声明不变式"按 timestamp 严格排序"（不变式只管 timestamp 序，不管 tie 序）；回放确定性破（同输入不同回放路径） | tick_replay.py:328-329 vs :8（INVARIANTS） | P2 | 构造两 symbol 同 timestamp 的 fetch 返回跑两次 run 对比 seq 分配 |
| A | **缺列默认值静默降级**：_row_to_tick_snapshot 对 5 档/stock_status/prev_close 等缺列默认 0——停牌位 0=正常交易、盘口 0=无流动性（撮合侧 unfilled fail-closed 兜底）、prev_close 0（下游 tick 模式不做涨跌停检查故暂无爆炸，B03 §2 联动）。列缺失无 warn | tick_replay.py:396-412 | P2 | provider 返回缺 ask_price_1 列的 DF，看回放无告警照常跑 |
| A | PIT 结构核验：全量预载后逐 tick 推送，callback 仅接收当前 TickEvent，**无未来访问通道**——结构性无前视 ✓；"禁止跨 Tick 跳跃"以逐条推送实现 ✓ | tick_replay.py:236-264 | 通过 | 代码审读 |
| A | 5 秒聚合：以 buffer 首元素时间差≥5s 触发，open/high/low/last 从 last_price 取、盘口取末 tick——聚合 K 线 sequence=-1 标识，event_driven 显式跳过（event_driven_engine.py:240-241）；grep 全仓无其他消费方=**聚合能力死路径嫌疑**（做T辅助声明 vs 零消费） | tick_replay.py:432-523;grep aggregate_5s src/ | P3 | `grep -rn "aggregate_5s" src/` 看开启方 |
| B | symbol 加载失败 fail-fast（raise TickReplayError）✓；**全部 symbol 空数据时仅 warning 静默返回**（:221-223）→ run_tick 后续 nav 只有 1 点 → MetricsError 裸穿（B01 §2 轴B 同源）——断供表现=模糊异常而非明确"无数据" | tick_replay.py:221-223,312-314 | P2 | 空 provider 跑 run_tick 看异常链 |
| B | 时区/时间戳类型零校验：tz-aware 与 naive 混排会 raise（loud）；timestamp 为字符串时（CH 链路）sort 靠字典序（ISO 格式下碰巧正确，隐式契约未文档化） | tick_replay.py:329,358 | P3 | 传 str timestamp 面板跑回放 |
| C | 消费方=event_driven_engine + dashboard 回放组件：两消费方对 sequence=-1 与空数据语义的处理各自独立（dashboard 无 sanity guard 兜底，可视化静默空转） | tick_replay.py:5;frontend/dashboard/components/tick_replay.py | P3 | 空 tick 窗口打开回放面板看表现 |
| D | `_load_and_merge_ticks`/`_row_to_tick_snapshot` 与 MultiSourceDataHandler 双份承载（data_handler.py:635-665,385-430）——第三处 tick 行处理在 ch_tick_replay（列映射）。合并建议：tick 行→TickSnapshot 构造收敛单点 | tick_replay.py:296-430 vs data_handler.py:635-665 | P3 | diff 对应方法 |
| E | callback 异常 error 日志后继续（:254-257）：与 B01 同病——策略半失效静默，trades 统计不区分异常中断；`_apply_speed_control` 对乱序/同刻不 sleep 容错 ✓ 但与"严格排序"不变式张力同轴A首条 | tick_replay.py:254-257,369-371 | P2 | callback 定向抛异常看回放完成态无异常痕迹 |
| E | real_time 模式 sleep 上限 1s（:377）：午休/停牌间隔被压成 1 秒——"1x 实时"语义失真，实时演练场景（做T盘感训练）误导 | tick_replay.py:374-383 | P3 | 用跨午休 tick 流跑 real_time 计时 |
| A(亮点) | 时间窗过滤语义清晰（dt.time 切片，:341-360）；统计包（ticks/耗时/速率/时间范围）完整 | tick_replay.py:341-360,108-124 | — | — |

## 3 SOTA 对照

- 事件重放确定性：**立卡候选**——NautilusTrader 回放强调 deterministic ordering（时间戳+优先级+序号稳定排序）；本件 tie 序不稳定是确定性缺口。（来源：NautilusTrader https://nautilustrader.io/ , 2026；docs.rs/nautilus-backtest）
- 全量预载 vs 流式回放：**对等已有**——单日做T场景内存预载与 Backtrader/VectorBT 数据 feed 惯例一致，跨日场景需流式（立卡长尾）。（来源：Quant Open-Source Frameworks Compared, waylandz.com, 2026）

## 4 缺陷清单

1. **[P2] 同时间戳排序非稳定**：建议修法 `sort_values(["timestamp"], kind="stable")` 或 (timestamp, symbol) 双键。验证法：§2 轴A。
2. **[P2] 缺列默认值静默降级（停牌位/盘口）**：建议修法：关键列缺失 warn 一次+计数进 ReplayStatistics。验证法：§2 轴A。
3. **[P2] 全空数据 warning 后静默返回**：建议修法：run_tick 侧转明确错误（配合 B01 异常契约整改）。验证法：§2 轴B。
4. **[P2] callback 异常吞没**：与 B01 §4.3 同修（计数区分"异常跳过 tick 数"）。
5. **[P3] 5 秒聚合死路径、real_time 语义失真、tick 行处理三处双份承载、字符串 timestamp 隐式契约**。

## 5 挂起疑问

- 同秒多笔 tick 在真实 MiniQMT/CH 数据中的占比（决定排序稳定性发现的爆炸半径）——需数据画像实证（本环境不可达）。
- 聚合 K 线能力（aggregate_5s）是否有规划消费方（做T辅助声明 vs 现状零消费）——退役或接线待 Owner 裁定。

## 6 完备性自评

六轴全查。长尾：①test_tick_replay_data_handler.py 逐断言审未做；②真实 tick 乱序/同秒画像缺；③dashboard 回放组件消费路径未逐行审。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
