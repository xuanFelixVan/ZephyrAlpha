# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.intelligence.switch_engine.shadow_runner
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc);
#                zephyr.gov_enforcement.rule_bridge.session_worktree (session_worktree_start,
#                双 worktree 租借默认实现，惰性导入)
# [CONSUMERS] zephyr.intelligence.switch_engine.switch_engine (T2 分歧率信号供方);
#             zephyr.ai_layer.switch_engine.revert_drill (演练环境核对)
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 影子不下真决策（第一不变量）：B 组一切产出只写对比区，report 恒带
#              consumer=comparator_only（仅供 L4 对比器消费，零生产决策路径）；
#              不互染三闸 fail-closed（DESIGN §②-A.1-4）——代码闸=双侧 worktree 物理隔离
#              且不得是主仓根；数据闸=corpus 只读快照+写出仅落注入 output_dir（进 data/
#              业务目录即拒）+PYTHONPATH 仅指向本 worktree src（禁 B import 主区代码）；
#              消费闸=产出仅落对比目录；corpus 冻结哈希不匹配即拒跑（改 corpus=新
#              switch_id）；触发=事件+周历窗口（调用方排班注册，本模块零 cron/Timer/sleep）；
#              计时用 monotonic（仅耗时测量），时间戳一律 now_utc
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-A.1/§④-S3
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 三闸任一违规/corpus 冻结哈希不匹配/manifest 缺失→ShadowGateError
#                  （fail-closed 拒跑，列出全部违规项）；单件 A/B 执行失败不炸整轮
#                  （记 diff_kind=error_a|error_b 继续，fail-open 于件级）；corpus 空目录
#                  →ShadowGateError（零样本对比无意义）
# [TESTS] tests/intelligence/switch_engine/test_shadow_runner.py（真 corpus+fake runner 全绿轮/
#         分歧率统计/三闸违规逐项拒跑（data 闸禁 data/ 路径）/corpus 冻结哈希篡改拒/
#         PYTHONPATH 隔离断言/报告落对比区+consumer 标记/单件 error 不炸）
"""shadow_runner — 模块级影子运行执行器（S3 施工件，全骨架最大新机制）。

双 worktree 各租一个（A=主区 HEAD 快照 champion、B=challenger 分支），同一冻结
corpus 分别喂 A/B（进程级隔离，PYTHONPATH 各指本侧 src），逐件记
{a_digest, b_digest, latency_a/b, diff_kind}，分歧率=非 identical 占比，报告只落
对比区。算力预算=配额池（定调 #10），越限由调用方发 T6 信号暂停——本模块不做配额裁决。
"""

from __future__ import annotations

from zephyr.shared.infra.process_pool import run_subprocess_hidden

import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

MANIFEST_NAME: Final[str] = "manifest.json"
CONSUMER_TAG: Final[str] = "comparator_only"
_FORBIDDEN_OUTPUT_ROOTS: Final[tuple[Path, ...]] = (REPO_ROOT / "data",)
_SHADOW_DRIVER: Final[str] = (
    "import importlib, json, sys;"
    "payload = json.load(open(sys.argv[1], encoding='utf-8'));"
    "mod_name, fn_name = sys.argv[2].split(':');"
    "result = getattr(importlib.import_module(mod_name), fn_name)(payload);"
    "print(json.dumps(result, ensure_ascii=False, sort_keys=True))"
)


class ShadowGateError(RuntimeError):
    """三闸违规/corpus 冻结违约（fail-closed 拒跑；detail 列全量违规）。"""


@dataclass(frozen=True)
class ShadowRunConfig:
    """一次影子运行的注入面（路径全部注入，测试零生产写）。"""

    switch_id: str
    champion_worktree: Path
    challenger_worktree: Path
    corpus_dir: Path
    output_dir: Path
    module_ref: str  # "<pkg.mod>:<func>"，A/B 同签名
    timeout_seconds: int = 120


@dataclass(frozen=True)
class SideOutcome:
    digest: str
    latency_ms: int
    error: str | None = None


@dataclass(frozen=True)
class ItemComparison:
    item: str
    a: SideOutcome
    b: SideOutcome
    diff_kind: str  # identical | semantic_diff | error_a | error_b


