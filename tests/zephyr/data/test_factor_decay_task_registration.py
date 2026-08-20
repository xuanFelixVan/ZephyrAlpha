# [A_test] module_id: MOD-TEST-DECAY-TASK-REG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | 15 号 §6
# [MODULE] tests.zephyr.data.test_factor_decay_task_registration
# [DOMAIN] D_DATA
# [DEPENDENCIES] yaml; pathlib
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError->fail
# [TESTS] tests/zephyr/data/test_factor_decay_task_registration.py
# [TTL] permanent
# [ARCH-REF] #15_data_feature_layer_spec §6 衰减监控调度化（配置级登记）
# [ALGO_FLOW]
# 层: 输入
# - I1: src/zephyr/data/config/tasks.yaml + schedule.yaml（真源文件）
# 层: 算法
# - A1: 解析并定位 factor_decay_monitor_weekly 条目，校验登记字段与 disabled 留痕
# 层: 输出
# - O1: 登记完整性断言
"""test_factor_decay_task_registration.py — 衰减监控调度化登记（15 号 §6）配置契约测试。

锁定：tasks.yaml 含 factor_decay_monitor_weekly 条目（source=internal /
schedule=weekend_calibration / extra.disabled=true 留痕 runner 未绑定），
且 schedule 槽位在 schedule.yaml 真实存在（防挂到不存在的时段）。
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

_CONFIG = pathlib.Path(__file__).resolve().parents[3] / "src" / "zephyr" / "data" / "config"


def _load_tasks() -> list[dict]:
    doc = yaml.safe_load((_CONFIG / "tasks.yaml").read_text(encoding="utf-8"))
    return doc["tasks"]


class TestFactorDecayTaskRegistration:
    def test_entry_exists(self):
        tasks = _load_tasks()
        ids = [t["task_id"] for t in tasks]
        assert "factor_decay_monitor_weekly" in ids
        assert len(ids) == len(set(ids)), "task_id 重复"

    def test_entry_fields(self):
        task = next(t for t in _load_tasks() if t["task_id"] == "factor_decay_monitor_weekly")
        assert task["source"] == "internal"
        assert task["schedule"] == "weekend_calibration"
        assert task["incremental"] is False
        # 分析型任务无 CH 落表、无 capability（validator 不校验），disabled 留痕待 runner
        assert task.get("table") is None
        assert "capability" not in task
        assert task["extra"]["disabled"] is True
        assert "runner" in task["extra"]["disabled_reason"]

    def test_schedule_slot_exists(self):
        doc = yaml.safe_load((_CONFIG / "schedule.yaml").read_text(encoding="utf-8"))
        assert "weekend_calibration" in doc["schedules"]

    def test_no_capability_no_validation_block(self):
        """无 capability 字段 → capability_validator 规则1 不校验（登记不被启动校验阻断）。"""
        from zephyr.data.capability_validator import _check_capability_exists

        task = next(t for t in _load_tasks() if t["task_id"] == "factor_decay_monitor_weekly")
        assert _check_capability_exists(task, None, []) is True  # type: ignore[arg-type]
