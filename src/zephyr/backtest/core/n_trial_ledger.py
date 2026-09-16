# [BLUEPRINT] MOD-BT-200 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.n_trial_ledger
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.io.file_utils; zephyr.shared.io.paths
# [CONSUMERS] scripts/backtest/dsr_recalc_backfill.py（A3 存量重算）；批次 B 确认跑（DSR 折减分母）；c4_batch_screen 后续批（可选自查）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 计数边界=只算可审计的机器回测次数（裁定 2026-09-15：台账 is_sharpe 非空证据行
#   +run 档案/manifest 可复核批量）；
#   manual_population（人工历史试错）只入 known_floor 披露、永不入 count——不可审计的计数进判定=可伪造的门禁；
#   账本真源=YAML（RULE-SSOT：规则数据归 YAML），本模块=机器口径唯一写入口（CAS+YAML 预检+写后核读）；
#   批次幂等（同 batch_id 拒绝重复登记）；n_trials 必须>=0；数字口径读数缺失时 fail-closed（拒猜测）
# [MODIFY-GUARD] tests/backtest/test_n_trial_ledger.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TrialLedgerError(账本读写/口径失败；复用 ValueError 校验入参)
# [TESTS] tests/backtest/test_n_trial_ledger.py
# [A_module] module_id=MOD-BT-200 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_BACKTEST — N 试次账本（全局累计试验数计数器，DSR 多重测试修正的分母真源）。

背景（2026-09-15 DSR 修口径裁定，本模块=A1 交付）：
- 台账 DSR 长期冻结的三根因之一 = "N 未落账"：num_trials 长期=批内行数口径，
  solo run 零折减、批间 DSR 不可横比、事后无法审计任一行的 N。
- 计数边界已裁定：**只算可审计的机器回测次数**（strategy_screen 台账行 +
  run 档案/manifest 可复核批量）；人工历史试错登记为已知下界（known_floor），
  不入机器判定分母。
- N_eff 预注册（2026-09-15）：effective_rank 估计器随批次 B 落地，本账本预留
  n_trials_effective 披露位；当前只交付 n_trials_raw（累计原始口径）。

计数口径（count = screen_runs + batch_records）：
1. screen_runs —— c1_backtest.strategy_screen 中 is_sharpe 非空行数（每行=一次
   机器回测成绩的证据行；deferred_c4 挂起行/C2 粗筛未考行零 is_sharpe，不算试验）。
   由 sync_screen_counts 自动同步。
2. batch_records —— 台账外可审计批量的显式登记（如 F-06 批次 A 网格 manifest 的
   实评格点数 1999：manifest.csv 即出生证可复核）。auto_sync 可从
   data/strategy_intake/grid_*/summary.json 自动发现追加，亦可 record_run 手工登记。
3. manual_population —— 人工历史试错，仅入 known_floor 披露位，永不入 count。

Usage:
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    ledger = TrialLedger()
    n = ledger.cumulative_trials()      # 累计口径（缺账本/缺读数=抛错，fail-closed）
    snap = ledger.snapshot()            # 全量快照（breakdown/known_floor/as_of）
    out = ledger.sync_screen_counts()   # 自动同步台账读数+发现网格批次（幂等）
    ledger.record_run("manual", "BATCH-x", 12, note="...")  # 显式登记（幂等）
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from zephyr.shared.io.file_utils import safe_read, safe_write_text
from zephyr.shared.io.paths import REPO_ROOT

_logger = logging.getLogger(__name__)

LEDGER_REGISTRY_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry"
    / "catalogs" / "trial_ledger_registry.yaml"
)
_GRID_ROOT = REPO_ROOT / "data" / "strategy_intake"

