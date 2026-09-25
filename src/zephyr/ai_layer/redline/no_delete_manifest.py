# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_no_delete_manifest
# [MODULE] zephyr.ai_layer.redline.no_delete_manifest
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT/DB_PATH，SSOT 引用不复制);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.redline.annual_review (S8 年审固定核对项④：生成器 freshness);
#             scripts/ 侧年审点火（CLI python -m zephyr.ai_layer.redline.no_delete_manifest generate）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 禁删清单一律生成器产出（AGENTS.md §9 运维红线第 5 条：静态清单禁手工维护，
#              手工必漂移）；枚举真源零复制：产库表=DDL 真源 schemas/categories/**/*.py 的
#              TABLE_NAME（AST 解析，禁正则猜）；注册表=ROOR（docs/registry_of_registries.yaml）
#              tier 0-2 全部 physical_path（DESIGN §2 档 A 原文）+ROOR 本体+档 A 必须覆盖点名件
#              （secret_registry/immutable_core/audit_key_eras/ruling_registry/gate_registry/
#              risk_tier_registry——ROOR 未列者以 coverage_required 来源入册，逐条带 provenance）；
#              覆盖缺口=诚实报告（coverage.missing 非空即年审立案素材，不静默补齐）；
#              条目排序确定性（同输入再生逐条一致=幂等再生）；计数用字段（total_entries）不写死散文
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §2 档 A/§4-S4
# [STABILITY] new
# [SAFETY] L（纯只读枚举+生成物落参数指定目录；不连库、不改真源）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 根/ROOR 缺文件 → ManifestInputError（fail-closed 输入）；
#                  单个 DDL 文件语法坏 → 跳过+bad_files 计数留痕（fail-open 读）；
#                  ROOR tiers 形状非法 → ManifestInputError；输出目录不存在自动创建
# [TESTS] tests/ai_layer/redline/test_no_delete_manifest.py（DDL AST 枚举含 sim 双表/
#         坏文件跳过留痕/ROOR tier 0-2 全收+tier3 排除/必须覆盖点名件齐/coverage missing 报告/
#         幂等再生逐条一致/写盘回读）
# [TTL] permanent
"""no_delete_manifest — 禁删清单生成器×2（OBJ_S 施工项 S4，DESIGN §2 档 A）。

机械判定总纲：删没删看"真源是否失 dereference"；禁删对象清单一律生成器产出。
两台生成器：

1. 产库禁删表清单：枚举真源=schemas/categories/**/*.py 的 ``TABLE_NAME``（DDL 真源，
   AST 解析 Assignment）；必须覆盖点名件=c1_backtest.sim_trade_log（事件溯源源，
   删=账本永不可重建）+c1_backtest.sim_pocket_daily（日账本体）。
2. 注册表禁删清单：枚举真源=ROOR tier 0-2 全部 physical_path + ROOR 本体 +
   档 A 必须覆盖点名件（gate_registry/risk_tier_registry/secret_registry/
   immutable_core/audit_key_eras/ruling_registry/audit_key_eras 本体/governance.db）。

输出 freshness（generated_at+条目清单）供 S8 年审固定核对项④（生成器 freshness）消费。
"""

from __future__ import annotations

import argparse
import ast
import json
import logging
import sys
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import DB_PATH, REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

SCHEMA_VERSION: Final = "1.0.0"
GENERATED_BY: Final = "zephyr.ai_layer.redline.no_delete_manifest"
DEFAULT_DDL_ROOT: Final = REPO_ROOT / "schemas" / "categories"
DEFAULT_ROOR_PATH: Final = REPO_ROOT / "docs" / "registry_of_registries.yaml"
DEFAULT_OUT_DIR: Final = REPO_ROOT / "docs" / "_working" / "ai_layer_vision" / "OBJ_S_perimeter" / "generated"
ROOR_MAX_TIER: Final = 2

REQUIRED_TABLES: Final[tuple[str, ...]] = (
    "c1_backtest.sim_trade_log",
    "c1_backtest.sim_pocket_daily",
)
REQUIRED_REGISTRY_FILES: Final[tuple[str, ...]] = (
    "registry_of_registries.yaml",
    "gate_registry.yaml",
    "risk_tier_registry.yaml",
    "secret_registry.yaml",
    "immutable_core.yaml",
    "audit_key_eras.yaml",
    "ruling_registry.yaml",
)
# 必须覆盖点名件的仓内 canonical 路径（2026-09-23 盘点核实存在；ROOR 已列者不重复入册）
# SSOT 链（VOCAB-CHAIN 合规）：catalogs 目录路径不经硬编码，运行时经 ROOR（registry_of_registries）
# 的 physical_path 反查解析；ROOR 自身路径为 docs/ 根（不在 SSoT 目录模式内）。
ROOR_PATH: Final[str] = "docs/registry_of_registries.yaml"
_COVERAGE_IN_ROOR: Final[tuple[str, ...]] = (
    "gate_registry.yaml",
    "risk_tier_registry.yaml",
    "ruling_registry.yaml",
)
_COVERAGE_FIXED: Final[dict[str, str]] = {
    "registry_of_registries.yaml": "docs/registry_of_registries.yaml",
    "secret_registry.yaml": "config/secret_registry.yaml",
    "immutable_core.yaml": "config/immutable_core.yaml",
    "audit_key_eras.yaml": "config/audit_key_eras.yaml",
}


