# [BLUEPRINT] MOD-GOV_ALGO_FLOW_DRAFTER | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance._shared.algo_flow_drafter
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.code_algorithm_extractor
# [CONSUMERS] algorithm_map_rollout（ALGO_FLOW 全量落地）；人工校准起点
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 只读源码不写回; AST解析失败降级空草稿不抛; 草稿质量低仅作AI校准起点（无公式/无断点判断/无中文翻译）
# [MODIFY-GUARD] 无
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AST损坏→空草稿; 文件不存在→空草稿
# [TESTS] 无（一次性 rollout 工具）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI/人工按需调用的 rollout 草稿工具，非常驻服务，由 algo_flow 落地流程显式触发
"""algo_flow_drafter.py — ALGO_FLOW 草稿生成器（半自动落地步骤①）。

输入一个 .py 模块文件，用 AST 解析提取：
  - module docstring（算法步骤文本按 ①②③/数字/换行切分成线性步骤 → 算法层草稿）
  - 顶层函数签名（输入参数 → 输入层草稿；返回值 → 输出层草稿）
  - 函数调用链（辅助判断算法步骤顺序）

输出 `# [ALGO_FLOW]` 标记格式的草稿文本（YAML 风格），质量低
（无公式/无断点判断/无中文翻译），仅作 AI 校准起点（方案步骤③逐个校准后写回 docstring）。

使用方式：
    # 单文件草稿（打印到 stdout）
    python scripts/governance/_shared/algo_flow_drafter.py src/zephyr/regime/core/regime_detector.py

    # 批量：对 .trae/documents/_operational_modules.json 里全部运营态模块生成草稿
    python scripts/governance/_shared/algo_flow_drafter.py --batch
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_SHARED_DIR = str(_THIS_FILE.parent)
if _SHARED_DIR not in sys.path:
    sys.path.insert(0, _SHARED_DIR)

from code_algorithm_extractor import (  # noqa: E402
    REPO_ROOT,
    _find_richest_docstring_file,
    _parse_module_docstring,
)

DRAFTS_DIR = REPO_ROOT / ".trae" / "documents" / "algo_flow_drafts"
MODULES_JSON = REPO_ROOT / ".trae" / "documents" / "_operational_modules.json"


def _safe_draft_name(module_id: str) -> str:
    """module_id → 安全文件名（__unmanaged__ 含路径分隔符，替换为 __）。"""
    return re.sub(r"[\\/:*?\"<>|]+", "__", module_id)


# 常见参数名 → 输入层中文猜测（校准起点，AI 校准时必须核实）
_PARAM_ZH_HINT = {
    "df": "数据帧 DataFrame",
    "data": "数据 DataFrame",
    "bars": "K线数据",
    "prices": "价格序列",
    "close": "收盘价序列",
    "volume": "成交量序列",
    "symbol": "股票代码",
    "symbols": "股票代码列表",
    "trade_date": "交易日",
    "config": "配置对象",
    "params": "参数",
    "signal": "信号",
    "signals": "信号列表",
    "positions": "持仓",
    "orders": "订单",
    "portfolio": "组合",
}

# docstring 步骤切分：①②③ 或 1. 2. 或 Step1 等
_STEP_RE = re.compile(r"^\s*(?:[①②③④⑤⑥⑦⑧⑨⑩]|\d+[.、)]|Step\s*\d+|步骤\s*\d+)")


def _split_algo_steps(docstring: str) -> list[str]:
    """从 docstring 文本切分线性算法步骤（①②③/数字/换行）。"""
    lines = [ln.rstrip() for ln in docstring.splitlines()]
    steps: list[str] = []
    current: list[str] = []
    for ln in lines:
        s = ln.strip()
        if not s:
            if current:
                steps.append(" ".join(current))
                current = []
            continue
        if _STEP_RE.match(s):
            if current:
                steps.append(" ".join(current))
            current = [s]
        elif current:
            current.append(s)
    if current:
        steps.append(" ".join(current))
    # 过滤太短的碎片（<8字无信息量）
    return [s for s in steps if len(s) >= 8]


def _guess_input_zh(param: str) -> str:
    return _PARAM_ZH_HINT.get(param.lower(), f"{param} 参数")


def _extract_func_sigs(tree) -> list[tuple[str, list[str], str]]:
    """AST 提取函数签名（名称/参数/返回注解）。"""
    sigs: list[tuple[str, list[str], str]] = []
    if tree is None:
        return sigs
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
            ret = ""
            if node.returns is not None:
                try:
                    ret = ast.unparse(node.returns)
                except Exception:  # noqa: BLE001
                    ret = ""
            sigs.append((node.name, args, ret))
    return sigs


def _draft_input_lines(func_sigs: list[tuple[str, list[str], str]]) -> tuple[list[str], int]:
    """输入层草稿：从所有函数参数去重取前 4 个。返回 (行, 输入数)。"""
    seen: list[str] = []
    for _fn, args, _ret in func_sigs:
        for a in args:
            if a not in seen and not a.startswith("_"):
                seen.append(a)
    inputs = seen[:4] or ["data"]
    lines = ["# 层: 输入"]
    for i, p in enumerate(inputs, 1):
        lines.append(f"# - id: I{i}")
        lines.append(f"#   name: {_guess_input_zh(p)}")
        lines.append("#   fields: 待校准")
        lines.append(f"#   code: {p}")
    return lines, len(inputs)


def _draft_feature_lines() -> list[str]:
    return [
        "# 层: 特征",
        "# - id: F1",
        "#   name_zh: 待校准特征",
        "#   name_en: feature_tbd",
        "#   intro: 待校准（AI读代码确认）",
        "#   formula: 待校准",
        "#   code: 待校准",
        "#   registry: factor_registry: 待查",
        "#   is_break: true",
    ]


def _draft_algo_lines(steps: list[str]) -> list[str]:
    lines = ["# 层: 算法"]
    for i, st in enumerate(steps[:8] or ["待校准算法步骤"], 1):
        lines.append(f"# - id: A{i}")
        lines.append(f"#   name_zh: {st[:40]}")
        lines.append("#   name_en: tbd")
        lines.append(f"#   intro: {st[:60]}")
        lines.append("#   inputs: 待校准")
        lines.append("#   outputs: 待校准")
    return lines


def _draft_output_lines(func_sigs: list[tuple[str, list[str], str]]) -> list[str]:
    rets = sorted({r for _fn, _a, r in func_sigs if r})[:2] or ["result"]
    lines = ["# 层: 输出"]
    for i, r in enumerate(rets, 1):
        lines.append(f"# - id: O{i}")
        lines.append(f"#   name_zh: 待校准输出 {r}")
        lines.append(f"#   name_en: {r}")
        lines.append("#   intro: 待校准")
        lines.append("#   downstream: 待校准")
    lines.append("# [/ALGO_FLOW]")
    return lines


def _draft_edge_lines(n_inputs: int, n_steps: int) -> list[str]:
    lines = ["#", "# 边:"]
    for i in range(1, n_inputs + 1):
        lines.append(f"# I{i} -.->|断点| F1")
    lines.append("# F1 --> A1")
    if n_steps:
        for i in range(1, min(n_steps, 8)):
            lines.append(f"# A{i} --> A{i + 1}")
        lines.append(f"# A{min(n_steps, 8)} --> O1")
    else:
        lines.append("# A1 --> O1")
    return lines


def draft_algo_flow(py_path: Path) -> tuple[str, dict]:
    """生成单模块 ALGO_FLOW 草稿。

    :return: (草稿文本, meta)；meta 含 target_path/docstring/n_functions/steps。
    """
    py_path = Path(py_path)
    if not py_path.is_absolute():
        py_path = REPO_ROOT / py_path
    meta = {"target_path": str(py_path), "docstring_len": 0, "n_functions": 0, "n_steps": 0}
    if not py_path.exists():
        return "# [ALGO_FLOW]（文件不存在，空草稿）", meta

    actual_path, docstring, _s, _e = _find_richest_docstring_file(py_path)
    meta["target_path"] = str(actual_path.relative_to(REPO_ROOT)).replace("\\", "/")
    meta["docstring_len"] = len(docstring)

    try:
        src = actual_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=str(actual_path))
    except (SyntaxError, OSError, ValueError):
        tree = None

    func_sigs = _extract_func_sigs(tree)
    meta["n_functions"] = len(func_sigs)
    steps = _split_algo_steps(docstring)
    meta["n_steps"] = len(steps)

    lines: list[str] = ["# [ALGO_FLOW]"]
    input_lines, n_inputs = _draft_input_lines(func_sigs)
    lines.extend(input_lines)
    lines.extend(_draft_feature_lines())
    lines.extend(_draft_algo_lines(steps))
    lines.extend(_draft_output_lines(func_sigs))
    lines.extend(_draft_edge_lines(n_inputs, len(steps)))
    return "\n".join(lines), meta


def _batch() -> None:
    """批量模式：对全部运营态模块生成草稿到 .trae/documents/algo_flow_drafts/。"""
    mods = json.loads(MODULES_JSON.read_text(encoding="utf-8"))
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    ok = skip = 0
    index_lines: list[str] = []
    for m in mods:
        mid = m["module_id"]
        if m.get("has_flow"):
            skip += 1
            continue
        src = m.get("src") or m.get("path") or ""
        if not src:
            skip += 1
            continue
        draft, meta = draft_algo_flow(REPO_ROOT / src)
        out = DRAFTS_DIR / f"{_safe_draft_name(mid)}.txt"
        header = (
            f"module_id: {mid}\n"
            f"target_path: {meta['target_path']}\n"
            f"depgraph_path: {m.get('path')}\n"
            f"docstring_len: {meta['docstring_len']} n_functions: {meta['n_functions']} n_steps: {meta['n_steps']}\n"
            f"{'-' * 60}\n"
        )
        out.write_text(header + draft + "\n", encoding="utf-8", newline="\n")
        index_lines.append(f"{mid}\t{meta['target_path']}")
        ok += 1
    (DRAFTS_DIR / "_index.tsv").write_text("\n".join(index_lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] 草稿生成 {ok} 个，跳过 {skip} 个（已有标记/无源码），目录 {DRAFTS_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description="ALGO_FLOW 草稿生成器（AI 校准起点）")
    parser.add_argument("py_file", nargs="?", help="单个 .py 模块文件")
    parser.add_argument("--batch", action="store_true", help="批量模式（读 _operational_modules.json）")
    args = parser.parse_args()
    if args.batch:
        _batch()
        return
    if not args.py_file:
        parser.error("需要 py_file 或 --batch")
    draft, meta = draft_algo_flow(Path(args.py_file))
    print(
        f"# target: {meta['target_path']} (docstring {meta['docstring_len']} 字, "
        f"{meta['n_functions']} 函数, {meta['n_steps']} 步骤)"
    )
    print(draft)


if __name__ == "__main__":
    main()