REGISTRY_SKELETON: dict[str, Any] = {
    "schema_version": "1.0.0",
    "ttl": "permanent",
    "doc_type": "register",
    "title": "全局累计试验数账本（N 账本，MOD-BT-200）",
    "status": "active",
    "version": "0.1.0",
    "date": "2026-09-15",
    "owner": "ZephyrAlpha-Owner",
    "counting_rule": (
        "计数边界=可审计机器回测次数（2026-09-15 裁定）。"
        "count = screen_runs.total_trials + sum(batch_records.n_trials)。"
        "manual_population 只入 known_floor 披露，不入 count。"
    ),
    "manual_population": 0,
    "manual_note": "人工历史试错不可审计，仅 Owner 登记时累加；当前无登记=0（诚实缺省）",
    "sources": {
        "screen_table": "c1_backtest.strategy_screen",
        "batch_records": "显式登记的台账外可审计批量（batch_id 唯一，幂等）",
    },
    "screen_runs": {
        "total_trials": 0,
        "total_runs": 0,
        "last_synced_at": None,
        "last_synced_by": None,
    },
    "batch_records": [],
}


class TrialLedgerError(Exception):
    """N 账本读写/口径错误（账本缺失、读数缺失、CAS 写失败等），fail-closed。"""


def _now_iso() -> str:
    """显式时区时间戳（UTC，ISO8601）。"""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class TrialLedgerSnapshot:
    """账本快照——不可变。

    Attributes:
        ledger_runs: 已登记批次数（screen_runs.total_runs + len(batch_records)）
        ledger_trials: 可审计累计试验数（count 口径真源读数）
        manual_population: 人工历史已知下界（不入 count）
        known_floor: = ledger_trials + manual_population（诚实披露位）
        n_trials_raw: = ledger_trials（预注册双口径披露名）
        n_trials_effective: 预留位（effective_rank 随批次 B 落地，当前恒 None）
        breakdown: 按来源分解 {"screen_runs": x, "batch:<batch_id>": y}
        as_of: 快照时间（UTC ISO8601）
    """

    ledger_runs: int
    ledger_trials: int
    manual_population: int
    known_floor: int
    n_trials_raw: int
    n_trials_effective: int | None
    breakdown: dict[str, int] = field(default_factory=dict)
    as_of: str = ""


def compute_effective_rank(
    net_returns_by_id: dict[str, Any],
    min_T: int = 60,
) -> tuple[int, dict[str, Any]]:
    """effective_rank 估计器（N_eff 预注册 4.1 规格实现，锁定勿改）。

    步骤（预注册原文）:
      1. 批次内 N 条试验的日净收益序列按日期对齐，共同长度 < min_T → 不折减（返回 N，boundary）；
      2. 两两 Pearson 相关矩阵；
      3. 特征值分解，λ_k 负值截 0（数值半正定修正）；
      4. p_k = λ_k / Σλ；N_eff = ceil(exp(-Σ p_k·ln p_k))（熵加权特征值广度），
         clamp 到 [1, N]。

    Returns:
        (n_eff, meta)：meta 含 n_trials/boundary/共同长度，供双口径披露留痕。
    """
    import numpy as np
    import pandas as pd

    # 序列按 index 对齐（不同格点净收益天数不齐是常态——universe/窗口差异），
    # 外连接对齐后 dropna 取共同覆盖窗
    aligned = pd.concat({k: pd.Series(v) for k, v in net_returns_by_id.items()}, axis=1)
    df = aligned.dropna(how="any")
    n = df.shape[1]
    meta: dict[str, Any] = {"n_trials": n, "common_T": int(len(df)), "boundary": False}
    if n < 2:
        meta["boundary"] = True
        return max(n, 1), meta
    if len(df) < min_T:
        meta["boundary"] = True
        return n, meta
    corr = df.corr().fillna(0.0).to_numpy()
    eig = np.clip(np.linalg.eigvalsh(corr), 0.0, None)
    total = float(eig.sum())
    if total <= 0.0:
        return 1, meta
    probs = eig[eig > 0] / total
    # ceil 前按 1e-9 容差规整：完全相关时数值微噪会给出 1.0000000000000004，
    # 裸 ceil 会虚增到 2（浮点噪声≠真实有效试验数）
    entropy_breadth = round(float(np.exp(-(probs * np.log(probs)).sum())), 9)
    n_eff = int(np.ceil(entropy_breadth))
    return int(min(max(n_eff, 1), n)), meta


