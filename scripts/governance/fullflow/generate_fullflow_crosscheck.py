# [BLUEPRINT] MOD-GOV_SCRIPTS
# [MODULE] scripts.governance.fullflow.generate_fullflow_crosscheck
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.fullflow.__init__
# [CONSUMERS] tests/governance/fullflow/test_fullflow_crosscheck_generator.py；docs/_working/fullflow_mining/00_skeleton/91_machine_crosscheck.yaml
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] render 幂等无时间戳 | claimed!=measured 必入 drift_flags | 实测面不可读必标 unavailable 且 measured=null | 作业簿集合只取 HEAD 跟踪集（未落地件不记功） | F 号合法性以总册为准（不认即必报漂移）
# [MODIFY-GUARD] 改判据口径/阈值须同步改配对测试（含"能红"族）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源文件缺失 -> 内部 ReadFailure 抛出后被采集层捕获转 status=unavailable +
#                  measured=null（绝不填估计值、绝不静默算绿）；无 .git / git 不可跑 /
#                  toplevel≠本仓根 -> HeadTracking(status="unavailable", reason=...)（不抛异常）；
#                  退出码：0=正常产出或 --stdout；--check 下生成物缺失或与再生成字节不一致 -> 1（STALE）；
#                  写盘 IO 异常不上抛包装，直接外溢（产物写失败不得装作成功）
# [TESTS] tests/governance/fullflow/test_fullflow_crosscheck_generator.py
# [TTL] permanent
"""全流通五向对账生成器（机生，宪法 §9.5"静态清单禁手工维护"的落地尺）。

一句话：把"散文里声称的数"和"实测的数"放在同一张 YAML 里对撞，
任一处不一致就标 ``drift: true``，不静默。

产出面（一份 YAML）：
1. 五向计数：F 环节 / TDM 节点 / 策略工厂 FAC 节点 / ROOR 注册表 / 挖矿簿册（HEAD 落地面）；
2. 逐段挖矿覆盖矩阵：F01-F1xx 每个环节 → 有没有**已落地**作业簿**显式认领**它（缺口地图）；
3. 漂移标志位：散文声称数 != 实测数 → 该条 drift true；取不到数 → status unavailable（报红，不填估计值）。

纪律：
- 幂等：禁 datetime.now()/time.time()（RULE-SCHEMA-TZ），输出全排序；git 子进程一律带
  ``-c core.quotePath=false``（否则非 ASCII 路径被八进制引号包裹，同一棵树产出两种 YAML）；
- 只读：本生成器不写任何真源册，只写自己的 YAML 产物；
- 落地面口径：作业簿**集合**取自 ``git ls-tree -r --name-only HEAD``；工作树未落地件不进
  真源记录（他道 WIP 被丢弃后不会留下悬空"证据"＝假绿持久化＋连坐）；
- 无本仓 `.git`／toplevel≠本仓根／git 不可跑 ⇒ 该向 ``unavailable`` 且**不算绿**，
  绝不静默上溯外层仓库把"没落地"报成 ok；
- 自述与实现同源：口径串（``definition.covered`` 与各 ``method``）由实现导出，
  读者按串复算必须得到同一套数。
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# create-guard-not-dup: 本件是全流通五向对账 YAML 生成器（读真源+git 实测对撞计数），非 LLM 运行时拦截器/import 副作用门/stale-base 规则的第二实现，命中词 read text=通用语料噪声

# ---------------------------------------------------------------- 真源路径
MINING_ROOT_REL = "docs/_working/fullflow_mining"
TOTAL_BOOK_REL = f"{MINING_ROOT_REL}/00_skeleton/00_全环节总册.md"
TDM_REL = "config/trading_decision_map.yaml"
SPM_REL = "config/strategy_production_map.yaml"
ROOR_REL = "docs/registry_of_registries.yaml"
FUNCTIONAL_DOMAIN_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"
WAVE1_COMMAND_BOOK_REL = f"{MINING_ROOT_REL}/91_chief_command_wave1.md"
OUTPUT_REL = f"{TOTAL_BOOK_REL.replace('00_全环节总册.md', '')}91_machine_crosscheck.yaml"
SRC_ZEPHYR_REL = "src/zephyr"

GENERATED_BY = "scripts/governance/fullflow/generate_fullflow_crosscheck.py"

# 任务书要求的五向（其余为附带观测面）
FIVE_WAY_KEYS = (
    "f_links",
    "tdm_nodes",
    "factory_nodes",
    "roor_registries",
    "mining_books",
)

# 覆盖矩阵的"非作业簿"排除面：总册=编号真源自指、分工册/指挥册/裁定册=编排面非作业面、
# 交叉验证册=候选漏项面（它列 F 编号是"指认缺口"不是"已挖"）。
# ⚠手工清单自 2026-09-26 起受本尺**自守校验**：每条路径必须在 HEAD 跟踪集里存在，
# 孤儿条目（盘上/HEAD 均无此件）当场进 ``drift_flags``（红队实测清单里就躺着一本不存在的册）。
NON_WORKBOOK_RELS: tuple[str, ...] = (
    "00_skeleton/00_全环节总册.md",
    "00_skeleton/00_挖矿分工册.md",
    "00_skeleton/90_crosscheck_link_census.md",
    "00_skeleton/91_machine_crosscheck.yaml",
    "00_orchestration.md",
    "90_chief_rulings_wave1.md",
    "91_chief_command_wave1.md",
    "92_chief_command_wave2.md",
    "05_missing_p0/91_machine_crosscheck_notes.md",
    # 取证页＝为"环节终数该怎么定"摆证据的分析面（同 90_crosscheck 类）。它只**点名**缺口，
    # 旧口径"提到即算"会把 F107 这类号当场洗白（2026-09-26 实测 uncovered 6→5）。
    # 现认领面已改**显式声明制**（见 ``_claim_tokens``），本清单只留"编排/分析面整册不进矩阵"的语义。
    "05_missing_p0/04_p1p3p5_evidence_pages.md",
    # 分诊册=按设计枚举全部缺口的分析面（与 90_crosscheck_link_census 同类）。
    "00_skeleton/92_coverage_triage_20260926.md",
)

# 认领面（三处，全部收紧自 2026-09-26 红队 RB-1 案卷）：
# ①文件名 ``fnn``；②行首**严格式**声明行（行尾不得再有任何散文）；③frontmatter ``covers:`` 且必须是 YAML 列表。
# 已删通道：行首 ``#`` 标题（红队实测一行塞 20 个号即可把 uncovered 45→25）、正文/注释 grep。
COVER_LINE_RE = re.compile(r"^本册覆盖(?:\s*F\d{2,3})(?:\s*[/、,]\s*F\d{2,3})*$")
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)(?:\r?\n)?---[ \t]*(?:\r?\n|\Z)", re.S)
# 候选号提取：**不贪婪切片**——整串数字一起吃（只禁"后面还有数字"），位数不合法即"非法号"而非"截成合法号"。
# 小写 f（文件名面另计）、``F 123``、``F-999``（红队案卷的零污染写法）都不成为 token，也不报漂移。
F_TOKEN_CAND_RE = re.compile(r"(?<![A-Za-z0-9_])F(\d{1,9})(?![0-9])")
F_NAME_CAND_RE = re.compile(r"(?<![a-z0-9])f(\d{1,9})(?![0-9])")
F_ID_RE = re.compile(r"F\d{2,3}")
F_ROW_RE = re.compile(r"^\|\s*(F\d{2,3})\s*\|")
SEGMENT_RE = re.compile(r"^### ([A-Z]) 段")
CLAIM_SURFACE_DESC = (
    "作业簿**显式认领**（三处，缺一不可仅此三处）：①文件名 ``fnn``（``f`` 紧接 2-3 位数字且前后非字母数字）"
    "②行首严格式声明行 ``^本册覆盖(?:\\s*F\\d{2,3})(?:\\s*[/、,]\\s*F\\d{2,3})*$``"
    "（整行只允许号与分隔符，行尾散文即不匹配——反讽/指认句不记功）"
    "③frontmatter ``covers:`` 且**必须是 YAML 列表**（空格分隔字符串按解析失败处理，不记功）。"
    "不认：正文/HTML 注释/标题行/任意散文位。"
    "号合法性以总册为准：只对总册实际存在的 ``F01..FNN`` 记功，"
    "其余（4 位以上溢出号、1 位号、不在总册的号）不记功并进 ``drift_flags``。"
)


# ---------------------------------------------------------------- 数据结构
@dataclass
class Metric:
    """一个计数面：实测值 + 取数口径 + 不可用语义。"""

    key: str
    label: str
    measured: int | None = None
    method: str = ""
    sources: tuple[str, ...] = ()
    status: str = "ok"  # ok | unavailable
    detail: dict[str, Any] = field(default_factory=dict)
    unavailable_reason: str = ""

    def unavailable(self, reason: str) -> None:
        self.status = "unavailable"
        self.measured = None
        self.unavailable_reason = reason

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "label": self.label,
            "status": self.status,
            "measured": self.measured,
            "method": self.method,
            "source_files": list(self.sources),
        }
        if self.detail:
            out["detail"] = self.detail
        if self.status != "ok":
            out["unavailable_reason"] = self.unavailable_reason
        return out


@dataclass
class Probe:
    """散文声称数探针：在指定文件的指定正则里抓一个数字当作"声称值"。"""

    metric: str
    file_rel: str
    pattern: str
    group: int = 1
    note: str = ""


class ReadFailure(Exception):
    """真源读不到——必须报红，绝不用估计值填数。"""


# ---------------------------------------------------------------- 读取工具
def _read_text(root: Path, rel: str) -> str:
    path = root / rel
    if not path.is_file():
        raise ReadFailure(f"missing file: {rel}")
    return path.read_text(encoding="utf-8", errors="replace")


def _count_lines(matching: list[str]) -> int:
    return len(matching)


# ---------------------------------------------------------------- 五向计数
def measure_f_links(root: Path) -> tuple[Metric, dict[str, list[str]]]:
    """解析总册表格：F 编号行 = 环节；### X 段 = 分段。"""
    text = _read_text(root, TOTAL_BOOK_REL)
    lines = text.splitlines()
    ids: list[str] = []
    seen: set[str] = set()
    duplicates: list[str] = []
    row_count = 0
    segments: dict[str, list[str]] = {}
    current = "UNSEGMENTED"
    for line in lines:
        seg = SEGMENT_RE.match(line)
        if seg:
            current = seg.group(1)
            segments.setdefault(current, [])
            continue
        row = F_ROW_RE.match(line)
        if row:
            row_count += 1
            fid = row.group(1)
            if fid in seen:
                duplicates.append(fid)
            else:
                seen.add(fid)
                ids.append(fid)
            segments.setdefault(current, [])
            if fid not in segments[current]:
                segments[current].append(fid)
    numbering = check_f_numbering(ids)
    metric = Metric(
        key="f_links",
        label="全流通环节数（F 编号）",
        measured=len(ids),
        method="grep -E '^\\|\\s*(F[0-9]{2,3})\\s*\\|' 逐行计数（去重）；分段按 '^### [A-Z] 段' 归属",
        sources=(TOTAL_BOOK_REL,),
        detail={
            "unique_ids": len(ids),
            "row_count": row_count,
            "duplicate_ids": sorted(set(duplicates)),
            "segment_count": len([s for s in segments if s != "UNSEGMENTED"]),
            "per_segment": {k: len(v) for k, v in sorted(segments.items())},
            **numbering,
        },
    )
    if not ids:
        metric.unavailable("no F rows parsed from total book")
    return metric, segments


