# create_guard_batch_replay.py — CLASS-UNIQUENESS 批量化等价重放取证工具（波13·包13.1，非 pytest 件）
"""
对 HEAD `git log --diff-filter=A` 的真实新增 .py 样本集（默认 ≥110 个含类文件），
逐条对比：
  - 旧判据参考实现（HEAD L497-551 逐名 `git grep -l` 语义的忠实复刻，本文件内
    `legacy_reference_check`，一次历史普查即一条 `git grep -l`）
  - 新实现（生产代码 `create_guard._check_class_uniqueness`，批量化 + 归因）
的 (passed, detail) 逐字节全等性，并导出证据 JSON 供 pytest 红证复算
（`test_create_guard_keyword_overlap_canary.py::test_batching_equivalence_replay`）。

用法（在仓库根或 worktree 根）：
    python tests/gov_enforcement/create_guard_batch_replay.py
输出：
    tests/gov_enforcement/create_guard_batch_replay_evidence.json
本工具只读（git grep/git log/subprocess 读 + 写自身证据 JSON），无生产路径副作用。
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from zephyr.gov_enforcement.commit_gates.create_guard import (  # noqa: E402
    _attribute_class_grep_lines,
    _chunk_class_names,
    _check_class_uniqueness,
)

_ALIAS_MARKER = "class-name-alias"


class _FakeGateway:
    """最小 gateway 替身：run_git(argv) + project_root（不触碰 GitCommitGateway 锁面）。"""

    def __init__(self, root: Path) -> None:
        self.project_root = root

    def run_git(self, argv: list[str]):
        return subprocess.run(
            argv, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(self.project_root)
        )


def _run(argv: list[str], root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(root))


def file_classes(root: Path, rel: str) -> list[str]:
    """与门一致的取证面：AST 全量 ClassDef，剔除 def 前 3 行含 class-name-alias 标记的类。"""
    p = root / rel
    try:
        src = p.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except Exception:  # noqa: BLE001 — 取证面与门同语义：解析失败=跳过该文件
        return []
    lines = src.splitlines()
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        has_marker = any(
            _ALIAS_MARKER in lines[i] for i in range(max(0, node.lineno - 4), node.lineno - 1) if i < len(lines)
        )
        if not has_marker:
            names.append(node.name)
    return names


def collect_samples(root: Path, min_files: int) -> list[str]:
    """真实新增 .py 样本：git log --diff-filter=A（新→旧）中现存且含类的 src/zephyr 文件。"""
    res = _run(["git", "log", "--diff-filter=A", "--name-only", "--pretty=format:", "--", "src/zephyr"], root)
    seen: dict[str, None] = {}
    for line in res.stdout.splitlines():
        line = line.replace("\\", "/").strip()
        if line.endswith(".py") and line.startswith("src/zephyr/") and line not in seen:
            seen[line] = None
    out: list[str] = []
    for rel in seen:
        if (root / rel).exists() and file_classes(root, rel):
            out.append(rel)
            if len(out) >= max(min_files, 110):
                break
    return out


def legacy_reference_check(gw: _FakeGateway, new_py_files: list[str]) -> tuple[bool, str, dict[str, list[str]], int, float]:
    """HEAD create_guard._check_class_uniqueness（L497-551）逐名版的忠实复刻 + 类名→文件清单导出。

    逐文件逐类名一条 `git grep -l "^class NAME\\b" -- src/zephyr/`，违规组装顺序与消息
    格式逐字照抄 HEAD（本函数在取证工具内自包含，不 import 已改的生产旧码）。
    """
    greps = 0
    elapsed = 0.0
    name_files: dict[str, list[str]] = {}
    _class_violations = []
    for _py_file in new_py_files:
        for name in file_classes(gw.project_root, _py_file):
            if name in name_files:
                _existing = [f for f in name_files[name] if f != _py_file]
                if _existing:
                    _class_violations.append((_py_file, name, _existing))
                continue  # 同名只查一次（逐名版对同名的两次查询返回值恒等）
            t = time.perf_counter()
            _grep_res = gw.run_git(["git", "grep", "-l", f"^class {name}\\b", "--", "src/zephyr/"])
            elapsed += time.perf_counter() - t
            greps += 1
            files = (
                [f.replace("\\", "/") for f in _grep_res.stdout.strip().splitlines() if f.strip()]
                if _grep_res.returncode == 0
                else []
            )
            name_files[name] = files
            _existing = [f for f in files if f != _py_file]
            if _existing:
                _class_violations.append((_py_file, name, _existing))
    if _class_violations:
        _detail = "; ".join(f"{f} 定义 class {name} 与已有 {existing} 同名" for f, name, existing in _class_violations)
        return (
            False,
            (
                f"类名跨模块冲突(ARCH-034 CLASS-UNIQUENESS): {_detail}. "
                f"同名不同义是 AI 开发幻觉温床（后导入覆盖前导入，不报错）。"
                f"修复：①改名区分（如 Managed* 前缀）②若是合法 re-export，"
                f"在 class 定义前加 '# class-name-alias: <理由>' 标记豁免。"
            ),
            name_files,
            greps,
            elapsed,
        )
    return True, "", name_files, greps, elapsed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=120)
    ap.add_argument("--out", default="tests/gov_enforcement/create_guard_batch_replay_evidence.json")
    args = ap.parse_args()
    root = _ROOT
    head = _run(["git", "rev-parse", "HEAD"], root).stdout.strip()

    samples = collect_samples(root, args.samples)
    if len(samples) < 100:
        print(f"RED: 样本不足 100（现 {len(samples)}），拒绝出证据")
        return 2
    gw = _FakeGateway(root)

    all_names = sorted({n for f in samples for n in file_classes(root, f)})
    non_ascii = [n for n in all_names if not n.isascii()]

    # 新实现（批量）：捕获生产代码实际发出的 git 调用与逐次 stdout
    calls: list[dict] = []
    orig_run_git = gw.run_git

    def _spy_run_git(argv):
        t = time.perf_counter()
        res = orig_run_git(argv)
        calls.append(
            {
                "argv": argv,
                "returncode": res.returncode,
                "stdout": res.stdout if argv[:3] == ["git", "grep", "-n"] else res.stdout[:200000],
                "elapsed_s": round(time.perf_counter() - t, 3),
            }
        )
        return res

    gw.run_git = _spy_run_git
    t = time.perf_counter()
    new_passed, new_detail = _check_class_uniqueness(gw, samples)
    new_elapsed = time.perf_counter() - t
    gw.run_git = orig_run_git

    # 旧判据参考实现（逐名）
    old_passed, old_detail, old_map, old_greps, old_grep_elapsed = legacy_reference_check(gw, samples)

    # 归因复算：批量 -n 输出 → _attribute_class_grep_lines == 逐名清单（对每个 ascii 名）
    attr_map: dict[str, list[str]] = {}
    for call in calls:
        if call["argv"][:4] == ["git", "grep", "-n", "-E"]:
            pat = call["argv"][4]
            chunk = pat[len("^class (") : -len(")\\b")].split("|")
            for k, v in _attribute_class_grep_lines(call["stdout"], chunk).items():
                attr_map[k] = v
    chunked = _chunk_class_names(all_names)
    attr_mismatch = sorted(n for n in all_names if n.isascii() and attr_map.get(n, []) != old_map.get(n, []))

    evidence = {
        "head": head,
        "n_samples": len(samples),
        "n_classes_total": len(all_names),
        "non_ascii_names": non_ascii,
        "old": {
            "passed": old_passed,
            "detail": old_detail,
            "grep_calls": old_greps,
            "grep_elapsed_s": round(old_grep_elapsed, 3),
            "name_map": {n: old_map[n] for n in all_names if old_map.get(n)},
        },
        "new": {
            "passed": new_passed,
            "detail": new_detail,
            "grep_calls": len(calls),
            "elapsed_s": round(new_elapsed, 3),
            "batch_calls": [
                {
                    "returncode": c["returncode"],
                    "pattern_len": len(c["argv"][4]),
                    "chunk": c["argv"][4][len("^class (") : -len(")\\b")].split("|"),
                    "stdout": c["stdout"],
                    "elapsed_s": c["elapsed_s"],
                }
                for c in calls
                if c["argv"][:4] == ["git", "grep", "-n", "-E"]
            ],
            "n_chunks": len(chunked),
        },
        "verdict_byte_equal": (old_passed, old_detail) == (new_passed, new_detail),
        "attribution_mismatch_names": attr_mismatch,
        "samples": [{"file": f, "classes": file_classes(root, f)} for f in samples],
    }
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=1), encoding="utf-8")
    print(
        f"samples={len(samples)} classes={len(all_names)} verdict_byte_equal={evidence['verdict_byte_equal']} "
        f"attr_mismatch={len(attr_mismatch)} old_greps={old_greps}({old_grep_elapsed:.1f}s) "
        f"new_greps={len(calls)}({new_elapsed:.1f}s) violations_old={old_detail.count('定义 class')} -> {out_path}"
    )
    return 0 if evidence["verdict_byte_equal"] and not attr_mismatch else 1


if __name__ == "__main__":
    sys.exit(main())
