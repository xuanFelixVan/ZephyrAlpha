"""test_ch_vm_config_snapshot.py — VM 配置面快照通道（型 A）的常驻尺：全离线，零 SSH、零 Hyper-V。

件头边界（照 PG 演练同一条铁律写醒目）：**本件证的是采集/裁决契约与 shell 安全面，
不证"这份快照真能把虚拟机拉起来"**。端到端可还原性只由真演练证，月度真跑不得因此撤。

钉住的四类已付学费：
  ① `ssh_run(use_sudo=True)` 走 get_pty 会把口令回显进 stdout ⇒ root 读取必须收在一个单口内；
  ② 存在性≠内容判据 ⇒ 0 命中一律判红，不许读成"查无"；
  ③ 误挂生产 vhdx / 把数据盘当配置盘 ⇒ DiskAttachments 必须为 0，且复制面只准碰 .vmcx/.vmgs；
  ④ 报告契约随路径变 ⇒ 失败支也必带全键集，`rows` 恒为 dict（同 PG 演练候裁⑦的定型理由）。
"""

from __future__ import annotations

import base64
import hashlib
import io
import sys
import tarfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "backup"))
import ch_vm_config_snapshot as m  # noqa: E402

SRC = Path(m.__file__).read_text(encoding="utf-8")
_ROOT_MOUTH_START = SRC.index("def _guest_root_file(")
_ROOT_MOUTH_END = SRC.index("def _guest_batch_b64(")


def _make_tar(files: dict[str, bytes], dirs: tuple[str, ...] = ()) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
        for name in dirs:
            info = tarfile.TarInfo(name)
            info.type = tarfile.DIRTYPE
            tf.addfile(info)
    return buf.getvalue()


def _fixture_files() -> dict[str, bytes]:
    """tar 内容从 `m.CORE_GUEST_FILES` 派生，不手抄路径（手抄的清单会在核心件变动时静默变红，本班首跑就撞过）。"""
    files = {k: f"body-of-{k}\n".encode() for k in m.CORE_GUEST_FILES}
    files["etc/hostname"] = b"zephyr-ch\n"
    return files


@pytest.fixture()
def snap_dir(tmp_path):
    d = tmp_path / "20260101_000000"
    (d / "guest").mkdir(parents=True)
    files = _fixture_files()
    (d / "guest" / "etc.tar.gz").write_bytes(_make_tar(files))
    lines = [f"{hashlib.sha256(v).hexdigest()}  /{k}" for k, v in files.items()]
    (d / "guest" / "etc_sha256sums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (d / "vm_definition.json").write_text(
        '{"Generation":"2","ProcessorCount":12,"MemoryStartup":8589934592,'
        '"Path":"D:/HyperV/VMs/zephyr-ch","Security":{"EnableSecureBoot":""},'
        '"Firmware":{"SecureBoot":"Off"}}',
        encoding="utf-8",
    )
    (d / "snapshot_manifest.json").write_text('{"config_blobs":[]}', encoding="utf-8")
    return d


# ---------- ① root 读取单口围栏 ----------


def test_use_sudo_lives_only_inside_the_rooted_mouth():
    """全文所有 `use_sudo=True` 必须落在 `_guest_root_file` 体内。

    体外出现＝有人在带 pty 的会话里直接取正文，会把口令回显当数据（实测样本见该件 docstring）。
    """
    outside = SRC[:_ROOT_MOUTH_START].count("use_sudo=True") + SRC[_ROOT_MOUTH_END:].count("use_sudo=True")
    assert outside == 0, f"_guest_root_file 之外出现 {outside} 处 use_sudo=True"
    inside = SRC[_ROOT_MOUTH_START:_ROOT_MOUTH_END]
    assert "base64 -w0" in inside and "chmod 644" in inside, "单口必须同时管住落盘读位与无 pty 读回"


def test_rooted_mouth_reads_back_without_pty(monkeypatch):
    """sudo 侧的输出（含回显口令）永不进正文；正文只来自第二次不带 pty 的调用。"""
    seen: list[tuple[str, bool]] = []

    def fake_ssh_run(cmd, timeout=120, use_sudo=False):
        seen.append((cmd, use_sudo))
        if use_sudo:
            return {"exit_code": 0, "stdout": "SECRETECHO", "stderr": ""}
        return {"exit_code": 0, "stdout": base64.b64encode(b"real-body\n").decode(), "stderr": ""}

    monkeypatch.setattr(m, "ssh_run", fake_ssh_run)
    out = m._guest_root_body("cat /etc/shadow", ".t")
    assert out == "real-body\n" and "SECRETECHO" not in out
    assert seen[0][1] is True, "产出侧走 sudo（带 pty）"
    assert seen[1][1] is False, "读回侧必须无 pty"


