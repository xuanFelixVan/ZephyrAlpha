# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §
# [MODULE] scripts.governance.d5_architecture.generators.externalize_algo_flow
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.code_algorithm_extractor; scripts.governance._shared.file_utils (safe_write_text)
# [CONSUMERS] P2-1 ALGO_FLOW 出仓批（Owner 2026-09-15 授权"逐域出仓+round-trip+域测试"）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 每文件先迁移后 round-trip 断言（nodes+edges 逐项一致）失败即回滚源文件（.bak 恢复）；
#   外部 yaml 落 docs/03_modules/<domain>/algo_flow/<stem>.yaml（doc_type=architecture_view 过 DCR-001，
#   目录契约 allowed=[.md,.yaml]）；幂等（已带 external 锚的文件跳过）；域过滤 --domain/--file；
#   --dry-run 零写入；yaml 块文本 = docstring 内联块逐字节副本（含边段，block-scalar 保留原样）；
#   死块四态收口（P2-1 普查 184 件实证，2026-09-16；旧口径"docstring 外块只计数不处理"留下
#   锚+头块双真源，读卡路径永看不见头块）——几何判据唯一真源
#   =extractor.algo_flow_dead_block_spans（与 ALGO-FLOW-LINK 门禁第 3 判据共用一份规则）：
#     ① 块只在契约头且可解析 → 逐字转正进 docstring 后走同一管写出仓（header_promoted）；
#     ② 转正后仍不可解析（手写速记无 ``# - id:``）→ 留在 docstring 当单真源内联块
#        （promoted_inline，不回滚——回滚即把该件永久锁死在门禁不可提交态）；
#     ③ 已出仓/本批出仓仍有头块 → 节点 id 被 yaml 覆盖者直删，未覆盖者逐字并入 yaml 新键
#        ``algo_flow_prose``（机器块零改动）后再删（header_reconcile=reconciled）；
#     ④ 无锚无 yaml 的双位镜像件 → 以 docstring 内块为参照，只删 provably 覆盖者（deduped），
#        未覆盖即 failed（宁漏不销毁口径）；
#   ②③④ 终验四要件：死块归零 + ast 可解析 + docstring 逐字未变 + yaml 机器块逐字节未变，
#   任一不过即源码/yaml 双件字节还原（不留"头块已删/prose 未落"半成品）；
#   批级 stem 碰撞预判（P2-1 orchestrator 批实证）：同域非 __init__ 同 stem 多文件时子包件
#   确定性改道 parent__stem，dry-run 预测=落盘路径（消除盘存在改道的时序依赖）；
#   批级容量镜像（P2-1 波次 GOV-DOC-018 实证）：域 algo_flow/ 平铺数（盘上+本批）≥ T_soft-20 时
#   该域本批新件全部改道 algo_flow/<源相对域根子包>/<名>.yaml（域根件入域名桶），桶仍超阈值按
#   stem 首/次字符分片；落点名逐级消歧且绝不覆盖他人真源 yaml（覆盖即 failed）；
#   既有 yaml（source_of_truth 反查）永最优先——重跑不改道（防锚错位）；
#   截断型块（docstring 内无 [/ALGO_FLOW]）：有边→按 extractor 同一几何推止界、镜像补一行
#   收标记后出仓（节点段"见标记即止否则扫到文本尾"、边段恒扫到文本尾 ⇒ 节点/边集可证等价）；
#   无边→拒出仓（validate_graph 对无边图报"无边定义"，出仓即造门禁必拦的镜像）；
#   根层件 src/zephyr/<mod>.py 无子包=跨包位置 → 落 _domain_shared，镜像名加 root_ 前缀保 provenance；
#   零节点块报因分家（五段式散文 vs 其余不可解析），只影响台账口径不影响处置；
#   W4 自指 fixture 豁免=机械谓词 is_selfref_fixture_clone（克隆区间⊆单一 Constant str
#   或解析器家族注释示例段即豁免，禁路径白名单/裁定#273），豁免态不计作者欠账（裁定#392）；
# [MODIFY-GUARD] 无
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单文件失败跳过并计入 failed 列表（不中断批次）；--dry-run 恒 exit 0
# [TESTS] tests/governance/generators/test_externalize_algo_flow_remap.py, tests/governance/generators/test_externalize_algo_flow_mirror.py, tests/governance/test_w4_selfref_exemption.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的批量出仓器（Owner 授权批次施工，非常驻服务）
"""externalize_algo_flow.py — ALGO_FLOW 内联块批量出仓器（P2-1 契约头减负实施器）。

把 src 模块 docstring 内驻留的 ``# [ALGO_FLOW]`` 机器块（AST 可再生，均值 ~47 行/模块）
迁移到 docs/03_modules/<domain>/algo_flow/<stem>.yaml，源码 docstring 换一行锚：
    # [ALGO_FLOW] external: <yaml 相对路径>
extractor（code_algorithm_extractor）已支持 external 锚加载 → 同一 parse_algo_flow 管线。

安全序（每文件，``externalize`` 编排）：
  0. 死块定位（extractor.algo_flow_dead_block_spans）：块在 module docstring 之外即双真源，
     按形态分流——只在头且可解析→转正进 docstring（①）；转正后仍不可解析→留在 docstring
     （②）；已出仓仍有头块→yaml 覆盖者删/未覆盖者逐字进 ``algo_flow_prose``（③）；
     无锚无 yaml 的镜像件→docstring 块覆盖者删，否则拒删（④）
  1. 解析内联块（_has_inline_algo_flow）→ 抽块原文（docstring 内 [# [ALGO_FLOW]..边段尾]）；
     截断型（无收标记）止界走 extractor 同一判据 unclosed_block_end，块尾补一行收标记
     （节点/边集逐字等价）；截断型且零边则拒出仓（门禁 validate_graph 必拦无边镜像）
  2. 写外部 yaml（algo_flow: | block-scalar 逐行缩进副本）
  3. 源码 docstring 内联块+边段替换为锚行（AST 定位 docstring 行范围，禁止正则改源码体）
  4. round-trip 断言：extract_algorithm_from_code 重新解析，nodes/edges 与迁移前逐项一致
  5. 失败 → .bak 回滚源文件 + 删除 yaml，计入 failed
  6. 步骤 0 的③④在出仓后收尾：终验不过即源码+yaml 双件字节还原

Usage::
    python scripts/governance/d5_architecture/generators/externalize_algo_flow.py --domain backtest --dry-run
    python scripts/governance/d5_architecture/generators/externalize_algo_flow.py --domain backtest
    python scripts/governance/d5_architecture/generators/externalize_algo_flow.py --file src/zephyr/x/y.py
    python scripts/governance/d5_architecture/generators/externalize_algo_flow.py --files-from list.txt
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.code_algorithm_extractor import (  # noqa: E402
    _ALGO_FLOW_END,
    _ALGO_FLOW_START,
    REPO_ROOT,
    _has_inline_algo_flow,
    algo_flow_dead_block_spans,
    parse_algo_flow,
    unclosed_block_end,
)

from zephyr.shared.io.file_utils import safe_write_text  # noqa: E402

_ANCHOR_RE = re.compile(r"^#\s*\[ALGO_FLOW\]\s+external:\s*(\S+)\s*$", re.MULTILINE)

# 机器块节点行（``# - id: A3``）——判定头块是"机器块旧快照"还是"手写算法速记"
_ID_LINE_RE = re.compile(r"^#\s*-\s*id:\s*(\S+)")

# 头块里的口径若 yaml 机器块未覆盖，逐字并入 yaml 该键（文件尾追加，所有读卡器忽略未知键）
_PROSE_KEY = "algo_flow_prose"

# 五段式散文口径行（``# 输入:`` ``# 算法:`` …）——旧版机器块语法，无 ``- id:`` 行
_FIVE_SECTION_RE = re.compile(r"^#\s*(输入|特征|指标|算法|输出)\s*[:：]")

# skipped 口径（进生成的盘点台账，措辞即后续批的分派依据，勿随手改写）
_LEGACY_PROSE_SKIP_REASON = "legacy 五段式 prose (no - id: rows)"
_NO_NODES_SKIP_REASON = "block unparsable (no nodes)"
# 零边拒出仓只作用于截断型块（本批新开的通道）：已闭合零边块沿用既有口径继续出仓
# （盘上 3157 件有边 / 1 件无边先例，改判即把死块清偿路径上的件一起锁死）
_NO_EDGE_SKIP_REASON = "graph has no edges (validate_graph would block)"

# W4 自指 fixture 判据式豁免（施工授权=裁定#392；判据真源=docs/_working/archive/2026-09/
# 2026-09-18-landing-anchor-algo-flow-closeout/W4_selfref_exemption.md）：ALGO_FLOW 解析器
# 家族与其测试夹具内嵌的块样本"天然像"被它解析的目标，克隆报告（CloneGuard/欠账台账）
# 对此误报。豁免走机械谓词 is_selfref_fixture_clone（命中即豁免，AST 判定），禁逐文件
# 路径白名单（裁定#273：白名单=治理逃逸）。注意：本报因故意不入 _CONTENT_SKIP_REASONS
# ——自指 fixture 是豁免态不是作者欠账，report_algo_flow_author_debt.py 据此不计欠账。
_SELFREF_FIXTURE_SKIP_REASON = "self-referential fixture clone (W4 exemption)"

# 内容级 skipped（块定位良好、按口径不出仓）：契约头转正后留在 docstring 即与其他内联件
# 同状态，回滚反而把该件永久锁死在死块态——externalize() 据此决定不回滚
_CONTENT_SKIP_REASONS = (_LEGACY_PROSE_SKIP_REASON, _NO_NODES_SKIP_REASON, _NO_EDGE_SKIP_REASON)

# src/zephyr/<mod>.py 根层件（无子包=跨包位置）镜像名前缀：落 _domain_shared 时保 provenance
_ROOT_STEM_PREFIX = "root_"

# 既有 yaml 反查缓存：domain_dir → {source_of_truth: yaml_rel}（批9 幂等治本）
_EXISTING_YAML_CACHE: dict[str, dict[str, str]] = {}

# 批级 stem 碰撞预判表：rel_py → yaml_rel（main() 批开始前静态填充）
_PLANNED_REMAP: dict[str, str] = {}


def _plan_stem_collision_remaps(targets: list[Path]) -> None:
    """批开始前静态判定同 stem 碰撞，子包件确定性改道 ``<parent>__<stem>.yaml``。

    映射改道雷同族（b9 实证）：_yaml_rel_for 靠"盘上 yaml 已存在"改道，同批内
    后处理文件在写入前阶段不可预测（依赖 rglob 排序+落盘副作用）——dry-run 与
    正式跑路径不一致。此处按批清单预判：同 domain_dir 内非 __init__ 同 stem
    ≥2 文件时，域根件保平铺名，子包件（深度 > src/zephyr/<domain>/）加 parent 前缀；
    不同子包各得唯一名，处理顺序无关。
    """
    _PLANNED_REMAP.clear()
    by_stem: dict[tuple[str, str], list[Path]] = {}
    for p in targets:
        if p.name == "__init__.py":
            continue
        rel = p.relative_to(REPO_ROOT).as_posix()
        by_stem.setdefault((_domain_of(rel), p.stem), []).append(p)
    for (domain_dir, stem), paths in by_stem.items():
        if len(paths) < 2:
            continue
        for p in paths:
            rel_parts = p.relative_to(REPO_ROOT).parts  # src/zephyr/<domain>/... 域根件=4 段
            if len(rel_parts) > 4:  # 子包件 → <parent>__<stem>.yaml
                _PLANNED_REMAP[p.relative_to(REPO_ROOT).as_posix()] = (
                    f"docs/03_modules/{domain_dir}/algo_flow/{p.parent.name}__{stem}.yaml"
                )


def _existing_yaml_for(rel_py: str, domain_dir: str) -> str:
    """已落盘 yaml 路径优先——按 yaml 头 ``source_of_truth`` 反查（重跑映射防改道）。

    批9 实证（st-btfix-p15-20260916）：yaml 先落盘（含镜像子目录重排，b9a_remap.json）
    而源码锚后补的场景下，_yaml_rel_for 的"盘存在=碰撞"检测会把映射整体改道到
    ``parent__stem`` 新路径——重复 yaml+锚错位。真源判定以 yaml 头 source_of_truth
    反查为准：盘上已有本文件专属 yaml 即复用原路径；无匹配才走 _yaml_rel_for 推导。
    """
    cache = _EXISTING_YAML_CACHE.get(domain_dir)
    if cache is None:
        cache = {}
        root = REPO_ROOT / "docs" / "03_modules" / domain_dir / "algo_flow"
        if root.is_dir():
            for y in sorted(root.rglob("*.yaml")):
                try:
                    head = y.read_text(encoding="utf-8").splitlines()[:8]
                except OSError:
                    continue
                for ln in head:
                    if ln.startswith("source_of_truth:"):
                        cache[ln.split(":", 1)[1].strip()] = y.relative_to(REPO_ROOT).as_posix()
                        break
        _EXISTING_YAML_CACHE[domain_dir] = cache
    return cache.get(rel_py, "")


# 真源域映射：src/zephyr/<pkg> → docs/03_modules/<domain>/（与 blueprint.md actual_disk_path 对齐）
_DOMAIN_DIRS: dict[str, str] = {
    # 以 docs/03_modules/ 实存目录为准（54 目录普查，2026-09-15）
    "backtest": "_domain_backtest",
    "data": "_domain_data",
    "data_eng": "_domain_data_eng",
    "data_governance": "_domain_data_governance",
    "data_security": "_domain_data_security",
    "market_data": "_domain_mkt_data",
    "ex_core": "_domain_execution_core",
    "ex_sor": "_domain_ex_sor",
    "execution_simulation": "_domain_execution_sim",
    "trading": "_domain_trading",
    "risk": "_domain_risk",
    "factor": "_domain_factor",
    "regime": "_domain_regime",
    "simulation": "_domain_simulation",
    "pf_core": "_domain_portfolio_core",
    "pf_alloc": "_domain_pf_alloc",
    "position": "_domain_position",
    "compliance": "_domain_compliance",
    "sell_decision": "_domain_sell_decision",
    "plan_engine": "_domain_plan_engine",
    "ml_train": "_domain_machine_learning_train",
    "ml_serve": "_domain_ml_serve",
    "intelligence": "_domain_intelligence",
    "frontend": "_domain_frontend",
    "reporting": "_domain_reporting",
    "knowledge": "_domain_knowledge",
    "research": "_domain_research",
    "alt_data": "_domain_alt_data",
    "signal_ashare": "_domain_signal",
    "signal_fundamental": "_domain_fundamental_signal",
    "signal_quality": "_domain_signal_quality",
    "nlp": "_domain_intelligence",
    "cross_asset": "_domain_trading",
    "orchestrator": "_domain_orchestrator",
    "feedback_loop": "_domain_feedback_loop",
    "security": "_domain_security",
    "infrastructure": "_domain_infrastructure",
    "infra_runtime": "_domain_infrastructure_runtime",
    "infra_ops": "_domain_infrastructure_operations",
    "runtime": "_domain_infrastructure_runtime",
    "experiment_tracking": "_domain_infrastructure",
    "shared": "_domain_shared",
    "governance": "_domain_governance",
    "gov_drift": "_domain_gov_drift",
    "gov_audit": "_domain_gov_audit",
    "gov_code_quality": "_domain_governance",
    "gov_rule": "_domain_gov_rule",
    "gov_enforcement": "_domain_gov_enforcement",
    "clone_guard": "_domain_gov_enforcement",
    "autonomy_core": "_domain_autonomy_core",
    "integration": "_domain_integration",
    "digital_twin": "_domain_digital_twin",
}


def _is_root_module(parts: list[str]) -> bool:
    """``src/zephyr/<mod>.py`` 根层件判定（parts 为拆好的路径段列表）。"""
    return parts[:2] == ["src", "zephyr"] and len(parts) == 3


def _mirror_stem_for(py_path: Path, rel: str) -> str:
    """镜像文件名主干（与 _yaml_rel_for 推导同源）。

    根层件无子包可作域键，落 ``_domain_shared`` 后加 ``root_`` 前缀保 provenance
    （``source_of_truth:`` 头仍指真实源路径，机械可逆）。
    """
    stem = py_path.stem
    return f"{_ROOT_STEM_PREFIX}{stem}" if _is_root_module(rel.replace("\\", "/").split("/")) else stem


def _domain_of(py_rel: str) -> str:
    """src/zephyr/<pkg>/... → 域目录名；scripts 走 _domain_governance。

    根层件（``src/zephyr/<mod>.py``）无子包=跨包位置，落既有 ``_domain_shared``，
    ``root_`` 前缀保 provenance（旧口径 ``parts[-1]`` 会造出 ``_domain___init__`` 这类
    不存在的域目录）。
    """
    parts = py_rel.replace("\\", "/").split("/")
    if parts[0] == "scripts":
        return "_domain_governance"
    if _is_root_module(parts):
        return "_domain_shared"
    pkg = parts[2] if len(parts) > 3 else parts[-1].removesuffix(".py")
    return _DOMAIN_DIRS.get(pkg, f"_domain_{pkg}")


# ---------------------------------------------------------------------------
# GOV-DOC-018 容量镜像（P2-1 波次实证：_domain_data 平铺 116/120、_domain_signal 102/120
# ——大域（governance/infrastructure/feedback_loop/shared/gov_enforcement/security）单域
# 余量不足，平铺命名必然撞 folder_capacity_hard_limit 硬阻断。治本=落点按源子包镜像。）
# ---------------------------------------------------------------------------


def _scalability_triggers() -> tuple[int, int]:
    """(平铺改道触发, 镜像桶分片触发)——真源 thresholds.yaml directory_scalability。

    平铺触发 = T_soft(src_py_error=120) - 20：给同批其他会话的并发落盘留余量。
    分片触发 = T_hard(src_py_warn=60) + 20：子包本身超大时按 stem 字符再分，
    仍远低于硬上限，保证任何目录平铺件数有界。
    """
    hard, warn = 120, 60
    try:
        from _shared.thresholds import get as _tget  # noqa: PLC0415

        hard = int(_tget("directory_scalability.src_py_error", hard))
        warn = int(_tget("directory_scalability.src_py_warn", warn))
    except Exception:  # noqa: BLE001 — 阈值不可达回退常量（宁保守勿越限）
        pass
    return max(hard - 20, warn + 1), warn + 20


_MIRROR_TRIGGER, _BUCKET_TRIGGER = _scalability_triggers()

# 镜像落点表：rel_py → yaml 相对路径（main() 批开始前静态填充，dry-run 预测=落盘路径）
_PLANNED_MIRROR: dict[str, str] = {}
# 本批进入镜像模式的域目录（报告用，便于波次核对布局）
_MIRROR_DOMAINS: list[str] = []


def _algo_flow_root(domain_dir: str) -> Path:
    return REPO_ROOT / "docs" / "03_modules" / domain_dir / "algo_flow"


def _flat_yaml_count(domain_dir: str) -> int:
    root = _algo_flow_root(domain_dir)
    if not root.is_dir():
        return 0
    return sum(1 for p in root.iterdir() if p.is_file() and not p.name.startswith("."))


_IGNORED_DIR_NAMES: frozenset[str] | None = None


def _gitignored_dir_names() -> frozenset[str]:
    """.gitignore 里"未锚定纯目录名"型忽略规则（``logs/`` ``build/`` ``tmp/`` …）。

    镜像桶沿用源子包名，撞上这类规则会让落点 yaml 被 git 忽略：提交时静默漏件、
    源码锚点变悬空指针，且登记工具（走 ``git ls-files --others``）根本看不见它。
    带通配或带路径的锚定规则只作用于特定路径，不纳入（避免无谓改名）。
    """
    global _IGNORED_DIR_NAMES
    if _IGNORED_DIR_NAMES is not None:
        return _IGNORED_DIR_NAMES
    names: set[str] = set()
    try:
        lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        lines = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith(("#", "!", "/")):
            continue
        core = s.rstrip("/")
        if not core or "*" in core or "?" in core or "/" in core:
            continue
        names.add(core.lower())
    _IGNORED_DIR_NAMES = frozenset(names)
    return _IGNORED_DIR_NAMES


def _safe_bucket_path(bucket: str) -> str:
    """桶路径逐段规避 git 忽略名（撞名段加 ``_doc`` 后缀，确定性可复算）。"""
    if not bucket:
        return bucket
    ignored = _gitignored_dir_names()
    return "/".join(f"{seg}_doc" if seg.lower() in ignored else seg for seg in bucket.split("/"))


def _src_bucket(rel_py: str) -> tuple[str, str]:
    """(pkg, 镜像桶路径)：桶 = 源文件相对域根的子包路径；域根件桶空（调用侧补域名）。

    段名经 _safe_bucket_path 规避 .gitignore 目录型忽略规则（撞名会被静默漏提交）。
    """
    parts = rel_py.split("/")
    if parts[:2] == ["src", "zephyr"] and len(parts) > 3:
        return parts[2], _safe_bucket_path("/".join(parts[3:-1]))
    if parts[0] == "scripts" and len(parts) > 2:
        return parts[1], _safe_bucket_path("/".join(parts[2:-1]))
    return "", ""


def _flatten_base(rel_py: str) -> str:
    """末路消歧名：整条源路径拉平（源路径唯一 ⇒ 名称唯一）。"""
    parts = rel_py.split("/")
    return "_".join(parts[:-1] + [Path(parts[-1]).stem]) + ".yaml"


def _candidate_bases(py_path: Path, rel_py: str, bucket: str) -> list[str]:
    """同名消歧阶梯（确定性，与批内处理顺序无关）。

    ``__init__.py`` 沿用既有约定 ``<parent>__init__.yaml``（域根件 = ``<pkg>__init__.yaml``，
    与盘上 autonomy_core__init.yaml 等既有件同名同形）。
    """
    pkg, _ = _src_bucket(rel_py)
    parent = py_path.parent.name
    if _is_root_module(rel_py.split("/")):
        # 根层件与 _yaml_rel_for 同源：root_<stem> 优先，撞名再退到最后一路拉平名
        return [f"{_ROOT_STEM_PREFIX}{py_path.stem}.yaml", _flatten_base(rel_py)]
    if py_path.name == "__init__.py":
        owner = parent if parent and parent != "zephyr" else bucket.rsplit("/", 1)[-1]
        base = f"{owner or 'algo_flow'}__init__.yaml"
        return [base, f"{pkg}__{base}", _flatten_base(rel_py)]
    stem = py_path.stem
    return [
        f"{stem}.yaml",
        f"{parent}__{stem}.yaml" if parent and parent != "zephyr" else f"{stem}.yaml",
        f"{pkg}__{parent}__{stem}.yaml",
        _flatten_base(rel_py),
    ]


def _yaml_owned_by(yaml_path: Path, rel_py: str) -> bool | None:
    """盘上 yaml 归属判定：True=本源自有（可复用），False=他人真源占用，None=无主/不可读。"""
    if not yaml_path.is_file():
        return None
    try:
        head = yaml_path.read_text(encoding="utf-8").splitlines()[:12]
    except OSError:
        return False
    for ln in head:
        if ln.startswith("source_of_truth:"):
            return ln.split(":", 1)[1].strip() == rel_py
    return False


def _shard_dir(base: str, depth: int) -> str:
    ch = base[depth].lower() if len(base) > depth else "_"
    return ch if ch.isalnum() else "_"


def _plan_domain_mirror(domain_dir: str, items: list[tuple[Path, str]]) -> None:
    """一域本批候选件的镜像落点：分桶 → 整桶逐级消歧 → 超容量桶按 stem 字符分片。

    消歧取"整桶同一阶梯级"而非逐件先到先得——避免批内顺序影响命名（与
    _plan_stem_collision_remaps 同源的确定性要求）。仅当某件在盘上被他人真源占名时
    单独升一级；四级用尽仍冲突则不入表（回落既有推导 + 写前占用检测报 failed）。
    """
    root = _algo_flow_root(domain_dir)
    dom_short = domain_dir.removeprefix("_domain_")
    by_bucket: dict[str, list[tuple[Path, str]]] = {}
    for p, rel in items:
        pkg, bucket = _src_bucket(rel)
        by_bucket.setdefault(bucket or f"{pkg or dom_short}", []).append((p, rel))

    planned: dict[str, str] = {}  # rel → "<bucket>[/<shard>]/<base>"
    for bucket, es in by_bucket.items():
        rels = [rel for _, rel in es]
        ladders = {rel: _candidate_bases(p, rel, bucket) for p, rel in es}
        bases: dict[str, str] = {}
        for step in range(max(len(v) for v in ladders.values())):
            trial = {rel: (ladder[step] if step < len(ladder) else ladder[-1]) for rel, ladder in ladders.items()}
            if len(set(trial.values())) == len(trial):
                bases = trial
                break
        if not bases:
            bases = {rel: ladders[rel][-1] for rel in rels}
        for rel in rels:
            while _yaml_owned_by(root / bucket / bases[rel], rel) is False:
                ladder = ladders[rel]
                idx = ladder.index(bases[rel])
                if idx + 1 >= len(ladder):
                    bases.pop(rel)  # 名称空间耗尽：不猜、不覆盖
                    break
                bases[rel] = ladder[idx + 1]
        if not bases:
            continue
        # 桶容量分片：盘上实存 + 本批计划 ≥ 触发值 → 按 stem 首字符（再次字符）下钻
        disk_n = sum(1 for q in (root / bucket).glob("*.yaml") if q.is_file()) if (root / bucket).is_dir() else 0
        shard_depth = 0
        if disk_n + len(bases) >= _BUCKET_TRIGGER:
            for depth in (1, 2):
                groups: dict[str, int] = {}
                for base in bases.values():
                    key = "/".join(_shard_dir(base, i) for i in range(depth))
                    groups[key] = groups.get(key, 0) + 1
                shard_depth = depth
                if max(groups.values(), default=0) < _BUCKET_TRIGGER:
                    break
        for rel, base in bases.items():
            segs = [bucket] + [_shard_dir(base, i) for i in range(shard_depth)]
            planned[rel] = "/".join(segs + [base])
    for rel, tail in planned.items():
        _PLANNED_MIRROR[rel] = f"docs/03_modules/{domain_dir}/algo_flow/{tail}"


def _plan_capacity_mirrors(targets: list[Path]) -> None:
    """批开始前静态镜像规划（与 _plan_stem_collision_remaps 同批调用，顺序无关）。

    触发口径宁多勿少：候选=docstring 区外仍含 ``# [ALGO_FLOW]`` 起标记的文件（含最终
    会 skipped 的不可解析件）——提前改道只会让布局更碎，延后改道则会撞硬阻断。
    """
    _PLANNED_MIRROR.clear()
    _MIRROR_DOMAINS.clear()
    by_dom: dict[str, list[tuple[Path, str]]] = {}
    for p in targets:
        rel = p.relative_to(REPO_ROOT).as_posix()
        try:
            src = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if _ANCHOR_RE.search(src) or not _has_inline_algo_flow(src):
            continue
        by_dom.setdefault(_domain_of(rel), []).append((p, rel))
    for dom, items in sorted(by_dom.items()):
        if _flat_yaml_count(dom) + len(items) < _MIRROR_TRIGGER:
            continue
        _MIRROR_DOMAINS.append(dom)
        _plan_domain_mirror(dom, items)


# 批级落点唯一性消歧表：rel_py → 升档后的 yaml_rel（main() 批末统一填充）
_PLANNED_UNIQ: dict[str, str] = {}


def _predicted_yaml_rel(py_path: Path, rel: str, domain_dir: str) -> str:
    """规划期落点预测——与 externalize() 的取值链逐字一致（dry-run=落盘同源）。"""
    return (
        _existing_yaml_for(rel, domain_dir)
        or _PLANNED_UNIQ.get(rel, "")
        or _PLANNED_MIRROR.get(rel, "")
        or _PLANNED_REMAP.get(rel, "")
        or _yaml_rel_for(py_path, rel, domain_dir)
    )


def _plan_path_uniqueness(targets: list[Path]) -> None:
    """批级落点注入性收口（dry-run 普查实证碰撞族）。

    两个触发面，同一升档处置：
    ① 批内同路径多源——_plan_stem_collision_remaps 跳过 __init__.py，前提是
      ``<parent>__init__`` 命名天然唯一，不同子包同名时不成立
      （signal_fundamental/{gen,strategy}/implementations/__init__.py 都推导出
      implementations__init__.yaml，后者覆盖前者=静默丢图）。
    ② 盘上他人真源占用——跨包路由到同一域目录时（cross_asset 件路由 _domain_trading，
      推导名 core__init__.yaml 已被 trading/core/__init__.py 落盘件占据），写前守卫
      只能报 failed，重跑必然同错=永久无解；规划期升档才解得开。
    处置=按 rel 字典序逐件认领：预测名未被批内认领、且非他人真源才保留原落点，
    否则沿 _candidate_bases 阶梯升到首个可用名，阶梯用尽落 flatten
    （源路径唯一 ⇒ 名称唯一）。
    """
    _PLANNED_UNIQ.clear()
    order: list[tuple[str, Path, str, str]] = []
    for p in targets:
        rel = p.relative_to(REPO_ROOT).as_posix()
        try:
            src = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if _ANCHOR_RE.search(src) or not _has_inline_algo_flow(src):
            continue
        dom = _domain_of(rel)
        order.append((rel, p, dom, _predicted_yaml_rel(p, rel, dom)))
    claimed: set[str] = set()
    for rel, p, dom, y in sorted(order, key=lambda t: t[0]):
        if y not in claimed and _yaml_owned_by(REPO_ROOT / y, rel) is not False:
            claimed.add(y)
            continue
        dir_part = y.rsplit("/", 1)[0]
        bucket = _src_bucket(rel)[1] or dom.removeprefix("_domain_")
        picked = ""
        for base in _candidate_bases(p, rel, bucket):
            cand = f"{dir_part}/{base}"
            if cand == y or cand in claimed or _yaml_owned_by(REPO_ROOT / cand, rel) is False:
                continue
            picked = cand
            break
        if not picked:
            picked = f"{dir_part}/{_flatten_base(rel)}"
        claimed.add(picked)
        _PLANNED_UNIQ[rel] = picked


def _docstring_span(src: str) -> tuple[int, int] | None:
    """module docstring 的 (start_line_idx, end_line_idx)（0 基，含端点）。"""
    tree = ast.parse(src)
    ds = ast.get_docstring(tree)
    if not ds:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return node.lineno - 1, (node.end_lineno or node.lineno) - 1
    return None


def _zero_node_reason(docstring: str) -> str:
    """零节点块的报因分家：五段式散文（欠机器块行）vs 其余不可解析（欠逐件诊断）。

    两族都不能自动出仓——补节点/边等于替作者臆造算法语义；分开报只是让后续批能按
    口径派工（旧口径一股脑报 ``block unparsable (no nodes)`` 把两族混成一族）。
    """
    if any(_FIVE_SECTION_RE.match(ln.strip()) for ln in docstring.splitlines()):
        return _LEGACY_PROSE_SKIP_REASON
    return _NO_NODES_SKIP_REASON


def _is_content_skip_reason(reason: str) -> bool:
    """skipped 是否"块内容欠账"（而非几何/定位缺陷）——契约头转正后不回滚的判据。"""
    return any(k in reason for k in _CONTENT_SKIP_REASONS)


# ALGO_FLOW 解析器家族 API 符号——谓词B"解析器家族"的机械判据（宿主文件的 AST 引用/
# 定义任一符号即解析器机械本体）。按内容判定，非路径白名单（裁定#273）。
_PARSER_FAMILY_SYMBOLS = frozenset(
    {
        "parse_algo_flow",
        "extract_algorithm_from_code",
        "_has_inline_algo_flow",
        "_ALGO_FLOW_START",
        "_ALGO_FLOW_END",
        "algo_flow_dead_block_spans",
        "unclosed_block_end",
    }
)


def _references_parser_family(tree: ast.AST) -> bool:
    """宿主文件 AST 是否引用/定义 ALGO_FLOW 解析器家族 API（谓词B 前半）。"""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in _PARSER_FAMILY_SYMBOLS:
            return True
        if isinstance(node, ast.Attribute) and node.attr in _PARSER_FAMILY_SYMBOLS:
            return True
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if any(
                a.name.split(".")[0] in _PARSER_FAMILY_SYMBOLS or a.name in _PARSER_FAMILY_SYMBOLS for a in node.names
            ):
                return True
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in _PARSER_FAMILY_SYMBOLS:
            return True
    return False


def is_selfref_fixture_clone(src: str, start_line: int, end_line: int) -> bool:
    """W4 自指 fixture 判据式豁免谓词（机械唯一入口；行号 1 基闭区间，与 CloneGuard
    fragment 的 ``line_start``/``line_end`` 同基可直接对接）。

    判据真源：docs/_working/archive/2026-09/2026-09-18-landing-anchor-algo-flow-closeout/
    W4_selfref_exemption.md；施工授权=裁定#392；禁路径白名单=裁定#273。
      谓词A（自指 fixture）：被报克隆区间整体位于单一 ``ast.Constant`` str 节点内
        （docstring/字符串字面量=夹具样本正文，是数据不是实现——两份"克隆"零行为
        等价风险，即豁免）；
      谓词B（解析器自引用）：宿主文件自身引用/定义 ALGO_FLOW 解析器家族 API
        （_references_parser_family），且命中区间全为注释/空行——解析器文件以注释
        形态内嵌的测试性示例段（注释不进 AST，谓词A 覆盖不到的形态在此收口）。
    fixture 自指对=克隆两侧均命中本谓词（W4："非真实两实现"）；任一侧是真实实现即
    不豁免（宁误报勿漏报）。源码不可解析一律 False——豁免必须可证，证不出就不豁。
    """
    if start_line < 1 or end_line < start_line:
        return False
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError, RecursionError):
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.lineno
            e = node.end_lineno or node.lineno
            if s <= start_line and end_line <= e:
                return True  # 谓词A：克隆区间 ⊆ 单一字符串字面量
    if _references_parser_family(tree):
        lines = src.splitlines()
        hit = lines[start_line - 1 : end_line]
        if hit and all((not ln.strip()) or ln.lstrip().startswith("#") for ln in hit):
            return True  # 谓词B：解析器家族文件的注释形态示例段
    return False


def _extract_inline_block(docstring: str) -> tuple[str, int, int] | None:
    """返回 (闭合块原文含边段, 起行 idx, 止行 idx)（docstring 内 0 基）。

    两形态：
      1. 有 ``# [/ALGO_FLOW]`` → 原文止于边段尾（无边段时止于收标记）；
      2. 截断型（全篇无收标记）→ 止界走 extractor 同一几何判据 ``unclosed_block_end``
         （止于首个非空非 ``#`` 行前一行 / 文本尾），并在块尾**补**一行收标记。

    补标记可证语义零改动：``parse_algo_flow`` 节点段"见收标记即止、否则扫到文本尾"，
    边段一律从起标记扫到文本尾，而补的标记行既非节点行也非边行 → 节点集/边集逐字等价
    （P2-1 尾池裁定：镜像必为闭合块，源码只留锚行）。
    """
    lines = docstring.splitlines()
    start = end = -1
    in_block = False
    edge_tail = 0  # [/ALGO_FLOW] 后连续 # 行（边段）的最后 idx
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not in_block:
            if s.startswith("#") and _ALGO_FLOW_START in s and "external:" not in s:
                start = i
                in_block = True
            continue
        if _ALGO_FLOW_END in s:
            end = i
            edge_tail = i
            continue
        if end >= 0:
            if not s or s.startswith("#"):
                edge_tail = i
                continue
            break  # 边段结束（首个真实内容行）
    if start < 0:
        return None
    if end < 0:
        end = unclosed_block_end(lines, start)
        body = lines[start : end + 1]
        if not body or _ALGO_FLOW_END not in body[-1].strip():
            body = body + [_ALGO_FLOW_END]
        return "\n".join(body), start, end
    # 边段尾部空行并入
    while edge_tail + 1 < len(lines) and not lines[edge_tail + 1].strip():
        edge_tail += 1
    return "\n".join(lines[start : edge_tail + 1]), start, edge_tail


def _yaml_for(rel_py: str, domain_dir: str, stem: str, block: str) -> str:
    header = (
        f"# ALGO_FLOW 外部真源——{stem}（{domain_dir} 域，真源 {rel_py}）\n"
        f"# 2026-09-15 P2-1 契约头减负批量出仓：docstring 内联块逐字节副本，extractor 经\n"
        f"# external 锚加载走同一 parse_algo_flow 管线；算法公共面变化时同步更新本块。\n"
        f"doc_type: architecture_view\nttl: permanent\nmodule: {rel_py.replace('/', '.')[:-3]}\n"
        f"source_of_truth: {rel_py}\n"
    )
    body = (
        "algo_flow: |\n"
        + "\n".join(("    " + ln) if ln.strip() else "" for ln in block.rstrip("\n").splitlines())
        + "\n"
    )
    return header + body


def _yaml_rel_for(py_path: Path, rel: str, domain_dir: str) -> str:
    """外部 yaml 相对路径；同目录同 stem 并存时加父目录后缀防覆盖。"""
    stem = _mirror_stem_for(py_path, rel)
    yaml_rel = f"docs/03_modules/{domain_dir}/algo_flow/{stem}.yaml"
    if _is_root_module(rel.replace("\\", "/").split("/")):
        return yaml_rel  # 根层件 root_<stem> 源路径唯一 ⇒ 名称唯一，不进 __init__/碰撞阶梯
    if py_path.name == "__init__.py" or (REPO_ROOT / yaml_rel).exists():
        parent = py_path.parent.name
        if parent and parent not in ("zephyr",) and py_path.name != "__init__.py":
            yaml_rel = f"docs/03_modules/{domain_dir}/algo_flow/{parent}__{stem}.yaml"
        elif py_path.name == "__init__.py" and parent != "zephyr":
            yaml_rel = f"docs/03_modules/{domain_dir}/algo_flow/{parent}__init__.yaml"
        elif py_path.name == "__init__.py":
            yaml_rel = f"docs/03_modules/{domain_dir}/algo_flow/{domain_dir.removeprefix('_domain_')}__init__.yaml"
    return yaml_rel


# 双真源几何判据唯一真源在 extractor（门禁与此共用一份规则，不各写一份）
_header_block_spans = algo_flow_dead_block_spans


def _module_docstring(src: str) -> str:
    try:
        return ast.get_docstring(ast.parse(src)) or ""
    except (SyntaxError, ValueError, RecursionError):
        return ""


def _ids_of(text: str) -> set[str]:
    """块内 ``# - id: X`` 节点 id 集合（机器块格式判据；手写速记块无此行→空集）。"""
    return {m.group(1) for m in (_ID_LINE_RE.match(x.strip()) for x in text.splitlines()) if m}


