# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §mount-coverage
# [MODULE] zephyr.gov_enforcement.commit_gates.tdm_mount_coverage_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.gov_enforcement.commit_gates._diff_helpers (_split_own_foreign); zephyr.shared.io.paths (REPO_ROOT); zephyr.infrastructure.database_service (DatabaseService, 只读反查); scripts.governance._shared.mount_obligation (build_mounted_set/collect_map_nodes/load_exemptions/has_not_trading_marker/extract_blueprint_module_id——挂载口径单计算双消费)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（in_process 名册装载）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] own-diff 作用域=staged 新增 blueprint.md（docs/03_modules/**）+ 新增 .py（src/zephyr/+scripts/，tests/demos/test_*前缀/__init__/_archive 豁免同 TRANSLATION-COVERAGE 口径）；三选一裁决放行=①module_id 已挂某图（module_id∪module_mounts 并集，staged 版图优先——图+模块同批合法）②豁免册命中（TDM-MOUNT-EXEMPT-001，staged 版同理）③[not-trading:<非空理由>] 标记（同批 blueprint.md 或 .py 头）；缺裁决=阻断+三选一处方；撞号拦（depgraph 同 blueprint_id 已注册到不同 path，e 裁决册 no2 实证形态）；蓝图锚一致性拦（新增 blueprint.md frontmatter module_id 与同批 .py [BLUEPRINT] 行不一致=拦；staged 地图 diff 新增 module_mounts 引用无 depgraph 蓝图锚=幽灵挂载拦）；挂载口径经 _shared.mount_obligation 单计算（与 B 账本/manifest 同源防漂移）；豁免册缺席=前置未落自锁 skip 非拦（工单A 前置在运行时面自证）；外来 staged warn+审计不阻断（_split_own_foreign 宪法§3.1）
# [MODIFY-GUARD] gate_id="TDM-MOUNT-COVERAGE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git/depgraph/YAML/IO 异常降级 fail-open（passed=True，logger.warning，环境异常非违规）；检出违规 fail-closed 硬阻断（无观察期——豁免册首拍 55 台随前置批同步落地，bootstrap 只拦新增文件存量零误拦）
# [TESTS] tests/governance/commit_gates/test_tdm_mount_coverage_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
tdm_mount_coverage_gate.py — TDM 挂载义务门禁（TDM-MOUNT-COVERAGE，priority=151）

检测 staged 新增 blueprint.md / 新 .py 模块（tests/ 豁免）是否带挂载裁决：三选一放行——
① module_id 已挂某图（module_id∪module_mounts 并集）②豁免册命中（域归属豁免）
③ 显式 [not-trading:<理由>] 标记；缺裁决=阻断+处方。附带撞号拦与蓝图锚↔地图节点
引用一致性校验（与 TDM v1.3 立项 0e94229a1b1 合流职责）。

病根（第一性原理）
-----------------
TDM 血肉挂载战役（B 账本 233 缺口→e 裁决册 233 行）治了存量，治不了增量：AI 新建
.py/blueprint.md 时无挂载裁决，事后靠普查批量补救——100% AI 开发下事后治理永远滞后
（同 TRANSLATION-COVERAGE 病根形态）。撞号两对（SIG-087/088 双注册）与幽灵挂载风险
同理：蓝图锚↔地图节点引用双向漂移无技术强制。本 gate 把「新模块必有挂载裁决」从
君子协定升级为提交时技术强制。

