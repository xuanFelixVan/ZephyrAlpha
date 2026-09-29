# [TTL] permanent
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §integrity-intent-ledger
# [MODULE] zephyr.gov_enforcement.derived_dirty_ledger
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.io.file_utils
# [CONSUMERS] scripts.governance.commit_queue_landing, zephyr.gov_enforcement.rule_bridge.git_commit_gateway, zephyr.governance.audit.reconciliation_registry
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只追加（append-only JSONL）；CAS 追加禁裸写；意图记录处处 fail-open 不阻断提交链
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CAS 重试 5 次后抛错=由调用方 fail-open 吞并告警
# [TESTS] tests/governance/audit/test_integrity_head_baseline.py
"""派生刷新意图账（战役 B0/M1·P3-G，2026-09-24）。

head 态下 GATE-RULES-INTEGRITY 判定读当前 HEAD（validate_rules_integrity check head 模式），
rules_integrity_db.json 快照退出判定链 ⇒ 基线刷新不再是提交关键路径义务。生产者
（landing / gateway post-flush / reconciler）只向本账追加"该刷了"的意图行；
消费端（belt 守护既有事件，后续批挂接）按 head_sha 去抖批量刷新审计快照。
消费状态记账（pending_head_sha/mark_success）随消费端批落地，本模块先供生产侧。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo_root 仓根
#   fields: Path|str（landing/gateway post-flush/reconciler 各调用方传各自仓根）
#   code: read_integrity_baseline_mode(repo_root) / append_intent(repo_root, record)
# - id: I2
#   name: 基线面配置源
#   fields: env ZEPHYR_INTEGRITY_BASELINE ∈ {head,snapshot} > flags.integrity_baseline_mode.mode > 出厂 snapshot
#   code: read_integrity_baseline_mode()
# - id: I3
#   name: 意图记录 record
#   fields: dict（qid/session_id/head_sha/rules_touched/reason；缺 ts 自动补 UTC ISO）
#   code: append_intent(record)
# 层: 特征
# - id: F1
#   name_zh: 快照退出判定链
#   name_en: snapshot_exit
#   intro: head 态校验参考面=当前 HEAD，rules_integrity_db.json 快照退出判定链 ⇒ 刷新降级为意图记账
#   formula: mode=head ⇒ 判定读 HEAD blob（一次 cat-file --batch，n=120 0.110s）；mode=snapshot ⇒ 同步刷新义务仍在
#   code: read_integrity_baseline_mode（scripts 侧镜像=validate_rules_integrity._baseline_mode，非 extract 级克隆）
#   registry: 无（基线面旗为本模块机生事实）
#   is_break: false
# 层: 算法
# - id: A1
#   name_zh: 基线面旗三级解析（env>flags>出厂）
#   name_en: read_integrity_baseline_mode
#   intro: fail-closed 解析；配置设施异常回 snapshot=现行为，绝不因读不到配置改变判定
#   inputs: I1/I2
#   outputs: "head"|"snapshot"
# - id: A2
#   name_zh: 意图 CAS 追加
#   name_en: append_intent
#   intro: JSONL 只追加；safe_write_text CAS 5 次重试后抛错=调用方 fail-open 吞并告警
#   inputs: I1/I3
#   outputs: .runtime/derived_dirty/integrity_intent.jsonl 追加一行
# 层: 输出
# - id: O1
#   name_zh: 基线面旗
#   name_en: baseline_mode
#   intro: 消费方据旗分流 snapshot 同步刷新 vs head 意图记账
#   downstream: commit_queue_landing._integrity_baseline_mode/_record_integrity_refresh_intent、validate_rules_integrity 判定链
# - id: O2
#   name_zh: 刷新意图行
#   name_en: intent_line
#   intro: 消费端（belt 守护既有事件）按 head_sha 去抖批量刷新审计快照（N 件→1 刷）
#   downstream: integrity 消费批（pending_head_sha/mark_success 随消费端批落地）
# [/ALGO_FLOW]
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.io.file_utils import content_sha256, safe_write_text

LEDGER_REL = Path(".runtime") / "derived_dirty" / "integrity_intent.jsonl"


def read_integrity_baseline_mode(repo_root: Path | str) -> str:
    """integrity 基线面旗读取唯一点（src 侧；fail-closed 回现状，不翻出厂默认）。

    优先级：env ZEPHYR_INTEGRITY_BASELINE ∈ {head, snapshot} > config/flags.yaml
    flags.integrity_baseline_mode.mode > "snapshot"（出厂默认=现行为）。
    scripts 侧同语义实现在 validate_rules_integrity._baseline_mode（该脚本独立运行
    不依赖 src 包，故两处互为镜像、同优先级；非 extract 级克隆）。
    """
    import os

    env = os.environ.get("ZEPHYR_INTEGRITY_BASELINE", "").strip().lower()
    if env in ("head", "snapshot"):
        return env
    try:
        import yaml

        with open(Path(repo_root) / "config" / "flags.yaml", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        mode = ((doc.get("flags") or {}).get("integrity_baseline_mode") or {}).get("mode")
        return mode if mode in ("head", "snapshot") else "snapshot"
    except Exception:  # noqa: BLE001 — 配置设施异常回现状
        return "snapshot"


def append_intent(repo_root: Path | str, record: dict[str, Any]) -> None:
    """CAS 追加一条意图记录（热文件纪律：safe_write_text；缺 ts 自动补 UTC ISO）。

    本函数绝不抛出除 CAS 耗尽外的异常路径语义——调用方普遍 fail-open。
    """
    root = Path(repo_root)
    rec = dict(record)
    rec.setdefault("ts", datetime.now(UTC).isoformat())
    path = root / LEDGER_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(rec, ensure_ascii=False, sort_keys=True)
    last: Exception | None = None
    for _ in range(5):
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        base = content_sha256(text)
        sep = "" if (not text or text.endswith("\n")) else "\n"
        res = safe_write_text(
            path,
            text + sep + line + "\n",
            expected_base_sha256=base,
            repo_root=str(root),
            allow_mass_edit=True,
        )
        ok = getattr(res, "ok", None)
        if ok is None:
            ok = getattr(res, "success", bool(res))
        if ok:
            return
        last = RuntimeError(f"append_intent CAS retry: {res}")
    raise last or RuntimeError("append_intent failed")
