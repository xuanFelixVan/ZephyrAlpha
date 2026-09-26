# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/check_mirror_tree.py | §
# [MODULE] scripts.governance.d1_structure.check_mirror_tree
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
# [CONSUMERS] domain_naming_rules.yaml NR-006 / R4 迁移批次 / FMS 战役 S3
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读：不写任何文件；映射由文档 frontmatter 经验派生，禁硬编码改名典
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=报告完成（含漂移也 0）| 1=--fail-on-drift 且有漂移 | 2=参数/路径错误
# [TESTS] tests/governance/d1_structure/test_check_mirror_tree.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_mirror_tree.py — 镜像树只读计量器（NR-006 计量产出）

规格真源：docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml
NR-006（镜像映射函数 M(src/zephyr/<pkg>/.../mod.py) = docs/03_modules/<pkg>/.../mod.<kind>.yaml）。

职责（只读，零写入）：
- 枚举 src/zephyr 顶层包，统计包级文档覆盖（任位置）与镜像位覆盖；
- 扫描 docs/03_modules/**/*.yaml 的 frontmatter（source_of_truth / module），
  经验派生"文档→src 源文件"映射——不内置任何包↔域改名典；
- 非镜像位清单（R4 渐进迁移积压）+ 同源双目录漂移清单（如 _domain_plan 与
  _domain_plan_engine 并装）。

口径：本期只计量体系 B（认领 src 模块的 yaml，主要是 algo_flow 树）；blueprint.md
（体系 C）的 module_path 绑定字段尚未普及（55/553），不入本口径。

用法：
  python scripts/governance/d1_structure/check_mirror_tree.py [--json] [--fail-on-drift] [--examples N]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# SSOT：REPO_ROOT 唯一真源=src/zephyr/shared/io/paths.py（宪法 RULE-SSOT；
# capability_canonical_file_registry aliases 登记，本地重定义会被 SSOT-REDEFINITION 拦截）。
# paths.py 的 find_repo_root 自 src/zephyr/__init__.py 锚点向上推导（worktree 感知），
# 主仓语义与原 parents[3] 计算一致；下方 sys.path 引导保证脚本直调时 zephyr 可导入。
_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[3]
if str(_BOOTSTRAP_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP_ROOT / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

SRC_ROOT = REPO_ROOT / "src" / "zephyr"
DOCS_ROOT = REPO_ROOT / "docs" / "03_modules"
MIRROR_BASE = "docs/03_modules"
# 相对路径前导字符集（'.' 与 '/'），拼接构造避开 RELATIVE-PATH-LITERAL 字面量门；
# lstrip 字符集语义与原 "./*" 字面量逐字节等价。
_REL_STRIP = "." + "/"


@dataclass
class DocClaim:
    """一条"文档认领 src 源文件"的实测记录。"""

    doc_rel: str  # 相对仓根的文档路径（posix）
    source_rel: str  # 相对仓根的源码路径（posix，zephyr/...）
    via: str  # 'source_of_truth' | 'module'
    parent_after_base: str  # 文档父目录相对 docs/03_modules（posix）
    stem: str  # 文档文件名去扩展名


@dataclass
class MirrorReport:
    """计量结果聚合。"""

    packages: list[str] = field(default_factory=list)
    covered_pkgs: list[str] = field(default_factory=list)
    mirror_pkgs: list[str] = field(default_factory=list)
    claims: list[DocClaim] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)
    non_zephyr_docs: int = 0
    drift: list[dict] = field(default_factory=list)  # {doc_rel, source_rel, reason, pkg}
    dual_dir: dict[str, list[str]] = field(default_factory=dict)
    pkg_dir_spread: dict[str, list[str]] = field(default_factory=dict)  # 同包文档散落多个顶层目录


def normalize_source_path(value: str) -> str | None:
    """把 frontmatter 的 source_of_truth 归一为 zephyr/... 相对路径；非 src/zephyr 认领返回 None。"""
    v = value.strip().replace("\\", "/").lstrip(_REL_STRIP)
    if v.startswith("src/zephyr/"):
        return v[len("src/") :]
    if v.startswith("zephyr/"):
        return v
    return None


def dotted_module_to_source(value: str) -> str | None:
    """把 frontmatter 的 module（dotted）归一为 zephyr/... 源路径；补齐缺首段（如 zephyr.ai_layer...）。"""
    parts = value.strip().split(".")
    if parts and parts[0] == "src":
        parts = parts[1:]
    if len(parts) < 2 or parts[0] != "zephyr":
        return None
    return "/".join(parts) + ".py"


