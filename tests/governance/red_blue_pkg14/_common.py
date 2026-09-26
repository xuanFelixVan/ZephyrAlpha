# [A_test] module_id: MOD-TEST-RB14-BASE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | docs/_working/commit_speedup_campaign/90_verification/red_blue_pkg14_report.md | §
# [MODULE] governance.red_blue_pkg14._common
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; subprocess(git); scripts.commit_queue; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现（tests/governance/red_blue_pkg14/*）
# [STARTUP] python -m pytest tests/governance/red_blue_pkg14/
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根 + tmp 手术副本），绝不触生产活体
#   （真 belt/真队列 .runtime/commit_queue/真 dev ref 一律不写不杀）；红方手术=对产品
#   文件的**字节级副本**做锚定替换后经 importlib 以独立模块名装载（原文件零触碰，
#   sha256 不变）；蓝方=worktree 现行产品码直接在沙盒跑。tests/ 免 token。
# [MODIFY-GUARD] 包14 红蓝极限对抗 7 场景（st-commitspeed-tbl-20260924）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 手术锚缺失=测试失败（防锚漂移后假绿）；断言失败即测试失败
# [TESTS] 本目录
# [TTL] task_bound
"""_common.py — red_blue_pkg14 共享设施（提交链治本夜战红蓝对抗 包14）。

沙盒三件套：
- ``sb_repo``：一次性 git 仓（main+dev 分支），等价 test_commit_queue_pool 约定；
- ``sb_queue``：一次性队列根（永不指向 D:/ZephyrAlpha/.runtime/commit_queue）；
- ``load_surgered``：把产品模块复制到 tmp、按锚定对做文本替换、以独立模块名装载
  ——红方"旧码副本"（复现已修复前的行为），原产品文件字节不动。
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
LANDING_SRC = REPO_ROOT / "scripts" / "governance" / "commit_queue_landing.py"
QUEUE_SRC = REPO_ROOT / "scripts" / "commit_queue.py"
CACHE_SRC = REPO_ROOT / "src" / "zephyr" / "gov_enforcement" / "rule_bridge" / "gate_cache_preflight.py"


def git(cwd: Path, *args: str, check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    """沙盒仓 git 调用（永不指向生产仓；check=False 用于红方攻击面）。"""
    e = dict(os.environ)
    e.setdefault("GIT_AUTHOR_NAME", "t")
    e.setdefault("GIT_AUTHOR_EMAIL", "t@t")
    e.setdefault("GIT_COMMITTER_NAME", "t")
    e.setdefault("GIT_COMMITTER_EMAIL", "t@t")
    if env:
        e.update(env)
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, timeout=60, env=e)
    if check and r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} -> rc={r.returncode}: {r.stderr.decode('utf-8', errors='replace')[:400]}"
        )
    return r


def git_text(cwd: Path, *args: str) -> str:
    return git(cwd, *args).stdout.decode("utf-8", errors="replace").strip()


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture()
def sb_repo(tmp_path: Path) -> Path:
    """一次性沙盒仓（main 初始化 + dev 分支），绝不触主仓。"""
    repo = tmp_path / "sb_repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "test")
    git(repo, "config", "core.autocrlf", "false")
    (repo / ".gitignore").write_text(".runtime/\n.ailocks/\n", encoding="utf-8")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "init")
    git(repo, "branch", "dev")
    return repo


@pytest.fixture()
def sb_queue(tmp_path: Path) -> Path:
    return tmp_path / "sb_commit_queue"


def load_surgered(
    src: Path,
    replacements: list[tuple[str, str]],
    module_name: str,
    tmp_path: Path,
    *,
    expected_counts: list[int] | None = None,
    append_tail: str = "",
):
    """产品模块的手术副本装载（红方旧码复活器）。

    - 原文件字节零触碰（副本写 tmp_path）；
    - 每个锚替换断言存在且次数=expected_counts（缺锚=失败，防锚漂移假绿）；
    - 以 module_name 独立装载（不污染 sys.modules 的真模块）。
    """
    text = src.read_text(encoding="utf-8")
    for i, (old, new) in enumerate(replacements):
        n = 1 if expected_counts is None else expected_counts[i]
        found = text.count(old)
        assert found == n, f"手术锚#{i} 期望 {n} 次、实见 {found} 次（锚漂移?）: {old[:80]!r}"
        text = text.replace(old, new)
    if append_tail:
        text += "\n\n" + append_tail + "\n"
    dst = tmp_path / f"surgered_{module_name.replace('.', '_')}.py"
    dst.write_text(text, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(module_name, dst)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod  # 手术副本内部 import 自身名字时命中副本
    spec.loader.exec_module(mod)
    return mod


class RecordingStubGateway:
    """真 git commit 桩（门禁豁免、ref/对象语义保真）。

    - 记录每次 commit 的 kwargs（internal_call 等 D2 断言用）；
    - overlap_guard：同路径 commit 体互斥检测（路径锁不互踩断言）；
    - fail_plan：qid -> 抛错计划（"once"=首次普通 Exception / "always" /
      "base_once"=首次 BaseException 杀工 / callable）。
    """

    def __init__(
        self,
        worktree_path: Path,
        *,
        fail_plan: dict | None = None,
        overlap_guard: dict | None = None,
        record: list | None = None,
    ) -> None:
        self._wt = worktree_path
        self.fail_plan = fail_plan or {}
        self.overlap_guard = overlap_guard  # {"flag": bool, "lock": threading.Lock, "violations": list}
        self.record = record if record is not None else []
        self.commits: list[dict] = []

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        return list(files)

    def release_files(self, session_id: str, files: list[str]) -> None:
        pass

    def commit(self, session_id, files, message, **kw):  # noqa: ANN001, ANN003
        plan = self.fail_plan.pop("next", None)
        if plan == "once":
            raise RuntimeError("rb14 注入的单次瞬态异常")
        if plan == "base_once":
            raise BaseException("rb14 注入的杀工 BaseException")
        if callable(plan):
            plan(session_id, files, message, kw)
        entry = {"session_id": session_id, "files": list(files), "message": message, "kw": dict(kw)}
        self.record.append(entry)
        guard = self.overlap_guard
        if guard is not None:
            with guard["lock"]:
                if guard["flag"]:
                    guard["violations"].append(sorted(str(f) for f in files))
                guard["flag"] = True
            try:
                self._do_commit(files, message)
            finally:
                with guard["lock"]:
                    guard["flag"] = False
        else:
            self._do_commit(files, message)
        entry["commit_hash"] = git_text(self._wt, "rev-parse", "HEAD")
        self.commits.append(entry)
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus

        return CommitResult(status=CommitStatus.OK, message="rb14-stub", commit_hash=entry["commit_hash"])

    def _do_commit(self, files: list[str], message: str) -> None:
        for f in files:
            target = Path(f) if Path(f).is_absolute() else self._wt / f
            if target.is_file():
                git(self._wt, "add", "--", f)
            else:
                git(self._wt, "rm", "--cached", "--ignore-unmatch", "--", f)
        r = git(self._wt, "commit", "--no-verify", "-qm", message, check=False)
        if r.returncode != 0:
            out = r.stdout.decode("utf-8", errors="replace") + r.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"stub commit 失败（nothing to commit?）: {out[:300]}")


def make_stub_landing_factory(record: list, module=None, **stub_kwargs):
    """make_worker_landing 替身工厂：指定模块的 WorktreeLanding + 桩 gateway。

    module=None 用现行产品模块；红方传手术副本模块，保证落的是「副本的 landing」。
    """
    real_make = (module or __import__("scripts.governance.commit_queue_landing", fromlist=["x"])).make_worker_landing

    def _make(repo, root, worker_id):  # noqa: ANN001
        landing = real_make(repo, root, worker_id)
        landing._gateway = RecordingStubGateway(landing.worktree_path, record=record, **stub_kwargs)
        return landing

    return _make


def read_wave_log(queue_root: Path) -> str:
    p = queue_root / "pool_wave.log"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def drain_stats_to_list(stats: dict) -> list[str]:
    return list(stats.get("processed_qids") or [])


def enqueue(repo: Path, qroot: Path, sid: str, rel: str, content: str, msg: str, **opt_kw) -> dict:
    """沙盒入队便捷封装（默认 base_head=dev）。"""
    import scripts.commit_queue as cq

    opts_kw = {"base_head": git_text(repo, "rev-parse", "refs/heads/dev")}
    opts_kw.update(opt_kw)
    return cq.enqueue_item(
        sid,
        msg,
        [(rel, content.encode("utf-8"))],
        queue_root=qroot,
        options=cq.EnqueueOptions(**opts_kw),
    )


def run_py_subprocess(script: Path, args: list[str], timeout: float = 240.0) -> subprocess.CompletedProcess:
    """独立 python 进程跑沙盒脚本（PYTHONPATH=worktree 根+src）。"""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(REPO_ROOT), str(REPO_ROOT / "src"), env.get("PYTHONPATH", "")])
    env["ZEPHYR_CQ_C1_DEBOUNCE"] = env.get("ZEPHYR_CQ_C1_DEBOUNCE", "")
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        timeout=timeout,
        env=env,
        cwd=str(REPO_ROOT),
    )


# S1 子进程脚本模板：独立 serializer 进程（非 belt）跑 drain_queue_pool。
# mode 语义见 test_rb14_s1_worker_revival.py 注释。
S1_SUBPROCESS_TEMPLATE = r"""
import json, sys, threading
from pathlib import Path

repo_root = Path(sys.argv[1])
queue_root = Path(sys.argv[2])
mode = sys.argv[3]
out_path = Path(sys.argv[4])
old_module = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] not in ("-", "") else None

sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root))

import scripts.governance.commit_queue_landing as cql

if old_module:
    import importlib.util
    spec = importlib.util.spec_from_file_location("cql_rb14_old", old_module)
    cql = importlib.util.module_from_spec(spec)
    sys.modules["cql_rb14_old"] = cql
    spec.loader.exec_module(cql)

real_claim = cql._pool_claim_item
real_process = cql._pool_process_item
state = {"raised": 0, "processed": 0}


class Stub:
    def __init__(self, wt):
        self._wt = wt

    def claim_files(self, session_id, files, adopt_prior_work=False):
        return list(files)

    def release_files(self, session_id, files):
        pass

    def commit(self, session_id, files, message, **kw):
        import subprocess
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus
        for f in files:
            subprocess.run(["git", "add", "--", f], cwd=str(self._wt), check=True, capture_output=True)
        subprocess.run(["git", "commit", "--no-verify", "-qm", message], cwd=str(self._wt), check=True,
                       capture_output=True)
        return CommitResult(status=CommitStatus.OK, message="rb14-subprocess-stub",
                            commit_hash=subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(self._wt),
                                                       check=True, capture_output=True).stdout.decode().strip())


def _make(repo, root, worker_id):
    landing = real_make(repo, root, worker_id)
    landing._gateway = Stub(landing.worktree_path)
    return landing


real_make = cql.make_worker_landing
cql.make_worker_landing = _make

if mode == "claim_raise_once":
    def patched(root):
        if state["raised"] == 0:
            state["raised"] += 1
            raise RuntimeError("rb14-S1 注入单次认领异常")
        return real_claim(root)
    cql._pool_claim_item = patched
elif mode == "claim_always_raise":
    def patched(root):
        state["raised"] += 1
        raise RuntimeError("rb14-S1 注入持续认领异常")
    cql._pool_claim_item = patched
elif mode == "process_crash_once":
    def patched(*a, **kw):
        if state["processed"] == 0:
            state["processed"] += 1
            import os
            os._exit(9)  # 硬杀独立 serializer 进程（模拟工棚死亡）
        return real_process(*a, **kw)
    cql._pool_process_item = patched

stats = cql.drain_queue_pool(queue_root, repo_root=repo_root, workers=2, max_items=None)
out_path.write_text(json.dumps(stats, ensure_ascii=False), encoding="utf-8")
print("RB14_S1_OK")
"""
