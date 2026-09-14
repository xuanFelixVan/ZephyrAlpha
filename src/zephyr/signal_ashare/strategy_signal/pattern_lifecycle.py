# [BLUEPRINT] MOD-SIG-149
# [MODULE] zephyr.signal_ashare.strategy_signal.pattern_lifecycle
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_evidence_certifier(四闸记录); zephyr.shared.io.file_utils(safe_write); math
# [CONSUMERS] pattern_evidence_certifier.run_certify(单写手接线:落表前 lifecycle 覆盖); 前端图形库页(退役徽章); 跨域复活协议(策略/因子域接线,协议文档=docs/_working/pattern_line/resurrection-protocol.md)
# [STARTUP] imported(随 certify 任务同进程;禁 cron 自轮询)
# [MATURITY] design
# [INVARIANTS] 生命周期状态机 retired/resurrected/frozen 为 148 三态之上的覆盖层(单写手:落表前覆盖当日判定,无双写者); 死亡快照={retired_at,n,hit_rate,baseline}为复活对照原点; 复活闸=死后增量二项检验 p<0.01(二次 0.005)且新事件≥50; 尝试预算=2(满额 frozen,Owner 门位解冻); structural 死因冻结自动复活(仅 Owner); 阈值预注册改动=裁定; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/pattern_lifecycle/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 记录缺字段/率越界->ValueError; store 不可写->safe_write 异常透传; 结构性死因复活请求->拒绝并提示 Owner 门位
# [TESTS] tests/signal_ashare/strategy_signal/test_pattern_lifecycle.py(合成 45 窗全循环:certified→20 failed→retired→复活→二次退役→frozen)
# [A_module] module_id=MOD-SIG-149 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pattern_lifecycle — 复活观察生命周期层（MOD-SIG-149，消费班续班）。

图形域试点实现（方案 v1.0：docs/_working/pattern_line/resurrection-watch-plan.md）。
在 MOD-SIG-148 三态（certified/probation/failed）之上的覆盖层：

    failed 连续 RETIRED_AFTER 窗 → retired（死亡快照=复活对照原点）
    retired → 死后增量过复活闸（p<0.01 且新事件≥50）→ resurrected
    resurrected 再退役 → 复活失败满 2 次 → frozen（Owner 门位解冻）

核心洞察：退役日=天然无偏样本起点（死后数据不受死前任何污染），复活判定
只需在死后增量上重跑统计。死因分类 statistical/structural——结构性死亡
冻结自动复活（机器看不出游戏规则变了，Owner 门位专属）。

# [ALGO_FLOW]
# 层: 生命周期
# - id: L1
#   name: 退役计数
#   code: failed_streak 连续 RETIRED_AFTER=20 窗 → retired+死亡快照；certified/probation 归零
# - id: L2
#   name: 复活闸
#   code: new_n=new_n_events−快照n ≥50 且 binomial_ge_pvalue(new_hits,new_n,快照baseline)<阈值(0.01/二次0.005) → resurrected
# - id: L3
#   name: 尝试预算
#   code: resurrect_failures≥2 → frozen（Owner 门位解冻）
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from zephyr.shared.io.file_utils import safe_write_text

__all__ = [
    "RETIRED_AFTER",
    "RESURRECT_Q_FIRST",
    "RESURRECT_Q_SECOND",
    "RESURRECT_MIN_NEW_EVENTS",
    "RESURRECT_MAX_ATTEMPTS",
    "LifecycleStore",
    "update_lifecycle",
]

RETIRED_AFTER = 20
RESURRECT_Q_FIRST = 0.01
RESURRECT_Q_SECOND = 0.005
RESURRECT_MIN_NEW_EVENTS = 50
RESURRECT_MAX_ATTEMPTS = 2
DEFAULT_STORE_PATH = "data/runtime/pattern_lifecycle_state.json"


def _key(pattern_id: str, timeframe: str, direction: str, fwd_window: int) -> str:
    return f"{pattern_id}|{timeframe}|{direction}|{fwd_window}"


def binomial_ge_pvalue_small(hits: float, n: float, p0: float) -> float:
    """单侧二项检验（148 同法局部复用，避免跨模块私有导入）。"""
    if n <= 0:
        return 1.0
    if hits > n:
        return 0.0
    if hits <= 0:
        return 1.0
    total = 0.0
    for i in range(int(math.ceil(hits)), int(n) + 1):
        logpmf = (
            math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
            + i * math.log(p0) + (n - i) * math.log1p(-p0)
        )
        total += math.exp(logpmf)
        if total >= 1.0:
            return 1.0
    return min(1.0, total)


