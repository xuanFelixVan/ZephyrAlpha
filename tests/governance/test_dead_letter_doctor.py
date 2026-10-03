# [A_test] module_id: MOD-GOV-048 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-048 | scripts/governance/dead_letter_doctor.py | §
# [MODULE] tests.governance.test_dead_letter_doctor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.governance.dead_letter_doctor; scripts.commit_queue（经被测模块复用）; scripts.governance.d3_metadata.batch_creation_tokens; scripts.governance.d3_metadata.add_module_translation（monkeypatch 沙盘化）
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_dead_letter_doctor.py
# [MATURITY] testing
# [INVARIANTS] 全部 tmp_path 沙盘，绝不触碰生产 .runtime/commit_queue 与登记册真源（batch/translation 工具全部 monkeypatch 或指向 tmp 假 registry）；验证三道铁闸（只动表格/不走捷径/只救一次）+ 诊断分类 + 处方 + 审计 + 幂等
# [MODIFY-GUARD] 与 scripts/governance/dead_letter_doctor.py 的 ERROR_CONTRACT 同批
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_dead_letter_doctor.py — 死信急诊分诊台验收（诊断/处方/执行/三道铁闸）。

覆盖清单：
1. 诊断：五族分类正确（含 env 归流/不治/损坏袋/已重投排除）+ 可治愈率；
2. --scan 严格零写 + 幂等（重复 scan 不重复计数、不落任何 doctor 文件）；
3. 处方：JSON 落盘结构（族/步骤/闸二 requeue 末步）+ 审计；
4. 闸三：首救放行、计数、二次拒绝（rc=2）+ 审计 refused；
5. apply 边界（闸一）：r5/vocab/depgraph 族只跳过不执行；CREATE-GUARD 的
   basename 碰撞子族只跳过；宽前缀防呆跳过；
6. apply 正面：creation_token 走 batch_creation_tokens 函数级正门（半集成：
   真 build_block/锚点解析 + 假 insert_block）；plain_zh 走 add_translation
   函数级正门（params 人工供稿）；
7. 自检失败处理：TokenInsertError 折叠为 failed（rc=3）且额度照耗；
8. plain_zh 参数闸：缺 entries 跳过；module_path 不在袋内=invalid_params 拒执行。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.governance.dead_letter_doctor as dld

# ---------------------------------------------------------------------------
# 沙盘：迷你队列 + 五族假袋（死因文本仿生产样本，标记与门禁名逐字对齐）
# ---------------------------------------------------------------------------

_R_TOKEN = (
    "网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 无 creation_token，"
    "禁止造第二真源（trae_060 §2）: ['docs/_working/alpha/report_a.md', "
    "'docs/_working/alpha/report_b.md']. commit 新建文件前 MUST 登记 token"
)
_R_PLAINZH = (
    "网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: "
    "TRANSLATION-COVERAGE: 1 个新建 .py 文件在翻译真源（module_translation_registry.yaml）"
    "缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py"
)
_R_R5 = (
    "网关落盘失败（COMMIT_FAILED）: 门禁 R5-DIGIT-SUFFIX 阻断: R5 数字后缀目录禁止: "
    "docs/_working/alpha/campaign_01/ -> gov_doc_003_directory_semantics R5 禁止 _NN 数字后缀"
)
_R_VOCAB = (
    "网关落盘失败（COMMIT_FAILED）: 门禁 GATE-VOCAB 阻断: [VOCAB-HARDCODE] "
    "新增 .py 文件含词表硬编码（应从 *_vocabulary.yaml 动态加载）"
)
_R_DEPGRAPH = (
    "网关落盘失败（COMMIT_FAILED）: 门禁 DEPGRAPH-ENFORCEMENT 阻断: "
    "[DEPGRAPH-PRE-REGISTRATION] 检测到 depgraph 状态滞后，违反 L1 铁律"
)
_R_ENV = "env_retry: 瞬态锁争用（index.lock）重试耗尽"
_R_UNTREATABLE = "网关落盘失败（COMMIT_FAILED）: 三向合并失败: 注册表三向合并冲突"


