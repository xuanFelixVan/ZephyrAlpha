# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_build_own_scope, _norm_rel, _read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（YAML 驱动自动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 注册表结构硬化门禁——staged 版本必须 yaml.safe_load 通过 且 顶层根键唯一（yaml.compose
#   节点树判重，PyYAML 对重复根键静默取后者的盲区由本检查补上）；capability 注册表另有 di_seam_exemptions
#   末位+creation_tokens list 两断言。解析失败/结构破坏 → fail-closed 阻断（2026-09-14 立：同名键嵌套
#   creation_tokens(L883) 与顶层(L4987) 共存+EOF 尾追悬挂条目致全库解析炸四连（9ca0f62b95 修/1edeea81b4 修/
#   a5883d01 修/94aa4111 批内修）；2026-09-15 扩：data_asset_registry.yaml 双 datasets 根键（L752/755，
#   PyYAML 静默取后者，前段插条目被解析层忽略）随 st-patgov 合并批入库（件3），watch 面同步扩入+根键唯一
#   硬化；正确追加姿势=插既有根键的列表尾+提交前必验 parse；阻断与放行均落审计 .runtime/gate_audit/registry_yaml_parse.jsonl；
#   2026-10-09 扩（A-12 治本）：capability 册加 token 级只增不减守门——HEAD 顶层
#   creation_tokens 复合身份（file|token=）相对 staged 差集非空 → 阻断（投影指纹只证
#   staged==PG 投影，不证投影未落后 HEAD；直提 render-sync 整档覆盖抹他道 token 的
#   病根封堵）；白名单=[allow-mass-deletion:reason≥10字]（与 REGISTRY-MASS-DELETION
#   同标记）；HEAD 缺失/解析失败 fail-open
# [MODIFY-GUARD] gate_id="REGISTRY-YAML-PARSE"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 失败/文件不可读 → fail-open 跳过（encoding 类 gate 覆盖）；staged 版本 YAML 解析失败/根键重复/capability 注册表结构破坏 → fail-closed 阻断（passed=False，报错附正确追加姿势教学）；审计写失败静默降级
# [TESTS] tests/governance/commit_gates/test_registry_yaml_parse_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L
# [TTL] permanent
"""registry_yaml_parse_gate.py — 注册表结构硬化门禁（防尾追悬挂/防重复根键）
# [ALGO_FLOW]

背景（2026-09-14，同病四连）：
    capability_canonical_file_registry.yaml 顶层键序=[schema_version…capabilities,
    creation_tokens, di_seam_exemptions]——di_seam_exemptions 在 creation_tokens 之后，
    EOF 追加 token 条目必落错段（悬挂在 exemptions 之后），全库 YAML 解析炸：
    capability_lookup 挂、所有读该表的会话挂。2026-09-13/14 四次同病
    （pattern 会话修一次/sim 会话修一次/st-sopreorg 修两次），口头纪律+"提交前验 parse"
    的约定反复失守 → 硬化为 commit gate。

扩面（2026-09-15，图形库治理上报件3）：
    data_asset_registry.yaml 双 `datasets:` 根键（L752 空 null 键/L755 真块）——
    PyYAML 对重复根键静默取后者，人工/工具往前段插条目会被解析层无感忽略。
    合并批入库后，watch 面扩入该文件，并新增**顶层根键唯一**断言（yaml.compose
    节点树判重——safe_load 对重复键静默覆盖，节点树才同时保留两个），
    capability 注册表同享此检查。

检测逻辑（对 staged 文本，按档案分档）：
    capability_registry 档：
        1. yaml.safe_load 通过（解析炸直接阻断）
        2. 顶层根键唯一（yaml.compose 判重）
        3. 顶层 di_seam_exemptions 键存在且为末位键（尾追悬挂判别式）
        4. creation_tokens 键存在且为 list（结构走样拦截）
    data_asset_registry 档：
        1. yaml.safe_load 通过
        2. 顶层根键唯一

触发范围：staged 命中 _WATCH_FILES（capability_canonical_file_registry.yaml /
data_asset_registry.yaml，两个高频追加热注册表）——紧范围不加宽（净删防护由
REGISTRY-MASS-DELETION 负责，编码由 ENCODING-SAFETY 负责）。

无逃生标记：解析炸/根键重复的注册表没有"先合入再修"的合法场景——修复后在同一
commit 重新 staged 即可（gate 看的是 staged 终态）。

Usage::

    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import (
        make_registry_yaml_parse_gate,
    )
    registry.register(make_registry_yaml_parse_gate())
"""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _build_own_scope,
    _norm_rel,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_registry_yaml_parse_gate"]

