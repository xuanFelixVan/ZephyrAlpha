# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_negative_list_gates
# [MODULE] zephyr.ai_layer.redline.negative_list_gates
# [DOMAIN] D_GOVERNANCE
# [TESTS] tests/ai_layer/（对应段测试目录）
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.redline.negative_list (REAL_KEY_MARKER/NL rule_id 常量，SSOT 引用不复制);
#                zephyr.gov_enforcement.commit_gates._diff_helpers (_read_staged_file/_split_own_foreign，共享原语);
#                zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] GitCommitGateway in-process gate 面（S2 接线批：在
#             docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml
#             追加三台 gate 条目即挂载——YAML 列表追加，无需改 gateway 代码；
#             本班不改既有文件，挂载条目=接线批随批落地）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 三台 gate 均 own-scope（_split_own_foreign 共享原语：外来 staged warn+审计不阻断，
#              §3.1 他会话在途违规不代修）；check 永不抛（git/读文件/YAML 解析失败 → fail-open
#              跳过该文件，不误报）；红线检查点（负面清单命中）=硬阻断 fail-closed；
#              YAML 判据=解析级 diff（yaml.safe_load 深比较），禁字符串比对（DESIGN §1 NL-5）；
#              白名单仅 secret_registry.yaml 本体与 SECRETS.md（NL-2 判据②原文）；
#              宪法行数上限=AGENTS.md ≤300 行硬上限（NL-3 判据②，宪法 §6 上下文预算）；
#              审计落 .runtime/gate_audit/ 家族（rule_id 统一留痕）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §1 NL-2/NL-3/NL-5
# [STABILITY] new
# [SAFETY] M（阻断提交=红线检查点；白名单外的 QMT 前缀实盘键名引用零逃生标记——
#          NL-2 无 [allow-*] 逃生，泄密面不给 message 漂洗通道）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 三台 check 永不抛：git diff/show 失败、文件不可读、YAML 解析失败 →
#                  跳过该文件继续（fail-open，交 syntax/encoding 类 gate）；命中判据 →
#                  (False, detail) 硬阻断；审计写失败静默降级；新任务书（HEAD 无基线）
#                  =判据预注册动作，放行+审计（near_miss 留痕供 S7）
# [TESTS] tests/ai_layer/redline/test_negative_list_gates.py（六条违例样例各一被拦：
#         QMT 前缀实盘键名引用/白名单放行/判据字段结构变更同批阻断/新任务书放行留痕/
#         宪法 >300 行阻断/300 行边界放行/外来 staged 不阻断）
"""negative_list_gates — OBJ_S 负面清单 gate 组（OBJ_S 施工项 S2，挂 GitCommitGateway）。
# [ALGO_FLOW] external: docs/03_modules/_domain_ai_layer/algo_flow/negative_list_gates.yaml

三台（DESIGN §1 检查点 + §4 S2 行）：

1. ``REAL-KEY-REFERENCE-SCAN``（NL-2 判据②）：own-diff 中出现 QMT 前缀实盘键名 字样引用
   （源码/脚本/配置/文档）=违例，白名单仅 secret_registry.yaml 本体与 SECRETS.md 文档行；
   增量口径=staged 出现次数须 > HEAD 基线次数才计违例（存量正文行不连坐——2026-09-27 实现
   对齐判据原文修：此前整文件扫描使载有该字样验收行的 OBJ_S DESIGN 等文档任何合法编辑恒被拦）。
2. ``TASK-ORDER-DOCS-LOCK``（NL-5）：同一会话 own-diff 同时包含施工产物 与 任务书
   （TO-*.yaml）definition_of_done/red_lines/acceptance 任一字段的结构性变更
   （YAML 解析级 diff）→ 阻断；判据变更唯一合法路径=独立复核会话出判据修订案或 Owner 改判。
3. ``CONSTITUTION-LINE-LIMIT``（NL-3 判据②）：AGENTS.md 修改后行数 >300（宪法 ≤300 行
   硬上限，等长替换的机械面）→ 阻断。NL-3 判据①（protected paths=immutable_core 运行时
   已有）与判据③（修宪裁定号=GW POST 链已有）不在本台重复建。

挂载（接线批）：in_process_gate_registry.yaml gates 列表追加条目
（module_path=zephyr.ai_layer.redline.negative_list_gates，factory_function=make_*_gate）。
"""

