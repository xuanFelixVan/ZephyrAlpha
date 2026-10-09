# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/batch_creation_tokens.py | §
# [MODULE] tests.governance.d3_metadata.test_batch_creation_tokens
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.governance.d3_metadata.batch_creation_tokens
# [CONSUMERS] 批量 token 工具质量守卫（意图 API 薄壳编排/幂等/W4 防呆/直写轨退役不变量）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例 monkeypatch 账本三步注入点（api.register/publish_snapshot/projection run），
#   不碰生产 PG；直写轨退役不变量=登记全程投影 YAML 字节零变化
# [MODIFY-GUARD] 2026-10-09 st-regsolo-20261010 随裁定#502 直写轨退役同批重写（原插入锚/守恒闸/
#   CAS 回滚用例随被删机械退役，语义由账本层测试 tests/governance/test_registry_ledger.py 承接）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""batch_creation_tokens 工具测试——裁定#502 直写轨退役后的意图 API 薄壳守卫。

三层断言面：
1. 编排正确性：register 逐条 payload / publish 一次 / render 一次 / 落位校验。
2. 幂等与失败面：OK_NOOP 跳过、CONFLICT_DUPLICATE WARN 继续、登记失败不 publish。
3. 退役不变量：全程不触碰投影 YAML 字节；锚点参数收下忽略。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

import scripts.governance.d3_metadata.batch_creation_tokens as bct

_API_REG = "zephyr.governance.registry_ledger.api.register"
_PUBLISH = "zephyr.governance.registry_ledger.baseline.publish_snapshot"
_PROJ_RUN = "zephyr.governance.registry_projection.projection_generator.run"


class _Result:
    """api.Result 形状最小替身（code/detail 契约）。"""

    def __init__(self, code: str, detail: dict | None = None):
        self.code = code
        self.detail = detail or {}


