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

## 22:4x 增补（红队与复测车道回来后新增的可执行项，均无方向分叉）

### B12 ★★ 护栏：`prestage`/恢复类脚本写 tracked 热配置前必须与 HEAD 比对（R-056a，本役最实用的一条）
- **为什么**：本役最后抓到**新签名**——`tasks.yaml` 工作区字节被替换成**一条死信的 19:30 快照**（blob `a11bc4fcb402`），
  且 `pending/processing/done` 无项引用它；4 分钟后同一签名又给刚进 HEAD 的推导器在**索引面**写了一笔 `D`。
  ⇒ 抹除的第二种形态不是"文件消失"，而是**"文件退回一个不存在的历史状态"**，比消失更难发现。
- **改法**：`scripts/git_commit.py` 的 prestage/快照恢复路径（及任何"从 blob 写回"的工具）在向 **tracked** 文件写入前：
  `git show HEAD:<path>` 比对 ⇒ 若待写字节相对 HEAD **落后**（缺少 HEAD 已有的行/任务块），**拒写 + 落审计留痕**，不许静默覆盖。
- **验收**：注入一份过期快照 ⇒ 护栏必红（拒写并留痕）；正常恢复 ⇒ 放行。**能红判据要真跑**，不接受"逻辑上会拦"。

### B13 两处"真偷懒"吞异常（复测车道抽样实证，非模式命中）
- `src/zephyr/data/ch_reader.py:130`：引擎探测失败 ⇒ 退化成**不带 FINAL 的计数** ⇒ **会掩盖真实缺口**（数出来的行数是未合并的）。
- `src/zephyr/alt_data/.../sector_distribution_comparator.py:77`：逐行 fit 失败**静默丢弃**仍返回"有数"表。
- 改法：两处都改成"**失败会响**"（六向台账第⑥向）——出声 + 显式标记不可用，不许返回看起来正常的表。
- 注：`fail-open` 面上另有 5 处抽样**全是设计意图降级**，**不要一起改**（那是 #273 要防的"顺手放宽"反向版：顺手收紧也是病）。

### B14 告警的"最后一米"仍断（8 条 breach 只落 1 件 failures/）
- 实测：300s 内同 `task_id` 去重 + `_alert_breaches` **不读 notify 返回值** ⇒ 连发 8 条只有 1 条留痕。
- 改法：去重指纹按 **端点 × 指纹** 独立（正在落地的 `alert_webhook_dispatch.py` 就是这个不变式），
  且 notify 返回值必须被读、失败必须出声。
- **交叉核对**：`st-ff-alarm2-20260918` 办的是出口，本条办的是入口汇聚，**两半都要落才是"会响"**。

### B15 两条数据面新断点（各车道均未记载，本役首次发现）
- `c1_market.daily_valuation`：**14 个周六/周日被写成有数日**（每日 5,534~5,562 行，周六=周日同数，
  对照 `kline_daily` 同日 0 行）；且 09-16/09-17 各仅 2,000 行 ⇒ **部分写入第三次复发**（BRK-043 的"复发"在续）。
- `c1_market.alt_movie_boxoffice`：**表根本不存在**（全库 ILIKE 0 命中），而普查把它当"空表"记 ⇒ 台账要改 `gap_type`。
- 验真：`SELECT trade_date, dayOfWeek(trade_date), count() FROM daily_valuation FINAL WHERE trade_date NOT IN (SELECT DISTINCT trade_date FROM kline_daily FINAL WHERE trade_date>='2026-07-01') GROUP BY 1,2`

### B16 尺子要把"测不到"与"真断链"分开（否则 CH 抖动会污染验收数）
- 实测：`--all` 重生成后 ①向 15 条红**全部**由 `broken_hop` 驱动、evidence=`-1行`（查询失败哨兵值），
  日志 `CH query 失败(TCP+HTTP 均失败)` 12 次（`tick_data FINAL` 超时）；同表 `strategy_screen` 旧 1306 行 → 新 `-1 行`。
- `_row_count` **已有** -1/-2 三态，但 ①向判据没区分 ⇒ 加"不可测 ⇒ 该格判 `未可判`，不得判红也不得判绿"，
  并在输出里要求 CH 健康前置检查。
- 同时：`04_sixway_*` 两件**必须重生成后再入库**（当前判为已知失真，刻意未提交）。

