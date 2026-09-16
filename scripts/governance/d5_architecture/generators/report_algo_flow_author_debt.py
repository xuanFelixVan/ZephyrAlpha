# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §algo_flow_author_debt
# [MODULE] scripts.governance.d5_architecture.generators.report_algo_flow_author_debt
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.externalize_algo_flow（只调 dry_run=True，零写入）; _common.idempotent_timestamp
# [CONSUMERS] P2-1 尾池作者欠账台账（docs/_working/reports/algo_flow_author_debt.md）
# [STARTUP] manual
# [MATURITY] candidate
# [INVARIANTS] 报因三态字符串唯一真源=出仓器常量（_LEGACY_PROSE_SKIP_REASON/_NO_EDGE_SKIP_REASON/
#   _NO_NODES_SKIP_REASON）+ 谓词 _is_content_skip_reason，本文件零重复硬编码；
#   只读分类（externalize(dry_run=True) 全程零写入，本器唯一写盘=--out/--json）；
#   台账绝不静默少报：欠账三类 + resolvable（dryrun/externalized/already）+ other（逐件带报因）
#   = 池总数，恒等式在报告统计区自证；池来源=--file-list 传入即如实报传入的池，
#   或 --scan-pool 现扫（AGENTS.md §9 第 5 条：清单必由生成器产出，手工清单必漂移）；
#   时间源走 idempotent_timestamp（GATE-GEN-NO-REALTIME-TIME：生成器禁实时时钟）；
#   域分组键=src/zephyr/<domain>/ 的 path 段 2（根层件 src/zephyr/<mod>.py 归 (root)）
# [MODIFY-GUARD] 无
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reporter 非 gate：成功出报告即 exit 0；单件异常/缺件归 other 桶不中断；
#   仅清单/输出路径不可用时 exit 1；恒打印一行 AUTHOR_DEBT total=… 摘要
# [TESTS] tests/governance/generators/test_report_algo_flow_author_debt.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的台账生成器（Owner 授权批次的静态清单产出，非常驻服务）
"""report_algo_flow_author_debt.py — ALGO_FLOW 出仓"作者欠账"台账生成器（P2-1 尾池）。

尾池里工具当场做不动的那半，欠的不是几何而是作者语义：补节点/补边=替作者臆造算法，
伪造的边会把一张错误的图渲染成"已验证"的全景图（且 ALGO-FLOW-LINK 门禁本来就拦零边
镜像）。所以这些件的正确处置是**登记**而不是硬出仓。按 §9.5"条目列表+计数"类清单必由
生成器产出，本器把出仓器 dry-run 的诚实报因分成三态落账：

  1. legacy 五段式 prose（欠 ``# - id:`` 机器块行）→ 按口径补机器块；
  2. graph has no edges（validate_graph 必拦）→ 欠边，须作者补；
  3. block unparsable (no nodes) → 欠逐件诊断。

判据不另起炉灶：报因字符串与"内容级欠账"谓词全部 import 自出仓器（``externalize_algo_flow``），
分类只跑 ``externalize(path, dry_run=True)``（零写入路径），因此台账与工具行为永不脱钩。

用法::

    python scripts/governance/d5_architecture/generators/report_algo_flow_author_debt.py \
        --file-list .runtime/tmp/bt_tail_files.txt --out .runtime/tmp/bt_author_debt_report.md
    python .../report_algo_flow_author_debt.py --scan-pool          # 现扫全仓内联块（无手工清单）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

__manifest__ = """
args: []
description: 'ALGO_FLOW 出仓作者欠账台账生成器（P2-1 尾池三态分家，零写入分类）'
dimensions:
- D5
priority: P2
timeout_seconds: 120
warn_only: false
"""

_THIS_FILE = Path(__file__).resolve()
_GEN_DIR = str(_THIS_FILE.parent)
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
for _p in (_GOV_DIR, _GEN_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import externalize_algo_flow as ext  # noqa: E402  # noqa: import-integrity  import-integrity豁免: 生成器同目录件，运行时 sys.path 注入后静态分析不可解析
from _common import idempotent_date, idempotent_timestamp  # noqa: E402  # noqa: import-integrity  import-integrity豁免: 生成器共享前缀件，经上一行 sys.path 注入动态加载
from _shared.code_algorithm_extractor import _has_inline_algo_flow  # noqa: E402

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# 出仓器的报因真源（禁在本文件重复字面量——改写措辞即让台账与工具脱钩）
_LEGACY_PROSE = ext._LEGACY_PROSE_SKIP_REASON
_NO_EDGES = ext._NO_EDGE_SKIP_REASON
_NO_NODES = ext._NO_NODES_SKIP_REASON

# 三态欠账：(桶键, 类名, 派工口径, 报因真源)——桶键+报因进 JSON，类名/口径进人读报告
DEBT_CLASSES: tuple[tuple[str, str, str, str], ...] = (
    ("prose", "五段式散文（欠机器块行）", "按五段式口径补 `- id:` 机器块行后重跑本批", _LEGACY_PROSE),
    ("no_edges", "零边图（欠边）", "补边须作者裁定语义，禁工具臆造（伪造边=错图冒充已验证）", _NO_EDGES),
    ("no_nodes", "块不可解析（零节点）", "逐件诊断块形，能补则补、该删则删（须作者确认）", _NO_NODES),
)
DEBT_KEYS = tuple(k for k, _n, _d, _r in DEBT_CLASSES)

# 非欠账：工具当场能机械出仓（含幂等复跑的已出仓件）
_RESOLVABLE_STATUSES = ("dryrun", "externalized", "already")
_RESOLVABLE_LABELS = {"dryrun": "待出仓", "externalized": "本批可出仓", "already": "已出仓"}

_ROOT_GROUP = "(root)"
_GENERATED_MARKER = "<!-- GENERATED — do not hand-edit -->"
DEFAULT_OUT = "docs/_working/reports/algo_flow_author_debt.md"


def _rel_of(path: Path, root: Path) -> str:
    """仓库根相对 posix 路径（越界件回落绝对路径，绝不抛——报不出=静默少报）。

    先按原样 ``relative_to``（调用方给的 root 拼写优先，pytest tmp_path 场景不受
    符号链接/短名解析差异干扰），再试 resolve 后比对，最后才落绝对路径。
    """
    for cand in (path, path.resolve()):
        try:
            return cand.relative_to(root).as_posix()
        except ValueError:
            continue
    return path.as_posix()


def _group_key(rel: str) -> str:
    """域分组键：``src/zephyr/<domain>/...`` 取段 2；根层件与仓外件另立桶。"""
    parts = rel.replace("\\", "/").split("/")
    if parts[:2] == ["src", "zephyr"]:
        return parts[2] if len(parts) > 3 else _ROOT_GROUP
    return "/".join(parts[:-1]) or _ROOT_GROUP


def _class_of(status: str, reason: str) -> str:
    """(status, reason) → 桶键：三态欠账优先，其次可机械出仓，其余落 other。

    欠账判据走出仓器谓词 ``_is_content_skip_reason``（内容级 vs 几何级），再按报因
    真源定具体桶——``promoted_inline``（契约头转正后留在 docstring 的不可解析块）同样
    计入欠账，否则该族会从台账里凭空消失。
    """
    if ext._is_content_skip_reason(reason):
        for key, _name, _dispatch, needle in DEBT_CLASSES:
            if needle in reason:
                return key
    if status in _RESOLVABLE_STATUSES:
        return "resolvable"
    return "other"


def classify_entry(path: Path, root: Path) -> dict:
    """单件分类：跑 ``externalize(dry_run=True)``（零写入）后归桶，异常/缺件不中断。"""
    rel = _rel_of(path, root)
    entry: dict = {"file": rel, "group": _group_key(rel), "status": "", "reason": "", "class": "other", "yaml": ""}
    if not path.is_file():
        entry["status"] = "missing"
        entry["reason"] = "清单条目在盘上不存在（清单与盘已脱钩，须重取池）"
        return entry
    try:
        res = ext.externalize(path, dry_run=True)
    except Exception as e:  # noqa: BLE001 — 单件异常归 other，绝不让台账少报一件
        entry["status"] = "error"
        entry["reason"] = f"{type(e).__name__}: {e}"
        return entry
    entry["status"] = str(res.get("status", ""))
    entry["reason"] = str(res.get("reason", "") or res.get("plan", ""))
    entry["class"] = _class_of(entry["status"], entry["reason"])
    if res.get("yaml"):
        entry["yaml"] = str(res["yaml"])
    return entry


def classify_pool(paths: list[Path], root: Path | str = REPO_ROOT) -> dict:
    """按传入的池逐件分类，返回 {pool, counts, entries}（本器唯一读盘+判桶入口）。

    出仓器按 ``REPO_ROOT`` 做 ``relative_to`` 与落点读盘，故此处临时改指 ``root``
    （含 tmp 假仓库，测试因此不依赖真实仓库布局），跑完原样还原。
    """
    root = Path(root)
    targets = [p if Path(p).is_absolute() else root / str(p).replace("\\", "/") for p in paths]
    prev = ext.REPO_ROOT
    if Path(prev) != root:
        ext.REPO_ROOT = root
    try:
        entries = [classify_entry(p, root) for p in targets]
    finally:
        ext.REPO_ROOT = prev
    counts: dict[str, int] = {k: 0 for k in DEBT_KEYS}
    counts.update({"resolvable": 0, "other": 0, "debt_total": 0, "pool": len(entries), "total": len(entries)})
    for e in entries:
        counts[e["class"]] = counts.get(e["class"], 0) + 1
    counts["debt_total"] = sum(counts[k] for k in DEBT_KEYS)
    return {"pool": len(entries), "counts": counts, "entries": entries, "root": root.as_posix()}


def read_file_list(list_path: Path, root: Path) -> list[Path]:
    """池清单：每行一个仓库根相对 ``src/zephyr/...py``（绝对行也接受，# 注释/空行忽略）。"""
    out: list[Path] = []
    for ln in Path(list_path).read_text(encoding="utf-8").splitlines():
        s = ln.strip().replace("\\", "/")
        if not s or s.startswith("#"):
            continue
        p = Path(s)
        out.append(p if p.is_absolute() else root / s)
    return out


