# [BLUEPRINT] MOD-GOV_CREATE_GUARD | tests/governance/test_create_guard_dup_tier.py | §create-guard-dup-tier
# [MODULE] tests.governance.test_create_guard_dup_tier
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.create_guard, zephyr.governance.capability_lookup
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 裁定#456 判重腿两档化红证：①探针仅命中 description 散文面⇒不阻断（warn：logger.warning+审计 jsonl 落账）②命中 capability_id/aliases/canonical_file 标识符级⇒仍硬拦（capability_id/alias 两臂）③硬拦与 warn 并存⇒硬拦短路优先且 warn 审计不落账 ④逃生标记 '# create-guard-not-dup: <理由>' 豁免语义零改动 ⑤lookup 缺失 fail-closed 零改动；测试隔离——全部 tmp_path，monkeypatch LOOKUP_AUDIT_DIR 禁写主仓 .runtime，缝注入小型 registry 禁跑全库扫描，禁改 capability_lookup.py
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""test_create_guard_dup_tier.py — 裁定#456：CREATE-GUARD 判重腿两档化红证。

覆盖：
  a) 探针仅命中 description（散文面）⇒ 提交不被此腿阻断（passed=True），
     logger.warning 落裁定#456 警告文案（含逃生标记与 library.lookup 处方）+
     审计 jsonl（.runtime/gate_audit/create_guard_keyword_dup_warn.jsonl）落账；
  b) 命中 capability_id / aliases（标识符级）⇒ 仍硬拦（passed=False，消息含
     capability_id / canonical_override / 逃生标记字面量）；
  c) 硬拦与 warn 并存 ⇒ 硬拦短路优先（warn 审计不落账）；
  d) 逃生标记豁免语义零改动（双档全豁免，无 warn 审计）；
  e) lookup 缺失 fail-closed 行为零改动。

纪律：不改任何既有测试/阈值/skip；全部 tmp_path 隔离。
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import zephyr.governance.capability_lookup as capability_lookup_mod  # noqa: E402
from zephyr.gov_enforcement.commit_gates import create_guard as cg  # noqa: E402

_DESCRIPTION_ONLY_CAP = "__p456_desc_only_cap"
_DESCRIPTION_ONLY_PHRASE = "跨日仓位漂移对账的季度审计摘要生成器红证"
_ID_CAP = "__p456_dedup_engine"
_ALIAS_CAP = "__p456_alias_cap"
_ALIAS_PHRASE = "ledger reconciliation sweep"

_DESC_ONLY_REL = "src/zephyr/data/__p456_prose_surface.py"
_ID_REL = "src/zephyr/foo/__p456_dedup_engine.py"
_ALIAS_REL = "src/zephyr/foo/__p456_ledger_sweep.py"

_DESC_ONLY_SRC = f'"""\n{_DESCRIPTION_ONLY_PHRASE}。\n"""\n\nx = 1\n'
_ID_SRC = "# 标识符级红证：stem 切词 dedup engine 直击 capability_id\n\nx = 1\n"
_ALIAS_SRC = "# 标识符级红证：stem 切词 ledger sweep 经 alias 直击\n\nx = 1\n"
_ESCAPE_SRC = (
    "# create-guard-not-dup: 红证散文面豁免——本文件非在册能力的第二实现\n"
    f'"""\n{_DESCRIPTION_ONLY_PHRASE}。\n"""\n\nx = 1\n'
)


def _desc_only_registry(canonical_rel: str) -> str:
    return f"""
capabilities:
  - capability_id: {_DESCRIPTION_ONLY_CAP}
    description: "跨日仓位漂移对账季度审计摘要生成器（散文面红证在册能力）"
    aliases: []
    canonical_override: {canonical_rel}
creation_tokens: []
"""


def _id_registry(canonical_rel: str) -> str:
    return f"""
capabilities:
  - capability_id: {_ID_CAP}
    description: "完全无关的散文面描述（identifier red proof words）"
    aliases: []
    canonical_override: {canonical_rel}
creation_tokens: []
"""