def _yaml_machine_block(yaml_path: Path) -> str:
    """yaml 侧 ``algo_flow`` 机器块原文（读不到=空串，交调用方判失败）。"""
    try:
        import yaml  # noqa: PLC0415 — 仅清偿路径需要，避免批处理期无谓导入

        doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 — 普查/清偿容错：坏 yaml 由链接门禁另判
        return ""
    block = doc.get("algo_flow") if isinstance(doc, dict) else None
    return block if isinstance(block, str) else ""


def _count_unreachable_blocks(src: str) -> int:
    """docstring 外死块计数（对外口径不变，供报告与普查消费；真源=_header_block_spans）。"""
    return len(_header_block_spans(src))


def _src_with_promoted_header(src: str, spans: list[tuple[int, int, bool]]) -> str | None:
    """把契约头里的机器块转正进 module docstring（供标准出仓管线消费），返回新源码。

    只处理唯一安全形态：块整体位于 module docstring **之上**（14 字段契约头区），且
    docstring 收引号独占一行——块体逐字插在其前（截断型补一行 ``# [/ALGO_FLOW]`` 收口，
    内容零改动）。其余形态（块在 docstring 之后 / 收引号与正文同行 / 无 docstring）一律
    None，交调用方判 skipped——宁漏勿猜，绝不在源码体里造字符串。
    """
    lines = src.splitlines()
    ds = _docstring_span(src)
    if ds is None or not spans:
        return None
    start, end, closed = spans[0]
    d_start, d_end = ds
    if start >= d_start or end >= d_end or len(spans) > 1:
        return None
    if lines[d_end].strip() not in ('"""', "'''"):
        return None
    block = lines[start : end + 1]
    if not closed:
        block = block + [_ALGO_FLOW_END]
    new_lines = lines[:start] + lines[end + 1 : d_end] + block + lines[d_end:]
    text = "\n".join(new_lines)
    if src.endswith("\n"):
        text += "\n"
    try:
        ast.parse(text)
    except (SyntaxError, ValueError, RecursionError):
        return None
    if _module_docstring(text) == _module_docstring(src) or not _has_inline_algo_flow(_module_docstring(text)):
        return None
    return text


