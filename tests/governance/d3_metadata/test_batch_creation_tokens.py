# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/batch_creation_tokens.py | §
# [MODULE] tests.governance.d3_metadata.test_batch_creation_tokens
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.governance.d3_metadata.batch_creation_tokens
# [CONSUMERS] 批量 token 工具质量守卫（纯插入/幂等/锚点 fail-closed）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例构造于 tmp 副本 registry（monkeypatch _REGISTRY，不碰生产）
# [MODIFY-GUARD] 与工具同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""batch_creation_tokens 工具测试——极限红蓝对抗 F1 治本守卫。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

import scripts.governance.d3_metadata.batch_creation_tokens as bct

_REPO = Path(__file__).resolve().parents[3]

_REG_BODY = """creation_tokens:
- file: docs/existing/anchor.md
  token: anchor-token-20260913
  created_by: someone
  capability: anchor_cap
- file: docs/existing/other.md
  token: other-token-20260913
  created_by: someone
  capability: anchor_cap
di_seam_exemptions:
- module_path: fake.Thing
  reason: test
- file: src/stray/dead_entry.py
  token: stray-token-20260913
  created_by: someone
  capability: stray_cap_zone
"""


@pytest.fixture()
def lab(tmp_path: Path, monkeypatch):
    """tmp 副本 registry + 假 git 扫描（不走真 git）。"""
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(_REG_BODY, encoding="utf-8")
    monkeypatch.setattr(bct, "_REGISTRY", reg)
    monkeypatch.setattr(bct, "_REPO", tmp_path)
    fake_files = [
        "docs/_working/lab/a/seg_001.md",
        "docs/_working/lab/a/seg_002.md",
        "docs/_working/lab/b/seg_003.md",
    ]
    monkeypatch.setattr(bct, "_git_output", lambda *a: fake_files if "ls-files" in a else [])
    return reg, fake_files


def test_batch_insert_and_yaml_valid(lab):
    reg, files = lab
    rc = bct.main() if False else None  # noqa: F633 — 直接调内部保证 argv 隔离
    block = bct.build_block(files, "sess-A", "lab_cap", "20260913")
    bct.insert_block(block, "anchor_cap")
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    toks = [e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]
    assert len(toks) == 3
    assert all(e["created_by"] == "sess-A" for e in toks)
    assert toks[0]["file"] == "docs/_working/lab/a/seg_001.md"
    # token 内 capability 归一化（lab_cap→lab-cap，token 正则只允许小写字母数字连字符）
    assert toks[0]["token"] == "lab-cap-seg-001-20260913"
    # 纯插入：既有条目不动（含死区条目原样保留——本工具不治理历史死区）
    assert any(e["token"] == "anchor-token-20260913" for e in data["creation_tokens"])
    assert len(data["di_seam_exemptions"]) == 2


def test_idempotent_skip_registered(lab):
    reg, files = lab
    registered = bct.load_registered()
    assert bct.scan_unregistered("docs/_working/lab", registered) == files
    # 登记 a/seg_001 后重扫只剩 2
    block = bct.build_block(files[:1], "sess-A", "lab_cap", "20260913")
    bct.insert_block(block, "anchor_cap")
    registered2 = bct.load_registered()
    assert bct.scan_unregistered("docs/_working/lab", registered2) == files[1:]


def test_anchor_missing_fail_closed(lab, capsys):
    with pytest.raises(bct.TokenInsertError) as ei:
        bct.insert_block("- file: x\n  token: y\n  created_by: z\n  capability: c\n", "no_such_anchor")
    assert "fail-closed" in str(ei.value)
    assert "no_such_anchor" in str(ei.value)


def test_cli_dry_run_zero_write(lab, monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["bct", "--prefix", "docs/_working/lab", "--created-by", "sess-A", "--capability", "lab_cap", "--dry-run"],
    )
    rc = bct.main()
    assert rc == 0
    assert "DRY-RUN" in capsys.readouterr().out
    # registry 零变化
    assert "lab_cap" not in lab[0].read_text(encoding="utf-8")