def _mk_dead_bag(
    root: Path,
    qid: str,
    *,
    reason: str,
    paths: list[str],
    session: str = "st-alpha-20261003",
    requeued: bool = False,
) -> None:
    """直写 dead/ 假袋（纯沙盘，绕 enqueue）。"""
    (root / "dead").mkdir(parents=True, exist_ok=True)
    item = {
        "qid": qid,
        "session_id": session,
        "created_at": "2026-10-03T00:00:00+00:00",
        "branch": "dev",
        "base_head": None,
        "files": [{"path": p, "blob_sha256": "0" * 64, "blob_ref": "", "action": "modify"} for p in paths],
        "message": f"sandbox bag {qid}",
        "meta": {},
        "dead_at": "2026-10-03T00:01:00+00:00",
        "dead_reason": reason,
    }
    if requeued:
        item["requeued"] = {"new_qid": "q-20261003-st-next-20261003-0001", "at": "2026-10-03T01:00:00+00:00"}
    (root / "dead" / f"{qid}.json").write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8", newline="\n")


@pytest.fixture()
def sandbox(tmp_path: Path) -> Path:
    root = tmp_path / "q"
    (root / "dead").mkdir(parents=True)
    return root


def _mk_five_family_zoo(root: Path) -> None:
    """五族 + env + 不治 + 已重投 各一袋（qid 满足 _QID_RE 白名单）。"""
    _mk_dead_bag(
        root,
        "q-20261003-st-alpha-20261003-0001",
        reason=_R_TOKEN,
        paths=["docs/_working/alpha/report_a.md", "docs/_working/alpha/report_b.md"],
    )
    _mk_dead_bag(
        root,
        "q-20261003-st-alpha-20261003-0002",
        reason=_R_PLAINZH,
        paths=["src/zephyr/alpha/mod.py"],
        session="st-alpha-20261003",
    )
    _mk_dead_bag(
        root,
        "q-20261003-st-alpha-20261003-0003",
        reason=_R_R5,
        paths=["docs/_working/alpha/campaign_01/note.md"],
    )
    _mk_dead_bag(
        root,
        "q-20261003-st-alpha-20261003-0004",
        reason=_R_VOCAB,
        paths=["scripts/governance/alpha_tool.py"],
    )
    _mk_dead_bag(
        root,
        "q-20261003-st-alpha-20261003-0005",
        reason=_R_DEPGRAPH,
        paths=["src/zephyr/alpha/graph_mod.py"],
    )
    _mk_dead_bag(
        root,
        "q-20261003-st-alpha-20261003-0006",
        reason=_R_ENV,
        paths=["docs/_working/alpha/x.md"],
    )
    _mk_dead_bag(
        root,
        "q-20261003-st-alpha-20261003-0007",
        reason=_R_UNTREATABLE,
        paths=["docs/_working/alpha/y.md"],
    )
    # 已重投的 token 族袋：必须被排除出待分诊（其手续由后继袋负责）
    _mk_dead_bag(
        root,
        "q-20261003-st-alpha-20261003-0008",
        reason=_R_TOKEN,
        paths=["docs/_working/alpha/old.md"],
        requeued=True,
    )


# ---------------------------------------------------------------------------
# 1. 诊断分类
# ---------------------------------------------------------------------------


