# [BLUEPRINT] MOD-requirements_version_sync | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] scripts.governance.d8_doc_sync.requirements_version_sync_reconciler
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-12:post-commit reconciler触发非时间触发 | INV-13:触发条件=pyproject.toml或requirements*.txt变更 | INV-14:校验失败降级warn不阻断其他reconciler | INV-15:依赖漂移只warn不auto-fix(版本约束变更需人工决策)
# [MODIFY-GUARD] gate_id="GATE-REQUIREMENTS-VERSION-SYNC"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] _reconcile异常降级为warn ReconcileResult；真源文件读取失败降级warn；依赖解析失败降级warn
# [TESTS] tests/scripts/governance/d8_doc_sync/test_requirements_version_sync_reconciler.py
# [A_module] module_id=MOD-requirements_version_sync | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""requirements_version_sync_reconciler.py — requirements.txt ↔ pyproject.toml 依赖一致性校验 reconciler

职责：注册为 ReconciliationRegistry 的 reconciler，post-commit 自动触发。
校验 requirements.txt / requirements-dev.txt / requirements-demo.txt 与 pyproject.toml
[project.dependencies] / [project.optional-dependencies] dev / demo 的依赖集是否一致，漂移时 warn。

治本病根（2026-08-01，AI-01 根目录审计 W1）：
  requirements*.txt 是 pyproject.toml 的手工镜像（Dockerfile/README 用 pip install -r）。
  AI 改 pyproject.toml 依赖时未必记得同步 requirements.txt，造成 Dockerfile 构建漏装/多装
  依赖的漂移。靠"AI 自觉"必然漂移，必须有机械校验。对标 GATE-README-VERSION-SYNC 模式。

设计：
  - 事件驱动：post-commit reconciler（非轮询，满足 PERM-TRIGGER gate）
  - 触发条件：committed_files 含 pyproject.toml 或 requirements*.txt
  - 校验项（3 组，每组返回漂移描述列表）：
    1. requirements.txt 依赖集 == pyproject.toml [project.dependencies]
    2. requirements-dev.txt 非引用依赖集 == pyproject.toml [project.optional-dependencies] dev
    3. requirements-demo.txt 非引用依赖集 == pyproject.toml [project.optional-dependencies] demo
  - 包名规范化：大小写不敏感 + 连字符/下划线等价（PEP 508 规范）
  - 版本约束：精确字符串匹配（requirements 行内注释已剥离）
  - 行为：漂移时 warn ReconcileResult（不 auto-fix，版本约束变更需人工决策）
  - 容错：真源文件读取失败/依赖解析失败 -> warn 不阻断其他 reconciler

Usage::

    from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry
    from requirements_version_sync_reconciler import make_requirements_version_sync_reconciler

    registry = ReconciliationRegistry()
    registry.register(make_requirements_version_sync_reconciler(project_root))
"""

from __future__ import annotations

__manifest__ = """
args: []
description: requirements_version_sync_reconciler.py — requirements.txt ↔ pyproject.toml
  依赖一致性校验 reconciler
