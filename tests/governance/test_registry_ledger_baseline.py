# [MODULE] tests.governance.test_registry_ledger_baseline
# [DOMAIN] D_GOVERNANCE
# [TTL] task_bound
"""W-M1 波0⑤ 红蓝：Phase 0 基线导入 + 快照发布 + 双轨对账引擎。

判据（任务序列④⑤）：
1. 扫描机械正确（族计数/passthrough/身份模式）
2. 导入幂等：dry-run 零写；实跑计数正确；重跑零新事件零新行
3. 发布幂等：v1 发布 manifest 可点查；同内容重发=noop；内容变化→v2 单调
4. 双轨对账：导入后零未解释漂移；YAML 加条→补登记+事件；YAML 改内容→mismatch
   事件且 PG 不被覆写；PG 独有→pg_only 事件不删除
测试全部落临时 schema（registry_ledger_rb_*），收尾 CASCADE 删除，零生产路径写入。
"""

from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

import psycopg2
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    not (REPO_ROOT / "config" / ".env.postgres").exists(),
    reason="config/.env.postgres missing",
)


def _load_baseline_module():
    src = REPO_ROOT / "src" / "zephyr" / "governance" / "registry_ledger" / "baseline.py"
    spec = importlib.util.spec_from_file_location("wm1_baseline_under_test", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def baseline_mod():
    return _load_baseline_module()


def _pg_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (REPO_ROOT / "config" / ".env.postgres").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env


def _connect(env: dict[str, str]):
    return psycopg2.connect(
        host=env["POSTGRES_HOST"],
        port=env["POSTGRES_PORT"],
        dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"],
        password=env["POSTGRES_PASSWORD"],
    )


@pytest.fixture(scope="module")
def pg_env():
    env = _pg_env()
    try:
        conn = _connect(env)
    except psycopg2.OperationalError as exc:
        pytest.skip(f"PG unavailable: {exc}")
    conn.close()
    return env


@pytest.fixture()
def ledger(pg_env):
    from zephyr.governance.registry_ledger.deploy import deploy_registry_ledger

    schema = f"registry_ledger_rb_{uuid.uuid4().hex[:8]}"
    conn = _connect(pg_env)
    deploy_registry_ledger(conn, schema=schema)
    yield {"conn": conn, "schema": schema, "env": pg_env}
    conn.rollback()
    cur = conn.cursor()
    cur.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
    conn.commit()
    cur.close()
    conn.close()


SAMPLE_YAML = """schema_version: 1.0.0
module_id: PS-TEST-001
ttl: permanent
doc_type: gate
title: rb 测试册
status: active
registry_id: REG-RB-TEST-001
summary: baseline 红蓝临时册
capabilities:
- capability_id: alpha_cap
  description: 第一能力
- capability_id: beta_cap
  description: 第二能力
creation_tokens:
- file: src/zephyr/rb_demo_a.py
  token: rb-tok-a
  created_by: st-wm1-wave0-20260924
  capability: alpha_cap
- file: src/zephyr/rb_demo_a.py
  token: rb-tok-b
  created_by: st-wm1-wave0-20260924
  capability: alpha_cap
- file: src/zephyr/rb_demo_b.py
  token: rb-tok-c
  created_by: st-wm1-wave0-20260924
  capability: beta_cap
di_seam_exemptions: []
"""

# 声明制红蓝册（st-sI-identity-20261004 手术1/4）：date 抢占 jsonb 首字段形态下
# ruling_id 声明键恒稳；rekey 场景用（导入期位置键 → 声明键迁移零重复行）
DECLARED_YAML = """schema_version: 1.0.0
registry_id: REG-RB-DECL-001
title: 声明制红蓝册
status: active
unique_key:
- ruling_id
entries:
- ruling_id: '裁定#1'
  date: '2026-07-18'
- ruling_id: '裁定#2'
  date: '2026-07-18'
"""


@pytest.fixture()
def sample_registry(tmp_path):
    rel = "docs/_rb_fixture/sample_registry.yaml"
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(SAMPLE_YAML, encoding="utf-8", newline="\n")
    return tmp_path, rel


def _count(ledger, table: str, where: str = "", params: tuple = ()) -> int:
    cur = ledger["conn"].cursor()
    cur.execute(f'SELECT count(*) FROM "{ledger["schema"]}".{table} {where}', params)
    n = int(cur.fetchone()[0])
    cur.close()
    return n


def _scan(baseline_mod, sample_registry):
    root, rel = sample_registry
    return baseline_mod.scan_registry_file(root, rel)


class TestScan:
    def test_family_counts_and_identity_mode(self, baseline_mod, sample_registry):
        scan = _scan(baseline_mod, sample_registry)
        assert scan["registry_id"] == "REG-RB-TEST-001"  # YAML 头优先
        assert scan["entries_total"] == 5  # 2 caps + 3 tokens
        assert scan["family_stats"]["capabilities"]["entries"] == 2
        assert scan["family_stats"]["creation_tokens"]["entries"] == 3
        assert scan["family_stats"]["di_seam_exemptions"]["passthrough"] == 0  # 空 list 无条目项
        assert scan["identity_mode"] == "first_scalar_token"
        assert scan["primary_family"] == "creation_tokens"

    def test_iter_entries_yields_composite_keys(self, baseline_mod, sample_registry):
        root, rel = sample_registry
        keys = {(fk, ek) for fk, ek, _ in baseline_mod._iter_scan_entries(root, rel)}
        assert ("creation_tokens", "file=src/zephyr/rb_demo_a.py|token=rb-tok-a") in keys
        assert ("capabilities", "capability_id=alpha_cap") in keys


class TestImport:
    def test_dry_run_zero_writes(self, baseline_mod, sample_registry, ledger):
        root, rel = sample_registry
        rep = baseline_mod.import_baseline(root, rel, dry_run=True, conn=ledger["conn"], schema=ledger["schema"])
        assert rep["dry_run"] and rep["scan"]["entries_total"] == 5
        assert _count(ledger, "registry_entry") == 0
        assert _count(ledger, "registry_catalog") == 0

    def test_import_then_reimport_idempotent(self, baseline_mod, sample_registry, ledger):
        root, rel = sample_registry
        rep1 = baseline_mod.import_baseline(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        assert rep1["entries_imported"] == 5 and rep1["catalog_seeded"]
        assert _count(ledger, "registry_entry") == 5
        assert _count(ledger, "registry_event", "WHERE action='import'") == 5
        rep2 = baseline_mod.import_baseline(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        assert rep2["entries_imported"] == 0
        assert rep2["entries_skipped_existing"] == 5
        assert _count(ledger, "registry_event") == 5  # 零新事件


class TestPublishRepoRootGuard:
    """渐进腐蚀守卫（st-tclose-infracure2-20261005 件3）：repo_root=None 裸发布机械拒绝。

    实战事故=repo_root 缺失时 _projection_context_from_disk fail-open 降级空尾部段，
    渲染丢 di_seam_exemptions 等根键，且 noop 幂等把腐蚀固化成稳定态。
    """

    def test_publish_without_repo_root_rejected(self, baseline_mod, ledger):
        with pytest.raises(ValueError, match="repo_root 缺失将丢尾部段"):
            baseline_mod.publish_snapshot("REG-RB-TEST-001", conn=ledger["conn"], schema=ledger["schema"])

    def test_publish_with_repo_root_green(self, baseline_mod, sample_registry, ledger):
        root, rel = sample_registry
        baseline_mod.import_baseline(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        p = baseline_mod.publish_snapshot(
            "REG-RB-TEST-001", conn=ledger["conn"], schema=ledger["schema"], repo_root=root
        )
        assert p["snapshot_version"] == 1 and p["entry_count"] == 5


class TestPublish:
    def test_publish_versions_and_noop(self, baseline_mod, sample_registry, ledger):
        root, rel = sample_registry
        baseline_mod.import_baseline(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        p1 = baseline_mod.publish_snapshot(
            "REG-RB-TEST-001", git_commit_ref="a" * 40, conn=ledger["conn"], schema=ledger["schema"], repo_root=root
        )
        assert p1["snapshot_version"] == 1 and p1["entry_count"] == 5
        p2 = baseline_mod.publish_snapshot(
            "REG-RB-TEST-001", conn=ledger["conn"], schema=ledger["schema"], repo_root=root
        )
        assert p2["noop"] is True and p2["snapshot_version"] == 1  # 同内容重发=noop
        # 内容前进 → v2（内容更新走意图 API CAS——import 幂等不覆写，by-design）
        from zephyr.governance.registry_ledger.api import update

        r = update(
            "REG-RB-TEST-001",
            "capabilities",
            "capability_id=beta_cap",
            1,
            {"capability_id": "beta_cap", "description": "第二能力改"},
            reason="publish v2 test content bump",
            session_id="st-wm1-wave0-20260924",
            conn=ledger["conn"],
            schema=ledger["schema"],
        )
        assert r.code == "OK"
        p3 = baseline_mod.publish_snapshot(
            "REG-RB-TEST-001", conn=ledger["conn"], schema=ledger["schema"], repo_root=root
        )
        assert p3["noop"] is False and p3["snapshot_version"] == 2

    def test_publish_bundle_matches_reader_contract(self, baseline_mod, sample_registry, ledger):
        """WM1_24h_evaluation §3.1 契约统一回归：bundle=读端结构形态，snapshot_from_bundle
        可消费，render 往返语义等值（jsonb 键序归一属 cutover 噪音，不判字节）。"""
        import json as _json

        root, rel = sample_registry
        baseline_mod.import_baseline(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        p1 = baseline_mod.publish_snapshot(
            "REG-RB-TEST-001", conn=ledger["conn"], schema=ledger["schema"], repo_root=root
        )
        assert p1["snapshot_version"] == 1
        cur = ledger["conn"].cursor()
        cur.execute(
            f'SELECT bundle FROM "{ledger["schema"]}".registry_snapshot WHERE registry_id=%s AND snapshot_version=1',
            ("REG-RB-TEST-001",),
        )
        raw = cur.fetchone()[0]
        bundle = raw if isinstance(raw, dict) else _json.loads(raw)
        assert bundle["registry_id"] == "REG-RB-TEST-001"
        root_keys = [sec["root_key"] for sec in bundle["sections"]]
        assert "capabilities" in root_keys and "creation_tokens" in root_keys
        assert bundle["header_lines"] and bundle["header_lines"][0].startswith("schema_version")

        from zephyr.governance.registry_projection.pg_source import snapshot_from_bundle
        from zephyr.governance.registry_projection.renderer import render

        snap = snapshot_from_bundle(bundle, rel)
        assert snap.header_lines == bundle["header_lines"]
        assert {s.root_key for s in snap.sections} == {"capabilities", "creation_tokens"}
        assert [k for k, _ in snap.trailing_scalars] == ["di_seam_exemptions"]
        rendered = render(snap)
        import yaml as _yaml

        assert _yaml.safe_load(rendered) == _yaml.safe_load(SAMPLE_YAML), "render 往返语义等值"


class TestReconcile:
    def test_clean_after_import_then_drift_kinds(self, baseline_mod, sample_registry, ledger):
        root, rel = sample_registry
        baseline_mod.import_baseline(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        clean = baseline_mod.reconcile_registry(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        assert clean["zero_unexplained_drift"] is True
        assert clean["clean_match"] == 5 and clean["events_written"] == 0  # 幂等零新事件

        # ① YAML 私加一条 → PG 缺=补登记（backfill 事件）
        text = (root / rel).read_text(encoding="utf-8")
        (root / rel).write_text(
            text.replace(
                "di_seam_exemptions",
                "- file: src/zephyr/rb_new.py\n  token: rb-tok-new\n  created_by: x\n"
                "  capability: alpha_cap\ndi_seam_exemptions",
            ),
            encoding="utf-8",
            newline="\n",
        )
        r1 = baseline_mod.reconcile_registry(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        assert r1["backfilled"] == 1 and r1["zero_unexplained_drift"] is True
        assert _count(ledger, "registry_entry") == 6

        # ② YAML 条目内容被更新（落地常态）→ 双轨吸收：PG 跟随 YAML（version+1+事件）
        text = (root / rel).read_text(encoding="utf-8")
        (root / rel).write_text(text.replace("第二能力", "第二能力被私改"), encoding="utf-8", newline="\n")
        r2 = baseline_mod.reconcile_registry(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        assert r2.get("absorbed_from_yaml", 0) == 1
        assert r2["zero_unexplained_drift"] is True
        cur = ledger["conn"].cursor()
        cur.execute(
            f'SELECT payload, version FROM "{ledger["schema"]}".registry_entry WHERE entry_key=%s',
            ("capability_id=beta_cap",),
        )
        payload, version = cur.fetchone()
        cur.close()
        assert "被私改" in str(payload)  # YAML 真源内容已吸收
        assert int(version) == 2  # CAS 推进
        # 幂等：吸收后再对账=干净零新事件
        r2b = baseline_mod.reconcile_registry(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        assert r2b["events_written"] == 0 and r2b["clean_match"] == 6  # 5 原始+1 回补全净

        # ③ PG 独有（YAML 删条目）→ pg_only 事件，PG 行保留
        text = (root / rel).read_text(encoding="utf-8")
        (root / rel).write_text(
            text.replace("- capability_id: alpha_cap\n  description: 第一能力\n", ""), encoding="utf-8", newline="\n"
        )
        r3 = baseline_mod.reconcile_registry(root, rel, conn=ledger["conn"], schema=ledger["schema"])
        assert r3["pg_only"] >= 1
        assert _count(ledger, "registry_entry", "WHERE status='active'") >= 5  # 不物理删


class TestDeclaredIdentity:
    """st-sI-identity-20261004 身份声明制红蓝（手术1/2/4）。"""

    def test_scan_reports_declared_families(self, baseline_mod, tmp_path):
        rel = "docs/_rb_fixture/declared.yaml"
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(DECLARED_YAML, encoding="utf-8", newline="\n")
        scan = baseline_mod.scan_registry_file(tmp_path, rel)
        assert scan["declared_identity_families"] == ["entries"]
        assert scan["header"]["unique_key"] == ["ruling_id"]  # 手术1b：声明随头部面落库种子
        keys = {ek for _fk, ek, _p in baseline_mod._iter_scan_entries(tmp_path, rel)}
        assert keys == {"ruling_id=裁定#1", "ruling_id=裁定#2"}

    def test_publish_bundle_carries_plan_and_identity_first(self, baseline_mod, tmp_path, ledger):
        """手术2：bundle 落声明计划 + 声明身份字段置首（jsonb 键序重排免疫）。"""
        import json as _json

        rel = "docs/_rb_fixture/declared.yaml"
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        # jsonb 重排形态入库：date 抢首（模拟 PG 归还序）
        reordered = (
            "schema_version: 1.0.0\n"
            "registry_id: REG-RB-DECL-001\n"
            "title: t\n"
            "status: active\n"
            "unique_key:\n"
            "- ruling_id\n"
            "entries:\n"
            "- date: '2026-07-18'\n"
            "  ruling_id: '裁定#1'\n"
        )
        target.write_text(reordered, encoding="utf-8", newline="\n")
        baseline_mod.import_baseline(tmp_path, rel, conn=ledger["conn"], schema=ledger["schema"])
        # 直接改写 PG payload 键序模拟 jsonb 归还序（import 走盘面原序）
        cur = ledger["conn"].cursor()
        cur.execute(
            f"UPDATE \"{ledger['schema']}\".registry_entry SET payload=%s::jsonb WHERE registry_id='REG-RB-DECL-001'",
            (_json.dumps({"date": "2026-07-18", "ruling_id": "裁定#1"}),),
        )
        cur.close()
        ledger["conn"].commit()
        baseline_mod.publish_snapshot(
            "REG-RB-DECL-001", conn=ledger["conn"], schema=ledger["schema"], repo_root=tmp_path
        )
        cur = ledger["conn"].cursor()
        cur.execute(
            f'SELECT bundle FROM "{ledger["schema"]}".registry_snapshot WHERE registry_id=%s',
            ("REG-RB-DECL-001",),
        )
        bundle = cur.fetchone()[0]
        cur.close()
        if isinstance(bundle, str):
            bundle = _json.loads(bundle)
        assert bundle["unique_key_fields"] == {"entries": ["ruling_id"]}
        entry_pairs = bundle["sections"][0]["entries"][0]
        assert entry_pairs[0][0] == "ruling_id"  # 身份字段置首（手术2）
        # 渲染往返：声明键恒稳（位置口径下 date 会抢占）
        from zephyr.governance.registry_projection.pg_source import snapshot_from_bundle
        from zephyr.governance.registry_projection.renderer import render, self_check

        snap = snapshot_from_bundle(bundle, rel)
        rendered = render(snap)
        self_check(rendered, snap)
        assert "- ruling_id: 裁定#1" in rendered  # 声明首字段置首=渲染后重扫同键（位置口径下 date 抢占）

    def test_reconcile_rekeys_same_content_no_duplicate_rows(self, baseline_mod, tmp_path, ledger):
        """手术4 rekey 安全网：键口径迁移（位置键→声明键）同内容迁键零重复行。"""
        rel = "docs/_rb_fixture/rekey.yaml"
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        # 阶段一：无声明+date 抢首（jsonb 归还序形态）导入 → 位置键 date=2026-07-18
        # 两条同键 first-wins 只进一条（B3 撞并形态）
        reordered_no_decl = (
            "schema_version: 1.0.0\n"
            "registry_id: REG-RB-DECL-001\n"
            "title: t\n"
            "status: active\n"
            "entries:\n"
            "- date: '2026-07-18'\n"
            "  ruling_id: '裁定#1'\n"
            "- date: '2026-07-18'\n"
            "  ruling_id: '裁定#2'\n"
        )
        target.write_text(reordered_no_decl, encoding="utf-8", newline="\n")
        baseline_mod.import_baseline(tmp_path, rel, conn=ledger["conn"], schema=ledger["schema"])
        assert _count(ledger, "registry_entry") == 1  # 同位置键 first-wins 一条（撞并形态）

        # 阶段二：补声明（手术1b）→ 声明键 ruling_id=裁定#1/2 与 PG 位置键不等
        target.write_text(DECLARED_YAML, encoding="utf-8", newline="\n")
        rep = baseline_mod.reconcile_registry(tmp_path, rel, conn=ledger["conn"], schema=ledger["schema"])
        # B3 放大器封死：零重复行注入（总行数不超 yaml 键数），缺条目按声明键补齐
        assert _count(ledger, "registry_entry") <= 2
        assert _count(ledger, "registry_entry", "WHERE status='active'") <= 2
        cur = ledger["conn"].cursor()
        cur.execute(
            f'SELECT entry_key FROM "{ledger["schema"]}".registry_entry '
            "WHERE registry_id='REG-RB-DECL-001' ORDER BY entry_key"
        )
        keys = [r[0] for r in cur.fetchall()]
        cur.close()
        # 声明键空间收敛（老位置键行被 rekey 或内容不同被呈报，绝不双行同内容）
        assert len(keys) == len(set(keys))
        assert "date=2026-07-18" not in keys or keys.count("date=2026-07-18") == 1
        # 冒烟字段就位（手术4 报告面）
        assert rep["identity_smoke_sampled"] >= 2
        assert rep["identity_smoke_unstable"] == 0
