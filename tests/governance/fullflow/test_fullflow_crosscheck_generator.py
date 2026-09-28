# [MODULE] scripts.governance.fullflow.generate_fullflow_crosscheck
# [DOMAIN] D_GOV_SCRIPTS
# [INVARIANTS] render() 幂等（无时间戳）；散文声称数 != 实测数必产 drift；实测面取不到必标 unavailable（禁填估计值）；作业簿集合只取 HEAD 跟踪集；F 号合法性以总册为准
# [CONSUMERS] pytest tests/governance/fullflow/test_fullflow_crosscheck_generator.py
# [STARTUP] manual
# [MATURITY] production
# [TTL] permanent
"""配对测试：机生对账尺（靶件=generate_fullflow_crosscheck.py）。

红队 RB-1 案卷（docs/_working/fullflow_mining/05_missing_p0/rb1_meter_attacks.md）打出了
七面绕过，本文件按"先证绕过存在、再证修后拦住"钉回归测：

①严格式声明行反讽句（``本册覆盖 F02 是事实``）——不记功
②行首 ``#`` 标题塞 20 个号——通道已删，一都不记
③非法长号（``本册覆盖 F12345678`` 洗 ``F123``）——不记功且报漂移位
④他道未 ``git add`` 的 WIP 簿——不得进入真源记录（无悬空证据）
⑤无 ``.git`` / 外层是仓库——不得静默读外层 HEAD 并标 ok
⑥豁免清单孤儿条目——当场报漂移

每面都配反向自证（真声明必须记功），防"修过头谁都不算"。
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_GEN_PATH = _REPO_ROOT / "scripts" / "governance" / "fullflow" / "generate_fullflow_crosscheck.py"

# 用 importlib 直载，绕开 src/zephyr/governance 与 scripts/governance 同名歧义
_spec = importlib.util.spec_from_file_location("generate_fullflow_crosscheck", _GEN_PATH)
assert _spec is not None and _spec.loader is not None
_gen = importlib.util.module_from_spec(_spec)
sys.modules["generate_fullflow_crosscheck"] = _gen
_spec.loader.exec_module(_gen)


# ---------------------------------------------------------------- 迷你仓库夹具
_TOTAL_BOOK_BODY = """# 全流通环节总册（L0 骨架）

> **方法**：七源真源通读：②config/trading_decision_map.yaml（消费端 {tdm} 节点四流）⑥src/zephyr/ 一级 {pkgs} 包实扫
> 与既有 M0 骨架的关系：合计 **{f_links} 环节 / {seg_count} 段**。

## 一、环节总清单（{f_links} 环节 / {seg_count} 段）

### A 段·数据供给链（F01-F02）

| # | 环节 | 一句话职责 | 上游 | 下游 | 核心模块路径（真源锚点） | 状态 | 优先 | M0 |
|---|------|-----------|------|------|--------------------------|------|------|----|
| F01 | 多源采集调度 | 灌水 | 外部 | F02 | `python -m zephyr.data` | built | P1 | D1 |
| F02 | 数据源接入生命周期 | 接入 | F96 | F01 | sop/xx.md | partial | P0 | D2 |

### B 段·策略供给链（F03-F04；{flow_claim}）

