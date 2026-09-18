# [BLUEPRINT] MOD-GOV_SCRIPTS | tests/governance/test_shared_yaml_utils_reexport.py | §
# [MODULE] tests.governance.test_shared_yaml_utils_reexport
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] ast; pathlib; pytest（零业务依赖，纯静态解析）
# [CONSUMERS] —
# [STARTUP] manual
# [MATURITY] candidate
# [INVARIANTS] 引用符号集由扫描 scripts/** 动态得出，禁硬编码符号名；本文件只读仓不写生产路径
# [MODIFY-GUARD]
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败输出 (shim, 缺失符号, SSoT 出处) 三元组；解析失败的文件静默跳过（不误判为缺失）
# [TESTS] 本文件即测试；能红自检见 test_scanner_detects_missing_reexport_on_synthetic_repo
# [A_test] module_id=MOD-TEST-SHARED-REEXPORT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""_shared re-export 契约测试（战役车道 st-ff-shim-20260918 / 处方 req_verifier3_01）.

病根（实跑复现，非推测）
------------------------
``scripts/governance/_shared/yaml_utils.py`` 是
``src/zephyr/shared/io/yaml_utils.py`` 的 re-export 壳，SSoT 侧新增
``DEFAULT_REGISTRY_CATALOG_DIR`` 后壳未同步转出 → 唯一 sanctioned 工具
``scripts/governance/d3_metadata/add_module_translation.py --help`` 直接
ImportError（TRANSLATION-COVERAGE 门禁指定的修复入口整条不可用）。
失效模式 = **SSoT 加符号 → 壳不同步 → 只有运行期才炸，无任何静态检出面**。

本文件把那层"检出面"补上，判据全部机械扫描得出：

