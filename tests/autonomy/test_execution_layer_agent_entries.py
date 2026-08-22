# [BLUEPRINT] MOD-EXE-AGENTS | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §4-S0.6
# [MODULE] tests.autonomy.test_execution_layer_agent_entries
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] pytest ; zephyr.autonomy_core.agents
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 四入口全部用真源注册表/真 gate 跑样例；落盘断言只认 tmp runtime_dir（不污染仓根 .runtime）
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4 Phase 0 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 无（测试件）
# [TESTS] 自测
# [A_test] module_id=MOD-EXE-AGENTS | layer=test | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""四类 Agent 薄入口测试（14号文 §4 Phase 0，S0.2~S0.6 验收口径）.

被测对象：src/zephyr/autonomy_core/agents/{governance,business,algorithm,
self_iteration}_agent_entry.py（角色化薄入口，纯组装，产出 100% 落盘 human_gated）。

覆盖：
- S0.2 治理：gate 检查工单端到端（输入工单→gate verdict→审计落盘）；
- S0.3 业务：注册状态查询 + 因子候选评估工单两样例；产出标"仅建议"；
  AST 断言零交易执行模块 import（不碰下单路径）；
- S0.4 算法：登记先于执行（steps 顺序）；显存 >=90% 拒启动（含边界值）；
- S0.5 迭代：只读证据→human_gated 建议工单；白名单外证据跳过；无代码自改路径；
- S0.6 纪律：四入口模块均 <200 行；产出信封 100% human_gated。
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from zephyr.autonomy_core.agents import (
    algorithm_agent_entry,
    business_agent_entry,
    governance_agent_entry,
    self_iteration_agent_entry,
)
from zephyr.experiment_tracking.config import ExperimentTrackingConfig

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / "src" / "zephyr" / "autonomy_core" / "agents"

ENTRY_FILES = [
    "governance_agent_entry.py",
    "business_agent_entry.py",
    "algorithm_agent_entry.py",
    "self_iteration_agent_entry.py",
]

# 各入口禁止 import 的交易执行/自改路径前缀（AST 断言，S0.3/S0.5 INVARIANTS）
FORBIDDEN_IMPORTS = {
    "governance_agent_entry.py": ("zephyr.ex_core", "zephyr.ex_sor", "zephyr.trading"),
    "business_agent_entry.py": ("zephyr.ex_core", "zephyr.ex_sor", "zephyr.trading"),
    # 算法入口合法复用 zephyr.trading.gpu_monitor（既有显存采集件，非执行路径）
    "algorithm_agent_entry.py": ("zephyr.ex_core", "zephyr.ex_sor"),
    "self_iteration_agent_entry.py": (
        "zephyr.ex_core",
        "zephyr.ex_sor",
        "zephyr.trading",
        "zephyr.feedback_loop.evolution.self_modification",
        "zephyr.feedback_loop.forensic.self_modification",
    ),
}
# 下单调用词面禁令（Grep 口径，S0.3 验收③）
FORBIDDEN_TOKENS = ("miniqmt", "miniQMT", "place_order", "OrderManager", "order_manager")


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _module_source(filename: str) -> str:
    return (AGENTS_DIR / filename).read_text(encoding="utf-8")


def _imported_modules(filename: str) -> list[str]:
    tree = ast.parse(_module_source(filename))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


