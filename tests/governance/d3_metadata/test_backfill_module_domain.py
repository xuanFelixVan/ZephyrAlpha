# [A_test] module_id: MOD-GOV_backfill_module_domain_tests | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/backfill_module_domain.py | §
# [MODULE] tests.governance.d3_metadata.test_backfill_module_domain
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_backfill_module_domain.py — [DOMAIN] 确定性补标生成器单测

覆盖契约（W4c）：
- TestSiblingVote        a 级：同目录兄弟 ≥2 一致才用；单兄弟不成立（d 未决）
- TestOwnershipMap       b 级：path_ownership_map 同 owner_blueprint 家族票
- TestDepgraphFallback   c 级：depgraph PG 兜底（file 节点 / prefix 表），PG 故障=无证据
- TestVocabularyGuard    非法域值拒写（SSoT 词表外一律未决）；别名值可用
- TestDeprecatedMigration 既有废弃值优先迁移到词表唯一 replacement，压过推断票；N/A 目标回落投票
- TestGitDirtyGuard      --apply 跳过 git 脏文件（假 git runner 注入）
- TestIdempotent         二次跑零变更（already_ok，不改字节）
- TestBatchLimit         单批上限
- TestEvidenceConflictHold 独立证据反对目录票 → needs_review 不写盘；--allow-conflict-write 才放量
- TestByteFidelity       CRLF/BOM/其余字节零改动；yaml 治理锚定块插入；无锚点不瞎插
- TestGhost              清单幽灵条目（磁盘无文件）

测试隔离：全部在 tmp_path 造迷你仓库 + 迷你词表，不读不写真实仓库业务路径
（宪法"测试禁写生产路径"）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts" / "governance" / "d3_metadata"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import backfill_module_domain as bmd  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VOCAB_YAML = """\
schema_version: "0.0.1-test"
values:
  - value: D_ALPHA
    definition: "测试域甲"
  - value: D_BETA
    definition: "测试域乙"
    aliases: ["D_BETA_LEGACY"]
deprecated_values:
  - value: D_OLD
    replacement: D_ALPHA
    reason: "测试废弃域，迁移目标唯一"
  - value: D_ORPHAN
    replacement: "N/A（无迁移目标）"
    reason: "测试废弃域，无唯一目标"
"""


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _mod(rel: str, domain: str | None = None, *, extra: str = "") -> str:
    """构造带 # [MODULE] 头的 .py 文本（domain=None → 缺 [DOMAIN]）。"""
    lines = ["# [BLUEPRINT] MOD-TEST-001", f"# [MODULE] {rel.replace('/', '.').replace('.py', '')}"]
    if domain is not None:
        lines.append(f"# [DOMAIN] {domain}")
    lines += ["# [TTL] permanent", '"""docstring."""', extra]
    return "\n".join(l for l in lines if l) + "\n"


class _FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows


class _FakePG:
    """假 depgraph 连接：按 SQL 文本分流 nodes / domain_mapping。"""

    def __init__(self, nodes=None, mapping=None, raise_exc=False):
        self.nodes = nodes or []
        self.mapping = mapping or []
        self.raise_exc = raise_exc
        self.closed = False

    def execute(self, sql, params=None):  # noqa: ARG002 — 兼容 sqlite3 语义
        if self.raise_exc:
            raise RuntimeError("pg down")
        if "from nodes" in sql:
            return _FakeCursor(self.nodes)
        if "from domain_mapping" in sql:
            return _FakeCursor(self.mapping)
        return _FakeCursor([])

    def close(self):
        self.closed = True


def _ownership_yaml(entries: list[tuple[str, str]]) -> str:
    body = "".join(
        "  - path: '{p}'\n    owner_blueprint: '{bp}'\n    claim_type: 'depgraph_node'\n\n".format(p=p, bp=bp)
        for p, bp in entries
    )
    return f"meta:\n  total_path_claims: {len(entries)}\nownership:\n{body}"


def _registry_yaml(entries: list[tuple[str, str]]) -> str:
    body = "".join(
        f"- domain: {dom}\n  subdomain: sub_{i}\n  ssot_path: {prefix}\n"
        for i, (prefix, dom) in enumerate(entries)
    )
    return f"module_id: REG-TEST\nentries:\n{body}"


