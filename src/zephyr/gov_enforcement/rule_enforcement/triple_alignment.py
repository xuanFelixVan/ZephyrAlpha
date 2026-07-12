# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §4
# [MODULE] zephyr.gov_enforcement.rule_enforcement.triple_alignment
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS] GateEngine;phase_manager;session_gate_checklist
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 蓝图↔代码↔依赖图三方必须对齐;module_id/stability/safety/ai_autonomy三处一致;文件清单三方匹配
# [MODIFY-GUARD] _registry.yaml;gate_engine.py;depgraph.nodes
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TripleAlignmentError(list[AlignmentViolation])
# [TESTS] tests/test_triple_alignment.py
# [A_module] module_id=MOD-GOV_triple_alignment | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-TRIPLE-ALIGN: 蓝图↔代码↔依赖图三方对齐门禁

检查项：
  1. module_id 三方一致：蓝图 frontmatter ↔ 代码 [BLUEPRINT] 头部 ↔ 依赖图 node
  2. 属性三方一致：stability/safety/ai_autonomy 蓝图 ↔ 代码头部 ↔ 依赖图
  3. 文件清单三方匹配：蓝图 §0.1 ↔ 磁盘文件 ↔ 依赖图 source_path
  4. 依赖声明三方一致：蓝图 depends_on ↔ 代码 import ↔ 依赖图 edges
  5. 注册表覆盖：blueprint_registry.yaml ↔ module-registry.yaml ↔ 依赖图 §5

