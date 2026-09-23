# [BLUEPRINT] MOD-LIB-BLOODGATE | docs/_working/ultimate_library/12_ulib3_directive.md | §1
# [MODULE] zephyr.gov_enforcement.commit_gates.library.library_blood_flesh_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.gov_enforcement.commit_gates.translation_coverage_gate (_is_in_scope); zephyr.gov_enforcement.commit_gates._diff_helpers (_build_own_scope, _norm_rel, _audit_foreign_staged)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（in_process_gate_registry.yaml 条目驱动）
# [STARTUP] imported by gate_auto_registrar
# [MATURITY] evolving
# [INVARIANTS] 观察期 warn-only（BLOOD_FLESH_GATE_MODE="warn"，未来翻 "block" 硬阻断）——"新资产登记必填血肉"（title_zh/plain_zh，08 字段词典 §1 人读描述区）：A 面=staged 新增 .py（范围同 TRANSLATION-COVERAGE）翻译条目 name_zh 缺失即违规；B 面=staged module_translation_registry.yaml 相对 HEAD 新增条目 name_zh/plain_zh 缺失或 generic 即违规；翻译册/加载器不可达 fail-open；plain_zh 合规检测复用 loader is_generic（与 TRANSLATION-COVERAGE 同真源）；own-scope（宪法 §3.3）外来 staged 剔除不阻断、warn+审计；净零声明=扩展既有翻译真源字段检查，不立平行登记表（ulib3 T8，千问苦力班前置件）
# [MODIFY-GUARD] gate_id="BLOOD-FLESH"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——yaml/git/loader/IO 异常降级 fail-open（passed=True，logger.warning）；warn 模式检出违规返回 passed=True+detail 留痕；"block" 模式才 fail-closed
# [TESTS] tests/gov_enforcement/test_library_blood_flesh_gate.py
# [A_module] module_id=MOD-LIB-BLOODGATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
library_blood_flesh_gate.py — 新资产登记必填血肉门（BLOOD-FLESH，ulib3 T8）

"血肉"=资产的人读描述区（08 字段词典 §1：title/one_liner/ai_contract——模块级落点=
翻译真源 module_translation_registry.yaml 的 name_zh（标题）+ plain_zh（大白话））。
两道检查面：
  A 面：staged 新增 .py（范围与 TRANSLATION-COVERAGE 完全同口径）→ 翻译条目必须带
        name_zh（plain_zh 已由 TRANSLATION-COVERAGE 硬闸负责，本闸不重复罚）。
  B 面：staged module_translation_registry.yaml 相对 HEAD **新增的条目** → name_zh
        与 plain_zh 双全且非通用模板（存量条目不追溯，bootstrap 豁免）。

病根（第一性原理）
-----------------
资产登记"有骨无肉"：只有路径/ID 没有中文标题和大白话，AI 检索命中后无法判读
"这是什么"，只能开文件重读——图书馆查询口的检索价值被抽空。千问苦力班（指令 B）
将批量补录血肉，本闸是其前置件：保证新血肉从出生就合格，不制造新欠账。

设计权衡
--------
1. **warn-only 起步**：苦力班在即，先观察误报率；BLOOD_FLESH_GATE_MODE 翻 "block" 升硬
   （对标 STATE-VOCAB-REGISTRY / FRONTEND-TRUTH-SOURCE 的 _HARD_BLOCK 先例）。
2. **与 TRANSLATION-COVERAGE 分工**：plain_zh 硬闸已存在（priority=59），本闸只补
   name_zh（A 面）与"登记册新增条目双全"（B 面），不重复检测 plain_zh 合规（A 面）；
   B 面双检因登记册条目是新资产出生点（新增条目绕过 A 面的场景=改册不建文件）。
3. **翻译册缺失/损坏 fail-open**；HEAD 版本不可读（首次提交等）→ B 面跳过。
4. **own-scope**（宪法 §3.3）：翻译册是全仓热注册表，外来 staged 剔除不阻断、warn+审计。
5. **priority=133**：TAG-VOCAB(134) 之前唯一空档。

Usage::

    from zephyr.gov_enforcement.commit_gates.library_blood_flesh_gate import (
        make_library_blood_flesh_gate,
    )
    registry.register(make_library_blood_flesh_gate())

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/l/library_blood_flesh_gate.yaml
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _audit_foreign_staged,
    _build_own_scope,
    _norm_rel,
)
from zephyr.gov_enforcement.commit_gates.translation_coverage_gate import _is_in_scope
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__: Final[list[str]] = ["make_library_blood_flesh_gate", "BLOOD_FLESH_GATE_MODE", "TRANSLATION_REGISTRY_REL_PATH"]

BLOOD_FLESH_GATE_MODE = "warn"

TRANSLATION_REGISTRY_REL_PATH = "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"

_GATE_ID = "BLOOD-FLESH"

