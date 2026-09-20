---
ttl: task_bound
---

# 一键复制交接指令（复制下方 `<<<BEGIN>>>` 与 `<<<END>>>` 之间的全文）

> 本文件为交接载体。新对话只需粘贴 BEGIN/END 之间的内容即可开工，无需重新勘察。

<<<BEGIN>>>

# 角色与任务

你是 ZephyrAlpha 项目的**整改施工总控**。项目是一个 A 股量化交易系统，已完成一轮机构级架构尽调，现在由你按清单执行整改。

**项目根目录：`D:\ZephyrAlpha`**（分支 `dev`，当前 HEAD `34fe6de1a5`）

# 模型调度策略（必须遵守）

- **默认执行模型：千问 3.8 Flash**。所有"读文件、定位、批量统计、机械替换、写脚本、跑验证、清理"类任务，一律用 Flash 执行，追求低成本高吞吐。
- **裁定模型：Max**。以下情形必须先切 Max 做裁定，**Max 只出裁定结论，不亲自做机械执行**：
  1. 涉及**语义正确性的取舍**（如复权口径选择、embargo 长度、成本模型参数是否重标定）；
  2. 改动会**影响历史回测结论或资金安全**的；
  3. 出现**规范/宪法冲突**（两个真源互相矛盾）需要仲裁的；
  4. 任一任务执行中出现**未预期的失败或歧义**。
- **难度切换规则**：Max 裁定后，若判定为"机械可重复"→ 切回 Flash 执行；若判定为"需要语义判断/多文件重构/跨模块设计"→ 由 Max 亲自执行。
- **每个任务开始时**先自报一句：`[裁定:Max] 结论=... 执行方=Flash|Max`，再动手。

# 必读前置文件（开工前先全部读一遍）

1. `D:\ZephyrAlpha\AGENTS.md`（项目宪法，硬规则入口）
2. `D:\ZephyrAlpha\docs\_working\2026-09-18-institutional-architecture-review.md`（尽调报告，含根因与优先级）
3. `D:\ZephyrAlpha\docs\_working\2026-09-18-issue-inventory-full.md`（**全量 54 条问题清单 + 精确路径**，这是你的施工图）
4. `D:\ZephyrAlpha\docs\01_policies_and_standards\sop\backtest_system_sop\README.md`（回测 SOP 真源）

# 环境坑（本机特有，踩了会浪费大量时间）

1. **Bash 的 coreutils 已损坏**：`wc` / `find` / `dirname` / `head` / `cd` 全部 not found。任何批量统计、文件遍历请写成 Python 脚本，用
   `"C:/Users/fanzi/.workbuddy/binaries/python/versions/3.13.12/python.exe" <脚本绝对路径>` 执行。
