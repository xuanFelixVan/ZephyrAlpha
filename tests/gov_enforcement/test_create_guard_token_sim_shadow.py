# [BLUEPRINT] MOD-GOV_CREATE_GUARD | tests/gov_enforcement/test_create_guard_token_sim_shadow.py | §create-guard-token-sim-shadow
# [MODULE] tests.gov_enforcement.test_create_guard_token_sim_shadow
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.create_guard, zephyr.governance.capability_lookup
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] S4-B 红证（手术簿 s4_b_token_sim.md）：R-B1 同构改名漏网红——canonical 同构复制+标识符同构改名+docstring 换写避开探针 → 现行只产散文级 warn → 断言二阶段影子账本标记高相似（实现前必红：影子账本不存在）；R-B2 历史账本零误拦锚——对 create_guard_keyword_dup_warn.jsonl 已放行样本重放二阶段，影子期硬拦判定数必须=0（锁死「影子先行」纪律）；差分矩阵——标识符级命中不触发二阶段/canonical 缺失 fail-open 记 skipped/缓存 mtime 失效/超 10k token 截断/lookup 桩；行为面零变化——影子采集前后 _check_capability_keyword_overlap 返回值逐字节全等；测试隔离——全部 tmp_path（主仓账本只读重放），禁跑全库扫描（缝注入小型 registry）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""test_create_guard_token_sim_shadow.py — S4-B：CREATE-GUARD 判重二阶段 token 相似度影子模式红证。

病根（手术簿 s4_b_token_sim.md §1）：#456 两档化后散文级命中只 warn 不拦——第二真源
若描述措辞避开探针但代码结构同构，现行无结构证据。本单只装影子采集（audit-only），
不改判据：相似度分布落
``.runtime/gate_audit/create_guard_token_sim_shadow.jsonl``，一周后 Owner 门位定档。

覆盖：
  R-B1  test_rb1_isomorphic_rename_flagged_high_similarity（实现前必红）；
  R-B2  test_rb2_history_replay_zero_hard_block（施工后红验，锁死影子先行）；
  矩阵  标识符级不触发 / canonical 缺失 skipped / 缓存 mtime 失效 / 大文件截断 /
        lookup 桩 / 行为面零变化。

纪律：不改任何既有测试/阈值/skip；影子账本断言 fail-open 面；全部 tmp_path 隔离。
"""

from __future__ import annotations

import json
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

_PROSE_PHRASE = "跨日异常回放审计影子红证专用描述面"
_CAP_ID = "__s4b_shadow_cap"
_CANON_REL = "src/zephyr/foo/__s4b_canon_engine.py"
_NEW_REL = "src/zephyr/foo/__s4b_shadow_target.py"

# canonical 源（在册能力真源，落盘 tmp 仓）——token 序列：dup sweep engine ×2 + scan dupes + rows + config
_CANON_SRC = (
    '"""In-registry canonical engine for token-sim shadow red proof."""\n'
    "\n"
    "\n"
    "class DupSweepEngine:\n"
    "    def scan_dupes(self, rows):\n"
    "        seen = set()\n"
    "        out = []\n"
    "        for row in rows:\n"
    "            if row not in seen:\n"
    "                seen.add(row)\n"
    "                out.append(row)\n"
    "        return out\n"
    "\n"
    "\n"
    "def build_dup_sweep_engine(config):\n"
    "    return DupSweepEngine(config)\n"
)

# 同构改名复制体（词素保留改名：engine→checker / scan→check；docstring 换写含探针散文面）
_ISOMORPH_SRC = (
    f'"""\n{_PROSE_PHRASE}。\n"""\n'
    "\n"
    "\n"
    "class DupSweepChecker:\n"
    "    def check_dupes(self, rows):\n"
    "        seen = set()\n"
    "        out = []\n"
    "        for row in rows:\n"
    "            if row not in seen:\n"
    "                seen.add(row)\n"
    "                out.append(row)\n"
    "        return out\n"
    "\n"
    "\n"
    "def build_dup_sweep_checker(config):\n"
    "    return DupSweepChecker(config)\n"
)


def _registry(canonical_rel: str) -> str:
    return f"""
capabilities:
  - capability_id: {_CAP_ID}
    description: "{_PROSE_PHRASE}（散文级影子红证在册能力）"
    aliases: []
    canonical_override: {canonical_rel}