def _alias_registry(canonical_rel: str) -> str:
    return f"""
capabilities:
  - capability_id: {_ALIAS_CAP}
    description: "unrelated prose entirely different words"
    aliases:
      - "{_ALIAS_PHRASE}"
    canonical_override: {canonical_rel}
creation_tokens: []
"""


def _mixed_registry() -> str:
    return f"""
capabilities:
  - capability_id: {_DESCRIPTION_ONLY_CAP}
    description: "跨日仓位漂移对账季度审计摘要生成器（散文面红证在册能力）"
    aliases: []
    canonical_override: src/zephyr/data/__p456_desc_canon.py
  - capability_id: {_ID_CAP}
    description: "完全无关的散文面描述（identifier red proof words）"
    aliases: []
    canonical_override: src/zephyr/foo/__p456_dedup_canon.py
creation_tokens: []
"""


@pytest.fixture()
def _isolate_env(monkeypatch, tmp_path):
    """审计重定向 + 会话环境变量清空（测试禁写主仓 .runtime；find 审计行为不变）。"""
    monkeypatch.setattr(capability_lookup_mod, "LOOKUP_AUDIT_DIR", tmp_path / "lookup_audit")
    monkeypatch.delenv(capability_lookup_mod.SESSION_ID_ENV_VAR, raising=False)


def _mini_lookup(tmp_path: Path, yaml_text: str):
    repo = tmp_path / "repo"
    reg = repo / "mini_registry.yaml"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(yaml_text, encoding="utf-8")
    scan = repo / "src" / "zephyr"
    scan.mkdir(parents=True, exist_ok=True)
    return capability_lookup_mod.CapabilityLookup(yaml_path=reg, scan_root=[scan], derive_removed=False)


def _write_new_file(repo: Path, rel: str, content: str) -> str:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return rel


def _warn_audit_records(repo: Path) -> list[dict]:
    import json

    audit = repo / ".runtime" / "gate_audit" / "create_guard_keyword_dup_warn.jsonl"
    if not audit.exists():
        return []
    return [json.loads(x) for x in audit.read_text(encoding="utf-8").splitlines() if x.strip()]


class TestDescriptionOnlyHitWarns:
    """红证 a：探针仅命中 description 散文面 ⇒ 不阻断（warn 路径：warning+审计）。"""

    def test_description_only_hit_passes_with_warn_and_audit(self, tmp_path: Path, _isolate_env, caplog) -> None:
        repo = tmp_path / "repo"
        mini = _mini_lookup(tmp_path, _desc_only_registry("src/zephyr/data/__p456_desc_canon.py"))
        rel = _write_new_file(repo, _DESC_ONLY_REL, _DESC_ONLY_SRC)
        gw = SimpleNamespace(project_root=repo)
        with caplog.at_level(logging.WARNING, logger="zephyr.gov_enforcement.commit_gates.create_guard"):
            passed, detail = cg._check_capability_keyword_overlap(gw, [rel], "p456-desc-sid", lookup=mini)
        assert passed is True, f"仅命中 description 散文面不得阻断（裁定#456 warn 化）: {detail!r}"
        assert detail == "", detail
        # 警告文案：裁定#456 + 处方（逃生标记字面量 + library.lookup 正查）
        joined = " ".join(r.getMessage() for r in caplog.records)
        assert "裁定#456" in joined, joined
        assert _DESCRIPTION_ONLY_CAP in joined, joined
        assert "# create-guard-not-dup:" in joined, joined
        assert "python -m zephyr.library.lookup" in joined, joined
        # 既有通道同族审计落账（fail-open jsonl）
        records = _warn_audit_records(repo)
        assert records, "warn 判定必须落账 create_guard_keyword_dup_warn.jsonl"
        assert records[-1]["event"] == "keyword_dup_description_warn"
        assert records[-1]["ruling"] == "456"
        assert any(v["capability_id"] == _DESCRIPTION_ONLY_CAP for v in records[-1]["violations"])


