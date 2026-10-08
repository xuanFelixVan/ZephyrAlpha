---
ttl: task_bound
completes_when: 全流通战役交付后归档
---

# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] docs._working.fullcirculation_campaign_20261008.01_dtable_rulings.tech_stack_absorption_spec
# [DOMAIN] D_INFRA_RUNTIME
# [A_module] module_id=DOC-FULLCIRC-DTABLE-TECHSTACK-ABSORB | layer=document | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# [GATE-SELFDOC:CREATE-GUARD]
ttl: task_bound
completes_when: chief 判读本细案并裁决后转施工批（或归档否决）
ruling_ref: "裁定#485：tech_stack 组件自检值得吸收进 boot_hooks（疑似真缺口：开机无系统性组件可用性检查）"
evidence_ref: docs/_working/map_census/gomap/capacity_eval_evidence.yaml（DD 表 16 行，CAPACITY-EVAL-EVIDENCE-001）
session: 2026-10-08 架构施工设计代理（只调研+写本文档，零代码改动）

---

# tech_stack 吸收进 boot_hooks 细案

## 0. 执行摘要

- **真缺口成立**：`TechStackValidator`（src/zephyr/infrastructure/capacity_assurance/tech_stack.py，292 行/21 方法）全仓零消费（`validate_on_startup` 无任何调用点，tests 亦无引用）——开机确实没有系统性组件可用性自检。
- **但 16 项中只有 6 项有实质检查**（全是 import/版本级），其余 10 项 `generic_check` 只回显终选字符串、`available` 恒 True——它们是清单回显，不是检查。
- **排雷点（组件已死不该吸收）**：DD-4（AiAuditGuard 全仓零构造=orphan）、DD-8 的 bandit 腿（不在依赖集）、DD-7（cold plane 开发工具误入运行时清单）。
- **宿主裁定**：吸收进 `boot_hooks.py`（在编且被 `AutoRuntimeCore.boot()` 接线）。**注意 `startup_shutdown.py` 的 `StartupOrchestrator` 本身全仓零实例化=孤儿件，不可作吸收宿主**（吸收进它等于接进死物）。
- **manifest 路径缺陷确认并给修正**：validator 默认路径 `src/zephyr/config/capacity/tech_stackmanifest.yaml` 不存在（`src/zephyr/config/` 目录本身不存在），运行时恒走内置漂移副本；事实真源=repo 根 `config/tech_stack_manifest.yaml`（REG-CAP-001，v2.7.0，含 runtime_plane/category 元数据）。
- **分布**：吸收 6 项（3 阻断/3 警告）｜废弃检查项 2 项｜保留在档 9 项（DD-5 拆两腿跨吸收/在档两档）。
- **工时**：约 2 人日（1.5–2.5 区间），改动 5 文件+1 测试文件，零新模块、零新注册表。

## 1. 调研结论 A：tech_stack.py 16 项组件与检查逻辑实测

检查分发机制：`_check_component()` 按 `dd_id` 反射查找 `_check_dd_N` 方法（tech_stack.py:109-114）；**只有 6 个 DD 有专属方法**（DD-1/2/3/5/7/16），其余 10 项落入 `_generic_check`（:116-122）——仅回显 `final_choice` 字符串、恒 `available=True`，无任何校验。