def test_cli_real_run(lab, monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["bct", "--prefix", "docs/_working/lab", "--created-by", "sess-A", "--capability", "lab_cap"],
    )
    rc = bct.main()
    assert rc == 0
    data = yaml.safe_load(lab[0].read_text(encoding="utf-8"))
    assert len([e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]) == 3
    assert "已插入 3 条" in capsys.readouterr().out
    # 回退锚点（lab_cap 段内不存在→回退段内最后一条 anchor_cap）后仍须落位正确段，
    # 不得落入尾部死区（2026-09-13 实弹教训：旧版全文件 findall 取到死区锚）
    dse = [e for e in data["di_seam_exemptions"] if e.get("capability") == "lab_cap"]
    assert dse == [], "回退锚点不得命中尾部死区"


def test_anchor_never_lands_in_trailing_dead_zone(lab):
    """实弹教训回归（2026-09-13 factory-bottleneck 批）：registry 尾部 di_seam_exemptions
    段混有 capability 行（历史错位死区）——锚点 MUST 限定 creation_tokens 段内，
    条目落进死区=YAML 合法但 CREATE-GUARD 读不到（登记静默丢失）。"""
    reg, files = lab
    block = bct.build_block(files, "sess-A", "lab_cap", "20260913")
    bct.insert_block(block, "anchor_cap")  # 段内锚
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    toks = [e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]
    assert len(toks) == 3, "条目必须落位 creation_tokens 段"
    dse = [e for e in data["di_seam_exemptions"] if e.get("capability") == "lab_cap"]
    assert dse == [], "条目不得落入 di_seam_exemptions 死区"
    # 死区锚点显式拒写（fail-closed——stray_cap_zone 只存在于死区）
    with pytest.raises(bct.TokenInsertError) as ei:
        bct.insert_block("- file: x\n  token: y\n  created_by: z\n  capability: c\n", "stray_cap_zone")
    assert "fail-closed" in str(ei.value)


# ---------------------------------------------------------------------------
# 2026-09-15 治理上报件1 收口：写后 parse/语义双自检 + 失败回滚（scaffold 同通道复用）
# ---------------------------------------------------------------------------


def test_resolve_anchor_prefers_exact_then_last(lab):
    reg, _ = lab
    text = reg.read_text(encoding="utf-8")
    sec_start, sec_end = bct._creation_tokens_section(text)
    section = text[sec_start:sec_end]
    assert bct.resolve_anchor(section, "anchor_cap") == "anchor_cap"  # 段内同名命中
    assert bct.resolve_anchor(section, "no_such") == "anchor_cap"  # 回退段内最后一条
    with pytest.raises(bct.TokenInsertError):
        bct.resolve_anchor("", "anything")  # 段内无锚点 → fail-closed


def test_section_missing_raises_token_insert_error(tmp_path, monkeypatch):
    reg = tmp_path / "reg.yaml"
    reg.write_text("di_seam_exemptions: []\n", encoding="utf-8")
    monkeypatch.setattr(bct, "_REGISTRY", reg)
    with pytest.raises(bct.TokenInsertError) as ei:
        bct._creation_tokens_section(reg.read_text(encoding="utf-8"))
    assert "fail-closed" in str(ei.value)


def test_post_write_issues_detects_broken_yaml_and_missing_landing(lab):
    reg, _ = lab
    reg.write_text("creation_tokens:\n  - [broken\n", encoding="utf-8")
    issues = bct._post_write_issues(None)
    assert issues and "解析失败" in issues[0]
    reg.write_text("creation_tokens:\n- file: a.md\n  token: t\n", encoding="utf-8")
    issues = bct._post_write_issues(["ghost.md"])
    assert issues and "未落位" in issues[0]
    assert bct._post_write_issues(["a.md"]) == []


def test_insert_block_rollback_on_verify_failure(lab, monkeypatch):
    """写后自检失败 → 回滚写前字节（scaffold 件1 收口的核心保证）。"""
    reg, _ = lab
    pre = reg.read_bytes()
    monkeypatch.setattr(bct, "_post_write_issues", lambda files: ["boom"])
    with pytest.raises(bct.TokenInsertError) as ei:
        bct.insert_block("- file: x.md\n  token: t-1\n  created_by: s\n  capability: anchor_cap\n", "anchor_cap")
    assert "回滚" in str(ei.value)
    assert reg.read_bytes() == pre, "自检失败必须回滚到写前字节"


