# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §热册三向合并器治本（QMine A1 四件）
# [MODULE] tests.governance.test_commit_queue_landing_qmine_a1
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; pyyaml; scripts.commit_queue; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_landing_qmine_a1.py
# [MATURITY] testing
# [INVARIANTS] 纯函数层红蓝零 IO（件①②③）+ tmp 隔离池化/gates 测试（件④）；判等只做侧内绝不跨侧（跨侧由三向规则 base 仲裁）；所有新分支退现状方向（声明缺失/解析失败/mismatch 一律回默认复合键，不引入新死法）；去重只作用于合并索引，不改写 ours 盘面字节
# [MODIFY-GUARD] QMine 战役施工线 A1（st-qmine-20260925，01_hot_registry_merge 作业簿 §4 治本方案）：①_index_family_blocks 侧内判等去重 ②_scalar_family_keys dict 形态 passthrough 扩面 ③unique_key 声明驱动身份键 ④_pool stale 重校验收进 env 计数闸 + __call__ gates 相位计时
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_landing_qmine_a1.py — QMine A1 四件红蓝钉（st-qmine-20260925）。

1. 侧内判等去重：同键同侧 data 全等（字节同/重序列化语义同）→ 静默去重落地不再
   陪死（死信袋回放 33% 死亡属此形态）；data 不等 → 同键异容死信带双条 dump+对账器
   处方；跨侧同键仍由三向规则仲裁（绝不静默吞任一侧）。
2. dict 形态 passthrough 扩面：流式 list 元数据块（``tags: [a, b]`` 单行 → 块文本
   safe_load 出 ``{"tags": [...]}``）不再判「身份判不了」——整族剔出合并空间保留
   ours（HEAD 6 册 14 块活雷形态）；混合形态族维持死信不放宽。
3. 声明驱动身份键：册头 unique_key 声明（list 全册默认 / dict 按族）构造复合身份；
   token 复合后缀保留（同 file 多 token 合法并存不被声明键错杀）；无声明/解析失败/
   三侧 mismatch → 退默认复合键零漂移。
4. env 逃逸口封堵：pool stale 基底重校验的 git 瞬态失败收进 env_retry 计数闸
   （38 笔逃逸实证），耗尽升级死信；__call__ gates 相位计时（env 守卫 finally 单点，
   主路径与 Mode B 重试天然同享）。
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
from pathlib import Path

import pytest
import yaml

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql

# ---------------------------------------------------------------------------
# 件① 侧内判等去重（纯函数层，nightfix 同款零 IO 风格）
# ---------------------------------------------------------------------------

_REG_REL = "docs/01_policies_and_standards/_registry/catalogs/qmine_a1_reg.yaml"


