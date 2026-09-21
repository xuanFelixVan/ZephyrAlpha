---
ttl: task_bound
title: 深度审查作业簿——券商柜台文件桥
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：券商柜台文件桥（X08）

- 状态: **已审**
- 级别: P0｜类型: 模块
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:319`
- 生产调用方: OrderManager.register_broker（经 qmt_trading_session 装配/real+sim 双环境；文件头 [MATURITY] draft）
- 测试文件: tests/ex_core/adapters/test_qmt_file_bridge_broker.py（15 passed，实测——**全部用例以 idempotency_key==order_id 构造订单，掩盖 P0-1 双键错配**）
- 备注: 真钱边界

## 1 对象快照

- **范围**：qmt_file_bridge_broker.py 全文 836 行（QmtFileBridgeBroker + CounterStateMirror 柜台镜像 + 指令/回执文件状态机 + HTTP 快路径）。
- **排除项**：miniqmt_broker（xtconstant 常量对照归该对象审）、qmt_trading_session 装配壳、LocalOrderQueue。
- **测试覆盖概况**：15 passed（21.38s）。覆盖指令写入/撤单写入/GBC 读/csv 容错。**未覆盖（且系统性掩盖缺陷）**：测试订单一律 idempotency_key==order_id，生产 OM.create_order 两键独立 uuid4（order_manager.py:239,251）——键配对全链失真未有任何测试暴露。
- **材料包缺项声明**：运行时证据包无（柜台 CSV 实际格式无法离线取证）；checklist 15 条已过——**命中 #3 测试假阳性、#13 外部契约（文件桥协议字段对照记受阻）**。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **双键错配（本案核心）**：submit_order 把 `order.idempotency_key` 写进指令 order_id 列（→柜台 remark），却返回 `order.order_id` 作 broker_order_id；本地 `_order_cache` 以 order_id 为键——OM.create_order 两键为独立 uuid4 → 生产链上 remark≠order_id 恒成立 | qmt_file_bridge_broker.py:488,506,502 vs order_manager.py:239,251 | **P0** | 用 OM.create_order 造单（两键不同）走 submit→镜像同步，断言 order_cache.get(remark) miss |
| A | 错配传导①状态推进失效：_sync_orders/_apply_acks 均以 `order_cache.get(remark/ack.order_id)` 配对 → 全 miss → 订单状态永不离开 SUBMITTED、sysid 永不回填 | qmt_file_bridge_broker.py:191,296,742 | P0(同上) | 同上集成复现 |
| A | 错配传导②成交配对失效：_sync_deals `order_cache.get(remark)` miss → 不更新订单；Fill.order_id=remark=idempotency_key，OM._on_fill 按 fill.order_id 查单 miss（不转 PARTIAL/FILLED）；paper dispatcher 双查（order_id、broker_order_id==order_id）全 miss → "成交无法配对本地订单，跳过入账" | qmt_file_bridge_broker.py:296-316 + order_manager.py:519 + start_paper_session.py:346-357 | **P0** | 同上+断言 dispatcher lookup 返 None |
| A | 错配传导③撤单链断裂：OM._cancel_at_broker 传 order.broker_order_id（=file bridge 返回的本地 order_id），cancel 指令 symbol 字段=该值，柜台按 remark 匹配 → remark=idempotency_key≠order_id → **撤单指令找不到目标**；且 cancel_order 无条件返回 True（"仅表示指令已写入"）→ OM 判撤单成功转 CANCELLED，柜台单仍活跃 | qmt_file_bridge_broker.py:508-521 vs order_manager.py:410-413,442 | **P0** | 造两键不同订单撤单，读指令文件看 symbol 列与 remark 口径差 |
| A | avg_fill_price 记末笔价非加权均价：cached.avg_fill_price = price（本笔价覆盖）——多笔部成订单均价失真（该字段在本 broker 内仅缓存展示，OM._on_fill 另算正确均价，但镜像口径错） | qmt_file_bridge_broker.py:299-300 | P2 | 两笔不同价部成断言 avg≠加权值 |
| A | fill_timestamp=now_utc() 冒充成交时刻（真实时刻在 Deal.csv row[19]/[20] 却只进 deals 展示字典）——回报时间口径失真 | qmt_file_bridge_broker.py:289,307 | P3 | 对比 fill.fill_timestamp 与 deals["time"] |
| B | 价格笼子无米之炊：check_price_cage 调用不传任何基准价（ask1/bid1/last/prev_close 全缺）→ 恒 UNKNOWN → 原价过笼（详见 X05 P1-1，本处为消费端现场） | qmt_file_bridge_broker.py:476-485 | P1 | 直调观察 UNKNOWN 原价返回 |
| B | qty=int(order.quantity) 静默截断小数（Decimal('100.5')→100）——上游应保证整数，无断言 | qmt_file_bridge_broker.py:466 | P3 | 造 100.5 股观察静默截断 |
| C | 消费方：OM 经 BrokerInterface 调用（submit/cancel/query_order/get_positions/register_fill_callback）+ 柜台镜像查询族（get_counter_*/get_available_*/get_pending_orders_count）。爆炸半径=实盘资金全路径（env=real 硬编码真实账户 8887871993） | qmt_file_bridge_broker.py:336-341,575-601 | 记录 | 读 ENV_CONFIG |
| D | 旁系：miniqmt_broker（xtquant 直连，价格笼子传真盘口）与本桥（无盘口降级）双通道防御不对称；board_lot 校验本桥只拦 BUY<min_unit（:467），不校 increment 对齐（卖出侧全放） | qmt_file_bridge_broker.py:464-468 | P3 | 造非对齐卖出量观察放行 |
| E | **静默失败面**：①柜合同步线程异常仅 warning 续跑（:651-652，可接受但连续失败无熔断/告警计数）；②ack/order CSV 读失败静默返空（:675-676,686-687,719-720）——**柜台 CSV 断供=状态/成交全停且无告警**（"断了没人知道"典型）；③_processed_fill_ids 纯内存，重启后 Deal.csv 全量重放重复回调（下游 OM/tracker 去重也多内存态，依赖对账兜底） | qmt_file_bridge_broker.py:651-652,675-676,129,271-273 | P1 | 改名 Stock 目录模拟断供，断言无 error 级日志 |
| E | 假阳性：cancel 恒 True（见 A 轴③）；HTTP 快路径 200 即算受理成功，不追踪该单后续（若 EXEC 受理后崩溃，指令既不在文件也无 ack——镜像 Order.csv 有则可追，无则丢单无痕） | qmt_file_bridge_broker.py:508-521,618-642 | P1 | 断言 cancel_order 返回值语义；HTTP 受理后查该单可观测状态 |
| E | 重复触发：submit_order 有 idempotency_map 拦截✓（进程内）；重启后 map 清空但指令行已落文件——**重启重放不会重写**（submit 由上层重发才触发）；HTTP+文件降级路径互斥✓不会双写 | qmt_file_bridge_broker.py:459-462,605-616 | 通过 | 同 idem 两次 submit 断言单行 |
| E | 时序：ack 文件偏移量断点续读✓（重启后 offset=0 全量重读→_apply_acks 幂等靠状态终态判断✓）；镜像 3s 轮询窗口内撤单与成交竞态由"终态不覆盖"防护✓ | qmt_file_bridge_broker.py:396,658,700-706,745-749 | 通过 | 读审 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

1. **柜台全量镜像/对账通道**：对等已有（方向）。券商 drop copy+独立对账流是业界标准（FIA Drop Copy Recommendations，FIA，2019，https://www.fia.org/sites/default/files/2019-05/FIA-Drop-Copy-0.pdf ；Deribit Starbase FIX Drop Copy 文档（ID 映射/去重/gap replay 指引），Deribit，https://docs.deribit.com/starbase/fix-drop-copy-api ；OnixS FIX Drop Copy 综述，https://www.onixs.biz/insights/understanding-fix-drop-copy-in-financial-trading ）。CounterStateMirror 全量镜像思路与 drop copy 对齐；但 **ID 映射与去重恰是 drop copy 规范的核心章节**——本桥的 remark/order_id 双键错配正跌在该规范最强调的坑上。
2. **重启重复回报**：立卡候选。重启后重复订单/回报需持久化去重+对账收敛（NautilusTrader #3176 IBKR 适配器重启重复订单实例，nautechsystems，2024，https://github.com/nautechsystems/nautilus_trader/issues/3176 ）。本桥 _processed_fill_ids 内存态属同型风险，建议去重集持久化（仓内 AppendOnlyDedupSet 现成）。
3. **协议字段官方对照（checklist#13）**：**受阻**——文件桥 pricetype("limit"/"latest")/CSV 列位与哑执行器(EXEC v16.4)的协议为本仓私有约定，无公开官方值可对照；QMT 官方 API 常量问题（历史案例 ae289436aa price_type LIMIT 0→11）属 miniqmt_broker 直连路径，不在本桥。建议：EXEC 协议契约表落盘为真源并加 smoke。

## 4 缺陷清单

**P0-1 remark/order_id 双键错配——状态推进、成交配对、撤单三链全断（测试假阳性掩盖）**
- 现状：指令写 idempotency_key、缓存/返回/撤单用 order_id；OM 造单两键独立 → 生产链 remark 配对恒 miss：①订单状态永停 SUBMITTED、sysid 永不回填；②成交永不配对本地订单（dispatcher 跳过入账，OM._on_fill 不推进状态）；③撤单指令 symbol=order_id 在柜台按 remark 匹配不到目标，且 cancel 恒返回 True → 本地假 CANCELLED、柜台单活跃。
- 证据：qmt_file_bridge_broker.py:488,502,506,508-521,191,296 + order_manager.py:239,251 + start_paper_session.py:346-357；测试掩盖证据：test_qmt_file_bridge_broker.py:77-78 等（idempotency_key==order_id）。
- 影响：实盘（env=real）下=静默错账（成交不入账）+资金敞口失控（撤单失效假成功）。爆炸半径=文件桥全部订单（实盘+模拟双环境）。文件头 [MATURITY] draft 与实盘用途不符加重风险。
- 建议修法：统一单键——指令 order_id 列改写 order.order_id（与缓存/返回/撤单一致），或全部通道改按 idempotency_key 配对且 cancel 传 idempotency_key；同时补"两键不同"的集成测试（OM.create_order 真实形态）；cancel 返回值改为柜台确认语义或注明"仅写入"并在 OM 侧不对该 True 做终态判定。
- 验证法：集成单测——OM.create_order 造单（两键不同 uuid）→ submit → 模拟 Order.csv/Deal.csv 回填 remark → 断言当前全 miss（复现）；修复后断言全命中。

**P1-1 柜台 CSV 断供静默无告警**（:675-676,686-687,719-720,651-652；OSError→返空续跑，QMT 导出停发=状态/成交全停无痕；修法：连续 N 轮读空/异常计 warning→error→health API 翻红（健康检查 API 已存在 b907bfbeb8 可挂接）；验证法：临时改名 Stock 目录观察日志级别）。
**P1-2 cancel_order 布尔契约撒谎**（:508-521 恒 True；OM 消费为真实撤单结果（order_manager.py:440-442 注释明确"透传券商端撤单布尔结果"）→ 假成功转 CANCELLED；修法：返回 None/抛"异步未知"，或 OM 对 file bridge 类 broker 走"撤单指令已写入，终态等镜像"分支；验证法：读两文件契约对比）。
**P1-3 价格笼子无基准价恒 UNKNOWN 过笼**（:476-485；与 X05 P1-1 同一缺陷的现场记录；修法：接 last/prev_close 至少回退链尾（可从 mirror/PositionStatics 或行情文件取）；验证法：超笼价单观察原价出桥）。
**P2-1 镜像 avg_fill_price 记末笔价**（:299-300；镜像展示/查询口径失真；修法：加权或标注 last；验证法：两笔部成对拍）。
**P2-2 _processed_fill_ids 内存态重启重放**（:129,271-273；修法：接 AppendOnlyDedupSet；验证法：重启后断言重复回调）。
**P2-3 HTTP 快路径受理后无追踪**（:618-642；200 即弃，EXEC 崩溃丢单无痕；修法：HTTP 受理单登记 pending 集，镜像超时未现单即告警；验证法：mock 200 后无 Order.csv 出现观察无告警）。
**P3**：①`_max_retry`/`#SENDING→#DONE` 状态机头注声称无实现（:8,363,372 死配置）；②fill_timestamp 用 now_utc 冒充成交时刻（:307）；③qty 静默截断小数（:466）；④卖出侧无 increment 对齐校验（:464-468）；⑤ENV_CONFIG 硬编码账户号在源码（:336-347，账户号非密钥但配置硬编码违反配置纪律精神）；⑥[MATURITY] draft/SAFETY=M 与实盘用途不符（:7,11）。

