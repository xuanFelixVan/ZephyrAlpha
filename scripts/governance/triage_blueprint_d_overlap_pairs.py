#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
将 `BLUEPRINT_D_OVERLAP_CANDIDATES_*.json` 做 A 档路径分流，并生成供更强模型二审的 JSONL。

- 全量分组与统计 → `BLUEPRINT_D_OVERLAP_TRIAGE_<date>.json` + 简短 `.md`
- 二审队列（逐行 JSON）→ `BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_<date>.jsonl`

仓库根:
  python scripts/governance/triage_blueprint_d_overlap_pairs.py --date 20260412
  python scripts/governance/triage_blueprint_d_overlap_pairs.py --input docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.json

二审提示词模板（固定输出 schema）:
  docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / "docs" / "09_AUDIT" / "STATE"
GEN = "scripts/governance/triage_blueprint_d_overlap_pairs.py"
PROMPT_TEMPLATE_REL = (
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/"
    "D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md"
)
# 自 docs/09_AUDIT/STATE/*.md 出发的相对链（../../ → docs/）
PROMPT_TEMPLATE_MD_LINK = (
    "../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/"
    "D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md"
)


def split_front_matter(raw: str) -> tuple[str, str]:
    if not raw.startswith("---"):
        return "", raw
    end = raw.find("\n---", 3)
    if end == -1:
        return "", raw
    return raw[3:end], raw[end + 4 :]


def parse_yaml_line(fm: str, key: str) -> str | None:
    for line in fm.splitlines():
        line = line.strip()
        if line.lower().startswith(key.lower() + ":"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def parse_responsibility_excerpt(fm: str, max_len: int = 600) -> str:
    if "responsibility:" not in fm.lower():
        return ""
    lines: list[str] = []
    in_block = False
    for line in fm.splitlines():
        ls = line.strip()
        if ls.lower().startswith("responsibility:"):
            in_block = True
            rest = ls.split(":", 1)[1].strip()
            if rest:
                lines.append(rest)
            continue
        if in_block:
            if ls.startswith("- "):
                lines.append(ls)
            elif not ls or ls.startswith("#"):
                break
            elif ":" in ls and not ls.startswith(" "):
                break
            else:
                lines.append(line)
    text = " ".join(lines)[:max_len]
    return text


def first_h1(body: str) -> str:
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# ") and not s.startswith("##"):
            return s[2:].strip()[:200]
    return ""


def extract_h2(body: str, limit: int = 12) -> list[str]:
    out: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+)$", line.strip())
        if m:
            t = m.group(1).strip()
            if t and not t.startswith("#"):
                out.append(t[:160])
            if len(out) >= limit:
                break
    return out


def body_excerpt(body: str, max_chars: int = 1600) -> str:
    # 跳过 front matter 后从第一个非空实质段落抽一点（含标题行之后）
    lines = body.splitlines()
    buf: list[str] = []
    n = 0
    for line in lines:
        if n >= max_chars:
            break
        buf.append(line)
        n += len(line) + 1
    return "\n".join(buf)[:max_chars]


def excerpt_for_path(repo: Path, rel: str) -> dict:
    p = repo / rel
    if not p.is_file():
        return {
            "path": rel,
            "readable": False,
            "error": "file_not_found",
        }
    raw = p.read_text(encoding="utf-8", errors="replace")
    fm, body = split_front_matter(raw)
    return {
        "path": rel,
        "readable": True,
        "module_id": parse_yaml_line(fm, "module_id"),
        "first_h1": first_h1(body),
        "responsibility_excerpt_zh": parse_responsibility_excerpt(fm),
        "h2_titles_sample": extract_h2(body),
        "body_excerpt": body_excerpt(body),
    }


def norm(p: str) -> str:
    return p.replace("\\", "/")


def in_blueprint_cabinet(p: str) -> bool:
    p = norm(p)
    return "/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/" in p


def is_strong_archive(p: str) -> bool:
    p = norm(p)
    if p.startswith("docs/06_ARCHIVE/"):
        return True
    if p.startswith("docs/09_ARCHIVE/"):
        return True
    if "/_archive/" in p.lower():
        return True
    return False


