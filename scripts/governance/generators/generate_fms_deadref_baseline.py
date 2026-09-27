# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/generate_gate_registry.py | §
# [MODULE] scripts.governance.generators.generate_fms_deadref_baseline
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.read_side.fms_ref_extractor（共享提取器——与 FMS-HYGIENE 门机械同源，S1 簿硬约束）; zephyr.shared.io.file_utils (safe_write_text/content_sha256——热册 CAS 写)
# [CONSUMERS] docs/01_policies_and_standards/_registry/catalogs/fms_deadref_baseline.yaml（唯一产物）; zephyr.gov_enforcement.commit_gates.read_side.fms_hygiene_gate（基线消费方）
# [STARTUP] manual
# [INVARIANTS] 基线册唯一合法写者（宪法 §9.5 静态清单禁手工维护）；只读扫描零副作用（唯一写动作=基线册本尊，safe_write_text CAS）；棘轮 monotonic_shrink=新条目集 ⊆ 旧条目集否则 exit 1（净增长=基线被篡改或门失效，S1 §4.1 文件 5）；分类优先级机械可复算 E1(.tmp)→盘面在册(活，E4 自愈不收录)→A(模板)→B(_working 分量)→E3(目录/无扩展名)→C(唯一命中可修)→C2(唯一命中低置信)→D(真死)；C 类不进基线（B2 清偿批改写对象，非豁免面）；与总筹 deadref_missing_2498.csv 现场对账并出差异报告（提取器不同必然有差，差异全量打印留痕）；确定性输出（entries 按 ref 排序，同输入同输出）；first_seen 幂等继承
# [MODIFY-GUARD] CLI: [--check] [--csv PATH] [--baseline PATH]；exit 0=成功/1=棘轮违例或扫描失败
# [STABILITY] evolving
# [MATURITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 扫描/git 异常=报错 exit 1（生成器允许抛错，与 in-process 门 ERROR_CONTRACT 无关）；写盘必经 safe_write_text（热册 CAS，拒写异常上抛）
# [TESTS] tests/gov_enforcement/read_side/test_fms_hygiene_gate.py（提取器/分类判据经共享模块覆盖；生成器本体以实跑产册为准）
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
generate_fms_deadref_baseline.py — FMS 死引用棘轮基线生成器

全仓扫描 docs 树 md/yaml 的盘面路径引用 → 共享提取器取 token → git 跟踪集
存在性判定 → S1 分类口径归类 → 产出/校验棘轮基线册
``docs/01_policies_and_standards/_registry/catalogs/fms_deadref_baseline.yaml``。

棘轮语义（ratchet: monotonic_shrink）
-------------------------------------
基线记录 2026-09-27 存量死引用全集，**只许逐批缩小**：清偿批（B2）每落地一批，
再生成自动收缩；若新扫描条目集出现旧基线没有的 ref（净增长）→ exit 1——
净增长只可能意味着 FMS-HYGIENE 门失效（warn 期漏放未清偿）或基线被篡改。
盘面复活的 ref（E4 时点漂移类）再生成自动消失（S1 §4.2 E4 处置同款自愈）。

分类优先级（机械可复算，S1 簿 §2.2）
------------------------------------
``E1(.tmp) → 盘面在册(活→不收录) → A(模板形态) → B(_working 分量) →
E3(目录/无扩展名) → C(唯一命中可修) → C2(唯一命中低置信) → D(真死)``

- C 类**不进基线**：C=唯一可修（deadref_fix_map 批改写对象），进基线=给可修
  债发豁免，与清偿目标相反；基线 schema 类别枚举 A|B|C2|D|E1|E3|E4 同口径。
- E4 不复现：本生成器用**当日**跟踪集判定，晨间快照时点漂移自愈（在册=活=不收录）。

Usage::

    PYTHONPATH=src python scripts/governance/generators/generate_fms_deadref_baseline.py
    PYTHONPATH=src python scripts/governance/generators/generate_fms_deadref_baseline.py --check

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/r/read_side_fms_hygiene_gate.yaml
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

import yaml  # noqa: E402  — 第三方段先于 zephyr（first-party），脚本直调 sys.path 引导后导入

from zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate import (  # noqa: E402
    _DOC_REF_BROKEN_SKIP_DIRS,
    _is_in_skip_dir,
)
from zephyr.gov_enforcement.commit_gates.read_side.fms_ref_extractor import (  # noqa: E402
    extract_refs,
    is_cas_residue,
    is_ephemeral_target,
    is_template_form,
    normalize_ref,
)
from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc

DEFAULT_BASELINE = _REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/fms_deadref_baseline.yaml"
DEFAULT_CSV = _REPO_ROOT / "docs/_working/fms_overhaul/_data/deadref_missing_2498.csv"
BASELINE_DATE = "2026-09-27"
SCAN_EXTS = {".md", ".yaml"}
CATEGORY_ORDER = ("A", "B", "C2", "D", "E1", "E3", "E4")


def git_tracked_index() -> tuple[set[str], set[str], dict[str, list[str]]]:
    """git 跟踪集三元组：(文件集, 祖先目录集, basename→路径清单索引)。只读 git ls-files。"""
    proc = subprocess.run(  # noqa: S603,bare-subprocess  生成器只读 ls-files，一次性进程可接受
        ["git", "ls-files", "-z"], cwd=str(_REPO_ROOT), capture_output=True, check=True
    )
    files = {p for p in proc.stdout.decode("utf-8", errors="replace").split("\0") if p}
    dirs: set[str] = set()
    basename_index: dict[str, list[str]] = {}
    for f in files:
        parts = f.split("/")
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]))
        basename_index.setdefault(parts[-1], []).append(f)
    return files, dirs, basename_index


def scan_doc_refs() -> tuple[set[str], int]:
    """扫描 docs 树 md/yaml 引用 token（含未跟踪文件；referrer 作用域与门对齐）。

    referrer 跳过目录复用 FMS-HYGIENE 门同一 SSoT（trae_028 n16 skip_dirs_docs，
    doc_ref_broken_gate 单写者 import）——门不可达的 referrer（_working 草稿区等）
    产生的引用不在豁免面上，收录即漂移源：草稿随会话高频增删，会把棘轮
    "只减不增"打穿（2026-09-27 实测 62 条净增全部来自草稿区未跟踪件）。
    只读，零副作用。
    """
    refs: set[str] = set()
    file_count = 0
    docs_root = _REPO_ROOT / "docs"
    for path in sorted(docs_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCAN_EXTS:
            continue
        rel = path.relative_to(_REPO_ROOT).as_posix()
        if _is_in_skip_dir(rel, _DOC_REF_BROKEN_SKIP_DIRS):
            continue
        file_count += 1
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for hit in extract_refs(content):
            refs.add(hit.token)
    return refs, file_count


def classify_ref(
    token: str,
    tracked_files: set[str],
    tracked_dirs: set[str],
    basename_index: dict[str, list[str]],
) -> str | None:
    """S1 分类优先级：E1 → 盘面在册(活→None) → A → B → E3 → C → C2 → D。

    Returns:
        基线类别（A|B|C2|D|E1|E3）；活引用返回 None（不收录；E4 自愈不复现）。
        C 类同样不进基线（清偿批改写对象）——本函数仍返回 "C" 供对账统计，
        由调用方决定收录与否。
    """
    t = normalize_ref(token)
    if not t:
        return None
    if is_cas_residue(t):
        return "E1"  # 优先级最高：CAS 残渣引用（即便目标碰巧在册也按残渣治理）
    probe = t.rstrip("/")
    if probe in tracked_files or probe in tracked_dirs:
        return None  # 盘面在册=活引用（E4 时点漂移自愈，不进基线）
    if is_template_form(t):
        return "A"
    if is_ephemeral_target(t):
        return "B"
    last = probe.split("/")[-1]
    if t.endswith("/") or "." not in last:
        return "E3"
    cands = basename_index.get(last, [])
    if len(cands) == 1:
        hit = cands[0]
        ref_ext = last.rsplit(".", 1)[-1].lower()
        hit_ext = hit.rsplit(".", 1)[-1].lower() if "." in hit else ""
        if is_ephemeral_target(hit) or hit_ext != ref_ext:
            return "C2"  # 唯一命中但目标落临时区/扩展名错配=低置信
        return "C"  # 唯一命中可修（不进基线，B2 清偿批对象）
    return "D"


def load_csv_refs(csv_path: Path) -> set[str]:
    """加载总筹实测死引用清单（每行一个被引路径，无表头）。缺失返回空集（对账跳过）。"""
    if not csv_path.exists():
        return set()
    out: set[str] = set()
    for line in csv_path.read_text(encoding="utf-8", errors="replace").splitlines():
        ref = normalize_ref(line.strip())
        if ref:
            out.add(ref)
    return out


def load_existing_entries(baseline_path: Path) -> dict[str, dict]:
    """读旧基线条目（ref→entry）；缺失/损坏返回空 dict（首跑/修复路径）。"""
    if not baseline_path.exists():
        return {}
    try:
        data = yaml.safe_load(baseline_path.read_text(encoding="utf-8")) or {}
        return {str(e["ref"]): e for e in data.get("entries") or [] if isinstance(e, dict) and e.get("ref")}
    except Exception as e:  # noqa: BLE001 — 旧册损坏按首跑处理（棘轮对照面缺失显性告警）
        print(f"WARN: 旧基线册解析失败（{type(e).__name__}: {e}）——棘轮对照面为空", file=sys.stderr)
        return {}


def build_baseline_doc(
    entries: list[dict],
    total_scanned_files: int,
    total_refs: int,
    recon: dict[str, int],
) -> dict:
    """组装基线册 dict（safe_dump sort_keys=False 保持字段序；计数一律字段不写散文）。"""
    cat_counts: dict[str, int] = {}
    for e in entries:
        cat_counts[e["category"]] = cat_counts.get(e["category"], 0) + 1
    now_iso = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "module_id": "REG-FMS-DEADREF-BASELINE",
        "doc_type": "register",
        "ttl": "permanent",
        "title": "FMS 死引用棘轮基线（生成物，禁手改）",
        "status": "active",
        "generated_at": now_iso,
        "generated_by": "scripts/governance/generators/generate_fms_deadref_baseline.py",
        "maintenance": "auto",
        "source": "docs 树 md/yaml 全量引用扫描（git 跟踪集存在性判定）",
        "ratchet": "monotonic_shrink",
        "baseline_date": BASELINE_DATE,
        "total_dead": len(entries),
        "category_counts": {k: cat_counts.get(k, 0) for k in CATEGORY_ORDER},
        "scan_stats": {"referrer_files": total_scanned_files, "unique_refs": total_refs},
        "csv_reconciliation": recon,
        "entries": entries,
    }


