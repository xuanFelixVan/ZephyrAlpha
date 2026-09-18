# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_get_staged_py_files, _read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（YAML 驱动自动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 登记表 mass-deletion 门禁——staged 登记表类 YAML 净删行（删>插）**或条目身份消失（HEAD 有而 staged 无的条目键）**→ 阻断（2026-09-09 险些蒸发 4703 行治本，nodebt 晨报裁定 7）；YAML 条目数减少 → 无论行数直接阻断；白名单=commit message 标记 [allow-mass-deletion:reason]（reason≥10 字，随 message 永久留痕，对标 capability_lookup_required_gate [no-lookup:reason] 先例）；阈值内合法重排（整文件重生成等）走标记逃生；阻断与放行均落审计 .runtime/gate_audit/registry_mass_deletion.jsonl；fail-open（HEAD 缺失/YAML 解析失败/文件不可读 → 跳过该文件，不误报）
# [MODIFY-GUARD] gate_id="REGISTRY-MASS-DELETION"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git show HEAD 失败（新增文件）/YAML 解析失败/文件不可读 → fail-open 跳过该文件（不误报，encoding/syntax 类 gate 覆盖）；检出净删行或条目数减少且无逃生标记 → fail-closed 阻断（passed=False）；审计写失败静默降级
# [TESTS] tests/governance/commit_gates/test_registry_mass_deletion_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L
# [TTL] permanent
"""
registry_mass_deletion_gate.py — 登记表 mass-deletion 门禁（防蒸发第二道保险）

背景（2026-09-09 夜 4703 行蒸发事故，nodebt 晨报裁定 7）：
    首版批量补登脚本正则未匹配缩进条目，纯删除逻辑一次性清空两登记表 4703 行。
    registry_batch_edit 工具（第一道保险）强制纯插入；本 gate 是第二道保险——
    即使绕过工具直接改登记表，commit 阶段净删行也会被拦截。

检测逻辑（三信号）：
    1. 净删行：difflib opcodes 累计 delete/replace 原行数 vs insert/replace 新行数，
       deleted > added → 阻断（4703 删/0 插必命中；改 1 行=1删1插 不命中；
       纯插入不命中；整文件重排这种高净删操作走 message 标记逃生）
    2. 条目数断言：两侧 yaml.safe_load 后顶层条目数 new < old → 无论行数直接阻断
       （防"大改小删"漏网；YAML 解析失败 fail-open 交 encoding/syntax 类 gate）
    3. 条目身份断言（红队加固③ st-ff-rb-gov-20260918，2026-09-18 攻面二 E1 实弹）：
       HEAD 侧条目身份集 - staged 侧 = 非空 → 阻断。信号 1/2 都是**计数型**，
       会被"删他人 16 条 + 插自己 25 条"的代数抵消批次整体放行（E1 实测三判据全绿、
       16 条静默蒸发）；身份比对不看代数只看"哪一条没了"。
       身份 = 每条首个标量字段（登记表惯例主键：capability_id/path/module_path/gate_id…）；
       条目非 dict 或首字段非标量 → 该条不计入身份集（判不了不误报，fail-open 同向）。

触发范围：staged 相对路径命中 _REGISTRY_DIR_MARKER（登记表目录）或 _WATCH_FILES
（目录外登记类 YAML）；_EXEMPT_FILES 豁免。

白名单（任务书"阈值内合法重排除外"）：commit message 含
    [allow-mass-deletion:<reason≥10字>]
→ 放行 + 落审计（含 reason）。零 gateway 改动，标记随 message 永久入库可审计。

Usage::

    from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import (
        make_registry_mass_deletion_gate,
    )
    registry.register(make_registry_mass_deletion_gate())
"""

from __future__ import annotations

import difflib
import json
import logging
import re
import time
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _audit_foreign_staged,
    _build_own_scope,
    _norm_rel,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_registry_mass_deletion_gate"]

# 审计落点（.runtime/gate_audit/ 家族惯例，对标 protected_paths_gate）
_AUDIT_REL = ".runtime/gate_audit/registry_mass_deletion.jsonl"

# 触发范围：登记表目录标记（路径含此段且 .yaml 结尾）
_REGISTRY_DIR_MARKER = "/_registry/catalogs/"

# 目录外登记类 YAML（显式清单）
_WATCH_FILES: frozenset[str] = frozenset(
    {
        "docs/01_policies_and_standards/_registry/registry_of_registries.yaml",
    }
)

# 豁免清单（对标 scripts_import_integrity_gate._EXEMPT_FILES 先例）
_EXEMPT_FILES: frozenset[str] = frozenset(
    {
        # 登记表目录内的生成物（自动再生，行数波动大，归生成器真源管）
        "docs/01_policies_and_standards/_registry/catalogs/script_manifest.yaml",
    }
)

# 逃生标记正则：[allow-mass-deletion:reason]（reason≥10 字符，防"标记漂洗"）
_ALLOW_MARKER_RE = re.compile(r"\[allow-mass-deletion:([^\]]{10,})\]")

# 行级统计信号（对 4703 行大表 SequenceMatcher 足够：行数千级毫秒内）