dimensions:
- D8
priority: P2
timeout_seconds: 60
warn_only: false
"""


import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["make_requirements_version_sync_reconciler"]

# ── 配置常量 ──
_project_root = Path(__file__).resolve().parent.parent.parent.parent  # D:\ZephyrAlpha
_PYPROJECT_FILE = _project_root / "pyproject.toml"
_REQUIREMENTS_MAIN = _project_root / "requirements.txt"
_REQUIREMENTS_DEV = _project_root / "requirements-dev.txt"
_REQUIREMENTS_DEMO = _project_root / "requirements-demo.txt"

# 触发文件清单（pyproject.toml 或 requirements*.txt 任一变更即触发校验）
_TRIGGER_FILES: frozenset[str] = frozenset(
    {
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-demo.txt",
    }
)


def _rel_path(file_path: str | Path) -> str:
    """将绝对路径转为相对项目根的相对路径（正斜杠）。"""
    try:
        import os

        return os.path.relpath(str(file_path), str(_project_root)).replace("\\", "/")
    except ValueError:
        return str(file_path)


def _trigger(committed_files: list[str]) -> bool:
    """触发条件判断：committed_files 含 pyproject.toml 或 requirements*.txt。"""
    for f in committed_files:
        rel = _rel_path(f)
        if rel in _TRIGGER_FILES:
            return True
    return False


def _read_text(path: Path) -> str | None:
    """安全读取文本文件，失败返回 None。"""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("requirements_version_sync: failed to read %s: %s", path, e)
        return None


def _normalize_name(name: str) -> str:
    """规范化包名：小写 + 连字符转下划线（PEP 508 大小写/分隔符不敏感）。"""
    return name.strip().lower().replace("-", "_")


def _parse_pyproject_dependencies(pyproject_text: str) -> dict[str, str]:
    """从 pyproject.toml [project.dependencies] 解析依赖。

    返回 {规范化包名: 版本约束} 字典。
    匹配 `dependencies = [ ... ]` 块内的双引号字符串。
    """
    deps: dict[str, str] = {}
    # 定位 dependencies = [ ... ] 块（行首，避免误匹配 optional-dependencies 子节）
    match = re.search(r"^dependencies\s*=\s*\[(.*?)\]", pyproject_text, re.DOTALL | re.MULTILINE)
    if not match:
        return deps
    block = match.group(1)
    for spec_match in re.finditer(r'"([^"]+)"', block):
        spec = spec_match.group(1).strip()
        name, version = _split_name_version(spec)
        if name:
            deps[_normalize_name(name)] = version
    return deps


def _parse_pyproject_optional(pyproject_text: str, section: str) -> dict[str, str]:
    """从 pyproject.toml [project.optional-dependencies] 的指定子节解析依赖。

    Args:
        section: "dev" 或 "demo"

    返回 {规范化包名: 版本约束} 字典。
    匹配 `<section> = [ ... ]` 块内的双引号字符串（行首匹配，避免误匹配）。
    """
    deps: dict[str, str] = {}
    pattern = rf"^{section}\s*=\s*\[(.*?)\]"
    match = re.search(pattern, pyproject_text, re.DOTALL | re.MULTILINE)
    if not match:
        return deps
    block = match.group(1)
    for spec_match in re.finditer(r'"([^"]+)"', block):
        spec = spec_match.group(1).strip()
        name, version = _split_name_version(spec)
        if name:
            deps[_normalize_name(name)] = version
    return deps


def _split_name_version(spec: str) -> tuple[str, str]:
    """从 PEP 508 依赖规格分离包名和版本约束。

    如 "pydantic>=2.0.0,<3.0.0" -> ("pydantic", ">=2.0.0,<3.0.0")
    如 "akshare>=1.12.0" -> ("akshare", ">=1.12.0")
    无版本约束时返回 ("package", "")
    """
    # 包名：字母数字 + 下划线/连字符/点，可能含 [extras]
    m = re.match(r"([a-zA-Z0-9_.-]+(?:\[[^\]]*\])?)\s*(.*)", spec)
    if not m:
        return ("", "")
    name = m.group(1)
    version = m.group(2).strip()
    # 剥离 extras（如 package[extra]）——对比时只看包名+版本
    name = re.sub(r"\[.*\]", "", name)
    return (name, version)


def _parse_requirements_file(path: Path) -> dict[str, str]:
    """解析 requirements 文件，返回 {规范化包名: 版本约束} 字典。

    跳过：空行、注释行（#）、-r/-e/--引用行、环境标记行（不含包名的纯标记）。
    剥离行内注释（空格+井号后的内容）。
    """
    deps: dict[str, str] = {}
    text = _read_text(path)
    if text is None:
        return deps
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        # 跳过 -r / -e / -- 引用
        if line.startswith("-r ") or line.startswith("-e ") or line.startswith("--"):
            continue
        # 剥离行内注释（空格 + #）
        if " #" in line:
            line = line.split(" #")[0].strip()
        # 剥离环境标记（; 后的内容）
        if ";" in line:
            line = line.split(";")[0].strip()
        name, version = _split_name_version(line)
        if name:
            deps[_normalize_name(name)] = version
    return deps


def _check_pair(
    req_deps: dict[str, str],
    pyproject_deps: dict[str, str],
    label: str,
) -> list[str]:
    """对比 requirements 依赖集与 pyproject 依赖集，返回漂移描述列表（空=一致）。

    三类漂移：
      - 缺失：pyproject 有但 requirements 无
      - 多余：requirements 有但 pyproject 无
      - 版本约束不一致
    """
    findings: list[str] = []
    req_names = set(req_deps.keys())
    pyproject_names = set(pyproject_deps.keys())

    missing = pyproject_names - req_names
    if missing:
        findings.append(f"{label}: pyproject 有但 requirements 缺失: {sorted(missing)}")

    extra = req_names - pyproject_names
    if extra:
        findings.append(f"{label}: requirements 有但 pyproject 缺失: {sorted(extra)}")

    for name in sorted(req_names & pyproject_names):
        if req_deps[name] != pyproject_deps[name]:
            findings.append(
                f"{label}: 版本约束不一致 {name}: requirements='{req_deps[name]}' vs pyproject='{pyproject_deps[name]}'"
            )

    return findings


def _reconcile(committed_files: list[str], session_id: str) -> Any:
    """执行依赖一致性校验。返回 ReconcileResult（auto_committed 或 warn）。"""
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        ReconcileResult = dict  # type: ignore

    # 读取 pyproject.toml（真源）
    pyproject_text = _read_text(_PYPROJECT_FILE)
    if pyproject_text is None:
        return ReconcileResult(
            action="warn",
            detail=f"pyproject.toml 读取失败: {_PYPROJECT_FILE}",
        )

    # 解析 pyproject 三组依赖
    pyproject_main = _parse_pyproject_dependencies(pyproject_text)
    pyproject_dev = _parse_pyproject_optional(pyproject_text, "dev")
    pyproject_demo = _parse_pyproject_optional(pyproject_text, "demo")

    # 解析 requirements 三组文件
    req_main = _parse_requirements_file(_REQUIREMENTS_MAIN)
    req_dev = _parse_requirements_file(_REQUIREMENTS_DEV)
    req_demo = _parse_requirements_file(_REQUIREMENTS_DEMO)

    # 逐组校验
    findings: list[str] = []
    findings.extend(_check_pair(req_main, pyproject_main, "requirements.txt ↔ [dependencies]"))
    findings.extend(_check_pair(req_dev, pyproject_dev, "requirements-dev.txt ↔ [dev]"))
    findings.extend(_check_pair(req_demo, pyproject_demo, "requirements-demo.txt ↔ [demo]"))

    if not findings:
        return ReconcileResult(
            action="auto_committed",
            detail="requirements*.txt 与 pyproject.toml 依赖一致（3 组校验通过）",
        )

    # 漂移：warn（不 auto-fix，版本约束变更需人工决策）
    summary = "; ".join(findings)
    logger.warning("requirements_version_sync: drift detected: %s", summary)
    return ReconcileResult(
        action="warn",
        detail=f"requirements 依赖漂移（{len(findings)} 项）: {summary}",
    )


def make_requirements_version_sync_reconciler(project_root: Path | None = None):
    """工厂函数：创建 requirements↔pyproject 依赖一致性校验 reconciler spec。

    Args:
        project_root: 项目根路径（默认自动检测）

    Returns:
        ReconcilerSpec（含 gate_id/trigger/reconcile/priority）
    """
    global _project_root, _PYPROJECT_FILE, _REQUIREMENTS_MAIN, _REQUIREMENTS_DEV, _REQUIREMENTS_DEMO
    if project_root is not None:
        _project_root = Path(project_root)
        _PYPROJECT_FILE = _project_root / "pyproject.toml"
        _REQUIREMENTS_MAIN = _project_root / "requirements.txt"
        _REQUIREMENTS_DEV = _project_root / "requirements-dev.txt"
        _REQUIREMENTS_DEMO = _project_root / "requirements-demo.txt"

    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec
    except ImportError:

        class _ReconcilerSpecFallback:  # type: ignore
            def __init__(self, gate_id, trigger, reconcile, priority=100):
                """__init__ implementation."""
                self.gate_id = gate_id
                self.trigger = trigger
                self.reconcile = reconcile
                self.priority = priority

        ReconcilerSpec = _ReconcilerSpecFallback

    return ReconcilerSpec(
        gate_id="GATE-REQUIREMENTS-VERSION-SYNC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=230,  # 晚于 METRIC-COUNT-DRIFT(220)，依赖同步校验非紧急
        file_ops=frozenset({"read", "write"}),
    )


if __name__ == "__main__":
    # 手动测试入口
    spec = make_requirements_version_sync_reconciler()
    print(f"gate_id={spec.gate_id}, priority={spec.priority}")
    # 模拟触发（pyproject.toml 在 committed_files 中）
    result = spec.reconcile([str(_PYPROJECT_FILE)], "manual-test")
    print(f"result={result}")