| DD | 组件（终选） | 现有检查体 | 检查类型 | 对照表 status（交叉参照） |
|----|-------------|-----------|---------|------------------------|
| DD-1 | SLO 配置（YAML+Pydantic v2） | `inspect_pydantic_v2`（:124-147） | import + **版本门**（必须 2.x） | wired（191 文件消费） |
| DD-2 | 审计存储（SQLite+hash 链） | `inspect_sqlite`（:149-164） | 内存库连通（`SELECT 1`） | wired（DatabaseManager/IntegrityVerifier） |
| DD-3 | 指标采样（structlog+OTel SDK） | `inspect_otel_sdk`（:166-188） | import + 版本 | wired；**但 otel 未声明于 pyproject**（本次复核确认 grep 零命中，环境已装属传递/手工） |
| DD-4 | AI 审计规则（YAML+Pydantic） | 无（generic 回显） | **无检查** | **orphan**（AiAuditGuard 全仓零构造，本次复核确认） |
| DD-5 | 治理闭环（自研 EMA+阈值） | `inspect_psutil`（:221-235） | import（**检查对象错位**：组件是 EMA 算法，检查的是 psutil 依赖） | wired（psutil 多域消费） |
| DD-6 | 类型校验（mypy+import-linter） | 无 | 无 | wired（双工具配置在编；manifest 标 `runtime_plane: cold`） |
| DD-7 | 单元测试（pytest+pytest-cov） | `inspect_pytest`（:190-204） | import + 版本 | wired（manifest 标 `runtime_plane: cold`） |
| DD-8 | 静态扫描（ruff+bandit） | 无 | 无 | **partial**（ruff 在编；bandit 全仓零命中，本次复核确认不在依赖集） |
| DD-9 | ContractBus 迁移（15+15+14） | 无 | 无 | wired（contract_bus.py 在编；capacity 侧 Loader 包外零消费=orphan 嫌疑） |
| DD-10 | Error Budget（SQLite+Pydantic v2） | 无 | 无 | wired（BudgetEngine 活件） |
| DD-11 | Token Budget（Token Bucket+滑窗） | 无 | 无 | wired（token_budget.py 七处消费） |
| DD-12 | Kill Switch（env+文件信号） | 无 | 无 | wired（**唯一 `runtime_plane: hot`**；security 版+fuse 版双件经 orchestrator 挂接） |
| DD-13 | Sandbox（子进程+资源限制） | 无 | 无 | wired（LSG ProcessSandboxLayer） |
| DD-14 | Graceful Degradation（YAML 降级链+路由） | 无 | 无 | wired（loader/manager 双要素在编） |
| DD-15 | OTel 语义规范（GenAI Conventions） | 无 | 无 | wired（规范以不变量声明落在 span_stub/event_sink——**无可检实体**） |
| DD-16 | 语义缓存（ChromaDB） | `inspect_chromadb`（:206-219） | import + 版本 | wired（pyproject 主依赖:39；**chroma→faiss 迁移件在编=迁移中信号**） |

manifest 附加元数据（分级依据）：`runtime_plane` hot=1（DD-12）/ warm=12 / cold=3（DD-6/7/8）；`category` safety=2（DD-12/13）/ storage=1（DD-2）/ quality=3（cold 三件）/ 其余 governance/observability 等。

## 2. 调研结论 B：启动链结构与插入点

真实接线链（实测，非设计稿）：

```
python -m zephyr.trading
└─ AutoRuntimeCore.boot()                       auto_runtime_core.py:308
   1. _warn_if_runtime_gate_down()              ← LSG 拦截器在岗自证（warn-only 先例，:355-381）
   2. lifecycle.boot_sequence(...)              ← 10 步线性序（config/stop_gate/registry/health/
   │                                               integration_validate fail-fast/watchdog）lifecycle_manager.py:98
   3. _start_local_models（可选 L2）
   4. _init_task_learner / _benchmark_and_learn
   5. ResourceOptimizationEngine.start_monitor  ← 失败=告警+降级标记先例（:333-340）
   6. _bootstrap_rbac
   7. register_task_system_cron_jobs
   8. register_task_system_hooks → register_boot_hooks()   boot_hooks.py:642  ★吸收宿主
      ├─ task hooks / RBAC hooks / 监控模块 / kill switch 编排器 / Rollback / SLA / Notifier /
      │  HealthAggregator / F5 / 14 个 EventBus 消费方 / skill freshness / governance regeneration
      │  （PYTEST_CURRENT_TEST 守卫先例 :371）/ RedBlue / MCP 集群线程
   9. start_task_queue / blueprint_watcher / fle_scheduler / triple_alignment / escalation
```