class TestSameSideEqualDuplicateDedup:
    """同键同侧重复的判等分层：等则去重计数，异则死信带双条 dump。"""

    BASE = "title: t\nitems:\n  - id: a\n    path: a.md\n  - id: a\n    path: a.md\n"

    def test_byte_equal_duplicate_dedups_and_lands(self):
        """字节级相同的同侧重复（token 双发主形态）→ 静默去重，合并落地不再陪死。"""
        theirs = self.BASE + "  - id: b\n    path: b.md\n"
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, self.BASE, theirs, rel_path=_REG_REL)
        assert err == "", f"字节同重复不得死信: {err}"
        ids = [e["id"] for e in yaml.safe_load(merged)["items"]]
        assert ids == ["a", "a", "b"], "ours 盘面原样保留（去重只作用于合并索引），theirs 新条照常插入"

    def test_semantic_equal_duplicate_dedups_and_lands(self):
        """语义相同仅字节异（YAML 重序列化：字段序颠倒）→ data 判等去重，合并落地。"""
        ours = "title: t\nitems:\n  - id: a\n    path: a.md\n  - path: a.md\n    id: a\n"
        theirs = ours + "  - id: b\n    path: b.md\n"
        merged, err = cql.three_way_merge_registry_yaml(ours, ours, theirs, rel_path=_REG_REL)
        assert err == "", f"语义同重复不得死信: {err}"
        ids = [e["id"] for e in yaml.safe_load(merged)["items"]]
        assert ids == ["a", "a", "b"]

    def test_true_conflict_duplicate_dead_letters_with_dual_dump(self):
        """同键异容（仓库态缺陷）→ 死信，reason 带双条 dump 与对账器处方。"""
        dupc = "title: t\nitems:\n  - id: a\n    path: a.md\n  - id: a\n    path: CONFLICT.md\n"
        merged, err = cql.three_way_merge_registry_yaml(dupc, dupc, dupc, rel_path=_REG_REL)
        assert merged is None, "同键异容必须死信（落地器无权择优）"
        for needle in ("同侧身份键重复且内容冲突", "在册先条", "重复后条", "path: a.md", "path: CONFLICT.md", "对账器"):
            assert needle in err, f"死信 detail 缺 {needle!r}: {err[:200]}"

    def test_dedup_is_side_internal_cross_side_three_way_still_arbitrates(self):
        """去重只做侧内：跨侧同键各自修改仍由三向规则死信（绝不静默吞任一侧）。"""
        base = "title: t\nitems:\n  - id: a\n    v: 1\n"
        ours = "title: t\nitems:\n  - id: a\n    v: 2\n"
        theirs = "title: t\nitems:\n  - id: a\n    v: 3\n"
        merged, err = cql.three_way_merge_registry_yaml(base, ours, theirs, rel_path=_REG_REL)
        assert merged is None and "同键条目内容冲突" in err, f"跨侧三方各改必须死信: {err[:150]}"

    def test_dedup_count_surfaced_for_audit_log(self):
        """dedup_count 出口：三侧去重条数可被日志消费（≥1 即证通道在）。"""
        fams, err = cql._split_registry_entries(self.BASE, None)
        assert err is None
        _idx, err2, deduped = cql._index_family_blocks(fams)
        assert err2 is None and deduped == 1, f"字节同重复对应 dedup_count=1: got {deduped}, err={err2}"


# ---------------------------------------------------------------------------
# 件② dict 形态 passthrough 扩面（流式 list 元数据块活雷解除）
# ---------------------------------------------------------------------------


class TestDictFormMetadataPassthrough:
    """流式 list 元数据块（块文本含族键前缀 → safe_load 出 {tags: [...]}）不再死信。"""

    MINE = (
        "title: t\n"
        "tags: [ai-governance, autonomy, registry]\n"
        "related_arch: [TDMAP-001, REG-DATAFLOW-001]\n"
        "items:\n"
        "  - id: a\n    path: a.md\n"
    )

    def test_flow_style_metadata_family_passthrough_not_dead(self):
        """HEAD 6 册 14 块活雷复形：tags/related_arch 流式族 + 正常条目族同册落地零死信。"""
        theirs = self.MINE + "  - id: b\n    path: b.md\n"
        merged, err = cql.three_way_merge_registry_yaml(self.MINE, self.MINE, theirs, rel_path=_REG_REL)
        assert err == "", f"流式元数据块误死信（活雷未解除）: {err[:200]}"
        got = yaml.safe_load(merged)
        assert got["tags"] == ["ai-governance", "autonomy", "registry"], "元数据族 ours 原样保留"
        assert [e["id"] for e in got["items"]] == ["a", "b"], "正常条目族合并不受牵连"

    def test_expanded_passthrough_contains_dict_form_family(self):
        """白盒：扩面后 _scalar_family_keys 认领流式 dict 形态族（identity 判不了前提）。"""
        fams, err = cql._split_registry_entries(self.MINE, None)
        assert err is None
        pt = cql._scalar_family_keys(fams)
        assert {"tags", "related_arch"} <= pt, f"流式 dict 元数据族应进 passthrough: {pt}"

    def test_mixed_family_still_dead_letters_no_loosening(self):
        """混合形态族（标量块与常规条目并存）不在扩面列——维持身份判不了死信，不放宽。"""
        base = "title: t\nitems:\n  - id: a\n  - scalar_entry\n"
        merged, err = cql.three_way_merge_registry_yaml(base, base, base + "  - id: z\n", rel_path=_REG_REL)
        assert merged is None and "身份判不了" in err, "混合族必须维持既有死信方向"


