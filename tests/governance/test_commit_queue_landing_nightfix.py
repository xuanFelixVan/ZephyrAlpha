# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §三向合并拼接与身份作用域
# [MODULE] tests.governance.test_commit_queue_landing_nightfix
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; pyyaml; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_landing_nightfix.py
# [MATURITY] testing
# [INVARIANTS] 纯函数层红蓝（零 IO 零 tmp 仓）；红=钉住夜班实测双缺陷（族尾多插拼接漂移 q-20260923-wm1-mineC-0003 死信实证 + 翻译册族身份单键误杀），绿=修复后全过；不改既有 test_commit_queue_landing.py 语义
# [MODIFY-GUARD] 夜班手术二a（st-nightfix-20260923，Lane 0b 授权）：①族尾同点多插 splice（取消 +1 伪递增）②module_translation_registry 族身份作用域化（entries=(module_path,name_zh,name_en)/algo_submodules=(module_path,node_id)，按 rel_path 键控，其余注册表走默认复合键零漂移）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_landing_nightfix.py — 夜班手术二a 红蓝钉（2026-09-23）。

两个实测缺陷（死信/直连绕行实证在案）：
1. **族尾多插拼接漂移**：_plan_insert_splices 对同族多条插入用 ``cached+1`` 伪递增，
   但全部插入点的正确坐标都是族尾同一行（降序应用天然保序）——第 2 条起落到
   末尾标量键（di_seam_exemptions）之后，渲染自检报"结果不可解析"
   （q-20260923-st-wm1-mineC-20260923-0003 与 st-ibt-remedy-a 批A 双死信实证）。
2. **翻译册族身份单键误杀**：module_translation_registry 的 entries/algo_submodules
   族合法持同 module_path 多条（7196/968 条实测 194 个 module_path 多条），单键身份
   一进合并就"同侧身份键重复"死信——翻译册落地结构性死锁，逼出直连绕行。