def _run(
    repo: Path,
    targets: list[str],
    *,
    apply: bool = False,
    batch: int = 200,
    git_runner=None,
    nodes=None,
    mapping=None,
    pg_down: bool = False,
    ownership_entries=(),
    registry_entries=(),
    skip_git_guard: bool = False,
    min_support: int = 2,
    vocab_exists: bool = True,
    allow_conflict_write: bool = False,
):
    out_dir = repo / ".runtime/tmp/test_out"
    vocab_path = repo.parent / f"{repo.name}_vocab/alpha_vocabulary.yaml"
    if vocab_exists:
        vocab = _write(Path(vocab_path), VOCAB_YAML)
    else:
        vocab = Path(vocab_path)
    own = _write(repo.parent / f"{repo.name}_own/path_ownership_map.yaml", _ownership_yaml(list(ownership_entries)))
    reg = _write(
        repo.parent / f"{repo.name}_reg/functional_domain_registry.yaml",
        _registry_yaml(list(registry_entries)),
    )
    return bmd.process(
        selection=bmd.TargetSelection(list_path=None, all_mode=False, files=targets),
        locations=bmd.EvidenceLocations(
            repo=repo,
            vocab_file=str(vocab),
            ownership_path=own,
            registry_path=reg,
        ),
        policy=bmd.BackfillWritePolicy(
            apply=apply,
            batch=batch,
            min_sibling_support=min_support,
            skip_git_guard=skip_git_guard,
            allow_conflict_write=allow_conflict_write,
        ),
        output=bmd.OutputOptions(out_dir=out_dir, write_report=True),
        hooks=bmd.InjectionHooks(
            git_runner=git_runner,
            conn_factory=(lambda: _FakePG(nodes=nodes, mapping=mapping, raise_exc=pg_down)),
        ),
    )


def _rows_by_path(res) -> dict[str, dict]:
    return {r["path"]: r for r in res["rows"]}


def _fake_git(dirty: list[str]):
    def runner(args, cwd):  # noqa: ARG001 — 假 runner 忽略 cwd
        class P:
            returncode = 0
            stdout = "".join(f" M {p}\n" for p in dirty)

        return P()

    return runner


# ---------------------------------------------------------------------------
# a 级：同目录兄弟票
# ---------------------------------------------------------------------------


class TestSiblingVote:
    def test_two_agreeing_siblings_infer_and_write(self, tmp_path: Path):
        _write(tmp_path / "src/pkg/one.py", _mod("src/pkg/one.py", "D_ALPHA"))
        _write(tmp_path / "src/pkg/two.py", _mod("src/pkg/two.py", "D_ALPHA"))
        target = _write(tmp_path / "src/pkg/three.py", _mod("src/pkg/three.py"))
        res = _run(tmp_path, ["src/pkg/three.py"])
        row = _rows_by_path(res)["src/pkg/three.py"]
        assert row["inferred"] == "D_ALPHA"
        assert row["inference_source"] == "sibling_vote"
        assert row["level"] == bmd.LEVEL_A
        assert row["action"] == "would_change" and row["reject_reason"] == "dry_run"
        assert "DOMAIN" not in target.read_text(encoding="utf-8")  # 干跑零写入

        res2 = _run(tmp_path, ["src/pkg/three.py"], apply=True)
        assert _rows_by_path(res2)["src/pkg/three.py"]["action"] == "inserted_after_module"
        text = target.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert lines[1] == "# [MODULE] src.pkg.three"  # 插在不破坏既有头
        assert "# [DOMAIN] D_ALPHA" in lines

    def test_single_sibling_below_threshold_is_unresolved(self, tmp_path: Path):
        _write(tmp_path / "src/only/one.py", _mod("src/only/one.py", "D_ALPHA"))
        target = _write(tmp_path / "src/only/two.py", _mod("src/only/two.py"))
        res = _run(tmp_path, ["src/only/two.py"], apply=True)
        row = _rows_by_path(res)["src/only/two.py"]
        assert row["inferred"] == "" and row["reject_reason"] == "below_threshold"
        assert "# [DOMAIN]" not in target.read_text(encoding="utf-8")  # 绝不瞎填

    def test_sibling_tie_prefers_deterministic_choice(self, tmp_path: Path):
        _write(tmp_path / "src/tie/a.py", _mod("src/tie/a.py", "D_ALPHA"))
        _write(tmp_path / "src/tie/b.py", _mod("src/tie/b.py", "D_ALPHA"))
        _write(tmp_path / "src/tie/c.py", _mod("src/tie/c.py", "D_BETA"))
        _write(tmp_path / "src/tie/d.py", _mod("src/tie/d.py", "D_BETA"))
        _write(tmp_path / "src/tie/target.py", _mod("src/tie/target.py"))
        runs = {_run(tmp_path, ["src/tie/target.py"])["rows"][0]["inferred"] for _ in range(3)}
        assert len(runs) == 1  # 平票也必须确定性（同输入同输出）


