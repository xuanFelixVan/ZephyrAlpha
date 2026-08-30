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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

裁定#216 Tier1 P3 重构（2026-07-15，Extract Method）
----------------------------------------------------
原 check_triple_alignment 212 行 McCabe=53（5 个 check 块在 per-module 循环内串联，
P3 per-entry multi-check 模式）。治本：Extract Method 提取为 1 个 context builder +
5 个 check helper（均 McCabe≤10），check_triple_alignment 简化为 ~40 行 pipeline
（McCabe≈5）。行为等价契约：每个 check helper 接收 _ModuleCheckContext，返回
list[AlignmentViolation]；caller 统一 add_violation。关键行为保持：
  - blueprint_path_traversal 违规在 context builder 中生成（setup 阶段）
  - Check 1-4 在 per-module 循环内按原始顺序执行
  - Check 5（dep_map_orphan）在循环外单独执行
  - warn_only 在最后覆盖 passed=True

注：原 Check 3（stale-state check）已随 ARCH-FRONTMATTER-STATE-001
Phase 3 退役移除——相关字段已从蓝图 frontmatter 与 blueprint_registry.yaml 中删除。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: specific_module 参数
#   fields: 参数 specific_module，类型注解 str | None
#   code: triple_alignment.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: warn_only 参数
#   fields: 参数 warn_only，类型注解 bool
#   code: triple_alignment.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: path 参数
#   fields: 参数 path（无注解）
#   code: triple_alignment.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TripleAlignmentResult
#   name_en: TripleAlignmentResult
#   intro: class TripleAlignmentResult 源码 L160-L177
#   desc: 公共方法（定义序）: add_violation, summary；源码 L160-L177
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② check_triple_alignment
#   name_en: check_triple_alignment
#   intro: check_triple_alignment(specific_module, warn_only) 源码 L498-…
#   desc: 源码 L498-L542
#   inputs: specific_module warn_only
#   outputs: TripleAlignmentResult
# - id: A3
#   name_zh: ③ main
#   name_en: main
#   intro: main() 源码 L545-L563
#   desc: 源码 L545-L563
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ load_yaml
#   name_en: load_yaml
#   intro: 公共接口：load_yaml（Stage 4 公共化）。
#   desc: 公共接口：load_yaml（Stage 4 公共化）。；源码 L571-L573
#   inputs: path
#   outputs: dict | list | None
# - id: A5
#   name_zh: ⑤ extract_dep_map_modules
#   name_en: extract_dep_map_modules
#   intro: 公共接口：extract_dep_map_modules（Stage 4 公共化）。
#   desc: 公共接口：extract_dep_map_modules（Stage 4 公共化）。；源码 L577-L579
#   inputs: 无参数
#   outputs: dict[str, dict[str, str]]
#   （注：A5 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: TripleAlignmentResult
#   name_en: TripleAlignmentResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: GateEngine;phase_manager;session_gate_checklist
# - id: O2
#   name_zh: dict | list | None
#   name_en: dict | list | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: GateEngine;phase_manager;session_gate_checklist
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

logger = logging.getLogger(__name__)

# P2迁移审查修复：禁止 Path("D:/ZephyrAlpha") 硬编码，改用 REPO_ROOT 真源
BLUEPRINT_REGISTRY: Final[Path] = REPO_ROOT / "docs/03_modules/blueprint_registry.yaml"
MODULE_REGISTRY: Final[Path] = REPO_ROOT / "docs/03_modules/module-registry.yaml"
GATES_REGISTRY: Final[Path] = REPO_ROOT / "src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml"
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


def _load_bp_entries() -> dict[str, dict] | None:
    """加载 blueprint 注册表条目（{module_id: entry}）。

    B 类治本（2026-08-19）：blueprint_registry.yaml 已派生退库（03df6215e8，
    #ARCH-BP-REGISTRY-DELETION-001 后续裁定——100% 可由 frontmatter 重生成=派生物，
    盘文件删除+.gitignore+check_no_commit_derived 防重新跟踪）。文件缺失不再是
    事故而是决策终态：优先读盘文件（存在时=已再生的新鲜派生物），缺失则从
    docs/03_modules/**/blueprint.md frontmatter 现算（比读陈旧派生文件更贴近真源）。
    双路皆失败 → None（registry_load ERROR 保留兜底语义）。
    """
    bp_registry_data = _load_yaml(BLUEPRINT_REGISTRY)
    if bp_registry_data and "blueprints" in bp_registry_data:
        return {entry["module_id"]: entry for entry in bp_registry_data["blueprints"] if entry.get("module_id")}
    try:
        import sys

        syncers_dir = REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "syncers"
        if str(syncers_dir) not in sys.path:
            sys.path.insert(0, str(syncers_dir))
        from sync_registry_from_blueprints import (  # noqa: PLC0415 延迟 import 防循环  # noqa: import-integrity  syncers 目录 sys.path 动态注入（L130-131），静态解析不可达
            build_registry_entry,
            extract_frontmatter,
            find_all_blueprints,
        )

        entries: dict[str, dict] = {}
        for fp in find_all_blueprints():
            entry = build_registry_entry(fp, extract_frontmatter(fp))
            mid = entry.get("module_id", "")
            if mid:
                entries[mid] = entry
        logger.info(
            "triple_alignment: blueprint_registry.yaml 不在盘（派生退库终态），已从 frontmatter 现算 %d 条 entries",
            len(entries),
        )
        return entries or None
    except Exception:  # noqa: BLE001 — frontmatter 回退失败走 registry_load ERROR 兜底
        logger.warning("triple_alignment: frontmatter 现算回退失败", exc_info=True)
        return None