def _resolve_roor_catalog_paths() -> dict[str, str]:
    """经 ROOR physical_path 反查 catalogs 目录注册表路径（查无=返回部分结果，由覆盖核对报缺）。"""
    resolved: dict[str, str] = {}
    try:
        import yaml
        from zephyr.shared.io.paths import REPO_ROOT
        doc = yaml.safe_load((REPO_ROOT / ROOR_PATH).read_text(encoding="utf-8"))

        def _walk(node: Any) -> None:
            if isinstance(node, dict):
                pp = node.get("physical_path")
                if isinstance(pp, str):
                    resolved[Path(pp).name] = pp
                for v in node.values():
                    _walk(v)
            elif isinstance(node, list):
                for v in node:
                    _walk(v)

        _walk(doc)
    except Exception:  # noqa: BLE001 — fail-open：解析失败由覆盖核对以"缺件"如实上报
        pass
    return {name: resolved[name] for name in _COVERAGE_IN_ROOR if name in resolved}


def _coverage_required_paths() -> dict[str, str]:
    """合并固定路径与 ROOR 反查路径（ROOR 查无的条目缺席=覆盖核对 FAIL，如实暴露）。"""
    return {**_COVERAGE_FIXED, **_resolve_roor_catalog_paths()}

REQUIRED_PROTECTED_FILES: Final[tuple[str, ...]] = (
    "config/audit_key_eras.yaml",
    "data/databases/governance.db",
)

TABLES_MANIFEST_NAME: Final = "no_delete_tables.yaml"
REGISTRIES_MANIFEST_NAME: Final = "no_delete_registries.yaml"


