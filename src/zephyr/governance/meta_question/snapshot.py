# noqa: m11-perm-manual-legitimate  M11豁免: 本文件 CLI 入口仅按需机生 YAML 快照（读侧导出，无常驻进程），与 gen_intake_ref_snapshots.py 同类
# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md | §1.3（DB 真源→YAML 只读机生镜像，禁手改）
# [MODULE] zephyr.governance.meta_question.snapshot
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.file_utils (safe_write_text); zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] CLI python -m zephyr.governance.meta_question.snapshot [--from-json PATH]; 未答看板/对账器（读侧，后续接线批）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] RULE-SSOT 判向：问题库=DB 真源，本件产出=YAML 只读机生镜像，禁手改，再生成即全量对账（10§1.3）；
#              全表导出按 q_id 排序（墓碑序稳定）；文件头机生（generated_at UTC ISO / row_count / source 禁手工维护声明）；
#              落盘必经 safe_write_text CAS（20§3.3，哈希不符=重新生成覆盖，禁人工仲裁合并）；
#              --from-json 备用通道仅限 PG 未部署/测试场景，生产对账真源仍为 PG 表
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md §3.3（改落盘纪律先改总册）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达=原样上抛（禁降级直写 YAML，10§9 fail-closed）；--from-json 输入非列表/不可解析=ValueError；
#                  safe_write_text CAS 冲突（StaleWriteRefused）=原样上抛由调用方重生成
# [TESTS] tests/governance/meta_question/test_registry.py（export_snapshot 走 SQLite mock 连接+tmp_path）
# [TTL] permanent
"""snapshot — meta_question_registry 的 YAML 机生快照（只读镜像，再生成即全量对账）。

设计真源：``docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md`` §1.3
+ ``20_management_policy.md`` §3.3（热 YAML 快照 CAS 纪律）。

用法::

    from zephyr.governance.meta_question.snapshot import export_snapshot

    export_snapshot(get_conn, out_path)                    # PG 通道
    python -m zephyr.governance.meta_question.snapshot --from-json rows.json --out out.yaml
# target: src/zephyr/governance/meta_question/snapshot.py (docstring 444 字, 6 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/snapshot.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Final

import yaml

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

_SQL_SNAPSHOT_ALL = "SELECT * FROM {schema}.meta_question ORDER BY q_id"

__all__: Final = ["DEFAULT_SNAPSHOT_PATH", "export_snapshot", "build_snapshot_payload"]

DEFAULT_SNAPSHOT_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "_working" / "chain_piling_campaign" / "snapshots" / "registry_latest.yaml"
)
FORBID_MANUAL_EDIT_DECLARATION: Final[str] = (
    "机生件禁手工维护——真源=PG meta_question 表（RULE-SSOT）；"
    "再生成即全量对账（10_intake_gate_design.md §1.3 / 20_management_policy.md §3.3）"
)

_JSONB_KEYS: Final[frozenset[str]] = frozenset(
    {"data_sources", "exam_plan", "consumers", "provenance", "chain_refs", "evidence_refs"}
)


def _coerce_row(row: dict[str, Any]) -> dict[str, Any]:
    """行值规整：datetime→UTC ISO 字符串；jsonb TEXT→结构化对象（SQLite mock 侧）。"""
    out: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            out[key] = value.isoformat()
        elif key in _JSONB_KEYS and isinstance(value, str):
            try:
                out[key] = json.loads(value)
            except ValueError:
                out[key] = value  # 非 JSON 文本原样保留（禁静默丢数据）
        else:
            out[key] = value
    return out


def build_snapshot_payload(rows: list[dict[str, Any]], *, schema: str) -> dict[str, Any]:
    """组装快照载荷（文件头机生 + questions 按 q_id 排序）。"""
    questions = [_coerce_row(dict(r)) for r in rows]
    questions.sort(key=lambda r: str(r.get("q_id") or ""))
    return {
        "generated_at": now_utc().isoformat(),
        "row_count": len(questions),
        "source": f"zephyr.governance.meta_question.snapshot (schema={schema})",
        "declaration": FORBID_MANUAL_EDIT_DECLARATION,
        "questions": questions,
    }


def export_snapshot(
    get_conn: Callable[..., Any],
    out_path: str | Path,
    *,
    schema: str = "meta_question",
) -> dict[str, Any]:
    """全表导出→YAML 机生快照落盘（safe_write_text CAS）。

    :param get_conn: 连接工厂 ``get_conn(*, read_only=True)``（与 registry 注入口径一致）
    :param out_path: 快照落盘路径（生产=DEFAULT_SNAPSHOT_PATH；测试走 tmp_path）
    :return: ``{"path", "row_count", "generated_at"}`` 摘要
    """
    conn = get_conn(read_only=True)
    try:
        cur = conn.cursor()
        cur.execute(_SQL_SNAPSHOT_ALL.format(schema=schema))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]
    finally:
        conn.close()
    return _dump_payload(build_snapshot_payload(rows, schema=schema), out_path)


def export_snapshot_from_json(
    rows_path: str | Path, out_path: str | Path, *, schema: str = "meta_question"
) -> dict[str, Any]:
    """--from-json 备用通道：PG 未部署/测试场景从 JSON 行清单导出（结构同 PG 导出）。"""
    raw = json.loads(Path(rows_path).read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not all(isinstance(r, dict) for r in raw):
        raise ValueError(f"--from-json 输入须为行对象列表：{rows_path}")
    return _dump_payload(build_snapshot_payload(raw, schema=schema), out_path)


def _dump_payload(payload: dict[str, Any], out_path: str | Path) -> dict[str, Any]:
    text = yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, default_flow_style=False)
    safe_write_text(out_path, text)
    return {
        "path": str(out_path),
        "row_count": int(payload["row_count"]),
        "generated_at": payload["generated_at"],
    }


def main(argv: list[str] | None = None) -> int:
    """CLI：PG 导出（默认）或 --from-json 备用通道。"""
    parser = argparse.ArgumentParser(description="meta_question YAML 机生快照（禁手工维护）")
    parser.add_argument("--out", default=str(DEFAULT_SNAPSHOT_PATH), help="快照落盘路径")
    parser.add_argument("--schema", default="meta_question", help="PG schema 名")
    parser.add_argument(
        "--from-json",
        default=None,
        help="备用通道：从 JSON 行清单文件导出（PG 未部署/测试场景），跳过 PG 连接",
    )
    args = parser.parse_args(argv)
    try:
        if args.from_json:
            summary = export_snapshot_from_json(args.from_json, args.out, schema=args.schema)
        else:
            from zephyr.governance.meta_question.meta_question_registry import MetaQuestionRegistry

            registry = MetaQuestionRegistry(schema=args.schema)
            summary = export_snapshot(registry.get_conn, args.out, schema=args.schema)
        print(f"SNAPSHOT {summary['path']} rows={summary['row_count']} generated_at={summary['generated_at']}")
        return 0
    except Exception as exc:  # noqa: BLE001 ——CLI 边界统一转退出码 2
        print(f"SNAPSHOT FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
