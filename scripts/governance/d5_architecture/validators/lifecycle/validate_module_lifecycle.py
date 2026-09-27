# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py | §
# [MODULE] scripts.governance.d5_architecture.validators.lifecycle.validate_module_lifecycle
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants; zephyr.shared.io.yaml_utils
# [CONSUMERS] .pre-commit gate-module-lifecycle-transition（P2 挂门，S9 簿 §4.5 形态）; GitCommitGateway ORPHAN-MODULE 配对（trae_032:632）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 枚举/转换表动态加载 PS-VOC-027（禁硬编码）；own-diff 作用域（--staged 只查暂存变更条目）；P0 红线硬拦；archived ID 禁重分配
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=合规 1=findings 2=error；--staged 模式=ORPHAN-MODULE 转换门入口（禁跳阶段/禁逆向/P0/deprecated 新增消费者/archived ID 重用）
# [TESTS] tests/governance/lifecycle/test_validate_module_lifecycle.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""validate_module_lifecycle.py — 模块生命周期转换门（ORPHAN-MODULE 执行体，B10-P1 升级）

对标：GOV-MOD-003 MLC-001/002/003（模块8阶段状态机）；S9 挖矿簿 §4.5/§4.6。
gate_id=ORPHAN-MODULE（trae_032:632 paired_gate_id 立法；gate_registry.yaml:1459 存根行
files_trigger 空——本件即其真实执行体，.pre-commit 挂门=P2 余量，本批禁碰该文件）。

B10-P1 修复（S9 簿 §4.6 四项）：
1. 词表平面分离：剔除文档 frontmatter 扫描，只扫账本 architecture_model/module_id_registry.yaml
   （职责归一；旧实现把文档 3 值词表混装模块 8 值词表，实测 318 违规/316 误报）。
2. 大小写归一：status 比较前 .lower()（旧误报主因）。
3. load_module_registry() 路径治本：指向实存账本并真正接线（旧路径指向不存在的 catalogs 册）。
4. 补 --staged 转换门模式 + 补测试。

门规格（S9 簿 §4.5）：
  枚举合法    status ∈ PS-VOC-027 动态加载（禁硬编码字面量）
  转换合法    from→to ∈ 词表 next_states（禁跳阶段/禁逆向；逆向白名单 testing→in_dev、
              suspended→active 已内嵌词表）；deprecated→archived 前置校验 retain_until
              已过（ABS-22 张力的机械化消解：90 天保留期满方可归档）
  P0 红线     P0 禁 suspended；P0 deprecated 须 successor active>=30 天
  deprecated  必填 superseded_by；暂存 diff 新增其 module_id 引用=新增消费者→拦
  archived    module_id 禁重新分配（撞 archived 记录→REJECT）

ABS-22 消解依据：S9 簿 §3.5——"跨级"指 active→archived 跳阶段；deprecated→archived
合法但须满 90 天保留期（PS-VOC-027 next_states deprecated→archived）。
"""

from __future__ import annotations

__manifest__ = """
args: [--staged]
description: 模块生命周期转换门（ORPHAN-MODULE 执行体 — 8阶段状态机+转换合法性+P0红线）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

from zephyr.shared.io.yaml_utils import DEFAULT_VOCAB_DIR  # noqa: E402  SSoT 词表目录

ensure_utf8_stdout()
import argparse  # noqa: E402
import subprocess  # noqa: E402

import yaml  # noqa: E402

DEFAULT_REGISTRY_REL = "architecture_model/module_id_registry.yaml"
VOCAB_FILE = "module_lifecycle_status_vocabulary.yaml"  # PS-VOC-027
DEPRECATED_MIN_DAYS = 90
P0_SUCCESSOR_MIN_DAYS = 30

# own-diff 作用域：新增消费者扫描的豁免路径（归档/草稿区/运行时不算新增 consumer）
CONSUMER_SCAN_EXEMPT = ("/_archive/", ".aidrafts/", ".runtime/", "node_modules/", ".git/")
# 消费者判定口径=代码/配置面（与 MLC-003 step2 活引用分类同口径；docs=历史记载放行）
CONSUMER_CODE_PREFIXES = ("src/", "scripts/", "config/", "data/")