# ---------------------------------------------------------------------------
# 件③ 声明驱动身份键（unique_key SSOT；缺失/解析失败/mismatch 一律退现状）
# ---------------------------------------------------------------------------


def _fd_reg(rows: list[tuple[str, str]], with_decl: bool = True) -> str:
    head = "unique_key:\n  - domain\n  - subdomain\n" if with_decl else ""
    body = "".join(f"  - domain: {d}\n    subdomain: {s}\n    name_zh: n\n" for d, s in rows)
    return f"{head}domains:\n{body}"


class TestDeclaredUniqueKeyIdentity:
    def test_list_form_cures_single_key_false_duplicate(self):
        """functional_domain 复形：同 domain 不同 subdomain（现单键错杀）→ 声明键治愈。"""
        base = _fd_reg([("D_A", "S1")])
        theirs = _fd_reg([("D_A", "S1"), ("D_A", "S2")])
        merged, err = cql.three_way_merge_registry_yaml(base, base, theirs, rel_path=_REG_REL)
        assert err == "", f"声明键未治愈单键错杀: {err[:200]}"
        rows = [(e["domain"], e["subdomain"]) for e in yaml.safe_load(merged)["domains"]]
        assert rows == [("D_A", "S1"), ("D_A", "S2")]

    def test_list_form_true_conflict_on_declared_key_still_dead(self):
        """声明键上的真冲突（同 domain+subdomain 各自改）→ 死信方向保留。"""
        base = _fd_reg([("D_A", "S1")])
        ours = base.replace("name_zh: n", "name_zh: ours版")
        theirs = base.replace("name_zh: n", "name_zh: theirs版")
        merged, err = cql.three_way_merge_registry_yaml(base, ours, theirs, rel_path=_REG_REL)
        assert merged is None and "同键条目内容冲突" in err, f"声明键真冲突必须死信: {err[:150]}"

    def test_per_family_dict_form_data_asset(self):
        """data_asset 按族 dict 声明形态：sources/datasets 各用各族键，互不串扰。"""
        base = (
            "unique_key:\n  sources: [source_id]\n  datasets: [dataset_id]\n"
            "sources:\n  - source_id: SRC-1\n    name: n\n"
            "datasets:\n  - dataset_id: DS-1\n    name: n\n"
        )
        theirs = (
            "unique_key:\n  sources: [source_id]\n  datasets: [dataset_id]\n"
            "sources:\n  - source_id: SRC-1\n    name: n\n  - source_id: SRC-2\n    name: n2\n"
            "datasets:\n  - dataset_id: DS-1\n    name: n\n  - dataset_id: DS-2\n    name: n2\n"
        )
        merged, err = cql.three_way_merge_registry_yaml(base, base, theirs, rel_path=_REG_REL)
        assert err == "", f"按族 dict 声明未生效: {err[:200]}"
        got = yaml.safe_load(merged)
        assert [e["source_id"] for e in got["sources"]] == ["SRC-1", "SRC-2"]
        assert [e["dataset_id"] for e in got["datasets"]] == ["DS-1", "DS-2"]

    def test_token_suffix_kept_under_declaration_multi_token_coexist(self):
        """声明 [file] 下 token 复合后缀保留：同 file 多 token 合法并存不被错杀（q-0078 复形）。"""
        base = "unique_key:\n  - file\ncreation_tokens:\n  - file: src/a.py\n    token: t1\n"
        theirs = base + "  - file: src/a.py\n    token: t2\n"
        merged, err = cql.three_way_merge_registry_yaml(base, base, theirs, rel_path=_REG_REL)
        assert err == "", f"声明键下多 token 形态被错杀: {err[:200]}"
        toks = [e["token"] for e in yaml.safe_load(merged)["creation_tokens"]]
        assert sorted(toks) == ["t1", "t2"]

    def test_no_declaration_falls_back_to_current_behavior(self):
        """无声明 → 默认复合键现状零漂移：真冲突死信 + 同 file 多 token 共存照旧。"""
        base = "items:\n  - id: a\n    v: 1\n"
        ours = "items:\n  - id: a\n    v: 2\n"
        theirs = "items:\n  - id: a\n    v: 3\n"
        merged, err = cql.three_way_merge_registry_yaml(base, ours, theirs, rel_path=_REG_REL)
        assert merged is None and "同键条目内容冲突" in err, "无声明真冲突必须维持现状死信"
        base2 = "items:\n  - file: a.py\n    token: t1\n"
        theirs2 = base2 + "  - file: a.py\n    token: t2\n"
        merged2, err2 = cql.three_way_merge_registry_yaml(base2, base2, theirs2, rel_path=_REG_REL)
        assert err2 == "" and [e["token"] for e in yaml.safe_load(merged2)["items"]] == ["t1", "t2"]

    def test_declaration_mismatch_across_sides_falls_back(self):
        """theirs 侧声明不同（跨窗口漂移）→ 整体退默认复合键：单键撞形仍按现状死信
        （mismatch 时 unique_key 声明不一致，两侧各自成立则会被声明键掩盖真冲突）。"""
        ours = "unique_key:\n  - domain\ndomains:\n  - domain: D_A\n    subdomain: S1\n    name_zh: n\n"
        theirs_diff_decl = (
            "unique_key:\n  - domain\n  - subdomain\n"
            "domains:\n  - domain: D_A\n    subdomain: S1\n    name_zh: n\n"
            "  - domain: D_A\n    subdomain: S2\n    name_zh: n\n"
        )
        merged, err = cql.three_way_merge_registry_yaml(ours, ours, theirs_diff_decl, rel_path=_REG_REL)
        assert merged is None and "同侧身份键重复" in err, f"声明 mismatch 必须退现状（单键死信）: {err[:150]}"

    def test_malformed_declaration_falls_back_to_default(self):
        """声明形态不识别（非清单字段）→ 退默认复合键，不引入新死法。"""
        text = "unique_key: domain\ndomains:\n  - domain: D_A\n    subdomain: S1\n    name_zh: n\n"
        assert cql._unique_key_decl(text) is None, "字符串声明不识别应返回 None"
        merged, err = cql.three_way_merge_registry_yaml(text, text, text, rel_path=_REG_REL)
        assert err == "", f"畸形声明不得阻断自合并: {err[:150]}"