# 审计落点（.runtime/gate_audit/ 家族惯例）
_AUDIT_REL = ".runtime/gate_audit/registry_yaml_parse.jsonl"

# 热追加目标 watch 表 → 结构断言档案（紧范围不加宽；净删防护归 REGISTRY-MASS-DELETION，
# 编码归 ENCODING-SAFETY）。capability=全量断言；data_asset=parse+根键唯一；
# hot_registry_basic=parse+根键唯一（结构面）+投影 tamper 判别（tamper 对全部 watch 面
# 生效，不分支档案——staged≠状态文件指纹即拦，2026-10-09 C 件扩面裁定#502 战役）。
# P0 七册扩面（st-regsolo-20261010）：六册在挂；module_translation_registry 暂缓——
# 他会话（st-dexp）活跃持有直写面，watch 上线即砖其合法流，随翻译登记改道意图 API
# 后同批上线（translate 轨退役=本战役 A2 车道）。
_WATCH_FILES: dict[str, str] = {
    "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml": "capability_registry",
    "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml": "data_asset_registry",
    "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml": "hot_registry_basic",
    "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml": "hot_registry_basic",
    "architecture_model/contracts/error_code_registry.yaml": "hot_registry_basic",
    "docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml": "hot_registry_basic",
    "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml": "hot_registry_basic",
}

# 向后兼容别名（capability 注册表=首 watch 目标）
_WATCH_FILE = next(iter(_WATCH_FILES))

# 教学信息（阻断时给出正确姿势，治"每次重新发明修法"）
_TEACH = (
    "正确追加姿势：条目插在既有根键的列表尾（capability 注册表的 token 条目插 "
    "creation_tokens 列表尾=di_seam_exemptions: 行之前，注意 L883 有一个嵌套同名键勿错插），"
    "顶层根键禁止重复（PyYAML 静默取后者，前段插条目会被解析层无感忽略），"
    "插入后必须 yaml.safe_load 验证通过再提交"
)

# ── W-M1 投影执法扩展（st-wm1-buildB-20260923）───────────────────────────────
# 投影管理册（状态文件存在=已武装）私改检测：staged blob sha ≠ 投影状态文件
# content_sha256 → 阻断。判别真源=本地状态文件（PG 宕机照样抓私改，丙号文 §3.2
# 执法层契约：门禁只读 staged blob + 状态文件两个便宜物，零 PG 依赖）。
# 未武装（状态文件缺失/损坏/registry_path 不符）→ fail-open 零行为（cutover 前
# 登记正门仍是 batch_creation_tokens 直写，全量兼容）。生成器自身提交天然
# staged==S 通过。挂本文件不新增 gate（净零红线），own-scope 由 _build_own_scope 既有。
_PROJECTION_STATE_REL = ".runtime/projection/registry_projection_state.json"