def load_transition_table(vocab_path: Path | None = None) -> dict[str, list[str]]:
    """动态加载 PS-VOC-027 next_states 转换表（SSoT，禁硬编码枚举）。"""
    p = vocab_path or (DEFAULT_VOCAB_DIR / VOCAB_FILE)
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    table: dict[str, list[str]] = {}
    for v in data.get("values") or []:
        if isinstance(v, dict) and v.get("value"):
            table[str(v["value"])] = [str(s) for s in (v.get("next_states") or [])]
    if not table:
        raise ValueError(f"词表为空: {p}")
    return table


# 治本（2026-06-30 引入；B10-P1 沿用动态加载，键集=转换表键集）
VALID_MODULE_STATUSES = set(load_transition_table().keys())


def normalize_status(status: Any) -> str:
    """大小写归一（S9 簿 §4.6 修复 2：旧实现 316 误报主因）。"""
    return str(status or "").strip().lower()


def load_module_registry(registry_path: Path | None = None) -> dict:
    """加载模块注册表（B10-P1 治本：路径指向实存账本 architecture_model/module_id_registry.yaml）。"""
    p = registry_path or (REPO_ROOT / DEFAULT_REGISTRY_REL)
    if not p.exists():
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError):
        return {}


def _is_p0(entry: dict) -> bool:
    return "P0" in str(entry.get("priority", "") or "")


def successor_active_days(entry: dict, repo_root: Path = REPO_ROOT) -> int | None:
    """successor active 起算天数：注册表无记录时回退 git log 首次出现日期（S9 簿 §4.1 P0 机械化）。"""
    path = str(entry.get("path") or "")
    if not path:
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "log", "--reverse", "--format=%ci", "--", path],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None
    if not out:
        return None
    try:
        first = datetime.strptime(out.splitlines()[0].split("+")[0].strip()[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return (datetime.now() - first).days


def _status_enum_findings(
    raw_status: str,
    status: str,
    table: dict[str, list[str]],
    module_id: str,
    rel: str,
) -> list[dict]:
    """枚举/大小写检查：MISSING_STATUS / CASE_DRIFT / INVALID_STATUS。"""
    findings: list[dict] = []
    if not raw_status:
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "MISSING_STATUS",
                "detail": "条目缺 status 字段",
                "severity": "MEDIUM",
            }
        )
    elif raw_status != status and status in table:
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "CASE_DRIFT",
                "detail": f"status='{raw_status}' 大小写越出词表（归一='{status}'）",
                "severity": "MEDIUM",
            }
        )
    if status and status not in table:
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "INVALID_STATUS",
                "detail": f"status='{raw_status}' 不在 8 阶段枚举（合法值: {', '.join(sorted(table))}）"
                "——越界值按 trae_032 修正批收敛映射逐条迁移（P3）",
                "severity": "HIGH",
            }
        )
    return findings


def _superseded_by_findings(
    entry: dict,
    status: str,
    superseded_by: Any,
    module_id: str,
    rel: str,
    today: datetime | None,
) -> list[dict]:
    """superseded_by 完整性检查：MISSING_SUPERSEDED_BY / DEPRECATION_TOO_EARLY / ACTIVE_WITH_SUPERSEDED_BY。"""
    findings: list[dict] = []
    if status == "deprecated" and not superseded_by:
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "MISSING_SUPERSEDED_BY",
                "detail": "deprecated 条目缺 superseded_by（trae_032:333 必填）",
                "severity": "HIGH",
            }
        )
    if status == "deprecated":
        dep_date = str(entry.get("deprecated_date", "") or "")
        if dep_date:
            try:
                days = ((today or datetime.now()) - datetime.strptime(dep_date, "%Y-%m-%d")).days
                if days < DEPRECATED_MIN_DAYS:
                    findings.append(
                        {
                            "module_id": module_id,
                            "where": rel,
                            "type": "DEPRECATION_TOO_EARLY",
                            "detail": f"deprecated 仅 {days} 天，保留期需 >= {DEPRECATED_MIN_DAYS} 天",
                            "severity": "MEDIUM",
                        }
                    )
            except ValueError:
                pass
    if status == "active" and superseded_by:
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "ACTIVE_WITH_SUPERSEDED_BY",
                "detail": "active 条目不应带 superseded_by（退役字段残留）",
                "severity": "MEDIUM",
            }
        )
    return findings


