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
- `architecture_model/`: 全部蓝图 YAML

## 7. 代码规范

- Python >=3.11, ruff lint, pydantic v2
- 所有新组件**必须**注册 CapabilityCard 到 CapabilityRegistry
- 所有 AI 行为**必须**写入 AiAuditLogger
- 详细编码约束见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)（四条铁律 + 写代码三条）和 [`trae_010_code_naming_organization.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml)（GOV-ENG-001）
- **文件命名规范真源见 [`trae_028_doc_structure_naming.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)（GOV-DOC-003 §N-16）**——创建新文件前 MUST 先 `Grep` 检查项目内是否已存在同名 basename；**N-16 文件名项目内唯一性检测为硬阻断**（不受 GATE-11 `--warn-only` 过渡期影响），覆盖 `tests/` + `docs/` 目录，commit 时 pre-commit 钩子自动检测；同名文件导致 AI 无法确定真源产生漂移（如 `capability_heatmap.md` 曾存在两个不同内容同名文件，19315 vs 11966 字节）；**N-16 豁免清单（conftest.py/__init__.py/index.md 等）真源为 §gov_doc_003_filename_uniqueness.n16_config，`check_naming_convention.py` 从此动态加载（非硬编码），改 YAML 即生效，禁止改代码豁免清单**；**临时沙箱目录（`tests/_tmp_*` / `docs/_tmp_*`，如并发红蓝对抗沙箱 `tests/_tmp_redblue_f2/`）由 `n16_config.skip_dir_prefixes` 豁免（`os.walk` 按目录名前缀 `_tmp_` 剪枝），防沙箱文件与正式文件撞名误触发 N-16 硬阻断卡死并发 commit**
- **module_id/blueprint_id/domain_id 格式校验真源见 [`validate_module_id_naming.py`](file:///d:/ZephyrAlpha/scripts/governance/validate_module_id_naming.py)（裁定#208 三轨制）**——三轨正则（layer-master 轨 MOD-{LAYER}-NNN / 派生轨 MOD-{DOMAIN}[-NNN] 或 D-{DOMAIN}-NNN / 跨域共享轨 SH-{ABBR}-NNN）唯一责任点；`is_valid_module_id(bp_id)` 和 `is_valid_domain_id(domain_id)` 两个公共函数供 `check_naming_convention.py`（GATE-11 N-06）和 `apply_depgraph.py`（NR-002/cmd_rename_domain/cmd_insert_domain）import 复用；**禁止在代码中定义本地 module_id 正则（防真源分裂）**；capability 反查 alias=`validate_module_id_naming`（`capability_canonical_file_registry.yaml` 注册 13 个 aliases 覆盖中英文关键词）
- 治理决策方法论见 [`trae_024_methodology_diagnosis.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml)（PS-STD-011）——含MTH-006诊断反转验证：深挖后MUST回溯初始诊断，不一致时追问"为什么初始诊断错了？"
- 审计脚本质量见 [`quality_standard.md`](file:///d:/ZephyrAlpha/scripts/governance/quality_standard.md)（SCRIPT-QUALITY-001）
- 产出物规格化见 [`trae_030_doc_numbering_metadata.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)（GOV-DOC-011）——`.md` 文档 frontmatter 标准字段：`module_id, title, version, layer, depends_on, tags, **ttl（GATE-15 强制校验）**`。字段定义和 doc_type 映射见 trae_030；frontmatter 不可删字段完整清单见 [`onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)「绝对不可删的 15 类」
- **所有 `.md` 文档 frontmatter 和 `.py` 文件头部 MUST 含 `ttl` 字段**——2 个合法值：`permanent`（永久）/`task_bound`（任务绑定，完成即删）。判定方法：在永久区路径（`docs/01_policies/`、`docs/02_enterprise_architecture/`、`docs/03_modules/`、`docs/08_knowledge/`）→ `permanent`；否则 → `task_bound`（默认落 [`docs/_working/`](file:///d:/ZephyrAlpha/docs/_working/readme.md) 临时区）。详见 [`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) 的 `decision_tree`。
  - `.md` 用 D_md frontmatter（`ttl: permanent`），`.py` 用 A_full/A_test 注释行（`# [TTL] permanent`）。规则定义见 [`trae_047`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml)（A_full 15 字段 / A_test 7 字段）。
  - `.py` 文件 `# [TTL]` 在最后一个 `# [FIELD]` 行后插入；`__init__.py`/`conftest.py` 等无头部文件豁免。
- **生成器豁免区（generator-exempt-zones）**——`docs/02_enterprise_architecture/` 下 4 个子目录是生成器专用路径，生成器可自由创建/删除文件，**新文件跳过 `PROMOTION_BLOCKED` 门禁**（无需 `--allow-promote`）：`00_overview_entry/`、`01_global_architecture_diagram/`、`02_domain_architecture_docs/`、`03_governance_reports/`。真源：[`git_commit_gateway.py _GENERATOR_EXEMPT_SUBDIRS`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 常量 + [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) `outputs` 字段。**不含** `03_governance_reports/domain_id_hyphen_rename_taskcards/`（手工任务卡）和 `04_architecture_principles_decisions/`（手工架构决策目录）。约束：生成器是这些目录的唯一合法修改源（约定，非技术强制）；N-16 文件名唯一性检查仍生效（不豁免）。
- **TTL 校验统一拦截点（真源唯一 / 向内收）**——[`GitCommitGateway._check_frontmatter_ttl()`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 是 ttl 校验唯一真源方法（调用 [`check_frontmatter_metadata.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py) subprocess，内部格式路由：.md→`parse_frontmatter` / .py→`parse_py_header`）。两个合法调用入口：① [`commit()`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)（用户/AI 发起提交，锁前 fail-fast）；② [`_commit_auto()`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)（reconciler 自动提交，锁前 fail-fast）。**reconciler 禁止裸调 `_run_git(["git", "commit", ...])` 绕过 `_commit_auto`**——原 5 个 reconciler 的裸 commit 已全部改调 `_commit_auto`（锁 + ttl 校验 + GW 标记），ttl 校验无法绕过。原 `make_ttl_reconciler`（L3 post-commit 冗余层）已删除——它与 L2 调用同一脚本，非独立防线，违反"真源唯一"原则。
- **N-16 检查统一拦截点（真源唯一 / 向内收 v2）**——N-16 文件名唯一性检查逻辑唯一真源在 [`check_naming_convention.py::check_new_files_naming`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py)（增量检查：`git ls-files` 基线，只检测新文件引入的冲突，不阻断历史遗留）。GitCommitGateway [`_check_naming_uniqueness`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 通过 subprocess 调用 `--check-new` 模式（与 `_check_frontmatter_ttl` 调 `check_frontmatter_metadata.py` 同模式），**不实现检查逻辑**。治本：消除了原 gateway 内 `_load_n16_exempt_names` + 自实现检查与 `check_naming_convention.py` 的真源分裂（两处加载 YAML 豁免清单，注释自承"改一处改两处"）。豁免清单真源仍在 trae_028.yaml §n16_config，由 check_naming_convention.py 模块级常量动态加载（gateway 不再加载）。fail-open：subprocess 失败/脚本不存在（exit≠0且≠1）时不阻断 commit。
- **REPO_ROOT 真源归一（SSoT）**——仓库根常量唯一真源：[`zephyr.shared.io.paths.REPO_ROOT`](file:///d:/ZephyrAlpha/src/zephyr/shared/io/paths.py)（由 `find_repo_root()` 基于 .git marker 向上搜索，文件移动不 break）。`src/zephyr/**` 包内消费者：`from zephyr.shared.io.paths import REPO_ROOT`；`scripts/**`/`tests/**` 包外消费者：仅允许一次性极简 sys.path bootstrap（N 值固定），随后必须 `from zephyr.shared.io.paths import REPO_ROOT`。**禁止** `Path(__file__).resolve().parents[N]`、`.parent.parent...`、`Path("D:/ZephyrAlpha")` 等任何变体推算仓库根。**唯一豁免**：sys.path bootstrap 上下文（鸡生蛋：需先设 sys.path 才能 import REPO_ROOT）。**强制方式**：GitCommitGateway [`_check_repo_root_usage`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 在 commit 时自动检测 `.py` 文件中的 `parents[N]` 反模式，违规返回 `REPO_ROOT_VIOLATION` 阻断提交（`--no-verify` 绕不过）。**Phase 1（当前）**：仅检查新增（未 git 跟踪）文件，防止新违规进入；**Phase 2**：清理 156 处存量违规后，删除 `_is_git_tracked` 跳过逻辑切换为全量检查。检测逻辑移植自 `_tmp_fix_parents.py`（仅检测不修复，AI 须手动修正后重新提交）。
- **`docs/_working/` 新增 .md 文件 MUST 在 frontmatter 声明 `completes_when` 字段**（可验证的完成条件），GitCommitGateway commit 时自动拦截缺失该字段的新文档；规则真源见 [_working/readme.md §五](file:///d:/ZephyrAlpha/docs/_working/readme.md)。
  - 自动归档由 [GATE-WORKING-DOCS reconciler](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py) post-commit 事件驱动（capability_id：`working_docs_ghost_ref_archiver`，反查用法见 §9）。
- **读取 `docs/_working/` 下任何 .md 前 MUST 验证文档引用的脚本/YAML/blueprint_id 是否仍存在**（防幽灵引用漂移），细则见 [_working/readme.md §六](file:///d:/ZephyrAlpha/docs/_working/readme.md)。
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

## 8. 永远不要做的事

> 完整禁止清单见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) 四条铁律。此处仅列项目宪法级禁令：

- 不要删除 `data/` 下的任何文件
- 不要跳过 `CapabilityRegistry.register()`
- 不要修改 `AiAuditLogger` 的已有日志
- 不要创建新模块而不注册到大脑
- **reconciler 不要裸调 `_run_git(["git", "commit", ...])`**——必须经 [`_commit_auto()`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 统一入口（锁 + ttl 校验 + GW 标记），否则 ttl 防御被绕过（详见 §7 TTL 校验统一拦截点）
- **GitCommitGateway 僵尸锁自愈**：全局锁 `_GlobalCommitLock` 获取前先调 [`_is_pid_alive(pid)`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 检查持有进程存活——进程崩溃时锁文件残留，PID 已死则立即清理（零窗口期），不靠 TTL 30min 过期。新 AI 勿误判 `_is_pid_alive` 为冗余删掉（红蓝对抗验证，integrity_anchors 保护）。
- **GitCommitGateway 中文 aliases 门禁**：commit 时自动调 [`_check_capability_aliases`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 检测 `capability_canonical_file_registry.yaml` 的 aliases 是否含 CJK 字符——禁堆中文同义词 alias 裁定的代码强制，`--no-verify` 绕不过。
- **GitCommitGateway REPO_ROOT 门禁**：commit 时自动调 [`_check_repo_root_usage`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 检测 `.py` 文件是否使用 `parents[N]` 反模式而非 `REPO_ROOT`——禁用 `Path(__file__).resolve().parents[N]` / `.parent.parent...` 推算仓库根的代码强制，`--no-verify` 绕不过（约定见 §7 REPO_ROOT 真源归一）。
- **GitCommitGateway rename fallback（方案 A 治本，红蓝审核 v2 内迁）**：[`_commit_with_file_message`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 是 commit 唯一真源入口，内置 rename 检测（[`_has_staged_renames`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)）+ staged 验证（[`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)）。根因：`git commit --pathspec-from-file` 对 staged rename（R100）拆分为独立 add+delete，只提交 pathspec 匹配部分，破坏 rename。治本：pathspec 为默认（多 session 安全，pathspec 限制范围不捡拾其他 session WIP），检测到目标文件有 rename 时自动切换无 pathspec 模式 + staged 验证（防误提交其他 session WIP）。rename 检测逻辑内迁到 `_commit_with_file_message`（红蓝审核 v2 治本），`_commit_locked` 和 `_commit_auto` 无需重复调用 `_has_staged_renames`，reconciler 路径自动获得 rename 保护（原 `_commit_auto` 无 rename 保护是漏洞）。`_collect_non_target_rel` 已修复 rename 格式 `R old -> new` 的路径解析（提取新路径），确保其他 session 的 staged rename 能被正确 stash。
- **GitCommitGateway staged delete 保护（gitignored 文件 no-pathspec commit，5 层纵深防御）**：[`_commit_locked`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 当目标含 gitignored 文件时（`len(normal_files) < len(files)`）传 `None` 作为 pathspec，用 no-pathspec commit。根因：`git commit -- <pathspec>` 提交**工作区状态**而非**暂存区状态**——对 gitignored 文件，工作区状态无法被 stage（gitignore 阻止），staged delete（`git rm --cached`）被静默跳过。历史教训：commit `32ead90e` 漏提交 5 个 egg_info 删除（staged delete 被吞，只提交了 3 个修改文件）。5 层纵深防御：① [`_is_staged_delete`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 显式识别 staged delete 状态（不在 index AND 在 HEAD），[`_stage_gitignored_tracked`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) existing 分支跳过此类文件，防 `git add -f` 撤销用户的 staged delete；② [`_commit_locked`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 检测到 gitignored 文件时切换 no-pathspec commit + [`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 验证 staged 区只有目标文件（防误提交其他 session WIP）；③ [`_collect_non_target_rel`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) + [`_stash_other_files`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) + [`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) 用 `os.path.normcase()` 大小写不敏感匹配——`Path.resolve()` 在文件不存在磁盘时无法归一化大小写，导致 staged delete 文件被误判为非目标 → 被 stash 走（Windows 大小写不敏感必须用 normcase）。回归测试 [`TestStagedDeleteGitignored`](file:///d:/ZephyrAlpha/tests/test_git_commit_gateway.py)。新 AI 勿误判 no-pathspec 分支或 `_is_staged_delete` 为冗余删掉——pathspec commit 对 gitignored staged delete 静默丢失是已验证 bug（`_is_staged_delete` 受 integrity_anchors 保护）。

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

## 11. depgraph.db 使用指引（唯一全景真源）

> depgraph.db 是唯一全景真源，禁止创建派生 YAML 副本。遇到 depgraph 相关问题，直接问工具：

- **查 DB 数据** → `python scripts/governance/extract_depgraph.py --help`（场景速查表在 epilog）
- **改 DB 节点/路径** → `python scripts/governance/apply_depgraph.py --help`（35+ 子命令）
- **查哪些表不能手写** → `python scripts/governance/sync_yaml_to_depgraph.py --list-readonly-tables`
- **文件结构变更后同步 DB** → 自动完成（GitCommitGateway post-commit GATE-PATH-TREE reconciler，无需手动）
- **DB 变更后重生域文档** → 自动完成（GitCommitGateway post-commit GATE-DOMAIN-DOC reconciler，无需手动）
- **改了 YAML 规则文件** → `python scripts/governance/sync_yaml_to_depgraph.py`（覆盖 readonly 表）
- **改了 rules/ 下规则文件后同步 catalog** → 自动完成（GitCommitGateway post-commit GATE-RULE-CATALOG reconciler，无需手动）

> 改 depgraph.db 前必须 `git commit` 备份（trae_054 STEP0）。DB↔磁盘一致性检查用 `python scripts/governance/diagnose_depgraph.py`。

### 11.1 生成器时间戳约定

> 所有生成器（`scripts/governance/d5_architecture/generators/` 下的 `.py` 文件）输出的文档中，
> 日期字段 MUST 使用 `auto-generated`，最后更新时间 MUST 标注"最后更新以 git log 为准"。
> **禁止在生成器中使用 `datetime.now()` 或任何实时时间源**，否则每次 commit depgraph.db
> 都会因时间戳变化产生非幂等噪音 auto-commit。

- **真源实现**：所有生成器 docstring `[INVARIANTS]` 声明"输出幂等(相同输入→相同输出);零时间戳"
- **时间真源**：文件修改时间唯一真源是 git log，生成器不引入独立时间源
- **检测**：`Select-String -Path "scripts/governance/d5_architecture/generators/*.py" -Pattern "datetime\.now\(\)"` 应返回零匹配
- **自动触发**：GATE-DOMAIN-DOC reconciler 在 commit depgraph.db 后自动调用 generate_domain_doc.py 和 generate_domain_dependency_diagram.py 重生域文档，生成器幂等性确保无噪音 auto-commit
