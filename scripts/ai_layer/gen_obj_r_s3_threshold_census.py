# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_obj_r
# [MODULE] scripts.ai_layer.gen_obj_r_s3_threshold_census
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml
#                (只读，gate_id 反查); src/zephyr/gov_enforcement/**（只读文本扫描）
# [CONSUMERS] 无运行时消费者（本件=OBJ_R S3 立案产物生成器，输出 YAML 提案骨架；
#             施工批消费该 YAML 建注册表并改 gate 源码）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 只读采集零改写：本生成器绝不写 src/、绝不改判据值；计数恒为字段
#              （total_* / counts），散文里不得复制数字（宪法 §9.5 静态清单禁手工维护）；
#              判定阈值名启发式集中在此一处（改口径=改本件+重跑，不散落）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_R_rules_standards/DESIGN.md §⑥-S3
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 扫描根缺失 -> FileNotFoundError（fail-closed，不出半份 census）；
#                  YAML 解析失败异常上抛；输出目录不存在则创建
# [TESTS] tests/ai_layer/test_obj_r_s3_threshold_census.py
# [TTL] permanent
"""gen_obj_r_s3_threshold_census — OBJ_R 施工项 S3「阈值外置化」机械普查生成器。

真源：docs/_working/ai_layer_vision/OBJ_R_rules_standards/DESIGN.md §⑥-S3
      （验收标准：外置化提案清单覆盖全部硬编码常量且逐条标真源行号）
母版：同卡 §②-R3 = alert_threshold_registry.yaml（REG-ATH-001）+
      src/zephyr/shared/alerts/threshold_loader.py fail-closed 统读改造（AI-THD-001）。

本件做三件事（且仅此三件）：
  1. 机械扫描被点名的源码面（commit_gates / gov_enforcement 其余子包），按 AST 取
     **模块级数值常量**（int/float/含数值的 tuple·list·dict），不靠 grep 正则漏项；
  2. 分层判定：identity（字符串/结构常量，非阈值）｜non_threshold（位标志/进制掩码类）｜
     threshold（名字或形态像判据）｜already_external（模块已有 config/注册表读取点）；
  3. 产出**提案骨架 YAML**：目标注册表结构（字段沿用 REG-ATH-001 口径+gate 特有字段）
     + 逐常量映射表（file/line/name/value/建议 threshold_id）。

红线（判据不松）：本件是"立案+生成器"，**不改任何代码判据值、不搬常量**——把常量真的
搬进 config 属下一波施工，且须先过内收判据（同真源可派生→必并）。
生成器禁 datetime.now()/time.time()（RULE-SCHEMA-TZ）：as_of 由命令行显式传入。
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Final

import yaml

# create-guard-not-dup: 本件是 OBJ_R S3 阈值常量普查生成器（AST 扫数值常量产提案 YAML），非 drift/depgraph/encoding/consumers 等 scan 类能力的第二实现，命中词=docstring 通用英文语料噪声

_REPO: Final[Path] = (
    Path(__file__).resolve().parents[2]
)  # 私有仓根（SSOT-REDEFINITION：REPO_ROOT 真源=src/zephyr/shared/io/paths.py，仓内脚本惯例=下划线私有别名，对标 run_ai_l1_scan_tick._REPO）

#: 扫描根（被 OBJ_R 卡点名的散落面；新增根=改本表，别处不复制）
SCAN_ROOTS: Final[tuple[str, ...]] = (
    "src/zephyr/gov_enforcement/commit_gates",
    "src/zephyr/gov_enforcement",
)

#: 阈值名启发式（大写常量名含这些语素即视为判据候选）
THRESHOLD_NAME_TOKENS: Final[tuple[str, ...]] = (
    "LIMIT",
    "MAX",
    "MIN",
    "THRESHOLD",
    "CAP",
    "QUOTA",
    "BUDGET",
    "WINDOW",
    "DAYS",
    "SECONDS",
    "MILLISECONDS",
    "PCT",
    "PERCENT",
    "RATIO",
    "SIZE",
    "DEPTH",
    "COUNT",
    "TOP",
    "WIDTH",
    "LENGTH",
    "TIMEOUT",
    "COOLDOWN",
    "STALE",
    "容忍",
    "余量",
)

#: 明确非判据的标识/结构常量名（消歧白名单，逐条带理由）
NON_THRESHOLD_NAME_ALLOWLIST: Final[dict[str, str]] = {
    "REGISTRY_PATH": "路径常量非阈值",
    "POLICY_PATH": "路径常量非阈值",
    "SEVERITY_ORDER": "枚举序非阈值",
    "ALLOWED_SEVERITIES": "枚举集合非阈值",
    "OWN_SCOPE_MARKER": "标记字符串非阈值",
}

#: 算法魔数/位掩码语素（哈希/布隆/位运算基准，外置化无意义）
ALGORITHMIC_MAGIC_TOKENS: Final[tuple[str, ...]] = (
    "PRIME",
    "BASIS",
    "MASK",
    "MAGIC",
    "SEED_SALT",
    "BIT_SHIFT",
)

#: 目标注册表落点（提案态，未施工；命名避开 REG-ATH-001 告警域，防双真源混淆）
PROPOSED_REGISTRY_ID: Final[str] = "REG-GTH-001"
PROPOSED_REGISTRY_PATH: Final[str] = "docs/01_policies_and_standards/_registry/catalogs/gate_threshold_registry.yaml"
DEFAULT_OUT: Final[str] = (
    "docs/_working/ai_layer_vision/OBJ_R_rules_standards/s3_threshold_externalization_proposal_v0.yaml"
)

GATE_REGISTRY_PATH: Final[str] = "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"


@dataclass(frozen=True)
# class-name-alias: 阈值普查结果结构记录（与 clone_guard/gov_enforcement/infrastructure/ml_serve 各自的 Finding 同名不同义、零 import 交互；保字节捞回不改名以维持原车道可追溯性）
class Finding:
    """一条模块级常量命中（两轴正交：是否判据 × 是否已有注入点）。"""

    file: str
    line: int
    name: str
    value_repr: str
    kind: str  # int | float | str | tuple | list | dict | expr | other
    is_threshold: bool  # 判据候选（阈值/配额/时长/容量类数值）
    injection_marker: str  # 模块已有配置读取点标记（空=无）
    annotation: str  # Final / Final[int] / 无
    reason: str  # 判定理由（可溯）


# ---------------------------------------------------------------- 扫描判定


def _numeric_nodes(value: ast.expr) -> list[ast.Constant]:
    """取表达式内全部数值字面量（递归容器）。"""
    hits: list[ast.Constant] = []
    for node in ast.walk(value):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            hits.append(node)
    return hits


def _kind_of(value: ast.expr) -> str:
    if isinstance(value, ast.Constant):
        if isinstance(value.value, bool):
            return "bool"
        if isinstance(value.value, int):
            return "int"
        if isinstance(value.value, float):
            return "float"
        return "str"
    if isinstance(value, ast.Tuple):
        return "tuple"
    if isinstance(value, ast.List):
        return "list"
    if isinstance(value, ast.Dict):
        return "dict"
    if isinstance(value, ast.BinOp):
        return "expr"
    return type(value).__name__


def _is_threshold_name(name: str) -> bool:
    upper = name.upper()
    return any(token in upper for token in THRESHOLD_NAME_TOKENS)


def _already_external(source: str) -> str | None:
    """模块已有配置注入点？返回读取点标记（None=无）。"""
    markers = (
        "threshold_loader",
        "load_alert_thresholds",
        "load_criteria",
        "yaml.safe_load",
        "read_config",
        "config/",
    )
    for marker in markers:
        if marker in source:
            return marker
    return None


def _classify(name: str, kind: str, has_numeric: bool) -> tuple[bool, str]:
    """判据候选判定（is_threshold, reason）——阈值/配额/时长/容量类数值=判据。"""
    upper = name.upper()
    if kind in ("str", "bool") and not has_numeric:
        return False, "字符串/布尔标识常量，非判据"
    if name in NON_THRESHOLD_NAME_ALLOWLIST:
        return False, NON_THRESHOLD_NAME_ALLOWLIST[name]
    if any(token in upper for token in ALGORITHMIC_MAGIC_TOKENS):
        return False, "算法魔数/位掩码基准（哈希/布隆类），外置化无意义"
    if kind == "expr" and not _is_threshold_name(name):
        return False, "位运算/组合表达式且名不含判据语素"
    if _is_threshold_name(name):
        return True, "名含判据语素且值为数值"
    if kind in ("int", "float") and has_numeric:
        return True, "裸数值模块常量（名字未含语素，待人工复看）"
    if has_numeric:
        return True, "容器内含数值（dict/list/tuple 型阈值族）"
    return False, "无数值判据形态"


def scan_file(path: Path, repo_root: Path) -> list[Finding]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    external = _already_external(source)
    rel = path.relative_to(repo_root).as_posix()
    findings: list[Finding] = []
    for node in tree.body:  # 仅模块级（tree.body 顶层）
        if not isinstance(node, ast.Assign | ast.AnnAssign):
            continue
        if isinstance(node, ast.Assign):
            targets = [t for t in node.targets if isinstance(t, ast.Name)]
            value: ast.expr | None = node.value
        else:
            targets = [node.target] if isinstance(node.target, ast.Name) else []
            value = node.value
        if value is None:
            continue
        names = [t.id for t in targets]
        for name in names:
            if not name.isupper():
                continue
            numerics = _numeric_nodes(value)
            kind = _kind_of(value)
            threshold, reason = _classify(name, kind, bool(numerics))
            annotation = ""
            if isinstance(node, ast.AnnAssign) and node.annotation is not None:
                annotation = ast.unparse(node.annotation)
            findings.append(
                Finding(
                    file=rel,
                    line=node.lineno,
                    name=name,
                    value_repr=_mask_marker_literals(ast.unparse(value)[:120]),
                    kind=kind,
                    is_threshold=threshold,
                    injection_marker=external or "",
                    annotation=annotation,
                    reason=reason,
                )
            )
    return findings


def scan_roots(repo_root: Path) -> tuple[list[Finding], dict[str, Any]]:
    seen_files: set[str] = set()
    findings: list[Finding] = []
    roots: list[str] = []
    for rel_root in SCAN_ROOTS:
        root = repo_root / rel_root
        if not root.is_dir():
            raise FileNotFoundError(f"扫描根缺失（fail-closed）：{root}")
        roots.append(rel_root)
        for py in sorted(root.rglob("*.py")):
            rel = py.relative_to(repo_root).as_posix()
            if rel in seen_files:
                continue
            seen_files.add(rel)
            findings.extend(scan_file(py, repo_root))
    stats: dict[str, Any] = {"scan_roots": sorted(set(roots)), "files_scanned": len(seen_files)}
    return findings, stats


# ------------------------------------------------------------ gate_id 反查


def _module_to_file(module_path: str) -> str:
    return "src/" + module_path.replace(".", "/") + ".py"


def load_gate_index(repo_root: Path) -> dict[str, dict[str, Any]]:
    """in_process_gate_registry.yaml -> {源文件相对路径: [gate 条目]}（只读）。"""
    path = repo_root / GATE_REGISTRY_PATH
    if not path.is_file():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    gates = payload.get("gates") or payload.get("entries") or []
    index: dict[str, dict[str, Any]] = {}
    if isinstance(gates, list):
        for gate in gates:
            if not isinstance(gate, dict):
                continue
            module_path = gate.get("module_path")
            if not isinstance(module_path, str):
                continue
            index[_module_to_file(module_path)] = {
                "gate_id": gate.get("gate_id"),
                "priority": gate.get("register_line", gate.get("priority")),
                "enabled": gate.get("enabled"),
                "source": gate.get("source"),
            }
    return index


# ---------------------------------------------------------------- 骨架产出


def threshold_id_for(file: str, name: str, used: set[str]) -> str:
    """建议条目号 THD-GATE-NNN（按文件聚合、稳定可重放）。"""
    stem = Path(file).stem.upper().replace("_", "")
    candidate = f"THD-GATE-{stem}"
    if candidate in used:
        idx = 2
        while f"{candidate}-{idx}" in used:
            idx += 1
        candidate = f"{candidate}-{idx}"
    used.add(candidate)
    return candidate


TARGET_ENTRY_SCHEMA: Final[dict[str, str]] = {
    "threshold_id": "str            # THD-GATE-<源文件>[-N]（本生成器建议值，立案时可改号）",
    "gate_id": "str|None       # 消费 gate（in_process_gate_registry 反查，None=非 gate 件）",
    "priority": "int|None         # 随 gate 条目带出（撞号由 ARCH-GATE-PRIORITY-UNIQUENESS 拦）",
    "name": "str",
    "name_zh": "str",
    "module_path": "str           # src/... 相对路径",
    "source_anchor": "str           # path::CONST 代码锚点（含行号快照）",
    "line_snapshot": "int           # 普查行号（源码漂移后以重跑生成器为准，非判据）",
    "value": "int|float|list|tuple # 现值（=外置化时写进注册表的初值，禁改动）",
    "value_kind": "str            # int/float/tuple/list/dict/expr",
    "unit": "str                  # count/lines/items/seconds/bytes/pct",
    "comparator": "str            # gt/gte/lt/lte/eq（语义由立案批人工填）",
    "severity_action": "str      # 触发后动作（block/warn/…）",
    "owner_gate_required": "bool  # 修订是否触 Owner 门（判据值变更=true）",
    "status": "str                # active/design/deprecated",
    "doc_ref": "str            # 真源锚（OBJ_R 卡/裁定/事故案例）",
    "replay_pair": "str        # §②-C 对照协议挂钩：old/new 常量覆写用例号",
}


def build_payload(findings: list[Finding], stats: dict[str, Any], as_of: date) -> dict[str, Any]:
    gate_index = load_gate_index(_REPO)
    used_ids: set[str] = set()
    entries = [
        {
            "file": f.file,
            "line": f.line,
            "name": f.name,
            "value_repr": f.value_repr,
            "value_kind": f.kind,
            "annotation": f.annotation,
            "is_threshold": f.is_threshold,
            "injection_marker": f.injection_marker,
            "suggested_threshold_id": threshold_id_for(f.file, f.name, used_ids) if f.is_threshold else None,
            "gate_id": (gate_index.get(f.file) or {}).get("gate_id"),
            "priority": (gate_index.get(f.file) or {}).get("priority"),
            "reason": f.reason,
        }
        for f in sorted(findings, key=lambda x: (x.file, x.line))
    ]
    per_file: dict[str, int] = {}
    for finding in findings:
        if finding.is_threshold:
            per_file[finding.file] = per_file.get(finding.file, 0) + 1

    return {
        "meta": {
            "artifact": "OBJ_R S3 阈值外置化提案骨架（机械普查产出）",
            "ttl": "task_bound",
            "session": "st-ailayer-final-20260924",
            "creation_token": "objr-s3-threshold-census-v0-20260926",
            "status": "filed_proposal_only",
            "generated_by": "scripts/ai_layer/gen_obj_r_s3_threshold_census.py",
            "as_of": as_of.isoformat(),
            "design_source": "docs/_working/ai_layer_vision/OBJ_R_rules_standards/DESIGN.md §⑥-S3"
            "（验收：覆盖全部硬编码常量且逐条标真源行号）",
            "master_template": "REG-ATH-001（alert_threshold_registry.yaml）+ threshold_loader.py"
            " fail-closed 统读（AI-THD-001，存量 9 模块码内硬编码已清零）",
            "approval_ref": "Owner 2026-09-26 已批项 #10，见"
            " docs/_working/ai_layer_vision/HANDOFF_st_ailayer_final.md §一",
            "net_zero_note": "本件只出提案不新增生产配置；下一波施工时**优先并入 REG-ATH-001"
            " 既有注册表或新建单册二选一**（内收判据：同域重复簇→收敛唯一），"
            "禁第三套阈值真源",
            "execution_policy": "生成器只读采集——零改写 src/、零搬常量、零改判据值；"
            "重跑即再生（计数与清单不得手工抄进散文）",
            "scan_roots": list(stats["scan_roots"]),
            "classification": {
                "axis_1_is_threshold": "判据候选=数值（或含数值容器）且名含判据语素，或裸数值模块"
                "常量（名字无语素者标注「待人工复看」）；排除标识串/枚举"
                "集合/算法魔数（PRIME/BASIS/MASK 语素）/位运算式",
                "axis_2_injection_marker": "模块文本已含配置读取点（threshold_loader /"
                " load_criteria / yaml.safe_load / config/ 路径）"
                "→ 迁移成本低；两轴正交不互斥",
                "threshold_name_tokens": list(THRESHOLD_NAME_TOKENS),
                "algorithmic_magic_tokens": list(ALGORITHMIC_MAGIC_TOKENS),
                "non_threshold_allowlist": dict(NON_THRESHOLD_NAME_ALLOWLIST),
                "recount_note": "前一波交接书（HANDOFF §一 已批项 #10）记有旧骨架「76 常量」，"
                "其载体随 .runtime 蒸发且口径不可复现——本 census 以本生成器实测"
                "字段为准，散文引用勿抄旧数（宪法 §9.5）",
            },
            "counts": {
                "files_scanned": stats["files_scanned"],
                "module_level_constants_total": len(findings),
                "threshold_candidates": len([f for f in findings if f.is_threshold]),
                "threshold_candidate_files": len(per_file),
                "threshold_candidate_distinct_names": len({f.name for f in findings if f.is_threshold}),
                "threshold_candidates_without_injection_point": len(
                    [f for f in findings if f.is_threshold and not f.injection_marker]
                ),
                "threshold_candidates_with_injection_point": len(
                    [f for f in findings if f.is_threshold and f.injection_marker]
                ),
                "non_threshold_entries": len([f for f in findings if not f.is_threshold]),
                "note": "全部计数由本生成器产出；散文引用请写「见 meta.counts」勿抄数字（宪法 §9.5）",
            },
        },
        "target_config": {
            "registry_id": PROPOSED_REGISTRY_ID,
            "proposed_path": PROPOSED_REGISTRY_PATH,
            "loader": "新增 gate 侧统读器（对标 threshold_loader.py，fail-closed："
            "缺文件/缺条目/类型畸形一律 raise，禁码内第二真源回退）",
            "entry_schema": TARGET_ENTRY_SCHEMA,
            "consumption_contract": [
                "gate 模块顶层常量改为 `_THRESHOLDS = load_gate_thresholds(__name__)` 后"
                "读条目；旧常量名保留为 key（不改语义、不改值）",
                "rule_replay（OBJ_R S1）以注册表 value 作 old 判定，以提案 value 作 new 判定，"
                "跑 §②-E P1-P4 四判据后方可出厂",
                "canary 档（L6 §②-G）：注册表 value 与旧码内常量不等时先 warn 后阻断",
            ],
        },
        "per_file_summary": [
            {"file": file, "threshold_candidates": count}
            for file, count in sorted(per_file.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
        "constants": entries,
    }


def _mask_marker_literals(text: str) -> str:
    """普查产物里不得原样回填门禁乱码标记表的字面量。

    本普查器扫 src 时常量面时会命中 gate_engine 自己的 `_MOJIBAKE_MARKERS` 取样字符串；
    照抄进 YAML 后，ENCODING-SAFETY（INJ-007）按"文件含双重编码乱码"打死整个产物文件
    ——2026-09-26 实测：提案册 274KB 因这一行被整袋拒落。故命中即换占位符，
    保留"此处本有一枚字面量"的事实而不带毒。标记表从门禁侧 import，不在此复制第二份。
    """
    from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import (
        _MOJIBAKE_MARKERS,
    )

    for marker in _MOJIBAKE_MARKERS:
        text = text.replace(marker, "<marker-literal>")
    return text


def write_payload(payload: dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# 机读物（YAML 非 JSON，DCR 口径）；本文件由生成器产出——禁手工维护条目与计数。\n"
        "# 再生成：python scripts/ai_layer/gen_obj_r_s3_threshold_census.py --as-of <YYYY-MM-DD>\n"
    )
    out_path.write_text(
        header + yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
        newline="\n",  # Windows 下 write_text 默认按 os.linesep 换行→8359 处 CRLF 被 INJ-007 报 WARN
    )
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OBJ_R S3 阈值外置化机械普查（只读）")
    parser.add_argument("--as-of", required=True, help="普查基准日 YYYY-MM-DD（生成器禁取系统时间）")
    parser.add_argument("--out", default=DEFAULT_OUT, help="输出 YAML（相对仓根）")
    args = parser.parse_args(argv)
    findings, stats = scan_roots(_REPO)
    payload = build_payload(findings, stats, date.fromisoformat(args.as_of))
    out = write_payload(payload, _REPO / args.out)
    counts = payload["meta"]["counts"]
    print(
        f"扫描文件 {counts['files_scanned']} / 模块级常量 "
        f"{counts['module_level_constants_total']} / 判据候选 "
        f"{counts['threshold_candidates']}（涉 {counts['threshold_candidate_files']} 文件；"
        f"无注入点 {counts['threshold_candidates_without_injection_point']}）"
    )
    print(f"产物：{out.relative_to(_REPO).as_posix()}")
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 普查生成器=立案批次按需手跑 CLI，非常驻自动任务，零事件订阅
    raise SystemExit(main())