def _p0_successor_findings(
    superseded_by: Any,
    module_id: str,
    rel: str,
    successor_age_fn: Callable[[dict], int | None],
    lookup: Callable[[str], dict | None],
) -> list[dict]:
    """P0 退役替代模块检查：P0_SUCCESSOR_MISSING / NOT_ACTIVE / AGE_UNKNOWN / TOO_YOUNG。"""
    findings: list[dict] = []
    succ = lookup(str(superseded_by or ""))
    if succ is None:
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "P0_SUCCESSOR_MISSING",
                "detail": f"P0 退役替代模块 {superseded_by} 不在注册表",
                "severity": "HIGH",
            }
        )
        return findings
    if normalize_status(succ.get("status")) != "active":
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "P0_SUCCESSOR_NOT_ACTIVE",
                "detail": f"P0 退役要求替代模块 status==active（现={succ.get('status')}，trae_032:302）",
                "severity": "HIGH",
            }
        )
        age: int | None = None
    else:
        age = successor_age_fn(succ)
    if normalize_status(succ.get("status")) == "active":
        if age is None:
            findings.append(
                {
                    "module_id": module_id,
                    "where": rel,
                    "type": "P0_SUCCESSOR_AGE_UNKNOWN",
                    "detail": "P0 替代模块 active≥30 天无法机械判定（缺记录且 git 无历史）——保守拦截，Owner 裁定可豁免",
                    "severity": "HIGH",
                }
            )
        elif age < P0_SUCCESSOR_MIN_DAYS:
            findings.append(
                {
                    "module_id": module_id,
                    "where": rel,
                    "type": "P0_SUCCESSOR_TOO_YOUNG",
                    "detail": f"P0 替代模块 active 仅 {age} 天（须 >= {P0_SUCCESSOR_MIN_DAYS}，trae_032:302）",
                    "severity": "HIGH",
                }
            )
    return findings


def _p0_findings(
    entry: dict,
    status: str,
    superseded_by: Any,
    module_id: str,
    rel: str,
    successor_age_fn: Callable[[dict], int | None],
    lookup: Callable[[str], dict | None],
) -> list[dict]:
    """P0 红线检查：P0_SUSPENDED + 退役替代模块活性/账龄。"""
    findings: list[dict] = []
    if status == "suspended":
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "P0_SUSPENDED",
                "detail": "P0 模块禁止 suspended（trae_032:301，须走紧急修复流程）",
                "severity": "HIGH",
            }
        )
    if status == "deprecated":
        findings += _p0_successor_findings(superseded_by, module_id, rel, successor_age_fn, lookup)
    return findings


def entry_findings(
    entry: dict,
    table: dict[str, list[str]],
    *,
    where: str = DEFAULT_REGISTRY_REL,
    successor_age_fn: Callable[[dict], int | None] = successor_active_days,
    today: datetime | None = None,
    registry_lookup: Callable[[str], dict | None] | None = None,
) -> list[dict]:
    """条目级检查（枚举/大小写/deprecated 完整性/90 天/P0 红线）——全扫与 --staged 共用。"""
    findings: list[dict] = []
    module_id = str(entry.get("module_id", "") or "")
    if not module_id:
        return findings
    raw_status = str(entry.get("status", "") or "")
    status = normalize_status(raw_status)
    rel = f"{where}:{module_id}"
    lookup = registry_lookup or load_module_registry_entry
    superseded_by = entry.get("superseded_by")

    findings += _status_enum_findings(raw_status, status, table, module_id, rel)
    findings += _superseded_by_findings(entry, status, superseded_by, module_id, rel, today)
    if _is_p0(entry):
        findings += _p0_findings(entry, status, superseded_by, module_id, rel, successor_age_fn, lookup)
    return findings


def load_module_registry_entry(module_id: str, registry_path: Path | None = None) -> dict | None:
    reg = load_module_registry(registry_path)
    for e in reg.get("registered_ids") or []:
        if isinstance(e, dict) and e.get("module_id") == module_id:
            return e
    return None


