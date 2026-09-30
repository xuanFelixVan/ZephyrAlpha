# [BLUEPRINT] MOD-LIB-006 | docs/03_modules/_domain_library/blueprint.md | §模块清单
# [MODULE] zephyr.governance.audit.library_new_module_reconciler
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec);
#   zephyr.library.librarian (Librarian); zephyr.library.ledger_schema (derive_asset_id);
#   zephyr.governance.depgraph_schema (get_depgraph_pg_connection);
#   zephyr.shared.infra.process_pool (run_subprocess_hidden)
# [CONSUMERS] zephyr.governance.audit.reconciliation_registry（_EXTERNAL_SPEC_MODULES 构造期发现，
#   post-commit 事件触发；清单行由总筹合批插入，见 docs/_working/three_piece_infra/piece1b_library/）;
#   scripts/ 消费普查引擎（丁道，复用本模块 CONSUMER_SCOPE_* 常量与 is_doc14_layer_excluded，禁另起口径）
# [STARTUP] imported by reconciliation_registry（惰性 importlib）
# [MATURITY] testing
# [INVARIANTS] 唯一写路径=Librarian.act（禁裸 SQL/禁直连写库）；potential_consumers 口径=波13 §3.4 单一
#   scope，壬道收敛后唯一真源=zephyr.governance.consumption.scan_scope_converged（本模块 CONSUMER_SCOPE_* /
#   is_doc14_layer_excluded 均为薄别名，禁再派生），
#   零消费者 MUST 如实写空数组（显式 []=有意清空，与 ledger_schema.py:104-106 语义一致），且同一批名进
#   ISLAND-OBSERVE 观测面（观测账本=potential_consumers 列本身，禁建第二账本）；
#   grep 一次只在落地时发生（事件触发，宪法 §9.3 禁 cron/Timer/sleep-loop）；
#   全程 fail-soft（单步异常折叠为 ReconcileResult(action="warn")，库不可达 action=skip）；
#   本模块零 git 写（不 commit/不 add/不改 .gitignore）
# [MODIFY-GUARD] gate_id 不适用（reconciler，非 pre-commit gate）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——异常降级 ReconcileResult(action="warn")；
#   derive_potential_consumers 在 git 不可达时抛 RuntimeError（由调用方 fail-soft 兜住）
# [TESTS] tests/governance/test_library_reconcilers_red_blue.py
# [A_module] module_id=MOD-GOV_LIB_NEW_MODULE_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""library_new_module_reconciler — 新 .py 落 HEAD → 图书馆在编 + 消费者派生（波13 包13.2①）。

病根（实测，见同波案卷 §一）：``Librarian.act`` 是总账唯一写路径，但"新建 .py"这一事件
从不触发登记；``potential_consumers`` 列（``ledger_schema.py:87``）唯一写手是馆员，
其回填脚本已删，读侧只剩 ``lookup --feeds`` CLI——列写了没人喂，于是"上架无客"不可见。

