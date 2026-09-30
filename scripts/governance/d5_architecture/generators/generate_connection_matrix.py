# [MODULE] scripts.governance.d5_architecture.generators.generate_connection_matrix
# create-guard-not-dup: TableProbe 已改名 MatrixTableProbe 消 CLASS-UNIQUENESS；本模块=全连接矩阵生成器（图族边面），非 foreign_market_coverage 第二实现
# [AI_AUTONOMY] ai_modifiable
# [SAFETY] L
# [STABILITY] stable
# [MODIFY-GUARD] schema-change（判据唯一真源=config/decision_map_loader 既有映射，禁擅改）
# [BLUEPRINT] MOD-GOV-114 | docs/03_modules/_domain_governance/blueprint.md
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.trading.decision_map（TDM 唯一 loader 真源，禁二次解析）; scripts.governance.d5_architecture.generators.check_decision_map（R9/R11 既有判据复用）; zephyr.governance.consumption.scan_scope_converged（§3.4 单一口径）; zephyr.data.ch_writer.get_client_strict（会抛错的行返回通道）; yaml; csv; argparse
# [CONSUMERS] scripts/governance/.../generate_connection_matrix.py --check（CI/自查）; src/zephyr/frontend/dashboard/components/connection_matrix.py（仪表盘数据源）; tests/governance/test_connection_matrix_rulers.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读输入（TDM/注册表/代码面）+ 只写两个产物（connection_matrix.csv 与其 JSON 兄弟）; TDM 解析唯一入口=load_decision_map; 状态四值封闭枚举，NO_DECLARED_EDGE 永不并入差集; ClickHouse 不可达永不折算成"0 行/表不存在"
# [ERROR_CONTRACT] run() 不吞异常（输入缺失/解析失败向上抛，main 折成 rc=2）; 单条边判定不得因外部通道失败而臆断（显式 read_channel 记录降级）
# [TESTS] tests/governance/test_connection_matrix_rulers.py
# [TTL] permanent
# [ARCH-REF] #ARCH-365 (包 13.4 / W-154)
# [CREATION-TOKEN] pending-registration: wave13-p3-matrix-20260926（总筹合批登记）
"""generate_connection_matrix.py — 全连接矩阵（数据源×因子×策略×决策地图）生成器。

大白话：把"谁该连谁"和"谁真的连上了"摆到同一张表上，逐条给证据，然后只数一个
头条数字——**该连未连**（应连性由在册声明成立、却查不到真接线）。猜出来的"该连"
不算数：任何一侧都没有声明字段的边一律进 NO_DECLARED_EDGE（声明缺失），单独记账。

六类边（波 13 §3.5）：
  data_source__collection_leg  SRC-* → JOB-*      数据源→采集腿
  collection_leg__table        JOB-* → db.table   采集腿→表
  table__factor                db.table → FCT-*   表→因子
  factor__strategy             FCT-* → STR-*      因子→策略
  strategy__tdm_node           STR-* → TDM-*      策略→决策地图节点
  tdm_node__execution_path     TDM-* → 文件路径    节点→执行路径

四态：WIRED / SHOULD_NOT_WIRED_BUT_ISN'T（差集，头条）/ MISSING_WIRING（指针悬空）
     / NO_DECLARED_EDGE（声明缺失，不入差集）。

用法::

    python scripts/governance/d5_architecture/generators/generate_connection_matrix.py
    ... --check            # rc=0 干净 / rc=1 差集非空或产物与重算不一致 / rc=2 工具故障
    ... --no-clickhouse    # 关掉 CH 强证据通道（默认开，不可达即降级并在 read_channel 披露）
    ... --out <csv> --json-out <json> --repo-root <dir>   # 测试/沙盘用
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Iterable

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

__all__: Final = [
    "STATES",
    "CSV_COLUMNS",
    "DIFFERENCE_STATE",
    "MatrixRow",
    "MatrixResult",
    "build_matrix",
    "render_csv",
    "to_json_payload",
    "check",
    "main",
]

# ===== 状态与列（封闭枚举，仪表盘与尺共用）=====

WIRED = "WIRED"
DIFFERENCE_STATE = "SHOULD_NOT_WIRED_BUT_ISN'T"
MISSING_WIRING = "MISSING_WIRING"
NO_DECLARED_EDGE = "NO_DECLARED_EDGE"
STATES: tuple[str, ...] = (WIRED, DIFFERENCE_STATE, MISSING_WIRING, NO_DECLARED_EDGE)

EDGE_TYPES: tuple[str, ...] = (
    "data_source__collection_leg",
    "collection_leg__table",
    "table__factor",
    "factor__strategy",
    "strategy__tdm_node",
    "tdm_node__execution_path",
)

#: 无对照侧的占位 id（声明侧缺口的行也要能被点名，但不能伪装成真实体）
NO_SOURCE = "SRC-NONE"
NO_TARGET = "TGT-NONE"

#: 声明字段存在、但其值域不是本边所需的轴（如 factor.inputs 存的是列名而非表名）时的
#: 标注词——机械可辨，用于自证断言的豁免面（见 _assert_self_consistency）
AXIS_MISMATCH = "[axis-mismatch]"

CSV_COLUMNS: tuple[str, ...] = (
    "edge_type",
    "source_id",
    "target_id",
    "declared_by",
    "wired_by",
    "state",
    "read_channel",
    "rule_id",
    "evidence_cmd",
)

_DEFAULT_CSV = _REPO_ROOT / "docs" / "_working" / "decision_map_campaign_20260924" / "connection_matrix.csv"
_DEFAULT_JSON = _REPO_ROOT / "data" / "runtime" / "connection_matrix" / "connection_matrix.json"
_TDM_PATH = _REPO_ROOT / "config" / "trading_decision_map.yaml"
_REGISTRY_DIR = _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
_DATA_TASKS = _REPO_ROOT / "src" / "zephyr" / "data" / "config" / "tasks.yaml"

_TDM_REL = "config/trading_decision_map.yaml"
_DAR_REL = "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml"
_FRR_REL = "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml"
_SRR_REL = "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"
_TASKS_REL = "src/zephyr/data/config/tasks.yaml"

#: §3.4 口径下真正要看的代码桶（E3/E4 的"已连侧"限定目录，越界即假绿）
_FACTOR_BUCKET = "src/zephyr/factor"
_STRATEGY_BUCKET = "src/zephyr/pf_core/strategies"

_TOKEN_RX = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*")


# ===== 产物结构 =====


@dataclass(frozen=True)
class MatrixRow:
    edge_type: str
    source_id: str
    target_id: str
    declared_by: str
    wired_by: str
    state: str
    read_channel: str
    rule_id: str
    evidence_cmd: str

    def as_csv_row(self) -> dict[str, str]:
        return {k: str(getattr(self, k)) for k in CSV_COLUMNS}


@dataclass
class MatrixResult:
    rows: list[MatrixRow] = field(default_factory=list)
    denominators: dict[str, dict[str, int]] = field(default_factory=dict)
    scope_stats: dict[str, int] = field(default_factory=dict)
    clickhouse: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, Any] = field(default_factory=dict)

    def count(self, state: str) -> int:
        return sum(1 for r in self.rows if r.state == state)

    @property
    def difference_set(self) -> list[MatrixRow]:
        return [r for r in self.rows if r.state == DIFFERENCE_STATE]

    def by_edge_type(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {et: {s: 0 for s in STATES} | {"total": 0} for et in EDGE_TYPES}
        for r in self.rows:
            out[r.edge_type][r.state] += 1
            out[r.edge_type]["total"] += 1
        return out

    def sorted_rows(self) -> list[MatrixRow]:
        return sorted(self.rows, key=lambda r: (EDGE_TYPES.index(r.edge_type), r.source_id, r.target_id))


# ===== §3.4 口径扫描索引（一遍扫完，多针共用；禁每类边各扫一遍全仓）=====


class ScopeIndex:
    """把"某符号在 §3.4 口径的哪个文件哪一行出现过"建成一次可用的索引。

    命中按桶（bucket）分别保留，桶外命中不算桶内证据——否则因子接线会被 config 里
    的一句注释判成已连（族① 假绿的同型病）。
    """

    _KEEP_PER_BUCKET = 4

    def __init__(self, repo_root: Path, needles: Iterable[str], buckets: Iterable[str] = ()) -> None:
        # 壬道收敛真源=consumption 子包（library_new_module_reconciler 同款指针）
        from zephyr.governance.consumption.scan_scope_converged import iter_scope_files

        self.repo_root = Path(repo_root)
        self.buckets = tuple(buckets)
        self._needles = {n for n in needles if n}
        self._dotted = {n for n in self._needles if "." in n}
        self._plain = self._needles - self._dotted
        hits: dict[tuple[str, str], list[tuple[str, int]]] = {}
        files_scanned = 0
        unreadable = 0
        for path in iter_scope_files(self.repo_root):
            rel = path.relative_to(self.repo_root).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                unreadable += 1
                continue
            files_scanned += 1
            bucket = self._bucket_of(rel)
            for line_no, line in enumerate(text.splitlines(), start=1):
                toks = set(_TOKEN_RX.findall(line))
                if not toks:
                    continue
                for tok in toks:
                    if tok in self._plain or tok in self._dotted:
                        key = (tok, bucket)
                        lst = hits.setdefault(key, [])
                        if len(lst) < self._KEEP_PER_BUCKET:
                            lst.append((rel, line_no))
                        other = (tok, "*")
                        olst = hits.setdefault(other, [])
                        if len(olst) < self._KEEP_PER_BUCKET:
                            olst.append((rel, line_no))
        self._hits = hits
        self.stats = {"scope_files_scanned": files_scanned, "scope_files_unreadable": unreadable}

    def _bucket_of(self, rel: str) -> str:
        for b in self.buckets:
            if rel == b or rel.startswith(b.rstrip("/") + "/"):
                return b
        return "*"

    def hits(self, needle: str, bucket: str | None = None) -> list[tuple[str, int]]:
        b = bucket if bucket is not None else "*"
        return list(self._hits.get((needle, b), []))

    def any_hit(self, needle: str, bucket: str | None = None) -> bool:
        return bool(self.hits(needle, bucket))


# ===== ClickHouse 强证据通道（会抛错、行返回；禁 ch_reader.query 下标直取）=====


@dataclass(frozen=True)
class MatrixTableProbe:
    """表实存读数：三态，绝不把"读失败"折算成"表不存在/0 行"。"""

    disposition: str  # present | absent | unreachable
    rows: int | None
    detail: str


class ClickHouseProber:
    """经 ch_writer.get_client_strict() 的 TCP 原生通道（execute 返回真行集，失败抛错）。

    契约 §2.2-4 红线：判据类 CH 读数禁 ch_reader.query()/ch_writer.query() 下标直取
    （二者返回 TSV 字符串且失败返回空串，r[0][0] 会取到首位数字、count() 失败返 0）。
    """

    _SQL_EXISTS = "SELECT count() FROM system.tables WHERE database = {db:String} AND name = {tbl:String}"

    def __init__(self, timeout: int = 5) -> None:
        self.timeout = timeout
        self.probes = 0
        self.unreachable = 0
        self._cache: dict[str, MatrixTableProbe] = {}

    def probe(self, entity: str) -> MatrixTableProbe:
        if "." not in entity:
            return MatrixTableProbe("absent", None, f"entity_name 无法拆成 db.table: {entity!r}")
        if entity in self._cache:
            return self._cache[entity]
        db, table = entity.split(".", 1)
        try:
            from zephyr.data.ch_writer import get_client_strict

            client = get_client_strict()
            rows = client.execute(self._SQL_EXISTS, {"db": db, "tbl": table})
        except Exception as exc:  # noqa: BLE001 — 不可达≠不存在，必须显式三态
            self.unreachable += 1
            probe = MatrixTableProbe("unreachable", None, f"CH 不可达（{type(exc).__name__}: {str(exc)[:120]}）")
        else:
            self.probes += 1
            n = int(rows[0][0]) if rows and rows[0] and rows[0][0] is not None else 0
            probe = MatrixTableProbe("present" if n > 0 else "absent", n, f"system.tables 命中 {n} 条")
        self._cache[entity] = probe
        return probe


# ===== 输入装载（全部经既有真源入口）=====


@dataclass
class MatrixInputs:
    repo_root: Path
    dm: Any
    sources: list[dict]
    datasets: list[dict]
    jobs: list[dict]
    factors: list[dict]
    strategies: list[dict]
    entity_map: dict[str, str]  # R11 通道复用（DS → CH entity_name）
    known_strategy_ids: frozenset[str]  # R3 通道复用（AST 代码 StrategyMeta）
    task_index: dict[str, TaskEntry]
    index: ScopeIndex
    prober: ClickHouseProber | None


def _registry_section(path: Path, key: str) -> list[dict]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [e for e in (raw.get(key) or []) if isinstance(e, dict)]


@dataclass(frozen=True)
class TaskEntry:
    """tasks.yaml 的一条采集任务（运行面的真注册证据：task_id + table + source）。"""

    task_id: str
    table: str
    source: str
    capability: str
    line: int | None


def _load_task_index(repo_root: Path, tasks_path: Path | None = None) -> dict[str, TaskEntry]:
    """采集腿运行注册面：tasks.yaml 的 task_id → 条目（含 table 轴与行号证据）。"""
    p = Path(tasks_path) if tasks_path else repo_root / "src" / "zephyr" / "data" / "config" / "tasks.yaml"
    out: dict[str, TaskEntry] = {}
    if not p.exists():
        return out
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()
    raw = yaml.safe_load(text) or {}
    tasks = raw.get("tasks") if isinstance(raw, dict) else raw
    for t in tasks or []:
        if not isinstance(t, dict) or not t.get("task_id"):
            continue
        tid = str(t["task_id"])
        line_no = next(
            (i for i, ln in enumerate(lines, start=1) if re.match(rf"^\s*-?\s*task_id:\s*{re.escape(tid)}\s*$", ln)),
            None,
        )
        out[tid] = TaskEntry(
            task_id=tid,
            table=str(t.get("table") or ""),
            source=str(t.get("source") or ""),
            capability=str(t.get("capability") or ""),
            line=line_no,
        )
    return out


def _collect_scope_needles(dm, datasets, sources, jobs, factors, strategies) -> set[str]:
    """§3.4 扫描词料收集（scope-grep 面的全部 needle：实体/源/腿/因子/策略/TDM 引用）。"""
    needles: set[str] = set()
    for ds in datasets:
        ent = str(ds.get("entity_name") or "")
        if ent:
            needles.add(ent)
            needles.add(ent.split(".")[-1])
    for e in list(sources) + list(jobs):
        for k in ("source_id", "job_id"):
            if e.get(k):
                needles.add(str(e[k]))
    for f in factors:
        if f.get("factor_id"):
            needles.add(str(f["factor_id"]))
    for s in strategies:
        if s.get("strategy_id"):
            needles.add(str(s["strategy_id"]))
    for n in dm.nodes:
        needles.update(n.factor_refs)
        needles.update(n.data_refs)
        for m in n.strategy_mounts:
            needles.add(m.strategy_ref)
    return needles


def build_inputs(
    repo_root: Path,
    *,
    map_path: Path | None = None,
    registry_dir: Path | None = None,
    tasks_path: Path | None = None,
    with_clickhouse: bool = True,
) -> MatrixInputs:
    """装载矩阵全部输入：TDM 必经 loader，R9/R11/R3 判据必经既有尺。"""
    from zephyr.trading.decision_map import load_decision_map

    root = Path(repo_root)
    rd = Path(registry_dir) if registry_dir else root / "docs/01_policies_and_standards/_registry/catalogs"
    dm = load_decision_map(Path(map_path) if map_path else root / "config/trading_decision_map.yaml")

    # R11 的 DS→表映射与 R3 的代码策略集=既有尺的判据面，直接复用（禁复制实现）
    from scripts.governance.d5_architecture.generators.check_decision_map import (
        _load_entity_map as r11_load_entity_map,
    )
    from scripts.governance.d5_architecture.generators.check_decision_map import (
        collect_strategy_ids_via_ast,
    )

    sources = _registry_section(rd / "data_asset_registry.yaml", "sources")
    datasets = _registry_section(rd / "data_asset_registry.yaml", "datasets")
    jobs = _registry_section(rd / "data_asset_registry.yaml", "jobs")
    factors = _registry_section(rd / "factor_registry.yaml", "factors")
    strategies = _registry_section(rd / "strategy_registry.yaml", "strategies")

    needles = _collect_scope_needles(dm, datasets, sources, jobs, factors, strategies)
    index = ScopeIndex(root, needles, buckets=(_FACTOR_BUCKET, _STRATEGY_BUCKET))
    prober = ClickHouseProber() if with_clickhouse else None
    return MatrixInputs(
        repo_root=root,
        dm=dm,
        sources=sources,
        datasets=datasets,
        jobs=jobs,
        factors=factors,
        strategies=strategies,
        entity_map=r11_load_entity_map(rd),
        known_strategy_ids=collect_strategy_ids_via_ast(root / "src" / "zephyr" / "pf_core"),
        task_index=_load_task_index(root, tasks_path),
        index=index,
        prober=prober,
    )


# ===== 证据串与行的构造助手 =====


def _grep_cmd(needle: str) -> str:
    return f"git grep -n -F {needle!r} -- src scripts config"


def _py_cmd(expr: str) -> str:
    return f'PYTHONPATH=src python -c "{expr}"'


def _row(edge_type: str, source_id: str, target_id: str, **fields: str) -> MatrixRow:
    """行构造守门员（§5.150 参数对象化：行字段经 **fields 透传 MatrixRow，调用点 kw 形态不变）。"""
    row = MatrixRow(edge_type=edge_type, source_id=source_id, target_id=target_id, **fields)
    if row.state not in STATES:  # 状态漂移=工具故障，宁炸不猜
        raise ValueError(f"未知状态: {row.state}")
    if row.declared_by == "NONE" and row.state in {WIRED, MISSING_WIRING, DIFFERENCE_STATE}:
        raise ValueError(f"无声明侧不得判成 {row.state}: {edge_type} {source_id}->{target_id}")
    return row


def _file_ref(root: Path, rel: str) -> str | None:
    """盘上实存性证据：文件 / 目录 / 点分模块 / path::symbol 四种在册写法都要认。

    写认不出＝把合法指针误判成悬空（假红），比漏判更贵，故四种形式逐个试。
    """
    if not rel:
        return None
    base = rel.split("::", 1)[0]
    root = Path(root)
    candidates = [base, base.rstrip("/")]
    if "." in base and "/" not in base and base.endswith(".py"):
        candidates.append(str(Path("src") / base.replace(".", "/")).replace("\\", "/"))
    if "." in base and "/" not in base and not base.endswith(".py"):  # 点分模块写法
        candidates.append(f"src/{base.replace('.', '/')}.py")
    for cand in candidates:
        p = root / cand
        if p.is_file():
            return f"{cand}:1" + (f"::{rel.split('::', 1)[1]}" if "::" in rel else "")
        if p.is_dir():
            return f"{cand}/:1"
    return None


def _hits_ref(hits: list[tuple[str, int]]) -> str:
    return "; ".join(f"{rel}:{ln}" for rel, ln in hits) or "NONE"


def _task_ref(tasks_rel: str, task: TaskEntry) -> str:
    loc = f"{tasks_rel}:{task.line}" if task.line else tasks_rel
    extra = ",".join(
        x
        for x in ((f"table={task.table}" if task.table else ""), (f"source={task.source}" if task.source else ""))
        if x
    )
    return f"{loc}#{task.task_id}" + (f"({extra})" if extra else "")


def _match_job_task(inp: MatrixInputs, job: dict, src_ref: str) -> TaskEntry | None:
    """采集腿的运行证据：tasks.yaml 里真登记了这条腿（四种在册对法，逐级放宽）。

    ① task_id 就是 job_id；② task_id 就是 job_name；③ task.table 落在该 job 声明
    outputs 的表上（最贴运行事实）；④ task_id 含代码文件 stem。都不中＝盘上没这条腿
    的注册面（差集候选，不是声明缺失——两侧声明都在）。
    """
    job_id = str(job.get("job_id") or "")
    job_name = str(job.get("job_name") or "")
    if job_id in inp.task_index:
        return inp.task_index[job_id]
    if job_name in inp.task_index:
        return inp.task_index[job_name]
    out_tables = {inp.entity_map.get(str(x)) or str(x) for x in (job.get("outputs") or [])}
    for t in inp.task_index.values():
        if t.table and t.table in out_tables:
            return t
    stem = Path(src_ref).stem
    if stem:
        for t in inp.task_index.values():
            if stem in t.task_id:
                return t
    return None


# ===== 六类边 =====


def _emit_e1_job_edge(inp: MatrixInputs, out: MatrixResult, job: dict) -> None:
    """E1 单 job 边判定：无源声明→ND-E1；代码指针悬空→MW-E1；task 轴零命中→SB-6；全中→W-E1。"""
    et = "data_source__collection_leg"
    job_id = str(job.get("job_id") or "")
    src_ref = str(job.get("source_code_ref") or "")
    outputs = {str(x) for x in (job.get("outputs") or [])}
    matched = [
        s
        for s in inp.sources
        if str(s.get("code_path") or "") == src_ref or outputs & {str(x) for x in (s.get("provides_datasets") or [])}
    ]
    if not matched:
        out.rows.append(
            _row(
                et,
                NO_SOURCE,
                job_id,
                declared_by="NONE",
                wired_by="NONE",
                state=NO_DECLARED_EDGE,
                read_channel="registry-only",
                rule_id="ND-E1",
                evidence_cmd=_grep_cmd(job_id),
            )
        )
        return
    src_id = str(matched[0].get("source_id") or "")
    declared = f"{_DAR_REL} sources[{src_id}].provides_datasets + jobs[{job_id}].source_code_ref"
    code_ref = _file_ref(inp.repo_root, src_ref) if src_ref else None
    if not code_ref:
        out.rows.append(
            _row(
                et,
                src_id,
                job_id,
                declared_by=declared,
                wired_by="NONE",
                state=MISSING_WIRING,
                read_channel="filesystem",
                rule_id="MW-E1",
                evidence_cmd=_py_cmd(f"from pathlib import Path;print(Path({src_ref!r}).exists())"),
            )
        )
        return
    task = _match_job_task(inp, job, src_ref)
    if task is None:
        out.rows.append(
            _row(
                et,
                src_id,
                job_id,
                declared_by=declared,
                wired_by=code_ref,
                state=DIFFERENCE_STATE,
                read_channel="filesystem+tasks.yaml(task=0)",
                rule_id="SB-6",
                evidence_cmd=_py_cmd(
                    f"import yaml;d=yaml.safe_load(open({_TASKS_REL!r},encoding='utf-8'));"
                    f"print([t['task_id'] for t in d['tasks'] if {job_id!r}==t.get('task_id')"
                    f" or t.get('table') in {sorted({inp.entity_map.get(x) or x for x in outputs})!r}])"
                ),
            )
        )
        return
    out.rows.append(
        _row(
            et,
            src_id,
            job_id,
            declared_by=declared,
            wired_by=f"{code_ref}; {_task_ref(_TASKS_REL, task)}",
            state=WIRED,
            read_channel="filesystem+tasks.yaml",
            rule_id="W-E1",
            evidence_cmd=_grep_cmd(task.task_id),
        )
    )


def _emit_e1_orphan_source_rows(inp: MatrixInputs, out: MatrixResult, src: dict, jobs_by_ds: dict) -> None:
    """E1 孤儿源判定：无 provides_datasets→ND-E1b；有声明但无 job 消费→SB-5。"""
    et = "data_source__collection_leg"
    src_id = str(src.get("source_id") or "")
    if not (src.get("provides_datasets") or []):
        out.rows.append(
            _row(
                et,
                src_id,
                NO_TARGET,
                declared_by="NONE",
                wired_by="NONE",
                state=NO_DECLARED_EDGE,
                read_channel="registry-only",
                rule_id="ND-E1b",
                evidence_cmd=_grep_cmd(src_id),
            )
        )
    elif not jobs_by_ds.get(str((src.get("provides_datasets") or [""])[0])):
        out.rows.append(
            _row(
                et,
                src_id,
                NO_TARGET,
                declared_by=f"{_DAR_REL} sources[{src_id}].provides_datasets",
                wired_by="NONE",
                state=DIFFERENCE_STATE,
                read_channel="registry-only",
                rule_id="SB-5",
                evidence_cmd=_py_cmd(
                    f"import yaml;d=yaml.safe_load(open({_DAR_REL!r},encoding='utf-8'));"
                    f"print(any({src_id!r} and {str((src.get('provides_datasets') or ['*'])[0])!r} in (j.get('outputs') or []) for j in d['jobs']))"
                ),
            )
        )


def build_data_source_to_job(inp: MatrixInputs, out: MatrixResult) -> None:
    """E1 数据源→采集腿：声明=data_asset_registry sources[].provides_datasets + jobs[].source_code_ref。"""
    jobs_by_ds: dict[str, list[dict]] = {}
    for job in inp.jobs:
        for ds in job.get("outputs") or []:
            jobs_by_ds.setdefault(str(ds), []).append(job)

    for job in inp.jobs:
        _emit_e1_job_edge(inp, out, job)

    for src in inp.sources:
        _emit_e1_orphan_source_rows(inp, out, src, jobs_by_ds)


def _emit_e2_dataset_edge(inp: MatrixInputs, out: MatrixResult, ds: dict) -> None:
    """E2 单 dataset 边判定：无 produced_by_job→ND-E2；CH absent→MW-E2；命中→W-E2；零命中→SB-4。"""
    et = "collection_leg__table"
    ds_id = str(ds.get("dataset_id") or "")
    entity = str(ds.get("entity_name") or "")
    job = str(ds.get("produced_by_job") or "")
    if not job:
        out.rows.append(
            _row(
                et,
                NO_SOURCE,
                f"{ds_id}({entity})",
                declared_by="NONE",
                wired_by="NONE",
                state=NO_DECLARED_EDGE,
                read_channel="registry-only",
                rule_id="ND-E2",
                evidence_cmd=_grep_cmd(ds_id),
            )
        )
        return
    declared = f"{_DAR_REL} datasets[{ds_id}].produced_by_job"
    table_token = entity.split(".")[-1]
    hits = inp.index.hits(entity) or inp.index.hits(table_token)
    # tasks.yaml 的 table 轴是最硬的"这条腿真写这张表"证据，排在 wired_by 首位
    task = next((t for t in inp.task_index.values() if t.table == entity), None)
    wired_parts = [x for x in ((_task_ref(_TASKS_REL, task) if task else ""), _hits_ref(hits)) if x and x != "NONE"]
    channel = "scope-grep(§3.4)+tasks.yaml"
    probe_note = ""
    absent_by_ch = False
    if inp.prober is not None and "." in entity:
        pr = inp.prober.probe(entity)
        probe_note = f" ch={pr.disposition}({pr.detail})"
        channel += "+clickhouse:system.tables"
        if pr.disposition == "absent":
            absent_by_ch = True
    if absent_by_ch:
        out.rows.append(
            _row(
                et,
                job,
                entity,
                declared_by=declared,
                wired_by="NONE",
                state=MISSING_WIRING,
                read_channel=channel,
                rule_id="MW-E2",
                evidence_cmd=_py_cmd(
                    f"from scripts.governance.d5_architecture.generators.generate_connection_matrix import ClickHouseProber as P;"
                    f"print(P().probe({entity!r}))"
                ),
            )
        )
        return
    if wired_parts:
        out.rows.append(
            _row(
                et,
                job,
                entity,
                declared_by=declared,
                wired_by="; ".join(wired_parts),
                state=WIRED,
                read_channel=channel + probe_note,
                rule_id="W-E2",
                evidence_cmd=_grep_cmd(table_token),
            )
        )
    else:
        out.rows.append(
            _row(
                et,
                job,
                entity,
                declared_by=declared,
                wired_by="NONE",
                state=DIFFERENCE_STATE,
                read_channel=channel + probe_note,
                rule_id="SB-4",
                evidence_cmd=_grep_cmd(table_token),
            )
        )


def _emit_e2_r11_dangling_rows(inp: MatrixInputs, out: MatrixResult) -> None:
    """R11 通道（复用 check_decision_map._load_entity_map 的 DS→CH 表映射）：
    TDM 声明了 data_refs 但映射不到任何在册表＝指针悬空，必判 MISSING_WIRING。
    注意与"CH 不可达"分开——不可达只降级披露，永不折算成"表不存在"。"""
    et = "collection_leg__table"
    for node in inp.dm.nodes:
        for ds in node.data_refs:
            if inp.entity_map.get(ds):
                continue
            out.rows.append(
                _row(
                    et,
                    f"TDM:{node.node_id}",
                    ds,
                    declared_by=f"{_TDM_REL} nodes[{node.node_id}].data_refs",
                    wired_by="NONE",
                    state=MISSING_WIRING,
                    read_channel="R11-channel(check_decision_map._load_entity_map)=no-mapping",
                    rule_id="MW-E2",
                    evidence_cmd=_grep_cmd(ds),
                )
            )


def build_job_to_table(inp: MatrixInputs, out: MatrixResult) -> None:
    """E2 采集腿→表：声明=datasets[].produced_by_job；已连=写表符号命中（+ CH 强证据）。"""
    for ds in inp.datasets:
        _emit_e2_dataset_edge(inp, out, ds)
    _emit_e2_r11_dangling_rows(inp, out)


def _factor_impl_files(inp: MatrixInputs, factor_id: str) -> list[tuple[str, int]]:
    """因子实现面：注册表 code_path 实存优先，其次 §3.4 口径的 FCT-* 命中（因子目录优先）。"""
    hits = inp.index.hits(factor_id, _FACTOR_BUCKET) or inp.index.hits(factor_id)
    return hits


def _emit_e3_proxy_edge(
    inp: MatrixInputs,
    out: MatrixResult,
    node,
    fct: str,
    ent: str,
    code_path_by_factor: dict,
    declared_pairs: set,
) -> None:
    """E3 代理边（TDM 同节点 data_refs × factor_refs）：无实现面→MW-E3；命中→W-E3；否则→SB-2。"""
    et = "table__factor"
    declared_pairs.add((fct, ent))
    token = ent.split(".")[-1] if "." in ent else ent
    fct_hits = _factor_impl_files(inp, fct)
    table_in_factor = inp.index.hits(ent, _FACTOR_BUCKET) or inp.index.hits(token, _FACTOR_BUCKET)
    if not fct_hits and not code_path_by_factor.get(fct):
        st, rule, wired = MISSING_WIRING, "MW-E3", "NONE"
    elif table_in_factor or (
        code_path_by_factor.get(fct)
        and _file_ref(inp.repo_root, code_path_by_factor[fct])
        and token in code_path_by_factor[fct]
    ):
        st, rule, wired = WIRED, "W-E3", _hits_ref(table_in_factor) or f"{code_path_by_factor[fct]}:1"
    else:
        st, rule, wired = DIFFERENCE_STATE, "SB-2", "NONE"
    out.rows.append(
        _row(
            et,
            ent or fct,
            fct,
            declared_by=f"{_TDM_REL} nodes[{node.node_id}].data_refs × factor_refs (proxy)",
            wired_by=wired,
            state=st,
            read_channel="scope-grep(§3.4:factor-bucket)",
            rule_id=rule,
            evidence_cmd=_grep_cmd(token or fct),
        )
    )


def _emit_e3_factor_decl_rows(
    inp: MatrixInputs, out: MatrixResult, f: dict, ds_ids: set, entities: set, proxy_declared_factors: set
) -> None:
    """E3 因子自声明行：factor.inputs 值域落在 dataset_id/entity_name 才算声明表轴（SB-2b），
    否则记轴错配/无声明（ND-E3）——禁猜该连。"""
    et = "table__factor"
    fct = str(f.get("factor_id") or "")
    if not fct or fct in proxy_declared_factors:
        return
    # factor.inputs 现存值=列名（close / limit_up_count…），逐条机械核：值域真的落在
    # dataset_id 或 entity_name 上才算声明了表轴，否则记 [axis-mismatch]——禁猜该连
    inputs = [str(x) for x in (f.get("inputs") or [])]
    table_decl = [i for i in inputs if i in ds_ids or i in entities]
    if table_decl:
        for ent in table_decl:
            out.rows.append(
                _row(
                    et,
                    ent,
                    fct,
                    declared_by=f"{_FRR_REL} factors[{fct}].inputs",
                    wired_by="NONE",
                    state=DIFFERENCE_STATE,
                    read_channel="scope-grep(§3.4:factor-bucket)",
                    rule_id="SB-2b",
                    evidence_cmd=_grep_cmd(ent.split(".")[-1] if "." in ent else ent),
                )
            )
        return
    out.rows.append(
        _row(
            et,
            NO_SOURCE,
            fct,
            declared_by="NONE" if not inputs else f"{_FRR_REL} factors[{fct}].inputs {AXIS_MISMATCH}",
            wired_by="NONE",
            state=NO_DECLARED_EDGE,
            read_channel="registry-only",
            rule_id="ND-E3",
            evidence_cmd=_grep_cmd(fct),
        )
    )


def build_table_to_factor(inp: MatrixInputs, out: MatrixResult) -> None:
    """E3 表→因子：注册表 inputs 只有列名（4/175）⇒ 代理声明=TDM 同节点 data_refs × factor_refs。"""
    code_path_by_factor = {str(f.get("factor_id")): str(f.get("code_path") or "") for f in inp.factors}
    declared_pairs: set[tuple[str, str]] = set()

    for node in inp.dm.nodes:
        if not node.data_refs or not node.factor_refs:
            continue
        tables = [inp.entity_map.get(ds, "") or ds for ds in node.data_refs]
        for fct in node.factor_refs:
            for ent in tables:
                _emit_e3_proxy_edge(inp, out, node, fct, ent, code_path_by_factor, declared_pairs)

    ds_ids = {str(d.get("dataset_id")) for d in inp.datasets}
    entities = {str(d.get("entity_name")) for d in inp.datasets}
    proxy_declared_factors = {fct for fct, _ in declared_pairs}
    for f in inp.factors:
        _emit_e3_factor_decl_rows(inp, out, f, ds_ids, entities, proxy_declared_factors)


def _emit_e4_mount_edges(inp: MatrixInputs, out: MatrixResult, node, mounted: set, declared_factors: set) -> None:
    """E4 代理边（TDM 同节点 factor_refs × strategy_mounts）：策略无实现→MW-E4；因子命中→W-E4；否则→SB-3。"""
    et = "factor__strategy"
    for mount in node.strategy_mounts:
        strat = mount.strategy_ref
        mounted.add(strat)
        impl = inp.index.hits(strat, _STRATEGY_BUCKET) or inp.index.hits(strat)
        for fct in node.factor_refs:
            declared_factors.add(fct)
            if not impl:
                st, rule, wired = MISSING_WIRING, "MW-E4", "NONE"
            elif inp.index.hits(fct, _STRATEGY_BUCKET):
                st, rule, wired = WIRED, "W-E4", _hits_ref(inp.index.hits(fct, _STRATEGY_BUCKET))
            else:
                st, rule, wired = DIFFERENCE_STATE, "SB-3", "NONE"
            out.rows.append(
                _row(
                    et,
                    fct,
                    strat,
                    declared_by=f"{_TDM_REL} nodes[{node.node_id}].factor_refs × strategy_mounts[{strat}].strategy_ref (proxy)",
                    wired_by=wired,
                    state=st,
                    read_channel="scope-grep(§3.4:strategy-bucket)",
                    rule_id=rule,
                    evidence_cmd=_grep_cmd(fct),
                )
            )


def _emit_e4_strategy_alpha_rows(
    inp: MatrixInputs, out: MatrixResult, s: dict, factor_ids: set, mounted: set, declared_factors: set
) -> None:
    """E4 策略自声明行：alpha_sources 值域真的是 FCT-*（在册 factor_id）才算声明（W-E4/SB-3b/MW-E4b），
    否则记轴错配/无声明（ND-E4）。"""
    et = "factor__strategy"
    sid = str(s.get("strategy_id") or "")
    if not sid or sid in mounted:
        return
    # 声明面双向都查：strategy.alpha_sources 与 factor.belongs_to_strategies
    # （实测 2/161 与 0/175 非空）——值域真的是 FCT-*/STR-* 才算声明了这条边
    alpha = [str(x) for x in (s.get("alpha_sources") or [])]
    fct_declared = [a for a in alpha if a in factor_ids]
    if fct_declared:
        impl = inp.index.hits(sid, _STRATEGY_BUCKET) or inp.index.hits(sid)
        for fct in fct_declared:
            declared_factors.add(fct)
            hits = inp.index.hits(fct, _STRATEGY_BUCKET)
            out.rows.append(
                _row(
                    et,
                    fct,
                    sid,
                    declared_by=f"{_SRR_REL} strategies[{sid}].alpha_sources",
                    wired_by=_hits_ref(hits),
                    state=WIRED if hits else (DIFFERENCE_STATE if impl else MISSING_WIRING),
                    read_channel="scope-grep(§3.4:strategy-bucket)",
                    rule_id="W-E4" if hits else ("SB-3b" if impl else "MW-E4b"),
                    evidence_cmd=_grep_cmd(fct),
                )
            )
        return
    out.rows.append(
        _row(
            et,
            "FCT-NONE",
            sid,
            declared_by="NONE" if not alpha else f"{_SRR_REL} strategies[{sid}].alpha_sources {AXIS_MISMATCH}",
            wired_by="NONE",
            state=NO_DECLARED_EDGE,
            read_channel="registry-only",
            rule_id="ND-E4",
            evidence_cmd=_grep_cmd(sid),
        )
    )


def _emit_e4_factor_belongs_rows(inp: MatrixInputs, out: MatrixResult) -> None:
    """E4 因子 belongs_to_strategies 自声明行（实测 0/175 常空）→SB-8 差集披露。"""
    et = "factor__strategy"
    for f in inp.factors:
        fct = str(f.get("factor_id") or "")
        owners = [str(x) for x in (f.get("belongs_to_strategies") or [])]
        if fct and owners:
            for sid in owners:
                out.rows.append(
                    _row(
                        et,
                        fct,
                        sid,
                        declared_by=f"{_FRR_REL} factors[{fct}].belongs_to_strategies",
                        wired_by="NONE",
                        state=DIFFERENCE_STATE,
                        read_channel="registry-only",
                        rule_id="SB-8",
                        evidence_cmd=_grep_cmd(fct),
                    )
                )


def _emit_e4_uncovered_factor_rows(inp: MatrixInputs, out: MatrixResult, declared_factors: set) -> None:
    """因子侧声明缺失（belongs_to_strategies 实测 0/175 + 无同节点代理）也要出行：
    只记策略侧＝175 个因子在 E4 里查无此行，"该连未连"与"没声明"就再也分不清（ND-E4b）。"""
    et = "factor__strategy"
    covered_factors = {
        r.source_id for r in out.rows if r.edge_type == et and r.declared_by != "NONE" and r.source_id != "FCT-NONE"
    }
    covered_factors |= declared_factors
    for f in inp.factors:
        fct = str(f.get("factor_id") or "")
        if not fct or fct in covered_factors:
            continue
        out.rows.append(
            _row(
                et,
                fct,
                NO_TARGET,
                declared_by="NONE"
                if not (f.get("belongs_to_strategies") or [])
                else f"{_FRR_REL} factors[{fct}].belongs_to_strategies {AXIS_MISMATCH}",
                wired_by="NONE",
                state=NO_DECLARED_EDGE,
                read_channel="registry-only",
                rule_id="ND-E4b",
                evidence_cmd=_grep_cmd(fct),
            )
        )


def build_factor_to_strategy(inp: MatrixInputs, out: MatrixResult) -> None:
    """E4 因子→策略：两侧注册表皆空（0/175、2/161）⇒ 只走 TDM strategy_mounts × factor_refs 代理。"""
    mounted: set[str] = set()
    declared_factors: set[str] = set()

    for node in inp.dm.nodes:
        if not node.factor_refs or not node.strategy_mounts:
            continue
        _emit_e4_mount_edges(inp, out, node, mounted, declared_factors)

    factor_ids = {str(f.get("factor_id")) for f in inp.factors}
    for s in inp.strategies:
        _emit_e4_strategy_alpha_rows(inp, out, s, factor_ids, mounted, declared_factors)

    _emit_e4_factor_belongs_rows(inp, out)
    _emit_e4_uncovered_factor_rows(inp, out, declared_factors)


def _emit_e5_mount_edge(
    inp: MatrixInputs, out: MatrixResult, node, mount, registry_ids: set, code_path_by_strategy: dict, mounted: set
) -> None:
    """E5 单挂载边：registry∪AST 双不可解析且零实现→MW-E5；§3.4 口径零命中→MW-E5b；否则→W-E5。"""
    et = "strategy__tdm_node"
    sid = mount.strategy_ref
    mounted.add(sid)
    declared = f"{_TDM_REL} nodes[{node.node_id}].strategy_mounts[].strategy_ref"
    resolvable = sid in registry_ids or sid in inp.known_strategy_ids
    impl = inp.index.hits(sid, _STRATEGY_BUCKET) or inp.index.hits(sid)
    cp = code_path_by_strategy.get(sid, "")
    if not resolvable and not impl:
        out.rows.append(
            _row(
                et,
                sid,
                node.node_id,
                declared_by=declared,
                wired_by="NONE",
                state=MISSING_WIRING,
                read_channel="R3-channel(registry ∪ AST StrategyMeta)",
                rule_id="MW-E5",
                evidence_cmd=_py_cmd(
                    f"print({sid!r} in __import__('yaml').safe_load(open({_SRR_REL!r},encoding='utf-8'))['strategies'][0])"
                ),
            )
        )
        return
    wired_by = "; ".join(
        x for x in (f"{cp}:1" if cp and _file_ref(inp.repo_root, cp) else "", _hits_ref(impl)) if x and x != "NONE"
    )
    if not wired_by:
        # 注册表/地图都说有这个策略，但 §3.4 口径内一行代码都找不到＝指针悬空
        out.rows.append(
            _row(
                et,
                sid,
                node.node_id,
                declared_by=declared,
                wired_by="NONE",
                state=MISSING_WIRING,
                read_channel="R3-channel(registry ∪ AST StrategyMeta)+scope-grep(§3.4)=0",
                rule_id="MW-E5b",
                evidence_cmd=_grep_cmd(sid),
            )
        )
        return
    out.rows.append(
        _row(
            et,
            sid,
            node.node_id,
            declared_by=declared,
            wired_by=wired_by,
            state=WIRED,
            read_channel="R3-channel(registry ∪ AST StrategyMeta)+scope-grep(§3.4)",
            rule_id="W-E5",
            evidence_cmd=_grep_cmd(sid),
        )
    )


def _emit_e5_unmounted_strategy_rows(inp: MatrixInputs, out: MatrixResult, mounted: set) -> None:
    """E5 孤儿策略行：注册表声明但地图零挂载→ND-E5（"没上地图"与"该连未连"分离）。"""
    et = "strategy__tdm_node"
    for s in inp.strategies:
        sid = str(s.get("strategy_id") or "")
        if sid and sid not in mounted:
            out.rows.append(
                _row(
                    et,
                    sid,
                    NO_TARGET,
                    declared_by="NONE",
                    wired_by="NONE",
                    state=NO_DECLARED_EDGE,
                    read_channel="registry-only",
                    rule_id="ND-E5",
                    evidence_cmd=_grep_cmd(sid),
                )
            )


def build_strategy_to_node(inp: MatrixInputs, out: MatrixResult) -> None:
    """E5 策略→TDM 节点：声明=nodes[].strategy_mounts[].strategy_ref，存在性走 R3 既有尺。"""
    registry_ids = {str(s.get("strategy_id")) for s in inp.strategies}
    code_path_by_strategy = {str(s.get("strategy_id")): str(s.get("code_path") or "") for s in inp.strategies}
    mounted: set[str] = set()

    for node in inp.dm.nodes:
        for mount in node.strategy_mounts:
            _emit_e5_mount_edge(inp, out, node, mount, registry_ids, code_path_by_strategy, mounted)

    _emit_e5_unmounted_strategy_rows(inp, out, mounted)


def build_node_to_execution_path(inp: MatrixInputs, out: MatrixResult) -> None:
    """E6 节点→执行路径：声明=nodes[].module_ref（文件路径值），实存性复用 R9 通道。"""
    et = "tdm_node__execution_path"
    for node in inp.dm.nodes:
        declared = f"{_TDM_REL} nodes[{node.node_id}].module_ref"
        if not node.module_ref:
            consumed_by = []
            if node.strategy_mounts:
                consumed_by.append("strategy_mounts")
            if node.data_refs:
                consumed_by.append("data_refs")
            if node.factor_refs:
                consumed_by.append("factor_refs")
            consumed_by_str = "+".join(consumed_by)
            out.rows.append(
                _row(
                    et,
                    node.node_id,
                    NO_TARGET,
                    # 应连性不来自 module_ref 自身（它就是缺的那侧），来自同节点的其他在册消费声明
                    declared_by="NONE" if not consumed_by else f"{_TDM_REL} nodes[{node.node_id}].{consumed_by_str}",
                    wired_by="NONE",
                    state=NO_DECLARED_EDGE if not consumed_by else DIFFERENCE_STATE,
                    read_channel="tdm-loader(zephyr.trading.decision_map)",
                    rule_id="ND-E6" if not consumed_by else "SB-1",
                    evidence_cmd=_py_cmd(
                        f"from zephyr.trading.decision_map import load_decision_map as L;"
                        f"print([n.module_ref for n in L(__import__('pathlib').Path({_TDM_REL!r})).nodes if n.node_id=={node.node_id!r}])"
                    ),
                )
            )
            continue
        ref = _file_ref(inp.repo_root, str(node.module_ref))
        if ref is None:
            out.rows.append(
                _row(
                    et,
                    node.node_id,
                    str(node.module_ref),
                    declared_by=declared,
                    wired_by="NONE",
                    state=MISSING_WIRING,
                    read_channel="filesystem",
                    rule_id="MW-E6",
                    evidence_cmd=_py_cmd(f"from pathlib import Path;print(Path({str(node.module_ref)!r}).exists())"),
                )
            )
            continue
        dep = _r9_depgraph_verdict(str(node.module_ref))
        out.rows.append(
            _row(
                et,
                node.node_id,
                str(node.module_ref),
                declared_by=declared,
                wired_by=ref,
                state=WIRED,
                read_channel=f"filesystem+R9(depgraph){dep}",
                rule_id="W-E6",
                evidence_cmd=_grep_cmd(Path(str(node.module_ref)).stem),
            )
        )


def _r9_depgraph_verdict(module_ref: str) -> str:
    """R9 既有尺（module_ref→depgraph 实存，PG fail-open）；不可达≠不存在，只披露。"""
    if not _R9_ENABLED:
        return "=skipped(--no-depgraph-r9)"
    try:
        from scripts.governance.d5_architecture.generators.check_decision_map import (
            _module_exists_in_depgraph,
        )

        return f"={_module_exists_in_depgraph(module_ref)}"
    except Exception as exc:  # noqa: BLE001 — R9 是增强通道，故障降级为披露
        return f"=skipped({type(exc).__name__})"


# ===== 组装 =====

_BUILDERS = (
    build_data_source_to_job,
    build_job_to_table,
    build_table_to_factor,
    build_factor_to_strategy,
    build_strategy_to_node,
    build_node_to_execution_path,
)


def build_matrix(
    repo_root: Path | None = None,
    *,
    map_path: Path | None = None,
    registry_dir: Path | None = None,
    with_clickhouse: bool = True,
    depgraph_r9: bool = False,
) -> MatrixResult:
    """跑全矩阵。depgraph_r9=False 时跳过 R9 的 PG 往返（测试/沙盘用，read_channel 明记）。"""
    root = Path(repo_root) if repo_root else _resolve_repo_root(map_path)
    inp = build_inputs(root, map_path=map_path, registry_dir=registry_dir, with_clickhouse=with_clickhouse)
    out = MatrixResult()
    out.scope_stats = dict(inp.index.stats)
    out.scope_stats.update({"needles": len(inp.index._needles)})  # noqa: SLF001 — 自检量
    out.inputs = {
        "tdm_nodes": len(inp.dm.nodes),
        "tdm_edges": len(inp.dm.edges),
        "data_asset_sources": len(inp.sources),
        "datasets": len(inp.datasets),
        "jobs": len(inp.jobs),
        "factors": len(inp.factors),
        "strategies": len(inp.strategies),
        "task_ids_in_tasks_yaml": len(inp.task_index),
    }
    global _R9_ENABLED
    _R9_ENABLED = depgraph_r9
    for builder in _BUILDERS:
        builder(inp, out)
    # CH 读数统计必须在跑完之后取（跑之前记=永远 0，等于把降级藏起来）
    if inp.prober is not None:
        out.clickhouse = {
            "channel": "ch_writer.get_client_strict()+execute(行返回)",
            "probes": inp.prober.probes,
            "unreachable": inp.prober.unreachable,
        }
    else:
        out.clickhouse = {"channel": "disabled(--no-clickhouse)", "probes": 0, "unreachable": 0}
    out.rows = _dedupe_rows(out.rows)
    out.denominators = out.by_edge_type()
    _assert_self_consistency(out)
    return out


def _merge_field(values: Iterable[str], cap: int = 8) -> str:
    uniq = sorted({v for v in values if v})
    if not uniq:
        return "NONE"
    shown = uniq[:cap]
    tail = f" |+{len(uniq) - cap}more" if len(uniq) > cap else ""
    return " || ".join(shown) + tail


def _dedupe_rows(rows: list[MatrixRow]) -> list[MatrixRow]:
    """同一 (边类, 源, 目标, 规则) 由多个节点/多条声明产生时合并成一行（声明源全留痕）。

    不合并＝同一根接线在差集里被数好几遍，头条数会虚高；合并＝声明面逐条可追。
    """
    groups: dict[tuple[str, str, str, str], list[MatrixRow]] = {}
    for r in rows:
        groups.setdefault((r.edge_type, r.source_id, r.target_id, r.rule_id), []).append(r)
    merged: list[MatrixRow] = []
    for (et, src, dst, rule), group in groups.items():
        states = {g.state for g in group}
        if len(states) > 1:
            raise AssertionError("connection matrix edge check failed (src/dst in details)")
        head = group[0]
        merged.append(
            _row(
                et,
                src,
                dst,
                declared_by=_merge_field(g.declared_by for g in group if g.declared_by != "NONE")
                if any(g.declared_by != "NONE" for g in group)
                else "NONE",
                wired_by=_merge_field(g.wired_by for g in group if g.wired_by != "NONE")
                if any(g.wired_by != "NONE" for g in group)
                else "NONE",
                state=head.state,
                read_channel=head.read_channel,
                rule_id=rule,
                evidence_cmd=head.evidence_cmd,
            )
        )
    return merged


_R9_ENABLED = False


def _resolve_repo_root(map_path: Path | None) -> Path:
    if map_path is not None:
        return Path(map_path).resolve().parents[1]
    return _REPO_ROOT


def _assert_self_consistency(out: MatrixResult) -> None:
    """机械自证：状态封闭枚举 + 行唯一 + 分母合计=行数 + 有声明源的行不得躲进"声明缺失"。"""
    seen: set[tuple[str, str, str, str]] = set()
    for r in out.rows:
        if r.state not in STATES:
            raise AssertionError(f"非法状态 {r.state}")
        key = (r.edge_type, r.source_id, r.target_id, r.rule_id)
        if key in seen:
            raise AssertionError(f"重复边行: {key}")
        seen.add(key)
        if (
            r.state == NO_DECLARED_EDGE
            and r.declared_by != "NONE"
            and "proxy" not in r.declared_by
            and AXIS_MISMATCH not in r.declared_by
        ):
            # 字段确实声明了这条边却记成"声明缺失"＝给红线留后门
            raise AssertionError(f"NO_DECLARED_EDGE 却带真声明源: {r.edge_type} {r.source_id}->{r.target_id}")
    per_type = {et: sum(1 for r in out.rows if r.edge_type == et) for et in EDGE_TYPES}
    out.denominators = {
        et: {s: sum(1 for r in out.rows if r.edge_type == et and r.state == s) for s in STATES}
        | {"total": per_type[et]}
        for et in EDGE_TYPES
    }
    if sum(v["total"] for v in out.denominators.values()) != len(out.rows):
        raise AssertionError("分母合计与行数不等（漏类或多类）")
    out.denominators["_all"] = {s: out.count(s) for s in STATES} | {
        "total": len(out.rows),
        "difference_set": out.count(DIFFERENCE_STATE),
        "declared_side_debt_rows": out.count(NO_DECLARED_EDGE),
    }


def render_csv(out: MatrixResult) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(CSV_COLUMNS), lineterminator="\n")
    w.writeheader()
    for r in out.sorted_rows():
        w.writerow(r.as_csv_row())
    return buf.getvalue()


def to_json_payload(out: MatrixResult) -> dict[str, Any]:
    """仪表盘数据源（读侧只见汇总+差集明细，全量行留在 CSV）。"""
    from zephyr.shared.utils.time_utils import now_utc  # 生成器禁 datetime.now()（RULE-SCHEMA-TZ）

    return {
        "ok": True,
        "generated_at": now_utc().isoformat(timespec="seconds"),
        "scope_ruling": "docs/_working/three_piece_infra/00_plan_and_ownership.md §3.4",
        "headline": {
            "difference_set_count": len(out.difference_set),
            "difference_state_label": DIFFERENCE_STATE,
            "no_declared_edge_count": out.count(NO_DECLARED_EDGE),
            "missing_wiring_count": out.count(MISSING_WIRING),
            "wired_count": out.count(WIRED),
            "total_rows": len(out.rows),
        },
        "denominators_by_edge_type": out.denominators,
        "inputs": out.inputs,
        "scope_stats": out.scope_stats,
        "clickhouse": out.clickhouse,
        "difference_set": [
            r.as_csv_row()
            for r in sorted(out.difference_set, key=lambda r: (EDGE_TYPES.index(r.edge_type), r.source_id, r.target_id))
        ],
        "missing_wiring": [
            r.as_csv_row()
            for r in sorted(out.rows, key=lambda r: (EDGE_TYPES.index(r.edge_type), r.source_id, r.target_id))
            if r.state == MISSING_WIRING
        ],
        "rows": [r.as_csv_row() for r in out.sorted_rows()],
    }


# ===== 校验模式（退出码钉死）=====

RC_CLEAN = 0
RC_DIFFERENCE = 1
RC_TOOL_FAILURE = 2


def check(
    csv_path: Path,
    *,
    repo_root: Path | None = None,
    map_path: Path | None = None,
    registry_dir: Path | None = None,
    with_clickhouse: bool = True,
    with_depgraph_r9: bool = True,
) -> tuple[int, dict[str, Any]]:
    """--check：rc=0 干净 / rc=1 差集非空或产物与重算不一致 / rc=2 工具故障。

    重算参数必须与生成时同档（否则 read_channel 漂移会被误判陈旧）——main() 里
    两者共用同一组 args 派生值。
    """
    report: dict[str, Any] = {}
    target = Path(csv_path)
    if not target.exists():
        return RC_TOOL_FAILURE, {"error": f"产物不存在: {target}"}
    try:
        out = build_matrix(
            repo_root,
            map_path=map_path,
            registry_dir=registry_dir,
            with_clickhouse=with_clickhouse,
            depgraph_r9=with_depgraph_r9,
        )
    except Exception as exc:  # noqa: BLE001 — 工具故障必须与判据红分开
        return RC_TOOL_FAILURE, {"error": f"{type(exc).__name__}: {exc}"}
    expected = render_csv(out)
    actual = target.read_text(encoding="utf-8")
    stale = actual != expected
    report["artifact_stale"] = stale
    report["denominators"] = out.denominators
    report["difference_set_count"] = len(out.difference_set)
    if stale:
        report["inconsistency"] = "CSV 与重算不等（产物陈旧或被手改）——生成物禁手改"
        return RC_DIFFERENCE, report
    if out.difference_set:
        report["difference_set"] = [
            f"{r.edge_type}:{r.source_id}->{r.target_id}[{r.rule_id}]" for r in out.difference_set[:50]
        ]
        return RC_DIFFERENCE, report
    return RC_CLEAN, report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="全连接矩阵生成器（波 13 包 13.4 / W-154）")
    ap.add_argument("--out", type=Path, default=_DEFAULT_CSV, help="CSV 产物路径")
    ap.add_argument("--json-out", type=Path, default=_DEFAULT_JSON, help="JSON 兄弟产物路径（仪表盘数据源）")
    ap.add_argument("--repo-root", type=Path, default=None)
    ap.add_argument("--map-path", type=Path, default=None)
    ap.add_argument("--registry-dir", type=Path, default=None)
    ap.add_argument("--no-clickhouse", action="store_true", help="关闭 CH 强证据通道")
    ap.add_argument("--no-depgraph-r9", action="store_true", help="关闭 R9 depgraph PG 往返（沙盘/离线自证用）")
    ap.add_argument("--check", action="store_true", help="校验模式（退出码见模块头）")
    ap.add_argument("--print-summary", action="store_true")
    args = ap.parse_args(argv)

    ch = not args.no_clickhouse
    r9 = not args.no_depgraph_r9
    try:
        if args.check:
            rc, report = check(
                args.out,
                repo_root=args.repo_root,
                map_path=args.map_path,
                registry_dir=args.registry_dir,
                with_clickhouse=ch,
                with_depgraph_r9=r9,
            )
            print(json.dumps({"rc": rc, **report}, ensure_ascii=False, indent=2))
            return rc
        out = build_matrix(
            args.repo_root,
            map_path=args.map_path,
            registry_dir=args.registry_dir,
            with_clickhouse=ch,
            depgraph_r9=r9,
        )
        write_artifacts(out, args.out, args.json_out)
    except Exception as exc:  # noqa: BLE001 — 工具故障=rc=2，绝不与判据红混报
        print(f"TOOL_FAILURE {type(exc).__name__}: {exc}", file=sys.stderr)
        return RC_TOOL_FAILURE

    if args.print_summary:
        print(json.dumps(to_json_payload(out)["headline"], ensure_ascii=False, indent=2))
    print(f"CSV: {args.out}\nJSON: {args.json_out}")
    return RC_CLEAN


def write_artifacts(out: MatrixResult, csv_path: Path, json_path: Path | None) -> None:
    """产物落盘（CSV 是永久仪表盘数据源，JSON 是读侧缓存）。"""
    from zephyr.shared.io.file_utils import safe_write_text

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(csv_path, render_csv(out))
    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        safe_write_text(json_path, json.dumps(to_json_payload(out), ensure_ascii=False, indent=1))


# noqa: m11-perm-manual-legitimate  M11豁免: 本件=双通道件——①判据件消费面=tests/governance/test_connection_matrix_rulers.py import+设计 CI --check 自查 subprocess 调用（非 cron/daemon/非常驻服务）②人工再生 CLI=会话显式触发；MANUAL-ONLY 启发式对 argv/argparse 的误判与 generate_manifest.py 同款豁免先例（2026-09-30 landing 死因 MANUAL-ONLY-PERMANENT 治本，8454beec5a）
if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
