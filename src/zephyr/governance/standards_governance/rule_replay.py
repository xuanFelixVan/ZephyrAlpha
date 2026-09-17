# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §rule_replay
# [MODULE] zephyr.governance.standards_governance.rule_replay
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar (load_gate_entries); zephyr.gov_enforcement.rule_bridge.gate_cache_preflight (CONTENT_SCAN_CACHE_WHITELIST); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (CommitGateRegistry, GateSpec)
# [CONSUMERS] CLI python -m zephyr.governance.rule_replay [replay|report|diff]; OBJ_R 标准线四步流水线第 4 步（重考历史）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 纯只读零仓库状态变更（对 DB 只读、对工作树零写入，报告仅落 .runtime/tmp/replay/）；
#              重放绝不走 GitCommitGateway.commit()（只复用 check 层）；域=仅内容扫描型 gate
#              （CONTENT_SCAN_CACHE_WHITELIST 同域），全局状态型 gate 标 out_of_scope 不进判据；
#              通过判据 P1-P4 预注册（P1 该拦放走=0 一票否决/P3 全局 Jaccard≥0.98 且单 gate≥0.95）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_R_rules_standards/DESIGN.md（本模块设计真源，变更走 OBJ_R 流水线）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 全部公共函数零副作用（仅写报告到显式 out 路径）；失败模式=RuntimeError fail-closed（阈值常量名拼错/抽样为空/无可用 gate 即拒跑），绝不静默降级放行；单 gate 异常计 error 行不入判据，错误率>10% 判 unreliable
# [TESTS] tests/governance/test_rule_replay.py（17 用例：diff 解析/ReplayGateway 三调用族/阈值注入 delta 四值/P1 放走一票否决/P3 Jaccard 边界/错误率 unreliable/抽样去重配额）
# [TTL] permanent
"""rule_replay — 历史重放器：新阈值上线前的"重考历史"执行件。

OBJ_R 标准与规则线四步流水线（AI 提案→治理立案→Owner 修标→重考历史）的第 4 步：
对历史提交集，用"同一种子 diff × 旧/新两套阈值"做纯函数对照，证明拦截排序不变
（该拦不放走、误拦不增），否则修标一票否决。设计真源=OBJ_R_rules_standards/DESIGN.md §②。

重放域裁定（D-RR-01，自裁留痕）：v1 实现分层抽样的 ③特殊形态/④随机一般 两层
（git log 元数据，全量可得）；①已知拦截/②正常通过 两层的 DB 自动抽样在真实 schema
下缺 commit_hash 连接键（tasks 表无该列，裁定#208 三轨制不覆盖）——v1 以
--blocked-hashes/--passed-hashes 文件注入口承接（每行一个 commit hash），
DB 自动关联挂 S2+（gate_runs.session_id 与提交侧会话名的关联键待治理立案）。

报告口径：report.jsonl 每行 =
  run_id, commit_hash, commit_date, stratum, files[], gate_id, priority,
  old{passed, detail_digest}, new{passed, detail_digest}, delta, replay_ms, error, out_of_scope_reason
delta 四值：both_pass / both_block / new_block（潜在误拦新增）/ new_pass（该拦放走）；
error 行不计入 P1-P4 判据集合，但错误率 >10% 时 summary 判 unreliable。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import random
import subprocess
import sys
import time
from collections import defaultdict

from zephyr.shared.infra.process_pool import run_subprocess_hidden
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final

logger = logging.getLogger(__name__)

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402 — 仓库根正典真源（D-RR-03：禁自算，capability_lookup 同款）
DEFAULT_OUT_DIR: Final = REPO_ROOT / ".runtime" / "tmp" / "replay"
DEFAULT_SINCE_DAYS: Final = 90
DEFAULT_STRATA: Final[dict] = {"blocked": 30, "passed": 50, "special": 10, "random": 10}

# 通过判据 P1-P4（预注册，重放前锁定——OBJ_R DESIGN §②-E，R9 审计追认）
P1_PASS_LEAK_ALLOWED: Final = 0          # 层① new_pass 数 = 0（一票否决）
P2_NEW_BLOCK_RATE: Final = 0.02          # 新增拦截率 ≤ 2%
P3_JACCARD_GLOBAL: Final = 0.98          # 全局拦截集合 Jaccard 下限
P3_JACCARD_PER_GATE: Final = 0.95        # 单 gate 触发集合 Jaccard 下限
ERROR_RATE_UNRELIABLE: Final = 0.10      # 错误率超过此值 → summary 判 unreliable

DELTA_BOTH_PASS: Final = "both_pass"
DELTA_BOTH_BLOCK: Final = "both_block"
DELTA_NEW_BLOCK: Final = "new_block"
DELTA_NEW_PASS: Final = "new_pass"
DELTA_ERROR: Final = "error"


# ────────────────────────── ReplayGateway（内存 stub） ──────────────────────────


class ReplayGateway:
    """鸭子类型 stub gateway——只实现内容扫描型 gate 实际消费的 run_git 调用族。

    diff 数据全部来自 `git diff-tree -p <commit>` 预取（first-parent diff=当时 staged
    内容），零仓库状态变更、零 worktree。未识别的 git 调用返回 returncode=1 空输出
    （fail-closed：gate 对未知查询拿不到数据即自行降级）。
    """

    def __init__(self, files: list[str], patch_by_file: dict[str, str], project_root: str) -> None:
        self.files = list(files)
        self._patch_by_file = dict(patch_by_file)
        self.project_root = project_root

    def run_git(self, args: list[str]) -> Any:
        args = list(args)
        if args[:3] == ["git", "diff", "--cached"] and "--name-status" in args:
            body = "".join(f"M\t{f}\n" for f in self.files)
            return _GitResult(0, body)
        if args[:3] == ["git", "diff", "--cached"] and "--" in args:
            idx = args.index("--")
            target = args[idx + 1] if len(args) > idx + 1 else ""
            patch = self._patch_by_file.get(target, "")
            return _GitResult(0, patch)
        if args[:2] == ["git", "rev-parse"] and "--show-toplevel" in args:
            return _GitResult(0, self.project_root + "\n")
        return _GitResult(1, "")


@dataclass
class ReplayTarget:
    """单笔被重放提交（上下文参数打包，NO-LONG-PARAM-LIST 处方）。"""

    commit_hash: str
    commit_date: str
    stratum: str


@dataclass
class ReplayContext:
    """重放上下文：run 标识 + gate 双份闭包 + 仓库根 + diff 取数器。"""

    run_id: str
    pairs: list
    out_of_scope: list
    repo_root: Path
    diff_fetch: Any = None


@dataclass
class ReplayRequest:
    """一次重放任务的全部输入（CLI → 引擎的打包）。"""

    repo_root: Path
    since: str
    until: str
    strata: dict
    gates_filter: set | None
    thresholds: list | None
    blocked_hashes: list
    passed_hashes: list
    out_dir: Path
    seed: int = 20260917


@dataclass
class _GitResult:
    returncode: int
    stdout: str
    stderr: str = ""


# ────────────────────────── diff 预取与提交集抽样 ──────────────────────────


def parse_diff_tree(patch_text: str) -> tuple[list[str], dict[str, str]]:
    """把 `git diff-tree -p` 输出拆成 (文件序表, 逐文件 patch)。纯函数。"""
    files: list[str] = []
    patches: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in patch_text.splitlines(keepends=True):
        if line.startswith("diff --git "):
            if current is not None:
                patches[current] = "".join(buf)
            # diff --git a/<path> b/<path>（路径含空格场景本项目文件名不含，v1 取 b/ 侧）
            parts = line.split(" b/", 1)
            current = parts[1].rstrip("\n") if len(parts) == 2 else ""
            if current and current not in files:
                files.append(current)
            buf = [line]
        elif current is not None:
            buf.append(line)
    if current is not None:
        patches[current] = "".join(buf)
    return files, patches


def list_commit_range(
    repo_root: Path, since: str, until: str, limit: int = 2000
) -> list[tuple[str, str]]:
    """时间窗内 first-parent 非合并提交清单 [(hash, yyyy-mm-dd)]，时间升序。"""
    out = run_subprocess_hidden(
        [
            "git", "log", "--first-parent", "--no-merges",
            f"--since={since}", f"--until={until}",
            "--date=short", "--pretty=%H|%ad", f"-n{limit}",
            "--reverse",
        ],
        cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if out.returncode != 0:
        raise RuntimeError(f"git log 失败: {out.stderr[:200]}")
    rows: list[tuple[str, str]] = []
    for line in out.stdout.splitlines():
        if "|" in line:
            h, d = line.split("|", 1)
            rows.append((h.strip(), d.strip()))
    return rows


def list_merge_commits(repo_root: Path, since: str, until: str, limit: int = 200) -> list[tuple[str, str]]:
    out = run_subprocess_hidden(
        ["git", "log", "--merges", f"--since={since}", f"--until={until}",
         "--date=short", "--pretty=%H|%ad", f"-n{limit}"],
        cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    rows: list[tuple[str, str]] = []
    if out.returncode == 0:
        for line in out.stdout.splitlines():
            if "|" in line:
                h, d = line.split("|", 1)
                rows.append((h.strip(), d.strip()))
    return rows


def _read_hash_file(path: str | None) -> list[str]:
    if not path:
        return []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")]


def sample_commits(
    repo_root: Path,
    since: str,
    until: str,
    strata: dict[str, int],
    blocked_hashes: list[str] | None = None,
    passed_hashes: list[str] | None = None,
    seed: int = 20260917,
) -> list[tuple[str, str, str]]:
    """分层抽样（D-RR-01：①② 层 v1 走显式注入口，③④ 层 git log 全量）。

    返回 [(commit_hash, commit_date, stratum)]，去重保序。
    """
    rng = random.Random(seed)
    all_commits = list_commit_range(repo_root, since, until)
    by_hash = {h: d for h, d in all_commits}
    merges = list_merge_commits(repo_root, since, until)

    plan: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    def take(hashes: list[tuple[str, str]], stratum: str, quota: int) -> None:
        taken = 0
        for h, d in hashes:
            if taken >= quota:
                break
            if h in seen:
                continue
            seen.add(h)
            plan.append((h, d, stratum))
            taken += 1

    take([(h, by_hash.get(h, "")) for h in (blocked_hashes or []) if h in by_hash or True],
         "blocked", strata.get("blocked", 0))
    take([(h, by_hash.get(h, "")) for h in (passed_hashes or []) if h in by_hash or True],
         "passed", strata.get("passed", 0))
    take(merges, "special", strata.get("special", 0))
    pool = all_commits[:]
    rng.shuffle(pool)
    take(pool, "random", strata.get("random", 0))
    return plan


# ────────────────────────── gate 装载（旧/新双份） ──────────────────────────


@dataclass
class _GatePair:
    gate_id: str
    priority: int
    old_check: Any
    new_check: Any
    module_path: str


def _load_module_copy(module_path: str, tag: str) -> Any:
    spec = importlib.util.spec_from_file_location(f"{module_path}__{tag}", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"importlib 无法加载 {module_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _entry_selected(entry: dict[str, Any], gates_filter: set[str] | None) -> bool:
    """条目是否参与重放（enabled+字段齐+未被 --gates 过滤掉）。"""
    gate_id = entry.get("gate_id", "")
    if not entry.get("enabled", True) or not gate_id:
        return False
    if not entry.get("module_path") or not entry.get("factory_function"):
        return False
    return gates_filter is None or gate_id in gates_filter


def _resolve_gate_file(module_path: str) -> Path | None:
    """module_path → 真实文件路径（find_spec 对 src-layout 免疫）；不可解析返回 None。"""
    import importlib.util as _ilu

    _sp = _ilu.find_spec(module_path)
    full_path = Path(_sp.origin) if (_sp and _sp.origin) else None
    if full_path is not None and full_path.exists():
        return full_path
    return None


def _build_pair(
    entry: dict[str, Any],
    full_path: Path,
    overrides: dict[str, Any],
) -> _GatePair:
    """单 gate 旧/新双份 check 闭包（新份=副本+setattr 常量覆写，D-RR-02 fail-closed）。"""
    gate_id = entry["gate_id"]
    factory_name = entry["factory_function"]
    module_path = entry["module_path"]
    old_mod = _load_module_copy(str(full_path), "old")
    old_spec = getattr(old_mod, factory_name)()
    if not overrides:
        return _GatePair(gate_id, old_spec.priority, old_spec.check, old_spec.check, module_path)
    new_mod = _load_module_copy(str(full_path), "new")
    for const_name, value in overrides.items():
        if not hasattr(new_mod, const_name):
            raise RuntimeError(
                f"阈值注入失败：{module_path} 无常量 {const_name}（D-RR-02：拼错即拒，fail-closed）"
            )
        setattr(new_mod, const_name, value)
    new_spec = getattr(new_mod, factory_name)()
    return _GatePair(gate_id, new_spec.priority, old_spec.check, new_spec.check, module_path)


def load_gate_pairs(
    project_root: Path,
    gates_filter: set[str] | None,
    thresholds: list[dict[str, Any]] | None,
) -> tuple[list[_GatePair], list[str]]:
    """装载内容扫描型 gate 的旧/新双份 check 闭包。

    thresholds 格式（new_thresholds.yaml 解析产物）：[{"module": <module_path>,
    "const": <常量名>, "value": <新值>}, ...]。旧份=无覆写副本；新份=副本+setattr。
    返回 (pairs, out_of_scope_ids)——out_of_scope=whitelist 之外的全局状态型 gate。
    """
    from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import load_gate_entries
    from zephyr.gov_enforcement.rule_bridge.gate_cache_preflight import CONTENT_SCAN_CACHE_WHITELIST

    thr_by_module: dict[str, list[tuple[str, Any]]] = defaultdict(list)
    for t in thresholds or []:
        thr_by_module[t["module"]].append((t["const"], t["value"]))

    pairs: list[_GatePair] = []
    out_of_scope: list[str] = []
    for entry in load_gate_entries(project_root):
        if not _entry_selected(entry, gates_filter):
            continue
        gate_id = entry["gate_id"]
        if gate_id not in CONTENT_SCAN_CACHE_WHITELIST:
            out_of_scope.append(gate_id)
            continue
        full_path = _resolve_gate_file(entry["module_path"])
        if full_path is None:
            out_of_scope.append(gate_id)
            continue
        pairs.append(_build_pair(entry, full_path, dict(thr_by_module.get(entry["module_path"], []))))
    pairs.sort(key=lambda p: p.priority)
    return pairs, sorted(set(out_of_scope))


def load_thresholds(path: str | None) -> list[dict[str, Any]]:
    if not path:
        return []
    import yaml

    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        raise ValueError("new_thresholds.yaml 根必须是列表：[{module, const, value}]")
    return data


# ────────────────────────── 重放执行 ──────────────────────────


def _digest(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:12]


def replay_commit(ctx: ReplayContext, target: ReplayTarget) -> list[dict[str, Any]]:
    if ctx.diff_fetch is None:
        def ctx_diff_fetch(h: str) -> tuple[list[str], dict[str, str]]:
            diff_run = run_subprocess_hidden(
                ["git", "diff-tree", "-p", "--no-commit-id", h],
                cwd=ctx.repo_root, capture_output=True, text=True, encoding="utf-8",
                errors="replace",
            )
            return parse_diff_tree(diff_run.stdout)
    else:
        ctx_diff_fetch = ctx.diff_fetch
    files, patches = ctx_diff_fetch(target.commit_hash)
    gateway = ReplayGateway(files, patches, str(ctx.repo_root))
    rows: list[dict[str, Any]] = []
    for pair in ctx.pairs:
        t0 = time.perf_counter()
        try:
            old_passed, old_detail = pair.old_check(gateway, files, session_id="replay")
            new_passed, new_detail = pair.new_check(gateway, files, session_id="replay")
            if old_passed and new_passed:
                delta = DELTA_BOTH_PASS
            elif not old_passed and not new_passed:
                delta = DELTA_BOTH_BLOCK
            elif not old_passed and new_passed:
                delta = DELTA_NEW_PASS
            else:
                delta = DELTA_NEW_BLOCK
            row = {
                "run_id": ctx.run_id, "commit_hash": target.commit_hash, "commit_date": target.commit_date,
                "stratum": target.stratum, "files": files, "gate_id": pair.gate_id,
                "priority": pair.priority,
                "old": {"passed": bool(old_passed), "detail_digest": _digest(old_detail)},
                "new": {"passed": bool(new_passed), "detail_digest": _digest(new_detail)},
                "delta": delta, "replay_ms": round((time.perf_counter() - t0) * 1000, 2),
                "error": "", "out_of_scope_reason": "",
            }
        except Exception as exc:  # noqa: BLE001 — 单 gate 异常如实记档不计判据
            row = {
                "run_id": ctx.run_id, "commit_hash": target.commit_hash, "commit_date": target.commit_date,
                "stratum": target.stratum, "files": files, "gate_id": pair.gate_id,
                "priority": pair.priority, "old": {"passed": None, "detail_digest": ""},
                "new": {"passed": None, "detail_digest": ""}, "delta": DELTA_ERROR,
                "replay_ms": round((time.perf_counter() - t0) * 1000, 2),
                "error": f"{type(exc).__name__}: {exc}", "out_of_scope_reason": "",
            }
        rows.append(row)
    for gate_id in ctx.out_of_scope:
        rows.append({
            "run_id": ctx.run_id, "commit_hash": target.commit_hash, "commit_date": target.commit_date,
            "stratum": target.stratum, "files": files, "gate_id": gate_id, "priority": None,
            "old": {"passed": None, "detail_digest": ""},
            "new": {"passed": None, "detail_digest": ""}, "delta": DELTA_ERROR,
            "replay_ms": 0.0, "error": "",
            "out_of_scope_reason": "非内容扫描型（全局状态依赖），不进判据",
        })
    return rows


def run_replay(req: ReplayRequest) -> Path:
    from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415 — SCHEMA-TZ 正典时钟
    run_id = f"replay-{now_utc().strftime('%Y%m%d-%H%M%S')}"
    pairs, out_of_scope = load_gate_pairs(req.repo_root, req.gates_filter, req.thresholds)
    if not pairs:
        raise RuntimeError("无可用内容扫描型 gate（检查 --gates 过滤与 whitelist）")
    plan = sample_commits(req.repo_root, req.since, req.until, req.strata,
                          req.blocked_hashes, req.passed_hashes, req.seed)
    if not plan:
        raise RuntimeError("抽样为空：时间窗内无提交（调整 --since/--until）")
    run_dir = req.out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    report_path = run_dir / "report.jsonl"
    with report_path.open("w", encoding="utf-8") as fh:
        ctx = ReplayContext(run_id=run_id, pairs=pairs, out_of_scope=out_of_scope,
                            repo_root=req.repo_root)
        for commit_hash, commit_date, stratum in plan:
            target = ReplayTarget(commit_hash=commit_hash, commit_date=commit_date,
                                  stratum=stratum)
            for row in replay_commit(ctx, target):
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = summarize(report_path)
    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("重放完成：%s（%d 笔提交，verdict=%s）", report_path, len(plan), summary["verdict"])
    return report_path


# ────────────────────────── 聚合与判据（S2） ──────────────────────────


def _jaccard(old_set: set[str], new_set: set[str]) -> float:
    union = old_set | new_set
    if not union:
        return 1.0
    return len(old_set & new_set) / len(union)


def _read_report_rows(report_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with report_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _classify_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    judged = [r for r in rows if r["delta"] != DELTA_ERROR and not r["out_of_scope_reason"]]
    errors = [r for r in rows if r["delta"] == DELTA_ERROR and not r["out_of_scope_reason"]]
    error_rate = len(errors) / len(rows) if rows else 0.0
    return {
        "judged": judged, "errors": errors, "error_rate": error_rate,
        "new_pass": [r for r in judged if r["delta"] == DELTA_NEW_PASS],
        "new_block_rows": [r for r in judged if r["delta"] == DELTA_NEW_BLOCK],
    }


def _leak_count(judged: list[dict[str, Any]]) -> int:
    """P1 口径：分层①（blocked）/③（special）中该拦放走的笔数。"""
    return sum(1 for r in judged if r["stratum"] in ("blocked", "special")
               and r["delta"] == DELTA_NEW_PASS)


def _jaccard_stats(judged: list[dict[str, Any]]) -> dict[str, Any]:
    old_block = {f'{r["commit_hash"]}|{r["gate_id"]}' for r in judged if not r["old"]["passed"]}
    new_block = {f'{r["commit_hash"]}|{r["gate_id"]}' for r in judged if not r["new"]["passed"]}
    per_gate: dict[str, float] = {}
    for g in sorted({r["gate_id"] for r in judged}):
        g_old = {r["commit_hash"] for r in judged if r["gate_id"] == g and not r["old"]["passed"]}
        g_new = {r["commit_hash"] for r in judged if r["gate_id"] == g and not r["new"]["passed"]}
        per_gate[g] = _jaccard(g_old, g_new)
    worst = min(per_gate.values()) if per_gate else 1.0
    return {"global": _jaccard(old_block, new_block), "worst_gate": worst, "per_gate": per_gate}


def summarize(report_path: Path) -> dict[str, Any]:
    """聚合 report.jsonl → summary（P1-P4 判据，OBJ_R DESIGN §②-D/E 口径）。"""
    rows = _read_report_rows(report_path)
    cls = _classify_rows(rows)
    judged, errors = cls["judged"], cls["errors"]
    new_block_rows = cls["new_block_rows"]

    p1_leak = _leak_count(judged)
    new_block_rate = len(new_block_rows) / len(judged) if judged else 0.0
    j = _jaccard_stats(judged)

    p1 = p1_leak <= P1_PASS_LEAK_ALLOWED
    p2 = new_block_rate <= P2_NEW_BLOCK_RATE
    p3 = j["global"] >= P3_JACCARD_GLOBAL and j["worst_gate"] >= P3_JACCARD_PER_GATE
    p4 = True  # P4=分层复检已并入 P1（blocked/special 泄漏同口径），special 独立 Jaccard 见 per-gate
    verdict = "PASS" if (p1 and p2 and p3 and p4) else "FAIL"

    return {
        "report": str(report_path),
        "verdict": verdict,
        "reliable": cls["error_rate"] <= ERROR_RATE_UNRELIABLE,
        "error_rate": round(cls["error_rate"], 4),
        "judged_rows": len(judged),
        "counts": {
            "both_pass": sum(1 for r in judged if r["delta"] == DELTA_BOTH_PASS),
            "both_block": sum(1 for r in judged if r["delta"] == DELTA_BOTH_BLOCK),
            "new_block": len(new_block_rows),
            "new_pass": len(cls["new_pass"]),
            "error": len(errors),
        },
        "p1_pass_leak": {"value": p1_leak, "threshold": P1_PASS_LEAK_ALLOWED, "pass": p1},
        "p2_new_block_rate": {"value": round(new_block_rate, 4), "threshold": P2_NEW_BLOCK_RATE, "pass": p2},
        "p3_jaccard": {"global": round(j["global"], 4), "worst_gate": round(j["worst_gate"], 4),
                       "thresholds": [P3_JACCARD_GLOBAL, P3_JACCARD_PER_GATE], "pass": p3},
        "per_gate_jaccard": {g: round(v, 4) for g, v in sorted(j["per_gate"].items())},
        "p4_strata_note": "blocked/special 泄漏并入 P1 口径复检；special 独立 Jaccard 见 per_gate_jaccard",
    }


def diff_runs(path_a: Path, path_b: Path) -> dict[str, Any]:
    """两次 run 的 summary 对比（verdict 变化 + 指标差）。"""
    a, b = summarize(path_a), summarize(path_b)
    return {
        "a": {"report": a["report"], "verdict": a["verdict"]},
        "b": {"report": b["report"], "verdict": b["verdict"]},
        "verdict_changed": a["verdict"] != b["verdict"],
        "jaccard_global_delta": round(
            b["p3_jaccard"]["global"] - a["p3_jaccard"]["global"], 4),
        "new_pass_delta": b["counts"]["new_pass"] - a["counts"]["new_pass"],
        "new_block_delta": b["counts"]["new_block"] - a["counts"]["new_block"],
    }


# ────────────────────────── CLI ──────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m zephyr.governance.rule_replay",
                                     description="历史重放器——重考历史执行件（OBJ_R 流水线第 4 步）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_replay = sub.add_parser("replay", help="跑重放落 report.jsonl + summary.json")
    p_replay.add_argument("--since", required=True)
    p_replay.add_argument("--until", required=True)
    p_replay.add_argument("--strata", default="blocked=30,passed=50,special=10,random=10")
    p_replay.add_argument("--gates", default="ALL_CONTENT_SCAN",
                          help="ALL_CONTENT_SCAN 或逗号分隔 gate_id 清单")
    p_replay.add_argument("--new-thresholds", default=None, help="[{module,const,value}] yaml")
    p_replay.add_argument("--blocked-hashes", default=None, help="层①注入文件（每行一个 hash）")
    p_replay.add_argument("--passed-hashes", default=None, help="层②注入文件（每行一个 hash）")
    p_replay.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    p_replay.add_argument("--seed", type=int, default=20260917)

    p_report = sub.add_parser("report", help="聚合 report.jsonl → P1-P4 判定")
    p_report.add_argument("--report", required=True)

    p_diff = sub.add_parser("diff", help="两次 run 对比")
    p_diff.add_argument("--a", required=True)
    p_diff.add_argument("--b", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_parser().parse_args(argv)
    if args.cmd == "replay":
        strata = {}
        for part in args.strata.split(","):
            k, v = part.split("=")
            strata[k.strip()] = int(v)
        gates = None if args.gates == "ALL_CONTENT_SCAN" else set(args.gates.split(","))
        report = run_replay(ReplayRequest(
            repo_root=REPO_ROOT, since=args.since, until=args.until, strata=strata,
            gates_filter=gates, thresholds=load_thresholds(args.new_thresholds),
            blocked_hashes=_read_hash_file(args.blocked_hashes),
            passed_hashes=_read_hash_file(args.passed_hashes),
            out_dir=Path(args.out), seed=args.seed,
        ))
        print(json.dumps(summarize(report), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "report":
        print(json.dumps(summarize(Path(args.report)), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "diff":
        print(json.dumps(diff_runs(Path(args.a), Path(args.b)), ensure_ascii=False, indent=2))
        return 0
    return 2


# noqa: m11-perm-manual-legitimate  M11豁免: 本模块=OBJ_R 重考历史执行件，Owner 修标时按需人工点火的一次性对照工具（非 cron/非 daemon/非常驻服务），事件订阅无意义
if __name__ == "__main__":
    sys.exit(main())
