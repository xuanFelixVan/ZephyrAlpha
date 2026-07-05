# ZephyrAlpha — AI Agent 接入宪法

> **硬规则入口**: [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)（IDE 自动注入，全读完再开工）
> **施工指导**: [`.trae/rules/onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)（详细规则/冷启动序列/方法论索引）
> **内部 Agent 系统**: [`data/capability_cards/`](file:///d:/ZephyrAlpha/data/capability_cards/)（22 个 skill_*.yaml，L0/L1/L2/L3 渐进披露，非 IDE AI 使用）

## RULE-GUARDIAN：第一件事

> **进入本项目的第一个命令（任何平台：Cursor/RooCode/Claude Code/Trae/VS Code）**：
> ```
> python scripts/lock_files.py cleanup && python scripts/ide_health_service.py --status
> ```
> running=false → `python scripts/ide_health_service.py --start`
> running=true → 继续
>
> 守护进程启动 ResourceOptimizationEngine（CPU/内存/进程自动监控+分级防御）+ IdeHealthDaemon（僵尸窗口自动清理）。
> **守护进程未运行 = 禁止任何写操作。**

## RULE-WORKTREE：第二件事（正式规则，2026-07-02 转正）

> **AI 对话启动后 MUST 调**（创建独立 worktree，消除 stash 冲突）：
> ```
> python -c "from zephyr.governance.rule_bridge.session_worktree import session_worktree_start, generate_session_id; sid = generate_session_id(); r = session_worktree_start(sid); print(r)"
> ```
> 记住返回的 `session_id`。**一个任务=1次start+多次Edit/Write+1次commit+1次merge**。后续编辑用 Edit/Write 正常操作（写项目根即可，`session_worktree_commit` 会自动同步到 worktree）。
>
> **提交时 MUST 调**（不用裸 `git commit`）：
> ```
> python -c "from zephyr.governance.rule_bridge.session_worktree import session_worktree_commit; r = session_worktree_commit('<session_id>', ['<file1>', '<file2>'], '<message>'); print(r)"
> ```
> **任务完成**：调 `session_worktree_merge(session_id)` merge 回主分支（pre-merge 自动清理冗余未提交改动，通常无需手动处理脏工作区）。**放弃**：调 `session_worktree_abort(session_id, files=['<file1>', '<file2>'])`——`files` 参数传入 AI 修改/创建的文件列表，abort 时自动清理主工作区残留（tracked→`git checkout --`恢复，untracked→物理删除）。**merge失败**（自动清理后仍失败=AI commit 后又编辑了同一文件导致内容不一致）：先 `git checkout -- <冲突文件>` 还原主工作区→重试 `session_worktree_merge`→仍失败才 `session_worktree_abort` + 改用 GitCommitGateway。
>
> **为什么**：多 AI 对话共享工作目录导致 stash 堆积（4 个 stash 卡住对话），worktree 独立 git index 从根本消除冲突。
> **君子协定（正式）**：无门禁强制（Trae IDE 不可 hook），依赖 AI 自觉。6 连续 PASS 已转正式（Round2-4 + Extreme A/B/C，覆盖 4 种代码路径）。**HELD-OVERLAP 已加硬（2026-07-02）**：`session_worktree_commit` 内置 auto-claim + 硬阻断（对标 GitCommitGateway 的 HELD-OVERLAP gate）——commit 前对每个文件调 `registry.claim_file()`（原子 check-and-claim，防 TOCTOU 竞态），被其他活跃 session 持有则 `HELD_OVERLAP_VIOLATION` 阻断（回滚已 claim 文件）；claim 是 session 级，merge/abort 时 `unregister` 自动释放。逃生通道：`allow_overlap=True` 参数放行（对标 `--allow-overlap`）。**逃生通道（永久保留）**：HELD-OVERLAP 加硬消除了"两 session 编辑同一文件"的搭便车根因，但无法解决 git 固有 merge conflict（`allow_overlap=True` 强行覆盖时）+ AI commit 后又编辑同一文件导致内容漂移——此时 `session_worktree_abort` + 改用 GitCommitGateway（stash 隔离）作为兜底。详见 [FP-ISO.4C](#fp-iso4c)。
>
> **豁免条款（reconciler 实弹验证专用，2026-07-02 裁定）**：验证 GitCommitGateway post-commit reconciler 链路时，允许走 `scripts/git_commit.py --reconciler-verify`（不经过 session_worktree）。**豁免理由**：reconciler 操作主分支数据（depgraph DB / 主仓库 index auto-commit），无法在 worktree 独立 index 内运行；且验证为单 session 诊断场景，与君子协定“防多 session 并发冲突”的核心目的正交。**三重前置条件**（缺一不可）：(1) 主工作区 clean（`git status --short` 空）(2) 无其他活跃 session（或 `--allow-concurrent` 逃生）(3) `claim_files` 全部成功（`--allow-overlap` 自动禁用）。搭便车风险由 claim_files 文件级锁 + `_GlobalCommitLock` 串行锁 + 干净环境三重防护覆盖。**仅限验证场景**，常规开发提交仍 MUST 走 session_worktree。

## RULE-DEPGRAPH：第三件事（防幻觉/防漂移治本规则，2026-07-02）

> **施工前 MUST 登记**：任何模块施工前（写第1行业务代码前），MUST先通过 `apply_depgraph.py` 将该模块的依赖关系（模块间/契约/事件/外部域）登记到 depgraph 设计态（`status=planned`）。禁止"先施工后补登记"或"施工中临时编造依赖"。施工完成并通过验证后，将 `status` 从 `planned → production`。
>
> **写入设计态前 MUST 检查运营态**：`apply_depgraph.py --add-design-node` 写入 `build_status=planned` 时，内置门闸自动检查 depgraph 运营态（production节点）是否就绪。运营态为空→阻断，提示先手动运行 `generate_project_depgraph.py` 刷新；运营态就绪→允许写入设计态。设计态必须基于最新运营态，否则在过期快照上设计=幻觉温床。逃生通道：`--skip-refresh`（仅限故障时使用，正常流程禁止）。
>
> **为什么**：depgraph 是依赖关系唯一真源。AI 从 depgraph 查询依赖=零幻觉空间；AI 绕过 depgraph 自行推断依赖=幻觉/漂移根源。未登记依赖在拓扑验证时自动阻断。
>
> **流程**：
> 1. `generate_project_depgraph.py` 刷新运营态（门闸自动执行）
> 2. `apply_depgraph.py --add-design-node PATH BLUEPRINT_ID DOMAIN_ID planned` 登记设计态
> 3. 拓扑验证（无循环/无缺失/无孤儿）
> 4. 施工（代码引用 depgraph 契约名）
> 5. 验证依赖一致性
> 6. `apply_depgraph.py --transition-build-status NODE_ID production` 转正

## 1. 项目概述

ZephyrAlpha 是一个 AI 治理框架。AutoRuntime Core 是其**系统大脑**——负责三层运行时编排、节律调度、健康监控、审计日志、工作编排、自动接入。

## 2. 终极目标

**接入项目里的所有模块、系统、脚本，能灵活运用所有东西。**

衡量标准：孤儿率 = 未接入模块数 / 总模块数 → 目标 = **0%**

## 3. 核心系统

| 系统 | 入口 | 职责 |
|------|------|------|
| AutoRuntime Core | `python -m zephyr.trading` | 系统大脑，调度所有 AI 运行时 |
| PipelineOrchestrator | `zephyr.integration.pipeline_orchestrator` | 管线编排（M1-M11） |
| AgentOrchestrator | `zephyr.trading.orchestrator` | Agent 生命周期管理 |
| TaskRepository | `zephyr.governance.task_repo` | 任务状态机（10 状态） |
| GitCommitGateway | `zephyr.governance.rule_bridge.git_commit_gateway` | 全项目唯一合法 git commit 入口（串行锁+stash隔离+GW标记） |
| A2A Protocol | `zephyr.infrastructure.a2a_protocol` | Agent 间通信与冲突解决（MOD-INF-025） |
| LLM 安全网关（LSG） | `zephyr.security.llm_defense.llm_security.gateway` | L1-L8 十层纵深防御，所有 LLM 调用必经安检（RULE-LSG-001） |
| MCP Servers（10 个） | [`config/mcp.json`](file:///d:/ZephyrAlpha/config/mcp.json) | MCP 服务器注册表（含工具列表/安全等级/ACL/限流） |
| Trigger Router（6 触发器） | [`config/trigger_router.yaml`](file:///d:/ZephyrAlpha/config/trigger_router.yaml) | 事件驱动路由表（含 handler/优先级/重试策略） |
| Dashboard (Panel) | `src/zephyr/frontend/dashboard/app_panel.py` | Panel+HoloViz 仪表盘主入口（v3.1.0, #ARCH-047），10 Tab 治理+交易/回测；`panel serve app_panel.py --show --port 5006` |

> MCP 服务器完整定义（工具清单/角色权限/熔断配置）见 [`config/mcp.json`](file:///d:/ZephyrAlpha/config/mcp.json)。触发器路由表（6 触发器+处理器+安全等级）见 [`config/trigger_router.yaml`](file:///d:/ZephyrAlpha/config/trigger_router.yaml)。

### config/ 发现契约（ARCH-038 P2）

新 AI 需发现 `config/` 下有哪些配置文件、用途线索、消费者时，运行：

```bash
python scripts/governance/d1_structure/validate_config_integrity.py --list-configs
```

输出 YAML 清单（按需生成，不持久化），每个文件含：`path`（相对路径）、`type`（yaml/yml/json）、`size_bytes`、`top_keys`（YAML 顶层 keys，用途线索）、`protected_by`（CBAC 保护状态）、`consumers`（代码中引用此文件的位置，最多 5 个）。向内收逻辑：复用 L1 枚举，无持久化文件，无维护成本。

## 4. 发现可用服务

```python
from zephyr.trading.capability_registry import CapabilityRegistry
registry = CapabilityRegistry()
all_capabilities = registry.list_all()
inference_caps = registry.find_by_tags(["inference", "text"])
a2a_caps = registry.find_by_tags(["a2a", "coordination"])
```

### 4.1 Agent 间通信（A2A Protocol）

```python
from zephyr.infrastructure.a2a_protocol import a2a_card_registry
agents = a2a_card_registry.discover(capability="write")

from zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_schemas import A2AMessage, A2AMessagePart, PartType
msg = A2AMessage(from_agent="your-id", to_agent="target-id", task_id="t-1")

from zephyr.infrastructure.a2a_protocol.layer3_coordination.conflict_detector import ConflictDetector, ChangeSet
from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import Arbitrator, AgentMeta, AgentRole
```

### 4.2 LLM 安全网关（RULE-LSG-001：强制调用）

> **铁律：所有 LLM 调用必须经过 LSGSecurityGateway。禁止裸调任何 LLM API。**
> 违反此规则会被 GATE-20 pre-commit 门禁硬阻断。

```python
from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway
from zephyr.security.llm_defense.llm_security.protocol import SecurityDecision

gateway = LSGSecurityGateway()

# 输入扫描：用户输入给 LLM 前先过安检
result = await gateway.scan_input(user_text, metadata={"provider": "openai"})
if result.decision == SecurityDecision.DENY:
    raise ValueError(f"输入被拦截: {result.reason}")

# 输出扫描：LLM 返回内容给用户前先过安检
result = await gateway.scan_output(llm_response)
if result.decision == SecurityDecision.DENY:
    llm_response = "[内容被安全策略过滤]"

# 全量扫描：输入+输出流水线
result = await gateway.full_scan(user_text, llm_response)
```

**参考实现（带重试机制）**：`src/zephyr/autonomy_core/llm_gateway.py` 中的 `_lsg_scan_input_sync` / `_lsg_scan_output_sync` 模式。

**GATE-20**：`python scripts/governance/d7_code/detect_direct_llm_calls.py --ci` — AST 扫描 src/zephyr/ 下所有裸调，已导入 LSG 的放行，未导入的阻断。

#### 4.2.1 运行时 Gate（GATE-20 后备防线）

> **GATE-20 是 pre-commit 静态门禁，存在不可修复的静态分析上限**：当代码内容在运行时
> 从外部（文件/网络/数据库）获取再 `exec` 时，AST 层面不可见。运行时 Gate 作为后备防线，
> 在 Python 进程运行时拦截所有绕过 LSG 的裸调 LLM API 调用。

- **真源**：[runtime_interceptor.py](file:///d:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py)
- **启动引导**：[sitecustomize.py](file:///d:/ZephyrAlpha/sitecustomize.py)（Python 解释器启动时自动 `install()`，零业务侵入）
- **机制（方案 A+B 融合）**：sitecustomize 自动引导 → `sys.meta_path` finder 拦截 openai/anthropic/litellm/langchain 导入 → 加载后 monkey-patch 核心调用方法（`chat.completions.create` / `messages.create` / `litellm.completion` 等）→ 调用时检查 LSG 放行令牌（`contextvar` + `threading.local` 混合存储，TTL 30s）→ 缺失令牌抛 `BareLLMCallError` 硬阻断
- **令牌颁发**：LSG 的 `scan_input` / `full_scan` / `scan_agent_action` 在返回 `ALLOW` 时自动调用 `grant_allowance()`（[gateway.py](file:///d:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/gateway.py) 单点注入，业务代码无感知）
- **kill-switch**：`ZEPHYR_RUNTIME_GATE=0` 关闭（sitecustomize 层 + install() 层双重尊重）
- **部署说明**：cwd=repo root 时自动生效（`python -m pytest` / `python -c` / `python -m zephyr...` / repo root 脚本）。运行 `python scripts/sub/foo.py`（sys.path[0]=脚本目录）需 `PYTHONPATH=<repo_root>`
- **测试**：`pytest tests/llm_security/test_runtime_interceptor.py`（含红蓝对抗：`code = read_file("payload.txt"); exec(code)` 运行时被拦截）
- **能力注册**：`runtime_llm_call_interceptor`（capability_canonical_file_registry.yaml）

### 4.3 RULE-TWO 注册审计（孤儿检测防线 2）

> **防线 2**：注册表（`__all__` / `script_manifest.yaml` / `_registry.yaml`）+ 自动审计。
> 防线 1 是 GATE-20 运行时拦截（§4.2.1），防线 3 是 N-16 文件名唯一性。

- **真源**：[audit_registration.py](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/audit_registration.py)
- **机制**：扫描磁盘 `.py`/`.yaml` 对比三个注册表，检测孤儿文件 / 僵尸引用 / 缺 `__all__`
- **审计范围（单一真源 `_in_audit_scope`）**：仅 `src/zephyr/` 与 `scripts/` 下文件；其他目录（`tests/`/`docs/`/根级）不扫。`--incremental`、`--files`、post-commit reconciler 三处 scope 过滤统一委托该函数，勿重复实现
- **RULE-TWO 豁免**：被其他模块 `import` 的文件视为"已有自然发现机制"，不报为 ORPHAN。消费者地图由 `_batch_collect_imports()` 构建，扫描范围 `src/`+`scripts/`+`tests/`+**根级 `*.py`**（如 `sitecustomize.py` 是系统级消费者，漏扫根级会导致 RULE-TWO 豁免失效 → 误报 orphan）
  - **消费者地图构建（双路径回退）**：优先使用 `rg`（ripgrep，快速路径），`rg` 不可用时自动回退到 Python `ast` 解析（`_collect_imports_via_ast()`，零外部依赖，跨环境一致）。消除 `rg` 不在 PATH 时静默返回空 map → RULE-TWO 豁免失效 → 误报 orphan 的脆弱性
- **post-commit reconciler**：`make_registry_sync_reconciler`（AD-GOV-001 合并后，GATE-REGISTRY-SYNC 统一入口，见 [reconciliation_registry.py](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)）在 commit 后自动触发，用 `--files <committed_files>` 精确扫描本次提交文件
  - **触发条件**：committed_files 含 `src/zephyr/*.py` 或 `scripts/governance/*.py`（注意：比 audit scope 窄，仅 governance 相关 commit 触发）
  - **禁用 `--incremental`**：它会扫工作树全部 WIP（`git diff HEAD` + 未跟踪），把与本次 commit 无关的 WIP 误判为 NEW orphan（历史 Bug：`runtime_interceptor.py` 为 WIP 未提交却被扫到）
  - **scope 过滤单一真源**：reconciler 仅筛 `.py`，scope 过滤委托 audit 的 `_in_audit_scope`（不重复过滤，避免漂移）
- **基线差分**：`--baseline-aware` 对比基线分类 NEW/RESOLVED/PERSISTENT，仅 NEW 阻断（exit 1），PERSISTENT 降级告警（exit 0）
- **双基线系统（勿混淆，防误判漂移）**：
  - `audit_registration_baseline.jsonl` — 本审计独立基线，`meta_path=None`（**从不写** `baseline_meta.json`）
  - `current_baseline.jsonl` + `baseline_meta.json` — `manage_baseline.py` 的独立系统（追踪 `phase_e_full` 等全量基线）
  - 两者独立，`baseline_meta.json` 的 `finding_count` 与 `audit_registration_baseline.jsonl` 行数**无关**，勿误判为漂移

### 4.4 能力反查与符号发现（ARCH-031 局限2 文档化，2026-07-01）

新 AI 进入项目后，发现已有功能/符号有两个互补手段，职责边界明确：

- **能力发现（CapabilityLookup）**：查"某个能力是否存在 + canonical 真源在哪"。
  - 真源：[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)（134 条已声明能力）
  - 用法：`from zephyr.governance.capability_lookup import CapabilityLookup; CapabilityLookup().find("handoff")`
  - 覆盖范围：仅已声明 capability_id 的功能。子目录文件（如 `audit_trail/agent_signer.py`）默认未声明，查不到。
  - 何时用：新 AI 想做"X 功能"前，反查是否已有该能力的 canonical 实现。

- **符号发现（Grep）**：查"某个符号（函数名/类名/常量）定义在哪"。
  - 用法：`Grep "class AgentSigner"` 或 `Grep "def agent_signer"`
  - 覆盖范围：`src/zephyr/**/*.py` 全部文件（含未声明能力的子目录文件）。
  - 何时用：新 AI 知道符号名时，直接 Grep 即可唯一命中 canonical 位置。
  - 已验证：`agent_signer`、`changelog_manager`、`self_healer` 等 7 个子目录符号 Grep 均唯一命中 canonical。

- **为什么不在 YAML 声明所有子目录文件**：维护成本高（governance/ 子目录有 200+ 文件）且无必要——Grep 已能可靠发现符号，CapabilityLookup 重复实现符号发现会破坏职责边界（向内收原则①：能现成不创造）。
- **何时声明新 capability**：当某个功能有明确能力边界、可被复用、且新 AI 可能不知道已存在时（如 `agent_signer`、`self_healer`），才在 YAML 声明 capability 条目。
- **pipeline 模块 canonical 声明**（2026-07-02，消除 `integration/` 与 `infrastructure/pipeline/` dual source 镜像副本）：管线核心13模块（`model_router`/`cost_tracker`/`ct_pipe_routing`/`preemption_manager`/`pipeline_agent_bridge`/`llm_gateway`/`routing_plugins`/`pipeline_lock`/`dead_letter_queue`/`circuit_breaker_manager`/`backpressure_types`/`backpressure_manager`/`pipeline_models`）已登记 capability，canonical = [`src/zephyr/infrastructure/pipeline/`](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/)（production/D_INFRA_RUNTIME）。原 `src/zephyr/integration/` 顶层镜像副本（prototype/D_INTEGRATION）已删除。`layer_router`/`layer_consumer_registry` 已于阶段1清除（14层概念废弃）。新 AI 想做"管线模型路由/成本追踪/背压管理/断路器"等前，CapabilityLookup 会反查到 canonical 在 `infrastructure/pipeline/`，勿在 `integration/` 重建。编排器 `PipelineOrchestrator` 例外，仍在 `integration/pipeline_orchestrator.py`（跨域集成入口，组合 infra.pipeline 组件）。

### 4.5 根目录 vs 子目录同名文件门禁（ARCH-031 局限1 调研结论，2026-07-01）

governance/ 等包的根目录 vs 子目录同名文件（stale duplicate）有三层自动门禁：

- **GATE-SSOT 第1层（check_ssot_conflicts）**：检测同 [MODULE] module_path 冲突。
  - 新 AI 创建根目录文件且 [MODULE] 标注与子目录文件相同时**硬阻断**。
  - 真源：文件头部 [MODULE] 字段。
- **GATE-SSOT 第2层（check_capability_duplicates）**：检测 basename 撞 capability_id/alias。
  - 已注册能力的同名文件**硬阻断**（relation=conflicting/sibling）。
  - 真源：capability_canonical_file_registry.yaml + 磁盘扫描派生。
- **CREATE-GUARD**：新建 .py / 非 rules/ .yaml 文件必须登记 creation_token。
  - 强制 AI 声明创建意图 + 关联 capability，未登记则**硬阻断**。
  - .yaml 扩展（2026-07-01）：非 rules/ .yaml 亦需 token（.yaml 是 YAML→DB 单向同步真源，第二份配置真源漂移污染 9 个 readonly DB 表）；rules/ .yaml 走命名检查不走 token。

**剩余缺口**：新 AI 创建根目录文件、[MODULE] 标注为根目录路径、文件名与子目录文件相同但未注册 capability 时，三层门禁均不触发。此缺口由本节提示 + governance/__init__.py docstring 文件归属规则提示兜底。

**N-16 扩展到 src/ 不可行**：src/zephyr/ 有 500 个同名 basename（含 499 个 __init__.py），豁免清单规模过大，维护成本高于收益。N-16 仍只覆盖 tests/ + docs/。

### 4.6 governance/ 根目录防平铺门禁（ARCH-031 P3 防复发，2026-07-02）

`src/zephyr/governance/` 根目录**禁止新增 .py 文件**（含 rename 到根目录）。治本前根目录平铺 33 个 .py 文件，治本后迁移 24 文件到 12 功能子目录，仅保留 9 个高风险核心模块：

| 保留文件 | 原因 |
|----------|------|
| `__init__.py` | 包标记 |
| `base.py` | 基类（被大量子目录 import） |
| `capability_lookup.py` | 能力反查引擎（消费者 76+） |
| `depgraph_schema.py` | depgraph schema（消费者 156+） |
| `evidence_pack.py` | 审计证据包 |
| `integrity.py` | 完整性校验（消费者 119+） |
| `merkle_hourly.py` | Merkle 小时聚合（消费者 71+） |
| `performance_attribution_report.py` | 绩效归因报告（消费者 71+） |
| `rule_patterns.py` | 治理规则正则 + 安全审计模式唯一真源（SSoT，被 create_guard / r5_digit_suffix_gate / validate_directory_structure / validate_rule_frontmatter + 三包 kb_gate/privacy 共同 import；含 PIICategory/POISONING_INDICATORS/PII_PATTERNS，原 security_patterns.py 已合并 ARCH-033） |

**门禁**：CREATE-GUARD 扩展检测（[`create_guard.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/create_guard.py)）——staged 新增(A) + rename(R) .py 文件路径匹配 `src/zephyr/governance/<name>.py`（`path.count("/")==3`）→ **硬阻断**。错误信息含 "ARCH-031 防复发" + "新模块 MUST 放入子目录"。

