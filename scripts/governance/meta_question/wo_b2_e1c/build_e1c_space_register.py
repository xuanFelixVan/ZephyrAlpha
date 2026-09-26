# [BLUEPRINT] MOD-CHAINPILE-METAQ | 11_template_generator_design.md §6（组合空间预注册：space_hash 机生）
# [MODULE] scripts.governance.meta_question.wo_b2_e1c.build_e1c_space_register
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] data/registers/metaq_e1c/e1c_space_design_cmb_e1c_v1.yaml（决策面真源）;
#                 docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml（积木族实读）;
#                 gplearn.functions（算子域实读，库=真源）; e1c_ledger（哈希/结构计数/词表）
# [CONSUMERS] apply_e1c_ledgers.py --register（把本件产物同步进 PG metaq_e1c 台账）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 静态清单禁手工维护 [宪法§9.5]：取值域成员/计数/space_hash 全由本件实读派生，
#              人工只改设计面 YAML（槽结构/约束/容量），不手填值清单；
#              时戳经 now_utc() 注入（RULE-SCHEMA-TZ 生成器纪律：禁 datetime.now()/time.time()）；
#              --check 模式做"取值域漂移→space_hash 变更"对账（机检禁事后扩空间的入口）。
# [MODIFY-GUARD] data/registers/metaq_e1c/e1c_space_cmb_e1c_v1.yaml 为本件产物，禁手工编辑
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 域解析为空->ValueError 拒写（空域=假预注册）；--check 漂移->退出码 5 并列差异。
# [TESTS] python scripts/governance/meta_question/wo_b2_e1c/build_e1c_space_register.py --check
# [A_module] module_id=MOD-CHAINPILE-METAQ | layer=script | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""生成 E1C 组合空间预注册册（机生：取值域实读 + 名义/可行计数 + space_hash）。

用法::

    python .../build_e1c_space_register.py            # 生成/刷新 e1c_space_cmb_e1c_v1.yaml
    python .../build_e1c_space_register.py --check    # 只比对：域漂移/hash 变更则非零退出
    python .../build_e1c_space_register.py --print    # 打到 stdout（排障）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Final

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import e1c_ledger as led  # noqa: E402

_FACTOR_REGISTRY: Final = led._REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml"  # noqa: SLF001,E501
_PRIMITIVE_RE: Final = re.compile(r"^[a-z]{2,6}\d$")