def _append_prose(yaml_path: Path, prose: str) -> tuple[bool, str]:
    """把未覆盖口径逐字追加进 yaml 的 ``algo_flow_prose`` 块标量（文件尾，键恒最后）。

    yaml 的 ``algo_flow`` 机器块永不动；新键对所有读卡路径是未知键（实测静默忽略），
    且不落在 ``source_of_truth`` 反查的前 8/12 行窗口内。
    """
    try:
        txt = yaml_path.read_text(encoding="utf-8")
    except OSError as e:
        return False, f"yaml 不可读: {e}"
    chunk = "".join(("    " + ln if ln.strip() else "") + "\n" for ln in prose.rstrip("\n").splitlines())
    if not txt.endswith("\n"):
        txt += "\n"
    if f"\n{_PROSE_KEY}:" in txt:
        # 已有 prose 键（本函数追加的恒在文件尾）：续块，幂等复核由调用方删块后再跑一次保证
        new = txt + chunk
    else:
        new = (
            txt
            + f"\n# 以下 {_PROSE_KEY} = 契约头双真源清偿归并（P2-1 死块批 2026-09-16）：\n"
            + "# 源码头块手写算法速记逐字副本，algo_flow 机器块未覆盖其口径故不删信息；\n"
            + f"{_PROSE_KEY}: |\n"
            + chunk
        )
    try:
        safe_write_text(yaml_path, new)
    except Exception as e:  # noqa: BLE001 — 写入被占等，调用方回滚
        return False, f"prose 写入失败: {type(e).__name__}"
    return True, ""


