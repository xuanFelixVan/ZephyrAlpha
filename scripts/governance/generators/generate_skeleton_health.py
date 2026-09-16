# [BLUEPRINT] MOD-AUTO-L4-001(暂编号) | docs/_working/automation/campaign/blueprints/skeleton_health_blueprint.md | §
# [MODULE] scripts.governance.generators.generate_skeleton_health
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] yaml
# [CONSUMERS] Owner（骨架级建议）+ 各施工线（血肉级建议）; ⑨骨架体检（骨架 v1.1 §1 工段⑨）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全只读（注册表/TDM/台账零写触碰）;
#   建议书两分：血肉级（可自动执行）vs 骨架级（转 Owner 拍板）——骨锁肉动制度（2026-09-17 裁定）;
#   单输入缺失降级为"缺证"小节，不阻断其余体检
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 全部输入缺失→仍产出报告（全缺证版）；out_dir 不可写→OSError 上抛
# [TESTS] tests/governance/test_generate_skeleton_health.py
# [A_module] module_id=MOD-AUTO-L4-001 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 月度骨架体检由 AI 会话/计划任务按需调用产出建议书，非进程内常驻
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
"""generate_skeleton_health — ⑨骨架体检月度报告（只读盘点→增/删/换建议书）。

体检面（全部既有真源，零新建依赖）：
  ①TDM 结构图谱（config/trading_decision_map.yaml：节点/边数+写崩 .tmp 残留卫生）
  ②骨架覆盖审计基准（docs/_working/trading_vision/2026-09-16-skeleton-coverage-audit.md 电态摘要，
    与 TDM 现节点数比对漂移）
  ③排班学籍（config/resource_profile_registry.yaml：状态分布+采样覆盖率）
  ④资源采样 (.runtime/logs/resource_samples/*.jsonl：每实体样本数)
  ⑤策略生命周期（data/runtime/strategy_decay_ledger.json：状态直方图+failed_streak 观察名单）

用法（仓库根，Python 3.12）：
    python scripts/governance/generators/generate_skeleton_health.py            # 全默认路径
    全部输入路径可注入（--tdm/--audit/--registry/--samples-dir/--decay/--out-dir，测试隔离）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from zephyr.shared.io.file_utils import safe_write_text  # noqa: E402

# 一次性 sys.path bootstrap（N 对本文件固定且仅用一次）——REPO_ROOT 真源是
# zephyr.shared.io.paths，本文件只 import 不重算（SSOT-REDEFINITION）。
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

TDM_DEFAULT = REPO_ROOT / "config" / "trading_decision_map.yaml"
AUDIT_DEFAULT = REPO_ROOT / "docs" / "_working" / "trading_vision" / "2026-09-16-skeleton-coverage-audit.md"
REGISTRY_DEFAULT = REPO_ROOT / "config" / "resource_profile_registry.yaml"
SAMPLES_DEFAULT = REPO_ROOT / ".runtime" / "logs" / "resource_samples"
DECAY_DEFAULT = REPO_ROOT / "data" / "runtime" / "strategy_decay_ledger.json"
OUT_DEFAULT = REPO_ROOT / "docs" / "_working" / "automation" / "campaign" / "health"

_ELECTRIC_RE = re.compile(
    r"(\d+)\s*个?\s*已接电\D*?(\d+)\s*个?\s*覆盖未接电\D*?(\d+)\s*个?\s*[^，,]*[、,]\s*(\d+)\s*个?\s*纯结构")


def check_tdm(tdm_path: Path) -> dict:
    out: dict = {"exists": tdm_path.exists()}
    if not out["exists"]:
        return out
    try:
        data = yaml.safe_load(tdm_path.read_text(encoding="utf-8")) or {}
        out["nodes"] = len(data.get("nodes") or [])
        out["edges"] = len(data.get("edges") or [])
        out["stale_tmp"] = sorted(
            p.name for p in tdm_path.parent.glob("trading_decision_map.yaml*tmp*")
        )
    except (yaml.YAMLError, OSError) as exc:
        out["error"] = str(exc)
    return out


def check_audit(audit_path: Path, tdm_nodes: int | None) -> dict:
    out: dict = {"exists": audit_path.exists()}
    if not out["exists"]:
        return out
    try:
        text = audit_path.read_text(encoding="utf-8")
        m = _ELECTRIC_RE.search(text)
        if m:
            wired, unwired, missing, structural = (int(x) for x in m.groups())
            out["electric"] = {"wired": wired, "unwired": unwired,
                               "missing": missing, "structural": structural,
                               "total": wired + unwired + missing + structural}
            if tdm_nodes is not None and out["electric"]["total"] != tdm_nodes:
                out["drift"] = f"审计基准 {out['electric']['total']} 节点 vs TDM 现 {tdm_nodes} 节点——骨架或图已变更，建议重跑覆盖审计"
        else:
            out["error"] = "电态摘要行未匹配（审计格式可能已变）"
    except OSError as exc:
        out["error"] = str(exc)
    return out


def check_registry(registry_path: Path) -> dict:
    out: dict = {"exists": registry_path.exists()}
    if not out["exists"]:
        return out
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
        ents = data.get("entities") or []
        by_status: dict[str, int] = {}
        for e in ents:
            s = str(e.get("status") or "unknown")
            by_status[s] = by_status.get(s, 0) + 1
        out["total"] = len(ents)
        out["by_status"] = dict(sorted(by_status.items(), key=lambda kv: -kv[1]))
    except (yaml.YAMLError, OSError) as exc:
        out["error"] = str(exc)
    return out


def check_samples(samples_dir: Path) -> dict:
    out: dict = {"exists": samples_dir.exists()}
    if not out["exists"]:
        return out
    per: dict[str, int] = {}
    for f in samples_dir.glob("*.jsonl"):
        per[f.stem] = sum(1 for ln in f.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip())
    out["entities_with_samples"] = len([k for k, v in per.items() if v > 0])
    out["sample_lines"] = per
    return out


def check_decay(decay_path: Path) -> dict:
    out: dict = {"exists": decay_path.exists()}
    if not out["exists"]:
        return out
    try:
        data = json.loads(decay_path.read_text(encoding="utf-8"))
        strategies = data.get("strategies") or {}
        states: dict[str, int] = {}
        watch = []
        for sid, info in strategies.items():
            info = info if isinstance(info, dict) else {}
            st = str(info.get("state") or "unknown")
            states[st] = states.get(st, 0) + 1
            try:
                if int(info.get("failed_streak") or 0) > 0:
                    watch.append(sid)
            except (TypeError, ValueError):
                watch.append(f"{sid}(streak 异常值)")  # 坏值也上观察名单，不炸全报告
        out["total"] = len(strategies)
        out["by_state"] = dict(sorted(states.items(), key=lambda kv: -kv[1]))
        out["failed_streak_watch"] = watch[:20]
    except (json.JSONDecodeError, OSError) as exc:
        out["error"] = str(exc)
    return out


def build_report(tdm: dict, audit: dict, registry: dict, samples: dict, decay: dict) -> str:
    now = now_utc().strftime("%Y-%m")
    flesh: list[str] = []
    bone: list[str] = []
    lines = [
        f"# 骨架体检月报（{now}，只读盘点机生）", "",
        "> 骨锁肉动制度：血肉级建议可自动执行；骨架级建议转 Owner 拍板（2026-09-17 裁定）。", "",
        "## ① TDM 结构图谱",
    ]
    if tdm.get("exists"):
        lines.append(f"- 节点 {tdm.get('nodes')} / 边 {tdm.get('edges')}")
        if tdm.get("stale_tmp"):
            lines.append(f"- ⚠ 卫生红旗：写崩 .tmp 残留 {len(tdm['stale_tmp'])} 件（{', '.join(tdm['stale_tmp'][:3])}…）")
            flesh.append(f"清理 TDM .tmp 残留 {len(tdm['stale_tmp'])} 件（三层验证后删除）")
    else:
        lines.append("- 缺证：TDM 文件不存在")
    lines += ["", "## ② 骨架覆盖审计基准"]
    if audit.get("electric"):
        e = audit["electric"]
        lines.append(f"- 电态：已接电 {e['wired']} / 覆盖未接电 {e['unwired']} / 缺失 {e['missing']} / 结构 {e['structural']}")
        if audit.get("drift"):
            lines.append(f"- ⚠ 漂移：{audit['drift']}")
            bone.append("重跑骨架覆盖审计（TDM 节点数与审计基准漂移）")
    else:
        lines.append(f"- 缺证：{audit.get('error') or '审计文件不存在'}")
    lines += ["", "## ③ 排班学籍"]
    if registry.get("exists"):
        lines.append(f"- 实体 {registry.get('total')}，状态分布：{registry.get('by_status')}")
        orphaned = (registry.get("by_status") or {}).get("orphaned_source", 0)
        if orphaned:
            bone.append(f"{orphaned} 个 orphaned_source 实体待 Owner 裁删除")
    else:
        lines.append("- 缺证：注册表不存在")
    lines += ["", "## ④ 资源采样覆盖"]
    if samples.get("exists"):
        lines.append(f"- 有样本实体 {samples.get('entities_with_samples')} 个（采样行明细略）")
        flesh.append("对零样本实体补采样观察映射（ops_* 种子等）")
    else:
        lines.append("- 缺证：采样目录不存在")
    lines += ["", "## ⑤ 策略生命周期"]
    if decay.get("exists"):
        lines.append(f"- 候选 {decay.get('total')}，状态直方图：{decay.get('by_state')}")
        if decay.get("failed_streak_watch"):
            lines.append(f"- 观察名单（failed_streak>0）：{', '.join(decay['failed_streak_watch'][:8])}…")
    else:
        lines.append("- 缺证：decay 台账不存在")
    lines += ["", "## 建议书（骨锁肉动两分）", "", "### 血肉级（可自动执行）"]
    lines += [f"- {x}" for x in flesh] or ["-（本月经 clean）"]
    lines += ["", "### 骨架级（转 Owner 拍板）"]
    lines += [f"- {x}" for x in bone] or ["-（本月经 clean）"]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="⑨骨架体检月度报告（只读盘点）")
    ap.add_argument("--tdm", type=str, default=str(TDM_DEFAULT))
    ap.add_argument("--audit", type=str, default=str(AUDIT_DEFAULT))
    ap.add_argument("--registry", type=str, default=str(REGISTRY_DEFAULT))
    ap.add_argument("--samples-dir", type=str, default=str(SAMPLES_DEFAULT))
    ap.add_argument("--decay", type=str, default=str(DECAY_DEFAULT))
    ap.add_argument("--out-dir", type=str, default=str(OUT_DEFAULT))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tdm = check_tdm(Path(args.tdm))
    audit = check_audit(Path(args.audit), tdm.get("nodes"))
    registry = check_registry(Path(args.registry))
    samples = check_samples(Path(args.samples_dir))
    decay = check_decay(Path(args.decay))
    report = build_report(tdm, audit, registry, samples, decay)
    if args.dry_run:
        print(report)
        return 0
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"skeleton-health-{now_utc().strftime('%Y%m')}.md"
    safe_write_text(out, report)
    print(f"OK: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