def check_f_numbering(ids: list[str]) -> dict[str, Any]:
    """总册编号不变式（红队实测：往总册塞 `F999` 行把 f_links 顶到 123 而零告警）。

    号合法性以总册为准 ⇒ 总册自身必须有可机械判定的形状：**F01..FNN 连续**，
    断号／跳段（含被塞进来的越界号）一律进 ``drift_flags``。只报事实，不改任何数值判据。
    """
    if not ids:
        return {}
    nums = sorted({int(i[1:]) for i in ids})
    missing = [n for n in range(nums[0], nums[-1] + 1) if n not in set(nums)]
    return {
        "min_number": nums[0],
        "max_number": nums[-1],
        "missing_numbers": [f"F{n:02d}" if n < 100 else f"F{n}" for n in missing],
        "contiguous_from_min": nums[0] == 1,
    }


def numbering_anomalies(ids: list[str]) -> list[dict[str, Any]]:
    numbering = check_f_numbering(ids)
    out: list[dict[str, Any]] = []
    missing = numbering.get("missing_numbers") or []
    if missing:
        out.append(
            {
                "kind": "f_id_noncontiguous",
                "metric": "f_links",
                "claimed": None,
                "measured": None,
                "file": TOTAL_BOOK_REL,
                "line": 0,
                "note": f"总册号段断裂/越界：缺 {len(missing)} 号 {missing[:20]}",
                "missing_numbers": missing,
            }
        )
    if not numbering.get("contiguous_from_min", True):
        out.append(
            {
                "kind": "f_id_not_started_at_F01",
                "metric": "f_links",
                "claimed": None,
                "measured": None,
                "file": TOTAL_BOOK_REL,
                "line": 0,
                "note": f"总册首号不是 F01（实为 F{numbering.get('min_number')}）",
            }
        )
    return out


# ---------------------------------------------------------------- git 归属与 HEAD 跟踪集
def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    """git 子进程：**一律带 `-c core.quotePath=false`**。

    红队实测默认引号路径下 33 本非 ASCII 册从 HEAD 面整行消失（120 vs 真值 153）
    ⇒ 同一棵树在不同 git 配置下产出不同 YAML＝确定性破口。
    """
    cmd = ["git", "-c", "core.quotePath=false", "-C", str(root), *args]
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return None


@dataclass
class HeadTracking:
    """HEAD 跟踪集（落地面）。取不到本仓 HEAD ⇒ ``unavailable``，**不得算绿**。"""

    status: str = "ok"  # ok | unavailable
    reason: str = ""
    files: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def resolve_head_tracking(root: Path) -> HeadTracking:
    """本仓 HEAD 跟踪集；**没有 `.git` 时绝不静默上溯外层仓库**。

    红队实测：无 `.git` 的目录会去读外层仓 HEAD，把 `head_count=0` 标成 `status: ok`
    ——把"没落地"报成"全没落地"却算绿。此处三重前置：根下有 `.git`（目录或 worktree 文件）、
    `rev-parse --show-toplevel` 可取、且 toplevel == 本仓根。任一不满足 ⇒ unavailable。
    """
    if not (root / ".git").exists():
        return HeadTracking(status="unavailable", reason=f"no .git at repo root: {root}")
    top = _run_git(root, "rev-parse", "--show-toplevel")
    if top is None:
        return HeadTracking(status="unavailable", reason="git not runnable (not in PATH or subprocess error)")
    if top.returncode != 0:
        return HeadTracking(
            status="unavailable", reason=f"git rev-parse failed rc={top.returncode}: {top.stderr.strip()[:160]}"
        )
    toplevel = os.path.normcase(os.path.realpath(top.stdout.strip()))
    if toplevel != os.path.normcase(os.path.realpath(str(root))):
        return HeadTracking(
            status="unavailable",
            reason=f"git toplevel {toplevel} != repo root {root}（拒绝读外层仓库）",
        )
    proc = _run_git(root, "ls-tree", "-r", "--name-only", "HEAD")
    if proc is None:
        return HeadTracking(status="unavailable", reason="git ls-tree not runnable")
    if proc.returncode != 0:
        return HeadTracking(
            status="unavailable", reason=f"git ls-tree HEAD failed rc={proc.returncode}: {proc.stderr.strip()[:160]}"
        )
    files = tuple(sorted(ln.strip() for ln in proc.stdout.splitlines() if ln.strip()))
    return HeadTracking(status="ok", files=files)