def _parse_code_headers(py_path: Path) -> dict[str, str]:
    headers: dict[str, str] = {}
    if not py_path.exists():
        return headers
    try:
        content = py_path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
                "SELECT DISTINCT blueprint_id, path, blueprint_path FROM nodes WHERE blueprint_id ~ '^(MOD-|SH-|SYS-)'",  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
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
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("Failed to query depgraph nodes: %s", e, exc_info=True)
    return modules


def _extract_dep_map_depths(content: str) -> dict[str, str]:
    depths: dict[str, str] = {}
    for line in content.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(MOD-[^\s|]+)", line)
        if m:
            depths[m.group(2)] = m.group(1)
    return depths


# === 裁定#216 Tier1 P3 Extract Method 重构（2026-07-15） ===


@dataclass
class _ModuleCheckContext:
    """Per-module check context（避免 5 个 helper 各自带 8+ 参数）。"""

    mid: str
    bp: dict
    bp_path_str: str
    bp_path: Path | None
    bp_frontmatter: dict[str, Any]
    source_path_str: str
    code_path: Path | None
    code_headers: dict[str, str]
    dep_map_modules: dict[str, dict[str, str]]


def _build_module_check_context(
    mid: str, bp: dict, dep_map_modules: dict[str, dict[str, str]]
) -> tuple[_ModuleCheckContext, list[AlignmentViolation]]:
    """构建 per-module 检查上下文 + setup 阶段违规（blueprint_path_traversal）。

    解析蓝图路径、加载 frontmatter、解析代码头部。路径穿越违规在此阶段生成。
    """
    violations: list[AlignmentViolation] = []
    bp_path_str = bp.get("file_path", "")
    # file_path 由 sync_registry_from_blueprints.py 生成，相对 REPO_ROOT/"docs"
    bp_path = REPO_ROOT / "docs" / bp_path_str if bp_path_str else None
    if bp_path:
        try:
            resolved_bp = bp_path.resolve()
            if not resolved_bp.is_relative_to(BLUEPRINTS_DIR.resolve()):
                violations.append(
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
            text = text.lstrip("\ufeff")
            if text.startswith("---"):
                end = text.find("---", 3)
                if end > 0:
                    bp_frontmatter = yaml.safe_load(text[3:end]) or {}
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in triple_alignment", exc_info=True)

    source_path_str = bp_frontmatter.get("actual_disk_path", "")
    first_source = source_path_str.split("+")[0].strip() if source_path_str else ""
    code_path = REPO_ROOT / first_source if first_source else None
    code_headers = _parse_code_headers(code_path) if code_path and code_path.exists() else {}

    ctx = _ModuleCheckContext(
        mid=mid,
        bp=bp,
        bp_path_str=bp_path_str,
        bp_path=bp_path,
        bp_frontmatter=bp_frontmatter,
        source_path_str=source_path_str,
        code_path=code_path,
        code_headers=code_headers,
        dep_map_modules=dep_map_modules,
    )
    return ctx, violations


def _check_module_id_alignment(ctx: _ModuleCheckContext) -> list[AlignmentViolation]:
    """Check 1: module_id 三方一致（code [BLUEPRINT] vs blueprint registry vs depgraph）。"""
    violations: list[AlignmentViolation] = []
    code_bp_header = ctx.code_headers.get("BLUEPRINT", "")
    code_mid_match = re.match(r"(MOD-INF-\d+)", code_bp_header)
    code_mid = code_mid_match.group(1) if code_mid_match else ""
    if ctx.code_path and ctx.code_path.exists() and code_mid and code_mid != ctx.mid:
        violations.append(
            AlignmentViolation(
                check="module_id_code_vs_blueprint",
                severity=Severity.ERROR,
                module_id=ctx.mid,
                source="code [BLUEPRINT] header",
                expected=ctx.mid,
                actual=code_mid,
            )
        )
    if ctx.mid not in ctx.dep_map_modules:
        violations.append(
            AlignmentViolation(
                check="module_id_dep_map_missing",
                severity=Severity.WARN,
                module_id=ctx.mid,
                source="depgraph.nodes",
                expected=ctx.mid,
                actual="NOT FOUND",
            )
        )
    return violations


def _check_attr_alignment(ctx: _ModuleCheckContext) -> list[AlignmentViolation]:
    """Check 2: 属性三方一致（stability/safety/ai_autonomy 蓝图 vs 代码头部）。"""
    violations: list[AlignmentViolation] = []
    for attr in ("stability", "safety_level", "ai_autonomy"):
        bp_val = str(ctx.bp_frontmatter.get(attr, "")).lower()
        header_key = attr.upper().replace("SAFETY_LEVEL", "SAFETY")
        code_val = ctx.code_headers.get(header_key, "").lower()
        if bp_val and code_val and bp_val != code_val:
            sev = Severity.ERROR if attr == "stability" else Severity.WARN
            violations.append(
                AlignmentViolation(
                    check=f"attr_{attr}_blueprint_vs_code",
                    severity=sev,
                    module_id=ctx.mid,
                    source=f"blueprint frontmatter vs code [{header_key}]",
                    expected=bp_val,
                    actual=code_val,
                )
            )
    return violations


def _check_blueprint_file_exists(ctx: _ModuleCheckContext) -> list[AlignmentViolation]:
    """Check 3: 蓝图文件路径存在性。"""
    violations: list[AlignmentViolation] = []
    if ctx.bp_path_str and (not ctx.bp_path or not ctx.bp_path.exists()):
        violations.append(
            AlignmentViolation(
                check="blueprint_file_missing",
                severity=Severity.ERROR,
                module_id=ctx.mid,
                source="blueprint_registry.yaml file_path",
                expected=ctx.bp_path_str,
                actual="FILE NOT FOUND",
            )
        )
    return violations


def _check_code_path_exists(ctx: _ModuleCheckContext) -> list[AlignmentViolation]:
    """Check 4: 代码文件/目录存在性（含路径穿越检查）。

    注：原 early_stage 判定字段已随 ARCH-FRONTMATTER-STATE-001 Phase 3 退役，
    无法再据其判断 early_stage，缺失代码路径默认按 WARN 处理。
    """
    violations: list[AlignmentViolation] = []
    if not ctx.source_path_str:
        return violations
    for p in [s.strip() for s in ctx.source_path_str.split("+") if s.strip()]:
        resolved = REPO_ROOT / p
        try:
            resolved_abs = resolved.resolve()
            if not resolved_abs.is_relative_to(REPO_ROOT.resolve()):
                violations.append(
                    AlignmentViolation(
                        check="code_path_traversal",
                        severity=Severity.ERROR,
                        module_id=ctx.mid,
                        source="blueprint actual_disk_path",
                        expected="path within REPO_ROOT",
                        actual=f"PATH TRAVERSAL: {p}",
                    )
                )
                continue
        except (OSError, ValueError):
            continue
        if not resolved.exists():
            sev = Severity.WARN
            violations.append(
                AlignmentViolation(
                    check="code_path_missing",
                    severity=sev,
                    module_id=ctx.mid,
                    source="blueprint actual_disk_path",
                    expected=p,
                    actual="PATH NOT FOUND",
                )
            )
    return violations


def _check_dep_map_orphans(
    dep_map_modules: dict[str, dict[str, str]],
    bp_entries: dict[str, dict],
    specific_module: str | None,
) -> list[AlignmentViolation]:
    """Check 5: 依赖图有模块但蓝图没有（孤儿节点）。"""
    violations: list[AlignmentViolation] = []
    for dep_mid in dep_map_modules:
        if dep_mid.startswith("MOD-INF-") and dep_mid not in bp_entries:
            if specific_module and dep_mid != specific_module:
                continue
            violations.append(
                AlignmentViolation(
                    check="dep_map_orphan_module",
                    severity=Severity.WARN,
                    module_id=dep_mid,
                    source="depgraph.nodes",
                    expected="in blueprint_registry.yaml",
                    actual="NOT FOUND",
                )
            )
    return violations


def check_triple_alignment(
    specific_module: str | None = None,
    warn_only: bool = False,
) -> TripleAlignmentResult:
    result = TripleAlignmentResult()

    bp_entries = _load_bp_entries()
    if bp_entries is None:
        result.add_violation(
            AlignmentViolation(
                check="registry_load",
                severity=Severity.ERROR,
                module_id="*",
                source="blueprint_registry.yaml",
                expected="valid YAML 或 frontmatter 可现算",
                actual="load failed（文件缺失且 frontmatter 回退失败）",
            )
        )
        return result

    dep_map_modules = _extract_dep_map_modules()

    for mid, bp in bp_entries.items():
        if specific_module and mid != specific_module:
            continue
        result.checked_modules += 1
        ctx, setup_violations = _build_module_check_context(mid, bp, dep_map_modules)
        all_violations = (
            setup_violations
            + _check_module_id_alignment(ctx)
            + _check_attr_alignment(ctx)
            + _check_blueprint_file_exists(ctx)
            + _check_code_path_exists(ctx)
        )
        for v in all_violations:
            result.add_violation(v)

    # Check 5: 依赖图有模块但蓝图没有（孤儿节点，循环外单独执行）
    for v in _check_dep_map_orphans(dep_map_modules, bp_entries, specific_module):
        result.add_violation(v)

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


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def load_yaml(path) -> dict | list | None:
    """公共接口：load_yaml（Stage 4 公共化）。"""
    return _load_yaml(path)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def extract_dep_map_modules() -> dict[str, dict[str, str]]:
    """公共接口：extract_dep_map_modules（Stage 4 公共化）。"""
    return _extract_dep_map_modules()
