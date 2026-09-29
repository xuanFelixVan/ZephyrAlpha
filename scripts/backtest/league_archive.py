# [BLUEPRINT] MOD-AUTO-L11-ARCHIVE | docs/_working/fullflow_mining/03_promotion_ab/02_ab_league.md | 第1节
# [MODULE] scripts.backtest.league_archive
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] yaml; zephyr.data.ch_reader; zephyr.shared.io.file_utils; zephyr.shared.utils.time_utils
# [CONSUMERS] scripts/backtest/league_restore.py（读 manifest 三指纹核对）; Owner 终审门（档案证据）;
#   league_registry.yaml archive_path 回填位
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] manifest 组装=纯函数（build_manifest 直喷可测）;
#   三指纹复原口径：代码 git hash + 因子定义清单 + 数据截止日 trade_date——缺 git hash 硬失败（fail-closed）;
#   CH/fw-auto 不可达→降级记 null+note（不硬造指纹，诚实边界写进 manifest）;
#   数据本体不可复原但 CH 可按截止日重查——此边界如实写 manifest.restore_semantics;
#   档案目录只新增不覆写（已存在→FileExistsError）
# [MODIFY-GUARD] none（只写 data/backtest_artifacts/league/archive/ 新目录）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git 不可用→RuntimeError 上抛; 档案目录已存在→FileExistsError;
#   CH/fw 断供→降级字段 null（不抛）
# [TESTS] tests/backtest/test_league_archive.py
# [A_module] module_id=MOD-AUTO-L11-ARCHIVE | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""league_archive — A/B 联赛参赛档案打包器（TC-11 件1，裁定#392 批）。

每组参赛时打包 manifest.yaml → data/backtest_artifacts/league/archive/<GROUP>-<YYYYMMDD>/：
git commit hash + 因子清单 + 数据截止日指纹（trade_date）+ 配置快照
+ 整装回测产物指针（data/backtest_artifacts/fw-auto/latest.json）+ 模块依赖链接。

复原口径=三指纹（代码 git hash+因子定义+数据截止日）；数据本体不可复原，
CH 可按截止日 trade_date 重查——边界如实写进 manifest（restore_semantics 字段）。

用法（仓库根，Python 3.12）：
    python scripts/backtest/league_archive.py --group A            # 打包 A 组参赛档案
    python scripts/backtest/league_archive.py --group A --dry-run  # 只打印 manifest 不落盘
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

# noqa: m11-perm-manual-legitimate  M11豁免: 参赛档案按需打包的 CLI 工具（每组参赛一次手动触发），非自动触发常驻

FW_LATEST = REPO_ROOT / "data" / "backtest_artifacts" / "fw-auto" / "latest.json"
ARCHIVE_ROOT = REPO_ROOT / "data" / "backtest_artifacts" / "league" / "archive"
REGISTRY_PATH = REPO_ROOT / "config" / "league_registry.yaml"

# 三指纹边界声明（manifest 必载，复原器 league_restore 按此核对）
RESTORE_SEMANTICS = (
    "复原口径=三指纹：代码 git hash + 因子定义清单 + 数据截止日 trade_date。"
    "数据本体不可复原，但 ClickHouse 可按数据截止日 trade_date 重查；"
    "三指纹齐备即可在指纹对齐后百分百重建参赛时点的考题环境（数据以截止日快照为准）。"
)

MODULE_DEPS = [
    {"module_id": "MOD-AUTO-L11-REGISTRY", "path": "scripts/backtest/league_registry.py"},
    {"module_id": "MOD-AUTO-L11-ARCHIVE", "path": "scripts/backtest/league_archive.py"},
    {"module_id": "MOD-AUTO-L11-RESTORE", "path": "scripts/backtest/league_restore.py"},
    {"module_id": "MOD-AUTO-L11-SNAPSHOT", "path": "scripts/backtest/league_monthly_snapshot.py"},
    {
        "module_id": "MOD-AUTO-L2-001",
        "path": "scripts/backtest/promotion_combo_gate.py",
        "role": "judge（复用本体零修改）",
    },
    {
        "module_id": "fw_backtest（整装战役）",
        "path": "data/backtest_artifacts/fw-auto/latest.json",
        "role": "整装产物指针",
    },
]