def measure_tdm(root: Path) -> Metric:
    text = _read_text(root, TDM_REL)
    lines = text.splitlines()
    nodes = [ln for ln in lines if re.match(r"^\s*-\s*node_id:", ln)]
    raw_flows: dict[str, int] = {}
    for ln in lines:
        m = re.match(r"^\s*flow:\s*([a-z_]+)\s*$", ln)
        if m:
            raw_flows[m.group(1)] = raw_flows.get(m.group(1), 0) + 1
    # 口径归一：TDM 实际取值是 entry_flow/position_flow/...，总册散文写 entry/position/...
    flows: dict[str, int] = {}
    for name, value in raw_flows.items():
        flows[_normalise_flow(name)] = value
    metric = Metric(
        key="tdm_nodes",
        label="TDM 消费端节点数",
        measured=_count_lines(nodes),
        method="grep -c '^\\s*-\\s*node_id:'（等价 grep -c -- '- node_id'）；flow 分布按 '^\\s*flow: <x>$' 并去 '_flow' 后缀归一",
        sources=(TDM_REL,),
        detail={
            "flow_distribution": dict(sorted(flows.items())),
            "flow_distribution_raw_keys": dict(sorted(raw_flows.items())),
            "flow_total": sum(flows.values()),
        },
    )
    if not nodes:
        metric.unavailable("no '- node_id' lines parsed")
    return metric


def _normalise_flow(name: str) -> str:
    return re.sub(r"_flow$", "", name)


def measure_factory(root: Path) -> Metric:
    text = _read_text(root, SPM_REL)
    lines = text.splitlines()
    raw_lines = [m.group(1) for m in (re.search(r"node_id:\s*(FAC-[A-Za-z0-9_-]+)", ln) for ln in lines) if m]
    fac_ids = sorted(set(raw_lines))
    null_nodes = sorted({node_id for node_id, is_null in _walk_node_module_refs(lines, "FAC-") if is_null})
    metric = Metric(
        key="factory_nodes",
        label="策略工厂节点数（FAC-）",
        measured=len(fac_ids),
        # 自述与实现一致：实现是**去重**，与 `grep -c 'node_id: FAC-'` 仅在无重复行时等价
        # （红队 followup P3 实测该背离点：追加一行重复 FAC 号 ⇒ 尺报 16、grep 面 17 且零告警）。
        method="node_id: FAC- 行**去重**计数（非 grep -c）；重复行另记 detail.raw_line_count 并进 drift_flags"
        "；null 面=同节点块 module_ref: null",
        sources=(SPM_REL,),
        detail={
            "fac_ids": fac_ids,
            "raw_line_count": len(raw_lines),
            "duplicate_fac_lines": len(raw_lines) - len(fac_ids),
            "module_ref_null_ids": null_nodes,
            "module_ref_null_count": len(null_nodes),
        },
    )
    if not fac_ids:
        metric.unavailable("no 'node_id: FAC-' lines parsed")
    return metric


def _walk_node_module_refs(lines: list[str], prefix: str) -> list[tuple[str, bool]]:
    """节点块内 module_ref 是否为 null（用于缺位登记面，不做判据只作观测）。"""
    out: list[tuple[str, bool]] = []
    current: str | None = None
    seen_null: set[str] = set()
    for line in lines:
        m = re.search(rf"node_id:\s*({re.escape(prefix)}[A-Za-z0-9_-]+)", line)
        if m:
            current = m.group(1)
            continue
        if current is not None:
            if re.match(r"^\s*-?\s*node_id:", line):
                current = None
            elif re.match(r"^\s*module_ref:\s*null\s*$", line):
                seen_null.add(current)
                current = None
            elif line.strip() == "" or re.match(r"^\S", line):
                current = None
    for node_id in sorted(seen_null):
        out.append((node_id, True))
    return out


def measure_roor(root: Path) -> Metric:
    text = _read_text(root, ROOR_REL)
    lines = text.splitlines()
    grep_count = sum(1 for ln in lines if "registry_id: REG-" in ln)
    summary_match = re.search(r"^\s*total_registries:\s*(\d+)\s*$", text, re.M)
    summary_value = int(summary_match.group(1)) if summary_match else None
    metric = Metric(
        key="roor_registries",
        label="ROOR 注册表数",
        measured=grep_count,
        method="grep -c 'registry_id: REG-'（实测面）；summary.total_registries 字段另记为声称探针",
        sources=(ROOR_REL,),
        detail={
            "grep_count": grep_count,
            "summary_field_present": summary_value is not None,
        },
    )
    if grep_count == 0:
        metric.unavailable("no 'registry_id: REG-' lines parsed")
    if summary_value is None:
        metric.detail["summary_field_note"] = "summary.total_registries 字段未找到"
    return metric, summary_value


def _disk_book_rels(mining: Path) -> set[str]:
    """盘面（含未落地 WIP）挖矿 *.md 集合，路径相对 mining root——只作观测，不记功。"""
    if not mining.is_dir():
        return set()
    return {p.relative_to(mining).as_posix().replace("\\", "/") for p in mining.rglob("*.md") if p.is_file()}


def head_mining_books(head: HeadTracking) -> list[str]:
    """HEAD 跟踪集里属于挖矿面的 `.md`（仓库根相对路径，已排序）。"""
    if not head.ok:
        return []
    prefix = MINING_ROOT_REL + "/"
    return sorted(f for f in head.files if f.startswith(prefix) and f.endswith(".md"))


def measure_mining_books(root: Path, head: HeadTracking | None = None) -> Metric:
    """簿册面：**以 HEAD 跟踪集为实测面**（盘面只作附带观测＝P-0 落地面差）。

    红队实测教训（最重一条）：旧实现实测面读盘面（rglob），他道**未 git add 的 WIP 簿**
    被写进真源记录 ⇒ WIP 一丢，YAML 里留下悬空证据且恒红＝假绿持久化＋连坐。
    现：未落地件不得进入真源记录；盘面多出的件只报数不记功。
    """
    head = head if head is not None else resolve_head_tracking(root)
    disk = sorted(
        p.relative_to(root).as_posix().replace("\\", "/") for p in (root / MINING_ROOT_REL).rglob("*.md") if p.is_file()
    )
    tracked = head_mining_books(head)
    detail: dict[str, Any] = {
        "head_status": head.status,
        "head_count": len(tracked) if head.ok else None,
        "disk_count": len(disk),
    }
    if head.ok:
        detail["not_in_head_count"] = len(set(disk) - set(tracked))
        detail["not_in_head_sample"] = sorted(set(disk) - set(tracked))[:40]
        detail["in_head_missing_on_disk_count"] = len(set(tracked) - set(disk))
        detail["in_head_missing_on_disk_sample"] = sorted(set(tracked) - set(disk))[:40]
    metric = Metric(
        key="mining_books",
        label="挖矿簿册数（fullflow_mining/*.md，HEAD 跟踪集）",
        measured=len(tracked) if head.ok else None,
        method="git -c core.quotePath=false ls-tree -r --name-only HEAD 过滤 "
        f"{MINING_ROOT_REL}/*.md 计数（落地面实测面）；盘面 rglob 计数另记为 detail.disk_count，"
        "两者之差=not_in_head_count（P-0 敞口，未落地件不记功）",
        sources=(MINING_ROOT_REL,),
        detail=detail,
    )
    if not head.ok:
        metric.unavailable(f"HEAD 跟踪集取不到：{head.reason}")
    elif not tracked:
        metric.unavailable("no tracked .md under mining root in HEAD")
    return metric