class TestGovernanceEntry:
    """S0.2：治理 Agent 入口——gate 检查工单端到端."""

    def test_gate_check_ticket_end_to_end(self, tmp_path):
        ticket = {
            "ticket_id": "gov-sample-001",
            "targets": [
                "src/zephyr/factor/alpha_momentum.py",  # ai_modifiable → allow
                "src/zephyr/data/market_connect.py",  # human_gated → escalate
                "src/zephyr/risk/risk_engine.py",  # immutable_core → block
            ],
            "session_id": "sess-test",
        }
        report = governance_agent_entry.run_gate_check_ticket(
            ticket, runtime_dir=tmp_path, repo_root=REPO_ROOT
        )
        assert report["overall"] == "blocked"
        assert report["decision_counts"] == {"allow": 1, "escalate": 1, "block": 1}

        run_dir = tmp_path / "agent_runs" / "governance"
        runs = [p for p in run_dir.iterdir() if p.is_dir()]
        assert len(runs) == 1
        verdicts = json.loads((runs[0] / "gate_verdicts.json").read_text(encoding="utf-8"))
        assert verdicts["ai_autonomy"] == "human_gated"
        assert verdicts["triggered_by"] == "human_manual"
        assert len(verdicts["verdicts"]) == 3
        run_record = json.loads((runs[0] / "run.json").read_text(encoding="utf-8"))
        assert run_record["status"] == "blocked"
        assert run_record["ai_autonomy"] == "human_gated"
        # 审计落盘：入口 audit.jsonl 一行 + 既有 gate 自身审计留痕
        assert len(_read_jsonl(run_dir / "audit.jsonl")) == 1
        gate_audit = tmp_path / "audit" / "autonomy_boundary_gate.jsonl"
        assert len(_read_jsonl(gate_audit)) == 3

    def test_ticket_validation(self, tmp_path):
        with pytest.raises(ValueError, match="ticket_id|targets"):
            governance_agent_entry.run_gate_check_ticket(
                {"ticket_id": "", "targets": []}, runtime_dir=tmp_path, repo_root=REPO_ROOT
            )


class TestBusinessEntry:
    """S0.3：业务 Agent 入口——两样例 + 仅建议 + 零下单断言."""

    def test_registration_status_query_real_registry(self, tmp_path):
        report = business_agent_entry.query_registration_status(
            {"ticket_id": "biz-status-001", "factor_id": "FCT-INTRADAY-015"},
            runtime_dir=tmp_path,
            repo_root=REPO_ROOT,
        )
        factor = report["registries"]["factor"]
        assert factor["total_entries"] > 0
        assert factor["status_counts"].get("candidate", 0) > 0
        assert factor["entry_found"] is True
        assert factor["entry"]["factor_id"] == "FCT-INTRADAY-015"
        strategy = report["registries"]["strategy"]
        assert strategy["total_entries"] > 0
        assert report["advice_only"] is True
        assert "仅建议" in report["disclaimer"]

        run_dir = next(
            p for p in (tmp_path / "agent_runs" / "business").iterdir() if p.is_dir()
        )
        landed = json.loads((run_dir / "registration_status.json").read_text(encoding="utf-8"))
        assert landed["ai_autonomy"] == "human_gated"

    def test_factor_candidate_evaluation_ticket(self, tmp_path):
        report = business_agent_entry.draft_factor_candidate_evaluation(
            {"ticket_id": "biz-eval-001", "limit": 2},
            runtime_dir=tmp_path,
            repo_root=REPO_ROOT,
        )
        assert report["status"] == "completed"
        assert report["advice_only"] is True
        assert len(report["candidates"]) == 2
        for candidate in report["candidates"]:
            assert candidate["human_gated"] is True
            assert "仅建议" in candidate["suggestion_zh"]
        assert report["candidate_pool_size"] >= 2

    def test_factor_candidate_evaluation_by_ids(self, tmp_path):
        report = business_agent_entry.draft_factor_candidate_evaluation(
            {"ticket_id": "biz-eval-002", "factor_ids": ["FCT-INTRADAY-015"]},
            runtime_dir=tmp_path,
            repo_root=REPO_ROOT,
        )
        assert [c["factor_id"] for c in report["candidates"]] == ["FCT-INTRADAY-015"]

    def test_no_trading_execution_path(self):
        """S0.3 验收③：零交易执行模块 import + 无下单词面（Grep 口径）."""
        for name in _imported_modules("business_agent_entry.py"):
            assert not name.startswith(FORBIDDEN_IMPORTS["business_agent_entry.py"]), name
        source = _module_source("business_agent_entry.py")
        for token in FORBIDDEN_TOKENS:
            assert token not in source


