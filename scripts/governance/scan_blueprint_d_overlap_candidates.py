#!/usr/bin/env python3
"""
D 类蓝图「主题/职责可能重叠」候选对扫描（启发式，非语义 embedding）。

产出 **机器裁决建议**：候选对、相似度指标、建议 canonical、建议合并大纲（H2 并集草案）。
**最终裁决与合稿**仍须 Owner / 架构评审（见办公室 Playbook）。

仓库根:
  python scripts/governance/scan_blueprint_d_overlap_candidates.py --date 20260411

输出:
  docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_<date>.json
  docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_<date>.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

GEN = "scripts/governance/scan_blueprint_d_overlap_candidates.py"

# 极常见虚词（中英），降低「泛泛相同」假阳性；可再扩
_STOP = frozenset(
    """
    the a an and or of to in for is are was were be been being on at by with from
    as if then else not no yes all any each both one two
    的 了 和 与 或 在 为 是 有 将 可 能 对 从 以 及 等 其 该 此 与 中 上 下 及 并 或 若 则 已 未 请 见 如 更 较 最
    蓝图 blueprint 模块 module 文档 系统 设计 实现 方案 概述 目标 功能 架构 层 layer
    """.split()
)


def git_ls_files(repo_root: Path) -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=repo_root, text=True)
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def is_blueprint_md(rel: str) -> bool:
    b = rel.rsplit("/", 1)[-1]
    if not b.lower().endswith(".md"):
        return False
    return "BLUEPRINT" in b.upper()


def default_exclude(rel: str) -> bool:
    if "docs/09_AUDIT/STATE/overnight_runs/" in rel:
        return True
    return False


def split_front_matter(raw: str) -> tuple[str, str]:
    if not raw.startswith("---"):
        return "", raw
    end = raw.find("\n---", 3)
    if end == -1:
        return "", raw
    return raw[3:end], raw[end + 4 :]


def parse_simple_yaml_field(fm: str, key: str) -> str | None:
    for line in fm.splitlines():
        line = line.strip()
        if line.lower().startswith(key.lower() + ":"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def parse_responsibility_block(fm: str) -> str:
    if "responsibility:" not in fm.lower():
        return ""
    lines: list[str] = []
    in_block = False
    for line in fm.splitlines():
        if re.match(r"^\s*responsibility\s*:", line, re.I):
            in_block = True
            rest = line.split(":", 1)[1].strip()
            if rest and not rest.startswith("|") and not rest.startswith(">"):
                lines.append(rest)
            continue
        if in_block:
            if line.startswith(" ") and re.match(r"^\s+-\s+", line):
                lines.append(line.strip())
            elif line.startswith(" ") and "|" in line:
                lines.append(line.strip())
            elif line.strip() and not line.startswith(" ") and ":" in line and not line.startswith("-"):
                break
            elif line.strip() == "":
                continue
    return " ".join(lines)


def first_markdown_title(body: str) -> str:
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# ") and not s.startswith("##"):
            return s[2:].strip()
    return ""


def extract_h2(body: str, limit: int = 48) -> list[str]:
    out: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+)$", line.strip())
        if m:
            t = m.group(1).strip()
            if t and not t.startswith("#"):
                out.append(t)
            if len(out) >= limit:
                break
    return out


def tokenize(text: str) -> set[str]:
    if not text:
        return set()
    parts = re.findall(r"[\w\u4e00-\u9fff]+", text.lower())
    return {p for p in parts if len(p) > 1 and p not in _STOP}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def heading_sim(h1: list[str], h2: list[str]) -> tuple[float, list[str]]:
    s1 = {normalize_heading(x) for x in h1 if x}
    s2 = {normalize_heading(x) for x in h2 if x}
    if not s1 and not s2:
        return 0.0, []
    inter = sorted(s1 & s2)
    return jaccard(s1, s2), inter


def normalize_heading(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())[:120]


def file_sha256_quick(path: Path, max_bytes: int = 2_000_000) -> str:
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            n += len(chunk)
            if n > max_bytes:
                break
            h.update(chunk)
    return h.hexdigest()


@dataclass
class DocFeat:
    path: str
    size: int
    module_id: str | None
    last_updated: str | None
    title: str
    resp_text: str
    tokens: set[str]
    h2: list[str]
    h2_set: set[str]
    partial_hash: str


def load_feat(repo: Path, rel: str) -> DocFeat | None:
    p = repo / rel
    if not p.is_file():
        return None
    raw = p.read_text(encoding="utf-8", errors="replace")
    fm, body = split_front_matter(raw)
    mid = parse_simple_yaml_field(fm, "module_id")
    lu = parse_simple_yaml_field(fm, "last_updated") or parse_simple_yaml_field(fm, "last_updated_date")
    title = first_markdown_title(body)
    resp = parse_responsibility_block(fm)
    sample = body[:8000]
    blob = f"{title}\n{resp}\n{mid or ''}\n{sample}"
    tokens = tokenize(blob)
    h2l = extract_h2(body)
    h2s = {normalize_heading(x) for x in h2l}
    ph = file_sha256_quick(p)
    return DocFeat(
        path=rel,
        size=len(raw.encode("utf-8")),
        module_id=mid,
        last_updated=lu,
        title=title,
        resp_text=resp,
        tokens=tokens,
        h2=h2l,
        h2_set=h2s,
        partial_hash=ph,
    )


def cabinet_score(path: str) -> int:
    p = path.replace("\\", "/")
    if "/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/" in p:
        return 120
    if "/01_BLUEPRINTS/" in p:
        return 80
    if p.startswith("docs/01_FRAMEWORK/"):
        return 40
    if "/08_HUMAN_AI_INTERFACE/" in p:
        return 20
    if "/10_AI_WORKFLOW/" in p:
        return 20
    if "/06_ARCHIVE/" in p:
        return 5
    return 10


def parse_date_loose(s: str | None) -> tuple[int, int, int] | None:
    if not s:
        return None
    m = re.search(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})", s)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None


def recency_score(lu: str | None) -> float:
    d = parse_date_loose(lu)
    if not d:
        return 0.0
    # 越新略加分；粗算天数自 2020-01-01
    y, mo, da = d
    days = (y - 2020) * 366 + mo * 31 + da
    return min(days / 1000.0, 3.0)


def canonical_preference(a: DocFeat, b: DocFeat) -> tuple[str, str, list[str]]:
    """返回 (canonical_path, other_path, reasons_zh)。"""
    sa = cabinet_score(a.path) + min(a.size, 800_000) / 30_000.0 + recency_score(a.last_updated)
    sb = cabinet_score(b.path) + min(b.size, 800_000) / 30_000.0 + recency_score(b.last_updated)
    reasons: list[str] = []
    if sa >= sb:
        win, lose = a, b
    else:
        win, lose = b, a
        sa, sb = sb, sa
    if "/01_BLUEPRINTS/" in win.path.replace("\\", "/"):
        reasons.append("建议路径含图纸柜 `01_BLUEPRINTS`")
    if win.size > lose.size * 1.15:
        reasons.append("建议正文体量更大（可能更完整）")
    if recency_score(win.last_updated) > recency_score(lose.last_updated) + 0.01:
        reasons.append("建议 front matter 日期更新")
    if not reasons:
        reasons.append("按规则加权分略高（图纸柜/体量/日期）")
    return win.path, lose.path, reasons


def merge_outline_suggestion(canonical: DocFeat, other: DocFeat) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for h in canonical.h2:
        k = normalize_heading(h)
        if k and k not in seen:
            seen.add(k)
            out.append(h)
    for h in other.h2:
        k = normalize_heading(h)
        if k and k not in seen:
            seen.add(k)
            out.append(f"{h}（自另一稿合并时需核对是否重复）")
    if not out:
        return ["（两稿均未解析到 ## 标题；合并时请人工拆章）"]
    return out[:36]


def main() -> int:
    ap = argparse.ArgumentParser(description="D 类蓝图重叠候选（启发式 + 机器建议）")
    ap.add_argument("--date", default=date.today().strftime("%Y%m%d"))
    ap.add_argument("--out-dir", default="docs/09_AUDIT/STATE")
    ap.add_argument("--prefix", default="docs/", help="仅包含此前缀下的路径")
    ap.add_argument(
        "--min-token-jaccard",
        type=float,
        default=0.08,
        help="token Jaccard 软下限（与 --min-score 组合）",
    )
    ap.add_argument(
        "--min-heading-jaccard",
        type=float,
        default=0.10,
        help="H2 归一化集合 Jaccard 软下限",
    )
    ap.add_argument(
        "--min-token-intersection",
        type=int,
        default=36,
        help="token 交集最小规模（防泛泛词）",
    )
    ap.add_argument(
        "--min-score",
        type=float,
        default=0.195,
        help="综合分 = 0.55*token_j + 0.35*heading_j + 0.10*min(1,|∩|/60)；低于此不入表",
    )
    ap.add_argument(
        "--max-output-pairs",
        type=int,
        default=400,
        help="按 score 截断后写入 JSON/MD 的最大候选对数（防超大报表）",
    )
    ap.add_argument("--top", type=int, default=120, help="MD 中展示的候选对数量上限")
    ap.add_argument(
        "--keep-state-overnight",
        action="store_true",
        help="默认排除 overnight_runs；传此参数则纳入",
    )
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    pre = args.prefix.replace("\\", "/")
    if pre and not pre.endswith("/"):
        pre += "/"

    rels = []
    for rel in git_ls_files(repo):
        if pre and not rel.startswith(pre):
            continue
        if not is_blueprint_md(rel):
            continue
        if not args.keep_state_overnight and default_exclude(rel):
            continue
        rels.append(rel)
    rels.sort()

    feats: dict[str, DocFeat] = {}
    for rel in rels:
        f = load_feat(repo, rel)
        if f:
            feats[rel] = f

    paths = sorted(feats.keys())
    candidates: list[dict] = []

    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            a = feats[paths[i]]
            b = feats[paths[j]]
            if a.partial_hash == b.partial_hash:
                continue  # 更像 C1，交给 hash 扫描
            tj = jaccard(a.tokens, b.tokens)
            hj, shared_h = heading_sim(a.h2, b.h2)
            inter_n = len(a.tokens & b.tokens)
            if inter_n < args.min_token_intersection:
                continue
            score = 0.55 * tj + 0.35 * hj + 0.10 * min(1.0, inter_n / 60.0)
            if score < args.min_score:
                continue
            # 双指标不能同时极低（避免仅靠交集规模混入弱相关对）
            if tj < args.min_token_jaccard and hj < args.min_heading_jaccard:
                continue
            can_path, oth_path, reasons = canonical_preference(a, b)
            can_f = a if can_path == a.path else b
            oth_f = b if can_path == a.path else a
            outline = merge_outline_suggestion(can_f, oth_f)
            candidates.append(
                {
                    "path_a": a.path,
                    "path_b": b.path,
                    "score": round(score, 4),
                    "metrics": {
                        "token_jaccard": round(tj, 4),
                        "heading_jaccard": round(hj, 4),
                        "token_intersection": inter_n,
                        "shared_h2": shared_h[:12],
                    },
                    "titles": {"a": a.title[:200], "b": b.title[:200]},
                    "module_ids": {"a": a.module_id, "b": b.module_id},
                    "suggested_canonical": can_path,
                    "suggested_other": oth_path,
                    "suggested_canonical_reasons_zh": reasons,
                    "suggested_merge_outline": outline,
                }
            )

    candidates.sort(key=lambda x: (-x["score"], x["path_a"], x["path_b"]))
    total_before_cap = len(candidates)
    if len(candidates) > args.max_output_pairs:
        candidates = candidates[: args.max_output_pairs]
    capped = total_before_cap > len(candidates)

    out_dir = repo / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_date": args.date,
        "generator": GEN,
        "blueprint_paths_scanned": len(paths),
        "exclude_overnight_runs_default": not args.keep_state_overnight,
        "thresholds": {
            "min_token_jaccard": args.min_token_jaccard,
            "min_heading_jaccard": args.min_heading_jaccard,
            "min_token_intersection": args.min_token_intersection,
            "min_score": args.min_score,
        },
        "candidate_pair_count": len(candidates),
        "candidate_pairs_total_before_cap": total_before_cap,
        "max_output_pairs": args.max_output_pairs,
        "candidates": candidates,
    }
    jpath = out_dir / f"BLUEPRINT_D_OVERLAP_CANDIDATES_{args.date}.json"
    jpath.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cap_note = f"（截断前 {total_before_cap} 对，仅保留 score 最高的 {len(candidates)} 对）" if capped else ""

    md: list[str] = [
        "---",
        "standard_type: audit_state",
        "applicable_scope: D 类蓝图主题重叠候选（启发式）",
        f"generated_date: '{args.date}'",
        f"generated_by: {GEN}",
        "---",
        "",
        "# 蓝图 D 类重叠候选（机器建议 · 非最终裁决）",
        "",
        f"> **机器真源**：[`BLUEPRINT_D_OVERLAP_CANDIDATES_{args.date}.json`](./BLUEPRINT_D_OVERLAP_CANDIDATES_{args.date}.json)",
        f"> **扫描蓝图数**：{len(paths)} ｜ **候选对（写入本文件）**：{len(candidates)}{cap_note}",
        "",
        "## 说明",
        "",
    ]
    if capped:
        md.append(
            f"- **截断**：满足阈值的候选共 **{total_before_cap}** 对，仅保留 score 最高的 **{len(candidates)}** 对（`--max-output-pairs`）；调参见 Playbook §4。"
        )
        md.append("")
    md.extend(
        [
        "- **不是**语义 embedding / LLM；基于 **标题、responsibility、正文抽样、H2 标题** 的 token 与标题集合相似度。",
        "- **建议 canonical** 与 **合并大纲** 为 **规则化启发式**，须经 [D 类蓝图重叠 Playbook](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/D_CLASS_BLUEPRINT_OVERLAP_PLAYBOOK.md) 评审后再改稿。",
        "- 与 **C1（字节相同）** 互补：本脚本跳过 **partial_hash** 全同对（应交给 `scan_duplicate_file_content.py`）。",
        "",
        "## 候选对（按 score 降序，截断展示）",
        "",
        ]
    )

    for idx, row in enumerate(candidates[: args.top], 1):
        md.append(f"### {idx}. score={row['score']}")
        md.append("")
        md.append(f"- **A**: `{row['path_a']}`")
        md.append(f"- **B**: `{row['path_b']}`")
        md.append(f"- **指标**: token_jaccard={row['metrics']['token_jaccard']}, heading_jaccard={row['metrics']['heading_jaccard']}, |∩token|={row['metrics']['token_intersection']}")
        if row["metrics"]["shared_h2"]:
            md.append(f"- **共有 H2（归一化后）**: {', '.join(row['metrics']['shared_h2'][:6])}")
        md.append(f"- **标题**: A「{row['titles']['a'][:80]}…」 / B「{row['titles']['b'][:80]}…」")
        md.append(f"- **建议 canonical**: `{row['suggested_canonical']}`")
        md.append(f"- **理由（机器）**: {'；'.join(row['suggested_canonical_reasons_zh'])}")
        md.append(f"- **另一路径**: `{row['suggested_other']}`（可 stub / archive / 叙事归并）")
        md.append("- **建议合并大纲（H2 草案）**:")
        for line in row["suggested_merge_outline"][:14]:
            md.append(f"  - {line}")
        md.append("")

    if len(candidates) > args.top:
        md.append(f"> 共 {len(candidates)} 对，上文仅展示前 {args.top} 对；详见 JSON。")
        md.append("")

    mpath = out_dir / f"BLUEPRINT_D_OVERLAP_CANDIDATES_{args.date}.md"
    mpath.write_text("\n".join(md), encoding="utf-8")

    print(f"Wrote: {jpath.relative_to(repo)}")
    print(f"Wrote: {mpath.relative_to(repo)}")
    print(
        f"blueprints={len(paths)} written_pairs={len(candidates)} "
        f"total_before_cap={total_before_cap}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