def test_scan_classifies_five_families_env_and_untreatable(sandbox: Path) -> None:
    _mk_five_family_zoo(sandbox)
    report = dld.diagnose(sandbox)
    fam = report["families"]
    assert fam[dld.FAMILY_CREATION_TOKEN]["count"] == 1  # 已重投袋排除
    assert fam[dld.FAMILY_PLAIN_ZH]["count"] == 1
    assert fam[dld.FAMILY_R5_SUFFIX]["count"] == 1
    assert fam[dld.FAMILY_VOCAB]["count"] == 1
    assert fam[dld.FAMILY_DEPGRAPH]["count"] == 1
    assert fam[dld.FAMILY_ENV]["count"] == 1
    assert fam[dld.FAMILY_UNTREATABLE]["count"] == 1
    assert report["total_dead"] == 8
    assert report["already_requeued"] == 1
    assert report["actionable"] == 7
    assert report["healable_count"] == 5
    assert report["healable_ratio"] == round(5 / 7, 4)
    assert report["auto_healable_count"] == 2
    # 代表 qid 指向真袋（可按图索骥）
    assert fam[dld.FAMILY_CREATION_TOKEN]["samples"] == ["q-20261003-st-alpha-20261003-0001"]


def test_scan_counts_corrupt_bag_as_untreatable(sandbox: Path) -> None:
    _mk_dead_bag(sandbox, "q-20261003-st-alpha-20261003-0001", reason=_R_TOKEN, paths=["a.md"])
    (sandbox / "dead" / "q-20261003-st-alpha-20261003-0002.json").write_text("{not-json", encoding="utf-8")
    report = dld.diagnose(sandbox)
    assert report["total_dead"] == 2
    assert report["families"][dld.FAMILY_UNTREATABLE]["count"] == 1
    assert report["families"][dld.FAMILY_CREATION_TOKEN]["count"] == 1


def test_classify_family_reuses_commit_queue_env_truth() -> None:
    # env 真源判定复用检验：即使串里混着 item 措辞，env 标记（index.lock）优先
    assert dld.classify_family("瞬态锁争用 index.lock: 网关落盘失败") == dld.FAMILY_ENV
    assert dld.classify_family("") == dld.FAMILY_UNTREATABLE


# ---------------------------------------------------------------------------
# 2. 零写 + 幂等
# ---------------------------------------------------------------------------


def test_scan_is_zero_write_and_idempotent(sandbox: Path) -> None:
    _mk_five_family_zoo(sandbox)
    before = sorted(str(p.relative_to(sandbox)) for p in sandbox.rglob("*"))
    r1 = dld.diagnose(sandbox)
    r2 = dld.diagnose(sandbox)
    after = sorted(str(p.relative_to(sandbox)) for p in sandbox.rglob("*"))
    # 诊断严格零写：不落 state/audit/处方任何文件（闸三计数也绝不被 scan 触发）
    assert before == after
    assert not (sandbox / dld._STATE_FILENAME).exists()
    assert not (sandbox / dld._AUDIT_FILENAME).exists()
    assert not (sandbox / dld._PRESCRIPTIONS_DIRNAME).exists()
    assert r1 == r2


# ---------------------------------------------------------------------------
# 3. 处方
# ---------------------------------------------------------------------------


def test_prescribe_writes_json_and_audit(sandbox: Path) -> None:
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0001",
        reason=_R_TOKEN,
        paths=["docs/_working/alpha/report_a.md", "docs/_working/alpha/report_b.md"],
    )
    rc, rx = dld.prescribe("q-20261003-st-alpha-20261003-0001", sandbox, operator="tester")
    assert rc == 0
    out = sandbox / dld._PRESCRIPTIONS_DIRNAME / "q-20261003-st-alpha-20261003-0001.json"
    assert out.is_file()
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    assert on_disk["family"] == dld.FAMILY_CREATION_TOKEN
    assert on_disk["qid"] == "q-20261003-st-alpha-20261003-0001"
    # 闸一/闸二/闸三 note 必须在处方里显化
    assert "闸一" in on_disk["gate_one_note"] and "闸二" in on_disk["gate_two_note"]
    # 末步=正门 requeue（闸二），且命令带本 qid
    last = on_disk["steps"][-1]
    assert last["kind"] == "requeue" and last["auto_executable"] is False
    assert "commit_queue.py requeue q-20261003-st-alpha-20261003-0001" in last["command"]
    # 登记步命令含正门工具与派生参数
    reg_step = next(s for s in on_disk["steps"] if s["kind"] == "register_creation_tokens")
    assert "batch_creation_tokens.py" in reg_step["command"]
    assert "--prefix docs/_working/alpha" in reg_step["command"]
    assert "--created-by st-alpha-20261003" in reg_step["command"]
    # 审计：action=prescribe，七字段齐全
    audit = dld._read_audit(sandbox)
    assert len(audit) == 1
    rec = audit[0]
    assert rec["action"] == "prescribe" and rec["operator"] == "tester"
    assert set(rec) == {"ts", "qid", "session_id", "action", "family", "result", "operator"}