### B17 一处注册表 headline 的真漂移（要改的数值已实测出来）
- `裁定#339` headline 写"tasks.yaml 63 任务 source=miniqmt"，**现值 57**（总任务 262→264）。
- 另：`#ARCH-338/339/343` 是 **z-arch 案卷系列不是裁定号**（总包混用过，见台账 R-048）⇒
  该更正动作落在 `lanes/arch_338_356_dossiers.md`；已实测回值：**#ARCH-343 importer W01=2/W02=0/W03=5/W04=4/W05=5/W06=0/W07=0**
  ⇒ 4 件有 importer、3 件零 ⇒ **"仅 W03 真接线"在 import 层不成立**；
  **#ARCH-338/339 需生产可达性 DFS**（不是 import 级），**该项尚未做，属真缺口**。

---

## 00:3x 增补两条（R-069 交回的，判据明确、无方向分叉）

### B18 ★ 给 `GATE-ERRCODE-CONSISTENCY` 补 own-scope（它现在违反宪法 §3.1）
- **实测**：`_check(gateway, files, **_kwargs)` **吞掉 kwargs、无 own-scope、观测面=全 git index**
  ⇒ 车道会被**他人 staged** 的未在册错误码连坐（本役 `paper_hedge_leg.py` 的 `ZA-RK-0075` 差点拦死一条无关批次，
  **只因对方车道先落地把它变成"存量"才侥幸自解**）。
- **改法**：按 `_build_own_scope` 模式（宪法 §3.1 房内标准）改成本批 diff 作用域，外来 staged 违规走 warn+审计（`_audit_foreign_staged`）；
  **或**按 §3.3 显式登记"全仓扫描"理由（结构校验型允许，但要登记）。
- **同根先例**：`604f414846`（"全仓对账门禁观测面=git index + HEAD 基线差分 + 全绿短路"）
  ⇒ **这条门是那次治本的漏网之鱼**，先读那次改动为什么没覆盖它。
- **验收**：造一条"他人 staged 未在册码" ⇒ 本批提交**不被连坐**且留下 warn 审计；自家批内引入未在册码 ⇒ 必拦。

### B19 把"提交前预跑进程内门禁"的载体入库（`gate_prerun.py`，下一役标准动作）
- **来源**：`st-ff-ailayer3` 自写。`run_gate_chain.py` 只聚合**脚本型**子门禁，
  **预跑不到本役任何一条死因门**（它们都是进程内 `GateSpec`）；它遍历 **113 个 GateSpec**、
  按真门调用形 `spec.check(gateway, files, **flags)` 只读预跑，把死信在入队前清到 0。
- **现状**：脚本躺在 `.runtime/tmp/`（TTL）。已三处留档：`.runtime/tmp/ff-recon/backup_prerun/gate_prerun.py`（97 行）
  + `G:/zephyr_cold/30_corpus/fullflow_harvest/prerun_20260919/`。
- **改法**：搬进 `scripts/governance/` 的**子包**（ARCH-031：`governance/` 根禁新增 .py），走新件三件套；
  并写进 `CONSTRUCTION_DISCIPLINE.md` §2 作为**入队前的标准一步**（R-065a 手法保留，载体换掉）。
- **三条使用坑（务必进 docstring）**：① 不传 `session_id` ⇒ SESSION/WORKTREE/HELD-OVERLAP/CLAIM-REQUIRED 四类**伪红**；
  ② 不调 `claim_files` ⇒ CLAIM-REQUIRED 伪红；③ **`claim_files` 返回的是"成功清单"**（失败者被排除），别读成冲突清单。

---

## 01:4x 增补三条（R-072 收口后剩下的，均已判清、无方向分叉）

### B20 ★ 单独落 `crisis_gate` 的一行日期修复（可脱离配额部分，不等 A00c/A16）
- **缺陷**：`log_crisis_gate_row` 把 `validate_date_literal()` 返回的**字符串** `'2026-07-17'` 塞进 `Date` 列槽位
  ⇒ 驱动取 `value.year` 抛 `AttributeError` ⇒ **被 `except Exception` 吞成一条 warning ⇒ 留痕静默蒸发**。
  ★ 缺陷自陈文案"表可能未注册 DDL，由总统筹 apply"是**假的**（`EXISTS TABLE c1_backtest.crisis_gate_log = 1`，列就是 `Date`）
  ⇒ **不要为它跑任何 DDL**（本役第二例"缺陷文案把施工者往错方向带"）。
