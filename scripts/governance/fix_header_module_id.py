# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""fix_header_module_id.py — 批量修复文件头 module_id 与 depgraph 一致

三层安全网:
  1. Pre-flight:  git 工作区干净检查 + depgraph ID 格式预检 + dry-run 报告
  2. Per-file:    原子写入(.tmp→rename) + 立即重读验证 + 单文件回滚
  3. Post-batch:  全量重扫 + JSON 报告 + before/after 对比

Usage::
  # Dry-run (只分析, 不修改)
  py -3.12 scripts/governance/fix_header_module_id.py --dry-run

  # 实际执行 (需要 --confirm)
  py -3.12 scripts/governance/fix_header_module_id.py --confirm

  # 按域过滤 + 限制数量 (测试用)
  py -3.12 scripts/governance/fix_header_module_id.py --confirm --domain D_RISK --limit 20

  # 使用已有 JSON (跳过数据库查询)
  py -3.12 scripts/governance/fix_header_module_id.py --dry-run --depgraph-json .runtime/tmp/depgraph_paths.json
"""

from __future__ import annotations

__manifest__ = """
args: []
description: fix_header_module_id.py — 批量修复文件头 module_id 与 depgraph 一致
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# 治本（2026-08-03）：module_id 格式校验改用权威真源 is_valid_module_id（裁定#208 三轨制）。
# 旧 validate_module_id_format 仅认 MOD- 前缀 → 误判 27 个 SH-* 跨域共享轨为「不合规」(假阳性)，
# 同时漏报 13 个以 MOD- 开头但格式非法的 ID（如 MOD-H1_REDIS_HOT，假阴性）。
# 权威真源：scripts/governance/d3_metadata/validate_module_id_naming.py
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
from d3_metadata.validate_module_id_naming import is_valid_module_id  # noqa: E402

# ─── Constants ────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parents[2]
EXTRACT_DEPGRAPH = BASE_DIR / "scripts" / "governance" / "extract_depgraph.py"
DEFAULT_REPORT = BASE_DIR / ".runtime" / "tmp" / "header_fix_report.json"
DEFAULT_DEPGRAPH_JSON = BASE_DIR / ".runtime" / "tmp" / "depgraph_paths.json"
PRODUCTION_STATUS = {"stable", "generated", "production"}
SCAN_LINES = 30

RE_A_MODULE = re.compile(r"^(#\s*\[A_module\]\s*module_id=)(\S+?)(\s*\|.*)?$")
RE_BLUEPRINT = re.compile(r"^(#\s*\[BLUEPRINT\]\s*)(\S+?)(\s*\|.*)?$")
RE_STABILITY = re.compile(r"^#\s*\[STABILITY\]\s*(\S+)", re.IGNORECASE)
RE_SAFETY = re.compile(r"^#\s*\[SAFETY\]\s*(\S+)", re.IGNORECASE)
RE_AI_AUTONOMY = re.compile(r"^#\s*\[AI_AUTONOMY\]\s*(\S+)", re.IGNORECASE)
RE_TTL = re.compile(r"^#\s*\[TTL\]", re.IGNORECASE)

# ─── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class FileResult:
    """单个文件的分析/修复结果。"""

    path: str
    depgraph_module_id: str
    build_status: str
    action: str  # FIX, ADD, SKIP, NO_CHANGE, ROLLBACK
    old_a_module_id: str | None = None
    new_a_module_id: str | None = None
    old_blueprint_id: str | None = None
    new_blueprint_id: str | None = None
    status: str = "PENDING"  # SUCCESS, VERIFIED, FAILED, ROLLED_BACK, SKIPPED
    error: str | None = None
    timestamp: str = ""


