# [A_test] module_id: MOD-GOV_commit_queue_readback_discovery | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_commit_queue_readback_discovery
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.governance.commit_queue_landing; scripts.governance.d5_architecture.validators.validate_static_manifest_drift
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_readback_discovery.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根，绝不碰主仓 .runtime/commit_queue 与真实 dev）；
#              三态各配阴阳控制组：合法 noop 必须通行（退役吸收/他袋已落/陈旧携带/自愈覆盖），
#              条目行/未覆盖头部键被吞必拒绝，恒绿尺不得进本文件
# [MODIFY-GUARD] 落地前自证读回（防 done 零变化，q-0006 假成功治本）+ SKIP-6 派生标量自动
#                发现器的永久回归闸：摘掉 merged==ours 分流判别或发现器同源口即红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] permanent
"""落地前自证读回（防 done 零变化）+ SKIP-6 派生标量自动发现器 的永久回归尺。

案卷真源：q-0006 名册标量袋假成功（状态 done 而 dev 零提交）——合并器对标量/头部行
恒取 ours（防陈旧快照吃热册头部的正确设计），袋内增量凡走不进条目合并通道即静默蒸发，
落地器却记 done。治本两件（同一袋）：
  ① merged == ours 必经返回点三态分流（_noop_absorption_verdict）：吸收有解=合法 noop
     带审计注；条目行/未覆盖头部键被吞=MergeSwallowVerifyError 死信带处方；判别不能=
     同样拒绝（fail-closed）。
  ② SKIP-6 自动发现器（discover_derived_total_pairs）：total_<x> 标量与同名段共存且
     当前自洽的册自动收编进配对全集（all_derived_total_pairs = 发现 ⊕ 手工点名），
     检测（GATE-21）/落地自愈/自证读回三者同源消费。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE_BOOK_REL = "docs/01_policies_and_standards/_registry/catalogs/probe_readback_registry.yaml"
GATE_BOOK_REL = "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _cql():
    return _load("_cql_readback", "scripts/governance/commit_queue_landing.py")


_CQL = _cql()
_PAIRS_FOR_RULER = sorted(_CQL.all_derived_total_pairs().items())
_RULER_IDS = [book for book, _ in _PAIRS_FOR_RULER]


@pytest.fixture(scope="module")
def cql():
    return _cql()


def _git(cwd: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120
    )
    assert r.returncode == 0, f"git {' '.join(args)} -> {r.stderr[:300]}"
    return r.stdout.strip()


def _commit(repo: Path, path: str, text: str, msg: str) -> str:
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))  # write_bytes=LF 恒定，不随平台翻行尾
    _git(repo, "add", "--", path)
    _git(repo, "commit", "-qm", msg)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "dev")
    _git(r, "config", "user.email", "probe@local")
    _git(r, "config", "user.name", "probe")
    _git(r, "config", "core.autocrlf", "false")
    return r


def _entries(entries: list[tuple[str, str]], declared: int | None = None, scalar: str = "total_entries") -> str:
    body = "".join(f"  - id: {e}\n    name: {n}\n" for e, n in entries)
    head = f"{scalar}: {declared if declared is not None else len(entries)}\n" if declared is not None else ""
    return f"{head}entries:\n{body}"


def _landing(cql, repo: Path, tmp_path: Path, qname: str):
    return cql.WorktreeLanding(repo_root=repo, queue_root=tmp_path / qname, worktree_path=tmp_path / "wt")


# ---------------------------------------------------------------------------
# ① 三态判别（_noop_absorption_verdict 直接尺）——合法 noop 三种吸收解各配控制
# ---------------------------------------------------------------------------


def test_verdict_entry_absorbed_by_dev_is_legal_noop(cql) -> None:
    """袋内新增条目已在 dev HEAD（他袋已落）→ 合法 noop，审计注点名吸收。"""
    base = _entries([("A", "a")])
    ours = _entries([("A", "a"), ("B", "b")])
    theirs = _entries([("A", "a"), ("B", "b")])
    swallow, note = cql._noop_absorption_verdict(PROBE_BOOK_REL, base, ours, theirs)
    assert swallow is None, f"他袋已落的吸收必须通行，实得 {swallow!r}"
    assert "B" in note and "他袋已落" in note, f"审计注必须点名吸收条目，实得 {note!r}"


def test_verdict_retirement_absorption_still_passes(cql) -> None:
    """正当退役吸收必须仍通行（判据不许放松）：theirs 真改已删条目（采纳恢复意图），
    dev 侧合法退役吸收 → 合法 noop 而非死信。"""
    base = _entries([("A", "a"), ("E7", "seven")])
    ours = _entries([("A", "a")])  # dev 已退役 E7
    theirs = _entries([("A", "a"), ("E7", "seven-restored")])  # 袋侧改动=采纳恢复意图
    swallow, note = cql._noop_absorption_verdict(PROBE_BOOK_REL, base, ours, theirs)
    assert swallow is None, f"退役吸收不得被打死（判据不许放松），实得 {swallow!r}"
    assert "E7" in note, f"审计注须点名退役吸收，实得 {note!r}"


def test_verdict_stale_carry_is_legal_noop(cql) -> None:
    """theirs==base（纯陈旧携带，非本袋意图）→ 合法 noop，不误吞也不复活。"""
    base = _entries([("A", "a"), ("E7", "seven")])
    ours = _entries([("A", "a")])
    swallow, note = cql._noop_absorption_verdict(PROBE_BOOK_REL, base, ours, base)
    assert swallow is None, f"陈旧携带必须通行（ATK-1 语义），实得 {swallow!r}"
    assert "陈旧携带" in note, f"审计注须点名陈旧携带，实得 {note!r}"


def test_verdict_refuses_swallowed_entry_row(cql) -> None:
    """【吞没态】袋内真新增条目（base 无）未落进 dev → 拒绝，报告点名条目。"""
    base = _entries([("A", "a")])
    theirs = _entries([("A", "a"), ("B", "b")])
    swallow, _note = cql._noop_absorption_verdict(PROBE_BOOK_REL, base, base, theirs)
    assert swallow is not None and "吞没" in swallow, f"条目行被吞必须拒绝，实得 {swallow!r}"
    assert "B" in swallow, f"报告必须点名被吞条目，实得 {swallow!r}"


def test_verdict_refuses_swallowed_uncovered_header_scalar(cql) -> None:
    """【吞没态】未覆盖头部标量（version）被袋修改而 dev 未携带 → 拒绝（q-0006 同型）。"""
    base = "version: 1\n" + _entries([("A", "a")])
    theirs = "version: 2\n" + _entries([("A", "a")])
    swallow, _note = cql._noop_absorption_verdict(PROBE_BOOK_REL, base, base, theirs)
    assert swallow is not None and "version" in swallow, f"未覆盖标量被吞必须拒绝，实得 {swallow!r}"


def test_verdict_covered_scalar_is_legal_when_dev_self_consistent(cql) -> None:
    """覆盖内标量（gate_registry 的 total_gates→gates）：袋侧计值被自愈权威值取代 → 合法 noop。
    阴性控制：同一册改 version（未覆盖）仍拒绝。"""
    base = "total_gates: 1\ngates:\n  - gate_id: A\n    note: probe-A\n"
    theirs = "total_gates: 99\ngates:\n  - gate_id: A\n    note: probe-A\n"  # 袋只改计数没改条目
    swallow, note = cql._noop_absorption_verdict(GATE_BOOK_REL, base, base, theirs)
    assert swallow is None, f"覆盖内标量须合法（自愈已处理），实得 {swallow!r}"
    assert "total_gates" in note and "自愈" in note, f"审计注须点名自愈覆盖，实得 {note!r}"
    # 阴性：同册未覆盖键被吞仍拒绝
    base2 = "version: 1\n" + base
    theirs2 = "version: 9\n" + theirs
    swallow2, _n2 = cql._noop_absorption_verdict(GATE_BOOK_REL, base2, base2, theirs2)
    assert swallow2 is not None and "version" in swallow2, f"同册未覆盖键仍须拒绝，实得 {swallow2!r}"


def test_verdict_indeterminable_is_fail_closed(cql) -> None:
    """判别不能（theirs 侧解析失败）→ 拒绝（证明不了的零变化不算自证通过）。"""
    base = _entries([("A", "a")])
    theirs = "entries: [unclosed\n  - id: B\n"
    swallow, _note = cql._noop_absorption_verdict(PROBE_BOOK_REL, base, base, theirs)
    assert swallow is not None and "无法判别" in swallow, f"判别不能必须拒绝，实得 {swallow!r}"


# ---------------------------------------------------------------------------
# ② merged == ours 必经返回点分流（_merge_registry_file 集成尺）
# ---------------------------------------------------------------------------


def test_merge_registry_file_legal_noop_records_audit_note(cql, repo: Path, tmp_path: Path) -> None:
    """合法 noop 走 merged==ours 分流：返回 None 且 item.meta.noop_audit 落审计注。

    构造：dev 已落 B（他袋），袋快照以旧基底携带 A 并新增 B，族内条目序与 dev 相反
    （字节异、身份同——默认身份键=每条首个标量字段，字段序不可翻转故只翻条目序），
    合并器逐块保留 ours 原文 → merged==ours → 判别须给"他袋已落"解。
    """
    base = _commit(repo, PROBE_BOOK_REL, _entries([("A", "a")]), "C0 基底")
    _commit(repo, PROBE_BOOK_REL, "note: dev moved\n" + _entries([("A", "a"), ("B", "b")]), "C1 dev 加 B+头部")
    dev = _git(repo, "rev-parse", "refs/heads/dev")
    landing = _landing(cql, repo, tmp_path, "q-noop")
    item = {"qid": "q-noop-1", "base_head": base, "files": [{"path": PROBE_BOOK_REL}]}
    theirs = b"note: dev moved\nentries:\n  - id: B\n    name: b\n  - id: A\n    name: a\n"  # 条目序翻转≠字节同
    out = landing._merge_registry_file(item, PROBE_BOOK_REL, theirs, dev)
    assert out is None, f"他袋已落的袋必须合法 noop，实得 {out!r}"
    audit = str((item.get("meta") or {}).get("noop_audit") or "")
    assert "他袋已落" in audit and PROBE_BOOK_REL in audit, f"done 前必须落审计注，实得 {audit!r}"


def test_merge_registry_file_swallowed_increment_refuses_done(cql, monkeypatch, repo: Path, tmp_path: Path) -> None:
    """【吞没态】集成尺：合并器吞掉袋内新增（返回 ours 原文）→ MergeSwallowVerifyError
    死信带处方、携 dead_result（确定性故障不烧重试）——未来合并器回归在此被抓住，
    而不是又一笔 done 零变化。"""
    base = _commit(repo, PROBE_BOOK_REL, _entries([("A", "a")]), "C0")
    dev = _commit(repo, PROBE_BOOK_REL, _entries([("A", "a")]) + "note: same content\n", "C1")
    landing = _landing(cql, repo, tmp_path, "q-swallow")
    item = {"qid": "q-swallow-1", "base_head": base, "files": [{"path": PROBE_BOOK_REL}]}
    theirs = _entries([("A", "a"), ("X", "swallowed-by-bug")]).encode("utf-8")

    def _buggy_merge(base_text, ours_text, theirs_text, *, rel_path, retired_check=None):
        return ours_text, ""  # 模拟吞没：合并结果 == dev 原文

    monkeypatch.setattr(cql, "three_way_merge_registry_yaml", _buggy_merge)
    with pytest.raises(cql.MergeSwallowVerifyError) as ei:
        landing._merge_registry_file(item, PROBE_BOOK_REL, theirs, dev)
    assert ei.value.dead_result is not None, "确定性吞没必须携 dead_result 即刻死信，不烧重试"
    reason = ei.value.dead_result.reason
    assert "吞没" in reason and "人工核查" in reason, f"死信必须带处方，实得 {reason[:200]!r}"
    assert "X" in str(ei.value), f"报告必须点名被吞条目，实得 {str(ei.value)[:200]!r}"
    assert not (item.get("meta") or {}).get("noop_audit"), "拒绝态不得留合法 noop 审计注"


# ---------------------------------------------------------------------------
# ③ SKIP-6 自动发现器（收编判据逐条 + 手工覆盖 + 参数化 heal 尺 + GATE-21 同源）
# ---------------------------------------------------------------------------


def test_discover_derived_total_pairs_acceptance_rules(cql, tmp_path: Path) -> None:
    """收编判据逐条实测：同名标量+段+当前自洽才收编；漂移/缺段/解析坏/非映射/布尔一律不收。"""
    cat = tmp_path / "catalogs"
    cat.mkdir()
    (cat / "good.yaml").write_bytes(b"total_widgets: 2\nwidgets:\n  - id: a\n  - id: b\n")
    (cat / "drifted.yaml").write_bytes(b"total_gadgets: 5\ngadgets:\n  - id: a\n  - id: b\n")
    (cat / "no_section.yaml").write_bytes(b"total_ghost: 3\n")
    (cat / "broken.yaml").write_bytes(b"gadgets: [unclosed\n")
    (cat / "nonmap.yaml").write_bytes(b"- a\n- b\n")
    (cat / "bool_scalar.yaml").write_bytes(b"total_flags: true\nflags:\n  - id: a\n")
    got = cql.discover_derived_total_pairs(cat)
    assert got == {"good.yaml": {"total_widgets": "widgets"}}, f"收编判据漂移，实得 {got!r}"
    assert cql.discover_derived_total_pairs(tmp_path / "nope") == {}, "目录不存在必须退空表而非抛"


def test_all_derived_total_pairs_manual_overrides_discovered(cql, monkeypatch) -> None:
    """生效全集 = 发现 ⊕ 手工点名（同名手工赢，净零不删条目）。"""
    monkeypatch.setattr(
        cql,
        "_DISCOVERED_PAIRS_CACHE",
        {"gate_registry.yaml": {"total_gates": "WRONG_SECTION"}, "fresh_book.yaml": {"total_items": "items"}},
    )
    try:
        union = cql.all_derived_total_pairs()
    finally:
        monkeypatch.undo()
        cql._DISCOVERED_PAIRS_CACHE = None
    assert union["gate_registry.yaml"] == {"total_gates": "gates"}, "同名冲突手工必须赢"
    assert union["fresh_book.yaml"] == {"total_items": "items"}, "发现集必须增量收编进全集"
    for book, pairs in cql._MANUAL_DERIVED_TOTAL_PAIRS.items():
        assert union.get(book) == pairs, f"手工点名层净零保位失败: {book}"


def _heal_text(scalar: str, section: str, n: int, declared: int = 999) -> str:
    body = "".join(f"  - id: e{i}\n    name: n{i}\n" for i in range(n))
    return f"{scalar}: {declared}\n{section}:\n{body}"


@pytest.mark.parametrize(("book", "pairs"), _PAIRS_FOR_RULER, ids=_RULER_IDS)
def test_every_rostered_book_actually_heals(cql, book: str, pairs: dict[str, str], tmp_path: Path) -> None:
    """参数化尺：名册内每一册的配对都必须真能自愈（构造失真必刷正），且已一致零改动。

    名册=SKIP-6 发现集 ⊕ 手工点名层——此后任何新册被收编，本尺自动长出一个新参数，
    不需要再有人记得为它写尺（结构性复发点就此封死）。
    """
    landing = _landing(cql, tmp_path, tmp_path, "q-heal-ruler")
    for scalar, section in pairs.items():
        n = 3
        healed = landing._heal_derived_totals(book, _heal_text(scalar, section, n))
        assert healed.splitlines()[0] == f"{scalar}: {n}", (
            f"{book} 的 {scalar} 必须按段长刷正为 {n}，实得 {healed.splitlines()[0]!r}"
        )
        consistent = _heal_text(scalar, section, n, declared=n)
        assert landing._heal_derived_totals(book, consistent) == consistent, f"{book} 已一致必须字节零变化"


def test_gate21_checks_eat_discovery_results(cql) -> None:
    """GATE-21 CHECKS 同步吃发现结果：手工三台保留（净零）+ 发现册自动上榜 + 口径同源。"""
    drift = _load("_vsmd_readback", "scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py")
    drift._ensure_discovered_stations()
    stations = {}
    for chk in drift.CHECKS:
        sc = chk.get("selfcheck") or {}
        if sc.get("path") and sc.get("pairs"):
            stations[Path(str(sc["path"])).name] = dict(sc["pairs"])
    union = cql.all_derived_total_pairs()
    for book, pairs in union.items():
        assert stations.get(book) == pairs, f"发现册 {book} 必须自动上榜且配对同源，实得 {stations.get(book)!r}"
    for book, pairs in cql._MANUAL_DERIVED_TOTAL_PAIRS.items():
        assert stations.get(book) == pairs, f"手工点名台净零保位失败: {book}"
    assert drift.derived_total_pairs() == union, "GATE-21 对外读口必须与落地侧全集同源"


def test_discovered_books_are_currently_self_consistent_on_dev() -> None:
    """防线尺：SKIP-6 名册在 dev HEAD 必须当前自洽——发现器收编的前提是"曾经自洽"，
    若此尺红说明某册标量被推进而自愈没跟上（GATE-21 与落地自愈双通道都该拦住它）。"""
    import yaml  # noqa: PLC0415

    for book, pairs in sorted(_PAIRS_FOR_RULER):
        rel = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs" / book
        assert rel.is_file(), f"名册 {book} 必须实存（名册与盘面漂移）"
        data = yaml.safe_load(rel.read_text(encoding="utf-8"))
        for scalar, section in pairs.items():
            declared, actual = data.get(scalar), data.get(section)
            assert isinstance(declared, int) and isinstance(actual, (list, dict)), f"{book} 配对形态漂移"
            assert declared == len(actual), f"{book} {scalar}={declared} ≠ {section} 实际 {len(actual)}"
