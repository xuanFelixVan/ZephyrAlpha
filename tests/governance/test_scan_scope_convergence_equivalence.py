# [MODULE] tests.governance.test_scan_scope_convergence_equivalence
# [DOMAIN] D_GOV
# [DEPENDENCIES] pytest; zephyr.governance.consumption.scan_scope_converged; zephyr.governance.consumption.consumption_census;
#   zephyr.governance.audit.library_new_module_reconciler
# [CONSUMERS] 波 13 壬道（§3.4 三分支收敛红证）
# [TTL] permanent
"""§3.4 单一 scope 收敛的等价性红证（壬道 st-p7-scope）。

判据（对应任务书第 3 项）：
  E-A 薄别名=同一对象：丙/丁两条道的口径公开名必须与真源**同一性绑定**（is），
      任何车道重新派生一份口径值，本尺立刻红（第二真源的结构性防线）。
  E-B 三调用点谓词全等：对固定真实路径集，真源 counts_as_consumer、丁道
      scope_verdict、丙道 derive_potential_consumers（注入 grep 走同一批路径）
      三者给出的"算不算消费者"结论完全一致，且逐条等于 §3.4+C1-C7 裁定的期望值。
  E-C observer 层红证（尺不能自我认证）：普查引擎/旧壳/生成器/真源/矩阵/入编器
      自身文件永不被计为消费者；摘掉 observer 层后引擎必须立刻把自己算成消费者
      ——证明这条排除真实承重，而不是恰好没命中。
  E-D 面/层两分一致性（裁决 C7）：iter_scope_files 产出的文件 ⇔ in_scan_surface，
      两面同源一处定义。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
for _p in (str(_REPO), str(_REPO / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import zephyr.governance.audit.library_new_module_reconciler as newmod  # noqa: E402
import zephyr.governance.consumption.consumption_census as cc  # noqa: E402
import zephyr.governance.consumption.scan_scope_converged as ssc  # noqa: E402


def _rel_glob(pattern: str) -> str:
    hits = sorted(p.relative_to(_REPO).as_posix() for p in _REPO.glob(pattern))
    assert hits, f"测试前提失效：本仓无匹配 {pattern} 的真实文件"
    return hits[0]


# ── E-A 薄别名同一性（禁再派生）──────────────────────────────────────────────


def test_lane_names_are_the_same_objects_not_copies():
    assert cc.CONSUMER_SCAN_SCOPE is ssc.CONSUMER_SCAN_SCOPE
    assert cc.DOC_EVIDENCE_SCOPE is ssc.DOC_EVIDENCE_SCOPE
    assert cc.ScanScope is ssc.ScanScope
    assert cc.exclusion_layer is ssc.exclusion_layer
    assert cc.PRODUCER_EXCLUDE_RE is ssc.PRODUCER_EXCLUDE_RE
    assert cc.DISPLAY_EXCLUDE_RE is ssc.DISPLAY_EXCLUDE_RE
    assert cc.INFRA_EXCLUDE_RE is ssc.INFRA_EXCLUDE_RE
    assert cc.OBSERVER_EXCLUDE_RE is ssc.OBSERVER_EXCLUDE_RE
    assert cc.EXCLUSION_LAYERS is ssc.EXCLUSION_LAYERS
    assert newmod.is_doc14_layer_excluded is ssc.is_doc14_layer_excluded
    assert newmod.DOC14_INFRA_TOKENS is ssc.DOC14_INFRA_TOKENS
    assert newmod.CONSUMER_SCAN_SCOPE is ssc.CONSUMER_SCAN_SCOPE


def test_aliases_preserve_lane_values():
    assert newmod.CONSUMER_SCOPE_ROOTS == ("src", "scripts", "config")  # 丙尺 L142 的 pathspec 面
    assert frozenset({".py", ".yaml"}) == newmod.CONSUMER_SCOPE_SUFFIXES  # C1：.yml 出局
    assert ssc.SCAN_SCOPE_DIRS == ("src", "scripts", "config")  # 戊尺原值
    assert ssc.SCAN_SCOPE_SUFFIXES == (".py", ".yaml")
    assert newmod.CONSUMER_CAP == ssc.CONSUMER_CAP == 200


# ── E-B 三调用点谓词对固定真实路径集全等 ────────────────────────────────────


def _fixed_real_paths() -> list[tuple[str, bool]]:
    """(相对路径, §3.4+C1..C7 裁定期望)——全部取本仓真实存在文件。"""
    impl = _rel_glob("src/zephyr/data/implementations/*.py")
    pe = "src/zephyr/plan_engine/intraday_tomorrow_forecast.py"
    assert (_REPO / pe).is_file(), f"测试前提失效：本仓无 {pe}"
    return [
        ("config/trading_decision_map.yaml", True),  # ③ config 算
        (pe, True),
        ("scripts/git_commit.py", True),  # ② scripts 算
        ("docs/library/INDEX.md", False),  # .md/docs 永不算
        ("config/infra/prometheus/prometheus.yml", False),  # C1：.yml 出局
        ("src/zephyr/frontend/dashboard/app_panel.py", False),  # C2：display 整删
        ("src/zephyr/governance/scan_scope_converged.py", False),  # C5：observer（真源自己）
        ("src/zephyr/governance/consumption_census.py", False),  # C5：observer
        ("src/zephyr/governance/indicator_usage_audit.py", False),  # C5：observer（旧壳）
        ("src/zephyr/governance/audit/library_new_module_reconciler.py", False),  # C5：observer
        ("scripts/governance/d3_metadata/generate_wiring_registry.py", False),  # C5：observer
        (impl, False),  # producer 目录层
    ]


def test_three_call_sites_agree_on_real_repo_paths():
    paths = _fixed_real_paths()
    assert len({p for p, _ in paths}) == len(paths)
    for rel, expected in paths:
        converged = ssc.counts_as_consumer(rel)
        census = cc.scope_verdict(rel)
        assert converged is expected, f"真源判 {rel}={converged}，裁定期望 {expected}"
        assert census is converged, f"丁调用点与真源分叉: {rel}"
    # 丙调用点：把同一批路径灌进 derive 的注入 grep，kept 集必须＝真源 True 集
    all_paths = [p for p, _ in paths] + ["README.md", "src/zephyr/demo/newmod.py"]
    grep = lambda pattern, roots: [x for x in all_paths if x != "src/zephyr/demo/newmod.py"]  # noqa: E731
    kept = set(newmod.derive_potential_consumers(_REPO, "src/zephyr/demo/newmod.py", grep=grep))
    assert kept == {p for p, exp in paths if exp}, f"丙调用点与真源分叉: {sorted(kept)}"


# ── E-C observer 层红证（摘除⇒引擎必自计；正常态必不自计）───────────────────


def test_observer_layer_is_load_bearing_not_incidental(tmp_path, monkeypatch):
    """红证构造：沙盘里唯一提到 IND-SELF-001 的文件＝"consumption_census_note.py"。

    正常态＝observer 层生效 ⇒ 该实体零消费者（孤岛不洗白）；
    摘除态＝把真源 EXCLUSION_LAYERS 里的 observer 条目剔掉 ⇒ 引擎必须立刻把这把尺
    自己算成消费者。后者不发生＝这条排除不承重＝本尺该红。
    """
    root = tmp_path / "repo"
    cat = root / "docs/01_policies_and_standards/_registry/catalogs"
    cat.mkdir(parents=True)
    (cat / "technical_indicator_registry.yaml").write_text(
        "tier: 3\nindicators:\n  - indicator_id: IND-SELF-001\n    name: selfcert\n    status: active\n    tier: 3\n",
        encoding="utf-8",
    )
    mentioner = root / "src/zephyr/governance/consumption_census_note.py"
    mentioner.parent.mkdir(parents=True)
    mentioner.write_text("# IND-SELF-001 的判据说明（尺自己提到≠有客）\n", encoding="utf-8")

    def _island() -> bool:
        doc = cc.run_consumption_census(
            families=["indicator"],
            repo_root=root,
            scan_root=root,
            output_path=root / ".runtime/tmp/led.json",
            cache_path=None,
            today="T",
            include_doc_mentions=False,
        )["doc"]
        return doc["families"][0]["entries"][0]["state"] == "zero"

    assert _island(), "observer 层缺位：尺提名已能把实体洗白成有客（C5 失守）"
    trimmed = tuple(x for x in ssc.EXCLUSION_LAYERS if x[0] != "observer")
    monkeypatch.setattr(ssc, "EXCLUSION_LAYERS", trimmed)
    assert not _island(), "摘除 observer 后引擎仍不自计——红证没咬到真承重（尺恒真是另一种假绿）"


# ── E-D 面/层两分一致性（单一声明处，C7）───────────────────────────────────


def test_iter_surface_and_predicate_share_one_declaration():
    yielded = {p.relative_to(_REPO).as_posix() for p in ssc.iter_scope_files(_REPO)}
    assert yielded, "扫描面为空=尺没接上"
    assert all(ssc.CONSUMER_SCAN_SCOPE.in_scan_surface(r) for r in yielded)
    # 面/层两分：observer 与 display 文件仍在面上（取证/诊断可见），但被层谓词剔出消费者
    for rel in (
        "src/zephyr/governance/consumption_census.py",
        "src/zephyr/frontend/dashboard/app_panel.py",
        _rel_glob("src/zephyr/data/implementations/*.py"),
    ):
        assert ssc.in_scan_surface(rel) is True, f"应在面上（层剔除才是不计客的理由）: {rel}"
        assert ssc.counts_as_consumer(rel) is False
    # 不在面上的：.md/docs（裁定①）与 .yml（C1）
    for rel in (
        "docs/library/INDEX.md",
        "config/infra/prometheus/prometheus.yml",
        "src/zephyr/notes.md" if (_REPO / "src/zephyr/notes.md").exists() else "README.md",
    ):
        assert ssc.in_scan_surface(rel) is False
    assert ("config/trading_decision_map.yaml" in yielded) is True