@dataclass
class BatchReport:
    """整批修复的报告。"""

    run_id: str
    started_at: str
    finished_at: str = ""
    mode: str = "dry-run"
    summary: dict = field(
        default_factory=lambda: {
            "total": 0,
            "fixed": 0,
            "added": 0,
            "no_change": 0,
            "skipped": 0,
            "rolled_back": 0,
            "verification_failed": 0,
        }
    )
    results: list[FileResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    before_stats: dict = field(default_factory=dict)
    after_stats: dict = field(default_factory=dict)


# ─── Helper Functions ─────────────────────────────────────────────────────────


def read_file(path: Path) -> tuple[str, str, str]:
    """读取文件, 返回 (content, encoding, newline)。自动检测 BOM 和行尾符。"""
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"
    text = raw.decode(encoding, errors="replace")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    return text, encoding, newline


def atomic_write(path: Path, content: str, encoding: str, newline: str) -> None:
    """原子写入: 先写 .tmp 文件, 再 os.replace rename。"""
    dir_ = path.parent
    fd, tmp = tempfile.mkstemp(dir=str(dir_), suffix=".tmp", prefix=".fix_")
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline=newline) as f:
            f.write(content)
        os.replace(tmp, str(path))
    except Exception:  # noqa: BLE001
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def extract_module_ids(content: str) -> tuple[str | None, str | None]:
    """从文件内容提取 [A_module] 和 [BLUEPRINT] 的 module_id。"""
    a_id = None
    bp_id = None
    for line in content.splitlines()[:SCAN_LINES]:
        if a_id is None:
            m = RE_A_MODULE.match(line)
            if m:
                a_id = m.group(2).strip()
                continue
        if bp_id is None:
            m = RE_BLUEPRINT.match(line)
            if m:
                bp_id = m.group(2).strip()
                continue
    return a_id, bp_id


def validate_module_id_format(mid: str) -> bool:
    """检查 module_id 是否符合裁定#208 双轨制（权威真源 is_valid_module_id）。

    三轨制（R2 治本修订后）：
      - layer-master 轨: MOD-{LAYER}-{SEQ}（如 MOD-INF-005）
      - 派生轨:        MOD-{DOMAIN_FRAGMENT}[-NNN]（如 MOD-SHARED-002）
      - 跨域共享轨:    SH-{ABBR}-{NNN}（如 SH-DB-001）

    旧实现仅认 MOD- 前缀，产生假阳性（SH-* 被误判不合规）与假阴性
    （MOD-H1_REDIS_HOT 等漏网）。现统一委托权威校验器。
    """
    if not mid:
        return False
    ok, _ = is_valid_module_id(mid)
    return ok


def build_a_module_line(module_id: str, content: str) -> str:
    """构建 [A_module] 行, 从现有 header 提取 stability/safety/ai_autonomy。"""
    stability = "evolving"
    safety = "L"
    ai_autonomy = "ai_modifiable"
    for line in content.splitlines()[:SCAN_LINES]:
        m = RE_STABILITY.match(line)
        if m:
            stability = m.group(1)
            continue
        m = RE_SAFETY.match(line)
        if m:
            safety = m.group(1)
            continue
        m = RE_AI_AUTONOMY.match(line)
        if m:
            ai_autonomy = m.group(1)
    return (
        f"# [A_module] module_id={module_id}"
        f" | layer=module | stability={stability}"
        f" | safety={safety} | ai_autonomy={ai_autonomy}"
    )


def apply_fix(content: str, depgraph_mid: str) -> tuple[str, bool, bool, bool]:
    """对文件内容应用修复。

    Returns:
        (new_content, a_module_fixed, blueprint_fixed, a_module_added)
    """
    lines = content.splitlines(keepends=True)
    a_fixed = False
    b_fixed = False
    a_exists = False

    for i, line in enumerate(lines[:SCAN_LINES]):
        stripped = line.rstrip("\r\n")
        m = RE_A_MODULE.match(stripped)
        if m:
            a_exists = True
            if m.group(2).strip() != depgraph_mid:
                ending = line[len(stripped) :]
                lines[i] = m.group(1) + depgraph_mid + (m.group(3) or "") + ending
                a_fixed = True
            continue
        m = RE_BLUEPRINT.match(stripped)
        if m:
            if m.group(2).strip() != depgraph_mid:
                ending = line[len(stripped) :]
                lines[i] = m.group(1) + depgraph_mid + (m.group(3) or "") + ending
                b_fixed = True
            continue

    a_added = False
    if not a_exists:
        new_line = build_a_module_line(depgraph_mid, content)
        first_line = lines[0] if lines else ""
        ending = "\r\n" if first_line.endswith("\r\n") else "\n"
        insert_at = None
        for i, line in enumerate(lines[:SCAN_LINES]):
            if RE_TTL.match(line.rstrip("\r\n")):
                insert_at = i
                break
        if insert_at is None:
            for i, line in enumerate(lines[:SCAN_LINES]):
                if not line.startswith("#"):
                    insert_at = i
                    break
        if insert_at is not None:
            lines.insert(insert_at, new_line + ending)
            a_added = True

    return "".join(lines), a_fixed, b_fixed, a_added


