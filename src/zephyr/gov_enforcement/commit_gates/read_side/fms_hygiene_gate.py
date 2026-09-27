# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.read_side.fms_hygiene_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.gov_enforcement.commit_gates._diff_helpers (_split_own_foreign, _read_staged_file, _read_head_file, _repo_state_has_file); zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate (_DOC_REF_BROKEN_SKIP_DIRS, _is_in_skip_dir——trae_028 skip_dirs_docs SSoT 复用，单写者); zephyr.gov_enforcement.commit_gates.read_side.fms_ref_extractor (共享提取器——与基线生成器机械同源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（in_process_gate_registry.yaml 条目驱动，files_trigger=[".md",".yaml"]）
# [STARTUP] imported by gate_auto_registrar
# [MATURITY] evolving
# [INVARIANTS] FMS-HYGIENE 读侧执法门（priority=138 实测空档）四查类：①HYGIENE-DEADREF-NEW 死引用棘轮——staged md/yaml ∩ own-scope，共享提取器取引用，存在性探针 _repo_state_has_file（裁定#279 观测面），当前引用−HEAD引用=新增（dangling_reference_gate 先例），新增死引用且不在基线册→违规，基线命中=存量豁免；②HYGIENE-ASCII-NEW 新增引用含非 ASCII（S3 ASCII 政策配套，只拦新增无豁免）；③HYGIENE-PERM-EPHEMERAL 永久侧文件新增引用指向 _working/.runtime/session_logs（五支柱 4 生命周期隔离执法面，基线 B 类命中豁免）；④HYGIENE-CAS-RESIDUE 引用匹配 CAS 残渣形态 .tmp（基线 E1 命中豁免）。与 DOC-REF-BROKEN 净零分工立法（S1 §3.6）：md_link 形态的存在性判定归彼门，本门只查裸路径/反引号/表格形态死引用；模板占位形态提取层豁免（A 类 196 实证形态内置提取器）；FMS_HYGIENE_GATE_MODE="warn" 起步（tag_vocab_gate 同构一行翻 "block" 升硬）；own-scope（宪法 §3）外来 staged 剔除不阻断 warn+审计（_split_own_foreign）；tests/ 区 is_test_exempt 豁免；skip-dirs 复用 trae_028 n16 SSoT（doc_ref_broken_gate 同源 import，fail-open fallback）；无行内 noqa 通道（逃逸唯一合法路径=修引用或基线册收录+Owner 裁定，路径类引用无 noqa——docs 是数据面禁嵌指令注释）；基线册进程级缓存（noqa_validation_gate 同款）；审计落 .runtime/gate_audit/fms_hygiene.jsonl
# [MODIFY-GUARD] gate_id="FMS-HYGIENE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；FMS_HYGIENE_GATE_MODE 常量
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git/IO/解析异常降级 fail-open（passed=True，logger.warning，环境异常非违规）；基线册缺失/损坏=豁免面为空（更严不更宽，warn 留痕）；warn 模式检出违规 passed=True+detail+审计留痕；"block" 模式检出违规 fail-closed（passed=False）
# [TESTS] tests/gov_enforcement/read_side/test_fms_hygiene_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
fms_hygiene_gate.py — FMS 读侧文件卫生门（FMS-HYGIENE，四查类）

文件管理体系大改造战役 B1 批交付（S1_reference_integrity 簿 §4.1 施工处方）。
读侧=文档/登记面对盘面路径的**引用**卫生：死引用是文档信任度的第一杀手
（S1 挖矿实测存量死引用 2,498 条 / 引用全集 10,683 条，23.4%）。

四查类（每查类判定/豁免/fail 语义与现行门家族同构）
----------------------------------------------------
1. **HYGIENE-DEADREF-NEW（棘轮）**：新增引用目标不存在（git 仓库态探针）且
   不在基线册。棘轮=只拦净新增：``当前引用 − HEAD 引用 = 新增``，存量死引用
   走基线册豁免（monotonic_shrink，只许逐批缩小）；md_link 形态不在本查类
   （DOC-REF-BROKEN 净零分工，远期配对退役）。
2. **HYGIENE-ASCII-NEW**：新增引用 token 含非 ASCII（S3 ASCII 政策配套，
   只拦新增不追溯，无豁免通道）。
