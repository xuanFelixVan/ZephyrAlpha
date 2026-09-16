# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] tests.governance.test_error_code_consistency
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] 代码定义点全量登记；active 条目全有存活定义点；跨定义点重码仅限注册表 known_duplicates 白名单；码前缀全声明；注册表内部唯一；观测面=git index（tree-ish 可切 HEAD 供门禁基线差分），判定结果与门禁运行目录无关
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即漂移证据（哪个码/哪个文件/哪条注册条目）
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=test | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""#ARCH-ERRCODE-001 error_code 注册表 ↔ 代码真源双向对账门禁.

裁定模型（2026-08-18 AI-ERR-001 全域收口后机器锁定，registry v3.0.0）：
  方向 A（code→registry）：src/zephyr 全仓 error_code 定义点（AST 提取——类属性赋值
    + raise 调用 error_code= 字面量两类）必须全部登记于
    architecture_model/contracts/error_code_registry.yaml——未登记即红；
    pre-commit GATE-ERRCODE 硬阻断新增未登记码。
  方向 B（registry→code）：每条非 deprecated 条目必须有 (class, file) 精确匹配的存活
    定义点——条目说谎（类改名/文件迁移/码漂移/幻影登记）即红。
  方向 C（contract→code，2026-09-06 第七断言）：tool_contracts.yaml 全部契约码
    （error_codes[].code + tools[].errors[]）必须有活定义点，或块内显式
    "# deferred" 注释（0bd159c4 先例格式）豁免——契约码死活由机器判定，
    不再依赖模型按 backend 指针人肉推断（批三实证：Flash 因 session_handoff 段
    backend 缺 server 文件指针，把 8 个活码误判为"无 server/骨架"，deferred
    化反而造假）。deferred 码若出现活定义点亦红（防 deferred 注释腐化）。
  重码：同一 code 跨 (file, class) 定义点 >1 违反「grep 唯一命中」不变量。存量 9 码 10 处
    经 git 首引入裁定登记于注册表 known_duplicates 段（GAP-010 高敏区人审约束，改号待
    Owner 批准）——白名单外新增重码即红；白名单条目不再是真实重码（改号完工后残留）
    亦红，防白名单腐化。
  前缀：code 首段（ZA- 后第一段）必须声明于 domain_prefixes。

观测面与基线差分（2026-09-16 事故治本；裁定#279）
  病根实证：同一批 13 文件在主区直连与 serializer worktree 两条通道得到相反判决——
  ZA-PA-0031/0032/0033 三条注册条目的定义点文件当时只存在于主区工作区（未入 git），
  门禁在纯净 dev 检出的 serializer worktree 里跑文件系统 rglob 时看不到它们，方向 B
  判"无存活定义点"，把一个内容无关的批次连坐挡死 4 小时（q-…-0008 死信）。
  第一性原理：门禁的判定对象必须是「本 commit 之后仓库的状态」，而不是「本机磁盘上
  恰好有什么」；否则判决随运行目录漂移，且他会话的在途欠账由无辜批次承担。
  治本两条：①观测面改 git index（``git grep --cached`` 枚举 + ``git cat-file --batch``
  批量读），git 不可达时退回文件系统 rglob（历史行为，全工作区审计仍可显式 tree="fs"）；
  ②对外暴露 collect_violations(tree=...) 违规证据集，门禁以 index−HEAD 差分只阻断本
  commit **新增**违规，HEAD 存量违规降级 warn+留痕（对标 Google Tricorder「只报新告警」
  与 bors-ng staging 分支模型）——欠账归属回到引入它的会话，全局对账不变量一条不放松。
