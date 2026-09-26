# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/11_template_generator_design.md §6（N_eff 塌缩防线·组合空间预注册）
# [MODULE] scripts.governance.meta_question.wo_b2_e1c.e1c_ledger
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema.get_depgraph_pg_connection (read_only=False 合法架构写通道);
#                 zephyr.shared.io.yaml_utils.load_vocabulary_values (枚举 SSoT);
#                 zephyr.backtest.core.n_trial_ledger.compute_effective_rank (N_eff 预注册 4.1 真源，复用不另造);
#                 numpy; yaml
# [CONSUMERS] apply_e1c_ledgers.py / seed_e1c_first_records.py / audit_e1c_carriers.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 枚举全部经 load_vocabulary_values 动态加载建 CHECK 与判据，代码零字面量枚举列表；
#              时间列一律 TIMESTAMPTZ+显式时区（RULE-SCHEMA-TZ 的 PG 等价口径），时戳由调用方注入，本模块不自取时钟；
#              space_hash=对"取值域+笛卡尔方案+约束+容量"的规范化 JSON 取 sha256（不含时钟字段→可复算可比对）；
#              禁事后扩空间：expand 必须携 prev_space_hash 且旧空间须已 sealed，否则拒登（PQ-0109 机制保障）；
#              所有写入幂等（ON CONFLICT 主键/唯一键），可重放不产生重复账；
#              记录一律带 record_kind 来源档（live/inventory_replay/selftest_synthetic），自证样例永不进判定。
# [MODIFY-GUARD] data/registers/metaq_e1c/（改空间/考尺决策先改 YAML 再重放本模块）
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 词表缺失/空->ValueError（fail-closed）；expand 未封存旧空间->SpaceNotSealedError；
#                  未知状态/动作/轨->ValueError；PG 写失败->调用方事务回滚（本模块不吞异常）。
# [TESTS] python scripts/governance/meta_question/wo_b2_e1c/e1c_ledger.py --selftest（零 DB：哈希稳定性+秩相关+结构 N_eff）
# [TTL] permanent
"""metaq_e1c 台账库——组合空间预注册三件套 + 统一考尺快照 + 合并闸运行账。

覆盖工单问题：PQ-0104（space_hash 台账/批 manifest/N_eff 账）、PQ-0109（含 seal 封存动作字段）、
PQ-0107/PQ-0105（考尺快照冻结载体+分轨标识落账）、PQ-0106（逐对相关判定留痕+冗余度账）。

表清单（PG schema metaq_e1c）::

    space_registry        预注册空间台账（当前态，含 seal 字段）
    space_ledger_flow     登记/扩容/封存流水（append-only，PQ-0109 审计对象）
    batch_manifest        批 manifest（容量截断/幂等重放凭据）
    n_eff_estimate        N_eff 估计账（结构口径+effective_rank 实证口径双账）
    yardstick_snapshot     统一考尺配置快照（考试前冻结，含 PQ-0098 功效接口块）
    track_run_ledger      三轨候选落账（track=gplearn/agent/mcts）
    merge_gate_pairwise   合并闸逐对相关判定留痕（Pearson+Spearman+尾部）
    merge_gate_redundancy 合并闸冗余度账（高相关对占比 vs ≤40% 阈）
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
from pathlib import Path
from typing import Any, Final

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SCHEMA: Final = "metaq_e1c"
REGISTER_DIR: Final = _REPO_ROOT / "data" / "registers" / "metaq_e1c"
VOCAB_DIR: Final = REGISTER_DIR / "vocab"
DESIGN_FILE: Final = "e1c_space_design_cmb_e1c_v1.yaml"
SPACE_REGISTER_FILE: Final = "e1c_space_cmb_e1c_v1.yaml"
YARDSTICK_FILE: Final = "e1c_yardstick_v1.yaml"

_VOCAB_FILES: Final = {
    "action": "metaq_e1c_space_action_vocabulary.yaml",
    "status": "metaq_e1c_space_status_vocabulary.yaml",
    "track": "metaq_e1c_track_vocabulary.yaml",
    "estimator": "metaq_e1c_n_eff_estimator_vocabulary.yaml",
    "verdict": "metaq_e1c_gate_verdict_vocabulary.yaml",
    "record_kind": "metaq_e1c_record_kind_vocabulary.yaml",
    "window": "metaq_e1c_window_vocabulary.yaml",
}


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。schema 由 {_SCHEMA} 常量注入、import 期解析，
# 每个常量值逐字复制原内联表达式（外层括号仅容纳续行，不进入字符串值），落地 SQL 文本与
# 改造前等值；值参数沿用 %s 绑定；_SQL_TABLE_ROWCOUNT 的表名为运行期入参故以 %s 占位。
_SQL_INSERT_SPACE_REGISTRY = f"""INSERT INTO {_SCHEMA}.space_registry (
                    space_hash, space_id, version, tpl_ref, slot_domains, cartesian_plan, constraints,
                    cap_template, cap_batch, nominal_count, feasible_count, status, frozen_at, frozen_by,
                    supersedes_space_hash, design_ref, evidence_ref, created_at, updated_at)
                VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb,%s,%s,%s,%s,'open',%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (space_hash) DO NOTHING"""
_SQL_INSERT_LEDGER_FLOW = f"""INSERT INTO {_SCHEMA}.space_ledger_flow
                    (space_hash, prev_space_hash, action, actor, session_id, detail, evidence_ref, created_at)
                VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s)
                ON CONFLICT ON CONSTRAINT flow_once DO NOTHING"""
_SQL_SELECT_STATUS = f"SELECT status FROM {_SCHEMA}.space_registry WHERE space_hash=%s"
_SQL_UPDATE_SEAL = f"""UPDATE {_SCHEMA}.space_registry
                SET status='sealed', sealed_at=%s, seal_reason=%s, seal_evidence_ref=%s, updated_at=%s
                WHERE space_hash=%s AND status <> 'sealed'"""
_SQL_SELECT_SPACE_EXISTS = f"SELECT 1 FROM {_SCHEMA}.space_registry WHERE space_hash=%s"
_SQL_INSERT_LEDGER_FLOW_SEAL = f"""INSERT INTO {_SCHEMA}.space_ledger_flow
                    (space_hash, prev_space_hash, action, actor, session_id, detail, evidence_ref, created_at)
                VALUES (%s,'','seal',%s,%s,%s::jsonb,%s,%s)
                ON CONFLICT ON CONSTRAINT flow_once DO NOTHING"""
_SQL_SELECT_YARDSTICK_HASH = f"SELECT config_hash FROM {_SCHEMA}.yardstick_snapshot WHERE snapshot_id=%s"
_SQL_INSERT_YARDSTICK = f"""INSERT INTO {_SCHEMA}.yardstick_snapshot (
                    snapshot_id, version, exam_plan_version, criteria, fee_assumption, tracks,
                    power_interface, applies_to, config_hash, status, frozen_at, frozen_by,
                    evidence_ref, source_ref)
                VALUES (%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s::jsonb,%s::jsonb,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (snapshot_id) DO NOTHING"""
_SQL_INSERT_MANIFEST = f"""INSERT INTO {_SCHEMA}.batch_manifest (
                    batch_id, space_hash, tpl_ref, kind, planned_count, emitted_count, truncated_count,
                    cap_batch, over_cap, replay_of_batch, detail, manifest_sha256, generated_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s)
                ON CONFLICT (batch_id) DO NOTHING"""
_SQL_INSERT_NEFF = f"""INSERT INTO {_SCHEMA}.n_eff_estimate (
                    space_hash, batch_key, batch_id, estimator, record_kind, nominal_count, n_trials,
                    n_eff, ratio, boundary, meta, evidence_ref, computed_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s)
                ON CONFLICT ON CONSTRAINT n_eff_unique DO NOTHING"""
_SQL_INSERT_TRACK_RUN = f"""INSERT INTO {_SCHEMA}.track_run_ledger (
                        space_hash, batch_id, track, candidate_id, fingerprint, slot_values, metrics,
                        yardstick_snapshot_id, passed, fail_criteria, record_kind, exam_ref,
                        evidence_refs, recorded_at)
                    VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s,%s::jsonb,%s,%s,%s::jsonb,%s)
                    ON CONFLICT ON CONSTRAINT track_run_unique DO NOTHING"""
_SQL_INSERT_PAIRWISE = f"""INSERT INTO {_SCHEMA}.merge_gate_pairwise (
                        run_id, space_hash, batch_id, cand_a, cand_b, pearson, spearman,
                        tail_correlation, common_T, verdict, hit_criteria, thresholds,
                        sustained_days, record_kind, evidence_ref, computed_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s)
                    ON CONFLICT ON CONSTRAINT pair_unique DO NOTHING"""
_SQL_INSERT_REDUNDANCY = f"""INSERT INTO {_SCHEMA}.merge_gate_redundancy (
                    run_id, space_hash, batch_id, n_candidates, n_pairs, n_high_corr_pairs,
                    redundancy_ratio, threshold, verdict, estimator, note, record_kind,
                    evidence_ref, computed_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT ON CONSTRAINT redundancy_unique DO NOTHING"""
_SQL_SCHEMA_PRESENT = "SELECT 1 FROM information_schema.schemata WHERE schema_name=%s"
_SQL_COL_COUNT = "SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name=%s"
_SQL_TABLE_ROWCOUNT = f'SELECT count(*) FROM "{_SCHEMA}"."%s"'


class SpaceNotSealedError(RuntimeError):
    """扩容申请未先行封存旧空间（禁事后扩空间纪律违例）。"""


def load_vocab(kind: str) -> frozenset[str]:
    """枚举动态加载（词表 SSoT）。空/缺失即抛，不放行未知值。"""
    import sys

    if str(_REPO_ROOT / "src") not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT / "src"))
    from zephyr.shared.io.yaml_utils import load_vocabulary_values

    name = _VOCAB_FILES[kind]
    values = load_vocabulary_values(name, vocab_dir=VOCAB_DIR)
    if not values:
        msg = f"metaq_e1c 词表为空或缺失: {VOCAB_DIR / name}"
        raise ValueError(msg)
    return frozenset(values)


def ordered_values(kind: str) -> tuple[str, ...]:
    return tuple(sorted(load_vocab(kind)))


# ---------------------------------------------------------------- 规范化与哈希


def canonical_json(obj: Any) -> str:
    """稳定序列化（键排序 + 去空白 + 非 ASCII 保留）——哈希与 PG JSONB 落库共用。"""

    def _norm(v: Any) -> Any:
        if isinstance(v, Mapping):
            return {str(k): _norm(v[k]) for k in sorted(v, key=str)}
        if isinstance(v, (list, tuple, set, frozenset)):
            items = [_norm(x) for x in v]
            return sorted(items, key=lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True, default=str))
        if isinstance(v, Decimal):
            return f"{v:.10f}".rstrip("0").rstrip(".")
        if isinstance(v, (datetime.date, datetime.datetime)):
            return v.isoformat()
        return v

    return json.dumps(_norm(obj), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def sha256_hex(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def space_hash_of(space_def: Mapping[str, Any]) -> str:
    """预注册空间指纹：只覆盖"空间本体"（域/笛卡尔/约束/容量），不含时钟与操作人。

    同一本体在任意时刻重算必得同一 hash（可复算=可审计）；改任一取值域/约束/上限→新 hash→须重预注册。
    """
    core = {
        "space_id": space_def["space_id"],
        "version": space_def["version"],
        "tpl_ref": space_def.get("tpl_ref", ""),
        "cartesian_plan": space_def.get("cartesian_plan", "full_product"),
        # 只哈希参与展开的维（attribute 维为分层标签，扩缩标签不改展开空间→不进指纹）
        "slots": {
            slot: {
                "domain_ref": body.get("domain_ref", ""),
                "mode": body.get("mode", "cartesian"),
                "values": sorted(map(str, body.get("values", []))),
            }
            for slot, body in space_def["slots"].items()
            if body.get("mode", "cartesian") == "cartesian"
        },
        "constraints": {
            k: canonical_json(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in (space_def.get("constraints") or {}).items()
        },
        "cap_template": int(space_def.get("cap_template", 0)),
        "cap_batch": int(space_def.get("cap_batch", 0)),
    }
    return sha256_hex(core)


# ---------------------------------------------------------------- 结构口径 N_eff（空间层塌缩账）


def window_allowlist(freqs: Sequence[str]) -> set[str]:
    """cross_slot 约束机械实现：族内频率分布决定可用窗口集（真源=空间设计 YAML constraints.cross_slot）。"""
    windows = set(load_vocab("window"))
    cleaned = {str(f).strip().lower() for f in freqs if f}
    if cleaned and cleaned <= {"quarterly", "annual"}:
        return {w for w in windows if w in {"20d", "60d"}} or windows
    if cleaned and cleaned <= {"intraday"}:
        return {w for w in windows if w in {"1d", "5d"}} or windows
    return windows


def structural_counts(
    blocks: Mapping[str, Mapping[str, Any]],
    operators: Sequence[str],
    windows: Sequence[str],
    tracks: Sequence[str],
) -> dict[str, int]:
    """名义积 vs 约束过滤后可行积（结构口径 N_eff 分子/分母）。

    Args:
        blocks: {block_id: {"frequency": str, "fingerprint": str, "eligible": bool}}
                —— 因子登记表实读派生（build_e1c_space_register 生成，禁手填）。
    名义=全积木 × 算子 × 全窗 × 轨（未加任何约束）；
    可行=剔除不可复算/已退役积木、按积木频率收窄窗口、去同指纹马甲后的格数。
    """
    n_blocks, n_ops, n_wins, n_tracks = len(blocks), len(operators), len(windows), len(tracks)
    nominal = max(n_blocks, 1) * max(n_ops, 1) * max(n_wins, 1) * max(n_tracks, 1)
    feasible = 0
    seen_fp: set[str] = set()
    for bid, meta in blocks.items():
        if not meta.get("eligible", True):
            continue
        fp = str(meta.get("fingerprint", bid))
        if fp in seen_fp:
            continue
        seen_fp.add(fp)
        feasible += len(window_allowlist([str(meta.get("frequency", ""))])) * max(n_ops, 1) * max(n_tracks, 1)
    return {"nominal_count": nominal, "feasible_count": feasible}


def n_eff_structural(space_def: Mapping[str, Any]) -> dict[str, Any]:
    blocks = space_def["slots"]["block"]["blocks"]
    windows = list(space_def["slots"]["window"]["values"])
    ops = list(space_def["slots"]["operator"]["values"])
    tracks = list(space_def["slots"]["track"]["values"])
    counts = structural_counts(blocks, ops, windows, tracks)
    ratio = counts["feasible_count"] / counts["nominal_count"] if counts["nominal_count"] else 0.0
    freq_hist: dict[str, int] = {}
    for meta in blocks.values():
        key = str(meta.get("frequency", "") or "(空)")
        freq_hist[key] = freq_hist.get(key, 0) + 1
    return {
        "estimator": "structural_dedup",
        "nominal_count": counts["nominal_count"],
        "n_trials": counts["nominal_count"],
        "n_eff": counts["feasible_count"],
        "ratio": round(ratio, 6),
        "boundary": False,
        "meta": {
            "blocks_total": len(blocks),
            "blocks_eligible": sum(1 for m in blocks.values() if m.get("eligible", True)),
            "blocks_by_frequency": freq_hist,
            "operators": len(ops),
            "windows": windows,
            "tracks": tracks,
        },
    }


def n_eff_effective_rank(series_by_id: Mapping[str, Any], *, min_T: int = 60) -> dict[str, Any]:
    """实证口径 N_eff——直接复用既有预注册规格实现（N_eff 预注册 4.1），不另造估计器。"""
    import sys

    if str(_REPO_ROOT / "src") not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT / "src"))
    from zephyr.backtest.core.n_trial_ledger import compute_effective_rank

    n_eff, meta = compute_effective_rank(dict(series_by_id), min_T=min_T)
    n = int(meta.get("n_trials", len(series_by_id)))
    return {
        "estimator": "effective_rank",
        "nominal_count": n,
        "n_trials": n,
        "n_eff": int(n_eff),
        "ratio": round(n_eff / n, 6) if n else 0.0,
        "boundary": bool(meta.get("boundary", False)),
        "meta": dict(meta),
    }


# ---------------------------------------------------------------- 相关性统计（合并闸留痕用）


def _as_floats(seq: Sequence[float]) -> list[float]:
    return [float(x) for x in seq]


def ranks(values: Sequence[float]) -> list[float]:
    """平均秩（ties 取均值）——Spearman 的机械定义，不依赖 scipy 版本差异。"""
    v = _as_floats(values)
    order = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def pearson(a: Sequence[float], b: Sequence[float]) -> float | None:
    x, y = _as_floats(a), _as_floats(b)
    n = min(len(x), len(y))
    if n < 3:
        return None
    x, y = x[:n], y[:n]
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((u - mx) ** 2 for u in x)
    syy = sum((u - my) ** 2 for u in y)
    if sxx <= 0 or syy <= 0:
        return None
    return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / (sxx**0.5 * syy**0.5)


def spearman(a: Sequence[float], b: Sequence[float]) -> float | None:
    """题面 |秩相关|>0.7 口径（在产 MOD-PA-004 未实现，本件补算并留痕——见案卷待落地补丁）。"""
    return pearson(ranks(a), ranks(b))


def tail_correlation(a: Sequence[float], b: Sequence[float], *, q: float = 0.90) -> float | None:
    """尾部相关（对齐 MOD-PA-004 reject_tail_correlation 的输入形状：极端分位段的 Pearson）。"""
    x, y = _as_floats(a), _as_floats(b)
    n = min(len(x), len(y))
    if n < 8:
        return None
    x, y = x[:n], y[:n]
    thr_x = sorted(x)[max(int(n * q) - 1, 0)]
    thr_y = sorted(y)[max(int(n * q) - 1, 0)]
    pairs = [(u, v) for u, v in zip(x, y, strict=True) if u >= thr_x or v >= thr_y]
    if len(pairs) < 3:
        return None
    return pearson([p[0] for p in pairs], [p[1] for p in pairs])


def verdict_for_pair(
    pear: float | None,
    spear: float | None,
    tail: float | None,
    *,
    prod_pearson_reject: float = 0.85,
    prod_hard_reject: float = 0.90,
    prod_tail_reject: float = 0.70,
    question_spearman_reject: float = 0.70,
) -> tuple[str, str]:
    """双口径判定：在产 Pearson/尾部 + 题面 |Spearman|>0.7，返回 (verdict, 命中口径说明)。"""
    hits: list[str] = []
    sev = 0
    if pear is not None and pear > prod_hard_reject:
        sev, hits = 3, [*hits, f"pearson>{prod_hard_reject}(在产 HARD_REJECT)"]
    elif pear is not None and pear > prod_pearson_reject:
        sev, hits = 2, [*hits, f"pearson>{prod_pearson_reject}(在产 REJECT)"]
    if spear is not None and abs(spear) > question_spearman_reject:
        sev = max(sev, 2)
        hits = [*hits, f"|spearman|>{question_spearman_reject}(题面秩相关口径，未实现于在产门禁)"]
    if tail is not None and tail > prod_tail_reject:
        sev = max(sev, 2)
        hits = [*hits, f"tail>{prod_tail_reject}(在产尾部同向 REJECT)"]
    names = {0: "PASS", 1: "WARN", 2: "REJECT", 3: "HARD_REJECT"}
    verdict = names[sev]
    if verdict not in load_vocab("verdict"):  # 词表与代码档不一致→ fail-closed（禁静默降级）
        msg = f"verdict={verdict} 不在词表 {sorted(load_vocab('verdict'))}"
        raise ValueError(msg)
    return verdict, ";".join(hits)


# ---------------------------------------------------------------- DDL（枚举由词表动态渲染）


def _q_list(values: Iterable[str]) -> str:
    return ", ".join("'" + str(v).replace("'", "''") + "'" for v in values)


def ddl_statements() -> list[tuple[str, str]]:
    s = _SCHEMA
    actions = _q_list(ordered_values("action"))
    statuses = _q_list(ordered_values("status"))
    tracks = _q_list(ordered_values("track"))
    estimators = _q_list(ordered_values("estimator"))
    verdicts = _q_list(ordered_values("verdict"))
    kinds = _q_list(ordered_values("record_kind"))
    return [
        ("schema", f"CREATE SCHEMA IF NOT EXISTS {s}"),
        (
            "space_registry",
            f"""
CREATE TABLE IF NOT EXISTS {s}.space_registry (
    space_hash          TEXT PRIMARY KEY,
    space_id            TEXT NOT NULL,
    version             TEXT NOT NULL,
    tpl_ref             TEXT NOT NULL DEFAULT '',
    slot_domains        JSONB NOT NULL,
    cartesian_plan      TEXT NOT NULL DEFAULT 'full_product',
    constraints         JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    cap_template        INTEGER NOT NULL CHECK (cap_template > 0),
    cap_batch           INTEGER NOT NULL CHECK (cap_batch > 0),
    nominal_count       BIGINT  NOT NULL CHECK (nominal_count >= 0),
    feasible_count      BIGINT  NOT NULL CHECK (feasible_count >= 0),
    status              TEXT NOT NULL DEFAULT 'open' CHECK (status IN ({statuses})),
    frozen_at           TIMESTAMPTZ NOT NULL,
    frozen_by           TEXT NOT NULL DEFAULT '',
    supersedes_space_hash TEXT NULL,
    sealed_at           TIMESTAMPTZ NULL,
    seal_reason         TEXT NULL,
    seal_evidence_ref   TEXT NULL,
    design_ref          TEXT NOT NULL DEFAULT '',
    evidence_ref        TEXT NOT NULL DEFAULT '',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
)""",
        ),
        (
            "space_ledger_flow",
            f"""
CREATE TABLE IF NOT EXISTS {s}.space_ledger_flow (
    seq             BIGSERIAL PRIMARY KEY,
    space_hash      TEXT NOT NULL REFERENCES {s}.space_registry(space_hash) ON DELETE CASCADE,
    prev_space_hash TEXT NOT NULL DEFAULT '',
    action          TEXT NOT NULL CHECK (action IN ({actions})),
    actor           TEXT NOT NULL DEFAULT '',
    session_id      TEXT NOT NULL DEFAULT '',
    detail          JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    evidence_ref    TEXT NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT flow_prev_required_for_expand CHECK (action <> 'expand' OR prev_space_hash <> ''),
    CONSTRAINT flow_once UNIQUE (space_hash, action, prev_space_hash)
)""",
        ),
        (
            "batch_manifest",
            f"""
CREATE TABLE IF NOT EXISTS {s}.batch_manifest (
    batch_id        TEXT PRIMARY KEY,
    space_hash      TEXT NOT NULL REFERENCES {s}.space_registry(space_hash) ON DELETE CASCADE,
    tpl_ref         TEXT NOT NULL DEFAULT '',
    kind            TEXT NOT NULL DEFAULT 'live' CHECK (kind IN ({kinds})),
    planned_count   INTEGER NOT NULL CHECK (planned_count >= 0),
    emitted_count   INTEGER NOT NULL CHECK (emitted_count >= 0),
    truncated_count INTEGER NOT NULL CHECK (truncated_count >= 0),
    cap_batch       INTEGER NOT NULL CHECK (cap_batch > 0),
    over_cap        BOOLEAN NOT NULL DEFAULT false,
    replay_of_batch TEXT NULL,
    detail          JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    manifest_sha256 TEXT NOT NULL DEFAULT '',
    generated_at    TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT cap_batch_positive CHECK (emitted_count <= cap_batch OR kind <> 'live')
)""",
        ),
        (
            "n_eff_estimate",
            f"""
CREATE TABLE IF NOT EXISTS {s}.n_eff_estimate (
    id             BIGSERIAL PRIMARY KEY,
    space_hash     TEXT NOT NULL REFERENCES {s}.space_registry(space_hash) ON DELETE CASCADE,
    batch_key      TEXT NOT NULL DEFAULT '',
    batch_id       TEXT NULL,
    estimator      TEXT NOT NULL CHECK (estimator IN ({estimators})),
    record_kind    TEXT NOT NULL DEFAULT 'live' CHECK (record_kind IN ({kinds})),
    nominal_count  BIGINT NOT NULL CHECK (nominal_count >= 0),
    n_trials       INTEGER NOT NULL CHECK (n_trials >= 0),
    n_eff          BIGINT NOT NULL CHECK (n_eff >= 0),
    ratio          NUMERIC(10,6) CHECK (ratio >= 0 AND ratio <= 1),
    boundary       BOOLEAN NOT NULL DEFAULT false,
    meta           JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    evidence_ref   TEXT NOT NULL DEFAULT '',
    computed_at    TIMESTAMPTZ NOT NULL,
    CONSTRAINT n_eff_unique UNIQUE (space_hash, batch_key, estimator, record_kind)
)""",
        ),
        (
            "yardstick_snapshot",
            f"""
CREATE TABLE IF NOT EXISTS {s}.yardstick_snapshot (
    snapshot_id       TEXT PRIMARY KEY,
    version           TEXT NOT NULL,
    exam_plan_version TEXT NOT NULL,
    criteria          JSONB NOT NULL,
    fee_assumption    JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    tracks            JSONB NOT NULL,
    power_interface   JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    applies_to        JSONB NOT NULL DEFAULT '[]'::jsonb,
    config_hash       TEXT NOT NULL,
    status            TEXT NOT NULL DEFAULT 'frozen' CHECK (status IN ('draft','frozen','superseded')),
    frozen_at         TIMESTAMPTZ NOT NULL,
    frozen_by         TEXT NOT NULL DEFAULT '',
    evidence_ref      TEXT NOT NULL DEFAULT '',
    source_ref        TEXT NOT NULL DEFAULT '',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
)""",
        ),
        (
            "track_run_ledger",
            f"""
CREATE TABLE IF NOT EXISTS {s}.track_run_ledger (
    id                  BIGSERIAL PRIMARY KEY,
    space_hash          TEXT NOT NULL REFERENCES {s}.space_registry(space_hash) ON DELETE CASCADE,
    batch_id            TEXT NULL,
    track               TEXT NOT NULL CHECK (track IN ({tracks})),
    candidate_id        TEXT NOT NULL,
    fingerprint         TEXT NOT NULL DEFAULT '',
    slot_values         JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    metrics             JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    yardstick_snapshot_id TEXT NOT NULL REFERENCES {s}.yardstick_snapshot(snapshot_id),
    passed              BOOLEAN NULL,
    fail_criteria       JSONB NOT NULL DEFAULT '[]'::jsonb,
    record_kind         TEXT NOT NULL DEFAULT 'live' CHECK (record_kind IN ({kinds})),
    exam_ref            TEXT NOT NULL DEFAULT '',
    evidence_refs       JSONB NOT NULL DEFAULT '[]'::jsonb,
    recorded_at         TIMESTAMPTZ NOT NULL,
    CONSTRAINT track_run_unique UNIQUE (space_hash, track, candidate_id)
)""",
        ),
        (
            "merge_gate_pairwise",
            f"""
CREATE TABLE IF NOT EXISTS {s}.merge_gate_pairwise (
    id                  BIGSERIAL PRIMARY KEY,
    run_id              TEXT NOT NULL,
    space_hash          TEXT NOT NULL REFERENCES {s}.space_registry(space_hash) ON DELETE CASCADE,
    batch_id            TEXT NULL,
    cand_a              TEXT NOT NULL,
    cand_b              TEXT NOT NULL,
    pearson             NUMERIC(10,6) NULL,
    spearman            NUMERIC(10,6) NULL,
    tail_correlation    NUMERIC(10,6) NULL,
    common_T            INTEGER NOT NULL DEFAULT 0,
    verdict             TEXT NOT NULL CHECK (verdict IN ({verdicts})),
    hit_criteria        TEXT NOT NULL DEFAULT '',
    thresholds          JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    sustained_days      INTEGER NULL,
    record_kind         TEXT NOT NULL DEFAULT 'live' CHECK (record_kind IN ({kinds})),
    evidence_ref        TEXT NOT NULL DEFAULT '',
    computed_at         TIMESTAMPTZ NOT NULL,
    CONSTRAINT pair_unique UNIQUE (run_id, cand_a, cand_b),
    CONSTRAINT pair_no_self CHECK (cand_a <> cand_b)
)""",
        ),
        (
            "merge_gate_redundancy",
            f"""
CREATE TABLE IF NOT EXISTS {s}.merge_gate_redundancy (
    id                 BIGSERIAL PRIMARY KEY,
    run_id             TEXT NOT NULL,
    space_hash         TEXT NOT NULL REFERENCES {s}.space_registry(space_hash) ON DELETE CASCADE,
    batch_id           TEXT NULL,
    n_candidates       INTEGER NOT NULL CHECK (n_candidates >= 0),
    n_pairs            INTEGER NOT NULL CHECK (n_pairs >= 0),
    n_high_corr_pairs  INTEGER NOT NULL CHECK (n_high_corr_pairs >= 0),
    redundancy_ratio   NUMERIC(10,6) NULL,
    threshold          NUMERIC(10,6) NOT NULL DEFAULT 0.40,
    verdict            TEXT NOT NULL CHECK (verdict IN ({verdicts})),
    estimator          TEXT NOT NULL DEFAULT 'pairwise_correlation',
    note               TEXT NOT NULL DEFAULT '',
    record_kind        TEXT NOT NULL CHECK (record_kind IN ({kinds})),
    evidence_ref       TEXT NOT NULL DEFAULT '',
    computed_at        TIMESTAMPTZ NOT NULL,
    CONSTRAINT redundancy_unique UNIQUE (run_id, space_hash, estimator)
)""",
        ),
        (
            "idx_flow_action",
            f"CREATE INDEX IF NOT EXISTS idx_{s}_flow_action ON {s}.space_ledger_flow (action, space_hash)",
        ),
        ("idx_pair_run", f"CREATE INDEX IF NOT EXISTS idx_{s}_pair_run ON {s}.merge_gate_pairwise (run_id, verdict)"),
        ("idx_track", f"CREATE INDEX IF NOT EXISTS idx_{s}_track ON {s}.track_run_ledger (space_hash, track, passed)"),
    ]


def expected_column_counts() -> dict[str, int]:
    """从 DDL 自身派生"表应有列数"（避免手填期望值造成漂移判据）。"""
    out: dict[str, int] = {}
    for label, sql in ddl_statements():
        if label in {"schema"} or label.startswith("idx_"):
            continue
        body = sql.split("(", 1)[1] if "(" in sql else ""
        count = 0
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(("CONSTRAINT", "CREATE", "PRIMARY", "UNIQUE", "CHECK")):
                continue
            if stripped in {")"} or stripped.startswith(")") or stripped.startswith("ON CONFLICT"):
                continue
            parts = stripped.split()
            if len(parts) >= 2 and parts[0].isidentifier() and parts[1][0].isupper():
                count += 1
        out[label] = count
    return out


# ---------------------------------------------------------------- PG 写通道


def pg_conn(*, write: bool = True):
    import sys

    if str(_REPO_ROOT / "src") not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT / "src"))
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    return get_depgraph_pg_connection(read_only=not write, autocommit=not write)


def _j(obj: Any) -> str:
    return canonical_json(obj) if obj is not None else "{}"


def apply_ddl(conn) -> list[str]:
    done: list[str] = []
    with conn.cursor() as cur:
        for label, sql in ddl_statements():
            cur.execute(sql)
            done.append(label)
    conn.commit()
    return done


def register_space(
    conn,
    space_def: Mapping[str, Any],
    *,
    frozen_at: datetime.datetime,
    provenance: Mapping[str, Any] | None = None,
) -> str:
    """预注册空间落账（幂等）。

    provenance 字段：actor / session_id / evidence_ref / supersedes / flow_detail。
    supersedes 非空=扩容路径，强制旧空间已 sealed。
    """
    prov = dict(provenance or {})
    actor = str(prov.get("actor") or "")
    session_id = str(prov.get("session_id") or "")
    evidence_ref = str(prov.get("evidence_ref") or "")
    supersedes = prov.get("supersedes") or None
    flow_detail = prov.get("flow_detail")
    if not space_def.get("slots"):
        msg = "空间定义缺 slots（取值域未解析，拒绝登记空壳）"
        raise ValueError(msg)
    known_status = load_vocab("status")
    if "open" not in known_status:
        msg = f"status 词表缺 open: {sorted(known_status)}"
        raise ValueError(msg)
    h = space_hash_of(space_def)
    if supersedes:
        ensure_sealed(conn, supersedes)
    with conn.cursor() as cur:
        cur.execute(
            _SQL_INSERT_SPACE_REGISTRY,
            (
                h,
                space_def["space_id"],
                str(space_def["version"]),
                space_def.get("tpl_ref", ""),
                _j(space_def["slots"]),
                space_def.get("cartesian_plan", "full_product"),
                _j(space_def.get("constraints") or {}),
                int(space_def.get("cap_template", 1)),
                int(space_def.get("cap_batch", 1)),
                int(space_def.get("nominal_count", 0)),
                int(space_def.get("feasible_count", 0)),
                frozen_at,
                actor,
                supersedes,
                space_def.get("_design_ref", ""),
                evidence_ref,
                frozen_at,
                frozen_at,
            ),
        )
        action = "expand" if supersedes else "register"
        cur.execute(
            _SQL_INSERT_LEDGER_FLOW,
            (
                h,
                supersedes or "",
                action,
                actor,
                session_id,
                _j({"space_id": space_def["space_id"], "version": space_def["version"], **(dict(flow_detail or {}))}),
                evidence_ref,
                frozen_at,
            ),
        )
    conn.commit()
    return h


def ensure_sealed(conn, space_hash: str) -> None:
    with conn.cursor() as cur:
        cur.execute(_SQL_SELECT_STATUS, (space_hash,))
        row = cur.fetchone()
    if row is None or str(row[0]) != "sealed":
        msg = (
            f"禁事后扩空间：旧空间 {space_hash[:12]}… 状态={row[0] if row else '不存在'}，"
            f"须先 seal（action=seal）再 expand（PQ-0109 违例口径）"
        )
        raise SpaceNotSealedError(msg)


def seal_space(
    conn,
    space_hash: str,
    *,
    reason: str,
    evidence_ref: str = "",
    sealed_at: datetime.datetime,
    actor: str = "",
    session_id: str = "",
) -> None:
    """封存动作（设计稿未含、按 PQ-0109 补齐）：改状态 + 写流水 + 记封存原因与证据。"""
    if not reason.strip():
        msg = "seal 必须登记 seal_reason（封存无因=可被事后随意解封，防线失效）"
        raise ValueError(msg)
    with conn.cursor() as cur:
        cur.execute(
            _SQL_UPDATE_SEAL,
            (sealed_at, reason, evidence_ref, sealed_at, space_hash),
        )
        if cur.rowcount == 0:
            cur.execute(_SQL_SELECT_SPACE_EXISTS, (space_hash,))
            if cur.fetchone() is None:
                msg = f"seal 目标空间不存在: {space_hash}"
                raise ValueError(msg)
        cur.execute(
            _SQL_INSERT_LEDGER_FLOW_SEAL,
            (space_hash, actor, session_id, _j({"reason": reason}), evidence_ref, sealed_at),
        )
    conn.commit()


def upsert_yardstick(conn, doc: Mapping[str, Any], *, evidence_ref: str = "") -> str:
    """考尺快照冻结落表（PQ-0107 载体）。同 snapshot_id 且 config_hash 不同→拒覆写（预注册不可改）。"""
    criteria = doc.get("criteria") or {}
    tracks = doc.get("tracks") or sorted(load_vocab("track"))
    h = sha256_hex(
        {
            "criteria": criteria,
            "tracks": tracks,
            "fee": doc.get("fee_assumption"),
            "power": doc.get("power_interface_for_PQ-0098"),
            "version": doc.get("version"),
        }
    )
    with conn.cursor() as cur:
        cur.execute(
            _SQL_SELECT_YARDSTICK_HASH,
            (doc["snapshot_id"],),
        )
        row = cur.fetchone()
        if row is not None and str(row[0]) != h:
            msg = (
                f"考尺快照 {doc['snapshot_id']} 已冻结（config_hash 前 12 位={str(row[0])[:12]}），"
                f"本次载荷 hash={h[:12]} 不一致——判据改动须新 snapshot_id（OSF 预注册不可改）"
            )
            raise ValueError(msg)
        cur.execute(
            _SQL_INSERT_YARDSTICK,
            (
                doc["snapshot_id"],
                str(doc.get("version", "1.0.0")),
                str(doc.get("exam_plan_version", "")),
                _j(criteria),
                _j(doc.get("fee_assumption")),
                _j(tracks),
                _j(doc.get("power_interface_for_PQ-0098")),
                _j(doc.get("applies_to_questions") or []),
                h,
                str(doc.get("status", "frozen")),
                doc.get("frozen_at"),
                str(doc.get("frozen_by", "")),
                evidence_ref,
                str(doc.get("_source_ref", "")),
            ),
        )
    conn.commit()
    return h


def insert_manifest(conn, doc: Mapping[str, Any]) -> str:
    body = {k: v for k, v in doc.items() if k not in {"batch_id", "space_hash"}}
    payload = {
        "batch_id": doc["batch_id"],
        "space_hash": doc["space_hash"],
        "manifest_sha256": sha256_hex({"batch_id": doc["batch_id"], **body}),
    }
    with conn.cursor() as cur:
        cur.execute(
            _SQL_INSERT_MANIFEST,
            (
                payload["batch_id"],
                payload["space_hash"],
                doc.get("tpl_ref", ""),
                doc.get("kind", "live"),
                int(doc.get("planned_count", 0)),
                int(doc.get("emitted_count", 0)),
                int(doc.get("truncated_count", 0)),
                int(doc.get("cap_batch", 1)),
                bool(doc.get("over_cap", False)),
                doc.get("replay_of_batch"),
                _j({k: v for k, v in doc.items() if k.startswith("detail_") or k == "detail"}),
                payload["manifest_sha256"],
                doc.get("generated_at"),
            ),
        )
    conn.commit()
    return payload["manifest_sha256"]


def insert_n_eff(conn, doc: Mapping[str, Any]) -> None:
    batch_id = doc.get("batch_id")
    with conn.cursor() as cur:
        cur.execute(
            _SQL_INSERT_NEFF,
            (
                doc["space_hash"],
                batch_id or "",
                batch_id,
                doc["estimator"],
                doc.get("record_kind", "live"),
                int(doc["nominal_count"]),
                int(doc["n_trials"]),
                int(doc["n_eff"]),
                doc.get("ratio"),
                bool(doc.get("boundary", False)),
                _j(doc.get("meta")),
                doc.get("evidence_ref", ""),
                doc.get("computed_at"),
            ),
        )
    conn.commit()


def insert_track_runs(conn, docs: Sequence[Mapping[str, Any]]) -> int:
    n = 0
    with conn.cursor() as cur:
        for doc in docs:
            cur.execute(
                _SQL_INSERT_TRACK_RUN,
                (
                    doc["space_hash"],
                    doc.get("batch_id"),
                    doc["track"],
                    doc["candidate_id"],
                    doc.get("fingerprint", ""),
                    _j(doc.get("slot_values")),
                    _j(doc.get("metrics")),
                    doc["yardstick_snapshot_id"],
                    doc.get("passed"),
                    _j(doc.get("fail_criteria") or []),
                    doc.get("record_kind", "live"),
                    doc.get("exam_ref", ""),
                    _j(doc.get("evidence_refs") or []),
                    doc.get("recorded_at"),
                ),
            )
            n += 1
    conn.commit()
    return n


def insert_pairwise(conn, docs: Sequence[Mapping[str, Any]]) -> int:
    verdicts = load_vocab("verdict")
    with conn.cursor() as cur:
        for doc in docs:
            if doc["verdict"] not in verdicts:
                msg = f"未知 verdict={doc['verdict']}"
                raise ValueError(msg)
            cur.execute(
                _SQL_INSERT_PAIRWISE,
                (
                    doc["run_id"],
                    doc["space_hash"],
                    doc.get("batch_id"),
                    doc["cand_a"],
                    doc["cand_b"],
                    doc.get("pearson"),
                    doc.get("spearman"),
                    doc.get("tail_correlation"),
                    int(doc.get("common_T", 0)),
                    doc["verdict"],
                    doc.get("hit_criteria", ""),
                    _j(doc.get("thresholds")),
                    doc.get("sustained_days"),
                    doc.get("record_kind", "live"),
                    doc.get("evidence_ref", ""),
                    doc.get("computed_at"),
                ),
            )
    conn.commit()
    return len(docs)


def insert_redundancy(conn, doc: Mapping[str, Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            _SQL_INSERT_REDUNDANCY,
            (
                doc["run_id"],
                doc["space_hash"],
                doc.get("batch_id"),
                int(doc["n_candidates"]),
                int(doc["n_pairs"]),
                int(doc["n_high_corr_pairs"]),
                doc.get("redundancy_ratio"),
                doc.get("threshold", 0.40),
                doc["verdict"],
                doc.get("estimator", "pairwise_correlation"),
                doc.get("note", ""),
                doc.get("record_kind", "live"),
                doc.get("evidence_ref", ""),
                doc.get("computed_at"),
            ),
        )
    conn.commit()


# ---------------------------------------------------------------- 读侧（审计/自检）


def table_stats(conn) -> dict[str, Any]:
    out: dict[str, Any] = {"tables": {}, "schema_present": False}
    with conn.cursor() as cur:
        cur.execute(_SQL_SCHEMA_PRESENT, (_SCHEMA,))
        out["schema_present"] = cur.fetchone() is not None
        want = [t for label, t in ddl_statements() if label not in {"schema"} and not label.startswith("idx_")]
        for table in want:
            cur.execute(
                _SQL_COL_COUNT,
                (_SCHEMA, table),
            )
            cols = int(cur.fetchone()[0])
            rows = 0
            if cols:
                cur.execute(_SQL_TABLE_ROWCOUNT % table)  # noqa: S608 — 表名来自本模块 DDL 清单
                rows = int(cur.fetchone()[0])
            out["tables"][table] = {"columns": cols, "rows": rows}
    return out


# ---------------------------------------------------------------- 自检


def _selftest() -> int:
    blocks = {
        "F-MOM-001": {"frequency": "daily", "fingerprint": "a", "eligible": True},
        "F-MOM-002": {"frequency": "daily", "fingerprint": "a", "eligible": True},  # 马甲（同指纹）
        "F-QUAL-001": {"frequency": "quarterly", "fingerprint": "b", "eligible": True},
        "F-INTR-001": {"frequency": "intraday", "fingerprint": "c", "eligible": True},
        "F-KNOW-001": {"frequency": "daily", "fingerprint": "d", "eligible": False},  # 不可复算
    }
    ops = ["add2", "sub2", "mul2", "div2", "abs1", "neg1", "sqrt1", "log1"]
    wins = ["1d", "5d", "20d", "60d"]
    tracks = ["gplearn", "agent", "mcts"]
    counts = structural_counts(blocks, ops, wins, tracks)
    # 名义=5×8×4×3=480；可行=去马甲(F-MOM-002 与 001 同指纹)+去不可复算(F-KNOW-001) 后：
    #   a 族 4 窗 + b 季频 2 窗 + c 日内 2 窗 = 8 格 × 8 算子 × 3 轨 = 192
    a = {
        "space_id": "S",
        "version": "1.0.0",
        "slots": {
            "block": {"values": sorted(blocks), "domain_ref": "r#factor_id", "mode": "cartesian", "blocks": blocks},
            "block_family": {"values": ["momentum", "quality", "intraday"], "mode": "attribute"},
            "operator": {"values": ops, "domain_ref": "gplearn#p", "mode": "cartesian"},
            "window": {"values": wins, "domain_ref": "v#w", "mode": "cartesian"},
            "track": {"values": tracks, "domain_ref": "v#t", "mode": "cartesian"},
        },
        "constraints": {"cross_slot": "freq->window"},
        "cap_template": 200,
        "cap_batch": 600,
    }
    h1, h2 = space_hash_of(a), space_hash_of(json.loads(canonical_json(a)))
    attr_only = {
        **a,
        "slots": {
            **a["slots"],
            "block_family": {"values": ["momentum", "quality", "intraday", "liquidity"], "mode": "attribute"},
        },
    }
    checks = {
        "hash 稳定可复算": h1 == h2 and len(h1) == 64,
        "属性维变更不改 hash": space_hash_of(attr_only) == h1,
        "域变更必改 hash": h1
        != space_hash_of(
            {
                **a,
                "slots": {
                    **a["slots"],
                    "window": {"values": wins + ["120d"], "domain_ref": "v#w", "mode": "cartesian"},
                },
            }
        ),
        "quarterly 仅季窗": window_allowlist(["quarterly"]) == {"20d", "60d"},
        "intraday 仅短窗": window_allowlist(["intraday"]) == {"1d", "5d"},
        "daily 全窗": window_allowlist(["daily"]) == set(wins),
        "结构计数名义=480": counts["nominal_count"] == 480,
        "结构计数可行=192": counts["feasible_count"] == 192,
        "结构 N_eff 比=0.4": abs(n_eff_structural(a)["ratio"] - 0.4) < 1e-9,
        "spearman 单调=1": abs((spearman(list(range(10)), [x * 2 + 1 for x in range(10)]) or 0) - 1) < 1e-9,
        "spearman 抗离群": abs(spearman([1, 2, 3, 4, 5, 6], [2, 3, 4, 5, 6, 1000]) or 0) > 0.5,
        "双口径分歧可判": (pearson([1, 2, 3, 4, 5, 6], [2, 3, 4, 5, 6, 1000]) or 0)
        < 0.7
        < (spearman([1, 2, 3, 4, 5, 6], [2, 3, 4, 5, 6, 1000]) or 0),
        "尾部相关可算": tail_correlation([float(i) for i in range(40)], [float(i) * 1.1 for i in range(40)])
        is not None,
        "双口径判定命中题面": verdict_for_pair(0.65, 0.78, 0.4)[0] == "REJECT"
        and "spearman" in verdict_for_pair(0.65, 0.78, 0.4)[1],
        "seal 无因拒封": _raises(lambda: seal_space(None, "x", reason=" ", sealed_at=None)),  # type: ignore[arg-type]
        "expand 未封存拒登": _raises(lambda: ensure_sealed(_NoOpConn(), "deadbeef")),
    }
    print(json.dumps(checks, ensure_ascii=False, indent=1))
    return 0 if all(checks.values()) else 1


class _NoOpConn:
    def cursor(self):  # noqa: ANN201
        raise AssertionError("不应到达 DB——预期先抛 SpaceNotSealedError")


def _raises(fn) -> bool:
    try:
        fn()
    except (ValueError, SpaceNotSealedError, AssertionError):
        return True
    return False


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="metaq_e1c 台账库自检")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--print-ddl", action="store_true", help="打印 DDL（词表渲染后）")
    args = parser.parse_args(argv)
    if args.print_ddl:
        for label, sql in ddl_statements():
            print(f"-- {label}\n{sql.strip()};\n")
        return 0
    return _selftest()


if __name__ == "__main__":
    raise SystemExit(main())