def classify_tier(path_a: str, path_b: str) -> tuple[str, list[str]]:
    ca, cb = in_blueprint_cabinet(path_a), in_blueprint_cabinet(path_b)
    aa, ab = is_strong_archive(path_a), is_strong_archive(path_b)

    if ca and cb:
        return "DUAL_CABINET", [
            "双方路径均落在正式图纸柜（01_BLUEPRINTS） subtree；若 basename 不同仍同题，二审高敏。"
        ]
    if (ca or cb) and (aa or ab):
        return "BLUEPRINTS_VS_ARCHIVE", [
            "一方在 01_BLUEPRINTS，另一方在归档区或 _archive；默认策略多为「图纸柜为 canonical + 归档侧 stub/链」，二审确认非误杀即可。"
        ]
    if aa and ab:
        return "DUAL_ARCHIVE", [
            "双方均在归档/副本区；二审判断保留单一叙事主档或仅互链，避免重复维护。"
        ]
    if not aa and not ab:
        return "DUAL_ACTIVE", [
            "双方均在活动区（非强归档前缀）；主题重叠时二审优先处理。"
        ]
    return "MIXED", ["路径组合不落入上述规则；二审综合判断。"]


def priority_for_tier(tier: str) -> str:
    if tier in ("DUAL_CABINET", "DUAL_ACTIVE"):
        return "HIGH"
    if tier in ("DUAL_ARCHIVE", "MIXED"):
        return "MEDIUM"
    if tier == "BLUEPRINTS_VS_ARCHIVE":
        return "LOW"
    return "MEDIUM"


def default_input_json(date: str | None) -> Path:
    if date:
        p = STATE / f"BLUEPRINT_D_OVERLAP_CANDIDATES_{date}.json"
        if p.is_file():
            return p
    cands = sorted(STATE.glob("BLUEPRINT_D_OVERLAP_CANDIDATES_*.json"), reverse=True)
    if not cands:
        raise FileNotFoundError("No BLUEPRINT_D_OVERLAP_CANDIDATES_*.json under docs/09_AUDIT/STATE/")
    return cands[0]


