# [BLUEPRINT] MOD-BT-242 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.writeback_exam_confidence
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] config/trading_decision_map.yaml; docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml;
#   zephyr.trading.decision_map; zephyr.shared.io.file_utils
# [CONSUMERS] W4 校准战役出分后的 confidence 回写位（考试卡 lineage.confidence_writeback 指向本工具管辖面）;
#   人工 CLI（分数册更新后重跑）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] v1 判据冻结（裁定#501，禁事后挪门柱 G4-5）：升级 proposed/untested→verified 当且仅当
#   分数行 verdict=pass 且 oos_ok 且 regimes ⊇ {bull,bear}（双行情段；W4 纪律：单变量候选关系禁升级）；
#   降级 verified→proposed 仅 decay_scan 行 verdict=fail；其余 fail 不动 confidence（只标候选关系）；
#   每次回写附分数行指针进 summary；TDM 编辑=节点块内 confidence 行外科替换（禁整文件重排）；
#   写后必过 load_decision_map 校验；写必经 safe_write_text CAS；缺省 dry-run。
# [MODIFY-GUARD] tests/backtest/test_writeback_exam_confidence.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError: 分数册缺字段/节点块定位失败/写后校验失败/CAS 冲突
# [TESTS] tests/backtest/test_writeback_exam_confidence.py
# [A_module] module_id=MOD-BT-242 | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [not-trading: 回测研究面工具（考试卡骨架/校准执行/置信度回写），不在实盘交易决策路径上；TDM 挂载随分数册集成批另办]
"""考试卡分数册 → TDM confidence 机生回写（W5 闭环件；裁定#501 冻结 v1 判据）。

读分数册 exam_scores_v1.yaml（每 examined 卡一行）→ 按冻结判据对 TDM 节点 confidence
做机械迁移 → 写回 config/trading_decision_map.yaml（节点块内 confidence 行外科替换）。

分数行 schema（v1）：
    card_id: <node_id>/<family>/<seq>
    node_id: TDM-E-...
    run_id: <run 档案号>
    kind: exam | decay_scan          # exam=常规考试行；decay_scan=衰减扫描行
    verdict: pass | fail
    pillars_all_pass: true|false     # 门柱全过与否
    oos_ok: true|false               # OOS 窗成立
    regimes: [bull, bear]            # 行情段覆盖（≥2 段含牛熊才可升级）
    date: 'YYYY-MM-DD'

用法:
    python scripts/backtest/writeback_exam_confidence.py             # dry-run 报告
    python scripts/backtest/writeback_exam_confidence.py --apply     # 实写
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT

TDM_PATH = REPO_ROOT / "config" / "trading_decision_map.yaml"
SCORES_PATH = REPO_ROOT / "docs" / "04_research_records" / "backtest" / "scores" / "2026" / "exam_scores_v1.yaml"

_REGIMES_BULL_BEAR = {"bull", "bear"}


class _ToolError(RuntimeError):
    def __init__(self, msg: str, details: dict | None = None):
        super().__init__(msg)
        self.details = details or {}


def load_score_rows(scores_path: Path = SCORES_PATH) -> list[dict]:
    docs = [d for d in yaml.safe_load_all(Path(scores_path).read_text(encoding="utf-8")) if isinstance(d, dict)]
    rows = next((d.get("rows") for d in docs if d.get("rows")), None)  # 双文档 register 兼容（裁定#536）
    if not rows:
        raise _ToolError("分数册无 rows 或为零行", {"path": str(scores_path)})
    required = {"card_id", "node_id", "run_id", "kind", "verdict"}
    for i, r in enumerate(rows):
        missing = required - set(r)
        if missing:
            raise _ToolError("分数行缺字段（fail-closed）", {"row_index": i, "missing": sorted(missing)})
    return rows


def decide_transition(row: dict, current: str) -> tuple[str | None, str]:
    """冻结判据（裁定#501）：返回 (新 confidence|None, 理由)。None=不变。"""
    verdict = row.get("verdict")
    if row.get("kind") == "decay_scan":
        if verdict == "fail" and current == "verified":
            return "proposed", "decay_scan fail：verified 降级 proposed（衰减扫描触发）"
        return None, f"decay_scan {verdict}：不触发迁移（current={current}）"
    # 常规考试行
    if verdict != "pass":
        return None, "exam fail：只标候选关系，confidence 不动（W4 纪律）"
    regimes = set(row.get("regimes") or [])
    if not (row.get("pillars_all_pass") is True and row.get("oos_ok") is True and regimes >= _REGIMES_BULL_BEAR):
        return None, (
            "exam pass 但三条件不全（pillars_all_pass/oos_ok/双行情段）——"
            "维持候选关系不升级（W4 纪律：过 OOS+双行情段才升级）"
        )
    if current in ("proposed", "untested"):
        return "verified", "exam pass+OOS+双行情段全齐：升级 verified"
    return None, f"已是 {current}：无迁移"