def test_insert_block_semantic_missing_triggers_rollback(lab):
    """端到端（零打桩）：块插入的 file 与 expect_files 不符 = 语义落位失败 → 回滚。"""
    reg, _ = lab
    pre = reg.read_bytes()
    with pytest.raises(bct.TokenInsertError) as ei:
        bct.insert_block(
            "- file: docs/real.md\n  token: real-1\n  created_by: s\n  capability: anchor_cap\n",
            "anchor_cap",
            expect_files=["docs/ghost.md"],
        )
    assert "未落位" in str(ei.value)
    assert reg.read_bytes() == pre, "语义落位失败必须回滚到写前字节"
    # 回滚后 registry 仍 parse 合法且无残留
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    assert all(e["file"] != "docs/real.md" for e in data["creation_tokens"])


def test_insert_block_with_expect_files_happy_path(lab):
    reg, files = lab
    block = bct.build_block(files, "sess-A", "lab_cap", "20260913")
    bct.insert_block(block, "anchor_cap", expect_files=files)  # 全部落位 → 通过
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    assert len([e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]) == 3


def test_insert_block_survives_concurrent_interleaved_write(lab, monkeypatch):
    """战伤回归（2026-09-16 st-commitspeed 高频写覆写丢 token，f09d2bc81e 前科复发）：
    insert_block 读基线后、CAS 落盘前，他会话抢先整段写入——CAS 拒写必须触发
    重读基线重放，最终双方条目并存（后写不吞先写）。非库路径的全文覆写不在此测。"""
    import zephyr.shared.io.file_utils as fu

    reg, _files = lab
    real_safe_write = fu.safe_write_text
    state = {"interleaved": False}

    def interleaved_writer(*args, **kwargs):
        if not state["interleaved"]:
            state["interleaved"] = True
            cur = reg.read_text(encoding="utf-8")
            idx = cur.index("di_seam_exemptions:")
            other = (
                "- file: docs/existing/raced.md\n"
                "  token: raced-token-20260916\n"
                "  created_by: sess-other\n"
                "  capability: other_new_cap\n"
            )
            reg.write_text(cur[:idx] + other + cur[idx:], encoding="utf-8")
        return real_safe_write(*args, **kwargs)

    monkeypatch.setattr(fu, "safe_write_text", interleaved_writer)

    block = bct.build_block(["docs/_working/lab/a/seg_001.md"], "sess-A", "race_cap", "20260916")
    bct.insert_block(block, "anchor_cap")  # CAS 拒→重读→重放，不得抛 TokenInsertError

    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    caps = [e["capability"] for e in data["creation_tokens"]]
    assert "race_cap" in caps, "我方条目必须存活"
    assert "other_new_cap" in caps, "他会话条目必须存活（后写不吞先写）"
    assert data["creation_tokens"][-1]["capability"] in {"race_cap", "other_new_cap", "anchor_cap", "stray_cap_zone"}


# ── B22 治本：写侧"只增不减"守恒闸（2026-09-19，全流通战役热册蒸发第 1/5 例的机制补强）──
_HEAD_EXTRA = """creation_tokens:
- file: docs/existing/anchor.md
  token: anchor-token-20260913
  created_by: someone
  capability: anchor_cap
- file: docs/existing/other.md
  token: other-token-20260913
  created_by: someone
  capability: anchor_cap
- file: docs/existing/evicted-by-stale-snapshot.md
  token: evicted-token-20260919
  created_by: st-other-lane
  capability: anchor_cap
di_seam_exemptions: []
"""


def _patch_git(monkeypatch, fake_files, head_text=None):
    """同时喂 ls-files 与 show HEAD:<registry> 两个 git 面（HEAD 面=None 表示读不到）。"""

    def _fake(*a):
        if "ls-files" in a:
            return fake_files
        if a and a[0] == "show" and head_text is not None:
            return [ln for ln in head_text.splitlines() if ln.strip()]
        return []

    monkeypatch.setattr(bct, "_git_output", _fake)