def scan_inline_pool(root: Path | str = REPO_ROOT) -> list[Path]:
    """现扫池：src/zephyr 下"仍有内联块且无 external 锚"的件（无手工清单时的真源）。

    枚举复用出仓器 ``_iter_targets`` 的目录过滤口径（__pycache__/tests/_archive），
    不另写一套 walker。
    """
    root = Path(root)
    prev = ext.REPO_ROOT
    if Path(prev) != root:
        ext.REPO_ROOT = root
    try:
        out: list[Path] = []
        for p in ext._iter_targets(None, None):
            try:
                src = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if ext._ANCHOR_RE.search(src):
                continue
            if _has_inline_algo_flow(ext._module_docstring(src)):
                out.append(p)
    finally:
        ext.REPO_ROOT = prev
    return out


def _grouped_lines(entries: list[dict]) -> list[str]:
    """按域分组的 ``- path`` 清单（域内计数、域间按件数降序、同数按域名升序，确定性）。"""
    by_group: dict[str, list[dict]] = {}
    for e in entries:
        by_group.setdefault(e["group"], []).append(e)
    lines: list[str] = []
    for grp, items in sorted(by_group.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        lines.append(f"### {grp}（{len(items)} 件）")
        lines.append("")
        for e in sorted(items, key=lambda x: x["file"]):
            suffix = f" —— {e['reason']}" if e["class"] == "other" else ""
            lines.append(f"- `{e['file']}`{suffix}")
        lines.append("")
    return lines


def _frontmatter() -> list[str]:
    """YAML frontmatter——docs/_working/ 是 directory_contract 的 temporary 区，
    .md 无 frontmatter 即 TTL-METADATA 硬拦（doc_type 临时区不要求，故不写）。

    字段口径与 docs/_working/reports/ 既有报告一致（ttl + date），另附生成器溯源对；
    两个时间源都是幂等的（脚本最近 commit → 相同 commit 相同输出）。
    """
    return [
        "---",
        "ttl: task_bound",
        f"date: {idempotent_date(_THIS_FILE)}",
        f"generated_at: {idempotent_timestamp(_THIS_FILE)}",
        f"generated_by: {_rel_of(_THIS_FILE, REPO_ROOT)}",
        "---",
        "",
    ]


def render_report(cls: dict, *, source: str) -> str:
    """分类结果 → markdown 台账（纯函数，便于测试直接喂桶）。"""
    counts = cls["counts"]
    entries = cls["entries"]
    lines: list[str] = [*_frontmatter(), _GENERATED_MARKER, ""]
    lines += [
        "# ALGO_FLOW 出仓作者欠账台账（P2-1 尾池）",
        "",
        "> 本文由 `scripts/governance/d5_architecture/generators/report_algo_flow_author_debt.py` 生成，勿手改"
        "（AGENTS.md §9 第 5 条：静态清单必由生成器产出）。",
        "> 时间源：`idempotent_timestamp`（本脚本最近 git commit 时间，相同 commit→相同输出）。",
        f"> 池来源：{source}；判据：`externalize(dry_run=True)`（零写入）的 skipped 报因。",
        "> 欠账=补节点/补边即臆造算法语义，禁工具代做（伪造边会把错图渲染成「已验证」全景图）。",
        "",
        "## 统计",
        "",
        "| 类 | 件数 | 报因真源（出仓器常量，勿改写） | 后续派工口径 |",
        "|------|:---:|------|------|",
    ]
    for key, name, dispatch, needle in DEBT_CLASSES:
        lines.append(f"| {name} | {counts.get(key, 0)} | `{needle}` | {dispatch} |")
    lines += [
        f"| **作者欠账合计** | **{counts.get('debt_total', 0)}** | — | 本台账的账 |",
        f"| 可机械出仓（dry-run 判可动） | {counts.get('resolvable', 0)} | — | 归出仓批，非欠账 |",
        f"| 其他（须逐件看报因） | {counts.get('other', 0)} | — | 几何/定位类，非内容欠账 |",
        f"| 池总数 | {counts.get('pool', 0)} | — | 恒等式：欠账+可机械+其他=池总数 |",
        "",
    ]
    by_status: dict[str, int] = {}
    for e in entries:
        by_status[e["status"]] = by_status.get(e["status"], 0) + 1
    lines += ["状态分布：" + "、".join(f"{s}={n}" for s, n in sorted(by_status.items())), ""]

    for key, name, dispatch, needle in DEBT_CLASSES:
        items = [e for e in entries if e["class"] == key]
        lines += [f"## {name}（{len(items)} 件）", "", f"报因：`{needle}`", f"派工：{dispatch}", ""]
        if not items:
            lines += ["（无）", ""]
            continue
        lines += _grouped_lines(items)

    resolvable = [e for e in entries if e["class"] == "resolvable"]
    lines += [f"## 可机械出仓（{len(resolvable)} 件，非欠账，登记防漏）", ""]
    if resolvable:
        tally: dict[str, int] = {}
        for e in resolvable:
            tally[e["status"]] = tally.get(e["status"], 0) + 1
        lines += [
            "构成：" + "、".join(
                f"{_RESOLVABLE_LABELS.get(s, s)}（{s}）={n}" for s, n in sorted(tally.items())
            ),
            "",
        ]
    lines += _grouped_lines(resolvable) if resolvable else ["（无）", ""]

    other = [e for e in entries if e["class"] == "other"]
    lines += [f"## 其他报因（{len(other)} 件，逐件诊断）", ""]
    lines += _grouped_lines(other) if other else ["（无）", ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def summary_line(counts: dict) -> str:
    """一行摘要（AUTHOR_DEBT total=… prose=… no_edges=… no_nodes=… resolvable=…）。"""
    return (
        f"AUTHOR_DEBT total={counts.get('debt_total', 0)} "
        f"prose={counts.get('prose', 0)} no_edges={counts.get('no_edges', 0)} "
        f"no_nodes={counts.get('no_nodes', 0)} resolvable={counts.get('resolvable', 0)}"
    )


def _parse(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ALGO_FLOW 出仓作者欠账台账生成器（P2-1 尾池，reporter 非 gate）"
    )
    parser.add_argument("--file-list", dest="file_list", help="池清单：每行一个仓库根相对 .py 路径")
    parser.add_argument(
        "--scan-pool",
        action="store_true",
        help="无清单时现扫 src/zephyr 内联块（缺省行为：--file-list 未给即走此路）",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"markdown 输出（默认 {DEFAULT_OUT}）")
    parser.add_argument("--json", dest="json_out", default="", help="机读孪生文件（可选）")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse(argv)
    try:
        if args.file_list:
            list_path = Path(args.file_list)
            if not list_path.is_absolute():
                list_path = REPO_ROOT / str(list_path).replace("\\", "/")
            paths = read_file_list(list_path, REPO_ROOT)
            source = f"`--file-list {_rel_of(list_path, REPO_ROOT)}`（{len(paths)} 件，如实报传入的池）"
        else:
            paths = scan_inline_pool(REPO_ROOT)
            source = "`--scan-pool`（现扫 src/zephyr 内联块，无手工清单）"
        cls = classify_pool(paths, REPO_ROOT)
    except OSError as e:
        print(f"[ERROR] 无法读取池清单：{type(e).__name__}: {e}")
        return 1

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / str(args.out).replace("\\", "/")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = render_report(cls, source=source)
    out_path.write_text(md, encoding="utf-8", newline="\n")
    if args.json_out:
        json_path = Path(args.json_out)
        if not json_path.is_absolute():
            json_path = REPO_ROOT / str(args.json_out).replace("\\", "/")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_by": _rel_of(_THIS_FILE, REPO_ROOT),
            "generated_at": idempotent_timestamp(_THIS_FILE),
            "source": source,
            "counts": cls["counts"],
            "debt_classes": {
                k: {"name": n, "dispatch": d, "skip_reason": r} for k, n, d, r in DEBT_CLASSES
            },
            "entries": cls["entries"],
        }
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
        )
    print(summary_line(cls["counts"]))
    print(f"[OK] 台账 → {_rel_of(out_path, REPO_ROOT)}（池 {cls['counts']['pool']} 件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