def _reconcile_header_blocks(py_path: Path, dry_run: bool, ref: str = "yaml") -> dict:
    """契约头双真源清偿：重复者删，未覆盖者逐字并入 yaml 后删。

    判据（宁保守勿丢口径）：头块是机器块格式（含 ``# - id:``）且其 id 集合 ⊙ 参照块
    的 id 集合（或块体本身是参照块子串）→ 参照已覆盖 → 删零信息损失；
    其余（手写速记 / 头块含参照没有的节点）→ 先进 ``algo_flow_prose`` 再删。

    ``ref="docstring"``：尚未出仓（无锚无 yaml）的"双位镜像"形态——参照块=docstring 内
    机器块本身（risk_layer_orchestrator 实证：头块与 docstring 块逐字相同，2026-08-18
    人工恢复副本留下的镜像）。此模式无 yaml 可归并 prose，故只删 provably 覆盖者，
    未覆盖即 failed（不造第二真源、也不静默销毁口径）。
    """
    rel = py_path.relative_to(REPO_ROOT).as_posix()
    src = py_path.read_text(encoding="utf-8")
    spans = _header_block_spans(src)
    if not spans:
        return {"file": rel, "status": "nothing"}
    yaml_path: Path | None = None
    yaml_rel = ""
    if ref == "docstring":
        extracted = _extract_inline_block(_module_docstring(src))
        if extracted is None:
            return {"file": rel, "status": "failed", "reason": "docstring 内无机器块可判覆盖"}
        machine = extracted[0]
    else:
        anchor = _ANCHOR_RE.search(src)
        if not anchor:
            return {"file": rel, "status": "failed", "reason": "头块无 external 锚可归并"}
        yaml_rel = anchor.group(1)
        yaml_path = REPO_ROOT / yaml_rel
        if not yaml_path.is_file():
            return {"file": rel, "status": "failed", "reason": f"锚指向不存在的 yaml: {yaml_rel}"}
        machine = _yaml_machine_block(yaml_path)
    if not machine.strip():
        return {"file": rel, "status": "failed", "reason": f"{ref} 参照机器块为空，无从判覆盖"}
    machine_ids = _ids_of(machine)
    lines = src.splitlines(keepends=True)
    src_lines = src.splitlines()
    prose: list[str] = []
    dropped = 0
    for start, end, _closed in sorted(spans, reverse=True):
        text = "\n".join(src_lines[start : end + 1])
        ids = _ids_of(text)
        covered = bool(ids) and ids <= machine_ids
        if not covered and text.strip() and text.strip() in machine.strip():
            covered = True
        if not covered:
            prose.insert(0, text)
        else:
            dropped += 1
        del lines[start : end + 1]
    plan = {"file": rel, "status": "dryrun", "deleted_blocks": dropped, "prose_blocks": len(prose)}
    if dry_run:
        return plan
    if prose and yaml_path is None:
        return {
            "file": rel,
            "status": "failed",
            "reason": f"{len(prose)} 个头块未被 docstring 机器块覆盖且无 yaml 可归并（不删信息）",
        }
    new_src = "".join(lines)
    py_orig = py_path.read_bytes()
    yaml_orig = yaml_path.read_bytes() if yaml_path is not None else b""
    try:
        if prose and yaml_path is not None:
            ok, why = _append_prose(yaml_path, "\n".join(prose))
            if not ok:
                return {"file": rel, "status": "failed", "reason": why}
        safe_write_text(py_path, new_src)
    except Exception as e:  # noqa: BLE001 — 写入失败即还原，不留半成品
        py_path.write_bytes(py_orig)
        if yaml_path is not None:
            yaml_path.write_bytes(yaml_orig)
        return {"file": rel, "status": "failed", "reason": f"写入异常 {type(e).__name__}"}
    # 终验：死块归零 + 源码仍可解析 + docstring 逐字未变 + yaml 机器块逐字节未变
    chk = py_path.read_text(encoding="utf-8")
    doc_ok = _module_docstring(chk) == _module_docstring(src)
    block_ok = not _header_block_spans(chk)
    mach_ok = yaml_path is None or _yaml_machine_block(yaml_path) == machine
    if not (doc_ok and block_ok and mach_ok):
        py_path.write_bytes(py_orig)
        if yaml_path is not None:
            yaml_path.write_bytes(yaml_orig)
        return {
            "file": rel,
            "status": "failed",
            "reason": f"清偿终验不过 doc={doc_ok} dead={block_ok} machine={mach_ok}",
        }
    try:
        ast.parse(chk)
    except SyntaxError as e:
        py_path.write_bytes(py_orig)
        if yaml_path is not None:
            yaml_path.write_bytes(yaml_orig)
        return {"file": rel, "status": "failed", "reason": f"清偿后语法错: {e}"}
    return {
        "file": rel,
        "status": "reconciled",
        "yaml": yaml_rel,
        "deleted_blocks": dropped,
        "prose_blocks": len(prose),
    }