# ---------------------------------------------------------------------------
# b 级：path_ownership_map 家族票 / 功能域注册表前缀
# ---------------------------------------------------------------------------


class TestOwnershipMap:
    def test_cohort_vote_across_directories(self, tmp_path: Path):
        _write(tmp_path / "src/svc/x.py", _mod("src/svc/x.py", "D_BETA"))
        _write(tmp_path / "src/svc/y.py", _mod("src/svc/y.py", "D_BETA"))
        _write(tmp_path / "src/svc/z.py", _mod("src/svc/z.py", "D_BETA"))
        target = _write(tmp_path / "tests/orphan/test_lonely.py", _mod("tests/orphan/test_lonely"))
        res = _run(
            tmp_path,
            ["tests/orphan/test_lonely.py"],
            apply=True,
            ownership_entries=[
                ("tests/orphan/test_lonely.py", "MOD-SHARED-7"),
                ("src/svc/x.py", "MOD-SHARED-7"),
                ("src/svc/y.py", "MOD-SHARED-7"),
            ],
        )
        row = _rows_by_path(res)["tests/orphan/test_lonely.py"]
        assert row["inference_source"] == "ownership_map" and row["level"] == bmd.LEVEL_B
        assert row["inferred"] == "D_BETA"
        assert "# [DOMAIN] D_BETA" in target.read_text(encoding="utf-8")

    def test_prefix_used_when_no_sibling_evidence(self, tmp_path: Path):
        _write(tmp_path / "src/zone/lone.py", _mod("src/zone/lone"))
        res = _run(tmp_path, ["src/zone/lone.py"], apply=True, registry_entries=[("src/zone/", "D_BETA")])
        row = _rows_by_path(res)["src/zone/lone.py"]
        assert row["inference_source"] == "domain_registry_prefix"
        assert row["level"] == bmd.LEVEL_B
        assert row["inferred"] == "D_BETA"
        assert row["chosen_note"] == "ssot_path 最长前缀=src/zone/"
        assert row["evidence"].count("|") == len(bmd.SOURCE_ORDER) - 1  # 六级证据全留，不静默丢
        assert "# [DOMAIN] D_BETA" in (tmp_path / "src/zone/lone.py").read_text(encoding="utf-8")

    def test_sibling_vote_outranks_prefix(self, tmp_path: Path):
        _write(tmp_path / "src/prio/a.py", _mod("src/prio/a", "D_ALPHA"))
        _write(tmp_path / "src/prio/b.py", _mod("src/prio/b", "D_ALPHA"))
        _write(tmp_path / "src/prio/c.py", _mod("src/prio/c"))
        res = _run(tmp_path, ["src/prio/c.py"], registry_entries=[("src/prio/", "D_BETA")])
        row = _rows_by_path(res)["src/prio/c.py"]
        assert row["inference_source"] == "sibling_vote" and row["inferred"] == "D_ALPHA"
        assert "domain_registry_prefix=D_BETA" in row["evidence"]  # 弱证据仍留列可审


# ---------------------------------------------------------------------------
# c 级：depgraph PG 兜底
# ---------------------------------------------------------------------------


class TestDepgraphFallback:
    def test_file_node_exact_match(self, tmp_path: Path):
        _write(tmp_path / "src/db/only.py", _mod("src/db/only"))
        res = _run(
            tmp_path,
            ["src/db/only.py"],
            apply=True,
            nodes=[{"path": "src/db/only.py", "domain_id": "D_BETA", "granularity": "file"}],
        )
        row = _rows_by_path(res)["src/db/only.py"]
        assert row["level"] == bmd.LEVEL_C and row["inference_source"] == "depgraph_node"
        assert row["inferred"] == "D_BETA"
        assert "# [DOMAIN] D_BETA" in (tmp_path / "src/db/only.py").read_text(encoding="utf-8")

    def test_prefix_table_and_directory_node(self, tmp_path: Path):
        _write(tmp_path / "src/dirnode/only.py", _mod("src/dirnode/only"))
        res = _run(
            tmp_path,
            ["src/dirnode/only.py"],
            mapping=[{"path_prefix": "src/dirnode/", "domain_id": "D_ALPHA"}],
            nodes=[{"path": "src/dirnode", "domain_id": "D_BETA", "granularity": "directory"}],
        )
        row = _rows_by_path(res)["src/dirnode/only.py"]
        assert row["inference_source"] == "depgraph_dir_node"  # 目录节点优先于粗前缀表
        assert row["inferred"] == "D_BETA"

    def test_pg_failure_degrades_to_no_evidence(self, tmp_path: Path):
        _write(tmp_path / "src/nodb/only.py", _mod("src/nodb/only"))
        target = tmp_path / "src/nodb/only.py"
        res = _run(tmp_path, ["src/nodb/only.py"], apply=True, pg_down=True)
        row = _rows_by_path(res)["src/nodb/only.py"]
        assert row["inferred"] == "" and row["reject_reason"] == "no_evidence"
        assert "# [DOMAIN]" not in target.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 词表护栏