class TestAlgorithmEntry:
    """S0.4：算法 Agent 入口——登记先于执行 + 显存 <90% 守卫."""

    @staticmethod
    def _seed_run(fallback_dir: Path) -> None:
        run_dir = fallback_dir / "c1-validation" / "run-demo-001"
        run_dir.mkdir(parents=True)
        meta = {
            "run_id": "run-demo-001",
            "component": "c1-validation",
            "run_name": "demo-eval",
            "status": "FINISHED",
            "start_time": "2026-08-22T10:00:00",
            "end_time": "2026-08-22T10:05:00",
            "metrics": {"passed": 1.0, "sharpe": 1.5},
            "tags": {"source": "w4_14_sample"},
            "artifacts": [],
        }
        (run_dir / "run_meta.json").write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )

    def _ticket(self) -> dict:
        return {
            "ticket_id": "algo-sample-001",
            "experiment_type": "model_evaluation",
            "target_id": "EXP-BACKTEST-DEMO",
            "run_id": "run-demo-001",
            "component": "c1-validation",
        }

    def test_registration_before_execution_and_eval(self, tmp_path):
        fallback = tmp_path / "fallback"
        self._seed_run(fallback)
        report = algorithm_agent_entry.run_algorithm_experiment_ticket(
            self._ticket(),
            runtime_dir=tmp_path / "rt",
            repo_root=REPO_ROOT,
            gpu_stats_provider=lambda: {
                "available": True, "memory_used_gb": 6.0, "memory_total_gb": 24.0,
            },
            tracking_config=ExperimentTrackingConfig(fallback_dir=fallback),
        )
        # 验收②：登记先于执行（registered 必在 evaluated 前）
        assert report["status"] == "completed"
        assert report["steps"] == ["registered", "passed", "evaluated"]
        assert report["evaluation"]["metrics"]["sharpe"] == 1.5
        assert report["evaluation"]["passed"] is True

        run_dir = next(
            p for p in (tmp_path / "rt" / "agent_runs" / "algorithm").iterdir() if p.is_dir()
        )
        registration = json.loads(
            (run_dir / "experiment_registration.pending.json").read_text(encoding="utf-8")
        )
        assert registration["status"] == "pending_registration"  # 本体交统筹，不落注册表
        assert (run_dir / "vram_guard.json").exists()
        assert (run_dir / "evaluation_report.json").exists()

    def test_vram_guard_refuses_over_90(self, tmp_path):
        report = algorithm_agent_entry.run_algorithm_experiment_ticket(
            self._ticket(),
            runtime_dir=tmp_path / "rt",
            repo_root=REPO_ROOT,
            gpu_stats_provider=lambda: {
                "available": True, "memory_used_gb": 22.5, "memory_total_gb": 24.0,
            },
            tracking_config=ExperimentTrackingConfig(fallback_dir=tmp_path / "fb"),
        )
        assert report["status"] == "refused_vram"
        assert report["steps"] == ["registered", "refused_vram"]  # 未进入执行步
        run_dir = next(
            p for p in (tmp_path / "rt" / "agent_runs" / "algorithm").iterdir() if p.is_dir()
        )
        assert (run_dir / "experiment_registration.pending.json").exists()
        assert not (run_dir / "evaluation_report.json").exists()

    def test_vram_guard_boundary_90_percent(self, tmp_path):
        report = algorithm_agent_entry.run_algorithm_experiment_ticket(
            self._ticket(),
            runtime_dir=tmp_path / "rt",
            repo_root=REPO_ROOT,
            gpu_stats_provider=lambda: {
                "available": True, "memory_used_gb": 21.6, "memory_total_gb": 24.0,
            },
            tracking_config=ExperimentTrackingConfig(fallback_dir=tmp_path / "fb"),
        )
        assert report["status"] == "refused_vram"  # 0.90 边界值同样拒启动（>=）

    def test_gpu_unavailable_degrades_open(self, tmp_path):
        fallback = tmp_path / "fallback"
        self._seed_run(fallback)
        report = algorithm_agent_entry.run_algorithm_experiment_ticket(
            self._ticket(),
            runtime_dir=tmp_path / "rt",
            repo_root=REPO_ROOT,
            gpu_stats_provider=lambda: {"available": False},
            tracking_config=ExperimentTrackingConfig(fallback_dir=fallback),
        )
        assert report["status"] == "completed"
        assert report["steps"][1] == "not_available"  # 降级如实留痕