**新模块归属规则**：新 .py 文件 MUST 放入对应功能子目录（`audit/` `persistence/` `commit_gates/` `strategies/` `ops_governance/` `resilience_governance/` `context_governance/` `data_governance/` `engine/` `financial_governance/` `trading_contracts/` `rule_enforcement/`）。不确定归属时 Grep `src/zephyr/governance/` 下已有子目录选择最匹配的。

### 4.7 目录平铺容量+前缀簇合规门禁（GOV-DOC-018 ARCH-043 Risk 2-B，2026-07-03）

**痛点**：GOV-DOC-018 规定 T_hard=60/T_soft=120 阈值，>T_hard 的目录享 T_soft=120 需在 `__init__.py` 文档化命名前缀约定。但原 `validate_nested_flat_dirs.py` 只数文件数不检查前缀文档，新 AI 可绕过裁定添加不合规文件，或在未读注释情况下强制拆分已裁定合规的目录。

**门禁**：[`validate_nested_flat_dirs.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_nested_flat_dirs.py) `--check-prefix` 模式——检测 >T_hard(60) 目录的 `__init__.py` 是否文档化命名前缀约定（标记词：`命名规则`/`前缀簇`/`T_soft`/`GOV-DOC-018`/`模块地图`），无约定报 ERROR。

**自动触发**：注册为 `GATE-NESTED-FLAT-PREFIX` 到 [`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml)，`src/zephyr/*.py` 变更时 pre-commit 自动运行（事件驱动，全自动，无需手工触发）。`--warn-only` 过渡期（9 个存量违规未清零：8 tests/ + src/zephyr/infrastructure/rollback，清零后转 `--ci` 硬阻断）。

**真源**：阈值 `thresholds.yaml` §directory_scalability（`src_py_warn: 60` / `src_py_error: 120`）；规则 `trae_028_doc_structure_naming.yaml` §directory_scalability。

## 5. 三层 AI 工作分配

- **L1 Trae**: 人在 IDE 交互时使用，免费，人在环
- **L2 Local**: 24/7 自动化，Ollama 本地推理（BGE-M3 + qwen3:8b），零成本
- **L3 API**: 夜班/高价值/不确定，DeepSeek V4 Pro / Claude，有成本

## 6. 关键路径

- `specs/auto_runtime_core/`: AutoRuntime Core 蓝图规范
- `src/zephyr/trading/`: AutoRuntime Core 实现
- `data/audit_logs/`: AI 行为审计日志
- `data/capability_cards/`: 能力卡片定义
- `data/work_dags/`: 工作 DAG 定义（待创建）
- `architecture_model/`（仓库根，单树，2026-06-30 治本合并）: 架构模型 YAML SSoT——53域清单（depgraph 派生）+ 跨层契约（`contracts/`）+ 不变量（`cross_cutting/`）+ `module_id_registry` + 领域事件（`events/`）+ DDD 模型（`domain/`）+ b_track 施工视图（`layers/b_*.yaml`）；53域是唯一物理分类（depgraph），4值（L0_infrastructure/L1_foundation/L2_domain/L3_application）是域的 `layer_id` 属性枚举（真源：`depgraph_schema.py` DB trigger）

### 6.1 目录生命周期（AI-03 审计 P10，2026-07-05）

临时+日志+工具区目录生命周期规则（`.gitignore` 已对齐）：

- **`tmp/`**：task_bound 一次性脚本退役区，运行时产物不入库（`.gitignore` 第 228 行 `tmp/*`，仅保留 `tmp/.gitkeep`）。新 AI 在 `tmp/` 创建脚本完成使命后**禁止清理 git rm**（`.gitignore` 已自动忽略）；历史已跟踪脚本通过批量 `git rm --cached` 退役（commit `6846813fac` 退役 21 脚本，2026-07-05 AI-03 审计再次退役 90+ 脚本）。
- **`logs/`**：运行时日志，`.gitignore` 第 187 行整目录忽略，禁止入库。
- **`session_logs/`**：Session Log 真源目录（snake_case），与 `session-logs/`（kebab-case，2026-07-05 AI-03 审计已删除）真源唯一；新 session yaml 落盘格式 `session_logs/YYYY/MM/session-YYYYMMDD-NNN.yaml`。
- **`_journals/`**：AI 行为日志（`skill_telemetry.jsonl` / `skill_transitions.jsonl`），`.gitignore` 第 190 行整目录忽略，运行时写入不入库。

## 7. 代码规范