@pytest.fixture()
def ledger(tmp_path: Path, monkeypatch):
    """账本三步注入点替身 + tmp 投影册（登记全程字节零变化断言基线）。"""
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(
        "creation_tokens:\n- file: docs/existing/a.md\n  token: a-token-20260913\n"
        "  created_by: someone\n  capability: cap\ndi_seam_exemptions:\n- module_path: fake.Thing\n  reason: test\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(bct, "_REGISTRY", reg)
    monkeypatch.setattr(bct, "_REPO", tmp_path)

    state = {"registered": [], "publish_calls": 0, "render_calls": 0}

    def fake_register(registry_id, family_key, payload, *, reason, session_id, actor_kind="agent", **kw):
        assert registry_id == bct._REGISTRY_ID
        assert family_key == bct._FAMILY
        assert len(str(reason)) >= 10
        state["registered"].append(dict(payload))
        return _Result("OK", {"entry_key": f"file={payload['file']}|token={payload['token']}"})

    def fake_publish(registry_id, *, repo_root=None, session_id="", **kw):
        state["publish_calls"] += 1
        assert repo_root == tmp_path
        return {"registry_id": registry_id, "noop": False, "snapshot_version": 999, "entry_count": 1}

    def fake_render(root, mode="check", **kw):
        state["render_calls"] += 1
        assert mode == "render"
        assert kw.get("registry_id") == bct._REGISTRY_ID
        assert kw.get("physical_path") == bct._REGISTRY_REL

        class R:
            ok = True
            quadrant = "clean"
            wrote = False
            evidence_path = ""
            detail = {"ledger_revision": 999}

            def to_dict(self):
                return {}

        return R()

    monkeypatch.setattr(_API_REG, fake_register)
    monkeypatch.setattr(_PUBLISH, fake_publish)
    monkeypatch.setattr(_PROJ_RUN, fake_render)
    monkeypatch.setattr(bct, "_registered_files_from_ledger", lambda: {e["file"] for e in state["registered"]})
    return state, reg


def _block(n: int = 2, created_by: str = "st-test") -> str:
    return bct.build_block(
        [f"docs/_working/lab/seg_{i:03d}.md" for i in range(1, n + 1)], created_by, "lab_cap", "20261009"
    )


def test_happy_path_registers_publishes_renders(ledger):
    state, _ = ledger
    bct.insert_block(_block(3), "lab_cap", expect_files=[f"docs/_working/lab/seg_{i:03d}.md" for i in range(1, 4)])
    assert len(state["registered"]) == 3
    assert state["publish_calls"] == 1
    assert state["render_calls"] == 1
    payloads = state["registered"]
    assert payloads[0]["token"] == "lab-cap-seg-001-20261009"
    assert payloads[0]["created_by"] == "st-test"
    assert payloads[0]["capability"] == "lab_cap"
    assert set(payloads[0]) == {"file", "token", "created_by", "capability"}


def test_merge_evaluation_lands_in_payload(ledger):
    state, _ = ledger
    block = bct.build_block(["docs/x.md"], "st-test", "lab_cap", "20261009", merge_evaluation="零同域消费方，新对象")
    bct.insert_block(block, "lab_cap")
    assert state["registered"][0]["merge_evaluation"] == "零同域消费方，新对象"


def test_idempotent_noop_skipped(ledger, monkeypatch):
    state, _ = ledger
    monkeypatch.setattr(_API_REG, lambda *a, **k: _Result("OK_NOOP", {"version": 5}))
    monkeypatch.setattr(bct, "_registered_files_from_ledger", lambda: {"docs/_working/lab/seg_001.md"})
    bct.insert_block(_block(1), "lab_cap", expect_files=["docs/_working/lab/seg_001.md"])
    assert state["publish_calls"] == 1  # noop 也走发布（幂等由发布层自判）


def test_conflict_duplicate_warns_and_continues(ledger, monkeypatch, capsys):
    state, _ = ledger
    codes = iter(["OK", "CONFLICT_DUPLICATE", "OK"])

    def fake_register(*a, **k):
        return _Result(next(codes), {"entry_key": "x"})

    monkeypatch.setattr(_API_REG, fake_register)
    bct.insert_block(_block(3), "lab_cap")
    assert state["publish_calls"] == 1
    assert "CONFLICT_DUPLICATE" in capsys.readouterr().err


def test_register_reject_code_aborts_before_publish(ledger, monkeypatch):
    state, _ = ledger
    monkeypatch.setattr(_API_REG, lambda *a, **k: _Result("SCHEMA_INVALID", {"cause": "bad payload"}))
    with pytest.raises(bct.TokenInsertError, match="SCHEMA_INVALID"):
        bct.insert_block(_block(2), "lab_cap")
    assert state["publish_calls"] == 0
    assert state["render_calls"] == 0


def test_register_exception_wraps_as_token_insert_error(ledger, monkeypatch):
    state, _ = ledger

    def boom(*a, **k):
        raise RuntimeError("pg unreachable")

    monkeypatch.setattr(_API_REG, boom)
    with pytest.raises(bct.TokenInsertError, match="pg unreachable"):
        bct.insert_block(_block(1), "lab_cap")
    assert state["publish_calls"] == 0


def test_render_failure_raises(ledger, monkeypatch):
    class BadR:
        ok = False
        quadrant = "conflict"
        wrote = False
        evidence_path = "evidence.diff"
        detail = {"error": "self-check failed"}

        def to_dict(self):
            return {}

    monkeypatch.setattr(_PROJ_RUN, lambda root, mode="check", **k: BadR())
    with pytest.raises(bct.TokenInsertError, match="conflict"):
        bct.insert_block(_block(1), "lab_cap")


def test_verify_landing_missing_raises(ledger, monkeypatch):
    monkeypatch.setattr(bct, "_registered_files_from_ledger", lambda: set())
    with pytest.raises(bct.TokenInsertError, match="未落位"):
        bct.insert_block(_block(1), "lab_cap", expect_files=["docs/_working/lab/seg_001.md"])


def test_verify_landing_unavailable_raises(ledger, monkeypatch):
    monkeypatch.setattr(bct, "_registered_files_from_ledger", lambda: None)
    with pytest.raises(bct.TokenInsertError, match="落位校验不可用"):
        bct.insert_block(_block(1), "lab_cap", expect_files=["docs/_working/lab/seg_001.md"])


def test_registration_never_touches_projection_yaml_bytes(ledger):
    """直写轨退役核心不变量：登记全程投影册字节零变化。"""
    state, reg = ledger
    before = reg.read_bytes()
    bct.insert_block(_block(3), "lab_cap")
    assert reg.read_bytes() == before


def test_parse_block_entries_rejects_bad_token():
    with pytest.raises(bct.TokenInsertError, match="token 非法格式"):
        bct._parse_block_entries("- file: a.md\n  token: BAD_TOKEN!\n  created_by: s\n  capability: c\n")


def test_parse_block_entries_rejects_missing_keys():
    with pytest.raises(bct.TokenInsertError, match="缺必填键"):
        bct._parse_block_entries("- file: a.md\n  created_by: s\n")


def test_parse_block_entries_rejects_non_list():
    with pytest.raises(bct.TokenInsertError, match="非 YAML 列表|非非空列表"):
        bct._parse_block_entries("creation_tokens: []\n")


def test_parse_block_entries_drops_none_fields(ledger):
    entries = bct._parse_block_entries("- file: a.md\n  token: abc-token-20260913\n  created_by: s\n  capability: c\n")
    assert entries == [{"file": "a.md", "token": "abc-token-20260913", "created_by": "s", "capability": "c"}]


def test_resolve_anchor_passthrough():
    assert bct.resolve_anchor("  capability: x\n", "wanted") == "wanted"


def test_load_registered_ledger_first(ledger, monkeypatch):
    monkeypatch.setattr(bct, "_registered_files_from_ledger", lambda: {"docs/ledger/a.md"})
    assert bct.load_registered() == {"docs/ledger/a.md"}


def test_load_registered_yaml_fallback_when_ledger_down(ledger, monkeypatch):
    state, reg = ledger
    monkeypatch.setattr(bct, "_registered_files_from_ledger", lambda: None)
    assert bct.load_registered() == {"docs/existing/a.md"}


def test_cli_dry_run_zero_write(ledger, monkeypatch, capsys):
    state, _ = ledger
    monkeypatch.setattr(bct, "_git_output", lambda *a: ["docs/_working/lab/new.md"] if "ls-files" in a else [])
    monkeypatch.setattr(
        sys,
        "argv",
        ["bct", "--prefix", "docs/_working/lab", "--created-by", "st-x", "--capability", "lab", "--dry-run"],
    )
    assert bct.main() == 0
    out = capsys.readouterr().out
    assert "DRY-RUN" in out
    assert state["registered"] == [] and state["publish_calls"] == 0 and state["render_calls"] == 0


def test_cli_real_run_end_to_end(ledger, monkeypatch, capsys):
    state, reg = ledger
    before = reg.read_bytes()
    monkeypatch.setattr(bct, "_git_output", lambda *a: ["docs/_working/lab/new.md"] if "ls-files" in a else [])
    monkeypatch.setattr(
        sys, "argv", ["bct", "--prefix", "docs/_working/lab", "--created-by", "st-x", "--capability", "lab"]
    )
    assert bct.main() == 0
    out = capsys.readouterr().out
    assert "OK: 已登记 1 条" in out
    assert len(state["registered"]) == 1
    assert reg.read_bytes() == before  # 退役不变量：CLI 全程不写投影册


def test_cli_wide_prefix_blocked_without_flag(ledger, monkeypatch, capsys):
    state, _ = ledger
    monkeypatch.setattr(
        bct, "_git_output", lambda *a: [f"d{i % 2}/f{i}.md" for i in range(60)] if "ls-files" in a else []
    )
    monkeypatch.setattr(sys, "argv", ["bct", "--prefix", "docs", "--created-by", "st-x", "--capability", "lab"])
    assert bct.main() == 1
    assert "宽前缀批拦截" in capsys.readouterr().err
    assert state["registered"] == []


def test_cli_anchor_arg_accepted_and_ignored(ledger, monkeypatch, capsys):
    state, _ = ledger
    monkeypatch.setattr(bct, "_git_output", lambda *a: ["docs/_working/lab/new.md"] if "ls-files" in a else [])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "bct",
            "--prefix",
            "docs/_working/lab",
            "--created-by",
            "st-x",
            "--capability",
            "lab",
            "--anchor-capability",
            "whatever",
        ],
    )
    assert bct.main() == 0
    assert "已随直写轨退役" in capsys.readouterr().out