def archived_ids(registry: dict, retirement_records: list[dict] | None = None) -> set[str]:
    """archived 身份集：条目 status==archived ∪ 台账 archived_date 非空（ID 永不回收）。"""
    ids = {
        str(e.get("module_id"))
        for e in registry.get("registered_ids") or []
        if isinstance(e, dict) and normalize_status(e.get("status")) == "archived"
    }
    for r in retirement_records or []:
        if isinstance(r, dict) and r.get("archived_date"):
            ids.add(str(r.get("module_id")))
    return ids


@dataclass(frozen=True)
class _TransitionCtx:
    """转换判定上下文（参数对象——收敛 _transition_legality_findings/
    _evaluate_entry_transition 形参个数至 ≤7，行为零变化）。"""

    table: dict[str, list[str]]
    records_map: dict[str, dict]
    old_map: dict[str, dict]
    arch: set[str]
    succ_map: dict[str, dict]
    where: str
    successor_age_fn: Callable[[dict], int | None]
    now: datetime


def _retain_until_findings(
    module_id: str,
    rel: str,
    rec: dict,
    entry: dict,
    now: datetime,
) -> list[dict]:
    """deprecated→archived 保留期检查：RETAIN_RECORD_MISSING / RETAIN_NOT_PASSED。"""
    findings: list[dict] = []
    retain = str(rec.get("retain_until") or entry.get("retain_until") or "")
    if not retain:
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "RETAIN_RECORD_MISSING",
                "detail": "deprecated→archived 缺 retain_until 记录（90 天保留期无法判定，ABS-22 消解前置）",
                "severity": "HIGH",
            }
        )
    else:
        try:
            if now < datetime.strptime(retain, "%Y-%m-%d"):
                findings.append(
                    {
                        "module_id": module_id,
                        "where": rel,
                        "type": "RETAIN_NOT_PASSED",
                        "detail": f"retain_until={retain} 未到期，禁归档（90 天保留期，ABS-22 消解）",
                        "severity": "HIGH",
                    }
                )
        except ValueError:
            findings.append(
                {
                    "module_id": module_id,
                    "where": rel,
                    "type": "RETAIN_RECORD_MISSING",
                    "detail": f"retain_until='{retain}' 非法日期",
                    "severity": "HIGH",
                }
            )
    return findings


def _transition_legality_findings(
    entry: dict,
    ctx: _TransitionCtx,
    module_id: str,
    rel: str,
    frm: str,
    to: str,
) -> list[dict]:
    """转换合法性判定（MLC-001/002）：跳阶段/逆向/保留期前置。"""
    findings: list[dict] = []
    table = ctx.table
    if frm == to or not frm or not to:
        return findings
    if frm not in table:
        return findings  # 越界 legacy 起点不做转换判（INVALID_STATUS 已报，收敛在 P3）
    if to not in table:
        return findings
    if to not in table[frm]:
        kind = "逆向转换" if _is_reverse(table, frm, to) else "跳阶段"
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "ILLEGAL_TRANSITION",
                "detail": f"{frm}→{to} 非法{kind}（词表 next_states[{frm}]={table[frm]}；MLC-001/002）",
                "severity": "HIGH",
            }
        )
        return findings
    if frm == "deprecated" and to == "archived":
        rec = ctx.records_map.get(module_id) or {}
        findings += _retain_until_findings(module_id, rel, rec, entry, ctx.now)
    return findings


def _evaluate_entry_transition(entry: dict, ctx: _TransitionCtx) -> list[dict]:
    """单条目 own-diff 转换判定：条目级检查 + archived ID 重用 + from→to 合法性。"""
    findings: list[dict] = []
    module_id = str(entry["module_id"])
    rel = f"{ctx.where}:{module_id}"
    findings += entry_findings(
        entry,
        ctx.table,
        where=ctx.where,
        successor_age_fn=ctx.successor_age_fn,
        today=ctx.now,
        registry_lookup=ctx.succ_map.get,
    )
    old = ctx.old_map.get(module_id)
    if old is None:
        if module_id in ctx.arch:
            findings.append(
                {
                    "module_id": module_id,
                    "where": rel,
                    "type": "ARCHIVED_ID_REUSE",
                    "detail": "archived 的 module_id 禁重新分配（trae_032:295,303 ID 永不回收）",
                    "severity": "HIGH",
                }
            )
        return findings
    frm = normalize_status(old.get("status"))
    to = normalize_status(entry.get("status"))
    if module_id in ctx.arch and frm == "archived" and to != "archived":
        findings.append(
            {
                "module_id": module_id,
                "where": rel,
                "type": "ARCHIVED_ID_REUSE",
                "detail": f"archived 条目重激活/重分配（{frm}→{to}，trae_032:295,303 ID 永不回收）",
                "severity": "HIGH",
            }
        )
        return findings
    findings += _transition_legality_findings(entry, ctx, module_id, rel, frm, to)
    return findings


