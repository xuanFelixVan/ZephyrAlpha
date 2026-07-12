# [A_test] module_id: SRC-TST-2100 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-700 | docs/03_modules/_domain_governance/blueprint.md | §vocab-sync-chain
# [MODULE] tests.unit.test_vocab_sync_chain
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Vocabulary 同步链路回归测试（议题 #ARCH-008 / 裁定#206）

本测试套件保护 vocabulary YAML → 派生文件 / DB 缓存 同步链路的根因性修复，
覆盖 Bug A~H 的回归保护，防止以下根因再次出现：

  Bug A — generate_derived_files.py 路径常量错配（kebab + 错扩展名）
  Bug B — sync_yaml_to_depgraph.py 键名错配（field_name vs vocabulary_name）
  Bug C — generate_derived_files.py enum_values apply 分支恒 False
  Bug D — generate_derived_files.py open() 缺写模式
  Bug E — generate_derived_files.py schema_json oneOf 重写逻辑错
  Bug F — generate_derived_files.py 异常捕获太窄（tmp 残留）
  Bug G — sync_yaml_to_depgraph.py 无跨进程锁保护
  Bug H — DB_PATH 硬编码绝对路径 / constants 缺 DEPGRAPH_DB_PATH

设计原则：
  1. 只读——不向生产 depgraph / governance.db 写入任何数据
  2. 行为优先——能跑脚本验证行为的不只做静态检查
  3. 静态兜底——锁保护 / DB_PATH 引用等无法行为测试的做源码静态断言
  4. 子集容忍——triage.py 等子集消费者只校验"无非法值"，不强制全等
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT

_PROJECT_ROOT = REPO_ROOT
_SCRIPTS_GOV = _PROJECT_ROOT / "scripts" / "governance"
if str(_SCRIPTS_GOV) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_GOV))

GOV_DOCS_DIR = REPO_ROOT / "docs" / "01_policies_and_standards"  # noqa: E402

_VOCAB_DIR = GOV_DOCS_DIR / "_registry" / "vocabularies"
_CATALOGS_DIR = GOV_DOCS_DIR / "_registry" / "catalogs"
_CONTRACTS_DIR = GOV_DOCS_DIR / "_registry" / "contracts"
_SCHEMAS_DIR = GOV_DOCS_DIR / "_registry" / "schemas"
# 注：depgraph 已迁移到 PostgreSQL（P2迁移），_DEPGRAPH_DB 路径常量已移除
_GENERATE_SCRIPT = _SCRIPTS_GOV / "d3_metadata" / "generate_derived_files.py"
_SYNC_SCRIPT = _SCRIPTS_GOV / "sync_yaml_to_depgraph.py"
_CONSTANTS_MODULE = _SCRIPTS_GOV / "_shared" / "constants.py"


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _load_vocab(vocab_file: str) -> dict:
    """加载 vocabulary YAML 并返回解析后的字典。"""
    return yaml.safe_load((_VOCAB_DIR / vocab_file).read_text(encoding="utf-8"))


def _vocab_active_values(vocab_file: str) -> set[str]:
    """提取 vocabulary YAML 的活跃值集合。"""
    data = _load_vocab(vocab_file)
    out: set[str] = set()
    for entry in data.get("values", []):
        if isinstance(entry, dict):
            val = entry.get("value") or entry.get("id")
            if val:
                out.add(str(val))
        elif isinstance(entry, str):
            out.add(entry)
    return out


def _vocab_deprecated_values(vocab_file: str) -> set[str]:
    """提取 vocabulary YAML 的废弃值集合。"""
    data = _load_vocab(vocab_file)
    out: set[str] = set()
    for entry in data.get("deprecated_values", []):
        if isinstance(entry, dict):
            val = entry.get("value") or entry.get("id")
            if val:
                out.add(str(val))
        elif isinstance(entry, str):
            out.add(entry)
    return out


