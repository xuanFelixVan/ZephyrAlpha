# [BLUEPRINT] MOD-GOVERNANCE | scripts/governance/d5_architecture/lifecycle/retire_module.py | §
# [MODULE] scripts.governance.d5_architecture.lifecycle.retire_module
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants; zephyr.shared.io.file_utils
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 默认 dry-run 零写侧；--execute 必须配 --owner-ruling（ruling_registry 校验 active）；step3-5 单 CAS 写事务；全程断点续跑状态留痕；账本唯一机器写者（本件）
# [MODIFY-GUARD] architecture_model/module_id_registry.yaml（retirement_records 节+条目级退役字段，safe_write_text CAS）
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] exit 0=完成 1=活引用中止(MLC-003 step2) 2=错误 3=门位拒绝（缺裁定/顺序缺失/批文未落地）；P1 骨架：step7 契约状态翻转暂不执行（待 Owner 增枝批文② --cascade-deprecate 立法），只登记 contracts_affected
# [TESTS] tests/governance/lifecycle/test_retire_module.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""retire_module.py — MLC-003 退役七步执行器（B10-P1 骨架；trae_032 mod_003 首个可执行真身）

对标：trae_032 mod_003 MLC-003 七步 + S9 挖矿簿 docs/_working/fms_overhaul/S9_module_retirement/README.md §4.2/§4.3。

七步（每步原子操作+台账写入+断点续跑）：
  1 确认依赖方迁移   edges 入边+consumer_registry+全仓 grep → consumers_report
  2 旧 ID 无断链     grep 命中分类：仅注释/archive/历史记载→放行；活引用→abort(exit 1)
  3 标记 deprecated  条目 status active→deprecated ┐
  4 设置 superseded_by + deprecated_reason + deprecated_date ├ 单 CAS 写事务（safe_write_text）
  5 保留 90 天       retain_until=deprecated_date+90d           ┘ + retirement_records upsert
  6 Owner 批准       --owner-ruling 在 ruling_registry 校验 active → approved_by
  7 IFC-007 级联     契约匹配→contracts_affected 登记；状态翻转待批文②（P1 只登记，REMAIN）

去向指针统一（S9 簿 §4.4，与 S5 successor_of 单值双写）：successor 身份一律用
module_id；step4 是唯一写入点，同时写 module_id_registry（条目 superseded_by+
retirement_records）与 lib_assets.successor_of（经 S5 处方 librarian 通道；
S5 DDL 未落地前=PENDING_P4 留痕，落地后自动生效）。

Owner 门位（risk_tier_registry：注册表真源条目退役=high human_gate）：
  --execute 缺 --owner-ruling → 拒跑(exit 3)；裁定不存在/status!=active → 拒跑(exit 3)。
  --dry-run（默认）零写侧，只打印将发生什么。

回收窗口：deprecated 90 天内 --rollback 可逆（同样须 --owner-ruling）。
"""

from __future__ import annotations

__manifest__ = """
args: [--module, --successor, --step, --all, --status, --rollback, --owner-ruling,
       --execute, --cascade-contracts, --registry, --ruling-registry,
       --consumer-registry, --contracts, --state-dir, --session]
