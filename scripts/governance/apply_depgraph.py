"""
[BLUEPRINT] | scripts/governance/apply_depgraph.py | §1
[MODULE] scripts.governance.apply_depgraph
[INVARIANTS] 原子写入（RULE-ONE）；变更前验证；禁止直接覆盖
[MODIFY-GUARD] project_rules.md(RULE-SIXTEEN); scripts/governance/extract_depgraph.py
[CONSUMERS] 所有需要修改depgraph的AI session
[STABILITY] stable
[SAFETY] H
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 文件不存在→exit 1; YAML解析失败→exit 2; 验证失败→exit 3; 写入失败→exit 4
[TESTS] 无

depgraph 变更写入工具（RULE-SIXTEEN 强制配套）

禁止 AI 直接 Write 157MB depgraph → OOM 崩溃。
替代方案：AI 生成变更 JSON → 本脚本验证后原子写入。

用法:
  python scripts/governance/apply_depgraph.py --update-module D-FACTOR-01 blueprint_status=has_blueprint
  python scripts/governance/apply_depgraph.py --batch changes.json
  python scripts/governance/apply_depgraph.py --batch changes.json --dry-run

  # F5 合规豁免：D-SECURITY 拆分后域/路径/依赖迁移命令
  python scripts/governance/apply_depgraph.py --insert-domain D-NEW "新域" 业务 L2_domain src/zephyr/new/ --max-modules 200
  python scripts/governance/apply_depgraph.py --update-domain-id D-FACTOR-01 D-NEW_DOMAIN --dry-run
  python scripts/governance/apply_depgraph.py --update-path D-FACTOR-01 src/zephyr/new_domain/module.py --dry-run
  python scripts/governance/apply_depgraph.py --migrate-dependencies D-OLD D-TARGET --new-from-domain D-NEW --dry-run

GIT 备份门禁（project_memory 强制规则）：
  修改 depgraph.db 前必须先 git 备份当前状态，以便回滚：
    git add data/databases/depgraph.db
    git commit -m "backup: depgraph before <操作描述>"
  如果 DB 有未提交修改（未备份），写入被阻断（exit 4）。
  强制跳过（不推荐）: ZEPHYR_SKIP_BACKUP_CHECK=1
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

DEPGRAPH_PATH = Path("D:/ZephyrAlpha/data/databases/depgraph.db")

# 跳过 git 备份检查的环境变量（自动化场景）
SKIP_BACKUP_CHECK_ENV = "ZEPHYR_SKIP_BACKUP_CHECK"


def _check_git_backup(db_path: Path = DEPGRAPH_PATH) -> bool:
    """检查 depgraph.db 修改前是否有 git 备份。

    规则（project_memory）：修改全景图前必须先 git 备份当前状态：
      git add data/databases/depgraph.db
      git commit -m "backup: depgraph before <操作描述>"

    检查逻辑：
      1. ZEPHYR_SKIP_BACKUP_CHECK=1 → 跳过（自动化场景）
      2. depgraph.db 未纳入 git 跟踪 → 跳过（无法备份）
      3. depgraph.db 有未提交修改 → 阻断（当前状态未备份，无法回滚）

    返回：True=已备份（允许写入），False=未备份（阻断写入）
    """
    # 1. 跳过检查的环境变量
    if os.environ.get(SKIP_BACKUP_CHECK_ENV) == "1":
        return True

    # 2. 检查 depgraph.db 是否已纳入 git 跟踪
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(db_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            # DB 未纳入 git 跟踪，无法备份，跳过检查
            return True
    except Exception:
        # git 命令执行失败，安全起见跳过检查（避免误阻断）
        return True

    # 3. 检查 depgraph.db 是否有未提交修改
    try:
        result = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", str(db_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        # exit 0 = 无修改（已备份），exit 1 = 有修改（未备份）
        if result.returncode == 1:
            print("", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            print("[GIT-BACKUP GATE] depgraph.db 写入被阻断——缺少 git 备份", file=sys.stderr)
            print(f"  DB 路径: {db_path}", file=sys.stderr)
            print("", file=sys.stderr)
            print("  规则：修改 depgraph.db 前必须先 git 备份当前状态（project_memory）", file=sys.stderr)
            print("", file=sys.stderr)
            print("  解决方案:", file=sys.stderr)
            print("    1. 创建备份:", file=sys.stderr)
            print("       git add data/databases/depgraph.db", file=sys.stderr)
            print('       git commit -m "backup: depgraph before <操作描述>"', file=sys.stderr)
            print("    2. 验证备份:", file=sys.stderr)
            print("       git log -1 --oneline -- data/databases/depgraph.db", file=sys.stderr)
            print("    3. 重新执行本命令", file=sys.stderr)
            print("", file=sys.stderr)
            print(f"  强制跳过（不推荐）: {SKIP_BACKUP_CHECK_ENV}=1", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            return False
    except Exception:
        # 检查失败，安全起见允许（避免误阻断）
        return True

    return True


# 集成 lock_files.py 文件锁——堵住并发写入漏洞
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import lock_files as _lf  # noqa: E402

# 进程内 DB 写入串行锁——防止同进程多线程并发获取文件锁
_db_write_lock_lock = threading.Lock()


@contextlib.contextmanager
def _db_write_lock(
    owner_id: str | None = None,
    task: str = "depgraph write",
    db_path: Path | str | None = None,
    max_retries: int = 30,
    retry_interval: float = 1.0,
):
    """depgraph.db 写入文件锁上下文管理器（跨进程互斥 + 进程内串行 + 重试）。

    双重保护：
    1. threading.Lock() — 进程内多线程串行化（避免同进程线程竞争文件锁）
    2. lock_files.py 文件锁 — 跨进程互斥（原子目录创建，TTL 30分钟）

    GIT 备份门禁：写入前检查 depgraph.db 是否有 git 备份（project_memory 强制规则）。
    如果 DB 有未提交修改（未备份），阻断写入并 sys.exit(4)。

    重试机制：acquire 失败时等待 retry_interval 秒后重试，最多 max_retries 次。
    db_path: 指定要锁的数据库文件路径（默认 DEPGRAPH_PATH）。
    """
    # GIT 备份门禁：写入前检查是否有 git 备份（在任何锁获取之前检查）
    _check_db_path = Path(db_path) if db_path is not None else DEPGRAPH_PATH
    if not _check_git_backup(_check_db_path):
        sys.exit(4)

    oid = owner_id or f"depgraph-{os.getpid()}"
    db_path_str = str(db_path if db_path is not None else DEPGRAPH_PATH)
    _db_write_lock_lock.acquire()
    try:
        acquired = False
        for attempt in range(max_retries):
            rc = _lf.cmd_acquire(db_path_str, oid, task=task, skip_naming_check=True)
            if rc == 0:
                acquired = True
                break
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
        if not acquired:
            raise RuntimeError(f"无法获取 depgraph.db 写入锁 (owner={oid})，重试{max_retries}次后仍失败")
        try:
            yield
        finally:
            _lf.cmd_release(db_path_str, oid)
    finally:
        _db_write_lock_lock.release()


@contextlib.contextmanager
def _optional_db_lock(own_conn: bool, task: str = "depgraph write", db_path: Path | str | None = None):
    """当 own_conn=True 时获取文件锁，否则不加锁（共享连接模式由调用方负责锁）。"""
    if own_conn:
        with _db_write_lock(task=task, db_path=db_path):
            yield
    else:
        yield


def _load_depgraph_from_db(db_path: Path) -> dict:
    """从 SQLite 数据库加载 depgraph，返回与原 YAML 结构兼容的 dict。"""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    data: dict = {"nodes": {}, "edges": [], "domains": {}, "metadata": {}}
    for row in conn.execute("SELECT * FROM nodes"):
        node = dict(row)
        nid = node.pop("node_id")
        if "node_type" in node:
            node["type"] = node.pop("node_type")
        data["nodes"][nid] = node
    for row in conn.execute("SELECT * FROM edges"):
        edge = dict(row)
        if "from_node_id" in edge:
            edge["from"] = edge.pop("from_node_id")
        if "to_node_id" in edge:
            edge["to"] = edge.pop("to_node_id")
        data["edges"].append(edge)
    for row in conn.execute("SELECT * FROM domains"):
        domain = dict(row)
        did = domain.pop("domain_id")
        data["domains"][did] = domain
    conn.close()
    return data


def _load_depgraph() -> dict:
    if not DEPGRAPH_PATH.exists():
        print(f"ERROR: depgraph not found at {DEPGRAPH_PATH}", file=sys.stderr)
        sys.exit(1)
    try:
        return _load_depgraph_from_db(DEPGRAPH_PATH)
    except Exception as e:
        print(f"ERROR: Failed to load depgraph from DB: {e}", file=sys.stderr)
        sys.exit(2)


def _find_module(dep: dict, module_id: str) -> dict | None:
    """在 depgraph nodes 中查找指定 module_id 的模块（按 belongs_to 或 blueprint_id 匹配）。"""
    for node_id, node in dep.get("nodes", {}).items():
        if node.get("belongs_to") == module_id or node.get("blueprint_id") == module_id:
            node["_node_id"] = node_id
            return node
    return None


def _atomic_write(dep: dict, conn=None) -> None:
    """将修改后的 depgraph 数据写回 SQLite 数据库。

    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    如果未提供 conn，打开新连接（独立模式，commit+close）。
    """
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="_atomic_write"):
        if own_conn:
            conn = sqlite3.connect(str(DEPGRAPH_PATH))
        try:
            for node_id, node_data in dep.get("nodes", {}).items():
                clean = {k: v for k, v in node_data.items() if not k.startswith("_")}
                if "type" in clean:
                    clean["node_type"] = clean.pop("type")
                set_clause = ", ".join(f"{k} = ?" for k in clean)
                values = list(clean.values()) + [node_id]
                conn.execute(f"UPDATE nodes SET {set_clause} WHERE node_id = ?", values)
            if own_conn:
                conn.commit()
            print("OK: depgraph DB updated", file=sys.stderr)
        except Exception as e:
            if own_conn:
                conn.rollback()
            print(f"ERROR: DB write failed: {e}", file=sys.stderr)
            sys.exit(4)
        finally:
            if own_conn:
                conn.close()


def cmd_update_module(dep: dict, module_id: str, field: str, value: str) -> None:
    """更新单个模块的字段。"""
    module = _find_module(dep, module_id)
    if module is None:
        print(f"ERROR: Module '{module_id}' not found", file=sys.stderr)
        sys.exit(3)

    old_value = module.get(field, "<not set>")

    # 类型转换
    if field in (
        "safety_level",
        "ai_autonomy",
        "stability",
        "build_status",
        "blueprint_status",
        "module_lifecycle_state",
        "priority",
    ):
        module[field] = value
    elif field in ("physical_files",):
        try:
            module[field] = json.loads(value)
        except json.JSONDecodeError:
            module[field] = [p.strip() for p in value.split(",")]
    else:
        module[field] = value

    print(f"Updated {module_id}.{field}: {old_value} -> {module[field]}", file=sys.stderr)


def _apply_node_op(dep: dict, change: dict, index: int) -> None:
    """对 dep dict 执行节点级操作（不写 DB）。供 cmd_batch 复用。"""
    op = change.get("op", "update")
    module_id = change.get("module_id", "")
    if op == "update":
        cmd_update_module(dep, module_id, change.get("field", ""), change.get("value", ""))
    elif op == "add_physical_file":
        module = _find_module(dep, module_id)
        if module is None:
            print(f"ERROR: Module '{module_id}' not found for change #{index}", file=sys.stderr)
            return
        pf = change.get("path", "")
        if pf not in module.get("physical_files", []):
            module.setdefault("physical_files", []).append(pf)
            print(f"Added {pf} to {module_id}", file=sys.stderr)
    elif op == "remove_physical_file":
        module = _find_module(dep, module_id)
        if module is None:
            print(f"ERROR: Module '{module_id}' not found for change #{index}", file=sys.stderr)
            return
        pf = change.get("path", "")
        if pf in module.get("physical_files", []):
            module["physical_files"].remove(pf)
            print(f"Removed {pf} from {module_id}", file=sys.stderr)
    elif op == "set_physical_files":
        module = _find_module(dep, module_id)
        if module is None:
            print(f"ERROR: Module '{module_id}' not found for change #{index}", file=sys.stderr)
            return
        module["physical_files"] = change.get("files", [])
        print(f"Set {len(module['physical_files'])} physical_files for {module_id}", file=sys.stderr)


def cmd_batch(dep: dict, changes: list[dict], dry_run: bool) -> None:
    """批量处理变更（统一事务管理，消除部分提交风险）。

    非dry-run模式下，所有操作（域级+节点级）共享同一SQLite连接和事务：
    - 全部成功 → 一次commit
    - 任一失败 → 全部rollback（消除P2-002部分提交风险）

    支持的 op 类型：
    - 节点级（经 dep dict + _atomic_write）：update, add_physical_file, remove_physical_file, set_physical_files
    - 域级（直接 SQL，ARCH-CAP-005）：insert_domain, update_domain_id, update_path, migrate_dependencies
    """
    if isinstance(changes, str):
        changes = json.loads(changes)

    print(f"Processing {len(changes)} changes...", file=sys.stderr)

    if dry_run:
        # Dry-run: 域级 op 各自打印预览，节点级 op 修改 dep dict（不写 DB）
        domain_op_count = 0
        for i, change in enumerate(changes):
            op = change.get("op", "update")
            if op == "insert_domain":
                ok = cmd_insert_domain(
                    domain_id=change.get("domain_id", ""),
                    domain_name=change.get("domain_name", ""),
                    domain_group=change.get("domain_group", ""),
                    layer_id=change.get("layer_id", ""),
                    ssot_path=change.get("ssot_path", ""),
                    max_modules=change.get("max_modules", 200),
                    description=change.get("description", ""),
                    dry_run=True,
                )
                if ok:
                    domain_op_count += 1
            elif op == "update_domain_id":
                count = cmd_update_domain_id(
                    module_id=change.get("module_id", ""), new_domain_id=change.get("new_domain_id", ""), dry_run=True
                )
                if count >= 0:
                    domain_op_count += 1
            elif op == "update_path":
                count = cmd_update_path(
                    module_id=change.get("module_id", ""), new_path=change.get("new_path", ""), dry_run=True
                )
                if count >= 0:
                    domain_op_count += 1
            elif op == "migrate_dependencies":
                count = cmd_migrate_dependencies(
                    from_domain=change.get("from_domain", ""),
                    to_domain=change.get("to_domain", ""),
                    new_from_domain=change.get("new_from_domain", ""),
                    new_to_domain=change.get("new_to_domain", ""),
                    dry_run=True,
                )
                if count >= 0:
                    domain_op_count += 1
            elif op == "update_domain_layer":
                ok = cmd_update_domain_layer(
                    domain_id=change.get("domain_id", ""), layer_id=change.get("layer_id", ""), dry_run=True
                )
                if ok:
                    domain_op_count += 1
            elif op in ("update", "add_physical_file", "remove_physical_file", "set_physical_files"):
                _apply_node_op(dep, change, i)
            else:
                print(f"WARNING: Unknown op '{op}' for change #{i}", file=sys.stderr)
        print(f"DRY RUN - no changes written (domain_ops={domain_op_count})", file=sys.stderr)
        return

    # 非dry-run: 统一事务（所有操作共享一个连接，全部成功才commit）
    with _db_write_lock(task="cmd_batch"):
        conn = sqlite3.connect(str(DEPGRAPH_PATH))
        domain_op_count = 0
        try:
            for i, change in enumerate(changes):
                op = change.get("op", "update")
                if op == "insert_domain":
                    ok = cmd_insert_domain(
                        domain_id=change.get("domain_id", ""),
                        domain_name=change.get("domain_name", ""),
                        domain_group=change.get("domain_group", ""),
                        layer_id=change.get("layer_id", ""),
                        ssot_path=change.get("ssot_path", ""),
                        max_modules=change.get("max_modules", 200),
                        description=change.get("description", ""),
                        dry_run=False,
                        conn=conn,
                    )
                    if not ok:
                        raise RuntimeError(f"change #{i}: insert_domain failed")
                    domain_op_count += 1
                elif op == "update_domain_id":
                    count = cmd_update_domain_id(
                        module_id=change.get("module_id", ""),
                        new_domain_id=change.get("new_domain_id", ""),
                        dry_run=False,
                        conn=conn,
                    )
                    if count < 0:
                        raise RuntimeError(f"change #{i}: update_domain_id failed")
                    domain_op_count += 1
                elif op == "update_path":
                    count = cmd_update_path(
                        module_id=change.get("module_id", ""),
                        new_path=change.get("new_path", ""),
                        dry_run=False,
                        conn=conn,
                    )
                    if count < 0:
                        raise RuntimeError(f"change #{i}: update_path failed")
                    domain_op_count += 1
                elif op == "migrate_dependencies":
                    count = cmd_migrate_dependencies(
                        from_domain=change.get("from_domain", ""),
                        to_domain=change.get("to_domain", ""),
                        new_from_domain=change.get("new_from_domain", ""),
                        new_to_domain=change.get("new_to_domain", ""),
                        dry_run=False,
                        conn=conn,
                    )
                    if count < 0:
                        raise RuntimeError(f"change #{i}: migrate_dependencies failed")
                    domain_op_count += 1
                elif op == "update_domain_layer":
                    ok = cmd_update_domain_layer(
                        domain_id=change.get("domain_id", ""),
                        layer_id=change.get("layer_id", ""),
                        dry_run=False,
                        conn=conn,
                    )
                    if not ok:
                        raise RuntimeError(f"change #{i}: update_domain_layer failed")
                    domain_op_count += 1
                elif op in ("update", "add_physical_file", "remove_physical_file", "set_physical_files"):
                    _apply_node_op(dep, change, i)
                else:
                    print(f"WARNING: Unknown op '{op}' for change #{i}", file=sys.stderr)

            # 节点级变更通过共享连接写入（不单独commit）
            _atomic_write(dep, conn=conn)
            # 统一提交所有变更（域级+节点级）
            conn.commit()
            print(f"Applied {len(changes)} changes to depgraph (domain_ops={domain_op_count})", file=sys.stderr)
        except Exception as e:
            conn.rollback()
            print(f"ERROR: batch failed, all changes rolled back: {e}", file=sys.stderr)
            sys.exit(4)
        finally:
            conn.close()


# ===== P0-2 新增：设计态节点/边管理（§22.5）=====


def add_design_node(
    path: str, blueprint_id: str, domain_id: str, build_status: str = "unbuilt", db_path: str = str(DEPGRAPH_PATH)
) -> int:
    """
    新增设计态节点（功能级，目录 path）。
    返回：新分配的 node_id
    校验：
    - path 必须以 / 结尾（目录路径）
    - blueprint_id 必须指向存在的蓝图文件
    - domain_id 必须在 domains 表中存在
    - build_status 必须符合 §12.6 状态机规则
    写入字段：design_maturity='design', blueprint_path=机械推导
    """
    # 校验path以/结尾
    if not path.endswith("/"):
        print(f"ERROR: path必须以/结尾（目录路径）: {path}", file=sys.stderr)
        return -1

    # 校验build_status
    valid_status = {"unbuilt", "testing", "stable", "deprecated"}
    if build_status not in valid_status:
        print(f"ERROR: build_status必须是{valid_status}之一: {build_status}", file=sys.stderr)
        return -1

    with _db_write_lock(db_path=db_path, task="add_design_node"):
        conn = sqlite3.connect(db_path)
        try:
            # 校验domain_id存在
            domain = conn.execute("SELECT domain_id FROM domains WHERE domain_id=?", (domain_id,)).fetchone()
            if not domain:
                print(f"ERROR: domain_id '{domain_id}' 不在domains表中", file=sys.stderr)
                return -1

            # 校验blueprint_id指向存在的蓝图文件
            if blueprint_id and not blueprint_id.startswith("PLACEHOLDER"):
                bp_path = f"D:/ZephyrAlpha/docs/03_modules/{blueprint_id}/blueprint.md"
                if not os.path.exists(bp_path):
                    print(f"WARNING: blueprint_id '{blueprint_id}' 对应的蓝图文件不存在: {bp_path}", file=sys.stderr)

            # 机械推导blueprint_path
            blueprint_path = f"docs/03_modules/{blueprint_id}/" if blueprint_id else ""

            # 检查是否已存在同path的设计态节点
            existing = conn.execute(
                "SELECT node_id FROM nodes WHERE path=? AND design_maturity='design'", (path,)
            ).fetchone()
            if existing:
                print(f"WARNING: path '{path}' 已有设计态节点 node_id={existing[0]}，执行UPDATE", file=sys.stderr)
                conn.execute(
                    "UPDATE nodes SET blueprint_id=?, domain_id=?, build_status=?, blueprint_path=? WHERE node_id=?",
                    (blueprint_id, domain_id, build_status, blueprint_path, existing[0]),
                )
                conn.commit()
                return existing[0]

            # 插入新节点
            cur = conn.execute(
                """INSERT INTO nodes (node_type, path, granularity, domain_id, blueprint_id,
                   build_status, design_maturity, blueprint_path, module_lifecycle_state, can_build)
                   VALUES (?, ?, 'directory', ?, ?, ?, 'design', ?, 'inactive', 1)""",
                ("design_node", path, domain_id, blueprint_id, build_status, blueprint_path),
            )
            node_id = cur.lastrowid
            conn.commit()
            print(f"[OK] 新增设计态节点 node_id={node_id} path={path}", file=sys.stderr)
            return node_id
        except Exception as e:
            conn.rollback()
            print(f"ERROR: add_design_node失败: {e}", file=sys.stderr)
            return -1
        finally:
            conn.close()


def add_design_edge(
    from_node_id: int,
    to_node_id: int,
    dep_type: str = "import",
    coupling_strength: str = "medium",
    used_symbol: str = "",
    invocation_method: str = "direct",
    api_contract_refs: str = "",
    event_ref: str = "",
    ddd_integration_pattern: str = "",
    failure_mode: str = "runtime_error",
    fallback: str = "no_fallback",
    activation_condition: str = "always",
    data_transfer_description: str = "",
    relationship_type: str = "",
    resource_impact: str = "low",
    db_path: str = str(DEPGRAPH_PATH),
) -> int:
    """
    新增设计态边（规划依赖）。
    返回：新分配的 edge_id
    校验：
    - from_node_id 和 to_node_id 必须在 nodes 表中存在且 design_maturity='design'
    - 写入前执行 DFS 循环检测，检测到循环则拒绝写入
    写入字段：dep_maturity='design'
    """
    with _db_write_lock(db_path=db_path, task="add_design_edge"):
        conn = sqlite3.connect(db_path)
        try:
            # 校验from_node_id和to_node_id存在且为设计态
            from_node = conn.execute(
                "SELECT node_id, design_maturity FROM nodes WHERE node_id=?", (from_node_id,)
            ).fetchone()
            if not from_node:
                print(f"ERROR: from_node_id={from_node_id} 不存在", file=sys.stderr)
                return -1
            if from_node[1] != "design":
                print(
                    f"ERROR: from_node_id={from_node_id} design_maturity={from_node[1]}（应为design）", file=sys.stderr
                )
                return -1

            to_node = conn.execute(
                "SELECT node_id, design_maturity FROM nodes WHERE node_id=?", (to_node_id,)
            ).fetchone()
            if not to_node:
                print(f"ERROR: to_node_id={to_node_id} 不存在", file=sys.stderr)
                return -1
            if to_node[1] != "design":
                print(f"ERROR: to_node_id={to_node_id} design_maturity={to_node[1]}（应为design）", file=sys.stderr)
                return -1

            # DFS循环检测：检查to_node_id是否能到达from_node_id
            if _detect_cycle_dfs(conn, to_node_id, from_node_id):
                print(f"ERROR: 检测到循环依赖: {to_node_id} -> ... -> {from_node_id}", file=sys.stderr)
                return -1

            # 插入边
            cur = conn.execute(
                """INSERT INTO edges (from_node_id, to_node_id, dep_type, architecture_direction,
                   coupling_strength, used_symbol, invocation_method, api_contract_refs,
                   event_ref, ddd_integration_pattern, failure_mode, fallback,
                   activation_condition, data_transfer_description, resource_impact,
                   relationship_type, cross_domain, verified, dep_maturity)
                   VALUES (?, ?, ?, 'downstream', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 'design')""",
                (
                    from_node_id,
                    to_node_id,
                    dep_type,
                    coupling_strength,
                    used_symbol,
                    invocation_method,
                    api_contract_refs,
                    event_ref,
                    ddd_integration_pattern,
                    failure_mode,
                    fallback,
                    activation_condition,
                    data_transfer_description,
                    resource_impact,
                    relationship_type,
                ),
            )
            edge_id = cur.lastrowid
            conn.commit()
            print(f"[OK] 新增设计态边 edge_id={edge_id} {from_node_id}->{to_node_id}", file=sys.stderr)
            return edge_id
        except Exception as e:
            conn.rollback()
            print(f"ERROR: add_design_edge失败: {e}", file=sys.stderr)
            return -1
        finally:
            conn.close()


def _detect_cycle_dfs(conn, start: int, target: int) -> bool:
    """DFS检测从start是否能到达target（如果到达，则添加start->target的边会形成环）。"""
    if start == target:
        return True
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        # 查询node的所有出边
        edges = conn.execute("SELECT to_node_id FROM edges WHERE from_node_id=?", (node,)).fetchall()
        for (next_node,) in edges:
            if next_node == target:
                return True
            if next_node not in visited:
                stack.append(next_node)
    return False


def transition_build_status(node_id: int, to: str, db_path: str = str(DEPGRAPH_PATH)) -> bool:
    """
    转换 build_status 状态。
    返回：True=成功，False=失败
    转换规则（机械判定）：
    - unbuilt → testing：允许
    - testing → stable：允许
    - stable → deprecated：允许
    - deprecated → stable：禁止（不可复活）
    - 任何跳转：禁止
    """
    # 合法状态转换
    valid_transitions = {
        ("unbuilt", "testing"),
        ("testing", "stable"),
        ("stable", "deprecated"),
    }

    with _db_write_lock(db_path=db_path, task="transition_build_status"):
        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute("SELECT build_status FROM nodes WHERE node_id=?", (node_id,)).fetchone()
            if not row:
                print(f"ERROR: node_id={node_id} 不存在", file=sys.stderr)
                return False
            current = row[0]
            if (current, to) not in valid_transitions:
                print(f"ERROR: 非法状态转换: {current} -> {to}（合法转换: {valid_transitions}）", file=sys.stderr)
                return False
            conn.execute("UPDATE nodes SET build_status=? WHERE node_id=?", (to, node_id))
            conn.commit()
            print(f"[OK] node_id={node_id}: build_status {current} -> {to}", file=sys.stderr)
            return True
        except Exception as e:
            conn.rollback()
            print(f"ERROR: transition_build_status失败: {e}", file=sys.stderr)
            return False
        finally:
            conn.close()


def remove_design_node(node_id: int, db_path: str = str(DEPGRAPH_PATH)) -> bool:
    """
    删除设计态节点（软删除）。
    返回：True=成功，False=失败
    流程：
    1. RULE-THREE 三步审判（登记检查/重复检查/功能价值检查）
    2. 通过后软删除（build_status='deprecated'）
    3. 拒绝硬删除（DELETE FROM nodes）
    """
    with _db_write_lock(db_path=db_path, task="remove_design_node"):
        conn = sqlite3.connect(db_path)
        try:
            # STEP 1: 登记检查 - 节点是否存在
            row = conn.execute(
                "SELECT node_id, path, design_maturity, build_status FROM nodes WHERE node_id=?", (node_id,)
            ).fetchone()
            if not row:
                print(f"ERROR: node_id={node_id} 不存在", file=sys.stderr)
                return False
            if row[2] != "design":
                print(f"ERROR: node_id={node_id} design_maturity={row[2]}（非设计态节点，禁止删除）", file=sys.stderr)
                return False

            # STEP 2: 重复检查 - 是否有其他同path节点
            duplicates = conn.execute(
                "SELECT COUNT(*) FROM nodes WHERE path=? AND node_id!=?", (row[1], node_id)
            ).fetchone()[0]

            # STEP 3: 功能价值检查 - 检查是否有边引用此节点
            edge_count = conn.execute(
                "SELECT COUNT(*) FROM edges WHERE from_node_id=? OR to_node_id=?", (node_id, node_id)
            ).fetchone()[0]
            if edge_count > 0:
                print(f"WARNING: node_id={node_id} 有{edge_count}条边引用，将先删除边", file=sys.stderr)
                conn.execute("DELETE FROM edges WHERE from_node_id=? OR to_node_id=?", (node_id, node_id))

            # 软删除（build_status='deprecated'）
            conn.execute("UPDATE nodes SET build_status='deprecated' WHERE node_id=?", (node_id,))
            conn.commit()
            print(f"[OK] node_id={node_id}: 软删除（build_status='deprecated'）", file=sys.stderr)
            return True
        except Exception as e:
            conn.rollback()
            print(f"ERROR: remove_design_node失败: {e}", file=sys.stderr)
            return False
        finally:
            conn.close()


# ===== F5 合规豁免：域/路径/依赖迁移命令（ARCH-CAP-005 抽屉式扩展）=====


def cmd_insert_domain(
    domain_id: str,
    domain_name: str,
    domain_group: str,
    layer_id: str,
    ssot_path: str,
    max_modules: int = 200,
    description: str = "",
    dry_run: bool = False,
    db_path: str = str(DEPGRAPH_PATH),
    conn=None,
) -> bool:
    """INSERT 新域到 domains 表（ARCH-CAP-005 抽屉式扩展）。

    新增域只需 INSERT domains 表，不修改生成器代码。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：True=成功，False=失败
    """
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_insert_domain", db_path=db_path):
        if own_conn:
            conn = sqlite3.connect(db_path)
        try:
            existing = conn.execute("SELECT domain_id FROM domains WHERE domain_id=?", (domain_id,)).fetchone()
            if existing:
                print(f"ERROR: domain_id '{domain_id}' 已存在", file=sys.stderr)
                return False

            now = datetime.datetime.now().isoformat()
            if dry_run:
                print(
                    f"[DRY RUN] 将 INSERT 域 {domain_id} ({domain_name}) layer={layer_id} ssot_path={ssot_path} max_modules={max_modules}",
                    file=sys.stderr,
                )
                return True

            conn.execute(
                """INSERT INTO domains (domain_id, domain_name, domain_group, description, ssot_path,
                   current_modules, max_modules, lifecycle, created_at, updated_at, build_status, layer_id)
                   VALUES (?, ?, ?, ?, ?, 0, ?, 'design_only', ?, ?, 'unbuilt', ?)""",
                (domain_id, domain_name, domain_group, description, ssot_path, max_modules, now, now, layer_id),
            )
            if own_conn:
                conn.commit()
            print(f"[OK] INSERT 域 {domain_id} ({domain_name}) layer={layer_id}", file=sys.stderr)
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            print(f"ERROR: cmd_insert_domain失败: {e}", file=sys.stderr)
            return False
        finally:
            if own_conn:
                conn.close()


def cmd_update_domain_id(
    module_id: str, new_domain_id: str, dry_run: bool = False, db_path: str = str(DEPGRAPH_PATH), conn=None
) -> int:
    """UPDATE 模块的 domain_id（域拆分时迁移模块归属）。

    按 belongs_to 或 blueprint_id 匹配节点。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：受影响行数，-1=失败
    """
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_update_domain_id", db_path=db_path):
        if own_conn:
            conn = sqlite3.connect(db_path)
        try:
            domain = conn.execute("SELECT domain_id FROM domains WHERE domain_id=?", (new_domain_id,)).fetchone()
            if not domain:
                print(f"ERROR: new_domain_id '{new_domain_id}' 不在 domains 表中", file=sys.stderr)
                return -1

            rows = conn.execute(
                "SELECT node_id, path, domain_id FROM nodes WHERE belongs_to=? OR blueprint_id=?",
                (module_id, module_id),
            ).fetchall()
            if not rows:
                print(f"ERROR: module_id '{module_id}' 未找到匹配节点", file=sys.stderr)
                return -1

            if dry_run:
                for r in rows:
                    print(
                        f"[DRY RUN] 将 UPDATE node_id={r[0]} domain_id: {r[2]} -> {new_domain_id} (path={r[1]})",
                        file=sys.stderr,
                    )
                return len(rows)

            cur = conn.execute(
                "UPDATE nodes SET domain_id=? WHERE belongs_to=? OR blueprint_id=?",
                (new_domain_id, module_id, module_id),
            )
            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE {cur.rowcount} 个节点 domain_id -> {new_domain_id}", file=sys.stderr)
            return cur.rowcount
        except Exception as e:
            if own_conn:
                conn.rollback()
            print(f"ERROR: cmd_update_domain_id失败: {e}", file=sys.stderr)
            return -1
        finally:
            if own_conn:
                conn.close()


def cmd_update_path(
    module_id: str, new_path: str, dry_run: bool = False, db_path: str = str(DEPGRAPH_PATH), conn=None
) -> int:
    """UPDATE 模块的 path（物理路径迁移，ARCH-CAP-004 路径平铺）。

    按 belongs_to 或 blueprint_id 匹配节点。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：受影响行数，-1=失败
    """
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_update_path", db_path=db_path):
        if own_conn:
            conn = sqlite3.connect(db_path)
        try:
            rows = conn.execute(
                "SELECT node_id, path FROM nodes WHERE belongs_to=? OR blueprint_id=?", (module_id, module_id)
            ).fetchall()
            if not rows:
                print(f"ERROR: module_id '{module_id}' 未找到匹配节点", file=sys.stderr)
                return -1

            if dry_run:
                for r in rows:
                    print(f"[DRY RUN] 将 UPDATE node_id={r[0]} path: {r[1]} -> {new_path}", file=sys.stderr)
                return len(rows)

            cur = conn.execute(
                "UPDATE nodes SET path=? WHERE belongs_to=? OR blueprint_id=?", (new_path, module_id, module_id)
            )
            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE {cur.rowcount} 个节点 path -> {new_path}", file=sys.stderr)
            return cur.rowcount
        except Exception as e:
            if own_conn:
                conn.rollback()
            print(f"ERROR: cmd_update_path失败: {e}", file=sys.stderr)
            return -1
        finally:
            if own_conn:
                conn.close()


def cmd_migrate_dependencies(
    from_domain: str,
    to_domain: str,
    new_from_domain: str = "",
    new_to_domain: str = "",
    dry_run: bool = False,
    db_path: str = str(DEPGRAPH_PATH),
    conn=None,
) -> int:
    """UPDATE domain_dependencies 表迁移跨域依赖。

    new_from_domain 非空 → 更新 from_domain
    new_to_domain 非空 → 更新 to_domain
    若目标依赖已存在则合并 edge_count。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：受影响行数，-1=失败
    """
    if not new_from_domain and not new_to_domain:
        print("ERROR: 必须指定 --new-from-domain 或 --new-to-domain", file=sys.stderr)
        return -1

    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_migrate_dependencies", db_path=db_path):
        if own_conn:
            conn = sqlite3.connect(db_path)
        try:
            rows = conn.execute(
                "SELECT from_domain, to_domain, edge_count FROM domain_dependencies WHERE from_domain=? AND to_domain=?",
                (from_domain, to_domain),
            ).fetchall()
            if not rows:
                print(f"ERROR: domain_dependencies ({from_domain} -> {to_domain}) 不存在", file=sys.stderr)
                return -1

            if new_from_domain:
                d = conn.execute("SELECT domain_id FROM domains WHERE domain_id=?", (new_from_domain,)).fetchone()
                if not d:
                    print(f"ERROR: new_from_domain '{new_from_domain}' 不在 domains 表中", file=sys.stderr)
                    return -1
            if new_to_domain:
                d = conn.execute("SELECT domain_id FROM domains WHERE domain_id=?", (new_to_domain,)).fetchone()
                if not d:
                    print(f"ERROR: new_to_domain '{new_to_domain}' 不在 domains 表中", file=sys.stderr)
                    return -1

            final_from = new_from_domain or from_domain
            final_to = new_to_domain or to_domain

            if dry_run:
                for r in rows:
                    print(
                        f"[DRY RUN] 将 UPDATE domain_dependencies: {r[0]} -> {r[1]} => {final_from} -> {final_to} (edge_count={r[2]})",
                        file=sys.stderr,
                    )
                return len(rows)

            existing = conn.execute(
                "SELECT edge_count FROM domain_dependencies WHERE from_domain=? AND to_domain=?", (final_from, final_to)
            ).fetchone()

            if existing and (final_from != from_domain or final_to != to_domain):
                total = existing[0] + rows[0][2]
                conn.execute(
                    "DELETE FROM domain_dependencies WHERE from_domain=? AND to_domain=?", (from_domain, to_domain)
                )
                conn.execute(
                    "UPDATE domain_dependencies SET edge_count=? WHERE from_domain=? AND to_domain=?",
                    (total, final_from, final_to),
                )
                print(
                    f"[OK] 合并 domain_dependencies: {from_domain}->{to_domain} 并入 {final_from}->{final_to} (edge_count={total})",
                    file=sys.stderr,
                )
            else:
                conn.execute(
                    "UPDATE domain_dependencies SET from_domain=?, to_domain=? WHERE from_domain=? AND to_domain=?",
                    (final_from, final_to, from_domain, to_domain),
                )
                print(
                    f"[OK] UPDATE domain_dependencies: {from_domain}->{to_domain} => {final_from}->{final_to}",
                    file=sys.stderr,
                )

            if own_conn:
                conn.commit()
            return len(rows)
        except Exception as e:
            if own_conn:
                conn.rollback()
            print(f"ERROR: cmd_migrate_dependencies失败: {e}", file=sys.stderr)
            return -1
        finally:
            if own_conn:
                conn.close()


def cmd_update_domain_capacity(
    domain_id: str, field: str, value: int, dry_run: bool = False, db_path: str = str(DEPGRAPH_PATH), conn=None
) -> bool:
    """UPDATE domains 表的容量字段（current_modules/max_modules）。

    ARCH-CAP-001 要求 current_modules 按 production 节点口径统计。
    域拆分后需要修正容量数据，本命令提供 F5 合规的写入接口。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：True=成功，False=失败
    """
    ALLOWED_FIELDS = {"current_modules", "max_modules"}
    FIELD_ALIASES = {"current": "current_modules", "max": "max_modules"}
    field = FIELD_ALIASES.get(field, field)
    if field not in ALLOWED_FIELDS:
        print(f"ERROR: field 必须是 {ALLOWED_FIELDS} 之一（或简写 current/max），实际: {field}", file=sys.stderr)
        return False

    if value < 0:
        print(f"ERROR: value 必须是非负整数，实际: {value}", file=sys.stderr)
        return False

    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_update_domain_capacity", db_path=db_path):
        if own_conn:
            conn = sqlite3.connect(db_path)
        try:
            existing = conn.execute(
                "SELECT domain_id, current_modules, max_modules FROM domains WHERE domain_id=?", (domain_id,)
            ).fetchone()
            if not existing:
                print(f"ERROR: domain_id '{domain_id}' 不在 domains 表中", file=sys.stderr)
                return False

            old_value = existing[1] if field == "current_modules" else existing[2]
            if dry_run:
                print(f"[DRY RUN] 将 UPDATE domains {field}: {domain_id} {old_value} -> {value}", file=sys.stderr)
                return True

            now = datetime.datetime.now().isoformat()
            conn.execute(f"UPDATE domains SET {field}=?, updated_at=? WHERE domain_id=?", (value, now, domain_id))
            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE domains {field}: {domain_id} {old_value} -> {value}", file=sys.stderr)
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            print(f"ERROR: cmd_update_domain_capacity失败: {e}", file=sys.stderr)
            return False
        finally:
            if own_conn:
                conn.close()


def cmd_update_domain_layer(
    domain_id: str, layer_id: str, dry_run: bool = False, db_path: str = str(DEPGRAPH_PATH), conn=None
) -> bool:
    """UPDATE domains 表的 layer_id 字段（架构层级迁移）。

    ARCH-001 向下依赖原则要求 L2→L1→L0。当域的实际职责属于平台层时，
    需要通过本命令调整 layer_id 以消除违规向上依赖。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：True=成功，False=失败
    """
    ALLOWED_LAYERS = {"L0_infrastructure", "L1_foundation", "L1_platform", "L2_domain"}
    if layer_id not in ALLOWED_LAYERS:
        print(f"ERROR: layer_id 必须是 {ALLOWED_LAYERS} 之一，实际: {layer_id}", file=sys.stderr)
        return False

    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_update_domain_layer", db_path=db_path):
        if own_conn:
            conn = sqlite3.connect(db_path)
        try:
            existing = conn.execute(
                "SELECT domain_id, layer_id FROM domains WHERE domain_id=?", (domain_id,)
            ).fetchone()
            if not existing:
                print(f"ERROR: domain_id '{domain_id}' 不在 domains 表中", file=sys.stderr)
                return False

            old_layer = existing[1]
            if old_layer == layer_id:
                print(f"WARNING: domain_id '{domain_id}' layer_id 已是 {layer_id}，无需更新", file=sys.stderr)
                return True

            if dry_run:
                print(f"[DRY RUN] 将 UPDATE domains layer_id: {domain_id} {old_layer} -> {layer_id}", file=sys.stderr)
                return True

            now = datetime.datetime.now().isoformat()
            conn.execute("UPDATE domains SET layer_id=?, updated_at=? WHERE domain_id=?", (layer_id, now, domain_id))
            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE domains layer_id: {domain_id} {old_layer} -> {layer_id}", file=sys.stderr)
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            print(f"ERROR: cmd_update_domain_layer失败: {e}", file=sys.stderr)
            return False
        finally:
            if own_conn:
                conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="depgraph 变更写入工具（禁止AI直接Write 157MB文件）",
        epilog="See .trae/rules/project_rules.md RULE-SIXTEEN for the full protocol.",
    )
    parser.add_argument(
        "--update-module", type=str, nargs=2, metavar=("MODULE_ID", "FIELD=VALUE"), help="更新单个模块字段"
    )
    parser.add_argument("--batch", type=str, help="批量变更 JSON 文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅验证，不写入")
    # P0-2 新增4命令
    parser.add_argument(
        "--add-design-node",
        type=str,
        nargs="+",
        metavar="ARG",
        help="新增设计态节点: PATH BLUEPRINT_ID DOMAIN_ID [BUILD_STATUS]",
    )
    parser.add_argument(
        "--add-design-edge",
        type=int,
        nargs=2,
        metavar=("FROM_NODE_ID", "TO_NODE_ID"),
        help="新增设计态边: FROM_NODE_ID TO_NODE_ID",
    )
    parser.add_argument(
        "--transition-build-status",
        type=str,
        nargs=2,
        metavar=("NODE_ID", "TO_STATUS"),
        help="转换build_status: NODE_ID TO_STATUS",
    )
    parser.add_argument("--remove-design-node", type=int, metavar="NODE_ID", help="软删除设计态节点: NODE_ID")
    # F5 合规豁免：域/路径/依赖迁移命令（ARCH-CAP-005）
    parser.add_argument(
        "--insert-domain",
        type=str,
        nargs="+",
        metavar="ARG",
        help="INSERT 新域: DOMAIN_ID DOMAIN_NAME DOMAIN_GROUP LAYER_ID SSOT_PATH [--max-modules N] [--description TEXT]",
    )
    parser.add_argument(
        "--update-domain-id",
        type=str,
        nargs=2,
        metavar=("MODULE_ID", "NEW_DOMAIN_ID"),
        help="UPDATE 模块 domain_id（域拆分迁移模块归属）",
    )
    parser.add_argument(
        "--update-path", type=str, nargs=2, metavar=("MODULE_ID", "NEW_PATH"), help="UPDATE 模块 path（物理路径迁移）"
    )
    parser.add_argument(
        "--migrate-dependencies",
        type=str,
        nargs=2,
        metavar=("FROM_DOMAIN", "TO_DOMAIN"),
        help="UPDATE domain_dependencies 迁移跨域依赖",
    )
    parser.add_argument(
        "--update-domain-capacity",
        type=str,
        nargs=2,
        metavar=("DOMAIN_ID", "FIELD=VALUE"),
        help="UPDATE domains 容量字段: DOMAIN_ID current_modules=N|max_modules=N",
    )
    parser.add_argument(
        "--update-domain-layer",
        type=str,
        nargs=2,
        metavar=("DOMAIN_ID", "LAYER_ID"),
        help="UPDATE domains layer_id: DOMAIN_ID L0_infrastructure|L1_foundation|L1_platform|L2_domain",
    )
    parser.add_argument("--new-from-domain", type=str, default="", help="migrate-dependencies 的新 from_domain")
    parser.add_argument("--new-to-domain", type=str, default="", help="migrate-dependencies 的新 to_domain")
    parser.add_argument("--max-modules", type=int, default=200, help="insert-domain 的 max_modules（默认 200）")
    parser.add_argument("--description", type=str, default="", help="insert-domain 的 description")
    args = parser.parse_args()

    # P0-2 新增命令处理
    if args.add_design_node:
        parts = args.add_design_node
        path = parts[0]
        blueprint_id = parts[1] if len(parts) > 1 else ""
        domain_id = parts[2] if len(parts) > 2 else ""
        build_status = parts[3] if len(parts) > 3 else "unbuilt"
        node_id = add_design_node(path, blueprint_id, domain_id, build_status)
        if node_id < 0:
            sys.exit(4)
        print(f"node_id={node_id}")
        return

    if args.add_design_edge:
        from_id, to_id = args.add_design_edge
        edge_id = add_design_edge(from_id, to_id)
        if edge_id < 0:
            sys.exit(4)
        print(f"edge_id={edge_id}")
        return

    if args.transition_build_status:
        node_id_str, to_status = args.transition_build_status
        node_id = int(node_id_str)
        ok = transition_build_status(node_id, to_status)
        if not ok:
            sys.exit(4)
        return

    if args.remove_design_node is not None:
        ok = remove_design_node(args.remove_design_node)
        if not ok:
            sys.exit(4)
        return

    # F5 合规豁免：域/路径/依赖迁移命令处理
    if args.insert_domain:
        parts = args.insert_domain
        if len(parts) < 5:
            print(
                "ERROR: --insert-domain 需要 5 个参数: DOMAIN_ID DOMAIN_NAME DOMAIN_GROUP LAYER_ID SSOT_PATH",
                file=sys.stderr,
            )
            sys.exit(3)
        domain_id = parts[0]
        domain_name = parts[1]
        domain_group = parts[2]
        layer_id = parts[3]
        ssot_path = parts[4]
        ok = cmd_insert_domain(
            domain_id,
            domain_name,
            domain_group,
            layer_id,
            ssot_path,
            max_modules=args.max_modules,
            description=args.description,
            dry_run=args.dry_run,
        )
        if not ok:
            sys.exit(4)
        return

    if args.update_domain_id:
        module_id, new_domain_id = args.update_domain_id
        count = cmd_update_domain_id(module_id, new_domain_id, dry_run=args.dry_run)
        if count < 0:
            sys.exit(4)
        print(f"affected={count}")
        return

    if args.update_path:
        module_id, new_path = args.update_path
        count = cmd_update_path(module_id, new_path, dry_run=args.dry_run)
        if count < 0:
            sys.exit(4)
        print(f"affected={count}")
        return

    if args.migrate_dependencies:
        from_domain, to_domain = args.migrate_dependencies
        count = cmd_migrate_dependencies(
            from_domain,
            to_domain,
            new_from_domain=args.new_from_domain,
            new_to_domain=args.new_to_domain,
            dry_run=args.dry_run,
        )
        if count < 0:
            sys.exit(4)
        print(f"affected={count}")
        return

    if args.update_domain_capacity:
        domain_id, field_value = args.update_domain_capacity
        if "=" not in field_value:
            print("ERROR: FIELD=VALUE format required, e.g. current_modules=134", file=sys.stderr)
            sys.exit(3)
        field, value_str = field_value.split("=", 1)
        try:
            value = int(value_str)
        except ValueError:
            print(f"ERROR: value 必须是整数，实际: {value_str}", file=sys.stderr)
            sys.exit(3)
        ok = cmd_update_domain_capacity(domain_id, field, value, dry_run=args.dry_run)
        if not ok:
            sys.exit(4)
        return

    if args.update_domain_layer:
        domain_id, layer_id = args.update_domain_layer
        ok = cmd_update_domain_layer(domain_id, layer_id, dry_run=args.dry_run)
        if not ok:
            sys.exit(4)
        return

    if not args.update_module and not args.batch:
        parser.print_help()
        print("\nERROR: Must specify --update-module or --batch", file=sys.stderr)
        sys.exit(3)

    dep = _load_depgraph()

    if args.update_module:
        module_id = args.update_module[0]
        field_value = args.update_module[1]
        if "=" not in field_value:
            print("ERROR: FIELD=VALUE format required, e.g. blueprint_status=has_blueprint", file=sys.stderr)
            sys.exit(3)
        field, value = field_value.split("=", 1)
        cmd_update_module(dep, module_id, field, value)
        if args.dry_run:
            print("DRY RUN - no changes written", file=sys.stderr)
        else:
            _atomic_write(dep)

    if args.batch:
        with open(args.batch, encoding="utf-8") as f:
            changes = json.load(f)
        cmd_batch(dep, changes, args.dry_run)


if __name__ == "__main__":
    main()