# plain_zh 最低 CJK（与 TRANSLATION-COVERAGE 同基线）
_MIN_CJK = 8


def _cjk_len(s: str) -> int:
    """统计 CJK 字符数。"""
    import re  # noqa: PLC0415 — 小函数内联依赖

    return len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def _load_loader():
    """懒加载翻译 loader（跨 src/scripts 边界，对标 translation_coverage_gate 模式）。

    Returns:
        (get_module_translation, is_generic_plain_zh, is_generic_plain_suffix) 或 None（fail-open）。
    """
    try:
        from zephyr.shared.io.paths import REPO_ROOT

        _shared_dir = str(REPO_ROOT / "scripts" / "governance")
        if _shared_dir not in sys.path:
            sys.path.insert(0, _shared_dir)
        from _shared.module_translation_loader import (
            get_module_translation,
            is_generic_plain_suffix,
            is_generic_plain_zh,
        )
        return get_module_translation, is_generic_plain_zh, is_generic_plain_suffix
    except Exception as e:  # noqa: BLE001 — loader 不可达=环境异常，fail-open
        logger.warning("%s: 翻译 loader 不可达（%s: %s）——fail-open。", _GATE_ID, type(e).__name__, e)
        return None


def _load_staged_new_py_files(gateway, files: list[str]) -> list[str]:
    """本 commit 内 staged 新增 .py（范围同 TRANSLATION-COVERAGE）。"""
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        if diff_result.returncode != 0:
            return []
    except Exception as e:  # noqa: BLE001 — git 异常 fail-open
        logger.warning("%s: git diff 异常（%s: %s）——A 面跳过。", _GATE_ID, type(e).__name__, e)
        return []
    commit_files_rel: set[str] = set()
    for f in files:
        try:
            commit_files_rel.add(os.path.relpath(f, str(gateway.project_root)).replace("\\", "/"))
        except (ValueError, OSError):
            continue
    return [
        line.strip().replace("\\", "/")
        for line in diff_result.stdout.strip().splitlines()
        if line.strip() and line.strip().endswith(".py") and _is_in_scope(line.strip().replace("\\", "/"))
        and line.strip().replace("\\", "/") in commit_files_rel
    ]


def _parse_registry_entries(content: str) -> dict[str, dict[str, Any]]:
    """解析翻译册 YAML → {module_path: entry}。损坏返回 {}。"""
    try:
        data = yaml.safe_load(content) or {}
    except Exception as e:  # noqa: BLE001 — 损坏 fail-open
        logger.warning("%s: 翻译册解析失败（%s: %s）——B 面跳过。", _GATE_ID, type(e).__name__, e)
        return {}
    return {
        (e.get("module_path") or "").strip(): e
        for e in (data.get("entries") or [])
        if isinstance(e, dict) and (e.get("module_path") or "").strip()
    }