@dataclass(frozen=True)
class ShadowRunReport:
    switch_id: str
    total: int
    identical: int
    disagreement_rate: float
    comparisons: list[ItemComparison] = field(default_factory=list)
    consumer: str = CONSUMER_TAG
    corpus_hash: str = ""
    started_at: str = ""


CommandRunner = Callable[[Path, str, Path, Path], tuple[str, str]]
"""(worktree, module_ref, item_path, out_dir) -> (stdout, stderr)。注入缝：测试用 fake。"""


def write_corpus_manifest(
    corpus_dir: Path, *, seed: int, min_samples: int = 1
) -> dict[str, Any]:
    """冻结 corpus：清单+固定 seed+内容哈希落 manifest.json（开工前一次性调用）。"""
    items = _corpus_items(corpus_dir)
    if len(items) < min_samples:
        raise ShadowGateError(f"corpus 样本不足：{len(items)} < {min_samples}")
    manifest: dict[str, Any] = {
        "seed": seed,
        "size": len(items),
        "corpus_hash": _corpus_hash(items),
        "created_at": now_utc().isoformat(),
    }
    (corpus_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def default_command_runner(
    worktree: Path, module_ref: str, item_path: Path, out_dir: Path
) -> tuple[str, str]:
    """默认执行件：进程级隔离子进程，PYTHONPATH 仅指本 worktree src（禁 B import 主区）。"""
    side_dir = out_dir / _side_name(worktree)
    side_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(worktree / "src")  # 覆盖式：不继承主区路径
    completed = run_subprocess_hidden(  # trae_067 CREATE_NO_WINDOW（BARE-SUBPROCESS 治本 2026-09-24）
        [sys.executable, "-c", _SHADOW_DRIVER, str(item_path), module_ref],
        capture_output=True, text=True, cwd=str(worktree), env=env,
        timeout=180, check=False,
    )
    (side_dir / f"{item_path.stem}.out.json").write_text(
        completed.stdout, encoding="utf-8"
    )
    return completed.stdout, completed.stderr


class ShadowRunner:
    """影子跑编排：三闸校验→corpus 分发→对比统计→报告落对比区。"""

    def __init__(
        self,
        config: ShadowRunConfig,
        *,
        command_runner: CommandRunner | None = None,
        clock: Callable[[], Any] = now_utc,
    ) -> None:
        self._config = config
        self._run_side = command_runner or default_command_runner
        self._clock = clock

    def run(self) -> ShadowRunReport:
        self.verify_gates()
        items = _corpus_items(self._config.corpus_dir)
        comparisons: list[ItemComparison] = []
        for item in items:
            comparisons.append(self._compare_item(item))
        identical = sum(1 for c in comparisons if c.diff_kind == "identical")
        report = ShadowRunReport(
            switch_id=self._config.switch_id,
            total=len(comparisons),
            identical=identical,
            disagreement_rate=(
                round((len(comparisons) - identical) / len(comparisons), 6)
                if comparisons else 1.0
            ),
            comparisons=comparisons,
            corpus_hash=self._manifest()["corpus_hash"],
            started_at=self._clock().isoformat(),
        )
        self._write_report(report)
        return report

    def verify_gates(self) -> None:
        """不互染三闸+corpus 冻结预检（全部通过才许开跑）。"""
        violations: list[str] = []
        cfg = self._config
        for name, wt in (("A", cfg.champion_worktree), ("B", cfg.challenger_worktree)):
            if not wt.is_dir():
                violations.append(f"代码闸：worktree {name} 不存在 {wt}")
            elif wt.resolve() == REPO_ROOT.resolve():
                violations.append(f"代码闸：worktree {name} 不得是主仓根（隔离失效）")
        if cfg.champion_worktree.resolve() == cfg.challenger_worktree.resolve():
            violations.append("代码闸：A/B 双检出不得同目录")
        for forbidden in _FORBIDDEN_OUTPUT_ROOTS:
            if cfg.output_dir.resolve().is_relative_to(forbidden.resolve()):
                violations.append(f"数据闸：output_dir 禁入业务目录 {forbidden}")
        if not (cfg.corpus_dir / MANIFEST_NAME).is_file():
            violations.append(f"数据闸：corpus 未冻结（缺 {MANIFEST_NAME}，先 write_corpus_manifest）")
        if not _corpus_items(cfg.corpus_dir):
            violations.append("数据闸：corpus 为空（零样本对比无意义）")
        if violations:
            raise ShadowGateError("影子三闸预检失败：" + "；".join(violations))
        self._verify_corpus_frozen()

    def _verify_corpus_frozen(self) -> None:
        manifest = self._manifest()
        actual = _corpus_hash(_corpus_items(self._config.corpus_dir))
        if manifest.get("corpus_hash") != actual:
            raise ShadowGateError(
                f"corpus 冻结违约：manifest={manifest.get('corpus_hash')} 现值={actual}"
                "（改 corpus=新 switch_id，禁止在役改冻结集）"
            )

    def _manifest(self) -> dict[str, Any]:
        text = (self._config.corpus_dir / MANIFEST_NAME).read_text(encoding="utf-8")
        return json.loads(text)

    def _compare_item(self, item: Path) -> ItemComparison:
        cfg = self._config
        started = time.monotonic()  # 仅耗时测量，非时间戳（时间戳一律 now_utc）
        out_dir = cfg.output_dir
        try:
            stdout_a, stderr_a = self._run_side(cfg.champion_worktree, cfg.module_ref, item, out_dir)
            latency_a = int((time.monotonic() - started) * 1000)
            outcome_a = SideOutcome(_digest(stdout_a), latency_a, stderr_a or None)
        except Exception as exc:  # noqa: BLE001  件级失败不炸整轮（fail-open 于件级）
            outcome_a = SideOutcome("", 0, f"exception:{exc}")
        started_b = time.monotonic()
        try:
            stdout_b, stderr_b = self._run_side(cfg.challenger_worktree, cfg.module_ref, item, out_dir)
            latency_b = int((time.monotonic() - started_b) * 1000)
            outcome_b = SideOutcome(_digest(stdout_b), latency_b, stderr_b or None)
        except Exception as exc:  # noqa: BLE001
            outcome_b = SideOutcome("", 0, f"exception:{exc}")
        return ItemComparison(item.name, outcome_a, outcome_b, _diff_kind(outcome_a, outcome_b))

    def _write_report(self, report: ShadowRunReport) -> None:
        comparison_dir = self._config.output_dir / "comparison"
        comparison_dir.mkdir(parents=True, exist_ok=True)  # 产出只落对比区（消费闸）
        payload = {
            "switch_id": report.switch_id,
            "total": report.total,
            "identical": report.identical,
            "disagreement_rate": report.disagreement_rate,
            "consumer": report.consumer,
            "corpus_hash": report.corpus_hash,
            "started_at": report.started_at,
            "comparisons": [
                {
                    "item": c.item, "diff_kind": c.diff_kind,
                    "a_digest": c.a.digest, "b_digest": c.b.digest,
                    "latency_a_ms": c.a.latency_ms, "latency_b_ms": c.b.latency_ms,
                }
                for c in report.comparisons
            ],
        }
        (comparison_dir / f"{report.switch_id}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def lease_shadow_worktrees(switch_id: str) -> dict[str, Path]:
    """双 worktree 租借（默认实现，经 session_worktree 同款机制；pool 空则其内部直建）。

    仅在真实影子上岗时调用（事件触发，非 import 期）；测试一律注入 fake 路径。
    """
    from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_start

    sessions: dict[str, Path] = {}
    for side in ("a", "b"):
        result = session_worktree_start(session_id=f"st-shadow-{switch_id}-{side}")
        sessions[side] = Path(result["worktree_path"])
    return sessions


def _side_name(worktree: Path) -> str:
    return worktree.name


def _corpus_items(corpus_dir: Path) -> list[Path]:
    if not corpus_dir.is_dir():
        return []
    return sorted(p for p in corpus_dir.glob("*.json") if p.name != MANIFEST_NAME)


def _corpus_hash(items: list[Path]) -> str:
    sha = hashlib.sha256()
    for item in items:
        sha.update(item.name.encode("utf-8"))
        sha.update(hashlib.sha256(item.read_bytes()).hexdigest().encode("ascii"))
    return sha.hexdigest()


def _digest(stdout: str) -> str:
    return hashlib.sha256(stdout.encode("utf-8")).hexdigest()


def _diff_kind(a: SideOutcome, b: SideOutcome) -> str:
    if a.error and not b.error:
        return "error_a"
    if b.error and not a.error:
        return "error_b"
    if a.digest == b.digest:
        return "identical"
    return "semantic_diff"