def _classify_all(
    refs: set[str],
    tracked_files: set[str],
    tracked_dirs: set[str],
    basename_index: dict[str, list[str]],
) -> dict[str, str]:
    """全量分类（活引用 classify_ref 返回 None→不收录）。"""
    classified: dict[str, str] = {}
    for token in refs:
        cat = classify_ref(token, tracked_files, tracked_dirs, basename_index)
        if cat:
            classified[token] = cat
    return classified


def _reconcile_csv(classified: dict[str, str], csv_path: Path) -> tuple[set[str], dict[str, int]]:
    """与总筹 CSV 现场对账（提取器不同必然有差，差异全量口径留痕）；返回 (csv_refs, recon)。"""
    csv_refs = load_csv_refs(csv_path)
    dead_all = set(classified)  # 含 C（对账口径=全部死引用）
    recon = {
        "csv_total": len(csv_refs),
        "scan_dead_total": len(dead_all),
        "in_both": len(csv_refs & dead_all),
        "csv_only": len(csv_refs - dead_all),
        "scan_only": len(dead_all - csv_refs),
    }
    return csv_refs, recon


def _build_entries(classified: dict[str, str], existing: dict[str, dict]) -> list[dict]:
    """组装收录条目（C 类不进基线；棘轮 first_seen 幂等继承）。"""
    included_refs = [r for r, c in classified.items() if c != "C"]
    entries: list[dict] = []
    for ref in sorted(included_refs):
        old = existing.get(ref)
        entries.append(
            {
                "ref": ref,
                "category": classified[ref],
                "first_seen": str(old.get("first_seen", BASELINE_DATE)) if old else BASELINE_DATE,
            }
        )
    return entries


def _check_ratchet(existing: dict[str, dict], entries: list[dict], classified: dict[str, str]) -> bool:
    """棘轮断言：新条目集 ⊆ 旧条目集；净增长（门失效/被篡改）打印违例并返回 True。"""
    old_refs = set(existing)
    new_refs = {e["ref"] for e in entries} - old_refs
    if existing and new_refs:
        print(
            f"FAIL: 棘轮违例——新基线含 {len(new_refs)} 条旧基线没有的条目（净增长=门失效或基线被篡改）：",
            file=sys.stderr,
        )
        for r in sorted(new_refs)[:20]:
            print(f"  + {r} ({classified.get(r, '?')})", file=sys.stderr)
        return True
    return False