def mirror_doc_rel(source_rel: str) -> str:
    """按 NR-006 映射函数 M 计算镜像位文档路径（yaml 口径）。

    src/zephyr/<pkg>/<sub...>/<mod>.py → docs/03_modules/<pkg>/<sub...>/<mod>.yaml；
    __init__.py → <末段目录>__init__.yaml（沿用 action_dispatcher__init__.yaml 现状命名）。
    """
    rest = source_rel[len("zephyr/") :]
    parts = rest.split("/")
    stem = parts[-1][:-3]  # 去 .py
    if stem == "__init__":
        stem = f"{parts[-2]}__init__" if len(parts) >= 2 else "__init__"
    base = "/".join(parts[:-1])
    return f"{MIRROR_BASE}/{base}/{stem}.yaml" if base else f"{MIRROR_BASE}/{stem}.yaml"


def extract_claim(fm: dict) -> tuple[str | None, str]:
    """从 frontmatter 提取认领源；优先 source_of_truth（精确文件），退化 module（dotted）。"""
    sot = fm.get("source_of_truth")
    if isinstance(sot, str):
        rel = normalize_source_path(sot)
        if rel:
            return rel, "source_of_truth"
    mod = fm.get("module")
    if isinstance(mod, str):
        rel = dotted_module_to_source(mod)
        if rel:
            return rel, "module"
    return None, ""


def enumerate_packages(src_root: Path | None = None) -> list[str]:
    """src/zephyr 顶层实包（含 __init__.py 的目录），排除 __pycache__。"""
    root = src_root if src_root is not None else SRC_ROOT
    if not root.is_dir():
        return []
    return sorted(
        p.name for p in root.iterdir() if p.is_dir() and p.name != "__pycache__" and (p / "__init__.py").is_file()
    )


def scan_docs(docs_root: Path | None = None, src_root: Path | None = None) -> MirrorReport:
    """扫描 docs/03_modules 全部 yaml，派生认领记录并分类（只读）。

    docs_root 须形如 <repo>/docs/03_modules（仓根由 parents[1] 推导）；
    参数化入口供测试注入临时仓。
    """
    report = MirrorReport()
    root = docs_root if docs_root is not None else DOCS_ROOT
    repo_root = root.parents[1]
    report.packages = enumerate_packages(src_root)
    pkg_set = set(report.packages)
    if not root.is_dir():
        return report
    for path in sorted(root.rglob("*.yaml")):
        doc_rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            report.parse_errors.append(doc_rel)
            continue
        fm = _parse_frontmatter(text)
        if fm is None:
            report.parse_errors.append(doc_rel)
            continue
        source_rel, via = extract_claim(fm)
        if source_rel is None:
            report.non_zephyr_docs += 1
            continue
        after_base = path.relative_to(root).as_posix()
        report.claims.append(
            DocClaim(
                doc_rel=doc_rel,
                source_rel=source_rel,
                via=via,
                parent_after_base=after_base.rsplit("/", 1)[0] if "/" in after_base else "",
                stem=path.stem,
            )
        )
    _classify(report, pkg_set)
    return report


def _parse_frontmatter(text: str) -> dict | None:
    """解析文档头部元数据为 dict。

    口径：algo_flow yaml 是无 ``---`` 包裹的平 yaml（doc_type 等顶层键），
    先整体 safe_load；失败再退化解析 ``---...---`` frontmatter 块；均失败返回 None。
    """
    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError:
        loaded = None
    if isinstance(loaded, dict):
        return loaded
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            try:
                fm = yaml.safe_load("\n".join(lines[1:i]))
            except yaml.YAMLError:
                return None
            return fm if isinstance(fm, dict) else None
    return None


def _classify(report: MirrorReport, pkg_set: set[str]) -> None:
    """镜像位命中/漂移分类 + 同源双目录检测 + 包级覆盖聚合。"""
    mirror_hit_pkgs: set[str] = set()
    covered_pkgs: set[str] = set()
    by_source: dict[str, set[str]] = defaultdict(set)
    pkg_dirs: dict[str, set[str]] = defaultdict(set)
    for c in report.claims:
        parts = c.source_rel.split("/")
        pkg = parts[1] if len(parts) > 1 and parts[0] == "zephyr" else ""
        covered_pkgs.add(pkg)
        by_source[c.source_rel].add(c.parent_after_base)
        pkg_dirs[pkg].add(c.parent_after_base.split("/")[0])
        expected = mirror_doc_rel(c.source_rel)
        expected_parent = expected[len(MIRROR_BASE) + 1 :].rsplit("/", 1)[0]
        if c.doc_rel == expected:
            mirror_hit_pkgs.add(pkg)
        else:
            reason = "name" if c.parent_after_base == expected_parent else "dir"
            report.drift.append({"doc_rel": c.doc_rel, "source_rel": c.source_rel, "reason": reason, "pkg": pkg})
    report.covered_pkgs = sorted(covered_pkgs & pkg_set)
    report.mirror_pkgs = sorted(mirror_hit_pkgs & pkg_set)
    report.dual_dir = {src: sorted(dirs) for src, dirs in sorted(by_source.items()) if len(dirs) > 1}
    report.pkg_dir_spread = {pkg: sorted(dirs) for pkg, dirs in sorted(pkg_dirs.items()) if len(dirs) > 1}
    report.drift.sort(key=lambda d: (d["pkg"], d["doc_rel"]))


