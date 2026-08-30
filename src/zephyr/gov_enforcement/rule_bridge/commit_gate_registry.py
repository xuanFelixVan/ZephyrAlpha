# [BLUEPRINT] MOD-GOV_COMMIT_GATE_REGISTRY | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §commit-gate-registry
# [MODULE] zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] (none — pure stdlib)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway; zephyr.governance.audit.reconciliation_registry.make_in_process_gate_registry_drift_reconciler (调用 list_gate_ids 进行 YAML↔内存双向校验, #ARCH-GATE-REGISTRY-AUTO-001 Phase 6)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] CommitGateRegistry.register 幂等（同 gate_id 覆盖旧 spec）；同 priority 不同 gate_id 抛 GateRegistrationError 阻断（#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 2 fail-closed 治本）；check_all 按 priority 升序执行所有 gate；单个 gate 异常降级为 fail-closed（passed=False，安全优先），不阻断后续 gate 执行
# [MODIFY-GUARD] GateSpec 字段结构；GateResult 语义；TEST_EXEMPT_PREFIXES / is_test_exempt（tests/ 豁免真源）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_all 永不抛异常——单个 gate 异常降级为 GateResult(passed=False)
# [TESTS] tests/governance/rule_bridge/test_commit_gate_registry.py
# [A_module] module_id=MOD-GOV_COMMIT_GATE_REGISTRY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
commit_gate_registry.py — GitCommitGateway pre-commit 门禁注册表（架构债务 #AD-001 治本）

把 ``commit()`` 方法体中硬编码的 ``_check_*`` 调用升级为声明式 registry：
每个 pre-commit gate 注册一个 ``GateSpec``，commit 前由 registry 统一调度。

设计理由（架构债务 #AD-001 治本）
--------------------------------
``git_commit_gateway.py`` 职责过重（2500+ 行，11 个硬编码 ``_check_*`` 门禁 +
reconciler 注册 + commit 编排 + stash 隔离），多 session 频繁修改同一文件是
搭便车事故的根因之一（模式6 与 GATE-ARCH-MODEL 同文件冲突）。注册制后新增
门禁只需 ``register(spec)``，不改 ``commit()`` 方法体，消除冲突源。

设计参考 ReconciliationRegistry（post-commit reconciler 注册表），纯 stdlib
解耦，便于 mutation testing 用 ``importlib.util.spec_from_file_location``
直接加载。

命名区隔（防混淆）
------------------
本模块的 ``GateSpec`` / ``CommitGateRegistry`` 管 **commit-gateway pre-commit
门禁检查**，与 ``ReconciliationRegistry``（post-commit 漂移对账）是**完全不同的
关注点**（pre-commit 阻断 vs post-commit 对账），勿混淆。

Usage::

    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
        GateResult, GateSpec, CommitGateRegistry,
    )

    registry = CommitGateRegistry()
    registry.register(GateSpec(
        gate_id="HELD-OVERLAP",
        check=lambda gw, files, **kw: gw._check_held_overlap(
            kw["session_id"], files, kw.get("allow_overlap", False)
        ),
        priority=50,
    ))
    results = registry.check_all(gateway, files, session_id="sess-001", allow_overlap=False)
    # results == [GateResult(gate_id="HELD-OVERLAP", passed=True, detail="")]

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: file_path 参数
#   fields: 参数 file_path，类型注解 str
#   code: commit_gate_registry.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: script_path 参数
#   fields: 参数 script_path，类型注解 str | Path
#   code: commit_gate_registry.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: args 参数
#   fields: 参数 args，类型注解 list[str]
#   code: commit_gate_registry.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: cwd 参数
#   fields: 参数 cwd（无注解）
#   code: commit_gate_registry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① is_test_exempt
#   name_en: is_test_exempt
#   intro: 判断文件是否在 tests/ 豁免区（路径段匹配，覆盖嵌套测试目录如 scripts/tests/）。
#   desc: 判断文件是否在 tests/ 豁免区（路径段匹配，覆盖嵌套测试目录如 scripts/tests/）。 治本2：封装归一化+比对逻辑，消除两 gate 实现不一致（create_…；源码 L198-L219
#   inputs: file_path
#   outputs: bool
# - id: A2
#   name_zh: ② run_checker_script
#   name_en: run_checker_script
#   intro: 运行 checker 脚本的共享 helper（5.176.4 治本：消除各 gate 的 subprocess 样板…
#   desc: 运行 checker 脚本的共享 helper（5.176.4 治本：消除各 gate 的 subprocess 样板重复）。 封装 ``[sys.executable, scr…；源码 L222-L277
#   inputs: script_path args cwd timeout text env
#   outputs: subprocess.CompletedProcess
# - id: A3
#   name_zh: ③ CommitGateRegistry
#   name_en: CommitGateRegistry
#   intro: pre-commit 门禁注册表（声明式，参考 ReconciliationRegistry）。
#   desc: pre-commit 门禁注册表（声明式，参考 ReconciliationRegistry）。 register 幂等（同 gate_id 覆盖旧 spec）。 check_a…；公共方法（定义序）: specs,…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A3 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway; zephyr.…
# - id: O2
#   name_zh: subprocess.CompletedProcess
#   name_en: subprocess.CompletedProcess
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway; zephyr.…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Final

