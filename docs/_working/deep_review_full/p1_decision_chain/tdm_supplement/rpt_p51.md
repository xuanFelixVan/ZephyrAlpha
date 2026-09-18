---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——条件触发队列
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：条件触发队列（P51）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/local_order_queue.py:80`
- TDM 节点: TDM-E-L4-07（aggregation，config/trading_decision_map.yaml:2296）
- 生产调用方: `src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py:112`（QmtFileBridgeAssembly 按 enable_algo_queue 创建）→ `src/zephyr/ex_core/qmt_trading_session.py:116`（enable_algo_queue 默认 False）。**但全仓 grep 无任何 `enqueue(/enqueue_batch(/get_queue(` 生产调用**——队列被创建、从不被喂单
- 测试文件: tests/ex_core/test_local_order_queue.py（154 行 6 测试，与另两对象同批 77 passed 5.52s）

## 1 对象快照

- 范围：LocalOrderQueue 全文件（271 行）——订单切片本地缓冲：enqueue/enqueue_batch 入队、1 秒调度循环按 scheduled_time 发送、失败 10 秒重试、get_stats/health_check 监控面。
- 排除项：trigger_registry.py（MOD-TRIG-001）单独在案——它才是本 TDM 节点声明语义（触发器统一注册/优先级仲裁）的真承载，见发现 1；qmt_file_bridge_broker/integration 只按消费口径引用。
- 测试覆盖概况：6 测试覆盖入队/批量/发送/一次重试/健康检查两态；**无 FAILED 状态路径测试、无无限重试上限测试、无重启丢单语义测试**；test_send_retry 只断言第一次失败（time.sleep(2.0) 真实等待，慢 CI 有脆性）。
- 材料包缺项声明：运行时证据包未取（生产零调用=无运行痕迹可查）；变更热力未做 --follow 统计（draft 模块低 churn）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **TDM-E-L4-07 module_ref 锚错位**：节点名"条件触发队列"、decision_question"触发器统一注册、tick 驱动按优先级触发（风控>卖出>买入）"，但其声明语义的真承载= `src/zephyr/trading/trigger_registry.py`（41_buy_flow.md §3.9/v1.7.0 明载落码点），而 module_ref 指向的 local_order_queue.py 是订单间隔缓冲（间隔发送/失败重试），**零触发器注册/优先级/风控>卖出>买入语义**。且 TriggerRegistry 自身 grep 零生产消费方（register/evaluate_all 全仓无调用）→ 节点声明的"一处注册全图复用"实为未接线，节点未标红 | config/trading_decision_map.yaml:2296-2320 vs src/zephyr/trading/trigger_registry.py:126,168,213 vs local_order_queue.py:17-29；docs/.../41_buy_flow.md:727（v1.7.0 落码记录） | P1 | `grep -rn "TriggerRegistry\|evaluate_all" src/ --include=*.py`（仅自身+测试）；对比 TDM 节点 algo_note 与两模块 docstring |
| C | **LocalOrderQueue 生产孤儿（结构性空转）**：唯一创建链 qmt_trading_session（默认关）→assembly 创建后全仓无喂单方，队列永远空转；模块 header [MATURITY] draft 诚实但 TDM-E-L4-07/边缘叙事把它当在网基础设施（checklist #8） | local_order_queue.py:118,136；qmt_trading_session.py:55,70,116；grep `.enqueue(` src/ 仅 ticket_queue/async_fill_dispatcher/DLQ 等无关队列 | P2 | `grep -rn "get_queue(\|enqueue_batch" src/ --include=*.py`，逐条核对与 LOQ 无关 |
| E | **FAILED 状态从不赋值→监控盲区**：全文件无 `status = OrderQueueItemStatus.FAILED` 赋值点，get_stats().failed 恒 0，health_check 的 degraded 分支（:194）不可达、ok 恒为线程存活布尔——持续发送失败对前端监控面完全不可见，只剩 warning 日志（checklist #6 同族"断了没人知道"） | local_order_queue.py:56,179,191-197,252-262 | P2 | `grep -n "OrderQueueItemStatus.FAILED" src/zephyr/ex_core/local_order_queue.py`（仅定义与计数行）；注入 submit_order 恒抛的 mock 跑 start() 看 health_check 恒 ok |
| E | **重试无上限无死信**：发送失败仅 scheduled_time=now+10s 无限重试，无 max_attempts/退避增长/死信队列/告警升级；永久性拒单（资金不足/价格越界类硬拒）会以 6 次/分钟频率永久空转刷 warning | local_order_queue.py:94-95,252-262 | P2 | mock submit_order 恒抛 Exception 跑 30 秒，看 attempts 无界增长且无终态 |
| B | **队列无持久化，进程重启丢全部 pending**：`_items` 纯内存 list；docstring"不丢单"仅在进程生命周期内成立；TDM 节点注释声明的"状态变量=扳机注册表；落盘先于生效；重启后全量重注册"（trading_decision_map.yaml:2317）在本模块零实现 | local_order_queue.py:109,166-171；config/trading_decision_map.yaml:2317 | P2 | enqueue 后 kill 进程重启，get_stats().total 归零且无任何补偿日志 |
| B | 隐式契约未文档化：队列按时间节流但**不核对券商侧在途同向挂单数**——"QMT 只看到 1~2 笔"的上限约束成立前提是"该 broker 全部订单必经此队列"；任何旁路直发单（qmt_file_bridge_broker 单笔通道）都会击穿 2~3 笔上限 | local_order_queue.py:21-23；src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:32 | P3 | 读 qmt_file_bridge_broker 下发路径确认直发通道存在 |
| E | submit_order 异常不分类：暂时性失败（网络）与永久性失败（硬拒单）同样处理，与发现"重试无上限"叠加成毒单永动 | local_order_queue.py:243-262 | P3 | 同上毒单剧本 |
| A(亮点) | 时钟用 time.monotonic()（immune 墙钟跳变）；_next_schedule_time 空队列 min(interval,0.05) 首笔快发与 docstring 一致；enqueue_batch 空列表 no-op 安全 | local_order_queue.py:143,212-222 | — | — |
| A | 良性数据竞态：_send 在锁外写 item.status/attempts，get_stats/get_items 锁内遍历读——CPython GIL 下无撕裂风险但违反锁纪律（P3） | local_order_queue.py:232-238,240-245 vs 173-180 | P3 | 压测并发 get_stats+_send 观察不一致快照 |

## 3 SOTA 对照

- 客户端节流队列：**对等已有**——业界标准做法是客户端 token bucket/滑动窗口节流+本地时间戳记录，集中所有下单经单一代 throttling 通道（TradeStation API Rate Limiting 文档，tradestation.com，2026；smudge.ai ratelimit algorithms，2024-2026）。本模块属该家族的最简定间隔实现；缺口在失败分类与在途对账，不在节流范式本身。
- TWAP 切片间隔 30s-5min 常规区间：**对等已有**（Time-Weighted Execution: Designing Robust TWAP & Hybrid Strategies，medium.com/@cmsfinancial2004，2026；TT TWAP+ 订单类型，library.tradingtechnologies.com，2026）——默认 180s 落在业界常规带内。
- 重试纪律：**立卡候选**——业界对交易 API 重试普遍要求 429/backoff 分类+最大重试数+死信（Hyperliquid Rate Limits Best Practices，onekey.so，2026）；本模块无上限重试是缺口（对齐轴 E 发现）。

## 4 缺陷清单

1. **[P1] TDM-E-L4-07 module_ref 锚错位+真承载未接线**。现状：节点声明"触发器统一注册/tick 驱动/优先级风控>卖出>买入/队列积压降级批量"，module_ref 却指向订单间隔缓冲，真承载 trigger_registry.py 零生产消费方且节点未标红。影响：按图施工/按图审计者会把"已建成"误判，触发器编排实际全图无人注册无人触发。建议修法：module_ref 改指 `src/zephyr/trading/trigger_registry.py` 并将该节点补红节点标记（编排缺口），或把 local_order_queue 从该节点摘除另挂 X-S2-04 已挂节点。验证法：§2 轴 D 验证法。
2. **[P2] 生产孤儿空转**（checklist #8）。现状：队列被创建从不被喂单。建议修法：要么在 qmt 下单链路真实接线 enqueue，要么降级 MATURITY 并在 TDM 摘除在网叙事。验证法：§2 轴 C 验证法。
3. **[P2] FAILED 恒 0 监控盲区**。现状：状态机三态只走两态，health_check degraded 不可达。建议修法：重试达 max_attempts 时置 FAILED+health_check 反映。验证法：注入恒抛 mock 看 health_check.level。
4. **[P2] 无上限重试+无死信**。建议修法：max_attempts（如 5）+超限转 FAILED+error 上报；永久拒单异常类别直接终态。验证法：毒单剧本观察 attempts。
5. **[P2] 无持久化重启丢单**。建议修法：pending 落盘（.runtime/sessions 或 DB）+启动重载，或显式声明"仅进程内"并把 TDM 注释"落盘先于生效"改挂实际承载。验证法：重启丢单复现。
6. **[P3] LocalOrderQueueError 定义零 raise（错误契约死条目）；_send 锁外写共享状态**。验证法：grep LocalOrderQueueError 使用点为 0。

## 5 挂起疑问

- trigger_registry.py（MOD-TRIG-001）应属哪个 TDM 节点/是否该独立开对象审查——本报告只判"锚错位"，其自身 15 条扳机清单的优先级仲裁正确性留待专对象（建议收口方登记）。
- qmt_trading_session 的 enable_algo_queue 上线路径是否存在真实开启计划（默认 False+无喂单=三无）；若 QMT 柜台上限 2~3 笔为真，算法单不排队直发是否会实际撞限需 Owner 提供柜台实证。

## 6 完备性自评

六轴全查（A 数学四问：本对象无统计公式，间隔调度边界已过；B 上游=order_manager 异常契约已查；C 下游 grep 全仓；D 同族=trigger_registry 双承载已查；E 五问：静默失败=FAILED 盲区、断供=重试永动、时序=monotonic 无死角、重复触发=enqueue 幂等依赖 order_id 上游、假阳性=health_check 假 ok）。长尾：①order_manager.submit_order 内部行为归 ex_core 其他对象；②qmt_file_bridge 文件桥全链归 blueprint_qmt_file_bridge 域对象；③真实 QMT 柜台行为无真机不可实测。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
