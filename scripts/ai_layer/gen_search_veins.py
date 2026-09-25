# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [MODULE] scripts.ai_layer.gen_search_veins
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.io.file_utils (safe_write_text, CAS 热文件纪律);
#                zephyr.shared.io.paths (REPO_ROOT); PyYAML
# [CONSUMERS] CLI python scripts/ai_layer/gen_search_veins.py [--dry-run] [--out PATH];
#             L1 外扫节拍（每轮取未封矿矿脉轮询，§2.5.4——宿主=施工项 7，T3 双前置未解锁）;
#             月度体检生成器（vein_coverage 段读本器产物）;
#             ROOR 登记=REG-AIVEIN-001（挂接操作由主会话统一执行）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 静态清单禁手工维护（宪法 §9.5）：矿脉清单全部由本生成器派生，重跑幂等（输入不变=逐字节不变，
#              产物零墙钟时间戳）; 三输入=config/strategy_production_map.yaml 节点（主）+ AI 层段卡清单
#              （docs/_working/ai_layer_vision/{L*,OBJ_*}/DESIGN.md）+ 功能域注册表（TDM 域辅助轴索引，
#              不派生独立矿脉防 63 域噪音——偏离已留痕报告）; vein_id=VEIN-{node_id} 派生、vein_family=stage
#              （§2.5.1）、关键词种子=decision_question; 墓碑不删除：节点退役→status=archived 保留行，
#              archived 粘滞（再生不自动复活——封矿=结构判据须治理动作才恢复）;
#              产物 CAS 写（safe_write_text），手改必被再生覆盖
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L1_perceive/DESIGN.md §2.5（骨架即地图机制）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 地图/域注册表缺文件或 YAML 畸形→异常上抛退出码 2（fail-closed，绝不派生半张矿脉图）;
#                  段卡目录缺 DESIGN.md→跳过该目录计数留痕（fail-open，段卡非硬依赖）;
#                  --dry-run 零写入; 产物写失败→上抛（不静默）
# [TESTS] tests/ai_layer/perceive/test_veins.py（地图节点全量派生 16 矿脉/vein_family=stage/关键词种子=
#         decision_question/段卡矿脉派生/再生幂等逐字节一致/节点退役→archived 墓碑保留+粘滞/
#         TDM 域辅助轴非矿脉/dry-run 零写）
"""gen_search_veins — "骨架即地图"矿脉清单生成器（施工项 3，DESIGN §2.5.1）。

设计真源：``docs/_working/ai_layer_vision/L1_perceive/DESIGN.md`` §2.5。
原则（定调 4）：矿脉清单=各层骨架本身——本器把骨架三真源机器派生成搜索矿脉清单，
骨架长一节搜索网密一层，骨架变更后再生即增/墓碑/重指向。

用法::

    python scripts/ai_layer/gen_search_veins.py --dry-run    # 只打印派生计数
    python scripts/ai_layer/gen_search_veins.py              # 再生 config/ai_search_veins.yaml（幂等）
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Final

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

log = logging.getLogger("ai_perceive.veins")

DEFAULT_MAP_PATH: Final = REPO_ROOT / "config" / "strategy_production_map.yaml"
DEFAULT_CARDS_ROOT: Final = REPO_ROOT / "docs" / "_working" / "ai_layer_vision"
DEFAULT_DOMAINS_PATH: Final = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "functional_domain_registry.yaml"
)
DEFAULT_OUT_PATH: Final = REPO_ROOT / "config" / "ai_search_veins.yaml"
VEIN_PRIORITY_DEFAULT: Final = 1.0
NOTE_EXCERPT_CHARS: Final = 60
EXIT_OK: Final = 0
EXIT_ERROR: Final = 2


def _one_line(text: Any, limit: int = NOTE_EXCERPT_CHARS) -> str:
    """多行文本 → 单行摘要（换行折叠+截断），供 algo_note 摘要字段。"""
    flat = " ".join(str(text or "").split())
    return flat[:limit]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        missing: FileNotFoundError = FileNotFoundError("骨架输入缺文件")
        missing.details = {"path": str(path)}  # type: ignore[attr-defined]
        raise missing
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        bad_shape: ValueError = ValueError("骨架输入顶层必须是映射")
        bad_shape.details = {"path": str(path)}  # type: ignore[attr-defined]
        raise bad_shape
    return raw


def derive_map_veins(map_raw: dict[str, Any]) -> list[dict[str, Any]]:
    """地图节点全量派生矿脉（vein_id=VEIN-{node_id}、vein_family=stage、种子=decision_question）。"""
    veins: list[dict[str, Any]] = []
    for node in map_raw.get("nodes") or []:
        node_id = str(node.get("node_id") or "")
        if not node_id:
            log.warning("地图节点缺 node_id，跳过: %s", node)
            continue
        veins.append(
            {
                "vein_id": f"VEIN-{node_id}",
                "vein_family": str(node.get("stage") or ""),
                "name_zh": str(node.get("name_zh") or ""),
                "keyword_seed": _one_line(node.get("decision_question"), limit=200),
                "note_excerpt": _one_line(node.get("algo_note_zh")),
                "module_ref": str(node.get("module_ref") or ""),
                "priority": VEIN_PRIORITY_DEFAULT,
                "status": "active",
                "derived_from": f"strategy_production_map#{node_id}",
            }
        )
    veins.sort(key=lambda v: v["vein_id"])
    return veins


def _is_segment_card_dir(path: Path) -> bool:
    """段卡目录判定：L1-L7（L+数字）或 OBJ_*（对象线）；V0/V1/V2 挖矿报告不派生矿脉。"""
    name = path.name
    return path.is_dir() and (name[:1] == "L" and name[1:2].isdigit() or name.startswith("OBJ_"))


def derive_card_veins(cards_root: Path) -> list[dict[str, Any]]:
    """AI 层段卡清单派生矿脉（family=ai_layer；段卡 DESIGN.md 缺失跳过计数留痕）。"""
    veins: list[dict[str, Any]] = []
    if not cards_root.exists():
        log.warning("段卡根目录不存在: %s（跳过段卡矿脉）", cards_root)
        return veins
    for card_dir in sorted(cards_root.iterdir()):
        design = card_dir / "DESIGN.md"
        if not _is_segment_card_dir(card_dir) or not design.exists():
            continue
        try:
            front = _parse_frontmatter(design.read_text(encoding="utf-8"))
        except ValueError as exc:
            log.warning("段卡 frontmatter 解析失败，跳过 %s: %s", design, exc)
            continue
        segment = card_dir.name.split("_")[0]
        veins.append(
            {
                "vein_id": f"VEIN-AI-{segment}",
                "vein_family": "ai_layer",
                "name_zh": str(front.get("title") or card_dir.name),
                "keyword_seed": _one_line(front.get("title"), limit=200),
                "note_excerpt": "",
                "module_ref": "",
                "priority": VEIN_PRIORITY_DEFAULT,
                "status": "active",
                "derived_from": f"ai_layer_segment_card#{card_dir.name}/DESIGN.md",
            }
        )
    veins.sort(key=lambda v: v["vein_id"])
    return veins


def _parse_frontmatter(text: str) -> dict[str, Any]:
    """极简 frontmatter 解析（--- 围栏 YAML）；无围栏=空映射。"""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    raw = yaml.safe_load(parts[1])
    return raw if isinstance(raw, dict) else {}


def derive_domain_axis(domains_raw: dict[str, Any]) -> list[dict[str, str]]:
    """TDM/功能域辅助轴索引（非矿脉——63 域独立矿脉=搜索噪音，偏离已留痕报告）。"""
    axis: dict[str, str] = {}
    for entry in domains_raw.get("entries") or []:
        domain = str(entry.get("domain") or "")
        if domain and domain not in axis:
            axis[domain] = str(entry.get("domain_name_zh") or "")
    return [{"domain": k, "name_zh": v} for k, v in sorted(axis.items())]


def _collect_previous_veins(previous: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    """carry_tombstones 内联逻辑搬移：上一轮矿脉行按 vein_id 索引（非 dict 行忽略）。"""
    return {
        str(v.get("vein_id")): dict(v)
        for v in ((previous or {}).get("veins") or [])
        if isinstance(v, dict)
    }


def _apply_archived_stickiness(
    fresh_veins: list[dict[str, Any]], previous_veins: dict[str, dict[str, Any]]
) -> None:
    """carry_tombstones 内联逻辑搬移：已 archived 粘滞（封矿=结构判据，恢复须治理动作）。"""
    for vein in fresh_veins:
        prior = previous_veins.get(vein["vein_id"])
        if prior is not None and prior.get("status") == "archived":
            vein["status"] = "archived"
            vein["tombstone_reason"] = str(prior.get("tombstone_reason") or "carried_archived")


def _tombstone_row(vein_id: str, prior: dict[str, Any]) -> dict[str, Any]:
    """carry_tombstones 内联逻辑搬移：本轮骨架缺行矿脉的墓碑行构造（键序=产物序列化序）。"""
    return {
        "vein_id": vein_id,
        "vein_family": str(prior.get("vein_family") or ""),
        "name_zh": str(prior.get("name_zh") or ""),
        "keyword_seed": str(prior.get("keyword_seed") or ""),
        "note_excerpt": str(prior.get("note_excerpt") or ""),
        "module_ref": str(prior.get("module_ref") or ""),
        "priority": prior.get("priority", VEIN_PRIORITY_DEFAULT),
        "status": "archived",
        "derived_from": str(prior.get("derived_from") or ""),
        "tombstone_reason": str(prior.get("tombstone_reason") or "absent_from_skeleton"),
    }


def _append_absent_tombstones(
    fresh_veins: list[dict[str, Any]],
    fresh_ids: set[str],
    previous_veins: dict[str, dict[str, Any]],
) -> None:
    """carry_tombstones 内联逻辑搬移：本轮派生缺行的矿脉补 archived 保留行。"""
    for vein_id, prior in previous_veins.items():
        if vein_id in fresh_ids:
            continue
        fresh_veins.append(_tombstone_row(vein_id, prior))


def carry_tombstones(
    fresh_veins: list[dict[str, Any]], previous: dict[str, Any] | None
) -> list[dict[str, Any]]:
    """墓碑语义：本轮派生缺行的矿脉标 archived 保留；已 archived 粘滞（再生不自动复活）。"""
    fresh_ids = {v["vein_id"] for v in fresh_veins}
    previous_veins = _collect_previous_veins(previous)
    _apply_archived_stickiness(fresh_veins, previous_veins)
    _append_absent_tombstones(fresh_veins, fresh_ids, previous_veins)
    fresh_veins.sort(key=lambda v: v["vein_id"])
    return fresh_veins


def build_artifact(
    *,
    map_path: Path = DEFAULT_MAP_PATH,
    cards_root: Path = DEFAULT_CARDS_ROOT,
    domains_path: Path = DEFAULT_DOMAINS_PATH,
    out_path: Path = DEFAULT_OUT_PATH,
) -> dict[str, Any]:
    """三输入 → 产物字典（确定性：零墙钟时间戳，同输入重跑逐字节一致）。"""
    map_raw = _load_yaml(map_path)
    domains_raw = _load_yaml(domains_path)
    previous: dict[str, Any] | None = None
    if out_path.exists():
        try:
            loaded = yaml.safe_load(out_path.read_text(encoding="utf-8"))
            previous = loaded if isinstance(loaded, dict) else None
        except yaml.YAMLError:
            log.warning("既有产物解析失败按无墓碑处理: %s", out_path)
    veins = derive_map_veins(map_raw)
    veins.extend(derive_card_veins(cards_root))
    veins = carry_tombstones(veins, previous)
    archived = sum(1 for v in veins if v["status"] == "archived")
    return {
        "schema_version": "1.0",
        "doc_type": "register",
        "registry_id": "REG-AIVEIN-001",
        "title": "AI 层 L1 搜索矿脉清单（骨架即地图派生，生成器产出禁手改）",
        "status": "active",
        "truth_source": "docs/_working/ai_layer_vision/L1_perceive/DESIGN.md §2.5",
        "derived_from": {
            "map": f"{map_path.relative_to(REPO_ROOT)} (schema {map_raw.get('schema_version')})",
            "segment_cards": str(cards_root.relative_to(REPO_ROOT)) + "/{L*,OBJ_*}/DESIGN.md",
            "domain_axis": str(domains_path.relative_to(REPO_ROOT)),
        },
        "total_veins": len(veins),
        "active_veins": len(veins) - archived,
        "archived_veins": archived,
        "veins": veins,
        "domain_axis": derive_domain_axis(domains_raw),
    }


def write_artifact(artifact: dict[str, Any], out_path: Path) -> str:
    """产物 CAS 落盘（safe_write_text 热文件纪律），返回写入字节数。"""
    from zephyr.shared.io.file_utils import content_sha256, safe_write_text

    content = yaml.safe_dump(artifact, allow_unicode=True, sort_keys=False, default_flow_style=False)
    expected_sha: str | None = None
    if out_path.exists():
        # 与 safe_write_text 同一口径（read_text+content_sha256），防 base 口径不一致误判 stale
        expected_sha = content_sha256(out_path.read_text(encoding="utf-8"))
    result = safe_write_text(out_path, content, expected_base_sha256=expected_sha)
    return str(getattr(result, "bytes_written", len(content)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="骨架即地图：搜索矿脉清单生成器（幂等）")
    parser.add_argument("--map", default=None, help="策略生产全景图路径（默认 config/strategy_production_map.yaml）")
    parser.add_argument("--cards-root", default=None, help="AI 层段卡根目录（默认 docs/_working/ai_layer_vision）")
    parser.add_argument("--domains", default=None, help="功能域注册表路径（TDM 域辅助轴）")
    parser.add_argument("--out", default=None, help="产物路径（默认 config/ai_search_veins.yaml）")
    parser.add_argument("--dry-run", action="store_true", help="只打印派生计数，零写入")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        artifact = build_artifact(
            map_path=Path(args.map) if args.map else DEFAULT_MAP_PATH,
            cards_root=Path(args.cards_root) if args.cards_root else DEFAULT_CARDS_ROOT,
            domains_path=Path(args.domains) if args.domains else DEFAULT_DOMAINS_PATH,
            out_path=Path(args.out) if args.out else DEFAULT_OUT_PATH,
        )
        print(
            f"矿脉派生: total={artifact['total_veins']} active={artifact['active_veins']} "
            f"archived={artifact['archived_veins']} domain_axis={len(artifact['domain_axis'])}"
        )
        if args.dry_run:
            print("dry-run 零写入")
            return EXIT_OK
        written = write_artifact(artifact, Path(args.out) if args.out else DEFAULT_OUT_PATH)
        print(f"产物落盘: {args.out or DEFAULT_OUT_PATH}（{written} 字节）")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001——CLI 边界统一 fail-closed 退出码 2
        print(f"ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班/人工点火, 非自动常驻任务
    raise SystemExit(main())
