# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] scripts.ai_layer.gen_heritage_dedup_snapshot
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.heritage.store (HeritageStore.snapshot_faces);
#                zephyr.ai_layer.intake.dedup (IntakeDedup.upsert_snapshot——T4 写入复用 L2 原语);
#                zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] CLI python scripts/ai_layer/gen_heritage_dedup_snapshot.py [--if-dirty] [--dry-run];
#             登记闸/降级路径 mark_snapshot_dirty 为触发源；月度体检窗兜底（L1 §2.6 同宿主）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 静态清单禁手工维护（宪法 §9.5）：T4 ref_family='L7' 面全部由本生成器产出，幂等重刷
#              （ON CONFLICT DO UPDATE + refreshed_at 刷新，L2 upsert_snapshot 原语复用）;
#              只写本 family='L7' 行，chart/indicator/algo_flow 三族零触碰（T4 写入权按 ref_family 划分，§2.4）;
#              入快照面=V2 缺陷全量（已踩坑防再进）+V1 精英每格 top3（已有赢家防换皮进货）;
#              刷新时点=传承条目登记/降级后（snapshot_dirty 标记）+月度兜底；完成发 intake_heritage_baseline
#              轻事件到本段 outbox（只发 elite|pattern 两 kind+count、不收阴性——红蓝 R1-B5 契约）;
#              生熟分离：只读 ai_heritage、只写 ai_intake T4 的 L7 family 行
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.4（快照时点与快照面裁定）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ai_heritage schema 缺件/ai_intake 不可达→异常上抛退出码 2（fail-closed，绝不生成半截快照面）;
#                  --dry-run 零写入（只算计数）; 单行 upsert 失败→中断回滚该行并上抛（幂等重跑补齐）
# [TESTS] tests/ai_layer/heritage/test_heritage_snapshot.py（幂等重刷 refreshed_at/他族行零触碰/
#         baseline outbox 只发 elite|pattern/dry-run 零写入）
"""gen_heritage_dedup_snapshot — L2 比对面第 5 族快照生成器（T4 `ref_family='L7'`）。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §2.4（回流接线：L2 查重基线）。
chart/indicator/algo_flow 三族由 ``gen_intake_ref_snapshots.py`` 管（其头注明 L7 面不在其职责内），
本器只写 ``ref_family='L7'`` 族——写入权按 ref_family 划分，防双头登记。

用法::

    python scripts/ai_layer/gen_heritage_dedup_snapshot.py --dry-run   # 只看快照面计数
    python scripts/ai_layer/gen_heritage_dedup_snapshot.py             # 全量刷新（幂等）
    python scripts/ai_layer/gen_heritage_dedup_snapshot.py --if-dirty  # 有脏标记才刷（登记/降级后 24h 内触发面）
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.ai_layer.heritage.store import DEFAULT_STATE_DIR, HeritageStore  # noqa: E402
from zephyr.ai_layer.intake.dedup import IntakeDedup  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

log = logging.getLogger("ai_heritage.snapshot")

HERITAGE_FAMILY: Final = "L7"
BASELINE_OUTBOX_NAME: Final = "baseline_events.jsonl"
BASELINE_KINDS: Final[tuple[str, ...]] = ("elite", "pattern")  # 红蓝 R1-B5：只发两 kind+count、不收阴性


def _write_baseline_outbox(outbox_path: Path, faces: dict[str, list[dict[str, Any]]]) -> int:
    """intake_heritage_baseline 轻事件落本段 outbox（L2 侧 journal 消费接线随 L2 批次，禁改其文件）。"""
    outbox_path.parent.mkdir(parents=True, exist_ok=True)
    day = now_utc().strftime("%Y%m%d")
    written = 0
    kind_by_face = {"elite": "elite", "defect": "pattern"}
    with outbox_path.open("a", encoding="utf-8") as handle:
        for face, baseline_kind in kind_by_face.items():
            if baseline_kind not in BASELINE_KINDS:
                continue
            payload = {
                "baseline_ref": f"ai_heritage:{day}:{face}",
                "kind": baseline_kind,
                "count": len(faces.get(face) or []),
                "emitted_at": now_utc().isoformat(),
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            written += 1
    return written


def refresh(
    heritage_store: HeritageStore,
    intake_dedup: IntakeDedup,
    *,
    dry_run: bool = False,
    state_dir: Path | None = None,
) -> dict[str, Any]:
    """刷新 T4 L7 族快照（幂等）。返回各面计数与 outbox 写入数。

    :param heritage_store: 传承库读面（V1/V2 源）
    :param intake_dedup: L2 T4 写入器（schema 白名单内，只落 ref_family='L7'）
    :param dry_run: True=只算计数零写入
    :param state_dir: baseline outbox 目录（缺省 .runtime/ai_heritage）
    """
    faces = heritage_store.snapshot_faces()
    summary: dict[str, Any] = {"dry_run": dry_run, "faces": {}}
    if not dry_run:
        for face_rows in faces.values():
            for row in face_rows:
                intake_dedup.upsert_snapshot(HERITAGE_FAMILY, row["ref_key"], row["text_norm"])
        baseline_dir = state_dir or DEFAULT_STATE_DIR
        summary["baseline_events"] = _write_baseline_outbox(
            baseline_dir / BASELINE_OUTBOX_NAME, faces
        )
        heritage_store.clear_dirty_marker()
    for name, rows in faces.items():
        summary["faces"][name] = len(rows)
    log.info("heritage 快照刷新完成：%s", summary["faces"])
    return summary


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：刷新 T4 ref_family='L7' 快照（幂等）。"""
    parser = argparse.ArgumentParser(description="L7 传承库 T4 查重快照生成器（ref_family='L7'）")
    parser.add_argument("--heritage-schema", default="ai_heritage", help="传承库 schema")
    parser.add_argument("--intake-schema", default="ai_intake", help="T4 所在 schema（L2 白名单）")
    parser.add_argument("--if-dirty", action="store_true", help="有 snapshot_dirty 标记才刷新")
    parser.add_argument("--dry-run", action="store_true", help="只算快照面计数，零写入")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        store = HeritageStore(args.heritage_schema)
        if args.if_dirty and store.dirty_since() is None:
            print("SNAPSHOT SKIP: no dirty marker（登记/降级后未变化）")
            return 0
        dedup = IntakeDedup(schema=args.intake_schema)
        summary = refresh(store, dedup, dry_run=args.dry_run)
        print("SNAPSHOT SUMMARY:", summary)
        return 0
    except Exception as exc:  # noqa: BLE001——CLI 边界统一转退出码 2（schema 缺件/不可达等）
        print(f"GEN FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 快照生成器属人工/体检窗调度入口，非常驻自动任务
    sys.exit(main())