def test_prescribe_refuses_requeued_and_bad_qid(sandbox: Path) -> None:
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0001",
        reason=_R_TOKEN,
        paths=["a.md"],
        requeued=True,
    )
    rc, res = dld.prescribe("q-20261003-st-alpha-20261003-0001", sandbox)
    assert rc == 1 and "已重投" in res["detail"]
    # 路径穿越/非法 qid 必须被 _QID_RE 白名单拦下
    rc, res = dld.prescribe("../../etc/passwd", sandbox)
    assert rc == 1
    rc, res = dld.prescribe("q-bad", sandbox)
    assert rc == 1


# ---------------------------------------------------------------------------
# 4. 闸三：只救一次
# ---------------------------------------------------------------------------


def _fake_translation_ok(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """把 add_translation 沙盘化为记录器（永真返回 ok）——不碰生产翻译真源。"""
    import scripts.governance.d3_metadata.add_module_translation as amt

    calls: list[dict] = []

    def fake_add(entry, *, dry_run=False):
        calls.append(entry)
        return 0, "ok"

    monkeypatch.setattr(amt, "add_translation", fake_add)
    return calls


_PLAINZH_PARAMS = {
    "entries": [
        {
            "module_path": "src/zephyr/alpha/mod.py",
            "domain_id": "D_GOV_CODE_QUALITY",
            "name_zh": "阿尔法示例模块",
            "plain_zh": "这个示例模块负责演示死信急诊分诊台的翻译登记通道，解决手续类死信无法补大白话简介的问题。",
        }
    ]
}


def test_gate_three_allows_once_then_refuses(sandbox: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0002",
        reason=_R_PLAINZH,
        paths=["src/zephyr/alpha/mod.py"],
    )
    calls = _fake_translation_ok(monkeypatch)
    qid = "q-20261003-st-alpha-20261003-0002"

    rc1, res1 = dld.apply_healing(qid, sandbox, operator="tester", params=_PLAINZH_PARAMS)
    assert rc1 == 0 and res1["status"] == "ok"
    assert len(calls) == 1
    # 闸三计数已落盘：1
    state = dld.load_state(sandbox)
    assert state["counts"]["st-alpha-20261003::plain_zh"] == 1

    rc2, res2 = dld.apply_healing(qid, sandbox, operator="tester", params=_PLAINZH_PARAMS)
    assert rc2 == 2 and res2["status"] == "refused"
    assert "闸三" in res2["detail"] and "转人工" in res2["detail"]
    # 拒绝后登记工具绝不再被调用，计数不涨
    assert len(calls) == 1
    assert dld.load_state(sandbox)["counts"]["st-alpha-20261003::plain_zh"] == 1
    # 审计：一次执行 + 一次拒绝
    actions = [r["action"] for r in dld._read_audit(sandbox)]
    assert actions == ["apply_executed", "apply_refused_gate3"]


def test_gate_three_keyed_by_session_and_family(sandbox: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """闸三键=(session_id, family)：换会话/换族不连坐。"""
    calls = _fake_translation_ok(monkeypatch)
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-beta-20261003-0001",
        reason=_R_PLAINZH,
        paths=["src/zephyr/beta/mod.py"],
        session="st-beta-20261003",
    )
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-beta-20261003-0002",
        reason=_R_PLAINZH,
        paths=["src/zephyr/beta/mod2.py"],
        session="st-beta-20261003",
    )
    p_beta = {
        "entries": [
            {
                "module_path": "src/zephyr/beta/mod.py",
                "domain_id": "D_GOV_CODE_QUALITY",
                "name_zh": "贝塔示例模块",
                "plain_zh": "贝塔模块演示同一会话同族第二次申请会被闸三拒绝，证明额度按会话与族记数。",
            }
        ]
    }
    rc1, _ = dld.apply_healing("q-20261003-st-beta-20261003-0001", sandbox, params=p_beta)
    rc2, res2 = dld.apply_healing("q-20261003-st-beta-20261003-0002", sandbox, params=p_beta)
    assert rc1 == 0
    assert rc2 == 2 and res2["status"] == "refused"
    assert len(calls) == 1  # 第二袋被闸三拦在执行前