class LifecycleStore:
    """生命周期台账 JSON 持久化（safe_write CAS；path 注入，测试 tmp_path）。"""

    def __init__(self, path: str | Path = DEFAULT_STORE_PATH) -> None:
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
        doc = {"schema": "pattern_lifecycle/1", "slices": slices}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        safe_write_text(
            str(self._path), json.dumps(doc, ensure_ascii=False, indent=1) + "\n", newline="\n"
        )


def update_lifecycle(
    records: list[dict],
    store: LifecycleStore,
    *,
    baseline_by_key: dict[str, float] | None = None,
    today: str,
) -> dict[str, list[str]]:
    """每日认证记录 → 生命周期流转（单写手：可覆盖 record.state 为 retired/frozen）。

    records 元素：{key, state, hit_rate, n_events}（key=pid|tf|dir|win 四元组串）。
    返回摘要 {"retired": [key], "resurrected": [key], "frozen": [key]}。
    分支互斥：retired/frozen 切片走专属通道后必 continue，不贯穿三态块。
    """
    slices = store.load()
    baseline_by_key = baseline_by_key or {}
    summary: dict[str, list[str]] = {"retired": [], "resurrected": [], "frozen": []}
    for rec in records:
        key = rec["key"]
        state = rec.get("state")
        cur = slices.get(key) or {
            "state": state, "failed_streak": 0, "resurrect_attempts": 0,
            "resurrect_failures": 0, "death": None,
        }
        # ── frozen：终态（Owner 门位解冻），只覆盖展示态 ──
        if cur["state"] == "frozen":
            rec["state"] = "frozen"
            slices[key] = cur
            continue
        # ── retired：复活观察通道（专属分支，处理完必 continue） ──
        if cur["state"] == "retired":
            rec["state"] = "retired"  # 单写手覆盖（每日三态不穿过退役层）
            death = cur.get("death") or {}
            new_n = float(rec.get("n_events") or 0) - float(death.get("n") or 0)
            if new_n >= RESURRECT_MIN_NEW_EVENTS:
                new_hits = (
                    float(rec.get("hit_rate") or 0) * float(rec.get("n_events") or 0)
                    - float(death.get("hit_rate") or 0) * float(death.get("n") or 0)
                )
                base = float(death.get("baseline", 0.5))
                q_threshold = (
                    RESURRECT_Q_FIRST if cur.get("resurrect_attempts", 0) == 0
                    else RESURRECT_Q_SECOND
                )
                if binomial_ge_pvalue_small(new_hits, new_n, base) < q_threshold:
                    cur["state"] = "resurrected"
                    cur["failed_streak"] = 0
                    cur["resurrect_attempts"] = cur.get("resurrect_attempts", 0) + 1
                    cur["resurrected_at"] = today
                    rec["state"] = "resurrected"
                    summary["resurrected"].append(key)
                    slices[key] = cur
                    continue
            # 增量不足/未达标：保持 retired（不猜）
            cur["post_death_windows"] = cur.get("post_death_windows", 0) + 1
            slices[key] = cur
            continue
        # ── 三态日更：failed 计连窗，其余归零 ──
        if state == "failed":
            cur["failed_streak"] = cur.get("failed_streak", 0) + 1
        else:
            cur["failed_streak"] = 0
            if cur["state"] != "resurrected":
                cur["state"] = state
        if cur["failed_streak"] >= RETIRED_AFTER and cur["state"] != "retired":
            if cur["state"] == "resurrected":
                cur["resurrect_failures"] = cur.get("resurrect_failures", 0) + 1
                if cur["resurrect_failures"] >= RESURRECT_MAX_ATTEMPTS:
                    cur["state"] = "frozen"
                    rec["state"] = "frozen"
                    summary["frozen"].append(key)
                    slices[key] = cur
                    continue
            cur["state"] = "retired"
            cur["retired_at"] = today
            cur["death"] = {
                "n": rec.get("n_events"), "hit_rate": rec.get("hit_rate"),
                "baseline": baseline_by_key.get(key, 0.5), "reason": "statistical",
            }
            rec["state"] = "retired"
            summary["retired"].append(key)
        slices[key] = cur
    store.save(slices)
    return summary
