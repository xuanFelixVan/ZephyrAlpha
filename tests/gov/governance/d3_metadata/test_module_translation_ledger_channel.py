# [MODULE] tests.gov.governance.d3_metadata.test_module_translation_ledger_channel
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.governance.d3_metadata.add_module_translation;
#   zephyr.governance.registry_ledger.api / .baseline；
#   zephyr.governance.registry_projection.projection_generator / .model；
#   zephyr.gov_enforcement.commit_gates.translation_coverage_gate；
#   基线 commit 的内容寻址 blob（git show cfbebbf8dd:<path>，不落 .orig 副本）
# [CONSUMERS] 本班红证（st-maint2-20261011 T3+T7：登记侧通道病根治 / drift 记账族名硬编码）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 账本三步（api.register/update、publish_snapshot、projection run）全部经
#   monkeypatch 替身或 tmp 仓 + JSON 影子快照源，**零生产 PG 写、零真仓投影写**；
#   红证面=死路三步逐条堵住（登记入 PG ∧ render 后条目仍在 ∧ 门禁提示语指回本 CLI）；
#   反向钉桩=baseline 发布 SQL 的 status='active' 过滤未被放松（retired 永不进快照）
# [MODIFY-GUARD] 新建 2026-10-11 st-maint2-20261011（任务书红证 1-8 + 两条附加钉桩）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError（含"pristine 缺陷必须成立"的反向断言）
# [TESTS] self
# [TTL] task_bound
"""模块翻译登记通道（意图 API 薄壳）红证——病=登记工具直写投影 → render 修剪 → 门禁指回直写工具。

十二例覆盖任务书红证 1-8 与四条附加钉桩：
1. 新登记 → api.register 收到正确 payload（module_path 置首）+ publish + render 各一次
2. 同 module_path 重复登记 → 走 update 且**他人字段一个不丢**（键集合差分=只注入声明键）
3. render 之后条目仍在（真跑投影生成器 render 腿，tmp 仓 + JSON 影子快照源）
4. 逃生旗：缺省不直写；显式 --legacy-disk-write 才直写，且红色警告 + 审计留痕可断言
5. 门禁提示语给出的命令能被本 CLI 真实参数解析（机判，非字符串比对）
6. drift 记账不再恒 0/0：按该册声明的族集合逐族算（entries 族非零、creation_tokens 族不变）
7. pristine 红证：dev 原版字节三处缺陷逐条成立（无账本调用 / 硬编码族名 / 提示语指直写）
8. 反向钉桩：baseline 发布 SQL 的 status='active' 未被改动 + 审计把未入账本条目报出来
9. PG 不可达 = 登记失败且不降级直写（死路不能被"应急"重新接通）
10. 未点名删除 = 拒写；多 active 行 = 拒登记（不再插副本）
11. 合规校验前置于账本调用（不合规简介零 PG 触达）
12. CLI 派发：审计与单条目参数互斥、审计零写
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import scripts.governance.d3_metadata.add_module_translation as amt
from zephyr.governance.registry_ledger import api, baseline
from zephyr.governance.registry_projection import projection_generator as pg
from zephyr.governance.registry_projection.model import snapshot_from_yaml
from zephyr.governance.registry_projection.state import load_state

_REPO_ROOT = Path(amt.__file__).resolve().parents[3]
API_REG = "zephyr.governance.registry_ledger.api.register"
API_UPDATE = "zephyr.governance.registry_ledger.api.update"
PUBLISH = "zephyr.governance.registry_ledger.baseline.publish_snapshot"
PROJ_RUN = "zephyr.governance.registry_projection.projection_generator.run"

# 被测面（tmp 沙盘用）：只有两族的小册，形态与真册同构（unique_key 声明 + 尾部标量）
SMALL_REGISTRY = """module_id: REG-MODULE-TRANSLATION-001
registry_id: REG-MODULE-TRANSLATION-001
ttl: permanent
unique_key:
  entries: [module_path]
  battle_map_steps: [step_id]
entries:
- module_path: a.py
  name_zh: 甲模块
  plain_zh: 甲模块的大白话简介说明它做什么
battle_map_steps:
- step_id: s1
  name_zh: 步骤一
