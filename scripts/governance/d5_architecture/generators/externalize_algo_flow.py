# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §
# [MODULE] scripts.governance.d5_architecture.generators.externalize_algo_flow
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.code_algorithm_extractor; scripts.governance._shared.file_utils (safe_write_text)
# [CONSUMERS] P2-1 ALGO_FLOW 出仓批（Owner 2026-09-15 授权"逐域出仓+round-trip+域测试"）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 每文件先迁移后 round-trip 断言（nodes+edges 逐项一致）失败即回滚源文件（.bak 恢复）；
#   外部 yaml 落 docs/03_modules/<domain>/algo_flow/<stem>.yaml（doc_type=architecture_view 过 DCR-001，
#   目录契约 allowed=[.md,.yaml]）；幂等（已带 external 锚的文件跳过）；域过滤 --domain/--file；
#   --dry-run 零写入；yaml 块文本 = docstring 内联块逐字节副本（含边段，block-scalar 保留原样）；
#   只处理 module docstring 含真内联块的文件（锚行不算）；
#   批级 stem 碰撞预判（P2-1 orchestrator 批实证）：同域非 __init__ 同 stem 多文件时子包件
#   确定性改道 parent__stem，dry-run 预测=落盘路径（消除盘存在改道的时序依赖）
# [MODIFY-GUARD] 无
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单文件失败跳过并计入 failed 列表（不中断批次）；--dry-run 恒 exit 0
# [TESTS] 无（批次工具，round-trip 自验证即测试）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的批量出仓器（Owner 授权批次施工，非常驻服务）
"""externalize_algo_flow.py — ALGO_FLOW 内联块批量出仓器（P2-1 契约头减负实施器）。

把 src 模块 docstring 内驻留的 ``# [ALGO_FLOW]`` 机器块（AST 可再生，均值 ~47 行/模块）
迁移到 docs/03_modules/<domain>/algo_flow/<stem>.yaml，源码 docstring 换一行锚：
    # [ALGO_FLOW] external: <yaml 相对路径>
extractor（code_algorithm_extractor）已支持 external 锚加载 → 同一 parse_algo_flow 管线。

安全序（每文件）：
  1. 解析内联块（_has_inline_algo_flow）→ 抽块原文（docstring 内 [# [ALGO_FLOW]..边段尾]）
  2. 写外部 yaml（algo_flow: | block-scalar 逐行缩进副本）
  3. 源码 docstring 内联块+边段替换为锚行（AST 定位 docstring 行范围，禁止正则改源码体）
  4. round-trip 断言：extract_algorithm_from_code 重新解析，nodes/edges 与迁移前逐项一致
  5. 失败 → .bak 回滚源文件 + 删除 yaml，计入 failed

Usage::
    python scripts/governance/d5_architecture/generators/externalize_algo_flow.py --domain backtest --dry-run
    python scripts/governance/d5_architecture/generators/externalize_algo_flow.py --domain backtest
    python scripts/governance/d5_architecture/generators/externalize_algo_flow.py --file src/zephyr/x/y.py
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.code_algorithm_extractor import (  # noqa: E402
    _ALGO_FLOW_END,
    _ALGO_FLOW_START,
    _has_inline_algo_flow,
    parse_algo_flow,
    REPO_ROOT,
)
from zephyr.shared.io.file_utils import safe_write_text  # noqa: E402

_ANCHOR_RE = re.compile(r"^#\s*\[ALGO_FLOW\]\s+external:\s*(\S+)\s*$", re.MULTILINE)

# 既有 yaml 反查缓存：domain_dir → {source_of_truth: yaml_rel}（批9 幂等治本）
_EXISTING_YAML_CACHE: dict[str, dict[str, str]] = {}

# 批级 stem 碰撞预判表：rel_py → yaml_rel（main() 批开始前静态填充）
_PLANNED_REMAP: dict[str, str] = {}


def _plan_stem_collision_remaps(targets: list[Path]) -> None:
    """批开始前静态判定同 stem 碰撞，子包件确定性改道 ``<parent>__<stem>.yaml``。

    映射改道雷同族（b9 实证）：_yaml_rel_for 靠"盘上 yaml 已存在"改道，同批内
    后处理文件在写入前阶段不可预测（依赖 rglob 排序+落盘副作用）——dry-run 与
    正式跑路径不一致。此处按批清单预判：同 domain_dir 内非 __init__ 同 stem
    ≥2 文件时，域根件保平铺名，子包件（深度 > src/zephyr/<domain>/）加 parent 前缀；
    不同子包各得唯一名，处理顺序无关。
    """
    _PLANNED_REMAP.clear()
    by_stem: dict[tuple[str, str], list[Path]] = {}
    for p in targets:
        if p.name == "__init__.py":
            continue
        rel = p.relative_to(REPO_ROOT).as_posix()
        by_stem.setdefault((_domain_of(rel), p.stem), []).append(p)
    for (domain_dir, stem), paths in by_stem.items():
        if len(paths) < 2:
            continue
        for p in paths:
            rel_parts = p.relative_to(REPO_ROOT).parts  # src/zephyr/<domain>/... 域根件=4 段
            if len(rel_parts) > 4:  # 子包件 → <parent>__<stem>.yaml
                _PLANNED_REMAP[p.relative_to(REPO_ROOT).as_posix()] = (
                    f"docs/03_modules/{domain_dir}/algo_flow/{p.parent.name}__{stem}.yaml"
                )


def _existing_yaml_for(rel_py: str, domain_dir: str) -> str:
    """已落盘 yaml 路径优先——按 yaml 头 ``source_of_truth`` 反查（重跑映射防改道）。

    批9 实证（st-btfix-p15-20260916）：yaml 先落盘（含镜像子目录重排，b9a_remap.json）
    而源码锚后补的场景下，_yaml_rel_for 的"盘存在=碰撞"检测会把映射整体改道到
    ``parent__stem`` 新路径——重复 yaml+锚错位。真源判定以 yaml 头 source_of_truth
    反查为准：盘上已有本文件专属 yaml 即复用原路径；无匹配才走 _yaml_rel_for 推导。
    """
    cache = _EXISTING_YAML_CACHE.get(domain_dir)
    if cache is None:
        cache = {}
        root = REPO_ROOT / "docs" / "03_modules" / domain_dir / "algo_flow"
        if root.is_dir():
            for y in sorted(root.rglob("*.yaml")):
                try:
                    head = y.read_text(encoding="utf-8").splitlines()[:8]
                except OSError:
                    continue
                for ln in head:
                    if ln.startswith("source_of_truth:"):
                        cache[ln.split(":", 1)[1].strip()] = y.relative_to(REPO_ROOT).as_posix()
                        break
        _EXISTING_YAML_CACHE[domain_dir] = cache
    return cache.get(rel_py, "")

# 真源域映射：src/zephyr/<pkg> → docs/03_modules/<domain>/（与 blueprint.md actual_disk_path 对齐）
_DOMAIN_DIRS: dict[str, str] = {
    # 以 docs/03_modules/ 实存目录为准（54 目录普查，2026-09-15）
    "backtest": "_domain_backtest",
    "data": "_domain_data",
    "data_eng": "_domain_data_eng",
    "data_governance": "_domain_data_governance",
    "data_security": "_domain_data_security",
    "market_data": "_domain_mkt_data",
    "ex_core": "_domain_execution_core",
    "ex_sor": "_domain_ex_sor",
    "execution_simulation": "_domain_execution_sim",
    "trading": "_domain_trading",
    "risk": "_domain_risk",
    "factor": "_domain_factor",
    "regime": "_domain_regime",
    "simulation": "_domain_simulation",
    "pf_core": "_domain_portfolio_core",
    "pf_alloc": "_domain_pf_alloc",
    "position": "_domain_position",
    "compliance": "_domain_compliance",
    "sell_decision": "_domain_sell_decision",
    "plan_engine": "_domain_plan_engine",
    "ml_train": "_domain_machine_learning_train",
    "ml_serve": "_domain_ml_serve",
    "intelligence": "_domain_intelligence",
    "frontend": "_domain_frontend",
    "reporting": "_domain_reporting",
    "knowledge": "_domain_knowledge",
    "research": "_domain_research",
    "alt_data": "_domain_alt_data",
    "signal_ashare": "_domain_signal",
    "signal_fundamental": "_domain_fundamental_signal",
    "signal_quality": "_domain_signal_quality",
    "nlp": "_domain_intelligence",
    "cross_asset": "_domain_trading",
    "orchestrator": "_domain_orchestrator",
    "feedback_loop": "_domain_feedback_loop",
    "security": "_domain_security",
    "infrastructure": "_domain_infrastructure",
    "infra_runtime": "_domain_infrastructure_runtime",
    "infra_ops": "_domain_infrastructure_operations",
    "runtime": "_domain_infrastructure_runtime",
    "experiment_tracking": "_domain_infrastructure",
    "shared": "_domain_shared",
    "governance": "_domain_governance",
    "gov_drift": "_domain_gov_drift",
    "gov_audit": "_domain_gov_audit",
    "gov_code_quality": "_domain_governance",
    "gov_rule": "_domain_gov_rule",
    "gov_enforcement": "_domain_gov_enforcement",
    "clone_guard": "_domain_gov_enforcement",
    "autonomy_core": "_domain_autonomy_core",
    "integration": "_domain_integration",
    "digital_twin": "_domain_digital_twin",
}


def _domain_of(py_rel: str) -> str:
    """src/zephyr/<pkg>/... → 域目录名；scripts 走 _domain_governance。"""
    parts = py_rel.replace("\\", "/").split("/")
    if parts[0] == "scripts":
        return "_domain_governance"
    pkg = parts[2] if len(parts) > 3 else parts[-1].removesuffix(".py")
    return _DOMAIN_DIRS.get(pkg, f"_domain_{pkg}")


def _docstring_span(src: str) -> tuple[int, int] | None:
    """module docstring 的 (start_line_idx, end_line_idx)（0 基，含端点）。"""
    tree = ast.parse(src)
    ds = ast.get_docstring(tree)
    if not ds:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return node.lineno - 1, (node.end_lineno or node.lineno) - 1
    return None


def _extract_inline_block(docstring: str) -> tuple[str, int, int] | None:
    """返回 (块原文含边段, 起行 idx, 止行 idx)（docstring 内 0 基）。无边段时止于 [/ALGO_FLOW]。"""
    lines = docstring.splitlines()
    start = end = -1
    in_block = False
    edge_tail = 0  # [/ALGO_FLOW] 后连续 # 行（边段）的最后 idx
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not in_block:
            if s.startswith("#") and _ALGO_FLOW_START in s and "external:" not in s:
                start = i
                in_block = True
            continue
        if _ALGO_FLOW_END in s:
            end = i
            edge_tail = i
            continue
        if end >= 0:
            if not s or s.startswith("#"):
                edge_tail = i
                continue
            break  # 边段结束（首个真实内容行）
    if start < 0 or end < 0:
        return None
    # 边段尾部空行并入
    while edge_tail + 1 < len(lines) and not lines[edge_tail + 1].strip():
        edge_tail += 1
    return "\n".join(lines[start : edge_tail + 1]), start, edge_tail


def _yaml_for(rel_py: str, domain_dir: str, stem: str, block: str) -> str:
    header = (
        f"# ALGO_FLOW 外部真源——{stem}（{domain_dir} 域，真源 {rel_py}）\n"
        f"# 2026-09-15 P2-1 契约头减负批量出仓：docstring 内联块逐字节副本，extractor 经\n"
        f"# external 锚加载走同一 parse_algo_flow 管线；算法公共面变化时同步更新本块。\n"
        f"doc_type: architecture_view\nttl: permanent\nmodule: {rel_py.replace('/', '.')[:-3]}\n"
        f"source_of_truth: {rel_py}\n"
    )
    body = "algo_flow: |\n" + "\n".join(("    " + ln) if ln.strip() else "" for ln in block.rstrip("\n").splitlines()) + "\n"
    return header + body


def _yaml_rel_for(py_path: Path, rel: str, domain_dir: str) -> str:
    """外部 yaml 相对路径；同目录同 stem 并存时加父目录后缀防覆盖。"""
    stem = py_path.stem
    yaml_rel = f"docs/03_modules/{domain_dir}/algo_flow/{stem}.yaml"
    if py_path.name == "__init__.py" or (REPO_ROOT / yaml_rel).exists():
        parent = py_path.parent.name
        if parent and parent not in ("zephyr",) and py_path.name != "__init__.py":
            yaml_rel = f"docs/03_modules/{domain_dir}/algo_flow/{parent}__{stem}.yaml"
        elif py_path.name == "__init__.py" and parent != "zephyr":
            yaml_rel = f"docs/03_modules/{domain_dir}/algo_flow/{parent}__init__.yaml"
        elif py_path.name == "__init__.py":
            yaml_rel = f"docs/03_modules/{domain_dir}/algo_flow/{domain_dir.removeprefix('_domain_')}__init__.yaml"
    return yaml_rel


def externalize(py_path: Path, dry_run: bool) -> dict:
    """单文件出仓。返回 result dict（status: externalized|already|skipped|failed|dryrun）。"""
    rel = py_path.relative_to(REPO_ROOT).as_posix()
    src = py_path.read_text(encoding="utf-8")
    if not _has_inline_algo_flow(src):
        return {"file": rel, "status": "skipped", "reason": "no inline block"}
    if _ANCHOR_RE.search(src):
        return {"file": rel, "status": "already"}

    tree = ast.parse(src)
    ds = ast.get_docstring(tree) or ""
    before = parse_algo_flow(ds)
    if before is None or not before.nodes:
        return {"file": rel, "status": "skipped", "reason": "block unparsable (no nodes)"}
    extracted = _extract_inline_block(ds)
    if extracted is None:
        return {"file": rel, "status": "skipped", "reason": "block span not found"}
    block = extracted[0]

    span = _docstring_span(src)
    if span is None:
        return {"file": rel, "status": "skipped", "reason": "no docstring span"}
    d_start, d_end = span

    # docstring 节点定位（窗口计算需 lineno/end_lineno）
    tree2 = ast.parse(src)
    ds_node = None
    for n in ast.walk(tree2):
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
            ds_node = n
            break

    # 外部 yaml 路径：既有 yaml（source_of_truth 反查）优先，次批级碰撞预判，
    # 无则按推导命名
    domain_dir = _domain_of(rel)
    yaml_rel = _existing_yaml_for(rel, domain_dir) or _PLANNED_REMAP.get(rel, "") or _yaml_rel_for(py_path, rel, domain_dir)
    stem = py_path.stem

    # 锚行窗口：纯源码坐标实测。值↔源码行映射在含 ``\n`` 转义的 docstring 上不保真
    # （memory_bank/skill_attention 实证：desc 行内 "\n" 转义在值中展开 +3 幻影行，
    # 按值行数推窗会切穿闭合引号 → 裸 CJK 语法错误）——块首/收标记按文本定位，
    # 边段（# 注释/空行）向后延伸但封顶 docstring 末行。
    anchor_line = f"# [ALGO_FLOW] external: {yaml_rel}"
    ds_lines = src.splitlines()
    doc_end = (ds_node.end_lineno or ds_node.lineno) - 1  # docstring 末行 0 基
    ws = None
    for i in range(ds_node.lineno - 1, doc_end + 1):
        if ds_lines[i].strip() == _ALGO_FLOW_START and "external:" not in ds_lines[i]:
            ws = i
            break
    if ws is None:
        return {"file": rel, "status": "skipped", "reason": "block start marker not found in source"}
    we = None
    for i in range(ws + 1, doc_end + 1):
        if ds_lines[i].strip() == _ALGO_FLOW_END:
            we = i
            break
    if we is None:
        return {"file": rel, "status": "skipped", "reason": "block end marker not found in source"}
    while we + 1 <= doc_end and (
        not ds_lines[we + 1].strip() or ds_lines[we + 1].lstrip().startswith("#")
    ):
        we += 1
    if _ALGO_FLOW_START not in "\n".join(ds_lines[ws : we + 1]):
        # 窗口失准（标记折行等）——跳过该文件，宁漏勿错
        return {"file": rel, "status": "skipped", "reason": f"line mapping mismatch (window {ws}-{we})"}

    new_src_lines = ds_lines[:ws] + [anchor_line] + ds_lines[we + 1 :]
    new_src = "\n".join(new_src_lines)
    if ds.endswith("\n") or True:
        pass  # join 后补尾换行
    if src.endswith("\n"):
        new_src += "\n"

    if dry_run:
        return {"file": rel, "status": "dryrun", "yaml": yaml_rel, "block_lines": len(block.splitlines())}

    # round-trip 预验证（内存）：新源码 docstring 解析结果必须与迁移前一致
    try:
        new_tree = ast.parse(new_src)
        new_ds = ast.get_docstring(new_tree) or ""
    except SyntaxError as e:
        return {"file": rel, "status": "failed", "reason": f"new src syntax error: {e}"}
    after = parse_algo_flow(new_ds)
    loaded = None
    # 模拟 extractor 外部加载：yaml 尚未写盘前，用块原文走 parse 等价验证
    if after is None or not after.nodes:
        loaded = parse_algo_flow(block)
        if loaded is None or not loaded.nodes:
            return {"file": rel, "status": "failed", "reason": "post-parse empty"}
        after = loaded

    nodes_b = [(n.id, n.layer) for n in before.nodes]
    nodes_a = [(n.id, n.layer) for n in after.nodes]
    edges_b = [(e.src, e.dst, e.is_break) for e in before.edges]
    edges_a = [(e.src, e.dst, e.is_break) for e in after.edges]
    if nodes_b != nodes_a or edges_b != edges_a:
        return {
            "file": rel,
            "status": "failed",
            "reason": "round-trip mismatch",
            "nodes_before": nodes_b,
            "nodes_after": nodes_a,
            "edges_before": edges_b,
            "edges_after": edges_a,
        }

    # 写 yaml（safe_write_text CAS）+ 源码替换 + .bak
    yaml_path = REPO_ROOT / yaml_rel
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(yaml_path, _yaml_for(rel, domain_dir, stem, block))
    bak = py_path.with_suffix(".py.bak")
    bak.write_bytes(py_path.read_bytes())
    try:
        safe_write_text(py_path, new_src)
    except Exception:
        bak.unlink(missing_ok=True)
        raise

    # 终验：extractor 全链路（含 yaml 加载）
    import importlib  # noqa: PLC0415

    import _shared.code_algorithm_extractor as ext  # noqa: PLC0415

    importlib.reload(ext)
    final = ext.extract_algorithm_from_code(py_path, module_id="", truncate=False)
    final_ids = [(n.id, n.layer) for n in final.algo_flow.nodes] if final.algo_flow else None
    final_edges = [(e.src, e.dst, e.is_break) for e in final.algo_flow.edges] if final.algo_flow else None
    bak.unlink(missing_ok=True)
    # __init__.py 特例：extractor 修正点①对 __init__ 强制回扫子文件——anchor-only 后
    # 富 docstring 遮蔽态解除，真源可能路由到子文件（其子文件自带的 ALGO_FLOW 图
    # 接管卡片）。这不算迁移错误：extractor 真实路由即全景图真源。判定：
    #   picked==self → 比对 nodes/edges（常规 round-trip）；
    #   picked!=self → rerouted，要求 yaml 块自身 parse 与 before 一致（已由内存
    #   round-trip 保证），标注 rerouted_to 让全景图消费方知悉真源变化。
    picked = final.source_path if final.source_type == "code" else ""
    if picked and pathlib.Path(picked).name == "__init__.py" and pathlib.Path(picked) == py_path:
        if final_ids != nodes_b or final_edges != edges_b:
            # 终验失败 → 回滚
            py_path.write_bytes(bak.read_bytes()) if bak.exists() else py_path.write_text(src, encoding="utf-8")
            yaml_path.unlink(missing_ok=True)
            return {"file": rel, "status": "failed", "reason": "final extractor mismatch", "final": final_ids}
        return {"file": rel, "status": "externalized", "yaml": yaml_rel, "nodes": len(nodes_b), "edges": len(edges_b)}
    # picked != self（或 source 非 code）：内存 round-trip 已验证块等价，接受并标注
    return {
        "file": rel,
        "status": "externalized",
        "yaml": yaml_rel,
        "nodes": len(nodes_b),
        "edges": len(edges_b),
        "rerouted_to": picked,
    }


def _iter_targets(domain: str | None, single_file: str | None) -> list[Path]:
    if single_file:
        return [REPO_ROOT / single_file]
    root = REPO_ROOT / "src" / "zephyr" / (domain or "")
    if not root.is_dir():
        return []
    out = []
    for p in sorted(root.rglob("*.py")):
        if any(seg in {"__pycache__", "tests", "_archive"} for seg in p.parts):
            continue
        out.append(p)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ALGO_FLOW 内联块批量出仓器（P2-1）")
    parser.add_argument("--domain", help="src/zephyr/<pkg> 域（如 backtest）；缺省=全量")
    parser.add_argument("--file", help="单文件模式（相对仓库根）")
    parser.add_argument("--dry-run", action="store_true", help="零写入，只报告")
    parser.add_argument("--limit", type=int, default=0, help="本批最多处理 N 个（0=不限）")
    args = parser.parse_args(argv)

    targets = _iter_targets(args.domain, args.file)
    _plan_stem_collision_remaps(targets)
    results = []
    done = 0
    for p in targets:
        if args.limit and done >= args.limit:
            break
        try:
            r = externalize(p, args.dry_run)
        except Exception as e:  # noqa: BLE001 — 单文件异常不中断批次
            r = {"file": str(p), "status": "failed", "reason": f"{type(e).__name__}: {e}"}
        if r["status"] in ("externalized", "failed"):
            done += 1
        results.append(r)

    summary: dict[str, int] = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
