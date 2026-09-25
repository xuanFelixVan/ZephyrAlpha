# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_drop_gate
# [MODULE] zephyr.ai_layer.redline.drop_gate
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.redline.negative_list (NL_DELETION rule_id，SSOT 引用不复制);
#                zephyr.gov_enforcement.commit_gates._diff_helpers (_read_staged_file/_split_own_foreign，共享原语);
#                zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] GitCommitGateway in-process gate 面（S3 接线批：in_process_gate_registry.yaml
#             追加条目即挂载；与 S2 三台同批）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] own-diff 静态扫描破坏性 DDL（DROP TABLE|DROP DATABASE|TRUNCATE|DROP COLUMN，
#              大小写不敏感）→ 拦+Owner 门（DESIGN §2 档 A 生产库类守卫闸，唯一新建台）；
#              own-scope（_split_own_foreign 共享原语：外来 staged warn+审计不阻断）；
#              Owner 门逃生=commit message 标记 [allow-drop-gate:<reason≥10字>]
#              （REGISTRY-MASS-DELETION 同款先例：标记随 message 永久留痕+审计，
#              使用前提=Owner 门位授权，档 A 物理删除语义不变）；
#              阻断/放行均落审计 .runtime/gate_audit/obj_s_drop_gate.jsonl
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §2 档 A
# [STABILITY] new
# [SAFETY] M（medium 实现+high 触发后果——拦的是生产库物理删除语句）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛：git diff 失败 → (True,"") fail-open；文件不可读/二进制 →
#                  跳过该文件；正则编译为模块级 Final（无每提交重编译）；检出破坏性 DDL
#                  且无逃生标记 → (False, detail) fail-closed
# [TESTS] tests/ai_layer/redline/test_drop_gate.py（对禁删清单样例路径的 DROP 语句被阻断/
#         TRUNCATE 与 DROP COLUMN 变体/大小写不敏感/普通 SQL 放行/逃生标记放行+审计/
#         reason<10 字标记无效/git 失败 fail-open）
"""drop_gate — DROP-GATE：own-diff 破坏性 DDL 静态扫描门禁（OBJ_S 施工项 S3）。

DESIGN §2 档 A 生产库类守卫闸：删除红线三档中唯一需新建的闸——
own-diff 中静态扫描 ``DROP TABLE|DROP DATABASE|TRUNCATE|DROP COLUMN`` SQL → 拦+Owner 门。
RULE-DATA-OPS 三步验证（已有）是操作时纪律，本台是提交时静态保险丝；两者互补，
不替代 RULE-DATA-OPS，不发明新刹车（物理删除的最终门位仍是 Owner）。

验收标准（红蓝 R1-F4）：对禁删清单样例路径的 DROP 语句被阻断。
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Final

from zephyr.ai_layer.redline.negative_list import NL_DELETION
from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _read_staged_file,
    _split_own_foreign,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__: Final[list[str]] = [
    "ALLOW_MARKER_RE",
    "DROP_PATTERN",
    "GATE_ID",
    "make_drop_gate",
    "scan_drop_lines",
]

GATE_ID: Final = "DROP-GATE"

# 破坏性 DDL 判据（DESIGN §2 档 A 原文四形态；大小写不敏感；词边界防误伤字段名）
DROP_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\bDROP\s+TABLE\b|\bDROP\s+DATABASE\b|\bTRUNCATE\b(?:\s+TABLE)?|\bDROP\s+COLUMN\b",
    re.IGNORECASE,
)

# Owner 门逃生标记（reason≥10 字防"标记漂洗"，REGISTRY-MASS-DELETION 同款正则语义）
ALLOW_MARKER_RE: Final[re.Pattern[str]] = re.compile(r"\[allow-drop-gate:([^\]]{10,})\]")


def scan_drop_lines(text: str) -> list[str]:
    """纯函数核：文本中破坏性 DDL 命中行（trim 后原文，供阻断 detail 与审计）。"""
    hits: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and DROP_PATTERN.search(stripped):
            hits.append(stripped)
    return hits


def _audit(gateway: Any, record: dict[str, Any]) -> None:
    """审计落盘（jsonl append 到 gateway.project_root/.runtime/gate_audit/；fail-open）。"""
    try:
        root = Path(str(getattr(gateway, "project_root", ".")))
        audit_dir = root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        with (audit_dir / "obj_s_drop_gate.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计失败不阻断判定
        logger.debug("DROP-GATE audit write failed (non-blocking)", exc_info=True)


def make_drop_gate() -> GateSpec:
    """构造 DROP-GATE 门禁（档 A 生产库守卫闸，own-scope，拦+Owner 门逃生标记）。"""

    def _check(gateway: Any, files: list[str], **kwargs: Any) -> tuple[bool, str]:
        try:
            result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
            if result.returncode != 0:
                return True, ""  # fail-open：git 失败不阻断
            staged = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        except Exception:  # noqa: BLE001 — fail-open
            logger.warning("DROP-GATE fail-open: git diff 异常", exc_info=True)
            return True, ""

        own, _foreign = _split_own_foreign(gateway, staged, files, kwargs.get("session_id"), gate_name=GATE_ID)
        all_hits: list[str] = []
        for rel in own:
            text = _read_staged_file(gateway, rel)
            if text is None:
                continue  # fail-open：读失败/二进制
            for hit_line in scan_drop_lines(text):
                all_hits.append(f"  {rel}: {hit_line[:160]}")

        if not all_hits:
            return True, ""

        message = str(kwargs.get("commit_message", "") or "")
        marker = ALLOW_MARKER_RE.search(message)
        if marker:
            _audit(
                gateway,
                {
                    "timestamp": now_utc().isoformat(),
                    "gate": GATE_ID,
                    "rule_id": NL_DELETION,
                    "action": "allowed_by_marker",
                    "session_id": kwargs.get("session_id") or "?",
                    "reason": marker.group(1),
                    "hits": all_hits[:50],
                },
            )
            note = (
                f"[warn] DROP-GATE: 破坏性 DDL 命中但 message 标记放行（reason: {marker.group(1)}）"
                "——档 A 物理删除=Owner 门位，请确认备份可回滚"
            )
            logger.warning("%s", note)
            return True, note

        _audit(
            gateway,
            {
                "timestamp": now_utc().isoformat(),
                "gate": GATE_ID,
                "rule_id": NL_DELETION,
                "action": "block",
                "session_id": kwargs.get("session_id") or "?",
                "hits": all_hits[:50],
            },
        )
        detail = (
            "DROP-GATE: own-diff 检出破坏性 DDL（DESIGN §2 档 A 生产库守卫闸，硬阻断）\n"
            "  DROP TABLE/DROP DATABASE/TRUNCATE/DROP COLUMN=物理删除，Owner 门位。\n"
            "  ①生产库删除走 RULE-DATA-OPS 三步验证流程（操作时纪律）；\n"
            "  ②确属 Owner 授权的合法 DDL 迁移：commit message 加标记\n"
            "    [allow-drop-gate:<reason≥10字>]（随 message 永久留痕+审计）。\n"
            + "\n".join(all_hits[:20])
            + (f"\n  ...(+{len(all_hits) - 20} more)" if len(all_hits) > 20 else "")
        )
        logger.error("%s", detail)
        return False, detail

    return GateSpec(gate_id=GATE_ID, check=_check, priority=148)