from __future__ import annotations

import fnmatch
import json
import logging
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.ai_layer.redline.negative_list import (
    NL_ACCEPTANCE_LOCK,
    NL_CONSTITUTION,
    NL_REAL_KEYS,
    REAL_KEY_MARKER,
)
from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _read_head_file,
    _read_staged_file,
    _split_own_foreign,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__: Final[list[str]] = [
    "CONSTITUTION_LINE_LIMIT",
    "TASK_ORDER_FIELDS",
    "TASK_ORDER_GLOB",
    "make_constitution_line_limit_gate",
    "make_real_key_reference_scan_gate",
    "make_task_order_docs_lock_gate",
    "scan_constitution_lines",
    "scan_real_key_hits",
    "structural_field_changes",
    "task_order_lock_violation",
]

CONSTITUTION_LINE_LIMIT: Final = 300
CONSTITUTION_FILE: Final = "AGENTS.md"
TASK_ORDER_GLOB: Final = "TO-*.yaml"
TASK_ORDER_FIELDS: Final[tuple[str, ...]] = ("definition_of_done", "red_lines", "acceptance")
_REAL_KEY_WHITELIST: Final[tuple[str, ...]] = ("secret_registry.yaml", "SECRETS.md")


def _audit(gateway, gate_id: str, record: dict[str, Any]) -> None:
    """gate 审计落盘（jsonl append 到 gateway.project_root/.runtime/gate_audit/；fail-open）。

    锚 gateway.project_root（gate 家族惯例）——测试传 tmp_path 项目根即天然隔离生产路径。
    """
    try:
        root = Path(str(getattr(gateway, "project_root", ".")))
        audit_dir = root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        path = audit_dir / (gate_id.lower().replace("-", "_") + ".jsonl")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计失败不阻断判定
        logger.debug("%s audit write failed (non-blocking)", gate_id, exc_info=True)


def _staged_all_files(gateway) -> list[str] | None:
    """staged 全量文件清单（AM filter；git 失败返回 None=fail-open 信号）。"""
    try:
        result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if result.returncode != 0:
            return None
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:  # noqa: BLE001 — fail-open
        logger.warning("obj_s gate fail-open: git diff 异常", exc_info=True)
        return None


# ────────────────── REAL-KEY-REFERENCE-SCAN（NL-2）──────────────────


def _is_real_key_whitelisted(rel: str) -> bool:
    """NL-2 白名单：secret_registry.yaml 本体与 SECRETS.md（basename 匹配，任意目录深度）。"""
    norm = rel.replace("\\", "/")
    return any(fnmatch.fnmatch(norm.split("/")[-1], pattern) for pattern in _REAL_KEY_WHITELIST)


def scan_real_key_hits(files_with_text: dict[str, str]) -> list[str]:
    """纯函数核：扫文本面中 QMT 前缀实盘键名 字样引用（白名单先剔除）→ 命中路径列表。"""
    hits: list[str] = []
    for rel, text in sorted(files_with_text.items()):
        if _is_real_key_whitelisted(rel):
            continue
        if REAL_KEY_MARKER in text:
            hits.append(rel)
    return hits


