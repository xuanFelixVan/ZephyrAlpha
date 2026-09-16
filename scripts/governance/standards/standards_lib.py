# [BLUEPRINT] MOD-AUTO-L5-001(暂编号) | docs/_working/automation/campaign/blueprints/standards_lib_blueprint.md | §
# [MODULE] scripts.governance.standards.standards_lib
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] yaml
# [CONSUMERS] promotion_combo_gate（阈值改由标准库供给的切换点）; 未来修标提案流水线（AI 层）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读库（本模块不写 standards.yaml——修标=治理层动作）;
#   regrade_diff 纯函数：给出新旧阈值+候选成绩，输出裁定翻转清单（修标重考历史的核心件）;
#   draft 状态的标准不得作为生效考纲
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 标准 ID 不存在→KeyError; YAML 损坏→异常上抛
# [TESTS] tests/governance/test_standards_lib.py
# [A_module] module_id=MOD-AUTO-L5-001 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
"""standards_lib — 考纲标准库加载器+修标重考历史工具（骨架 v1.1 §8）。

用法（仓库根，Python 3.12）：
    python -m scripts.governance.standards.standards_lib --check
    python scripts/governance/standards/standards_lib.py --regrade \\
        --std STD-SIM-ACCESS-001 --candidates cands.json   # 用 frozen 尺子打分（v0：展示口径）
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

# 一次性 sys.path bootstrap（N 对本文件固定且仅用一次；先例 scripts/governance/_shared/constants.py
# 的 _PROJECT_ROOT——bootstrap 用的局部量不叫 REPO_ROOT，避免与真源同名）。
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # scripts/governance/standards/ -> 仓库根
for _p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT

STANDARDS_PATH = REPO_ROOT / "config" / "standards.yaml"

# noqa: m11-perm-manual-legitimate  M11豁免: 治理层修标/校验按需调用的标准库工具（--check/--regrade），非自动触发常驻


def load_standards(path: Path | str = STANDARDS_PATH) -> dict[str, dict]:
    """标准库 → {std_id: 标准 dict}；draft 状态带标记。"""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    out: dict[str, dict] = {}
    for s in data.get("standards") or []:
        s = dict(s)
        s["_frozen"] = s.get("status") == "frozen"
        out[str(s["std_id"])] = s
    return out


def get_frozen_thresholds(std_id: str, standards: dict[str, dict] | None = None) -> dict:
    """取 frozen 标准的阈值；draft/damaged → ValueError（draft 不得作生效考纲）。"""
    stds = standards if standards is not None else load_standards()
    if std_id not in stds:
        raise KeyError(f"标准不存在: {std_id}")
    std = stds[std_id]
    if not std.get("_frozen"):
        raise ValueError(f"标准 {std_id} 状态={std.get('status')}，draft 不得作为生效考纲")
    return dict(std.get("thresholds") or {})


def regrade_diff(old: dict, new: dict, candidates: list[dict]) -> list[dict]:
    """修标重考历史核心：新旧阈值对同一批候选重打分，输出裁定翻转清单。

    候选口径：{id, oos_sharpe, max_drawdown, trades, dsr}（与组合门四条对齐，缺项=该条跳过）。
    """
    def verdict(th: dict, c: dict) -> str:
        results = []
        if c.get("oos_sharpe") is not None:
            results.append(c["oos_sharpe"] >= th.get("oos_sharpe_min", 1.5))
        if c.get("max_drawdown") is not None:
            results.append(c["max_drawdown"] <= th.get("max_drawdown_max", 0.15))
        if c.get("trades") is not None:
            results.append(c["trades"] >= th.get("min_trades", 30))
        if c.get("dsr") is not None:
            results.append(c["dsr"] > th.get("dsr_min", 0.0))
        if not results:
            return "borderline"
        return "promote_ready" if all(results) else "reject"

    flips = []
    for c in candidates:
        v_old, v_new = verdict(old, c), verdict(new, c)
        if v_old != v_new:
            flips.append({"id": c.get("id"), "old": v_old, "new": v_new})
    return flips


def main() -> int:
    ap = argparse.ArgumentParser(description="考纲标准库工具（check/regrade）")
    ap.add_argument("--check", action="store_true", help="校验 standards.yaml 可解析+frozen 状态")
    ap.add_argument("--regrade", action="store_true", help="重考历史演示：frozen 尺子对样例候选打分")
    ap.add_argument("--candidates", type=str, default=None, help="候选 JSON（regrade 用）")
    args = ap.parse_args()
    stds = load_standards()
    if args.check:
        for sid, s in stds.items():
            print(f"{sid}: status={s.get('status')} frozen={s['_frozen']}")
        return 0
    if args.regrade:
        cands = json.loads(Path(args.candidates).read_text(encoding="utf-8")) if args.candidates else [
            {"id": "demo-A", "oos_sharpe": 1.8, "max_drawdown": 0.10, "trades": 40, "dsr": 0.4},
            {"id": "demo-B", "oos_sharpe": 1.3, "max_drawdown": 0.12, "trades": 35, "dsr": 0.2},
        ]
        th = get_frozen_thresholds("STD-SIM-ACCESS-001", stds)
        flips = regrade_diff(th, th, cands)  # 同尺自检=零翻转
        print(json.dumps({"thresholds": th, "flips": flips}, ensure_ascii=False))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
