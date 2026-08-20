"""test_depgraph_design_conversion.py — #ARCH-70 双态转换 PG 集成测试。

覆盖 depgraph design→production 同身份 UPDATE 通道（2026-08-13 死锁实证治本）：
1. _SQL_CONVERT_DESIGN_NODE 在真实 PG 完成身份转换——file_path 回填、
   design_maturity→production、node_id 不变（edges FK 不断链的前提）
2. _resolve_converted_build_status 保护口径——testing/stable/deprecated 保留，
   planned 等占位值转扫描推导值
3. NEW-FILE-DEPGRAPH 门禁提示文案与实际 CLI 一致（防文案再漂移——漂移实证曾致
   AI 按不存在的 --module/--path/--transition-to-production 参数连环踩坑）

测试节点路径前缀 test/design_conversion/（幂等清理，可重复运行）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
for _p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT / "scripts" / "governance")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import generate_project_depgraph as gen  # noqa: E402

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

# 测试用唯一路径前缀（避免与真实数据冲突，对齐 design_protection 测试惯例）
_TEST_PATH = "test/design_conversion/probe.py"
_TEST_DOMAIN = "D_GOVERNANCE"

_PROBE_NODE = {
    "type": "script",
    "granularity": "file",
    "domain_id": _TEST_DOMAIN,
    "subdomain_id": None,
    "blueprint_id": "MOD-TEST-ARCH70",
    "belongs_to": "",
    "change_policy": "evolving",
    "impact_level": "L",
    "modification_permission": "ai_modifiable",
    "file_header_score": 15,
    "tags": "[]",
    "architecture_layer": "",
    "deployment_lifecycle": "stable",
    "type_specific_data": "{}",
    "node_name": "probe",
    "content_hash": "deadbeef" * 8,
    "public_api": "probe_func",
}


def _conn_or_skip():
    """PG 写连接（dict 行）；不可用则跳过（集成测试降级，不污染 CI）。

    对齐 test_cross_domain_trigger.py 先例：read_only=False + RealDictCursor。
    """
    try:
        from psycopg2.extras import RealDictCursor

        conn = get_depgraph_pg_connection(autocommit=False, read_only=False)
        conn.cursor_factory = RealDictCursor
        return conn
    except Exception as e:  # noqa: BLE001 — 连接失败即降级 skip
        pytest.skip(f"depgraph PG 不可用: {e}")


@pytest.fixture()
def conn():
    c = _conn_or_skip()
    yield c
    c.close()


@pytest.fixture(autouse=True)
def cleanup_probe(conn):
    """每个用例前后幂等清理测试节点（含关联边）。"""
    _delete_probe(conn)
    yield
    _delete_probe(conn)


def _delete_probe(conn) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM nodes WHERE path LIKE 'test/design_conversion/%'")
    conn.commit()


def _insert_design_probe(conn, build_status: str = "planned") -> int:
    """插入 design 态探针节点（file_path 空——复现 add_design_node 旧行为），返回 node_id。"""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO nodes (node_type, path, file_path, granularity, domain_id, "
        "blueprint_id, build_status, design_maturity, can_build) "
        "VALUES ('module', %s, '', 'file', %s, 'MOD-TEST-ARCH70', %s, 'design', 1) "
        "RETURNING node_id",
        (_TEST_PATH, _TEST_DOMAIN, build_status),
    )
    nid = cur.fetchone()["node_id"]
    conn.commit()
    return nid


def _run_convert_sql(conn, node_id: int, conv_build_status: str) -> None:
    """以探针扫描字段执行 #ARCH-70 同身份 UPDATE（与生成器 INSERT 循环同路径）。"""
    from datetime import datetime

    n = _PROBE_NODE
    cur = conn.cursor()
    cur.execute(
        gen._SQL_CONVERT_DESIGN_NODE,
        (
            n["type"],
            n["granularity"],
            n["domain_id"],
            n["subdomain_id"],
            n["blueprint_id"],
            n["belongs_to"],
            n["change_policy"],
            n["impact_level"],
            n["modification_permission"],
            n["file_header_score"],
            n["tags"],
            n["architecture_layer"],
            n["deployment_lifecycle"],
            n["type_specific_data"],
            datetime.now().isoformat(),
            n["node_name"],
            _TEST_PATH,
            1,
            conv_build_status,
            n["content_hash"],
            n["public_api"],
            node_id,
        ),
    )
    conn.commit()


