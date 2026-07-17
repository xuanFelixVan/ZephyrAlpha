# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.noqa_validation_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml (SSoT，动态加载合法标记清单)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件含未登记或无理由的自定义 noqa 标记时阻断 commit；ruff/flake8 标准码（E402/BLE001/S324 等）跳过；registry 加载失败 fail-open（不阻断）；只检 staged .py（增量检测，现存违规 grandfather）
# [MODIFY-GUARD] gate_id="NOQA-VALIDATION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——registry/IO 异常降级为 fail-open；检出违规则 fail-closed
# [TESTS] tests/governance/commit_gates/test_noqa_validation_gate.py
# [A_module] module_id=MOD-GOV-noqa_validation_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""noqa_validation_gate.py — 自定义 noqa 标记合规性门禁（NOQA-VALIDATION，ARCH-NOQA-GOV-001 治本）

治本（2026-07-17，ARCH-NOQA-GOV-001）：项目5种自定义 noqa 标记（m02-manual /
m03-duplicate / m07-orphan / m10-time-trigger / gate-vocab）散落221处使用但无门禁
阻断滥用。本 gate 在 GitCommitGateway pre-commit 阶段（in-process）注册，
--no-verify 绕不过。

检测逻辑（in-process，非 subprocess）：
    1. 加载 noqa_exempt_registry.yaml（SSoT，合法标记清单）
    2. 遍历 staged .py 文件
    3. 正则提取 `# noqa: <marker>` 标记
    4. 跳过 ruff/flake8 标准码（格式 `^[A-Z]+\\d+$`，如 E402/BLE001/S324）
    5. 自定义标记 MUST 在 registry 预登记（阻断未登记标记）
    6. 标记行 MUST 附理由（marker 之后同行文本 >= 10 字符，阻断裸豁免）

设计原则：
    - SSoT：合法标记清单从 noqa_exempt_registry.yaml 动态加载，不硬编码
    - fail-open：registry 加载失败/IO 异常时不阻断（环境异常非违规）
    - fail-closed：检出未登记/无理由标记时硬阻断
    - 增量检测：只检 staged .py（现存违规 grandfather，不回溯）

Usage::

    from zephyr.gov_enforcement.commit_gates.noqa_validation_gate import make_noqa_validation_gate
    registry.register(make_noqa_validation_gate())