def main() -> int:
    ap = argparse.ArgumentParser(description="Triage D-overlap JSON → tiers + second-pass JSONL")
    ap.add_argument("--input", type=str, default=None, help="Path to BLUEPRINT_D_OVERLAP_*.json")
    ap.add_argument("--date", type=str, default=None, help="YYYYMMDD matching BLUEPRINT_D_OVERLAP_CANDIDATES_*")
    ap.add_argument(
        "--queue-mode",
        choices=("all", "high_medium"),
        default="all",
        help="all=全部写入 jsonl；high_medium=排除 second_pass_priority=LOW",
    )
    ap.add_argument("--out-dir", type=str, default=str(STATE), help="Output directory")
    args = ap.parse_args()

    in_path = Path(args.input) if args.input else default_input_json(args.date)
    in_path = in_path.resolve()
    if not in_path.is_file():
        raise SystemExit(f"Input not found: {in_path}")

    payload = json.loads(in_path.read_text(encoding="utf-8"))
    cands: list[dict] = payload.get("candidates") or []
    src_date = args.date
    if not src_date:
        m = re.search(r"(\d{8})", in_path.name)
        src_date = m.group(1) if m else datetime.now(timezone.utc).strftime("%Y%m%d")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    tier_counts: dict[str, int] = {}
    pri_counts: dict[str, int] = {}
    queue_pri_counts: dict[str, int] = {}
    rows_out: list[dict] = []
    jsonl_lines: list[str] = []

    for i, row in enumerate(cands, 1):
        pa, pb = row["path_a"], row["path_b"]
        tier, reasons = classify_tier(pa, pb)
        pri = priority_for_tier(tier)
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        pri_counts[pri] = pri_counts.get(pri, 0) + 1

        ex_a = excerpt_for_path(REPO, pa)
        ex_b = excerpt_for_path(REPO, pb)

        rec = {
            "pair_id": f"D-{src_date}-{i:04d}",
            "source_json": str(in_path.relative_to(REPO)).replace("\\", "/"),
            "triage_tier": tier,
            "triage_reasons_zh": reasons,
            "second_pass_priority": pri,
            "machine": {
                "score": row.get("score"),
                "metrics": row.get("metrics"),
                "titles": row.get("titles"),
                "module_ids": row.get("module_ids"),
                "suggested_canonical": row.get("suggested_canonical"),
                "suggested_other": row.get("suggested_other"),
                "suggested_canonical_reasons_zh": row.get("suggested_canonical_reasons_zh"),
                "suggested_merge_outline": (row.get("suggested_merge_outline") or [])[:20],
            },
            "path_a": pa,
            "path_b": pb,
            "excerpt_a": ex_a,
            "excerpt_b": ex_b,
            "prompt_template_repo_relative": PROMPT_TEMPLATE_REL,
        }
        rows_out.append(rec)

        if args.queue_mode == "high_medium" and pri == "LOW":
            continue
        jsonl_lines.append(json.dumps(rec, ensure_ascii=False))
        queue_pri_counts[pri] = queue_pri_counts.get(pri, 0) + 1

    summary = {
        "generated_utc": ts,
        "generator": GEN,
        "source_overlap_json": str(in_path.relative_to(REPO)).replace("\\", "/"),
        "source_overlap_meta": {
            "candidate_pair_count": len(cands),
            "thresholds": payload.get("thresholds"),
        },
        "tier_counts": dict(sorted(tier_counts.items(), key=lambda x: -x[1])),
        "second_pass_priority_counts_all_pairs": dict(sorted(pri_counts.items(), key=lambda x: -x[1])),
        "second_pass_priority_counts_in_jsonl": dict(sorted(queue_pri_counts.items(), key=lambda x: -x[1])),
        "queue_mode": args.queue_mode,
        "jsonl_line_count": len(jsonl_lines),
        "prompt_template_repo_relative": PROMPT_TEMPLATE_REL,
        "pairs": rows_out,
    }

    j_out = out_dir / f"BLUEPRINT_D_OVERLAP_TRIAGE_{src_date}.json"
    j_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    jl_out = out_dir / f"BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_{src_date}.jsonl"
    jl_out.write_text("\n".join(jsonl_lines) + ("\n" if jsonl_lines else ""), encoding="utf-8")

    md_lines = [
        "---",
        f"module_id: AUDIT_BLUEPRINT_D_OVERLAP_TRIAGE_{src_date}",
        "standard_type: audit_state",
        "generated_by: " + GEN,
        f"source_overlap_json: '{in_path.name}'",
        "---",
        "",
        f"# 蓝图 D 类重叠 — A 档分流摘要（`{src_date}`）",
        "",
        f"> **输入**：`{in_path.relative_to(REPO).as_posix()}`",
        f"> **二审提示词模板**：[D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md]({PROMPT_TEMPLATE_MD_LINK})",
        "",
        "## 统计",
        "",
        f"- 候选对数：**{len(cands)}**",
        f"- 写入二审队列（JSONL）行数：**{len(jsonl_lines)}**（`queue_mode={args.queue_mode}`）",
        "",
        "### triage_tier",
        "",
    ]
    for k, v in sorted(tier_counts.items(), key=lambda x: -x[1]):
        md_lines.append(f"- `{k}`: **{v}**")
    md_lines.extend(["", "### second_pass_priority（写入 JSONL 的分布）", ""])
    for k, v in sorted(queue_pri_counts.items(), key=lambda x: -x[1]):
        md_lines.append(f"- `{k}`: **{v}**")
    if args.queue_mode == "high_medium":
        md_lines.append("")
        md_lines.append("> `queue_mode=high_medium`：已排除 `second_pass_priority=LOW` 的对。")
    md_lines.extend(
        [
            "",
            "## 产出文件",
            "",
            f"- [`BLUEPRINT_D_OVERLAP_TRIAGE_{src_date}.json`](./BLUEPRINT_D_OVERLAP_TRIAGE_{src_date}.json)",
            f"- [`BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_{src_date}.jsonl`](./BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_{src_date}.jsonl)",
            "",
        ]
    )
    md_out = out_dir / f"BLUEPRINT_D_OVERLAP_TRIAGE_{src_date}.md"
    md_out.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote {j_out.relative_to(REPO)}")
    print(f"Wrote {jl_out.relative_to(REPO)} ({len(jsonl_lines)} lines)")
    print(f"Wrote {md_out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
