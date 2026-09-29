# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/backfill_roor_reg_annotation.py | §
# [MODULE] scripts.governance.d3_metadata.backfill_roor_reg_annotation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] _shared.constants; _shared.encoding; _shared.yaml_utils; zephyr.shared.io.file_utils
# [CONSUMERS] manual CLI; registry-consistency 车道（--check 可挂门）；维护班（--patch 应用）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 缺失映射全程机生（宪法 §9.5 禁手工清单）；默认零写入——回填只出建议 diff/patch；
#  写入必经 --only 显式清单 + safe_write_text CAS；maintenance:auto 册（机生文件）默认拒写归
#  generator 车道（注进机生文件会被下次再生抹掉，修因在生成器模板）；不可达条目（postgresql://
#  等非文件 medium）机检豁免仅列报。
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无欠账/成功）；EXIT_FINDINGS=1（有欠账/--check 模式）；EXIT_ERROR=2（异常）
# [TESTS] tests/governance/d3_metadata/test_backfill_roor_reg_annotation.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""backfill_roor_reg_annotation.py — ROOR 册页 REG 名批注欠账扫描/回填机制（F92 治本件）

病灶（F92 原问题账本处方）：ROOR（docs/registry_of_registries.yaml）76+ 册中约 40 册
"环节在、册内未点 REG 名"——登记表物理文件内不含自己的 registry_id（如 REG-GATE-001），
从册页侧机检不可达 ROOR 条目，只能单向 ROOR→册。本件建"册页回填"机生机制：

  1. 扫描器：深度遍历 ROOR 全部条目（registry_id+physical_path）→ 读物理册页 →
     判定 ok（已点 REG 名）/ missing（欠账）/ unreachable（非文件 medium，豁免）/
     nofile（路径失效漂移）；同时与 ROOR summary.total_registries 对账报漂移。
  2. 回填器：对欠账册页产出**建议 diff**（默认零写入）；--patch 落统一 patch 文件供
     维护班应用；--apply --only <path,...> 半自动确认写（safe_write_text CAS，
     行为与 F92 短期回填先例 3cb98bb6f6 同门）。

批注形态（机检锚点，一行点全名）::

    # [ROOR] registry_id=REG-A-001 REG-B-002      （yaml/py/注释头文件）
    <!-- [ROOR] registry_id=REG-X-001 -->          （无 frontmatter 的 .md）

注入位规则（保各格式解析不变量）：
  - 首行 `---`（frontmatter 册）→ 注入 frontmatter 块内第 2 行（YAML 注释合法）
  - 首行 `#` 开头（代码头/注释头册）→ 首行之后（保"首行即代码头"解析不变量）
  - .md 无 frontmatter → 顶部 HTML 注释
  - 其余纯文本/yaml → 顶部行注

Usage::

    python scripts/governance/d3_metadata/backfill_roor_reg_annotation.py            # 扫描报告
    python ... backfill_roor_reg_annotation.py --output report.yaml                  # 机生映射落盘
    python ... backfill_roor_reg_annotation.py --diff                                # 建议 diff 到 stdout
    python ... backfill_roor_reg_annotation.py --patch f92_roor.patch                # patch 文件
    python ... backfill_roor_reg_annotation.py --apply --only path/a.yaml,path/b.md  # 确认写（CAS）
    python ... backfill_roor_reg_annotation.py --check                               # 门就绪出口
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_yaml

__manifest__ = """
dimensions: [D3]
priority: P2
timeout_seconds: 60
args:
  - {flag: --check, type: bool, description: "门出口：有欠账 exit 1"}
  - {flag: --diff, type: bool, description: "打印欠账册页建议 diff（零写入）"}
  - {flag: --patch, type: str, description: "建议 diff 落 patch 文件"}
  - {flag: --apply, type: bool, description: "半自动写（必须配 --only）"}
  - {flag: --only, type: str, description: "显式确认的册页相对路径清单（逗号分隔）"}
  - {flag: --output, type: str, description: "机生缺失映射 YAML 输出路径"}
  - {flag: --roor, type: str, description: "ROOR 路径覆盖（默认 docs/registry_of_registries.yaml）"}
  - {flag: --repo-root, type: str, description: "仓库根覆盖（测试用）"}
warn_only: false
description: >
  ROOR 册页 REG 名批注欠账机生扫描/回填：对账产出缺失映射，回填只出建议 diff/patch，
  --only 显式确认后 safe_write_text CAS 写入；maintenance:auto 册归 generator 车道默认拒写。
"""