def test_rooted_mouth_refuses_single_quote_and_empty_body(monkeypatch):
    with pytest.raises(m.CaptureFailed, match="单引号"):
        m._guest_root_body("echo it's", ".x")
    monkeypatch.setattr(
        m,
        "ssh_run",
        lambda cmd, timeout=120, use_sudo=False: {"exit_code": 0, "stdout": "" if use_sudo else "", "stderr": ""},
    )
    with pytest.raises(m.CaptureFailed, match="empty"):
        m._guest_root_body("cat /etc/whatever", ".x")


def test_rooted_mouth_raises_when_sudo_stage_fails(monkeypatch):
    monkeypatch.setattr(
        m,
        "ssh_run",
        lambda cmd, timeout=120, use_sudo=False: {
            "exit_code": 1,
            "stdout": "",
            "stderr": "sudo: a terminal is required",
        },
    )
    with pytest.raises(m.CaptureFailed, match="guest sudo rc=1"):
        m._guest_root_body("tar -czf {tmp} -C / etc", ".tgz")


def test_batch_b64_parses_key_payload_pairs(monkeypatch):
    raw = "".join(f"KEY:{k}\n{base64.b64encode(v).decode()}\n\n" for k, v in [("etc/a", b"one\n"), ("etc/b", b"two\n")])
    monkeypatch.setattr(m, "_guest_root_body", lambda *a, **k: raw)
    assert m._guest_batch_b64(["etc/a", "etc/b"]) == {"etc/a": b"one\n", "etc/b": b"two\n"}


def test_batch_b64_drops_unparsable_payload_instead_of_trusting_it(monkeypatch):
    """解不开＝该件不可信，不入库；下游按 unreadable 判红（禁把坏读数当相等）。"""
    monkeypatch.setattr(m, "_guest_root_body", lambda *a, **k: "KEY:etc/a\nnot_base64!!!\n")
    got = m._guest_batch_b64(["etc/a"])
    assert got == {}


# ---------- ② 证1 内容级对拍 ----------


def test_evidence1_green_when_snapshot_matches_live(snap_dir, monkeypatch):
    monkeypatch.setattr(m, "_guest_batch_b64", lambda keys, **kw: _fixture_files())
    v = m.verify_evidence_1(snap_dir)
    assert v["ok"] is True and v["mismatched"] == [] and v["unreadable"] == []
    assert v["core_hit"] == len(m.CORE_GUEST_FILES)
    assert v["tar_members_total"] == v["sha_manifest_lines"] == len(_fixture_files())


def test_evidence1_red_on_a_single_byte_change(snap_dir, monkeypatch):
    """红绿对拍（尺有牙）：改一个字节必须当场红。"""
    bad = _fixture_files()
    key = m.CORE_GUEST_FILES[0]
    bad[key] = b"TAMPERED\n"
    monkeypatch.setattr(m, "_guest_batch_b64", lambda keys, **kw: bad)
    v = m.verify_evidence_1(snap_dir)
    assert v["ok"] is False and key in v["mismatched"]


def test_evidence1_red_on_zero_hits_never_as_not_applicable(snap_dir, monkeypatch):
    """0 命中＝尺瞎，不是"查无"（在册老病：降级态与未触发同形）。"""
    monkeypatch.setattr(m, "_guest_batch_b64", lambda keys, **kw: {})
    v = m.verify_evidence_1(snap_dir)
    assert v["ok"] is False and v["compared"] > 0 and len(v["unreadable"]) == v["compared"]


def test_evidence1_red_when_tar_and_manifest_counts_diverge(snap_dir, monkeypatch):
    monkeypatch.setattr(m, "_guest_batch_b64", lambda keys, **kw: _fixture_files())
    (snap_dir / "guest" / "etc_sha256sums.txt").write_text("one line only\n", encoding="utf-8")
    v = m.verify_evidence_1(snap_dir)
    assert v["ok"] is False and v["self_consistency"].startswith("tar4!=sha1")


