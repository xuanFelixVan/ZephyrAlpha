# [A_test] module_id: MOD-GOV_commit_queue_revalidate_mergeable_pred | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_commit_queue_revalidate_mergeable_pred
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; copy; inspect; json; subprocess; importlib; scripts.commit_queue
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_revalidate_mergeable_pred.py
# [MATURITY] testing
# [INVARIANTS] 零生产写入（head_reader/谓词全为注入的纯可调用对象，不落盘不取 git 树）；
#              每条尺既能红又能绿（阳性=漂移必判死/必留痕，阴性=对齐必静默放行），恒绿尺不得进本文件；
#              回归锁的修复前基线取自钉死 blob 的**真实旧码**，非当前 HEAD（防自我循环论证）
# [MODIFY-GUARD] 半接线回归闸：_revalidate_stale_base 丢 mergeable_pred 形参、或 mergeable 放行
#                吞掉真冲突/放宽非 mergeable 判定、或 head_reader 缺失保险丝被谓词松动 ⇒ 即红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] permanent
"""`_revalidate_stale_base` 的 mergeable_pred 形参四条红证 + 半接线签名锁。

病灶（2026-09-27 一夜两袋实证，死因逐字相同）：落地侧
`scripts/governance/commit_queue_landing.py::_stale_revalidate_counted` 以
`mergeable_pred=is_registry_mergeable` 三参调用队列层 `_revalidate_stale_base`，
而该函数签名只有两参 ⇒ 任何被标 stale 的袋子在重校验时必抛
`TypeError: _revalidate_stale_base() got an unexpected keyword argument 'mergeable_pred'`，
被包成 `LandingEnvironmentError` → env_retry×3 耗尽 → 升级死信（处决式而非判据式退袋）。

治本口径（改动面只有定义侧，调用点/注入设计不属本尺）：
  ① 缺省 `mergeable_pred=None` ⇒ 判定与修复前**逐字节一致**（回归锁，红证 A）；
  ② 给出谓词时，确已比对出与 HEAD 不一致且谓词判真的路径改交落地侧条目级三向合并
     仲裁（W2 2026-09-22 上线），并写 `item.meta.rebased_registry` 留痕（红证 B）；
  ③ 非 mergeable 路径漂移仍判不适用，**禁放宽**（红证 C）；
  ④ `head_reader` 缺失＝根本没比对，保险丝照旧 fail-closed 判不适用，谓词无投票权
     （红证 D）；
  ⑤ 签名级防半接线：形参存在且有关省值、参数数 ≤7（红证 E，钉死本类缺陷不再复发）。

谓词真值口径由调用方持有（生产注入的是 `commit_queue_landing.is_registry_mergeable`，
= 注册表 catalogs 族 .yaml）；本文件用本地等价谓词，不 import 落地模块——那是别人的面。
"""

from __future__ import annotations

import copy
import importlib.util
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REG_REL = "docs/01_policies_and_standards/_registry/catalogs/probe_registry.yaml"
PY_REL = "scripts/demo_tool.py"
HEAD_MISSING = "(head_reader 缺失无法重校验)"
# 修复前基线：dev e8999a1593 的 scripts/commit_queue.py blob（不可变，钉死防 HEAD 漂移后
# 拿"改后码"当"改前基线"自我论证）。对象缺失时红证 A 降级为仅用转录件，见 _pre_fix_source。
PRE_FIX_BLOB = "56bba2e4552e18e20793a31008aaa5af921ac1e3"

# 修复前函数原文（逐字转录自 PRE_FIX_BLOB；红证 A 会用 git 取回的同一函数体做等值校验）
_PRE_FIX_SRC = '''def _revalidate_stale_base(item: dict, head_reader) -> tuple[bool, list[str]]:
    """stale 项基底重校验（66 号 §6.4）：base_blob vs 当前 HEAD 逐文件比对。

    返回 (仍适用, 不适用路径清单)。判定口径：
    - base_blob 为空的条目跳过（A 段无基底信息，无法判定→放行口径）；
    - base_blob 非空而 head_reader 缺失 → fail-closed 判不适用（无法确认仍适用即
      降死信候选，人工经 requeue 基于当前工作区重建快照取回，66 号 §6.4 死信闭环）；
    - head_reader: callable(仓内相对路径) -> 当前 HEAD 该路径 blob 标识（与 base_blob
      同 id 空间），路径不在 HEAD 返回 None；比对不一致即不适用。
    队列层保持零 git 依赖（66 号 §6.1 刻意出入 #3）——HEAD 读取能力由调用方注入。
    """
    mismatched: list[str] = []
    for f in item.get("files") or []:
        base_blob = f.get("base_blob")
        if not base_blob:
            continue
        path = f.get("path", "?")
        if head_reader is None:
            mismatched.append(f"{path}(head_reader 缺失无法重校验)")
            continue
        if head_reader(path) != base_blob:
            mismatched.append(path)
    return (not mismatched, mismatched)'''


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cq():
    return _load("_cq_revalidate_pred", "scripts/commit_queue.py")