def _projection_tamper_issue(gateway, watch_file: str) -> str | None:
    """投影私改判别（返回问题文案或 None=通过/不适用）。永不抛异常。

    状态文件双形态（PD-1 v2）：v2 map（registries 键控多册）逐条目匹配本册；
    v1 单册平铺兼容。本册无条目=别册（fail-open 零行为）。
    """
    try:
        import json

        from zephyr.shared.io.file_utils import content_sha256

        root = Path(getattr(gateway, "project_root", "."))
        state_file = root / _PROJECTION_STATE_REL
        if not state_file.exists():
            return None  # 未武装：投影管理未启用，零行为
        state = json.loads(state_file.read_text(encoding="utf-8"))
        entry: dict | None = None
        registries = state.get("registries")
        if isinstance(registries, dict) and registries:
            for key, value in registries.items():
                if not isinstance(value, dict):
                    continue
                candidate = str(value.get("registry_path") or key)
                if candidate and _norm_rel(gateway, candidate) == _norm_rel(gateway, watch_file):
                    entry = value
                    break
            if entry is None:
                return None  # v2 在挂但本册无条目：别册/未武装本册
        else:
            state_registry = str(state.get("registry_path", ""))
            if not state_registry or _norm_rel(gateway, state_registry) != _norm_rel(gateway, watch_file):
                return None  # 状态文件登记的是别册
            entry = state
        expected = entry.get("content_sha256")
        if not expected:
            return None  # 状态损坏 → fail-open（daemon 层兜底抓）
        staged_text = _read_staged_file(gateway, watch_file)
        if staged_text is None:
            return None  # 读失败 fail-open（encoding 类 gate 覆盖）
        if content_sha256(staged_text) != expected:
            return (
                "staged 内容与投影状态文件指纹不符（私改投影册无效）——"
                "此文件是 PG 账本投影：改动请走意图 API 登记+生成器重打（"
                "python scripts/governance/registry_projection/registry_projection_generator.py --render）"
            )
    except Exception:  # noqa: BLE001 — 执法扩展整体 fail-open
        logger.debug("projection tamper check fail-open", exc_info=True)
        return None
    return None


# ── A-12 直提通道 token 级只增不减守门（st-chiefc-20261009，2026-10-09）────────
# 病根：capability 册是机生投影（REGISTRY-YAML-PARSE 强制 staged==投影状态指纹），
# 但指纹只证「staged==PG 投影」，不证「投影未落后于 HEAD」——batch_creation_tokens
# 直写轨（gate 可见 PG 不知）与他道 api.register 轨在「入队→落地」窗内互相覆盖，
# 直提 render-sync 整文件 commit 把 HEAD 有而投影无的 token 整批抹掉（实弹：5 token
# 三次被抹，死信再产根因）。本守门=投影指纹之外的第二判据：HEAD 顶层 creation_tokens
# 复合身份（file|token=，与合并器 _merge_entry_identity 同构）相对 staged 的差集非空
# → 阻断；白名单=[allow-mass-deletion:reason≥10字]（与 REGISTRY-MASS-DELETION 同
# 标记同语义——合法退役经 PG retire 后重打投影时用同一标记过两门）。HEAD 缺失/读取
# 失败/解析失败 → fail-open。挂本文件不新增 gate（净零红线），own-scope 既有。
_PROJECTION_LAG_MARKER_RE = re.compile(r"\[allow-mass-deletion:([^\]]{10,})\]")


def _creation_token_identities(text: str) -> dict[str, str] | None:
    """顶层 creation_tokens 条目复合身份集（file|token= → 展示名）。解析失败/结构不符 → None。"""
    try:
        import yaml

        data = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 — 解析失败由 _structural_issues 报告
        return None
    if not isinstance(data, dict):
        return None
    ct = data.get("creation_tokens")
    if not isinstance(ct, list):
        return None
    out: dict[str, str] = {}
    for entry in ct:
        if not isinstance(entry, dict):
            continue
        file_v = entry.get("file")
        token_v = entry.get("token")
        if isinstance(file_v, str) and isinstance(token_v, (str, int, float)):
            out[f"{file_v}|token={token_v}"] = f"{file_v} (token={token_v})"
        else:
            for v in entry.values():  # 无 file/token 对 → 退首标量单键（存在级比对）
                if isinstance(v, (str, int, float, bool)):
                    out[str(v)] = str(v)
                    break
    return out


