# [BLUEPRINT] MOD-LIB-006 | docs/03_modules/_domain_library/blueprint.md | §test
# [A_test] module_id: MOD-GOV_LIB_NEW_MODULE_RECONCILER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_library_reconcilers_red_blue
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_library_reconcilers_red_blue.py — 波13 包13.2 三件红蓝尺（R-5：没红过的尺不是尺）。

覆盖（一一对应丙道三件，全部走 tmp_path 沙盘，**零生产库/零生产路径写**）：
- 件① 新 .py 落 HEAD ⇒ 经 Librarian.act 入馆 + 落地时一次真 grep 派生 potential_consumers
- 件② 投影页与 HEAD 字节不等 ⇒ 恰 1 个幂等落地意图（只含差异页）；等值/已在道 ⇒ 0
- 件③ 零命中审计行 ⇒ 健康 reconciler 读侧点名（加分支，不另起第二台）

红证跑法（本仓 worktree 内，zephyr 可编辑安装在主仓，必须让 worktree src 抢先）::

    PYTHONPATH="$PWD/src:$PWD" python -m pytest \\
        tests/governance/test_library_reconcilers_red_blue.py -q

`_zephyr_resolves_to_this_repo()` 在解析错树时**直接抛错**（不是 skip——skip 藏绿）。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO = Path(__file__).resolve().parents[2]
for _p in (str(_REPO / "src"), str(_REPO)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _zephyr_resolves_to_this_repo() -> None:
    """尺必须吃在本 worktree 的代码上——解析到别的树就抛错（禁 skip 伪装绿）。"""
    import zephyr

    expected = (_REPO / "src" / "zephyr" / "__init__.py").resolve()
    actual = Path(zephyr.__file__).resolve()
    if actual != expected:
        raise RuntimeError(
            f"zephyr 解析到 {actual}，非本仓 {expected}——"
            f'请带 PYTHONPATH="$PWD/src:$PWD" 跑 pytest（否则测的是别的树的代码）'
        )


_zephyr_resolves_to_this_repo()

import zephyr.governance.audit.library_new_module_reconciler as newmod  # noqa: E402
import zephyr.library.library_regen_reconciler as regen  # noqa: E402
from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    make_capability_lookup_health_reconciler,
)


class _FakeLibrarian:
    """沙盘总账：只记 act、只答 lookup（零 DB，零裸 SQL）。"""

    def __init__(self, homes: tuple[str, ...] = ()) -> None:
        self.acts: list[dict[str, Any]] = []
        self._homes = set(homes)

    def act(self, action, asset_id, *, actor="", fields=None, authority=None, detail=None):  # noqa: A002,ANN001,ANN003,ANN201
        self.acts.append(
            {"action": action, "asset_id": asset_id, "actor": actor, "fields": dict(fields or {}), "detail": detail}
        )
        return len(self.acts)

    def lookup(self, query, limit=20, **_kw):  # noqa: ANN001,ANN002,ANN003,ANN201
        hits = [h for h in self._homes if query.replace("\\", "/") in h]
        return [
            {"asset_id": f"MOD:{h}", "home": h, "kind": "module", "status": "active", "title": Path(h).name}
            for h in hits[:limit]
        ]


def _sandbox_repo(tmp_path: Path) -> Path:
    """造一棵最小仓：1 个新件 + 1 个真消费者 + 三层剔除面各一件 + 一张 .md。"""
    files = {
        "src/zephyr/demo/newmod.py": '"""新件：孤岛候选。\n\n细节。\n"""\n',
        "src/zephyr/demo/user.py": "from zephyr.demo.newmod import thing  # 真消费者\n",
        "config/thing.yaml": "module: src/zephyr/demo/newmod.py\n",
        "docs/notes.md": "文档里提了一句 newmod——不算消费者\n",
        "src/zephyr/frontend/display.py": "import zephyr.demo.newmod  # display 层，不算\n",
        "src/zephyr/data/implementations/producer.py": "import zephyr.demo.newmod  # producer 层，不算\n",
        "scripts/ops/newmod_backfill.py": "import zephyr.demo.newmod  # infra 层，不算\n",
        "src/zephyr/demo/kind_provider.py": "import zephyr.demo.newmod  # producer 名，不算\n",
    }
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    return tmp_path


def _grep_returning(*matched: str):
    """注入 grep：固定返回（并记录被问到的 pattern/candidates，证明确实发生了真查询）。"""
    calls: list[tuple[str, list[str]]] = []

    def _grep(pattern: str, candidates: list[str]) -> list[str]:
        calls.append((pattern, list(candidates)))
        return list(matched)

    return _grep, calls


