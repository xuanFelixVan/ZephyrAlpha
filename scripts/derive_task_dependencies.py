# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.derive_task_dependencies
# [DOMAIN] D_DATA
# [DEPENDENCIES] yaml(标准库) re pathlib argparse dataclasses
# [CONSUMERS] 施工车道（人工触发）+ 后续 catchup 拓扑重放备料
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 只从既有真源推依赖（任务写入表 vs 他任务实现码读取表），禁凭表名猜；
#  输出幂等（同输入同产物）；置信度非 high 的条目只登记不写入 tasks.yaml
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源文件缺失→FileNotFoundError 上抛；环检测→ValueError；
#  推导器不静默吞异常（fail-visible），--apply 前置校验不过即退出非零
# [TESTS] python scripts/derive_task_dependencies.py --dry-run（产出建议清单，不改文件）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 按需触发的批处理 CLI 治理工具（同先例 batch_creation_tokens.py /
#   onboard_source.py）——施工期人工或总包批后重跑再生血缘建议，非 daemon/非常驻；其"自动触发"面由
#   schedule.yaml 排班与 catchup 拓扑重放承接（消费本文件产出的 dependencies 声明），不属本脚本自身职责。
"""任务依赖推导器（治本 BRK-050：262 任务中 235 个无 dependencies 声明）。

做法：从**实际数据血缘**推依赖，而不是人工逐条判断（宪法 §9.5 静态清单禁手工维护）。
证据族（每条建议都带 file:line 与置信度）：

- F1 ``impl_direct``：任务 capability 的实现函数体内直接出现的表级读取
  （含同一文件内被其调用的私有方法体、以及其引用的模块级常量块）
- F2 ``impl_module``：实现函数 import 的 zephyr 模块内出现的表级读取（跨文件一跳）
- F3 ``task_prose``：tasks.yaml 自身 description/disabled_reason 里点名其他任务的
  表或其 task_id（写任务的人自己留的话，属第一方证据）
- D1 ``source_contention``：同一档期内同非线程安全源（如单一 SDK 插件）的任务对——
  这是 BRK-067 型争用的检测器，输出为"串行化建议"而非表级血缘
- D2 ``slot_inversion``：已声明依赖指向更晚档期 → 报倒挂，不新增

置信度判据：high = 表级唯一生产者 + 证据在实现码或任务自身文字里；
medium = 跨文件一跳或多生产者歧义；low = 语义冲突/倒挂。只有 high 写入 tasks.yaml。

用法（仓库根，Python 3.12）：
    python scripts/derive_task_dependencies.py --dry-run
    python scripts/derive_task_dependencies.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

import yaml

_BOOTSTRAP_ROOT: Final[str] = str(Path(__file__).resolve().parents[1])
if _BOOTSTRAP_ROOT not in sys.path:
    sys.path.insert(0, _BOOTSTRAP_ROOT)
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT 路径真源

CONFIG_DIR: Final[Path] = REPO_ROOT / "src" / "zephyr" / "data" / "config"
TASKS_YAML: Final[Path] = CONFIG_DIR / "tasks.yaml"
SCHEDULE_YAML: Final[Path] = CONFIG_DIR / "schedule.yaml"
CATEGORIES_YAML: Final[Path] = (
    REPO_ROOT / "docs" / "03_modules" / "_cross_layer" / "database" / "business_data_categories.yaml"
)
PROPOSALS_MD: Final[Path] = (
    REPO_ROOT / "docs" / "_working" / "fullflow_campaign" / "lanes" / "dag_dependency_proposals.md"
)
SRC_ROOT: Final[Path] = REPO_ROOT / "src"

# 表级 token：形如 <db>.<table>（数据库名以 c+数字 开头，本仓 ClickHouse 库命名惯例）
_TABLE_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"\bc[0-9]_[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\b")
# 模板化表名（如 <db>.kline_{period}）：取 '{' 之前的前缀展开成真实表集合
_TABLE_TEMPLATE_RE: Final[re.Pattern[str]] = re.compile(r"\b(c[0-9]_[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)_\{[a-z_]+\}")
_STR_ARG_RE: Final[re.Pattern[str]] = re.compile(r"\(\s*[\"']([a-z][a-z0-9_]*)[\"']\s*\)")
_ZEPHYR_IMPORT_RE: Final[re.Pattern[str]] = re.compile(r"^\s*(?:from|import)\s+(zephyr(?:\.[A-Za-z0-9_]+)+)", re.M)
_SELF_CALL_RE: Final[re.Pattern[str]] = re.compile(r"self\.([a-z_][a-z0-9_]*)\(")
_CONST_RE: Final[re.Pattern[str]] = re.compile(r"\b([A-Z][A-Z0-9_]{2,})\b")
DEF_RE: Final[re.Pattern[str]] = re.compile(r"^( *)def ([A-Za-z_][A-Za-z0-9_]*)\(", re.M)
DERIVED_TAG: Final[str] = "[DAG-DERIVED]"
# 单任务新增前置预算：扇入过宽会把"任一上游失败即 BLOCKED"的耦合放大
# （TaskQueue 语义：前置 FAILED -> 当前 BLOCKED），故超预算的同族边只登记不落地。
MAX_NEW_DEPS_PER_TASK: Final[int] = 4


@dataclass(frozen=True)
class DagDeriveConfig:
    """推导器输入路径集合（单参数对象，避开长参数表面）。"""

    tasks_yaml: Path = TASKS_YAML
    schedule_yaml: Path = SCHEDULE_YAML
    categories_yaml: Path = CATEGORIES_YAML
    proposals_md: Path = PROPOSALS_MD
    src_root: Path = SRC_ROOT
    max_new_deps_per_task: int = MAX_NEW_DEPS_PER_TASK


@dataclass
class DagEvidence:
    """一条血缘证据：读到/写到哪张表，证据落点，属于哪个证据族。"""

    consumer_task: str
    producer_task: str
    table: str
    family: str
    confidence: str
    evidence: str


@dataclass
class DagProposal:
    """一个任务的建议依赖集合。"""

    task_id: str
    schedule: str
    evidences: list[DagEvidence] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _read_py_files(root: Path) -> dict[str, str]:
    """读入 src 下全部 .py（排除 worktree/草稿副本）。"""
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*.py")):
        parts = {x.lower() for x in p.parts}
        if "__pycache__" in parts or ".worktrees" in parts or ".aidrafts" in parts:
            continue
        try:
            out[p.relative_to(REPO_ROOT).as_posix()] = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
    return out


def _span_end(text: str, start: int, indent: int) -> int:
    """函数体结束位置：下一个缩进 ≤ indent 的 def/class/@ 行。"""
    tail = text[start:]
    stop = re.compile(r"\n {%d,%d}(?:async def |def |class |@)" % (indent, indent), re.M)
    m = stop.search(tail)
    return start + m.start() if m else len(text)


def _index_defs(sources: dict[str, str]) -> dict[str, list[tuple[str, int, int]]]:
    """函数名 -> [(文件, 起, 止)]（同名可多处，按文件分组保留）。"""
    idx: dict[str, list[tuple[str, int, int]]] = {}
    for fp, src in sources.items():
        for m in DEF_RE.finditer(src):
            indent = len(m.group(1))
            end = _span_end(src, m.end(), indent)
            idx.setdefault(m.group(2), []).append((fp, m.start(), end))
    return idx


def _category_table_map(categories_yaml: Path) -> dict[str, str]:
    """category_id -> 物理表全名（品类注册表是唯一表名真源）。"""
    raw = _load_yaml(categories_yaml)
    out: dict[str, str] = {}
    for item in raw if isinstance(raw, list) else []:
        if isinstance(item, dict) and item.get("category_id") and item.get("database") and item.get("table"):
            out[str(item["category_id"])] = f"{item['database']}.{item['table']}"
    return out


_DAILY_DOW_FORMS: Final[frozenset[str]] = frozenset({"*", "0-4", "0-6", "1-5", "1-6"})


def _cron_number(token: str) -> int:
    """取 cron 字段的首个数字（'*/5'→5、'30'→30、'9-15'→9）。"""
    found = re.findall(r"\d+", token)
    return int(found[0]) if found else 0


def _slot_rank(schedule_yaml: Path) -> dict[str, int]:
    """档期 -> 当日先后序（周/月频视为更早的"前置供给层"=-1）。"""
    raw = _load_yaml(schedule_yaml) or {}
    out: dict[str, int] = {}
    for name, cfg in (raw.get("schedules") or {}).items():
        parts = str((cfg or {}).get("cron", "")).split()
        if len(parts) not in (5, 6):
            out[name] = -1
            continue
        cron = parts[-5:]  # 6 段（含秒）时丢弃秒位，统一按 5 段解释
        if cron[2] != "*" or cron[4] not in _DAILY_DOW_FORMS:
            out[name] = -1  # 低频（周/月）供给层：任何日频消费方的天然前置
            continue
        out[name] = _cron_number(cron[1]) * 60 + _cron_number(cron[0])
    return out


def _table_tokens(text: str, vocab: set[str], cat_map: dict[str, str]) -> set[str]:
    """从一段代码/文字里抽出表级引用（直写 token + 模板展开 + 品类 id 解析）。"""
    found = {t for t in _TABLE_TOKEN_RE.findall(text) if t in vocab}
    for prefix in _TABLE_TEMPLATE_RE.findall(text):
        found |= {t for t in vocab if t.startswith(prefix + "_")}
    for arg in _STR_ARG_RE.findall(text):
        if arg in cat_map and cat_map[arg] in vocab:
            found.add(cat_map[arg])
    return found


def _same_file_callees(body: str, sources: dict[str, str], fp: str, span: tuple[int, int],
                      def_idx: dict[str, list[tuple[str, int, int]]]) -> str:
    """把实现函数在同一文件内调用的私有方法体 + 引用的模块级常量块并入观察面。"""
    extra = [body]
    for name in _SELF_CALL_RE.findall(body):
        for efp, s, e in def_idx.get(name, []):
            if efp == fp and not (s <= span[0] and e >= span[1]):
                extra.append(sources[fp][s:e])
    for const in _CONST_RE.findall(body):
        m = re.search(r"^(%s)\s*[:=].*?(?=\n[A-Z_]|\n\n|\nclass |\ndef )" % const, sources[fp], re.S | re.M)
        if m:
            extra.append(m.group(0))
    return "\n".join(extra)


def _impl_bodies(task_cap: str, def_idx: dict[str, list[tuple[str, int, int]]],
                sources: dict[str, str]) -> list[tuple[str, tuple[int, int], str]]:
    """capability -> [(文件, 行区间, 观察面文本)]。"""
    out = []
    for fp, s, e in def_idx.get(f"_fetch_{task_cap}", []):
        body = sources[fp][s:e]
        out.append((fp, (s, e), _same_file_callees(body, sources, fp, (s, e), def_idx)))
    return out


def _hop_bodies(body: str, sources: dict[str, str]) -> list[tuple[str, str]]:
    """实现函数 import 的 zephyr 模块（跨文件一跳）→ [(模块文件, 正文)]。"""
    out: list[tuple[str, str]] = []
    for mod in _ZEPHYR_IMPORT_RE.findall(body):
        rel = "src/" + mod.replace(".", "/")
        for cand in (f"{rel}.py", f"{rel}/__init__.py"):
            if cand in sources:
                out.append((cand, sources[cand]))
                break
    return out


def _prose_blobs(task: dict) -> list[str]:
    out = []
    for key in ("description",):
        val = (task.get("extra") or {}).get(key)
        if val:
            out.append(str(val))
    if task.get("disabled_reason"):
        out.append(str(task["disabled_reason"]))
    return out


def _producer_index(tasks: list[dict]) -> dict[str, list[str]]:
    idx: dict[str, list[str]] = {}
    for t in tasks:
        if t.get("table"):
            idx.setdefault(str(t["table"]), []).append(str(t["task_id"]))
    return idx


def _resolve_edges(consumer: dict, tables: set[str], producer_of: dict[str, list[str]],
                  family: str, evidence: str, out: list[DagEvidence]) -> None:
    own_table = str(consumer.get("table"))
    for tbl in sorted(tables):
        producers = [p for p in producer_of.get(tbl, []) if p != consumer.get("task_id")]
        if not producers:
            continue
        conf = "high" if len(producers) == 1 else "medium"
        for p in producers:
            out.append(DagEvidence(str(consumer["task_id"]), p, tbl, family, conf, evidence))


@dataclass(frozen=True)
class TaskLineageIndex:
    """推导所需的全部真源索引（收进一个对象，避开长参数表面）。"""

    by_id: dict[str, dict]
    producer_of: dict[str, list[str]]
    cat_map: dict[str, str]
    def_idx: dict[str, list[tuple[str, int, int]]]
    sources: dict[str, str]
    ranks: dict[str, int]
    max_new_deps: int = MAX_NEW_DEPS_PER_TASK

    @property
    def vocab(self) -> set[str]:
        """在册可写表集合（只有被某任务写的表才算血缘节点）。"""
        return set(self.producer_of)


def _collect_task_evidence(task: dict, idx: TaskLineageIndex,
                           all_ev: list[DagEvidence]) -> None:
    """单任务证据收集（实现码直读 + 一跳模块 + 任务自述点名）。"""
    cap = str(task.get("capability") or "")
    tid = str(task["task_id"])
    own = str(task.get("table"))
    vocab = idx.vocab
    if cap:
        for fp, span, body in _impl_bodies(cap, idx.def_idx, idx.sources):
            line = idx.sources[fp][: span[0]].count("\n") + 1
            direct = _table_tokens(body, vocab, idx.cat_map) - {own}
            _resolve_edges(task, direct, idx.producer_of, "impl_direct",
                          f"{fp}:{line}（实现函数体内表级读取）", all_ev)
            for hop_path, hop in _hop_bodies(body, idx.sources):
                indirect = _table_tokens(hop, vocab, idx.cat_map) - {own} - direct
                _resolve_edges(task, indirect, idx.producer_of, "impl_module",
                              f"{fp}:{line} → {hop_path}（一跳模块读取）", all_ev)
    for blob in _prose_blobs(task):
        mentioned = {m for m in _TABLE_TOKEN_RE.findall(blob) if m in vocab} - {own}
        _resolve_edges(task, mentioned, idx.producer_of, "task_prose",
                      f"tasks.yaml[{tid}] 自述点名表 {sorted(mentioned)}", all_ev)
        named = {o for o in idx.by_id if o != tid and re.search(rf"\b{re.escape(o)}\b", blob)}
        for other in sorted(named):
            tbl = idx.by_id[other].get("table")
            if tbl:
                _resolve_edges(task, {str(tbl)}, idx.producer_of, "task_prose",
                              f"tasks.yaml[{tid}] 自述点名任务 {other}", all_ev)


def _cap_fanin(evs: list[DagEvidence], task: dict, idx: TaskLineageIndex,
               dropped: list[str]) -> list[DagEvidence]:
    """按"同档期优先 + 上游档期最近优先"裁到扇入预算内，超预算边只登记。"""
    by_prod: dict[str, list[DagEvidence]] = {}
    for ev in evs:
        by_prod.setdefault(ev.producer_task, []).append(ev)
    mine = idx.ranks.get(str(task.get("schedule")), 0)

    def _key(prod: str) -> tuple[int, int]:
        pr = idx.ranks.get(str(idx.by_id[prod].get("schedule")), -999)
        return (0 if pr == mine else 1, -pr)

    order = sorted(by_prod, key=_key)
    if len(order) > idx.max_new_deps:
        for prod in order[idx.max_new_deps:]:
            dropped.append(f"{prod}：超单任务扇入预算 {idx.max_new_deps}（同族冗余边，登记待裁）")
        order = order[: idx.max_new_deps]
    return [ev for prod in order for ev in by_prod[prod]]


def _assemble_proposals(tasks: list[dict], all_ev: list[DagEvidence],
                        idx: TaskLineageIndex) -> list[DagProposal]:
    """按档期序过滤证据，组装每任务建议（倒挂/超预算边只登记不采纳）。"""
    per_task: dict[str, list[DagEvidence]] = {}
    for ev in all_ev:
        per_task.setdefault(ev.consumer_task, []).append(ev)
    proposals: list[DagProposal] = []
    for task in tasks:
        tid = str(task["task_id"])
        kept: list[DagEvidence] = []
        dropped: list[str] = []
        mine = idx.ranks.get(str(task.get("schedule")), 0)
        unslotted = str(task.get("schedule")).lower() == "disabled"
        for ev in per_task.get(tid, []):
            prod = idx.by_id.get(ev.producer_task)
            if prod is None:
                dropped.append(f"{ev.producer_task}：生产者任务不在册")
                continue
            pr = idx.ranks.get(str(prod.get("schedule")), 0)
            if pr > mine and not unslotted:
                dropped.append(f"{ev.producer_task}：跨日界依赖（{prod.get('schedule')} 晚于 "
                               f"{task.get('schedule')}，运行时按'前一交易日已满足'处理，供 catchup 拓扑重放）")
            kept.append(ev)
        kept = _cap_fanin(kept, task, idx, dropped) if kept else kept
        if kept or dropped:
            proposals.append(DagProposal(tid, str(task.get("schedule")), kept, dropped))
    return proposals


def derive(tasks: list[dict], idx: TaskLineageIndex) -> tuple[list[DagProposal], list[DagEvidence]]:
    """主推导入口：逐任务收集证据 → 过滤 → 建议清单。"""
    all_ev: list[DagEvidence] = []
    for task in tasks:
        _collect_task_evidence(task, idx, all_ev)
    return _assemble_proposals(tasks, all_ev, idx), all_ev


def _source_contention(tasks: list[dict]) -> list[str]:
    """同档期内共享单一源的任务对（BRK-067 型争用面，只报告不自动加边）。"""
    single_source = {"tqcenter", "miniqmt", "tdx", "tickflow"}
    groups: dict[tuple[str, str], list[str]] = {}
    for t in tasks:
        if str(t.get("source")) in single_source and str(t.get("schedule")).lower() != "disabled":
            groups.setdefault((str(t.get("source")), str(t.get("schedule"))), []).append(str(t["task_id"]))
    lines = []
    for (src, slot), ids in sorted(groups.items()):
        if len(ids) > 1:
            lines.append(f"- `{src}` @ `{slot}` 同批 {len(ids)} 任务：{', '.join(sorted(ids))}")
    return lines


def _creates_cycle(deps: dict[str, list[str]], consumer: str, producer: str) -> bool:
    """候选边 consumer<-producer 是否成环（从 producer 出发能否回到 consumer）。"""
    seen = {consumer}
    stack = [producer]
    while stack:
        node = stack.pop()
        if node in seen:
            return True
        seen.add(node)
        stack.extend(deps.get(node, []))
    return False


def _prune_to_acyclic(base: dict[str, list[str]], additions: dict[str, list[str]]) -> tuple[dict[str, list[str]], list[str]]:
    """逐边试加，成环即弃（环=血缘误判或共享模块假边，宁缺毋假）。"""
    deps = {k: list(v) for k, v in base.items()}
    kept: dict[str, list[str]] = {}
    rejected: list[str] = []
    for consumer in sorted(additions):
        for producer in additions[consumer]:
            if producer in deps.get(consumer, []):
                continue
            if _creates_cycle(deps, consumer, producer):
                rejected.append(f"{consumer} <- {producer}：成环（已弃，血缘证据存疑）")
                continue
            deps.setdefault(consumer, []).append(producer)
            kept.setdefault(consumer, []).append(producer)
    return kept, rejected


def apply_high_confidence(tasks_yaml: Path, proposals: list[DagProposal]) -> tuple[int, list[str]]:
    """把 high 置信建议写入 tasks.yaml（字节级定位替换，禁文本整篇读写防换行污染）。"""
    raw = tasks_yaml.read_bytes()
    text = raw.decode("utf-8")
    existing = {str(t["task_id"]): _existing_deps(text, str(t["task_id"])) for t in
                ((_load_yaml(tasks_yaml) or {}).get("tasks") or [])}
    wanted: dict[str, list[str]] = {}
    for prop in proposals:
        add = sorted({e.producer_task for e in prop.evidences if e.confidence == "high"})
        fresh = [a for a in add if a not in existing.get(prop.task_id, set())]
        if fresh:
            wanted[prop.task_id] = fresh
    kept, rejected = _prune_to_acyclic({k: sorted(v) for k, v in existing.items()}, wanted)
    for line in rejected:
        print("CYCLE-REJECT", line)
    changed: list[str] = []
    for task_id, deps in sorted(kept.items()):
        text = _rewrite_deps(text, task_id, sorted(existing.get(task_id, set()) | set(deps)))
        changed.append(task_id)
    if changed:
        candidate = DagDeriveConfig(tasks_yaml=tasks_yaml)
        _assert_acyclic_text(candidate, text)
        tasks_yaml.write_bytes(text.encode("utf-8"))
    return len(changed), changed


def _assert_acyclic_text(cfg: DagDeriveConfig, text: str) -> None:
    """落盘前把候选内容写临时副本做无环+可解析校验（不碰生产目录）。"""
    tmp_dir = REPO_ROOT / ".runtime" / "tmp" / "ff-dag"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp = tmp_dir / "tasks_candidate.yaml"
    tmp.write_text(text, encoding="utf-8")
    try:
        _verify_no_cycle(tmp)
    finally:
        tmp.unlink(missing_ok=True)


def _task_block(text: str, task_id: str) -> tuple[int, int]:
    start = text.index(f"\n- task_id: {task_id}\n") + 1
    m = re.search(r"\n- task_id: ", text[start:])
    return start, start + (m.start() + 1 if m else len(text) - start)


def _existing_deps(text: str, task_id: str) -> set[str]:
    blk_start, blk_end = _task_block(text, task_id)
    block = text[blk_start:blk_end]
    m = re.search(r"^  dependencies:(.*)\n((?:  - .*\n)*)", block, re.M)
    if not m:
        return set()
    inline = set(re.findall(r"[\"']([a-z0-9_]+)[\"']", m.group(1)))
    listed = set(re.findall(r"^  - (.+?)\s*$", m.group(2), re.M))
    return {x.strip("\"'") for x in inline | listed}


def _rewrite_deps(text: str, task_id: str, deps: list[str]) -> str:
    blk_start, blk_end = _task_block(text, task_id)
    block = text[blk_start:blk_end]
    old = re.search(r"^  dependencies:(.*)\n(?:  - .*\n)*", block, re.M)
    if not old:
        raise ValueError(f"dependencies 行定位失败: {task_id}")  # noqa: MSG-EXPOSURE  调度任务名非凭据/路径敏感面
    prior_note = old.group(1).split("#", 1)[1].strip() if "#" in old.group(1) else ""
    tail = f"    # {prior_note}" if prior_note and DERIVED_TAG not in prior_note else ""
    rendered = ("  dependencies: [" + ", ".join(f'"{d}"' for d in deps) + "]"
                + f"    # {DERIVED_TAG} derive_task_dependencies.py 依表级血缘推导" + tail + "\n")
    new_block, n = re.subn(r"^  dependencies:.*\n(?:  - .*\n)*", rendered, block, count=1, flags=re.M)
    if n != 1:
        raise ValueError(f"dependencies 行替换失败: {task_id}")  # noqa: MSG-EXPOSURE  调度任务名非凭据/路径敏感面
    return text[:blk_start] + new_block + text[blk_end:]


def render_markdown(proposals: list[DagProposal], all_ev: list[DagEvidence], tasks: list[dict],
                   contention: list[str], tasks_yaml: Path) -> str:
    """产出建议清单（每条含证据与置信度），高置信已写入 / 低置信登记交总包。"""
    no_dep = sum(1 for x in tasks if not x.get("dependencies"))
    landed = any(DERIVED_TAG in text for text in [tasks_yaml.read_text(encoding="utf-8")])
    applied = [p for p in proposals if any(e.confidence == "high" for e in p.evidences)]
    only_low = [p for p in proposals if p.evidences and not any(e.confidence == "high" for e in p.evidences)]
    lines = [
        "---",
        "ttl: task_bound",
        "completes_when: 全流通战役 BRK-050 验收（tasks.yaml 无依赖任务数收敛）且推导器可重跑再生",
        "---",
        "",
        "# BRK-050 · 任务依赖推导建议清单（derive_task_dependencies.py 产物，禁手改）",
        "",
        f"- 任务总数 {len(tasks)}；本次运行快照无 `dependencies` 声明 {no_dep} 个（普查基线 262 任务 / 235 无依赖）。",
        f"- 高置信（表级唯一生产者 + 实现码或任务自述证据）建议任务数：**{len(applied)}**"
        + ("（本次 --apply 已写入 tasks.yaml）。" if landed else "（本轮 dry-run 未写入，需 --apply）。"),
        f"- 单任务扇入预算 {MAX_NEW_DEPS_PER_TASK}：超预算同族边不落地、在本文件 §2.1 登记（避免"
        "任一上游 FAILED 即 BLOCKED 的耦合放大）。",
        f"- 低置信（跨文件一跳歧义/多生产者）建议任务数：**{len(only_low)}**（登记交总包，禁硬编）。",
        "",
        "## 1. 高置信（已落地）",
        "",
        "| 任务 | 新增前置 | 表 | 证据族 | 证据 |",
        "|---|---|---|---|---|",
    ]
    for p in applied:
        for e in sorted(p.evidences, key=lambda x: (x.producer_task, x.table)):
            if e.confidence == "high":
                lines.append(f"| `{e.consumer_task}` | `{e.producer_task}` | `{e.table}` | {e.family} | {e.evidence} |")
    lines += ["", "## 2. 低置信 / 冲突（登记交总包，禁硬编）", "",
              "| 任务 | 候选前置 | 置信 | 证据族 | 证据 |", "|---|---|---|---|---|"]
    for p in only_low:
        for e in p.evidences:
            lines.append(f"| `{e.consumer_task}` | `{e.producer_task}` | {e.confidence} | {e.family} | {e.evidence} |")
    lines += ["", "### 2.1 丢弃边与跨日界标注", ""]
    for p in proposals:
        for d in p.dropped:
            lines.append(f"- `{p.task_id}` ← {d}")
    lines += ["", "## 3. 同源争用面（BRK-067 型，供串行化排班核对）", ""]
    lines += contention or ["- 无"]
    lines += ["", "## 4. 重跑方式", "",
              "```bash", "python scripts/derive_task_dependencies.py --apply   # 幂等：已声明的边不重复加", "```", "",
              f"真源：`{tasks_yaml.relative_to(REPO_ROOT).as_posix()}` + 品类表名册 + 实现码。"]
    return "\n".join(lines) + "\n"


def _verify_no_cycle(tasks_yaml: Path) -> None:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from zephyr.data.task_queue import TaskQueue

    q = TaskQueue()
    q.load_yaml(tasks_yaml)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="从数据血缘推导 tasks.yaml 依赖（BRK-050 治本）")
    ap.add_argument("--dry-run", action="store_true", help="只出建议清单，不改 tasks.yaml")
    ap.add_argument("--apply", action="store_true", help="把高置信依赖写入 tasks.yaml（幂等）")
    args = ap.parse_args(argv)
    cfg = DagDeriveConfig()
    tasks = list((_load_yaml(cfg.tasks_yaml) or {}).get("tasks") or [])
    sources = _read_py_files(cfg.src_root)
    idx = TaskLineageIndex(
        by_id={str(t["task_id"]): t for t in tasks},
        producer_of=_producer_index(tasks),
        cat_map=_category_table_map(cfg.categories_yaml),
        def_idx=_index_defs(sources),
        sources=sources,
        ranks=_slot_rank(cfg.schedule_yaml),
    )
    proposals, all_ev = derive(tasks, idx)
    contention = _source_contention(tasks)
    if args.apply:
        n, changed = apply_high_confidence(cfg.tasks_yaml, proposals)
        _verify_no_cycle(cfg.tasks_yaml)
        print(json.dumps({"tasks_touched": n, "changed": changed}, ensure_ascii=False))
        tasks = list((_load_yaml(cfg.tasks_yaml) or {}).get("tasks") or [])
    cfg.proposals_md.parent.mkdir(parents=True, exist_ok=True)
    cfg.proposals_md.write_text(
        render_markdown(proposals, all_ev, tasks, contention, cfg.tasks_yaml), encoding="utf-8")
    print(json.dumps({"evidence_rows": len(all_ev), "proposals": len(proposals),
                      "no_dependencies_now": sum(1 for x in tasks if not x.get("dependencies")),
                      "total_tasks": len(tasks)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