ROOR_REL_DEFAULT = "docs/registry_of_registries.yaml"

# 批注锚点行：行内含 "[ROOR] registry_id="，值域 REG 名（空格分隔可多点）。
ANNOTATION_MARKER = "[ROOR] registry_id="
_ANNOTATION_LINE_RE = re.compile(r"^\s*(?:#|<!--)\s*\[ROOR\]\s*registry_id=(?P<ids>[\w\-. ]+?)(?:\s*-->)?\s*$")
_RID_RE = re.compile(r"^REG-[A-Za-z0-9_\-]+$")

# writer 注入点：默认 safe_write_text CAS；测试注 fake（宪法测试隔离，不碰生产路径）
Writer = Callable[[Path, str, str], None]


def parse_annotation_ids(content: str) -> list[str]:
    """从册页内容解析已点 REG 名（[ROOR] 锚点行，可多行多点）。"""
    ids: list[str] = []
    for line in content.splitlines():
        m = _ANNOTATION_LINE_RE.match(line)
        if m:
            ids += [t for t in m.group("ids").split() if t]
    return ids


def walk_roor_entries(node: object) -> list[dict]:
    """深度遍历 ROOR，产出全部含 registry_id+physical_path 的登记表条目（跨 tier 嵌套）。"""
    out: list[dict] = []
    if isinstance(node, dict):
        if "registry_id" in node and "physical_path" in node:
            out.append(node)
        for v in node.values():
            out += walk_roor_entries(v)
    elif isinstance(node, list):
        for v in node:
            out += walk_roor_entries(v)
    return out


def _norm_rel_path(raw: str) -> str:
    return raw.replace("\\", "/").strip().lstrip("./")


def _declares_auto_maintenance(entry: dict) -> bool:
    """ROOR 条目 maintenance 声明是否 auto（机生文件——批注须进生成器模板，禁直改册页）。"""
    maint = str(entry.get("maintenance", ""))
    return maint.strip().lower().startswith("auto")


def classify_entries(roor: dict, repo_root: Path) -> dict:
    """扫描器主体：ROOR 条目 → 册页判定四态 + summary 对账。

    Returns dict with rows (逐条目) / missing / unreachable / nofile / counts /
    summary_total_registries / summary_drift。
    """
    entries = walk_roor_entries(roor)
    rows: list[dict] = []
    for e in entries:
        rid = str(e["registry_id"])
        raw_pp = str(e.get("physical_path", ""))
        pp = _norm_rel_path(raw_pp)
        row = {
            "registry_id": rid,
            "physical_path": pp,
            "maintenance": str(e.get("maintenance", "manual")).strip(),
            "format": str(e.get("format", "")).strip(),
            "status": "ok",
            "reason": "",
        }
        if "://" in raw_pp:  # postgresql:// 等非文件 medium——机检结构性豁免
            row.update(status="unreachable", reason="non-file medium（DB/外链）")
        else:
            f = repo_root / pp
            if not f.exists():
                row.update(status="nofile", reason="physical_path 磁盘不存在")
            elif f.is_dir():
                row.update(status="unreachable", reason="physical_path 是目录")
            else:
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                except OSError as ex:
                    row.update(status="unreachable", reason=f"read fail: {type(ex).__name__}")
                else:
                    if rid in content:
                        row["status"] = "ok"
                    else:
                        row.update(
                            status="missing",
                            reason="册内未点 REG 名（机检不可达）",
                            lane="generator" if _declares_auto_maintenance(e) else "manual",
                        )
        rows.append(row)

    missing = [r for r in rows if r["status"] == "missing"]
    grouped: dict[str, list[str]] = {}
    for r in sorted(missing, key=lambda x: (x["physical_path"], x["registry_id"])):
        grouped.setdefault(r["physical_path"], []).append(r["registry_id"])

    summary = roor.get("summary") if isinstance(roor, dict) else None
    summary_total = summary.get("total_registries") if isinstance(summary, dict) else None
    return {
        "rows": rows,
        "missing": missing,
        "grouped_missing": grouped,
        "unreachable": [r for r in rows if r["status"] == "unreachable"],
        "nofile": [r for r in rows if r["status"] == "nofile"],
        "total_entries": len(rows),
        "summary_total_registries": summary_total,
        "summary_drift": bool(isinstance(summary_total, int) and summary_total != len(rows)),
    }


