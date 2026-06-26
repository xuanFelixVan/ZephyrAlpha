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
- 治理决策方法论见 [`trae_024_methodology_diagnosis.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml)（PS-STD-011）——含MTH-006诊断反转验证：深挖后MUST回溯初始诊断，不一致时追问"为什么初始诊断错了？"
- 审计脚本质量见 [`quality_standard.md`](file:///d:/ZephyrAlpha/scripts/governance/quality_standard.md)（SCRIPT-QUALITY-001）
- 产出物规格化见 [`trae_030_doc_numbering_metadata.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)（GOV-DOC-011）——`.md` 文档 frontmatter 标准字段：`module_id, title, version, layer, depends_on, tags, **ttl（GATE-15 强制校验）**`。字段定义和 doc_type 映射见 trae_030；frontmatter 不可删字段完整清单见 [`onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)「绝对不可删的 15 类」
- **所有 `.md` 文档 frontmatter MUST 含 `ttl` 字段**——2 个合法值：`permanent`（永久）/`task_bound`（任务绑定，完成即删）。判定方法：在永久区路径（`docs/01_policies/`、`docs/02_enterprise_architecture/`、`docs/03_modules/`、`docs/08_knowledge/`）→ `permanent`；否则 → `task_bound`（默认落 [`docs/_working/`](file:///d:/ZephyrAlpha/docs/_working/README.md) 临时区）。详见 [`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) 的 `decision_tree`。
- **`docs/_working/` 新增 .md 文件 MUST 在 frontmatter 声明 `completes_when` 字段**（可验证的完成条件），GitCommitGateway commit 时自动拦截缺失该字段的新文档；规则真源见 [_working/README.md §五](file:///d:/ZephyrAlpha/docs/_working/README.md)；自动归档由 [GATE-WORKING-DOCS reconciler](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py) post-commit 事件驱动（capability 反查：`python -m zephyr.governance.capability_lookup --find ghost`）。
- **读取 `docs/_working/` 下任何 .md 前 MUST 验证文档引用的脚本/YAML/blueprint_id 是否仍存在**（防幽灵引用漂移），细则见 [_working/README.md §六](file:///d:/ZephyrAlpha/docs/_working/README.md)。
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
  - **配套门禁**：**GATE-VOCAB** 已接入 [`.pre-commit-config.yaml` L286-303](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L286-L303) 作为 pre-commit 钩子（`id: gate-vocab-hardcode`，`--warn-only` 起步模式，待 trae_060 §5 evidence 违规清零后转 `--ci` 硬阻断），`src/zephyr/**/*.py` 或 `scripts/**/*.py` 变更时自动触发。AST 扫描检测 `VALID/ALLOWED/LEGAL/PERMITTED_*_VALUES/STATUSES/TYPES/LEVELS/LAYERS/TTL/CATEGORIES/CLASSIFICATIONS/LIST/SET` 模式的字面量硬编码（含 `dict()/list()/tuple()/"a,b".split()` 隐式字面量 + walrus 操作符）+ `load_vocabulary_values("xxx.yaml")` 引用文件存在性校验。例外：DDL 文件（`sqlite_schema.py` 等）走 DDL-as-Code 协议；`_archive/` 排除；**`# noqa: gate-vocab`** 内联豁免（带理由的诚实豁免，非偷偷绕过）。门禁真源见 [trae_060 §5 prohibition_list](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml#L189-L213)。
  - **capability 反查注册表**已登记 2 条能力（`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`）：`vocabulary_values_loader`（canonical = `src/zephyr/shared/io/yaml_utils.py`）+ `vocab_hardcode_detector`（canonical = `scripts/governance/d3_metadata/check_vocab_hardcode.py`）。新 AI 创建词表加载器或硬编码检测器前，CapabilityLookup 会反查阻止重复造轮子。

## 8. 永远不要做的事

> 完整禁止清单见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) 四条铁律。此处仅列项目宪法级禁令：

- 不要删除 `data/` 下的任何文件
- 不要跳过 `CapabilityRegistry.register()`
- 不要修改 `AiAuditLogger` 的已有日志
- 不要创建新模块而不注册到大脑

## 9. 新模块接入规则

创建新模块时，必须：
0. **查 CapabilityLookup 确认能力是否已存在**（防止重复造轮子）：
   ```python
   from zephyr.governance.capability_lookup import CapabilityLookup
   reg = CapabilityLookup()              # 自动扫磁盘+派生 canonical
   hits = reg.find("rollback")            # 关键词搜（匹配 capability_id/aliases/description/canonical_file）
   cap = reg.get("rollback_executor")     # 按 capability_id 精确查
   reg.check_file_canonical("src/zephyr/xxx.py")  # 反查某文件是哪个能力的 canonical
   ```
   真源：[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)（能力索引，仅声明 capability_id/aliases/description；canonical_file/duplicates/removed_duplicates 全部由 CapabilityLookup 从磁盘头部+git log 自动派生）。已存在的能力 → 扩展现有 canonical 文件，禁止新建重复实现。
   **aliases 只放英文标识符**（函数名/常量，如 `REPO_ROOT`/`load_blueprint_path`）；中文变体由 `find()` 的 token 包含匹配（CJK ≥3 字符公共子串）自然处理，**禁止在 YAML 堆中文同义词 alias**（反模式，见注册表顶部 alias 策略）。
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

> 改 depgraph.db 前必须 `git commit` 备份（trae_054 STEP0）。DB↔磁盘一致性检查用 `python scripts/governance/diagnose_depgraph.py`。