# ---------------------------------------------------------------------------


class TestVocabularyGuard:
    def test_illegal_domain_is_unresolved_and_not_written(self, tmp_path: Path):
        _write(tmp_path / "src/illegal/only.py", _mod("src/illegal/only"))
        res = _run(
            tmp_path,
            ["src/illegal/only.py"],
            apply=True,
            nodes=[{"path": "src/illegal/only.py", "domain_id": "D_NOT_REGISTERED", "granularity": "file"}],
        )
        row = _rows_by_path(res)["src/illegal/only.py"]
        assert row["inferred"] == ""
        assert row["reject_reason"].startswith("illegal_value:D_NOT_REGISTERED")
        assert "# [DOMAIN]" not in (tmp_path / "src/illegal/only.py").read_text(encoding="utf-8")

    def test_alias_value_accepted_via_ssot_visibility(self, tmp_path: Path):
        _write(tmp_path / "src/alias/only.py", _mod("src/alias/only"))
        res = _run(
            tmp_path,
            ["src/alias/only.py"],
            nodes=[{"path": "src/alias/only.py", "domain_id": "D_BETA_LEGACY", "granularity": "file"}],
        )
        assert _rows_by_path(res)["src/alias/only.py"]["inferred"] == "D_BETA_LEGACY"

    def test_vocab_unavailable_means_zero_writes(self, tmp_path: Path):
        assert bmd.load_legal_domains(str(tmp_path / "no_such_vocabulary.yaml")) == set()
        _write(tmp_path / "src/novocab/a.py", _mod("src/novocab/a", "D_ALPHA"))
        _write(tmp_path / "src/novocab/b.py", _mod("src/novocab/b", "D_ALPHA"))
        target = _write(tmp_path / "src/novocab/c.py", _mod("src/novocab/c"))
        before = target.read_bytes()
        res = _run(tmp_path, ["src/novocab/c.py"], apply=True, vocab_exists=False)
        row = _rows_by_path(res)["src/novocab/c.py"]
        assert row["inferred"] == "" and row["reject_reason"].startswith("illegal_value:")
        assert target.read_bytes() == before  # 词表故障时零写入（fail-safe）

    def test_existing_legal_value_never_overwritten(self, tmp_path: Path):
        target = _write(tmp_path / "src/exist/only.py", _mod("src/exist/only", "D_BETA"))
        res = _run(
            tmp_path,
            ["src/exist/only.py"],
            apply=True,
            nodes=[{"path": "src/exist/only.py", "domain_id": "D_ALPHA", "granularity": "file"}],
            ownership_entries=[],
        )
        row = _rows_by_path(res)["src/exist/only.py"]
        assert row["action"] == "skip_legal_exists" and row["reject_reason"] == "existing_legal_differs"
        assert "# [DOMAIN] D_BETA" in target.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# m 级：词表废弃值迁移优先（2026-09-18 W4c 放量实证治本）
# ---------------------------------------------------------------------------