红=本文件在缺陷代码上必红；绿=修复后全过 + 既有 test_commit_queue_landing.py 回归零漂移。
"""

from __future__ import annotations

import yaml

import scripts.governance.commit_queue_landing as cql

_TRANS_REL = "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"


def _last_key_order(merged: str) -> list[str]:
    """merged 顶层键序（registry_yaml_parse_gate 同款 di_seam 居末断言的原料）。"""
    return list((yaml.safe_load(merged) or {}).keys())


class TestFamilyTailSpliceFix:
    """缺陷1：同族多条插入必须全部落在族尾之内，末尾标量键保持居末。"""

    BASE = (
        "schema_version: 1.0.0\n"
        "title: t\n"
        "items:\n"
        "  - id: a\n    path: a.md\n"
        "di_seam_exemptions: []\n"
    )
    THEIRS = (
        "schema_version: 1.0.0\n"
        "title: t\n"
        "items:\n"
        "  - id: a\n    path: a.md\n"
        "  - id: b\n    path: b.md\n"
        "  - id: c\n    path: c.md\n"
        "di_seam_exemptions: []\n"
    )

    def test_two_inserts_into_last_family_parse_and_stay_inside(self):
        """ours==base，theirs 追加 2 条 → 两条都进 items 族，di_seam 仍居末（q-0003 死形）。"""
        merged, err = cql.three_way_merge_registry_yaml(
            self.BASE, self.BASE, self.THEIRS, rel_path="docs/x/registry.yaml"
        )
        assert err == "", f"合并失败: {err}"
        data = yaml.safe_load(merged)  # 不可解析即炸（缺陷形态）
        ids = [e["id"] for e in data["items"]]
        assert ids == ["a", "b", "c"], f"族内条目序漂移: {ids}"
        assert _last_key_order(merged)[-1] == "di_seam_exemptions", "di_seam_exemptions 必须居末"

    def test_multi_insert_order_preserved(self):
        """同点多条插入保持 theirs 相对顺序（b 在 c 前）。"""
        merged, err = cql.three_way_merge_registry_yaml(
            self.BASE, self.BASE, self.THEIRS, rel_path="docs/x/registry.yaml"
        )
        assert err == ""
        assert merged.index("- id: b") < merged.index("- id: c"), "插入顺序须保持 theirs 序"


class TestTranslationFamilyIdentityScoping:
    """缺陷2：module_translation_registry 族真键（按 rel_path 键控，其余册零漂移）。"""

    @staticmethod
    def _entry(mp: str, nz: str, plain: str = "") -> str:
        return f"  - module_path: {mp}\n    name_zh: {nz}\n    plain_zh: {plain}\n"

    BASE_TRANS = (
        "module_id: MOD-X\n"
        "title: 翻译册\n"
        "entries:\n" + _entry.__func__("src/zephyr/a.py", "甲", "旧")
    )

    def test_entries_same_module_diff_name_both_survive(self):
        """theirs：改甲的 plain + 新增同 module_path 不同 name_zh 的乙 → 双条共存零死信。"""
        theirs = (
            "module_id: MOD-X\n"
            "title: 翻译册\n"
            "entries:\n"
            + self._entry("src/zephyr/a.py", "甲", "新")
            + self._entry("src/zephyr/a.py", "乙", "第二条")
        )
        merged, err = cql.three_way_merge_registry_yaml(self.BASE_TRANS, self.BASE_TRANS, theirs, rel_path=_TRANS_REL)
        assert err == "", f"同 module_path 不同 name 误死信: {err}"
        data = yaml.safe_load(merged)
        rows = [e for e in data["entries"] if e["module_path"] == "src/zephyr/a.py"]
        assert sorted(e["name_zh"] for e in rows) == ["乙", "甲"], f"条目集漂移: {rows}"
        assert rows[0]["plain_zh"] in ("新", "旧")

    def test_algo_submodules_multi_node_merge(self):
        """algo_submodules 同 module_path 多 node（A1 在 ours，theirs 追加 A2）→ 合并成功。"""
        base = (
            "module_id: MOD-Y\n"
            "title: 翻译册\n"
            "algo_submodules:\n"
            "  - module_path: src/zephyr/m.py\n    node_id: A1\n    name_zh: 一号\n"
        )
        theirs = (
            "module_id: MOD-Y\n"
            "title: 翻译册\n"
            "algo_submodules:\n"
            "  - module_path: src/zephyr/m.py\n    node_id: A1\n    name_zh: 一号\n"
            "  - module_path: src/zephyr/m.py\n    node_id: A2\n    name_zh: 二号\n"
        )
        merged, err = cql.three_way_merge_registry_yaml(base, base, theirs, rel_path=_TRANS_REL)
        assert err == "", f"同 module_path 多 node 误死信: {err}"
        nodes = [e["node_id"] for e in yaml.safe_load(merged)["algo_submodules"]]
        assert nodes == ["A1", "A2"]

    def test_translation_true_conflict_still_dead_letters(self):
        """真冲突仍死信：双侧各自新增同 (module_path, name_zh) 且内容异。"""
        ours = (
            "module_id: MOD-X\n"
            "title: 翻译册\n"
            "entries:\n" + self._entry("src/zephyr/a.py", "甲", "ours版")
        )
        theirs = (
            "module_id: MOD-X\n"
            "title: 翻译册\n"
            "entries:\n" + self._entry("src/zephyr/a.py", "甲", "theirs版")
        )
        merged, err = cql.three_way_merge_registry_yaml(self.BASE_TRANS, ours, theirs, rel_path=_TRANS_REL)
        assert merged is None and err, "真冲突必须死信"
        assert "同键条目内容冲突" in err


class TestDefaultIdentityZeroDrift:
    """非翻译册走默认复合键零漂移（creation_tokens 同 file 多 token 共存）。"""

    BASE = "title: t\nitems:\n  - file: a.py\n    token: t1\n"

    def test_same_file_multi_token_both_survive(self):
        theirs = "title: t\nitems:\n  - file: a.py\n    token: t1\n  - file: a.py\n    token: t2\n"
        merged, err = cql.three_way_merge_registry_yaml(self.BASE, self.BASE, theirs, rel_path="docs/x/registry.yaml")
        assert err == "", f"复合键零漂移破坏: {err}"
        assert [e["token"] for e in yaml.safe_load(merged)["items"]] == ["t1", "t2"]

    def test_non_translation_registry_single_key_still_works(self):
        """entries 族在非翻译册仍走默认身份（id 首字段）——既有 W2 测试语义不变。"""
        base = "title: t\nentries:\n  - id: a\n    path: a.md\n"
        theirs = "title: t\nentries:\n  - id: a\n    path: a.md\n  - id: b\n    path: b.md\n"
        merged, err = cql.three_way_merge_registry_yaml(base, base, theirs, rel_path="docs/x/other.yaml")
        assert err == ""
        assert [e["id"] for e in yaml.safe_load(merged)["entries"]] == ["a", "b"]
