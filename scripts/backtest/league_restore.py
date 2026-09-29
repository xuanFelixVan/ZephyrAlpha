# [BLUEPRINT] MOD-AUTO-L11-RESTORE | docs/_working/fullflow_mining/03_promotion_ab/02_ab_league.md | 第1节
# [MODULE] scripts.backtest.league_restore
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] yaml; scripts.backtest.league_archive（指纹采集复用）; zephyr.shared.utils.time_utils
# [CONSUMERS] Owner/终审复核（参赛环境百分百复原口径的核对报告）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只核对不执行——本工具输出可复原性判定+核对报告，禁自动 git checkout（切换动作须人执行）;
#   判定三态 faithfulness 口径：faithful=三指纹全同｜restorable=有漂移但三指纹齐备（可对齐复原）｜
#   unverifiable=任一指纹证据缺失（不硬判）;
#   compare/verdict 纯函数（测试直喷），IO 采集全部降级不抛
# [MODIFY-GUARD] none（只读 manifest + 只读采集当前指纹）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] manifest 缺失→FileNotFoundError 上抛; 指纹采集断供→unknown 降级（不抛）
# [TESTS] tests/backtest/test_league_restore.py
# [A_module] module_id=MOD-AUTO-L11-RESTORE | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""league_restore — A/B 联赛参赛档案复原判定器（TC-11 件1，裁定#392 批）。

读参赛档案 manifest.yaml → 核对当前 git/因子/数据截止日与三指纹（代码 git hash+因子定义+数据
截止日 trade_date）的差异 → 输出可复原性判定+核对报告。不自动执行 git checkout——切换动作
（checkout 指纹 commit + 按截止日重查 CH 数据）须人按报告执行。

用法（仓库根，Python 3.12）：
    python scripts/backtest/league_restore.py --archive data/backtest_artifacts/league/archive/A-20260921
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc_str  # noqa: E402

# noqa: m11-perm-manual-legitimate  M11豁免: 复原核对按需手动的报告工具（终审/审计时点触发），非自动触发常驻

STATE_MATCH = "match"
STATE_DRIFT = "drift"
STATE_UNKNOWN = "unknown"

VERDICT_FAITHFUL = "faithful"
VERDICT_RESTORABLE = "restorable"
VERDICT_UNVERIFIABLE = "unverifiable"


def load_manifest(archive: Path | str) -> dict:
    """读参赛档案 manifest.yaml；入参可为档案目录或 manifest 文件路径。缺失→FileNotFoundError。"""
    p = Path(archive)
    if p.is_dir():
        p = p / "manifest.yaml"
    if not p.exists():
        raise FileNotFoundError(f"参赛档案 manifest 不存在: {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def compare_fingerprint(archived, current) -> str:
    """单指纹三态比对（纯函数）：双值相等=match｜有值不等=drift｜任一缺失=unknown。"""
    if archived is None or current is None or archived == "" or current == "":
        return STATE_UNKNOWN
    if isinstance(archived, list) or isinstance(current, list):
        return STATE_MATCH if list(archived or []) == list(current or []) else STATE_DRIFT
    return STATE_MATCH if archived == current else STATE_DRIFT


def compare_manifest(manifest: dict, current: dict) -> list[dict]:
    """三指纹核对（纯函数，测试直喷）。current 口径：git_hash/factors/data_cutoff（缺失传 None）。"""
    rows = [
        {
            "name": "code_git_hash",
            "archived": manifest.get("fingerprint_code_git_hash"),
            "current": current.get("git_hash"),
            "hint": "差异=checkout 至档案 hash 可对齐（本工具不自动执行）",
        },
        {
            "name": "factor_definitions",
            "archived": manifest.get("fingerprint_factors"),
            "current": current.get("factors"),
            "hint": "差异=因子定义漂移，按档案清单复原因子版本后重跑",
        },
        {
            "name": "data_cutoff_trade_date",
            "archived": (manifest.get("fingerprint_data_cutoff") or {}).get("trade_date"),
            "current": current.get("data_cutoff"),
            "hint": "差异=按档案截止日 trade_date 在 CH 重查（数据本体不可复原，重查口径见 manifest.restore_semantics）",
        },
    ]
    for r in rows:
        r["state"] = compare_fingerprint(r["archived"], r["current"])
    return rows


def restore_verdict(rows: list[dict]) -> str:
    """三态判定（纯函数）：全 match=faithful｜有 drift 但零 unknown=restorable｜含 unknown=unverifiable。"""
    states = {r["state"] for r in rows}
    if STATE_UNKNOWN in states:
        return VERDICT_UNVERIFIABLE
    if STATE_DRIFT in states:
        return VERDICT_RESTORABLE
    return VERDICT_FAITHFUL


def render_report(manifest: dict, rows: list[dict], verdict: str) -> str:
    """核对报告渲染（纯函数）。三态建议文案与 RESTORE_SEMANTICS 边界一致。"""
    lines = [
        "# 参赛档案复原核对报告",
        "",
        f"- 核对时间: {now_utc_str()}（机生禁手改）",
        f"- 档案组: {manifest.get('group_id')}（archive 时状态={manifest.get('status_at_archive')}，"
        f"archive 时点={manifest.get('created_at')}）",
        f"- 判定: **{verdict}**",
        "",
        "| 指纹 | 档案值 | 当前值 | 状态 | 处置提示 |",
        "|------|--------|--------|------|----------|",
    ]
    for r in rows:
        lines.append(f"| {r['name']} | {r['archived']} | {r['current']} | {r['state']} | {r['hint']} |")
    lines.append("")
    rec = {
        VERDICT_FAITHFUL: "当前环境即参赛环境，无需切换，可直接重放终审考题。",
        VERDICT_RESTORABLE: "三指纹齐备存在漂移：按上表对齐（checkout 档案 hash+复原因子版本+按截止日重查数据）后可百分百重建；切换动作须人执行，本工具不自动 checkout。",
        VERDICT_UNVERIFIABLE: "存在缺失指纹，无法判定可复原性——先补齐档案或当前侧指纹再核对（不硬判）。",
    }[verdict]
    lines.append(f"- 结论: {rec}")
    lines.append(f"- 边界: {manifest.get('restore_semantics') or '（manifest 未载边界声明）'}")
    lines.append("")
    return "\n".join(lines)


def _collect_current() -> dict:
    """当前三指纹采集（IO 层，全部降级不抛）。"""
    from league_archive import (  # noqa: PLC0415  同目录复用采集件
        current_git_hash,
        factor_list_from_fw_plan,
        load_fw_pointer,
        query_data_cutoff,
    )

    cur: dict = {"git_hash": None, "factors": None, "data_cutoff": None}
    try:
        cur["git_hash"] = current_git_hash()
    except RuntimeError:
        pass
    fw = load_fw_pointer()
    if fw.get("exists"):
        fw_path = REPO_ROOT / str(fw.get("path") or "")  # 档案指针为仓内相对路径（绝对路径拼接时 pathlib 自愈）
        try:
            cur["factors"] = factor_list_from_fw_plan(json.loads(fw_path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    cur["data_cutoff"] = query_data_cutoff().get("trade_date")
    return cur


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="A/B 联赛参赛档案复原判定器（只核对报告，不自动 checkout）")
    ap.add_argument("--archive", type=str, required=True, help="参赛档案目录（或 manifest.yaml 路径）")
    args = ap.parse_args()

    manifest = load_manifest(args.archive)
    rows = compare_manifest(manifest, _collect_current())
    verdict = restore_verdict(rows)
    print(render_report(manifest, rows, verdict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