def make_real_key_reference_scan_gate() -> GateSpec:
    """构造 REAL-KEY-REFERENCE-SCAN 门禁（NL-2 判据②，own-scope，命中即阻断，无逃生标记）。"""

    def _check(gateway, files: list[str], **kwargs: Any) -> tuple[bool, str]:
        staged = _staged_all_files(gateway)
        if staged is None:
            return True, ""
        own, _foreign = _split_own_foreign(
            gateway,
            staged,
            files,
            kwargs.get("session_id"),
            gate_name="REAL-KEY-REFERENCE-SCAN",
        )
        candidates: dict[str, str] = {}
        for rel in own:
            if _is_real_key_whitelisted(rel):
                continue
            text = _read_staged_file(gateway, rel)
            if text is None or REAL_KEY_MARKER not in text:
                continue
            head_text = _read_head_file(gateway, rel)
            if head_text is not None and text.count(REAL_KEY_MARKER) <= head_text.count(REAL_KEY_MARKER):
                continue  # 增量口径：own-diff 未新增实盘键名字样（存量正文行不连坐——NL-2 判据
                # ②原文"own-diff 中出现"的实现对齐修，2026-09-27；否则载有该字样验收行的
                # OBJ_S DESIGN 等文档任何合法编辑恒被拦）
            candidates[rel] = text
        if not candidates:
            return True, ""
        hits = scan_real_key_hits(candidates)
        _audit(
            gateway,
            "REAL-KEY-REFERENCE-SCAN",
            {
                "timestamp": now_utc().isoformat(),
                "gate": "REAL-KEY-REFERENCE-SCAN",
                "rule_id": NL_REAL_KEYS,
                "action": "block",
                "session_id": kwargs.get("session_id") or "?",
                "hits": hits,
            },
        )
        detail = (
            "REAL-KEY-REFERENCE-SCAN: own-diff 出现实盘密钥键名引用（NL-2 判据②，硬阻断无逃生）\n"
            "  AI 会话源码/脚本/配置/文档禁出现 " + REAL_KEY_MARKER + " 字样；白名单仅\n"
            "  secret_registry.yaml 本体与 SECRETS.md 文档行。\n" + "\n".join(f"  {h}" for h in hits[:20])
        )
        logger.error("%s", detail)
        return False, detail

    return GateSpec(gate_id="REAL-KEY-REFERENCE-SCAN", check=_check, priority=149)


# ────────────────── TASK-ORDER-DOCS-LOCK（NL-5）──────────────────


def _parse_yaml_mapping(text: str) -> dict[str, Any] | None:
    """YAML → dict（解析失败/非 dict → None，调用方 fail-open）。"""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def structural_field_changes(
    head_text: str | None,
    staged_text: str,
    *,
    fields: tuple[str, ...] = TASK_ORDER_FIELDS,
) -> list[str]:
    """纯函数核：任务书判据字段**解析级**结构变更清单（YAML 深比较，非字符串比对）。

    head_text=None（新任务书）→ 返回 []（判据预注册动作，由调用方放行+审计）。
    任一侧 YAML 解析失败 → 返回 []（fail-open，判不了不误报）。
    """
    staged_map = _parse_yaml_mapping(staged_text)
    if staged_map is None:
        return []
    if head_text is None:
        return []
    head_map = _parse_yaml_mapping(head_text)
    if head_map is None:
        return []
    return [name for name in fields if head_map.get(name) != staged_map.get(name)]


def task_order_lock_violation(
    changed_fields: list[str],
    has_construction_artifacts: bool,
) -> bool:
    """纯函数核：判据字段有结构变更 且 同批含施工产物 → NL-5 违例成立。"""
    return bool(changed_fields) and has_construction_artifacts


def make_task_order_docs_lock_gate() -> GateSpec:
    """构造 TASK-ORDER-DOCS-LOCK 门禁（NL-5，own-scope，与 REGISTRY-MASS-DELETION 同挂载面）。"""

    def _check(gateway, files: list[str], **kwargs: Any) -> tuple[bool, str]:
        staged = _staged_all_files(gateway)
        if staged is None:
            return True, ""
        own, _foreign = _split_own_foreign(
            gateway,
            staged,
            files,
            kwargs.get("session_id"),
            gate_name="TASK-ORDER-DOCS-LOCK",
        )
        cards = [rel for rel in own if fnmatch.fnmatch(rel.replace("\\", "/").split("/")[-1], TASK_ORDER_GLOB)]
        if not cards:
            return True, ""
        has_artifacts = any(rel not in cards for rel in own)
        hits: list[str] = []
        near_miss: list[str] = []
        for rel in cards:
            staged_text = _read_staged_file(gateway, rel)
            if staged_text is None:
                continue  # fail-open：读失败
            head_result = None
            try:
                head_result = gateway.run_git(["git", "show", f"HEAD:{rel}"])
            except Exception:  # noqa: BLE001 — fail-open
                pass
            head_text = head_result.stdout if head_result is not None and head_result.returncode == 0 else None
            changed = structural_field_changes(head_text, staged_text)
            if not changed:
                continue
            if task_order_lock_violation(changed, has_artifacts):
                hits.append(f"  {rel}: 判据字段结构变更 {changed}")
            else:
                near_miss.append(f"  {rel}: 判据字段结构变更 {changed}（同批无施工产物，放行留痕）")
        if not hits:
            if near_miss:
                _audit(
                    gateway,
                    "TASK-ORDER-DOCS-LOCK",
                    {
                        "timestamp": now_utc().isoformat(),
                        "gate": "TASK-ORDER-DOCS-LOCK",
                        "rule_id": NL_ACCEPTANCE_LOCK,
                        "action": "near_miss_warn",
                        "session_id": kwargs.get("session_id") or "?",
                        "detail": near_miss,
                    },
                )
            return True, ""
        _audit(
            gateway,
            "TASK-ORDER-DOCS-LOCK",
            {
                "timestamp": now_utc().isoformat(),
                "gate": "TASK-ORDER-DOCS-LOCK",
                "rule_id": NL_ACCEPTANCE_LOCK,
                "action": "block",
                "session_id": kwargs.get("session_id") or "?",
                "hits": hits,
            },
        )
        detail = (
            "TASK-ORDER-DOCS-LOCK: 施工会话同批改自己的验收判据+施工产物（NL-5，硬阻断）\n"
            "  判据变更唯一合法路径=独立复核会话出判据修订案或 Owner 改判\n"
            "  （复核级/终审级协议，主文档 §3.2）。\n" + "\n".join(hits[:20])
        )
        logger.error("%s", detail)
        return False, detail

    return GateSpec(gate_id="TASK-ORDER-DOCS-LOCK", check=_check, priority=150)