def measure_code_top_domains(root: Path) -> Metric:
    base = root / SRC_ZEPHYR_REL
    if not base.is_dir():
        return Metric(
            key="code_top_domains",
            label="代码顶层包/域数（src/zephyr 一级目录）",
            method="目录实扫",
            sources=(SRC_ZEPHYR_REL,),
            status="unavailable",
            unavailable_reason=f"missing dir: {SRC_ZEPHYR_REL}",
        )
    dirs = sorted(
        d.name for d in base.iterdir() if d.is_dir() and not d.name.startswith((".", "_")) and d.name != "__pycache__"
    )
    return Metric(
        key="code_top_domains",
        label="代码顶层包/域数（src/zephyr 一级目录）",
        measured=len(dirs),
        method="一级目录计数，排除 . / __ 前缀与 __pycache__",
        sources=(SRC_ZEPHYR_REL,),
        detail={"excluded_prefixes": ["'.'", "'_'", "__pycache__"]},
    )


def measure_functional_domains(root: Path) -> Metric:
    """功能域注册表条目面（观测项，不与"模块册 58 域"混量纲——那是另一个对象）。"""
    try:
        text = _read_text(root, FUNCTIONAL_DOMAIN_REGISTRY_REL)
    except ReadFailure as exc:
        return Metric(
            key="functional_domain_registry_entries",
            label="功能域注册表条目数（functional_domain_registry）",
            method="grep -c '^- domain:' 行计数；去重 domain 值另记",
            sources=(FUNCTIONAL_DOMAIN_REGISTRY_REL,),
            status="unavailable",
            unavailable_reason=str(exc),
        )
    entry_lines = [ln for ln in text.splitlines() if re.match(r"^- domain:\s*\S+", ln)]
    domains = sorted({m.group(1).strip() for m in (re.match(r"^- domain:\s*(\S+)", ln) for ln in entry_lines) if m})
    metric = Metric(
        key="functional_domain_registry_entries",
        label="功能域注册表条目数（functional_domain_registry）",
        measured=len(entry_lines),
        method="grep -c '^- domain:'（条目行，含 domain+subdomain 粒度）；去重 domain 值数见 detail.distinct_domain_count",
        sources=(FUNCTIONAL_DOMAIN_REGISTRY_REL,),
        detail={
            "distinct_domain_count": len(domains),
            "distinct_domains": domains,
            "caliber_note": "与总册'模块册 58 域'不同量纲，勿直接比对（该项见 unverified_prose_claims）",
        },
    )
    if not entry_lines:
        metric.unavailable("no '^- domain:' entry lines matched")
    return metric


# ---------------------------------------------------------------- 声称值探针
CLAIM_PROBES: tuple[Probe, ...] = (
    Probe("f_links", TOTAL_BOOK_REL, r"合计 \*\*(\d+) 环节 / (\d+) 段\*\*", 1, "总册摘要行合计"),
    Probe("f_segment_count", TOTAL_BOOK_REL, r"合计 \*\*(\d+) 环节 / (\d+) 段\*\*", 2, "总册摘要行分段"),
    Probe("f_links", TOTAL_BOOK_REL, r"环节总清单（(\d+) 环节 / (\d+) 段）", 1, "§一 标题"),
    Probe("f_segment_count", TOTAL_BOOK_REL, r"环节总清单（(\d+) 环节 / (\d+) 段）", 2, "§一 标题分段"),
    Probe("f_segment_B", TOTAL_BOOK_REL, r"六车道 (\d+) 环节", 1, "摘要行：策略工厂新增段行数声称"),
    Probe("f_segment_D", TOTAL_BOOK_REL, r"环节级细化（(\d+) 环节）", 1, "摘要行：TDM 细化段行数声称"),
    Probe("f_segment_C", TOTAL_BOOK_REL, r"知识供给线 L9（(\d+) 环节）", 1, "摘要行：L9 段行数声称"),
    Probe("f_segment_H", TOTAL_BOOK_REL, r"模拟盘→转正链（(\d+) 环节）", 1, "摘要行：转正链段行数声称"),
    Probe("tdm_nodes", TOTAL_BOOK_REL, r"消费端 (\d+) 节点四流", 1, "七源真源行"),
    Probe("tdm_nodes", TOTAL_BOOK_REL, r"(\d+) 节点：entry", 1, "§D 段标题"),
    Probe(
        "tdm_nodes", WAVE1_COMMAND_BOOK_REL, r"TDM\D{0,2}(\d+)\s*节点", 1, "波1 指挥册数值漂移四例之一（过期声称面）"
    ),
    Probe("roor_registries", TOTAL_BOOK_REL, r"registry_of_registries\.yaml（(\d+) 册）", 1, "七源真源行"),
    Probe("roor_registries", TOTAL_BOOK_REL, r"ROOR (\d+) 册", 1, "F109 行"),
    Probe("code_top_domains", TOTAL_BOOK_REL, r"src/zephyr/ 一级 (\d+) 包实扫", 1, "七源真源行⑥"),
)

# 无对照实测面的散文声称（如实挂"未验"，不填估计值）
UNVERIFIED_CLAIM_PROBES: tuple[Probe, ...] = (
    Probe("module_catalog_rows", TOTAL_BOOK_REL, r"模块册（(\d+) 模块/58 域）", 1, "七源真源行③：模块册行数"),
    Probe("module_catalog_domains", TOTAL_BOOK_REL, r"模块册（7686 模块/(\d+) 域）", 1, "七源真源行③：模块册域数"),
    Probe("business_asset_tables_vs_axes", TOTAL_BOOK_REL, r"业务资产库 (\d+) 表", 1, "§五 口径漂移①宪法侧表数"),
    Probe("business_asset_tables_vs_axes", TOTAL_BOOK_REL, r"declared (\d+) 轴", 1, "§五 口径漂移①代码侧轴数"),
    Probe("backlog_objects", TOTAL_BOOK_REL, r"backtest_backlog (\d+) 对象", 1, "F66 行"),
    Probe("gate_canonical", TOTAL_BOOK_REL, r"(\d+) 门禁 canonical", 1, "F98 行"),
    Probe("trae_rule_files", TOTAL_BOOK_REL, r"(\d+) trae_\*\.yaml", 1, "F101 行"),
)

TDM_FLOW_CLAIM_RE = re.compile(r"(\d+) 节点：entry (\d+)/position (\d+)/exit (\d+)/portfolio (\d+)")


def _roor_summary_probe_value(text: str) -> int | None:
    m = re.search(r"^\s*total_registries:\s*(\d+)\s*$", text, re.M)
    return int(m.group(1)) if m else None


class _ClaimSink:
    """散文声称收集器（按 (metric,file,line,value) 去重；行为等价拆出，COMPLEXITY-GUARD 治本）。"""

    __slots__ = ("claims", "measured", "seen")

    def __init__(
        self, claims: list[dict[str, Any]], seen: set[tuple[str, str, int, int]], measured: dict[str, Metric]
    ) -> None:
        self.claims = claims
        self.seen = seen
        self.measured = measured

    def add(self, metric: str, file_rel: str, line_no: int, text: str, value: int, note: str) -> None:
        dedupe = (metric, file_rel, line_no, value)
        if dedupe in self.seen:
            return
        self.seen.add(dedupe)
        m = self.measured.get(metric)
        self.claims.append(
            {
                "metric": metric,
                "claimed": value,
                "measured": (m.measured if m else None),
                "file": file_rel,
                "line": line_no,
                "note": note,
                "excerpt": text.strip()[:160],
            }
        )