# ───────────────────────────── 件① 新 .py 落 HEAD → 在编 + 消费者派生 ─────────────


class TestNewModuleRegistration:
    def test_ruler_is_red_capable(self, tmp_path):
        """判据本身会红：不在账 ⇒ 判 False；在账 ⇒ 判 True（恒真的尺不配当尺）。"""
        repo = _sandbox_repo(tmp_path)
        assert newmod._is_in_library(_FakeLibrarian(), "src/zephyr/demo/newmod.py") is False
        assert (
            newmod._is_in_library(_FakeLibrarian(("src/zephyr/demo/newmod.py",)), "src/zephyr/demo/newmod.py") is True
        )

    def test_new_py_lands_in_library_via_librarian(self, tmp_path):
        repo = _sandbox_repo(tmp_path)
        lib = _FakeLibrarian()
        # 桩故意把负样本面也"grep 到"——口径过滤必须由尺自己扛住（真 git 通道另测一条）
        grep, calls = _grep_returning(
            "src/zephyr/demo/user.py",
            "config/thing.yaml",
            "src/zephyr/demo/newmod.py",  # 自己不算自己的消费者
            "src/zephyr/demo/readme_notes.md",  # .md 不算
            "src/zephyr/frontend/display.py",  # display 层不算
            "src/zephyr/data/implementations/producer.py",  # producer 层不算
            "scripts/ops/newmod_backfill.py",  # infra 层不算
            "src/zephyr/demo/kind_provider.py",  # producer 名不算
            "docs/notes.md",  # docs 全目录不算
        )
        outcome = newmod.register_new_module_asset(lib, repo, "src/zephyr/demo/newmod.py", actor="st-p1b", grep=grep)
        assert outcome["asset_id"] == "MOD:src/zephyr/demo/newmod.py"
        assert outcome["consumers"] == ["config/thing.yaml", "src/zephyr/demo/user.py"]
        assert outcome["island"] is False
        assert lib.acts and lib.acts[0]["action"] == "register"
        assert lib.acts[0]["fields"]["potential_consumers"] == ["config/thing.yaml", "src/zephyr/demo/user.py"]
        assert lib.acts[0]["fields"]["kind"] == "module"
        assert calls and calls[0][0] == r"\bnewmod\b"  # 一次真查询确实发生
        assert tuple(calls[0][1]) == newmod.CONSUMER_SCOPE_ROOTS  # 查询面=§3.4 三根，不夹带 docs/

    def test_reconcile_registers_and_reports(self, tmp_path):
        repo = _sandbox_repo(tmp_path)
        lib = _FakeLibrarian()
        spec = newmod.make_library_new_module_reconciler(
            type("Gw", (), {"project_root": str(repo)})(),
            librarian_factory=lambda: lib,
        )
        result = spec.reconcile([str(repo / "src/zephyr/demo/newmod.py")], "st-p1b")
        assert result.action == "clean"
        assert "入编 1 件" in result.detail
        assert lib.acts and lib.acts[0]["fields"]["potential_consumers"] == []
        assert "ISLAND-OBSERVE" in result.detail  # 零消费者必须被点名，不静默

    def test_zero_consumers_written_honestly_and_surfaced(self, tmp_path):
        repo = _sandbox_repo(tmp_path)
        lib = _FakeLibrarian()
        grep, _calls = _grep_returning()
        outcome = newmod.register_new_module_asset(lib, repo, "src/zephyr/demo/newmod.py", actor="s", grep=grep)
        assert outcome["consumers"] == [] and outcome["island"] is True
        # 显式空数组（不是 None=保留存量）——账上写的就是 0
        assert lib.acts[0]["fields"]["potential_consumers"] == []

    def test_already_registered_is_not_double_act(self, tmp_path):
        repo = _sandbox_repo(tmp_path)
        lib = _FakeLibrarian(("src/zephyr/demo/newmod.py",))
        spec = newmod.make_library_new_module_reconciler(
            type("Gw", (), {"project_root": str(repo)})(),
            librarian_factory=lambda: lib,
        )
        result = spec.reconcile([str(repo / "src/zephyr/demo/newmod.py")], "s")
        assert lib.acts == []
        assert "入编 0 件" in result.detail

    def test_grep_channel_failure_never_fakes_zero(self, tmp_path):
        """git 通道坏了必须红，不得把"没测到"写成"零消费者"（假绿禁令）。"""
        repo = _sandbox_repo(tmp_path)
        lib = _FakeLibrarian()

        def _boom(pattern: str, candidates: list[str]) -> list[str]:
            raise RuntimeError("git 不可达")

        with pytest.raises(RuntimeError):
            newmod.register_new_module_asset(lib, repo, "src/zephyr/demo/newmod.py", actor="s", grep=_boom)
        assert lib.acts == []  # 没登记成"0 消费者"的假账

    def test_trigger_scope(self, tmp_path):
        repo = _sandbox_repo(tmp_path)
        spec = newmod.make_library_new_module_reconciler(
            type("Gw", (), {"project_root": str(repo)})(),
            librarian_factory=lambda: _FakeLibrarian(),
        )
        assert spec.trigger([str(repo / "src/zephyr/demo/newmod.py")]) is True
        assert spec.trigger([str(repo / "docs/library/code.md")]) is False
        assert spec.trigger([str(repo / "src/zephyr/demo/gone.py")]) is False  # 盘上没有（删除件不入本尺）
        assert spec.gate_id == "LIBRARY-NEW-MODULE"
        assert spec.file_ops == frozenset({"read"})

    def test_doc14_layer_and_scope_predicates(self):
        assert newmod.is_doc14_layer_excluded("src/zephyr/frontend/x.py") is True
        assert newmod.is_doc14_layer_excluded("src/zephyr/data/implementations/y.py") is True
        assert newmod.is_doc14_layer_excluded("scripts/ch/z.py") is True
        assert newmod.is_doc14_layer_excluded("src/zephyr/demo/kind_fetcher.py") is True
        assert newmod.is_doc14_layer_excluded("src/zephyr/demo/real.py") is False
        assert frozenset({".py", ".yaml"}) == newmod.CONSUMER_SCOPE_SUFFIXES

    def test_real_git_grep_channel_on_this_repo(self):
        """真通道自证：本仓实有引用必须被 git grep 抓到（桩测不到的那一半）。"""
        pages = newmod.derive_potential_consumers(_REPO, "src/zephyr/library/library_regen_reconciler.py")
        assert "src/zephyr/governance/audit/reconciliation_registry.py" in pages

    def test_external_spec_hook_contract(self):
        """总筹插行前钩子签名必须先对（插行即生效，不留暗坑）。"""
        assert callable(getattr(newmod, "make_external_reconciler_spec", None))
        src = (_REPO / "src/zephyr/governance/audit/library_new_module_reconciler.py").read_text(encoding="utf-8")
        marker_lines = [ln for ln in src.splitlines() if ln.startswith("# trae_060-reviewed:")]
        assert marker_lines, "CREATE-GUARD 要求 make_*_reconciler 上方 5 行内有 trae_060 标记"