# ---------------------------------------------------------------------------
# 5. apply 边界（闸一）
# ---------------------------------------------------------------------------


def test_apply_skips_prescription_only_families(sandbox: Path) -> None:
    """闸一：r5/vocab/depgraph 族只出处方不执行——apply 返回跳过且零登记册调用。"""
    _mk_dead_bag(
        sandbox, "q-20261003-st-alpha-20261003-0003", reason=_R_R5, paths=["docs/_working/alpha/campaign_01/note.md"]
    )
    _mk_dead_bag(
        sandbox, "q-20261003-st-alpha-20261003-0004", reason=_R_VOCAB, paths=["scripts/governance/alpha_tool.py"]
    )
    _mk_dead_bag(
        sandbox, "q-20261003-st-alpha-20261003-0005", reason=_R_DEPGRAPH, paths=["src/zephyr/alpha/graph_mod.py"]
    )
    for qid in (
        "q-20261003-st-alpha-20261003-0003",
        "q-20261003-st-alpha-20261003-0004",
        "q-20261003-st-alpha-20261003-0005",
    ):
        rc, res = dld.apply_healing(qid, sandbox, operator="tester")
        assert rc == 0 and res["status"] == "skipped"
        assert "闸一" in res["detail"]
    audit = dld._read_audit(sandbox)
    assert [r["action"] for r in audit] == ["apply_skipped"] * 3
    assert {r["family"] for r in audit} == {dld.FAMILY_R5_SUFFIX, dld.FAMILY_VOCAB, dld.FAMILY_DEPGRAPH}
    # 跳过不消耗闸三额度：状态文件根本不落
    assert not (sandbox / dld._STATE_FILENAME).exists()