description: MLC-003 退役七步执行器（默认 dry-run；真实执行须 --execute+--owner-ruling）
dimensions:
- D5
priority: P1
timeout_seconds: 120
warn_only: false
"""

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
import yaml  # noqa: E402
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402

# SQL 集中化（§5.160.2 NO-BARE-SQL）：模块级常量，禁散落
_SQL_DEPGRAPH_EDGES_FOR_MODULE = (
    "SELECT e.from_node_id AS from_node, e.to_node_id AS to_node, "
    "fn.path AS from_path, tn.path AS to_path "
    "FROM edges e JOIN nodes fn ON fn.node_id = e.from_node_id "
    "JOIN nodes tn ON tn.node_id = e.to_node_id "
    "WHERE tn.blueprint_id = %s OR tn.belongs_to = %s"
)
_SQL_MODULE_DOMAINS = "SELECT DISTINCT domain_id AS d FROM nodes WHERE blueprint_id=%s OR belongs_to=%s"

DEFAULT_REGISTRY = Path("architecture_model/module_id_registry.yaml")
DEFAULT_RULING_REGISTRY = Path("docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml")
DEFAULT_CONSUMER_REGISTRY = Path("architecture_model/contracts/consumer_registry.yaml")
DEFAULT_CONTRACTS = Path("architecture_model/contracts/cross_layer_contracts.yaml")
RETAIN_DAYS = 90
EXIT_REFUSED = 3

# step2 活引用判定：这些前缀下的非归档命中=活引用；其余（docs/注释/历史记载）=放行
LIVE_PREFIXES = ("src/", "scripts/", "config/", "data/")
ARCHIVE_MARKS = ("_archive", ".aidrafts", ".runtime")


# ---------- 端口（可注入，测试用假件） ----------


@dataclass
class Ports:
    """外部世界端口：路径+连接+写通道；测试注入假件，生产走默认构造。"""

    repo_root: Path = REPO_ROOT
    registry_path: Path = DEFAULT_REGISTRY
    ruling_registry_path: Path = DEFAULT_RULING_REGISTRY
    consumer_registry_path: Path = DEFAULT_CONSUMER_REGISTRY
    contracts_path: Path = DEFAULT_CONTRACTS
    state_dir: Path = Path(".runtime/sessions")  # 实际落 <state_dir>/<sid>/staging/retirement/
    session: str = ""
    depgraph_conn_factory: Callable[[], Any] | None = None
    lib_audit: Callable[[str, str, dict], str] | None = None  # (action, asset_id, detail) -> note
    lib_write_successor: Callable[[Any, str, str], str] | None = None  # (ports, module_id, successor) -> note
    now: Callable[[], datetime] = datetime.now  # 可注入时钟（测试冻结时间；函数默认值=不可变，安全）

    def state_file(self, module_id: str) -> Path:
        sid = self.session or "default"
        return self.state_dir / sid / "staging" / "retirement" / module_id / "state.json"


# ---------- 台账：行手术式补丁（保留原册注释，零结构重排） ----------


def find_entry_block(lines: list[str], module_id: str) -> tuple[int, int]:
    """定位 `  - module_id: <id>` 条目块 [start, end)；找不到返回 (-1, -1)。"""
    start = -1
    for i, ln in enumerate(lines):
        if ln.rstrip("\n") == f"  - module_id: {module_id}":
            start = i
            break
    if start < 0:
        return -1, -1
    end = len(lines)
    for j in range(start + 1, len(lines)):
        s = lines[j]
        if s.startswith("  - module_id: ") or (s and not s[0].isspace() and not s.startswith("#")):
            end = j
            break
    return start, end


def patch_entry_fields(text: str, module_id: str, fields: dict[str, Any], remove: list[str] | None = None) -> str:
    """条目块内写/删字段；字段已存在则原位替换（保留同行尾注释），缺失则插到块内最后一个字段行之后。"""
    lines = text.splitlines(keepends=True)
    start, end = find_entry_block(lines, module_id)
    if start < 0:
        raise KeyError(f"module_id {module_id} 不在注册表中")
    remove = remove or []
    block = lines[start:end]

    def _render(key: str, val: Any) -> str:
        if isinstance(val, str) and (":" in val or val.strip() == "" or val.startswith("#")):
            rendered = f"{key}: {json.dumps(val, ensure_ascii=False)}"
        elif val is None:
            rendered = f"{key}: null"
        elif isinstance(val, list):
            rendered = f"{key}: {json.dumps(val, ensure_ascii=False)}"
        else:
            rendered = f"{key}: {val}"
        return "    " + rendered + "\n"

    for key in remove:
        block = [ln for ln in block if not ln.startswith(f"    {key}:")]
    for key, val in fields.items():
        prefix = f"    {key}:"
        hit = False
        for idx, ln in enumerate(block):
            if ln.startswith(prefix):
                block[idx] = _render(key, val)
                hit = True
                break
        if hit:
            continue
        # 插入点：块内最后一个 4 空格缩进行之后
        insert_at = 0
        for idx, ln in enumerate(block):
            if ln.startswith("    "):
                insert_at = idx + 1
        block.insert(insert_at, _render(key, val))
    return "".join(lines[:start] + block + lines[end:])


RECORD_FIELDS = (
    "module_id",
    "ruling",
    "deprecated_date",
    "superseded_by",
    "retain_until",
    "consumers_report",
    "contracts_affected",
    "archived_date",
    "rollback_of",
)


def render_record(record: dict) -> list[str]:
    """渲染单条 retirement_records 记录（schema=S9 簿 §4.3）；字符串值一律 json 引号化保确定性。

    条目缩进钉 4 空格（字段 6 空格与 dash 后首字段对齐）——MODULE-ID-CONSISTENCY 计数
    正则恰匹配 `^  - module_id:`（2 空格），台账条目结构性避开计数口径（S4 协调假设的
    机械保障，S9 簿 §3.5）。
    """
    out = []
    for key in RECORD_FIELDS[1:]:
        val = record.get(key)
        if isinstance(val, (str, list)):
            out.append(f"      {key}: {json.dumps(val, ensure_ascii=False)}\n")
        elif val is None:
            out.append(f"      {key}: null\n")
        else:
            out.append(f"      {key}: {val}\n")
    return ["    - module_id: " + str(record["module_id"]) + "\n"] + out


def upsert_retirement_record(text: str, record: dict) -> str:
    """retirement_records 顶层节 upsert（唯一键=module_id）；节缺失则在文末创建。"""
    lines = text.splitlines(keepends=True)
    sec_start = -1
    for i, ln in enumerate(lines):
        if ln.startswith("retirement_records:"):
            sec_start = i
            break
    if sec_start >= 0 and lines[sec_start].strip() == "retirement_records: []":
        lines[sec_start] = "retirement_records:\n"  # 空列表占位归一为块列表（首条记录落账时）
    target = "    - module_id: " + str(record["module_id"]) + "\n"
    if sec_start < 0:
        block = [
            "\n",
            "# === retirement_records 退役台账（trae_032 MLC-003；载体=S9 簿 §4.3，Owner 增补令 B10-P1）===\n",
            "# 唯一键=module_id；唯一机器写者=retire_module.py（safe_write_text CAS）；\n"
            "# 独立顶层节不进 registered_ids 集合与 total_registered 口径（S4 协调假设，S9 簿 §3.5）。\n",
            "retirement_records:\n",
        ]
        block += render_record(record)
        return text.rstrip("\n") + "\n" + "".join(block)
    # 节边界：下一个 col-0 键或 EOF
    sec_end = len(lines)
    for j in range(sec_start + 1, len(lines)):
        s = lines[j]
        if s and not s[0].isspace() and not s.startswith("#"):
            sec_end = j
            break
    rec_start = -1
    for i in range(sec_start + 1, sec_end):
        if lines[i] == target:
            rec_start = i
            break
    rec_end = sec_end
    if rec_start >= 0:
        for j in range(rec_start + 1, sec_end):
            if lines[j].startswith("    - module_id: "):
                rec_end = j
                break
        return "".join(lines[:rec_start] + render_record(record) + lines[rec_end:])
    return "".join(lines[:sec_end] + render_record(record) + lines[sec_end:])


# ---------- Owner 门位 ----------


def normalize_ruling(ruling: str) -> str:
    r = (ruling or "").strip()
    if not r:
        return ""
    if r.startswith("裁定"):
        return r if "#" in r else "裁定#" + r.lstrip("裁定")
    if r.startswith("#"):
        return "裁定" + r
    return "裁定#" + r


def validate_ruling(ruling_registry_path: Path, ruling: str) -> tuple[bool, str]:
    """裁定必须登记且 status=active（Owner 门位校验桩，S9 簿 §4.2 step6）。"""
    canonical = normalize_ruling(ruling)
    if not canonical or canonical == "裁定#":
        return False, "缺裁定号"
    try:
        data = yaml.safe_load(ruling_registry_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        return False, f"ruling_registry 不可读: {exc}"
    for e in data.get("entries") or []:
        if isinstance(e, dict) and str(e.get("ruling_id", "")).strip() == canonical:
            status = str(e.get("status", ""))
            if status == "active":
                return True, canonical
            return False, f"裁定 {canonical} status={status}（须 active）"
    return False, f"裁定 {canonical} 未在 ruling_registry 登记"


# ---------- 数据采集（只读端口） ----------


def depgraph_inedges(ports: Ports, module_id: str) -> list[dict]:
    """edges 入边明细（谁依赖本模块）。"""
    factory = ports.depgraph_conn_factory
    conn = factory() if factory else None
    if conn is None:
        return []
    try:
        return [
            dict(r)
            for r in conn.execute(
                _SQL_DEPGRAPH_EDGES_FOR_MODULE,
                (module_id, module_id),
            ).fetchall()
        ]
    except Exception:  # noqa: BLE001 -- fail-open：依赖图不可达时降级为空边集，不限异常族
        return []


def repo_grep(ports: Ports, module_id: str) -> list[str]:
    """全仓 grep 旧 module_id（git grep -w 全词，防 MOD-A 误吞 MOD-ALT；无命中=空表）。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(ports.repo_root), "grep", "-I", "-l", "-w", "-e", module_id],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return sorted({ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()})