def test_stale_base_vs_head_refuses_write(lab, monkeypatch, capsys):
    """写前闸：盘上基底相对 HEAD 已缺条目 ⇒ 拒写 + 点名少了哪几条 + **磁盘零改动**。"""
    reg, files = lab
    pre = reg.read_bytes()
    _patch_git(monkeypatch, files, _HEAD_EXTRA)  # HEAD 有 3 条，盘上只有 2 条
    block = bct.build_block(files[:1], "sess-A", "lab_cap", "20260919")
    with pytest.raises(bct.TokenInsertError) as ei:
        bct.insert_block(block, "anchor_cap")
    msg = str(ei.value)
    assert "只增不减" in msg and "evicted-token-20260919" in msg, f"未点名被蒸发条目: {msg}"
    assert reg.read_bytes() == pre, "拒写必须是真零写入（fail-safe=不写）"
    assert "未落盘任何改动" in msg
    assert capsys is not None


def test_head_matched_base_still_lands(lab, monkeypatch):
    """阴性对照：基底与 HEAD 一致（正常路径）⇒ 守恒闸不得拦，登记照旧成功。"""
    reg, files = lab
    _patch_git(monkeypatch, files, _REG_BODY)
    block = bct.build_block(files[:1], "sess-A", "lab_cap", "20260919")
    bct.insert_block(block, "anchor_cap")  # 不得抛
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    assert len(data["creation_tokens"]) == 3, "正常路径条目数应只增"
    assert [e["token"] for e in data["creation_tokens"] if e["capability"] == "lab_cap"] == ["lab-cap-seg-001-20260919"]


def test_head_unreadable_skips_pre_gate_without_fabricating(lab, monkeypatch):
    """HEAD 读不到（临时副本/非 git 环境）⇒ 跳过对照面，**不得**拿空集当基线把所有写入判死。"""
    reg, files = lab
    _patch_git(monkeypatch, files, None)
    assert bct._head_entry_keys() is None
    block = bct.build_block(files[:1], "sess-A", "lab_cap", "20260919")
    bct.insert_block(block, "anchor_cap")  # 不抛=未被假基线误杀
    assert len(yaml.safe_load(reg.read_text(encoding="utf-8"))["creation_tokens"]) == 3


def test_concurrent_overwrite_after_write_is_refused_and_named(lab, monkeypatch):
    """写后闸实弹面：他会话在我们落盘后整片压回陈旧快照 ⇒ 必须判"条目数净减"并拒收。

    回滚同样不得整片覆写对方——磁盘已推进 ⇒ 放弃回滚，报错里写明"未回滚，需人工分诊"。
    """
    import zephyr.shared.io.file_utils as fu

    reg, files = lab
    _patch_git(monkeypatch, files, _REG_BODY)
    real_safe_write = fu.safe_write_text
    state = {"raced": False}
    shorter = (
        "creation_tokens:\n"
        "- file: docs/existing/other.md\n  token: other-token-20260913\n"
        "  created_by: someone\n  capability: anchor_cap\n"
        "di_seam_exemptions: []\n"
    )

    def racy_writer(*args, **kwargs):
        res = real_safe_write(*args, **kwargs)
        if not state["raced"]:
            state["raced"] = True
            reg.write_text(shorter, encoding="utf-8")  # 模拟他会话压回只含 1 条的陈旧快照
        return res

    monkeypatch.setattr(fu, "safe_write_text", racy_writer)
    block = bct.build_block(files[:1], "sess-A", "lab_cap", "20260919")
    with pytest.raises(bct.TokenInsertError) as ei:
        bct.insert_block(block, "anchor_cap")
    msg = str(ei.value)
    assert "净减" in msg and "只增不减" in msg, f"守恒闸未触发: {msg}"
    assert "anchor-token-20260913" in msg, f"未点名被蒸发条目: {msg}"
    assert "未回滚" in msg and "人工分诊" in msg, f"回滚面失守（会二次蒸发）: {msg}"


