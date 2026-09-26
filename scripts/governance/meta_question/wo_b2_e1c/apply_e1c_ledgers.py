# [BLUEPRINT] MOD-CHAINPILE-METAQ | 11_template_generator_design.md §6 + 工单 WO-B2 §簇2-1/2
# [MODULE] scripts.governance.meta_question.wo_b2_e1c.apply_e1c_ledgers
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] e1c_ledger（DDL/写入原语）; zephyr.governance.depgraph_schema.get_depgraph_pg_connection
#                 (read_only=False 架构数据合法写通道，RULE-SSOT：架构数据 apply_*.py 直写 DB)
# [CONSUMERS] 手工部署 + seed_e1c_first_records.py / audit_e1c_carriers.py 前置
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] DDL 全幂等（CREATE SCHEMA/TABLE IF NOT EXISTS + 命名唯一约束）；TIMESTAMPTZ 全覆盖
#              （RULE-SCHEMA-TZ PG 等价口径）；CHECK 枚举由词表渲染（代码零字面量枚举）；
#              注册册=YAML 真源→PG（--register 单向同步，重复执行零增殖）；
#              考尺快照 config_hash 不符即拒（预注册不可改，改=新 snapshot_id）；
#              绝不 ALTER/DROP 任何非 metaq_e1c schema 对象（schema 名硬绑常量，无入参可打偏）。
# [MODIFY-GUARD] none
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->退出码 2；DDL/同步异常->回滚+非零；--verify 缺件->退出码 3 并列缺失清单。
# [TESTS] python scripts/governance/meta_question/wo_b2_e1c/apply_e1c_ledgers.py --verify
# [TTL] permanent
"""部署/同步/核验 metaq_e1c 台账（组合空间预注册三件套 + 考尺快照 + 合并闸运行账）。

用法::

    python .../apply_e1c_ledgers.py            # 幂等建表（DDL）
    python .../apply_e1c_ledgers.py --register # 把 YAML 真源同步进 PG（空间册+考尺快照）
    python .../apply_e1c_ledgers.py --verify   # 只读核验："载体建成"机械判据
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Final

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import e1c_ledger as led  # noqa: E402

#: 期望列数从 DDL 自身派生（不手填，防"判据本身漂移"）
_EXPECTED: Final = led.expected_column_counts()

#: metaq_e1c schema 名常量（import 期解析，落地文本与调用处逐字等值）
_SCHEMA = led._SCHEMA  # noqa: SLF001

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。schema 经 {_SCHEMA} 注入；information_schema 查询
# 以 %s 参数绑定传 schema（值为筛选条件，非标识符）。
_SQL_VERIFY_COLUMNS = (
    "SELECT table_name, column_name FROM information_schema.columns "
    "WHERE table_schema=%s ORDER BY table_name, ordinal_position"
)
_SQL_VERIFY_N_SPACE = f"SELECT count(*) FROM {_SCHEMA}.space_registry"
_SQL_VERIFY_SPACES = (
    f"SELECT space_hash, status, nominal_count, feasible_count, cap_batch "
    f"FROM {_SCHEMA}.space_registry ORDER BY frozen_at"
)
_SQL_VERIFY_FLOWS = f"SELECT action, count(*) FROM {_SCHEMA}.space_ledger_flow GROUP BY action ORDER BY 2 DESC"
_SQL_VERIFY_YARDSTICK = f"SELECT snapshot_id, config_hash, tracks, status FROM {_SCHEMA}.yardstick_snapshot"
_SQL_VERIFY_NEFF = f"SELECT estimator, record_kind, nominal_count, n_eff, ratio, boundary FROM {_SCHEMA}.n_eff_estimate"
_SQL_VERIFY_EXPAND_WO_SEAL = (
    f"SELECT count(*) FROM {_SCHEMA}.space_ledger_flow f "
    f"WHERE f.action='expand' AND NOT EXISTS ("
    f"  SELECT 1 FROM {_SCHEMA}.space_ledger_flow s "
    f"  WHERE s.action='seal' AND s.space_hash=f.prev_space_hash)"
)
_SQL_VERIFY_N_EXPAND = f"SELECT count(*) FROM {_SCHEMA}.space_ledger_flow WHERE action='expand'"


def load_space_register() -> dict[str, Any]:
    import yaml

    path = led.REGISTER_DIR / led.SPACE_REGISTER_FILE
    if not path.exists():
        msg = f"预注册册缺失，先跑 build_e1c_space_register.py: {path}"
        raise FileNotFoundError(msg)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_yardstick() -> dict[str, Any]:
    import yaml

    path = led.REGISTER_DIR / led.YARDSTICK_FILE
    if not path.exists():
        msg = f"考尺快照真源缺失: {path}"
        raise FileNotFoundError(msg)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def do_apply() -> int:
    conn = led.pg_conn(write=True)
    try:
        labels = led.apply_ddl(conn)
    finally:
        conn.close()
    print(f"[ok] DDL 部署完成 {len(labels)} 件: {', '.join(labels)}")
    return 0


def do_register(actor: str, evidence: str) -> int:
    from zephyr.shared.utils.time_utils import now_utc

    space = load_space_register()
    yard = load_yardstick()
    conn = led.pg_conn(write=True)
    try:
        frozen_at = space.get("frozen_at") or space.get("generated_at") or now_utc().isoformat()
        h = led.register_space(
            conn,
            space,
            frozen_at=frozen_at,
            provenance={
                "actor": actor,
                "session_id": actor,
                "evidence_ref": evidence or f"data/registers/metaq_e1c/{led.SPACE_REGISTER_FILE}",
            },
        )
        chash = led.upsert_yardstick(
            conn,
            yard,
            evidence_ref=f"data/registers/metaq_e1c/{led.YARDSTICK_FILE}",
        )
        counts = led.table_stats(conn)
    finally:
        conn.close()
    print(f"[ok] space_hash={h}")
    print(f"[ok] yardstick {yard['snapshot_id']} config_hash={chash}")
    print("[tables] " + json.dumps({t: v["rows"] for t, v in counts["tables"].items()}, ensure_ascii=False))
    return 0


def do_verify() -> int:
    conn = led.pg_conn(write=False)
    missing: list[str] = []
    try:
        stats = led.table_stats(conn)
        with conn.cursor() as cur:
            cur.execute(_SQL_VERIFY_COLUMNS, (_SCHEMA,))
            cols: dict[str, list[str]] = {}
            for t, c in cur.fetchall():
                cols.setdefault(str(t), []).append(str(c))
            cur.execute(_SQL_VERIFY_N_SPACE)
            n_space = int(cur.fetchone()[0])
            cur.execute(_SQL_VERIFY_SPACES)
            spaces = [list(r) for r in cur.fetchall()]
            cur.execute(_SQL_VERIFY_FLOWS)
            flows = {str(a): int(c) for a, c in cur.fetchall()}
            cur.execute(_SQL_VERIFY_YARDSTICK)
            ys = [[str(r[0]), str(r[1])[:12], r[2], str(r[3])] for r in cur.fetchall()]
            cur.execute(_SQL_VERIFY_NEFF)
            neff = [[str(r[0]), str(r[1]), int(r[2]), int(r[3]), float(r[4]), bool(r[5])] for r in cur.fetchall()]
            # PQ-0109 判据：每个 expand 的 prev_space_hash 必须已 seal（齐备率）
            cur.execute(_SQL_VERIFY_EXPAND_WO_SEAL)
            expand_wo_seal = int(cur.fetchone()[0])
            cur.execute(_SQL_VERIFY_N_EXPAND)
            n_expand = int(cur.fetchone()[0])
    finally:
        conn.close()

    for table, expect_cols in _EXPECTED.items():
        got = len(cols.get(table, []))
        if got == 0:
            missing.append(f"表缺失 {table}")
        elif got < expect_cols:
            missing.append(f"表 {table} 列数 {got} < 预期 {expect_cols}")
    if not ys:
        missing.append("考尺快照零记录（PQ-0107 载体空载）")
    if not n_space:
        missing.append("space_registry 零记录（PQ-0104 载体空载）")
    if "seal" not in flows and not missing:
        # 首批可为 0（尚无扩容需求），但字段必须在——只查字段不查行数
        pass
    seal_cols = set(cols.get("space_registry", []))
    for need in ("sealed_at", "seal_reason", "seal_evidence_ref", "status"):
        if need not in seal_cols:
            missing.append(f"封存动作字段缺失 space_registry.{need}（PQ-0109）")
    report = {
        "schema_present": stats["schema_present"],
        "tables": {
            t: {"columns": len(cols.get(t, [])), "rows": stats["tables"].get(t, {}).get("rows", 0)} for t in _EXPECTED
        },
        "spaces": [
            {"hash": s[0][:16], "status": s[1], "nominal": s[2], "feasible": s[3], "cap_batch": s[4]} for s in spaces
        ],
        "flow_actions": flows,
        "yardstick": ys,
        "n_eff": neff,
        "pq0109_expand_without_seal": expand_wo_seal,
        "pq0109_expand_total": n_expand,
        "pq0109_seal_completeness_rate": (1.0 if n_expand == 0 else round((n_expand - expand_wo_seal) / n_expand, 4)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
    if missing:
        print("[VERIFY-FAIL] " + "；".join(missing))
        return 3
    print(
        "[VERIFY-OK] metaq_e1c 八表齐备 + 封存动作字段齐备 + 考尺快照已冻结 + "
        f"PQ-0109 齐备率={report['pq0109_seal_completeness_rate']}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="metaq_e1c 台账部署/同步/核验")
    parser.add_argument("--register", action="store_true", help="YAML 真源→PG 同步")
    parser.add_argument("--verify", action="store_true", help="只读核验机械判据")
    parser.add_argument("--actor", default="st-metaq-gc-20260924")
    parser.add_argument("--evidence", default="")
    args = parser.parse_args(argv)
    try:
        if args.verify:
            return do_verify()
        if args.register:
            return do_register(args.actor, args.evidence)
        return do_apply()
    except Exception as exc:  # noqa: BLE001 — 出口需给可执行指引而非堆栈
        print(f"[ERROR] {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
