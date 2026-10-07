# [BLUEPRINT] MOD-INF-043 | scripts/backup/retention_derived.py | §
# [MODULE] scripts.backup.retention_derived
# [DOMAIN] D_GOVERNANCE
# create-guard-not-dup: 与 n16_exemption_lookup 等命中能力跨域不同对象——本器=备份链 P95 时限派生（读 backup_config 实测值）+reaper 免死影子账（只读抄录 keep.txt），非任何豁免查找/决策通道；token backup_retention_derived 已登记
# [DEPENDENCIES] stdlib（argparse/json/re/datetime/hashlib/pathlib）；yaml；zephyr.shared.io.file_utils（safe_write_text——影子账 CAS 写）
# [CONSUMERS] manual CLI（总包夜战 C440）；.runtime/audit/keep_shadow_*.json（3 天影子快照，判读面=维护班/Owner 晨会）；tests/backup/test_retention_derived.py（纯函数单测）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 免死影子账骨架：只读 process_reaper_keep.txt 本体（禁改/禁写/禁挪——保命面真源不可触碰）；
#  影子快照只落 .runtime/audit/keep_shadow_*.json（自家产物，expires_at=+3 天；清理仅限本前缀过期件，
#  抄录要点=快照本体重全量条目，零信息丢失）；时限派生=纯函数（config dict 进、读数 dict 出，无 IO 无时钟——
#  可测试性铁律），IO 与 now_utc 只在 CLI 壳层；派生判据全部溯源 config 实测值（retention_days/min_keep_days/
#  min_interval_seconds/mirror_guard 帽），不发明系数；config 缺键=记 violations 不猜默认。
# [MODIFY-GUARD] CLI: [derive-limits --config PATH] / [keep-shadow --keep PATH --out-dir PATH --no-prune]；零参数缺省=derive-limits
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] config/keep 缺失=exit 2 报路径；纯函数对缺键返回 violations 不抛；影子账写必经
#  safe_write_text（.runtime/audit 非热册，CAS 只防并发覆写）；prune 仅 glob keep_shadow_*.json 且
#  mtime>3 天，其余文件零触碰
# [TESTS] tests/backup/test_retention_derived.py（纯函数 derive/validate 影子账解析单测）
# [A_module] module_id=MOD-INF-043 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""retention_derived — 备份链 P95 时限派生器 + reaper 免死影子账生成器（C440）。

两件事一个壳（同为"备份链/保命链时限尺"域，合并评估=同域收敛唯一，不立第二脚本）：

1. ``derive-limits``：从 ``scripts/backup/backup_config.yaml`` 实测值纯函数派生监测时限读数
   （retention P95 天/下限天/触发间隔 P95 小时/镜像删除帽可信上界核验），零写盘。
2. ``keep-shadow``：读 ``data/runtime/process_reaper_keep.txt`` 生成 3 天影子快照 JSON 到
   ``.runtime/audit/``——keep.txt 本体零触碰（保命面真源），影子账供"免死清单被谁改了"
   的对账基线（watchdog 误杀取证输入）。

Usage::

    python scripts/backup/retention_derived.py derive-limits
    python scripts/backup/retention_derived.py keep-shadow
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.shared.io.file_utils import safe_write_text  # noqa: E402

DEFAULT_CONFIG = _REPO_ROOT / "scripts/backup/backup_config.yaml"
DEFAULT_KEEP = _REPO_ROOT / "data/runtime/process_reaper_keep.txt"
DEFAULT_OUT_DIR = _REPO_ROOT / ".runtime/audit"
SHADOW_GLOB = "keep_shadow_*.json"
SHADOW_TTL_DAYS = 3
# mirror_guard 帽可信上界（backup_config.yaml 注记：写 999999 这类值=帽不可用）
MIRROR_CAP_TRUSTED_BOUND = 5000


def derive_retention_p95(config: dict) -> dict:
    """纯函数：config 实测值 → P95 时限读数（无 IO 无时钟，可单测）。

    判据溯源（不发明系数）：retention_days 是"实际保留随空间自适应收缩"的**上限**，
    驱逐只在空间压力下发生，故保留时长的 P95≈上限本身；下限=min_keep_days。
    """
    wv = config.get("working_vault") or {}
    dd = config.get("db_dumps") or {}
    trig = config.get("trigger") or {}
    mg = config.get("mirror_guard") or {}
    wv_retention = wv.get("retention_days")
    wv_floor = wv.get("min_keep_days")
    dd_retention = dd.get("retention_days")
    interval = trig.get("min_interval_seconds")
    cap = mg.get("max_propagated_deletes")
    return {
        "working_vault_retention_p95_days": wv_retention,
        "working_vault_retention_floor_days": wv_floor,
        "db_dumps_retention_p95_days": dd_retention,
        "trigger_interval_p95_hours": (round(interval / 3600, 2) if isinstance(interval, (int, float)) else None),
        "mirror_delete_cap": cap,
        "mirror_cap_trusted": bool(isinstance(cap, int) and 0 < cap <= MIRROR_CAP_TRUSTED_BOUND),
    }