def test_rollback_refuses_when_disk_moved(lab):
    """回滚基底校验：磁盘已被推进 ⇒ 返回 False 且**不改一个字节**（不制造第二次蒸发）。"""
    reg, _files = lab
    pre = reg.read_bytes()
    assert bct._rollback(pre, expect_sha="0" * 64) is False
    assert reg.read_bytes() == pre


def test_rollback_restores_when_disk_untouched(lab):
    """回滚正向腿：磁盘未动 ⇒ 按 expect_sha 放行并逐字节还原（含 CRLF 原样）。"""
    from zephyr.shared.io.file_utils import content_sha256

    reg, _files = lab
    pre = reg.read_bytes()
    reg.write_text("creation_tokens:\n- file: x.md\n  token: t\n", encoding="utf-8")
    assert bct._rollback(pre, expect_sha="") is True
    assert reg.read_bytes() == pre
    assert bct._rollback(pre, expect_sha=content_sha256(reg.read_text(encoding="utf-8"))) is True
    assert reg.read_bytes() == pre


# ---------------------------------------------------------------------------
# 裁定#375 内收判据门禁化（2026-09-20 P9③）：--merge-evaluation 登记通道。
# CREATE-GUARD 对缺 merge_evaluation 的新建资产 warn+审计，本工具是补填正门。
# ---------------------------------------------------------------------------


def test_build_block_with_merge_evaluation(lab):
    """--merge-evaluation 非空 → 每条 token 落 merge_evaluation 字段（YAML 合法）。"""
    reg, files = lab
    me = "grep+计划任务+注册表三查零同域消费方，新对象"
    block = bct.build_block(files, "sess-A", "lab_cap", "20260920", merge_evaluation=me)
    bct.insert_block(block, "anchor_cap")
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    toks = [e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]
    assert len(toks) == 3
    assert all(e.get("merge_evaluation") == me for e in toks), "三条均应携带 merge_evaluation"


def test_build_block_without_merge_evaluation_omits_field(lab):
    """缺省 → 条目无该字段（向后兼容：不破坏既有无参调用路径）。"""
    reg, files = lab
    block = bct.build_block(files, "sess-A", "lab_cap", "20260920")
    assert "merge_evaluation" not in block
    bct.insert_block(block, "anchor_cap")
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    toks = [e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]
    assert len(toks) == 3
    assert all("merge_evaluation" not in e for e in toks)


def test_yaml_quote_escapes_and_flattens():
    """特殊字符转义+换行压平（保持单行 YAML 双引号标量）。"""
    q = bct._yaml_quote('含"引号"与\\反斜杠\n换行\t制表')
    assert "\n" not in q and "\t" not in q, "多行/制表必须压平"
    assert '\\"' in q and "\\\\" in q, "双引号与反斜杠必须转义"


def test_cli_merge_evaluation_hint_and_landing(lab, monkeypatch, capsys):
    """CLI 红证双向：缺省提示补填（不阻断）；--merge-evaluation 携带则字段落条目。"""
    # ① 缺省：dry-run 输出补填提示（rc=0 不阻断）
    monkeypatch.setattr(
        sys,
        "argv",
        ["bct", "--prefix", "docs/_working/lab", "--created-by", "sess-A", "--capability", "lab_cap", "--dry-run"],
    )
    assert bct.main() == 0
    out1 = capsys.readouterr().out
    assert "提示" in out1 and "--merge-evaluation" in out1, "缺省应提示补填"
    assert "lab_cap" not in lab[0].read_text(encoding="utf-8"), "dry-run 零写入"
    # ② 携带：真实落盘，三条均含 merge_evaluation
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "bct",
            "--prefix",
            "docs/_working/lab",
            "--created-by",
            "sess-A",
            "--capability",
            "lab_cap",
            "--merge-evaluation",
            "grep+计划任务+注册表三查零同域消费方，新对象",
        ],
    )
    assert bct.main() == 0
    assert "已插入 3 条" in capsys.readouterr().out
    data = yaml.safe_load(lab[0].read_text(encoding="utf-8"))
    toks = [e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]
    assert len(toks) == 3
    assert all(e["merge_evaluation"] == "grep+计划任务+注册表三查零同域消费方，新对象" for e in toks)
