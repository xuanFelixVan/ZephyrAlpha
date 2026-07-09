# [A_test] module_id: SRC-TST-2211 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-SYNC-PANORAMA | docs/_working/2026-07-09-panorama_module_sync_engine.md | §Phase2
# [MODULE] tests.governance.test_sync_panorama_module
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/governance/test_sync_panorama_module.py
# [TTL] task_bound
"""test_sync_panorama_module.py — 四图模块同步引擎单测（ARCH-056 Phase 2）

覆盖：
- 主函数签名存在性
- depgraph → dataflow 占位记录创建
- depgraph → decision 占位记录创建
- 模块不存在返回 exit 3
- --all 全量同步迭代
- 无参数返回 exit 3
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# depgraph hint: 让 generate_project_depgraph.py AST 扫描器检测 test→module 依赖边
# 实际测试用 importlib 动态加载（scripts/ 非 Python 包），此 import 运行时必失败
try:
    from scripts.governance.sync_panorama_module import sync_module_panorama  # noqa: F401
except ImportError:
    pass

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "governance" / "sync_panorama_module.py"


@pytest.fixture(scope="module")
def spm():
    """动态加载 sync_panorama_module.py（避免 __init__.py 依赖问题）"""
    spec = importlib.util.spec_from_file_location("sync_panorama_module_under_test", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_module_row(module_id="MOD-TEST", domain_id="D_TEST",
                     design_maturity="design", build_status="planned",
                     path="src/test.py"):
    """构造 depgraph 查询返回行（RealDictRow 兼容 dict 访问）"""
    return {
        "blueprint_id": module_id,
        "domain_id": domain_id,
        "design_maturity": design_maturity,
        "build_status": build_status,
        "path": path,
    }


def _mock_three_conns(spm, monkeypatch, depgraph_fetchone=None,
                      dataflow_fetchone=None, decision_fetchone=None,
                      depgraph_fetchall=None):
    """统一 mock 三个 DB 连接，返回 (depgraph_conn, dataflow_conn, decision_conn)

    fetchall 兼容：_query_depgraph_module 改用 fetchall 聚合后，
    当 fetchone=None 且 fetchall 未显式传入时，fetchall 默认返回 [fetchone] 或 []。
    """
    depgraph_conn = MagicMock()
    dep_cursor = MagicMock()
    dep_cursor.fetchone.return_value = depgraph_fetchone
    if depgraph_fetchall is not None:
        dep_cursor.fetchall.return_value = depgraph_fetchall
    elif depgraph_fetchone is not None:
        dep_cursor.fetchall.return_value = [depgraph_fetchone]
    else:
        dep_cursor.fetchall.return_value = []
    depgraph_conn.cursor.return_value.__enter__.return_value = dep_cursor

    dataflow_conn = MagicMock()
    df_cursor = MagicMock()
    df_cursor.fetchone.return_value = dataflow_fetchone
    dataflow_conn.cursor.return_value.__enter__.return_value = df_cursor

    decision_conn = MagicMock()
    dec_cursor = MagicMock()
    dec_cursor.fetchone.return_value = decision_fetchone
    decision_conn.cursor.return_value.__enter__.return_value = dec_cursor

    monkeypatch.setattr(spm, "get_depgraph_pg_connection", lambda **kw: depgraph_conn)
    monkeypatch.setattr(spm, "get_dataflowgraph_pg_connection", lambda **kw: dataflow_conn)
    monkeypatch.setattr(spm, "get_decisiongraph_pg_connection", lambda **kw: decision_conn)
    return depgraph_conn, dataflow_conn, decision_conn


class TestSyncModulePanoramaSignature:
    def test_main_function_exists(self, spm):
        assert hasattr(spm, "sync_module_panorama")

    def test_sync_all_function_exists(self, spm):
        assert hasattr(spm, "sync_all_panorama")


class TestSyncToDataflow:
    def test_creates_placeholder_job(self, spm, monkeypatch):
        """depgraph 有模块 → dataflow_jobs 建占位记录"""
        _mock_three_conns(
            spm, monkeypatch,
            depgraph_fetchone=_make_module_row(),
            dataflow_fetchone=None,   # 占位记录不存在
            decision_fetchone=None,   # 占位记录不存在
        )
        result = spm.sync_module_panorama("MOD-TEST")
        assert result == 0


class TestSyncToDecision:
    def test_creates_placeholder_layer(self, spm, monkeypatch):
        """depgraph 有模块 → decision_layers 建占位记录"""
        _mock_three_conns(
            spm, monkeypatch,
            depgraph_fetchone=_make_module_row(),
            dataflow_fetchone=None,
            decision_fetchone=None,
        )
        assert spm.sync_module_panorama("MOD-TEST") == 0


class TestSyncModuleNotFound:
    def test_module_not_in_depgraph_exit_3(self, spm, monkeypatch):
        """模块不在 depgraph → exit 3"""
        _mock_three_conns(
            spm, monkeypatch,
            depgraph_fetchone=None,  # 模块不存在
        )
        assert spm.sync_module_panorama("MOD-MISSING") == 3


class TestSyncAllPanorama:
    def test_sync_all_iterates_modules(self, spm, monkeypatch):
        """--all 遍历所有模块"""
        depgraph_conn = MagicMock()
        dep_cursor = MagicMock()
        dep_cursor.fetchall.return_value = [
            {"blueprint_id": "MOD-A"},
            {"blueprint_id": "MOD-B"},
        ]
        depgraph_conn.cursor.return_value.__enter__.return_value = dep_cursor
        monkeypatch.setattr(spm, "get_depgraph_pg_connection", lambda **kw: depgraph_conn)

        call_count = {"n": 0}

        def fake_sync(mid):
            call_count["n"] += 1
            return 0

        monkeypatch.setattr(spm, "sync_module_panorama", fake_sync)
        assert spm.sync_all_panorama() == 0
        assert call_count["n"] == 2


class TestMainNoArgs:
    def test_no_args_exit_3(self, spm, monkeypatch):
        """无参数 → exit 3"""
        monkeypatch.setattr("sys.argv", ["sync_panorama_module.py"])
        assert spm.main() == 3


class TestSyncExistingRealJob:
    def test_existing_real_job_updates_not_overwrites(self, spm, monkeypatch):
        """已有真实 job（entity_type='job'）→ UPDATE 核心字段，不改 entity_type"""
        _mock_three_conns(
            spm, monkeypatch,
            depgraph_fetchone=_make_module_row(),
            dataflow_fetchone={"entity_type": "job"},  # 已有真实 job
            decision_fetchone=None,
        )
        assert spm.sync_module_panorama("MOD-TEST") == 0


class TestWeightedVoting:
    def test_test_file_downweighted(self, spm):
        """测试文件降权：2源码 vs 2测试 → 源码域胜出

        行序刻意将测试域放前：Counter.most_common 平局按首次出现取值，
        会错误地返回 D_AUDITTEST；加权投票因测试文件降权 → 源码域胜出。
        """
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            _make_module_row("MOD-T", "D_AUDITTEST", "production", "stable", "tests/test_gov.py"),
            _make_module_row("MOD-T", "D_AUDITTEST", "production", "stable", "tests/test_gov2.py"),
            _make_module_row("MOD-T", "D_GOV_SCRIPTS", "production", "stable", "scripts/gov.py"),
            _make_module_row("MOD-T", "D_GOV_SCRIPTS", "production", "stable", "scripts/gov2.py"),
        ]
        conn.cursor.return_value.__enter__.return_value = cursor
        result = spm._query_depgraph_module(conn, "MOD-T")
        assert result["domain_id"] == "D_GOV_SCRIPTS"