- Python >=3.12, ruff lint, pydantic v2
- 所有新组件**必须**注册 CapabilityCard 到 CapabilityRegistry
- 所有 AI 行为**必须**写入 AiAuditLogger
- 详细编码约束见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)（四条铁律 + 写代码三条）和 [`trae_010_code_naming_organization.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml)（GOV-ENG-001）
- **文件命名规范真源见 [`trae_028_doc_structure_naming.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)（GOV-DOC-003 §N-16）**——创建新文件前 MUST 先 `Grep` 检查项目内是否已存在同名 basename；**N-16 文件名项目内唯一性检测为硬阻断**（不受 GATE-NAMING `--warn-only` 过渡期影响），覆盖 `tests/` + `docs/` 目录，commit 时 pre-commit 钩子自动检测；同名文件导致 AI 无法确定真源产生漂移（如 `capability_heatmap.md` 曾存在两个不同内容同名文件，19315 vs 11966 字节）；**N-16 豁免清单（conftest.py/__init__.py/index.md 等）真源为 §gov_doc_003_filename_uniqueness.n16_config，`check_naming_convention.py` 从此动态加载（非硬编码），改 YAML 即生效，禁止改代码豁免清单**；**临时沙箱目录（`tests/_tmp_*` / `docs/_tmp_*`，如并发红蓝对抗沙箱 `tests/_tmp_redblue_f2/`）由 `n16_config.skip_dir_prefixes` 豁免（`os.walk` 按目录名前缀 `_tmp_` 剪枝），防沙箱文件与正式文件撞名误触发 N-16 硬阻断卡死并发 commit**
- **规则文件创建入口（ARCH-037，GOV-DOC-003 主题前缀条款）**——新建 `docs/.../rules/trae_XXX.yaml` MUST 经 `python scripts/scaffold.py rule <主题_描述>`（RULE-TWO 强制入口）。scaffold 检查1.5 强制文件名格式 `trae_NNN_<主题>_<描述>.yaml`——单段 name 阻断，新主题前缀仅警告。绕过 scaffold 直接 Write 规则文件 → 双层强制：① [`validate_rule_frontmatter.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/validate_rule_frontmatter.py) DIM-5 pre-commit 检测（可被 `--no-verify` 绕过）② [`create_guard.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/create_guard.py) commit-time 强制（ARCH-037 B 选项，扩展现有 CREATE-GUARD gate 检测范围，`--no-verify` 绕不过）→ 非 trae 命名 + 单段 name 硬阻断（含 rename 检测）。主题前缀集合由 `scaffold.py::_derive_rule_theme_prefixes` 从现有文件名自动派生（无独立词表真源，符合向内收）。
- **module_id/blueprint_id/domain_id/submodule_id 格式校验真源见 [`validate_module_id_naming.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/validate_module_id_naming.py)（裁定#208 双轨制 + R2 治本修订）**——双轨正则（layer-master 轨 MOD-{LAYER}-NNN / 派生轨 MOD-{DOMAIN_FRAGMENT}[-NNN] / 跨域共享轨 SH-{ABBR}-NNN）唯一责任点；`is_valid_module_id(bp_id)`、`is_valid_domain_id(domain_id)` 和 `is_valid_submodule_id(submodule_id)` 三个公共函数供 `check_naming_convention.py`（GATE-NAMING N-06）和 `apply_depgraph.py`（NR-002/cmd_rename_domain/cmd_insert_domain）import 复用；**禁止在代码中定义本地 module_id 正则（防真源分裂）**；capability 反查 alias=`validate_module_id_naming`（`capability_canonical_file_registry.yaml` 注册 13 个 aliases 覆盖中英文关键词）
  - **R2 治本修订（2026-07-05）**：D-XXX-NNN 已废弃为 module_id 派生轨，重定义为 submodule_id 专用（蓝图内部子模块编号）。module_id 仅保留双轨：layer-master 轨（MOD-）+ domain-functional 派生轨（MOD-）。`is_valid_module_id("D-GOVERNANCE-001")` 现在 return `(False, "D-XXX-NNN 已废弃...")`；蓝图内部子模块编号使用 `is_valid_submodule_id("D-FACTOR-01")` 校验（return `(True, "")`）。规则真源见 [trae_028 §gov_doc_009_submodule_id_convention](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)。
  - **submodule_id 作用域**：仅用于蓝图正文 §sections/§modules/§lifecycle 章节引用；**禁止**写入 blueprint frontmatter 的 `module_id` 字段；**禁止**作为 `depgraph.nodes.blueprint_id` 值。三种 ID 区分：`module_id=MOD-*/SH-*`（蓝图级）、`submodule_id=D-{DOMAIN}-NNN`（蓝图内部，连字符+序号）、`domain_id=D_{DOMAIN}`（域，下划线+无序号）。
- 治理决策方法论见 [`trae_024_methodology_diagnosis.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml)（PS-STD-011）——含MTH-006诊断反转验证：深挖后MUST回溯初始诊断，不一致时追问"为什么初始诊断错了？"
- 审计脚本质量见 [`quality_standard.md`](file:///d:/ZephyrAlpha/scripts/governance/quality_standard.md)（SCRIPT-QUALITY-001）
- 产出物规格化见 [`trae_030_doc_numbering_metadata.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)（GOV-DOC-011）——`.md` 文档 frontmatter 标准字段：`module_id, title, version, layer, depends_on, tags, **ttl（GATE-FRONTMATTER 强制校验）**`。**doc_type 合法值（v3.0.0，10 值）唯一真源见 [`doc_type_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml)**（非 trae_030）；doc_type↔rule_form 映射也在该词表中 per-value 定义。frontmatter 不可删字段完整清单见 [`onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)「绝对不可删的 15 类」
- **所有 `.md` 文档 frontmatter 和 `.py` 文件头部 MUST 含 `ttl` 字段**——2 个合法值：`permanent`（永久）/`task_bound`（任务绑定，完成即删）。判定方法：在永久区路径（`docs/01_policies/`、`docs/02_enterprise_architecture/`、`docs/03_modules/`、`docs/08_knowledge/`）→ `permanent`；否则 → `task_bound`（默认落 [`docs/_working/`](file:///d:/ZephyrAlpha/docs/_working/) 临时区）。详见 [`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) 的 `decision_tree`。
  - `.md` 用 D_md frontmatter（`ttl: permanent`），`.py` 用 A_full/A_test 注释行（`# [TTL] permanent`）。规则定义见 [`trae_047`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml)（A_full 15 字段 / A_test 7 字段）。
  - `.py` 文件 `# [TTL]` 在最后一个 `# [FIELD]` 行后插入；`__init__.py`/`conftest.py` 等无头部文件豁免。
- **生成器豁免区（generator-exempt-zones）**——`docs/02_enterprise_architecture/` 下 4 个子目录是生成器专用路径，生成器可自由创建/删除文件，**新文件跳过 `PROMOTION_BLOCKED` 门禁**（无需 `--allow-promote`）：`00_overview_entry/`、`01_global_architecture_diagram/`、`02_domain_architecture_docs/`、`03_governance_reports/`。真源：[`directory_contract.yaml directory_zones.permanent.exempt_subdirs`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml)（FILE-PLACEMENT-TTL gate 动态加载，ARCH-049）+ [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) `outputs` 字段。**不含** `03_governance_reports/domain_id_hyphen_rename_taskcards/`（手工任务卡）和 `04_architecture_principles_decisions/`（手工架构决策目录）。约束：生成器是这些目录的唯一合法修改源（约定，非技术强制）；N-16 文件名唯一性检查仍生效（不豁免）。
- **TTL 校验统一拦截点（真源唯一 / 向内收）**——pre-commit hook **GATE-FRONTMATTER**（[`check_frontmatter_metadata.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py)）是 ttl 校验**唯一真源**（全格式路由：.md→`parse_frontmatter` / .py+.sh+.ps1+.mmd→`parse_py_header` / .yaml→`parse_byyaml_anchor` / .json→`parse_json_meta`；全格式校验 ttl 值合法性，doc_type 仅对 .md 校验）。**拦截范围**：pre-commit hook 触发时校验（`files: ^docs/.*\.md$` 限制为 docs/ 下 .md 增量触发；全量扫描 `--all-files` 覆盖 docs/+src/+scripts/+tests/ 全格式）。**GitCommitGateway TTL-METADATA gate**——[`ttl_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/ttl_gate.py)（gate_id="TTL-METADATA", priority=32，subprocess 调 `check_frontmatter_metadata.py` 复用真源），覆盖 `commit()` 和 `_commit_auto()` 路径，gateway 路径（用 `--no-verify` 绕过 pre-commit）下 ttl 校验不再失效（fail-closed：checker 缺失/执行失败时阻断）。**GitCommitGateway FILE-PLACEMENT-TTL gate（ARCH-049，2026-07-05）**——[`file_placement_ttl_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/file_placement_ttl_gate.py)（gate_id="FILE-PLACEMENT-TTL", priority=33，in-process gate 动态加载 directory_contract.yaml + ttl_vocabulary.yaml），三重校验：①永久区新文件准入（PROMOTION_BLOCKED，需 `allow_promote=True`，exempt_subdirs 生成器输出豁免）②TTL↔zone 一致性（frontmatter.ttl=permanent 但在临时区→阻断；task_bound 但在永久区→阻断）③根目录子目录准入（第一级目录不在 directory_zones→阻断，防乱建子目录）。覆盖 `commit()` 和 `_commit_auto()` 路径（`_commit_auto` 传 `allow_promote=True`，reconciler 受信任）。**reconciler 路径**：`_commit_auto()` 跑 DCR gate + TTL-METADATA gate + FILE-PLACEMENT-TTL gate（三者均通过 `gate_registry.get` 复用，不复制检测逻辑）。
- **N-16 检查统一拦截点（真源唯一 / 向内收 v2）**——N-16 文件名唯一性检查逻辑唯一真源在 [`check_naming_convention.py::check_new_files_naming`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py)（增量检查：`git ls-files` 基线，只检测新文件引入的冲突，不阻断历史遗留）。GitCommitGateway 通过 subprocess 调用 `--check-new-full` 模式（subprocess 复用真源模式，同 DIRECTORY-CONTRACT gate 调 `check_directory_contract.py`），**不实现检查逻辑**。豁免清单真源在 trae_028.yaml §n16_config，由 check_naming_convention.py 模块级常量动态加载。fail-open：subprocess 失败/脚本不存在（exit≠0且≠1）时不阻断 commit。
- **config/ 平铺规则（ARCH-038，2026-07-01）**——`config/` 根目录**平铺所有配置 YAML/JSON**，禁止建模块归属子目录（如 `config/capacity/`、`config/compression/`）。**仅允许两个语义子目录**：`config/runtime/`（运行时状态文件）和 `config/infra/`（基础设施配置）。命名规则：小写+下划线，名字即责任（如 `capacity_slo.yaml` = 容量SLO，`compression_policy.yaml` = 压缩策略）。**根因**：按模块名建子目录导致同一功能域配置散在子目录和根两处，AI 找配置要猜位置；平铺后一眼看完所有配置，`config/<name>.yaml` 路径可预测。约束真源见 [directory_contract.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml)。
- **REPO_ROOT 真源归一（SSoT）**——仓库根常量唯一真源：[`zephyr.shared.io.paths.REPO_ROOT`](file:///d:/ZephyrAlpha/src/zephyr/shared/io/paths.py)（由 `find_repo_root()` 基于 .git marker 向上搜索，文件移动不 break）。`src/zephyr/**` 包内消费者：`from zephyr.shared.io.paths import REPO_ROOT`；`scripts/**`/`tests/**` 包外消费者：仅允许一次性极简 sys.path bootstrap（N 值固定），随后必须 `from zephyr.shared.io.paths import REPO_ROOT`。**禁止** `Path(__file__).resolve().parents[N]`、`.parent.parent...`、`Path("D:/ZephyrAlpha")` 等任何变体推算仓库根。**唯一豁免**：sys.path bootstrap 上下文（鸡生蛋：需先设 sys.path 才能 import REPO_ROOT）。**强制方式（已废弃，AD-001 阶段3 删除）**：原 GitCommitGateway `_check_repo_root_usage` 在 commit 时自动检测 `.py` 文件中的 `parents[N]` 反模式，2026-06-30 commit `cde1255c` 批量删除 12 个 `_check_*` 时删除此方法（详见 §8 L283）。现 REPO_ROOT 违规检测仅靠 pre-commit hook GATE-DD07（warn-only，被 gateway `--no-verify` 绕过）+ CI 兜底。原 Phase 1/Phase 2 计划（`_is_git_tracked` 跳过逻辑）随方法删除失效。**DB 路径硬编码禁令（P2 PG 迁移治本，2026-06-29）**——`sqlite3.connect("绝对路径.db")` 硬编码数据库连接违规，原 `_check_repo_root_usage` 模式5 AST 检测（已废弃，见 §8 L283，`:memory:` 内存库原豁免），现无 gateway 内置阻断。depgraph 连接入口 `get_depgraph_pg_connection()`，governance 连接入口 `get_governance_connection()`。**DB 写入脚本禁用 lock_files.py（P3 防复发门禁，2026-06-29）**——DB 写入用 PG MVCC 事务保护（文件锁对 PG 写无保护作用），原 `_check_repo_root_usage` 模式6 AST 检测（已废弃，见 §8 L283）：同一文件内同时出现 DB 写入信号（`import psycopg2` / `get_depgraph_pg_connection` / `get_governance_connection`）+ lock_files import 信号 → 原返回 `REPO_ROOT_VIOLATION` 阻断提交，现无 gateway 内置阻断（靠 code review + CI 兜底）。规则真源见 [trae_054](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml) §mandatory + [trae_001](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml) §db_write_protocol。
- **ZephyrBaseError 真源归一（SSoT）**——[`zephyr.shared.foundation.errors`](file:///d:/ZephyrAlpha/src/zephyr/shared/foundation/errors.py) 是 `ZephyrBaseError` 体系（13 个 Error 类）唯一真源。新增 Error 子类 MUST 改 `shared.foundation.errors`（唯一真源）；`shared` 层禁止 import `integration.*`（向下依赖原则）。
- **GATE-PURE-ASSERTION 纯陈述原则门禁（GOV-DOC-016）**——规则文档（`.trae/rules/*.md` + `AGENTS.md`）只含当前有效规则的肯定陈述句，禁止过渡文本（否定陈述句、历史对比描述、迁移标记等）。规则真源及违规词表见 [trae_030 §gov_doc_016_pure_assertion](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml#L533-L563)。强制方式（已废弃，AD-001 阶段3 删除）：原 GitCommitGateway `_check_pure_assertion` 在 commit 时正则扫描规则文档，2026-06-30 commit `cde1255c` 删除此方法，**未迁移到注册制 gate**。现纯陈述检测仅靠 rules_integrity_reconciler（post-commit，非阻断）+ code review。历史版本差异通过 git log 追踪，不写入正文。检测范围：AI 直接消费的规则入口（`.trae/rules/` + `AGENTS.md`）；YAML 规则定义文件（`docs/01_policies_and_standards/rules/`）的纯陈述治理由 rules_integrity_reconciler 独立负责。
- **`docs/_working/` 新增 .md 文件 MUST 在 frontmatter 声明 `completes_when` 字段**（可验证的完成条件），GitCommitGateway commit 时自动拦截缺失该字段的新文档；规则真源见 [trae_028 §归档与废弃流程](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)。
  - 自动归档由 [GATE-DELETE-AUDIT reconciler（含原 WORKING-DOCS 功能）](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) post-commit 事件驱动（capability_id：`working_docs_ghost_ref_archiver`，反查用法见 §9）。
- **读取 `docs/_working/` 下任何 .md 前 MUST 验证文档引用的脚本/YAML/blueprint_id 是否仍存在**（防幽灵引用漂移），细则见 [GATE-DELETE-AUDIT reconciler（含原 WORKING-DOCS 功能）](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（`scan_and_archive_working_docs` 幽灵引用检测）。
- **归档区 `docs/_archive/`（永久保留历史文件）**——归档触发条件采用二分法判定树（禁止凭"感觉不再需要"归档），所有永久区(01/02/03/08)的文件归档统一归此：

  **判定树（按顺序回答，命中即归档；两个问题均答 NO 则保留原位）**：

  - **Q1 替换归档**：是否存在新文件 Y 承担与目标文件 X 相同的职责，且 Y 是 X 的真源继任者（典型场景：md 规则→yaml 规则重写、旧脚本→新脚本重写、模块拆分合并）？
    - **YES → 执行替换归档**：① `git mv X docs/_archive/`；② 扫描全库引用点（.md/.yaml/.json/.csv），所有指向 X 的引用 MUST 更新为指向 Y（新真源）；③ frontmatter `ttl: permanent` + `status: deprecated`。
    - **NO → 进入 Q2**。

  - **Q2 删除归档**：目标文件 X 是否属于下线资产（功能下线 / 模块移除 / 脚本停用，且全库无活跃引用点）？
    - **YES → 执行删除归档**：① `git mv X docs/_archive/`；② 扫描全库引用点（.md/.yaml/.json/.csv），所有指向 X 的引用 MUST 从源头删除（无继任真源，不指向新文件）；③ frontmatter `ttl: permanent` + `status: deprecated`。
    - **NO → 保留原位**（X 仍有活跃职责，不归档）。

  **核心原则**：真源唯一——文件有继任者时，目标文件保留在原地 = 双真源并存 = AI 漂移，MUST 移走。归档区在 [`directory_contract.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml) `directory_zones.permanent.paths` 中（default_ttl=permanent），`validate_document_ttl.py --list-all-non-permanent` 不列为清理候选。**`docs/_archive/` 是唯一合法归档区**——禁止在 `docs/` 下创建其他归档目录。归档后引用断裂由 [GATE-FRONTMATTER/DOC-REF](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/audit_broken_links.py) 门禁在 commit 时检测断链并阻断。
- **共享能力真源位置**——跨层共享能力（errors / paths / yaml_utils / infra 等）真源在 [`src/zephyr/shared/`](file:///d:/ZephyrAlpha/src/zephyr/shared/)。新增共享能力 MUST 直接在 `src/zephyr/shared/` 创建或扩展，**禁止在 `src/zephyr/integration/` 下创建 `shared_*` proxy 层**（CapabilityLookup 反查 `shared.foundation.errors` / `shared.io.paths` 等能力可定位真源，`check_capability_duplicates` 在 commit 时自动检测 basename 撞 capability_id/alias）。`src/zephyr/shared/` 禁止 import `integration.*`（向下依赖原则，详见 §7 ZephyrBaseError 真源归一）。
- **禁止纯 re-export shim 文件（GATE-SSOT-CODE/check_pure_shim，治本漏洞1，2026-06-29）**——禁止新建纯 re-export shim 文件（`from zephyr.shared.* import *` 无实质代码的 .py 文件）。纯 shim 是真源分裂温床——AI 看到两个 import 路径指向同一符号，无法确定真源产生漂移。**判定标准**：AST 白名单分析，技术细节（哪些节点算实质代码、哪些不算）以 [`check_pure_shim.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_pure_shim.py) 的 `is_pure_reexport_shim()` 函数为**唯一真源**，本规则文档只描述"做什么"（禁止纯 shim），不重复描述"怎么做"（白名单判定逻辑），避免规则文档与代码分裂。**合法例外**：①`__init__.py` 包聚合 ②临时过渡 shim（文件头部含 `# [TTL] task_bound` + `# [DEPRECATED]` 标记，有 TTL 自动清理机制）。**强制方式**：[`check_pure_shim.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_pure_shim.py) GATE-SSOT-CODE pre-commit 钩子，commit `src/zephyr/**/*.py` 时自动检测（`--no-verify` 绕不过 GitCommitGateway Python 层门禁）。
- **禁止附带性 re-export（SSoT 治本 D1，2026-06-30）**——模块 import 符号仅供自身使用，禁止成为该符号的下游再导出点。例如 `from zephyr.shared.io.paths import REPO_ROOT` 后，其他模块 MUST 从 `zephyr.shared.io.paths`（真源）或 `_shared.constants`（sanctioned re-exporter）import，而非从本模块再 import。**唯一 sanctioned re-exporter**：[`_shared/constants.py`](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py)（scripts/ 域 SSoT 桥接层，re-export REPO_ROOT/DB_PATH 等常量给 scripts/ 域使用）。病根：模块为自身使用 import 常量后，下游从该模块 import 同一符号 → 多 import 路径 → AI 无法确定真源 → 漂移。与 GATE-SSOT-CODE/check_pure_shim 区别：纯 shim 是"文件只做 re-export 无实质代码"；附带性 re-export 是"文件有实质代码但意外成为 import 路径"。两者均违反真源唯一原则。
- **词表合法值加载规范** → 见 [trae_060 §2 唯一真源与直接消费](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L84-L115)（向内收原则①+②；禁止硬编码/同步复制词表合法值，必须 yaml.safe_load 动态加载；GATE-VOCAB 门禁强制执行）。本节不复制规则文本，仅提供实现层用法示例。
  - **真源实现**（治本1 后）：`src/zephyr/shared/io/yaml_utils.py` 提供 `load_vocabulary_values()`、`load_vocabulary_entries()` 和 `load_vocabulary_deprecated_map()` 三个函数。`load_vocabulary_values` 返回 `set[str]`（只需值集合时用）；`load_vocabulary_entries` 返回 `list[dict]`（需要 value+definition 时用，如 schema.json 双向同步填充 description）；`load_vocabulary_deprecated_map` 返回废弃值映射。`strict=True` 默认 fail-fast，文件不存在抛 `FileNotFoundError`（消除静默失败 DoS 漂移）。
  - **scripts/ 侧用法**（重新导出，保持兼容）：
    ```python
    import sys
    from pathlib import Path
    _GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
    if _GOV_DIR not in sys.path:
        sys.path.insert(0, _GOV_DIR)
    from _shared.yaml_utils import load_vocabulary_values, load_vocabulary_deprecated_map
    VALID_STATUSES = load_vocabulary_values("status_vocabulary.yaml")
    DEPRECATED_MAP = load_vocabulary_deprecated_map("doc_type_vocabulary.yaml")
    ```
  - **src/zephyr/ 侧用法**（直接 import）：
    ```python
    from zephyr.shared.io.yaml_utils import load_vocabulary_values, load_vocabulary_deprecated_map
    VALID_DOC_TYPES = load_vocabulary_values("doc_type_vocabulary.yaml")
    ```
  - **配套门禁**：**GATE-VOCAB** 已接入 [`.pre-commit-config.yaml` L262-275](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L262-L275) 作为 pre-commit 钩子（`id: gate-vocab`，`--ci` 硬阻断模式，2026-06-26 违规清零后转），`src/zephyr/**/*.py` 或 `scripts/**/*.py` 变更时自动触发。AST 扫描检测 `VALID/ALLOWED/LEGAL/PERMITTED_*_VALUES/STATUSES/TYPES/LEVELS/LAYERS/TTL/CATEGORIES/CLASSIFICATIONS/LIST/SET` 模式的字面量硬编码（含 `dict()/list()/tuple()/"a,b".split()` 隐式字面量 + walrus 操作符）+ `load_vocabulary_values("xxx.yaml")` 引用文件存在性校验。例外：DDL 文件（`sqlite_schema.py` 等）走 DDL-as-Code 协议；`_archive/` 排除；**`# noqa: gate-vocab`** 内联豁免（带理由的诚实豁免，非偷偷绕过）。门禁真源见 [trae_060 §5 prohibition_list](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L189-L213)。**注意**：§5 中 "23处(9词表)" 的 evidence 举例已过时（2026-06-26 审计确认所有举例文件已不存在或已修复，GATE-VOCAB 实时扫描 0 违规），审计报告见 [`docs/_working/trae_060_s5_evidence_audit.md`](file:///d:/ZephyrAlpha/docs/_working/trae_060_s5_evidence_audit.md)。新 AI 应以 GATE-VOCAB 实时扫描结果为准，而非 §5 的快照式列举。
  - **capability 反查注册表**已登记 2 条能力（`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`）：`vocabulary_values_loader`（canonical = `src/zephyr/shared/io/yaml_utils.py`）+ `vocab_hardcode_detector`（canonical = `scripts/governance/d3_metadata/check_vocab_hardcode.py`）。新 AI 创建词表加载器或硬编码检测器前，CapabilityLookup 会反查阻止重复造轮子。
- **pre-commit hook id 唯一性门禁**（GATE-ID-UNIQ）→ 历史教训：commit a09e510ec6 中两个 SSoT 门禁同用 `id: gate-ssot`，后者覆盖前者导致 `src/zephyr/*.py` 检测静默失效。已加自动化门禁防止未来 AI 再造重复 id：
  - **pre-commit 阻断层**：[`.pre-commit-config.yaml` L209-224](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L209-L224) `id: gate-id-uniq`，改 `.pre-commit-config.yaml` 时自动触发 [`check_precommit_id_uniqueness.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py) 扫描所有 `repos[].hooks[].id`，same-repo 重复 → hard block (exit 1)，cross-repo 重复 → warn。
  - **post-commit 兜底层**（治本改进点2）：[`reconciliation_registry.py` `make_precommit_id_uniqueness_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) priority=250，`--no-verify` 绕过 pre-commit 后，commit `.pre-commit-config.yaml` 时自动重校，违规报告落盘 `.runtime/reconcile_reports/id_uniqueness_<ts>.json`（非阻断，供追责）。
  - **capability 反查**已登记 `precommit_id_uniqueness_check`（canonical = `scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py`）。新 AI 想做"检测 yaml id 唯一性"前，CapabilityLookup 会反查到本脚本，提示"扩展本脚本（加 `--target` 参数），勿新建 checker"。
  - **脚本自篡改纵深防御**（A+C 双层，治脚本自篡改缺口）：检测脚本（如 `check_precommit_id_uniqueness.py`）的检测逻辑被 AI 直接删改时，pre-commit hook 和 reconciler 共用同一脚本，两层防线同时失效。本防御补此缺口：
    - **A 层（已废弃，AD-001 阶段3 删除）**：原 `_check_protected_script_integrity` 在 commit 前用 AST 校验受保护脚本锚点。2026-06-30 commit `cde1255c`（AD-001 阶段3 瘦身）批量删除 12 个 `_check_*` 时误删此方法（附带损害——它既是业务检查应迁移到注册制 gate，又是元校验机制保护检查本身不被篡改，不应删除）。[`capability_canonical_file_registry.yaml` `integrity_anchors`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) 字段当前无代码消费者（死数据，仅保留 4 个仍存在的方法 anchor 供未来参考）。**不复活 A 层**（违反向内收原则，只防误删不防故意绕过，测试是更好的误删防线）。脚本篡改检测现仅靠 C 层（pre-commit hook，被 gateway `--no-verify` 绕过）+ CI 层（GitHub Actions，事后兜底）。
    - **C 层（兜底）**：[`.pre-commit-config.yaml` `gate-rules-integrity`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) pre-commit 钩子，改 `AGENTS.md` 或 `scripts/governance/` 下文件时触发 [`validate_rules_integrity.py --check`](file:///d:/ZephyrAlpha/scripts/governance/meta/validate_rules_integrity.py) golden hash 校验（exit 2 硬阻断）。覆盖不走 gateway 的裸 commit 路径 + 检测"保留锚点名但篡改内部逻辑"的精细攻击。受保护文件清单：`RULES_MANIFEST`（validate_rules_integrity.py 内声明）。**基线自动同步**（红蓝发现1 治本）：`rules_integrity_db.json` 不被 git 跟踪，合法 commit 修改 RULES_MANIFEST 文件后基线不自动更新 → `--check` 误报 TAMPERED 阻断裸 commit。已加 [`make_integrity_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（AD-GOV-001 合并后含原 rules_integrity 功能，priority=800）post-commit 自动 `--register` 重注册基线（trigger 总是触发——第一性原理：--register 仅 hash RULES_MANIFEST 文件，毫秒级，不值得为省此开销引入路径假设；RULES_MANIFEST 真源在 validate_rules_integrity.py 内）。重注册的基线基于 git HEAD（见下条 register 基于 git HEAD），消除 WIP 篡改合法化风险。
    - **register 基于 git HEAD**（红蓝发现3 治本）：原 `register()` 基于工作树状态（`_hash_file`）注册基线——攻击者篡改受保护脚本后 commit 无关文件，post-commit `--register` 会把 WIP 篡改注册为新基线（合法化篡改）。已改为基于 `git show HEAD:<path>` hash（[`_hash_git_head`](file:///d:/ZephyrAlpha/scripts/governance/meta/validate_rules_integrity.py)），只注册已 commit 的 HEAD 状态；工作树 WIP 篡改不进基线。`check()` 仍用 `_hash_file` 基于工作树状态（检测 WIP 篡改）。新文件不在 git HEAD 时回退 `_hash_file`。
    - **--register 门禁**（红蓝发现4 治本）：`--register` 重置基线 = 合法化当前状态，是危险操作。原无门禁，可手动任意重置（合法化篡改）。已加环境变量门禁：`ZEPHYR_RECONCILER_MODE=1`（对标 `ZEPHYR_COMMIT_GATEWAY=1` 模式）。只有 [`make_integrity_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（AD-GOV-001 合并后含原 rules_integrity 功能）内部 `_reconcile_rules_integrity` 闭包调用时设置此令牌才允许 `--register`（元问题4治本后内联，无 `_make_old_*` 私有函数）；手动 `python validate_rules_integrity.py --register` 不设置 → `sys.exit(1)` 阻断。
    - **残留缺口（诚实记录）**：自指悖论——gateway 本身能被改，但改 gateway 触发 `gate-triple-align`/`gate-reg-bl` 等门禁且 `[SAFETY] M` 受保护；validate_rules_integrity.py 自身可被改，但它不在自身 RULES_MANIFEST 内（避免自指死锁）。这是可接受的架构权衡，非彻底治本。
    - **capability 反查**：`integrity_anchors` 字段在 `precommit_id_uniqueness_check` 能力条目下声明（注：A 层已废弃后 integrity_anchors 为死数据，保留供未来复活参考）。新增受保护脚本时：①`validate_rules_integrity.py` `RULES_MANIFEST` 加条目 ②YAML `integrity_anchors` + `canonical_override` 同步声明（供未来 A 层复活时直接复用）。

- **目录契约门禁**（GATE-DIRECTORY-CONTRACT）→ 文件放错目录 = AI 找不到 + 真源散落 + 规则无法自动执行。已加自动化门禁强制文件目录归属合规：
  - **pre-commit 阻断层**：[`.pre-commit-config.yaml` L411-434](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L411-L434) `id: gate-directory-contract`，每次 `git commit` 自动触发，`--staged` 模式只校验暂存文件，`--ci` 硬阻断（exit 1 拒绝提交）。
  - **真源**：[`directory_contract.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml)（目录维度约束唯一真源：directory_zones + directory_extensions + root_directory_whitelist）+ [`doc_type_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml)（doc_type 的 allowed/forbidden_directories 真源）。消费者动态加载，路径变更只需改契约一处。
  - **检测内容**（DCR-001~007 全部已启用）：DCR-001 doc_type 的 allowed_directories 包含文件所在目录（error）；DCR-002 forbidden_directories 不包含文件所在目录（error）；DCR-003 永久区 .md 文件 ttl==permanent（error）；DCR-004 临时区 ttl==task_bound（warning）；DCR-005 扩展名在目录的 allowed 清单内（error）；DCR-006 扩展名不在 forbidden 清单内（error）；DCR-007 根目录文件在白名单内（error）。
  - **豁免区**（DCR-001/002 跳过）：`docs/_working/`（临时区）、`docs/_archive/`（归档区）、`.runtime/`（运行时归档区）、`.trae/`（IDE 工具区）、`docs/01_policies_and_standards/templates/`（模板区 TMP-EX-001——模板是 Class Definition，cookbook template 的 doc_type 取目标类型，不受目标类型的 allowed_directories 约束）。
  - **capability 反查**：已登记 `directory_contract_checker`（canonical = `scripts/governance/d1_structure/check_directory_contract.py`，aliases 含 `DCR_checker`/`directory_contract_validation`）。新 AI 想做"文件目录校验/目录归属检查"前，CapabilityLookup 会反查到本脚本，提示"扩展本脚本（加 DCR 规则），勿新建 checker"。
  - **新 AI 必读**：创建新文件前，先查 doc_type_vocabulary.yaml 的 allowed_directories 确认目标目录合法。违反将被 DCR-001 在 commit 时阻断——不是"建议"，是硬约束。
- **并发 session 文件冲突防护门禁**（HELD-OVERLAP + CLAIM-REQUIRED，2026-06-30 治本）→ 多 session 并发开发时，session A 修改的文件可能被 session B 的 commit 覆盖（回退）。两层门禁防护：
  - **CLAIM-REQUIRED**（阻断）：[`claim_required_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/claim_required_gate.py) priority=40。已注册 session commit 前必须先 `claim_files` 声明目标文件，未 claim → `CLAIM_REQUIRED_VIOLATION` 阻断。逃生通道：`--allow-overlap` 参数放行（特殊情况）。病根：不 claim 可绕过 HELD-OVERLAP（未声明 held_files 则无比对基准）。
  - **HELD-OVERLAP**（阻断）：[`held_overlap_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/held_overlap_gate.py) priority=50。commit 中包含其他 session held（claim）的文件 → 阻断。防搭便车覆盖。
  - **capability 反查**：两者均已登记 `capability_canonical_file_registry.yaml`（`claim_required_gate` + `held_overlap_gate`）。新 AI 想做"文件冲突防护/file claim"前，CapabilityLookup 会反查阻止重复造轮子。

- **新建 .py/.yaml CapabilityLookup 提示门禁**（CAPABILITY-OVERLAP，warn-only，2026-06-30 治本）→ commit 时 [`capability_overlap_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/capability_overlap_gate.py) priority=200 自动检测：①新建 .py 文件名是否与 `capability_canonical_file_registry.yaml` 已注册能力 aliases token 重叠 ②`_registry/` 下新增 .yaml/.yml 文件名是否与同目录现有 yaml token 重叠（≥2 token = 高置信度第二真源）。命中则 `logger.warning` 告警（**不阻断**）——文件名匹配是启发式，AI 看到 warning 后自行判断是扩展还是新建。检测范围覆盖 `_registry/` 所有子目录（contracts/vocabularies/catalogs/schemas/ + 未来新增），不硬编码子目录列表。病根：AGENTS.md §7 把"查 CapabilityLookup"列为 step 0，但仅靠文档约定——新 AI 跳过 AGENTS.md 即可重复造轮子，本 gate 补上代码层兜底。**capability 反查**已登记 `capability_overlap_gate`。新 AI 想做"重复造轮子检测/second source yaml"前，CapabilityLookup 会反查阻止重复造轮子。

- **post-commit 规则文件审计+ARCH引用查重 reconciler**（GATE-RULE-AUDIT + GATE-EXEMPT-ZONE-FM，warn-only，2026-06-30 治本 + 元问题2治本）→ 修改 5 个规则文件（directory_contract.yaml / doc_type_vocabulary.yaml / node_type_vocabulary.yaml / capability_canonical_file_registry.yaml / layer_vocabulary.yaml）会触发 `GATE-RULE-AUDIT`（[`reconciliation_registry.py` `make_rule_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) priority=710，3-way compose），落盘审计报告到 `.runtime/reconcile_reports/rule_file_audit_*.json`。**GATE-ARCH-REFS（priority=710，元问题2治本 2026-06-30）**扫描 committed_files 中所有 `#ARCH-XXX` 引用，检查是否在 [`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 的 `entries` 中有对应条目——病根：注册表铁律#6"任何 #ARCH-XXX 引用必须在本注册表有对应条目，禁止 grep-and-claim 占位"是君子协定，无技术强制（#ARCH-027 冲突就是 AI 占位而不查重导致）。检测到未登记的 `#ARCH-XXX` 引用→warn（非阻断，detail 列出未登记编号）。单独提交豁免区（`docs/_working/`等）下带 frontmatter 的文件会触发 `GATE-EXEMPT-ZONE-FM`（`make_exempt_zone_frontmatter_reconciler` priority=710），检测本应放正式目录却被塞进豁免区的文件。三者均 warn-only（不阻断），报告供人工审查。

- **文档引用完整性门禁**（GATE-FRONTMATTER/DOC-REF 子项）→ 调研发现 AI 在 .md/.csv/.yaml 中编造虚假文件引用（如 dom_gov_001 虚假审计闭环：index.md 列 22 张不存在的任务卡，move_plan.csv 引用 4 个不存在的文件）。已加自动化门禁防止未来 AI 再造虚假引用：
  - **pre-commit 阻断层**：[`.pre-commit-config.yaml` L244-260](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L244-L260) `id: gate-frontmatter`（DOC-REF 子项，run_gate_chain 第4步），staged 的 .md/.csv/.yaml/.json 文件触发 [`audit_broken_links.py`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 扫描 markdown 链接 + 纯文本路径 + CSV 列值 + YAML 值 + frontmatter blueprint_id + index.md 清单 + audit_report 审计对象，`--ci` 硬阻断 + `--check-new` 历史豁免（仅阻断本次修改新引入的断链，对比 HEAD 版本，参考 N-16 模式）。
  - **检测范围**：.md（markdown 链接 + 纯文本路径 + frontmatter blueprint_id + index.md 清单 + audit_report 审计对象）/ .csv（列值路径）/ .yaml/.yml（值路径 + 纯文本）/ .json（纯文本路径）。跳过 http/https/ftp/mailto 锚点 URL。
  - **路径解析**：三重尝试——①先相对于文件目录（markdown 链接习惯）②再相对于项目根（CSV/YAML 项目根相对路径）③basename 全局搜索兜底（裸文件名如 blueprint.md 在项目其他目录存在）。注意：index.md 清单检测**禁用 basename 兜底**（本目录契约语义，兜底会掩盖幻觉）。
  - **capability 反查**已登记 `broken_link_detector`（canonical = `scripts/governance/d2_links/audit_broken_links.py`）。新 AI 想做"断链检测/ghost ref/phantom reference"前，CapabilityLookup 会反查到本脚本，提示"扩展本脚本（加提取器函数），勿新建 checker"。
  - **治本 GAP-1**：解决"非 .md 文件（.csv/.yaml/.json）中的路径引用无检测"防护缺口。真源：[`audit_broken_links.py` `_extract_csv_paths`/`_extract_text_paths`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。
  - **治本 GAP-2**：解决"frontmatter.blueprint_id 引用的蓝图是否存在无检测"防护缺口。检测 .md frontmatter 的 blueprint_id 字段值是否在 [`blueprint_registry.yaml`](file:///d:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml) 中存在。空值跳过（合法，如 index.md 无归属蓝图）；格式非法跳过（交给 GATE-NAMING N-06 三轨制格式校验）。真源：[`audit_broken_links.py` `_check_blueprint_id_exists`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。
  - **治本 GAP-3**：解决"index.md 列出的文件清单是否存在无检测"防护缺口。对名为 index.md 的文件做**严格本地解析**（仅相对 source.parent，禁 basename 兜底——本目录契约语义）。处理 markdown 链接 + `file:///D:/ZephyrAlpha/...` 绝对 URL 两种格式。真源：[`audit_broken_links.py` `_check_index_md_inventory`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。
  - **治本 GAP-4**：解决"audit_report 审计对象存在性无检测"防护缺口。对 doc_type=audit_report 的 .md 文件，校验三类引用：①frontmatter.blueprint_id ②frontmatter.module_id ③正文 MODULE_ID 匹配（MOD-XXX-NNN/D-XXX-NNN/SH-XXX-NNN 三轨制）。自动生成 audit_report（无 blueprint_id 无 module_id）跳过。真源：[`audit_broken_links.py` `_check_audit_report_objects`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。已检出幻觉：ai_12/17/18_report.md 引用不存在的 `MOD-DB_DEPGRAPH_PG`/`MOD-INF`。

- **tests/ 目录组织规范（向内收防回归，[#ARCH-029](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 治本）**——病根：tests/ 根曾平铺 1699 个 test_*.py（新 AI 无法定位 + 无分类指引），子目录粒度混合维度（unit/integration/e2e 按测试类型 vs governance/llm_security 按功能域 vs contract/contracts 按测试种类），contract/ 与 contracts/ 单复数歧义并存。治本约定（文档化防回归，无硬门禁——AD-GOV-001 收敛期不新增 gate）：
  - **单一维度=功能域**：tests/ 子目录按功能域归类（a2a/skill/trae_rules/kb/governance/llm_security/...），不混入测试类型维度（unit/integration/e2e）。新测试文件按文件名前缀归对应功能域子目录。
  - **根目录禁平铺**：tests/ 根目录禁止新增 test_*.py 平铺文件（根目录仅允许 conftest.py/__init__.py 等基础文件）。新增 test_*.py MUST 归功能域子目录。
  - **contracts/ 唯一**：契约测试唯一目录为 `contracts/`（单复数歧义已消除——原 `contract/` 元测试 5 文件已合并入 `contracts/_meta/`）。禁止再造 `contract/` 单数目录。
  - **目录名禁 test_ 前缀**：tests/ 下子目录名禁止 `test_` 前缀（`test_code_dedup_engine/` 已改名 `code_dedup_engine/`）。`test_` 前缀只用于文件名。
  - **迁移状态**：ARCH-029 全部治本完成——1699/1699 文件已迁移（100%），tests/ 根目录扁平 test_*.py 清零，84 个功能域子目录。session3 路线B 全量治本：批次1 commit 6fc3c755（471文件 governance/feedback/audit/llm_security）；批次2 commit 218a870a（291文件 34个子目录）。分类方法：AST import 自动匹配 533 + AI 语义分析 229（BLUEPRINT 优先）。维度混合清理（session4）：批次1 commit 556a845c 消除 6 个测试类型维度目录（integration/e2e/adversarial/red_blue/benchmarks/performance，96文件）；批次2+3 commit b25d9a46 消除 unit/ 目录（25子目录合并+132平铺文件分类迁移，548文件）。至此 tests/ 下 7 个测试类型维度目录全部消除，全部按功能域归类。漂移源 `validate_test_directory_structure.py` 与本条冲突+虚假引用 GOV-DOC-002，已删除（session3 commit）。
  - **强制方式**：文档约定（本条目）+ code review + **GATE-NO-TESTS-UNIT 硬阻断门禁**。
  - **自动化 guard**（ARCH-029 漂移种子防复发，2026-07-01 添加）：[`.pre-commit-config.yaml` L664-686](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L664-L686) `id: gate-no-tests-unit`，pygrep hook 检测活跃代码/文档中 `tests/unit/` 旧路径重引入，检测到即 exit 1 拒绝提交。豁免：`_archive/`、`scripts/_archive/`、`scripts/.*/_archive/`、`session_logs/`、`data/`、`reports/`、历史规则文件(`trae_028/034`)、`.pre-commit-config.yaml`、`AGENTS.md` 自身（文档真源需描述旧路径）。每次 `git commit` 自动触发，无需手工干预。治本依据：并发 session 不知情回退已修复文件（commit 021c2274 后被回退为 tests/unit/），证明无 guard 时漂移会重新发生。

## 8. 永远不要做的事

> 完整禁止清单见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) 四条铁律。此处仅列项目宪法级禁令：

- 不要删除 `data/` 下的任何文件
- **数据真源唯一位置（data/ 目录，src/ 禁 data/ 子目录）**：`data/` 是运行态数据（brain passport / audit_logs / telemetry / capability_cards 等）唯一合法存放位置。**禁止在 `src/` 下创建 `data/` 子目录**——双真源漂移根因（历史教训：`src/data/brain/passports/` 与 `data/brain/passports/` 并存导致版本漂移，2026-06-27 清理 commit 36871193）。规则真源见 [trae_047 §gov_eng_002_directory_mapping](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml) 禁止规则；pre-commit 钩子 [`gate-src-no-data`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_src_no_data.py) 自动检测 staged 文件 `src/data/` 路径前缀，`--ci` 硬阻断；原 GitCommitGateway 内部 `_check_src_no_data` 等效校验（已废弃，AD-001 阶段3 删除，2026-06-30 commit `cde1255c`），现 gateway 路径下 src/data/ 检测失效（靠 pre-commit gate-src-no-data + CI 兜底）。
- **文件清理操作规范（禁止只删工作区不 git rm）**：删除文件时必须用 `git rm <file>` 或通过 [`GitCommitGateway --files <deleted_file>`](file:///d:/ZephyrAlpha/scripts/git_commit.py) 提交删除——**禁止只 `rm`/`del` 工作区文件而不 git rm**（会产生 D 悬空文件污染 git status，历史教训：2026-06-27 清理 51 个 D 悬空文件 commit efc2d03b/5f2835bb）。正确流程：`git rm <file>` → GitCommitGateway 提交；或直接 `GitCommitGateway --files <file>` 传 D 状态文件（gateway 第 112-131 行识别 D 场景放行）。
- **临时文件命名规范（_tmp_/_debug_ 前缀 + 用完即删）**：一次性脚本必须用 `_tmp_` 前缀（如 `scripts/_tmp_scan.py`），调试测试必须用 `_debug_` 前缀（如 `tests/_debug_race.py`），任务完成后立即删除。**禁止创建 .bak/.baseline/.backup 备份文件**——用 `git stash`/`git diff` 替代。GATE-ZR [`detect_temp_files.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/detect_temp_files.py) 自动检测 `_tmp_`/`_debug_`/`.bak`/`.baseline` 等模式，`error` 级别硬阻断（`is_clean=False` 拒绝提交）。
- 不要跳过 `CapabilityRegistry.register()`
- 不要修改 `AiAuditLogger` 的已有日志
- 不要创建新模块而不注册到大脑
- **reconciler auto-commit 统一入口（2026-06-30 红蓝对抗治本修订）**：7 个 reconciler（manifest/rule_catalog/registry_index/working_docs/domain_doc/arch_model/vocab_change）的 auto-commit 统一经 [`_commit_auto()`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py)，禁止裸调 [`_run_git(["git","commit",...])`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py)。**DCR gate 真源复用**：`_commit_auto` 通过 `gate_registry.get("DIRECTORY-CONTRACT")` 获取已注册 GateSpec，调其 check 方法对 reconciler 提交的文件跑 DCR 等效校验（真源唯一在 [directory_contract_gate.py](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/directory_contract_gate.py) → [check_directory_contract.py](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py)），不复制检测逻辑。**只跑 DCR gate + TTL-METADATA gate**（不触发全部 gate，避免 CLAIM-REQUIRED/HELD-OVERLAP 等对 reconciler 无意义的 gate 误阻断）；**ttl 校验靠 TTL-METADATA gate**（gateway 内置，同 DCR gate 的 `gate_registry.get("TTL-METADATA")` 复用模式，subprocess 调 check_frontmatter_metadata.py 真源，见上方"TTL 校验统一拦截点"）。**arch_model reconciler 特例**：双树合并（2026-06-30）已完成，`_ARCH_MODEL_INDEX` 已指向根树 `architecture_model/index.yaml`，DCR gate 不再触发 NAMING_VIOLATION（保留 warn 降级作为防御纵深）。**新增 gate 同步评估**：新增 pre-commit gate 时 MUST 评估 `_commit_auto` 是否需要同步——新增 gate 若涉及机器生成文件的安全约束（如目录/扩展名/内容校验），MUST 在 `_commit_auto` 中同步加入（对标 DCR gate 的 `gate_registry.get` 复用模式）；若 gate 仅对人工提交有意义（如 claim/overlap/promote），则不同步（`_commit_auto` 无 session claim 语义）。判断标准：reconciler 是否会提交该 gate 关心的文件？
- **GitCommitGateway 僵尸锁自愈**：全局锁 `_GlobalCommitLock` 获取前先调 [`is_pid_alive(pid)`](file:///d:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py) 检查持有进程存活——进程崩溃时锁文件残留，PID 已死则立即清理（零窗口期），不靠 TTL 30min 过期。`is_pid_alive` 真源唯一在 [`process_pool.py`](file:///d:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py)（红蓝对抗归一：曾三处分裂——gateway/ide_health_service/_concurrency 各自定义，现统一；语义最匹配：与 PooledProcess.is_alive / _reap_zombies 同属进程存活检测）。调用方 MUST `from zephyr.shared.infra.process_pool import is_pid_alive`，禁止重复定义（capability_id=process_liveness_detection）。
- **GitCommitGateway 中文 aliases 门禁（已废弃，AD-001 阶段3 删除）**：原 gateway 内嵌 `_check_capability_aliases` 检测 `capability_canonical_file_registry.yaml` 的 aliases 是否含 CJK 字符。2026-06-30 commit `cde1255c` 批量删除 12 个 `_check_*` 时删除此方法，**未迁移到注册制 gate**（[`capability_overlap_gate`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/capability_overlap_gate.py) 只做文件名 token 重叠检测，不查 CJK）。现 CJK alias 约束仅靠 [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) 头部注释文档约定 + code review。
- **GitCommitGateway REPO_ROOT 门禁（已废弃，AD-001 阶段3 删除）**：原 gateway 内嵌 `_check_repo_root_usage` 检测 `.py` 文件两类违规——① `parents[N]` 反模式；② AST 检测 missing import（`REPO_ROOT`/`DB_PATH`/`find_repo_root` 使用但未 import）。2026-06-30 commit `cde1255c` 批量删除 12 个 `_check_*` 时删除此方法，**未迁移到注册制 gate**。现 REPO_ROOT 违规检测仅靠 pre-commit hook GATE-DD07（warn-only，被 gateway `--no-verify` 绕过）+ CI 兜底。REPO_ROOT 真源归一约定见 §7。
- **GitCommitGateway rename fallback（方案 A 治本，红蓝审核 v2 内迁）**：[`_commit_with_file_message`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 是 commit 唯一真源入口，内置 rename 检测（[`_has_staged_renames`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py)）+ staged 验证（[`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py)）。根因：`git commit --pathspec-from-file` 对 staged rename（R100）拆分为独立 add+delete，只提交 pathspec 匹配部分，破坏 rename。治本：pathspec 为默认（多 session 安全，pathspec 限制范围不捡拾其他 session WIP），检测到目标文件有 rename 时自动切换无 pathspec 模式 + staged 验证（防误提交其他 session WIP）。rename 检测逻辑内迁到 `_commit_with_file_message`（红蓝审核 v2 治本），`_commit_locked` 和 `_commit_auto` 无需重复调用 `_has_staged_renames`，reconciler 路径自动获得 rename 保护（原 `_commit_auto` 无 rename 保护是漏洞）。`_collect_non_target_rel` 已修复 rename 格式 `R old -> new` 的路径解析（提取新路径），确保其他 session 的 staged rename 能被正确 stash。**staging 区自动清理（ARCH-038 治本，2026-07-01）**：无 pathspec 模式下 `_verify_staged_is_clean` 检查失败时（staging 区有并发 session 污染的非目标文件），不再直接拒绝 commit，而是由 [`_unstage_non_target_files`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 自动 `git reset HEAD -- <非目标文件>` 清理后重新验证，通过则继续 commit。此前需调用方手动 unstage（反复出现 commit 卡死）。回归测试 [`test_rename_with_dirty_staged_auto_unstage`](file:///d:/ZephyrAlpha/tests/git/test_git_commit_gateway.py)。
- **GitCommitGateway staged delete 保护（gitignored 文件 no-pathspec commit，5 层纵深防御）**：[`_commit_locked`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 当目标含 gitignored 文件时（`len(normal_files) < len(files)`）传 `None` 作为 pathspec，用 no-pathspec commit。根因：`git commit -- <pathspec>` 提交**工作区状态**而非**暂存区状态**——对 gitignored 文件，工作区状态无法被 stage（gitignore 阻止），staged delete（`git rm --cached`）被静默跳过。历史教训：commit `32ead90e` 漏提交 5 个 egg_info 删除（staged delete 被吞，只提交了 3 个修改文件）。5 层纵深防御：① [`_is_staged_delete`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 显式识别 staged delete 状态（不在 index AND 在 HEAD），[`_stage_gitignored_tracked`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) existing 分支跳过此类文件，防 `git add -f` 撤销用户的 staged delete；② [`_should_use_no_pathspec`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 检测目标含 gitignored 文件时返回 True，[`_commit_locked`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 据此切换 no-pathspec commit + [`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 验证 staged 区只有目标文件（防误提交其他 session WIP）；③ [`_collect_non_target_rel`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) + [`_stash_other_files`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) + [`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 用 `os.path.normcase()` 大小写不敏感匹配——`Path.resolve()` 在文件不存在磁盘时无法归一化大小写，导致 staged delete 文件被误判为非目标 → 被 stash 走（Windows 大小写不敏感必须用 normcase）。回归测试 [`TestStagedDeleteGitignored`](file:///d:/ZephyrAlpha/tests/test_git_commit_gateway.py)。新 AI 勿误判 no-pathspec 分支或 `_is_staged_delete` 为冗余删掉——pathspec commit 对 gitignored staged delete 静默丢失是已验证 bug。
- **GATE-COMMIT-GW 裸 commit 检测门禁（OPS-2026062513 治本，RB-6 修复 2026-06-29）**：[`validate_commit_gateway.py`](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/validate_commit_gateway.py) 是 pre-commit hook（`.pre-commit-config.yaml` gate-commit-gw，`always_run: true`），强制所有 commit 走 GitCommitGateway。**检测逻辑（红蓝修复后）**：hook 运行本身=裸 commit（gateway 用 `--no-verify` 绕过 hook）→ 阻断 exit 1；合并提交（`.git/MERGE_HEAD` 存在）放行。**废除的旧逻辑**：env var `ZEPHYR_COMMIT_GATEWAY=1` 检查（RB-2：env var 在 shell 中持久存在，可绕过）和 commit message `[GW:...]` 标记检查（RB-6：伪造标记可绕过）。**唯一合法绕过**：`git commit --no-verify`（conscious bypass，由 GATE-INTEGRITY-AUDIT 审计 reconciler 追踪）。**纵深防御**：① 本 hook 拦截非 `--no-verify` 路径 ② post-commit 审计 reconciler 扫描最近 20 个 commit，标记无 `[GW:]` 的裸 commit ③ 过程纪律（code review）。
- **GATE-INTEGRITY-AUDIT post-commit 审计+引用检测 reconciler（含原 COMMIT-GW-AUDIT + 新增 AGENTS-MD-REFS，C级 缺口4 + 元问题1治本）**：[`make_integrity_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（priority=810）3-way compose 合并三个检测：① GATE-RULES-INTEGRITY（priority=270）重注册 rules_integrity 基线 ② GATE-COMMIT-GW-AUDIT（priority=800）审计最近 20 个 commit 标记无 `[GW:` 标记的裸 commit（merge commit 跳过），报告落盘 `.runtime/reconcile_reports/commit_gateway_audit_<ts>.json` ③ **GATE-AGENTS-MD-REFS（priority=810，元问题1治本 2026-06-30）**检测 AGENTS.md 中引用的 `make_*_reconciler` 公共函数名是否在 `reconciliation_registry.__all__` 中——病根：AGENTS.md 硬编码函数名，reconciler 重命名/合并后 AGENTS.md 不会自动更新，新AI按失效指引造幻觉（如步骤1修复的 `_make_old_rules_integrity_reconciler` 失效引用）。检测到失效引用→warn（非阻断，detail 列出失效函数名供人工修正）。trigger：AGENTS.md 或 reconciliation_registry.py 变更时触发。非阻断（warn），供追责与修正。
- **AD-GOV-001 reconciler 合并策略（compose，2026-06-30 治理收敛）**：5 组职能重叠的 reconciler 已通过 [`_compose_reconcilers`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) 合并为 5 个新入口（16→11）。**compose 规则**：① trigger = 所有 spec trigger 的 OR（任一命中即执行）② reconcile = 串联执行全部 spec（按传入顺序），action 取较严重（severity: skip=0/clean=1/warn=2/auto_committed=2），detail 平铺拼接 ③ priority = max(所有 spec)。**`_compose_reconcilers` 支持 `*specs` 可变参数**（元问题1治本扩展 2026-06-30：原签名只支持 2 个 spec，GATE-INTEGRITY-AUDIT 3-way 合并需可变参数；向后兼容 2 参数，5 个现有调用点零回归）。**合并映射**：GATE-GHOST+GATE-WORKING-DOCS→GATE-DELETE-AUDIT；GATE-DOMAIN-DOC+GATE-ARCH-MODEL→GATE-REGENERATE；GATE-RULE-CATALOG+GATE-RULE-FILE-AUDIT→GATE-RULE-AUDIT；GATE-REGISTRY-INDEX+GATE-BASELINE-AWARE→GATE-REGISTRY-SYNC；GATE-RULES-INTEGRITY+GATE-COMMIT-GW-AUDIT+GATE-AGENTS-MD-REFS→GATE-INTEGRITY-AUDIT（3-way，元问题1治本）。**`_make_old_*` 私有函数已删除（2026-06-30 元问题4治本）**：原 `_make_old_*_reconciler` 私有函数已删除，reconcile 逻辑内联到 5 个 `make_*` compose 包装函数闭包中（Python 无真私有，保留等于留可 import 的绕过入口；内联后仅在闭包内可见）。测试规范见 [`test_integrity_audit_reconciler.py`](file:///d:/ZephyrAlpha/tests/governance/audit/test_integrity_audit_reconciler.py)——用公共 API + mock spec + 模块级函数 `_audit_commit_history` 测试。**AD-GOV-001 收敛期约束**：新增 reconciler 前 MUST 过 [trae_060 §4](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml) 元问题审查（该不该存在/能否合并进已有），教训登记 [#ARCH-028](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)。
- **废弃目录门禁 GATE-DEPRECATED-DIR（09_audit 治本加固，红蓝对抗修复）**：双层防御（①② 层均已于 2026-06-30 修复）——① [`directory_contract_gate`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/directory_contract_gate.py)（priority=30，注册制 gate）通过 subprocess 调用 [`check_directory_contract.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py)，`scan_files` 调用 [`check_deprecated_directory`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py) 检测提交文件是否位于 [`directory_contract.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml) §7 `deprecated_directories` 字段声明的废弃目录（当前含 `docs/09_audit/`），命中则阻断——gateway 内嵌注册制 gate，`--no-verify` 绕不过（2026-06-30 补全：原 `_check_deprecated_directories` 在 AD-001 阶段3 删除后 `scan_files` 漏检 deprecated_directories，新增 `check_deprecated_directory` 函数修复）；② [`make_deprecated_directory_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（priority=600）post-commit **自动修复**（2026-06-30 治本：从 directory_contract.yaml §7 `deprecated_directories` 字段动态加载）：检测到废弃目录存在时自动迁移文件到 `docs/_working/audit/` + 删除空目录。报告落盘 `.runtime/reconcile_reports/deprecated_directory_<ts>.json`。
- **审计产物路径引导（09_audit 治本，新 AI 必读）**：审计报告 / session handoff / 安全 finding / 红蓝对抗报告等审计产物**统一写入 `docs/_working/audit/`**（子目录：`handoff/`、`findings/`、`reports/`、`STATE/`）。**禁止 `docs/09_audit/`**——该目录已合并入 `docs/_working/audit/`（[trae_047 gov_eng_002_directory_mapping](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml#L154)）。`doc_type_vocabulary.yaml` 中 `audit_report` 的 `allowed_directories: ["_working/audit/"]`。新 AI 创建审计产物时按此路径引导，违反将被 GATE-DEPRECATED-DIR 阻断。
- **禁止手工创建 YAML tracker（漂移源治本，2026-06-29）**：禁止在 `docs/03_modules/` 下手工创建 `*_tracker.yaml`/`*_matrix.yaml`/`phase_plan.yaml`/`a2a_anomaly.yaml`/`adversarial_test_report.yaml`/`decomposition_completeness.yaml` 等过程态 YAML 文件——这些是漂移源和孤儿，违反真源唯一 + 向内收原则（tra_060）。**真源已在别处**：① 架构数据真源在 [`depgraph`](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py) PostgreSQL 数据库（通过 `apply_depgraph.py` 修改）② 模块版本真源在蓝图 frontmatter `version` 字段 ③ Python 模块状态真源在代码本身（如 `anomaly_detector.py` 是 canonical）④ 决策记录真源在 `git log` + `data/audit_logs/`。**历史教训**：2026-06-29 删除 11 个漂移/孤儿 YAML（commit `0f8fbe21`），它们用 `# ttl: permanent` 注释锚定（非 frontmatter）自欺永久，实际 0 代码消费 0 蓝图注册，内容与 depgraph/蓝图矛盾（如 `version_tracker.yaml` 声明 V1-V40 实际 V1-V5、`blind_spot_tracker.yaml` 157 vs 183 矛盾）。**注释锚定 ≠ frontmatter**：`# ttl: permanent` 注释不受 GATE-FRONTMATTER（[`check_frontmatter_metadata.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py)）校验保护——GATE-FRONTMATTER 解析 frontmatter `ttl:` 字段（YAML frontmatter / .py 头部 `# [TTL]` 字段），不解析散文注释 `# ttl:`，只有 frontmatter `ttl:` 字段才受校验。**新 AI 引导**：如需追踪过程态，扩展已有 Python 模块（向内收）或写入 `docs/_working/`（task_bound，`completes_when` 声明完成条件后自动归档），禁止创建手工 YAML tracker。
- **治本变更未提交前禁止并发 AI 对话（搭便车治本 codify，2026-06-30）**：治本变更（refactor/fix 涉及多文件）在工作区有未提交 WIP 时，禁止开启并发 AI 对话处理同文件——GitCommitGateway 文件级隔离无法分离同一文件内两个 session 的行级修改，后提交的 session 会把工作区全部修改（含前一个 session WIP）一并提交（"搭便车提交"/ghost commit），导致 commit message 与实际内容不符、回滚连带、审计断裂。**历史教训**：commit `abea0b219c`（GATE-ARCH-MODEL）搭便车带入模式6 代码。约束真源见 [parallel_session_coordination_policy.md §3.2](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md) 治本原理。
- **工作区回退风险（编辑阶段覆盖，2026-06-30 Phase D 治本指针）**：≥2 session 并发时，AI 用 IDE Edit/Write 工具直接编辑共享工作区文件——若 session A 已 commit `foo.py`，session B 的 Edit/Write 工具用旧版本覆盖 `foo.py` 工作区副本，session B 下次 commit 会带回退版本（"工作区回退事故"）。**根因**：AI 工具链不读 HEAD 比对，盲目覆盖磁盘。**Edit/Write 覆盖无法代码层治本**（IDE 工具不能 hook，Edit/Write 工作区固定为项目根，worktree 对 Edit/Write 不适用——但 worktree 对 RunCommand 操作适用，见下条 FP-ISO.4C 治本方案）。**治本路径**：≥2 session 并发时 MUST 走 StagingArea 草稿模式（[project_rules.md 多 AI 并发提交协议](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) L161-187，[onboarding_detail.md 模式 B](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)），禁止共享工作区直接 Edit/Write。**取消 B2（workspace_drift_reconciler）裁定**：post-commit reconciler 治不了编辑阶段回退（reconciler 在 commit 后触发，工作区回退发生在 Edit/Write 阶段，检测不到），违反第一性原理，不创造无价值代码（向内收原则①）。**指针**：StagingArea 实现见 [`staging_area.py`](file:///d:/ZephyrAlpha/src/zephyr/trading/staging_area.py)，并发协议见 [`parallel_session_coordination_policy.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md)。
**协议层治本补充（2026-06-30 第29轮调研）**：L301 原裁定"代码层无法治本"成立的前提是 claim 必然在 commit 阶段。调研发现 claim 协议前移到 Edit 前（[`git_commit.py --claim-only`](file:///d:/ZephyrAlpha/scripts/git_commit.py)）+ [`pre_write_gate.py --session`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/pre_write_gate.py) 扩展 session_overlap 检测，可在不违反 AD-GOV-001 下显著降低 Edit 阶段覆盖风险（软约束，依赖 AI 自觉；IDE 不可 hook 是硬上限，无法技术强制）。复用 [`SessionRegistry`](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/session_concurrency.py) 已有 API（`find_session_by_file`/`other_held_files`），零新真源，符合向内收。详见 [project_rules.md RULE-ZERO claim 前移协议](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)。StagingArea 仍为高风险场景的物理隔离兜底。
- **FP-ISO.4C worktree 物理隔离（并发工作丢失治本，2026-07-01，正式规则 2026-07-02 转正）**：41 个并发丢失案例分析结论——Mode A（git stash/reset/checkout 冲掉工作区）占 51%，Mode B（直接编辑同一文件覆盖）占 17%，Mode D（未 commit 被回收）占 7%。**唯一能同时治 A+B+D 的方案是 worktree 物理隔离**：每 AI 对话独占 `.aidrafts/{session_id}/` worktree（独立 git index），从物理层面消除共享工作目录冲突。**AI 对话启动时 MUST 调** [`session_worktree_start`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/session_worktree.py)（返回 `worktree_path`）→ AI 可正常用 Edit/Write 编辑文件（写项目根，`session_worktree_commit` 会自动将改动同步到 worktree）→ 提交调 [`session_worktree_commit`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/session_worktree.py)（自动同步文件项目根→worktree + worktree 内 git add+commit，独立 index 无需 GitCommitGateway，`--no-verify` 绕过 pre-commit hook）→ 完成调 [`session_worktree_merge`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/session_worktree.py)（merge 回主分支 + 清理 worktree）→ 放弃调 [`session_worktree_abort`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/session_worktree.py)（丢弃修改 + 清理）。**GATE-COMMIT-GW 放行**：[`validate_commit_gateway.py`](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/validate_commit_gateway.py) 检测 cwd 含 `.aidrafts/sess-` 时放行 worktree 内 commit（授权绕过 GitCommitGateway 全局锁，worktree 独立 index 无共享冲突）。**底层引擎** [`WorktreeManager`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/worktree_manager.py)（create/merge/cleanup + Windows 文件锁兜底 `_force_rmtree`）。**capability 反查**：已登记 `session_worktree_lifecycle`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)），新 AI 想做"并发隔离/worktree"前 CapabilityLookup 会反查到此。**测试**：[`test_session_worktree.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree.py)（6 个端到端测试，连续两遍通过）。**文档**：[blueprint §FP-ISO.4C](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md)。**正式规则状态（2026-07-02 转正）**：Trae IDE 不支持自动触发 worktree（无启动 hook、IDE 不可 hook、AI 不可改 cwd），走君子协定——AI 自觉调 start/commit/merge，对标 AI 自觉查锁。6 连续 PASS 已转正式（Round2-4 + Extreme A/B/C，覆盖 Edit tracked/Write 新文件/文件删除/abort 4 种代码路径，merge 首次成功率 3/3）。文件同步已实现（`session_worktree_commit` 内 `shutil.copy2` 项目根→worktree + 文件删除同步），AI 无需手动同步。**HELD-OVERLAP 加硬（2026-07-02，文件锁与 worktree 一样硬）**：`session_worktree_commit` 新增 `allow_overlap: bool = False` 参数，commit 前对每个文件调 `SessionRegistry.claim_file()`（原子 check-and-claim，内部加锁防 TOCTOU）——被其他活跃 session 持有则 `HELD_OVERLAP_VIOLATION` 硬阻断（回滚已 claim 文件，避免 dangling claim 阻塞其他 session）；未被持有则 claim 成功（session 级，不 per-commit 释放）。claim 在 merge/abort 时 `unregister` 自动释放。对标 GitCommitGateway 的 HELD-OVERLAP gate，使 worktree 模式下的文件锁一样硬。`allow_overlap=True` 逃生通道放行（对标 `--allow-overlap`）。**逃生通道（永久保留，非临时）**：HELD-OVERLAP 加硬消除了"两 session 编辑同一文件"的搭便车根因，但无法解决 git 固有 merge conflict（`allow_overlap=True` 强行覆盖时两分支改同一文件 git 无法自动合并）+ AI commit 后又编辑同一文件导致内容漂移（pre-merge auto-clean 跳过不一致文件）——此时 `session_worktree_abort` + 改用 GitCommitGateway（stash 隔离）作为兜底。测试：`test_worktree_commit_held_overlap_blocks`/`test_worktree_commit_allow_overlap`/`test_worktree_merge_releases_claims`（11/11 PASS）。**pre-merge gate 检查 + reconcile_verify 默认 True（2026-07-04，治本 merge 前 gate 漂移 + post-merge reconciler 缺失）**：[`session_worktree_merge`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/session_worktree.py) 在 `_pre_merge_auto_clean` 后执行 `_pre_merge_gate_check`——用 `git reset --soft merge-base` 模拟 staged 状态运行 7 个 worktree-compatible gate（跳过 HELD-OVERLAP/CLAIM-REQUIRED，捕获 commit 后到 merge 前主分支更新的 gate 规则，如新 capability 登记），gate 阻断则 return `merged=False`，gate 异常降级为 warn 不阻断，HEAD 用 `git reset --soft orig_head` 恢复。`reconcile_verify` 默认值 False→True：merge 后自动触发 17 个 reconciler（`_run_reconcilers_after_merge`），补齐 post-merge 漂移修复（manifest/path_tree/path_ownership/depgraph_ops 等 auto_commit + warn-only）。治本 worktree commit 绕过 GitCommitGateway 的设计间隙——commit 时 gate 检查通过不代表 merge 时仍通过（主分支可能有新 commit），merge 后 reconciler 不触发则漂移无修复。**breaking_change 并发阻断（§9.7 治本，2026-07-04）**：codify 本文件 §391"治本变更未提交前禁止并发 AI 对话"——原为君子协定（靠 AI 自觉不并发），AI 不遵守就并发导致搭便车提交/工作区回退。[`session_worktree_start`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/session_worktree.py) 新增 `breaking_change: bool = False` + `allow_concurrent: bool = False` 参数，在注册 session 之前执行双向阻断：① `breaking_change=True` 时检查是否有其他活跃 session → 有则返回 `BREAKING_CHANGE_CONCURRENCY_BLOCKED` 阻断（治本变更期间禁止并发）；② `breaking_change=False` 时检查是否有其他活跃 session 声明了 `breaking_change=True`（调 [`SessionRegistry.find_breaking_change_session`](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/session_concurrency.py)）→ 有则返回 `BREAKING_CHANGE_AVOIDANCE_BLOCKED` 阻断（避让治本变更）。`allow_concurrent=True` 逃生通道跳过阻断（对标 `allow_overlap`）。fail-open：并发检测异常不阻断 start（对标 held_overlap_gate fail-open）。**AI 使用指引**：refactor/fix 涉及多文件的治本变更会话 MUST 传 `breaking_change=True` 启动；普通会话默认 `breaking_change=False` 自动避让。**capability 反查**：已登记 `breaking_change_concurrency_blocker`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)），新 AI 搜 "breaking_change/治本变更并发/§9.7" 可定位真源。**测试**：`test_worktree_start_breaking_change_blocks_new_session`/`test_worktree_start_breaking_change_blocks_concurrent_breaking`/`test_worktree_start_breaking_change_allow_concurrent_escape`（3/3 PASS）。**自动触发条件**：Trae 原生支持 worktree（对标 VS Code 1.107）后激活自动 start。
- **commit 前必须 claim_files 声明工作范围（搭便车防护前提，2026-06-30）**：AI session 通过 GitCommitGateway commit 前 MUST 先调 [`claim_files`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 声明本次修改的文件列表——held_files 阻断层（下条）依赖 claim_files 注册的文件归属数据，未 claim 的 session 无法被阻断层检测。CLI 封装 [`scripts/git_commit.py`](file:///d:/ZephyrAlpha/scripts/git_commit.py) 已内置 claim_files → commit → release_files 流程。
- **GitCommitGateway held_files 冲突阻断（搭便车治本，2026-06-30）**：[`commit()`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/git_commit_gateway.py) 时 [`HeldOverlapGate`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/held_overlap_gate.py) 自动检测目标文件是否被其他**活跃** session 持有（通过 [`SessionRegistry.other_held_files`](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/session_concurrency.py)），命中则返回 `HELD_OVERLAP_VIOLATION` 阻断（`--no-verify` 绕不过，在 gateway 内部非 pre-commit hook）。**逃生通道**：`commit(allow_overlap=True)` 或 CLI `--allow-overlap` 显式声明时放行，commit message 追加 `[GW:<sid>:overlap]` 标记供审计追踪。过期 session 的持有自动忽略（TTL=3600s + PID 存活检测）。约束真源见 [parallel_session_coordination_policy.md §3.2/§5.2](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md)。
- **GitCommitGateway 门禁注册制 CommitGateRegistry（架构债务 #AD-001 治本，2026-06-30）**：[`commit_gate_registry.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_bridge/commit_gate_registry.py) 把 `commit()` 方法体中硬编码的 `_check_*` 调用升级为声明式 registry——新增 pre-commit 门禁只需 `register(GateSpec)`，不改 `commit()` 方法体，消除多 session 频繁修改同一文件（git_commit_gateway.py 2500+ 行）的搭便车冲突源。设计参考 [`ReconciliationRegistry`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（post-commit reconciler 注册表），纯 stdlib 解耦。gate 实现放 [`commit_gates/`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/) 子目录，每个 gate 一个文件 + `make_*_gate()` 工厂函数。**新 AI 添加门禁**：在 `commit_gates/` 下创建 `make_xxx_gate()` → 在 `GitCommitGateway.__init__` 中 `register`，禁止在 `commit()` 方法体硬编码 `_check_*` 调用。
- **GitCommitGateway DIRECTORY-CONTRACT gate（DCR-001~007 等效校验，--no-verify 补偿，2026-06-30 治本）**：[`make_directory_contract_gate`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/directory_contract_gate.py)（priority=30，在 CLAIM-REQUIRED(40)/HELD-OVERLAP(50) 之前执行）通过 subprocess 调用 [`check_directory_contract.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py) 复用真源——DCR-001~007 校验逻辑唯一在 check_directory_contract.py，gateway 不复制检测代码（subprocess 复用真源模式）。**病根**：GitCommitGateway 用 `--no-verify` 绕过 pre-commit hook（GATE-DIRECTORY-CONTRACT），DCR-001~007 防御断层——新 AI 可在 gateway 路径创建违规文件（如根目录 .txt、docs/03_modules/.py）绕过目录契约。本 gate 在 gateway 内部注册制执行等效校验，`--no-verify` 绕不过。**fail-closed**：check_directory_contract.py 缺失/执行失败/超时（60s）时阻断 commit（防 checker 被删后静默放行）。文件数 >200 时改用 `--all-files` 全量扫描避免 WinError 206（Windows 命令行长度限制）。**reconciler 路径已覆盖**：`_commit_auto`（reconciler auto-commit 入口）通过 `gate_registry.get("DIRECTORY-CONTRACT")` 复用本 gate 的 GateSpec，调其 check 方法对 reconciler 提交的文件跑 DCR 等效校验（2026-06-30 红蓝对抗治本，见上方"reconciler auto-commit 统一入口"条目）。约束真源见 [directory_contract.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml)。
- **GitCommitGateway CREATE-GUARD 门禁（新建 .py 文件 creation_token 阻断，2026-06-30 治本）**：[`make_create_guard`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/create_guard.py)（priority=60，在 HELD-OVERLAP(50) 之后、CAPABILITY-OVERLAP(200) 之前执行）检测 staged 新增 .py 文件是否在 [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) 的 `creation_tokens` 字段登记。**病根（"造第二真源"根因）**：AI 新建 .py 文件时可能复制已有实现（违反 [trae_060 §2](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml) 唯一真源原则），现有缓解（GATE-SSOT module_path 冲突检测 + GATE-SSOT-SINGLESOURCE 文件名检测 + capability_overlap_gate warn-only）均在 commit 时检测，检测滞后于创建。本 gate 治本：强制 AI 在创建新 .py 文件前先在 `creation_tokens` 字段登记 token（声明创建意图 + 关联 capability），未登记则 commit 硬阻断——把检测点从"commit 时"前移到"创建前"。**files 参数过滤治本（2026-06-30）**：gateway 选择性提交（只提交 files_in_scope，其他 staged 文件 stash），create_guard 只检测 commit 文件中的新增 .py（通过 `os.path.relpath(f, project_root)` 过滤），不检测其他 session 的 staged WIP（防误判）。**tests/ 豁免**：测试文件不是能力真源（对标 capability_overlap_gate 设计），不要求登记 token。**fail-open（YAML 不可达）**：registry 缺失/解析失败时放行——registry 故障不应卡死 commit 工作流（对标 capability_overlap_gate 的 fail-open 设计）。**token 登记格式**：`- file: "<相对路径>"  token: "auto-xxx"  created_by: "session-xxx"  capability: "xxx"`（详见 [create_guard.py](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/create_guard.py) docstring）。约束真源见 [trae_060 §2 唯一真源与直接消费](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml)。**元问题3治本扩展（2026-06-30，AD-GOV-001 收敛约束技术强制）**：扩展检测范围——若 commit 包含 [`reconciliation_registry.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)，用 AST 对比 staged 与 HEAD 版本的 `make_*_reconciler` 函数集，新增函数需在 def 前 5 行内添加 `# trae_060-reviewed: <审查结论>` 标记，否则硬阻断。**病根**：AD-GOV-001 约束"新增 reconciler 前 MUST 过 trae_060 §4 元问题审查"是君子协定，新 AI 可直接造新 reconciler 绕过审查。**递归陷阱规避**：若新增门禁强制此审查，门禁本身也是"新增"需过 §4 审查（无限递归）；治本是扩展已有 create_guard 检测范围，不新增门禁。**检测逻辑**：`commit_files_rel` 含 `src/zephyr/governance/audit/reconciliation_registry.py` 时触发 → `git show :path` 取 staged 源码 + `git show HEAD:path` 取 HEAD 源码 → `ast.parse` 提取 `make_*_reconciler` 函数集 → 新增函数（staged - HEAD）检查 def 前 5 行是否含 `trae_060-reviewed` 标记 → 无标记则阻断（detail 列出未标记函数名 + 修复指引）。**fail-open**：git show 失败/SyntaxError 时不阻断（避免误伤正常 commit，其他 gate 兜底语法检测）。**标记格式**：`# trae_060-reviewed: <审查结论>`（如 `# trae_060-reviewed: 该存在+可合并入GATE-X+治本`）。

- **GitCommitGateway ARCH-REFERENCE 门禁（#ARCH-NNN 悬空引用阻断，2026-07-01 治本）**：[`make_arch_reference_gate`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/arch_reference_gate.py)（priority=75，在 DANGLING-REFERENCE(70) 之后、CAPABILITY-OVERLAP(200) 之前执行）检测 staged 文件中新增的 `#ARCH-NNN` 引用是否在 [`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 中登记。**病根（编号铁律#6 代码强制）**：编号铁律#6"任何 #ARCH-XXX 引用必须在本注册表有对应条目，禁止 grep-and-claim 占位"原为文档约束（靠 AI 自觉查 registry），AI 不查就占位导致编号冲突（如 ARCH-027 误用冲突改 ARCH-028）。本 gate 治本：新 AI 不查 registry 就用未登记编号 → GitCommitGateway 硬阻断（exit=1）。**增量检测**：只检测 staged 文件中**新增的**引用（通过 `git show HEAD:<path>` 对比），不阻断历史悬空引用（防卡死工作流）。**fail-closed**：registry 缺失/git 异常时阻断（防门禁静默失效）。**tests/ 豁免**：测试文件不检测。**capability 反查**：已登记 `arch_reference_gate`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)）。新 AI 想做"#ARCH 编号引用检测/phantom arch id"前，CapabilityLookup 会反查阻止重复造轮子。

### 8.1 蓝图/模块删除价值判定（RULE-THREE + ARCH-027 + RULE-TWELVE）

> **新AI必读**：当你发现一个模块/蓝图"零消费者"或"看起来没用"时，**禁止直接删除**。必须按以下二元判定标准逐项审判。

**核心铁律**：零消费者 ≠ 无价值

- 真源：[ARCH-027 价值判定原则](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_017_arch_governance_order.yaml) + [RULE-THREE 删除前置确认](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml) + [RULE-TWELVE 项目瘦身](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_052_cross_blueprint_change_cleanup.yaml)
- 禁止：仅凭"零消费者"判定删除（误删有价值的安全/治理组件）

**判定决策树**（按序执行，任一YES即保留）：

```
发现零消费者/疑似无价值模块时：
│
├─ STEP 0: 功能价值判定（ARCH-027 三维度，ANY为YES→保留并接通，不进入删除流程）
│   ├─ 3a 独立功能价值：该模块是否提供其他模块无法替代的独立功能？
│   │   YES → 保留，接通消费者管线（接入系统）
│   ├─ 3b 客观原因：零消费者是否有客观原因？
│   │   （管线未接通 / C轨业务层未施工 [ARCH-045 P0 已解除占位禁令，C轨blocked 历史状态退役] / 前置依赖未就绪 / 暂缓施工Suspended）
│   │   YES → 保留，待管线就绪后自然产生消费者
│   └─ 3c 重建成本：删除后若需要重建，成本是否高昂？
│       YES → 保留，重建成本高于维护成本
│
│   └─ ALL NO（三维度均为NO）→ 进入 RULE-THREE 三步审判
│
├─ RULE-THREE STEP 1: 登记检查
│   该文件在 manifest/registry/__init__.py 中被引用？
│   YES → 有价值，不能删
│
├─ RULE-THREE STEP 2: 重复检查
│   有另一个文件与它内容完全相同且已注册？
│   YES → 真正重复，可删
│
└─ RULE-THREE STEP 3: 逐行价值检查
    逐行检查代码/设计内容是否无价值？
    确认无价值 → 删除
│
└─ 删除后验证三步（RULE-TWELVE 强制）：
    1. audit_registration.py exit 0
    2. generate_project_path_tree.py --write
    3. generate_project_depgraph.py --max-workers 8
```

**执行器**：[`pre_delete_safety_check.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/pre_delete_safety_check.py)（5项机械检查：.py消费者 / .yaml消费者 / 注册表登记 / 重复内容 / 高价值标记，exit 0=SAFE 允许删除 / exit 1=BLOCKED 禁止删除）

```bash
# 删除前必须先跑执行器（--dry-run 不修改任何文件）
python scripts/governance/d5_architecture/pre_delete_safety_check.py <file_path> --dry-run
```

**P0模块特殊约束**（[trae_032 §MLC-003](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_032_module_lifecycle.yaml)）：P0模块禁止退役——必须先完成P1+等效替代并active≥30天。

## 9. 新模块接入规则

创建新模块时，必须：
0. **查 CapabilityLookup 确认能力是否已存在**（防止重复造轮子）：
   ```python
   from zephyr.governance.capability_lookup import CapabilityLookup
   reg = CapabilityLookup()              # 自动扫磁盘+派生 canonical
   hits = reg.find("rollback")            # 关键词搜（匹配 capability_id/aliases/description/canonical_file）
   hits = reg.find("session handoff")     # 多词短语也支持（token AND 匹配，词无需连续出现）
   cap = reg.get("rollback_executor")     # 按 capability_id 精确查
   reg.check_file_canonical("src/zephyr/xxx.py")  # 反查某文件是哪个能力的 canonical
   ```
   真源：[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)（能力索引，仅声明 capability_id/aliases/description；canonical_file/duplicates/removed_duplicates 全部由 CapabilityLookup 从磁盘头部+git log 自动派生）。已存在的能力 → 扩展现有 canonical 文件，禁止新建重复实现。
   **aliases 只放英文标识符**（函数名/常量，如 `REPO_ROOT`/`load_blueprint_path`）；中文变体由 `find()` 的 token 包含匹配（CJK ≥3 字符公共子串）自然处理，**禁止在 YAML 堆中文同义词 alias**（反模式，见注册表顶部 alias 策略）。

   **commit 时自动检测能力重复**（事件驱动兜底，治本 2b）：即使 AI 忘记执行上方手动查重，GitCommitGateway 在 commit 时会自动调用 [`check_capability_duplicates`](file:///d:/ZephyrAlpha/src/zephyr/governance/capability_lookup.py) 检测新增 `.py` 文件是否参与"同能力多实现"：
   - 新文件 basename 撞已有 capability_id/alias（registry 派生标为 duplicate）→ commit 被 BLOCK，修复指令见报错信息。
   - L3 pre-commit hook（[`check_ssot_gate.py`](file:///d:/ZephyrAlpha/scripts/governance/check_ssot_gate.py)）作为双保险，绕过 gateway 直接 `git commit` 时同样阻断。
   - 检测逻辑唯一真源：`capability_lookup.check_capability_duplicates`（L2/L3 共用，避免两份实现漂移）。
1. 构造 CapabilityCard 并注册到 CapabilityRegistry
2. 在 `data/capability_cards/` 下创建对应的 YAML
3. 如果有自动化工作，创建 WorkDAG 并注册到 WorkOrchestrator
4. 写入 AiAuditLogger 记录注册事件

如果不注册，ModuleOnboardingScanner 会在扫描时发现并自动触发接入流程。

## 10. Git 命令封装约定（绕过 Trae 批准弹窗）

> **根因**：Trae 对 `git` 前缀命令有硬编码安全审查，settings.json 的 allowList/alwaysRun 对 git 无效，但对 `python` 前缀有效。直接用 `git xxx` 会弹出批准框，打断 AI 连续工作。

**强制规则**：所有 git 命令 MUST 通过 `python scripts/git_guard.py` 封装执行，禁止直接用 `git` 前缀。

| 场景 | ❌ 禁止（会弹窗） | ✅ 必须（不弹窗） |
|------|------|------|
| 暂存 | `git add <file>` | `python scripts/git_guard.py add <file>` |
| 提交 | `git commit -m "..."` | `python scripts/git_guard.py commit -m "..."` |
| 提交(文件) | `git commit -F <file>` | `python scripts/git_guard.py commit -F <file>` |
| 状态 | `git status` | `python scripts/git_guard.py status` |
| 日志 | `git log --oneline -5` | `python scripts/git_guard.py log --oneline -5` |
| 差异 | `git diff` | `python scripts/git_guard.py diff` |
| 推送 | `git push` | `python scripts/git_guard.py push` |
| 拉取 | `git pull` | `python scripts/git_guard.py pull` |

**复合命令**：禁止用 `;` 或 `&&` 串联多个 git 命令（RULE-SEVENTEEN），分多次 RunCommand 执行。

**git_guard.py 行为**：
- 非危险命令（add/commit/status/log/diff/push/pull 等）→ 直接透传给 git（[第 477 行](file:///d:/ZephyrAlpha/scripts/git_guard.py#L477)）
- 危险命令（reset --hard/checkout/stash/revert/restore/mv）→ 检查 `.ailocks/` 锁冲突后透传

**示例**：用户要求 `git add src/x.py; git commit -F _tmp.txt --no-verify` 时，AI 应分两次执行：
1. `python scripts/git_guard.py add src/x.py`
2. `python scripts/git_guard.py commit -F _tmp.txt --no-verify`

## 11. depgraph 使用指引（唯一全景真源）

### 11.0 真源方向决策表（唯一入口，新 AI 必读）

> 项目存在两个真源方向，按数据类型机械判定。**禁止凭记忆推断真源方向**——拿到数据先查此表。

| 数据类型 | 真源 | 修改入口 | 判定关键词 | DB 表 |
|---------|------|---------|-----------|-------|
| 架构全景图（域/模块/依赖/path_design/physical_files） | PostgreSQL depgraph | `apply_depgraph.py` | 实例态（磁盘上有什么） | nodes/edges/domains/domain_dependencies/domain_mapping 等 16+ 张可写表 |
| 规则/契约/门禁/词汇表 | YAML 文件 | 改 YAML → GATE-YAML-SYNC 自动同步 | 声明态（应该有什么） | gates/field_vocabularies/registries/cross_registry_rules/hard_boundaries/business_streams/infrastructure_components/model_capabilities（8 张 readonly 表，禁止手写） |
| 数据库清单 | `infrastructure_registry.yaml` | 改 YAML | INFRA-DB-* | infrastructure_components（与规则数据共享表，但真源是 YAML） |

> **判定规则**：拿到一个数据，先问"是实例态还是声明态？"——实例态（磁盘上有什么模块/文件/依赖）→ DB 真源（apply_depgraph.py）；声明态（规则/契约/词表应该有什么）→ YAML 真源（改 YAML，DB 自动同步）。边界模糊时查此表。
>
> **blueprint_links 特殊裁定（2026-07-02）**：`blueprint_links` 表是从 `nodes` 表派生的物化视图（非 YAML 真源），由 `sync_yaml_to_depgraph.py` 重建，但无 readonly 触发器保护，`apply_depgraph.py` 可直接写入。

### 11.0.1 数据库清单真源指针（新 AI 进入项目先读此段）

> **唯一真源**：[`docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml) 的 `infrastructure:` 段（`type` 含 `*_db` 的条目）。
>
> **铁律**：禁止在任何其它文档（蓝图/规则/onboarding/副本）同步数据库清单——所有引用 MUST 用纯指针指向上方真源，禁止摘抄数据库条目作为同步副本。新增/废弃数据库 MUST 先改 infrastructure_registry.yaml，再由 reconciler 派生，禁止反向。违反此铁律会导致 17+ 副本漂移重演（历史教训）。

**新 AI 发现路径**：
1. 想知道"项目有几个数据库/各负责什么" → 直接读 infrastructure_registry.yaml 的 `infrastructure:` 段，禁止凭记忆或其它文档推断。
2. 准备改 DB 连接/新增 DB → 先查真源确认当前状态，再按下方 §11 depgraph 流程或对应模块蓝图施工。
3. 写文档需要提"数据库清单" → 一律用纯指针引用真源，禁止复制条目。
4. ~~准备操作 market.duckdb~~ → **market.duckdb（原 INFRA-DB-005）已于 2026-07-01 彻底删除**（墓碑清理，见 ARCH-046 铁律3"删除即彻底删除"）。原 market_schema.py 同步删除（死代码）。业务行情数据迁移至 ClickHouse c1_market（INFRA-DB-006，status=connected），统一入口 `DatabaseService.get_clickhouse_conn()`（readonly=1），详见 [c1_market_clickhouse.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md)。**注意**：DuckDB OLAP 引擎（INFRA-DB-004，:memory: 内存模式只读挂载 governance.db）保留不变，与 market.duckdb 是两个独立实体。
5. **ARCH-046 数据库节点全景图登记三铁律**（2026-07-04 固化）：(1) 粒度铁律——数据库在全景图中有且仅有一个点（`infrastructure_components` 表），不展开内部表/schema；(2) 运营态/设计态语义铁律——数据库存在并使用=运营态（status=connected），不存在=设计态（status=planned），禁止 status 漂移；(3) 动态更新铁律——数据库节点随项目实况增删，不保留墓碑，生成器（generate_project_depgraph.py）MUST NOT 碰 `infrastructure_components` 表。详见 [ARCH-046](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)。

> depgraph 是唯一全景真源（PostgreSQL 16，localhost:5432），禁止创建派生 YAML 副本。连接配置见 `config/.env.postgres`，连接入口 `zephyr.governance.depgraph_schema.get_depgraph_pg_connection()`。遇到 depgraph 相关问题，直接问工具：

- **查 DB 数据** → `python scripts/governance/extract_depgraph.py --help`（场景速查表在 epilog）
- **改 DB 节点/路径** → `python scripts/governance/apply_depgraph.py --help`（35+ 子命令）
- **批量改 DB（多 op 原子事务）** → `python scripts/governance/apply_depgraph.py --batch changes.json`（先 `--dry-run` 预览）。op 清单运行 `--list-ops` 查看（从 `_DOMAIN_OPS`/`_NODE_OPS` 注册表自动派生，真源唯一——禁止手工同步到 docstring/AGENTS.md，§6.16 铁律）；所有 op 共享单一 PostgreSQL 事务，全部成功才 commit，任一失败全部 rollback。批量重命名域 ID 时**禁止**手写 `_tmp_batch_rename.py` 调 `--rename-domain` 单命令循环（失去原子性，部分失败留半成品数据）。
- **查哪些表不能手写** → `python scripts/governance/sync_yaml_to_depgraph.py --list-readonly-tables`
- **文件结构变更后同步 DB** → 自动完成（GitCommitGateway post-commit GATE-PATH-TREE reconciler，无需手动）
- **DB 变更后重生域文档** → 自动完成（GitCommitGateway post-commit GATE-REGENERATE reconciler（含原 DOMAIN-DOC 功能），无需手动）
- **文件删除后重生域文档** → 自动完成（GATE-REGENERATE trigger 已扩展：committed 文件不在磁盘 = 删除 commit 时也触发生成器重生。生成器内置 ghost 过滤，重生后的文档自动排除已删除文件的节点，无需手动 deprecate）
- **scripts/ 下 .py 增删后重生 manifest** → 自动完成（GitCommitGateway post-commit GATE-MANIFEST reconciler，priority=620，2026-07-01 新增。无需手动跑 generate_script_manifest.py）
- **铁律：架构文档（02_domain_architecture_docs/ + generated/domains/）由生成器自动产出，禁止手动编辑**。手动编辑会被下次生成器运行覆盖。如需修改内容，改 depgraph 或生成器代码，不要改输出文件。
- **改了 YAML 规则文件后同步 DB** → 自动完成（GitCommitGateway post-commit GATE-YAML-SYNC reconciler，无需手动）。手动调试可跑 `python scripts/governance/sync_yaml_to_depgraph.py`
- **改了 rules/ 下规则文件后同步 catalog** → 自动完成（GitCommitGateway post-commit GATE-RULE-AUDIT reconciler（含原 RULE-CATALOG 功能），无需手动）。catalog 真源：`_registry/catalogs/rule_catalog_registry.yaml`（由 `scripts/governance/d3_metadata/generate_rule_catalog.py` 自动生成，60 条规则元数据；#ARCH-024 治本：原 `rules/_index.yaml` 手工索引已删除）
- **改了 infrastructure_registry.yaml 后同步 registry_master_index** → 自动完成（GitCommitGateway post-commit GATE-REGISTRY-SYNC reconciler（含原 REGISTRY-INDEX 功能），无需手动）
- **查 PG 运行时健康** → `python scripts/governance/verify_schema_health.py --warn-only`（校验4：死锁/连接饱和/长事务，pre-commit 自动跑；`--skip-runtime` 可跳过）

> **GATE-SCHEMA-HEALTH 门禁（ARCH-016/017/018 治本，2026-06-26）**：depgraph (PostgreSQL) Schema 健康度校验，4 项校验（DDL 列一致性/只读触发器/Schema 版本/PG 运行时健康）。**门禁路由**：原独立 `gate-schema-health` 已于 ARCH-017 治本时合并到 **GATE-C2**（run_gate_chain 顺序执行 check_contract_code_drift + check_contract_physical_path + verify_schema_health），`.pre-commit-config.yaml` stages 从 manual 升级为 commit（--no-verify 绕不过 GitCommitGateway in-process gate）。**检测真源**：`scripts/governance/d11_compliance/verify_schema_health.py`（capability=schema_health_verification，aliases 含 GATE-SCHEMA-HEALTH/verify_schema_health/schema_health）。**重定向锚点**：gate_registry.yaml 保留 GATE-SCHEMA-HEALTH 条目（status=deprecated, redirect_to=GATE-C2）供历史引用可追溯。退出码：0=健康/1=漂移/2=脚本错误；模式：--ci 硬阻断（默认）/--warn-only 软警告/--skip-runtime 跳过校验4。

> 改 depgraph 前必须通过 `pg_dump` 或 apply_depgraph.py 内置物理备份（trae_054 STEP0）。DB↔磁盘一致性检查用 `python scripts/governance/diagnose_depgraph.py`。

> **ghost 自动检测+自动清理（已实现，勿重复造）**：删除文件 commit 时，GitCommitGateway post-commit 的 `GATE-DELETE-AUDIT` reconciler（含原 GHOST 功能，priority=400）自动调用 `diagnose_depgraph.py` 检测 ghost node（磁盘已删但 DB 残留），报告落盘 `.runtime/reconcile_reports/ghost_*.json`。无需手动跑 diagnose 检测 ghost。**清理路径（2026-07-04 P1 治本，auto_clean 闭环）**：① ghost 数 ≤ 50 → reconciler 自动调 `apply_depgraph.py --cleanup-orphan-nodes` + `--cleanup-orphan-edges` 清理（备份先行：`_backup_depgraph_for_autoclean` 用 F1 裸 psycopg2 connection + copy_expert 导出 nodes/edges CSV 到 `data/databases/backups/ghost_autoclean_<ts>/`，备份失败 fail-closed 不清理）；② ghost 数 > 50 或解析失败 → 走 warn 不清理（防批量误删），需人工 `apply_depgraph.py --cleanup-orphan-nodes`。阈值 `_GHOST_AUTO_CLEAN_THRESHOLD=50`（reconciliation_registry.py），与 generate_project_depgraph.py `_GHOST_WARNING_THRESHOLD=50` 对齐。trigger 仅覆盖"删除 commit"是 intentional（删除才会产生 ghost），勿扩展到 PG 写入脚本 commit（脚本 commit ≠ DB 内容变更，扩展会引入噪音）。

> **三层 ghost 防御（2026-07-01 ARCH-038 铁律，勿重复造）**：
> 1. **Layer 1（技术铁律）**：生成器（`generate_domain_doc.py` + `generate_domain_dependency_diagram.py`）内置 `_is_ghost()` 过滤——path 非空但磁盘不存在的节点自动排除。即使 depgraph 有 2774 个 ghost 节点，生成的文档也不会引用幽灵文件。**新 AI 不需要知道要跑 deprecate——不跑也不会有问题**。
> 2. **Layer 2（自动修复）**：GATE-REGENERATE trigger 已扩展——文件删除 commit 时自动触发生成器重生。GATE-MANIFEST（priority=620）自动重生 script_manifest.yaml。GitCommitGateway post-commit 全自动，无需人工触发。
> 3. **Layer 3（规则补充）**：本段 AGENTS.md 规则。禁止裸连数据库，必须通过 `apply_depgraph.py` 程序化访问（真源方向见 §11.0 决策表）。架构文档由生成器自动产出，禁止手动编辑。

> **命名规范（2026-06-30）**：本数据库的标准名字是 `depgraph (PostgreSQL)`——一眼可知引擎、区别于 SQLite 物理文件 `depgraph.db`。禁止使用以下变体：① 带括号缩写 `depgraph (PG)`/`PG（depgraph）`；② 带"数据库"后缀 `depgraph 数据库`；③ 无括号全称 `PostgreSQL depgraph`/`depgraph PostgreSQL`；④ 无括号缩写 `PG depgraph`/`depgraph PG`。物理标识符不改：`depgraph.db`（SQLite 文件名）、`localhost:5432/depgraph`（PG 连接 URL 中的 database 名）、`数据库名 \`depgraph\``（PG 物理 database 名）、函数名 `get_depgraph_pg_connection`。

### 11.1 生成器发现指引与时间戳约定

> **新 AI 进入项目涉及"生成器"相关工作时，MUST 先读本节。**
> 病根：AI 跨域复刻生成器（wave_generator 4 份副本、index_generator 影子副本等），
> 根因是新 AI 不知道已有生成器存在。治本：发现指引 + P0 防再生门禁。

#### 11.1.0 生成器发现指引（RULE-EIGHT 生成器专项）

**创建新生成器前 MUST 执行以下 3 步查重**：

1. **关键词搜索**：`python -m zephyr.governance.capability_lookup --find <关键词>`
   - 搜索 capability_id / aliases / description / canonical_file / module_id
   - 例：`--find generator`、`--find path_tree`、`--find index`
2. **注册表匹配**：查 [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)
   - `domain_architecture_generators` 条目列出全部 12 个架构生成器及其别名
   - `outputs` 字段列出生成器→输出目录映射
3. **复用决策**：命中已有 → 扩展已有生成器（RULE-EIGHT 扩展优先于新建）；未命中 → 通过 `scaffold.py` 创建（P0-5 create_guard 强制）

**已有生成器清单**（真源：`scripts/governance/d5_architecture/generators/`）：

| 生成器 | 输出目录 | 用途 |
|--------|----------|------|
| `generate_navigation_index.py` | `02_enterprise_architecture/00_overview_entry/` | 导航索引 |
| `generate_path_tree.py` | `01_global_architecture_diagram/` | 项目路径树 |
| `generate_cross_domain_matrix.py` | `01_global_architecture_diagram/` | 跨域矩阵 |
| `generate_integration_topology.py` | `01_global_architecture_diagram/` | 集成拓扑 |
| `generate_capability_heatmap.py` | `01_global_architecture_diagram/` | 能力热图 |
| `generate_domain_doc.py` | `02_domain_architecture_docs/` | 域架构文档 |
| `generate_domain_index.py` | `02_domain_architecture_docs/` | 域索引 |
| `generate_domain_dependency_diagram.py` | `02_domain_architecture_docs/` | 域依赖图 |
| `generate_design_vs_production.py` | `03_governance_reports/` | 设计 vs 生产 |
| `generate_constraint_violations.py` | `03_governance_reports/` | 约束违规 |
| `generate_capacity_report.py` | `03_governance_reports/` | 容量报告 |
| `generate_contracts.py` | `05_contracts/` | 契约文档 |

**P0 防再生门禁**（2026-07-01 生成器治理治本）：
- P0-1：N-16 src/ basename 唯一门禁——同 basename 跨域 commit 阻断
- P0-2：GATE-SSOT 硬层3——同 module_id 多文件 commit 阻断
- P0-3：GATE-SSOT 硬层4——[MODULE] 声明域 ≠ 物理路径域 commit 阻断
- P0-4：scaffold 维度3b——同 basename 跨域创建阻断
- P0-5：scaffold 自动登记 creation_token——绕 scaffold 直接 Write .py → commit 阻断

#### 11.1.1 时间戳约定

> 所有生成器（`scripts/governance/d5_architecture/generators/` 下的 `.py` 文件）输出的文档中，
> 日期字段 MUST 使用 `auto-generated`，最后更新时间 MUST 标注"最后更新以 git log 为准"。
> **禁止在生成器中使用 `datetime.now()` 或任何实时时间源**，否则每次修改 depgraph (PostgreSQL)
> 都会因时间戳变化产生非幂等噪音 auto-commit。

- **真源实现**：所有生成器 docstring `[INVARIANTS]` 声明"输出幂等(相同输入→相同输出);零时间戳"
- **时间真源**：文件修改时间唯一真源是 git log，生成器不引入独立时间源
- **检测**：`Select-String -Path "scripts/governance/d5_architecture/generators/*.py" -Pattern "datetime\.now\(\)"` 应返回零匹配
- **自动触发**：GATE-REGENERATE reconciler（含原 DOMAIN-DOC 功能）在修改 depgraph 后自动调用 generate_domain_doc.py 和 generate_domain_dependency_diagram.py 重生域文档，生成器幂等性确保无噪音 auto-commit
- **按域编号生成器 --all 模式 MUST 调用 cleanup_stale_files**：生成"按域编号文件"（`NN_d_xxx.md`/`.mmd`，域重命名/删除后旧编号会残留）的生成器，在 `--all` 模式下 MUST 调用 `_common.cleanup_stale_files()` 清理孤儿文件，治本"只增不删"。当前适用：`generate_domain_doc.py`、`generate_domain_dependency_diagram.py`（均已调用）。单域模式不清理（避免误删）；生成单文件/非编号文件的生成器（导航索引、容量报告、集成拓扑等）不适用。真源：[`_common.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/_common.py)
- **检测**：对生成 `NN_d_xxx` 格式文件的生成器，`Select-String -Pattern "cleanup_stale_files"` 应返回至少 1 匹配（当前 2 个生成器均通过）

#### 11.1.2 ARCH 引用校验门禁（Phase 4 防御性门禁，ARCH-033，2026-07-02）

> **新 AI 修改 `generate_project_depgraph.py` 中 `#ARCH-XXX` 引用时 MUST 先读本节。**
> 病根：AI 在脚本中随意写 `#ARCH-XXX` 引用但不在 [`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 登记，导致 grep-and-claim 占位（编号铁律#6 违规）。
> 治本：`generate_project_depgraph.py` 启动时自动校验本文件所有 `ARCH-XXX` 引用是否在 registry 有对应条目。

- **真源实现**：[`generate_project_depgraph.py`](file:///d:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py) `_validate_arch_references()` 函数（L2524）
- **自动触发**：`generate_project_depgraph.py` 的 `main()` 中 `parse_args()` 后自动调用（L3598-3599），无需手动触发
- **自动运行**：正则 `\bARCH-(\d+)` 扫描本文件源代码 → 提取所有 ARCH 编号 → 读取 registry → 比对差集；另用 `\bARCH-\d+`（IGNORECASE）检测小写 `arch-` 违规（标识符编号必须大写，trae_028 §标识符编号格式）
- **自动关闭**：校验完成后打印结果即返回；校验失败 sys.exit(1) 阻断运行（ERROR 级别）
- **校验范围**：仅校验 `generate_project_depgraph.py` 自身源码中的 ARCH 引用，不扫描其他文件
- **registry 真源**：[`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) `entries[].issue_id` 字段
- **编号铁律#6**：任何 `#ARCH-XXX` 引用必须在本注册表有对应条目，禁止 grep-and-claim 占位
- **标识符编号大写**：ARCH 编号必须大写（`ARCH-033` 合规，`arch-033` 违规），小写引用触发 ERROR 阻断；规则真源见 [trae_028 §标识符编号格式](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)
- **当前状态**：ERROR 阻断（校验失败 sys.exit(1)，2026-07-02 从 WARN 升级为 ERROR）

### 11.2 P3 PostgreSQL 优化裁定记录（2026-06-28）

> **本节是 P3 相关工作的硬约束。** 任何 AI 在涉及 PostgreSQL 优化时必须先读本节。
> 真源：本节（P3方案文档已于 2026-06-30 归档删除，裁定记录内联于此作为唯一真源）

P3 原计划 4 个任务经第一性原理审查（38 个问题），裁定如下：

| 任务 | 裁定 | 理由 |
|------|------|------|
| P3-T1 pgvector | **改造**（不建 pgvector） | 项目已有 VMS（ChromaDB+BGE-M3+Hybrid+reranker），pgvector 是降级重复造轮子。治本：扩展 VMS code_context indexer |
| P3-T2 LISTEN/NOTIFY | **删除** | 100% AI 开发无常驻监听者，GitCommitGateway+ReconciliationRegistry 事件驱动对账已覆盖 |
| P3-T3 分区表 | **删除** | 24MB/6429行过度工程，edges 无 domain_id 无法分区 |
| P3-T4 监控告警 | **改造已实现** ✅ | 扩展 `verify_schema_health.py` 校验4 `check_pg_runtime_health()`，事件驱动替代违反 trae_053 的常驻 monitor_pg.py |

**禁止新建的文件/对象**（违反则为重复造轮子或伪需求）：
- `pgvector` 扩展、`code_embedding.py`、`nodes.embedding` 列 — VMS 已覆盖向量检索
- `pg_notify.py`、`depgraph_events` 表、LISTEN/NOTIFY 触发器 — GitCommitGateway 已覆盖事件协调
- `monitor_pg.py`、`config/pg_monitor.yaml` — verify_schema_health.py 校验4 已覆盖 PG 运行时监控
- 分区表（nodes/edges 按 domain_id HASH 分区）— 数据量不达标，过度工程

**P3-T4 已实现能力**：`verify_schema_health.py` 新增校验4，检查死锁（信息性）/连接饱和（>80%阻断）/长事务（>300s阻断），pre-commit 事件驱动。`--skip-runtime` 可跳过。

**CT-TEL-001~004 codegen 死代码治本约束**（SSoT 三重冗余修复后裁定，2026-06-28）：
- **真源唯一**：CT-TEL-001~004 的手工实现真源唯一为 [src/zephyr/infrastructure/system_telemetry/](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/) 下的对应文件（MOD-INF-015）：
  - CT-TEL-001 → `system_telemetry/contract_metrics.py`
  - CT-TEL-002 → `system_telemetry/logs/structured_sink.py`
  - CT-TEL-003 → `system_telemetry/traces/span_stub.py`
  - CT-TEL-004 → `system_telemetry/health_probes.py`
- **physical_path: null 不可恢复**：[cross_layer_contracts.yaml](file:///d:/ZephyrAlpha/architecture_model/contracts/cross_layer_contracts.yaml) 中 CT-TEL-001~004 的 `physical_path` 字段 MUST 保持 `null`，禁止改回路径——`generate_contracts.py` 第 540 行 `if not physical: skipped_count += 1; continue` 会自动跳过生成。
- **禁止重建连字符目录**：`src/zephyr/system-telemetry/`（连字符）是历史 codegen 死代码目录，Python 无法 import 连字符目录名，MUST NOT 重建。新增 system_telemetry 相关模块 MUST 放在 `src/zephyr/infrastructure/system_telemetry/`（下划线）下。
- **pre-commit 阻断**：`gate-contract-physical-path` 钩子（[.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml)）在 `cross_layer_contracts.yaml` 变更时触发 [`check_contract_physical_path.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_contract_physical_path.py)，检测 `physical_path` 指向连字符目录（如 `system-telemetry`）→ hard block (exit 1)。
- **capability 反查**：`capability_canonical_file_registry.yaml` 已登记 `system_telemetry_metrics_collector` / `system_telemetry_logs_sink` / `system_telemetry_traces_span` / `system_telemetry_health_probe` 四条能力，canonical 均指向 `src/zephyr/infrastructure/system_telemetry/` 下对应文件。新 AI 想做"遥测指标采集/日志持久化/链路追踪/健康探针"前，CapabilityLookup 会反查阻止重复造轮子。
- **observability/ 模块边界**：[src/zephyr/infrastructure/observability/](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/observability/) 仅含 `notifier` + `trace_decorator` 两个模块，不再有 `contract_metrics.py` / `health_probes.py`（已作为 codegen 死代码删除）。新 AI 不要在 observability/ 下重建这两个文件。

**路径命名约束（全仓库治本，2026-06-28）**：
- **下划线唯一合法**：`docs/02_enterprise_architecture/` 下的目录名 MUST 使用下划线：`architecture_model/`（不是连字符 `architecture-model/`）。
- **历史病根**：路径重命名（连字符→下划线）时漏改 48 个 .py 文件，导致 `gate-c2-contract-code-drift` 钩子空跑数月（找不到文件就 WARN 跳过返回 PASS），`check_contract_code_drift.py` 的 `_REPO_ROOT = parents[3]` 也少算一层。本次治本：48 文件机械替换 + `_REPO_ROOT` 改为 `from _shared.constants import REPO_ROOT` 真源常量 + 基线重新冻结。
- **pre-commit 防复发**：`gate-path-naming` 钩子（[.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml)）用 pygrep 检测 .py 文件中含 `architecture-model` → hard block。新 AI 不要在 .py 文件中写连字符路径，MUST 用下划线 `architecture_model`。
- **REPO_ROOT 真源唯一**：scripts/ 下脚本 MUST `from _shared.constants import REPO_ROOT` 获取仓库根常量，禁止 `Path(__file__).resolve().parents[N]` 自行推算（易错且违反 SSoT）。

**P3 遗留项登记**（第二轮第一性原理审查 2026-06-28）：

> **本节是 P3 第二轮审查后的遗留项硬约束。** 任何 AI 在涉及 code_context indexer 或 health_probes 修复前必须先读本节。
> 真源：[p3_t1_code_context_indexer_task_card.md §0](file:///d:/ZephyrAlpha/docs/_working/p3_t1_code_context_indexer_task_card.md) + [health_probes_stub_disposition.md §0](file:///d:/ZephyrAlpha/docs/_working/health_probes_stub_disposition.md)

#### 遗留项-1：code_context indexer 暂缓施工

- **状态**：Suspended（暂缓施工，消费方为零）
- **前置条件**（满足任一方可重新评估）：
  1. CE 接入 VMS：[context_engine.py](file:///d:/ZephyrAlpha/src/zephyr/shared/context_engine.py) 从 stub 升级为真实接入 VMS/hybrid_retriever
  2. Agent 增加 code_search 工具：autonomy_core 的 Agent 工具集新增显式消费 code_context collection 的工具
- **施工硬约束**（解除暂缓后若施工必须遵守）：
  1. writer 路径必须用 `col.upsert + 确定性业务 id`，**禁用** [write_with_provenance](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/collection_manager.py#L446) 的 `col.add + uuid` 路径（会制造 90 天重复垃圾）
  2. AST 分块必须扩展 [chunk_strategy_router.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/chunk_strategy_router.py) 的 `_ast_aware_chunk` 方法，**禁用**新建独立分块函数
  3. AST 解析必须复用 [symbol_index.py](file:///d:/ZephyrAlpha/src/zephyr/governance/symbol_index.py) 的 `ast.parse + ast.walk` 模式
  4. GATE-CODE-CONTEXT reconciler 仅在消费方就绪后注册，避免死代码
- **替代方案**：L1 IDE 场景已由 trae `SearchCodebase` 工具覆盖（语义搜索 + 实时代码库索引，覆盖 src/zephyr/，零成本零维护）
- **新 AI 警告**：勿尝试"修复"或"实现"本 indexer——在消费方为零时建 indexer 是往黑洞灌数据，违反 RULE-THREE 功能价值审判

#### 遗留项-2：health_probes database 探针治本

- **状态**：务实搁置（stub 已降级 Maturity=prototype + 行内注释标记，不修不删）
- **诚实定位**：本搁置是**务实搁置（pragmatic deferral）非治本（root-cause fix）**。真正的治本需要修复 HealthAggregator 调用方 + 补 wal_checkpoint_lag 采集器 + 补 API 消费者
- **搁置理由**：P3-T4 裁定 PG 健康检查真源迁移至 `verify_schema_health.py` 校验4（事件驱动，pre-commit），完整修复 health_probes 会违反 trae_053 常驻监控禁令
- **触发条件**（满足任一可重新评估）：
  1. 项目部署到生产环境，需要常驻健康监控（trae_053 可能有例外条款）
  2. verify_schema_health.py 校验4 无法覆盖某些运行时场景（如 WAL 复制延迟）
  3. 出现 API 消费者需求（如 dashboard 展示健康状态）
- **新 AI 警告**：勿尝试"修复"此 stub——它是项目治理层选择事件驱动路线后留下的协议层化石，修复会违反 P3-T4 裁定。PG 健康检查真源在 `verify_schema_health.py` 校验4

#### 遗留项-3：write_with_provenance 治本（已治本，2026-06-28）

- **状态**：已治本（5 阶段全部完成，8 commits）
- **问题本质**：[collection_manager.py:446-468](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/collection_manager.py#L446) 的 `col.add + uuid` doc_id 路径是 VMS 全局设计缺陷，影响所有 HOT collection（decisions/lessons/knowledge/rules/code_context）。同一内容 commit N 次堆 N 份重复 doc，TTL 到期才清理
- **正确范式**：[kb_repo._upsert_vector](file:///d:/ZephyrAlpha/src/zephyr/intelligence/model_evaluation/kb_repo.py#L399) 的 `col.upsert + 确定性业务 id`（同 id 覆盖，零垃圾）
- **治本动作**（8 commits）：
  1. S1 `6797764c`：write_with_provenance 加 doc_id 入参 + col.add→col.upsert
  2. S2A `6eb1019c`：vector_bridge 5 处补确定性 doc_id
  3. S2B `fd80aaa5`：retrieval_feedback 2 份 + vms_memory_backend 补 doc_id
  4. S2C `dc7a9925`：mcp + infrastructure vector_memory_server 补 doc_id 透传
  5. S2D `2d513d37`：sync_engine + memory_writer + context_ingest 补 doc_id
  6. S3.0 `12c522e9`：integration 版缺陷修复（COLLECTION_ALIASES + datetime import + snapshot_backup 完整实现）
  7. S3.1 `306dbb2f`+`01377504`：governance/vector_memory 整包删除 + 91 处 import 重定向 + context_ingest 移植
  8. 风险B `548e8638`：write_failure_pattern 提取稳定 root_cause 作 pattern_text（治本内容哈希无效问题）
- **真源声明**：integration/vector_memory/ 是 VMS 唯一真源；governance/vector_memory/ 已删除（2026-06-28）
- **遗留子项**：已全部治本（2026-06-28 补充施工）——(1) faiss_collection_manager.write_with_provenance 死代码已删除（零调用方，FAISS 启用时按 CollectionManager 真源签名重新实现）；(2) test_vms_full_e2e.py 破损冗余测试已删除（VMS API 测试由 test_vms_lifecycle.py 22 测试覆盖，FAISS 测试由 benchmark_vms_e2e.py + benchmark_vms_v2.py 覆盖）；(3) 蓝图 L500 签名已同步补 doc_id
- **新 AI 警告**：
  1. 勿重建 governance/vector_memory/ 目录——它是已删除的漂移副本，integration/vector_memory/ 是唯一真源
  2. 勿补全 faiss_collection_manager.write_with_provenance——它是零调用方死代码，FAISS 启用时按 CollectionManager 真源签名重新实现（勿在 FAISS 未启用时提前补全）
- **pre-commit 防复发**：`gate-vms-ssot` 钩子（[.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml)）三重检测——① 检测 staged 文件路径前缀 `src/zephyr/governance/vector_memory/`（大小写不敏感）→ hard block (exit 1)，治本 SSoT 双向漂移防复发；② AST 扫描 `src/zephyr/integration/vector_memory/` 下 .py 防重建 snapshot 方法（详见遗留项-4）；③ AST 扫描防重建 `write_with_provenance` 方法（faiss_collection_manager.py 死代码防复发）

#### 遗留项-4：VMS 快照功能删除治本（已治本，2026-06-28）

- **状态**：已治本（snapshot 功能整体删除——从"修 bug"升级为"删功能"）
- **问题本质**：[index_health_monitor.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/index_health_monitor.py) `snapshot_backup` 三重缺陷叠加：(1) 目标路径在源路径内 → copytree 递归自复制 → 30GB 膨胀；(2) 无 max_snapshots 清理 → 无限堆积；(3) R4 风险被高估（chromadb 1.5.8 SQLite ACID+WAL 已应对断电，R4 审计 6 盲点 F1-F6 与数据损坏无关）
- **第一性原理裁定**：元问题"VMS 需要本地 snapshot 备份吗？"→ 不需要。R4 被 ChromaDB SQLite ACID+WAL 覆盖；snapshot 零消费方（只写不读，无 restore 实现）；死代码（vms_snapshot_backup.py import 断裂）；30GB 灾难根因
- **治本动作**（删除而非修复）：
  1. 删除 [index_health_monitor.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/index_health_monitor.py) 的 `snapshot_backup()`/`_cleanup_old_snapshots()`/`cleanup_snapshots()` 三方法 + unused imports（shutil/Path）
  2. 删除 [in_process_vector_memory.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/in_process_vector_memory.py) 维护线程的 `snapshot_backup()` 调用
  3. 删除死脚本 `scripts/governance/vms_snapshot_backup.py`（import 断裂）+ manifest/naming 白名单条目
  4. 更新蓝图 [blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_domain_knowledge/vector_memory/blueprint.md) / 治理脚本 / 测试（移除所有 snapshot 声明，R4 缓解改为"ChromaDB SQLite ACID+WAL 防断电 + auto_repair()"，删除虚构的"完整性校验/幂等重建/回放重写"声明）
  5. 删除 `data/vector_db/_snapshots/` 30GB 递归垃圾（.NET `\\?\` 前缀瞬间清完 334 层嵌套）
  6. [in_process_vector_memory.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/in_process_vector_memory.py) `last_daily_ts` 初始化修正为 `datetime.now(UTC).timestamp()`（修启动即触发 bug，独立于 snapshot 删除）
- **新 AI 警告**：勿重建 snapshot 备份功能——R4 已被 ChromaDB SQLite ACID+WAL 覆盖，snapshot 是冗余的且是 30GB 灾难根因。数据损坏恢复靠 `auto_repair()` 尝试修复，不走 snapshot（`audit_chain 回放重写` 未实现，勿虚构）
- **门禁**：GATE-VMS-SSOT（[check_vms_ssot.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_vms_ssot.py)）已扩展 AST 检测——重建 `snapshot_backup`/`cleanup_snapshots`/`_cleanup_old_snapshots` 方法名即 hard block

### 11.3 012B 5 组件第一性原理裁定记录（2026-06-28）

> **本节是 012B 数据库 v3.0 组件相关工作的硬约束。** 任何 AI 在涉及 DualDBRouter/WriteBatcher/ScriptScheduler/ScriptRegistry/ScriptExecutionLogger 时必须先读本节。
> 真源：[database/blueprint.md §组件全景](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/blueprint.md)

blueprint.md §组件全景原列 5 个"待施工"组件，经第一性原理审查（19 个问题），裁定如下：

| # | 组件 | 裁定 | 理由 |
|---|------|------|------|
| 14 | DualDBRouter | **删除** | P2 迁移完成，过渡期前提消失；由 [`get_depgraph_pg_connection()`](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py)（PG）+ [`get_db_connection()`](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py)（SQLite）双入口覆盖（无路由器，见 §11.4） |
| 15 | WriteBatcher | **暂缓**（待 L 级） | 真问题（SQLite 单写锁）但 L 级（5000+脚本）需求，当前 S 级 571 脚本无写争抢实证 |
| 16 | ScriptScheduler | **删除** | [BulkheadExecutorV2](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py)（四池+熔断）已覆盖；MOD-INF-005 已有同名组件 |
| 17 | ScriptRegistry | **已覆盖** ✅ | 已由 [_concurrency.py:1292](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py) ScriptRegistry 类覆盖，CT-DB-005 契约对齐现有类 |
| 18 | ScriptExecutionLogger | **暂缓**（待 M-1 级） | 571 脚本已达 M-1 下限 500，纯新增低风险，待 JSONL 查询痛点实证后启动 |

**禁止新建的文件**（违反则为重复造轮子）：
- `dual_db_router.py` — P2 完成，由 `get_depgraph_pg_connection()`（PG）+ `get_db_connection()`（SQLite）双入口覆盖
- `script_scheduler.py`（012B 范畴）— 由 BulkheadExecutorV2 + MOD-INF-005 覆盖

**暂缓清单**（待规模达标启动，不得提前新建）：
- `write_batcher.py` — 待 L 级（5000+脚本）实证写争抢
- `script_execution_logger.py` — 待 M-1 级（500+脚本，当前 571 已达）JSONL 查询痛点实证

**已覆盖清单**（不新建，扩展现有）：
- `script_registry.py` — 已存在于 [_concurrency.py:1292](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py)，CT-DB-005 契约对齐

**跨文档同步修改**（已完成的断链修复）：
- [audit_orchestrator/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md)：DualDBRouter 引用改为 get_depgraph_pg_connection()（PG）+ get_db_connection()（SQLite）双入口
- [shared_core/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/shared_core/blueprint.md)：WriteBatcher 标注"暂缓待 L 级"
- [governance_automation/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/governance_automation/blueprint.md) §36.4/36.5：标注暂缓条件
- [blueprint_registry.yaml](file:///d:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml)：summary 更新

### 11.4 数据库连接函数真源冲突治本（2026-06-28）

> **本节是数据库连接函数的硬约束。** 任何 AI 在涉及 `get_db_connection` 或 `get_depgraph_pg_connection` 时必须先读本节。
> 真源：[depgraph_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) + [db_utils.py](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py) + [sqlite_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/persistence/sqlite_schema.py) + [_shared/constants.py](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py)

**病根**：P2 迁移前 depgraph 是 SQLite，`depgraph_schema.get_db_connection` 命名合理。P2 迁移后变 PG，函数名没改，与 SQLite 的 2 个同名 `get_db_connection` 冲突。文档编造"路由器"语义合理化同名冲突，但实际无路由器。

**治本前的 9 个 import 入口**（3 真实定义 + 5 re-export + 1 wrapper）：

| 函数 | 位置 | 返回 | 目标 DB | 导入点 |
|------|------|------|---------|--------|
| F1 `get_depgraph_pg_connection`（原 `get_db_connection`） | [depgraph_schema.py:1169](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) | psycopg2.conn | **PG** (depgraph) | 42 |
| F2 `get_db_connection` | [sqlite_schema.py:465](file:///d:/ZephyrAlpha/src/zephyr/governance/persistence/sqlite_schema.py) | sqlite3.conn | SQLite (governance) | 70 |
| F3 `get_db_connection`（转发到 F2，治本 2026-06-30） | [db_utils.py:35](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py) | sqlite3.conn | SQLite (governance) | 13 |
| F4 `get_depgraph_pg_connection` | [constants.py:97](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py) | PgConnExecuteWrapper | **PG** (包装 F1) | 29 |

**治本措施**：
1. F1 改名 `get_db_connection` → `get_depgraph_pg_connection`（消除与 SQLite 同名冲突），保留 deprecation 别名 `get_db_connection = get_depgraph_pg_connection`（向后兼容）
2. 16 个 import 文件更新为新名
3. 删除 [blueprint.md:125](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/blueprint.md) 虚假"路由器"语义，改为真实双入口数据流
4. 标注 [p2_postgresql_migration.md:1299](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md) `db_type` 路由器设计稿为"未实现"
5. 新增 F1/F2/F3 存在性断言测试

**新 AI 警告**：
- ❌ **勿按 `db_type` 路由器设计稿补全** F3——会破坏 83 处 SQLite 导入点隐式契约
- ❌ **勿用 SQLite 入口连 PG**——`db_utils.get_db_connection` / `sqlite_schema.get_db_connection` 返回 sqlite3.Connection，连 depgraph 会报 `no such table: nodes`
- ✅ **连 PG 用** `from zephyr.governance.depgraph_schema import get_depgraph_pg_connection`（src 包）或 `from _shared.constants import get_depgraph_pg_connection`（scripts 包，wrapper 兼容 sqlite3 接口）
- ✅ **连 SQLite 用** `from zephyr.shared.utils.db_utils import get_db_connection` 或 `from zephyr.governance.sqlite_schema import get_db_connection`
- ✅ F3 已转发到 F2（治本 2026-06-30，db_utils.py L34-36 `get_db_connection = _mod.get_db_connection`），不再独立定义。F3 作为 shared/utils 公共 API 层保留（避免上层 trading/orchestrator 直接 import governance.sqlite_schema 层级倒置）。12 个 F3 调用点抽查确认用显式事务（BEGIN IMMEDIATE/COMMIT/ROLLBACK），与 F2 autocommit 兼容

#### 治本完成：F3 已转发到 F2（2026-06-30 治本）

- **状态**：已治本（F3 不再独立定义 `get_db_connection`，转发到 F2）
- **治本措施**（2026-06-30）：
  1. `db_utils.py` L34-36 用 `importlib.import_module("zephyr.governance.sqlite_schema")` 转发 `get_db_connection` / `init_db`
  2. F3 文件头 docstring 已标注真源声明（`get_db_connection` / `init_db` 真源为 `zephyr.governance.sqlite_schema`）
  3. F3 作为 `shared/utils` 公共 API 层保留，避免上层（trading/orchestrator 等）直接 import `governance.sqlite_schema`（层级倒置）
- **调用方兼容性验证**（2026-06-30 抽查）：
  - `circuit_breaker_repo.py`：用显式事务 `BEGIN IMMEDIATE`/`COMMIT`/`ROLLBACK`，与 F2 autocommit (`isolation_level=None`) 兼容
  - `file_task_mapper.py`：只读查询 + 显式事务，兼容
  - 其余 10 个调用方同模式（显式事务控制），F3 转发到 F2 后实际运行 F2 autocommit 行为，安全
- **capability 反查**：[capability_canonical_file_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) `sqlite_db_connection` 已更新（`canonical_override` 指向 F2 `sqlite_schema.py`，F3 标记为 `re_export` sanctioned 转发层）
- **新 AI 警告**：
  - ❌ **勿新建第三个 `get_db_connection`**——违反真源唯一
  - ❌ **勿在 `db_utils.py` 重新定义 `get_db_connection`**——会破坏 F3→F2 转发治本
  - ✅ **连 SQLite 用** `from zephyr.shared.utils.db_utils import get_db_connection`（公共 API 层）或 `from zephyr.governance.sqlite_schema import get_db_connection`（真源直连）
