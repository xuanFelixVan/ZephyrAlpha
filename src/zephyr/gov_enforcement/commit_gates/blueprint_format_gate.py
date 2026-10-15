# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.blueprint_format_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d3_metadata.validate_module_id_naming (is_valid_module_id)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py added 行含 [BLUEPRINT] 头部时，module_id 必须合规（裁定#208 双轨制：MOD-/SH- 前缀）；存量基线违规 grandfathered（只检 added 行）；git diff不可达fail-open；检出违规则fail-closed。治本（#ARCH-DATAQUALITY-V1.1）：移除 tests/ 豁免——100% AI 开发下豁免区=债务温床，482 个 SRC-XXX 违规因 tests/ 豁免累积；own 化 2026-10-05(st-sQ-infra-20261005 修4)：扫描范围=全暂存∩本 session，外来 staged warn+审计不阻断(_split_own_foreign)；P1-3 单趟化（st-perfz2-20261015）：聚合门每轮注入 _doc_suite_ctx（_DocSuiteContext），七判据对同一批文档的 staged 清单/added 行/全文/docstring AST/HEAD ls-tree/链接存在性只读一次（纯 memo 同输入同返回，判定行为零变化）；单文件读入+解析累计 >5s 熔断=跳过后续判据不重扫（warn+审计 .runtime/gate_audit/doc_header_suite_breaker.jsonl，图纸明定唯一新行为，仅聚合门路径生效）
# [MODIFY-GUARD] gate_id="DOC-HEADER-SUITE"（T8簇2 聚合门，st-commitspeed-pkg8-20260925；本模块同时保留吸收台 BLUEPRINT-FORMAT 薄工厂）；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；2026-10-15 st-perfz2 P1-3 单趟化：kwarg _doc_suite_ctx 注入缝+熔断判据（_DOC_SUITE_BREAKER_SECONDS）变更须与七判据子门（blueprint_amodule_consistency_gate/blueprint_amodule_cross_check_gate/module_id_consistency_gate/file_placement_ttl_gate/exempt_zone_frontmatter_gate/doc_ref_broken_gate）及 tests/gov/governance/commit_gates/test_doc_header_suite_single_pass.py 同批
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
blueprint_format_gate.py — [BLUEPRINT] 头部格式门禁 + DOC-HEADER-SUITE 文档头七判据聚合门

本模块双重身份（T8簇2，st-commitspeed-pkg8-20260925）：
1. BLUEPRINT-FORMAT 判定体（[BLUEPRINT] 头部 module_id 格式硬阻断）——原门保留，
   薄工厂 make_blueprint_format_gate 供历史测试/引用兼容（不再入册）。
2. DOC-HEADER-SUITE 聚合门（make_doc_header_suite_gate）——七台文档头/放置门
   （BLUEPRINT-FORMAT/BLUEPRINT-HEADER/MODULE-ID-CONSISTENCY/TTL-METADATA/
   FILE-PLACEMENT-TTL/EXEMPT-ZONE-FM/DOC-REF-BROKEN）一台聚合 + 7 条判据数据，
   判据零退役（对齐 gslim P4 union 家工厂先例）。

检测 staged .py 文件 added 行中的 [BLUEPRINT] 头部，校验 module_id 格式
是否符合裁定#208 双轨制（MOD-/SH- 前缀）。

病根（第一性原理）
-----------------
裁定#214 调研发现 139 条 SRC-XXX 旧格式 + 10 条 (migrated) + 6 条空头 +
2 条其他格式错误的 [BLUEPRINT] 头部。Phase 1 已修复 18 个文件，但若无门禁，
新 AI 会继续制造同类违规——格式蔓延的根因是"无 commit 阶段强制"。

治本方案
--------
在 GitCommitGateway pre-commit 阶段注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 对每个文件解析 diff，检查 added 行是否含 [BLUEPRINT] 头部
  3. 提取 module_id，调用 validate_module_id_naming.is_valid_module_id() 校验
  4. 不合规 -> 硬阻断