def test_apply_skips_create_guard_ssot_collision_subfamily(sandbox: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CREATE-GUARD 的 basename 碰撞子族治法是改内容（超闸一）——只出处方。"""
    import scripts.governance.d3_metadata.batch_creation_tokens as bct

    def _must_not_register(*a, **k):  # pragma: no cover - 一旦被调即测试失败
        raise AssertionError("SSOT 碰撞子族禁止触发 token 登记")

    monkeypatch.setattr(bct, "insert_block", _must_not_register)
    reason = (
        "网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 能力重复/basename碰撞"
        "(GATE-SSOT L2): src/zephyr/governance/meta_question/__init__.py: 新文件与已有文件 basename 碰撞"
    )
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0009",
        reason=reason,
        paths=["src/zephyr/governance/meta_question/__init__.py"],
    )
    rc, res = dld.apply_healing("q-20261003-st-alpha-20261003-0009", sandbox, operator="tester")
    assert rc == 0 and res["status"] == "skipped"
    assert "碰撞" in res["detail"] or "闸一" in res["detail"]


def test_apply_token_wide_prefix_guard(sandbox: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """W4 宽前缀防呆（复用正门同源判据）：目标跨多个一级目录 → 跳过转人工确认。"""
    import scripts.governance.d3_metadata.batch_creation_tokens as bct

    def _must_not_register(*a, **k):  # pragma: no cover - 一旦被调即测试失败
        raise AssertionError("宽前缀批禁止自动登记")

    monkeypatch.setattr(bct, "insert_block", _must_not_register)
    reason = "门禁 CREATE-GUARD 阻断: 无 creation_token: ['docs/_working/alpha/a.md', 'src/zephyr/alpha/b.py']"
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0010",
        reason=reason,
        paths=["docs/_working/alpha/a.md", "src/zephyr/alpha/b.py"],
    )
    rc, res = dld.apply_healing("q-20261003-st-alpha-20261003-0010", sandbox, operator="tester")
    assert rc == 0 and res["status"] == "skipped"
    assert "W4" in res["detail"]


# ---------------------------------------------------------------------------
# 6. apply 正面（函数级正门 + 沙盘化登记册）
# ---------------------------------------------------------------------------


def _fake_token_registry(tmp_path: Path) -> Path:
    """tmp 假 registry：含 creation_tokens 段（带 capability 锚点）+ 后续段。"""
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(
        "creation_tokens:\n"
        "- file: docs/old.md\n"
        "  token: cap-old-20260101\n"
        "  created_by: someone\n"
        "  capability: cap\n"
        "other_section:\n"
        "- x: 1\n",
        encoding="utf-8",
    )
    return reg


def test_apply_creation_token_registers_via_batch_functions(
    sandbox: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """半集成：真 load_registered/build_block/锚点解析 + 假 insert_block（零生产写）。"""
    import scripts.governance.d3_metadata.batch_creation_tokens as bct

    monkeypatch.setattr(bct, "_REGISTRY", _fake_token_registry(tmp_path))
    called: dict = {}

    def fake_insert(block, anchor, expect_files=None):
        called["block"] = block
        called["anchor"] = anchor
        called["expect_files"] = expect_files

    monkeypatch.setattr(bct, "insert_block", fake_insert)

    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0001",
        reason=_R_TOKEN,
        paths=["docs/_working/alpha/report_a.md", "docs/_working/alpha/report_b.md"],
    )
    rc, res = dld.apply_healing("q-20261003-st-alpha-20261003-0001", sandbox, operator="tester")
    assert rc == 0 and res["status"] == "ok"
    # 目标清单=死因点名（与袋内一致），已登记的（docs/old.md 不在袋）不掺入
    assert set(called["expect_files"]) == {
        "docs/_working/alpha/report_a.md",
        "docs/_working/alpha/report_b.md",
    }
    # block 内容来自真 build_block：token 格式 + created_by=session + capability 派生
    assert "file: docs/_working/alpha/report_a.md" in called["block"]
    assert "created_by: st-alpha-20261003" in called["block"]
    assert "capability: st-alpha-20261003" in called["block"]
    # 锚点解析来自真 _creation_tokens_section/resolve_anchor（段内最后一条 capability）
    assert called["anchor"] == "cap"
    # 额度消耗 + 审计
    assert dld.load_state(sandbox)["counts"]["st-alpha-20261003::creation_token"] == 1
    audit = dld._read_audit(sandbox)
    assert audit[-1]["action"] == "apply_executed" and audit[-1]["family"] == "creation_token"


def test_apply_creation_token_selfcheck_failure_consumes_quota(
    sandbox: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """写前自检失败（TokenInsertError）必须被折叠为 failed（rc=3），且额度照耗——
    "再失败转人工"语义；二次申请被闸三拒绝。"""
    import scripts.governance.d3_metadata.batch_creation_tokens as bct

    monkeypatch.setattr(bct, "_REGISTRY", _fake_token_registry(tmp_path))

    def boom(block, anchor, expect_files=None):
        raise bct.TokenInsertError("写前自检不过，未落盘任何改动（fail-safe=不写）: 基底陈旧")

    monkeypatch.setattr(bct, "insert_block", boom)
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0001",
        reason=_R_TOKEN,
        paths=["docs/_working/alpha/report_a.md", "docs/_working/alpha/report_b.md"],
    )
    qid = "q-20261003-st-alpha-20261003-0001"
    rc1, res1 = dld.apply_healing(qid, sandbox, operator="tester")
    assert rc1 == 3 and res1["status"] == "failed"
    assert "自检失败" in res1["detail"]
    assert dld.load_state(sandbox)["counts"]["st-alpha-20261003::creation_token"] == 1
    rc2, res2 = dld.apply_healing(qid, sandbox, operator="tester")
    assert rc2 == 2 and res2["status"] == "refused"
    actions = [r["action"] for r in dld._read_audit(sandbox)]
    assert actions == ["apply_failed", "apply_refused_gate3"]


def test_apply_creation_token_nothing_to_do_is_idempotent(
    sandbox: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """目标文件已全部登记 → nothing_to_do，不耗额度（幂等重跑仍放行）。"""
    import scripts.governance.d3_metadata.batch_creation_tokens as bct

    reg = _fake_token_registry(tmp_path)
    monkeypatch.setattr(bct, "_REGISTRY", reg)
    called = {}
    monkeypatch.setattr(bct, "insert_block", lambda *a, **k: called.setdefault("hit", True))
    # 死因点名的两个文件都预先登进假 registry
    reg.write_text(
        reg.read_text(encoding="utf-8").replace(
            "creation_tokens:\n",
            "creation_tokens:\n"
            "- file: docs/_working/alpha/report_a.md\n"
            "  token: cap-a-20261003\n  created_by: s\n  capability: cap\n"
            "- file: docs/_working/alpha/report_b.md\n"
            "  token: cap-b-20261003\n  created_by: s\n  capability: cap\n",
        ),
        encoding="utf-8",
    )
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0001",
        reason=_R_TOKEN,
        paths=["docs/_working/alpha/report_a.md", "docs/_working/alpha/report_b.md"],
    )
    rc, res = dld.apply_healing("q-20261003-st-alpha-20261003-0001", sandbox, operator="tester")
    assert rc == 0 and res["status"] == "nothing_to_do"
    assert "hit" not in called  # 登记函数零调用
    assert not (sandbox / dld._STATE_FILENAME).exists()  # 不耗额度


def test_apply_plain_zh_registers_via_add_translation(sandbox: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """plain_zh 族：--params 人工供稿 → 函数级正门 add_translation；登记对象必须在袋内。"""
    calls = _fake_translation_ok(monkeypatch)
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0002",
        reason=_R_PLAINZH,
        paths=["src/zephyr/alpha/mod.py"],
    )
    rc, res = dld.apply_healing("q-20261003-st-alpha-20261003-0002", sandbox, operator="tester", params=_PLAINZH_PARAMS)
    assert rc == 0 and res["status"] == "ok"
    assert len(calls) == 1
    assert calls[0]["module_path"] == "src/zephyr/alpha/mod.py"
    assert calls[0]["plain_zh"] == _PLAINZH_PARAMS["entries"][0]["plain_zh"]
    assert dld.load_state(sandbox)["counts"]["st-alpha-20261003::plain_zh"] == 1


def test_apply_plain_zh_without_params_skips(sandbox: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """大白话必须人工供稿（doctor 不生成文案）：缺 entries=skipped，零登记册调用。"""
    calls = _fake_translation_ok(monkeypatch)
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0002",
        reason=_R_PLAINZH,
        paths=["src/zephyr/alpha/mod.py"],
    )
    rc, res = dld.apply_healing("q-20261003-st-alpha-20261003-0002", sandbox, operator="tester")
    assert rc == 0 and res["status"] == "skipped"
    assert "供稿" in res["detail"]
    assert calls == []
    assert not (sandbox / dld._STATE_FILENAME).exists()


def test_apply_plain_zh_rejects_foreign_module_path(sandbox: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """闸一护栏：entries.module_path 不在袋内 → invalid_params（rc=1）拒执行。"""
    calls = _fake_translation_ok(monkeypatch)
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0002",
        reason=_R_PLAINZH,
        paths=["src/zephyr/alpha/mod.py"],
    )
    bad = {
        "entries": [
            {
                "module_path": "src/zephyr/other/foreign.py",
                "domain_id": "D_GOV_CODE_QUALITY",
                "name_zh": "外来模块",
                "plain_zh": "这个路径不属于本袋，急诊台必须拒绝为它登记翻译，防止张冠李戴。",
            }
        ]
    }
    rc, res = dld.apply_healing("q-20261003-st-alpha-20261003-0002", sandbox, operator="tester", params=bad)
    assert rc == 1 and res["status"] == "invalid_params"
    assert "不在袋内文件清单" in res["detail"]
    assert calls == []


# ---------------------------------------------------------------------------
# 7. CLI
# ---------------------------------------------------------------------------


def test_cli_scan_json(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _mk_five_family_zoo(sandbox)
    rc = dld.main(["--scan", "--json", "--queue-root", str(sandbox)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["actionable"] == 7 and out["healable_count"] == 5


def test_cli_scan_text_and_default_action(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _mk_five_family_zoo(sandbox)
    # 缺省动作=诊断（不带 --scan 也走 scan）
    assert dld.main(["--queue-root", str(sandbox)]) == 0
    text = capsys.readouterr().out
    assert "死信急诊分诊报告" in text
    assert "可治愈率" in text and "creation_token" in text
    # 零写再确认（CLI 路径同样不落盘）
    assert not (sandbox / dld._STATE_FILENAME).exists()


def test_cli_apply_requires_valid_params_file(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _mk_dead_bag(sandbox, "q-20261003-st-alpha-20261003-0002", reason=_R_PLAINZH, paths=["src/zephyr/alpha/mod.py"])
    rc = dld.main(
        ["--apply", "q-20261003-st-alpha-20261003-0002", "--params", "nonexistent.json", "--queue-root", str(sandbox)]
    )
    assert rc == 1
    assert "不可读" in capsys.readouterr().err


def test_cli_prescribe_and_gate_three_rc(
    sandbox: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI 全链：prescribe → apply（假登记册）→ 二次 apply rc=2。"""
    import scripts.governance.d3_metadata.batch_creation_tokens as bct

    monkeypatch.setattr(bct, "_REGISTRY", _fake_token_registry(tmp_path))
    monkeypatch.setattr(bct, "insert_block", lambda *a, **k: None)
    _mk_dead_bag(
        sandbox,
        "q-20261003-st-alpha-20261003-0001",
        reason=_R_TOKEN,
        paths=["docs/_working/alpha/report_a.md", "docs/_working/alpha/report_b.md"],
    )
    qid = "q-20261003-st-alpha-20261003-0001"
    assert dld.main(["--prescribe", qid, "--queue-root", str(sandbox), "--operator", "cli-tester"]) == 0
    assert "OK" in capsys.readouterr().out
    assert dld.main(["--apply", qid, "--queue-root", str(sandbox), "--operator", "cli-tester"]) == 0
    assert "OK" in capsys.readouterr().out
    rc = dld.main(["--apply", qid, "--queue-root", str(sandbox), "--operator", "cli-tester"])
    assert rc == 2
    assert "REFUSED" in capsys.readouterr().out
    # 审计贯穿 CLI：prescribe + executed + refused 三条
    actions = [r["action"] for r in dld._read_audit(sandbox)]
    assert actions == ["prescribe", "apply_executed", "apply_refused_gate3"]
