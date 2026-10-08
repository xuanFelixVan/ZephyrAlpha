# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
#   （对账窗工具，CLI 按需触发——PERM-TRIGGER 代码级检测 argparse/main，permanent 格不可用）
# [STARTUP] manual（对账窗人工/CI 触发——task_bound 格合法值）
# [CONSUMERS] docs/_working/total_command_closeout/wave1a/enforcement_surface_reconciliation.yaml（本脚本自写机生真源）;
#             tests/governance/test_enforcement_surface_reconcile_canary.py（红名单变异自检）;
#             docs/_working/total_command_closeout/wave1a/enforcement_surface_tables.md（人读案卷引用本件数据）
# [MODULE] scripts.governance.meta.enforcement_surface_reconcile
# [A_module] module_id=MOD-ENFORCEMENT-SURFACE-RECONCILE | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar(_trigger_hit/auto_register_gates/REGISTRY_REL_PATH), zephyr.gov_enforcement.rule_bridge.commit_gate_registry.CommitGateRegistry
# [INVARIANTS] 只读生产册（禁改 gate_registry.yaml / in_process_gate_registry.yaml / rules/*.yaml）；进程内实载=真 import 而非读册；
#              确定性输出（无 datetime.now()/time.time()；数据时点取 HEAD commit 时间）；红名单=（enabled 声明却未实载）∪（非空 files_trigger 却 HEAD 全树零命中）。
# [ERROR_CONTRACT] --check 模式红名单非空 → 退出码 1；缺输入/异常 → 打印红因非零退出，禁静默降级。
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [DOMAIN] D_GOV_CODE_QUALITY
# [MATURITY] draft
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
"""enforcement_surface_reconcile.py — 强制面对账生成器（波 1A.3 + 1A.4 内收合一）

一张脚本产两张表（不新造第二个生成器，替代散尺 G-05 与三处各自为政的门禁排查）：

  表①触发面三列对账（1A.3）：in_process_gate_registry.yaml 每台门一行
      = 名册声明(enabled / files_trigger 原文) / 进程内实载(真实注册进引擎的门名集合)
      / files_trigger 在 `git ls-tree -r --name-only HEAD` 全树上的命中文件数。
      任何"声明 enabled 却实载 0"或"非空 files_trigger 却命中 0"自动进红名单并列名。
      —— 一表收敛三悬案：名册 103 vs 实载 99、CREATE-GUARD 空触发每链全跑、密钥门路径子串死触发。

  表②规则↔执法面覆盖（1A.4）：docs/01_policies_and_standards/rules/trae_*.yaml 规则号
      两种写法（册内 TRAE-060 / 门禁文案 trae_060）先别名归一再算覆盖率；
      对每条零匹配规则给二级判定所需字段（catalog 提及 / gate 源码提及），
      区分"被提及"与"真执法"（真执法=进程内可调其判据函数改变结果，本尺只给字段不代裁）。

用法：
    PYTHONPATH=<lane>/src python scripts/governance/meta/enforcement_surface_reconcile.py [--json] [--check] [--no-write]

    --json     打印 JSON 到 stdout
    --check    红名单非空 → 退出码 1（供 CI/gate 消费）
    --no-write 不落盘 yaml（仅计算）

设计约束：恢复门/翻旗标属 Owner 门位，本尺只出事实与选项，绝不改 enabled/任何生产册。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Final

import yaml

from zephyr.shared.infra.process_pool import run_subprocess_hidden

__all__ = [
    "reconcile_trigger_surface",
    "reconcile_rule_coverage",
    "build_cli_result",
    "normalize_rule_token",
]

# ── 路径常量（相对 repo root）───────────────────────────────────────────────
_CATALOGS_DIR: Final = Path("docs") / "01_policies_and_standards" / "_registry" / "catalogs"
ROSTER_REL: Final = str(_CATALOGS_DIR / "in_process_gate_registry.yaml")
CATALOG_REL: Final = str(_CATALOGS_DIR / "gate_registry.yaml")
RULES_GLOB_REL: Final = "docs/01_policies_and_standards/rules"
OUT_YAML_REL: Final = "docs/_working/total_command_closeout/wave1a/enforcement_surface_reconciliation.yaml"
GENERATOR_ID: Final = "scripts/governance/meta/enforcement_surface_reconcile.py"

# 表②执法面 corpus（覆盖判定的检索面；排除 rules/ 自身防自证）。分两层：
#   真执法面 CODE = 门禁实现 + 门禁 spawn 的 checker 脚本（py）——rule 号被"可执行判据"命名。
#   被提及面 CATALOG = 注册册描述（yaml）——rule 号只被散文/目录提及。
# 主覆盖率=真执法面口径（"每条规则是否被某台可执行门禁引用"），零匹配规则再用被提及面做二级判定。
CODE_CORPUS_REL: Final = ("src/zephyr/gov_enforcement", "scripts")
CODE_CORPUS_SUFFIXES: Final = (".py",)
CATALOG_CORPUS_REL: Final = ("docs/01_policies_and_standards/_registry",)
CATALOG_CORPUS_SUFFIXES: Final = (".yaml", ".yml")
_RULES_PREFIX: Final = "docs/01_policies_and_standards/rules/"

# 规则号别名归一：TRAE-060 / trae_060 / trae_60 / TRAE 060 → int 60
_RULE_REF_RE = re.compile(r"trae[\s_\-]?0*(\d{1,3})\b", re.IGNORECASE)


# ── 触发匹配原语（复用装载器真源语义，内收不重写第二套）─────────────────────
def _default_trigger_hit(pattern: str, rel: str) -> bool:
    """缺省命中语义 = gate_auto_registrar._trigger_hit 四路 OR。

    优先复用生产装载器同一个函数（单一真源）；导入失败时回退到逐字等价实现，
    使纯函数在无包环境下亦可被 canary 测试直接调用。
    """
    try:
        from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import _trigger_hit  # noqa: PLC0415

        return _trigger_hit(pattern, rel)
    except Exception:  # noqa: BLE001 — 纯逻辑回退，与生产四路语义一致
        import fnmatch  # noqa: PLC0415

        p = pattern.replace("\\", "/")
        r = rel.replace("\\", "/")
        return (p.endswith("/") and r.startswith(p)) or r == p.rstrip("/") or fnmatch.fnmatch(r, p) or p in r


def _normalize_entry_trigger(entry: dict[str, Any]) -> tuple[str | None, list[str], bool]:
    """把 roster entry 的 files_trigger 归一为 (raw_repr, patterns, always_fire)。

    roster entry 无 files_trigger 键 / None / 空 list / 空串 → always_fire=True（引擎语义：
    spec.files_trigger=() → check_all 不过滤 → 每链全跑，CREATE-GUARD 即此态）。
    list[str] → patterns（非空即过滤）。非 list 标量按装载器拒收语义记 raw 供点名，patterns=[]。
    """
    ft = entry.get("files_trigger")
    if ft is None:
        return (None, [], True)
    if isinstance(ft, list):
        pats = [str(p) for p in ft if isinstance(p, str)]
        return (list(ft), pats, len(pats) == 0)
    # 非常规形态：字符串（如目录册的 ''）→ 空即 always_fire，非空当作单模式待点名
    if isinstance(ft, str):
        s = ft.strip()
        return (ft, [s] if s else [], s == "")
    return (repr(ft), [], False)


# ── 表①：触发面三列对账（纯函数，canary 直接调用）─────────────────────────
def reconcile_trigger_surface(
    roster_entries: list[dict[str, Any]],
    catalog_by_id: dict[str, dict[str, Any]],
    loaded_ids: set[str],
    head_paths: set[str],
    *,
    hit_fn: Callable[[str, str], bool] = _default_trigger_hit,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """对每台在册门算三列 → (rows, red_rows)。

    red 判据（任务口径：严格"声明有、实载 0 或命中 0"）：
      (a) 装载缺口：roster enabled=True 却不在 loaded_ids（名册声明有、实载 0）。
      (b) 死触发：roster files_trigger 非空，且其中某个子模式对 HEAD tracked 全树命中 0
          （密钥门 NO-BARE-GETENV / NO-SECRET-HARDCODE / BARE-SUBPROCESS 的 password/api_key 即此态；
           整表聚合命中可 >0，但死子模式＝执法洞，须点名）。
    enabled=False 的"实载 0"属主动禁用，不进红（归因表另列）。always_fire（空/缺触发，如 CREATE-GUARD）
    不进红（命中＝全链非 0），仅在 always_fire=True 列 surfaced，其"每链全跑成本"在案卷叙述层定性。
    注：catalog 的 always_run 字段不被 auto_register_gates 消费，不作为红判据（否则 67 台设计内
    常跑门被误报），避免尺过蓝反噬其红信号。
    """
    rows: list[dict[str, Any]] = []
    red: list[dict[str, Any]] = []
    for entry in roster_entries:
        gid = str(entry.get("gate_id", ""))
        enabled = bool(entry.get("enabled", True))
        raw, patterns, always_fire = _normalize_entry_trigger(entry)
        cat = catalog_by_id.get(gid, {})
        cat_raw = cat.get("files_trigger")
        loaded = gid in loaded_ids
        per_pattern: dict[str, int] = {}
        if patterns:
            for p in patterns:
                per_pattern[p] = sum(1 for rel in head_paths if hit_fn(p, rel))
            hits = sum(1 for rel in head_paths if any(hit_fn(p, rel) for p in patterns))
        else:
            hits = None  # always_fire / 无过滤：不参与"命中数"，语义=全链
        dead_patterns = sorted(p for p, c in per_pattern.items() if c == 0)
        reasons: list[str] = []
        if enabled and not loaded:
            reasons.append("装载缺口：名册声明 enabled 却未进进程内实载集合")
        if dead_patterns:
            reasons.append(f"死触发：files_trigger 子模式 {dead_patterns} 在 HEAD 全树零命中（疑路径子串误用）")
        row = {
            "gate_id": gid,
            "roster_enabled": enabled,
            "roster_files_trigger_raw": raw,
            "catalog_files_trigger_raw": cat_raw,
            "catalog_always_run": cat.get("always_run"),
            "always_fire": bool(always_fire),
            "in_process_loaded": loaded,
            "trigger_hit_count": hits,
            "trigger_hit_by_pattern": per_pattern,
        }
        if reasons:
            row["red_reason"] = reasons
            red.append({"gate_id": gid, "reason": reasons})
        rows.append(row)
    return rows, red


# ── 表②：规则↔执法面覆盖（纯函数，canary 直接调用）─────────────────────────
def normalize_rule_token(token: str) -> int | None:
    """把一个规则号写法归一为 int（别名归一）。"""
    m = re.match(r"^\s*trae[\s_\-]?0*(\d{1,3})\s*$", token, re.IGNORECASE)
    return int(m.group(1)) if m else None


def reconcile_rule_coverage(
    rule_files: list[str],
    code_corpus_by_path: dict[str, str],
    catalog_corpus_by_path: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """对 rules/ 每文件抽规则号 → 两层执法面判覆盖（别名归一：TRAE-060 == trae_060）。

    返回 (rows, zero_match_rows, stats)。
      code_refs    = 真执法面（门禁代码+checker 脚本）命中的文件；>0 判"真执法"。
      catalog_refs = 被提及面（注册册描述）命中；>0 判"被提及"。
    covered(主口径)= 真执法面命中>0。zero_match(二级判定对象)= 真执法面零命中的规则，
    每条带 code_refs(=0) / catalog_refs / mentioned_broadly 字段供"补执法面/改判据/退役"定性。
    """
    rule_numbers: list[tuple[int, str]] = []  # (num, file)
    for f in rule_files:
        m = re.search(r"trae_0*(\d{1,3})_", Path(f).name, re.IGNORECASE)
        if m:
            rule_numbers.append((int(m.group(1)), f))

    def _refs(corpus: dict[str, str]) -> dict[int, list[str]]:
        acc: dict[int, list[str]] = {}
        for path, text in corpus.items():
            for mm in _RULE_REF_RE.finditer(text):
                acc.setdefault(int(mm.group(1)), []).append(path)
        return {k: sorted(set(v)) for k, v in acc.items()}

    code_map = _refs(code_corpus_by_path)
    cat_map = _refs(catalog_corpus_by_path)

    rows: list[dict[str, Any]] = []
    zero: list[dict[str, Any]] = []
    covered = 0
    for num, f in rule_numbers:
        code_refs = code_map.get(num, [])
        cat_refs = cat_map.get(num, [])
        is_cov = len(code_refs) > 0
        covered += 1 if is_cov else 0
        row = {
            "rule_no": f"{num:03d}",
            "rule_file": f,
            "enforced_in_code": is_cov,
            "code_ref_files": code_refs,
            "code_ref_count": len(code_refs),
            "mentioned_in_catalog": len(cat_refs) > 0,
            "catalog_ref_count": len(cat_refs),
        }
        rows.append(row)
        if not is_cov:
            zero.append(row)
    total = len(rule_numbers)
    stats = {
        "rules_total": total,
        "rules_enforced_in_code": covered,
        "rules_code_zero_match": total - covered,
        "coverage_pct_enforced_in_code": round(covered / total * 100, 1) if total else 0.0,
        "rules_mentioned_in_catalog": sum(1 for r in rows if r["mentioned_in_catalog"]),
        "rules_mentioned_not_enforced": sum(1 for r in rows if r["mentioned_in_catalog"] and not r["enforced_in_code"]),
        "corpus_note": "主覆盖率口径=真执法面(门禁代码+checker脚本 py)；被提及面=注册册 yaml 描述。二者分列，勿与散文册的 80/86 混用。",
    }
    return rows, zero, stats


# ── 采集器（CLI 侧，读生产册只读）──────────────────────────────────────────
def _read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _head_tracked_paths(root: Path) -> set[str]:
    out = run_subprocess_hidden(
        ["git", "ls-tree", "-r", "--name-only", "HEAD"],
        cwd=str(root),
        capture_output=True,
        timeout=60,
    )
    if out.returncode != 0:
        raise RuntimeError(f"git ls-tree HEAD 失败 rc={out.returncode}: {out.stderr.decode('utf-8', 'replace')[:200]}")
    text = out.stdout.decode("utf-8", errors="replace")
    return {ln.strip() for ln in text.splitlines() if ln.strip()}


def _head_commit_time(root: Path) -> str:
    """数据时点=HEAD commit 时间（确定性，不用 datetime.now()，合 RULE-SCHEMA-TZ）。"""
    try:
        out = run_subprocess_hidden(
            ["git", "log", "-1", "--format=%cI", "HEAD"],
            cwd=str(root),
            capture_output=True,
            timeout=15,
        )
        return out.stdout.decode("utf-8", "replace").strip() or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def _in_process_loaded_ids(root: Path) -> tuple[set[str], str]:
    """真·进程内实载：调生产装载器 auto_register_gates 注册进一个空 CommitGateRegistry，
    读其 list_gate_ids()。fail-closed 抛错时也返回已成功注册的集合（register 先于对账）。
    """
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry  # noqa: PLC0415
    from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import auto_register_gates  # noqa: PLC0415

    reg = CommitGateRegistry()
    note = "ok"
    try:
        auto_register_gates(reg, root)
    except Exception as e:  # noqa: BLE001 — 装载器 fail-closed 不影响枚举已注册集合
        note = f"loader-raised: {type(e).__name__}: {str(e)[:300]}"
    return set(reg.list_gate_ids()), note


def _build_catalog_by_id(root: Path) -> dict[str, dict[str, Any]]:
    data = _read_yaml(root / CATALOG_REL) or {}
    out: dict[str, dict[str, Any]] = {}
    for g in data.get("gates", []) or []:
        if isinstance(g, dict):
            out[str(g.get("gate_id", ""))] = g
    return out


def _collect_corpus(root: Path, dirs: tuple[str, ...], suffixes: tuple[str, ...]) -> dict[str, str]:
    corpus: dict[str, str] = {}
    for rel_dir in dirs:
        base = root / rel_dir
        if not base.exists():
            continue
        if base.is_file():
            files = [base]
        else:
            files = [p for p in base.rglob("*") if p.is_file() and p.name.endswith(suffixes)]
        for p in files:
            rp = p.relative_to(root).as_posix()
            if rp.startswith(_RULES_PREFIX):
                continue  # 排除 rules 自身防自证
            try:
                corpus[rp] = p.read_text(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
    return corpus


def build_cli_result(root: Path) -> dict[str, Any]:
    roster = _read_yaml(root / ROSTER_REL) or {}
    entries = roster.get("gates", []) or []
    catalog_by_id = _build_catalog_by_id(root)
    head_paths = _head_tracked_paths(root)
    loaded_ids, load_note = _in_process_loaded_ids(root)

    t1_rows, t1_red = reconcile_trigger_surface(entries, catalog_by_id, loaded_ids, head_paths)

    rule_files = sorted(
        str((Path(RULES_GLOB_REL) / f.name).as_posix()) for f in (root / RULES_GLOB_REL).glob("trae_*.yaml")
    )
    code_corpus = _collect_corpus(root, CODE_CORPUS_REL, CODE_CORPUS_SUFFIXES)
    catalog_corpus = _collect_corpus(root, CATALOG_CORPUS_REL, CATALOG_CORPUS_SUFFIXES)
    t2_rows, t2_zero, t2_stats = reconcile_rule_coverage(rule_files, code_corpus, catalog_corpus)

    # 四台禁用门事实（供归因，恢复动作属 Owner，本尺不代裁）
    disabled_facts = []
    for entry in entries:
        if bool(entry.get("enabled", True)):
            continue
        gid = str(entry.get("gate_id", ""))
        cat = catalog_by_id.get(gid, {})
        disabled_facts.append(
            {
                "gate_id": gid,
                "roster_source": entry.get("source"),
                "catalog_status": cat.get("status"),
                "catalog_files_trigger_raw": cat.get("files_trigger"),
                "in_process_loaded": gid in loaded_ids,
            }
        )

    result = {
        "meta": {
            "generator": GENERATOR_ID,
            "roster_path": ROSTER_REL,
            "catalog_path": CATALOG_REL,
            "code_corpus_dirs": list(CODE_CORPUS_REL),
            "catalog_corpus_dirs": list(CATALOG_CORPUS_REL),
            "data_as_of_head_commit_time": _head_commit_time(root),
            "roster_declared_total_gates": roster.get("total_gates"),
            "roster_entry_count": len(entries),
            "enabled_false_count": len(disabled_facts),
            "in_process_loaded_count": len(loaded_ids),
            "in_process_load_note": load_note,
            "head_tracked_file_count": len(head_paths),
        },
        "table1_trigger_surface": {
            "red_list": t1_red,
            "red_count": len(t1_red),
            "rows": t1_rows,
        },
        "table2_rule_enforcement": {
            "stats": t2_stats,
            "zero_match": t2_zero,
            "rows": t2_rows,
        },
        "disabled_gates_facts": disabled_facts,
    }
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="强制面对账生成器（触发面三列 + 规则执法覆盖）")
    ap.add_argument("--root", default=None, help="仓库根（默认为脚本上溯 4 级即车道根）")
    ap.add_argument("--json", action="store_true", help="打印 JSON 到 stdout")
    ap.add_argument("--check", action="store_true", help="红名单非空 → rc=1")
    ap.add_argument("--no-write", action="store_true", help="不落盘 yaml")
    args = ap.parse_args(argv)

    root = Path(args.root) if args.root else Path(__file__).resolve().parents[3]
    result = build_cli_result(root)

    red_count = result["table1_trigger_surface"]["red_count"]

    if not args.no_write:
        out_path = root / OUT_YAML_REL
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            yaml.safe_dump(result, sort_keys=False, allow_unicode=True, width=100),
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        m = result["meta"]
        t2 = result["table2_rule_enforcement"]["stats"]
        print(
            f"[表①] 名册 {m['roster_entry_count']} / enabled_false {m['enabled_false_count']} / 实载 {m['in_process_loaded_count']}"
        )
        print(f"[表①] 红名单 {red_count} 台：")
        for r in result["table1_trigger_surface"]["red_list"]:
            print(f"   - {r['gate_id']}: {'; '.join(r['reason'])}")
        print(
            f"[表②] 真执法面覆盖率 {t2['rules_enforced_in_code']}/{t2['rules_total']} = {t2['coverage_pct_enforced_in_code']}%；代码零匹配 {t2['rules_code_zero_match']}；被提及未执法 {t2['rules_mentioned_not_enforced']}"
        )
        for z in result["table2_rule_enforcement"]["zero_match"]:
            tag = "被提及(仅册)" if z["mentioned_in_catalog"] else "零提及"
            print(f"   - trae_{z['rule_no']} [{tag}] ({z['rule_file']})")
        if not args.json:
            print(f"[写出] {OUT_YAML_REL}" if not args.no_write else "[写出] 已跳过 (--no-write)")

    if args.check and red_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
