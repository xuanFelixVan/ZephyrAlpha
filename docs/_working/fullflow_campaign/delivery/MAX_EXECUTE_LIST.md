---
ttl: task_bound
completes_when: 全流通战役收官且本清单每项都被执行或明确移交
---

# Max 待执行清单（B 类：路径明确、无方向分叉、只缺工时）

> 判据：**B 类 = Flash 已把"改哪一行/建哪张表/接哪根线"判清楚，但（a）工时不够、（b）在途车道占着、
> （c）需要先跑一轮全量才能安全动。** 这类不需要你再裁定方向，切到 Max 直接开工即可。
> 每项含：完整路径 → 具体改法 → **验收判据（含能红证据要求）** → 前置阻塞。
> ⚠️ 通用前置：**本役断点 85 条中仅 5 条被独立复跑过**（见 `MAX_REVIEW_CHECKLIST.md` §7.0）。
> 动任何一条前先跑 `R-019` 原始命令复测——**下列引用的行号与数字都是 2026-09-18 22:0x 的快照，可能已漂**。

---

## B1 ★★ 幂等键命门修复（资金级，判据最明确，无待裁）
- **文件**：`src/zephyr/shared/infra/idempotency.py` · `src/zephyr/ex_core/order_manager.py` ·
  `src/zephyr/ex_core/adapters/miniqmt_broker.py` · 测试 `tests/ex_core/`
- **实测缺陷（红队亲验）**：`begin_signal_batch` 在 `src/zephyr` **零调用者** ⇒ 批次判别符**恒为空串** ⇒
  键退化成 `sha256(strategy|symbol|UTC日|side)`（准确说法是"与被标识对象无关"，不是"随机"）。两条相反失效同因：
  ① **误吞合法单**：同日同标的同向第二笔被静默短路，返回**上一笔的 `broker_order_id`** 并写进新单
  ⇒ 两笔本地单共享一个券商号 + 幻影 SUBMITTED 事件（实测 `9001/9001, order_stock 总调用=1`）；
  ② **漏拦重放**：`trade_date` 取墙钟 UTC 日而非信号携带的交易日 ⇒ 跨日界重放得新键。
- **改法**：在信号→下单的**同一事务边界**上真调 `begin_signal_batch`（把批次判别符喂上真值），
  并把 `trade_date` 改为**信号携带的交易日**（禁墙钟）。
- **验收（必须两条同时成立才算修好）**：
  (a) 同日同标的同向两笔 ⇒ `order_stock` 调用=2 且两个不同 broker id；
  (b) 跨 UTC 日界的同信号重放 ⇒ 得到**同一个**键并被去重；
  (c) 未虚设部分保持：崩溃重启硬判据、PROCESSING 态 fail-closed、跨进程 PRIMARY KEY（原实测 6 进程→1 OK/5 FAIL）。
  **模拟盘 ONLY**（账户 `8886156677` 双重断言），禁实盘 `8887871993`。
- **阻塞**：无。

## B2 ★ `slippage_bps` 真正写 NULL（一行级，但被 A1 卡住）
- **文件**：`src/zephyr/ex_core/execution_report_producer.py:414`（`f"{float(v):.6f}"` 使 NULL 永不可达）
- **前置**：**A1 契约批准**（`architecture_model/contracts/cross_layer_contracts.yaml:806`）。
- **改法**：未成交/撤单场景显式产出 `None`，序列化层不再套 `float()` 格式串；
  并加**测试钉**（战役记录：本役曾有车道报"NULL 测试钉"但 HEAD 里 grep 0 命中——**先证明测试存在再宣称已修**）。
- **验收**：产一行 NULL 的 `slippage_bps` 进 `c1_market.execution_report`（可逆：追加新版本行，
  该表 `ReplacingMergeTree` **无版本列**已实测，追加比 mutation 可逆性好），
  且契约不再把它换算成 `-10000.0`。
