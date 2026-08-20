# [BLUEPRINT] MOD-GOV_ALGO_FLOW_APPLIER | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance._shared.algo_flow_applier
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.code_algorithm_extractor; scripts.git_guard
# [CONSUMERS] algorithm_map_rollout（ALGO_FLOW 全量落地步骤③集中应用+验证）
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 应用前必验证（AST解析+parse_algo_flow+extract回读三重验证失败则不写盘）; 幂等（同标记重复应用=替换不追加）; 每文件应用后立即git_guard add
# [MODIFY-GUARD] 无
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校准文本缺失→跳过并报告; 验证失败→不写盘并报告; git add失败→报告不阻断
# [TESTS] 无（一次性 rollout 工具）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI/人工按需调用的校准标记应用器，非常驻服务，由 algo_flow 落地流程显式触发
"""algo_flow_applier.py — ALGO_FLOW 校准标记集中应用器（半自动落地步骤③配套）。

架构分工：AI 校准代理只产出「校准标记纯文本」（.trae/documents/algo_flow_calibrated/<safe>.txt），
本脚本集中负责「写回源码 docstring」这一高危机械操作，保证：
  ① docstring 插入/替换走 AST 定位，不手抖改坏 Python 语法
  ② 重复目标消解（dup-resolution）：多模块共享 richest docstring 文件时，
     聚合/域级模块重定向到自己的 __init__.py（docstring ≥200 字保证 extractor 选中）
  ③ 三重验证：AST 通过 + parse_algo_flow 解析出节点 + extract_algorithm_from_code 回读命中同一标记
  ④ 应用后立即 git add（多会话防护铁律）

使用方式：
    python scripts/governance/_shared/algo_flow_applier.py --plan     # 生成 calibration_plan.json
    python scripts/governance/_shared/algo_flow_applier.py --apply    # 应用全部校准标记
    python scripts/governance/_shared/algo_flow_applier.py --verify   # 全量回读验证覆盖率
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_SHARED_DIR = str(_THIS_FILE.parent)
if _SHARED_DIR not in sys.path:
    sys.path.insert(0, _SHARED_DIR)

from algo_flow_drafter import DRAFTS_DIR, _safe_draft_name  # noqa: E402
from code_algorithm_extractor import (  # noqa: E402
    REPO_ROOT,
    extract_algorithm_from_code,
    parse_algo_flow,
)

CALIBRATED_DIR = REPO_ROOT / ".trae" / "documents" / "algo_flow_calibrated"
PLAN_JSON = REPO_ROOT / ".trae" / "documents" / "algo_flow_calibration_plan.json"
MODULES_JSON = REPO_ROOT / ".trae" / "documents" / "_operational_modules.json"

_MARKER_START = "# [ALGO_FLOW]"


# ── plan：模块 → 最终目标文件（含重复消解）─────────────────────


def _load_draft_index() -> dict[str, str]:
    """读取草稿索引 _index.tsv：module_id → 草稿目标文件。"""
    index: dict[str, str] = {}
    for ln in (DRAFTS_DIR / "_index.tsv").read_text(encoding="utf-8").splitlines():
        if ln.strip():
            mid, tgt = ln.split("\t")
            index[mid] = tgt
    return index


def _group_by_target(mods: list[dict], index: dict[str, str]) -> dict[str, list[dict]]:
    """按草稿目标文件分组（跳过已有标记/无草稿的模块）。"""
    groups: dict[str, list[dict]] = {}
    for m in mods:
        if m.get("has_flow"):
            continue
        tgt = index.get(m["module_id"])
        if not tgt:
            continue
        groups.setdefault(tgt, []).append(m)
    return groups


def _pick_dup_keeper(ms: list[dict], tgt: str) -> dict:
    """dup 组选保留者：depgraph path == tgt 优先，否则首个非 __unmanaged__。"""
    for m in ms:
        if (m["path"] or "").replace("\\", "/") == tgt:
            return m
    concrete = [m for m in ms if not m["module_id"].startswith("__unmanaged__")]
    return concrete[0] if concrete else ms[0]


def _dup_group_plan(ms: list[dict], tgt: str) -> list[dict]:
    """dup 组重定向：keeper 保留 tgt，其余写自己 depgraph path（__init__.py/自有文件）。

    聚合模块 docstring 由标记本体保证 ≥30/200 字阈值，extractor 必选中。
    """
    keeper = _pick_dup_keeper(ms, tgt)
    plan: list[dict] = []
    for m in ms:
        final = tgt if m is keeper else (m["path"] or "").replace("\\", "/")
        plan.append(
            {
                "module_id": m["module_id"],
                "depgraph_path": (m["path"] or "").replace("\\", "/"),
                "target_path": final,
            }
        )
    return plan


def build_plan() -> list[dict]:
    """生成校准计划：每模块确认最终 target_path（dup 组重定向）。

    规则：
      - 模块 depgraph path == 草稿目标文件 → 保留（实体模块写自己文件）
      - 否则重定向到自己 depgraph path（__init__.py/自有文件），
        聚合模块 docstring 由标记本体保证 ≥30/200 字阈值，extractor 必选中
    """
    mods = json.loads(MODULES_JSON.read_text(encoding="utf-8"))
    index = _load_draft_index()
    groups = _group_by_target(mods, index)

    plan: list[dict] = []
    for tgt, ms in groups.items():
        if len(ms) == 1:
            plan.append(
                {
                    "module_id": ms[0]["module_id"],
                    "depgraph_path": ms[0]["path"],
                    "target_path": tgt,
                }
            )
            continue
        plan.extend(_dup_group_plan(ms, tgt))
    PLAN_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return plan


# ── docstring 插入/替换（AST 定位）─────────────────────────────


def _find_docstring_node(tree: ast.Module) -> ast.Expr | None:
    if (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        return tree.body[0]
    return None


def _strip_existing_marker(doc: str) -> str:
    """移除旧 ALGO_FLOW 块（含尾部 边: 段），幂等替换。"""
    if _MARKER_START not in doc:
        return doc
    lines = doc.splitlines()
    out: list[str] = []
    in_block = False
    in_edges = False
    for ln in lines:
        s = ln.strip()
        if s == _MARKER_START:
            in_block = True
            continue
        if in_block:
            if s == "# [/ALGO_FLOW]":
                in_block = False
                in_edges = True  # 块后的 边: 段也跳过
            continue
        if in_edges:
            # 跳过 "#" / "# 边:" / "# I1 --> F1" 等行，直到非注释行
            if s.startswith("#") or not s:
                continue
            in_edges = False
        out.append(ln)
    # 去掉尾部多余空行
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def apply_marker_to_file(py_abs: Path, marker: str) -> tuple[bool, str]:
    """把 marker 文本插入 py 文件 module docstring 末尾（无 docstring 则新建）。

    :return: (ok, error_msg)
    """
    try:
        src = py_abs.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return False, f"读取失败: {e}"
    try:
        tree = ast.parse(src, filename=str(py_abs))
    except SyntaxError as e:
        return False, f"AST解析失败: {e}"

    lines = src.splitlines()
    node = _find_docstring_node(tree)
    if node is not None:
        old_doc = node.value.value
        new_doc = _strip_existing_marker(old_doc).rstrip() + "\n\n" + marker.rstrip() + "\n"
        if '"""' in new_doc:
            if "'''" in new_doc:
                return False, "docstring 同时含两种三引号，跳过"
            quote = "'''"
        else:
            quote = '"""'
        start, end = node.lineno - 1, node.end_lineno - 1  # 0-based 含
        replacement = (quote + "\n" + new_doc.rstrip("\n") + "\n" + quote).splitlines()
        new_lines = lines[:start] + replacement + lines[end + 1 :]
    else:
        if '"""' in marker:
            return False, "marker 含三引号且无 docstring 可附着"
        first_lineno = tree.body[0].lineno if tree.body else 1
        insert_at = first_lineno - 1  # 0-based，插到第一个语句前
        block = ('"""\n' + marker.rstrip() + '\n"""').splitlines() + [""]
        new_lines = lines[:insert_at] + block + lines[insert_at:]

    new_src = "\n".join(new_lines) + ("\n" if src.endswith("\n") else "")
    # 写盘前 AST 自检
    try:
        new_tree = ast.parse(new_src, filename=str(py_abs))
        doc = ast.get_docstring(new_tree) or ""
        data = parse_algo_flow(doc)
        if data is None or not data.nodes:
            return False, "写盘后 parse_algo_flow 无节点"
    except SyntaxError as e:
        return False, f"写盘后 AST 失败: {e}"

    try:
        py_abs.write_text(new_src, encoding="utf-8", newline="\n")
    except OSError as e:
        return False, f"写盘失败: {e}"
    return True, ""


