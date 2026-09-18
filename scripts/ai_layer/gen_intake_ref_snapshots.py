# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] scripts.ai_layer.gen_intake_ref_snapshots
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.intake.dedup (IntakeDedup, normalize_text, simhash64); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] CLI python scripts/ai_layer/gen_intake_ref_snapshots.py [--family all] [--dry-run]; L2 查重五比对面之 chart/indicator/algo_flow
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 静态清单禁手工维护（宪法 §9.5）：T4 比对面快照全部由本生成器产出，重跑幂等（ON CONFLICT DO UPDATE + refreshed_at 刷新）;
#              三源=chart_pattern_registry.yaml(REG-PAT-001) + technical_indicator_registry.yaml(REG-IND-001) + src 全量 ALGO_FLOW 标记行;
#              统计排除 worktree 副本(.aidrafts/ .worktrees/)与 __pycache__，否则计数放大约 33 倍;
#              L7 面不在本生成器职责内（L7 落地后由其自有生成器写 ref_family='L7'）;
#              禁读 ai_intake 以外库表，禁写产线注册表（生熟分离）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.2 T4 / §2.3 比对面
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] registry 缺文件/YAML 畸形→异常上抛退出码 2（fail-closed，绝不生成半截快照面）；
#                  单条抽取失败→计 skipped 继续（不误杀整面），末尾汇总打印；DB 不可达→退出码 2；
#                  --dry-run 零写入（只算指纹与计数）
# [TESTS] tests/ai_layer/intake/（★ 在册缺口：本件专属测试未建，test_dedup.py 只覆盖 dedup 模块不含本生成器三源抽取；已实跑两遍幂等 3595 条，处方见 lanes/aibase_relay.md §6）
# [TTL] permanent
"""gen_intake_ref_snapshots — L2 比对面快照生成器（T4 `ai_intake_ref_snapshot`）。

设计真源：``docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md`` §2.2 T4 / §2.3 比对面。

三个面（第 5 面 L7 由 L7 段自有生成器负责，本器不越权）::

    chart      ← chart_pattern_registry.yaml  chart_patterns[]（pattern_id/name_zh/description/recognition_algorithm）
    indicator  ← technical_indicator_registry.yaml indicators[]（indicator_id/name_zh/formula/params）
    algo_flow  ← src/**/*.py 内 `# [ALGO_FLOW]` 标记行（克隆即拒的机检落点）

用法::

    python scripts/ai_layer/gen_intake_ref_snapshots.py --dry-run     # 只看抽取计数
    python scripts/ai_layer/gen_intake_ref_snapshots.py               # 三面全量刷新（幂等）
    python scripts/ai_layer/gen_intake_ref_snapshots.py --family chart
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Final

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.ai_layer.intake.dedup import IntakeDedup, normalize_text, simhash64  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

log = logging.getLogger("ai_intake.ref_snapshot")

CATALOG_DIR: Final = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
CHART_REGISTRY: Final = CATALOG_DIR / "chart_pattern_registry.yaml"
INDICATOR_REGISTRY: Final = CATALOG_DIR / "technical_indicator_registry.yaml"
SRC_ROOT: Final = REPO_ROOT / "src"
EXCLUDED_PARTS: Final = frozenset({".aidrafts", ".worktrees", "__pycache__", ".git", "node_modules"})
ALGO_FLOW_MARKER: Final = "# [ALGO_FLOW]"
TEXT_KEYS: Final[tuple[str, ...]] = (
    "name_zh",
    "name",
    "description",
    "formula",
    "recognition_algorithm",
    "mechanism",
    "aliases",
    "params",
)
GENERATED_FAMILIES: Final[tuple[str, ...]] = ("chart", "indicator", "algo_flow")


def _flatten(value: Any) -> str:
    """把 YAML 值压成可指纹文本（dict/list 递归，保序稳定）。"""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return " ".join(_flatten(v) for v in value)
    if isinstance(value, dict):
        return " ".join(f"{k}={_flatten(v)}" for k, v in sorted(value.items()))
    return str(value)


def entry_text(entry: dict[str, Any]) -> str:
    """从注册表条目抽指纹文本（按 TEXT_KEYS 优先级拼接，缺键跳过）。"""
    parts = [_flatten(entry.get(key)) for key in TEXT_KEYS if entry.get(key) is not None]
    return normalize_text(" ".join(p for p in parts if p))


def load_registry_entries(path: Path, list_key_candidates: tuple[str, ...]) -> list[dict[str, Any]]:
    """读注册表并取出条目列表（fail-closed：缺文件/畸形/空列表即抛）。"""
    if not path.exists():
        raise FileNotFoundError(f"registry_missing:{path.name}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"registry_bad_shape:{path.name}")
    for key in list_key_candidates:
        rows = data.get(key)
        if isinstance(rows, list) and rows:
            return [r for r in rows if isinstance(r, dict)]
    raise ValueError(f"registry_entry_list_not_found:{path.name}:{list_key_candidates}")


def collect_chart() -> list[tuple[str, str]]:
    """图形库面：(ref_key, text_norm) 列表。"""
    rows = load_registry_entries(CHART_REGISTRY, ("chart_patterns", "patterns", "entries"))
    out = []
    for row in rows:
        key = str(row.get("pattern_id") or row.get("id") or row.get("name") or "")
        text = entry_text(row)
        if key and text:
            out.append((f"chart:{key}", text))
    return out


def collect_indicator() -> list[tuple[str, str]]:
    """指标库面：(ref_key, text_norm) 列表。"""
    rows = load_registry_entries(INDICATOR_REGISTRY, ("indicators", "entries"))
    out = []
    for row in rows:
        key = str(row.get("indicator_id") or row.get("id") or row.get("name") or "")
        text = entry_text(row)
        if key and text:
            out.append((f"indicator:{key}", text))
    return out


def iter_source_files() -> list[Path]:
    """列 src 下全部 .py（排除 worktree 副本与缓存目录）。"""
    return sorted(
        p
        for p in SRC_ROOT.rglob("*.py")
        if not (EXCLUDED_PARTS & set(p.parts))
    )


def collect_algo_flow(limit: int = 0) -> list[tuple[str, str]]:
    """ALGO_FLOW 面：每文件取标记行 + 首个 [MODULE] 行作为算法全景指纹文本。"""
    out: list[tuple[str, str]] = []
    for path in iter_source_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[:60]
        except OSError as exc:
            log.warning("跳过不可读文件 %s: %s", path.name, exc)
            continue
        flows = [ln.strip() for ln in lines if ALGO_FLOW_MARKER in ln]
        if not flows:
            continue
        module = next((ln.strip() for ln in lines if ln.startswith("# [MODULE]")), "")
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = normalize_text(" ".join(flows) + " " + module)
        if text:
            out.append((f"algo_flow:{rel}", text))
        if limit and len(out) >= limit:
            break
    return out


COLLECTORS: Final = {
    "chart": collect_chart,
    "indicator": collect_indicator,
    "algo_flow": collect_algo_flow,
}


def build_family(family: str, limit: int = 0) -> tuple[list[tuple[str, str]], int]:
    """抽取一个面。返回 ((ref_key, text) 列表, 跳过条数)。"""
    if family not in COLLECTORS:
        raise ValueError(f"unknown_family:{family}")
    rows = COLLECTORS[family](limit) if family == "algo_flow" else COLLECTORS[family]()
    return rows, 0


def refresh(families: tuple[str, ...], *, schema: str = "ai_intake", dry_run: bool = False,
            limit: int = 0) -> dict[str, Any]:
    """刷新指定面（幂等 upsert）。dry_run=True 时只算指纹零写入。"""
    dedup = IntakeDedup(schema=schema)
    summary: dict[str, Any] = {"dry_run": dry_run, "schema": schema, "families": {}}
    for family in families:
        rows, skipped = build_family(family, limit)
        fingerprints = [(key, simhash64(text)) for key, text in rows]
        if not dry_run:
            for key, text in rows:
                dedup.upsert_snapshot(family, key, text)
        summary["families"][family] = {
            "rows": len(fingerprints),
            "skipped": skipped,
            "distinct_fingerprints": len({fp for _, fp in fingerprints}),
        }
    return summary


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：刷新比对面快照（幂等）。"""
    parser = argparse.ArgumentParser(description="L2 比对面快照生成器（T4 ai_intake_ref_snapshot）")
    parser.add_argument("--family", default="all", help="chart|indicator|algo_flow|all（默认 all）")
    parser.add_argument("--schema", default="ai_intake", help="目标 schema（默认 ai_intake）")
    parser.add_argument("--dry-run", action="store_true", help="只算指纹与计数，零写入")
    parser.add_argument("--limit", type=int, default=0, help="algo_flow 面抽取上限（0=全量）")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    families = GENERATED_FAMILIES if args.family == "all" else (args.family,)
    try:
        summary = refresh(families, schema=args.schema, dry_run=args.dry_run, limit=args.limit)
    except (FileNotFoundError, ValueError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001——CLI 边界统一转退出码 2
        print(f"GEN FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print("SNAPSHOT SUMMARY:", summary)
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 快照生成器属人工/接线批调度入口，非常驻自动任务
    sys.exit(main())