class TestSelfIterationEntry:
    """S0.5：自我迭代 Agent 入口——只读证据→human_gated 建议工单."""

    def _seed_evidence(self, tmp_path: Path) -> str:
        evidence_dir = tmp_path / "agent_runs" / "governance" / "run-x"
        evidence_dir.mkdir(parents=True)
        payload = {
            "verdicts": [{"decision": "block"}, {"decision": "escalate"}],
            "kind": "model_evaluation_report",
            "passed": False,
        }
        path = evidence_dir / "gate_verdicts.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def test_review_consumes_evidence_produces_human_gated_ticket(self, tmp_path):
        evidence = self._seed_evidence(tmp_path)
        report = self_iteration_agent_entry.run_iteration_review(
            {"ticket_id": "iter-sample-001", "evidence_paths": [evidence]},
            runtime_dir=tmp_path,
            repo_root=REPO_ROOT,
        )
        assert report["evidence_consumed"] == 1
        assert report["summary"]["gate_decision_counts"] == {"block": 1, "escalate": 1}
        assert report["summary"]["experiments"]["failed"] == 1
        assert len(report["suggestions"]) >= 2
        for suggestion in report["suggestions"]:
            assert suggestion["human_gated"] is True
            assert suggestion["advice_only"] is True

        run_dir = next(
            p
            for p in (tmp_path / "agent_runs" / "self_iteration").iterdir()
            if p.is_dir()
        )
        landed = json.loads(
            (run_dir / "iteration_suggestion.json").read_text(encoding="utf-8")
        )
        assert landed["ai_autonomy"] == "human_gated"

    def test_evidence_whitelist_skips_outside_files(self, tmp_path):
        report = self_iteration_agent_entry.run_iteration_review(
            {
                "ticket_id": "iter-sample-002",
                "evidence_paths": ["pyproject.toml", "src/zephyr/factor/value_factor.py"],
            },
            runtime_dir=tmp_path,
            repo_root=REPO_ROOT,
        )
        assert report["evidence_consumed"] == 0
        assert len(report["skipped_evidence"]) == 2  # 白名单（.runtime/logs/docs）外一律跳过

    def test_no_code_self_modification_path(self):
        """S0.5 验收③：零执行/自改模块 import（AST 断言）."""
        for name in _imported_modules("self_iteration_agent_entry.py"):
            assert not name.startswith(
                FORBIDDEN_IMPORTS["self_iteration_agent_entry.py"]
            ), name
        source = _module_source("self_iteration_agent_entry.py")
        for token in FORBIDDEN_TOKENS:
            assert token not in source


class TestThinEntryDiscipline:
    """S0.6：薄入口纪律——行数上限 + 产出信封 human_gated 全覆盖."""

    def test_entry_modules_under_200_lines(self):
        for filename in ENTRY_FILES:
            line_count = len(_module_source(filename).splitlines())
            assert line_count < 200, f"{filename} {line_count} 行，超 200 行薄入口上限"

    def test_all_entries_forbidden_imports(self):
        for filename, prefixes in FORBIDDEN_IMPORTS.items():
            for name in _imported_modules(filename):
                assert not name.startswith(prefixes), f"{filename} 越权 import {name}"

    def test_envelope_marks(self, tmp_path):
        """四入口产出信封统一 human_gated（抽治理/迭代两路复核）."""
        governance_agent_entry.run_gate_check_ticket(
            {"ticket_id": "env-001", "targets": ["src/zephyr/factor/alpha_momentum.py"]},
            runtime_dir=tmp_path,
            repo_root=REPO_ROOT,
        )
        for path in (tmp_path / "agent_runs").rglob("*.json"):
            record = json.loads(path.read_text(encoding="utf-8"))
            assert record.get("ai_autonomy") == "human_gated", path
            assert record.get("triggered_by") == "human_manual", path
