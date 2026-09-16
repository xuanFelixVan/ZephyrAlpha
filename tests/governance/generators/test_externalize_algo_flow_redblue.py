# [A_test] test_id=P21-REDBLUE-001 | module=scripts/governance/d5_architecture/generators/externalize_algo_flow.py | gate=pytest
# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | scripts/governance/d5_architecture/generators/externalize_algo_flow.py | 出仓规划面红蓝不变量
# [MODULE] tests.governance.generators.test_externalize_algo_flow_redblue
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_externalize_algo_flow_redblue.py — 出仓器规划面八不变量红蓝对抗（P2-1 战役 2026-09-16）。

波次 2246 件把 `# [ALGO_FLOW]` 机器块从 src/ 模块 docstring 外迁到
docs/03_modules/<域>/algo_flow/*.yaml，出仓器一次跑数百件；任何一条不变量破口都是
**静默丢图**（两源共用一 yaml 后者覆盖前者）或**跨会话污染**（写到别人真源上），
故按"最坏故障优先"固化成回归面。八条不变量：

  I1 注入性  批内两源绝不共用一落点
  I2 落点合法 全部落 docs/03_modules/<域>/algo_flow/…，域目录不得退化成 ``_domain___init__``
  I3 容量    任一落点目录件数 < folder_capacity_hard_limit(120)
  I4 确定性  批内乱序 → 映射集合不变（dry-run 可复现）
  I5 幂等    全量二跑 → already/skipped、零新件、源文件字节不变
  I6 封闭性  写入只发生在本批 .py 与 docs/03_modules
  I7 侵犯性  预置 foreign yaml 内容逐字节不变（他人真源不可侵犯）
  I8 路径长  绝对路径 < 240（Windows MAX_PATH，含 flatten 末路名）

外加"图守恒"判据：落点 yaml 重解析必须仍是 3 节点/3 边（含 1 条断边）——
出仓前后 extractor 读到的图逐项等，才是链路真通。

六个场景族覆盖实证踩过的坑：``__init__`` 同名风暴 / 全域饱和镜像分片 /
CJK 同 stem 深路径 + flatten 末路名 / 升档阶梯部分被占（必须升档）/
整条阶梯被占（fail-closed 宁漏勿覆盖）/ 真实家族抽样（gov_enforcement 源路径深、__init__ 多）。

另钉一条链路不变量：rollout 应用器（algo_flow_applier）写完内联块后必须串调出仓器——
内联块在 extractor ``own_graph`` 里优先于 external 锚，只写内联会把已出仓件吞回并留下孤儿 yaml。

全测试在 tmp_path 假仓库里跑（monkeypatch 出仓器与 extractor 两侧 REPO_ROOT），零触真盘。
"""

from __future__ import annotations

import hashlib
import random
import shutil
import sys
import textwrap
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

_GOV_DIR = str(REPO_ROOT / "scripts" / "governance")
_GEN_DIR = str(REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "generators")
for _p in (_GOV_DIR, _GEN_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import _shared.code_algorithm_extractor as coae  # noqa: E402
import externalize_algo_flow as ext  # noqa: E402

BLOCK = (
    "# [ALGO_FLOW]\n"
    "# 层: 输入\n"
    "# - id: I1\n"
    "#   name: 入参\n"
    "# 层: 算法\n"
    "# - id: A1\n"
    "#   name_zh: ① 主流程\n"
    "# 层: 输出\n"
    "# - id: O1\n"
    "#   name: 出参\n"
    "# [/ALGO_FLOW]\n"
    "#\n"
    "# 边:\n"
    "# I1 --> A1\n"
    "# A1 --> O1\n"
    "# A1 -.-> O1\n"
)

_DEEP = "src/zephyr/gov_enforcement/rule_enforcement/detectors/triple_alignment/long_named_subpackage"

_CAPACITY = 120
_MAX_PATH = 240


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    def _clear():
        for d in (
            ext._PLANNED_REMAP,
            ext._PLANNED_MIRROR,
            ext._PLANNED_UNIQ,
            ext._EXISTING_YAML_CACHE,
        ):
            d.clear()
        ext._MIRROR_DOMAINS.clear()

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(coae, "REPO_ROOT", tmp_path)
    _clear()
    yield tmp_path
    _clear()


def _mk(root: Path, rel: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f'"""{p.stem} —— 红蓝夹具。\n\n{BLOCK}"""\n', encoding="utf-8")
    return p


def _plan(root: Path, targets: list[Path]) -> dict[str, str]:
    ext._EXISTING_YAML_CACHE.clear()
    ext._plan_stem_collision_remaps(targets)
    ext._plan_capacity_mirrors(targets)
    ext._plan_path_uniqueness(targets)
    out: dict[str, str] = {}
    for p in targets:
        rel = p.relative_to(root).as_posix()
        dom = ext._domain_of(rel)
        out[rel] = (
            ext._existing_yaml_for(rel, dom)
            or ext._PLANNED_UNIQ.get(rel, "")
            or ext._PLANNED_MIRROR.get(rel, "")
            or ext._PLANNED_REMAP.get(rel, "")
            or ext._yaml_rel_for(p, rel, dom)
        )
    return out


def _snapshot(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


def _seed_flat(root: Path, dom: str, n: int) -> None:
    d = root / "docs" / "03_modules" / dom / "algo_flow"
    d.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        (d / f"legacy_{i:05d}.yaml").write_text(
            f"source_of_truth: src/zephyr/legacy_owner/l{i:05d}.py\n", encoding="utf-8"
        )


def _run_scenario(
    root: Path,
    rels: list[str],
    *,
    seed_dom: str = "",
    seed_n: int = 0,
    foreign: list[str] | None = None,
    expect_failed: bool = False,
    expect_escalated: bool = False,
) -> list[str]:
    """跑一遍八不变量，返回破口清单（空=全绿）。"""
    targets = [_mk(root, r) for r in rels]
    if seed_dom and seed_n:
        _seed_flat(root, seed_dom, seed_n)
    for i, f in enumerate(foreign or []):
        p = root / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"source_of_truth: src/zephyr/foreign_{i}/x.py\n# 不可侵犯\n", encoding="utf-8")
    foreign_before = {f: (root / f).read_bytes() for f in foreign or []}

    breaks: list[str] = []
    m = _plan(root, targets)

    if expect_escalated:
        for p in targets:
            rel = p.relative_to(root).as_posix()
            ext._PLANNED_UNIQ.clear()  # 复原"未消歧"预测名=阶梯第一级
            pre = ext._predicted_yaml_rel(p, rel, ext._domain_of(rel))
            if pre not in set(foreign or []):
                breaks.append(f"升档陷阱未咬合: {rel} 原始预测 {pre} 未被 foreign 占据")
            elif m[rel] == pre:
                breaks.append(f"升档未发生: {rel} 仍落在他人真源 {m[rel]}")
        ext._plan_stem_collision_remaps(targets)
        ext._plan_capacity_mirrors(targets)
        ext._plan_path_uniqueness(targets)

    dup: dict[str, list[str]] = {}
    for rel, y in m.items():
        dup.setdefault(y, []).append(rel)
    if bad := {y: v for y, v in dup.items() if len(v) > 1}:
        breaks.append(f"I1 注入性: {list(bad.items())[:2]}")

    illegal = [y for y in m.values() if not y.startswith("docs/03_modules/") or "/algo_flow/" not in y]
    degenerate = [y for y in m.values() if "_domain___init__" in y or y.endswith("/_domain_/")]
    if illegal or degenerate:
        breaks.append(f"I2 落点合法: {(illegal + degenerate)[:2]}")

    per_dir: dict[str, int] = {}
    for y in m.values():
        per_dir[y.rsplit("/", 1)[0]] = per_dir.get(y.rsplit("/", 1)[0], 0) + 1
    for d0 in list(per_dir):
        p0 = root / d0
        if p0.is_dir():
            per_dir[d0] += sum(1 for q in p0.iterdir() if q.is_file())
    if over := {d0: c for d0, c in per_dir.items() if c >= _CAPACITY}:
        breaks.append(f"I3 容量<{_CAPACITY}: {list(over.items())[:3]}")

    # I8 判的是"落点路径在生产仓根下的长度"——用 tmp_path 前缀会虚高误报
    if long := [y for y in m.values() if len(str(REPO_ROOT / y)) >= _MAX_PATH]:
        breaks.append(f"I8 路径<{_MAX_PATH}: {long[:2]}")

    sh = list(targets)
    for k in (1, 2, 3):
        random.Random(k).shuffle(sh)
        if _plan(root, sh) != m:
            breaks.append(f"I4 乱序确定性: seed={k} 映射变化")
            break

    _plan(root, targets)
    before = _snapshot(root)
    r1 = [ext.externalize(p, dry_run=False) for p in targets]
    after1 = _snapshot(root)
    _plan(root, targets)
    r2 = [ext.externalize(p, dry_run=False) for p in targets]
    after2 = _snapshot(root)

    landed = {r["file"] for r in r1 if r["status"] == "externalized"}
    for rel, y in m.items():
        if rel not in landed:
            continue
        yp = root / y
        if not yp.is_file():
            breaks.append(f"图守恒: {rel} yaml 缺失")
            continue
        raw = yp.read_text(encoding="utf-8")
        body = raw.split("algo_flow: |\n", 1)
        g = ext.parse_algo_flow(textwrap.dedent(body[1]) if len(body) > 1 else raw)
        if g is None or len(g.nodes) != 3 or len(g.edges) != 3:
            nn = 0 if g is None else len(g.nodes)
            ee = 0 if g is None else len(g.edges)
            breaks.append(f"图守恒: {rel} nodes={nn} edges={ee}（应 3n3e 含 1 断边）")

    st2 = {r["status"] for r in r2}
    allowed = {"already", "skipped"} | ({"failed"} if expect_failed else set())
    if after1 != after2 or not st2 <= allowed:
        breaks.append(f"I5 幂等: 二跑状态={sorted(st2)} 快照差异={len(set(after1) ^ set(after2))}")
    if newfiles := set(after2) - set(after1):
        breaks.append(f"I5 零新件: {list(newfiles)[:3]}")
    for rel in landed:
        t = (root / rel).read_text(encoding="utf-8")
        if "# [ALGO_FLOW] external:" not in t or "# [ALGO_FLOW]\n" in t:
            breaks.append(f"I5 源留单锚: {rel}")
            break

    touched = {k for k in set(after1) ^ set(before) if not k.startswith("docs/03_modules/")}
    if outside := {k for k in touched if k not in m}:
        breaks.append(f"I6 封闭性: {list(outside)[:3]}")

    for f, b in foreign_before.items():
        if (root / f).read_bytes() != b:
            breaks.append(f"I7 foreign 不可侵犯: {f}")
            break

    failed = [r for r in r1 if r["status"] == "failed"]
    if expect_failed:
        ok = len(failed) == len(targets) and all(
            "被他人真源占用" in r.get("reason", "") for r in failed
        )
        leaked = {f for f in set(after1) - set(before)} - {f for f in after1 if f.endswith(".py.bak")} - set(m.values())
        if not ok or leaked:
            breaks.append(
                f"fail-closed: failed={len(failed)}/{len(targets)} "
                f"reasons={[(r['file'], r.get('reason', '')[:40]) for r in failed][:2]} leaked={list(leaked)[:2]}"
            )
    elif failed:
        breaks.append(f"无 failed: {[(r['file'], r.get('reason', '')[:60]) for r in failed][:3]}")
    return breaks


SCENARIOS: dict[str, dict] = {
    # ``__init__`` 风暴：五个同名子包 + 域根同名，平铺命名天然不唯一（F1 事故族）
    "init_storm": {
        "rels": [f"src/zephyr/sf/{p}/implementations/__init__.py" for p in ("gen", "strategy", "macro", "micro", "x")]
        + ["src/zephyr/sf/implementations/__init__.py"]
    },
    # 全域饱和：平铺触镜像阈值后按源子包镜像，超容量桶再分片（GOV-DOC-018 自动化）
    "saturated_mirror": {
        "rels": [f"src/zephyr/big/sub{i % 7}/mod{j}.py" for i in range(7) for j in range(30)],
        "seed_dom": "_domain_big",
        "seed_n": ext._MIRROR_TRIGGER,
    },
    # 深路径 + CJK 同 stem 多子包 + flatten 末路名长度压力（Windows MAX_PATH）
    "deep_cjk_path": {
        "rels": [
            f"{_DEEP}/detector_混合.py",
            f"{_DEEP}/nested/detector_混合.py",
            f"{_DEEP}/nested/deeper/detector_混合.py",
            "src/zephyr/big/sub0/__init__.py",
            "src/zephyr/big/__init__.py",
        ]
    },
    # 升档阶梯（F-C 治本后）四级：stem / parent__stem / pkg__parent__stem / 路径拉平。
    # 占前两级 + 一个诱饵名 → 必须升档到第三级落盘（规划期消歧，重跑可解），不再 fail-closed
    "foreign_ladder_escalates": {
        "rels": ["src/zephyr/zz/solo.py"],
        "foreign": [
            "docs/03_modules/_domain_zz/algo_flow/solo.yaml",
            "docs/03_modules/_domain_zz/algo_flow/zz__solo.yaml",
            "docs/03_modules/_domain_zz/algo_flow/s4__solo.yaml",
        ],
        "expect_escalated": True,
    },
    # 整条阶梯（含末路拉平名）全被他人真源占 → 唯一剩余处置=fail-closed，
    # 宁漏勿覆盖（静默改写别人的图=最坏故障）
    "foreign_whole_ladder": {
        "rels": ["src/zephyr/zz/solo.py"],
        "foreign": [
            "docs/03_modules/_domain_zz/algo_flow/solo.yaml",
            "docs/03_modules/_domain_zz/algo_flow/zz__solo.yaml",
            "docs/03_modules/_domain_zz/algo_flow/zz__zz__solo.yaml",
            "docs/03_modules/_domain_zz/algo_flow/src_zephyr_zz_solo.yaml",
        ],
        "expect_failed": True,
    },
    # 真实形态抽样：源路径深、__init__ 多、平铺余量贴近阈值
    "real_family_sample": {
        "rels": [
            f"src/zephyr/gov_enforcement/{pkg}/{kind}"
            for pkg in ("rule_enforcement", "commit_gates", "rule_bridge")
            for kind in ("module_a.py", "module_b.py", "module_c.py", "__init__.py")
        ],
        "seed_dom": "_domain_gov_enforcement",
        "seed_n": 95,
    },
}


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_planner_invariants_hold(name: str, tmp_path: Path) -> None:
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    tmp_path.mkdir(parents=True)
    cfg = SCENARIOS[name]
    breaks = _run_scenario(
        tmp_path,
        cfg["rels"],
        seed_dom=cfg.get("seed_dom", ""),
        seed_n=cfg.get("seed_n", 0),
        foreign=cfg.get("foreign"),
        expect_failed=cfg.get("expect_failed", False),
        expect_escalated=cfg.get("expect_escalated", False),
    )
    assert not breaks, f"{name} 不变量破口:\n" + "\n".join(f"  - {b}" for b in breaks)


def test_applier_chain_externalizes(monkeypatch, tmp_path: Path) -> None:
    """rollout→出仓 串调（#28 链路对冲）：写完内联块必须当场外迁成锚。

    只写内联的后果不是"少一步美化"而是**功能回退**：extractor ``own_graph`` 里
    内联块优先于 external 锚，已出仓件被内联吞回、yaml 成孤儿图。
    """
    shared = str(REPO_ROOT / "scripts" / "governance" / "_shared")
    if shared not in sys.path:
        sys.path.insert(0, shared)
    import algo_flow_applier as applier  # noqa: PLC0415

    monkeypatch.setattr(applier, "REPO_ROOT", tmp_path)
    p = _mk(tmp_path, "src/zephyr/zz_chain/solo.py")

    status, yaml_rel = applier.externalize_after_apply(p)
    assert status == "externalized", f"首跑应外迁，实为 {status} {yaml_rel}"
    assert (tmp_path / yaml_rel).is_file(), f"落盘 yaml 缺失 {yaml_rel}"

    src = p.read_text(encoding="utf-8")
    assert "# [ALGO_FLOW] external: " in src, "源码未留 external 锚"
    assert "# [/ALGO_FLOW]" not in src, "内联块残留=own_graph 会优先吞回"

    got = coae.extract_algorithm_from_code(p, module_id="", truncate=False)
    assert got.algo_flow is not None and len(got.algo_flow.nodes) == 3, "锚→yaml 链路未解出全图"

    assert applier.externalize_after_apply(p)[0] == "already", "二跑必须 already（幂等）"


# ---------------------------------------------------------------- 写法变体红蓝（图判据批 2026-09-16）
# 出仓器只搬字节不搬语义的风险，全在"写法"这一维：真实语料里三种写法（速记 id 带中文描述 /
# 并列端点 # I1,I2 --> F1 / 分号紧凑 # 边: A --> B ; C --> D）曾被解析器静默降级成
# "锚在、块在、图空"。三写法过出仓器必须图逐项等——这才是链路真通的判据。
_SPELLINGS: dict[str, str] = {
    "shorthand_id": (
        "# [ALGO_FLOW]\n"
        "# 层: 输入\n# - id: I1 入参闸门\n"
        "# 层: 算法\n# - id: A1 主流程\n"
        "# 层: 输出\n# - id: O1 出参\n"
        "# [/ALGO_FLOW]\n#\n# 边:\n# I1 --> A1\n# A1 --> O1\n"
    ),
    "comma_fanin": (
        "# [ALGO_FLOW]\n"
        "# 层: 输入\n# - id: I1\n#   name: 入参一\n# - id: I2\n#   name: 入参二\n"
        "# 层: 算法\n# - id: F1\n#   name_zh: 汇流\n# - id: A1\n#   name_zh: 主流程\n"
        "# [/ALGO_FLOW]\n#\n# 边:\n# I1, I2 --> F1\n# F1 --> A1\n"
    ),
    "semicolon_compact": (
        "# [ALGO_FLOW]\n"
        "# 层: 输入\n# - id: I1\n#   name: 入参\n"
        "# 层: 算法\n# - id: A1\n#   name_zh: 主流程\n"
        "# 层: 输出\n# - id: O1\n#   name_zh: 出参\n#   is_break: true\n"
        "# [/ALGO_FLOW]\n#\n# 边: I1 --> A1 ; A1 -.->|断点| O1\n"
    ),
}


@pytest.mark.parametrize("name", sorted(_SPELLINGS))
def test_spelling_variants_survive_externalization(name: str, tmp_path: Path) -> None:
    """三种真实写法过出仓器：镜像图 == 内联图 == 锚回读图，且过图判据零问题。"""
    from _shared.algo_flow_validate_marker import validate_graph  # noqa: PLC0415

    def key(g):
        return ({n.id for n in g.nodes}, {(e.src, e.dst, e.is_break) for e in g.edges})

    p = tmp_path / "src/zephyr/zz_spell/solo.py"
    p.parent.mkdir(parents=True)
    p.write_text(f'"""solo —— 红蓝夹具。\n\n{_SPELLINGS[name]}"""\n', encoding="utf-8")
    before = coae.parse_algo_flow(p.read_text(encoding="utf-8"))
    assert before is not None and before.edges, "夹具本身无边=红蓝失效（前置判据）"

    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "externalized", f"出仓失败：{r}"
    mirror = (tmp_path / r["yaml"]).read_text(encoding="utf-8")
    after = coae.parse_algo_flow(mirror)
    assert after is not None, "镜像重解析不到节点"

    assert key(after) == key(before), f"{name} 出仓前后图不等：{key(before)} -> {key(after)}"
    problems = validate_graph(after)
    assert problems == [], f"{name} 镜像过图判据仍有问题：{problems}"

    back = coae.extract_algorithm_from_code(p, module_id="", truncate=False)
    assert back.algo_flow is not None, "锚→yaml 读路未解出图"
    assert key(back.algo_flow) == key(before), f"{name} 锚回读图与源图不等：{key(back.algo_flow)}"