def externalize(py_path: Path, dry_run: bool) -> dict:
    """单文件出仓编排：先转正契约头死块，再走标准出仓，最后清偿残留双真源。

    旧口径（只报告 unreachable 并跳过）在 184 件上留下"锚 + 头块"双真源——读卡路径
    看不见头块，于是没人再删它。此处把两种形态一次收口：
      - 无锚且块只在头 → 搬进 docstring 后走同一管写出仓（``header_promoted``）；
      - 已出仓/本批出仓且仍有头块 → 删或并入 ``algo_flow_prose``（``header_reconcile``）。
    """
    rel = py_path.relative_to(REPO_ROOT).as_posix()
    try:
        src = py_path.read_text(encoding="utf-8")
    except OSError as e:
        return {"file": rel, "status": "failed", "reason": f"读取失败 {type(e).__name__}"}
    spans = _header_block_spans(src)
    anchored = _ANCHOR_RE.search(src)
    if spans and not anchored and not _has_inline_algo_flow(_module_docstring(src)):
        promoted = _src_with_promoted_header(src, spans)
        if promoted is None:
            return {"file": rel, "status": "skipped", "reason": "header block unpromotable (no docstring)"}
        if dry_run:
            return {
                "file": rel,
                "status": "dryrun",
                "plan": "promote_header_block",
                "header_blocks": len(spans),
            }
        orig = py_path.read_bytes()
        try:
            safe_write_text(py_path, promoted)
        except Exception as e:  # noqa: BLE001 — 写入被占即放弃本件
            return {"file": rel, "status": "failed", "reason": f"转正写入失败 {type(e).__name__}"}
        res = _outbox_docstring_block(py_path, dry_run)
        if res["status"] in ("externalized", "already"):
            res["header_promoted"] = True
            return res
        if res["status"] == "skipped" and _is_content_skip_reason(res.get("reason", "")):
            # 速记块（无 ``# - id:`` 节点）按既有口径不出仓——但"块在契约头=永远读不到"
            # 才是本件缺陷。转正后留在 docstring 内即与全仓其他不可解析块同状态（内联、
            # 单真源、门禁放行），不回滚——回滚等于把不可解析件永久锁死在死块态。
            chk = py_path.read_text(encoding="utf-8")
            try:
                ast.parse(chk)
                ok = not _header_block_spans(chk) and _has_inline_algo_flow(_module_docstring(chk))
            except (SyntaxError, ValueError, RecursionError):
                ok = False
            if ok:
                return {"file": rel, "status": "promoted_inline", "reason": res["reason"], "header_promoted": True}
            res["reason"] = f"转正终验不过，已回滚（{res['reason']}）"
        py_path.write_bytes(orig)
        return res
    res = _outbox_docstring_block(py_path, dry_run)
    if spans and res["status"] in ("externalized", "already"):
        res["header_reconcile"] = _reconcile_header_blocks(py_path, dry_run)
        if res["header_reconcile"]["status"] == "failed":
            res["status"] = "failed"
            res["reason"] = f"头块清偿失败: {res['header_reconcile']['reason']}"
        return res
    if spans and res["status"] == "skipped" and not anchored:
        # 不出仓的"双位镜像"件（docstring 块为速记格式→无 yaml）：头块与 docstring 块
        # 逐字相同即可删——门禁第 3 判据对此类件同样生效，不清偿则该件永不可提交。
        dedup = _reconcile_header_blocks(py_path, dry_run, ref="docstring")
        if dedup["status"] in ("reconciled", "dryrun"):
            dedup["file"] = rel
            dedup["status"] = "deduped" if dedup["status"] == "reconciled" else "dryrun"
            dedup.setdefault("plan", "dedup_header_mirror")
            return dedup
        res["header_dedup"] = dedup
    return res


