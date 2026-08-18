# [A_test] module_id: MOD-GOV_capability_lookup_audit_log_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_capability_lookup_audit_log
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_capability_lookup_audit_log.py — capability_lookup audit log 落盘 e2e smoke test

#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S3 Phase 2 治本 G3：
验证 capability_lookup.find / get 调用时正确写入 audit log 到
.runtime/lookup_audit/<session_id>.jsonl，与 rule_discovery_server.write_lookup_audit_log
对称。CAPABILITY-LOOKUP-REQUIRED gate 据此识别 Python API 路径的调用。

测试组：
- TestWriteLookupAuditLog: 模块级 write_lookup_audit_log 函数（直接调用）
- TestFindWritesAuditLog: CapabilityLookup.find 调用 → audit log 落盘
- TestGetWritesAuditLog: CapabilityLookup.get 调用 → audit log 落盘
- TestSessionIdResolution: session_id 参数 / ZEPHYR_SESSION_ID env var 优先级
- TestGateIntegration: audit log 写入 → gate 读取 → entry count > 0 放行
- TestBackwardCompat: 无 session_id 时不写 audit log（向后兼容）

测试隔离：使用 tmp_path + monkeypatch 替换 LOOKUP_AUDIT_DIR，不污染真实 .runtime/。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


SAMPLE_YAML = """
schema_version: "1.1.0"
capabilities:
  - capability_id: test_cap
    aliases:
      - canonical
      - 测试
    description: "A test capability for audit log smoke test"
"""


def _write_yaml(tmp_path: Path, content: str = SAMPLE_YAML) -> Path:
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(content, encoding="utf-8")
    return yaml_path


# ---------------------------------------------------------------------------
# TestWriteLookupAuditLog
# ---------------------------------------------------------------------------


class TestWriteLookupAuditLog:
    """模块级 write_lookup_audit_log 函数测试。"""

    def test_writes_jsonl_entry(self, tmp_path: Path):
        """write_lookup_audit_log 写入 JSONL 条目，格式与 rule_discovery_server 对称。"""
        from zephyr.governance.capability_lookup import write_lookup_audit_log
        audit_dir = tmp_path / "lookup_audit"
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
        ):
            write_lookup_audit_log(
                session_id="sess-test-001",
                query={"query": "session handoff"},
                result_count=2,
                capability_ids=["session_handoff", "doc_guard"],
                tool="capability_lookup.find",
            )
        log_path = audit_dir / "sess-test-001.jsonl"
        assert log_path.is_file(), f"audit log 文件应已创建: {log_path}"
        content = log_path.read_text(encoding="utf-8").strip()
        entry = json.loads(content)
        assert entry["tool"] == "capability_lookup.find"
        assert entry["query"] == {"query": "session handoff"}
        assert entry["result_count"] == 2
        assert entry["rule_ids"] == ["session_handoff", "doc_guard"]
        assert "ts" in entry, "entry 必须含 ts 字段（ISO 8601 时间戳）"

    def test_appends_to_existing_log(self, tmp_path: Path):
        """多次调用追加到同一 session log 文件（不覆盖）。"""
        from zephyr.governance.capability_lookup import write_lookup_audit_log
        audit_dir = tmp_path / "lookup_audit"
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
        ):
            write_lookup_audit_log(
                session_id="sess-append",
                query={"query": "first"},
                result_count=1,
                capability_ids=["cap_a"],
            )
            write_lookup_audit_log(
                session_id="sess-append",
                query={"query": "second"},
                result_count=0,
                capability_ids=[],
            )
        log_path = audit_dir / "sess-append.jsonl"
        lines = [
            line for line in log_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(lines) == 2, f"应有 2 条 entry（追加模式），实际 {len(lines)}"
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        assert first["query"] == {"query": "first"}
        assert second["query"] == {"query": "second"}

    def test_empty_session_id_skipped(self, tmp_path: Path):
        """空 session_id / 'unknown' / 'none' / 'null' → 跳过 audit log。"""
        from zephyr.governance.capability_lookup import write_lookup_audit_log
        audit_dir = tmp_path / "lookup_audit"
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
        ):
            for invalid_sid in ["", "unknown", "none", "null"]:
                write_lookup_audit_log(
                    session_id=invalid_sid,
                    query={"query": "x"},
                    result_count=0,
                    capability_ids=[],
                )
        assert not audit_dir.exists() or not any(audit_dir.iterdir()), \
            "无效 session_id 不应写入任何 audit log"

    def test_fail_open_on_os_error(self, tmp_path: Path):
        """OSError 时 fail-open（logger.warning 不抛异常）。"""
        from zephyr.governance.capability_lookup import write_lookup_audit_log
        # 模拟 mkdir 失败（路径是文件而非目录）
        blocker = tmp_path / "lookup_audit"
        blocker.write_text("blocker", encoding="utf-8")
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", blocker
        ):
            # 不应抛异常
            write_lookup_audit_log(
                session_id="sess-fail",
                query={"query": "x"},
                result_count=0,
                capability_ids=[],
            )


