# [A_test] module_id: SRC-TST-2200 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-D5-ARCH-TOOLS | docs/03_modules/d5_architecture/blueprint.md | §query_tools
# [MODULE] tests.governance.test_query_module_panorama
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_query_module_panorama.py — 模块全景查询入口单测（四图模块对齐 Step 5）

权威依据：scripts/governance/query_module_panorama.py

测试组：
- TestQueryDepgraphNodes: _query_depgraph_nodes 返回 list[dict]
- TestQueryDepgraphMetadata: _query_depgraph_metadata 返回 dict|None
- TestQueryDataflowEntities: _query_dataflow_entities 合并 datasets+jobs
- TestQueryDecisionNodes: _query_decision_nodes 合并 layers+nodes
- TestQueryAllModules: _query_all_modules 返回 list[dict]
- TestSingleModuleNotFound: module_id 不存在 → exit 3（ERROR_CONTRACT）
- TestSingleModuleFound: module_id 存在 → exit 0
- TestAllModules: --all → exit 0
- TestMainNoArgs: 无参数 → exit 3
- TestMainAll: main(["--all"]) → exit 0

DB 连接全部 mock，不依赖真实 PostgreSQL。
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "governance"
    / "query_module_panorama.py"
)


@pytest.fixture(scope="module")
def qmp():
    """通过 importlib 加载 query_module_panorama.py 为独立模块。

    避免 scripts/ 路径与 governance 包名冲突。
    """
    spec = importlib.util.spec_from_file_location(
        "query_module_panorama_under_test", _SCRIPT_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 辅助：脚本化 mock cursor / connection
# ---------------------------------------------------------------------------


class _ScriptedCursor:
    """按 execute() 调用顺序返回预置 (description, fetchall, fetchone)。

    每次 execute() 推进到下一个脚本，使多查询函数（如 _query_dataflow_entities
    执行 datasets + jobs 两次 execute）可分别返回不同结果。
    """

    def __init__(self, scripts: list[tuple]):
        # scripts: list of (description, fetchall_rows, fetchone_row)
        self._scripts = scripts
        self._idx = 0
        self._current = scripts[0] if scripts else (None, [], None)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self._current = self._scripts[self._idx]
        self._idx += 1

    @property
    def description(self):
        return self._current[0]

    def fetchall(self):
        return self._current[1]

    def fetchone(self):
        return self._current[2]


def _make_mock_conn(scripts: list[tuple]) -> MagicMock:
    """构造 mock connection，cursor 返回 _ScriptedCursor。

    Args:
        scripts: list of (description, fetchall_rows, fetchone_row)；
                 description 是列名元组如 [("path",), ("node_type",)]
    """
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = _ScriptedCursor(scripts)
    return conn


# ---------------------------------------------------------------------------
# 1. 底层查询函数
# ---------------------------------------------------------------------------


class TestQueryDepgraphNodes:
    """_query_depgraph_nodes 返回 list[dict]。"""

    def test_returns_list_of_dict(self, qmp, monkeypatch):
        desc = [("path",), ("node_type",), ("domain_id",),
                ("design_maturity",), ("build_status",),
                ("entry_point",), ("public_api",), ("blueprint_path",)]
        rows = [
            ("src/a.py", "module", "D_GOVERNANCE", "production", "stable", True, "run", "bp.md"),
            ("src/b.py", "module", "D_GOVERNANCE", "production", "stable", False, "", "bp.md"),
        ]
        conn = _make_mock_conn([(desc, rows, None)])
        monkeypatch.setattr(qmp, "get_depgraph_pg_connection", lambda: conn)
        result = qmp._query_depgraph_nodes("MOD-TEST")
        assert len(result) == 2
        assert result[0]["path"] == "src/a.py"
        assert result[0]["entry_point"] is True
        assert result[1]["public_api"] == ""
        conn.close.assert_called_once()


class TestQueryDepgraphMetadata:
    """_query_depgraph_metadata 返回 dict|None。"""

    def test_returns_dict_when_found(self, qmp, monkeypatch):
        desc = [("path",), ("module_name_cn",), ("module_name_en",),
                ("description_cn",), ("description_en",), ("tags",), ("last_updated",)]
        row = ("src/a.py", "测试模块", "test_module", "desc", "desc_en", "t1", "2026-07-09")
        conn = _make_mock_conn([(desc, [], row)])
        monkeypatch.setattr(qmp, "get_depgraph_pg_connection", lambda: conn)
        result = qmp._query_depgraph_metadata("MOD-TEST")
        assert result is not None
        assert result["module_name_cn"] == "测试模块"

    def test_returns_none_when_not_found(self, qmp, monkeypatch):
        conn = _make_mock_conn([((("path",),), [], None)])
        monkeypatch.setattr(qmp, "get_depgraph_pg_connection", lambda: conn)
        result = qmp._query_depgraph_metadata("MOD-MISSING")
        assert result is None


class TestQueryDataflowEntities:
    """_query_dataflow_entities 合并 datasets + jobs。"""

    def test_merges_datasets_and_jobs(self, qmp, monkeypatch):
        ds_desc = [("entity_name",), ("entity_type",), ("scope",),
                   ("domain_id",), ("physical_type",)]
        ds_rows = [("ds1", "dataset", "global", "D_MARKET", "table")]
        job_desc = [("job_name",), ("entity_type",), ("scope",),
                    ("source_code_ref",), ("trigger_type",)]
        job_rows = [("job1", "job", "global", "src/j.py", "event")]
        # 两次 execute：datasets / jobs
        conn = _make_mock_conn([
            (ds_desc, ds_rows, None),
            (job_desc, job_rows, None),
        ])
        monkeypatch.setattr(qmp, "get_dataflowgraph_pg_connection", lambda: conn)
        result = qmp._query_dataflow_entities("MOD-TEST")
        assert len(result) == 2
        assert result[0]["entity_name"] == "ds1"
        assert result[1]["job_name"] == "job1"


class TestQueryDecisionNodes:
    """_query_decision_nodes 合并 layers + nodes。"""

    def test_merges_layers_and_nodes(self, qmp, monkeypatch):
        node_desc = [("decision_name",), ("layer_id",), ("node_type",),
                     ("design_maturity",), ("build_status",)]
        node_rows = [("dec1", "L1", "action", "production", "stable")]
        layer_desc = [("layer_name",), ("layer_id",), ("design_maturity",),
                      ("build_status",)]
        layer_rows = [("Layer1", "L1", "production", "stable")]
        conn = _make_mock_conn([
            (node_desc, node_rows, None),
            (layer_desc, layer_rows, None),
        ])
        monkeypatch.setattr(qmp, "get_decisiongraph_pg_connection", lambda: conn)
        result = qmp._query_decision_nodes("MOD-TEST")
        assert len(result) == 2
        # layers 在前（代码 return layers + nodes）
        assert result[0]["layer_name"] == "Layer1"
        assert result[1]["decision_name"] == "dec1"


class TestQueryAllModules:
    """_query_all_modules 返回 list[dict]。"""

    def test_returns_grouped_modules(self, qmp, monkeypatch):
        desc = [("blueprint_id",), ("domain_id",), ("file_count",),
                ("design_maturity",), ("build_status",),
                ("blueprint_path",), ("has_entry_point",)]
        rows = [
            ("MOD-A", "D_GOVERNANCE", 3, "production", "stable", "bp/a.md", True),
            ("MOD-B", "D_MARKET", 1, "prototype", "generated", "bp/b.md", False),
        ]
        conn = _make_mock_conn([(desc, rows, None)])
        monkeypatch.setattr(qmp, "get_depgraph_pg_connection", lambda: conn)
        result = qmp._query_all_modules()
        assert len(result) == 2
        assert result[0]["blueprint_id"] == "MOD-A"
        assert result[1]["file_count"] == 1


# ---------------------------------------------------------------------------
# 2. 打印函数 + main（exit code 契约）
# ---------------------------------------------------------------------------


class TestSingleModuleNotFound:
    """module_id 不存在 → exit 3（ERROR_CONTRACT）。"""

    def test_not_found_exit_3(self, qmp, monkeypatch, capsys):
        # depgraph 返回空
        desc = [("path",), ("node_type",), ("domain_id",),
                ("design_maturity",), ("build_status",),
                ("entry_point",), ("public_api",), ("blueprint_path",)]
        conn = _make_mock_conn([(desc, [], None)])
        monkeypatch.setattr(qmp, "get_depgraph_pg_connection", lambda: conn)
        rc = qmp._print_single_module("MOD-MISSING")
        assert rc == 3
        captured = capsys.readouterr()
        assert "MOD-MISSING" in captured.err


class TestSingleModuleFound:
    """module_id 存在 → exit 0。"""

    def test_found_exit_0(self, qmp, monkeypatch, capsys):
        node_desc = [("path",), ("node_type",), ("domain_id",),
                     ("design_maturity",), ("build_status",),
                     ("entry_point",), ("public_api",), ("blueprint_path",)]
        node_rows = [("src/a.py", "module", "D_GOVERNANCE", "production", "stable", True, "run", "bp.md")]
        meta_desc = [("path",), ("module_name_cn",), ("module_name_en",),
                     ("description_cn",), ("description_en",), ("tags",), ("last_updated",)]
        # depgraph 连接被调用两次：_query_depgraph_nodes + _query_depgraph_metadata
        conn_nodes = _make_mock_conn([(node_desc, node_rows, None)])
        conn_meta = _make_mock_conn([(meta_desc, [], None)])
        monkeypatch.setattr(
            qmp, "get_depgraph_pg_connection",
            MagicMock(side_effect=[conn_nodes, conn_meta]),
        )
        # dataflow + decision 返回空
        monkeypatch.setattr(
            qmp, "get_dataflowgraph_pg_connection",
            lambda: _make_mock_conn([
                ((("entity_name",),), [], None),
                ((("job_name",),), [], None),
            ]),
        )
        monkeypatch.setattr(
            qmp, "get_decisiongraph_pg_connection",
            lambda: _make_mock_conn([
                ((("decision_name",),), [], None),
                ((("layer_name",),), [], None),
            ]),
        )
        rc = qmp._print_single_module("MOD-TEST")
        assert rc == 0


class TestAllModules:
    """--all → exit 0。"""

    def test_all_modules_exit_0(self, qmp, monkeypatch, capsys):
        desc = [("blueprint_id",), ("domain_id",), ("file_count",),
                ("design_maturity",), ("build_status",),
                ("blueprint_path",), ("has_entry_point",)]
        rows = [("MOD-A", "D_GOVERNANCE", 2, "production", "stable", "bp.md", True)]
        conn = _make_mock_conn([(desc, rows, None)])
        monkeypatch.setattr(qmp, "get_depgraph_pg_connection", lambda: conn)
        rc = qmp._print_all_modules()
        assert rc == 0
        captured = capsys.readouterr()
        assert "MOD-A" in captured.out


class TestMainNoArgs:
    """无参数 → exit 3。"""

    def test_no_args_exit_3(self, qmp, monkeypatch):
        monkeypatch.setattr("sys.argv", ["query_module_panorama.py"])
        rc = qmp.main()
        assert rc == 3


class TestMainAll:
    """main() with --all → exit 0。"""

    def test_main_all_exit_0(self, qmp, monkeypatch):
        monkeypatch.setattr("sys.argv", ["query_module_panorama.py", "--all"])
        desc = [("blueprint_id",), ("domain_id",), ("file_count",),
                ("design_maturity",), ("build_status",),
                ("blueprint_path",), ("has_entry_point",)]
        rows = [("MOD-A", "D_GOVERNANCE", 1, "production", "stable", "bp.md", False)]
        conn = _make_mock_conn([(desc, rows, None)])
        monkeypatch.setattr(qmp, "get_depgraph_pg_connection", lambda: conn)
        rc = qmp.main()
        assert rc == 0
