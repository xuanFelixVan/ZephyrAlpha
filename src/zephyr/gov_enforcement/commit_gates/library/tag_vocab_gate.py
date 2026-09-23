# [BLUEPRINT] MOD-LIB-TAGVOCAB-GATE | docs/_working/ultimate_library/12_ulib3_directive.md | §1
# [MODULE] zephyr.gov_enforcement.commit_gates.library.tag_vocab_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.gov_enforcement.commit_gates._diff_helpers (_build_own_scope, _norm_rel, _audit_foreign_staged)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（in_process_gate_registry.yaml 条目驱动）
# [STARTUP] imported by gate_auto_registrar
# [MATURITY] evolving
# [INVARIANTS] 观察期 warn-only（TAG_VOCAB_GATE_MODE="warn"，未来翻 "block" 硬阻断）——staged yaml 中资产登记 tags 出现非枚举词/不可解析别名则 WARN+审计放行；library_tag_vocabulary.yaml 缺失 fail-open 跳过（观察门不得比词库先行阻断）；staged 词库本尊时加做结构自检（重复 canonical/别名冲突=孤儿）；own-scope（宪法 §3.3）外来 staged 剔除不阻断、warn+审计；解析异常 fail-open；净零声明=词库收编 15 份内联标签簇，本闸只管"词准不准"不立平行登记表（ulib3 T7）
# [MODIFY-GUARD] gate_id="TAG-VOCAB"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——yaml/IO 异常降级 fail-open（passed=True，logger.warning）；warn 模式检出违规返回 passed=True+detail 留痕；"block" 模式才 fail-closed
# [TESTS] tests/gov_enforcement/test_tag_vocab_gate.py
# [A_module] module_id=MOD-LIB-TAGVOCAB-GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
tag_vocab_gate.py — 图书馆标签枚举门（TAG-VOCAB，ulib3 T7）

staged yaml 的资产登记 ``tags`` 列表出现**非枚举词**（不在标准词库
``library_tag_vocabulary.yaml`` 且不是可解析到唯一标准词的别名）→ WARN+审计留痕+放行
（观察期 warn-only）。staged 词库本尊时加做结构自检：重复 canonical / 别名冲突（同别名
挂多个标准词=别名孤儿）→ 同样进入 findings。

病根（第一性原理）
-----------------
资产 tags 各登记表自由发挥：同一语义多写法（翻转/反转、阻力/压力）跨表对不齐；
检索按 tag 聚合时同义分裂。词库（REG-TAGVOCAB-001）固化标准词+别名层后，
本闸把"新登记只准选词不准造词"从纪律升级为技术强制。

设计权衡
--------
1. **warn-only 起步**：存量 564 在用值中含过程性噪音（批2/rejected/layer:L0），
   观察期收集误报与噪音清单，TAG_VOCAB_GATE_MODE 翻 "block" 一行升硬。
2. **词库缺失 fail-open**：观察门不得比词库先行阻断（对标 STATE-VOCAB-REGISTRY）。
3. **own-scope**（宪法 §3.3）：外来 staged 剔除不阻断、warn+审计。
4. **priority=134**：STATE-VOCAB-REGISTRY(135) 之前唯一空档。
5. **范围**：catalogs/ 下 staged yaml（资产登记 tags 的主登记面）+ 词库本尊自检。

Usage::

    from zephyr.gov_enforcement.commit_gates.tag_vocab_gate import make_tag_vocab_gate
    registry.register(make_tag_vocab_gate())

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/t/tag_vocab_gate.yaml
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _audit_foreign_staged,
    _build_own_scope,
    _norm_rel,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final[list[str]] = ["make_tag_vocab_gate", "TAG_VOCAB_GATE_MODE", "TAG_VOCAB_REGISTRY_REL_PATH"]

TAG_VOCAB_GATE_MODE = "warn"

TAG_VOCAB_REGISTRY_REL_PATH = "docs/01_policies_and_standards/_registry/catalogs/library_tag_vocabulary.yaml"

