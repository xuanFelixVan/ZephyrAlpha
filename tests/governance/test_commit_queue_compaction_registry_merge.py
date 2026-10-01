# [A_test] module_id: MOD-GOV-046 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-046 | scripts/commit_queue.py | §compaction
# [MODULE] tests.governance.test_commit_queue_compaction_registry_merge
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_compaction_registry_merge.py
# [MATURITY] testing
# [INVARIANTS] 全部 tmp_path 队列根隔离，零生产队列触碰；注册表身份集合并=纯加法（幸存∪victim 独有，零删除零改写）；不可信合并拒绝压缩两袋保留
# [MODIFY-GUARD] W-CASE st-zcloseout-20260928 病案处方 §4（w_case_compaction_lost_update.md）；66 号 §6.2 compaction 语义
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_compaction_registry_merge.py — 同会话 supersede 压缩注册表 lost-update 回归钉。

缺陷真源（病案：docs/_working/qoder_legacy_closeout/w_case_compaction_lost_update.md）：
`_compact_pending` 同会话兄弟 lane 先后入队两袋都携带同一注册表路径时，后袋整份快照
静默顶替前袋——前袋对该注册表的独有增量身份条目（creation_token / 翻译条目）被驱逐，
且无告警（实证：closeout_leaf_books 6 token 三条死袋链，EVICTED-IN-FLIGHT）。

修复语义（本文件钉死）：
1. GREEN 主张：supersede 前对共享注册表族路径做身份集**纯加法合并前递**——幸存快照
   身份集 = survivor ∪ victim 独有（零删除、零改写）；整袋顶替与部分压缩两条路都合并。
2. RED 主张：无合并闸的旧逻辑（gate 打桩直通模拟缺陷时代）同场景必丢 victim token
   ——本文件在未打补丁的生产代码上 RED（attr 不存在 AttributeError）。
3. 拒绝语义：同键异容（同 (file,token) 身份双载不同内容=modification）→ 拒绝压缩，
   两袋都保留，supersedes 链不记，交落地侧条目级三向合并按 FIFO 理顺。
4. 非注册表路径快照整体替换语义不变（66 号 §4 裁定 2）——由 test_commit_queue.py
   TestCompaction 既有用例守护，本文件不重复。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.commit_queue as cq

# 注册表族判据 = landing is_registry_mergeable：catalogs 前缀 + .yaml 后缀（真源同款路径形态）
_REG = "docs/01_policies_and_standards/_registry/catalogs/zz_compaction_merge_probe_registry.yaml"

_TOKEN_TMPL = (
    '- file: {file}\n  token: {token}\n  created_by: {sid}\n  capability: {cap}\n  merge_evaluation: "{note}"\n'
)


def _reg_yaml(tokens: list[dict[str, str]]) -> str:
    """仿真 CCR 形态：标量头 + creation_tokens 顶层 list 族（真册同构，条目首标量=file）。"""
    body = "".join(_TOKEN_TMPL.format(**t) for t in tokens)
    return (
        "# [A_config] merge probe registry (test fixture)\n"
        "module_id: REG-MERGE-PROBE-001\n"
        "ttl: permanent\n"
        "title: compaction merge probe\n"
        "creation_tokens:\n" + body
    )


def _t1(note: str = "victim lane batch") -> dict[str, str]:
    return {
        "file": "docs/_working/probe/leaf_book_a.md",
        "token": "probe-leaf-books-victim-20260928",
        "sid": "st-zcloseout-20260928",
        "cap": "closeout_leaf_books",
        "note": note,
    }


def _t2(note: str = "survivor lane batch") -> dict[str, str]:
    return {
        "file": "docs/_working/probe/leaf_book_b.md",
        "token": "probe-leaf-books-survivor-20260928",
        "sid": "st-zcloseout-20260928",
        "cap": "closeout_leaf_books",
        "note": note,
    }


@pytest.fixture()
def isolated_queue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """tmp 队列根 + 关 C1 合批（否则短窗吸收走 _c1_apply_absorb 顶替了 compaction 场景）。

    worktree_root 传 tmp（无 .git）→ 登记三族预检整体跳过（fail-open 口径，见
    _run_registration_gate）；C1 经出厂 env 旗关闭，compaction 路径独占受测。
    """
    monkeypatch.setenv("ZEPHYR_CQ_C1_DEBOUNCE", "0")
    return tmp_path / "commit_queue"