def _is_watch_file(rel: str) -> bool:
    """staged 相对路径是否命中触发范围。"""
    norm = rel.replace("\\", "/")
    if norm in _EXEMPT_FILES:
        return False
    if norm in _WATCH_FILES:
        return True
    return _REGISTRY_DIR_MARKER in norm and norm.endswith(".yaml")


def _line_delta(head: str, staged: str) -> tuple[int, int]:
    """行级统计 → (deleted, added)（SequenceMatcher opcodes 累计）。"""
    head_lines = head.splitlines()
    staged_lines = staged.splitlines()
    deleted = 0
    added = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=head_lines, b=staged_lines, autojunk=False).get_opcodes():
        if tag == "delete":
            deleted += i2 - i1
        elif tag == "insert":
            added += j2 - j1
        elif tag == "replace":
            deleted += i2 - i1
            added += j2 - j1
    return deleted, added


def _yaml_entry_count(text: str) -> int | None:
    """YAML 条目数（list=元素数 / dict=各 list 值元素总和，无 list 值则键数）。

    dict 根取 list 值总和：登记表惯例形如 {meta: {...}, entries: [36 条]}，
    裁定 7 场景（entries 36→0）必须命中条目信号。
    """
    try:
        import yaml

        data = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 — 解析失败由调用方 fail-open
        return None
    if data is None:
        return 0
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        list_items = sum(len(v) for v in data.values() if isinstance(v, list))
        return list_items if list_items else len(data)
    return None


def _entry_identity_keys(text: str) -> set[str] | None:
    """登记表条目**身份集**：每条首个标量字段 → `"key=value"` 集合。

    红队加固③（st-ff-rb-gov-20260918，2026-09-18 全流通战役攻面二 E1 实弹）：
    本 gate 原两信号都是**计数型**（净删行 deleted>added / 条目数 new<old），
    故"删他人 16 条 + 插自己 25 条"这种**代数为正**的批次双双放行，
    而被删的 16 条就此蒸发——计数守不住身份，身份只能按身份比。
    scratch 实测：三方合并（base=dev）对陈旧 ours 会静默采纳"我方删除"，
    `grep -c '^<'`=0（人工判据绿）+ 净删<净插（本 gate 绿）+ 条目数增加（信号2 绿）。

    Returns:
        身份集合；YAML 解析失败 / 无 list 结构 / 条目非 dict → None（调用方跳过本信号，
        与原 fail-open 语义同向：判不了就不误报，交 encoding/syntax 类 gate 管）。
    """
    try:
        import yaml  # noqa: PLC0415 — lazy import，与原 _yaml_entry_count 同风格

        data = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 — 解析失败 fail-open（交 syntax 类 gate）
        return None
    if isinstance(data, list):
        lists: list[list] = [data]
    elif isinstance(data, dict):
        lists = [v for v in data.values() if isinstance(v, list)]
    else:
        return None
    keys: set[str] = set()
    for lst in lists:
        for item in lst:
            if not isinstance(item, dict) or not item:
                continue
            first = next(iter(item))
            value = item[first]
            if isinstance(value, (str, int, float, bool)):
                keys.add(f"{first}={value}")
    return keys or None


