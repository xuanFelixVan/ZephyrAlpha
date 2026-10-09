# [A_test] module_id: MOD-GOV_boot_hooks_selfcheck | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.trading.test_boot_hooks_selfcheck
# [DOMAIN] D_INFRA_RUNTIME
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.trading.boot_hooks
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] —
# [TTL] task_bound
"""boot_hooks 技术栈自检单测（裁定#485 吸收批，细案=tech_stack_absorption_spec.md）.

覆盖：阻断级 ×3（DD-1/2/12）+ 警告级 ×3（DD-3/5/16）+ manifest 回退 + env 逃生门 +
幂等 + pytest 守卫 + 降级指标。全部 monkeypatch/tmp_path 隔离，禁写生产路径
（宪法 §9.6）：组件缺席用 sys.modules 注入 None / 属性补丁 / find_spec 替身模拟，
不真装卸依赖；manifest 用 tmp_path 假档，不碰 config/ 真源；kill switch 用 stub
替身，不污染真实单例。
"""

from __future__ import annotations

import importlib.util
import json
import logging
import sqlite3
import sys

import pytest
import yaml

import zephyr.trading.boot_hooks as boot_hooks

LOGGER_NAME = "zephyr.trading.boot_hooks"


@pytest.fixture(autouse=True)
def _hermetic_selfcheck_env(tmp_path, monkeypatch):
    """每用例：复位幂等标志 + 清环境开关 + manifest 指向 tmp 假档（不读不写 config/ 真源）."""
    monkeypatch.delenv("ZEPHYR_TECH_STACK_CHECK", raising=False)
    monkeypatch.delenv("ZEPHYR_KILL_SWITCH_STATE_PATH", raising=False)
    manifest = tmp_path / "tech_stack_manifest.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "manifest_version": "test",
                "decisions": [
                    {"dd_id": "DD-1", "component": "SLO 配置", "final_choice": "YAML + Pydantic v2"},
                    {"dd_id": "DD-2", "component": "审计存储", "final_choice": "SQLite + hash 链"},
                    {"dd_id": "DD-3", "component": "指标采样", "final_choice": "structlog + OTel SDK"},
                    {"dd_id": "DD-5", "component": "治理闭环", "final_choice": "自研 EMA + 阈值"},
                    {"dd_id": "DD-12", "component": "Kill Switch", "final_choice": "环境变量 + 文件信号"},
                    {"dd_id": "DD-16", "component": "语义缓存", "final_choice": "ChromaDB"},
                ],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(boot_hooks, "_TECH_STACK_MANIFEST_PATH", manifest)
    boot_hooks._tech_stack_check_done = False
    yield
    boot_hooks._tech_stack_check_done = False


def _make_find_spec_missing(monkeypatch: pytest.MonkeyPatch, *names: str) -> None:
    """让 find_spec 对指定顶级包返回 None（缺席模拟，不真装卸依赖）."""
    real_find_spec = importlib.util.find_spec

    def _fake(name: str, package: object = None):  # noqa: ANN001 — 对齐 find_spec 签名
        if name in names:
            return None
        return real_find_spec(name, package=package)

    monkeypatch.setattr(importlib.util, "find_spec", _fake)


def _stub_kill_switch(monkeypatch: pytest.MonkeyPatch, state_path) -> None:
    """用 stub 替身接管 get_kill_switch（state_path 模拟持久化/纯内存两种通道形态）."""
    import zephyr.security.access_control.kill_switch as ks_mod

    class _StubKillSwitch:
        def __init__(self, path):
            self.state_path = path

    monkeypatch.setattr(ks_mod, "get_kill_switch", lambda *args, **kwargs: _StubKillSwitch(state_path))


# ---------------------------------------------------------------------------
# 阻断级 ×3（DD-1/2/12）——失败必须 raise RuntimeError 且带组件名
# ---------------------------------------------------------------------------


def test_dd1_pydantic_wrong_version_blocks(monkeypatch):
    import pydantic

    monkeypatch.setattr(pydantic, "__version__", "1.10.13", raising=False)
    with pytest.raises(RuntimeError, match="DD-1"):
        boot_hooks._run_tech_stack_self_check()


def test_dd1_pydantic_missing_blocks(monkeypatch):
    # sys.modules 置 None = import pydantic 直接 ImportError（CPython 语义）
    monkeypatch.setitem(sys.modules, "pydantic", None)
    with pytest.raises(RuntimeError, match="DD-1"):
        boot_hooks._run_tech_stack_self_check()


def test_dd2_sqlite_probe_failure_blocks(monkeypatch):
    def _broken_connect(*args, **kwargs):
        raise RuntimeError("sqlite3 unavailable")

    monkeypatch.setattr(sqlite3, "connect", _broken_connect)
    with pytest.raises(RuntimeError, match="DD-2"):
        boot_hooks._run_tech_stack_self_check()


def test_dd12_kill_switch_unreachable_blocks(monkeypatch):
    import zephyr.security.access_control.kill_switch as ks_mod

    def _broken_get(*args, **kwargs):
        raise ImportError("kill_switch module broken")

    monkeypatch.setattr(ks_mod, "get_kill_switch", _broken_get)
    with pytest.raises(RuntimeError, match="DD-12"):
        boot_hooks._run_tech_stack_self_check()