class TestDeprecatedMigration:
    def test_deprecated_map_excludes_non_unique_targets(self, tmp_path: Path):
        vocab = _write(tmp_path / "v.yaml", VOCAB_YAML)
        m = bmd.load_deprecated_replacements(str(vocab))
        assert m == {"D_OLD": "D_ALPHA"}  # D_ORPHAN 的 N/A 目标不入图（宁缺勿滥）

    def test_deprecated_current_wins_over_sibling_vote(self, tmp_path: Path):
        # 兄弟票 D_BETA ≥2 成立，但既有值是词表废弃值 → 迁移目标 D_ALPHA 优先
        _write(tmp_path / "src/mig/a.py", _mod("src/mig/a", "D_BETA"))
        _write(tmp_path / "src/mig/b.py", _mod("src/mig/b", "D_BETA"))
        target = _write(tmp_path / "src/mig/t.py", _mod("src/mig/t", "D_OLD"))
        res = _run(tmp_path, ["src/mig/t.py"], apply=True)
        row = _rows_by_path(res)["src/mig/t.py"]
        assert row["inferred"] == "D_ALPHA"
        assert row["inference_source"] == "vocab_deprecated_migration"
        assert row["level"] == bmd.LEVEL_MIGRATION
        assert row["action"] == "replaced"  # 非法废弃值 → 原地替换
        assert "既有值 D_OLD=词表废弃" in row["evidence"]  # 迁移依据留痕
        text = target.read_text(encoding="utf-8")
        assert "# [DOMAIN] D_ALPHA" in text and "D_OLD" not in text

    def test_deprecated_without_unique_target_falls_back_to_vote(self, tmp_path: Path):
        _write(tmp_path / "src/mig2/a.py", _mod("src/mig2/a", "D_BETA"))
        _write(tmp_path / "src/mig2/b.py", _mod("src/mig2/b", "D_BETA"))
        target = _write(tmp_path / "src/mig2/t.py", _mod("src/mig2/t", "D_ORPHAN"))
        res = _run(tmp_path, ["src/mig2/t.py"], apply=True)
        row = _rows_by_path(res)["src/mig2/t.py"]
        assert row["inference_source"] == "sibling_vote"
        assert row["inferred"] == "D_BETA"
        assert "# [DOMAIN] D_BETA" in target.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# git 脏文件护栏
# ---------------------------------------------------------------------------


class TestGitDirtyGuard:
    def test_dirty_file_skipped_on_apply(self, tmp_path: Path):
        target = _write(tmp_path / "src/wip/a.py", _mod("src/wip/a", "D_ALPHA"))
        _write(tmp_path / "src/wip/b.py", _mod("src/wip/b", "D_ALPHA"))
        _write(tmp_path / "src/wip/c.py", _mod("src/wip/c"))
        before = target.read_bytes()
        res = _run(
            tmp_path,
            ["src/wip/c.py"],
            apply=True,
            git_runner=_fake_git(["src/wip/c.py"]),
        )
        row = _rows_by_path(res)["src/wip/c.py"]
        assert row["action"] == "skip_git_dirty" and row["reject_reason"] == "workspace_wip_other_session"
        assert target.read_bytes() == before

    def test_dirty_check_only_in_apply_mode(self, tmp_path: Path):
        _write(tmp_path / "src/wip2/a.py", _mod("src/wip2/a", "D_ALPHA"))
        _write(tmp_path / "src/wip2/b.py", _mod("src/wip2/b", "D_ALPHA"))
        _write(tmp_path / "src/wip2/c.py", _mod("src/wip2/c"))
        called = []

        def runner(args, cwd):  # noqa: ARG001
            called.append(args)

            class P:
                returncode = 0
                stdout = " M src/wip2/c.py\n"

            return P()

        res = _run(tmp_path, ["src/wip2/c.py"], apply=False, git_runner=runner)
        assert called == []  # 干跑不查 git
        assert _rows_by_path(res)["src/wip2/c.py"]["action"] == "would_change"

    def test_ignore_git_dirty_escape_hatch(self, tmp_path: Path):
        _write(tmp_path / "src/wip3/a.py", _mod("src/wip3/a", "D_ALPHA"))
        _write(tmp_path / "src/wip3/b.py", _mod("src/wip3/b", "D_ALPHA"))
        target = _write(tmp_path / "src/wip3/c.py", _mod("src/wip3/c"))
        res = _run(
            tmp_path,
            ["src/wip3/c.py"],
            apply=True,
            git_runner=_fake_git(["src/wip3/c.py"]),
            skip_git_guard=True,
        )
        assert _rows_by_path(res)["src/wip3/c.py"]["action"] == "inserted_after_module"
        assert "# [DOMAIN] D_ALPHA" in target.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 幂等与批量
# ---------------------------------------------------------------------------