def _collect_prose_claims(root: Path, sink: _ClaimSink) -> None:
    """CLAIM_PROBES 散文声称扫描（total_registries 除外——值在字段而非散文）。"""
    for probe in CLAIM_PROBES:
        if probe.pattern.startswith("total_registries"):
            continue  # 特殊处理（值在字段而非散文）
        try:
            text = _read_text(root, probe.file_rel)
        except ReadFailure:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            m = re.search(probe.pattern, line)
            if m:
                sink.add(probe.metric, probe.file_rel, line_no, line, int(m.group(probe.group)), probe.note)


def _collect_roor_claim(root: Path, sink: _ClaimSink) -> None:
    """ROOR summary 字段：散文声称 vs grep 实测。"""
    try:
        roor_text = _read_text(root, ROOR_REL)
        summary_value = _roor_summary_probe_value(roor_text)
        if summary_value is not None:
            for line_no, line in enumerate(roor_text.splitlines(), start=1):
                if re.match(r"^\s*total_registries:\s*\d+\s*$", line):
                    sink.add(
                        "roor_registries",
                        ROOR_REL,
                        line_no,
                        line,
                        summary_value,
                        "summary.total_registries 字段（机读声称面）",
                    )
                    break
    except ReadFailure:
        pass


def _collect_tdm_claims(root: Path, measured: dict[str, Metric], claims: list[dict[str, Any]]) -> None:
    """TDM 分段声称（entry/position/exit/portfolio）。"""
    try:
        book = _read_text(root, TOTAL_BOOK_REL)
    except ReadFailure:
        book = ""
    for line_no, line in enumerate(book.splitlines(), start=1):
        m = TDM_FLOW_CLAIM_RE.search(line)
        if m:
            tdm = measured.get("tdm_nodes")
            flows = tdm.detail.get("flow_distribution", {}) if tdm else {}
            for name, idx in (("entry", 2), ("position", 3), ("exit", 4), ("portfolio", 5)):
                claims.append(
                    {
                        "metric": f"tdm_flow_{name}",
                        "claimed": int(m.group(idx)),
                        "measured": flows.get(name),
                        "file": TOTAL_BOOK_REL,
                        "line": line_no,
                        "note": f"§D 段标题 flow:{name}",
                        "excerpt": line.strip()[:160],
                    }
                )


def _build_drifts(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """声称 vs 实测对撞：取不到数=measured_unavailable 报红；对不上=claimed_ne_measured。"""
    drifts: list[dict[str, Any]] = []
    for claim in claims:
        measured_value = claim.get("measured")
        if measured_value is None:
            drifts.append(
                {
                    "id": f"{claim['metric']}@{Path(claim['file']).name}:{claim['line']}",
                    "kind": "measured_unavailable",
                    "metric": claim["metric"],
                    "claimed": claim["claimed"],
                    "measured": None,
                    "file": claim["file"],
                    "line": claim["line"],
                    "note": "实测面取不到——报红，不填估计值",
                }
            )
        elif int(claim["claimed"]) != int(measured_value):
            drifts.append(
                {
                    "id": f"{claim['metric']}@{Path(claim['file']).name}:{claim['line']}",
                    "kind": "claimed_ne_measured",
                    "metric": claim["metric"],
                    "claimed": claim["claimed"],
                    "measured": measured_value,
                    "delta": int(claim["claimed"]) - int(measured_value),
                    "file": claim["file"],
                    "line": claim["line"],
                    "note": claim["note"],
                    "excerpt": claim["excerpt"],
                }
            )
    return drifts


def _collect_unverified(root: Path) -> list[dict[str, Any]]:
    """无实测面的散文声称：如实挂未验（本尺只报"没有对照面"，不猜数）。"""
    unverified: list[dict[str, Any]] = []
    unverified_seen: set[tuple[str, str, int]] = set()
    for probe in UNVERIFIED_CLAIM_PROBES:
        try:
            text = _read_text(root, probe.file_rel)
        except ReadFailure:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            m = re.search(probe.pattern, line)
            if m:
                try:
                    value: int | str = int(m.group(probe.group))
                except ValueError:
                    value = m.group(probe.group)
                key = (probe.metric, probe.file_rel, line_no)
                if key in unverified_seen:
                    continue
                unverified_seen.add(key)
                unverified.append(
                    {
                        "metric": probe.metric,
                        "claimed": value,
                        "measured_source": "none_registered",
                        "status": "unverified",
                        "file": probe.file_rel,
                        "line": line_no,
                        "note": probe.note,
                        "excerpt": line.strip()[:160],
                    }
                )
    unverified.sort(key=lambda u: (u["metric"], u["file"], u["line"]))
    return unverified


def collect_claims(
    root: Path, measured: dict[str, Metric]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """返回 (claims 列表, drift 列表, unverified_prose_claims 列表)。"""
    claims: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int, int]] = set()
    sink = _ClaimSink(claims, seen, measured)

    _collect_prose_claims(root, sink)
    _collect_roor_claim(root, sink)
    _collect_tdm_claims(root, measured, claims)

    drifts = _build_drifts(claims)
    claims.sort(key=lambda c: (c["metric"], c["file"], c["line"], c["claimed"]))
    drifts.sort(key=lambda d: (d["metric"], d["file"], d["line"], str(d["claimed"])))

    # 无实测面的散文声称：如实挂未验（本尺只报"没有对照面"，不猜数）
    unverified = _collect_unverified(root)
    return claims, drifts, unverified


# ---------------------------------------------------------------- 覆盖矩阵
def classify_token(digits: str, valid_ids: set[str]) -> tuple[str, str]:
    """候选 F 号 → (记功号 or "", 不认原因 or "")。

    判据只有两条：**位数必须 2-3 位**（禁贪婪切片，`F12345678` 不得被切成 `F123`/`F12`）
    且**必须在总册实际存在的号集里**。二者任一不满足 ⇒ 不记功，且必须报漂移位。
    """
    if len(digits) > 3:
        return "", "too_many_digits"
    if len(digits) < 2:
        return "", "too_few_digits"
    fid = f"F{digits}"
    if fid not in valid_ids:
        return "", "not_in_total_book"
    return fid, ""


def _covers_from_frontmatter(text: str) -> tuple[set[str], list[dict[str, Any]]]:
    """frontmatter ``covers:`` 必须是 **YAML 列表**；否则按解析失败处理、不记功。

    红队实测：``covers: F01 F02``（空格分隔）被 YAML 解析成字符串（甚至解析失败），
    旧尺却照样记功。此处解析不出列表＝零记功＋挂异常，不给"写了就等于认领"留缝。
    """
    anomalies: list[dict[str, Any]] = []
    m = FRONTMATTER_RE.match(text)
    if not m:
        return set(), anomalies
    block = m.group(1)
    if not re.search(r"^covers:", block, re.M):
        return set(), anomalies
    try:
        parsed = yaml.safe_load(block.replace("\r\n", "\n"))
    except Exception as exc:  # noqa: BLE001
        # frontmatter 解析失败＝不记功，但必须留痕（不静默隐身）
        anomalies.append({"surface": "covers:", "reason": "frontmatter_unparsable", "detail": str(exc)[:120]})
        return set(), anomalies
    if not isinstance(parsed, dict) or "covers" not in parsed:
        return set(), anomalies
    value = parsed.get("covers")
    if not isinstance(value, list):
        anomalies.append(
            {"surface": "covers:", "reason": "covers_not_a_list", "detail": f"{type(value).__name__}:{str(value)[:80]}"}
        )
        return set(), anomalies
    out: set[str] = set()
    for item in value:
        token = str(item).strip()
        cm = re.fullmatch(r"F(\d{1,9})", token)
        if not cm:
            anomalies.append({"surface": "covers:", "reason": "covers_item_not_an_f_id", "detail": token[:20]})
            continue
        out.add(token.upper())
    return out, anomalies