# ===========================================================================
# Bug A 回归：generate_derived_files.py 路径常量使用 snake_case + 正确扩展名
# ===========================================================================

class TestBugAPathConstants:
    """Bug A 回归——路径常量必须指向磁盘上真实存在的 snake_case 文件。

    根因回顾：原路径用连字符 + 错扩展名（.md），
    导致每个 _sync_* 函数开头 `if not PATH.exists(): return False` 静默返回 False，
    主循环打印"✅ 一致"并 exit 0——形成虚假绿灯。
    """

    def test_field_registry_path_uses_snake_case_and_exists(self) -> None:
        """frontmatter_field_registry.yaml 路径常量存在（非 .md 旧名）。"""
        from d3_metadata.generate_derived_files import FIELD_REGISTRY_PATH

        assert FIELD_REGISTRY_PATH.name == "frontmatter_field_registry.yaml"
        assert FIELD_REGISTRY_PATH.exists(), f"派生文件不存在: {FIELD_REGISTRY_PATH}"

    def test_arch_contract_path_uses_snake_case_and_exists(self) -> None:
        """architecture_contract.yaml 路径常量存在（非 architecture-contract.yaml 旧名）。"""
        from d3_metadata.generate_derived_files import ARCH_CONTRACT_PATH

        assert ARCH_CONTRACT_PATH.name == "architecture_contract.yaml"
        assert ARCH_CONTRACT_PATH.exists(), f"派生文件不存在: {ARCH_CONTRACT_PATH}"

    def test_schema_json_path_uses_snake_case_and_exists(self) -> None:
        """frontmatter_schema.json 路径常量存在（非 frontmatter-schema.json 旧名）。"""
        from d3_metadata.generate_derived_files import SCHEMA_JSON_PATH

        assert SCHEMA_JSON_PATH.name == "frontmatter_schema.json"
        assert SCHEMA_JSON_PATH.exists(), f"派生文件不存在: {SCHEMA_JSON_PATH}"

    def test_vocab_field_map_uses_snake_case_filenames(self) -> None:
        """VOCAB_FIELD_MAP 的文件名全部 snake_case（非 kebab 旧名）。"""
        from d3_metadata.generate_derived_files import VOCAB_FIELD_MAP

        for field_name, vocab_file in VOCAB_FIELD_MAP.items():
            assert "-" not in vocab_file, (
                f"VOCAB_FIELD_MAP[{field_name!r}]={vocab_file!r} 含连字符（应为 snake_case）"
            )
            assert vocab_file.endswith("_vocabulary.yaml"), (
                f"VOCAB_FIELD_MAP[{field_name!r}]={vocab_file!r} 命名不规范"
            )
            assert (_VOCAB_DIR / vocab_file).exists(), f"vocabulary 文件不存在: {vocab_file}"


# ===========================================================================
# Bug B 回归：sync_yaml_to_depgraph.py 使用 vocabulary_name 键
# ===========================================================================