def current_git_hash(repo_root: Path = REPO_ROOT) -> str:
    """当前 HEAD commit hash（fail-closed：git 不可用→RuntimeError，无 hash 不打包）。"""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
    except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"git rev-parse HEAD 失败，无指纹不打包: {exc}") from exc
    return out.stdout.strip()


def parse_scalar_tsv(tsv: str) -> str | None:
    """ch_reader 单值查询 TSV → 首个含数字的数据值；空/纯表头 → None（纯函数）。

    ch_reader.query 实测返回无表头 TSV（如 '2026-09-21\\n'）；兼容带表头形态：
    跳过不含数字的行（如 'max(trade_date)'）。
    """
    for ln in (tsv or "").strip().splitlines():
        cell = ln.split("\t")[0].strip()
        if cell and any(c.isdigit() for c in cell):
            return cell
    return None


def query_data_cutoff() -> dict:
    """数据截止日指纹：sim_pocket_daily max(trade_date)。CH 不可达→{"trade_date": None}+note。"""
    try:
        from zephyr.data.ch_reader import query  # noqa: PLC0415

        tsv = query("SELECT max(trade_date) FROM c1_backtest.sim_pocket_daily")  # noqa: ch-final  月度留档快照只留档不判定，max 聚合与 ReplacingMergeTree 未合并行无歧义
        td = parse_scalar_tsv(tsv)
    except Exception as exc:  # noqa: BLE001 — CH 断连/模块缺失统一降级（诚实边界不硬造）
        return {"trade_date": None, "note": f"CH 不可达，截止日指纹缺失: {exc}"}
    if td is None:
        return {"trade_date": None, "note": "sim_pocket_daily 无行，截止日指纹缺失"}
    return {"trade_date": td, "note": ""}


def load_fw_pointer(path: Path | str = FW_LATEST) -> dict:
    """整装回测产物指针（只存定位+指纹字段，不整拷大文件）。缺失→exists=False 降级。"""
    p = Path(path)
    pointer: dict = {
        "path": str(Path(path).relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p),
        "exists": p.exists(),
    }
    if not p.exists():
        pointer["note"] = "fw-auto latest.json 缺失（整装产物未产出或被清理）"
        return pointer
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        pointer["note"] = f"latest.json 不可解析: {exc}"
        return pointer
    plan = data.get("plan") or {}
    window = data.get("window") or {}
    pointer.update(
        {
            "plan_id": plan.get("plan_id"),
            "fingerprint": plan.get("fingerprint"),
            "window": {"start": window.get("start"), "end": window.get("end")},
            "trigger": data.get("trigger"),
        }
    )
    return pointer


def factor_list_from_fw(fw_pointer: dict, override: list[str] | None = None) -> list[str]:
    """因子清单：显式 override 优先；否则取 fw-auto plan.weights 键（成员策略/因子口径）。"""
    if override:
        return list(override)
    return []


def factor_list_from_fw_plan(fw_data: dict) -> list[str]:
    """fw-auto 完整 dict → 成员清单（plan.weights 键，纯函数供测试）。"""
    plan = fw_data.get("plan") or {}
    weights = plan.get("weights") or {}
    return sorted(str(k) for k in weights)