def _claim_tokens(rel: str, text: str, valid_ids: set[str]) -> tuple[set[str], list[dict[str, Any]]]:
    """环节认领＝**三处显式声明位**（文件名／严格式声明行／frontmatter covers 列表）。

    收紧史（红队 RB-1 案卷实测）：
    - 全文 grep → 裁定册/案卷只**点名**缺口就被判"已挖"（uncovered 6→0，尺当场说谎）；
    - 改版加"行首 `#` 标题"通道 → 一行塞 20 个号即把 uncovered 45→25；
    - "本册覆盖 …… 是事实"反讽句 → 宽松前缀匹配照样记功 ⇒ 声明行改**严格式**（行尾不得有散文）。
    删通道是收紧，不是放松。
    """
    tokens: set[str] = set()
    anomalies: list[dict[str, Any]] = []

    def consume(raw: str, digits: str, surface: str, line_no: int = 0) -> None:
        fid, why = classify_token(digits, valid_ids)
        if fid:
            tokens.add(fid)
        else:
            anomalies.append(
                {
                    "kind": "illegal_f_token_in_claim_surface",
                    "metric": "f_link_id_legality",
                    "claimed": raw,
                    "measured": None,
                    "file": f"{MINING_ROOT_REL}/{rel}",
                    "line": line_no,
                    "surface": surface,
                    "token": raw,
                    "reason": why,
                    "note": f"声明位 {surface} 出现不合法 F 号 {raw}（{why}）：不记功并报漂移",
                }
            )

    for digits in F_NAME_CAND_RE.findall(Path(rel).name.lower()):
        consume(f"F{digits}", digits, "filename")
    for line_no, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if not s.startswith("本册覆盖"):
            continue
        if COVER_LINE_RE.match(s):
            for digits in F_TOKEN_CAND_RE.findall(s):
                consume(f"F{digits}", digits, "本册覆盖-line", line_no)
            continue
        # 前缀像声明行但**不是**严格式（行尾带散文＝反讽/指认句，或号本身不合法）：整行不记功，
        # 且非法号仍要现形——"不认"与"必报"是两条独立的义务，缺一条就又回到零痕迹洗白。
        anomalies.append(
            {
                "kind": "declaration_line_malformed",
                "metric": "f_link_id_legality",
                "claimed": s[:80],
                "measured": None,
                "file": f"{MINING_ROOT_REL}/{rel}",
                "line": line_no,
                "surface": "本册覆盖-line",
                "reason": "declaration_line_not_strict",
                "note": "声明行不符严格式（行尾不得再有任何散文）⇒ 整行不记功",
            }
        )
        for digits in F_TOKEN_CAND_RE.findall(s):
            fid, why = classify_token(digits, valid_ids)
            if not fid:
                anomalies.append(
                    {
                        "kind": "illegal_f_token_in_claim_surface",
                        "metric": "f_link_id_legality",
                        "claimed": f"F{digits}",
                        "measured": None,
                        "file": f"{MINING_ROOT_REL}/{rel}",
                        "line": line_no,
                        "surface": "本册覆盖-line",
                        "token": f"F{digits}",
                        "reason": why,
                        "note": f"非严格式声明行内出现不合法 F 号 F{digits}（{why}）：不记功并报漂移",
                    }
                )
    fm_tokens, fm_anomalies = _covers_from_frontmatter(text)
    for token in sorted(fm_tokens):
        digits = token[1:]
        consume(token, digits, "covers:", 0)
    for a in fm_anomalies:
        anomalies.append(
            {
                "kind": "covers_surface_not_creditable",
                "metric": "f_link_id_legality",
                "claimed": a.get("detail", ""),
                "measured": None,
                "file": f"{MINING_ROOT_REL}/{rel}",
                "line": 0,
                "surface": a["surface"],
                "reason": a["reason"],
                "note": f"covers: 声明面不可记功（{a['reason']}）：{a.get('detail', '')}",
            }
        )
    return tokens, anomalies


def exclusion_anomalies(head: HeadTracking, root: Path | None = None) -> list[dict[str, Any]]:
    """豁免清单自守（宪法 §9.5：手工清单必漂移）——每条必须在 HEAD 跟踪集里存在。

    两态分开报，便于落地侧分辨处置：
    - ``non_workbook_exclusion_orphan``：盘上根本没有此件＝清单躺尸（红队实测 A2.4 抓到一条），
      须删条目（本函数只报，不代改清单）；
    - ``non_workbook_exclusion_not_landed``：盘上有、HEAD 无（已 staged 未提交）——落地后自愈，
      但当前同样不得算绿（清单引用了一条不在真源记录里的路径）。
    """
    if not head.ok:
        return [
            {
                "kind": "non_workbook_exclusions_unverifiable",
                "metric": "non_workbook_exclusions",
                "claimed": len(NON_WORKBOOK_RELS),
                "measured": None,
                "file": MINING_ROOT_REL,
                "line": 0,
                "note": f"HEAD 跟踪集不可用，无法校验豁免清单完备性：{head.reason}",
            }
        ]
    tracked = set(head.files)
    out: list[dict[str, Any]] = []
    for rel in NON_WORKBOOK_RELS:
        full = f"{MINING_ROOT_REL}/{rel}"
        if full in tracked:
            continue
        on_disk = bool(root is not None and (root / full).is_file())
        out.append(
            {
                "kind": "non_workbook_exclusion_not_landed" if on_disk else "non_workbook_exclusion_orphan",
                "metric": "non_workbook_exclusions",
                "claimed": 1,
                "measured": 0,
                "file": full,
                "line": 0,
                "note": (
                    "豁免清单条目盘上有但未入 HEAD（已 staged 未落地）"
                    if on_disk
                    else "豁免清单条目盘上无此件（孤儿，须从清单删）＝手工清单漂移"
                ),
            }
        )
    return out


def _collect_workbook_claims(
    root: Path,
    head: HeadTracking,
    valid_ids: set[str],
    excluded: set[str],
) -> tuple[dict[str, set[str]], list[dict[str, Any]], list[str], list[str]]:
    """HEAD 跟踪作业簿的认领面收集（COMPLEXITY-GUARD 治本：自 build_coverage 拆出，行为等价）。

    返回 (workbooks, anomalies, missing_on_disk, tracked)。
    """
    tracked = head_mining_books(head)
    workbooks: dict[str, set[str]] = {}
    anomalies: list[dict[str, Any]] = []
    missing_on_disk: list[str] = []
    for rel in tracked:
        book_rel = rel[len(MINING_ROOT_REL) + 1 :]
        if book_rel in excluded:
            continue
        path = root / rel
        if not path.is_file():
            missing_on_disk.append(rel)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        workbooks[book_rel], extra = _claim_tokens(book_rel, text, valid_ids)
        anomalies.extend(extra)

    if not head.ok:
        anomalies.append(
            {
                "kind": "coverage_claim_surface_unavailable",
                "metric": "coverage_matrix",
                "claimed": None,
                "measured": None,
                "file": MINING_ROOT_REL,
                "line": 0,
                "note": f"作业簿集合取不到（HEAD 面不可用）⇒ 覆盖矩阵无真源可依，不算绿：{head.reason}",
            }
        )
    if not valid_ids:
        # 总册读不到＝号集无权威：不逐册刷"非法号"噪音，只挂一条根因（矩阵全 uncovered，照样红）
        anomalies = [
            {
                "kind": "f_id_authority_unavailable",
                "metric": "f_link_id_legality",
                "claimed": None,
                "measured": None,
                "file": TOTAL_BOOK_REL,
                "line": 0,
                "note": "总册取不到 ⇒ 无合法号集可依，认领一律不记功（不猜号）",
            }
        ]
    for rel in missing_on_disk:
        anomalies.append(
            {
                "kind": "head_book_missing_on_disk",
                "metric": "coverage_matrix",
                "claimed": None,
                "measured": None,
                "file": rel,
                "line": 0,
                "note": "HEAD 有而工作树无（工作树删除未落地）——本轮不记功，只报观测",
            }
        )
    return workbooks, anomalies, missing_on_disk, tracked