class TestConvertDesignNodeSQL:
    """同身份 UPDATE 的 PG 行为断言。"""

    def test_identity_conversion(self, conn):
        """design 行被原地 UPDATE：maturity 转 production、file_path 回填、node_id 不变。"""
        nid = _insert_design_probe(conn, build_status="planned")
        conv_bs = gen._resolve_converted_build_status("planned", "generated")
        _run_convert_sql(conn, nid, conv_bs)

        cur = conn.cursor()
        cur.execute(
            "SELECT node_id, path, file_path, design_maturity, build_status, node_type, "
            "content_hash, public_api FROM nodes WHERE node_id = %s",
            (nid,),
        )
        row = cur.fetchone()
        assert row is not None, "转换后节点必须仍存在（同身份，非删旧插新）"
        assert row["node_id"] == nid, "node_id 不变（edges FK 不断链前提）"
        assert row["design_maturity"] == "production"
        assert row["file_path"] == _TEST_PATH, "file_path 回填（门禁查询列）"
        assert row["build_status"] == "generated", "planned 占位值 → 扫描推导值"
        assert row["node_type"] == "script", "node_type 采用扫描真实类型"
        assert row["content_hash"] == _PROBE_NODE["content_hash"]
        assert row["public_api"] == _PROBE_NODE["public_api"]

    def test_conversion_is_idempotent_guard(self, conn):
        """UPDATE 的 WHERE design_maturity='design' 条件使重复转换安全空转。"""
        nid = _insert_design_probe(conn, build_status="planned")
        _run_convert_sql(conn, nid, "generated")
        # 第二次转换：行已 production → WHERE 不命中 → 0 行更新，不报错
        cur = conn.cursor()
        from datetime import datetime

        n = _PROBE_NODE
        cur.execute(
            gen._SQL_CONVERT_DESIGN_NODE,
            (
                n["type"],
                n["granularity"],
                n["domain_id"],
                n["subdomain_id"],
                n["blueprint_id"],
                n["belongs_to"],
                n["change_policy"],
                n["impact_level"],
                n["modification_permission"],
                n["file_header_score"],
                n["tags"],
                n["architecture_layer"],
                n["deployment_lifecycle"],
                n["type_specific_data"],
                datetime.now().isoformat(),
                n["node_name"],
                _TEST_PATH,
                1,
                "generated",
                n["content_hash"],
                n["public_api"],
                nid,
            ),
        )
        assert cur.rowcount == 0, "已转 production 的行不应再被 UPDATE（幂等守卫）"
        conn.commit()


class TestResolveConvertedBuildStatus:
    """build_status 保护口径（纯逻辑，与 STATUS-PRESERVE 快照一致）。"""

    @pytest.mark.parametrize("preserved", ["testing", "stable", "deprecated"])
    def test_manual_promotion_preserved(self, preserved):
        assert gen._resolve_converted_build_status(preserved, "generated") == preserved

    @pytest.mark.parametrize("placeholder", ["planned", "", "generated"])
    def test_placeholder_replaced_by_scanned(self, placeholder):
        assert gen._resolve_converted_build_status(placeholder, "generated") == "generated"

    def test_empty_scanned_falls_back_generated(self):
        assert gen._resolve_converted_build_status("planned", "") == "generated"


class TestGateMessageCliAccuracy:
    """门禁提示文案 ↔ 实际 CLI 一致性（防文案漂移，#ARCH-70 断点A）。"""

    def _gate_message(self) -> str:
        from zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate import (
            make_new_file_depgraph_gate,
        )

        class _FakeGitResult:
            returncode = 0
            stdout = "src/zephyr/_arch70_gate_probe.py\n"

        class _FakeGateway:
            project_root = _REPO_ROOT

            def run_git(self, _args):
                return _FakeGitResult()

        spec = make_new_file_depgraph_gate()
        # mock 查询强制"未登记" → 走违规分支拿提示文案
        import zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate as gate_mod

        orig = gate_mod._check_depgraph_has_file
        gate_mod._check_depgraph_has_file = lambda _p: False
        try:
            # files 必须与 staged 新增交集非空（gate L229-240 的 commit 范围收窄）
            probe_abs = str(_REPO_ROOT / "src" / "zephyr" / "_arch70_gate_probe.py")
            ok, detail = spec.check(_FakeGateway(), [probe_abs], commit_message="", session_id="t")
        finally:
            gate_mod._check_depgraph_has_file = orig
        assert not ok, "强制 missing 时门禁必须阻断"
        return detail

    def test_no_phantom_cli_params(self):
        detail = self._gate_message()
        # 漂移实证的不存在参数/子命令，禁止再出现
        assert "--module <module_id> --path <file_path>" not in detail
        assert "--transition-to-production" not in detail

    def test_actual_cli_present(self):
        detail = self._gate_message()
        assert "--granularity file" in detail, "add-design-node 必须给位置参数+粒度旗标"
        assert "--output-db depgraph --force" in detail, "裸跑不写库，提示必须带 --output-db --force"