3. **HYGIENE-PERM-EPHEMERAL**：永久侧 referrer 新增引用指向临时区
   （_working/.runtime/session_logs）——引用必随 TTL 腐烂成死引用，事前拦截；
   基线 B 类命中豁免（_working 内部互引随 TTL 自然消亡，不修腐烂品）。
4. **HYGIENE-CAS-RESIDUE**：引用匹配 CAS 残渣形态（safe_write_text 崩溃残渣
   被文档当真源引用）；基线 E1 命中豁免，修复指引指向 S2 残渣清零。

设计权衡
--------
1. **warn 起步两段制**：FMS_HYGIENE_GATE_MODE="warn"（误报率连续两轮=0 才翻
   "block"，S1 §4.4 风险 5；tag_vocab_gate 同构升硬机制）。
2. **观测面=git 仓库态**（裁定#279 同盲区家族）：内容读 staged blob、目标
   存在性走 index/HEAD——序列化器落地 worktree 未 checkout 的同批目标不误报。
3. **单写者提取器**：与基线生成器共用 fms_ref_extractor——基线收录键与门拦截
   键机械同字符串，杜绝口径漂移（S1 簿硬约束）。
4. **净零**：不立平行豁免登记表（存量豁免唯一通道=基线册）；与 DOC-REF-BROKEN
   分工立法替代功能重复；挖矿 .csv 由基线册+生成器收编替代。

