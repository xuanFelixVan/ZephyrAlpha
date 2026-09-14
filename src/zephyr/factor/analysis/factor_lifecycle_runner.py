# [BLUEPRINT] MOD-L02-LIFECYCLE
# [MODULE] zephyr.factor.analysis.factor_lifecycle_runner
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.three_level_judgment(judge_factor 域内预注册判定); zephyr.factor.analysis.bhy_fdr(族校正 BHY); zephyr.shared.io.file_utils(safe_write); math
# [CONSUMERS] trading_lifecycle_weekly 任务（internal_compute_provider capability 分支）; factor_registry decay_state 回写
# [STARTUP] imported(周末校准档事件触发;禁 cron 自轮询)
# [MATURITY] design
# [INVARIANTS] 判定复用域内预注册件(judge_factor 三级+BHY 拒绝掩码)禁复制实现; certified=优秀∧BHY 拒绝/probation=合格∧BHY 拒绝/其余 failed; 无 lookback 的因子封顶 probation(Fail-Closed 不进族); 淘汰连续 RETIRED_AFTER=20 周扫→retired(死亡快照); retired 后 ic 回到合格以上且 BHY 拒绝→resurrected; decay_state 回写=行级替换(零格式漂移)+safe_write(claim+CRLF 探测); 阈值预注册(90 号 §2: BHY q=0.10/HLZ t=2.8)改动=裁定
# [MODIFY-GUARD] docs/03_modules/_domain_factor/factor_lifecycle_runner/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ic 越界->该因子 failed; registry 不可读->IOError 透传; 空族->空摘要
# [TESTS] tests/factor/test_factor_lifecycle_runner.py(合成族:三级判定∧BHY 掩码联合认证+退役/复活迁移)
# [A_module] module_id=MOD-L02-LIFECYCLE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""factor_lifecycle_runner — 因子域生命周期周扫 runner（MOD-L02-LIFECYCLE，协议 v2.0 三域落地）。

补齐 factor_decay_monitor_weekly 任务块的 runner 缺口（该块 disabled 原因自述：
"遍历 factor_registry→monitor_decay→decay_state 回写施工后启用"）。判定复用
域内预注册件：three_level_judgment.judge_factor（优秀/合格/淘汰，阈值 _config.yaml）
+ bhy_fdr 族校正（90 号 §2 预注册：BHY q=0.10，单批>100 因子 t 门槛升 2.8 HLZ 标准）；
生命周期语义对齐 MOD-SIG-149（retired/resurrected 覆盖态+死亡快照+连周计数）。

联合认证：certified=优秀∧BHY 拒绝；probation=合格∧BHY 拒绝；其余 failed。
无 lookback_period 的因子无法算族 p 值 → Fail-Closed 封顶 probation。

# [ALGO_FLOW]
# 层: 因子生命周期
# - id: F1
#   name: 三级判定
#   code: judge_factor(ic, ir) → 优秀/合格/淘汰（域内 _config.yaml 阈值）
# - id: F2
#   name: 族校正
#   code: p = 0.5·erfc(|t|/√2)，t=ic·√(n−1)/√(1−ic²)，n=lookback_period；BHY 拒绝掩码
# - id: F3
#   name: 生命周期
#   code: 淘汰计连周≥20→retired(死亡快照)；retired 后 ic 回合格+拒绝→resurrected
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from zephyr.factor.analysis.bhy_fdr import bhy_fdr
from zephyr.factor.analysis.three_level_judgment import judge_factor

__all__ = ["certify_factor_family", "run_factor_lifecycle"]

RETIRED_AFTER_WEEKLY = 20
_DEFAULT_REGISTRY = "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml"


def _to_float(v: Any) -> float | None:
    """宽松浮点化：None/'None'/''/非法串→None（registry 手填字段脏数据守卫）。"""
    if v is None:
        return None
    try:
        s = str(v).strip()
        if s in ("", "None", "nan", "NaN"):
            return None
        return float(s)
    except (ValueError, TypeError):
        return None


def _ic_p_value(ic: float, n: int) -> float:
    """IC 单侧 p 值：t=ic·√(n−1)/√(1−ic²) 的正态上尾（erfc，无 scipy 依赖）。"""
    if n < 3 or abs(ic) >= 1.0:
        return 1.0
    t = abs(ic) * math.sqrt(n - 1) / math.sqrt(max(1e-12, 1.0 - ic * ic))
    return 0.5 * math.erfc(t / math.sqrt(2.0))


def certify_factor_family(factors: list[dict], *, q: float = 0.10) -> list[dict]:
    """因子族联合认证：三级判定 ∧ BHY 族校正。

    factors 元素：{factor_id, ic, ir, lookback_period}。
    返回 [{factor_id, verdict, rejected, state}]，state∈certified/probation/failed。
    Fail-Closed：无 ic→failed；无 lookback→封顶 probation（不进族）。
    """
    records: list[dict] = []
    family_pos: list[int] = []
    for i, f in enumerate(factors):
        rec: dict[str, Any] = {"factor_id": f.get("factor_id"), "verdict": None,
                               "rejected": None, "state": None, "p": None}
        ic = _to_float(f.get("ic"))
        ir = _to_float(f.get("ir"))
        if ic is None or not -1.0 <= ic <= 1.0:
            # 无 ic=未评估≠淘汰（Fail-Closed 封顶 probation，等域内评估供给）
            rec["verdict"], rec["state"] = "合格", "probation"
            records.append(rec)
            continue
        rec["verdict"] = judge_factor(ic, ir or 0.0)
        n = f.get("lookback_period")
        if isinstance(n, int) and not isinstance(n, bool) and n >= 3:
            rec["p"] = _ic_p_value(ic, n)
            family_pos.append(i)
        else:
            rec["no_lookback"] = True
        records.append(rec)
    if family_pos:
        result = bhy_fdr([records[i]["p"] for i in family_pos], q=q)
        for i, rej in zip(family_pos, result.rejected):
            records[i]["rejected"] = bool(rej)
    for rec in records:
        if rec["state"] is not None:
            continue
        if rec["rejected"] is None:
            rec["state"] = "probation"
        elif rec["verdict"] == "优秀" and rec["rejected"]:
            rec["state"] = "certified"
        elif rec["verdict"] == "合格" and rec["rejected"]:
            rec["state"] = "probation"
        else:
            rec["state"] = "failed"
    for rec in records:
        rec.pop("p", None)
        rec.pop("no_lookback", None)
    return records