def _block_entry(item: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    """单条因子登记 → (bid, 积木元数据)；无 factor_id/name 的条目返回 None。"""
    bid = str(item.get("factor_id") or item.get("name") or "").strip()
    if not bid:
        return None
    status = str(item.get("status") or "").strip().lower()
    formula = str(item.get("formula") or "").strip()
    fam = str(item.get("factor_class") or "(未分类)").strip() or "(未分类)"
    entry = {
        "frequency": str(item.get("frequency") or "").strip().lower(),
        "block_family": fam,
        "fingerprint": led.sha256_hex(
            {
                "factor_class": fam,
                "formula": formula,
                "params": canonical_params(item.get("params")),
            }
        )[:16],
        "eligible": status not in {"deprecated", "retired"} and bool(formula),
        "status": status or "(空)",
    }
    return bid, entry


def _resolve_blocks() -> tuple[dict[str, dict[str, Any]], list[str], dict[str, int]]:
    """积木域=因子登记表实读条目；同时产出族分层与资格/指纹元数据（结构口径 N_eff 的输入）。

    资格判据（constraints.eligibility）：status ∉ {deprecated, retired} 且 formula 非空
    （knowledge_only/未量化条目不可复算→不得进组合空间）。
    指纹（constraints.fingerprint_dedup）：sha256(factor_class|formula|params)[:16]，同指纹=马甲。
    """
    import yaml

    doc = yaml.safe_load(_FACTOR_REGISTRY.read_text(encoding="utf-8"))
    factors = doc.get("factors") or []
    if not factors:
        msg = f"因子登记表无条目，积木域不可解析: {_FACTOR_REGISTRY}"
        raise ValueError(msg)
    blocks: dict[str, dict[str, Any]] = {}
    families: set[str] = set()
    for item in factors:
        resolved = _block_entry(item)
        if resolved is None:
            continue
        bid, entry = resolved
        families.add(entry["block_family"])
        blocks[bid] = entry
    if len(blocks) < 10:
        msg = f"积木域解析异常（仅 {len(blocks)} 条），拒写预注册册"
        raise ValueError(msg)
    return (
        blocks,
        sorted(families),
        {
            "blocks_total": len(blocks),
            "blocks_eligible": sum(1 for b in blocks.values() if b["eligible"]),
        },
    )


def canonical_params(raw: Any) -> Any:
    """params 归一（list/dict/标量混用是登记册常态）——只为指纹稳定，不改语义。"""
    return raw if raw is not None else ""


def _resolve_operators() -> tuple[list[str], str]:
    """算子域=gplearn 导出基元（库自身为真源，按 <name><arity> 命名约定取用）。"""
    import gplearn.functions as gf

    names = sorted(n for n in dir(gf) if _PRIMITIVE_RE.match(n))
    if len(names) < 4:
        msg = f"gplearn 基元解析异常（仅 {names}）"
        raise ValueError(msg)
    return names, getattr(gf, "__name__", "gplearn.functions") + "@" + str(
        getattr(sys.modules.get("gplearn"), "__version__", "unknown")
    )


def build_space(as_of_iso: str) -> dict[str, Any]:
    import yaml

    design = yaml.safe_load((led.REGISTER_DIR / led.DESIGN_FILE).read_text(encoding="utf-8"))
    blocks, families, fam_summary = _resolve_blocks()
    operators, operator_source = _resolve_operators()
    windows = sorted(led.load_vocab("window"))
    tracks = sorted(led.load_vocab("track"))

    counts = led.structural_counts(blocks, operators, windows, tracks)
    cartesian = {"mode": "cartesian", "values": []}
    slots = {
        "block": {
            **cartesian,
            "domain_ref": design["slots"]["block"]["domain_ref"],
            "values": sorted(blocks),
            "blocks": blocks,
            "source_fingerprint": led.sha256_hex(_FACTOR_REGISTRY.read_bytes())[:16],
        },
        "block_family": {
            "mode": "attribute",
            "domain_ref": design["slots"]["block_family"]["domain_ref"],
            "values": families,
            "summary": fam_summary,
        },
        "operator": {
            **cartesian,
            "domain_ref": design["slots"]["operator"]["domain_ref"],
            "values": operators,
            "source_fingerprint": operator_source,
        },
        "window": {
            **cartesian,
            "domain_ref": design["slots"]["window"]["domain_ref"],
            "values": windows,
            "source_fingerprint": "metaq_e1c_window_vocabulary",
        },
        "track": {
            **cartesian,
            "domain_ref": design["slots"]["track"]["domain_ref"],
            "values": tracks,
            "source_fingerprint": "metaq_e1c_track_vocabulary",
        },
    }
    space: dict[str, Any] = {
        "space_id": design["space_id"],
        "version": design["version"],
        "tpl_ref": design["tpl_ref"],
        "cartesian_plan": design["cartesian_plan"],
        "slots": slots,
        "constraints": design["constraints"],
        "cap_template": design["cap_template"],
        "cap_batch": design["cap_batch"],
        "nominal_count": counts["nominal_count"],
        "feasible_count": counts["feasible_count"],
        "_design_ref": f"data/registers/metaq_e1c/{led.DESIGN_FILE}",
        "generated_at": as_of_iso,
    }
    space["space_hash"] = led.space_hash_of(space)
    space["n_eff_structural"] = led.n_eff_structural(space)
    space["seal_policy"] = design["seal_policy"]
    space["applies_to_questions"] = design["applies_to_questions"]
    return space


def main(argv: list[str] | None = None) -> int:
    from zephyr.shared.utils.time_utils import now_utc  # 时戳唯一合法取法（RULE-SCHEMA-TZ 生成器纪律）

    parser = argparse.ArgumentParser(description="生成 E1C 组合空间预注册册")
    parser.add_argument("--check", action="store_true", help="只与在册产物比对（漂移→退出码 5）")
    parser.add_argument("--print", dest="to_stdout", action="store_true", help="输出到 stdout")
    args = parser.parse_args(argv)

    import yaml

    space = build_space(now_utc().isoformat())
    target = led.REGISTER_DIR / led.SPACE_REGISTER_FILE
    doc = {
        "module_id": "MOD-CHAINPILE-METAQ",
        "ttl": "permanent",
        "doc_type": "e1c_space_register",
        "generated_by": "scripts/governance/meta_question/wo_b2_e1c/build_e1c_space_register.py",
        "hand_edit": "forbidden",
        **space,
    }
    rendered = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=110)
    if args.to_stdout:
        print(rendered)
        return 0
    if args.check:
        if not target.exists():
            print(f"[CHECK-FAIL] 预注册册缺失: {target}")
            return 5
        old = yaml.safe_load(target.read_text(encoding="utf-8"))
        diffs = [
            f"{k}: 在册={old.get(k)} 现算={space.get(k)}"
            for k in ("space_hash", "nominal_count", "feasible_count")
            if old.get(k) != space.get(k)
        ]
        for slot in space["slots"]:
            if sorted(map(str, (old.get("slots") or {}).get(slot, {}).get("values", []))) != sorted(
                map(str, space["slots"][slot]["values"])
            ):
                diffs.append(f"槽 {slot} 取值域漂移（扩缩=新 space_hash+expand/seal 流水，禁事后扩空间）")
        if diffs:
            print("[CHECK-FAIL] " + "；".join(diffs))
            return 5
        print(f"[CHECK-OK] space_hash={space['space_hash'][:16]}… 无漂移")
        return 0
    led.REGISTER_DIR.mkdir(parents=True, exist_ok=True)
    from zephyr.shared.io.file_utils import safe_write_text

    safe_write_text(target, rendered)  # 热文件 CAS 写（宪法硬规则 13）
    print(f"[written] {target}")
    print(f"  space_hash={space['space_hash']}")
    print(
        f"  槽基数={ {k: len(v['values']) for k, v in space['slots'].items()} } "
        f"名义={space['nominal_count']} 可行={space['feasible_count']} "
        f"结构 N_eff 比={space['n_eff_structural']['ratio']:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
