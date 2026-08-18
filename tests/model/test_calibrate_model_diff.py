# [A_test] module_id: MOD-GOV_calibrate_model_diff | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §test
# [MODULE] tests.test_calibrate_model_diff
# [INVARIANTS] 零成本合成数据;不调真实模型;覆盖退出码0/1/2/3
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound
"""
calibrate_model_diff.py 单元测试（P1-3 配套, 零成本合成数据）。

覆盖:
    1. _compute_per_capability_ratio 纯函数逻辑
    2. main() 退出码 0 (PASS: 比率在范围内)
    3. main() 退出码 1 (FAIL: 比率超出范围)
    4. main() 退出码 2 (护照不存在)
    5. main() 退出码 3 (分母为 0)
    6. --list 列出可用护照
    7. CLI 参数解析 (--target-ratio, --tolerance)

设计原则:
    - 全部用合成 CapabilityPassport 对象, monkeypatch CapabilityPassport.load
    - 不依赖 data/brain/passports/ 真实数据, 保证测试可复现
    - 不调真实模型, 零成本
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 确保 scripts/ 包可被导入 (pytest 从项目根运行时通常已可发现)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# 导入被测脚本 (注意: scripts/ 是包, 见 scripts/__init__.py)
from scripts.calibrate_model_diff import (  # noqa: E402
    CAP_DISCRIMINATION_DRIFT,
    DEFAULT_TARGET_RATIO,
    DEFAULT_TOLERANCE,
    _compute_per_capability_ratio,
    _print_report,
    main,
)
from zephyr.intelligence.model_profiling.capability_passport import (  # noqa: E402
    CapabilityPassport,
    DepthCapabilityResult,
    DepthResult,
)

# ══════════════════════════════════════════════════════════════
# 合成护照工厂
# ══════════════════════════════════════════════════════════════


def _make_passport(
    model_id: str,
    overall_score: float,
    capabilities: dict[str, float] | None = None,
) -> CapabilityPassport:
    """构造合成护照 (仅填充校准脚本使用的字段)。"""
    p = CapabilityPassport(model_id=model_id)
    p.overall_score = overall_score
    p.overall_grade = "B"  # 占位, 校准脚本不依赖
    if capabilities:
        p.depth = DepthResult(
            overall_score=overall_score,
            capabilities={
                cap: DepthCapabilityResult(f1=f1, pass_=f1 >= 0.55)
                for cap, f1 in capabilities.items()
            },
        )
    return p


# ══════════════════════════════════════════════════════════════
# Test 1: _compute_per_capability_ratio 纯函数
# ══════════════════════════════════════════════════════════════


class TestComputePerCapabilityRatio:
    def test_basic_ratio(self):
        # cap_x: 0.9/0.3 = 3.0, |3.0 - 1.3| = 1.7 > 0.3 → drift
        # cap_y: 0.6/0.5 = 1.2, |1.2 - 1.3| = 0.1 < 0.3 → not drift
        a = _make_passport("a", 0.8, {"cap_x": 0.9, "cap_y": 0.6})
        b = _make_passport("b", 0.6, {"cap_x": 0.3, "cap_y": 0.5})
        rows = _compute_per_capability_ratio(a, b)
        assert len(rows) == 2
        cap_x = next(r for r in rows if r["capability"] == "cap_x")
        cap_y = next(r for r in rows if r["capability"] == "cap_y")
        assert cap_x["ratio"] == pytest.approx(3.0)
        assert cap_x["drift"] is True
        assert cap_y["ratio"] == pytest.approx(1.2)
        assert cap_y["drift"] is False

    def test_zero_denominator_returns_none_ratio(self):
        a = _make_passport("a", 0.8, {"cap_x": 0.5})
        b = _make_passport("b", 0.0, {"cap_x": 0.0})
        rows = _compute_per_capability_ratio(a, b)
        assert rows[0]["ratio"] is None
        assert rows[0]["drift"] is True  # None 视为 drift

    def test_union_of_capabilities(self):
        """A 和 B 能力集合不一致时, 取并集。"""
        a = _make_passport("a", 0.8, {"cap_a_only": 0.5, "shared": 0.6})
        b = _make_passport("b", 0.6, {"shared": 0.3, "cap_b_only": 0.4})
        rows = _compute_per_capability_ratio(a, b)
        caps = {r["capability"] for r in rows}
        assert caps == {"cap_a_only", "cap_b_only", "shared"}
        # cap_a_only 在 B 中缺失 → f1_b=0 → ratio=None
        cap_a_only = next(r for r in rows if r["capability"] == "cap_a_only")
        assert cap_a_only["f1_b"] == 0.0
        assert cap_a_only["ratio"] is None

    def test_empty_capabilities(self):
        a = _make_passport("a", 0.8, {})
        b = _make_passport("b", 0.6, {})
        rows = _compute_per_capability_ratio(a, b)
        assert rows == []


# ══════════════════════════════════════════════════════════════
# Test 2: _print_report 通过/失败判定
# ══════════════════════════════════════════════════════════════


class TestPrintReportVerdict:
    def test_pass_when_ratio_in_range(self, capsys):
        # 0.78 / 0.60 = 1.30 → 恰好在 [1.2, 1.4] 内
        a = _make_passport("strong", 0.78)
        b = _make_passport("weak", 0.60)
        passed = _print_report(a, b, 1.3, 0.1, verbose=False)
        assert passed is True
        out = capsys.readouterr().out
        assert "PASS" in out
        assert "1.3000" in out or "1.30" in out

    def test_fail_when_ratio_below_range(self, capsys):
        # 0.65 / 0.60 = 1.083 → 低于 1.2
        a = _make_passport("strong", 0.65)
        b = _make_passport("weak", 0.60)
        passed = _print_report(a, b, 1.3, 0.1, verbose=False)
        assert passed is False
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "偏低" in out

    def test_fail_when_ratio_above_range(self, capsys):
        # 0.90 / 0.60 = 1.50 → 高于 1.4
        a = _make_passport("strong", 0.90)
        b = _make_passport("weak", 0.60)
        passed = _print_report(a, b, 1.3, 0.1, verbose=False)
        assert passed is False
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "偏高" in out

    def test_returns_none_when_denominator_zero(self, capsys):
        a = _make_passport("strong", 0.78)
        b = _make_passport("weak", 0.0)
        passed = _print_report(a, b, 1.3, 0.1, verbose=False)
        assert passed is None
        err = capsys.readouterr().err
        assert "overall_score = 0" in err

    def test_boundary_lo_inclusive(self, capsys):
        # 0.72 / 0.60 = 1.20 → 边界值, 应通过
        a = _make_passport("strong", 0.72)
        b = _make_passport("weak", 0.60)
        passed = _print_report(a, b, 1.3, 0.1, verbose=False)
        assert passed is True

    def test_boundary_hi_inclusive(self, capsys):
        # 0.84 / 0.60 = 1.40 → 边界值, 应通过
        a = _make_passport("strong", 0.84)
        b = _make_passport("weak", 0.60)
        passed = _print_report(a, b, 1.3, 0.1, verbose=False)
        assert passed is True

    def test_verbose_includes_capability_table(self, capsys):
        a = _make_passport("strong", 0.78, {"cap_x": 0.6})
        b = _make_passport("weak", 0.60, {"cap_x": 0.3})
        _print_report(a, b, 1.3, 0.1, verbose=True)
        out = capsys.readouterr().out
        assert "cap_x" in out
        assert "drift" in out.lower() or "判别力" in out


# ══════════════════════════════════════════════════════════════
# Test 3: main() 退出码
# ══════════════════════════════════════════════════════════════


class TestMainExitCodes:
    def test_exit_0_when_pass(self, monkeypatch, capsys):
        # 0.78 / 0.60 = 1.30 → PASS
        a = _make_passport("strong", 0.78)
        b = _make_passport("weak", 0.60)

        def fake_load(model_id, verify=False):
            return a if model_id == "strong" else b

        monkeypatch.setattr(
            "scripts.calibrate_model_diff.CapabilityPassport.load", staticmethod(fake_load)
        )
        rc = main(["--model-a", "strong", "--model-b", "weak"])
        assert rc == 0

    def test_exit_1_when_fail(self, monkeypatch, capsys):
        # 0.65 / 0.60 = 1.083 → FAIL (低于 1.2)
        a = _make_passport("strong", 0.65)
        b = _make_passport("weak", 0.60)

        def fake_load(model_id, verify=False):
            return a if model_id == "strong" else b

        monkeypatch.setattr(
            "scripts.calibrate_model_diff.CapabilityPassport.load", staticmethod(fake_load)
        )
        rc = main(["--model-a", "strong", "--model-b", "weak"])
        assert rc == 1

    def test_exit_2_when_passport_missing(self, monkeypatch, capsys):
        def fake_load(model_id, verify=False):
            return None

        monkeypatch.setattr(
            "scripts.calibrate_model_diff.CapabilityPassport.load", staticmethod(fake_load)
        )
        with pytest.raises(SystemExit) as exc:
            main(["--model-a", "ghost", "--model-b", "weak"])
        assert exc.value.code == 2

    def test_exit_3_when_denominator_zero(self, monkeypatch, capsys):
        a = _make_passport("strong", 0.78)
        b = _make_passport("weak", 0.0)  # 分母为 0

        def fake_load(model_id, verify=False):
            return a if model_id == "strong" else b

        monkeypatch.setattr(
            "scripts.calibrate_model_diff.CapabilityPassport.load", staticmethod(fake_load)
        )
        rc = main(["--model-a", "strong", "--model-b", "weak"])
        assert rc == 3

    def test_list_flag(self, monkeypatch, capsys):
        # 合成 2 个护照
        p1 = _make_passport("alpha", 0.85)
        p2 = _make_passport("beta", 0.70)

        def fake_load(model_id, verify=False):
            return {"alpha": p1, "beta": p2}.get(model_id)

        monkeypatch.setattr(
            "scripts.calibrate_model_diff.CapabilityPassport.load", staticmethod(fake_load)
        )
        monkeypatch.setattr(
            "scripts.calibrate_model_diff.CapabilityPassport.list_all",
            staticmethod(lambda: ["alpha", "beta"]),
        )
        rc = main(["--list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out
        assert "可用护照" in out


# ══════════════════════════════════════════════════════════════
# Test 4: CLI 参数
# ══════════════════════════════════════════════════════════════


class TestCliArgs:
    def test_custom_target_ratio_and_tolerance(self, monkeypatch, capsys):
        # 0.60 / 0.50 = 1.20, 自定义目标 1.5 ± 0.1 → 区间 [1.4, 1.6], 1.20 在区间外 → FAIL
        a = _make_passport("a", 0.60)
        b = _make_passport("b", 0.50)

        def fake_load(model_id, verify=False):
            return a if model_id == "a" else b

        monkeypatch.setattr(
            "scripts.calibrate_model_diff.CapabilityPassport.load", staticmethod(fake_load)
        )
        rc = main(
            [
                "--model-a", "a",
                "--model-b", "b",
                "--target-ratio", "1.5",
                "--tolerance", "0.1",
            ]
        )
        assert rc == 1
        out = capsys.readouterr().out
        assert "1.50" in out
        assert "[1.40, 1.60]" in out

    def test_default_constants(self):
        # 验证默认常量符合 P1-3 设计目标
        assert DEFAULT_TARGET_RATIO == 1.3
        assert DEFAULT_TOLERANCE == 0.1
        assert CAP_DISCRIMINATION_DRIFT == 0.3