# ---------------------------------------------------------------------------
# 批注注入与 diff
# ---------------------------------------------------------------------------


def _detect_newline(lines: list[str]) -> str:
    return "\r\n" if lines and lines[0].endswith("\r\n") else "\n"


def annotation_line(rids: list[str], *, markdown_bare: bool = False, newline: str = "\n") -> str:
    """构造批注锚点行（一册一行点全名，rid 排序去重）。"""
    uniq = sorted(dict.fromkeys(rids))
    body = f"{ANNOTATION_MARKER}{' '.join(uniq)}"
    text = f"<!-- {body} -->" if markdown_bare else f"# {body}"
    return text + newline


def propose_content(content: str, rids: list[str], suffix: str = ".yaml") -> str:
    """按注入位规则产出回填后内容（纯函数，不落盘）。"""
    lines = content.splitlines(keepends=True)
    nl = _detect_newline(lines)
    if not lines:
        return annotation_line(rids, markdown_bare=(suffix == ".md"), newline="")
    first = lines[0].rstrip("\r\n")
    if first == "---":  # frontmatter 册：注 frontmatter 块内（YAML 注释合法，保块结构）
        idx, bare = 1, False
    elif suffix == ".md":  # md 无 frontmatter：顶部 HTML 注释（md 的 `#` 是标题，非注释）
        idx, bare = 0, True
    elif first.startswith("#"):  # 代码头/注释头册：首行之后（保首行即代码头不变量）
        idx, bare = 1, False
    else:  # 纯 yaml/文本：顶部行注
        idx, bare = 0, False
    ann = annotation_line(rids, markdown_bare=bare, newline=nl)
    return "".join(lines[:idx]) + ann + "".join(lines[idx:])


def build_diff(rel_path: str, old: str, new: str) -> str:
    """统一 diff（建议 diff 形态，维护班可直接 git apply）。"""
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}",
        )
    )


def build_all_diffs(result: dict, repo_root: Path, *, include_auto: bool = False) -> list[str]:
    """对欠账册页逐个产出建议 diff（同册多 REG 合并一行）。"""
    diffs: list[str] = []
    for rel, rids in sorted(result["grouped_missing"].items()):
        lane_rows = [r for r in result["missing"] if r["physical_path"] == rel]
        if not include_auto and any(r.get("lane") == "generator" for r in lane_rows):
            continue
        f = repo_root / rel
        old = f.read_text(encoding="utf-8", errors="replace")
        new = propose_content(old, rids, suffix=f.suffix)
        diffs.append(build_diff(rel, old, new))
    return diffs


# ---------------------------------------------------------------------------
# apply（半自动确认写）
# ---------------------------------------------------------------------------


def _default_writer(path: Path, new_content: str, expected_base_sha256: str) -> None:
    """默认写口：safe_write_text CAS（热册防并发覆盖，写后进程外可核）。"""
    from zephyr.shared.io.file_utils import safe_write_text  # noqa: PLC0415

    safe_write_text(
        path,
        new_content,
        expected_base_sha256=expected_base_sha256,
        allow_mass_edit=True,
    )