def verify_fix(path: Path, expected_mid: str) -> tuple[bool, str | None]:
    """写入后重新读取文件, 验证 [A_module] module_id 是否正确。"""
    try:
        content, _, _ = read_file(path)
        a_id, _ = extract_module_ids(content)
        if a_id is None:
            return False, "[A_module] 行不存在"
        if a_id != expected_mid:
            return False, f"[A_module] {a_id} != {expected_mid}"
        return True, None
    except Exception as e:  # noqa: BLE001
        return False, f"验证读取失败: {e}"


# ─── Core: Per-file Fix ──────────────────────────────────────────────────────


def fix_file(path: Path, depgraph_mid: str, build_status: str) -> FileResult:
    """对单个文件执行 dry-run 分析 + (可选) 修复 + 验证 + 回滚。"""
    rel_path = str(path.relative_to(BASE_DIR)).replace("\\", "/")
    result = FileResult(
        path=rel_path,
        depgraph_module_id=depgraph_mid,
        build_status=build_status,
        action="NO_CHANGE",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
    )

    # 边界 1: 路径含 YAML anchor
    if "#" in rel_path:
        result.action = "SKIP"
        result.status = "SKIPPED"
        result.error = "路径含 YAML anchor"
        return result

    # 边界 2: 文件不存在
    if not path.is_file():
        result.action = "SKIP"
        result.status = "SKIPPED"
        result.error = "文件不存在"
        return result

    # 边界 3: depgraph module_id 格式不合规
    if not validate_module_id_format(depgraph_mid):
        result.action = "SKIP"
        result.status = "SKIPPED"
        result.error = f"depgraph module_id 格式不合规: {depgraph_mid}"
        return result

    # 读取文件
    try:
        content, encoding, newline = read_file(path)
    except Exception as e:  # noqa: BLE001
        result.action = "SKIP"
        result.status = "SKIPPED"
        result.error = f"读取失败: {e}"
        return result

    # 分析当前状态
    old_a_id, old_bp_id = extract_module_ids(content)
    result.old_a_module_id = old_a_id
    result.old_blueprint_id = old_bp_id

    needs_fix = False
    if old_a_id is None:
        result.action = "ADD"
        needs_fix = True
    elif old_a_id != depgraph_mid:
        result.action = "FIX"
        needs_fix = True
    if old_bp_id is not None and old_bp_id != depgraph_mid:
        result.action = "FIX" if result.action == "NO_CHANGE" else result.action
        needs_fix = True

    if not needs_fix:
        result.status = "SKIPPED"
        return result

    # === 修复阶段 ===
    new_content, a_fixed, b_fixed, a_added = apply_fix(content, depgraph_mid)
    result.new_a_module_id = depgraph_mid
    result.new_blueprint_id = depgraph_mid if b_fixed else old_bp_id

    # 原子写入
    try:
        atomic_write(path, new_content, encoding, newline)
    except Exception as e:  # noqa: BLE001
        result.status = "FAILED"
        result.action = "ROLLBACK"
        result.error = f"写入失败: {e}"
        return result

    # === 验证阶段 ===
    verified, verify_error = verify_fix(path, depgraph_mid)
    if verified:
        result.status = "VERIFIED"
        return result

    # === 回滚阶段 ===
    try:
        atomic_write(path, content, encoding, newline)
        result.status = "ROLLED_BACK"
        result.action = "ROLLBACK"
        result.error = f"验证失败已回滚: {verify_error}"
    except Exception as e:  # noqa: BLE001
        result.status = "FAILED"
        result.error = f"验证失败({verify_error}) 且回滚失败: {e}"

    return result


# ─── Depgraph Loading ─────────────────────────────────────────────────────────


