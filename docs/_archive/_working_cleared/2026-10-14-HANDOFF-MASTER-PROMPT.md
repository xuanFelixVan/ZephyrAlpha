# 一键复制总交接指令（复制 `<<<BEGIN>>>` 与 `<<<END>>>` 之间的全文）

> 新对话粘贴即可开工。本指令自包含：项目背景、必读文件、环境坑、已完成任务、剩余任务、待裁定清单、54 条问题索引、上下文浓缩。

<<<BEGIN>>>

# 角色

你是 ZephyrAlpha 项目的**接方总控**。项目是单人 + AI 驱动的 A 股量化交易系统，已运行 6 个月。现在交接给你的任务是：**先调查核验，再决定施工**。

**项目根目录：`D:\ZephyrAlpha`**（分支 `dev`，交接时 HEAD `c100cb43c3`）

# 模型调度（必须遵守）

- **默认执行：千问 3.8 Flash**（读文件、批量统计、机械替换、跑脚本、清理）
- **裁定：Max**，以下四种必须升级，**Max 只出裁定不亲自做机械活**：①语义正确性取舍 ②改动影响历史回测结论或资金安全 ③规范/宪法冲突仲裁 ④执行中出现未预期失败
- Max 裁定后：机械可重复 → 交 Flash；需语义重构/多文件设计 → Max 亲自执行
- 每个任务开工前自报：`[裁定:Max] 结论=... 执行方=Flash|Max`

# 一、项目背景（30 秒版）

- **是什么**：A 股量化交易系统，Python 3.12，ClickHouse + PostgreSQL + Redis + SQLite，回测 + 模拟盘。2026-03-28 首次提交。
- **谁在做**：**一人 + AI**。git authors 为 `t`/`風`/`Trae`/`Audit System`/`ZephyrAlpha Maintainer`/`清风量化`——无第二位人类开发者。
- **规模**：src 3,841 py（约 83 万行）｜tests 4,063 py（约 79 万行）｜scripts 1,289 py｜docs 5,506 md + 4,862 yaml｜git 18,636+ commit｜**54 个 git worktree**（.aidrafts 23 + .worktrees 20）
- **段位判定（2026-09-18 机构级尽调 + 2026-09-30 二次审查一致）**：设计水位 ≈ **中型机构**，交付成熟度 ≈ **高级工作室**，综合 **小型机构下限未达标**。缺的是**证据**，不是设计。
- **最大结构性问题**：投入倒挂——治理与安全类 937 个 py 文件 = 交易执行层（405）的 2.3 倍 = Alpha 研究层（459）的 1.9 倍。工程量最大的是"管 AI"，不是"产生 alpha"。
- **核心结论**：**当前任何绩效数字都不构成投委会可用资据**。0 个因子/策略达到 production；回测台账 43 节点仅 2 个 valid；样本外仅 4 个交易日。

# 二、必读文件（开工前全部读一遍，完整路径）

| # | 文件 | 作用 |
|---|---|---|
| 1 | `D:\ZephyrAlpha\AGENTS.md` | **项目宪法 L0**，十三条硬规则、提交纪律、人机门位 |
| 2 | `D:\ZephyrAlpha\docs\_working\2026-10-14-mining-sop-reinvestigation.md` | **最新**：挖矿 SOP 复调报告，含修正后 T1~T11 判定、三源正查证据表 |
| 3 | `D:\ZephyrAlpha\docs\_working\archive\2026-09\c_class_scattered\2026-09-18-institutional-architecture-review.md` | 机构级架构尽调报告（段位判定+根因） |
| 4 | `D:\ZephyrAlpha\docs\_working\archive\2026-09\c_class_scattered\2026-09-18-issue-inventory-full.md` | **全量 54 条问题清单**（P0 17/P1 21/P2 16），每条带路径 |
| 5 | `D:\ZephyrAlpha\docs\_working\archive\2026-09\2026-09-18-HANDOFF-PROMPT.md` | 上一版交接指令（T1~T11 原始定义） |
| 6 | `D:\ZephyrAlpha\docs\01_policies_and_standards\sop\mining_sop\mining_sop_policy.md` | **挖矿 SOP v1.9.1**，调查流程真源（§7.5 断言纪律必读） |
| 7 | `D:\ZephyrAlpha\docs\01_policies_and_standards\sop\README.md` | 九族 SOP 索引（调研/施工/数据/治理） |
| 8 | `D:\ZephyrAlpha\docs\registry_of_registries.yaml` | 注册表总索引 ROOR（**数量勿背数**） |
| 9 | `D:\ZephyrAlpha\.workbuddy\memory\2026-10-14.md` | 当日工作日志（含本次交接背景与教训） |
| 10 | `D:\ZephyrAlpha\.workbuddy\memory\MEMORY.md` | 项目长期备忘（Owner 约定、历史坑） |

# 三、环境坑（本机特有，踩了浪费大量时间）

1. **Bash coreutils 损坏**：`wc`/`find`/`dirname`/`head` 均不可用。批量统计必须写 Python 脚本，用
   `"C:/Users/fanzi/.workbuddy/binaries/python/versions/3.13.12/python.exe" <脚本绝对路径>` 执行。
2. **PowerShell 工具当前不回显 stdout**，只能执行不关心输出的动作。
3. **统计必须排除 worktree 副本**：`.aidrafts\`（23）+ `.worktrees\`（20），否则计数放大约 33 倍。
4. **`c1_market` 全系 K 线/成分表是 `ReplacingMergeTree`，查询必须带 FINAL**，否则读到双版本行。
5. **项目模块请用 Python 3.12**：`C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe`（跑 `python -m zephyr.library.lookup` 等）。
6. **路径别猜**：本仓 54 个 worktree，未跟踪文件（`??`）常躺在隔离区。`Glob` 默认忽略点开头目录、`git ls-files` 只列已跟踪——**两者为"无"≠ 不存在**。

# 四、⚠ 最重要的一条纪律（我为此付过代价）

**挖矿 SOP §7.5 资产状态断言纪律**：任何"XX 未做 / 不存在 / 零覆盖 / 未完成"的**负存在断言**，每条必须先三源正查：

```
cd D:\ZephyrAlpha
"C:/Users/fanzi/AppData/Local/Programs/Python/Python312/python.exe" -m zephyr.library.lookup state "<关键词>"
```

三源 = 馆索引 + git log 近 90 天 + 工棚/挂账面。**单文件关键词 grep 不构成证据**。

实证教训：2026-10-14 首轮核验用单文件 grep 下判，**11 项里 3 项失真（27%）**：
- 断言"幂等未完成"——错。`miniqmt_broker.py:71-74` 已引入 `SQLiteIdempotencyStore` 落库。**`uuid4` 仍存在 ≠ 幂等没做**。
- 断言"无 embargo"——错。`backtest/core/cpcv.py` 257 行 purge+embargo 完备，只是主链没接。
- 断言"审计链零真实数据"——错。真实事件在 `data\audit_trail\events.jsonl`（93MB/124,974 行），与 `gate_chain.jsonl` 是两条链。

# 五、已完成的任务清单（✅ 有证据）

| 任务 | 状态 | 证据路径 |
|---|---|---|
| 机构级架构尽调 | ✅ | `docs\_working\archive\2026-09\c_class_scattered\2026-09-18-institutional-architecture-review.md` |
| 全量问题清单 54 条 | ✅ | `docs\_working\archive\2026-09\c_class_scattered\2026-09-18-issue-inventory-full.md` |
| 交接指令 v1 | ✅ | `docs\_working\archive\2026-09\2026-09-18-HANDOFF-PROMPT.md` |
| **T1 复权链修复** | ✅ | `src\zephyr\backtest\core\data_handler.py:279,396,430`（registry 真源表名 + adj_factor 列 + `compute_qfq_close`） |
| **T3 订单幂等落库** | ✅ | `src\zephyr\ex_core\adapters\miniqmt_broker.py:71-74,96,260-265`（`SQLiteIdempotencyStore`，注释明写"R-L3（尽调 C1）：内存映射降级为快路径缓存，权威去重状态落库"） |
| 挖矿 SOP 复调（推翻 3 条误判） | ✅ | `docs\_working\2026-10-14-mining-sop-reinvestigation.md` |
| 本次总交接包 | ✅ | `docs\_working\2026-10-14-HANDOFF-MASTER-PROMPT.md`（本文件） |

# 六、剩余任务清单（按优先级）

### ◐ 部分完成，需收尾（5 项）

| # | 任务 | 现状 | 主战场（完整路径） |
|---|---|---|---|
| T2 | ETF 分钟时区修复 | dry_run 已非默认 True，但**无验收报告** | `D:\ZephyrAlpha\scripts\ch\repair_etf_minute_tz_split.py` |
| T4 | CI 真跑测试 | nightly 已 `pytest --cov-fail-under=70 -n 4`；残留 `--collect-only` 与 2 处 `continue-on-error:true` | `D:\ZephyrAlpha\.github\workflows\governance.yml`（:108、:124-127、:274、:350） |
| T5 | WF 主链接 CPCV + 固种 | 模块有、主链未接 | 零件：`D:\ZephyrAlpha\src\zephyr\backtest\core\cpcv.py`；主链：`D:\ZephyrAlpha\src\zephyr\backtest\core\walk_forward.py`（:23「CPCV v2 配置预留 P1-18」、:281 `default_rng()` 无种子）；固种范例：`D:\ZephyrAlpha\src\zephyr\backtest\regime_validation\e2_stationary_bootstrap.py:75,170`（`seed: int = 42`） |
| T6 | 因子三重门真校验 | 注册表达 v2.1，但**门仍恒真** | `D:\ZephyrAlpha\src\zephyr\factor\factor_factory.py:218-220`（`lambda c: True`）；`D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\factor_registry.yaml` |
| T7 | 门禁结果入 gate_chain | hash 链机制完备，真实门禁未入链 | 机制：`D:\ZephyrAlpha\src\zephyr\gov_enforcement\rule_enforcement\audit_chain_verifier.py`（:8、:23、:108）；G0 链：`D:\ZephyrAlpha\data\audit_trail\gate_chain.jsonl`（167 行全 G0）；真实事件：`D:\ZephyrAlpha\data\audit_trail\events.jsonl`（124,974 行） |

### ❌ 未完成（4 项）

| # | 任务 | 现状 | 主战场（完整路径） |
|---|---|---|---|
| T8 | worktree 清理 | **反向恶化** 42 → 54 | `D:\ZephyrAlpha\.aidrafts\`（23）、`D:\ZephyrAlpha\.worktrees\`（20）。销毁前 Max 逐目录裁定有无未合并成果 |
| T9 | 实盘/一年 paper | **无任何证据** | `D:\ZephyrAlpha\scripts\start_paper_session.py:119`（只读 `QMT_SIM_*`） |
| T10 | CH/Redis 拆分 + 副本灾备 | Redis 与 CH 仍同机 172.24.30.100 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\infrastructure_registry.yaml`（INFRA-DB-007） |
| T11 | pre-trade 规则补全 + 探针接线 | `probe is None` fail-open；无行业集中度/换手/黑名单/流动性 | `D:\ZephyrAlpha\src\zephyr\ex_core\pre_execution_checker.py:181`；`D:\ZephyrAlpha\src\zephyr\risk\core\risk_veto_engine.py:320` |

