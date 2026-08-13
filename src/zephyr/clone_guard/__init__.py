# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.1
# [MODULE] zephyr.clone_guard
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.orchestrator; zephyr.clone_guard.config; zephyr.clone_guard.engines.echo_guard_adapter; zephyr.clone_guard.mcp_server
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.capability_overlap_gate; config/mcp.json (servers.clone_guard)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] CloneGuard 是代码克隆检测集成防御体系的统一入口；MVP(Phase A)仅调度 Echo-Guard；升级 CAPABILITY-OVERLAP 门禁不新增门禁（守 I-GOV-3）；extract 级硬阻断=必须合并，review 级警告=尽量精简；reconciler 只 warn 不 commit（守 I-GOV-2）；L0 MCP check_before_write 是 advisory 不阻断（源头预防非强制）
# [MODIFY-GUARD] gate_id="CAPABILITY-OVERLAP"；blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] orchestrator.check() 永不抛异常——echo-guard 不可用时 degraded=True + passed=True（fail-loud warn 不阻断，守 warn-only 兜底契约）；mcp_server._check_before_write 永不抛异常——L0 降级放行，L1 兜底
# [TESTS] tests/clone_guard/test_orchestrator.py; tests/clone_guard/test_mcp_server.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

CloneGuard — 多引擎代码克隆检测集成防御体系（Phase A MVP）

治本 100% AI 开发场景下的"重复造轮子"病根。MVP 阶段仅集成 Echo-Guard，
通过升级现有 CAPABILITY-OVERLAP 门禁接入 GitCommitGateway 提交链路。

四层防御纵深（Phase A 仅 L0+L1）：
  L0 源头预防 — MCP check_before_write（Phase A 注册）
  L1 提交拦截 — pre-commit 硬阻断 extract 级克隆（Phase A 实现）
  L2 周期审计 — 全量语义扫描（Phase B）
  L3 跨边界审计 — 跨仓库/跨项目（Phase C）

Usage::

    from zephyr.clone_guard.orchestrator import CloneGuardOrchestrator
    result = CloneGuardOrchestrator(repo_root).check(staged_files)
    if not result.passed:
        print(f"CloneGuard 阻断: {result.findings}")

    # L0 源头预防——AI 写代码前主动查重
    from zephyr.clone_guard.mcp_server import create_server
    server = create_server(repo_root=".")
    # 通过 MCP stdio 协议调用 clone_guard.check_before_write

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 仓库根目录 + staged 待提交文件列表
#   fields: repo_root 仓库根路径 + staged_files git 暂存文件路径列表（L1 提交拦截入参）
#   code: CloneGuardOrchestrator(repo_root).check(staged_files)（docstring Usage L30-33）
# - id: I2
#   name: 待写入候选代码片段
#   fields: AI 写代码前待查重的代码内容（L0 源头预防入参）
#   code: mcp_server.create_server / clone_guard.check_before_write（docstring L35-38）
# 层: 算法
# - id: A1
#   name_zh: ① L1 提交拦截编排入口
#   name_en: CloneGuardOrchestrator.check
#   intro: 统一入口调度克隆检测引擎（Phase A 仅 Echo-Guard），对 staged 文件给出放行/阻断判定
#   desc: __init__ 再导出 orchestrator 的 CheckResult/CloneGuardOrchestrator/Finding（L43）；契约=check() 永不抛异常，echo-guard 不可用时 degraded=True+passed=True 兜底放行；extract 级硬阻断、review 级警告（[INVARIANTS]/[ERROR_CONTRACT]）
#   inputs: I1
#   outputs: CheckResult(passed/findings)
#   invariant: 升级 CAPABILITY-OVERLAP 门禁不新增门禁（守 I-GOV-3）
# - id: A2
#   name_zh: ② L0 源头预防 MCP 服务
#   name_en: CloneGuardMCPServer/create_server
#   intro: AI 写代码前经 MCP stdio 主动查重，advisory 只提醒不阻断
#   desc: __init__ 再导出 mcp_server 的 CloneGuardMCPServer/create_server（L42）；check_before_write 永不抛异常——L0 降级放行、L1 兜底（[ERROR_CONTRACT]）
#   inputs: I2
#   outputs: MCP stdio 查重建议（advisory）
#   invariant: L0 advisory 不阻断（源头预防非强制）
# - id: A3
#   name_zh: ③ 多引擎结果聚合
#   name_en: FindingAggregator
#   intro: 把各检测引擎的 findings 聚成统一结果（Phase A 单引擎 Echo-Guard）
#   desc: __init__ 再导出 aggregator 的 AggregatedFinding/AggregationResult/FindingAggregator（L41）；reconciler 只 warn 不 commit（守 I-GOV-2）
#   inputs: A1
#   outputs: AggregationResult 聚合判定
# 层: 输出
# - id: O1
#   name_zh: 克隆检测门禁判定结果
#   name_en: CheckResult/AggregationResult
#   intro: passed=False 时阻断提交并列出 findings，供 pre-commit 门禁硬阻断 extract 级克隆
#   downstream: zephyr.gov_enforcement.commit_gates.capability_overlap_gate MOD-GATE_ENGINE（[CONSUMERS]）
# - id: O2
#   name_zh: 统一公共 API 面（8 符号）
#   name_en: __all__（orchestrator/aggregator/mcp_server 再导出）
#   intro: 把三类子模块公共符号聚成 zephyr.clone_guard 单一 import 面，含 MCP server 工厂
#   downstream: config/mcp.json servers.clone_guard（[CONSUMERS]）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A3
# A3 --> O1
# I2 --> A2
# A2 --> O2
"""

from zephyr.clone_guard.aggregator import AggregatedFinding, AggregationResult, FindingAggregator
from zephyr.clone_guard.mcp_server import CloneGuardMCPServer, create_server
from zephyr.clone_guard.orchestrator import CheckResult, CloneGuardOrchestrator, Finding

__all__ = [
    "AggregatedFinding",
    "AggregationResult",
    "CheckResult",
    "CloneGuardMCPServer",
    "CloneGuardOrchestrator",
    "Finding",
    "FindingAggregator",
    "create_server",
]
