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
| GitCommitGateway | `zephyr.governance.git_commit_gateway` | 全项目唯一合法 git commit 入口（串行锁+stash隔离+GW标记） |
| A2A Protocol | `zephyr.infra_runtime.a2a_protocol` | Agent 间通信与冲突解决（MOD-INF-025） |
| LLM 安全网关（LSG） | `zephyr.security.llm_defense.llm_security.gateway` | L1-L8 十层纵深防御，所有 LLM 调用必经安检（RULE-LSG-001） |
| MCP Servers（10 个） | [`config/mcp.json`](file:///d:/ZephyrAlpha/config/mcp.json) | MCP 服务器注册表（含工具列表/安全等级/ACL/限流） |
| Trigger Router（6 触发器） | [`config/trigger_router.yaml`](file:///d:/ZephyrAlpha/config/trigger_router.yaml) | 事件驱动路由表（含 handler/优先级/重试策略） |

> MCP 服务器完整定义（工具清单/角色权限/熔断配置）见 [`config/mcp.json`](file:///d:/ZephyrAlpha/config/mcp.json)。触发器路由表（6 触发器+处理器+安全等级）见 [`config/trigger_router.yaml`](file:///d:/ZephyrAlpha/config/trigger_router.yaml)。

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
from zephyr.infra_runtime.a2a_protocol import a2a_card_registry
agents = a2a_card_registry.discover(capability="write")

from zephyr.infra_runtime.a2a_protocol.layer2_communication.a2a_schemas import A2AMessage, A2AMessagePart, PartType
msg = A2AMessage(from_agent="your-id", to_agent="target-id", task_id="t-1")

from zephyr.infra_runtime.a2a_protocol.layer3_coordination.conflict_detector import ConflictDetector, ChangeSet
from zephyr.infra_runtime.a2a_protocol.layer3_coordination.arbitrator import Arbitrator, AgentMeta, AgentRole
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

- **真源**：[audit_registration.py](file:///d:/ZephyrAlpha/scripts/governance/audit_registration.py)
- **机制**：扫描磁盘 `.py`/`.yaml` 对比三个注册表，检测孤儿文件 / 僵尸引用 / 缺 `__all__`
- **审计范围（单一真源 `_in_audit_scope`）**：仅 `src/zephyr/` 与 `scripts/` 下文件；其他目录（`tests/`/`docs/`/根级）不扫。`--incremental`、`--files`、post-commit reconciler 三处 scope 过滤统一委托该函数，勿重复实现
- **RULE-TWO 豁免**：被其他模块 `import` 的文件视为"已有自然发现机制"，不报为 ORPHAN。消费者地图由 `_batch_collect_imports()` 构建，扫描范围 `src/`+`scripts/`+`tests/`+**根级 `*.py`**（如 `sitecustomize.py` 是系统级消费者，漏扫根级会导致 RULE-TWO 豁免失效 → 误报 orphan）
  - **消费者地图构建（双路径回退）**：优先使用 `rg`（ripgrep，快速路径），`rg` 不可用时自动回退到 Python `ast` 解析（`_collect_imports_via_ast()`，零外部依赖，跨环境一致）。消除 `rg` 不在 PATH 时静默返回空 map → RULE-TWO 豁免失效 → 误报 orphan 的脆弱性
- **post-commit reconciler**：`make_baseline_aware_reconciler`（[reconciliation_registry.py](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py)）在 commit 后自动触发，用 `--files <committed_files>` 精确扫描本次提交文件
  - **触发条件**：committed_files 含 `src/zephyr/*.py` 或 `scripts/governance/*.py`（注意：比 audit scope 窄，仅 governance 相关 commit 触发）
  - **禁用 `--incremental`**：它会扫工作树全部 WIP（`git diff HEAD` + 未跟踪），把与本次 commit 无关的 WIP 误判为 NEW orphan（历史 Bug：`runtime_interceptor.py` 为 WIP 未提交却被扫到）
  - **scope 过滤单一真源**：reconciler 仅筛 `.py`，scope 过滤委托 audit 的 `_in_audit_scope`（不重复过滤，避免漂移）
- **基线差分**：`--baseline-aware` 对比基线分类 NEW/RESOLVED/PERSISTENT，仅 NEW 阻断（exit 1），PERSISTENT 降级告警（exit 0）
- **双基线系统（勿混淆，防误判漂移）**：
  - `audit_registration_baseline.jsonl` — 本审计独立基线，`meta_path=None`（**从不写** `baseline_meta.json`）
  - `current_baseline.jsonl` + `baseline_meta.json` — `manage_baseline.py` 的独立系统（追踪 `phase_e_full` 等全量基线）
  - 两者独立，`baseline_meta.json` 的 `finding_count` 与 `audit_registration_baseline.jsonl` 行数**无关**，勿误判为漂移

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
- `architecture_model/`（仓库根，单树，2026-06-30 治本合并）: 架构模型 YAML SSoT——53域清单（depgraph 派生）+ 跨层契约（`contracts/`）+ 不变量（`cross_cutting/`）+ `module_id_registry` + 领域事件（`events/`）+ DDD 模型（`domain/`）+ b_track 施工视图（`layers/b_*.yaml`）；53域是唯一物理分类（depgraph），14层（L00-L13）是域的 `layer_id` 属性枚举

### 6.1 target_architecture 目录读写规则

[`docs/02_enterprise_architecture/target_architecture/`](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/index.md) 是 TOGAF 架构视图集 + EA YAML 模型真源区。新 AI 进入此目录前 MUST 读 [`index.md`](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/index.md) 责任声明。

**分区与真源映射**（违反 = 漂移源）：

| 子目录/文件 | doc_type | 数据流方向 | 治本铁律 |
|------------|---------|-----------|----------|
| `overview.md` ~ `frontend_architecture.md` (14 视图) | architecture_view | 手工撰写 | 视图解释 why；结构化数据 MUST 引用 YAML/depgraph，禁止硬编码会变数字（如域数）|
| `architecture_principles.md` | architecture_view | 手工撰写 SSoT | 架构原则唯一真源（R1-R4 安全红线 + BvB + 准入铁律），其他文件引用只读 |
| `architecture_endgame_locked.md` | architecture_view | 手工撰写（status: Draft 占位）| 终局验收标准 + Emergency Change Board 协议；激活需 Owner 手动转 Active |
| `dimension_audit_matrix.md` | audit_report | 手工撰写 + 脚本消费 | 12 维架构评分矩阵；[`score_architecture.py`](file:///d:/ZephyrAlpha/scripts/governance/score_architecture.py) `AUDIT_MATRIX_PATH` 真源，禁止删/移位 |
| `session_carryover_schema.md` | gate | 手工撰写（placement_note 标注暂放）| Context Engine 子接口契约；doc_type=gate 与位置不一致是已知折中，14 个引用点不支持迁移 |
| `revision_history.md` | audit_report | 手工撰写（永久归档）| `index.md §10` 完整版归档；§10 仅保留最近 3 条 |
| `architecture_model/` | - | YAML SSoT | 结构化数据真源；53域清单/契约/事件/能力热力图等，禁止手编 MD 同步副本 |
| `architecture_model/cross_cutting/capability_heatmap.yaml` | - | depgraph 派生 | `data_source: depgraph_db`；53域×10能力域矩阵，禁止手编 |
| `diagrams/` | - | Mermaid 图源 | 仅 .mmd；非 Mermaid 图表不入库；`index.md` 文件清单登记 |

**新 AI 防漂移 5 条**：
1. **找文件先读 `index.md` §3 文件清单**——target_architecture 下所有文件 MUST 在 index.md §3 登记；新文件创建 MUST 同步登记。
2. **结构化数据从 `architecture_model/` YAML 或 `depgraph` 派生**——禁止在 .md 视图中硬编码会变化的数字（如 53域、模块数、节点数）。
3. **`generated/` 目录是派生视图**——由 [`generators/`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/) 自动生成，禁止手编；depgraph 变更后由 reconciler 自动重生。
4. **`architecture_model/index.yaml` 的 `domains` 列表是 depgraph 派生**——禁止手编；改 depgraph 后由生成器自动同步。
5. **删除/迁移文件前 MUST `Grep` 全库引用**——target_architecture 下文件被多个脚本/文档活跃引用（如 `score_architecture.py` 真源 `dimension_audit_matrix.md`，[`check_scaffold_exit_gates.py`](file:///d:/ZephyrAlpha/scripts/arch_guard/check_scaffold_exit_gates.py) 真源 `security_architecture.md` §10.2），强删会导致脚本断裂。

## 7. 代码规范

- Python >=3.11, ruff lint, pydantic v2
- 所有新组件**必须**注册 CapabilityCard 到 CapabilityRegistry
- 所有 AI 行为**必须**写入 AiAuditLogger
- 详细编码约束见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)（四条铁律 + 写代码三条）和 [`trae_010_code_naming_organization.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml)（GOV-ENG-001）
- **文件命名规范真源见 [`trae_028_doc_structure_naming.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)（GOV-DOC-003 §N-16）**——创建新文件前 MUST 先 `Grep` 检查项目内是否已存在同名 basename；**N-16 文件名项目内唯一性检测为硬阻断**（不受 GATE-11 `--warn-only` 过渡期影响），覆盖 `tests/` + `docs/` 目录，commit 时 pre-commit 钩子自动检测；同名文件导致 AI 无法确定真源产生漂移（如 `capability_heatmap.md` 曾存在两个不同内容同名文件，19315 vs 11966 字节）；**N-16 豁免清单（conftest.py/__init__.py/index.md 等）真源为 §gov_doc_003_filename_uniqueness.n16_config，`check_naming_convention.py` 从此动态加载（非硬编码），改 YAML 即生效，禁止改代码豁免清单**；**临时沙箱目录（`tests/_tmp_*` / `docs/_tmp_*`，如并发红蓝对抗沙箱 `tests/_tmp_redblue_f2/`）由 `n16_config.skip_dir_prefixes` 豁免（`os.walk` 按目录名前缀 `_tmp_` 剪枝），防沙箱文件与正式文件撞名误触发 N-16 硬阻断卡死并发 commit**
- **module_id/blueprint_id/domain_id 格式校验真源见 [`validate_module_id_naming.py`](file:///d:/ZephyrAlpha/scripts/governance/validate_module_id_naming.py)（裁定#208 三轨制）**——三轨正则（layer-master 轨 MOD-{LAYER}-NNN / 派生轨 MOD-{DOMAIN}[-NNN] 或 D-{DOMAIN}-NNN / 跨域共享轨 SH-{ABBR}-NNN）唯一责任点；`is_valid_module_id(bp_id)` 和 `is_valid_domain_id(domain_id)` 两个公共函数供 `check_naming_convention.py`（GATE-11 N-06）和 `apply_depgraph.py`（NR-002/cmd_rename_domain/cmd_insert_domain）import 复用；**禁止在代码中定义本地 module_id 正则（防真源分裂）**；capability 反查 alias=`validate_module_id_naming`（`capability_canonical_file_registry.yaml` 注册 13 个 aliases 覆盖中英文关键词）
- 治理决策方法论见 [`trae_024_methodology_diagnosis.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml)（PS-STD-011）——含MTH-006诊断反转验证：深挖后MUST回溯初始诊断，不一致时追问"为什么初始诊断错了？"
- 审计脚本质量见 [`quality_standard.md`](file:///d:/ZephyrAlpha/scripts/governance/quality_standard.md)（SCRIPT-QUALITY-001）
- 产出物规格化见 [`trae_030_doc_numbering_metadata.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)（GOV-DOC-011）——`.md` 文档 frontmatter 标准字段：`module_id, title, version, layer, depends_on, tags, **ttl（GATE-15 强制校验）**`。**doc_type 合法值（v3.0.0，10 值）唯一真源见 [`doc_type_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml)**（非 trae_030）；doc_type↔rule_form 映射也在该词表中 per-value 定义。frontmatter 不可删字段完整清单见 [`onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)「绝对不可删的 15 类」
- **所有 `.md` 文档 frontmatter 和 `.py` 文件头部 MUST 含 `ttl` 字段**——2 个合法值：`permanent`（永久）/`task_bound`（任务绑定，完成即删）。判定方法：在永久区路径（`docs/01_policies/`、`docs/02_enterprise_architecture/`、`docs/03_modules/`、`docs/08_knowledge/`）→ `permanent`；否则 → `task_bound`（默认落 [`docs/_working/`](file:///d:/ZephyrAlpha/docs/_working/) 临时区）。详见 [`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) 的 `decision_tree`。
  - `.md` 用 D_md frontmatter（`ttl: permanent`），`.py` 用 A_full/A_test 注释行（`# [TTL] permanent`）。规则定义见 [`trae_047`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml)（A_full 15 字段 / A_test 7 字段）。
  - `.py` 文件 `# [TTL]` 在最后一个 `# [FIELD]` 行后插入；`__init__.py`/`conftest.py` 等无头部文件豁免。
- **生成器豁免区（generator-exempt-zones）**——`docs/02_enterprise_architecture/` 下 4 个子目录是生成器专用路径，生成器可自由创建/删除文件，**新文件跳过 `PROMOTION_BLOCKED` 门禁**（无需 `--allow-promote`）：`00_overview_entry/`、`01_global_architecture_diagram/`、`02_domain_architecture_docs/`、`03_governance_reports/`。真源：[`git_commit_gateway.py _GENERATOR_EXEMPT_SUBDIRS`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 常量 + [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) `outputs` 字段。**不含** `03_governance_reports/domain_id_hyphen_rename_taskcards/`（手工任务卡）和 `04_architecture_principles_decisions/`（手工架构决策目录）。约束：生成器是这些目录的唯一合法修改源（约定，非技术强制）；N-16 文件名唯一性检查仍生效（不豁免）。
- **TTL 校验统一拦截点（真源唯一 / 向内收）**——[`GitCommitGateway._check_frontmatter_ttl()`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 是 ttl 校验唯一真源方法（调用 [`check_frontmatter_metadata.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py) subprocess，内部格式路由：.md→`parse_frontmatter` / .py→`parse_py_header`）。两个合法调用入口：① [`commit()`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)（用户/AI 发起提交，锁前 fail-fast）；② [`_commit_auto()`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)（reconciler 自动提交，锁前 fail-fast）。**reconciler 禁止裸调 `_run_git(["git", "commit", ...])` 绕过 `_commit_auto`**——原 7 个 reconciler 的裸 commit 已全部改调 `_commit_auto`（锁 + 五重 gate：ttl/deprecated/pure_assertion/pure_shim/DCR + GW 标记），ttl 校验无法绕过（详见 §8 L281）。原 `make_ttl_reconciler`（L3 post-commit 冗余层）已删除——它与 L2 调用同一脚本，非独立防线，违反"真源唯一"原则。
- **N-16 检查统一拦截点（真源唯一 / 向内收 v2）**——N-16 文件名唯一性检查逻辑唯一真源在 [`check_naming_convention.py::check_new_files_naming`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py)（增量检查：`git ls-files` 基线，只检测新文件引入的冲突，不阻断历史遗留）。GitCommitGateway [`_check_naming_uniqueness`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 通过 subprocess 调用 `--check-new-full` 模式（与 `_check_frontmatter_ttl` 调 `check_frontmatter_metadata.py` 同模式），**不实现检查逻辑**。治本：消除了原 gateway 内 `_load_n16_exempt_names` + 自实现检查与 `check_naming_convention.py` 的真源分裂（两处加载 YAML 豁免清单，注释自承"改一处改两处"）。豁免清单真源仍在 trae_028.yaml §n16_config，由 check_naming_convention.py 模块级常量动态加载（gateway 不再加载）。fail-open：subprocess 失败/脚本不存在（exit≠0且≠1）时不阻断 commit。
- **REPO_ROOT 真源归一（SSoT）**——仓库根常量唯一真源：[`zephyr.shared.io.paths.REPO_ROOT`](file:///d:/ZephyrAlpha/src/zephyr/shared/io/paths.py)（由 `find_repo_root()` 基于 .git marker 向上搜索，文件移动不 break）。`src/zephyr/**` 包内消费者：`from zephyr.shared.io.paths import REPO_ROOT`；`scripts/**`/`tests/**` 包外消费者：仅允许一次性极简 sys.path bootstrap（N 值固定），随后必须 `from zephyr.shared.io.paths import REPO_ROOT`。**禁止** `Path(__file__).resolve().parents[N]`、`.parent.parent...`、`Path("D:/ZephyrAlpha")` 等任何变体推算仓库根。**唯一豁免**：sys.path bootstrap 上下文（鸡生蛋：需先设 sys.path 才能 import REPO_ROOT）。**强制方式**：GitCommitGateway [`_check_repo_root_usage`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 在 commit 时自动检测 `.py` 文件中的 `parents[N]` 反模式，违规返回 `REPO_ROOT_VIOLATION` 阻断提交（`--no-verify` 绕不过）。**Phase 1（当前）**：仅检查新增（未 git 跟踪）文件，防止新违规进入；**Phase 2**：清理 156 处存量违规后，删除 `_is_git_tracked` 跳过逻辑切换为全量检查。检测逻辑移植自 `_tmp_fix_parents.py`（仅检测不修复，AI 须手动修正后重新提交）。**DB 路径硬编码禁令（P2 PG 迁移治本，2026-06-29）**——`sqlite3.connect("绝对路径.db")` 硬编码数据库连接违规，`_check_repo_root_usage` 模式5 AST 检测阻断（`:memory:` 内存库豁免）。depgraph 连接入口 `get_depgraph_pg_connection()`，governance 连接入口 `get_governance_connection()`。**DB 写入脚本禁用 lock_files.py（P3 防复发门禁，2026-06-29）**——DB 写入用 PG MVCC 事务保护（文件锁对 PG 写无保护作用），`_check_repo_root_usage` 模式6 AST 检测阻断：同一文件内同时出现 DB 写入信号（`import psycopg2` / `get_depgraph_pg_connection` / `get_governance_connection`）+ lock_files import 信号 → 返回 `REPO_ROOT_VIOLATION` 阻断提交（`--no-verify` 绕不过）。规则真源见 [trae_054](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml) §mandatory + [trae_001](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml) §db_write_protocol。
- **ZephyrBaseError 真源归一 + 循环依赖治本（P3 前置，2026-06-29）**——[`zephyr.shared.foundation.errors`](file:///d:/ZephyrAlpha/src/zephyr/shared/foundation/errors.py) 是 `ZephyrBaseError` 体系（13 个 Error 类）唯一真源。原 `integration/shared_08/` proxy 层（含 `foundation/errors.py` re-export shim）已彻底删除（commit b1588d46），真源唯一归一到 `shared.foundation.errors`。**循环依赖根因**：`shared.infra_06.{idempotency,lock,limiter,outbox}` 越层引用 `integration.shared_08.foundation.errors.ZephyrBaseError`，而 `integration.shared_08._patterns` 反向引用 `shared.infra_06.*`，形成双向闭合循环（import-order-dependent 脆性态，先 import infra_06 触发 ImportError）。**治本**：4 个 infra_06 文件改引同层 `shared.foundation.errors.ZephyrBaseError`，切断 `shared→integration` 方向。**新 AI 引导**：新增 Error 子类改 `shared.foundation.errors`（唯一真源）；`shared` 层禁止 import `integration.*`（向下依赖原则）。
- **GATE-PURE-ASSERTION 纯陈述原则门禁（GOV-DOC-016）**——规则文档（`.trae/rules/*.md` + `AGENTS.md`）只含当前有效规则的肯定陈述句，禁止过渡文本（否定陈述句、历史对比描述、迁移标记等）。规则真源及违规词表见 [trae_030 §gov_doc_016_pure_assertion](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml#L533-L563)。强制方式：GitCommitGateway [`_check_pure_assertion`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 在 commit 时正则扫描规则文档，违规返回 `PURE_ASSERTION_VIOLATION` 阻断提交（`--no-verify` 绕不过）。历史版本差异通过 git log 追踪，不写入正文。检测范围：AI 直接消费的规则入口（`.trae/rules/` + `AGENTS.md`）；YAML 规则定义文件（`docs/01_policies_and_standards/rules/`）的纯陈述治理由 rules_integrity_reconciler 独立负责。
- **`docs/_working/` 新增 .md 文件 MUST 在 frontmatter 声明 `completes_when` 字段**（可验证的完成条件），GitCommitGateway commit 时自动拦截缺失该字段的新文档；规则真源见 [trae_028 §归档与废弃流程](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)。
  - 自动归档由 [GATE-WORKING-DOCS reconciler](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py) post-commit 事件驱动（capability_id：`working_docs_ghost_ref_archiver`，反查用法见 §9）。
- **读取 `docs/_working/` 下任何 .md 前 MUST 验证文档引用的脚本/YAML/blueprint_id 是否仍存在**（防幽灵引用漂移），细则见 [GATE-WORKING-DOCS reconciler](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py)（`scan_and_archive_working_docs` 幽灵引用检测）。
- **归档区 `docs/_archive/`（永久保留历史文件）**——归档触发条件采用二分法判定树（禁止凭"感觉不再需要"归档），所有永久区(01/02/03/08)的文件归档统一归此：

  **判定树（按顺序回答，命中即归档；两个问题均答 NO 则保留原位）**：

  - **Q1 替换归档**：是否存在新文件 Y 承担与目标文件 X 相同的职责，且 Y 是 X 的真源继任者（典型场景：md 规则→yaml 规则重写、旧脚本→新脚本重写、模块拆分合并）？
    - **YES → 执行替换归档**：① `git mv X docs/_archive/`；② 扫描全库引用点（.md/.yaml/.json/.csv），所有指向 X 的引用 MUST 更新为指向 Y（新真源）；③ frontmatter `ttl: permanent` + `status: deprecated`。
    - **NO → 进入 Q2**。

  - **Q2 删除归档**：目标文件 X 是否属于下线资产（功能下线 / 模块移除 / 脚本停用，且全库无活跃引用点）？
    - **YES → 执行删除归档**：① `git mv X docs/_archive/`；② 扫描全库引用点（.md/.yaml/.json/.csv），所有指向 X 的引用 MUST 从源头删除（无继任真源，不指向新文件）；③ frontmatter `ttl: permanent` + `status: deprecated`。
    - **NO → 保留原位**（X 仍有活跃职责，不归档）。

  **核心原则**：真源唯一——文件有继任者时，目标文件保留在原地 = 双真源并存 = AI 漂移，MUST 移走。归档区在 [`directory_contract.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml) `directory_zones.permanent.paths` 中（default_ttl=permanent），`validate_document_ttl.py --list-all-non-permanent` 不列为清理候选。**`docs/_archive/` 是唯一合法归档区**——禁止在 `docs/` 下创建其他归档目录。归档后引用断裂由 [GATE-DOC-REF](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/audit_broken_links.py) 门禁在 commit 时检测断链并阻断。
- **共享能力真源位置**——跨层共享能力（errors / paths / yaml_utils / infra_06 等）真源在 [`src/zephyr/shared/`](file:///d:/ZephyrAlpha/src/zephyr/shared/)。新增共享能力 MUST 直接在 `src/zephyr/shared/` 创建或扩展，**禁止在 `src/zephyr/integration/` 下创建 `shared_*` proxy 层**（CapabilityLookup 反查 `shared.foundation.errors` / `shared.io.paths` 等能力可定位真源，`check_capability_duplicates` 在 commit 时自动检测 basename 撞 capability_id/alias）。`src/zephyr/shared/` 禁止 import `integration.*`（向下依赖原则，详见 §7 ZephyrBaseError 真源归一）。
- **禁止纯 re-export shim 文件（GATE-NO-PURE-SHIM，治本漏洞1，2026-06-29）**——禁止新建纯 re-export shim 文件（`from zephyr.shared.* import *` 无实质代码的 .py 文件）。纯 shim 是真源分裂温床——AI 看到两个 import 路径指向同一符号，无法确定真源产生漂移。**判定标准**：AST 白名单分析，技术细节（哪些节点算实质代码、哪些不算）以 [`check_pure_shim.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_pure_shim.py) 的 `is_pure_reexport_shim()` 函数为**唯一真源**，本规则文档只描述"做什么"（禁止纯 shim），不重复描述"怎么做"（白名单判定逻辑），避免规则文档与代码分裂。**合法例外**：①`__init__.py` 包聚合 ②临时过渡 shim（文件头部含 `# [TTL] task_bound` + `# [DEPRECATED]` 标记，有 TTL 自动清理机制）。**强制方式**：[`check_pure_shim.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_pure_shim.py) GATE-NO-PURE-SHIM pre-commit 钩子，commit `src/zephyr/**/*.py` 时自动检测（`--no-verify` 绕不过 GitCommitGateway Python 层门禁）。
- **禁止附带性 re-export（SSoT 治本 D1，2026-06-30）**——模块 import 符号仅供自身使用，禁止成为该符号的下游再导出点。例如 `from zephyr.shared.io.paths import REPO_ROOT` 后，其他模块 MUST 从 `zephyr.shared.io.paths`（真源）或 `_shared.constants`（sanctioned re-exporter）import，而非从本模块再 import。**唯一 sanctioned re-exporter**：[`_shared/constants.py`](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py)（scripts/ 域 SSoT 桥接层，re-export REPO_ROOT/DB_PATH 等常量给 scripts/ 域使用）。病根：模块为自身使用 import 常量后，下游从该模块 import 同一符号 → 多 import 路径 → AI 无法确定真源 → 漂移。与 GATE-NO-PURE-SHIM 区别：纯 shim 是"文件只做 re-export 无实质代码"；附带性 re-export 是"文件有实质代码但意外成为 import 路径"。两者均违反真源唯一原则。
- **词表合法值加载规范** → 见 [trae_060 §2 唯一真源与直接消费](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L84-L115)（向内收原则①+②；禁止硬编码/同步复制词表合法值，必须 yaml.safe_load 动态加载；GATE-VOCAB 门禁强制执行）。本节不复制规则文本，仅提供实现层用法示例。
  - **真源实现**（治本1 后）：`src/zephyr/shared/io/yaml_utils.py` 提供 `load_vocabulary_values()` 和 `load_vocabulary_deprecated_map()` 两个函数。`strict=True` 默认 fail-fast，文件不存在抛 `FileNotFoundError`（消除静默失败 DoS 漂移）。
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
  - **配套门禁**：**GATE-VOCAB** 已接入 [`.pre-commit-config.yaml` L286-303](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L286-L303) 作为 pre-commit 钩子（`id: gate-vocab-hardcode`，`--ci` 硬阻断模式，2026-06-26 违规清零后转），`src/zephyr/**/*.py` 或 `scripts/**/*.py` 变更时自动触发。AST 扫描检测 `VALID/ALLOWED/LEGAL/PERMITTED_*_VALUES/STATUSES/TYPES/LEVELS/LAYERS/TTL/CATEGORIES/CLASSIFICATIONS/LIST/SET` 模式的字面量硬编码（含 `dict()/list()/tuple()/"a,b".split()` 隐式字面量 + walrus 操作符）+ `load_vocabulary_values("xxx.yaml")` 引用文件存在性校验。例外：DDL 文件（`sqlite_schema.py` 等）走 DDL-as-Code 协议；`_archive/` 排除；**`# noqa: gate-vocab`** 内联豁免（带理由的诚实豁免，非偷偷绕过）。门禁真源见 [trae_060 §5 prohibition_list](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L189-L213)。**注意**：§5 中 "23处(9词表)" 的 evidence 举例已过时（2026-06-26 审计确认所有举例文件已不存在或已修复，GATE-VOCAB 实时扫描 0 违规），审计报告见 [`docs/_working/trae_060_s5_evidence_audit.md`](file:///d:/ZephyrAlpha/docs/_working/trae_060_s5_evidence_audit.md)。新 AI 应以 GATE-VOCAB 实时扫描结果为准，而非 §5 的快照式列举。
  - **capability 反查注册表**已登记 2 条能力（`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`）：`vocabulary_values_loader`（canonical = `src/zephyr/shared/io/yaml_utils.py`）+ `vocab_hardcode_detector`（canonical = `scripts/governance/d3_metadata/check_vocab_hardcode.py`）。新 AI 创建词表加载器或硬编码检测器前，CapabilityLookup 会反查阻止重复造轮子。
- **pre-commit hook id 唯一性门禁**（GATE-ID-UNIQ）→ 历史教训：commit a09e510ec6 中两个 SSoT 门禁同用 `id: gate-ssot`，后者覆盖前者导致 `src/zephyr/*.py` 检测静默失效。已加自动化门禁防止未来 AI 再造重复 id：
  - **pre-commit 阻断层**：[`.pre-commit-config.yaml` L209-224](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L209-L224) `id: gate-id-uniq`，改 `.pre-commit-config.yaml` 时自动触发 [`check_precommit_id_uniqueness.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py) 扫描所有 `repos[].hooks[].id`，same-repo 重复 → hard block (exit 1)，cross-repo 重复 → warn。
  - **post-commit 兜底层**（治本改进点2）：[`reconciliation_registry.py` `make_precommit_id_uniqueness_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py) priority=250，`--no-verify` 绕过 pre-commit 后，commit `.pre-commit-config.yaml` 时自动重校，违规报告落盘 `.runtime/reconcile_reports/id_uniqueness_<ts>.json`（非阻断，供追责）。
  - **capability 反查**已登记 `precommit_id_uniqueness_check`（canonical = `scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py`）。新 AI 想做"检测 yaml id 唯一性"前，CapabilityLookup 会反查到本脚本，提示"扩展本脚本（加 `--target` 参数），勿新建 checker"。
  - **脚本自篡改纵深防御**（A+C 双层，治脚本自篡改缺口）：检测脚本（如 `check_precommit_id_uniqueness.py`）的检测逻辑被 AI 直接删改时，pre-commit hook 和 reconciler 共用同一脚本，两层防线同时失效。本防御补此缺口：
    - **A 层（主防线）**：[`git_commit_gateway.py` `_check_protected_script_integrity`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 在 commit 前用 AST 校验受保护脚本的关键结构锚点（函数/常量）是否仍在。`--no-verify` 绕不过（gateway 内嵌校验，对标 `_check_ssot_canonical` 模式）。锚点缺失/脚本删除 → `SCRIPT_INTEGRITY_VIOLATION` 阻断。锚点清单真源：[`capability_canonical_file_registry.yaml` `integrity_anchors`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) 字段（fail-open 回退硬编码）。当前受保护脚本：`check_precommit_id_uniqueness.py`（4 锚点：`_HOOK_ID_RE`/`_scan_hook_ids`/`_classify_duplicates`/`main`）。**空桩校验增强**（红蓝发现2 治本）：A 层原只校验模块级 name 存在，攻击者可保留 name 但清空实现（`def f(): pass` / `return []` / `_X = None`）绕过。已升级为 `defined_nodes` 映射 + `_has_substantial_body`（FunctionDef body 含 For/While/If/With/Try/Expr+Call/Assign/非空 Return）+ `_assign_has_substantial_value`（Assign value 非 None/非空串）实质性校验，空桩必被检出。（元问题：A 层原校验是**形式校验**——只查 name 在不在；空桩校验升级为**实质校验**——查 name 背后的逻辑是否还在。形式合规但实质失效是纵深防御的常见盲区。）
    - **C 层（兜底）**：[`.pre-commit-config.yaml` `gate-rules-integrity`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) pre-commit 钩子，改 `AGENTS.md` 或 `scripts/governance/` 下文件时触发 [`validate_rules_integrity.py --check`](file:///d:/ZephyrAlpha/scripts/governance/meta/validate_rules_integrity.py) golden hash 校验（exit 2 硬阻断）。覆盖不走 gateway 的裸 commit 路径 + 检测"保留锚点名但篡改内部逻辑"的精细攻击。受保护文件清单：`RULES_MANIFEST`（validate_rules_integrity.py 内声明）。**基线自动同步**（红蓝发现1 治本）：`rules_integrity_db.json` 不被 git 跟踪，合法 commit 修改 RULES_MANIFEST 文件后基线不自动更新 → `--check` 误报 TAMPERED 阻断裸 commit。已加 [`make_rules_integrity_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py) priority=270 post-commit 自动 `--register` 重注册基线（trigger 总是触发——第一性原理：--register 仅 hash RULES_MANIFEST 文件，毫秒级，不值得为省此开销引入路径假设；RULES_MANIFEST 真源在 validate_rules_integrity.py 内）。A 层空桩校验已先行通过，故重注册的基线是"已验证合法"状态——消除误报同时不削弱篡改检测。
    - **register 基于 git HEAD**（红蓝发现3 治本）：原 `register()` 基于工作树状态（`_hash_file`）注册基线——攻击者篡改受保护脚本后 commit 无关文件，post-commit `--register` 会把 WIP 篡改注册为新基线（合法化篡改）。已改为基于 `git show HEAD:<path>` hash（[`_hash_git_head`](file:///d:/ZephyrAlpha/scripts/governance/meta/validate_rules_integrity.py)），只注册已 commit 的 HEAD 状态；工作树 WIP 篡改不进基线。`check()` 仍用 `_hash_file` 基于工作树状态（检测 WIP 篡改）。新文件不在 git HEAD 时回退 `_hash_file`。
    - **--register 门禁**（红蓝发现4 治本）：`--register` 重置基线 = 合法化当前状态，是危险操作。原无门禁，可手动任意重置（合法化篡改）。已加环境变量门禁：`ZEPHYR_RECONCILER_MODE=1`（对标 `ZEPHYR_COMMIT_GATEWAY=1` 模式）。只有 [`make_rules_integrity_reconciler._reconcile`](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py) 调用时设置此令牌才允许 `--register`；手动 `python validate_rules_integrity.py --register` 不设置 → `sys.exit(1)` 阻断。
    - **fail-open 不静默**（红蓝发现6 治本）：[`_load_protected_scripts`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 原 `except Exception: pass` 静默吞掉 YAML 解析异常——YAML 损坏（可能是篡改信号）不可见。已改为 `except Exception as e: logger.warning(...)`。fail-open 策略保留（回退硬编码，避免 registry 损坏导致全项目 commit 瘫痪），但异常可见供追责。
    - **残留缺口（诚实记录）**：自指悖论——gateway 本身能被改，但改 gateway 触发 `gate-triple-align`/`gate-reg-bl` 等门禁且 `[SAFETY] M` 受保护；validate_rules_integrity.py 自身可被改，但它不在自身 RULES_MANIFEST 内（避免自指死锁）。这是可接受的架构权衡，非彻底治本。
    - **capability 反查**：`integrity_anchors` 字段在 `precommit_id_uniqueness_check` 能力条目下声明。新增受保护脚本时：①YAML 加 `integrity_anchors` + `canonical_override` ②gateway `_load_protected_scripts` 回退硬编码同步更新 ③`validate_rules_integrity.py` `RULES_MANIFEST` 加条目。

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

- **post-commit 规则文件审计 reconciler**（GATE-RULE-FILE-AUDIT + GATE-EXEMPT-ZONE-FM，warn-only，2026-06-30 治本）→ 修改 5 个规则文件（directory_contract.yaml / doc_type_vocabulary.yaml / node_type_vocabulary.yaml / capability_canonical_file_registry.yaml / layer_vocabulary.yaml）会触发 `GATE-RULE-FILE-AUDIT`（[`reconciliation_registry.py` `make_rule_file_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py) priority=700），落盘审计报告到 `.runtime/reconcile_reports/rule_file_audit_*.json`。单独提交豁免区（`docs/_working/`等）下带 frontmatter 的文件会触发 `GATE-EXEMPT-ZONE-FM`（`make_exempt_zone_frontmatter_reconciler` priority=710），检测本应放正式目录却被塞进豁免区的文件。两者均 warn-only（不阻断），报告供人工审查。

- **文档引用完整性门禁**（GATE-DOC-REF）→ 调研发现 AI 在 .md/.csv/.yaml 中编造虚假文件引用（如 dom_gov_001 虚假审计闭环：index.md 列 22 张不存在的任务卡，move_plan.csv 引用 4 个不存在的文件）。已加自动化门禁防止未来 AI 再造虚假引用：
  - **pre-commit 阻断层**：[`.pre-commit-config.yaml` L244-261](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L244-L261) `id: gate-doc-ref`，staged 的 .md/.csv/.yaml/.json 文件触发 [`audit_broken_links.py`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 扫描 markdown 链接 + 纯文本路径 + CSV 列值 + YAML 值 + frontmatter blueprint_id + index.md 清单 + audit_report 审计对象，`--ci` 硬阻断 + `--check-new` 历史豁免（仅阻断本次修改新引入的断链，对比 HEAD 版本，参考 N-16 模式）。
  - **检测范围**：.md（markdown 链接 + 纯文本路径 + frontmatter blueprint_id + index.md 清单 + audit_report 审计对象）/ .csv（列值路径）/ .yaml/.yml（值路径 + 纯文本）/ .json（纯文本路径）。跳过 http/https/ftp/mailto 锚点 URL。
  - **路径解析**：三重尝试——①先相对于文件目录（markdown 链接习惯）②再相对于项目根（CSV/YAML 项目根相对路径）③basename 全局搜索兜底（裸文件名如 blueprint.md 在项目其他目录存在）。注意：index.md 清单检测**禁用 basename 兜底**（本目录契约语义，兜底会掩盖幻觉）。
  - **capability 反查**已登记 `broken_link_detector`（canonical = `scripts/governance/d2_links/audit_broken_links.py`）。新 AI 想做"断链检测/ghost ref/phantom reference"前，CapabilityLookup 会反查到本脚本，提示"扩展本脚本（加提取器函数），勿新建 checker"。
  - **治本 GAP-1**：解决"非 .md 文件（.csv/.yaml/.json）中的路径引用无检测"防护缺口。真源：[`audit_broken_links.py` `_extract_csv_paths`/`_extract_text_paths`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。
  - **治本 GAP-2**：解决"frontmatter.blueprint_id 引用的蓝图是否存在无检测"防护缺口。检测 .md frontmatter 的 blueprint_id 字段值是否在 [`blueprint_registry.yaml`](file:///d:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml) 中存在。空值跳过（合法，如 index.md 无归属蓝图）；格式非法跳过（交给 GATE-11 N-06 三轨制格式校验）。真源：[`audit_broken_links.py` `_check_blueprint_id_exists`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。
  - **治本 GAP-3**：解决"index.md 列出的文件清单是否存在无检测"防护缺口。对名为 index.md 的文件做**严格本地解析**（仅相对 source.parent，禁 basename 兜底——本目录契约语义）。处理 markdown 链接 + `file:///D:/ZephyrAlpha/...` 绝对 URL 两种格式。真源：[`audit_broken_links.py` `_check_index_md_inventory`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。
  - **治本 GAP-4**：解决"audit_report 审计对象存在性无检测"防护缺口。对 doc_type=audit_report 的 .md 文件，校验三类引用：①frontmatter.blueprint_id ②frontmatter.module_id ③正文 MODULE_ID 匹配（MOD-XXX-NNN/D-XXX-NNN/SH-XXX-NNN 三轨制）。自动生成 audit_report（无 blueprint_id 无 module_id）跳过。真源：[`audit_broken_links.py` `_check_audit_report_objects`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。已检出幻觉：ai_12/17/18_report.md 引用不存在的 `MOD-DB_DEPGRAPH_PG`/`MOD-INF`。

## 8. 永远不要做的事

> 完整禁止清单见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) 四条铁律。此处仅列项目宪法级禁令：

- 不要删除 `data/` 下的任何文件
- **数据真源唯一位置（data/ 目录，src/ 禁 data/ 子目录）**：`data/` 是运行态数据（brain passport / audit_logs / telemetry / capability_cards 等）唯一合法存放位置。**禁止在 `src/` 下创建 `data/` 子目录**——双真源漂移根因（历史教训：`src/data/brain/passports/` 与 `data/brain/passports/` 并存导致版本漂移，2026-06-27 清理 commit 36871193）。规则真源见 [trae_047 §gov_eng_002_directory_mapping](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml) 禁止规则；pre-commit 钩子 [`gate-src-no-data`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_src_no_data.py) 自动检测 staged 文件 `src/data/` 路径前缀，`--ci` 硬阻断；GitCommitGateway 内部 [`_check_src_no_data`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 等效校验弥补 `--no-verify` 绕过。
- **文件清理操作规范（禁止只删工作区不 git rm）**：删除文件时必须用 `git rm <file>` 或通过 [`GitCommitGateway --files <deleted_file>`](file:///d:/ZephyrAlpha/scripts/git_commit.py) 提交删除——**禁止只 `rm`/`del` 工作区文件而不 git rm**（会产生 D 悬空文件污染 git status，历史教训：2026-06-27 清理 51 个 D 悬空文件 commit efc2d03b/5f2835bb）。正确流程：`git rm <file>` → GitCommitGateway 提交；或直接 `GitCommitGateway --files <file>` 传 D 状态文件（gateway 第 112-131 行识别 D 场景放行）。
- **临时文件命名规范（_tmp_/_debug_ 前缀 + 用完即删）**：一次性脚本必须用 `_tmp_` 前缀（如 `scripts/_tmp_scan.py`），调试测试必须用 `_debug_` 前缀（如 `tests/_debug_race.py`），任务完成后立即删除。**禁止创建 .bak/.baseline/.backup 备份文件**——用 `git stash`/`git diff` 替代。GATE-ZR [`detect_temp_files.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/detect_temp_files.py) 自动检测 `_tmp_`/`_debug_`/`.bak`/`.baseline` 等模式，`error` 级别硬阻断（`is_clean=False` 拒绝提交）。
- 不要跳过 `CapabilityRegistry.register()`
- 不要修改 `AiAuditLogger` 的已有日志
- 不要创建新模块而不注册到大脑
- **reconciler auto-commit 统一入口（2026-06-30 红蓝对抗治本修订）**：7 个 reconciler（manifest/rule_catalog/registry_index/working_docs/domain_doc/arch_model/vocab_change）的 auto-commit 统一经 [`_commit_auto()`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)，跑五重 gate（ttl/deprecated/pure_assertion/pure_shim/DCR），禁止裸调 [`_run_git(["git","commit",...])`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)。**治本背景**：原 7 个 reconciler 裸调 `_run_git` 绕过 `commit()` 全部 gate 校验，是 DCR 防御盲区——若生成器写到废弃/违规目录（如 `docs/09_audit/`），reconciler 会把违规文件 commit 入 git 历史（DCR-001~007 全失效）。**原"需白名单设计"裁定过时**：L280 原裁定"强制走 _commit_auto 需白名单设计，复杂度收益不匹配"经验证过时——4 个 gate 的校验范围均不误拦 reconciler 提交的机器生成文件：① `_check_frontmatter_ttl` 只校验 `docs/*.md` + `src/scripts/tests/*.py`（不校验 .yaml）；② `_check_deprecated_directories` 只查 `_DEPRECATED_DIRS`（reconciler 不写废弃目录）；③ `_check_pure_assertion` 只校验 `.trae/rules/` + `AGENTS.md`；④ `_check_pure_shim` 只校验 `.py`（reconciler 不写 .py）。**DCR gate 真源复用**：`_commit_auto` 通过 `gate_registry.get("DIRECTORY-CONTRACT")` 获取已注册 GateSpec，调其 check 方法，不复制 DCR 逻辑（真源唯一在 [directory_contract_gate.py](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/directory_contract_gate.py) → [check_directory_contract.py](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py)）。只跑 DCR gate（不触发全部 gate，避免 CLAIM-REQUIRED/HELD-OVERLAP 等对 reconciler 无意义的 gate 误阻断）。**arch_model reconciler 特例**：双树合并（2026-06-30）已完成，`_ARCH_MODEL_INDEX` 已指向根树 `architecture_model/index.yaml`，DCR gate 不再触发 NAMING_VIOLATION（原 EA 树旧路径特例降级逻辑已无触发场景，保留 warn 降级作为防御纵深）。**新增 gate 同步评估**：新增 pre-commit gate 时 MUST 评估 `_commit_auto` 是否需要同步——`_commit_auto` 只跑五重 gate（ttl/deprecated/pure_assertion/pure_shim/DCR），新增 gate 若涉及机器生成文件的安全约束（如目录/扩展名/内容校验），MUST 在 `_commit_auto` 中同步加入（对标 DCR gate 的 `gate_registry.get` 复用模式）；若 gate 仅对人工提交有意义（如 claim/overlap/promote），则不同步（`_commit_auto` 无 session claim 语义）。判断标准：reconciler 是否会提交该 gate 关心的文件？
- **GitCommitGateway 僵尸锁自愈**：全局锁 `_GlobalCommitLock` 获取前先调 [`is_pid_alive(pid)`](file:///d:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py) 检查持有进程存活——进程崩溃时锁文件残留，PID 已死则立即清理（零窗口期），不靠 TTL 30min 过期。`is_pid_alive` 真源唯一在 [`process_pool.py`](file:///d:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py)（红蓝对抗归一：曾三处分裂——gateway/ide_health_service/_concurrency 各自定义，现统一；语义最匹配：与 PooledProcess.is_alive / _reap_zombies 同属进程存活检测）。调用方 MUST `from zephyr.shared.infra.process_pool import is_pid_alive`，禁止重复定义（integrity_anchors 保护，capability_id=process_liveness_detection）。
- **GitCommitGateway 中文 aliases 门禁**：commit 时自动调 [`_check_capability_aliases`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 检测 `capability_canonical_file_registry.yaml` 的 aliases 是否含 CJK 字符——禁堆中文同义词 alias 裁定的代码强制，`--no-verify` 绕不过。
- **GitCommitGateway REPO_ROOT 门禁**：commit 时自动调 [`_check_repo_root_usage`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 检测 `.py` 文件两类违规——① `parents[N]` 反模式（`Path(__file__).resolve().parents[N]` / `.parent.parent...` 推算仓库根）；② **AST 检测 missing import**（P2 治本 2026-06-29）：用 `ast.parse` + `ast.walk` 检测使用 `REPO_ROOT`/`DB_PATH`/`find_repo_root` 但未 `from zephyr.shared.io.paths import` 或 import 顺序错误（import 在使用之后）——背景：P2 遗留 5 个 src 文件 missing import 导致 9 个 collection error，此门禁防止复发。`find_repo_root` 于 2026-06-30 D2 收敛期合并进来（原 D2 post-commit reconciler GATE-SSOT-IMPORT-DRIFT 经红蓝对抗审计判定冗余——`_check_repo_root_usage` 是 Python 层 blocking gate，`--no-verify` 绕不过，post-commit warn-only 备份无存在价值，已 revert）。豁免：`from zephyr.shared.io.paths import *` 覆盖；`paths.py` 自身定义合法。`--no-verify` 绕不过（约定见 §7 REPO_ROOT 真源归一）。
- **GitCommitGateway rename fallback（方案 A 治本，红蓝审核 v2 内迁）**：[`_commit_with_file_message`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 是 commit 唯一真源入口，内置 rename 检测（[`_has_staged_renames`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)）+ staged 验证（[`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)）。根因：`git commit --pathspec-from-file` 对 staged rename（R100）拆分为独立 add+delete，只提交 pathspec 匹配部分，破坏 rename。治本：pathspec 为默认（多 session 安全，pathspec 限制范围不捡拾其他 session WIP），检测到目标文件有 rename 时自动切换无 pathspec 模式 + staged 验证（防误提交其他 session WIP）。rename 检测逻辑内迁到 `_commit_with_file_message`（红蓝审核 v2 治本），`_commit_locked` 和 `_commit_auto` 无需重复调用 `_has_staged_renames`，reconciler 路径自动获得 rename 保护（原 `_commit_auto` 无 rename 保护是漏洞）。`_collect_non_target_rel` 已修复 rename 格式 `R old -> new` 的路径解析（提取新路径），确保其他 session 的 staged rename 能被正确 stash。
- **GitCommitGateway staged delete 保护（gitignored 文件 no-pathspec commit，5 层纵深防御）**：[`_commit_locked`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 当目标含 gitignored 文件时（`len(normal_files) < len(files)`）传 `None` 作为 pathspec，用 no-pathspec commit。根因：`git commit -- <pathspec>` 提交**工作区状态**而非**暂存区状态**——对 gitignored 文件，工作区状态无法被 stage（gitignore 阻止），staged delete（`git rm --cached`）被静默跳过。历史教训：commit `32ead90e` 漏提交 5 个 egg_info 删除（staged delete 被吞，只提交了 3 个修改文件）。5 层纵深防御：① [`_is_staged_delete`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 显式识别 staged delete 状态（不在 index AND 在 HEAD），[`_stage_gitignored_tracked`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) existing 分支跳过此类文件，防 `git add -f` 撤销用户的 staged delete；② [`_should_use_no_pathspec`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 检测目标含 gitignored 文件时返回 True（受 integrity_anchors 保护，删则触发 SCRIPT_INTEGRITY_VIOLATION），[`_commit_locked`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 据此切换 no-pathspec commit + [`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 验证 staged 区只有目标文件（防误提交其他 session WIP）；③ [`_collect_non_target_rel`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) + [`_stash_other_files`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) + [`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 用 `os.path.normcase()` 大小写不敏感匹配——`Path.resolve()` 在文件不存在磁盘时无法归一化大小写，导致 staged delete 文件被误判为非目标 → 被 stash 走（Windows 大小写不敏感必须用 normcase）。回归测试 [`TestStagedDeleteGitignored`](file:///d:/ZephyrAlpha/tests/test_git_commit_gateway.py)。新 AI 勿误判 no-pathspec 分支或 `_is_staged_delete` 为冗余删掉——pathspec commit 对 gitignored staged delete 静默丢失是已验证 bug（`_is_staged_delete` 受 integrity_anchors 保护）。
- **GATE-COMMIT-GW 裸 commit 检测门禁（OPS-2026062513 治本，RB-6 修复 2026-06-29）**：[`validate_commit_gateway.py`](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/validate_commit_gateway.py) 是 pre-commit hook（`.pre-commit-config.yaml` gate-commit-gw，`always_run: true`），强制所有 commit 走 GitCommitGateway。**检测逻辑（红蓝修复后）**：hook 运行本身=裸 commit（gateway 用 `--no-verify` 绕过 hook）→ 阻断 exit 1；合并提交（`.git/MERGE_HEAD` 存在）放行。**废除的旧逻辑**：env var `ZEPHYR_COMMIT_GATEWAY=1` 检查（RB-2：env var 在 shell 中持久存在，可绕过）和 commit message `[GW:...]` 标记检查（RB-6：伪造标记可绕过）。**唯一合法绕过**：`git commit --no-verify`（conscious bypass，由 GATE-COMMIT-GW-AUDIT 审计 reconciler 追踪）。**纵深防御**：① 本 hook 拦截非 `--no-verify` 路径 ② post-commit 审计 reconciler 扫描最近 20 个 commit，标记无 `[GW:]` 的裸 commit ③ 过程纪律（code review）。
- **GATE-COMMIT-GW-AUDIT post-commit 审计 reconciler（C级 缺口4）**：[`make_commit_gateway_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py)（priority=800）在每次 commit 后审计最近 20 个 commit，标记无 `[GW:` 标记的裸 commit（merge commit 跳过），报告落盘 `.runtime/reconcile_reports/commit_gateway_audit_<ts>.json`。非阻断（warn），供追责。检测逻辑：`git log -20 --oneline` → 逐行检查 subject 是否含 `[GW:` → 不含则记为 violation。
- **废弃目录门禁 GATE-DEPRECATED-DIR（09_audit 治本加固，红蓝对抗修复）**：双层防御——① [`_check_deprecated_directories`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 在 `commit()` 和 `_commit_auto()` 中内嵌校验，检测提交文件是否位于 `_DEPRECATED_DIRS` 清单中的废弃目录（当前含 `docs/09_audit/`），命中则 `raise NAMING_VIOLATION` 阻断——gateway 内嵌，`--no-verify` 绕不过（对标 `_check_capability_aliases` 模式）；② [`make_deprecated_directory_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py)（priority=600）post-commit **自动修复**（非 warn-only）：检测到 `docs/09_audit/` 存在时，**自动迁移**其中的文件到 `docs/_working/audit/`（`shutil.move`，不覆盖已有文件）+ **自动删除**空目录（`os.rmdir` bottom-up）——空目录 → `action=clean`（彻底消灭）；非空 → 迁移后删除 + `action=warn`（提示迁移文件待 commit）。报告落盘 `.runtime/reconcile_reports/deprecated_directory_<ts>.json`。废弃目录清单真源：`GitCommitGateway._DEPRECATED_DIRS`（reconciler 通过 `getattr(gateway, "_DEPRECATED_DIRS")` 引用，不复制）。integrity_anchors 保护：`_check_deprecated_directories` 已注册在 [capability_canonical_file_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)。**消灭"只告警不消除"**：无论脚本如何 `mkdir docs/09_audit/`，下一次 commit 后 reconciler 自动迁移+清理。
- **审计产物路径引导（09_audit 治本，新 AI 必读）**：审计报告 / session handoff / 安全 finding / 红蓝对抗报告等审计产物**统一写入 `docs/_working/audit/`**（子目录：`handoff/`、`findings/`、`reports/`、`STATE/`）。**禁止 `docs/09_audit/`**——该目录已合并入 `docs/_working/audit/`（[trae_047 gov_eng_002_directory_mapping](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml#L154)）。`doc_type_vocabulary.yaml` 中 `audit_report` 的 `allowed_directories: ["_working/audit/"]`。新 AI 创建审计产物时按此路径引导，违反将被 GATE-DEPRECATED-DIR 阻断。
- **禁止手工创建 YAML tracker（漂移源治本，2026-06-29）**：禁止在 `docs/03_modules/` 下手工创建 `*_tracker.yaml`/`*_matrix.yaml`/`phase_plan.yaml`/`a2a_anomaly.yaml`/`adversarial_test_report.yaml`/`decomposition_completeness.yaml` 等过程态 YAML 文件——这些是漂移源和孤儿，违反真源唯一 + 向内收原则（tra_060）。**真源已在别处**：① 架构数据真源在 [`depgraph`](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py) PostgreSQL 数据库（通过 `apply_depgraph.py` 修改）② 模块版本真源在蓝图 frontmatter `version` 字段 ③ Python 模块状态真源在代码本身（如 `anomaly_detector.py` 是 canonical）④ 决策记录真源在 `git log` + `data/audit_logs/`。**历史教训**：2026-06-29 删除 11 个漂移/孤儿 YAML（commit `0f8fbe21`），它们用 `# ttl: permanent` 注释锚定（非 frontmatter）自欺永久，实际 0 代码消费 0 蓝图注册，内容与 depgraph/蓝图矛盾（如 `version_tracker.yaml` 声明 V1-V40 实际 V1-V5、`blind_spot_tracker.yaml` 157 vs 183 矛盾）。**注释锚定 ≠ frontmatter**：`# ttl: permanent` 注释不受 [`_check_frontmatter_ttl`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) fail-closed 保护，只有 YAML frontmatter `ttl:` 字段才受保护。**新 AI 引导**：如需追踪过程态，扩展已有 Python 模块（向内收）或写入 `docs/_working/`（task_bound，`completes_when` 声明完成条件后自动归档），禁止创建手工 YAML tracker。
- **治本变更未提交前禁止并发 AI 对话（搭便车治本 codify，2026-06-30）**：治本变更（refactor/fix 涉及多文件）在工作区有未提交 WIP 时，禁止开启并发 AI 对话处理同文件——GitCommitGateway 文件级隔离无法分离同一文件内两个 session 的行级修改，后提交的 session 会把工作区全部修改（含前一个 session WIP）一并提交（"搭便车提交"/ghost commit），导致 commit message 与实际内容不符、回滚连带、审计断裂。**历史教训**：commit `abea0b219c`（GATE-ARCH-MODEL）搭便车带入模式6 代码。约束真源见 [parallel_session_coordination_policy.md §3.2](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md) 治本原理。
- **工作区回退风险（编辑阶段覆盖，2026-06-30 Phase D 治本指针）**：≥2 session 并发时，AI 用 IDE Edit/Write 工具直接编辑共享工作区文件——若 session A 已 commit `foo.py`，session B 的 Edit/Write 工具用旧版本覆盖 `foo.py` 工作区副本，session B 下次 commit 会带回退版本（"工作区回退事故"）。**根因**：AI 工具链不读 HEAD 比对，盲目覆盖磁盘。**项目代码层无法治本**（IDE 工具不能 hook，git worktree 物理隔离对 AI 工具链不适用——IDE 工作区固定为项目根）。**治本路径**：≥2 session 并发时 MUST 走 StagingArea 草稿模式（[project_rules.md 多 AI 并发提交协议](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) L161-187，[onboarding_detail.md 模式 B](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)），禁止共享工作区直接 Edit/Write。**取消 B2（workspace_drift_reconciler）裁定**：post-commit reconciler 治不了编辑阶段回退（reconciler 在 commit 后触发，工作区回退发生在 Edit/Write 阶段，检测不到），违反第一性原理，不创造无价值代码（向内收原则①）。**指针**：StagingArea 实现见 [`staging_area.py`](file:///d:/ZephyrAlpha/src/zephyr/trading/staging_area.py)，并发协议见 [`parallel_session_coordination_policy.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md)。
- **commit 前必须 claim_files 声明工作范围（搭便车防护前提，2026-06-30）**：AI session 通过 GitCommitGateway commit 前 MUST 先调 [`claim_files`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 声明本次修改的文件列表——held_files 阻断层（下条）依赖 claim_files 注册的文件归属数据，未 claim 的 session 无法被阻断层检测。CLI 封装 [`scripts/git_commit.py`](file:///d:/ZephyrAlpha/scripts/git_commit.py) 已内置 claim_files → commit → release_files 流程。
- **GitCommitGateway held_files 冲突阻断（搭便车治本，2026-06-30）**：[`commit()`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 时 [`HeldOverlapGate`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/held_overlap_gate.py) 自动检测目标文件是否被其他**活跃** session 持有（通过 [`SessionRegistry.other_held_files`](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/session_concurrency.py)），命中则返回 `HELD_OVERLAP_VIOLATION` 阻断（`--no-verify` 绕不过，在 gateway 内部非 pre-commit hook）。**逃生通道**：`commit(allow_overlap=True)` 或 CLI `--allow-overlap` 显式声明时放行，commit message 追加 `[GW:<sid>:overlap]` 标记供审计追踪。过期 session 的持有自动忽略（TTL=3600s + PID 存活检测）。约束真源见 [parallel_session_coordination_policy.md §3.2/§5.2](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md)。
- **GitCommitGateway 门禁注册制 CommitGateRegistry（架构债务 #AD-001 治本，2026-06-30）**：[`commit_gate_registry.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gate_registry.py) 把 `commit()` 方法体中硬编码的 `_check_*` 调用升级为声明式 registry——新增 pre-commit 门禁只需 `register(GateSpec)`，不改 `commit()` 方法体，消除多 session 频繁修改同一文件（git_commit_gateway.py 2500+ 行）的搭便车冲突源。设计参考 [`ReconciliationRegistry`](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py)（post-commit reconciler 注册表），纯 stdlib 解耦。gate 实现放 [`commit_gates/`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/) 子目录，每个 gate 一个文件 + `make_*_gate()` 工厂函数。**新 AI 添加门禁**：在 `commit_gates/` 下创建 `make_xxx_gate()` → 在 `GitCommitGateway.__init__` 中 `register`，禁止在 `commit()` 方法体硬编码 `_check_*` 调用。
- **GitCommitGateway DIRECTORY-CONTRACT gate（DCR-001~007 等效校验，--no-verify 补偿，2026-06-30 治本）**：[`make_directory_contract_gate`](file:///d:/ZephyrAlpha/src/zephyr/governance/commit_gates/directory_contract_gate.py)（priority=30，在 CLAIM-REQUIRED(40)/HELD-OVERLAP(50) 之前执行）通过 subprocess 调用 [`check_directory_contract.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py) 复用真源——DCR-001~007 校验逻辑唯一在 check_directory_contract.py，gateway 不复制检测代码（对标 [`_check_pure_shim`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) subprocess 复用模式）。**病根**：GitCommitGateway 用 `--no-verify` 绕过 pre-commit hook（GATE-DIRECTORY-CONTRACT），DCR-001~007 防御断层——新 AI 可在 gateway 路径创建违规文件（如根目录 .txt、docs/03_modules/.py）绕过目录契约。本 gate 在 gateway 内部注册制执行等效校验，`--no-verify` 绕不过。**fail-closed**：check_directory_contract.py 缺失/执行失败/超时（60s）时阻断 commit（对标 [`_check_frontmatter_ttl`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 模式，防 checker 被删后静默放行）。文件数 >200 时改用 `--all-files` 全量扫描避免 WinError 206（Windows 命令行长度限制）。**reconciler 路径已覆盖**：`_commit_auto`（reconciler auto-commit 入口）通过 `gate_registry.get("DIRECTORY-CONTRACT")` 复用本 gate 的 GateSpec，调其 check 方法对 reconciler 提交的文件跑 DCR 等效校验（2026-06-30 红蓝对抗治本，见上方"reconciler auto-commit 统一入口"条目）。约束真源见 [directory_contract.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml)。

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

### 11.0 数据库清单真源指针（新 AI 进入项目先读此段）

> **唯一真源**：[`docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml) 的 `infrastructure:` 段（`type` 含 `*_db` 的条目）。
>
> **铁律**：禁止在任何其它文档（蓝图/规则/onboarding/副本）同步数据库清单——所有引用 MUST 用纯指针指向上方真源，禁止摘抄数据库条目作为同步副本。新增/废弃数据库 MUST 先改 infrastructure_registry.yaml，再由 reconciler 派生，禁止反向。违反此铁律会导致 17+ 副本漂移重演（历史教训）。

**新 AI 发现路径**：
1. 想知道"项目有几个数据库/各负责什么" → 直接读 infrastructure_registry.yaml 的 `infrastructure:` 段，禁止凭记忆或其它文档推断。
2. 准备改 DB 连接/新增 DB → 先查真源确认当前状态，再按下方 §11 depgraph 流程或对应模块蓝图施工。
3. 写文档需要提"数据库清单" → 一律用纯指针引用真源，禁止复制条目。

> depgraph 是唯一全景真源（PostgreSQL 16，localhost:5432），禁止创建派生 YAML 副本。连接配置见 `config/.env.postgres`，连接入口 `zephyr.governance.depgraph_schema.get_depgraph_pg_connection()`。遇到 depgraph 相关问题，直接问工具：

- **查 DB 数据** → `python scripts/governance/extract_depgraph.py --help`（场景速查表在 epilog）
- **改 DB 节点/路径** → `python scripts/governance/apply_depgraph.py --help`（35+ 子命令）
- **批量改 DB（多 op 原子事务）** → `python scripts/governance/apply_depgraph.py --batch changes.json`（先 `--dry-run` 预览）。op 清单运行 `--list-ops` 查看（从 `_DOMAIN_OPS`/`_NODE_OPS` 注册表自动派生，真源唯一——禁止手工同步到 docstring/AGENTS.md，§6.16 铁律）；所有 op 共享单一 PostgreSQL 事务，全部成功才 commit，任一失败全部 rollback。批量重命名域 ID 时**禁止**手写 `_tmp_batch_rename.py` 调 `--rename-domain` 单命令循环（失去原子性，部分失败留半成品数据）。
- **查哪些表不能手写** → `python scripts/governance/sync_yaml_to_depgraph.py --list-readonly-tables`
- **文件结构变更后同步 DB** → 自动完成（GitCommitGateway post-commit GATE-PATH-TREE reconciler，无需手动）
- **DB 变更后重生域文档** → 自动完成（GitCommitGateway post-commit GATE-DOMAIN-DOC reconciler，无需手动）
- **改了 YAML 规则文件** → `python scripts/governance/sync_yaml_to_depgraph.py`（覆盖 readonly 表）
- **改了 rules/ 下规则文件后同步 catalog** → 自动完成（GitCommitGateway post-commit GATE-RULE-CATALOG reconciler，无需手动）。catalog 真源：`_registry/catalogs/rule_catalog_registry.yaml`（由 `scripts/governance/d3_metadata/generate_rule_catalog.py` 自动生成，60 条规则元数据；#ARCH-024 治本：原 `rules/_index.yaml` 手工索引已删除）
- **改了 infrastructure_registry.yaml 后同步 registry_master_index** → 自动完成（GitCommitGateway post-commit GATE-REGISTRY-INDEX reconciler，无需手动）
- **查 PG 运行时健康** → `python scripts/governance/verify_schema_health.py --warn-only`（校验4：死锁/连接饱和/长事务，pre-commit 自动跑；`--skip-runtime` 可跳过）

> 改 depgraph 前必须通过 `pg_dump` 或 apply_depgraph.py 内置物理备份（trae_054 STEP0）。DB↔磁盘一致性检查用 `python scripts/governance/diagnose_depgraph.py`。

### 11.1 生成器时间戳约定

> 所有生成器（`scripts/governance/d5_architecture/generators/` 下的 `.py` 文件）输出的文档中，
> 日期字段 MUST 使用 `auto-generated`，最后更新时间 MUST 标注"最后更新以 git log 为准"。
> **禁止在生成器中使用 `datetime.now()` 或任何实时时间源**，否则每次修改 depgraph (PostgreSQL)
> 都会因时间戳变化产生非幂等噪音 auto-commit。

- **真源实现**：所有生成器 docstring `[INVARIANTS]` 声明"输出幂等(相同输入→相同输出);零时间戳"
- **时间真源**：文件修改时间唯一真源是 git log，生成器不引入独立时间源
- **检测**：`Select-String -Path "scripts/governance/d5_architecture/generators/*.py" -Pattern "datetime\.now\(\)"` 应返回零匹配
- **自动触发**：GATE-DOMAIN-DOC reconciler 在修改 depgraph 后自动调用 generate_domain_doc.py 和 generate_domain_dependency_diagram.py 重生域文档，生成器幂等性确保无噪音 auto-commit

### 11.2 P3 PostgreSQL 优化裁定记录（2026-06-28）

> **本节是 P3 相关工作的硬约束。** 任何 AI 在涉及 PostgreSQL 优化时必须先读本节。
> 真源：[P3方案 §裁定记录](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p3_postgresql_optimization.md)

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
- **下划线唯一合法**：`docs/02_enterprise_architecture/` 下的目录名 MUST 使用下划线：`target_architecture/` + `architecture_model/`（不是连字符 `target-architecture/` + `architecture-model/`）。
- **历史病根**：路径重命名（连字符→下划线）时漏改 48 个 .py 文件，导致 `gate-c2-contract-code-drift` 钩子空跑数月（找不到文件就 WARN 跳过返回 PASS），`check_contract_code_drift.py` 的 `_REPO_ROOT = parents[3]` 也少算一层。本次治本：48 文件机械替换 + `_REPO_ROOT` 改为 `from _shared.constants import REPO_ROOT` 真源常量 + 基线重新冻结。
- **pre-commit 防复发**：`gate-path-naming` 钩子（[.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml)）用 pygrep 检测 .py 文件中含 `target-architecture` 或 `architecture-model` → hard block。新 AI 不要在 .py 文件中写连字符路径，MUST 用下划线 `target_architecture` / `architecture_model`。
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
> 真源：[depgraph_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) + [db_utils.py](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py) + [sqlite_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) + [_shared/constants.py](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py)

**病根**：P2 迁移前 depgraph 是 SQLite，`depgraph_schema.get_db_connection` 命名合理。P2 迁移后变 PG，函数名没改，与 SQLite 的 2 个同名 `get_db_connection` 冲突。文档编造"路由器"语义合理化同名冲突，但实际无路由器。

**治本前的 9 个 import 入口**（3 真实定义 + 5 re-export + 1 wrapper）：

| 函数 | 位置 | 返回 | 目标 DB | 导入点 |
|------|------|------|---------|--------|
| F1 `get_depgraph_pg_connection`（原 `get_db_connection`） | [depgraph_schema.py:1169](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) | psycopg2.conn | **PG** (depgraph) | 42 |
| F2 `get_db_connection` | [sqlite_schema.py:465](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) | sqlite3.conn | SQLite (governance) | 70 |
| F3 `get_db_connection` | [db_utils.py:59](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py) | sqlite3.conn | SQLite (governance) | 13 |
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
- ⚠ F2/F3 仍同名 `get_db_connection`（SQLite governance.db），合并需独立任务卡（83 导入点风险高）

#### 遗留项：F2/F3 SQLite 同名冲突（待合并，2026-06-28 登记）

- **状态**：未治本（待独立任务卡，83 导入点风险高）
- **问题本质**：两个文件各有一个 `get_db_connection()`，函数名相同但实现不同：
  - F2 [sqlite_schema.py:465](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py) — governance.db 专用，含 schema 初始化，70 导入点
  - F3 [db_utils.py:59](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py) — 通用 SQLite，接受 db_path 参数，13 导入点
- **未合并原因**：83 导入点（真实 `get_db_connection` 调用点约 51）需逐一迁移验证，风险高，需独立任务卡裁定真源（F2 还是 F3）
- **技术调查推荐方向**（2026-06-28 审查补充，供合并任务卡参考）：**F3→F2（合并 F3 入 F2，F2 作为真源）**
  - 依据①：F2 签名是 F3 超集——F2 含 `check_same_thread`/`timeout` 关键字参数，F3 仅 `db_path` 一参数。F3 调用方迁到 F2 无需改调用代码；反向不成立
  - 依据②：F2 用 `isolation_level=None`（autocommit），被 `database_manager.py` 3 处实现（infrastructure/db/、governance/、governance/persistence/）依赖显式事务控制（BEGIN IMMEDIATE/COMMIT/ROLLBACK）。F3 用默认 deferred 隔离级，无法承接 F2 调用方
  - 依据②补充（F3→F2 迁移风险，2026-06-28 调查）：F3 调用方迁移到 F2 时，依赖隐式事务（多条 DML 在一个事务中自动 BEGIN/需 commit()）的调用方需改为显式 BEGIN/COMMIT，否则 autocommit 下每条 DML 立即提交无法回滚。只读查询（SELECT）迁移安全。DB_PATH 两者一致（`data/databases/governance.db`，F2 自定义 / F3 从 `zephyr.shared.io.paths` 导入）。F3 的 12 个 import 点中含漂移副本（`kb/kb_repo.py` vs `kb/storage/kb_repo.py`、`audit_orchestration/wave_generator.py` vs `audit_orchestration/core/wave_generator.py`），合并前需先清理漂移副本
  - 依据③：实际 `get_db_connection` 调用点 F2=39 处 vs F3=12 处（"70/13"是 [CONSUMERS] 头部所有符号导入数，非真实调用点），迁移 F3→F2 仅需改 12 处，风险更低
  - 依据④：F2 同文件含 `init_db`/`SchemaManager`/`_MIGRATIONS`/`schema_version`，是 governance.db schema 管理唯一综合体；F3 的 `init_db` 是轻量版，docstring 自承"full schema migration support, use F2 directly"
  - **注意**：capability_canonical_file_registry.yaml 当前 `sqlite_db_connection.canonical_override` 指向 F3 是临时占位（登记现状），合并任务卡应按 F3→F2 方向裁定后同步修正
- **触发条件**（任一满足即应启动合并任务卡）：
  1. 出现第三个 `get_db_connection` 实现（违反真源唯一）
  2. F2/F3 行为差异导致 bug（如 schema 初始化副作用不一致）
  3. 调用方误用错误入口导致连接错误 DB
- **capability 反查**：[capability_canonical_file_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) 已注册 `sqlite_db_connection` capability（canonical_override 指向 F3，F2 标记为 conflicting duplicate）。新 AI 搜 `get_db_connection` 可通过 `CapabilityLookup.find()` 定位真源 + 知晓同名冲突
- **新 AI 警告**：
  - ❌ **勿新建第三个 `get_db_connection`**——违反真源唯一，应扩展现有 F2 或 F3
  - ❌ **勿在未读本节时修改 SQLite 连接代码**——可能误用入口
  - ⚠ **合并 F2/F3 需独立任务卡**——83 导入点逐一迁移，勿在本节治本中夹带
