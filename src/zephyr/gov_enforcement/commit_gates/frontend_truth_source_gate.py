# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.frontend_truth_source_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] warn-only 起步（Owner 2026-09-04 裁定：TRAE-086 §truth_source_wiring 配套门禁）——staged web/**/*.js 命中"内联数据数组/零后端接线"启发式时返回 passed=True + 明细 warn + 审计落盘，不阻断 commit；_HARD_BLOCK=True 一行升级为硬阻断；git diff 不可达 fail-open（logger.warning）；检出异常由 registry 统一 fail-closed
# [MODIFY-GUARD] gate_id="FRONTEND-TRUTH-SOURCE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级 fail-open（passed=True，logger.warning）；审计写失败静默（non-blocking）
# [TESTS] tests/governance/commit_gates/test_frontend_truth_source_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
frontend_truth_source_gate.py — 前端真源接通门禁（FRONTEND-TRUTH-SOURCE，TRAE-086 §truth_source_wiring 配套）

病根（第一性原理）
-----------------
Owner 2026-09-04 裁定：前端不许自建数据世界。AI 施工前端页面时若后端盘点缺位，
会顺手编造 demo 数组/硬编码数值顶上（"前端幻觉"），产生前后端双真源与口径漂移
（实证：download-status 中文名双真源事故）。TRAE-086 v1.2.0 已立
§truth_source_wiring 铁律（施工前后端盘点四步），本 gate 在 commit 阶段做可见性兜底。