def _head_token_lag_issue(gateway, watch_file: str, staged_text: str, message: str) -> str | None:
    """直提通道 capability 册 token 级只增不减判别（返回问题文案或 None=通过/不适用）。永不抛异常。"""
    try:
        result = gateway.run_git(["git", "show", f"HEAD:{watch_file}"])
        if result.returncode != 0:
            return None  # 新文件/无 HEAD → fail-open
        head_ids = _creation_token_identities(result.stdout)
        staged_ids = _creation_token_identities(staged_text)
        if head_ids is None or staged_ids is None:
            return None  # 判不了 → fail-open（结构面由 _structural_issues 把守）
        missing = sorted(set(head_ids) - set(staged_ids))
        if not missing:
            return None
        if _PROJECTION_LAG_MARKER_RE.search(message or ""):
            logger.warning(
                "REGISTRY-YAML-PARSE: %s 相对 HEAD 少 %d 条 token，message 标记放行（合法退役须 PG retire 对账）",
                watch_file,
                len(missing),
            )
            return None
        sample = "; ".join(head_ids[k] for k in missing[:5])
        return (
            f"相对 HEAD 少 {len(missing)} 条 creation_token（如 {sample}）——直提整档覆盖"
            f"会抹掉他道已落条目（陈旧投影/双轨滞后）。修法：PG 登记（api.register）后"
            f"重打投影（registry_projection_generator --render）再提交；确属合法退役"
            f"（PG retire 已对账）：commit message 加 [allow-mass-deletion:<reason≥10字>]"
        )
    except Exception:  # noqa: BLE001 — 执法扩展整体 fail-open
        logger.debug("head token lag check fail-open", exc_info=True)
        return None


