---
ttl: task_bound
title: 深度审查作业簿——成交回报处理
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：成交回报处理（X07）

- 状态: **已审**
- 级别: P0｜类型: 模块
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/fill_handler.py:182`
- 生产调用方: **process_fill 链零生产调用方（已查无）**——唯一消费方 aggregate_root_manager（Facade）本身零生产构造（grep 实证）；query_fills_by_date 有生产消费（run_post_settlement.py:273,396 盘后对账回放）；**生产成交入账实际路径=OrderManager._on_fill（订单账）+ AsyncFillDispatcher→tracker.apply_fill（持仓账，start_paper_session.py:358-364）**
- 测试文件: tests/ex_core/test_fill_handler.py + test_fill_id_dedup_persistence.py + test_async_fill_dispatcher.py（合计 58 passed，实测）
- 备注: 幂等去重

## 1 对象快照

- **范围**：fill_handler.py 全文 499 行（process_fill 幂等/累积/状态转换、JSONL 落盘与回放、FillSummary）+ 关联装配链（async_fill_dispatcher 生产接线确认）。
- **排除项**：PositionTracker.apply_fill 内部（去重模式已对照）、AppendOnlyDedupSet 实现、run_post_settlement 对账逻辑主体。
- **测试覆盖概况**：58 passed（3.65s，3 套）。覆盖幂等/持久化去重重启存活/超量警告/坏行跳过/派发器排空。**未覆盖**：同单多 fill 并发累计竞态、CANCELLED 后迟到 fill 入账路径。
- **材料包缺项声明**：运行时证据包无；数据画像不适用；checklist 15 条已过——命中 #8 孤儿死码（process_fill 链）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 加权均价增量公式正确（old_avg×old_filled + price×qty)/new_filled，old_filled>0 分支处理首笔✓；filled_quantity 单调递增✓；Decimal 全程✓ | fill_handler.py:301-315 | 通过 | 两笔成交数值对拍（58 tests 含） |
| A | 幂等门为原子单步（claim-then-process）：持久化集 add 自带原子性、内存集 _dedup_lock 串行（AI-R3 P2 治本）✓；claim 后 crash 丢该 fill=at-most-once 权衡已注释声明"宁可少计不重复计"✓ | fill_handler.py:228-243,269-296 | 通过 | test_fill_id_dedup_persistence 13 用例 |
| A | **同单多 fill 并发累计无锁**：_dedup_lock 只串行化 fill_id 认领；filled_quantity/avg 的读-改-写（:302-315）与 _fills append、_summaries 写入不在任何公共锁内——同订单两笔不同 fill 并发到达会丢更新（OrderManager._on_fill 有 _fill_lock，本模块没有） | fill_handler.py:299-355 vs order_manager.py:493-494 | P2 | 双线程同单不同 fill_id 压测，断言 filled 累计少于预期 |
| A | CANCELLED/EXPIRED 后迟到 fill：累积照做（:302-315 先于状态转换）+ _try_transition 跳过仅 warning（:489-497）——真实成交入账但订单终态带已成交量，语义正确性依赖下游对账；与 OrderManager 迟到 fill 行为一致（双处同构） | fill_handler.py:317-324,481-499 | P3 | 过期订单注入 fill 断言 filled 增加状态不变 |
| B | 上游 Fill 契约校验：qty≤0 拒✓、order_id 匹配✓；**无 fill_price 有效性校验**（0/负/NaN 价直接进均价计算——OrderManager._on_fill 有 NaN/≤0 防御，本模块没有，双处防御不对称） | fill_handler.py:263-267 vs order_manager.py:499-509 | P2 | 注入 price=0 的 fill 断言不拒绝（均价被污染） |
| C | 消费方：process_fill→aggregate_root_manager（零生产构造）；query_fills_by_date→run_post_settlement（活）；callbacks→无生产注册。爆炸半径=接线后订单成交账 | grep 实证 | 记录 | grep 复核 |
| D | **孤儿链+上下游断裂**：process_fill 零生产调用（孤儿族第 5 例）；但其落盘写入端在 process_fill 尾部（:382）——**写入端不接线则 run_post_settlement 的读取端（query_fills_by_date）永远读空文件**，"56号文 G3 进程退出不丢当日 Fill"的保障实际不存在；生产成交入账走 dispatcher→tracker 旁路（不经本模块） | fill_handler.py:381-382 + run_post_settlement.py:273,396 + start_paper_session.py:358-364 | P1 | grep process_fill 生产调用方；对照 paper session 成交链（直连 tracker） |
| D | 双账本承载对照：订单成交账=OrderManager._on_fill（self._fills），持仓账=tracker.apply_fill（dedup 文件），本模块第三套 _fills 聚合——同 fill 三处承载（订单量/持仓/本模块聚合），生产只活两处；若 process_fill 接线且传同一 Order 对象会与 OrderManager._on_fill 双计 order.filled_quantity（双通道无跨通道去重） | order_manager.py:517 + fill_handler.py:299 + tracker 模式 | P2(接线风险) | 同 fill 走 OM._on_fill+FH.process_fill 断言 filled 双计 |
| E | 静默失败：落盘失败仅 error 日志不阻断（设计声明✓）；回调异常隔离✓；坏行跳过 warning✓——旁路失败均有痕，主流程静默点无 | fill_handler.py:402-406,370-379,438-441 | 通过 | 造只读目录断言 error 日志 |
| E | 假阳性：幂等拦截的重启重放分支按订单现状构建 summary（fill_count=0/commission=0 的合成 summary）——调用方若把该 summary 当真实成交增量会误读（契约未高亮合成语义） | fill_handler.py:277-296 | P3 | 重启重放场景查 summary.fill_count=0 |
| E | 断了没人知道：dispatcher 未 start 时 enqueue 静默积压——paper session 已修（先 start 后注册，:361-364 注释）；stop 排空失败 CRITICAL 出声✓（start_paper_session.py:389-397） | start_paper_session.py:361-364,389-397 | 通过 | 读装配代码 |
| E | 重复触发/时序：fill_id 全局唯一契约+claim 门✓；fill_timestamp 仅作摘要字段不作排序键（处理顺序=入账顺序）✓ | fill_handler.py:272,353 | 通过 | 读审 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

1. **成交回报幂等/投递语义**：对等已有。业界 trade capture 标准做法= venues at-least-once 推送 + 消费端以唯一成交号（exec ID/复合键）去重保证 each fill booked exactly once（ByteByteGo 幂等与投递语义指南，https://blog.bytebytego.com/p/a-detailed-guide-to-idempotency-delivery ，2023；CockroachDB 事件驱动系统幂等与排序，https://www.cockroachlabs.com/blog/idempotency-and-ordering-in-event-driven-systems/ ，2022-2023）。本模块 fill_id claim 门+持久化去重集与该模式一致；at-most-once 取舍（宁少计不重复计）有意识声明并有对账兜底设计，符合"exactly-once = at-least-once + 幂等消费"框架（Hacker News/业界共识综述，https://news.ycombinator.com/item?id=34986995 ）。
2. **崩溃恢复语义**：立卡候选。claim 后 crash 丢 fill 的窗口可用 WAL/两阶段（先写 JSONL 再 claim）收窄——当前靠盘后对账兜底（漏入账→drift→冻结），可接受但若接线 process_fill 建议调序（先落盘后认领，幂等由去重集保证）。

## 4 缺陷清单

**P1-1 process_fill 链零生产接线，落盘写入端断链致盘后对账读空（孤儿族第 5 例+上下游断裂）**
- 现状：process_fill 唯一消费方 aggregate_root_manager 零生产构造；JSONL 落盘挂在 process_fill 尾部——生产成交链（OM._on_fill + dispatcher→tracker）完全不经过本模块，fills_dir 永无写入；run_post_settlement 按日回放永远得空列表。
- 证据：fill_handler.py:382（落盘在 process_fill 内）+ grep（process_fill 零生产调用）+ run_post_settlement.py:273,396（读取端活）+ start_paper_session.py:358-364（生产入账走 tracker 旁路）。
- 影响："56号文 G3 进程退出不丢当日 Fill"保障纸面化；盘后对账系统侧无成交明细，对账只能靠券商侧单源——账实核对强度降级。爆炸半径=盘后对账链。
- 建议修法：把 _persist_fill 挂到生产成交链（dispatcher 消费侧或 OM._on_fill 后），或 process_fill 接线进 dispatcher 消费函数（替代裸 tracker.apply_fill，顺带获得 fill_id 持久去重）。
- 验证法：跑 paper session 空转一日查 data/fills/*.jsonl 是否生成（预期现状=不生成）。

**P2-1 同单多 fill 并发累计无锁**（fill_handler.py:299-355；接线后同单并发 fill 丢更新；修法：累计段并入 _dedup_lock 或独立订单锁；验证法：双线程压测断言累计守恒）。
**P2-2 fill_price 无有效性校验（防御不对称）**（fill_handler.py:263-267 vs order_manager.py:499-509；0/NaN 价污染均价；修法：对齐 OM 防御；验证法：注入 price=0 fill 断言当前不拒）。
**P2-3 若接线将与 OM._on_fill 双计 order.filled_quantity**（order_manager.py:517 + fill_handler.py:299；跨通道无去重；修法：接线时明确订单账唯一写者=OM，FillHandler 只做聚合查询或传副本 Order；验证法：同 fill 双通道注入断言双计）。
**P3**：①迟到 fill 入账但终态死角（:317-324，与 X02 同根因）；②_trade_date_of 依本机时区（:133-135，非 CST 部署日切错档）；③重启重放合成 summary 的 fill_count=0/commission=0 语义未高亮（:286-296）。

## 5 挂起疑问

1. run_post_settlement 盘后对账在系统侧 fill 为空时的实际行为（是否有告警/降级）——对账逻辑主体归后续对象审。
2. dispatcher 消费函数改用 FillHandler.process_fill 是否为设计意图（注释显示 40 号文 §决策①只要求异步化，未指定处理器）——接线方向需 Owner 裁定。

## 6 完备性自评

- 六轴全查：A（均价公式/幂等门/并发窗口/迟到回报四问）、B（Fill 契约防御对称性）、C（消费方=写入端断链实证）、D（三处承载对照+双计风险预登记）、E（五问：静默=通过、假阳性=合成 summary、断了没人知道=P1-1、重复触发=通过、时序=通过）、F（2 条带 URL 对照+1 立卡）。
- 长尾：①AppendOnlyDedupSet 内部实现未逐行（模式已对照）；②run_post_settlement 对账主体未审；③dispatcher 队列有界性参数未审（排空语义已核）。

## 7 收口裁定（收口方填）
- 三态逐条：
- 修复 commit:
- 复检结论:
