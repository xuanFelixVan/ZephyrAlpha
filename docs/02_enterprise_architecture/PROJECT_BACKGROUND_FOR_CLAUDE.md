# ZephyrAlpha 项目背景介绍（致 Claude）

> 本文档面向 Claude 分析，目的是让对方在缺乏项目上下文的情况下，快速理解 ZephyrAlpha 是什么、为什么这么做、当前在哪、要去哪。
> 文档基于项目真实文件、规则、架构裁定撰写，所有引用均可溯源。

---

## 一、一句话定位

ZephyrAlpha 是一套**100% AI 开发模式**下的**专业级 A 股量化交易系统**，Python 3.12+，版本 v2.0.0。资产规模见 depgraph（PostgreSQL）+ 各注册表动态统计（模块数 / 域数 / 节点数均为时点值，见各真源动态统计）。

它不是传统意义上的"量化策略库"，而是一个**自治理的 AI 量化操作系统**——用治理代码（门禁、注册表、reconciler、worktree 隔离）替代人类工程师的纪律，让 AI 能在缺乏人类监督的情况下持续演进一个金融级系统而不漂移。

---

## 二、为什么会有这个项目：核心矛盾与设计哲学

### 2.1 核心矛盾

传统量化系统假设**人类工程师**是主要开发者：人写代码、人 review、人决定架构演进、人保证一致性。

ZephyrAlpha 的假设完全相反：

- **开发者主体是 AI**（Trae IDE 对话触发，Ollama 本地推理 + DeepSeek/Claude API 复杂分析）
- **AI 上下文有限**（每次对话能看到的代码/规则有限，跨对话记忆弱）
- **AI 会幻觉**（凭记忆推断依赖关系、凭直觉编造路径、凭习惯写硬编码）
- **AI 会漂移**（同一逻辑在多个文件里写出不同实现，时间一长多真源并存）

如果用传统"轻治理 + 重人治"的方式，AI 在 4000+ 模块的项目里**必然漂移成不可维护的垃圾场**。

### 2.2 解法：用机器可执行的治理替代人类纪律

项目的核心设计哲学浓缩在两条顶层规则里：

#### 规则一：trae_057 — AI 消费优先原则

> "本原则是项目 100% AI 开发模式的顶层设计约束。所有项目产出物 MUST 以 AI 可发现、可解析、可执行为第一优先级。人类可读性是约束条件，不是优化目标。"

格式分工铁律：
- 规则/元数据 = YAML（机器可解析）
- 叙事/蓝图 = Markdown（人类可读）
- 代码 = 十五字段头部（自动抽取）
- 数据交换 = JSON

三性要求：可发现（Discoverable）/ 可解析（Parsable）/ 可执行（Executable）。

#### 规则二：trae_060 — 向内收敛约束

> "100% AI 开发、上下文有限、靠 trae 对话触发工作的自治理项目的顶层收敛约束。"

三原则：

| 原则 | 一句话 | 违反后果 |
|------|--------|---------|
| ① 能现成不创造 | 动手前先 Grep / 搜注册表 / 查 CapabilityLookup；能扩展不新建；禁止同步复制 | 造第二真源 → 漂移 |
| ② 创造必全自动 | 永久脚本必须事件驱动 + 自动运行 + 自动维护 + 自动关闭；禁止手工触发，禁止时间触发 | 必然被遗忘 → 漂移 |
| ③ 第一性原理治本 | 先问元问题该不该存在 / 能否删除或合并；治本不治标 | 症状反复 |

### 2.3 四条安全红线（不可撤销）

- **R1 键盘不录 key**：API Key / Secret 永不通过键盘输入
- **R2 日志不写 secret**：任何日志/异常/审计记录禁止出现敏感字段
- **R3 金融不盲信任 AI**：金融决策必须有可验证的护栏，AI 输出不直接执行交易
- **R4 PRD 永远不改**：产品需求文档一旦定稿冻结，禁止回写

### 2.4 开源优先

技术选型遵循"开源优先"原则。架构原则详见 [architecture_principles.md](../../docs/02_enterprise_architecture/04_architecture_principles_decisions/architecture_principles.md)（v1.3.0，2026-07-06 已删除 BvB 五维评分法附录及 5 条硬约束——BvB 从未落地，5 条硬约束为孤岛概念）。

---

## 三、项目的治理体系：机器可执行的纪律

这是 ZephyrAlpha 最独特的部分——**它把传统软件工程里靠人盯的纪律，全部写成了代码和门禁**。

### 3.1 真源唯一（SSoT）原则

项目核心约束：**文件必须责任唯一、真源唯一，禁止多真源同步**。每个真源对应一个 canonical 文件，其他位置只能引用不能复制。

#### 六大真源

| 真源 | 文件/系统 | 用途 |
|------|----------|------|
| 规则数据 | YAML 文件（trae_XXX 规则，条数见规则目录动态统计） | DB 规则表只读缓存，`sync_yaml_to_depgraph.py` 单向同步 |
| 跨层契约 | `cross_layer_contracts.yaml`（CTR-XXX，条数见契约文件动态统计） | codegen 生成 Python dataclass，禁止手改 |
| 能力反查 | `capability_canonical_file_registry.yaml`（能力条数见注册表动态统计） | 新 AI 通过 capability_id 反查 canonical 文件，避免重复造轮子 |
| 蓝图 | `blueprint_registry.yaml`（蓝图数见注册表动态统计） | 从 `blueprint.md` frontmatter 自动同步，已替代 `module_registry.yaml` |
| 任务系统 | TaskRepository（SQLite） | 10 状态机，L3 铁律禁止读 MD 做决策 |
| 架构全景图 | depgraph（PostgreSQL 16，表数见 schema 动态统计） | 依赖 + 路径全景图唯一真源，禁止裸连 |

#### SSoT 门禁

- `ssot_redefinition_gate`（priority=65）：硬阻断文件内重新定义已 SSoT 化的常量
- 蓝图间引用必须用 module_id 而非路径字符串，建立反向引用索引
- 模块迁移时自动触发更新所有引用

### 3.2 depgraph — 架构全景图真源

PostgreSQL `localhost:5432/depgraph`，存储 nodes / edges / domains / contracts / rule_bindings / arch_constraints 等（表数见 schema 动态统计）。

- **运营态**：节点数见 depgraph 动态统计（代码现状真实依赖快照）
- **设计态**：节点数见 depgraph 动态统计（planned，尚未施工）
- **schema 版本**：见 depgraph schema 动态统计

两条铁律（2026-07-02 治本规则）：

- **L1 依赖关系先行铁律**：任何模块施工前（写第 1 行业务代码前），MUST 先通过 `apply_depgraph.py` 将该模块的依赖关系登记到 depgraph 设计态（status=planned）。禁止"先施工后补登记"或"施工中临时编造依赖"。
- **L2 设计态基于最新运营态铁律**：写入设计态前 MUST 确保运营态已就绪，否则在过期快照上设计 = 幻觉温床。

修改 depgraph 必须用 `apply_depgraph.py`，禁止直接改数据库；改前必须 `git commit` 备份。

### 3.3 GitCommitGateway — 全项目唯一合法 git commit 入口

[git_commit_gateway.py](../../src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)：

- **全局跨进程串行锁**：`.ailocks/git_commit_global.lock`，TTL=1800s
- **门禁注册制 CommitGateRegistry**：commit_gates 数量见注册表动态统计（arch_reference / bare_getenv / capability_overlap / claim_required / create_guard / dangling_reference / directory_contract / doc_ref_broken / empty_handler / file_copy / function_dup / held_overlap / id_uniqueness / module_id_consistency / orphan_module / perm_trigger / r5_digit_suffix / rule_four_way_alignment / session_required / ssot_redefinition / ttl / vocab_hardcode 等）
- 禁止裸 `git commit`，所有提交必须通过 GitCommitGateway

关键门禁举例：
- **ARCH-REFERENCE**（priority=75）：检测 `#ARCH-NNN` 引用是否在 registry 登记，未登记硬阻断，`--no-verify` 无法绕过
- **FILE-COPY**（priority=85）：AST 归一化后 >70% 相似度硬阻断文件复制
- **FUNCTION-DUP**（priority=90）：重复函数硬阻断
- **ORPHAN-MODULE**（priority=86）：孤儿模块死代码硬阻断
- **VOCAB-HARDCODE**（priority=80）：词表硬编码硬阻断
- **TTL-METADATA**（priority=32）：fail-closed 模式，frontmatter 元数据缺失硬阻断

### 3.4 session_worktree — 并发 AI 物理隔离

41 个并发丢失案例分析结论：
- Mode A（git stash/reset/checkout 冲掉工作区）占 51%
- Mode B（直接编辑同一文件覆盖）占 17%
- Mode D（未 commit 被回收）占 7%

唯一能同时治 A+B+D 的方案是 **git worktree 物理隔离**。每 AI 对话独占 `.aidrafts/{session_id}/` worktree，独立 git index 物理隔离消除搭便车提交（共享 index 下后提交者把别人 staged 改动一并提交）。

君子协定（Trae IDE 不可 hook，依赖 AI 自觉）：
- AI 对话启动后第一件事执行 `session_worktree_start(sid)`
- 提交时执行 `session_worktree_commit(sid, files, message)`
- 完成调 `session_worktree_merge(sid)`，放弃调 `session_worktree_abort(sid, files=...)`

### 3.5 CapabilityLookup — 能力反查引擎

[capability_lookup.py](../../src/zephyr/governance/capability_lookup.py)，被 76+ 消费者使用。能力 → 真源文件反查（条数见注册表动态统计）。

新 AI 通过 capability 反查可发现正确入口，避免重复造轮子。这是"能现成不创造"原则的运行时落地。

### 3.6 reconciler + gate + 词表（见各注册表动态统计）

> "ZephyrAlpha 项目治理体系设计严谨（trae_060 三原则 + reconciler + gate + 词表 + CapabilityLookup 反查机制），但执行覆盖存在系统性断层。"精确数量见各注册表动态统计。

治理军备竞赛反思（#ARCH-028 / AD-GOV-001）：治理收敛 49 门禁 → 29，17 reconciler → 11（历史值，见 #ARCH-028 裁定记录）。这反映 100% AI 开发模式的内在张力——治理过严增加 AI 上下文负担，治理过松导致漂移。

### 3.7 三层 AI 工作分配

- **L1 Trae（人在环）**：主开发对话，规则注入 + 工具调用
- **L2 Local（Ollama BGE-M3 + qwen3:8b）**：本地向量检索 + 推理
- **L3 API（DeepSeek / Claude）**：复杂分析 + 代码生成

### 3.8 Vibe Coding 2.0 基础设施（5 大核心服务）

- **LSG**（Lifecycle State Governance）生命周期状态治理
- **CE**（Contract Engine）契约引擎
- **Orc**（Orchestrator）编排器
- **VMS**（Vector Memory Service）向量记忆服务
- **FLE**（Feedback Loop Engine）反馈闭环引擎

AutoRuntime Core 是系统大脑，孤儿率 = 未接入模块数 / 总模块数 → 目标 0%。

---

## 四、架构原则：域平级

### 4.1 域唯一物理分类

核心架构决策：**所有域是唯一物理分类**（域数见 depgraph 动态统计）。原 14 层（L00-L13）降级为域的 `layer_id` 属性，消除"域分层 + 物理路径分层"的双分类幻觉。

> "所有域平级，无父子关系；新增域只需 INSERT 到 domains 表，不修改生成器"
> "架构与功能域层级保持一致：功能域平级 → 物理路径平级；能平铺绝不嵌套，每多一层嵌套增加 AI 理解成本"

`layer` 字段定义的是**逻辑分层**（如 `infra_ops = L01`），不是物理路径前缀。物理路径统一为 `src/zephyr/{domain}/`。

域分布（按 layer_id 分组，各组域数见 depgraph domains 表动态统计）：
- L0_infrastructure
- L1_foundation
- L2_domain
- unassigned

### 4.2 容量治理二元规则

**ARCH-CAP-002 v1.0.8**：单域 production_nodes ≤150 通过，>150 必须拆分，无例外。

文件夹平铺容量阈值：T_hard=60（无稳定命名前缀）/ T_soft=120（有前缀）/ >120 必须拆分。线性增长无封顶型文件夹直接判拆。

### 4.3 三大方法论合成

- **ISO 42010**：定方法论——Architecture Description 由多个 View 组成
- **TOGAF**：定四层视图——Business / Information / Application / Technology
- **C4 Model**：定应用视图的可视化——系统上下文（L1）和容器（L2）

### 4.4 运行时三平面 + 治理三层

- **运行时三平面**：Hot（控制面，<10ms）/ Warm（数据面，10ms-1s）/ Cold（质量面，>1s）——按延迟预算切分
- **治理三层**：Policy（强约束，编译期）/ Factory（中约束，构建期）/ Runtime（弱约束，运行期）——按生命周期切分

---

## 五、技术栈

### 5.1 语言与核心依赖

- **Python 3.12+**（统一 py312，避免 3.11 SyntaxError）
- **Pydantic V2**（>=2.0.0,<3.0.0）—— 数据建模
- **pandas + pyarrow** —— 数据处理
- **structlog** —— 结构化日志
- **panel + holoviews + plotly + plotly_resampler + lightweight-charts v5.2** —— 可视化（G0.5 Python 过渡层，ARCH-047 裁定，已从 Streamlit 切换）
- **openai + sentence-transformers + mcp** —— LLM/AI
- **pyyaml + python-dotenv** —— 配置

### 5.2 五库分工（DatabaseService 统一访问）

| infra_id | 数据库 | 用途 | 表数 |
|---|---|---|---|
| INFRA-DB-001 | SQLite governance.db | 治理运行时——TaskCard/事件/门禁/断路器/FLE 指标 | 15+ |
| INFRA-DB-002 | ChromaDB | 向量检索与 KMS 语义检索（8 Collection，BGE-M3 + bge-small-zh） | — |
| INFRA-DB-003 | PostgreSQL 16 depgraph | 架构静态真源——nodes/edges/domains 等（表数见 schema 动态统计） | 见 schema |
| INFRA-DB-004 | DuckDB（内存 `:memory:`） | OLAP 分析——只读挂载 governance.db 执行聚合，输出 Parquet | — |
| INFRA-DB-006 | ClickHouse 26.6.1 c1_market | 业务行情仓库——日线/分钟线/Tick/5 档盘口/可转债隐含波动率 | — |

约束：
- 禁止裸 `duckdb.connect(market.duckdb)`，必须通过 DatabaseService
- 必须通过 DatabaseService 访问 ClickHouse，禁止直接连接
- 业务数据库连接必须显式指定 `read_only=True`
- 原 INFRA-DB-005 market.duckdb 已于 2026-07-01 废弃，由 ClickHouse 替代

### 5.3 16 项技术决策（DD-1 至 DD-16）

完整技术决策清单见 [tech_stack_manifest.yaml](../../config/tech_stack_manifest.yaml)。典型决策：

- DD-2：审计 Provenance 存储 = SQLite + hash 链（只追加 + 完整性校验，零运维）
- DD-6：类型校验 = mypy + import-linter（本地 + CI 双保险）
- DD-8：静态扫描 = ruff + bandit（取代 pylint，速度快 100×）
- DD-9：契约总线迁移 = 分三批 15+15+14（控制回归风险）
- DD-16：语义缓存 = ChromaDB 向量相似度（复用 VMS 基础设施）

### 5.4 代码质量工具链

- **ruff**（lint + format，target-version="py312"，line-length=120）
- **mypy**（python_version="3.12"）
- **pytest + pytest-asyncio + pytest-cov**（fail_under=70）
- **pre-commit**
- **importlinter**（导入依赖检查）
- **CI**：GitHub Actions（governance.yml + dedup-test.yml，windows-latest）

---

## 六、回测子系统（重点）

回测是 ZephyrAlpha 当前重点施工的子系统，也是可视化方案的直接服务对象。

### 6.1 域定位

> "D_BACKTEST 域是 ZephyrAlpha 量化系统的策略验证引擎"
> "架构决策：回测引擎统一归口 D_BACKTEST，消除 research/intelligence/rollback 多处置放"

代码唯一存放于 [src/zephyr/backtest/](../../src/zephyr/backtest/)。

### 6.2 双模式架构

| 引擎 | 文件 | 推进单位 | 适用场景 |
|------|------|---------|---------|
| `DefaultBacktestEngine`（向量化） | [vectorized_engine.py](../../src/zephyr/backtest/implementations/vectorized_engine.py) | 日 bar | 快速筛选因子 IC/IR |
| `EventDrivenEngine`（事件驱动） | [event_driven_engine.py](../../src/zephyr/backtest/implementations/event_driven_engine.py) | Tick | 精确验证策略 PnL，做 T 专用 |

### 6.3 BacktestResult — CTR-P1-016 frozen dataclass 契约

[engine_base.py](../../src/zephyr/backtest/core/engine_base.py) 中的 `@dataclass(frozen=True) BacktestResult`，由 codegen 从 `cross_layer_contracts.yaml` 自动生成。

11 个必填字段 + 4 个可选字段：

| # | 字段 | 类型 | 含义 |
|---|------|------|------|
| 1 | strategy_id | str | 策略 ID |
| 2 | total_return | float | 累计收益率 |
| 3 | annual_return | float | 年化收益率 |
| 4 | sharpe_ratio | float | Sharpe 比率 |
| 5 | max_drawdown | float | 最大回撤 |
| 6 | trades_count | int | 总交易笔数 |
| 7 | win_rate | float | 胜率（0.0-1.0） |
| 8 | start_date | datetime | 回测开始时间 |
| 9 | end_date | datetime | 回测结束时间 |
| 10 | overfitting_flag | bool | 过拟合标志 |
| 11 | idempotency_key | str | 幂等键（唯一标识本次回测） |
| 12 | timestamp | datetime | 回测产出时间戳 |
| 13 | benchmark_symbol | Optional[str] | 基准标的代码 |
| 14 | schema_version | str | 契约版本（默认 "1.0"） |
| 15 | trace_context | Optional[TraceContext] | 链路追踪上下文 |

关键缺口（可视化需补全）：BacktestResult **不含**净值曲线、回撤曲线、trades 明细、持仓、sortino/dsr/adjusted_sharpe 等派生指标——这些在引擎内部生成后被聚合成 11 个标量字段后丢弃。

### 6.4 PIT 铁律（零前瞻偏差）

[pit_manager.py](../../src/zephyr/backtest/core/pit_manager.py)，**PIT 三公理**：

1. **时点标记**：`event_time` / `available_at`
2. **版本对齐**：禁用后续修正数据
3. **泄漏防护**：query_time T 不得返回 event_time > T 的数据

关键参数：`DEFAULT_EMBARGO_DAYS=5` / `DEFAULT_CONSISTENCY_THRESHOLD=0.01`

回测引擎必须遵循 PIT 铁律：零前瞻偏差 / 幸存者偏差零容忍 / PIT 三平面一致性 / PIT 隔离 / PIT 三公理 + Embargo 期 + `pit_consistency_test()` CI/CD。

### 6.5 Walk-Forward 三模式

[walk_forward.py](../../src/zephyr/backtest/core/walk_forward.py)：

| 模式 | 适用场景 | 训练窗口策略 |
|------|---------|------------|
| rolling | 短周期/非平稳策略 | 固定训练窗口滑动 |
| anchored | 中周期 | 训练集从起点按 step 扩展 |
| expanding | 长周期/稳健 | 训练集逐步吸收测试数据增长 |

- **White's Reality Check**：多重比较偏差校正，`WRC_SIGNIFICANCE_LEVEL=0.05`
- **CPCV v2**：配置预留
- **PIT 铁律**：训练集严禁包含测试集数据，`train_end <= test_start`

### 6.6 过拟合检测三维度 + 三层

[overfitting_detector.py](../../src/zephyr/backtest/core/overfitting_detector.py)：

**三维度**：
1. Walk-Forward 稳定性（`WF_POSITIVE_RATIO_THRESHOLD=0.60` / `WF_CV_THRESHOLD=1.50` / `WF_DISASTER_SHARPE=-0.50`）
2. 参数敏感性（`PARAM_MAX_CHANGE_THRESHOLD=0.30`）
3. 泛化能力

**三层**：
- SIM-18：研究时手动
- SIM-38：样本内外对比
- SIM-56：上线前自动门禁

**P0-9 否决阈值**：样本外 Sharpe < 70% 样本内 Sharpe → 否决上线。

### 6.7 DecisionGate — 3 阶段决策门控

[decision_gate.py](../../src/zephyr/backtest/core/decision_gate.py)，**3 阶段不可跳级**：

1. **IS（In-Sample）**：样本内回测 → 参数优化 → 稳定性门控（`is_sharpe_threshold=0.5`）
2. **WFA（Walk-Forward Analysis）**：滚动窗口样本外验证（`wfa_majority_pct=0.5`）
3. **OOS（Out-of-Sample）**：最终样本外验证，进入后参数锁定（`oos_sharpe_ratio_threshold=0.7`）

回测-实盘偏差监控：`backtest_live_deviation_warn=0.30`（>30% 告警）/ `backtest_live_deviation_retire=0.50`（>50% 退役）。

### 6.8 回测=实盘一致性（B 方案：MatchingLogic 共享）

> "顶级机构同一份代码方案需'团队+C++低延迟+SimBroker+SRE'四件套，xttrader 非线程安全同步阻塞强行统一回测慢 3-10 倍，A 股硬校验反向污染回测逻辑；完全分离方案是偏差 >30% 告警根源；B 方案消除 >80% 偏差源且保留优化空间，为个人开发者最优解"

两个引擎共用 `MatchingLogic` 模块（[matching_logic.py](../../src/zephyr/backtest/core/matching_logic.py)），撮合规则与 D_EX_CORE 的 MiniQMT Broker 保持一致。

升级触发条件（3 信号同时出现）：① MatchingLogic 共享后偏差仍 >5% 且定位不到 ② 策略迭代速度成瓶颈 ③ 有模拟实盘环境需求。升级路径为加 ReplayMode 不推翻架构，v2.3+ 考虑。

### 6.9 回测指标修正要求

- 必须包含 **Sharpe 修正**（中国 10 年期国债无风险利率 / 样本量 < 60 不计算 / DSR）
- 必须包含 **DSR 多重测试偏差修正**（Deflated Sharpe Ratio）

### 6.10 事件系列

- **E-BT-01 BacktestCompleted** → D_PORTFOLIO_CORE / D_RISK / D_REPORTING / D_FRONTEND
- **E-BT-02 BacktestPassed** → D_PORTFOLIO_CORE / D_FRONTEND（触发 E-PF-01）
- **E-BT-03 OverfittingDetected** → D_FACTOR（因子衰减）/ D_FRONTEND

### 6.11 当前施工状态

回测域 Phase 1+2 模块状态（production / prototype 节点数及模块清单见 depgraph 动态统计）：

测试覆盖情况（ARCH-MM-001裁定：以 depgraph nodes.design_maturity 为真源，[MATURITY] 标记为声明）：
- 有正式测试覆盖（tests/ 目录，depgraph 推导为 production）：matching_engine、matching_logic、portfolio、tick_replay、data_handler、event_driven_engine、engine_base、vectorized_engine、decisiongraph_adapter
- 无正式测试覆盖（depgraph 推导为 prototype）：decision_gate、metrics、overfitting_detector、pit_manager、walk_forward、backtest_result_sink、result_repository

---

## 七、前端与可视化现状

### 7.1 当前状态（G0.5 Python 过渡层，ARCH-047 裁定）

[src/zephyr/frontend/](../../src/zephyr/frontend/) 已部署 Panel dashboard（G0.5 Python 过渡层，ARCH-047 v1.2.0，2026-07-04 DONE）：

- [app_panel.py](../../src/zephyr/frontend/dashboard/app_panel.py)：Panel 应用（Tab 清单见源码：任务进度/知识库/门禁/Fitness/OLAP + 交易/回测组件）
- [components/](../../src/zephyr/frontend/dashboard/components/)：组件清单见目录（backtest_results / tick_replay / order_book / position_monitor / trade_panel / fitness_functions / gate_statistics / knowledge_overview / olap_trend / task_progress）
- [chart_factory.py](../../src/zephyr/frontend/dashboard/components/chart_factory.py)：ChartFactory 统一工厂（make_equity / make_drawdown / make_heatmap / make_tick / make_kline）

技术栈：Panel + HoloViz（HoloViews + Datashader + hvPlot）+ Plotly + plotly_resampler + TradingView Lightweight Charts v5.2。已从 Streamlit 切换（旧 app.py 保留为迁移参考）。

### 7.2 长期前端终局

[frontend_architecture.md](../../docs/02_enterprise_architecture/target_architecture/frontend_architecture.md)（v1.2.0，含 G0.5 过渡层章节）定义了 7 条前端铁律：

- **FE-P1**：技术栈异构隔离（React/TS 与 Python 物理隔离）
- **FE-P2**：API Gateway 唯一对接（FastAPI `api_gateway/`）
- **FE-P3**：契约先行（OpenAPI 3.1 + WebSocket Topic）
- **FE-P4**：微前端边界（Module Federation）
- **FE-P5**：设计系统单一真源
- **FE-P6**：可观测性内建
- **FE-P7**：渐进激活

7 档激活触发器（G0→G6）：
- 当前在 **G0**（无前端，CLI + Cursor + Feishu Bot 承担 Day-1 UI）
- **G1**（最小 dashboard）：触发条件"外部干系人看报表 ≥ 2 周/次"
- **G2**（2-3 App 平台）：G1 稳定 ≥ 1 个月 + 第 2 个 App 业务需求成熟
- **G3+**：团队级、AI Operator、外部租户

### 7.3 可视化方案选型争议（当前正在做）

用户要求"考虑长期部署，不光是回测要可视化，还有其他相关工作嫁接集成"。经第一性原理调研，得出推荐：

**Panel + HoloViz（HoloViews + Datashader + hvPlot + Bokeh）+ Plotly + plotly_resampler + TradingView Lightweight Charts v5.2**

理由（相对 Streamlit 的决定性优势）：
1. **crossfiltering**：Streamlit 图表只能做 output 不能做 input，Panel 原生支持双向交互（框选 K 线 → 联动交易明细）
2. **百万级 tick 渲染**：Panel + Datashader 服务端聚合，100 万点 0.5-1 秒；Streamlit 传全量数据到浏览器卡顿
3. **原生 WebSocket 推送**：Panel + Bokeh server 原生支持；Streamlit "10+ 并发流式连接是架构性禁区"
4. **金融原生**：HoloViz 官方 Portfolio Optimizer 示例 + `df.hvplot.ohlc()` 一行出 K 线
5. **与终局架构一致**：Panel 响应式模型 + server 模式与 React + FastAPI 状态管理 + API 网关架构同构

Trade-off：Panel AI 代码生成友好度低于 Streamlit（训练数据少），但 hvPlot 的 pandas-like API 可缓解。

---

## 八、项目演进历程与当前状态

### 8.1 当前阶段

- **阶段**：experimental
- **域总数**：见 depgraph domains 表动态统计
- **节点**：见 depgraph 动态统计（按 design / prototype / production 状态分组）
- **依赖边**：见 depgraph 动态统计

### 8.2 ARCH 编号体系

[architecture_issue_registry.yaml](../../docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)（REG-ARCH-ISSUE-001）：

- 连续分配、不回收、`superseded_by` 链、status 四值（active / superseded / resolved / deprecated）
- 已登记 #ARCH-001 到 #ARCH-051+（连续分配，不回收）

关键裁定：
- **#ARCH-028**：治理军备竞赛陷阱（49 门禁 → 29，17 reconciler → 11）
- **#ARCH-029**：tests/ 目录治理（1699 根平铺文件迁移）
- **#ARCH-037**：规则文件命名约定（`trae_NNN_<主题>_<描述>.yaml`）
- **#ARCH-044**：5-Why 根因分析，P0 已完成，P1/P2 待施工

### 8.3 治理军备竞赛反思

[architecture_debt_registry.md](../../docs/02_enterprise_architecture/architecture_debt_registry.md) 执行摘要：

> "31 轮调研去重后违规点总数 3193 个，分布在 177 个维度"

这反映 100% AI 开发模式的内在张力——治理过严增加 AI 上下文负担，治理过松导致漂移。AD-GOV-001 收敛是关键反思。

### 8.4 文档原则

> "文档应遵循'当前真源唯一'原则——正文只含当前信息（当前架构、当前资产、当前规则）；历史记录在 git log（commit message + changelog + ARCH-XXX 5-Why）；墓碑（任何形式）都是负债——完整墓碑、半墓碑（划除标示）、任务卡墓碑（_working 已完成文件）都应清理；_working 语义必须保持——只保留'进行中'的任务卡，已完成即退役"

### 8.5 废弃策略

采用标记 deprecated 而非直接删除，给未来留余地。例如 `session_claim_start` 已废弃，所有调用点迁移至 `session_worktree_start`，`session_claim.py` 标记为 deprecated 但保留 `generate_session_id` 函数。

---

## 九、src/zephyr/ 域结构速览

一级域（数量见 src/zephyr/ 目录结构，按职能分类）：

### 9.1 核心业务域
- **backtest**：回测引擎域（D_BACKTEST）
- **trading**：交易与编排域（含 AutoPilot/Conductor/WorkDAG）
- **risk**：风控域（D_RISK）
- **factor**：因子域（D_FACTOR）
- **pf_core / pf_alloc**：组合核心与配置
- **position**：持仓域
- **research**：研究域
- **reporting**：报告域（TCA/归因）
- **sell_decision**：卖出决策域
- **signal_ashare / signal_fundamental / signal_quality**：三个信号子域

### 9.2 执行与数据域
- **ex_core**：执行核心（broker_interface / execution_engine / order_manager / miniqmt_broker）
- **ex_sor**：Smart Order Routing
- **execution_simulation**：执行模拟
- **market_data / alt_data / data_eng / data_governance / data_security**：数据相关
- **cross_asset / digital_twin / simulation**：跨资产/数字孪生/仿真

### 9.3 治理与基础设施域
- **governance**：治理域（DOM-GOV-001，治理八件套 + kb + code_dedup + commit_gates + persistence 等 20+ 子目录）
- **infrastructure**：基础设施（database_service / MCP server 见 infrastructure 目录）
- **integration**：集成（MCP server 见 integration/mcp 目录 / llm_bridge / mcp_server / ports）
- **security**：安全（access_control / llm_defense）
- **compliance**：合规（aisg_sandbox / artifact_scanner / compliance_manager / evidence_pack / merkle_hourly）

### 9.4 AI 与自治域
- **autonomy_core**：自治核心（context / skills / phase_planner / prompt_registry / spec_engine / trigger_router）
- **autonomy_perm**：自治权限
- **intelligence**：智能（model_profiling）
- **knowledge**：知识
- **ml_train / ml_serve**：ML 训练与服务

### 9.5 共享与前端
- **shared**：共享基础（contracts / events / io / infra / utils / foundation / resilience / protocols / schema 等 22 子目录）
- **frontend**：前端（D_FRONTEND，G0.5 Python 过渡层 Panel dashboard）

---

## 十、项目的独特价值与挑战

### 10.1 独特价值

1. **100% AI 开发模式的工程实践**：把"AI 会幻觉/漂移"作为第一性原理，用机器可执行的治理（门禁/注册表/reconciler/worktree）替代人类纪律，形成可复制的 AI 自治理工程范式
2. **A 股场景的专业级回测**：PIT 铁律 + WFA 三模式 + 过拟合三维度 + IS→WFA→OOS 三级门控 + 回测=实盘一致性（MatchingLogic 共享），达到机构级回测严谨度
3. **depgraph 架构全景图**：PostgreSQL 存储节点 + 依赖边（表数见 schema 动态统计），作为架构静态真源，让 AI 查询零幻觉
4. **SSoT 真源唯一体系**：六大真源各司其职，从机制上消除多真源漂移
5. **域平级架构**：消除双分类幻觉，物理路径与功能域层级一致

### 10.2 当前挑战

1. **治理军备竞赛**：3193 个违规点分布在 177 维度，治理过严增加 AI 上下文负担，过松导致漂移——平衡点是 #ARCH-028 持续探索的
2. **回测副产物未持久化**：BacktestResult 不含净值曲线/trades 明细，仅内存累积，进程结束即丢失
3. **可视化平台已迁移**：已从 Streamlit 迁移到 Panel + HoloViz（ARCH-047 v1.2.0，2026-07-04 DONE），G0.5 Python 过渡层已部署
4. **前端 G0.5→G1 激活**：长期终局是 React + FastAPI，当前 G0.5（Panel 过渡层）已部署，待 3 信号触发 G1 升级
5. **production 节点占比偏低**：大量 prototype 待施工或退役（占比见 depgraph 动态统计，时点值）

---

## 十一、给 Claude 的分析请求

请 Claude 基于以上背景，分析以下问题（任选其一或多）：

1. **治理体系评估**：100% AI 开发模式下的治理体系（门禁 + reconciler + 6 真源 + worktree 隔离，数量见各注册表动态统计）是否过度？哪些可以简化，哪些是刚需？

2. **可视化方案选型**：Panel + HoloViz + Plotly + Lightweight Charts 的组合是否是 ZephyrAlpha 的最优解？有没有更优组合？考虑到 100% AI 开发模式，Panel 的 AI 友好度劣势如何缓解？

3. **回测副产物持久化**：BacktestResult 不含净值曲线/trades 明细，仅内存累积。如何在不违反 CTR-P1-016 frozen dataclass 契约的前提下，设计 BacktestRunArtifact 装配层 + ResultRepository 持久化层？

4. **域架构演进**：当前域数 / 节点数 / 依赖边数（时点值，见 depgraph 动态统计），production 节点占比见 depgraph 动态统计。架构健康度如何？哪些域应该优先施工，哪些应该合并或退役？

5. **G0.5→G1 前端激活路径**：从当前 G0.5（Panel Python 过渡层）到 G1（React 最小 dashboard）到 G2（React + FastAPI），迁移路径如何设计才能让资产不浪费？Panel 组件嵌入 React 的可行性如何？

6. **100% AI 开发模式的可持续性**：这种治理密集型模式长期是否可持续？治理代码本身的维护成本会不会成为新的漂移源？

---

## 附：关键文件索引

### 顶层政策
- [README.md](../../README.md)
- [AGENTS.md](../../AGENTS.md)
- [.trae/rules/project_rules.md](../../.trae/rules/project_rules.md)
- [trae_057_ai_consumer_first.yaml](../../docs/01_policies_and_standards/rules/trae_057_ai_consumer_first.yaml)
- [trae_060_inward_consolidation.yaml](../../docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml)
- [trae_053_automation_dual_track.yaml](../../docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml)

### 架构
- [architecture_principles.md](../../docs/02_enterprise_architecture/04_architecture_principles_decisions/architecture_principles.md)
- [dependency_path_panorama.md](../../docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
- [target_architecture/index.md](../../docs/02_enterprise_architecture/target_architecture/index.md)
- [target_architecture/overview.md](../../docs/02_enterprise_architecture/target_architecture/overview.md)
- [application_architecture.md](../../docs/02_enterprise_architecture/target_architecture/application_architecture.md)
- [frontend_architecture.md](../../docs/02_enterprise_architecture/target_architecture/frontend_architecture.md)
- [architecture_debt_registry.md](../../docs/02_enterprise_architecture/architecture_debt_registry.md)

### 治理代码
- [git_commit_gateway.py](../../src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)
- [session_worktree.py](../../src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)
- [depgraph_schema.py](../../src/zephyr/governance/depgraph_schema.py)
- [capability_lookup.py](../../src/zephyr/governance/capability_lookup.py)
- [task_repo.py](../../src/zephyr/governance/persistence/task_repo.py)
- [commit_gates/](../../src/zephyr/gov_enforcement/commit_gates/)

### 注册表
- [capability_canonical_file_registry.yaml](../../docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)
- [architecture_issue_registry.yaml](../../docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)
- [infrastructure_registry.yaml](../../docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml)
- [blueprint_registry.yaml](../../docs/03_modules/blueprint_registry.yaml)

### 回测子系统
- [_domain_backtest/blueprint.md](../../docs/03_modules/_domain_backtest/blueprint.md)
- [src/zephyr/backtest/](../../src/zephyr/backtest/)
- [engine_base.py](../../src/zephyr/backtest/core/engine_base.py)
- [decision_gate.py](../../src/zephyr/backtest/core/decision_gate.py)
- [overfitting_detector.py](../../src/zephyr/backtest/core/overfitting_detector.py)
- [walk_forward.py](../../src/zephyr/backtest/core/walk_forward.py)
- [pit_manager.py](../../src/zephyr/backtest/core/pit_manager.py)

### 技术栈
- [pyproject.toml](../../pyproject.toml)
- [tech_stack_manifest.yaml](../../config/tech_stack_manifest.yaml)

---

**文档完。** 这份背景介绍覆盖了 ZephyrAlpha 的核心矛盾、设计哲学、治理体系、架构原则、技术栈、回测子系统、前端现状、演进历程和当前挑战，可作为 Claude 分析的完整上下文。