def _audit_findings(gateway, findings: dict[str, list[str]]) -> None:
    """审计落盘（non-blocking）。"""
    try:
        from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

        audit_dir = Path(gateway.project_root) / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        rec = {
            "timestamp": now_utc().isoformat(),
            "gate": _GATE_ID,
            "mode": BLOOD_FLESH_GATE_MODE,
            "findings": findings,
        }
        with (audit_dir / "library_blood_flesh.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计失败不阻断（ERROR_CONTRACT）
        logger.debug("%s audit write failed (non-blocking)", _GATE_ID, exc_info=True)


def _collect_face_a_findings(gateway, files: list[str], get_module_translation) -> dict[str, list[str]]:
    """A 面：staged 新增 .py 须带 name_zh（plain_zh 归 TRANSLATION-COVERAGE 硬闸）。"""
    findings: dict[str, list[str]] = {}
    for file_path in _load_staged_new_py_files(gateway, files):
        try:
            trans = get_module_translation(file_path)
        except Exception as e:  # noqa: BLE001 — 查询异常 fail-open 此文件
            logger.warning("%s: 翻译查询异常（%s: %s）file=%s。", _GATE_ID, type(e).__name__, e, file_path)
            continue
        if not trans or not (trans.get("name_zh") or "").strip():
            findings.setdefault(file_path, []).append("A 面：无 name_zh 中文标题（血肉缺，add_module_translation.py 补录）")
    return findings


def _collect_face_b_findings(
    gateway, files: list[str], session_id: str | None, loader=None
) -> dict[str, list[str]]:
    """B 面：翻译册 staged 变更时，相对 HEAD 新增条目须血肉双全。"""
    findings: dict[str, list[str]] = {}
    wt_root = gateway.project_root
    try:
        rel_reg = _norm_rel(gateway, str(Path(wt_root) / TRANSLATION_REGISTRY_REL_PATH))
    except Exception:  # noqa: BLE001
        rel_reg = TRANSLATION_REGISTRY_REL_PATH
    staged_reg = any(_norm_rel(gateway, f) == rel_reg for f in files)
    own_scope = _build_own_scope(gateway, files, session_id)
    if staged_reg and own_scope is not None and rel_reg not in own_scope:
        _audit_foreign_staged(gateway, session_id, [rel_reg], gate_name=_GATE_ID)
        logger.warning("%s: 翻译册为外来 staged 变更，B 面跳过（warn+审计）。", _GATE_ID)
        return findings
    if not staged_reg:
        return findings
    reg_abs = Path(wt_root) / TRANSLATION_REGISTRY_REL_PATH
    try:
        head_result = gateway.run_git(["git", "show", f"HEAD:{TRANSLATION_REGISTRY_REL_PATH}"])
        # rc!=0（首次提交等 HEAD 无此文件）=不可读 → None 跳过 B 面；
        # 与"HEAD 有但为空册"（{}=全部视为新增）语义区分
        head_entries = _parse_registry_entries(head_result.stdout) if head_result.returncode == 0 else None
    except Exception as e:  # noqa: BLE001 — HEAD 不可读（首次提交等）B 面跳过
        logger.warning("%s: HEAD 翻译册不可读（%s: %s）——B 面跳过。", _GATE_ID, type(e).__name__, e)
        head_entries = None
    if head_entries is None:
        return findings
    _, is_generic_plain_zh, is_generic_plain_suffix = loader
    staged_entries = _parse_registry_entries(reg_abs.read_text(encoding="utf-8"))
    for module_path, entry in staged_entries.items():
        if module_path in head_entries:
            continue  # 存量条目不追溯（bootstrap 豁免）
        findings.setdefault(TRANSLATION_REGISTRY_REL_PATH, []).extend(
            _entry_blood_defects(module_path, entry, is_generic_plain_zh, is_generic_plain_suffix)
        )
    return findings


def _entry_blood_defects(
    module_path: str, entry: dict[str, Any], is_generic_plain_zh, is_generic_plain_suffix
) -> list[str]:
    """单条目血肉缺陷列表（空列表=合格）。"""
    defects: list[str] = []
    name_zh = (entry.get("name_zh") or "").strip()
    plain = (entry.get("plain_zh") or "").strip()
    if not name_zh:
        defects.append(f"B 面：新增条目 {module_path} 无 name_zh")
    if not plain:
        defects.append(f"B 面：新增条目 {module_path} 无 plain_zh")
    elif _cjk_len(plain) < _MIN_CJK:
        defects.append(f"B 面：新增条目 {module_path} plain_zh CJK<{_MIN_CJK}")
    elif is_generic_plain_zh(plain) or is_generic_plain_suffix(plain, name_zh):
        defects.append(f"B 面：新增条目 {module_path} plain_zh 通用模板")
    return defects


def make_library_blood_flesh_gate() -> GateSpec:
    """构造新资产登记必填血肉门 GateSpec（观察期 warn 型）。

    Returns:
        GateSpec(gate_id="BLOOD-FLESH", priority=133)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        loader = _load_loader()
        if loader is None:
            return True, ""
        get_module_translation, is_generic_plain_zh, is_generic_plain_suffix = loader

        # ---- A 面：staged 新增 .py 须带 name_zh；B 面：翻译册新增条目血肉双全 ----
        findings = _collect_face_a_findings(gateway, files, get_module_translation)
        face_b = _collect_face_b_findings(gateway, files, kwargs.get("session_id"), loader)
        for line in face_b.get(TRANSLATION_REGISTRY_REL_PATH, []):
            findings.setdefault(TRANSLATION_REGISTRY_REL_PATH, []).append(line)

        if not findings:
            return True, ""

        _audit_findings(gateway, findings)
        detail_lines = [f"  {fp}:\n" + "\n".join(f"    - {c}" for c in cs) for fp, cs in findings.items()]
        detail = (
            "BLOOD-FLESH warn：新资产登记缺血肉（name_zh 中文标题/plain_zh 大白话，08 字段词典 §1 人读描述区，"
            "ulib3 T8 千问苦力班前置件）\n"
            + "\n".join(detail_lines)
            + "\n-> 修复：python scripts/governance/d3_metadata/add_module_translation.py "
            "--path <file> --domain <D_*> --name-zh <中文名> --plain-zh <大白话>。SOP="
            "docs/01_policies_and_standards/sop/library_sop/blood_flesh_cataloging_sop.md。"
            "误报请回评 Owner（warn 起步，稳定后升硬阻断）"
        )
        if BLOOD_FLESH_GATE_MODE == "block":
            logger.error("%s gate block:\n%s", _GATE_ID, detail)
            return False, detail
        logger.warning("%s gate warn-only:\n%s", _GATE_ID, detail)
        return True, detail

    return GateSpec(gate_id=_GATE_ID, check=_check, priority=133)