| # | 环节 | 一句话职责 | 上游 | 下游 | 核心模块路径（真源锚点） | 状态 | 优先 | M0 |
|---|------|-----------|------|------|--------------------------|------|------|----|
| F03 | E0 算力调度心跳 | 问闸 | 日历 | 全厂 | strategy_production_map FAC-E0 | partial | P1 | — |
| F04 | E1 想法进货编排 | 进货 | F03 | F99 | MOD-BT-154 | partial | P1 | — |
"""

_MINING = "docs/_working/fullflow_mining"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.quotePath=false", "-c", "commit.gpgsign=false", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def git_land(root: Path) -> None:
    """把夹具工作树"落地"进 HEAD（测试禁走静默降级路径：git 不可用即当场失败）。"""
    for cmd in (
        ["init", "-q", "-b", "main"],
        ["-c", "user.email=t@example.invalid", "-c", "user.name=t", "add", "-A"],
        ["-c", "user.email=t@example.invalid", "-c", "user.name=t", "commit", "-q", "-m", "fixture"],
    ):
        proc = _git(root, *cmd)
        assert proc.returncode == 0, f"git {' '.join(cmd)} 失败（夹具无法落地，测试不得静默放行）：{proc.stderr[:400]}"


def _flow_cycle(count: int) -> dict[str, int]:
    cycle = ["entry", "position", "exit", "portfolio"]
    out = {name: 0 for name in cycle}
    for i in range(count):
        out[cycle[i % 4]] += 1
    return out


def make_fixture_repo(
    tmp_path: Path,
    *,
    tdm_nodes: int = 4,
    roor_entries: int = 3,
    roor_summary: int = 3,
    prose_tdm_claim: int | None = None,
    prose_pkg_claim: int = 2,
    f_claim: int = 4,
    mining_books: bool = True,
    total_book_body: str | None = None,
    land: bool = True,
    dir_name: str = "repo",
) -> Path:
    """造一个只含对账所需真源的迷你仓库（不碰生产文件，输出全在 tmp_path）。

    ``land=True`` ⇒ 夹具自带 ``.git`` 且真源已入 HEAD（尺的实测面＝落地面，见判定 §3）。
    """
    root = tmp_path / dir_name
    root.mkdir(parents=True, exist_ok=True)

    claimed_tdm = prose_tdm_claim if prose_tdm_claim is not None else tdm_nodes
    flows = _flow_cycle(tdm_nodes)
    flow_claim = (
        f"{tdm_nodes} 节点：entry {flows['entry']}/position {flows['position']}"
        f"/exit {flows['exit']}/portfolio {flows['portfolio']}"
    )
    body = (_TOTAL_BOOK_BODY) if total_book_body is None else total_book_body
    _write(
        root / _gen.TOTAL_BOOK_REL,
        body.format(tdm=claimed_tdm, pkgs=prose_pkg_claim, f_links=f_claim, seg_count=2, flow_claim=flow_claim),
    )

    flow_cycle = ["entry_flow", "position_flow", "exit_flow", "portfolio_flow"]
    tdm_lines = ["nodes:"]
    for i in range(tdm_nodes):
        tdm_lines.append(f"- node_id: TDM-E-L{i % 4}-{i + 1:02d}")
        tdm_lines.append(f"  flow: {flow_cycle[i % 4]}")
        tdm_lines.append(f"  module_ref: MOD-{i}")
    _write(root / _gen.TDM_REL, "\n".join(tdm_lines) + "\n")

    spm = ["nodes:"]
    for i, fid in enumerate(("FAC-E0", "FAC-E1")):
        spm.append(f"- node_id: {fid}")
        spm.append("  module_ref: MOD-BT-151" if i == 0 else "  module_ref: null")
    _write(root / _gen.SPM_REL, "\n".join(spm) + "\n")

    roor_lines = ["summary:", f"  total_registries: {roor_summary}", "registries:"]
    for i in range(roor_entries):
        roor_lines.append(f"- registry_id: REG-{i:03d}")
    _write(root / _gen.ROOR_REL, "\n".join(roor_lines) + "\n")

    fdr = ["entries:"]
    for name in ("D_GOV_SCRIPTS", "D_GOV_RULE"):
        fdr.append(f"- domain: {name}")
        fdr.append("  subdomain: x")
    _write(root / _gen.FUNCTIONAL_DOMAIN_REGISTRY_REL, "\n".join(fdr) + "\n")

    for pkg in ("data", "trading"):
        (root / _gen.SRC_ZEPHYR_REL / pkg).mkdir(parents=True, exist_ok=True)
        _write(root / _gen.SRC_ZEPHYR_REL / pkg / "__init__.py", "")
    (root / _gen.SRC_ZEPHYR_REL / "__pycache__").mkdir(parents=True, exist_ok=True)

    if mining_books:
        _write(root / f"{_MINING}/m1_data/01_ingest.md", "# 采集作业簿\n\n本册覆盖 F01\n")
        _write(root / f"{_MINING}/m2_backtest_sim/20_f04_intake.md", "# 进货簿（仅文件名认领）\n")
    _write(root / _gen.WAVE1_COMMAND_BOOK_REL, f'# 指挥册\n> TDM"{tdm_nodes} 节点"（实 {tdm_nodes}）\n')
    # 手工豁免清单自守要求每条都在 HEAD 里——把清单面铺齐，"零漂移"测才不是空转
    for rel in _gen.NON_WORKBOOK_RELS:
        book = root / _MINING / rel
        if not book.is_file():
            _write(book, "# 编排/分析面（非作业簿）\n")
    if land:
        git_land(root)
    return root


def payload_of(root: Path) -> dict[str, Any]:
    return _gen.build_payload(root)


def drift_kinds(payload: dict[str, Any]) -> list[str]:
    return sorted({str(d["kind"]) for d in payload["drift_flags"]})


def coverage_rows(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cm = payload["coverage_matrix"]
    return {r["id"]: r for seg in cm["segments"] for r in cm["segments"][seg]["rows"]}


# ---------------------------------------------------------------- ① 幂等
def test_render_is_byte_identical_across_runs(tmp_path: Path) -> None:
    root = make_fixture_repo(tmp_path)
    first = _gen.render(payload_of(root))
    second = _gen.render(payload_of(root))
    assert first == second, "同输入两次渲染必须字节相同（生成器禁时间戳）"

    out_a = tmp_path / "a.yaml"
    out_b = tmp_path / "b.yaml"
    for out in (out_a, out_b):
        with out.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(_gen.render(payload_of(root)))
    assert out_a.read_bytes() == out_b.read_bytes()


def test_rendered_yaml_has_no_clock_fields(tmp_path: Path) -> None:
    text = _gen.render(payload_of(make_fixture_repo(tmp_path)))
    assert not re.search(r"(generated_at|timestamp|created_at|updated_at)\s*:", text), "机生册禁时间戳字段"
    assert _gen.GENERATED_BY in text
    assert "source_files:" in text


def test_main_writes_into_tmp_path_only(tmp_path: Path) -> None:
    root = make_fixture_repo(tmp_path)
    out = tmp_path / "nested" / "91_machine_crosscheck.yaml"
    rc = _gen.main(["--repo-root", str(root), "--out", str(out), "--quiet"])
    assert rc == 0
    assert out.is_file()
    parsed = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert parsed["generated_by"] == _gen.GENERATED_BY
    assert parsed["counts"]["f_links"]["measured"] == 4


def test_check_passes_on_fresh_and_fails_on_hand_edit(tmp_path: Path) -> None:
    """GATE-21 语义＝只判陈旧：手改产物必红（拦住），字节一致即绿。"""
    root = make_fixture_repo(tmp_path)
    out = tmp_path / "91.yaml"
    assert _gen.main(["--repo-root", str(root), "--out", str(out), "--quiet"]) == 0
    assert _gen.main(["--repo-root", str(root), "--out", str(out), "--check", "--quiet"]) == 0
    out.write_bytes(out.read_bytes().replace(b"machine_generated_do_not_hand_edit", b"hand_edited_marker"))
    assert _gen.main(["--repo-root", str(root), "--out", str(out), "--check", "--quiet"]) == 1


def test_check_is_eol_insensitive(tmp_path: Path) -> None:
    """检出被 renormalize 成 CRLF 的产物不得恒红（RB-1 A6.4），但内容差仍须红。"""
    root = make_fixture_repo(tmp_path)
    out = tmp_path / "91.yaml"
    assert _gen.main(["--repo-root", str(root), "--out", str(out), "--quiet"]) == 0
    lf = out.read_bytes()
    assert b"\r\n" not in lf
    out.write_bytes(lf.replace(b"\n", b"\r\n"))
    assert _gen.main(["--repo-root", str(root), "--out", str(out), "--check", "--quiet"]) == 0, (
        "CRLF 检出即恒红＝连坐无辜"
    )
    out.write_bytes(lf.replace(b"machine_generated_do_not_hand_edit", b"hand_edited_marker"))
    assert _gen.main(["--repo-root", str(root), "--out", str(out), "--check", "--quiet"]) == 1


# ---------------------------------------------------------------- ② 判别力自证（这把尺能红）
def test_caught_claimed_ne_measured_roor(tmp_path: Path) -> None:
    """ROOR summary 字段与 grep 实测不一致 → 必须标 drift（生产里 76 vs 77 的原型）。"""
    root = make_fixture_repo(tmp_path, roor_entries=5, roor_summary=4)
    payload = payload_of(root)
    roor_drifts = [d for d in payload["drift_flags"] if d["metric"] == "roor_registries"]
    assert roor_drifts, "声称 4 != 实测 5 必须被抓到，否则尺恒绿"
    assert roor_drifts[0]["claimed"] == 4
    assert roor_drifts[0]["measured"] == 5
    assert payload["drift_summary"]["red"] is True


def test_caught_stale_tdm_node_claim(tmp_path: Path) -> None:
    """总册散文写 138 节点、实扫 182 型场景：声称面与实测面背离必须红。"""
    root = make_fixture_repo(tmp_path, tdm_nodes=6, prose_tdm_claim=2)
    payload = payload_of(root)
    hits = [d for d in payload["drift_flags"] if d["metric"] == "tdm_nodes"]
    assert hits, "过期节点声称必须被抓到"
    assert {h["claimed"] for h in hits} == {2}
    assert {h["measured"] for h in hits} == {6}


def test_clean_fixture_reports_zero_drift(tmp_path: Path) -> None:
    """反向自证：全部对齐时不得误报——否则上面两条红测没有意义。"""
    root = make_fixture_repo(tmp_path, tdm_nodes=4, roor_entries=3, roor_summary=3, prose_pkg_claim=2, f_claim=4)
    payload = payload_of(root)
    assert payload["drift_flags"] == [], f"干净夹具不该有漂移：{payload['drift_flags']}"
    # red 仍可为 True：夹具里 F02/F03 本就无簿（覆盖缺口），不得把"无漂移"混同于"世界已齐"
    assert payload["drift_summary"]["coverage_uncovered_links"] == 2


def test_unavailable_metric_is_reported_not_guessed(tmp_path: Path) -> None:
    """真源缺失 → status unavailable 且 measured=null，绝不用估计值填数。"""
    root = make_fixture_repo(tmp_path)
    (root / _gen.TDM_REL).unlink()
    payload = payload_of(root)
    tdm = payload["counts"]["tdm_nodes"]
    assert tdm["status"] == "unavailable"
    assert tdm["measured"] is None
    assert tdm["unavailable_reason"]
    assert "tdm_nodes" in payload["drift_summary"]["unavailable_metrics"]
    assert payload["drift_summary"]["red"] is True


def test_duplicate_f_rows_are_flagged(tmp_path: Path) -> None:
    """F 编号复用（行数 != 去重 id 数）必须红。"""
    dup = _TOTAL_BOOK_BODY + "\n| F01 | 重复行 | x | y | z | built | P1 | D1 |\n"
    root = make_fixture_repo(
        tmp_path,
        total_book_body=dup.format(
            tdm=4, pkgs=2, f_links=4, seg_count=2, flow_claim="4 节点：entry 1/position 1/exit 1/portfolio 1"
        ),
    )
    payload = payload_of(root)
    kinds = {d["kind"] for d in payload["drift_flags"]}
    assert "row_count_ne_unique_ids" in kinds
    assert payload["counts"]["f_links"]["detail"]["duplicate_ids"] == ["F01"]


# ---------------------------------------------------------------- ③ 覆盖矩阵（HEAD 面 + 三处声明位）
def test_coverage_matrix_splits_covered_and_uncovered(tmp_path: Path) -> None:
    root = make_fixture_repo(tmp_path)
    coverage = payload_of(root)["coverage_matrix"]
    assert coverage["totals"]["links"] == 4
    # F01 由严格式声明行认领、F04 由文件名认领；F02/F03 无簿
    assert "F01" in coverage["covered_ids"]
    assert "F04" in coverage["covered_ids"]
    assert coverage["uncovered_ids"] == ["F02", "F03"]
    assert coverage["totals"]["uncovered"] == 2
    seg_b = coverage["segments"]["B"]
    assert seg_b["row_count"] == 2 and seg_b["uncovered"] == 1


def test_coverage_goes_red_when_a_workbook_is_removed(tmp_path: Path) -> None:
    root = make_fixture_repo(tmp_path)
    (root / f"{_MINING}/m1_data/01_ingest.md").unlink()
    payload = payload_of(root)
    coverage = payload["coverage_matrix"]
    assert "F01" in coverage["uncovered_ids"], "删簿后 F01 必须落未覆盖——矩阵不是恒绿装饰"
    assert coverage["totals"]["covered"] == 1
    assert "head_book_missing_on_disk" in drift_kinds(payload)


def test_skeleton_index_books_do_not_count_as_coverage(tmp_path: Path) -> None:
    """总册自指（编号源）不算已挖——排除面必须在 YAML 里可见。"""
    root = make_fixture_repo(tmp_path, mining_books=False)
    book = root / _gen.TOTAL_BOOK_REL
    book.write_text(book.read_text(encoding="utf-8") + "\n本册覆盖 F01 F99\n", encoding="utf-8")
    payload = payload_of(root)
    coverage = payload["coverage_matrix"]
    assert "00_skeleton/00_全环节总册.md" in coverage["definition"]["non_workbook_excluded"]
    assert coverage["definition"]["workbook_count"] == 0
    assert "F01" in coverage["uncovered_ids"], "只剩总册自指时不得判为已覆盖"


def test_ruling_book_listing_gaps_does_not_claim_coverage(tmp_path: Path) -> None:
    """红队回归（2026-09-26 实测绕过）：战役面册只是**点名**缺口，不得算该环节已挖。

    旧实现全文 grep：总筹裁定册与红队案卷列出 F02/F03 ⇒ uncovered 6→0，尺当场说谎。
    现只认三处声明位（文件名 fnn／严格式声明行／covers 列表）。
    反向自证同做：真簿用声明行认领必须判 covered，防修过头变成谁都不算。
    """
    root = make_fixture_repo(tmp_path)
    mining = root / _MINING
    _write(
        mining / "94_chief_rulings_wave2.md",
        "# 94 总筹裁定册\n\n残余缺口：F02 F03，派单下波；已落 F01 F04。\n<!-- 注释里藏 F02 -->\n# F02 标题也不算\n",
    )
    git_land(root)  # 已落地也不得记功（绕过面＝"提到即算"，与落地与否无关）
    rows = coverage_rows(payload_of(root))
    assert rows["F02"]["status"] == "uncovered", rows["F02"]
    assert rows["F03"]["status"] == "uncovered", rows["F03"]
    assert "94_chief_rulings_wave2.md" not in rows["F02"]["workbooks"]

    _write(mining / "m1_data/05_declared_book.md", "# 一本真簿\n\n本册覆盖 F02\n")
    git_land(root)
    rows2 = coverage_rows(payload_of(root))
    assert rows2["F02"]["status"] == "covered", rows2["F02"]
    assert "m1_data/05_declared_book.md" in rows2["F02"]["workbooks"]
    assert rows2["F03"]["status"] == "uncovered"


# ---------------------------------------------------------------- ④ 红队七面逐面回归（RB-1 案卷）
def test_rb_face1_sarcastic_declaration_line_is_not_credit(tmp_path: Path) -> None:
    """面①：严格式声明行——行尾有任何散文即不记功（反讽/指认句绕过）。"""
    root = make_fixture_repo(tmp_path, mining_books=False)
    _write(
        root / f"{_MINING}/m1_data/99_sarcastic.md",
        "# 指认册\n\n本册覆盖 F01 是事实，其实并没有\n\n本册覆盖 F01、F02 尚未落簿\n\n"
        "本册覆盖 F01\n",  # 只有这一行是严格式
    )
    git_land(root)
    payload = payload_of(root)
    rows = coverage_rows(payload)
    assert rows["F01"]["status"] == "covered", "严格式声明行必须记功（反向自证）"
    assert rows["F01"]["workbooks"] == ["m1_data/99_sarcastic.md"]
    assert rows["F02"]["status"] == "uncovered", "带行尾散文的半截声明不得记功（RB-1 V1 反讽句绕过）"
    malformed = [d for d in payload["drift_flags"] if d["kind"] == "declaration_line_malformed"]
    assert len(malformed) == 2, f"非严格式声明行必须留痕（不静默隐身）：{malformed}"
    assert {m["line"] for m in malformed} == {3, 5}


def test_covers_surface_must_be_a_yaml_list(tmp_path: Path) -> None:
    """面①补（RB-1 §九②）：``covers:`` 空格分隔字符串解析不出列表 ⇒ 不记功且留痕；列表才记功。"""
    root = make_fixture_repo(tmp_path, mining_books=False)
    _write(
        root / f"{_MINING}/m1_data/97_fm_bad.md",
        "---\nttl: task_bound\nvolume: 97_fm_bad\ncovers: F01 F02\n---\n\n# 空格分隔的假列表\n",
    )
    _write(
        root / f"{_MINING}/m1_data/96_fm_flow_list.md",
        "---\nttl: task_bound\nvolume: 96_fm_flow_list\ncovers: [F03]\n---\n\n# 流式列表\n",
    )
    _write(
        root / f"{_MINING}/m1_data/95_fm_block_list.md",
        "---\nttl: task_bound\nvolume: 95_fm_block_list\ncovers:\n  - F04\n---\n\n# 块式列表\n",
    )
    git_land(root)
    payload = payload_of(root)
    rows = coverage_rows(payload)
    assert rows["F01"]["status"] == "uncovered" and rows["F02"]["status"] == "uncovered"
    assert rows["F03"]["status"] == "covered", "YAML 流式列表必须记功（反向自证）"
    assert rows["F04"]["status"] == "covered", "YAML 块式列表必须记功（反向自证）"
    bad = [d for d in payload["drift_flags"] if d["kind"] == "covers_surface_not_creditable"]
    assert len(bad) == 1 and "covers_not_a_list" in bad[0]["reason"], bad
    assert Path(bad[0]["file"]).name == "97_fm_bad.md"

    # frontmatter 整块解析失败（值里带裸冒号）⇒ 同样不记功、必须留痕
    _write(
        root / f"{_MINING}/m1_data/94_fm_broken.md",
        "---\nttl: task_bound\nvolume: 94_fm_broken\ncovers: [F01\n---\n\n# 坏 frontmatter\n",
    )
    git_land(root)
    payload2 = payload_of(root)
    bad2 = [d for d in payload2["drift_flags"] if d["kind"] == "covers_surface_not_creditable"]
    assert any("frontmatter_unparsable" in d["reason"] for d in bad2), bad2
    assert coverage_rows(payload2)["F01"]["status"] == "uncovered"


def test_rb_face2_title_line_cannot_launder_twenty_ids(tmp_path: Path) -> None:
    """面②：行首 ``#`` 标题通道已删——一行塞一排号（红队实测 20 个）一都不记。"""
    root = make_fixture_repo(tmp_path, mining_books=False)
    ids = " ".join(f"F{n:02d}" for n in range(1, 5))
    _write(root / f"{_MINING}/m1_data/98_title_dump.md", f"# 标题塞号 {ids}\n\n散文里再提 {ids}\n")
    git_land(root)
    payload = payload_of(root)
    rows = coverage_rows(payload)
    assert all(rows[f"F{n:02d}"]["status"] == "uncovered" for n in range(1, 5)), rows
    assert payload["coverage_matrix"]["totals"]["covered"] == 0
    assert payload["coverage_matrix"]["totals"]["uncovered"] == 4
    # 反向自证：同一本册改用严格式声明行即全部记功（证明拦的是通道不是号）
    _write(
        root / f"{_MINING}/m1_data/98_title_dump.md",
        f"# 标题塞号\n\n本册覆盖 {'/'.join(f'F{n:02d}' for n in range(1, 5))}\n",
    )
    payload2 = payload_of(root)
    assert payload2["coverage_matrix"]["totals"]["covered"] == 4


