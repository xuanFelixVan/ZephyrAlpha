# [A_test] module_id: MOD-TEST-274 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §architecture-health-dashboard
# [MODULE] tests.governance.test_architecture_health_dashboard_metrics
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_architecture_health_dashboard_metrics.py — P1 防复发 metric 单测

权威依据：scripts/governance/architecture_health_dashboard.py
覆盖 P1 新增 5 个 metric（M22/M23/M26/M27/M29）：

测试组：
- TestMetric22DocstringCoverage: 公共函数无 docstring 检测
- TestMetric23AsyncioCalls: asyncio.run/get_event_loop 调用计数
- TestMetric26TodoFixme: TODO/FIXME 标记计数
- TestMetric27OpenNotInWith: open() 未在 with 语句检测
- TestMetric29ResourceNotInTryFinally: 资源未在 try/finally 检测
- TestMetricsRegistered: METRICS 列表注册完整性

测试隔离：mock iter_prod_py_files() 返回 tmp_path 下的合成 .py 文件；
不依赖真实仓库状态。
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_GOV = _PROJECT_ROOT / "scripts" / "governance"
if str(_SCRIPTS_GOV) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_GOV))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from architecture_health_dashboard import (  # noqa: E402
    METRICS,
    metric_22_docstring_coverage,
    metric_23_asyncio_calls,
    metric_26_todo_fixme,
    metric_27_open_not_in_with,
    metric_29_resource_not_in_try_finally,
)


def _write_py(tmp_path: Path, name: str, content: str) -> Path:
    """在 tmp_path 下写合成 .py 文件，返回路径。"""
    fp = tmp_path / name
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    return fp


# ============================================================================
# TestMetric22DocstringCoverage
# ============================================================================