def load_depgraph(json_path: Path | None = None) -> dict:
    """加载 depgraph 路径数据。优先使用已有 JSON, 否则调用 extract_depgraph.py。"""
    if json_path and json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))

    output = DEFAULT_DEPGRAPH_JSON
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(EXTRACT_DEPGRAPH), "--paths", "--output", str(output)]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BASE_DIR))
    if proc.returncode != 0:
        print(f"ERROR: extract_depgraph.py 失败:\n{proc.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(output.read_text(encoding="utf-8"))


def check_git_clean() -> bool:
    """检查 git 工作区是否干净 (有未提交改动则返回 False)。"""
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    return proc.returncode == 0 and proc.stdout.strip() == ""


# ─── Post-batch Re-scan ──────────────────────────────────────────────────────


def full_rescan(depgraph: dict) -> dict:
    """全量重扫, 返回一致性统计。"""
    consistent = 0
    inconsistent = 0
    missing = 0
    for info in depgraph.values():
        if not isinstance(info, dict):
            continue
        for f in info.get("files", []):
            if f.get("build_status") not in PRODUCTION_STATUS:
                continue
            path_str = f.get("path", "")
            if "#" in path_str:
                continue
            path = BASE_DIR / path_str.replace("/", "\\")
            if not path.is_file():
                continue
            try:
                content, _, _ = read_file(path)
                a_id, _ = extract_module_ids(content)
                if a_id is None:
                    missing += 1
                elif a_id == f.get("module_id"):
                    consistent += 1
                else:
                    inconsistent += 1
            except Exception:  # noqa: BLE001
                pass
    return {"consistent": consistent, "inconsistent": inconsistent, "missing": missing}


# ─── Console Output ──────────────────────────────────────────────────────────


def print_result(r: FileResult, verbose: bool) -> None:
    """控制台单行输出。"""
    action_tag = {
        "FIX": "[FIX]   ",
        "ADD": "[ADD]   ",
        "NO_CHANGE": "[NOCHG] ",
        "SKIP": "[SKIP]  ",
        "ROLLBACK": "[ROLLBK]",
    }.get(r.action, "[????]  ")

    status_icon = {
        "VERIFIED": "✅",
        "SUCCESS": "✅",
        "SKIPPED": "⏭️",
        "ROLLED_BACK": "❌",
        "FAILED": "❌",
        "PENDING": "⏳",
    }.get(r.status, "❓")

    old_id = r.old_a_module_id or "(缺头)"
    new_id = r.new_a_module_id or r.depgraph_module_id
    arrow = f"{old_id} → {new_id}" if old_id != new_id else old_id

    line = f"{action_tag} {status_icon} {r.path:<60s} {arrow}"
    if r.error and (verbose or r.status in ("ROLLED_BACK", "FAILED")):
        line += f"  ⚠ {r.error}"
    print(line)


# ─── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="批量修复文件头 module_id 与 depgraph 一致")
    parser.add_argument("--dry-run", action="store_true", default=True, help="只分析, 不修改 (默认)")
    parser.add_argument("--confirm", action="store_true", help="实际执行修改")
    parser.add_argument("--depgraph-json", type=Path, default=None, help="使用已有的 depgraph JSON")
    parser.add_argument("--domain", type=str, default=None, help="只处理指定域 (如 D_RISK)")
    parser.add_argument("--build-status", type=str, nargs="+", default=None, help="过滤 build_status")
    parser.add_argument("--limit", type=int, default=0, help="只处理前 N 个文件 (0=全部)")
    parser.add_argument("--fail-fast", action="store_true", help="第一个失败就停止")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT, help="JSON 报告路径")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--skip-git-check", action="store_true", help="跳过 git 干净检查 (批处理用)")
    args = parser.parse_args()

    mode = "confirm" if args.confirm else "dry-run"
    report = BatchReport(
        run_id=time.strftime("%Y%m%d-%H%M%S"),
        started_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        mode=mode,
    )

    # === Pre-flight ===
    print(f"=== Header Module-ID Fix ({mode}) ===")
    print(f"Run ID: {report.run_id}")
    print()

    if args.confirm and not args.skip_git_check:
        if not check_git_clean():
            print("ERROR: git 工作区不干净, 请先 commit 或 stash 当前改动。", file=sys.stderr)
            print("       (安全机制: 确保 --confirm 模式下有干净的回滚点)", file=sys.stderr)
            print("       (批处理可用 --skip-git-check 跳过)", file=sys.stderr)
            sys.exit(1)
        print("✅ Pre-flight: git 工作区干净")
    elif args.confirm and args.skip_git_check:
        print("⚠️  Pre-flight: 跳过 git 干净检查 (--skip-git-check)")

    # 加载 depgraph
    print("加载 depgraph 路径数据...")
    depgraph = load_depgraph(args.depgraph_json)
    total_files = sum(len(info.get("files", [])) for info in depgraph.values() if isinstance(info, dict))
    print(f"  depgraph 总文件数: {total_files}")

    # 过滤
    build_filter = set(args.build_status) if args.build_status else PRODUCTION_STATUS
    domain_filter = args.domain

    tasks: list[tuple[Path, str, str]] = []
    for domain, info in depgraph.items():
        if not isinstance(info, dict):
            continue
        if domain_filter and domain != domain_filter:
            continue
        for f in info.get("files", []):
            bs = f.get("build_status", "")
            if bs not in build_filter:
                continue
            path_str = f.get("path", "")
            mid = f.get("module_id", "")
            full_path = BASE_DIR / path_str.replace("/", "\\")
            tasks.append((full_path, mid, bs))

    if args.limit > 0:
        tasks = tasks[: args.limit]
    print(f"  待检查文件数: {len(tasks)} (filter: domain={domain_filter or '*'}, status={build_filter})")
    print()

    # === Before stats ===
    print("全量预扫 (before)...")
    report.before_stats = full_rescan(depgraph)
    print(
        f"  一致={report.before_stats['consistent']}  不一致={report.before_stats['inconsistent']}  缺头={report.before_stats['missing']}"
    )
    print()

    # === 逐文件处理 ===
    print("=== 逐文件处理 ===")
    for path, mid, bs in tasks:
        r = fix_file(path, mid, bs)
        report.results.append(r)
        report.summary["total"] += 1

        if r.action == "FIX" and r.status == "VERIFIED":
            report.summary["fixed"] += 1
        elif r.action == "ADD" and r.status == "VERIFIED":
            report.summary["added"] += 1
        elif r.action == "NO_CHANGE" or r.status == "SKIPPED":
            if r.action == "SKIP":
                report.summary["skipped"] += 1
            else:
                report.summary["no_change"] += 1
        elif r.status == "ROLLED_BACK":
            report.summary["rolled_back"] += 1
            report.summary["verification_failed"] += 1
        elif r.status == "FAILED":
            report.summary["rolled_back"] += 1
            report.errors.append(f"{r.path}: {r.error}")

        print_result(r, args.verbose)

        if args.fail_fast and r.status in ("ROLLED_BACK", "FAILED"):
            print("\n⛔ fail-fast: 检测到失败, 停止处理。")
            break

    # === Post-batch ===
    if args.confirm:
        print("\n=== 全量重扫 (after) ===")
        report.after_stats = full_rescan(depgraph)
        print(
            f"  一致={report.after_stats['consistent']}  不一致={report.after_stats['inconsistent']}  缺头={report.after_stats['missing']}"
        )
        delta_ok = report.after_stats["consistent"] - report.before_stats["consistent"]
        print(f"  Delta: +{delta_ok} consistent")

    report.finished_at = time.strftime("%Y-%m-%d %H:%M:%S")

    # === Summary ===
    print("\n=== 汇总 ===")
    s = report.summary
    print(f"  总数:       {s['total']}")
    print(f"  修复(FIX):  {s['fixed']}")
    print(f"  补头(ADD):  {s['added']}")
    print(f"  无变化:     {s['no_change']}")
    print(f"  跳过:       {s['skipped']}")
    print(f"  回滚:       {s['rolled_back']}")
    if report.errors:
        print(f"  错误:       {len(report.errors)}")
        for e in report.errors[:10]:
            print(f"    - {e}")

    # === Save JSON report ===
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report_dict = {
        "run_id": report.run_id,
        "started_at": report.started_at,
        "finished_at": report.finished_at,
        "mode": report.mode,
        "summary": report.summary,
        "before_stats": report.before_stats,
        "after_stats": report.after_stats,
        "errors": report.errors,
        "results": [asdict(r) for r in report.results],
    }
    args.output.write_text(json.dumps(report_dict, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📄 报告已保存: {args.output}")

    # === Exit code ===
    if report.summary["rolled_back"] > 0 and args.confirm:
        sys.exit(1)


if __name__ == "__main__":
    main()
