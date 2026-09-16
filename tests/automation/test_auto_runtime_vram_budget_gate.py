# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §6.2
# [MODULE] tests.automation.test_auto_runtime_vram_budget_gate
# [DOMAIN] D_INFRA_RUNTIME
# [INVARIANTS] VRAM 预算门数值只来自 config/gguf_vram_budget.yaml（代码零副本）；表不可读=降级放行不炸链路
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即"代码抄数/降级语义破功"证据
# [TESTS] self
# [TTL] permanent
"""AutoRuntimeCore VRAM 预算门读表验收单测（排班表 v2 §2.3 C-2 治本）。

背景：M4 治理战役给 `_OllamaProcessManager.ensure_running` 加了"显存超硬上限拒绝
再孵 ollama"的门禁，但把上限 21.6 抄进了代码——违反 config/gguf_vram_budget.yaml
自订纪律（"单真源，禁止另造口径"）与 RULE-SSOT。本批改为复用既有 loader
（zephyr.intelligence.gguf_model_manager.load_budget_table，MOD-INF-060）。

覆盖：
- `_vram_hard_cap_gb()` 读表：tmp 注入 fixture YAML 改值即改线（证明无代码副本）
- 生产表可用（loader 未跑偏），且值>0
- 表缺席/结构非法 → None（fail-safe 降级，loud warning，不抛）
- ensure_running 三态：超线拒孵（不碰 incubator）/ 未超线放行 / 表不可读放行
- 回归锁：nvidia-smi 缺席（FileNotFoundError）必须走 fail-safe 放行，
  不得因 except 子句里未绑定的 `subprocess` 名字反抛 NameError 炸穿启动链路
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import zephyr.trading.auto_runtime_core as arc  # noqa: E402


def _budget_yaml(hard_cap: float) -> str:
    """最小合法显存预算表（load_budget_table 三段齐全，仅数值与本测试相关）。"""
    import yaml

    return yaml.safe_dump(
        {
            "hard_cap_gb": hard_cap,
            "period_quotas": {"night": {"window": ["00:00", "01:00"], "inference_quota_gb": 1.0}},
            "models": [{"name": "tiny:1b", "vram_gb": 0.1}],
        },
        allow_unicode=True,
    )


def _repo_with_budget(root: Path, hard_cap: float | None, raw_text: str | None = None) -> Path:
    """在临时仓根写 config/gguf_vram_budget.yaml（raw_text 用于坏 YAML 场景）。"""
    cfg = root / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    text = raw_text if raw_text is not None else _budget_yaml(hard_cap)
    (cfg / "gguf_vram_budget.yaml").write_text(text, encoding="utf-8")
    return root


class _CoreStub:
    """ensure_running 用到的 core 面：_ollama_proc 落点 + 存活探测（永远存活）。"""

    def __init__(self) -> None:
        self._ollama_proc = None

    def _ollama_alive(self, timeout_s: float = 2.0) -> bool:  # noqa: ARG002
        return True


class _IncubatorStub:
    def __init__(self) -> None:
        self.calls: list = []

    def spawn(self, cmd, **kw):  # noqa: ANN001, ANN201 — 与 ProcessIncubator.spawn 同形
        self.calls.append((list(cmd), kw))
        return "FAKE_PROC"


def _patch_nvidia_smi(monkeypatch: pytest.MonkeyPatch, used_mib: int | None = None, boom: Exception | None = None):
    """替换 subprocess.run（ensure_running 内 lazy import 的是同一模块对象）。"""

    def _run(cmd, **kw):  # noqa: ARG001
        if boom is not None:
            raise boom
        stdout = "" if used_mib is None else f"{used_mib}\n"
        return subprocess.CompletedProcess(list(cmd), 0, stdout=stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", _run)


@pytest.fixture()
def spawn_env(monkeypatch: pytest.MonkeyPatch):
    """孵化面全桩：ollama 路径解析 / get_incubator / 轮询 sleep。"""
    inc = _IncubatorStub()
    monkeypatch.setattr(arc.shutil, "which", lambda _name: "ollama")
    monkeypatch.setattr(arc, "get_incubator", lambda: inc)
    monkeypatch.setattr(arc.time, "sleep", lambda _s: None)
    return inc


# ── 读表器 ───────────────────────────────────────────────────────────────────


def test_hard_cap_comes_from_yaml_not_code(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """改表即改线（13.5 这种生产里不存在的值被读到=代码零副本的铁证）。"""
    monkeypatch.setattr(arc, "REPO_ROOT", _repo_with_budget(tmp_path / "a", 13.5))
    assert arc._vram_hard_cap_gb() == pytest.approx(13.5)

    monkeypatch.setattr(arc, "REPO_ROOT", _repo_with_budget(tmp_path / "b", 30.0))
    assert arc._vram_hard_cap_gb() == pytest.approx(30.0)


def test_production_table_is_readable():
    """生产表可读且为正数（loader 路径/结构未跑偏）。"""
    cap = arc._vram_hard_cap_gb()
    assert cap is not None and cap > 0


@pytest.mark.parametrize("raw_text", ["hard_cap_gb: not-a-number\n", "hcap: 1\n", "\tbad: ["])
def test_unreadable_table_degrades_to_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raw_text: str):
    """结构非法/缺 hard_cap/坏 YAML → None + 不抛（fail-safe 降级）。"""
    monkeypatch.setattr(arc, "REPO_ROOT", _repo_with_budget(tmp_path / f"bad{abs(hash(raw_text))}", None, raw_text))
    assert arc._vram_hard_cap_gb() is None


def test_missing_table_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(arc, "REPO_ROOT", tmp_path / "nonexistent_repo_root")
    assert arc._vram_hard_cap_gb() is None


# ── ensure_running 三态 ──────────────────────────────────────────────────────


def test_refuses_spawn_above_table_cap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, spawn_env):
    """超表线 → 拒绝孵化（返回 False，incubator 一次都不被调用）。"""
    monkeypatch.setattr(arc, "REPO_ROOT", _repo_with_budget(tmp_path / "r1", 20.0))
    _patch_nvidia_smi(monkeypatch, used_mib=int(21.5 * 1024))
    assert arc._OllamaProcessManager.ensure_running(_CoreStub()) is False
    assert spawn_env.calls == []


def test_allows_spawn_below_table_cap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, spawn_env):
    """未超表线 → 正常孵化。"""
    monkeypatch.setattr(arc, "REPO_ROOT", _repo_with_budget(tmp_path / "r2", 20.0))
    _patch_nvidia_smi(monkeypatch, used_mib=int(19.0 * 1024))
    assert arc._OllamaProcessManager.ensure_running(_CoreStub()) is True
    assert len(spawn_env.calls) == 1


def test_cap_boundary_equal_value_allows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, spawn_env):
    """边界=严格大于才拒（== 硬上限放行，与改造前 `>` 语义一致）。"""
    monkeypatch.setattr(arc, "REPO_ROOT", _repo_with_budget(tmp_path / "r3", 24.0))
    _patch_nvidia_smi(monkeypatch, used_mib=int(24.0 * 1024))
    assert arc._OllamaProcessManager.ensure_running(_CoreStub()) is True
    assert len(spawn_env.calls) == 1


def test_gate_skipped_when_table_unreadable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, spawn_env):
    """表不可读 → 门禁降级放行（即便显存打满也不炸启动链路）。"""
    monkeypatch.setattr(arc, "REPO_ROOT", tmp_path / "no_such_config")
    _patch_nvidia_smi(monkeypatch, used_mib=int(23.0 * 1024))
    assert arc._OllamaProcessManager.ensure_running(_CoreStub()) is True
    assert len(spawn_env.calls) == 1


def test_no_nvidia_smi_failsafe_no_nameerror(monkeypatch: pytest.MonkeyPatch, spawn_env):
    """回归锁：nvidia-smi 缺席必须放行，不得因 except 子句未绑定名反抛 NameError。"""
    _patch_nvidia_smi(monkeypatch, boom=FileNotFoundError("nvidia-smi not found"))
    assert arc._OllamaProcessManager.ensure_running(_CoreStub()) is True
    assert len(spawn_env.calls) == 1


def test_smi_timeout_failsafe(monkeypatch: pytest.MonkeyPatch, spawn_env):
    """nvidia-smi 超时=放行（原语义）。"""
    _patch_nvidia_smi(monkeypatch, boom=subprocess.TimeoutExpired(cmd="nvidia-smi", timeout=8))
    assert arc._OllamaProcessManager.ensure_running(_CoreStub()) is True
    assert len(spawn_env.calls) == 1