def _audit(gateway, record: dict) -> None:
    """审计落盘（jsonl append；fail-open：写失败不阻断）。"""
    try:
        root = Path(getattr(gateway, "project_root", "."))
        audit_dir = root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        with (audit_dir / "registry_yaml_parse.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        logger.debug("REGISTRY-YAML-PARSE audit write failed (non-blocking)", exc_info=True)


def _duplicate_root_keys(text: str) -> list[str]:
    """yaml.compose 节点树判重——safe_load 对重复根键静默取后者，节点树才同时保留两个。

    永不抛异常（compose 失败返回空=由 safe_load 断言兜底报解析失败）。
    """
    try:
        import yaml

        node = yaml.compose(text)
    except Exception:  # noqa: BLE001 — 解析失败由 _structural_issues 的 safe_load 断言报告
        return []
    if node is None or not hasattr(node, "value") or not isinstance(node.value, list):
        return []  # 非 MappingNode（Scalar/Sequence）→ 无根键可判重
    seen: set[str] = set()
    dups: list[str] = []
    for key_node, _ in node.value:
        k = str(getattr(key_node, "value", ""))
        if k in seen and k not in dups:
            dups.append(k)
        seen.add(k)
    return dups


_PARSE_CACHE: dict[str, tuple[str, list[str]]] = {}
_PARSE_CACHE_MAX = 8


def _structural_issues(text: str, profile: str) -> list[str]:
    """二层⑦缓存（Owner 全批 2026-10-05）：13k 条热册 yaml.safe_load 每次 ~2s，
    同内容重复解析 36 次/天=白跑 72s。以 sha256(text) 为键缓存结果，命中即返。
    fail-open：缓存写入失败静默跳过（安全不降级=每次都全量解析）。"""
    import hashlib as _hl

    _key = f"{profile}:{_hl.sha256(text.encode('utf-8')).hexdigest()[:16]}"
    _cached = _PARSE_CACHE.get(_key)
    if _cached is not None:
        return list(_cached)
    """对 staged 文本做档案化断言 → 问题清单（空=通过）。永不抛异常。

    capability_registry 档：parse + 根键唯一 + exemptions 末位 + creation_tokens list。
    data_asset_registry 档：parse + 根键唯一。
    """
    issues: list[str] = []
    try:
        import yaml

        data = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001 — 解析失败=阻断本体
        issues.append(f"yaml.safe_load 解析失败: {str(exc)[:160]}")
        return issues
    if not isinstance(data, dict):
        issues.append(f"顶层不是 mapping（实际 {type(data).__name__}）")
        return issues
    dups = _duplicate_root_keys(text)
    if dups:
        issues.append(f"顶层根键重复: {dups}（PyYAML 静默取后者——前段条目会被解析层无感忽略，必须合并为单键）")
    if profile == "capability_registry":
        keys = list(data.keys())
        if "di_seam_exemptions" not in keys:
            issues.append("顶层 di_seam_exemptions 键缺失")
        elif keys[-1] != "di_seam_exemptions":
            issues.append(f"di_seam_exemptions 不是末位顶层键（当前末位={keys[-1]!r}，键序={keys[-3:]}）")
        ct = data.get("creation_tokens")
        if not isinstance(ct, list):
            issues.append(f"creation_tokens 不是 list（实际 {type(ct).__name__}）")
    if len(_PARSE_CACHE) < _PARSE_CACHE_MAX * 2:
        _PARSE_CACHE[_key] = list(issues)
    return issues


def make_registry_yaml_parse_gate() -> GateSpec:
    """构造 REGISTRY-YAML-PARSE pre-commit 门禁（priority=54）。

    staged 热注册表按档案断言（parse 通过/根键唯一/capability 注册表另查 exemptions
    末位+creation_tokens list）任一不满足 → fail-closed 阻断+教学信息；
    读失败/git 异常 → fail-open 跳过。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        try:
            result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
            if result.returncode != 0:
                return True, ""  # fail-open：git 失败不阻断
            staged_yaml = [
                f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f and f.endswith(".yaml")
            ]
        except Exception:  # noqa: BLE001 — fail-open
            logger.warning("REGISTRY-YAML-PARSE fail-open: git diff 异常", exc_info=True)
            return True, ""

        session_id = kwargs.get("session_id")
        own_scope = _build_own_scope(gateway, files, session_id)
        if own_scope is not None:
            staged_yaml = [f for f in staged_yaml if _norm_rel(gateway, f) in own_scope]

        watched = [(f, profile) for f, profile in _WATCH_FILES.items() if f in staged_yaml]
        if not watched:
            return True, ""

        all_issues: list[tuple[str, list[str]]] = []
        for watch_file, profile in watched:
            staged_text = _read_staged_file(gateway, watch_file)
            if staged_text is None:
                continue  # fail-open：读失败（encoding 类 gate 覆盖）
            issues = _structural_issues(staged_text, profile)
            tamper = _projection_tamper_issue(gateway, watch_file)
            if tamper:
                issues.append(tamper)
            if profile == "capability_registry":
                # A-12 直提通道守门：投影指纹只证 staged==PG 投影，不证投影未落后 HEAD——
                # token 级只增不减补上双轨滞后窗（复用 own-scope：外来 staged 不拦，§3.1）
                lag = _head_token_lag_issue(gateway, watch_file, staged_text, str(kwargs.get("commit_message") or ""))
                if lag:
                    issues.append(lag)
            if issues:
                all_issues.append((watch_file, issues))

        _audit(
            gateway,
            {
                "timestamp": int(time.time()),
                "gate": "REGISTRY-YAML-PARSE",
                "action": "block" if all_issues else "pass",
                "session_id": session_id or "?",
                "files": {f: issues for f, issues in all_issues} if all_issues else [f for f, _ in watched],
            },
        )
        if not all_issues:
            return True, ""
        detail = "\n".join(
            line
            for f, issues in all_issues
            for line in (f"REGISTRY-YAML-PARSE: {f} 结构校验未过:", *(f"  - {i}" for i in issues))
        )
        msg = f"{detail}\n  {_TEACH}"
        logger.error(msg)
        return False, msg

    return GateSpec(
        gate_id="REGISTRY-YAML-PARSE",
        check=_check,
        priority=54,
    )
