#!/usr/bin/env python3
"""
DM-014: 孤儿节点补边 v3 —— 增加 test 文件文件名匹配策略

策略:
  1. import 分析（含 importorskip）
  2. __init__.py contains 边
  3. 非 .py sibling 边
  4. 【NEW】test 文件按文件名匹配源文件（去掉test_前缀）
  5. 【NEW】script 文件按父目录匹配
"""

import os
import re
import sqlite3
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DB_PATH = "data/databases/depgraph.db"
PROJECT_ROOT = Path(".")
_MAX_WORKERS = 8

RE_IMPORT_ZEPHYR = re.compile(
    r"(?:^|\n)\s*(?:from\s+(zephyr(?:\.[a-zA-Z_]\w*)+)\s+import|import\s+(zephyr(?:\.[a-zA-Z_]\w*)+))", re.MULTILINE
)
RE_IMPORTORSKIP = re.compile(r'pytest\.importorskip\(\s*["\'](zephyr(?:\.[a-zA-Z_]\w*)+)["\']', re.MULTILINE)


def _parse_imports(file_path: str) -> list[str]:
    full_path = PROJECT_ROOT / file_path
    if not full_path.exists():
        return []
    try:
        content = full_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    imports = set()
    for m in RE_IMPORT_ZEPHYR.finditer(content):
        pkg = m.group(1) or m.group(2)
        if pkg:
            imports.add(pkg)
    for m in RE_IMPORTORSKIP.finditer(content):
        pkg = m.group(1)
        if pkg:
            imports.add(pkg)
    return list(imports)


def _build_target_map(conn):
    rows = conn.execute(
        "SELECT node_id, file_path FROM nodes WHERE file_path IS NOT NULL AND file_path != ''"
    ).fetchall()
    target_map = {}
    name_to_node = {}  # 文件名 -> node_id (用于test匹配)
    for node_id, file_path in rows:
        if file_path.startswith("src/zephyr/") and file_path.endswith(".py"):
            pkg_part = file_path[len("src/zephyr/") : -3].replace("/", ".").replace("\\", ".")
            target_map[f"zephyr.{pkg_part}"] = node_id
        if file_path.endswith("__init__.py") and file_path.startswith("src/zephyr/"):
            pkg_dir = file_path[len("src/zephyr/") : -len("__init__.py")].rstrip("/").rstrip("\\")
            if pkg_dir:
                target_map[f"zephyr.{pkg_dir.replace('/', '.').replace(chr(92), '.')}"] = node_id
        # 文件名匹配映射
        basename = os.path.basename(file_path)
        if basename not in name_to_node:
            name_to_node[basename] = node_id
    return target_map, name_to_node


