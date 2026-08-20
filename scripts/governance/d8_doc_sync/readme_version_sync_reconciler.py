# [BLUEPRINT] MOD-readme_version_sync | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] scripts.governance.d8_doc_sync.readme_version_sync_reconciler
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-08:post-commit reconciler触发非时间触发 | INV-09:触发条件=README.md或真源文件(pyproject.toml/infrastructure_registry.yaml)变更 | INV-10:校验失败降级warn不阻断其他reconciler | INV-11:版本号漂移只warn不auto-fix(版本升级需人工决策)
# [MODIFY-GUARD] gate_id="GATE-README-VERSION-SYNC"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] _reconcile异常降级为warn ReconcileResult；真源文件读取失败降级warn；版本号解析失败降级warn
# [TESTS] tests/scripts/governance/d8_doc_sync/test_readme_version_sync_reconciler.py
# [A_module] module_id=MOD-readme_version_sync | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""readme_version_sync_reconciler.py — README 版本号派生展示校验 reconciler

职责：注册为 ReconciliationRegistry 的 reconciler，post-commit 自动触发。
校验 README.md "环境要求"章节的版本号是否与真源文件一致，漂移时 warn。

治本病根（2026-07-19）：
  100% AI 开发项目里，README 版本号是派生展示（真源在 pyproject.toml +
  infrastructure_registry.yaml）。AI 改真源时未必记得同步改 README，造成
  README 写旧版本 / 真源已升级的漂移。靠"AI 自觉"必然漂移，必须有机械校验。

设计：
  - 事件驱动：post-commit reconciler（非 time.sleep/while True 轮询，满足PERM-TRIGGER gate）
  - 触发条件：committed_files 含 README.md 或真源文件
  - 校验项：
    1. README Python 版本 == pyproject.toml requires-python
    2. README PostgreSQL 版本 == infrastructure_registry.yaml INFRA-DB-003 note
    3. README ClickHouse 版本 == infrastructure_registry.yaml INFRA-DB-006 note
    4. README ChromaDB 版本 >= pyproject.toml chromadb 下限
  - 行为：漂移时 warn ReconcileResult（不 auto-fix，版本升级需人工决策）
  - 容错：真源文件读取失败/版本号解析失败 -> warn 不阻断其他 reconciler

校验规则说明：
  - Python: 精确匹配（README ">=3.12" == pyproject 'requires-python = ">=3.12"'）
  - PostgreSQL: 提取主版本号（README "16" == INFRA-DB-003 note "PostgreSQL 16"）
  - ClickHouse: 提取版本号（README "26.6.1" == INFRA-DB-006 note "ClickHouse 26.6.1"）
  - ChromaDB: 范围校验（README "0.5.23" >= pyproject "chromadb>=0.4.24,<1.0.0" 下限）

Usage::

    from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry
    from readme_version_sync_reconciler import make_readme_version_sync_reconciler

    registry = ReconciliationRegistry()
    registry.register(make_readme_version_sync_reconciler(project_root))
"""

from __future__ import annotations

__manifest__ = """
args: []
description: readme_version_sync_reconciler.py — README 版本号派生展示校验 reconciler
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

import yaml

logger = logging.getLogger(__name__)

__all__ = ["make_readme_version_sync_reconciler"]

# ── 配置常量 ──
_project_root = Path(__file__).resolve().parent.parent.parent.parent  # D:\ZephyrAlpha
_README_FILE = _project_root / "README.md"
_PYPROJECT_FILE = _project_root / "pyproject.toml"
_INFRA_REGISTRY_FILE = (
    _project_root / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "infrastructure_registry.yaml"
)