def evaluate_transitions(
    old_entries: list[dict],
    new_entries: list[dict],
    table: dict[str, list[str]],
    *,
    retirement_records: list[dict] | None = None,
    successor_age_fn: Callable[[dict], int | None] = successor_active_days,
    today: datetime | None = None,
    where: str = DEFAULT_REGISTRY_REL,
) -> list[dict]:
    """转换合法性门（--staged own-diff 作用域：只对变更条目判 from→to）。"""
    findings: list[dict] = []
    old_map = {str(e.get("module_id")): e for e in old_entries if isinstance(e, dict) and e.get("module_id")}
    arch = archived_ids({"registered_ids": old_entries}, retirement_records)
    now = today or datetime.now()
    records_map = {str(r.get("module_id")): r for r in (retirement_records or []) if isinstance(r, dict)}
    succ_map = {
        str(e.get("module_id")): e
        for e in list(old_entries) + list(new_entries)
        if isinstance(e, dict) and e.get("module_id")
    }

    ctx = _TransitionCtx(
        table=table,
        records_map=records_map,
        old_map=old_map,
        arch=arch,
        succ_map=succ_map,
        where=where,
        successor_age_fn=successor_age_fn,
        now=now,
    )

    for entry in new_entries:
        if not isinstance(entry, dict) or not entry.get("module_id"):
            continue
        findings += _evaluate_entry_transition(entry, ctx)
    return findings


def _is_reverse(table: dict[str, list[str]], frm: str, to: str) -> bool:
    """8 阶段线性序上的逆向判定（仅用于违规文案；合法性唯一判据=next_states）。"""
    order = ["planned", "in_design", "in_dev", "testing", "active", "suspended", "deprecated", "archived"]
    if frm in order and to in order:
        return order.index(to) < order.index(frm)
    return False


def scan_deprecated_new_consumers(
    deprecated_ids: set[str],
    added_lines: list[tuple[str, str]],
    *,
    registry_rel: str = DEFAULT_REGISTRY_REL,
) -> list[dict]:
    """deprecated 阶段禁新增 consumer（trae_032:415）：暂存新增行提及 deprecated module_id → 拦。

    判定口径=代码/配置面（CONSUMER_CODE_PREFIXES）；docs 命中=历史记载放行（同 step2 分类）。
    """
    findings: list[dict] = []
    if not deprecated_ids:
        return findings
    for rel, line in added_lines:
        norm = rel.replace("\\", "/")
        if norm == registry_rel or any(m in norm for m in CONSUMER_SCAN_EXEMPT):
            continue
        if not norm.startswith(CONSUMER_CODE_PREFIXES):
            continue
        for mid in deprecated_ids:
            if mid and mid in line:
                findings.append(
                    {
                        "module_id": mid,
                        "where": f"{rel}",
                        "type": "DEPRECATED_NEW_CONSUMER",
                        "detail": f"deprecated 模块 {mid} 出现新增代码引用（禁新增 consumer，trae_032:415）",
                        "severity": "HIGH",
                    }
                )
                break
    return findings


# ---------- git --staged 取证 ----------


def staged_old_registry_text(repo_root: Path, rel: str) -> str | None:
    """暂存区（index）版本文本；文件未暂存/新增返回 None。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "show", f":{rel}"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout if out.returncode == 0 else None


def staged_added_lines(repo_root: Path) -> list[tuple[str, str]]:
    """全部暂存文件的新增行（unified=0）：[(rel_path, line_text)]。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--cached", "--unified=0"],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    lines: list[tuple[str, str]] = []
    cur = ""
    for ln in out.splitlines():
        if ln.startswith("+++ b/"):
            cur = ln[6:].replace("\\", "/")
        elif ln.startswith("+") and not ln.startswith("+++"):
            lines.append((cur, ln[1:]))
    return lines