# ---------------------------------------------------------------------------
# 件④a pool stale 重校验收进 env 计数闸（逃逸口封堵）
# ---------------------------------------------------------------------------


class _StaleEnvFailLanding:
    """stale 项 + head_reader git 读瞬态失败桩（模拟索引锁争用/句柄占用）。"""

    def __init__(self, repo_root: Path) -> None:
        self.target_branch = "dev"
        self.repo_root = repo_root
        self.landing_calls = 0

    def _item_paths(self, item: dict) -> list[str]:
        return []

    def _git_repo(self, *args: str, **_: object):
        raise RuntimeError("git rev-parse -> rc=128: index.lock 争用（QMine A1 逃逸口测试）")

    def __call__(self, item: dict, root: Path):
        self.landing_calls += 1
        raise AssertionError("stale 重校验环境失败不得触达 landing 主链路")


class _StaleOkLanding(_StaleEnvFailLanding):
    """stale 清标放行桩：head_reader 恒返回与 base_blob 一致的 sha（重校验通过）。"""

    def __init__(self, repo_root: Path, base_blob: str) -> None:
        super().__init__(repo_root)
        self._base_blob = base_blob

    def _git_repo(self, *args: str, **_: object):
        r = subprocess.CompletedProcess(["git"], 0)
        r.stdout = self._base_blob + "\n"
        r.stderr = ""
        return r

    def __call__(self, item: dict, root: Path):
        self.landing_calls += 1
        return cq.LandingResult(ok=True, landed_id="a" * 40)


