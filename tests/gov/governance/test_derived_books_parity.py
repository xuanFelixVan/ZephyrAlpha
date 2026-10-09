# [A_test] module_id: MOD-GOV_derived_books_parity | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_derived_books_parity
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; yaml; scripts.governance.generators.generate_gate_registry; scripts.governance.d5_architecture.validators.validate_static_manifest_drift; scripts.governance.d7_code.generate_fail_open_register; zephyr.shared.io.yaml_utils; zephyr.governance.audit._git_helpers
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_derived_books_parity.py
# [MATURITY] testing
# [INVARIANTS] 每条尺都必须"能红又能绿"：同一断言配阳性组（构造违规必红）与阴性组（合规必绿），
#              恒绿/恒红判尺无效；全 tmp/内存隔离——只读生产册，绝不写生产路径、绝不起子进程写盘
# [MODIFY-GUARD] 提交链全流通战役 20260925 lane_derived_books：派生册与在册状态一致性
#                （gate_registry 锚点覆盖权 / 位置=在册 / 标量单行自愈通道 / fail-open HEAD 基）的永久回归闸
# [STABILITY] volatile
# [SAFETY] L
# [TTL] permanent
"""派生册 ↔ 在册状态 一致性永久尺（lane_derived_books）。

对症病形（三条，全部实测复现于 docs/_working/chain_fullflow_20260925/lane_gate_derived_books.md）：
1. "顺手跑一下生成器"在热册 gate_registry 上制造 143 增/143 删——逐字段比对后定性为
   **纯条目换位**（内容 0 差），根因=生成器把重定向锚点追加到尾部而在册锚点停在原块位；
2. 27 条 MANUAL_GATES 登记里 15 条被扫描条目吃掉 ⇒ 在册以 `status: active` 报**假活门禁**
   （运行时名册 in_process_gate_registry.yaml 里 0 命中，真身在合并目标内部调用）；
3. GATE-21 `--auto-fix` 对"只错一个派生标量"的失真走**整册再生**，与判据不成比例，
   且与落地侧"标量恒取 ours"的合并器口径互相抵消（改一个数要搅动他人条目）。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


GATE_REG_REL = "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml"
GATE_GEN_REL = "scripts/governance/generators/generate_gate_registry.py"
DRIFT_REL = "scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py"
FAILOPEN_GEN_REL = "scripts/governance/d7_code/generate_fail_open_register.py"


@pytest.fixture(scope="module")
def gate_gen():
    return _load("_ggr_parity", GATE_GEN_REL)


@pytest.fixture(scope="module")
def disk_gates():
    """在册面（本仓工作树＝dev 净检出时即为在册；读盘而非读 HEAD 与工作树同值，刻意不跑 git）。"""
    return yaml.safe_load((REPO_ROOT / GATE_REG_REL).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def drift():
    return _load("_vsmd_parity", DRIFT_REL)


# ---------------------------------------------------------------------------
# 尺 A｜MANUAL_GATES 锚点对同名扫描条目具覆盖权（假活门禁必须被登记真源压住）
# ---------------------------------------------------------------------------

_ANCHOR = {
    "gate_id": "PROBE-MERGED",
    "name": "PROBE-MERGED: 探针（已合并至 PROBE-TARGET）",
    "entry": "N/A (merged into PROBE-TARGET, see redirect_to)",
    "description": "探针锚点",
    "files_trigger": "",
    "always_run": False,
    "category": "commit_gate",
    "status": "deprecated",
    "source": "manual",
    "enforcement_channel": "manual",
    "redirect_to": "PROBE-TARGET",
}
_ENTITY = {
    "gate_id": "PROBE-MERGED",
    "name": "PROBE-MERGED: 垫片文件扫出来的活体（CommitGate, priority=99）",
    "entry": "in-process (GitCommitGateway)",
    "description": "垫片",
    "files_trigger": "",
    "always_run": False,
    "category": "commit_gate",
    "status": "active",
    "source": "commit-gate",
    "own_scope": False,
}


def test_manual_authority_overrides_scanned_entity(gate_gen, monkeypatch) -> None:
    """阳性=同名扫描条目必被锚点替换（原样保留锚点 dict）；阴性=非登记 id 不得被动过。"""
    monkeypatch.setattr(gate_gen, "MANUAL_GATES", [_ANCHOR])
    out = gate_gen._apply_manual_authority([_ENTITY, {"gate_id": "OTHER", "name": "x"}])
    assert out[0] is _ANCHOR, "锚点未获得覆盖权＝被合并门禁仍在册上报 active/in-process（假活登记）"
    assert out[0]["status"] == "deprecated" and out[0]["redirect_to"] == "PROBE-TARGET"
    assert out[1]["gate_id"] == "OTHER", "阴性控制：非登记 id 必须原样通过（尺不是无差别改写）"
    # 红队补硬：覆盖权不得改变条目数（不新增、不吞并）
    assert len(out) == 2


def test_in_book_anchors_are_all_derived(gate_gen, disk_gates) -> None:
    """在册真数据面：MANUAL_GATES 每条都必须能派生落地（0 条被扫描源吃掉）。

    旧口径下 27 条里 15 条隐形（生成器 `if mg["gate_id"] not in auto_ids` 只在扫描源
    没产出同名条目时才放锚点进门）。本尺直接锁死"登记了却派生不出来"这一族。
    """
    gen = gate_gen.generate(existing=disk_gates)
    by_id = {g["gate_id"]: g for g in gen["gates"]}
    swallowed = []
    for mg in gate_gen.MANUAL_GATES:
        got = by_id.get(mg["gate_id"])
        if got is None or got.get("status") != mg.get("status") or got.get("entry") != mg.get("entry"):
            swallowed.append(mg["gate_id"])
    assert not swallowed, f"锚点被扫描条目吃掉（假活/漏登记）: {swallowed}"
    # 阴性控制：集合必须真的非空，否则上面那条断言是恒绿的空集断言
    assert len(gate_gen.MANUAL_GATES) > 20


# ---------------------------------------------------------------------------
# 尺 B｜位置=在册：生成器重跑不得在热册上制造换位 churn
# ---------------------------------------------------------------------------


def test_generation_is_position_stable(gate_gen, disk_gates) -> None:
    """阳性=不带在册喂入时顺序必与在册不同（证明"位置"确实需要被显式保住，尺非恒绿）；

    阴性=带在册喂入时顺序与在册逐位相同 ⇒ 重跑生成器零换位（143 行 churn 的根因面）。
    """
    ids = [g["gate_id"] for g in disk_gates["gates"]]
    preserved = [g["gate_id"] for g in gate_gen.generate(existing=disk_gates)["gates"]]
    assert preserved == ids, "带在册喂入后条目换位＝重跑生成器仍会在热册上制造百行级 churn"
    naive = [g["gate_id"] for g in gate_gen.generate()["gates"]]
    assert naive != ids, (
        "阴性控制失效：不喂在册的顺序竟然与在册一致——说明顺序保位逻辑已成死码或扫描序意外同构，本尺失去信号，须重判口径"
    )


def test_content_parity_zero_drift_and_ignores_order(gate_gen, disk_gates) -> None:
    """生成器台第二半（旧 --check 只比标量⇒条数恰好相等时恒绿）＋ 行序不判红。"""
    gen = gate_gen.generate(existing=disk_gates)
    cmp = gate_gen.compare_with_disk(disk_gates, gen)
    assert cmp == {"disk_missing": [], "disk_extra": [], "field_drift": []}, f"派生册与在册内容不一致: {cmp}"
    # 位置差不判红（判据对准内容不对准行序）
    shuffled = {"gates": list(reversed(disk_gates["gates"]))}
    assert gate_gen.compare_with_disk(shuffled, gen) == cmp, "行序差被判红＝把无语义的顺序当契约，必复发 churn"
    # 阳性控制：三类失真各必红
    missing = {"gates": [g for g in disk_gates["gates"] if g["gate_id"] != "CREATE-GUARD"]}
    assert gate_gen.compare_with_disk(missing, gen)["disk_missing"] == ["CREATE-GUARD"]
    extra = {"gates": [*disk_gates["gates"], {"gate_id": "ZZ-GHOST", "name": "幽灵"}]}
    assert gate_gen.compare_with_disk(extra, gen)["disk_extra"] == ["ZZ-GHOST"]
    drifted = {
        "gates": [({**g, "status": "bogus"} if g["gate_id"] == "CREATE-GUARD" else g) for g in disk_gates["gates"]]
    }
    assert any("CREATE-GUARD" in d for d in gate_gen.compare_with_disk(drifted, gen)["field_drift"])


def test_gate_registry_anchors_are_not_live_in_runtime_roster(disk_gates) -> None:
    """交叉轴：在册标 deprecated+redirect 的锚点，其目标必须在运行时名册里活着。

    这是"改成锚点会不会把门禁改没了"的反问闸——只放松登记态、不放松执行面。
    """
    roster = yaml.safe_load(
        (REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml").read_text(
            encoding="utf-8"
        )
    )
    live = {g.get("gate_id") for g in (roster.get("gates") or []) if isinstance(g, dict)}
    # 执行面真源两路：in-process 运行时名册 + .pre-commit-config.yaml 钩子（GATE-C2 类在后者）
    pcc = yaml.safe_load((REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    for repo in pcc.get("repos") or []:
        for hook in repo.get("hooks") or []:
            for key in ("id", "name"):
                token = str(hook.get(key) or "")
                live.add(token)
                live.add(token.split(":", 1)[0].strip().upper())
    assert "FUNCTION-DUP" in live and "GATE-C2" in live, "执行面取数口失效＝本尺恒绿，判无效"
    anchors = [g for g in disk_gates["gates"] if str(g.get("entry", "")).startswith("N/A")]
    assert anchors, "在册锚点为空＝本尺恒绿，判无效"
    unmet = []
    for a in anchors:
        tgt = str(a.get("redirect_to", ""))
        if tgt and not tgt.startswith(("gate_audit_report", "docs/")) and tgt not in live:
            unmet.append((a["gate_id"], tgt))
    assert not unmet, f"锚点重定向目标不在运行时名册＝重定向后无处可去（执行面真丢）: {unmet}"


# ---------------------------------------------------------------------------
# 尺 C｜派生标量单行自愈：检测侧与落地侧共用一条改写真源
# ---------------------------------------------------------------------------

_BOOK = """# 头部注释（不得被改写）
module_id: PS-REG-014
total_gates: {declared}
gates:
{body}
"""


def _book(declared: int, actual: int) -> str:
    body = "".join(f"  - gate_id: G{i}\n    name: '门禁 {i}'\n" for i in range(actual))
    return _BOOK.format(declared=declared, body=body)


def test_heal_scalar_changes_exactly_one_line() -> None:
    """阳性=174 vs 180 必被刷正且只动那一行（顺序/其余字节全等）。"""
    from zephyr.shared.io.yaml_utils import heal_derived_scalars

    src = _book(174, 180)
    out, changes = heal_derived_scalars(src, {"total_gates": "gates"})
    assert changes == [("total_gates", 174, 180)], f"标量失真必须被刷正，实得 {changes}"
    diff = [(a, b) for a, b in zip(src.splitlines(), out.splitlines(), strict=False) if a != b]
    assert diff == [("total_gates: 174", "total_gates: 180")], f"改一行以外的任何东西都是 churn: {diff}"
    assert out.startswith("# 头部注释"), "头部注释被连带改写＝热册头部被工具吃掉"


def test_heal_scalar_noop_and_conservative_branches() -> None:
    """阴性/保守三组：已一致不动、顶层重复键不动、段非集合不动（绝不把假成功写进册）。"""
    from zephyr.shared.io.yaml_utils import heal_derived_scalars

    same, ch = heal_derived_scalars(_book(180, 180), {"total_gates": "gates"})
    assert ch == [] and same == _book(180, 180), "阴性控制：已一致必须零改动（尺非恒红）"

    dup = _book(174, 180) + "total_gates: 100\n"
    out2, ch2 = heal_derived_scalars(dup, {"total_gates": "gates"})
    assert ch2 == [] and out2 == dup, "顶层同键多行＝不知该改哪行，必须一律不动"

    nosec, ch3 = heal_derived_scalars("total_gates: 5\n", {"total_gates": "gates"})
    assert ch3 == [] and nosec == "total_gates: 5\n", "段不是集合时无从判定长度，必须不动"

    crlf, ch4 = heal_derived_scalars(_book(174, 180).replace("\n", "\r\n"), {"total_gates": "gates"})
    assert ch4 == [("total_gates", 174, 180)] and crlf.count("\r\n") == crlf.count("\n"), (
        "行尾保真：CRLF 册不得被改成混合行尾"
    )


def test_gate21_selfcheck_fix_channel_is_scalar_only(drift) -> None:
    """GATE-21 判据与修复通道必须同口径：自洽台的 fix 只能是单行自愈，不得整册再生。

    阳性=在册 CHECKS 全部通过；阴性控制=注入一条"fix 指向整册生成器"的自洽台，
    判据谓词必须判 False（否则本尺恒绿）。
    """

    def scalar_only(item: dict) -> bool:
        cmd = [str(x) for x in (item.get("fix") or [])]
        return bool(cmd) and "--heal-derived-totals" in cmd and not any("generate_" in c for c in cmd)

    selfchecks = [c for c in drift.CHECKS if "selfcheck" in c]
    assert selfchecks, "自洽台为空＝本尺无对象，判无效"
    for c in selfchecks:
        assert scalar_only(c), f"自洽台 fix 通道越界（整册再生热册）: {c['name']} → {c.get('fix')}"
    assert not scalar_only({"fix": ["python", "scripts/governance/generators/generate_gate_registry.py"]}), (
        "阴性控制：整册再生必须被判 False"
    )
    # 配对表仍与落地侧同源（口径漂移=两半各说各话，L4 S-24 已立法）
    landing = _load("_cql_pairs", "scripts/governance/commit_queue_landing.py")
    assert drift.derived_total_pairs() == landing._DERIVED_TOTAL_PAIRS


def test_heal_derived_totals_writes_tmp_copy_only(drift, tmp_path: Path) -> None:
    """生产函数级验尺：--heal-derived-totals 的落盘动作确实只刷标量（tmp 隔离，零写生产册）。"""
    rel = Path("docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml")
    p = tmp_path / rel
    p.parent.mkdir(parents=True)
    p.write_text(_book(174, 180), encoding="utf-8", newline="\n")
    import copy

    checks = copy.deepcopy(drift.CHECKS)
    drift.CHECKS[:] = [c for c in checks if "selfcheck" in c]
    try:
        notes = drift.heal_derived_totals(root=tmp_path)
    finally:
        drift.CHECKS[:] = checks
    assert any("HEALED" in n and "174 → 180" in n for n in notes), f"自愈通道未刷正: {notes}"
    got = (tmp_path / rel).read_text(encoding="utf-8")
    assert got == _book(180, 180), "落盘内容必须只有标量归位，其余逐字节等值"


# ---------------------------------------------------------------------------
# 尺 D｜fail-open 登记册入选集以 HEAD 树为准（同族第四例）
# ---------------------------------------------------------------------------


@pytest.fixture()
def failopen():
    return _load("_gfo_parity", FAILOPEN_GEN_REL)


def test_fail_open_head_basis_excludes_inflight(failopen, monkeypatch, tmp_path: Path) -> None:
    """阳性=在途未提交件不得入登记册；阴性=HEAD 内文件必入；补刀=HEAD 取不到必抛。"""
    root = tmp_path / "repo"
    (root / "scripts" / "d7").mkdir(parents=True)
    (root / "scripts" / "d7" / "tracked_ok.py").write_text("x = 1\n", encoding="utf-8")
    (root / "scripts" / "d7" / "zz_inflight.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(failopen, "REPO_ROOT", root)
    monkeypatch.setattr(failopen, "SCAN_ROOTS", ("scripts",))
    monkeypatch.setattr(
        "zephyr.governance.audit._git_helpers.git_ls_tree_paths",
        lambda repo_root, ref="HEAD", suffixes=(): ["scripts/d7/tracked_ok.py"],
    )
    names = {p.name for p in failopen._iter_py()}
    assert names == {"tracked_ok.py"}, f"入选集必须以 HEAD 为准，实得 {names}"

    monkeypatch.setattr(
        "zephyr.governance.audit._git_helpers.git_ls_tree_paths",
        lambda repo_root, ref="HEAD", suffixes=(): None,
    )
    with pytest.raises(RuntimeError, match="拒绝降回工作树枚举"):
        failopen._iter_py()


# ---------------------------------------------------------------------------
# 尺 E｜普查台账：三本派生册"在册有物无 / 现产未刷"的漂移登记簿
# ---------------------------------------------------------------------------

# 归零路径：重跑各自生成器并由属主批落地后，把本表对应项删除（或删除后计数归零）——
# 表内每一项都必须是"别人正在修的"，新增项=新病形，须先立案再登记（禁靠扩表让尺变绿）。
_CENSUS_LEDGER: dict[str, dict[str, object]] = {
    "config/governance_operations_map.yaml": {
        # L3 属主批待落（HEAD 基生成器已在册，重跑即归零）：幻影 3 件＝他包在途 .py 曾被烤进图
        "phantom_files": {
            "scripts/governance/check_meta_question_audit_reconcile.py",
            "scripts/sector_line/build_gpu_input_pack.py",
            "src/zephyr/intelligence/budget_analyzer.py",
        },
    },
    "docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml": {
        # 同族第四例（本包治生成侧，在册 29 条/12 文件待属主批重生成归零）
        "phantom_files": {
            "scripts/ai_layer/gen_ai_layer_monthly_checkup.py",
            "scripts/ai_layer/gen_search_veins.py",
            "src/zephyr/ai_layer/heritage/closure_check.py",
            "src/zephyr/ai_layer/perceive/search_orders.py",
            "src/zephyr/ai_layer/redline/drop_gate.py",
            "src/zephyr/ai_layer/redline/freedom_weekly_report.py",
            "src/zephyr/ai_layer/redline/negative_list_gates.py",
            "src/zephyr/ai_layer/redline/no_delete_manifest.py",
            "src/zephyr/ai_layer/tools/__init__.py",
            "src/zephyr/governance/registry_projection/generator.py",
            "src/zephyr/governance/registry_projection/state.py",
            "src/zephyr/governance/standards_governance/standard_checkup.py",
            "src/zephyr/intelligence/switch_engine/shadow_runner.py",
        },
    },
}


def _head_tree() -> set[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-tree", "-r", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert out.returncode == 0, "git ls-tree 失败＝本尺无从判定，禁静默放行"
    return set(out.stdout.splitlines())


def _listed_paths(book: dict, rel: str) -> set[str]:
    """按册各自的字段口径抽出"条目指向的文件路径"（POSIX，去 #锚点）。"""
    raw: set[str] = set()
    if rel.endswith("governance_operations_map.yaml"):
        for mods in (book.get("families") or {}).values():
            for m in mods or []:
                if m.get("path"):
                    raw.add(str(m["path"]))
    else:
        for bucket in ("hardcoded_default_permit", "money_path_no_trace", "undeclared_needs_review"):
            for e in (book.get(bucket) or {}).get("entries") or []:
                if e.get("file"):
                    raw.add(str(e["file"]))
    return {x.split("#")[0] for x in raw}


