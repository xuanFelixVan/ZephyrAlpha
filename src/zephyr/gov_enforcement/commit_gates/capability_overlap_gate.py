# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.capability_overlap_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec), zephyr.governance.capability_lookup (REGISTRY_YAML), zephyr.clone_guard.orchestrator (CloneGuardOrchestrator)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Phase A 升级——extract 级克隆硬阻断(passed=False), review 级警告, CloneGuard 降级时 warn-only 兜底(passed=True); tests/ 豁免; token overlap 检查保留 warn-only(原有行为); CloneGuard 检查所有 staged .py 文件(AM filter); git diff 失败 fail-loud; token 匹配 ≥4 字符才告警
# [MODIFY-GUARD] gate_id="CAPABILITY-OVERLAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——CloneGuard/YAML/git diff 异常降级为 fail-loud warn(passed=True 不阻断, logger.warning 告警检测器失效防静默漂移); extract 级克隆发现时 passed=False 硬阻断; CloneGuard 降级时 passed=True warn-only 兜底
# [TESTS] tests/governance/commit_gates/test_capability_overlap_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
capability_overlap_gate.py — 新建 .py 文件 CapabilityLookup 提示门禁 + CloneGuard 语义克隆检测

Phase A 升级（2026-08-06, #ARCH-FORCE-MERGE-DEDUP-001）：
  在原有 token overlap warn-only 检查基础上，接入 CloneGuard（Echo-Guard）语义克隆检测。
  extract 级克隆（3+副本）硬阻断——"必须合并"；review 级（2副本）警告——"尽量精简"。
  CloneGuard 不可用时降级为 warn-only（passed=True），logger.warning 告警检测器失效。

病根（缺口4：CapabilityLookup 被动反查 + AI 重复造轮子）
------------------------------------------------------
AGENTS.md §7 已把"查 CapabilityLookup 确认能力是否已存在"列为 step 0，但仅靠文档约定——
新 AI 若跳过 AGENTS.md 或未读 §7，可在 commit 时直接新建 .py 脚本导致重复造轮子。
Phase A 前：token overlap 检查仅 warn-only（文件名启发式，不阻断）。
Phase A 后：+ CloneGuard 语义检测（AST哈希+CodeSAGE嵌入），extract 级硬阻断。

降级策略（守 blueprint §5.2）
----------------------------
  - CloneGuard 不可用（CLI 未装/索引缺失） → warn-only 兜底（passed=True）
  - CloneGuard 超时 → warn-only 兜底
  - CloneGuard 正常 → extract 级硬阻断, review 级警告