Usage::

    from zephyr.gov_enforcement.commit_gates.read_side.fms_hygiene_gate import (
        make_fms_hygiene_gate,
    )

    registry.register(make_fms_hygiene_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/r/read_side_fms_hygiene_gate.yaml
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _read_head_file,
    _read_staged_file,
    _repo_state_has_file,
    _split_own_foreign,
)
from zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate import (
    _DOC_REF_BROKEN_SKIP_DIRS,
    _get_worktree_root,
    _is_in_skip_dir,
)
from zephyr.gov_enforcement.commit_gates.read_side.fms_ref_extractor import (
    RefHit,
    extract_refs,
    is_cas_residue,
    is_ephemeral_target,
    is_permanent_referrer,
    is_template_form,
    normalize_ref,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__: Final = [
    "make_fms_hygiene_gate",
    "FMS_HYGIENE_GATE_MODE",
    "FMS_BASELINE_REL_PATH",
]

# warn→block 两段制（S1 §4.1 文件 3 / tag_vocab_gate 同构）：误报率连续两轮=0 翻 "block"
FMS_HYGIENE_GATE_MODE = "warn"

FMS_BASELINE_REL_PATH = "docs/01_policies_and_standards/_registry/catalogs/fms_deadref_baseline.yaml"

_GATE_ID = "FMS-HYGIENE"
_PRIORITY = 138  # 实测空档（137/139 均占用，S1 簿 §4.1 文件 3）

_DOC_EXTS = (".md", ".yaml", ".yml")

# 违规查类标签（detail/审计用）
_CLASS_DEADREF = "HYGIENE-DEADREF-NEW"
_CLASS_ASCII = "HYGIENE-ASCII-NEW"
_CLASS_PERM_EPHEMERAL = "HYGIENE-PERM-EPHEMERAL"
_CLASS_CAS = "HYGIENE-CAS-RESIDUE"

# 基线册进程级缓存（noqa_validation_gate._REGISTRY_CACHE 同款；key=normcase 项目根，
# 测试 tmp_path 多根互不串扰）
_BASELINE_CACHE: dict[str, frozenset[str]] = {}


def _reset_baseline_cache() -> None:
    """清空基线缓存（测试隔离钩子；生产进程内基线册恒定无需调用）。"""
    _BASELINE_CACHE.clear()


def _load_baseline_refs(project_root: str) -> frozenset[str]:
    """加载棘轮基线册收录的存量引用键集合（fail-open：缺失/损坏=空豁免面，更严不更宽）。

    基线缺失（首跑前）≠ 检测失效：棘轮的 HEAD 差分仍拦真新增，只是无存量豁免面；
    解析失败 warn 留痕（基线是 catalogs 热册，损坏属事故面应显性暴露）。
    """
    key = os.path.normcase(str(project_root))
    if key in _BASELINE_CACHE:
        return _BASELINE_CACHE[key]
    refs: set[str] = set()
    path = Path(project_root) / FMS_BASELINE_REL_PATH
    if path.exists():
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for entry in data.get("entries") or []:
                if isinstance(entry, dict) and entry.get("ref"):
                    refs.add(normalize_ref(str(entry["ref"])))
        except Exception as e:  # noqa: BLE001 — 基线损坏=空豁免面（fail-open 不阻断 commit 主链）
            logger.warning("%s: 基线册解析失败（%s: %s）——豁免面置空（更严口径）。", _GATE_ID, type(e).__name__, e)
    else:
        logger.debug("%s: 基线册不存在（%s）——豁免面为空，棘轮仍拦真新增。", _GATE_ID, FMS_BASELINE_REL_PATH)
    frozen = frozenset(refs)
    _BASELINE_CACHE[key] = frozen
    return frozen


def _get_staged_doc_files(gateway) -> list[str] | None:
    """获取 staged 新增/修改的读侧文件（.md/.yaml/.yml，fail-open：异常返回 None=检测器失效）。"""
    try:
        result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if result.returncode != 0:
            logger.warning("%s fail-open: git diff 失败(rc=%d)，检测器失效。", _GATE_ID, result.returncode)
            return None
        staged = result.stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001 — 环境异常非违规（ERROR_CONTRACT）
        logger.warning(
            "%s fail-open: git diff 异常(%s: %s)，检测器失效。", _GATE_ID, type(e).__name__, e, exc_info=True
        )
        return None
    return [f.replace("\\", "/") for f in staged if f and f.endswith(_DOC_EXTS)]


def _read_file_content(gateway, rel: str, wt_root: str) -> str | None:
    """读文件内容：staged blob 优先（裁定#279 观测面），磁盘降级；两者皆败返回 None（跳过）。"""
    content = _read_staged_file(gateway, rel)
    if content is not None:
        return content
    abs_path = os.path.join(wt_root, rel.replace("/", os.sep))
    try:
        with open(abs_path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError as e:
        logger.warning("%s: 跳过文件 %s（读取失败 %s: %s）。", _GATE_ID, rel, type(e).__name__, e)
        return None


def _new_refs_of_file(gateway, rel: str, wt_root: str) -> dict[str, frozenset[str]] | None:
    """计算单文件净新增引用：staged token→形态集 − HEAD token 集。

    HEAD 无此文件（新增文件）= 全部引用皆新增（dangling_reference_gate 先例
    `head_content is None → new_refs = current_refs`）。读取失败返回 None（跳过）。
    """
    content = _read_file_content(gateway, rel, wt_root)
    if content is None:
        return None
    staged_hits: list[RefHit] = extract_refs(content)
    token_forms: dict[str, set[str]] = {}
    for hit in staged_hits:
        token_forms.setdefault(hit.token, set()).add(hit.form)
    head_content = _read_head_file(gateway, rel)
    if head_content is not None:
        head_tokens = {hit.token for hit in extract_refs(head_content)}
        token_forms = {t: f for t, f in token_forms.items() if t not in head_tokens}
    return {t: frozenset(f) for t, f in token_forms.items()}


def _classify_new_ref(
    gateway, token: str, forms: frozenset[str], permanent_referrer: bool, baseline: frozenset[str]
) -> str | None:
    """单条净新增引用的四查类判定（链序 ASCII→CAS→永久引临时→死引用；模板形态已在提取层豁免）。

    Returns:
        违规查类标签；合法（含基线命中豁免）返回 None。
    """
    if not token.isascii():
        return _CLASS_ASCII  # 查类 2：无豁免通道（S3 配套，只拦新增）
    in_baseline = normalize_ref(token) in baseline
    if is_cas_residue(token):
        return None if in_baseline else _CLASS_CAS  # 查类 4：基线 E1 豁免
    if permanent_referrer and is_ephemeral_target(token):
        return None if in_baseline else _CLASS_PERM_EPHEMERAL  # 查类 3：基线 B 豁免
    # 查类 1：死引用棘轮——md_link 形态归 DOC-REF-BROKEN（净零分工，S1 §3.6），
    # 仅当该 token 的全部出现形态都不是 md_link 时才查存在性
    if forms == {"md_link"}:
        return None
    if not _repo_state_has_file(gateway, token.rstrip("/")):
        return None if in_baseline else _CLASS_DEADREF  # 查类 1：基线命中=存量豁免放行
    return None


def _audit_findings(gateway, findings: dict[str, list[str]]) -> None:
    """审计落盘（non-blocking，tag_vocab_gate._audit_findings 同款）：供 Owner 回评误报率与升硬决策。"""
    try:
        from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

        audit_dir = Path(getattr(gateway, "project_root", ".")) / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        rec = {
            "timestamp": now_utc().isoformat(),
            "gate": _GATE_ID,
            "mode": FMS_HYGIENE_GATE_MODE,
            "findings": findings,
        }
        with (audit_dir / "fms_hygiene.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计失败不阻断（ERROR_CONTRACT）
        logger.debug("%s audit write failed (non-blocking)", _GATE_ID, exc_info=True)


def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
    """FMS-HYGIENE 判定体（never raises；warn/block 双模）。"""
    try:
        staged = _get_staged_doc_files(gateway)
        if not staged:
            return True, ""
        # own-scope（宪法 §3）：只扫全暂存 ∩ 本 session；外来 staged 剔除不阻断、warn+审计
        own, _foreign = _split_own_foreign(gateway, staged, files, kwargs.get("session_id"), gate_name=_GATE_ID)
        own = [f for f in own if not is_test_exempt(f)]
        if not own:
            return True, ""
        # 草稿/归档区豁免（trae_028 n16 skip_dirs_docs SSoT，与 DOC-REF-BROKEN 同源同语义）
        own = [f for f in own if not _is_in_skip_dir(f, _DOC_REF_BROKEN_SKIP_DIRS)]
        if not own:
            return True, ""

        wt_root = _get_worktree_root(gateway)
        baseline = _load_baseline_refs(str(getattr(gateway, "project_root", ".")))

        findings: dict[str, list[str]] = {
            _CLASS_DEADREF: [],
            _CLASS_ASCII: [],
            _CLASS_PERM_EPHEMERAL: [],
            _CLASS_CAS: [],
        }
        for rel in own:
            permanent = is_permanent_referrer(rel)
            new_refs = _new_refs_of_file(gateway, rel, wt_root)
            if not new_refs:
                continue
            for token, forms in sorted(new_refs.items()):
                if is_template_form(token):
                    continue  # 模板/占位形态提取层豁免（A 类 196 实证，S1 §4.4 风险 1）
                cls = _classify_new_ref(gateway, token, forms, permanent, baseline)
                if cls:
                    findings[cls].append(f"{rel} -> {token}")

        findings = {k: v for k, v in findings.items() if v}
        if not findings:
            return True, ""

        _audit_findings(gateway, findings)
        lines = [f"  [{cls}] {item}" for cls, items in findings.items() for item in items[:20]]
        detail = (
            f"FMS-HYGIENE {FMS_HYGIENE_GATE_MODE}：读侧文件卫生四查检出新增违规"
            "（死引用棘轮/非ASCII/永久引临时/CAS残渣；基线 fms_deadref_baseline.yaml 未收录）\n"
            + "\n".join(lines)
            + "\n-> 修复：①修正引用指向真实在册路径 ②规划/迁移记录类存量语义引述走基线册收录+Owner 裁定"
            " ③CAS 残渣引用随残渣清零同灭（S2） ④路径类引用无 noqa 通道（修引用是唯一合法逃生）"
            "。误报请回评 Owner（warn 起步收集噪音清单，稳定后升硬阻断）"
        )
        if FMS_HYGIENE_GATE_MODE == "block":
            logger.error("%s gate block:\n%s", _GATE_ID, detail)
            return False, detail
        logger.warning("%s gate warn-only:\n%s", _GATE_ID, detail)
        return True, detail
    except Exception as e:  # noqa: BLE001 — ERROR_CONTRACT 兜底：判定体任何异常降级 fail-open
        logger.warning("%s fail-open: 判定体异常(%s: %s)。", _GATE_ID, type(e).__name__, e, exc_info=True)
        return True, ""


def make_fms_hygiene_gate() -> GateSpec:
    """构造 FMS 读侧文件卫生门 GateSpec（warn→block 两段制）。

    Returns:
        GateSpec(gate_id="FMS-HYGIENE", priority=138)。
        priority=138——实测空档（137/139 均占用）。
    """
    return GateSpec(gate_id=_GATE_ID, check=_check, priority=_PRIORITY)
