# [A_test] module_id: TEST-MOD-GOV-047-TEST_COMMIT_QUEUE_LANDING_EVOLVED_SCOPE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_commit_queue_landing_evolved_scope
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; subprocess; scripts.commit_queue; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/gov/governance/test_commit_queue_landing_evolved_scope.py
# [MATURITY] testing
# [INVARIANTS] 全部 tmp_path 隔离（临时 git 仓+队列根），零生产仓零生产队列触碰；
#              红证用生产真谓词（is_registry_mergeable 本尊注入，非本地等价件）；
#              每条红证在扩面前必红（谓词窄口径/基底冲突死信/条目级 YAML 误合并），扩面后必绿
# [MODIFY-GUARD] commitmap-cure P0 治本（总令 §B P0）：is_registry_mergeable "演进件仍判已落地"
#                口径自 docs/_working/ 前缀扩到全部路径。本文件钉：①谓词全路径真；
#                ②stale 重校验 src/ 漂移交合并仲裁并留痕；③基底冲突判定不再 path 级死信 src/；
#                ④落地仲裁语义（整文件三分局+非注册表 YAML 整文件回退+双侧改/dev 删件 fail-closed）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""commitmap-cure P0 治本红蓝钉：三向合并仲裁扩面到全部路径。

病源（总令 §B P0 处方，承 2daf737060 二层⑥）：`is_registry_mergeable` 只对
注册表 catalogs 族 .yaml 与 `docs/_working/` 前缀放行合并仲裁；`src/`、`config/`
等其他路径的基底漂移仍在队列层被判 cascade_stale 死信（或基底冲突 path 级死信）
——演进件（dev 侧已推进、袋侧未改）本可安全吸收，却被逐袋退回人工。

P0 治本口径：
  ① `is_registry_mergeable` 对全部路径返回 True——所有路径基底漂移交落地侧
     条目级/整文件三向合并仲裁，不再在队列层判死；
  ② 落地侧 `_merge_registry_file` 分流收窄：条目级 YAML 合并仅限注册表族
     （catalogs 前缀 .yaml），其余 YAML 与全部非 YAML 件走整文件标准三方
     （仅袋改→取袋；仅 dev 改→noop 吸收留审计；双侧皆改→真冲突死信）；
  ③ fail-closed 面随扩面同步覆盖全部路径：dev 已删件拒绝复活、双侧真改死信。

红证组织：TestPredicateScope / TestStaleRevalidateProductionPred /
TestConflictArbitrationHandover 为改前红-改后绿的行为红证（谓词窄口径、
生产链路 stale 重校验、基底冲突死信三分面）；TestMergeSemanticsOnArbitratedPaths
钉扩面后的仲裁语义（含 fail-closed 与 YAML 分流收窄——扩面前该面不可达或走
错误语义，扩面后为唯一语义）。
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as landing

SRC_REL = "src/zephyr/evolved_probe.py"
CFG_REL = "config/evolved_probe.yaml"
CATALOG_REL = "docs/01_policies_and_standards/_registry/catalogs/probe_registry.yaml"


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, f"git {' '.join(args)} 失败: {r.stderr}"
    return r.stdout.strip()