def staged_files(repo_root: Path) -> list[str]:
    """暂存文件清单（相对路径，/ 归一）。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def _staged_registry_diff_findings(
    repo_root: Path,
    registry_rel: str,
    new_text: str,
    table: dict[str, list[str]],
) -> list[dict]:
    """账本暂存 diff 转换校验：old 有=判 from→to；old 无（新增）=逐条 entry_findings。"""
    findings: list[dict] = []
    old_text = staged_old_registry_text(repo_root, registry_rel)
    new_reg = yaml.safe_load(new_text) or {}
    if old_text is not None:
        old_reg = yaml.safe_load(old_text) or {}
        findings += evaluate_transitions(
            old_reg.get("registered_ids") or [],
            new_reg.get("registered_ids") or [],
            table,
            retirement_records=new_reg.get("retirement_records") or [],
        )
    else:
        for e in new_reg.get("registered_ids") or []:
            findings += entry_findings(e, table)
    return findings


def run_staged_gate(
    repo_root: Path = REPO_ROOT,
    registry_rel: str = DEFAULT_REGISTRY_REL,
    *,
    table: dict[str, list[str]] | None = None,
) -> list[dict]:
    """--staged 转换门入口：账本暂存 diff 转换校验 + 全暂存面 deprecated 新增消费者扫描。

    own-diff 作用域（宪法 §3）：账本未暂存=本门对账本零判读（不拦无辜提交人）；
    新增消费者扫描恒只看暂存新增行。
    """
    table = table or load_transition_table()
    findings: list[dict] = []
    staged = staged_files(repo_root)
    new_path = repo_root / registry_rel
    new_text = new_path.read_text(encoding="utf-8") if new_path.exists() else ""
    if registry_rel in staged:
        findings += _staged_registry_diff_findings(repo_root, registry_rel, new_text, table)
    dep_ids = {
        str(e.get("module_id"))
        for e in (yaml.safe_load(new_text) or {}).get("registered_ids") or []
        if isinstance(e, dict) and normalize_status(e.get("status")) == "deprecated"
    }
    findings += scan_deprecated_new_consumers(dep_ids, staged_added_lines(repo_root), registry_rel=registry_rel)
    return findings


def scan_registry_lifecycle(registry: dict, **kw: Any) -> list[dict]:
    """全账本审计（无 --staged 默认模式）：逐条目检查（转换判定属 own-diff，不在此模式）。"""
    table = kw.get("table") or load_transition_table()
    findings: list[dict] = []
    for e in registry.get("registered_ids") or []:
        findings += entry_findings(e, table)
    return findings


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(
        description="模块生命周期转换门（ORPHAN-MODULE 执行体，GOV-MOD-003 MLC-001/002/003）"
    )
    parser.add_argument("--staged", action="store_true", help="转换门模式：只校验暂存变更（own-diff 作用域）")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY_REL, help="账本路径（相对仓根）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    try:
        findings = (
            run_staged_gate(REPO_ROOT, args.registry)
            if args.staged
            else scan_registry_lifecycle(
                load_module_registry(REPO_ROOT / args.registry),
            )
        )
    except (yaml.YAMLError, OSError, ValueError) as exc:
        print(f"[MODULE-LIFECYCLE] ERROR: {exc}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    by_type: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_type[f["type"]].append(f)
    if findings:
        print(f"\n[MODULE-LIFECYCLE] {len(findings)} 个模块生命周期违规:", file=sys.stderr)
        for rtype, items in by_type.items():
            print(f"\n  {rtype} ({len(items)} 个):", file=sys.stderr)
            for f in items[:10]:
                print(f"    [{f['severity']}] {f['module_id']} ({f['where']})", file=sys.stderr)
                print(f"      {f['detail']}", file=sys.stderr)
    else:
        print("[MODULE-LIFECYCLE] 模块生命周期合规（ORPHAN-MODULE 转换门通过）", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)


if __name__ == "__main__":
    main()