creation_tokens: []
"""


@pytest.fixture()
def _isolate_env(monkeypatch, tmp_path):
    """审计重定向 + 会话环境变量清空（测试禁写主仓 .runtime）。"""
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


def _shadow_records(repo: Path) -> list[dict]:
    audit = repo / ".runtime" / "gate_audit" / "create_guard_token_sim_shadow.jsonl"
    if not audit.exists():
        return []
    return [json.loads(x) for x in audit.read_text(encoding="utf-8").splitlines() if x.strip()]


def _warn_audit_records(repo: Path) -> list[dict]:
    audit = repo / ".runtime" / "gate_audit" / "create_guard_keyword_dup_warn.jsonl"
    if not audit.exists():
        return []
    return [json.loads(x) for x in audit.read_text(encoding="utf-8").splitlines() if x.strip()]


# ---------------------------------------------------------------- R-B1


class TestRB1IsomorphicRename:
    """R-B1：同构改名漏网红——现行码只产 warn，二阶段影子必须标高相似。"""

    def test_rb1_isomorphic_rename_flagged_high_similarity(self, tmp_path: Path, _isolate_env) -> None:
        repo = tmp_path / "repo"
        mini = _mini_lookup(tmp_path, _registry(_CANON_REL))
        # canonical 落盘（在册真源可读）
        canon_abs = repo / _CANON_REL
        canon_abs.parent.mkdir(parents=True, exist_ok=True)
        canon_abs.write_text(_CANON_SRC, encoding="utf-8")
        # 新建文件：同构改名复制体（docstring 含散文面探针词，标识符全改名）
        new_abs = repo / _NEW_REL
        new_abs.parent.mkdir(parents=True, exist_ok=True)
        new_abs.write_text(_ISOMORPH_SRC, encoding="utf-8")
        gw = SimpleNamespace(project_root=repo)
        passed, detail = cg._check_capability_keyword_overlap(gw, [_NEW_REL], "s4b-rb1-sid", lookup=mini)
        assert passed is True, f"影子期散文级命中必须维持 warn 不阻断（判据零变化）: {detail!r}"
        assert _warn_audit_records(repo), "现行 warn 账本必须照旧落账（行为面零变化）"
        records = _shadow_records(repo)
        assert records, "影子账本 create_guard_token_sim_shadow.jsonl 必须落记录（实现前本断言必红——二阶段不存在）"
        rec = [r for r in records if r.get("event") == "token_sim_shadow"][-1]
        assert rec["file"] == _NEW_REL and rec["canonical"] == _CANON_REL, rec
        assert rec["mode"] == "shadow", rec
        assert rec["similarity"] >= 0.6, f"同构改名体必须被判高相似: {rec}"
        assert rec["would_block"] is False, "影子期永不判死"
        assert rec["threshold"] is None, "阈值未标定（Owner 一周后定档）"


# ---------------------------------------------------------------- R-B2


class TestRB2HistoryReplay:
    """R-B2：历史 warn 账本重放零误拦（影子先行纪律锚）。"""

    def test_rb2_history_replay_zero_hard_block(self, tmp_path: Path, _isolate_env, monkeypatch) -> None:
        prod_ledger = _ROOT / ".runtime" / "gate_audit" / "create_guard_keyword_dup_warn.jsonl"
        if not prod_ledger.exists():
            pytest.skip("主仓无历史 warn 账本（空窗期），锚无样本可重放")
        lines = [x for x in prod_ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
        assert lines, "历史账本存在但为空"
        repo = tmp_path / "repo"
        repo.mkdir(parents=True, exist_ok=True)
        gw = SimpleNamespace(project_root=repo)
        replayed = 0
        for line in lines[:50]:
            rec = json.loads(line)
            for v in rec.get("violations", []):
                # 重放：canonical 读不到（历史文件已删）→ skipped；读得到→影子打分
                cg._audit_token_sim_shadow(
                    gw,
                    "s4b-rb2-replay",
                    [v["file"]],
                    [(v["file"], v["capability_id"], v["canonical"], v.get("hit_tokens", []))],
                )
                replayed += 1
        assert replayed > 0, "重放必须覆盖至少一条历史样本"
        records = _shadow_records(repo)
        assert len(records) == replayed, "每条重放样本必须落一条影子记录（含 skipped）"
        hard = [r for r in records if r.get("would_block") is True or r.get("event") == "token_sim_block"]
        assert hard == [], f"影子期硬拦判定数必须=0（若一期就直接判死，本测必红）: {hard[:3]}"
        assert all(r.get("mode") == "shadow" for r in records), "全部记录必须带 mode=shadow"


# ---------------------------------------------------------------- 差分矩阵


class TestDifferentialMatrixShadow:
    """手术簿 §5 差分矩阵抽样（影子面）。"""

    def test_identifier_level_hit_never_triggers_shadow(self, tmp_path: Path, _isolate_env) -> None:
        repo = tmp_path / "repo"
        ident_registry = f"""
capabilities:
  - capability_id: __s4b_dup_sweep_engine
    description: "unrelated prose entirely"
    aliases: []
    canonical_override: {_CANON_REL}