@pytest.fixture()
def probe_repo(tmp_path: Path) -> tuple[Path, str]:
    """tmp git 仓：base commit 含 src/ 件（V1）。后续演进由用例自行推进。"""
    repo = tmp_path / "probe_repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "probe@test.local")
    _git(repo, "config", "user.name", "probe")
    (repo / "src" / "zephyr").mkdir(parents=True)
    (repo / "src" / "zephyr" / "evolved_probe.py").write_bytes(b"V1\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    return repo, _git(repo, "rev-parse", "HEAD")


def _evolve_dev(repo: Path, rel: str, content: bytes) -> str:
    """dev 侧演进一格（他人改了同名文件），返回演进后 commit。"""
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", f"dev evolve {rel}")
    return _git(repo, "rev-parse", "HEAD")


def _blob_at(repo: Path, commit: str, rel: str) -> str:
    return _git(repo, "rev-parse", f"{commit}:{rel}")


def _item(base_head: str, files: list[dict]) -> dict:
    return {"qid": "q-evolved-scope", "session_id": "st-cure-p0-20261006", "base_head": base_head, "files": files}


def _f(rel: str, base_blob: str | None) -> dict:
    return {"path": rel, "base_blob": base_blob}


# ---------------------------------------------------------------------------
# 红证 A：谓词扩面（总令处方的直接口径钉）
# ---------------------------------------------------------------------------


class TestPredicateScope:
    def test_mergeable_predicate_covers_all_paths(self) -> None:
        """演进件判已落地口径覆盖全部路径：src/config/docs(非_working)/data/scripts 全真。

        扩面前：仅 catalogs 前缀 .yaml 与 docs/_working/ 前缀为真，本用例其余路径断言即红。
        """
        for rel in (SRC_REL, CFG_REL, "docs/03_modules/MOD-ANY.md", "data/evolved_probe.json", "scripts/probe.py"):
            assert landing.is_registry_mergeable(rel), f"路径 {rel} 应交三向合并仲裁（演进件仍判已落地）"

    def test_mergeable_predicate_keeps_former_scopes(self) -> None:
        """既有作用域不回归：catalogs 族 .yaml 与 docs/_working/ 件仍真（零收窄）。"""
        assert landing.is_registry_mergeable(CATALOG_REL)
        assert landing.is_registry_mergeable("docs/_working/commitmap_cure/final_closeout_report.md")

    def test_mergeable_predicate_windows_separator_normalized(self) -> None:
        """Windows 反斜杠路径归一后仍判真（与真源 norm 语义同源）。"""
        assert landing.is_registry_mergeable("src\\zephyr\\evolved_probe.py")
        assert landing.is_registry_mergeable("docs\\_working\\report.md")


# ---------------------------------------------------------------------------
# 红证 B：stale 重校验（生产链路）——src/ 漂移交合并仲裁并留痕
# ---------------------------------------------------------------------------


class TestStaleRevalidateProductionPred:
    def test_src_drift_handed_to_arbitration_with_trace(self) -> None:
        """生产真谓词注入：src/ 路径 base_blob≠HEAD blob → 交仲裁留痕，不再判不适用。

        扩面前：is_registry_mergeable(SRC_REL)=False ⇒ 该路径被判 mismatched
        （cascade_stale 死信候选）——本用例必红；扩面后 rebased_registry 留痕放行。
        """
        item = _item("sha-base", [_f(SRC_REL, "blob-src-base")])
        reader = lambda rel: {SRC_REL: "blob-src-moved"}.get(rel)  # noqa: E731 — 注入件，同生产 head_reader 口径
        ok, mism = cq._revalidate_stale_base(item, reader, mergeable_pred=landing.is_registry_mergeable)
        assert ok and mism == [], f"src/ 漂移应交合并仲裁，实得 ok={ok} mism={mism!r}"
        assert item["meta"]["rebased_registry"] == [SRC_REL], "交仲裁必须留痕（漂移被接管不得静默）"

    def test_mixed_bag_all_drifted_paths_rebased(self) -> None:
        """混合袋（src+config+catalogs 全漂移）：扩面后全数交仲裁、零殉葬、保序留痕。"""
        files = [_f(SRC_REL, "b1"), _f(CFG_REL, "b2"), _f(CATALOG_REL, "b3")]
        item = _item("sha-base", files)
        reader = lambda rel: {SRC_REL: "m1", CFG_REL: "m2", CATALOG_REL: "m3"}.get(rel)  # noqa: E731
        ok, mism = cq._revalidate_stale_base(item, reader, mergeable_pred=landing.is_registry_mergeable)
        assert ok and mism == [], f"全路径扩面后混合袋应整体放行，实得 ok={ok} mism={mism!r}"
        assert item["meta"]["rebased_registry"] == [SRC_REL, CFG_REL, CATALOG_REL]


# ---------------------------------------------------------------------------
# 红证 C：基底冲突判定不再 path 级死信 src/（交落地仲裁）
# ---------------------------------------------------------------------------


class TestConflictArbitrationHandover:
    def test_src_evolution_no_longer_dead_letters(self, probe_repo: tuple[Path, str], tmp_path: Path) -> None:
        """dev 侧演进 src/ 件（袋侧未跟上）：_conflict_reason 返回 None（交仲裁）。

        扩面前：overlap 非空且非本会话落地 ⇒ 返回基底冲突 reason（path 级死信）——必红。
        """
        repo, base = probe_repo
        dev = _evolve_dev(repo, SRC_REL, b"V2-dev\n")
        land = landing.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue")
        item = _item(base, [_f(SRC_REL, _blob_at(repo, base, SRC_REL))])
        assert land._conflict_reason(item, dev) is None, "dev 演进件不应 path 级死信，应交三向合并仲裁"


# ---------------------------------------------------------------------------
# 语义钉：扩面后的落地仲裁行为（TestMergeSemanticsOnArbitratedPaths）
# ---------------------------------------------------------------------------


class TestMergeSemanticsOnArbitratedPaths:
    def test_src_only_dev_evolution_noop_absorbed(self, probe_repo: tuple[Path, str], tmp_path: Path) -> None:
        """演进件核心语义：袋字节==基底（袋侧没改）且 dev 已演进 → noop 吸收（None）。

        这就是"演进件仍判已落地"：dev 现内容保留，旧字节不再回写（ATK-2/3 防护
        由合并器 theirs==base→noop 语义接管，扩面后全路径生效）。
        """
        repo, base = probe_repo
        dev = _evolve_dev(repo, SRC_REL, b"V2-dev\n")
        land = landing.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue")
        item = _item(base, [_f(SRC_REL, _blob_at(repo, base, SRC_REL))])
        assert land._merge_registry_file(item, SRC_REL, b"V1\n", dev) is None, "演进件应被 noop 吸收"

    def test_src_bag_only_change_takes_bag(self, probe_repo: tuple[Path, str], tmp_path: Path) -> None:
        """仅袋侧改（dev 未动本件）→ 取袋字节。"""
        repo, base = probe_repo
        _git(repo, "commit", "--allow-empty", "-qm", "dev moves elsewhere")
        dev = _git(repo, "rev-parse", "HEAD")
        land = landing.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue")
        item = _item(base, [_f(SRC_REL, _blob_at(repo, base, SRC_REL))])
        merged = land._merge_registry_file(item, SRC_REL, b"V1-bag\n", dev)
        assert merged == b"V1-bag\n", f"仅袋侧改应取袋字节，实得 {merged!r}"

    def test_src_dual_sided_edit_raises_fail_closed(self, probe_repo: tuple[Path, str], tmp_path: Path) -> None:
        """双侧皆改 → RuntimeError（真冲突死信，绝不静默覆盖）。"""
        repo, base = probe_repo
        dev = _evolve_dev(repo, SRC_REL, b"V2-dev\n")
        land = landing.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue")
        item = _item(base, [_f(SRC_REL, _blob_at(repo, base, SRC_REL))])
        with pytest.raises(RuntimeError, match="真冲突"):
            land._merge_registry_file(item, SRC_REL, b"V2-bag\n", dev)

    def test_dev_deleted_file_not_revived(self, probe_repo: tuple[Path, str], tmp_path: Path) -> None:
        """dev 已删而袋基底有 → RuntimeError（陈旧袋拒绝复活已删件，fail-closed 面随扩面覆盖 src/）。"""
        repo, base = probe_repo
        (repo / SRC_REL).unlink()
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "dev deletes src file")
        dev = _git(repo, "rev-parse", "HEAD")
        land = landing.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue")
        item = _item(base, [_f(SRC_REL, _blob_at(repo, base, SRC_REL))])
        with pytest.raises(RuntimeError, match="dev 已删"):
            land._merge_registry_file(item, SRC_REL, b"V1\n", dev)

    def test_config_yaml_whole_file_three_way_not_entry_level(
        self, probe_repo: tuple[Path, str], tmp_path: Path
    ) -> None:
        """非注册表 YAML 走整文件三方而非条目级合并（分流收窄）。

        仅 dev 改 → None（noop 吸收）；条目级合并对普通 YAML 是错误语义
        （退役检查/唯一键推断/total 自愈只对 catalogs 族有意义），且 frontmatter
        文本可能诱发 yaml.compose 必炸（ed695bd7ff 0016 死实例同源）。
        """
        repo, base = probe_repo
        (repo / "config").mkdir()
        (repo / "config" / "evolved_probe.yaml").write_bytes(b"key: v1\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "add config probe")
        base2 = _git(repo, "rev-parse", "HEAD")
        dev = _evolve_dev(repo, CFG_REL, b"key: v2-dev\n")
        land = landing.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue")
        item = _item(base2, [_f(CFG_REL, _blob_at(repo, base2, CFG_REL))])
        assert land._merge_registry_file(item, CFG_REL, b"key: v1\n", dev) is None, (
            "非注册表 YAML 演进件应走整文件三方 noop 吸收（不得走条目级合并）"
        )

    def test_config_yaml_dual_sided_edit_raises(self, probe_repo: tuple[Path, str], tmp_path: Path) -> None:
        """非注册表 YAML 双侧皆改 → RuntimeError（整文件三方 fail-closed）。"""
        repo, base = probe_repo
        (repo / "config").mkdir()
        (repo / "config" / "evolved_probe.yaml").write_bytes(b"key: v1\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "add config probe")
        base = _git(repo, "rev-parse", "HEAD")
        dev = _evolve_dev(repo, CFG_REL, b"key: v2-dev\n")
        land = landing.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue")
        item = _item(base, [_f(CFG_REL, _blob_at(repo, base, CFG_REL))])
        with pytest.raises(RuntimeError, match="真冲突"):
            land._merge_registry_file(item, CFG_REL, b"key: v2-bag\n", dev)