1. 引用侧：扫 ``scripts/**.py`` 的模块级 ``from _shared.X import a, b``，
   汇总每个壳被实际引用的符号集（禁硬编码符号名 —— 否则 SSoT 再加符号时
   本测试同样失明，违宪法 §9.5"静态清单禁手工维护"）。
2. 供给侧：解析壳自身的模块级绑定（def/class/顶层赋值/具名导入/
   ``import *`` 展开/包的子模块）得到其可用符号集。
3. 契约：引用集 ⊆ 供给集；壳若声明静态 ``__all__`` 则再加一道
   引用集 ⊆ ``__all__``（``__all__`` 不得漏项，也不得含幽灵名）。
4. 反向契约：壳的具名转清单项必须在真源里真实存在（防 SSoT 改名/删符号
   后壳在 import 期就炸）。

覆盖面按目录枚举（``scripts/governance/_shared/*.py`` 全量参数化），新增壳
自动入面，不维护清单。所有写入仅发生在 ``tmp_path`` 下的合成迷你仓。
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

# ── 仓内路径（tests/governance/<file>.py → parents[2] = repo root）──
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
_SKIP_DIR_NAMES = frozenset({"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"})
# 具名转出的递归展开深度上限（防循环 import 无限递归）
_MAX_EXPAND_DEPTH = 4
# 只在模块级收集绑定；这些容器是"条件式模块级定义"（try: import x / if 分支）
_CONDITIONAL_CONTAINERS = (ast.If, ast.Try, ast.With, ast.AsyncWith, ast.ExceptHandler)
_BINDING_NODES = (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Import, ast.ImportFrom)
_DEF_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


# ============================================================================
# 静态解析原语
# ============================================================================


def _shared_dir_of(repo_root: Path) -> Path:
    """_shared 包目录（同一布局在合成仓里可复刻）。"""
    return repo_root / "scripts" / "governance" / "_shared"


def _parse(path: Path) -> ast.Module | None:
    """解析 .py 为 AST；语法/编码异常返回 None（调用侧跳过，不误判为缺失）。"""
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
        return None


def _import_froms(tree: ast.Module) -> list[ast.ImportFrom]:
    """模块级 ImportFrom（不下钻函数体——函数内延迟 import 不构成壳契约）。"""
    return [node for node in tree.body if isinstance(node, ast.ImportFrom)]


def _assign_names(node: ast.stmt) -> set[str]:
    """取赋值语句左侧被绑定的名字（含 tuple/list 拆包）。"""
    raw = getattr(node, "targets", None) or [node.target]
    out: set[str] = set()
    for tgt in raw:
        out |= {child.id for child in ast.walk(tgt) if isinstance(child, ast.Name)}
    return out


def _binding_statements(tree: ast.Module) -> list[ast.stmt]:
    """模块级绑定语句，含 try/if/with 条件分支内的定义（常见于降级 import）。"""
    out: list[ast.stmt] = []
    pending: list[ast.AST] = list(tree.body)
    while pending:
        node = pending.pop()
        if isinstance(node, _DEF_NODES) or isinstance(node, _BINDING_NODES):
            out.append(node)
        elif isinstance(node, _CONDITIONAL_CONTAINERS):
            pending.extend(ast.iter_child_nodes(node))
    return out


def _top_level_names(tree: ast.Module) -> set[str]:
    """模块可用名字：def/class/顶层赋值/import 绑定（剔除 ``*``）。"""
    names: set[str] = set()
    for node in _binding_statements(tree):
        if isinstance(node, _DEF_NODES):
            names.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names |= {a.asname or a.name.split(".")[0] for a in node.names if a.name != "*"}
        else:
            names |= _assign_names(node)
    return names


def _static_dunder_all(tree: ast.Module) -> frozenset[str] | None:
    """静态字面量 ``__all__``；动态/不可静态求值返回 None（不参与判定）。"""
    for node in _binding_statements(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and "__all__" in _assign_names(node):
            value = node.value
            if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
                items = [e.value for e in value.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                if len(items) == len(value.elts):
                    return frozenset(items)
            return None
    return None


# ============================================================================
# import 目标解析（点分模块名 → 磁盘文件）
# ============================================================================


def _as_module_file(base: Path, parts: tuple[str, ...]) -> Path | None:
    """parts 指向的模块 .py 或包 __init__.py；不存在返回 None。"""
    if not parts:
        init = base / "__init__.py"
        return init if init.is_file() else None
    candidate = base.joinpath(*parts)
    as_file = candidate.with_suffix(".py")
    if as_file.is_file():
        return as_file
    as_pkg = candidate / "__init__.py"
    return as_pkg if as_pkg.is_file() else None


def _absolute_target(parts: tuple[str, ...], repo_root: Path) -> Path | None:
    """绝对 import 的落盘位置：``_shared.*`` 走 scripts/governance/_shared，
    ``scripts.*`` 走仓根，其余（zephyr.* 等）先试 src/ 再试仓根。"""
    if parts[0] == "_shared":
        return _as_module_file(_shared_dir_of(repo_root), parts[1:])
    if parts[0] == "scripts":
        return _as_module_file(repo_root, parts)
    return _as_module_file(repo_root / "src", parts) or _as_module_file(repo_root, parts)


def _relative_target(consumer: Path, node: ast.ImportFrom, repo_root: Path) -> Path | None:
    """相对 import：按 level 从消费方目录逐级上溯。"""
    base = consumer.parent
    for _ in range(node.level - 1):
        base = base.parent
    parts = tuple(node.module.split(".")) if node.module else ()
    target = _as_module_file(base, parts)
    if target is not None:
        return target
    return _absolute_target(("_shared",) + parts, repo_root)


def _import_target(consumer: Path, node: ast.ImportFrom, repo_root: Path) -> Path | None:
    """ImportFrom 的仓内落盘文件；三方库/标准库返回 None。"""
    if node.level:
        return _relative_target(consumer, node, repo_root)
    if not node.module:
        return None
    return _absolute_target(tuple(node.module.split(".")), repo_root)


# ============================================================================
# 供给侧：某模块实际能对外提供哪些名字
# ============================================================================


def _submodule_names(mod: Path) -> set[str]:
    """包的子模块名（``from pkg import sub`` 合法即使 __init__ 是空的）。"""
    if mod.name != "__init__.py":
        return set()
    return {p.stem for p in mod.parent.glob("*.py") if p.stem != "__init__"}


def _star_visible_names(
    mod: Path, repo_root: Path, cache: dict[Path, frozenset[str]], depth: int
) -> set[str]:
    """``import *`` 的可见名字：静态 __all__ 优先，否则全部非下划线开头名字。"""
    tree = _parse(mod)
    if tree is None:
        return set()
    declared = _static_dunder_all(tree)
    if declared is not None:
        return set(declared)
    return {n for n in _provided_names(mod, repo_root, cache, depth) if not n.startswith("_")}


def _provided_names(
    mod: Path,
    repo_root: Path,
    cache: dict[Path, frozenset[str]] | None = None,
    depth: int = 0,
) -> frozenset[str]:
    """模块对外可被 ``from mod import X`` 取到的名字集合（递归展开 ``import *``）。"""
    if cache is None:
        cache = {}
    if mod in cache:
        return cache[mod]
    cache[mod] = frozenset()  # 占位破环
    tree = _parse(mod)
    if tree is None:
        return frozenset()
    names = _top_level_names(tree) | _submodule_names(mod)
    if depth < _MAX_EXPAND_DEPTH:
        for node in _import_froms(tree):
            if not any(a.name == "*" for a in node.names):
                continue
            src = _import_target(mod, node, repo_root)
            if src is not None:
                names |= _star_visible_names(src, repo_root, cache, depth + 1)
    result = frozenset(names)
    cache[mod] = result
    return result


# ============================================================================
# 引用侧：scripts/** 从各壳实际引用了哪些符号
# ============================================================================


def _iter_py(paths: tuple[Path, ...]) -> list[Path]:
    out: list[Path] = []
    for root in paths:
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.py")):
            if _SKIP_DIR_NAMES.isdisjoint(p.parts):
                out.append(p)
    return out


def _scan_references(
    repo_root: Path, consumer_dirs: tuple[Path, ...]
) -> tuple[dict[Path, set[str]], list[tuple[str, Path, str]]]:
    """一次扫描出两面：{提供方: 被引符号集} + [(消费方相对路径, 提供方, 符号)]。

    引用集完全由 AST 扫出——禁硬编码符号名（否则 SSoT 再加符号时本测试同样失明）。
    """
    shared_dir = _shared_dir_of(repo_root)
    refs: dict[Path, set[str]] = {}
    triples: list[tuple[str, Path, str]] = []
    for path in _iter_py(consumer_dirs):
        tree = _parse(path)
        if tree is None:
            continue
        for node in _import_froms(tree):
            target = _import_target(path, node, repo_root)
            if target is None or shared_dir not in target.parents:
                continue
            for a in node.names:
                if a.name == "*":
                    continue
                refs.setdefault(target, set()).add(a.name)
                triples.append((_rel(path, repo_root), target, a.name))
    return refs, triples


def _where_defined(provider: Path, name: str, repo_root: Path) -> list[str]:
    """诊断：该符号存在于 provider 的哪些转出真源里（定位"壳漏转出"vs"仓内不存在"）。"""
    tree = _parse(provider)
    if tree is None:
        return []
    cache: dict[Path, frozenset[str]] = {}
    hits: list[str] = []
    for node in _import_froms(tree):
        src = _import_target(provider, node, repo_root)
        if src is None or name not in _provided_names(src, repo_root, cache):
            continue
        try:
            hits.append(src.relative_to(repo_root).as_posix())
        except ValueError:
            hits.append(src.as_posix())
    return hits


def _named_reexport_claims(provider: Path, repo_root: Path) -> list[tuple[str, str]]:
    """壳的具名转出清单 [(真源相对路径, 符号名)]——反向契约的输入。"""
    tree = _parse(provider)
    if tree is None:
        return []
    cache: dict[Path, frozenset[str]] = {}
    claims: list[tuple[str, str]] = []
    for node in _import_froms(tree):
        src = _import_target(provider, node, repo_root)
        if src is None:
            continue
        try:
            rel = src.relative_to(repo_root).as_posix()
        except ValueError:
            rel = src.as_posix()
        for a in node.names:
            if a.name != "*":
                claims.append((rel, a.name))
    return claims


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


# ── 真仓扫描结果（收集期一次，参数化用）──
_SCANNED_FILES = _iter_py((_SCRIPTS_DIR,))
_SHIM_FILES = sorted(p for p in _shared_dir_of(_REPO_ROOT).glob("*.py") if p.name != "__init__.py")
_REFS, _REF_TRIPLES = _scan_references(_REPO_ROOT, (_SCRIPTS_DIR,))
_TOTAL_REF_PAIRS = sum(len(v) for v in _REFS.values())


# ============================================================================
# 契约 1：引用集 ⊆ 供给集（现故障的检出面）
# ============================================================================


@pytest.mark.parametrize("shim", _SHIM_FILES, ids=lambda p: p.name)
def test_no_referenced_symbol_is_dropped_by_the_shim(shim: Path) -> None:
    """契约 1（本役病根）：真源里有、壳没转出 = 漏转出 → 运行期 ImportError。

    零容忍：只要被 scripts/** 引用、又确实存在于该壳的某个转出真源里，
    壳就必须转出它（或消费方改道）。这类缺失一旦新增，本判据立刻红。
    """
    missing = sorted(_REFS.get(shim, set()) - _provided_names(shim, _REPO_ROOT))
    dropped = {name: _where_defined(shim, name, _REPO_ROOT) for name in missing}
    offenders = {name: srcs for name, srcs in dropped.items() if srcs}
    assert not offenders, f"{_rel(shim, _REPO_ROOT)} 漏转出被引用符号（真源在括号内）：" + "; ".join(
        f"{name} <- {', '.join(srcs)}" for name, srcs in sorted(offenders.items())
    )


# 存量悬空引用基线（= (消费方, 壳, 符号) 三元组）：符号在壳及其转出真源里都不存在。
# 与"漏转出"不同型——无符号可补转出，治本要改消费方或补实现，属其它模块的独占面。
# 本车道只把它钉成棘轮：新增悬空引用即红；顺手修掉存量也即红（逼着回来更新本基线）。
# 三件均已实跑亲验 ImportError（见车道报告 T3 表），非推断。
_KNOWN_DANGLING_REFERENCES: frozenset[tuple[str, str, str]] = frozenset(
    {
        (
            "scripts/governance/d1_structure/audit_directory_integrity.py",
            "scripts/governance/_shared/frontmatter.py",
            "extract_module_id",
        ),
        (
            "scripts/governance/d3_metadata/validate_module_id.py",
            "scripts/governance/_shared/frontmatter.py",
            "extract_module_id",
        ),
        (
            "scripts/governance/d5_architecture/validators/validate_depends_on_format.py",
            "scripts/governance/_shared/frontmatter.py",
            "parse_frontmatter_raw_from_file",
        ),
    }
)


def test_dangling_shared_references_do_not_grow() -> None:
    """契约 1b（棘轮）：引用了壳根本给不出的符号 = 消费方脚本 import 期即炸，不得新增。"""
    cache: dict[Path, frozenset[str]] = {}
    dangling = {
        (consumer, _rel(provider, _REPO_ROOT), name)
        for consumer, provider, name in _REF_TRIPLES
        if name not in _provided_names(provider, _REPO_ROOT, cache) and not _where_defined(provider, name, _REPO_ROOT)
    }
    new = sorted(dangling - _KNOWN_DANGLING_REFERENCES)
    fixed = sorted(_KNOWN_DANGLING_REFERENCES - dangling)
    assert not new, f"新增悬空 _shared 引用（消费方 import 期必 ImportError）：{new}"
    assert not fixed, f"存量悬空引用已被修掉——请同步删除基线条目以恢复检出面：{fixed}"


# ============================================================================
# 契约 2：__all__ 与引用集同步（壳一旦声明 __all__ 就必须诚实）
# ============================================================================


@pytest.mark.parametrize("shim", _SHIM_FILES, ids=lambda p: p.name)
def test_dunder_all_stays_in_sync_with_referenced_symbols(shim: Path) -> None:
    """声明了静态 __all__ 的壳：引用集必须 ⊆ __all__，且 __all__ 不含幽灵名。"""
    tree = _parse(shim)
    assert tree is not None, f"无法解析 {_rel(shim, _REPO_ROOT)}"
    declared = _static_dunder_all(tree)
    if declared is None:
        pytest.skip(f"{_rel(shim, _REPO_ROOT)} 未声明静态 __all__（不强制，声明后本判据自动生效）")
    referenced = _REFS.get(shim, set())
    provided = _provided_names(shim, _REPO_ROOT)
    not_exported = sorted(referenced - declared)
    phantoms = sorted(declared - provided)
    assert not not_exported, f"{_rel(shim, _REPO_ROOT)} 的 __all__ 漏了被引用符号：{not_exported}"
    assert not phantoms, f"{_rel(shim, _REPO_ROOT)} 的 __all__ 含未绑定幽灵名：{phantoms}"


# ============================================================================
# 契约 3：反向——壳的具名转清单不得引用真源已不存在的符号
# ============================================================================


@pytest.mark.parametrize("shim", _SHIM_FILES, ids=lambda p: p.name)
def test_named_reexport_targets_exist_in_source_module(shim: Path) -> None:
    """壳里 ``from <真源> import <名字>`` 的每个名字必须在该真源中真实存在。"""
    cache: dict[Path, frozenset[str]] = {}
    broken = [
        f"{name}（真源 {rel} 未定义）"
        for rel, name in _named_reexport_claims(shim, _REPO_ROOT)
        if name not in _provided_names(_REPO_ROOT / rel, _REPO_ROOT, cache)
    ]
    assert not broken, f"{_rel(shim, _REPO_ROOT)} 转出真源不存在的符号：{broken}"


# ============================================================================
# 契约 4：检出面自身不能空转（防扫描器静默失效 → 假绿）
# ============================================================================


def test_scanner_actually_sees_a_nontrivial_reference_surface() -> None:
    """引用集必须非平凡——扫描器一旦失效（路径根算错/解析全抛异常）本测试先红。"""
    assert len(_SCANNED_FILES) >= 300, f"scripts/** 仅扫到 {len(_SCANNED_FILES)} 个 .py，路径根可疑"
    assert _SHIM_FILES, f"未枚举到任何壳：{_shared_dir_of(_REPO_ROOT)}"
    assert _TOTAL_REF_PAIRS >= 60, f"仅扫到 {_TOTAL_REF_PAIRS} 个 (壳,符号) 引用对，扫描器可疑"
    covered = {k.name for k in _REFS}
    assert len(covered) >= 5, f"仅 {sorted(covered)} 有消费方，覆盖面判据失效"


def test_scanner_detects_missing_reexport_on_synthetic_repo(tmp_path: Path) -> None:
    """合成迷你仓自检：SSoT 加符号、壳不同步 → 检出面必须变红（判据自证非空转）。"""
    repo = tmp_path / "repo"
    shared = _shared_dir_of(repo)
    sso_root = repo / "src" / "zephyr" / "shared" / "io"
    for d in (shared, sso_root, repo / "scripts"):
        d.mkdir(parents=True, exist_ok=True)
    (shared / "__init__.py").write_text("", encoding="utf-8")
    (sso_root / "__init__.py").write_text("", encoding="utf-8")
    (sso_root / "yaml_utils.py").write_text("ALPHA = 1\nBETA = 2\n\ndef gamma():\n    return 3\n", encoding="utf-8")
    (shared / "yaml_utils.py").write_text(
        "from zephyr.shared.io.yaml_utils import ALPHA, gamma\n__all__ = ['ALPHA', 'gamma']\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "consumer.py").write_text(
        "from _shared.yaml_utils import ALPHA, BETA, gamma\n",
        encoding="utf-8",
    )

    refs, triples = _scan_references(repo, (repo / "scripts",))
    shim = shared / "yaml_utils.py"
    assert refs.get(shim) == {"ALPHA", "BETA", "gamma"}, "引用集未按扫描结果得出"
    assert {n for _, _, n in triples} == {"ALPHA", "BETA", "gamma"}
    missing = sorted(refs[shim] - _provided_names(shim, repo))
    assert missing == ["BETA"], f"合成故障未被检出（missing={missing}）——检出面失效"
    assert _where_defined(shim, "BETA", repo) == ["src/zephyr/shared/io/yaml_utils.py"], "未定位到漏转出的真源"
    declared = _static_dunder_all(_parse(shim))
    assert declared is not None and "BETA" not in declared, "对照：__all__ 同样漏项（契约 2 的输入形状）"


def test_scanner_accepts_synchronized_synthetic_shim(tmp_path: Path) -> None:
    """对照组：壳与 __all__ 都同步时判据必须判干净（防恒红型假严）。"""
    repo = tmp_path / "repo2"
    shared = _shared_dir_of(repo)
    sso_root = repo / "src" / "zephyr" / "shared" / "io"
    for d in (shared, sso_root, repo / "scripts"):
        d.mkdir(parents=True, exist_ok=True)
    (shared / "__init__.py").write_text("", encoding="utf-8")
    (sso_root / "__init__.py").write_text("", encoding="utf-8")
    (sso_root / "const.py").write_text("ALPHA = 1\nBETA = 2\n__all__ = ['ALPHA', 'BETA']\n", encoding="utf-8")
    (shared / "const.py").write_text(
        "from zephyr.shared.io.const import ALPHA, BETA\n__all__ = ['ALPHA', 'BETA']\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "consumer.py").write_text("from _shared.const import ALPHA, BETA\n", encoding="utf-8")

    refs, _ = _scan_references(repo, (repo / "scripts",))
    shim = shared / "const.py"
    assert sorted(refs[shim] - _provided_names(shim, repo)) == []
    declared = _static_dunder_all(_parse(shim))
    assert declared == frozenset({"ALPHA", "BETA"})


# ============================================================================
# 直连回归：sanctioned 工具入口必须能 --help（ImportError 的终检）
# ============================================================================


def test_sanctioned_tool_add_module_translation_help_renders() -> None:
    """TRANSLATION-COVERAGE 唯一修复入口 ``add_module_translation.py --help`` 必须可跑。

    子进程隔离：该脚本 import 期会 bootstrap sys.path，进程内测会把脏状态带进其它用例。
    """
    from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

    script = _SCRIPTS_DIR / "governance" / "d3_metadata" / "add_module_translation.py"
    assert script.is_file(), f"sanctioned 工具不存在：{script}"
    proc = run_subprocess_hidden([str(_python_executable()), str(script), "--help"], capture_output=True, text=True, timeout=120)
    out = f"{proc.stdout or ''}{proc.stderr or ''}"
    assert proc.returncode == 0, f"--help 退出码 {proc.returncode}：{out[-1500:]}"
    assert "--plain-zh" in out, f"--help 未渲染参数面：{out[-500:]}"


def _python_executable() -> str:
    import sys  # noqa: PLC0415

    return sys.executable


def test_yaml_shim_reexports_every_symbol_its_own_consumer_needs() -> None:
    """把本役故障点显式化：壳必须转出 add_module_translation.py 的全部 import。

    该脚本的引用集仍由扫描得出（不硬编码符号名），本判据只是"契约 1 + 指定消费方"的
    定位版，报错信息直接指向真因（原始事故只给一句 ImportError）。
    """
    script = _SCRIPTS_DIR / "governance" / "d3_metadata" / "add_module_translation.py"
    tree = _parse(script)
    assert tree is not None, f"无法解析 {_rel(script, _REPO_ROOT)}"
    shim = _shared_dir_of(_REPO_ROOT) / "yaml_utils.py"
    wanted: set[str] = set()
    for node in _import_froms(tree):
        if _import_target(script, node, _REPO_ROOT) == shim:
            wanted |= {a.name for a in node.names if a.name != "*"}
    assert wanted, f"{_rel(script, _REPO_ROOT)} 未从 {shim.name} 引符号——本判据的消费方假设已变，请改判据而非删测试"
    missing = sorted(wanted - _provided_names(shim, _REPO_ROOT))
    assert not missing, f"{_rel(script, _REPO_ROOT)} 需要的符号未从壳转出：{missing}"
