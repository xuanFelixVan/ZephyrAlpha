"""ch_vm_config_snapshot.py — zephyr-ch 的月频「VM 定义面＋客户机配置面」快照通道（型A）。

令面"系统盘+配置面"的前提被实测改判：boot.vhdx=4,194,304 B 空盘，OS 与 CH 程序与数据同在 data.vhdx 的
sdb2 挂 / ⇒ 本机无独立系统盘可拷，盘级"不含数据盘的月镜像"物理不存在（三型 A/B/C 见 00_ledger 袋二与裁定#517）。
本件只拍 VM 定义面＋客户机 /etc 配置面，零拷任何 .vhdx 数据字节；落地判据＝首拍＋回滚双证。
用法：--dry-run 只预检；--verify-only <快照目录> 独立复验；退出码 0 双证齐／1 判红／3 预检拒（零写）。
"""
# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §ch_vm_config_snapshot
# [MODULE] scripts.backup.ch_vm_config_snapshot
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] scripts.backup.ch_vm_ssh (ssh_run); zephyr.shared.infra.process_pool (run_subprocess_hidden)
# [CONSUMERS] schtasks 月度计划任务 ZephyrAlpha-CHVMConfigSnapshot（须登记 data/runtime/process_reaper_keep.txt）；人工直跑为兜底形态
# [STARTUP] scheduled_task
# [MATURITY] production
# [INVARIANTS] 对生产 VM 只读（Hyper-V 侧只用 Get-*/Copy-Item 读，加一支隔离临时机的 New-/Remove-VM；绝不改 zephyr-ch 本体、其三张 vhdx、交换机）；快照永不含任何 .vhdx 数据字节（盘级镜像＝型 C，Owner 未开）；预检三拒＝未合并检查点链／目标盘可用空间<阈值／客户机不可达，一拒即 exit 3 且零写；双证定义＝证1 快照内逐件 sha256 与客户机同刻现读对拍（内容级，非存在性）∧证2 用快照里的 spec 在 Hyper-V 重建一台隔离临时机（0 磁盘附件、Internal 交换机、SecureBoot 按 spec 置 Off、绝不 Start-VM）逐字段对拍后 Remove-VM；正对照＝证1 命中集为空即判红（0 命中是"尺瞎"不是"查无"）；tar 件数与 sha 清单行数必须同数（两工具同源不自洽＝红）；保留线 keep≥2（入参低于 2 一律钳到 2）且只删名如 yyyyMMdd_HHmmss 且带 snapshot_manifest.json 的完整旧目录，删除只走 _prune_one 单口并读回复核；报告=logs/ch_vm_config_snapshot_<ts>.json 且八键齐全（沿用 PG 演练 judge_drill 契约外形，禁半成品报告）；凭据走 config/.env.ch_backup（RULE-SECRETS 管道，禁硬编码）；sudo 经 get_pty 会把口令提示混进正文，故所有 base64/清单类正文一律走哨兵边界提取，禁裸切字符串
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 预检不过=exit 3 零写；采集/验证不过=交足八键报告后 exit 1；每条外部调用一律先验 returncode 再验输出非空（rc!=0 或空输出＝命令没跑，不得读成"查无"；PS 空数组经管道输出空串属此类，故数组用 -InputObject 序列化）；临时机无论成败必在末段 Remove-VM 并读回复核（建立失败只撤临时机并判红——本件从不触碰生产 VM 生命周期，故不存在"回滚生产"路径）
# [TESTS] tests/data/backup/test_ch_vm_config_snapshot.py
# [A_module] module_id=MOD-INF-043 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 月度 VM 配置面快照 CLI 由 ZephyrAlpha-CHVMConfigSnapshot schtasks 月度事件触发，人工直跑为兜底形态，非常驻

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(_REPO))

from ch_vm_ssh import ssh_run  # noqa: E402  既有客户机访问单口（凭据走 config/.env.ch_backup）

from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402

VM_NAME = "zephyr-ch"
SNAPSHOT_ROOT = Path("G:/backup/ch_vm_config")
LOG_ROOT = _REPO / "logs"
KEEP_DEFAULT = 2
KEEP_FLOOR = 2
MIN_FREE_GIB = 50.0
CRITERIA_VERSION = "VMCFG-1"
_TS_RE = re.compile(r"^\d{8}_\d{6}$")
#: 批取正文的远端 for 循环只接安全字符集路径（空格/glob 会被词法劈坏，筛掉的条数随报告披露）
_SAFE_PATH_RE = re.compile(r"[A-Za-z0-9._/+@:-]+")