def _enqueue(root: Path, tmp_path: Path, session: str, msg: str, files: list[tuple[str, bytes]]) -> dict:
    return cq.enqueue_item(
        session,
        msg,
        files,
        queue_root=root,
        options=cq.EnqueueOptions(worktree_root=str(tmp_path)),
    )


def _pending_items(root: Path) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / "pending").glob("q-*.json"))]


def _blob_text(root: Path, item: dict, path: str) -> str:
    entry = next(f for f in item["files"] if f["path"] == path)
    return (root / entry["blob_ref"]).read_text(encoding="utf-8")


class TestCompactionRegistryMergeForward:
    def test_victim_token_survives_whole_supersede(self, isolated_queue: Path, tmp_path: Path) -> None:
        """GREEN 主张（病案 §4 断言一·合并语义）：整袋顶替前 victim 独有 token 并入幸存快照。"""
        ia = _enqueue(isolated_queue, tmp_path, "AI-MERGE1", "victim bag", [(_REG, _reg_yaml([_t1()]).encode())])
        ib = _enqueue(isolated_queue, tmp_path, "AI-MERGE1", "survivor bag", [(_REG, _reg_yaml([_t2()]).encode())])

        pendings = _pending_items(isolated_queue)
        assert [p["qid"] for p in pendings] == [ib["qid"]], "compaction 仍只留最新袋（不因合并闸放弃压缩）"
        survivor = pendings[0]
        assert set(survivor["meta"]["supersedes"]) == {ia["qid"]}, "顶替链可追溯（victim 入 supersedes）"
        text = _blob_text(isolated_queue, survivor, _REG)
        assert _t1()["token"] in text, "victim 独有 token 必须在幸存快照（缺陷即此行丢失）"
        assert _t2()["token"] in text, "幸存自有 token 不动"
        assert _t1()["file"] in text and _t2()["file"] in text, "两侧 file 行齐备（身份集并集）"

    def test_victim_token_survives_partial_compaction(self, isolated_queue: Path, tmp_path: Path) -> None:
        """GREEN 主张（部分压缩路）：victim 袋缩水保留内容件，其注册表增量仍并入幸存快照。"""
        victim_files = [(_REG, _reg_yaml([_t1()]).encode()), ("docs/_working/probe/leaf_book_a.md", b"# leaf book a\n")]
        ia = _enqueue(isolated_queue, tmp_path, "AI-MERGE2", "victim bag with content", victim_files)
        ib = _enqueue(isolated_queue, tmp_path, "AI-MERGE2", "survivor bag", [(_REG, _reg_yaml([_t2()]).encode())])

        pendings = {p["qid"]: p for p in _pending_items(isolated_queue)}
        assert set(pendings) == {ia["qid"], ib["qid"]}, "部分压缩=两袋并存"
        shrunk = pendings[ia["qid"]]
        assert [f["path"] for f in shrunk["files"]] == ["docs/_working/probe/leaf_book_a.md"], (
            "victim 仅缩去被覆盖的注册表条目，内容件保留（病案 0038 丢 6 本 .md 反例）"
        )
        assert shrunk["meta"].get("compacted_partial") is True
        text = _blob_text(isolated_queue, pendings[ib["qid"]], _REG)
        assert _t1()["token"] in text and _t2()["token"] in text, "部分压缩路同样合并前递"

    def test_drain_lands_union_pure_addition(self, isolated_queue: Path, tmp_path: Path) -> None:
        """GREEN 主张（病案 §4 断言二·端到端）：drain 落地面注册表含 T1∪T2，身份集纯增无净删。"""
        ia = _enqueue(isolated_queue, tmp_path, "AI-MERGE3", "victim bag", [(_REG, _reg_yaml([_t1()]).encode())])
        ib = _enqueue(isolated_queue, tmp_path, "AI-MERGE3", "survivor bag", [(_REG, _reg_yaml([_t2()]).encode())])
        landed: dict[str, bytes] = {}

        def recording_landing(item: dict, queue_root: Path) -> cq.LandingResult:
            for f in item.get("files") or []:
                if f.get("blob_ref"):
                    landed[f["path"]] = (queue_root / f["blob_ref"]).read_bytes()
            return cq.LandingResult(ok=True, landed_id=item["qid"])

        stats = cq.drain_queue(isolated_queue, landing=recording_landing)
        assert stats["done"] == 1, "合并语义下 victim 袋被顶替（其增量已并入幸存袋），仅幸存袋落地"
        final = landed[_REG].decode("utf-8")
        assert _t1()["token"] in final, "T1（victim 增量）经合并前递最终在册（缺陷即此行被驱逐）"
        assert _t2()["token"] in final, "T2（survivor 增量）最终在册"
        assert ia["qid"] != ib["qid"]