_CATALOGS_PREFIX = "docs/01_policies_and_standards/_registry/catalogs/"

_GATE_ID = "TAG-VOCAB"


class _Vocab:
    """词库快照：canonical 集合 + 别名→标准词映射 + 自检缺陷。"""

    def __init__(self, canonical: set[str], alias_to_canonical: dict[str, str], defects: list[str]) -> None:
        self.canonical = canonical
        self.alias_to_canonical = alias_to_canonical
        self.defects = defects

    def resolve(self, tag: str) -> str | None:
        """标签 → 标准词；枚举外返回 None。"""
        if tag in self.canonical:
            return tag
        return self.alias_to_canonical.get(tag)


def _load_vocab(project_root: str) -> _Vocab | None:
    """加载词库（SSoT：yaml_utils.load_vocabulary_alias_map，D-D-05 收敛）。

    词库缺失（fail-open，debug）或损坏/结构非法（fail-open，warning，缺陷进 findings）
    返回 None——调用方跳过，绝不报错。
    """
    path = Path(project_root) / TAG_VOCAB_REGISTRY_REL_PATH
    if not path.exists():
        logger.debug("%s: 词库不存在（%s）——配套词库未落地，fail-open 跳过。", _GATE_ID, TAG_VOCAB_REGISTRY_REL_PATH)
        return None
    try:
        from zephyr.shared.io.yaml_utils import load_vocabulary_alias_map  # noqa: PLC0415 — 懒加载

        canonical, alias_map = load_vocabulary_alias_map(path, strict=True)
        return _Vocab(canonical, alias_map, [])
    except (OSError, ValueError, yaml.YAMLError) as e:
        # 结构非法（重复 canonical/别名冲突/YAML 损坏）= 词库自身缺陷，进 findings 展示而非崩溃
        logger.warning("%s: 词库结构缺陷（%s: %s）——按缺陷呈现。", _GATE_ID, type(e).__name__, e)
        return _Vocab(set(), {}, [str(e)])


def _collect_yaml_tags(node: object, out: list[str]) -> None:
    """递归收集 yaml 结构中键名 tags/tag 的字符串列表值。"""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("tags", "tag") and isinstance(v, list):
                out.extend(str(t).strip() for t in v if isinstance(t, str) and str(t).strip())
            _collect_yaml_tags(v, out)
    elif isinstance(node, list):
        for item in node:
            _collect_yaml_tags(item, out)