def _extract_func(text: str, name: str) -> str:
    """从模块源码里切出一个顶层函数（含 docstring），列 0 处遇下一定义即止。"""
    picked: list[str] = []
    inside = False
    for line in text.splitlines():
        if not inside:
            if line.startswith(f"def {name}("):
                inside = True
                picked.append(line)
            continue
        if line.strip() and not line[0].isspace():
            break
        picked.append(line)
    assert inside, f"源码中未找到顶层函数 {name}（旧码结构变了？转录件需同步）"
    return "\n".join(picked).rstrip()


def _pre_fix_source() -> tuple[str, str]:
    """返回 (修复前函数源码, 来源标签)。优先用钉死的不可变 blob，缺失则退回逐字转录件。"""
    r = subprocess.run(
        ["git", "cat-file", "blob", PRE_FIX_BLOB],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if r.returncode != 0:
        return _PRE_FIX_SRC, "transcript(钉死 blob 不可达，降级用逐字转录件)"
    return _extract_func(r.stdout.replace("\r\n", "\n"), "_revalidate_stale_base"), f"blob:{PRE_FIX_BLOB[:12]}"


def _pre_fix_impl():
    """把修复前源码 exec 成可调用对象（旧函数体不引用任何模块级名字，故空命名空间即可）。"""
    src, _origin = _pre_fix_source()
    ns: dict = {}
    exec(compile(src, "<pre-fix _revalidate_stale_base>", "exec"), ns)  # noqa: S102 — 回归锁须跑真实旧码
    return ns["_revalidate_stale_base"]


def _registry_family(path: str) -> bool:
    """本地等价谓词（生产注入 `is_registry_mergeable`：注册表 catalogs 族 .yaml）。"""
    return path.startswith("docs/01_policies_and_standards/_registry/catalogs/") and path.endswith(".yaml")


def _always_true(path: str) -> bool:  # noqa: ARG001 — 保险丝测试要"谓词说什么都没有用"
    return True


def _reader(mapping: dict):
    """head_reader 注入件：仓内相对路径 → HEAD blob id；不在 HEAD → None（与生产同口径）。"""

    def read(rel: str) -> str | None:
        return mapping.get(rel)

    return read


def _item(files: list[dict], **meta) -> dict:
    item: dict = {"qid": "q-revalidate-pred", "session_id": "probe", "base_head": "sha-base", "files": files}
    if meta or files:
        item["meta"] = {"stale": True, **meta}
    return item


def _f(path: str, base_blob: str | None) -> dict:
    return {"path": path, "base_blob": base_blob}


# 红证 A 的判定矩阵：覆盖旧码全部分支（含 base_blob 空/缺键、reader 缺失、路径不在 HEAD、
# 多文件保序、无 meta 键、files 为 None/缺键、path 键缺失）——每一格都须新旧同结论。
_MATRIX: list[tuple[str, dict, dict | None]] = [
    (
        "全对齐",
        _item([_f(REG_REL, "blob-reg-base"), _f(PY_REL, "blob-py-base")]),
        {REG_REL: "blob-reg-base", PY_REL: "blob-py-base"},
    ),
    (
        "族文件漂移",
        _item([_f(REG_REL, "blob-reg-base")]),
        {REG_REL: "blob-reg-head-moved"},
    ),
    (
        "非族文件漂移",
        _item([_f(PY_REL, "blob-py-base")]),
        {PY_REL: "blob-py-head-moved"},
    ),
    (
        "路径不在 HEAD（reader 返 None）",
        _item([_f(PY_REL, "blob-py-base")]),
        {},
    ),
    (
        "head_reader 缺失 + base_blob 非空",
        _item([_f(REG_REL, "blob-reg-base"), _f(PY_REL, "blob-py-base")]),
        None,
    ),
    (
        "head_reader 缺失 + base_blob 空（跳过→放行）",
        _item([_f(REG_REL, ""), _f(PY_REL, None)]),
        None,
    ),
    (
        "base_blob 键缺失",
        _item([{"path": PY_REL}]),
        {PY_REL: "anything"},
    ),
    (
        "多文件混判（保序）",
        _item([_f(PY_REL, "b1"), _f(REG_REL, "b2"), _f("docs/x.md", "b3")]),
        {PY_REL: "b1", REG_REL: "b2-changed", "docs/x.md": "b3"},
    ),
    ("path 键缺失（回退 '?'）", _item([{"base_blob": "b1"}]), {"?": "b2"}),
    ("files 空表", _item([]), {}),
    ("files 为 None", {"qid": "q", "files": None, "meta": {"stale": True}}, {PY_REL: "b1"}),
    ("files 键缺失", {"qid": "q", "meta": {"stale": True}}, None),
    ("无 meta 键", {"qid": "q", "files": [_f(PY_REL, "b1")]}, {PY_REL: "b1"}),
    ("meta 为 None", {"qid": "q", "meta": None, "files": [_f(PY_REL, "b1")]}, {PY_REL: "b2"}),
]


# ---------------------------------------------------------------------------
# 红证 A（回归锁）：mergeable_pred 缺省时与修复前逐字节同结论 + 同入参 dict 零改动。
# ---------------------------------------------------------------------------


def test_red_a_default_pred_is_byte_identical_to_pre_fix(cq) -> None:
    pre_fix = _pre_fix_impl()
    src, origin = _pre_fix_source()
    if origin.startswith("blob"):
        # 反篡改交叉核：钉死 blob 取回的真实旧码必须等于文件头的逐字转录件
        assert src == _PRE_FIX_SRC, "基线旧码与转录件不一致——须复核（不得改转录件凑数）"
    for label, item, mapping in _MATRIX:
        for pass_name, reader in (("head_reader", _reader(mapping or {})), ("reader=None", None)):
            old_item = copy.deepcopy(item)
            new_item = copy.deepcopy(item)
            got_old = pre_fix(old_item, reader)  # 不传第三参＝修复前唯一口径
            got_new = cq._revalidate_stale_base(new_item, reader)  # 缺省 mergeable_pred
            assert got_old == got_new, f"[{label}/{pass_name}] 结论漂移：旧={got_old} 新={got_new}"
            assert json.dumps(old_item, sort_keys=True) == json.dumps(new_item, sort_keys=True), (
                f"[{label}/{pass_name}] 缺省谓词不得改写袋子内容（禁偷注 meta）"
            )


# ---------------------------------------------------------------------------
# 红证 B（本改动要点）：mergeable 族确已漂移 → 不判不适用 + meta 留痕；同项缺省谓词必死。
# ---------------------------------------------------------------------------


def test_red_b_mergeable_drift_handed_to_merge_arbitration_with_trace(cq) -> None:
    item = _item([_f(REG_REL, "blob-reg-base")])
    strict = copy.deepcopy(item)
    # 先能红：缺省谓词（=旧严格口径）必须判不适用，否则本尺是恒绿尺
    ok_strict, mism_strict = cq._revalidate_stale_base(strict, _reader({REG_REL: "blob-moved"}))
    assert not ok_strict and mism_strict == [REG_REL], "旧严格口径失效——改动面被顺手放宽？"
    assert "rebased_registry" not in (strict.get("meta") or {}), "严格口径不得留 re-base 痕"

    ok, mism = cq._revalidate_stale_base(item, _reader({REG_REL: "blob-moved"}), mergeable_pred=_registry_family)
    assert ok and mism == [], f"mergeable 族漂移应交合并仲裁，实得 ok={ok} mism={mism!r}"
    assert item["meta"]["rebased_registry"] == [REG_REL], f"放行必须留审计痕，实得 meta={item['meta']!r}"

    # 阴性控制（尺非恒放行）：基底对齐 ⇒ 放行但**不**记 rebased_registry（区分两种放行）
    aligned = _item([_f(REG_REL, "blob-reg-base")])
    ok2, mism2 = cq._revalidate_stale_base(
        aligned, _reader({REG_REL: "blob-reg-base"}), mergeable_pred=_registry_family
    )
    assert ok2 and mism2 == [] and "rebased_registry" not in (aligned.get("meta") or {})

    # 多路径留痕须保序且只收漂移项
    mixed = _item(
        [_f(REG_REL, "b1"), _f(PY_REL, "b2"), _f("docs/01_policies_and_standards/_registry/catalogs/other.yaml", "b3")]
    )
    ok3, mism3 = cq._revalidate_stale_base(
        mixed,
        _reader({REG_REL: "x", PY_REL: "b2", "docs/01_policies_and_standards/_registry/catalogs/other.yaml": "y"}),
        mergeable_pred=_registry_family,
    )
    assert ok3 and mism3 == []
    assert mixed["meta"]["rebased_registry"] == [
        REG_REL,
        "docs/01_policies_and_standards/_registry/catalogs/other.yaml",
    ]


# ---------------------------------------------------------------------------
# 红证 C（禁放宽）：非 mergeable 路径漂移在注入谓词后仍判不适用，且不混入留痕。
# ---------------------------------------------------------------------------


def test_red_c_nonmergeable_drift_still_inapplicable(cq) -> None:
    item = _item([_f(PY_REL, "blob-py-base")])
    ok, mism = cq._revalidate_stale_base(item, _reader({PY_REL: "blob-py-moved"}), mergeable_pred=_registry_family)
    assert not ok and mism == [PY_REL], f"非 mergeable 漂移必须仍判不适用，实得 ok={ok} mism={mism!r}"
    assert "rebased_registry" not in (item.get("meta") or {}), "非 mergeable 不得混入 re-base 痕"

    # 混合袋：族项放行留痕、非族项拖袋殉葬语义不变（ok=False，清单只含非族）
    bag = _item([_f(PY_REL, "p1"), _f(REG_REL, "r1")])
    ok2, mism2 = cq._revalidate_stale_base(
        bag, _reader({PY_REL: "p1-moved", REG_REL: "r1-moved"}), mergeable_pred=_registry_family
    )
    assert not ok2 and mism2 == [PY_REL], f"混合袋只该非族项殉葬，实得 {mism2!r}"
    assert bag["meta"]["rebased_registry"] == [REG_REL]

    # 路径不在 HEAD（reader 返 None）＝确已比对出不一致，非族项仍死、不得混入留痕
    gone = _item([_f(PY_REL, "blob-py-base")])
    ok3, mism3 = cq._revalidate_stale_base(gone, _reader({}), mergeable_pred=_registry_family)
    assert not ok3 and mism3 == [PY_REL], f"非 mergeable 路径不得因谓词在场而放行：{mism3!r}"
    assert "rebased_registry" not in (gone.get("meta") or {})

    # 谓词说了算（口径边界留证）：谓词恒真时 .py 也被交合并仲裁——爆炸半径由**注入方**负责
    # （生产注入的是窄口径 is_registry_mergeable，故本行不构成放宽；红证 D 另钉"谓词无投票权"
    # 的那一面：没比对出结果时谁都别想放行）
    wide = _item([_f(PY_REL, "blob-py-base")])
    ok4, mism4 = cq._revalidate_stale_base(wide, _reader({PY_REL: "moved"}), mergeable_pred=_always_true)
    assert ok4 and mism4 == [] and wide["meta"]["rebased_registry"] == [PY_REL]


# ---------------------------------------------------------------------------
# 红证 D（保险丝不动）：head_reader=None 且 base_blob 非空 → 仍 fail-closed 判不适用，
# loud marker 逐字保留，谓词无投票权，且不留 re-base 痕（没比对＝谈不上漂移）。
# ---------------------------------------------------------------------------


def test_red_d_missing_head_reader_fuse_untouched(cq) -> None:
    for pred in (None, _registry_family, _always_true):
        item = _item([_f(REG_REL, "blob-reg-base"), _f(PY_REL, "blob-py-base")])
        ok, mism = cq._revalidate_stale_base(item, None, mergeable_pred=pred)
        label = getattr(pred, "__name__", "None")
        assert not ok, f"[谓词={label}] head_reader 缺失必须 fail-closed，实得 ok={ok}"
        assert mism == [f"{REG_REL}{HEAD_MISSING}", f"{PY_REL}{HEAD_MISSING}"], (
            f"[谓词={label}] loud marker 文案/顺序须逐字不变，实得 {mism!r}"
        )
        assert "rebased_registry" not in (item.get("meta") or {}), f"[谓词={label}] 未比对不得留 re-base 痕"


# ---------------------------------------------------------------------------
# 红证 E（签名级防半接线）：第三形参存在/有省值/参数数 ≤7——钉死本类 TypeError 不再复发。
# ---------------------------------------------------------------------------


def test_red_e_signature_accepts_mergeable_pred_keyword(cq) -> None:
    params = inspect.signature(cq._revalidate_stale_base).parameters
    assert "mergeable_pred" in params, f"形参缺失＝半接线缺陷复发（调用侧三参必抛 TypeError）：{list(params)}"
    assert params["mergeable_pred"].default is None, "缺省必须 None（向后兼容＝旧严格口径）"
    assert len(params) <= 7, f"NO-LONG-PARAM-LIST 违例：{list(params)}"
    # 逃生实证：修复前的两参签名对三参调用必抛 TypeError（先能红，证明本尺确有判别力）
    pre_fix = _pre_fix_impl()
    with pytest.raises(TypeError):
        pre_fix(_item([_f(REG_REL, "b")]), _reader({REG_REL: "x"}), mergeable_pred=_registry_family)