分层现状：
- **分层存在于两处**：`lifecycle.boot_sequence` 的线性步序列（真实运行）与 `startup_shutdown.py` 的 P1–P6 DAG（secrets_db→context_gate→market_data→factor→oms→dashboard，**纯设计件，`StartupOrchestrator` 全仓零实例化=孤儿**，仅被 `governance/__init__.py:130` 与 `ops_governance/__init__.py:27-29` 作 re-export 映射，无消费者）。
- **最自然插入点**：`register_boot_hooks()` 函数体开头（第 8 步入口处）——依据裁定#485 明示"吸收进 boot_hooks"，且该位置先于全部订阅/重初始化逻辑，依赖面自检先行才使后继初始化的成败可归因。
- **时序说明（不选 boot() 最早点的理由）**：register_boot_hooks 位于 boot() 中段（RBAC 之后），非最早点；但 P0 依赖（pydantic/sqlite）在模块 import 期已被启动链隐式验证（startup_shutdown.py 自身 import pydantic；SQLite 在 boot_sequence 内真实开库），显式版本门的价值是**可诊断性**（错版在随机位置崩 vs 一条明确 RuntimeError），提前几百毫秒检出收益不值改 boot() 编排序的扰动面。

## 3. 逐项吸收/废弃/保留裁定表

判定原则：① 有实质检查语义且组件在编→吸收；② 组件已死/不在册/检查对象错位→废弃该项或拆分；③ cold plane 开发工具→保留在档（生产环境不装 dev 依赖是常态，运行时检查=语义错误）；④ 规范/迁移计划类无可检实体→保留在档；⑤ 依赖已被他项覆盖→保留在档（禁重复检查）。

| DD | 裁定 | 等级 | 依据与备注 |
|----|------|------|-----------|
| DD-1 | **吸收**（boot_hooks 自检函数） | **阻断** | 版本门是真检查（v1/v2 API 不兼容，191 文件基座）；import 失败实际到不了此处（启动链已隐式 import），到=环境诡异仍阻断 |
| DD-2 | **吸收** | **阻断** | 内存库探活=编译进检测，标准库损坏属环境级故障；文件库连通已由 boot_sequence 真实开库覆盖，不重复造 |
| DD-3 | **吸收** | 警告+降级 | 遥测链有 stub 降级设计（tracing.py/span_stub.py 缺席可跑）；**附带行动项：pyproject 补 opentelemetry 声明**（未声明依赖是治理洞，与吸收同批修） |
| DD-4 | **废弃检查项** | — | 组件 orphan（AiAuditGuard 零构造，对照表+本次复核双证）；检查不存在运行时消费的组件=伪检查。组件本体去留是独立议题留 chief，本细案不越权处置 |
| DD-5 | **拆分**：psutil 依赖检查**吸收**；EMA 算法本体**保留在档** | 警告+降级 | 检查对象错位（组件=EMA 算法，检查=psutil）；psutil 是多域活依赖值得自检（挂"共享依赖"组，dd_id 溯源注记）；EMA 无可检依赖 |
| DD-6 | **保留在档** | — | `runtime_plane: cold`；mypy/import-linter 是开发时工具，运行时检查语义错误 |
| DD-7 | **废弃检查项**（归保留在档） | — | cold plane 同 DD-6；生产装 pytest=供应链面扩大；CI 面已由 pyproject `[tool.pytest.ini_options]` 事实覆盖 |
| DD-8 | **保留在档** | — | cold plane；且 bandit 不在依赖集——检查不在册工具只会产出恒假信号。**附带发现：manifest 终选与事实漂移（bandit 未采纳），除名判读留 chief** |
| DD-9 | **保留在档** | — | "分三批 15+15+14"是迁移计划非组件，迁移已完成（ContractBus wired），无可检对象；capacity 侧 Loader orphan 嫌疑留 chief |
| DD-10 | **保留在档** | — | 依赖（SQLite+Pydantic）已被 DD-1/2 覆盖；BudgetEngine 活性已由 `_hook_session_startup_init_budget` 注册即验覆盖 |
| DD-11 | **保留在档** | — | Token Bucket+滑窗是纯算法（token_budget.py 七处消费 wired），无外部依赖可检 |
| DD-12 | **吸收（换检查体，新增设计）** | **阻断** | 唯一 hot plane+宪法 §7 核心系统。generic_check 无检查，吸收时新设计检查体：`get_kill_switch()` 单例可达 + state 通道（env `ZEPHYR_KILL_SWITCH_STATE_PATH`/默认路径）可解析；hot 安全件通道失位=阻断。与后段 `_init_kill_switch_orchestrator`（:604）不重复——自检只做通道存在性早检。**此项超出原 tech_stack.py 能力，标注为新增设计给 chief 复核** |
| DD-13 | **保留在档** | — | LSG ProcessSandbox 活性由网关自身保证；同域在岗自证已有 F88 `_warn_if_runtime_gate_down` 先例覆盖，禁重复检查 |
| DD-14 | **保留在档** | — | config 文件存在性检查价值低（loader 失败自会响亮报错）；EngineDegradationManager 单例活性由 RBAC bootstrap 链覆盖 |
| DD-15 | **保留在档** | — | 命名规范不是可 import 实体，落地=不变量声明，由评审/测试保证 |
| DD-16 | **吸收** | 警告+降级 | pyproject 主依赖+vector_memory 三处 import；import 失败→警告+向量记忆降级（`_start_vms` 本就"失败仅警告"）。**注记：chroma→faiss 迁移件在编，终态判读留 chief——若 faiss 成为终态，本项检查对象应随终态切换或除名** |