def _audit_findings(gateway, findings: dict[str, list[str]]) -> None:
    """审计落盘（non-blocking）：供 Owner 回评误报率与升硬决策。"""
    try:
        from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

        audit_dir = Path(gateway.project_root) / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        rec = {
            "timestamp": now_utc().isoformat(),
            "gate": _GATE_ID,
            "mode": TAG_VOCAB_GATE_MODE,
            "findings": findings,
        }
        with (audit_dir / "tag_vocab.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计失败不阻断（ERROR_CONTRACT）
        logger.debug("%s audit write failed (non-blocking)", _GATE_ID, exc_info=True)


def _resolve_wt_root(gateway) -> str:
    """worktree 根解析（回退 project_root，fail-open；与 state_vocab 实现差异=异常收窄 OSError）。"""
    try:
        toplevel = gateway.run_git(["git", "rev-parse", "--show-toplevel"])
        if toplevel.returncode == 0:
            return toplevel.stdout.strip()
    except OSError:  # 窄化捕获——非 git 环境回退 project_root（fail-open）
        pass
    return getattr(gateway, "project_root", None) or "."


def _scan_yaml_files_for_findings(gateway, yaml_files: list[str], vocab: _Vocab) -> dict[str, list[str]]:
    """逐文件扫描 tags 枚举合规（单文件失败降级跳过）。"""
    findings: dict[str, list[str]] = {}
    wt_root = _resolve_wt_root(gateway)
    for rel_path in yaml_files:
        abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(wt_root, rel_path.replace("/", os.sep))
        is_vocab_self = rel_path == TAG_VOCAB_REGISTRY_REL_PATH
        if not os.path.isfile(abs_path):
            continue
        try:
            data = yaml.safe_load(Path(abs_path).read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001 — 解析失败跳过（SYNTAX 面归他闸）
            logger.warning("%s: 跳过文件 %s (%s: %s)", _GATE_ID, abs_path, type(e).__name__, e)
            continue
        if data is None:
            continue
        file_findings: list[str] = []
        if is_vocab_self:
            file_findings.extend(vocab.defects)
        tags: list[str] = []
        _collect_yaml_tags(data, tags)
        for tag in tags:
            if vocab.resolve(tag) is None:
                file_findings.append(f"tags 非枚举：{tag}")
        if file_findings:
            findings[rel_path] = file_findings
    return findings


def make_tag_vocab_gate() -> GateSpec:
    """构造图书馆标签枚举门 GateSpec（观察期 warn 型）。

    Returns:
        GateSpec(gate_id="TAG-VOCAB", priority=134)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 词库 fail-open 前置：缺失/损坏 → 跳过（不报错）
        project_root = str(getattr(gateway, "project_root", "."))
        vocab = _load_vocab(project_root)
        if vocab is None:
            return True, ""

        # 2. staged yaml（catalogs/ 登记面 + 词库本尊），AM 态
        # _norm_rel 返回 normcase（Windows 反斜杠）形态，前缀匹配前统一转正斜杠
        yaml_files: list[str] = []
        scope_keys: dict[str, str] = {}
        for f in files:
            rel_nc = _norm_rel(gateway, f)
            rel = rel_nc.replace("\\", "/")
            scope_keys[rel] = rel_nc
            if not rel.endswith(".yaml"):
                continue
            if rel == TAG_VOCAB_REGISTRY_REL_PATH or rel.startswith(_CATALOGS_PREFIX):
                yaml_files.append(rel)
        if not yaml_files:
            return True, ""

        # 3. own-scope（宪法 §3.3）：外来 staged 剔除不阻断、warn+审计
        session_id = kwargs.get("session_id")
        own_scope = _build_own_scope(gateway, files, session_id)
        if own_scope is not None:
            own_files = [f for f in yaml_files if scope_keys[f] in own_scope]
            foreign_staged = [f for f in yaml_files if scope_keys[f] not in own_scope]
            if foreign_staged:
                _audit_foreign_staged(gateway, session_id, foreign_staged, gate_name=_GATE_ID)
                logger.warning(
                    "%s: %d 个外来 session staged 文件未检查（warn+审计，不阻断）: %s",
                    _GATE_ID,
                    len(foreign_staged),
                    ", ".join(foreign_staged[:5]) + ("..." if len(foreign_staged) > 5 else ""),
                )
            yaml_files = own_files
            if not yaml_files:
                return True, ""

        findings = _scan_yaml_files_for_findings(gateway, yaml_files, vocab)
        if not findings:
            return True, ""

        # 5. 输出姿态照先例（STATE-VOCAB-REGISTRY）：审计留痕 + warn/branch by mode
        _audit_findings(gateway, findings)
        detail_lines = [f"  {fp}:\n" + "\n".join(f"    - {c}" for c in cs) for fp, cs in findings.items()]
        detail = (
            "TAG-VOCAB warn：tags 出现非枚举词/别名冲突（标准词库 REG-TAGVOCAB-001"
            " library_tag_vocabulary.yaml，ulib3 T7）\n"
            + "\n".join(detail_lines)
            + "\n-> 合法情形自查：①改用词库标准词或其登记别名 ②确需新词→馆员/裁定增补词库"
            "（施工 AI 只能选不能造）。误报请回评 Owner（warn 起步收集噪音清单，稳定后升硬阻断）"
        )
        if TAG_VOCAB_GATE_MODE == "block":
            logger.error("%s gate block:\n%s", _GATE_ID, detail)
            return False, detail
        logger.warning("%s gate warn-only:\n%s", _GATE_ID, detail)
        return True, detail

    return GateSpec(gate_id=_GATE_ID, check=_check, priority=134)