Usage::

    from zephyr.gov_enforcement.commit_gates.capability_overlap_gate import make_capability_overlap_gate

    registry.register(make_capability_overlap_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: capability_overlap_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_capability_overlap_gate
#   name_en: make_capability_overlap_gate
#   intro: 构造新建 .py 文件 CapabilityLookup 提示门禁 GateSpec（warn-only）。
#   desc: 构造新建 .py 文件 CapabilityLookup 提示门禁 GateSpec（warn-only）。 Returns: GateSpec(gate_id="CAPABIL…；源码 L301-L358
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_capability_overlap_gate"]

_REGISTRY_PREFIX = "docs/01_policies_and_standards/_registry/"


# #ARCH-CAPABILITY-OVERLAP-001 治本（2026-07-22）：
# 高频共性 stop-word 集合——这些 token 在 commit_gates/ 目录下所有 *_gate.py 文件名
# 中必然出现（如 gate），或在其他命名约定中高频出现（如 test/init）。保留这些 token
# 作为 overlap 信号无诊断价值（任何 *_gate.py 都会与所有已注册 gate capability 产生
# 'gate' token 交集 = 确定性误报）。原阈值 len>=4 使 gate（4 字符）通过过滤。
# 方案 B（stop-word）比方案 A（阈值>=5）更精准——不会误过滤 data/core/base 等
# 有诊断价值的 4 字符 token。
_STOP_WORDS: frozenset[str] = frozenset(
    {
        "gate",  # 77 个 *_gate.py 文件的共性后缀
        "test",  # 测试文件共性前缀
        "init",  # __init__.py 的共性 token
    }
)


def _tokenize(name: str) -> set[str]:
    """文件名/alias 分词：按 ``_`` / ``-`` / ``.`` 拆分，过滤 <4 字符的 token + stop-word。

    #ARCH-CAPABILITY-OVERLAP-001 治本（2026-07-22）：新增 _STOP_WORDS 过滤，
    排除 gate/test/init 等高频共性短 token，避免 *_gate.py 文件必然与已注册
    gate capability 产生 'gate' token 交集的确定性误报。
    """
    parts = re.split(r"[_\-\.]", name.lower())
    return {p for p in parts if len(p) >= 4 and p not in _STOP_WORDS}


# === 裁定#217 Tier2 P1 Extract Method 重构（2026-07-15）===
# 原 _check 136 行 McCabe=31（6 段 pipeline：staged→filter→load YAML→build index→
# check py overlap→check yaml overlap）。治本：提取为 6 个模块级 helper（均 McCabe≤15），
# _check 简化为 ~25 行 pipeline（McCabe≈7）。行为等价契约：warn-only（永远 passed=True），
# fail-loud 语义不变，token 匹配规则不变。


def _get_staged_new_files(gateway) -> list[str] | None:
    """获取 staged 新增(A) 文件列表。None=fail-loud（warn-only 契约仍 return True）。"""
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        if diff_result.returncode != 0:
            logger.warning(
                "CAPABILITY-OVERLAP gate fail-loud: git diff 失败(rc=%d)，检测器失效，无法检测 capability 重叠。",
                diff_result.returncode,
            )
            return None
        return diff_result.stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.error(
            "CAPABILITY-OVERLAP gate fail-loud: git diff 异常(%s: %s)，检测器失效，无法检测 capability 重叠。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _filter_new_files(staged_new: list[str]) -> tuple[list[str], list[str]]:
    """从 staged 新增文件中筛选 (.py 文件, _registry/ .yaml/.yml 文件)。"""
    py_files = [f.replace("\\", "/") for f in staged_new if f.endswith(".py") and not is_test_exempt(f)]
    yaml_files = [
        f.replace("\\", "/")
        for f in staged_new
        if f.replace("\\", "/").endswith((".yaml", ".yml")) and f.replace("\\", "/").startswith(_REGISTRY_PREFIX)
    ]
    return py_files, yaml_files


def _load_registry_data() -> dict | None:
    """加载 capability registry YAML。None=fail-loud（warn-only 契约仍 return True）。"""
    from zephyr.governance.capability_lookup import REGISTRY_YAML

    if not REGISTRY_YAML.exists():
        logger.warning(
            "CAPABILITY-OVERLAP gate fail-loud: registry 缺失(%s)，检测器失效，"
            "无法检测 capability 重叠。修复：git checkout HEAD -- %s",
            REGISTRY_YAML,
            REGISTRY_YAML,
        )
        return None
    try:
        import yaml

        data = yaml.safe_load(REGISTRY_YAML.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "CAPABILITY-OVERLAP gate fail-loud: registry 解析失败(%s: %s)，检测器失效，无法检测 capability 重叠。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None
    if not isinstance(data, dict):
        logger.warning("CAPABILITY-OVERLAP gate fail-loud: registry 顶层非 dict，检测器失效。")
        return None
    return data


def _build_cap_token_index(data: dict) -> dict[str, set[str]]:
    """从 registry data 构建 capability_id -> token set 索引。"""
    cap_tokens: dict[str, set[str]] = {}
    for cap in data.get("capabilities", []) or []:
        if not isinstance(cap, dict):
            continue
        cap_id = cap.get("capability_id", "")
        if not cap_id:
            continue
        tokens = _tokenize(cap_id)
        for alias in cap.get("aliases", []) or []:
            if isinstance(alias, str):
                tokens |= _tokenize(alias)
        if tokens:
            cap_tokens[cap_id] = tokens
    return cap_tokens


def _check_py_overlap(new_py_files: list[str], cap_tokens: dict[str, set[str]]) -> list[str]:
    """检测新建 .py 文件名 token 与 capability token 交集（每文件只报第一个命中）。"""
    warnings: list[str] = []
    for py_file in new_py_files:
        stem = os.path.basename(py_file)[:-3]  # 去 .py 后缀
        file_tokens = _tokenize(stem)
        if not file_tokens:
            continue
        for cap_id, tokens in cap_tokens.items():
            overlap = file_tokens & tokens
            if overlap:
                warnings.append(
                    f"new .py '{py_file}' tokens {sorted(overlap)} "
                    f"overlap with capability '{cap_id}'——"
                    f"扩展该 capability 的 canonical 文件，勿新建（见 AGENTS.md §7 step 0）"
                )
                break  # 每文件只报第一个命中
    return warnings


def _check_yaml_overlap(new_yaml_files: list[str]) -> list[str]:
    """检测新建 _registry/ .yaml 文件名与同目录现有 .yaml token 交集（≥2 token=高置信度第二真源）。"""
    import glob

    warnings: list[str] = []
    for yaml_file in new_yaml_files:
        stem = os.path.basename(yaml_file).rsplit(".", 1)[0]
        file_tokens = _tokenize(stem)
        if not file_tokens:
            continue
        yaml_dir = os.path.dirname(yaml_file)
        for existing in glob.glob(os.path.join(yaml_dir, "*.yaml")) + glob.glob(os.path.join(yaml_dir, "*.yml")):
            existing_rel = existing.replace("\\", "/")
            if existing_rel == yaml_file:
                continue
            existing_stem = os.path.basename(existing).rsplit(".", 1)[0]
            overlap = file_tokens & _tokenize(existing_stem)
            if len(overlap) >= 2:
                warnings.append(
                    f"new .yaml '{yaml_file}' tokens {sorted(overlap)} "
                    f"overlap with existing '{existing_rel}'——"
                    f"可能是第二真源，扩展现有文件勿新建"
                )
                break
    return warnings


# ── Phase A: CloneGuard 语义克隆检测辅助函数（#ARCH-FORCE-MERGE-DEDUP-001）──


def _get_all_staged_py_files(gateway) -> list[str]:
    """获取所有 staged 的 .py 文件（Added + Modified），排除测试文件。

    CloneGuard 检查所有 staged .py 文件（不只是新建的），因为修改文件
    也可能引入重复代码。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "CAPABILITY-OVERLAP gate: git diff AM 失败(rc=%d)，跳过 CloneGuard 检测",
                diff_result.returncode,
            )
            return []
        return [
            f.replace("\\", "/")
            for f in diff_result.stdout.strip().splitlines()
            if f.endswith(".py") and not is_test_exempt(f)
        ]
    except Exception as e:  # noqa: BLE001  门禁不抛异常
        logger.warning(
            "CAPABILITY-OVERLAP gate: git diff AM 异常(%s: %s)，跳过 CloneGuard 检测",
            type(e).__name__,
            e,
        )
        return []


def _run_clone_guard_check(py_files: list[str]):
    """运行 CloneGuard 语义克隆检测。

    Returns:
        CheckResult | None: None=CloneGuard 不可用（降级 warn-only），
        CheckResult=检测结果。
    """
    try:
        from zephyr.clone_guard.orchestrator import CloneGuardOrchestrator

        orch = CloneGuardOrchestrator(Path.cwd())
        return orch.check(py_files)
    except Exception as e:  # noqa: BLE001  门禁不抛异常
        logger.warning(
            "CAPABILITY-OVERLAP gate: CloneGuard 不可用(%s: %s)，降级 warn-only",
            type(e).__name__,
            e,
        )
        return None


def make_capability_overlap_gate() -> GateSpec:
    """构造新建 .py 文件 CapabilityLookup 提示门禁 GateSpec（warn-only）。

    Returns:
        GateSpec(gate_id="CAPABILITY-OVERLAP", priority=200)。
        priority=200——在 HELD-OVERLAP(50) 之后、其他阻断 gate 之前执行
        （warn-only 不阻断，早执行晚执行无差异，但早执行可早 log）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # ── 阶段1: token overlap 检查（warn-only，保留原有行为）──
        # 文件名 token 与 capability registry 的启发式匹配，仅警告不阻断
        staged_new = _get_staged_new_files(gateway)
        if staged_new is not None:
            new_py_files, new_yaml_files = _filter_new_files(staged_new)
            if new_py_files or new_yaml_files:
                data = _load_registry_data()
                if data is not None:
                    cap_tokens = _build_cap_token_index(data)
                    if cap_tokens:
                        token_warnings: list[str] = []
                        token_warnings.extend(_check_py_overlap(new_py_files, cap_tokens))
                        token_warnings.extend(_check_yaml_overlap(new_yaml_files))
                        if token_warnings:
                            logger.warning(
                                "CAPABILITY-OVERLAP gate warn-only: %s",
                                " | ".join(token_warnings),
                            )

        # ── 阶段2: CloneGuard 语义克隆检测（Phase A——extract 级硬阻断）──
        # 检查所有 staged .py 文件（AM filter）是否与索引中的已有函数语义重复
        all_staged_py = _get_all_staged_py_files(gateway)
        if not all_staged_py:
            return True, ""  # 无 .py 文件需检测

        cg_result = _run_clone_guard_check(all_staged_py)
        if cg_result is None:
            return True, ""  # CloneGuard 不可用，降级 warn-only 兜底

        if not cg_result.passed:
            # extract 级克隆发现——硬阻断（"必须合并"）
            reasons = []
            for f in cg_result.findings:
                reasons.append(
                    f"  - {f.source_file}:{f.source_function} 与 "
                    f"{f.existing_file}:{f.existing_lineno} 的 {f.existing_function} "
                    f"相似度 {f.similarity:.0%}（{f.severity} 级, {f.clone_type}）"
                )
            reason = (
                "CloneGuard 检测到 extract 级代码克隆——必须合并而非新建:\n"
                + "\n".join(reasons)
                + "\n修复: 扩展现有函数而非新建，或使用 import_suggestion"
            )
            return False, reason

        return True, ""

    return GateSpec(gate_id="CAPABILITY-OVERLAP", check=_check, priority=200)