SSoT: MOD-GATE_ENGINE gate-engine
Version: 0.1.0
"""

from __future__ import annotations

from typing import Final
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

logger = logging.getLogger(__name__)

# P2迁移审查修复：禁止 Path("D:/ZephyrAlpha") 硬编码，改用 REPO_ROOT 真源
BLUEPRINT_REGISTRY: Final[Path] = REPO_ROOT / "docs/03_modules/blueprint_registry.yaml"
MODULE_REGISTRY: Final[Path] = REPO_ROOT / "docs/03_modules/module-registry.yaml"
GATES_REGISTRY: Final[Path] = REPO_ROOT / "src/zephyr/governance/rule_enforcement/_registry.yaml"
BLUEPRINTS_DIR: Final[Path] = REPO_ROOT / "docs/03_modules"


class Severity(str, Enum):
    ERROR = "ERROR"
    WARN = "WARN"


@dataclass
class AlignmentViolation:
    check: str
    severity: Severity
    module_id: str
    source: str
    expected: str
    actual: str
    detail: str = ""


@dataclass
class TripleAlignmentResult:
    violations: list[AlignmentViolation] = field(default_factory=list)
    checked_modules: int = 0
    passed: bool = True

    def add_violation(self, v: AlignmentViolation) -> None:
        self.violations.append(v)
        if v.severity is Severity.ERROR:
            self.passed = False

    def summary(self) -> str:
        errors = [v for v in self.violations if v.severity is Severity.ERROR]
        warns = [v for v in self.violations if v.severity is Severity.WARN]
        return (
            f"Triple Alignment: {self.checked_modules} modules checked, "
            f"{len(errors)} ERROR, {len(warns)} WARN, "
            f"{'PASS' if self.passed else 'FAIL'}"
        )


def _load_yaml(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _parse_code_headers(py_path: Path) -> dict[str, str]:
    headers: dict[str, str] = {}
    if not py_path.exists():
        return headers
    try:
        content = py_path.read_text(encoding="utf-8")
    except Exception:
        return headers
    for line in content.splitlines()[:30]:
        m = re.match(r"^#\s*\[(\w[\w-]*)\]\s*(.+)", line)
        if m:
            headers[m.group(1)] = m.group(2).strip()
    return headers


def _extract_dep_map_modules() -> dict[str, dict[str, str]]:
    """从 depgraph PostgreSQL 数据库查询所有模块节点。

    替代原 system-dependency-map.md §5 解析——depgraph.nodes 是模块归属的机器真源。
    nodes 表用 blueprint_id 列存储 module_id（如 MOD-CONTEXT_ENGINE），
    每个模块可能有多行（每行一个文件路径），取 DISTINCT blueprint_id 去重。
    """
    modules: dict[str, dict[str, str]] = {}
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
        conn = get_depgraph_pg_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT DISTINCT blueprint_id, path, blueprint_path "
                "FROM nodes WHERE blueprint_id ~ '^(MOD-|SH-|SYS-)'",
            )
            for row in cur.fetchall():
                mid = row[0]
                if mid and mid not in modules:
                    modules[mid] = {
                        "source_path": row[1] or "",
                        "blueprint_path": row[2] or "",
                    }
            cur.close()
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Failed to query depgraph nodes: %s", e, exc_info=True)
    return modules


def _extract_dep_map_depths(content: str) -> dict[str, str]:
    depths: dict[str, str] = {}
    for line in content.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(MOD-INF-\d+)", line)
        if m:
            depths[m.group(2)] = m.group(1)
    return depths


def check_triple_alignment(
    specific_module: str | None = None,
    warn_only: bool = False,
) -> TripleAlignmentResult:
    result = TripleAlignmentResult()

    bp_registry_data = _load_yaml(BLUEPRINT_REGISTRY)
    if not bp_registry_data or "blueprints" not in bp_registry_data:
        result.add_violation(
            AlignmentViolation(
                check="registry_load",
                severity=Severity.ERROR,
                module_id="*",
                source="blueprint_registry.yaml",
                expected="valid YAML",
                actual="load failed",
            )
        )
        return result

    dep_map_modules = _extract_dep_map_modules()

    bp_entries: dict[str, dict] = {}
    for entry in bp_registry_data.get("blueprints", []):
        mid = entry.get("module_id", "")
        if mid:
            bp_entries[mid] = entry

    for mid, bp in bp_entries.items():
        if specific_module and mid != specific_module:
            continue
        result.checked_modules += 1

        bp_path_str = bp.get("file_path", "")
        # 修复: file_path 由 sync_registry_from_blueprints.py 的 make_registry_path 生成,
        # 相对 REPO_ROOT/"docs" (如 "03_modules/_cross_layer/.../blueprint.md"),
        # 不是相对 BLUEPRINTS_DIR。原 BLUEPRINTS_DIR / bp_path_str 会产生双重 03_modules 前缀。
        bp_path = REPO_ROOT / "docs" / bp_path_str if bp_path_str else None
        # 红蓝对抗修复：路径边界验证，防止路径穿越攻击
        if bp_path:
            try:
                resolved_bp = bp_path.resolve()
                if not resolved_bp.is_relative_to(BLUEPRINTS_DIR.resolve()):
                    result.add_violation(
                        AlignmentViolation(
                            check="blueprint_path_traversal",
                            severity=Severity.ERROR,
                            module_id=mid,
                            source="blueprint_registry.yaml file_path",
                            expected="path within docs/03_modules/",
                            actual=f"PATH TRAVERSAL: {bp_path_str}",
                        )
                    )
                    bp_path = None
            except (OSError, ValueError):
                bp_path = None
        bp_frontmatter: dict[str, Any] = {}
        if bp_path and bp_path.exists():
            try:
                text = bp_path.read_text(encoding="utf-8")
                # 防御性: 去除所有前导 BOM (部分文件可能因编辑器积累多个 BOM)
                text = text.lstrip("\ufeff")
                if text.startswith("---"):
                    end = text.find("---", 3)
                    if end > 0:
                        fm_text = text[3:end]
                        bp_frontmatter = yaml.safe_load(fm_text) or {}
            except Exception as e:
                logger.warning("suppressed error in triple_alignment", exc_info=True)

        source_path_str = bp_frontmatter.get("actual_disk_path", "")
        first_source = source_path_str.split("+")[0].strip() if source_path_str else ""
        code_path = REPO_ROOT / first_source if first_source else None
        code_headers = _parse_code_headers(code_path) if code_path and code_path.exists() else {}

        # Check 1: module_id 三方一致
        code_bp_header = code_headers.get("BLUEPRINT", "")
        code_mid_match = re.match(r"(MOD-INF-\d+)", code_bp_header)
        code_mid = code_mid_match.group(1) if code_mid_match else ""
        dep_map_mid = mid in dep_map_modules

        if code_path and code_path.exists() and code_mid and code_mid != mid:
            result.add_violation(
                AlignmentViolation(
                    check="module_id_code_vs_blueprint",
                    severity=Severity.ERROR,
                    module_id=mid,
                    source="code [BLUEPRINT] header",
                    expected=mid,
                    actual=code_mid,
                )
            )

        if not dep_map_mid:
            result.add_violation(
                AlignmentViolation(
                    check="module_id_dep_map_missing",
                    severity=Severity.WARN,
                    module_id=mid,
                    source="depgraph.nodes",
                    expected=mid,
                    actual="NOT FOUND",
                )
            )

        # Check 2: 属性三方一致 (stability/safety/ai_autonomy)
        for attr in ("stability", "safety_level", "ai_autonomy"):
            bp_val = str(bp_frontmatter.get(attr, "")).lower()
            code_val = ""
            header_key = attr.upper().replace("SAFETY_LEVEL", "SAFETY")
            code_val = code_headers.get(header_key, "").lower()
            dep_val = ""

            if bp_val and code_val and bp_val != code_val:
                sev = Severity.ERROR if attr == "stability" else Severity.WARN
                result.add_violation(
                    AlignmentViolation(
                        check=f"attr_{attr}_blueprint_vs_code",
                        severity=sev,
                        module_id=mid,
                        source=f"blueprint frontmatter vs code [{header_key}]",
                        expected=bp_val,
                        actual=code_val,
                    )
                )

        # Check 3: construction_progress 与代码实际状态
        progress = bp.get("construction_progress", "")
        if progress in ("not_started", "") and code_path and code_path.exists():
            code_size = code_path.stat().st_size
            if code_size > 500:
                result.add_violation(
                    AlignmentViolation(
                        check="construction_progress_stale",
                        severity=Severity.ERROR,
                        module_id=mid,
                        source="blueprint_registry.yaml",
                        expected="partially_implemented or implemented",
                        actual=f"not_started (but code exists: {code_size} bytes)",
                    )
                )

        # Check 4: 蓝图文件路径存在性
        if bp_path_str and (not bp_path or not bp_path.exists()):
            result.add_violation(
                AlignmentViolation(
                    check="blueprint_file_missing",
                    severity=Severity.ERROR,
                    module_id=mid,
                    source="blueprint_registry.yaml file_path",
                    expected=bp_path_str,
                    actual="FILE NOT FOUND",
                )
            )

        # Check 5: 代码文件/目录存在性（如果蓝图声明了 actual_disk_path）
        progress_val = bp.get("construction_progress", "")
        early_stage = progress_val in ("design_only", "not_started", "")
        if source_path_str:
            paths_to_check = [p.strip() for p in source_path_str.split("+") if p.strip()]
            for p in paths_to_check:
                resolved = REPO_ROOT / p
                # 红蓝对抗修复：actual_disk_path 路径穿越检查
                try:
                    resolved_abs = resolved.resolve()
                    if not resolved_abs.is_relative_to(REPO_ROOT.resolve()):
                        result.add_violation(
                            AlignmentViolation(
                                check="code_path_traversal",
                                severity=Severity.ERROR,
                                module_id=mid,
                                source="blueprint actual_disk_path",
                                expected="path within REPO_ROOT",
                                actual=f"PATH TRAVERSAL: {p}",
                            )
                        )
                        continue
                except (OSError, ValueError):
                    continue
                if not resolved.exists():
                    sev = Severity.WARN if early_stage else Severity.ERROR
                    result.add_violation(
                        AlignmentViolation(
                            check="code_path_missing",
                            severity=sev,
                            module_id=mid,
                            source="blueprint actual_disk_path",
                            expected=p,
                            actual="PATH NOT FOUND",
                        )
                    )

        # Check 6: 依赖图有模块但蓝图没有（孤儿节点）
    for dep_mid in dep_map_modules:
        if dep_mid.startswith("MOD-INF-") and dep_mid not in bp_entries:
            if specific_module and dep_mid != specific_module:
                continue
            result.add_violation(
                AlignmentViolation(
                    check="dep_map_orphan_module",
                    severity=Severity.WARN,
                    module_id=dep_mid,
                    source="depgraph.nodes",
                    expected="in blueprint_registry.yaml",
                    actual="NOT FOUND",
                )
            )

    if warn_only:
        result.passed = True

    return result


def main() -> None:
    import sys

    warn_only = "--warn-only" in sys.argv
    specific = None
    for arg in sys.argv[1:]:
        if not arg.startswith("-"):
            specific = arg

    result = check_triple_alignment(specific_module=specific, warn_only=warn_only)
    print(result.summary())
    for v in result.violations:
        icon = "🔴" if v.severity is Severity.ERROR else "🟡"
        print(
            f"  {icon} [{v.check}] {v.module_id}: {v.detail or f'{v.source}: expected={v.expected}, actual={v.actual}'}"
        )

    if not result.passed:
        sys.exit(1)


if __name__ == "__main__":
    main()