class TrialLedger:
    """N 试次账本——全局累计试验数计数器（真源=YAML 注册表，本类=唯一机器写入口）。

    Args:
        registry_path: 账本 YAML 路径（默认仓内真源；测试注入 tmp_path）。
    """

    def __init__(self, registry_path: Path | None = None) -> None:
        self._path = Path(registry_path) if registry_path else LEDGER_REGISTRY_PATH

    # ---------- 读 ----------

    def load_registry(self, *, create_if_missing: bool = False) -> dict[str, Any]:
        """读账本 YAML。缺失时按需落骨架（仅显式允许时），否则抛错（fail-closed）。"""
        if not self._path.exists():
            if create_if_missing:
                import yaml

                text = yaml.safe_dump(REGISTRY_SKELETON, allow_unicode=True, sort_keys=False)
                safe_write_text(self._path, text)
                _logger.info("N 账本骨架初始化: %s", self._path)
            else:
                raise TrialLedgerError(f"N 账本不存在: {self._path}")
        import yaml

        data = yaml.safe_load(safe_read(self._path))
        if not isinstance(data, dict) or "screen_runs" not in data:
            raise TrialLedgerError(f"N 账本结构非法（缺 screen_runs 段）: {self._path}")
        return data

    def cumulative_trials(self) -> int:
        """累计口径读数（count = screen_runs + batch_records）。账本缺失=抛错。"""
        data = self.load_registry()
        return self._count_of(data)

    @staticmethod
    def _count_of(data: dict[str, Any]) -> int:
        sr = data.get("screen_runs") or {}
        total = int(sr.get("total_trials") or 0)
        for rec in data.get("batch_records") or []:
            total += int(rec.get("n_trials") or 0)
        return total

    def snapshot(self) -> TrialLedgerSnapshot:
        """全量快照（含 breakdown / known_floor / 双口径披露位）。"""
        data = self.load_registry()
        sr = data.get("screen_runs") or {}
        breakdown: dict[str, int] = {"screen_runs": int(sr.get("total_trials") or 0)}
        for rec in data.get("batch_records") or []:
            key = f"batch:{rec.get('batch_id', '?')}"
            breakdown[key] = breakdown.get(key, 0) + int(rec.get("n_trials") or 0)
        trials = sum(breakdown.values())
        manual = int(data.get("manual_population") or 0)
        return TrialLedgerSnapshot(
            ledger_runs=int(sr.get("total_runs") or 0) + len(data.get("batch_records") or []),
            ledger_trials=trials,
            manual_population=manual,
            known_floor=trials + manual,
            n_trials_raw=trials,
            n_trials_effective=(data.get("n_trials_effective") or {}).get("value")
            if isinstance(data.get("n_trials_effective"), dict)
            else None,
            breakdown=breakdown,
            as_of=_now_iso(),
        )

    # ---------- 写（CAS+重试+写后核读，热文件纪律） ----------

    def _cas_update(self, mutate: Callable[[dict[str, Any]], str | None]) -> dict[str, Any]:
        """CAS 循环更新账本：mutate(data)->None 表示无需变更；返回最终 data。

        带退避重试（他会话并发写注册表常态），10 次失败抛 TrialLedgerError。
        """
        import hashlib

        import yaml

        last_exc: Exception | None = None
        for attempt in range(10):
            text = safe_read(self._path)
            base_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
            data = yaml.safe_load(text)
            note = mutate(data)
            if note is None:
                return data
            new_text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
            # YAML 预检（写前自证结构合法）
            reparsed = yaml.safe_load(new_text)
            if not isinstance(reparsed, dict) or "screen_runs" not in reparsed:
                raise TrialLedgerError("N 账本回读预检失败（结构非法），拒写")
            try:
                safe_write_text(self._path, new_text, expected_base_sha256=base_sha)
                # 写后进程外核实
                final = yaml.safe_load(safe_read(self._path))
                if final != reparsed:  # pragma: no cover - 并发窗口极窄，兜底
                    raise TrialLedgerError("N 账本写后核读不一致（并发覆盖），拒绝确认")
                return final
            except Exception as exc:  # noqa: BLE001 - CAS 冲突/文件锁 → 立即重试（次数上限，无 sleep——永久模块禁时间触发铁律）
                last_exc = exc
                _logger.warning("N 账本 CAS 写第 %d 次冲突: %s", attempt + 1, exc)
        raise TrialLedgerError(f"N 账本 CAS 写重试耗尽: {last_exc}") from last_exc

    # ---------- 显式登记 ----------

    def set_effective_trials(self, n_eff: int, note: str = "") -> dict[str, Any]:
        """写入 n_trials_effective 披露位（CAS；批次 B 双口径披露的账本侧落点）。

        覆盖语义：披露位=最新批次的 N_eff（非累加），note 记录来源批次与 meta。
        """

        def _mutate(data: dict[str, Any]) -> str | None:
            old = data.get("n_trials_effective")
            new_rec = {
                "value": int(n_eff),
                "estimator": "effective_rank",
                "note": note,
                "updated_at": _now_iso(),
                "previous": old if isinstance(old, dict) else None,
            }
            if isinstance(old, dict) and old.get("value") == new_rec["value"]:
                return None  # 同值幂等：无需变更
            data["n_trials_effective"] = new_rec
            return f"n_trials_effective -> {n_eff}"

        self._cas_update(_mutate)
        snap = self.snapshot()
        return {"n_eff": n_eff, "snapshot_n_raw": snap.n_trials_raw}

    def record_run(
        self,
        kind: str,
        batch_id: str,
        n_trials: int,
        *,
        note: str = "",
        recorded_by: str = "n_trial_ledger",
    ) -> dict[str, Any]:
        """显式登记一批台账外可审计批量（幂等：同 batch_id 存在则跳过返回现状）。

        Args:
            kind: 批次种类（如 manual / factory_grid_batch_a / oos_archive）
            batch_id: 批次唯一 id
            n_trials: 本批可审计试验数（>=0）
            note: 备注（审计凭据路径等）
            recorded_by: 登记者（会话名）
        """
        if not batch_id or not str(batch_id).strip():
            raise ValueError("batch_id 不能为空")
        n_trials = int(n_trials)
        if n_trials < 0:
            raise ValueError(f"n_trials 必须>=0: {n_trials}")
        if not kind or not str(kind).strip():
            raise ValueError("kind 不能为空")

        state = {"changed": False}

        def _mutate(data: dict[str, Any]) -> str | None:
            records: list[dict[str, Any]] = list(data.get("batch_records") or [])
            if any(str(r.get("batch_id")) == str(batch_id) for r in records):
                return None  # 幂等：已登记
            records.append({
                "batch_id": str(batch_id),
                "n_trials": n_trials,
                "kind": str(kind),
                "note": str(note),
                "recorded_at": _now_iso(),
                "recorded_by": str(recorded_by),
            })
            records.sort(key=lambda r: str(r.get("batch_id")))
            data["batch_records"] = records
            state["changed"] = True
            return f"record_run {batch_id} n={n_trials}"

        data = self._cas_update(_mutate)
        if not state["changed"]:
            return {"batch_id": batch_id, "n_trials": n_trials, "status": "exists"}
        total = self._count_of(data)
        return {"batch_id": batch_id, "n_trials": n_trials, "status": "recorded",
                "cumulative_trials": total}

    # ---------- 自动同步 ----------

    def sync_screen_counts(
        self,
        conn: Any | None = None,
        *,
        grid_root: Path | None = None,
        synced_by: str = "n_trial_ledger",
    ) -> dict[str, Any]:
        """自动同步台账读数 + 自动发现网格批次（幂等，可重复执行）。

        Args:
            conn: ClickHouse 连接（DatabaseService().get_clickhouse_conn()）；
                None=自动构造。测试注入假对象（需 execute(sql) -> rows）。
            grid_root: 网格产物根目录（默认 data/strategy_intake；测试注入 tmp_path）。
            synced_by: 同步者标识。

        Returns:
            {"screen_runs": x, "screen_batches": y, "grid_added": [batch_id...],
             "batch_total": z, "cumulative_trials": n}
        """
        if conn is None:
            from zephyr.infrastructure.database_service import DatabaseService

            conn = DatabaseService().get_clickhouse_conn()
        self.load_registry(create_if_missing=True)  # 引导入口：骨架缺失自动落盘
        rows = conn.execute(
            "SELECT run_id, count() FROM c1_backtest.strategy_screen "
            "WHERE is_sharpe IS NOT NULL GROUP BY run_id"
        )
        screen_trials = sum(int(r[1]) for r in rows)
        screen_batches = len(rows)

        # 自动发现网格批次（manifest=出生证，可复核 → 可审计）
        root = Path(grid_root) if grid_root else _GRID_ROOT
        discovered: list[dict[str, Any]] = []
        if root.exists():
            for summary_path in sorted(root.glob("grid_*/summary.json")):
                try:
                    import json

                    summary = json.loads(summary_path.read_text(encoding="utf-8"))
                except (OSError, ValueError) as exc:
                    _logger.warning("网格 summary 读取失败 %s: %s", summary_path, exc)
                    continue
                m = re.match(r"grid_(.+)$", summary_path.parent.name)
                if not m:
                    continue
                n = summary.get("evaluated")
                if n is None:
                    n = summary.get("n_sampled")
                if n is None:
                    continue
                discovered.append({
                    "batch_id": f"grid_{m.group(1)}",
                    "n_trials": int(n),
                    "kind": "factory_grid_batch_a",
                    "note": f"auto: {summary_path.relative_to(REPO_ROOT).as_posix()}",
                })

        state = {"added": []}

        def _mutate(data: dict[str, Any]) -> str | None:
            sr = data.setdefault("screen_runs", {})
            changed = (int(sr.get("total_trials") or 0) != screen_trials
                       or int(sr.get("total_runs") or 0) != screen_batches)
            sr["total_trials"] = screen_trials
            sr["total_runs"] = screen_batches
            sr["last_synced_at"] = _now_iso()
            sr["last_synced_by"] = str(synced_by)
            records: list[dict[str, Any]] = list(data.get("batch_records") or [])
            known = {str(r.get("batch_id")) for r in records}
            for disc in discovered:
                if str(disc["batch_id"]) in known:
                    continue
                rec = dict(disc)
                rec["recorded_at"] = _now_iso()
                rec["recorded_by"] = str(synced_by)
                records.append(rec)
                state["added"].append(str(disc["batch_id"]))
            records.sort(key=lambda r: str(r.get("batch_id")))
            data["batch_records"] = records
            return f"sync screen={screen_trials} grids+{len(state['added'])}" if (
                changed or state["added"]) else None

        data = self._cas_update(_mutate)
        return {
            "screen_runs": screen_trials,
            "screen_batches": screen_batches,
            "grid_added": state["added"],
            "batch_total": len(data.get("batch_records") or []),
            "cumulative_trials": self._count_of(data),
        }


__all__ = [
    "LEDGER_REGISTRY_PATH",
    "REGISTRY_SKELETON",
    "TrialLedger",
    "TrialLedgerError",
    "TrialLedgerSnapshot",
]