def test_rb_face3_illegal_long_number_cannot_launder_and_reports(tmp_path: Path) -> None:
    """面③：非法号（4 位以上溢出／1 位／不在总册的号）不记功，且必须报漂移位。"""
    # 给总册加一个合法供体环节 F05（C 段），模拟红队"总册含 F123 供体"的情形
    body = _TOTAL_BOOK_BODY.format(
        tdm=4, pkgs=2, f_links=5, seg_count=3, flow_claim="4 节点：entry 1/position 1/exit 1/portfolio 1"
    )
    body += "\n### C 段·溢出（F05）\n\n| # | 环节 | x |\n|---|---|---|\n| F05 | 供体环节 | y |\n"
    root = make_fixture_repo(tmp_path, mining_books=False, f_claim=5, total_book_body=body)
    _write(
        root / f"{_MINING}/atk/zz_overflow_launder.md",
        "# 洗白册\n\n本册覆盖 F5\n\n本册覆盖 F678\n\n本册覆盖 F0506\n",
    )
    _write(root / f"{_MINING}/atk/07_f12345678_overflow.md", "# 文件名溢出号\n")
    git_land(root)
    payload = payload_of(root)
    rows = coverage_rows(payload)
    assert rows["F05"]["status"] == "uncovered", "贪婪切片（F0506→F05/F050/F5）不得成为认领证据"
    assert payload["coverage_matrix"]["totals"]["covered"] == 0
    illegal = [d for d in payload["drift_flags"] if d["kind"] == "illegal_f_token_in_claim_surface"]
    assert illegal, "非法号必须报漂移位（RB-1 A7.4 零成本零痕迹绕过）"
    tokens = {d["token"] for d in illegal}
    assert {"F5", "F678", "F0506", "F12345678"} <= tokens, tokens
    # 反向自证：合法号照样记功
    _write(root / f"{_MINING}/atk/08_clean.md", "本册覆盖 F05\n")
    git_land(root)
    rows2 = coverage_rows(payload_of(root))
    assert rows2["F05"]["status"] == "covered"


