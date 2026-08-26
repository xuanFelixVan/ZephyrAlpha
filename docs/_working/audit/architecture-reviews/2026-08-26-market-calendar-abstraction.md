---
ttl: task_bound
---

# 架构评审记录：市场日历抽象（market_calendar）

> 日期：2026-08-26 ｜ 评审人：AI-CAL-001（Owner 书面委托，W0 派单 §〇）｜ 级别：L2 局部变更级（同层接口抽象化，MINOR）
> 对象：CAND-CRYPTO-001 晋升施工——scheduler/K线聚合/回测时间轴/PIT asof 四类消费点改日历注入式
> 依据：construction_workflow_sop Step 1.8（trae_036 §gov_arch_002）｜ 设计真源：94 号 §4.1（active v1.3.0）

## 1. KB 决策冲突检查

| 检查项 | 结论 |
|---|---|
| 94 号 §4.1 裁定（抽象接口+按市场注入，禁 if/else 判市场） | 方案完全一致：策略对象接口 + ASHare/Crypto 双实现，消费点只认注入实例 |
| 硬门槛（A股零行为变化） | ASHareCalendar=薄封装委托 trading_calendar.py 真源，真源本体一行不动；存量改动全部为"加可选参数默认 None→原路径" |
| 三道闸物理闸（市场后缀包+子目录） | 接口与 A股实现=共用层（data/calendar/），CryptoCalendar=共用接口的币实例（非 signal_crypto 业务包），符合"差异只走参数/规则集/实例"裁定 |
| CAND-CRYPTO-001 注册表 sub_layer | "data/calendar" 一致，落点 src/zephyr/data/calendar/ |
| 同名冲突 | feedback_loop.collectors.market_calendar.MarketCalendar（holiday 集，FLE 专用）语义不等价，包路径区分，不冲突 |

**结论：无冲突。**

## 2. 跨层循环依赖检查

- 新包 data/calendar/ 依赖：trading_calendar.py（同 D_DATA 域内委托）+ exchange_calendars（pip）+ 标准库。
- 消费方向：scheduler/fusion/pit_query（D_DATA 同层）→ calendar；backtest（下游层）→ calendar（仅经装配层注入产物，不新增 import）。
- calendar 包不 import 任何消费方；ASHareCalendar→trading_calendar 为同层单向委托。
- **结论：无循环，依赖方向单向（消费方→接口→真源）。**

## 3. 可观测性

- 消费点 calendar=None 解析为 A股默认实例时 DEBUG 日志一次（构造期，非热路径）；接口方法=纯函数无日志噪音。
- CryptoCalendar 无外部依赖，行为确定，无需运行时监控。
- 既有真源日志（exchange_calendars 加载/降级 warning）保持不变。

## 4. 数据一致性

- A股口径单真源：ASHareCalendar 全部委托 trading_calendar.py（XSHG 单例），与 c1_market.trade_calendar 表同源语义（trading_calendar.py docstring 已声明同源）。
- 双实现语义隔离：CryptoCalendar=自然日全集 7×24，不读 A股真源，无交叉污染。
- pit_query 默认 embargo 口径=自然日（现状），calendar 参数仅提供可选交易日路径，默认不变。
- **结论：无一致性风险（新增能力全为可选路径，默认路径=现状）。**

## 5. 回滚方案

- 新增 src/zephyr/data/calendar/ 包：独立目录，删除即整体回滚。
- 存量三文件改动（scheduler.py/fusion/pit_query）：均为追加可选参数，git revert 单提交即回滚，无数据迁移、无配置变更、无 DDL。
- 消费点默认路径与原路径等价（ASHareCalendar 委托同一真源函数），回滚不影响 A股行为。

## 6. 性能退化评估

- is_trading_day：ASHareCalendar 委托 lru_cache 单例真源，增量开销=1 次方法分派（纳秒级）。
- scheduler：日历判定频次=每时段触发 1 次，非热路径。
- fusion：calendar 参数仅在 resample 调用时展开一次 trading_days 集合，与现状显式传参同阶。
- pit_query：calendar=None 时 SQL 拼接路径与现状逐字节一致。
- **结论：无可测性能退化。**

## 7. 文档更新清单（Step 7 执行）

| 文档 | 动作 |
|---|---|
| 94_crypto_quant_expansion.md | frontmatter v1.3.0→v1.3.1；§4.1 补"已施工（commit hash）" |
| 00_index_trading_decision.md | §0/§7.3 同步（按 Step 7 规定动作） |
| candidate_module_registry.yaml | 仅 CAND-CRYPTO-001 条目行 status→promoted（其余零触碰） |
| depgraph | apply_depgraph --add-design-node 登记设计态节点+边 |
| 设施盘点（R11） | 补 data/calendar/ 路径 |
| 本评审记录 + 盘点报告 | 已落盘 |

## 评审结论

**PASS**（7 项全过）——准予进入 Step 2（全景图设计态登记）与 Step 4（施工编码）。

> 备注（遗留登记，不阻塞）：94 号正文缺 §4.5 章节（三道闸内容仅见于 v1.3.0 修订记录行，HEAD 与工作区一致，属 v1.3.0 提交时内容缺失）；按避让纪律不顺手改，登记 construction_progress_tracker.md §六报 Owner。