# ────────────────── CONSTITUTION-LINE-LIMIT（NL-3 判据②）──────────────────


def scan_constitution_lines(staged_text: str, *, limit: int = CONSTITUTION_LINE_LIMIT) -> int:
    """纯函数核：staged 宪法文本行数（splitlines 口径，与 wc -l 语义兼容：末行无换行也计）。"""
    return len(staged_text.splitlines())


def make_constitution_line_limit_gate() -> GateSpec:
    """构造 CONSTITUTION-LINE-LIMIT 门禁（NL-3 判据②：AGENTS.md ≤300 行硬上限）。"""

    def _check(gateway, files: list[str], **kwargs: Any) -> tuple[bool, str]:
        staged = _staged_all_files(gateway)
        if staged is None:
            return True, ""
        own, _foreign = _split_own_foreign(
            gateway,
            staged,
            files,
            kwargs.get("session_id"),
            gate_name="CONSTITUTION-LINE-LIMIT",
        )
        target = next(
            (rel for rel in own if rel.replace("\\", "/").split("/")[-1] == CONSTITUTION_FILE),
            None,
        )
        if target is None:
            return True, ""
        staged_text = _read_staged_file(gateway, target)
        if staged_text is None:
            return True, ""  # fail-open：读失败
        lines = scan_constitution_lines(staged_text)
        if lines <= CONSTITUTION_LINE_LIMIT:
            return True, ""
        _audit(
            gateway,
            "CONSTITUTION-LINE-LIMIT",
            {
                "timestamp": now_utc().isoformat(),
                "gate": "CONSTITUTION-LINE-LIMIT",
                "rule_id": NL_CONSTITUTION,
                "action": "block",
                "session_id": kwargs.get("session_id") or "?",
                "file": target,
                "lines": lines,
                "limit": CONSTITUTION_LINE_LIMIT,
            },
        )
        detail = (
            f"CONSTITUTION-LINE-LIMIT: 宪法 {lines} 行 >{CONSTITUTION_LINE_LIMIT} 行硬上限"
            "（NL-3 判据②，硬阻断）\n"
            "  宪法 §6：新增内容必须等长替换；AI 只有提案权，走 OBJ_R 四步流水线。"
        )
        logger.error("%s", detail)
        return False, detail

    return GateSpec(gate_id="CONSTITUTION-LINE-LIMIT", check=_check, priority=151)


# [接线批 2026-09-24 st-ailayer-final-20260924] priority 重编号 145/146/147→149/150/151：实占扫描发现四图门
# （DECISION-MAP/GATE-BATTLE-MAP-ALIGNMENT/INDUSTRY-CHAIN-MAP/FACTORY-MAP）代码 GateSpec 实占 145-148，
# 本组按 DESIGN 陈旧值 142 旁落成撞号（历史事故同型：oddjobs 夜四 map 门 145-148 撞车）——登记册注释同步。
