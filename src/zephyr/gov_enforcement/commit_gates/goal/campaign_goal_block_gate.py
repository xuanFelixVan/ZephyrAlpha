# [BLUEPRINT] MOD-GOV-GOALGATE | docs/_working/infoaxis/00_ledger.md §3-Q7
# [MODULE] zephyr.gov_enforcement.commit_gates.goal.campaign_goal_block_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [CONSUMERS] GitCommitGateway pre-commit（新开班令目标块硬前置执法面）; 提交队列 serializer
#   （同门复用——队列落地同过本门）; gate_registry.yaml 机生投影
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] own-scope（宪法 §3.3：只对本次 commit files 执法，他会话 staged 不连坐
#   ——外来降级 warn+审计）；触发面收窄=git A 态（本笔新增）.md 且 docs/ 下且正文含开班令
#   族标记词（开班令/总包令/派工令/施工令/开工令/统筹令/开役令）——存量文件与收班册零打扰；
#   合法态=frontmatter goal_block 映射含 goal_statement＋(exam_ref|acceptance_criteria)
#   ＋campaign_ref 三要（Q5 四字段子集口径）；豁免=frontmatter goal_block_exempt:<理由≥10字>
#   （留痕在案非口头）；fail-open on git/读盘异常（禁设施瞬态误伤提交人）
# [MODIFY-GUARD] tests/gov/governance/test_campaign_goal_block_gate.py
# [STABILITY] experimental
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git diff 失败=放行＋warn；goal_block 判定只做机械解析禁语义裁量
# [TESTS] tests/gov/governance/test_campaign_goal_block_gate.py
# [A_module] module_id=MOD-GOV-GOALGATE | layer=module | stability=experimental | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-gov-goalgate-campaign-goal-block-20261013
"""开班令目标块硬前置门（CAMPAIGN-GOAL-BLOCK，Q7＝裁定#516）。

真源：docs/_working/infoaxis/00_goal_structure_research_2026_10_13.md §5（开班令目标块设为
硬前置——无目标块=门禁拦）＋ infoaxis/00_ledger.md §3-Q7（预告时刻在案）。

净零声明（宪法 §4，裁定#375）：新执法面无旧门可替代（开班令结构校验此前零覆盖）；
登记于 gate_registry 机生投影 own_scope 字段；owner 消费面=统筹派工令自我适用（上锁
先于自身——预告 30 分钟窗在 infoaxis/00_ledger.md §3-Q7 留痕）。

用法::

    from zephyr.gov_enforcement.commit_gates.goal.campaign_goal_block_gate import (
        make_campaign_goal_block_gate,
    )

    registry.register(make_campaign_goal_block_gate())

# [ALGO_FLOW]
# 层: files 集合 → 开班令面识别（A 态 .md＋docs/＋前 80 行令词）→ frontmatter 三要/豁免校验
# - 触发面: 本笔新增 .md（git diff-filter=A）且 docs/ 且令词命中
# - 判定: goal_block{goal_statement＋campaign_ref＋(exam_ref|acceptance_criteria)} 或 goal_block_exempt≥10 字
# - 失败集: 缺块违规列表 → 阻断；git/解析异常 fail-open 放行
# [/ALGO_FLOW]
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import _audit_foreign_staged
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_campaign_goal_block_gate"]

#: 开班令族标记词（正文前 80 行命中任一即视为开班令面；大小写不敏感不适用中文，精确词表）
_ORDER_MARKERS: tuple[str, ...] = (
    "开班令",
    "总包令",
    "派工令",
    "施工令",
    "开工令",
    "统筹令",
    "开役令",
)

#: goal_block 合法三要（Q5 四字段子集：goal_statement 必＋exam/acceptance 二选一必＋campaign_ref 必）
_GOAL_REQUIRED_KEYS = ("goal_statement", "campaign_ref")
_GOAL_ALT_KEYS = ("exam_ref", "acceptance_criteria")

_RE_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def _is_new_order_md(gateway, rel: str) -> bool:
    """A 态（本笔新增）＋docs/ 下 ＋.md＋正文含开班令族标记词。fail-open on git/读盘。"""
    if not rel.endswith(".md") or not rel.startswith("docs/"):
        return False
    try:
        r = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A", "--", rel])
        if r.returncode != 0 or rel.replace("\\", "/") not in (r.stdout or ""):
            return False
        text = Path(rel).read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 — 设施瞬态 fail-open
        logger.warning("CAMPAIGN-GOAL-BLOCK fail-open: %s 探测异常 %s", rel, exc)
        return False
    head = "\n".join(text.split("\n")[:80])
    return any(m in head for m in _ORDER_MARKERS)


def _goal_block_ok(rel: str) -> tuple[bool, str]:
    """frontmatter goal_block 三要校验＋豁免标记。"""
    try:
        text = Path(rel).read_text(encoding="utf-8", errors="replace")
        m = _RE_FRONTMATTER.match(text)
        if not m:
            return False, "缺 frontmatter goal_block"
        fm = yaml.safe_load(m.group(1)) or {}
        exempt = fm.get("goal_block_exempt")
        if isinstance(exempt, str) and len(exempt.strip()) >= 10:
            return True, f"EXEMPT（留痕）: {exempt.strip()[:80]}"
        gb = fm.get("goal_block")
        if not isinstance(gb, dict):
            return False, "frontmatter 缺 goal_block 映射"
        miss = [k for k in _GOAL_REQUIRED_KEYS if not str(gb.get(k) or "").strip()]
        if not any(str(gb.get(k) or "").strip() for k in _GOAL_ALT_KEYS):
            miss.append("exam_ref|acceptance_criteria")
        if miss:
            return False, f"goal_block 缺要件 {miss}"
        return True, ""
    except Exception as exc:  # noqa: BLE001 — 解析异常 fail-open（禁误伤）
        logger.warning("CAMPAIGN-GOAL-BLOCK fail-open: %s 解析异常 %s", rel, exc)
        return True, ""


def make_campaign_goal_block_gate() -> GateSpec:
    """构造开班令目标块硬前置 GateSpec（硬阻断型，own-scope，priority=142）。"""

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        session_id = str(kwargs.get("session_id") or "")
        own = [f.replace("\\", "/") for f in (files or [])]
        foreign: list[str] = []
        if not own:  # 无清单退回全 staged（保守面不改宽；外来分离同族门惯例）
            try:
                r = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
                staged = (
                    [f.replace("\\", "/") for f in (r.stdout or "").strip().splitlines() if f]
                    if r.returncode == 0
                    else []
                )
            except Exception:  # noqa: BLE001
                staged = []
            own, foreign = [f for f in staged if f.endswith(".md") and f.startswith("docs/")], []
        if not own:
            return True, ""
        if foreign:
            _audit_foreign_staged(gateway, session_id, foreign, gate_name="CAMPAIGN-GOAL-BLOCK")
        violations: list[str] = []
        for rel in own:
            if not _is_new_order_md(gateway, rel):
                continue
            ok, why = _goal_block_ok(rel)
            if not ok:
                violations.append(f"  {rel}: {why}")
        if violations:
            detail = (
                "CAMPAIGN-GOAL-BLOCK：新开班令缺目标块（Q7＝裁定#516：开班令必须带 goal_block，\n"
                "  无目标块的新开班令=拦，本令之后的令自我适用）。\n"
                "  合法形态=frontmatter goal_block: {goal_statement, exam_ref|acceptance_criteria, campaign_ref}\n"
                "  （样例=docs/_working/infoaxis/00_ledger.md）。\n"
                "  确属豁免（如收班册/纯归档件）：frontmatter 写 goal_block_exempt: <理由≥10字> 留痕放行。\n"
                + "\n".join(violations)
            )
            return False, detail
        return True, ""

    return GateSpec(gate_id="CAMPAIGN-GOAL-BLOCK", check=_check, priority=142)