def test_rb_face3b_illegal_id_inserted_into_total_book_is_reported(tmp_path: Path) -> None:
    """面③补：往总册塞越界号（F999）顶高 f_links ⇒ 号段不变式必须报漂移。"""
    body = _TOTAL_BOOK_BODY.format(
        tdm=4, pkgs=2, f_links=4, seg_count=2, flow_claim="4 节点：entry 1/position 1/exit 1/portfolio 1"
    )
    body += "\n### Z 段·塞号\n\n| # | 环节 | x |\n|---|---|---|\n| F999 | 非法塞入 | y |\n"
    root = make_fixture_repo(tmp_path, total_book_body=body)
    payload = payload_of(root)
    kinds = drift_kinds(payload)
    assert "f_id_noncontiguous" in kinds, "F01..FNN 断号/越界必须现形（RB-1 A7.1 零告警绕过）"
    missing = [d for d in payload["drift_flags"] if d["kind"] == "f_id_noncontiguous"][0]["missing_numbers"]
    assert "F005" in missing or "F05" in missing
    assert payload["drift_summary"]["red"] is True


def test_rb_face4_uncommitted_wip_book_never_enters_the_record(tmp_path: Path) -> None:
    """面④（最重）：他道**未 git add 的 WIP 簿**不得进入真源记录，且 WIP 丢弃后不留悬空证据。"""
    root = make_fixture_repo(tmp_path)
    wip = root / f"{_MINING}/m3_governance/09_f03_wip_of_other_lane.md"
    _write(wip, "# 他道 WIP 簿\n\n本册覆盖 F03\n")  # 只写盘，不落地
    payload = payload_of(root)
    rows = coverage_rows(payload)
    assert rows["F03"]["status"] == "uncovered", "未落地 WIP 不得被记功（RB-1 P4 假绿持久化）"
    cm = payload["coverage_matrix"]
    census = cm["definition"]["f_token_census_per_workbook"]
    assert "m3_governance/09_f03_wip_of_other_lane.md" not in census, "未落地簿不得留证据链"
    for row in cm["segments"]["A"]["rows"] + cm["segments"]["B"]["rows"]:
        assert "m3_governance/09_f03_wip_of_other_lane.md" not in row["workbooks"], row
    assert "m3_governance/09_f03_wip_of_other_lane.md" in cm["definition"]["untracked_books_ignored_sample"], (
        "未落地件必须被**观测**到（隐身＝下一波又当新件），只是不得记功"
    )
    assert cm["definition"]["untracked_books_ignored_count"] >= 1
    assert payload["counts"]["mining_books"]["detail"]["not_in_head_count"] >= 1
    # WIP 被丢弃 ⇒ 真源记录（认领面/矩阵）逐字段不变；盘面观测面（P-0 敞口）随文件消失而回落，
    # 关键是**不得留下指向不存在路径的悬空"证据"**（RB-1 P4.2-P4.6 的假绿持久化形态）。
    before = payload_of(root)
    census_before = before["coverage_matrix"]["definition"]["f_token_census_per_workbook"]
    totals_before = before["coverage_matrix"]["totals"]
    wip.unlink()
    after = payload_of(root)
    cm_after = after["coverage_matrix"]
    assert cm_after["definition"]["f_token_census_per_workbook"] == census_before
    assert cm_after["totals"] == totals_before
    assert "m3_governance/09_f03_wip_of_other_lane.md" not in str(cm_after["definition"])
    assert "09_f03_wip_of_other_lane" not in str(after["counts"]["mining_books"]["detail"])
    # 反向自证：同一本册落地后必须记功（证明拦的是"未落地"，不是"这本册"）
    _write(wip, "# 他道 WIP 簿\n\n本册覆盖 F03\n")
    git_land(root)
    assert coverage_rows(payload_of(root))["F03"]["status"] == "covered"