- **正解**：行元组里 `day` → `date.fromisoformat(day)`（**一行**；`day` 作 SQL 字面量的口径不受影响）。
  驱动级已复现三种输入：str 抛 / `date` OK / tz-aware `datetime` OK。补丁件在 `.runtime/tmp/ff-recon/backup_last/`
  与 `G:/zephyr_cold/30_corpus/fullflow_harvest/last_20260919/`（另见车道 `backup/crisis_gate_proposed_datefix.py`）。
- **必须同时关掉那条假绿通道**：`tests/pf_alloc/test_crisis_gate.py:534`
  `test_log_crisis_gate_row_column_order_and_insert` 注入假 writer（只查列序、不查驱动序列化）
  ⇒ 该缺陷**在测试面上天然不可见**，这就是它能随 HEAD 存活的原因。补一条"真驱动序列化"级断言（`write_column` 或等价）。
- **注意别顺手带走配额改动**：同一文件里 `B1~B5/B7 退化 → warning` 那部分会**真激活 `CRISIS_SHRINKAGE_FLOOR=0.05`**
  （`regime_meta_allocator.py:109/426`）=改配额的主动闸 ⇒ **属 A18，不得混进本笔**。

### B21 用 clean HEAD 态复跑 16 目录（把"两轮 0 问题"从工作区口径升成 HEAD 口径）
- 现状：`st-ff-last` 两轮 12229 collected / 12181 passed / 0 failed，但**跑的是工作区字节**，
  其中 `src/zephyr/pf_alloc/{crisis_gate,allocation_inputs,allocation_orchestrator}.py` 含死车道未提交件（+31/-7、+45/-5、+13/-4）。
- **步骤**：先把 index 里的"回退快照"逐件判归口清掉（**Q-1**：`akshare_alt_provider.py` 186 删/0 增、
  `tests/zephyr/data/test_silent_latch_before_delivery.py` 265 删/0 增、`locks`=0）
  ⇒ 再 `git stash`-free 地确认 `git status` 干净 ⇒ 用 `.runtime/tmp/ff-recon/loopcheck.py` 重跑两轮
  （★ 先 `--only ai_layer` 自证脚本不产假红；**`--basetemp` 父目录必须先建**，见 R-067）。
- **同时确认两条"未触发≠已消失"的偶发面**：`tests/security/access_control/test_key_hierarchy.py:182`
  字面量黑名单随机假红（≈1.1e-4/次）、`msg_style_gate.py` 的 `"commit_gates/" in` 子串自豁免、
  `GATE-ERRCODE-CONSISTENCY` 观测面=live index（**B18** 同源）。

### B22 给 token 工具补"只增不减"自检（并把 B19 的优先级上调为"下一役第一件事"）
- 见 B19（同一件，优先级上调）：`batch_creation_tokens.py` 实弹吃掉过他道刚入 HEAD 的 4 行 token 并自报"落盘 True (CAS)"，
  **只有进程内门预跑抓到** ⇒ 预跑器不是"锦上添花"而是**当前唯一能拦住热册蒸发的面**。
- 工具侧要补：写后条目数**守恒或只增**（`len(creation_tokens)` 单调），减少即拒写并留痕。

---

## 附：本清单的产生方式
1. 各车道回报的 §"未达成 / 处方 / 指派"段 + 台账 `COORDINATION_LEDGER.md` R-039~R-057 的落点。
2. `dead_inventory.py`（**只读可重跑**）扫出的 12 件 GONE + 44 件 on-disk-unlanded；
   冷库差集普查扫出的 **121 件 ③wiped**（`lanes/cold_archive_diff.yaml` 逐件真值表）。
3. 红队/复测车道的 `lanes/{rbpit,rbstats,rbsafe,dag2,cold}_*.md` 处方集。
4. **未纳入本清单的**：需方向裁定的（→ A 类）；需 Owner 门位的（→ A00 / A3 / A6 / A9 / §末表）。

## 优先级建议（按"错了会让钱或结论变脏"排序）
**B1 → B2 → B4 → B12 → B3 → B13 → B14 → B16 → B8 → B9 → B10 → B5/B6/B7 → B15/B17 → B11**
（B1/B2/B4/B13/B14 是"已知具体缺陷 + 修法明确"，其余是"完工率缺口"，性质不同：
**前几条不做会持续产错数或让保命链失效，后几条不做只是慢**。B12 提到第四位是因为
**它是唯一一条"防住本役已四次发生的损失"的护栏**——不修，前面所有救回工作都要重做一遍。）