**分布统计**：吸收 6 项（DD-1/2/3/5-psutil/12/16；阻断 3=DD-1/2/12，警告 3=DD-3/5/16）｜废弃检查项 2 项（DD-4、DD-7）｜保留在档 9 项（DD-5-EMA/6/8/9/10/11/13/14/15）。DD-5 一项跨两档（拆分处理），按 DD 计 16 项无遗漏。

**排雷点汇总（"组件已死不该吸收"）**：
1. **DD-4**：AiAuditGuard 全仓零构造（orphan）——吸收其"检查"= 永真伪检查，必须剔除。
2. **DD-8 bandit 腿**：不在 pyproject/脚本/pre-commit 任何依赖面——manifest 终选与事实漂移。
3. **DD-7**：组件活着但属 cold plane——活着≠该在运行时检查。
4. **DD-16 半雷**：chromadb 活着但在向 faiss 迁移途中——吸收按警告级，不按阻断级，防迁移终态反转后自检误伤。
5. **宿主雷**：`startup_shutdown.py` 的 StartupOrchestrator 零实例化——严禁把吸收目标写成"接入 P1-P6 DAG"，那是接进孤儿件。

## 4. 设计：自检函数规格（boot_hooks.py 内新增）

### 4.1 函数骨架

```python
_tech_stack_check_done = False   # 幂等标志（对齐 _monitoring_modules_initialized 先例）

def _run_tech_stack_self_check() -> None:
    """技术栈组件可用性自检（裁定#485 吸收自 capacity_assurance/tech_stack.py）。

    分级语义：
      BLOCK  —— DD-1 版本门 / DD-2 sqlite 探活 / DD-12 kill switch 通道：raise RuntimeError。
                这是 boot_hooks "失败仅告警"惯例的显式例外：基座错版/缺失时后续一切
                初始化都在错误地基上跑，静默降级比崩溃更危险（fail-fast）。
      WARN   —— DD-3 otel / DD-5 psutil / DD-16 chromadb：logger.warning +
                MetricsRegistry.observe("tech_stack.degraded", ...)（复用 :145 observe 先例，
                不新注册表不新降级机制）。
    逃生门：ZEPHYR_TECH_STACK_CHECK=0 全关；=warn 时 BLOCK 降为警告（调试用）。
    pytest 隔离：PYTEST_CURRENT_TEST 在岗时只跑轻量项、跳过 chromadb import
    （对齐 _subscribe_governance_regeneration :371 守卫先例；chromadb import 慢且测试环境可能缺）。
    """
```

接线：`register_boot_hooks()` 函数体**第一行**调用 `_run_tech_stack_self_check()`（先于所有订阅/初始化——依赖面自检先行）。

BLOCK 的传播路径（实测核认）：`register_task_system_hooks`（auto_runtime_core.py:1125-1126）**无 try 包裹**，`boot()` 对该调用亦无包裹（:344）→ raise 直接崩 boot → `__main__` 非零退出。这是设计意图；施工批须验证 `python -m zephyr.trading` 入口对 boot 异常的错误呈现可诊断。

### 4.2 manifest 路径缺陷修正