def test_dd12_state_channel_corrupt_blocks(tmp_path, monkeypatch):
    bad = tmp_path / "ks_state.json"
    bad.write_text("{not-json", encoding="utf-8")
    _stub_kill_switch(monkeypatch, bad)
    with pytest.raises(RuntimeError, match="DD-12"):
        boot_hooks._run_tech_stack_self_check()


def test_dd12_state_channel_valid_engaged_not_blocks(tmp_path, monkeypatch, caplog):
    # engaged=true 是合法状态非通道失位——影子件可解析即通过，不做熔断态判读
    state = tmp_path / "ks_state.json"
    state.write_text(json.dumps({"version": 1, "engaged": True, "reason": "test"}), encoding="utf-8")
    _stub_kill_switch(monkeypatch, state)
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        boot_hooks._run_tech_stack_self_check()
    assert any("DD-12" in r.getMessage() for r in caplog.records)


# ---------------------------------------------------------------------------
# 警告级 ×3（DD-3/5/16）——只 warning 不阻断
# ---------------------------------------------------------------------------


def test_dd3_otel_missing_warns_not_blocks(monkeypatch, caplog):
    _make_find_spec_missing(monkeypatch, "opentelemetry")
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        boot_hooks._run_tech_stack_self_check()
    assert any("DD-3" in r.getMessage() for r in caplog.records)


def test_dd5_psutil_missing_warns_not_blocks(monkeypatch, caplog):
    _make_find_spec_missing(monkeypatch, "psutil")
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        boot_hooks._run_tech_stack_self_check()
    assert any("DD-5" in r.getMessage() for r in caplog.records)


def test_dd16_chromadb_missing_warns_not_blocks(monkeypatch, caplog):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)  # 关掉 pytest 守卫才探 DD-16
    _make_find_spec_missing(monkeypatch, "chromadb")
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        boot_hooks._run_tech_stack_self_check()
    assert any("DD-16" in r.getMessage() for r in caplog.records)


def test_dd16_skipped_under_pytest_guard(monkeypatch, caplog):
    # PYTEST_CURRENT_TEST 由 pytest 在岗注入（不删）——DD-16 应被守卫跳过不告警
    _make_find_spec_missing(monkeypatch, "chromadb")
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        boot_hooks._run_tech_stack_self_check()
    assert not any("DD-16" in r.getMessage() for r in caplog.records)


# ---------------------------------------------------------------------------
# env 逃生门 / manifest 回退 / 幂等 / 降级指标
# ---------------------------------------------------------------------------


def test_env_zero_disables_entire_check(monkeypatch):
    monkeypatch.setenv("ZEPHYR_TECH_STACK_CHECK", "0")
    monkeypatch.setitem(sys.modules, "pydantic", None)  # 组件坏也不查
    boot_hooks._run_tech_stack_self_check()  # 不 raise
    assert boot_hooks._tech_stack_check_done is True


def test_env_warn_demotes_block_to_warning(monkeypatch, caplog):
    import pydantic

    monkeypatch.setenv("ZEPHYR_TECH_STACK_CHECK", "warn")
    monkeypatch.setattr(pydantic, "__version__", "1.10.13", raising=False)
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        boot_hooks._run_tech_stack_self_check()  # BLOCK 降级为警告，不 raise
    assert any("DD-1" in r.getMessage() for r in caplog.records)


def test_manifest_missing_falls_back_with_warning(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(boot_hooks, "_TECH_STACK_MANIFEST_PATH", tmp_path / "absent.yaml")
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        boot_hooks._run_tech_stack_self_check()  # 回退后检查照常（pydantic v2 在场→不阻断）
    assert any("回退" in r.getMessage() for r in caplog.records)


def test_manifest_corrupt_falls_back_with_warning(tmp_path, monkeypatch, caplog):
    bad = tmp_path / "corrupt_manifest.yaml"
    bad.write_text("{{{{not yaml", encoding="utf-8")
    monkeypatch.setattr(boot_hooks, "_TECH_STACK_MANIFEST_PATH", bad)
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        boot_hooks._run_tech_stack_self_check()
    assert any("回退" in r.getMessage() for r in caplog.records)


def test_all_present_happy_path(monkeypatch, caplog):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)  # 连 DD-16 也真实探测
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        boot_hooks._run_tech_stack_self_check()
    assert boot_hooks._tech_stack_check_done is True
    assert any("tech_stack 自检完成" in r.getMessage() for r in caplog.records)


def test_idempotent_second_call_skips_recheck(monkeypatch):
    boot_hooks._run_tech_stack_self_check()
    monkeypatch.setitem(sys.modules, "pydantic", None)  # 二次调用前把环境搞坏
    boot_hooks._run_tech_stack_self_check()  # 幂等跳过→不 raise


def test_warn_emits_degraded_metric(monkeypatch):
    import zephyr.shared.observability.metrics as metrics_mod

    calls: list[tuple[str, dict | None]] = []

    class _FakeRegistry:
        def observe(self, name, value, labels=None):
            calls.append((name, labels))

    monkeypatch.setattr(metrics_mod, "MetricsRegistry", _FakeRegistry)
    _make_find_spec_missing(monkeypatch, "psutil")
    boot_hooks._run_tech_stack_self_check()
    degraded = [labels for name, labels in calls if name == "tech_stack.degraded"]
    assert degraded and any(labels and "DD-5" in labels.get("component", "") for labels in degraded)