def _outbox_docstring_block(py_path: Path, dry_run: bool) -> dict:
    """单文件出仓。返回 result dict（status: externalized|already|skipped|failed|dryrun）。"""
    rel = py_path.relative_to(REPO_ROOT).as_posix()
    src = py_path.read_text(encoding="utf-8")
    dead = _count_unreachable_blocks(src)
    anchor = _ANCHOR_RE.search(src)
    if anchor:
        # 有锚即已出仓（内联块按设计已被换成锚行）——此判据必须先于内联块检查，
        # 否则幂等复跑会把已完成件报成 skipped/no inline block（dry-run 口径失真）。
        res: dict = {"file": rel, "status": "already", "yaml": anchor.group(1)}
        if dead:
            res["unreachable_blocks"] = dead
        return res
    dead_reason = f"{dead} block(s) outside module docstring (unreachable)" if dead else ""
    if not _has_inline_algo_flow(src):
        return {"file": rel, "status": "skipped", "reason": dead_reason or "no inline block"}

    tree = ast.parse(src)
    ds = ast.get_docstring(tree) or ""
    before = parse_algo_flow(ds)
    if before is None or not before.nodes:
        # 零节点两族分开报（后续批据此派工：五段式=按口径补机器块，其余=逐件诊断）
        return {"file": rel, "status": "skipped", "reason": dead_reason or _zero_node_reason(ds)}
    extracted = _extract_inline_block(ds)
    if extracted is None:
        return {"file": rel, "status": "skipped", "reason": "block span not found"}
    block = extracted[0]

    span = _docstring_span(src)
    if span is None:
        return {"file": rel, "status": "skipped", "reason": "no docstring span"}
    d_start, d_end = span

    # docstring 节点定位（窗口计算需 lineno/end_lineno）
    tree2 = ast.parse(src)
    ds_node = None
    for n in ast.walk(tree2):
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
            ds_node = n
            break

    # 外部 yaml 路径：既有 yaml（source_of_truth 反查）优先，次批级容量镜像，
    # 次批级碰撞预判，无则按平铺推导命名
    domain_dir = _domain_of(rel)
    yaml_rel = (
        _existing_yaml_for(rel, domain_dir)
        or _PLANNED_UNIQ.get(rel, "")
        or _PLANNED_MIRROR.get(rel, "")
        or _PLANNED_REMAP.get(rel, "")
        or _yaml_rel_for(py_path, rel, domain_dir)
    )
    stem = _mirror_stem_for(py_path, rel)

    # 锚行窗口：纯源码坐标实测。值↔源码行映射在含 ``\n`` 转义的 docstring 上不保真
    # （memory_bank/skill_attention 实证：desc 行内 "\n" 转义在值中展开 +3 幻影行，
    # 按值行数推窗会切穿闭合引号 → 裸 CJK 语法错误）——块首/收标记按文本定位，
    # 边段（# 注释/空行）向后延伸但封顶 docstring 末行。
    anchor_line = f"# [ALGO_FLOW] external: {yaml_rel}"
    ds_lines = src.splitlines()
    doc_end = (ds_node.end_lineno or ds_node.lineno) - 1  # docstring 末行 0 基
    ws = None
    for i in range(ds_node.lineno - 1, doc_end + 1):
        if ds_lines[i].strip() == _ALGO_FLOW_START and "external:" not in ds_lines[i]:
            ws = i
            break
    if ws is None:
        return {"file": rel, "status": "skipped", "reason": "block start marker not found in source"}
    we = None
    for i in range(ws + 1, doc_end + 1):
        if ds_lines[i].strip() == _ALGO_FLOW_END:
            we = i
            break
    if we is None:
        if not before.edges:
            # 截断型 + 无边：出仓即造门禁必拦镜像（validate_graph 报"无边定义"）——宁不出仓
            return {"file": rel, "status": "skipped", "reason": dead_reason or _NO_EDGE_SKIP_REASON}
        # 截断型块（源码区无收标记）：止界按 extractor 同一几何判据推定，再映射回
        # 源码绝对坐标——镜像补收标记（_extract_inline_block 已补），源码只留锚行。
        we = ws + unclosed_block_end(ds_lines[ws : doc_end + 1], 0)
    while we + 1 <= doc_end and (not ds_lines[we + 1].strip() or ds_lines[we + 1].lstrip().startswith("#")):
        we += 1
    if _ALGO_FLOW_START not in "\n".join(ds_lines[ws : we + 1]):
        # 窗口失准（标记折行等）——跳过该文件，宁漏勿错
        return {"file": rel, "status": "skipped", "reason": f"line mapping mismatch (window {ws}-{we})"}

    new_src_lines = ds_lines[:ws] + [anchor_line] + ds_lines[we + 1 :]
    new_src = "\n".join(new_src_lines)
    if ds.endswith("\n") or True:
        pass  # join 后补尾换行
    if src.endswith("\n"):
        new_src += "\n"

    if dry_run:
        return {"file": rel, "status": "dryrun", "yaml": yaml_rel, "block_lines": len(block.splitlines())}

    # round-trip 预验证（内存）：新源码 docstring 解析结果必须与迁移前一致
    try:
        new_tree = ast.parse(new_src)
        new_ds = ast.get_docstring(new_tree) or ""
    except SyntaxError as e:
        return {"file": rel, "status": "failed", "reason": f"new src syntax error: {e}"}
    after = parse_algo_flow(new_ds)
    loaded = None
    # 模拟 extractor 外部加载：yaml 尚未写盘前，用块原文走 parse 等价验证
    if after is None or not after.nodes:
        loaded = parse_algo_flow(block)
        if loaded is None or not loaded.nodes:
            return {"file": rel, "status": "failed", "reason": "post-parse empty"}
        after = loaded

    nodes_b = [(n.id, n.layer) for n in before.nodes]
    nodes_a = [(n.id, n.layer) for n in after.nodes]
    edges_b = [(e.src, e.dst, e.is_break) for e in before.edges]
    edges_a = [(e.src, e.dst, e.is_break) for e in after.edges]
    if nodes_b != nodes_a or edges_b != edges_a:
        return {
            "file": rel,
            "status": "failed",
            "reason": "round-trip mismatch",
            "nodes_before": nodes_b,
            "nodes_after": nodes_a,
            "edges_before": edges_b,
            "edges_after": edges_a,
        }

    # 写 yaml（safe_write_text CAS）+ 源码替换 + .bak
    yaml_path = REPO_ROOT / yaml_rel
    if _yaml_owned_by(yaml_path, rel) is False:
        # 落点已属他人真源——宁漏勿覆盖（丢一张图比静默改写别人的图轻）
        return {"file": rel, "status": "failed", "reason": f"yaml 落点被他人真源占用: {yaml_rel}"}
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(yaml_path, _yaml_for(rel, domain_dir, stem, block))
    bak = py_path.with_suffix(".py.bak")
    bak.write_bytes(py_path.read_bytes())
    try:
        safe_write_text(py_path, new_src)
    except Exception:
        bak.unlink(missing_ok=True)
        raise

    # 终验：extractor 全链路（含 yaml 加载）。不 reload——reload 重跑模块体会冲掉
    # 测试套件的 REPO_ROOT 打桩（终验于是读不到刚写的临时 yaml，误判空图），
    # 且逐件 re-import 在 2000+ 件批次上是纯开销；extractor 每次调用现读源码与 yaml。
    import _shared.code_algorithm_extractor as ext  # noqa: PLC0415

    final = ext.extract_algorithm_from_code(py_path, module_id="", truncate=False)
    final_ids = [(n.id, n.layer) for n in final.algo_flow.nodes] if final.algo_flow else None
    final_edges = [(e.src, e.dst, e.is_break) for e in final.algo_flow.edges] if final.algo_flow else None
    picked = final.source_path if final.source_type == "code" else ""
    picked_tail = picked.replace("\\", "/")
    # 尾缀比对而非全等：本函数内 importlib.reload(ext) 会重跑 extractor 模块体，
    # 测试套件的 REPO_ROOT 打桩被冲掉 → source_path 带回临时根前缀（同一文件、不同根）。
    if not (picked_tail == rel or picked_tail.endswith("/" + rel)) or final_ids != nodes_b or final_edges != edges_b:
        # 能到此步说明本文件自身声明了块 → extractor 必须解到自己。
        # 旧「__init__ 回扫子文件也算通过（rerouted_to）」宽松分支随 F-A 治本删除：
        # 真源被顶到子文件=包卡片张冠李戴，按失败回滚（字节级还原，不靠文本重排）。
        py_path.write_bytes(bak.read_bytes())
        bak.unlink(missing_ok=True)
        yaml_path.unlink(missing_ok=True)
        return {
            "file": rel,
            "status": "failed",
            "reason": "final extractor mismatch" + (" (rerouted)" if picked_tail and picked_tail != rel else ""),
            "picked": picked,
            "nodes_after": final_ids,
        }
    bak.unlink(missing_ok=True)
    out = {"file": rel, "status": "externalized", "yaml": yaml_rel, "nodes": len(nodes_b), "edges": len(edges_b)}
    if dead:
        out["unreachable_blocks"] = dead
    return out