# ---------------------------------------------------------------------------
# TestFindWritesAuditLog
# ---------------------------------------------------------------------------


class TestFindWritesAuditLog:
    """CapabilityLookup.find 调用 → audit log 落盘。"""

    def test_find_with_session_id_writes_log(self, tmp_path: Path):
        """find(query, session_id='xxx') 写入 audit log。"""
        from zephyr.governance.capability_lookup import CapabilityLookup
        yaml_path = _write_yaml(tmp_path)
        audit_dir = tmp_path / "lookup_audit"
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
        ):
            reg = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
            results = reg.find("test", session_id="sess-find-001")
        assert len(results) >= 1, "find 应至少命中 test_cap"
        log_path = audit_dir / "sess-find-001.jsonl"
        assert log_path.is_file(), f"audit log 应已创建: {log_path}"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["tool"] == "capability_lookup.find"
        assert entry["query"] == {"query": "test"}
        assert entry["result_count"] == len(results)
        assert "test_cap" in entry["rule_ids"]

    def test_find_without_session_id_no_log(self, tmp_path: Path):
        """find(query) 无 session_id 且无 env var → 不写 audit log（向后兼容）。"""
        from zephyr.governance.capability_lookup import CapabilityLookup
        yaml_path = _write_yaml(tmp_path)
        audit_dir = tmp_path / "lookup_audit"
        # 确保 env var 未设置
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ZEPHYR_SESSION_ID", None)
            with patch(
                "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
            ):
                reg = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
                results = reg.find("test")
        assert len(results) >= 1, "find 仍应正常返回结果"
        assert not audit_dir.exists() or not any(audit_dir.iterdir()), \
            "无 session_id 时不应写 audit log"


# ---------------------------------------------------------------------------
# TestGetWritesAuditLog
# ---------------------------------------------------------------------------


class TestGetWritesAuditLog:
    """CapabilityLookup.get 调用 → audit log 落盘。"""

    def test_get_existing_writes_log(self, tmp_path: Path):
        """get(capability_id, session_id='xxx') 写入 audit log，含命中条目。"""
        from zephyr.governance.capability_lookup import CapabilityLookup
        yaml_path = _write_yaml(tmp_path)
        audit_dir = tmp_path / "lookup_audit"
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
        ):
            reg = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
            result = reg.get("test_cap", session_id="sess-get-001")
        assert result is not None, "test_cap 应存在"
        log_path = audit_dir / "sess-get-001.jsonl"
        assert log_path.is_file()
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["tool"] == "capability_lookup.get"
        assert entry["query"] == {"capability_id": "test_cap"}
        assert entry["result_count"] == 1
        assert entry["rule_ids"] == ["test_cap"]

    def test_get_not_found_writes_log(self, tmp_path: Path):
        """get(不存在的 id, session_id='xxx') 也写 audit log（result_count=0）。"""
        from zephyr.governance.capability_lookup import CapabilityLookup
        yaml_path = _write_yaml(tmp_path)
        audit_dir = tmp_path / "lookup_audit"
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
        ):
            reg = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
            result = reg.get("nonexistent", session_id="sess-get-404")
        assert result is None
        log_path = audit_dir / "sess-get-404.jsonl"
        assert log_path.is_file()
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["result_count"] == 0
        assert entry["rule_ids"] == []


# ---------------------------------------------------------------------------
# TestSessionIdResolution
# ---------------------------------------------------------------------------


