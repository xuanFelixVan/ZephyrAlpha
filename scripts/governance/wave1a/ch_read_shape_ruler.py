#!/usr/bin/env python
# [TTL] task_bound
# [STARTUP] on_demand: 施工/审计/落地窗口手工跑；升 gate 后由 commit 门禁按 own-diff 触发（本尺自身不注册 gate）
# [CONSUMERS] docs/_working/total_command_closeout/wave1a/dead_store_triage.md §3（违规清单）; 后续 W-180.2 gate 注册时的判据函数原型; tests/governance/test_wave1a_query_shape_ruler.py
# [MODULE] module_id=MOD-GOV-wave1a-ch_read_shape_ruler | layer=script | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(pathlib/subprocess/json/re/datetime)；yaml
# [MATURITY] draft
# [PORT-NOTE] 2026-09-29 W-180 落地批 st-nightsweep-sw4-20260929 自 aidrafts st-final-build-20260926 原样移植（尺为脚本原型，自身不注册 gate——卡面"commit_gates 下扫描尺"系猜测位，按其自带设计落 scripts/governance/wave1a/）
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 外部依赖失败必抛并点名，禁把异常吞成空值/空表（假绿源）
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# create-guard-not-dup: CH 读通道查询形状量尺（wave1a 严格读判据的 AST 扫描尺，测试靶件）；与 runtime_llm_call_interceptor（LLM 防御拦截器）无同源关系，关键词命中系"读/拦截"字面泛化
"""CH 字符串读接口"形状违约"静态尺（W-180.2）。

大白话：`ch_reader.query()` / `ch_writer.query()` / `query_table()` 返回的是 **TSV 字符串**。
对它 `r[0][0]` 取到的是"首行首字符"（467 读成 4）、`for r in it` 迭代的是**字符**——
2026-09-26 终审卷 §7.1 的 P1/P2 两个病样本都源于此。本尺把 HEAD 树（或指定文件）里
这类调用点全部扫出来，按"判据路径 / 非判据路径"分级，**尺必须能红**。

三类模式：
  S1 DIRECT_SUBSCRIPT  `…​.query(...)[0]` / `[0][0]` / `[-1]`         —— 字符串下标＝首位数字假象
  S2 FOR_IN_CALL       `for x in ….query(...)`                        —— 字符串逐字符迭代
  S3 VAR_USE           `t = ….query(...)` 后 `t[<数字>]` 或 `for x in t` —— 同一违约换个写法

分级：命中文件在判据面（scripts/ 下审计/核查/尺/探针/对账类、docs/_working 案卷、
gate/governance 路径）⇒ `JUDGMENT`（硬红，W-180 红线）；其余 ⇒ `NON_JUDGMENT`（软红，须改但不阻断）。

内收声明：本尺是 W-180.2 的判据函数原型，**不另立第 N 个扫描器**——后续升 gate 时
直接 import 本文件的 `scan_text()`，不复制规则。

用法：
    python scripts/governance/wave1a/ch_read_shape_ruler.py --root <lane>            # 扫 HEAD 树
    python scripts/governance/wave1a/ch_read_shape_ruler.py --files a.py b.py        # 扫指定文件（canary 用）
    ... --out-md <path> --out-jsonl <path>
退出码：0＝零命中；1＝有 JUDGMENT 命中（硬红）；2＝仅 NON_JUDGMENT（--strict 时亦为红）
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# 字符串读接口（严格通道 query_rows/query_rows_table/count_strict 不在此列——它们返回 list[int]）
_STR_READER_RX = re.compile(
    r"(?:ch_reader|ch_writer|reader|writer|creader|cwriter)\s*\.\s*"
    r"(?P<fn>query|query_table)\s*\((?:[^()\n]|\((?:[^()\n])*\))*\)"
)
# 裸符号导入（`from zephyr.data.ch_reader import query`）后不带接收者的调用——同一违约面，
# 接收者前缀写不出来，只能按"本文件确实导入过字符串读接口"开第二把正则
_BARE_IMPORT_RX = re.compile(r"from\s+zephyr\.data\.ch_reader\s+import[^\n]*\bquery\b")
_STR_READER_BARE_RX = re.compile(r"(?<![\w.])(?P<fn>query|query_table)\s*\((?:[^()\n]|\((?:[^()\n])*\))*\)")
_SUBSCRIPT_RX = re.compile(r"^\s*(?P<idx>\[\s*-?\d+\s*\](\s*\[\s*-?\d+\s*\])?)")
_FOR_ASSIGN_RX = re.compile(r"^\s*for\s+(?P<targets>[\w()\s,]+?)\s+in\s+(?P<name>[A-Za-z_]\w*)\s*:?\s*(?:#.*)?$")
_ASSIGN_RX = re.compile(r"^\s*(?P<name>[A-Za-z_]\w*)\s*=\s*")
_INDEX_AFTER_ASSIGN_RX = re.compile(r"\b(?P<name>\w+)\s*\[\s*-?\d+\s*\]")

# 判据面路径特征（W-180 红线适用范围）
_JUDGMENT_PATH_RX = re.compile(
    r"(^|/)(governance|audit|gates?|closeout)(/|_)|"
    r"(^|/)[\w.\-]*(check|audit|verify|probe|ruler|scan|reconcil|triage|clos|report|guard)[\w.\-]*\.py$"
)
# 豁免面：严格通道实现本体、测试、归档件（尺对它们只作 INFO）
_EXEMPT_RX = re.compile(r"(^|/)(tests?/|_archive/|vendor/)|ch_(reader|writer|probe)\.py$")


@dataclass
class ChReaderShapeFinding:
    file: str
    line_no: int
    kind: str
    severity: str
    snippet: str
    suggestion: str = ""
    context: list[str] = field(default_factory=list)


def _severity_for(rel_path: str) -> str:
    """_severity_for implementation."""
    p = rel_path.replace("\\", "/")
    if _EXEMPT_RX.search(p):
        return "EXEMPT"
    for marker in ("scripts/", "src/", "tools/", "docs/_working/", "docs/"):
        i = p.rfind(marker)
        if i >= 0:
            p = p[i:]
            break
    if p.startswith(("scripts/", "src/", "tools/", "docs/_working/")):
        if _JUDGMENT_PATH_RX.search(p):
            return "JUDGMENT"
    return "NON_JUDGMENT"


def _reader_match(line: str, bare_mode: bool):
    """第一/第二把正则：带接收者命中优先；裸导入文件降级用裸调用正则同判。"""
    m = _STR_READER_RX.search(line)
    if m is None and bare_mode:
        # 裸导入命中与带接收者命中同判（违约面相同，文件首部的 import 行即证据）
        m = _STR_READER_BARE_RX.search(line)
    return m


def _record_reader_hit(
    findings: list[ChReaderShapeFinding],
    rel_path: str,
    line: str,
    m,
    i: int,
    raw: str,
    severity: str,
    str_reader_vars: dict[str, int],
) -> None:
    """命中字符串读接口后的三分类：S1 下标直取 / S2 for-in 逐字迭代 / 赋值登记（S3 追踪用）。"""
    tail = line[m.end() :]
    sub = _SUBSCRIPT_RX.match(tail)
    if sub:
        findings.append(
            ChReaderShapeFinding(
                rel_path,
                i,
                "S1_DIRECT_SUBSCRIPT",
                severity,
                raw.strip()[:200],
                suggestion="改 ch_reader.query_rows(sql)（返回 list[tuple]，失败必抛），"
                "一次性判据读数改 ch_probe.py；字符串下标取到的是「首行首字符」，判据必错",
            )
        )
    elif re.match(r"^\s*for\s+[\w()\s,]+\s+in\s*$", line[: m.start()]) and re.match(r"^\s*:\s*$", tail):
        # 直接 `for x in ch_reader.query(...)`＝逐字符迭代（P1 病样本）；
        # 经 .splitlines()/.split() 转换后的按行迭代是**正确用法**，不报
        findings.append(
            ChReaderShapeFinding(
                rel_path,
                i,
                "S2_FOR_IN_CALL",
                severity,
                raw.strip()[:200],
                suggestion="改 ch_reader.query_rows(sql)；对 TSV 字符串 for-in 会逐字符迭代",
            )
        )
    else:
        am = _ASSIGN_RX.match(line)
        if am and not tail.strip().startswith((".", ")", ",")):
            str_reader_vars[am.group("name")] = i


def _check_var_uses(
    findings: list[ChReaderShapeFinding],
    rel_path: str,
    line: str,
    raw: str,
    i: int,
    str_reader_vars: dict[str, int],
    lines: list[str],
    severity: str,
) -> None:
    """S3：变量名来自字符串读接口，随后被数字下标 / for-in 使用。"""
    for var, def_line in list(str_reader_vars.items()):
        if def_line == i:
            continue
        use_idx = re.search(rf"\b{re.escape(var)}\s*\[\s*-?\d+\s*\]", line)
        for_m = _FOR_ASSIGN_RX.match(line)
        guarded = any(
            re.search(rf"isinstance\(\s*{re.escape(var)}\s*,", ln)
            for ln in lines[max(0, def_line - 1) : min(len(lines), i)]
        )
        if guarded:
            continue  # 调用点已显式做了形状检查（isinstance 分流 str/list）⇒ 非形状违约
        if use_idx:
            findings.append(
                ChReaderShapeFinding(
                    rel_path,
                    i,
                    "S3_VAR_SUBSCRIPT",
                    severity,
                    raw.strip()[:200],
                    suggestion=f"`{var}` 来自 ch_*.query() 的 TSV 字符串（定义于第 {def_line} 行），"
                    f"数字下标＝首位数字假象；赋值处改 `{var} = ch_reader.query_rows(...)`",
                )
            )
        elif for_m and for_m.group("name") == var:
            findings.append(
                ChReaderShapeFinding(
                    rel_path,
                    i,
                    "S3_VAR_FOR_IN",
                    severity,
                    raw.strip()[:200],
                    suggestion=f"`{var}` 是 TSV 字符串（定义于第 {def_line} 行），for-in＝逐字符迭代；"
                    f"赋值处改 ch_reader.query_rows(...) 后按行元组迭代",
                )
            )


def _attach_contexts(findings: list[ChReaderShapeFinding], lines: list[str]) -> None:
    """每条 finding 回填前后 5 行上下文（截断 160 字符）。"""
    for f in findings:
        lo, hi = max(0, f.line_no - 3), min(len(lines), f.line_no + 2)
        f.context = [ln.strip()[:160] for ln in lines[lo:hi]]


def scan_text(text: str, rel_path: str) -> list[ChReaderShapeFinding]:
    """核心判据函数（升 gate 时直接复用，禁复制规则）。

    判据本体拆为三个 helper（_record_reader_hit/_check_var_uses/_attach_contexts，
    行为与拆分前逐字节等价——2026-09-30 SW19 死账救援降 COMPLEXITY-GUARD 复杂度）。
    """
    findings: list[ChReaderShapeFinding] = []
    lines = text.splitlines()
    severity = _severity_for(rel_path)
    str_reader_vars: dict[str, int] = {}  # 变量名 -> 定义行号（S3 用）
    # 本文件是否"裸导入"了字符串读接口（`from zephyr.data.ch_reader import query`）——
    # 若是，则不带接收者的 query(...) 调用同样属违约面（第二把正则）
    bare_mode = bool(_BARE_IMPORT_RX.search(text))

    for i, raw in enumerate(lines, start=1):
        line = raw.split("#", 1)[0] if raw.lstrip().startswith("#") else raw
        if raw.lstrip().startswith("#"):
            continue
        m = _reader_match(line, bare_mode)
        if m:
            _record_reader_hit(findings, rel_path, line, m, i, raw, severity, str_reader_vars)
        _check_var_uses(findings, rel_path, line, raw, i, str_reader_vars, lines, severity)
    _attach_contexts(findings, lines)
    return findings


def _iter_head_files(root: Path) -> list[tuple[str, str]]:
    """HEAD 树里"提到字符串读接口"的候选 .py（(rel_path, blob_sha)）。

    先用 `git grep` 预筛（一次子进程），再按 blob 批读——避免对 8000+ 文件逐个 `git show`。
    """
    out = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "grep",
            "-I",
            "-l",
            "-E",
            r"(ch_reader|ch_writer|reader|writer|creader|cwriter)[[:space:]]*\.[[:space:]]*query(_table)?\(",
            "HEAD",
            "--",
            "src",
            "scripts",
            "tools",
            "tests",
            "docs/_working",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if out.returncode not in (0, 1):  # 1＝无命中
        raise SystemExit(f"[FATAL] git grep 失败 rc={out.returncode}: {out.stderr[:300]}")
    rels = sorted({ln.split(":", 1)[1] for ln in out.stdout.splitlines() if ":" in ln and ln.endswith(".py")})
    if not rels:
        return []
    lt = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-r", "--format=%(objectname)\t%(path)", "HEAD", "--"] + rels,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if lt.returncode != 0:
        raise SystemExit(f"[FATAL] git ls-tree 失败: {lt.stderr[:300]}")
    pairs: list[tuple[str, str]] = []
    for ln in lt.stdout.splitlines():
        sha, _, path = ln.partition("\t")
        if sha and path:
            pairs.append((path, sha))
    return pairs


def _read_blobs_batch(root: Path, shas: list[str]) -> dict[str, str]:
    """一次 `git cat-file --batch` 读完全部候选 blob（防子进程爆炸）。"""
    if not shas:
        return {}
    proc = subprocess.run(
        ["git", "-C", str(root), "cat-file", "--batch"],
        input=("\n".join(shas) + "\n").encode(),
        capture_output=True,
    )
    raw = proc.stdout
    out: dict[str, str] = {}
    i = 0
    want = set(shas)
    while i < len(raw):
        j = raw.find(b"\n", i)
        if j < 0:
            break
        header = raw[i:j].decode("utf-8", errors="replace").strip()
        parts = header.split(" ")
        if len(parts) == 3 and parts[1] == "blob":
            sha, size = parts[0], int(parts[2])
            body = raw[j + 1 : j + 1 + size]
            if sha in want:
                out[sha] = body.decode("utf-8", errors="replace")
            i = j + 1 + size + 1
        else:
            i = j + 1
    return out


def run(root: Path, files: list[str] | None) -> tuple[list[ChReaderShapeFinding], int, int]:
    """files=None ⇒ 扫 HEAD 树（提交面真源）；否则扫显式文件清单（canary/增量）。"""
    findings: list[ChReaderShapeFinding] = []
    skipped = 0
    if files:
        targets = [(rel, "") for rel in files]
        texts: dict[str, str] = {}
    else:
        pairs = _iter_head_files(root)
        texts = _read_blobs_batch(root, [sha for _, sha in pairs])
        targets = pairs
    for rel, sha in targets:
        if sha:
            text = texts.get(sha)
            rel_disp = rel
            if text is None:
                skipped += 1
                continue
        else:
            p = Path(rel)
            candidate = p if p.is_absolute() else root / rel
            try:
                text = candidate.read_text(encoding="utf-8", errors="replace")
            except OSError:
                skipped += 1
                continue
            rel_disp = str(candidate).replace("\\", "/")
        findings.extend(scan_text(text, rel_disp))
    return findings, len(targets), skipped


def to_markdown(findings: list[ChReaderShapeFinding], scanned: int, skipped: int, src: str, gen: str) -> str:
    """to_markdown implementation."""
    order = {"JUDGMENT": 0, "NON_JUDGMENT": 1, "EXEMPT": 2}
    findings = sorted(findings, key=lambda f: (order.get(f.severity, 9), f.file, f.line_no))
    out = [
        "<!-- 本表由 scripts/governance/wave1a/ch_read_shape_ruler.py 机生，禁手改（重跑覆盖） -->",
        f"<!-- source={src} scanned_files={scanned} unreadable={skipped} generated_at={gen} -->",
        "",
        f"扫描面：`{src}`，{scanned} 个 .py 文件；命中 {len(findings)} 处"
        f"（判据路径 {sum(1 for f in findings if f.severity == 'JUDGMENT')}、"
        f"非判据路径 {sum(1 for f in findings if f.severity == 'NON_JUDGMENT')}、"
        f"豁免面 {sum(1 for f in findings if f.severity == 'EXEMPT')}）。",
        "",
        "| 分级 | 文件 | 行 | 模式 | 命中原文 | 建议补丁位置 |",
        "|---|---|---|---|---|---|",
    ]
    for f in findings:
        out.append(f"| {f.severity} | `{f.file}` | {f.line_no} | {f.kind} | `{f.snippet}` | {f.suggestion} |")
    out.append("")
    out.append(
        "补丁口径统一＝把字符串读接口换成立即可用的严格通道："
        "`ch_reader.query_rows()` / `count_strict()` / `query_rows_table()`（W-180.1），"
        "判据类一次性读数走 `scripts/data/ch_probe.py`（W-180.4）。"
    )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="W-180.2 CH 读接口形状违约静态尺")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[3]))
    ap.add_argument("--files", nargs="*", default=None, help="显式文件清单（canary/增量用，默认扫 HEAD 树）")
    ap.add_argument("--out-md", default=None)
    ap.add_argument("--out-jsonl", default=None)
    ap.add_argument("--strict", action="store_true", help="非判据路径命中也算红")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()

    findings, scanned, skipped = run(root, args.files)
    gen = f"{len(findings)} findings"
    if args.out_md:
        p = Path(args.out_md)
        p.parent.mkdir(parents=True, exist_ok=True)
        src = "explicit-files" if args.files else "git HEAD tree"
        p.write_text(to_markdown(findings, scanned, skipped, src, str(gen)), encoding="utf-8")
    if args.out_jsonl:
        p = Path(args.out_jsonl)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("".join(json.dumps(asdict(f), ensure_ascii=False) + "\n" for f in findings), encoding="utf-8")

    for f in findings:
        print(f"[{f.severity}] {f.file}:{f.line_no} {f.kind} :: {f.snippet}")
    hard = [f for f in findings if f.severity == "JUDGMENT"]
    soft = [f for f in findings if f.severity == "NON_JUDGMENT"]
    print(
        f"[RULER] 扫描 {scanned} 文件（读不到 {skipped}）：判据路径 {len(hard)}、非判据 {len(soft)}、"
        f"豁免 {len(findings) - len(hard) - len(soft)}",
        file=sys.stderr,
    )
    if hard:
        print("[RED] 判据路径存在字符串读接口形状违约（W-180 红线）", file=sys.stderr)
        return 1
    if soft and args.strict:
        print("[RED] --strict：非判据路径命中亦红", file=sys.stderr)
        return 2
    print("[GREEN] 判据路径零命中" if findings else "[GREEN] 零命中", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