真源边界（SSoT 分类铁律 TRAE-062）
----------------------------------
- 挂载面=规则数据 YAML（config/*_map.yaml 节点 module_id+module_mounts，policy v1.3 三字段）
- 豁免册=规则数据 YAML（config/tdm_mount_exemption_registry.yaml，TDM-MOUNT-EXEMPT-001）
- 蓝图锚=架构数据（depgraph PG nodes.blueprint_id，只读反查）
- 本 gate 只读，不写任何真源；裁决真源维护=总筹裁决册增量（policy v1.3）。

设计要点
--------
1. **priority=151**：编排在 NEW-FILE-DEPGRAPH-ENFORCEMENT(58)→TRANSLATION-COVERAGE(59)→
   CREATE-GUARD(60) 之后——先确认节点已登记，再问挂载裁决（61 号段与 RULE-EXECUTION-PAIRING
   撞号，gate 册渲染在案，后到者让位顺延 150→151（150 与 TASK-ORDER-DOCS-LOCK 撞号二次让位，st-tests-chief-20261004 全局阻塞最小机械修 2026-10-04））。
2. **staged 版真源**：挂载面/豁免册读暂存区内容（图+模块同批合法，防 HEAD 口径误杀
   同批挂载提交；静窗学费「预检读暂存区非工作树」直接适用）。
3. **单计算双消费**：挂载面并集经 ``scripts/governance/_shared/mount_obligation``——
   与 B 账本生成器、义务清单 manifest 同源，口径变更一处生效（本 gate 立项的直接动因
   即 B 账本生成器只认 module_id 不认 module_mounts 的口径漂移）。
4. **前置自锁**：豁免册文件缺席=前置（工单A 落豁免首拍）未同步，skip 留言非拦——
   防止 gate 先于其真源上线即全量误拦。
5. **fail-open on 环境异常**：depgraph PG/地图 YAML/git 不可达=环境异常非违规，放行
   +warning（对标 TRANSLATION-COVERAGE/NEW-FILE-DEPGRAPH-ENFORCEMENT）。

Usage::

    from zephyr.gov_enforcement.commit_gates.tdm_mount_coverage_gate import (
        make_tdm_mount_coverage_gate,
    )

    registry.register(make_tdm_mount_coverage_gate())

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/t/tdm_mount_coverage_gate.yaml
"""

from __future__ import annotations

import logging
import os
import re
import sys
from typing import Final

from zephyr.gov_enforcement.commit_gates._diff_helpers import _split_own_foreign
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__: Final = ["make_tdm_mount_coverage_gate"]

# 范围限定（同 TRANSLATION-COVERAGE）：src/zephyr/ + scripts/ 下的能力模块
_SRC_ZEPHYR_PREFIX = "src/zephyr/"
_SCRIPTS_PREFIX = "scripts/"
# blueprint.md 触发面
_BLUEPRINT_DIR_PREFIX = "docs/03_modules/"
_BLUEPRINT_BASE = "blueprint.md"
# .py 头 [BLUEPRINT] 锚行：# [BLUEPRINT] MOD-X | docs/.../blueprint.md | §...
_RE_PY_BP_ANCHOR = re.compile(r"^#\s*\[BLUEPRINT\]\s+(\S+)\s+\|\s+(\S+)\s+\|", re.M)
# depgraph 反查 SQL（集中常量，对标 B 账本生成器 §5.160.2 口径）
_SQL_BID_PATHS = "SELECT blueprint_id, path FROM nodes WHERE blueprint_id IS NOT NULL AND blueprint_id <> ''"
_SQL_ALL_BIDS = "SELECT DISTINCT blueprint_id FROM nodes WHERE blueprint_id IS NOT NULL AND blueprint_id <> ''"


def _is_py_in_scope(file_path: str) -> bool:
    """新增 .py 触发面：src/zephyr/+scripts/ 能力模块（豁免面同 TRANSLATION-COVERAGE）。"""
    if not file_path.endswith(".py"):
        return False
    if is_test_exempt(file_path):
        return False
    norm = file_path.replace("\\", "/")
    if "demos" in norm.split("/"):
        return False
    base = norm.rsplit("/", 1)[-1]
    if base.startswith("test_") or base.endswith("_test.py"):
        return False
    if norm.endswith("__init__.py"):
        return False
    if "/_archive/" in norm or norm.startswith("_archive/"):
        return False
    return norm.startswith(_SRC_ZEPHYR_PREFIX) or norm.startswith(_SCRIPTS_PREFIX)


def _get_staged_new_files(gateway) -> tuple[list[str], list[str]] | None:
    """staged 新增文件分流 (新 .py in-scope, 新 blueprint.md)。git 失败返回 None（fail-open）。"""
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        if diff_result.returncode != 0:
            logger.warning("TDM-MOUNT-COVERAGE fail-open: git diff 失败(rc=%d)。", diff_result.returncode)
            return None
        new_py: list[str] = []
        new_bp: list[str] = []
        for line in diff_result.stdout.strip().splitlines():
            path = line.strip().replace("\\", "/")
            if not path:
                continue
            if path.endswith(_BLUEPRINT_BASE) and path.startswith(_BLUEPRINT_DIR_PREFIX):
                new_bp.append(path)
            elif _is_py_in_scope(path):
                new_py.append(path)
        return new_py, new_bp
    except Exception as e:  # noqa: BLE001 — git 异常=环境异常
        logger.warning("TDM-MOUNT-COVERAGE fail-open: git diff 异常(%s: %s)。", type(e).__name__, e, exc_info=True)
        return None


def _read_staged_text(gateway, path: str) -> str | None:
    """读暂存区版本内容（图+模块同批口径的真源面）；不可达回退工作树，再不可达返回 None。"""
    try:
        r = gateway.run_git(["git", "show", f":{path}"])
        if r.returncode == 0:
            return r.stdout
    except Exception:  # noqa: BLE001 — 回退工作树
        pass
    try:
        p = gateway.project_root / path
        if p.exists():
            return p.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001 — 双通道皆败
        logger.warning("TDM-MOUNT-COVERAGE fail-open: 读真源失败 %s(%s: %s)。", path, type(e).__name__, e)
    return None


def _load_shared_helpers():
    """懒加载共享助手（跨 src/scripts 边界，对标 translation gate 的 sys.path 注入模式）。"""
    try:
        from zephyr.shared.io.paths import REPO_ROOT

        shared_dir = str(REPO_ROOT / "scripts" / "governance")
        if shared_dir not in sys.path:
            sys.path.insert(0, shared_dir)
        from _shared.mount_obligation import (  # noqa: PLC0415
            build_mounted_set,
            collect_map_nodes,
            extract_blueprint_module_id,
            has_not_trading_marker,
        )

        return build_mounted_set, collect_map_nodes, extract_blueprint_module_id, has_not_trading_marker
    except Exception as e:  # noqa: BLE001 — loader 不可达=环境异常
        logger.warning("TDM-MOUNT-COVERAGE fail-open: 挂载助手不可达(%s: %s)。", type(e).__name__, e, exc_info=True)
        return None


def _depgraph_maps() -> tuple[dict[str, list[str]], set[str]] | None:
    """depgraph 只读反查面：(blueprint_id → [path]) 与蓝图锚全集。不可达返回 None（fail-open）。"""
    try:
        from zephyr.infrastructure.database_service import DatabaseService

        ds = DatabaseService()
        conn = ds.get_depgraph_conn(read_only=True)
        cur = conn.cursor()
        cur.execute(_SQL_BID_PATHS)
        bid_paths: dict[str, list[str]] = {}
        for r in cur.fetchall():
            bid_paths.setdefault(r["blueprint_id"], []).append(r["path"])
        cur.execute(_SQL_ALL_BIDS)
        all_bids = {r["blueprint_id"] for r in cur.fetchall()}
        conn.close()
        return bid_paths, all_bids
    except Exception as e:  # noqa: BLE001 — PG 不可达=环境异常
        logger.warning("TDM-MOUNT-COVERAGE fail-open: depgraph 不可达(%s: %s)。", type(e).__name__, e)
        return None


def _check_ghost_mounts(gateway, commit_rel: set[str]) -> list[str]:
    """幽灵挂载独立检视：staged 地图 diff 新增的 MOD-* 引用（module_mounts 列表成员与
    module_id 五联锚两种行形态）必须有 depgraph 蓝图锚或豁免册席位。

    与新增模块裁决解耦——地图单提交同样可造幽灵引用。环境异常（diff/depgraph/豁免册
    不可达）返回 []（fail-open 此项跳过，不误杀）。
    """
    try:
        map_paths = [p for p in commit_rel if p.startswith("config/") and p.endswith(".yaml")]
        if not map_paths:
            return []
        dg = _depgraph_maps()
        all_bids = dg[1] if dg else set()
        try:
            from _shared.mount_obligation import load_exemptions  # noqa: PLC0415

            exemptions = load_exemptions(gateway.project_root)
        except Exception:  # noqa: BLE001 — 豁免册不可读时按空册（ghost 判定从严但 diff 面仍需 MOD- 前缀）
            exemptions = {}
        violations: list[str] = []
        for path in map_paths:
            r = gateway.run_git(["git", "diff", "--cached", "--unified=0", "--", path])
            if r.returncode != 0 or not r.stdout:
                continue
            added: set[str] = set(re.findall(r"^\+\s*-\s*(MOD-[A-Za-z0-9_-]+)", r.stdout, re.M))
            added |= set(re.findall(r"^\+\s*module_id:\s*(MOD-[A-Za-z0-9_-]+)", r.stdout, re.M))
            ghost = {mid for mid in added if mid not in all_bids and mid not in exemptions}
            for mid in sorted(ghost):
                violations.append(
                    f"幽灵挂载[{path}]: 新增引用 {mid} 无 depgraph 蓝图锚——先落蓝图+depgraph 登记再挂图（防幽灵挂载）"
                )
        return violations
    except Exception as e:  # noqa: BLE001 — 检视面异常=环境异常，此项跳过
        logger.warning("TDM-MOUNT-COVERAGE fail-open: 幽灵挂载检视失败(%s: %s)。", type(e).__name__, e)
        return []


def _format_prescription(module_id: str, path: str, collision_hint: str = "") -> str:
    """三选一处方文案（spec §5 原文口径）。"""
    msg = (
        f"TDM-MOUNT-COVERAGE: 新模块 {path}（{module_id or 'module_id未解析'}）无挂载裁决。三选一修复后重提：\n"
        f"① 挂图：在总筹裁决册增量登记 mount 行（判据=policy v1.3 挂图 SOP 四判据）→ apply 写 module_mounts → 重跑 manifest；\n"
        f"② 豁免：config/tdm_mount_exemption_registry.yaml 增条（域归属+conclusion_zh+basis+review_when，缺依据不收）；\n"
        f"③ 标记：blueprint.md frontmatter 或模块头注释加 [not-trading:<大白话理由>]（非交易域设施专用）。"
    )
    if collision_hint:
        msg += f"\n撞号时另见：{collision_hint}"
    return msg


def make_tdm_mount_coverage_gate() -> GateSpec:
    """构造 TDM 挂载义务门禁 GateSpec（gate_id="TDM-MOUNT-COVERAGE"，priority=61）。

    priority=158——61 撞 RULE-EXECUTION-PAIRING、150 撞 TASK-ORDER-DOCS-LOCK（后到者让位两连，live 代码全仓扫描取 158 真空位；58/59/60=NEW-FILE-DEPGRAPH-ENFORCEMENT/TRANSLATION-COVERAGE/CREATE-GUARD）
    之后：先确认节点登记与简介齐全，再问挂载裁决。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 非 Zephyr 项目 skip（对标家族先例）
        _governance_dir = gateway.project_root / "scripts" / "governance" / "d1_structure"
        if not _governance_dir.is_dir():
            return True, "non-Zephyr project (no scripts/governance/d1_structure), skipping TDM-MOUNT-COVERAGE"

        # 2. 前置自锁：豁免册缺席=前置未落（工单A 豁免首拍未同步），skip 非拦
        exemption_path = gateway.project_root / "config" / "tdm_mount_exemption_registry.yaml"
        if not exemption_path.exists():
            return True, (
                "TDM-MOUNT-COVERAGE 前置自锁：config/tdm_mount_exemption_registry.yaml 缺席"
                "（工单A 豁免首拍未落），gate 待前置后自动激活"
            )

        # 3. staged 新增文件分流（None=fail-open）
        split = _get_staged_new_files(gateway)
        if split is None:
            return True, ""
        new_py, new_bp = split

        # 4. own 化（宪法 §3.1：外来 staged warn+审计不阻断）
        touched = list(new_py) + list(new_bp)
        touched = _split_own_foreign(gateway, touched, files, kwargs.get("session_id"), gate_name="TDM-MOUNT-COVERAGE")[
            0
        ]
        new_py = [p for p in new_py if p in touched]
        new_bp = [p for p in new_bp if p in touched]

        # 5. 只检本次 commit 文件交集（对标 depgraph gate 治本）
        commit_rel: set[str] = set()
        for f in files:
            try:
                commit_rel.add(os.path.relpath(f, str(gateway.project_root)).replace("\\", "/"))
            except (ValueError, OSError):
                continue
        new_py = [p for p in new_py if p in commit_rel]
        new_bp = [p for p in new_bp if p in commit_rel]

        # 5.5 幽灵挂载独立检视（不依赖新增模块存在——地图单提交同样可造幽灵引用）
        ghost_violations = _check_ghost_mounts(gateway, commit_rel)
        if not new_py and not new_bp:
            if ghost_violations:
                detail = "；".join(ghost_violations[:5]) + (
                    f"（还有 {len(ghost_violations) - 5} 条）" if len(ghost_violations) > 5 else ""
                )
                return False, f"TDM-MOUNT-COVERAGE: {len(ghost_violations)} 条挂载义务违规。详情: {detail}"
            return True, ""

        # 6. 共享助手 + 真源装载（fail-open 面）
        helpers = _load_shared_helpers()
        if helpers is None:
            return True, ""
        build_mounted_set, collect_map_nodes, extract_blueprint_module_id, has_not_trading_marker = helpers
        try:
            nodes = collect_map_nodes(gateway.project_root)
            mounted_set = build_mounted_set(nodes)
        except Exception as e:  # noqa: BLE001 — 地图不可达=环境异常
            logger.warning("TDM-MOUNT-COVERAGE fail-open: 挂载面装载失败(%s: %s)。", type(e).__name__, e)
            return True, ""
        try:
            from _shared.mount_obligation import load_exemptions  # noqa: PLC0415

            exemptions = load_exemptions(gateway.project_root)
        except Exception as e:  # noqa: BLE001 — 豁免册不可读=环境异常（存在性已在步骤2验过）
            logger.warning("TDM-MOUNT-COVERAGE fail-open: 豁免册读取失败(%s: %s)。", type(e).__name__, e)
            return True, ""

        # 7. depgraph 反查面（fail-open）
        dg = _depgraph_maps()
        bid_paths = dg[0] if dg else {}
        all_bids = dg[1] if dg else set()

        violations: list[str] = []

        # 7.5 同批蓝图文本预载（③ 标记与 ⑨ 锚一致性共用；读不到的跳过）
        bp_texts: dict[str, str] = {}
        for bp in new_bp:
            bp_text = _read_staged_text(gateway, bp)
            if bp_text is not None:
                bp_texts[bp] = bp_text

        # 8. 新 .py 模块逐台裁决
        for path in new_py:
            py_text = _read_staged_text(gateway, path)
            if py_text is None:
                continue  # 读不到内容=环境异常，fail-open 此文件
            m = _RE_PY_BP_ANCHOR.search(py_text)
            module_id = m.group(1).strip() if m else ""
            if not module_id:
                # 无锚行：depgraph 反查兜底（58 号 gate 已保证登记存在）
                module_id = ""
                for bid, paths in bid_paths.items():
                    norm = {p.replace("\\", "/") for p in paths}
                    if path in norm:
                        module_id = bid
                        break
            # ① 已挂（staged 版挂载面并集）＋ ref 直挂面（任一 staged 图节点 module_ref 精确
            #    指向本文件——零 DB 依赖的确定性判定；ref 折算全量口径归 B 账本/reconciler）
            ref_mounted = any(
                str(n.get("module_ref", "")).replace("\\", "/") == path for n in nodes if n.get("module_ref")
            )
            if (module_id and module_id in mounted_set) or ref_mounted:
                continue
            # ② 豁免册命中
            if module_id and module_id in exemptions:
                continue
            # ③ [not-trading:<理由>] 标记（本文件头；或同批 frontmatter module_id 精确匹配的
            #    companion blueprint——锚精确匹配防跨模块标记误放）
            marker = has_not_trading_marker(py_text)
            if not marker and module_id:
                for bp, bp_text in bp_texts.items():
                    if extract_blueprint_module_id(bp_text) == module_id and has_not_trading_marker(bp_text):
                        marker = "companion-blueprint"
                        break
            if marker:
                continue
            # 撞号判据：module_id 已注册到不同 path（e 裁决册 no2 形态）
            collision_hint = ""
            if module_id and module_id in bid_paths:
                others = [p.replace("\\", "/") for p in bid_paths[module_id] if p.replace("\\", "/") != path]
                if others:
                    collision_hint = (
                        f"module_id {module_id} 已被 {', '.join(others[:3])} 持有——按 e 裁决册 no2 案例取真空位新号"
                    )
                    violations.append(f"撞号[{path}]: {collision_hint}")
                    continue
            violations.append(_format_prescription(module_id, path))

        # 9. 蓝图锚一致性（新增 blueprint.md；文本已于 7.5 预载）
        for bp, bp_text in bp_texts.items():
            bp_mid = extract_blueprint_module_id(bp_text)
            if not bp_mid:
                violations.append(f"蓝图锚缺失[{bp}]: frontmatter 无 module_id——新蓝图必须持锚（幽灵蓝图=拦）")
                continue
            # 9a. 与同批 .py [BLUEPRINT] 行一致性（frontmatter module_id == .py 锚行 module_id）
            for p in new_py:
                p_text = _read_staged_text(gateway, p)
                if not p_text:
                    continue
                pm = _RE_PY_BP_ANCHOR.search(p_text)
                if pm and pm.group(2).strip() == bp and pm.group(1).strip() != bp_mid:
                    violations.append(
                        f"蓝图锚不一致[{bp} ⇄ {p}]: frontmatter module_id={bp_mid} ≠ .py [BLUEPRINT] 行 {pm.group(1).strip()}"
                    )
            # 9b. 撞号：同 module_id 已被其他蓝图持有（depgraph 面）
            if bp_mid in bid_paths:
                others = [p.replace("\\", "/") for p in bid_paths[bp_mid] if p.replace("\\", "/") != bp]
                if others:
                    violations.append(f"蓝图撞号[{bp}]: module_id {bp_mid} 已注册到 {', '.join(others[:3])}")

        # 9c. 幽灵挂载违规并入（5.5 已独立检视——地图单提交场景在早退分支单独返回）
        violations.extend(ghost_violations)

        if not violations:
            return True, ""

        detail = "；".join(violations[:5]) + (f"（还有 {len(violations) - 5} 条）" if len(violations) > 5 else "")
        return False, f"TDM-MOUNT-COVERAGE: {len(violations)} 条挂载义务违规。详情: {detail}"

    return GateSpec(gate_id="TDM-MOUNT-COVERAGE", check=_check, priority=158)
