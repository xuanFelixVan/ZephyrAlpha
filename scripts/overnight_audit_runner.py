# -*- coding: utf-8 -*-
"""
过夜 / 长任务文档审计报告生成器（只读 + 子进程调用现有脚本）

在仓库根执行:
  python scripts/overnight_audit_runner.py

产出目录: docs/09_AUDIT/STATE/overnight_runs/<UTC或本地时间戳>/
  - run.log              完整日志
  - MANIFEST.json        步骤、耗时、退出码
  - CONSOLIDATED_REPORT_FOR_AI.md  给下一轮 AI 阅读的主报告（含统计、路径、摘要）
  - module_id_duplicates_detail.md
  - invalid_links_detail.md
  - git_snapshot.txt
  - 并复制 inventory / sentinel 扫描结果副本（便于单目录打包）

说明: 本脚本不修改任何文档正文；仅调用 generate_md_inventory_by_dir 与 sentinel_l1_governance_scan
（二者会覆盖 STATE 下固定文件名，故本运行结束后将关键文件复制到本次 run 子目录）。
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "docs" / "09_AUDIT" / "STATE"
SCRIPTS = REPO / "scripts"
SKIP_PARTS = {".git", ".venv", ".pytest_cache", "__pycache__"}


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def run_cmd(
    log: logging.Logger,
    name: str,
    args: list[str],
    cwd: Path,
    env: dict | None = None,
) -> int:
    log.info("=== STEP: %s ===", name)
    log.info("cmd: %s", " ".join(args))
    p = subprocess.run(
        args,
        cwd=str(cwd),
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if p.stdout:
        log.info("stdout:\n%s", p.stdout[-8000:] if len(p.stdout) > 8000 else p.stdout)
    if p.stderr:
        log.warning("stderr:\n%s", p.stderr[-4000:] if len(p.stderr) > 4000 else p.stderr)
    log.info("exit_code=%s", p.returncode)
    return p.returncode


def git_snapshot(log: Path) -> str:
    lines = []
    for cmd in [
        ["git", "rev-parse", "HEAD"],
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        ["git", "status", "-sb"],
        ["git", "tag", "-l", "audit-snapshot-*"],
        ["git", "tag", "-l", "audit-phase0-*"],
    ]:
        try:
            r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
            lines.append("$ " + " ".join(cmd))
            lines.append((r.stdout or "") + (r.stderr or ""))
            lines.append("")
        except Exception as e:
            lines.append(f"$ {' '.join(cmd)} -> ERROR {e}\n")
    # 与快照 tag 的差异（若存在）
    for tag in ["audit-snapshot-20260408", "audit-snapshot-20260407"]:
        try:
            r = subprocess.run(
                ["git", "diff", "--name-status", f"{tag}...HEAD"],
                cwd=str(REPO),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            if r.returncode == 0 and (r.stdout or "").strip():
                lines.append(f"$ git diff --name-status {tag}...HEAD (truncated)")
                out = r.stdout
                lines.append(out[:50000] + ("\n... [truncated]\n" if len(out) > 50000 else ""))
                lines.append("")
                break
        except Exception as e:
            lines.append(f"# diff {tag}: {e}\n")
    text = "\n".join(lines)
    log.write_text(text, encoding="utf-8")
    return text


def aggregate_docs_top_level() -> list[tuple[str, int, int]]:
    """返回 (顶层, 文件数, 总字节) 仅 docs/ 下"""
    counts: Counter[str] = Counter()
    bytes_by_top: dict[str, int] = {}
    for p in REPO.glob("docs/**/*.md"):
        if not p.is_file():
            continue
        if any(x in p.parts for x in SKIP_PARTS):
            continue
        try:
            rel = p.relative_to(REPO / "docs")
        except ValueError:
            continue
        top = rel.parts[0] if rel.parts else "."
        counts[top] += 1
        try:
            bytes_by_top[top] = bytes_by_top.get(top, 0) + p.stat().st_size
        except OSError:
            pass
    out = [(k, counts[k], bytes_by_top.get(k, 0)) for k in sorted(counts.keys())]
    out.sort(key=lambda x: -x[1])
    return out


def largest_md_files(n: int = 80) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for p in REPO.rglob("*.md"):
        if not p.is_file():
            continue
        if any(x in p.parts for x in SKIP_PARTS):
            continue
        try:
            sz = p.stat().st_size
            rel = p.relative_to(REPO).as_posix()
        except OSError:
            continue
        rows.append((sz, rel))
    rows.sort(reverse=True)
    return rows[:n]


def build_module_id_report(sentinel_json: dict, out_md: Path, max_per_group: int = 40) -> None:
    mi = sentinel_json.get("module_ids") or {}
    dup = mi.get("duplicates") or {}
    lines = [
        "# module_id 重复明细（供 AI 分批消解）",
        "",
        f"> 重复组数: {mi.get('duplicate_ids_count', 0)}",
        "",
    ]
    for mid, files in sorted(dup.items(), key=lambda x: -len(x[1]))[:120]:
        lines.append(f"## `{mid}` — {len(files)} 个文件")
        lines.append("")
        show = files[:max_per_group]
        for f in show:
            lines.append(f"- `{f}`")
        if len(files) > max_per_group:
            lines.append(f"- … 另有 {len(files) - max_per_group} 个文件未展开")
        lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def build_invalid_links_report(sentinel_json: dict, out_md: Path, cap: int = 1500) -> None:
    details = sentinel_json.get("links", {}).get("invalid_details_sample") or []
    lines = [
        "# 无效内链明细（样本上限可调整）",
        "",
        f"> 条数: {len(details)}（扫描器上限内）",
        "",
        "| source | url | resolved |",
        "|--------|-----|----------|",
    ]
    for i, row in enumerate(details[:cap]):
        s = str(row.get("source", "")).replace("|", "\\|")
        u = str(row.get("url", "")).replace("|", "\\|")
        r = str(row.get("resolved", "")).replace("|", "\\|")
        lines.append(f"| `{s}` | `{u}` | `{r}` |")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def write_consolidated(
    run_dir: Path,
    sentinel_json: dict,
    git_text: str,
    top_level: list[tuple[str, int, int]],
    large_files: list[tuple[int, str]],
    manifest: dict,
) -> None:
    s = sentinel_json.get("links", {}).get("stats", {})
    mi = sentinel_json.get("module_ids", {})
    md_count = sentinel_json.get("md_file_count", 0)

    lines = [
        "# CONSOLIDATED REPORT FOR AI（过夜审计汇总 — 供下一轮会话阅读）",
        "",
        f"> 生成时间: {manifest.get('finished_at_local', '')}",
        f"> 仓库: `{REPO}`",
        f"> 运行目录: `{run_dir.relative_to(REPO)}`",
        "",
        "## 1. 执行摘要",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| Markdown 文件数 | {md_count} |",
        f"| 内链解析数（相对路径类） | {s.get('total_md_links', '—')} |",
        f"| 判定有效链接 | {s.get('valid', '—')} |",
        f"| 判定无效链接 | {s.get('invalid', '—')} |",
        f"| 重复 module_id 组数 | {mi.get('duplicate_ids_count', '—')} |",
        f"| 未检出 module_id 文件数（头 120KB） | {mi.get('no_id_total', '—')} |",
        "",
        "## 2. 本目录产出文件（请优先阅读）",
        "",
        "- `MANIFEST.json` — 步骤与时间",
        "- `module_id_duplicates_detail.md` — 重复 id 与路径列表",
        "- `invalid_links_detail.md` — 无效链接表",
        "- `git_snapshot.txt` — 分支、tag、diff 摘要",
        "- `SENTINEL_L1_SCAN_*.json` — 机器可读全量",
        "- `MD_FILES_BY_SUBDIRECTORY_*.md` — 按目录文件清单副本",
        "",
        "## 3. docs/ 一级目录文档量（Top 30）",
        "",
        "| 目录 | 文件数 | 约字节 |",
        "|------|--------|--------|",
    ]
    for name, cnt, b in top_level[:30]:
        lines.append(f"| `{name}` | {cnt} | {b} |")
    lines.extend(
        [
            "",
            "## 4. 体积最大的 Markdown（Top 40）",
            "",
            "| 字节 | 路径 |",
            "|------|------|",
        ]
    )
    for sz, path in large_files[:40]:
        lines.append(f"| {sz} | `{path}` |")
    lines.extend(
        [
            "",
            "## 5. Git 快照（摘录）",
            "",
            "```text",
            git_text[:12000] + ("\n... [truncated]" if len(git_text) > 12000 else ""),
            "```",
            "",
            "## 6. 下一轮 AI 建议动作",
            "",
            "1. 阅读 `invalid_links_detail.md`，按类修复：缺失文件 / 伪链接 / 路径层级错误。",
            "2. 按 `module_id_duplicates_detail.md` 分批消解重复（先 audit_state 与 INDEX 模板）。",
            "3. 对照 `FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md` 继续做 L2 分批职责审计。",
            "",
        ]
    )
    (run_dir / "CONSOLIDATED_REPORT_FOR_AI.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    run_id = _ts()
    run_dir = STATE / "overnight_runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "run.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    log = logging.getLogger("overnight")

    manifest: dict = {
        "run_id": run_id,
        "repo": str(REPO),
        "started_at_local": datetime.now().isoformat(timespec="seconds"),
        "steps": [],
    }
    code = 0

    try:
        git_path = run_dir / "git_snapshot.txt"
        git_text = git_snapshot(git_path)
        manifest["steps"].append({"name": "git_snapshot", "ok": True})

        # 1) inventory
        rc = run_cmd(log, "generate_md_inventory", [sys.executable, str(SCRIPTS / "generate_md_inventory_by_dir.py")], REPO)
        manifest["steps"].append({"name": "generate_md_inventory_by_dir.py", "exit_code": rc})
        if rc != 0:
            code = 1
        inv_src = STATE / "MD_FILES_BY_SUBDIRECTORY_20260408.md"
        if inv_src.is_file():
            dst = run_dir / f"MD_FILES_BY_SUBDIRECTORY_{run_id}.md"
            dst.write_text(inv_src.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

        # 2) sentinel
        rc2 = run_cmd(log, "sentinel_l1", [sys.executable, str(SCRIPTS / "sentinel_l1_governance_scan.py")], REPO)
        manifest["steps"].append({"name": "sentinel_l1_governance_scan.py", "exit_code": rc2})
        if rc2 != 0:
            code = 1

        sj = STATE / "SENTINEL_L1_SCAN_20260408.json"
        sentinel_data: dict = {}
        if sj.is_file():
            sentinel_data = json.loads(sj.read_text(encoding="utf-8"))
            for name in ["SENTINEL_L1_SCAN_20260408.json", "SENTINEL_L1_SCAN_20260408.md"]:
                p = STATE / name
                if p.is_file():
                    (run_dir / f"{p.stem}_{run_id}{p.suffix}").write_bytes(p.read_bytes())

        build_module_id_report(sentinel_data, run_dir / "module_id_duplicates_detail.md")
        build_invalid_links_report(sentinel_data, run_dir / "invalid_links_detail.md")

        top_level = aggregate_docs_top_level()
        large_files = largest_md_files(80)

        manifest["finished_at_local"] = datetime.now().isoformat(timespec="seconds")
        write_consolidated(run_dir, sentinel_data, git_text, top_level, large_files, manifest)

        (run_dir / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        # 可选：inventory CSV 若存在则复制
        csv_path = STATE / "inventory_md_20260408.csv"
        if csv_path.is_file():
            (run_dir / f"inventory_md_{run_id}.csv").write_bytes(csv_path.read_bytes())

        log.info("DONE run_dir=%s exit=%s", run_dir, code)
        return code
    except Exception as e:
        log.exception("FATAL: %s", e)
        manifest["error"] = str(e)
        manifest["finished_at_local"] = datetime.now().isoformat(timespec="seconds")
        (run_dir / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return 2


if __name__ == "__main__":
    sys.exit(main())