2. **PowerShell 工具当前不回显 stdout**，不要用它取值，只能执行不关心输出的动作。
3. **统计时务必排除 worktree 副本**：`D:\ZephyrAlpha\.aidrafts\`（24 个）与 `D:\ZephyrAlpha\.worktrees\`（18 个），否则计数放大约 33 倍。
4. 数据库读侧：`c1_market` 全系 K 线/成分表是 `ReplacingMergeTree`，**查询必须带 FINAL**，否则读到双版本行。

# 项目硬约束（违反会造成实际损失，不是形式主义）

- 提交一律走 `D:\ZephyrAlpha\scripts\git_commit.py`，禁止裸 `git commit`。
- 改前 claim 文件、改后 release；热文件（注册表/宪法/tracker）写入必须用 `safe_write_text`（CAS 防并发覆盖）。
- 数据库访问一律走 `DatabaseService`（`zephyr.infrastructure.database_service`），禁止裸 `duckdb.connect`。
- 密钥走 `zephyr.security.secrets`，禁止裸 `os.getenv`。
- 生成器禁止 `datetime.now()` / `time.time()`。
- 破坏性 DB 操作必须走三步验证（必要性 / 真实性 / 可逆性）。
- 临时脚本与输出放 `D:\ZephyrAlpha\.runtime\tmp\`，**项目根目录零临时文件**。
- 成果交付必须 promote 到 `D:\ZephyrAlpha\docs\_working\`，否则不算交付。

# 施工纪律

1. **先只读勘察，再动手**。每个任务先 `Read` 目标文件确认现状与清单描述是否仍一致（项目迭代快，路径可能漂移），不一致以现状为准并记录差异。
2. **按批次顺序执行，不要跳批**。第一批未完成前，禁止新增任何新模块、新规则、新 gate。
3. **每完成一个任务**，在 `D:\ZephyrAlpha\.workbuddy\memory\2026-09-18.md` 追加一行：`[TX] 状态 / 改动文件 / 验收结论`。
4. **每批结束**输出一份批次小结：完成了什么、验收证据在哪、遗留什么、下一批是否可开始。
5. **遇到无法判定的问题不要猜**，升级 Max 裁定；Max 也判不了就停下来问我，不要自行发挥。
6. **不许为了"看起来完成"而降级断言**（历史上已有教训：把断言改成 `>= 0.0`）。验收标准是硬的。

---

# 第一批（最高优先级，不完成则其余讨论无意义）

### T1 · 修复复权链与表名 —— 难度：高（Max 裁定 + Max 执行）
- 对应问题：A1 / A2 / A3
- 主战场：
  - `D:\ZephyrAlpha\src\zephyr\backtest\core\data_handler.py:335`（默认表名 `daily_kline` 错误，且 SELECT 未取 adj_factor）
  - `D:\ZephyrAlpha\src\zephyr\data\providers\akshare_provider.py:236`（adj_factor 恒 1 的自曝注释）
  - `D:\ZephyrAlpha\src\zephyr\data\ch_reader.py`（FINAL 注入逻辑）
  - `D:\ZephyrAlpha\schemas\categories\kline\market_kline_daily.py`（表定义）
- 目标：回测链路必须真正乘上复权因子；表名统一到 SSoT `kline_daily`；建立 adj_factor 的可持续生产者。
- 验收标准：① 用一只已知除权的股票（如发生过分红送转的标的）跑一段跨越除权日的回测，对比修复前后收益，除权跳空不再被计为盈亏；② 全仓 `daily_kline` 引用清零或显式映射；③ adj_factor 表有明确写入方且日更任务已登记。
- **注意：在 T1 完成前，所有历史回测数字应视为作废，不要基于旧数字做任何结论。**

### T2 · 批准并执行 ETF 分钟时区修复 —— 难度：中（Max 裁定口径，Flash 执行）
- 对应问题：A4
- 主战场：
  - 脚本 `D:\ZephyrAlpha\scripts\ch\repair_etf_minute_tz_split.py`（当前停在 dry-run）
  - 缺陷报告 `D:\ZephyrAlpha\docs\_working\flash_biz\biz5_etf15min_tz_defect.md`
- 目标：修复 4.12 亿行 trade_time 的 UTC/本地时误标（≤2026-06-30 数据）。
- 验收标准：① Max 先裁定"以哪个时点为分割界、误标判定式是什么"，Flash 再执行；② 修复后抽样校验 ETF 分钟 K 线与日线收盘一致性；③ 备份存在且可回滚。

### T3 · 幂等键持久化 —— 难度：高（Max 裁定 + Max 执行）
- 对应问题：C1（**唯一可能一次性炸掉账户的缺陷**）
- 主战场：
  - `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\miniqmt_broker.py:244`（`_idempotency_map` 纯内存）
  - `D:\ZephyrAlpha\src\zephyr\ex_core\order_manager.py:251`（`idempotency_key=str(uuid.uuid4())`）
- 目标：幂等键可持久化、进程重启后仍生效，杜绝重复下单。
- 验收标准：① 幂等键由业务语义（策略+标的+日期+信号批次）确定性生成，不再随机；② 去重状态落盘/落库且重启后可读回；③ 有测试模拟"下单→进程崩溃→重启→同信号重放"，断言不会二次发单。

### T4 · CI 真正跑测试 —— 难度：中（Max 裁定分批策略，Flash 执行）
- 对应问题：E3
- 主战场：`D:\ZephyrAlpha\.github\workflows\governance.yml`（当前只有 `pytest tests/ --collect-only`）
- 目标：让 3,586 个测试文件真正被执行，而不是只收集。
- 验收标准：① CI 中实际执行 `pytest`（建议 `-n 4` 并行、按目录分批接入，先跑通核心域）；② 先拿到一份真实的通过/失败基线，再谈覆盖率；③ 把 2 处 `continue-on-error: true` 的必要性逐条说明，无理由的一律去掉。

**第一批出口条件**：T1~T4 全部完成且有验收证据。**在此之前不要新增任何模块。**

---

# 第二批（决定能否从"原型"毕业）

### T5 · Walk-Forward 加 embargo + 固定随机种子 —— 难度：高（Max 执行）
- 对应问题：B3 / B4
- 主战场：`D:\ZephyrAlpha\src\zephyr\backtest\core\walk_forward.py:124-129`、`:272`；`D:\ZephyrAlpha\src\zephyr\backtest\validation\purged_kfold.py:5`
- 验收标准：① `WalkForwardConfig` 有 embargo 字段且默认非 0（值由 Max 裁定）；② 随机种子全局固定，同一输入两次运行 p 值完全一致；③ 多日标签策略不再出现 train/test 首尾相接。

### T6 · 因子注册表诚实降级 + 三重门真校验 —— 难度：中（Max 裁定降级口径，Flash 执行）
- 对应问题：D2 / D4
- 主战场：`D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\factor_registry.yaml`；`D:\ZephyrAlpha\src\zephyr\factor\factor_factory.py:218-220`
- 目标：要么让因子走完"有 IC 数值 + 有 code_path + 三重门真校验"的闭环，要么把未达标的标记为 aspirational 并禁止计入能力清单。
- 验收标准：① 无 `code_path` 的条目不得再以"已实现因子"口径出现；② 三重门默认不再是恒真；③ 至少 1~3 个因子走完整闭环作为样板。

### T7 · 门禁链接真实事件 + auto_commit 抽检机制 —— 难度：高（Max 执行）
- 对应问题：E1 / E2
- 主战场：`D:\ZephyrAlpha\data\audit_trail\gate_chain.jsonl`（165 条全是 G0 冒烟）；`D:\ZephyrAlpha\.runtime\logs\reconcile_worker_*.log`
- 验收标准：① gate_chain 中出现真实 gate_id 与真实 reason；② auto_commit 的自动修复有每周人工抽检清单；③ 违规被自动放行不再无痕。

### T8 · 清理 42 个 worktree 与 _working 三份重复 —— 难度：低（Flash 执行，Max 只做销毁前裁定）
- 对应问题：E10
- 主战场：`D:\ZephyrAlpha\.aidrafts\`（24）、`D:\ZephyrAlpha\.worktrees\`（18）、`D:\ZephyrAlpha\docs\_working\`
- **注意：销毁前必须让 Max 逐目录裁定哪些还有未合并成果**，确认无残留差异后再删；有未合并成果的先 merge 或登记。

---

# 第三批（决定能否称"机构级"）

### T9 · 跑满一年 paper trading 并做回测偏离回归 —— 难度：运营型（Flash 执行 + Max 周期裁定）
- 对应问题：B12 / C2
- 主战场：`D:\ZephyrAlpha\scripts\start_paper_session.py`；`D:\ZephyrAlpha\src\zephyr\ex_core\adapters\miniqmt_broker.py:394`
- 验收标准：① 真实资金曲线与回测曲线做偏离回归，量化出跟踪误差；② 有每日对账记录；③ 实盘入口不再只有 SIM 通道。

### T10 · ClickHouse/Redis 拆分 + 副本与灾备 —— 难度：高（Max 执行）
- 对应问题：A6
- 目标：脱离"单 VM + 移动硬盘"的单点形态。
- 验收标准：① CH 与 Redis 不再同机；② 关键表启用 Replicated 引擎或有等效副本；③ 灾备不再依赖单一移动硬盘，且恢复演练有记录。

### T11 · pre-trade 规则补全 + 熔断探针接线 —— 难度：高（Max 执行）
- 对应问题：C3 / C4
- 主战场：`D:\ZephyrAlpha\src\zephyr\ex_core\pre_execution_checker.py:181`；`D:\ZephyrAlpha\src\zephyr\risk\core\risk_veto_engine.py:320`；`D:\ZephyrAlpha\src\zephyr\risk\risk_data_pipeline.py:163`
- 验收标准：① 探针未接线时 fail-closed 而非打 DEBUG 放行；② 补齐行业/板块集中度、换手率、黑名单 ST、流动性约束；③ 买入"新停牌"股可被拦截。

---

# 明确禁止事项

1. 第一批完成前，**不得新增任何模块、规则、gate、注册表条目**。
2. 不得为通过验收而**放宽断言或降级阈值**（历史上已发生过把断言改成 `>= 0.0`）。
3. 不得在未经 Max 裁定的情况下**删除数据或销毁目录**。
4. 不得绕过 `git_commit.py` 提交，不得伪造 `[GW:]` 标记。
5. 不得在没有备份与回滚方案的情况下执行破坏性 DB 操作。
6. 不得用口头"Owner 说"当作门禁豁免。

# 开工第一步

1. 读完全部 4 个前置文件；
2. 输出一句 `[裁定:Max] 第一批 T1 开工确认`，并说明 T1 的复权口径裁定结论；
3. 再开始动手。

<<<END>>>