class TestIdempotent:
    def test_second_run_zero_change(self, tmp_path: Path):
        _write(tmp_path / "src/idem/a.py", _mod("src/idem/a", "D_ALPHA"))
        _write(tmp_path / "src/idem/b.py", _mod("src/idem/b", "D_ALPHA"))
        _write(tmp_path / "src/idem/c.py", _mod("src/idem/c"))
        first = _run(tmp_path, ["src/idem/c.py"], apply=True)
        assert _rows_by_path(first)["src/idem/c.py"]["action"] == "inserted_after_module"
        after_first = (tmp_path / "src/idem/c.py").read_bytes()

        second = _run(tmp_path, ["src/idem/c.py"], apply=True)
        row = _rows_by_path(second)["src/idem/c.py"]
        assert row["action"] == "skip_already_ok"
        assert second["stats"]["applied"] == 0 and second["written"] == 0
        assert (tmp_path / "src/idem/c.py").read_bytes() == after_first


class TestBatchLimit:
    def test_batch_caps_written_files(self, tmp_path: Path):
        _write(tmp_path / "src/batch/a.py", _mod("src/batch/a", "D_ALPHA"))
        _write(tmp_path / "src/batch/b.py", _mod("src/batch/b", "D_ALPHA"))
        targets = [f"src/batch/t{i}.py" for i in range(4)]
        for t in targets:
            _write(tmp_path / t, _mod(t))
        res = _run(tmp_path, targets, apply=True, batch=2)
        actions = {r["path"]: r["action"] for r in res["rows"]}
        assert res["written"] == 2 == res["stats"]["applied"]
        assert [p for p, a in actions.items() if a == "batch_limited"] == ["src/batch/t2.py", "src/batch/t3.py"]
        assert [p for p, a in actions.items() if a == "inserted_after_module"] == ["src/batch/t0.py", "src/batch/t1.py"]
        written = [t for t in targets if "# [DOMAIN]" in (tmp_path / t).read_text(encoding="utf-8")]
        assert sorted(written) == ["src/batch/t0.py", "src/batch/t1.py"]


class TestEvidenceConflictHold:
    """独立证据（depgraph file 节点）反对目录兄弟票 → 不写盘，转人工裁定。"""

    def _repo(self, tmp_path: Path) -> Path:
        _write(tmp_path / "src/mixed/a.py", _mod("src/mixed/a", "D_ALPHA"))
        _write(tmp_path / "src/mixed/b.py", _mod("src/mixed/b", "D_ALPHA"))
        return _write(tmp_path / "src/mixed/c.py", _mod("src/mixed/c"))

    def test_conflict_is_held_not_written(self, tmp_path: Path):
        target = self._repo(tmp_path)
        before = target.read_bytes()
        res = _run(
            tmp_path,
            ["src/mixed/c.py"],
            apply=True,
            nodes=[{"path": "src/mixed/c.py", "domain_id": "D_BETA", "granularity": "file"}],
        )
        row = _rows_by_path(res)["src/mixed/c.py"]
        assert row["inferred"] == "D_BETA"  # 取值仍是最强证据
        assert row["review_flag"] == "sibling_vote_conflicts_independent"
        assert row["action"] == "needs_review"
        assert row["planned_action"] == "inserted_after_module"
        assert res["stats"]["needs_review"] == 1 and res["written"] == 0
        assert target.read_bytes() == before  # 零写入、零字节抖动
        assert "sibling_vote_conflicts_independent" in (res["report"]).read_text(encoding="utf-8")

    def test_allow_conflict_write_releases_the_row(self, tmp_path: Path):
        self._repo(tmp_path)
        res = _run(
            tmp_path,
            ["src/mixed/c.py"],
            apply=True,
            allow_conflict_write=True,
            nodes=[{"path": "src/mixed/c.py", "domain_id": "D_BETA", "granularity": "file"}],
        )
        row = _rows_by_path(res)["src/mixed/c.py"]
        assert row["action"] == "inserted_after_module"
        text = (tmp_path / "src/mixed/c.py").read_text(encoding="utf-8")
        assert "# [DOMAIN] D_BETA" in text and "D_ALPHA" not in text

    def test_agreeing_evidence_writes_without_flag(self, tmp_path: Path):
        _write(tmp_path / "src/pure/a.py", _mod("src/pure/a", "D_BETA"))
        _write(tmp_path / "src/pure/b.py", _mod("src/pure/b", "D_BETA"))
        _write(tmp_path / "src/pure/c.py", _mod("src/pure/c"))
        res = _run(
            tmp_path,
            ["src/pure/c.py"],
            apply=True,
            nodes=[{"path": "src/pure/c.py", "domain_id": "D_BETA", "granularity": "file"}],
        )
        row = _rows_by_path(res)["src/pure/c.py"]
        assert row["review_flag"] == "" and row["action"] == "inserted_after_module"
        assert row["inference_source"] == "sibling_vote" and row["level"] == bmd.LEVEL_A