def test_evidence1_red_on_dirs_only_tar(tmp_path):
    d = tmp_path / "x"
    (d / "guest").mkdir(parents=True)
    (d / "guest" / "etc.tar.gz").write_bytes(_make_tar({}, dirs=("etc/",)))
    v = m.verify_evidence_1(d)
    assert v["ok"] is False and v["reason"].startswith("zero_tar_members")


def test_evidence1_red_when_tar_file_absent(tmp_path):
    v = m.verify_evidence_1(tmp_path)
    assert v["ok"] is False and v["reason"] == "missing_etc_tar"


def test_sample_keys_deterministic_and_bounded():
    members = {f"etc/f{i:03d}": "0" * 64 for i in range(500)}
    assert m._sample_keys(members, 12) == m._sample_keys(members, 12)
    assert len(m._sample_keys(members, 12)) == 12
    assert m._sample_keys({"etc/x": "1"}, 12) == ["etc/x"]


def test_evidence1_skips_paths_the_remote_loop_cannot_quote(snap_dir, monkeypatch):
    """含空格/中文的路径不进远端 `for f in ...`；被筛掉的那份必须可见，不能凭空少测。"""
    files = _fixture_files()
    files["etc/weird name/带空格.txt"] = b"x"
    (snap_dir / "guest" / "etc.tar.gz").write_bytes(_make_tar(files))
    lines = [f"{hashlib.sha256(v).hexdigest()}  /{k}" for k, v in files.items()]
    (snap_dir / "guest" / "etc_sha256sums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    asked: list[list[str]] = []

    def spy(keys, **kw):
        asked.append(list(keys))
        return {k: files[k] for k in keys}

    monkeypatch.setattr(m, "_guest_batch_b64", spy)
    v = m.verify_evidence_1(snap_dir)
    assert v["ok"] is True
    assert not any(" " in k or "带" in k for k in asked[0]), "不安全路径被放进远端循环"


# ---------- ③ 证2 纯比较面 ----------


def _spec():
    return {"Generation": "2", "ProcessorCount": 12, "MemoryStartup": 8589934592}


def _got(**over):
    base = {
        "Generation": "2",
        "ProcessorCount": 12,
        "MemoryStartup": 8589934592,
        "SecureBoot": "Off",
        "State": "Off",
        "DiskAttachments": 0,
        "Switch": "ZephyrCH-Net",
    }
    base.update(over)
    return base


def test_compare_rebuild_green_only_on_full_match():
    v = m.compare_rebuild(_spec(), "Off", _got(), True, "dr-x")
    assert v["ok"] is True and v["field_diff"] == []


@pytest.mark.parametrize(
    "over",
    [
        {"DiskAttachments": 3},  # 挂到盘＝可能挂生产 vhdx
        {"State": "Running"},  # 开过机
        {"ProcessorCount": 4},  # 字段不符
        {"SecureBoot": "On"},  # SecureBoot 未按 spec
        {"MemoryStartup": 1073741824},  # 内存未按 spec
    ],
)
def test_compare_rebuild_each_deviation_is_red(over):
    assert m.compare_rebuild(_spec(), "Off", _got(**over), True, "dr-x")["ok"] is False


def test_compare_rebuild_red_when_temp_vm_survives():
    v = m.compare_rebuild(_spec(), "Off", _got(), False, "dr-x")
    assert v["ok"] is False and v["temp_vm_removed"] is False


def test_verify_evidence2_refuses_unreadable_secureboot_spec(tmp_path, monkeypatch):
    """本机 Get-VMSecurity.EnableSecureBoot 实测为 null ⇒ 判据源只能取 Get-VMFirmware.SecureBoot；
    读不到就拒判，不许猜一个值继续。"""
    d = tmp_path / "s"
    d.mkdir()
    (d / "vm_definition.json").write_text(
        '{"Generation":"2","ProcessorCount":1,"MemoryStartup":524288000,"Firmware":{"SecureBoot":""}}', encoding="utf-8"
    )
    monkeypatch.setattr(m, "_ps", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("不该调 PS")))
    v = m.verify_evidence_2(d)
    assert v["ok"] is False and "secureboot_spec_unreadable" in v["reason"]


# ---------- ④ 保留线与快照根 ----------