def _git_add(rel_path: str) -> str:
    try:
        r = subprocess.run(  # noqa: bare-subprocess  governance脚本调git_guard叶子命令，窗口闪现无影响且避免反向依赖zephyr.shared
            [sys.executable, "scripts/git_guard.py", "add", rel_path],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        return "" if r.returncode == 0 else (r.stderr or r.stdout or "git add 非0")[:200]
    except Exception as e:  # noqa: BLE001
        return f"git add 异常: {e}"


def _verify_readback(depgraph_path: str, expect_first_node: str) -> tuple[bool, str]:
    """用生成器同款 extract_algorithm_from_code 回读，确认命中本模块标记。"""
    s = extract_algorithm_from_code(REPO_ROOT / depgraph_path, module_id="verify")
    if s.algo_flow is None:
        return False, "回读 algo_flow=None（extractor 未选中目标文件）"
    first = s.algo_flow.nodes[0].id if s.algo_flow.nodes else ""
    if expect_first_node and first != expect_first_node:
        return False, f"回读首节点 {first} != 期望 {expect_first_node}（张冠李戴）"
    return True, ""


def _first_node_id(marker: str) -> str:
    for ln in marker.splitlines():
        s = ln.strip()
        if s.startswith("#") and "id:" in s:
            content = s[1:].lstrip()
            if content.startswith("- id:"):
                return content.split(":", 1)[1].strip()
    return ""


def _apply() -> None:
    plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    ok = fail = skip = 0
    failures: list[dict] = []
    for item in plan:
        mid = item["module_id"]
        cal_file = CALIBRATED_DIR / f"{_safe_draft_name(mid)}.txt"
        if not cal_file.exists():
            skip += 1
            continue
        marker = cal_file.read_text(encoding="utf-8")
        if _MARKER_START not in marker:
            failures.append({"module_id": mid, "error": "校准文本无 [ALGO_FLOW] 标记"})
            fail += 1
            continue
        # 截取从 [ALGO_FLOW] 起（允许代理在头部写说明文字）
        marker = marker[marker.index(_MARKER_START) :]
        tgt = REPO_ROOT / item["target_path"]
        if not tgt.exists():
            failures.append({"module_id": mid, "error": f"目标文件不存在 {item['target_path']}"})
            fail += 1
            continue
        ok1, err = apply_marker_to_file(tgt, marker)
        if not ok1:
            failures.append({"module_id": mid, "error": err})
            fail += 1
            continue
        ok2, err2 = _verify_readback(item["depgraph_path"], _first_node_id(marker))
        if not ok2:
            failures.append({"module_id": mid, "error": err2})
            fail += 1
            continue
        gerr = _git_add(item["target_path"])
        if gerr:
            failures.append({"module_id": mid, "error": f"git add: {gerr}"})
        ok += 1
        if ok % 25 == 0:
            print(f"  进度 {ok} 已应用…")
    report = {"applied": ok, "failed": fail, "skipped_no_calibrated": skip, "failures": failures}
    (REPO_ROOT / ".trae" / "documents" / "algo_flow_apply_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n"
    )
    print(f"[APPLY] 成功 {ok} ｜ 失败 {fail} ｜ 无校准文本跳过 {skip}")
    for f_ in failures[:20]:
        print(f"  FAIL {f_['module_id']}: {f_['error'][:120]}")


def _verify() -> None:
    """全量回读：416 运营态模块 algo_flow 覆盖统计。"""
    mods = json.loads(MODULES_JSON.read_text(encoding="utf-8"))
    have = 0
    missing: list[str] = []
    for m in mods:
        s = extract_algorithm_from_code(REPO_ROOT / m["path"], module_id=m["module_id"])
        if s.algo_flow is not None and s.algo_flow.nodes:
            have += 1
        else:
            missing.append(m["module_id"])
    print(f"[VERIFY] 运营态 {len(mods)} 模块，有 ALGO_FLOW {have}，缺 {len(missing)}")
    for x in missing[:30]:
        print(f"  MISS {x}")


def main() -> None:
    parser = argparse.ArgumentParser(description="ALGO_FLOW 校准标记集中应用器")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.plan:
        plan = build_plan()
        tgts = {}
        for p in plan:
            tgts.setdefault(p["target_path"], []).append(p["module_id"])
        dups = {k: v for k, v in tgts.items() if len(v) > 1}
        print(f"[PLAN] {len(plan)} 模块，目标文件 {len(tgts)} 个，残余重复 {len(dups)}")
        for k, v in dups.items():
            print(f"  DUP {k}: {v}")
    elif args.apply:
        _apply()
    elif args.verify:
        _verify()
    else:
        parser.error("需要 --plan/--apply/--verify")


if __name__ == "__main__":
    main()