def test_rb_face4b_no_quiet_degradation_when_git_is_unusable(tmp_path: Path) -> None:
    """面④补：git 不在 PATH ⇒ mining_books 必 unavailable 且不算绿（旧实现 status=partial 静默降级）。"""
    root = make_fixture_repo(tmp_path)
    baseline = payload_of(root)
    assert baseline["counts"]["mining_books"]["status"] == "ok"
    import os

    empty_bin = tmp_path / "emptybin"
    empty_bin.mkdir()
    saved = os.environ.get("PATH") or ""
    os.environ["PATH"] = str(empty_bin)
    try:
        payload = payload_of(root)
    finally:
        os.environ["PATH"] = saved or ""
    mb = payload["counts"]["mining_books"]
    assert mb["status"] == "unavailable", mb
    assert mb["measured"] is None, "取不到数不得填数（也不得沿用 ok）"
    assert "mining_books" in payload["drift_summary"]["unavailable_metrics"]
    assert payload["drift_summary"]["red"] is True


def test_rb_face5_no_git_dir_must_not_read_outer_repo(tmp_path: Path) -> None:
    """面⑤：没有 ``.git`` 的目录**绝不上溯外层仓库**，且不得标 ``status: ok``。

    场景照抄 RB-1 P1.3：worktree/tmp 副本外层是仓库、内层无 ``.git`` ⇒ 旧尺读外层 HEAD，
    把 ``head_count=0``/``not_in_head=153`` 标成 ok（"没落地"报成"全没落地"却算绿）。
    """
    inner = make_fixture_repo(tmp_path, dir_name="outer/work", mining_books=False, land=False)
    outer = inner.parent
    _write(inner / f"{_MINING}/m1_data/01_ingest.md", "本册覆盖 F01\n")
    git_land(outer)  # 外层 HEAD 里看得见 work/docs/_working/fullflow_mining/...（旧尺就是读到这里）
    tracked = _gen.resolve_head_tracking(outer)
    assert tracked.ok and any(f.startswith(f"work/{_MINING}/") for f in tracked.files), tracked.files[:5]

    assert not (inner / ".git").exists()
    head = _gen.resolve_head_tracking(inner)
    assert head.status == "unavailable", head
    assert "no .git" in head.reason, head.reason
    payload = payload_of(inner)
    mb = payload["counts"]["mining_books"]
    assert mb["status"] == "unavailable" and mb["measured"] is None
    assert mb["detail"]["head_count"] is None, "不得沿用外层 HEAD 的数（哪怕是 0）"
    assert payload["drift_summary"]["head_tracking_ok"] is False
    assert payload["drift_summary"]["red"] is True, "取不到本仓 HEAD 不得算绿（RB-1 P1.3 无声错值）"
    assert "coverage_claim_surface_unavailable" in drift_kinds(payload)

    # 第二式：`.git` 存在但是坏仓（rev-parse 非零）⇒ 同样 unavailable，不得退回"读外层/填 0"
    broken = tmp_path / "broken"
    (broken / ".git").mkdir(parents=True)
    head2 = _gen.resolve_head_tracking(broken)
    assert head2.status == "unavailable", head2
    assert "no .git" not in head2.reason, "须走到 git 调用面（证明两条前置各自有效）"