def consumer_registry_hits(ports: Ports, module_id: str) -> list[str]:
    """consumer_registry.yaml 中提及本 module_id 的契约 ID（registered_consumers 消费面）。"""
    try:
        data = yaml.safe_load(ports.consumer_registry_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return []
    hits = []
    for e in data.get("consumers") or []:
        if isinstance(e, dict) and module_id in json.dumps(e, ensure_ascii=False, default=str):
            hits.append(str(e.get("contract_id", "?")))
    return hits


def classify_hits(files: list[str]) -> tuple[list[str], list[str]]:
    """grep 命中分类：（src/scripts/config/data 下非归档）=活引用；其余=历史记载/归档放行。"""
    live, historical = [], []
    for f in files:
        norm = f.replace("\\", "/")
        if any(mark in norm for mark in ARCHIVE_MARKS):
            historical.append(norm)
        elif norm.startswith(LIVE_PREFIXES):
            live.append(norm)
        else:
            historical.append(norm)
    return live, historical


def match_contracts(ports: Ports, module_id: str, module_domains: list[str]) -> list[str]:
    """IFC-007 对象匹配：契约 source_domain ∈ 模块域，或契约全文提及 module_id/路径。"""
    try:
        data = yaml.safe_load(ports.contracts_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return []
    hits = []
    for c in data.get("contracts") or []:
        if not isinstance(c, dict):
            continue
        cid = str(c.get("id", ""))
        blob = json.dumps(c, ensure_ascii=False, default=str)
        if (str(c.get("source_domain", "")) in module_domains) or module_id in blob:
            hits.append(cid)
    return hits


# ---------- 断点续跑状态 ----------


def load_state(ports: Ports, module_id: str) -> dict:
    p = ports.state_file(module_id)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def save_state(ports: Ports, module_id: str, state: dict) -> Path:
    p = ports.state_file(module_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()[
        :16
    ]


# ---------- 七步 ----------


def step1_consumers(ports: Ports, module_id: str) -> dict:
    """step1 确认依赖方迁移：三源 consumers_report。"""
    report = {
        "depgraph_inedges": depgraph_inedges(ports, module_id),
        "consumer_registry_contracts": consumer_registry_hits(ports, module_id),
        "repo_grep_files": repo_grep(ports, module_id),
    }
    report["digest"] = digest({k: v for k, v in report.items()})
    return report


def step2_no_broken_links(report: dict) -> tuple[bool, list[str], list[str]]:
    """step2 旧 ID 无断链：活引用非空 → False（abort）。"""
    live, historical = classify_hits(report.get("repo_grep_files", []))
    return (not live), live, historical


def steps_345_mark_deprecated(
    ports: Ports,
    module_id: str,
    successor: str,
    reason: str,
    record_extra: dict,
) -> dict:
    """step3-5 同一 CAS 写事务：status/superseded_by/deprecated_reason/deprecated_date/retain_until + 台账 upsert。"""
    text = ports.registry_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    entry = next((e for e in data.get("registered_ids") or [] if e.get("module_id") == module_id), None)
    if entry is None:
        raise KeyError(f"module_id {module_id} 不在注册表中")
    today = ports.now().strftime("%Y-%m-%d")
    if str(entry.get("status")) == "deprecated":
        return {"status": "skip", "detail": "条目已 deprecated（CAS 幂等跳过）"}
    record = {
        "module_id": module_id,
        "ruling": record_extra.get("ruling"),
        "deprecated_date": today,
        "superseded_by": successor,
        "retain_until": (ports.now() + timedelta(days=RETAIN_DAYS)).strftime("%Y-%m-%d"),
        "consumers_report": record_extra.get("consumers_report"),
        "contracts_affected": record_extra.get("contracts_affected", []),
        "archived_date": None,
        "rollback_of": None,
    }
    new_text = patch_entry_fields(
        text,
        module_id,
        {
            "status": "deprecated",
            "superseded_by": successor,
            "deprecated_reason": reason,
            "deprecated_date": today,
            "retain_until": record["retain_until"],
        },
    )
    new_text = upsert_retirement_record(new_text, record)
    result = safe_write_text(
        ports.registry_path,
        new_text,
        expected_base_sha256=content_sha256(text),
        repo_root=ports.repo_root,
    )
    if not getattr(result, "written", False):
        return {"status": "error", "detail": f"CAS 写失败: {result}"}
    return {
        "status": "done",
        "record": record,
        "detail": f"step3-5 单事务落账（retain_until={record['retain_until']}）",
    }


def step6_owner_approval(ports: Ports, ruling: str) -> dict:
    ok, detail = validate_ruling(ports.ruling_registry_path, ruling)
    return {"status": "done" if ok else "refused", "ruling": normalize_ruling(ruling), "detail": detail}


def step7_contract_cascade(ports: Ports, module_id: str, module_domains: list[str]) -> dict:
    """step7 IFC-007：P1 只登记命中契约；状态翻转待 Owner 增枝批文②（trae_032 --cascade-deprecate 立法）。"""
    hits = match_contracts(ports, module_id, module_domains)
    if not hits:
        return {"status": "done", "detail": "无命中契约=N/A 完成", "contracts_affected": []}
    return {
        "status": "remain",
        "detail": "命中契约已登记 contracts_affected；契约状态翻转须 Owner 增枝批文②（--cascade-deprecate 立法）后启用",
        "contracts_affected": hits,
    }


def _default_lib_audit(action: str, asset_id: str, detail: dict) -> str:
    """lib_events 追加留痕（S9 簿 §4.2）；图书馆不可用时留痕降级为 deferred。"""
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))
        from _shared.constants import get_depgraph_pg_connection  # noqa: PLC0415

        from zephyr.library.librarian import Librarian  # noqa: PLC0415

        conn = get_depgraph_pg_connection(read_only=False)
        librarian = Librarian(conn)
        event_id = librarian.act("audit", asset_id=asset_id, actor="retire_module", detail=detail)
        return f"lib_events#{event_id}"
    except Exception as exc:  # noqa: BLE001  留痕通道故障不阻断主流程，但必须显式留名
        return f"deferred: {type(exc).__name__}: {exc}"


def successor_of_payload(module_id: str, successor: str) -> dict:
    """S5 单值双写接口（S9 簿 §4.4）：successor 身份一律 module_id。

    step4 唯一写入点消费本 payload：同时写 module_id_registry（条目 superseded_by+
    retirement_records）与 lib_assets.successor_of（S5 librarian delete 分支透传；
    S5 DDL 落地前=PENDING_P4，落地后同 payload 直接生效）。禁两处手工各自写。
    """
    return {"successor_of": successor, "asset_id": module_id, "vocab": "module_id"}


def write_library_successor_of(ports: Ports, module_id: str, successor: str) -> str:
    """lib_assets.successor_of 双写（S5 DDL 未落地=显式 PENDING_P4 留痕，不静默）。"""
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))
        from _shared.constants import get_depgraph_pg_connection  # noqa: PLC0415

        from zephyr.library.librarian import Librarian  # noqa: PLC0415

        conn = get_depgraph_pg_connection(read_only=False)
        payload = successor_of_payload(module_id, successor)
        librarian = Librarian(conn)
        librarian.act(
            "update",
            asset_id=payload["asset_id"],
            actor="retire_module",
            fields={"successor_of": payload["successor_of"]},
        )
        return "written"
    except Exception as exc:  # noqa: BLE001
        return f"PENDING_P4: {type(exc).__name__}"


