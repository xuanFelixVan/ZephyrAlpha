# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/00_master_skeleton.md | W-102 第 1 把尺
# [MODULE] scripts.governance.data_supply.no_cache_endorsement
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.data_supply.strict_truth_reader, ast
# [CONSUMERS] scripts.governance.data_supply.check_wave3_rulers; [待登记] run_all.py / phase_manager.py 的 gate 缓存面（见 registration_needs.yaml）
# [STARTUP] imported
# [MATURITY] testing
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] permanent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 扫描目标缺失 -> raise CacheRulerSourceError（禁"扫不到=无违规"）
# [A_module] module_id=MOD-GOV-DS-NOCACHE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# noqa: m02-manual  M02豁免: 一次性 AST 扫描 + 双读探针，无常驻循环
"""W-102 第 1 把尺：**禁缓存背书**。

判据＝"用于下结论的读数，必须是当场读出来的"。两条腿，各自都能红：

  A. 结构腿（AST）：判据路径上的模块不得调用 fail-silent 读数通道
     （``ch_reader.query`` / ``ch_reader.count`` / ``ch_reader.inject_final``——三者失败分别
     返回 ""/0/原串，正是 W-180.1 点名的洗白面），也不得给判据函数套
     ``functools.lru_cache`` / ``functools.cache`` / ``GateCache``。
  B. 行为腿（双读探针）：同一参数连读两次，底层探针调用计数必须 +2；
     不增＝结果被缓存背书，尺红。这条腿是**运行时**证据，不依赖代码长相，
     因此装饰性"看着没缓存"的实现蒙不过去。

既有消费者面：门禁缓存宿主＝``scripts/governance/observability/gate_cache.py``
（[CONSUMERS] 实测在册 `phase_manager.py;run_all.py`）。本尺不修它、不复制它，
只保证**判据类读数**不从它或任何记忆化通道取数。
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

_VALDIR = str(Path(__file__).resolve().parent)
if _VALDIR not in sys.path:
    sys.path.insert(0, _VALDIR)
from strict_truth_reader import TruthReadError  # noqa: E402  CLONEGUARD合并:同族异常单一真源

FAIL_SILENT_CALLS = frozenset({"query", "count", "inject_final"})
FAIL_SILENT_HOSTS = frozenset({"ch_reader", "chwriter", "ch_writer"})
CACHE_DECORATORS = frozenset({"lru_cache", "cache", "cached_property"})
CACHE_SYMBOLS = frozenset({"GateCache", "gate_cache"})
STRICT_OK = frozenset({"query_rows", "count_strict", "inject_final_strict", "query_rows_table"})


class CacheRulerSourceError(TruthReadError):
    """扫描目标不存在——禁把"扫不到文件"当成"无违规"。

    CLONEGUARD 合并整改：details 载荷构造继承 TruthReadError（同族异常单一真源），本件删副本 __init__。"""


@dataclass(frozen=True)
class DataSupplyScanFinding:
    path: str
    lineno: int
    code: str
    detail: str


@dataclass(frozen=True)
class CacheVerdict:
    findings: tuple[DataSupplyScanFinding, ...]
    scanned_files: int
    probe_reads: int

    @property
    def ok(self) -> bool:
        return not self.findings


def _attr_chain(node: ast.AST) -> tuple[str, ...]:
    """Flatten ``a.b.c`` into ('a','b','c'); bare name into ('name',)."""
    if isinstance(node, ast.Attribute):
        return _attr_chain(node.value) + (node.attr,)
    if isinstance(node, ast.Name):
        return (node.id,)
    return ()


def _classify_call(node: ast.Call) -> DataSupplyScanFinding | None:
    chain = _attr_chain(node.func)
    if not chain:
        return None
    tail = chain[-1]
    if tail in STRICT_OK:
        return None
    if tail in FAIL_SILENT_CALLS and any(h in chain[:-1] for h in FAIL_SILENT_HOSTS):
        return DataSupplyScanFinding(
            "", node.lineno, "FAIL_SILENT_READ", f"判据路径调用 fail-silent 通道 {'.'.join(chain)}()（改走严格通道）"
        )
    if tail in CACHE_SYMBOLS or any(s in chain[:-1] for s in CACHE_SYMBOLS):
        return DataSupplyScanFinding(
            "", node.lineno, "GATE_CACHE_ON_JUDGMENT_PATH", f"判据路径引用缓存背书面 {'.'.join(chain)}"
        )
    return None


def _decorator_findings(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[DataSupplyScanFinding]:
    out: list[DataSupplyScanFinding] = []
    for dec in node.decorator_list:
        chain = _attr_chain(dec.func if isinstance(dec, ast.Call) else dec)
        if chain and chain[-1] in CACHE_DECORATORS:
            out.append(
                DataSupplyScanFinding(
                    "", node.lineno, "MEMOIZED_JUDGMENT_FUNC", f"判据函数 {node.name} 被套 {'.'.join(chain)}"
                )
            )
    return out


def scan_source(text: str, *, path: str) -> list[DataSupplyScanFinding]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [
            DataSupplyScanFinding(path, exc.lineno or 0, "UNPARSEABLE_SOURCE", f"AST 解析失败，禁默认放行: {exc.msg}")
        ]
    out: list[DataSupplyScanFinding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            found = _classify_call(node)
            if found:
                out.append(DataSupplyScanFinding(path, found.lineno, found.code, found.detail))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.extend(_decorator_findings(node))
    return out


def scan_files(paths: Iterable[Path]) -> tuple[list[DataSupplyScanFinding], int]:
    findings: list[DataSupplyScanFinding] = []
    counted = 0
    for path in paths:
        if not path.is_file():
            raise CacheRulerSourceError("扫描目标缺失", details={"path": str(path)})
        counted += 1
        findings.extend(scan_source(path.read_text(encoding="utf-8"), path=str(path)))
    return findings, counted


def default_scan_targets(root: Path) -> tuple[Path, ...]:
    pkg = root / "scripts" / "governance" / "data_supply"
    if not pkg.is_dir():
        raise CacheRulerSourceError(f"判据目录缺失: {pkg}")
    return tuple(sorted(p for p in pkg.glob("*.py") if p.name != Path(__file__).name))


def probe_live_reads(reader_factory) -> tuple[int, bool]:
    """B 行为腿：同参数连读两次，底层探针调用必须各发生一次（共 2 次）。"""
    import datetime as dt

    calls: list[str] = []

    def _probe(sql: str) -> Sequence[tuple[object, ...]]:
        calls.append(sql)
        return ((dt.date(2026, 1, 5),),) if "max(" in sql else ()

    reader = reader_factory(_probe)
    day = dt.date(2026, 1, 5)
    reader.read_leg("db.t", "trade_date", lo=day, hi=day)
    first = len(calls)
    reader.read_leg("db.t", "trade_date", lo=day, hi=day)
    second = len(calls) - first
    return len(calls), second > 0


def evaluate(root: Path, reader_factory) -> CacheVerdict:
    findings, scanned = scan_files(default_scan_targets(root))
    total_reads, live_on_reread = probe_live_reads(reader_factory)
    if not live_on_reread:
        findings.append(
            DataSupplyScanFinding("<probe>", 0, "CACHE_ENDORSED_REREAD", "同参数二次读数未触达底层通道——结论被缓存背书")
        )
    return CacheVerdict(tuple(findings), scanned, total_reads)


@dataclass(frozen=True)
class ControlResult:
    """负控制＝植入违规必点名；正控制＝干净源码不得误报（防"只会喊红的尺"）。"""

    ruler: str
    reddened: bool
    greened: bool
    codes: tuple[str, ...] = ()
    detail: str = ""
    observed_reads: int = 0

    @property
    def passed(self) -> bool:
        return self.reddened and self.greened


_CLEAN_SOURCE = "def n():\n    return 1\n"


def run_counterfactual() -> ControlResult:
    """反事实控制组：植一条 fail-silent 读数与一个记忆化 reader，尺必须红。"""
    poisoned = "from zephyr.data import ch_reader\n\ndef n():\n    return ch_reader.count('db.t')\n"
    hits = scan_source(poisoned, path="<control>/poisoned.py")
    memo = scan_source("import functools\n\n@functools.lru_cache\ndef n():\n    return 1\n", path="<control>/memo.py")
    codes = tuple(sorted({f.code for f in hits + memo}))
    clean = scan_source(_CLEAN_SOURCE, path="<control>/clean.py")
    total_reads, live = probe_live_reads(_default_reader_factory())
    return ControlResult(
        ruler="W-102_no_cache_endorsement",
        reddened=bool({"FAIL_SILENT_READ", "MEMOIZED_JUDGMENT_FUNC"} <= set(codes) and live),
        greened=not clean,
        codes=codes,
        detail=f"植入 ch_reader.count() 与 @lru_cache 两个反例须双双点名（实得 {list(codes)}）；干净源码误报 {len(clean)} 条；行为腿双读 live={live}",
        observed_reads=total_reads,
    )


def _default_reader_factory():
    from scripts.governance.data_supply.strict_truth_reader import StrictTruthReader

    return lambda probe: StrictTruthReader(projection=probe)
