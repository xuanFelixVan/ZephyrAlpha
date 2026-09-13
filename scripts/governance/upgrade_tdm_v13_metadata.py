# [BLUEPRINT] MOD-BT-085 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.governance.upgrade_tdm_v13_metadata
# [DOMAIN] D_DATA
# [DEPENDENCIES] ruamel.yaml; config/trading_decision_map.yaml; backtest_backlog.yaml
# [CONSUMERS] trading_decision_map.yaml（节点治理元数据回填，备忘 96 批1）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] materiality 由 P0 冻结 backlog 脚本化推导（禁手挑）；不改判据本体；CAS 写入；
#   幂等（重复执行结果一致）；verified 证据回填留空（当前无 verified 节点，诚实原则）
# [STABILITY] experimental
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(backlog P0 缺失/CAS 冲突)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-085 | layer=module | stability=experimental | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TDM v1.3 节点治理元数据回填（备忘 96 批1）。

materiality 推导规则：node_id ∈ {P0 冻结对象（testable=true）的 node_ids} → critical；
其余 → normal。decay_scan_frequency：critical=monthly / normal=semiannual（备忘 96 §2.2）。
last_validated_at/validated_by：全部留空（当前无 verified 节点，诚实原则，备忘 §2.1 回填规则）。
"""

from __future__ import annotations

import sys
from pathlib import Path

MAP = Path("config/trading_decision_map.yaml")
BACKLOG = Path("docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml")


def p0_critical_nodes() -> set[str]:
    import yaml

    with BACKLOG.open(encoding="utf-8") as f:
        d = yaml.safe_load(f)
    ids: set[str] = set()
    for obj in d.get("objects", []):
        if str(obj.get("object_id", "")).startswith("BT-P0") and obj.get("testable"):
            for nid in obj.get("node_ids", []) or []:
                ids.add(str(nid))
    if not ids:
        raise RuntimeError("backlog 无 P0 testable 对象——推导失败")
    return ids


def main() -> None:
    from ruamel.yaml import YAML
    from ruamel.yaml.scalarstring import PlainScalarString

    from zephyr.shared.io.file_utils import content_sha256, safe_write_text

    critical = p0_critical_nodes()
    yaml_rt = YAML()
    yaml_rt.preserve_quotes = True
    raw = MAP.read_text(encoding="utf-8")
    base = content_sha256(raw)
    data = yaml_rt.load(raw)
    nodes = data.get("nodes", [])
    changed = 0
    for node in nodes:
        nid = str(node.get("node_id", ""))
        mat = "critical" if nid in critical else "normal"
        freq = "monthly" if mat == "critical" else "semiannual"
        if node.get("materiality") != mat:
            node["materiality"] = PlainScalarString(mat)
            changed += 1
        if node.get("decay_scan_frequency") != freq:
            node["decay_scan_frequency"] = PlainScalarString(freq)
            changed += 1
        # last_validated_at / validated_by：无 verified 节点，留空（诚实）
    from io import StringIO

    buf = StringIO()
    yaml_rt.dump(data, buf)
    new_text = buf.getvalue()
    r = safe_write_text(MAP, new_text, expected_base_sha256=base, encoding="utf-8", newline="")
    print("write:", r.written, "| critical nodes:", len(critical & {str(n.get('node_id', '')) for n in nodes}),
          "| fields changed:", changed)
    chk = yaml_rt.load(MAP.read_text(encoding="utf-8"))
    mats = {}
    for n in chk.get("nodes", []):
        mats[n.get("materiality")] = mats.get(n.get("materiality"), 0) + 1
    print("verify materiality dist:", mats)


if __name__ == "__main__":
    sys.exit(main())