def test_census_phantom_ledger_is_exact() -> None:
    """台账尺：在册条目指向"HEAD 里根本不存在"的文件——集合必须逐条等于登记值。

    既能红（多一条幻影=新病形；少一条=已归零须删表项）又能绿（当前实测集合）。
    阴性控制组在 test_census_ledger_detects_fabricated_phantom。
    """
    tree = _head_tree()
    for rel, expect in _CENSUS_LEDGER.items():
        book = yaml.safe_load((REPO_ROOT / rel).read_text(encoding="utf-8"))
        phantoms = _listed_paths(book, rel) - tree
        assert phantoms == set(expect["phantom_files"]), (
            f"{rel} 幻影集合与台账不符（既可能变坏也可能已归零，两种都要显式改台账）"
        )


def test_census_ledger_detects_fabricated_phantom(tmp_path: Path) -> None:
    """阴性控制：把幻影塞进册再走同一判据必须被抓到（证明上一条不是恒绿断言）。"""
    tree = {"src/zephyr/real.py"}
    book = {"families": {"L1": [{"path": "src/zephyr/real.py"}, {"path": "src/zephyr/ghost.py"}]}}
    found = _listed_paths(book, "x/governance_operations_map.yaml") - tree
    assert found == {"src/zephyr/ghost.py"}