def test_prune_keeps_floor_two_and_never_touches_half_made_dirs(tmp_path):
    for name, complete in (
        ("20260101_000000", True),
        ("20260102_000000", False),
        ("20260103_000000", True),
        ("20260104_000000", True),
    ):
        d = tmp_path / name
        (d / "guest").mkdir(parents=True)
        if complete:
            (d / "snapshot_manifest.json").write_text("{}", encoding="utf-8")
    (tmp_path / "not_a_timestamp").mkdir()
    res = m.prune(tmp_path, keep=2)
    assert res["keep"] == 2 and (tmp_path / "20260104_000000").exists() and (tmp_path / "20260103_000000").exists()
    assert not (tmp_path / "20260101_000000").exists(), "超出保留线的完整旧快照应被撤"
    assert (tmp_path / "20260102_000000").exists(), "无 manifest 的半成品禁删（宁留不删）"
    assert (tmp_path / "not_a_timestamp").exists(), "名不符 yyyyMMdd_HHmmss 的目录一律不动"
    assert res["removed"][0]["gone_after"] is True, "删除必须读回复核"


def test_prune_clamps_keep_below_two(tmp_path):
    for name in ("20260101_000000", "20260102_000000", "20260103_000000"):
        d = tmp_path / name
        d.mkdir()
        (d / "snapshot_manifest.json").write_text("{}", encoding="utf-8")
    res = m.prune(tmp_path, keep=0)
    assert res["keep"] == 2
    assert sum(1 for x in tmp_path.iterdir() if x.is_dir()) == 2, "keep 硬下限失守"


def test_prune_one_is_safe_on_absent_path():
    r = m._prune_one(Path("D:/definitely/not/here"))
    assert r["existed_before"] is False and r["gone_after"] is True


def test_snapshot_root_is_the_backup_vault():
    assert str(m.SNAPSHOT_ROOT).replace("\\", "/").startswith("G:/backup/"), "快照只能落备份总仓"


def test_copy_surface_excludes_every_vhdx():
    """前提被实测证伪后的纪律：本机无独立系统盘，boot/data 两张 vhdx 一律不进快照。"""
    assert m.CONFIG_BLOB_SUFFIXES == (".vmcx", ".vmgs")
    assert not any(s.endswith(".vhdx") for s in m.CONFIG_BLOB_SUFFIXES)
    span = SRC[SRC.index("def copy_config_blobs(") : SRC.index("def capture_guest(")]
    assert "vhdx" not in span.replace(".vhdx 数据字节", ""), "复制面里出现了 vhdx 字面量"


# ---------- ⑤ 报告八键契约（沿用 PG 演练外形，失败支禁半成品） ----------


def test_skeleton_carries_the_eight_contract_keys():
    keys = set(m._skeleton())
    need = {
        "pass",
        "criteria",
        "failed_criteria",
        "rows",
        "criteria_version",
        "criteria_change_note",
        "legacy_judge_note",
        "status",
        "started_at",
    }
    assert need <= keys, f"报告骨架缺键：{need - keys}"


def test_rows_stays_dict_on_failure_path():
    """读侧 report['rows'][t] 不得因失败支换型抛 TypeError（候裁⑦定的 {} 语义）。"""
    sk = m._skeleton()
    assert isinstance(sk["rows"], dict) and sk["rows"] == {}
    assert sk["criteria"] == {} and sk["failed_criteria"] == []


def test_precheck_refusal_carries_full_skeleton_and_exit_three(tmp_path, monkeypatch):
    """预检拒绝＝exit 3 且报告仍交足键集（不许拿"没跑"交白卷）。"""
    monkeypatch.setattr(
        m, "precheck", lambda: (_ for _ in ()).throw(m.PrecheckRefused("unmerged_checkpoint_chain=['x']"))
    )
    rep = m.run(dry_run=False, keep=2)
    assert rep["status"] == "precheck_refused" and rep["pass"] is False and rep["exit_code"] == 3
    assert set(m._skeleton()) <= set(rep)


def test_criteria_version_and_constants_pinned():
    assert m.CRITERIA_VERSION == "VMCFG-1"
    assert m.KEEP_FLOOR == 2 and m.KEEP_DEFAULT >= m.KEEP_FLOOR
    assert m.MIN_FREE_GIB > 0 and m.EVIDENCE1_SAMPLE_N >= 1
