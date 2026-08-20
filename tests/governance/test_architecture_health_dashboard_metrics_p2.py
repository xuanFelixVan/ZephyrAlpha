# [A_test] module_id: MOD-TEST-275 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §architecture-health-dashboard
# [MODULE] tests.governance.test_architecture_health_dashboard_metrics_p2
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_architecture_health_dashboard_metrics_p2.py — P2 防复发 metric 单测

权威依据：scripts/governance/architecture_health_dashboard.py
覆盖 P2 新增 5 个 metric（M24/M25/M28/M30/M31）：

测试组：
- TestMetric24FieldShadowing: dataclass/BaseModel 字段遮蔽内置名检测
- TestMetric25ModuleConstMissingFinal: 模块级常量未标 Final 检测
- TestMetric28SingletonNoLock: 单例类无 Lock 检测
- TestMetric30ZephyrEnvEnumConsistency: ZEPHYR_ENV 直接访问检测
- TestMetric31McpVersionCoverage: MCP 工具 version 字段覆盖检测
- TestMetricsRegistered: METRICS 列表注册完整性（P2 扩展）

测试隔离：mock iter_prod_py_files() 返回 tmp_path 下的合成 .py 文件；
不依赖真实仓库状态。M31 测试 mock MCP_JSON_CANDIDATES 路径。
"""

from __future__ import annotations

import json
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
    metric_24_field_shadowing,
    metric_25_module_const_missing_final,
    metric_28_singleton_no_lock,
    metric_30_zephyr_env_enum_consistency,
    metric_31_mcp_version_coverage,
)


def _write_py(tmp_path: Path, name: str, content: str) -> Path:
    """在 tmp_path 下写合成 .py 文件，返回路径。"""
    fp = tmp_path / name
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    return fp


# ============================================================================
# TestMetric24FieldShadowing
# ============================================================================


class TestMetric24FieldShadowing:
    """M24 字段遮蔽计数（5.101 变量遮蔽与命名冲突）。"""

    def test_dataclass_field_shadowing_detected(self, tmp_path):
        """dataclass 字段遮蔽 id 被检测。"""
        fp = _write_py(
            tmp_path,
            "mod.py",
            ("from dataclasses import dataclass\n\n@dataclass\nclass Foo:\n    id: int\n    name: str\n"),
        )
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_24_field_shadowing()
        assert result["metric_id"] == "M24"
        assert result["count"] == 1
        assert "Foo.id" in result["details"][0]

    def test_dataclass_field_no_shadow_passes(self, tmp_path):
        """dataclass 字段不遮蔽内置名通过。"""
        fp = _write_py(
            tmp_path,
            "mod.py",
            ("from dataclasses import dataclass\n\n@dataclass\nclass Foo:\n    name: str\n    value: int\n"),
        )
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_24_field_shadowing()
        assert result["count"] == 0

    def test_basemodel_field_shadowing_detected(self, tmp_path):
        """Pydantic BaseModel 子类字段遮蔽 type 被检测。"""
        fp = _write_py(tmp_path, "mod.py", ("class Foo(BaseModel):\n    type: str\n    format: str\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_24_field_shadowing()
        assert result["count"] == 2

    def test_non_dataclass_class_not_scanned(self, tmp_path):
        """普通类（无 @dataclass / 非 BaseModel）不扫描。"""
        fp = _write_py(tmp_path, "mod.py", ("class Foo:\n    id: int = 0\n    type: str = ''\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_24_field_shadowing()
        assert result["count"] == 0

    def test_multiple_violations_all_reported(self, tmp_path):
        """多违规全部报告。"""
        fp = _write_py(
            tmp_path,
            "mod.py",
            (
                "from dataclasses import dataclass\n"
                "\n"
                "@dataclass\n"
                "class Foo:\n"
                "    id: int\n"
                "    file: str\n"
                "    type: str\n"
                "    format: str\n"
            ),
        )
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_24_field_shadowing()
        assert result["count"] == 4


# ============================================================================
# TestMetric25ModuleConstMissingFinal
# ============================================================================


class TestMetric25ModuleConstMissingFinal:
    """M25 模块级常量未标 Final 计数（5.114 Final/@final 强制）。"""

    def test_bare_const_no_final_detected(self, tmp_path):
        """裸常量赋值（无 Final 标注）被检测。"""
        fp = _write_py(tmp_path, "mod.py", ("MAX_RETRIES = 5\nTIMEOUT = 30.0\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_25_module_const_missing_final()
        assert result["metric_id"] == "M25"
        assert result["count"] == 2

    def test_final_annotated_const_passes(self, tmp_path):
        """Final 标注的常量通过。"""
        fp = _write_py(
            tmp_path,
            "mod.py",
            ("from typing import Final\n\nMAX_RETRIES: Final[int] = 5\nTIMEOUT: Final[float] = 30.0\n"),
        )
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_25_module_const_missing_final()
        assert result["count"] == 0

    def test_non_literal_const_passes(self, tmp_path):
        """非字面量常量（函数调用）通过。"""
        fp = _write_py(tmp_path, "mod.py", ("CONFIG = load_config()\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_25_module_const_missing_final()
        assert result["count"] == 0

    def test_lowercase_name_not_counted(self, tmp_path):
        """非大写命名风格不计数。"""
        fp = _write_py(tmp_path, "mod.py", ("retries = 5\ntimeout = 30.0\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_25_module_const_missing_final()
        assert result["count"] == 0

    def test_annassign_non_final_annotation_detected(self, tmp_path):
        """AnnAssign 注解非 Final 被检测。"""
        fp = _write_py(tmp_path, "mod.py", ("MAX_RETRIES: int = 5\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_25_module_const_missing_final()
        assert result["count"] == 1
        assert "MAX_RETRIES" in result["details"][0]

    def test_no_module_const_passes(self, tmp_path):
        """无模块级常量通过。"""
        fp = _write_py(tmp_path, "mod.py", ("def foo():\n    return 42\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_25_module_const_missing_final()
        assert result["count"] == 0


# ============================================================================
# TestMetric28SingletonNoLock
# ============================================================================


class TestMetric28SingletonNoLock:
    """M28 模块级单例无锁 double-check 计数（5.165 全局状态管理）。"""

    def test_singleton_no_lock_detected(self, tmp_path):
        """单例类无 Lock 被检测。"""
        fp = _write_py(
            tmp_path,
            "mod.py",
            (
                "class Foo:\n"
                "    _instance = None\n"
                "\n"
                "    @classmethod\n"
                "    def get(cls):\n"
                "        if cls._instance is None:\n"
                "            cls._instance = cls()\n"
                "        return cls._instance\n"
            ),
        )
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_28_singleton_no_lock()
        assert result["metric_id"] == "M28"
        assert result["count"] == 1
        assert "Foo" in result["details"][0]

    def test_singleton_with_lock_passes(self, tmp_path):
        """单例类有 Lock 通过。"""
        fp = _write_py(
            tmp_path,
            "mod.py",
            (
                "import threading\n"
                "\n"
                "class Foo:\n"
                "    _instance = None\n"
                "    _lock = threading.Lock()\n"
                "\n"
                "    @classmethod\n"
                "    def get(cls):\n"
                "        with cls._lock:\n"
                "            if cls._instance is None:\n"
                "                cls._instance = cls()\n"
                "        return cls._instance\n"
            ),
        )
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_28_singleton_no_lock()
        assert result["count"] == 0

    def test_no_singleton_passes(self, tmp_path):
        """无单例模式通过。"""
        fp = _write_py(tmp_path, "mod.py", ("class Foo:\n    pass\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_28_singleton_no_lock()
        assert result["count"] == 0

    def test_dunder_instance_detected(self, tmp_path):
        """__instance 私有变量也被检测。"""
        fp = _write_py(tmp_path, "mod.py", ("class Foo:\n    __instance = None\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_28_singleton_no_lock()
        assert result["count"] == 1

    def test_instance_not_none_passes(self, tmp_path):
        """_instance 非 None 不被检测。"""
        fp = _write_py(tmp_path, "mod.py", ("class Foo:\n    _instance = Foo()\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_28_singleton_no_lock()
        assert result["count"] == 0


# ============================================================================
# TestMetric30ZephyrEnvEnumConsistency
# ============================================================================


class TestMetric30ZephyrEnvEnumConsistency:
    """M30 ZEPHYR_ENV 枚举一致性（5.34 环境隔离）。"""

    def test_os_environ_subscript_detected(self, tmp_path):
        """os.environ['ZEPHYR_ENV'] 被检测。"""
        fp = _write_py(tmp_path, "mod.py", ("import os\nenv = os.environ['ZEPHYR_ENV']\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_30_zephyr_env_enum_consistency()
        assert result["metric_id"] == "M30"
        assert result["count"] == 1

    def test_os_environ_get_detected(self, tmp_path):
        """os.environ.get('ZEPHYR_ENV') 被检测。"""
        fp = _write_py(tmp_path, "mod.py", ("import os\nenv = os.environ.get('ZEPHYR_ENV')\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_30_zephyr_env_enum_consistency()
        assert result["count"] == 1

    def test_os_getenv_detected(self, tmp_path):
        """os.getenv('ZEPHYR_ENV') 被检测。"""
        fp = _write_py(tmp_path, "mod.py", ("import os\nenv = os.getenv('ZEPHYR_ENV')\n"))
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_30_zephyr_env_enum_consistency()
        assert result["count"] == 1

    def test_no_direct_access_passes(self, tmp_path):
        """无直接访问（通过 is_prod() canonical 入口）通过。"""
        fp = _write_py(
            tmp_path, "mod.py", ("from zephyr.shared.foundation.environment import is_prod\nif is_prod():\n    pass\n")
        )
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_30_zephyr_env_enum_consistency()
        assert result["count"] == 0

    def test_multiple_accesses_all_reported(self, tmp_path):
        """多处直接访问全部报告。"""
        fp = _write_py(
            tmp_path,
            "mod.py",
            (
                "import os\n"
                "a = os.environ['ZEPHYR_ENV']\n"
                "b = os.getenv('ZEPHYR_ENV')\n"
                "c = os.environ.get('ZEPHYR_ENV')\n"
            ),
        )
        with patch("architecture_health_dashboard.iter_prod_py_files", return_value=[fp]):
            with patch("architecture_health_dashboard.REPO_ROOT", tmp_path):
                result = metric_30_zephyr_env_enum_consistency()
        assert result["count"] == 3


# ============================================================================
# TestMetric31McpVersionCoverage
# ============================================================================


class TestMetric31McpVersionCoverage:
    """M31 MCP version 字段覆盖率（5.35 API 版本管理）。"""

    def test_tool_missing_version_detected(self, tmp_path):
        """工具缺 version 字段被检测。"""
        mcp_path = tmp_path / "mcp.json"
        mcp_path.write_text(
            json.dumps(
                {
                    "tools": [
                        {"name": "tool1"},  # 缺 version
                        {"name": "tool2", "version": "1.0.0"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        with patch("architecture_health_dashboard.MCP_JSON_CANDIDATES", (mcp_path,)):
            result = metric_31_mcp_version_coverage()
        assert result["metric_id"] == "M31"
        assert result["count"] == 1
        assert "tool1" in result["details"][0]

    def test_all_tools_have_version_passes(self, tmp_path):
        """所有工具有 version 通过。"""
        mcp_path = tmp_path / "mcp.json"
        mcp_path.write_text(
            json.dumps(
                {
                    "tools": [
                        {"name": "tool1", "version": "1.0.0"},
                        {"name": "tool2", "version": "2.0.0"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        with patch("architecture_health_dashboard.MCP_JSON_CANDIDATES", (mcp_path,)):
            result = metric_31_mcp_version_coverage()
        assert result["count"] == 0

    def test_mcp_json_not_found(self, tmp_path):
        """mcp.json 不存在返回 error。"""
        nonexistent = tmp_path / "nonexistent.json"
        with patch("architecture_health_dashboard.MCP_JSON_CANDIDATES", (nonexistent,)):
            result = metric_31_mcp_version_coverage()
        assert result["count"] == 0
        assert "not found" in result["error"]

    def test_multiple_tools_missing_version(self, tmp_path):
        """多工具缺 version 全部报告。"""
        mcp_path = tmp_path / "mcp.json"
        mcp_path.write_text(
            json.dumps(
                {
                    "tools": [
                        {"name": "a"},
                        {"name": "b"},
                        {"name": "c", "version": "1.0.0"},
                        {"name": "d"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        with patch("architecture_health_dashboard.MCP_JSON_CANDIDATES", (mcp_path,)):
            result = metric_31_mcp_version_coverage()
        assert result["count"] == 3

    def test_empty_tools_passes(self, tmp_path):
        """空 tools 列表通过。"""
        mcp_path = tmp_path / "mcp.json"
        mcp_path.write_text(json.dumps({"tools": []}), encoding="utf-8")
        with patch("architecture_health_dashboard.MCP_JSON_CANDIDATES", (mcp_path,)):
            result = metric_31_mcp_version_coverage()
        assert result["count"] == 0

    def test_invalid_json_returns_error(self, tmp_path):
        """无效 JSON 返回 error。"""
        mcp_path = tmp_path / "mcp.json"
        mcp_path.write_text("{invalid json}", encoding="utf-8")
        with patch("architecture_health_dashboard.MCP_JSON_CANDIDATES", (mcp_path,)):
            result = metric_31_mcp_version_coverage()
        assert result["count"] == 0
        assert "parse failed" in result["error"]


# ============================================================================
# TestMetricsRegistered (P2 扩展)
# ============================================================================


class TestMetricsRegistered:
    """METRICS 列表注册完整性（P2 扩展）。"""

    def test_m24_registered(self):
        """M24 已注册到 METRICS 列表。"""
        ids = [m[0] for m in METRICS]
        assert "M24" in ids

    def test_m25_registered(self):
        """M25 已注册到 METRICS 列表。"""
        ids = [m[0] for m in METRICS]
        assert "M25" in ids

    def test_m28_registered(self):
        """M28 已注册到 METRICS 列表。"""
        ids = [m[0] for m in METRICS]
        assert "M28" in ids

    def test_m30_registered(self):
        """M30 已注册到 METRICS 列表。"""
        ids = [m[0] for m in METRICS]
        assert "M30" in ids

    def test_m31_registered(self):
        """M31 已注册到 METRICS 列表。"""
        ids = [m[0] for m in METRICS]
        assert "M31" in ids

    def test_metrics_count_at_least_30(self):
        """METRICS 列表至少 30 项（M01-M31 含跳号）。"""
        assert len(METRICS) >= 30

    def test_metric_tuple_format(self):
        """每项是三元组 (id, name, callable)。"""
        for entry in METRICS:
            assert len(entry) == 3
            assert isinstance(entry[0], str)
            assert isinstance(entry[1], str)
            assert callable(entry[2])