"""
from __future__ import annotations

import logging
import os
import re
from typing import Any

import yaml

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_noqa_validation_gate"]

_PROJECT_ROOT = (
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))))
)
_REGISTRY_PATH = os.path.join(
    _PROJECT_ROOT, "docs", "01_policies_and_standards", "_registry",
    "catalogs", "noqa_exempt_registry.yaml",
)

# noqa 标记提取正则：`# noqa: <marker>`，marker 含字母（跳过纯注释）
_NOQA_RE = re.compile(r"#\s*noqa:\s*([a-zA-Z][a-zA-Z0-9_-]*)")
# ruff/flake8 标准码格式：大写字母+数字（如 E402/BLE001/S324/W503/F401）
_STANDARD_CODE_RE = re.compile(r"^[A-Z]+\d+$")
_REASON_MIN_LENGTH = 10  # 理由文本最小长度（字符），阻断裸豁免

# registry 缓存（进程级，避免每次 commit 重复加载 YAML）
_REGISTRY_CACHE: dict[str, Any] | None = None


def _load_registry() -> dict[str, Any] | None:
    """加载 noqa_exempt_registry.yaml（SSoT）。fail-open：加载失败返回 None。"""
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None:
        return _REGISTRY_CACHE
    try:
        with open(_REGISTRY_PATH, encoding="utf-8") as f:
            _REGISTRY_CACHE = yaml.safe_load(f)
        return _REGISTRY_CACHE
    except Exception as e:  # noqa: BLE001 — fail-open 不阻断
        logger.warning(
            "NOQA-VALIDATION fail-open: registry 加载失败(%s: %s, path=%s)",
            type(e).__name__, e, _REGISTRY_PATH,
        )
        return None


def _get_registered_markers(registry: dict[str, Any]) -> frozenset[str]:
    """从 registry 提取合法标记集合。"""
    markers = registry.get("markers", []) or []
    return frozenset(m.get("marker", "") for m in markers if m.get("marker"))


def _get_staged_py_files(gateway) -> list[str]:
    """获取所有 staged .py 文件（新增+修改）。git 异常时返回空列表（fail-open）。"""
    try:
        r = gateway._run_git(["git", "diff", "--cached", "--name-only"])
        if r.returncode != 0:
            logger.warning("NOQA-VALIDATION fail-open: git diff 失败(rc=%d)。", r.returncode)
            return []
        return [
            f.replace("\\", "/") for f in r.stdout.strip().splitlines()
            if f.endswith(".py")
        ]
    except Exception as e:  # noqa: BLE001 — fail-open
        logger.warning("NOQA-VALIDATION fail-open: git diff 异常(%s: %s)。", type(e).__name__, e)
        return []


def _resolve_worktree_root(gateway) -> str:
    """获取 worktree root 绝对路径，失败回退 gateway.project_root。"""
    try:
        r = gateway._run_git(["git", "rev-parse", "--show-toplevel"])
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:  # noqa: BLE001
        pass
    return str(getattr(gateway, "project_root", _PROJECT_ROOT))


def _resolve_abs_paths(rel_files: list[str], wt_root: str) -> list[str]:
    """将相对路径解析为绝对路径，过滤不存在的文件。"""
    abs_files: list[str] = []
    for rel in rel_files:
        path = rel if os.path.isabs(rel) else os.path.join(wt_root, rel.replace("/", os.sep))
        if os.path.isfile(path):
            abs_files.append(path)
    return abs_files


def _scan_file_noqa(abs_path: str, registered: frozenset[str]) -> list[str]:
    """扫描单个 .py 文件的 noqa 标记，返回违规描述列表。

    复杂度控制：单函数只做"遍历行+提取marker+校验"三步，校验逻辑内联避免再拆分。
    """
    violations: list[str] = []
    try:
        with open(abs_path, encoding="utf-8") as f:
            source = f.read()
    except Exception as e:  # noqa: BLE001 — fail-open 跳过该文件
        logger.warning("NOQA-VALIDATION skip: 读取失败 %s (%s)", abs_path, e)
        return violations
    for line_no, line in enumerate(source.splitlines(), 1):
        for match in _NOQA_RE.finditer(line):
            marker = match.group(1)
            if _STANDARD_CODE_RE.match(marker):
                continue  # ruff/flake8 标准码跳过
            if marker not in registered:
                violations.append(
                    f"{abs_path}:L{line_no} 未登记的 noqa 标记 '{marker}'"
                    "（需先在 noqa_exempt_registry.yaml 登记）"
                )
                continue
            reason = line[match.end():].strip()
            if len(reason) < _REASON_MIN_LENGTH:
                violations.append(
                    f"{abs_path}:L{line_no} noqa '{marker}' 缺少理由"
                    f"（marker 后需附>={_REASON_MIN_LENGTH}字符理由，阻断裸豁免）"
                )
    return violations


def make_noqa_validation_gate() -> GateSpec:
    """构造 noqa 标记合规性门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NOQA-VALIDATION", priority=71)。
        priority=71——紧随 DANGLING-REFERENCE(70) 之后、BLUEPRINT-FORMAT(70) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        registry = _load_registry()
        if registry is None:
            return True, ""  # fail-open：registry 加载失败不阻断
        registered = _get_registered_markers(registry)
        staged_py = _get_staged_py_files(gateway)
        if not staged_py:
            return True, ""
        wt_root = _resolve_worktree_root(gateway)
        abs_files = _resolve_abs_paths(staged_py, wt_root)
        if not abs_files:
            return True, ""
        violations: list[str] = []
        for fp in abs_files:
            violations.extend(_scan_file_noqa(fp, registered))
        if violations:
            detail = "\n".join(violations[:20])
            return False, (
                "NOQA_VALIDATION_VIOLATION——检出未登记或无理由的自定义 noqa 标记"
                "（ARCH-NOQA-GOV-001）：\n"
                + detail
            )
        return True, ""

    return GateSpec(gate_id="NOQA-VALIDATION", check=_check, priority=71)