class TestMetric22DocstringCoverage:
    """M22 docstring 覆盖率倒数——公共函数无 docstring 检测。"""

    def test_public_function_without_docstring_detected(self, tmp_path):
        """公共函数无 docstring → 计入违规。"""
        fp = _write_py(tmp_path, "mod.py", "def foo():\n    pass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_22_docstring_coverage()
        assert result["metric_id"] == "M22"
        assert result["count"] == 1
        assert "foo" in result["details"][0]

    def test_public_function_with_docstring_passes(self, tmp_path):
        """公共函数有 docstring → 不计入违规。"""
        fp = _write_py(tmp_path, "mod.py", 'def foo():\n    """doc."""\n    pass\n')
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_22_docstring_coverage()
        assert result["count"] == 0

    def test_private_function_without_docstring_passes(self, tmp_path):
        """私有函数（_ 开头）无 docstring → 不计入违规。"""
        fp = _write_py(tmp_path, "mod.py", "def _foo():\n    pass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_22_docstring_coverage()
        assert result["count"] == 0

    def test_async_function_without_docstring_detected(self, tmp_path):
        """async 公共函数无 docstring → 计入违规。"""
        fp = _write_py(tmp_path, "mod.py", "async def foo():\n    pass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_22_docstring_coverage()
        assert result["count"] == 1

    def test_multiple_violations_all_reported(self, tmp_path):
        """多个无 docstring 函数全报告。"""
        fp = _write_py(tmp_path, "mod.py", "def foo():\n    pass\ndef bar():\n    pass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_22_docstring_coverage()
        assert result["count"] == 2


# ============================================================================
# TestMetric23AsyncioCalls
# ============================================================================


class TestMetric23AsyncioCalls:
    """M23 asyncio.run/get_event_loop 调用计数。"""

    def test_asyncio_run_detected(self, tmp_path):
        """asyncio.run( 调用 → 计入。"""
        fp = _write_py(tmp_path, "mod.py", "import asyncio\nasyncio.run(main())\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_23_asyncio_calls()
        assert result["metric_id"] == "M23"
        assert result["count"] == 1

    def test_get_event_loop_detected(self, tmp_path):
        """get_event_loop( 调用 → 计入。"""
        fp = _write_py(tmp_path, "mod.py", "loop = get_event_loop()\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_23_asyncio_calls()
        assert result["count"] == 1

    def test_no_asyncio_calls_passes(self, tmp_path):
        """无 asyncio 调用 → 0。"""
        fp = _write_py(tmp_path, "mod.py", "def foo():\n    pass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_23_asyncio_calls()
        assert result["count"] == 0

    def test_asyncio_module_attribute_not_counted(self, tmp_path):
        """asyncio.sleep 等非 run/get_event_loop 调用 → 不计入。"""
        fp = _write_py(tmp_path, "mod.py", "import asyncio\nasyncio.sleep(1)\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_23_asyncio_calls()
        assert result["count"] == 0


# ============================================================================
# TestMetric26TodoFixme
# ============================================================================


class TestMetric26TodoFixme:
    """M26 TODO/FIXME 计数。"""

    def test_todo_detected(self, tmp_path):
        """# TODO 标记 → 计入。"""
        fp = _write_py(tmp_path, "mod.py", "# TODO: fix this\npass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_26_todo_fixme()
        assert result["metric_id"] == "M26"
        assert result["count"] == 1

    def test_fixme_detected(self, tmp_path):
        """# FIXME 标记 → 计入。"""
        fp = _write_py(tmp_path, "mod.py", "# FIXME: broken\npass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_26_todo_fixme()
        assert result["count"] == 1

    def test_case_insensitive(self, tmp_path):
        """# todo / # Todo 大小写不敏感 → 计入。"""
        fp = _write_py(tmp_path, "mod.py", "# todo: lower case\n# Todo: mixed case\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_26_todo_fixme()
        assert result["count"] == 2

    def test_no_todo_fixme_passes(self, tmp_path):
        """无 TODO/FIXME → 0。"""
        fp = _write_py(tmp_path, "mod.py", "def foo():\n    pass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_26_todo_fixme()
        assert result["count"] == 0

    def test_word_boundary_not_false_positive(self, tmp_path):
        """'todolist' 等无 word boundary → 不计入。"""
        fp = _write_py(tmp_path, "mod.py", "x = 'todolist for today'\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_26_todo_fixme()
        assert result["count"] == 0


# ============================================================================
# TestMetric27OpenNotInWith
# ============================================================================


class TestMetric27OpenNotInWith:
    """M27 open() 未在 with 语句检测。"""

    def test_open_not_in_with_detected(self, tmp_path):
        """裸 open() 调用 → 计入违规。"""
        fp = _write_py(tmp_path, "mod.py", "f = open('file.txt')\nf.read()\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_27_open_not_in_with()
        assert result["metric_id"] == "M27"
        assert result["count"] == 1

    def test_open_in_with_passes(self, tmp_path):
        """with open() → 不计入违规。"""
        fp = _write_py(tmp_path, "mod.py", "with open('file.txt') as f:\n    f.read()\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_27_open_not_in_with()
        assert result["count"] == 0

    def test_multiple_open_calls_all_reported(self, tmp_path):
        """多个裸 open() → 全报告。"""
        fp = _write_py(tmp_path, "mod.py", "f1 = open('a')\nf2 = open('b')\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_27_open_not_in_with()
        assert result["count"] == 2

    def test_no_open_calls_passes(self, tmp_path):
        """无 open() → 0。"""
        fp = _write_py(tmp_path, "mod.py", "def foo():\n    pass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_27_open_not_in_with()
        assert result["count"] == 0


# ============================================================================
# TestMetric29ResourceNotInTryFinally
# ============================================================================


class TestMetric29ResourceNotInTryFinally:
    """M29 资源未在 try/finally 检测。"""

    def test_bare_open_not_in_try_detected(self, tmp_path):
        """裸 open() 不在 try/finally → 计入违规。"""
        fp = _write_py(tmp_path, "mod.py", "f = open('file.txt')\nf.read()\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_29_resource_not_in_try_finally()
        assert result["metric_id"] == "M29"
        assert result["count"] == 1

    def test_open_in_try_finally_passes(self, tmp_path):
        """open() 在 try/finally → 不计入违规。"""
        content = "try:\n    f = open('file.txt')\n    f.read()\nfinally:\n    f.close()\n"
        fp = _write_py(tmp_path, "mod.py", content)
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_29_resource_not_in_try_finally()
        assert result["count"] == 0

    def test_open_in_with_passes(self, tmp_path):
        """open() 在 with → 不计入违规（with 等价 try/finally）。"""
        fp = _write_py(tmp_path, "mod.py", "with open('file.txt') as f:\n    f.read()\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_29_resource_not_in_try_finally()
        assert result["count"] == 0

    def test_lock_acquire_not_in_try_detected(self, tmp_path):
        """Lock() 不在 try/finally → 计入违规。"""
        fp = _write_py(tmp_path, "mod.py", "lock = Lock()\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_29_resource_not_in_try_finally()
        assert result["count"] == 1

    def test_lock_in_try_finally_passes(self, tmp_path):
        """Lock() 在 try/finally → 不计入违规。"""
        content = "try:\n    lock = Lock()\nfinally:\n    pass\n"
        fp = _write_py(tmp_path, "mod.py", content)
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_29_resource_not_in_try_finally()
        assert result["count"] == 0

    def test_no_resource_acquire_passes(self, tmp_path):
        """无资源获取 → 0。"""
        fp = _write_py(tmp_path, "mod.py", "def foo():\n    pass\n")
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_29_resource_not_in_try_finally()
        assert result["count"] == 0


# ============================================================================
# TestMetricsRegistered
# ============================================================================


class TestMetricsRegistered:
    """METRICS 列表注册完整性。"""

    def test_m22_registered(self):
        """M22 在 METRICS 列表中。"""
        ids = [m[0] for m in METRICS]
        assert "M22" in ids

    def test_m23_registered(self):
        """M23 在 METRICS 列表中。"""
        ids = [m[0] for m in METRICS]
        assert "M23" in ids

    def test_m26_registered(self):
        """M26 在 METRICS 列表中。"""
        ids = [m[0] for m in METRICS]
        assert "M26" in ids

    def test_m27_registered(self):
        """M27 在 METRICS 列表中。"""
        ids = [m[0] for m in METRICS]
        assert "M27" in ids

    def test_m29_registered(self):
        """M29 在 METRICS 列表中。"""
        ids = [m[0] for m in METRICS]
        assert "M29" in ids

    def test_metrics_count_at_least_25(self):
        """METRICS 至少 25 项（原 20 + P1 新增 5）。"""
        assert len(METRICS) >= 25

    def test_metric_tuple_format(self):
        """每个 metric 是 (id, name, callable) 三元组。"""
        for mid, name, fn in METRICS:
            assert isinstance(mid, str)
            assert isinstance(name, str)
            assert callable(fn)