def main():
    conn = sqlite3.connect(DB_PATH)
    target_map, name_to_node = _build_target_map(conn)

    remaining = conn.execute("""
        SELECT n.node_id, n.node_type, n.domain_id, n.file_path
        FROM nodes n
        WHERE n.design_maturity != 'design'
        AND n.node_type NOT IN ('contract','event','invariant')
        AND n.node_id NOT IN (SELECT from_node FROM edges)
        AND n.node_id NOT IN (SELECT to_node FROM edges)
    """).fetchall()

    print(f"[DM-014 v3] 剩余孤儿: {len(remaining)}")

    edges_to_add = []

    # --- 策略1: import 分析 ---
    py_orphans = [(nid, fp) for nid, ntype, _, fp in remaining if fp and fp.endswith(".py")]
    print(f"[DM-014 v3] import分析: {len(py_orphans)} .py孤儿")
    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {executor.submit(_parse_imports, fp): (nid, fp) for nid, fp in py_orphans}
        for future in as_completed(futures):
            nid, fp = futures[future]
            for pkg in future.result():
                if pkg in target_map:
                    edges_to_add.append((nid, target_map[pkg], "import", "weak"))
                else:
                    parts = pkg.split(".")
                    for i in range(len(parts) - 1, 0, -1):
                        shorter = ".".join(parts[:i])
                        if shorter in target_map:
                            edges_to_add.append((nid, target_map[shorter], "import", "weak"))
                            break

    # --- 策略2: test 文件名匹配 ---
    test_orphans = [(nid, fp) for nid, ntype, _, fp in remaining if ntype == "test" and fp]
    print(f"[DM-014 v3] test文件名匹配: {len(test_orphans)} test孤儿")
    for nid, fp in test_orphans:
        basename = os.path.basename(fp)
        # tests/test_a2a_anomaly_detector.py -> a2a_anomaly_detector.py
        if basename.startswith("test_"):
            candidate_name = basename[5:]  # remove "test_"
            if candidate_name in name_to_node:
                edges_to_add.append((nid, name_to_node[candidate_name], "test", "weak"))

    # --- 策略3: contains 边 + belongs_to 属性（替代 sibling 边） ---
    all_nodes = conn.execute(
        "SELECT node_id, file_path FROM nodes WHERE file_path IS NOT NULL AND file_path != ''"
    ).fetchall()
    dir_to_nodes = defaultdict(list)
    for nid, fp in all_nodes:
        if fp:
            dir_to_nodes[os.path.dirname(fp)].append(nid)

    belongs_to_updates = []
    for nid, ntype, _, fp in remaining:
        if not fp:
            continue
        dir_path = os.path.dirname(fp)
        if fp.endswith("__init__.py"):
            # contains 边保留（__init__.py 对同目录文件的关系）
            for sib in dir_to_nodes.get(dir_path, []):
                if sib != nid:
                    edges_to_add.append((nid, sib, "contains", "weak"))
        else:
            # DM-019: 用 belongs_to 节点属性替代 sibling 边，避免 O(n²) 膨胀
            belongs_to_updates.append((nid, f"same_dir:{dir_path}"))

    # 批量更新 belongs_to 属性
    if belongs_to_updates:
        conn.executemany(
            "UPDATE nodes SET belongs_to = ? WHERE node_id = ?",
            [(bt, nid) for nid, bt in belongs_to_updates],
        )
        print(f"[DM-014 v3] 更新 belongs_to 属性: {len(belongs_to_updates)} 节点")

    # 去重+插入
    unique = list(set(edges_to_add))
    print(f"[DM-014 v3] 候选边: {len(unique)}")
    added = 0
    skipped = 0
    for from_node, to_node, dep_type, coupling_strength in unique:
        if from_node == to_node:
            skipped += 1
            continue
        try:
            conn.execute(
                "INSERT INTO edges (from_node, to_node, dep_type, coupling_strength) VALUES (?, ?, ?, ?)",
                (from_node, to_node, dep_type, coupling_strength),
            )
            added += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    print(f"[DM-014 v3] 新增边: {added}, 跳过: {skipped}")

    # 验证
    remaining_count = conn.execute("""
        SELECT COUNT(*) FROM nodes n
        WHERE n.design_maturity != 'design'
        AND n.node_type NOT IN ('contract','event','invariant')
        AND n.node_id NOT IN (SELECT from_node FROM edges)
        AND n.node_id NOT IN (SELECT to_node FROM edges)
    """).fetchone()[0]

    total_eligible = conn.execute("""
        SELECT COUNT(*) FROM nodes n
        WHERE n.design_maturity != 'design'
        AND n.node_type NOT IN ('contract','event','invariant')
    """).fetchone()[0]

    orphan_rate = remaining_count / total_eligible * 100 if total_eligible else 0
    total_edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

    print("\n[DM-014 v3] ===== 补边结果 =====")
    print(f"剩余孤儿: {remaining_count}")
    print(f"可补边总数: {total_eligible}")
    print(f"孤儿率: {orphan_rate:.1f}%")
    print(f"总边数: {total_edges}")

    conn.close()

    if orphan_rate < 5.0:
        print("[DM-014 v3] PASS: 孤儿率 < 5%")
        sys.exit(0)
    else:
        print(f"[DM-014 v3] FAIL: 孤儿率 {orphan_rate:.1f}% >= 5%")
        sys.exit(1)


if __name__ == "__main__":
    import sys

    sys.exit("DEPRECATED: 此脚本已归档，depgraph.db 已迁移至 PostgreSQL 16")
    main()
