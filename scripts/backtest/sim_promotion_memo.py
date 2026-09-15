# [BLUEPRINT] MOD-BT-193 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.sim_promotion_memo
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.strategy_pipeline.screen_source; zephyr.shared.io.file_utils
# [CONSUMERS] Owner sim→production 签字前最后一眼；pipeline_events.sim_memo_monthly（月度档）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读生成（台账/注册表零触碰）；建议书=机器备料，签字权=Owner（OwnerTokenGuard，
#   机器流程不带 token 天然停门）；数字全部来自 strategy_screen 真源（键=strategy_id+source_file）；
#   建议非裁定：输出=评估要点+反证清单，不做 production 推荐结论
# [MODIFY-GUARD] tests/backtest/test_sim_promotion_memo.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(sim 台账不可达)；单策略数据缺失降级为"数据不足"段落不阻断
# [TESTS] tests/backtest/test_sim_promotion_memo.py
# [A_module] module_id=MOD-BT-193 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] sim-promotion-memo-mod-bt-193-20260915
"""sim 绩效月报+转正建议书生成器（交接清单⑭）——Owner 签字前最后一眼由机器备好。

月度档由 pipeline_events（MOD-BT-190）事件唤醒点评估到期后调用（sim_memo_monthly），
也可手动：python scripts/backtest/sim_promotion_memo.py
产出：docs/_working/pipeline-research/sim-memos/sim-memo-<YYYYMM>.md
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

MEMO_DIR = ROOT / "docs/_working/pipeline-research/sim-memos"
from zephyr.strategy_pipeline.registry_writer import REGISTRY  # noqa: PLC0415——SSoT 路径单一真源（VOCAB-CHAIN）


def _q(sql: str) -> list[tuple]:
    from zephyr.data.ch_writer import get_client_strict

    return get_client_strict().execute(sql)


def _stats_for(source_file: str) -> dict[str, Any]:
    """单翻译件 IS+各 OOS 段成绩（bothwin 同源口径）。"""
    rows = _q(
        "SELECT strategy_id, screen_batch, verdict, is_sharpe, oos_years_decay, screened_at "
        "FROM c1_backtest.strategy_screen "
        f"WHERE source_file = '{source_file}' AND is_sharpe IS NOT NULL ORDER BY screened_at")
    is_v = next((r[3] for r in rows if r[2] == "translated_c4"), None)
    oos = [{"batch": r[1], "sharpe": r[3], "decay": r[4]} for r in rows if r[2] == "oos_tested"]
    return {"is_sharpe": is_v, "oos": oos}


def collect() -> dict[str, list[dict[str, Any]]]:
    """注册表 sim/candidate 两档条目+台账成绩。"""
    import yaml

    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    sims, cands = [], []
    for e in reg.get("strategies", []):
        life = (e.get("lifecycle_status") or "").lower()
        if life not in ("sim", "candidate"):
            continue
        item = {"sid": e["strategy_id"], "name": e.get("name_zh") or e.get("name"),
                "cls": e.get("strategy_class"), "code_path": e.get("code_path") or "",
                "evidence": (e.get("evidence") or "")[:160]}
        try:
            item["stats"] = _stats_for(e["code_path"]) if e.get("code_path") else {}
        except Exception as exc:  # noqa: BLE001——单条目台账缺失降级不阻断
            item["stats"] = {"error": str(exc)[:120]}
        (sims if life == "sim" else cands).append(item)
    return {"sim": sims, "candidate": cands}


def generate(out_dir: Path | None = None, now: time.struct_time | None = None) -> dict[str, Any]:
    """生成月度建议书（Markdown 一页+JSON 同名）。返回回执。"""
    data = collect()
    stamp = time.strftime("%Y%m", now or time.localtime())
    out_dir = out_dir or MEMO_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    md = out_dir / f"sim-memo-{stamp}.md"
    lines = [
        f"# sim 绩效月报+转正建议书——{stamp}",
        "",
        f"> {time.strftime('%Y-%m-%d %H:%M')}｜MOD-BT-193 机器备料｜**sim→production = Owner 门"
        "（OwnerTokenGuard），本件非裁定、仅评估要点**",
        "",
        f"## sim 档（{len(data['sim'])} 条）",
        "",
    ]
    if not data["sim"]:
        lines.append("（当前无 sim 档条目）")
    for it in data["sim"]:
        st = it.get("stats") or {}
        oos_txt = "; ".join(f"{o['batch']}:SR={o['sharpe']}(衰减{o['decay']})" for o in st.get("oos", [])) or "无"
        lines += [f"### {it['sid']} {it['name']}",
                  f"- 类别：{it['cls']}｜代码：`{it['code_path']}`",
                  f"- IS Sharpe：{st.get('is_sharpe')}｜OOS：{oos_txt}",
                  f"- 入库证据：{it['evidence']}",
                  "- Owner 评估要点：①模拟盘成交/滑点与回测口径偏差 ②最近一段 OOS 是否仍>0 ③与实盘 sleeve 相关系数 ④容量与换手可执行性",
                  ""]
    lines += [f"## candidate 档留观（{len(data['candidate'])} 条）", ""]
    for it in data["candidate"]:
        st = it.get("stats") or {}
        oos_n = len(st.get("oos", []))
        lines.append(f"- {it['sid']} {it['name']}（{it['cls']}）：IS={st.get('is_sharpe')}，OOS 段数={oos_n}"
                     + ("｜BH-FDR 留观（q≤0.10 未过，强证据批次出现时自动流转）" if oos_n else ""))
    md.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    md.with_suffix(".json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1, default=str), encoding="utf-8", newline="\n")
    return {"path": str(md), "sim_n": len(data["sim"]), "candidate_n": len(data["candidate"])}


def main() -> int:
    out = generate()
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