# ---------- 编排 ----------


def _run_step1(ports: Ports, module_id: str, execute: bool, state: dict) -> tuple[dict, int]:
    """step1 确认依赖方迁移（resume 比对：execute 且报告变化→exit 4 请复跑 --all）。"""
    report = step1_consumers(ports, module_id)
    if execute and state.get("steps", {}).get("1", {}).get("report_digest") not in (None, report["digest"]):
        return ({"status": "changed", "detail": "step1 报告与上次不同（resume 比对），请复跑 --all"}, EXIT_FINDINGS)
    return ({"status": "done", "consumers_report": report}, EXIT_PASS)


def _run_step2(ports: Ports, module_id: str, state: dict) -> tuple[dict, int]:
    """step2 旧 ID 无断链（复用 step1 落账报告，缺则现采）。"""
    report = state.get("steps", {}).get("1", {}).get("consumers_report") or step1_consumers(ports, module_id)
    ok, live, historical = step2_no_broken_links(report)
    detail = f"活引用={live}；历史记载放行={len(historical)} 处"
    return (
        {"status": "done" if ok else "abort", "live": live, "historical": historical, "detail": detail},
        EXIT_PASS if ok else EXIT_FINDINGS,
    )


def _run_step345(
    ports: Ports, module_id: str, successor: str, reason: str, execute: bool, ruling: str
) -> tuple[dict, int]:
    """step3-5（execute=单 CAS 写事务+图书馆双写/留痕；dry-run=零写侧预告）。"""
    if execute:
        record_extra = {
            "ruling": normalize_ruling(ruling) if ruling else None,
            "consumers_report": str(ports.state_file(module_id).parent / "consumers_report.json"),
        }
        res = steps_345_mark_deprecated(ports, module_id, successor, reason, record_extra)
        if res["status"] == "done":
            res["successor_of"] = (ports.lib_write_successor or write_library_successor_of)(ports, module_id, successor)
            res["lib_audit"] = (ports.lib_audit or _default_lib_audit)(
                "audit", module_id, {"step": "3-5", "module_id": module_id, "successor": successor}
            )
        return (res, EXIT_PASS if res["status"] in ("done", "skip") else EXIT_ERROR)
    return (
        {
            "status": "dry-run",
            "detail": "将单 CAS 写：status→deprecated + superseded_by/"
            "deprecated_reason/deprecated_date/retain_until + retirement_records upsert",
        },
        EXIT_PASS,
    )