def build_manifest(
    group: dict,
    git_hash: str,
    factors: list[str],
    data_cutoff: dict,
    fw_pointer: dict,
    config_snapshot: dict,
    *,
    created_at: str | None = None,
    module_deps: list[dict] | None = None,
) -> dict:
    """manifest 组装（纯函数，测试直喷）。字段缺指纹如实记 null，不硬造。"""
    return {
        "manifest_version": "0.1.0",
        "doc_type": "league_archive_manifest",
        "group_id": group.get("group_id"),
        "status_at_archive": group.get("status"),
        "created_at": created_at or now_utc().strftime("%Y%m%dT%H%M%S%z"),
        "fingerprint_code_git_hash": git_hash,
        "fingerprint_factors": list(factors),
        "fingerprint_data_cutoff": data_cutoff,
        "config_snapshot": config_snapshot,
        "fw_artifact_pointer": fw_pointer,
        "module_deps": list(module_deps or MODULE_DEPS),
        "restore_semantics": RESTORE_SEMANTICS,
    }


def archive_dir_name(group_id: str, date_str: str) -> str:
    """档案目录名 <GROUP>-<YYYYMMDD>（纯函数）。"""
    return f"{group_id}-{date_str}"


def config_snapshot(registry_path: Path | str = REGISTRY_PATH, group_id: str = "") -> dict:
    """配置快照：参赛组条目+判定政策（注册表相关切片，非整文件拷贝）。"""
    from league_registry import get_group, load_registry  # noqa: PLC0415  同目录先例风格

    data = load_registry(registry_path)
    snap: dict = {"review_policy": data.get("review_policy") or {}, "registry_source": str(registry_path)}
    try:
        snap["group_entry"] = get_group(data, group_id)
    except KeyError:
        snap["group_entry"] = None
    return snap


def write_archive(manifest: dict, archive_root: Path | str = ARCHIVE_ROOT) -> Path:
    """manifest.yaml 落盘到 archive/<GROUP>-<date>/；目录已存在→FileExistsError（只新增不覆写）。"""
    created = str(manifest.get("created_at") or now_utc().strftime("%Y%m%dT%H%M%S%z"))
    date_part = created[:8].replace("-", "") or now_utc().strftime("%Y%m%d")
    out_dir = Path(archive_root) / archive_dir_name(str(manifest.get("group_id")), date_part)
    if out_dir.exists():
        raise FileExistsError(f"参赛档案目录已存在（只新增不覆写）: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=False)
    out = out_dir / "manifest.yaml"
    out.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return out


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="A/B 联赛参赛档案打包器（manifest.yaml → archive/<GROUP>-<date>/）")
    ap.add_argument("--group", type=str, required=True, help="参赛组 ID（league_registry.yaml 已登记）")
    ap.add_argument("--factors", type=str, default=None, help="逗号分隔因子清单（缺省取 fw-auto plan 成员）")
    ap.add_argument("--registry", type=str, default=None)
    ap.add_argument("--archive-root", type=str, default=None)
    ap.add_argument("--dry-run", action="store_true", help="只打印 manifest 不落盘")
    args = ap.parse_args()

    from league_registry import get_group, load_registry  # noqa: PLC0415

    reg_path = Path(args.registry) if args.registry else REGISTRY_PATH
    group = get_group(load_registry(reg_path), args.group)

    fw_pointer = load_fw_pointer()
    factors = args.factors.split(",") if args.factors else []
    if not factors:
        fw_path = REPO_ROOT / str(fw_pointer.get("path") or "")
        if fw_pointer.get("exists") and fw_path.exists():
            try:
                factors = factor_list_from_fw_plan(json.loads(fw_path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                factors = []

    manifest = build_manifest(
        group=group,
        git_hash=current_git_hash(),
        factors=factors,
        data_cutoff=query_data_cutoff(),
        fw_pointer=fw_pointer,
        config_snapshot=config_snapshot(reg_path, args.group),
    )
    text = yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False)
    if args.dry_run:
        print(text)
        return 0
    out = write_archive(manifest, Path(args.archive_root) if args.archive_root else ARCHIVE_ROOT)
    print(
        json.dumps(
            {
                "ok": True,
                "manifest": str(out),
                "group": args.group,
                "git_hash": manifest["fingerprint_code_git_hash"][:12],
                "factors_n": len(factors),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
