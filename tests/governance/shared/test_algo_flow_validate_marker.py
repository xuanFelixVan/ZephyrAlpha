# [A_test] test_id=AFG-VALIDATE-001 | module=scripts/governance/_shared/algo_flow_validate_marker.py | gate=pytest
# [BLUEPRINT] MOD-GOV_ALGO_FLOW_VALIDATOR | scripts/governance/_shared/algo_flow_validate_marker.py
# [MODULE] tests.governance.shared.test_algo_flow_validate_marker
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_algo_flow_validate_marker.py — 图判据/字段判据分家行为锚点（2026-09-16 P2-1 收尾批）。

为什么要有这份测试：ALGO-FLOW-LINK 门禁第 3 判据改为消费 validate_graph（图可达），
而字段完整度判据（缺必填字段，全仓尚有 125 件历史欠账）留在 validate_file 供人工校准。
两副口径一旦重新混装，要么门禁连坐无辜提交（字段判据进门禁），要么图坏重新静默放行
（图判据退出门禁）——本文件把"图判据不含字段判据、且图判据抓得住四类真实坏图"钉死。

第二职责=存量防线：门禁只扫 own-diff，全仓镜像语料自洽由
test_repo_mirrors_all_pass_graph_rules 常驻兜底（同一判据真源，非第二套规则）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SCRIPT = _REPO / "scripts" / "governance" / "_shared" / "algo_flow_validate_marker.py"