def _iter_targets(domain: str | None, single_file: str | None, files_from: str | None = None) -> list[Path]:
    if files_from:
        # 清单模式：整波跨包一次规划（逐 pkg 调用会把同域容量规划切成多批）
        out: list[Path] = []
        for ln in (REPO_ROOT / files_from).read_text(encoding="utf-8").splitlines():
            rel = ln.strip()
            if not rel or not rel.endswith(".py"):
                continue
            p = REPO_ROOT / rel
            if p.is_file():
                out.append(p)
        return out
    if single_file:
        return [REPO_ROOT / single_file]
    root = REPO_ROOT / "src" / "zephyr" / (domain or "")
    if not root.is_dir():
        return []
    out = []
    for p in sorted(root.rglob("*.py")):
        if any(seg in {"__pycache__", "tests", "_archive"} for seg in p.parts):
            continue
        out.append(p)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ALGO_FLOW 内联块批量出仓器（P2-1）")
    parser.add_argument("--domain", help="src/zephyr/<pkg> 域（如 backtest）；缺省=全量")
    parser.add_argument("--file", help="单文件模式（相对仓库根）")
    parser.add_argument(
        "--files-from",
        dest="files_from",
        help="清单模式：每行一个仓库根相对 .py 路径（整波跨包一次规划，优先于 --domain/--file）",
    )
    parser.add_argument("--dry-run", action="store_true", help="零写入，只报告")
    parser.add_argument("--limit", type=int, default=0, help="本批最多处理 N 个（0=不限）")
    args = parser.parse_args(argv)

    targets = _iter_targets(args.domain, args.file, args.files_from)
    _plan_stem_collision_remaps(targets)
    _plan_capacity_mirrors(targets)
    _plan_path_uniqueness(targets)
    results = []
    done = 0
    for p in targets:
        if args.limit and done >= args.limit:
            break
        try:
            r = externalize(p, args.dry_run)
        except Exception as e:  # noqa: BLE001 — 单文件异常不中断批次
            r = {"file": str(p), "status": "failed", "reason": f"{type(e).__name__}: {e}"}
        if r["status"] in ("externalized", "failed"):
            done += 1
        results.append(r)

    summary: dict[str, int] = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    # 落点目录平铺件数实测（GOV-DOC-018 取证：批后仍须远低于 120 硬上限）
    dir_counts: dict[str, int] = {}
    if not args.dry_run:
        touched_dirs = {(REPO_ROOT / r["yaml"]).parent for r in results if r.get("yaml")}
        for d in sorted(touched_dirs):
            try:
                dir_counts[str(d.relative_to(REPO_ROOT)).replace("\\", "/")] = sum(
                    1 for q in d.iterdir() if q.is_file() and not q.name.startswith(".")
                )
            except OSError:
                continue
    print(
        json.dumps(
            {
                "summary": summary,
                "mirror_domains": list(_MIRROR_DOMAINS),
                "max_dir_flat_count": max(dir_counts.values(), default=0),
                "results": results,
            },
            ensure_ascii=False,
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