- **同时该修的一条**：`ch_writer.query():471` HTTP 降级用 GET ⇒ 写语句必被 readonly 拒；`:477` 不读错误体 ⇒ 真因被吞
  （这是某次 HTTP 500 的真因，案卷在 `req_drift_01`）。

## B3 判定链的可读性与"只有判定没有验证"
- **文件**：`src/zephyr/plan_engine/judgment_settler.py`（`aggregate_report()` **全仓零调用方**）、
  `judgment_intraday_market_state` 表（除结算器外**零读者**）、`c1_market.judgment_plan_verification`（线上 **0 行**）
- **性质**：三条都是 R-021 型"只写不读"。修法是**接一处真消费**（作战室/日报投影）而不是加告警。
- **验收**：`aggregate_report()` 至少一个 `src/**` 内调用者（注意 ORPHAN-MODULE 只 `git grep` `src/**/*.py`，
  scripts/ 里的 import **不算引用**）；`judgment_plan_verification` 行数 > 0 且能对上被验证的 plan id。
- **前置**：z-judgment2 正在落 SSoT 注册批（同批含四表哨兵腿）→ 在其之后做，避免抢 `plan_engine/**`。

## B4 pf_alloc L1 危机闸 33 行接线落回（**冷备里，越晚越危险**）
- **文件**：`src/zephyr/strategy_pipeline/pipeline_events.py`（`_crisis_l1_check`，HEAD 与磁盘 `grep -c`=0）
- **来源**：`G:/zephyr_cold/30_corpus/fullflow_harvest/20260918-194729/worktree/src/zephyr/strategy_pipeline/pipeline_events.py`
  （z-cold 车道正在出四态判清单，含 diff 摘要）
- **性质**：`pf_alloc_daily` 唤醒链的 L1 闸现在**既不在 HEAD 也不报错**——最坏的一种状态。
  在其落回之前，任何"危机闸已接电"的表述都不成立。
- **前置**：A5 的授权判据（死会话遗产算不算在途）。

## B5 L0 生命周期族接线（引导/收尾链整族纸面，BRK-003）
- **文件**：`src/zephyr/orchestrator/lifecycle/{startup_sequencer,teardown_manager,rolling_upgrade,state_synchronizer,state_propagation,system_transfer,session_conflict,incident_postmortem,housekeeping}.py`（9 件）
- **要接的**：AutoRuntime L0 引导/优雅停机/滚动升级/状态同步。
- **复测提示**：本项属"未复测 80 条"之一，先跑 GOMAP 口径 `python -c "...governance_operations_map...['families']['L0_lifecycle']"` 复测 wiring 是否仍是 `suspect_orphan`。

## B6 反馈循环引擎（FF-12 闭环回流的实体，BRK-011）
- **文件**：`src/zephyr/feedback_loop/**`（340 .py，普查称 200 件零入度）
- **注意口径**：BRK-007/008 已实证**两个零入度口径差 16 倍**（静态 1585 上界 vs GOMAP 严口径 95）⇒
  先按 GOMAP 严口径取子集再施工，别按 340 件全接。

## B7 决策层与策略工厂的建节点（FF-06/FF-03，普查完工率最低处）
- **决策**：depgraph `decision_nodes` 213 行 100% `planned`；1754 层里 1744 是 ARCH-056 占位，真实 10 层中 6 层未建
  （信号层/主力行为层/大盘预测层/知识图谱因果层/学习层/自评估层）。
- **策略工厂**：16 节点仅 4 建成；`FAC-E7 模拟盘前哨` `build_status=pending` 且 `module_ref=None` ⇒ E6→E8 断链。
- **复测提示**：同上，属未复测集。

