# [BLUEPRINT] MOD-GOV_ALGO_FLOW_VALIDATOR | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance._shared.algo_flow_validate_marker
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.code_algorithm_extractor
# [CONSUMERS] algorithm_map_rollout 校准代理自检；algo_flow_applier 集中复验
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 只读不写; 按§4.14/§4.15/§4.16校验; exit 0=通过 1=有问题
# [MODIFY-GUARD] 无
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件不存在/无标记→exit 1
# [TESTS] 无（一次性 rollout 工具）
# [TTL] permanent
"""algo_flow_validate_marker.py — ALGO_FLOW 校准标记质量校验器。

按 visualization_view_template.md §4.14/§4.15/§4.16 校验单个校准标记文件：
  - 节点 ID 合法（[A-Za-z0-9_]+）且唯一
  - 五层必填字段：输入=name；特征/指标=name_zh+name_en+intro+formula+code+registry+is_break；
    算法=name_zh+name_en+intro+inputs+outputs；输出=name_zh+intro
  - 边端点必须是已定义节点
  - 边断点一致性：断点边必须指向 is_break=true 节点，正常边不得指向断点节点
  - 至少 输入/算法/输出 三层非空

使用方式：
    python scripts/governance/_shared/algo_flow_validate_marker.py <calibrated.txt> [<more.txt> ...]
    python scripts/governance/_shared/algo_flow_validate_marker.py --dir <目录>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_SHARED_DIR = str(_THIS_FILE.parent)
if _SHARED_DIR not in sys.path:
    sys.path.insert(0, _SHARED_DIR)

from code_algorithm_extractor import parse_algo_flow  # noqa: E402

_ID_RE = re.compile(r"^[A-Za-z0-9_]+$")

_REQUIRED = {
    "输入": ["name_zh"],
    "特征": ["name_zh", "name_en", "intro", "formula", "code", "registry"],
    "指标": ["name_zh", "name_en", "intro", "formula", "code", "registry"],
    "算法": ["name_zh", "name_en", "intro", "inputs", "outputs"],
    "输出": ["name_zh", "intro"],
}


def _check_node_fields(n, problems: list[str]) -> None:
    """单节点字段校验：ID 合法/层名合法/必填字段/registry 查实。"""
    if n.layer not in _REQUIRED:
        problems.append(f"节点 {n.id} 层名非法: {n.layer!r}（必须 输入/特征/指标/算法/输出）")
        return
    for f in _REQUIRED[n.layer]:
        if not getattr(n, f, ""):
            problems.append(f"节点 {n.id}（{n.layer}）缺必填字段 {f}")
    if n.layer in ("特征", "指标") and n.is_break and "待" in n.registry:
        problems.append(f"节点 {n.id} registry 未查实（含'待'字）")


def _check_nodes(data, problems: list[str]) -> set[str]:
    """节点层校验，返回已见层名集合。"""
    ids: set[str] = set()
    layers_seen: set[str] = set()
    for n in data.nodes:
        if not _ID_RE.match(n.id):
            problems.append(f"节点ID非法: {n.id!r}")
        if n.id in ids:
            problems.append(f"节点ID重复: {n.id}")
        ids.add(n.id)
        layers_seen.add(n.layer)
        _check_node_fields(n, problems)
    for must in ("输入", "算法", "输出"):
        if must not in layers_seen:
            problems.append(f"缺必要层: {must}")
    return ids


def _check_edges(data, ids: set[str], problems: list[str]) -> None:
    """边校验：端点已定义 + 断点边一致性。"""
    if not data.edges:
        problems.append("无边定义（边: 段缺失或格式错）")
    node_by_id = {n.id: n for n in data.nodes}
    for e in data.edges:
        if e.src not in ids:
            problems.append(f"边起点未定义: {e.src}")
        if e.dst not in ids:
            problems.append(f"边终点未定义: {e.dst}")
            continue
        dst_break = node_by_id[e.dst].is_break
        if e.is_break and not dst_break:
            problems.append(f"断点边指向非断点节点: {e.src} -.-> {e.dst}")
        if not e.is_break and dst_break:
            problems.append(f"正常边指向断点节点: {e.src} --> {e.dst}（应为 -.->|断点|）")


def validate_file(path: Path) -> list[str]:
    """校验单个校准标记文件，返回问题列表（空=通过）。"""
    problems: list[str] = []
    if not path.exists():
        return [f"文件不存在: {path}"]
    text = path.read_text(encoding="utf-8")
    if "# [ALGO_FLOW]" not in text:
        return ["缺 # [ALGO_FLOW] 起始标记"]
    data = parse_algo_flow(text)
    if data is None or not data.nodes:
        return ["parse_algo_flow 解析不到节点"]

    ids = _check_nodes(data, problems)
    _check_edges(data, ids, problems)
    return problems


def main() -> int:
    args = sys.argv[1:]
    files: list[Path] = []
    if args and args[0] == "--dir":
        if len(args) < 2:
            print("用法: algo_flow_validate_marker.py --dir <目录>")
            return 1
        files = sorted(Path(args[1]).glob("*.txt"))
    else:
        files = [Path(a) for a in args]
    if not files:
        print("用法: algo_flow_validate_marker.py <file.txt> [...] | --dir <目录>")
        return 1
    total_problems = 0
    fail_files = 0
    for f in files:
        probs = validate_file(f)
        if probs:
            fail_files += 1
            total_problems += len(probs)
            print(f"[FAIL] {f.name}")
            for p in probs:
                print(f"   - {p}")
        elif len(files) == 1:
            print(f"[OK] {f.name}")
    print(f"[SUMMARY] {len(files)} 文件，{fail_files} 失败，{total_problems} 问题")
    return 1 if total_problems else 0


if __name__ == "__main__":
    sys.exit(main())
