# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] tests.governance.test_error_code_consistency
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] 代码定义点全量登记；active 条目全有存活定义点；跨定义点重码仅限注册表 known_duplicates 白名单；码前缀全声明；注册表内部唯一
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
  重码：同一 code 跨 (file, class) 定义点 >1 违反「grep 唯一命中」不变量。存量 9 码 10 处
    经 git 首引入裁定登记于注册表 known_duplicates 段（GAP-010 高敏区人审约束，改号待
    Owner 批准）——白名单外新增重码即红；白名单条目不再是真实重码（改号完工后残留）
    亦红，防白名单腐化。
  前缀：code 首段（ZA- 后第一段）必须声明于 domain_prefixes。
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "zephyr"
REGISTRY_PATH = REPO_ROOT / "architecture_model" / "contracts" / "error_code_registry.yaml"

_CODE_RE = re.compile(r"^ZA-[A-Z0-9]+(?:-[A-Z0-9]+)*$")


def _literal_code(node: ast.expr | None) -> str | None:
    """提取 error_code 字面量（仅接受 ZA- 开头的纯字面字符串）。"""
    if isinstance(node, ast.Constant) and isinstance(node.value, str) and _CODE_RE.match(node.value):
        return node.value
    return None


def scan_code_definitions(src_root: Path = SRC_ROOT) -> list[dict]:
    """AST 扫描 error_code 定义点：类属性赋值 + raise Xxx(error_code=...) 字面量。

    返回 [{file, class, code, lineno}]；同 (file, class, code) 多 raise 点去重（同一逻辑码）。
    """
    rows: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for py in sorted(src_root.rglob("*.py")):
        text = py.read_text(encoding="utf-8")
        if "error_code" not in text or "ZA-" not in text:
            continue  # 文本预过滤：无字面码文件免 AST 解析（门禁时延优化）
        rel = py.relative_to(REPO_ROOT).as_posix()
        tree = ast.parse(text, filename=rel)
        for node in ast.walk(tree):
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


def load_registry(path: Path = REGISTRY_PATH) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _prefix_of(code: str) -> str:
    """域前缀 = ZA- 后第一段（子码/模块号嵌入段不参与前缀声明判定）。"""
    return code.split("-")[1]


class TestCodeToRegistry:
    """方向 A：代码真源 → 注册表（硬阻断新增未登记码/未声明前缀）。"""

    def test_all_code_definitions_registered(self):
        reg = load_registry()
        registered = {e["code"] for e in reg["error_codes"]}
        unregistered = sorted({r["code"] for r in scan_code_definitions()} - registered)
        assert not unregistered, (
            f"{len(unregistered)} 个 error_code 未登记（先登记 error_code_registry.yaml 再提交）: "
            + ", ".join(unregistered[:20])
        )

    def test_all_prefixes_declared(self):
        reg = load_registry()
        declared = set(reg["domain_prefixes"])
        undeclared = sorted(
            {_prefix_of(r["code"]) for r in scan_code_definitions()} - declared
        )
        assert not undeclared, f"error_code 前缀未在 domain_prefixes 声明: {undeclared}"


class TestRegistryToCode:
    """方向 B：注册表 → 代码真源（条目不许说谎）。"""

    def test_active_entries_have_live_definition(self):
        reg = load_registry()
        live = {(r["code"], r["class"], r["file"]) for r in scan_code_definitions()}
        stale = [
            f"{e['code']} ({e.get('class')}, {e.get('file')})"
            for e in reg["error_codes"]
            if "deprecated" not in e and (e["code"], e.get("class"), e.get("file")) not in live
        ]
        assert not stale, (
            f"{len(stale)} 条 active 注册条目无存活定义点（退役请加 deprecated/replacement）: "
            + "; ".join(stale[:20])
        )

    def test_registry_internal_uniqueness_and_fields(self):
        reg = load_registry()
        seen: dict[str, int] = {}
        missing = []
        for e in reg["error_codes"]:
            seen[e["code"]] = seen.get(e["code"], 0) + 1
            for field in ("code", "class", "module", "file"):
                if not e.get(field):
                    missing.append(f"{e.get('code')}: 缺字段 {field}")
        dups = sorted(c for c, n in seen.items() if n > 1)
        assert not dups, f"注册表内部重码条目: {dups}"
        assert not missing, f"注册条目缺必填字段: {missing[:20]}"


class TestDuplicates:
    """重码：「grep 唯一命中」不变量——known_duplicates 白名单外零容忍。"""

    def _locations_by_code(self) -> dict[str, set[tuple[str, str]]]:
        locs: dict[str, set[tuple[str, str]]] = {}
        for r in scan_code_definitions():
            locs.setdefault(r["code"], set()).add((r["file"], r["class"]))
        return locs

    def test_no_unsanctioned_duplicate_codes(self):
        reg = load_registry()
        sanctioned = {
            d["code"]: {(li["file"], li["class"]) for li in d["later_introducers"]}
            for d in reg.get("known_duplicates", [])
        }
        violations = []
        for code, locs in sorted(self._locations_by_code().items()):
            if len(locs) <= 1:
                continue
            extra = locs - sanctioned.get(code, set())
            # canonical 定义点应占一席；剩余全部须在白名单内
            if len(extra) > 1 or code not in sanctioned:
                violations.append(f"{code} @ {sorted(locs)}")
        assert not violations, (
            f"{len(violations)} 个新增跨定义点重码（须先经 git 首引入裁定并登记 known_duplicates）: "
            + "; ".join(violations[:10])
        )

    def test_known_duplicates_allowlist_hygiene(self):
        """白名单防腐：改号完工后条目必须同步移除（不再是真实重码即红）。"""
        reg = load_registry()
        locs_by_code = self._locations_by_code()
        rotten = []
        for d in reg.get("known_duplicates", []):
            code = d["code"]
            locs = locs_by_code.get(code, set())
            canon = (d["canonical"]["file"], d["canonical"]["class"])
            expected = {canon} | {(li["file"], li["class"]) for li in d["later_introducers"]}
            if locs != expected or len(locs) <= 1:
                rotten.append(f"{code}: 代码实况 {sorted(locs)} != 白名单 {sorted(expected)}")
        assert not rotten, "known_duplicates 白名单与代码实况不符（改号完工后请移除条目）: " + "; ".join(
            rotten[:10]
        )
