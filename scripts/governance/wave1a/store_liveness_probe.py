#!/usr/bin/env python
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
# [STARTUP] manual
#   （原值 on_demand： 由总包在波 1A.5 落地窗口与事故复盘时手工执行（python scripts/governance/wave1a/store_liveness_probe.py）——GATE-VOCAB 词表归正 manual）
# [CONSUMERS] docs/_working/total_command_closeout/wave1a/dead_store_triage.md §1（本案卷表）; 波 1A.5 出口判据尺; 后续周审计可复用
# [MODULE] module_id=MOD-GOV-wave1a-store_liveness_probe | layer=script | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(pathlib/subprocess/json/re/datetime)；yaml
# [MATURITY] draft
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 外部依赖失败必抛并点名，禁把异常吞成空值/空表（假绿源）
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
"""死库与死指针普查器（波 1A.5 / W-180 前置）。

大白话：把仓库 data/ 下每个"打不开、没内容、或长期没人写"的 .db 拖出来晒一遍，
逐个给出四列证据——**字节数 / 被多少 .py 引用 / 有无活替代 / 消费者数**——
再按内收判据（w5_1：零触发零消费→退役；同真源可派生→必并）给三态处置建议：
`revive`（复活）/ `repoint`（改指活库）/ `retire`（退役）。

设计约束：
- **只读**：全程不写生产路径、不连任何数据库、不 import zephyr（可在裸 Python 下跑）。
- 引用面（ref_py）＝ .py 文本提到该库文件名或路径的文件数；
  消费者数（consumer_py）＝ 其中在提及行 ±8 行内出现真实读写动作（connect/execute/query/
  count/sqlite3/duckdb/psycopg）的文件数——"被提到"不等于"被用"，trae_034 型死指针就藏在这差里。
- 活替代＝同 stem（文件名去掉 .db）的其他 .db 且 size>0；跨后端替代（如 depgraph 已迁
  Postgres）由 §案卷人工判词补，尺本身只报文件面证据。
输出：stdout/markdown 表 + jsonl 逐条记录（禁手改，重跑覆盖）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# 真实读写动作标记（消费者判定）
_USE_PATTERN = re.compile(
    r"(duckdb\.connect|sqlite3\.connect|psycopg2?\.connect|get_governance_conn|"
    r"get_depgraph_conn|get_clickhouse_conn|\.execute\(|\.executemany\(|\.sql\(|"
    r"\.query\(|\.count\(|read_sql|to_sql|cursor\()",
    re.IGNORECASE,
)
# 非活体标记：注释/docstring 里的提及单独计，不混进引用面
_COMMENT_PREFIX = ("#", "//")
_ANY_DB_RE = re.compile(r"([\w.\-]+\.db)\b")
STALE_DAYS_DEFAULT = 45
_TEXT_CACHE: dict[str, tuple[float, str]] = {}


def _read_text_cached(path: Path) -> str | None:
    """文件文本缓存（同一次普查多库共用盘面，避免反复 IO）。"""
    key = str(path)
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    hit = _TEXT_CACHE.get(key)
    if hit and hit[0] == mtime:
        return hit[1]
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    _TEXT_CACHE[key] = (mtime, text)
    return text


@dataclass
class StoreRecord:
    path: str
    size_bytes: int
    mtime: str
    stale_days: float
    suspicious: bool
    ref_py: int = 0
    ref_py_path_qualified: int = 0
    consumer_py: int = 0
    ref_files_sample: list[str] = field(default_factory=list)
    path_ptr_files_sample: list[str] = field(default_factory=list)
    consumer_files_sample: list[str] = field(default_factory=list)
    ref_rule_yaml: int = 0
    rule_files: list[str] = field(default_factory=list)
    ref_other: int = 0
    live_alternatives: list[dict] = field(default_factory=list)
    successor_candidates: list[str] = field(default_factory=list)
    disposition: str = ""
    reason: str = ""


def _repo_rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(p).replace("\\", "/")


def _iter_text_files(root: Path, subdirs: tuple[str, ...], suffixes: tuple[str, ...]):
    for sub in subdirs:
        base = root / sub
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in suffixes:
                continue
            parts = set(p.parts)
            if {"__pycache__", ".git", "node_modules", ".mypy_cache"} & parts:
                continue
            yield p


_TOKEN_RE_CACHE: dict[str, re.Pattern] = {}


def _token_regex(filename: str) -> re.Pattern:
    """匹配 <可选目录前缀>/<filename>，用于区分"带路径的真指针"与"裸文件名提及"."""
    rx = _TOKEN_RE_CACHE.get(filename)
    if rx is None:
        rx = re.compile(r"(?:[\w.\-]+[/\\])*" + re.escape(filename))
        _TOKEN_RE_CACHE[filename] = rx
    return rx


def _scan_references(filename: str, parent_dir: str, root: Path) -> dict:
    """扫全仓 .py/.yaml/.md/.ps1 对该库的提及，区分"提及 / 消费 / 带路径真指针"."""
    refs: set[str] = set()  # .py 提及（裸文件名或带路径）
    consumers: set[str] = set()  # .py 提及且邻近有真实读写动作
    path_ptrs: set[str] = set()  # 带目录前缀、且前缀尾段 == 本库所在目录 ⇒ 指向本库而非同名他库
    rule_files: set[str] = set()
    other: set[str] = set()
    co_named_map: dict[str, list[str]] = {}
    patterns = {
        ".py": ("src", "scripts", "tools"),
        ".yaml": ("docs", "config", "data", "schemas"),
        ".yml": ("docs", "config", "data", "schemas"),
        ".md": ("docs",),
        ".ps1": ("scripts",),
    }
    rx = _token_regex(filename)
    for suffix, dirs in patterns.items():
        for path in _iter_text_files(root, dirs, (suffix,)):
            text = _read_text_cached(path)
            if text is None or filename not in text:
                continue
            rel = _repo_rel(path, root)
            lines = text.splitlines()
            hit_lines = [i for i, ln in enumerate(lines) if rx.search(ln)]
            if not hit_lines:
                continue
            qualified = False
            for m in rx.finditer(text):
                prefix = m.group(0)[: -len(filename)].rstrip("/\\")
                if prefix and re.split(r"[/\\\\]", prefix)[-1] == parent_dir:
                    qualified = True
                    break
            real_code = False
            co_named: set[str] = set()
            for i in hit_lines:
                lo, hi = max(0, i - 8), min(len(lines), i + 9)
                window = "\n".join(lines[lo:hi])
                if _USE_PATTERN.search(window):
                    real_code = True
                # 同行共现的其他 .db ＝"活替代/后继库"声明面证据（如
                # "SqliteAdapter 读取 governance.db（zalpha_metadata.db）"）
                for m in _ANY_DB_RE.finditer(lines[i]):
                    name = m.group(1)
                    if name != filename:
                        co_named.add(name)
            if suffix == ".py":
                if real_code:
                    consumers.add(rel)
                refs.add(rel)
                if qualified:
                    path_ptrs.add(rel)
                co_named_map[rel] = sorted(co_named)
            elif suffix in (".yaml", ".yml") and rel.startswith("docs/01_policies_and_standards/rules/"):
                rule_files.add(rel)
            else:
                other.add(rel)
    return {
        "ref_py_files": sorted(refs),
        "consumer_py_files": sorted(consumers),
        "path_ptr_py_files": sorted(path_ptrs),
        "co_named": co_named_map,
        "rule_files": sorted(rule_files),
        "other_files": sorted(other),
    }


def scan(root: Path, live_root: Path, stale_days: float) -> list[StoreRecord]:
    now = time.time()
    data_dir = live_root / "data"
    if not data_dir.exists():
        raise SystemExit(f"[FATAL] 数据盘目录不存在：{data_dir}（禁猜路径，请用 --live-root 指真盘面）")
    dbs = [p for p in data_dir.rglob("*.db") if p.is_file()]
    dbs += [p for p in (root / "data").rglob("*.db") if p.is_file()] if (root / "data").exists() else []
    # 去重（lane 与 live 同路径时）
    seen: dict[str, Path] = {}
    for p in dbs:
        key = str(p.resolve()).lower()
        seen.setdefault(key, p)

    # 活替代总表：所有 size>0 的 .db（含车道外真盘面）
    alive_by_stem: dict[str, list[Path]] = {}
    for p in seen.values():
        try:
            if p.stat().st_size > 0:
                alive_by_stem.setdefault(p.stem, []).append(p)
        except OSError:
            continue

    # 同名索引（供"共现后继"判定用）：db 文件名 -> 盘面上最大的那份及其字节数
    by_name: dict[str, tuple[Path, int]] = {}
    for key2, p2 in seen.items():
        try:
            s2 = p2.stat().st_size
        except OSError:
            continue
        cur = by_name.get(p2.name)
        if cur is None or s2 > cur[1]:
            by_name[p2.name] = (p2, s2)

    records: list[StoreRecord] = []
    for key in sorted(seen):
        p = seen[key]
        try:
            st = p.stat()
        except OSError as e:  # 读不到元数据＝本身即事故证据，显式报出
            print(f"[WARN] stat 失败 {key}: {e}", file=sys.stderr)
            continue
        stale = (now - st.st_mtime) / 86400.0
        suspicious = st.st_size == 0 or (st.st_size < 4096 and stale > stale_days)
        if not suspicious:
            continue
        rec = StoreRecord(
            path=_repo_rel(p, live_root if str(p).lower().startswith(str(live_root).lower()) else root),
            size_bytes=st.st_size,
            mtime=time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime)),
            stale_days=round(stale, 1),
            suspicious=True,
        )
        scan_root = root if (root / "src").exists() else live_root
        hits = _scan_references(p.name, p.parent.name, scan_root)
        rec.ref_py = len(hits["ref_py_files"])
        rec.ref_py_path_qualified = len(hits["path_ptr_py_files"])
        rec.consumer_py = len(hits["consumer_py_files"])
        rec.ref_files_sample = hits["ref_py_files"][:12]
        rec.path_ptr_files_sample = hits["path_ptr_py_files"][:12]
        rec.consumer_files_sample = hits["consumer_py_files"][:12]
        rec.rule_files = hits["rule_files"]
        rec.ref_rule_yaml = len(hits["rule_files"])
        rec.ref_other = len(hits["other_files"])
        alts = []
        for alt in alive_by_stem.get(p.stem, []):
            if str(alt).lower() == key:
                continue
            try:
                ast = alt.stat()
            except OSError:
                continue
            if ast.st_size <= 0:
                continue
            alts.append(
                {
                    "path": _repo_rel(alt, live_root),
                    "size_bytes": ast.st_size,
                    "mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(ast.st_mtime)),
                }
            )
        rec.live_alternatives = sorted(alts, key=lambda d: -d["size_bytes"])[:5]
        co: set[str] = set()
        for names in hits["co_named"].values():
            co.update(names)
        rec.successor_candidates = sorted(
            n for n in co if n in by_name and by_name[n][1] > 0 and _repo_rel(by_name[n][0], live_root) != rec.path
        )[:6]
        rec.disposition, rec.reason = decide(rec)
        records.append(rec)
    return records


def decide(rec: StoreRecord) -> tuple[str, str]:
    """三态处置建议（内收判据 w5_1，仅建议不裁定）."""
    succ = ""
    if rec.live_alternatives:
        succ = rec.live_alternatives[0]["path"]
    elif rec.successor_candidates:
        succ = rec.successor_candidates[0]
    if rec.consumer_py == 0 and rec.ref_rule_yaml == 0:
        return "retire", "零消费者 + 零规则指向（声明面与消费面双空）⇒ 内收判据'零触发零消费→退役'"
    if rec.consumer_py == 0 and rec.ref_rule_yaml > 0:
        return (
            "retire_or_repoint",
            f"规则册明文指向（{rec.ref_rule_yaml} 册）但零代码消费者 ⇒ 纯死指针：优先改指活库，"
            "无活库则该规则条退役——规则与代码必须同批改，禁留死指针",
        )
    if succ:
        extra = "；规则册亦指向本库 ⇒ 规则与代码同批" if rec.ref_rule_yaml else ""
        return ("repoint", f"{rec.consumer_py} 个真实消费者 + 存在活替代/共现后继 `{succ}` ⇒ 改指活库{extra}")
    return (
        "revive",
        f"{rec.consumer_py} 个真实消费者且盘面无可指活替代 ⇒ 复活（重建 schema+回灌），"
        "或裁定改用其他后端（如已迁 Postgres/duckdb 的域）",
    )


def to_markdown(recs: list[StoreRecord], generated_at: str) -> str:
    out = [
        "<!-- 本表由 scripts/governance/wave1a/store_liveness_probe.py 机生，禁手改（重跑覆盖） -->",
        f"<!-- generated_at={generated_at} -->",
        "",
        "| 库（rel path） | 字节数 | mtime | .py 引用数（带路径真指针数） | 真实消费者数 | 规则册指向数 | 规则册样例 | 活替代（同 stem 最大件） | 共现后继（同行点名） | 三态建议 | 判据 |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in recs:
        alt = "无"
        if r.live_alternatives:
            a = r.live_alternatives[0]
            alt = f"{a['path']} ({a['size_bytes']:,}B @{a['mtime']})"
        succ = ", ".join(f"`{s}`" for s in r.successor_candidates) or "无"
        rules = ", ".join(Path(x).name for x in r.rule_files[:4])
        if len(r.rule_files) > 4:
            rules += f" …(+{len(r.rule_files) - 4})"
        rules = rules or "无"
        out.append(
            f"| `{r.path}` | {r.size_bytes:,} | {r.mtime} | {r.ref_py}（{r.ref_py_path_qualified}） | "
            f"{r.consumer_py} | {r.ref_rule_yaml} | {rules} | {alt} | {succ} | **{r.disposition}** | {r.reason} |"
        )
    out.append("")
    out.append(f"合计可疑库 {len(recs)} 个；其中 0 字节 {sum(1 for r in recs if r.size_bytes == 0)} 个。")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="波 1A.5 死库普查器（只读）")
    ap.add_argument("--root", default=None, help="代码扫描根（默认=本脚本所在车道根）")
    ap.add_argument("--live-root", default=None, help="真盘面根（数据目录所在，默认=--root）")
    ap.add_argument("--stale-days", type=float, default=STALE_DAYS_DEFAULT, help="非 0 字节但 N 天未写的库也算可疑")
    ap.add_argument("--out-md", default=None)
    ap.add_argument("--out-jsonl", default=None)
    ap.add_argument("--json", action="store_true", help="stdout 出 JSON（默认可读表）")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]
    live_root = Path(args.live_root).resolve() if args.live_root else root
    recs = scan(root, live_root, args.stale_days)
    generated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if args.out_jsonl:
        p = Path(args.out_jsonl)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("".join(json.dumps(asdict(r), ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
    if args.out_md:
        p = Path(args.out_md)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(to_markdown(recs, generated_at), encoding="utf-8")

    if args.json:
        print(json.dumps([asdict(r) for r in recs], ensure_ascii=False, indent=2))
    else:
        print(to_markdown(recs, generated_at))
    # 尺必须能红：仍有 0 字节库 ⇒ 退出码 1（出口判据"0 字节库数→0"未达）
    zero = [r for r in recs if r.size_bytes == 0]
    if zero:
        print(f"[RED] 仍有 {len(zero)} 个 0 字节库未处置（波 1A.5 出口判据未达）", file=sys.stderr)
        return 1
    print("[GREEN] 0 字节库已清零（复活或退役）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