def apply_backfill(
    result: dict,
    repo_root: Path,
    only: list[str],
    *,
    writer: Writer = _default_writer,
    allow_auto: bool = False,
) -> tuple[list[str], list[str]]:
    """对 --only 显式清单执行回填写（CAS）。返回 (written, skipped)。

    拒写语义：清单外路径 / manual 车道外的 auto 册（无 --allow-auto）/ 非欠账册。
    """
    manual_by_path = {
        rel: rids
        for rel, rids in result["grouped_missing"].items()
        if not any(r.get("lane") == "generator" for r in result["missing"] if r["physical_path"] == rel)
    }
    written: list[str] = []
    skipped: list[str] = []
    import hashlib

    for rel in only:
        rel_n = _norm_rel_path(rel)
        rids = manual_by_path.get(rel_n)
        if rids is None:
            is_auto = rel_n in result["grouped_missing"]
            skipped.append(f"{rel_n}（{'auto 车道需 --allow-auto' if is_auto else '不在欠账清单/已确认'}）")
            continue
        f = repo_root / rel_n
        old = f.read_text(encoding="utf-8", errors="replace")
        expected = hashlib.sha256(old.encode("utf-8")).hexdigest()
        new = propose_content(old, rids, suffix=f.suffix)
        if new == old:
            skipped.append(f"{rel_n}（内容未变，跳写）")
            continue
        writer(f, new, expected)
        written.append(rel_n)
    return written, skipped


# ---------------------------------------------------------------------------
# 报告与 CLI
# ---------------------------------------------------------------------------


def build_report(result: dict, roor_rel: str) -> dict:
    """机生缺失映射（宪法 §9.5：清单只许生成器产出）。"""
    return {
        "generated_by": "scripts/governance/d3_metadata/backfill_roor_reg_annotation.py",
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "roor": roor_rel,
        "total_entries": result["total_entries"],
        "summary_total_registries": result["summary_total_registries"],
        "summary_drift": result["summary_drift"],
        "counts": {
            "ok": sum(1 for r in result["rows"] if r["status"] == "ok"),
            "missing": len(result["missing"]),
            "missing_manual_lane": sum(1 for r in result["missing"] if r.get("lane") == "manual"),
            "missing_generator_lane": sum(1 for r in result["missing"] if r.get("lane") == "generator"),
            "unreachable": len(result["unreachable"]),
            "nofile": len(result["nofile"]),
        },
        "missing": [
            {k: r[k] for k in ("registry_id", "physical_path", "lane", "maintenance", "format")}
            for r in sorted(result["missing"], key=lambda x: (x["physical_path"], x["registry_id"]))
        ],
        "grouped_missing": {k: result["grouped_missing"][k] for k in sorted(result["grouped_missing"])},
        "unreachable": [{k: r[k] for k in ("registry_id", "physical_path", "reason")} for r in result["unreachable"]],
        "nofile": [{k: r[k] for k in ("registry_id", "physical_path", "reason")} for r in result["nofile"]],
    }


def _print_summary(result: dict) -> None:
    c = build_report(result, "")["counts"]
    print(
        f"ROOR 册页 REG 名对账：条目 {result['total_entries']}"
        f"｜已点 {c['ok']}｜欠账 {c['missing']}（manual {c['missing_manual_lane']}"
        f"/generator {c['missing_generator_lane']}）"
        f"｜不可达豁免 {c['unreachable']}｜路径失效 {c['nofile']}"
    )
    if result["summary_drift"]:
        print(
            f"DRIFT: ROOR summary.total_registries={result['summary_total_registries']}"
            f" ≠ 实扫条目 {result['total_entries']}（summary 由 --refresh-summary 机生，另案对齐）"
        )


def _load_roor_checked(args) -> dict | None:
    """解析并校验 ROOR（失败打印 ERROR 并返回 None——main 据此走 EXIT_ERROR）。"""
    repo_root = Path(args.repo_root).resolve()
    roor_path = Path(args.roor)
    if not roor_path.is_absolute():
        roor_path = repo_root / roor_path
    roor = load_yaml(roor_path)
    if not isinstance(roor, dict):
        print(f"ERROR: ROOR 解析失败或非映射：{roor_path}")
        return None
    return roor