def _build_segment_matrix(
    segments: dict[str, list[str]], workbooks: dict[str, set[str]]
) -> tuple[dict[str, Any], list[str], list[str]]:
    """逐段覆盖矩阵行装配（COMPLEXITY-GUARD 治本：自 build_coverage 拆出，行为等价）。"""
    matrix: dict[str, Any] = {}
    covered: list[str] = []
    uncovered: list[str] = []
    for seg in sorted(segments):
        rows: list[dict[str, Any]] = []
        for fid in sorted(segments[seg], key=lambda x: int(x[1:])):
            hits = sorted(rel for rel, tokens in workbooks.items() if fid in tokens)
            rows.append(
                {
                    "id": fid,
                    "status": "covered" if hits else "uncovered",
                    "workbooks": hits,
                    "workbook_count": len(hits),
                }
            )
            (covered if hits else uncovered).append(fid)
        matrix[seg] = {
            "declared_range": f"{segments[seg][0]}-{segments[seg][-1]}" if segments[seg] else "",
            "row_count": len(rows),
            "covered": sum(1 for r in rows if r["status"] == "covered"),
            "uncovered": sum(1 for r in rows if r["status"] == "uncovered"),
            "rows": rows,
        }
    covered.sort(key=lambda x: int(x[1:]))
    uncovered.sort(key=lambda x: int(x[1:]))
    return matrix, covered, uncovered


def build_coverage(
    root: Path,
    segments: dict[str, list[str]],
    all_ids: list[str],
    head: HeadTracking | None = None,
) -> dict[str, Any]:
    """逐段挖矿覆盖矩阵：每个 F 环节 → 有没有**已落地**作业簿**显式认领**它（缺口地图）。

    作业簿集合＝HEAD 跟踪集 ∩ mining root − 非作业簿清单；工作树未落地件不进入记录，
    故他道 WIP 被丢弃后不会在真源 YAML 里留下悬空"证据"。
    """
    head = head if head is not None else resolve_head_tracking(root)
    mining = root / MINING_ROOT_REL
    excluded = {e.replace("\\", "/") for e in NON_WORKBOOK_RELS}
    valid_ids = set(all_ids)
    workbooks, anomalies, _missing, tracked = _collect_workbook_claims(root, head, valid_ids, excluded)

    matrix, covered, uncovered = _build_segment_matrix(segments, workbooks)
    id_hits: dict[str, int] = {rel: len(tokens) for rel, tokens in sorted(workbooks.items())}
    anomalies.sort(
        key=lambda a: (str(a.get("kind")), str(a.get("file")), int(a.get("line") or 0), str(a.get("token", "")))
    )
    return {
        "definition": {
            # 自述与实现同源：这段文字必须与 ``_claim_tokens`` 一致（旧串仍写"正文 grep"＝读者按串复算得另一套数）。
            "covered": CLAIM_SURFACE_DESC,
            "claim_surfaces": ["filename:fnn", "本册覆盖-line(strict)", "frontmatter covers: (YAML list)"],
            "removed_claim_surfaces": [
                "行首 # 标题行（一行塞 20 号即可批量洗白）",
                "正文/HTML 注释/frontmatter 散文 grep（裁定册只点名缺口就被判已挖）",
            ],
            "workbook_set": f"HEAD 跟踪集（git -c core.quotePath=false ls-tree -r --name-only HEAD）∩ {MINING_ROOT_REL}/*.md − 非作业簿清单；工作树未落地件不记功",
            "head_status": head.status,
            "non_workbook_excluded": sorted(excluded),
            "non_workbook_excluded_count": len(excluded),
            "workbook_count": len(workbooks),
            "tracked_book_count": len(tracked),
            "untracked_books_ignored_count": len(
                _disk_book_rels(mining) - {r[len(MINING_ROOT_REL) + 1 :] for r in tracked}
            ),
            "untracked_books_ignored_sample": sorted(
                _disk_book_rels(mining) - {r[len(MINING_ROOT_REL) + 1 :] for r in tracked}
            )[:40],
            "workbooks_with_zero_f_tokens": sorted(rel for rel, tokens in workbooks.items() if not tokens),
            "f_token_census_per_workbook": dict(sorted(id_hits.items())),
            "claim_anomalies": anomalies,
        },
        "totals": {
            "links": len(all_ids),
            "covered": len(covered),
            "uncovered": len(uncovered),
        },
        "covered_ids": covered,
        "uncovered_ids": uncovered,
        "segments": matrix,
    }


# ---------------------------------------------------------------- 装配
def _safe_measure(root: Path, key: str, label: str, sources: tuple[str, ...], fn) -> Metric:
    """真源读不到 → status unavailable（报红、不崩、不填估计值）。"""
    try:
        return fn(root)
    except ReadFailure as exc:
        return Metric(
            key=key,
            label=label,
            method="未取到（真源不可读）",
            sources=sources,
            status="unavailable",
            unavailable_reason=str(exc),
        )


def measure_roor_grep(root: Path) -> Metric:
    return measure_roor(root)[0]


def _measure_all(
    root: Path, head: HeadTracking
) -> tuple[list[Metric], dict[str, Metric], dict[str, list[str]], Metric]:
    """五向计数实测面装配（COMPLEXITY-GUARD 治本：自 build_payload 拆出，行为等价）。

    返回 (metrics, measured, segments, f_metric)；measured 含 f_segment_*/tdm_flow_* 派生键；真源读不到→status unavailable 报红不崩。
    """
    metrics: list[Metric] = []
    try:
        f_metric, segments = measure_f_links(root)
    except ReadFailure as exc:
        f_metric = Metric(
            key="f_links",
            label="全流通环节数（F 编号）",
            method="未取到（总册不可读）",
            sources=(TOTAL_BOOK_REL,),
            status="unavailable",
            unavailable_reason=str(exc),
        )
        segments = {}
    metrics.append(f_metric)
    metrics.append(_safe_measure(root, "tdm_nodes", "TDM 消费端节点数", (TDM_REL,), measure_tdm))
    metrics.append(_safe_measure(root, "factory_nodes", "策略工厂节点数（FAC-）", (SPM_REL,), measure_factory))
    metrics.append(_safe_measure(root, "roor_registries", "ROOR 注册表数", (ROOR_REL,), measure_roor_grep))
    metrics.append(measure_mining_books(root, head))
    metrics.append(_safe_measure(root, "code_top_domains", "代码顶层包数", (SRC_ZEPHYR_REL,), measure_code_top_domains))
    metrics.append(
        _safe_measure(
            root,
            "functional_domain_registry_entries",
            "功能域注册表条目数",
            (FUNCTIONAL_DOMAIN_REGISTRY_REL,),
            measure_functional_domains,
        )
    )

    measured = {m.key: m for m in metrics}
    per_segment = dict(f_metric.detail.get("per_segment", {}))
    measured["f_segment_count"] = Metric(
        key="f_segment_count",
        label="总分段数",
        measured=f_metric.detail.get("segment_count"),
        method="同 f_links：'^### [A-Z] 段' 计数",
        sources=(TOTAL_BOOK_REL,),
    )
    for letter in sorted(per_segment):
        if letter == "UNSEGMENTED":
            continue
        measured[f"f_segment_{letter}"] = Metric(
            key=f"f_segment_{letter}",
            label=f"{letter} 段行数",
            measured=per_segment[letter],
            method="同 f_links：段内 F 行去重计数",
            sources=(TOTAL_BOOK_REL,),
        )
    tdm = measured["tdm_nodes"]
    for name, value in (tdm.detail.get("flow_distribution") or {}).items():
        measured[f"tdm_flow_{name}"] = Metric(
            key=f"tdm_flow_{name}",
            label=f"TDM flow:{name} 节点数",
            measured=value,
            method="TDM 'flow:' 行计数（去 '_flow' 后缀归一）",
            sources=(TDM_REL,),
        )
    return metrics, measured, segments, f_metric