# ───────────────────────────── 件② 投影页落地面（幂等）─────────────────────────────
# 2026-09-30 处置（q0213 捞回）：plan_projection_landing / _projection_pages /
# diff_projection_pages 三 API 自始不存在于 library_regen_reconciler（git 全历史 -S
# 零命中证实）——考卷写未来规格。按 R2 修复令逐例 xfail 留痕（strict=False，规格全文
# 见 defer lane-r2.md 供日班立项）；落地实现日并入即自动转正。守卫意图不删不改。

_XFAIL_PROJECTION = pytest.mark.xfail(
    reason="投影落地面 plan_projection_landing 属未来规格，q0213 捞回；API 从未存在，规格全文见 defer lane-r2",
    strict=False,
)

_PAGES = ("docs/library/INDEX.md", "docs/library/code.md")


def _landing_repo(tmp_path: Path, *, index_body: bytes = b"index v2\n", code_body: bytes = b"code v2\n") -> Path:
    for rel, body in zip(_PAGES, (index_body, code_body), strict=True):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body)
    return tmp_path


class TestProjectionLanding:
    @_XFAIL_PROJECTION
    def test_drift_yields_exactly_one_intent_with_only_drifted_pages(self, tmp_path):
        repo = _landing_repo(tmp_path)
        head = {"docs/library/INDEX.md": b"index v1 (4 days old)\n", "docs/library/code.md": b"code v2\n"}
        sent: list[tuple[str, list[tuple[str, bytes]]]] = []

        def _enqueue(msg: str, files: list[tuple[str, bytes]]) -> dict:
            sent.append((msg, files))
            return {"qid": "q-test"}

        intents = regen.plan_projection_landing(
            repo,
            session_id="s",
            pages=list(_PAGES),
            head_reader=lambda p: head[p],
            pending_view=lambda: {},
            enqueue=_enqueue,
        )
        assert len(intents) == 1
        assert intents[0]["files"] == ["docs/library/INDEX.md"]  # 等值页不得进袋
        assert sent and [f for f, _b in sent[0][1]] == ["docs/library/INDEX.md"]
        assert sent[0][1][0][1] == b"index v2\n"  # 落地面=盘上新字节
        assert "docs/library/code.md" not in intents[0]["files"]

    @_XFAIL_PROJECTION
    def test_second_run_is_zero(self, tmp_path):
        """幂等：同一份待落内容已在队列 pending ⇒ 第二次跑产 0 个意图。"""
        repo = _landing_repo(tmp_path)
        head = {"docs/library/INDEX.md": b"index v1\n", "docs/library/code.md": b"code v2\n"}
        calls: list[list[tuple[str, bytes]]] = []

        def _enqueue(msg: str, files: list[tuple[str, bytes]]) -> dict:
            calls.append(files)
            return {"qid": "q-1"}

        pending: dict[str, str] = {}

        def _pending_view() -> dict[str, str]:
            return dict(pending)

        first = regen.plan_projection_landing(
            repo,
            session_id="s",
            pages=list(_PAGES),
            head_reader=lambda p: head[p],
            pending_view=_pending_view,
            enqueue=_enqueue,
        )
        assert len(first) == 1 and len(calls) == 1
        pending.update({p: hashlib.sha256(b).hexdigest() for p, b in calls[0]})  # 模拟队列已落袋
        second = regen.plan_projection_landing(
            repo,
            session_id="s",
            pages=list(_PAGES),
            head_reader=lambda p: head[p],
            pending_view=_pending_view,
            enqueue=_enqueue,
        )
        assert second == []
        assert len(calls) == 1  # 第二次没再入队

    @_XFAIL_PROJECTION
    def test_equal_bytes_is_noop(self, tmp_path):
        repo = _landing_repo(tmp_path)
        disk_index = (repo / "docs/library/INDEX.md").read_bytes()
        head = {"docs/library/INDEX.md": disk_index, "docs/library/code.md": b"code v2\n"}
        sent: list[Any] = []
        intents = regen.plan_projection_landing(
            repo,
            session_id="s",
            pages=list(_PAGES),
            head_reader=lambda p: head[p],
            pending_view=lambda: {},
            enqueue=lambda m, f: sent.append((m, f)),
        )
        assert intents == [] and sent == []

    @_XFAIL_PROJECTION
    def test_new_page_missing_in_head_lands(self, tmp_path):
        repo = _landing_repo(tmp_path)
        head = {"docs/library/INDEX.md": None, "docs/library/code.md": b"code v2\n"}
        intents = regen.plan_projection_landing(
            repo,
            session_id="s",
            pages=list(_PAGES),
            head_reader=lambda p: head[p],
            pending_view=lambda: {},
            enqueue=lambda m, f: {"qid": "q"},
        )
        assert intents[0]["files"] == ["docs/library/INDEX.md"]

    def test_trigger_excludes_projection_pages(self, tmp_path):
        """自环第一道闸：投影页落地 commit 不再触发本台。"""
        repo = _landing_repo(tmp_path)
        spec = regen.make_library_regen_reconciler(type("Gw", (), {"project_root": str(repo)})())
        assert spec.trigger([str(repo / "docs/library/INDEX.md")]) is False
        assert spec.trigger([str(repo / "src/zephyr/library/foo.py")]) is True

    @_XFAIL_PROJECTION
    def test_page_list_is_generator_derived_not_hardcoded(self, tmp_path):
        """页面清单向生成器要（单一真源，计数不写死在尺里）；空清单 ⇒ 空差异集。"""
        from scripts.governance.generators import generate_library_index as gen

        pages = regen._projection_pages(_REPO)
        expected = ["docs/library/INDEX.md"] + [f"docs/library/{n}.md" for n in sorted(gen._HALL_ASSET_IDS)]
        assert pages == expected
        assert regen.diff_projection_pages(tmp_path, pages=[]) == []

    @_XFAIL_PROJECTION
    def test_reconcile_surfaces_landing_stage(self, tmp_path, monkeypatch):
        """第⑤步接进 _reconcile：有漂移时 stage 文案点名待落地页。"""
        repo = _landing_repo(tmp_path)
        monkeypatch.setattr(
            regen,
            "plan_projection_landing",
            lambda root, session_id="": [
                {"action": "queue_landing", "files": ["docs/library/INDEX.md"], "digests": {}, "receipt": None}
            ],
        )
        monkeypatch.setattr("zephyr.library.collectors.collect_all", lambda *a, **k: [])
        monkeypatch.setattr("zephyr.library.collectors.ingest_all", lambda *a, **k: 0)
        # dev 侧裁-07 缩水闸改造了①②步入账契约（ingest_with_shrink_guard），本测聚焦第⑤步
        # 投影面 stage 文案——顺应当前被提交树的入账签名打桩，判据零变化（2026-09-28 接管合并适配）。
        monkeypatch.setattr(regen, "ingest_with_shrink_guard", lambda conn, lib, collected, actor="": (0, 0, 0))
        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            lambda: type(
                "C", (), {"cursor": lambda self: None, "commit": lambda self: None, "close": lambda self: None}
            )(),
        )
        spec = regen.make_library_regen_reconciler(type("Gw", (), {"project_root": str(repo)})())
        result = spec.reconcile([str(repo / "src/zephyr/x.py")], "s")
        assert "投影待落地 1 页: docs/library/INDEX.md" in result.detail