def _run_step6(ports: Ports, ruling: str, execute: bool) -> tuple[dict, int]:
    """step6 Owner 门位（dry-run=校验预告；execute=校验不过 exit 3）。"""
    if not execute:
        ok, detail = validate_ruling(ports.ruling_registry_path, ruling) if ruling else (False, "缺裁定号")
        return (
            {
                "status": "dry-run",
                "detail": f"Owner 门位校验预告：{detail}" + ("" if ok else "（--execute 时将硬拒 exit 3）"),
            },
            EXIT_PASS,
        )
    res = step6_owner_approval(ports, ruling)
    return (res, EXIT_PASS if res["status"] == "done" else EXIT_REFUSED)


def _step7_domains(ports: Ports, module_id: str) -> list[str]:
    """step7 前置：depgraph 域归属（连接不可用/查询失败=空域，保守不炸）。"""
    domains: list[str] = []
    conn = ports.depgraph_conn_factory() if ports.depgraph_conn_factory else None
    if conn is not None:
        try:
            rows = conn.execute(_SQL_MODULE_DOMAINS, (module_id, module_id)).fetchall()
            domains = [r["d"] for r in rows if r["d"]]
        except Exception:  # noqa: BLE001  域查询失败按无域处理（与原实现行为一致）
            domains = []
    return domains