def test_rb_face5b_non_ascii_books_survive_head_listing(tmp_path: Path) -> None:
    """面⑤补：git 子进程必须带 ``-c core.quotePath=false``，否则非 ASCII 册从 HEAD 面消失。"""
    root = make_fixture_repo(tmp_path, mining_books=False)
    _write(root / f"{_MINING}/m5_scheduling/补挖波_20260925/06_f83_automation_crew.md", "本册覆盖 F03\n")
    git_land(root)
    head = _gen.resolve_head_tracking(root)
    assert head.ok
    joined = "\n".join(head.files)
    assert "补挖波_20260925/06_f83_automation_crew.md" in joined, "非 ASCII 路径被八进制引号包裹＝33 本册消失"
    assert "\\346\\241" not in joined, "出现八进制引号路径即 quotePath 未关"
    assert coverage_rows(payload_of(root))["F03"]["status"] == "covered"


def test_rb_face6_exemption_list_orphan_is_reported(tmp_path: Path) -> None:
    """面⑥：豁免清单自守——孤儿条目（盘上/HEAD 均无此件）必须报漂移；未落地条目也报。"""
    root = make_fixture_repo(tmp_path)
    assert "non_workbook_exclusion_orphan" not in drift_kinds(payload_of(root))

    saved = _gen.NON_WORKBOOK_RELS
    try:
        _gen.NON_WORKBOOK_RELS = tuple(list(saved) + ["05_missing_p0/91_chief_command_wave2.md"])
        payload = payload_of(root)
        orphans = [d for d in payload["drift_flags"] if d["kind"] == "non_workbook_exclusion_orphan"]
        assert orphans, "清单里塞一条不存在的册必须现形（宪法 §9.5 手工清单必漂移）"
        assert orphans[0]["file"].endswith("91_chief_command_wave2.md")
        assert payload["drift_summary"]["red"] is True
        # 反向自证：盘上有但未落地 ⇒ 报 not_landed 而非孤儿（处置不同，不得混为一谈）
        _write(root / f"{_MINING}/05_missing_p0/99_unlanded.md", "# 未落地编排面\n")
        _gen.NON_WORKBOOK_RELS = tuple(list(saved) + ["05_missing_p0/99_unlanded.md"])
        kinds2 = drift_kinds(payload_of(root))
        assert "non_workbook_exclusion_not_landed" in kinds2
        assert "non_workbook_exclusion_orphan" not in kinds2
    finally:
        _gen.NON_WORKBOOK_RELS = saved


