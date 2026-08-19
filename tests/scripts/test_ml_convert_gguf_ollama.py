# [BLUEPRINT] MOD-NLP-PIPELINE | 13_regime_phase3_engineering_plan.md | §Phase 6
# [TTL] permanent
"""test_ml_convert_gguf_ollama.py — GGUF 回灌 Ollama 转换脚本单元测试（Phase 6）。

覆盖（全程不执行真实转换——只验证命令计划构造与 dry-run 路径）：
  1. build_plan —— 四步命令组装/路径派生/量化类型参数化
  2. render_modelfile —— FROM 指向量化 GGUF
  3. run_plan dry-run —— 打印计划返回 0，不触碰文件系统
  4. run_plan 执行 —— 子进程失败返回 1（mock subprocess.run）
  5. main 守卫 —— adapter 缺失 exit 1；执行模式缺 llama.cpp exit 1
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "convert_gguf_ollama", _ROOT / "scripts" / "ml" / "convert_gguf_ollama.py",
)
cgo = importlib.util.module_from_spec(_spec)
sys.modules["convert_gguf_ollama"] = cgo  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(cgo)


def _plan(tmp_path: pathlib.Path, qtype: str = "Q4_K_M"):
    return cgo.build_plan(
        adapter_dir=tmp_path / "adapter",
        llama_cpp_dir=tmp_path / "llama.cpp",
        output_dir=tmp_path / "out",
        model_name="qwen25-7b-sft-v1",
        qtype=qtype,
    )


# ============ 1. build_plan ============


class TestBuildPlan:
    def test_four_steps_assembled(self, tmp_path):
        plan = _plan(tmp_path)
        steps = dict(plan.steps())
        assert set(steps) == {"merge", "convert", "quantize", "ollama_create"}

    def test_merge_cmd_invokes_peft_snippet(self, tmp_path):
        plan = _plan(tmp_path)
        cmd = plan.merge_cmd
        assert "-c" in cmd
        assert any("merge_and_unload" in c for c in cmd)
        assert str(tmp_path / "adapter") in cmd

    def test_convert_cmd_points_llama_script(self, tmp_path):
        plan = _plan(tmp_path)
        cmd = plan.convert_cmd
        assert str(tmp_path / "llama.cpp" / "convert_hf_to_gguf.py") in cmd
        assert "--outtype" in cmd and "f16" in cmd
        assert plan.gguf_f16.name == "qwen25-7b-sft-v1-f16.gguf"

    def test_quantize_cmd_type_parametrized(self, tmp_path):
        plan = _plan(tmp_path, qtype="Q8_0")
        assert plan.quantize_cmd[-1] == "Q8_0"
        assert plan.gguf_quant.name == "qwen25-7b-sft-v1-Q8_0.gguf"

    def test_ollama_create_cmd(self, tmp_path):
        plan = _plan(tmp_path)
        cmd = plan.ollama_cmd
        assert cmd[:3] == ["ollama", "create", "qwen25-7b-sft-v1"]
        assert "-f" in cmd


# ============ 2. render_modelfile ============


class TestRenderModelfile:
    def test_from_points_to_quantized_gguf(self, tmp_path):
        text = cgo.render_modelfile(tmp_path / "model-Q4_K_M.gguf", "m1")
        assert text.startswith("FROM ")
        assert "model-Q4_K_M.gguf" in text

    def test_temperature_zero_pinned(self, tmp_path):
        # 与 nlp_inference InferConfig temperature=0.0 口径一致
        assert "temperature 0.0" in cgo.render_modelfile(tmp_path / "m.gguf", "m1")


# ============ 3. run_plan dry-run ============


class TestRunPlanDryRun:
    def test_dry_run_prints_and_returns_zero(self, tmp_path, capsys):
        plan = _plan(tmp_path)
        rc = cgo.run_plan(plan, dry_run=True)
        assert rc == 0
        out = capsys.readouterr().out
        assert "dry-run" in out
        assert "merge" in out and "quantize" in out
        assert "ollama" in out

    def test_dry_run_writes_nothing(self, tmp_path):
        plan = _plan(tmp_path)
        cgo.run_plan(plan, dry_run=True)
        assert not plan.modelfile_path.exists()
        assert not (tmp_path / "out").exists()


# ============ 4. run_plan 执行（mock 子进程）============


class _FakeProc:
    def __init__(self, returncode: int) -> None:
        self.returncode = returncode


class TestRunPlanExec:
    def test_writes_modelfile_and_runs_all_steps(self, tmp_path, monkeypatch):
        calls: list[list[str]] = []
        monkeypatch.setattr(
            cgo.subprocess, "run",
            lambda cmd, check=False: (calls.append(list(cmd)), _FakeProc(0))[1],
        )
        (tmp_path / "out").mkdir(parents=True)
        plan = _plan(tmp_path)
        rc = cgo.run_plan(plan, dry_run=False)
        assert rc == 0
        assert len(calls) == 4
        assert plan.modelfile_path.exists()

    def test_step_failure_short_circuits(self, tmp_path, monkeypatch):
        calls: list[list[str]] = []
        monkeypatch.setattr(
            cgo.subprocess, "run",
            lambda cmd, check=False: (calls.append(list(cmd)), _FakeProc(3))[1],
        )
        (tmp_path / "out").mkdir(parents=True)
        plan = _plan(tmp_path)
        rc = cgo.run_plan(plan, dry_run=False)
        assert rc == 1
        assert len(calls) == 1  # 首步失败即终止


# ============ 5. main 守卫 ============


class TestMainGuards:
    def test_missing_adapter_exits_1(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(
            cgo.sys, "argv",
            ["convert_gguf_ollama.py", "--adapter-dir", str(tmp_path / "nope"), "--dry-run"],
        )
        with pytest.raises(SystemExit) as exc:
            cgo.main()
        assert exc.value.code == 1

    def test_exec_mode_requires_llama_cpp_dir(self, tmp_path, monkeypatch):
        (tmp_path / "adapter").mkdir()
        monkeypatch.setattr(
            cgo.sys, "argv",
            ["convert_gguf_ollama.py", "--adapter-dir", str(tmp_path / "adapter")],
        )
        with pytest.raises(SystemExit) as exc:
            cgo.main()
        assert exc.value.code == 1

    def test_dry_run_main_returns_zero(self, tmp_path, monkeypatch):
        (tmp_path / "adapter").mkdir()
        monkeypatch.setattr(
            cgo.sys, "argv",
            ["convert_gguf_ollama.py", "--adapter-dir", str(tmp_path / "adapter"), "--dry-run"],
        )
        with pytest.raises(SystemExit) as exc:
            cgo.main()
        assert exc.value.code == 0