### 卫生问题（非任务但极严重）

- **`D:\ZephyrAlpha\.runtime\tmp` 堆积 802,844 个文件**，绝大多数是死会话 runlane 遗物（`st-deadcure2-20261009\runlane_3\data\failures` 15,580、`backfix_reset_recovery\blobs` 2,862、`...\red_blue\trigger_queue` 2,826、`test_guard` 2,524）。**只清死会话遗物，不要碰活跃会话。**

# 七、待 Owner 裁定清单（实测，2026-10-14）

| 台账 | 状态分布 | 路径 |
|---|---|---|
| 裁定登记 | **decided 13**（已裁定待落地）/ active 320 / superseded 4 / void 2 / draft 1 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ruling_registry.yaml`（4,828 行） |
| 架构议题 | **open 75 + proposed 54 + in_progress 18** = 147 条未闭合；decided 324 / resolved 282 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\architecture_issue_registry.yaml`（10,307 行） |

> 按宪法 §5，**proposed = AI 提议待 Owner 确认**（54 条即 Owner 门位）。

历史会话点名未裁（10-02/10-03 日志在册）：
1. R2-F1 判死闸本体 `session_concurrency.py` 未落地
2. R2-F5 接管门禁命中面全为 0（"在执法但咬不到真目标"）
3. `git worktree prune` 清孤儿登记项
4. abs→rel 路径失配第 3/4 次复发（有裁定#461 授权却两度进死信）
5. sweeper 迁移感知方案
6. doctor 通道三道铁闸

# 八、54 条问题索引（P0 全列；P1/P2 见清单文件）