def _collect_structural_drifts(
    drifts: list[dict[str, Any]],
    f_metric: Metric,
    all_ids: list[str],
    measured: dict[str, Metric],
) -> None:
    """结构性缺口漂移追加（COMPLEXITY-GUARD 治本：自 build_payload 拆出，行为等价）。"""
    # 结构性缺口漂移：表格行数 vs 去重 id 数（重复行/漏号在此现形）
    row_count = int(f_metric.detail.get("row_count", 0) or 0)
    if row_count != len(all_ids):
        drifts.append(
            {
                "id": "f_links@rows_vs_unique",
                "kind": "row_count_ne_unique_ids",
                "metric": "f_links",
                "claimed": row_count,
                "measured": len(all_ids),
                "delta": row_count - len(all_ids),
                "file": TOTAL_BOOK_REL,
                "line": 0,
                "note": "F 表格行数与去重 id 数不一致（重复行或编号复用）",
            }
        )
    # 总册编号不变式（断号/越界/首号）——红队实测"塞一行 F999 顶高 f_links 而零告警"
    drifts.extend(numbering_anomalies(all_ids))
    # 工厂面：method 自述"去重"与 grep 面的背离点（重复 FAC 行必须现形，不再零告警）
    fac_metric = measured.get("factory_nodes")
    if fac_metric is not None and fac_metric.status == "ok":
        dup_fac = int(fac_metric.detail.get("duplicate_fac_lines", 0) or 0)
        if dup_fac:
            drifts.append(
                {
                    "kind": "factory_fac_line_duplicates",
                    "metric": "factory_nodes",
                    "claimed": int(fac_metric.detail.get("raw_line_count", 0) or 0),
                    "measured": fac_metric.measured,
                    "delta": dup_fac,
                    "file": SPM_REL,
                    "line": 0,
                    "note": "node_id: FAC- 存在重复行（grep -c 面与去重面不等价）",
                }
            )


def build_payload(root: Path) -> dict[str, Any]:
    head = resolve_head_tracking(root)
    metrics, measured, segments, f_metric = _measure_all(root, head)
    all_ids = sorted({fid for ids in segments.values() for fid in ids}, key=lambda x: int(x[1:]))

    claims, drifts, unverified = collect_claims(root, measured)

    coverage = build_coverage(root, segments, all_ids, head)

    # 结构性缺口漂移：表格行数 vs 去重 id 数（重复行/漏号在此现形）
    _collect_structural_drifts(drifts, f_metric, all_ids, measured)
    # 手工豁免清单自守（宪法 §9.5）——孤儿条目当场报漂移
    drifts.extend(exclusion_anomalies(head, root))
    # 认领面异常（非法号 / covers 非列表 / HEAD 面不可用）——"不认且必报"，不静默
    drifts.extend(coverage["definition"]["claim_anomalies"])
    for d in drifts:
        d.setdefault("id", f"{d.get('metric')}@{Path(str(d.get('file'))).name}:{d.get('line')}")
    drifts.sort(key=lambda d: (str(d.get("metric")), str(d.get("file")), int(d.get("line") or 0), str(d.get("kind"))))

    payload: dict[str, Any] = {
        "generated_by": GENERATED_BY,
        "artifact_kind": "machine_generated_do_not_hand_edit",
        "idempotency": "无时间戳/无随机项；输入相同则字节相同（配 pytest 幂等断言）",
        "head_tracking": {
            "status": head.status,
            "reason": head.reason,
            "tracked_files_total": len(head.files) if head.ok else None,
            "method": "git -c core.quotePath=false ls-tree -r --name-only HEAD（先验 .git 与 toplevel==repo root，绝不上溯外层仓库）",
        },
        "source_files": sorted(
            {
                TOTAL_BOOK_REL,
                TDM_REL,
                SPM_REL,
                ROOR_REL,
                FUNCTIONAL_DOMAIN_REGISTRY_REL,
                WAVE1_COMMAND_BOOK_REL,
                MINING_ROOT_REL,
                SRC_ZEPHYR_REL,
            }
        ),
        "scope_note": "本表只读真源、只写自身 YAML；数字只出现在字段里，散文引用数字须写'见 YAML 的 <字段>'",
        "five_way_counts": [m.key for m in metrics if m.key in FIVE_WAY_KEYS],
        "counts": {m.key: m.to_dict() for m in metrics},
        "claims": claims,
        "unverified_prose_claims": unverified,
        "drift_flags": drifts,
        "drift_summary": {
            "total_drifts": len(drifts),
            "by_metric": _count_by(drifts, "metric"),
            "unavailable_metrics": sorted(m.key for m in metrics if m.status == "unavailable"),
            "unverified_prose_claims": len(unverified),
            "coverage_uncovered_links": coverage["totals"]["uncovered"],
            "head_tracking_ok": head.ok,
            "red": bool(drifts)
            or any(m.status == "unavailable" for m in metrics)
            or not head.ok
            or coverage["totals"]["uncovered"] > 0,
        },
        "coverage_matrix": coverage,
    }
    return payload


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        out[str(item.get(key))] = out.get(str(item.get(key)), 0) + 1
    return dict(sorted(out.items()))


def render(payload: dict[str, Any]) -> str:
    header = (
        "# 机生对账表：勿手改（改判据请改生成器）。宪法 §9.5「静态清单禁手工维护」的落地尺。\n"
        "# 幂等：无时间戳字段；重复运行字节相同。数字只在字段里，散文引用请写「见 YAML 的 <字段>」。\n"
    )
    body = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=118)
    return header + body


def _normalize_eol(data: bytes) -> bytes:
    """行尾归一：检出被 git renormalize 成 CRLF 的产物不得恒红（红队实测 A6.4）。

    语义未放宽——仍只判"生成物是否陈旧"，只是不再把与内容无关的行尾差异算成陈旧。
    """
    return data.replace(b"\r\n", b"\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="全流通五向对账生成器（机生 YAML）")
    parser.add_argument("--repo-root", default=None, help="仓库根（默认由脚本位置推断）")
    parser.add_argument("--out", default=None, help=f"输出路径（默认 {OUTPUT_REL}）")
    parser.add_argument("--stdout", action="store_true", help="只打印不写盘")
    parser.add_argument(
        "--check",
        action="store_true",
        help="GATE-21 陈旧检测：生成物与再生成字节不一致即 exit 1（不判世界状态漂移）",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[3]
    payload = build_payload(root)
    text = render(payload)

    if args.stdout:
        sys.stdout.write(text)
        return 0

    out = Path(args.out) if args.out else root / OUTPUT_REL

    if args.check:
        # 只判"生成物是否落后于真源"，不判 drift_flags：后者是数据面事实（如 ROOR 声称 76 vs 实 77），
        # 硬拦＝用别人的账挡住本仓所有提交。判红须由对账面自己收口，不由门位连带坐牢。
        if not out.exists():
            print(f"STALE: {out} 不存在——跑本生成器（去 --check）产出")
            return 1
        if _normalize_eol(out.read_bytes()) != _normalize_eol(text.encode("utf-8")):
            print(f"STALE: {out} 与再生成字节不一致（作业簿/真源已动而 YAML 未重跑）")
            return 1
        print(f"fresh: {out}")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    if not args.quiet:
        summary = payload["drift_summary"]
        print(f"wrote {out}")
        print("counts: " + ", ".join(f"{k}={v['measured']}" for k, v in payload["counts"].items()))
        print(f"drifts: {summary['total_drifts']} by_metric={summary['by_metric']}")
        print(
            f"coverage: covered={payload['coverage_matrix']['totals']['covered']} "
            f"uncovered={payload['coverage_matrix']['totals']['uncovered']}"
        )
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 对账尺=车道/总筹按需手跑 CLI，非常驻自动任务，零事件订阅
    raise SystemExit(main())
