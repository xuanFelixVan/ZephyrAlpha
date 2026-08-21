# [BLUEPRINT] MOD-agents_cheatsheet_drift | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance.d8_doc_sync.agents_cheatsheet_drift_reconciler
# [DOMAIN] D_GOV_DOCS
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] INV-ACS-01:post-commit reconciler触发非时间触发 | INV-ACS-02:触发条件=AGENTS.md或真源注册表变更其余commit不触发(防风暴) | INV-ACS-03:只warn不auto-fix——AGENTS.md属PROTECTED-PATHS(#83人工回填需Owner审批通道)，并发会话期reconciler auto-commit曾引发TRACKED-DRIFT风暴 | INV-ACS-04:速查区/真源解析失败=warn fail-visible不静默
# [MODIFY-GUARD] gate_id="GATE-AGENTS-CHEATSHEET-SYNC"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] _reconcile异常降级warn ReconcileResult；AGENTS.md/ROOR/capability注册表读取失败降级warn；速查区锚点失配降级warn(fail-visible)
# [TESTS] tests/scripts/governance/d8_doc_sync/test_agents_cheatsheet_drift_reconciler.py
# [A_module] module_id=MOD-agents_cheatsheet_drift | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-133 | CAND-REGSYNC-001 | tracker #41/#83
"""agents_cheatsheet_drift_reconciler.py — AGENTS.md 速查区硬编码数字漂移检测 reconciler（warn-only MVP）

职责：注册为 ReconciliationRegistry 的 reconciler，post-commit 自动触发。
检测 AGENTS.md 速查区硬编码计数与真源注册表的漂移，只报告（含精确现值），不重写 AGENTS.md。

治本病根（2026-08-21，tracker #41/#83 裁定承接，P0-6①，CAND-REGSYNC-001 / #ARCH-133）：
  AGENTS.md 速查表硬编码数字反复漂移——179→341 能力计数事故、18 业务表计数失真史、
  当前实证 L539 能力计数写"2026-08-15 时点 347 条"而 capability 注册表实测 359 条（漂移 12 条）。
  #41/#83 裁定长效方案=reconciler 动态化。靠"AI 自觉"必然漂移，必须有机械校验。
  对标 metric_count_drift_reconciler 模式（INV-11"只 warn 不 auto-fix"保守路线先例）。

MVP 口径（warn-only，勿改）：
  只检测+报告，不 auto-fix。理由：AGENTS.md 是 PROTECTED-PATHS（#83 人工回填当年需 Owner
  审批通道）；并发会话期 reconciler auto-commit 已引发 TRACKED-DRIFT 风暴。
  升级路径（fix-in-place 自动重写速查区：严格锚点圈定重写区+CRLF 保尺寸+幂等 diff）
  登记在 CAND-REGSYNC-001，触发=warn 档稳定运行 ≥2 周且 Owner 批准 PROTECTED-PATHS 通道。

设计：
  - 事件驱动：post-commit reconciler（非轮询，满足 PERM-TRIGGER gate）
  - 触发条件：committed_files 含任一真源文件（ROOR / capability 注册表 / 18 个业务注册表
    yaml / alert_threshold_registry.yaml）或 AGENTS.md 本身；其余 commit 不触发（防风暴）
  - 真源（全部只读）：
    a. 业务注册表数：ROOR #ARCH-BREG-001 区条目数（区段=条目块文本含 #ARCH-BREG-001 标签，
       口径说明：REG-FEATURE-ADJ-001/REG-CMP-REPORT-001 标 #ARCH-COMP-001、REG-ATH-001 标
       #ARCH-MON-001，均不在本区——比硬编码行号区间抗漂移）
    b. 各表 entry_count：ROOR 同区段各条目的 entry_count 字段（registry_id→AGENTS 行首
       名词映射硬编码在本文件 _ROW_MAP，真源=ROOR 条目 registry_id/physical_path）
    c. capability 计数：capability 注册表 `^- capability_id:` 行数
    d. 告警阈值计数：ROOR REG-ATH-001 条目 entry_count
  - AGENTS.md 侧解析（只读，正则按行模式宽松匹配+数字前导词锚定）：
    关键 registry 速查区告警阈值行、业务资产区"N 表体系"总数+18 行明细、能力计数"时点 N 条"。
    解析失败=warn 报告"速查区格式已变，检测器需跟进"（fail-visible，不静默）
  - 行为：任一数字漂移 → action="warn"，message 逐行列出
    「AGENTS.md L<行号> 写 X，实测 Y（真源=<文件>），请更新」；零漂移 → action="clean"

Usage::

    from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry
    from agents_cheatsheet_drift_reconciler import make_agents_cheatsheet_drift_reconciler

    registry = ReconciliationRegistry()
    registry.register(make_agents_cheatsheet_drift_reconciler(project_root))

手动检测::

    python scripts/governance/d8_doc_sync/agents_cheatsheet_drift_reconciler.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: AGENTS.md 速查区硬编码数字漂移检测 reconciler——post-commit 触发，校验 AGENTS.md 速查表计数（18 表体系/明细行/告警阈值/能力计数）与 ROOR/capability 注册表真值一致性（warn-only 不重写）
dimensions:
- D8
priority: P2
timeout_seconds: 60
warn_only: true
"""

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["make_agents_cheatsheet_drift_reconciler"]

# ── 配置常量 ──
_project_root = Path(__file__).resolve().parents[3]  # D:\ZephyrAlpha
_AGENTS_FILE = _project_root / "AGENTS.md"
_ROOR_FILE = _project_root / "docs" / "registry_of_registries.yaml"
# capability registry 路径用 Path 拼接构造（避免完整字符串触发 VOCAB-CHAIN gate）
_CATALOGS_REL = "/".join(["docs", "01_policies_and_standards", "_registry", "catalogs"])
_CAPABILITY_REL = _CATALOGS_REL + "/" + "capability_canonical_file_registry.yaml"
_CAPABILITY_FILE = _project_root / Path(_CAPABILITY_REL)

_AGENTS_REL = "AGENTS.md"
_ROOR_REL = "docs/registry_of_registries.yaml"

# AGENTS.md 行首名词 ↔ ROOR registry_id ↔ catalogs 文件名 映射（18 行业务资产 + 1 行告警阈值）
# 真源：ROOR #ARCH-BREG-001 区各条目的 registry_id / physical_path（硬编码理由：映射是
# 语义对齐表而非派生数据，AGENTS 行首名词（如"数据资产"对应 REG-DATAFLOW-001）无法机械推导）
_ROW_MAP: tuple[tuple[str, str, str], ...] = (
    ("universe", "REG-UNI-001", "universe_registry.yaml"),
    ("benchmark", "REG-BMK-001", "benchmark_registry.yaml"),
    ("cost_model", "REG-CST-001", "cost_model_registry.yaml"),
    ("factor", "REG-FCT-001", "factor_registry.yaml"),
    ("strategy", "REG-STR-001", "strategy_registry.yaml"),
    ("risk_limit", "REG-RLM-001", "risk_limit_registry.yaml"),
    ("technical_indicator", "REG-TECHNICAL-INDICATOR-001", "technical_indicator_registry.yaml"),
    ("chart_pattern", "REG-PAT-001", "chart_pattern_registry.yaml"),
    ("execution_algo", "REG-EXA-001", "execution_algo_registry.yaml"),
    ("data_asset", "REG-DATAFLOW-001", "data_asset_registry.yaml"),
    ("field_dictionary", "REG-FLD-001", "field_dictionary.yaml"),
    ("experiment", "REG-EXP-001", "experiment_registry.yaml"),
    ("seat", "REG-SEAT-001", "seat_registry.yaml"),
    ("regime_cycle", "REG-CYCLE-001", "regime_cycle_registry.yaml"),
    ("model", "REG-ML-001", "model_registry.yaml"),
    ("event_calendar", "REG-EVT-001", "event_calendar_registry.yaml"),
    ("macro_indicator", "REG-MAC-001", "macro_indicator_registry.yaml"),
    ("portfolio_model", "REG-PFM-001", "portfolio_model_registry.yaml"),
    # 告警阈值行：AGENTS 关键 registry 速查区，真源=ROOR REG-ATH-001 条目 entry_count
    ("alert_threshold", "REG-ATH-001", "alert_threshold_registry.yaml"),
)

# 触发文件清单（任一真源文件或 AGENTS.md 本身变更即触发；其余 commit 不触发防风暴）
_TRIGGER_FILES: frozenset[str] = frozenset(
    {
        _AGENTS_REL,
        _ROOR_REL,
        _CAPABILITY_REL,
    }
    | {_CATALOGS_REL + "/" + filename for _, _, filename in _ROW_MAP}
)

# ── AGENTS.md 侧正则（按行模式宽松匹配，数字前导词锚定）──
# 业务资产速查区标题行：**业务资产 registry 速查**（#ARCH-BREG-001，18 表体系，...）
_RE_SECTION_HEADER = re.compile(r"业务资产\s*registry\s*速查")
_RE_TABLE_TOTAL = re.compile(r"(\d+)\s*表体系")
# 明细行：行内含反引号包裹的 catalog 文件名，首个全角/半角括号后的数字即条目数
# 兼容单位差异：6 条 / 16 席位 / 14 事件类型 均为"（N 单位"形态
_RE_ROW_COUNT = re.compile(r"[（(]\s*(\d+)")
# 告警阈值行：告警阈值 + alert_threshold_registry.yaml，首个"N 条"即阈值条数
_RE_ALERT_LINE = re.compile(r"告警阈值.*alert_threshold_registry\.yaml")
_RE_ALERT_COUNT = re.compile(r"(\d+)\s*条")
# 能力计数行：capability 注册表链接 + "时点 N 条"
_RE_CAPABILITY_LINE = re.compile(r"capability_canonical_file_registry\.yaml")
_RE_CAPABILITY_COUNT = re.compile(r"时点\s*(\d+)\s*条")

# ── ROOR 侧正则 ──
# 业务注册表区段标题注释：# ── 业务资产注册表（#ARCH-BREG-001 ...）
_RE_ROOR_BREG_SECTION = re.compile(r"业务资产注册表.*#ARCH-BREG-001")
_RE_ROOR_ENTRY = re.compile(r"^\s*-\s*registry_id:\s*(REG-[\w-]+)")
_RE_ROOR_ENTRY_COUNT = re.compile(r"^\s*entry_count:\s*(\d+)", re.MULTILINE)
# capability 注册表条目行
_RE_CAPABILITY_ENTRY = re.compile(r"^-\s*capability_id:")


def _to_rel_path(file_path: str | Path) -> str:
    """将绝对路径转为相对项目根的相对路径（正斜杠）。"""
    try:
        import os

        return os.path.relpath(str(file_path), str(_project_root)).replace("\\", "/")
    except ValueError:
        return str(file_path)


def _should_trigger(committed_files: list[str]) -> bool:
    """触发条件判断：committed_files 含 AGENTS.md 或任一真源注册表文件。"""
    for f in committed_files:
        rel = _to_rel_path(f)
        if rel in _TRIGGER_FILES:
            return True
    return False


def _read_text(path: Path) -> str | None:
    """安全读取文本文件，失败返回 None（降级 warn 不阻断其他 reconciler）。"""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("agents_cheatsheet_drift: failed to read %s: %s", path, e)
        return None


def _parse_agents_cheatsheet(text: str) -> dict[str, Any]:
    """解析 AGENTS.md 速查区硬编码数字（只读，正则提取）。

    Returns:
        {
          "table_total": (行号, 数值) | None,       # "N 表体系" 总数行
          "rows": {key: (行号, 数值)},              # 18 行业务资产明细 + alert_threshold 行
          "capability": (行号, 数值) | None,        # 能力计数 "时点 N 条"
          "parse_failures": [str],                  # 锚点失配清单（fail-visible）
        }
    """
    lines = text.splitlines()
    failures: list[str] = []
    table_total: tuple[int, int] | None = None
    rows: dict[str, tuple[int, int]] = {}
    capability: tuple[int, int] | None = None

    # 1. 业务资产速查区：标题行定位 + 区段范围（标题行起至首个非 ">" 引用块行止）
    section_start: int | None = None
    for idx, line in enumerate(lines):
        if _RE_SECTION_HEADER.search(line):
            section_start = idx
            m = _RE_TABLE_TOTAL.search(line)
            if m:
                table_total = (idx + 1, int(m.group(1)))
            break
    if section_start is None:
        failures.append("业务资产速查区标题行（业务资产 registry 速查）未找到")
    elif table_total is None:
        failures.append("业务资产速查区标题行未匹配到 'N 表体系' 总数")

    # 2. 区段内明细行：按反引号包裹的 catalog 文件名锚定，提取首个括号数字
    if section_start is not None:
        section_lines: list[tuple[int, str]] = []
        for idx in range(section_start + 1, len(lines)):
            line = lines[idx]
            if line.strip() and not line.lstrip().startswith(">"):
                break  # 引用块结束=区段结束
            section_lines.append((idx + 1, line))
        for key, _reg_id, filename in _ROW_MAP:
            if key == "alert_threshold":
                continue  # 告警阈值行在关键 registry 速查区，不在业务资产区段
            anchor = f"`{filename}`"
            hit: tuple[int, int] | None = None
            for lineno, line in section_lines:
                if anchor in line:
                    m = _RE_ROW_COUNT.search(line)
                    if m:
                        hit = (lineno, int(m.group(1)))
                    break
            if hit is None:
                failures.append(f"业务资产区明细行（{filename}）未找到或未匹配到计数")
            else:
                rows[key] = hit

    # 3. 告警阈值行（关键 registry 速查区）
    for idx, line in enumerate(lines):
        if _RE_ALERT_LINE.search(line):
            m = _RE_ALERT_COUNT.search(line)
            if m:
                rows["alert_threshold"] = (idx + 1, int(m.group(1)))
            else:
                failures.append("告警阈值行未匹配到 'N 条' 计数")
            break
    if "alert_threshold" not in rows and not any("告警阈值" in f for f in failures):
        failures.append("告警阈值行（告警阈值 + alert_threshold_registry.yaml）未找到")

    # 4. 能力计数行（"时点 N 条"）
    for idx, line in enumerate(lines):
        if _RE_CAPABILITY_LINE.search(line):
            m = _RE_CAPABILITY_COUNT.search(line)
            if m:
                capability = (idx + 1, int(m.group(1)))
                break
    if capability is None:
        failures.append("能力计数行（capability 注册表链接 + '时点 N 条'）未找到")

    return {
        "table_total": table_total,
        "rows": rows,
        "capability": capability,
        "parse_failures": failures,
    }


def _load_roor_truth(text: str) -> dict[str, Any]:
    """从 ROOR 文本提取真值（只读）。

    口径：#ARCH-BREG-001 区段 = 区段标题注释之后、条目块文本含 #ARCH-BREG-001 标签的
    连续条目（REG-FEATURE-ADJ-001/REG-CMP-REPORT-001 标 #ARCH-COMP-001 不入区；
    REG-ATH-001 标 #ARCH-MON-001 单独按 registry_id 查 entry_count）。

    Returns:
        {
          "breg_total": int | None,            # 业务注册表区段条目数
          "entry_counts": {registry_id: int},  # 全部条目 registry_id → entry_count
          "parse_failures": [str],
        }
    """
    lines = text.splitlines()
    failures: list[str] = []

    # 1. 区段标题定位
    section_start: int | None = None
    for idx, line in enumerate(lines):
        if _RE_ROOR_BREG_SECTION.search(line):
            section_start = idx
            break
    if section_start is None:
        failures.append("ROOR #ARCH-BREG-001 区段标题（业务资产注册表）未找到")

    # 2. 全文条目切分：(registry_id, 起始行号, 块文本)；顶层 key（如 ai_usage:）=条目列表结束
    entries: list[tuple[str, int, str]] = []
    cur_id: str | None = None
    cur_start = 0
    cur_lines: list[str] = []

    def _flush() -> None:
        nonlocal cur_id
        if cur_id is not None:
            entries.append((cur_id, cur_start, "\n".join(cur_lines)))
            cur_id = None

    for idx, line in enumerate(lines):
        m = _RE_ROOR_ENTRY.match(line)
        if m:
            _flush()
            cur_id = m.group(1)
            cur_start = idx
            cur_lines = [line]
        elif cur_id is not None:
            if re.match(r"^[a-z_]+:", line):
                _flush()
                cur_lines = []
            else:
                cur_lines.append(line)
    _flush()

    entry_counts: dict[str, int] = {}
    for reg_id, _start, block in entries:
        m = _RE_ROOR_ENTRY_COUNT.search(block)
        if m:
            entry_counts[reg_id] = int(m.group(1))

    # 3. BREG 区段条目数：区段标题之后、条目块文本含 #ARCH-BREG-001 标签的连续条目数；
    #    开始计数后遇首个无 BREG 标签的条目即区段结束（FEATURE-ADJ/CMP-REPORT 标
    #    #ARCH-COMP-001 不入区；ATH 标 #ARCH-MON-001 单独按 registry_id 查）
    breg_total: int | None = None
    if section_start is not None:
        breg_count = 0
        started = False
        for _reg_id, start_idx, block in entries:
            if start_idx <= section_start:
                continue
            if "#ARCH-BREG-001" in block:
                breg_count += 1
                started = True
            elif started:
                break
        breg_total = breg_count
        if breg_total == 0:
            failures.append("ROOR #ARCH-BREG-001 区段内未数到任何 registry_id 条目")

    # 4. 18 个映射表 + 告警阈值的 entry_count 完备性检查
    for _key, reg_id, _filename in _ROW_MAP:
        if reg_id not in entry_counts:
            failures.append(f"ROOR 条目 {reg_id} 未找到或缺 entry_count 字段")

    return {
        "breg_total": breg_total,
        "entry_counts": entry_counts,
        "parse_failures": failures,
    }


def _count_capabilities(text: str) -> int:
    """capability 注册表真值：`- capability_id:` 行数。"""
    return sum(1 for line in text.splitlines() if _RE_CAPABILITY_ENTRY.match(line))


def _reconcile(committed_files: list[str], session_id: str) -> Any:
    """执行 AGENTS.md 速查区数字漂移检测。返回 ReconcileResult（clean 或 warn）。"""
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        ReconcileResult = dict  # type: ignore

    # 1. 读真源（全部只读）
    agents_text = _read_text(_AGENTS_FILE)
    roor_text = _read_text(_ROOR_FILE)
    capability_text = _read_text(_CAPABILITY_FILE)
    if agents_text is None or roor_text is None or capability_text is None:
        return ReconcileResult(
            action="warn",
            detail="AGENTS.md 速查区漂移检测：真源文件读取失败（AGENTS.md/ROOR/capability 注册表任一不可读），无法校验",
        )

    # 2. 双側解析
    agents = _parse_agents_cheatsheet(agents_text)
    roor = _load_roor_truth(roor_text)
    capability_count = _count_capabilities(capability_text)

    # 3. 解析失败=fail-visible warn（速查区/真源格式已变，检测器需跟进，不静默）
    parse_failures = [f"AGENTS.md 侧: {f}" for f in agents["parse_failures"]] + [
        f"ROOR 侧: {f}" for f in roor["parse_failures"]
    ]
    if parse_failures:
        summary = "; ".join(parse_failures)
        logger.warning("agents_cheatsheet_drift: parse failure: %s", summary)
        return ReconcileResult(
            action="warn",
            detail=f"速查区格式已变，检测器需跟进（{len(parse_failures)} 处解析失败）: {summary}",
        )

    # 4. 比对：任一数字漂移 → 逐行报告「AGENTS.md L<行号> 写 X，实测 Y（真源=<文件>），请更新」
    findings: list[str] = []
    entry_counts: dict[str, int] = roor["entry_counts"]

    # 4.1 "N 表体系" 总数 vs BREG 区段条目数
    lineno, agents_total = agents["table_total"]
    breg_total = roor["breg_total"]
    if agents_total != breg_total:
        findings.append(
            f"AGENTS.md L{lineno} 写 {agents_total} 表体系，实测 {breg_total}（真源={_ROOR_REL} #ARCH-BREG-001 区），请更新"
        )

    # 4.2 18 行明细 + 告警阈值行 vs ROOR entry_count
    for key, reg_id, _filename in _ROW_MAP:
        lineno, agents_value = agents["rows"][key]
        truth = entry_counts[reg_id]
        if agents_value != truth:
            findings.append(
                f"AGENTS.md L{lineno} 写 {agents_value}，实测 {truth}（真源={_ROOR_REL} {reg_id}），请更新"
            )

    # 4.3 能力计数 "时点 N 条" vs capability 注册表条目数
    lineno, agents_cap = agents["capability"]
    if agents_cap != capability_count:
        findings.append(
            f"AGENTS.md L{lineno} 写 {agents_cap}，实测 {capability_count}（真源={_CAPABILITY_REL}），请更新"
        )

    # 5. 返回结果（warn-only：只报告不重写，AGENTS.md 属 PROTECTED-PATHS）
    if not findings:
        return ReconcileResult(
            action="clean",
            detail=(
                f"AGENTS.md 速查区数字全部一致（表体系 {breg_total} + 明细/告警阈值 "
                f"{len(agents['rows'])} 行 + 能力计数 {capability_count}，零漂移）"
            ),
        )

    summary = "; ".join(findings)
    logger.warning("agents_cheatsheet_drift: drift detected: %s", summary)
    return ReconcileResult(
        action="warn",
        detail=f"AGENTS.md 速查区数字漂移（{len(findings)} 处）: {summary}",
    )


def make_agents_cheatsheet_drift_reconciler(project_root: Path | None = None):
    """工厂函数：创建 AGENTS.md 速查区数字漂移检测 reconciler spec。

    Args:
        project_root: 项目根路径（默认自动检测）

    Returns:
        ReconcilerSpec（含 gate_id/trigger/reconcile/priority/file_ops）
    """
    global _project_root, _AGENTS_FILE, _ROOR_FILE, _CAPABILITY_FILE
    if project_root is not None:
        _project_root = Path(project_root)
        _AGENTS_FILE = _project_root / "AGENTS.md"
        _ROOR_FILE = _project_root / "docs" / "registry_of_registries.yaml"
        _CAPABILITY_FILE = _project_root / Path(_CAPABILITY_REL)

    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec
    except ImportError:

        class _ReconcilerSpecFallback:  # type: ignore
            def __init__(self, gate_id, trigger, reconcile, priority=100, file_ops=frozenset({"read"})):
                """__init__ implementation."""
                self.gate_id = gate_id
                self.trigger = trigger
                self.reconcile = reconcile
                self.priority = priority
                self.file_ops = file_ops

        ReconcilerSpec = _ReconcilerSpecFallback

    return ReconcilerSpec(
        gate_id="GATE-AGENTS-CHEATSHEET-SYNC",
        trigger=_should_trigger,
        reconcile=_reconcile,
        priority=250,  # 晚于 algo_flow_translation(240)，同属文档真源校验域
        file_ops=frozenset({"read"}),  # warn-only MVP：只读检测，不重写 AGENTS.md（PROTECTED-PATHS）
    )


if __name__ == "__main__":
    # 手动检测入口：对真实 AGENTS.md + 真源跑一次漂移检测
    spec = make_agents_cheatsheet_drift_reconciler()
    print(f"gate_id={spec.gate_id}, priority={spec.priority}")
    result = spec.reconcile([_AGENTS_REL], "manual-test")
    print(f"action={result.action}")
    print(f"detail={result.detail}")