治本（post-commit 事件触发，禁 cron/Timer/sleep-loop）：
1. 本次 commit 里的 ``src/**.py`` / ``scripts/**.py`` 若总账无同名 home 资产 ⇒ 经
   :class:`~zephyr.library.librarian.Librarian` 的 ``act("register", ...)`` 入编；
2. 入编的同一时刻做**一次真 grep**（``git grep -l -E`` 单次调用，口径=波13 §3.4）派生
   ``potential_consumers``；零消费者如实写 ``[]`` 并把件名进 ISLAND-OBSERVE 观测面；
3. 与丁道（消费普查）的协调面=**同一列** ``lib_assets.potential_consumers``，本模块不建
   第二孤岛账本；口径常量在本模块单一驻留，丁道引擎请 import 复用（勿抄第二份）。

# algo_flow 卡待总筹补 docs/03_modules/_domain_library/algo_flow/library_new_module_reconciler.yaml
# （补卡后再挂 `# [ALGO_FLOW] external:` 锚——ALGO-FLOW-LINK 闸要求锚指真实文件，先不挂假锚）
# create-guard-not-dup: 本模块是图书馆"新 .py 入编+消费者派生"post-commit reconciler（写路径=Librarian.act 总账），与 ai_intake_l2（AI 层 intake 门）和 obj_m_models（模型画像双跑）仅共享 "_is_in_library" 字面词，能力域零重叠、非第二实现。
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Final

logger = logging.getLogger(__name__)

__all__: Final[list[str]] = [
    "CONSUMER_SCOPE_ROOTS",
    "CONSUMER_SCOPE_SUFFIXES",
    "DOC14_INFRA_TOKENS",
    "derive_potential_consumers",
    "is_doc14_layer_excluded",
    "make_library_new_module_reconciler",
    "register_new_module_asset",
]

#: 在编判定面（包13.2① 只管这两个根；tests/ 由 CREATE-GUARD 口径排除）
_IN_LIBRARY_INPUT_PREFIXES: Final[tuple[str, ...]] = ("src/", "scripts/")

# ── 波13 §3.4 单一消费者 scope——壬道收敛后唯一真源在 zephyr.governance.consumption.scan_scope_converged，
#    本车道只留薄别名（import 绑定，禁在此再派生任何口径值/谓词；第二真源=禁止）。
#    三层剔除词真源=docs/_working/decision_map_campaign/14_consumption_census.md:11，
#    收敛裁决案卷=docs/_working/three_piece_infra/scope_convergence/CASE.md §二。──────────

from zephyr.governance.consumption.scan_scope_converged import (  # noqa: E402
    CONSUMER_CAP,
    CONSUMER_SCAN_SCOPE,
    DOC14_INFRA_TOKENS,
    counts_as_consumer,
    is_doc14_layer_excluded,
)

#: 扫描根别名（§3.4 三根：src/ + scripts/ + config/——config 算消费者，TDM/任务声明是真运行输入）
CONSUMER_SCOPE_ROOTS: Final[tuple[str, ...]] = tuple(r.rstrip("/") for r in CONSUMER_SCAN_SCOPE.roots)

#: 后缀别名——**.md 与 docs/ 永不算消费者**（14 号文 IND-REV-001 假绿实证）
CONSUMER_SCOPE_SUFFIXES: Final[frozenset[str]] = frozenset(CONSUMER_SCAN_SCOPE.suffixes)


def derive_potential_consumers(
    root: Path | str,
    module_rel: str,
    *,
    grep: Callable[[str, tuple[str, ...]], list[str]] | None = None,
) -> list[str]:
    """落地时**一次真 grep** 派生 potential_consumers（§3.4 口径）。

    口径负样本面（一律不算消费者）：非 ``.py/.yaml`` 后缀、``docs/`` 全目录、
    14 号文三层（producer/display/infra，见 :func:`is_doc14_layer_excluded`）、被查件自己。

    Args:
        root: 仓库根。
        module_rel: 新件仓内相对路径（如 ``src/zephyr/library/foo.py``）。
        grep: 注入点（测试沙盘用）——``(pattern, scope_roots) -> matched_rels``；
            缺省 = 一次 ``git grep -l -E``（pathspec 只给三个根：逐文件清单会撑爆
            Windows 命令行上限，实测 WinError 206「文件名或扩展名太长」）。

    Returns:
        排序后的消费者相对路径列表（可为空——空=如实的零消费者，不是"没测"）。

    Raises:
        RuntimeError: 缺省 grep 通道 git 不可用（调用方 fail-soft，不静默当零消费者）。
    """
    stem = Path(module_rel).stem
    pattern = rf"\b{stem}\b"
    rel = module_rel.replace("\\", "/")
    matcher = grep or _default_grep(Path(str(root)))
    matched = matcher(pattern, CONSUMER_SCOPE_ROOTS)
    # 壬道收敛：负样本面（docs/.md/根外/后缀外/四层）全部由唯一真源谓词 counts_as_consumer 判定，
    # 本函数只加"被查件自己不算自己消费者"这一调用方语义（丙道旧内联口径已删——防第二真源）。
    kept = sorted({m for m in (x.replace("\\", "/") for x in matched) if m != rel and counts_as_consumer(m)})
    return kept[:CONSUMER_CAP]


def _default_grep(root: Path):
    """缺省 grep 通道＝单次 ``git grep -l -E``（绑定仓根做 cwd）。"""

    def _matcher(pattern: str, scope_roots: tuple[str, ...]) -> list[str]:
        return _git_grep_files(pattern, scope_roots, root)

    return _matcher


def _git_grep_files(pattern: str, scope_roots: tuple[str, ...], root: Path) -> list[str]:
    """单次 ``git grep -l -E`` 真 grep（零匹配 rc=1 是合法答案，不是故障）。

    Args:
        pattern: ERE 模式。
        scope_roots: pathspec 根（§3.4 三根；只给根不给逐文件清单）。
        root: 仓库根（git 的 cwd——pathspec 是仓内相对路径，cwd 错则全盘空命中）。

    Returns:
        命中文件相对路径列表（后缀/三层过滤由调用方按同一口径做，不在此重复真源）。

    Raises:
        RuntimeError: git 不可达/模式非法（rc>=2 或异常）——严禁降级成"零消费者"假绿。
    """
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    args = ["git", "--no-pager", "grep", "-l", "-E", pattern, "--", *scope_roots]
    try:
        proc = run_subprocess_hidden(args, cwd=str(root), capture_output=True, text=True, timeout=180)
    except Exception as exc:  # noqa: BLE001 — 通道故障必须上报，不当零消费者
        raise RuntimeError(f"git grep 通道不可用: {type(exc).__name__}: {exc}") from exc
    rc = getattr(proc, "returncode", 1)
    if rc == 1 and not (getattr(proc, "stderr", "") or "").strip():
        return []  # grep 语义：1=无命中
    if rc not in (0, 1):
        raise RuntimeError(f"git grep 失败 rc={rc}: {(getattr(proc, 'stderr', '') or '')[:200]}")
    out = (getattr(proc, "stdout", "") or "").splitlines()
    return [line.strip().replace("\\", "/") for line in out if line.strip()]


def register_new_module_asset(
    librarian: object,
    root: Path | str,
    module_rel: str,
    *,
    actor: str,
    consumers: list[str] | None = None,
    grep: Callable[[str, list[str]], list[str]] | None = None,
) -> dict[str, Any]:
    """把一个刚落 HEAD 的 .py 经**馆员唯一写路径**入编（禁裸 SQL）。

    Args:
        librarian: :class:`zephyr.library.librarian.Librarian`（或鸭子等价物，测试注入）。
        root: 仓库根。
        module_rel: 仓内相对路径。
        actor: 登记会话标识。
        consumers: 预派生消费者清单（None=本函数现场 grep）。
        grep: grep 注入点（测试沙盘用）。

    Returns:
        ``{asset_id, kind, home, consumers, island}``——island=True 即零消费者观测件。

    Raises:
        OSError: 文件不可读（调用方 fail-soft）。
    """
    from zephyr.library.ledger_schema import derive_asset_id

    base = Path(str(root))
    rel = module_rel.replace("\\", "/")
    text = (base / rel).read_text(encoding="utf-8", errors="replace")
    kind = "module" if rel.startswith("src/") else "file"
    asset_id = derive_asset_id(kind, rel)
    if consumers is None:
        consumers = derive_potential_consumers(base, rel, grep=grep)
    one_liner = _first_prose_line(text)
    librarian.act(
        "register",
        asset_id,
        actor=actor,
        fields={
            "kind": kind,
            "home": rel,
            "title": Path(rel).name,
            "one_liner": one_liner,
            # 显式数组（含空数组）=有意判定结论，非"没测"：COALESCE 语义见 ledger_schema.py:104-106
            "potential_consumers": list(consumers),
            "tags": ["fs", "auto-landing"],
        },
        detail={
            "source": "library_new_module_reconciler",
            "consumer_scope": "wave13_§3.4",
            "grep_hits": len(consumers),
        },
    )
    return {"asset_id": asset_id, "kind": kind, "home": rel, "consumers": list(consumers), "island": not consumers}


def _first_prose_line(text: str) -> str:
    """取模块 docstring 首行作大白话简介（无 docstring 则空串，不编造）。"""
    lines = text.splitlines()
    in_doc = False
    for raw in lines[:80]:
        line = raw.strip()
        if not in_doc:
            if line.startswith(('"""', "'''")):
                marker = line[:3]
                rest = line[3:].strip()
                if rest.startswith("[ALGO_FLOW]") or rest.startswith("#"):
                    continue
                return rest[:200] if rest and not rest.startswith(marker) else ""
            continue
        if line:
            return line[:200]
    return ""


def _is_in_library(librarian: object, module_rel: str) -> bool:
    """总账是否已有该 home 的资产（读侧只走 Librarian.lookup，禁裸 SQL）。"""
    rel = module_rel.replace("\\", "/")
    rows = librarian.lookup(rel, limit=CONSUMER_CAP) or []
    return any((row.get("home") or "").replace("\\", "/") == rel for row in rows)


# trae_060-reviewed: ①该存在——"新 .py 落 HEAD"事件从不喂总账，potential_consumers 回填脚本已删
#   ⇒ 列成死维度（实测读侧只剩 lookup --feeds），图书馆"自动更新"因此缺一半；
# ②能否合并进已有：LIBRARY-REGEN 的 trigger 面是"馆藏输入面变更→重生成页面"，其 reconcile
#   全量重采集不携 consumers，且它在 docs/library 变更时故意不触发（防 regen 风暴）——
#   把逐件消费者判定塞进去会让页面落地与在编判定互相牵连（自环风险），故独立一台、
#   只读同库同列；③治本——事件触发（commit 落地时一次真 grep），非时间触发。


def make_library_new_module_reconciler(
    gateway: object | None = None, *, librarian_factory: Callable[[], object] | None = None
):
    """构造"新 .py 落 HEAD → 图书馆在编 + 消费者派生"reconciler。

    Args:
        gateway: GitCommitGateway 实例（用 project_root）；None 时回退 REPO_ROOT。
        librarian_factory: 注入点——返回满足 ``Librarian`` 协议的对象（测试给沙盘件，
            **禁在测试里连生产 depgraph 库**）。

    Returns:
        ReconcilerSpec(gate_id="LIBRARY-NEW-MODULE", priority=201)。
    """
    from zephyr.governance.audit.reconciliation_registry import ReconcileResult, ReconcilerSpec

    if gateway is not None and getattr(gateway, "project_root", None):
        project_root = Path(str(gateway.project_root))
    else:
        from zephyr.shared.io.paths import REPO_ROOT

        project_root = Path(str(REPO_ROOT))

    def _rel(f: str) -> str:
        try:
            return os.path.relpath(f, str(project_root)).replace("\\", "/")
        except ValueError:
            return str(f).replace("\\", "/")

    def _trigger(committed_files: list[str]) -> bool:
        """命中落在 src/ 或 scripts/ 的 .py（盘上真实存在才算——删件走死亡证明人工链）。"""
        return any(
            _rel(f).startswith(_IN_LIBRARY_INPUT_PREFIXES)
            and _rel(f).endswith(".py")
            and (project_root / _rel(f)).is_file()
            for f in committed_files
        )

    def _process_committed(
        files: list[str], librarian: object, actor: str
    ) -> tuple[list[dict[str, Any]], list[str], list[str]]:
        """逐件入编（fail-soft：单件失败不拖垮整批）。返回 (registered, islands, failures)。

        （COMPLEXITY-GUARD 治本 2026-09-28：从 _reconcile 拆出逐件循环，判定零变化。）
        """
        registered: list[dict[str, Any]] = []
        islands: list[str] = []
        failures: list[str] = []
        for f in files:
            rel = _rel(f)
            if not (rel.startswith(_IN_LIBRARY_INPUT_PREFIXES) and rel.endswith(".py")):
                continue
            if not (project_root / rel).is_file():
                continue
            try:
                if _is_in_library(librarian, rel):
                    continue
                outcome = register_new_module_asset(librarian, project_root, rel, actor=actor)
            except Exception as exc:  # noqa: BLE001 — 单件失败不拖垮整批（fail-soft）
                failures.append(f"{rel}:{type(exc).__name__}")
                logger.warning("library-new-module 单件入编失败 %s: %s", rel, exc, exc_info=True)
                continue
            registered.append(outcome)
            if outcome["island"]:
                islands.append(outcome["home"])
        return registered, islands, failures

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        actor = session_id or "library-new-module"
        own_conn = None  # 仅生产分支自开的连接需自关（注入件由注入方生命周期负责）
        try:
            if librarian_factory is not None:
                librarian = librarian_factory()
            else:
                from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
                from zephyr.library.librarian import Librarian

                own_conn = get_depgraph_pg_connection()
                librarian = Librarian(own_conn)
        except Exception as exc:  # noqa: BLE001 — 库不可达不是业务失败
            logger.warning("library-new-module 总账不可达，本轮 skip: %s", exc)
            return ReconcileResult(action="skip", detail=f"library-new-module 总账不可达（skip，非缺陷）: {exc}")

        try:
            registered, islands, failures = _process_committed(committed_files, librarian, actor)
        finally:
            if own_conn is not None:
                try:
                    own_conn.close()
                except Exception:  # noqa: BLE001 — 关闭失败不改判定
                    logger.debug("library-new-module 连接关闭失败", exc_info=True)

        parts = [f"入编 {len(registered)} 件"]
        if islands:
            parts.append(
                "ISLAND-OBSERVE(potential_consumers=[]) " + str(len(islands)) + " 件: " + ", ".join(sorted(islands))
            )
        if failures:
            parts.append("失败 " + ", ".join(failures))
        detail = "library-new-module post-commit（" + actor + "）：" + "；".join(parts)
        logger.info(detail)
        if failures:
            return ReconcileResult(action="warn", detail=detail)
        return ReconcileResult(action="clean", detail=detail)

    return ReconcilerSpec(
        gate_id="LIBRARY-NEW-MODULE",
        trigger=_trigger,
        reconcile=_reconcile,
        # 读=盘上新件+总账在编判定；写=仅经 Librarian.act 改总账（零文件写、零 git 操作、零删除）
        file_ops=frozenset({"read"}),
        priority=201,  # LIBRARY-REGEN@200 之后、CAPABILITY-LOOKUP-HEALTH@220 之前
    )


def make_external_reconciler_spec(host: object | None = None):
    """ReconciliationRegistry 外部规格发现钩子入口（签名稳定）。"""
    if TYPE_CHECKING:  # pragma: no cover — 仅静态声明依赖边，运行时零导入
        import zephyr.library.librarian  # noqa: F401
    return make_library_new_module_reconciler(host)