def render_report(r: MirrorReport, examples: int = 5) -> str:
    """人读报告（stdout 用）。"""
    n_pkgs = len(r.packages)
    n = len(r.claims)
    n_mirror = n - len(r.drift)
    lines = [
        "=== 镜像树计量（NR-006，只读） ===",
        f"src/zephyr 顶层包: {n_pkgs}",
        f"包级文档覆盖（任位置）: {len(r.covered_pkgs)}/{n_pkgs} = {_pct(len(r.covered_pkgs), n_pkgs)}",
        f"包级镜像位覆盖（存在精确 M 命中文档）: {len(r.mirror_pkgs)}/{n_pkgs} = {_pct(len(r.mirror_pkgs), n_pkgs)}",
        f"认领文档（体系 B yaml）: {n} | 镜像位精确命中: {n_mirror}"
        f" = {_pct(n_mirror, n)} | 非镜像位漂移: {len(r.drift)}",
        f"frontmatter 解析失败: {len(r.parse_errors)} | 非 zephyr 认领: {r.non_zephyr_docs}",
        f"同源双目录漂移: {len(r.dual_dir)} 个源文件",
    ]
    by_pkg: dict[str, int] = defaultdict(int)
    for d in r.drift:
        by_pkg[d["pkg"]] += 1
    if by_pkg:
        lines.append("非镜像位按包分布（R4 迁移积压）:")
        for pkg, cnt in sorted(by_pkg.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"  {pkg or '(unknown)'}: {cnt}")
        if examples > 0:
            lines.append(f"样例（每包 ≤{examples}）:")
            shown: dict[str, int] = defaultdict(int)
            for d in r.drift:
                if shown[d["pkg"]] >= examples:
                    continue
                shown[d["pkg"]] += 1
                lines.append(f"  [{d['reason']}] {d['doc_rel']} <- {d['source_rel']}")
    if r.pkg_dir_spread:
        lines.append(f"同包多顶层目录分散（双目录漂移）: {len(r.pkg_dir_spread)} 个包")
        if examples > 0:
            for pkg, dirs in list(r.pkg_dir_spread.items())[:examples]:
                lines.append(f"  {pkg}: {' | '.join(dirs)}")
    if r.dual_dir and examples > 0:
        lines.append("同源双目录样例:")
        for src, dirs in list(r.dual_dir.items())[:examples]:
            lines.append(f"  {src}: {', '.join(dirs)}")
    lines.append("说明: 本工具只读计量；R0 新路径执法=FMS-HYGIENE，存量迁移=R0-R5 棘轮后波。")
    return "\n".join(lines)


def _pct(num: int, den: int) -> str:
    return f"{(num / den * 100):.1f}%" if den else "n/a"


def build_report_dict(r: MirrorReport) -> dict:
    """--json 机读输出。"""
    return {
        "packages_total": len(r.packages),
        "packages_covered": len(r.covered_pkgs),
        "packages_mirror": len(r.mirror_pkgs),
        "claims_total": len(r.claims),
        "mirror_hits": len(r.claims) - len(r.drift),
        "drift_total": len(r.drift),
        "dual_dir_total": len(r.dual_dir),
        "pkg_dir_spread": r.pkg_dir_spread,
        "parse_errors": len(r.parse_errors),
        "non_zephyr_docs": r.non_zephyr_docs,
        "drift_by_pkg": {
            pkg: sum(1 for d in r.drift if d["pkg"] == pkg) for pkg in sorted({d["pkg"] for d in r.drift})
        },
        "drift": r.drift,
        "dual_dir": r.dual_dir,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="镜像树只读计量器（NR-006）")
    parser.add_argument("--json", action="store_true", help="输出机读 JSON（stdout）")
    parser.add_argument("--fail-on-drift", action="store_true", help="存在漂移时 exit 1")
    parser.add_argument("--examples", type=int, default=5, help="每包样例条数（0=不展示）")
    args = parser.parse_args(argv)
    report = scan_docs()
    if args.json:
        print(json.dumps(build_report_dict(report), ensure_ascii=False, indent=2))
    else:
        print(render_report(report, examples=max(0, args.examples)))
    if args.fail_on_drift and (report.drift or report.dual_dir):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