**P0（17 条）**
- A1 回测不乘复权因子 → `src\zephyr\backtest\core\data_handler.py:335`（**已随 T1 修复，需复验**）
- A2 默认表名 `daily_kline` 写错（真源 `kline_daily`）→ 同上（**已随 T1 修复**）
- A3 `adj_factor` 965 万行恒为 1 → `src\zephyr\data\providers\akshare_provider.py:236`
- A4 ETF 分钟 4.12 亿行时区误标 → `scripts\ch\repair_etf_minute_tz_split.py`
- B1 回测台账 43 节点 pending 41/valid 2 → `c1_backtest.node_verdict`
- B2 样本外仅 4 个交易日 → `docs\_working\2026-09-17-node-verdict-triage.md`
- B3 Walk-Forward 无 embargo → `src\zephyr\backtest\core\walk_forward.py`（**模块已有 cpcv.py，主链未接**）
- B4 随机种子不固定 → `walk_forward.py:281`（**见 T5**）
- C1 幂等未持久化 → `miniqmt_broker.py` + `ex_core\order_manager.py`（**✅ 已修复，需复验**）
- C2 无实盘入口 → `scripts\start_paper_session.py:119`
- C3 熔断探针未接线即放行 → `ex_core\pre_execution_checker.py:181`
- D1 161 条策略 production 全 0 → `_registry\catalogs\strategy_registry.yaml`
- D2 175 条因子多数无 IC/无 code_path → `_registry\catalogs\factor_registry.yaml`
- D3 真正实现的因子仅 4 个类 → `src\zephyr\factor\`
- D4 因子三重门恒真 → `factor\factor_factory.py:218-220`
- E1 审计链全 G0 冒烟 → `data\audit_trail\gate_chain.jsonl`（**部分修正，见 T7**）
- E2 reconciler 违规 auto_commit 自动放行 → `.runtime\logs\reconcile_worker_*.log`
- E3 CI 只 `--collect-only` → `.github\workflows\governance.yml`（**部分修正，见 T4**）
- E4 AI 自证闭环无人类签字位 → `AGENTS.md` §5

**P1（21 条）/ P2（16 条）**：完整表格见
`D:\ZephyrAlpha\docs\_working\archive\2026-09\c_class_scattered\2026-09-18-issue-inventory-full.md`

# 九、项目硬约束（违反会造成实际损失）

- 提交一律走 `D:\ZephyrAlpha\scripts\git_commit.py`，**禁止裸 `git commit`**
- 热文件（注册表/宪法/tracker）写入必须用 `safe_write_text`（`src\zephyr\shared\io\file_utils.py`）防并发覆盖
- 数据库一律走 `DatabaseService`（`zephyr.infrastructure.database_service`），禁裸 `duckdb.connect`
- 密钥走 `zephyr.security.secrets`，禁裸 `os.getenv`
- 破坏性 DB 操作三步验证（必要性/真实性/可逆性）
- 临时脚本与输出放 `D:\ZephyrAlpha\.runtime\tmp\`；**成果必须 promote 到 `docs\_working\` 才算交付**；项目根目录零临时文件
- **当前工作区有 655 个未提交项（其中约 400 个是 10-14 当天改动），有活跃会话在飞——严禁代提交、严禁清理他人改动**（owner 责任制 + 禁连坐）

# 十、禁止事项

1. 未完成调查核验前，禁止下"XX 已完成/未完成"的结论
2. 禁止用单文件 grep 做状态断言（见第四节）
3. 禁止为通过验收放宽断言或降级阈值（历史教训：把断言改成 `>= 0.0`）
4. 未经 Max 裁定不得删除数据或销毁目录
5. 不得绕过 `git_commit.py`，不得伪造 `[GW:]` 标记
6. 不得用口头"Owner 说"当门禁豁免

# 十一、开工第一步（本轮定位=调查，不是施工）

1. 读完第二节的 10 个必读文件
2. **复验**第五节两项"已完成"（T1 复权链、T3 幂等落库）——用三源正查 + 读代码，确认它们真的成立
3. **复扫**第六节 9 项剩余任务的当前状态（项目迭代快，27 天内状态可能又变了）
4. 输出一份《现状核验表》：每项给 `✅/◐/❌` + **证据指针（文件:行号 或 命令输出）**，无指针的结论标注"未核实"
5. 再向 Owner 报告，等裁定后再施工。**本轮不要动任何 src/ 代码。**

<<<END>>>