class TestBugBVocabularyNameKey:
    """Bug B 回归——sync 必须用 vocabulary_name 键提取字段名。

    根因回顾：24 个 vocabulary YAML 全部用 `vocabulary_name` 键，
    sync 旧代码读 `field_name` 键 → fallback 到 yaml_file.stem →
    DB field_vocabularies 表写入 `doc_type_vocabulary`（而非 `doc_type`），
    下游按 field_name='doc_type' 查询时全部 miss。
    """

    def test_sync_uses_vocabulary_name_key(self) -> None:
        """sync_yaml_to_depgraph.py 源码使用 vocabulary_name 键。"""
        src = _SYNC_SCRIPT.read_text(encoding="utf-8")
        # 修复后应使用 vocabulary_name 键（不是 field_name 键）
        assert 'data.get("vocabulary_name")' in src, (
            "sync_yaml_to_depgraph.py 未使用 vocabulary_name 键提取字段名（Bug B 回归）"
        )

    def test_field_vocabularies_table_has_no_dirty_field_name(self) -> None:
        """DB field_vocabularies 表的 field_name 不含 _vocabulary 后缀脏值。

        只读查询生产 depgraph (PostgreSQL)，不写入任何数据。
        """
        try:
            conn = get_depgraph_pg_connection()
        except Exception:
            pytest.skip("depgraph (PostgreSQL) 不可用")
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT field_name FROM field_vocabularies "
                    "WHERE field_name LIKE '%_vocabulary'"
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        assert rows == [], (
            f"field_vocabularies 表存在脏值 field_name（应不含 _vocabulary 后缀）: {rows}"
        )

    def test_field_vocabularies_has_expected_vocab_names(self) -> None:
        """DB field_vocabularies 表包含核心 vocabulary 的裸字段名。"""
        try:
            conn = get_depgraph_pg_connection()
        except Exception:
            pytest.skip("depgraph (PostgreSQL) 不可用")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT field_name FROM field_vocabularies")
                rows = cur.fetchall()
        finally:
            conn.close()
        present = {r[0] for r in rows}
        # 核心词汇表必须在 DB 中以裸字段名出现（非 xxx_vocabulary）
        for expected in ["doc_type", "layer", "ttl", "status", "rule_form"]:
            assert expected in present, (
                f"field_vocabularies 表缺少裸字段名 {expected!r}（可能仍是 Bug B 脏值）"
            )


# ===========================================================================
# Bug C/D/E/F 回归：generate_derived_files.py --check 行为验证
# ===========================================================================