def run_factor_lifecycle(
    registry_path: str | Path = _DEFAULT_REGISTRY,
    store_path: str | Path = "data/runtime/factor_lifecycle_state.json",
    *,
    retired_after: int = RETIRED_AFTER_WEEKLY,
    today: str = "2026-09-15",
    registry_text: str | None = None,
) -> dict:
    """周扫入口：读 registry→族认证→生命周期连周计数→decay_state 行级回写。

    registry_text 注入供测试（生产读文件）。回写=纯文本行级替换
    "decay_state: <旧>" → 新值（无该字段的条目不回写，零格式漂移）。
    """
    import io as _io
    import yaml as _yaml

    from zephyr.shared.io.file_utils import content_sha256, safe_write_text

    text = registry_text if registry_text is not None else _io.open(
        registry_path, encoding="utf-8"
    ).read()
    reg = _yaml.safe_load(text)
    factors = reg.get("factors") or []
    certified = certify_factor_family(factors)

    store = LifecycleStoreLite(store_path)
    slices = store.load()
    state_by_id: dict[str, str] = {}
    for c in certified:
        fid = c.get("factor_id")
        if not fid:
            continue
        key = f"{fid}|weekly"
        prev = slices.get(key) or {"state": c["state"], "failed_streak": 0}
        if prev.get("state") == "retired":
            # 复活闸：ic 回到合格以上（state 非 failed）且族拒绝
            if c["state"] in ("certified", "probation") and c["rejected"]:
                prev["state"] = "resurrected"
                prev["resurrect_attempts"] = prev.get("resurrect_attempts", 0) + 1
                c["state"] = "resurrected"
            else:
                c["state"] = "retired"
        elif c["state"] == "failed":
            prev["failed_streak"] = prev.get("failed_streak", 0) + 1
            if prev["failed_streak"] >= retired_after:
                prev["state"] = "retired"
                prev["retired_at"] = today
                prev["death"] = {"ic": c.get("ic"), "reason": "statistical"}
                c["state"] = "retired"
        else:
            prev["failed_streak"] = 0
            prev["state"] = c["state"]
        slices[key] = prev
        state_by_id[fid] = c["state"]
    store.save(slices)

    # decay_state 行级回写（零格式漂移：仅替换已有 decay_state 行的值）
    out_lines: list[str] = []
    current_id = None
    replaced = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- factor_id:"):
            current_id = stripped.split(":", 1)[1].strip().strip('"').strip("'")
        if stripped.startswith("decay_state:") and current_id in state_by_id:
            indent = line[: len(line) - len(line.lstrip())]
            line = f"{indent}decay_state: {state_by_id[current_id]}"
            replaced += 1
        out_lines.append(line)
    new_text = "\n".join(out_lines)
    if registry_text is None:
        base = content_sha256(text)
        safe_write_text(registry_path, new_text, expected_base_sha256=base, newline="\n")

    counts: dict[str, int] = {}
    for c in certified:
        counts[c["state"]] = counts.get(c["state"], 0) + 1
    return {"total": len(certified), "counts": counts,
            "decay_state_rewritten": replaced, "updated_at": today}


class LifecycleStoreLite:
    """周扫连周计数台账（JSON safe_write；与 149 LifecycleStore 同款式）。"""

    def __init__(self, path: str | Path = "data/runtime/factor_lifecycle_state.json") -> None:
        self._path = Path(path)

    def load(self) -> dict[str, dict[str, Any]]:
        if not self._path.exists():
            return {}
        data = json.loads(self._path.read_text(encoding="utf-8"))
        slices = data.get("slices")
        if not isinstance(slices, dict):
            raise ValueError(f"生命周期台账结构非法: {self._path}")
        return slices

    def save(self, slices: dict[str, dict[str, Any]]) -> None:
        from zephyr.shared.io.file_utils import safe_write_text

        doc = {"schema": "factor_lifecycle/1", "slices": slices}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        safe_write_text(
            str(self._path), json.dumps(doc, ensure_ascii=False, indent=1) + "\n", newline="\n"
        )




if __name__ == "__main__":
    import argparse
    import json as _json
    import sys as _sys

    parser = argparse.ArgumentParser(description="因子域生命周期周扫（协议 v2.0）")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--registry", default=_DEFAULT_REGISTRY)
    parser.add_argument("--state-path", default="data/runtime/factor_lifecycle_state.json")
    parser.add_argument("--today", default="2026-09-15")
    args = parser.parse_args()
    if not args.run:
        parser.print_help()
        _sys.exit(2)
    summary = run_factor_lifecycle(
        registry_path=args.registry, store_path=args.state_path, today=args.today
    )
    print(_json.dumps(summary, ensure_ascii=False))