def _persist_contracts_affected(ports: Ports, module_id: str, res: dict) -> None:
    """台账二次落账：contracts_affected 写回 retirement_records（step7 独立 CAS 写事务）。

    写失败不吞——显式进 res["detail"]（行为与原 run_step 内联块一致）。
    """
    try:
        text = ports.registry_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        existing = next((r for r in data.get("retirement_records") or [] if r.get("module_id") == module_id), None)
        if existing is not None:
            rec = {
                **{k: existing.get(k) for k in RECORD_FIELDS},
                "module_id": module_id,
                "contracts_affected": res["contracts_affected"],
            }
            new_text = upsert_retirement_record(text, rec)
            result = safe_write_text(
                ports.registry_path, new_text, expected_base_sha256=content_sha256(text), repo_root=ports.repo_root
            )
            if getattr(result, "written", False):
                res["detail"] += "；contracts_affected 已落台账"
            else:
                res["detail"] += f"；台账 CAS 写失败: {result}"
    except Exception as exc:  # noqa: BLE001  台账写失败不吞——显式进 detail
        res["detail"] += f"；台账写异常: {type(exc).__name__}: {exc}"


def _run_step7(ports: Ports, module_id: str, execute: bool) -> tuple[dict, int]:
    """step7 IFC-007：契约命中登记；execute 且有命中→台账二次落账。"""
    domains = _step7_domains(ports, module_id)
    res = step7_contract_cascade(ports, module_id, domains)
    if execute and res.get("contracts_affected"):
        _persist_contracts_affected(ports, module_id, res)
    return (res, EXIT_PASS)


@dataclass
class _StepContext:
    """单步/顺序执行上下文（NO-LONG-PARAM-LIST 治理件：run_step 8 参→3 参、_run_steps 9 参→2 参，CLI 行为零变化）。"""

    module_id: str
    successor: str = ""
    reason: str = ""
    steps: list[int] = field(default_factory=list)
    execute: bool = False
    ruling: str = ""
    state: dict = field(default_factory=dict)
    is_all: bool = False


def run_step(ports: Ports, ctx: _StepContext, n: int) -> tuple[dict, int]:
    """执行单步；返回 (step_result, exit_code)。断点续跑：前置步未 done → 拒绝(exit 3)。"""
    module_id, execute, state = ctx.module_id, ctx.execute, ctx.state
    for prev in range(1, n):
        if state.get("steps", {}).get(str(prev), {}).get("status") not in ("done", "skip"):
            return (
                {"status": "refused", "detail": f"断点续跑校验失败：step{prev} 未完成，禁越序执行 step{n}"},
                EXIT_REFUSED,
            )
    if n == 1:
        return _run_step1(ports, module_id, execute, state)
    if n == 2:
        return _run_step2(ports, module_id, state)
    if n in (3, 4, 5):
        return _run_step345(ports, module_id, ctx.successor, ctx.reason, execute, ctx.ruling)
    if n == 6:
        return _run_step6(ports, ctx.ruling, execute)
    if n == 7:
        return _run_step7(ports, module_id, execute)
    return ({"status": "error", "detail": f"未知 step {n}（合法 1-7）"}, EXIT_ERROR)