def test_shipped_exemption_list_has_no_true_orphans() -> None:
    """出厂清单自检：真仓里每条豁免路径都必须存在（RB-1 A2.4 实测躺着一具尸）。"""
    root = _REPO_ROOT
    missing = [rel for rel in _gen.NON_WORKBOOK_RELS if not (root / _MINING / rel).is_file()]
    assert missing == [], f"NON_WORKBOOK_RELS 含盘上不存在的孤儿条目：{missing}"


# ---------------------------------------------------------------- ⑤ 口径自述与实现一致
def test_definition_text_matches_implementation(tmp_path: Path) -> None:
    """面⑦：产物自述（definition.covered / method 串）必须与实现同口径，禁"仍写正文 grep"。"""
    payload = payload_of(make_fixture_repo(tmp_path))
    definition = payload["coverage_matrix"]["definition"]
    text = definition["covered"]
    assert "正文" not in text or "不认" in text, text
    assert "grep F" not in text, "自述仍写'正文 grep'＝读者按串复算会得另一套数（RB-1 V0.4/A8.5）"
    for surface in ("文件名", "本册覆盖", "covers"):
        assert surface in text, f"自述缺声明位面：{surface}"
    assert (
        payload["counts"]["mining_books"]["measured"] == payload["coverage_matrix"]["definition"]["tracked_book_count"]
    )
    assert "HEAD" in payload["counts"]["mining_books"]["method"]
    assert "去重" in payload["counts"]["factory_nodes"]["method"], "工厂面自述须写明去重（与 grep -c 不等价）"


def test_factory_duplicate_fac_lines_are_reported(tmp_path: Path) -> None:
    """面⑦补：重复 FAC 行 ⇒ 去重面与 grep 面背离必须现形（RB-1 followup P3 零告警）。"""
    root = make_fixture_repo(tmp_path)
    spm = root / _gen.SPM_REL
    spm.write_text(spm.read_text(encoding="utf-8") + "- node_id: FAC-E0\n  module_ref: MOD-BT-999\n", encoding="utf-8")
    payload = payload_of(root)
    hits = [d for d in payload["drift_flags"] if d["kind"] == "factory_fac_line_duplicates"]
    assert hits, "重复 node_id: FAC- 行必须报（尺报 16、grep 面 17 的背离点）"
    assert hits[0]["claimed"] == 3 and hits[0]["measured"] == 2
    assert payload["drift_summary"]["red"] is True