creation_tokens: []
"""
        mini = _mini_lookup(tmp_path, ident_registry)
        canon_abs = repo / _CANON_REL
        canon_abs.parent.mkdir(parents=True, exist_ok=True)
        canon_abs.write_text(_CANON_SRC, encoding="utf-8")
        # stem 切词 dup sweep engine 直击 capability_id → 标识符级硬拦，二阶段不触发
        rel = "src/zephyr/foo/__s4b_dup_sweep_engine.py"
        new_abs = repo / rel
        new_abs.parent.mkdir(parents=True, exist_ok=True)
        new_abs.write_text("# 标识符级红证：stem 直击 capability_id\n\nx = 1\n", encoding="utf-8")
        gw = SimpleNamespace(project_root=repo)
        passed, detail = cg._check_capability_keyword_overlap(gw, [rel], "s4b-m1-sid", lookup=mini)
        assert passed is False, "标识符级命中必须维持硬拦（逐字节不变）"
        assert _shadow_records(repo) == [], "标识符级路径不得触发二阶段（矩阵 1）"

    def test_canonical_missing_fail_open_skipped(self, tmp_path: Path, _isolate_env) -> None:
        repo = tmp_path / "repo"
        mini = _mini_lookup(tmp_path, _registry(_CANON_REL))  # canonical 不落盘
        new_abs = repo / _NEW_REL
        new_abs.parent.mkdir(parents=True, exist_ok=True)
        new_abs.write_text(_ISOMORPH_SRC, encoding="utf-8")
        gw = SimpleNamespace(project_root=repo)
        passed, detail = cg._check_capability_keyword_overlap(gw, [_NEW_REL], "s4b-m5-sid", lookup=mini)
        assert passed is True, f"canonical 缺失 fail-open 维持 warn: {detail!r}"
        records = _shadow_records(repo)
        assert records and records[-1]["event"] == "token_sim_skipped", records
        assert records[-1]["reason"] == "canonical_unreadable", records[-1]
        assert "would_block" not in records[-1], "skipped 记录不得携带判定"

    def test_canonical_cache_mtime_invalidation(self, tmp_path: Path, _isolate_env) -> None:
        repo = tmp_path / "repo"
        canon_abs = repo / _CANON_REL
        canon_abs.parent.mkdir(parents=True, exist_ok=True)
        canon_abs.write_text(_CANON_SRC, encoding="utf-8")
        first = cg._canonical_token_string(repo, _CANON_REL)
        assert first is not None
        # 同 mtime+size 读缓存命中
        assert cg._canonical_token_string(repo, _CANON_REL) == first
        # 重写（mtime 变 + 新增标识符）→ 缓存失效重读出新 token 串
        import os

        st = canon_abs.stat()
        os.utime(canon_abs, ns=(st.st_atime_ns, st.st_mtime_ns + 100))
        canon_abs.write_text(_CANON_SRC + "\ntouched_marker_var = 1\n", encoding="utf-8")
        second = cg._canonical_token_string(repo, _CANON_REL)
        assert second is not None and "touched_marker_var" in second, "mtime_ns 变必须失效重读（缓存判据）"

    def test_large_file_token_truncation_guard(self) -> None:
        # 矩阵 9：超 _TOKEN_SIM_TRUNC 标识符的大文件序列截断护栏
        src = "\n".join(f"var_{i} = {i}" for i in range(12000))
        import ast

        seq = cg._ast_identifier_sequence(ast.parse(src))
        assert seq is not None
        assert len(seq.split()) == cg._TOKEN_SIM_TRUNC, "标识符序列必须截断到护栏常量"

    def test_lookup_stub_with_real_static_tokenizer(self, tmp_path: Path, _isolate_env) -> None:
        """矩阵 12：异构 lookup 桩（真 _tokenize/_token_match 静态件+桩 find）。"""
        repo = tmp_path / "repo"
        entry = {
            "capability_id": _CAP_ID,
            "description": f"{_PROSE_PHRASE}（散文级影子红证在册能力）",
            "aliases": [],
            "canonical_file": _CANON_REL,
            "module_id": "",
        }
        canon_abs = repo / _CANON_REL
        canon_abs.parent.mkdir(parents=True, exist_ok=True)
        canon_abs.write_text(_CANON_SRC, encoding="utf-8")
        new_abs = repo / _NEW_REL
        new_abs.parent.mkdir(parents=True, exist_ok=True)
        new_abs.write_text(_ISOMORPH_SRC, encoding="utf-8")

        def _stub_find(query, session_id=None):
            return [entry] if _PROSE_PHRASE[:8] in query else []

        stub = SimpleNamespace(
            find=_stub_find,
            _tokenize=capability_lookup_mod.CapabilityLookup._tokenize,
            _token_match=capability_lookup_mod.CapabilityLookup._token_match,
        )
        gw = SimpleNamespace(project_root=repo)
        passed, detail = cg._check_capability_keyword_overlap(gw, [_NEW_REL], "s4b-m12-sid", lookup=stub)
        assert passed is True, f"桩路径散文级 warn 不变: {detail!r}"
        records = [r for r in _shadow_records(repo) if r.get("event") == "token_sim_shadow"]
        assert records and records[-1]["similarity"] >= 0.6, records