def rollback(ports: Ports, module_id: str, ruling: str, execute: bool) -> tuple[dict, int]:
    """回收窗口回退：deprecated→active（须 Owner 裁定锚定；窗口外拒）。"""
    ok, detail = validate_ruling(ports.ruling_registry_path, ruling)
    if not ok:
        return ({"status": "refused", "detail": f"rollback 门位拒绝：{detail}"}, EXIT_REFUSED)
    text = ports.registry_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    entry = next((e for e in data.get("registered_ids") or [] if e.get("module_id") == module_id), None)
    if entry is None or str(entry.get("status")) != "deprecated":
        return ({"status": "refused", "detail": "条目非 deprecated，无可回退"}, EXIT_REFUSED)
    dep_date = str(entry.get("deprecated_date") or "")
    try:
        window_end = datetime.strptime(dep_date, "%Y-%m-%d") + timedelta(days=RETAIN_DAYS)
        if ports.now() > window_end:
            return (
                {"status": "refused", "detail": f"回收窗口已过（retain_until={window_end:%Y-%m-%d}）"},
                EXIT_REFUSED,
            )
    except ValueError:
        pass
    if not execute:
        return (
            {
                "status": "dry-run",
                "detail": "将回退 status→active 并清条目级退役字段（retirement_records 记 rollback_of）",
            },
            EXIT_PASS,
        )
    prev_key = f"{module_id}:{dep_date}"
    existing = data.get("retirement_records") or []
    rec = next((r for r in existing if r.get("module_id") == module_id), {})
    new_text = patch_entry_fields(
        text,
        module_id,
        {"status": "active"},
        remove=["superseded_by", "deprecated_reason", "deprecated_date", "retain_until"],
    )
    if rec:
        rec = {**{k: rec.get(k) for k in RECORD_FIELDS}, "module_id": module_id, "rollback_of": prev_key}
        new_text = upsert_retirement_record(new_text, rec)
    result = safe_write_text(
        ports.registry_path,
        new_text,
        expected_base_sha256=content_sha256(text),
        repo_root=ports.repo_root,
    )
    if not getattr(result, "written", False):
        return ({"status": "error", "detail": f"CAS 写失败: {result}"}, EXIT_ERROR)
    return ({"status": "done", "detail": f"已回退 active（rollback_of={prev_key}）"}, EXIT_PASS)


# ---------- CLI ----------


def _build_ports(args: argparse.Namespace) -> Ports:
    """CLI 参数 → Ports（相对路径锚 REPO_ROOT；repo-root 覆盖供测试隔离）。"""

    def _abs(p: str) -> Path:
        pp = Path(p)
        return pp if pp.is_absolute() else REPO_ROOT / pp

    return Ports(
        repo_root=Path(args.repo_root) if args.repo_root else REPO_ROOT,
        registry_path=_abs(args.registry),
        ruling_registry_path=_abs(args.ruling_registry),
        consumer_registry_path=_abs(args.consumer_registry),
        contracts_path=_abs(args.contracts),
        state_dir=Path(args.state_dir) if Path(args.state_dir).is_absolute() else REPO_ROOT / args.state_dir,
        session=args.session,
        depgraph_conn_factory=_depgraph_factory,
    )


def _enforce_execute_gate(ports: Ports, ruling: str) -> bool:
    """--execute Owner 门位（risk_tier=high）：缺裁定/裁定无效 → 打印 REFUSED 返回 False。"""
    if not ruling:
        print("REFUSED: --execute 必须配 --owner-ruling（Owner 门位，risk_tier=high）", file=sys.stderr)
        return False
    ok, detail = validate_ruling(ports.ruling_registry_path, ruling)
    if not ok:
        print(f"REFUSED: {detail}", file=sys.stderr)
        return False
    return True


def _record_step_state(ports: Ports, state: dict, module_id: str, n: int, res: dict, execute: bool) -> None:
    """断点推进：execute=持久化到状态文件；dry-run=仅会话内推进（预演 --all 顺序）。"""
    rec: dict = {"at": ports.now().isoformat(timespec="seconds")}
    if n == 1:
        if res.get("consumers_report"):
            rec.update(
                status="done", consumers_report=res["consumers_report"], report_digest=res["consumers_report"]["digest"]
            )
        else:
            rec = None
    else:
        rec["status"] = res.get("status") if execute else "done"
        if n != 1 and res.get("detail"):
            rec["detail"] = str(res.get("detail"))
    if rec is not None:
        state.setdefault("steps", {})[str(n)] = rec
        if n == 7 and res.get("contracts_affected") is not None:
            state["contracts_affected"] = res["contracts_affected"]
        if execute:
            save_state(ports, module_id, state)