def _replace_node_confidence(text: str, node_id: str, new_conf: str) -> tuple[str, str] | None:
    """节点块内 confidence 行外科替换；返回 (新文本, 旧值)。定位失败返回 None。"""
    lines = text.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.rstrip() == f"- node_id: {node_id}":
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^- node_id: ", lines[j]):
            end = j
            break
    old = None
    for j in range(start + 1, end):
        m = re.match(r"^  confidence: (\S+)$", lines[j])
        if m:
            old = m.group(1)
            lines[j] = f"  confidence: {new_conf}"
            break
    if old is None:
        return None
    return "\n".join(lines), old


def run(
    apply: bool = False, tdm_path: Path = TDM_PATH, scores_path: Path = SCORES_PATH, post_validate: bool = True
) -> dict:
    rows = load_score_rows(scores_path)
    text = Path(tdm_path).read_text(encoding="utf-8")
    transitions: list[dict] = []
    for row in rows:
        node_id = row["node_id"]
        m = re.search(rf"- node_id: {re.escape(node_id)}\n(.*?)(?=^- node_id: |\Z)", text, re.S | re.M)
        if not m:
            raise _ToolError("分数行节点不在 TDM（fail-closed）", {"node_id": node_id})
        cm = re.search(r"^  confidence: (\S+)$", m.group(1), re.M)
        if not cm:
            raise _ToolError("节点缺 confidence 行", {"node_id": node_id})
        current = cm.group(1)
        new_conf, reason = decide_transition(row, current)
        if new_conf is None or new_conf == current:
            transitions.append(
                {
                    "card_id": row["card_id"],
                    "node_id": node_id,
                    "from": current,
                    "to": new_conf or current,
                    "changed": False,
                    "reason": reason,
                }
            )
            continue
        transitions.append(
            {
                "card_id": row["card_id"],
                "node_id": node_id,
                "from": current,
                "to": new_conf,
                "changed": True,
                "reason": reason,
                "run_id": row.get("run_id"),
            }
        )
        if apply:
            replaced = _replace_node_confidence(text, node_id, new_conf)
            if replaced is None:
                raise _ToolError("节点块 confidence 行替换失败", {"node_id": node_id})
            text, _old = replaced
    if apply:
        changed = [t for t in transitions if t["changed"]]
        if changed:
            result = safe_write_text(Path(tdm_path), text, repo_root=REPO_ROOT)
            if not result.written:
                raise _ToolError("TDM CAS 写失败", {"result": str(result)})
            # 写后校验：整图重载（R 系校验全跑）；生产恒开，最小夹具测试可关
            if post_validate:
                from zephyr.trading.decision_map import load_decision_map

                load_decision_map(Path(tdm_path))
    return {
        "apply": apply,
        "rows": len(rows),
        "changed": sum(1 for t in transitions if t["changed"]),
        "transitions": transitions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="实写（缺省 dry-run 报告）")
    parser.add_argument("--scores", default=str(SCORES_PATH), help="分数册路径")
    args = parser.parse_args()
    summary = run(apply=args.apply, scores_path=Path(args.scores))
    import json

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  人工CLI设计如此（同域MOD-BT-197先例）：按TDM变更/分数册更新/逐卡开考人工触发，非永久自动系统面
    sys.exit(main())