class TestIdentifierHitStillBlocks:
    """红证 b：命中 capability_id / aliases（标识符级）⇒ 仍硬拦。"""

    def test_capability_id_hit_blocks(self, tmp_path: Path, _isolate_env) -> None:
        repo = tmp_path / "repo"
        mini = _mini_lookup(tmp_path, _id_registry("src/zephyr/foo/__p456_dedup_canon.py"))
        rel = _write_new_file(repo, _ID_REL, _ID_SRC)
        gw = SimpleNamespace(project_root=repo)
        passed, detail = cg._check_capability_keyword_overlap(gw, [rel], "p456-id-sid", lookup=mini)
        assert passed is False, f"capability_id 标识符级命中必须维持硬拦: {detail!r}"
        assert _ID_CAP in detail, detail
        assert "canonical_override=" in detail, detail
        assert "# create-guard-not-dup: <一句话理由>" in detail, detail
        assert "裁定#456" in detail, detail
        assert _warn_audit_records(repo) == [], "硬拦路径不得写 warn 审计"

    def test_alias_hit_blocks(self, tmp_path: Path, _isolate_env) -> None:
        repo = tmp_path / "repo"
        mini = _mini_lookup(tmp_path, _alias_registry("src/zephyr/foo/__p456_alias_canon.py"))
        rel = _write_new_file(repo, _ALIAS_REL, _ALIAS_SRC)
        gw = SimpleNamespace(project_root=repo)
        passed, detail = cg._check_capability_keyword_overlap(gw, [rel], "p456-alias-sid", lookup=mini)
        assert passed is False, f"aliases 标识符级命中必须维持硬拦: {detail!r}"
        assert _ALIAS_CAP in detail, detail
        assert _ALIAS_PHRASE.split()[0] in detail or "命中词=" in detail, detail


class TestHardWinsOverWarn:
    """红证 c：硬拦与 warn 并存 ⇒ 硬拦短路优先，warn 审计不落账。"""

    def test_mixed_commit_blocks_and_skips_warn_audit(self, tmp_path: Path, _isolate_env) -> None:
        repo = tmp_path / "repo"
        mini = _mini_lookup(tmp_path, _mixed_registry())
        rel_desc = _write_new_file(repo, _DESC_ONLY_REL, _DESC_ONLY_SRC)
        rel_id = _write_new_file(repo, _ID_REL, _ID_SRC)
        gw = SimpleNamespace(project_root=repo)
        passed, detail = cg._check_capability_keyword_overlap(gw, [rel_desc, rel_id], "p456-mixed-sid", lookup=mini)
        assert passed is False, "并存时必须硬拦（标识符级判死优先）"
        assert _ID_CAP in detail, detail
        assert _DESCRIPTION_ONLY_CAP not in detail, "硬拦消息只列标识符级条目"
        assert _warn_audit_records(repo) == [], "硬拦短路时 warn 审计不得落账"


class TestEscapeAndFailClosedUnchanged:
    """红证 d/e：逃生标记豁免与 fail-closed 语义零改动。"""

    def test_escape_marker_exempts_both_tiers(self, tmp_path: Path, _isolate_env, caplog) -> None:
        repo = tmp_path / "repo"
        mini = _mini_lookup(tmp_path, _desc_only_registry("src/zephyr/data/__p456_desc_canon.py"))
        rel = _write_new_file(repo, _DESC_ONLY_REL, _ESCAPE_SRC)
        gw = SimpleNamespace(project_root=repo)
        with caplog.at_level(logging.WARNING, logger="zephyr.gov_enforcement.commit_gates.create_guard"):
            passed, detail = cg._check_capability_keyword_overlap(gw, [rel], "p456-esc-sid", lookup=mini)
        assert passed is True, f"逃生标记必须整文件豁免（双档全豁免）: {detail!r}"
        assert _warn_audit_records(repo) == [], "豁免文件不得落 warn 审计"
        assert "裁定#456" not in " ".join(r.getMessage() for r in caplog.records)

    def test_missing_lookup_fail_closed(self, tmp_path: Path) -> None:
        gw = SimpleNamespace(project_root=tmp_path)
        passed, detail = cg._check_capability_keyword_overlap(
            gw, ["src/zephyr/x/y.py"], "p456-fc-sid", lookup=None, lookup_error="simulated outage"
        )
        assert passed is False and "fail-closed" in detail, detail