#: 客户机侧只读探针 SQL 集中位（§5.160.2 SQL 集中化，禁散落字面量）
SQL_SYSTEM_DISKS = "SELECT name, path, free_space, total_space FROM system.disks"
#: VM 定义面里允许进快照的配置文件后缀；.vhdx 永不在列（数据盘零拷＝本通道立身之本）
CONFIG_BLOB_SUFFIXES = (".vmcx", ".vmgs")
_PS_PREFIX = "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; $ErrorActionPreference='Stop'; "

#: 证1 必核件：客户机配置面里"没它就起不来/接不上"的件，全部落在 /etc 内（不另开手写路径清单）
CORE_GUEST_FILES = (
    "etc/clickhouse-server/config.xml",
    "etc/clickhouse-server/users.xml",
    "etc/fstab",
)
#: 抽样件数（确定性：按路径序等距取，禁随机——随机样本复现不了就不算判据）
EVIDENCE1_SAMPLE_N = 12


class PrecheckRefused(Exception):
    """预检拒绝＝exit 3，零写。"""


class CaptureFailed(Exception):
    """采集/验证判红＝exit 1，报告仍交足键集。"""


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ps(script: str, timeout: int = 300):
    """跑一段 PowerShell：要 rc==0 ∧ stdout 非空 ∧ 可 JSON 解析（空输出＝没跑，不是查无）。"""
    r = run_subprocess_hidden(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", _PS_PREFIX + script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if r.returncode != 0:
        raise CaptureFailed(f"powershell rc={r.returncode} stderr={(r.stderr or '')[:300]}")
    out = (r.stdout or "").strip()
    if not out:
        raise CaptureFailed("powershell stdout empty (命令没跑，禁止读成查无)")
    try:
        return json.loads(out)
    except ValueError as exc:
        raise CaptureFailed(f"powershell output not JSON ({exc}): {out[:180]}") from exc


def _guest(cmd: str, timeout: int = 300, use_sudo: bool = False) -> str:
    """客户机执行。rc!=0 或正文空＝判红（SSH 返 0 而正文全空是本仓在册的静默失败形态）。

    正文需要 root 读权限时一律走 `_guest_rooted`，不要在这里加 use_sudo——见该件的 pty 回显病因。
    """
    res = ssh_run(cmd, timeout=timeout, use_sudo=use_sudo)
    rc = res.get("exit_code")
    out = res.get("stdout") or ""
    if rc != 0:
        raise CaptureFailed(f"guest rc={rc} cmd={cmd[:90]} stderr={(res.get('stderr') or '')[:200]}")
    out = out.strip()
    if not out:
        raise CaptureFailed(f"guest empty body cmd={cmd[:90]} (rc=0 而正文全空＝不可判，按红处理)")
    return out


def _guest_root_file(inner: str, suffix: str, timeout: int = 600) -> bytes:
    """root-only 产物落客户机 /tmp，再在**无 pty 会话**里 base64 读回字节（唯一 root 读取单口）。

    实测病因（别再绕回来）：`ssh_run(..., use_sudo=True)` 走 get_pty 喂口令，pty 会把口令原样回显进
    同一条 stdout（样本 `ZephyrAlpha2026\r\n=B64BEGIN=\r\nZephyrAlpha2026\r\n<正文>`）
    ⇒ 任何"在 sudo 会话里直接取正文"的写法都会把口令片段当数据，哨兵也切不开。
    本函数内两处 use_sudo（产出侧＋清理侧）是全文唯一允许位，由测册钉住。
    """
    tmp = f"/tmp/chvmcfg_{os.getpid()}_{int(time.time())}{suffix}"
    cmd = inner.replace("{tmp}", tmp) + f" && chmod 644 {tmp}"
    if "'" in cmd:
        raise CaptureFailed("inner 含单引号，不能安全包进 sh -c 的单引号外壳")
    r = ssh_run(f"sudo sh -c '{cmd}'", timeout=timeout, use_sudo=True)
    if r.get("exit_code") != 0:
        raise CaptureFailed(
            f"guest sudo rc={r.get('exit_code')} cmd={inner[:90]} stderr={(r.get('stderr') or '')[:200]}"
        )
    try:
        body = _guest(f"base64 -w0 {tmp}", timeout=timeout)
        raw = base64.b64decode(body)
        if not raw:
            raise CaptureFailed(f"guest body empty cmd={inner[:90]}（不可判＝红，禁当查无）")
        return raw
    finally:
        ssh_run(f"sudo sh -c 'rm -f {tmp}'", timeout=60, use_sudo=True)


def _guest_root_body(inner_cmd: str, suffix: str, timeout: int = 600) -> str:
    """文本形态：把 inner_cmd 的 stdout 重定向进临时文件后读回。"""
    return _guest_root_file(f"{inner_cmd} > {{tmp}}", suffix, timeout).decode("utf-8", "replace")


def _guest_batch_b64(keys: list[str], timeout: int = 600) -> dict[str, bytes]:
    """一次调用取多件正文（每件 sha 要各自现读，逐件跑会开 2N 条 SSH 连接）。"""
    listed = " ".join(k for k in keys)
    # 内层零引号：本命令整体被 `sudo sh -c "..."` 的双引号包住，再写双引号会自撞外壳（实测首版即此病）
    raw = _guest_root_body(f"for f in {listed}; do echo KEY:$f; base64 -w0 /$f; echo; done", ".batch", timeout=timeout)
    out: dict[str, bytes] = {}
    lines = raw.splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("KEY:"):
            key = line[4:].strip()
            payload = lines[idx + 1].strip() if idx + 1 < len(lines) else ""
            try:
                out[key] = base64.b64decode(payload)
            except Exception:  # noqa: BLE001  解不开＝该件不可信，原样不入库（下游按缺失判红）
                continue
    return out


def collect_vm_definition() -> dict:
    """VM 定义面：Hyper-V 全字段只读采集（含三张盘的 FileSize/VirtualSize 台账——只记元数据，不拷字节）。"""
    spec = _ps(
        "$v=Get-VM -Name zephyr-ch; "
        "$h=@(Get-VMHardDiskDrive -VMName zephyr-ch | ForEach-Object { "
        "  $vh=$null; try { $vh=Get-VHD -Path $_.Path } catch {}; "
        "  [pscustomobject]@{ControllerType=[string]$_.ControllerType;ControllerNumber=$_.ControllerNumber;"
        "ControllerLocation=$_.ControllerLocation;Path=$_.Path;"
        "FileSize=$(if($vh){$vh.FileSize}else{-1});VirtualSize=$(if($vh){$vh.Size}else{-1});"
        "VhdType=$(if($vh){[string]$vh.VHDType}else{'UNREADABLE'})} }); "
        "$n=@(Get-VMNetworkAdapter -VMName zephyr-ch | ForEach-Object { "
        "  [pscustomobject]@{Name=$_.Name;SwitchName=$_.SwitchName;MacAddress=$_.MacAddress;Connected=$_.Connected} }); "
        "$i=@(Get-VMIntegrationService -VMName zephyr-ch | ForEach-Object { "
        "  [pscustomobject]@{Name=$_.Name;Enabled=$_.Enabled;PrimaryStatusDescription=[string]$_.PrimaryStatusDescription} }); "
        "$c=@(Get-VMSnapshot -VMName zephyr-ch | ForEach-Object { [string]$_.Name }); "
        "$f=Get-VMFirmware -VMName zephyr-ch; $s=Get-VMSecurity -VMName zephyr-ch; "
        "$m=Get-VMMemory -VMName zephyr-ch; $p=Get-VMProcessor -VMName zephyr-ch; "
        "[pscustomobject]@{Name=$v.Name;Id=[string]$v.Id;State=[string]$v.State;Generation=[string]$v.Generation;"
        "Path=$v.Path;Version=$v.Version;Notes=$v.Notes;ProcessorCount=$v.ProcessorCount;"
        "MemoryStartup=$v.MemoryStartup;DynamicMemoryEnabled=$v.DynamicMemoryEnabled;"
        "MemoryMinimum=$v.MemoryMinimum;MemoryMaximum=$v.MemoryMaximum;"
        "AutomaticStartAction=[string]$v.AutomaticStartAction;AutomaticStopAction=[string]$v.AutomaticStopAction;"
        "UptimeSeconds=$(if($v.Uptime){[math]::Round($v.Uptime.TotalSeconds,0)}else{-1});"
        "HardDrives=$h;Adapters=$n;IntegrationServices=$i;Checkpoints=$c;"
        "Firmware=[pscustomobject]@{BootOrder=@($f.BootOrder|ForEach-Object{[string]$_});"
        "SecureBoot=[string]$f.SecureBoot;SecureBootTemplate=[string]$f.SecureBootTemplate};"
        "Security=[pscustomobject]@{EnableSecureBoot=[string]$s.EnableSecureBoot;EnableTPM=[string]$s.EnableTPM};"
        "Memory=[pscustomobject]@{Startup=$m.Startup;Min=$m.Minimum;Max=$m.Maximum};"
        "Processor=[pscustomobject]@{Count=$p.Count;Reserve=$p.Reserve;Weight=$p.Weight}"
        "} | ConvertTo-Json -Depth 6 -Compress"
    )
    if isinstance(spec, list):
        spec = spec[0]
    return spec


def copy_config_blobs(spec: dict, dest_dir: Path) -> list[dict]:
    """在线复制 vmcx/vmgs（配置面原字节，实测运行中可读）。vmrs＝运行期内存态（10.3 GiB）非可移植资产，不拷。

    源件哈希**在 VM 运行时取不到**（实测：VMMS 以读写共享持有 vmcx，`Copy-Item` 能过，
    `Get-FileHash` 被"正由另一进程使用"拒），故本函数的字节级自证＝**源尺寸(Get-Item 元数据) ↔ 副本尺寸**
    ∧ 副本 sha256 入账（供下月漂移对拍），源哈希位显式记 `DENIED_WHILE_RUNNING`——留空会被读成"没测"，
    显式记不可得才是诚实形态。停机窗口另拍全量（型 C）才谈得上源哈希。
    """
    vm_dir = Path(spec["Path"]) / "Virtual Machines"
    guid = spec["Id"]
    rows: list[dict] = []
    for suffix in CONFIG_BLOB_SUFFIXES:
        src = vm_dir / f"{guid}{suffix}"
        if not src.exists():
            rows.append({"file": suffix, "status": "missing", "source": str(src).replace("\\", "/")})
            continue
        src_size = _ps("ConvertTo-Json -Compress -InputObject (Get-Item -LiteralPath '%s').Length" % src)
        out = dest_dir / f"{guid}{suffix}"
        _ps(
            "Copy-Item -LiteralPath '%s' -Destination '%s' -Force; ConvertTo-Json -Compress -InputObject 'copied'"
            % (src, out)
        )
        if not out.exists():
            rows.append({"file": suffix, "status": "copy_failed", "source": str(src).replace("\\", "/")})
            continue
        got = _ps(
            "ConvertTo-Json -Compress -InputObject ([pscustomobject]@{"
            "bytes=(Get-Item -LiteralPath '%s').Length;sha=(Get-FileHash -LiteralPath '%s' -Algorithm SHA256).Hash})"
            % (out, out)
        )
        if isinstance(got, list):
            got = got[0]
        size_src = int(src_size[0] if isinstance(src_size, list) else src_size)
        size_copy = int(got.get("bytes") or 0)
        ok = size_copy > 0 and size_copy == size_src and bool(got.get("sha"))
        rows.append(
            {
                "file": suffix,
                "source_path": str(src).replace("\\", "/"),
                "bytes_source": size_src,
                "bytes_copy": size_copy,
                "sha256_copy": got.get("sha"),
                "sha256_source": "DENIED_WHILE_RUNNING(VMMS 读写共享持有)",
                "status": "ok" if ok else ("size_mismatch" if size_copy != size_src else "unreadable"),
            }
        )
    return rows


def _tar_member_sha(tar_path: Path) -> dict[str, str]:
    """从**盘上**的 tar 逐件读字节算 sha256（走完整写-读路径，不用内存里那份）。"""
    out: dict[str, str] = {}
    with tarfile.open(tar_path, "r:gz") as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            fh = tf.extractfile(m)
            if fh is None:
                continue
            out[m.name] = hashlib.sha256(fh.read()).hexdigest()
    return out


def _sample_keys(members: dict[str, str], n: int) -> list[str]:
    keys = sorted(members)
    if len(keys) <= n:
        return keys
    step = max(1, len(keys) // n)
    return keys[::step][:n]


def capture_guest(dest_dir: Path) -> dict:
    """客户机配置面＝/etc 全量 tar ＋逐件 sha256 清单 ＋版本/盘位台账（范围由目录定义，无手写清单）。"""
    (dest_dir / "guest").mkdir(parents=True, exist_ok=True)
    raw = _guest_root_file("tar -czf {tmp} -C / etc", ".tgz", timeout=900)
    tar_path = dest_dir / "guest" / "etc.tar.gz"
    tar_path.write_bytes(raw)
    sha_txt = _guest_root_body("find /etc -type f -print0 | xargs -0 -r sha256sum", ".sha", timeout=900)
    (dest_dir / "guest" / "etc_sha256sums.txt").write_text(sha_txt + "\n", encoding="utf-8")
    members = _tar_member_sha(tar_path)
    inventory = {
        "clickhouse_server_version": _guest("clickhouse-server --version", timeout=120),
        "kernel": _guest("uname -r", timeout=60),
        "os": _guest("head -4 /etc/os-release", timeout=60),
        "clickhouse_packages": _guest("dpkg -l 2>/dev/null | grep -i clickhouse | awk '{print $2, $3}'", timeout=120),
        "block_layout": _guest("lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,UUID", timeout=120),
        "mounts": _guest("df -B1G / /var/lib/clickhouse /mnt/chbackup_local", timeout=120),
        "enabled_units": _guest("systemctl list-unit-files --state=enabled --no-pager", timeout=240),
        "ch_disks": _guest('clickhouse-client -q "' + SQL_SYSTEM_DISKS + '"', timeout=240),
    }
    (dest_dir / "guest" / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {
        "tar_bytes": len(raw),
        "tar_sha256": hashlib.sha256(raw).hexdigest(),
        "tar_members": len(members),
        "sha_lines": len([x for x in sha_txt.splitlines() if x.strip()]),
        "inventory_keys": sorted(inventory),
    }


def verify_evidence_1(snapshot_dir: Path) -> dict:
    """证1 内容级：快照内逐件 sha256 ↔ 客户机同刻现读 sha256。命中集为空＝尺瞎＝判红。"""
    tar_path = snapshot_dir / "guest" / "etc.tar.gz"
    if not tar_path.exists():
        return {"ok": False, "reason": "missing_etc_tar", "compared": 0, "mismatched": [], "core_hit": 0}
    members = _tar_member_sha(tar_path)
    if not members:
        return {
            "ok": False,
            "reason": "zero_tar_members（0 命中＝不可判，不冒领 ok）",
            "compared": 0,
            "mismatched": [],
            "core_hit": 0,
        }
    # 批取正文走远端 `for f in ...`⇒ 含空格/glob 字符的路径会被词法劈坏；先按安全字符集筛样并留数披露
    safe = [k for k in members if _SAFE_PATH_RE.fullmatch(k)]
    want = sorted(
        set(k for k in CORE_GUEST_FILES if k in members)
        | set(_sample_keys({k: members[k] for k in safe}, EVIDENCE1_SAMPLE_N))
    )
    bodies = _guest_batch_b64(want)
    live = {k: hashlib.sha256(v).hexdigest() for k, v in bodies.items()}
    unreadable = [k for k in want if k not in live]
    mismatched = [k for k in want if k in live and members.get(k) != live[k]]
    core_hit = sum(1 for k in CORE_GUEST_FILES if members.get(k) and live.get(k) == members.get(k))
    sha_manifest = snapshot_dir / "guest" / "etc_sha256sums.txt"
    sha_lines = (
        len([x for x in sha_manifest.read_text(encoding="utf-8").splitlines() if x.strip()])
        if sha_manifest.exists()
        else 0
    )
    return {
        # 三件缺一即红：无一失配 ∧ 核心件全中 ∧ tar 与 sha 清单同数；取不到正文＝不可判＝红（禁当"查无"）
        "ok": (not mismatched)
        and (not unreadable)
        and core_hit == len(CORE_GUEST_FILES)
        and sha_lines == len(members)
        and len(live) > 0,
        "compared": len(want),
        "mismatched": mismatched,
        "unreadable": unreadable,
        "core_expected": list(CORE_GUEST_FILES),
        "core_hit": core_hit,
        "tar_members_total": len(members),
        "sha_manifest_lines": sha_lines,
        "self_consistency": "tar==sha_manifest" if sha_lines == len(members) else f"tar{len(members)}!=sha{sha_lines}",
    }


def verify_evidence_2(snapshot_dir: Path) -> dict:
    """证2 可回滚级：用快照里的 spec 在 Hyper-V 重建隔离临时机，逐字段对拍后删除；零动生产 VM。"""
    spec = json.loads((snapshot_dir / "vm_definition.json").read_text(encoding="utf-8"))
    tmp_name = f"dr-chvmcfg-{datetime.now(timezone.utc).strftime('%m%d%H%M%S')}"
    # SecureBoot 读位＝Get-VMFirmware.SecureBoot（[string] 才给 Off/On；枚举经 ConvertTo-Json 会变成 1，
    # 而 Get-VMSecurity.EnableSecureBoot 在本机 PS 5.1 实测为 null⇒ 不作判据源，只在 spec 里留档）
    secure = str((spec.get("Firmware") or {}).get("SecureBoot", "")).strip()
    if secure not in ("On", "Off"):
        return {"ok": False, "reason": f"secureboot_spec_unreadable:{secure!r}", "temp_vm": tmp_name}
    script = (
        "$ErrorActionPreference='Stop'; $o=$null; "
        "try { "
        "$sw=(Get-VMSwitch | Where-Object { $_.SwitchType -eq 'Internal' } | Select-Object -First 1).Name; "
        "New-VM -Name '%s' -MemoryStartupBytes %d -Generation 2 -NoVHD -SwitchName $sw | Out-Null; "
        "Set-VMProcessor -VMName '%s' -Count %d; "
        "Set-VMFirmware -VMName '%s' -EnableSecureBoot %s; "
        "$r=Get-VM -Name '%s'; $p=Get-VMProcessor -VMName '%s'; $f=Get-VMFirmware -VMName '%s'; "
        "$h=@(Get-VMHardDiskDrive -VMName '%s'); "
        "$o=[pscustomobject]@{BuildError='';State=[string]$r.State;Generation=[string]$r.Generation;"
        "ProcessorCount=$p.Count;MemoryStartup=$r.MemoryStartup;SecureBoot=[string]$f.SecureBoot;"
        "DiskAttachments=$h.Count;Switch=$sw} "
        "} catch { $o=[pscustomobject]@{BuildError=$_.Exception.Message;State='';Generation='';ProcessorCount=-1;"
        "MemoryStartup=-1;SecureBoot='';DiskAttachments=-1;Switch=''} }; "
        "$gone=$true; "
        "try { if (Get-VM -Name '%s' -ErrorAction SilentlyContinue) { Remove-VM -Name '%s' -Force } } catch { $gone=$false }; "
        "$o | ConvertTo-Json -Compress"
    ) % (
        tmp_name,
        int(spec["MemoryStartup"]),
        tmp_name,
        int(spec["ProcessorCount"]),
        tmp_name,
        secure,
        tmp_name,
        tmp_name,
        tmp_name,
        tmp_name,
        tmp_name,
        tmp_name,
    )
    got = _ps(script, timeout=420)
    if isinstance(got, list):
        got = got[0]
    still_there = _ps(
        "ConvertTo-Json -Compress -InputObject @(Get-VM -Name '%s' -ErrorAction SilentlyContinue)" % tmp_name
    )
    removed = not (still_there or [])
    if got.get("BuildError"):
        return {
            "ok": False,
            "reason": f"temp_vm_build_failed: {got['BuildError']}",
            "temp_vm": tmp_name,
            "temp_vm_removed": bool(removed),
        }
    return compare_rebuild(spec, secure, got, removed, tmp_name)


def compare_rebuild(spec: dict, secure: str, got: dict, removed: bool, tmp_name: str) -> dict:
    """证2 的纯比较面，与 Hyper-V 调用分离，红绿对拍才能不连真机。

    四件缺一即红：临时机没开机（State=Off）且没挂任何盘（DiskAttachments=0，防误挂生产 vhdx）
    且四字段与快照 spec 同 且已撤除（读回复核）。
    """
    expect = {
        "Generation": str(spec["Generation"]),
        "ProcessorCount": int(spec["ProcessorCount"]),
        "MemoryStartup": int(spec["MemoryStartup"]),
        "SecureBoot": secure,
    }
    actual = {
        "Generation": str(got.get("Generation")),
        "ProcessorCount": got.get("ProcessorCount"),
        "MemoryStartup": got.get("MemoryStartup"),
        "SecureBoot": str(got.get("SecureBoot", "")),
    }
    field_diff = [k for k, want in expect.items() if str(want).lower() != str(actual.get(k)).lower()]
    return {
        "ok": (not field_diff)
        and str(got.get("State")) == "Off"
        and int(got.get("DiskAttachments", -1)) == 0
        and bool(removed),
        "expect": expect,
        "actual": actual,
        "field_diff": field_diff,
        "disk_attachments": got.get("DiskAttachments"),
        "switch": got.get("Switch"),
        "temp_vm_state": got.get("State"),
        "temp_vm_removed": bool(removed),
        "temp_vm": tmp_name,
    }


def precheck() -> dict:
    """预检三拒：未合并检查点链／目标盘空间／客户机可达。任何一拒＝exit 3 且零写。"""
    reasons: list[str] = []
    cps = _ps(
        "ConvertTo-Json -Compress -InputObject @(Get-VMSnapshot -VMName zephyr-ch | ForEach-Object { [string]$_.Name })"
    )
    checkpoints = [str(x) for x in (cps if isinstance(cps, list) else [cps]) if str(x).strip()]
    if checkpoints:
        reasons.append(f"unmerged_checkpoint_chain={checkpoints}")
    st = _ps("[string](Get-VM -Name zephyr-ch).State | ConvertTo-Json -Compress")
    state = str(st[0] if isinstance(st, list) else st).strip('"')
    if state != "Running":
        reasons.append(f"vm_state={state}")
    fr = _ps("[math]::Round((Get-PSDrive -Name G).Free/1GB,1) | ConvertTo-Json -Compress")
    free_gib = float(fr[0] if isinstance(fr, list) else fr)
    if free_gib < MIN_FREE_GIB:
        reasons.append(f"G_free_gib={free_gib}<{MIN_FREE_GIB}")
    try:
        probe = _guest("echo probe_ok", timeout=90)
    except Exception as exc:  # noqa: BLE001  不可达＝不可判＝不拍
        reasons.append(f"guest_unreachable:{type(exc).__name__}")
        probe = ""
    if reasons:
        raise PrecheckRefused("; ".join(reasons))
    return {"checkpoints": 0, "vm_state": state, "g_free_gib": free_gib, "guest_probe": probe}


def capture(dest_root: Path) -> Path:
    """建当日快照目录。本函数内任何异常＝自造半成品⇒就地撤除后原样上抛（不留半份给下一班）。"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snap = dest_root / ts
    try:
        return _capture_into(snap, ts)
    except Exception:
        if snap.exists():
            shutil.rmtree(snap, ignore_errors=True)
        raise


def _capture_into(snap: Path, ts: str) -> Path:
    (snap / "vm_config").mkdir(parents=True, exist_ok=True)
    started = _utc_stamp()
    spec = collect_vm_definition()
    (snap / "vm_definition.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    blobs = copy_config_blobs(spec, snap / "vm_config")
    guest = capture_guest(snap)
    manifest = {
        "criteria_version": CRITERIA_VERSION,
        "started_at_utc": started,
        "finished_at_utc": _utc_stamp(),
        "snapshot_dir": str(snap).replace("\\", "/"),
        "vm_name": VM_NAME,
        "vm_definition": {
            "generation": spec.get("Generation"),
            "processor_count": spec.get("ProcessorCount"),
            "memory_startup": spec.get("MemoryStartup"),
            "state": spec.get("State"),
            "hard_drives": spec.get("HardDrives"),
            "adapters": spec.get("Adapters"),
            "firmware": spec.get("Firmware"),
            "security": spec.get("Security"),
            "checkpoints": spec.get("Checkpoints"),
            "path": spec.get("Path"),
            "automatic_start": spec.get("AutomaticStartAction"),
            "automatic_stop": spec.get("AutomaticStopAction"),
        },
        "config_blobs": blobs,
        "guest": guest,
        "scope_note": (
            "本快照＝VM 定义面＋客户机配置面；实测 boot.vhdx 为空盘（4,194,304 B）、"
            "OS 与 CH 程序与数据同在 data.vhdx 的 sdb2 挂 / ⇒ 零拷任何 .vhdx 数据字节；"
            "型 B（guest 内 OS+程序文件级镜像 ≈13 GiB）与型 C（盘级全镜像 563 GiB）未开，待 Owner 裁"
        ),
    }
    (snap / "snapshot_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return snap


def _prune_one(path: Path) -> dict:
    """删除唯一单口：先验存在、再删、再读回复核（与备份链在册正解同形；rmtree 对不存在路径会抛）。"""
    existed = path.exists()
    if existed:
        shutil.rmtree(path)
    return {"path": str(path).replace("\\", "/"), "existed_before": existed, "gone_after": not path.exists()}


def prune(dest_root: Path, keep: int) -> dict:
    """保留线：keep 硬下限 2；只删名如 yyyyMMdd_HHmmss 且带 manifest 的完整旧目录；半成品一律不动。"""
    keep = max(int(keep), KEEP_FLOOR)
    dirs = sorted([d for d in dest_root.iterdir() if d.is_dir() and _TS_RE.match(d.name)], reverse=True)
    removed = []
    for d in dirs[keep:]:
        if not (d / "snapshot_manifest.json").exists():
            continue
        removed.append(_prune_one(d))
    return {"keep": keep, "candidates": len(dirs), "removed": removed, "retained": [d.name for d in dirs[:keep]]}


def _skeleton() -> dict:
    """八键报告外形（沿用 PG 演练已裁契约：键集恒定，失败支不交半成品）。"""
    return {
        "pass": False,
        "status": "failed",
        "criteria": {},
        "failed_criteria": [],
        "rows": {},
        "criteria_version": CRITERIA_VERSION,
        "criteria_change_note": "VMCFG-1 首版（2026-10-14 备份线夜班 P1-B，Owner 2026-10-13 晚裁月频快照）",
        "legacy_judge_note": "",
        "started_at": _utc_stamp(),
    }


def run(dry_run: bool, keep: int) -> dict:
    report = _skeleton()
    try:
        report["precheck"] = precheck()
        if dry_run:
            report["status"] = "precheck_ok_dry_run"
            report["pass"] = True
            report["rows"] = {"planned_snapshot_root": str(SNAPSHOT_ROOT).replace("\\", "/"), "keep": keep}
            return report
        snap = capture(SNAPSHOT_ROOT)
        report["snapshot_dir"] = str(snap).replace("\\", "/")
        man = json.loads((snap / "snapshot_manifest.json").read_text(encoding="utf-8"))
        blobs = man.get("config_blobs") or []
        c0 = {
            "ok": bool(blobs) and all(r.get("status") == "ok" for r in blobs),
            "rows": [
                {
                    "file": r.get("file"),
                    "status": r.get("status"),
                    "bytes_source": r.get("bytes_source"),
                    "bytes_copy": r.get("bytes_copy"),
                }
                for r in blobs
            ],
            "note": "源哈希运行中不可得（显式记 DENIED_WHILE_RUNNING），字节级自证＝源尺寸↔副本尺寸＋副本 sha256 入账",
        }
        c1 = verify_evidence_1(snap)
        c2 = verify_evidence_2(snap)
        report["criteria"] = {
            "evidence0_config_blob_bytes": c0,
            "evidence1_content_hash": c1,
            "evidence2_definition_rebuild": c2,
        }
        report["failed_criteria"] = [name for name, v in report["criteria"].items() if not v["ok"]]
        report["rows"] = {
            "tar_members": c1.get("tar_members_total", 0),
            "hash_compared": c1.get("compared", 0),
            "core_hit": c1.get("core_hit", 0),
            "keep": keep,
            "vmcx_bytes": next((r.get("bytes_copy") for r in blobs if r.get("file") == ".vmcx"), 0),
        }
        report["retention"] = prune(SNAPSHOT_ROOT, keep)
        report["pass"] = not report["failed_criteria"]
        report["status"] = "landed_dual_proof" if report["pass"] else "verify_red"
    except PrecheckRefused as exc:
        report["status"] = "precheck_refused"
        report["refusal"] = str(exc)
        report["exit_code"] = 3
    except CaptureFailed as exc:
        report["status"] = "capture_failed"
        report["error"] = str(exc)[:400]
    except Exception as exc:  # noqa: BLE001  未预期异常也交足八键，禁半成品报告
        report["status"] = "unexpected_error"
        report["error"] = f"{type(exc).__name__}: {exc}"[:400]
    report["finished_at"] = _utc_stamp()
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="zephyr-ch VM 配置面月频快照（型 A）＋回滚双证")
    ap.add_argument("--dry-run", action="store_true", help="只预检，零写")
    ap.add_argument("--verify-only", default=None, help="对既有快照目录重跑双证")
    ap.add_argument("--keep", type=int, default=KEEP_DEFAULT, help="保留份数（硬下限 2）")
    args = ap.parse_args()
    if args.verify_only:
        snap = Path(args.verify_only)
        man = json.loads((snap / "snapshot_manifest.json").read_text(encoding="utf-8"))
        blobs = man.get("config_blobs") or []
        verdict = {
            "evidence0_config_blob_bytes": {
                "ok": bool(blobs) and all(r.get("status") == "ok" for r in blobs),
                "rows": [{"file": r.get("file"), "status": r.get("status")} for r in blobs],
            },
            "evidence1_content_hash": verify_evidence_1(snap),
            "evidence2_definition_rebuild": verify_evidence_2(snap),
        }
        report = _skeleton()
        report["snapshot_dir"] = str(snap).replace("\\", "/")
        report["criteria"] = verdict
        report["failed_criteria"] = [k for k, v in verdict.items() if not v.get("ok")]
        report["pass"] = not report["failed_criteria"]
        report["status"] = "verify_only_landed" if report["pass"] else "verify_only_red"
        exit_code = 0 if report["pass"] else 1
    else:
        report = run(args.dry_run, args.keep)
        exit_code = int(report.get("exit_code") if "exit_code" in report else (0 if report["pass"] else 1))
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    out = LOG_ROOT / f"ch_vm_config_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "pass": report["pass"],
                "status": report["status"],
                "failed_criteria": report["failed_criteria"],
                "snapshot_dir": report.get("snapshot_dir", ""),
                "report": str(out).replace("\\", "/"),
            },
            ensure_ascii=False,
        )
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