def _audit(gateway, record: dict) -> None:
    """审计落盘（jsonl append；fail-open：写失败不阻断）。"""
    try:
        root = Path(getattr(gateway, "project_root", "."))
        audit_dir = root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        with (audit_dir / "registry_mass_deletion.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        logger.debug("REGISTRY-MASS-DELETION audit write failed (non-blocking)", exc_info=True)


def make_registry_mass_deletion_gate() -> GateSpec:
    """构造 REGISTRY-MASS-DELETION pre-commit 门禁（priority=140）。

    检测 staged 登记表类 YAML 净删行 / 条目数减少，硬阻断；
    commit message 含 [allow-mass-deletion:reason≥10字] 放行+审计。
    fail-open：HEAD 缺失（新增文件）/YAML 解析失败/文件不可读 → 跳过。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        message = str(kwargs.get("commit_message", "") or "")
        marker = _ALLOW_MARKER_RE.search(message)

        # 登记表是 .yaml——直接用底层 git diff 全量文件清单（.py 过滤器不适用）
        try:
            result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
            if result.returncode != 0:
                return True, ""  # fail-open：git 失败不阻断
            staged_all = [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f and f.endswith(".yaml")]
        except Exception:  # noqa: BLE001 — fail-open
            logger.warning("REGISTRY-MASS-DELETION fail-open: git diff 异常", exc_info=True)
            return True, ""

        # own-scope（#ARCH-GATE-OWN-SCOPE-001 推广批，2026-09-11）：本 gate 原按 staged
        # 全量判定（净删行是文件级信号）。但 gateway 提交走 pathspec 只含本 session 文件
        # ——外来 staged 登记表进不了本次 commit，其风险在归属会话提交时必经本闸（全部
        # 提交走唯一入口，覆盖保证不变）。共享暂存区大登记表批（20+ catalogs YAML 逐个
        # git show+YAML 解析）曾使 5 文件小提交付出 34.6s。own_scope=None（无归属信息）
        # → 退化为旧行为扫全量（保守面不改宽）。
        session_id = kwargs.get("session_id")
        own_scope = _build_own_scope(gateway, files, session_id)
        if own_scope is not None:
            foreign_yaml = [f for f in staged_all if _norm_rel(gateway, f) not in own_scope]
            if foreign_yaml:
                _audit_foreign_staged(gateway, session_id, foreign_yaml, gate_name="REGISTRY-MASS-DELETION")
                logger.warning(
                    "REGISTRY-MASS-DELETION: %d 个外来 session staged .yaml 未检查（warn+审计，不阻断）: %s",
                    len(foreign_yaml),
                    ", ".join(foreign_yaml[:5]) + ("..." if len(foreign_yaml) > 5 else ""),
                )
                staged_all = [f for f in staged_all if _norm_rel(gateway, f) in own_scope]

        watch = [f for f in staged_all if _is_watch_file(f)]
        if not watch:
            return True, ""

        hits: list[str] = []
        for rel in watch:
            try:
                head_result = gateway.run_git(["git", "show", f"HEAD:{rel}"])
                if head_result.returncode != 0:
                    continue  # 新增文件无 HEAD 基线 → fail-open 跳过
                head_text = head_result.stdout
            except Exception:  # noqa: BLE001 — fail-open
                continue
            staged_text = _read_staged_file(gateway, rel)
            if staged_text is None:
                continue  # fail-open：读失败

            deleted, added = _line_delta(head_text, staged_text)
            n_head = _yaml_entry_count(head_text)
            n_staged = _yaml_entry_count(staged_text)
            entry_shrunk = n_head is not None and n_staged is not None and n_staged < n_head
            net_delete = deleted > added

            # 信号3（红队加固③ st-ff-rb-gov-20260918）：条目**身份**消失——计数型判据
            # 会被"删他人 N 条 + 插自己 M 条（M>N）"的批次代数抵消掉，身份比对不会。
            k_head = _entry_identity_keys(head_text)
            k_staged = _entry_identity_keys(staged_text)
            lost_keys: set[str] = set()
            if k_head is not None and k_staged is not None:
                lost_keys = k_head - k_staged
            identity_loss = bool(lost_keys)

            if net_delete or entry_shrunk or identity_loss:
                hits.append(
                    f"  {rel}: 净删行 deleted={deleted} added={added}"
                    + (f"（条目数 {n_head} -> {n_staged} 减少）" if entry_shrunk else "")
                    + (
                        f"（条目身份消失 {len(lost_keys)} 条，示例 {sorted(lost_keys)[:3]}）"
                        if identity_loss
                        else ""
                    )
                )
                _audit(
                    gateway,
                    {
                        "timestamp": int(time.time()),
                        "gate": "REGISTRY-MASS-DELETION",
                        "action": "block" if not marker else "block_pending_marker",
                        "session_id": kwargs.get("session_id") or "?",
                        "file": rel,
                        "deleted": deleted,
                        "added": added,
                        "entries_head": n_head,
                        "entries_staged": n_staged,
                        "lost_identity_count": len(lost_keys),
                        "lost_identity_sample": sorted(lost_keys)[:10],
                    },
                )

        if not hits:
            return True, ""

        if marker:
            # 白名单放行 + 审计（reason 随 commit message 永久留痕）
            _audit(
                gateway,
                {
                    "timestamp": int(time.time()),
                    "gate": "REGISTRY-MASS-DELETION",
                    "action": "allowed_by_marker",
                    "session_id": kwargs.get("session_id") or "?",
                    "reason": marker.group(1),
                    "files": [h.split(":")[0].strip() for h in hits],
                },
            )
            note = (
                f"[warn] REGISTRY-MASS-DELETION: 净删行/条目减少命中但 message 标记放行"
                f"（reason: {marker.group(1)}）——登记表重排请确认备份可回滚: "
                + "; ".join(h.split(":")[0].strip() for h in hits[:5])
            )
            logger.warning("%s", note)
            return True, note

        detail = (
            "REGISTRY-MASS-DELETION: 登记表净删行/条目数减少（2026-09-09 4703 行蒸发治本）\n"
            "  病根：批量编辑正则失配把插入变删除；登记表条目只应增长（历史裁定 #ARCH-BP-REGISTRY-DELETION-001 同向）。\n"
            "  修复：①批量补登走 scripts/governance/registry_batch_edit.py 纯插入工具；\n"
            "        ②确属合法重排（整文件重生成/历史清理）：commit message 加标记\n"
            "          [allow-mass-deletion:<reason≥10字>]（随 message 永久留痕+审计）。\n"
            + "\n".join(hits[:20])
            + (f"\n  ...(+{len(hits) - 20} more)" if len(hits) > 20 else "")
        )
        logger.error("REGISTRY-MASS-DELETION gate block:\n%s", detail)
        return False, detail

    return GateSpec(
        gate_id="REGISTRY-MASS-DELETION",
        check=_check,
        priority=140,
    )