logger = logging.getLogger(__name__)


def _audit_allow_overlap_usage(gateway: object, files: list[str], kwargs: dict) -> None:
    """落审计：allow_overlap=True 逃生通道的真实使用（GATE-COMMIT-GW-ABUSE-MONITOR 维度3 真源）。

    治本（2026-07-20，sess-23300-20260720092540）：滥用监控原以 post_commit_guard
    warn_only(gw_env=1) 事件反推 allow_overlap 滥用，实际混入 merge 后 reconciler
    auto-commit 的注册表生命周期伪影（1829/7d 持续误报）。改为在 gate 统一入口直接
    落审计——只有真实传入 allow_overlap=True 的 commit 才计数。
    fail-open：审计写入失败不阻断 commit（check_all ERROR_CONTRACT：永不抛异常）。
    """
    if not kwargs.get("allow_overlap"):
        return
    try:
        root = Path(getattr(gateway, "project_root", "."))
        audit_dir = root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": int(time.time()),  # noqa: m46-time — 审计事件时间戳（allow_overlap 逃生通道使用记录），合法场景
            "session_id": kwargs.get("session_id", "?"),
            "files_count": len(files),
        }
        with (audit_dir / "allow_overlap_usage.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计写入失败不阻断 commit
        logger.debug("allow_overlap usage audit write failed (non-blocking)", exc_info=True)


__all__ = [
    "GateResult",
    "GateSpec",
    "CommitGateRegistry",
    "GateRegistrationError",
    "TEST_EXEMPT_PREFIXES",
    "is_test_exempt",
    "run_checker_script",
]


# ---------------------------------------------------------------------------
# tests/ 豁免真源（治本2，2026-06-30；治本4，2026-07-31）
# ---------------------------------------------------------------------------
# 病根：tests/ 豁免前缀在 create_guard.py / capability_overlap_gate.py 两处硬编码，
# 且实现不一致（create_guard L99 先归一再比对；capability_overlap_gate L87 直接 startswith，
# 未归一化——Windows 反斜杠路径会漏豁免，latent bug）。
#
# 治本（向内收·真源唯一）：提取到本模块（gate 基础设施真源），两 gate import 复用。
# 放此处而非 capability_lookup.py：tests/ 豁免是 gate 行为配置（哪些文件跳过 token 检查），
# 非能力索引关注点——关注点分离。
#
# 治本4（#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase A4，2026-07-31）：
# consumers_accuracy_gate.py:573 baseline-scan 硬编码 `"/tests/" in py_file or
# py_file.startswith("tests/")` 检查嵌套 tests/ 目录（如 scripts/tests/），但
# 原 is_test_exempt 仅 startswith 匹配顶级 tests/。将匹配语义从"前缀"升级为
# "路径段"——任意层级的 tests/ 目录均豁免（scripts/tests/、tests/ 等）。这是更
# 正确的"测试文件豁免"语义：测试文件无论位于何处都应豁免生产检查。50+ 调用方
# 语义更宽松（多豁免嵌套测试文件），符合测试豁免意图。
#
# 安全约束：本常量是高价值篡改目标（加 "src/" 可豁免所有源码绕过 create_guard），
# 已纳入 validate_rules_integrity.py RULES_MANIFEST C 层 golden hash 保护。
# 值保持 ("tests/",) 不变（golden hash 稳定）；匹配逻辑从 startswith 改为段匹配，
# 段名取 prefix.rstrip("/") 消除尾部斜杠。
TEST_EXEMPT_PREFIXES: Final[tuple[str, ...]] = ("tests/",)


def is_test_exempt(file_path: str) -> bool:
    """判断文件是否在 tests/ 豁免区（路径段匹配，覆盖嵌套测试目录如 scripts/tests/）。

    治本2：封装归一化+比对逻辑，消除两 gate 实现不一致（create_guard 归一化、
    capability_overlap_gate 未归一化）。调用方不再自行实现 startswith 判断。

    治本4（#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase A4，2026-07-31）：
    从 startswith 升级为路径段匹配——不仅匹配顶级 tests/，还匹配任意层级的
    tests/ 目录（如 scripts/tests/）。consumers_accuracy_gate.py:573 的硬编码
    `"/tests/" in path` 检查由本函数统一承担，消除调用方自行实现 contains 判断。

    Args:
        file_path: 文件相对路径（可能含正斜杠或反斜杠）。

    Returns:
        True 表示文件在 tests/ 豁免区（不需要 creation_token / 不检测 capability 重叠）。
        匹配任意路径段名为 tests 的目录（tests/foo.py、scripts/tests/foo.py 均命中）。
    """
    normalized = file_path.replace("\\", "/")
    segments = normalized.split("/")
    test_segments = {prefix.rstrip("/") for prefix in TEST_EXEMPT_PREFIXES}
    return any(seg in test_segments for seg in segments)


def run_checker_script(
    script_path: str | Path,
    args: list[str],
    *,
    cwd: str | Path,
    timeout: int = 60,
    text: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """运行 checker 脚本的共享 helper（5.176.4 治本：消除各 gate 的 subprocess 样板重复）。

    封装 ``[sys.executable, script_path, *args]`` + ``capture_output=True`` +
    ``cwd`` + ``timeout`` 样板；``text=True``（默认）时附加
    ``encoding="utf-8", errors="replace"``（各 text 模式 gate 的既有约定）。

    责任边界：本函数只负责执行并返回 ``CompletedProcess``——**returncode 解析
    （exit 0/1/2 语义）与 ``subprocess.TimeoutExpired``/``OSError`` 处理由各 gate
    按自身 fail-open/fail-closed 策略负责**（helper 不吞异常、不判结果）。

    Args:
        script_path: checker 脚本路径（str 或 Path）。
        args: 传给脚本的参数列表（不含解释器与脚本路径）。
        cwd: 子进程工作目录（gate 传入 project_root 或 worktree root）。
        timeout: 超时秒数（各 gate 保持既有值）。
        text: True=文本模式（stdout/stderr 为 str）；False=字节模式
            （stdout/stderr 为 bytes，由 gate 自行 decode）。
        env: 自定义环境变量（如 directory_contract_gate 注入 PYTHONPATH）；
            None=继承父进程环境。

    Returns:
        subprocess.CompletedProcess（returncode/stdout/stderr 由调用方解析）。

    Raises:
        subprocess.TimeoutExpired: 超时（各 gate 按自身策略捕获）。
        OSError: 子进程启动失败（各 gate 按自身策略捕获）。
    """
    kwargs: dict[str, Any] = {
        "capture_output": True,
        "cwd": str(cwd),
        "timeout": timeout,
    }
    if text:
        kwargs.update({"text": True, "encoding": "utf-8", "errors": "replace"})
    else:
        # 显式设 text=False，防止 run_subprocess_hidden 的 setdefault("text", True)
        # 覆盖调用方的字节模式意图（导致 ttl_gate.py result.stderr.decode() 崩溃）
        kwargs["text"] = False
    if env is not None:
        kwargs["env"] = env
    # TRAE-067 铁律2 落地（2026-07-20 Phase 1.5）：commit gate spawn python checker
    # MUST 用 CREATE_NO_WINDOW，消除 commit 流程闪窗（之前每次 commit 跑 10+ 个
    # checker 都闪窗）。run_subprocess_hidden 默认注入 CREATE_NO_WINDOW |
    # CREATE_NEW_PROCESS_GROUP，且 errors='replace' 与本函数语义一致。
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    return run_subprocess_hidden([sys.executable, str(script_path), *args], **kwargs)


@dataclass
class GateResult:
    """pre-commit 门禁检查结果。

    passed=True 时通过，passed=False 时阻断（detail 含违规信息）。
    """

    gate_id: str
    passed: bool
    detail: str = ""


class GateRegistrationError(RuntimeError):
    """门禁注册异常——priority 冲突时抛出（fail-closed 治本）。

    治本（#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 2，2026-07-21）：
    100% AI 开发场景下，原 warn-only 不构成闭环（AI 把 warn 当"通过"，
    与 #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 同一病根）。升级为 fail-closed
    阻断注册——新 AI 添加 priority 撞号的 gate 时立即抛异常，强制分配唯一 priority。

    历史 warn-only 期间已存在的撞号（priority=77 BLUEPRINT-FORMAT vs
    RULING-COMMIT-VERIFIED）已在 Phase 1 消除（RULING-COMMIT-VERIFIED 迁移至 109），
    Phase 2 block 不会卡死现有系统。
    """

    error_code = "ZA-GV-0050"


@dataclass
class GateSpec:
    """单个 pre-commit 门禁声明。

    Attributes:
        gate_id: 门禁标识（如 "HELD-OVERLAP"）。
        check: 执行检查，返回 ``(passed, detail)``。
            签名 ``(gateway, files: list[str], **kwargs) -> tuple[bool, str]``。
            gate 是闭包，注册时捕获所需上下文。
        priority: 执行优先级（升序，数字小先执行）；同 priority 按 register 顺序。
    """

    gate_id: str
    check: Callable[..., tuple[bool, str]]
    priority: int = 100


class CommitGateRegistry:
    """pre-commit 门禁注册表（声明式，参考 ReconciliationRegistry）。

    register 幂等（同 gate_id 覆盖旧 spec）。
    check_all 按 priority 升序执行所有 gate，单个 gate 异常降级为 fail-closed
    （passed=False，安全优先），不阻断后续 gate 执行。
    """

    def __init__(self) -> None:
        self._specs: dict[str, GateSpec] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def specs(self) -> dict[str, GateSpec]:
        """只读：specs（Stage 4 公共化）。"""
        return self._specs

    @specs.setter
    def specs(self, value):
        """写入：specs（Stage 4 公共化）。"""
        self._specs = value

    def register(self, spec: GateSpec) -> None:
        """注册门禁（幂等，同 gate_id 覆盖；同 priority 不同 gate_id 阻断）。

        治本（#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 2，2026-07-21）：
        100% AI 开发场景下，原 warn-only 不构成闭环（AI 把 warn 当"通过"，
        与 #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 同一病根）。升级为 fail-closed
        阻断注册——同 priority 不同 gate_id 抛 GateRegistrationError。

        历史先例（后到者让位）：DATA-TASK 78->41 / RENAME-DEPGRAPH-SYNC 36->39 /
        ORPHAN-MODULE 86->89 / DOC-REF-BROKEN 88->91 / RULING-COMMIT-VERIFIED 77->109
        """
        for existing_id, existing_spec in self._specs.items():
            if existing_spec.priority == spec.priority and existing_id != spec.gate_id:
                raise GateRegistrationError(
                    f"priority={spec.priority} 冲突——gate '{spec.gate_id}' 与已注册的 "
                    f"'{existing_id}' 同 priority. 执行顺序依赖注册顺序（非显式），"
                    f"违反'显式优于隐式'原则. 请分配唯一 priority. "
                    f"历史先例（后到者让位）：DATA-TASK 78->41 / "
                    f"RENAME-DEPGRAPH-SYNC 36->39 / ORPHAN-MODULE 86->89 / "
                    f"DOC-REF-BROKEN 88->91 / RULING-COMMIT-VERIFIED 77->109"
                )
        self._specs[spec.gate_id] = spec

    def check_all(
        self,
        gateway: object,
        files: list[str],
        skip_gates: frozenset[str] = frozenset(),
        **kwargs: Any,
    ) -> list[GateResult]:
        """按 priority 升序执行所有 gate，返回结果列表。

        单个 gate 异常降级为 fail-closed（passed=False，安全优先），
        不阻断后续 gate 执行。

        skip_gates: 命中的 gate_id 跳过执行（结果中保留 skipped 记录供审计）。
        唯一消费场景=worktree 物理隔离 commit（跳过集合单一真源=
        session_worktree._WORKTREE_SKIP_GATES，tracker #92 治本——物理隔离下
        搭便车三 gate 无检测对象，对齐 merge 预演既有跳过口径）。
        """
        _audit_allow_overlap_usage(gateway, files, kwargs)
        results: list[GateResult] = []
        for spec in sorted(self._specs.values(), key=lambda s: s.priority):
            if spec.gate_id in skip_gates:
                results.append(
                    GateResult(
                        gate_id=spec.gate_id,
                        passed=True,
                        detail="skipped: worktree 物理隔离（无检测对象）",
                    )
                )
                continue
            try:
                passed, detail = spec.check(gateway, files, **kwargs)
                results.append(GateResult(gate_id=spec.gate_id, passed=passed, detail=detail))
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("CommitGateRegistry: gate %s 异常降级为 fail-closed: %s", spec.gate_id, e, exc_info=True)
                results.append(
                    GateResult(
                        gate_id=spec.gate_id,
                        passed=False,
                        detail=f"gate 异常（fail-closed）: {e}",
                    )
                )
        return results

    def get(self, gate_id: str) -> GateSpec | None:
        """按 gate_id 获取已注册的 GateSpec（_commit_auto 复用 DCR gate 用）。

        Returns:
            GateSpec 或 None（gate_id 未注册时）。
        """
        return self._specs.get(gate_id)

    def list_all(self) -> list[GateSpec]:
        """返回所有已注册的 GateSpec（按 priority 升序）。

        #ARCH-GATE-REGISTRY-AUTO-001 Phase 6——用于 YAML ↔ 内存注册表双向校验。
        """
        return sorted(self._specs.values(), key=lambda s: s.priority)

    def list_gate_ids(self) -> list[str]:
        """返回所有已注册的 gate_id 列表（按 priority 升序）。

        #ARCH-GATE-REGISTRY-AUTO-001 Phase 6——用于 YAML ↔ 内存注册表双向校验。
        """
        return [s.gate_id for s in self.list_all()]