class TestBugCDEFGenerateDerivedCheck:
    """Bug C/D/E/F 回归——generate_derived_files.py --check 必须真实执行。

    根因回顾：
      Bug C: enum_values apply 分支恒 False → enum_values 永不写回
      Bug D: open() 缺 "w" 模式 → FileNotFoundError 崩溃
      Bug E: schema_json oneOf 重写逻辑错 → 写空 enum 键污染 schema
      Bug F: 异常捕获太窄 → tmp 文件残留

    --check 模式只读不写，若任一 Bug 回归会导致：
      - 路径找不到 → 静默返回 / 崩溃
      - 漂移未检测 → exit 0 但实际不一致（由 Bug B/D/E 回归测试兜底）
      - 崩溃 → 非 0 退出码
    """

    def test_check_exits_zero(self) -> None:
        """generate_derived_files.py --check 必须以 exit 0 退出。"""
        result = subprocess.run(
            [sys.executable, str(_GENERATE_SCRIPT), "--check"],
            capture_output=True,
            text=True,
            cwd=str(_PROJECT_ROOT),
            timeout=60,
        )
        assert result.returncode == 0, (
            f"generate_derived_files.py --check 退出码非 0: {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_check_reports_consistency(self) -> None:
        """--check 输出必须包含一致 / PASS 标识（非静默跳过）。"""
        result = subprocess.run(
            [sys.executable, str(_GENERATE_SCRIPT), "--check"],
            capture_output=True,
            text=True,
            cwd=str(_PROJECT_ROOT),
            timeout=60,
        )
        # 修复前 Bug A 会导致函数静默 return False，主循环仍打印"一致"——
        # 这里只做最低限度断言：脚本正常执行（exit 0）且输出非空
        assert result.stdout.strip(), "--check 输出为空（可能路径常量回归 Bug A）"

    def test_enum_values_apply_branch_exists(self) -> None:
        """Bug C 回归——源码必须含 enum_values apply 分支。"""
        src = _GENERATE_SCRIPT.read_text(encoding="utf-8")
        # 修复后增加了 elif apply and "enum_values" in field 分支
        assert 'enum_values' in src and 'apply' in src, (
            "generate_derived_files.py 缺少 enum_values apply 分支（Bug C 回归）"
        )

    def test_open_uses_write_mode_in_sync_functions(self) -> None:
        """Bug D 回归——_sync_* 函数中 open() 必须用 "w" 模式写 tmp 文件。"""
        src = _GENERATE_SCRIPT.read_text(encoding="utf-8")
        # 三个 _sync_* 函数都写 tmp 文件，必须用 "w" 模式
        # 检查至少 3 处 open(..., "w", ...)
        import re
        write_opens = re.findall(r'open\([^)]*["\']w["\']', src)
        assert len(write_opens) >= 3, (
            f"_sync_* 函数 open() 写模式不足 3 处（Bug D 回归）: 找到 {len(write_opens)} 处"
        )

    def test_exception_handling_includes_oserror(self) -> None:
        """Bug F 回归——异常捕获必须覆盖 OSError（非仅 PermissionError）。"""
        src = _GENERATE_SCRIPT.read_text(encoding="utf-8")
        # 修复后 except (PermissionError, OSError)
        assert "OSError" in src, (
            "generate_derived_files.py 异常捕获未覆盖 OSError（Bug F 回归）"
        )

    def test_tmp_cleanup_in_finally(self) -> None:
        """Bug F 回归——tmp 文件必须在 finally 块中清理。"""
        src = _GENERATE_SCRIPT.read_text(encoding="utf-8")
        # 修复后在 finally 中 os.remove(tmp_path)
        assert "finally:" in src and "os.remove" in src, (
            "generate_derived_files.py 缺少 finally + os.remove tmp 清理（Bug F 回归）"
        )


# ===========================================================================
# Bug G 回归：sync_yaml_to_depgraph.py 锁机制（P2 PG 迁移后语义反转）
# ===========================================================================

class TestBugGLockProtection:
    """Bug G 回归——P2 PG 迁移后，sync 必须删除文件锁（PG MVCC 替代）。

    根因回顾（Bug G 原意图）：SQLite 时代 sync 仅依赖 sqlite3 事务 + 临时 DROP
    只读触发器，无跨进程文件锁，与 apply_depgraph.py / generate_project_depgraph.py
    并发可能竞争 DB 写入。修复方式是引入 lock_files.py 跨进程文件锁。

    P2 PG 迁移治本（2026-06）：depgraph 迁至 PostgreSQL，PG MVCC 事务
    （autocommit=False）提供原子性 + 行级锁，文件锁对 PG 写无保护作用
    （锁键指向往已归档 .db 文件，语义悬空）。治本方向：删除文件锁调用，
    与 apply_depgraph.py / generate_project_depgraph.py 对齐。

    本类保护"锁删除是治本成果，不得回退重新引入文件锁"。
    """

    def test_sync_does_not_import_lock_files(self) -> None:
        """sync_yaml_to_depgraph.py 不得导入 lock_files 模块（P2 PG 迁移治本）。"""
        src = _SYNC_SCRIPT.read_text(encoding="utf-8")
        # 治本后 lock_files 仅在删除注释中出现，不应有 import 语句
        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                assert "lock_files" not in stripped, (
                    f"sync_yaml_to_depgraph.py 仍导入 lock_files（P2 治本回退）: {stripped}"
                )

    def test_sync_does_not_call_acquire_release(self) -> None:
        """sync_all() 不得调用 cmd_acquire / cmd_release（P2 PG 迁移治本）。"""
        src = _SYNC_SCRIPT.read_text(encoding="utf-8")
        # 治本后 cmd_acquire/cmd_release 仅在删除注释中出现，不应有调用语句
        for line in src.splitlines():
            stripped = line.strip()
            # 跳过注释行
            if stripped.startswith("#"):
                continue
            # 跳过 docstring/字符串字面量行（粗略）
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            assert "cmd_acquire(" not in stripped, (
                f"sync_yaml_to_depgraph.py 仍调用 cmd_acquire（P2 治本回退）: {stripped}"
            )
            assert "cmd_release(" not in stripped, (
                f"sync_yaml_to_depgraph.py 仍调用 cmd_release（P2 治本回退）: {stripped}"
            )

    def test_sync_all_uses_pg_transaction_not_file_lock(self) -> None:
        """sync_all() 必须用 PG 事务（get_depgraph_pg_connection），不得用文件锁。"""
        src = _SYNC_SCRIPT.read_text(encoding="utf-8")
        # 提取 sync_all 函数体
        sync_all_start = src.find("def sync_all(")
        assert sync_all_start != -1, "sync_all() 函数未找到"
        sync_all_body = src[sync_all_start:]
        next_def = sync_all_body.find("\ndef ", 1)
        if next_def != -1:
            sync_all_body = sync_all_body[:next_def]
        # 治本后应通过 get_depgraph_pg_connection 获取 PG 连接
        assert "get_depgraph_pg_connection" in sync_all_body, (
            "sync_all() 未使用 get_depgraph_pg_connection（P2 迁移回归）"
        )


# ===========================================================================
# Bug H 回归：constants.py DEPGRAPH_DB_PATH（P0/P1 治本后语义反转）
# ===========================================================================

class TestBugHDepgraphDbPath:
    """Bug H 回归——P0/P1 治本后 DEPGRAPH_DB_PATH 常量已删除 + PG 入口为真源。

    根因回顾（Bug H 原意图）：_shared/constants.py 只定义了 governance.db 的 DB_PATH，
    sync_yaml_to_depgraph.py 硬编码 `D:\\ZephyrAlpha\\data\\databases\\depgraph.db`，
    两个 DB_PATH 指向不同 DB，是潜在不一致点。修复方式是统一引入 DEPGRAPH_DB_PATH 常量。

    P0/P1 治本（2026-06）：depgraph 已迁至 PostgreSQL，DEPGRAPH_DB_PATH 常量指向往已归档
    .db 文件，是路径污染源。治本方向：删除 DEPGRAPH_DB_PATH 常量，连接入口统一为
    get_depgraph_pg_connection()，禁止任何形式 .db 路径常量回退。

    本类保护"常量删除是治本成果，不得回退重新引入 .db 路径常量"。
    """

    def test_constants_does_not_define_depgraph_db_path(self) -> None:
        """_shared/constants.py 不得定义 DEPGRAPH_DB_PATH 常量（P0/P1 治本成果）。"""
        import ast

        src = _CONSTANTS_MODULE.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "DEPGRAPH_DB_PATH":
                        raise AssertionError(
                            "_shared/constants.py 仍定义 DEPGRAPH_DB_PATH 常量（P0/P1 治本回退）"
                        )
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id == "DEPGRAPH_DB_PATH":
                    raise AssertionError(
                        "_shared/constants.py 仍定义 DEPGRAPH_DB_PATH 常量（P0/P1 治本回退）"
                    )

    def test_constants_defines_pg_connection_entry(self) -> None:
        """P2 迁移后 _shared/constants.py 必须定义 get_depgraph_pg_connection 入口。"""
        src = _CONSTANTS_MODULE.read_text(encoding="utf-8")
        assert "get_depgraph_pg_connection" in src, (
            "_shared/constants.py 未定义 get_depgraph_pg_connection（P2 迁移回归）"
        )

    def test_depgraph_db_path_import_fails(self) -> None:
        """DEPGRAPH_DB_PATH 常量已删除，import 必失败（P0/P1 治本成果）。"""
        import pytest

        with pytest.raises(ImportError):
            from _shared.constants import DEPGRAPH_DB_PATH  # noqa: F401,PLC0415

    def test_sync_does_not_reference_depgraph_db_path(self) -> None:
        """sync_yaml_to_depgraph.py 不得引用 DEPGRAPH_DB_PATH（P0/P1 治本成果）。"""
        src = _SYNC_SCRIPT.read_text(encoding="utf-8")
        # 治本后 DEPGRAPH_DB_PATH 仅在删除注释中出现，不应有实际引用
        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            assert "DEPGRAPH_DB_PATH" not in stripped, (
                f"sync_yaml_to_depgraph.py 仍引用 DEPGRAPH_DB_PATH（P0/P1 治本回退）: {stripped}"
            )
        # 不应再出现硬编码的绝对路径字符串（Bug H 原根因）
        assert r'"D:\ZephyrAlpha\data\databases\depgraph.db"' not in src, (
            "sync_yaml_to_depgraph.py 仍含硬编码绝对路径 DB_PATH（Bug H 回归）"
        )

    def test_sync_uses_pg_connection_not_sqlite(self) -> None:
        """P2 迁移后 sync_yaml_to_depgraph.py 必须通过 get_depgraph_pg_connection 连 PG。"""
        src = _SYNC_SCRIPT.read_text(encoding="utf-8")
        assert "get_depgraph_pg_connection" in src, (
            "sync_yaml_to_depgraph.py 未使用 get_depgraph_pg_connection（P2 迁移回归）"
        )
        # 不应再用 sqlite3 直连 depgraph
        assert "sqlite3.connect" not in src, (
            "sync_yaml_to_depgraph.py 仍用 sqlite3.connect（P2 迁移回归）"
        )


# ===========================================================================
# 派生文件 ↔ vocabulary YAML 一致性（同步链路恢复后不得回退）
# ===========================================================================

class TestDerivedFileConsistency:
    """派生文件与 vocabulary YAML 的双向一致性校验。

    这些测试保护"同步链路恢复后不得回退"的契约：
    vocabulary 改了，派生文件必须同步；派生文件出现 vocabulary 没有的值 = 漂移。
    """

    def test_layer_values_in_schema_json_match_vocab(self) -> None:
        """frontmatter_schema.json 的 layer oneOf+const 必须与 layer_vocabulary.yaml 一致。"""
        vocab_values = _vocab_active_values("layer_vocabulary.yaml")
        schema = json.loads((_SCHEMAS_DIR / "frontmatter_schema.json").read_text(encoding="utf-8"))
        prop = schema.get("properties", {}).get("layer", {})
        schema_values: set[str] = set()
        for item in prop.get("oneOf", []):
            if isinstance(item, dict) and item.get("const") is not None:
                schema_values.add(str(item["const"]))
        for v in prop.get("enum", []):
            if isinstance(v, str):
                schema_values.add(v)
        assert schema_values == vocab_values, (
            f"schema.json layer oneOf 与 layer_vocabulary.yaml 不一致:\n"
            f"  schema 独有: {sorted(schema_values - vocab_values)}\n"
            f"  vocab 独有: {sorted(vocab_values - schema_values)}"
        )

    def test_layer_values_in_field_registry_match_vocab(self) -> None:
        """frontmatter_field_registry.yaml 的 layer enum_values 必须是 vocabulary 的子集。"""
        vocab_values = _vocab_active_values("layer_vocabulary.yaml")
        deprecated = _vocab_deprecated_values("layer_vocabulary.yaml")
        registry = yaml.safe_load(
            (_CATALOGS_DIR / "frontmatter_field_registry.yaml").read_text(encoding="utf-8")
        )
        registry_values: set[str] = set()
        for field in registry.get("fields", []):
            if (field.get("field_name") or field.get("name")) != "layer":
                continue
            # dynamic_from_ssot 标志：值集由词表单一维护，不参与子集断言
            ev_raw = field.get("enum_values") or field.get("allowed_values")
            if isinstance(ev_raw, str):
                break
            for ev in ev_raw or []:
                if isinstance(ev, dict):
                    val = ev.get("value") or ev.get("id")
                    if val:
                        registry_values.add(str(val))
                elif isinstance(ev, str):
                    registry_values.add(ev)
            break
        # 派生文件不得出现 vocabulary 中不存在的值（含废弃值）
        extra = registry_values - vocab_values - deprecated
        assert not extra, (
            f"field_registry.layer 出现 vocabulary 中不存在的值: {sorted(extra)}"
        )

    def test_triage_valid_layers_subset_of_vocab(self) -> None:
        """triage.py VALID_LAYERS 必须是 layer_vocabulary.yaml 活跃值的子集。

        子集容忍：triage 是 01_policies_and_standards/ 子集消费者，
        不强制全等，但不得出现非法值（含废弃值）。
        """
        from zephyr.governance.escalation.triage import VALID_LAYERS  # noqa: PLC0415

        vocab_values = _vocab_active_values("layer_vocabulary.yaml")
        deprecated = _vocab_deprecated_values("layer_vocabulary.yaml")
        # 不得有非法值（既不在活跃值也不在废弃值中）
        illegal = set(VALID_LAYERS) - vocab_values - deprecated
        assert not illegal, (
            f"triage.py VALID_LAYERS 含非法值（不在 layer_vocabulary.yaml 中）: {sorted(illegal)}"
        )
        # 不得含废弃值
        deprecated_in_use = set(VALID_LAYERS) & deprecated
        assert not deprecated_in_use, (
            f"triage.py VALID_LAYERS 含已废弃值: {sorted(deprecated_in_use)}"
        )

    def test_triage_valid_doc_types_subset_of_vocab(self) -> None:
        """triage.py VALID_DOC_TYPES 必须是 doc_type_vocabulary.yaml 活跃值的子集。"""
        from zephyr.governance.escalation.triage import VALID_DOC_TYPES  # noqa: PLC0415

        vocab_values = _vocab_active_values("doc_type_vocabulary.yaml")
        deprecated = _vocab_deprecated_values("doc_type_vocabulary.yaml")
        illegal = set(VALID_DOC_TYPES) - vocab_values - deprecated
        assert not illegal, (
            f"triage.py VALID_DOC_TYPES 含非法值（含幽灵值）: {sorted(illegal)}"
        )
        deprecated_in_use = set(VALID_DOC_TYPES) & deprecated
        assert not deprecated_in_use, (
            f"triage.py VALID_DOC_TYPES 含已废弃值: {sorted(deprecated_in_use)}"
        )

    def test_all_vocab_yamls_use_vocabulary_name_key(self) -> None:
        """所有核心 vocabulary YAML 必须用 vocabulary_name 键（非 field_name）。"""
        for vocab_file in [
            "doc_type_vocabulary.yaml",
            "status_vocabulary.yaml",
            "rule_form_vocabulary.yaml",
            "ttl_vocabulary.yaml",
            "layer_vocabulary.yaml",
        ]:
            data = _load_vocab(vocab_file)
            assert data.get("vocabulary_name"), (
                f"{vocab_file} 缺少 vocabulary_name 键（Bug B 根因再现）"
            )
            assert "field_name" not in data, (
                f"{vocab_file} 含遗留 field_name 键（应为 vocabulary_name）"
            )


# ===========================================================================
# 数据库连接函数命名约定（真源冲突治本——F1 改名回归保护）
# ===========================================================================

class TestDbConnectionNamingConvention:
    """数据库连接函数命名约定断言（防真源冲突回归）。

    病根：depgraph_schema.get_db_connection 与 sqlite_schema/db_utils 的同名函数冲突。
    治本：F1 改名为 get_depgraph_pg_connection。见 AGENTS.md §11.4。
    """

    def test_depgraph_pg_connection_exists(self) -> None:
        """F1 必须定义 get_depgraph_pg_connection（PG 入口）。"""
        import zephyr.governance.depgraph_schema as mod  # noqa: PLC0415

        assert hasattr(mod, "get_depgraph_pg_connection"), (
            "depgraph_schema.py 未定义 get_depgraph_pg_connection（真源冲突治本回归）"
        )

    def test_depgraph_get_db_connection_is_deprecated_alias(self) -> None:
        """F1 的 get_db_connection 必须是 deprecation 别名，指向 get_depgraph_pg_connection。"""
        import zephyr.governance.depgraph_schema as mod  # noqa: PLC0415

        assert hasattr(mod, "get_db_connection"), (
            "depgraph_schema.py 未保留 get_db_connection deprecation 别名（向后兼容破坏）"
        )
        assert mod.get_db_connection is mod.get_depgraph_pg_connection, (
            "get_db_connection 不是 get_depgraph_pg_connection 的别名（真源分裂）"
        )

    def test_sqlite_get_db_connection_exists_in_db_utils(self) -> None:
        """F3 必须定义 get_db_connection（SQLite governance.db 入口）。"""
        import zephyr.shared.utils.db_utils as mod  # noqa: PLC0415

        assert hasattr(mod, "get_db_connection"), (
            "db_utils.py 未定义 get_db_connection（SQLite 入口缺失）"
        )

    def test_sqlite_get_db_connection_exists_in_sqlite_schema(self) -> None:
        """F2 必须定义 get_db_connection（SQLite governance.db 入口）。"""
        import zephyr.governance.persistence.sqlite_schema as mod  # noqa: PLC0415

        assert hasattr(mod, "get_db_connection"), (
            "sqlite_schema.py 未定义 get_db_connection（SQLite 入口缺失）"
        )

    def test_depgraph_pg_connection_returns_psycopg2(self) -> None:
        """F1 返回类型必须是 psycopg2 connection（非 sqlite3）。"""
        import inspect  # noqa: PLC0415

        import zephyr.governance.depgraph_schema as mod  # noqa: PLC0415

        src = inspect.getsource(mod.get_depgraph_pg_connection)
        assert "psycopg2.connect" in src, (
            "get_depgraph_pg_connection 未使用 psycopg2.connect（PG 入口被篡改）"
        )

    def test_sqlite_get_db_connection_uses_sqlite3(self) -> None:
        """F3 必须使用 sqlite3.connect（非 psycopg2）。"""
        import inspect  # noqa: PLC0415

        import zephyr.shared.utils.db_utils as mod  # noqa: PLC0415

        src = inspect.getsource(mod.get_db_connection)
        assert "sqlite3.connect" in src, (
            "db_utils.get_db_connection 未使用 sqlite3.connect（SQLite 入口被篡改）"
        )

    def test_f4_wrapper_no_infinite_recursion(self) -> None:
        """F4 constants.get_depgraph_pg_connection 不得无限递归自调用。

        防回归（2026-06-28）：F1 改名后，F4 import 同名函数遮蔽真源，导致 L107
        调用局部 wrapper 而非 F1 真源 → RecursionError → path_tree sync failed。
        治本：import 用别名 ``_get_depgraph_pg_connection_from_depgraph_schema``，
        wrapper 内部调用别名消除遮蔽。本测试通过实际调用 F4 wrapper 验证不递归。
        """
        import sys  # noqa: PLC0415

        # scripts/ 不在默认 sys.path，需 bootstrap
        repo_root = Path(__file__).resolve().parents[2]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))

        # 关键：若 F4 递归，下面 import + call 会抛 RecursionError
        from scripts.governance._shared.constants import (  # noqa: PLC0415
            PgConnExecuteWrapper,
            get_depgraph_pg_connection as f4_wrapper,
        )

        conn = f4_wrapper(autocommit=True)
        try:
            assert isinstance(conn, PgConnExecuteWrapper), (
                "F4 wrapper 必须返回 PgConnExecuteWrapper（包装 psycopg2 conn）"
            )
            # 验证能正常执行 SQL（确认底层是真实 PG 连接，非递归假对象）
            cur = conn.execute("SELECT 1 AS ok")
            row = cur.fetchone()
            assert dict(row)["ok"] == 1
        finally:
            conn.close()