@dataclass
class _ScanReport:
    """扫描留痕报告数据包（参数对象——收敛 _print_scan_report 形参个数，行为零变化）。"""

    file_count: int
    refs: set[str]
    dead_all: set[str]
    csv_refs: set[str]
    recon: dict[str, int]
    doc: dict
    classified: dict[str, str]
    existing: dict[str, dict]
    entries: list[dict]


def _print_scan_report(report: _ScanReport) -> None:
    """stdout 留痕报告（扫描计数/对账/分类抽样/棘轮收缩）。"""
    print(f"扫描 referrer 文件: {report.file_count}（docs 树 md/yaml，含未跟踪）")
    refs_n = len(report.refs)
    print(f"唯一引用 token: {refs_n}；死引用（含 C）: {len(report.dead_all)}；基线收录（剔 C）: {len(report.entries)}")
    print("分类计数: " + ", ".join(f"{k}={report.doc['category_counts'][k]}" for k in CATEGORY_ORDER))
    recon = report.recon
    print(
        f"CSV 对账: 双侧命中 {recon['in_both']} / CSV 独有 {recon['csv_only']} / 扫描独有 {recon['scan_only']}"
        f"（CSV 总 {recon['csv_total']}，扫描死引用总 {recon['scan_dead_total']}）"
    )
    scan_only_sample = sorted(report.dead_all - report.csv_refs)[:10]
    if scan_only_sample:
        print("扫描独有样例（提取器口径差，全量见基线册）:")
        for r in scan_only_sample:
            print(f"  - {r} ({report.classified.get(r, '?')})")
    print("分类抽样（每类至多 3 条，人工核验窗口）:")
    for cat in CATEGORY_ORDER:
        sample = sorted(r for r, c in report.classified.items() if c == cat)[:3]
        if sample:
            print(f"  [{cat}] " + " | ".join(sample))
    if report.existing:
        old_n = len(report.existing)
        print(f"棘轮: 旧 {old_n} 条 → 新 {len(report.entries)} 条（收缩 {old_n - len(report.entries)}，净增 0 合规）")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FMS 死引用棘轮基线生成器（只读扫描+CAS 产册）")
    parser.add_argument("--check", action="store_true", help="只校验不写盘（棘轮+对账报告）")
    parser.add_argument(
        "--csv", type=str, default=str(DEFAULT_CSV), help="总筹对账 CSV（默认 deadref_missing_2498.csv）"
    )
    parser.add_argument("--baseline", type=str, default=str(DEFAULT_BASELINE), help="基线册输出路径")
    args = parser.parse_args(argv)
    baseline_path = Path(args.baseline)
    csv_path = Path(args.csv)

    # 1. 只读扫描 + 分类
    refs, file_count = scan_doc_refs()
    tracked_files, tracked_dirs, basename_index = git_tracked_index()
    classified = _classify_all(refs, tracked_files, tracked_dirs, basename_index)

    # 2. 与总筹 CSV 现场对账（提取器不同必然有差，差异全量口径打印留痕）
    csv_refs, recon = _reconcile_csv(classified, csv_path)

    # 3. 组装收录条目（C 类不进基线；棘轮 first_seen 幂等继承）
    existing = load_existing_entries(baseline_path)
    entries = _build_entries(classified, existing)

    # 4. 棘轮断言：新条目集 ⊆ 旧条目集（净增长=基线被篡改或门失效 → exit 1）
    if _check_ratchet(existing, entries, classified):
        return 1

    doc = build_baseline_doc(entries, file_count, len(refs), recon)
    content = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=4096)

    # 5. 报告（stdout 留痕）
    _print_scan_report(
        _ScanReport(
            file_count=file_count,
            refs=refs,
            dead_all=set(classified),
            csv_refs=csv_refs,
            recon=recon,
            doc=doc,
            classified=classified,
            existing=existing,
            entries=entries,
        )
    )

    if args.check:
        print("CHECK 模式：不写盘。")
        return 0

    # 6. CAS 写盘（catalogs 热册：存在即带 base hash，safe_write_text 拒并发覆盖）
    expected = content_sha256(baseline_path.read_text(encoding="utf-8")) if baseline_path.exists() else None
    result = safe_write_text(baseline_path, content, expected_base_sha256=expected, repo_root=str(_REPO_ROOT))
    print(f"WROTE: {result.path}（written={result.written}, after_sha256={result.after_sha256[:12]}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