def _emit_missing_report(args, result: dict) -> None:
    """--output：机生缺失映射 YAML 落盘（零行为变化自 main 抽出）。"""
    import yaml  # noqa: PLC0415

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        yaml.dump(build_report(result, args.roor), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"机生缺失映射 → {out}")


def _emit_diffs(args, repo_root: Path, result: dict) -> None:
    """--diff/--patch：欠账建议 diff 打印/落 patch（零行为变化自 main 抽出）。"""
    diffs = build_all_diffs(result, repo_root, include_auto=args.include_auto_diff)
    if not diffs:
        print("（无 manual 车道欠账 diff——auto 车道用 --include-auto-diff 只读展示）")
    text = "".join(diffs)
    if args.diff and text:
        print(text, end="")
    if args.patch:
        pf = Path(args.patch)
        pf.parent.mkdir(parents=True, exist_ok=True)
        pf.write_text(text, encoding="utf-8")
        print(f"建议 patch（{len(diffs)} 册）→ {pf}")


def _run_apply(args, repo_root: Path, result: dict) -> int | None:
    """--apply：半自动确认写。返回 int=main 立即以该码退出；None=继续后续车道。"""
    if not args.only:
        print("ERROR: --apply 必须配 --only <path,...> 显式清单（热册禁盲写）")
        return EXIT_ERROR
    only = [p for p in args.only.split(",") if p.strip()]
    written, skipped = apply_backfill(result, repo_root, only, allow_auto=args.allow_auto)
    for w in written:
        print(f"WROTE(CAS): {w}")
    for s in skipped:
        print(f"SKIP: {s}")
    if skipped and not written:
        return EXIT_FINDINGS
    return None


def main() -> int:  # noqa: PLR0912, PLR0915  CLI 分支平铺可读
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="ROOR 册页 REG 名批注欠账扫描/回填（默认零写入）")
    parser.add_argument("--check", action="store_true", help="门出口：有欠账 exit 1")
    parser.add_argument("--diff", action="store_true", help="打印欠账册页建议 diff（零写入）")
    parser.add_argument("--patch", type=str, default=None, help="建议 diff 落 patch 文件")
    parser.add_argument("--apply", action="store_true", help="半自动确认写（必须配 --only）")
    parser.add_argument("--only", type=str, default=None, help="显式确认的册页相对路径清单（逗号分隔）")
    parser.add_argument("--allow-auto", action="store_true", help="放量写 maintenance:auto 册（默认拒）")
    parser.add_argument("--include-auto-diff", action="store_true", help="diff/patch 含 auto 车道（只读展示）")
    parser.add_argument("--output", type=str, default=None, help="机生缺失映射 YAML 输出路径")
    parser.add_argument("--roor", type=str, default=ROOR_REL_DEFAULT, help="ROOR 路径覆盖")
    parser.add_argument("--repo-root", type=str, default=str(REPO_ROOT), help="仓库根覆盖（测试用）")
    args = parser.parse_args()

    # [COMPLEXITY 修复 st-c9-close4] 原 main 21>15：按 CLI 车道拆四 helper
    # （_load_roor_checked/_emit_missing_report/_emit_diffs/_run_apply）——调度序、
    # 打印文本、退出码语义逐行保持零行为变化。
    try:
        repo_root = Path(args.repo_root).resolve()
        roor = _load_roor_checked(args)
        if roor is None:
            return EXIT_ERROR
        result = classify_entries(roor, repo_root)
        _print_summary(result)

        if args.output:
            _emit_missing_report(args, result)

        if args.diff or args.patch:
            _emit_diffs(args, repo_root, result)

        if args.apply:
            apply_rc = _run_apply(args, repo_root, result)
            if apply_rc is not None:
                return apply_rc

        if args.check:
            debt = len(result["missing"])
            print(f"CHECK: {'FAIL' if debt else 'PASS'}（欠账 {debt} 册条目）")
            return EXIT_FINDINGS if debt else EXIT_PASS
        return EXIT_PASS
    except Exception as ex:  # noqa: BLE001  CLI 顶层兜底（ERROR_CONTRACT EXIT_ERROR）
        print(f"ERROR: {type(ex).__name__}: {ex}")
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