def _load():
    name = "afvm_under_test"
    if name in sys.modules:
        return sys.modules[name]
    shared = str(_SCRIPT.parent)
    if shared not in sys.path:
        sys.path.insert(0, shared)
    spec = importlib.util.spec_from_file_location(name, _SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


vm = _load()


def _block(body: str) -> str:
    return "# [ALGO_FLOW]\n" + body + "# [/ALGO_FLOW]\n"


def _load_graph(text: str):
    from code_algorithm_extractor import parse_algo_flow  # noqa: PLC0415 — 判据真源同一份

    return parse_algo_flow(text)


_CLEAN = (
    "# 层: 输入\n# - id: I1\n#   name: 入参\n"
    "# 层: 算法\n# - id: A1\n#   name_zh: 主流程\n# - id: O1\n#   name_zh: 结果\n"
    "# [/ALGO_FLOW]\n#\n# 边:\n# I1 --> A1\n# A1 --> O1\n"
)


def _data(edges_body: str):
    return _load_graph("# [ALGO_FLOW]\n" + edges_body)


def test_clean_graph_has_zero_problems() -> None:
    data = _data(_CLEAN)
    assert data is not None
    assert vm.validate_graph(data) == []


def test_field_rules_do_not_leak_into_graph_rules() -> None:
    """图判据必须与字段完整度无关：缺 name_en/intro 的速记图不得在门禁侧报问题。

    （全仓 125 件镜像缺必填字段——若字段判据混进 validate_graph，门禁一次性收紧=连坐
    所有无辜提交，正是本判据分家要防的事。）
    """
    body = (
        "# 层: 输入\n# - id: I1 入参\n# 层: 算法\n# - id: A1 主流程\n# - id: O1 结果\n"
        "# [/ALGO_FLOW]\n#\n# 边:\n# I1 --> A1\n# A1 --> O1\n"
    )
    data = _load_graph("# [ALGO_FLOW]\n" + body)
    assert data is not None
    assert vm.validate_graph(data) == []
    # 同一图走字段判据仍应报欠账（人工校准口径不失明）
    field_problems: list[str] = []
    vm._check_nodes(data, field_problems)  # noqa: SLF001 — 只为确认字段判据仍在
    assert any("缺必填字段" in p for p in field_problems), field_problems


def test_illegal_node_id_detected() -> None:
    data = _data(
        "# 层: 输入\n# - id: I1\n#   name: 入参\n# 层: 算法\n# - id: F1~F7 七族\n"
        "#   name_zh: x\n# - id: O1\n#   name_zh: 结果\n# [/ALGO_FLOW]\n#\n# 边:\n# I1 --> O1\n"
    )
    assert data is not None
    problems = vm.validate_graph(data)
    assert any("节点ID非法" in p for p in problems), problems


def test_duplicate_node_id_detected() -> None:
    data = _data(
        "# 层: 输入\n# - id: I1\n#   name: 入参\n# - id: I1\n#   name: 重复\n"
        "# 层: 算法\n# - id: A1\n#   name_zh: 主流程\n# - id: O1\n#   name_zh: 结果\n"
        "# [/ALGO_FLOW]\n#\n# 边:\n# I1 --> A1\n# A1 --> O1\n"
    )
    assert data is not None
    assert any("节点ID重复" in p for p in vm.validate_graph(data))


def test_zero_edge_detected() -> None:
    """无边=推导图全体孤立（普查实证 5 件零边镜像），必须与"可解析"分开判。"""
    data = _data(
        "# 层: 输入\n# - id: I1\n#   name: 入参\n# 层: 算法\n# - id: A1\n#   name_zh: 主流程\n"
        "# - id: O1\n#   name_zh: 结果\n# [/ALGO_FLOW]\n"
    )
    assert data is not None
    assert any("无边定义" in p for p in vm.validate_graph(data))


def test_dangling_endpoint_detected() -> None:
    data = _data(
        "# 层: 输入\n# - id: I1\n#   name: 入参\n# 层: 算法\n# - id: A1\n#   name_zh: 主流程\n"
        "# - id: O1\n#   name_zh: 结果\n# [/ALGO_FLOW]\n#\n# 边:\n# I1 --> A1\n# A1 --> A9\n"
    )
    assert data is not None
    problems = vm.validate_graph(data)
    assert any("边终点未定义: A9" in p for p in problems), problems


def test_break_edge_consistency_detected() -> None:
    """断点边指向非断点节点 / 正常边指向断点节点，两向都要抓。"""
    body_base = (
        "# 层: 输入\n# - id: I1\n#   name: 入参\n# 层: 特征\n# - id: F1\n#   name_zh: 断点族\n"
        "#   is_break: true\n# 层: 算法\n# - id: O1\n#   name_zh: 结果\n# [/ALGO_FLOW]\n#\n# 边:\n"
    )
    plain_to_break = _data(body_base + "# I1 --> F1\n# F1 --> O1\n")
    assert plain_to_break is not None
    assert any("正常边指向断点节点" in p for p in vm.validate_graph(plain_to_break))

    break_to_plain = _data(body_base.replace("is_break: true", "is_break: false") + "# I1 -.->|断点| F1\n# F1 --> O1\n")
    assert break_to_plain is not None
    assert any("断点边指向非断点节点" in p for p in vm.validate_graph(break_to_plain))


def test_validate_file_still_aggregates_both_layers(tmp_path: Path) -> None:
    """validate_file = 字段判据 + 图判据（人工校准口径不变，一次给全）。"""
    p = tmp_path / "bad.txt"
    p.write_text(
        _block(
            "# 层: 输入\n# - id: I1\n#   name: 入参\n# 层: 算法\n# - id: A1\n#   name_zh: 主\n"
            "# - id: O1\n#   name_zh: 果\n# [/ALGO_FLOW]\n#\n# 边:\n# I1 --> A1\n# A1 --> A7\n"
        ),
        encoding="utf-8",
    )
    problems = vm.validate_file(p)
    assert any("边终点未定义: A7" in x for x in problems), problems
    assert any("缺必填字段" in x for x in problems), problems


def test_repo_mirrors_all_pass_graph_rules() -> None:
    """存量防线：全仓 algo_flow 镜像图必须全体可达。

    门禁只扫本 commit 清单（own-diff，#ARCH-GATE-OWN-SCOPE-001），坏图一旦落在提交窗外
    （生成器改口径、人工编辑镜像、解析器演化让旧语料失配）门禁永不再看见——唯有把
    "语料整体自洽"钉成常跑测试才有第二道防线。实测 3154 件单进程 0.8s，成本可忽略。
    """
    from code_algorithm_extractor import parse_algo_flow  # noqa: PLC0415 — 判据真源同一份

    mirrors = [m for m in (_REPO / "docs/03_modules").rglob("*.yaml") if "/algo_flow/" in m.as_posix()]
    assert mirrors, "docs/03_modules/**/algo_flow 无镜像=仓库检出异常（判据失真前置）"
    bad: list[str] = []
    for m in mirrors:
        try:
            text = m.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            bad.append(f"{m.name} 不可读({type(e).__name__})")
            continue
        data = parse_algo_flow(text)
        if data is None:
            bad.append(f"{m.name} 解析不到节点")
            continue
        bad.extend(f"{m.name}: {p}" for p in vm.validate_graph(data))
    assert not bad, f"{len(bad)} 条图判据问题：" + "；".join(bad[:10])
