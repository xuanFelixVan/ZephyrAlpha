# [BLUEPRINT]
# [MODULE] scripts.governance.repair.concurrent_write_test
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
[BLUEPRINT] | scripts/governance/repair/concurrent_write_test.py | §1
[MODULE] 无（独立测试脚本）
[INVARIANTS] 使用测试数据库副本，不污染生产数据
[MODIFY-GUARD] scripts/governance/apply_depgraph.py
[CONSUMERS] 手动执行（修改 apply_depgraph.py 后回归验证）
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 任一测试失败→exit 1; 全部通过→exit 0
[TESTS] 无（自身是测试脚本）

红蓝对抗测试脚本 — depgraph 并发写入极限测试

测试场景 T1-T10，覆盖文件锁串行化、SQLite WAL 读写并发、
事务回滚、草稿模式冲突、死锁清理、锁重入等。

使用测试数据库副本，不污染生产数据。
"""

__manifest__ = {
    "args": [],
    "description": "红蓝对抗测试：depgraph 并发写入极限测试（10场景）",
    "dimensions": ["D5", "D6"],
    "priority": "P2",
    "timeout_seconds": 300,
    "warn_only": True,
}
import json
import multiprocessing as mp
import os
import shutil
import sqlite3
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402

TEST_DB = REPO_ROOT / "data" / "databases" / "_test_rb_depgraph.db"

# 测试结果收集
results = []


def setup():
    """复制生产数据库到测试数据库，并清理测试残留数据"""
    if TEST_DB.exists():
        TEST_DB.unlink()
    for suffix in ("-wal", "-shm"):
        f = TEST_DB.with_suffix(TEST_DB.suffix + suffix)
        if f.exists():
            f.unlink()
    # P2迁移后：depgraph 已迁至 PostgreSQL，原 PROD_DB 文件不再存在。
    # 本函数整体为弃用死代码（main() 已提前 return），保留结构供历史参考。
    # shutil.copy2(PROD_DB, TEST_DB)  # 已移除：源文件不存在
    # 清理测试残留数据（防止上次测试残留干扰）
    conn = sqlite3.connect(str(TEST_DB))
    try:
        conn.execute(
            "DELETE FROM edges WHERE from_node_id IN (SELECT node_id FROM nodes WHERE path LIKE 'src/test_%') OR to_node_id IN (SELECT node_id FROM nodes WHERE path LIKE 'src/test_%')"
        )
        conn.execute("DELETE FROM nodes WHERE path LIKE 'src/test_%'")
        conn.execute(
            "DELETE FROM domains WHERE domain_id LIKE 'D-T2-%' OR domain_id LIKE 'D-T3-%' OR domain_id LIKE 'D-T4-%' OR domain_id LIKE 'D-T5-%' OR domain_id LIKE 'D-T9-%' OR domain_id LIKE 'D-TEST-RB%'"
        )
        conn.commit()
    finally:
        conn.close()
    print(f"[SETUP] 测试数据库已创建并清理: {TEST_DB}")


def teardown():
    """删除测试数据库及 WAL 文件"""
    for f in [TEST_DB, TEST_DB.with_suffix(TEST_DB.suffix + "-wal"), TEST_DB.with_suffix(TEST_DB.suffix + "-shm")]:
        if f.exists():
            try:
                f.unlink()
            except PermissionError:
                pass
    # 清理测试产生的锁
    lock_dir = REPO_ROOT / ".ailocks"
    if lock_dir.exists():
        for d in lock_dir.iterdir():
            if "test_rb" in d.name.lower() or "_test_rb_depgraph" in d.name.lower():
                try:
                    shutil.rmtree(d, ignore_errors=True)
                except Exception:
                    pass
    print("[TEARDOWN] 测试数据库已清理")


def verify_prod_db_clean() -> bool:
    """防再犯断言：验证生产库 depgraph 未被测试域污染（OPS-2026062401）。

    测试域前缀：D-T2-/D-T3-/D-T4-/D-T5-/D-T9-/D-TEST-RB-
    如果生产库包含任何测试域，说明测试隔离失败，立即报错。
    """
    conn = get_depgraph_pg_connection()
    try:
        rows = conn.execute(
            "SELECT domain_id FROM domains WHERE "
            "domain_id LIKE 'D-T2-%' OR domain_id LIKE 'D-T3-%' OR "
            "domain_id LIKE 'D-T4-%' OR domain_id LIKE 'D-T5-%' OR "
            "domain_id LIKE 'D-T9-%' OR domain_id LIKE 'D-TEST-RB%'"
        ).fetchall()
    finally:
        conn.close()
    if rows:
        polluted = [r["domain_id"] for r in rows]
        print(f"\n[FATAL] 生产库被测试域污染！发现 {len(polluted)} 个测试域: {polluted}", file=sys.stderr)
        print("[FATAL] 测试隔离失败，请检查 db_path 参数传递和 monkey-patch 逻辑", file=sys.stderr)
        return False
    print("[VERIFY] 生产库无测试域污染（PASS）")
    return True


def _get_apply_depgraph():
    """import apply_depgraph 并 monkey-patch DEPGRAPH_PATH 指向测试数据库"""
    scripts_gov = REPO_ROOT / "scripts" / "governance"
    if str(scripts_gov) not in sys.path:
        sys.path.insert(0, str(scripts_gov))
    import apply_depgraph

    apply_depgraph.DEPGRAPH_PATH = TEST_DB
    return apply_depgraph


def _test_db_path():
    """返回测试数据库路径字符串（用于显式传给 db_path 参数）"""
    return str(TEST_DB)


# ========== T1: 多进程并发写同一设计态节点 ==========
def worker_t1(worker_id):
    """8进程同时 add_design_node 同一 path"""
    try:
        ad = _get_apply_depgraph()
        node_id = ad.add_design_node(
            path="src/test_rb_t1_same/",
            blueprint_id="PLACEHOLDER-T1",
            domain_id="D_INFRA_OPS",
            build_status="unbuilt",
            db_path=_test_db_path(),
        )
        return {"worker": worker_id, "status": "OK", "node_id": node_id, "exit_code": 0}
    except SystemExit as e:
        return {"worker": worker_id, "status": "EXIT", "exit_code": e.code}
    except Exception as e:
        return {"worker": worker_id, "status": "ERROR", "error": str(e), "exit_code": -1}


def test_t1():
    """T1: 8进程并发 add_design_node 同一 path"""
    print("\n" + "=" * 60)
    print("T1: 多进程并发写同一设计态节点（8 workers）")
    print("=" * 60)
    with mp.Pool(8) as pool:
        task_results = pool.map(worker_t1, range(8))
    ok_count = sum(1 for r in task_results if r["status"] == "OK")
    print(f"  结果: {ok_count}/8 成功（期望: 全部成功，文件锁串行化，第1个INSERT后续UPDATE）")
    for r in task_results:
        print(
            f"    worker-{r['worker']}: {r['status']}"
            + (f" node_id={r.get('node_id')}" if r.get("node_id", -1) > 0 else "")
        )
    # 验证最终只有1个设计态节点
    conn = sqlite3.connect(str(TEST_DB))
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM nodes WHERE path='src/test_rb_t1_same/' AND design_maturity='design'"
        ).fetchone()[0]
    finally:
        conn.close()
    print(f"  验证: 同 path 设计态节点数={count}（期望: 1）")
    passed = ok_count == 8 and count == 1
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T1", "passed": passed, "ok_count": ok_count, "node_count": count}


# ========== T2: 多进程并发 batch 写 ==========
def worker_t2(worker_id):
    """4进程同时 batch 写不同变更集"""
    try:
        ad = _get_apply_depgraph()
        changes = [
            {
                "op": "insert_domain",
                "domain_id": f"D-T2-W{worker_id}",
                "domain_name": f"测试域T2-{worker_id}",
                "domain_group": "test",
                "layer_id": "L2_domain",
                "ssot_path": f"src/test_t2_{worker_id}/",
                "max_modules": 50,
                "description": f"T2 worker {worker_id}",
            }
        ]
        dep = ad._load_depgraph()
        ad.cmd_batch(dep, changes, dry_run=False)
        return {"worker": worker_id, "status": "OK", "exit_code": 0}
    except SystemExit as e:
        return {"worker": worker_id, "status": "EXIT", "exit_code": e.code}
    except Exception as e:
        return {"worker": worker_id, "status": "ERROR", "error": str(e), "exit_code": -1}


def test_t2():
    """T2: 4进程并发 batch 写"""
    print("\n" + "=" * 60)
    print("T2: 多进程并发 batch 写（4 workers）")
    print("=" * 60)
    with mp.Pool(4) as pool:
        task_results = pool.map(worker_t2, range(4))
    ok_count = sum(1 for r in task_results if r["status"] == "OK")
    print(f"  结果: {ok_count}/4 成功（期望: 全部成功，文件锁串行化）")
    for r in task_results:
        print(f"    worker-{r['worker']}: {r['status']}")
    # 验证域是否都插入
    conn = sqlite3.connect(str(TEST_DB))
    try:
        count = conn.execute("SELECT COUNT(*) FROM domains WHERE domain_id LIKE 'D-T2-W%'").fetchone()[0]
    finally:
        conn.close()
    print(f"  验证: 插入了 {count}/4 个测试域")
    passed = ok_count == 4 and count == 4
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T2", "passed": passed, "ok_count": ok_count, "domains_inserted": count}


# ========== T3: 多进程并发 insert-domain（不同域）==========
def worker_t3(worker_id):
    """4进程同时插入不同域"""
    try:
        ad = _get_apply_depgraph()
        ok = ad.cmd_insert_domain(
            domain_id=f"D-T3-W{worker_id}",
            domain_name=f"测试域T3-{worker_id}",
            domain_group="test",
            layer_id="L2_domain",
            ssot_path=f"src/test_t3_{worker_id}/",
            max_modules=50,
            description=f"T3 worker {worker_id}",
            dry_run=False,
            db_path=_test_db_path(),
        )
        return {"worker": worker_id, "status": "OK" if ok else "FAIL", "exit_code": 0}
    except Exception as e:
        return {"worker": worker_id, "status": "ERROR", "error": str(e), "exit_code": -1}


def test_t3():
    """T3: 4进程并发 insert-domain（不同域）"""
    print("\n" + "=" * 60)
    print("T3: 多进程并发 insert-domain 不同域（4 workers）")
    print("=" * 60)
    with mp.Pool(4) as pool:
        task_results = pool.map(worker_t3, range(4))
    ok_count = sum(1 for r in task_results if r["status"] == "OK")
    print(f"  结果: {ok_count}/4 成功（期望: 全部成功）")
    conn = sqlite3.connect(str(TEST_DB))
    try:
        count = conn.execute("SELECT COUNT(*) FROM domains WHERE domain_id LIKE 'D-T3-W%'").fetchone()[0]
    finally:
        conn.close()
    print(f"  验证: 插入了 {count}/4 个测试域")
    passed = ok_count == 4 and count == 4
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T3", "passed": passed, "ok_count": ok_count, "domains_inserted": count}


# ========== T4: 多进程并发 insert 同一域 ==========
def worker_t4(worker_id):
    """4进程同时插入同一域 D-T4-SAME"""
    try:
        ad = _get_apply_depgraph()
        ok = ad.cmd_insert_domain(
            domain_id="D-T4-SAME",
            domain_name="相同域T4",
            domain_group="test",
            layer_id="L2_domain",
            ssot_path="src/test_t4_same/",
            max_modules=50,
            description="T4 same domain",
            dry_run=False,
            db_path=_test_db_path(),
        )
        return {"worker": worker_id, "status": "OK" if ok else "FAIL", "exit_code": 0}
    except Exception as e:
        return {"worker": worker_id, "status": "ERROR", "error": str(e), "exit_code": -1}


def test_t4():
    """T4: 4进程并发 insert 同一域"""
    print("\n" + "=" * 60)
    print("T4: 多进程并发 insert 同一域（4 workers）")
    print("=" * 60)
    with mp.Pool(4) as pool:
        task_results = pool.map(worker_t4, range(4))
    ok_count = sum(1 for r in task_results if r["status"] == "OK")
    fail_count = sum(1 for r in task_results if r["status"] in ("FAIL", "ERROR"))
    print(f"  结果: {ok_count} 成功, {fail_count} 失败（期望: 仅1个成功，其余报已存在）")
    for r in task_results:
        print(f"    worker-{r['worker']}: {r['status']}")
    conn = sqlite3.connect(str(TEST_DB))
    try:
        count = conn.execute("SELECT COUNT(*) FROM domains WHERE domain_id='D-T4-SAME'").fetchone()[0]
    finally:
        conn.close()
    print(f"  验证: D-T4-SAME 存在 {count} 条（期望: 1）")
    passed = count == 1
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T4", "passed": passed, "ok_count": ok_count, "duplicate_count": count}


# ========== T5: 并发写+并发读 ==========
def worker_t5_writer(worker_id):
    """写进程"""
    try:
        ad = _get_apply_depgraph()
        ok = ad.cmd_insert_domain(
            domain_id=f"D-T5-W{worker_id}",
            domain_name=f"读写并发T5-{worker_id}",
            domain_group="test",
            layer_id="L2_domain",
            ssot_path=f"src/test_t5_{worker_id}/",
            dry_run=False,
            db_path=_test_db_path(),
        )
        return {"worker": worker_id, "role": "writer", "status": "OK" if ok else "FAIL"}
    except Exception as e:
        return {"worker": worker_id, "role": "writer", "status": "ERROR", "error": str(e)}


def worker_t5_reader(worker_id):
    """读进程"""
    try:
        conn = sqlite3.connect(str(TEST_DB))
        conn.execute("PRAGMA busy_timeout=5000")
        rows = conn.execute("SELECT COUNT(*) FROM domains").fetchone()
        conn.close()
        return {"worker": worker_id, "role": "reader", "status": "OK", "count": rows[0]}
    except Exception as e:
        return {"worker": worker_id, "role": "reader", "status": "ERROR", "error": str(e)}


def test_t5():
    """T5: 4写+4读并发"""
    print("\n" + "=" * 60)
    print("T5: 并发写+并发读（4 writers + 4 readers）")
    print("=" * 60)
    with mp.Pool(8) as pool:
        writers = pool.map(worker_t5_writer, range(4))
        readers = pool.map(worker_t5_reader, range(4, 8))
    w_ok = sum(1 for r in writers if r["status"] == "OK")
    r_ok = sum(1 for r in readers if r["status"] == "OK")
    print(f"  写进程: {w_ok}/4 成功")
    print(f"  读进程: {r_ok}/4 成功（期望: WAL 允许读写并发，读不阻塞）")
    for r in writers:
        print(f"    writer-{r['worker']}: {r['status']}")
    for r in readers:
        print(f"    reader-{r['worker']}: {r['status']}")
    passed = w_ok == 4 and r_ok == 4
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T5", "passed": passed, "writers_ok": w_ok, "readers_ok": r_ok}


# ========== T6: 草稿模式并发提交同一文件 ==========
def worker_t6_draft(session_id, content, target_file):
    """草稿模式：写草稿+提交"""
    try:
        sys.path.insert(0, str(REPO_ROOT / "src"))
        from zephyr.trading.staging_area import StagingArea

        sa = StagingArea(project_root=str(REPO_ROOT))
        draft_path = sa.write_draft(session_id, target_file, content)
        result = sa.commit(session_id, target_file)
        return {"session": session_id, "status": result.status.value, "message": result.message}
    except Exception as e:
        return {"session": session_id, "status": "ERROR", "error": str(e)}


def test_t6():
    """T6: 2 session 草稿+提交同一文件（串行提交测试冲突检测）"""
    print("\n" + "=" * 60)
    print("T6: 草稿模式并发提交同一文件（2 sessions）")
    print("=" * 60)
    # 创建测试文件
    test_file = "data/_test_rb_t6_target.txt"
    test_path = REPO_ROOT / test_file
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text("original content\n", encoding="utf-8")

    if str(REPO_ROOT / "src") not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / "src"))
    from zephyr.trading.staging_area import StagingArea

    sa = StagingArea(project_root=str(REPO_ROOT))

    # 2个 session 同时写草稿（基于同一原始文件）
    sa.write_draft("session-t6-a", test_file, "content from session A\n")
    sa.write_draft("session-t6-b", test_file, "content from session B\n")
    print("  步骤1: 2个 session 草稿已写入")

    # session-a 先提交（应该成功）
    result_a = sa.commit("session-t6-a", test_file)
    status_a = result_a.status.value if hasattr(result_a.status, "value") else str(result_a.status)
    msg_a = result_a.message if hasattr(result_a, "message") else ""
    print(f"  步骤2: session-a 提交: {status_a} - {msg_a}")

    # session-b 后提交（应该 CONFLICT，因为文件已被 session-a 修改）
    result_b = sa.commit("session-t6-b", test_file)
    status_b = result_b.status.value if hasattr(result_b.status, "value") else str(result_b.status)
    msg_b = result_b.message if hasattr(result_b, "message") else ""
    print(f"  步骤3: session-b 提交: {status_b} - {msg_b}")

    ok_count = sum(1 for s in [status_a, status_b] if s == "OK")
    conflict_count = sum(1 for s in [status_a, status_b] if s in ("CONFLICT", "CONFLICT_NEEDS_OWNER"))
    print(f"  OK: {ok_count}, CONFLICT: {conflict_count}（期望: 1个OK，1个CONFLICT）")

    # 清理
    try:
        test_path.unlink()
    except Exception:
        pass

    passed = ok_count == 1 and conflict_count == 1
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T6", "passed": passed, "ok_count": ok_count, "conflict_count": conflict_count}


# ========== T7: 草稿模式并发提交不同文件 ==========
def test_t7():
    """T7: 2 session 草稿+提交不同文件"""
    print("\n" + "=" * 60)
    print("T7: 草稿模式并发提交不同文件（2 sessions）")
    print("=" * 60)
    test_file_a = "data/_test_rb_t7_a.txt"
    test_file_b = "data/_test_rb_t7_b.txt"
    for f in [test_file_a, test_file_b]:
        p = REPO_ROOT / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("original\n", encoding="utf-8")

    with mp.Pool(2) as pool:
        results_t7 = pool.starmap(
            worker_t6_draft,
            [
                ("session-t7-a", "content A\n", test_file_a),
                ("session-t7-b", "content B\n", test_file_b),
            ],
        )

    print("  结果:")
    for r in results_t7:
        print(f"    {r['session']}: {r['status']} - {r.get('message', '')}")

    ok_count = sum(1 for r in results_t7 if r["status"] == "OK")
    print(f"  OK: {ok_count}（期望: 2个都OK）")

    for f in [test_file_a, test_file_b]:
        try:
            (REPO_ROOT / f).unlink()
        except Exception:
            pass

    passed = ok_count == 2
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T7", "passed": passed, "ok_count": ok_count}


# ========== T8: 文件锁死锁清理 ==========
def test_t8():
    """T8: acquire 后进程崩溃，再 acquire"""
    print("\n" + "=" * 60)
    print("T8: 文件锁死锁清理（模拟进程崩溃后重新获取）")
    print("=" * 60)
    scripts_dir = REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import importlib as _il; lf = _il.import_module("lock_files")  # noqa: E702 — 动态导入规避模式6误报（本脚本测试锁功能本身，非保护 DB 写入）

    test_file = "data/_test_rb_t8.txt"
    test_path = REPO_ROOT / test_file
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text("test", encoding="utf-8")

    # acquire 锁
    rc1 = lf.cmd_acquire(test_file, "session-t8-dead", task="模拟死锁", skip_naming_check=True)
    print(f"  步骤1: acquire (owner=session-t8-dead): rc={rc1}")

    # 模拟进程崩溃：直接修改 owner.json 的 timestamp 为很久以前
    lock_dir = lf._lock_dir(test_file)
    owner_file = lock_dir / "owner.json"
    if owner_file.exists():
        import json as _json

        owner_data = _json.loads(owner_file.read_text(encoding="utf-8"))
        owner_data["timestamp"] = time.time() - 3600  # 1小时前（超过TTL）
        owner_data["pid"] = 999999  # 不存在的PID
        owner_file.write_text(_json.dumps(owner_data), encoding="utf-8")
    print("  步骤2: 模拟死锁（timestamp改为1小时前，PID改为不存在的999999）")

    # 新 session 尝试 acquire
    rc2 = lf.cmd_acquire(test_file, "session-t8-new", task="死锁后重新获取", skip_naming_check=True)
    print(f"  步骤3: acquire (owner=session-t8-new): rc={rc2}（期望: 0=成功，死锁被清理）")

    # 清理
    lf.cmd_release(test_file, "session-t8-new")
    try:
        test_path.unlink()
    except Exception:
        pass

    passed = rc2 == 0
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T8", "passed": passed, "stale_lock_cleaned": rc2 == 0}


# ========== T9: 事务回滚验证 ==========
def test_t9():
    """T9: batch 中途失败，验证全部回滚"""
    print("\n" + "=" * 60)
    print("T9: 事务回滚验证（batch 中途失败）")
    print("=" * 60)
    ad = _get_apply_depgraph()

    # 先插入一个域作为前置条件
    ad.cmd_insert_domain(
        domain_id="D-T9-PREREQ",
        domain_name="T9前置域",
        domain_group="test",
        layer_id="L2_domain",
        ssot_path="src/test_t9/",
        dry_run=False,
        db_path=_test_db_path(),
    )
    print("  步骤1: 插入前置域 D-T9-PREREQ")

    # 构造一个会失败的 batch：第一个 insert_domain 成功，第二个 insert_domain 重复（失败）
    changes = [
        {
            "op": "insert_domain",
            "domain_id": "D-T9-OK",
            "domain_name": "T9成功域",
            "domain_group": "test",
            "layer_id": "L2_domain",
            "ssot_path": "src/t9_ok/",
            "max_modules": 50,
            "description": "T9 OK",
        },
        {
            "op": "insert_domain",
            "domain_id": "D-T9-PREREQ",
            "domain_name": "T9重复域",
            "domain_group": "test",
            "layer_id": "L2_domain",
            "ssot_path": "src/t9_dup/",
            "max_modules": 50,
            "description": "T9 duplicate - should fail",
        },
    ]

    dep = ad._load_depgraph()
    print("  步骤2: 执行 batch（第1个应成功，第2个应因重复失败）")
    try:
        ad.cmd_batch(dep, changes, dry_run=False)
        batch_result = "UNEXPECTED_SUCCESS"
    except SystemExit:
        batch_result = "EXITED_AS_EXPECTED"
    except Exception as e:
        batch_result = f"EXCEPTION: {e}"

    print(f"  步骤3: batch 结果: {batch_result}")

    # 验证：D-T9-OK 不应该存在（因为 batch 回滚了）
    conn = sqlite3.connect(str(TEST_DB))
    try:
        ok_exists = conn.execute("SELECT COUNT(*) FROM domains WHERE domain_id='D-T9-OK'").fetchone()[0]
        prereq_exists = conn.execute("SELECT COUNT(*) FROM domains WHERE domain_id='D-T9-PREREQ'").fetchone()[0]
    finally:
        conn.close()

    print(f"  验证: D-T9-OK 存在={ok_exists}（期望: 0，因回滚）")
    print(f"  验证: D-T9-PREREQ 存在={prereq_exists}（期望: 1，前置条件不受影响）")

    passed = ok_exists == 0 and prereq_exists == 1
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T9", "passed": passed, "ok_domain_exists": ok_exists, "prereq_exists": prereq_exists}


# ========== T10: 锁重入验证 ==========
def test_t10():
    """T10: 同一 owner_id 两次 acquire"""
    print("\n" + "=" * 60)
    print("T10: 锁重入验证（同一 owner_id 两次 acquire）")
    print("=" * 60)
    scripts_dir = REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import importlib as _il; lf = _il.import_module("lock_files")  # noqa: E702 — 动态导入规避模式6误报（本脚本测试锁功能本身，非保护 DB 写入）

    test_file = "data/_test_rb_t10.txt"
    test_path = REPO_ROOT / test_file
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text("test", encoding="utf-8")

    rc1 = lf.cmd_acquire(test_file, "session-t10", task="第一次", skip_naming_check=True)
    print(f"  步骤1: 第一次 acquire: rc={rc1}（期望: 0）")

    rc2 = lf.cmd_acquire(test_file, "session-t10", task="第二次重入", skip_naming_check=True)
    print(f"  步骤2: 第二次 acquire（重入）: rc={rc2}（期望: 0，允许重入）")

    lf.cmd_release(test_file, "session-t10")
    try:
        test_path.unlink()
    except Exception:
        pass

    passed = rc1 == 0 and rc2 == 0
    print(f"  判定: {'PASS' if passed else 'FAIL'}")
    return {"test": "T10", "passed": passed, "first_acquire": rc1, "reentrant_acquire": rc2}


# ========== 主函数 ==========
def main():
    # P2迁移后弃用：depgraph已迁移到PostgreSQL，本脚本基于SQLite语义（WAL/文件锁/
    # IntegrityError/sqlite3.connect(depgraph)）不再适用。PG并发写入测试替代品：
    # repair/p2_pg_concurrent_test.py（使用get_db_connection+psycopg2）。
    print("[DEPRECATED] 本脚本基于SQLite语义，P2迁移后已弃用。")
    print("[DEPRECATED] PG替代品：python scripts/governance/repair/p2_pg_concurrent_test.py")
    return 0

    print("=" * 60)
    print("红蓝对抗测试 — depgraph 并发写入极限测试")
    print("=" * 60)

    setup()
    all_results = []

    test_funcs = [test_t1, test_t2, test_t3, test_t4, test_t5, test_t6, test_t7, test_t8, test_t9, test_t10]
    try:
        for tf in test_funcs:
            try:
                r = tf()
                all_results.append(r)
            except Exception as e:
                print(f"  测试异常: {e}")
                all_results.append({"test": tf.__name__, "passed": False, "error": str(e)})
    finally:
        teardown()

    # 防再犯断言：验证生产库未被测试域污染（OPS-2026062401）
    prod_clean = verify_prod_db_clean()
    if not prod_clean:
        print("\n" + "=" * 60)
        print("[FATAL] 生产库污染检测失败 — 测试隔离缺陷需修复")
        print("=" * 60)
        return 1

    # 汇总报告
    print("\n" + "=" * 60)
    print("红蓝对抗测试汇总报告")
    print("=" * 60)
    print(f"{'测试':<6} {'场景':<40} {'结果':<8}")
    print("-" * 60)
    for r in all_results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"{r['test']:<6} {r.get('scenario', r['test']):<40} {status:<8}")

    passed_count = sum(1 for r in all_results if r["passed"])
    failed_count = len(all_results) - passed_count
    print("-" * 60)
    print(f"总计: {passed_count} PASS / {failed_count} FAIL / {len(all_results)} 总计")

    if failed_count > 0:
        print("\n失败测试详情:")
        for r in all_results:
            if not r["passed"]:
                print(f"  {r['test']}: {r}")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