class ManifestInputError(RuntimeError):
    """生成器输入错误（DDL 根/ROOR 缺文件或形状非法，fail-closed）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


# ────────────────── 生成器 1：产库禁删表清单（DDL 真源）──────────────────


def iter_ddl_table_names(ddl_root: Path) -> tuple[list[dict[str, str]], list[str]]:
    """AST 枚举 DDL 根下全部 ``TABLE_NAME = "<db.table>"`` → (条目, 坏文件清单)。

    条目形如 {"kind": "ch_table", "name": ..., "source": 相对路径}，按 name 排序。
    语法坏文件跳过计数留痕（fail-open 读）。
    """
    entries: list[dict[str, str]] = []
    bad_files: list[str] = []
    for py_file in sorted(ddl_root.rglob("*.py")):
        if py_file.name.startswith("_") or py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, ValueError, OSError):
            bad_files.append(py_file.name)
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "TABLE_NAME" not in targets or not isinstance(node.value, ast.Constant):
                continue
            value = node.value.value
            if isinstance(value, str) and value:
                entries.append(
                    {"kind": "ch_table", "name": value, "source": py_file.as_posix()}
                )
    entries.sort(key=lambda item: item["name"])
    return entries, bad_files


def generate_tables_manifest(ddl_root: Path) -> dict[str, Any]:
    """生成产库禁删表清单（档 A 生产库类；覆盖缺口诚实报告）。"""
    if not ddl_root.exists():
        raise ManifestInputError(f"DDL 真源目录不存在（fail-closed）: {ddl_root}")
    entries, bad_files = iter_ddl_table_names(ddl_root)
    names = {entry["name"] for entry in entries}
    missing = [name for name in REQUIRED_TABLES if name not in names]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "generated_at": now_utc().isoformat(),
        "manifest": "no_delete_tables",
        "deletion_tier": "A_physical_delete_owner_gate",
        "ddl_root": ddl_root.as_posix(),
        "entries": entries,
        "bad_files_skipped": bad_files,
        "coverage": {"required": list(REQUIRED_TABLES), "missing": missing},
        "total_entries": len(entries),
    }


# ────────────────── 生成器 2：注册表禁删清单（ROOR）──────────────────


def _rel_to_repo(path: Path) -> str:
    """路径 → 仓根相对（不在仓内则原样 posix；测试 tmp 场景诚实保留绝对路径）。"""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def roor_registry_paths(roor_path: Path) -> tuple[list[dict[str, str]], int]:
    """ROOR tier 0-2 全部 physical_path → (条目, 注册表计数)（tiers 形状非法抛错）。"""
    try:
        data = yaml.safe_load(roor_path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, yaml.YAMLError) as exc:
        raise ManifestInputError("ROOR 读取/解析失败（fail-closed）", details={"path": str(roor_path)}) from exc
    tiers = data.get("tiers") if isinstance(data, dict) else None
    if not isinstance(tiers, list):
        raise ManifestInputError("ROOR tiers 形状非法（fail-closed）", details={"path": str(roor_path)})
    entries: list[dict[str, str]] = []
    registry_count = 0
    for tier_block in tiers:
        if not isinstance(tier_block, dict):
            continue
        tier_no = tier_block.get("tier")
        if not isinstance(tier_no, int) or tier_no > ROOR_MAX_TIER:
            continue
        for registry in tier_block.get("registries") or []:
            if not isinstance(registry, dict):
                continue
            path = registry.get("physical_path")
            registry_count += 1
            if not isinstance(path, str) or not path:
                continue
            kind = "db_dsn" if "://" in path else "registry_file"
            entries.append(
                {
                    "kind": kind,
                    "name": path,
                    "source": f"ROOR tier{tier_no}:{registry.get('registry_id', '?')}",
                }
            )
    entries.append(
        {
            "kind": "roor_self",
            "name": _rel_to_repo(roor_path),
            "source": "ROOR 本体（自身 dereference 根）",
        }
    )
    entries.sort(key=lambda item: (item["kind"], item["name"]))
    return entries, registry_count


def generate_registries_manifest(roor_path: Path) -> dict[str, Any]:
    """生成注册表禁删清单（档 A 注册表类；必须覆盖点名件齐套核对）。"""
    if not roor_path.exists():
        raise ManifestInputError("ROOR 不存在（fail-closed）", details={"path": str(roor_path)})
    roor_entries, registry_count = roor_registry_paths(roor_path)
    roor_names = {entry["name"] for entry in roor_entries}
    roor_basenames = {Path(name).name for name in roor_names}
    coverage_entries: list[dict[str, str]] = []
    for required in REQUIRED_REGISTRY_FILES:
        if required in roor_names or required in roor_basenames:
            continue  # ROOR 已列（全名或 basename 命中），不重复入册
        coverage_entries.append(
            {
                "kind": "coverage_required",
                "name": _coverage_required_paths().get(required, required),
                "source": "DESIGN §2 档 A 必须覆盖点名件（ROOR 未列，补册留痕）",
            }
        )
    for required_file in REQUIRED_PROTECTED_FILES:
        coverage_entries.append(
            {
                "kind": "coverage_required",
                "name": required_file,
                "source": "DESIGN §2 档 A 审计件/生产库文件级点名",
            }
        )
    all_entries = roor_entries + sorted(coverage_entries, key=lambda item: item["name"])
    basenames = {Path(entry["name"]).name for entry in all_entries}
    missing = [name for name in REQUIRED_REGISTRY_FILES if name not in basenames]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "generated_at": now_utc().isoformat(),
        "manifest": "no_delete_registries",
        "deletion_tier": "A_physical_delete_owner_gate",
        "roor_path": roor_path.as_posix(),
        "roor_registries_scanned": registry_count,
        "entries": all_entries,
        "coverage": {"required": list(REQUIRED_REGISTRY_FILES), "missing": missing},
        "total_entries": len(all_entries),
    }


# ────────────────── 落盘与 CLI ──────────────────


def write_manifest(manifest: dict[str, Any], out_path: Path) -> Path:
    """清单落盘（yaml.safe_dump sort_keys=False + allow_unicode；目录不存在创建）。"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return out_path


def generate_all(ddl_root: Path, roor_path: Path, out_dir: Path) -> dict[str, Any]:
    """两台生成器编排（只读真源+生成物落 out_dir）。"""
    tables = generate_tables_manifest(ddl_root)
    registries = generate_registries_manifest(roor_path)
    tables_path = write_manifest(tables, out_dir / TABLES_MANIFEST_NAME)
    registries_path = write_manifest(registries, out_dir / REGISTRIES_MANIFEST_NAME)
    return {
        "generated_at": tables["generated_at"],
        "tables_manifest": str(tables_path),
        "tables_total": tables["total_entries"],
        "tables_coverage_missing": tables["coverage"]["missing"],
        "registries_manifest": str(registries_path),
        "registries_total": registries["total_entries"],
        "registries_coverage_missing": registries["coverage"]["missing"],
    }


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.ai_layer.redline.no_delete_manifest",
        description="禁删清单生成器×2（OBJ_S S4）：DDL 真源产库表清单 + ROOR 注册表清单",
    )
    parser.add_argument("--ddl-root", default=str(DEFAULT_DDL_ROOT), help="DDL 真源目录")
    parser.add_argument("--roor", default=str(DEFAULT_ROOR_PATH), help="ROOR 路径")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="生成物输出目录")
    args = parser.parse_args(argv)
    try:
        summary = generate_all(Path(args.ddl_root), Path(args.roor), Path(args.out))
    except ManifestInputError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班/人工点火, 非自动常驻任务
    sys.exit(main())