# 触发文件清单（README.md 或真源文件任一变更即触发校验）
_TRIGGER_FILES: frozenset[str] = frozenset(
    {
        "README.md",
        "pyproject.toml",
        "docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml",
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
    """触发条件判断：committed_files 含 README.md 或真源文件。"""
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
        logger.warning("readme_version_sync: failed to read %s: %s", path, e)
        return None


def _extract_readme_python_version(readme: str) -> str | None:
    """从 README 提取 Python 版本（如 ">=3.12"）。

    匹配 "环境要求" 章节的 Python 行：`| Python | >=3.12 | ...`
    """
    # 匹配表格行：| Python | <版本> |
    match = re.search(r"\|\s*Python\s*\|\s*([<>!=~.\d]+)\s*\|", readme)
    return match.group(1) if match else None


def _extract_pyproject_python_version(pyproject: str) -> str | None:
    """从 pyproject.toml 提取 requires-python 版本。"""
    match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', pyproject)
    return match.group(1) if match else None


def _extract_readme_pg_version(readme: str) -> str | None:
    """从 README 提取 PostgreSQL 主版本号（如 "16"）。"""
    match = re.search(r"\|\s*PostgreSQL\s*\|\s*(\d+)\s*\|", readme)
    return match.group(1) if match else None


def _extract_readme_clickhouse_version(readme: str) -> str | None:
    """从 README 提取 ClickHouse 版本号（如 "26.6.1"）。"""
    match = re.search(r"\|\s*ClickHouse\s*\|\s*([\d.]+)\s*\|", readme)
    return match.group(1) if match else None


def _extract_readme_chromadb_version(readme: str) -> str | None:
    """从 README 提取 ChromaDB 版本号（如 "0.5.23"）。"""
    match = re.search(r"\|\s*ChromaDB\s*\|\s*([\d.]+)\s*\|", readme)
    return match.group(1) if match else None


def _extract_pyproject_chromadb_lower_bound(pyproject: str) -> str | None:
    """从 pyproject.toml 提取 chromadb 依赖下限版本。

    匹配 `chromadb>=0.4.24,<1.0.0` -> "0.4.24"
    """
    match = re.search(r'"chromadb>=([\d.]+)', pyproject)
    return match.group(1) if match else None


def _extract_infra_pg_version(infra_yaml: dict) -> str | None:
    """从 infrastructure_registry.yaml 提取 PostgreSQL 主版本号。

    在 INFRA-DB-003 note 字段中查找 "PostgreSQL 16" 模式。
    """
    for item in infra_yaml.get("infrastructure", []):
        if item.get("infra_id") == "INFRA-DB-003":
            note = item.get("note", "")
            # 匹配 "PostgreSQL 16" 或 "PostgreSQL 16.x"
            match = re.search(r"PostgreSQL\s+(\d+)", note)
            if match:
                return match.group(1)
            # 也在 description 字段找
            desc = item.get("description", "")
            match = re.search(r"PostgreSQL\s+(\d+)", desc)
            if match:
                return match.group(1)
    return None


def _extract_infra_clickhouse_version(infra_yaml: dict) -> str | None:
    """从 infrastructure_registry.yaml 提取 ClickHouse 版本号。

    在 INFRA-DB-006 note 字段中查找 "ClickHouse 26.6.1" 模式。
    """
    for item in infra_yaml.get("infrastructure", []):
        if item.get("infra_id") == "INFRA-DB-006":
            note = item.get("note", "")
            # 匹配 "ClickHouse 26.6.1" 或 "ClickHouse 26.6"
            match = re.search(r"ClickHouse\s+([\d.]+)", note)
            if match:
                return match.group(1)
            # 也在 description 字段找
            desc = item.get("description", "")
            match = re.search(r"ClickHouse\s+([\d.]+)", desc)
            if match:
                return match.group(1)
    return None


def _parse_version_tuple(version: str) -> tuple[int, ...]:
    """将版本字符串解析为整数元组（如 "0.5.23" -> (0, 5, 23)）。

    用于版本大小比较。解析失败返回空元组。
    """
    parts = re.findall(r"\d+", version)
    return tuple(int(p) for p in parts)


def _check_python(readme: str, pyproject: str) -> list[str]:
    """校验 Python 版本一致性。返回漂移描述列表（空=一致）。"""
    findings: list[str] = []
    readme_v = _extract_readme_python_version(readme)
    pyproject_v = _extract_pyproject_python_version(pyproject)
    if readme_v is None:
        findings.append("README 未找到 Python 版本号（期望表格行 | Python | <版本> |）")
    if pyproject_v is None:
        findings.append("pyproject.toml 未找到 requires-python")
    if readme_v and pyproject_v and readme_v != pyproject_v:
        findings.append(f"Python 版本漂移：README='{readme_v}' vs pyproject.toml='{pyproject_v}'")
    return findings


def _check_postgresql(readme: str, infra_yaml: dict) -> list[str]:
    """校验 PostgreSQL 版本一致性。返回漂移描述列表（空=一致）。"""
    findings: list[str] = []
    readme_v = _extract_readme_pg_version(readme)
    infra_v = _extract_infra_pg_version(infra_yaml)
    if readme_v is None:
        findings.append("README 未找到 PostgreSQL 主版本号")
    if infra_v is None:
        findings.append("infrastructure_registry.yaml INFRA-DB-003 未找到 PostgreSQL 版本")
    if readme_v and infra_v and readme_v != infra_v:
        findings.append(f"PostgreSQL 版本漂移：README='{readme_v}' vs INFRA-DB-003='{infra_v}'")
    return findings


def _check_clickhouse(readme: str, infra_yaml: dict) -> list[str]:
    """校验 ClickHouse 版本一致性。返回漂移描述列表（空=一致）。"""
    findings: list[str] = []
    readme_v = _extract_readme_clickhouse_version(readme)
    infra_v = _extract_infra_clickhouse_version(infra_yaml)
    if readme_v is None:
        findings.append("README 未找到 ClickHouse 版本号")
    if infra_v is None:
        findings.append("infrastructure_registry.yaml INFRA-DB-006 未找到 ClickHouse 版本")
    if readme_v and infra_v and readme_v != infra_v:
        findings.append(f"ClickHouse 版本漂移：README='{readme_v}' vs INFRA-DB-006='{infra_v}'")
    return findings


def _check_chromadb(readme: str, pyproject: str) -> list[str]:
    """校验 ChromaDB 版本范围（README 版本 >= pyproject 下限）。返回漂移描述列表。"""
    findings: list[str] = []
    readme_v = _extract_readme_chromadb_version(readme)
    lower_bound = _extract_pyproject_chromadb_lower_bound(pyproject)
    if readme_v is None:
        findings.append("README 未找到 ChromaDB 版本号")
        return findings
    if lower_bound is None:
        findings.append("pyproject.toml 未找到 chromadb 依赖下限")
        return findings
    readme_tuple = _parse_version_tuple(readme_v)
    lower_tuple = _parse_version_tuple(lower_bound)
    if not readme_tuple or not lower_tuple:
        findings.append(f"ChromaDB 版本解析失败：README='{readme_v}' lower_bound='{lower_bound}'")
        return findings
    if readme_tuple < lower_tuple:
        findings.append(f"ChromaDB 版本低于下限：README='{readme_v}' < pyproject下限='{lower_bound}'")
    return findings


def _reconcile(committed_files: list[str], session_id: str) -> Any:
    """执行版本号校验。返回 ReconcileResult（auto_committed 或 warn）。"""
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        ReconcileResult = dict  # type: ignore

    # 读取三个真源文件
    readme_text = _read_text(_README_FILE)
    if readme_text is None:
        return ReconcileResult(
            action="warn",
            detail=f"README.md 读取失败: {_README_FILE}",
        )

    pyproject_text = _read_text(_PYPROJECT_FILE)
    if pyproject_text is None:
        return ReconcileResult(
            action="warn",
            detail=f"pyproject.toml 读取失败: {_PYPROJECT_FILE}",
        )

    try:
        infra_yaml = yaml.safe_load(_read_text(_INFRA_REGISTRY_FILE)) or {}
    except (yaml.YAMLError, OSError) as e:
        return ReconcileResult(
            action="warn",
            detail=f"infrastructure_registry.yaml 解析失败: {e}",
        )

    # 逐项校验
    findings: list[str] = []
    findings.extend(_check_python(readme_text, pyproject_text))
    findings.extend(_check_postgresql(readme_text, infra_yaml))
    findings.extend(_check_clickhouse(readme_text, infra_yaml))
    findings.extend(_check_chromadb(readme_text, pyproject_text))

    if not findings:
        return ReconcileResult(
            action="auto_committed",
            detail="README 版本号与真源一致（Python/PostgreSQL/ClickHouse/ChromaDB 4 项校验通过）",
        )

    # 漂移：warn（不 auto-fix，版本升级需人工决策）
    summary = "; ".join(findings)
    logger.warning("readme_version_sync: drift detected: %s", summary)
    return ReconcileResult(
        action="warn",
        detail=f"README 版本号漂移（{len(findings)} 项）: {summary}",
    )


def make_readme_version_sync_reconciler(project_root: Path | None = None):
    """工厂函数：创建 README 版本号校验 reconciler spec。

    Args:
        project_root: 项目根路径（默认自动检测）

    Returns:
        ReconcilerSpec（含 gate_id/trigger/reconcile/priority）
    """
    global _project_root, _README_FILE, _PYPROJECT_FILE, _INFRA_REGISTRY_FILE
    if project_root is not None:
        _project_root = Path(project_root)
        _README_FILE = _project_root / "README.md"
        _PYPROJECT_FILE = _project_root / "pyproject.toml"
        _INFRA_REGISTRY_FILE = (
            _project_root
            / "docs"
            / "01_policies_and_standards"
            / "_registry"
            / "catalogs"
            / "infrastructure_registry.yaml"
        )

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
        gate_id="GATE-README-VERSION-SYNC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=210,  # 晚于 BACKUP-RECONILER(200)，README 校验非紧急
        file_ops=frozenset({"read", "write"}),
    )


if __name__ == "__main__":
    # 手动测试入口
    spec = make_readme_version_sync_reconciler()
    print(f"gate_id={spec.gate_id}, priority={spec.priority}")
    # 模拟触发（README.md 在 committed_files 中）
    result = spec.reconcile([str(_README_FILE)], "manual-test")
    print(f"result={result}")