检测对象（src/zephyr/frontend/dashboard/web/ 下 staged .js，豁免基建/宿主/纯UI）
--------
A. 内联数据数组启发式（疑似前端自建数据）：
   - 连续 ≥6 行对象字面量行（``{...},``）—— fabricated 数据表形状
   - 声明即数组的 DEMO/MOCK/FAKE/SAMPLE 命名变量（``var DL_DEMO = [``）
B. 零后端接线：文件全文无 ``ZK.api`` / ``fetch(`` 引用（core/ 页逻辑 + features/
   业务功能模块按 TRAE-086 目录契约必须经 services/api.js 通道取数）

豁免：services/api.js（通道基建本身）、core/loader.js+core/event_bus.js（启动器/
事件总线）、app*.js+theme.js（宿主布局）、widgets/（纯 UI 展示件，数据经参数注入）、
vendor/、mocks/（若未来设立）。

设计权衡
--------
1. **warn-only 起步**：启发式必有误报（合法配置数组/演示诚实纪律回退数据），
   先跑 warn 收集误报率，AI 回评后收紧阈值，稳定后 ``_HARD_BLOCK=True`` 一行升硬
   （对齐 #ARCH-GATE-PRIORITY-UNIQUENESS-001 "warn 不构成闭环"教训——升级有时限承诺）。
2. **只看 added 行**（Check A）：存量债务不追溯，gate 只防新增；Check B 看全文
   是因为"零接线"是文件级属性（新文件零接线=自建数据世界，改文件零接线=仍是）。
3. **目录契约豁免而非内容猜**：按 TRAE-086 §folder_assignment 七类目录边界豁免
   纯 UI/宿主/基建，避免内容启发式二次误报。
4. **审计落盘**：命中明细追加 .runtime/gate_audit/frontend_truth_source.jsonl，
   供 Owner 周期回评误报率与升级决策。
5. **priority=136**：尾部（135 之后 200 之前），warn 型不影响主链路语义。

Usage::

    from zephyr.gov_enforcement.commit_gates.frontend_truth_source_gate import (
        make_frontend_truth_source_gate,
    )

    registry.register(make_frontend_truth_source_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: staged .js 文件 diff
#   fields: name-only 文件列表 + per-file unified=0 diff + git show :path 全文
#   code: _collect_eligible_js_files / _parse_diff_with_line_numbers / _read_staged_file
# 层: 算法
# - id: A1
#   name_zh: ① 目录契约过滤
#   name_en: _collect_eligible_js_files
#   intro: web/ 前缀 .js 过滤 + 基建/宿主/纯UI 豁免
#   desc: TRAE-086 §folder_assignment 七类目录边界：core/features 参检，services/api.js、loader、event_bus、app*、theme、widgets/、vendor/、mocks/ 豁免
#   inputs: I1
#   outputs: 参检文件列表
# - id: A2
#   name_zh: ② 内联数据数组启发式
#   name_en: _scan_inline_data_rows
#   intro: added 行连续 ≥6 对象字面量行 + DEMO/MOCK/FAKE/SAMPLE 数组声明命中
#   desc: 只看 added 行（不追溯存量）；命中记 (起始行, 行数)
#   inputs: 参检文件的 added 行
#   outputs: findings 明细
# - id: A3
#   name_zh: ③ 零后端接线检测
#   name_en: _scan_zero_wiring
#   intro: 文件全文无 ZK.api/fetch( 引用 → warn
#   desc: 文件级属性检查（新文件零接线=自建数据世界）
#   inputs: git show :path 全文
#   outputs: findings 明细
# - id: A4
#   name_zh: ④ warn 输出 + 审计落盘
#   name_en: _audit_findings
#   intro: findings 追加 .runtime/gate_audit/frontend_truth_source.jsonl
#   desc: _HARD_BLOCK=False 时 passed=True + warn 明细；True 时 fail-closed 阻断（一行升级预留）
#   inputs: A2/A3 findings
#   outputs: (passed, detail)
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec(gate_id="FRONTEND-TRUTH-SOURCE", priority=136)
#   intro: warn 型门禁（升级预留 _HARD_BLOCK）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A3
# A2 --> A4
# A3 --> A4
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Final

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _parse_diff_with_line_numbers,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_frontend_truth_source_gate"]

# ── 升级开关（Owner 裁定 warn 起步，误报率回评后一行升硬）──
_HARD_BLOCK = False

# ── 作用域：桌面面板 web/ 目录 ──
_WEB_DIR = "src/zephyr/frontend/dashboard/web/"

# ── 豁免（TRAE-086 §folder_assignment 目录契约：基建/宿主/纯UI/第三方）──
_EXEMPT_EXACT: Final = {
    "src/zephyr/frontend/dashboard/web/services/api.js",   # 通道基建本身（fetch 助手定义处）
    "src/zephyr/frontend/dashboard/web/core/loader.js",    # 启动器/路由
    "src/zephyr/frontend/dashboard/web/core/event_bus.js", # 事件总线
}
_EXEMPT_BASE_RE = re.compile(r"^(app\d+|theme)\.js$")      # 宿主大文件/主题
_EXEMPT_DIR_RE = re.compile(r"/(widgets|vendor|mocks)/")   # 纯UI件/第三方/演示隔离区

# ── Check A：内联数据数组启发式 ──
_OBJ_ROW_RE = re.compile(r"^\s*\{[^{}]*\}\s*,?\s*$")        # 对象字面量行：  { id: 1, name: "x" },
_OBJ_ROW_RUN = 6                                            # 连续 ≥6 行判定为数据表形状
_DEMO_ARRAY_RE = re.compile(
    r"^\s*(?:var|let|const)\s+\w*(?:DEMO|MOCK|FAKE|SAMPLE)\w*\s*=\s*\[", re.IGNORECASE)

# ── Check B：后端接线指纹（services/api.js 通道）──
_WIRING_RE = re.compile(r"ZK\.api|fetch\(")


def _is_eligible(path: str) -> bool:
    """目录契约过滤：web/ 下 .js 且非豁免（core/features 参检）。"""
    p = path.replace("\\", "/")
    if not p.startswith(_WEB_DIR) or not p.endswith(".js"):
        return False
    if p in _EXEMPT_EXACT:
        return False
    base = p.rsplit("/", 1)[-1]
    if _EXEMPT_BASE_RE.match(base):
        return False
    if _EXEMPT_DIR_RE.search("/" + p):
        return False
    return True


def _collect_eligible_js_files(gateway) -> list[str] | None:
    """staged added/modified .js 过滤（fail-open：git 失败返回 None → gate 放行）。"""
    try:
        result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if result.returncode != 0:
            logger.warning("FRONTEND-TRUTH-SOURCE fail-open: git diff(rc=%d)。", result.returncode)
            return None
        staged = [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f]
    except Exception as e:  # noqa: BLE001 — fail-open
        logger.warning("FRONTEND-TRUTH-SOURCE fail-open: git diff 异常(%s: %s)。", type(e).__name__, e)
        return None
    return [f for f in staged if _is_eligible(f)]


def _scan_inline_data_rows(added_lines: list[tuple[int, str]]) -> list[str]:
    """Check A：连续对象行 ≥6 / DEMO 型数组声明 → findings（只看 added 行，不追溯存量）。"""
    findings: list[str] = []
    run = 0
    start = 0
    for line_no, content in added_lines:
        if _OBJ_ROW_RE.match(content):
            if run == 0:
                start = line_no
            run += 1
        else:
            if run >= _OBJ_ROW_RUN:
                findings.append(f"连续 {run} 行对象字面量（L{start} 起）——疑似自建数据数组")
            run = 0
        if _DEMO_ARRAY_RE.match(content):
            findings.append(f"L{line_no}: {content.strip()[:80]}——DEMO/MOCK 型数组声明")
    if run >= _OBJ_ROW_RUN:
        findings.append(f"连续 {run} 行对象字面量（L{start} 起）——疑似自建数据数组")
    return findings


def _scan_zero_wiring(content: str | None) -> str:
    """Check B：全文无 ZK.api/fetch( → 返回 warn 文案（有接线返回空）。"""
    if content and _WIRING_RE.search(content):
        return ""
    return "文件零后端接线（无 ZK.api/fetch 引用）——前端不得自建数据世界（TRAE-086 §truth_source_wiring）"


def _audit_findings(gateway, findings: dict[str, list[str]]) -> None:
    """审计落盘（non-blocking）：供 Owner 回评误报率与升硬决策。"""
    try:
        from pathlib import Path
        audit_dir = Path(gateway.project_root) / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "gate": "FRONTEND-TRUTH-SOURCE",
               "mode": "hard_block" if _HARD_BLOCK else "warn_only", "findings": findings}
        with (audit_dir / "frontend_truth_source.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计失败不阻断
        logger.debug("FRONTEND-TRUTH-SOURCE audit write failed (non-blocking)", exc_info=True)


def make_frontend_truth_source_gate() -> GateSpec:
    """构造前端真源接通 warn 型 GateSpec（TRAE-086 §truth_source_wiring 配套）。

    Returns:
        GateSpec(gate_id="FRONTEND-TRUTH-SOURCE", priority=136)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        js_files = _collect_eligible_js_files(gateway)
        if not js_files:
            return True, ""

        findings: dict[str, list[str]] = {}
        for js_file in js_files:
            # Check A：added 行内联数据数组
            try:
                file_diff = gateway.run_git(
                    ["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", js_file])
                added = _parse_diff_with_line_numbers(file_diff.stdout) if file_diff.returncode == 0 else []
            except Exception as e:  # noqa: BLE001 — fail-open（单文件 diff 异常跳过 Check A）
                logger.warning("FRONTEND-TRUTH-SOURCE: git diff 失败 file=%s, %s", js_file, e)
                added = []
            hits = _scan_inline_data_rows(added)

            # Check B：零后端接线（文件级属性，core/features 目录契约）
            zero = _scan_zero_wiring(_read_staged_file(gateway, js_file))
            if zero:
                hits.append(zero)

            if hits:
                findings[js_file] = hits

        if not findings:
            return True, ""

        _audit_findings(gateway, findings)

        detail_lines = [f"  {f}:{chr(10)}" + "\n".join("    - " + h for h in hs) for f, hs in findings.items()]
        detail = (
            "FRONTEND-TRUTH-SOURCE warn：疑似前端自建数据/零后端接线（TRAE-086 §truth_source_wiring 铁律："
            "施工前后端盘点四步——取数清单→后端三查→三分支决策→接线验收；缺端点先建后端，禁止前端造数据顶上）\n"
            + "\n".join(detail_lines)
            + "\n-> 合法情形自查：①演示诚实纪律标注的断线回退数据（须红灯明示+15s 重试至真源）②纯配置数组（非数据）"
            "③命中即改：接 services/api.js 通道真源。误报请回评 Owner（warn 起步收期误报率，稳定后升硬阻断）"
        )
        if _HARD_BLOCK:
            logger.error("FRONTEND-TRUTH-SOURCE gate block:\n%s", detail)
            return False, detail
        logger.warning("FRONTEND-TRUTH-SOURCE gate warn-only:\n%s", detail)
        return True, detail

    return GateSpec(gate_id="FRONTEND-TRUTH-SOURCE", check=_check, priority=136)