def _run_steps(ports: Ports, ctx: _StepContext) -> int:
    """顺序执行 steps，返回最终退出码；--all 中 FINDINGS/REFUSED 即中止。"""
    final = EXIT_PASS
    for n in ctx.steps:
        if not ctx.execute and n in (3, 4, 5, 6):
            print(f"[DRY-RUN] step{n}: ", end="")
        res, code = run_step(ports, ctx, n)
        print(f"step{n}: {json.dumps(res, ensure_ascii=False, default=str)}")
        if code == EXIT_PASS:
            _record_step_state(ports, ctx.state, ctx.module_id, n, res, ctx.execute)
        if code != EXIT_PASS:
            final = code
            if ctx.is_all and code in (EXIT_FINDINGS, EXIT_REFUSED):
                print(f"[ABORT] step{n} 中止 --all（exit={code}）")
                break
    return final


def _print_done_banner(module_id: str, successor: str, ruling: str, execute: bool, is_all: bool, final: int) -> None:
    """七步全成收尾横幅（仅 --execute --all 全 PASS 时打印）。"""
    if execute and final == EXIT_PASS and is_all:
        print(
            f"[DONE] MLC-003 七步完成：{module_id} → deprecated（successor={successor}，"
            f"retain 90 天，ruling={normalize_ruling(ruling)}）"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MLC-003 退役七步执行器（默认 dry-run）")
    parser.add_argument("--module", required=True, help="目标 module_id")
    parser.add_argument("--successor", default="", help="替代模块 module_id（step4 superseded_by；统一词汇=module_id）")
    parser.add_argument("--step", type=int, default=0, help="执行单步 1-7（断点续跑）")
    parser.add_argument("--all", action="store_true", help="顺序执行 1-7")
    parser.add_argument("--status", action="store_true", help="查看断点状态")
    parser.add_argument("--rollback", action="store_true", help="回收窗口回退 deprecated→active（须裁定）")
    parser.add_argument("--owner-ruling", default="", help="Owner 裁定号（--execute 必配）")
    parser.add_argument("--execute", action="store_true", help="真实执行（缺省=dry-run 零写侧）")
    parser.add_argument("--cascade-contracts", action="store_true", help="[P1 恒拒] 契约级联翻转（待 Owner 增枝批文②）")
    parser.add_argument("--reason", default="", help="deprecated_reason（缺省自动生成）")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--ruling-registry", default=str(DEFAULT_RULING_REGISTRY))
    parser.add_argument("--consumer-registry", default=str(DEFAULT_CONSUMER_REGISTRY))
    parser.add_argument("--contracts", default=str(DEFAULT_CONTRACTS))
    parser.add_argument("--state-dir", default=".runtime/sessions")
    parser.add_argument("--session", default="")
    parser.add_argument("--repo-root", default="", help="仓根覆盖（测试隔离用；缺省=真实仓根）")
    args = parser.parse_args(argv)

    ports = _build_ports(args)
    module_id = args.module
    successor = args.successor
    ruling = args.owner_ruling

    if args.cascade_contracts:
        print(
            "REFUSED: step7 契约级联翻转须 Owner 增枝批文②（trae_032 修正批 --cascade-deprecate 立法）落地后启用；"
            "P1 只登记 contracts_affected",
            file=sys.stderr,
        )
        return EXIT_REFUSED

    state = load_state(ports, module_id)
    if args.status:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return EXIT_PASS

    if args.rollback:
        res, code = rollback(ports, module_id, ruling, args.execute)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return code

    if not args.all and args.step == 0:
        parser.error("需要 --step N / --all / --status / --rollback 之一")

    if args.execute and not _enforce_execute_gate(ports, ruling):
        return EXIT_REFUSED
    execute = args.execute

    reason = args.reason or f"MLC-003 退役（successor={successor or 'N/A'}）"
    steps = list(range(1, 8)) if args.all else [args.step]
    if args.all and not successor:
        print("REFUSED: --all 需要 --successor（step4 superseded_by 必填）", file=sys.stderr)
        return EXIT_REFUSED

    ctx = _StepContext(
        module_id=module_id,
        successor=successor,
        reason=reason,
        steps=steps,
        execute=execute,
        ruling=ruling,
        state=state,
        is_all=args.all,
    )
    final = _run_steps(ports, ctx)
    _print_done_banner(module_id, successor, ruling, execute, args.all, final)
    return final


def _depgraph_factory() -> Any:
    try:
        from _shared.constants import get_depgraph_pg_connection  # noqa: PLC0415

        return get_depgraph_pg_connection(read_only=True)
    except Exception:  # noqa: BLE001 -- fail-open 工厂：连接源不可用返回 None 由调用方降级，不限异常族
        return None


if __name__ == "__main__":
    sys.exit(main())