现状三重缺陷：① 默认路径 `src/zephyr/config/capacity/tech_stackmanifest.yaml` 不存在（连 `src/zephyr/config/` 目录都不存在）；② 事实真源是 repo 根 `config/tech_stack_manifest.yaml`（REG-CAP-001 挂 asset_inventory，manifest_version 2.7.0）；③ 运行时因此恒走 `_default_decisions()` 内置清单——且该清单是**漂移副本**（真源已含 interpreter/runtime_plane/category/rationale 元数据，内置副本只有 3 字段）。

修正（吸收时一并治，零新路径机制）：
1. 自检函数直接读真源：`REPO_ROOT / "config" / "tech_stack_manifest.yaml"`（REPO_ROOT 是 boot_hooks.py:34 已在用真源）。
2. manifest 缺失/解析失败 → **警告 + 回退内置最小清单**（只含吸收 6 项所需元数据，不再复制全 16 项），不阻断——manifest 是治理档非运行时必需。
3. 死亡路径代码（三层 dirname 计算 + `_load_manifest` 旧逻辑 + `_default_decisions` 全量副本）随吸收退役删除，不留第二真源。

### 4.3 tech_stack.py 本体终态与内收对账

- 检查逻辑（6 个 inspect 体 + `ComponentStatus`）迁入 boot_hooks.py 后，`tech_stack.py` **退役**（同真源必并——内收铁律 w5_1：内置清单与 manifest 真源可派生→必并）。
- 同批连带：`capacity_assurance/__init__.py:48,69` 移除 tech_stack 出口；`contracts/batch2_governance.py` 的 TechStackValidator 契约段（:73 schema 定义）改为指向 boot_hooks 新函数或随主体退役（施工批裁量，倾向后者——契约描述的校验器形态将不存在）。
- 零新模块、零新注册表、零新配置册——降级可观测走现有 MetricsRegistry，分级元数据走现有 manifest 字段。

## 5. 工作量估算

| # | 文件 | 改动 | 估时 |
|---|------|------|------|
| 1 | `src/zephyr/trading/boot_hooks.py` | 新增 `_run_tech_stack_self_check()`（约 120 行：6 检查+分级+manifest 加载+env 门+pytest 守卫+幂等）+ register_boot_hooks 首行接线 | 0.5 天 |
| 2 | `src/zephyr/infrastructure/capacity_assurance/tech_stack.py` | 退役（删文件；tests 无引用已核，安全） | 0.25 天 |
| 3 | `src/zephyr/infrastructure/capacity_assurance/__init__.py` | 移除 tech_stack 双处出口 | 0.1 天 |
| 4 | `src/zephyr/infrastructure/capacity_assurance/contracts/batch2_governance.py` | TechStackValidator 契约段处置 | 0.25 天 |
| 5 | `pyproject.toml` | 补 opentelemetry-api/sdk 依赖声明（DD-3 附带治理洞） | 0.1 天 |
| 6 | `tests/trading/test_boot_hooks_tech_stack.py`（新建，tests/ 豁免 CREATE-GUARD） | 6 检查各自 pass/fail 分级 + manifest 缺失回退 + env 门 + 幂等 + pytest 守卫（全部 tmp_path/mock，禁写生产路径） | 0.5 天 |
| 7 | 治理面 | 蓝图 MOD-INF-001 §5.1 注记吸收去向；apply_depgraph 登记；`python -m zephyr.trading` 入口 BLOCK 呈现实测 | 0.25 天 |

**合计约 2 人日**（区间 1.5–2.5）。风险注记：boot_hooks.py 增长约 120 行（801→约 920），仍在单文件可接受范围；不拆新模块（内收铁律）。

## 6. 留 chief 判读清单（本细案不越权处置）

1. DD-4 AiAuditGuard orphan 组件本体去留（对照表已标记，独立于本吸收案）。
2. DD-8 bandit 是否从 manifest 终选除名（manifest 与依赖集漂移）。
3. DD-9 capacity 侧 ContractBusLoader orphan 嫌疑。
4. DD-16 chroma→faiss 迁移终态（影响自检检查对象）。
5. `startup_shutdown.py` StartupOrchestrator 孤儿件本身的去留（本细案仅阻止其作吸收宿主；其 P1-P6 分层思想是否值得激活是独立议题）。
6. DD-12 新增检查体（超出原 tech_stack.py 能力的升级设计）是否照准。