## B8 任务依赖边补全（BRK-050，89% 无依赖）
- **文件**：`src/zephyr/data/config/tasks.yaml` · 生成器 `scripts/derive_task_dependencies.py`（**刚从 blob 救回，已 staged**）
- **现状**：`264 任务 / 236 无依赖 / 28 有依赖`；前手产物自称"高置信 22 条已 `--apply`"但净增仅 1 条（账不对，z-dag2 正在分辨）。
- **要做的**：跑 `--dry-run` 出清单 → 按高置信 `--apply`（幂等判据：二次跑 `tasks_touched: 0`）→
  中/低置信留在文档，**不硬塞**（多生产者歧义/跨文件一跳/语义倒挂是机械不可推的，要人看）。

## B9 数据面：换源与回补的可施工部分（不含 Owner 门位的三条）
- `rate_decision_calendar`：Fed 官网（实测 HTTP 200）+ 东财 `RPT_CBANCIAL_RATE`（200 但需 `columns` 参数）两条 provider 腿；
  ★ 注意 `fed_official`/`eastmoney_datacenter` 两个 source **尚未注册** ⇒ 先注册再建任务，否则必失败空挂。
- `daily_valuation`：写侧禁写 0（错值进闭环，实测 `close<>0` 计数=0、跨表 20/20 不一致）。
- `cftc_positioning` / `gold_etf_holdings`：provider 腿已落（`df42bf8374`），
  **要做的是把一次性回填变成常态调度**（实测两表 ingest 只有 2026-09-18 单日）。
- `northbound_hold_snapshot`（三接口失效 + 243 组撞码）、`index_valuation_daily`（双行腐败）：按 RULE-DATA-OPS 判重，
  **判重只准用 `scripts/ch/check_tick_duplication.py`，禁聚合数**。
- **不在此列（Owner 门位）**：ETF 分钟 4.12 亿行时区劈叉的 `--execute`、L2 付费权限、北向资金替代源注册（A3/§7）。

## B10 循环检查与全量回归（Owner 硬要求："连续两轮 0 问题"）
- **做法**：逐目录跑 `tests/**`（全仓一次跑会 OOM，本役有内存耗尽事故在案），
  每目录记 `collected/passed/failed`；发现即改；**再跑一轮**；两轮都 0 问题才算这一项过。
- **同时**：红蓝 §6 十二面的余 8 面本轮已派 4 条车道（`z-rb-pit`/`z-rb-stats`/`z-rb-gov`/`z-rb-safe`），
  它们的结果要并入同一轮复核，**不要当成两件事**。
- **禁**：把"未跑"记成"通过"（本役最重的罪，总包自己犯过一次并已在全役首屏入账）。

## B11 收口批（Flash 可做但需串行窗口，若我未做完则由你接手）
- 统一裁定号登记：战役内部 `R-0NN` → `ruling_registry.yaml` 正式 `#NNN`（**总包独占写**，并发风暴下曾整批被覆盖）。
- 注册表标题更正：`#ARCH-338/339/343` headline 计数（等 `st-ff-rv3-20260918` 的 GOMAP/ROOR 实测值）。
- `skeleton/04_sixway_*` 两件**先重生成再入库**（当前判为已知失真，刻意不提交）。
- 临时件清零：`.runtime/tmp/ff-recon/`、`ff_quarantine/`、`.runtime/tmp/fullflow/`；
  注册表目录 18 个 `.capability_*.tmp`（z-rb-gov 在清）。
- claim 全释放：读 `.ailocks/registry.json` 的 **`locks`** 键核实（不是看命令退出码）。
- ⚠️ **`git add -A` 禁用**：index 现有 5 个文件带 staged 净删（他车道在途，§3.4 不代修），全量 add 会吸收他人内容。

---

## 附：优先级建议（按"错了会让钱或结论变脏"排序）
**B1 → B2 → B4 → B3 → B8 → B9 → B10 → B5/B6/B7 → B11**
（B1/B2/B4 是三条"已知具体缺陷 + 修法明确"，其余是"完工率缺口"，性质不同：**前三条不做会持续产错数，后几条不做只是慢**。）
