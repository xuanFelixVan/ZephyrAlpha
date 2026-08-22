# [A_test] module_id: MOD-GOV_runtime_config | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_runtime_config
# [INVARIANTS] RuntimeConfig真源在zephyr.shared.contracts.runtime_types;本测试验证re-export+模型字段
# [MODIFY-GUARD] src/zephyr/runtime/runtime_config.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeConfig是Pydantic模型;DATA_DIR是Path
# [TESTS] tests/test_runtime_config.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.trading.runtime_config import (
    DATA_DIR,
    BrainResourceBudget,
    RuntimeConfig,
    check_brain_memory_budget,
    ensure_runtime_dirs,
)


class TestRuntimeConfigDefaults:
    def test_default_poll_interval(self):
        cfg = RuntimeConfig()
        assert cfg.poll_interval == 5.0

    def test_default_dashboard_enabled(self):
        cfg = RuntimeConfig()
        assert cfg.dashboard_enabled is True

    def test_default_auto_start_l2(self):
        cfg = RuntimeConfig()
        assert cfg.auto_start_l2 is True

    def test_default_auto_start_l3(self):
        cfg = RuntimeConfig()
        assert cfg.auto_start_l3 is False

    def test_default_enable_dream_cycle(self):
        cfg = RuntimeConfig()
        assert cfg.enable_dream_cycle is True

    def test_default_enable_stop_gate(self):
        cfg = RuntimeConfig()
        assert cfg.enable_stop_gate is True

    def test_default_max_parallel(self):
        cfg = RuntimeConfig()
        assert cfg.max_parallel_l1 == 1
        assert cfg.max_parallel_l2 == 3
        assert cfg.max_parallel_l3 == 2

    def test_default_working_hours(self):
        cfg = RuntimeConfig()
        assert cfg.working_hours_start == 9
        assert cfg.working_hours_end == 21

    def test_default_ollama_urls(self):
        cfg = RuntimeConfig()
        assert cfg.ollama_base_url == "http://localhost:11434"


class TestRuntimeConfigCustom:
    def test_custom_poll_interval(self):
        cfg = RuntimeConfig(poll_interval=10.0)
        assert cfg.poll_interval == 10.0

    def test_custom_dashboard_disabled(self):
        cfg = RuntimeConfig(dashboard_enabled=False)
        assert cfg.dashboard_enabled is False

    def test_custom_max_parallel(self):
        cfg = RuntimeConfig(max_parallel_l1=2, max_parallel_l2=5, max_parallel_l3=3)
        assert cfg.max_parallel_l1 == 2
        assert cfg.max_parallel_l2 == 5
        assert cfg.max_parallel_l3 == 3

    def test_custom_paths(self, tmp_path: Path):
        cfg = RuntimeConfig(
            night_shift_storage_path=tmp_path / "nsq.jsonl",
            audit_log_dir=tmp_path / "audit",
        )
        assert cfg.night_shift_storage_path == tmp_path / "nsq.jsonl"
        assert cfg.audit_log_dir == tmp_path / "audit"


class TestRuntimeConfigEnsureDirs:
    def test_ensure_dirs_creates_directories(self, tmp_path: Path):
        # 迁移后契约=模块级 ensure_runtime_dirs(config)（auto_runtime_core/lifecycle_manager 在消费），
        # RuntimeConfig 保持纯数据模型，不挂方法。
        cfg = RuntimeConfig(
            audit_log_dir=tmp_path / "audit",
            capability_card_dir=tmp_path / "cards",
            work_dag_dir=tmp_path / "dags",
            dream_archive_dir=tmp_path / "dream",
            feedback_proposal_dir=tmp_path / "feedback",
            health_snapshot_dir=tmp_path / "health",
            night_shift_storage_path=tmp_path / "nsq" / "queue.jsonl",
        )
        ensure_runtime_dirs(cfg)
        assert cfg.audit_log_dir.exists()
        assert cfg.capability_card_dir.exists()
        assert cfg.work_dag_dir.exists()
        assert cfg.dream_archive_dir.exists()
        assert cfg.feedback_proposal_dir.exists()
        assert cfg.health_snapshot_dir.exists()
        assert cfg.night_shift_storage_path.parent.exists()


class TestDataDir:
    def test_data_dir_is_path(self):
        assert isinstance(DATA_DIR, Path)

    def test_data_dir_points_to_data(self):
        assert DATA_DIR.name == "data"


class TestRuntimeConfigSerialization:
    def test_model_dump(self):
        cfg = RuntimeConfig()
        data = cfg.model_dump()
        assert "poll_interval" in data
        assert "dashboard_enabled" in data
        assert "max_parallel_l1" in data

    def test_model_dump_json_roundtrip(self):
        cfg = RuntimeConfig(poll_interval=7.5, dashboard_enabled=False)
        json_str = cfg.model_dump_json()
        restored = RuntimeConfig.model_validate_json(json_str)
        assert restored.poll_interval == 7.5
        assert restored.dashboard_enabled is False


class TestBrainResourceBudget:
    """大脑 RAM 预算（GAP-006 / D-INF035-08）+ 冷启动/恢复 SLA 参数（GAP-010 / D-INF035-09）。"""

    def test_defaults_match_blueprint_decisions(self):
        budget = BrainResourceBudget()
        assert budget.max_brain_memory_mb == 2048  # D-INF035-08：2GB
        assert budget.boot_timeout_ms == 10_000  # D-INF035-09：P99<10s
        assert budget.recovery_timeout_ms == 300_000  # RTO<5min

    def test_custom_budget(self):
        budget = BrainResourceBudget(max_brain_memory_mb=512)
        assert budget.max_brain_memory_mb == 512

    def test_within_budget_ok(self):
        result = check_brain_memory_budget(rss_reader=lambda: 1024.0)
        assert result.within_budget is True
        assert result.action == "ok"
        assert result.current_mb == 1024.0
        assert result.budget_mb == 2048

    def test_over_budget_runtime_triggers_degrade(self):
        """超限注入：mock RSS 超 2GB → 运行中触发降级。"""
        result = check_brain_memory_budget(rss_reader=lambda: 4096.0)
        assert result.within_budget is False
        assert result.action == "degrade"

    def test_over_budget_boot_phase_refuses_start(self):
        """超限注入：mock RSS 超 2GB → boot 阶段拒启动。"""
        result = check_brain_memory_budget(rss_reader=lambda: 4096.0, boot_phase=True)
        assert result.within_budget is False
        assert result.action == "refuse_start"

    def test_boundary_exactly_at_budget_ok(self):
        result = check_brain_memory_budget(rss_reader=lambda: 2048.0)
        assert result.within_budget is True
        assert result.action == "ok"

    def test_custom_budget_injection(self):
        result = check_brain_memory_budget(
            budget=BrainResourceBudget(max_brain_memory_mb=512),
            rss_reader=lambda: 600.0,
        )
        assert result.within_budget is False
        assert result.budget_mb == 512