def _mk_stale_item(qid: str, base_blob: str) -> dict:
    return {
        "qid": qid,
        "session_id": "s-qmine-a1",
        "created_at": "2026-09-25T00:00:00+00:00",
        "base_head": "",
        "meta": {"stale": True, "stale_by": "q-20260925-prev-0001"},
        "files": [{"path": "docs/x.txt", "base_blob": base_blob}],
    }


def _run_pool_single(tmp_path: Path, item: dict, landing) -> tuple[Path, dict, dict]:
    root = tmp_path / "q"
    cq._ensure_dirs(root)
    proc = root / "processing" / f"{item['qid']}.json"
    proc.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
    stats: dict = {"dead": 0, "done": 0, "processed_qids": [], "stale_cleared": 0, "cascade_marked": 0}
    shared: dict = {"processed": 0, "budget_left": None, "env_aborted": False}
    cql._pool_process_item(landing, root, proc, stats, threading.Lock(), shared)
    return root, stats, shared


class TestPoolStaleRevalidationCounted:
    def test_stale_env_failure_counted_and_back_to_pending(self, tmp_path: Path):
        """逃逸口封堵红蓝钉：stale 重校验 git 瞬态失败 → env_retry 计数 + 退回 pending，
        不再绕闸滞留 processing 无限重放（修复前：RuntimeError 裸逃逸，零计数）。"""
        landing = _StaleEnvFailLanding(tmp_path)
        item = _mk_stale_item("q-a1-esc-0001", "b" * 40)
        root, _stats, shared = _run_pool_single(tmp_path, item, landing)
        assert shared["env_aborted"] is True, "环境失败必须终止旗（与 landing 内环境失败同语义）"
        assert landing.landing_calls == 0, "重校验失败不得触达 landing 主链路"
        pending = json.loads((root / "pending" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert pending["meta"]["env_retry"] == 1, "env_retry 计数落项 JSON（跨轮存活）"
        assert pending.get("attempts") == 1, "B5 attempts 同步累加"

    def test_stale_env_failure_exhausts_three_rounds_to_dead_letter(self, tmp_path: Path):
        """同一 item 三轮环境失败 → 第 3 轮升级死信（防活锁），处方可行动。"""
        landing = _StaleEnvFailLanding(tmp_path)
        item = _mk_stale_item("q-a1-esc-0002", "b" * 40)
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        for round_no in (1, 2, 3):
            if round_no == 1:
                cur = item
            else:
                # 生产同名语义：pending→processing 原子搬移（留在原地会让 rename-back
                # 撞目标存在而失败，env_retry 计数读到的恒是 stale 副本）
                src = root / "pending" / f"{item['qid']}.json"
                proc = root / "processing" / f"{item['qid']}.json"
                os.replace(str(src), str(proc))
                cur = json.loads(proc.read_text(encoding="utf-8"))
            _run_pool_single(tmp_path, cur, landing)
        dead = json.loads((root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert dead["meta"]["env_retry"] == 3, "计数跨轮持久化"
        assert "env_retry=3" in dead["dead_reason"] and "requeue" in dead["dead_reason"], dead["dead_reason"][:200]

    def test_stale_revalidation_still_cleared_on_success(self, tmp_path: Path):
        """对照组：重校验通过 → 清标放行（既有语义零漂移，封堵不误伤正常 stale 件）。"""
        base_blob = "c" * 40
        landing = _StaleOkLanding(tmp_path, base_blob)
        item = _mk_stale_item("q-a1-esc-0003", base_blob)
        root, stats, _shared = _run_pool_single(tmp_path, item, landing)
        assert stats["stale_cleared"] == 1, "重校验通过必须清标放行"
        cleared = json.loads((root / "done" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert "stale" not in cleared["meta"] and "stale_cleared_at" in cleared["meta"]


# ---------------------------------------------------------------------------
# 件④b __call__ gates 相位计时（M5 矿①观测面：env 守卫 finally 单点）
# ---------------------------------------------------------------------------


class _StubGateway:
    """最小桩：claim/release 留痕，commit 做真 git commit（复用 qcure_m5 组装语义）。"""

    def __init__(self, worktree_path: Path) -> None:
        self._wt = worktree_path
        self.events: list[tuple[str, object]] = []

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        self.events.append(("claim", session_id))
        return list(files)

    def release_files(self, session_id: str, files: list[str]) -> None:
        self.events.append(("release", session_id))

    def commit(self, session_id: str, files: list[str], message: str, allow_non_worktree: bool = False, **_: object):
        self.events.append(("commit", session_id))
        for f in files:
            target = Path(f)
            if target.is_file():
                _git(self._wt, "add", "--", f)
            else:
                _git(self._wt, "rm", "--cached", "--ignore-unmatch", "--", f)
        _git(self._wt, "commit", "--no-verify", "-qm", message)
        r = _git(self._wt, "rev-parse", "HEAD")
        sha = r.stdout.decode("utf-8", errors="replace").strip()
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus

        return CommitResult(status=CommitStatus.OK, message="stub committed", commit_hash=sha)


def _git(cwd: Path, *args: str, check: bool = True):
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, timeout=60)
    if check and r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} -> rc={r.returncode}: {r.stderr.decode('utf-8', errors='replace')[:400]}"
        )
    return r


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")
    (repo / ".gitignore").write_text(".runtime/\n.ailocks/\n", encoding="utf-8")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "branch", "dev")
    return repo


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    return tmp_path / "commit_queue"


class TestGatesPhaseTiming:
    def test_gates_phase_recorded_on_landing_main_path(self, tmp_repo: Path, queue_root: Path):
        """落地主路径 → landing._phase_ms 必含 gates 相位（>0）；累加器单点在 env 守卫
        finally，Mode B 重试的第二次 commit 与 CAS 重试天然同享同一累加口径。"""
        stub = _StubGateway((queue_root / "worktree").resolve())
        landing = cql.WorktreeLanding(repo_root=tmp_repo, queue_root=queue_root, gateway=stub)
        item = cq.enqueue_item("sess-a1-gates", "feat: gates phase", [("docs/g.txt", b"g\n")], queue_root=queue_root)

        r = landing(item, queue_root)

        assert r.ok, f"落地失败: {r.reason}"
        phases = getattr(landing, cql._PHASE_ACC, {})
        assert phases.get("gates", 0.0) > 0.0, f"gates 相位未记录: {phases}"
        assert any(e[0] == "commit" for e in stub.events), "gates 计时锚必须在 gateway.commit 期间"

    def test_gates_phase_accumulates_across_calls(self, tmp_repo: Path, queue_root: Path):
        """跨项复用同一 landing：_record_phase 累加语义（第二项 gates ≥ 单项值，非覆盖）。"""
        stub = _StubGateway((queue_root / "worktree").resolve())
        landing = cql.WorktreeLanding(repo_root=tmp_repo, queue_root=queue_root, gateway=stub)
        item1 = cq.enqueue_item("sess-a1-g2a", "feat: one", [("docs/g1.txt", b"1\n")], queue_root=queue_root)
        item2 = cq.enqueue_item("sess-a1-g2b", "feat: two", [("docs/g2.txt", b"2\n")], queue_root=queue_root)

        assert landing(item1, queue_root).ok
        first = getattr(landing, cql._PHASE_ACC, {}).get("gates", 0.0)
        assert landing(item2, queue_root).ok
        second = getattr(landing, cql._PHASE_ACC, {}).get("gates", 0.0)

        assert first > 0.0 and second > first, (
            f"gates 相位必须跨项累加（_record_phase 累加语义）: first={first} second={second}"
        )