设计权衡
--------
1. **只检测 added 行**：存量 139 条 SRC-XXX 违规由专项任务清理，gate 只防新增。
2. **diff-based**：与 bare_sql_gate / hardcoded_url_gate 一致的检测模式。
3. **复用真源**：is_valid_module_id() 是格式校验唯一真源（裁定#208），禁止复制正则。
4. **priority=77**：在 RULE-FOUR-WAY(76) 之后，VOCAB-HARDCODE(80) 之前。
5. **移除 tests/ 豁免**（#ARCH-DATAQUALITY-V1.1，2026-07-18）：原设计豁免 tests/，
   导致 482 个 SRC-XXX 违规在 tests/ 下无限累积（AI 复制现有模式）。100% AI 开发
   下任何豁免区=债务温床。存量 grandfathered（只检 added 行），新增必须合规。

Usage::

    from zephyr.gov_enforcement.commit_gates.blueprint_format_gate import make_blueprint_format_gate
    registry.register(make_blueprint_format_gate())

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/b/blueprint_format_gate.yaml
"""

from __future__ import annotations

import importlib.util
import logging
import re
import subprocess
import time
from pathlib import Path
from typing import Final

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _get_added_lines,
    _get_staged_py_files,
    _read_staged_file,
    _split_own_foreign,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_blueprint_format_gate", "make_doc_header_suite_gate"]

# 治本（#ARCH-WORKTREE-002 缺陷1，2026-07-19）：动态加载 validate_module_id_naming
# 原设计：模块级 import 通过 REPO_ROOT 定位 scripts/governance/d3_metadata/
# 问题：REPO_ROOT 基于 __file__ 永远指向主工作区（src/zephyr/shared/io/paths.py:65），
#       worktree 模式下 pre-merge gate import 主工作区旧版本而非 worktree 新版本
#       （实测：regex 修复 [A-Z]→[A-Za-z] 后仍被旧版本拒绝 MOD-migrate_sqlite_to_pg）
# 方案：用 importlib.util.spec_from_file_location 从 gateway.project_root 动态加载，
#       确保 worktree 模式下使用 worktree 中的模块版本。缓存按 project_root key，
#       避免 repeated exec_module（实际 project_root 只有主工作区/worktree 两个值）
_validate_module_id_cache: dict[str, object] = {}


def _load_is_valid_module_id(project_root: Path):
    """从 project_root 动态加载 validate_module_id_naming.is_valid_module_id。

    治本（#ARCH-WORKTREE-002 缺陷1）：用 gateway.project_root 而非 REPO_ROOT，
    确保 worktree 模式下 import worktree 中的模块版本。

    Args:
        project_root: gateway.project_root（worktree 模式下为 worktree 路径）

    Returns:
        validate_module_id_naming.is_valid_module_id 函数引用

    Raises:
        FileNotFoundError: 模块文件不存在（project_root 异常时回退到 REPO_ROOT）
    """
    key = str(project_root)
    if key in _validate_module_id_cache:
        return _validate_module_id_cache[key]
    module_path = project_root / "scripts" / "governance" / "d3_metadata" / "validate_module_id_naming.py"
    if not module_path.exists():
        # 回退到 REPO_ROOT（非 worktree 模式或路径异常）
        from zephyr.shared.io.paths import REPO_ROOT

        module_path = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "validate_module_id_naming.py"
    spec = importlib.util.spec_from_file_location(
        "_validate_module_id_naming_dynamic",
        module_path,
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _validate_module_id_cache[key] = mod.is_valid_module_id
    return mod.is_valid_module_id


# 匹配 [BLUEPRINT] 头部行，提取 module_id token（第一个非空白 token）
# 合规：# [BLUEPRINT] MOD-INF-029 | docs/...
# 违规：# [BLUEPRINT]（空）/ # [BLUEPRINT] (migrated...) / # [BLUEPRINT] SRC-XXX | ...
_BP_HEADER_RE = re.compile(r"^#\s*\[BLUEPRINT\]\s*(\S+)?")


# st-commitspeed-pkg8-20260925 T8簇2 闭包提级：原 make_blueprint_format_gate 内层 _check 闭包体，行为逐字节保留；
# 模块级化供 DOC-HEADER-SUITE 聚合器同调（gslim P4 合并先例：吸收台闭包提级）。
# st-perfz2-20261015 P1-3：kwarg _doc_suite_ctx 给定时走共享读入（staged 清单/added 行
# 各读一次），熔断文件跳过不重扫；kwarg 缺省（历史直调/本台单测）逐字走原路径。
def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
    # 治本（#ARCH-DATAQUALITY-V1.1，2026-07-18）：移除 tests/ 豁免——100% AI 开发下，
    # 豁免区=债务温床（482 个 SRC-XXX 违规因 tests/ 豁免累积）。存量 grandfathered
    # （只检 added 行），但新增 tests/ 文件必须用合规 MOD-/SH- 前缀。
    # 治本（#ARCH-WORKTREE-002 缺陷1，2026-07-19）：从 gateway.project_root 动态加载
    # is_valid_module_id，确保 worktree 模式下使用 worktree 中的模块版本
    is_valid_module_id = _load_is_valid_module_id(gateway.project_root)
    ctx = kwargs.get("_doc_suite_ctx")
    py_files = ctx.staged_py_files(gateway) if ctx is not None else _get_staged_py_files(gateway, "BLUEPRINT-FORMAT")
    # own 化（修4，st-sQ-infra-20261005，#ARCH-GATE-OWN-SCOPE-001 推广面/M2 道 92 台同款）：
    # 扫描范围=全暂存∩本 session；外来 staged 不扫描、不产生违规、不阻断（warn+审计，
    # 多会话连坐结构性消除）。无归属信息（files 空+无 session_id）退化旧行为扫全量。
    py_files = _split_own_foreign(gateway, py_files, files, kwargs.get("session_id"), gate_name="BLUEPRINT-FORMAT")[0]
    violations: list[str] = []
    for py_file in py_files:
        if ctx is not None and ctx.is_broken(py_file):
            ctx.note_skip(py_file, "BLUEPRINT-FORMAT")
            continue
        added = (
            ctx.added_lines(gateway, py_file, "BLUEPRINT-FORMAT")
            if ctx is not None
            else _get_added_lines(gateway, py_file, "BLUEPRINT-FORMAT")
        )
        for line_no, content in added:
            m = _BP_HEADER_RE.match(content)
            if not m:
                continue
            # [BLUEPRINT] 头部行被 added/modified——校验 module_id
            module_id = m.group(1)
            if not module_id:
                violations.append(
                    f"  {py_file}:{line_no}: [BLUEPRINT] header missing module_id "
                    f"(expected: # [BLUEPRINT] MOD-XXX | docs/...)"
                )
                continue
            ok, reason = is_valid_module_id(module_id)
            if not ok:
                violations.append(
                    f"  {py_file}:{line_no}: [BLUEPRINT] header invalid module_id '{module_id}': {reason}"
                )
    if violations:
        detail = (
            "BLUEPRINT-FORMAT: [BLUEPRINT] 头部 module_id 格式不合规"
            "（裁定#214 Phase 0 防蔓延）\n"
            "  合规格式: # [BLUEPRINT] MOD-XXX | docs/03_modules/.../blueprint.md\n"
            "  禁止格式: 空头部 / (migrated...) / SRC-XXX / DOM-XXX / 路径作 module_id\n"
            + "\n".join(violations)
            + "\n-> 修复 [BLUEPRINT] 头部，使用合规的 MOD-/SH- 前缀 module_id"
        )
        logger.error("BLUEPRINT-FORMAT gate block:\n%s", detail)
        return False, detail
    return True, ""


def make_blueprint_format_gate() -> GateSpec:
    """构造 [BLUEPRINT] 头部格式门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="BLUEPRINT-FORMAT", priority=130)。
    """

    # priority=130：原 77 让位给 DOC-HEADER-SUITE 聚合门（后到者让位先例；本薄工厂已出名册，
    # 仅 fresh-import 注册路径会与 suite 撞号——M5.2 确定性判别实证，2026-09-26 st-metaq-gc-20260924）
    return GateSpec(gate_id="BLUEPRINT-FORMAT", check=_check, priority=130)


# ═══ T8 簇2 聚合门（st-commitspeed-pkg8-20260925，对齐 gslim P4 union 家工厂先例）═══
# 七台文档头/放置门收敛为一台聚合门 + 7 条判据数据；判据零退役——七个判定体各自
# 独立判定（各模块级 _check/_header_union_check 闭包提级同调），违规聚合呈现带
# [源台名] 前缀（首行），任一失败即阻断。吸收台薄工厂（gate_id/priority 原样保留，
# 不再入册）供历史测试与 RULE-EXECUTION-PAIRING 引用兼容。
# 7 条判据数据（源台 gate_id, 模块, 判定体, 原 priority）：
_DOC_HEADER_SUITE_SUBS: list[tuple[str, str | None, str, int]] = [
    ("BLUEPRINT-FORMAT", None, "_check", 77),
    ("BLUEPRINT-HEADER", "blueprint_amodule_consistency_gate", "_header_union_check", 79),
    ("MODULE-ID-CONSISTENCY", "module_id_consistency_gate", "_check", 88),
    ("TTL-METADATA", "ttl_gate", "_check", 32),
    ("FILE-PLACEMENT-TTL", "file_placement_ttl_gate", "_check", 33),
    ("EXEMPT-ZONE-FM", "exempt_zone_frontmatter_gate", "_check", 87),
    ("DOC-REF-BROKEN", "doc_ref_broken_gate", "_check", 91),
]


# ═══ P1-3 单趟化（st-perfz2-20261015，总包 st-diskp0-20261015 图纸③）═══
# 病根（W42 实测）：本聚合门占门禁 CPU 12.5%、p95=54.8s、max 30min——七判据各自
# 独立重复读同一批文档（staged py 清单 git diff ×3、每文件 added 行 diff ×3、
# staged 全文 git show ×2、docstring AST 解析 ×2、HEAD ls-tree ×2、链接存在性
# ls-files ×links……），全部是对同一 commit 暂存态的重复观测。
# 治本＝一次读入共享：聚合器构造 _DocSuiteContext 注入各判定体（kwarg opt-in，
# 不改变任何判定体直调路径），同一 (文件, 数据面) 只读一次；frontmatter/AST 解析
# （docstring 行号集）同样按文件 memo。判定行为零变化红线：memo 的键=完整输入、
# 值=同一函数在同一输入上的返回（纯 memo）；熔断（单文件累计读入/解析 >5s 跳过
# 后续判据不重扫+warn+审计）是图纸明定的唯一新行为，仅聚合门路径生效。
_DOC_SUITE_BREAKER_SECONDS = 5.0
_DOC_SUITE_AUDIT_NAME = "doc_header_suite_breaker.jsonl"


def _now_iso_for_audit() -> str:
    from zephyr.shared.utils.time_utils import now_utc

    return now_utc().isoformat()  # m46：时间戳唯一真源（fallback 禁 time.time，DATETIME-NOW-FORBIDDEN 硬规）


def _audit_breaker(root: Path, record: dict) -> None:
    """熔断/跳过留痕（jsonl append；fail-open——留痕面不是裁决面）。"""
    try:
        from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl

        append_audit_jsonl(root / ".runtime" / "gate_audit", _DOC_SUITE_AUDIT_NAME, record)
    except Exception:  # noqa: BLE001 — 留痕失败不阻断
        logger.debug("DOC-HEADER-SUITE breaker audit write failed (non-blocking)", exc_info=True)


class _DocSuiteContext:
    """DOC-HEADER-SUITE 单趟共享读入上下文（一次聚合门调用范围内有效，七判据共享）。

    - 纯 memo：每方法=既有共享原语（_diff_helpers 同名函数/gateway 方法）的同输入
      缓存，键=完整输入，值逐字节同原函数返回——不经过 ctx 的直调路径零变化。
    - 熔断：单文件累计共享读入/解析耗时 > _DOC_SUITE_BREAKER_SECONDS 即标记 broken，
      后续判据经 is_broken() 跳过该文件（warn+审计留痕，不重扫）。
    - 非 thread-safe（门禁链串行执行）；生命周期=单次 _union_check 调用。
    """

    def __init__(self, project_root: Path, breaker_seconds: float | None = None) -> None:
        self._root = project_root
        # 阈值经模块常量延迟绑定（测试 monkeypatch 面；生产恒 _DOC_SUITE_BREAKER_SECONDS）
        self.breaker_seconds = _DOC_SUITE_BREAKER_SECONDS if breaker_seconds is None else breaker_seconds
        self._staged_py: list[str] | None = None
        self._added: dict[str, list] = {}
        self._texts: dict[str, str | None] = {}
        self._docstrings: dict[str, set] = {}
        self._head_ls: dict[str, tuple[int | None, str]] = {}
        self._tracked: dict[str, bool] = {}
        self._repo_has: dict[tuple[str, str], bool] = {}
        self._cost: dict[str, float] = {}
        self._broken: dict[str, str] = {}
        self._skips: list[tuple[str, str, str]] = []

    # ── 熔断面 ──
    def _charge(self, rel: str, seconds: float, what: str) -> None:
        total = self._cost.get(rel, 0.0) + max(float(seconds), 0.0)
        self._cost[rel] = total
        if total > self.breaker_seconds and rel not in self._broken:
            self._broken[rel] = f"{what} 累计 {total:.1f}s > {self.breaker_seconds}s 熔断阈值"
            logger.warning(
                "DOC-HEADER-SUITE 单文件熔断（st-perfz2 P1-3）: %s %s——后续判据跳过该文件不重扫",
                rel,
                self._broken[rel],
            )
            _audit_breaker(
                self._root,
                {
                    "ts": _now_iso_for_audit(),
                    "event": "doc_header_suite_breaker",
                    "file": rel,
                    "tripped_by": what,
                    "total_seconds": round(total, 2),
                    "threshold_seconds": self.breaker_seconds,
                },
            )

    def is_broken(self, rel: str) -> bool:
        return rel in self._broken

    def note_skip(self, rel: str, gate_id: str) -> None:
        if self.is_broken(rel):
            self._skips.append((gate_id, rel, self._broken[rel]))

    def flush(self) -> None:
        """聚合轮末尾落跳过摘要（有破文件才落；fail-open）。"""
        if not self._skips:
            return
        _audit_breaker(
            self._root,
            {
                "ts": _now_iso_for_audit(),
                "event": "doc_header_suite_breaker_skips",
                "skips": [{"gate": g, "file": f, "reason": r} for g, f, r in self._skips[:50]],
                "skip_count": len(self._skips),
            },
        )

    # ── 共享读入面（每方法=同输入同返回的纯 memo）──
    def staged_py_files(self, gateway) -> list[str]:
        if self._staged_py is None:
            self._staged_py = _get_staged_py_files(gateway, "DOC-HEADER-SUITE")
        return self._staged_py

    def added_lines(self, gateway, py_file: str, gate_name: str = "DOC-HEADER-SUITE") -> list[tuple[int, str]]:
        if py_file not in self._added:
            t0 = time.perf_counter()
            self._added[py_file] = _get_added_lines(gateway, py_file, gate_name)
            self._charge(py_file, time.perf_counter() - t0, "added_lines")
        return self._added[py_file]

    def staged_text(self, gateway, rel: str) -> str | None:
        if rel not in self._texts:
            t0 = time.perf_counter()
            self._texts[rel] = _read_staged_file(gateway, rel)
            self._charge(rel, time.perf_counter() - t0, "staged_text")
        return self._texts[rel]

    def docstring_lines(self, rel: str, text: str | None) -> set:
        """docstring 行号集（AST）按文件 memo——AMODULE 与 CROSS-CHECK 对同一 staged
        文本各解析一遍的开销收敛为一遍。"""
        if rel not in self._docstrings:
            t0 = time.perf_counter()
            self._docstrings[rel] = _extract_docstring_lines(text) if text else set()
            self._charge(rel, time.perf_counter() - t0, "docstring_ast")
        return self._docstrings[rel]

    def head_ls_tree(self, gateway, rel: str) -> tuple[int | None, str]:
        """``git ls-tree HEAD -- <rel>`` 共享（MODULE-ID 历史豁免与 EXEMPT-ZONE-FM 历史
        豁免同命令同判据面）。返回 (returncode, stdout)；(TimeoutExpired/OSError) 异常
        → (None, "")（与两台各自的异常分支语义对齐）；其余异常照原样上抛（与直调
        行为逐字一致）。"""
        if rel not in self._head_ls:
            try:
                r = gateway.run_git(["git", "ls-tree", "HEAD", "--", rel])
                self._head_ls[rel] = (int(getattr(r, "returncode", 1)), str(getattr(r, "stdout", "") or ""))
            except (subprocess.TimeoutExpired, OSError):
                self._head_ls[rel] = (None, "")
        return self._head_ls[rel]

    def is_git_tracked(self, gateway, rel: str) -> bool:
        if rel not in self._tracked:
            self._tracked[rel] = bool(gateway.is_git_tracked(rel))
        return self._tracked[rel]

    def repo_state_has(self, gateway, rel_path: str, rev: str = "") -> bool:
        key = (rev, rel_path)
        if key not in self._repo_has:
            from zephyr.gov_enforcement.commit_gates._diff_helpers import _repo_state_has_file

            self._repo_has[key] = _repo_state_has_file(gateway, rel_path, rev)
        return self._repo_has[key]


def make_doc_header_suite_gate() -> GateSpec:
    """构造 DOC-HEADER-SUITE 文档头七判据聚合门禁（T8 簇2，st-commitspeed-pkg8-20260925）。

    聚合子检查（各自独立判定，违规聚合呈现带 [源台名] 前缀，任一失败即阻断）——
    判据对象不同（ttl ↔ 头格式 ↔ module_id ↔ 链接实存 ↔ 放置区），判据一条不退役：
    见 _DOC_HEADER_SUITE_SUBS（7 条判据数据）。priority=77（BLUEPRINT-FORMAT 原槽位，
    其余六槽位随吸收台出册释放）。

    st-perfz2-20261015 P1-3 单趟化：每轮聚合构造一个 _DocSuiteContext 注入各判定体
    （kwarg ``_doc_suite_ctx``，opt-in——判定体直调路径零变化），七判据对同一批文档
    的 staged 清单/added 行/全文/docstring AST/HEAD ls-tree/链接存在性只读一次；
    单文件读入+解析累计 >5s 熔断（warn+审计，后续判据跳过不重扫，图纸明定唯一新行为）。
    """

    def _union_check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        ctx = _DocSuiteContext(Path(str(getattr(gateway, "project_root", ".") or ".")))
        kwargs = {**kwargs, "_doc_suite_ctx": ctx}
        failures: list[str] = []
        for sgid, mod, impl_name, _prio in _DOC_HEADER_SUITE_SUBS:
            try:
                if mod is None:
                    fn = globals()[impl_name]  # 本文件判定体（闭包提级后的模块级 _check）
                else:
                    import importlib  # noqa: PLC0415

                    fn = getattr(importlib.import_module(f"zephyr.gov_enforcement.commit_gates.{mod}"), impl_name)
            except Exception as exc:  # noqa: BLE001 — 子检查缺失=聚合面残缺，fail-closed 呈报
                failures.append(f"[{sgid}] 子检查不可加载: {type(exc).__name__}")
                continue
            ok, detail = fn(gateway, files, **kwargs)
            if not ok:
                failures.append(f"[{sgid}] " + detail)
        try:
            ctx.flush()
        except Exception:  # noqa: BLE001 — 留痕失败不影响判定
            logger.debug("doc suite ctx flush failed (non-blocking)", exc_info=True)
        if failures:
            return False, "\n".join(failures)
        return True, ""

    return GateSpec(gate_id="DOC-HEADER-SUITE", check=_union_check, priority=77)