class TestCompactionRegistryRefusal:
    def test_same_key_divergent_payload_refuses_and_keeps_both(self, isolated_queue: Path, tmp_path: Path) -> None:
        """拒绝语义（病案 §4 处方 (b)）：同身份键双载异容=modification 不可信合并 → 拒绝压缩两袋保留。"""
        divergent = dict(_t1(note="payload diverges on same identity"))
        divergent["cap"] = "closeout_leaf_books_v2"
        ia = _enqueue(isolated_queue, tmp_path, "AI-MERGE4", "victim bag", [(_REG, _reg_yaml([_t1()]).encode())])
        ib = _enqueue(
            isolated_queue,
            tmp_path,
            "AI-MERGE4",
            "survivor bag (same identity, different payload)",
            [(_REG, _reg_yaml([_t2(), divergent]).encode())],
        )

        pendings = {p["qid"]: p for p in _pending_items(isolated_queue)}
        assert set(pendings) == {ia["qid"], ib["qid"]}, "不可信合并=拒绝压缩：两袋都保留"
        assert pendings[ia["qid"]].get("meta", {}).get("compacted_partial") is not True, "victim 袋原样未动"
        survivor = pendings[ib["qid"]]
        assert survivor["meta"]["supersedes"] == [], "拒绝压缩不得记 supersedes 链（顶替未发生）"
        text = _blob_text(isolated_queue, survivor, _REG)
        assert _t2()["token"] in text, "幸存快照原样（合并没有发生）"
        assert "capability: closeout_leaf_books_v2" in text, "幸存侧同键异容条目保持自己的载荷（未被 victim 改写）"
        assert _t1()["note"] not in text, "victim 载荷（其 merge_evaluation 原文）不得混入幸存快照（拒绝=零合并）"
        victim_text = _blob_text(isolated_queue, pendings[ia["qid"]], _REG)
        assert _t1()["note"] in victim_text and _t1()["cap"] in victim_text, "victim 增量完整留在其自袋内，按序落地理顺"


class TestCompactionDefectRepro:
    def test_red_gate_disabled_supersede_loses_victim_token(
        self, isolated_queue: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """RED 主张：合并闸打桩直通=缺陷时代逻辑，同场景 victim token 必丢（病案实证复刻）。

        未打补丁的生产代码无 `_compact_merge_registry_overlap` 属性 → 本用例 AttributeError
        即 RED（缺陷在）；打补丁后桩直通模拟"闸不存在"，断言丢失确实发生（缺陷机理钉）。
        """
        monkeypatch.setattr(cq, "_compact_merge_registry_overlap", lambda *a, **k: True, raising=True)
        ia = _enqueue(isolated_queue, tmp_path, "AI-RED1", "victim bag", [(_REG, _reg_yaml([_t1()]).encode())])
        ib = _enqueue(isolated_queue, tmp_path, "AI-RED1", "survivor bag", [(_REG, _reg_yaml([_t2()]).encode())])

        pendings = _pending_items(isolated_queue)
        assert [p["qid"] for p in pendings] == [ib["qid"]]
        assert set(pendings[0]["meta"]["supersedes"]) == {ia["qid"]}
        text = _blob_text(isolated_queue, pendings[0], _REG)
        assert _t1()["token"] not in text, "缺陷复现：victim token 被静默驱逐（closeout_leaf_books 同款）"
        assert _t2()["token"] in text