def validate_config(config: dict) -> list[str]:
    """纯函数：config 一致性校验，返回 violations 列表（空=过）。"""
    v: list[str] = []
    wv = config.get("working_vault") or {}
    trig = config.get("trigger") or {}
    ret, floor = wv.get("retention_days"), wv.get("min_keep_days")
    if not isinstance(ret, int) or ret <= 0:
        v.append(f"working_vault.retention_days 非法: {ret!r}")
    if not isinstance(floor, int) or floor <= 0:
        v.append(f"working_vault.min_keep_days 非法: {floor!r}")
    if isinstance(ret, int) and isinstance(floor, int) and floor >= ret:
        v.append(f"min_keep_days({floor}) 必须 < retention_days({ret})")
    interval = trig.get("min_interval_seconds")
    if not isinstance(interval, (int, float)) or interval <= 0:
        v.append(f"trigger.min_interval_seconds 非法: {interval!r}")
    return v


def parse_keep_text(text: str) -> dict:
    """纯函数：keep.txt 文本 → 条目/注释计数与条目清单（保命面只读解析）。"""
    entries: list[str] = []
    comment_lines = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            comment_lines += 1
            continue
        entries.append(line)
    return {"entries": entries, "comment_lines": comment_lines, "entry_count": len(entries)}


def build_shadow_doc(keep_path: Path, now: datetime) -> tuple[dict, str]:
    """读 keep 本体 → 影子快照 dict（含 source sha256 与 3 天有效期）；返回 (doc, raw_text)。"""
    raw = keep_path.read_text(encoding="utf-8", errors="replace")
    parsed = parse_keep_text(raw)
    sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    expires = now + timedelta(days=SHADOW_TTL_DAYS)
    doc = {
        "kind": "keep_shadow_account",
        "captured_at": now.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "expires_at": expires.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "ttl_days": SHADOW_TTL_DAYS,
        "source": keep_path.relative_to(_REPO_ROOT).as_posix()
        if keep_path.is_relative_to(_REPO_ROOT)
        else str(keep_path),
        "source_sha256": sha,
        "entry_count": parsed["entry_count"],
        "comment_lines": parsed["comment_lines"],
        "entries": parsed["entries"],
        "note": "影子账=只读抄录（零信息丢失），keep.txt 本体零触碰；对账口径=逐条目集合 diff",
    }
    return doc, raw


def prune_expired_shadows(out_dir: Path, now: datetime) -> int:
    """清理自家过期影子快照（仅 keep_shadow_*.json 且 mtime>3 天）；返回清理数。"""
    pruned = 0
    cutoff = (now - timedelta(days=SHADOW_TTL_DAYS)).timestamp()
    for p in out_dir.glob(SHADOW_GLOB):
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink()
                pruned += 1
        except OSError:
            continue
    return pruned


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="备份链 P95 时限派生 + reaper 免死影子账（C440）")
    sub = parser.add_subparsers(dest="cmd")
    p_lim = sub.add_parser("derive-limits", help="从 backup_config.yaml 派生时限读数（零写盘）")
    p_lim.add_argument("--config", type=str, default=str(DEFAULT_CONFIG))
    p_shadow = sub.add_parser("keep-shadow", help="keep.txt → 3 天影子快照 JSON（本体零触碰）")
    p_shadow.add_argument("--keep", type=str, default=str(DEFAULT_KEEP))
    p_shadow.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT_DIR))
    p_shadow.add_argument("--no-prune", action="store_true", help="跳过自家过期快照清理")
    args = parser.parse_args(argv)

    if args.cmd == "keep-shadow":
        keep_path = Path(args.keep)
        if not keep_path.is_file():
            print(f"ERROR: keep 本体不存在: {keep_path}", file=sys.stderr)
            return 2
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).astimezone()
        doc, _ = build_shadow_doc(keep_path, now)
        stamp = now.strftime("%Y%m%d_%H%M%S")
        target = out_dir / f"keep_shadow_{stamp}.json"
        content = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
        result = safe_write_text(target, content, repo_root=str(_REPO_ROOT))
        pruned = 0 if args.no_prune else prune_expired_shadows(out_dir, now)
        print(
            f"SHADOW: {result.path}（entries={doc['entry_count']} comment_lines={doc['comment_lines']} "
            f"sha256={doc['source_sha256'][:12]} expires_at={doc['expires_at']} pruned_expired={pruned}）"
        )
        return 0

    # 缺省=derive-limits
    config_path = Path(getattr(args, "config", str(DEFAULT_CONFIG)))
    if not config_path.is_file():
        print(f"ERROR: config 不存在: {config_path}", file=sys.stderr)
        return 2
    import yaml

    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    limits = derive_retention_p95(config)
    violations = validate_config(config)
    print(
        json.dumps(
            {"config": str(config_path), "derived": limits, "violations": violations}, ensure_ascii=False, indent=2
        )
    )
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