di_seam_exemptions: []
"""


def _entry(path: str = "scripts/demo/mod.py", **over) -> dict:
    base = {
        "module_path": path,
        "domain_id": "D_TEST",
        "name_zh": "演示模块",
        "name_en": "Demo Module",
        "desc_zh": "演示用技术简介",
        "desc_en": "demo desc",
        "plain_zh": "演示模块：把一条大白话简介登记进账本，再发布快照重打投影给门禁读",
    }
    base.update(over)
    return base


def _res(code: str, detail: dict | None = None) -> SimpleNamespace:
    return SimpleNamespace(code=code, detail=detail or {}, entry=None, event_id=1)


class _Ledger:
    """账本替身：签名对齐本工具的三个包装（_ledger_rows/_ledger_register/_ledger_update）。"""

    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.calls: list[tuple] = []

    def read_rows(self, module_path: str) -> list[dict]:
        return [
            dict(r, payload=dict(r["payload"])) for r in self.rows if r["payload"].get("module_path") == module_path
        ]

    def register(self, payload, *, reason, session_id):
        self.calls.append(("register", dict(payload), reason, session_id))
        assert next(iter(payload)) == "module_path", "身份键必须置首（PG jsonb 键序重排免疫）"
        self.rows.append(
            {
                "entry_key": f"module_path={payload['module_path']}",
                "payload": dict(payload),
                "version": 1,
                "status": "active",
            }
        )
        return _res(api.OK)

    def update(self, entry_key, expected_version, payload, *, reason, session_id):
        self.calls.append(("update", entry_key, expected_version, dict(payload), reason, session_id))
        row = next((r for r in self.rows if r["entry_key"] == entry_key), None)
        if row is None:
            return _res(api.NOT_FOUND)
        if int(row["version"]) != int(expected_version):
            return _res(api.CONFLICT_VERSION, {"current_version": row["version"]})
        row["payload"] = dict(payload)
        row["version"] = int(row["version"]) + 1
        return _res(api.OK, {"version": row["version"]})


@pytest.fixture(autouse=True)
def hermetic_generic_check(monkeypatch):
    """通用模板检测走生产册（只读）——测试里换成确定性替身。"""
    monkeypatch.setattr(amt, "is_generic_plain_zh", lambda s: s.startswith("提供包入口"))
    monkeypatch.setattr(amt, "is_generic_plain_suffix", lambda s, n: False)


def _render_face_from_ledger(reg: Path, ledger: _Ledger) -> None:
    """把账本 active 面重打成投影册（模拟生成器 PG-wins 写盘；复用被测模块的段落切分器）。"""
    text = reg.read_text(encoding="utf-8")
    preamble, _body, tail = amt._split_entries_section(text)
    entries = [r["payload"] for r in ledger.rows if r["status"] == "active"]
    new_body = "".join(yaml.safe_dump([p], allow_unicode=True, sort_keys=False) for p in entries)
    reg.write_text(amt._join_sections(preamble, new_body, tail), encoding="utf-8", newline="\n")


@pytest.fixture()
def sandbox(tmp_path: Path, monkeypatch):
    """账本替身 + tmp 投影册 + publish/render 替身（零生产写）。"""
    reg = tmp_path / amt.REGISTRY_REL
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(SMALL_REGISTRY, encoding="utf-8", newline="\n")
    ledger = _Ledger()
    state = {"publish": 0, "render": 0, "disk_writes": 0}

    monkeypatch.setattr(amt, "REGISTRY_YAML", reg)
    monkeypatch.setattr(amt, "PROJECTION_ROOT", tmp_path)
    monkeypatch.setattr(amt, "LEGACY_DISK_WRITE_AUDIT_PATH", tmp_path / ".runtime" / "gate_audit" / "legacy.jsonl")
    monkeypatch.setattr(amt, "_read_layer_map", lambda: {"D_TEST": "governance"})
    monkeypatch.setattr(amt, "_ledger_rows", ledger.read_rows)
    monkeypatch.setattr(amt, "_ledger_register", ledger.register)
    monkeypatch.setattr(amt, "_ledger_update", ledger.update)

    def fake_publish(registry_id, *, repo_root=None, session_id="", **kw):
        state["publish"] += 1
        assert repo_root == tmp_path, "publish_snapshot 必须带 repo_root（裸发布被 baseline 机械拒绝）"
        return {"registry_id": registry_id, "noop": False, "snapshot_version": 999}

    def fake_render(root, mode="check", **kw):
        state["render"] += 1
        assert mode == "render"
        assert kw.get("registry_id") == amt.REGISTRY_ID
        assert kw.get("physical_path") == amt.REGISTRY_REL
        _render_face_from_ledger(reg, ledger)
        return SimpleNamespace(ok=True, quadrant="stale", wrote=True, evidence_path="", detail={})

    monkeypatch.setattr(PUBLISH, fake_publish)
    monkeypatch.setattr(PROJ_RUN, fake_render)

    def spy_disk_write(new_text: str, base_text: str) -> None:
        state["disk_writes"] += 1
        reg.write_text(new_text, encoding="utf-8", newline="\n")

    monkeypatch.setattr(amt, "_write_registry", spy_disk_write)
    return SimpleNamespace(ledger=ledger, state=state, reg=reg, root=tmp_path)


# ---------------------------------------------------------------------------
# 1. 登记新条目 → 账本出现该行（调用参数正确），随后 publish+render+三方核验
# ---------------------------------------------------------------------------


def test_new_registration_writes_ledger_then_publish_render(sandbox):
    code, msg = amt.add_translation(_entry(), session_id="st-test")
    assert code == amt.EXIT_SUCCESS, msg
    calls = sandbox.ledger.calls
    assert calls[0][0] == "register"
    payload = calls[0][1]
    assert list(payload)[0] == "module_path"
    assert payload["plain_zh"].startswith("演示模块")
    assert payload["responsibility_layer"] == "governance", "层由域→层映射真源派生，非调用方塞值"
    assert calls[0][3] == "st-test"
    assert sandbox.state["publish"] == 1 and sandbox.state["render"] == 1
    assert sandbox.state["disk_writes"] == 0, "账本通道绝不再手改投影"
    assert "落地核验=PG active 行 version=1" in msg, msg


# ---------------------------------------------------------------------------
# 2. 同 module_path 重复登记：他人已有字段一个不被清（已裁教训反向钉桩）
# ---------------------------------------------------------------------------


def test_reregister_keeps_others_fields(sandbox):
    others = {"module_id": "MOD-DEMO", "build_status": "dormant", "curator": "st-other-session"}
    first = _entry("scripts/demo/mod.py", **others)
    assert amt.add_translation(first, session_id="st-other")[0] == amt.EXIT_SUCCESS
    before = dict(sandbox.ledger.rows[0]["payload"])

    # 第二次只声明 path+plain_zh（其余参数缺省=空值，不得进入声明集）
    second = {
        "module_path": "scripts/demo/mod.py",
        "domain_id": "D_TEST",
        "name_zh": "演示模块",
        "name_en": "",
        "desc_zh": "",
        "desc_en": "",
        "plain_zh": "换了个大白话：这条记录仍然完整，别人登记的字段一个都不该丢。",
    }
    code, msg = amt.add_translation(second, session_id="st-me")
    assert code == amt.EXIT_SUCCESS, msg
    after = dict(sandbox.ledger.rows[0]["payload"])
    assert [c[0] for c in sandbox.ledger.calls[1:]] == ["update"], "已存行必须走 update，不插同键副本"
    for k, v in others.items():
        assert after.get(k) == v, f"他人字段 {k} 被清/覆盖（键集合差分失效）"
    assert after["plain_zh"] == second["plain_zh"]
    assert set(before) - set(after) == set(), "未点名的键不得从在册 payload 消失"
    assert after["responsibility_layer"] == "governance"


def test_empty_declared_values_never_blank_registered_fields(sandbox):
    assert amt.add_translation(_entry(name_en="Registered EN"), session_id="st-a")[0] == amt.EXIT_SUCCESS
    assert amt.add_translation(_entry(name_en=""), session_id="st-b")[0] == amt.EXIT_SUCCESS
    assert sandbox.ledger.rows[0]["payload"]["name_en"] == "Registered EN"


def test_named_clear_field_is_the_only_removal_path(sandbox):
    assert amt.add_translation(_entry(desc_en="to be cleared"), session_id="st-a")[0] == amt.EXIT_SUCCESS
    code, msg = amt.add_translation(
        _entry(desc_en="", plain_zh="大白话句子要够八个汉字才能过前置校验"),
        session_id="st-b",
        clear_fields=("desc_en",),
    )
    assert code == amt.EXIT_SUCCESS, msg
    assert "desc_en" not in sandbox.ledger.rows[0]["payload"]
    # 未点名的键（desc_zh）不受点名删除牵连
    assert sandbox.ledger.rows[0]["payload"]["desc_zh"] == "演示用技术简介"


def test_clear_field_never_removes_identity_key(sandbox):
    assert amt.add_translation(_entry(), session_id="st-a")[0] == amt.EXIT_SUCCESS
    code, msg = amt.add_translation(_entry(), session_id="st-b", clear_fields=("module_path", "name_zh"))
    assert code == amt.EXIT_SUCCESS, msg
    payload = sandbox.ledger.rows[0]["payload"]
    assert payload["module_path"] == "scripts/demo/mod.py", "身份键不可被点名删除"
    assert "name_zh" not in payload


def test_unauthorized_removal_guard_is_fail_closed():
    """删除集守卫（纯函数）：未点名的键从在册 payload 消失即判越界。"""
    existing = {"module_path": "a.py", "name_zh": "甲", "curator": "st-other"}
    declared = {"module_path": "a.py", "name_zh": "甲乙"}
    merged = amt._merge_payload(existing, declared, set())
    assert amt._unauthorized_removals(existing, merged, set()) == set()
    assert merged["curator"] == "st-other", "未声明的他人键必须原样带过"
    tampered = {"module_path": "a.py", "name_zh": "甲乙"}  # 整条覆盖姿态：他人键全丢
    assert amt._unauthorized_removals(existing, tampered, set()) == {"curator"}
    assert amt._unauthorized_removals(existing, tampered, {"curator"}) == set(), "点名后放行"


# ---------------------------------------------------------------------------
# 3. render 之后条目仍在（死路第二步被堵住）——真跑投影生成器 render 腿
# ---------------------------------------------------------------------------


def _snapshot_json(tmp_path: Path, text: str, revision: int) -> str:
    snap = snapshot_from_yaml(text, registry_id=amt.REGISTRY_ID, physical_path=amt.REGISTRY_REL)
    snap.ledger_revision = revision
    snap.snapshot_version = revision
    bundle = {
        "registry_id": snap.registry_id,
        "snapshot_version": revision,
        "ledger_revision": revision,
        "content_sha256": "",
        "header_lines": snap.header_lines,
        "sections": [
            {"root_key": s.root_key, "entries": [[list(p) for p in e] for e in s.entries]} for s in snap.sections
        ],
        "trailing_scalars": [list(t) for t in snap.trailing_scalars],
        "unique_key_fields": {k: list(v) for k, v in snap.unique_key_fields.items()},
    }
    path = tmp_path / f"snap_{revision}.json"
    path.write_text(
        json.dumps({"physical_path": amt.REGISTRY_REL, "bundle": bundle}, ensure_ascii=False), encoding="utf-8"
    )
    return str(path)


def _with_entry(text: str, block: str) -> str:
    """把条目块插到 entries 段末尾（下一个**顶层**键之前；unique_key 声明块里的同名字面量不算）。"""
    marker = "\nbattle_map_steps:\n"
    assert marker in text, "沙盘册缺顶层 battle_map_steps 段"
    return text.replace(marker, "\n" + block + "battle_map_steps:\n", 1)


def test_render_keeps_ledgered_entry_and_prunes_un_ledgered(tmp_path: Path, monkeypatch):
    reg = tmp_path / amt.REGISTRY_REL
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(SMALL_REGISTRY, encoding="utf-8", newline="\n")

    # 武装：v1 快照 = 账本现状（只有 a.py 一条）
    snap1 = _snapshot_json(tmp_path, SMALL_REGISTRY, 1)
    assert pg.run(tmp_path, mode="render", source=snap1, registry_id=amt.REGISTRY_ID, physical_path=amt.REGISTRY_REL).ok
    assert load_state(tmp_path) is not None

    # 账本前进：v2 = v1 + scripts/demo/new_mod.py（本班登记后的账本形态，payload 与登记声明同构）
    ledgered_payload = {k: v for k, v in _entry("scripts/demo/new_mod.py").items() if v}
    ledgered_payload["responsibility_layer"] = "governance"
    ledgered_face = _with_entry(
        SMALL_REGISTRY,
        yaml.safe_dump([ledgered_payload], allow_unicode=True, sort_keys=False),
    )
    snap2 = _snapshot_json(tmp_path, ledgered_face, 2)

    # 盘上另有"没入账本"的直写产物（旧通道留下的），render 必剪
    dirty = _with_entry(
        reg.read_text(encoding="utf-8"),
        "- module_path: scripts/demo/hand_written.py\n  name_zh: 手工直写\n"
        "  plain_zh: 这条没进账本，下一次 render 会把它剪掉\n",
    )
    reg.write_text(dirty, encoding="utf-8", newline="\n")

    ledger = _Ledger()
    ledger.register(_entry("scripts/demo/new_mod.py"), reason="seed", session_id="st-test")

    real_run = pg.run  # 打补丁前先取真函数（render_leg 内部不能再走已被替换的属性，否则自递归）

    captured: list = []

    def render_leg(root, mode="check", **kw):
        """本工具的 render 腿＝真投影生成器（source 走 JSON 影子快照通道）。"""
        assert mode == "render" and kw.get("registry_id") == amt.REGISTRY_ID
        rep = real_run(root, mode=mode, source=snap2, registry_id=amt.REGISTRY_ID, physical_path=amt.REGISTRY_REL)
        captured.append(rep)
        return rep

    monkeypatch.setattr(amt, "REGISTRY_YAML", reg)
    monkeypatch.setattr(amt, "PROJECTION_ROOT", tmp_path)
    monkeypatch.setattr(amt, "_read_layer_map", lambda: {"D_TEST": "governance"})
    monkeypatch.setattr(amt, "_ledger_rows", ledger.read_rows)
    monkeypatch.setattr(amt, "_ledger_register", ledger.register)
    monkeypatch.setattr(amt, "_ledger_update", ledger.update)
    monkeypatch.setattr(PROJ_RUN, render_leg)
    monkeypatch.setattr(PUBLISH, lambda rid, **kw: {"snapshot_version": 2, "noop": False})

    code, msg = amt.add_translation(_entry("scripts/demo/new_mod.py"), session_id="st-test")
    assert code == amt.EXIT_SUCCESS, msg
    face = reg.read_text(encoding="utf-8")
    assert "scripts/demo/new_mod.py" in face, "账本有该行 → render 后条目仍在（死路第二步已堵）"
    assert "scripts/demo/hand_written.py" not in face, "未入账本的直写条目被 render 修剪=病本体（通道已禁直写）"
    # drift 账面看得见修剪（C 项联测：身份增减量按该册声明的族集合逐族算，不再恒 0/0）。
    # 取=add_translation 自己那一趟 render 的报告——修剪就发生在这一趟；反向再跑一趟
    # "回退到 snap1"的 render 测不到它（状态锚已前进到 v2，象限判 clean、wrote=False）。
    assert captured, "add_translation 没走到 render 腿"
    post = captured[-1]
    assert post.ok and post.wrote, post
    assert post.detail["removed"] >= 1, (
        f"修剪必须落账面（旧缺陷＝族名硬编码 creation_tokens ⇒ 本册恒记 0/0）：{post.detail}"
    )
    assert post.detail["families"], f"逐族明细须可见：{post.detail}"


# ---------------------------------------------------------------------------
# 4. 逃生旗：缺省不直写；显式旗标才直写 + 红色警告 + 审计留痕
# ---------------------------------------------------------------------------


def test_legacy_flag_is_opt_in_and_leaves_warning_and_audit(sandbox, capsys):
    amt.add_translation(_entry(), session_id="st-test")
    assert sandbox.state["disk_writes"] == 0, "缺省绝不走直写腿"
    assert "LEGACY-DISK-WRITE" not in capsys.readouterr().err

    code, msg = amt.add_translation(_entry("scripts/demo/legacy.py"), session_id="st-test", legacy_disk_write=True)
    assert code == amt.EXIT_SUCCESS, msg
    assert sandbox.state["disk_writes"] == 1, "显式逃生旗才允许触到直写腿"
    err = capsys.readouterr().err
    assert "\033[31m" in err and "render" in err and "修剪" in err, err
    lines = [
        json.loads(x) for x in amt.LEGACY_DISK_WRITE_AUDIT_PATH.read_text(encoding="utf-8").splitlines() if x.strip()
    ]
    assert lines[-1]["module_path"] == "scripts/demo/legacy.py"
    assert lines[-1]["actor_session"] == "st-test" and lines[-1]["channel"] == "legacy_disk_write"


def test_dry_run_writes_nothing(sandbox):
    code, msg = amt.add_translation(_entry(), session_id="st-test", dry_run=True)
    assert code == amt.EXIT_SUCCESS, msg
    assert "[dry-run]" in msg
    assert sandbox.ledger.calls == [] and sandbox.state["publish"] == 0
    assert sandbox.state["render"] == 0 and sandbox.state["disk_writes"] == 0


# ---------------------------------------------------------------------------
# 5. 门禁提示语必须指回新 CLI（机判：解析为本 CLI 真实参数）
# ---------------------------------------------------------------------------


def _gate_message(tmp_path: Path, monkeypatch) -> str:
    import zephyr.gov_enforcement.commit_gates.translation_coverage_gate as tcg

    target = "scripts/demo/mod.py"
    monkeypatch.setattr(tcg, "_get_staged_new_py_files", lambda gw: [target])
    monkeypatch.setattr(tcg, "_check_translation_entry", lambda fp: "missing")
    monkeypatch.setattr(tcg, "_split_own_foreign", lambda gw, files, own, sid, gate_name="": (files, []))
    (tmp_path / "scripts" / "governance" / "d1_structure").mkdir(parents=True, exist_ok=True)
    gateway = SimpleNamespace(project_root=tmp_path, run_git=lambda *a: SimpleNamespace(returncode=0, stdout=""))
    passed, msg = tcg.make_translation_coverage_gate().check(gateway, [str(tmp_path / target)], session_id="st-x")
    assert passed is False, "判据本体（硬阻断）不得放松"
    return msg


def test_gate_fix_hint_parses_as_real_cli(tmp_path, monkeypatch):
    msg = _gate_message(tmp_path, monkeypatch)
    m = re.search(r"python (\S*add_module_translation\.py)", msg)
    assert m, msg
    script = m.group(1)
    pairs = re.findall(r"(--[a-z][a-z0-9-]*)\s+(\S+)", msg)
    flags = [f for f, _v in pairs]
    real_opts = {a for action in amt._build_argparser()._actions for a in action.option_strings}
    assert flags, f"提示语没给出任何参数: {msg}"
    assert set(flags) <= real_opts, f"提示语含本 CLI 不存在的参数: {set(flags) - real_opts}"
    assert "--legacy-disk-write" not in flags, "修复指引不得指向退役直写逃生旗"
    ns = amt._build_argparser().parse_args([t for pair in pairs for t in pair])
    assert ns.legacy_disk_write is False
    for key in ("path", "domain", "name_zh", "plain_zh"):
        assert str(getattr(ns, key)), f"提示语缺关键参数 {key}: {ns}"
    assert Path(amt.__file__).name == Path(script).name, "单口脚本必须是本工具（禁幻影路径处方）"
    assert "register" in msg and "render" in msg and "账本" in msg, "提示语须声明账本单口三步"


# ---------------------------------------------------------------------------
# 6. C 项：drift 记账族名不再硬编码 creation_tokens
# ---------------------------------------------------------------------------


def test_drift_accounting_is_per_declared_family(tmp_path: Path):
    reg = tmp_path / amt.REGISTRY_REL
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(SMALL_REGISTRY, encoding="utf-8", newline="\n")
    snap_v1 = _snapshot_json(tmp_path, SMALL_REGISTRY, 1)
    assert pg.run(
        tmp_path, mode="render", source=snap_v1, registry_id=amt.REGISTRY_ID, physical_path=amt.REGISTRY_REL
    ).ok

    # v17→v18 式两 bundle：entries 族删一条 + battle_map_steps 族加一条
    removed_one = SMALL_REGISTRY.replace(
        "entries:\n- module_path: a.py\n  name_zh: 甲模块\n  plain_zh: 甲模块的大白话简介说明它做什么\n",
        "entries:\n",
    )
    assert removed_one != SMALL_REGISTRY
    plus_step = removed_one.replace(
        "- step_id: s1\n  name_zh: 步骤一\n",
        "- step_id: s1\n  name_zh: 步骤一\n- step_id: s2\n  name_zh: 步骤二\n",
    )
    snap_v2 = _snapshot_json(tmp_path, plus_step, 2)
    report = pg.run(
        tmp_path, mode="render", source=snap_v2, registry_id=amt.REGISTRY_ID, physical_path=amt.REGISTRY_REL
    )
    assert report.ok and report.wrote
    assert report.detail["added"] == 1 and report.detail["removed"] == 1, report.detail
    assert report.detail["families"] == {"battle_map_steps": (1, 0), "entries": (0, 1)}, report.detail


def test_drift_accounting_creation_tokens_family_unchanged(tmp_path: Path):
    """creation_tokens 册：该族的数字与硬编码时代逐字相同（行为不变，只是不再独吞记账）。"""
    rel = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
    cap_v1 = "title: 测试册\ncreation_tokens:\n- file: a.md\n  token: tok-a\n  created_by: s\ndi_seam_exemptions: []\n"
    reg = tmp_path / rel
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(cap_v1, encoding="utf-8", newline="\n")

    def snap_json(text: str, rev: int) -> str:
        snap = snapshot_from_yaml(text, registry_id="REG-CAPCAN-001", physical_path=rel)
        snap.ledger_revision = rev
        snap.snapshot_version = rev
        bundle = {
            "registry_id": "REG-CAPCAN-001",
            "snapshot_version": rev,
            "ledger_revision": rev,
            "content_sha256": "",
            "header_lines": snap.header_lines,
            "sections": [
                {"root_key": s.root_key, "entries": [[list(p) for p in e] for e in s.entries]} for s in snap.sections
            ],
            "trailing_scalars": [list(t) for t in snap.trailing_scalars],
        }
        path = tmp_path / f"cap{rev}.json"
        path.write_text(json.dumps({"physical_path": rel, "bundle": bundle}, ensure_ascii=False), encoding="utf-8")
        return str(path)

    p1 = snap_json(cap_v1, 1)
    assert pg.run(tmp_path, mode="render", source=p1, registry_id="REG-CAPCAN-001", physical_path=rel).ok
    cap_v2 = cap_v1.replace(
        "di_seam_exemptions: []", "- file: b.md\n  token: tok-b\n  created_by: s\ndi_seam_exemptions: []"
    )
    p2 = snap_json(cap_v2, 2)
    report = pg.run(tmp_path, mode="render", source=p2, registry_id="REG-CAPCAN-001", physical_path=rel)
    assert report.detail["added"] == 1 and report.detail["removed"] == 0, report.detail
    assert report.detail["families"]["creation_tokens"] == (1, 0)


def test_api_code_literals_match_api_constants():
    """本工具不 import api（保 dry-run 轻依赖），字面量必须与 api 常量等值。"""
    assert (amt._CODE_OK, amt._CODE_NOOP, amt._CODE_CONFLICT_DUPLICATE, amt._CODE_CONFLICT_VERSION) == (
        api.OK,
        api.OK_NOOP,
        api.CONFLICT_DUPLICATE,
        api.CONFLICT_VERSION,
    )


# ---------------------------------------------------------------------------
# 7. pristine 红证：dev 原版字节的三处缺陷必须成立
# ---------------------------------------------------------------------------


def _pristine(name: str) -> tuple[str, str]:
    """基线 commit 的内容寻址原始字节（不落 .orig 副本：docs/_working 目录契约不允该
    扩展名，且根宪法 §4 全资产净零禁上 MB 级重复件）。二进制读，防行尾折叠改字节——
    实测取回字节与当初落盘的 .orig 副本 sha 逐一对齐＝等价性已证。"""
    rel = PRISTINE_RELS[name]
    proc = subprocess.run(
        ["git", "-C", str(_REPO_ROOT), "show", f"{BASELINE_SHA}:{rel}"],
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, f"基线 blob 取回失败 {rel}: {proc.stderr[:200]}"
    return proc.stdout.decode("utf-8"), hashlib.sha256(proc.stdout).hexdigest()


BASELINE_SHA = "cfbebbf8dd49f8b8ae935d186f4fbe7f8cfc6c66"
PRISTINE_RELS = {
    "add_module_translation.py.orig": "scripts/governance/d3_metadata/add_module_translation.py",
    "projection_generator.py.orig": "src/zephyr/governance/registry_projection/projection_generator.py",
    "translation_coverage_gate.py.orig": "src/zephyr/gov_enforcement/commit_gates/translation_coverage_gate.py",
}
PRISTINE_SHA256 = {
    "add_module_translation.py.orig": "56f09f2f926e1adeb0ee372d50361b51eeb182462c54650a00db962cd8a6269b",
    "projection_generator.py.orig": "c7048f5f167e97ee61193f8e9960072285a7f3fdc8cb26c019d4e352d1365233",
    "translation_coverage_gate.py.orig": "34ac8a2e10371c00afad50423fba516a65950144cf6af411ca3d68efd0896064",
}


def test_pristine_defects_reproduce():
    amt_src, amt_sha = _pristine("add_module_translation.py.orig")
    pg_src, pg_sha = _pristine("projection_generator.py.orig")
    gate_src, gate_sha = _pristine("translation_coverage_gate.py.orig")
    assert amt_sha == PRISTINE_SHA256["add_module_translation.py.orig"]
    assert pg_sha == PRISTINE_SHA256["projection_generator.py.orig"]
    assert gate_sha == PRISTINE_SHA256["translation_coverage_gate.py.orig"]

    # 缺陷①：登记工具全文件零账本调用（死路第一步=直写投影）
    for token in ("registry_ledger", "api.register", "api.update", "publish_snapshot", "projection_generator"):
        assert token not in amt_src, f"pristine 里竟有账本调用 {token}（缺陷①不成立=基线取错）"
    assert amt.REGISTRY_ID not in amt_src

    # 缺陷②：drift 记账族名硬编码 creation_tokens（"无据修剪"的账面来源）
    pristine_body = pg_src.split("def _drift_write_phase")[1].split("\ndef run")[0]
    assert '"creation_tokens"' in pristine_body, "pristine drift 记账不是硬编码单族（缺陷②不成立）"

    # 缺陷③：门禁提示语指向那个直写工具（死循环）
    hint = re.search(r"修复：python (\S*add_module_translation\.py)([^\n]*)", gate_src)
    assert hint, "pristine 门禁文案不指向直写工具（缺陷③不成立）"
    assert "--session" not in hint.group(2) and "publish" not in hint.group(2)

    # 修后对照：三处均已改道
    live_amt = Path(amt.__file__).read_text(encoding="utf-8")
    assert "publish_snapshot" in live_amt and "register_via_ledger" in live_amt
    live_pg_body = (
        Path(pg.__file__).read_text(encoding="utf-8").split("def _drift_write_phase")[1].split("\ndef run")[0]
    )
    assert '"creation_tokens"' not in live_pg_body
    import zephyr.gov_enforcement.commit_gates.translation_coverage_gate as tcg

    live_msg = Path(tcg.__file__).read_text(encoding="utf-8")
    assert "--session" in live_msg


# ---------------------------------------------------------------------------
# 8. 反向钉桩：retired 不渲染的在册口径未被放松
# ---------------------------------------------------------------------------


def test_baseline_active_filter_untouched():
    src = Path(baseline.__file__).read_text(encoding="utf-8")
    body = src.split("def publish_snapshot")[1]
    assert "WHERE registry_id=%s AND status='active' ORDER BY family_key, entry_key" in body, (
        "发布 SQL 的 active 过滤被改动=retired 也会被渲染（放松门禁红线）"
    )


def test_audit_reports_un_ledgered_projection_entry(tmp_path: Path):
    """审计＝机判"投影面有而最新快照无"；未入账本（含 retired 被剔）的条目不在快照 ⇒ 报出。"""
    reg = tmp_path / amt.REGISTRY_REL
    reg.parent.mkdir(parents=True, exist_ok=True)
    dirty = _with_entry(
        SMALL_REGISTRY,
        "- module_path: scripts/demo/hand_written.py\n  name_zh: 手工直写\n"
        "  plain_zh: 没进账本的条目，下一次 render 会剪掉\n",
    )
    reg.write_text(dirty, encoding="utf-8", newline="\n")
    snap = _snapshot_json(tmp_path, SMALL_REGISTRY, 1)  # 最新快照=账本 active 面（无该条）
    before_bytes = reg.read_bytes()
    code, msg = amt.audit_projection_vs_ledger(repo_root=tmp_path, snapshot_file=snap)
    assert code == amt.EXIT_VALIDATION
    assert "投影面有而快照无 = 1 条" in msg and "scripts/demo/hand_written.py" in msg
    assert reg.read_bytes() == before_bytes, "审计必须零写"


# ---------------------------------------------------------------------------
# 9-12. 通道纪律与 CLI 派发
# ---------------------------------------------------------------------------


def test_ledger_unreachable_fails_closed_without_disk_write(sandbox, monkeypatch):
    def boom(_path):
        raise RuntimeError("pg down")

    monkeypatch.setattr(amt, "_ledger_rows", boom)
    code, msg = amt.add_translation(_entry(), session_id="st-test")
    assert code == amt.EXIT_IO, msg
    assert "绝不降级直写" in msg
    assert sandbox.state["disk_writes"] == 0 and sandbox.state["publish"] == 0


def test_multiple_active_rows_refuses_registration(sandbox):
    assert amt.add_translation(_entry(), session_id="st-a")[0] == amt.EXIT_SUCCESS
    sandbox.ledger.rows.append(
        {
            "entry_key": "desc_en=d",
            "payload": dict(_entry(), plain_zh="第二条 active 副本"),
            "version": 1,
            "status": "active",
        }
    )
    publishes_before = sandbox.state["publish"]
    code, msg = amt.add_translation(_entry(), session_id="st-b")
    assert code == amt.EXIT_VALIDATION and "身份漂移" in msg, msg
    assert sandbox.state["publish"] == publishes_before, "多 active 行时绝不 publish/render"


def test_generic_plain_zh_rejected_before_any_ledger_call(sandbox):
    code, msg = amt.add_translation(_entry(plain_zh="提供包入口和模块加载功能的具体实现"), session_id="st-test")
    assert code == amt.EXIT_VALIDATION and "plain_zh 校验失败" in msg
    assert sandbox.ledger.calls == [] and sandbox.state["publish"] == 0


def test_main_dispatches_audit_and_rejects_mixing(capsys, tmp_path, monkeypatch):
    reg = tmp_path / amt.REGISTRY_REL
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(SMALL_REGISTRY, encoding="utf-8", newline="\n")
    monkeypatch.setattr(amt, "PROJECTION_ROOT", tmp_path)
    monkeypatch.setattr(
        amt,
        "_latest_snapshot",
        lambda rid, phys, f=None: snapshot_from_yaml(SMALL_REGISTRY, registry_id=rid, physical_path=phys),
    )
    assert amt.main(["--audit-projection-vs-ledger"]) == amt.EXIT_SUCCESS
    assert "零写只读" in capsys.readouterr().out
    assert amt.main(["--audit-projection-vs-ledger", "--path", "a.py"]) == amt.EXIT_VALIDATION
    assert amt.main(["--dedupe", "--sync-layer"]) == amt.EXIT_VALIDATION
    assert amt.main(["--path", "a.py"]) == amt.EXIT_VALIDATION  # 缺 --domain/--name-zh/--plain-zh