"""

from __future__ import annotations

import ast
import logging
import re
import subprocess
from collections import Counter
from functools import lru_cache
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "zephyr"
REGISTRY_PATH = REPO_ROOT / "architecture_model" / "contracts" / "error_code_registry.yaml"
CONTRACTS_PATH = REPO_ROOT / "src" / "zephyr" / "integration" / "mcp" / "tool_contracts.yaml"

_SRC_REL = "src/zephyr"  # git 观测面 pathspec（与 SRC_ROOT 同义，git 只认仓内相对路径）
_GIT_TIMEOUT = 180  # 单次 git 调用上限（批量读 645 blob 实测 <2s，余量给冷缓存/杀软扫描）
FS = "fs"  # tree= 哨兵：强制文件系统观测面（git 不可达时的兜底亦走此路径）
_REQUIRED_FIELDS = ("code", "class", "module", "file")

_CODE_RE = re.compile(r"^ZA-[A-Z0-9]+(?:-[A-Z0-9]+)*$")


def _literal_code(node: ast.expr | None) -> str | None:
    """提取 error_code 字面量（仅接受 ZA- 开头的纯字面字符串）。"""
    if isinstance(node, ast.Constant) and isinstance(node.value, str) and _CODE_RE.match(node.value):
        return node.value
    return None


def _git(args: list[str]) -> str | None:
    """在 REPO_ROOT 执行 git（args 为完整 argv，含首位 "git"），返回 stdout。

    不可达/非零退出返回 None（调用方 fail-soft 退回文件系统观测面）。
    """
    try:
        proc = subprocess.run(args, cwd=REPO_ROOT, capture_output=True, timeout=_GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", errors="replace")


def _read_blobs(object_names: list[str]) -> dict[str, str]:
    """单进程批量读 git 对象内容（``git cat-file --batch``）。

    逐文件 ``git show :path`` = 每文件一个子进程（645 文件 ≈ 20s，门禁时延不可接受）；
    批量协议一次喂全部对象名，stdout 按 "<oid> SP <type> SP <size> LF <content> LF" 切分。
    缺失对象输出 "<name> SP missing LF"（两段）——跳过，不计入结果。
    """
    if not object_names:
        return {}
    try:
        proc = subprocess.run(
            ["git", "cat-file", "--batch"],
            input="\n".join(object_names).encode("utf-8"),
            cwd=REPO_ROOT,
            capture_output=True,
            timeout=_GIT_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return {}
    buf = proc.stdout
    out: dict[str, str] = {}
    pos = 0
    for name in object_names:
        nl = buf.find(b"\n", pos)
        if nl < 0:
            break
        header = buf[pos:nl].decode("utf-8", errors="replace").split()
        pos = nl + 1
        if len(header) < 3:
            continue  # "<name> missing" —— 对象不存在
        size = int(header[2])
        out[name] = buf[pos : pos + size].decode("utf-8", errors="replace")
        pos += size + 1  # 内容后的换行
    return out


def _fs_sources(src_root: Path) -> list[tuple[str, str]]:
    """文件系统观测面（历史行为）：rglob 全量 .py，返回 (仓内相对路径, 内容)。"""
    out: list[tuple[str, str]] = []
    for py in sorted(src_root.rglob("*.py")):
        try:
            text = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue  # 不可读文件归 ENCODING gate 管，此处跳过不遮蔽其余判定
        try:
            rel = py.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = py.as_posix()  # 外部注入根（测试 tmp_path）无仓内相对路径
        out.append((rel, text))
    return out


def _git_sources(tree: str | None) -> list[tuple[str, str]] | None:
    """git 观测面：tree=None→index（``git grep --cached``），否则该 tree-ish（如 HEAD）。

    返回 None=git 不可达（调用方退回文件系统面）；返回空列表=真无命中（二者不可混淆，
    否则"git 坏了"会被读成"仓库干净"＝假绿）。
    """
    # 观测面必须与文件系统面同口径＝只 src/zephyr 下的 .py：git grep 不加后缀约束会把
    # tool_contracts.yaml 之类 YAML 一并枚举（实证：多灌 18 个码串，其中 5 个 deferred
    # 契约码被误判"已在代码出现"）。注意 git 的多条 pathspec 是 **OR** 不是 AND（实测
    # 追加 "*.py" 反而把 src/zephyr 之外的 .py 也灌进来），故后缀过滤在 Python 侧做。
    if tree is None:
        raw = _git(["git", "grep", "--cached", "-l", "-e", "ZA-", "--", _SRC_REL])
        files = [f for f in raw.splitlines() if f.endswith(".py")] if raw is not None else None
        names = [f":{f}" for f in files] if files else []
    else:
        raw = _git(["git", "grep", "-l", "-e", "ZA-", tree, "--", _SRC_REL])
        if raw is None:
            return None
        files = [
            ln.split(":", 1)[1]
            for ln in raw.splitlines()
            if ":" in ln and ln.split(":", 1)[1].endswith(".py")
        ]
        names = [f"{tree}:{f}" for f in files]
    if files is None:
        return None
    blobs = _read_blobs(names)
    return [(f, blobs[n]) for f, n in zip(files, names) if n in blobs]


def _iter_sources(src_root: Path, tree: str | None) -> list[tuple[str, str]]:
    """观测面解析：默认 git index，git 不可达或外部注入根时退文件系统面。

    退化必须出声（禁静默降级——architecture_issue_registry「静默降级吞错」同族教训）：
    git 面不可达却静默改用文件系统面，会让判决口径悄悄换掉且无人知晓（实证：本模块
    _git 双写 "git" argv 缺陷导致全程跑文件系统面、测试照样全绿）。注入外部根
    （src_root != SRC_ROOT，测试 tmp_path）是显式意图，不属退化，不告警。
    """
    if tree != FS and src_root == SRC_ROOT:
        got = _git_sources(tree)
        if got is not None:
            return got
        logger.warning(
            "error_code 对账观测面退化：git 不可达（tree=%s），改用文件系统 rglob——"
            "判决口径已变（磁盘态≠本 commit 后仓库态），请检查 git 可用性",
            tree,
        )
    return _fs_sources(src_root)


def _read_at(path: Path, tree: str | None) -> str | None:
    """按观测面读仓内文件。返回 None＝该观测面上文件不存在。

    三态严格区分（混淆即造假）：
      ① path 在 REPO_ROOT 之外（测试注入 tmp_path）或 tree=``FS`` → 读工作区文件；
      ② git 整体不可达 → 退回工作区文件**并告警**（口径退化禁静默）；
      ③ git 可用而该 tree-ish 无此对象 → 返回 None（该面确实没有这个文件）。
         此处若偷偷改用工作区内容，HEAD 基线就会把本 commit 自己的注册表改动读成
         "存量违规"，把真新增违规洗白——基线差分的全部价值当场归零。
    """
    try:
        rel = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.read_text(encoding="utf-8") if path.exists() else None
    if tree == FS:
        return path.read_text(encoding="utf-8") if path.exists() else None
    obj = f":{rel}" if tree is None else f"{tree}:{rel}"
    if _git(["git", "cat-file", "-e", obj]) is not None:
        return _git(["git", "show", obj])
    if _git(["git", "rev-parse", "--git-dir"]) is None:
        logger.warning(
            "error_code 对账观测面退化：git 不可达（tree=%s），改读工作区文件 %s", tree, rel,
        )
        return path.read_text(encoding="utf-8") if path.exists() else None
    return None


def scan_code_definitions(src_root: Path = SRC_ROOT, *, tree: str | None = None) -> list[dict]:
    """AST 扫描 error_code 定义点：类属性赋值 + raise Xxx(error_code=...) 字面量。

    返回 [{file, class, code, lineno}]；同 (file, class, code) 多 raise 点去重（同一逻辑码）。

    tree：观测面——None=git index（默认，＝"本 commit 之后仓库的状态"）；
    ``FS``=文件系统 rglob（历史行为，全工作区审计用）；其他字符串=该 git tree-ish
    （如 "HEAD"，门禁基线差分用）。src_root 非默认根时强制文件系统面（外部目录无 git 语义）。
    """
    rows: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for rel, text in _iter_sources(src_root, tree):
        if "error_code" not in text or "ZA-" not in text:
            continue  # 文本预过滤：无字面码文件免 AST 解析（门禁时延优化）
        try:
            ast_tree = ast.parse(text, filename=rel)
        except SyntaxError:
            continue  # 语法坏文件归 SYNTAX-VALIDATION gate；此处跳过不让单文件 fail-close 全局对账
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.ClassDef):
                for stmt in node.body:
                    value: ast.expr | None = None
                    if isinstance(stmt, ast.Assign) and any(
                        isinstance(t, ast.Name) and t.id == "error_code" for t in stmt.targets
                    ):
                        value = stmt.value
                    elif (
                        isinstance(stmt, ast.AnnAssign)
                        and isinstance(stmt.target, ast.Name)
                        and stmt.target.id == "error_code"
                    ):
                        value = stmt.value
                    code = _literal_code(value)
                    if code is not None:
                        key = (rel, node.name, code)
                        if key not in seen:
                            seen.add(key)
                            rows.append({"file": rel, "class": node.name, "code": code, "lineno": stmt.lineno})
            elif isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                func = node.exc.func
                raised_cls = func.id if isinstance(func, ast.Name) else None
                if raised_cls is None:
                    continue
                for kw in node.exc.keywords:
                    code = _literal_code(kw.value) if kw.arg == "error_code" else None
                    if code is not None:
                        key = (rel, raised_cls, code)
                        if key not in seen:
                            seen.add(key)
                            rows.append({"file": rel, "class": raised_cls, "code": code, "lineno": kw.lineno})
    return rows


def load_registry(path: Path = REGISTRY_PATH, *, tree: str | None = None) -> dict:
    """读 error_code 注册表（观测面同 scan_code_definitions，两侧必须同面才可比对）。

    该观测面无注册表 → 抛错而非当空表：空表会把全仓每个码都判成"未登记"，作为 HEAD
    基线时更会伪造出一整片"新增违规"，把无关批次连坐挡死。
    """
    text = _read_at(path, tree)
    if text is None:
        raise FileNotFoundError(
            f"error_code 注册表在观测面 [{tree if tree is not None else 'git index'}] 上不存在: {path}"
        )
    return yaml.safe_load(text)


def _prefix_of(code: str) -> str:
    """域前缀 = ZA- 后第一段（子码/模块号嵌入段不参与前缀声明判定）。"""
    return code.split("-")[1]


def _collect_contract_codes(*, tree: str | None = None) -> tuple[set[str], set[str]]:
    """收集契约码（active, deferred）。

    active：error_codes[].code + tools[].errors[]（yaml 结构化解析）。
    deferred：文本级解析——"- code:" 块内含 "# deferred" 注释（0bd159c4 先例格式，
    safe_load 不可见故走文本）；deferred 码从 active 集排除。
    """
    text = _read_at(CONTRACTS_PATH, tree)
    if text is None:
        logger.warning("方向 C 无约束：观测面 [%s] 上无 tool_contracts.yaml", tree if tree is not None else "git index")
        return set(), set()
    data = yaml.safe_load(text)

    active: set[str] = set()

    def _walk(node) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "code" and isinstance(v, str) and _CODE_RE.match(v):
                    active.add(v)
                elif k == "errors" and isinstance(v, list):
                    for item in v:
                        if isinstance(item, str) and _CODE_RE.match(item):
                            active.add(item)
                else:
                    _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(data)

    deferred: set[str] = set()
    for block in text.split("- code:")[1:]:
        chunk = block.split("- code:")[0]  # 块边界=下一个码条目
        m = re.match(r'\s*"?(ZA-[A-Z0-9-]+)"?', chunk)
        if m and "# deferred" in chunk:
            deferred.add(m.group(1))
    return active - deferred, deferred


@lru_cache(maxsize=4)
def _collect(tree: str | None) -> tuple[tuple[str, frozenset[str]], ...]:
    """违规集计算（一次扫描供六断言+门禁双观测面共用；按观测面缓存）。

    返回 tuple[(断言名, frozenset[证据])]——lru_cache 要求可哈希，故不用 dict[str, set]。
    """
    rows = scan_code_definitions(tree=tree)
    reg = load_registry(tree=tree)
    entries = reg["error_codes"]
    registered = {e["code"] for e in entries}
    declared = set(reg.get("domain_prefixes") or {})
    live = {(r["code"], r["class"], r["file"]) for r in rows}

    locs: dict[str, set[tuple[str, str]]] = {}
    for r in rows:
        locs.setdefault(r["code"], set()).add((r["file"], r["class"]))

    sanctioned = {
        d["code"]: {(li["file"], li["class"]) for li in d["later_introducers"]}
        for d in reg.get("known_duplicates") or []
    }
    unsanctioned: set[str] = set()
    for code, where in locs.items():
        if len(where) <= 1:
            continue
        extra = where - sanctioned.get(code, set())
        # canonical 定义点应占一席；剩余全部须在白名单内
        if len(extra) > 1 or code not in sanctioned:
            unsanctioned.add(code)

    rotten: set[str] = set()
    for d in reg.get("known_duplicates") or []:
        code = d["code"]
        expected = {(d["canonical"]["file"], d["canonical"]["class"])} | sanctioned.get(code, set())
        if locs.get(code, set()) != expected or len(locs.get(code, set())) <= 1:
            rotten.add(code)

    return (
        ("unregistered_code", frozenset({r["code"] for r in rows} - registered)),
        ("undeclared_prefix", frozenset({_prefix_of(r["code"]) for r in rows} - declared)),
        (
            "stale_entry",
            frozenset(
                f"{e['code']}|{e.get('class')}|{e.get('file')}"
                for e in entries
                if "deprecated" not in e and (e["code"], e.get("class"), e.get("file")) not in live
            ),
        ),
        ("registry_dup_code", frozenset(c for c, n in Counter(e["code"] for e in entries).items() if n > 1)),
        (
            "registry_missing_field",
            frozenset(
                f"{e.get('code')}|{field}" for e in entries for field in _REQUIRED_FIELDS if not e.get(field)
            ),
        ),
        ("unsanctioned_duplicate", frozenset(unsanctioned)),
        ("rotten_allowlist", frozenset(rotten)),
    )


def collect_violations(*, tree: str | None = None) -> dict[str, set[str]]:
    """六断言违规证据集（可差分口径，供门禁基线差分用）。

    Args:
        tree: 观测面（None=git index／``FS``=文件系统／其他=该 tree-ish，如 "HEAD"）。

    Returns:
        {断言名: {证据字符串}}——证据串跨观测面稳定（不含计数与顺序），门禁据此做
        index−HEAD 差分：差集非空＝本 commit 新增违规（阻断），交集＝HEAD 存量（warn）。
    """
    return {name: set(evidence) for name, evidence in _collect(tree)}


def _locations_by_code(*, tree: str | None = None) -> dict[str, set[tuple[str, str]]]:
    locs: dict[str, set[tuple[str, str]]] = {}
    for r in scan_code_definitions(tree=tree):
        locs.setdefault(r["code"], set()).add((r["file"], r["class"]))
    return locs


class TestCodeToRegistry:
    """方向 A：代码真源 → 注册表（硬阻断新增未登记码/未声明前缀）。"""

    def test_all_code_definitions_registered(self):
        unregistered = sorted(collect_violations()["unregistered_code"])
        assert not unregistered, (
            f"{len(unregistered)} 个 error_code 未登记（先登记 error_code_registry.yaml 再提交）: "
            + ", ".join(unregistered[:20])
        )

    def test_all_prefixes_declared(self):
        undeclared = sorted(collect_violations()["undeclared_prefix"])
        assert not undeclared, f"error_code 前缀未在 domain_prefixes 声明: {undeclared}"


class TestRegistryToCode:
    """方向 B：注册表 → 代码真源（条目不许说谎）。"""

    def test_active_entries_have_live_definition(self):
        stale = sorted(collect_violations()["stale_entry"])
        pretty = [s.replace("|", " (", 1).replace("|", ", ", 1) + ")" for s in stale]
        assert not stale, (
            f"{len(stale)} 条 active 注册条目无存活定义点（退役请加 deprecated/replacement）: " + "; ".join(pretty[:20])
        )

    def test_registry_internal_uniqueness_and_fields(self):
        v = collect_violations()
        dups = sorted(v["registry_dup_code"])
        missing = sorted(f"{c}: 缺字段 {f}" for c, f in (s.split("|", 1) for s in v["registry_missing_field"]))
        assert not dups, f"注册表内部重码条目: {dups}"
        assert not missing, f"注册条目缺必填字段: {missing[:20]}"


class TestDuplicates:
    """重码：「grep 唯一命中」不变量——known_duplicates 白名单外零容忍。"""

    def test_no_unsanctioned_duplicate_codes(self):
        codes = sorted(collect_violations()["unsanctioned_duplicate"])
        locs = _locations_by_code()
        violations = [f"{c} @ {sorted(locs.get(c, set()))}" for c in codes]
        assert not violations, (
            f"{len(violations)} 个新增跨定义点重码（须先经 git 首引入裁定并登记 known_duplicates）: "
            + "; ".join(violations[:10])
        )

    def test_known_duplicates_allowlist_hygiene(self):
        """白名单防腐：改号完工后条目必须同步移除（不再是真实重码即红）。"""
        reg = load_registry()
        locs = _locations_by_code()
        rotten = sorted(collect_violations()["rotten_allowlist"])
        detail = [
            f"{c}: 代码实况 {sorted(locs.get(c, set()))} != 白名单 "
            f"{sorted({(d['canonical']['file'], d['canonical']['class'])} | {(li['file'], li['class']) for li in d['later_introducers']})}"
            for c in rotten
            for d in reg.get("known_duplicates") or []
            if d["code"] == c
        ]
        assert not rotten, "known_duplicates 白名单与代码实况不符（改号完工后请移除条目）: " + "; ".join(detail[:10])


def _live_code_strings(src_root: Path = SRC_ROOT, *, tree: str | None = None) -> set[str]:
    """文本级活码全集：src/ 下 .py 文件中出现的全部 ZA- 码字符串（含注释/字符串/dict 值）。

    死活判定用宽口径（与方向 A/B 的 AST (class,file) 精度对账解耦）：B 类 fail-soft 码
    形态为 dict 赋值 out["error_code"]="ZA-X"（非 raise 字面量），AST 扫不出但确实活着。
    """
    codes: set[str] = set()
    pat = re.compile(r"ZA-[A-Z0-9]+(?:-[A-Z0-9]+)*")
    for _rel, text in _iter_sources(src_root, tree):
        if "ZA-" in text:
            codes.update(pat.findall(text))
    return codes


class TestContractToCode:
    """方向 C（第七断言，2026-09-06）：tool_contracts.yaml 契约码 ↔ 代码死活机器对账。

    背景（批三 Root Cause）：Flash 按 backend 指针找 server 文件，session_handoff 段
    backend 只列文档/模型名，未列实现文件（真源=doc_guard_server.py，文件名≠server_id）
    → 8 个活码被误判"无 server/骨架族"。本断言把"契约码死活"从模型判断改为机器判定：
    非 deferred 契约码必须在 src/ 有码字符串出现（宽口径，覆盖 raise/fail-soft dict/
    dataclass 全形态）；deferred 码必须真的零出现。
    """

    def test_active_contract_codes_have_live_definition(self):
        active, _deferred = _collect_contract_codes()
        live = _live_code_strings()
        dead = sorted(active - live)
        assert not dead, (
            f"{len(dead)} 个契约码在 src/ 零出现（实现它，或在契约块内加 '# deferred' 注释+理由）: "
            + ", ".join(dead[:20])
        )

    def test_deferred_contract_codes_truly_dead(self):
        """deferred 防腐：标了 deferred 却在代码出现 = 注释腐化，须除名。"""
        _active, deferred = _collect_contract_codes()
        live = _live_code_strings()
        revived = sorted(deferred & live)
        assert not revived, (
            "deferred 契约码已在代码出现（deferred 注释腐化，请移除注释）: " + ", ".join(revived[:20])
        )
