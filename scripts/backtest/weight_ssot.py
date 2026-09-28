"""配比真源单头化机械闸（W3-F 施工，R-M2-6：pf_alloc=生效，auto_mount=只提名）。

大白话：一条钱的分法只能有一个"说话算数的人"。以前 auto_mount 和 pf_alloc 都在
给同一个权重定数，事后从落库行看不出到底是谁说的（不可归因）。本件把"谁提名、
谁生效"写死成机器可查的一张表，并提供两把尺：提名越权=拒；两处同时写同一权重=报。

# [MODULE] backtest.weight_ssot
# [TTL] permanent
# [DOMAIN] D_BACKTEST
# [BLUEPRINT] MOD-BACKTEST | docs/03_modules/_domain_backtest/blueprint.md | §R-M2-6 配比真源单头化（模块册 module_id=backtest.weight_ssot；depgraph 设计态 node=15320908 PLACEHOLDER-R-M2-6，蓝图编号待收编）
# [MATURITY] trial
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M（权柄判定面=资金分配邻接；自身纯文本扫描零资金副作用，禁接下单/调仓链路）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fail-closed：出参缺权重字段/未知权级/生效面多头/写手记录不完整/作者未声明写作字段/源不可读 -> WeightAuthorityError；未登记路径=WILD_WRITER（attributable=False 计入 conflicts，不抛错不隐身）
# [TESTS] tests/backtest/test_weight_ssot_single_authority.py
# [DEPENDENCIES] 仅 stdlib（re/pathlib/dataclasses/typing/collections）——刻意零业务依赖（完整标注见文末 [DEPENDENCIES] 段）
# [STARTUP] manual
# [CONSUMERS] scripts/backtest/auto_mount.py（写图前权柄闸）；tests/backtest/test_weight_ssot_single_authority.py
# [INVARIANTS]
  ① 本模块**只判权、不产数**：绝不生成/修改任何权重数值，绝不触碰风险平价、
     cap/step、再平衡带宽等任何判据（改数值=改判据禁区）；
  ② 生效权单值：EFFECTIVE_AUTHORITY 只有一个（pf_alloc），第二个人说"生效"即冲突；
  ③ 提名≠生效：带 weight 但缺 binding 标记的出参一律判不可归因并拒绝（禁默认生效）；
  ④ fail-closed：扫描读不到源文件/真源字段拼不出=报错，不静默放行；
  ⑤ 零资金副作用：全模块纯文本+映射运算，禁 import 任何下单/调仓/撮合链路
     （本车道离真实资金分配最近，资金破坏性操作=Owner 门位）。
  ⑥ 作者真源在本文件内（WEIGHT_PRODUCERS），不新增注册表册（净零纪律：
     docs/01.../catalogs/** 是热册，改它须走 safe_write_text 与总筹单点）。
  ⑦ 认不出作者≠没有写手：未登记路径一律判 WILD_WRITER（attributable=False 且计入
     conflicts），禁回 None 隐身——rb2_guard_attacks §三.4 点名的最大结构性逃生。
     副作用即收益：谁把 PRODUCER_PATH_KEYS 里自己的路径键改成别名玩"自隐身"，
     它的写点立刻以野生身份被 census 抓住。

# [DEPENDENCIES] 仅 stdlib（re/pathlib/dataclasses/typing/collections）——刻意零业务依赖，
  使 auto_mount 与测试可在无 DB/无 CH 环境下调用本闸。
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

# ---------- 权级词表（封闭集，勿另立） ----------

BINDING_EFFECTIVE: str = "effective"  # 说话算数：进落库/进真源的那一路
BINDING_NOMINATION: str = "nomination"  # 只提名：可参考，不可直接生效
BINDINGS: tuple[str, ...] = (BINDING_EFFECTIVE, BINDING_NOMINATION)

EFFECTIVE_AUTHORITY: str = "pf_alloc"  # 唯一配比真源（R-M2-6 裁定）

#: 提名面（auto_mount 挂图写这里——R-M2-6 之后它只是"先验/提名"，不是权威）
NOMINATION_FIELD: str = "portfolio_plan.sleeves[].weight"
#: 生效面（pf_alloc 落库写这里——唯一说话算数的配比结果）
EFFECTIVE_FIELD: str = "alloc_budget_daily.weight"
#: 兼容旧称（历史文档/06 册按"权重字段"引用本案病根坐标）
WEIGHT_FIELD: str = NOMINATION_FIELD

#: 作者→权级声明真源（auto_mount 降为提名即在此生效）
WEIGHT_PRODUCERS: dict[str, str] = {
    "pf_alloc": BINDING_EFFECTIVE,
    "auto_mount": BINDING_NOMINATION,
}

#: 作者→其实际写作的字段（两个作者写同一个字段=不可归因；写不同字段=分层合法）
PRODUCER_FIELDS: dict[str, str] = {
    "auto_mount": NOMINATION_FIELD,
    "pf_alloc": EFFECTIVE_FIELD,
}

#: 生产真源/落库面的物理路径特征（扫描用来认人）
PRODUCER_PATH_KEYS: dict[str, tuple[str, ...]] = {
    "pf_alloc": ("src/zephyr/pf_alloc/",),
    "auto_mount": ("scripts/backtest/auto_mount.py",),
}

#: 权重作者位的写手感（file:line 可复核；两条以上同字段=不可归因）
_WRITE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("sleeve_write_literal", r"weight:\s*\{?"),  # f-string 直写 weight: 到地图文本
    ("sleeve_rescale", r"\bweight\b\s*[:=]"),  # 原位改写 weight 字段
    ("alloc_persist", r"write_budget_daily|alloc_budget_daily|target_weight"),
)

_WEIGHT_KEY_RE = re.compile(r"(?<![A-Za-z_])weight\b")

#: 未登记作者的占位名。修前形态＝`classify_path` 认不出人回 None，调用方一律跳过
#: ⇒ 野生权重写手在这台尺上**隐身**（rb2_guard_attacks §三.4 点名的最大结构性逃生，
#: 连"把自己在 PRODUCER_PATH_KEYS 里的键改成别名"这种自隐身，修后都会立刻现形为 wild）。
#: 铁律：认不出人≠没有写手，一律 WILD_WRITER → attributable=False → 计入 conflicts。
WILD_WRITER: str = "<wild-writer>"

#: 野生写手判据指纹（沿用 discover_weight_writers 的严判据：同一行既要出现归因键
#: strategy_ref 又要出现 weight 写入形状）。宽判据 `_WRITE_PATTERNS` 用在未登记文件上
#: 会把全仓 `weight = 0.5` 的局部变量都算成写手＝噪音→告警疲劳→被拔线（BRK-046 教训同族），
#: 故扫描口径在 census 里以 wild_scan_dirs 如实披露，不装作全仓无死角。
_WILD_WEIGHT_RE = re.compile(r"weight\s*[:=]")


class WeightAuthorityError(RuntimeError):
    """权级越权/不可归因（fail-closed 契约错，非资金动作）。"""


def binding_of(producer: str) -> str:
    """查作者权级；未登记作者=拒绝（禁凭记忆放行新写手）。"""
    try:
        return WEIGHT_PRODUCERS[producer]
    except KeyError as exc:
        raise WeightAuthorityError(
            f"未登记的权重作者 {producer!r}（须先入 WEIGHT_PRODUCERS 声明权级；已登记={sorted(WEIGHT_PRODUCERS)}）"
        ) from exc


# ---------- 提名面（只加标记，永不改数） ----------


def make_nomination(
    rows: Iterable[Mapping[str, Any]], *, produced_by: str, weight_key: str = "weight"
) -> list[dict[str, Any]]:
    """把出参整批打上**提名级**标记：只在原行上追加权级字段，数值与其余键逐位原样透传。

    禁改判据的实现约束：本函数不归一、不截断、不 round、不排序重分配、不删键
    （调用方要动数值请自己去过 Owner 门）。
    """
    binding = binding_of(produced_by)
    out: list[dict[str, Any]] = []
    for r in rows:
        if weight_key not in r:
            raise WeightAuthorityError(f"出参缺 {weight_key} 字段，无法定权级（不可归因）: {sorted(r)}")
        merged = dict(r)  # 原行全键透传（stage/signal_weight/capacity 等既有契约不动）
        merged.update(
            {
                "producer": produced_by,
                "binding": binding,
                "authority": produced_by,
                "effective": binding == BINDING_EFFECTIVE,
            }
        )
        out.append(merged)
    return out


def assert_nomination_not_binding(
    payload: Iterable[Mapping[str, Any]], *, strict_present: bool = True
) -> list[dict[str, Any]]:
    """红测尺一：提名面被拒／生效面只剩一条路径。

    - 带 weight 却无 binding 标记 → 不可归因 → 拒（strict_present=True，生产默认）；
    - binding=effective 且作者 ≠ EFFECTIVE_AUTHORITY → 越权 → 拒；
    - 一批里出现两个不同的 effective 作者 → 双头 → 拒。
    返回通过的行（原样，不改数值），便于调用方直接续用。
    """
    rows = list(payload)
    effective_authors: set[str] = set()
    for r in rows:
        if "weight" not in r:
            continue
        binding = r.get("binding")
        authority = str(r.get("authority") or r.get("producer") or "")
        if binding is None:
            if strict_present:
                raise WeightAuthorityError(f"提名未标记权级（不可归因，禁默认生效）: {r.get('strategy_ref') or r}")
            continue
        if binding not in BINDINGS:
            raise WeightAuthorityError(f"未知权级 {binding!r}（合法={list(BINDINGS)}）")
        if binding == BINDING_EFFECTIVE:
            if authority != EFFECTIVE_AUTHORITY:
                raise WeightAuthorityError(
                    f"提名越权改生效：{authority!r} 声明 effective，而生效权唯一归属 {EFFECTIVE_AUTHORITY!r}（R-M2-6）"
                )
            effective_authors.add(authority)
    if len(effective_authors) > 1:
        raise WeightAuthorityError(f"生效面出现多头：{sorted(effective_authors)}")
    return rows


# ---------- 病根判据：两处同时写同一权重 ----------


def _group_write_intents(
    write_intents: Iterable[Mapping[str, Any]], *, field: str | None = None
) -> tuple[dict[tuple[str, str], set[str]], dict[tuple[str, str], list[str]]]:
    """写手意图归口分组（COMPLEXITY-GUARD 治本：自 find_weight_writer_conflicts 拆出，行为等价）。

    分组键=(field, strategy_ref)；缺 field 者按 field 参数（再缺省=WEIGHT_FIELD）归口。
    """
    by_key: dict[tuple[str, str], set[str]] = defaultdict(set)
    sites_by_key: dict[tuple[str, str], list[str]] = defaultdict(list)
    for w in write_intents:
        producer = str(w.get("producer") or "")
        ref = str(w.get("strategy_ref") or "")
        if not producer or not ref:
            raise WeightAuthorityError(f"写手记录不完整（producer/strategy_ref 必填）: {w}")
        if producer != WILD_WRITER:
            binding_of(producer)  # 凭空造一个作者名仍先拒；WILD_WRITER 是"没登记"的占位，不查表
        f = str(w.get("field") or field or WEIGHT_FIELD)
        by_key[(f, ref)].add(producer)
        for site in w.get("sites") or []:
            sites_by_key[(f, ref)].append(str(site))
    return by_key, sites_by_key


def find_weight_writer_conflicts(
    write_intents: Iterable[Mapping[str, Any]], *, field: str | None = None
) -> list[dict[str, Any]]:
    """红测尺二：同一字段上的同一权重被两处作者写=探出（本案病根，不可归因即为此形）。

    write_intents: [{"producer": str, "strategy_ref": str, "field": str(可选)}, ...]
    缺 field 者按 field 参数（再缺省=WEIGHT_FIELD）归口；分组键=(field, strategy_ref)，
    故"提名写 PP-001、生效写 alloc 表"的分层写法不算冲突，而"两头挤同一字段"必报。
    返回冲突列表（含全部作者、是否多头生效、是否可归因）。
    """
    by_key, sites_by_key = _group_write_intents(write_intents, field=field)
    conflicts: list[dict[str, Any]] = []
    for (f, ref), authors in sorted(by_key.items()):
        wild = WILD_WRITER in authors
        if len(authors) < 2 and not wild:
            continue  # 单人且登记=合法单头
        named = sorted(a for a in authors if a != WILD_WRITER)
        eff = [a for a in named if WEIGHT_PRODUCERS[a] == BINDING_EFFECTIVE]
        nom = [a for a in named if WEIGHT_PRODUCERS[a] == BINDING_NOMINATION]
        conflicts.append(
            {
                "strategy_ref": ref,
                "field": f,
                "writers": sorted(authors),
                "effective_writers": eff,
                # 两个"说话算数的人"同时写=多头生效（最恶性）
                "multi_effective": len(eff) > 1,
                # 提名作者挤进生效字段=越权（本案 R-M2-6 的原始形态：auto_mount 要 pf_alloc 别算了）
                "nomination_overreach": bool(f == EFFECTIVE_FIELD and nom),
                # 野生写手（未登记作者）：哪怕只有它一个人也算冲突——它没登记＝没人有权写
                "wild_writers": wild,
                "wild_writer_sites": sorted(set(sites_by_key.get((f, ref), []))),
                "attributable": False,  # 双写即不可归因，与是否数值相同无关
            }
        )
    return conflicts


def assert_single_effective_writer(write_intents: Iterable[Mapping[str, Any]], *, field: str | None = None) -> None:
    """写图前的 fail-closed 闸：任一权重字段被两处写=当场拒（含"提名+生效"混写、含野生写手）。"""
    conflicts = find_weight_writer_conflicts(write_intents, field=field)
    if conflicts:
        detail = "; ".join(
            f"{c['field']}::{c['strategy_ref']}<-{'+'.join(c['writers'])}"
            + ("（多头生效）" if c["multi_effective"] else "")
            + ("（提名与生效并写）" if c["nomination_overreach"] else "")
            + (f"（野生写手 {len(c['wild_writer_sites'])} 处未登记）" if c["wild_writers"] else "")
            for c in conflicts
        )
        raise WeightAuthorityError(
            f"配比真源双头：{len(conflicts)} 处并写同一权重 -> {detail}"
            "；生效权唯一归 pf_alloc，提名侧（auto_mount）不得同时落生效值，"
            "未登记作者一律先登记权级再谈写权"
        )


def field_writer_map(producers: Iterable[str] | None = None) -> dict[str, set[str]]:
    """字段→作者集合（按 PRODUCER_FIELDS 声明真源派生，禁手写第二张表）。"""
    ps = sorted(producers) if producers is not None else sorted(PRODUCER_FIELDS)
    out: dict[str, set[str]] = defaultdict(set)
    for p in ps:
        if p not in PRODUCER_FIELDS:
            raise WeightAuthorityError(f"作者 {p!r} 未声明写作字段（PRODUCER_FIELDS 缺项）")
        out[PRODUCER_FIELDS[p]].add(p)
    return dict(out)


def effective_writers(producers: Iterable[str] | None = None) -> set[str]:
    """谁在写生效字段（本案收敛后必须只剩 pf_alloc 一个）。"""
    return set(field_writer_map(producers).get(EFFECTIVE_FIELD, set()))


def assert_effective_path_single(producers: Iterable[str] | None = None) -> None:
    """生效面只剩一条路径的机械断言（多头即拒，包括"提名侧偷偷也写生效字段"）。"""
    prods = sorted(set(producers)) if producers is not None else sorted(PRODUCER_FIELDS)
    for p in prods:
        binding_of(p)
    eff = effective_writers(prods)
    if eff != {EFFECTIVE_AUTHORITY}:
        raise WeightAuthorityError(
            f"生效配比路径不唯一：{EFFECTIVE_FIELD} 的作者是 {sorted(eff)}，"
            f"而唯一合法生效作者={EFFECTIVE_AUTHORITY!r}（R-M2-6：auto_mount 只提名）"
        )
    assert_single_effective_writer(
        [{"producer": p, "strategy_ref": "__field_level__", "field": PRODUCER_FIELDS[p]} for p in prods]
    )


def assert_producer_writes_nomination(producer: str) -> None:
    """作者自证：我的权级=提名，且我写的字段不是生效字段（auto_mount 写图前调用）。"""
    binding = binding_of(producer)
    field = PRODUCER_FIELDS.get(producer)
    if field is None:
        raise WeightAuthorityError(f"作者 {producer!r} 未声明写作字段")
    if binding == BINDING_NOMINATION and field == EFFECTIVE_FIELD:
        raise WeightAuthorityError(f"提名作者 {producer!r} 不得写生效字段 {EFFECTIVE_FIELD}（提名≠生效）")
    if binding == BINDING_EFFECTIVE and field != EFFECTIVE_FIELD:
        raise WeightAuthorityError(f"生效作者 {producer!r} 的字段应为 {EFFECTIVE_FIELD}，实为 {field}")
    assert_effective_path_single()


def classify_path(rel_path: str) -> str:
    """把仓内相对路径认成已登记的权重作者。

    认不出=返回 :data:`WILD_WRITER`（**不再回 None**）——"认不出=不参与判定"正是这台尺
    失守的那条路：未登记作者的写手隐身，双头就永远探不到。
    """
    p = rel_path.replace("\\", "/")
    for producer, keys in PRODUCER_PATH_KEYS.items():
        if any(k in p for k in keys):
            return producer
    return WILD_WRITER


def is_wild_writer(producer: str) -> bool:
    """是否"未登记作者"（野生写手）。"""
    return producer == WILD_WRITER


def _scan_one_file_for_writes(path: Path, rel: str, producer: str) -> list[dict[str, Any]]:
    """单文件逐行严判据扫描（COMPLEXITY-GUARD 治本：自 find_weight_writing_sites 拆出，行为等价）。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        # INVARIANTS ④：读不到源文件=报错，绝不静默当"这里没有写手"
        raise WeightAuthorityError(f"写手源文件读不到（fail-closed）: {rel}: {exc}") from exc
    if "strategy_ref" not in text or "weight" not in text:
        return []  # 廉价前置过滤（两词皆无=不可能在写 sleeve 权重）
    hits: list[dict[str, Any]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("#") or "strategy_ref" not in s:
            continue
        if not _WILD_WEIGHT_RE.search(s):
            continue
        hits.append(
            {
                "producer": producer,
                "file": rel,
                "line": lineno,
                "kind": "wild_sleeve_weight_write" if is_wild_writer(producer) else "sleeve_weight_write",
                "registered": not is_wild_writer(producer),
                "attributable": not is_wild_writer(producer),
                "text": s[:120],
            }
        )
    return hits


def find_weight_writing_sites(
    repo_root: Path | str = ".", *, dirs: tuple[str, ...] = ("src", "scripts"), only_wild: bool = True
) -> list[dict[str, Any]]:
    """严判据扫描器（同一行须同时出现归因键 strategy_ref 与 weight 写入形状）。

    `only_wild=True` → 只回**未登记作者**的写点（野生面）；`False` → 登记作者也回。
    两条判据并存是刻意的：宽判据 `_WRITE_PATTERNS` 用在未登记文件上会把全仓
    `weight = 0.5` 的局部变量都算成写手＝噪音→告警疲劳→被拔线（BRK-046 教训同族）；
    故野生面用严判据，扫描范围在 census 的 wild_scan_dirs 里如实披露，不装作无死角。
    """
    root = Path(repo_root)
    if not root.exists():
        raise WeightAuthorityError(f"扫描根不存在：{root}")
    hits: list[dict[str, Any]] = []
    for d in dirs:
        base = root / d
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            rel = path.relative_to(root).as_posix()
            producer = classify_path(rel)
            if only_wild and not is_wild_writer(producer):
                continue  # 已登记作者走 scan_weight_writers 的宽判据，不在本面
            hits.extend(_scan_one_file_for_writes(path, rel, producer))
    return hits


def find_wild_weight_writers(
    repo_root: Path | str = ".", *, dirs: tuple[str, ...] = ("src", "scripts")
) -> list[dict[str, Any]]:
    """不靠声明表的野生写手探测：未登记路径里的 sleeve 权重写点逐条列 file:line。

    修前：未登记路径在 `scan_weight_writers` 里被 `continue` 掉（隐身），在
    `discover_weight_writers` 里也只进一个"没人读"的 unregistered 列表；修后：本函数
    的产物直接进 `authority_census` 的 conflicts 面（attributable=False），
    宿主 `alloc_authority_guard` 据此拒写图——"探不到就当没有"的日子结束了。
    """
    return find_weight_writing_sites(repo_root, dirs=dirs, only_wild=True)


def wild_writer_intents(wild: Iterable[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    """野生写手 → 写手意图（按"它写的就是提名面同一字段"归口，宁可判重不可放行）。"""
    sites_by_file: dict[str, list[str]] = defaultdict(list)
    for h in wild or []:
        f = str(h["file"])
        sites_by_file[f].append(f"{f}:{h['line']}")
    return [
        {"producer": WILD_WRITER, "strategy_ref": "__field_level__", "field": NOMINATION_FIELD, "sites": sorted(v)}
        for _f, v in sorted(sites_by_file.items())
    ]


def scan_weight_writers(repo_root: Path | str = ".", *, glob: str = "**/*.py") -> list[dict[str, Any]]:
    """实测扫描：**已登记**作者在代码里写权重的位置（file:line 可复核，禁凭记忆）。

    未登记作者不在此列（宽判据用在未登记面上＝满屏局部变量噪音）——那部分由
    :func:`find_wild_weight_writers` 以严判据补，两半合起来才是 census。
    """
    root = Path(repo_root)
    if not root.exists():
        raise WeightAuthorityError(f"扫描根不存在：{root}")
    sites: list[dict[str, Any]] = []
    for path in sorted(root.glob(glob)):
        rel = path.relative_to(root).as_posix()
        producer = classify_path(rel)
        if is_wild_writer(producer):  # 未登记作者走 wild 面（严判据），此处只认登记人
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise WeightAuthorityError(f"写手源文件读不到（fail-closed）: {rel}: {exc}") from exc
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue  # 注释不算写手
            if not _WEIGHT_KEY_RE.search(line):
                continue
            for kind, pat in _WRITE_PATTERNS:
                if re.search(pat, line):
                    sites.append(
                        {"producer": producer, "file": rel, "line": lineno, "kind": kind, "text": stripped[:120]}
                    )
                    break
    return sites


def writers_by_producer(sites: Iterable[Mapping[str, Any]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for s in sites:
        out[str(s["file"])].add(str(s["producer"]))
    return dict(out)


def authority_census(repo_root: Path | str = ".", *, dirs: tuple[str, ...] = ("src", "scripts")) -> dict[str, Any]:
    """一张表回答"这个权重现在谁说话算数"——生效面路径数必须=1，且**不许有隐身写手**。"""
    sites = scan_weight_writers(repo_root)
    wild = find_wild_weight_writers(repo_root, dirs=dirs)
    producers = sorted({str(s["producer"]) for s in sites})
    effective = sorted(effective_writers(producers)) if producers else []
    intents = [{"producer": p, "strategy_ref": "__field_level__", "field": PRODUCER_FIELDS[p]} for p in producers]
    intents += wild_writer_intents(wild)
    conflicts = find_weight_writer_conflicts(intents)
    return {
        "nomination_field": NOMINATION_FIELD,
        "effective_field": EFFECTIVE_FIELD,
        "effective_authority": EFFECTIVE_AUTHORITY,
        "producers_observed": producers,
        "effective_producers": effective,
        "effective_paths": len(effective),
        "single_effective_path": effective == [EFFECTIVE_AUTHORITY],
        # 野生写手面（修前恒空=隐身）：命中即进 conflicts，同时在此单列可核
        "wild_writer_sites": [f"{h['file']}:{h['line']}" for h in wild],
        "wild_scan_dirs": list(dirs),
        "unattributable": bool(conflicts),
        "clean": not conflicts and not wild,
        "conflicts": conflicts,
        "sites": sites,
    }


def discover_weight_writers(
    repo_root: Path | str = ".", *, dirs: tuple[str, ...] = ("src", "scripts")
) -> dict[str, Any]:
    """病根探针：不靠声明表，直接从源码里找"谁在往 sleeves 写 weight"。

    用于探出**未登记的第二头**（新脚本/新模块顺手改权重）：命中即列 file:line，
    认不出作者的写手记为 :data:`WILD_WRITER` 并进 unregistered 面（调用方据此报红，
    禁默认放行——旧版这里回 None 让它"看起来不存在"，本函数只报不判，判在 census）。
    """
    hits = find_weight_writing_sites(repo_root, dirs=dirs, only_wild=False)
    registered = sorted({str(h["producer"]) for h in hits if h["registered"]})
    unregistered = sorted({f"{h['file']}:{h['line']}" for h in hits if not h["registered"]})
    return {
        "hits": hits,
        "registered_producers": registered,
        "unregistered_writer_sites": unregistered,
        "effective_writers": sorted(
            set(registered) & {p for p, b in WEIGHT_PRODUCERS.items() if b == BINDING_EFFECTIVE}
        ),
        "clean": not unregistered and len(set(registered)) <= 2,
    }