# ───────────────────────────── 件③ 零命中读侧（同一台加分支）─────────────────────────────


def _health_spec(root: Path):
    return make_capability_lookup_health_reconciler(type("Gw", (), {"project_root": root})())


def _write_audit(root: Path, sid: str, records: list[dict]) -> Path:
    d = root / ".runtime" / "lookup_audit"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{sid}.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    return p


class TestZeroHitReadSide:
    def test_planted_zero_hit_is_named(self, tmp_path):
        _write_audit(
            tmp_path,
            "st-p1b",
            [
                {
                    "ts": "x",
                    "tool": "capability_lookup.find",
                    "query": {"query": "孤岛观测面反查器"},
                    "result_count": 0,
                    "rule_ids": [],
                },
                {
                    "ts": "x",
                    "tool": "capability_lookup.find",
                    "query": {"query": "排班三表一致性"},
                    "result_count": 3,
                    "rule_ids": ["a"],
                },
            ],
        )
        spec = _health_spec(tmp_path)
        result = spec.reconcile(["src/zephyr/demo/newmod.py"], "st-p1b", "普通提交信息")
        assert result.action == "warn"
        assert "零命中" in result.detail and "孤岛观测面反查器" in result.detail
        assert "排班三表一致性" not in result.detail  # 有命中的不得混进来
        assert spec.gate_id == "CAPABILITY-LOOKUP-HEALTH"  # 加分支，未另起一台

    def test_per_session_aggregation(self, tmp_path):
        _write_audit(tmp_path, "sessA", [{"tool": "t", "query": {"query": "能力甲缺件"}, "result_count": 0}])
        _write_audit(tmp_path, "sessB", [{"tool": "t", "query": {"query": "能力乙缺件"}, "result_count": 0}])
        result = _health_spec(tmp_path).reconcile(["src/zephyr/x.py"], "sessA", "")
        assert "sessA" in result.detail and "sessB" in result.detail
        assert result.detail.count("零命中") >= 2  # 按 session 各自计数

    def test_hits_only_stays_clean(self, tmp_path):
        _write_audit(tmp_path, "s1", [{"tool": "t", "query": {"query": "已有能力"}, "result_count": 2}])
        result = _health_spec(tmp_path).reconcile(["src/zephyr/x.py"], "s1", "")
        assert result.action == "clean" and "零命中" not in result.detail

    def test_bypass_log_never_read_as_queries(self, tmp_path):
        """bypass_audit.jsonl 不得被当查询证据（否则本台自己制造"有人查过"的假绿）。"""
        _write_audit(tmp_path, "s2", [{"tool": "t", "query": {"query": "真实查询"}, "result_count": 5}])
        d = tmp_path / ".runtime" / "lookup_audit"
        (d / "bypass_audit.jsonl").write_text(
            json.dumps({"tool": "t", "query": {"query": "不该被点名的桩"}, "result_count": 0}) + "\n", encoding="utf-8"
        )
        result = _health_spec(tmp_path).reconcile(["src/zephyr/x.py"], "s2", "")
        assert "不该被点名的桩" not in result.detail

    def test_ruler_is_red_capable_without_audit_stream(self, tmp_path):
        """没有任何审计流时尺不得凭空点名（防"恒红/恒绿"两种失效）。"""
        result = _health_spec(tmp_path).reconcile(["src/zephyr/x.py"], "s3", "")
        assert result.action == "warn"  # 老语义保留：无日志无 bypass=G6 静默失效嫌疑
        assert "零命中" not in result.detail
