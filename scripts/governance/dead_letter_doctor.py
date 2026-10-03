# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §commit_queue 死信急诊
# create-guard-not-dup: 本模块=死信袋"手续类死因"的急诊分诊台（诊断/处方/受控执行），非死因归因引擎（session_takeover_ledger.triage_bag 归因管"内容"）/非 requeue 通道（commit_queue.requeue 是重投正门）/非分类真源（classify_dead_reason 是 env/item/other 真源）的任一复用——三者命中词仅因共享 "dead/classify" 通用词
# noqa: m11-perm-manual-legitimate  M11豁免: CLI 操作员工具（--scan/--prescribe/--apply 人工/总包触发），非常驻服务；写面=登记类元数据（经 d3_metadata 正门工具），默认零写
# [MODULE] scripts.governance.dead_letter_doctor
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(argparse/ast/json/os/re/sys/time/datetime/pathlib)；scripts.commit_queue（classify_dead_reason 死因三分类真源 + _QID_RE qid 白名单，复用禁重写）；scripts.governance.d3_metadata.batch_creation_tokens（函数级 import：load_registered/build_block/resolve_anchor/insert_block/_creation_tokens_section/_wide_prefix_issues/_TOKEN_RE/_REGISTRY）；scripts.governance.d3_metadata.add_module_translation（函数级 import：add_translation）
# [CONSUMERS] 命令行（--scan 分诊报告 / --prescribe <qid> 处方 / --apply <qid> 受控执行）；总包/人工消费 doctor_prescriptions/<qid>.json 后自行走 commit_queue.py requeue 正门重投
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 三道铁闸（Owner 裁定 B，一字不打折）——闸一·只动表格不动货：doctor 只生成/登记"登记类元数据"（creation_token/plain_zh/depgraph 指引），被提交的业务内容一个字节不许改（r5_suffix/vocab/depgraph 族只出处方不执行，涉及改名/改内容/改依赖图）；闸二·不许走捷径：doctor 永不直接 requeue，处方末步固定指向 python scripts/commit_queue.py requeue <qid> 正门（全部门禁重过，一次不跳）；闸三·只救一次：同一 (session_id, 手续族) 自动补手续最多 1 次（dead_letter_doctor_state.json 计数，达标拒绝再补转人工）；--scan 严格零写（不落 state/audit/处方任何文件，天然幂等）；处方是建议（--prescribe 零登记册写入）；--apply 只对机器可定处方执行且 plain_zh 条目必须人工经 --params 供稿（登记 module_path 必须属于袋内文件，防张冠李戴）；执行前查闸三计数、执行后写 doctor_audit.jsonl（ts/qid/session_id/action/family/result/operator）；creation_token 执行复用 batch_creation_tokens 函数级 import（含 W4 宽前缀防呆同源判据 + 写前/写后自检失败捕获）；状态/审计/处方全部只写队列根下 doctor 自有文件（禁碰袋本体/生产数据/git 元数据）；CREATE-GUARD 的 SSOT 碰撞子族（能力重复/basename 碰撞）属内容问题超闸一，只出处方
# [MODIFY-GUARD] 五族标记表/闸三上限/审计字段变更须与 scripts/commit_queue.py 的 _DEAD_PRESCRIPTIONS 标记族及 docs/_working 分诊战役笔记同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功（含设计内跳过：族不自动执行/参数未定/无事可做——均已审计留痕）; exit 1=参数/IO 错误（qid 非法/袋不存在/params 不可解析/已重投袋/invalid_params）; exit 2=闸三拒绝（额度用尽转人工）; exit 3=执行失败（登记工具自检失败/返回非 0）; 库层 apply_healing/prescribe 返回 (exit_code, dict) 不抛（内部异常折叠进 result）
# [TESTS] tests/governance/test_dead_letter_doctor.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# -*- coding: utf-8 -*-
"""dead_letter_doctor.py — 死信急诊分诊台（commit_queue 手续类死因的"先补手续再重投"通道）。

病根：.runtime/commit_queue/dead/ 死信积压中约六成死因是**纯手续问题**（CREATE-GUARD
缺 creation_token / TRANSLATION-COVERAGE 缺大白话简介 / R5-DIGIT-SUFFIX 目录数字
后缀 / GATE-VOCAB 术语硬编码 / DEPGRAPH-ENFORCEMENT 未登记依赖节点）——袋内容是
完好的工作成果，只因手续不全被挡；而死信流水线只有 requeue 重投一条路，没有
"先补手续再重投"的通道，手续类袋永远卡死。

治法（Owner 裁定 B，三道铁闸）：
- 闸一·只动表格不动货：doctor 只生成/登记登记类元数据，业务内容零改动；
- 闸二·不许走捷径：doctor 本身不 requeue——只产出"处方+已补齐的手续"，重投由
  人/总包显式走 ``commit_queue.py requeue`` 正门（重新过全部原门禁）；
- 闸三·只救一次：同一 (session_id, 手续族) 自动补手续最多 1 次，再失败转人工。

与既有设施的分 Rights（禁重造轮子）：
- 死因三分类真源=scripts.commit_queue.classify_dead_reason（env/item/other）——
  doctor 复用之，env 族（requeue 即愈）不进急诊；
- 五族标记是 doctor 自有的手续族层（三分类里没有），单一标记表 _FAMILY_MARKERS
  同时供分类与处方使用；
- 内容归因=session_takeover_ledger.triage_bag/classify_entry（八类归因管"内容"），
  doctor 管"手续"——互补不重叠。

Usage::

    python scripts/governance/dead_letter_doctor.py --scan               # 诊断（默认，零写）
    python scripts/governance/dead_letter_doctor.py --scan --json        # 机读分诊报告
    python scripts/governance/dead_letter_doctor.py --prescribe <qid>    # 单袋处方（建议，不执行）
    python scripts/governance/dead_letter_doctor.py --apply <qid> \\     # 受控执行（默认关，须显式）
        [--params params.json]                                           # plain_zh 人工供稿/能力名覆盖
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# 引导 repo 根入 sys.path：直跑场景（python scripts/governance/dead_letter_doctor.py）
# sys.path[0]=scripts/governance，`import scripts.commit_queue` 需要根在 path（对齐
# scripts/commit_queue.py 自身的引导姿势）。
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import scripts.commit_queue as _cq  # noqa: E402 — 依赖上面的 sys.path 引导，必须后置

__all__ = [
    "FAMILY_CREATE_GUARD",
    "FAMILY_PLAIN_ZH",
    "FAMILY_R5_SUFFIX",
    "FAMILY_VOCAB",
    "FAMILY_DEPGRAPH",
    "FAMILY_ENV",
    "FAMILY_UNTREATABLE",
    "AUTO_HEALABLE_FAMILIES",
    "PRESCRIPTION_ONLY_FAMILIES",
    "MAX_AUTO_HEAL_ATTEMPTS",
    "classify_family",
    "load_dead_bags",
    "diagnose",
    "build_prescription",
    "prescribe",
    "load_state",
    "apply_healing",
    "main",
]

# ---------------------------------------------------------------------------
# 手续族定义（单一标记表：分类与处方共用，禁第二套判据）
# ---------------------------------------------------------------------------

FAMILY_CREATE_GUARD = "creation_token"
FAMILY_PLAIN_ZH = "plain_zh"
FAMILY_R5_SUFFIX = "r5_suffix"
FAMILY_VOCAB = "vocab"
FAMILY_DEPGRAPH = "depgraph"
# env 族：物品无辜 requeue 即愈（classify_dead_reason 真源判定），不是手续问题
FAMILY_ENV = "env_requeueable"
# 不治族：既非手续也非 env，人工排查（内容归因请走 session_takeover_ledger.triage_bag）
FAMILY_UNTREATABLE = "untreatable"

# 五族标记=门禁名子串（与 _DEAD_PRESCRIPTIONS 同款"marker in reason"姿势；这些
# 门禁名在三分类真源里不存在，属 doctor 自有的手续族层——不是重写第二套正则）。
_FAMILY_MARKERS: tuple[tuple[str, str], ...] = (
    (FAMILY_CREATE_GUARD, "CREATE-GUARD"),
    (FAMILY_PLAIN_ZH, "TRANSLATION-COVERAGE"),
    (FAMILY_R5_SUFFIX, "R5-DIGIT-SUFFIX"),
    (FAMILY_VOCAB, "GATE-VOCAB"),
    (FAMILY_DEPGRAPH, "DEPGRAPH-ENFORCEMENT"),
)

# 闸一落地：机器可自动执行的族只有登记类两族（token/翻译都是"登记表格"动作）
AUTO_HEALABLE_FAMILIES = frozenset({FAMILY_CREATE_GUARD, FAMILY_PLAIN_ZH})
# 闸一落地：这三族治法是改名/改内容/改依赖图——只出处方，永不自动执行
PRESCRIPTION_ONLY_FAMILIES = frozenset({FAMILY_R5_SUFFIX, FAMILY_VOCAB, FAMILY_DEPGRAPH})
# 手续五族=可治愈（补手续后正门重投可过）
PROCEDURAL_FAMILIES = AUTO_HEALABLE_FAMILIES | PRESCRIPTION_ONLY_FAMILIES

# 闸三：同 (session_id, 手续族) 自动补手续最大次数——再失败转人工
MAX_AUTO_HEAL_ATTEMPTS = 1

# doctor 自有文件面（全部在队列根下，不碰袋本体）
_DEFAULT_QUEUE_ROOT = _REPO_ROOT / ".runtime" / "commit_queue"
_PRESCRIPTIONS_DIRNAME = "doctor_prescriptions"
_AUDIT_FILENAME = "doctor_audit.jsonl"
_STATE_FILENAME = "dead_letter_doctor_state.json"
_DEFAULT_OPERATOR = "dead-letter-doctor-cli"

# 死因文本里门禁点名的文件清单（Python repr 风格 "['a.md', 'b.md']"）——CREATE-GUARD
# 缺 token 型死因把涉案路径整份嵌在死因串里，这是机器可定目标清单的正门来源。
_BRACKET_LIST_RE = re.compile(r"\[[^\[\]]*\]")

# CREATE-GUARD 的 SSOT 碰撞子族标记：治法是改内容（删除新文件/挪目录），不是补
# 手续——闸一禁自动，只出处方（判据来自生产死因样本 q-20260923-st-chainpile-…-0055）。
_SSOT_COLLISION_MARKERS = ("能力重复", "basename")


def _now_iso() -> str:
    """当前 UTC ISO8601。

    为什么经 epoch 中转而非裸 ``datetime.now()``：项目生成器面禁 naive now（m46），
    审计/处方时间戳是运行面一次性取时——``fromtimestamp(t, tz=utc)`` 天然带时区，
    无需 noqa 豁免。
    """
    return datetime.fromtimestamp(time.time(), tz=timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 分诊（诊断模式，严格零写）
# ---------------------------------------------------------------------------


def classify_family(dead_reason: str) -> str:
    """死因 → 手续族（七值：五手续族 + env_requeueable + untreatable）。

    为什么先走 ``_cq.classify_dead_reason``：env/item/other 三分类是既有真源
    （commit_queue.py:3349，复用禁重写第二套正则）——env 族（瞬态锁/句柄争用）
    物品无辜 requeue 即愈，根本不是手续问题，不进急诊；item/other 再按门禁名
    标记细分手续五族，未命中=不治（人工排查）。
    """
    reason = dead_reason or ""
    if _cq.classify_dead_reason(reason) == "env":
        return FAMILY_ENV
    for family, marker in _FAMILY_MARKERS:
        if marker in reason:
            return family
    return FAMILY_UNTREATABLE


def _bag_from_data(data: dict, fallback_qid: str) -> dict:
    """死袋 JSON → doctor 标准视图（只读不改原 dict 的键语义）。"""
    reason = str(data.get("dead_reason") or "")
    return {
        "qid": str(data.get("qid") or fallback_qid),
        "session_id": data.get("session_id"),
        "dead_reason": reason,
        "family": classify_family(reason),
        # requeued 是 {new_qid, at} 或假值——bool 化即可（真源写口在 requeue 命令）
        "requeued": bool(data.get("requeued")),
        "file_paths": [f.get("path") for f in (data.get("files") or []) if isinstance(f, dict) and f.get("path")],
    }


def load_dead_bags(queue_root: Path) -> list[dict]:
    """遍历 dead/ 袋（只 q-*.json，天然跳过 _recurrence_state 等非袋件）。

    损坏袋不抛：记 corrupt=True 归不治族（急诊台不能被一具坏尸体卡死分诊）。
    """
    dead_dir = queue_root / "dead"
    if not dead_dir.is_dir():
        return []
    bags: list[dict] = []
    for entry in sorted(dead_dir.glob("q-*.json")):
        try:
            data = json.loads(entry.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("袋顶层不是 object")
        except (OSError, ValueError):
            bags.append(
                {
                    "qid": entry.stem,
                    "session_id": None,
                    "dead_reason": "",
                    "family": FAMILY_UNTREATABLE,
                    "requeued": False,
                    "file_paths": [],
                    "corrupt": True,
                }
            )
            continue
        bag = _bag_from_data(data, entry.stem)
        bag["corrupt"] = False
        bags.append(bag)
    return bags


def diagnose(queue_root: Path) -> dict:
    """分诊报告（纯读零写）：各族数量、代表 qid、可治愈率。

    已重投（requeued 标记在册）的袋排除在待分诊外——它的后继袋是新 qid，
    再处理旧袋会造成同一改动双份手续。
    """
    bags = load_dead_bags(queue_root)
    actionable = [b for b in bags if not b["requeued"]]
    families: dict[str, dict] = {}
    all_families = [f for f, _ in _FAMILY_MARKERS] + [FAMILY_ENV, FAMILY_UNTREATABLE]
    for family in all_families:
        members = [b for b in actionable if b["family"] == family]
        families[family] = {
            "count": len(members),
            # 代表 qid 只取 3 个：报告是给人看的锚点，不是全量清单
            "samples": [b["qid"] for b in members[:3]],
        }
    healable = sum(families[f]["count"] for f, _ in _FAMILY_MARKERS)
    auto = sum(families[f]["count"] for f in AUTO_HEALABLE_FAMILIES)
    return {
        "queue_root": str(queue_root),
        "total_dead": len(bags),
        "already_requeued": len(bags) - len(actionable),
        "actionable": len(actionable),
        "families": families,
        "healable_count": healable,
        # 可治愈率=手续五族 / 待分诊（不含已重投）
        "healable_ratio": round(healable / len(actionable), 4) if actionable else 0.0,
        "auto_healable_count": auto,
        "prescription_only_count": healable - auto,
    }


def _print_report(report: dict) -> None:
    """人读分诊报告（--scan 缺省输出）。"""
    print("=== 死信急诊分诊报告（dead_letter_doctor）===")
    print(f"队列根: {report['queue_root']}")
    print(f"死袋总数: {report['total_dead']}（已重投 {report['already_requeued']}，待分诊 {report['actionable']}）")
    print(
        f"手续五族合计（可治愈）: {report['healable_count']}"
        f"，可治愈率 {report['healable_ratio']:.1%}"
        f"（自动 {report['auto_healable_count']} / 仅处方 {report['prescription_only_count']}）"
    )
    for family, _ in _FAMILY_MARKERS:
        s = report["families"][family]
        tag = "自动" if family in AUTO_HEALABLE_FAMILIES else "仅处方"
        print(f"  {family:<14} {s['count']:>5}  [{tag}]  代表: {', '.join(s['samples']) or '—'}")
    print(f"env（requeue 即愈，非 doctor 职责）: {report['families'][FAMILY_ENV]['count']}")
    print(f"不治（人工排查，内容归因走 session_takeover_ledger）: {report['families'][FAMILY_UNTREATABLE]['count']}")
    print("下一步: 单袋处方 --prescribe <qid>；机器可定族受控执行 --apply <qid>；")
    print("        重投正门: python scripts/commit_queue.py requeue <qid>（doctor 永不代投）")


# ---------------------------------------------------------------------------
# 处方（建议面：零登记册写入）
# ---------------------------------------------------------------------------


def _common_prefix(paths: list[str]) -> str:
    """多路径公共目录前缀（posix 口径）——token 批量登记的 --prefix 推导。"""
    if not paths:
        return ""
    seg_lists = [p.replace("\\", "/").split("/")[:-1] for p in paths]
    common: list[str] = []
    for segs in zip(*seg_lists, strict=False):
        # strict=False：路径深度可不同（a/b.md vs a/c/d.md），浅路径先耗尽即停比前缀
        if len(set(segs)) == 1:
            common.append(segs[0])
        else:
            break
    return "/".join(common)


def _extract_gate_file_list(dead_reason: str) -> list[str]:
    """从死因文本提取门禁点名的文件清单（形如 ``['a.md', 'b.md']``）。

    为什么用 ast.literal_eval 而非手写 split：门禁输出是 Python repr 风格列表，
    literal_eval 是唯一保真解析通道；解析不出（非字符串列表）返回空表，由调用
    方回退袋内文件清单。
    """
    for m in _BRACKET_LIST_RE.finditer(dead_reason or ""):
        try:
            val = ast.literal_eval(m.group(0))
        except (ValueError, SyntaxError):
            continue
        if isinstance(val, list) and val and all(isinstance(x, str) for x in val):
            return [x.replace("\\", "/") for x in val]
    return []


def _derive_capability(session_id: str | None) -> str:
    """session_id → 合法 capability 缺省值。

    为什么需要缺省派生：capability 本是人工判断的"能力名"，但 MVP 要求机器可定
    ——session_id 归一（小写/下划线转连字符/剔非法字符）保证 token 字符合法且
    可追溯（token 里 created_by 同源）。人工可用 --params.capability 覆盖。
    """
    s = (session_id or "").strip().lower().replace("_", "-")
    s = re.sub(r"[^a-z0-9-]", "", s).strip("-")
    return s or "dead-letter"


def _requeue_step(qid: str, step: int) -> dict:
    """闸二落地的固定末步：正门重投，doctor 永不代投。"""
    return {
        "step": step,
        "kind": "requeue",
        "auto_executable": False,
        "command": f"python scripts/commit_queue.py requeue {qid}",
        "note": "闸二：补完手续必须走正门重投（全部门禁重过，一次不跳）；doctor 本身不执行 requeue",
    }


def _prescription_steps(bag: dict) -> list[dict]:
    """按族生成处方步骤（建议面，零执行）。"""
    qid = bag["qid"]
    reason = bag["dead_reason"]
    family = bag["family"]
    steps: list[dict] = []

    if family == FAMILY_CREATE_GUARD:
        targets = _extract_gate_file_list(reason) or list(bag["file_paths"])
        prefix = _common_prefix(targets) or "<需人工指定 --prefix>"
        cap = _derive_capability(bag["session_id"])
        base_cmd = (
            "python scripts/governance/d3_metadata/batch_creation_tokens.py "
            f"--prefix {prefix} --created-by {bag['session_id'] or '<session>'} --capability {cap}"
        )
        steps.append(
            {
                "step": 1,
                "kind": "preview_creation_tokens",
                "auto_executable": False,
                "command": f"{base_cmd} --dry-run",
                "note": "先预览计划登记清单（W4 宽前缀防呆正门，>50 条/跨一级目录须人工确认）",
            }
        )
        steps.append(
            {
                "step": 2,
                "kind": "register_creation_tokens",
                "auto_executable": True,
                "command": base_cmd,
                "note": "登记类元数据（闸一允许自动）；doctor --apply 可代执行（函数级 import 正门工具）",
            }
        )
        steps.append(_requeue_step(qid, 3))
        return steps

    if family == FAMILY_PLAIN_ZH:
        py_files = [p for p in bag["file_paths"] if p.endswith(".py")]
        targets = py_files or ["<袋内新建 .py 路径>"]
        for i, p in enumerate(targets, start=1):
            steps.append(
                {
                    "step": i,
                    "kind": "register_plain_zh",
                    "auto_executable": True,
                    "command": (
                        "python scripts/governance/d3_metadata/add_module_translation.py "
                        f"--path {p} --domain <D_域ID> --name-zh <模块中文名> "
                        "--plain-zh <大白话：做什么/解决什么/怎么做（CJK≥8，禁模板化）>"
                    ),
                    "note": "登记类元数据（闸一允许自动）；但 domain/名称/大白话需人工供稿——"
                    "--apply --params 传入 entries[] 后 doctor 代执行",
                }
            )
        steps.append(_requeue_step(qid, len(steps) + 1))
        return steps

    if family == FAMILY_R5_SUFFIX:
        steps.append(
            {
                "step": 1,
                "kind": "rename_directory",
                "auto_executable": False,
                "command": None,
                "note": "闸一：目录改名动的是业务内容，doctor 不代执行——把 _NN 数字后缀目录改为"
                "语义化名称（R5 禁数字后缀=禁多真源暗示）并更新引用",
            }
        )
        steps.append(_requeue_step(qid, 2))
        return steps

    if family == FAMILY_VOCAB:
        steps.append(
            {
                "step": 1,
                "kind": "externalize_vocab",
                "auto_executable": False,
                "command": None,
                "note": "闸一：改代码内容超出 doctor 职权——把硬编码词表移到 *_vocabulary.yaml 并动态加载",
            }
        )
        steps.append(_requeue_step(qid, 2))
        return steps

    if family == FAMILY_DEPGRAPH:
        steps.append(
            {
                "step": 1,
                "kind": "register_depgraph_node",
                "auto_executable": False,
                "command": "python scripts/governance/apply_depgraph.py（参数未确认——按其 --help 与 L1 铁律登记依赖节点）",
                "note": "闸一：依赖图登记涉及结构判断，doctor 不代执行——按 DEPGRAPH-PRE-REGISTRATION 指引补登记后转 production",
            }
        )
        steps.append(_requeue_step(qid, 2))
        return steps

    if family == FAMILY_ENV:
        steps.append(_requeue_step(qid, 1))
        return steps

    # 不治族：内容归因请走 session_takeover_ledger.triage_bag（互补分工）
    steps.append(
        {
            "step": 1,
            "kind": "manual_triage",
            "auto_executable": False,
            "command": "python scripts/commit_queue.py health（死因聚合）",
            "note": "不治族：人工排查；内容归因（八类）走 session_takeover_ledger 的 triage_bag",
        }
    )
    return steps


def build_prescription(bag: dict, operator: str) -> dict:
    """单袋处方（纯构造，零 IO）——处方是建议，不自动执行任何登记动作。"""
    return {
        "qid": bag["qid"],
        "session_id": bag["session_id"],
        "family": bag["family"],
        "dead_reason": bag["dead_reason"],
        "generated_at": _now_iso(),
        "operator": operator,
        "gate_one_note": "闸一：doctor 只生成/登记登记类元数据，被提交的业务内容一个字节不改",
        "gate_two_note": (
            f"闸二：补完手续必须走正门重投 python scripts/commit_queue.py requeue {bag['qid']}，"
            "重新过全部原门禁；doctor 本身不执行 requeue"
        ),
        "gate_three_note": (
            f"闸三：同一 (session_id, 手续族) 自动补手续最多 {MAX_AUTO_HEAL_ATTEMPTS} 次，"
            "超出转人工（dead_letter_doctor_state.json 计数）"
        ),
        "steps": _prescription_steps(bag),
    }


def _load_bag(qid: str, queue_root: Path) -> dict | None:
    """按 qid 读单袋；qid 已过白名单校验（调用方保证），此处只兜 IO/解析错。"""
    p = queue_root / "dead" / f"{qid}.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
    except (OSError, ValueError):
        return None
    return _bag_from_data(data, qid)


def prescribe(qid: str, queue_root: Path, operator: str = _DEFAULT_OPERATOR) -> tuple[int, dict]:
    """处方模式：生成处方 JSON 落 doctor_prescriptions/<qid>.json（零登记册写入）+ 审计。"""
    # qid 白名单（防路径穿越，同 requeue 入口口径——_QID_RE 是 commit_queue 真源）
    if not qid or not _cq._QID_RE.match(qid):
        return 1, {"status": "error", "detail": f"qid 非法: {qid!r}"}
    bag = _load_bag(qid, queue_root)
    if bag is None:
        return 1, {"status": "error", "detail": f"死袋不存在或不可解析: {qid}"}
    if bag["requeued"]:
        return 1, {"status": "error", "detail": f"{qid} 已重投（requeued 标记在册），勿再处理"}
    rx = build_prescription(bag, operator)
    out_dir = queue_root / _PRESCRIPTIONS_DIRNAME
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{qid}.json"
    out_path.write_text(json.dumps(rx, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    audit_append(
        queue_root,
        qid=qid,
        session_id=bag["session_id"],
        action="prescribe",
        family=bag["family"],
        result=f"处方落盘 {_PRESCRIPTIONS_DIRNAME}/{qid}.json（{len(rx['steps'])} 步）",
        operator=operator,
    )
    return 0, rx


# ---------------------------------------------------------------------------
# 状态面（闸三）与审计
# ---------------------------------------------------------------------------


def load_state(queue_root: Path) -> dict:
    """闸三计数面：{(session_id, family): count}。缺省零计数（首救放行）。"""
    p = queue_root / _STATE_FILENAME
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": 1, "counts": {}}
    if not isinstance(data, dict) or not isinstance(data.get("counts"), dict):
        return {"version": 1, "counts": {}}
    return data


def _save_state(queue_root: Path, state: dict) -> None:
    """状态落盘：tmp + os.replace 原子写（对齐 session_takeover_ledger 台账姿势）。"""
    p = queue_root / _STATE_FILENAME
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    os.replace(tmp, p)


def _gate_three_key(session_id: str | None, family: str) -> str:
    """闸三身份键=(session_id, 手续族)；session 缺失（损坏袋）归 unknown 仍受闸限。"""
    return f"{session_id or 'unknown'}::{family}"


def audit_append(
    queue_root: Path,
    *,
    qid: str,
    session_id: str | None,
    action: str,
    family: str,
    result: str,
    operator: str,
) -> None:
    """审计追加（doctor_audit.jsonl，字段 ts/qid/session_id/action/family/result/operator）。

    为什么 append 而非整写：审计是只增不减的流水（与 takeover_ledger.jsonl 同款
    语义），整写会在并发/崩溃窗口丢前史。
    """
    rec = {
        "ts": _now_iso(),
        "qid": qid,
        "session_id": session_id,
        "action": action,
        "family": family,
        "result": result,
        "operator": operator,
    }
    p = queue_root / _AUDIT_FILENAME
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _read_audit(queue_root: Path) -> list[dict]:
    """审计回读（测试/排障用；坏行跳过不抛——审计是观测面不是裁决面）。"""
    p = queue_root / _AUDIT_FILENAME
    out: list[dict] = []
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for ln in lines:
        if not ln.strip():
            continue
        try:
            out.append(json.loads(ln))
        except ValueError:
            continue
    return out


# ---------------------------------------------------------------------------
# 执行模式（--apply，默认关）：只对"机器可确定"的处方执行登记动作
# ---------------------------------------------------------------------------


def _apply_creation_token(bag: dict, params: dict) -> dict:
    """creation_token 族执行：函数级 import batch_creation_tokens 正门工具。

    闸一落地：本函数只写 capability_canonical_file_registry.yaml（登记表格），
    不碰袋内任何业务文件。写前/写后自检失败由 insert_block 抛 TokenInsertError
    （其内部已回滚），此处显式捕获折叠为 failed 结果——绝不重试（重试=二次插入）。
    """
    import scripts.governance.d3_metadata.batch_creation_tokens as bct

    reason = bag["dead_reason"]
    bag_paths = set(bag["file_paths"])
    # 目标清单首选死因点名（门禁输出=真源）；死因与袋内清单不一致=数据异常，转人工
    reason_paths = _extract_gate_file_list(reason)
    if reason_paths and not set(reason_paths) <= bag_paths:
        return {
            "status": "skipped",
            "detail": f"死因点名路径与袋内文件不一致，转人工核对: {reason_paths}",
        }
    targets = reason_paths or list(bag["file_paths"])

    # 幂等：已登记的跳过（batch 工具自身语义同源），全已登记=无事可做（不耗闸三额度）
    registered = bct.load_registered()
    todo = [p for p in targets if p not in registered]
    if not todo:
        return {"status": "nothing_to_do", "detail": "目标文件均已登记 creation_token"}

    # W4 宽前缀防呆：复用正门工具同源判据（>50 条/跨多个一级目录须人工显式确认）
    wide = bct._wide_prefix_issues(todo)
    if wide:
        return {"status": "skipped", "detail": "W4 宽前缀防呆（同源判据）: " + "；".join(wide)}

    created_by = params.get("created_by") or bag["session_id"] or _DEFAULT_OPERATOR
    capability = params.get("capability") or _derive_capability(bag["session_id"])
    # token 日期取 UTC 当日（经 epoch 中转，禁 naive now）
    today = datetime.fromtimestamp(time.time(), tz=timezone.utc).strftime("%Y%m%d")
    # 能力名预检（复用正门 _TOKEN_RE，防 build_block 内 sys.exit 逃逸库层契约）
    if not bct._TOKEN_RE.match(f"{capability}-x-{today}"):
        return {
            "status": "skipped",
            "detail": f"capability 缺省派生不合法（{capability!r}）——--params 人工指定后重试",
        }

    try:
        block = bct.build_block(
            todo,
            created_by,
            capability,
            today,
            merge_evaluation=params.get("merge_evaluation"),
        )
        # 锚点解析对齐 CLI 正门姿势：段内同名 capability 优先，回退段内最后一条
        text = bct._REGISTRY.read_text(encoding="utf-8")
        sec_start, sec_end = bct._creation_tokens_section(text)
        anchor = bct.resolve_anchor(text[sec_start:sec_end], params.get("anchor_capability") or capability)
        bct.insert_block(block, anchor, expect_files=todo)
    except bct.TokenInsertError as exc:
        # 写前/写后自检失败：insert_block 已自行回滚（或声明未回滚需人工分诊）
        return {"status": "failed", "detail": f"batch_creation_tokens 自检失败: {exc}"}
    except SystemExit as exc:
        # build_block 对非法 token 走 sys.exit——库层契约要求折叠为结果不杀进程
        return {"status": "failed", "detail": f"build_block 拒绝（exit {exc.code}）: token 格式非法"}
    return {
        "status": "ok",
        "detail": f"已登记 {len(todo)} 条 creation_token（capability={capability}, 锚点={anchor}）",
        "files": todo,
    }


def _apply_plain_zh(bag: dict, params: dict) -> dict:
    """plain_zh 族执行：函数级 import add_module_translation 正门工具。

    闸一落地：只写 module_translation_registry.yaml（登记表格）。大白话内容必须
    人工经 --params 供稿（doctor 不生成文案——机器生成的简介必撞 is_generic 模板闸）。
    """
    import scripts.governance.d3_metadata.add_module_translation as amt

    entries = params.get("entries")
    if not isinstance(entries, list) or not entries:
        return {
            "status": "skipped",
            "detail": "plain_zh 需人工供稿：--params JSON 的 entries[]"
            "（module_path/domain_id/name_zh/plain_zh，可先 --prescribe 看命令模板）",
        }
    bag_paths = {p.replace("\\", "/") for p in bag["file_paths"]}
    normalized: list[dict] = []
    for e in entries:
        if not isinstance(e, dict):
            return {"status": "invalid_params", "detail": f"entries 元素非 object: {e!r}"}
        missing = [k for k in ("module_path", "domain_id", "name_zh", "plain_zh") if not (e.get(k) or "").strip()]
        if missing:
            return {"status": "invalid_params", "detail": f"entries 缺必填字段 {missing}"}
        mp = str(e["module_path"]).replace("\\", "/")
        if mp not in bag_paths:
            return {
                "status": "invalid_params",
                "detail": f"entries.module_path {mp} 不在袋内文件清单（闸一：只登记袋内模块，防张冠李戴）",
            }
        ne = dict(e)
        ne["module_path"] = mp
        normalized.append(ne)

    results: list[dict] = []
    for e in normalized:
        # add_translation 内含写前校验（CJK≥8/拒模板）+ CAS 写 + 写后解析校验
        code, msg = amt.add_translation(e)
        results.append({"module_path": e["module_path"], "code": code, "message": msg})
        if code != 0:
            return {
                "status": "failed",
                "detail": f"add_translation 返回 {code}: {msg}",
                "results": results,
            }
    return {
        "status": "ok",
        "detail": f"已登记 {len(normalized)} 条翻译（{'; '.join(r['module_path'] for r in results)}）",
        "results": results,
    }


def apply_healing(
    qid: str,
    queue_root: Path,
    operator: str = _DEFAULT_OPERATOR,
    params: dict | None = None,
) -> tuple[int, dict]:
    """执行模式入口：闸三检查 → 族分派 → 审计/计数。

    结果 status 语义（与 ERROR_CONTRACT 对齐）：
      ok=已执行登记（耗额度，exit 0）/ failed=执行失败（耗额度，exit 3）/
      nothing_to_do=幂等无动作（不耗额度，exit 0）/ skipped=设计内跳过（不耗额度，exit 0）/
      invalid_params=调用方参数错（不耗额度，exit 1）/ refused=闸三拒绝（exit 2）。
    """
    params = params or {}
    if not qid or not _cq._QID_RE.match(qid):
        return 1, {"status": "error", "detail": f"qid 非法: {qid!r}"}
    bag = _load_bag(qid, queue_root)
    if bag is None:
        return 1, {"status": "error", "detail": f"死袋不存在或不可解析: {qid}"}
    if bag["requeued"]:
        return 1, {"status": "error", "detail": f"{qid} 已重投（requeued 标记在册），勿再处理"}

    family = bag["family"]

    # 闸一：非登记类族永不自动执行（改名/改内容/改依赖图超出"只动表格"）
    if family not in AUTO_HEALABLE_FAMILIES:
        detail = (
            f"闸一：{family} 族治法涉及改名/改内容/改依赖图，doctor 只出处方不自动执行（--prescribe {qid} 取处方单）"
        )
        audit_append(
            queue_root,
            qid=qid,
            session_id=bag["session_id"],
            action="apply_skipped",
            family=family,
            result=detail,
            operator=operator,
        )
        return 0, {"status": "skipped", "family": family, "detail": detail}

    # CREATE-GUARD 的 SSOT 碰撞子族：治法是改内容（删新文件/挪目录），超闸一只出处方
    if family == FAMILY_CREATE_GUARD and any(m in bag["dead_reason"] for m in _SSOT_COLLISION_MARKERS):
        detail = "CREATE-GUARD 的能力重复/basename 碰撞子族：治法是改内容不是补手续（闸一），只出处方"
        audit_append(
            queue_root,
            qid=qid,
            session_id=bag["session_id"],
            action="apply_skipped",
            family=family,
            result=detail,
            operator=operator,
        )
        return 0, {"status": "skipped", "family": family, "detail": detail}

    # 闸三：执行前查计数——同 (session_id, 手续族) 最多救一次
    state = load_state(queue_root)
    key = _gate_three_key(bag["session_id"], family)
    used = int(state["counts"].get(key, 0))
    if used >= MAX_AUTO_HEAL_ATTEMPTS:
        detail = (
            f"闸三：({bag['session_id']}, {family}) 自动补手续已用 {used} 次（上限 {MAX_AUTO_HEAL_ATTEMPTS}），转人工"
        )
        audit_append(
            queue_root,
            qid=qid,
            session_id=bag["session_id"],
            action="apply_refused_gate3",
            family=family,
            result=detail,
            operator=operator,
        )
        return 2, {"status": "refused", "family": family, "detail": detail}

    # 执行（机器可定处方）；未预期异常折叠为 failed（额度照耗——真相是"试过没成"）
    try:
        if family == FAMILY_CREATE_GUARD:
            result = _apply_creation_token(bag, params)
        else:
            result = _apply_plain_zh(bag, params)
    except Exception as exc:  # noqa: BLE001 — 急诊台不向上抛，全部折叠进结果+审计
        result = {"status": "failed", "detail": f"未预期异常: {type(exc).__name__}: {exc}"}
    result.setdefault("family", family)

    if result["status"] == "skipped":
        audit_append(
            queue_root,
            qid=qid,
            session_id=bag["session_id"],
            action="apply_skipped",
            family=family,
            result=result["detail"],
            operator=operator,
        )
        return 0, result
    if result["status"] == "invalid_params":
        audit_append(
            queue_root,
            qid=qid,
            session_id=bag["session_id"],
            action="apply_invalid_params",
            family=family,
            result=result["detail"],
            operator=operator,
        )
        return 1, result
    if result["status"] == "nothing_to_do":
        # 幂等无动作：没发生登记动作就不消耗闸三额度（重跑仍放行，直到真写一次）
        audit_append(
            queue_root,
            qid=qid,
            session_id=bag["session_id"],
            action="apply_noop",
            family=family,
            result=result["detail"],
            operator=operator,
        )
        return 0, result

    # ok / failed：真实执行过登记尝试——无论成败都记数（"再失败转人工"语义）
    state["counts"][key] = used + 1
    state["updated_at"] = _now_iso()
    _save_state(queue_root, state)
    if result["status"] == "ok":
        audit_append(
            queue_root,
            qid=qid,
            session_id=bag["session_id"],
            action="apply_executed",
            family=family,
            result=result["detail"],
            operator=operator,
        )
        return 0, result
    audit_append(
        queue_root,
        qid=qid,
        session_id=bag["session_id"],
        action="apply_failed",
        family=family,
        result=result["detail"],
        operator=operator,
    )
    return 3, result


# ---------------------------------------------------------------------------
# CLI（argparse，风格对齐 session_takeover_ledger.main）
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：--scan（默认零写诊断）/ --prescribe / --apply。"""
    ap = argparse.ArgumentParser(
        prog="dead_letter_doctor.py",
        description="死信急诊分诊台：手续类死因先补手续再正门重投（三道铁闸：只动表格/不走捷径/只救一次）",
    )
    ap.add_argument("--scan", action="store_true", help="诊断模式（默认，零写）：五族分诊报告")
    ap.add_argument(
        "--prescribe", metavar="QID", help="处方模式：单袋处方 JSON 落 doctor_prescriptions/（建议，不执行）"
    )
    ap.add_argument("--apply", metavar="QID", help="执行模式（默认关）：只对机器可定的处方执行登记动作")
    ap.add_argument(
        "--params",
        metavar="PATH",
        help="apply 参数 JSON（plain_zh entries[] 人工供稿 / capability 等覆盖）",
    )
    ap.add_argument(
        "--queue-root",
        default=None,
        help="队列根覆盖（缺省 <repo>/.runtime/commit_queue；测试沙盘注入用）",
    )
    ap.add_argument("--operator", default=_DEFAULT_OPERATOR, help="审计操作者名（缺省 dead-letter-doctor-cli）")
    ap.add_argument("--json", action="store_true", help="--scan 输出机读 JSON")
    args = ap.parse_args(argv)

    queue_root = Path(args.queue_root).resolve() if args.queue_root else _DEFAULT_QUEUE_ROOT

    if args.prescribe and args.apply:
        print("FAIL: --prescribe 与 --apply 互斥（一次只做一种）", file=sys.stderr)
        return 1

    if args.prescribe:
        code, rx = prescribe(args.prescribe, queue_root, operator=args.operator)
        if code != 0:
            print(f"FAIL: {rx['detail']}", file=sys.stderr)
            return code
        print(
            f"OK: 处方落盘 {_PRESCRIPTIONS_DIRNAME}/{args.prescribe}.json（{rx['family']} 族，{len(rx['steps'])} 步）"
        )
        for s in rx["steps"]:
            auto = "可自动" if s["auto_executable"] else "人工"
            print(f"  step {s['step']} [{auto}] {s['kind']}: {s['command'] or s['note']}")
        return 0

    if args.apply:
        params: dict = {}
        if args.params:
            try:
                loaded = json.loads(Path(args.params).read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                print(f"FAIL: --params 不可读/不可解析: {exc}", file=sys.stderr)
                return 1
            if not isinstance(loaded, dict):
                print("FAIL: --params 顶层必须是 object", file=sys.stderr)
                return 1
            params = loaded
        code, res = apply_healing(args.apply, queue_root, operator=args.operator, params=params)
        tag = {
            "ok": "OK",
            "skipped": "SKIP",
            "nothing_to_do": "NOOP",
            "refused": "REFUSED",
            "invalid_params": "FAIL",
            "failed": "FAIL",
            "error": "FAIL",
        }.get(res.get("status"), "DONE")
        print(f"{tag}: [{res.get('family', '?')}] {res.get('detail', '')}")
        if res.get("status") not in ("ok", "skipped", "nothing_to_do"):
            print(f"（审计已留痕 doctor_audit.jsonl；处方参考 --prescribe {args.apply}）")
        return code

    # 缺省动作=诊断（零写）
    report = diagnose(queue_root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