## 5 挂起疑问

1. EXEC v16.4 哑执行器解析指令的确切口径（order_id 列是否即写入 Order.csv remark）——本报告按"remark=指令 order_id 列"推演（_sync_orders 注释与 deals 处理佐证）；需 Owner 用真实柜台 CSV 取证复核 P0-1。
2. env=real 通道是否已实际投产（文件头 draft vs ENV_CONFIG 真实账户并存）——决定 P0-1 修复优先级。
3. min_unit 校验为何只拦 BUY（卖出零股合法性由上游 board_lot 保证？）——装配契约待确认。

## 6 完备性自评

- 六轴全查：A（双键错配数学/均价/时间戳/截断）、B（笼子无米之炊+协议字段受阻记）、C（消费方+真钱爆炸半径）、D（miniqmt 双通道防御不对称）、E（五问：静默=P1-1、假阳性=P1-2/测试掩盖、断了没人知道=P1-1、重复触发=通过、时序=通过）、F（2 条带 URL 对照+1 受阻）。
- 长尾：①EXEC 哑执行器侧（沙箱内脚本）未审（不在仓内）；②CounterStateMirror 各 CSV 列位假设（row[9]/row[15]/row[16] 等）无真实样本核验——离线环境受限，全部依赖注释自述；③test_qmt_file_bridge_full.py 构造脚本链路未跑（需真柜台）。

## 7 收口裁定（收口方填）
- 三态逐条：
- 修复 commit:
- 复检结论:


## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P0-1 双键错配: **确认**（独立核 submit_order:488/502/506、mirror._sync_orders:191、_sync_deals:296、_apply_acks:742、OM.create_order:242/:253 双独立 uuid4、旧测试 15 例全用 idem==order_id）→ 已治本：双键配对视图 _pairing_cache 喂四配对点 + cancel 经 order_cache 解析 remark + _dispatch_fill 以 dataclasses.replace 回解 Fill.order_id（Fill frozen）。
- 复检: 新增 TestDistinctKeyPairing 三回归（挂单同步/成交回解/撤单remark）+ 套件 18/18 + 扩散 adapters/OM/FillHandler 102/102 全绿。
- 遗留移交: 真柜台 CSV 取证（EXEC v16.4 解析口径）归实盘首日验证；position_monitor 只读消费不受影响。
- 修复提交: 队列 q-20260918-st-deeprev-20260918-0006。