# ---------------------------------------------------------------------------
# 字节保真与插入位置
# ---------------------------------------------------------------------------


class TestByteFidelity:
    def test_crlf_and_bom_preserved_only_one_line_changes(self, tmp_path: Path):
        _write(tmp_path / "src/eol/a.py", _mod("src/eol/a", "D_ALPHA"))
        _write(tmp_path / "src/eol/b.py", _mod("src/eol/b", "D_ALPHA"))
        body = "# [BLUEPRINT] MOD-TEST\r\n# [MODULE] src.eol.c\r\nclass C:\r\n    pass\r\n"
        target = tmp_path / "src/eol/c.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\xef\xbb\xbf" + body.encode("utf-8"))

        res = _run(tmp_path, ["src/eol/c.py"], apply=True)
        assert _rows_by_path(res)["src/eol/c.py"]["action"] == "inserted_after_module"
        raw = target.read_bytes()
        assert raw.startswith(b"\xef\xbb\xbf")  # BOM 原样
        text = raw.decode("utf-8-sig")
        assert "# [DOMAIN] D_ALPHA\r\n" in text  # CRLF 原样
        assert bmd.strip_domain_lines(text) == body  # 其余字节零改动

    def test_empty_domain_line_replaced_in_place(self, tmp_path: Path):
        _write(tmp_path / "src/empty/a.py", _mod("src/empty/a", "D_ALPHA"))
        _write(tmp_path / "src/empty/b.py", _mod("src/empty/b", "D_ALPHA"))
        _write(tmp_path / "src/empty/c.py", _mod("src/empty/c", ""))
        res = _run(tmp_path, ["src/empty/c.py"], apply=True)
        row = _rows_by_path(res)["src/empty/c.py"]
        assert row["action"] == "replaced"
        text = (tmp_path / "src/empty/c.py").read_text(encoding="utf-8")
        assert text.count("# [DOMAIN]") == 1
        assert "# [DOMAIN] D_ALPHA" in text

    def test_yaml_anchor_block_insertion(self, tmp_path: Path):
        yaml_text = (
            "# --- 治理锚定 ---\n"
            "# blueprint: MOD-TEST | docs/03_modules/x/blueprint.md\n"
            "# module_id: MOD-TEST\n"
            "# ttl: permanent\n"
            "# --- 治理锚定结束 ---\n"
            "module_id: MOD-TEST\n"
            "values: []\n"
        )
        for name, dom in (("ref1.yaml", "D_ALPHA"), ("ref2.yaml", "D_ALPHA")):
            _write(tmp_path / "scripts/meta" / name, yaml_text.replace("# module_id: MOD-TEST", f"# [MODULE] m\n# [DOMAIN] {dom}", 1))
        target = _write(tmp_path / "scripts/meta/new.yaml", yaml_text)
        res = _run(tmp_path, ["scripts/meta/new.yaml"], apply=True)
        row = _rows_by_path(res)["scripts/meta/new.yaml"]
        assert row["inferred"] == "D_ALPHA"
        assert row["action"] == "inserted_in_anchor"
        text = target.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert lines[lines.index("# [DOMAIN] D_ALPHA") - 1] == "# ttl: permanent"

    def test_no_anchor_is_not_written(self, tmp_path: Path):
        _write(tmp_path / "src/noanch/a.py", _mod("src/noanch/a", "D_ALPHA"))
        _write(tmp_path / "src/noanch/b.py", _mod("src/noanch/b", "D_ALPHA"))
        target = _write(tmp_path / "src/noanch/plain.py", "import os\n\nprint(os.name)\n")
        res = _run(tmp_path, ["src/noanch/plain.py"], apply=True)
        row = _rows_by_path(res)["src/noanch/plain.py"]
        assert row["action"] == "no_anchor" and row["reject_reason"] == "no_header_anchor"
        assert target.read_text(encoding="utf-8") == "import os\n\nprint(os.name)\n"


class TestGhostAndExcluded:
    def test_ghost_entry_skipped(self, tmp_path: Path):
        res = _run(tmp_path, ["tests/deleted/gone.py"], apply=True)
        row = _rows_by_path(res)["tests/deleted/gone.py"]
        assert row["action"] == "skip_ghost" and row["reject_reason"] == "file_not_on_disk"

    def test_aidrafts_excluded(self, tmp_path: Path):
        _write(tmp_path / ".aidrafts/sess/x.py", _mod(".aidrafts/sess/x"))
        res = _run(tmp_path, [".aidrafts/sess/x.py"], apply=True)
        assert _rows_by_path(res)[".aidrafts/sess/x.py"]["action"] == "skip_excluded"