class TestSessionIdResolution:
    """session_id 参数 / ZEPHYR_SESSION_ID env var 优先级。"""

    def test_param_overrides_env(self, tmp_path: Path):
        """session_id 参数优先于 ZEPHYR_SESSION_ID 环境变量。"""
        from zephyr.governance.capability_lookup import CapabilityLookup
        yaml_path = _write_yaml(tmp_path)
        audit_dir = tmp_path / "lookup_audit"
        with patch.dict(os.environ, {"ZEPHYR_SESSION_ID": "env-session"}):
            with patch(
                "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
            ):
                reg = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
                reg.find("test", session_id="param-session")
        # 参数优先 → log 文件名应是 param-session
        assert (audit_dir / "param-session.jsonl").is_file()
        assert not (audit_dir / "env-session.jsonl").exists()

    def test_env_var_fallback(self, tmp_path: Path):
        """无 session_id 参数时回退到 ZEPHYR_SESSION_ID 环境变量。"""
        from zephyr.governance.capability_lookup import CapabilityLookup
        yaml_path = _write_yaml(tmp_path)
        audit_dir = tmp_path / "lookup_audit"
        with patch.dict(os.environ, {"ZEPHYR_SESSION_ID": "env-fallback"}):
            with patch(
                "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
            ):
                reg = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
                reg.find("test")
        assert (audit_dir / "env-fallback.jsonl").is_file(), \
            "无参数时应回退到 ZEPHYR_SESSION_ID 环境变量"


# ---------------------------------------------------------------------------
# TestGateIntegration
# ---------------------------------------------------------------------------


class TestGateIntegration:
    """audit log 写入 → CAPABILITY-LOOKUP-REQUIRED gate 读取 → entry count > 0 放行。"""

    def test_find_then_gate_passes(self, tmp_path: Path):
        """e2e: find() 写 log → gate 读取 → entry count > 0 放行。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            _count_valid_log_entries,
        )
        from zephyr.governance.capability_lookup import CapabilityLookup
        yaml_path = _write_yaml(tmp_path)
        audit_dir = tmp_path / "lookup_audit"
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
        ):
            reg = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
            reg.find("test", session_id="sess-e2e")
        # 验证 gate 能读取并计数
        log_path = audit_dir / "sess-e2e.jsonl"
        count, err = _count_valid_log_entries(log_path)
        assert err is None, f"audit log 不应有解析错误: {err}"
        assert count >= 1, f"应至少有 1 条有效 entry，实际 {count}"

    def test_no_log_then_gate_blocks(self, tmp_path: Path):
        """e2e: 未调用 find() → log 不存在 → gate 阻断（entry_count=0）。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import (
            _count_valid_log_entries,
        )
        log_path = tmp_path / "never-called.jsonl"
        count, err = _count_valid_log_entries(log_path)
        assert err is None
        assert count == 0, "未调用的 session 应有 0 条 entry"


# ---------------------------------------------------------------------------
# TestBackwardCompat
# ---------------------------------------------------------------------------


class TestBackwardCompat:
    """向后兼容：旧调用方式（无 session_id）不应破坏。"""

    def test_find_returns_same_results_with_or_without_session(self, tmp_path: Path):
        """find(query) 与 find(query, session_id='x') 返回相同结果。"""
        from zephyr.governance.capability_lookup import CapabilityLookup
        yaml_path = _write_yaml(tmp_path)
        audit_dir = tmp_path / "lookup_audit"
        # 无 session_id
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ZEPHYR_SESSION_ID", None)
            reg1 = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
            results_no_sid = reg1.find("test")
        # 有 session_id
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
        ):
            reg2 = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
            results_with_sid = reg2.find("test", session_id="sess-bc")
        assert results_no_sid == results_with_sid, \
            "session_id 参数不应影响 find() 返回结果"

    def test_get_returns_same_results_with_or_without_session(self, tmp_path: Path):
        """get(id) 与 get(id, session_id='x') 返回相同结果。"""
        from zephyr.governance.capability_lookup import CapabilityLookup
        yaml_path = _write_yaml(tmp_path)
        audit_dir = tmp_path / "lookup_audit"
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ZEPHYR_SESSION_ID", None)
            reg1 = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
            r1 = reg1.get("test_cap")
        with patch(
            "zephyr.governance.capability_lookup.LOOKUP_AUDIT_DIR", audit_dir
        ):
            reg2 = CapabilityLookup(yaml_path=yaml_path, scan_root=tmp_path, scan=False)
            r2 = reg2.get("test_cap", session_id="sess-bc")