def test_cli_no_new_files_short_circuits(ledger, monkeypatch, capsys):
    state, _ = ledger
    monkeypatch.setattr(bct, "_registered_files_from_ledger", lambda: {"docs/_working/lab/new.md"})
    monkeypatch.setattr(bct, "_git_output", lambda *a: ["docs/_working/lab/new.md"] if "ls-files" in a else [])
    monkeypatch.setattr(
        sys, "argv", ["bct", "--prefix", "docs/_working/lab", "--created-by", "st-x", "--capability", "lab"]
    )
    assert bct.main() == 0
    assert "无待登记文件" in capsys.readouterr().out
    assert state["publish_calls"] == 0


def test_wide_prefix_issues_counts_and_top_dirs():
    issues = bct._wide_prefix_issues([f"a/f{i}.md" for i in range(51)])
    assert any("上限" in i for i in issues)
    issues = bct._wide_prefix_issues(["a/x.md", "b/y.md"])
    assert any("一级目录" in i for i in issues)
    assert bct._wide_prefix_issues(["a/x.md"]) == []


def test_yaml_quote_escapes_and_flattens():
    assert bct._yaml_quote('多"行"\n文本\\x') == '"多\\"行\\" 文本\\\\x"'


def test_build_block_invalid_token_exits():
    # capability 带非法字符 → token "bad!cap-x-20261009" 不匹配 _TOKEN_RE → sys.exit(1)
    with pytest.raises(SystemExit):
        bct.build_block(["docs/x.md"], "s", "bad!cap", "20261009")


def test_detect_file_type_table():
    assert bct.detect_file_type("src/zephyr/x.py") == "new_src_py"
    assert bct.detect_file_type("docs/01_policies_and_standards/_registry/catalogs/x.yaml") == "registry_yaml"
    assert bct.detect_file_type("docs/_working/x.md") == "working_md"
    assert bct.detect_file_type("misc.bin") is None