# ---------------------------------------------------------------------------
# 输入清单 / 辅助函数
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_read_list_dedup_and_header_tolerance(self, tmp_path: Path):
        csv_path = _write(
            tmp_path / "list.csv",
            "# comment line\npath\nsrc/a.py\nsrc/b.py\nsrc/a.py\nsrc/c.py,extra\n",
        )
        assert bmd.read_list(csv_path) == ["src/a.py", "src/b.py", "src/c.py"]

    def test_all_mode_rescans_repo(self, tmp_path: Path):
        _write(tmp_path / "src/scan/a.py", _mod("src/scan/a", "D_ALPHA"))
        _write(tmp_path / "src/scan/b.py", _mod("src/scan/b", "D_ALPHA"))
        _write(tmp_path / "src/scan/c.py", _mod("src/scan/c"))
        vocab = _write(tmp_path / "vocab/alpha_vocabulary.yaml", VOCAB_YAML)
        res = bmd.process(
            selection=bmd.TargetSelection(list_path=None, all_mode=True),
            locations=bmd.EvidenceLocations(
                repo=tmp_path,
                vocab_file=str(vocab),
                ownership_path=tmp_path / "missing.yaml",
                registry_path=tmp_path / "missing2.yaml",
            ),
            policy=bmd.BackfillWritePolicy(apply=True, batch=200),
            output=bmd.OutputOptions(out_dir=tmp_path / "out", write_report=False),
            hooks=bmd.InjectionHooks(conn_factory=lambda: _FakePG()),
        )
        assert "src/scan/c.py" in {r["path"] for r in res["rows"]}
        assert "# [DOMAIN] D_ALPHA" in (tmp_path / "src/scan/c.py").read_text(encoding="utf-8")

    def test_ownership_parser_is_field_order_agnostic(self, tmp_path: Path):
        text = (
            "meta:\n  total_ssot_claims: 0\nownership:\n"
            "  - owner_blueprint: 'MOD-A'\n    path: 'src/svc/a.py'\n    claim_type: 'depgraph_node'\n\n"
            "  - path: 'src/svc/b.py'\n    owner_blueprint: 'MOD-B'\n    claim_type: 'depgraph_node'\n\n"
            "ssot_claims:\n  - claim: 'x'\n"
        )
        p = _write(tmp_path / "ownership.yaml", text)
        assert bmd.load_ownership_map(p) == {"src/svc/a.py": "MOD-A", "src/svc/b.py": "MOD-B"}

    def test_audit_jsonl_and_table_written(self, tmp_path: Path):
        _write(tmp_path / "src/aud/a.py", _mod("src/aud/a", "D_ALPHA"))
        _write(tmp_path / "src/aud/b.py", _mod("src/aud/b", "D_ALPHA"))
        _write(tmp_path / "src/aud/c.py", _mod("src/aud/c"))
        res = _run(tmp_path, ["src/aud/c.py"], apply=True)
        audit = res["audit"].read_text(encoding="utf-8").strip().splitlines()
        assert len(audit) == 1
        rec = __import__("json").loads(audit[0])
        assert rec["path"] == "src/aud/c.py" and rec["verify_body_unchanged"] is True
        assert rec["sha_before"] and rec["sha_after"] and rec["sha_before"] != rec["sha_after"]
        table_rows = res["table"].read_text(encoding="utf-8").splitlines()
        assert table_rows[0].startswith("path,exists_on_disk,current_domain,inferred,inference_source")
        assert res["report"].exists()

    def test_write_failure_is_recorded_not_raised(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        _write(tmp_path / "src/fail/a.py", _mod("src/fail/a", "D_ALPHA"))
        _write(tmp_path / "src/fail/b.py", _mod("src/fail/b", "D_ALPHA"))
        _write(tmp_path / "src/fail/c.py", _mod("src/fail/c"))

        def boom(target, data):  # noqa: ARG001
            raise OSError("locked")

        monkeypatch.setattr(bmd, "atomic_write_bytes", boom)
        res = _run(tmp_path, ["src/fail/c.py"], apply=True)
        row = _rows_by_path(res)["src/fail/c.py"]
        assert row["action"] == "error" and row["reject_reason"].startswith("write_error:")
        assert "# [DOMAIN]" not in (tmp_path / "src/fail/c.py").read_text(encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
