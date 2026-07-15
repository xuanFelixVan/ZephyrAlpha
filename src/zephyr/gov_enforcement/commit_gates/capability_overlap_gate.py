# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.capability_overlap_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec), zephyr.governance.capability_lookup (REGISTRY_YAML)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] warn-only——永不阻断 commit（passed=True）；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；YAML 不可达时 fail-loud（logger.warning 告警检测器失效，仍 return True 保留 warn-only 契约；create_guard 已 fail-closed 阻断，本 gate 无需重复阻断）；git diff 失败亦 fail-loud；token 匹配 ≥4 字符才告警（减少短词误报）
# [MODIFY-GUARD] gate_id="CAPABILITY-OVERLAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML/git diff 异常降级为 fail-loud warn（不阻断 commit 保留 warn-only 契约，但 logger.warning 告警检测器失效以防静默漂移）；warn-only gate 的 fail-closed 语义=告警而非阻断
# [TESTS] tests/governance/commit_gates/test_capability_overlap_gate.py
# [A_module] module_id=MOD-GOV-capability_overlap_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""capability_overlap_gate.py — 新建 .py 文件 CapabilityLookup 提示门禁（warn-only，2026-06-30 治本）

检测 commit 中新建的 .py 文件名是否与 capability_canonical_file_registry.yaml 已注册能力
的 aliases 重叠——命中则 logger.warning 告警（**不阻断 commit**），提示 AI 应扩展现有
canonical 文件而非新建。

病根（缺口4：CapabilityLookup 被动反查）
-----------------------------------------
AGENTS.md §7 已把"查 CapabilityLookup 确认能力是否已存在"列为 step 0，但仅靠文档约定——
新 AI 若跳过 AGENTS.md 或未读 §7，可在 commit 时直接新建 .py 脚本导致重复造轮子。
GATE-NO-PURE-SHIM 只拦 pure re-export shim，拦不住完整实现（新 AI 写了个完整的重复实现，
不是 shim，GATE-NO-PURE-SHIM 放行）。本 gate 在 commit 时自动反查 capability registry，
补上文档约定的代码层兜底。

warn-only 裁定
---------------
文件名 token 匹配是启发式（可能误报：新建 ``data_loader.py`` 可能命中 ``data_loader``
capability 但实际是不同域的合法新脚本）。阻断会阻碍合法开发，故仅 logger.warning 告警——
AI 看到 warning 后自行判断是扩展还是新建。

Usage::

    from zephyr.gov_enforcement.commit_gates.capability_overlap_gate import make_capability_overlap_gate

    registry.register(make_capability_overlap_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import re

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_capability_overlap_gate"]

_REGISTRY_PREFIX = "docs/01_policies_and_standards/_registry/"


def _tokenize(name: str) -> set[str]:
    """文件名/alias 分词：按 ``_`` / ``-`` / ``.`` 拆分，过滤 <4 字符的 token。"""
    parts = re.split(r"[_\-\.]", name.lower())
    return {p for p in parts if len(p) >= 4}


# === 裁定#217 Tier2 P1 Extract Method 重构（2026-07-15）===
# 原 _check 136 行 McCabe=31（6 段 pipeline：staged→filter→load YAML→build index→
# check py overlap→check yaml overlap）。治本：提取为 6 个模块级 helper（均 McCabe≤15），
# _check 简化为 ~25 行 pipeline（McCabe≈7）。行为等价契约：warn-only（永远 passed=True），
# fail-loud 语义不变，token 匹配规则不变。


def _get_staged_new_files(gateway) -> list[str] | None:
    """获取 staged 新增(A) 文件列表。None=fail-loud（warn-only 契约仍 return True）。"""
    try:
        diff_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
        )
        if diff_result.returncode != 0:
            logger.warning(
                "CAPABILITY-OVERLAP gate fail-loud: git diff 失败(rc=%d)，"
                "检测器失效，无法检测 capability 重叠。", diff_result.returncode,
            )
            return None
        return diff_result.stdout.strip().splitlines()
    except Exception as e:
        logger.error(
            "CAPABILITY-OVERLAP gate fail-loud: git diff 异常(%s: %s)，"
            "检测器失效，无法检测 capability 重叠。", type(e).__name__, e,
            exc_info=True,
        )
        return None


def _filter_new_files(staged_new: list[str]) -> tuple[list[str], list[str]]:
    """从 staged 新增文件中筛选 (.py 文件, _registry/ .yaml/.yml 文件)。"""
    py_files = [
        f.replace("\\", "/") for f in staged_new
        if f.endswith(".py") and not is_test_exempt(f)
    ]
    yaml_files = [
        f.replace("\\", "/") for f in staged_new
        if f.replace("\\", "/").endswith((".yaml", ".yml"))
        and f.replace("\\", "/").startswith(_REGISTRY_PREFIX)
    ]
    return py_files, yaml_files


def _load_registry_data() -> dict | None:
    """加载 capability registry YAML。None=fail-loud（warn-only 契约仍 return True）。"""
    from zephyr.governance.capability_lookup import REGISTRY_YAML

    if not REGISTRY_YAML.exists():
        logger.warning(
            "CAPABILITY-OVERLAP gate fail-loud: registry 缺失(%s)，检测器失效，"
            "无法检测 capability 重叠。修复：git checkout HEAD -- %s",
            REGISTRY_YAML, REGISTRY_YAML,
        )
        return None
    try:
        import yaml
        data = yaml.safe_load(REGISTRY_YAML.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(
            "CAPABILITY-OVERLAP gate fail-loud: registry 解析失败(%s: %s)，"
            "检测器失效，无法检测 capability 重叠。",
            type(e).__name__, e, exc_info=True,
        )
        return None
    if not isinstance(data, dict):
        logger.warning(
            "CAPABILITY-OVERLAP gate fail-loud: registry 顶层非 dict，检测器失效。"
        )
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


def make_capability_overlap_gate() -> GateSpec:
    """构造新建 .py 文件 CapabilityLookup 提示门禁 GateSpec（warn-only）。

    Returns:
        GateSpec(gate_id="CAPABILITY-OVERLAP", priority=200)。
        priority=200——在 HELD-OVERLAP(50) 之后、其他阻断 gate 之前执行
        （warn-only 不阻断，早执行晚执行无差异，但早执行可早 log）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        staged_new = _get_staged_new_files(gateway)
        if staged_new is None:
            return True, ""  # warn-only 契约：fail-loud 仍 return True

        new_py_files, new_yaml_files = _filter_new_files(staged_new)
        if not new_py_files and not new_yaml_files:
            return True, ""

        data = _load_registry_data()
        if data is None:
            return True, ""  # warn-only 契约：fail-loud 仍 return True

        cap_tokens = _build_cap_token_index(data)
        if not cap_tokens:
            return True, ""  # registry 空，无意义

        warnings: list[str] = []
        warnings.extend(_check_py_overlap(new_py_files, cap_tokens))
        warnings.extend(_check_yaml_overlap(new_yaml_files))

        if warnings:
            logger.warning(
                "CAPABILITY-OVERLAP gate warn-only: %s", " | ".join(warnings)
            )
        return True, ""  # warn-only：永远 passed=True

    return GateSpec(gate_id="CAPABILITY-OVERLAP", check=_check, priority=200)
